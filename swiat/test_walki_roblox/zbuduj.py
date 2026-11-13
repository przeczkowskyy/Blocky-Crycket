#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Odtwarza w Roblox Studio kontener testu walki 3D (Workspace/TestWalki) ze źródeł w tym folderze.

    python -B swiat/test_walki_roblox/zbuduj.py            # buduje / odbudowuje kontener (idempotentnie)
    python -B swiat/test_walki_roblox/zbuduj.py --sucho    # tylko sprawdza źródła i pokazuje plan
    python -B swiat/test_walki_roblox/zbuduj.py --usun     # usuwa wygenerowany kontener
    python -B swiat/test_walki_roblox/zbuduj.py --studio <studio_id>   # wymagane, gdy otwartych jest kilka okien Studio

Zasady bezpieczeństwa (wspólne miejsce Team Create) — te same co w tools/studio_buduj.py:
- wszystko trafia do JEDNEGO kontenera Workspace/TestWalki z atrybutem `Wygenerowane = true`;
- odbudowa i --usun ruszają TYLKO kontener z tym atrybutem — jeśli pod tą nazwą jest coś cudzego, skrypt przerywa;
- przed budową sprawdzane jest, czy w miejscu areny nic obcego nie stoi (GetPartBoundsInBox);
- przed i po stawiany jest punkt historii (ChangeHistoryService) — całość cofa się przez Ctrl+Z;
- każdy skrypt musi zaczynać się od strażnika „poza Studio nic nie rób” (sprawdzane przed wysłaniem);
- skrypt działa tylko w trybie Edit; niczego nie publikuje, nie zapisuje miejsca i nie zmienia Lighting;
- okno Studio wybiera cel_studio.py: bez --studio musi być otwarte dokładnie jedno, a miejsce musi mieć placeId gry
  (sprawdzane też wewnątrz Studio przez game.PlaceId) — inaczej skrypt przerywa, zanim cokolwiek zmieni.
