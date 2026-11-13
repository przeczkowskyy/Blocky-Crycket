#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola WSZYSTKICH klipów postaci z klocków w Roblox Studio (tryb Edit): dane kontra prawdziwy Animator.

    python -B swiat/postacie/roblox_klipy.py                 # wszystkie modele z wynik/_roblox/*_klocki.json
    python -B swiat/postacie/roblox_klipy.py --tylko rycerz,pies
    python -B swiat/postacie/roblox_klipy.py --zapisz        # dopisz tabelę do wynik/_roblox/klipy_kontrola.txt

Dla każdego klipu z `AnimSaves` (KeyframeSequence) i kilku klatek: klip jest rejestrowany, wczytywany przez Animator
postaci, ustawiany na czas klatki i przeliczany (`Animator:StepAnimations`). Potem dla każdego animowanego stawu
porównujemy `Motor6D.Transform` z wartością zapisaną w danych rigu (`<id>_klocki.json`, czyli z próbkami krzywych
Blendera po zamianie układu). To sprawdza całą drogę: dane → KeyframeSequence w Studio → Animator → staw.
Na końcu każda postać wraca do spoczynku przez klip neutralny, a narzędzie mierzy, czy naprawdę wróciła.
Dotyka tylko miejsca gry (PlaceId) i kontenera `Workspace/TestPostaci` z atrybutem `Wygenerowane`; niczego nie
zapisuje w miejscu. Kod wyjścia 1, gdy którykolwiek staw odbiega od danych albo postać nie wróciła do spoczynku.
"""
import argparse
import glob
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
sys.path.insert(0, os.path.join(REPO, "tools"))

KONTENER = "TestPostaci"
PLACE_ID = 129485428021967
TOLERANCJA_KAT = 0.05      # stopnie
TOLERANCJA_POZ = 0.005     # studs

KONTROLA = r'''
local HS = game:GetService("HttpService")
if game.PlaceId ~= __PLACE__ then
	return HS:JSONEncode({ stop = "to nie jest miejsce gry (PlaceId " .. tostring(game.PlaceId) .. ")" })
end
local kont = workspace:FindFirstChild("__KONTENER__")
if not kont or kont:GetAttribute("Wygenerowane") ~= true then
	return HS:JSONEncode({ stop = "brak kontenera __KONTENER__ z atrybutem Wygenerowane" })
end
local D = __DANE__
local model = kont:FindFirstChild(D.model)
local kontroler = model and model:FindFirstChild("AnimationController")
local animator = kontroler and kontroler:FindFirstChild("Animator")
local saves = model and model:FindFirstChild("AnimSaves")
if not animator or not saves then
	return HS:JSONEncode({ stop = "brak modelu, Animatora albo AnimSaves: " .. tostring(D.model) })
end
local KSP = game:GetService("KeyframeSequenceProvider")
local stare = animator:GetPlayingAnimationTracks()
for _, t in stare do
	t:Stop(0)
end
animator:StepAnimations(0)
for _, t in stare do
	t:Destroy()
end
local function wczytaj(ks)
	local anim = Instance.new("Animation")
	anim.AnimationId = KSP:RegisterKeyframeSequence(ks)
	local track = animator:LoadAnimation(anim)
	local t0 = os.clock()
	while track.Length == 0 and os.clock() - t0 < 5 do
		task.wait(0.05)
	end
	return track
end
-- klip neutralny (wszystkie stawy w zerze, najniższy priorytet) — gra pod każdym klipem i służy do powrotu
local neutralny = Instance.new("KeyframeSequence")
neutralny.Loop = true
neutralny.Priority = Enum.AnimationPriority.Core
for _, t in { 0, 0.1 } do
	local kf = Instance.new("Keyframe")
	kf.Time = t
	local korzen = Instance.new("Pose")
	korzen.Name = model.PrimaryPart.Name
	korzen.Weight = 0
	korzen.Parent = kf
	local pozy = { [model.PrimaryPart] = korzen }
	local kolejka = { model.PrimaryPart }
	while #kolejka > 0 do
		local cz = table.remove(kolejka, 1)
		for _, d in model:GetDescendants() do
			if d:IsA("Motor6D") and d.Part0 == cz and d.Part1 and not pozy[d.Part1] then
				local ps = Instance.new("Pose")
				ps.Name = d.Part1.Name
				ps.Weight = 1
				ps.Parent = pozy[cz]
				pozy[d.Part1] = ps
				table.insert(kolejka, d.Part1)
			end
		end
	end
	kf.Parent = neutralny
end
local zero = wczytaj(neutralny)
zero:Play(0, 1, 0)
local stawy = {}
for i, nazwa in D.kosci do
	local cz = model:FindFirstChild(nazwa)
	stawy[i] = cz and cz:FindFirstChildWhichIsA("Motor6D")
end
local wyniki = {}
for _, k in D.klipy do
	local w = { n = k.n, klatek = #k.klatki, stawow = #k.kosci, maxKat = 0, maxPoz = 0, ruch = 0 }
	local ks = saves:FindFirstChild(k.n)
	if not ks then
		w.blad = "brak klipu w AnimSaves"
	else
		local track = wczytaj(ks)
		w.dlugosc = track.Length
		w.petla = ks.Loop
		track:Play(0, 1, 0)
		for _, kl in k.klatki do
			track.TimePosition = kl.t
			animator:StepAnimations(0)
			for j, idx in k.kosci do
				local staw = stawy[idx]
				if not staw then
					w.blad = "brak stawu dla kości nr " .. idx
				else
					local o = (j - 1) * 6
					local oczek = CFrame.new(kl.w[o + 1], kl.w[o + 2], kl.w[o + 3]) * CFrame.fromOrientation(kl.w[o + 4], kl.w[o + 5], kl.w[o + 6])
					local roz = oczek:ToObjectSpace(staw.Transform)
					local _, kat = roz:ToAxisAngle()
					w.maxKat = math.max(w.maxKat, math.abs(math.deg(kat)))
					w.maxPoz = math.max(w.maxPoz, roz.Position.Magnitude)
					local _, katRuchu = staw.Transform:ToAxisAngle()
					w.ruch = math.max(w.ruch, math.abs(math.deg(katRuchu)), staw.Transform.Position.Magnitude * 10)
				end
			end
		end
		track:Stop(0)
		animator:StepAnimations(0)
		track:Destroy()
	end
	table.insert(wyniki, w)
end
-- powrót do spoczynku i pomiar
animator:StepAnimations(0)
zero:Stop(0)
animator:StepAnimations(0)
zero:Destroy()
local maxPoz, maxKat = 0, 0
for _, d in model:GetDescendants() do
	if d:IsA("Motor6D") and d.Part0 and d.Part1 then
		d.Transform = CFrame.identity
		local roz = (d.Part0.CFrame * d.C0 * d.C1:Inverse()):ToObjectSpace(d.Part1.CFrame)
		maxPoz = math.max(maxPoz, roz.Position.Magnitude)
		local _, kat = roz:ToAxisAngle()
		maxKat = math.max(maxKat, math.abs(math.deg(kat)))
	end
end
return HS:JSONEncode({ model = D.model, klipy = wyniki, spoczynek_st = maxPoz, spoczynek_deg = maxKat,
	klipow_w_studio = #saves:GetChildren() })
'''


def luau(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, (list, tuple)):
        return "{" + ",".join(luau(x) for x in v) + "}"
    if isinstance(v, dict):
        return "{" + ",".join("%s=%s" % (k, luau(x)) for k, x in v.items()) + "}"
    raise TypeError(type(v))


def klatki_do_proby(dl):
    """Kilka klatek rozłożonych po klipie, bez ostatniej (tam czas jest przycinany tuż przed koniec)."""
    if dl <= 2:
        return [0]
    return sorted({0, dl // 4, dl // 2, (3 * dl) // 4, dl - 1})


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Kontrola wszystkich klipów postaci z klocków w Studio (dane kontra Animator)")
    ap.add_argument("--tylko", default="", help="początki nazw plików <id>_klocki.json po przecinku (np. rycerz,pies)")
    ap.add_argument("--dane", default=os.path.join(TU, "wynik", "_roblox"), help="folder z plikami <id>_klocki.json")
    ap.add_argument("--zapisz", action="store_true", help="zapisz tabelę do <dane>/klipy_kontrola.txt")
    a = ap.parse_args()
    from studio_mcp import StudioMCP, StudioError, first_studio_id

    wybrane = [x for x in a.tylko.split(",") if x]
    pliki = sorted(p for p in glob.glob(os.path.join(a.dane, "*_klocki.json")) if os.path.basename(p) != "ekwipunek_klocki.json")
    if wybrane:
        pliki = [p for p in pliki if any(os.path.basename(p).startswith(w) for w in wybrane)]
    if not pliki:
        sys.exit("Nie ma plików *_klocki.json w %s" % a.dane)
    linie, zle, razem_klipow, razem_stawow, razem_klatek, porownan = [], 0, 0, 0, 0, 0
    try:
        with StudioMCP() as s:
            sid = first_studio_id(s)
            if not sid:
                sys.exit("Roblox Studio nie jest podłączone.")
            for p in pliki:
                with open(p, encoding="utf-8") as f:
                    d = json.load(f)
                klipy = []
                for k in d.get("klipy", []):
                    klipy.append({"n": k["n"], "kosci": k["kosci"],
                                  "klatki": [{"t": f / float(k["fps"]), "w": k["klatki"][f]} for f in klatki_do_proby(k["dl"])]})
                if not klipy:
                    continue
                dane = {"model": d["model"], "kosci": [x[0] for x in d["kosci"]], "klipy": klipy}
                kod = (KONTROLA.replace("__PLACE__", str(PLACE_ID)).replace("__KONTENER__", KONTENER)
                       .replace("__DANE__", luau(dane)))
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
                if r["is_error"]:
                    raise StudioError(r["text"])
                w = json.loads(r["text"])
                if w.get("stop"):
                    sys.exit("Studio odmówiło: %s" % w["stop"])
                for k in w["klipy"]:
                    razem_klipow += 1
                    razem_stawow += k["stawow"]
                    razem_klatek += k["klatek"]
                    porownan += k["stawow"] * k["klatek"]
                    ok = (not k.get("blad") and k["maxKat"] <= TOLERANCJA_KAT and k["maxPoz"] <= TOLERANCJA_POZ and k["ruch"] > 0.05)
                    zle += 0 if ok else 1
                    linie.append("%-18s %-12s %4.2f s %-5s stawów %2d, klatek próby %d: odchyłka %.4f° / %.5f st.%s  %s"
                                 % (w["model"], k["n"], k.get("dlugosc", 0), "pętla" if k.get("petla") else "raz", k["stawow"], k["klatek"],
                                    k["maxKat"], k["maxPoz"], "" if k["ruch"] > 0.05 else "  (klip niczego nie rusza!)",
                                    "ZGODNY" if ok else "NIEZGODNY" + (": " + k["blad"] if k.get("blad") else "")))
                spoczynek = w["spoczynek_st"] <= 0.01 and w["spoczynek_deg"] <= 0.5
                zle += 0 if spoczynek else 1
                linie.append("%-18s powrót do spoczynku: odchyłka %.4f st. / %.2f°  %s"
                             % (w["model"], w["spoczynek_st"], w["spoczynek_deg"], "OK" if spoczynek else "NIE WRÓCIŁA — użyj roblox_klatki.py --tylko-reset"))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)
    naglowek = ("Kontrola klipów w Animatorze Roblox Studio (tryb Edit), %s. Tolerancja: %.2f° i %.3f studa."
                % (time.strftime("%Y-%m-%d %H:%M"), TOLERANCJA_KAT, TOLERANCJA_POZ))
    stopka = ("RAZEM: klipów %d, porównań staw × klatka %d; wierszy z zastrzeżeniem: %d. WYNIK: %s"
              % (razem_klipow, porownan, zle, "ZGODNE" if zle == 0 else "NIEZGODNE"))
    tekst = "\n".join([naglowek] + linie + [stopka])
    print(tekst)
    if a.zapisz:
        with open(os.path.join(a.dane, "klipy_kontrola.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst + "\n")
    sys.exit(0 if zle == 0 else 1)


if __name__ == "__main__":
    main()
