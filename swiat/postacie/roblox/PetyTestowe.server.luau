-- Pety idące za graczem — TYLKO w Roblox Studio (Play). W opublikowanej grze nic nie robi.
-- Instalowany przez `python -B swiat/postacie/roblox_postac.py` jako Workspace/TestPostaci/PetyTestowe.
-- Przy psie, slimie i smoku pojawia się podpowiedź „Weź peta” (klawisz E albo dotknięcie). Pet rusza za graczem:
-- gdy gracz idzie, odtwarza klip ruchu (bieg, skok, lot), gdy stoi — spoczynek. Drugie naciśnięcie odsyła go na miejsce.
-- Do testów ze skryptu: kontener.WezPeta:Fire(gracz, "Pies") — weź albo odeślij.
-- To próba zachowania, nie system petów: ruch liczy serwer co klatkę (zakotwiczony korzeń przesuwany po CFrame),
-- bez omijania przeszkód i bez zapisu, kto ma jakiego peta.
local RunService = game:GetService("RunService")
if not RunService:IsStudio() then
	return
end
local KSP = game:GetService("KeyframeSequenceProvider")
local kontener = script.Parent

-- nazwa modelu -> klip ruchu, klip spoczynku, prędkość (studs/s), miejsce względem gracza (w prawo, do tyłu), unoszenie
local PETY = {
	Pies = { ruch = "bieg", spoczynek = "idle", predkosc = 15, bok = 3.0, tyl = 3.5, unoszenie = 0 },
	Slime = { ruch = "skok", spoczynek = "idle", predkosc = 10, bok = -3.5, tyl = 4.0, unoszenie = 0 },
	Smok = { ruch = "lot", spoczynek = "idle_lot", predkosc = 17, bok = 0.5, tyl = 6.0, unoszenie = 2.5 },
}
local BLISKO = 0.7 -- bliżej niż tyle studów od celu pet stoi
local DALEKO = 80 -- dalej niż tyle (np. po teleporcie gracza) pet przeskakuje do celu

local parametry = RaycastParams.new()
parametry.FilterType = Enum.RaycastFilterType.Exclude

local function podloze(punkt, zapas)
	local traf = workspace:Raycast(punkt + Vector3.new(0, 8, 0), Vector3.new(0, -40, 0), parametry)
	return traf and traf.Position.Y or zapas
end

local stany = {}

local function wczytaj(animator, ks)
	local anim = Instance.new("Animation")
	anim.Name = ks.Name
	anim.AnimationId = KSP:RegisterKeyframeSequence(ks)
	return animator:LoadAnimation(anim)
end

local function przelacz(stan, nazwa)
	if stan.gra == nazwa then
		return
	end
	for klucz, sciezka in stan.sciezki do
		if klucz == nazwa then
			sciezka:Play(0.15)
		elseif sciezka.IsPlaying then
			sciezka:Stop(0.15)
		end
	end
	stan.gra = nazwa
end

local function przygotuj(model, cfg)
	local korzen = model.PrimaryPart
	local kontroler = model:FindFirstChildWhichIsA("AnimationController")
	local animator = kontroler and kontroler:FindFirstChildWhichIsA("Animator")
	local saves = model:FindFirstChild("AnimSaves")
	if not korzen or not animator or not saves then
		return
	end
	local ruch, spoczynek = saves:FindFirstChild(cfg.ruch), saves:FindFirstChild(cfg.spoczynek)
	if not ruch or not spoczynek then
		return
	end
	local dom = korzen.CFrame
	local stan = {
		model = model,
		korzen = korzen,
		cfg = cfg,
		dom = dom,
		nadZiemia = dom.Position.Y - podloze(dom.Position, dom.Position.Y),
		wlasciciel = nil,
		wraca = false,
		gra = "",
		sciezki = { ruch = wczytaj(animator, ruch), spoczynek = wczytaj(animator, spoczynek) },
	}
	local pp = Instance.new("ProximityPrompt")
	pp.Name = "WezPeta"
	pp.ActionText = "Weź peta"
	pp.ObjectText = model.Name
	pp.HoldDuration = 0
	pp.MaxActivationDistance = 12
	pp.RequiresLineOfSight = false
	pp.Parent = korzen
	stan.podpowiedz = pp
	stany[model.Name] = stan
	return stan