"""
import argparse
import os
import re
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
sys.path.insert(0, os.path.join(REPO, "tools"))
from studio_mcp import StudioMCP, StudioError  # noqa: E402
sys.path.insert(0, TU)
from cel_studio import MIEJSCE, wybierz_studio  # noqa: E402

KONTENER = "TestWalki"
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'

# (plik źródłowy, klasa, ścieżka w kontenerze, RunContext)
SKRYPTY = [
    ("zrodla/Ustawienia.luau", "ModuleScript", "Moduly/Ustawienia", None),
    ("zrodla/SilnikWalki.luau", "ModuleScript", "Moduly/SilnikWalki", None),
    ("zrodla/InterfejsWalki.luau", "ModuleScript", "Moduly/InterfejsWalki", None),
    ("zrodla/OdtwarzaczWalki.luau", "ModuleScript", "Moduly/OdtwarzaczWalki", None),
    ("zrodla/SerwerWalki.server.luau", "Script", "SerwerWalki", "Server"),
    ("zrodla/KlientWalki.client.luau", "Script", "KlientWalki", "Client"),
]
BUDOWA = ["budowa/arena.luau", "budowa/aktorzy.luau"]

START = r'''
local CH = game:GetService("ChangeHistoryService")
local RunService = game:GetService("RunService")
if RunService:IsRunning() then
	return "STOP: Studio jest w trybie Play — buduję tylko w trybie Edit"
end
if game.PlaceId ~= __MIEJSCE__ then
	return "STOP: otwarte miejsce ma placeId " .. tostring(game.PlaceId) .. ", a nie __MIEJSCE__ — nie buduję w cudzym miejscu"
end
local nazwa = "__KONTENER__"
local stary = workspace:FindFirstChild(nazwa)
if stary and stary:GetAttribute("Wygenerowane") ~= true then
	return "STOP: w Workspace jest już obiekt '" .. nazwa .. "' bez atrybutu Wygenerowane — nie ruszam cudzej pracy"
end
if __USUN__ then
	if not stary then
		return "USUNIETO (kontenera nie było)"
	end
	CH:SetWaypoint("TestWalki: przed usunięciem")
	stary:Destroy()
	CH:SetWaypoint("TestWalki: usunięto")
	return "USUNIETO"
end
-- czy miejsce jest wolne: nic poza płytą Baseplate i (starym) własnym kontenerem
local srodek = Vector3.new(__SRODEK__)
local filtr = OverlapParams.new()
filtr.FilterType = Enum.RaycastFilterType.Exclude
local wyklucz = {}
if stary then table.insert(wyklucz, stary) end
local plyta = workspace:FindFirstChild("Baseplate")
if plyta then table.insert(wyklucz, plyta) end
filtr.FilterDescendantsInstances = wyklucz
local obce = workspace:GetPartBoundsInBox(CFrame.new(srodek + Vector3.new(4, 100, 0)), Vector3.new(112, 400, 104), filtr)
if #obce > 0 then
	local lista = {}
	for i = 1, math.min(#obce, 5) do table.insert(lista, obce[i]:GetFullName()) end
	return "STOP: w miejscu areny stoi coś obcego (" .. #obce .. " części), np. " .. table.concat(lista, ", ")
end
CH:SetWaypoint("TestWalki: przed budową")
if stary then stary:Destroy() end
local f = Instance.new("Folder")
f.Name = nazwa
f:SetAttribute("Wygenerowane", true)
f:SetAttribute("Zrodlo", "swiat/test_walki_roblox")
f:SetAttribute("Zbudowano", "__CZAS__")
for _, n in { "Moduly", "Zdalne", "Sygnaly" } do
	local d = Instance.new("Folder")
	d.Name = n
	d.Parent = f
end
local rf = Instance.new("RemoteFunction")
rf.Name = "RozpocznijWalke"
rf.Parent = f.Zdalne
for _, n in { "StartTestu", "PominTest", "ZamknijTest" } do
	local b = Instance.new("BindableEvent")
	b.Name = n
	b.Parent = f.Sygnaly
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
local ile = {}
local razem = 0
for _, d in f:GetDescendants() do
	razem += 1
	local k = if d:IsA("BasePart") then "części" elseif d:IsA("LuaSourceContainer") then "skrypty" else nil
	if k then ile[k] = (ile[k] or 0) + 1 end
end
game:GetService("ChangeHistoryService"):SetWaypoint("TestWalki: zbudowano")
return "instancji: " .. razem .. ", części: " .. (ile["części"] or 0) .. ", skryptów: " .. (ile["skrypty"] or 0)
'''


def bez_komentarzy_na_poczatku(tekst):
    """Zwraca kod bez wiodących komentarzy i pustych linii (do sprawdzenia strażnika)."""
    t = tekst.lstrip()
    while True:
        if t.startswith("--[["):
            koniec = t.find("]]")
            if koniec < 0:
                return ""
            t = t[koniec + 2:].lstrip()
        elif t.startswith("--"):
            t = t.split("\n", 1)[1].lstrip() if "\n" in t else ""
        else:
            return t


def dlugi_napis(tekst):
    """Tekst jako literał Luau [==[ … ]==] z poziomem, którego nie ma w treści."""
    poziom = 3
    while ("]" + "=" * poziom + "]") in tekst or ("[" + "=" * poziom + "[") in tekst:
        poziom += 1
    return "[" + "=" * poziom + "[\n" + tekst + "]" + "=" * poziom + "]"


def wczytaj(wzgledna):
    with open(os.path.join(TU, wzgledna), encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def srodek_z_ustawien():
    m = re.search(r"U\.SRODEK\s*=\s*Vector3\.new\(([^)]*)\)", wczytaj("zrodla/Ustawienia.luau"))
    if not m:
        sys.exit("Nie znalazłem U.SRODEK w zrodla/Ustawienia.luau")
    return m.group(1).strip()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje kontener testu walki 3D w Roblox Studio")
    ap.add_argument("--usun", action="store_true", help="usuń wygenerowany kontener")
    ap.add_argument("--sucho", action="store_true", help="tylko sprawdź źródła i pokaż plan")
    ap.add_argument("--studio", default=None, help="studio_id (wymagane, gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()

    zrodla = []
    for plik, klasa, sciezka, kontekst in SKRYPTY:
        tekst = wczytaj(plik)
        if not bez_komentarzy_na_poczatku(tekst).startswith(STRAZNIK):
            sys.exit("BŁĄD: %s nie zaczyna się od strażnika „%s”" % (plik, STRAZNIK))
        zrodla.append((plik, klasa, sciezka, kontekst, tekst))
    budowa = [(plik, wczytaj(plik)) for plik in BUDOWA]
    srodek = srodek_z_ustawien()
    print("Kontener: Workspace/%s · środek areny: (%s) · skryptów: %d · kroków budowy: %d" % (KONTENER, srodek, len(zrodla), len(budowa)))
    for plik, klasa, sciezka, kontekst, tekst in zrodla:
        print("  %-34s → %s %s%s (%d znaków)" % (plik, klasa, sciezka, " [RunContext=%s]" % kontekst if kontekst else "", len(tekst)))
    if a.sucho:
        return

    try:
        with StudioMCP() as s:
            sid = wybierz_studio(s, a.studio)
            stan = s.call("get_studio_state", {"studio_id": sid})["text"]
            if "Current Studio Mode: Edit" not in stan:
                sys.exit("Studio nie jest w trybie Edit — zatrzymaj Play i spróbuj ponownie.\n" + stan)

            def wykonaj(kod):
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
                if r["is_error"]:
                    raise StudioError(r["text"])
                return r["text"].strip()

            t0 = time.time()
            wynik = wykonaj(START.replace("__KONTENER__", KONTENER).replace("__USUN__", "true" if a.usun else "false")
                            .replace("__MIEJSCE__", str(MIEJSCE))
                            .replace("__SRODEK__", srodek).replace("__CZAS__", time.strftime("%Y-%m-%dT%H:%M:%S")))
            print("start:", wynik)
            if a.usun or not wynik.endswith("OK"):
                if wynik.startswith("STOP"):
                    sys.exit(2)
                return
            for plik, klasa, sciezka, kontekst, tekst in zrodla:
                kod = (SKRYPT.replace("__KONTENER__", KONTENER).replace("__SCIEZKA__", sciezka).replace("__KLASA__", klasa)
                       .replace("__RUNCONTEXT__", "s.RunContext = Enum.RunContext.%s" % kontekst if kontekst else "")
                       .replace("__ZRODLO__", dlugi_napis(tekst)))
                wynik = wykonaj(kod)
                print("  skrypt:", wynik)
                if wynik.startswith("STOP"):
                    sys.exit(2)
            for plik, kod in budowa:
                wynik = wykonaj(kod)
                print("  %s: %s" % (plik, wynik))
                if wynik.startswith("STOP"):
                    sys.exit(2)
            print("gotowe: %s (%.0f s)" % (wykonaj(KONIEC.replace("__KONTENER__", KONTENER)), time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
