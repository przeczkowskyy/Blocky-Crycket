#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba postaci niezależnych w trybie PLAY w Studio — punkty N00–N14, wynik w <folder>/wynik_play.json (POZA repo).

    python -B swiat/npc_gra/testy/proba_play.py --sprawdz                       # bez Studio: lista punktów i składnia Luau
    python -B swiat/npc_gra/testy/proba_play.py <folder wyników poza repo> [--bez-zrzutow] [--studio <id>]

Wymaga: kontener Workspace/NpcGra (zbuduj.py), mapa bazaru w Studio, Studio w trybie Edit. Play tylko na czas próby
(SesjaPlay z swiat/test_walki2/testy/sesja_play.py zatrzymuje go zawsze i sprawdza powrót do Edit).
  N00 Edit: kontener, źródła i skrót = lokalne, sygnały, zero części postaci
  N01 Play (serwer): SerwerNpc gotowy, wyłącznik włączony, 12 rigów w danych
  N02 klient przy karczmie: NPC bazaru w zasięgu zbudowane (bryły = dane), żadna część nie ma kolizji, dotyku ani
      promieni, stopy na posadzce, figury z klocków schowane u gracza (kolizje figur zostają)
  N03 tabliczki: imię i rola (rola z miejsca bazaru)
  N04 spoczynek: głowy NPC w zasięgu animacji się ruszają; NPC dalej niż zasięg stoją (uśpione)
  N05 powitanie: po podejściu do zbrojmistrza klip powitania i tekst nad tabliczką — raz
  N06 wzrok: gracz z lewej strony opiekunki → głowa i tułów skręcają w lewo, w stronę gracza
  N07 gest na polecenie: Polecenie „graj” → gest, po jego czasie powrót do spoczynku
  N08 trener z kotwicy i z polecenia: kotwica z tagiem (serwer) i „postaw” (klient) stawiają NPC, „usun” go zdejmuje
  N09 wyłącznik: false → NPC znikają, figury z klocków znów widać; true → NPC wracają
  N10 podpowiedź E karczmy istnieje, jest włączona i w zasięgu gracza na stoisku
  N11 czas pętli pakietu i czas klatki przy NPC
  N12 konsola bez wpisów pakietu
  N13 zrzuty do swiat/npc_gra/klatki/
  N14 po próbie Studio wróciło do trybu Edit
