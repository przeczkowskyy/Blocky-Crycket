#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Szara płyta Baseplate pod miasteczkiem — chowanie i przywracanie (zlecenie Karola z 26.11.2026: „usuń placeholdery”).

    python -B tools/studio/plyta_bazowa.py --sucho     # tylko odczyt: stan płyty (przezroczystość, tekstury, atrybuty)
    python -B tools/studio/plyta_bazowa.py --ukryj     # Transparency = 1 płycie i jej teksturom / naklejkom
    python -B tools/studio/plyta_bazowa.py --pokaz     # przywraca zapamiętane wartości
    [--studio <studio_id>]

Rusza wyłącznie wspólny Workspace.Baseplate (bezpośrednie dziecko Workspace, BasePart) i jego Texture / Decal.
Kolizje, położenie, rozmiar, materiał i kolor zostają bez zmian — postać dalej stoi na płycie tam, gdzie mapa nie ma
gruntu. Przed zmianą zapisuje dotychczasowe przezroczystości w atrybucie płyty PlytaPrzed (JSON), a atrybuty
PlytaUkryta = true i Zrodlo = "tools/studio/plyta_bazowa.py" mówią, kto i co zmienił; --pokaz wraca do zapisanych
wartości i zdejmuje te atrybuty. Punkty historii przed i po (Ctrl+Z cofa). Tylko tryb Edit i tylko miejsce gry
(placeId); niczego nie zapisuje ani nie publikuje, Lighting nietknięty.
"""
import argparse
import json
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
    if _s not in sys.path:
        sys.path.insert(0, _s)

MIEJSCE = 129485428021967  # placeId miejsca gry (to samo co swiat/test_walki_roblox/cel_studio.py)
ZRODLO = "tools/studio/plyta_bazowa.py"

KOD = r'''
if game.PlaceId ~= __MIEJSCE__ then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end
if game:GetService("RunService"):IsRunning() then return "STOP: Studio jest w trybie Play — zmieniam tylko w trybie Edit" end
local H = game:GetService("HttpService")
local CH = game:GetService("ChangeHistoryService")
local TRYB = "__TRYB__"
local plyty = {}
for _, d in workspace:GetChildren() do
	if d.Name == "Baseplate" then table.insert(plyty, d) end
end
if #plyty == 0 then return "STOP: w Workspace nie ma obiektu Baseplate" end
if #plyty > 1 then return "STOP: w Workspace jest " .. #plyty .. " obiektów o nazwie Baseplate — nie zgaduję, który" end
local p = plyty[1]
if not p:IsA("BasePart") then return "STOP: Workspace.Baseplate to " .. p.ClassName .. ", nie BasePart" end
local function stan()
	local dzieci = {}
	for _, d in p:GetChildren() do
		if d:IsA("Texture") or d:IsA("Decal") then table.insert(dzieci, { n = d.Name, k = d.ClassName, t = d.Transparency }) end
	end
	return { przezroczystosc = p.Transparency, kolizja = p.CanCollide, rozmiar = { p.Size.X, p.Size.Y, p.Size.Z },
		pozycja = { p.Position.X, p.Position.Y, p.Position.Z }, dzieci = dzieci, ukryta = p:GetAttribute("PlytaUkryta") == true,
		zrodlo = p:GetAttribute("Zrodlo") }
end
local przed = stan()
if TRYB == "sucho" then return H:JSONEncode({ przed = przed }) end
if TRYB == "ukryj" then
	if p:GetAttribute("PlytaUkryta") == true then return H:JSONEncode({ przed = przed, uwaga = "już ukryta — bez zmian" }) end
	CH:SetWaypoint("Baseplate: przed ukryciem")
	local zapis = { p = p.Transparency, dzieci = {} }
	for i, d in p:GetChildren() do
		if d:IsA("Texture") or d:IsA("Decal") then
			zapis.dzieci[tostring(i) .. ":" .. d.Name] = d.Transparency
			d.Transparency = 1
		end
	end
	p:SetAttribute("PlytaPrzed", H:JSONEncode(zapis))
	p.Transparency = 1
	p:SetAttribute("PlytaUkryta", true)
	p:SetAttribute("Zrodlo", "__ZRODLO__")
	CH:SetWaypoint("Baseplate: ukryta")
elseif TRYB == "pokaz" then
	local ok, zapis = pcall(function() return H:JSONDecode(p:GetAttribute("PlytaPrzed")) end)
	if not ok or type(zapis) ~= "table" then return "STOP: brak zapisu PlytaPrzed — płyta nie była ukryta tym narzędziem" end
	CH:SetWaypoint("Baseplate: przed pokazaniem")
	p.Transparency = zapis.p or 0
	for i, d in p:GetChildren() do
		local t = zapis.dzieci and zapis.dzieci[tostring(i) .. ":" .. d.Name]
		if t ~= nil and (d:IsA("Texture") or d:IsA("Decal")) then d.Transparency = t end
	end
	p:SetAttribute("PlytaPrzed", nil)
	p:SetAttribute("PlytaUkryta", nil)
	if p:GetAttribute("Zrodlo") == "__ZRODLO__" then p:SetAttribute("Zrodlo", nil) end
	CH:SetWaypoint("Baseplate: pokazana")
end
return H:JSONEncode({ przed = przed, po = stan() })
'''


def kod(tryb):
    return KOD.replace("__MIEJSCE__", str(MIEJSCE)).replace("__TRYB__", tryb).replace("__ZRODLO__", ZRODLO)


def wypisz(etykieta, s):
    print("  %-5s Transparency %s, CanCollide %s, rozmiar %s, środek %s, tekstury/naklejki %s, PlytaUkryta %s, Zrodlo %s" % (
        etykieta, s.get("przezroczystosc"), s.get("kolizja"), "×".join("%g" % x for x in s.get("rozmiar") or []),
        "; ".join("%g" % x for x in s.get("pozycja") or []),
        ", ".join("%s %s=%s" % (d["k"], d["n"], d["t"]) for d in s.get("dzieci") or []) or "brak",
        s.get("ukryta"), s.get("zrodlo")))


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Chowa albo przywraca szarą płytę Workspace.Baseplate")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--sucho", action="store_true", help="tylko odczyt")
    g.add_argument("--ukryj", action="store_true", help="Transparency = 1 płycie i jej teksturom (kolizje zostają)")
    g.add_argument("--pokaz", action="store_true", help="przywraca zapamiętane przezroczystości")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()
    tryb = "sucho" if a.sucho else ("ukryj" if a.ukryj else "pokaz")

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
                sys.exit("Studio nie jest w trybie Edit — narzędzie działa tylko w Edit.\n" + stan)
            r = s.call("execute_luau", {"code": kod(tryb), "datamodel_type": "Edit", "studio_id": sid}, timeout=120)
            if r["is_error"]:
                raise StudioError(r["text"][:3000])
            t = r["text"].strip()
            if t.startswith("STOP"):
                sys.exit(t)
            o = json.loads(t)
            wypisz("przed", o["przed"])
            if o.get("po"):
                wypisz("po", o["po"])
            if o.get("uwaga"):
                print("  uwaga:", o["uwaga"])
            print("sucho: nic nie zostało zmienione" if a.sucho else "gotowe (Ctrl+Z w Studio cofa; zapis miejsca: Ctrl+S)")
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
