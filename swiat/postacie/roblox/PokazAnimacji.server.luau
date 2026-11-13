-- Pokaz animacji postaci z klocków — TYLKO w Roblox Studio (Play albo Run). W opublikowanej grze nic nie robi.
-- Instalowany przez `python -B swiat/postacie/roblox_postac.py` jako Workspace/TestPostaci/PokazAnimacji.
-- Każda postać odtwarza po kolei swoje klipy z `AnimSaves` (KeyframeSequence) przez własny Animator.
-- Uwaga: `RegisterKeyframeSequence` działa wyłącznie w Studio. Do prawdziwej gry klipy trzeba opublikować jako
-- zasoby Animation (Animation Editor → Publish to Roblox) na koncie WŁAŚCICIELA gry i wpisać ich AnimationId.
local RunService = game:GetService("RunService")
if not RunService:IsStudio() then
	return
end
local KSP = game:GetService("KeyframeSequenceProvider")
local kontener = script.Parent
local PRZERWA = 0.5 -- sekundy w pozie spoczynkowej między klipami

local function pokaz(model)
	local kontroler = model:FindFirstChildWhichIsA("AnimationController")
	local animator = kontroler and kontroler:FindFirstChildWhichIsA("Animator")
	local saves = model:FindFirstChild("AnimSaves")
	if not animator or not saves then
		return
	end
	local sciezki = {}
	for _, ks in saves:GetChildren() do
		if ks:IsA("KeyframeSequence") then
			local anim = Instance.new("Animation")
			anim.Name = ks.Name
			anim.AnimationId = KSP:RegisterKeyframeSequence(ks)
			local ok, track = pcall(function()
				return animator:LoadAnimation(anim)
			end)
			if ok then
				table.insert(sciezki, { nazwa = ks.Name, track = track, petla = ks.Loop })
			else
				warn("PokazAnimacji: " .. model.Name .. "/" .. ks.Name .. ": " .. tostring(track))
			end
		end
	end
	if #sciezki == 0 then
		return
	end
	model:SetAttribute("Klipow", #sciezki)
	while model.Parent do
		for _, s in sciezki do
			model:SetAttribute("Klip", s.nazwa)
			s.track:Play(0.15)
			local dl = s.track.Length
			task.wait(if s.petla then math.max(2.4, dl * 3) else dl + 0.1)
			s.track:Stop(0.15)
			model:SetAttribute("Klip", "")
			task.wait(PRZERWA)
		end
	end
end

for _, model in kontener:GetChildren() do
	if model:IsA("Model") then
		task.spawn(pokaz, model)
	end
end
