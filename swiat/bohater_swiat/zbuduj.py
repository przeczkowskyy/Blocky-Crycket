#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buduje w Roblox Studio kontener Workspace/BohaterSwiat — „bohater w świecie” (propozycja): po wyborze klasy gracz
chodzi po świecie bohaterem swojej klasy zamiast awatara Roblox.

    python -B swiat/bohater_swiat/zbuduj.py --sucho      # bez Studio: dane, kontrola Luau, strażniki, plan budowy
    python -B swiat/bohater_swiat/zbuduj.py              # buduje / odbudowuje kontener (Studio w trybie Edit)
    python -B swiat/bohater_swiat/zbuduj.py --skrypty    # tylko moduły i skrypty (kontener i wyłącznik zostają)
    python -B swiat/bohater_swiat/zbuduj.py --usun       # usuwa Workspace/BohaterSwiat (przed publikacją miejsca)
    python -B swiat/bohater_swiat/zbuduj.py --studio <studio_id>   # gdy otwartych jest kilka okien Studio

Co powstaje (tylko w Workspace/BohaterSwiat z atrybutem Wygenerowane = true; cudzych kontenerów budowa NIE zmienia —
TestWalki2 i StrojeProba są potrzebne dopiero w grze i tylko do odczytu):
  Moduly/DaneBohatera (wygenerowany przez dane.py), Moduly/LogikaBohatera
  SerwerBohatera (RunContext = Server), KlientBohatera (RunContext = Client)
  Sygnaly/RuchBohatera (BindableFunction — umowa z mini-grami), Sygnaly/SterowanieSerwera i Sygnaly/SterowanieKlienta
  (BindableFunction, testy). Żadnych części: bohaterów składa klient w grze, lokalnie.
Atrybuty kontenera: Wygenerowane, Zrodlo, Zbudowano, Skrot, BohaterWSwiecie (wyłącznik; domyślnie true, wartość
ustawiona ręcznie w Edit przechodzi na odbudowany kontener).

Zasady (wspólne miejsce Team Create): okno wybiera swiat/test_walki_roblox/cel_studio.py (jedno okno albo --studio,
zawsze placeId gry); KAŻDY wysyłany kod sprawdza game.PlaceId i tryb Edit; ruszany jest tylko własny kontener
(obiekt o tej nazwie bez atrybutu Wygenerowane → STOP); punkty historii przed i po (Ctrl+Z cofa całość); nic nie jest
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
import sprawdz_luau_bohatera as SLB  # noqa: E402

SL = SLB.SL
MIEJSCE = 129485428021967  # placeId miejsca gry (to samo co swiat/test_walki_roblox/cel_studio.py)
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
LIMIT_ZRODLA = 199000
ZRODLO = "swiat/bohater_swiat"
ZRODLA = os.path.join(TU, "zrodla")

SKRYPTY = [
    ("DaneBohatera.luau", "ModuleScript", "Moduly/DaneBohatera", None),
    ("LogikaBohatera.luau", "ModuleScript", "Moduly/LogikaBohatera", None),
    ("SerwerBohatera.server.luau", "Script", "SerwerBohatera", "Server"),
    ("KlientBohatera.client.luau", "Script", "KlientBohatera", "Client"),
]
FOLDERY = ["Moduly", "Sygnaly"]
INNE = [
    ("BindableFunction", "Sygnaly/RuchBohatera"),
    ("BindableFunction", "Sygnaly/SterowanieSerwera"),
    ("BindableFunction", "Sygnaly/SterowanieKlienta"),
]

NAGLOWEK_MIEJSCA = ('if game.PlaceId ~= __MIEJSCE__ then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end\n'
                    'if game:GetService("RunService"):IsRunning() then return "STOP: Studio jest w trybie Play — buduję tylko w trybie Edit" end\n')

# ------------------------------------------------------------------------------------------------ kod Luau
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
local wlacznik = true
for _, d in stare do
	local v = d:GetAttribute("__WLACZNIK__")
	if v == false then wlacznik = false end
