--!strict
--[[
	QuestyClient — wysuwana szuflada questów po prawej stronie ekranu (Paweł 25.11). GUI: HUD/QuestDrawer
	(src/gui/HUD.model.json, tools/hud_pety_build_gui.py). Zakładka ze strzałką wysuwa panel zza krawędzi ekranu
	i chowa go z powrotem; zastępuje dawny przycisk „Quests” w HUD.

	Treść: na razie TRZY PRZYKŁADOWE questy wpisane niżej (bez postępu i nagród po stronie serwera). Kanon mówi
	o zadaniach na czas z karczmy z licznikiem w HUD (B&C/Gra/Karczma (Questy).md, D-034) — ta szuflada jest na nie
	miejscem; podpięcie prawdziwych zadań czeka na decyzję (Pytania otwarte).

	Dla innych skryptów: ReplicatedStorage.QuestyPanel (BindableFunction, tylko klient)
	  :Invoke("ustaw", { { nazwa, opis, postep, cel, nagroda, waluta = "fish" | "gems", gotowe } … })  — do 3 wierszy
	  :Invoke("otworz") / :Invoke("zamknij")
]]
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local TS = game:GetService("TweenService")

local player = Players.LocalPlayer
local hud = player:WaitForChild("PlayerGui"):WaitForChild("HUD") :: ScreenGui
local drawer = hud:WaitForChild("QuestDrawer") :: Frame
local tab = drawer:WaitForChild("Tab") :: ImageButton
local WYSUN = tab.Image
local SCHOWAJ = (drawer:WaitForChild("TabOpenArt") :: ImageLabel).Image
local IKONY = { fish = "rbxassetid://76704302626777", gems = "rbxassetid://130974323293639" }
local MARGINES = 8
local RUCH = TweenInfo.new(0.28, Enum.EasingStyle.Quart, Enum.EasingDirection.Out)

type Quest = { nazwa: string, opis: string, postep: number, cel: number, nagroda: number, waluta: string, gotowe: boolean? }
local questy: { Quest } = {
	{ nazwa = "FOREST PATROL", opis = "Defeat monsters", postep = 0, cel = 10, nagroda = 120, waluta = "fish" },
	{ nazwa = "EGG HUNTER", opis = "Hatch eggs", postep = 0, cel = 2, nagroda = 300, waluta = "fish" },
	{ nazwa = "LUCKY ROLL", opis = "Roll the dice", postep = 0, cel = 3, nagroda = 5, waluta = "gems" },
}

local function rysuj()
	for i = 1, 3 do
		local w = drawer:WaitForChild("Quest" .. i) :: Frame
		local q = questy[i]
		w.Visible = q ~= nil
		if q then
			local gotowe = q.gotowe or q.postep >= q.cel;
			(w:WaitForChild("Name") :: TextLabel).Text = q.nazwa;
			(w:WaitForChild("Progress") :: TextLabel).Text = string.format("%s  %d/%d", q.opis, math.min(q.postep, q.cel), q.cel);
			(w:WaitForChild("Check") :: TextLabel).Text = if gotowe then "✓" else "";
			(w:WaitForChild("Reward") :: TextLabel).Text = tostring(q.nagroda);
			(w:WaitForChild("RewardIcon") :: ImageLabel).Image = IKONY[q.waluta] or ""
		end
	end
end

local otwarta = false
local function ustaw(animuj: boolean)
	local y = drawer.Position.Y
	local cel = if otwarta then UDim2.new(1, -MARGINES, y.Scale, y.Offset) else UDim2.new(1, drawer.AbsoluteSize.X, y.Scale, y.Offset)
	tab.Image = if otwarta then SCHOWAJ else WYSUN
	if animuj then
		TS:Create(drawer, RUCH, { Position = cel }):Play()
	else
		drawer.Position = cel
	end
end

local skala = tab:FindFirstChildWhichIsA("UIScale")
tab.Activated:Connect(function()
	otwarta = not otwarta
	ustaw(true)
	if skala then
		skala.Scale = 0.88
		TS:Create(skala, TweenInfo.new(0.18, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	end
end)
drawer:GetPropertyChangedSignal("AbsoluteSize"):Connect(function()
	if not otwarta then
		ustaw(false)
	end
end)

local api = Instance.new("BindableFunction")
api.Name = "QuestyPanel"
api.OnInvoke = function(polecenie: any, a: any)
	if polecenie == "ustaw" and type(a) == "table" then
		questy = a
		rysuj()
	elseif polecenie == "otworz" or polecenie == "zamknij" then
		otwarta = polecenie == "otworz"
		ustaw(true)
	end
	return true
end
api.Parent = RS

-- bazar Karola (tablica w karczmie) woła dawny przycisk „Quests” — otwieramy wtedy szufladę
task.spawn(function()
	local e = RS:WaitForChild("HUDButtonPressed", 120)
	if e and e:IsA("BindableEvent") then
		e.Event:Connect(function(nazwa)
			if nazwa == "Quests" and not otwarta then
				otwarta = true
				ustaw(true)
			end
		end)
	end
end)

rysuj()
ustaw(false)
