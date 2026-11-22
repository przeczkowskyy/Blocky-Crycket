#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Budowa zabawek w Studio: Workspace/ZabawkiGra (moduły, skrypty, sygnały, wzorce potworów, dwa tereny).

    python -B swiat/zabawki/zbuduj.py [--sucho] [--skrypty] [--studio <id>]
    python -B swiat/zabawki/zbuduj.py --wlacz on|off --studio <id>   # wyłącznik (atrybut ZabawkiWlaczone + Enabled skryptów)

Skrypty bez strażnika „tylko Studio” (działają w prywatnej wersji testowej na telefonie). Budowa odmawia w miejscu gry
B&C, poza trybem Edit i gdy w Workspace jest obcy obiekt o tej nazwie (bez atrybutu Wygenerowane). Wzorce potworów
kopiuje z Workspace/PetArenaGra/Wzorce (albo ReplicatedStorage/PetArenaWzorce) do własnego kontenera.
"""
import argparse
import json
import math
import os
import sys
import time

sys.dont_write_bytecode = True
PAKIET = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(PAKIET))
sys.path.insert(0, PAKIET)
sys.path.append(os.path.join(REPO, "tools"))
import dane as DN  # noqa: E402

ZR = os.path.join(PAKIET, "zrodla")
MODULY = ["DaneZabawek", "LogikaZabawek", "EfektyZabawek"]
SKRYPTY = [("SerwerZabawek", "SerwerZabawek.server.luau", "Server"), ("KlientZabawek", "KlientZabawek.client.luau", "Client")]


def log(*a):
    print("Zabawki |", *a, flush=True)


def zrodla():
    w = {}
    for n in MODULY:
        w[n] = open(os.path.join(ZR, n + ".luau"), encoding="utf-8").read()
    for n, plik, _ in SKRYPTY:
        w[n] = open(os.path.join(ZR, plik), encoding="utf-8").read()
    for n, t in w.items():
        if "IsStudio" in t and n != "EfektyZabawek":
            raise SystemExit("BŁĄD: %s zawiera strażnika Studio — zabawki mają działać poza Studio" % n)
    return w


def czesc(lista, grupa, nazwa, poz, roz, kolor, mat="SmoothPlastic", ksztalt="Block", obrot=(0, 0, 0), przez=0):
    lista.append({"g": grupa, "n": nazwa, "p": [round(x, 3) for x in poz], "s": [round(x, 3) for x in roz], "c": kolor, "m": mat,
                  "k": ksztalt, "r": [round(x, 4) for x in obrot], "t": przez})


def scena(D):
    Z, W = D["zjadacz"], D["wabik"]
    L = []
    # ------------------------------------------------ zabawka 1: pole z niskim murem i skałami
    cx, cy, cz = Z["srodek"]
    R = Z["pole_r"]
    czesc(L, "Teren1", "Pole", (cx, cy - 2, cz), (4, 2 * R + 24, 2 * R + 24), "8FD46B", "Grass", "Cylinder", (0, 0, math.pi / 2))
    czesc(L, "Teren1", "Obrzeze", (cx, cy - 2.1, cz), (4, 2 * R + 60, 2 * R + 60), "6FB04F", "Grass", "Cylinder", (0, 0, math.pi / 2))
    n = 48
    for i in range(n):
        a = 2 * math.pi * i / n
        r = R + 1.5
        kol = ["F2C36B", "E8A85A"][i % 2]
        czesc(L, "Teren1", "Mur", (cx + math.sin(a) * r, cy + Z["mur_y"] / 2, cz + math.cos(a) * r),
              (2 * math.pi * r / n + 0.6, Z["mur_y"], 2.5), kol, "Slate", "Block", (0, a, 0))
    for i, s in enumerate(Z["skalyPoz"]):
        czesc(L, "Teren1", "Skala", (cx + s["x"], cy + 2, cz + s["z"]), (5, s["r"] * 2, s["r"] * 2), ["9C8C7A", "8A7C6C", "A89A86"][i % 3],
              "Slate", "Cylinder", (0, 0, math.pi / 2))
        czesc(L, "Teren1", "SkalaCzubek", (cx + s["x"], cy + 4.6, cz + s["z"]), (s["r"] * 1.4, 3, s["r"] * 1.4), "B5A792", "Slate", "Ball")
    # łąka kwiatów (kolorowe kropki) — tanio, żeby pole nie było puste
    for i in range(60):
        a = i * 2.39996
        r = math.sqrt((i + 0.5) / 60) * (R - 6)
        czesc(L, "Teren1", "Kwiat", (cx + math.sin(a) * r, cy + 0.05, cz + math.cos(a) * r), (0.1, 2.2, 2.2),
              ["FFF07A", "FF9AD8", "9BE8FF", "FFFFFF"][i % 4], "SmoothPlastic", "Cylinder", (0, 0, math.pi / 2))
    czesc(L, "Teren1", "Schowek", (cx, cy - 33, cz), (20, 2, 20), "3A3148")
    # ------------------------------------------------ zabawka 2: zagrody na skraju łąki, strefy
    wx, wy, wz = W["srodek"]
    sz, dl = W["laka_szer"], W["laka_dl"]
    czesc(L, "Teren2", "Laka", (wx, wy - 1, wz + dl / 2 - 20), (sz + 60, 2, dl + 70), "86CF62", "Grass")
    for i, St in enumerate(W["strefy"]):
        czesc(L, "Teren2", "Strefa" + St["nazwa"], (wx, wy + 0.02, wz + (St["od"] + St["koniec"]) / 2), (sz, 0.1, St["koniec"] - St["od"] - 0.6),
              St["kolor"], "Grass")
        czesc(L, "Teren2", "Granica", (wx, wy + 0.06, wz + St["koniec"]), (sz, 0.12, 0.8), "FFFFFF", "SmoothPlastic", "Block", (0, 0, 0), 0.3)
    for strona in (-1, 1):
        czesc(L, "Teren2", "Plot", (wx + strona * (sz / 2 + 1), wy + 1.2, wz + dl / 2 - 6), (1, 2.4, dl + 30), "8A5A32", "Wood")
    czesc(L, "Teren2", "PlotKoniec", (wx, wy + 1.2, wz + dl - 4), (sz + 2, 2.4, 1), "8A5A32", "Wood")
    for i, (px, pz) in enumerate(W["zagrodyPoz"]):
        x, z = wx + px, wz + pz
        sw, gl = W["zagroda_szer"] - 1.4, W["zagroda_gl"]
        czesc(L, "Teren2", "Zagroda%d" % (i + 1), (x, wy + 0.15, z), (sw, 0.3, gl), ["FFD9D9", "D9ECFF", "DDF7DD", "FFEBCF", "EBDDFF", "FFDDF0", "D6FAF6", "F7F7D2"][i],
              "WoodPlanks")
        for bx in (-sw / 2, sw / 2):
            czesc(L, "Teren2", "Plotek", (x + bx, wy + 1.1, z), (0.5, 2.2, gl), "A86A3A", "Wood")
        czesc(L, "Teren2", "Plotek", (x, wy + 1.1, z - gl / 2), (sw, 2.2, 0.5), "A86A3A", "Wood")
        czesc(L, "Teren2", "Podest", (x, wy + 0.5, z + gl / 2 - 1.5), (3, 1, 3), "C99A6B", "Wood")
    czesc(L, "Teren2", "Zywoplot", (wx, wy + 2.5, wz - W["zagroda_gl"] - 2), (sz + 60, 5, 3), "4E9A3C", "Grass")
    return L


def tablice(D):
    W = D["wabik"]
    wx, wy, wz = W["srodek"]
    t = []
    for St in W["strefy"]:
        z = wz + (St["od"] + St["koniec"]) / 2
        t.append({"tekst": St["nazwa"], "poz": [wx - W["laka_szer"] / 2 - 3, wy + 6, z], "patrz": [wx, wy + 6, wz - 50], "szer": 12, "wys": 4})
    return t


LUAU = r'''
local HS = game:GetService("HttpService")
local RS = game:GetService("ReplicatedStorage")
if game.PlaceId == __BC__ then
	return "STOP: to miejsce gry B&C — zabawki budują się tylko w innym miejscu"
end
local K = "__KONTENER__"
local zr = HS:JSONDecode(__ZRODLA__)
local stary = workspace:FindFirstChild(K)
if stary and not stary:GetAttribute("Wygenerowane") then
	return "STOP: w Workspace jest obcy obiekt " .. K .. " (bez atrybutu Wygenerowane) — nie ruszam"
end
local tylkoSkrypty = __TYLKO__
if tylkoSkrypty then
	if not stary then
		return "STOP: brak kontenera — najpierw pełna budowa"
	end
	for n, t in zr do
		local s = stary:FindFirstChild(n, true)
		if s then
			s.Source = t
		end
	end
	return "skrypty zaktualizowane"
end
-- wzorce potworów z Pet Areny (kopia)
local zrodloWz = (workspace:FindFirstChild("PetArenaGra") and workspace.PetArenaGra:FindFirstChild("Wzorce")) or RS:FindFirstChild("PetArenaWzorce")
if not zrodloWz then
	return "STOP: brak wzorców potworów (Workspace/PetArenaGra/Wzorce) — zbuduj Pet Arenę"
end
local wlaczone = if stary then stary:GetAttribute("ZabawkiWlaczone") else nil
if stary then
	stary:Destroy()
end
local k = Instance.new("Folder")
k.Name = K
k:SetAttribute("Wygenerowane", true)
k:SetAttribute("Zbudowano", "__CZAS__")
local mod = Instance.new("Folder")
mod.Name = "Moduly"
mod.Parent = k
for _, n in { "DaneZabawek", "LogikaZabawek", "EfektyZabawek" } do
	local m = Instance.new("ModuleScript")
	m.Name = n
	m.Source = zr[n]
	m.Parent = mod
end
local syg = Instance.new("Folder")
syg.Name = "Sygnaly"
syg.Parent = k
for _, n in { "Akcja", "Zdarzenia" } do
	local e = Instance.new("RemoteEvent")
	e.Name = n
	e.Parent = syg
end
for _, n in { "Stan1", "Stan2" } do
	local e = Instance.new("UnreliableRemoteEvent")
	e.Name = n
	e.Parent = syg
end
local bf = Instance.new("BindableFunction")
bf.Name = "SterowanieSerwera"
bf.Parent = syg
local wz = Instance.new("Folder")
wz.Name = "Wzorce"
wz.Parent = k
local ileWz = 0
for _, m in zrodloWz:GetChildren() do
	if string.sub(m.Name, 1, 4) == "Pet_" then
		m:Clone().Parent = wz
		ileWz += 1
	end
end
-- tereny
local sc = Instance.new("Folder")
sc.Name = "Scena"
sc.Parent = k
local grupy = {}
for _, c in HS:JSONDecode(__SCENA__) do
	local g = grupy[c.g]
	if not g then
		g = Instance.new("Model")
		g.Name = c.g
		g.Parent = sc
		grupy[c.g] = g
	end
	local p = Instance.new("Part")
	p.Name = c.n
	p.Anchored = true
	p.Shape = Enum.PartType[c.k]
	p.Size = Vector3.new(c.s[1], c.s[2], c.s[3])
	p.CFrame = CFrame.new(c.p[1], c.p[2], c.p[3]) * CFrame.Angles(c.r[1], c.r[2], c.r[3])
	p.Color = Color3.fromHex(c.c)
	p.Material = Enum.Material[c.m]
	p.Transparency = c.t
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = g
end
for _, T in HS:JSONDecode(__TABLICE__) do
	local p = Instance.new("Part")
	p.Name = "Tablica"
	p.Anchored = true
	p.CanCollide = false
	p.Size = Vector3.new(T.szer, T.wys, 0.4)
	p.CFrame = CFrame.lookAt(Vector3.new(T.poz[1], T.poz[2], T.poz[3]), Vector3.new(T.patrz[1], T.patrz[2], T.patrz[3]))
	p.Color = Color3.fromHex("2A1A3A")
	p.Parent = grupy.Teren2 or sc
	local sg = Instance.new("SurfaceGui")
	sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 30
	sg.LightInfluence = 0
	sg.Parent = p
	local l = Instance.new("TextLabel")
	l.BackgroundTransparency = 1
	l.Size = UDim2.fromScale(1, 1)
	l.Text = T.tekst
	l.TextScaled = true
	l.Font = Enum.Font.LuckiestGuy
	l.TextColor3 = Color3.fromHex("FFC83D")
	l.Parent = sg
end
for _, s in { { "SerwerZabawek", Enum.RunContext.Server }, { "KlientZabawek", Enum.RunContext.Client } } do
	local sk = Instance.new("Script")
	sk.Name = s[1]
	sk.RunContext = s[2]
	sk.Source = zr[s[1]]
	sk.Enabled = wlaczone ~= false
	sk.Parent = k
end
k:SetAttribute("ZabawkiWlaczone", wlaczone ~= false)
k.Parent = workspace
local czesci = 0
for _, d in sc:GetDescendants() do
	if d:IsA("BasePart") then
		czesci += 1
	end
end
return string.format("zbudowano: %d części sceny, %d wzorców, %d modułów", czesci, ileWz, #mod:GetChildren())
'''


WLACZNIK = "ZabawkiWlaczone"
# --wlacz on|off (22.11.2026, dodane przy Monster Evolution, żeby zabawki nie działały w cudzych próbach Play):
# atrybut ZabawkiWlaczone kontenera + Enabled obu skryptów; źródła skryptów bez zmian. Pełna budowa zachowuje stan.
LUAU_WLACZ = r'''
if game:GetService("RunService"):IsRunning() then
	return "STOP: Studio jest w trybie Play"
end
local k = workspace:FindFirstChild("__KONTENER__")
if not k or k:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak własnego kontenera __KONTENER__"
end
local CH = game:GetService("ChangeHistoryService")
CH:SetWaypoint("__KONTENER__: przed __WLACZNIK__")
k:SetAttribute("__WLACZNIK__", __WARTOSC__)
local n = 0
for _, nazwa in { "SerwerZabawek", "KlientZabawek" } do
	local s = k:FindFirstChild(nazwa)
	if s and s:IsA("BaseScript") then
		s.Enabled = __WARTOSC__
		n += 1
	end
end
CH:SetWaypoint("__KONTENER__: __WLACZNIK__ = " .. tostring(__WARTOSC__))
return string.format("__WLACZNIK__ = %s (skryptów: %d)", tostring(k:GetAttribute("__WLACZNIK__")), n)
'''


def luau_str(t):
    """Napis jako literał Luau (długi nawias, bez ucieczek)."""
    n = 1
    while ("]" + "=" * n + "]") in t:
        n += 1
    return "[" + "=" * n + "[" + t + "]" + "=" * n + "]"


def main():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--sucho", action="store_true")
    ap.add_argument("--skrypty", action="store_true")
    ap.add_argument("--studio", default=None)
    ap.add_argument("--wlacz", choices=["on", "off"], help="wyłącznik ZabawkiWlaczone (atrybut + Enabled skryptów)")
    a = ap.parse_args()
    if a.wlacz:
        from studio_mcp import StudioMCP
        if not a.studio:
            raise SystemExit("podaj --studio <id>")
        kod = (LUAU_WLACZ.replace("__KONTENER__", "ZabawkiGra").replace("__WLACZNIK__", WLACZNIK)
               .replace("__WARTOSC__", "true" if a.wlacz == "on" else "false"))
        with StudioMCP(timeout=120) as s:
            if "Current Studio Mode: Edit" not in s.call("get_studio_state", {"studio_id": a.studio})["text"]:
                log("PRZERWANO — Studio nie jest w trybie Edit")
                return 1
            r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": a.studio})
            t = (r["text"] or "").strip()
            log(t[:300])
            return 1 if r["is_error"] or t.startswith("STOP") else 0
    DN.main()
    D = DN.dane()
    zr = zrodla()
    sc = scena(D)
    log("źródła: %s (%d kB); scena: %d części; bez strażnika Studio" % (", ".join(zr), sum(len(t.encode("utf-8")) for t in zr.values()) // 1000, len(sc)))
    if a.sucho:
        return 0
    from studio_mcp import StudioMCP
    kod = (LUAU.replace("__BC__", str(D["miejsceBC"])).replace("__KONTENER__", D["kontener"]).replace("__CZAS__", time.strftime("%Y-%m-%d %H:%M"))
           .replace("__TYLKO__", "true" if a.skrypty else "false").replace("__ZRODLA__", luau_str(json.dumps(zr, ensure_ascii=False)))
           .replace("__SCENA__", luau_str(json.dumps(sc))).replace("__TABLICE__", luau_str(json.dumps(tablice(D)))))
    with StudioMCP(timeout=240) as s:
        sid = a.studio
        if not sid:
            raise SystemExit("podaj --studio <id>")
        if "Current Studio Mode: Edit" not in s.call("get_studio_state", {"studio_id": sid})["text"]:
            log("PRZERWANO — Studio nie jest w trybie Edit")
            return 1
        r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
        t = (r["text"] or "").strip()
        log(t[:600])
        return 1 if r["is_error"] or t.startswith("STOP") else 0


if __name__ == "__main__":
    sys.exit(main())
