# -*- coding: utf-8 -*-
"""Próba scenki wyklucia jajek (leśne jajo Pawła + jajka Bagna i Dżungli) w trybie Play. Sama włącza i wyłącza Play
(przez tools/studio_mcp.py — znacznik próby, bez prawdziwego zapisu), niczego nie zapisuje w miejscu i nie publikuje.

    python -B swiat/jajka_biomow/testy/proba_play.py <folder wyników POZA repo> [--studio <id>] [--bez-zrzutow]
                                                     [--tylko-lesne]

Warunki (tryb Edit): skrypty Pawła JajkoKoroweClient / JajkoKorowe w wersji z repo (po zmianie 26.11), Workspace/PetyProba,
StanGracza, Workspace/JajkaBiomowPodglad z JajkaBiomowSpoczynek; jajka biomów = modele z atrybutem JajkoId w tym
kontenerze (prawdziwe po `wdroz.py wstaw` albo atrapy z siatki leśnego jaja). Bez modelu jajko biomu jest pomijane.
Złoto (atrybut Gold, w grze „Rybki”) próba ustawia wprost, jak próby petów. Zrzuty: swiat/jajka_biomow/podglad/scenka_*.jpg
(lista graczy i czat schowane). Wyniki (mogą zawierać nazwę konta) tylko w folderze poza repo.

LISTA (OK / BŁĄD / ?):
  S00 Edit: skrypty Pawła w Studio = pliki repo; skrypty spoczynku w kontenerze; które jajka biomów stoją
  S01 Play: serwer petów gotowy, podpowiedzi E „Kup jajko” na punktach stojących jajek, inne E w pobliżu (wypisane)
  Dla każdego jajka (L = leśne, B = Bagno, D = Dżungla):
  x0 karta nad punktem E (tytuł, cena = cena jajka, szanse) i jajo przygotowane przez klienta (rdzeń, obrys)
  x1 spoczynek: jeden „pisarz” CFrame jaja (zmian na klatkę ≈ 1), blask żył 0,35–0,6
  x2 brak Złota (Gold = 0): prawdziwe E → odmowa, bez wyklucia i scenki, nic nie zabrane (zagroda może dopisać Rybkę)
  x3 zakup prawdziwym E: wyklucie TEGO jajka u kupującego, Gold − cena, scenka (kino), Wyklucie = true, quest „jajka” +1
  D4 drugi E w trakcie scenki (Dżungla; bez Dżungli — Bagno, bez obu — leśne) → odmowa „pęka”, Złoto zabrane raz
  x5 5 kliknięć (spacja): blask rośnie, rozpad (jajo → skorupy), odlot kawałka, słup; Final +1; w scence jeden pisarz
     (zmian CFrame na klatkę liczone tylko, gdy jajo widać — po BOOM jest niewidoczne i nikt go nie rusza)
  x6 kolory: światło rdzenia i iskry = KolorZyl jajka (leśne 53E89A), KolorRzadkosci = kolor trafionego peta
  x7 pet: napis nad petem = nazwa z wyklucia, model peta ze słupa, pet z puli TEGO jajka, cena zakupu = cena jajka
  x8 koniec: Wyklucie zdjęte, kino zamknięte, kamera Custom, ruch przywrócony, jajo z powrotem całe
  x9 (Bagno, Dżungla) ozdoby grają finał (odchylenie liści / trzcin, błysk kryształów, bąble)
  xA zakup „bez pokazu”: stary inkubator nie gra animacji, napis „Wykluł się…” dopiero po wyłonieniu peta
  xB po scence aktywny pet idzie za graczem (model „Pet <PetAktywny>” bliżej niż 12 st)
  xZ zrzuty: jajo świeci / pęka, rozpad ze słupem, pet (ocena człowieka: „?”)
  K01 konsola bez błędów skryptów jajek (JajkoKorowe*, JajkaBiomow*)
"""
import io
import json
import os
import re
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"),
           os.path.join(REPO, "swiat", "test_walki2", "testy")):
    if _s not in sys.path:
        sys.path.insert(0, _s)

PODGLAD = os.path.join(PAKIET, "podglad")
JAJKA = [
    {"tag": "L", "nazwa": "lesne", "id": "jajko_lesne", "kontener": "JajkoKorowePodglad", "model": "Jajko korowe",
     "punkt": "PunktJajka", "tytul": "FOREST EGG", "cena": 300, "zyl": "53E89A", "pas": None, "ozdoby": []},
    {"tag": "B", "nazwa": "bagno", "id": "jajko_bagienne", "kontener": "JajkaBiomowPodglad", "model": "Jajko Bagna",
     "punkt": "Punkt Jajko Bagna", "tytul": "SWAMP EGG", "cena": 750, "zyl": None, "pas": "BagnoPasGra",
     "ozdoby": ["Reeds", "Bubbles", "Crystals", "MushroomSpots"]},
    {"tag": "D", "nazwa": "dzungla", "id": "jajko_dzungli", "kontener": "JajkaBiomowPodglad", "model": "Jajko Dżungli",
     "punkt": "Punkt Jajko Dżungli", "tytul": "JUNGLE EGG", "cena": 1350, "zyl": None, "pas": "DzunglaPasGra",
     "ozdoby": ["BigLeaves", "Flowers", "Crystals", "Shards"]},
]
ZNANE_W_KONSOLI = ("Requester does not have permission for Asset",)

