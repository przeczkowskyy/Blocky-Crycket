#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Start gracza w miasteczku-bazarze (zlecenie Karola z 26.11.2026): przenosi wspólny Workspace/SpawnLocation na
znacznik startu bazaru i chowa go (niewidzialny, bez kolizji), bez budowania nowego obiektu.

    python -B tools/studio/start_w_miasteczku.py --sucho     # tylko odczyt: stan dziś → stan po zmianie, grunt pod punktem
    python -B tools/studio/start_w_miasteczku.py             # zmienia (Studio w trybie Edit; Ctrl+Z cofa)
    python -B tools/studio/start_w_miasteczku.py --studio <studio_id>

Skąd punkt: swiat/miasteczko_bazar/znaczniki.json → „start” (swiat = punkt na gruncie, kier = kierunek patrzenia gracza
na starcie — wzdłuż uliczki ku Lasowi). Liczb położenia nie ma w tym pliku: zmiana mapy bazaru (generuj.py) zmienia
znacznik, a ponowne uruchomienie przenosi start. Te same liczby czyta pakiet swiat/miasteczko_bazar_gra
(PunktStartuBazaru), więc start i przejście przez chmury „Miasteczko” trafiają w to samo miejsce.

Dlaczego przenosimy istniejący SpawnLocation, a nie budujemy nowego w kontenerze: kontenery gry (np.
MiasteczkoBazarGra) poza Studio usuwają się same (strażnik IsStudio), a start musi zostać w opublikowanym miejscu.

Po zmianie SpawnLocation: CFrame = punkt startu, górna ściana na wysokości gruntu ze znacznika, przodem w stronę „kier”
(Roblox stawia postać przodem tak jak SpawnLocation); Size = ROZMIAR (mały — Roblox losuje miejsce na całej górnej
ścianie); Transparency = 1 (także naklejki i tekstury w środku); CanCollide = false, CanQuery = false; Anchored,
Neutral i Enabled = true. Duration (pole siłowe), AllowTeamChangeOnTouch i reszta zostają bez zmian. Atrybut Zrodlo
mówi, skąd zmiana. Narzędzie ODMAWIA, gdy w Workspace jest inny włączony SpawnLocation (start byłby losowany między
nimi) albo gdy nie ma mapy Workspace/MiasteczkoBazar. Niczego nie zapisuje ani nie publikuje; Lighting nietknięty.
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
ZNACZNIKI = os.path.join(REPO, "swiat", "miasteczko_bazar", "znaczniki.json")
SPAWN = "SpawnLocation"            # Workspace/SpawnLocation — wspólny, jedyny start miejsca
MAPA = "MiasteczkoBazar"
ROZMIAR = (4.0, 1.0, 4.0)
ZRODLO = "tools/studio/start_w_miasteczku.py"

NAGLOWEK = ('if game.PlaceId ~= %d then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end\n'
            'if game:GetService("RunService"):IsRunning() then return "STOP: Studio jest w trybie Play — zmieniam tylko w trybie Edit" end\n'
            % MIEJSCE)

KOD = r'''
local H = game:GetService("HttpService")
local CH = game:GetService("ChangeHistoryService")
local ZMIEN = __ZMIEN__
local punkt = Vector3.new(__PUNKT__)
local kier = Vector3.new(__KIER__)
local rozmiar = Vector3.new(__ROZMIAR__)
local sp = workspace:FindFirstChild("__SPAWN__")
if not sp or not sp:IsA("SpawnLocation") then return "STOP: brak Workspace/__SPAWN__ (klasa SpawnLocation)" end
local inne = {}
for _, d in workspace:GetDescendants() do
	if d:IsA("SpawnLocation") and d ~= sp and d.Enabled then table.insert(inne, d:GetFullName()) end
end
local mapa = workspace:FindFirstChild("__MAPA__")
-- grunt pod punktem (tylko odczyt): promień w dół, części z kolizją, bez samego spawnu
local par = RaycastParams.new()
par.FilterType = Enum.RaycastFilterType.Exclude
par.FilterDescendantsInstances = { sp }
par.RespectCanCollide = true
local r = workspace:Raycast(punkt + Vector3.new(0, 20, 0), Vector3.new(0, -60, 0), par)
local function opis(s)
	local look = s.CFrame.LookVector
	local przezr = {}
	for _, d in s:GetDescendants() do
		if d:IsA("Decal") or d:IsA("Texture") then table.insert(przezr, d.Name .. "=" .. d.Transparency) end
	end
	return { p = { s.Position.X, s.Position.Y, s.Position.Z }, przod = { look.X, look.Z }, rozmiar = { s.Size.X, s.Size.Y, s.Size.Z },
		przezr = s.Transparency, kolizja = s.CanCollide, zapytania = s.CanQuery, kotwica = s.Anchored, neutralny = s.Neutral,
		wlaczony = s.Enabled, pole = s.Duration, zmianaDruzyny = s.AllowTeamChangeOnTouch, naklejki = przezr,
		zrodlo = s:GetAttribute("Zrodlo") }
end
local o = { przed = opis(sp), inne = inne, mapa = mapa ~= nil and mapa:GetAttribute("Wygenerowane") == true,
	grunt = r and { r.Position.Y, r.Instance:GetFullName() } or nil }
if not ZMIEN then return H:JSONEncode(o) end
if #inne > 0 then return "STOP: inne włączone SpawnLocation: " .. table.concat(inne, ", ") end
if not o.mapa then return "STOP: brak mapy Workspace/__MAPA__ (Wygenerowane) — start stałby w powietrzu" end
CH:SetWaypoint("Start w miasteczku: przed przeniesieniem SpawnLocation")
local srodek = punkt - Vector3.new(0, rozmiar.Y / 2, 0)
sp.Anchored = true
sp.Size = rozmiar
sp.CFrame = CFrame.lookAt(srodek, srodek + Vector3.new(kier.X, 0, kier.Z))
sp.Transparency = 1
sp.CanCollide = false
sp.CanQuery = false
sp.Neutral = true
sp.Enabled = true
for _, d in sp:GetDescendants() do
	if d:IsA("Decal") or d:IsA("Texture") then d.Transparency = 1 end
end
sp:SetAttribute("Zrodlo", "__ZRODLO__")
CH:SetWaypoint("Start w miasteczku: SpawnLocation przeniesiony")
o.po = opis(sp)
return H:JSONEncode(o)
'''


