-- Spoczynek figur wystawy ras (Workspace/RasyProba/SpoczynekRas) — TYLKO w Roblox Studio (Play albo Run).
-- Instaluje go `python -B swiat/rasy_proba/zbuduj.py`; kąty i okres wpisuje budowniczy z ustawienia.json.
-- Jedna wspólna, trzyklatkowa sekwencja „oddechu” (ok. 20 obiektów) dla wszystkich figur: mają te same kości
-- R15, więc każda odtwarza ją własnym Animatorem. RegisterKeyframeSequence działa wyłącznie w Studio — w opublikowanej
-- grze figury stoją nieruchomo (i tak ten skrypt kończy się na strażniku). Niczego poza własnym kontenerem nie rusza.
if not game:GetService("RunService"):IsStudio() then
	return
end
local KSP = game:GetService("KeyframeSequenceProvider")
local kontener = script.Parent
local PREFIKS = "[RasyProba] "
local OKRES = __OKRES__
local KATY = __KATY__ -- kość -> {rx, ry, rz} w szczycie oddechu (radiany, układ rigu)

local function sekwencja()
	local ks = Instance.new("KeyframeSequence")
	ks.Name = "spoczynek"
	ks.Loop = true
	ks.Priority = Enum.AnimationPriority.Idle
	for i, czas in { 0, OKRES / 2, OKRES } do
		local k = if i == 2 then 1 else 0
		local kf = Instance.new("Keyframe")
		kf.Time = czas
		local korzen = Instance.new("Pose")
		korzen.Name = "HumanoidRootPart"
		korzen.Weight = 0
		korzen.Parent = kf
		local biodra = Instance.new("Pose")
		biodra.Name = "LowerTorso"
		biodra.Weight = 0
		biodra.Parent = korzen
		local function poza(nazwa, rodzic)
			local a = KATY[nazwa] or { 0, 0, 0 }
			local p = Instance.new("Pose")
			p.Name = nazwa
			p.Weight = 1
			p.EasingStyle = Enum.PoseEasingStyle.Cubic
			p.EasingDirection = Enum.PoseEasingDirection.InOut
			p.CFrame = CFrame.fromOrientation(a[1] * k, a[2] * k, a[3] * k)
			p.Parent = rodzic
			return p
		end
		local tulow = poza("UpperTorso", biodra)
		poza("Head", tulow)
		poza("LeftUpperArm", tulow)
		poza("RightUpperArm", tulow)
		kf.Parent = ks
	end
	return ks
end

local ok, id = pcall(function()
	return KSP:RegisterKeyframeSequence(sekwencja())
end)
if not ok then
	warn(PREFIKS .. "spoczynek: nie udało się zarejestrować sekwencji: " .. tostring(id))
	kontener:SetAttribute("SpoczynekGra", 0)
	return
end
local gra = 0
for _, model in kontener:GetChildren() do
	local kontroler = model:IsA("Model") and model:FindFirstChildWhichIsA("AnimationController")
	local animator = kontroler and kontroler:FindFirstChildWhichIsA("Animator")
	if animator then
		local anim = Instance.new("Animation")
		anim.Name = "spoczynek"
		anim.AnimationId = id
		local ok2, sciezka = pcall(function()
			return animator:LoadAnimation(anim)
		end)
		if ok2 then
			sciezka.Looped = true
			sciezka:Play(0.2)
			sciezka.TimePosition = (gra % 4) * OKRES / 4 -- figury nie oddychają równo
			gra += 1
		else
			warn(PREFIKS .. "spoczynek: " .. model.Name .. ": " .. tostring(sciezka))
		end
	end
end
kontener:SetAttribute("SpoczynekGra", gra)
