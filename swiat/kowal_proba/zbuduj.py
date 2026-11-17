#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buduje w Roblox Studio kontener Workspace/KowalProba — kowal na próbę (kuźnia z klocków w bazarze, kowal z klipem
kucia, tymczasowe okno, ulepszanie i rozbiórka). Status: propozycja (PROJEKT.md).

    python -B swiat/kowal_proba/zbuduj.py --sucho      # bez Studio: dane, kontrola Luau, strażniki, plan budowy
    python -B swiat/kowal_proba/zbuduj.py              # buduje / odbudowuje kontener (Studio w trybie Edit)
    python -B swiat/kowal_proba/zbuduj.py --skrypty    # tylko moduły i skrypty do istniejącego kontenera
    python -B swiat/kowal_proba/zbuduj.py --usun       # usuwa Workspace/KowalProba (gra wraca do stanu sprzed próby)
    python -B swiat/kowal_proba/zbuduj.py --studio <studio_id>   # gdy otwartych jest kilka okien Studio

Co powstaje (tylko w Workspace/KowalProba z atrybutem Wygenerowane = true; cudzych obiektów budowa NIE zmienia —
miejsce kuźni sprawdza dane.py na danych mapy bazaru):
  Moduly/DaneKowala, LogikaKowala, OknoKowala, RigKowala, RigKowal     ModuleScript (zrodla/; DaneKowala i RigKowal
                                                                       wygenerowane przez dane.py)
  SerwerKowala (RunContext = Server), KlientKowala (RunContext = Client)
  Zdalne/Kuznia (RemoteFunction), Zdalne/ZdarzeniaKowala (RemoteEvent)
  Sygnaly/SterowanieSerwera, Sygnaly/SterowanieKlienta   BindableFunction — haczyki testowe
  Kuznia (Model „Persistent”): części z kuznia/czesci.json w podgrupach (Podloga, Palenisko, Miech, Kowadlo, Kadz,
  Stojak, Daszek), światło i ogień w żarze, iskry nad sztabą, napis na szyldzie (SurfaceGui), Kowal (rig z klocków
  w pozie zamachu), E (niewidzialna część z ProximityPrompt „Podpowiedz”, Enabled = false w Edit — włącza serwer w Play)
Atrybuty kontenera: Wygenerowane, Zrodlo, Zbudowano, Skrot.

