#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buduje w Roblox Studio kontener Workspace/StanGracza — jeden właściciel stanu gracza między systemami gry
(łup z walk, awans, statystyki klasy, trening → statystyki, bohater walki z danych gracza). Bez części w świecie.

    python -B swiat/stan_gracza/zbuduj.py --sucho      # bez Studio: dane, kontrola Luau, strażniki, plan budowy
    python -B swiat/stan_gracza/zbuduj.py              # buduje / odbudowuje kontener (Studio w trybie Edit)
    python -B swiat/stan_gracza/zbuduj.py --skrypty    # tylko moduły i skrypty do istniejącego kontenera
    python -B swiat/stan_gracza/zbuduj.py --usun       # usuwa Workspace/StanGracza (gra wraca do stanu sprzed pakietu)
    python -B swiat/stan_gracza/zbuduj.py --studio <studio_id>   # gdy otwartych jest kilka okien Studio

Co powstaje (tylko w Workspace/StanGracza z atrybutem Wygenerowane = true; cudzych obiektów budowa NIE zmienia):
  Moduly/DaneStanu, Moduly/LogikaStanu        ModuleScript (zrodla/; DaneStanu wygenerowany przez dane.py)
  SerwerStanu (RunContext = Server), KlientStanu (RunContext = Client)
  Zdalne/ZdarzeniaStanu                        RemoteEvent ("awans" do klienta, "pokaz" do serwera)
  Sygnaly/Bohater, Sygnaly/PrzyznajLup         BindableFunction — woła je SerwerPotworow obu lasów
  Sygnaly/SterowanieSerwera                    BindableFunction — haczyk testowy
Atrybuty kontenera: Wygenerowane, Zrodlo, Zbudowano, Skrot, StatystykiKlasy (true; false = zostają wartości testowe
statystyk z src/server/PlayerStatsDefaults). StatystykiKlasy ustawione ręcznie w Edit przechodzi na odbudowany kontener.

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
import dane as DANE  # noqa: E402
import sprawdz_luau_stanu as SLS  # noqa: E402

SL = SLS.SL
MIEJSCE = 129485428021967  # placeId miejsca gry (to samo co swiat/test_walki_roblox/cel_studio.py)
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
LIMIT_ZRODLA = 199000
ZRODLO = "swiat/stan_gracza"
ZRODLA = os.path.join(TU, "zrodla")
KONTENER = "StanGracza"

SKRYPTY = [
    ("DaneStanu.luau", "ModuleScript", "Moduly/DaneStanu", None),
    ("LogikaStanu.luau", "ModuleScript", "Moduly/LogikaStanu", None),
    ("SerwerStanu.server.luau", "Script", "SerwerStanu", "Server"),
    ("KlientStanu.client.luau", "Script", "KlientStanu", "Client"),
]
FOLDERY = ["Moduly", "Zdalne", "Sygnaly"]
INNE = [
    ("RemoteEvent", "Zdalne/ZdarzeniaStanu"),
    ("BindableFunction", "Sygnaly/Bohater"),
    ("BindableFunction", "Sygnaly/PrzyznajLup"),
    ("BindableFunction", "Sygnaly/SterowanieSerwera"),
]
ATRYBUTY_TESTOWE = ["StatystykiKlasy"]

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
local testowe = {}
for _, d in stare do
	for _, a in { __TESTOWE__ } do
		local v = d:GetAttribute(a)
		if v ~= nil then testowe[a] = v end
	end
end
CH:SetWaypoint(nazwa .. ": przed budową")
for _, d in stare do d:Destroy() end
local f = Instance.new("Folder")
f.Name = nazwa
f:SetAttribute("Wygenerowane", true)
f:SetAttribute("Zrodlo", "__ZRODLO__")
f:SetAttribute("Zbudowano", "__CZAS__")
f:SetAttribute("Skrot", "__SKROT__")
f:SetAttribute("StatystykiKlasy", true)
for a, v in testowe do f:SetAttribute(a, v) end
for _, n in { __FOLDERY__ } do
	local d = Instance.new("Folder")
	d.Name = n
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

KONIEC = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f then return "STOP: brak kontenera" end
local razem, skrypty = 0, 0
for _, d in f:GetDescendants() do
	razem += 1
	if d:IsA("LuaSourceContainer") then skrypty += 1 end