end
CH:SetWaypoint(nazwa .. ": przed budową")
for _, d in stare do d:Destroy() end
local f = Instance.new("Folder")
f.Name = nazwa
f:SetAttribute("Wygenerowane", true)
f:SetAttribute("Zrodlo", "__ZRODLO__")
f:SetAttribute("Zbudowano", "__CZAS__")
f:SetAttribute("Skrot", "__SKROT__")
f:SetAttribute("__WLACZNIK__", wlacznik)
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
return "OK (wyłącznik __WLACZNIK__ = " .. tostring(wlacznik) .. ")"
'''

SKRYPT = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera __KONTENER__"
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
local razem, skrypty, czesci, sygnaly = 0, 0, 0, 0
for _, d in f:GetDescendants() do
	razem += 1
	if d:IsA("LuaSourceContainer") then skrypty += 1 end
	if d:IsA("BasePart") then czesci += 1 end
	if d:IsA("BindableFunction") then sygnaly += 1 end
end
local zal = {}
for _, n in { __ZALEZNOSCI__ } do
	local k = workspace:FindFirstChild(n)
	table.insert(zal, n .. (if k ~= nil and k:GetAttribute("Wygenerowane") == true then " jest" else " BRAK — bez niego bohatera w grze nie będzie"))
end
game:GetService("ChangeHistoryService"):SetWaypoint("__KONTENER__: __PUNKT_HISTORII__")
local uwaga = if czesci ~= 0 then " | UWAGA: części " .. czesci .. " zamiast 0" else ""
return "instancji: " .. razem .. ", skryptów: " .. skrypty .. ", sygnałów: " .. sygnaly .. ", części: " .. czesci
	.. ", Skrot = " .. tostring(f:GetAttribute("Skrot")) .. ", __WLACZNIK__ = " .. tostring(f:GetAttribute("__WLACZNIK__"))
	.. " | " .. table.concat(zal, ", ") .. uwaga
'''


