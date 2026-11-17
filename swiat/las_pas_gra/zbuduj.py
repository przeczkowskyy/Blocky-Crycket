#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buduje w Roblox Studio kontener Workspace/LasPasGra — „las-pas w grze”: potwory w przegrodach (ten sam kod co
stary las, swiat/las_potwory, na nowych danych), brama do Bagna, teleport i Kamień Powrotu, mgła i przelot kamery.

    python -B swiat/las_pas_gra/zbuduj.py --sucho      # bez Studio: dane aktualne, kontrola Luau, strażniki, plan budowy
    python -B swiat/las_pas_gra/zbuduj.py              # buduje / odbudowuje Workspace/LasPasGra (tryb Edit)
    python -B swiat/las_pas_gra/zbuduj.py --skrypty    # tylko skrypty, moduły, zdalne i atrybuty Stale_* (bez części)
    python -B swiat/las_pas_gra/zbuduj.py --usun       # usuwa Workspace/LasPasGra
    python -B swiat/las_pas_gra/zbuduj.py --studio <studio_id>   # gdy otwartych jest kilka okien Studio

Wzór: swiat/las_potwory/zbuduj.py (te same zasady bezpieczeństwa wspólnego miejsca Team Create):
- wszystko w JEDNYM kontenerze Workspace/LasPasGra z atrybutem Wygenerowane = true; odbudowa i --usun ruszają tylko
  ten kontener; obiekt o tej nazwie bez atrybutu → STOP (nie ruszamy cudzej pracy);
- przed budową tylko odczyt i ostrzeżenia: mapa Workspace/LasPas (Wygenerowane, Płyta, wrota, zapowiedź Bagna,
  Kamień Powrotu), prototyp walki TestWalki2 (odtwarzacz, 5 szablonów aktorów), Workspace/LasTeleport;
- przed i po budowie punkt historii (ChangeHistoryService) — całość cofa Ctrl+Z;
- każdy skrypt i moduł zaczyna się od strażnika Studio (sprawdzane przed wysłaniem); poza Studio SerwerPasa i
  SerwerPotworow usuwają cały kontener;
- tylko tryb Edit, game.PlaceId gry sprawdzany w KAŻDYM wysyłanym kodzie; niczego nie publikuje, nie zapisuje miejsca,
  nie zmienia Lighting ani cudzych instancji (przekierowanie bramy miasteczka robi SerwerPasa dopiero w trybie Play);
- --sucho nie importuje studio_mcp ani cel_studio.

Drugi biom (17.11.2026): swiat/bagno_pas_gra/zbuduj.py wczytuje ten moduł, woła ustaw_konfiguracje() z własnym
kontenerem, mapą, danymi, szablonami i Stale_*, i dalej buduje tym samym kodem (main()). Dla lasu nic się nie zmienia.

Kod potworów jest JEDEN: Stale, Logika, SerwerPotworow, KlientPotworow, Wzorcowe i kopia silnika walki są te same co w
Workspace/LasPotwory (lista plików z swiat/las_potwory/zbuduj.py); różnią się tylko dane (DanePotworow ← nasz
zrodla/DanePotworowPasa.luau) i atrybuty kontenera Stale_* (nazwy szablonów, GUI, mapy, prefiks komunikatów).
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if TU not in sys.path:
    sys.path.insert(0, TU)
import sprawdz_luau_pasa  # noqa: E402


def _modul(nazwa, sciezka):
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ZB_LASU = _modul("zbuduj_las_potwory", os.path.join(REPO, "swiat", "las_potwory", "zbuduj.py"))
SL = ZB_LASU.sprawdz_luau

KONTENER = "LasPasGra"
ZRODLO = "swiat/las_pas_gra"
MAPA = "LasPas"
STRAZNIK = ZB_LASU.STRAZNIK
LIMIT_ZRODLA = ZB_LASU.LIMIT_ZRODLA
SZABLONY = ["lesny_slime", "cierniowy_wilk", "muchomornik", "lesny_troll", "straznik_lasu"]
# atrybuty testowe ustawione ręcznie w Edit przechodzą na odbudowany kontener
ATRYBUTY_TESTOWE = list(ZB_LASU.ATRYBUTY_TESTOWE) + ["PrzekierujBrameMiasteczka", "MglaWylaczona"]

