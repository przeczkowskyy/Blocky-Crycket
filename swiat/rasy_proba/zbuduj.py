#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wystawa ras w Roblox Studio (D-104, etap B; propozycja): figury sześciu ras i człowieka z części Roblox.

    python -B swiat/rasy_proba/zbuduj.py            # zbuduj od nowa własny kontener Workspace/RasyProba
    python -B swiat/rasy_proba/zbuduj.py --sucho    # tylko policz i sprawdź źródła, bez Studio
    python -B swiat/rasy_proba/zbuduj.py --usun     # usuń własny kontener (cudzy obiekt o tej nazwie zostaje)
    python -B swiat/rasy_proba/zbuduj.py --stan     # odczyt: co stoi w kontenerze (niczego nie zmienia)

Co robi w Studio (tylko tryb Edit, tylko miejsce gry — numer miejsca bierze z swiat/test_walki_roblox/cel_studio.py):
  1. sprawdza, że miejsca figur są wolne (pudło nad ziemią bez cudzych części) — inaczej STOP, nic nie zmienia;
  2. punkt historii, własny kontener Workspace/RasyProba (atrybut Wygenerowane) budowany od nowa;
  3. każda figura = Model: zakotwiczony HumanoidRootPart, niewidzialna część na kość R15, stawy Motor6D, bryły
     przyspawane do kości (bez kolizji, bez dotyku, bez promieni), AnimationController z Animatorem, tabliczka
     z nazwą rasy nad głową (BillboardGui); skala rasy jest w geometrii figury (rasy.w_skali), stopy na ziemi;
  4. skrypt SpoczynekRas (zrodla/SpoczynekRas.server.luau, strażnik IsStudio) — oddech figur w Play;
  5. punkt historii. Niczego nie zapisuje ani nie publikuje, nie rusza Lighting ani cudzych instancji.