H = 'local H = game:GetService("HttpService") '
GR = H + 'local gracz = game:GetService("Players"):GetPlayers()[1] '
KOD = {
    "edit": H + r'''
local function fnv(s)
	s = s:gsub("\r\n", "\n")
	local h = 2166136261
	for i = 1, #s do
		h = bit32.bxor(h, string.byte(s, i))
		h = (bit32.lshift(h, 24) + h * 403) % 4294967296
	end
	return string.format("%08x:%d", h, #s)
end
local kl = game:GetService("StarterPlayer").StarterPlayerScripts.Client:FindFirstChild("JajkoKoroweClient")
local sv = game:GetService("ServerScriptService").Server:FindFirstChild("JajkoKorowe")
local b = workspace:FindFirstChild("JajkaBiomowPodglad")
local o = { klient = kl and fnv(kl.Source) or "brak", serwer = sv and fnv(sv.Source) or "brak", biomy = {},
	spoczynek = b ~= nil and b:FindFirstChild("JajkaBiomowSpoczynek") ~= nil,
	dane = b ~= nil and b:FindFirstChild("Moduly") ~= nil and b.Moduly:FindFirstChild("JajkaBiomowDane") ~= nil }
if b then
	for _, m in ipairs(b:GetChildren()) do
		if m:IsA("Model") and m:GetAttribute("JajkoId") then
			table.insert(o.biomy, { nazwa = m.Name, id = m:GetAttribute("JajkoId"), atrapa = m:GetAttribute("Atrapa") == true })
		end
	end
end
return H:JSONEncode(o)''',
    "gotowy_klient": 'local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)',
    "bez_nazwy": ('local SG = game:GetService("StarterGui") for _, t in { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Chat } do '
                  'pcall(function() SG:SetCoreGuiEnabled(t, false) end) end return "ok"'),
    "wybor_klasy": (H + 'local p = game:GetService("Players").LocalPlayer '
                    'local g = p.PlayerGui:FindFirstChild("ClassSelect") local hud = p.PlayerGui:FindFirstChild("HUD") '
                    'return H:JSONEncode({ ekran = g ~= nil and g.Enabled, hud = hud ~= nil and hud.Enabled, '
                    'klasa = p:GetAttribute("Class") or false })'),
    "zmien_klase": 'game:GetService("ReplicatedStorage"):WaitForChild("ChooseClass"):FireServer("Warrior") return "ok"',
    "podpowiedzi": H + r'''
local o = { punkty = {}, blisko = {} }
for _, sc in ipairs({ { "JajkoKorowePodglad", "PunktJajka" }, { "JajkaBiomowPodglad", "Punkt Jajko Bagna" },
	{ "JajkaBiomowPodglad", "Punkt Jajko Dżungli" } }) do
	local k = workspace:FindFirstChild(sc[1])
	local p = k and k:FindFirstChild(sc[2])
	local pp = p and p:FindFirstChild("PodpowiedzJajka")
	o.punkty[sc[2]] = if pp then { akcja = pp.ActionText, obiekt = pp.ObjectText, zasieg = pp.MaxActivationDistance,
		pos = { p.Position.X, p.Position.Y, p.Position.Z } } else false
end
for _, d in ipairs(workspace:GetDescendants()) do
	if d:IsA("ProximityPrompt") and d.Name ~= "PodpowiedzJajka" and d.Parent and d.Parent:IsA("BasePart") then
		for nazwa, w in pairs(o.punkty) do
			if w then
				local dist = (d.Parent.Position - Vector3.new(w.pos[1], w.pos[2], w.pos[3])).Magnitude
				if dist < 20 then
					table.insert(o.blisko, { przy = nazwa, akcja = d.ActionText, obiekt = d.ObjectText,
						odl = math.floor(dist * 10) / 10, zasieg = d.MaxActivationDistance, klawisz = tostring(d.KeyboardKeyCode) })
				end
			end
		end
	end
end
o.serwerPetow = workspace:FindFirstChild("PetyProba") ~= nil and workspace.PetyProba:GetAttribute("SerwerPetowGotowy") == true
return H:JSONEncode(o)''',
    "miejsce": H + r'''
local k = workspace:FindFirstChild("__K__")
local m = k and k:FindFirstChild("__M__")
if not m then return H:JSONEncode({ brak = true }) end
local cf = m:GetPivot()
local lv = cf.LookVector
local zyl = m:GetAttribute("KolorZyl")
return H:JSONEncode({ p = { cf.Position.X, cf.Position.Y, cf.Position.Z }, przod = { lv.X, lv.Z },
	zyl = if typeof(zyl) == "Color3" then zyl:ToHex() else false })''',
    "przestaw": GR + r'''
local p = Vector3.new(__X__, __Y__, __Z__)
pcall(function() gracz:RequestStreamAroundAsync(p, 8) end)
local hrp = gracz.Character.HumanoidRootPart
hrp.Parent:PivotTo(CFrame.lookAt(p, Vector3.new(__LX__, p.Y, __LZ__)))
hrp.AssemblyLinearVelocity = Vector3.zero
return "ok"''',
    "bramy": GR + r'''
local o = {}
for _, n in ipairs({ "LasPasGra", "BagnoPasGra" }) do
	local k = workspace:FindFirstChild(n)
	local ok, w = pcall(function() return k.Sygnaly.SterowaniePasa:Invoke("otworzBrame") end)
	o[n] = ok and tostring(w) or "błąd"
end
gracz:SetAttribute("PokonalStraznikaBagna", true)
return H:JSONEncode(o)''',
    "przelot": ('local k = workspace:FindFirstChild("__K__") local lp = game:GetService("Players").LocalPlayer '
                'local h = lp.Character and lp.Character:FindFirstChild("HumanoidRootPart") '
                'local p = k and k:FindFirstChild("Sygnaly") and (k.Sygnaly.SterowaniePasaKlienta:Invoke("stan") or {}).przelot '
                'return tostring((p ~= nil and p ~= false) or (h ~= nil and h.Anchored) or '
                'workspace.CurrentCamera.CameraType ~= Enum.CameraType.Custom)'),
    "klient_stan": H + r'''
local pg = game:GetService("Players").LocalPlayer.PlayerGui
local o = { karty = {}, jajko = false }
for _, b in ipairs(pg:GetChildren()) do
	if b.Name == "SzanseJajka" and b:IsA("BillboardGui") then
		local f = b:FindFirstChildWhichIsA("ImageLabel")
		local w = { adornee = if b.Adornee then b.Adornee.Name else false, wlaczona = b.Enabled }
		if f then
			for _, n in ipairs({ "Tytul", "Cena", "Szansa1", "Szansa2", "Szansa3", "Szansa4", "Szansa5", "Pet1", "Komunikat" }) do
				local x = f:FindFirstChild(n)
				w[n] = if x then x.Text else false
			end
		end
		table.insert(o.karty, w)
	end
end
local k = workspace:FindFirstChild("__K__")
local m = k and k:FindFirstChild("__M__")
if m then
	o.jajko = { rdzen = m:FindFirstChild("Rdzen") ~= nil, obrys = m:FindFirstChild("ObrysKomiksowy") ~= nil,
		egg = m:FindFirstChild("Egg") ~= nil }
end
return H:JSONEncode(o)''',
    "gold": GR + 'return H:JSONEncode({ gold = gracz:GetAttribute("Gold") or 0 })',
    "ustaw_gold": GR + 'gracz:SetAttribute("Gold", __N__) return "ok"',
    "quest": H + r'''
local SS = game:GetService("ServerStorage")
local q = SS:FindFirstChild("QuestPostep")
local f = SS:FindFirstChild("ProbaScenkiJajekSerwer")
if not f then
	f = Instance.new("Folder")
	f.Name = "ProbaScenkiJajekSerwer"
	f:SetAttribute("jajka", 0)
	f.Parent = SS
	if q and q:IsA("BindableEvent") then
		q.Event:Connect(function(_, licznik, ile)
			if licznik == "jajka" then
				f:SetAttribute("jajka", (f:GetAttribute("jajka") or 0) + (tonumber(ile) or 0))
			end
		end)
	end
end
return H:JSONEncode({ jajka = f:GetAttribute("jajka"), sygnal = q ~= nil })''',
    "zakup": H + r'''
local k = workspace.PetyProba
local s = tostring(k:GetAttribute("OstatniZakup") or "")
local j, p, c = string.match(s, ":([%w_]+):([%w_]+):(%d+)z$")
local D = require(k.Moduly.DanePetow)
local pula = {}
for _, jj in ipairs(D.jajka) do
	if jj.id == j then
		for _, sz in ipairs(jj.szanse) do
			table.insert(pula, sz.pet)
		end
	end
end
return H:JSONEncode({ jajko = j or false, pet = p or false, cena = tonumber(c) or false, wPuli = table.find(pula, p) ~= nil,
	pula = pula, licznik = k:GetAttribute("LicznikZakupow") or 0 })''',
    "rejestrator": H + r'''
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local lp = game:GetService("Players").LocalPlayer
local f = RS:FindFirstChild("ProbaScenkiJajek")
if not f then
	f = Instance.new("Folder")
	f.Name = "ProbaScenkiJajek"
	f.Parent = RS
end
local nr = (f:GetAttribute("nr") or 0) + 1
f:SetAttribute("nr", nr)
local k = workspace:FindFirstChild("__K__")
local m = k and k:FindFirstChild("__M__")
if not (m and m:FindFirstChild("Egg")) then
	return H:JSONEncode({ blad = "brak modelu" })
end
local egg = m.Egg
local OZDOBY = { __OZDOBY__ }
local function hex(c)
	return if typeof(c) == "Color3" then c:ToHex() else nil
end
local t0 = os.clock()
local o = { nr = nr, odmowy = {}, wyklucia = {}, final0 = m:GetAttribute("Final") or 0, finalMax = m:GetAttribute("Final") or 0,
	zapisy = { spoczynek = 0, scenka = 0 }, klatki = { spoczynek = 0, scenka = 0, scenkaJajo = 0 },
	emisja = { spoczynek = { 99, -1 }, scenka = { 99, -1 } }, ozdoby = {} }
local sa = egg:FindFirstChildWhichIsA("SurfaceAppearance")
local domy = {}
for _, n in ipairs(OZDOBY) do
	local c = m:FindFirstChild(n)
	if c and c:IsA("BasePart") then
		domy[n] = { cf = c.CFrame, kolor = c.Color }
		o.ozdoby[n] = { katSpoczynek = 0, katFinal = 0, kolorFinal = 0, przezrFinal = c.Transparency }
	end
end
local function faza()
	return if m:GetAttribute("Wyklucie") == true then "scenka" else "spoczynek"
end
local pol = {}
table.insert(pol, egg:GetPropertyChangedSignal("CFrame"):Connect(function()
	o.zapisy[faza()] += 1
end))
table.insert(pol, RS.JajkoKoroweZdarzenia.OnClientEvent:Connect(function(rodzaj, a, b)
	if rodzaj == "wyklucie" and type(b) == "table" then
		table.insert(o.wyklucia, { jajko = b.jajko or false, pet = b.pet, nazwa = b.nazwa, kolor = b.kolor,
			rzadkosc = b.rzadkosc, moje = a == lp.UserId, t = os.clock() - t0 })
	elseif rodzaj == "odmowa" then
		table.insert(o.odmowy, { tekst = tostring(a), jajko = b or false, t = os.clock() - t0 })
	end
end))
local shTR, shB = m:FindFirstChild("ShellTopRight"), m:FindFirstChild("ShellBottom")
local trDom = shTR and shTR.CFrame
table.insert(pol, RunService.RenderStepped:Connect(function()
	local t = os.clock() - t0
	local fz = faza()
	o.klatki[fz] += 1
	if fz == "scenka" and egg.Transparency < 1 then
		o.klatki.scenkaJajo += 1
	end
	if sa then
		local e = (sa :: any).EmissiveStrength
		local r = o.emisja[fz]
		r[1], r[2] = math.min(r[1], e), math.max(r[2], e)
	end
	if fz == "scenka" and not o.tWyklucie then
		o.tWyklucie = t
	end
	if fz ~= "scenka" and o.tWyklucie and not o.tKoniecWyklucia then
		o.tKoniecWyklucia = t
	end
	local fin = m:GetAttribute("Final") or 0
	if fin > o.finalMax then
		o.finalMax, o.tFinal = fin, t
	end
	o.kolorRzadkosci = hex(m:GetAttribute("KolorRzadkosci")) or o.kolorRzadkosci
	local pg = lp:FindFirstChild("PlayerGui")
	local kino = pg and pg:FindFirstChild("KinoJajka")
	if kino and not o.tKino then
		o.tKino = t
	end
	if not kino and o.tKino and not o.tKinoKoniec then
		o.tKinoKoniec = t
	end
	if kino then
		local hum = lp.Character and lp.Character:FindFirstChildOfClass("Humanoid")
		o.predkoscWKinie = hum and hum.WalkSpeed
		o.kameraWKinie = tostring(workspace.CurrentCamera.CameraType)
	end
	if egg.Transparency >= 1 and not o.tRozpad then
		o.tRozpad = t
	end
	if shB and shB.Transparency < 0.5 and not o.tSkorupa then
		o.tSkorupa = t
	end
	if shTR and trDom and (shTR.Position - trDom.Position).Magnitude > 1 and not o.tOdlot then
		o.tOdlot = t
	end
	local slup = m:FindFirstChild("Slup swiatla")
	if slup and slup.Transparency < 0.2 and not o.tSlup then
		o.tSlup = t
	end
	local rdzen = m:FindFirstChild("Rdzen")
	if rdzen then
		local sw = rdzen:FindFirstChild("SwiatloRdzenia")
		if sw and not o.tFinal then
			o.swiatloPrzed = hex(sw.Color)
		end
		local em = rdzen:FindFirstChildWhichIsA("ParticleEmitter")
		if em and not o.iskryKoniec then
			local kp = em.Color.Keypoints
			o.iskryKoniec = hex(kp[#kp].Value)
		end
		if rdzen.Transparency < 1 and not o.tRdzen then
			o.tRdzen, o.rdzenKolor = t, hex(rdzen.Color)
		end
	end
	local pk = pg and pg:FindFirstChild("PetyProba")
	local kom = pk and pk:FindFirstChild("Komunikat")
	if kom and kom:IsA("TextLabel") and kom.Visible and not o.tNapisPetow
		and (string.find(kom.Text, "Wykluł się", 1, true) or string.find(kom.Text, "Kopia peta", 1, true)) then
		o.tNapisPetow, o.napisPetow = t, kom.Text
	end
	local kp = workspace:FindFirstChild("PetyProba")
	local lok = kp and kp:FindFirstChild("PetyLokalne")
	if lok and (lok:FindFirstChild("Jajko wyklucie") or lok:FindFirstChild("Pet wyklucie")) and not o.tAnimInkubatora then
		o.tAnimInkubatora = t
	end
	if not o.tPet and workspace:FindFirstChild("PetZJajka") then
		o.tPet = t
	end
	local napisy = pg and pg:FindFirstChild("PetZJajkaNapisy")
	if napisy and not o.petNapisy then
		local l = {}
		for _, x in ipairs(napisy:GetChildren()) do
			if x:IsA("TextLabel") then
				table.insert(l, x.Text)
			end
		end
		o.petNapisy = l
	end
	for n, d in pairs(domy) do
		local c = m:FindFirstChild(n)
		if c then
			local kat = math.deg(math.acos(math.clamp(c.CFrame.UpVector:Dot(d.cf.UpVector), -1, 1)))
			local r = o.ozdoby[n]
			if o.tFinal then
				r.katFinal = math.max(r.katFinal, kat)
				r.kolorFinal = math.max(r.kolorFinal, math.abs(c.Color.R - d.kolor.R) + math.abs(c.Color.G - d.kolor.G)
					+ math.abs(c.Color.B - d.kolor.B))
				r.przezrFinal = math.max(r.przezrFinal, c.Transparency)
			else
				r.katSpoczynek = math.max(r.katSpoczynek, kat)
			end
		end
	end
end))
task.spawn(function()
	while os.clock() - t0 < 150 and f:GetAttribute("stop") ~= nr do
		f:SetAttribute("wynik", H:JSONEncode(o))
		task.wait(0.25)
	end
	for _, c in ipairs(pol) do
		c:Disconnect()
	end
	o.koniec = true
	o.jajoPo = egg.Transparency
	o.kameraPo = tostring(workspace.CurrentCamera.CameraType)
	local hum = lp.Character and lp.Character:FindFirstChildOfClass("Humanoid")
	o.predkoscPo = hum and hum.WalkSpeed
	o.wyklucieAtrPo = tostring(m:GetAttribute("Wyklucie"))
	f:SetAttribute("wynik", H:JSONEncode(o))
end)
return H:JSONEncode({ nr = nr })''',
    "towarzysz": H + r'''
local lp = game:GetService("Players").LocalPlayer
local a = lp:GetAttribute("PetAktywny")
local kp = workspace:FindFirstChild("PetyProba")
local lok = kp and kp:FindFirstChild("PetyLokalne")
local m = if a and lok then lok:FindFirstChild("Pet " .. a) else nil
local hrp = lp.Character and lp.Character:FindFirstChild("HumanoidRootPart")
local odl = if m and hrp then (m:GetPivot().Position - hrp.Position).Magnitude else false
return H:JSONEncode({ aktywny = a or false, model = m ~= nil, odl = odl })''',
    "rejestr_czytaj": ('local f = game:GetService("ReplicatedStorage"):FindFirstChild("ProbaScenkiJajek") '
                       'return f and f:GetAttribute("wynik") or "{}"'),
    "rejestr_stop": ('local f = game:GetService("ReplicatedStorage"):FindFirstChild("ProbaScenkiJajek") '
                     'if f then f:SetAttribute("stop", f:GetAttribute("nr")) end return "ok"'),
}


