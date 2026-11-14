#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Czytelność na TELEFONIE w poziomie — emulacja ekranu w trybie Play (sam wraca do trybu Edit).

    python -B swiat/test_walki2/testy/telefon.py                 # 844×390 i 667×375 → klatki/telefon_*.jpg + raport
    python -B swiat/test_walki2/testy/telefon.py --rozmiary 844x390

Studio nie daje przez MCP emulatora urządzeń, więc interfejs prototypu ma własną emulację: atrybut kontenera
EmulacjaEkranu = Vector2 (rozmiar ekranu telefonu w punktach). Panel wyboru i interfejs walki układają się wtedy
w prostokącie o tych proporcjach na środku okna (pomniejszonym, jeśli okno Studio jest mniejsze), a kamera walki
kadruje jak na tym ekranie. Skrypt wycina ten prostokąt ze zrzutu i mierzy wysokość każdego widocznego napisu
w punktach telefonu (TextBounds ÷ skala emulacji). Próg czytelności: napisy stałe ≥ 12 punktów.

Czego to NIE sprawdza: wydajności telefonu, dotyku, gęstości pikseli ani wyglądu w pionie (gra jest pozioma).
"""
import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
KATALOG = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(KATALOG))
for _s in (TU, os.path.join(REPO, "tools", "walka")):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import silnik as S  # noqa: E402
import wzorcowe as WZ  # noqa: E402
from sesja_play import SesjaPlay, log  # noqa: E402

PROG = 12.0
WYBOR_WALKI = ("zwiadowca", "lesny_troll", 10, 950601)  # wszystkie rodzaje zdarzeń, efekty na obu stronach

POMIAR = r'''
local TS = game:GetService("TextService")
local pg = game:GetService("Players").LocalPlayer.PlayerGui
local M = workspace.TestWalki2.Moduly
local I = require(M.InterfejsWalki2)
local ox, oy, sz, wys, f = I.ekran()
local vp = workspace.CurrentCamera.ViewportSize
local gui = pg:FindFirstChild("__GUI__")
local lista = {}
local function widoczny(o)
	local p = o
	while p and p ~= gui do
		if p:IsA("GuiObject") and not p.Visible then return false end
		p = p.Parent
	end
	return gui and gui.Enabled
end
if gui then
	for _, t in gui:GetDescendants() do
		if (t:IsA("TextLabel") or t:IsA("TextButton")) and t.Text ~= "" and t.TextTransparency < 0.9 and widoczny(t)
			and not string.find(t.Name, "Cien") then
			local h = t.TextBounds.Y
			local linii = 1
			if t.TextWrapped and h > 0 then
				for n = 1, 3 do
					local r = TS:GetTextSize(t.Text, h / n, t.Font, Vector2.new(t.AbsoluteSize.X, 1e5))
					if math.abs(r.Y - h) < h * 0.12 then linii = n break end
				end
			end
			local sciezka = string.gsub(t:GetFullName(), "^.-__GUI__%.", "")
			table.insert(lista, { n = sciezka, t = t.Text, pkt = math.floor(h / linii / f * 10 + 0.5) / 10, linii = linii })
		end
	end
end
return game:GetService("HttpService"):JSONEncode({ ox = ox, oy = oy, sz = sz, wys = wys, f = f, vp = { vp.X, vp.Y }, napisy = lista })
'''


def zmierz(s, gui):
    return json.loads(s.luau(POMIAR.replace("__GUI__", gui)))


def wytnij(im, p):
    """Prostokąt emulowanego ekranu ze zrzutu (zrzut może mieć inną rozdzielczość niż ViewportSize)."""
    kx, ky = im.size[0] / p["vp"][0], im.size[1] / p["vp"][1]
    return im.crop((int(p["ox"] * kx), int(p["oy"] * ky), int((p["ox"] + p["sz"]) * kx), int((p["oy"] + p["wys"]) * ky)))


def podsumuj(nazwa, p, drobne_dozwolone=()):
    napisy = sorted(p["napisy"], key=lambda x: x["pkt"])
    drobne = [x for x in napisy if x["pkt"] < PROG and not any(d in x["n"] for d in drobne_dozwolone)]
    najm = napisy[0] if napisy else None
    log("%s: %d napisów, najmniejszy %.1f pkt (%s: %r); poniżej %g pkt: %d" % (
        nazwa, len(napisy), najm["pkt"] if najm else 0, najm["n"] if najm else "-", najm["t"] if najm else "", PROG, len(drobne)))
    for x in drobne[:12]:
        log("   drobny: %.1f pkt  %s  %r" % (x["pkt"], x["n"], x["t"][:40]))
    return {"napisow": len(napisy), "najmniejszy_pkt": najm["pkt"] if najm else None, "najmniejszy": najm,
            "ponizej_progu": drobne, "wszystkie": napisy}


def chwila_walki():
    """Chwila w walce pokazowej: umiejętność z nazwą na wstędze i co najmniej jeden efekt aktywny."""
    w = S.symuluj(WZ.postac(WYBOR_WALKI[0], WYBOR_WALKI[2]), {"potwor": WYBOR_WALKI[1], "poziom": WYBOR_WALKI[2]}, WYBOR_WALKI[3])
    aktywne = set()
    for z in w["dziennik"]:
        if z["typ"] == "efekt_nalozony":
            aktywne.add((z["cel"], z["efekt"]))
        elif z["typ"] == "efekt_koniec":
            aktywne.discard((z["cel"], z["efekt"]))
        elif z["typ"] == "umiejetnosc" and z["kto"] != z["cel"] and aktywne:
            return z["t"] + z["trwa"] * 0.62
    return w["dziennik"][len(w["dziennik"]) // 2]["t"]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--rozmiary", default="844x390,667x375")
    ap.add_argument("--wyj", default=os.path.join(KATALOG, "klatki"))
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    rozmiary = [tuple(int(v) for v in r.split("x")) for r in a.rozmiary.split(",")]
    raport = {"prog_pkt": PROG, "data": time.strftime("%Y-%m-%d %H:%M"), "ekrany": {}}
    tau = chwila_walki()
    with SesjaPlay(a.studio) as s:
        for _ in range(40):  # ekran ładowania gry
            if s.luau('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("LoadingScreen") '
                      'local b = g and g:FindFirstChild("Background") '
                      'return tostring(g == nil or not g.Enabled or b == nil or not b.Visible or b.BackgroundTransparency >= 0.99)').strip() == "true":
                break
            time.sleep(0.5)
        s.przy_tablicy()
        s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", true) return "ok"', "Server")
        try:
            for (w, h) in rozmiary:
                klucz = "%dx%d" % (w, h)
                log("ekran", klucz)
                s.luau('workspace.TestWalki2:SetAttribute("EmulacjaEkranu", Vector2.new(%d, %d)) return "ok"' % (w, h))
                wynik = {}
                # 1) panel wyboru przy tablicy
                s.steruj('"zamknij"')
                time.sleep(0.8)
                s.steruj('"wybor"')
                time.sleep(1.2)
                p = zmierz(s, "TestWalki2Wybor")
                im = s.zrzut()
                wytnij(im, p).save(os.path.join(a.wyj, "telefon_%s_panel.jpg" % klucz), "JPEG", quality=88)
                wynik["panel"] = podsumuj("panel wyboru " + klucz, p)
                wynik["skala_emulacji"] = p["f"]
                wynik["okno_studio"] = p["vp"]
                s.luau('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("TestWalki2Wybor") if g then g:Destroy() end return "ok"')
                # 2) walka: umiejętność, efekty, liczby
                s.ziarno(WYBOR_WALKI[3])
                s.start(WYBOR_WALKI[0], WYBOR_WALKI[1], str(WYBOR_WALKI[2]), "{ reczny = true }")
                st, _ = s.czekaj(("odtwarzanie",), 15)
                if st.get("OstatniStan") == "odtwarzanie":
                    s.steruj('"przewinDo", %f' % tau)
                    time.sleep(0.3)
                    p = zmierz(s, "TestWalki2Cutscenka")
                    im, _ = s.zrzut_odtwarzacza()
                    wytnij(im, p).save(os.path.join(a.wyj, "telefon_%s_walka.jpg" % klucz), "JPEG", quality=88)
                    # napisy nad postaciami są duże z założenia; mierzymy wszystkie, a stopka panelu wyniku (ziarno, czas)
                    # jest informacją techniczną dla testów — ją dopuszczamy jako drobną
                    wynik["walka"] = podsumuj("walka " + klucz, p)
                    s.steruj('"przewinDo", 1000')
                    time.sleep(1.8)
                    p = zmierz(s, "TestWalki2Cutscenka")
                    im, _ = s.zrzut_odtwarzacza()
                    wytnij(im, p).save(os.path.join(a.wyj, "telefon_%s_wynik.jpg" % klucz), "JPEG", quality=88)
                    wynik["wynik"] = podsumuj("panel wyniku " + klucz, p, drobne_dozwolone=("Stopka",))
                else:
                    log("walka nie wystartowała:", st.get("OstatniStan"), st.get("OstatniaOdmowa"))
                s.steruj('"zamknij"')
                time.sleep(0.8)
                raport["ekrany"][klucz] = wynik
        finally:
            try:
                s.luau('workspace.TestWalki2:SetAttribute("EmulacjaEkranu", nil) return "ok"')
                s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", nil) workspace.TestWalki2:SetAttribute("ZiarnoTestowe", nil) return "ok"', "Server")
            except Exception:  # noqa: BLE001
                pass
    zle = sum(len(v.get(c, {}).get("ponizej_progu", [])) for v in raport["ekrany"].values() for c in ("panel", "walka", "wynik"))
    raport["ponizej_progu_razem"] = zle
    with open(os.path.join(a.wyj, "raport_telefonu.json"), "w", encoding="utf-8") as f:
        json.dump(raport, f, ensure_ascii=False, indent=1)
    log("WYNIK: napisów poniżej %g pkt: %d; Studio w trybie Edit: %s" % (PROG, zle, s.edit_po))
    sys.exit(0 if zle == 0 and s.edit_po else 1)


if __name__ == "__main__":
    main()
