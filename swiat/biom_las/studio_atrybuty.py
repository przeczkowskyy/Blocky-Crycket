#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ustawia w Studio właściwości streamingu grup lasu z `znaczniki.json` (czesci.json ich nie przenosi).

    python -B swiat/biom_las/studio_atrybuty.py            # ustawia i wypisuje, co zrobił
    python -B swiat/biom_las/studio_atrybuty.py --sucho    # tylko pokazuje listę grup

- `grupy_stale_wczytane` → Model.ModelStreamingMode = Persistent (sylwetki punktów orientacyjnych),
- `grupy_niski_detal`    → Model.LevelOfDetail = StreamingMesh (kępy lasu, mur, tło).
Działa WYŁĄCZNIE w kontenerze Workspace/BiomLas z atrybutem `Wygenerowane` (inaczej przerywa). Grupa, która powstała
jako Folder (bo pierwsza część trafiła do jej podgrupy), jest zamieniana na Model o tej samej nazwie z tymi samymi
dziećmi — tylko w tym kontenerze. Punkt historii przed i po. Niczego nie publikuje ani nie zapisuje; ustawień miejsca
(Workspace.StreamingEnabled, Lighting) nie zmienia — tylko je odczytuje i wypisuje.
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
sys.path.insert(0, os.path.join(_REPO, "tools"))
from studio_mcp import StudioMCP, StudioError, first_studio_id  # noqa: E402

PLACE_ID = 129485428021967

KOD = r'''
local KORZEN = "__KORZEN__"
local STALE = __STALE__
local NISKI = __NISKI__
local CH = game:GetService("ChangeHistoryService")
if game.PlaceId ~= __PLACE__ then return "STOP: inne miejsce (PlaceId " .. game.PlaceId .. ")" end
local f = workspace:FindFirstChild(KORZEN)
if not f then return "STOP: brak Workspace/" .. KORZEN end
if f:GetAttribute("Wygenerowane") ~= true then return "STOP: " .. KORZEN .. " bez atrybutu Wygenerowane" end
CH:SetWaypoint("Panel: przed atrybutami " .. KORZEN)
local function znajdz(sc)
	local cur = f
	for _, s in string.split(sc, "/") do
		cur = cur and cur:FindFirstChild(s)
	end
	return cur
end
local function model(sc)
	local m = znajdz(sc)
	if not m then return nil, "brak" end
	if m:IsA("Model") then return m, "" end
	if m:IsA("Folder") then                                   -- zamień Folder na Model (tylko w naszym kontenerze)
		local nowy = Instance.new("Model")
		nowy.Name = m.Name
		for k, v in m:GetAttributes() do nowy:SetAttribute(k, v) end
		for _, c in m:GetChildren() do c.Parent = nowy end
		nowy.Parent = m.Parent
		m:Destroy()
		return nowy, " (Folder→Model)"
	end
	return nil, "klasa " .. m.ClassName
end
local ok, zle, uw = 0, {}, {}
for _, sc in STALE do
	local m, info = model(sc)
	if m then
		m.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
		m:SetAttribute("Streaming", "Persistent")
		ok += 1
		if info ~= "" then table.insert(uw, sc .. info) end
	else
		table.insert(zle, sc .. ": " .. info)
	end
end
local ok2 = 0
for _, sc in NISKI do
	local m, info = model(sc)
	if m then
		m.LevelOfDetail = Enum.ModelLevelOfDetail.StreamingMesh
		m:SetAttribute("Streaming", "StreamingMesh")
		ok2 += 1
		if info ~= "" then table.insert(uw, sc .. info) end
	else
		table.insert(zle, sc .. ": " .. info)
	end
end
CH:SetWaypoint("Panel: atrybuty " .. KORZEN)
return string.format("Persistent: %d/%d, StreamingMesh: %d/%d; zamiany: %s; błędy: %s; Workspace.StreamingEnabled=%s",
	ok, #STALE, ok2, #NISKI, (#uw > 0 and table.concat(uw, ", ") or "brak"), (#zle > 0 and table.concat(zle, "; ") or "brak"),
	tostring(workspace.StreamingEnabled))
'''


def luau_lista(xs):
    return "{" + ",".join(json.dumps(x, ensure_ascii=False) for x in xs) + "}"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Właściwości streamingu grup lasu w Studio")
    ap.add_argument("--znaczniki", default=os.path.join(_TU, "znaczniki.json"))
    ap.add_argument("--sucho", action="store_true")
    a = ap.parse_args()
    with open(a.znaczniki, encoding="utf-8") as f:
        z = json.load(f)
    k = z.get("kontener") or "Workspace/BiomLas"
    korzen = (k.get("nazwa") if isinstance(k, dict) else k).split("/")[-1]
    stale = z["grupy_stale_wczytane"]["grupy"]
    niski = z["grupy_niski_detal"]["grupy"]
    print("Kontener: Workspace/%s · Persistent: %d grup · StreamingMesh: %d grup" % (korzen, len(stale), len(niski)))
    if a.sucho:
        return
    kod = (KOD.replace("__KORZEN__", korzen).replace("__STALE__", luau_lista(stale))
           .replace("__NISKI__", luau_lista(niski)).replace("__PLACE__", str(PLACE_ID)))
    try:
        with StudioMCP() as s:
            sid = first_studio_id(s)
            if not sid:
                sys.exit("Roblox Studio nie jest podłączone.")
            r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=120)
            print(r["text"].strip())
            if r["is_error"] or r["text"].strip().startswith("STOP"):
                sys.exit(1)
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
