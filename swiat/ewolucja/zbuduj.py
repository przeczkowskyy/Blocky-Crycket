#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Budowa Monster Evolution w Studio: Workspace/EwolucjaGra (moduły, skrypty, sygnały, wzorce 8 form, pole).

    python -B swiat/ewolucja/zbuduj.py --sucho                 # bez Studio: dane, kontrola Luau, plan
    python -B swiat/ewolucja/zbuduj.py --studio <id>           # pełna budowa (strażnik „tylko Studio” w skryptach)
    python -B swiat/ewolucja/zbuduj.py --skrypty --studio <id> # tylko moduły i skrypty (scena i wzorce zostają)
    python -B swiat/ewolucja/zbuduj.py --publikacja ...        # skrypty BEZ strażnika Studio (prywatna wersja testowa)
    python -B swiat/ewolucja/zbuduj.py --wlacz on|off ...      # wyłącznik EwolucjaWlaczona (atrybut kontenera)
    python -B swiat/ewolucja/zbuduj.py --stan | --usun ...     # odczyt / usunięcie własnego kontenera

Zasady: odmowa w miejscu gry B&C, poza trybem Edit i przy obcym obiekcie EwolucjaGra (bez atrybutu Wygenerowane);
punkt historii przed i po każdej zmianie; niczego nie zapisuje ani nie publikuje; Lighting bez zmian. Wzorce potworów
kopiuje z Workspace/PetArenaGra/Wzorce (tylko 8 modeli drabiny) do własnego kontenera; serwer w czasie gry przenosi je
do ReplicatedStorage/EwolucjaWzorce.
"""
import argparse
import importlib.util
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
MODULY = ["DaneEwolucji", "LogikaEwolucji", "EfektyEwolucji"]
SKRYPTY = [("SerwerEwolucji", "SerwerEwolucji.server.luau", "Server"), ("KlientEwolucji", "KlientEwolucji.client.luau", "Client")]


def log(*a):
    print("Ewolucja |", *a, flush=True)


def bez_straznika(tekst):
    """--publikacja: usuwa blok strażnika Studio (`if not …IsStudio() then` … `end` w kolumnie 0)."""
    i = tekst.find(DN.STRAZNIK)
    if i < 0:
        raise ValueError("brak strażnika Studio")
    k = tekst.find("\nend\n", i)
    if k < 0:
        raise ValueError("strażnik bez `end` w kolumnie 0")
    return tekst[:i] + "-- (publikacja: bez strażnika Studio)\n" + tekst[k + 5:]


def zrodla(publikacja=False):
    w = {}
    for n in MODULY:
        w[n] = open(os.path.join(ZR, n + ".luau"), encoding="utf-8").read().replace("\r\n", "\n")
    for n, plik, _ in SKRYPTY:
        t = open(os.path.join(ZR, plik), encoding="utf-8").read().replace("\r\n", "\n")
        if DN.STRAZNIK not in t:
            raise SystemExit("BŁĄD: %s bez strażnika Studio" % plik)
        w[n] = bez_straznika(t) if publikacja else t
    return w


def kontrola_luau():
    spec = importlib.util.spec_from_file_location("kontrola_luau_potworow", os.path.join(REPO, "swiat", "las_potwory", "sprawdz_luau.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # skrypty: wszystkie reguły (bilans, strażnik Studio, zakazane konstrukcje); moduły: bez strażnika (czyste rachunki
    # uruchamiane też w testach bez Studio; działają tylko, gdy wymaga ich skrypt ze strażnikiem)
    bledy = mod.sprawdz_pliki([os.path.join(ZR, p) for _, p, _ in SKRYPTY], wypisz=lambda t: None)
    for n in MODULY:
        s = os.path.join(ZR, n + ".luau")
        t = mod.wczytaj(s)
        nazwa = os.path.relpath(s, REPO).replace("\\", "/")
        bez_kom, bez_kom_nap = mod.rozbierz(t)
        bledy += mod.sprawdz_tekst(t, nazwa, pelne=False) + mod.zakazane(bez_kom, bez_kom_nap, nazwa)
    return bledy


def czesc(lista, grupa, nazwa, poz, roz, kolor, mat="SmoothPlastic", ksztalt="Block", obrot=(0, 0, 0), przez=0, kol=False):
    lista.append({"g": grupa, "n": nazwa, "p": [round(x, 3) for x in poz], "s": [round(x, 3) for x in roz], "c": kolor, "m": mat,
                  "k": ksztalt, "r": [round(x, 4) for x in obrot], "t": przez, "kol": kol})


def drzewo(L, cx, cy, cz, x, z, h, nazwa):
    pien = max(1.6, h * 0.11)
    czesc(L, "Drzewa", nazwa, (cx + x, cy + h * 0.4, cz + z), (h * 0.8, pien, pien), "7A5232", "Wood", "Cylinder", (0, 0, math.pi / 2))
    for i, (dx, dy, dz, s, k) in enumerate([(0, 0.82, 0, 0.62, "4E9A3C"), (0.18, 0.7, 0.12, 0.45, "5DB047"), (-0.16, 0.68, -0.1, 0.42, "3F8A33")]):
        czesc(L, "Drzewa", nazwa + "Korona", (cx + x + dx * h, cy + dy * h, cz + z + dz * h), (s * h, s * h * 0.85, s * h), k, "LeafyGrass", "Ball")


def scena(D):
    P = D["pole"]
    cx, cy, cz = P["srodek"]
    R = P["r"]
    W = DN.wystroj(P)
    L = []
    czesc(L, "Teren", "Pole", (cx, cy - 2, cz), (4, 2 * R + 20, 2 * R + 20), "8FD46B", "Grass", "Cylinder", (0, 0, math.pi / 2))
    czesc(L, "Teren", "Okolica", (cx, cy - 2.2, cz), (4, 2 * R + 140, 2 * R + 140), "6FB04F", "Grass", "Cylinder", (0, 0, math.pi / 2))
    for i, p in enumerate(W["plamy"]):
        czesc(L, "Teren", "Plama", (cx + p["x"], cy + 0.02 + i * 0.002, cz + p["z"]), (0.12, p["r"] * 2, p["r"] * 2), p["c"], p["m"], "Cylinder",
              (0, 0, math.pi / 2))
    # ścieżka z piasku przez środek (punkt orientacyjny)
    for i in range(9):
        a = -0.9 + i * 0.22
        czesc(L, "Teren", "Sciezka", (cx + math.sin(a) * 60 * (i - 4) / 4, cy + 0.06, cz + (i - 4) * 30), (0.1, 9, 9), "E6D3A0", "Sand", "Cylinder",
              (0, 0, math.pi / 2))
    n = 56
    for i in range(n):
        a = 2 * math.pi * i / n
        r = R + 1.5
        czesc(L, "Mur", "Mur", (cx + math.sin(a) * r, cy + P["mur_y"] / 2, cz + math.cos(a) * r), (2 * math.pi * r / n + 0.6, P["mur_y"], 2.6),
              ["F2C36B", "E8A85A"][i % 2], "Slate", "Block", (0, a, 0), 0, True)
    for i, s in enumerate(D["przeszkody"]):
        if s["typ"] == "skala":
            czesc(L, "Skaly", "Skala", (cx + s["x"], cy + 2.5, cz + s["z"]), (6, s["r"] * 2, s["r"] * 2), ["9C8C7A", "8A7C6C", "A89A86"][i % 3],
                  "Slate", "Cylinder", (0, 0, math.pi / 2), 0, True)
            czesc(L, "Skaly", "SkalaCzubek", (cx + s["x"], cy + 5.6, cz + s["z"]), (s["r"] * 1.5, 4, s["r"] * 1.5), "B5A792", "Rock", "Ball")
            czesc(L, "Skaly", "SkalaMala", (cx + s["x"] + s["r"] * 0.9, cy + 1.2, cz + s["z"] - s["r"] * 0.5), (s["r"] * 0.7, s["r"] * 0.5, s["r"] * 0.7),
                  "8A7C6C", "Rock", "Ball")
        else:
            drzewo(L, cx, cy, cz, s["x"], s["z"], s["h"], "DrzewoPole")
    for d in W["drzewa"]:
        drzewo(L, cx, cy, cz, d["x"], d["z"], d["h"], "DrzewoZa")
    # trzy menhiry za murem (orientacja) i staw
    for i in range(3):
        a = 2 * math.pi * i / 3 + 0.5
        r = R + 10
        czesc(L, "Znaki", "Menhir", (cx + math.sin(a) * r, cy + 7, cz + math.cos(a) * r), (4, 14, 3), "7C7486", "Slate", "Block", (0, a, 0.08))
    czesc(L, "Znaki", "Staw", (cx - R - 34, cy + 0.05, cz + 30), (0.12, 34, 34), "5FB8E8", "Glass", "Cylinder", (0, 0, math.pi / 2), 0.2)
    for i, (x, z) in enumerate(W["kwiaty"]):
        czesc(L, "Kwiaty", "Kwiat", (cx + x, cy + 0.08, cz + z), (0.1, 1.6, 1.6), ["FFF07A", "FF9AD8", "FFFFFF", "C8A8FF"][i % 4], "SmoothPlastic",
              "Cylinder", (0, 0, math.pi / 2))
    return L


WSTEP = r'''
local HS = game:GetService("HttpService")
if game.PlaceId == __BC__ then
	return "STOP: to miejsce gry B&C — Monster Evolution buduje się tylko w innym miejscu"
end
if game:GetService("RunService"):IsRunning() then
	return "STOP: Studio jest w trybie Play"
end
local K = "__KONTENER__"
local CH = game:GetService("ChangeHistoryService")
local stary = workspace:FindFirstChild(K)
if stary and stary:GetAttribute("Wygenerowane") ~= true then
	return "STOP: w Workspace jest obcy obiekt " .. K .. " (bez atrybutu Wygenerowane) — nie ruszam"
end
'''

BUDOWA = WSTEP + r'''
local zr = HS:JSONDecode(__ZRODLA__)
local tylkoSkrypty = __TYLKO__
CH:SetWaypoint(K .. ": przed budową")
local wlaczona = if stary then stary:GetAttribute("__WYLACZNIK__") else nil
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
	stary:SetAttribute("Zbudowano", "__CZAS__")
	stary:SetAttribute("Publikacja", __PUBLIKACJA__)
	CH:SetWaypoint(K .. ": skrypty")
	return "skrypty zaktualizowane"
end
local zrodloWz = workspace:FindFirstChild("PetArenaGra") and workspace.PetArenaGra:FindFirstChild("Wzorce")
if not zrodloWz then
	return "STOP: brak wzorców potworów (Workspace/PetArenaGra/Wzorce)"
end
local potrzebne = HS:JSONDecode(__WZORCE__)
for _, n in potrzebne do
	if not zrodloWz:FindFirstChild(n) then
		return "STOP: brak wzorca " .. n
	end
end
if stary then
	stary:Destroy()
end
local k = Instance.new("Folder")
k.Name = K
k:SetAttribute("Wygenerowane", true)
k:SetAttribute("Zrodlo", "swiat/ewolucja")
k:SetAttribute("Zbudowano", "__CZAS__")
k:SetAttribute("Publikacja", __PUBLIKACJA__)
k:SetAttribute("__WYLACZNIK__", if wlaczona == nil then true else wlaczona)
local mod = Instance.new("Folder")
mod.Name = "Moduly"
mod.Parent = k
for _, n in { "DaneEwolucji", "LogikaEwolucji", "EfektyEwolucji" } do
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
local st = Instance.new("UnreliableRemoteEvent")
st.Name = "Stan"
st.Parent = syg
local bf = Instance.new("BindableFunction")
bf.Name = "SterowanieSerwera"
bf.Parent = syg
local wz = Instance.new("Folder")
wz.Name = "Wzorce"
wz.Parent = k
for _, n in potrzebne do
	local m = zrodloWz:FindFirstChild(n):Clone()
	m:PivotTo(CFrame.new(0, -200, 0))
	m.Parent = wz
end
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
	p.CanCollide = c.kol
	p.CanTouch = false
	p.CanQuery = c.kol
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
for _, s in { { "SerwerEwolucji", Enum.RunContext.Server }, { "KlientEwolucji", Enum.RunContext.Client } } do
	local sk = Instance.new("Script")
	sk.Name = s[1]
	sk.RunContext = s[2]
	sk.Source = zr[s[1]]
	sk.Parent = k
end
k.Parent = workspace
CH:SetWaypoint(K .. ": zbudowano")
local czesci = 0
for _, d in sc:GetDescendants() do
	if d:IsA("BasePart") then
		czesci += 1
	end
end
return string.format("zbudowano: %d części sceny, %d wzorców, %d modułów", czesci, #wz:GetChildren(), #mod:GetChildren())
'''

WLACZ = WSTEP + r'''
if not stary then
	return "STOP: brak kontenera — najpierw zbuduj"
end
CH:SetWaypoint(K .. ": przed __WYLACZNIK__")
stary:SetAttribute("__WYLACZNIK__", __WARTOSC__)
CH:SetWaypoint(K .. ": __WYLACZNIK__ = " .. tostring(__WARTOSC__))
return "__WYLACZNIK__ = " .. tostring(stary:GetAttribute("__WYLACZNIK__"))
'''

USUN = WSTEP + r'''
if not stary then
	return "nie ma czego usuwać"
end
CH:SetWaypoint(K .. ": przed usunięciem")
stary:Destroy()
CH:SetWaypoint(K .. ": usunięto")
return "USUNIĘTO Workspace/" .. K
'''

STAN = r'''
local HS = game:GetService("HttpService")
local k = workspace:FindFirstChild("__KONTENER__")
if not k or k:GetAttribute("Wygenerowane") ~= true then
	return HS:JSONEncode({ jest = false })
end
local w = { jest = true, atrybuty = k:GetAttributes(), zrodla = {}, wzorce = {}, czesci = 0 }
for _, d in k:GetDescendants() do
	if d:IsA("LuaSourceContainer") then
		w.zrodla[d.Name] = { bajtow = #d.Source, straznik = string.find(d.Source, "IsStudio()", 1, true) ~= nil }
	elseif d:IsA("BasePart") and d:IsDescendantOf(k.Scena) then
		w.czesci += 1
	end
end
for _, m in k.Wzorce:GetChildren() do
	table.insert(w.wzorce, m.Name)
end
return HS:JSONEncode(w)
'''


def luau_str(t):
    n = 1
    while ("]" + "=" * n + "]") in t:
        n += 1
    return "[" + "=" * n + "[" + t + "]" + "=" * n + "]"


def wstaw(szablon, **w):
    for k, v in w.items():
        szablon = szablon.replace("__%s__" % k, v)
    return szablon


def main():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--sucho", action="store_true")
    ap.add_argument("--skrypty", action="store_true")
    ap.add_argument("--stan", action="store_true")
    ap.add_argument("--usun", action="store_true")
    ap.add_argument("--wlacz", choices=["on", "off"])
    ap.add_argument("--publikacja", action="store_true")
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    DN.main()
    D = DN.dane()
    zr = zrodla(a.publikacja)
    bledy = kontrola_luau()
    for b in bledy:
        log("BŁĄD Luau:", b)
    sc = scena(D)
    wzorce = sorted({f["wzorzec"] for f in D["formy"]})
    log("źródła: %s (%d kB); scena: %d części; wzorce: %d; %s" % (
        ", ".join(zr), sum(len(t.encode("utf-8")) for t in zr.values()) // 1000, len(sc), len(wzorce),
        "PUBLIKACJA: bez strażnika Studio" if a.publikacja else "ze strażnikiem Studio (tylko w Studio)"))
    if bledy:
        return 1
    if a.sucho:
        return 0
    if not a.studio:
        raise SystemExit("podaj --studio <id>")
    from studio_mcp import StudioMCP
    wsp = dict(BC=str(D["miejsceBC"]), KONTENER=D["kontener"], WYLACZNIK=D["wylacznik"])
    with StudioMCP(timeout=240) as s:
        if "Current Studio Mode: Edit" not in s.call("get_studio_state", {"studio_id": a.studio})["text"]:
            log("PRZERWANO — Studio nie jest w trybie Edit; nic nie zmieniono")
            return 1

        def wykonaj(kod, opis):
            r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": a.studio}, timeout=240)
            t = (r["text"] or "").strip()
            if r["is_error"] or t.startswith("STOP"):
                log("PRZERWANO (%s): %s" % (opis, t[:600]))
                raise SystemExit(1)
            return t

        if a.stan:
            print(json.dumps(json.loads(wykonaj(wstaw(STAN, KONTENER=D["kontener"]), "stan")), ensure_ascii=False, indent=1))
            return 0
        if a.usun:
            log(wykonaj(wstaw(USUN, **wsp), "usuwanie"))
            return 0
        if a.wlacz:
            log(wykonaj(wstaw(WLACZ, WARTOSC="true" if a.wlacz == "on" else "false", **wsp), "wyłącznik"))
            return 0
        kod = wstaw(BUDOWA, CZAS=time.strftime("%Y-%m-%d %H:%M"), TYLKO="true" if a.skrypty else "false",
                    PUBLIKACJA="true" if a.publikacja else "false", WZORCE=luau_str(json.dumps(wzorce)),
                    ZRODLA=luau_str(json.dumps(zr, ensure_ascii=False)), SCENA=luau_str(json.dumps(sc)), **wsp)
        log(wykonaj(kod, "budowa"))
        st = json.loads(wykonaj(wstaw(STAN, KONTENER=D["kontener"]), "stan"))
        zle = [n for n, t in zr.items() if (st["zrodla"].get(n) or {}).get("bajtow") != len(t.encode("utf-8"))]
        log("sprawdzenie: %s; wyłącznik %s = %s; publikacja %s" % ("źródła zgodne" if not zle else "NIEZGODNE: " + ", ".join(zle),
                                                                 D["wylacznik"], st["atrybuty"].get(D["wylacznik"]), st["atrybuty"].get("Publikacja")))
        return 1 if zle else 0


if __name__ == "__main__":
    sys.exit(main())