def start_bazaru():
    """(punkt na gruncie, kierunek) ze znacznika „start” mapy bazaru."""
    with open(ZNACZNIKI, encoding="utf-8-sig") as f:
        zn = json.load(f)
    st = zn["start"]
    p, k = [float(x) for x in st["swiat"]], [float(x) for x in st["kier"]]
    if abs(k[0]) + abs(k[2]) < 1e-6:
        raise SystemExit("BŁĄD: znacznik start bez kierunku w poziomie: %r" % (k,))
    return p, k


def kod(zmien):
    p, k = start_bazaru()
    w = lambda v: ", ".join("%g" % x for x in v)  # noqa: E731
    return NAGLOWEK + (KOD.replace("__ZMIEN__", "true" if zmien else "false").replace("__PUNKT__", w(p))
                       .replace("__KIER__", w(k)).replace("__ROZMIAR__", w(ROZMIAR)).replace("__SPAWN__", SPAWN)
                       .replace("__MAPA__", MAPA).replace("__ZRODLO__", ZRODLO))


def wypisz(nazwa, o):
    print("  %-6s poz (%.1f; %.1f; %.1f), przód (%.2f; %.2f), rozmiar %s, Transparency %s, CanCollide %s, CanQuery %s, "
          "Anchored %s, Neutral %s, Enabled %s, Duration %s, naklejki %s, Zrodlo %s" % (
              nazwa, o["p"][0], o["p"][1], o["p"][2], o["przod"][0], o["przod"][1],
              "×".join("%g" % x for x in o["rozmiar"]), o["przezr"], o["kolizja"], o["zapytania"], o["kotwica"],
              o["neutralny"], o["wlaczony"], o["pole"], ", ".join(o["naklejki"]) or "—", o.get("zrodlo") or "—"))


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Przenosi Workspace/SpawnLocation na start bazaru")
    ap.add_argument("--sucho", action="store_true", help="tylko odczyt")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()
    p, k = start_bazaru()
    print("Start bazaru ze znacznika (swiat/miasteczko_bazar/znaczniki.json): grunt (%g; %g; %g), kierunek (%g; %g; %g); "
          "SpawnLocation %s, górna ściana na wysokości gruntu" % (p[0], p[1], p[2], k[0], k[1], k[2],
                                                                  "×".join("%g" % x for x in ROZMIAR)))

    from cel_studio import MIEJSCE as MIEJSCE_GRY, wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    if MIEJSCE_GRY != MIEJSCE:
        sys.exit("BŁĄD: placeId w cel_studio.py (%s) ≠ %s — przerywam" % (MIEJSCE_GRY, MIEJSCE))
    try:
        with StudioMCP() as s:
            s.studios(wait=15)
            sid = wybierz_studio(s, a.studio)
            if not a.sucho:
                stan = s.call("get_studio_state", {"studio_id": sid})["text"]
                if "Current Studio Mode: Edit" not in stan:
                    sys.exit("Studio nie jest w trybie Edit — zatrzymaj Play i spróbuj ponownie.\n" + stan)
            r = s.call("execute_luau", {"code": kod(not a.sucho), "datamodel_type": "Edit", "studio_id": sid}, timeout=120)
            if r["is_error"]:
                raise StudioError(r["text"][:3000])
            t = r["text"].strip()
            if t.startswith("STOP"):
                sys.exit(t)
            o = json.loads(t)
            wypisz("dziś", o["przed"])
            if o.get("po"):
                wypisz("po", o["po"])
            g = o.get("grunt")
            print("  grunt pod punktem: %s; mapa %s: %s; inne włączone SpawnLocation: %s" % (
                ("y %.2f (%s), znacznik %.2f" % (g[0], g[1], p[1])) if g else "BRAK (nic pod punktem)", MAPA,
                "jest" if o["mapa"] else "BRAK", ", ".join(o["inne"]) or "brak"))
            if a.sucho:
                print("sucho: nic nie zostało zmienione")
            else:
                print("gotowe — zapisz miejsce w Studio (Ctrl+S), gdy start w Play jest dobry; Ctrl+Z cofa przeniesienie.")
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