# nadpisania stałych pakietu potworów (Stale.luau, koniec pliku) — ten kontener nie może kolidować ze starym lasem
STALE = {
    "NAZWA_KONTENERA": KONTENER,
    "NAZWA_BIOMU": MAPA,
    "NAZWA_SZABLONOW": "LasPasGraSzablony",
    "SZABLONY": ",".join(SZABLONY),
    "PREFIKS": "[LasPasGra] ",
    "GUI_BOHATERA": "LasPasGraBohater",
    "GUI_BANERA": "LasPasGraBaner",
    # 17.11.2026: panel bohatera każdego lasu widać tylko w jego lesie (Stale.PANEL_TYLKO_W_LESIE) — na tym samym
    # miejscu co panel starego lasu (wcześniej 48 px, pod nim, bo widać było dwa naraz)
    "PANEL_Y": 8,
    "PANEL_PREFIKS": "Las-pas · ",
}

DANE_POTWOROW_PASA = "swiat/las_pas_gra/zrodla/DanePotworowPasa.luau"
# (plik względem repozytorium, klasa, ścieżka w kontenerze, RunContext) — pakiet potworów z podmienionymi danymi
SKRYPTY = []
for _plik, _klasa, _sciezka, _kontekst, _kto in ZB_LASU.SKRYPTY:
    SKRYPTY.append((DANE_POTWOROW_PASA if _sciezka == "Moduly/DanePotworow" else _plik, _klasa, _sciezka, _kontekst))
SKRYPTY += [
    ("swiat/las_pas_gra/zrodla/DanePasa.luau", "ModuleScript", "Moduly/DanePasa", None),
    ("swiat/las_pas_gra/zrodla/LogikaPasa.luau", "ModuleScript", "Moduly/LogikaPasa", None),
    ("swiat/las_pas_gra/zrodla/PamiecGracza.luau", "ModuleScript", "Moduly/PamiecGracza", None),
    ("swiat/las_pas_gra/zrodla/SerwerPasa.server.luau", "Script", "SerwerPasa", "Server"),
    ("swiat/las_pas_gra/zrodla/KlientPasa.client.luau", "Script", "KlientPasa", "Client"),
    ("swiat/las_pas_gra/zrodla/MglaPasa.client.luau", "Script", "MglaPasa", "Client"),
]
SILNIK = list(ZB_LASU.SILNIK)
FOLDERY = ["Moduly", "Moduly/Walka", "Stan", "Zdalne", "Sygnaly", "Punkty"]
INNE = [
    ("RemoteFunction", "Zdalne/RozpocznijWalke2"),        # walka (odtwarzacz prototypu → SerwerPotworow)
    ("RemoteEvent", "Zdalne/ZdarzeniaPasa"),              # przelot i komunikaty (SerwerPasa ↔ KlientPasa)
    ("BindableFunction", "Sygnaly/SterowanieSerwera"),    # haczyk testowy SerwerPotworow
    ("BindableFunction", "Sygnaly/SterowanieKlienta"),    # haczyk KlientPotworow (też „wymus” i „klip” dla przelotu)
    ("BindableEvent", "Sygnaly/WynikWalki"),              # SerwerPotworow → SerwerPasa: wynik walki (brama)
    ("BindableFunction", "Sygnaly/ZwolnijPoPominieciu"),  # pominięcie walki (D-078): gracz i potwór wolni od razu
    ("BindableFunction", "Sygnaly/PrzeniesDoLasu"),       # uchwyt dla innych skryptów serwera (przejście przez chmury)
    ("BindableFunction", "Sygnaly/SterowaniePasa"),       # haczyk testowy SerwerPasa
    ("BindableFunction", "Sygnaly/SterowaniePasaKlienta"),  # haczyk testowy KlientPasa
]

NAGLOWEK_MIEJSCA = ZB_LASU.NAGLOWEK_MIEJSCA
# skąd dane i kontrola Luau (drugi biom podaje swoje w ustaw_konfiguracje)
GENERATOR = os.path.join(TU, "generuj_dane.py")
ZRODLA_LUAU = [os.path.join(TU, "zrodla")]