"""
import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (REPO, os.path.join(REPO, "tools"), os.path.join(REPO, "tools", "walka"),
           os.path.join(REPO, "swiat", "test_walki2", "testy"), os.path.join(REPO, "swiat", "test_walki_roblox")):
    if _s not in sys.path:
        sys.path.append(_s)
if PAKIET in sys.path:
    sys.path.remove(PAKIET)
sys.path.insert(0, PAKIET)                             # własne moduły pakietu zawsze pierwsze (dane, zbuduj)
import dane as DN  # noqa: E402
import zbuduj as ZB  # noqa: E402

KLATKI = os.path.join(PAKIET, "klatki")
PUNKTY = ["N%02d" % i for i in range(15)]

PRZENIES = r'''
local gracz = game:GetService("Players"):GetPlayers()[1]
local hrp = gracz and gracz.Character and gracz.Character:FindFirstChild("HumanoidRootPart")
if not hrp then return "brak" end
hrp.AssemblyLinearVelocity = Vector3.zero
hrp.CFrame = CFrame.lookAt(Vector3.new(__POZ__), Vector3.new(__NA__))
return "ok"
'''

SERWER_STAN = r'''
local HS = game:GetService("HttpService")
local k = workspace:FindFirstChild("__KONTENER__")
if not k then return HS:JSONEncode({ jest = false }) end
local w = k.Sygnaly.SterowanieSerwera:Invoke("stan") or {}
w.jest = true
w.serwerGotowy = k:GetAttribute("SerwerGotowy")
return HS:JSONEncode(w)
'''

SERWER_WLACZ = r'''
return tostring(workspace.__KONTENER__.Sygnaly.SterowanieSerwera:Invoke("wlacz", __WARTOSC__))
'''

KLIENT_STAN = r'''
local HS = game:GetService("HttpService")
local k = workspace:WaitForChild("__KONTENER__", 10)
if not k or not k:GetAttribute("KlientGotowy") then return HS:JSONEncode({ gotowy = false }) end
return HS:JSONEncode(k.Sygnaly.SterowanieKlienta:Invoke("stan"))
'''

KLIENT_POLECENIE = r'''
local HS = game:GetService("HttpService")
local w = workspace.__KONTENER__.Sygnaly.Polecenie:Invoke(__ARGI__)
return HS:JSONEncode({ w = w })
'''

KLIENT_ZERUJ = r'''
return tostring(workspace.__KONTENER__.Sygnaly.SterowanieKlienta:Invoke("pomiar_zeruj"))
'''

KLIENT_FIGURY = r'''
local HS = game:GetService("HttpService")
local w = {}
for _, sciezka in { __SCIEZKI__ } do
	local o = game
	for kawalek in string.gmatch(sciezka, "[^/]+") do
		o = o and o:FindFirstChild(kawalek)
	end
	local ukryte, widoczne, kolizje = 0, 0, 0
	if o then
		for _, p in o:GetDescendants() do
			if p:IsA("BasePart") and p.Transparency < 1 then
				if p.LocalTransparencyModifier >= 1 then ukryte += 1 else widoczne += 1 end
				if p.CanCollide then kolizje += 1 end
			end
		end
	end
	w[sciezka] = { jest = o ~= nil, ukryte = ukryte, widoczne = widoczne, kolizje = kolizje }
end
return HS:JSONEncode(w)
'''

SERWER_KOTWICA = r'''
local kont = workspace.__KONTENER__
__KOTWICA__
return "ok"
'''

SERWER_BEZ_KOTWICY = r'''
local a = workspace.__KONTENER__.__KOTWICE__:FindFirstChild("__NAZWA__")
if a then a:Destroy() end
return tostring(a ~= nil)
'''

SERWER_PODPOWIEDZ = r'''
local HS = game:GetService("HttpService")
local o = game
for kawalek in string.gmatch("__SCIEZKA__", "[^/]+") do
	o = o and o:FindFirstChild(kawalek)
end
local pp = o and o:FindFirstChildWhichIsA("ProximityPrompt", true)
if not pp then return HS:JSONEncode({ jest = false }) end
local cz = pp.Parent
return HS:JSONEncode({ jest = true, wlaczona = pp.Enabled, zasieg = pp.MaxActivationDistance, tekst = pp.ActionText,
	obiekt = pp.ObjectText, poz = { cz.Position.X, cz.Position.Y, cz.Position.Z } })
'''

KLATKA = r'''
local RS = game:GetService("RunService")
local n, suma, maks = 0, 0, 0
local t0 = os.clock()
while os.clock() - t0 < 3 do
	local dt = RS.RenderStepped:Wait()
	n += 1
	suma += dt
	maks = math.max(maks, dt)
end
return string.format("%.2f %.2f %d", suma / n * 1000, maks * 1000, n)
'''

SCHOWAJ = r'''
local SG = game:GetService("StarterGui")
local gracz = game:GetService("Players").LocalPlayer
pcall(function() SG:SetCoreGuiEnabled(Enum.CoreGuiType.All, false) end)
for _, g in gracz.PlayerGui:GetChildren() do
	if g:IsA("ScreenGui") and g.Enabled then
		g.Enabled = false
		g:SetAttribute("NpcProbaSchowane", true)
	end
end
local hum = gracz.Character and gracz.Character:FindFirstChildOfClass("Humanoid")
if hum then
	hum.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
end
game:GetService("ProximityPromptService").Enabled = false
return "ok"
'''

POKAZ = r'''
local SG = game:GetService("StarterGui")
local gracz = game:GetService("Players").LocalPlayer
for _, g in gracz.PlayerGui:GetChildren() do
	if g:IsA("ScreenGui") and g:GetAttribute("NpcProbaSchowane") then
		g.Enabled = true
		g:SetAttribute("NpcProbaSchowane", nil)
	end
end
pcall(function() SG:SetCoreGuiEnabled(Enum.CoreGuiType.All, true) end)
local hum = gracz.Character and gracz.Character:FindFirstChildOfClass("Humanoid")
if hum then
	hum.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.Viewer
end
game:GetService("ProximityPromptService").Enabled = true
return "ok"
'''


def log(*a):
    print("[%s]" % time.strftime("%H:%M:%S"), *a, flush=True)


def wek(v):
    return ", ".join(repr(float(x)) for x in v)


def miejsce_gracza(s, przod, lewo=0.0, wys=3.2):
    """Punkt przed NPC stanowiska s: `przod` studów ku przodowi NPC i `lewo` ku jego lewej; korzeń gracza nad ziemią."""
    kx, kz = s["kier"]
    return [s["poz"][0] + kx * przod + kz * lewo, s["poz"][1] + wys, s["poz"][2] + kz * przod - kx * lewo]


def kody(U, S):
    """Wszystkie kawałki Luau próby z przykładowymi wartościami — do kontroli składni bez Studio."""
    kont = U["kontener"]
    s = S[0]
    return [
        ("PRZENIES", ZB.wstaw(PRZENIES, POZ=wek(s["stoisko"]), NA=wek(s["poz"]))),
        ("SERWER_STAN", ZB.wstaw(SERWER_STAN, KONTENER=kont)), ("SERWER_WLACZ", ZB.wstaw(SERWER_WLACZ, KONTENER=kont, WARTOSC="true")),
        ("KLIENT_STAN", ZB.wstaw(KLIENT_STAN, KONTENER=kont)),
        ("KLIENT_POLECENIE", ZB.wstaw(KLIENT_POLECENIE, KONTENER=kont, ARGI='"graj", "zbrojownia", "gest"')),
        ("KLIENT_ZERUJ", ZB.wstaw(KLIENT_ZERUJ, KONTENER=kont)),
        ("KLIENT_FIGURY", ZB.wstaw(KLIENT_FIGURY, SCIEZKI=json.dumps(s["zastepuje"]))),
        ("SERWER_KOTWICA", ZB.wstaw(SERWER_KOTWICA, KONTENER=kont, KOTWICA=ZB.kotwica_luau(
            U, "trener_sila", "proba_kotwica", (0, 0, 0), (0, 1), "kont:FindFirstChild(%s)" % json.dumps(ZB.FOLDER_KOTWIC)))),
        ("SERWER_BEZ_KOTWICY", ZB.wstaw(SERWER_BEZ_KOTWICY, KONTENER=kont, KOTWICE=ZB.FOLDER_KOTWIC, NAZWA="Kotwica_proba_kotwica")),
        ("SERWER_PODPOWIEDZ", ZB.wstaw(SERWER_PODPOWIEDZ, SCIEZKA="Workspace/MiasteczkoBazar")),
        ("KLATKA", KLATKA), ("SCHOWAJ", SCHOWAJ), ("POKAZ", POKAZ), ("STAN", ZB.kod_stanu(U)),
    ]


def sprawdz(U, S):
    try:
        import luau_mini as LM
    except ImportError:
        LM = None
    zle = []
    for nazwa, kod in kody(U, S):
        if "__" in kod:
            zle.append("%s: niewstawione pole" % nazwa)
        if LM is not None:
            try:
                LM.Parser(kod, nazwa, LM.Interpreter()).program()
            except Exception as e:  # noqa: BLE001
                zle.append("%s: %s" % (nazwa, str(e)[:160]))
    print("próba NPC: %d punktów (%s–%s), %d kawałków Luau, składnia: %s" % (
        len(PUNKTY), PUNKTY[0], PUNKTY[-1], len(kody(U, S)),
        ("bez błędów" if not zle else "; ".join(zle)) if LM is not None else "nie sprawdzona (brak luau_mini)"))
    return 1 if zle else 0


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Próba postaci niezależnych (Play)")
    ap.add_argument("folder", nargs="?", help="folder wyników POZA repozytorium")
    ap.add_argument("--sprawdz", action="store_true", help="bez Studio: lista punktów i składnia kawałków Luau")
    ap.add_argument("--bez-zrzutow", action="store_true")
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    U, D, R, pliki = DN.wszystkie_pliki()
    S = DN.stanowiska_bazaru(U)
    if a.sprawdz:
        return sprawdz(U, S)
    if not a.folder:
        ap.error("podaj folder wyników (poza repozytorium) albo --sprawdz")
    folder = os.path.abspath(a.folder)
    if os.path.commonpath([folder, REPO]) == REPO:
        sys.exit("Folder wyników musi leżeć poza repozytorium.")
    os.makedirs(folder, exist_ok=True)
    kont, P, Zs = U["kontener"], U["proba"], U["zasiegi"]
    st = {s["klucz"]: s for s in S}
    wyniki, dane = [], {}

    def punkt(kod, ok, opis):
        wyniki.append({"punkt": kod, "wynik": "OK" if ok is True else ("?" if ok is None else "BŁĄD"), "opis": opis})
        log("%s %s — %s" % (kod, wyniki[-1]["wynik"], opis))

    from sesja_play import SesjaPlay  # noqa: E402  (tylko odczyt: wspólna obsługa Play)
    from studio_mcp import StudioMCP  # noqa: E402
    from cel_studio import wybierz_studio  # noqa: E402

    with StudioMCP(timeout=120) as s:
        sid = wybierz_studio(s, a.studio)
        edit = json.loads(s.call("execute_luau", {"code": ZB.kod_stanu(U), "datamodel_type": "Edit", "studio_id": sid})["text"])
    dane["edit"] = edit
    oczek = {n: len(t.encode("utf-8")) for _, n, _, _, t in ZB.zrodla(pliki)}
    zle = []
    if not edit.get("jest"):
        zle.append("brak kontenera Workspace/%s" % kont)
    else:
        zle += ["%s: %s bajtów zamiast %d" % (n, (edit["zrodla"].get(n) or {}).get("bajtow"), b) for n, b in oczek.items()
                if (edit["zrodla"].get(n) or {}).get("bajtow") != b]
        if edit.get("skrot") != D["skrot"]:
            zle.append("skrót %s ≠ lokalny %s" % (edit.get("skrot"), D["skrot"]))
        if sorted(edit.get("sygnaly", [])) != sorted(ZB.SYGNALY):
            zle.append("sygnały %s" % edit.get("sygnaly"))
        if edit.get("czesci", 0) != len(edit.get("kotwice", [])):
            zle.append("części w kontenerze: %s (poza kotwicami ma być 0)" % edit.get("czesci"))
    punkt("N00", not zle, "Edit: %d źródeł = lokalne, skrót %s, kotwic %d" % (len(oczek), D["skrot"], len(edit.get("kotwice", [])))
          if not zle else "; ".join(zle))

    def czekaj(sp, warunek, limit=6.0, co=0.3):
        """Odczyt klienta powtarzany do spełnienia warunku albo limitu czasu → ostatni odczyt."""
        t0 = time.time()
        while True:
            k = json.loads(sp.luau(ZB.wstaw(KLIENT_STAN, KONTENER=kont), "Client", timeout=60))
            if (k.get("gotowy") and warunek(k)) or time.time() - t0 > limit:
                return k
            time.sleep(co)

    def stanowisko(k, klucz):
        return next((x for x in k.get("stanowiska", []) if x["klucz"] == klucz), None)

    def przenies(sp, poz, na):
        return sp.luau(ZB.wstaw(PRZENIES, POZ=wek(poz), NA=wek(na)), "Server", timeout=60)

    def polecenie(sp, *argi):
        return json.loads(sp.luau(ZB.wstaw(KLIENT_POLECENIE, KONTENER=kont, ARGI=", ".join(argi)), "Client", timeout=60)).get("w")

    with SesjaPlay(a.studio) as sp:
        time.sleep(2.0)
        ser = json.loads(sp.luau(ZB.wstaw(SERWER_STAN, KONTENER=kont), "Server"))
        dane["serwer"] = ser
        punkt("N01", bool(ser.get("gotowy") and ser.get("wlaczone") and ser.get("rigow") == len(R) and ser.get("skrot") == D["skrot"]),
              "serwer: gotowy %s, włączone %s, rigów %s, skrót %s" % (ser.get("gotowy"), ser.get("wlaczone"), ser.get("rigow"), ser.get("skrot")))

        # N02–N04: gracz na stoisku karczmy
        ka = st["karczma"]
        przenies(sp, [ka["stoisko"][0], ka["stoisko"][1] + 3.2, ka["stoisko"][2]], [ka["poz"][0], ka["stoisko"][1] + 3.2, ka["poz"][2]])
        k = czekaj(sp, lambda k: all(x["zbudowany"] for x in k["stanowiska"] if (x.get("odl") or 1e9) <= Zs["budowa"] - 5))
        dane["klient"] = k
        zle, zbud = [], 0
        for x in k.get("stanowiska", []):
            s_ = st.get(x["klucz"])
            if not s_ or (x.get("odl") or 1e9) > Zs["budowa"] - 5:
                continue
            r = R[x["npc"]]
            if not x["zbudowany"]:
                zle.append("%s: nie zbudowany (odl %.0f)" % (x["klucz"], x["odl"]))
                continue
            zbud += 1
            if x["bryl"] != len(r["czesci"]) or x["czesci"] != DN.czesci_w_studio(r):
                zle.append("%s: brył %s/%d, części %s/%d" % (x["klucz"], x["bryl"], len(r["czesci"]), x["czesci"], DN.czesci_w_studio(r)))
            if x["fizyka"]:
                zle.append("%s: %d części z kolizją, dotykiem albo promieniami" % (x["klucz"], x["fizyka"]))
            if x["klucz"] != "mistrz_gier" and abs(x["spod"]) > 0.08:
                zle.append("%s: spód %.2f st od posadzki" % (x["klucz"], x["spod"]))
            if not x.get("figura") or x.get("figuraWidoczne", 1) != 0 or x.get("figuraUkryte", 0) < 20:
                zle.append("%s: figura z klocków nie schowana (%s widocznych, %s ukrytych)" % (x["klucz"], x.get("figuraWidoczne"), x.get("figuraUkryte")))
        fig = json.loads(sp.luau(ZB.wstaw(KLIENT_FIGURY, SCIEZKI=", ".join(json.dumps(s_["zastepuje"]) for s_ in S)), "Client", timeout=60))
        dane["figury"] = fig
        bez_kolizji = [p for p, v in fig.items() if v["jest"] and v["kolizje"] == 0]
        if bez_kolizji:
            zle.append("figury bez kolizji (kamera i przejście): %s" % ", ".join(bez_kolizji))
        punkt("N02", not zle and zbud >= 3, "zbudowanych NPC bazaru %d (klient: %d stanowisk, rusza się %d); brył %d; figury schowane, ich kolizje zostały"
              % (zbud, len(k.get("stanowiska", [])), k.get("ruszaSie", 0), sum(x.get("bryl", 0) for x in k.get("stanowiska", [])))
              if not zle else "; ".join(zle))
        zle = []
        for x in k.get("stanowiska", []):
            s_ = st.get(x["klucz"])
            if s_ and x["zbudowany"] and x.get("napisy") != [D["npc"][x["npc"]]["imie"], s_["rola"]]:
                zle.append("%s: napisy %s" % (x["klucz"], x.get("napisy")))
        punkt("N03", not zle and zbud > 0, "tabliczki: %s" % "; ".join(" / ".join(x["napisy"]) for x in k["stanowiska"] if x.get("napisy"))
              if not zle else "; ".join(zle))
        time.sleep(0.5)
        k2 = czekaj(sp, lambda k: True, limit=0)
        zle, ruch = [], []
        for x in k.get("stanowiska", []):
            y = stanowisko(k2, x["klucz"])
            if not (x["zbudowany"] and y and y["zbudowany"]):
                continue
            d = sum((p - q) ** 2 for p, q in zip(x["glowaPoz"], y["glowaPoz"])) ** 0.5 + sum(abs(p - q) for p, q in zip(x["glowaPrzod"], y["glowaPrzod"]))
            if x["tryb"] in ("blisko", "daleko") and y["tryb"] in ("blisko", "daleko"):
                ruch.append(d)
                if d < 1e-4:
                    zle.append("%s: głowa stoi (tryb %s)" % (x["klucz"], x["tryb"]))
            elif x["tryb"] == "uspiony" and y["tryb"] == "uspiony" and d > 1e-5:
                zle.append("%s: uśpiony, a głowa się rusza (%.5f)" % (x["klucz"], d))
        punkt("N04", not zle and len(ruch) > 0, "rusza się %d NPC (ruch głowy %.4f–%.4f), uśpionych %d"
              % (len(ruch), min(ruch or [0]), max(ruch or [0]), sum(1 for x in k2["stanowiska"] if x["tryb"] == "uspiony"))
              if not zle else "; ".join(zle))

        # N05: powitanie zbrojmistrza
        zb = st["zbrojownia"]
        przed = (stanowisko(czekaj(sp, lambda k: True, limit=0), "zbrojownia") or {}).get("powitan", 0)
        przenies(sp, miejsce_gracza(zb, 30), zb["poz"])
        time.sleep(1.0)
        przenies(sp, [zb["stoisko"][0], zb["stoisko"][1] + 3.2, zb["stoisko"][2]], [zb["poz"][0], zb["stoisko"][1] + 3.2, zb["poz"][2]])
        k = czekaj(sp, lambda k: (stanowisko(k, "zbrojownia") or {}).get("powitan", 0) > przed, limit=5)
        x = stanowisko(k, "zbrojownia") or {}
        widac = x.get("powitanieWidac")
        time.sleep(D["npc"]["zbrojmistrz"]["dlugosci"]["powitanie"] + 1.0)
        x2 = stanowisko(czekaj(sp, lambda k: True, limit=0), "zbrojownia") or {}
        punkt("N05", x.get("powitan", 0) == przed + 1 and x.get("klip") == "powitanie" and widac is True and x2.get("powitan") == przed + 1
              and x2.get("klip") in ("spoczynek", "gest"),
              "zbrojmistrz: powitań %s → %s, klip %s, tekst widać %s; po klipie: %s, powitań %s"
              % (przed, x.get("powitan"), x.get("klip"), widac, x2.get("klip"), x2.get("powitan")))

        # N06: wzrok opiekunki — gracz przed nią, po jej lewej
        op = st["zagroda_petow"]
        przenies(sp, miejsce_gracza(op, 7, 4), op["poz"])
        time.sleep(2.0)
        x = stanowisko(czekaj(sp, lambda k: (stanowisko(k, "zagroda_petow") or {}).get("zbudowany"), limit=5), "zagroda_petow") or {}
        kat = (x.get("tulow") or 0) + (x.get("glowa") or 0)
        cel = miejsce_gracza(op, 7, 4)
        zgod = None
        if x.get("glowaPoz"):
            dx, dz = cel[0] - x["glowaPoz"][0], cel[2] - x["glowaPoz"][2]
            dl = (dx * dx + dz * dz) ** 0.5
            zgod = (x["glowaPrzod"][0] * dx + x["glowaPrzod"][2] * dz) / dl
        punkt("N06", kat > 0.3 and zgod is not None and zgod > 0.9,
              "opiekunka: skręt tułowia %.2f + głowy %.2f rad (oczekiwane ok. +0,52, w lewo), głowa patrzy na gracza: zgodność kierunku %s"
              % (x.get("tulow") or 0, x.get("glowa") or 0, "%.2f" % zgod if zgod is not None else "?"))

        # N07: gest na polecenie
        czas = polecenie(sp, '"graj"', '"zagroda_petow"', '"gest"')
        x = stanowisko(czekaj(sp, lambda k: True, limit=0), "zagroda_petow") or {}
        oczek_czas = D["npc"]["opiekunka"]["dlugosci"]["gest"]
        time.sleep(oczek_czas + 0.6)
        x2 = stanowisko(czekaj(sp, lambda k: True, limit=0), "zagroda_petow") or {}
        punkt("N07", isinstance(czas, (int, float)) and abs(czas - oczek_czas) < 0.01 and x.get("klip") == "gest" and x2.get("klip") == "spoczynek"
              and polecenie(sp, '"graj"', '"nie_ma"', '"gest"') is False,
              "„graj” gest → %s s (dane %.2f), klip %s, po czasie %s; nieznany klucz → false" % (czas, oczek_czas, x.get("klip"), x2.get("klip")))

        # N08: kotwica (serwer) i „postaw” (klient) obok gracza w zagrodzie
        g = miejsce_gracza(op, 7, 4, wys=0.0)
        kot = ZB.kotwica_luau(U, "trener_sila", "proba_kotwica", (g[0] + 5, g[1], g[2]), (g[0], g[2]),
                              "kont:FindFirstChild(%s)" % json.dumps(ZB.FOLDER_KOTWIC))
        sp.luau(ZB.wstaw(SERWER_KOTWICA, KONTENER=kont, KOTWICA=kot), "Server", timeout=60)
        ok_postaw = polecenie(sp, '"postaw"', '"proba_golem"', '"golem"', "CFrame.lookAt(Vector3.new(%s), Vector3.new(%s))"
                              % (wek((g[0] - 6, g[1], g[2])), wek((g[0], g[1], g[2]))), "1.5")
        k = czekaj(sp, lambda k: all((stanowisko(k, n) or {}).get("zbudowany") for n in ("proba_kotwica", "proba_golem")), limit=6)
        xa, xg = stanowisko(k, "proba_kotwica") or {}, stanowisko(k, "proba_golem") or {}
        sp.luau(ZB.wstaw(SERWER_BEZ_KOTWICY, KONTENER=kont, KOTWICE=ZB.FOLDER_KOTWIC, NAZWA="Kotwica_proba_kotwica"), "Server", timeout=60)
        ok_usun = polecenie(sp, '"usun"', '"proba_golem"')
        k = czekaj(sp, lambda k: not stanowisko(k, "proba_kotwica") and not stanowisko(k, "proba_golem"), limit=5)
        zostaly = [n for n in ("proba_kotwica", "proba_golem") if stanowisko(k, n)]
        punkt("N08", bool(xa.get("zbudowany") and xa.get("bryl") == len(R["trener_sila"]["czesci"]) and abs(xa.get("skala", 0) - D["npc"]["trener_sila"]["skala"]) < 1e-6
                          and xg.get("zbudowany") and xg.get("bryl") == len(R["golem"]["czesci"]) and abs(xg.get("skala", 0) - 1.5) < 1e-6
                          and abs(xg.get("spod", 9)) < 0.1 and ok_postaw is True and ok_usun is True and not zostaly),
              "kotwica → trener Siły (brył %s, skala %s); „postaw” → golem (brył %s, skala %s, spód %s); po usunięciu zostało: %s"
              % (xa.get("bryl"), xa.get("skala"), xg.get("bryl"), xg.get("skala"), xg.get("spod"), zostaly or "nic"))

        # N09: wyłącznik
        sp.luau(ZB.wstaw(SERWER_WLACZ, KONTENER=kont, WARTOSC="false"), "Server")
        k = czekaj(sp, lambda k: not any(x["zbudowany"] for x in k["stanowiska"]), limit=5)
        fig = json.loads(sp.luau(ZB.wstaw(KLIENT_FIGURY, SCIEZKI=", ".join(json.dumps(s_["zastepuje"]) for s_ in S)), "Client", timeout=60))
        wyl_ok = not any(x["zbudowany"] for x in k["stanowiska"]) and all(v["ukryte"] == 0 and v["widoczne"] > 20 for v in fig.values() if v["jest"])
        sp.luau(ZB.wstaw(SERWER_WLACZ, KONTENER=kont, WARTOSC="true"), "Server")
        k = czekaj(sp, lambda k: (stanowisko(k, "zagroda_petow") or {}).get("zbudowany"), limit=5)
        punkt("N09", bool(wyl_ok and (stanowisko(k, "zagroda_petow") or {}).get("zbudowany")),
              "wyłącznik false: NPC 0, figury widoczne (%s); true: NPC wracają (%s)"
              % (", ".join("%d" % v["widoczne"] for v in fig.values() if v["jest"]), (stanowisko(k, "zagroda_petow") or {}).get("zbudowany")))

        # N10: podpowiedź E karczmy
        ZN = DN.czytaj_json(DN.sciezka_repo(U["bazar"]["znaczniki"]))
        zk = DN._znajdz(ZN, "sklepy/karczma")
        pp = json.loads(sp.luau(ZB.wstaw(SERWER_PODPOWIEDZ, SCIEZKA=zk["grupa_zaczepu"] + "/" + zk["czesc_podpowiedzi"]), "Server", timeout=60))
        dane["podpowiedz"] = pp
        odl = None
        if pp.get("jest"):
            odl = sum((p - q) ** 2 for p, q in zip(pp["poz"], [ka["stoisko"][0], ka["stoisko"][1] + 4.5, ka["stoisko"][2]])) ** 0.5
        punkt("N10", bool(pp.get("jest") and pp.get("wlaczona") and odl is not None and odl <= pp["zasieg"]),
              "podpowiedź E karczmy: jest %s, włączona %s, „%s / %s”, %.1f st od głowy gracza na stoisku (zasięg %s)"
              % (pp.get("jest"), pp.get("wlaczona"), pp.get("obiekt"), pp.get("tekst"), odl or -1, pp.get("zasieg")))

        # N11: czas pętli i klatki przy karczmie
        przenies(sp, [ka["stoisko"][0], ka["stoisko"][1] + 3.2, ka["stoisko"][2]], [ka["poz"][0], ka["stoisko"][1] + 3.2, ka["poz"][2]])
        time.sleep(1.5)
        sp.luau(ZB.wstaw(KLIENT_ZERUJ, KONTENER=kont), "Client")
        try:
            kl = sp.luau(KLATKA, "Client", timeout=60).split()
        except Exception as e:  # noqa: BLE001
            kl = None
            log("pomiar klatki: %s" % str(e)[:100])
        k = czekaj(sp, lambda k: True, limit=0)
        dane["petla"] = {"srednio_ms": k.get("petla_ms"), "najwiecej_ms": k.get("petla_maks_ms"), "klatek": k.get("klatek"),
                         "rusza_sie": k.get("ruszaSie"), "klatka": kl}
        ok = k.get("petla_ms") is not None and k["petla_ms"] <= P["prog_petli_ms"] and k.get("bledy") == 0
        punkt("N11", ok if (kl is None or float(kl[0]) <= P["prog_klatki_ms"]) else None,
              "pętla pakietu %.3f ms średnio (najwięcej %.2f, %s klatek, rusza się %s NPC; próg %.1f ms); klatka %s ms"
              % (k.get("petla_ms") or -1, k.get("petla_maks_ms") or -1, k.get("klatek"), k.get("ruszaSie"), P["prog_petli_ms"],
                 kl[0] if kl else "?"))

        # N13: zrzuty
        if a.bez_zrzutow:
            punkt("N13", None, "zrzuty pominięte (--bez-zrzutow)")
        else:
            os.makedirs(KLATKI, exist_ok=True)
            zapisane = []
            try:
                sp.luau(SCHOWAJ, "Client")
                for klucz in ("karczma", "mistrz_gier", "sklep_magiczny", "zbrojownia", "training_center", "zagroda_petow"):
                    s_ = st[klucz]
                    stoi = miejsce_gracza(s_, 12, 3)
                    przenies(sp, stoi, s_["poz"])
                    time.sleep(1.2)
                    oko = miejsce_gracza(s_, 9, -2.5, wys=5.5)
                    im = sp.zrzut(oko, [s_["poz"][0], s_["poz"][1] + 4.2, s_["poz"][2]])
                    if im.width > 1600:
                        im = im.resize((1600, round(im.height * 1600 / im.width)))
                    sc = os.path.join(KLATKI, "npc_%s.jpg" % klucz)
                    im.save(sc, quality=88)
                    zapisane.append(os.path.basename(sc))
            finally:
                sp.luau(POKAZ, "Client")
            punkt("N13", len(zapisane) == 6, "zrzuty: %s" % ", ".join(zapisane))

        kons = sp.konsola()
        linie = [l for l in kons.splitlines() if U["prefiks"].strip() in l or "KlientNpc" in l or "SerwerNpc" in l or "RigNpc" in l]
        with open(os.path.join(folder, "konsola.txt"), "w", encoding="utf-8") as f:
            f.write(kons)
        punkt("N12", not linie, "konsola bez wpisów pakietu" if not linie else "wpisy pakietu w konsoli: " + " | ".join(linie[:4]))
    edit_po = getattr(sp, "edit_po", None)
    punkt("N14", edit_po is True, "Studio po próbie w trybie Edit: %s" % edit_po)
    wyniki.sort(key=lambda w: w["punkt"])
    with open(os.path.join(folder, "wynik_play.json"), "w", encoding="utf-8") as f:
        json.dump({"kiedy": time.strftime("%Y-%m-%d %H:%M"), "skrot": D["skrot"], "wyniki": wyniki, "dane": dane}, f,
                  ensure_ascii=False, indent=1)
    ile = {w: sum(1 for x in wyniki if x["wynik"] == w) for w in ("OK", "?", "BŁĄD")}
    log("RAZEM: %d × OK, %d × ?, %d × BŁĄD" % (ile["OK"], ile["?"], ile["BŁĄD"]))
    return 1 if ile["BŁĄD"] else 0


if __name__ == "__main__":
    sys.exit(main())