# ------------------------------------------------------------------------------------------------ pomocnicze
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
    try:
        ok, D = DANE.aktualny()
    except DANE.BladDanych as e:
        sys.exit("BŁĄD DANYCH: %s" % e)
    print("dane.py --sprawdz: %s (skrót %s, %d klas)" % ("aktualny" if ok else "NIEAKTUALNY", D["skrot"], len(D["klasy"])))
    if not ok:
        sys.exit("BŁĄD: zrodla/DaneBohatera.luau nieaktualny — uruchom python -B swiat/bohater_swiat/dane.py")
    bledy, parser = SLB.sprawdz_pliki(SLB.pliki_pakietu(), wypisz=print)
    print("sprawdz_luau_bohatera.py: %d plików, %s%s" % (len(zrodla), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
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


# ------------------------------------------------------------------------------------------------ składanie kodu
def kod_start(D, usun=False, czas="", skrot=""):
    return (START.replace("__KONTENER__", D["kontener"]).replace("__USUN__", "true" if usun else "false")
            .replace("__ZRODLO__", ZRODLO).replace("__CZAS__", czas).replace("__SKROT__", skrot)
            .replace("__WLACZNIK__", D["atrybut_wlacznika"])
            .replace("__FOLDERY__", ", ".join(DANE._napis(x) for x in FOLDERY))
            .replace("__INNE__", ", ".join("{%s, %s}" % (DANE._napis(k), DANE._napis(p)) for k, p in INNE)))


def kod_skryptu(kontener, sciezka, klasa, kontekst, tekst):
    kod = (SKRYPT.replace("__KONTENER__", kontener).replace("__SCIEZKA__", sciezka).replace("__KLASA__", klasa)
           .replace("__RUNCONTEXT__", "s.RunContext = Enum.RunContext.%s" % kontekst if kontekst else ""))
    return kod.replace("__ZRODLO__", dlugi_napis(tekst))


def kod_konca(D, punkt_historii="zbudowano"):
    return (KONIEC.replace("__KONTENER__", D["kontener"]).replace("__PUNKT_HISTORII__", punkt_historii)
            .replace("__WLACZNIK__", D["atrybut_wlacznika"])
            .replace("__ZALEZNOSCI__", ", ".join(DANE._napis(D[k]) for k in ("kontener_walki", "kontener_strojow"))))


def kod_wymiany(D):
    """Początek --skrypty: kontener musi być, nowy skrót danych, punkt historii."""
    return ('local f = workspace:FindFirstChild("%s") if not f or f:GetAttribute("Wygenerowane") ~= true '
            'then return "STOP: brak kontenera — zbuduj całość" end '
            'game:GetService("ChangeHistoryService"):SetWaypoint("%s: przed wymianą skryptów") '
            'f:SetAttribute("Skrot", "%s") return "OK"' % (D["kontener"], D["kontener"], D["skrot"]))


def wszystkie_kody(D):
    """Kod wysyłany do Studio (bez skryptów) — do --sucho i do testu parsowania."""
    return {"start": kod_start(D, czas="x", skrot="x"), "usun": kod_start(D, True), "koniec": kod_konca(D),
            "wymiana": kod_wymiany(D), "skrypt": kod_skryptu("X", "Moduly/Y", "ModuleScript", None, "return 1")}


# ------------------------------------------------------------------------------------------------ główna
def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje kontener Workspace/BohaterSwiat w Roblox Studio")
    ap.add_argument("--sucho", action="store_true", help="bez Studio: sprawdź dane i źródła, pokaż plan")
    ap.add_argument("--skrypty", action="store_true", help="tylko moduły i skrypty do istniejącego kontenera")
    ap.add_argument("--usun", action="store_true", help="usuń Workspace/BohaterSwiat")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()

    if a.usun and not a.sucho:
        U = DANE.ustawienia()
        D = {"kontener": U["kontener"], "atrybut_wlacznika": U["atrybut_wlacznika"]}
        zrodla = []
    else:
        zrodla = zrodla_pakietu()
        D = sprawdz_offline(zrodla)
        print("Kontener: Workspace/%s · skrót danych %s · placeId %d · modułów i skryptów: %d"
              % (D["kontener"], D["skrot"], MIEJSCE, len(zrodla)))
        print("  %-26s → %s" % ("Folder", ", ".join(FOLDERY)))
        for klasa, sciezka in INNE:
            print("  %-26s → %s" % (sciezka, klasa))
        for sciezka, klasa, kontekst, tekst, plik in zrodla:
            print("  %-26s → %s%s, zrodla/%s (%d znaków)" % (sciezka, klasa, " [RunContext=%s]" % kontekst if kontekst else "",
                                                           plik, len(tekst)))
        print("  %-26s → %s = true (wartość false ustawiona w Edit przechodzi na odbudowany kontener)"
              % ("wyłącznik", D["atrybut_wlacznika"]))
        print("  %-26s → Workspace/%s (Moduly/Klipy, Moduly/DaneAktorow) i Workspace/%s (Moduly/Ubieranie) — tylko "
              "odczyt, w grze" % ("zależności", D["kontener_walki"], D["kontener_strojow"]))
        for linia in DANE.podsumowanie(D):
            print(linia)
        kody = wszystkie_kody(D)
        print("  kod wysyłany do Studio: %s" % ", ".join("%s %d zn." % (k, len(v)) for k, v in kody.items()))
    if a.sucho:
        print("sucho: OK (Studio nieużywane)")
        return

    # --- dopiero tutaj Studio (--sucho niczego z tego nie importuje)
    for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
        if _s not in sys.path:
            sys.path.append(_s)
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

            t0 = time.time()

            def skrypty():
                for sciezka, klasa, kontekst, tekst, plik in zrodla:
                    print("  skrypt:", wykonaj(kod_skryptu(D["kontener"], sciezka, klasa, kontekst, tekst)))

            if a.skrypty:
                wykonaj(kod_wymiany(D))
                skrypty()
                print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca(D, "skrypty wymienione")), time.time() - t0))
                return
            wynik = wykonaj(kod_start(D, a.usun, time.strftime("%Y-%m-%dT%H:%M:%S"), "" if a.usun else D["skrot"]))
            print("start:", wynik)
            if a.usun or not wynik.startswith("OK"):
                return
            skrypty()
            print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca(D)), time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