SPRAWDZ = r'''
local uwagi = {}
local mapa = workspace:FindFirstChild("__MAPA__")
if not mapa then
	table.insert(uwagi, "brak Workspace/__MAPA__ (bez mapy SerwerPasa i potwory nie wystartują; TestBezBiomu = true omija)")
else
	if mapa:GetAttribute("Wygenerowane") ~= true then
		table.insert(uwagi, "__MAPA__ nie ma atrybutu Wygenerowane = true")
	end
	local function szukaj(sciezka)
		local o = mapa
		for _, n in string.split(sciezka, "/") do
			o = o and o:FindFirstChild(n)
		end
		return o
	end
	local p = szukaj("Teren/Grunt/Płyta")
	if p and p:IsA("BasePart") then
		table.insert(uwagi, string.format("Płyta: (%.2f, %.2f, %.2f) rozmiar (%.1f, %.1f, %.1f) obrót Y %.1f — dane: __PLYTA__",
			p.Position.X, p.Position.Y, p.Position.Z, p.Size.X, p.Size.Y, p.Size.Z, p.Orientation.Y))
	else
		table.insert(uwagi, "brak __MAPA__/Teren/Grunt/Płyta")
	end
	for _, g in { "__WROTA__", "__ZAPOWIEDZ__", "Punkty/KamienPowrotu" } do
		if not szukaj(g) then
			table.insert(uwagi, "brak __MAPA__/" .. g)
		end
	end
end
local tw = workspace:FindFirstChild("TestWalki2")
local m = tw and tw:FindFirstChild("Moduly")
if not m or not m:FindFirstChild("OdtwarzaczWalki2") then
	table.insert(uwagi, "brak Workspace/TestWalki2/Moduly/OdtwarzaczWalki2 (walki niedostępne)")
end
local a = tw and tw:FindFirstChild("Aktorzy")
for _, k in { __SZABLONY__ } do
	if not a or not a:FindFirstChild(k) then
		table.insert(uwagi, "brak szablonu TestWalki2/Aktorzy/" .. k .. " (klient pokaże bryły zastępcze)")
	end
end
local t = workspace:FindFirstChild("LasTeleport")
if not t then
	table.insert(uwagi, "brak Workspace/LasTeleport — brama miasteczka nie zostanie przekierowana (zostaje uchwyt PrzeniesDoLasu)")
else
	table.insert(uwagi, "LasTeleport: PunktLas " .. tostring(t:GetAttribute("PunktLas")) .. ", PunktMiasteczka " .. tostring(t:GetAttribute("PunktMiasteczka")))
end
if workspace:FindFirstChild("LasPotwory") then
	table.insert(uwagi, "jest też Workspace/LasPotwory (stary las) — działa obok, osobne szablony i GUI")
end
return if #uwagi == 0 then "OK" else table.concat(uwagi, " | ")
'''

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
	CH:SetWaypoint("__KONTENER__: przed usunięciem")
	for _, d in stare do d:Destroy() end
	CH:SetWaypoint("__KONTENER__: usunięto")
	return "USUNIETO"
end
local testowe = {}
for _, d in stare do
	for _, a in { __TESTOWE__ } do
		local v = d:GetAttribute(a)
		if v ~= nil then testowe[a] = v end
	end