Zasady (wspólne miejsce Team Create): okno wybiera swiat/test_walki_roblox/cel_studio.py (jedno okno albo --studio,
zawsze placeId gry); KAŻDY wysyłany kod sprawdza game.PlaceId i tryb Edit; ruszany jest tylko własny kontener (obiekt
o tej nazwie bez atrybutu Wygenerowane → STOP); punkty historii przed i po (Ctrl+Z cofa całość); nic nie jest
zapisywane ani publikowane, Lighting nietknięty. --sucho nie importuje studio_mcp ani cel_studio.
"""
import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if not sys.path or sys.path[0] != TU:
    sys.path.insert(0, TU)
import dane as DANE  # noqa: E402
import sprawdz_luau_kowala as SLK  # noqa: E402

SL = SLK.SL
MIEJSCE = 129485428021967  # placeId miejsca gry (to samo co swiat/test_walki_roblox/cel_studio.py)
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
LIMIT_ZRODLA = 199000
ZRODLO = "swiat/kowal_proba"
ZRODLA = os.path.join(TU, "zrodla")
KONTENER = "KowalProba"

SKRYPTY = [
    ("DaneKowala.luau", "ModuleScript", "Moduly/DaneKowala", None),
    ("LogikaKowala.luau", "ModuleScript", "Moduly/LogikaKowala", None),
    ("OknoKowala.luau", "ModuleScript", "Moduly/OknoKowala", None),
    ("RigKowala.luau", "ModuleScript", "Moduly/RigKowala", None),
    ("RigKowal.luau", "ModuleScript", "Moduly/RigKowal", None),
    ("SerwerKowala.server.luau", "Script", "SerwerKowala", "Server"),
    ("KlientKowala.client.luau", "Script", "KlientKowala", "Client"),
]
FOLDERY = ["Moduly", "Zdalne", "Sygnaly", "Kuznia"]
TRWALE = ["Kuznia"]   # Model z ModelStreamingMode = Persistent (streaming nie wypycha kuźni ani kowala)
INNE = [
    ("RemoteFunction", "Zdalne/Kuznia"),
    ("RemoteEvent", "Zdalne/ZdarzeniaKowala"),
    ("BindableFunction", "Sygnaly/SterowanieSerwera"),
    ("BindableFunction", "Sygnaly/SterowanieKlienta"),
]

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
	local d
	local trwale = __TRWALE__
	if trwale[sciezka] then
		d = Instance.new("Model")
		d.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
	else
		d = Instance.new("Folder")
	end
	d.Name = sciezka
	d.Parent = f
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

# części kuźni (z kuznia/czesci.json), dodatki i kowal (po modułach — wymaga Moduly/DaneKowala, RigKowala i RigKowal)
CZESCI = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera"
end
local M = f.Moduly
local D = require(M.DaneKowala)
local Rig = require(M.RigKowala)
local daneRigu = require(M[D.kowal.rig])
local K = f.Kuznia
local G = __GRUPY__
local MAT = __MATERIALY__
local P = __CZESCI__
local grupy = {}
local function grupa(i)
	if grupy[i] then return grupy[i] end
	local sciezka = string.split(G[i], "/")
	local cur = K
	for j = 4, #sciezka do
		local nxt = cur:FindFirstChild(sciezka[j])
		if not nxt then
			nxt = Instance.new("Model")
			nxt.Name = sciezka[j]
			nxt.Parent = cur
		end
		cur = nxt
	end
	grupy[i] = cur
	return cur
end
local n = 0
local zar, sztaba, szyld = {}, nil, nil
for _, c in P do
	local ks = c[1]
	local p
	if ks == 3 then
		p = Instance.new("WedgePart")
	elseif ks == 4 then
		p = Instance.new("CornerWedgePart")
	else
		p = Instance.new("Part")
		p.Shape = if ks == 1 then Enum.PartType.Ball elseif ks == 2 then Enum.PartType.Cylinder else Enum.PartType.Block
	end
	local cechy = c[16] or 0
	p.Name = c[15]
	p.Anchored = true
	p.Size = Vector3.new(c[9], c[10], c[11])
	p.CFrame = CFrame.new(c[3], c[4], c[5]) * CFrame.fromOrientation(c[6], c[7], c[8])
	p.Color = Color3.fromHex(c[12])
	p.Material = Enum.Material[MAT[c[13] + 1]]
	p.Transparency = c[14]
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.CanTouch = false
	p.CanCollide = bit32.band(cechy, 1) == 0
	p.CanQuery = p.CanCollide
	p.CastShadow = bit32.band(cechy, 2) == 0
	p.Parent = grupa(c[2] + 1)
	if p.Name == "Żar" then table.insert(zar, p) end
	if p.Name == "Sztaba" then sztaba = p end
	if p.Name == "Szyld" then szyld = p end
	n += 1
end
-- żar: ciepłe światło i ogień (wbudowane efekty Roblox, nic nie jest wgrywane)
for _, p in zar do
	local l = Instance.new("PointLight")
	l.Color = Color3.fromRGB(255, 140, 60)
	l.Range = 16
	l.Brightness = 1.6
	l.Shadows = false
	l.Parent = p
	local o = Instance.new("Fire")
	o.Size = 3
	o.Heat = 6
	o.Color = Color3.fromRGB(255, 120, 40)
	o.SecondaryColor = Color3.fromRGB(255, 210, 90)
	o.Parent = p
end
if sztaba then
	local l = Instance.new("PointLight")
	l.Color = Color3.fromRGB(255, 120, 50)
	l.Range = 6
	l.Brightness = 1
	l.Parent = sztaba
	local e = Instance.new("ParticleEmitter")
	e.Name = "Iskry"
	e.Color = ColorSequence.new(Color3.fromRGB(255, 200, 80), Color3.fromRGB(255, 90, 30))
	e.LightEmission = 1
	e.Size = NumberSequence.new(0.18, 0)
	e.Lifetime = NumberRange.new(0.25, 0.5)
	e.Speed = NumberRange.new(6, 10)
	e.SpreadAngle = Vector2.new(70, 70)
	e.Rate = 6
	e.Acceleration = Vector3.new(0, -30, 0)
	e.Parent = sztaba
end
-- szyld: napis od strony uliczki (przód kuźni +Z = ściana Back części)
if szyld then
	local s = Instance.new("SurfaceGui")
	s.Name = "Napis"
	s.Face = Enum.NormalId.Back
	s.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	s.PixelsPerStud = 80
	s.LightInfluence = 0
	s.Parent = szyld
	local function tekst(t, y, h, kol, czcionka)
		local l = Instance.new("TextLabel")
		l.BackgroundTransparency = 1
		l.Position = UDim2.fromScale(0.04, y)
		l.Size = UDim2.fromScale(0.92, h)
		l.Font = Enum.Font[czcionka]
		l.TextScaled = true
		l.TextColor3 = Color3.fromHex(kol)
		l.Text = t
		l.Parent = s
		return l
	end
	tekst(D.teksty.szyld, 0.04, 0.66, "3E2A16", "LuckiestGuy")
	tekst(D.teksty.szyld_podpis, 0.68, 0.28, "6B4A2A", "FredokaOne")
end
-- kowal: rig z klocków za kowadłem, przodem do uliczki, w pozie zamachu (w Play klip gra klient)
local baza = CFrame.new(D.kuznia.kowal[1], D.kuznia.kowal[2], D.kuznia.kowal[3]) * CFrame.Angles(0, math.rad(D.kuznia.kowalRy), 0)
local kowal, u = Rig.zbuduj(daneRigu, daneRigu.skala, "Kowal")
kowal.Parent = K
kowal:PivotTo(baza * u.korzen.CFrame)
Rig.graj(u, D.kowal.klip)
Rig.krok(u, 9 / 30)
-- punkt E przy kowadle (podpowiedź wyłączona w Edit; włącza ją serwer w Play)
local e = Instance.new("Part")
e.Name = "E"
e.Anchored = true
e.Size = Vector3.new(1, 1, 1)
e.Transparency = 1
e.CanCollide = false
e.CanQuery = false
e.CanTouch = false
e.CastShadow = false
e.CFrame = CFrame.new(D.kuznia.e[1], D.kuznia.e[2], D.kuznia.e[3])
e.Parent = K
local pp = Instance.new("ProximityPrompt")
pp.Name = "Podpowiedz"
pp.ActionText = D.teksty.podpowiedz_akcja
pp.ObjectText = D.teksty.podpowiedz_obiekt
pp.KeyboardKeyCode = Enum.KeyCode.E
pp.GamepadKeyCode = Enum.KeyCode.ButtonX
pp.HoldDuration = 0
pp.MaxActivationDistance = D.kuznia.zasieg
pp.RequiresLineOfSight = false
pp.Enabled = false
pp:SetAttribute("Akcja", "kowal")
pp.Parent = e
return "części kuźni: " .. n .. ", żar: " .. #zar .. ", kowal: " .. #Rig.czesci(u) .. " brył"
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
    for plik, klasa, sciezka, kontekst in SKRYPTY:
        pelna = os.path.join(ZRODLA, plik)
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
    print("dane.py --sprawdz: %s (skrót %s, przypadków %d)" % ("aktualne" if not zle else "NIEAKTUALNE: " + ", ".join(zle),
                                                              D["skrot"], sum(len(v) for v in D["przypadki"].values())))
    if zle:
        sys.exit("BŁĄD: pliki nieaktualne — uruchom python -B swiat/kowal_proba/dane.py")
    if D["kontener"] != KONTENER:
        sys.exit("BŁĄD: D.kontener (%s) ≠ %s" % (D["kontener"], KONTENER))
    bledy, parser = SLK.sprawdz_pliki(SLK.pliki_pakietu(), wypisz=print)
    print("sprawdz_luau_kowala.py: %d plików, %s%s" % (len(zrodla), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
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
    with open(DANE.PLIK_KUZNI, encoding="utf-8") as f:
        d = json.load(f)
    return (CZESCI.replace("__KONTENER__", KONTENER).replace("__GRUPY__", DANE._luau(d["grupy"]))
            .replace("__MATERIALY__", DANE._luau(d["materialy"])).replace("__CZESCI__", DANE._luau(d["czesci"])))


def kod_konca(punkt_historii="zbudowano"):
    return (KONIEC.replace("__KONTENER__", KONTENER).replace("__OCZEKIWANE__", str(len(SKRYPTY)))
            .replace("__PUNKT_HISTORII__", punkt_historii))


def wszystkie_kody():
    """Kod wysyłany do Studio (bez skryptów) — do --sucho i do testu parsowania."""
    return {"start": kod_start(czas="x", skrot="x"), "usun": kod_start(True), "czesci": kod_czesci(),
            "koniec": kod_konca()}


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje kontener Workspace/KowalProba w Roblox Studio")
    ap.add_argument("--sucho", action="store_true", help="bez Studio: sprawdź dane i źródła, pokaż plan")
    ap.add_argument("--skrypty", action="store_true", help="tylko moduły i skrypty do istniejącego kontenera")
    ap.add_argument("--usun", action="store_true", help="usuń Workspace/KowalProba")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()

    if a.usun:
        zrodla, D = [], None
    else:
        zrodla = zrodla_pakietu()
        D = sprawdz_offline(zrodla)
        print("Kontener: Workspace/%s · Skrot danych: %s · placeId %d · modułów i skryptów: %d"
              % (KONTENER, D["skrot"], MIEJSCE, len(zrodla)))
        print("  %-28s → %s" % ("Folder / Model", ", ".join(FOLDERY)))
        for klasa, sciezka in INNE:
            print("  %-28s → %s" % (sciezka, klasa))
        for sciezka, klasa, kontekst, tekst, plik in zrodla:
            print("  %-28s → %s%s, zrodla/%s (%d znaków)" % (sciezka, klasa, " [RunContext=%s]" % kontekst if kontekst else "",
                                                           plik, len(tekst)))
        kz = D["kuznia"]
        print("  kuźnia: środek %s (ry %d°), E %s (zasięg %s, serwer +%s), kowal %s (ry %d°), zakres %s"
              % (kz["srodek"], kz["ry"], kz["e"], kz["zasieg"], kz["zapasSerwera"], kz["kowal"], kz["kowalRy"],
                 kz["zakres"]))
        print("  odstępy punktu E od cudzych E: %s" % kz["odstepyE"])
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
