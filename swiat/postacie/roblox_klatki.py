#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Klatki animacji postaci z klocków prosto z Roblox Studio (tryb Edit, bez uruchamiania gry).

    python -B swiat/postacie/roblox_klatki.py --model "Rycerz Blocky" --klip chod --wyj <folder>
    python -B swiat/postacie/roblox_klatki.py --model "Rycerz Blocky" --klip atak_miecz --klatki 0,8,12,16,20,24,28,32
    python -B swiat/postacie/roblox_klatki.py --model "Rycerz Blocky" --spoczynek --katy 0,40,90,180

Dla każdej klatki: klip z `AnimSaves` (KeyframeSequence) jest rejestrowany w Studio, wczytywany przez PRAWDZIWY
Animator postaci, ustawiany na czas klatki i przeliczany (`Animator:StepAnimations`) — to ta sama droga, którą
animacja pójdzie w grze. Potem zrzut ekranu z kamery ustawionej względem postaci. Na końcu poza wraca do spoczynku.
Wynik: pojedyncze klatki JPG i arkusz `<model>_<klip>_studio.jpg` (kolejność wierszami).
Po zrzutach postać wraca do spoczynku przez klip neutralny i narzędzie MIERZY, czy części naprawdę wróciły
(samo zatrzymanie ścieżki w trybie Edit zostawia części w ostatniej pozie). `--tylko-reset` robi sam powrót.
"""
import argparse
import json
import math
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
sys.path.insert(0, os.path.join(REPO, "tools"))
from studio_mcp import StudioMCP, StudioError, first_studio_id  # noqa: E402

KONTENER = "TestPostaci"

POZA = r'''
local kont = workspace:FindFirstChild("__KONTENER__")
local model = kont and kont:FindFirstChild(__MODEL__)
if not model then
	return { blad = "brak modelu" }
end
local KSP = game:GetService("KeyframeSequenceProvider")
local animator = model.AnimationController.Animator
local stare = animator:GetPlayingAnimationTracks()
for _, t in stare do
	t:Stop(0)
end
animator:StepAnimations(0)
for _, t in stare do
	t:Destroy()
end
local klip, czas = __KLIP__, __CZAS__
local wynik = { klip = klip, czas = czas }

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

-- Klip neutralny: wszystkie stawy w pozie zerowej, najniższy priorytet. Gra pod każdym klipem, bo w trybie Edit
-- zatrzymanie ścieżki NIE cofa części (sprawdzone 13.11.2026): staw, którego nowy klip nie animuje, zostałby
-- w pozie z poprzedniego klipu. Ten sam klip służy do powrotu do spoczynku.
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
if klip ~= "" then
	local ks = model.AnimSaves:FindFirstChild(klip)
	if not ks then
		return { blad = "brak klipu " .. klip }
	end
	local track = wczytaj(ks)
	wynik.dlugosc = track.Length
	track:Play(0, 1, 0)
	track.TimePosition = math.min(czas, math.max(track.Length - 0.001, 0))
end
animator:StepAnimations(0)
if klip == "" then
	zero:Stop(0)
	animator:StepAnimations(0)
	zero:Destroy()
	local n = 0
	for _, d in model:GetDescendants() do
		if d:IsA("Motor6D") then
			d.Transform = CFrame.identity
			n += 1
		end
	end
	wynik.wyzerowane = n
end
-- kontrola: o ile części kości odbiegają od miejsca wyznaczonego przez stawy w spoczynku
local maxPoz, maxKat = 0, 0
for _, d in model:GetDescendants() do
	if d:IsA("Motor6D") and d.Part0 and d.Part1 then
		local roz = (d.Part0.CFrame * d.C0 * d.C1:Inverse()):ToObjectSpace(d.Part1.CFrame)
		maxPoz = math.max(maxPoz, roz.Position.Magnitude)
		local _, kat = roz:ToAxisAngle()
		maxKat = math.max(maxKat, math.abs(math.deg(kat)))
	end
end
wynik.odchylka_st = maxPoz
wynik.odchylka_deg = maxKat
local hrp = model.PrimaryPart
local cf, rozmiar = model:GetBoundingBox()
wynik.hrp = { hrp.Position.X, hrp.Position.Y, hrp.Position.Z }
wynik.przod = { hrp.CFrame.LookVector.X, hrp.CFrame.LookVector.Z }
wynik.srodek = { cf.Position.X, cf.Position.Y, cf.Position.Z }
wynik.rozmiar = { rozmiar.X, rozmiar.Y, rozmiar.Z }
return wynik
'''


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Klatki animacji postaci z klocków ze Studio (tryb Edit)")
    ap.add_argument("--model", required=True, help="nazwa modelu w Workspace/%s" % KONTENER)
    ap.add_argument("--klip", default="")
    ap.add_argument("--klatki", default="", help="numery klatek po przecinku (domyślnie 8 równo rozłożonych)")
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--spoczynek", action="store_true", help="poza spoczynkowa z kilku stron (--katy)")
    ap.add_argument("--tylko-reset", action="store_true", help="tylko przywróć pozę spoczynkową (bez zrzutów)")
    ap.add_argument("--katy", default="35", help="kąt kamery w stopniach od przodu postaci (dodatni = od jej lewej strony)")
    ap.add_argument("--odleglosc", type=float, default=0.0, help="odległość kamery (0 = dobierz do wzrostu)")
    ap.add_argument("--wyj", default=os.path.join(TU, "wynik", "_roblox"))
    ap.add_argument("--kolumny", type=int, default=4)
    ap.add_argument("--bok", type=int, default=360, help="bok kafelka arkusza w pikselach")
    a = ap.parse_args()
    os.makedirs(a.wyj, exist_ok=True)
    from PIL import Image

    try:
        with StudioMCP() as s:
            sid = first_studio_id(s)
            if not sid:
                sys.exit("Roblox Studio nie jest podłączone.")

            def poza(klip, czas):
                kod = (POZA.replace("__KONTENER__", KONTENER).replace("__MODEL__", json.dumps(a.model, ensure_ascii=False))
                       .replace("__KLIP__", json.dumps(klip)).replace("__CZAS__", repr(float(czas))))
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=120)
                if r["is_error"]:
                    raise StudioError(r["text"])
                d = json.loads(r["text"])
                if d.get("blad"):
                    sys.exit("Studio: %s" % d["blad"])
                for k, v in list(d.items()):                   # tablice Luau wracają jako {"1": …, "2": …}
                    if isinstance(v, dict):
                        d[k] = [v[str(i)] for i in range(1, len(v) + 1)]
                return d

            def zrzut(nazwa, info, kat):
                x, y, z = info["hrp"]
                fx, fz = info["przod"]
                h = max(info["rozmiar"][1], 2.5)
                cy = info["srodek"][1]
                odl = a.odleglosc or max(5.0, max(h, info["rozmiar"][0], info["rozmiar"][2]) * 1.45)
                k = math.radians(kat)
                dx, dz = fx * math.cos(k) - fz * math.sin(k), fx * math.sin(k) + fz * math.cos(k)
                r = s.call("screen_capture", {"studio_id": sid, "capture_id": "postac_" + nazwa,
                                              "camera_position": [x + dx * odl, cy + h * 0.25, z + dz * odl],
                                              "look_at_position": [x, cy, z]}, timeout=120)
                if r["is_error"] or not r["images"]:
                    sys.exit("zrzut %s: %s" % (nazwa, (r["text"] or "brak obrazu")[:200]))
                png = os.path.join(a.wyj, nazwa + ".png")
                with open(png, "wb") as f:
                    f.write(r["images"][0])
                im = Image.open(png).convert("RGB")
                os.remove(png)
                return im

            if a.tylko_reset:
                k = poza("", 0.0)
                print("%s: spoczynek, odchyłka %.4f studa, %.2f°" % (a.model, k["odchylka_st"], k["odchylka_deg"]))
                return
            slug = "".join(c if c.isalnum() else "_" for c in a.model.lower())
            kafle, podpisy = [], []
            if a.spoczynek or not a.klip:
                info = poza("", 0.0)
                for kat in [float(v) for v in a.katy.split(",")]:
                    kafle.append(zrzut("%s_spoczynek_%03d" % (slug, int(kat)), info, kat))
                    podpisy.append("%d°" % int(kat))
                nazwa_arkusza = "%s_spoczynek_studio.jpg" % slug
            else:
                info = poza(a.klip, 0.0)
                ostatnia = int(round(info["dlugosc"] * a.fps))
                if a.klatki:
                    klatki = [int(v) for v in a.klatki.split(",")]
                else:
                    klatki = [int(round(ostatnia * i / 8.0)) for i in range(8)]
                kat = float(a.katy.split(",")[0])
                for f in klatki:
                    info = poza(a.klip, f / a.fps)
                    kafle.append(zrzut("%s_%s_%03d" % (slug, a.klip, f), info, kat))
                    podpisy.append("kl. %d" % f)
                nazwa_arkusza = "%s_%s_studio.jpg" % (slug, a.klip)
            koniec = poza("", 0.0)
            if koniec["odchylka_st"] > 0.01 or koniec["odchylka_deg"] > 0.5:
                print("UWAGA: postać NIE wróciła do spoczynku (odchyłka %.3f studa, %.1f°) — przebuduj ją: roblox_postac.py --tylko …"
                      % (koniec["odchylka_st"], koniec["odchylka_deg"]))
            else:
                print("poza wróciła do spoczynku — sprawdzone pomiarem (odchyłka %.4f studa, %.2f°)"
                      % (koniec["odchylka_st"], koniec["odchylka_deg"]))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)

    # arkusz: kafelki kwadratowe wycięte ze środka zrzutu
    bok, kol = a.bok, min(a.kolumny, len(kafle))
    wiersze = (len(kafle) + kol - 1) // kol
    arkusz = Image.new("RGB", (kol * bok, wiersze * bok), (20, 18, 24))
    for i, im in enumerate(kafle):
        w, h = im.size
        m = min(w, h)
        im = im.crop(((w - m) // 2, (h - m) // 2, (w - m) // 2 + m, (h - m) // 2 + m)).resize((bok, bok), Image.LANCZOS)
        arkusz.paste(im, ((i % kol) * bok, (i // kol) * bok))
    sciezka = os.path.join(a.wyj, nazwa_arkusza)
    arkusz.save(sciezka, "JPEG", quality=88)
    print("arkusz: %s (%s)" % (sciezka, ", ".join(podpisy)))


if __name__ == "__main__":
    main()
