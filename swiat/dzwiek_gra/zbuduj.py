#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pakiet „dźwięk gry” — buduje w Roblox Studio kontener Workspace/DzwiekGra (katalog dźwięków i muzyka stref).

    python -B swiat/dzwiek_gra/zbuduj.py --sucho                     # bez Studio: odśwież KatalogDzwiekow.luau, sprawdź, plan
    python -B swiat/dzwiek_gra/zbuduj.py                             # buduje / odbudowuje Workspace/DzwiekGra (tryb Edit)
    python -B swiat/dzwiek_gra/zbuduj.py --skrypty                   # tylko moduł katalogu, skrypt muzyki i haczyk
    python -B swiat/dzwiek_gra/zbuduj.py --usun                      # usuwa Workspace/DzwiekGra
    python -B swiat/dzwiek_gra/zbuduj.py --identyfikatory plik.json  # wpisz identyfikatory po wgraniu (+ --skrypty)
    python -B swiat/dzwiek_gra/zbuduj.py --identyfikatory plik.json --sucho   # tylko zapis w repozytorium
    python -B swiat/dzwiek_gra/zbuduj.py --studio <studio_id>        # gdy otwartych jest kilka okien Studio

Co powstaje (tylko w Workspace/DzwiekGra z atrybutem Wygenerowane = true; bez części):
  Moduly/KatalogDzwiekow  (ModuleScript, WYGENEROWANY tu z assets/audio/arkusz/sfx_arkusz_a.json, map arkuszy muzyki
                          (assets/audio/arkusz/muzyka_arkusz_*.json), ustawienia.json i identyfikatory.json — także
                          plik zrodla/KatalogDzwiekow.luau w repozytorium)
  MuzykaStref             (Script, RunContext = Client) — muzyka stref i kontekstów (walka, walka ze Strażnikiem,
                          mini-gry Training Center); utwór może być osobnym plikiem albo odcinkiem arkusza muzyki
  Sygnaly/SterowanieMuzyki (BindableFunction, haczyk testowy klienta)
Odtwarzacz walki prototypu (swiat/test_walki2/zrodla/OdtwarzaczWalki2.luau) sam czyta Moduly/KatalogDzwiekow: gdy
kontener jest i arkusz ma identyfikator ≠ 0, zdarzenia walki grają odcinki arkusza; inaczej zostają wbudowane dźwięki.

--identyfikatory przyjmuje JSON w jednej z dwóch postaci:
  {"arkusz": 123, "arkusze_muzyki": {"muzyka_arkusz_b": 789}, "muzyka": {"muzyka_06_bagno_petla": 456, …}}
  {"wgrane": [{"plik": "assets/audio/arkusz/sfx_arkusz_a.ogg", "assetId": "123"}, …]}   (assets/audio/wgrane.json:
      …/sfx_arkusz_*.ogg = arkusz efektów, …/muzyka_arkusz_*.ogg = arkusz muzyki, …/muzyka_XX_…_petla.ogg = utwór)
Nazwy spoza listy i liczby ≤ 0 są błędem (nic nie zapisujemy). Plik repozytorium: swiat/dzwiek_gra/identyfikatory.json.

