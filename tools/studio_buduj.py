#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buduje w Roblox Studio scenę z klocków zapisaną w `czesci.json` (format panelu: panel/README.md).

    python tools/studio_buduj.py swiat/demo_lesna_baza/czesci.json            # buduje / odbudowuje kontener
    python tools/studio_buduj.py swiat/demo_lesna_baza/czesci.json --sucho    # tylko pokaż, co by zrobił
    python tools/studio_buduj.py swiat/demo_lesna_baza/czesci.json --usun     # usuń wygenerowany kontener

Zasady bezpieczeństwa (wspólne miejsce Team Create):
- wszystko trafia do JEDNEGO kontenera (drugi człon ścieżki grupy, np. Workspace/DemoLesnaBaza); nic poza nim nie jest
  zmieniane ani usuwane;
- kontener ma atrybut `Wygenerowane = true`; odbudowa usuwa TYLKO kontener z tym atrybutem — jeśli pod tą nazwą jest
  coś cudzego, skrypt przerywa;
- przed i po budowie stawiany jest punkt historii (ChangeHistoryService) — całość cofa się jednym Ctrl+Z;
- skrypt niczego nie publikuje i nie zapisuje miejsca.
Części: Anchored, bez CanTouch; liście, kwiaty, dym, ogień i woda bez kolizji.
"""
import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from studio_mcp import StudioMCP, StudioError, first_studio_id  # noqa: E402

BEZ_KOLIZJI = ("korona", "igły", "Krzak", "Kwiat", "Grzyb", "Dym", "Tatarak", "Lilia", "Ogień", "ogień", "woda", "tafla", "wir",
               "Łata trawy", "kropka", "Zlecenie", "łańcuch", "lina", "runa", "Kryształ", "światło", "Lampa", "markiza", "baner")
BEZ_CIENIA = ("Kwiat", "Łata trawy", "Droga", "Bruk", "kropka", "Dym", "woda", "tafla", "wir", "Zlecenie", "runa", "podkład")

WSPOLNE = r'''
local G = __GRUPY__
local M = __MATERIALY__
local cache = {}
local function grupa(i)
	local m = cache[i]
	if m then return m end
	local path = string.split(G[i], "/")
	local cur = workspace
	for k = 2, #path do
		local nxt = cur:FindFirstChild(path[k])
		if not nxt then
			nxt = Instance.new(k == #path and "Model" or "Folder")
			nxt.Name = path[k]
			nxt.Parent = cur
		end
		cur = nxt
	end
	cache[i] = cur
	return cur
end
'''

START = r'''
local CH = game:GetService("ChangeHistoryService")
local nazwa = "__KORZEN__"
local stary = workspace:FindFirstChild(nazwa)
if stary then
	if stary:GetAttribute("Wygenerowane") ~= true then
		return "STOP: w Workspace jest już obiekt '" .. nazwa .. "' bez atrybutu Wygenerowane — nie ruszam cudzej pracy"
	end
	CH:SetWaypoint("Panel: przed usunięciem " .. nazwa)
	stary:Destroy()
end
if __USUN__ then
	CH:SetWaypoint("Panel: usunięto " .. nazwa)
	return "USUNIETO"
end
CH:SetWaypoint("Panel: przed budową " .. nazwa)
local f = Instance.new("Folder")
f.Name = nazwa
f:SetAttribute("Wygenerowane", true)
f:SetAttribute("Zrodlo", "__ZRODLO__")
f:SetAttribute("Zbudowano", "__CZAS__")
f.Parent = workspace
return "OK"
'''

PACZKA = r'''
local D = __DANE__
local n = 0
for _, c in D do
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
	p.Name = c[15]
	p.Anchored = true
	p.Size = Vector3.new(c[9], c[10], c[11])
	p.CFrame = CFrame.new(c[3], c[4], c[5]) * CFrame.fromOrientation(c[6], c[7], c[8])
	p.Color = Color3.fromHex(c[12])
	p.Material = Enum.Material[M[c[13] + 1]]
	p.Transparency = c[14]
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.CanTouch = false
	p.CanCollide = c[16] == 1
	p.CastShadow = c[17] == 1
	p.Parent = grupa(c[2] + 1)
	n += 1
end
return n
'''

KONIEC = r'''
local f = workspace:FindFirstChild("__KORZEN__")
local n = 0
if f then
	for _, d in f:GetDescendants() do
		if d:IsA("BasePart") then n += 1 end
	end
end
game:GetService("ChangeHistoryService"):SetWaypoint("Panel: zbudowano __KORZEN__")
return n
'''


def luau(v):
    """Wartość Pythona jako literał Luau."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, (list, tuple)):
        return "{" + ",".join(luau(x) for x in v) + "}"
    raise TypeError(type(v))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje scenę z czesci.json w Roblox Studio")
    ap.add_argument("plik")
    ap.add_argument("--paczka", type=int, default=150)
    ap.add_argument("--sucho", action="store_true")
    ap.add_argument("--usun", action="store_true")
    a = ap.parse_args()
    with open(a.plik, encoding="utf-8") as f:
        d = json.load(f)
    grupy, materialy, czesci = d["grupy"], d["materialy"], d["czesci"]
    korzenie = {g.split("/")[1] for g in grupy if g.startswith("Workspace/") and g.count("/") >= 1}
    if len(korzenie) != 1:
        sys.exit("Wszystkie grupy muszą leżeć w jednym kontenerze Workspace/<Nazwa>/… (jest: %s)" % sorted(korzenie))
    korzen = korzenie.pop()
    print("Kontener: Workspace/%s · części: %d · grup: %d · materiały: %s" % (korzen, len(czesci), len(grupy), ", ".join(materialy)))
    if a.sucho:
        return
    wspolne = WSPOLNE.replace("__GRUPY__", luau(grupy)).replace("__MATERIALY__", luau(materialy))
    zrodlo = os.path.relpath(os.path.abspath(a.plik), os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace("\\", "/")
    try:
        with StudioMCP() as s:
            sid = first_studio_id(s)
            if not sid:
                sys.exit("Roblox Studio nie jest podłączone (Assistant → Manage MCP Servers → Enable Studio as MCP server).")

            def wykonaj(kod):
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=180)
                if r["is_error"]:
                    raise StudioError(r["text"])
                return r["text"].strip()

            kod = (START.replace("__KORZEN__", korzen).replace("__USUN__", "true" if a.usun else "false")
                   .replace("__ZRODLO__", zrodlo).replace("__CZAS__", time.strftime("%Y-%m-%dT%H:%M:%S")))
            wynik = wykonaj(kod)
            print("start:", wynik)
            if a.usun or not wynik.endswith("OK"):
                return
            t0 = time.time()
            razem = 0
            for i in range(0, len(czesci), a.paczka):
                paczka = []
                for c in czesci[i:i + a.paczka]:
                    nazwa = c[14]
                    kolizja = 0 if any(k in nazwa for k in BEZ_KOLIZJI) else 1
                    cien = 0 if any(k in nazwa for k in BEZ_CIENIA) else 1
                    paczka.append(list(c) + [kolizja, cien])
                n = wykonaj(wspolne + PACZKA.replace("__DANE__", luau(paczka)))
                razem += int(float(n))
                print("  %5d / %d" % (razem, len(czesci)), flush=True)
            n = wykonaj(KONIEC.replace("__KORZEN__", korzen))
            print("gotowe: w Studio jest %s części w Workspace/%s (%.0f s)" % (n, korzen, time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
