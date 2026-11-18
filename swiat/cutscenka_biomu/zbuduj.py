#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cutscenka biomu w Roblox Studio (D-077; propozycja wykonania): kontener Workspace/CutscenkaBiomu.

    python -B swiat/cutscenka_biomu/zbuduj.py --sucho     # bez Studio: dane aktualne, kontrola Luau, plan budowy
    python -B swiat/cutscenka_biomu/zbuduj.py             # zbuduj od nowa własny kontener (kilka sekund)
    python -B swiat/cutscenka_biomu/zbuduj.py --skrypty   # tylko wymień moduły i skrypty w istniejącym kontenerze
    python -B swiat/cutscenka_biomu/zbuduj.py --stan      # odczyt: co stoi w kontenerze (niczego nie zmienia)
    python -B swiat/cutscenka_biomu/zbuduj.py --usun      # usuń własny kontener (cudzy obiekt o tej nazwie zostaje)

Co robi w Studio (tylko tryb Edit, tylko miejsce gry — numer miejsca bierze z swiat/test_walki_roblox/cel_studio.py):
punkt historii, własny kontener (atrybut Wygenerowane) budowany od nowa — foldery Moduly, Zdalne, Sygnaly, zdarzenie
zdalne, uchwyty, dwa moduły i dwa skrypty; punkt historii. Kontener nie ma ani jednej części. Niczego nie zapisuje,
nie publikuje, nie rusza Lighting ani cudzych instancji. Wyłącznik pomijania (atrybut Pomijanie = false ustawiony
w Edit) przechodzi na odbudowany kontener. Stary przelot pasa ustępuje tylko wtedy, gdy kontenery gry biomów mają
skrypt SerwerPasa z haczykiem (swiat/las_pas_gra — wgrywa się go budowniczymi tamtych pakietów).
"""
import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if TU in sys.path:
    sys.path.remove(TU)
sys.path.insert(0, TU)                                 # własne moduły pakietu zawsze pierwsze
import dane as DN  # noqa: E402
import sprawdz_luau_cutscenki as SLC  # noqa: E402

SL = SLC.SL
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
LIMIT_ZRODLA = 199000
ZRODLA = os.path.join(TU, "zrodla")

SKRYPTY = [
    ("DaneCutscenki.luau", "ModuleScript", "Moduly/DaneCutscenki", None),
    ("LogikaCutscenki.luau", "ModuleScript", "Moduly/LogikaCutscenki", None),
    ("SerwerCutscenki.server.luau", "Script", "SerwerCutscenki", "Server"),
    ("KlientCutscenki.client.luau", "Script", "KlientCutscenki", "Client"),
]
FOLDERY = ["Moduly", "Zdalne", "Sygnaly"]
INNE = [
    ("RemoteEvent", "Zdalne/ZdarzeniaCutscenki"),
    ("BindableFunction", "Sygnaly/SterowanieCutscenki"),
    ("BindableFunction", "Sygnaly/SterowanieCutscenkiKlienta"),
]

NAGLOWEK_MIEJSCA = ('if game.PlaceId ~= __MIEJSCE__ then return "STOP: inne miejsce — nic nie zmieniono" end\n'
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
local wlacznik = true
for _, d in stare do
	if d:GetAttribute("__WLACZNIK__") == false then wlacznik = false end
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
return "OK (pomijanie: __WLACZNIK__ = " .. tostring(wlacznik) .. ")"
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
s.Source = __TEKST__
s.Parent = rodzic
return "OK " .. s:GetFullName() .. " (" .. #s.Source .. " znaków)"
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
local biomy = {}
for _, w in { __BIOMY__ } do
	local gra, mapa = workspace:FindFirstChild(w[1]), workspace:FindFirstChild(w[2])
	local haczyk = false
	local sp = gra and gra:FindFirstChild("SerwerPasa")
	if sp and sp:IsA("LuaSourceContainer") then
		haczyk = string.find(sp.Source, "__USTEPUJE__", 1, true) ~= nil
	end
	table.insert(biomy, w[1] .. (if gra then " jest" else " BRAK") .. ", mapa " .. w[2] .. (if mapa then " jest" else " BRAK")
		.. ", haczyk w SerwerPasa: " .. (if haczyk then "jest" else "BRAK — biom zostanie przy starym przelocie"))
end
game:GetService("ChangeHistoryService"):SetWaypoint("__KONTENER__: __PUNKT_HISTORII__")
return "instancji: " .. razem .. ", skryptów: " .. skrypty .. ", części: " .. czesci .. ", Skrot = " .. tostring(f:GetAttribute("Skrot"))
	.. " | " .. table.concat(biomy, " | ")
'''

# odczyt stanu (Edit i Play): JSON; niczego nie zmienia
STAN = r'''
local HS = game:GetService("HttpService")
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then
	return HS:JSONEncode({ jest = false })
end
local w = { jest = true, atrybuty = {}, dzieci = {}, czesci = 0 }
for k, v in f:GetAttributes() do
	w.atrybuty[k] = if typeof(v) == "Vector3" then tostring(v) else v
end
for _, d in f:GetDescendants() do
	if d:IsA("BasePart") then w.czesci += 1 end
	if d:IsA("LuaSourceContainer") then
		table.insert(w.dzieci, d.Name .. " (" .. d.ClassName .. ", " .. #d.Source .. " zn.)")
	elseif not d:IsA("Folder") then
		table.insert(w.dzieci, d.Name .. " (" .. d.ClassName .. ")")
	end
end
return HS:JSONEncode(w)
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
        sys.exit("BŁĄD: brak plików w zrodla/: " + ", ".join(braki))
    return wynik


def sprawdz_offline(zrodla, wypisz=print):
    try:
        ok, D = DN.aktualny()
    except DN.BladDanych as e:
        sys.exit("BŁĄD DANYCH: %s" % e)
    wypisz("dane.py --sprawdz: %s (skrót %s, %d biomy)" % ("aktualny" if ok else "NIEAKTUALNY", D["skrot"], len(D["biomy"])))
    if not ok:
        sys.exit("BŁĄD: zrodla/DaneCutscenki.luau nieaktualny — uruchom python -B swiat/cutscenka_biomu/dane.py")
    bledy, parser = SLC.sprawdz_pliki(SLC.pliki_pakietu(), wypisz=wypisz)
    wypisz("sprawdz_luau_cutscenki.py: %d plików, %s%s" % (len(zrodla), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
                                                         " (z parserem luau_mini)" if parser else " (bez parsera)"))
    if bledy:
        for b in bledy:
            wypisz("  " + b)
        sys.exit("BŁĄD: kontrola Luau")
    for sciezka, _klasa, _kontekst, tekst, plik in zrodla:
        if not SL.pierwsza_instrukcja(tekst).startswith(STRAZNIK):
            sys.exit("BŁĄD: %s (%s) nie zaczyna się od strażnika Studio" % (sciezka, plik))
        if len(tekst) > LIMIT_ZRODLA:
            sys.exit("BŁĄD: %s ma %d znaków (limit Source 200 000)" % (sciezka, len(tekst)))
    return D


def _wlacznik(D):
    return D["U"]["oprawa"]["pomijanie"]["atrybut_wylacznika"]


def kod_start(D, usun=False, czas="", skrot=""):
    return (START.replace("__KONTENER__", D["kontener"]).replace("__USUN__", "true" if usun else "false")
            .replace("__ZRODLO__", D["U"]["zrodlo"]).replace("__CZAS__", czas).replace("__SKROT__", skrot)
            .replace("__WLACZNIK__", _wlacznik(D))
            .replace("__FOLDERY__", ", ".join(DN._napis(x) for x in FOLDERY))
            .replace("__INNE__", ", ".join("{%s, %s}" % (DN._napis(k), DN._napis(p)) for k, p in INNE)))


def kod_skryptu(kontener, sciezka, klasa, kontekst, tekst):
    kod = (SKRYPT.replace("__KONTENER__", kontener).replace("__SCIEZKA__", sciezka).replace("__KLASA__", klasa)
           .replace("__RUNCONTEXT__", "s.RunContext = Enum.RunContext.%s" % kontekst if kontekst else ""))
    return kod.replace("__TEKST__", dlugi_napis(tekst))


def kod_konca(D, punkt_historii="zbudowano"):
    return (KONIEC.replace("__KONTENER__", D["kontener"]).replace("__PUNKT_HISTORII__", punkt_historii)
            .replace("__USTEPUJE__", D["U"]["zaleznosci"]["haczyk_pasa"]["atrybut_ustepuje"])
            .replace("__BIOMY__", ", ".join("{%s, %s}" % (DN._napis(b["kontenerGry"]), DN._napis(b["mapa"]))
                                            for b in D["biomy"])))


def kod_wymiany(D):
    return ('local f = workspace:FindFirstChild("%s") if not f or f:GetAttribute("Wygenerowane") ~= true '
            'then return "STOP: brak kontenera — zbuduj całość" end '
            'game:GetService("ChangeHistoryService"):SetWaypoint("%s: przed wymianą skryptów") '
            'f:SetAttribute("Skrot", "%s") return "OK"' % (D["kontener"], D["kontener"], D["skrot"]))


def kod_stanu(kontener):
    return STAN.replace("__KONTENER__", kontener)


def wszystkie_kody(D):
    """Kod wysyłany do Studio (bez skryptów) — do --sucho i do testu parsowania."""
    return {"start": kod_start(D, czas="x", skrot="x"), "usun": kod_start(D, True), "koniec": kod_konca(D),
            "wymiana": kod_wymiany(D), "stan": kod_stanu(D["kontener"]),
            "skrypt": kod_skryptu("X", "Moduly/Y", "ModuleScript", None, "return 1")}


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje kontener Workspace/CutscenkaBiomu w Roblox Studio")
    ap.add_argument("--sucho", action="store_true", help="bez Studio: sprawdź dane i źródła, pokaż plan")
    ap.add_argument("--skrypty", action="store_true", help="tylko moduły i skrypty do istniejącego kontenera")
    ap.add_argument("--usun", action="store_true", help="usuń Workspace/CutscenkaBiomu")
    ap.add_argument("--stan", action="store_true", help="odczytaj, co stoi w kontenerze")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()

    U = DN.ustawienia()
    if (a.usun or a.stan) and not a.sucho:
        D = {"kontener": U["kontener"], "U": U, "skrot": "", "biomy": []}
        zrodla = []
    else:
        zrodla = zrodla_pakietu()
        D = sprawdz_offline(zrodla)
        print("Kontener: Workspace/%s · skrót danych %s · modułów i skryptów: %d" % (D["kontener"], D["skrot"], len(zrodla)))
        print("  %-34s → %s" % ("Folder", ", ".join(FOLDERY)))
        for klasa, sciezka in INNE:
            print("  %-34s → %s" % (sciezka, klasa))
        for sciezka, klasa, kontekst, tekst, plik in zrodla:
            print("  %-34s → %s%s, zrodla/%s (%d znaków)" % (sciezka, klasa, " [RunContext=%s]" % kontekst if kontekst else "",
                                                           plik, len(tekst)))
        print("  %-34s → %s = true (false ustawione w Edit przechodzi na odbudowany kontener)" % ("wyłącznik pomijania", _wlacznik(D)))
        for linia in DN.opis(D):
            print(linia)
        kody = wszystkie_kody(D)
        print("  kod wysyłany do Studio: %s" % ", ".join("%s %d zn." % (k, len(v)) for k, v in kody.items()))
    if a.sucho:
        print("sucho: OK (Studio nieużywane)")
        return 0

    # --- dopiero tutaj Studio (--sucho niczego z tego nie importuje)
    for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
        if _s not in sys.path:
            sys.path.append(_s)
    from cel_studio import MIEJSCE, wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    try:
        with StudioMCP() as s:
            s.studios(wait=15)
            sid = wybierz_studio(s, a.studio)
            stan = s.call("get_studio_state", {"studio_id": sid})["text"]
            if a.stan:
                tryb = "Server" if "Current Studio Mode: Edit" not in stan else "Edit"
                r = s.call("execute_luau", {"code": kod_stanu(D["kontener"]), "datamodel_type": tryb, "studio_id": sid}, timeout=60)
                print(json.dumps(json.loads(r["text"].strip()), ensure_ascii=False, indent=1))
                return 0
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
                for sciezka, klasa, kontekst, tekst, _plik in zrodla:
                    print("  skrypt:", wykonaj(kod_skryptu(D["kontener"], sciezka, klasa, kontekst, tekst)))

            if a.skrypty:
                wykonaj(kod_wymiany(D))
                skrypty()
                print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca(D, "skrypty wymienione")), time.time() - t0))
                return 0
            wynik = wykonaj(kod_start(D, a.usun, time.strftime("%Y-%m-%dT%H:%M:%S"), "" if a.usun else D["skrot"]))
            print("start:", wynik)
            if a.usun or not wynik.startswith("OK"):
                return 0
            skrypty()
            print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca(D)), time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
