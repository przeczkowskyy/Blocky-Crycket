#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy Pet Arena bez Studio (D-118, etap 1).

    python -B swiat/pet_arena/testy/test_pet_arena.py           # wszystkie testy
    python -B swiat/pet_arena/testy/test_pet_arena.py --tabela  # dodatkowo tabela tempa (symulacja walki)

1. dane: generator aktualny i powtarzalny; 12 petów, różne umiejętności (co najmniej 6 typów, w tym fala, szarża,
   ogłuszenie, zamrożenie, skorupa, skok); kamera: cała arena w pasie ekranu na telefonie, komputerze i tablecie
2. logika (zrodla/LogikaPetArena.luau w interpreterze tools/walka/luau_mini.py): odrzut a życie i waga, krawędź (RING
   OUT) i KO z zaliczeniem wybicia, strefy złota, nagroda za głowę, limit areny i cel rzutu, odpoczynek, wiadro tempa,
   boty (dopełnianie, losowanie, decyzja), każda umiejętność, symulacja walki dzikich petów (liczby skończone, wybicia)
3. źródła: kontrola Luau (swiat/las_potwory/sprawdz_luau.py), strażnik Studio, wersja --publikacja bez strażnika,
   sieć (od klienta tylko Akcja: rzut / umiejętność / wybór; serwer sprawdza typy, tempo, limit, cel), zapis prób
