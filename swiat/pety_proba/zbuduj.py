#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buduje w Roblox Studio kontener Workspace/PetyProba — jajka i pety na próbę (serwer zakupu jajek dla jajek ze scenką
Pawła, pet przy graczu, zagroda w bazarze, sprzedaż petów). Status: propozycja (PROJEKT.md). Od 26.11.2026 BEZ
starych inkubatorów (jajko z klocków, tablica szans, punkt E): pełna budowa usuwa je ze Studio razem ze starym
kontenerem (zostaje tylko to, co niżej).

    python -B swiat/pety_proba/zbuduj.py --sucho      # bez Studio: dane, kontrola Luau, strażniki, plan budowy
    python -B swiat/pety_proba/zbuduj.py              # buduje / odbudowuje kontener (Studio w trybie Edit)
    python -B swiat/pety_proba/zbuduj.py --skrypty    # tylko moduły i skrypty do istniejącego kontenera
    python -B swiat/pety_proba/zbuduj.py --usun       # usuwa Workspace/PetyProba (gra wraca do stanu sprzed próby)
    python -B swiat/pety_proba/zbuduj.py --studio <studio_id>   # gdy otwartych jest kilka okien Studio

Co powstaje (tylko w Workspace/PetyProba z atrybutem Wygenerowane = true; cudzych obiektów budowa NIE zmienia —
mapę bazaru tylko czyta promieniem w dół, żeby postawić tablicę zagrody na gruncie):
  Moduly/DanePetow, Moduly/LogikaPetow, Moduly/RigPetow, Moduly/Rigi/*   ModuleScript (zrodla/; dane i rigi
                                                                          wygenerowane przez dane_petow.py)
  SerwerPetow (RunContext = Server), KlientPetow (RunContext = Client)
  Zdalne/ZdarzeniaPetow             RemoteEvent ("wyklucie", "odmowa", "lista", "wybrany", "okno" do klienta;
                                    "lista", "wybierz", "odstaw", "czekaj" do serwera)
  Zdalne/SprzedajPety               RemoteFunction (26.11.2026): klient (okno Pets) → serwer, lista petów do sprzedania
  Sygnaly/SterowanieSerwera, Sygnaly/SterowanieKlienta   BindableFunction — haczyki (zakup ze scenki jajka, testy)
  Zagroda/Tablica (+ słupki, daszek), Zagroda/E wybor (zapasowe E — gdy nie ma MiasteczkoBazarGra)
Atrybuty kontenera: Wygenerowane, Zrodlo, Zbudowano, Skrot.

Zasady (wspólne miejsce Team Create): okno wybiera swiat/test_walki_roblox/cel_studio.py (jedno okno albo --studio,
zawsze placeId gry); KAŻDY wysyłany kod sprawdza game.PlaceId i tryb Edit; ruszany jest tylko własny kontener (obiekt
o tej nazwie bez atrybutu Wygenerowane → STOP); punkty historii przed i po (Ctrl+Z cofa całość); nic nie jest
zapisywane ani publikowane, Lighting nietknięty. --sucho nie importuje studio_mcp ani cel_studio.
"""
import argparse
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if not sys.path or sys.path[0] != TU:
    sys.path.insert(0, TU)
import dane_petow as DANE  # noqa: E402
import sprawdz_luau_petow as SLP  # noqa: E402

SL = SLP.SL
MIEJSCE = 129485428021967  # placeId miejsca gry (to samo co swiat/test_walki_roblox/cel_studio.py)
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
LIMIT_ZRODLA = 199000
ZRODLO = "swiat/pety_proba"
ZRODLA = os.path.join(TU, "zrodla")
KONTENER = "PetyProba"

SKRYPTY_STALE = [
    ("DanePetow.luau", "ModuleScript", "Moduly/DanePetow", None),
    ("LogikaPetow.luau", "ModuleScript", "Moduly/LogikaPetow", None),
    ("RigPetow.luau", "ModuleScript", "Moduly/RigPetow", None),
    ("SerwerPetow.server.luau", "Script", "SerwerPetow", "Server"),
    ("KlientPetow.client.luau", "Script", "KlientPetow", "Client"),
]
FOLDERY = ["Moduly", "Moduly/Rigi", "Zdalne", "Sygnaly", "Zagroda"]
TRWALE = ["Zagroda"]   # Model z ModelStreamingMode = Persistent (streaming nie wypycha)
INNE = [
    ("RemoteEvent", "Zdalne/ZdarzeniaPetow"),
    ("RemoteFunction", "Zdalne/SprzedajPety"),
    ("BindableFunction", "Sygnaly/SterowanieSerwera"),
    ("BindableFunction", "Sygnaly/SterowanieKlienta"),
]


def skrypty():
    """Lista (plik względem zrodla/, klasa, ścieżka w kontenerze, RunContext) — stałe + jeden moduł na rig."""
    w = list(SKRYPTY_STALE[:3])
    rigi = sorted(os.listdir(os.path.join(ZRODLA, "rigi"))) if os.path.isdir(os.path.join(ZRODLA, "rigi")) else []
    for plik in rigi:
        if plik.endswith(".luau"):
            w.append(("rigi/" + plik, "ModuleScript", "Moduly/Rigi/" + plik[:-5], None))
    return w + list(SKRYPTY_STALE[3:])


NAGLOWEK_MIEJSCA = ('if game.PlaceId ~= __MIEJSCE__ then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end\n'
                    'if game:GetService("RunService"):IsRunning() then return "STOP: Studio jest w trybie Play — buduję tylko w trybie Edit" end\n')

START = r'''
local CH = game:GetService("ChangeHistoryService")
local nazwa = "__KONTENER__"
local stare = {}
for _, d in workspace:GetChildren() do
	if d.Name == nazwa then
		if d:GetAttribute("Wygenerowane") ~= true then
			return "STOP: w Workspace jest obiekt '" .. nazwa .. "' bez atrybutu Wygenerowane — nie ruszam cudzej pracy"
		end
		table.insert(stare, d)
	end
end
if __USUN__ then
	if #stare == 0 then
		return "USUNIETO (kontenera nie było)"
	end
	CH:SetWaypoint(nazwa .. ": przed usunięciem")
	for _, d in stare do d:Destroy() end
	CH:SetWaypoint(nazwa .. ": usunięto")
	return "USUNIETO"
end
CH:SetWaypoint(nazwa .. ": przed budową")
for _, d in stare do d:Destroy() end
local f = Instance.new("Folder")
f.Name = nazwa
f:SetAttribute("Wygenerowane", true)
f:SetAttribute("Zrodlo", "__ZRODLO__")
f:SetAttribute("Zbudowano", "__CZAS__")
f:SetAttribute("Skrot", "__SKROT__")
for _, sciezka in { __FOLDERY__ } do
	local czesci = string.split(sciezka, "/")
	local rodzic = f
	for i = 1, #czesci - 1 do
		rodzic = rodzic:FindFirstChild(czesci[i])
	end
	local d
	local trwale = __TRWALE__
	if trwale[czesci[#czesci]] then
		-- części w świecie: Model „Persistent” — klient ma je od wejścia (streaming), jak areny i przymierzalnia
		d = Instance.new("Model")
		d.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
	else
		d = Instance.new("Folder")
	end
	d.Name = czesci[#czesci]
	d.Parent = rodzic
end
for _, w in { __INNE__ } do
	local czesci = string.split(w[2], "/")
	local o = Instance.new(w[1])
	o.Name = czesci[2]
	o.Parent = f:FindFirstChild(czesci[1])
end
f.Parent = workspace
return "OK"
'''

SKRYPT = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera"
end
local sciezka = string.split("__SCIEZKA__", "/")
local rodzic = f
for i = 1, #sciezka - 1 do
	rodzic = rodzic:FindFirstChild(sciezka[i])
	if not rodzic then return "STOP: brak folderu " .. sciezka[i] end
end
local stary = rodzic:FindFirstChild(sciezka[#sciezka])
if stary then stary:Destroy() end
local s = Instance.new("__KLASA__")
s.Name = sciezka[#sciezka]
__RUNCONTEXT__
s.Source = __ZRODLO__
s.Parent = rodzic
return "OK " .. s:GetFullName() .. " (" .. #s.Source .. " znaków)"
'''

# części w świecie (po modułach — wymaga Moduly/DanePetow, RigPetow i rigu jajka); tylko we własnym kontenerze
CZESCI = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera"
end
local M = f.Moduly
local D = require(M.DanePetow)
local Z = D.zagroda
local wyklucz = RaycastParams.new()
wyklucz.FilterType = Enum.RaycastFilterType.Exclude
wyklucz.FilterDescendantsInstances = { f }
local raporty = {}

local function czesc(nazwa, rozmiar, cf, kolor, mat, rodzic, kolizja)
	local p = Instance.new("Part")
	p.Name = nazwa
	p.Anchored = true
	p.Size = rozmiar
	p.CFrame = cf
	p.Color = Color3.fromHex(kolor)
	p.Material = Enum.Material[mat or "SmoothPlastic"]
	p.CanCollide = kolizja == true
	p.CanQuery = kolizja == true
	p.CanTouch = false
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = rodzic
	return p
end

local function punktE(rodzic, nazwa, poz, akcja, obiekt, zasieg, przytrzymaj)
	local p = czesc(nazwa, Vector3.new(0.6, 0.6, 0.6), CFrame.new(poz), "FFC94A", "SmoothPlastic", rodzic, false)
	p.Transparency = 1
	p.CastShadow = false
	local pp = Instance.new("ProximityPrompt")
	pp.Name = "Podpowiedz"
	pp.ActionText = akcja
	pp.ObjectText = obiekt
	pp.KeyboardKeyCode = Enum.KeyCode.E
	pp.HoldDuration = przytrzymaj or 0
	pp.MaxActivationDistance = zasieg
	pp.RequiresLineOfSight = false
	pp.Enabled = false
	pp.Parent = p
	return p
end


local function grunt(x, z, domyslny)
	local r = workspace:Raycast(Vector3.new(x, 60, z), Vector3.new(0, -120, 0), wyklucz)
	if r then
		return r.Position.Y, r.Instance:GetFullName()
	end
	return domyslny, "dane (promień nic nie trafił)"
end

------------------------------------------------------------------ zagroda w bazarze: tablica i zapasowe E
local G = D.polozenia
local zg = f.Zagroda
local tp = G.zagroda_tablica
local kier = Vector3.new(G.zagroda_kier[1], 0, G.zagroda_kier[3])
local yg, zrodloG = grunt(tp[1], tp[3], tp[2])
local sz, wy = Z.tablica_rozmiar[1], Z.tablica_rozmiar[2]
local baza = CFrame.lookAt(Vector3.new(tp[1], yg, tp[3]), Vector3.new(tp[1], yg, tp[3]) + kier)
czesc("Tablica", Vector3.new(sz, wy, 0.3), baza * CFrame.new(0, 1.2 + wy / 2, 0), "6B4A2E", "WoodPlanks", zg, true)
for _, zn in { -1, 1 } do
	czesc("Tablica slupek", Vector3.new(0.4, 1.4 + wy, 0.4), baza * CFrame.new(zn * (sz / 2 + 0.1), (1.4 + wy) / 2, 0.05),
		"4A3220", "Wood", zg, true)
end
czesc("Tablica daszek", Vector3.new(sz + 0.8, 0.3, 0.9), baza * CFrame.new(0, 1.35 + wy + 0.2, 0.05), "4A3220", "Wood", zg, true)
local pe = (baza * CFrame.new(0, 2.4, -2.4)).Position
punktE(zg, "E wybor", pe, Z.napis_e, Z.napis_tablicy .. " (" .. Z.napis_proby .. ")", 8, 0)
table.insert(raporty, string.format("tablica zagrody: grunt %.2f (%s)", yg, zrodloG))
return "OK " .. table.concat(raporty, " | ")
'''

KONIEC = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f then return "STOP: brak kontenera" end
local razem, skrypty, czesci = 0, 0, 0
for _, d in f:GetDescendants() do
	razem += 1
	if d:IsA("LuaSourceContainer") then skrypty += 1 end
	if d:IsA("BasePart") then czesci += 1 end
end
game:GetService("ChangeHistoryService"):SetWaypoint("__KONTENER__: __PUNKT_HISTORII__")
local uwaga = if skrypty ~= __OCZEKIWANE__ then " | UWAGA: skryptów " .. skrypty .. " zamiast __OCZEKIWANE__" else ""
return "instancji: " .. razem .. ", skryptów: " .. skrypty .. ", części: " .. czesci .. ", Skrot = " .. tostring(f:GetAttribute("Skrot")) .. uwaga
'''


def wczytaj(sciezka):
    with open(sciezka, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def dlugi_napis(tekst):
    poziom = 3
    while ("]" + "=" * poziom + "]") in tekst or ("[" + "=" * poziom + "[") in tekst:
        poziom += 1
    return "[" + "=" * poziom + "[\n" + tekst + "]" + "=" * poziom + "]"


def zrodla_pakietu():
    wynik, braki = [], []
    for plik, klasa, sciezka, kontekst in skrypty():
        pelna = os.path.join(ZRODLA, *plik.split("/"))
        if not os.path.isfile(pelna):
            braki.append(plik)
            continue
        wynik.append((sciezka, klasa, kontekst, wczytaj(pelna), plik))
    if braki:
        print("BŁĄD: brak plików w zrodla/: " + ", ".join(braki))
        sys.exit(2)
    return wynik


def sprawdz_offline(zrodla):
    zle, D, _pliki = DANE.aktualny()
    print("dane_petow.py --sprawdz: %s (skrót %s, przypadków %d)" % ("aktualne" if not zle else "NIEAKTUALNE: " + ", ".join(zle),
                                                                    D["skrot"], sum(len(v) for v in D["przypadki"].values())))
    if zle:
        sys.exit("BŁĄD: zrodla/ nieaktualne — uruchom python -B swiat/pety_proba/dane_petow.py")
    if D["kontener"] != KONTENER:
        sys.exit("BŁĄD: D.kontener (%s) ≠ %s" % (D["kontener"], KONTENER))
    bledy, parser = SLP.sprawdz_pliki(SLP.pliki_pakietu(), wypisz=print)
    print("sprawdz_luau_petow.py: %d plików, %s%s" % (len(zrodla), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
                                                     " (z parserem luau_mini)" if parser else " (bez parsera)"))
    if bledy:
        for b in bledy:
            print("  " + b)
        sys.exit("BŁĄD: kontrola Luau")
    for sciezka, klasa, kontekst, tekst, plik in zrodla:
        if not SL.pierwsza_instrukcja(tekst).startswith(STRAZNIK):
            sys.exit("BŁĄD: %s (%s) nie zaczyna się od strażnika Studio" % (sciezka, plik))
        if len(tekst) > LIMIT_ZRODLA:
            sys.exit("BŁĄD: %s ma %d znaków (limit Source 200 000)" % (sciezka, len(tekst)))
    return D


def _napis(s):
    return DANE._napis(s)


def kod_start(usun=False, czas="", skrot=""):
    return (START.replace("__KONTENER__", KONTENER).replace("__USUN__", "true" if usun else "false")
            .replace("__ZRODLO__", ZRODLO).replace("__CZAS__", czas).replace("__SKROT__", skrot)
            .replace("__FOLDERY__", ", ".join(_napis(x) for x in FOLDERY))
            .replace("__TRWALE__", "{ %s }" % ", ".join("[%s] = true" % _napis(x) for x in TRWALE))
            .replace("__INNE__", ", ".join("{%s, %s}" % (_napis(k), _napis(p)) for k, p in INNE)))


def kod_skryptu(sciezka, klasa, kontekst, tekst):
    kod = (SKRYPT.replace("__KONTENER__", KONTENER).replace("__SCIEZKA__", sciezka).replace("__KLASA__", klasa)
           .replace("__RUNCONTEXT__", "s.RunContext = Enum.RunContext.%s" % kontekst if kontekst else ""))
    return kod.replace("__ZRODLO__", dlugi_napis(tekst))


def kod_czesci():
    return CZESCI.replace("__KONTENER__", KONTENER)


def kod_konca(punkt_historii="zbudowano"):
    return (KONIEC.replace("__KONTENER__", KONTENER).replace("__OCZEKIWANE__", str(len(skrypty())))
            .replace("__PUNKT_HISTORII__", punkt_historii))


def wszystkie_kody():
    """Kod wysyłany do Studio (bez skryptów) — do --sucho i do testu parsowania."""
    return {"start": kod_start(czas="x", skrot="x"), "usun": kod_start(True), "czesci": kod_czesci(),
            "koniec": kod_konca()}


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje kontener Workspace/PetyProba w Roblox Studio")
    ap.add_argument("--sucho", action="store_true", help="bez Studio: sprawdź dane i źródła, pokaż plan")
    ap.add_argument("--skrypty", action="store_true", help="tylko moduły i skrypty do istniejącego kontenera")
    ap.add_argument("--usun", action="store_true", help="usuń Workspace/PetyProba")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()

    if a.usun:
        zrodla, D = [], None
    else:
        zrodla = zrodla_pakietu()
        D = sprawdz_offline(zrodla)
        print("Kontener: Workspace/%s · Skrot danych: %s · placeId %d · modułów i skryptów: %d"
              % (KONTENER, D["skrot"], MIEJSCE, len(zrodla)))
        print("  %-26s → %s" % ("Folder", ", ".join(FOLDERY)))
        for klasa, sciezka in INNE:
            print("  %-26s → %s" % (sciezka, klasa))
        for sciezka, klasa, kontekst, tekst, plik in zrodla:
            print("  %-26s → %s%s, zrodla/%s (%d znaków)" % (sciezka, klasa, " [RunContext=%s]" % kontekst if kontekst else "",
                                                           plik, len(tekst)))
        G = D["polozenia"]
        for j in D["jajka"]:
            print("  %s: cena %d (%s; licznik %s), podłoga %d, sprzedaż kopii: %s" % (
                j["id"], DANE.LP.cena(D, j, 0), j["cena"]["tryb"], D["licznik_ceny"]["tryb"], j["podloga_ceny"],
                ", ".join("%s %d" % (p, DANE.LP.cena_sprzedazy(D, p)) for p in j["pula"])))
        print("  zagroda: E %s, tablica %s, miejsc na pety %d" % (G["zagroda_e"], G["zagroda_tablica"],
                                                                 len(G["miejsca_petow"])))
        kody = wszystkie_kody()
        print("  kod wysyłany do Studio: %s" % ", ".join("%s %d zn." % (k, len(v)) for k, v in kody.items()))
    if a.sucho:
        print("sucho: OK (Studio nieużywane)")
        return

    # --- dopiero tutaj Studio (--sucho niczego z tego nie importuje)
    for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
        if _s not in sys.path:
            sys.path.insert(0, _s)
    from cel_studio import MIEJSCE as MIEJSCE_GRY, wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    if MIEJSCE_GRY != MIEJSCE:
        sys.exit("BŁĄD: placeId w cel_studio.py (%s) ≠ %s — przerywam" % (MIEJSCE_GRY, MIEJSCE))
    try:
        with StudioMCP() as s:
            s.studios(wait=15)
            sid = wybierz_studio(s, a.studio)
            stan = s.call("get_studio_state", {"studio_id": sid})["text"]
            if "Current Studio Mode: Edit" not in stan:
                sys.exit("Studio nie jest w trybie Edit — zatrzymaj Play i spróbuj ponownie.\n" + stan)

            def wykonaj(kod):
                kod = NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", str(MIEJSCE)) + kod
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
                if r["is_error"]:
                    raise StudioError(r["text"][:3000])
                w = r["text"].strip()
                if w.startswith("STOP"):
                    print(w)
                    sys.exit(2)
                return w

            def wyslij_skrypty():
                for sciezka, klasa, kontekst, tekst, plik in zrodla:
                    print("  skrypt:", wykonaj(kod_skryptu(sciezka, klasa, kontekst, tekst)))

            t0 = time.time()
            if a.skrypty:
                wykonaj('local f = workspace:FindFirstChild("%s") if not f or f:GetAttribute("Wygenerowane") ~= true '
                        'then return "STOP: brak kontenera — zbuduj całość" end '
                        'game:GetService("ChangeHistoryService"):SetWaypoint("%s: przed wymianą skryptów") '
                        'f:SetAttribute("Skrot", "%s") return "OK"' % (KONTENER, KONTENER, D["skrot"]))
                wyslij_skrypty()
                print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca("skrypty wymienione")), time.time() - t0))
                return
            wynik = wykonaj(kod_start(a.usun, time.strftime("%Y-%m-%dT%H:%M:%S"), "" if a.usun else D["skrot"]))
            print("start:", wynik)
            if a.usun or wynik != "OK":
                return
            wyslij_skrypty()
            print("części:", wykonaj(kod_czesci()))
            print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca()), time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