Bez wgrywania: części, kolory i materiały Roblox (świecące oczy i aureola = materiał Neon).
"""
import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (REPO, os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
    if _s not in sys.path:
        sys.path.append(_s)
if TU in sys.path:
    sys.path.remove(TU)
sys.path.insert(0, TU)                                 # własne moduły pakietu zawsze pierwsze (dane, zbuduj)
import dane as DN  # noqa: E402

ZRODLA = os.path.join(TU, "zrodla")
SKRYPT_PLIK = os.path.join(ZRODLA, "SpoczynekRas.server.luau")

# wspólny początek każdego kodu wysyłanego do Studio: właściwe miejsce, tryb Edit, tylko własny kontener
WSTEP = r'''
if game.PlaceId ~= __MIEJSCE__ then
	return "STOP: to nie jest miejsce gry — nic nie zmieniono"
end
if game:GetService("RunService"):IsRunning() then
	return "STOP: Studio nie jest w trybie Edit — nic nie zmieniono"
end
local KONTENER = "__KONTENER__"
local function kontenery()
	local nasze, obce = {}, {}
	for _, d in workspace:GetChildren() do
		if d.Name == KONTENER then
			table.insert(if d:GetAttribute("Wygenerowane") == true then nasze else obce, d)
		end
	end
	return nasze, obce
end
local function kontener()
	local nasze, obce = kontenery()
	if #obce > 0 then
		return nil, string.format("STOP: w Workspace jest %d obiekt(ów) '%s' bez atrybutu Wygenerowane — nie ruszam cudzej pracy", #obce, KONTENER)
	end
	if #nasze > 1 then
		return nil, string.format("STOP: w Workspace są %d kontenery '%s' — usuń je (--usun) i zbuduj od nowa", #nasze, KONTENER)
	end
	return nasze[1], nil
end
'''

START = WSTEP + r'''
local D = __DANE__
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
-- wolne miejsce: nad ziemią w pudle każdej figury nie może być cudzej części
local params = RaycastParams.new()
params.FilterType = Enum.RaycastFilterType.Exclude
params.FilterDescendantsInstances = if kont then { kont } else {}
local op = OverlapParams.new()
op.FilterType = Enum.RaycastFilterType.Exclude
op.FilterDescendantsInstances = if kont then { kont } else {}
local zajete = {}
for _, f in D.figury do
	local traf = workspace:Raycast(Vector3.new(f.poz[1], 200, f.poz[2]), Vector3.new(0, -400, 0), params)
	if not traf then
		table.insert(zajete, f.id .. ": brak podłoża")
	else
		local y = traf.Position.Y + D.nad + D.pudlo[2] / 2
		for _, p in workspace:GetPartBoundsInBox(CFrame.new(f.poz[1], y, f.poz[2]), Vector3.new(D.pudlo[1], D.pudlo[2], D.pudlo[3]), op) do
			if not p:IsA("Terrain") then
				table.insert(zajete, f.id .. ": " .. p:GetFullName())
			end
		end
	end
end
if #zajete > 0 then
	return "STOP: miejsce wystawy jest zajęte — nic nie zmieniono: " .. table.concat(zajete, "; ", 1, math.min(#zajete, 6))
end
local CH = game:GetService("ChangeHistoryService")
CH:SetWaypoint("RasyProba: przed budową")
if kont then
	kont:Destroy()
end
kont = Instance.new("Folder")
kont.Name = KONTENER
kont:SetAttribute("Wygenerowane", true)
kont:SetAttribute("Zrodlo", "__ZRODLO__")
kont:SetAttribute("Zbudowano", "__CZAS__")
kont:SetAttribute("Figur", #D.figury)
kont:SetAttribute("SpoczynekGra", 0)
kont.Parent = workspace
return "kontener gotowy, miejsca wolne: " .. #D.figury
'''

FIGURA = WSTEP + r'''
local D = __DANE__
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
if not kont then
	return "STOP: brak kontenera Workspace/" .. KONTENER
end
local stary = kont:FindFirstChild(D.id)
if stary then
	stary:Destroy()
end
local params = RaycastParams.new()
params.FilterType = Enum.RaycastFilterType.Exclude
params.FilterDescendantsInstances = { kont }
local traf = workspace:Raycast(Vector3.new(D.poz[1], 200, D.poz[2]), Vector3.new(0, -400, 0), params)
if not traf then
	return "STOP: brak podłoża pod figurą " .. D.id
end
local y = traf.Position.Y
local pos = Vector3.new(D.poz[1], y, D.poz[2])
local baza = CFrame.lookAt(pos, Vector3.new(D.patrz[1], y, D.patrz[2]))

local model = Instance.new("Model")
model.Name = D.id
model:SetAttribute("Wygenerowane", true)
model:SetAttribute("Nazwa", D.nazwa)
model:SetAttribute("Skala", D.skala)
model:SetAttribute("Wzrost", D.wzrost)
model:SetAttribute("Bryl", #D.czesci)
model:SetAttribute("Ziemia", y)

local function bezFizyki(p)
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.Massless = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
end

local hrpPos = Vector3.new(D.hrp[1], D.hrp[2], D.hrp[3])
local hrp = Instance.new("Part")
hrp.Name = "HumanoidRootPart"
hrp.Size = Vector3.new(2, 2, 1)
hrp.Transparency = 1
hrp.Anchored = true
bezFizyki(hrp)
hrp.CFrame = baza * CFrame.new(hrpPos)
hrp.Parent = model
model.PrimaryPart = hrp

local kosci = {}
for i, k in D.kosci do
	local p = Instance.new("Part")
	p.Name = k[1]
	p.Size = Vector3.new(k[9], k[10], k[11])
	p.Transparency = 1
	p.Anchored = false
	p.CastShadow = false
	bezFizyki(p)
	p.CFrame = baza * CFrame.new(k[6], k[7], k[8])
	p.Parent = model
	kosci[i] = p
end
for i, k in D.kosci do
	local rodzic, srodekRodzica
	if k[2] == 0 then
		rodzic, srodekRodzica = hrp, hrpPos
	else
		local kr = D.kosci[k[2]]
		rodzic, srodekRodzica = kosci[k[2]], Vector3.new(kr[6], kr[7], kr[8])
	end
	local staw = Vector3.new(k[3], k[4], k[5])
	local m = Instance.new("Motor6D")
	m.Name = k[12]
	m.C0 = CFrame.new(staw - srodekRodzica)
	m.C1 = CFrame.new(staw - Vector3.new(k[6], k[7], k[8]))
	m.Part0 = rodzic
	m.Part1 = kosci[i]
	m.Parent = kosci[i]
end
local n, neon = 0, 0
for _, c in D.czesci do
	local ks = c[2]
	local p
	if ks == 3 then
		p = Instance.new("WedgePart")
	elseif ks == 4 then
		p = Instance.new("CornerWedgePart")
	else
		p = Instance.new("Part")
		p.Shape = if ks == 1 then Enum.PartType.Ball elseif ks == 2 then Enum.PartType.Cylinder else Enum.PartType.Block
	end
	p.Name = c[3]
	p.Size = Vector3.new(c[10], c[11], c[12])
	p.CFrame = baza * CFrame.new(c[4], c[5], c[6]) * CFrame.fromOrientation(c[7], c[8], c[9])
	p.Color = Color3.fromHex(c[13])
	local mat = D.materialy[c[14] + 1]
	p.Material = Enum.Material[mat[1]]
	p.Reflectance = mat[2]
	if mat[1] == "Neon" then
		neon += 1
	end
	p.Anchored = false
	bezFizyki(p)
	if c[16] ~= "" then
		local sm = Instance.new("SpecialMesh")
		sm.MeshType = Enum.MeshType[c[16]]
		sm.Parent = p
	end
	local kosc = kosci[c[1]]
	local w = Instance.new("WeldConstraint")
	w.Part0 = kosc
	w.Part1 = p
	w.Parent = p
	p.Parent = kosc
	n += 1
end
local ac = Instance.new("AnimationController")
ac.Parent = model
local an = Instance.new("Animator")
an.Parent = ac
model.Parent = kont

-- tabliczka z nazwą rasy nad najwyższym punktem figury
local cf, rozmiar = model:GetBoundingBox()
local szczyt = cf.Position.Y + rozmiar.Y / 2
local t = Instance.new("Part")
t.Name = "Tabliczka"
t.Size = Vector3.new(0.2, 0.2, 0.2)
t.Transparency = 1
t.Anchored = true
bezFizyki(t)
t.CFrame = CFrame.new(pos.X, szczyt + D.tabliczka.nad_szczytem, pos.Z)
local bg = Instance.new("BillboardGui")
bg.Name = "Nazwa"
bg.Size = UDim2.fromScale(D.tabliczka.szer, D.tabliczka.wys)
bg.MaxDistance = D.tabliczka.zasieg
bg.LightInfluence = 0
bg.Adornee = t
local tl = Instance.new("TextLabel")
tl.Name = "Napis"
tl.Size = UDim2.fromScale(1, 1)
tl.BackgroundColor3 = Color3.fromRGB(29, 23, 41)
tl.BackgroundTransparency = 0.2
tl.BorderSizePixel = 0
tl.Text = D.nazwa
tl.TextColor3 = Color3.fromRGB(255, 255, 255)
tl.TextScaled = true
tl.Font = Enum.Font.GothamBold
local rog = Instance.new("UICorner")
rog.CornerRadius = UDim.new(0.3, 0)
rog.Parent = tl
local odstep = Instance.new("UIPadding")
odstep.PaddingTop = UDim.new(0.12, 0)
odstep.PaddingBottom = UDim.new(0.12, 0)
odstep.PaddingLeft = UDim.new(0.06, 0)
odstep.PaddingRight = UDim.new(0.06, 0)
odstep.Parent = tl
tl.Parent = bg
bg.Parent = t
t.Parent = model
model:SetAttribute("Szczyt", szczyt - y)
return string.format("%s: %d brył (świecących %d), %d kości; podłoże %s na y = %.2f; stoi w (%.1f; %.1f), szczyt %.2f",
	D.id, n, neon, #D.kosci, traf.Instance.Name, y, pos.X, pos.Z, szczyt - y)
'''

SKRYPT = WSTEP + r'''
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
if not kont then
	return "STOP: brak kontenera Workspace/" .. KONTENER
end
local stary = kont:FindFirstChild("__NAZWA__")
if stary then
	stary:Destroy()
end
local s = Instance.new("Script")
s.Name = "__NAZWA__"
s.Source = __TEKST__
s.Parent = kont
game:GetService("ChangeHistoryService"):SetWaypoint("RasyProba: zbudowano")
local modeli, czesci = 0, 0
for _, d in kont:GetChildren() do
	if d:IsA("Model") then
		modeli += 1
	end
end
for _, d in kont:GetDescendants() do
	if d:IsA("BasePart") then
		czesci += 1
	end
end
return string.format("skrypt __NAZWA__ zainstalowany (%d znaków); w kontenerze %d figur, %d części", #s.Source, modeli, czesci)
'''

USUN = WSTEP + r'''
local nasze, obce = kontenery()
local zostawione = ""
if #obce > 0 then
	zostawione = string.format("; zostawiono %d obiekt(ów) '%s' bez atrybutu Wygenerowane (cudza praca, nie ruszam)", #obce, KONTENER)
end
if #nasze == 0 then
	return (if #obce > 0 then "STOP: nic nie usunięto" else "nie ma czego usuwać") .. zostawione
end
local CH = game:GetService("ChangeHistoryService")
CH:SetWaypoint("RasyProba: przed usunięciem")
for _, k in nasze do
	k:Destroy()
end
CH:SetWaypoint("RasyProba: usunięto")
return string.format("USUNIĘTO %d × Workspace/%s%s", #nasze, KONTENER, zostawione)
'''

# odczyt stanu wystawy (Edit i Play): JSON; niczego nie zmienia
STAN = r'''
local HS = game:GetService("HttpService")
local kont = workspace:FindFirstChild("__KONTENER__")
if not kont or kont:GetAttribute("Wygenerowane") ~= true then
	return HS:JSONEncode({ jest = false })
end
local w = { jest = true, figury = {}, czesci = 0, skrypt = kont:FindFirstChild("__NAZWA__") ~= nil,
	spoczynek = kont:GetAttribute("SpoczynekGra"), zbudowano = kont:GetAttribute("Zbudowano") }
for _, m in kont:GetChildren() do
	if m:IsA("Model") then
		local f = { id = m.Name, nazwa = m:GetAttribute("Nazwa"), skala = m:GetAttribute("Skala"), bryl = m:GetAttribute("Bryl"),
			czesci = 0, koliduja = 0, dotyk = 0, promienie = 0, niezakotwiczone_korzenie = 0, neon = 0 }
		local ziemia = m:GetAttribute("Ziemia")
		local dol = math.huge
		for _, p in m:GetDescendants() do
			if p:IsA("BasePart") then
				f.czesci += 1
				if p.CanCollide then f.koliduja += 1 end
				if p.CanTouch then f.dotyk += 1 end
				if p.CanQuery then f.promienie += 1 end
				if p.Material == Enum.Material.Neon then f.neon += 1 end
				if p.Transparency < 1 then
					local s, c = p.Size / 2, p.CFrame
					for _, zx in { -1, 1 } do
						for _, zy in { -1, 1 } do
							for _, zz in { -1, 1 } do
								dol = math.min(dol, (c * Vector3.new(s.X * zx, s.Y * zy, s.Z * zz)).Y)
							end
						end
					end
				end
			end
		end
		local hrp = m:FindFirstChild("HumanoidRootPart")
		local glowa = m:FindFirstChild("Head")
		local tab = m:FindFirstChild("Tabliczka")
		local napis = tab and tab:FindFirstChild("Nazwa") and tab.Nazwa:FindFirstChild("Napis")
		f.korzen_zakotwiczony = hrp ~= nil and hrp.Anchored
		f.stopy = dol - ziemia
		f.wzrost = glowa and (glowa.Position.Y + glowa.Size.Y / 2 - ziemia) or -1
		f.tabliczka = napis and napis.Text or ""
		f.tabliczka_nad = tab and (tab.Position.Y - ziemia) or -1
		f.poz = hrp and { hrp.Position.X, hrp.Position.Z } or {}
		f.patrzy = hrp and { hrp.CFrame.LookVector.X, hrp.CFrame.LookVector.Z } or {}
		w.czesci += f.czesci
		table.insert(w.figury, f)
	end
end
return HS:JSONEncode(w)
'''


def log(*a):
    print("RASY-PROBA |", *a, flush=True)


def wstaw(szablon, **w):
    for k, v in w.items():
        szablon = szablon.replace("__%s__" % k, v)
    return szablon


def zrodlo_skryptu(U):
    """Tekst skryptu spoczynku z wpisanym okresem i kątami z ustawień."""
    with open(SKRYPT_PLIK, encoding="utf-8") as f:
        tekst = f.read().replace("\r\n", "\n")
    return wstaw(tekst, OKRES=repr(float(U["spoczynek"]["okres_s"])), KATY=DN.luau(DN.spoczynek(U)))


def kontrola_luau():
    """Moduł kontroli statycznej swiat/las_potwory/sprawdz_luau.py wczytany po ścieżce (tylko odczyt)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "kontrola_luau_potworow", os.path.join(REPO, "swiat", "las_potwory", "sprawdz_luau.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sprawdz_zrodla():
    """Kontrola statyczna źródeł Luau pakietu (reguły swiat/las_potwory/sprawdz_luau.py, tylko odczyt modułu)."""
    SL = kontrola_luau()
    return SL.sprawdz_pliki([SKRYPT_PLIK], wypisz=lambda t: None)


def kod_stanu(U):
    return wstaw(STAN, KONTENER=U["kontener"], NAZWA=U["skrypt_spoczynku"])


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Wystawa ras w Studio: Workspace/RasyProba")
    ap.add_argument("--sucho", action="store_true", help="tylko policz i sprawdź źródła, bez Studio")
    ap.add_argument("--usun", action="store_true", help="usuń własny kontener")
    ap.add_argument("--stan", action="store_true", help="odczytaj, co stoi w kontenerze")
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    U = DN.ustawienia()
    F = DN.figury(U)
    bledy = sprawdz_zrodla()
    for b in bledy:
        log("BŁĄD źródeł:", b)
    for f in F:
        log("%-12s %-12s skala %.2f, wzrost %.2f, brył %d, części w Studio %d, świecących %d%s"
            % (f["id"], f["nazwa"], f["skala"], f["wzrost"], len(f["czesci"]), DN.liczba_czesci(f), f["swiecace"],
               "; uwagi: " + "; ".join(f["uwagi"]) if f["uwagi"] else ""))
    log("razem części w Studio: %d; źródła Luau: %s" % (sum(DN.liczba_czesci(f) for f in F),
                                                        "bez błędów" if not bledy else "%d błędów" % len(bledy)))
    if bledy:
        return 1
    if a.sucho:
        return 0
    from studio_mcp import StudioMCP  # noqa: E402
    from cel_studio import MIEJSCE, wybierz_studio  # noqa: E402
    wspolne = dict(MIEJSCE=str(MIEJSCE), KONTENER=U["kontener"])
    with StudioMCP(timeout=240) as s:
        sid = wybierz_studio(s, a.studio)
        if "Current Studio Mode: Edit" not in s.call("get_studio_state", {"studio_id": sid})["text"]:
            log("PRZERWANO — Studio nie jest w trybie Edit (ktoś może grać); nic nie zmieniono")
            return 1

        def wykonaj(kod, opis):
            r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
            tekst = (r["text"] or "").strip()
            if r["is_error"] or tekst.startswith("STOP"):
                log("PRZERWANO — Studio odmówiło (%s): %s" % (opis, tekst[:600]))
                raise SystemExit(1)
            return tekst

        if a.stan:
            print(json.dumps(json.loads(wykonaj(kod_stanu(U), "stan")), ensure_ascii=False, indent=1))
            return 0
        if a.usun:
            log(wykonaj(wstaw(USUN, **wspolne), "usuwanie"))
            return 0
        start = {"figury": [{"id": f["id"], "poz": f["poz"]} for f in F], "pudlo": U["wolne_miejsce"]["pudlo"],
                 "nad": U["wolne_miejsce"]["nad_ziemia"]}
        log(wykonaj(wstaw(START, DANE=DN.luau(start), ZRODLO=U["zrodlo"], CZAS=time.strftime("%Y-%m-%d %H:%M"),
                          **wspolne), "start"))
        for f in F:
            d = {k: f[k] for k in ("id", "nazwa", "skala", "wzrost", "poz", "patrz", "hrp", "kosci", "czesci",
                                   "materialy")}
            d["tabliczka"] = U["tabliczka"]
            log(wykonaj(wstaw(FIGURA, DANE=DN.luau(d), **wspolne), f["id"]))
        log(wykonaj(wstaw(SKRYPT, NAZWA=U["skrypt_spoczynku"], TEKST=DN.luau(zrodlo_skryptu(U)), **wspolne), "skrypt"))
        stan = json.loads(wykonaj(kod_stanu(U), "stan"))
        zle = []
        for f in F:
            m = next((x for x in stan["figury"] if x["id"] == f["id"]), None)
            if m is None:
                zle.append("%s: brak figury" % f["id"])
            elif m["czesci"] != DN.liczba_czesci(f) or m["koliduja"] or abs(m["stopy"]) > 0.03:
                zle.append("%s: części %d (oczekiwane %d), kolidujących %d, stopy %.3f"
                           % (f["id"], m["czesci"], DN.liczba_czesci(f), m["koliduja"], m["stopy"]))
        log("kontrola po budowie: %s" % ("zgodne — %d figur, %d części" % (len(stan["figury"]), stan["czesci"])
                                         if not zle else "NIEZGODNE: " + "; ".join(zle)))
        return 1 if zle else 0


if __name__ == "__main__":
    sys.exit(main())