4. zbuduj.py --sucho
"""
import json
import math
import os
import subprocess
import sys
import unittest

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
ZR = os.path.join(PAKIET, "zrodla")
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "tools", "walka")):
    if _s not in sys.path:
        sys.path.append(_s)
if PAKIET in sys.path:
    sys.path.remove(PAKIET)
sys.path.insert(0, PAKIET)
import dane as DN  # noqa: E402
import luau_mini as LM  # noqa: E402
import zapis_prob as ZP  # noqa: E402

U, D, PLIKI = DN.wszystkie_pliki()
TABELA = "--tabela" in sys.argv
if TABELA:
    sys.argv.remove("--tabela")


def czytaj(nazwa):
    with open(os.path.join(ZR, nazwa), encoding="utf-8") as f:
        return f.read()


def interpreter():
    it = LM.Interpreter()
    rs = LM.Tabela()
    rs.set("IsStudio", lambda _s: True)
    game = LM.Tabela()
    game.set("GetService", lambda _s, _n: rs)
    it.globalne.z["game"] = game
    m = it.globalne.z["math"]
    m.set("rad", math.radians)
    m.set("cos", math.cos)
    m.set("sin", math.sin)
    m.set("atan2", lambda y, x: math.atan2(y, x))
    m.set("pi", math.pi)
    m.set("clamp", lambda x, a, b: min(max(x, a), b))
    tb = it.globalne.z["table"]

    def klon(t):
        n = LM.Tabela()
        n.d = dict(t.d)
        return n
    tb.set("clone", klon)
    return it


IT = interpreter()
L = IT.wykonaj(czytaj("LogikaPetArena.luau"), "LogikaPetArena")[0]
DL = IT.wykonaj(PLIKI[DN.PLIK_DANYCH], "DanePetArena")[0]


class Los:
    """Powtarzalny los 0–1 (LCG) albo stała wartość."""

    def __init__(self, ziarno=1, stala=None):
        self.s = ziarno
        self.stala = stala

    def __call__(self, *_a):
        if self.stala is not None:
            return float(self.stala)
        self.s = (self.s * 1103515245 + 12345) % 2147483648
        return self.s / 2147483648.0


def wolaj(nazwa, *argi):
    a = [LM.do_luau(x) if isinstance(x, (dict, list)) else (float(x) if isinstance(x, (int, float)) and not isinstance(x, bool)
                                                              else x) for x in argi]
    return IT.wywolaj(L.get(nazwa), a)


def jeden(nazwa, *argi):
    return wolaj(nazwa, *argi)[0]


def z(t):
    return LM.z_luau(t)


def nr_peta(pid):
    return [p["id"] for p in D["pety"]].index(pid) + 1


def stan(los=None):
    return jeden("nowyStan", DL, los or Los(7))


def dodaj(S, pid, x, zz, wl=1, dziki=False, wyladuj=True):
    p = jeden("dodajPeta", S, nr_peta(pid), wl, dziki, x, 12, zz + 30, x, zz)
    if wyladuj:
        p.set("faza", "walka")
        p.set("cd", 99.0)
    return p


def krok(S, ile=1, dt=None):
    dt = dt or D["walka"]["krok_s"]
    zd = []
    for _ in range(ile):
        zd += z(jeden("krok", S, dt)) or []
    return zd


def zdarzenia(S):
    return LM.Tabela()


# ============================================================================================== 1. dane
class TestDanych(unittest.TestCase):
    def test_1a_aktualne_i_powtarzalne(self):
        self.assertEqual(DN.nieaktualne(PLIKI), [], "uruchom python -B swiat/pet_arena/dane.py")
        self.assertEqual(DN.dane(DN.ustawienia())["skrot"], D["skrot"])
        self.assertTrue(PLIKI[DN.PLIK_DANYCH].split("]]\n", 1)[1].startswith(DN.STRAZNIK))

    def test_1b_pety_i_umiejetnosci(self):
        self.assertEqual(len(D["pety"]), 12)
        typy = {p["umiejetnosc"]["typ"] for p in D["pety"]}
        self.assertGreaterEqual(len(typy), 6)
        for t in ("fala", "szarza", "ogluszenie", "zamrozenie", "skorupa", "skok"):
            self.assertIn(t, typy)
        nazwy = [p["umiejetnosc"]["nazwa"] for p in D["pety"]]
        self.assertEqual(len(nazwy), len(set(nazwy)), "każdy pet z inną umiejętnością")
        for pid in U["gracz"]["pety_startowe"]:
            self.assertIn(pid, [p["id"] for p in D["pety"]])
        # cięższy: więcej życia, wolniejszy; wyższy stopień: więcej życia
        lek = next(p for p in D["pety"] if p["id"] == "lesny_slime")
        ciez = next(p for p in D["pety"] if p["id"] == "mchowy_slimak")
        self.assertGreater(ciez["zycie"], lek["zycie"])
        self.assertLess(ciez["predkosc"], lek["predkosc"])

    def test_1c_scena_zwarta(self):
        c = DN.scena(U)
        self.assertLess(len(c), 2000)
        nazwy = {x[15] for x in c}
        for n in ("Platforma", "Srodek", "Pierscien2", "Pierscien1", "Woda", "Gejzer1", "Trawa", "Bariera", "Cokol", "Mata1", "Mata8"):
            self.assertIn(n, nazwy)

    def test_1d_kamera_cala_arena_w_kadrze(self):
        K = U["kamera"]
        pas = K["pas_ekranu"]
        R = U["scena"]["arena_r"]
        for szer, wys in ((667, 375), (1920, 1080), (1024, 768), (2041, 1095)):
            for s in D["sloty"]:
                kam, cel = DN.kamera_dla(U, s["katKamery"])
                for i in range(48):
                    a = 2 * math.pi * i / 48
                    x, y = DN.rzut_punktu(kam, cel, (math.sin(a) * R, 0, math.cos(a) * R), K["fov"], szer / wys)
                    xmin, xmax = (0.15, 0.85) if szer / wys > 1.5 else (0.03, 0.97)
                    self.assertTrue(pas[0] <= y <= pas[1] and xmin <= x <= xmax,
                                    "arena poza kadrem %dx%d slot %d: (%.2f; %.2f)" % (szer, wys, s["nr"], x, y))

    def test_1e_dzwieki_z_arkusza(self):
        self.assertGreater(D["dzwieki"]["arkusz"], 0)
        for rola in ("cios", "kryt", "plusk", "monety", "klik"):
            e = D["dzwieki"]["efekty"][rola]
            self.assertLess(e["od"], e["koniec"])


# ============================================================================================== 2. logika
class TestLogiki(unittest.TestCase):
    def test_2a_odrzut_rosnie_z_ubytkiem_i_maleje_z_waga(self):
        pelne = jeden("odrzut", DL, 20, 100, 100, 1.0)
        pol = jeden("odrzut", DL, 20, 50, 100, 1.0)
        malo = jeden("odrzut", DL, 20, 10, 100, 1.0)
        self.assertAlmostEqual(pelne, 20)
        self.assertAlmostEqual(pol, 20 * (1 + D["walka"]["wspolczynnik_odrzutu"] * 0.5))
        self.assertTrue(pelne < pol < malo)
        lekki = jeden("odrzut", DL, 20, 100, 100, 0.7)
        ciezki = jeden("odrzut", DL, 20, 100, 100, 1.5)
        self.assertTrue(ciezki < pelne < lekki)
        self.assertGreater(jeden("drogaOdrzutu", DL, malo), 2 * jeden("drogaOdrzutu", DL, pelne))
        # lód (zamrożenie): mniejsze tarcie = dalej
        self.assertGreater(jeden("drogaOdrzutu", DL, pelne, D["walka"]["tarcie"] * D["walka"]["lod_tarcie"]),
                           2 * jeden("drogaOdrzutu", DL, pelne))

    def test_2b_cios_w_ciagu_odrzuca_dalej(self):
        drogi = []
        for hp_frac in (1.0, 0.3):
            S = stan(Los(stala=0.5))                   # bez krytyka, bez rozrzutu
            a = dodaj(S, "lesny_troll", -6, 0)
            b = dodaj(S, "lesny_slime", 6, 0, wl=2)
            a.set("ogl", 99.0)
            b.set("hp", b.get("hpMax") * hp_frac)
            jeden("cios", S, a, b, 0, 20, 1, 0, True, zdarzenia(S))
            x0 = b.get("x")
            maks = 0
            for _ in range(60):
                krok(S, 1)
                p = jeden("petPoId", S, b.get("id"))
                if p is None:
                    maks = 99
                    break
                maks = max(maks, p.get("x") - x0)
            drogi.append(maks)
        self.assertGreater(drogi[1], drogi[0] * 1.8, drogi)

    def test_2c_ring_out_i_ko_z_zaliczeniem(self):
        S = stan(Los(stala=0.5))
        a = dodaj(S, "lesny_troll", 15, 0, wl=1)
        b = dodaj(S, "lesny_slime", 20, 0, wl=2)
        b.set("hp", 10.0)
        jeden("cios", S, a, b, 0, 30, 1, 0, False, zdarzenia(S))
        zd = krok(S, 40)
        ro = [e for e in zd if e["t"] == "ringout"]
        self.assertEqual(len(ro), 1, zd[-3:])
        self.assertEqual(ro[0]["przez"], 1)
        self.assertEqual(ro[0]["premia"], D["zloto"]["premia_wybicia"] * 1)
        self.assertIsNone(jeden("petPoId", S, b.get("id")))
        # KO: życie 0, dziki pet → premia dzikiego × stopień
        c = dodaj(S, "rechotek", 0, 5, wl=0, dziki=True)
        c.set("hp", 3.0)
        jeden("cios", S, a, c, 10, 0.01, 0, 1, False, zdarzenia(S))
        zd = krok(S, 1)
        ko = [e for e in zd if e["t"] == "ko"]
        self.assertEqual(len(ko), 1)
        self.assertEqual(ko[0]["premia"], D["zloto"]["premia_dzikiego"] * 1)
        # wybicie bez ciosu gracza w ciągu ostatni_cios_s — bez premii
        d = dodaj(S, "lesny_slime", 23.9, 0, wl=3)
        d.set("kx", 30.0)
        zd = krok(S, 5)
        self.assertEqual([e["premia"] for e in zd if e["t"] == "ringout"], [0])

    def test_2d_strefy_zlota(self):
        S = stan()
        a = dodaj(S, "lesny_slime", 0, 1, wl=1)        # środek ×5
        b = dodaj(S, "lisciolis", 8, 0, wl=2)          # pierścień ×2, stopień 2
        c = dodaj(S, "rechotek", 0, 20, wl=3)          # pierścień ×1
        e = dodaj(S, "lesny_troll", -20, 0, wl=0, dziki=True)
        w = jeden("zlotoTick", S)
        baza = D["zloto"]["baza"]
        self.assertEqual(w.get(1.0), baza * 5 * 1)
        self.assertEqual(w.get(2.0), baza * 2 * 2)
        self.assertEqual(w.get(3.0), baza * 1 * 1)
        self.assertIsNone(w.get(0.0))
        self.assertEqual(e.get("zl"), 0)
        self.assertEqual(wolaj("strefa", DL, 30), [None, 0])

    def test_2e_nagroda_za_glowe(self):
        S = stan(Los(stala=0.5))
        k = dodaj(S, "mchowy_slimak", 0, 0, wl=0, dziki=True)
        zd = krok(S, int(D["nagroda"]["korona_po_s"] / D["walka"]["krok_s"]) + 2)
        self.assertTrue(any(e["t"] == "krol" and e["id"] == k.get("id") for e in zd))
        krok(S, 40)                                    # 2 s króla
        nagroda = S.get("nagroda")
        self.assertGreater(nagroda, D["nagroda"]["start"] + D["nagroda"]["na_s"] * 1.5)
        a = dodaj(S, "lesny_troll", -4, 0, wl=5)
        k.set("hp", 1.0)
        jeden("cios", S, a, k, 5, 1, 1, 0, False, zdarzenia(S))
        zd = krok(S, 1)
        ko = [e for e in zd if e["t"] == "ko"][0]
        self.assertTrue(ko["krol"])
        self.assertEqual(ko["przez"], 5)
        self.assertGreaterEqual(ko["nagroda"], math.floor(nagroda))
        self.assertIsNone(S.get("krol"))

    def test_2f_limit_areny_i_cel_rzutu(self):
        S = stan()
        self.assertEqual(wolaj("mozeRzucic", S, 0, 0), [True, None])
        self.assertEqual(wolaj("mozeRzucic", S, 30, 0)[1], "poza")
        self.assertEqual(wolaj("mozeRzucic", S, float("nan"), 0)[1], "zle")
        self.assertEqual(wolaj("mozeRzucic", S, "x", 0)[1], "zle")
        for i in range(D["rzut"]["limit_areny"]):
            dodaj(S, "lesny_slime", (i - 4) * 4, 0, wl=i + 1)
        self.assertEqual(wolaj("mozeRzucic", S, 0, 0), [False, "pelna"])
        # rzut: lot, potem lądowanie odpycha sąsiadów
        S = stan(Los(stala=0.5))
        b = dodaj(S, "lesny_slime", 1.5, 0, wl=2)
        p = jeden("dodajPeta", S, 1, 1, False, 0, 12, 35, 0, 0)
        self.assertEqual(p.get("faza"), "lot")
        zd = krok(S, int(p.get("lotCzas") / D["walka"]["krok_s"]) + 2)
        self.assertEqual(p.get("faza"), "walka")
        self.assertTrue(any(e["t"] == "ladowanie" for e in zd))
        self.assertGreater(b.get("x"), 1.5)

    def test_2g_odpoczynek_i_druzyna(self):
        prof = jeden("profilNowy", DL)
        dr = z(jeden("druzyna", DL, prof, None))
        self.assertEqual([w["id"] for w in dr], U["gracz"]["pety_startowe"])
        w = LM.do_luau({"odpoczynek": 0})
        self.assertTrue(jeden("gotowy", w, 100))
        wolaj("odpocznij", DL, w, 100)
        self.assertEqual(D["odpoczynek"], 30)
        self.assertFalse(jeden("gotowy", w, 100 + D["odpoczynek"] - 1))
        self.assertEqual(jeden("zostalo", w, 100.5), D["odpoczynek"])
        self.assertTrue(jeden("gotowy", w, 100 + D["odpoczynek"]))
        # profil v1 (etap 1: lista id) → v2 z gwiazdką 1; nieznane pety pominięte
        p = z(jeden("profil", DL, LM.do_luau({"zloto": 55, "pety": ["lesny_troll", "kot"]})))
        self.assertEqual(p["zloto"], 55)
        self.assertEqual(p["pety"], {"lesny_troll": 1})
        self.assertEqual(p["druzyna"], ["lesny_troll"])
        # drużyna: tylko posiadane, bez powtórzeń, do 3
        prof = jeden("profilNowy", DL)
        self.assertFalse(jeden("ustawDruzyne", DL, prof, LM.do_luau(["lesny_troll"])))
        self.assertFalse(jeden("ustawDruzyne", DL, prof, LM.do_luau(["lesny_slime", "lesny_slime"])))
        self.assertTrue(jeden("ustawDruzyne", DL, prof, LM.do_luau(["zoledziak"])))
        self.assertEqual(z(prof.get("druzyna")), ["zoledziak"])
    def test_2h_wiadro_tempa(self):
        w = LM.do_luau({})
        ok = sum(1 for _ in range(30) if jeden("wiadro", w, 10.0, D["rzut"]["wiadro_na_s"], D["rzut"]["wiadro_zapas"]))
        self.assertEqual(ok, D["rzut"]["wiadro_zapas"])
        self.assertTrue(jeden("wiadro", w, 11.0, D["rzut"]["wiadro_na_s"], D["rzut"]["wiadro_zapas"]))

    def test_2i_boty(self):
        S = stan()
        self.assertEqual(jeden("ileBotowBrakuje", S), D["boty"]["do_ilu"])
        for i in range(3):
            dodaj(S, "lesny_slime", i * 4, 0, wl=i + 1)
        self.assertEqual(jeden("ileBotowBrakuje", S), D["boty"]["do_ilu"] - 3)
        ile = {}
        los = Los(3)
        for _ in range(400):
            n = int(jeden("losujPetaBota", DL, los(), los()))
            s = D["pety"][n - 1]["stopien"]
            ile[s] = ile.get(s, 0) + 1
        self.assertGreater(ile.get(1, 0), ile.get(3, 0))
        self.assertGreater(ile.get(1, 0), 120)
        # decyzja: pełny pasek i wróg obok
        S = stan()
        a = dodaj(S, "lesny_troll", 0, 0, wl=0, dziki=True)
        a.set("pasek", 1.0)
        self.assertFalse(jeden("botChce", S, a, 99))
        dodaj(S, "lesny_slime", 5, 0, wl=1)
        self.assertTrue(jeden("botChce", S, a, 99))

    def _arena(self, pid, wrogowie, los=None):
        S = stan(los or Los(stala=0.5))
        p = dodaj(S, pid, 0, 0, wl=1)
        p.set("pasek", 1.0)
        w = [dodaj(S, "rechotek", x, zz, wl=0, dziki=True) for x, zz in wrogowie]
        zd = LM.Tabela()
        ok = jeden("uzyj", S, p, zd)
        return S, p, w, ok, z(zd) or []

    def test_2j_umiejetnosci(self):
        tarcza = DL.get("tarcza")
        stara = tarcza.get("roznica")
        tarcza.set("roznica", 99.0)                    # tu sprawdzamy same umiejętności (tarcza: test_2l)
        try:
            self._umiejetnosci()
        finally:
            tarcza.set("roznica", stara)

    def _umiejetnosci(self):
        # fala: wszyscy w zasięgu odrzuceni od środka
        S, p, w, ok, zd = self._arena("lesny_troll", [(5, 0), (-5, 0), (0, 15)])
        self.assertTrue(ok)
        self.assertGreater(w[0].get("kx"), 10)
        self.assertLess(w[1].get("kx"), -10)
        self.assertEqual(w[2].get("kx"), 0)
        self.assertEqual(p.get("pasek"), 0)
        self.assertFalse(jeden("uzyj", S, p, LM.Tabela()), "pasek pusty — drugi raz nie")
        # ogłuszenie
        S, p, w, ok, zd = self._arena("muchomornik", [(4, 0), (0, 14)])
        self.assertGreater(w[0].get("ogl"), S.get("czas"))
        self.assertEqual(w[1].get("ogl"), 0)
        # zamrożenie najbliższego
        S, p, w, ok, zd = self._arena("wazeczka", [(6, 0), (9, 3)])
        self.assertGreater(w[0].get("lod"), S.get("czas"))
        self.assertEqual(w[1].get("lod"), 0)
        # skorupa: cios odbity, bez obrażeń
        S, p, w, ok, zd = self._arena("mchowy_slimak", [(4.5, 0)])
        hp = p.get("hp")
        jeden("cios", S, w[0], p, 20, 20, -1, 0, True, LM.Tabela())
        self.assertEqual(p.get("hp"), hp)
        self.assertGreater(w[0].get("kx"), 5)
        # szarża (przebija): przejazd przez dwóch
        S, p, w, ok, zd = self._arena("pancernik_ruin", [(6, 0), (12, 0.5)])
        self.assertEqual(S.get("pety").get(1).get("akcja").get("typ"), "szarza")
        hp0 = [x.get("hp") for x in w]
        krok(S, 30)
        self.assertTrue(all(x.get("hp") < h for x, h in zip(w, hp0)) or len(z(S.get("pety"))) < 3)
        # skok na tłum: ląduje i fala
        S, p, w, ok, zd = self._arena("ropucha_z_chatka", [(10, 0), (12, 2), (-15, 0)])
        zd2 = krok(S, int(D["pety"][nr_peta("ropucha_z_chatka") - 1]["umiejetnosc"]["czas"] / D["walka"]["krok_s"]) + 2)
        lad = [e for e in zd2 if e["t"] == "ladowanie_skoku"]
        self.assertEqual(len(lad), 1)
        self.assertGreaterEqual(lad[0]["trafione"], 2)
        self.assertGreater(p.get("x"), 5)
        # rykoszet: trzy cele po kolei
        S, p, w, ok, zd = self._arena("lesny_slime", [(4, 0), (7, 3), (9, -3), (20, 0)])
        zd2 = krok(S, 20)
        self.assertEqual(len([e for e in zd2 if e["t"] == "odbicie_slime"]), 3)
        # język: wróg przerzucony za plecy
        S, p, w, ok, zd = self._arena("rechotek", [(8, 0)])
        self.assertLess(w[0].get("x"), 0)
        self.assertLess(w[0].get("kx"), 0)
        # podpalenie w stożku
        S, p, w, ok, zd = self._arena("ognik", [(5, 0), (-6, 0)])
        self.assertGreater(w[0].get("pal"), S.get("czas"))
        self.assertEqual(w[1].get("pal"), 0)
        hp = w[0].get("hp")
        krok(S, 20)
        self.assertLess(w[0].get("hp"), hp)
        # szarża bez przebicia (Headbutt): staje na pierwszym
        S, p, w, ok, zd = self._arena("zoledziak", [(5, 0), (8, 0)])
        krok(S, 10)
        self.assertIsNone(p.get("akcja"))
        # Pounce: skok na króla
        S = stan(Los(stala=0.5))
        k = dodaj(S, "mchowy_slimak", 0, 0, wl=0, dziki=True)
        krok(S, 40)
        self.assertEqual(S.get("krol"), k.get("id"))
        wolf = dodaj(S, "cierniowy_wilk", 15, 10, wl=4)
        wolf.set("pasek", 1.0)
        zd = LM.Tabela()
        self.assertTrue(jeden("uzyj", S, wolf, zd))
        u = [e for e in z(zd) if e["t"] == "umiejetnosc"][0]
        self.assertLess(math.hypot(u["x1"], u["z1"]), 4)

    def test_2l_tarcza_slabszego(self):
        S = stan(Los(stala=0.5))
        silny = dodaj(S, "cierniowy_wilk", 0, 0, wl=1)          # stopień 3
        slaby = dodaj(S, "lesny_slime", 4, 0, wl=2)             # stopień 1 → tarcza
        rowny = dodaj(S, "lisciolis", -4, 0, wl=3)              # stopień 2 → bez tarczy
        self.assertTrue(jeden("chroniony", S, slaby))
        self.assertFalse(jeden("chroniony", S, rowny))
        zd = LM.Tabela()
        jeden("cios", S, silny, slaby, 10, 20, 1, 0, False, zd)
        jeden("cios", S, silny, rowny, 10, 20, -1, 0, False, zd)
        e = z(zd)
        self.assertAlmostEqual(e[0]["o"], round(10 * D["tarcza"]["mnoznik"]))
        self.assertEqual(e[1]["o"], 10)
        self.assertLess(e[0]["v"], e[1]["v"])

    def test_2m_boss(self):
        S = stan(Los(stala=0.5))
        a = dodaj(S, "lesny_troll", -8, 0, wl=1)
        b = dodaj(S, "lesny_slime", 8, 0, wl=2)
        boss = jeden("dodajBossa", S, 1, 2)
        self.assertEqual(boss.get("hpMax"), D["boss"]["zycie"] + 2 * D["boss"]["na_gracza"])
        zd = krok(S, int((1.4 + D["boss"]["fala_co_s"]) / D["walka"]["krok_s"]) + 4)
        self.assertTrue(any(e["t"] == "ladowanie" and e["id"] == boss.get("id") for e in zd))
        self.assertTrue(any(e["t"] == "boss_fala" for e in zd), "fala bossa")
        self.assertNotEqual(S.get("krol"), boss.get("id"), "boss nie jest królem")
        for pet_, ile in ((a, 300), (b, 100)):
            jeden("cios", S, pet_, boss, ile, 1, 1, 0, False, LM.Tabela())
        boss.set("hp", 1.0)
        jeden("cios", S, a, boss, 5, 1, 1, 0, False, LM.Tabela())
        zd = krok(S, 1)
        ko = [e for e in zd if e["t"] == "ko" and e.get("boss")]
        self.assertEqual(len(ko), 1)
        n = ko[0]["nagrody"]
        self.assertGreater(n[0] if isinstance(n, list) else n.get(1), D["boss"]["minimum"])
        self.assertEqual(n[1] if isinstance(n, list) else n.get(2), max(D["boss"]["minimum"], round(D["boss"]["pula"] * 100 / 405)))
        # nagrody: minimum dla drobnego udziału
        w = z(jeden("nagrodyBossa", DL, LM.do_luau({1: 1000.0, 2: 1.0})))
        self.assertEqual(w[1] if isinstance(w, list) else w[2], D["boss"]["minimum"])
        # ucieczka po czasie
        S2 = stan(Los(stala=0.5))
        jeden("dodajBossa", S2, 2, 1)
        zd = krok(S2, int((D["boss"]["czas_s"] + 0.5) / D["walka"]["krok_s"]))
        self.assertTrue(any(e["t"] == "boss_uciekl" for e in zd))

    def test_2n_zloty_pet(self):
        S = stan(Los(stala=0.5))
        a = dodaj(S, "lesny_troll", 0, 0, wl=1)
        g = jeden("dodajZlotego", S, 0, 0, 0, 6, 0)
        g.set("faza", "walka")
        x0 = g.get("x")
        krok(S, 10)
        self.assertGreater(g.get("x"), x0 + 1, "ucieka od wroga")
        zd = LM.Tabela()
        jeden("cios", S, a, g, 5, 5, 1, 0, False, zd)
        mon = [e for e in z(zd) if e["t"] == "zloto_cios"]
        self.assertEqual(mon[0]["ile"], D["zloty"]["za_cios"] * 4)
        g.set("hp", 0.0)
        ko = [e for e in krok(S, 1) if e["t"] == "ko"]
        self.assertEqual(ko[0]["premia"], D["zloty"]["premia"])

    def test_2o_jajka_kolekcja_gwiazdki(self):
        los = Los(5)
        ile = {}
        for _ in range(600):
            nr, rz = wolaj("losujZJajka", DL, 1, los(), los())
            ile[int(rz)] = ile.get(int(rz), 0) + 1
            self.assertEqual(D["pety"][int(nr) - 1]["stopien"], rz)
        sz = D["jajka"][0]["szanse"]
        for r in range(1, 6):
            self.assertAlmostEqual(ile.get(r, 0) / 600, sz[r - 1], delta=0.06)
        self.assertNotIn(5, ile, "jajko 1 bez legendarnych")
        self.assertEqual(int(wolaj("losujZJajka", DL, 3, 0.0, 0.0)[1]), 2, "jajko 3 zaczyna od Uncommon")
        prof = jeden("profilNowy", DL)
        w1 = z(jeden("dodajDoKolekcji", DL, prof, "lesny_troll", 1500))
        self.assertTrue(w1["nowy"])
        self.assertIn("lesny_troll", z(prof.get("druzyna")), "wolne miejsce w drużynie — nowy pet trafia do drużyny")
        for g in range(2, D["gwiazdki"]["maks"] + 1):
            self.assertEqual(z(jeden("dodajDoKolekcji", DL, prof, "lesny_troll", 1500))["gwiazdki"], g)
        w = z(jeden("dodajDoKolekcji", DL, prof, "lesny_troll", 1500))
        self.assertTrue(w["maks"])
        self.assertEqual(prof.get("zloto"), round(1500 * D["gwiazdki"]["zwrot_przy_maks"]))
        self.assertTrue(prof.get("ksiega").get("lesny_troll"))
        m = z(jeden("mnoznikPeta", DL, 5, 1))
        self.assertAlmostEqual(m["zycie"], 1 + 4 * D["gwiazdki"]["na_gwiazdke"])

    def test_2p_trener(self):
        self.assertEqual(wolaj("poziom", DL, 0)[0], 1)
        n1 = jeden("potrzeba", DL, 1)
        self.assertEqual(wolaj("poziom", DL, n1)[0], 2)
        self.assertGreater(jeden("potrzeba", DL, 5), jeden("potrzeba", DL, 2))
        m = z(jeden("mnoznikPeta", DL, 1, 11))
        self.assertAlmostEqual(m["sila"], 1 + 10 * D["trener"]["na_poziom"])
        # silniejszy pet (gwiazdki + poziom) zadaje więcej
        S = stan(Los(stala=0.5))
        a = jeden("dodajPeta", S, 1, 1, False, 0, 0, 0, 0, 0, LM.do_luau({"zycie": 1.3, "sila": 1.3, "gwiazdki": 3}))
        a.set("faza", "walka")
        b = dodaj(S, "lesny_slime", 3, 0, wl=2)
        self.assertAlmostEqual(a.get("hpMax"), D["pety"][0]["zycie"] * 1.3)
        zd = LM.Tabela()
        jeden("cios", S, a, b, 10, 10, 1, 0, False, zd)
        self.assertEqual(z(zd)[0]["o"], 13)

    def test_2q_zapis_z_atrapa(self):
        class Atrapa:
            def __init__(self, bledy=0):
                self.bledy, self.dane, self.wolania = bledy, {}, 0

            def tabela(self):
                t = LM.Tabela()

                def get(_s, k):
                    self.wolania += 1
                    if self.bledy > 0:
                        self.bledy -= 1
                        raise LM.BladLuau("DataStore niedostępny")
                    return self.dane.get(k)

                def upd(_s, k, f):
                    if self.bledy > 0:
                        self.bledy -= 1
                        raise LM.BladLuau("DataStore niedostępny")
                    self.dane[k] = IT.wywolaj(f, [self.dane.get(k)])[0]
                t.set("GetAsync", get)
                t.set("UpdateAsync", upd)
                return t
        Z = D["zapis"]
        self.assertEqual(wolaj("magazyn", DL.get("zapis"), True, 200, 100, False), [None, "wyłączony (próba gry)"])
        self.assertEqual(wolaj("magazyn", DL.get("zapis"), True, 200, 100, True)[0], Z["magazyn"] + Z["przyrostek_studio"] + Z["przyrostek_proby"])
        self.assertEqual(wolaj("magazyn", DL.get("zapis"), False, 200, 100, False)[0], Z["magazyn"])
        # bez magazynu: gra w pamięci, zapis wyłączony
        p, ok = wolaj("wczytajProfil", DL, None, "k", None)
        self.assertFalse(ok)
        self.assertFalse(jeden("zapiszProfil", DL, None, "k", p, True))
        # magazyn pada zawsze → nowy profil, zapis wyłączony (nie nadpiszemy prawdziwego postępu)
        a = Atrapa(bledy=99)
        p, ok = wolaj("wczytajProfil", DL, a.tabela(), "k", None)
        self.assertFalse(ok)
        self.assertEqual(a.wolania, Z["proby"])
        # pada raz, potem działa: tam i z powrotem
        a = Atrapa(bledy=1)
        t = a.tabela()
        p, ok = wolaj("wczytajProfil", DL, t, "k", None)
        self.assertTrue(ok)
        p.set("zloto", 1234.0)
        jeden("dodajDoKolekcji", DL, p, "ognik", 250)
        jeden("dodajDoKolekcji", DL, p, "ognik", 250)
        self.assertTrue(jeden("zapiszProfil", DL, t, "k", p, True))
        p2, ok2 = wolaj("wczytajProfil", DL, t, "k", None)
        p2 = z(p2)
        self.assertEqual(p2["zloto"], 1234)
        self.assertEqual(p2["pety"]["ognik"], 2)
        self.assertIn("ognik", p2["druzyna"])
        self.assertTrue(p2["ksiega"]["ognik"])

    def test_2r_tablice_i_wydarzenia(self):
        t = z(jeden("top", LM.do_luau([{"nazwa": "a", "w": 3}, {"nazwa": "b", "w": 9}, {"nazwa": "c", "w": 0}, {"nazwa": "d", "w": 5}]), 2))
        self.assertEqual([x["nazwa"] for x in t], ["b", "d"])
        k = D["wydarzenia"]["kolejnosc"]
        self.assertEqual([jeden("typWydarzenia", DL, n) for n in (1, 2, 3)], [k[0], k[1], k[0]])
        self.assertEqual(sorted(k), ["boss", "zloty"])
    def test_2k_symulacja_walki(self):
        """Pięć dzikich petów przez 60 s gry: liczby skończone, są wybicia; tabela tempa (--tabela)."""
        wynik = symulacja(60, Los(11))
        self.assertGreater(wynik["wybic"], 0)
        self.assertTrue(wynik["skonczone"])
        if TABELA:
            print("\nsymulacja 60 s (boty, 5 naraz):", json.dumps(wynik, ensure_ascii=False))


def symulacja(sekund, los, gracz_pet=None):
    S = stan(los)
    dt = D["walka"]["krok_s"]
    zycia, pierwsze = [], None
    narodziny = {}
    wybic = {"ringout": 0, "ko": 0}
    t = 0.0
    while t < sekund:
        brak = int(jeden("ileBotowBrakuje", S))
        if brak > 0:
            nr = int(jeden("losujPetaBota", DL, los(), los()))
            a = los() * 2 * math.pi
            r = los() * 16
            p = jeden("dodajPeta", S, nr, 0, True, math.sin(a) * 40, 14, math.cos(a) * 40, math.sin(a) * r, math.cos(a) * r)
            narodziny[p.get("id")] = t
        for e in krok(S, 1):
            if e["t"] in wybic:
                wybic[e["t"]] += 1
                zycia.append(t - narodziny.get(e["id"], t))
                if pierwsze is None:
                    pierwsze = t
        for p in z(S.get("pety")) or []:
            pass
        for i in range(1, int(S.get("pety").dlugosc()) + 1):
            p = S.get("pety").get(i)
            if jeden("botChce", S, p, 2.0):
                jeden("uzyj", S, p, LM.Tabela())
        t += dt
    skonczone = all(math.isfinite(S.get("pety").get(i).get("x")) for i in range(1, int(S.get("pety").dlugosc()) + 1))
    return {"wybic": wybic["ringout"] + wybic["ko"], "ringout": wybic["ringout"], "ko": wybic["ko"],
            "sr_zycie_s": round(sum(zycia) / len(zycia), 1) if zycia else None, "pierwsze_s": round(pierwsze, 1) if pierwsze else None,
            "skonczone": skonczone}


# ============================================================================================== 3. źródła
class TestZrodel(unittest.TestCase):
    def test_3a_kontrola_luau(self):
        import zbuduj as ZB
        bledy = ZB.sprawdz_zrodla()
        self.assertEqual(bledy, [])

    def test_3b_straznik_i_publikacja(self):
        import zbuduj as ZB
        for r, n, k, c, t in ZB.zrodla(PLIKI):
            self.assertIn(DN.STRAZNIK, t.split("\n\n", 3)[0] + t[:2000], n)
        for r, n, k, c, t in ZB.zrodla(PLIKI, publikacja=True):
            self.assertNotIn(DN.STRAZNIK, t, n)

    def test_3c_siec(self):
        serwer = czytaj("SerwerPetArena.server.luau")
        klient = czytaj("KlientPetArena.client.luau")
        self.assertEqual(klient.count("FireServer("), klient.count("evAkcja:FireServer("), "od klienta tylko Akcja")
        self.assertIn("OnServerEvent", serwer)
        for slowo in ("L.wiadro", "L.mozeRzucic", "L.petGracza", "L.gotowy", '"rzut"', '"umiejetnosc"', '"wybierz"',
                      "type(rodzaj) ~= \"string\""):
            self.assertIn(slowo, serwer, slowo)
        for slowo in ("L.magazyn", "L.wczytajProfil", "L.zapiszProfil", "BindToClose", "\"jajko\"", "\"druzyna\"", "\"trening\""):
            self.assertIn(slowo, serwer, slowo)

    def test_3d_znacznik_prob(self):
        self.assertIn(U["kontener"], ZP.KONTENERY_DODATKOWE)


class TestBudowy(unittest.TestCase):
    def test_4a_zbuduj_sucho(self):
        r = subprocess.run([sys.executable, "-B", os.path.join(PAKIET, "zbuduj.py"), "--sucho"], capture_output=True, text=True,
                           encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-1500:])


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    unittest.main(verbosity=1)
