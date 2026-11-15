#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lekka mgła w biomie Las — budowa skryptu klienta w Roblox Studio (zgoda Karola z 15.11.2026).

    python -B swiat/biom_las/mgla.py            # buduje Workspace/LasMgla/MglaLasu (Studio w trybie Edit)
    python -B swiat/biom_las/mgla.py --sucho    # tylko pokazuje, co by powstało (Studio nieużywane)
    python -B swiat/biom_las/mgla.py --usun     # usuwa kontener Workspace/LasMgla

Co powstaje: folder Workspace/LasMgla (atrybut Wygenerowane = true) z jednym skryptem MglaLasu
(Script, RunContext = Client; źródło swiat/biom_las/zrodla/MglaLasu.client.luau). Skrypt zmienia mgłę tylko
u gracza, którego kamera jest w lesie; wspólne ustawienia Lighting zostają bez zmian. Nic poza własnym
kontenerem nie jest ruszane; przed budową i po niej jest punkt historii zmian. Miejsca nie zapisuje i nie publikuje.
"""
import argparse
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
ZRODLO = os.path.join(TU, "zrodla", "MglaLasu.client.luau")
KONTENER = "LasMgla"
MIEJSCE = 129485428021967  # placeId miejsca gry

NAGLOWEK = ('if game.PlaceId ~= %d then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end\n'
            'local CH = game:GetService("ChangeHistoryService")\n' % MIEJSCE)

USUN = NAGLOWEK + '''
local f = workspace:FindFirstChild("%(k)s")
if not f then return "OK: nie ma kontenera %(k)s" end
if f:GetAttribute("Wygenerowane") ~= true then return "STOP: %(k)s bez atrybutu Wygenerowane — nie ruszam" end
CH:SetWaypoint("%(k)s: przed usunięciem")
f:Destroy()
CH:SetWaypoint("%(k)s: usunięto")
return "OK: usunięto %(k)s"
''' % {"k": KONTENER}

BUDUJ = NAGLOWEK + '''
local stary = workspace:FindFirstChild("%(k)s")
if stary and stary:GetAttribute("Wygenerowane") ~= true then
	return "STOP: w Workspace jest obiekt %(k)s bez atrybutu Wygenerowane — nie ruszam cudzej pracy"
end
CH:SetWaypoint("%(k)s: przed budową")
if stary then stary:Destroy() end
local f = Instance.new("Folder")
f.Name = "%(k)s"
f:SetAttribute("Wygenerowane", true)
f:SetAttribute("Zrodlo", "swiat/biom_las/mgla.py")
local s = Instance.new("Script")
s.Name = "MglaLasu"
s.RunContext = Enum.RunContext.Client
s.Source = __ZRODLO__
s.Parent = f
f.Parent = workspace
CH:SetWaypoint("%(k)s: zbudowano")
return "OK " .. s:GetFullName() .. " (" .. #s.Source .. " znaków)"
''' % {"k": KONTENER}


def napis_luau(tekst):
    """Długi napis Luau z poziomem nawiasów, którego nie ma w tekście."""
    n = 0
    while "]" + "=" * n + "]" in tekst:
        n += 1
    return "[" + "=" * n + "[\n" + tekst + "]" + "=" * n + "]"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Mgła w biomie Las (skrypt klienta w Studio)")
    ap.add_argument("--sucho", action="store_true", help="tylko pokaż, co by powstało")
    ap.add_argument("--usun", action="store_true", help="usuń kontener Workspace/LasMgla")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()
    with open(ZRODLO, encoding="utf-8") as f:
        zrodlo = f.read()
    if a.sucho:
        print("sucho: Workspace/%s (Folder, Wygenerowane) → MglaLasu (Script, RunContext = Client, %d znaków)"
              % (KONTENER, len(zrodlo)))
        print("sucho: OK (Studio nieużywane)")
        return
    sys.path.insert(0, os.path.join(REPO, "tools"))
    from studio_mcp import StudioMCP, StudioError, first_studio_id  # noqa: E402
    kod = USUN if a.usun else BUDUJ.replace("__ZRODLO__", napis_luau(zrodlo))
    try:
        with StudioMCP() as s:
            sid = a.studio or first_studio_id(s)
            r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=120)
    except StudioError as e:
        sys.exit("BŁĄD: %s" % e)
    print(r["text"])
    if r["is_error"] or not r["text"].startswith("OK"):
        sys.exit(2)


if __name__ == "__main__":
    main()