end
game:GetService("ChangeHistoryService"):SetWaypoint("__KONTENER__: __PUNKT_HISTORII__")
local uwaga = if skrypty ~= __OCZEKIWANE__ then " | UWAGA: skryptów " .. skrypty .. " zamiast __OCZEKIWANE__" else ""
return "instancji: " .. razem .. ", skryptów: " .. skrypty .. ", StatystykiKlasy = " .. tostring(f:GetAttribute("StatystykiKlasy"))
	.. ", Skrot = " .. tostring(f:GetAttribute("Skrot")) .. uwaga
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
    ok, D = DANE.aktualny()
    print("dane.py --sprawdz: %s (skrót %s, przypadków %d)" % ("aktualny" if ok else "NIEAKTUALNY", D["skrot"],
                                                              sum(len(v) for v in D["przypadki"].values())))
    if not ok:
        sys.exit("BŁĄD: zrodla/DaneStanu.luau nieaktualny — uruchom python -B swiat/stan_gracza/dane.py")
    if D["kontener"] != KONTENER:
        sys.exit("BŁĄD: D.kontener (%s) ≠ %s" % (D["kontener"], KONTENER))
    bledy, parser = SLS.sprawdz_pliki(SLS.pliki_pakietu(), wypisz=print)
    print("sprawdz_luau_stanu.py: %d plików, %s%s" % (len(zrodla), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
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


def kod_start(usun=False, czas="", skrot=""):
    return (START.replace("__KONTENER__", KONTENER).replace("__USUN__", "true" if usun else "false")
            .replace("__ZRODLO__", ZRODLO).replace("__CZAS__", czas).replace("__SKROT__", skrot)
            .replace("__TESTOWE__", ", ".join(DANE._napis(a) for a in ATRYBUTY_TESTOWE))
            .replace("__FOLDERY__", ", ".join(DANE._napis(x) for x in FOLDERY))
            .replace("__INNE__", ", ".join("{%s, %s}" % (DANE._napis(k), DANE._napis(p)) for k, p in INNE)))


def kod_skryptu(sciezka, klasa, kontekst, tekst):
    kod = (SKRYPT.replace("__KONTENER__", KONTENER).replace("__SCIEZKA__", sciezka).replace("__KLASA__", klasa)
           .replace("__RUNCONTEXT__", "s.RunContext = Enum.RunContext.%s" % kontekst if kontekst else ""))
    return kod.replace("__ZRODLO__", dlugi_napis(tekst))


def kod_konca(punkt_historii="zbudowano"):
    return (KONIEC.replace("__KONTENER__", KONTENER).replace("__OCZEKIWANE__", str(len(SKRYPTY)))
            .replace("__PUNKT_HISTORII__", punkt_historii))


def wszystkie_kody():
    """Kod wysyłany do Studio (bez skryptów) — do --sucho i do testu parsowania."""
    return {"start": kod_start(czas="x", skrot="x"), "usun": kod_start(True), "koniec": kod_konca()}


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje kontener Workspace/StanGracza w Roblox Studio")
    ap.add_argument("--sucho", action="store_true", help="bez Studio: sprawdź dane i źródła, pokaż plan")
    ap.add_argument("--skrypty", action="store_true", help="tylko moduły i skrypty do istniejącego kontenera")
    ap.add_argument("--usun", action="store_true", help="usuń Workspace/StanGracza")
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
        print("  atrybuty: StatystykiKlasy = true (przenoszone przy odbudowie: %s)" % ", ".join(ATRYBUTY_TESTOWE))
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

            def skrypty():
                for sciezka, klasa, kontekst, tekst, plik in zrodla:
                    print("  skrypt:", wykonaj(kod_skryptu(sciezka, klasa, kontekst, tekst)))

            t0 = time.time()
            if a.skrypty:
                wykonaj('local f = workspace:FindFirstChild("%s") if not f or f:GetAttribute("Wygenerowane") ~= true '
                        'then return "STOP: brak kontenera — zbuduj całość" end '
                        'game:GetService("ChangeHistoryService"):SetWaypoint("%s: przed wymianą skryptów") '
                        'f:SetAttribute("Skrot", "%s") return "OK"' % (KONTENER, KONTENER, D["skrot"]))
                skrypty()
                print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca("skrypty wymienione")), time.time() - t0))
                return
            wynik = wykonaj(kod_start(a.usun, time.strftime("%Y-%m-%dT%H:%M:%S"), "" if a.usun else D["skrot"]))
            print("start:", wynik)
            if a.usun or wynik != "OK":
                return
            skrypty()
            print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca()), time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
