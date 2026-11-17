#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Odtwarza w Roblox Studio kontener prototypu walki v2 (Workspace/TestWalki2) ze źródeł w tym folderze.

    python -B swiat/test_walki2/zbuduj.py              # buduje / odbudowuje kontener (idempotentnie)
    python -B swiat/test_walki2/zbuduj.py --sucho      # tylko sprawdza źródła i dane, pokazuje plan (bez Studio)
    python -B swiat/test_walki2/zbuduj.py --usun       # usuwa wygenerowany kontener (np. przed publikacją)
    python -B swiat/test_walki2/zbuduj.py --skrypty    # tylko skrypty i moduły (zrodla/, kopia silnika, tabela) — ok. 1 s
    python -B swiat/test_walki2/zbuduj.py --tylko-aktorzy k1,k2  # tylko dane i szablony tych aktorów
    python -B swiat/test_walki2/zbuduj.py --studio <studio_id>   # wymagane, gdy otwartych jest kilka okien Studio

Co powstaje (tylko w Workspace/TestWalki2 z atrybutem Wygenerowane = true):
  Moduly/      Ustawienia, Klipy, Aktorzy, TabelaAktorow (z aktorzy.py + zasięg broni i pierś z geometria.py),
               DaneAktorow/<klucz> (klipy z dane/<klucz>.json); etap 2: Wzorcowe (postać wzorcowa dla serwera),
               Choreografie, Efekty3D, InterfejsWalki2, WyborWalki2, OdtwarzaczWalki2; v3: PlanWalki (czysta logika
               dziennika v3), PamiecWalk (pamięć pomijania walk — serwer),
               Walka/ — KOPIA silnika z src/server/Walka robiona przy każdej budowie (jedno źródło prawdy zostaje
               w src/), Dziennik — kopia src/shared/Walka/Dziennik.luau; każda kopia dostaje na początku strażnika Studio
  Aktorzy/     szablony aktorów (rigi z klocków, Motor6D, punkty Punkt_*), stoją w galerii na północ od podestu
  Galeria/     cokoły z tabliczkami
  Arena/       leśna polana z podestem, las w tle, tablica z (wyłączoną) podpowiedzią, świecący słup
  Zdalne/RozpocznijWalke2 i Zdalne/PominiecieWalki2 (RemoteFunction; v3: pomijanie walk, D-078),
  Sygnaly/PokazAktora i Sygnaly/Sterowanie (haczyki testowe),
  SerwerWalki2 (Server), KlientWalki2 (Client)
Dane aktorów przygotowuje wcześniej aktorzy.py (Blender tylko tam); ta budowa Blendera nie woła.

Zasady bezpieczeństwa (wspólne miejsce Team Create) — jak w swiat/test_walki_roblox/zbuduj.py:
- wszystko trafia do JEDNEGO kontenera Workspace/TestWalki2 z atrybutem Wygenerowane = true; odbudowa i --usun
  ruszają TYLKO ten kontener — jeśli pod tą nazwą jest coś bez atrybutu, skrypt przerywa;
- przed budową sprawdzane jest, czy w pudle sceny nie stoi nic obcego (GetPartBoundsInBox, bez płyty Baseplate);
- przed i po budowie punkt historii (ChangeHistoryService) — całość cofa się przez Ctrl+Z;
- każdy skrypt i moduł w kontenerze zaczyna się od strażnika „poza Studio nic nie rób” (sprawdzane przed wysłaniem);
- tylko tryb Edit; niczego nie publikuje, nie zapisuje miejsca, nie zmienia Lighting;
- okno Studio wybiera swiat/test_walki_roblox/cel_studio.py (jedno okno albo --studio, zawsze placeId gry,
  sprawdzany jeszcze raz w Studio przez game.PlaceId).
