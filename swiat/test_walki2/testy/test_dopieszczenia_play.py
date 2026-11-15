#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Play poprawek „dopieszczenia” walki v2 (15.11.2026, lista D1–D8). Sam wraca do trybu Edit.

    python -B swiat/test_walki2/testy/test_dopieszczenia_play.py                 # wszystko (ok. 6 min)
    python -B swiat/test_walki2/testy/test_dopieszczenia_play.py --tylko final,lot,napisy,twarz,dzwiek,slime,tempo

Części (mierzone na prawdziwym odtwarzaniu w Studio; czas sceny przesuwa odtwarzacz w trybie `reczny`, pętla kroków
biegnie w jednym wywołaniu po stronie klienta):
  final   D1: po ciosie kończącym ujęcie POKONANEGO (≥ 1,0 s przy ×1), pokonany w kadrze, jego klip upadku kończy się
          w tym ujęciu; potem objazd zwycięzcy: zwycięzca w kadrze i niezasłonięty, szczątki pokonanego nie bliżej
          kamery niż 0,95 odległości do zwycięzcy (stos głazów Strażnika nie na pierwszym planie), kąt twarzy
          zwycięzcy ≤ 60° od 0,5 s radości (wiwat widać z przodu, nie plecy) — 8 finałów
  lot     D2: strzała leci 0,45–0,7 s i obrażenia wchodzą, gdy doleci; w czasie „jak w grze” (z zwolnieniem krytyka)
          od chwili, gdy pocisk jest ≤ 0,5 studa od powierzchni celu, do zmiany paska ≤ 0,15 s; strzała przy celu
          nie znika w nim (promień z kamery w ostatnich 0,2 s przed trafieniem nie trafia w cel) — strzała przy Slimie,
          krytyk przy Strażniku i Trollu, iskra i lodowy pocisk Maga przy Slimie; światło strzały słabe i gaśnie;
          bańka kwasu leci ≥ 0,45 s, kałuża (dysk) stoi przy celu ≥ 0,8 s
  napisy  D3: (a) tury z kilkoma napisami (tarcza, umiejętność + efekt, krytyk, tyknięcie + utrata tury) i (b) trzy
          CAŁE walki (wilk z Wojownikiem i z Magiem, Strażnik ze Zwiadowcą) klatka po klatce co 1/30 s czasu „jak w
          grze”, z animacją wejścia i wygaszania: żadne dwa narysowane napisy na siebie nie wchodzą, najwyżej 3 przy
          postaci, żaden napis nie leży na swojej małej postaci, głowa dużego celu przykryta napisami ≤ 20%
  twarz   D5: kąt twarzy potwora (0° = w twarz, 90° = profil) w chwili każdego trafienia walki z każdym potworem ≤ 62°;
          gracz w kadrze ≥ 50% części, a gdy potwór bije gracza — ≥ 60%
  dzwiek  D4: każdy dźwięk z Ustawienia.DZWIEKI wczytuje się z klienta (rbxasset://, długość > 0); przycisk wyciszenia
  slime   D6: brzuszki slime'a schowane w spoczynku (niewidoczne), widoczne jako płaty kałuży po upadku; w upadku płaty
          (obrócone brzuszki) niewidoczne, póki galareta jest wyższa niż 62% (sześcian); galareta nie Glass
  tempo   D7: pełna walka przy ×2 i ×4 (zwykłe odtwarzanie): wszystkie zdarzenia, bez błędów, paski zgodne; przy ×4 ujęcie
          pokonanego nadal ≥ 1,0 s i upadek w nim; napisy bez nakładania i bez napisu na małym celu (także walki
          z wilkiem), dźwięki najwyżej 3 naraz
Wynik: testy/wynik_dopieszczenia.json.
"""
import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
KATALOG = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(KATALOG))
for _s in (TU, os.path.join(REPO, "tools", "walka")):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import silnik as S  # noqa: E402
import wzorcowe as WZ  # noqa: E402
from sesja_play import SesjaPlay, log  # noqa: E402

WYNIKI = []
KAT_TWARZY_MAKS = 62
KAT_ZWYCIEZCY_MAKS = 60      # D1: kąt twarzy zwycięzcy w radości (od 0,5 s, po obrocie do widza)
PROG_SZCZATKOW = 0.95        # D1: szczątki pokonanego co najmniej tyle × odległość kamery do zwycięzcy
GRACZ_W_KADRZE = 0.5         # D5: gracz w kadrze przy każdym trafieniu…
GRACZ_CEL_W_KADRZE = 0.6     # …a gdy to on obrywa od potwora


def wynik(nazwa, ok, opis=""):
    WYNIKI.append({"nazwa": nazwa, "ok": bool(ok), "opis": opis})
    log("%-70s %s %s" % (nazwa, "OK" if ok else "BŁĄD", opis))


def dziennik(p):
    return S.symuluj(WZ.postac(p["klasa"], p["poziom"]), {"potwor": p["przeciwnik"], "poziom": p["poziom"]}, p["ziarno"])


def start(s, p, opcje="{ reczny = true, tempo = 1 }"):
    s.steruj('"zamknij"')
    time.sleep(0.8)
    s.ziarno(p["ziarno"])
    s.start(p["klasa"], p["przeciwnik"], str(p["poziom"]), opcje)
    st, _ = s.czekaj(("odtwarzanie",), 15)
    return st.get("OstatniStan") == "odtwarzanie"


NAGLOWEK = '''
local S = workspace.TestWalki2.Sygnaly.Sterowanie
local HS = game:GetService("HttpService")
local scena = workspace.TestWalki2:FindFirstChild("ScenaLokalna")
'''

# ---------------------------------------------------------------------------------------------------- D1 finał
FINAL = NAGLOWEK + '''
local st = S:Invoke("przewinDo", __T0__)
local hit = st.trafienie or __T0__
local tp, tr, kon = st.tPokonany, st.tRadosc, st.czasKonca
local probki = {}
local t = hit
while t < kon - 0.05 do
	t += 0.1
	local s2 = S:Invoke("przewinDo", t)
	task.wait() -- części na stawach Motor6D przestawiają się dopiero w kroku silnika
	local k = S:Invoke("kadr")
	table.insert(probki, { tau = s2.tau, uj = s2.ujecie, kadr = k, upadek = s2.upadek })
	if s2.faza ~= "odtwarzanie" then break end
end
return HS:JSONEncode({ hit = hit, tp = tp, tr = tr, kon = kon, pokonany = st.pokonany, zwyciezca = st.zwyciezca, probki = probki })
'''


def test_final(s, Z):
    finaly = [("wygrana, Strażnik", Z["shard"]), ("przegrana, Muchomornik", Z["krotka"]),
              ("wygrana, Slime", Z["umiejetnosci"]["kwasny_plusk"])]
    for p in Z["play"]:
        if p["przeciwnik"] == "lesny_slime" and p["wynik"] == "przegrana":
            finaly.append(("przegrana, Slime", p))
        if p["przeciwnik"] == "straznik_lasu" and p["wynik"] == "przegrana":
            finaly.append(("przegrana, Strażnik", p))
        if p["przeciwnik"] == "lesny_troll":
            finaly.append(("%s, Troll" % p["wynik"], p))
    finaly.append(("wygrana, Troll", Z["umiejetnosci"]["ogluszajace_uderzenie"]))
    for nazwa, p in finaly:
        w = dziennik(p)
        ost = w["dziennik"][-1]
        if not start(s, p):
            wynik("D1 finał %s" % nazwa, False, "walka nie wystartowała")
            continue
        r = json.loads(s.luau(FINAL.replace("__T0__", "%f" % (ost["t"] + 0.01)), timeout=300))
        P, W = r["pokonany"], r["zwyciezca"]
        tp, tr = r["tp"], r["tr"]
        zle = []
        w_ujeciu = [x for x in r["probki"] if tp + 0.05 <= x["tau"] <= tr - 0.05]
        if not w_ujeciu:
            zle.append("brak klatek ujęcia pokonanego")
        for x in w_ujeciu:
            if x["uj"] != "pokonany":
                zle.append("τ=%.2f ujęcie %s" % (x["tau"], x["uj"]))
            elif x["kadr"][P]["wKadrze"] < 0.6:
                zle.append("τ=%.2f pokonany w kadrze %.2f" % (x["tau"], x["kadr"][P]["wKadrze"]))
        przed = [x for x in r["probki"] if x["tau"] <= tr + 0.001]
        upadek = przed[-1]["upadek"] if przed and przed[-1].get("upadek") else None
        if not upadek or upadek["czas"] < upadek["dlugosc"] - 0.02:
            zle.append("upadek nie skończony przed radością: %s" % upadek)
        objazd = [x for x in r["probki"] if x["tau"] >= tr + 0.15]
        for x in objazd:
            k = x["kadr"]
            if k[W]["wKadrze"] < 0.6 or k[W]["odsloniete"] < 0.7:
                zle.append("τ=%.2f objazd: zwycięzca w kadrze %.2f odsł. %.2f" % (x["tau"], k[W]["wKadrze"], k[W]["odsloniete"]))
            if k.get("pokonanyOdKamery", 99) < PROG_SZCZATKOW * k.get("zwyciezcaOdKamery", 0):
                zle.append("τ=%.2f szczątki %.1f studa od kamery (zwycięzca %.1f)" % (x["tau"], k["pokonanyOdKamery"], k["zwyciezcaOdKamery"]))
            # wiwat z przodu (przegląd 15.11: radość zwycięzcy widać było od tyłu, panel na tle pleców)
            if x["tau"] >= tr + 0.5 and k.get("katTwarzyZwyciezcy", 0) > KAT_ZWYCIEZCY_MAKS:
                zle.append("τ=%.2f twarz zwycięzcy %.0f°" % (x["tau"], k["katTwarzyZwyciezcy"]))
        dl = tr - tp
        if dl < 1.0:
            zle.append("ujęcie pokonanego %.2f s" % dl)
        minOdl = min((x["kadr"].get("pokonanyOdKamery", 99) / max(x["kadr"].get("zwyciezcaOdKamery", 1), 0.1)) for x in objazd) if objazd else -1
        katy = [x["kadr"].get("katTwarzyZwyciezcy", 0) for x in objazd if x["tau"] >= tr + 0.5]
        wynik("D1 finał %s (%s/%s/%d ziarno %d)" % (nazwa, p["klasa"], p["przeciwnik"], p["poziom"], p["ziarno"]), not zle,
              "; ".join(zle[:5]) if zle else "ujęcie pokonanego %.2f s, upadek skończony w ujęciu, objazd: %d klatek, "
                                              "szczątki ≥ %.2f odległości zwycięzcy, twarz zwycięzcy %.0f–%.0f°"
              % (dl, len(objazd), minOdl, min(katy) if katy else -1, max(katy) if katy else -1))


# ---------------------------------------------------------------------------------------------------- D2 pociski
LOT_POCISKU = NAGLOWEK + '''
local st = S:Invoke("przewinDo", __T0__)
local hit, wyp = st.trafienie, st.wypuszczenie
local POLE = if st.cel == "wrog" then "paskiWrog" else "paskiGracz"
local hp0 = st[POLE]
S:Invoke("przewinDo", wyp - 0.08)
-- przednia część pocisku i jak daleko od niej jest przód (studs)
local NAZWY = { StrzalaGrot = 0, PociskIskra = 0.38, KulaOgnia = 0.6, Lod = 1.0 }
local cel = scena:FindFirstChild("__CELMODEL__")
local zmienione = {}
for _, c in cel:GetDescendants() do
	if c:IsA("BasePart") and not c.CanQuery then
		c.CanQuery = true
		table.insert(zmienione, c)
	end
end
local params = RaycastParams.new()
params.FilterType = Enum.RaycastFilterType.Include
params.FilterDescendantsInstances = { cel }
local rzeczywisty = 0
local probki = {}
local pierwsza, blisko, bliskoR, hpZmiana, hpZmianaR = nil, nil, nil, nil, nil
local swiatloMaks, zasiegMaks = 0, 0
for i = 1, 260 do
	local s2 = S:Invoke("przewin", 1 / 60)
	rzeczywisty += 1 / 60
	task.wait()
	local pt = s2.punktTrafienia and Vector3.new(s2.punktTrafienia[1], s2.punktTrafienia[2], s2.punktTrafienia[3])
	local odl = nil
	local widac, czesci = 0, 0
	local kam = workspace.CurrentCamera.CFrame.Position
	for _, c in scena:GetChildren() do
		if c:IsA("BasePart") and NAZWY[c.Name] ~= nil and c.LocalTransparencyModifier < 0.9 then
			pierwsza = pierwsza or s2.tau
			if pt then
				local d = (c.Position - pt).Magnitude - NAZWY[c.Name]
				odl = if odl then math.min(odl, d) else d
			end
			if c.Name == "StrzalaGrot" then
				local l = c:FindFirstChildOfClass("PointLight")
				if l and l.Enabled and hit - s2.tau <= 0.1 and hit - s2.tau >= 0 then
					swiatloMaks = math.max(swiatloMaks, l.Brightness)
					zasiegMaks = math.max(zasiegMaks, l.Range)
				end
			end
		end
		if c:IsA("BasePart") and (c.Name == "Strzala" or c.Name == "StrzalaLotka") and c.LocalTransparencyModifier < 0.9 then
			czesci += 1
			local traf = workspace:Raycast(kam, c.Position - kam, params)
			if not traf then
				widac += 1
			end
		end
	end
	if odl and odl <= 0.5 and not blisko then
		blisko, bliskoR = s2.tau, rzeczywisty
	end
	if hpZmiana == nil and s2[POLE] ~= hp0 then
		hpZmiana, hpZmianaR = s2.tau, rzeczywisty
	end
	table.insert(probki, { r = rzeczywisty, tau = s2.tau, odl = odl, widac = widac, czesci = czesci })
	if hpZmiana and rzeczywisty > hpZmianaR + 0.3 then break end
end
for _, c in zmienione do c.CanQuery = false end
-- strzała w ostatnich 0,2 s (czasu rzeczywistego) przed zmianą paska: ile klatek, w których jest zasłonięta przez cel
local zaslon, klatek = 0, 0
if hpZmianaR then
	for _, p in probki do
		if p.r >= hpZmianaR - 0.2 and p.r <= hpZmianaR and p.czesci > 0 then
			klatek += 1
			if p.widac == 0 then zaslon += 1 end
		end
	end
end
return HS:JSONEncode({ hit = hit, wyp = wyp, lot = st.lot, pierwsza = pierwsza, blisko = blisko, bliskoR = bliskoR,
	hpZmiana = hpZmiana, hpZmianaR = hpZmianaR, zaslon = zaslon, klatek = klatek, swiatlo = swiatloMaks, zasieg = zasiegMaks,
	krytyk = st.krytyk })
'''

LOT_BANKI = NAGLOWEK + '''
local st = S:Invoke("przewinDo", __T0__)
local hit, wyp = st.trafienie, st.wypuszczenie
local slime = scena:FindFirstChild("lesny_slime_lokalny")
local kula = slime:FindFirstChild("Kula")
local korzen = slime:FindFirstChild("HumanoidRootPart")
local t = wyp - 0.15
local probki = {}
local kaluzaOd, kaluzaDo = nil, nil
while t < hit + 1.6 do
	t += 1 / 60
	local s2 = S:Invoke("przewinDo", t)
	task.wait() -- kość bańki (Motor6D) przestawia się dopiero w kroku silnika
	local d = (kula.Position - korzen.Position) * Vector3.new(1, 0, 1)
	table.insert(probki, { s2.tau, d.Magnitude })
	if scena:FindFirstChild("KaluzaKwasu") then
		kaluzaOd = kaluzaOd or s2.tau
		kaluzaDo = s2.tau
	end
end
return HS:JSONEncode({ hit = hit, wyp = wyp, lot = st.lot, probki = probki, kaluzaOd = kaluzaOd, kaluzaDo = kaluzaDo })
'''


def test_lot(s, Z):
    przypadki = [("strzała przy Slimie", Z["umiejetnosci"]["zatruta_strzala"], None, "zatruta_strzala"),
                 ("strzała, krytyk przy Strażniku", Z["shard"], 6, None),
                 ("strzała, krytyk przy Trollu", Z["wszystkie_typy"]["zwiadowca"], 11, None),
                 ("iskra Maga, krytyk przy Slimie", {"klasa": "mag", "przeciwnik": "lesny_slime", "poziom": 5, "ziarno": 63518}, 0, None),
                 ("lodowy pocisk przy Slimie", {"klasa": "mag", "przeciwnik": "lesny_slime", "poziom": 5, "ziarno": 63518}, 9, None)]
    for opis, p, idx, um in przypadki:
        w = dziennik(p)
        d = w["dziennik"]
        if idx is None:
            idx = next(i for i, z in enumerate(d) if z["umiejetnosc"] == um and z["typ"] == "umiejetnosc")
        z = d[idx]
        model = (p["przeciwnik"] if z["cel"] == "wrog" else p["klasa"]) + "_lokalny"
        if not start(s, p):
            wynik("D2 lot: %s" % opis, False, "walka nie wystartowała")
            continue
        r = json.loads(s.luau(LOT_POCISKU.replace("__T0__", "%f" % (z["t"] + 0.01)).replace("__CELMODEL__", model), timeout=300))
        for k in ("pierwsza", "blisko", "bliskoR", "hpZmiana", "hpZmianaR"):
            r.setdefault(k, None)
        log("  surowe: %s" % {k: v for k, v in r.items()})
        zle = []
        lot = (r["blisko"] or 0) - (r["pierwsza"] or 0)
        if r["pierwsza"] is None or r["blisko"] is None:
            zle.append("pocisk nie doleciał do powierzchni celu (pierwsza %s, blisko %s)" % (r["pierwsza"], r["blisko"]))
        elif not 0.4 <= lot <= 0.75:
            zle.append("lot %.2f s czasu sceny" % lot)
        if r["hpZmiana"] is None or abs(r["hpZmiana"] - r["hit"]) > 0.03:
            zle.append("pasek w τ=%s, trafienie z dziennika τ=%.2f" % (r["hpZmiana"], r["hit"]))
        opoz = (r["hpZmianaR"] - r["bliskoR"]) if (r["hpZmianaR"] is not None and r["bliskoR"] is not None) else 99
        if opoz > 0.15:
            zle.append("od dolotu do paska %.2f s czasu rzeczywistego" % opoz)
        if "strzała" in opis:
            if r["klatek"] == 0 or r["zaslon"] > 0:
                zle.append("strzała zasłonięta przez cel w %d z %d klatek ostatnich 0,2 s" % (r["zaslon"], r["klatek"]))
            if r["swiatlo"] > 0.35 or r["zasieg"] > 3.5:
                zle.append("światło strzały przy dolocie: jasność %.2f, zasięg %.1f" % (r["swiatlo"], r["zasieg"]))
        wynik("D2 lot: %s (%s/%s/%d ziarno %d, zd. %d%s)" % (opis, p["klasa"], p["przeciwnik"], p["poziom"], p["ziarno"], idx + 1,
                                                             ", krytyk" if r["krytyk"] else ""), not zle,
              "; ".join(zle) if zle else
              "lot %.2f s (τ %.2f → %.2f przy powierzchni celu), pasek τ=%.3f (dziennik %.2f); od dolotu do paska %.2f s "
              "czasu rzeczywistego; strzała zasłonięta w %d/%d klatek; światło przy dolocie %.2f"
              % (lot, r["pierwsza"], r["blisko"], r["hpZmiana"], r["hit"], opoz, r["zaslon"], r["klatek"], r["swiatlo"]))
    p = Z["umiejetnosci"]["kwasny_plusk"]
    w = dziennik(p)
    idx = next(i for i, z in enumerate(w["dziennik"]) if z["umiejetnosc"] == "kwasny_plusk" and z["typ"] == "umiejetnosc")
    z = w["dziennik"][idx]
    if start(s, p):
        r = json.loads(s.luau(LOT_BANKI.replace("__T0__", "%f" % (z["t"] + 0.01)), timeout=300))
        pr = r["probki"]
        # lot: od chwili, gdy bańka wysuwa się dalej niż 1,5 studa przed slime'a, do największego wysunięcia
        start_lotu = next((t for t, d in pr if d > 1.5), None)
        maks = max(pr, key=lambda x: x[1])
        lot = (maks[0] - start_lotu) if start_lotu is not None else 0
        kaluza = (r["kaluzaDo"] or 0) - (r["kaluzaOd"] or 0)
        ok = lot >= 0.4 and abs(maks[0] - r["hit"]) <= 0.06 and kaluza >= 0.8
        wynik("D2 lot bańki kwasu i kałuża (%s/%s/%d, zd. %d)" % (p["klasa"], p["przeciwnik"], p["poziom"], idx + 1), ok,
              "bańka leci %.2f s (od τ %.2f do %.2f, %.1f studa), trafienie τ=%.2f; dysk kałuży %.2f s"
              % (lot, start_lotu or -1, maks[0], maks[1], r["hit"], kaluza))


# ---------------------------------------------------------------------------------------------------- D3 napisy
NAPISY = NAGLOWEK + '''
-- klatki co 1/30 s czasu „jak w grze” (przewin: tempo, zwolnienia), napisy narysowane (z wejściem i wygaszaniem)
if __T0__ > 0 then S:Invoke("przewinDo", __T0__) end
local function pole(a, b)
	local w = math.min(a.x1, b.x1) - math.max(a.x0, b.x0)
	local h = math.min(a.y1, b.y1) - math.max(a.y0, b.y0)
	if w <= 0 or h <= 0 then return 0 end
	return w * h
end
local r = { klatek = 0, nakladania = 0, naCelu = 0, naInnym = 0, maks = 0, glowa = 0, problemy = {}, teksty = {} }
local function problem(t)
	if #r.problemy < 8 then table.insert(r.problemy, t) end
end
local czas = 0
while czas < __DO__ do
	local st = S:Invoke("przewin", 1 / 30)
	czas += 1 / 30
	r.klatek += 1
	if r.klatek % 10 == 0 then task.wait() end
	local n = S:Invoke("napisy")
	local lista = {}
	for _, x in n.napisy or {} do
		if x.widoczny then
			table.insert(lista, x)
			r.teksty[x.tekst] = true
		end
	end
	local kadr, kotwice = n.kadr, n.kotwice or {}
	local ile = {}
	local zle = false
	for i = 1, #lista do
		local a = lista[i]
		ile[a.klucz] = (ile[a.klucz] or 0) + 1
		for j = i + 1, #lista do
			local b = lista[j]
			if pole(a, { x0 = b.x0 + 2, y0 = b.y0 + 2, x1 = b.x1 - 2, y1 = b.y1 - 2 }) > 0 then
				zle = true
				problem(string.format("τ=%.2f „%s” na „%s”", st.tau or -1, a.tekst, b.tekst))
			end
		end
		for k, R in kotwice do
			local maly = kadr and (R.y1 - R.y0) < 0.4 * kadr.wys
			if maly and pole(a, { x0 = R.x0 + 3, y0 = R.y0 + 3, x1 = R.x1 - 3, y1 = R.y1 - 3 }) > 0 then
				if k == a.klucz then
					r.naCelu += 1
					problem(string.format("τ=%.2f „%s” na swojej małej postaci (%s)", st.tau or -1, a.tekst, k))
				else
					r.naInnym += 1
				end
			end
		end
	end
	for k, R in kotwice do
		local G = R.glowa
		if G and kadr and (R.y1 - R.y0) >= 0.4 * kadr.wys then
			local s = 0
			for _, a in lista do s += pole(a, G) end
			local u = s / math.max(1, (G.x1 - G.x0) * (G.y1 - G.y0))
			if u > r.glowa then r.glowa = u end
			if u > 0.2 then problem(string.format("τ=%.2f głowa (%s) przykryta w %.0f%%", st.tau or -1, k, u * 100)) end
		end
	end
	if zle then r.nakladania += 1 end
	for _, c in ile do if c > r.maks then r.maks = c end end
	if st.faza ~= "odtwarzanie" then break end
end
local t = {}
for k in r.teksty do table.insert(t, k) end
r.teksty = t
return HS:JSONEncode(r)
'''


def ocen_napisy(nazwa, r):
    zle = list(r["problemy"])
    ok = r["nakladania"] == 0 and r["maks"] <= 3 and r["naCelu"] == 0 and r["glowa"] <= 0.2
    wynik(nazwa, ok, ("; ".join(zle[:4]) + " (klatek z nakładaniem %d, na swojej małej postaci %d, głowa %.0f%%)"
                      % (r["nakladania"], r["naCelu"], r["glowa"] * 100)) if not ok else
          "%d klatek co 1/30 s: 0 nakładań, najwyżej %d przy postaci, 0 na swojej małej postaci, głowa dużego celu "
          "przykryta najwyżej %.0f%%, na drugiej (małej) postaci %d klatek; napisy: %s"
          % (r["klatek"], r["maks"], r["glowa"] * 100, r["naInnym"], ", ".join(sorted(r["teksty"]))[:300]))


def test_napisy(s, Z):
    przypadki = []
    warunki = (("cios / blok na tarczy", lambda d, i: d[i]["typ"] in ("cios", "krytyk", "blok") and d[i]["pochloniete"] > 0),
               ("umiejętność + nałożenie efektu", lambda d, i: d[i]["typ"] == "umiejetnosc" and d[i]["kto"] != d[i]["cel"]
                and i + 1 < len(d) and d[i + 1]["typ"] == "efekt_nalozony"),
               ("krytyk", lambda d, i: d[i]["typ"] == "krytyk" and d[i]["cel"] == "wrog"),
               ("tyknięcie + utrata tury", lambda d, i: d[i]["typ"] == "efekt_tick" and i + 1 < len(d) and d[i + 1]["typ"] == "utrata_tury"))
    for opis, war in warunki:
        for p in [Z["shard"], Z["dluga"]] + Z["play"] + list(Z["umiejetnosci"].values()):
            d = dziennik(p)["dziennik"]
            idx = next((i for i in range(len(d)) if war(d, i)), None)
            if idx is not None:
                przypadki.append((opis, p, idx))
                break
    for opis, p, idx in przypadki:
        z = dziennik(p)["dziennik"][idx]
        if not start(s, p):
            wynik("D3 napisy %s" % opis, False, "walka nie wystartowała")
            continue
        hit = z["t"] + z["trwa"] * 0.5 if z["typ"] in ("cios", "krytyk", "blok", "unik") else z["t"]
        r = json.loads(s.luau(NAPISY.replace("__T0__", "%f" % max(0.01, hit - 0.3)).replace("__DO__", "2.4"), timeout=300))
        ocen_napisy("D3 napisy: %s (%s/%s/%d zd. %d)" % (opis, p["klasa"], p["przeciwnik"], p["poziom"], idx + 1), r)
    # całe walki klatka po klatce: wilk (mały cel) z Wojownikiem i z Magiem, Strażnik (duży cel) ze Zwiadowcą
    # (×4 też klatka po klatce: przy ×4 napisy żyją krócej, a kamera częściej przechodzi płynnie)
    for opis, p, tempo in (("cała walka, Wojownik z wilkiem", Z["wszystkie_typy"]["wojownik"], 1),
                           ("cała walka, Mag z wilkiem", Z["wszystkie_typy"]["mag"], 1),
                           ("cała walka, Zwiadowca ze Strażnikiem", Z["shard"], 1),
                           ("cała walka ×4, Mag z wilkiem", Z["wszystkie_typy"]["mag"], 4),
                           ("cała walka ×4, Wojownik ze Slime'em", Z["umiejetnosci"]["kwasny_plusk"], 4)):
        if not start(s, p, "{ reczny = true, tempo = %d }" % tempo):
            wynik("D3 napisy %s" % opis, False, "walka nie wystartowała")
            continue
        r = json.loads(s.luau(NAPISY.replace("__T0__", "0").replace("__DO__", "1000"), timeout=600))
        ocen_napisy("D3 napisy: %s (%s/%s/%d ziarno %d)" % (opis, p["klasa"], p["przeciwnik"], p["poziom"], p["ziarno"]), r)


# ---------------------------------------------------------------------------------------------------- D5 twarz potwora
TWARZ = NAGLOWEK + '''
local wynik = {}
for _, t0 in { __CHWILE__ } do
	local st = S:Invoke("przewinDo", t0)
	local hit = st.trafienie or t0
	S:Invoke("przewinDo", hit + 0.005)
	task.wait()
	local k = S:Invoke("kadr")
	table.insert(wynik, { t = hit, kat = k.katTwarzy, uj = k.ujecie, typ = st.typ, um = st.umiejetnosc, cel = st.cel,
		wG = k.gracz.wKadrze, wW = k.wrog.wKadrze, oG = k.gracz.odsloniete, oW = k.wrog.odsloniete })
end
return HS:JSONEncode(wynik)
'''


def test_twarz(s, Z):
    walki = {}
    for p in Z["play"] + list(Z["umiejetnosci"].values()) + [Z["dluga"], Z["shard"]]:
        walki.setdefault(p["przeciwnik"], p)
    wszystkie = []
    for wrog, p in sorted(walki.items()):
        d = dziennik(p)["dziennik"]
        chwile = [z["t"] + 0.01 for z in d if z["typ"] in ("cios", "krytyk", "blok", "unik") or
                  (z["typ"] == "umiejetnosc" and z["kto"] != z["cel"])]
        if not start(s, p):
            wynik("D5 twarz %s" % wrog, False, "walka nie wystartowała")
            continue
        r = json.loads(s.luau(TWARZ.replace("__CHWILE__", ", ".join("%f" % c for c in chwile)), timeout=600))
        zle = [x for x in r if x["kat"] > KAT_TWARZY_MAKS]
        # gracz w kadrze (przegląd 15.11: po obrocie do twarzy Wojownik był ucinany lewą krawędzią)
        zgubione = [x for x in r if x["wW"] < 0.25 or x["wG"] < (GRACZ_CEL_W_KADRZE if x.get("cel") == "gracz" else GRACZ_W_KADRZE)]
        wszystkie += r
        sr = sum(x["kat"] for x in r) / max(1, len(r))
        minG = min(x["wG"] for x in r)
        minGc = min([x["wG"] for x in r if x.get("cel") == "gracz"] or [1])
        wynik("D5 twarz potwora: %s (%s/%d ziarno %d), %d trafień" % (wrog, p["klasa"], p["poziom"], p["ziarno"], len(r)),
              not zle and not zgubione,
              "kąt średnio %.0f°, najwięcej %.0f° (%s); gracz w kadrze najmniej %.0f%% (gdy obrywa od potwora %.0f%%)%s%s"
              % (sr, max(x["kat"] for x in r), max(r, key=lambda x: x["kat"])["uj"], minG * 100, minGc * 100,
                 "; ponad %d°: %s" % (KAT_TWARZY_MAKS, ["%.2f %s %.0f°" % (x["t"], x["uj"], x["kat"]) for x in zle[:4]]) if zle else "",
                 "; za mało w kadrze: %s" % ["%.2f %s cel %s G %.2f W %.2f" % (x["t"], x["uj"], x.get("cel"), x["wG"], x["wW"]) for x in zgubione[:4]] if zgubione else ""))
    return wszystkie


# ---------------------------------------------------------------------------------------------------- D4 dźwięki
DZWIEKI = r'''
local U = require(workspace.TestWalki2.Moduly.Ustawienia)
local SS = game:GetService("SoundService")
local wynik = {}
for n, d in U.DZWIEKI do
	local s = Instance.new("Sound")
	s.SoundId = d.id
	s.Volume = 0
	s.Parent = SS
	local t0 = os.clock()
	while not s.IsLoaded and os.clock() - t0 < 6 do task.wait(0.05) end
	wynik[n] = { id = d.id, zaladowany = s.IsLoaded, dlugosc = s.TimeLength }
	s:Destroy()
end
return game:GetService("HttpService"):JSONEncode(wynik)
'''


def test_dzwiek(s, Z):
    r = json.loads(s.luau(DZWIEKI, timeout=120))
    zle = [n for n, d in r.items() if not d["zaladowany"] or d["dlugosc"] <= 0]
    pliki = sorted({d["id"].split("/")[-1] for d in r.values()})
    wynik("D4 dźwięki wbudowane wczytują się (%d nazw, %d plików)" % (len(r), len(pliki)), not zle,
          ("nie wczytane: %s" % zle) if zle else "pliki: %s" % ", ".join(pliki))
    # przycisk wyciszenia: klik → wyciszone (atrybut i ikona), drugi klik → z powrotem
    p = Z["krotka"]
    if start(s, p, "{ reczny = true, tempo = 1 }"):
        s.steruj('"przewinDo", 0.5')
        time.sleep(0.3)
        s.klik("TestWalki2Cutscenka.Kadr.Dzwiek.Przycisk")
        time.sleep(0.4)
        a = s.stan()
        wyc1 = a.get("OstatnieWyciszenie")
        ik1 = s.luau('local p = game:GetService("Players").LocalPlayer.PlayerGui.TestWalki2Cutscenka.Kadr.Dzwiek.Przycisk '
                     'return tostring(p:GetAttribute("Wyciszone"))').strip()
        s.klik("TestWalki2Cutscenka.Kadr.Dzwiek.Przycisk")
        time.sleep(0.4)
        b = s.stan()
        wynik("D4 przycisk wyciszenia w interfejsie walki", wyc1 is True and ik1 == "true" and b.get("OstatnieWyciszenie") is False,
              "po 1. kliknięciu: wyciszone=%s (ikona %s), po 2.: %s" % (wyc1, ik1, b.get("OstatnieWyciszenie")))


# ---------------------------------------------------------------------------------------------------- D6 slime
SLIME = NAGLOWEK + '''
local function stan()
	local slime = scena:FindFirstChild("lesny_slime_lokalny")
	local w = { schowane = 0, widoczne = 0, glass = 0 }
	for _, n in { "BokL", "BokP", "Przod", "Tyl" } do
		local kosc = slime:FindFirstChild(n)
		for _, c in slime:GetDescendants() do
			if c:IsA("BasePart") then
				local wc = c:FindFirstChildOfClass("WeldConstraint")
				if wc and wc.Part0 == kosc then
					if c.LocalTransparencyModifier >= 1 then w.schowane += 1 else w.widoczne += 1 end
				end
			end
		end
	end
	for _, c in slime:GetDescendants() do
		if c:IsA("BasePart") and c.Material == Enum.Material.Glass then w.glass += 1 end
	end
	local g = slime:FindFirstChild("Galareta", true)
	w.galareta = g and g.Material.Name .. " " .. g.Color:ToHex()
	return w
end
S:Invoke("przewinDo", 0.6)
task.wait()
local spoczynek = stan()
-- upadek klatka po klatce: obrócony brzuszek (płat kałuży) widoczny, gdy galareta jest jeszcze wyższa niż 62%?
local slime = scena:FindFirstChild("lesny_slime_lokalny")
local soczewki, probkiUpadku, najnizej = 0, 0, 1
local t = __TH__
S:Invoke("przewinDo", t)
while t < __TR__ do
	t += 1 / 30
	S:Invoke("przewinDo", t)
	task.wait()
	local h = slime:GetAttribute("WysokoscSkory") or 1
	najnizej = math.min(najnizej, h)
	probkiUpadku += 1
	if h >= 0.62 then
		for _, n in { "BokL", "BokP", "Przod", "Tyl" } do
			local kosc = slime:FindFirstChild(n)
			local staw = kosc and kosc:FindFirstChildOfClass("Motor6D")
			local obrot = staw and (staw.Transform.LookVector:Dot(Vector3.new(0, 0, -1)) < 0.999 or staw.Transform.UpVector.Y < 0.999)
			if obrot then
				for _, c in slime:GetDescendants() do
					if c:IsA("BasePart") then
						local wc = c:FindFirstChildOfClass("WeldConstraint")
						if wc and wc.Part0 == kosc and c.LocalTransparencyModifier < 0.99 then soczewki += 1 end
					end
				end
			end
		end
	end
end
S:Invoke("przewinDo", __TR__)
task.wait()
local lezy = stan()
return HS:JSONEncode({ spoczynek = spoczynek, lezy = lezy, soczewki = soczewki, probkiUpadku = probkiUpadku, najnizej = najnizej })
'''


def test_slime(s, Z):
    p = Z["umiejetnosci"]["kwasny_plusk"]                 # wygrana Wojownika: slime kończy w kałuży
    w = dziennik(p)
    if not start(s, p):
        wynik("D6 slime", False, "walka nie wystartowała")
        return
    st = json.loads(s.steruj('"przewinDo", %f' % (w["dziennik"][-1]["t"] + 0.01)))
    s.steruj('"zamknij"')
    time.sleep(0.6)
    if not start(s, p):
        return
    r = json.loads(s.luau(SLIME.replace("__TR__", "%f" % ((st.get("tRadosc") or w["czas"]) - 0.05))
                          .replace("__TH__", "%f" % (st.get("trafienie") or w["dziennik"][-1]["t"])), timeout=300))
    sp, lz = r["spoczynek"], r["lezy"]
    wynik("D6 slime: brzuszki schowane w spoczynku, płaty kałuży widoczne po upadku, bez Glass, bez soczewek w upadku",
          sp["widoczne"] == 0 and sp["schowane"] > 0 and lz["widoczne"] > 0 and sp["glass"] == 0 and r["soczewki"] == 0
          and r["probkiUpadku"] > 10 and r["najnizej"] < 0.4,
          "spoczynek: schowane %d, widoczne %d; leży: widoczne %d; brył Glass %d; galareta %s; upadek: %d klatek, "
          "płat widoczny przy galarecie ≥ 62%%: %d razy, najniżej %.2f wysokości"
          % (sp["schowane"], sp["widoczne"], lz["widoczne"], sp["glass"], sp["galareta"], r["probkiUpadku"], r["soczewki"], r["najnizej"]))


# ---------------------------------------------------------------------------------------------------- D7 tempo
def test_tempo(s, Z):
    for nazwa, p, tempo in (("długa ×2", Z["dluga"], 2), ("finał Strażnika ×4", Z["shard"], 4), ("przegrana ×4", Z["krotka"], 4),
                            ("slime ×4", Z["umiejetnosci"]["kwasny_plusk"], 4),
                            ("Wojownik z wilkiem ×4", Z["wszystkie_typy"]["wojownik"], 4),
                            ("Mag z wilkiem ×4", Z["wszystkie_typy"]["mag"], 4)):
        w = dziennik(p)
        s.steruj('"zamknij"')
        time.sleep(0.8)
        s.ziarno(p["ziarno"])
        t0 = time.time()
        s.start(p["klasa"], p["przeciwnik"], str(p["poziom"]), "{ tempo = %d }" % tempo)
        st, _ = s.czekaj(("odtwarzanie",), 15)
        st, dt = s.czekaj(("wynik", "blad", "przerwano"), 120)
        ost = w["dziennik"][-1]
        ok = (st.get("OstatniStan") == "wynik" and st.get("OstatniaLiczbaObsluzonych") == len(w["dziennik"])
              and st.get("OstatnieBrakiChoreografii") == 0 and st.get("OstatnieBledyObslugi") == 0
              and st.get("OstatniaNiezgodnoscPaskow") == 0
              and st.get("OstatniePaskiKoniec") == "%d/%d" % (ost["hp_gracz"], ost["hp_wrog"])
              and (st.get("OstatnieUjeciePokonanego") or 0) >= 1.0 and st.get("OstatniUpadekWUjeciu") is True
              and st.get("OstatnieNapisyNakladania") == 0 and (st.get("OstatnieNapisyMaksNaraz") or 0) <= 3
              and st.get("OstatnieNapisyNaCelu") == 0 and (st.get("OstatnieDzwiekiMaksNaraz") or 0) <= 3)
        katy = [int(x.split(":")[2]) for x in (st.get("OstatnieKatyTwarzy") or "").split(",") if x]
        wynik("D7 pełna walka %s (%s/%s/%d, %d tur)" % (nazwa, p["klasa"], p["przeciwnik"], p["poziom"], w["tury"]), ok,
              "trwała %.1f s (dziennik %.1f s), zdarzenia %s/%d, braki %s, błędy %s, niezgodności pasków %s; ujęcie pokonanego "
              "%.2f s, upadek w ujęciu %s; napisy: pokazane %s, najwyżej %s przy postaci, nakładania %s, na małym celu %s "
              "(na drugiej postaci %s, głowa dużego celu %s); "
              "dźwięki: zagrane %s, pominięte %s, najwyżej %s naraz; kąt twarzy przy trafieniach: maks. %s°, śr. %.0f°"
              % (st.get("OstatniCzasTrwania") or -1, w["czas"], st.get("OstatniaLiczbaObsluzonych"), len(w["dziennik"]),
                 st.get("OstatnieBrakiChoreografii"), st.get("OstatnieBledyObslugi"), st.get("OstatniaNiezgodnoscPaskow"),
                 st.get("OstatnieUjeciePokonanego") or -1, st.get("OstatniUpadekWUjeciu"), st.get("OstatnieNapisyPokazane"),
                 st.get("OstatnieNapisyMaksNaraz"), st.get("OstatnieNapisyNakladania"), st.get("OstatnieNapisyNaCelu"),
                 st.get("OstatnieNapisyNaInnym"), st.get("OstatnieNapisyNaGlowie"),
                 st.get("OstatnieDzwiekiZagrane"), st.get("OstatnieDzwiekiPominiete"), st.get("OstatnieDzwiekiMaksNaraz"),
                 max(katy) if katy else -1, sum(katy) / max(1, len(katy))))
    s.steruj('"tempo", 1')


CZESCI = ["final", "lot", "napisy", "twarz", "dzwiek", "slime", "tempo"]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tylko", default="")
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    czesci = [c for c in a.tylko.split(",") if c] or CZESCI
    with open(os.path.join(TU, "ziarna.json"), encoding="utf-8") as f:
        Z = json.load(f)
    with SesjaPlay(a.studio) as s:
        for _ in range(40):
            if s.luau('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("LoadingScreen") '
                      'local b = g and g:FindFirstChild("Background") '
                      'return tostring(g == nil or not g.Enabled or b == nil or not b.Visible or b.BackgroundTransparency >= 0.99)').strip() == "true":
                break
            time.sleep(0.5)
        s.przy_tablicy()
        s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", true) return "ok"', "Server")
        try:
            for c in czesci:
                {"final": test_final, "lot": test_lot, "napisy": test_napisy, "twarz": test_twarz, "dzwiek": test_dzwiek,
                 "slime": test_slime, "tempo": test_tempo}[c](s, Z)
            s.steruj('"zamknij"')
        finally:
            try:
                s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", nil) workspace.TestWalki2:SetAttribute("ZiarnoTestowe", nil) return "ok"', "Server")
            except Exception:  # noqa: BLE001
                pass
        kons = s.konsola()
        zle = [w for w in kons.splitlines() if "TestWalki2" in w]
        wynik("konsola bez komunikatów z TestWalki2", not zle, "; ".join(z[:200] for z in zle[:3]))
    ok = sum(1 for w in WYNIKI if w["ok"])
    log("WYNIK: %d/%d" % (ok, len(WYNIKI)))
    sciezka = os.path.join(TU, "wynik_dopieszczenia.json")
    stare = {}
    if os.path.isfile(sciezka) and a.tylko:
        with open(sciezka, encoding="utf-8") as f:
            stare = {w["nazwa"]: w for w in json.load(f).get("wyniki", [])}
    for w in WYNIKI:
        stare[w["nazwa"]] = w
    with open(sciezka, "w", encoding="utf-8") as f:
        json.dump({"data": time.strftime("%Y-%m-%d %H:%M"), "czesci": czesci, "wyniki": list(stare.values())}, f,
                  ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