def podstaw(kod, **zm):
    for k, v in zm.items():
        kod = kod.replace("__%s__" % k, str(v))
    return kod


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def stosunek(z, k):
    return round(z / k, 2) if k else None


def main():
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    try:
        w_repo = os.path.commonpath([os.path.normcase(wyj), os.path.normcase(REPO)]) == os.path.normcase(REPO)
    except ValueError:
        w_repo = False
    if w_repo:
        sys.exit("Folder wyników leży w repozytorium (wyniki mogą zawierać nazwę konta) — podaj folder poza repo")
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    bez_zrzutow = "--bez-zrzutow" in argv
    tylko_lesne = "--tylko-lesne" in argv
    os.makedirs(wyj, exist_ok=True)
    from cel_studio import wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    try:
        from czuwanie import nie_usypiaj  # noqa: E402
    except ImportError:
        def nie_usypiaj():
            return False
    try:
        from PIL import Image  # noqa: E402
    except ImportError:
        Image = None

    WYNIKI, LISTA = {}, []

    def zapisz(klucz, wartosc):
        WYNIKI[klucz] = wartosc
        with open(os.path.join(wyj, "wyniki.json"), "w", encoding="utf-8") as f:
            json.dump(WYNIKI, f, ensure_ascii=False, indent=1)

    def punkt(kod, ok, opis):
        LISTA.append((kod, "OK" if ok is True else ("BŁĄD" if ok is False else "?"), opis))
        log("%s %s — %s" % (kod, LISTA[-1][1], opis))
        with open(os.path.join(wyj, "lista.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join("%s %-4s %s" % x for x in LISTA) + "\n")

    with StudioMCP(timeout=180) as s:
        sid = wybierz_studio(s, studio)

        def call(n, a=None, timeout=None):
            d = dict(a or {})
            d["studio_id"] = sid
            return s.call(n, d, timeout=timeout)

        def luau(kod, dm, proby=3):
            for i in range(proby):
                try:
                    r = call("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=120)
                    if r["is_error"]:
                        raise StudioError(r["text"][:800])
                    return r["text"].strip()
                except Exception as e:  # noqa: BLE001 — Studio czasem nie odpowiada chwilę
                    if i == proby - 1:
                        raise
                    log("luau: ponawiam po błędzie:", str(e)[:200])
                    time.sleep(6)

        def js(kod, dm):
            w = json.loads(luau(kod, dm) or "{}")
            return {} if w == [] else w

        def czekaj_na(warunek, limit, co=0.5):
            koniec = time.time() + limit
            while time.time() < koniec:
                w = warunek()
                if w:
                    return w
                time.sleep(co)
            return None

        def nacisnij(klawisz):
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": klawisz}]})

        def zrzut(nazwa):
            if bez_zrzutow:
                return None
            nie_usypiaj()
            t0 = time.time()
            r = call("screen_capture", {"capture_id": "jajka_" + nazwa}, timeout=150)
            dl = round(time.time() - t0, 1)
            if r["is_error"] or not r.get("images"):
                log("zrzut %s: BŁĄD %s" % (nazwa, r["text"][:120]))
                return None
            dane = r["images"][0]
            if Image is not None:
                im = Image.open(io.BytesIO(dane)).convert("RGB")
                if im.width > 1280:
                    im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
                im.save(os.path.join(PODGLAD, nazwa + ".jpg"), "JPEG", quality=85)
            else:
                with open(os.path.join(PODGLAD, nazwa + ".png"), "wb") as f:
                    f.write(dane)
            log("zrzut", nazwa, "(%.1f s)" % dl)
            return dl

        def rejestr():
            return json.loads(luau(KOD["rejestr_czytaj"], "Client") or "{}")

        def gold():
            return js(KOD["gold"], "Server").get("gold")

        nie_usypiaj()
        if "Current Studio Mode: Edit" not in call("get_studio_state")["text"]:
            sys.exit("Studio nie jest w trybie Edit — ta próba sama włącza Play")

        # ---------------------------------------------------------------- S00
        sys.path.insert(0, os.path.join(REPO, "tools"))

        def fnv(p):
            with open(p, "rb") as f:
                b = f.read().replace(b"\r\n", b"\n")
            h = 2166136261
            for c in b:
                h ^= c
                h = (h * 16777619) % 4294967296
            return "%08x:%d" % (h, len(b))
        e0 = js(KOD["edit"], "Edit")
        repo_k = fnv(os.path.join(REPO, "src", "client", "JajkoKoroweClient.client.luau"))
        repo_s = fnv(os.path.join(REPO, "src", "server", "JajkoKorowe.server.luau"))
        zapisz("S00", {"edit": e0, "repo": {"klient": repo_k, "serwer": repo_s}})
        biomy_w = {b["nazwa"]: b for b in e0.get("biomy", [])}
        jajka = [j for j in JAJKA if j["tag"] == "L" or (not tylko_lesne and j["model"] in biomy_w)]
        punkt("S00", e0.get("klient") == repo_k and e0.get("serwer") == repo_s and e0.get("spoczynek") and e0.get("dane"),
              "skrypty Pawła = repo: klient %s, serwer %s; spoczynek %s, dane %s; jajka biomów: %s" % (
                  e0.get("klient") == repo_k, e0.get("serwer") == repo_s, e0.get("spoczynek"), e0.get("dane"),
                  ", ".join("%s (%s%s)" % (b["nazwa"], b["id"], ", atrapa" if b["atrapa"] else "") for b in e0.get("biomy", []))
                  or "brak"))

        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        try:
            czekaj_na(lambda: "Client" in call("get_studio_state")["text"] and luau(KOD["gotowy_klient"], "Client") == "true",
                      90, 1.0)
            luau(KOD["bez_nazwy"], "Client")
            time.sleep(3)
            czekaj_na(lambda: js(KOD["wybor_klasy"], "Client").get("ekran"), 30, 1.0)
            wk = js(KOD["wybor_klasy"], "Client")
            for _ in range(10):
                if not wk.get("ekran") and wk.get("klasa") and wk.get("hud"):
                    break
                nacisnij("Return")
                time.sleep(1.5)
                wk = js(KOD["wybor_klasy"], "Client")
            if not wk.get("klasa"):
                luau(KOD["zmien_klase"], "Client")
                time.sleep(2)
            luau(KOD["bez_nazwy"], "Client")
            # ---------------------------------------------------------------- S01
            pp = czekaj_na(lambda: (lambda a: a if a.get("serwerPetow") and a["punkty"].get("PunktJajka") else None)(
                js(KOD["podpowiedzi"], "Server")), 60, 1.0) or js(KOD["podpowiedzi"], "Server")
            q0 = js(KOD["quest"], "Server")
            zapisz("S01", {"podpowiedzi": pp, "quest": q0, "klasa": wk})
            ok_pp = all(pp.get("punkty", {}).get(j["punkt"]) for j in jajka)
            bliskie_e = [b for b in pp.get("blisko", []) if b["klawisz"] == "Enum.KeyCode.E"]
            punkt("S01", bool(pp.get("serwerPetow")) and ok_pp and q0.get("sygnal") is True,
                  "serwer petów %s; podpowiedzi E: %s; inne E < 20 st: %s; QuestPostep %s" % (
                      pp.get("serwerPetow"), {k: (v["obiekt"] if v else None) for k, v in pp.get("punkty", {}).items()},
                      [(b["przy"], b["akcja"], b["odl"], b["zasieg"]) for b in bliskie_e] or "brak", q0.get("sygnal")))

            brama = False
            drugi_e = next((j["tag"] for j in reversed(jajka)), "L")
            for J in jajka:
                T = J["tag"]
                mj = js(podstaw(KOD["miejsce"], K=J["kontener"], M=J["model"]), "Server")
                if mj.get("brak"):
                    punkt(T + "0", False, "brak modelu %s na serwerze" % J["model"])
                    continue
                p, pz = mj["p"], mj["przod"]
                stoi = (p[0] + pz[0] * 5.0, p[1] + 3.0, p[2] + pz[1] * 5.0)

                def do_jajka():
                    luau(podstaw(KOD["przestaw"], X=stoi[0], Y=stoi[1], Z=stoi[2], LX=p[0], LZ=p[2]), "Server")
                    time.sleep(1.0)
                if J["pas"]:
                    if not brama:
                        zapisz("bramy", js(KOD["bramy"], "Server"))
                        brama = True
                    do_jajka()
                    czekaj_na(lambda: luau(podstaw(KOD["przelot"], K=J["pas"]), "Client") == "true", 6, 0.4)
                    czekaj_na(lambda: luau(podstaw(KOD["przelot"], K=J["pas"]), "Client") == "false", 45, 1.0)
                do_jajka()
                # ------------------------------------------------ x0 karta i przygotowanie
                ks = czekaj_na(lambda: (lambda a: a if (a.get("jajko") or {}).get("rdzen") and any(
                    k.get("adornee") == J["punkt"] and k.get("Cena") for k in a.get("karty", [])) else None)(
                    js(podstaw(KOD["klient_stan"], K=J["kontener"], M=J["model"]), "Client")), 25, 1.0) \
                    or js(podstaw(KOD["klient_stan"], K=J["kontener"], M=J["model"]), "Client")
                karta = next((k for k in ks.get("karty", []) if k.get("adornee") == J["punkt"]), {})
                szanse = [karta.get("Szansa%d" % i) for i in range(1, 6) if karta.get("Szansa%d" % i)]
                zapisz(T + "0", ks)
                punkt(T + "0", karta.get("Tytul") == J["tytul"] and karta.get("Cena") == str(J["cena"]) and len(szanse) >= 3
                      and (ks.get("jajko") or {}).get("rdzen") is True and (ks.get("jajko") or {}).get("obrys") is True,
                      "karta „%s”, cena %s (ma być %d), szanse %s; jajo: %s; kart u gracza %d" % (
                          karta.get("Tytul"), karta.get("Cena"), J["cena"], szanse, ks.get("jajko"), len(ks.get("karty", []))))
                # ------------------------------------------------ x1 spoczynek
                nr = js(podstaw(KOD["rejestrator"], K=J["kontener"], M=J["model"],
                                OZDOBY=", ".join('"%s"' % o for o in J["ozdoby"])), "Client")
                if nr.get("blad"):
                    punkt(T + "1", False, "rejestrator: %s" % nr["blad"])
                    continue
                time.sleep(2.5)
                r = rejestr()
                st_sp = stosunek(r["zapisy"]["spoczynek"], r["klatki"]["spoczynek"])
                em = r["emisja"]["spoczynek"]
                punkt(T + "1", st_sp is not None and 0.7 <= st_sp <= 1.3 and 0.35 <= em[0] and em[1] <= 0.6,
                      "spoczynek: zmian CFrame jaja na klatkę %s (%d/%d), blask %.2f–%.2f" % (
                          st_sp, r["zapisy"]["spoczynek"], r["klatki"]["spoczynek"], em[0], em[1]))
                # ------------------------------------------------ x2 brak Złota
                luau(podstaw(KOD["ustaw_gold"], N=0), "Server")
                time.sleep(0.5)
                nacisnij("E")
                time.sleep(1.8)
                r = rejestr()
                g2 = gold()
                ks2 = js(podstaw(KOD["klient_stan"], K=J["kontener"], M=J["model"]), "Client")
                kom = next((k.get("Komunikat") for k in ks2.get("karty", []) if k.get("adornee") == J["punkt"]), None)
                zapisz(T + "2", {"rejestr": r, "gold": g2, "komunikat": kom})
                punkt(T + "2", len(r["odmowy"]) >= 1 and not r["wyklucia"] and not r.get("tKino") and not r.get("tWyklucie")
                      and g2 is not None and g2 <= 10, "odmowy %s, komunikat na karcie %r, wykluć %d, kino %s, Gold %s (0 + ewentualne Rybki z zagrody)" % (
                          [o["tekst"] for o in r["odmowy"]], kom, len(r["wyklucia"]), r.get("tKino"), g2))
                # ------------------------------------------------ x3 zakup prawdziwym E
                q_przed = js(KOD["quest"], "Server").get("jajka")
                start = J["cena"] + 100
                luau(podstaw(KOD["ustaw_gold"], N=start), "Server")
                time.sleep(0.5)
                odm_przed = len(r["odmowy"])
                nacisnij("E")
                time.sleep(1.0)
                g3 = gold()
                r = rejestr()
                w = next((x for x in r["wyklucia"] if x.get("moje")), None)
                q_po = js(KOD["quest"], "Server").get("jajka")
                zapisz(T + "3", {"rejestr": r, "gold": g3, "quest": [q_przed, q_po]})
                punkt(T + "3", w is not None and w.get("jajko") == J["id"] and g3 is not None
                      and start - J["cena"] <= g3 <= start - J["cena"] + 10 and r.get("tKino") is not None
                      and r.get("tWyklucie") is not None and q_po == (q_przed or 0) + 1,
                      "wyklucie %s (pet %s), Gold %s → %s (cena %d), kino %s, Wyklucie od %s s, quest jajka %s → %s" % (
                          w and w.get("jajko"), w and w.get("pet"), start, g3, J["cena"], r.get("tKino") is not None,
                          r.get("tWyklucie"), q_przed, q_po))
                # ------------------------------------------------ D4 drugi E w trakcie scenki
                if T == drugi_e:
                    nacisnij("E")
                    time.sleep(1.0)
                    r = rejestr()
                    g4 = gold()
                    nowe = [o["tekst"] for o in r["odmowy"][odm_przed:]]
                    zapisz(T + "4", {"odmowy": nowe, "gold": g4, "wyklucia": len(r["wyklucia"])})
                    punkt(T + "4", any("pęka" in t for t in nowe) and g4 == g3 and len(r["wyklucia"]) == 1,
                          "drugi E w scence: odmowy %s, Gold %s (było %s), wykluć %d" % (nowe, g4, g3, len(r["wyklucia"])))
                else:
                    time.sleep(0.4)
                # ------------------------------------------------ x5 kliknięcia
                for _ in range(4):
                    nacisnij("Space")
                    time.sleep(0.8)
                dl1 = zrzut("scenka_%s_1_pekanie" % J["nazwa"])
                r_przed_boom = rejestr()
                nacisnij("Space")
                time.sleep(0.5)
                dl2 = zrzut("scenka_%s_2_slup" % J["nazwa"])
                time.sleep(1.7)   # pet wznosi się 1,4–2,3 s po BOOM, napis nad nim od ok. 2,1 s
                dl3 = zrzut("scenka_%s_3_pet" % J["nazwa"])
                czekaj_na(lambda: (lambda a: a if a.get("tKoniecWyklucia") and a.get("tKinoKoniec") else None)(rejestr()), 40, 1.0)
                time.sleep(1.0)
                luau(KOD["rejestr_stop"], "Client")
                time.sleep(0.8)
                r = rejestr()
                zapisz(T + "5", {"rejestr": r, "przed_boom": r_przed_boom, "zrzuty_s": [dl1, dl2, dl3]})
                st_sc = stosunek(r["zapisy"]["scenka"], r["klatki"].get("scenkaJajo") or 0)
                es = r["emisja"]["scenka"]
                tw = r.get("tWyklucie") or 0
                ok5 = (es[1] >= 1.1 and all(r.get(k) and r[k] > tw for k in ("tRozpad", "tSkorupa", "tOdlot", "tSlup"))
                       and r["finalMax"] == r["final0"] + 1 and st_sc is not None and 0.7 <= st_sc <= 1.3)
                punkt(T + "5", ok5, "blask w scence do %.2f (przed BOOM do %.2f); rozpad %s s, skorupy %s, odlot %s, słup %s, "
                      "Final %s → %s; zmian CFrame na klatkę scenki z widocznym jajem %s (%d/%d)" % (
                          es[1], r_przed_boom.get("emisja", {}).get("scenka", [0, 0])[1], r.get("tRozpad"), r.get("tSkorupa"),
                          r.get("tOdlot"), r.get("tSlup"), r["final0"], r["finalMax"], st_sc, r["zapisy"]["scenka"],
                          r["klatki"].get("scenkaJajo") or 0))
                # ------------------------------------------------ x6 kolory
                zyl = (J["zyl"] or mj.get("zyl") or "").upper()
                kol_peta = ((w or {}).get("kolor") or "").upper()
                ok6 = ((r.get("swiatloPrzed") or "").upper() == zyl and (r.get("iskryKoniec") or "").upper() == zyl
                       and (r.get("kolorRzadkosci") or "").upper() == kol_peta)
                punkt(T + "6", ok6, "światło rdzenia przed finałem %s, iskry %s (KolorZyl %s); KolorRzadkosci %s (pet %s)" % (
                    r.get("swiatloPrzed"), r.get("iskryKoniec"), zyl, r.get("kolorRzadkosci"), kol_peta))
                # ------------------------------------------------ x7 pet
                zk = js(KOD["zakup"], "Server")
                napisy = r.get("petNapisy") or []
                zapisz(T + "7", {"zakup": zk, "napisy": napisy})
                punkt(T + "7", bool(napisy) and w is not None and napisy[0] == w.get("nazwa") and r.get("tPet") is not None
                      and zk.get("jajko") == J["id"] and zk.get("wPuli") is True and zk.get("pet") == (w or {}).get("pet")
                      and zk.get("cena") == J["cena"],
                      "napisy nad petem %s, model peta od %s s; zakup: jajko %s, pet %s (w puli %s), cena %s" % (
                          napisy, r.get("tPet"), zk.get("jajko"), zk.get("pet"), zk.get("wPuli"), zk.get("cena")))
                # ------------------------------------------------ x8 koniec
                ok8 = (r.get("tKoniecWyklucia") is not None and r.get("wyklucieAtrPo") == "nil" and r.get("tKinoKoniec")
                       and r.get("kameraPo") == "Enum.CameraType.Custom" and (r.get("predkoscPo") or 0) > 0
                       and r.get("jajoPo") == 0 and r.get("predkoscWKinie") == 0)
                punkt(T + "8", ok8, "Wyklucie %s → %s (scenka %.1f s), kino do %s s, kamera %s, ruch w kinie %s → %s, jajo %s" % (
                    r.get("tWyklucie"), r.get("wyklucieAtrPo"), (r.get("tKoniecWyklucia") or 0) - tw, r.get("tKinoKoniec"),
                    r.get("kameraPo"), r.get("predkoscWKinie"), r.get("predkoscPo"), r.get("jajoPo")))
                # ------------------------------------------------ xA bez spoilera (zakup „bez pokazu”)
                tn, tp = r.get("tNapisPetow"), r.get("tPet")
                okA = (r.get("tAnimInkubatora") is None and tn is not None and tp is not None and tn >= tp
                       and (w or {}).get("nazwa", "?") in (r.get("napisPetow") or ""))
                anim = "BYŁA od %s s" % r["tAnimInkubatora"] if r.get("tAnimInkubatora") is not None else "brak"
                punkt(T + "A", okA, "animacja starego inkubatora: %s; napis pakietu petów od %s s (BOOM %s s, pet "
                      "wyłania się od %s s): %r" % (anim, tn, r.get("tRozpad"), tp, r.get("napisPetow")))
                # ------------------------------------------------ xB pet za graczem po scence
                tw_ = czekaj_na(lambda: (lambda a: a if a.get("model") and a.get("odl") and a["odl"] < 12 else None)(
                    js(KOD["towarzysz"], "Client")), 8, 0.5) or js(KOD["towarzysz"], "Client")
                zapisz(T + "B", tw_)
                punkt(T + "B", bool(tw_.get("model")) and bool(tw_.get("odl")) and tw_["odl"] < 12,
                      "po scence: aktywny pet %s, model za graczem %s, odległość %s st" % (
                          tw_.get("aktywny"), tw_.get("model"), round(tw_["odl"], 1) if tw_.get("odl") else None))
                # ------------------------------------------------ x9 ozdoby
                if J["ozdoby"]:
                    oz = r.get("ozdoby") or {}
                    oz = oz if isinstance(oz, dict) else {}
                    ruch = [n for n, v in oz.items() if v["katFinal"] > v["katSpoczynek"] + 2]
                    blysk = [n for n, v in oz.items() if v["kolorFinal"] > 0.15]
                    pek = [n for n, v in oz.items() if v["przezrFinal"] > 0.9]
                    punkt(T + "9", bool(ruch) and bool(blysk),
                          "po finale: odchylone %s, błysk %s, pękły %s (szczegóły w wyniki.json)" % (ruch, blysk, pek))
                punkt(T + "Z", None, "zrzuty scenka_%s_1/2/3 (czas zrzutu %s s)" % (J["nazwa"], [dl1, dl2, dl3]))
                time.sleep(1.5)

            out = call("get_console_output")["text"]
            wzor = re.compile(r"(JajkoKorowe\w*|JajkaBiomow\w*):\d+:|Script '[^']*(JajkoKorowe|JajkaBiomow)|"
                              r"\[JajkoKorowe\]|\[JajkaBiomowSpoczynek\]")
            zle = [x for x in out.splitlines() if wzor.search(x) and not any(z in x for z in ZNANE_W_KONSOLI)]
            zapisz("K01", {"linie": zle[:30]})
            punkt("K01", not zle, "linii błędów/ostrzeżeń skryptów jajek w konsoli: %d" % len(zle))
        finally:
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
    zle = [x for x in LISTA if x[1] == "BŁĄD"]
    log("KONIEC: %d punktów — OK %d, BŁĄD %d, ? %d" % (len(LISTA), sum(1 for x in LISTA if x[1] == "OK"), len(zle),
                                                       sum(1 for x in LISTA if x[1] == "?")))
    return 1 if zle else 0


if __name__ == "__main__":
    sys.exit(main())