"""
import argparse
import math
import os
import re
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (REPO, os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"), TU):
    if _s not in sys.path:
        sys.path.insert(0, _s)
from cel_studio import MIEJSCE, wybierz_studio  # noqa: E402  (wybór okna jak w v1 — plik v1 tylko czytamy)
import aktorzy as A  # noqa: E402

KONTENER = "TestWalki2"
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
STRAZNIK_MODULU = 'if not game:GetService("RunService"):IsStudio() then\n\treturn {}\nend\n'

# (plik źródłowy, klasa, ścieżka w kontenerze, RunContext)
SKRYPTY = [
    ("zrodla/Ustawienia.luau", "ModuleScript", "Moduly/Ustawienia", None),
    ("zrodla/Klipy.luau", "ModuleScript", "Moduly/Klipy", None),
    ("zrodla/Aktorzy.luau", "ModuleScript", "Moduly/Aktorzy", None),
    # etap 2: serwer, odtwarzacz, interfejs
    ("zrodla/Wzorcowe.luau", "ModuleScript", "Moduly/Wzorcowe", None),
    ("zrodla/Choreografie.luau", "ModuleScript", "Moduly/Choreografie", None),
    # v3 (17.11): czysta logika odtwarzacza (dziennik v3) i pamięć pomijania walk (D-078, tylko serwer jej używa)
    ("zrodla/PlanWalki.luau", "ModuleScript", "Moduly/PlanWalki", None),
    ("zrodla/PamiecWalk.luau", "ModuleScript", "Moduly/PamiecWalk", None),
    ("zrodla/Efekty3D.luau", "ModuleScript", "Moduly/Efekty3D", None),
    ("zrodla/InterfejsWalki2.luau", "ModuleScript", "Moduly/InterfejsWalki2", None),
    ("zrodla/WyborWalki2.luau", "ModuleScript", "Moduly/WyborWalki2", None),
    ("zrodla/OdtwarzaczWalki2.luau", "ModuleScript", "Moduly/OdtwarzaczWalki2", None),
    ("zrodla/SerwerWalki2.server.luau", "Script", "SerwerWalki2", "Server"),
    ("zrodla/KlientWalki2.client.luau", "Script", "KlientWalki2", "Client"),
]
# kopia silnika walki v2 (źródło prawdy: src/) — kolejność bez znaczenia, moduły szukają się przez script.Parent
SILNIK = [("src/server/Walka/%s.luau" % n, "Moduly/Walka/%s" % n)
          for n in ("Dane", "Los", "Statystyki", "Przeciwnicy", "Umiejetnosci", "Silnik")]
SILNIK.append(("src/shared/Walka/Dziennik.luau", "Moduly/Dziennik"))
FOLDERY = ["Moduly", "Moduly/Walka", "Moduly/DaneAktorow", "Zdalne", "Sygnaly", "Aktorzy", "Galeria"]
SYGNALY = ["PokazAktora"]
# (klasa, ścieżka) — zdalna funkcja walki i haczyk testowy klienta (etap 2)
INNE = [("RemoteFunction", "Zdalne/RozpocznijWalke2"), ("BindableFunction", "Sygnaly/Sterowanie"),
        ("RemoteFunction", "Zdalne/PominiecieWalki2")]  # v3: pomijanie walk (D-078) — zgoda i zgłoszenie

START = r'''
local CH = game:GetService("ChangeHistoryService")
local RunService = game:GetService("RunService")
if RunService:IsRunning() then
	return "STOP: Studio jest w trybie Play — buduję tylko w trybie Edit"
end
if game.PlaceId ~= __MIEJSCE__ then
	return "STOP: otwarte miejsce ma placeId " .. tostring(game.PlaceId) .. ", a nie __MIEJSCE__ — nie buduję w cudzym miejscu"
end
local nazwa = "__KONTENER__"
local stare = {}
for _, d in workspace:GetChildren() do
	if d.Name == nazwa then
		if d:GetAttribute("Wygenerowane") ~= true then
			return "STOP: w Workspace jest obiekt '" .. nazwa .. "' bez atrybutu Wygenerowane — nie ruszam cudzej pracy"
		end
		table.insert(stare, d)
	end
end
if __USUN__ then
	if #stare == 0 then
		return "USUNIETO (kontenera nie było)"
	end
	CH:SetWaypoint("TestWalki2: przed usunięciem")
	for _, d in stare do d:Destroy() end
	CH:SetWaypoint("TestWalki2: usunięto")
	return "USUNIETO"
end
-- czy miejsce jest wolne: nic poza płytą Baseplate i (starym) własnym kontenerem
local filtr = OverlapParams.new()
filtr.FilterType = Enum.RaycastFilterType.Exclude
local wyklucz = table.clone(stare)
local plyta = workspace:FindFirstChild("Baseplate")
if plyta then table.insert(wyklucz, plyta) end
filtr.FilterDescendantsInstances = wyklucz
local obce = workspace:GetPartBoundsInBox(CFrame.new(__OBSZAR_SRODEK__), Vector3.new(__OBSZAR_ROZMIAR__), filtr)
if #obce > 0 then
	local lista = {}
	for i = 1, math.min(#obce, 5) do table.insert(lista, obce[i]:GetFullName()) end
	return "STOP: w miejscu sceny stoi coś obcego (" .. #obce .. " części), np. " .. table.concat(lista, ", ")
end
CH:SetWaypoint("TestWalki2: przed budową")
for _, d in stare do d:Destroy() end
local f = Instance.new("Folder")
f.Name = nazwa
f:SetAttribute("Wygenerowane", true)
f:SetAttribute("Zrodlo", "swiat/test_walki2")
f:SetAttribute("Zbudowano", "__CZAS__")
for _, sciezka in { __FOLDERY__ } do
	local rodzic = f
	local czesci = string.split(sciezka, "/")
	for i = 1, #czesci - 1 do rodzic = rodzic:FindFirstChild(czesci[i]) end
	local d = Instance.new("Folder")
	d.Name = czesci[#czesci]
	d.Parent = rodzic
end
for _, n in { __SYGNALY__ } do
	local b = Instance.new("BindableEvent")
	b.Name = n
	b.Parent = f.Sygnaly
end
f.Parent = workspace
return "OK"
'''

# zdalna funkcja i haczyki (idempotentnie; także przy --skrypty na starym kontenerze)
INNE_KOD = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera"
end
local zrobione = {}
for _, w in { __INNE__ } do
	local sciezka = string.split(w[2], "/")
	local rodzic = f
	for i = 1, #sciezka - 1 do
		rodzic = rodzic:FindFirstChild(sciezka[i])
		if not rodzic then return "STOP: brak folderu " .. sciezka[i] end
	end
	local stary = rodzic:FindFirstChild(sciezka[#sciezka])
	if not stary or stary.ClassName ~= w[1] then
		if stary then stary:Destroy() end
		local o = Instance.new(w[1])
		o.Name = sciezka[#sciezka]
		o.Parent = rodzic
		table.insert(zrobione, w[2])
	end
end
return "OK (" .. #zrobione .. " nowych)"
'''

SKRYPT = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera"
end
local sciezka = string.split("__SCIEZKA__", "/")
local rodzic = f
for i = 1, #sciezka - 1 do
	rodzic = rodzic:FindFirstChild(sciezka[i])
	if not rodzic then return "STOP: brak folderu " .. sciezka[i] end
end
local stary = rodzic:FindFirstChild(sciezka[#sciezka])
if stary then stary:Destroy() end
local s = Instance.new("__KLASA__")
s.Name = sciezka[#sciezka]
__RUNCONTEXT__
s.Source = __ZRODLO__
s.Parent = rodzic
return "OK " .. s:GetFullName() .. " (" .. #s.Source .. " znaków)"
'''

# --skrypty: napisy tablicy prototypu jak w budowa/arena.luau (bez przebudowy areny) — 17.11.2026 „PRÓBA WALKI”
# zamiast „WALKA v2”; tylko teksty istniejących obiektów w Arena/Tablica naszego kontenera
NAPISY_TABLICY = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then return "STOP: brak kontenera" end
local tablica = f:FindFirstChild("Tablica", true)
local deska = tablica and tablica:FindFirstChild("Deska")
if not deska then return "brak Tablica/Deska — bez zmian" end
local zmiany = 0
local sg = deska:FindFirstChild("Napis")
if sg then
	for _, t in sg:GetChildren() do
		if t:IsA("TextLabel") and t.Text == "WALKA v2" then t.Text = "PRÓBA WALKI" zmiany += 1 end
	end
end
local p = deska:FindFirstChild("PodpowiedzWalki2")
if p and p.ObjectText == "Walka v2 (prototyp)" then p.ObjectText = "Próba walki (prototyp)" zmiany += 1 end
return "OK (" .. zmiany .. " napisów)"
'''

KONIEC = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f then return "STOP: brak kontenera" end
local ile = {}
local razem = 0
for _, d in f:GetDescendants() do
	razem += 1
	local k = if d:IsA("BasePart") then "części" elseif d:IsA("LuaSourceContainer") then "skrypty" else nil
	if k then ile[k] = (ile[k] or 0) + 1 end
end
local wAktorach = 0
for _, d in f.Aktorzy:GetDescendants() do
	if d:IsA("BasePart") then wAktorach += 1 end
end
game:GetService("ChangeHistoryService"):SetWaypoint("TestWalki2: zbudowano")
return "instancji: " .. razem .. ", części: " .. (ile["części"] or 0) .. " (w szablonach aktorów " .. wAktorach .. "), skryptów: " .. (ile["skrypty"] or 0)
'''


def bez_komentarzy_na_poczatku(tekst):
    """Kod bez wiodących komentarzy i pustych linii (do sprawdzenia strażnika)."""
    t = tekst.lstrip()
    while True:
        if t.startswith("--[["):
            koniec = t.find("]]")
            if koniec < 0:
                return ""
            t = t[koniec + 2:].lstrip()
        elif t.startswith("--"):
            t = t.split("\n", 1)[1].lstrip() if "\n" in t else ""
        else:
            return t


def dlugi_napis(tekst):
    """Tekst jako literał Luau [==[ … ]==] z poziomem, którego nie ma w treści."""
    poziom = 3
    while ("]" + "=" * poziom + "]") in tekst or ("[" + "=" * poziom + "[") in tekst:
        poziom += 1
    return "[" + "=" * poziom + "[\n" + tekst + "]" + "=" * poziom + "]"


def luau(v):
    """Wartość Pythona jako literał Luau (słownik → tabela z kluczami-identyfikatorami, None → false)."""
    import json
    if v is None:
        return "false"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return repr(round(v, 5))
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, (list, tuple)):
        return "{" + ",".join(luau(x) for x in v) + "}"
    if isinstance(v, dict):
        czesci = []
        for k, x in v.items():
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", str(k)):
                czesci.append("%s=%s" % (k, luau(x)))
            else:
                czesci.append("[%s]=%s" % (luau(str(k)), luau(x)))
        return "{" + ",".join(czesci) + "}"
    raise TypeError(type(v))


def wczytaj(sciezka):
    with open(sciezka, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def z_ustawien(nazwa):
    m = re.search(r"U\.%s\s*=\s*Vector3\.new\(([^)]*)\)" % nazwa, wczytaj(os.path.join(TU, "zrodla", "Ustawienia.luau")))
    if not m:
        sys.exit("Nie znalazłem U.%s w zrodla/Ustawienia.luau" % nazwa)
    return [float(x) for x in m.group(1).split(",")]


def geometria_ciosu(d):
    """Dla odtwarzacza (etap 2): zasięg punktu Bron do przodu w chwili trafienia każdego klipu z `chwile`
    (studs od punktu na ziemi pod aktorem) i jak daleko z przodu jest pierś (punkt Piers) w spoczynku.
    Ta sama kinematyka co Motor6D (geometria.py), więc doskok w walce kończy się bronią przy piersi celu."""
    from geometria import Rig, punkt
    r = Rig(d)
    pk = {p[0]: p for p in d["punkty"]}
    wynik = {"zasiegi": {}, "boki": {}, "piersPrzod": 0.6, "torBroni": {}}
    if "Piers" in pk:
        p = pk["Piers"]
        wynik["piersPrzod"] = round(max(0.3, -punkt(r.pozy()[p[1]], tuple(p[2:5]))[2]), 3)
    if "Bron" in pk:
        b = pk["Bron"]
        for klip, s in d.get("chwile", {}).items():
            if klip not in r.klipy:
                continue
            kl = r.klipy[klip]
            f = max(0, min(kl["dl"], int(round(s * kl["fps"]))))
            q = punkt(r.pozy(r.transformy(klip, f))[b[1]], tuple(b[2:5]))
            wynik["zasiegi"][klip] = round(max(0.5, -q[2]), 3)
            wynik["boki"][klip] = round(q[0], 3)  # w prawo od osi aktora (rig: prawa +X) — do celowania (etap 9)
            # tor broni (17.11.2026): wysokość punktu Bron nad ziemią w 8 klatkach przed chwilą trafienia i w niej —
            # odtwarzacz wręcz przesuwa trafienie na chwilę, w której broń schodzi do wierzchu NISKIEGO celu (krytyk
            # Wojownika przy wilku: miecz w chwili z modułu jest już przy ziemi, błysk spóźniał się o ok. 0,05 s sceny)
            ys = []
            for g in range(max(0, f - 8), f + 1):
                ys.append(round(punkt(r.pozy(r.transformy(klip, g))[b[1]], tuple(b[2:5]))[1], 3))
            wynik["torBroni"][klip] = {"od": max(0, f - 8), "fps": kl["fps"], "y": ys}
    return wynik


def celowanie(w, geo):
    """Wpis „celowanie” z tabeli aktorów → {klip: kąt w radianach, + = obrót w lewo}: o tyle odtwarzacz obraca atakującego
    na czas doskoku, żeby punkt Bron w chwili trafienia leżał na osi celu (atan(bok / przód); zasięg rośnie wtedy do
    przód / cos(kąt), co liczy odtwarzacz w `odlegloscCiosu`)."""
    wynik = {}
    for klip in w.get("celowanie", []):
        if klip not in geo["zasiegi"]:
            sys.exit("%s: klip %s z „celowanie” nie ma chwili trafienia ani punktu Bron" % (w["klucz"], klip))
        wynik[klip] = round(math.atan2(geo["boki"][klip], geo["zasiegi"][klip]), 4)
    return wynik


def obwiednia_lezenia(d):
    """Obwiednia brył w ostatniej klatce klipu „upadek” (układ rigu: przód −Z, prawa +X, ziemia y = 0) — odtwarzacz
    kadruje z niej ujęcie pokonanego i pilnuje, żeby objazd w finale nie wjeżdżał w leżącego (np. stos głazów).
    Bez skórowania (galareta slime'a rozlewa się jeszcze siatką, ale jest mała)."""
    from geometria import Rig, obwiednia
    r = Rig(d)
    klip = next((k for k in d["klipy"] if k["n"] == "upadek"), None)
    if not klip:
        return None
    mn, mx = obwiednia(r, r.pozy(r.transformy("upadek", klip["dl"])))
    return {"mn": [round(v, 2) for v in mn], "mx": [round(v, 2) for v in mx]}


def chowane_kosci(d, w):
    """Wpis „chowane” z tabeli aktorów → [[indeks kości, [kierunek na zewnątrz], próg]] dla modułu Klipy."""
    indeks = {k[0]: i + 1 for i, k in enumerate(d["kosci"])}
    wynik = []
    for nazwa, (kier, prog) in (w.get("chowane") or {}).items():
        if nazwa not in indeks:
            sys.exit("%s: kość %s z „chowane” nie istnieje w rigu" % (w["klucz"], nazwa))
        wynik.append([indeks[nazwa], [float(v) for v in kier], float(prog)])
    return wynik


def wyglad_roblox(d, w):
    """Wygląd brył na rigu z klocków (wpis „wyglad_roblox”): podmiana materiałów i kolorów tylko w prototypie —
    plik modelu i dane z Blendera zostają bez zmian. Zwraca nowe listy (materialy, czesci)."""
    wr = w.get("wyglad_roblox") or {}
    materialy = [list(m) for m in d["materialy"]]
    for i, m in enumerate(materialy):
        if m[0] in (wr.get("materialy") or {}):
            nowy = wr["materialy"][m[0]]
            materialy[i] = [nowy[0], float(nowy[1])]
    kolory = {k.upper(): v.upper() for k, v in (wr.get("kolory") or {}).items()}
    czesci = []
    for c in d["czesci"]:
        c = list(c)
        if c[12].upper() in kolory:
            c[12] = kolory[c[12].upper()]
        czesci.append(c)
    return materialy, czesci


def moduly_danych():
    """(ścieżka, źródło) modułów wygenerowanych z tabeli aktorów i dane/<klucz>.json, plus dane do szablonów."""
    naglowek = "-- Wygenerowane przez swiat/test_walki2/zbuduj.py z %s — nie edytuj ręcznie.\n" + STRAZNIK_MODULU
    tabela = {"kolejnosc": [w["klucz"] for w in A.AKTORZY], "akcje": A.AKCJE, "aktorzy": {}}
    dane_aktorow, szablony = [], []
    for w in A.AKTORZY:
        d = A.wczytaj(w["klucz"])
        wym = d["wymiary"]
        proceduralne = [a for a in A.AKCJE if not w["klipy"].get(a)]
        proceduralne += [u for u, k in w["umiejetnosci"].items() if not k]
        tabela["aktorzy"][w["klucz"]] = {
            "klucz": w["klucz"], "rola": w["rola"], "nazwa": w["nazwa"], "model": w["model"],
            "zastepczy": w["zastepczy"] or False,
            "klipy": {a: w["klipy"].get(a) or False for a in A.AKCJE},
            "umiejetnosci": {u: k or False for u, k in w["umiejetnosci"].items()},
            "chwile": d["chwile"],
            "dlugosci": {k["n"]: round(k["dl"] / float(k["fps"]), 3) for k in d["klipy"]},
            "proceduralne": proceduralne,
            "zastepczeKlipy": w.get("zastepcze_klipy", []),
            # klipy z własnym ruchem całej postaci: odtwarzacz nie dokłada ślizgu / odrzutu / podskoku (aktorzy.py)
            "ruchWKlipie": {k: True for k in w.get("ruch_w_klipie", [])},
            "wysokosc": wym["wysokosc"], "promien": wym["promien"], "przod": wym["przod"],
            "szerokosc": wym["szerokosc"], "glebokosc": wym["glebokosc"], "pasek": round(wym["wysokosc"] + 0.9, 2),
            "hrp": d["hrp"], "punkty": [p[0] for p in d["punkty"]],
            "liczbaCzesci": len(d["czesci"]),
            "lezy": obwiednia_lezenia(d) or False,
        }
        geo = geometria_ciosu(d)
        tabela["aktorzy"][w["klucz"]].update(geo)
        # celowanie (etap 9): obrót atakującego na czas doskoku, żeby broń spadła na oś celu (miażdżący cios)
        tabela["aktorzy"][w["klucz"]]["obrotCiosu"] = celowanie(w, geo)
        # ręczne zasięgi z tabeli (klip „trafia” dalej niż punkt Bron: kałuża kwasu, środek uścisku korzeni)
        tabela["aktorzy"][w["klucz"]]["zasiegi"].update({k: float(v) for k, v in (w.get("zasiegi") or {}).items()})
        # moduł aktora: kości + klipy z modułów-dzieci (jeden klip = jeden moduł: Source ma limit 200 000 znaków)
        sciezka = "Moduly/DaneAktorow/" + w["klucz"]
        glowny = (naglowek % ("dane/%s.json" % w["klucz"]) +
                  "local klipy = {}\nfor _, m in script:GetChildren() do\n\tif m:IsA(\"ModuleScript\") then\n"
                  "\t\tklipy[m.Name] = require(m)\n\tend\nend\n" +
                  "return { klucz = %s, kosci = %s, klipy = klipy, skora = %s, wydluzenia = %s, chowane = %s }\n"
                  % (luau(w["klucz"]), luau([[k[0], k[1], k[11]] for k in d["kosci"]]), luau(d.get("skora", [])),
                     luau(d.get("wydluzenia", {})), luau(chowane_kosci(d, w))))
        dane_aktorow.append((sciezka, glowny))
        for k in d["klipy"]:
            klip = {"fps": k["fps"], "petla": k["petla"], "dl": k["dl"], "kosci": k["kosci"], "klatki": k["klatki"]}
            dane_aktorow.append((sciezka + "/" + k["n"], naglowek % ("dane/%s.json, klip %s" % (w["klucz"], k["n"])) +
                                 "return " + luau(klip) + "\n"))
        szablony.append((w, d))
    zrodlo_tabeli = naglowek % "aktorzy.py (TABELA AKTORÓW)" + "return " + luau(tabela) + "\n"
    return [("Moduly/TabelaAktorow", zrodlo_tabeli)] + dane_aktorow, szablony


def dane_szablonow(szablony):
    """Dane do budowa/szablon.luau: rig + miejsce w galerii (rząd od zachodu na wschód, przodem na północ)."""
    start = z_ustawien("GALERIA_START")
    krok = float(re.search(r"U\.GALERIA_KROK\s*=\s*([0-9.]+)", wczytaj(os.path.join(TU, "zrodla", "Ustawienia.luau"))).group(1))
    x = start[0]
    wynik = []
    for w, d in szablony:
        wym = d["wymiary"]
        # aktor patrzy na północ (−Z świata): jego prawa strona (+X rigu) jest na zachodzie, więc szerokość liczymy po X
        x += wym["szerokosc"] / 2.0
        materialy, czesci = wyglad_roblox(d, w)
        dane = {"klucz": w["klucz"], "nazwa": w["nazwa"], "rola": w["rola"], "zastepczy": w["zastepczy"] or "",
                "poz": [round(x, 3), start[1] + 0.5, start[2]], "patrz": [0, -1],
                "hrp": d["hrp"], "kosci": d["kosci"], "czesci": czesci, "grupy": d["grupy"],
                "materialy": materialy, "zaczepy": d["zaczepy"], "punkty": d["punkty"],
                "szer": wym["szerokosc"], "glab": wym["glebokosc"], "przod": wym["przod"]}
        x += wym["szerokosc"] / 2.0 + krok
        wynik.append(dane)
    return wynik


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje kontener prototypu walki v2 w Roblox Studio")
    ap.add_argument("--usun", action="store_true", help="usuń wygenerowany kontener")
    ap.add_argument("--sucho", action="store_true", help="tylko sprawdź źródła i pokaż plan")
    ap.add_argument("--studio", default=None, help="studio_id (wymagane, gdy otwartych jest kilka okien Studio)")
    ap.add_argument("--tylko-aktorzy", default="", help="przebuduj tylko te szablony i ich dane (klucze po przecinku); "
                                                         "reszta kontenera zostaje")
    ap.add_argument("--skrypty", action="store_true", help="wyślij tylko skrypty i moduły (zrodla/, kopia silnika, "
                                                           "tabela aktorów) do istniejącego kontenera — bez areny i szablonów")
    a = ap.parse_args()

    # --- źródła: (ścieżka w kontenerze, klasa, RunContext, źródło)
    zrodla = []
    for plik, klasa, sciezka, kontekst in SKRYPTY:
        tekst = wczytaj(os.path.join(TU, plik))
        zrodla.append((sciezka, klasa, kontekst, tekst, plik))
    for plik, sciezka in SILNIK:
        tekst = wczytaj(os.path.join(REPO, plik))
        kopia = ("-- KOPIA %s zrobiona przez swiat/test_walki2/zbuduj.py (%s) — źródło prawdy jest w repozytorium.\n"
                 % (plik, time.strftime("%Y-%m-%d"))) + STRAZNIK_MODULU + tekst
        zrodla.append((sciezka, "ModuleScript", None, kopia, plik))
    generowane, szablony = moduly_danych()
    for sciezka, tekst in generowane:
        zrodla.append((sciezka, "ModuleScript", None, tekst, "(wygenerowany)"))
    for sciezka, klasa, kontekst, tekst, plik in zrodla:
        if not bez_komentarzy_na_poczatku(tekst).startswith(STRAZNIK):
            sys.exit("BŁĄD: %s (%s) nie zaczyna się od strażnika „%s”" % (sciezka, plik, STRAZNIK))
    budowa_areny = wczytaj(os.path.join(TU, "budowa", "arena.luau"))
    szablon_kod = wczytaj(os.path.join(TU, "budowa", "szablon.luau"))
    dane_sz = dane_szablonow(szablony)
    tylko = [k for k in a.tylko_aktorzy.split(",") if k]
    for k in tylko:
        if k not in A.PO_KLUCZU:
            sys.exit("nie ma aktora %r" % k)
    obszar_s, obszar_r = z_ustawien("OBSZAR_SRODEK"), z_ustawien("OBSZAR_ROZMIAR")

    print("Kontener: Workspace/%s · pudło sceny: środek %s, rozmiar %s · modułów i skryptów: %d · aktorów: %d"
          % (KONTENER, obszar_s, obszar_r, len(zrodla), len(dane_sz)))
    for sciezka, klasa, kontekst, tekst, plik in zrodla:
        print("  %-34s → %s %s%s (%d znaków)" % (plik if plik != "(wygenerowany)" else "(z tabeli / danych)", klasa, sciezka,
                                                  " [RunContext=%s]" % kontekst if kontekst else "", len(tekst)))
    for d in dane_sz:
        print("  aktor %-15s %3d brył, galeria x = %6.1f" % (d["klucz"], len(d["czesci"]), d["poz"][0]))
    if a.sucho:
        return

    from studio_mcp import StudioMCP, StudioError
    try:
        with StudioMCP() as s:
            sid = wybierz_studio(s, a.studio)
            stan = s.call("get_studio_state", {"studio_id": sid})["text"]
            if "Current Studio Mode: Edit" not in stan:
                sys.exit("Studio nie jest w trybie Edit — zatrzymaj Play i spróbuj ponownie.\n" + stan)

            def wykonaj(kod):
                kod = ('if game.PlaceId ~= %d then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end\n'
                       % MIEJSCE) + kod
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
                if r["is_error"]:
                    raise StudioError(r["text"][:3000])
                w = r["text"].strip()
                if w.startswith("STOP"):
                    print(w)
                    sys.exit(2)
                return w

            def wyslij_skrypt(sciezka, klasa, kontekst, tekst):
                kod = (SKRYPT.replace("__KONTENER__", KONTENER).replace("__SCIEZKA__", sciezka).replace("__KLASA__", klasa)
                       .replace("__RUNCONTEXT__", "s.RunContext = Enum.RunContext.%s" % kontekst if kontekst else ""))
                kod = kod.replace("__ZRODLO__", dlugi_napis(tekst))
                return wykonaj(kod)

            t0 = time.time()
            inne_kod = (INNE_KOD.replace("__KONTENER__", KONTENER)
                        .replace("__INNE__", ", ".join("{%s, %s}" % (luau(k), luau(p)) for k, p in INNE)))
            if a.skrypty:
                wykonaj('local f = workspace:FindFirstChild("%s") if not f or f:GetAttribute("Wygenerowane") ~= true '
                        'then return "STOP: brak kontenera — zbuduj całość" end '
                        'game:GetService("ChangeHistoryService"):SetWaypoint("TestWalki2: przed wymianą skryptów") return "OK"' % KONTENER)
                print("  zdalne i haczyki:", wykonaj(inne_kod))
                print("  napisy tablicy:", wykonaj(NAPISY_TABLICY.replace("__KONTENER__", KONTENER)))
                for sciezka, klasa, kontekst, tekst, plik in zrodla:
                    if not sciezka.startswith("Moduly/DaneAktorow/"):
                        print("  skrypt:", wyslij_skrypt(sciezka, klasa, kontekst, tekst))
                print("gotowe: %s (%.0f s)" % (wykonaj(KONIEC.replace("__KONTENER__", KONTENER)), time.time() - t0))
                return
            if tylko:
                # częściowa przebudowa: kontener musi istnieć; nowe dane i szablony wybranych aktorów
                wykonaj('local f = workspace:FindFirstChild("%s") if not f or f:GetAttribute("Wygenerowane") ~= true '
                        'then return "STOP: brak kontenera — zbuduj całość" end '
                        'game:GetService("ChangeHistoryService"):SetWaypoint("TestWalki2: przed przebudową aktorów") return "OK"' % KONTENER)
                for sciezka, klasa, kontekst, tekst, plik in zrodla:
                    if sciezka == "Moduly/TabelaAktorow" or any(
                            sciezka == "Moduly/DaneAktorow/" + k or sciezka.startswith("Moduly/DaneAktorow/" + k + "/")
                            for k in tylko):
                        print("  skrypt:", wyslij_skrypt(sciezka, klasa, kontekst, tekst))
                for d in dane_sz:
                    if d["klucz"] in tylko:
                        print("  szablon:", wykonaj(szablon_kod.replace("__DANE__", luau(d))))
                print("gotowe: %s (%.0f s)" % (wykonaj(KONIEC.replace("__KONTENER__", KONTENER)), time.time() - t0))
                return
            wynik = wykonaj(START.replace("__KONTENER__", KONTENER).replace("__USUN__", "true" if a.usun else "false")
                            .replace("__MIEJSCE__", str(MIEJSCE))
                            .replace("__OBSZAR_SRODEK__", ", ".join(repr(v) for v in obszar_s))
                            .replace("__OBSZAR_ROZMIAR__", ", ".join(repr(v) for v in obszar_r))
                            .replace("__FOLDERY__", ", ".join(luau(x) for x in FOLDERY))
                            .replace("__SYGNALY__", ", ".join(luau(x) for x in SYGNALY))
                            .replace("__CZAS__", time.strftime("%Y-%m-%dT%H:%M:%S")))
            print("start:", wynik)
            if a.usun or not wynik.endswith("OK"):
                return
            print("  zdalne i haczyki:", wykonaj(inne_kod))
            for sciezka, klasa, kontekst, tekst, plik in zrodla:
                print("  skrypt:", wyslij_skrypt(sciezka, klasa, kontekst, tekst))
            print("  arena:", wykonaj(budowa_areny))
            for d in dane_sz:
                print("  szablon:", wykonaj(szablon_kod.replace("__DANE__", luau(d))))
            print("gotowe: %s (%.0f s)" % (wykonaj(KONIEC.replace("__KONTENER__", KONTENER)), time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