end
CH:SetWaypoint("__KONTENER__: przed budową")
for _, d in stare do d:Destroy() end
local f = Instance.new("Folder")
f.Name = nazwa
f:SetAttribute("Wygenerowane", true)
f:SetAttribute("Zrodlo", "__ZRODLO__")
f:SetAttribute("Zbudowano", "__CZAS__")
f:SetAttribute("Skrot", "__SKROT__")
for a, v in testowe do f:SetAttribute(a, v) end
for _, sciezka in { __FOLDERY__ } do
	local rodzic = f
	local czesci = string.split(sciezka, "/")
	for i = 1, #czesci - 1 do rodzic = rodzic:FindFirstChild(czesci[i]) end
	local d = Instance.new("Folder")
	d.Name = czesci[#czesci]
	d.Parent = rodzic
end
f.Parent = workspace
return "OK"
'''

# zdalne, haczyki i atrybuty Stale_* (idempotentnie; także przy --skrypty)
INNE_KOD = ZB_LASU.INNE_KOD.replace('f:SetAttribute("Skrot", "__SKROT__")',
                                     'f:SetAttribute("Skrot", "__SKROT__")\nfor k, v in { __STALE__ } do f:SetAttribute("Stale_" .. k, v) end')

if "Stale_" not in INNE_KOD:
    raise SystemExit("BŁĄD: swiat/las_potwory/zbuduj.py zmienił INNE_KOD — nie umiem dopisać atrybutów Stale_*")

SKRYPT = ZB_LASU.SKRYPT

# części pakietu (bez części mapy — te są w Workspace/LasPas): zapora i napis bramy, zabezpieczenie i tabliczka za
# bramą, punkt E Kamienia Powrotu. Liczby z DanePasa (wstawia czesci_kod()).
CZESCI = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera"
end
for _, n in { "Brama", "ZaBrama" } do
	local stary = f:FindFirstChild(n)
	if stary then stary:Destroy() end
end
local pkt = f:FindFirstChild("Punkty")
local staryKamien = pkt and pkt:FindFirstChild("KamienPowrotu")
if staryKamien then staryKamien:Destroy() end
local KREM, TUSZ = Color3.fromHex("FFF3D1"), Color3.fromHex("17121F")
local function czesc(nazwa, rodzic, srodek, rozmiar, w)
	local p = Instance.new("Part")
	p.Name = nazwa
	p.Anchored = true
	p.Size = rozmiar
	p.CFrame = CFrame.new(srodek)
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.CanTouch = false
	p.CastShadow = w.cien == true
	p.Transparency = w.przezroczystosc or 0
	p.CanCollide = w.kolizja == true
	if not p.CanCollide then p.CanQuery = false end
	p.Material = w.material or Enum.Material.SmoothPlastic
	p.Color = w.kolor or Color3.fromRGB(200, 200, 200)
	p.Parent = rodzic
	return p
end
local function napisy(rodzic, tytul, podpis, kolorTytulu)
	local t = Instance.new("TextLabel")
	t.Name = "Tytul"
	t.BackgroundTransparency = 1
	t.Size = UDim2.fromScale(1, 0.62)
	t.Font = Enum.Font.Bangers
	t.TextScaled = true
	t.Text = tytul
	t.TextColor3 = kolorTytulu
	t.Parent = rodzic
	local s = Instance.new("UIStroke")
	s.Color = TUSZ
	s.Thickness = 2
	s.Parent = t
	local p = Instance.new("TextLabel")
	p.Name = "Podpis"
	p.BackgroundTransparency = 1
	p.Position = UDim2.fromScale(0, 0.62)
	p.Size = UDim2.fromScale(1, 0.34)
	p.Font = Enum.Font.Bangers
	p.TextScaled = true
	p.Text = podpis
	p.TextColor3 = TUSZ
	p.Parent = rodzic
end

-- 1. Brama: niewidzialna zapora przez cały pas (u klienta zwycięzcy Strażnika bez kolizji) i napis nad wrotami
local brama = Instance.new("Model")
brama.Name = "Brama"
brama.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
brama:SetAttribute("Wygenerowane", true)
local zapora = czesc("Zapora", brama, Vector3.new(__ZAPORA_SRODEK__), Vector3.new(__ZAPORA_ROZMIAR__),
	{ kolizja = true, przezroczystosc = 1 })
brama.PrimaryPart = zapora
local kotwica = czesc("Napis", brama, Vector3.new(__NAPIS__), Vector3.new(1, 1, 1), { przezroczystosc = 1 })
local bb = Instance.new("BillboardGui")
bb.Name = "NapisBramy"
bb.Size = UDim2.fromOffset(230, 70)
bb.MaxDistance = 45
bb.AlwaysOnTop = false
bb.LightInfluence = 0
bb.Parent = kotwica
local ramka = Instance.new("Frame")
ramka.Size = UDim2.fromScale(1, 1)
ramka.BackgroundColor3 = KREM
ramka.BorderSizePixel = 0
ramka.Parent = bb
local r = Instance.new("UICorner")
r.CornerRadius = UDim.new(0.2, 0)
r.Parent = ramka
local o = Instance.new("UIStroke")
o.Color = TUSZ
o.Thickness = 3
o.Parent = ramka
napisy(ramka, __NAPIS_TYTUL__, __NAPIS_PODPIS__, Color3.fromHex("E8364F"))
brama.Parent = f

-- 2. Za bramą: zapasowa podłoga tuż pod Płytą mapy, ściana na końcu (obie niewidzialne) i tabliczka „Bagno — wkrótce”
local zaBrama = Instance.new("Model")
zaBrama.Name = "ZaBrama"
zaBrama:SetAttribute("Wygenerowane", true)
czesc("Podloga", zaBrama, Vector3.new(__PODLOGA_SRODEK__), Vector3.new(__PODLOGA_ROZMIAR__), { kolizja = true, przezroczystosc = 1 })
czesc("Sciana", zaBrama, Vector3.new(__SCIANA_SRODEK__), Vector3.new(__SCIANA_ROZMIAR__), { kolizja = true, przezroczystosc = 1 })
local tab = Instance.new("Model")
tab.Name = "Tabliczka"
local x, y, z = __TABLICZKA__
czesc("Slupek", tab, Vector3.new(x, y + 3.5, z), Vector3.new(0.8, 7, 0.8),
	{ kolizja = true, cien = true, material = Enum.Material.Wood, kolor = Color3.fromRGB(110, 74, 44) })
local deska = czesc("Deska", tab, Vector3.new(x - 0.5, y + 6.2, z), Vector3.new(0.4, 4, 10),
	{ kolizja = true, cien = true, material = Enum.Material.WoodPlanks, kolor = Color3.fromRGB(196, 150, 96) })
tab.PrimaryPart = deska
local sg = Instance.new("SurfaceGui")
sg.Name = "NapisTabliczki"
sg.Face = Enum.NormalId.Left -- −X: w stronę bramy i gracza, który przez nią przechodzi
sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
sg.PixelsPerStud = 50
sg.LightInfluence = 0
sg.Parent = deska
local tlo = Instance.new("Frame")
tlo.Size = UDim2.fromScale(1, 1)
tlo.BackgroundColor3 = KREM
tlo.BorderSizePixel = 0
tlo.Parent = sg
local pad = Instance.new("UIPadding")
pad.PaddingLeft = UDim.new(0.05, 0)
pad.PaddingRight = UDim.new(0.05, 0)
pad.PaddingTop = UDim.new(0.08, 0)
pad.PaddingBottom = UDim.new(0.08, 0)
pad.Parent = tlo
napisy(tlo, __TAB_TYTUL__, __TAB_PODPIS__, Color3.fromHex("52D273"))
tab.Parent = zaBrama
zaBrama.Parent = f

-- 3. Kamień Powrotu: punkt E (podpowiedź włącza SerwerPasa w Play) przy kamieniu z mapy
local k = czesc("KamienPowrotu", pkt, Vector3.new(__KAMIEN__), Vector3.new(2, 2, 2), { przezroczystosc = 1 })
local pp = Instance.new("ProximityPrompt")
pp.Name = "PodpowiedzPowrotu"
pp.ActionText = "Wróć do miasteczka"
pp.ObjectText = "Kamień Powrotu"
pp.KeyboardKeyCode = Enum.KeyCode.E
pp.GamepadKeyCode = Enum.KeyCode.ButtonX
pp.HoldDuration = 0
pp.MaxActivationDistance = __ZASIEG__
pp.RequiresLineOfSight = false
pp.ClickablePrompt = true
pp.Enabled = false
pp.Parent = k
local etykieta = Instance.new("BillboardGui")
etykieta.Name = "Tabliczka"
etykieta.Size = UDim2.fromOffset(190, 44)
etykieta.StudsOffset = Vector3.new(0, 4, 0)
etykieta.MaxDistance = 60
etykieta.AlwaysOnTop = false
etykieta.Parent = k
local et = Instance.new("TextLabel")
et.Size = UDim2.fromScale(1, 1)
et.BackgroundColor3 = Color3.fromRGB(27, 24, 38)
et.BackgroundTransparency = 0.2
et.TextColor3 = Color3.fromRGB(190, 255, 170)
et.Font = Enum.Font.FredokaOne
et.TextScaled = true
et.Text = "MIASTECZKO  (E)"
et.Parent = etykieta
local rr = Instance.new("UICorner")
rr.CornerRadius = UDim.new(0, 10)
rr.Parent = et
local n = 0
for _, d in f:GetDescendants() do
	if d:IsA("BasePart") then n += 1 end
end
return "OK (części pakietu: " .. n .. ")"
'''

KONIEC = ZB_LASU.KONIEC.replace("LasPotwory: zbudowano", "__KONTENER__: zbudowano")


# ----------------------------------------------------------------------------------------------- źródła i kontrole
def zrodla_pakietu():
    """Lista (ścieżka w kontenerze, klasa, RunContext, źródło, plik). Przerywa (kod 2), gdy brakuje pliku."""
    wynik, braki = [], []
    for plik, klasa, sciezka, kontekst in SKRYPTY:
        pelna = os.path.join(REPO, plik)
        if not os.path.isfile(pelna):
            braki.append(plik)
            continue
        wynik.append((sciezka, klasa, kontekst, ZB_LASU.wczytaj(pelna), plik))
    # BC_SILNIK_KORZEN: skąd brać kopię silnika walki (domyślnie repozytorium). Pozwala wgrać do Studio wersję
    # zgodną z odtwarzaczem, gdy silnik w repo jest właśnie zmieniany (17.11.2026: silnik v3 czeka na odtwarzacz).
    korzen_silnika = os.environ.get("BC_SILNIK_KORZEN") or REPO
    for plik, sciezka in SILNIK:
        # pliki z swiat/ (np. dane walki drugiego biomu) zawsze z repozytorium
        pelna = os.path.join(REPO if plik.startswith("swiat/") else korzen_silnika, plik)
        if not os.path.isfile(pelna):
            braki.append(plik)
            continue
        kopia = ("-- KOPIA %s zrobiona przez %s/zbuduj.py (%s) — źródło prawdy jest w repozytorium.\n"
                 % (plik, ZRODLO, time.strftime("%Y-%m-%d"))) + ZB_LASU.STRAZNIK_MODULU + ZB_LASU.wczytaj(pelna)
        wynik.append((sciezka, "ModuleScript", None, kopia, plik))
    if braki:
        print("BŁĄD: brak plików źródłowych:\n  " + "\n  ".join(braki))
        sys.exit(2)
    return wynik


def dane_pasa():
    """Liczby z generatora (te same co w zrodla/DanePasa.luau) — do kodu części."""
    gen = _modul("generuj_dane_" + KONTENER, GENERATOR)
    _, dp, dpa = gen.wszystko()
    return dp, dpa


def sprawdz_offline(zrodla):
    """--sucho i każda budowa: dane aktualne, oba sprawdzacze Luau czyste, strażniki, rozmiary. Zwraca skrót danych."""
    gen = GENERATOR
    r = subprocess.run([sys.executable, "-B", gen, "--sprawdz"], cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    wyjscie = (r.stdout + r.stderr).strip()
    print("generuj_dane.py --sprawdz: kod %d%s" % (r.returncode, (" — " + wyjscie.splitlines()[-1]) if wyjscie else ""))
    if r.returncode != 0:
        print(wyjscie)
        sys.exit("BŁĄD: dane nieaktualne — uruchom python -B %s" % os.path.relpath(gen, REPO).replace(os.sep, "/"))
    pliki = sorted(os.path.join(d, n) for d in ZRODLA_LUAU for n in os.listdir(d) if n.endswith(".luau"))
    bledy, parser = sprawdz_luau_pasa.sprawdz_pliki(pliki, wypisz=print)
    print("sprawdz_luau_pasa.py: %d plików, %s%s" % (len(pliki), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
                                                    " (z parserem luau_mini)" if parser else ""))
    if bledy:
        for b in bledy:
            print("  " + b)
        sys.exit("BŁĄD: sprawdz_luau_pasa.py zgłosił błędy")
    pliki_lasu = sorted(os.path.join(REPO, "swiat", "las_potwory", "zrodla", n)
                        for n in os.listdir(os.path.join(REPO, "swiat", "las_potwory", "zrodla")) if n.endswith(".luau"))
    bledy_lasu = SL.sprawdz_pliki(pliki_lasu, wypisz=print)
    print("swiat/las_potwory/sprawdz_luau.py (kod potworów wspólny): %d plików, %s"
          % (len(pliki_lasu), "OK" if not bledy_lasu else "BŁĘDY: %d" % len(bledy_lasu)))
    if bledy_lasu:
        for b in bledy_lasu:
            print("  " + b)
        sys.exit("BŁĄD: kod potworów nie przechodzi własnej kontroli")
    for sciezka, klasa, kontekst, tekst, plik in zrodla:
        if not SL.pierwsza_instrukcja(tekst).startswith(STRAZNIK):
            sys.exit("BŁĄD: %s (%s) nie zaczyna się od strażnika „%s”" % (sciezka, plik, STRAZNIK))
        if len(tekst) > LIMIT_ZRODLA:
            sys.exit("BŁĄD: %s ma %d znaków (limit Source 200 000)" % (sciezka, len(tekst)))
    dane = next(t for s, k, c, t, p in zrodla if s == "Moduly/DanePotworow")
    skrot = ZB_LASU.skrot_danych(dane)
    if not skrot:
        sys.exit("BŁĄD: w DanePotworowPasa.luau nie ma pola skrot")
    return skrot


def _w(v):
    return ", ".join("%g" % x for x in v)


def czesci_kod(dpa):
    n = ZB_LASU.luau_napis
    zast = {
        "__KONTENER__": KONTENER,
        "__ZAPORA_SRODEK__": _w(dpa["zapora"]["srodek"]), "__ZAPORA_ROZMIAR__": _w(dpa["zapora"]["rozmiar"]),
        "__NAPIS__": _w(dpa["napisBramy"]["punkt"]),
        "__NAPIS_TYTUL__": n(dpa["napisBramy"]["tekst"]), "__NAPIS_PODPIS__": n(dpa["napisBramy"]["podpis"]),
        "__PODLOGA_SRODEK__": _w(dpa["zabezpieczenie"]["podloga"]["srodek"]),
        "__PODLOGA_ROZMIAR__": _w(dpa["zabezpieczenie"]["podloga"]["rozmiar"]),
        "__SCIANA_SRODEK__": _w(dpa["zabezpieczenie"]["sciana"]["srodek"]),
        "__SCIANA_ROZMIAR__": _w(dpa["zabezpieczenie"]["sciana"]["rozmiar"]),
        "__TABLICZKA__": _w(dpa["tabliczka"]["punkt"]),
        "__TAB_TYTUL__": n(dpa["tabliczka"]["tekst"]), "__TAB_PODPIS__": n(dpa["tabliczka"]["podpis"]),
        "__KAMIEN__": _w([dpa["powrot"]["punkt"][0], dpa["powrot"]["punkt"][1] + 2.5, dpa["powrot"]["punkt"][2]]),
        "__ZASIEG__": "%g" % dpa["powrot"]["zasieg"],
    }
    kod = CZESCI
    for k, v in zast.items():
        kod = kod.replace(k, v)
    return kod


def plan_czesci(dpa):
    """Opis części pakietu do --sucho (bez Studio)."""
    return [
        ("Brama/Zapora", "Part niewidzialny, kolizja (u zwycięzcy Strażnika bez)", dpa["zapora"]["srodek"], dpa["zapora"]["rozmiar"]),
        ("Brama/Napis", "kotwica BillboardGui „%s / %s”" % (dpa["napisBramy"]["tekst"], dpa["napisBramy"]["podpis"]),
         dpa["napisBramy"]["punkt"], [1, 1, 1]),
        ("ZaBrama/Podloga", "niewidzialna, kolizja (zapas pod Płytą)", dpa["zabezpieczenie"]["podloga"]["srodek"],
         dpa["zabezpieczenie"]["podloga"]["rozmiar"]),
        ("ZaBrama/Sciana", "niewidzialna, kolizja (koniec za bramą)", dpa["zabezpieczenie"]["sciana"]["srodek"],
         dpa["zabezpieczenie"]["sciana"]["rozmiar"]),
        ("ZaBrama/Tabliczka", "słupek + deska z SurfaceGui „%s”" % dpa["tabliczka"]["tekst"], dpa["tabliczka"]["punkt"], [0.8, 8.2, 10]),
        ("Punkty/KamienPowrotu", "punkt E (ProximityPrompt → miasteczko)", dpa["powrot"]["punkt"], [2, 2, 2]),
    ]


def stale_luau():
    czesci = []
    for k, v in STALE.items():
        czesci.append("%s = %s" % (k, ZB_LASU.luau_napis(v) if isinstance(v, str) else json.dumps(v)))
    return ", ".join(czesci)


def ustaw_konfiguracje(k):
    """Drugi biom (swiat/bagno_pas_gra/zbuduj.py): podmienia ustawienia modułu przed main(). Klucze jak globalne
    tego pliku: KONTENER, ZRODLO, MAPA, SZABLONY, STALE, SKRYPTY, SILNIK, INNE, GENERATOR, ZRODLA_LUAU."""
    znane = {"KONTENER", "ZRODLO", "MAPA", "SZABLONY", "STALE", "SKRYPTY", "SILNIK", "INNE", "GENERATOR", "ZRODLA_LUAU"}
    nieznane = set(k) - znane
    if nieznane:
        raise SystemExit("ustaw_konfiguracje: nieznane klucze %s" % sorted(nieznane))
    globals().update(k)


# ----------------------------------------------------------------------------------------------- główna
def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje kontener Workspace/%s w Roblox Studio" % KONTENER)
    ap.add_argument("--sucho", action="store_true", help="bez Studio: sprawdź dane i źródła, pokaż plan")
    ap.add_argument("--skrypty", action="store_true", help="tylko skrypty, moduły, zdalne i atrybuty Stale_*")
    ap.add_argument("--usun", action="store_true", help="usuń Workspace/%s" % KONTENER)
    ap.add_argument("--studio", default=None, help="studio_id (wymagane, gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()

    zrodla = [] if a.usun else zrodla_pakietu()
    skrot = "" if a.usun else sprawdz_offline(zrodla)
    dp, dpa = (None, None) if a.usun else dane_pasa()

    if not a.usun:
        print("Kontener: Workspace/%s · Skrot danych: %s · modułów i skryptów: %d · mapa: Workspace/%s (%s)"
              % (KONTENER, skrot, len(zrodla), dpa["mapa"]["nazwa"], dpa["mapa"]["zrodlo"]))
        print("  %-52s → %s" % ("Folder", ", ".join(FOLDERY)))
        for klasa, sciezka in INNE:
            print("  %-52s → %s %s" % ("(nowa instancja)", klasa, sciezka))
        for sciezka, klasa, kontekst, tekst, plik in zrodla:
            print("  %-52s → %s %s%s (%d znaków)" % (plik, klasa, sciezka,
                                                      " [RunContext=%s]" % kontekst if kontekst else "", len(tekst)))
        for sciezka, opis, srodek, rozmiar in plan_czesci(dpa):
            print("  %-52s → %s @ (%s) %s" % ("(część)", sciezka, _w(srodek), opis))
        print("  atrybuty Stale_*: " + ", ".join("%s = %r" % kv for kv in STALE.items()))
        print("  atrybuty testowe przenoszone przy odbudowie: " + ", ".join(ATRYBUTY_TESTOWE))
    if a.sucho:
        print("sucho: OK (Studio nieużywane)")
        return

    # --- dopiero tutaj Studio (--sucho niczego z tego nie importuje)
    for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
        if _s not in sys.path:
            sys.path.insert(0, _s)
    from cel_studio import MIEJSCE, wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    try:
        with StudioMCP() as s:
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

            def wyslij_skrypt(sciezka, klasa, kontekst, tekst):
                kod = (SKRYPT.replace("__KONTENER__", KONTENER).replace("__SCIEZKA__", sciezka).replace("__KLASA__", klasa)
                       .replace("__RUNCONTEXT__", "s.RunContext = Enum.RunContext.%s" % kontekst if kontekst else ""))
                return wykonaj(kod.replace("__ZRODLO__", ZB_LASU.dlugi_napis(tekst)))

            t0 = time.time()
            if not a.usun:
                plyta = dp["biom"]["plyta"]
                opis_plyty = ("(%s) rozmiar (%s)" % (_w(plyta["pozycja"]), _w(plyta["rozmiar"]))) if plyta else "bez Płyty"
                print("w miejscu (tylko odczyt):", wykonaj(
                    SPRAWDZ.replace("__MAPA__", dpa["mapa"]["nazwa"]).replace("__PLYTA__", opis_plyty)
                    .replace("__WROTA__", dpa["mapa"]["grupaWrot"]).replace("__ZAPOWIEDZ__", dpa["mapa"]["zapowiedz"])
                    .replace("__SZABLONY__", ", ".join(ZB_LASU.luau_napis(k) for k in SZABLONY))))
            inne_kod = (INNE_KOD.replace("__KONTENER__", KONTENER).replace("__SKROT__", skrot)
                        .replace("__FOLDERY__", ", ".join(ZB_LASU.luau_napis(x) for x in FOLDERY))
                        .replace("__INNE__", ", ".join("{%s, %s}" % (ZB_LASU.luau_napis(k), ZB_LASU.luau_napis(p))
                                                        for k, p in INNE))
                        .replace("__STALE__", stale_luau()))
            if a.skrypty:
                wykonaj('local f = workspace:FindFirstChild("%s") if not f or f:GetAttribute("Wygenerowane") ~= true '
                        'then return "STOP: brak kontenera — zbuduj całość" end '
                        'game:GetService("ChangeHistoryService"):SetWaypoint("%s: przed wymianą skryptów") return "OK"'
                        % (KONTENER, KONTENER))
                print("  zdalne, haczyki, Stale_*:", wykonaj(inne_kod))
                for sciezka, klasa, kontekst, tekst, plik in zrodla:
                    print("  skrypt:", wyslij_skrypt(sciezka, klasa, kontekst, tekst))
                print("gotowe: %s (%.0f s)" % (wykonaj(KONIEC.replace("__KONTENER__", KONTENER)), time.time() - t0))
                return
            wynik = wykonaj(START.replace("__KONTENER__", KONTENER).replace("__USUN__", "true" if a.usun else "false")
                            .replace("__ZRODLO__", ZRODLO).replace("__SKROT__", skrot)
                            .replace("__TESTOWE__", ", ".join(ZB_LASU.luau_napis(x) for x in ATRYBUTY_TESTOWE))
                            .replace("__FOLDERY__", ", ".join(ZB_LASU.luau_napis(x) for x in FOLDERY))
                            .replace("__CZAS__", time.strftime("%Y-%m-%dT%H:%M:%S")))
            print("start:", wynik)
            if a.usun or not wynik.endswith("OK"):
                return
            print("  zdalne, haczyki, Stale_*:", wykonaj(inne_kod))
            print("  części:", wykonaj(czesci_kod(dpa)))
            for sciezka, klasa, kontekst, tekst, plik in zrodla:
                print("  skrypt:", wyslij_skrypt(sciezka, klasa, kontekst, tekst))
            print("gotowe: %s (%.0f s)" % (wykonaj(KONIEC.replace("__KONTENER__", KONTENER)), time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
