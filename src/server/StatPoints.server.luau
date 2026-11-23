--[[
	StatPoints — WYŁĄCZONE (Paweł 23.11).
	Był to testowy przycisk „+” w oknie ekwipunku: ReplicatedStorage.AddStatPoint podnosił statystykę o 1 bez kosztu.
	Statystyki rosną teraz tylko z treningu i przedmiotów, więc przyciski „+” zniknęły z okna (EquipmentPanelClient),
	a serwer nie przyjmuje już darmowych punktów — inaczej każdy mógłby je sobie dodawać, wysyłając zdarzenie ręcznie.
	Zdarzenie zostaje (puste), żeby starsze skrypty, które na nie czekają, nie wisiały.
]]

local RS = game:GetService("ReplicatedStorage")

local remote = RS:FindFirstChild("AddStatPoint")
if not remote then
	remote = Instance.new("RemoteEvent")
	remote.Name = "AddStatPoint"
	remote.Parent = RS
end

remote.OnServerEvent:Connect(function()
	-- celowo nic: darmowe punkty statystyk wyłączone
end)