Zasady (wspólne miejsce Team Create, jak swiat/las_potwory/zbuduj.py): tylko własny kontener z atrybutem
Wygenerowane; cudze kontenery (MiasteczkoBazar, LasPas, TestWalki2) tylko CZYTAMY (skrypt muzyki sprawdza, czy są);
punkt historii przed i po; strażnik Studio w każdym skrypcie; tylko tryb Edit; niczego nie zapisuje, nie publikuje,
nie wgrywa i nie zmienia Lighting.
"""
import argparse
import hashlib
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
sys.path.insert(0, os.path.join(REPO, "swiat", "las_potwory"))
import sprawdz_luau as SL  # noqa: E402  (wspólna kontrola Luau pakietów lasu)

KONTENER = "DzwiekGra"
ZRODLO = "swiat/dzwiek_gra"
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
STRAZNIK_MODULU = 'if not game:GetService("RunService"):IsStudio() then\n\treturn {}\nend\n'
USTAWIENIA = os.path.join(TU, "ustawienia.json")
IDENTYFIKATORY = os.path.join(TU, "identyfikatory.json")
KATALOG = os.path.join(TU, "zrodla", "KatalogDzwiekow.luau")
MUZYKA = os.path.join(TU, "zrodla", "MuzykaStref.client.luau")
MUZYKA_PLIKI = os.path.join(REPO, "assets", "audio", "muzyka")
FOLDERY = ["Moduly", "Sygnaly"]
INNE = [("BindableFunction", "Sygnaly/SterowanieMuzyki")]
LIMIT_ZRODLA = 199000
KONTEKSTY = ("walka", "walka_straznik", "trening")   # konteksty muzyki, które zna MuzykaStref

NAGLOWEK_MIEJSCA = ('if game.PlaceId ~= __MIEJSCE__ then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end\n'
                    'if game:GetService("RunService"):IsRunning() then return "STOP: Studio jest w trybie Play — buduję tylko w trybie Edit" end\n')

START = r'''
local CH = game:GetService("ChangeHistoryService")
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
	if #stare == 0 then return "USUNIETO (kontenera nie było)" end
	CH:SetWaypoint("DzwiekGra: przed usunięciem")
	for _, d in stare do d:Destroy() end
	CH:SetWaypoint("DzwiekGra: usunięto")
	return "USUNIETO"
end
CH:SetWaypoint("DzwiekGra: przed budową")
for _, d in stare do d:Destroy() end
local f = Instance.new("Folder")
f.Name = nazwa
f:SetAttribute("Wygenerowane", true)
f:SetAttribute("Zrodlo", "__ZRODLO__")
f:SetAttribute("Zbudowano", "__CZAS__")
f:SetAttribute("Skrot", "__SKROT__")
for _, n in { __FOLDERY__ } do
	local d = Instance.new("Folder")
	d.Name = n
	d.Parent = f
end
f.Parent = workspace
return "OK"
'''

INNE_KOD = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then return "STOP: brak kontenera" end
for _, n in { __FOLDERY__ } do
	if not f:FindFirstChild(n) then
		local d = Instance.new("Folder")
		d.Name = n
		d.Parent = f
	end
end
local nowe = 0
for _, w in { __INNE__ } do
	local s = string.split(w[2], "/")
	local rodzic = f:FindFirstChild(s[1])
	local stary = rodzic:FindFirstChild(s[2])
	if not stary or stary.ClassName ~= w[1] then
		if stary then stary:Destroy() end
		local o = Instance.new(w[1])
		o.Name = s[2]
		o.Parent = rodzic
		nowe += 1
	end
end
f:SetAttribute("Skrot", "__SKROT__")
return "OK (" .. nowe .. " nowych)"
'''

SKRYPT = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then return "STOP: brak kontenera" end
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

KONIEC = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f then return "STOP: brak kontenera" end
local razem, skrypty = 0, 0
for _, d in f:GetDescendants() do
	razem += 1
	if d:IsA("LuaSourceContainer") then skrypty += 1 end
end
game:GetService("ChangeHistoryService"):SetWaypoint("DzwiekGra: zbudowano")
return "instancji: " .. razem .. ", skryptów: " .. skrypty .. ", Skrot = " .. tostring(f:GetAttribute("Skrot"))
'''


# --------------------------------------------------------------------------- dane
def wczytaj_json(sciezka):
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def wczytaj(sciezka):
    with open(sciezka, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def luau(v, wciecie=1):
    """Wartość Pythona jako literał Luau (słowniki z kluczami-identyfikatorami, listy, liczby, napisy)."""
    tab = "\t" * wciecie
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(round(v, 4)) if isinstance(v, float) else str(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        if all(not isinstance(x, (dict, list)) for x in v):
            return "{ " + ", ".join(luau(x) for x in v) + " }"
        return "{\n" + "".join(tab + luau(x, wciecie + 1) + ",\n" for x in v) + "\t" * (wciecie - 1) + "}"
    if isinstance(v, dict):
        wiersze = []
        for k in sorted(v) if not isinstance(v, KolejnySlownik) else v:
            klucz = k if k.isidentifier() else "[%s]" % json.dumps(k, ensure_ascii=False)
            wiersze.append("%s%s = %s,\n" % (tab, klucz, luau(v[k], wciecie + 1)))
        return "{\n" + "".join(wiersze) + "\t" * (wciecie - 1) + "}"
    raise TypeError("nieobsługiwany typ %r" % type(v))


class KolejnySlownik(dict):
    """Słownik wypisywany w kolejności wstawiania (nagłówek katalogu czyta się lepiej)."""


def prostokat_mapy(sciezka):
    """Prostokąt (x1, x2, z1, z2) gruntu mapy z czesci.json (największa bryła o nazwie Grunt / Płyta) — mapa bez obrotu."""
    d = wczytaj_json(os.path.join(REPO, sciezka))
    najlepsza = None
    for c in d["czesci"]:
        if len(c) > 14 and c[14] in ("Grunt", "Płyta"):
            pole = c[8] * c[10]
            if najlepsza is None or pole > najlepsza[0]:
                najlepsza = (pole, c)
    if not najlepsza:
        raise SystemExit("BŁĄD: %s — nie znalazłem bryły Grunt / Płyta (granice strefy muzyki)" % sciezka)
    c = najlepsza[1]
    x, z, sx, sz = c[2], c[4], c[8], c[10]
    return [round(x - sx / 2, 2), round(x + sx / 2, 2), round(z - sz / 2, 2), round(z + sz / 2, 2)]


def katalog(ustawienia, ident):
    """Dane katalogu (słownik) z mapy arkusza, ustawień i identyfikatorów. Sprawdza spójność (SystemExit przy błędzie)."""
    mapa_sciezka = ustawienia["arkusz"]["mapa"]
    mapa = wczytaj_json(os.path.join(REPO, mapa_sciezka))
    efekty = KolejnySlownik()
    for nazwa in sorted(mapa["efekty"]):
        e = mapa["efekty"][nazwa]
        if not (0 <= e["poczatek"] < e["koniec"] <= mapa["dlugosc_s"] + 1e-6):
            raise SystemExit("BŁĄD: %s — odcinek %s poza plikiem" % (mapa_sciezka, nazwa))
        if not (0 <= e["atak"] <= e["szczyt"] <= e["koniec"] - e["poczatek"] + 1e-6):
            raise SystemExit("BŁĄD: %s — %s: atak / szczyt poza odcinkiem" % (mapa_sciezka, nazwa))
        g = ustawienia["glosnosci"].get(nazwa, 1.0)
        efekty[nazwa] = KolejnySlownik(poczatek=e["poczatek"], koniec=e["koniec"], atak=e["atak"], szczyt=e["szczyt"],
                                        glosnosc=float(g))
    for nazwa in ustawienia["glosnosci"]:
        if nazwa not in efekty:
            raise SystemExit("BŁĄD: ustawienia.json — głośność dla nieznanego efektu %s" % nazwa)
    zdarzenia = KolejnySlownik()
    for z, w in sorted(ustawienia["zdarzenia"].items()):
        if w["efekt"] not in efekty:
            raise SystemExit("BŁĄD: ustawienia.json — zdarzenie %s gra nieznany efekt %s" % (z, w["efekt"]))
        zdarzenia[z] = KolejnySlownik(efekt=w["efekt"], uderzenie=bool(w.get("uderzenie")))
    for aktor, z in ustawienia["glosy_potworow"].items():
        if z not in zdarzenia:
            raise SystemExit("BŁĄD: ustawienia.json — odgłos %s: nieznane zdarzenie %s" % (aktor, z))
    arkusz_id = int(ident.get("arkusz") or 0)
    m = ustawienia["muzyka"]
    arkusze, mapy_muzyki = arkusze_muzyki(m, ident)
    uzyte = set()

    def utwory_z(lista, gdzie):
        """Nazwy utworów → wpisy katalogu: osobny plik { nazwa, id } albo odcinek arkusza muzyki
        { nazwa, id (arkusza), arkusz, poczatek, koniec }."""
        wynik = []
        for u in lista:
            if not os.path.isfile(os.path.join(MUZYKA_PLIKI, u + ".ogg")):
                raise SystemExit("BŁĄD: ustawienia.json — %s: nie ma pliku assets/audio/muzyka/%s.ogg" % (gdzie, u))
            uzyte.add(u)
            if u in ident["muzyka"]:
                wynik.append(KolejnySlownik(nazwa=u, id=int(ident["muzyka"][u] or 0)))
                continue
            ark = next((a for a, mp in mapy_muzyki.items() if u in mp["utwory"]), None)
            if ark is None:
                raise SystemExit("BŁĄD: %s — utwór %s nie ma pozycji w identyfikatory.json (osobny plik) ani w żadnym "
                                 "arkuszu muzyki" % (gdzie, u))
            e = mapy_muzyki[ark]["utwory"][u]
            wynik.append(KolejnySlownik(nazwa=u, id=arkusze[ark]["id"], arkusz=ark, poczatek=e["graj_od"], koniec=e["graj_do"]))
        return wynik

    strefy = KolejnySlownik()
    for nazwa, s in m["strefy"].items():
        utwory = utwory_z(s["utwory"], "strefa %s" % nazwa)
        wpis = KolejnySlownik(glosnosc=float(s["glosnosc"]), podpiete=bool(s.get("podpiete", True)), utwory=utwory)
        if s.get("zastepcze"):
            # utwory zastępcze: grają, dopóki żaden własny utwór strefy nie ma identyfikatora (żeby nie zapadła cisza)
            z = s["zastepcze"]
            wpis["zastepcze"] = KolejnySlownik(glosnosc=float(z["glosnosc"]),
                                               utwory=utwory_z(z["utwory"], "strefa %s (zastępcze)" % nazwa))
        if s.get("kontener"):
            wpis["kontener"] = s["kontener"]
        wpis["prostokaty"] = [prostokat_mapy(p) for p in s.get("mapy", [])]
        # prostokąty podane wprost (x1, x2, z1, z2) — dla miejsc bez mapy w czesci.json albo o nieprostokątnym gruncie
        for r in s.get("prostokaty", []):
            if (not isinstance(r, list) or len(r) != 4 or not all(isinstance(v, (int, float)) for v in r)
                    or r[0] >= r[1] or r[2] >= r[3]):
                raise SystemExit("BŁĄD: ustawienia.json — strefa %s: prostokąt %r ma być [x1, x2, z1, z2] z x1 < x2 i z1 < z2" % (nazwa, r))
            wpis["prostokaty"].append([float(v) for v in r])
        strefy[nazwa] = wpis
    konteksty = KolejnySlownik()
    for nazwa, s in (m.get("konteksty") or {}).items():
        if nazwa not in KONTEKSTY:
            raise SystemExit("BŁĄD: ustawienia.json — nieznany kontekst muzyki %s (znane: %s)" % (nazwa, ", ".join(KONTEKSTY)))
        wpis = KolejnySlownik(glosnosc=float(s["glosnosc"]), utwory=utwory_z(s["utwory"], "kontekst %s" % nazwa))
        if nazwa == "walka_straznik":
            gatunki = s.get("gatunki")
            if not isinstance(gatunki, list) or not gatunki or not all(isinstance(g, str) and g for g in gatunki):
                raise SystemExit("BŁĄD: ustawienia.json — kontekst walka_straznik: gatunki mają być niepustą listą nazw")
            wpis["gatunki"] = list(gatunki)
        if nazwa == "trening":
            atr = s.get("atrybut_gracza")
            if not isinstance(atr, str) or not atr:
                raise SystemExit("BŁĄD: ustawienia.json — kontekst trening: brak atrybut_gracza")
            wpis["atrybutGracza"] = atr
        konteksty[nazwa] = wpis
    for u in ident["muzyka"]:
        if u not in uzyte:
            raise SystemExit("BŁĄD: identyfikatory.json — %s nie należy do żadnej strefy ani kontekstu" % u)
    with open(os.path.join(REPO, mapa_sciezka.replace(".json", ".ogg").replace("sfx_arkusz_a.ogg", mapa["plik"])), "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    if sha != mapa.get("sha256"):
        raise SystemExit("BŁĄD: plik arkusza %s ma inny skrót niż w mapie (%s…) — mapa nieaktualna" % (mapa["plik"], sha[:12]))
    k = KolejnySlownik()
    k["wersja"] = 1
    k["arkusz"] = KolejnySlownik(id=arkusz_id, plik=mapa["plik"], wariant=mapa.get("wariant", ""), sha256=mapa["sha256"],
                                 dlugosc=mapa["dlugosc_s"], glosnosc=float(ustawienia["arkusz"]["glosnosc"]),
                                 naraz=int(ustawienia["arkusz"]["naraz"]))
    k["efekty"] = efekty
    k["zdarzenia"] = zdarzenia
    k["glosyPotworow"] = KolejnySlownik(sorted(ustawienia["glosy_potworow"].items()))
    k["muzyka"] = KolejnySlownik(przejscie=float(m["przejscie_s"]), przyciszenieWalki=float(m["przyciszenie_walki"]),
                                 przyciszenieCzas=float(m["przyciszenie_s"]), arkusze=arkusze, konteksty=konteksty,
                                 strefy=strefy)
    return k


def arkusze_muzyki(m, ident):
    """Arkusze muzyki z ustawień → (wpisy katalogu { nazwa: id, plik, sha256, dlugosc }, mapy { nazwa: mapa z pliku }).
    Sprawdza: plik arkusza = mapa (sha256), odcinki w pliku i bez nakładania, pozycja w identyfikatory.json."""
    wpisy, mapy = KolejnySlownik(), {}
    znane = ident.get("arkusze_muzyki") or {}
    for nazwa, a in (m.get("arkusze") or {}).items():
        mapa = wczytaj_json(os.path.join(REPO, a["mapa"]))
        if nazwa not in znane:
            raise SystemExit("BŁĄD: identyfikatory.json — brak pozycji arkusze_muzyki.%s" % nazwa)
        plik = os.path.join(os.path.dirname(os.path.join(REPO, a["mapa"])), mapa["plik"])
        with open(plik, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        if sha != mapa.get("sha256"):
            raise SystemExit("BŁĄD: plik arkusza muzyki %s ma inny skrót niż w mapie (%s…) — mapa nieaktualna" % (mapa["plik"], sha[:12]))
        if set(mapa["kolejnosc"]) != set(mapa["utwory"]):
            raise SystemExit("BŁĄD: %s — kolejnosc i utwory nie zgadzają się" % a["mapa"])
        poprzedni = 0.0
        for u in mapa["kolejnosc"]:
            e = mapa["utwory"][u]
            if not (poprzedni <= e["poczatek"] < e["graj_od"] < e["graj_do"] < e["koniec"] <= mapa["dlugosc_s"] + 1e-6):
                raise SystemExit("BŁĄD: %s — odcinek %s poza plikiem albo nachodzi na poprzedni" % (a["mapa"], u))
            poprzedni = e["koniec"]
        mapy[nazwa] = mapa
        wpisy[nazwa] = KolejnySlownik(id=int(znane[nazwa] or 0), plik=mapa["plik"], sha256=mapa["sha256"],
                                      dlugosc=mapa["dlugosc_s"])
    for nazwa in znane:
        if nazwa not in wpisy:
            raise SystemExit("BŁĄD: identyfikatory.json — arkusza muzyki %s nie ma w ustawienia.json (muzyka.arkusze)" % nazwa)
    return wpisy, mapy


def zrodlo_katalogu(k):
    tresc = luau(k)
    skrot = hashlib.sha256(tresc.encode("utf-8")).hexdigest()[:12]
    return ("--[[\n\tKatalogDzwiekow — WYGENEROWANY przez swiat/dzwiek_gra/zbuduj.py z assets/audio/arkusz/sfx_arkusz_a.json\n"
            "\t(odcinki arkusza efektów), map arkuszy muzyki (assets/audio/arkusz/muzyka_arkusz_*.json), ustawienia.json\n"
            "\t(głośności, zdarzenia, muzyka stref i kontekstów) i identyfikatory.json.\n"
            "\tNIE EDYTUJ RĘCZNIE: zmień pliki źródłowe i uruchom python -B swiat/dzwiek_gra/zbuduj.py --sucho.\n\n"
            "\tCzytają go: OdtwarzaczWalki2 (prototyp walki: odcinki arkusza zamiast wbudowanych dźwięków, gdy arkusz.id ≠ 0)\n"
            "\ti MuzykaStref (muzyka stref i kontekstów). Identyfikator 0 = plik jeszcze nie wgrany (cisza, utwory zastępcze\n"
            "\talbo dźwięki wbudowane). Czasy efektów: poczatek / koniec = sekundy w pliku arkusza, atak / szczyt = sekundy\n"
            "\tod początku odcinka. Utwór muzyki z polami arkusz / poczatek / koniec to odcinek pliku arkusza muzyki\n"
            "\t(sekundy w pliku, już zwężone o margines); bez nich — osobny plik grany w całości.\n]]\n"
            + STRAZNIK_MODULU + "\nreturn " + tresc.replace("\twersja = 1,\n", '\twersja = 1,\n\tskrot = "%s",\n' % skrot, 1) + "\n"), skrot


def wpisz_identyfikatory(sciezka, ident):
    """Scala identyfikatory z pliku (dwie postaci, opis w nagłówku) do ident; zwraca listę zmian."""
    d = wczytaj_json(sciezka)
    nowe = {}
    arkusze = ident.setdefault("arkusze_muzyki", {})
    if "wgrane" in d:
        for w in d["wgrane"]:
            plik, aid = os.path.basename(str(w.get("plik", ""))), w.get("assetId")
            if not aid:
                continue
            nazwa, roz = os.path.splitext(plik)
            if nazwa.startswith("sfx_arkusz"):
                nowe["arkusz"] = aid
            elif nazwa in arkusze:
                nowe["arkusze_muzyki." + nazwa] = aid
            elif nazwa in ident["muzyka"]:
                nowe[nazwa] = aid
    else:
        if "arkusz" in d:
            nowe["arkusz"] = d["arkusz"]
        for n, v in (d.get("arkusze_muzyki") or {}).items():
            nowe["arkusze_muzyki." + n] = v
        for n, v in (d.get("muzyka") or {}).items():
            nowe[n] = v
    if not nowe:
        raise SystemExit("BŁĄD: %s — nie ma w nim żadnego identyfikatora arkusza ani muzyki" % sciezka)
    zmiany = []
    for n, v in nowe.items():
        try:
            liczba = int(str(v).strip())
        except ValueError:
            raise SystemExit("BŁĄD: %s — %s: %r to nie liczba" % (sciezka, n, v))
        if liczba <= 0:
            raise SystemExit("BŁĄD: %s — %s: identyfikator musi być > 0 (jest %d)" % (sciezka, n, liczba))
        if n == "arkusz":
            if ident["arkusz"] != liczba:
                zmiany.append("arkusz: %s → %d" % (ident["arkusz"], liczba))
            ident["arkusz"] = liczba
        elif n.startswith("arkusze_muzyki.") and n.split(".", 1)[1] in arkusze:
            a = n.split(".", 1)[1]
            if arkusze[a] != liczba:
                zmiany.append("arkusz muzyki %s: %s → %d" % (a, arkusze[a], liczba))
            arkusze[a] = liczba
        elif n in ident["muzyka"]:
            if ident["muzyka"][n] != liczba:
                zmiany.append("%s: %s → %d" % (n, ident["muzyka"][n], liczba))
            ident["muzyka"][n] = liczba
        else:
            raise SystemExit("BŁĄD: %s — nieznana pozycja %s (znane: arkusz, %s, %s)" % (
                sciezka, n, ", ".join("arkusze_muzyki." + a for a in arkusze), ", ".join(ident["muzyka"])))
    return zmiany


def zrodla_pakietu(tekst_katalogu):
    zrodla = [("Moduly/KatalogDzwiekow", "ModuleScript", None, tekst_katalogu, "zrodla/KatalogDzwiekow.luau"),
              ("MuzykaStref", "Script", "Client", wczytaj(MUZYKA), "zrodla/MuzykaStref.client.luau")]
    for sciezka, klasa, kontekst, tekst, plik in zrodla:
        if not SL.pierwsza_instrukcja(tekst).startswith(STRAZNIK):
            sys.exit("BŁĄD: %s (%s) nie zaczyna się od strażnika „%s”" % (sciezka, plik, STRAZNIK))
        if len(tekst) > LIMIT_ZRODLA:
            sys.exit("BŁĄD: %s ma %d znaków (limit Source 200 000)" % (sciezka, len(tekst)))
    return zrodla


def dlugi_napis(tekst):
    poziom = 3
    while ("]" + "=" * poziom + "]") in tekst or ("[" + "=" * poziom + "[") in tekst:
        poziom += 1
    return "[" + "=" * poziom + "[\n" + tekst + "]" + "=" * poziom + "]"


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje kontener Workspace/DzwiekGra w Roblox Studio")
    ap.add_argument("--sucho", action="store_true", help="bez Studio: odśwież katalog, sprawdź źródła, pokaż plan")
    ap.add_argument("--skrypty", action="store_true", help="tylko moduł katalogu, skrypt muzyki i haczyk")
    ap.add_argument("--usun", action="store_true", help="usuń Workspace/DzwiekGra")
    ap.add_argument("--identyfikatory", default=None, help="plik JSON z identyfikatorami po wgraniu (opis w nagłówku)")
    ap.add_argument("--studio", default=None, help="studio_id (wymagane, gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()

    ust = wczytaj_json(USTAWIENIA)
    ident = wczytaj_json(IDENTYFIKATORY)
    if a.identyfikatory:
        zmiany = wpisz_identyfikatory(a.identyfikatory, ident)
        katalog(ust, ident)  # najpierw kontrola, potem zapis
        with open(IDENTYFIKATORY, "w", encoding="utf-8", newline="\n") as f:
            json.dump(ident, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("identyfikatory.json: %s" % ("; ".join(zmiany) if zmiany else "bez zmian"))
        a.skrypty = a.skrypty or not a.sucho
    k = katalog(ust, ident)
    tekst, skrot = zrodlo_katalogu(k)
    stary = wczytaj(KATALOG) if os.path.isfile(KATALOG) else ""
    if stary != tekst:
        os.makedirs(os.path.dirname(KATALOG), exist_ok=True)
        with open(KATALOG, "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst)
        print("zrodla/KatalogDzwiekow.luau: odświeżony (skrót %s)" % skrot)
    else:
        print("zrodla/KatalogDzwiekow.luau: aktualny (skrót %s)" % skrot)
    zrodla = zrodla_pakietu(tekst)
    bledy = SL.sprawdz_pliki([KATALOG, MUZYKA])
    print("sprawdz_luau.py: 2 pliki, %s" % ("OK" if not bledy else "BŁĘDY: %d" % len(bledy)))
    if bledy:
        for b in bledy:
            print("  " + b)
        sys.exit("BŁĄD: sprawdz_luau.py zgłosił błędy")
    print("Kontener: Workspace/%s · arkusz %s: id %d, %d efektów, %d zdarzeń · muzyka: %s" % (
        KONTENER, k["arkusz"]["plik"], k["arkusz"]["id"], len(k["efekty"]), len(k["zdarzenia"]),
        ", ".join("%s %d/%d z id%s" % (n, sum(1 for u in s["utwory"] if u["id"]), len(s["utwory"]),
                                        "" if s["podpiete"] else " (niepodpięte)") for n, s in k["muzyka"]["strefy"].items())))
    for n, ark in k["muzyka"]["arkusze"].items():
        z_arkusza = sorted({u["nazwa"] for zr in list(k["muzyka"]["strefy"].values()) + list(k["muzyka"]["konteksty"].values())
                            for u in zr["utwory"] if u.get("arkusz") == n})
        print("  arkusz muzyki %s: id %d, %.1f s, utwory: %s" % (n, ark["id"], ark["dlugosc"], ", ".join(z_arkusza)))
    for n, s in k["muzyka"]["konteksty"].items():
        print("  kontekst %-15s %d/%d utworów z id (%s)" % (n, sum(1 for u in s["utwory"] if u["id"]), len(s["utwory"]),
                                                         ", ".join(u["nazwa"] for u in s["utwory"])))
    for n, s in k["muzyka"]["strefy"].items():
        if s.get("zastepcze"):
            wlasne = sum(1 for u in s["utwory"] if u["id"])
            print("  strefa %-8s własne utwory z id: %d/%d → gra %s" % (
                n, wlasne, len(s["utwory"]),
                "własne" if wlasne else "zastępcze (%s)" % ", ".join(u["nazwa"] for u in s["zastepcze"]["utwory"])))
    for n, s in k["muzyka"]["strefy"].items():
        if s["prostokaty"]:
            print("  strefa %-6s prostokąty %s (z map, tylko odczyt), kontener mapy %s" % (n, s["prostokaty"], s.get("kontener")))
    for sciezka, klasa, kontekst, tekst_, plik in zrodla:
        print("  %-36s → %s %s%s (%d znaków)" % (plik, klasa, sciezka, " [RunContext=%s]" % kontekst if kontekst else "", len(tekst_)))
    for klasa, sciezka in INNE:
        print("  %-36s → %s %s" % ("(nowa instancja)", klasa, sciezka))
    if a.sucho:
        print("sucho: OK (Studio nieużywane)")
        return

    for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
        if _s not in sys.path:
            sys.path.insert(0, _s)
    from cel_studio import MIEJSCE, wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    try:
        with StudioMCP() as s:
            sid = wybierz_studio(s, a.studio)
            stan = s.call("get_studio_state", {"studio_id": sid})["text"]
            if "Current Studio Mode: Edit" not in stan:
                sys.exit("Studio nie jest w trybie Edit — zatrzymaj Play i spróbuj ponownie.\n" + stan)

            def wykonaj(kod):
                kod = NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", str(MIEJSCE)) + kod
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
                if r["is_error"]:
                    raise StudioError(r["text"][:3000])
                w = r["text"].strip()
                if w.startswith("STOP"):
                    print(w)
                    sys.exit(2)
                return w

            def wyslij(sciezka, klasa, kontekst, tekst_):
                kod = (SKRYPT.replace("__KONTENER__", KONTENER).replace("__SCIEZKA__", sciezka).replace("__KLASA__", klasa)
                       .replace("__RUNCONTEXT__", "s.RunContext = Enum.RunContext.%s" % kontekst if kontekst else ""))
                return wykonaj(kod.replace("__ZRODLO__", dlugi_napis(tekst_)))

            t0 = time.time()
            foldery = ", ".join(json.dumps(x) for x in FOLDERY)
            inne = INNE_KOD.replace("__KONTENER__", KONTENER).replace("__SKROT__", skrot).replace("__FOLDERY__", foldery) \
                .replace("__INNE__", ", ".join("{%s, %s}" % (json.dumps(k_), json.dumps(p)) for k_, p in INNE))
            if a.skrypty and not a.usun:
                wykonaj('local f = workspace:FindFirstChild("%s") if not f or f:GetAttribute("Wygenerowane") ~= true '
                        'then return "STOP: brak kontenera — zbuduj całość" end '
                        'game:GetService("ChangeHistoryService"):SetWaypoint("DzwiekGra: przed wymianą skryptów") return "OK"'
                        % KONTENER)
            else:
                w = wykonaj(START.replace("__KONTENER__", KONTENER).replace("__USUN__", "true" if a.usun else "false")
                            .replace("__ZRODLO__", ZRODLO).replace("__SKROT__", skrot).replace("__FOLDERY__", foldery)
                            .replace("__CZAS__", time.strftime("%Y-%m-%dT%H:%M:%S")))
                print("start:", w)
                if a.usun or not w.endswith("OK"):
                    return
            print("  haczyki:", wykonaj(inne))
            for sciezka, klasa, kontekst, tekst_, plik in zrodla:
                print("  skrypt:", wyslij(sciezka, klasa, kontekst, tekst_))
            print("gotowe: %s (%.0f s)" % (wykonaj(KONIEC.replace("__KONTENER__", KONTENER)), time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