end

local function wezAlboOdeslij(gracz, nazwa)
	local stan = stany[nazwa]
	if not stan or not gracz then
		return
	end
	if stan.wlasciciel == gracz then
		stan.wlasciciel = nil
		stan.wraca = true
		stan.podpowiedz.ActionText = "Weź peta"
	elseif stan.wlasciciel == nil then
		stan.wlasciciel = gracz
		stan.wraca = false
		stan.model:SetAttribute("Zajety", true) -- PokazAnimacji przestaje sterować tym modelem
		stan.podpowiedz.ActionText = "Odeślij"
	end
end

parametry.FilterDescendantsInstances = { kontener }
for nazwa, cfg in PETY do
	local model = kontener:FindFirstChild(nazwa)
	if model and model:IsA("Model") then
		local stan = przygotuj(model, cfg)
		if stan then
			stan.podpowiedz.Triggered:Connect(function(gracz)
				wezAlboOdeslij(gracz, nazwa)
			end)
		end
	end
end

local zdarzenie = Instance.new("BindableEvent")
zdarzenie.Name = "WezPeta"
zdarzenie.Event:Connect(wezAlboOdeslij)
zdarzenie.Parent = kontener

RunService.Heartbeat:Connect(function(dt)
	for _, stan in stany do
		local cel, przod
		local wl = stan.wlasciciel
		local cialo = wl and wl.Character and wl.Character:FindFirstChild("HumanoidRootPart")
		if wl and (not wl.Parent or not cialo) then
			stan.wlasciciel, stan.wraca = nil, true -- gracz wyszedł albo nie ma postaci: pet wraca
			stan.podpowiedz.ActionText = "Weź peta"
			cialo = nil
		end
		if cialo then
			parametry.FilterDescendantsInstances = { kontener, wl.Character }
			local cf = cialo.CFrame
			local p = cf.Position + cf.RightVector * stan.cfg.bok - cf.LookVector * stan.cfg.tyl
			local y = podloze(p, cf.Position.Y - 3) + stan.nadZiemia + stan.cfg.unoszenie
			cel, przod = Vector3.new(p.X, y, p.Z), cf.LookVector
		elseif stan.wraca then
			cel, przod = stan.dom.Position, stan.dom.LookVector
		end
		if cel then
			local poz = stan.korzen.Position
			local plasko = Vector3.new(cel.X - poz.X, 0, cel.Z - poz.Z)
			local odl = plasko.Magnitude
			local kierunek = stan.korzen.CFrame.LookVector
			local nowa
			if odl > DALEKO then
				nowa = cel
			elseif odl > BLISKO then
				local krok = math.min(odl, stan.cfg.predkosc * dt)
				kierunek = plasko.Unit
				local y = poz.Y + (cel.Y - poz.Y) * math.min(1, dt * 6)
				nowa = Vector3.new(poz.X + kierunek.X * krok, y, poz.Z + kierunek.Z * krok)
				przelacz(stan, "ruch")
			else
				nowa = Vector3.new(poz.X, poz.Y + (cel.Y - poz.Y) * math.min(1, dt * 6), poz.Z)
				local plaskiPrzod = Vector3.new(przod.X, 0, przod.Z)
				if plaskiPrzod.Magnitude > 0.01 then
					kierunek = kierunek:Lerp(plaskiPrzod.Unit, math.min(1, dt * 8))
				end
				przelacz(stan, "spoczynek")
				if stan.wraca then
					stan.wraca = false
					stan.korzen.CFrame = stan.dom
					przelacz(stan, "")
					stan.model:SetAttribute("Zajety", nil) -- oddaj model pokazowi animacji
					continue
				end
			end
			local plaskiKierunek = Vector3.new(kierunek.X, 0, kierunek.Z)
			if plaskiKierunek.Magnitude < 0.01 then
				plaskiKierunek = Vector3.new(0, 0, -1)
			end
			stan.korzen.CFrame = CFrame.lookAt(nowa, nowa + plaskiKierunek.Unit)
		end
	end
end)
