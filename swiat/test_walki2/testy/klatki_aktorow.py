#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arkusze klatek aktorów walki v2 — w trybie PLAY, na lokalnym klonie u klienta, przez prawdziwy moduł Klipy.

    python -B swiat/test_walki2/testy/klatki_aktorow.py                       # wszyscy aktorzy, domyślne klipy
    python -B swiat/test_walki2/testy/klatki_aktorow.py --tylko wojownik,mag --klatki 8
    python -B swiat/test_walki2/testy/klatki_aktorow.py --obrys                # porównanie obrysu (Leśny Troll)
    python -B swiat/test_walki2/testy/klatki_aktorow.py --wyj <folder>         # domyślnie swiat/test_walki2/klatki

Co robi: włącza Play, czeka na klienta, chowa lokalnie interfejs gry, stawia klon aktora na środku podestu tak jak
w walce (klasa po lewej patrzy w prawo, przeciwnik po prawej patrzy w lewo), kamera skryptowa z boku (jak plan
walki) i dla każdej klatki: Klipy:poza(klip, czas) → dwie klatki fizyki → zrzut. Na końcu ZAWSZE zatrzymuje Play
(także po błędzie i Ctrl+C) i sprawdza, że Studio wróciło do trybu Edit. Zmienia wyłącznie stan sesji Play.
Wynik: <aktor>_spoczynek.jpg, <aktor>_<klip>.jpg (arkusze, czytaj wierszami), pomiar klonu w raport_klatek.json.
"""
import argparse
import io
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
KATALOG = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(KATALOG))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"), KATALOG, REPO):
    if _s not in sys.path:
        sys.path.insert(0, _s)
from studio_mcp import StudioMCP, StudioError  # noqa: E402
from cel_studio import wybierz_studio  # noqa: E402
import aktorzy as A  # noqa: E402
sys.path.insert(0, TU)
from czuwanie import nie_usypiaj  # noqa: E402

PRZYGOTUJ = r'''
local k = workspace:FindFirstChild("TestWalki2")
if not k then return "STOP: brak kontenera" end
local gracz = game:GetService("Players").LocalPlayer
local t0 = os.clock()
while not gracz.Character and os.clock() - t0 < 15 do task.wait(0.1) end
task.wait(0.5)
for _, g in gracz.PlayerGui:GetChildren() do
	if g:IsA("ScreenGui") then g.Enabled = false end
end
pcall(function() game:GetService("StarterGui"):SetCoreGuiEnabled(Enum.CoreGuiType.All, false) end)
-- własna postać i szablony z galerii nie wchodzą w kadr (zmiana lokalna)
if gracz.Character then
	for _, d in gracz.Character:GetDescendants() do
		if d:IsA("BasePart") or d:IsA("Decal") then d.LocalTransparencyModifier = 1 end
	end
end
local f = k:FindFirstChild("KlatkiLokalne") or Instance.new("Folder")
f.Name = "KlatkiLokalne"
f.Parent = k
return "OK"
'''

# __KLUCZ__, __OBRYS__, __STRONA__ ; zwraca opis klonu
POSTAW = r'''
local k = workspace.TestWalki2
local U = require(k.Moduly.Ustawienia)
local Aktorzy = require(k.Moduly.Aktorzy)
U.POKAZ_PUNKTOW = __PUNKTY__ -- zmiana tylko w tej sesji Play (kopia modułu u klienta)
local f = k.KlatkiLokalne
f:ClearAllChildren()
_G.TW2_AKTOR = nil
local cf = U.scena() * CFrame.lookAt(Vector3.zero, Vector3.new(__KIERUNEK__, 0, 0))
local t0 = os.clock()
local a = Aktorzy.nowy("__KLUCZ__", cf, { rodzic = f, obrys = "__OBRYS__", reczny = true, bezSpoczynku = true })
local czas = os.clock() - t0
_G.TW2_AKTOR = a
local cam = workspace.CurrentCamera
cam.CameraType = Enum.CameraType.Scriptable
cam.FieldOfView = 50
local n, skorupy = 0, 0
for _, d in a.model:GetDescendants() do
	if d:IsA("BasePart") then
		if d:GetAttribute("Obrys") then skorupy += 1 else n += 1 end
	end
end
return game:GetService("HttpService"):JSONEncode({ czesci = n, skorupy = skorupy, widoczne = a.liczbaCzesci,
	instancje = #a.model:GetDescendants() + 1, ms = czas * 1000 })
'''

# __KLIP__, __CZAS__, __KAMERA__ (x,y,z w układzie sceny), __CEL__
POZA = r'''
local k = workspace.TestWalki2
local U = require(k.Moduly.Ustawienia)
local a = _G.TW2_AKTOR
if not a then return "STOP: brak aktora" end
local klip = "__KLIP__"
if klip == "" then
	a.klipy:zatrzymaj(0)
	table.clear(a.klipy.tory)
	a.klipy:zastosuj()
else
	if not a.klipy:poza(klip, __CZAS__) then return "STOP: brak klipu " .. klip end
end
-- interfejs gry potrafi się włączyć później (ekran ładowania, HUD) — chowamy go przy każdej klatce (zmiana lokalna)
for _, g in game:GetService("Players").LocalPlayer.PlayerGui:GetChildren() do
	if g:IsA("ScreenGui") then g.Enabled = false end
end
local s = U.scena()
workspace.CurrentCamera.CameraType = Enum.CameraType.Scriptable
workspace.CurrentCamera.FieldOfView = 50
workspace.CurrentCamera.CFrame = CFrame.lookAt((s * CFrame.new(__KAMERA__)).Position, (s * CFrame.new(__CEL__)).Position)
game:GetService("RunService").PreSimulation:Wait()
game:GetService("RunService").Heartbeat:Wait()
task.wait(0.05)
task.wait(0.05)
-- kontrola: czy części kości stoją tam, gdzie każą stawy (Transform naprawdę zadziałał)
local maks = 0
for _, m in a.model:GetDescendants() do
	if m:IsA("Motor6D") and m.Part0 and m.Part1 then
		local roz = (m.Part0.CFrame * m.C0 * m.Transform * m.C1:Inverse()).Position - m.Part1.Position
		maks = math.max(maks, roz.Magnitude)
	end
end
return string.format("OK %.4f", maks)
'''

BOK = 300  # bok kafelka arkusza (px)

SPRZATAJ = r'''
local k = workspace:FindFirstChild("TestWalki2")
if k and k:FindFirstChild("KlatkiLokalne") then k.KlatkiLokalne:Destroy() end
_G.TW2_AKTOR = nil
return "OK"
'''


def klipy_do_zdjec(w, d, wszystkie):
    nazwy = []
    for akcja in ("atak",):
        if w["klipy"].get(akcja):
            nazwy.append(w["klipy"][akcja])
    for kl in w["umiejetnosci"].values():
        if kl and kl not in nazwy:
            nazwy.append(kl)
    if wszystkie:
        for akcja in ("blok", "unik", "trafienie", "upadek", "radosc", "ruch"):
            kl = w["klipy"].get(akcja)
            if kl and kl not in nazwy:
                nazwy.append(kl)
    else:
        for kl in w.get("zastepcze_klipy", []):
            if kl not in nazwy:
                nazwy.append(kl)
    dl = {k["n"]: k["dl"] / float(k["fps"]) for k in d["klipy"]}
    return [(n, dl[n]) for n in nazwy]


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tylko", default="")
    ap.add_argument("--klatki", type=int, default=8)
    ap.add_argument("--wszystkie", action="store_true", help="też blok/unik/trafienie/upadek/radość/ruch każdego aktora")
    ap.add_argument("--obrys", action="store_true", help="tylko porównanie obrysu na Leśnym Trollu")
    ap.add_argument("--punkty", action="store_true", help="pokaż punkty Punkt_* jako świecące kulki")
    ap.add_argument("--bez-klipow", action="store_true", help="tylko spoczynek")
    ap.add_argument("--przod", action="store_true", help="klipy z przodu 3/4 (twarz, miny) zamiast z boku; pliki *_przod.jpg")
    ap.add_argument("--wyj", default=os.path.join(KATALOG, "klatki"))
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    from PIL import Image, ImageDraw
    os.makedirs(a.wyj, exist_ok=True)
    wybrane = [x for x in a.tylko.split(",") if x] or [w["klucz"] for w in A.AKTORZY]
    raport = {}

    with StudioMCP(timeout=180) as s:
        sid = wybierz_studio(s, a.studio)

        def call(nazwa, args=None, timeout=None):
            x = dict(args or {})
            x["studio_id"] = sid
            return s.call(nazwa, x, timeout=timeout)

        def luau(kod):
            r = call("execute_luau", {"code": kod, "datamodel_type": "Client"}, timeout=120)
            if r["is_error"]:
                raise StudioError(r["text"][:2000])
            t = r["text"].strip()
            if t.startswith("STOP"):
                raise StudioError(t)
            return t

        def tryb_edit():
            return "Current Studio Mode: Edit" in call("get_studio_state")["text"]

        kamera_teraz = {}

        def do_swiata(txt):
            # układ sceny (Ustawienia.scena): środek (0, 1, 250), LookVector = +Z świata, więc lokalne (x, y, z) → (−x, y, −z)
            x, y, z = (float(v) for v in txt.split(","))
            return [-x, 1.0 + y, 250.0 - z]

        def pozuj(klip, czas, kam, cel):
            kamera_teraz["k"], kamera_teraz["c"] = do_swiata(kam), do_swiata(cel)
            return luau(POZA.replace("__KLIP__", klip).replace("__CZAS__", czas).replace("__KAMERA__", kam).replace("__CEL__", cel))

        def zrzut(podpis):
            nie_usypiaj()
            # w Play narzędzie zrzutu samo ustawia kamerę (bez tego wraca do kamery gracza), więc podajemy ją jawnie
            r = call("screen_capture", {"capture_id": "tw2_klatka", "camera_position": kamera_teraz["k"],
                                        "look_at_position": kamera_teraz["c"]}, timeout=120)
            if r["is_error"] or not r["images"]:
                raise StudioError("zrzut: %s" % (r["text"] or "brak obrazu")[:300])
            im = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
            w, h = im.size
            m = min(w, h)
            im = im.crop(((w - m) // 2, (h - m) // 2, (w - m) // 2 + m, (h - m) // 2 + m)).resize((BOK, BOK), Image.LANCZOS)
            ImageDraw.Draw(im).text((8, 6), podpis, fill=(255, 255, 255))
            return im

        def arkusz(kafle, sciezka, kolumny=4):
            kol = min(kolumny, len(kafle))
            wiersze = (len(kafle) + kol - 1) // kol
            ark = Image.new("RGB", (kol * BOK, wiersze * BOK), (20, 18, 24))
            for i, im in enumerate(kafle):
                ark.paste(im, ((i % kol) * BOK, (i // kol) * BOK))
            ark.save(sciezka, "JPEG", quality=82)
            print("  arkusz:", os.path.relpath(sciezka, REPO), flush=True)

        if not tryb_edit():
            sys.exit("Studio nie jest w trybie Edit — nie zaczynam.")
        nie_usypiaj()
        try:
            print("Play:", call("start_stop_play", {"is_start": True})["text"][:80], flush=True)
            for _ in range(120):
                if "Client" in call("get_studio_state")["text"]:
                    try:
                        if luau('local k = workspace:FindFirstChild("TestWalki2") return tostring(k and k:GetAttribute("KlientGotowy"))') == "true":
                            break
                    except StudioError:
                        pass
                time.sleep(0.5)
            time.sleep(1.5)
            print("przygotowanie:", luau(PRZYGOTUJ), flush=True)

            def postaw(klucz, obrys="brak"):
                w = A.PO_KLUCZU[klucz]
                kier = 1 if w["rola"] == "klasa" else -1          # klasa patrzy w prawo ekranu, przeciwnik w lewo
                return json.loads(luau(POSTAW.replace("__KLUCZ__", klucz).replace("__OBRYS__", obrys)
                                       .replace("__KIERUNEK__", str(kier)).replace("__PUNKTY__", "true" if a.punkty else "false")))

            def kamera(d, bok=True, kat=0.0, kier=1):
                h = max(d["wymiary"]["wysokosc"], 2.5)
                zasieg = max(d["wymiary"]["promien"], h * 0.6)
                odl = max(9.0, min(zasieg * 2.0, h * 0.8 + 4.0) + h * 1.4)   # maczuga leżąca na ziemi zawyża zasięg
                odl = min(odl, 27.0)   # Strażnik Gaju (14,5 studa): z dalszej kamery kadr zasłaniała tablica areny
                if bok:   # widok z boku sceny (jak w walce), lekko z góry
                    return "%.2f, %.2f, %.2f" % (odl * 0.18, h * 0.62, odl), "0, %.2f, 0" % (h * 0.45)
                import math
                return ("%.2f, %.2f, %.2f" % (odl * 0.75 * math.cos(kat) * kier, h * 0.6, odl * 0.75 * math.sin(kat)),
                        "0, %.2f, 0" % (h * 0.48))

            if a.obrys:
                d = A.wczytaj("lesny_troll")
                kafle = []
                for tryb, opis in (("brak", "bez obrysu"), ("highlight", "Highlight"), ("skorupa", "skorupa")):
                    info = postaw("lesny_troll", tryb)
                    raport["obrys_" + tryb] = info
                    kam, cel = kamera(d)
                    pozuj("idle", "0.5", kam, cel)
                    im = zrzut("%s: %d czesci + %d skorup" % (opis, info["czesci"], info["skorupy"]))
                    im.save(os.path.join(a.wyj, "obrys_%s.jpg" % tryb), quality=90)
                    kafle.append(im)
                    # bliżej: głowa i ramię
                    h = d["wymiary"]["wysokosc"]
                    pozuj("idle", "0.5", "%.2f, %.2f, %.2f" % (1.5, h * 0.75, h * 0.9), "0, %.2f, 0" % (h * 0.7))
                    kafle.append(zrzut("%s (zblizenie)" % opis))
                arkusz(kafle, os.path.join(a.wyj, "obrys_porownanie.jpg"), kolumny=2)
            else:
                for klucz in wybrane:
                    w = A.PO_KLUCZU[klucz]
                    d = A.wczytaj(klucz)
                    kier = 1 if w["rola"] == "klasa" else -1
                    info = postaw(klucz)
                    raport[klucz] = {"klon": info, "odchylka_stawow": 0.0}
                    print("%s: klon %d brył, %d instancji, %.1f ms" % (klucz, info["czesci"], info["instancje"], info["ms"]), flush=True)
                    # spoczynek: z boku (jak w walce) i trzy czwarte z przodu
                    kafle = []
                    import math
                    for nazwa, (kam, cel) in (("bok", kamera(d)), ("przod 3/4", kamera(d, bok=False, kat=math.radians(30), kier=kier)),
                                              ("przod", kamera(d, bok=False, kat=0.0, kier=kier)), ("tyl 3/4", kamera(d, bok=False, kat=math.radians(150), kier=kier))):
                        # kat liczony od kierunku, w który patrzy aktor (oś X sceny), w stronę kamery (+Z sceny)
                        wynik = pozuj(w["klipy"]["spoczynek"], "0", kam, cel)
                        kafle.append(zrzut("%s spoczynek - %s" % (klucz, nazwa)))
                    arkusz(kafle, os.path.join(a.wyj, "%s_spoczynek.jpg" % klucz), kolumny=4)
                    if a.bez_klipow:
                        continue
                    for klip, dlug in klipy_do_zdjec(w, d, a.wszystkie):
                        kafle = []
                        kam, cel = kamera(d, bok=False, kat=math.radians(30), kier=kier) if a.przod else kamera(d)
                        for i in range(a.klatki):
                            t = dlug * i / float(a.klatki - 1)
                            wynik = pozuj(klip, "%.4f" % t, kam, cel)
                            raport[klucz]["odchylka_stawow"] = max(raport[klucz]["odchylka_stawow"], float(wynik.split()[1]))
                            chw = d["chwile"].get(klip)
                            znak = " *TRAF" if chw is not None and abs(t - chw) < dlug / (2.0 * (a.klatki - 1)) else ""
                            kafle.append(zrzut("%s %s t=%.2f s%s" % (klucz, klip, t, znak)))
                        arkusz(kafle, os.path.join(a.wyj, "%s_%s%s.jpg" % (klucz, klip, "_przod" if a.przod else "")))
            luau(SPRZATAJ)
        finally:
            print("Stop:", call("start_stop_play", {"is_start": False})["text"][:80], flush=True)
            for _ in range(40):
                time.sleep(0.5)
                if tryb_edit():
                    break
            print("Studio w trybie Edit:", tryb_edit(), flush=True)
            if raport:
                with open(os.path.join(a.wyj, "raport_klatek.json" if not a.obrys else "raport_obrysu.json"), "w", encoding="utf-8") as f:
                    json.dump(raport, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
