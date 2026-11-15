#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kolory zaimportowanych siatek: tekstura koloru prosto na części zamiast przez SurfaceAppearance.

    python -B swiat/postacie/roblox_import_kolory.py                      # wszystkie modele „(import …)” w TestPostaci
    python -B swiat/postacie/roblox_import_kolory.py --tylko "Zwiadowca (import FBX)"
    python -B swiat/postacie/roblox_import_kolory.py --sucho              # tylko pokaż, co by się zmieniło

Po co (ustalone 15.11.2026): importer Roblox dokłada każdej części SurfaceAppearance z mapą koloru, metalu i szorstkości
oraz z BŁĘDNYM odwołaniem emisji (`rbxassetid://5`). Studio nie potrafi wtedy złożyć paczki tekstur („Failed to upload
TexturePack … Referenced Asset 5 is NOT found”) i model jest szary. Samo wyczyszczenie emisji nie pomogło. Pomaga
ustawienie mapy koloru jako `TextureID` części i usunięcie SurfaceAppearance — nasze modele są płasko kolorowane, więc
map metalu i szorstkości nie potrzebują (to też tańsze na telefonie). Adresy usuniętych map zostają w atrybutach części
(ImportColorMap, ImportMetalnessMap, ImportRoughnessMap), żeby dało się wrócić.

Dotyka tylko kontenera Workspace/TestPostaci (atrybut Wygenerowane) w miejscu gry; punkt historii przed i po.
Uruchamiaj po każdym imporcie (roblox_import.py / roblox_import_lasu.py), Studio w trybie Edit.
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
MIEJSCE = 129485428021967  # placeId miejsca gry

KOD = '''
if game.PlaceId ~= %(miejsce)d then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end
local k = workspace:FindFirstChild("TestPostaci")
if not k or k:GetAttribute("Wygenerowane") ~= true then return "STOP: brak Workspace/TestPostaci z atrybutem Wygenerowane" end
local TYLKO = %(tylko)s
local SUCHO = %(sucho)s
local CH = game:GetService("ChangeHistoryService")
if not SUCHO then CH:SetWaypoint("Import: przed zamianą SurfaceAppearance na TextureID") end
local w = {}
for _, m in k:GetChildren() do
	local pasuje = (#TYLKO == 0 and string.find(m.Name, "(import ", 1, true) ~= nil) or table.find(TYLKO, m.Name) ~= nil
	if pasuje then
		local n = 0
		for _, d in m:GetDescendants() do
			if d:IsA("SurfaceAppearance") and d.Parent:IsA("MeshPart") and d.ColorMap ~= "" then
				n += 1
				if not SUCHO then
					local cz = d.Parent
					cz:SetAttribute("ImportColorMap", d.ColorMap)
					cz:SetAttribute("ImportMetalnessMap", d.MetalnessMap)
					cz:SetAttribute("ImportRoughnessMap", d.RoughnessMap)
					cz.TextureID = d.ColorMap
					cz.Color = Color3.new(1, 1, 1)
					d:Destroy()
				end
			end
		end
		table.insert(w, m.Name .. ": " .. n)
	end
end
if not SUCHO then CH:SetWaypoint("Import: SurfaceAppearance zamienione na TextureID") end
return "OK " .. (SUCHO and "(na sucho) " or "") .. (#w > 0 and table.concat(w, " | ") or "nie ma modeli z importu")
'''


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Kolory zaimportowanych siatek (TextureID zamiast SurfaceAppearance)")
    ap.add_argument("--tylko", action="append", default=[], help="dokładna nazwa modelu w TestPostaci (można powtarzać)")
    ap.add_argument("--sucho", action="store_true", help="niczego nie zmieniaj, tylko policz")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()
    kod = KOD % {"miejsce": MIEJSCE, "sucho": "true" if a.sucho else "false",
                 "tylko": "{" + ", ".join(json.dumps(n, ensure_ascii=False) for n in a.tylko) + "}"}
    sys.path.insert(0, os.path.join(REPO, "tools"))
    from studio_mcp import StudioMCP, StudioError, first_studio_id  # noqa: E402
    try:
        with StudioMCP() as s:
            s.studios(wait=15)
            sid = a.studio or first_studio_id(s)
            r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=120)
    except StudioError as e:
        sys.exit("BŁĄD: %s" % e)
    print(r["text"])
    if r["is_error"] or not r["text"].startswith("OK"):
        sys.exit(2)


if __name__ == "__main__":
    main()
