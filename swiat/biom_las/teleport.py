#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teleport między miasteczkiem a biomem Las — budowa w Roblox Studio (prośba Karola z 15.11.2026).

    python -B swiat/biom_las/teleport.py            # buduje Workspace/LasTeleport (Studio w trybie Edit)
    python -B swiat/biom_las/teleport.py --sucho    # tylko pokazuje, co by powstało (Studio nieużywane)
    python -B swiat/biom_las/teleport.py --usun     # usuwa kontener Workspace/LasTeleport

Co powstaje (wszystko w jednym kontenerze Workspace/LasTeleport z atrybutem Wygenerowane = true):
  PortalStart   — mała brama z zieloną taflą przy miejscu startu gracza; E → las (skrót do testów)
  BramaMiejska  — niewidoczny punkt z podpowiedzią w Bramie Miejskiej Krzywego Miasteczka; E → las (jak w planie lasu)
  KamienPowrotu — niewidoczny punkt z podpowiedzią przy Kamieniu Powrotu w lesie; E → Brama Miejska
  TeleportLasu  — skrypt serwera (źródło swiat/biom_las/zrodla/TeleportLasu.server.luau), działa tylko w Studio
  Steruj        — haczyk testowy (BindableFunction)
Budowa sama szuka wolnego miejsca na portal wokół miejsca startu, mierzy grunt w punktach docelowych i zapisuje je jako
atrybuty kontenera. Niczego poza własnym kontenerem nie rusza; przed budową i po niej jest punkt historii zmian.
Miejsca nie zapisuje i nie publikuje.
"""
import argparse
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
ZRODLO = os.path.join(TU, "zrodla", "TeleportLasu.server.luau")
KONTENER = "LasTeleport"
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
local las = workspace:FindFirstChild("BiomLas")
local miasto = workspace:FindFirstChild("KrzyweMiasteczko")
local brama = miasto and miasto:FindFirstChild("BramaMiejska")
if not las or not brama then
	return "STOP: brak Workspace/BiomLas albo Workspace/KrzyweMiasteczko/BramaMiejska"
end
CH:SetWaypoint("%(k)s: przed budową")
if stary then stary:Destroy() end

local uwagi = {}
local function grunt(x, z, pomin)
	local par = RaycastParams.new()
	par.FilterType = Enum.RaycastFilterType.Exclude
	par.FilterDescendantsInstances = pomin or {}
	local r = workspace:Raycast(Vector3.new(x, 120, z), Vector3.new(0, -300, 0), par)
	return r and r.Position.Y or 0
end

-- środek i obrys Bramy Miejskiej (Folder albo Model)
local mn, mx = Vector3.new(1e9, 1e9, 1e9), Vector3.new(-1e9, -1e9, -1e9)
for _, p in brama:GetDescendants() do
	if p:IsA("BasePart") then
		mn = mn:Min(p.Position - p.Size / 2)
		mx = mx:Max(p.Position + p.Size / 2)
	end
end
local srodekBramy = (mn + mx) / 2
local srodekMiasta = Vector3.new(0.3, 0, -698.7) -- środek układu Krzywego Miasteczka w świecie
local doMiasta = Vector3.new(srodekMiasta.X - srodekBramy.X, 0, srodekMiasta.Z - srodekBramy.Z).Unit

local f = Instance.new("Folder")
f.Name = "%(k)s"
f:SetAttribute("Wygenerowane", true)
f:SetAttribute("Zrodlo", "swiat/biom_las/teleport.py")

-- punkty docelowe
local lasXZ = Vector3.new(-200, 0, -2400) -- wejście lasu (uklad.json „wejscie”), w układzie świata
local punktLas = Vector3.new(lasXZ.X, grunt(lasXZ.X, lasXZ.Z) + 3.2, lasXZ.Z)
local mXZ = srodekBramy + doMiasta * 18
local punktMiasta = Vector3.new(mXZ.X, grunt(mXZ.X, mXZ.Z) + 3.2, mXZ.Z)
f:SetAttribute("PunktLas", punktLas)
f:SetAttribute("PatrzLas", Vector3.new(0, punktLas.Y, -2000))
f:SetAttribute("PunktMiasteczka", punktMiasta)
f:SetAttribute("PatrzMiasteczko", Vector3.new(srodekMiasta.X, punktMiasta.Y, srodekMiasta.Z))

local function podpowiedz(rodzic, cel, akcja, obiekt, zasieg)
	local pp = Instance.new("ProximityPrompt")
	pp.Name = "PodpowiedzTeleportu"
	pp.ActionText = akcja
	pp.ObjectText = obiekt
	pp.KeyboardKeyCode = Enum.KeyCode.E
	pp.HoldDuration = 0
	pp.MaxActivationDistance = zasieg
	pp.RequiresLineOfSight = false
	pp.Enabled = false -- włącza skrypt serwera (tylko w Studio)
	pp:SetAttribute("Cel", cel)
	pp.Parent = rodzic
	return pp
end

local function tabliczka(rodzic, napis, wysokosc)
	local b = Instance.new("BillboardGui")
	b.Name = "Tabliczka"
	b.Size = UDim2.fromOffset(190, 44)
	b.StudsOffset = Vector3.new(0, wysokosc, 0)
	b.MaxDistance = 160
	b.AlwaysOnTop = false
	local t = Instance.new("TextLabel")
	t.Size = UDim2.fromScale(1, 1)
	t.BackgroundColor3 = Color3.fromRGB(27, 24, 38)
	t.BackgroundTransparency = 0.2
	t.TextColor3 = Color3.fromRGB(190, 255, 170)
	t.Font = Enum.Font.FredokaOne
	t.TextScaled = true
	t.Text = napis
	local r = Instance.new("UICorner")
	r.CornerRadius = UDim.new(0, 10)
	r.Parent = t
	t.Parent = b
	b.Parent = rodzic
end

local function punkt(nazwa, pozycja, cel, akcja, obiekt, zasieg, napis)
	local p = Instance.new("Part")
	p.Name = nazwa
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Transparency = 1
	p.Size = Vector3.new(2, 2, 2)
	p.Position = pozycja
	podpowiedz(p, cel, akcja, obiekt, zasieg)
	if napis then tabliczka(p, napis, 7) end
	p.Parent = f
	return p
end

-- 1. Brama Miejska → las (w przejściu bramy, na wysokości postaci)
local yBramy = grunt(srodekBramy.X, srodekBramy.Z, { brama })
punkt("BramaMiejska", Vector3.new(srodekBramy.X, yBramy + 3.5, srodekBramy.Z), "las", "Idź do lasu", "Bór Pod Ukłonem", 18, "LAS  (E)")

-- 2. Kamień Powrotu → miasteczko
local kamien
for _, p in las:GetDescendants() do
	if p:IsA("BasePart") and p.Name == "Kamień Powrotu romb" then kamien = p break end
end
if kamien then
	punkt("KamienPowrotu", kamien.Position, "miasteczko", "Wróć do miasteczka", "Kamień Powrotu", 12, "MIASTECZKO  (E)")
else
	table.insert(uwagi, "nie znalazłem części „Kamień Powrotu romb” — punkt powrotu stoi w wejściu lasu")
	punkt("KamienPowrotu", punktLas + Vector3.new(6, 0, 0), "miasteczko", "Wróć do miasteczka", "Kamień Powrotu", 12, "MIASTECZKO  (E)")
end

-- 3. Portal przy miejscu startu: pierwsze wolne miejsce na okręgu wokół SpawnLocation
local start = workspace:FindFirstChildWhichIsA("SpawnLocation", true)
local sPos = start and start.Position or Vector3.new(0, 0, 0)
local wybrane, opisWyboru
for _, promien in { 16, 20, 24, 28, 34 } do
	for i = 0, 15 do
		local a = math.rad(i * 22.5)
		local x, z = sPos.X + math.sin(a) * promien, sPos.Z + math.cos(a) * promien
		local y = grunt(x, z)
		if math.abs(y - sPos.Y) < 3 then
			local zajete = workspace:GetPartBoundsInBox(CFrame.new(x, y + 6.2, z), Vector3.new(11, 10, 11))
			if #zajete == 0 then
				wybrane = Vector3.new(x, y, z)
				opisWyboru = string.format("promień %%d, kąt %%.0f°", promien, i * 22.5)
				break
			end
		end
	end
	if wybrane then break end
end
if not wybrane then
	wybrane = Vector3.new(sPos.X + 16, grunt(sPos.X + 16, sPos.Z), sPos.Z)
	opisWyboru = "brak wolnego miejsca — postawiony 16 studów na wschód od startu"
	table.insert(uwagi, opisWyboru)
end

local portal = Instance.new("Model")
portal.Name = "PortalStart"
local doStartu = Vector3.new(sPos.X - wybrane.X, 0, sPos.Z - wybrane.Z)
local cfPortalu = CFrame.lookAt(wybrane, wybrane + (doStartu.Magnitude > 0.1 and doStartu.Unit or Vector3.new(0, 0, 1)))
local function klocek(nazwa, rozmiar, przesuniecie, kolor, material, przezroczystosc, kolizja)
	local p = Instance.new("Part")
	p.Name = nazwa
	p.Anchored = true
	p.Size = rozmiar
	p.CFrame = cfPortalu * CFrame.new(przesuniecie)
	p.Color = kolor
	p.Material = material
	p.Transparency = przezroczystosc or 0
	p.CanCollide = kolizja ~= false
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = portal
	return p
end
local pien = Color3.fromRGB(92, 62, 38)
klocek("Słup lewy", Vector3.new(1.4, 9, 1.4), Vector3.new(-3.3, 4.5, 0), pien, Enum.Material.Wood)
klocek("Słup prawy", Vector3.new(1.4, 9, 1.4), Vector3.new(3.3, 4.5, 0), pien, Enum.Material.Wood)
klocek("Belka", Vector3.new(9, 1.4, 1.8), Vector3.new(0, 9.5, 0), pien, Enum.Material.Wood)
klocek("Daszek", Vector3.new(10.4, 0.6, 2.6), Vector3.new(0, 10.5, 0), Color3.fromRGB(58, 122, 64), Enum.Material.Grass)
local tafla = klocek("Tafla", Vector3.new(5.2, 8, 0.3), Vector3.new(0, 4.2, 0), Color3.fromRGB(120, 255, 140), Enum.Material.Neon, 0.35, false)
tafla.CanQuery = false
podpowiedz(tafla, "las", "Leć do lasu", "Bór Pod Ukłonem", 14)
tabliczka(tafla, "LAS  (E)", 7.2)
portal.PrimaryPart = tafla
portal.Parent = f

local steruj = Instance.new("BindableFunction")
steruj.Name = "Steruj"
steruj.Parent = f

local s = Instance.new("Script")
s.Name = "TeleportLasu"
s.RunContext = Enum.RunContext.Server
s.Source = __ZRODLO__
s.Parent = f
f.Parent = workspace
CH:SetWaypoint("%(k)s: zbudowano")
return string.format("OK %%s | portal przy starcie: (%%.1f; %%.1f; %%.1f) %%s | las: (%%.1f; %%.1f; %%.1f) | miasteczko: (%%.1f; %%.1f; %%.1f) | brama: (%%.1f; %%.1f; %%.1f)%%s",
	s:GetFullName(), wybrane.X, wybrane.Y, wybrane.Z, opisWyboru, punktLas.X, punktLas.Y, punktLas.Z,
	punktMiasta.X, punktMiasta.Y, punktMiasta.Z, srodekBramy.X, yBramy + 3.5, srodekBramy.Z,
	#uwagi > 0 and (" | UWAGI: " .. table.concat(uwagi, "; ")) or "")
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
    ap = argparse.ArgumentParser(description="Teleport miasteczko <-> las (kontener w Studio)")
    ap.add_argument("--sucho", action="store_true", help="tylko pokaż, co by powstało")
    ap.add_argument("--usun", action="store_true", help="usuń kontener Workspace/LasTeleport")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()
    with open(ZRODLO, encoding="utf-8") as f:
        zrodlo = f.read()
    if a.sucho:
        print("sucho: Workspace/%s (Folder, Wygenerowane) → PortalStart, BramaMiejska, KamienPowrotu, Steruj, "
              "TeleportLasu (Script, RunContext = Server, %d znaków)" % (KONTENER, len(zrodlo)))
        print("sucho: OK (Studio nieużywane)")
        return
    sys.path.insert(0, os.path.join(REPO, "tools"))
    from studio_mcp import StudioMCP, StudioError, first_studio_id  # noqa: E402
    kod = USUN if a.usun else BUDUJ.replace("__ZRODLO__", napis_luau(zrodlo))
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
