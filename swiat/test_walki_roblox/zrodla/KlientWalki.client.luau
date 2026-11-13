--[[
	KlientWalki — kliencka połowa testu walki 3D (Script, RunContext = Client; działa z kontenera w Workspace).
	Spina wejścia z odtwarzaczem:
		• ProximityPrompt „Test walki 3D (prototyp)” na tablicy przy arenie (klawisz E / dotknięcie),
		• Sygnaly/StartTestu  (BindableEvent) — haczyk do testów automatycznych: Fire(opcje?) uruchamia cutscenkę
		  bez podchodzenia do tablicy; opcje opisane w OdtwarzaczWalki,
		• Sygnaly/PominTest   — to samo co przycisk „POMIŃ”,
		• Sygnaly/ZamknijTest — to samo co przycisk „Zamknij”.
	Sam nic nie liczy i nic nie wysyła poza prośbą o walkę (robi to odtwarzacz).
]]
if not game:GetService("RunService"):IsStudio() then
	return -- prototyp działa wyłącznie w Studio; w opublikowanej grze jest bezwładny
end

local Players = game:GetService("Players")
local ProximityPromptService = game:GetService("ProximityPromptService")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local sygnaly = kontener:WaitForChild("Sygnaly")
kontener:WaitForChild("Zdalne"):WaitForChild("RozpocznijWalke")
local Odtwarzacz = require(moduly:WaitForChild("OdtwarzaczWalki"))

local function uruchom(opcje)
	task.spawn(Odtwarzacz.uruchom, kontener, opcje)
end

-- Podpowiedź pojawia się i znika razem z doczytywaniem mapy, więc słuchamy usługi, a nie konkretnej instancji.
ProximityPromptService.PromptTriggered:Connect(function(podpowiedz: ProximityPrompt, gracz: Player)
	if gracz ~= Players.LocalPlayer then
		return
	end
	if podpowiedz.Name == "PodpowiedzWalki" and podpowiedz:IsDescendantOf(kontener) then
		uruchom(nil)
	end
end)

-- Po walce (zwłaszcza pominiętej) serwer przez chwilę nie przyjmie następnej: podpowiedź pokazuje odliczanie (zmiana lokalna).
task.spawn(function()
	while kontener.Parent do
		local podpowiedz = kontener:FindFirstChild("PodpowiedzWalki", true)
		if podpowiedz and podpowiedz:IsA("ProximityPrompt") then
			local zostalo = Odtwarzacz.wolnaZa()
			local tekst = if zostalo > 0 then string.format("Walcz! (za %d s)", math.ceil(zostalo)) else "Walcz!"
			if podpowiedz.ActionText ~= tekst then
				podpowiedz.ActionText = tekst
			end
		end
		task.wait(0.25)
	end
end)

sygnaly:WaitForChild("StartTestu").Event:Connect(function(opcje)
	uruchom(opcje)
end)
sygnaly:WaitForChild("PominTest").Event:Connect(function()
	Odtwarzacz.pomin()
end)
sygnaly:WaitForChild("ZamknijTest").Event:Connect(function()
	Odtwarzacz.zamknij()
end)

kontener:SetAttribute("KlientGotowy", true) -- lokalny znak dla testów: klient jest podpięty
