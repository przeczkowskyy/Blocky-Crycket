#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba techniczna: jedna małpa na standardowym szkielecie R15 (klocki, bez Blendera) zamiast ośmiu różnych potworów.

    python -B swiat/ewolucja/proba_malpy.py --studio <id>            # buduje, próbuje w Play, mierzy, sprząta
    python -B swiat/ewolucja/proba_malpy.py --studio <id> --zostaw   # bez sprzątania na końcu

Buduje szablon małpy (części + przyczepy stawów → Humanoid:BuildRigFromAttachments) w ServerStorage/EwolucjaProbaMalpy
i kontener Workspace/EwolucjaProbaMalpy (podłoga, skrypty ze strażnikiem „tylko Studio”). Na czas Play wyłącza
EwolucjaGra (pozostałe gry już wyłączone) i przywraca ją dokładnie po próbie. Animacje: standardowe klipy R15 ze
skryptu Animate postaci gracza (gracz: ten skrypt; boty: te same identyfikatory przez Animator na serwerze).
Na końcu usuwa tymczasowe obiekty (chyba że --zostaw) i sprawdza stan wydania. Zrzuty: klatki/proba_malpy_*.jpg.
"""
import argparse
import io
import json
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
PAKIET = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(PAKIET))
sys.path.append(os.path.join(REPO, "tools"))
from studio_mcp import StudioMCP  # noqa: E402

K = "EwolucjaProbaMalpy"
SRODEK = (700, 0, -800)  # z dala od łąki (0, 0, −800), zabawek i Pet Areny
ETAPY = [  # (nazwa, skala, futro, przyczepy)
    ("BABY MONKEY", 0.6, "B07A4A", []),
    ("GORILLA", 2.0, "3A3540", ["brwi", "srebrny_grzbiet"]),
    ("GIANT APE", 5.0, "241E26", ["brwi", "srebrny_grzbiet", "pancerz", "korona"]),
]

WZORZEC = r'''
if game:GetService("RunService"):IsRunning() then return "STOP: Play" end
local SS = game:GetService("ServerStorage")
local CH = game:GetService("ChangeHistoryService")
CH:SetWaypoint("EwolucjaProbaMalpy: przed")
for _, d in { SS:FindFirstChild("__K__"), workspace:FindFirstChild("__K__") } do
	if d and d:GetAttribute("Wygenerowane") ~= true then return "STOP: obcy obiekt __K__" end
	if d then d:Destroy() end
end
local m = Instance.new("Model")
m.Name = "Malpa"
local function cz(n, roz, poz, kolor)
	local p = Instance.new("Part")
	p.Name = n
	p.Size = roz
	p.CFrame = CFrame.new(poz)
	p.Color = Color3.fromHex(kolor or "7A5A3A")
	p.Material = Enum.Material.SmoothPlastic
	p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
	p.Parent = m
	return p
end
local V = Vector3.new
-- proporcje małpy: krótkie nogi, długie ręce (dłonie przy kolanach), duża głowa; ziemia y = 0, przód −Z
local P = {
	HumanoidRootPart = cz("HumanoidRootPart", V(2, 2, 1), V(0, 3.05, 0)),
	LowerTorso = cz("LowerTorso", V(2.2, 0.8, 1.4), V(0, 2.45, 0)),
	UpperTorso = cz("UpperTorso", V(2.8, 1.8, 1.7), V(0, 3.75, 0.1)),
	Head = cz("Head", V(1.9, 1.7, 1.7), V(0, 5.5, -0.1)),
}
for _, s in { { "Left", -1 }, { "Right", 1 } } do
	local n, k = s[1], s[2]
	P[n .. "UpperArm"] = cz(n .. "UpperArm", V(0.8, 1.6, 0.8), V(k * 1.8, 3.6, 0))
	P[n .. "LowerArm"] = cz(n .. "LowerArm", V(0.75, 1.6, 0.75), V(k * 1.8, 2.0, 0))
	P[n .. "Hand"] = cz(n .. "Hand", V(0.9, 0.6, 0.9), V(k * 1.8, 0.9, 0))
	P[n .. "UpperLeg"] = cz(n .. "UpperLeg", V(0.9, 0.9, 0.9), V(k * 0.6, 1.6, 0))
	P[n .. "LowerLeg"] = cz(n .. "LowerLeg", V(0.8, 0.8, 0.8), V(k * 0.6, 0.75, 0))
	P[n .. "Foot"] = cz(n .. "Foot", V(0.9, 0.35, 1.2), V(k * 0.6, 0.175, -0.15))
end
P.HumanoidRootPart.Transparency = 1
P.HumanoidRootPart.CanCollide = false
m.PrimaryPart = P.HumanoidRootPart
-- przyczepy stawów (te same nazwy co w R15) w obu częściach → Motor6D z BuildRigFromAttachments
local function staw(nazwa, a, b, poz)
	for _, p in { P[a], P[b] } do
		local at = Instance.new("Attachment")
		at.Name = nazwa .. "RigAttachment"
		at.Parent = p
		at.WorldPosition = poz
	end
	-- Motor6D jak w R15 (nazwa stawu, w części potomnej); C0/C1 z pozycji stawu
	local mo = Instance.new("Motor6D")
	mo.Name = nazwa
	mo.Part0, mo.Part1 = P[a], P[b]
	mo.C0 = P[a].CFrame:Inverse() * CFrame.new(poz)
	mo.C1 = P[b].CFrame:Inverse() * CFrame.new(poz)
	mo.Parent = P[b]
end
staw("Root", "HumanoidRootPart", "LowerTorso", V(0, 2.45, 0))
staw("Waist", "LowerTorso", "UpperTorso", V(0, 2.85, 0))
staw("Neck", "UpperTorso", "Head", V(0, 4.65, 0))
for _, s in { { "Left", -1 }, { "Right", 1 } } do
	local n, k = s[1], s[2]
	staw(n .. "Shoulder", "UpperTorso", n .. "UpperArm", V(k * 1.45, 4.4, 0))
	staw(n .. "Elbow", n .. "UpperArm", n .. "LowerArm", V(k * 1.8, 2.8, 0))
	staw(n .. "Wrist", n .. "LowerArm", n .. "Hand", V(k * 1.8, 1.2, 0))
	staw(n .. "Hip", "LowerTorso", n .. "UpperLeg", V(k * 0.6, 2.05, 0))
	staw(n .. "Knee", n .. "UpperLeg", n .. "LowerLeg", V(k * 0.6, 1.15, 0))
	staw(n .. "Ankle", n .. "LowerLeg", n .. "Foot", V(k * 0.6, 0.35, 0))
end
-- twarz: pysk i oczy (spawane do głowy)
local function przyczep(n, roz, poz, kolor, rodzic, ksztalt)
	local p = cz(n, roz, poz, kolor)
	p.CanCollide = false
	p.Massless = true
	if ksztalt then p.Shape = ksztalt end
	local w = Instance.new("WeldConstraint")
	w.Part0, w.Part1 = rodzic, p
	w.Parent = p
	return p
end
przyczep("Pysk", V(1.3, 0.8, 0.5), V(0, 5.15, -1.0), "D9B08C", P.Head)
przyczep("OkoL", V(0.3, 0.3, 0.1), V(-0.45, 5.8, -0.97), "111111", P.Head)
przyczep("OkoP", V(0.3, 0.3, 0.1), V(0.45, 5.8, -0.97), "111111", P.Head)
local h = Instance.new("Humanoid")
h.RigType = Enum.HumanoidRigType.R15
h.AutomaticScalingEnabled = false
h.HipHeight = 2.05
h.Parent = m
Instance.new("Animator").Parent = h
local f = Instance.new("Folder")
f.Name = "__K__"
f:SetAttribute("Wygenerowane", true)
f.Parent = SS
m.Parent = f
local n = 0
for _, d in m:GetDescendants() do
	if d:IsA("Motor6D") then n += 1 end
end
-- kontener w Workspace: podłoga próby i skrypty (strażnik Studio)
local k = Instance.new("Folder")
k.Name = "__K__"
k:SetAttribute("Wygenerowane", true)
local pod = Instance.new("Part")
pod.Name = "Podloga"
pod.Anchored = true
pod.Size = V(260, 2, 260)
pod.Position = V(__SX__, -1, __SZ__)
pod.Color = Color3.fromHex("86C062")
pod.Material = Enum.Material.Grass
pod.Parent = k
for _, s in { { "SerwerMalp", Enum.RunContext.Server, __SERWER__ }, { "KlientMalp", Enum.RunContext.Client, __KLIENT__ } } do
	local sk = Instance.new("Script")
	sk.Name = s[1]
	sk.RunContext = s[2]
	sk.Source = s[3]
	sk.Parent = k
end
k.Parent = workspace
CH:SetWaypoint("EwolucjaProbaMalpy: zbudowano")
return string.format("motory %d, części %d", n, #m:GetChildren())
'''

# wspólne (serwer i podgląd w Edit): etap = skala, futro, przyczepy
ETAP_LUAU = r'''
local function etap(m, skala, futro, dodatki)
	local V = Vector3.new
	for _, p in m:GetChildren() do
		if p:IsA("BasePart") and p.Name ~= "HumanoidRootPart" and p.Name ~= "Pysk" and not string.match(p.Name, "^Oko") then
			p.Color = Color3.fromHex(futro)
		end
	end
	local function przyczep(n, roz, off, kolor, rodzic, mat, ksztalt)
		local p = Instance.new("Part")
		p.Name = n
		p.Size = roz
		p.CFrame = rodzic.CFrame * CFrame.new(off)
		p.Color = Color3.fromHex(kolor)
		p.Material = mat or Enum.Material.SmoothPlastic
		p.CanCollide = false
		p.Massless = true
		if ksztalt then p.Shape = ksztalt end
		local w = Instance.new("WeldConstraint")
		w.Part0, w.Part1 = rodzic, p
		w.Parent = p
		p.Parent = m
	end
	local H, T = m.Head, m.UpperTorso
	for _, d in dodatki do
		if d == "brwi" then
			przyczep("Brwi", V(1.9, 0.35, 0.5), V(0, 0.45, -0.75), "1A1418", H)
		elseif d == "srebrny_grzbiet" then
			przyczep("Grzbiet", V(2.6, 1.5, 0.3), V(0, 0.1, 0.85), "B8B8C4", T)
		elseif d == "pancerz" then
			przyczep("Pancerz", V(2.4, 1.3, 0.3), V(0, 0.1, -0.9), "8A6A3A", T, Enum.Material.Wood)
			przyczep("NaramiennikL", V(1.0, 0.4, 1.0), V(-1.55, 0.95, 0), "8A6A3A", T, Enum.Material.Wood)
			przyczep("NaramiennikP", V(1.0, 0.4, 1.0), V(1.55, 0.95, 0), "8A6A3A", T, Enum.Material.Wood)
		elseif d == "korona" then
			przyczep("Korona", V(1.6, 0.5, 1.6), V(0, 1.1, 0), "FFC83D", H, Enum.Material.Neon)
			for i = 0, 3 do
				local a = i * math.pi / 2
				przyczep("Zab" .. i, V(0.35, 0.6, 0.35), V(math.cos(a) * 0.6, 1.5, math.sin(a) * 0.6), "FFC83D", H, Enum.Material.Neon)
			end
		end
	end
	local h = m:FindFirstChildOfClass("Humanoid")
	m:ScaleTo(skala)
	return h
end
'''

SERWER = r'''
if not game:GetService("RunService"):IsStudio() then
	return
end
local Players = game:GetService("Players")
local SS = game:GetService("ServerStorage")
local k = script.Parent
local wz = SS:WaitForChild("__K__"):WaitForChild("Malpa")
__ETAP__
local C = Vector3.new(__SX__, 0, __SZ__)
local ETAPY = __ETAPY__
local anim = {}
k:SetAttribute("Gotowy", false)

-- gracz: ta sama małpa, standardowy skrypt Animate z jego własnej postaci
local function zrobGracza(plr, nr, skala)
	local stara = plr.Character
	local animate = stara and stara:FindFirstChild("Animate")
	if not animate then
		return false
	end
	animate = animate:Clone()
	for _, d in animate:GetDescendants() do
		if d:IsA("Animation") then
			anim[d.Parent.Name .. "/" .. d.Name] = d.AnimationId
		end
	end
	local E = ETAPY[nr]
	local m = wz:Clone()
	m.Name = plr.Name
	local h = etap(m, skala or E[2], E[3], E[4])
	m:PivotTo(CFrame.new(C + Vector3.new(0, 1 + h.HipHeight + 1 * (skala or E[2]), 0)))
	animate.Parent = m
	m:SetAttribute("Malpa", nr)
	m.Parent = workspace
	plr.Character = m
	if stara then
		stara:Destroy()
	end
	return true
end

-- boty: ta sama małpa, te same klipy przez Animator na serwerze
local boty = {}
local function zrobBota(i, skala, E)
	local m = wz:Clone()
	m.Name = "MalpaBot" .. i
	local h = etap(m, skala, E[3], E[4])
	local a = math.random() * math.pi * 2
	m:PivotTo(CFrame.new(C + Vector3.new(math.sin(a) * 60, 2 + h.HipHeight + skala, math.cos(a) * 60)))
	m.Parent = k
	h.WalkSpeed = 10 + skala * 2
	local an = h:FindFirstChildOfClass("Animator")
	local tr = {}
	for nazwa, id in { idle = anim["idle/Animation1"], walk = anim["walk/WalkAnim"], run = anim["run/RunAnim"] } do
		if id then
			local x = Instance.new("Animation")
			x.AnimationId = id
			tr[nazwa] = an:LoadAnimation(x)
			tr[nazwa].Looped = true
		end
	end
	if tr.idle then
		tr.idle:Play()
	end
	h.Running:Connect(function(v)
		local ruch = v > 0.5
		if tr.walk then
			if ruch and not tr.walk.IsPlaying then
				tr.walk:Play(0.2)
				if tr.idle then tr.idle:Stop(0.2) end
			elseif not ruch and tr.walk.IsPlaying then
				tr.walk:Stop(0.2)
				if tr.idle then tr.idle:Play(0.2) end
			end
			tr.walk:AdjustSpeed(math.max(0.3, v / (16 * skala)) * 1.2)
		end
	end)
	m.PrimaryPart:SetNetworkOwner(nil)
	table.insert(boty, { m = m, h = h, skala = skala, tr = tr })
	m:SetAttribute("Skala", skala)
end

local function gracz(plr)
	local c = plr.Character or plr.CharacterAdded:Wait()
	c:WaitForChild("Animate", 10)
	task.wait(0.5)
	if zrobGracza(plr, 2) then
		k:SetAttribute("GraczMalpa", true)
	end
	if #boty == 0 then
		for i = 1, __BOTOW__ do
			local skala = if i == 1 then 0.5 elseif i == 2 then 6 else 0.6 + (i % 9) * 0.55
			local E = if skala < 1 then ETAPY[1] elseif skala < 3.5 then ETAPY[2] else ETAPY[3]
			zrobBota(i, skala, E)
		end
		k:SetAttribute("Gotowy", true)
	end
end
Players.PlayerAdded:Connect(gracz)
for _, p in Players:GetPlayers() do
	task.spawn(gracz, p)
end
-- boty chodzą do losowych punktów
task.spawn(function()
	while true do
		for _, b in boty do
			if b.h.Parent and math.random() < 0.35 then
				local a = math.random() * math.pi * 2
				local r = math.random() * 100
				b.h:MoveTo(C + Vector3.new(math.sin(a) * r, 0, math.cos(a) * r))
			end
		end
		task.wait(1)
	end
end)
-- haczyk próby: stan i skala gracza
local bf = Instance.new("BindableFunction")
bf.Name = "Sterowanie"
bf.Parent = k
bf.OnInvoke = function(co, a)
	if co == "stan" then
		local w = { boty = {} }
		w.zgubione = 0
		for _, b in boty do
			local hrp = b.m.PrimaryPart
			if not hrp or not b.h.Parent then
				w.zgubione += 1
				continue
			end
			local graj = {}
			for _, t in b.h:FindFirstChildOfClass("Animator"):GetPlayingAnimationTracks() do
				table.insert(graj, t.Animation.AnimationId)
			end
			table.insert(w.boty, { skala = b.skala, y = hrp.Position.Y, hip = b.h.HipHeight, hrp_y = hrp.Size.Y, v = hrp.AssemblyLinearVelocity.Magnitude,
				ws = b.h.WalkSpeed, stan = b.h:GetState().Name, klipy = graj })
		end
		return w
	elseif co == "skala_gracza" then
		local plr = Players:GetPlayers()[1]
		local c = plr and plr.Character
		if c then
			c:ScaleTo(a)
			local h = c:FindFirstChildOfClass("Humanoid")
			h.WalkSpeed = 12 + a * 2
			return { hip = h.HipHeight, skala = c:GetScale() }
		end
	end
	return nil
end
'''

KLIENT = r'''
if not game:GetService("RunService"):IsStudio() then
	return
end
local RS = game:GetService("RunService")
local plr = game:GetService("Players").LocalPlayer
local n, s, okno = 0, 0, 0
RS.RenderStepped:Connect(function(dt)
	-- serwer podmienia postać (Player.Character = małpa): kamera musi dostać nowego Humanoida
	local c0 = plr.Character
	local h0 = c0 and c0:FindFirstChildOfClass("Humanoid")
	if h0 and workspace.CurrentCamera.CameraSubject ~= h0 then
		workspace.CurrentCamera.CameraSubject = h0
	end
	-- kamera gry (z góry, odległość rośnie ze skalą postaci) — domyślna kamera nie skaluje się z postacią
	if c0 and c0.PrimaryPart and c0:GetAttribute("Malpa") then
		local cam = workspace.CurrentCamera
		local s = c0:GetScale()
		local d = 16 + 7 * s
		local p0 = c0.PrimaryPart.Position
		cam.CameraType = Enum.CameraType.Scriptable
		cam.CFrame = CFrame.lookAt(p0 + Vector3.new(0, d * 0.85, -d * 0.6), p0)
	end
	n += 1
	s += dt
	okno += dt
	if okno >= 2 then
		plr:SetAttribute("MP_Klatka", s / n * 1000)
		local c = plr.Character
		local h = c and c:FindFirstChildOfClass("Humanoid")
		local an = h and h:FindFirstChildOfClass("Animator")
		local graj = {}
		if an then
			for _, t in an:GetPlayingAnimationTracks() do
				table.insert(graj, t.Name)
			end
		end
		plr:SetAttribute("MP_Klipy", table.concat(graj, ","))
		plr:SetAttribute("MP_Malpa", c and c:GetAttribute("Malpa") or 0)
		n, s, okno = 0, 0, 0
	end
end)
'''

PODGLAD = r'''
if game:GetService("RunService"):IsRunning() then return "STOP: Play" end
local k = workspace:FindFirstChild("__K__")
local wz = game:GetService("ServerStorage"):FindFirstChild("__K__").Malpa
__ETAP__
local stary = k:FindFirstChild("Podglad")
if stary then stary:Destroy() end
local f = Instance.new("Folder")
f.Name = "Podglad"
f.Parent = k
local x = __SX__ - 30
for i, E in __ETAPY__ do
	local m = wz:Clone()
	m.Name = E[1]
	local h = etap(m, E[2], E[3], E[4])
	m:PivotTo(CFrame.new(x, 1 + h.HipHeight + E[2], __SZ__))
	m.PrimaryPart.Anchored = true
	m.Parent = f
	x += 6 + E[2] * 6
end
local cam = workspace.CurrentCamera
if k:GetAttribute("KameraEdycji") == nil then
	k:SetAttribute("KameraEdycji", cam.CFrame) -- widok edytora wraca po zrzucie
end
cam.CFrame = CFrame.lookAt(Vector3.new(__SX__ - 14, 14, __SZ__ - 46), Vector3.new(__SX__ - 14, 8, __SZ__))
return "ok"
'''


URZADZENIE = r'''
local svc = game:GetService("StudioDeviceSimulatorService")
for _, id in svc:GetDeviceListAsync() do
	local info = svc:GetDeviceInfoAsync(id)
	if info.Name == "Samsung Galaxy A06" then
		svc:SetDeviceAsync(id)
		task.wait(0.4)
		return info.Name .. " " .. tostring(workspace.CurrentCamera.ViewportSize)
	end
end
return "brak telefonu"
'''

SPRZATANIE = r'''
local CH = game:GetService("ChangeHistoryService")
CH:SetWaypoint("EwolucjaProbaMalpy: przed sprzątaniem")
local k = workspace:FindFirstChild("__K__")
local cf = k and k:GetAttribute("KameraEdycji")
if typeof(cf) == "CFrame" then
	workspace.CurrentCamera.CFrame = cf
end
for _, d in { k, game:GetService("ServerStorage"):FindFirstChild("__K__") } do
	if d and d:GetAttribute("Wygenerowane") == true then
		d:Destroy()
	end
end
CH:SetWaypoint("EwolucjaProbaMalpy: usunięto")
return "usunięto"
'''


def wstaw(t, **w):
    for k, v in w.items():
        t = t.replace("__%s__" % k, v)
    return t


def luau_str(t):
    n = 1
    while ("]" + "=" * n + "]") in t:
        n += 1
    return "[" + "=" * n + "[" + t + "]" + "=" * n + "]"


def etapy_luau():
    return "{ " + ", ".join('{ "%s", %s, "%s", { %s } }' % (n, s, f, ", ".join('"%s"' % d for d in dd)) for n, s, f, dd in ETAPY) + " }"


def main():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio", required=True)
    ap.add_argument("--zostaw", action="store_true")
    ap.add_argument("--botow", type=int, default=25)
    a = ap.parse_args()
    w = dict(K=K, SX=str(SRODEK[0]), SZ=str(SRODEK[2]), ETAPY=etapy_luau(), BOTOW=str(a.botow), ETAP=ETAP_LUAU)
    serwer, klient = wstaw(SERWER, **w), wstaw(KLIENT, **w)
    kod = wstaw(WZORZEC, SERWER=luau_str(serwer), KLIENT=luau_str(klient), **w)
    print(kod if False else "", end="")
    with StudioMCP(timeout=240) as s:
        def luau(k, dm="Edit"):
            r = s.call("execute_luau", {"code": k, "datamodel_type": dm, "studio_id": a.studio}, timeout=240)
            if r["is_error"]:
                raise SystemExit("BŁĄD Luau: " + r["text"][:800])
            return r["text"].strip()
        def studio_edit():
            return "Current Studio Mode: Edit" in s.call("get_studio_state", {"studio_id": a.studio})["text"]

        def play(start):
            r = subprocess.run([sys.executable, "-B", os.path.join(REPO, "tools", "studio_mcp.py"), "call", "start_stop_play", "--args",
                                json.dumps({"is_start": start, "studio_id": a.studio})], capture_output=True, text=True, encoding="utf-8", timeout=180)
            return (r.stdout + r.stderr).strip()[-40:]

        def zrzut(nazwa):
            from PIL import Image
            r = s.call("screen_capture", {"capture_id": "malpa", "studio_id": a.studio}, timeout=120)
            img = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
            img.save(os.path.join(PAKIET, "klatki", nazwa), quality=85)
            print("zrzut klatki/" + nazwa)

        def czekaj(f, limit):
            t0 = time.time()
            while time.time() - t0 < limit:
                try:
                    if f():
                        return True
                except SystemExit:
                    pass
                time.sleep(0.5)
            return False

        def atr():
            return json.loads(luau('local p = game:GetService("Players").LocalPlayer local a = p:GetAttributes() local c = p.Character '
                                   'a.poz = c and { c.PrimaryPart.Position.X, c.PrimaryPart.Position.Z } a.cam = (workspace.CurrentCamera.CFrame.Position - '
                                   '(c and c.PrimaryPart.Position or Vector3.zero)).Magnitude return game:GetService("HttpService"):JSONEncode(a)', "Client"))

        def idz(dx, dz, czas):
            luau('local c = game:GetService("Players").LocalPlayer.Character c.Humanoid:MoveTo(c.PrimaryPart.Position + Vector3.new(%f, 0, %f)) return "ok"'
                 % (dx, dz), "Client")
            p0 = atr()["poz"]
            time.sleep(czas)
            a1 = atr()
            return ((a1["poz"][0] - p0[0]) ** 2 + (a1["poz"][1] - p0[1]) ** 2) ** 0.5 / czas, a1

        if not studio_edit():
            raise SystemExit("Studio nie jest w trybie Edit — przerwano")
        print("budowa:", luau(kod))
        print("podgląd:", luau(wstaw(PODGLAD, **w)))
        zrzut("proba_malpy_etapy.jpg")
        wyn = {}
        zb = [sys.executable, "-B", os.path.join(PAKIET, "zbuduj.py"), "--studio", a.studio, "--wlacz"]
        print(subprocess.run(zb + ["off"], capture_output=True, text=True, encoding="utf-8").stdout.strip()[-60:])
        print("telefon:", luau(URZADZENIE))
        try:
            print("Play:", play(True))
            ok = czekaj(lambda: json.loads(luau('return game:GetService("HttpService"):JSONEncode({ workspace.%s:GetAttribute("Gotowy"), '
                                                 'workspace.%s:GetAttribute("GraczMalpa") })' % (K, K), "Server")) == [True, True], 40)
            wyn["gotowe"] = ok
            luau('local SG = game:GetService("StarterGui") pcall(function() SG:SetCoreGuiEnabled(Enum.CoreGuiType.PlayerList, false) '
                 'SG:SetCoreGuiEnabled(Enum.CoreGuiType.Chat, false) end) return "ok"', "Client")
            time.sleep(3)
            v, a1 = idz(30, 10, 2.5)
            wyn["gracz_2x"] = {"v": round(v, 1), "klipy": a1.get("MP_Klipy"), "malpa": a1.get("MP_Malpa"), "kamera_st": round(a1["cam"], 1)}
            zrzut("proba_malpy_gracz.jpg")
            st = json.loads(luau('return game:GetService("HttpService"):JSONEncode(workspace.%s.Sterowanie:Invoke("stan"))' % K, "Server"))
            boty = st["boty"]
            wyn["boty"] = {"zgubione": st.get("zgubione"), "ile": len(boty), "z_klipami": sum(1 for b in boty if b["klipy"]),
                           "stoja_na_ziemi": sum(1 for b in boty if abs(b["y"] - b["hip"] - b["hrp_y"] / 2) < 0.6 * max(1, b["skala"])),
                           "skrajne": [{k: (round(x, 2) if isinstance(x, float) else x) for k, x in b.items() if k != "klipy"} | {"klipow": len(b["klipy"])}
                                       for b in boty[:2]]}
            for skala, nazwa in ((0.5, "mala"), (6, "wielka")):
                r = json.loads(luau('return game:GetService("HttpService"):JSONEncode(workspace.%s.Sterowanie:Invoke("skala_gracza", %s))' % (K, skala), "Server"))
                time.sleep(1.5)
                v, a1 = idz(-40, 20, 3)
                wyn["gracz_%s" % nazwa] = {"skala": r and r.get("skala"), "hip": r and round(r.get("hip"), 2), "v": round(v, 1), "klipy": a1.get("MP_Klipy"),
                                           "kamera_st": round(a1["cam"], 1)}
                if nazwa == "wielka":
                    zrzut("proba_malpy_skala6.jpg")
            time.sleep(4)
            wyn["klatka_ms"] = round(atr().get("MP_Klatka") or 0, 1)
            r = s.call("get_console_output", {"studio_id": a.studio}, timeout=60)
            wyn["bledy"] = [l for l in (r["text"] or "").splitlines() if "error" in l.lower() or "Stack" in l][:8]
        finally:
            print("Stop:", play(False))
            czekaj(studio_edit, 40)
            print("telefon off:", luau('local svc = game:GetService("StudioDeviceSimulatorService") pcall(function() svc:StopSimulationAsync() end) '
                                       'return tostring(workspace.CurrentCamera.ViewportSize)'))
            print(subprocess.run(zb + ["on"], capture_output=True, text=True, encoding="utf-8").stdout.strip()[-60:])
            if not a.zostaw:
                print("sprzątanie:", luau(SPRZATANIE.replace("__K__", K)))
        print(json.dumps(wyn, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
