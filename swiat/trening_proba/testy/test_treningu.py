# -*- coding: utf-8 -*-
"""Testy offline pakietu swiat/trening_proba (próba Training Center). Bez Studio, bez sieci.

    python -B swiat/trening_proba/testy/test_treningu.py        (unittest; kod 1 przy błędzie)

1. Dane: dane.py deterministyczny i aktualny; bez BOM, dat i ścieżek lokalnych; złe ustawienia → BladDanych (także
   reguły czterech nowych rodzajów gier i zdarzenia arkusza dźwięku); sześć statystyk = System RPG i atrybuty =
   PlayerStatsDefaults, wszystkie grywalne; styk z bazarem; arena daleko od zajętych obszarów świata.
2. Logika (lustro w Pythonie): plan rundy każdej z sześciu gier, przyrosty, seria i waga, trafienie / pudło / zmyłka /
   pusty / dubel, granice czasu klienta, spam (kubełek żetonów), koniec rundy, opóźnienie sieci, balans sześciu gier
   (D-074), wejście i start; osobno Bieżnia (rytm, podbiegi, zła stopa), Kłody (skok / padnij, zmiana wysokości),
   Runy (pokaz, kolejność, kara, bezczynność, dubel, zaklęcie), Koniczyny (tor przy upadku, kamień, złota, stanie
   w miejscu = 0, ruch bez werdyktu), przerwanie rundy, bot spamujący bez zysku w każdej grze.
3. Luau w luau_mini: pliki parsują się; przypadki wzorcowe OK (zepsuty wykryty); losowe wywołania = lustro (wszystkie
   gry); dane w Luau = dane z Pythona; kod wysyłany do Studio parsuje się, bez niewstawionych __…__.
4. Scena: części, rozmiary, obrys, nazwy animowane, stanowiska widoczne z kamery (sześć), tory lotu i obrotu kłody bez
   przeszkód, ściany, miejsce gracza wolne.
5. Telefon: przyciski ≥ 44 px i teksty ≥ 12 pt przy 667 × 375 i przy skali minimalnej; panele i przyciski sześciu
   gier mieszczą się i nie nachodzą na siebie; teksty bez napisów dla twórców.
6. Styki: wiadomości zdalne, nazwy instancji, atrybuty, zakazy (Lighting, zasoby; adres arkusza dźwięku tylko
   z katalogu), dźwięki wbudowane i zdarzenia arkusza, PlaceId, punkty historii, --sucho bez studio_mcp,
   proba_play.py (T01–T22, --sprawdz), podgląd stanowisk, bez ścieżek i nazw kont w plikach pakietu.
"""
import copy
import glob
import importlib.util
import json
import math
import os
import py_compile
import random
import re
import subprocess
import sys
import tempfile
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
sys.dont_write_bytecode = True
sys.path.insert(0, PAKIET)


def _modul(nazwa, plik):
    spec = importlib.util.spec_from_file_location(nazwa, os.path.join(PAKIET, plik))
    m = importlib.util.module_from_spec(spec)
    sys.modules[nazwa] = m
    spec.loader.exec_module(m)
    return m


LT = _modul("logika_treningu", "logika_treningu.py")
DANE = _modul("dane", "dane.py")
SCENA = _modul("scena", "scena.py")
SLT = _modul("sprawdz_luau_treningu", "sprawdz_luau_treningu.py")
ZB = _modul("zbuduj_treningu", "zbuduj.py")

K, D = DANE.dane_z_przypadkami()
ZR = os.path.join(PAKIET, "zrodla")
LM = SLT.luau_mini()


def czytaj(*czesci):
    with open(os.path.join(*czesci), encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


LICZBA_CZESCI = 202  # arena: sześć stanowisk, lobby, mury (zmiana sceny = świadoma zmiana tej liczby)
SERWER = czytaj(ZR, "SerwerTreningu.server.luau")
KLIENT = czytaj(ZR, "KlientTreningu.client.luau")
LOGIKA = czytaj(ZR, "LogikaTreningu.luau")


def bez_komentarzy(tekst):
    return SLT.SL.rozbierz(tekst)[0]


CZASOWE = ("sila", "pancerz", "kondycja", "zrecznosc")
GRY = ("sila", "pancerz", "kondycja", "zrecznosc", "inteligencja", "szczescie")


def runda(gra="sila", z=1, t0=100.0, d=None):
    d = d or D
    return LT.nowa_runda(d, gra, 1, t0, LT.plan(d, gra, z))


def akcja_dla(gra, e):
    G = D["gry"][gra]
    return "blok" if G["typ"] == "blok" else LT.odpowiedz(G, e["wartosc"])


def gracz_runy(R, rnd, t=0.0, blad=0.0, reakcja=0.5, krok=0.4, koniec=None):
    """Model gracza Run: po pokazie reakcja, potem kolejne runy co krok (z prawdopodobieństwem błędu) → R."""
    G = D["gry"][R["gra"]]
    koniec = D["runda"]["dlugosc_s"] if koniec is None else koniec
    while t < koniec and not R["koniec"]:
        r = t - R["t0"]
        if r < R["pokazDo"]:
            t = R["t0"] + R["pokazDo"] + reakcja
            continue
        dobra = R["plan"][R["offset"] + R["poz"]]["wartosc"]
        w = dobra if rnd.random() >= blad else [k for k in G["akcje"] if k != dobra][rnd.randrange(3)]
        LT.zgloszenie(D, R, w, t, t + 0.05)
        t += krok
    return R


def gracz_koniczyn(R, rnd, celnosc=1.0, reakcja=0.45, ruch_s=0.18, krok=0.05, ruchy=None):
    """Model gracza Koniczyn w czasie rzeczywistym (jak autogra klienta): co krok patrzy na najwcześniejszą
    nierozstrzygniętą rzecz w powietrzu (widzianą od reakcja s): pod koniczynę idzie (z prawdopodobieństwem celnosc),
    spod kamienia, który zaraz spadnie na jego tor, schodzi; jeden tor na ruch, nie częściej niż co ruch_s.
    Werdykty od razu przy upadku (zapas 0, jak klient). ruchy — lista (t, tor) do odtworzenia na serwerze → R."""
    G = D["gry"][R["gra"]]
    tor = G["tory"].index(G["start_tor"]) + 1
    t0 = R["t0"]
    t, ostatni = t0, -1e9
    pominiete, zdecydowane = set(), set()
    while t < t0 + D["runda"]["dlugosc_s"] + 1:
        LT.przeterminowane(D, R, t, 0)
        cel = None
        for e in R["plan"]:
            ti = t0 + e["t"]
            if t < ti - G["lot_s"] + reakcja:
                break
            if e["nr"] in R["rozstrzygniete"]:
                continue
            k, _ = LT.tory_zdarzenia(D, R, e)
            if e["wartosc"] == "kamien":
                if k == tor and ti - t < 0.6:
                    cel = 1 if tor != 1 else 2
                    break
                continue
            if e["nr"] not in zdecydowane:
                zdecydowane.add(e["nr"])
                if rnd.random() >= celnosc:
                    pominiete.add(e["nr"])
            if e["nr"] in pominiete:
                continue
            cel = k
            break
        nastepny = tor + (1 if cel is not None and cel > tor else -1)
        kamien_tuz = any(e["wartosc"] == "kamien" and e["nr"] not in R["rozstrzygniete"] and e["nr"] in R["tory"]
                         and R["tory"][e["nr"]][0] == nastepny and 0 <= t0 + e["t"] - t < 0.3 for e in R["plan"])
        if cel is not None and cel != tor and t - ostatni >= ruch_s and not kamien_tuz:
            tor = nastepny
            LT.zgloszenie(D, R, G["tory"][tor - 1], t, t)
            if ruchy is not None:
                ruchy.append((t, G["tory"][tor - 1]))
            ostatni = t
        t += krok
    LT.przeterminowane(D, R, 1e9)
    return R


# ============================================================================================== 1. dane
class TestDanych(unittest.TestCase):
    def test_1a_generator_deterministyczny_i_aktualny(self):
        tresci = []
        with tempfile.TemporaryDirectory() as tmp:
            for nr in (1, 2):
                folder = os.path.join(tmp, str(nr))
                r = subprocess.run([sys.executable, "-B", os.path.join(PAKIET, "dane.py"), "--wyjscie", folder], capture_output=True)
                self.assertEqual(r.returncode, 0, r.stdout.decode("utf-8", "replace"))
                with open(os.path.join(folder, DANE.PLIK_LUAU), "rb") as f:
                    tresci.append(f.read())
        self.assertEqual(tresci[0], tresci[1])
        ok, _ = DANE.aktualny()
        self.assertTrue(ok, "zrodla/DaneTreningu.luau nieaktualny — uruchom dane.py")

    def test_1b_bez_bom_dat_i_sciezek(self):
        for plik in glob.glob(os.path.join(PAKIET, "**", "*.*"), recursive=True):
            if "__pycache__" in plik or not plik.endswith((".py", ".luau", ".json", ".md")):
                continue
            with open(plik, "rb") as f:
                surowe = f.read()
            self.assertFalse(surowe.startswith(b"\xef\xbb\xbf"), plik)
            tekst = surowe.decode("utf-8")
            nazwa = os.path.relpath(plik, REPO)
            for wzor in (r"[A-Za-z]:\\\\?" + "Us" + "ers", "/Us" + "ers/", "App" + "Data", "bib" + "ac",
                         r"[\w.]+@[\w-]+\.[a-z]{2,}"):
                self.assertIsNone(re.search(wzor, tekst), "%s: %s" % (nazwa, wzor))
        dane = czytaj(ZR, DANE.PLIK_LUAU)
        self.assertIsNone(re.search(r"20\d\d-\d\d-\d\d", dane), "data w wygenerowanym pliku")

    def test_1c_zle_ustawienia(self):
        def zle(zmiana):
            k = copy.deepcopy(DANE._czytaj_json(DANE.USTAWIENIA))
            zmiana(k)
            with self.assertRaises(DANE.BladDanych):
                DANE._sprawdz(k)
        zle(lambda k: k["statystyki"].pop())
        zle(lambda k: k["statystyki"][1].update(stan="w_projekcie"))  # stan ≠ wpis w gry
        zle(lambda k: k["gry"]["sila"]["poziomy"][3].update(odstep_s=0.4))
        zle(lambda k: k["gry"]["sila"]["poziomy"][0].update(od_s=1))
        zle(lambda k: k["gry"]["pancerz"]["poziomy"][2].update(zmylki=0.9))
        zle(lambda k: k["przyrost"]["za_trafienie"].pop())
        zle(lambda k: k["ui"].update(przycisk_maly_px=40))
        zle(lambda k: k["ui"]["tekst_px"].update(maly=11))
        zle(lambda k: k["dzwieki"]["trafienie"].update(plik="moj_dzwiek.mp3"))
        zle(lambda k: k["sterowanie"]["gora"]["klawisze"].append("Strzalka"))
        zle(lambda k: k["gry"]["sila"].update(akcje=["gora", "lewo"]))
        # nowe rodzaje gier (17.11.2026)
        zle(lambda k: k["gry"]["kondycja"]["podbieg"].update(mnoznik=0.6))  # podbieg: kroki zachodzą na siebie
        zle(lambda k: k["gry"]["kondycja"].update(akcje=["lewa"]))
        zle(lambda k: k["gry"]["zrecznosc"].update(odpowiedz={"nisko": "skok", "wysoko": "skok"}))
        zle(lambda k: k["gry"]["zrecznosc"]["poziomy"][0].update(wartosci=3))
        zle(lambda k: k["gry"]["inteligencja"].update(min_dlugosc=5))
        zle(lambda k: k["gry"]["inteligencja"].update(baza=10))
        zle(lambda k: k["gry"]["inteligencja"]["poziomy"][1].update(pokaz_s=0.05))
        zle(lambda k: k["gry"]["szczescie"]["poziomy"][3].update(odstep_s=0.5))
        zle(lambda k: k["gry"]["szczescie"].update(start_tor="gora"))
        zle(lambda k: k["gry"]["szczescie"].update(pierwsze_s=1.0))
        zle(lambda k: k["gry"]["szczescie"].update(kubelek={"pojemnosc": 0, "uzupelnianie_na_s": 6}))
        zle(lambda k: k["gry"]["kondycja"].update(waga=0))
        zle(lambda k: k["gry"]["kondycja"].update(typ="skakanka"))
        zle(lambda k: k["gry"]["szczescie"].update(przyciski=["w_gore"]))
        zle(lambda k: k["dzwieki_katalog"].update(punkt="fanfara_ktorej_nie_ma"))
        zle(lambda k: k["dzwieki_katalog"]["trafienie"].update(kondycja="krok_ktorego_nie_ma"))
        DANE._sprawdz(DANE._czytaj_json(DANE.USTAWIENIA))  # prawdziwe ustawienia przechodzą

    def test_1d_szesc_statystyk_z_systemu_rpg(self):
        rpg = czytaj(REPO, "B&C", "Gra", "System RPG.md")
        # sekcja „## Sześć statystyk”: punkty „- **Siła** — …”, „- **Kondycja (Życie)** — …” (stan sejfu od 17.11.2026)
        m = re.search(r"## Sześć statystyk\n(.*?)(\n## |\Z)", rpg, re.S)
        self.assertIsNotNone(m)
        nazwy = [x.split(" (")[0].strip() for x in re.findall(r"^- \*\*([^*]+)\*\*", m.group(1), re.M)]
        self.assertEqual([s["nazwa"] for s in D["statystyki"]], nazwy)
        domyslne = czytaj(REPO, "src", "server", "PlayerStatsDefaults.server.luau")
        for s in D["statystyki"]:
            self.assertRegex(domyslne, r"\b%s\s*=" % s["atrybut"])
            self.assertNotEqual(s["atrybut"], s["atrybut_sesji"])
        # od 17.11.2026 (noc): wszystkie sześć mini-gier grywalne (D-074: każda statystyka ma mini-grę)
        self.assertEqual(sorted(s["id"] for s in D["statystyki"] if s["stan"] == "grywalna"), sorted(GRY))
        self.assertEqual(sorted(D["gry"]), sorted(GRY))
        self.assertEqual(sorted(D["swiat"]), sorted(GRY + ("przybycie", "patrz_przybycie")))

    def test_1e_styk_z_bazarem(self):
        m = DANE._czytaj_json(DANE.MIEJSCA_BAZARU)
        tc = [x for x in m["miejsca"] if x["id"] == D["id_miejsca_bazaru"]]
        self.assertEqual(len(tc), 1)
        self.assertEqual(tc[0]["akcja"], "okno")
        dane_bazaru = czytaj(REPO, "swiat", "miasteczko_bazar_gra", "zrodla", "DaneBazaru.luau")
        self.assertIn('zdarzenie_okien = "%s"' % D["zdarzenie_okien"], dane_bazaru)
        self.assertIn('kontener = "%s"' % D["bazar"]["kontener"], dane_bazaru)
        zb = czytaj(REPO, "swiat", "miasteczko_bazar_gra", "zbuduj.py")
        self.assertIn('p.Name = "E " .. id', zb)
        self.assertEqual(D["bazar"]["podpowiedz"], "Punkty/E " + D["id_miejsca_bazaru"])
        klient_bazaru = czytaj(REPO, "swiat", "miasteczko_bazar_gra", "zrodla", "KlientBazaru.client.luau")
        self.assertIn("okna:GetAttribute(id)", klient_bazaru)  # atrybut zdarzenia wyłącza dymek „w budowie”
        zn = DANE._czytaj_json(DANE.ZNACZNIKI)["training_center"]
        self.assertEqual(D["bazar"]["punkt_zapasowy"], zn["podpowiedz"])

    def test_1f_arena_z_dala_od_zajetych_obszarow(self):
        mn, mx = SCENA.obrys(D)
        krainy = DANE._czytaj_json(os.path.join(REPO, "swiat", "teleport_chmury", "krainy.json"))
        prostokaty = []

        def zbierz(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k == "obszary_xz":
                        prostokaty.extend(v)
                    else:
                        zbierz(v)
            elif isinstance(o, list):
                for v in o:
                    zbierz(v)
        zbierz(krainy)
        self.assertGreater(len(prostokaty), 5)
        # punkty z innych pakietów: demo przy (0; 0), sale testów walki, wybór klasy, makieta przejścia przez chmury
        prostokaty += [[-400, 400, -400, 600], [-150, 150, 3850, 4150], [-5700, -4300, 4300, 5700]]
        for x0, x1, z0, z1 in prostokaty:
            dx = max(x0 - mx[0], mn[0] - x1, 0)
            dz = max(z0 - mx[2], mn[2] - z1, 0)
            self.assertGreater(math.hypot(dx, dz), 500, "arena za blisko obszaru %s" % [x0, x1, z0, z1])
        self.assertGreater(mn[1], 200, "arena wysoko nad mapami")


# ============================================================================================== 2. logika
class TestLogiki(unittest.TestCase):
    def test_2a_plan_rundy(self):
        for gra in CZASOWE + ("szczescie",):
            G = D["gry"][gra]
            licz = {}
            wszystkie = 0
            for z in range(1, 301):
                pl = LT.plan(D, gra, z)
                self.assertEqual(pl, LT.plan(D, gra, z))
                self.assertEqual(pl[0]["t"], G.get("pierwsze_s", D["runda"]["pierwsze_s"]))
                self.assertLessEqual(pl[-1]["t"], D["runda"]["dlugosc_s"] - D["runda"]["koniec_zapas_s"] + 1e-9)
                for a, b in zip(pl, pl[1:]):
                    p = G["poziomy"][a["poziom"] - 1]
                    najkr = p["odstep_s"] * (1 - G["rozrzut"])
                    if a.get("podbieg") and b.get("podbieg"):
                        najkr *= G["podbieg"]["mnoznik"]
                    self.assertGreaterEqual(b["t"] - a["t"], najkr - 2e-3, (gra, z, a, b))
                    if G["typ"] != "lapanie":
                        self.assertGreater(b["t"] - a["t"], 2 * max(a["okno"], b["okno"]) + 0.05 - 1e-3)
                for e in pl:
                    p = G["poziomy"][e["poziom"] - 1]
                    # czas zdarzenia jest zaokrąglony do 1 ms — tuż przed granicą poziomu może wyjść równo granica
                    self.assertIn(e["poziom"], (LT.poziom(G, e["t"]), LT.poziom(G, e["t"] - 1.5e-3)))
                    self.assertEqual(e["okno"], p.get("okno_s", 0))
                    licz[e["wartosc"]] = licz.get(e["wartosc"], 0) + 1
                    wszystkie += 1
                    if G["typ"] == "kierunki":
                        self.assertIn(e["wartosc"], G["kierunki"][:p["kierunki"]])
                    elif G["typ"] == "blok":
                        self.assertIn(e["wartosc"], ("cios", "zmylka"))
                        if e["poziom"] == 1:
                            self.assertEqual(e["wartosc"], "cios")
                    elif G["typ"] == "rytm":
                        self.assertEqual(e["wartosc"], G["kierunki"][(e["nr"] - 1) % 2], "stopy na zmianę")
                        if e["poziom"] <= 2:
                            self.assertNotIn("podbieg", e, "podbiegi dopiero od trzeciego poziomu")
                    elif G["typ"] == "unik":
                        self.assertIn(e["wartosc"], G["wartosci"][:p["wartosci"]])
                        if p["zmiany"] == 0:
                            self.assertNotIn("zmiana", e)
                    else:
                        self.assertIn(e["wartosc"], ("koniczyna", "zlota", "kamien"))
                        self.assertTrue(0 <= e["los"] < 1)
                        if p["kamienie"] == 0:
                            self.assertNotEqual(e["wartosc"], "kamien")
                        if "wiatr" in e:
                            self.assertIn(e["wiatr"], (-1, 1))
                            self.assertNotEqual(e["wartosc"], "kamien")
            self.assertNotEqual(LT.plan(D, gra, 1), LT.plan(D, gra, 2))
            if gra == "pancerz":
                self.assertTrue(0.1 < licz["zmylka"] / wszystkie < 0.25, licz)
            if gra == "zrecznosc":
                self.assertTrue(0.3 < licz["wysoko"] / wszystkie < 0.5, licz)  # pierwszy poziom tylko niskie
            if gra == "szczescie":
                self.assertTrue(0.12 < licz["kamien"] / wszystkie < 0.3, licz)
                self.assertTrue(0.03 < licz["zlota"] / wszystkie < 0.1, licz)
        # Runy: lista run bez tej samej dwa razy z rzędu (podwójnego mignięcia nie widać), wszystkie cztery w użyciu
        G = D["gry"]["inteligencja"]
        for z in range(1, 301):
            pl = LT.plan(D, "inteligencja", z)
            self.assertEqual(len(pl), G["baza"])
            self.assertEqual([e["nr"] for e in pl], list(range(1, G["baza"] + 1)))
            for a, b in zip(pl, pl[1:]):
                self.assertNotEqual(a["wartosc"], b["wartosc"])
            self.assertEqual(set(e["wartosc"] for e in pl), set(G["runy"]))

    def test_2b_przyrost_seria_pasek(self):
        P = D["przyrost"]
        # pasek z BALANS_1711 (część 6): 4 / 5 / 6 / 8 jednostek = ×1 / ×1,25 / ×1,5 / ×2, próg 40 przy W = 0
        self.assertEqual([LT.przyrost(D, s) for s in (1, 4, 5, 9, 10, 19, 20, 99)], [4, 4, 5, 5, 6, 6, 8, 8])
        self.assertEqual(LT.prog(D, 0, LT.pula(D, 1)), 40)
        self.assertEqual(LT.pula(D, 1), 30)
        self.assertEqual(LT.pula(D, 65), 670)
        self.assertEqual(LT.prog(D, 3, 30), 40 * 4)  # W = 10% puli → próg ×4 (malejący zysk)
        self.assertEqual(LT.punkty_za_serie(D, 10)[0], 1, "10 trafień bez serii-premii ≈ +1 punkt świeżej statystyki")
        d2 = copy.deepcopy(D)
        d2["przyrost"]["mnoznik_centrum"] = 2
        self.assertEqual(LT.przyrost(d2, 12), 12)
        # wariant dosłowny D-050 (✅): +1 za trafienie, seria daje więcej, bez malejącego zysku — tylko zmiana danych
        d050 = copy.deepcopy(D)
        d050["przyrost"].update(za_trafienie=[1, 2, 3, 4], prog_paska=1, malejacy_zysk=False)
        DANE._sprawdz(dict(DANE._czytaj_json(DANE.USTAWIENIA), przyrost=d050["przyrost"]))
        R = runda("sila", 4)
        R2 = LT.nowa_runda(d050, "sila", 1, R["t0"], R["plan"])
        punkty = []
        for e in R2["plan"][:12]:
            punkty.append(LT.zgloszenie(d050, R2, e["wartosc"], R2["t0"] + e["t"], R2["t0"] + e["t"] + 0.05)["przyrost"])
        self.assertEqual(punkty, [1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3])
        # waga mini-gry (D-074: wyrównanie jednostek na minutę) mnoży jednostki za trafienie; Siła i Pancerz — 1
        for gra in GRY:
            G = D["gry"][gra]
            for s in (1, 5, 10, 20):
                self.assertAlmostEqual(LT.przyrost(D, s, G), LT.przyrost(D, s) * G.get("waga", 1))
        self.assertEqual((D["gry"]["sila"]["waga"], D["gry"]["pancerz"]["waga"]), (1, 1))
        R = runda("kondycja", 3)
        e = R["plan"][0]
        w = LT.zgloszenie(D, R, e["wartosc"], R["t0"] + e["t"], R["t0"] + e["t"] + 0.05)
        self.assertAlmostEqual(w["jednostki"], 4 * D["gry"]["kondycja"]["waga"])

    def test_2c_trafienie_pudlo_zmylka_pusty_dubel(self):
        R = runda("sila", 5)
        e1, e2, e3 = R["plan"][0], R["plan"][1], R["plan"][2]
        t = R["t0"] + e1["t"]
        w = LT.zgloszenie(D, R, e1["wartosc"], t + e1["okno"], t + 0.1)
        self.assertTrue(w["trafienie"], "brzeg okna = trafienie")
        self.assertEqual((w["seria"], w["jednostki"], w["przyrost"], w["pasek"]), (1, 4, 0, 4))
        w = LT.zgloszenie(D, R, e1["wartosc"], t + 0.1, t + 0.2)
        self.assertEqual(w["powod"], "dubel", "podwójne kliknięcie nie karze")
        self.assertEqual(R["seria"], 1)
        t2 = R["t0"] + e2["t"]
        zly = [k for k in D["gry"]["sila"]["akcje"] if k != e2["wartosc"]][0]
        w = LT.zgloszenie(D, R, zly, t2, t2 + 0.05)
        self.assertEqual((w["trafienie"], w["powod"], w["seria"]), (False, "zly_kierunek", 0))
        t3 = R["t0"] + e3["t"]
        w = LT.zgloszenie(D, R, e3["wartosc"], t3 - e3["okno"] - 0.01, t3 - e3["okno"])
        self.assertEqual(w["powod"], "za_wczesnie")
        w = LT.zgloszenie(D, R, "gora", t3 + 0.45, t3 + 0.45)
        self.assertEqual(w["powod"], "pusty", "naciśnięcie bez zdarzenia w pobliżu")
        e4 = R["plan"][3]
        t4 = R["t0"] + e4["t"]
        w = LT.zgloszenie(D, R, e4["wartosc"], t4 + e4["okno"] + 0.02, t4 + e4["okno"] + 0.1)
        self.assertEqual(w["powod"], "za_pozno")
        e5 = R["plan"][4]
        wyg = LT.przeterminowane(D, R, R["t0"] + e5["t"] + e5["okno"] + D["ochrona"]["max_opoznienie_s"] + 0.01)
        self.assertEqual([(x["nr"], x["powod"]) for x in wyg], [(5, "przepuszczone")])
        self.assertEqual((R["trafienia"], R["pudla"], R["puste"]), (1, 4, 1))
        # Pancerz: zmyłka przeczekana = trafienie, zablokowana = pudło
        for z in range(1, 400):
            P = runda("pancerz", z)
            zm = [e for e in P["plan"] if e["wartosc"] == "zmylka"]
            if len(zm) >= 2:
                break
        a, b2 = zm[0], zm[1]
        for e in P["plan"]:
            if e["nr"] >= a["nr"]:
                break
            LT.zgloszenie(D, P, "blok", P["t0"] + e["t"], P["t0"] + e["t"] + 0.05)
        wyg = LT.przeterminowane(D, P, P["t0"] + a["t"] + a["okno"] + D["ochrona"]["max_opoznienie_s"] + 0.01)
        self.assertEqual(wyg[-1]["powod"], "przetrwana_zmylka")
        self.assertTrue(wyg[-1]["trafienie"])
        for e in P["plan"]:
            if a["nr"] < e["nr"] < b2["nr"]:
                LT.zgloszenie(D, P, "blok", P["t0"] + e["t"], P["t0"] + e["t"] + 0.05)
        w = LT.zgloszenie(D, P, "blok", P["t0"] + b2["t"], P["t0"] + b2["t"] + 0.05)
        self.assertEqual((w["trafienie"], w["powod"]), (False, "zmylka"))

    def test_2d_granice_czasu_klienta(self):
        O = D["ochrona"]
        R = runda("sila", 9)
        e = R["plan"][0]
        t = R["t0"] + e["t"]
        # klient twierdzi, że nacisnął idealnie, ale wiadomość przyszła za późno → serwer bierze własny czas
        w = LT.zgloszenie(D, R, e["wartosc"], t, t + O["max_opoznienie_s"] + 0.1)
        self.assertEqual(w["powod"], "za_pozno")
        R = runda("sila", 9)
        w = LT.zgloszenie(D, R, e["wartosc"], t + 5, t)  # czas z przyszłości → czas serwera (= t, trafienie)
        self.assertTrue(w["trafienie"])
        for zly in ("tekst", None, float("nan"), float("inf"), True):
            R = runda("sila", 9)
            w = LT.zgloszenie(D, R, e["wartosc"], zly, t)
            self.assertTrue(w["trafienie"], repr(zly))
        R = runda("sila", 9)
        self.assertEqual(LT.zgloszenie(D, R, "miecz", t, t)["powod"], "zla_wartosc")
        self.assertEqual(LT.zgloszenie(D, R, 7, t, t)["powod"], "zla_wartosc")
        P = runda("pancerz", 9)
        self.assertEqual(LT.zgloszenie(D, P, "gora", t, t)["powod"], "zla_wartosc")

    def test_2e_spam_nie_oplaca_sie(self):
        O = D["ochrona"]
        R = runda("sila", 3)
        t = R["t0"] + 5
        przyjete = 0
        for i in range(100):
            w = LT.zgloszenie(D, R, "gora", t + i * 0.01, t + i * 0.01)
            przyjete += w["przyjete"]
        self.assertLessEqual(przyjete, O["pojemnosc"] + O["uzupelnianie_na_s"] * 1.0 + 1)
        self.assertGreaterEqual(R["spam"], 90)
        # bot wciskający losowe akcje 20 razy na sekundę przez całą rundę vs gracz trafiający 80% — w KAŻDEJ grze
        rnd = random.Random(5)
        for gra in GRY:
            zyski_bota, zyski_gracza = [], []
            for z in range(1, 31):
                B = runda(gra, z, 0.0)
                t = 0.0
                while t < D["runda"]["dlugosc_s"] + 1:
                    a = rnd.choice(D["gry"][gra]["akcje"])
                    LT.zgloszenie(D, B, a, t, t)
                    LT.przeterminowane(D, B, t)
                    t += 0.05
                LT.przeterminowane(D, B, 1e6)
                zyski_bota.append(B["jednostki"])
                if gra == "inteligencja":
                    # Runy: zgadywanie 1 z 4 run zawsze coś daje (bot ok. 18% gracza mylącego 1 runę na 10, ok. 25%
                    # gracza mylącego co piątą — taki gracz rzadko kończy sekwencję); porównanie z graczem 90% run
                    P = gracz_runy(runda(gra, z, 0.0), rnd, blad=0.1)
                elif gra == "szczescie":
                    P = gracz_koniczyn(runda(gra, z, 0.0), rnd, celnosc=0.8)
                else:
                    P = runda(gra, z, 0.0)
                    for e in P["plan"]:
                        if e["wartosc"] != "zmylka" and rnd.random() < 0.8:
                            LT.zgloszenie(D, P, akcja_dla(gra, e), e["t"] + 0.03, e["t"] + 0.08)
                        LT.przeterminowane(D, P, e["t"] + 0.6)
                    LT.przeterminowane(D, P, 1e6)
                zyski_gracza.append(P["jednostki"])
            self.assertLess(sum(zyski_bota), 0.2 * sum(zyski_gracza), (gra, sum(zyski_bota), sum(zyski_gracza)))

    def test_2f_koniec_rundy(self):
        O = D["ochrona"]
        R = runda("pancerz", 11)
        kon = R["t0"] + D["runda"]["dlugosc_s"]
        LT.przeterminowane(D, R, kon)
        self.assertFalse(R["koniec"])
        LT.przeterminowane(D, R, kon + O["max_opoznienie_s"] + 0.01)
        self.assertTrue(R["koniec"])
        self.assertEqual(R["trafienia"] + R["pudla"], len(R["plan"]))
        self.assertEqual(LT.zgloszenie(D, R, "blok", kon + 1, kon + 1)["powod"], "koniec")
        p = LT.podsumowanie(D, R)
        self.assertEqual(p["n"], len(R["plan"]))

    def test_2g_opoznienie_sieci(self):
        """Gracz naciska idealnie, wiadomość dochodzi po 0–0,3 s: czas klienta mieści się w granicach → wszystko trafia."""
        rnd = random.Random(8)
        for gra in CZASOWE:
            for z in range(1, 31):
                R = runda(gra, z, 50.0)
                for e in R["plan"]:
                    tk = R["t0"] + e["t"] + rnd.uniform(-0.6, 0.6) * e["okno"]
                    if e["wartosc"] != "zmylka":
                        LT.zgloszenie(D, R, akcja_dla(gra, e), tk, tk + rnd.uniform(0, 0.3))
                    LT.przeterminowane(D, R, tk + 0.3)
                LT.przeterminowane(D, R, 1e6)
                G = D["gry"][gra]
                self.assertEqual(R["trafienia"], len(R["plan"]), (gra, z))
                self.assertAlmostEqual(R["jednostki"], sum(LT.przyrost(D, s, G) for s in range(1, len(R["plan"]) + 1)))
                self.assertEqual(R["suma"], LT.punkty_za_serie(D, len(R["plan"]), G=G)[0])
        # Koniczyny: klient rozstrzyga od razu przy upadku; te same ruchy dochodzą do serwera po 0–0,3 s (czasem
        # w innej kolejności), serwer co tik rozstrzyga z zapasem → ten sam wynik; dobry gracz nie ma pudeł
        for z in range(1, 21):
            R = runda("szczescie", z, 50.0)
            ruchy = []
            K = gracz_koniczyn(copy.deepcopy(R), random.Random(z), ruchy=ruchy)
            przyjscia = sorted((t + rnd.uniform(0, 0.3), t, tor) for t, tor in ruchy)
            tik, i = R["t0"], 0
            while tik < R["t0"] + D["runda"]["dlugosc_s"] + 1:
                while i < len(przyjscia) and przyjscia[i][0] <= tik:
                    LT.zgloszenie(D, R, przyjscia[i][2], przyjscia[i][1], przyjscia[i][0])
                    i += 1
                LT.przeterminowane(D, R, tik)
                tik += D["ochrona"]["tik_s"]
            LT.przeterminowane(D, R, 1e9)
            self.assertEqual((R["trafienia"], R["pudla"], R["jednostki"]), (K["trafienia"], K["pudla"], K["jednostki"]), z)
            self.assertEqual(R["pudla"], 0, "gracz idący zawsze pod koniczynę i spod kamienia nie ma pudeł")
            self.assertEqual(R["trafienia"], sum(1 for e in R["plan"] if e["wartosc"] != "kamien"))

    def test_2h_balans_szesciu_gier(self):
        """D-074: żadna mini-gra nie może dawać wyraźnie więcej na minutę (model gracza: w grach czasowych celność
        zależy od okna; Runy — reakcja 0,55 s, runa co 0,42 s, błąd rośnie z długością; Koniczyny — 90% koniczyn)."""
        rnd = random.Random(74)
        wynik = {}
        for gra in GRY:
            sumy = []
            for z in range(1, 151):
                if gra == "inteligencja":
                    R = runda(gra, z, 0.0)
                    t = 0.0
                    while t < D["runda"]["dlugosc_s"] and not R["koniec"]:
                        if t < R["pokazDo"]:
                            t = R["pokazDo"] + 0.55
                            continue
                        dobra = R["plan"][R["offset"] + R["poz"]]["wartosc"]
                        zle = rnd.random() < 0.03 + 0.012 * R["dl"]
                        LT.zgloszenie(D, R, [k for k in D["gry"][gra]["akcje"] if k != dobra][0] if zle else dobra, t, t + 0.05)
                        t += 0.42
                    LT.przeterminowane(D, R, 1e6)
                elif gra == "szczescie":
                    R = gracz_koniczyn(runda(gra, z, 0.0), rnd, celnosc=0.9)
                else:
                    R = runda(gra, z, 0.0)
                    for e in R["plan"]:
                        p = min(0.97, 0.5 + 1.5 * e["okno"])
                        if e["wartosc"] == "zmylka":
                            if rnd.random() > 0.85:
                                LT.zgloszenie(D, R, "blok", e["t"], e["t"] + 0.05)
                        elif rnd.random() < p:
                            LT.zgloszenie(D, R, akcja_dla(gra, e), e["t"], e["t"] + 0.05)
                        LT.przeterminowane(D, R, e["t"] + 0.6)
                    LT.przeterminowane(D, R, 1e6)
                sumy.append(R["jednostki"])
            wynik[gra] = sum(sumy) / len(sumy) * 60 / D["runda"]["dlugosc_s"]
        for gra in GRY:
            stosunek = wynik[gra] / wynik["sila"]
            self.assertTrue(0.85 <= stosunek <= 1.18, (gra, wynik))

    def test_2j_malejacy_zysk_jednej_mini_gry(self):
        """D-074: kolejne rundy tej samej mini-gry dają coraz mniej punktów; świeża statystyka wraca do pełnego tempa."""
        rnd = random.Random(9)
        pl = LT.pula(D, 10)

        def runda_modelu(gra, z, S0):
            R = LT.nowa_runda(D, gra, 1, 0.0, LT.plan(D, gra, z), S0)
            for e in R["plan"]:
                if e["wartosc"] != "zmylka" and rnd.random() < 0.85:
                    LT.zgloszenie(D, R, akcja_dla(gra, e), e["t"], e["t"] + 0.05)
                LT.przeterminowane(D, R, e["t"] + 0.6)
            LT.przeterminowane(D, R, 1e6)
            return R
        S0 = {"pasek": 0, "W": 0, "pula": pl}
        punkty = []
        for z in range(1, 21):
            R = runda_modelu("sila", z, S0)
            punkty.append(R["suma"])
            S0 = {"pasek": R["pasek"], "W": R["W"], "pula": pl}
        self.assertLess(sum(punkty[-5:]), 0.5 * sum(punkty[:5]), punkty)
        swieza = runda_modelu("pancerz", 1, {"pasek": 0, "W": 0, "pula": pl})["suma"]
        self.assertGreater(swieza, punkty[-1], (swieza, punkty))

    def test_2k_biezna_rytm(self):
        """Bieżnia: lewa / prawa na zmianę w oknie rytmu; zła stopa, za wcześnie, przepuszczony krok; seria i waga."""
        G = D["gry"]["kondycja"]
        R = runda("kondycja", 21)
        e1, e2, e3, e4 = R["plan"][:4]
        self.assertEqual((e1["wartosc"], e2["wartosc"]), ("lewa", "prawa"))
        t = R["t0"]
        w = LT.zgloszenie(D, R, "lewa", t + e1["t"] + e1["okno"], t + e1["t"] + e1["okno"] + 0.05)
        self.assertTrue(w["trafienie"], "brzeg okna = trafienie")
        self.assertAlmostEqual(w["jednostki"], 4 * G["waga"])
        w = LT.zgloszenie(D, R, "lewa", t + e2["t"], t + e2["t"] + 0.05)
        self.assertEqual((w["trafienie"], w["powod"], w["seria"]), (False, "zly_kierunek", 0), "zła stopa")
        w = LT.zgloszenie(D, R, "lewa", t + e3["t"] - e3["okno"] - 0.02, t + e3["t"] - e3["okno"])
        self.assertEqual(w["powod"], "za_wczesnie")
        wyg = LT.przeterminowane(D, R, t + e4["t"] + e4["okno"] + D["ochrona"]["max_opoznienie_s"] + 0.01)
        self.assertEqual([(x["nr"], x["powod"]) for x in wyg], [(4, "przepuszczone")])
        # pełna runda w rytmie: każdy krok trafiony, seria rośnie do końca, podbiegi krótsze, ale dalej rozdzielne
        R = runda("kondycja", 5, 0.0)
        for e in R["plan"]:
            LT.zgloszenie(D, R, e["wartosc"], e["t"] + 0.05, e["t"] + 0.1)
        LT.przeterminowane(D, R, 1e6)
        self.assertEqual((R["trafienia"], R["najdluzsza"]), (len(R["plan"]), len(R["plan"])))
        self.assertTrue(55 <= len(R["plan"]) <= 75, len(R["plan"]))
        podbiegi = sum(1 for z in range(1, 101) for e in LT.plan(D, "kondycja", z) if e.get("podbieg"))
        self.assertGreater(podbiegi, 0)
        # zawsze ta sama stopa (zamiast na zmianę) nie opłaca się: co drugi krok to pudło, seria nie rośnie
        R = runda("kondycja", 5, 0.0)
        for e in R["plan"]:
            LT.zgloszenie(D, R, "lewa", e["t"], e["t"] + 0.05)
            LT.przeterminowane(D, R, e["t"] + 0.6)
        LT.przeterminowane(D, R, 1e6)
        self.assertLessEqual(R["najdluzsza"], 1)
        self.assertLess(R["jednostki"], 0.3 * sum(LT.przyrost(D, s, G) for s in range(1, len(R["plan"]) + 1)))

    def test_2l_klody_skok_padnij(self):
        """Kłody: niska kłoda = SKOK, wysoka = PADNIJ; odwrotna akcja to pudło; na pierwszym poziomie tylko niskie."""
        G = D["gry"]["zrecznosc"]
        self.assertEqual(LT.odpowiedz(G, "nisko"), "skok")
        self.assertEqual(LT.odpowiedz(G, "wysoko"), "padnij")
        for z in range(1, 50):
            R = runda("zrecznosc", z)
            wys = [e for e in R["plan"] if e["wartosc"] == "wysoko"]
            if wys:
                break
        e = wys[0]
        t = R["t0"] + e["t"]
        w = LT.zgloszenie(D, R, "skok", t, t + 0.05)
        self.assertEqual((w["trafienie"], w["powod"]), (False, "zly_kierunek"), "skok pod wysoką kłodą")
        nis = [x for x in R["plan"] if x["wartosc"] == "nisko" and x["nr"] > e["nr"] + 1][0]
        t = R["t0"] + nis["t"]
        w = LT.zgloszenie(D, R, "skok", t - 0.1, t)
        self.assertTrue(w["trafienie"])
        self.assertAlmostEqual(w["jednostki"], 4 * G["waga"])
        self.assertEqual(LT.zgloszenie(D, R, "unik", t, t)["powod"], "zla_wartosc")
        # zmiana wysokości (zmyłka w obrazie) nie zmienia oceny: liczy się wartość zdarzenia
        for z in range(1, 400):
            pl = LT.plan(D, "zrecznosc", z)
            zm = [x for x in pl if x.get("zmiana")]
            if zm:
                break
        self.assertTrue(zm)
        self.assertTrue(all(x["poziom"] >= 3 for x in zm), "zmiany wysokości dopiero na trzecim poziomie")
        R = LT.nowa_runda(D, "zrecznosc", 1, 0.0, pl)
        x = zm[0]
        self.assertTrue(LT.zgloszenie(D, R, LT.odpowiedz(G, x["wartosc"]), x["t"], x["t"] + 0.05)["trafienie"])
        # pełna runda bez pudła: ok. 30 kłód w 45 s
        R = runda("zrecznosc", 7, 0.0)
        for e in R["plan"]:
            LT.zgloszenie(D, R, LT.odpowiedz(G, e["wartosc"]), e["t"], e["t"] + 0.05)
        LT.przeterminowane(D, R, 1e6)
        self.assertEqual(R["trafienia"], len(R["plan"]))
        self.assertTrue(25 <= len(R["plan"]) <= 36, len(R["plan"]))

    def test_2m_runy_sekwencja(self):
        """Runy: pokaz → wpisywanie; naciśnięcia w czasie pokazu pomijane bez kary; zła runa = pudło i sekwencja krótsza
        o karę; cała sekwencja = zaklęcie i +1 runa; bezczynność = ten sam pokaz od początku; dubel bez kary."""
        G = D["gry"]["inteligencja"]
        O = D["ochrona"]
        R = runda("inteligencja", 31, 0.0)
        self.assertEqual((R["dl"], R["poz"], R["pokazOd"]), (G["start_dlugosc"], 0, D["runda"]["pierwsze_s"]))
        p1 = G["poziomy"][0]
        self.assertAlmostEqual(R["pokazDo"], 1.0 + 3 * p1["pokaz_s"] + 2 * p1["przerwa_s"])
        run = [e["wartosc"] for e in R["plan"]]
        w = LT.zgloszenie(D, R, run[0], 1.2, 1.2)
        self.assertEqual((w["przyjete"], w["powod"]), (False, "pokaz"), "w czasie pokazu: pominięte, bez kary")
        self.assertEqual((R["seria"], R["pudla"], R["poz"]), (0, 0, 0))
        t = R["pokazDo"] + 0.3
        for i in range(3):
            w = LT.zgloszenie(D, R, run[i], t, t + 0.05)
            self.assertTrue(w["trafienie"], i)
            self.assertEqual(w["nr"], i + 1)
            t += 0.4
        self.assertTrue(w["zaklecie"])
        self.assertEqual((R["dl"], R["poz"], R["zaklecia"], R["seria"]), (4, 0, 1, 3))
        self.assertAlmostEqual(R["pokazOd"], t - 0.4 + G["przerwa_s"])
        self.assertAlmostEqual(w["jednostki"], 4 * G["waga"])
        # ta sama sekwencja dłuższa o jedną runę (początek się nie zmienia)
        t = R["pokazDo"] + 0.3
        LT.zgloszenie(D, R, run[0], t, t)
        w = LT.zgloszenie(D, R, run[0], t + 0.1, t + 0.1)
        self.assertEqual(w["powod"], "dubel", "drugie stuknięcie tej samej runy zaraz po pierwszej — bez kary")
        zla = [k for k in G["runy"] if k != run[1]][0]
        w = LT.zgloszenie(D, R, zla, t + 0.4, t + 0.4)
        self.assertEqual((w["trafienie"], w["powod"], w["seria"]), (False, "zla_runa", 0))
        self.assertEqual((R["dl"], R["poz"]), (max(G["min_dlugosc"], 4 - G["kara"]), 0))
        self.assertAlmostEqual(R["pokazOd"], t + 0.4 + G["przerwa_bledu_s"])
        # bezczynność: po bezczynnosc_s bez naciśnięcia pokaz jeszcze raz (chwila nie zależy od chwili sprawdzenia)
        do = R["pokazDo"]
        LT.przeterminowane(D, R, do + G["bezczynnosc_s"] - 0.1)
        self.assertEqual(R["pokazDo"], do)
        pokazy = R["pokazy"]
        for kiedy in (0.05, 2.0):
            X = copy.deepcopy(R)
            LT.przeterminowane(D, X, do + G["bezczynnosc_s"] + kiedy)
            self.assertAlmostEqual(X["pokazOd"], do + G["bezczynnosc_s"])
            self.assertEqual(X["pokazy"], pokazy + 1)
        # oczekiwana runa poza listą (nie zdarza się w 45 s) — każde naciśnięcie to pudło, bez błędu
        X = runda("inteligencja", 31, 0.0)
        X["offset"] = len(X["plan"])
        w = LT.zgloszenie(D, X, "gora", X["pokazDo"] + 0.1, X["pokazDo"] + 0.1)
        self.assertEqual(w["powod"], "zla_runa")
        # długość: od startu rośnie do maks, potem nowe zaklęcie od startu i dalsze runy z listy
        R = runda("inteligencja", 32, 0.0)
        dl = []
        t = 0.0
        while len(dl) < 9:
            if t < R["pokazDo"]:
                t = R["pokazDo"] + 0.1
            w = LT.zgloszenie(D, R, R["plan"][R["offset"] + R["poz"]]["wartosc"], t, t)
            t += 0.3
            if w.get("zaklecie"):
                dl.append(R["dl"])
            if t > 1e4:
                break
        self.assertEqual(dl[:6], [4, 5, 6, 7, 8, G["start_dlugosc"]])
        self.assertEqual(R["offset"], G["maks_dlugosc"])
        # koniec rundy dopiero po czasie + zapas; potem „koniec”
        R = runda("inteligencja", 33, 0.0)
        LT.przeterminowane(D, R, D["runda"]["dlugosc_s"])
        self.assertFalse(R["koniec"])
        LT.przeterminowane(D, R, D["runda"]["dlugosc_s"] + O["max_opoznienie_s"] + 0.01)
        self.assertTrue(R["koniec"])
        self.assertEqual(LT.zgloszenie(D, R, "gora", 99, 99)["powod"], "koniec")
        p = LT.podsumowanie(D, R)
        self.assertEqual((p["n"], p["zaklecia"], p["najdluzszaSekwencja"]), (0, 0, 0))
        # dobry gracz: większość run trafiona, kilka zaklęć w rundzie
        R = gracz_runy(runda("inteligencja", 34, 0.0), random.Random(3), blad=0.05)
        LT.przeterminowane(D, R, 1e6)
        self.assertGreaterEqual(R["zaklecia"], 3)
        self.assertGreater(R["trafienia"], 4 * R["pudla"])

    def test_2n_koniczyny_lapanie(self):
        """Koniczyny: ruch koszyka nie jest werdyktem; koniczyna złapana, gdy koszyk jest na jej torze w chwili upadku;
        spada poza tor koszyka z chwili, gdy zaczęła spadać (stanie w miejscu = 0), i omija tor lecącego kamienia;
        kamień celuje w koszyk; złota = ×2; kamień obok = bez werdyktu."""
        G = D["gry"]["szczescie"]
        R = runda("szczescie", 41, 0.0)
        w = LT.zgloszenie(D, R, "lewy", 0.5, 0.5)
        self.assertEqual((w["przyjete"], w["ruch"], w["tor"], w["powod"]), (True, True, 1, "ruch"))
        self.assertEqual(LT.kod_wyniku(w), "R")
        self.assertEqual((R["seria"], R["pudla"], R["trafienia"], R["puste"]), (0, 0, 0, 0))
        self.assertEqual(LT.tor_w(D, R, 0.4), 2)
        self.assertEqual(LT.tor_w(D, R, 0.5), 1)
        self.assertEqual(LT.zgloszenie(D, R, "gora", 0.6, 0.6)["powod"], "zla_wartosc")
        # stanie w miejscu: koniczyny nigdy nie spadają na tor koszyka, kamienie zawsze → 0 jednostek, same pudła
        for z in range(1, 41):
            R = runda("szczescie", z, 0.0)
            LT.przeterminowane(D, R, 1e6)
            self.assertEqual((R["trafienia"], R["jednostki"]), (0, 0), z)
            self.assertEqual(R["kamienie"], sum(1 for e in R["plan"] if e["wartosc"] == "kamien"))
        # model gracza: wszystko złapane, żadnego kamienia; złote dają podwójnie
        for z in range(1, 41):
            R = gracz_koniczyn(runda("szczescie", z, 0.0), random.Random(z))
            n_k = sum(1 for e in R["plan"] if e["wartosc"] != "kamien")
            self.assertEqual((R["trafienia"], R["pudla"], R["zlapane"]), (n_k, 0, n_k), z)
            mn = [G["zlota_mnoznik"] if e["wartosc"] == "zlota" else 1 for e in R["plan"] if e["wartosc"] != "kamien"]
            self.assertAlmostEqual(R["jednostki"], sum(LT.przyrost(D, s, G) * mn[s - 1] for s in range(1, n_k + 1)))
        # koniczyna nie spada na tor kamienia, który jeszcze leci (gdy jest wolny tor)
        sprawdzone = 0
        for z in range(1, 80):
            R = runda("szczescie", z, 0.0)
            rnd = random.Random(z)
            for e in R["plan"]:
                start = e["t"] - G["lot_s"]
                LT.zgloszenie(D, R, rnd.choice(G["tory"]), start - 0.2, start - 0.2)
                k, zt = LT.tory_zdarzenia(D, R, e)
                self.assertNotEqual(k, LT.tor_w(D, R, start)) if e["wartosc"] != "kamien" else None
                if e["wartosc"] != "kamien":
                    lecace = [LT.tory_zdarzenia(D, R, x)[0] for x in R["plan"] if x["nr"] < e["nr"] and
                              x["wartosc"] == "kamien" and x["t"] > start]
                    wolne = [i for i in (1, 2, 3) if i != LT.tor_w(D, R, start) and i not in lecace]
                    if wolne:
                        self.assertNotIn(k, lecace)
                        sprawdzone += 1
                    if "wiatr" in e:
                        self.assertEqual(abs(zt - k), 1)
                else:
                    self.assertEqual(k, LT.tor_w(D, R, start))
        self.assertGreater(sprawdzone, 500)
        # werdykt u klienta (zapas 0, od razu przy upadku) = werdykt serwera (z zapasem)
        R = runda("szczescie", 43, 0.0)
        K = copy.deepcopy(R)
        e = R["plan"][0]
        k, _ = LT.tory_zdarzenia(D, K, e)
        for X in (R, K):
            LT.zgloszenie(D, X, G["tory"][k - 1], e["t"] - 0.6, e["t"] - 0.6)
        wk = LT.przeterminowane(D, K, e["t"] + 0.001, 0)
        self.assertEqual(LT.przeterminowane(D, R, e["t"] + 0.001), [], "serwer czeka zapas na spóźnione ruchy")
        ws = LT.przeterminowane(D, R, e["t"] + D["ochrona"]["max_opoznienie_s"] + 0.01)
        self.assertEqual([(x["nr"], x["powod"], x["tor"]) for x in wk], [(x["nr"], x["powod"], x["tor"]) for x in ws])

    def test_2o_przerwanie_i_koniec_kazdej_gry(self):
        """Przerwanie rundy w połowie: podsumowanie liczy tylko rozstrzygnięte próby; koniec rundy w każdej grze."""
        for gra in GRY:
            R = runda(gra, 51, 0.0)
            if gra == "inteligencja":
                gracz_runy(R, random.Random(1), koniec=20.0)
            elif gra == "szczescie":
                G = D["gry"][gra]
                for e in R["plan"]:
                    if e["t"] > 20:
                        break
                    k, _ = LT.tory_zdarzenia(D, R, e)
                    if e["wartosc"] != "kamien":
                        LT.zgloszenie(D, R, G["tory"][k - 1], e["t"] - 0.5, e["t"] - 0.5)
                    LT.przeterminowane(D, R, e["t"] + 0.4)
            else:
                for e in R["plan"]:
                    if e["t"] > 20:
                        break
                    if e["wartosc"] != "zmylka":
                        LT.zgloszenie(D, R, akcja_dla(gra, e), e["t"], e["t"] + 0.05)
                    LT.przeterminowane(D, R, e["t"] + 0.6)
            R["koniec"] = True  # serwer: zakoncz(…, przerwana = true)
            p = LT.podsumowanie(D, R)
            self.assertGreater(p["trafienia"], 5, gra)
            self.assertEqual(p["celnosc"], math.floor(100 * p["trafienia"] / max(1, p["trafienia"] + p["pudla"] + p["puste"]) + 0.5))
            self.assertEqual(LT.zgloszenie(D, R, D["gry"][gra]["akcje"][0], 30, 30)["powod"], "koniec")
            # zwykły koniec: po czasie rundy + zapas
            R = runda(gra, 52, 0.0)
            LT.przeterminowane(D, R, D["runda"]["dlugosc_s"] + D["ochrona"]["max_opoznienie_s"] + 0.01)
            self.assertTrue(R["koniec"], gra)

    def test_2i_wejscie_start_arena_skala(self):
        O = D["ochrona"]
        S = LT.nowy_gracz()
        self.assertEqual(LT.wejscie(D, "sila", S, 10.0, O["zasieg_wejscia"] + 1, False)["powod"], "za_daleko")
        d2 = copy.deepcopy(D)
        d2["statystyki"][1]["stan"] = "w_projekcie"
        self.assertEqual(LT.wejscie(d2, "kondycja", LT.nowy_gracz(), 10.0, 1.0, False)["powod"], "w_projekcie")
        self.assertEqual(LT.wejscie(D, "kondycja", LT.nowy_gracz(), 10.0, 1.0, False)["powod"], "ok")
        self.assertEqual(LT.wejscie(D, "xyz", S, 10.0, 1.0, False)["powod"], "nieznana")
        self.assertEqual(LT.wejscie(D, 5, S, 10.0, 1.0, False)["powod"], "nieznana")
        self.assertTrue(LT.wejscie(D, "sila", S, 10.0, 1.0, False)["ok"])
        self.assertEqual(LT.wejscie(D, "pancerz", S, 10.5, None, True)["powod"], "za_szybko")
        self.assertTrue(LT.wejscie(D, "pancerz", S, 10.0 + O["odstep_wejsc_s"], None, True)["ok"])
        self.assertEqual(LT.start(D, LT.nowy_gracz(), 1.0)["powod"], "brak_gry")
        S["gra"] = "pancerz"
        self.assertTrue(LT.start(D, S, 20.0)["ok"])
        S["runda"] = {"koniec": False}
        self.assertEqual(LT.start(D, S, 30.0)["powod"], "trwa_runda")
        self.assertEqual(LT.wejscie(D, "sila", S, 40.0, 1.0, True)["powod"], "trwa_runda")
        S["runda"] = {"koniec": True}
        self.assertEqual(LT.start(D, S, 20.5)["powod"], "za_szybko")
        c = D["arena"]["srodek"]
        self.assertTrue(LT.w_arenie(D, c[0], c[1] + 3, c[2]))
        self.assertFalse(LT.w_arenie(D, c[0] + D["arena"]["rozmiar"][0] / 2 + 10, c[1] + 3, c[2]))
        self.assertFalse(LT.w_arenie(D, c[0], c[1] - 50, c[2]))
        self.assertEqual(LT.skala_ui(D, 667, 375), 1.0)
        self.assertEqual(LT.skala_ui(D, 480, 270), D["ui"]["skala_min"])
        self.assertEqual(LT.skala_ui(D, 3840, 2160), D["ui"]["skala_max"])


# ============================================================================================== 3. Luau w luau_mini
def luau_modul(plik):
    it = LM.Interpreter()
    rs = LM.Tabela()
    rs.set("IsStudio", lambda _self: True)
    game = LM.Tabela()
    game.set("GetService", lambda _self, _n: rs)
    it.globalne.z["game"] = game
    return it, it.wykonaj(czytaj(ZR, plik), plik)[0]


def norm(v):
    if isinstance(v, dict):
        return {k: norm(x) for k, x in v.items() if x is not None} if v else "pusty"
    if isinstance(v, list):
        return [norm(x) for x in v] if v else "pusty"
    if isinstance(v, bool) or v is None or isinstance(v, str):
        return v
    return round(float(v), 6)


@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py — Luau nie wykonany")
class TestLuau(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.it, cls.Dl = luau_modul(DANE.PLIK_LUAU)
        cls.L = cls.it.wykonaj(LOGIKA, "LogikaTreningu.luau")[0]

    def wolaj(self, nazwa, *argi):
        return self.it.wywolaj(self.L.get(nazwa), list(argi))

    def test_3a_pliki_parsuja_sie(self):
        bledy, parser = SLT.sprawdz_pliki(SLT.pliki_pakietu(), wypisz=lambda *_: None)
        self.assertTrue(parser)
        self.assertEqual(bledy, [])
        self.assertEqual(len(SLT.pliki_pakietu()), 4)

    def test_3b_przypadki_wzorcowe(self):
        ok, n, bledy = self.wolaj("sprawdzPrzypadki", self.Dl)
        self.assertTrue(ok, LM.z_luau(bledy))
        P = D["przypadki"]
        self.assertEqual(n, len(P["plany"]) + len(P["sekwencje"]) + len(P["przyrosty"]) + len(P["wejscia"]) + len(P["skale"]))
        zepsute = copy.deepcopy(D)
        zepsute["przypadki"]["sekwencje"][0]["wynik"]["kod"] += ",T99"
        zepsute["przypadki"]["plany"][0]["n"] += 1
        ok, _, bledy = self.wolaj("sprawdzPrzypadki", LM.do_luau(zepsute))
        self.assertFalse(ok)
        self.assertEqual(len(LM.z_luau(bledy)), 2)

    def test_3c_losowe_wywolania_jak_lustro(self):
        rnd = random.Random(1711)
        for _ in range(90):
            gra, z = rnd.choice(GRY), rnd.randrange(1, 2 ** 31 - 2)
            lu = LM.z_luau(self.wolaj("plan", self.Dl, gra, float(z))[0])
            self.assertEqual(norm(lu), norm(LT.plan(D, gra, z)))
        for _ in range(72):
            gra, z, t0 = rnd.choice(GRY), rnd.randrange(1, 2 ** 31 - 2), round(rnd.uniform(1, 9000), 3)
            kroki = DANE.sekwencja_krokow(D, gra, z, t0, rnd, ile=rnd.randrange(5, 40))
            s0 = {"pasek": round(rnd.uniform(0, 60), 3), "W": rnd.randrange(0, 200), "pula": LT.pula(D, rnd.randrange(1, 66))}
            kroki_lu = [{k: v for k, v in x.items() if v is not None} for x in kroki]
            kod_lu, R_lu = self.wolaj("wykonajKroki", self.Dl, gra, float(z), t0, LM.do_luau(kroki_lu), LM.do_luau(s0))
            kod_py, R_py = LT.wykonaj_kroki(D, gra, z, t0, kroki, s0)
            self.assertEqual(kod_lu, kod_py, gra)
            for pole in ("trafienia", "pudla", "puste", "spam", "odrzucone", "seria", "najdluzsza", "suma", "koniec",
                         "jednostki", "W", "pasek", "dl", "poz", "offset", "pokazOd", "pokazDo", "pokazy", "zaklecia",
                         "zlapane", "kamienie"):
                self.assertEqual(norm(R_lu.get(pole)), norm(R_py.get(pole)), (gra, pole))
            if gra == "szczescie":
                v = LM.z_luau(R_lu.get("tory"))
                tory_lu = {str(i + 1): x for i, x in enumerate(v)} if isinstance(v, list) else {str(k): x for k, x in v.items()}
                self.assertEqual(norm(tory_lu), norm({str(k): x for k, x in R_py["tory"].items()}))
            p_lu = LM.z_luau(self.wolaj("podsumowanie", self.Dl, R_lu)[0])
            self.assertEqual(norm(p_lu), norm(LT.podsumowanie(D, R_py)))
        for _ in range(150):
            S = LT.nowy_gracz()
            S["ostatnieWejscie"] = rnd.choice([LT.NIGDY, rnd.uniform(0, 100)])
            gra = rnd.choice(list(GRY) + ["nic", 3])
            teraz, odl, wa = rnd.uniform(0, 110), rnd.choice([None, rnd.uniform(0, 30)]), rnd.random() < 0.3
            Sl = LM.do_luau({"gra": None, "ostatnieWejscie": S["ostatnieWejscie"], "ostatniStart": LT.NIGDY})
            wl = LM.z_luau(self.wolaj("wejscie", self.Dl, gra if isinstance(gra, str) else float(gra), Sl, teraz, odl, wa)[0])
            wp = LT.wejscie(D, gra, S, teraz, odl, wa)
            self.assertEqual((wl["ok"], wl["powod"]), (wp["ok"], wp["powod"]))
        c = D["arena"]["srodek"]
        for _ in range(150):
            x, y, z = c[0] + rnd.uniform(-70, 70), c[1] + rnd.uniform(-40, 60), c[2] + rnd.uniform(-50, 50)
            self.assertEqual(self.wolaj("wArenie", self.Dl, x, y, z)[0], LT.w_arenie(D, x, y, z))
            w, h = float(rnd.randrange(300, 4000)), float(rnd.randrange(200, 2500))
            self.assertAlmostEqual(self.wolaj("skalaUI", self.Dl, w, h)[0], LT.skala_ui(D, w, h))
            t, n = rnd.uniform(0, 1e9), float(rnd.randrange(1, 1000))
            self.assertEqual(self.wolaj("ziarnoZCzasu", t, n)[0], LT.ziarno_z_czasu(t, n))
        for s in range(0, 41):
            self.assertEqual(self.wolaj("przyrost", self.Dl, float(s))[0], LT.przyrost(D, s))
            for gra in GRY:
                Gl = self.Dl.get("gry").get(gra)
                self.assertAlmostEqual(self.wolaj("przyrost", self.Dl, float(s), Gl)[0], LT.przyrost(D, s, D["gry"][gra]))
        for gra in GRY:
            Gl = self.Dl.get("gry").get(gra)
            for w in ("nisko", "wysoko", "lewo", "cios", "lewa"):
                self.assertEqual(self.wolaj("odpowiedz", Gl, w)[0], LT.odpowiedz(D["gry"][gra], w))
        for _ in range(100):
            lv = rnd.choice([None, "x", 0.5, float(rnd.randrange(1, 80)), rnd.uniform(1, 80)])
            self.assertEqual(self.wolaj("pula", self.Dl, lv)[0], LT.pula(D, lv))
            W, pl = float(rnd.randrange(0, 500)), float(LT.pula(D, rnd.randrange(1, 66)))
            self.assertAlmostEqual(self.wolaj("prog", self.Dl, W, pl)[0], LT.prog(D, W, pl), places=9)

    def test_3d_dane_w_luau_jak_w_pythonie(self):
        dl = LM.z_luau(self.Dl)
        for klucz in ("gry", "przyrost", "ochrona", "runda", "statystyki", "swiat", "ui", "sterowanie", "nazwy", "bazar", "arena",
                      "dzwieki_katalog"):
            self.assertEqual(norm(dl[klucz]), norm(D[klucz]), klucz)
        self.assertEqual(dl["skrot"], D["skrot"])

    def test_3e_kod_do_studio_parsuje_sie(self):
        kody = dict(ZB.wszystkie_kody(D))
        for sciezka, klasa, kontekst, tekst, plik in ZB.zrodla_pakietu():
            kody["skrypt " + plik] = ZB.kod_skryptu(D, sciezka, klasa, kontekst, tekst)
        kody["skrypty --skrypty"] = ('local f = workspace:FindFirstChild("%s") if not f then return "STOP" end '
                                     'f:SetAttribute("Skrot", "%s") return "OK"' % (D["kontener"], D["skrot"]))
        for nazwa, kod in kody.items():
            pelny = ZB.NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", str(ZB.MIEJSCE)) + kod
            LM.Parser(pelny, nazwa, LM.Interpreter()).program()
            self.assertIsNone(re.search(r"__[A-Z_]+__", kod), nazwa)


# ============================================================================================== 4. scena
def _pudlo(c):
    s = SCENA.rozmiar_osiowy(c)
    return [c["p"][i] - s[i] / 2 for i in range(3)], [c["p"][i] + s[i] / 2 for i in range(3)]


def _odcinek_w_pudle(a, b, mn, mx):
    """Czy odcinek a–b przecina pudło (metoda płyt)."""
    t0, t1 = 0.0, 1.0
    for i in range(3):
        d = b[i] - a[i]
        if abs(d) < 1e-9:
            if a[i] < mn[i] or a[i] > mx[i]:
                return False
            continue
        u0, u1 = (mn[i] - a[i]) / d, (mx[i] - a[i]) / d
        if u0 > u1:
            u0, u1 = u1, u0
        t0, t1 = max(t0, u0), min(t1, u1)
        if t0 > t1:
            return False
    return True


class TestSceny(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cz = SCENA.czesci(D)
        cls.lita = [c for c in cls.cz if c.get("t", 0) < 0.5]

    def test_4a_czesci_rozmiary_obrys(self):
        self.assertEqual(len(self.cz), LICZBA_CZESCI)
        self.assertEqual([c for c in self.cz if c["r"].startswith("Arena/Zapowiedzi")], [], "wszystkie gry mają stanowiska")
        sciezki = [c["r"] + "/" + c["n"] for c in self.cz]
        self.assertEqual(len(sciezki), len(set(sciezki)), "powtórzone nazwy w jednym rodzicu")
        A = D["arena"]
        c = A["srodek"]
        for x in self.cz:
            self.assertTrue(all(v >= 0.05 for v in x["s"]), x["n"])
            mn, mx = _pudlo(x)
            self.assertGreaterEqual(mn[0], c[0] - A["rozmiar"][0] / 2 - 1.01, x["n"])
            self.assertLessEqual(mx[0], c[0] + A["rozmiar"][0] / 2 + 1.01, x["n"])
            self.assertGreaterEqual(mn[2], c[2] - A["rozmiar"][1] / 2 - 1.01, x["n"])
            self.assertLessEqual(mx[2], c[2] + A["rozmiar"][1] / 2 + 1.01, x["n"])
            self.assertTrue(x["r"].startswith("Arena/"))
            self.assertIn(x.get("m", "SmoothPlastic"), ("SmoothPlastic", "Neon", "WoodPlanks", "Metal", "Slate"))

    def test_4b_nazwy_animowane_i_podpowiedzi(self):
        sciezki = {c["r"] + "/" + c["n"] for c in self.cz}
        for klucz in ("miotacz_ramie", "golem_piesc", "tablica_wyboru", "wyjscie", "beben", "palka", "kula_maga",
                      "podest_klody"):
            self.assertIn(D["nazwy"][klucz], sciezki, klucz)
        rodzice = {c["r"] for c in self.cz}
        pasy = [c for c in self.cz if c["r"] == D["nazwy"]["tasma_pasy"] and c["n"].startswith("Pas")]
        self.assertEqual(len(pasy), K["stanowiska"]["kondycja"]["pasy"])
        self.assertTrue(all(c.get("kol") is False for c in pasy), "pasy taśmy przesuwa klient — bez kolizji")
        self.assertEqual(sorted(c["n"] for c in self.cz if c["r"] == D["nazwy"]["cele_stop"]), sorted(D["gry"]["kondycja"]["akcje"]))
        ramie = [c for c in self.cz if c["r"] == D["nazwy"]["ramie_klody"]]
        self.assertTrue(ramie and all(c.get("kol") is False for c in ramie), "kłodę obraca klient — bez kolizji")
        for k in D["gry"]["inteligencja"]["runy"]:
            self.assertIn(D["nazwy"]["runy"] + "/" + k, rodzice)
            self.assertTrue([c for c in self.cz if c["r"] == D["nazwy"]["runy"] + "/" + k and c["n"].startswith("Znak")])
            self.assertIn(D["nazwy"]["runy"] + "/" + k + "/Kamien", sciezki)
        self.assertEqual(sorted(c["n"] for c in self.cz if c["r"] == D["nazwy"]["tory"]), sorted(D["gry"]["szczescie"]["tory"]))
        for n in D["nazwy"]["golem_oczy"]:
            self.assertIn(n, sciezki)
        for k in D["gry"]["sila"]["akcje"]:
            self.assertIn(D["nazwy"]["strefy"] + "/" + k, sciezki)
        for p in ZB.PODPOWIEDZI:
            if not p[0].startswith("TablicaWejscia"):
                self.assertIn(p[0], sciezki)
        self.assertEqual(D["nazwy"]["tablica_wejscia"], "TablicaWejscia/E")

    def _wolne(self, a, b, pomin=()):
        for c in self.lita:
            if c["n"] in pomin or (c["r"] + "/" + c["n"]) in pomin:
                continue
            mn, mx = _pudlo(c)
            if _odcinek_w_pudle(a, b, mn, mx):
                return c["r"] + "/" + c["n"]
        return None

    def test_4c_kamera_widzi_strefy_i_tory_lotu(self):
        W = D["swiat"]["sila"]
        oko = W["oko"]
        for k, z in W["strefy"].items():
            self.assertIsNone(self._wolne(oko, z), "kamera → strefa %s" % k)
            H = W["reka"]
            C = [(H[i] + z[i]) / 2 + W["luki"][k][i] for i in range(3)]
            pkt = []
            for j in range(0, 21):
                a = j / 20
                pkt.append([(1 - a) ** 2 * H[i] + 2 * (1 - a) * a * C[i] + a * a * z[i] for i in range(3)])
            for p, q in zip(pkt[2:], pkt[3:]):  # bez pierwszych kroków (ręka miotacza w jego bryle)
                self.assertIsNone(self._wolne(p, q, pomin=("RamieP",)), "tor %s" % k)
            self.assertGreater(min(p[1] for p in pkt), D["arena"]["srodek"][1] + 0.5, "tor %s nad podłogą" % k)
            self.assertIsNone(self._wolne(oko, H, pomin=("RamieP", "Tulow", "Glowa", "Opaska")), "kamera → miotacz")
        P = D["swiat"]["pancerz"]
        self.assertIsNone(self._wolne(P["oko"], P["piesc_cel"]), "kamera → cel pięści")
        self.assertIsNone(self._wolne(P["oko"], P["tarcza"]), "kamera → tarcza")
        for p in (P["piesc_spoczynek"], P["piesc_zamach"], P["piesc_cel"]):
            self.assertIsNone(self._wolne(p, p, pomin=("Piesc", "RamieP")), "pięść nie w bryle")

    def test_4e_kamery_nowych_stanowisk(self):
        """Z kamery każdej nowej mini-gry widać to, na co gracz reaguje (bez litej części po drodze)."""
        # Bieżnia: linia kroku i ślady od chwili pojawienia się (biegacz stoi ZA linią — twarzą do kamery)
        W = D["swiat"]["kondycja"]
        for k, p in W["stopy"].items():
            for dt in (0, W["slady_s"] / 2, W["slady_s"]):
                q = [p[0], p[1] + 0.1, p[2] + W["slad_predkosc"] * dt]
                self.assertIsNone(self._wolne(W["oko"], q, pomin=("Plyta",)), "Bieżnia: kamera → ślad %s, %.1f s" % (k, dt))
            self.assertLess(p[2] - W["podest"][2], W["oko"][2] - W["podest"][2], "linia między biegaczem a kamerą")
            ts, tr = W["tasma_srodek"], W["tasma_rozmiar"]
            self.assertLessEqual(p[2] + W["slad_predkosc"] * W["slady_s"], ts[2] + tr[2] / 2, "ślad pojawia się na taśmie")
            self.assertLess(abs(p[0] - ts[0]) + 0.5, tr[0] / 2, "tor śladu na taśmie")
        # Kłody: miejsce przejścia kłody (nisko i wysoko) i postać; ramię obraca się bez kolizji z litymi częściami
        W = D["swiat"]["zrecznosc"]
        pd, sl = W["podest"], W["slup"]
        for nazwa, h in W["wysokosci"].items():
            self.assertIsNone(self._wolne(W["oko"], [pd[0], pd[1] + h, pd[2]]), "Kłody: kamera → kłoda %s" % nazwa)
            for i in range(72):
                a = math.radians(i * 5)
                koniec = [sl[0] + math.cos(a) * (W["ramie"] + W["kloda_srednica"] / 2), pd[1] + h,
                          sl[2] + math.sin(a) * (W["ramie"] + W["kloda_srednica"] / 2)]
                ramie = tuple(c["r"] + "/" + c["n"] for c in self.cz if c["r"] == D["nazwy"]["ramie_klody"])
                self.assertIsNone(self._wolne([sl[0], pd[1] + h, sl[2]], koniec, pomin=("Pal", "Czapa", "Plac", "Podest") + ramie),
                                  "Kłody: ramię %s przy kącie %d°" % (nazwa, i * 5))
        self.assertLess(math.hypot(pd[0] - sl[0], pd[2] - sl[2]), W["ramie"] - 1, "gracz w zasięgu kłody")
        self.assertIsNone(self._wolne(W["oko"], [pd[0], pd[1] + 4.5, pd[2]]), "Kłody: kamera → głowa gracza")
        # Runy: każdy kamień ze znakiem widoczny (postać gracza półprzezroczysta — nie jest częścią sceny)
        W = D["swiat"]["inteligencja"]
        for k, p in W["kamienie"].items():
            przod = [p[0], p[1], p[2] + W["kamien_rozmiar"][2] / 2 + 0.2]
            self.assertIsNone(self._wolne(W["oko"], przod), "Runy: kamera → kamień %s" % k)
        # Koniczyny: każdy tor od chwili wypadnięcia z korony do koszyka nad głową
        W = D["swiat"]["szczescie"]
        pd = W["podest"]
        kosz = [W["koszyk"][i] - pd[i] for i in range(3)]
        for k, p in W["tory"].items():
            for y in (pd[1] + W["spad_y"], (pd[1] + W["spad_y"] + p[1] + kosz[1]) / 2, p[1] + kosz[1] + 0.6):
                self.assertIsNone(self._wolne(W["oko"], [p[0], y, p[2] + kosz[2]]), "Koniczyny: kamera → tor %s, y %.1f" % (k, y))
            self.assertIsNone(self._wolne([p[0], p[1] + 0.3, p[2]], [p[0], p[1] + 5.4, p[2]]), "Koniczyny: tor %s wolny" % k)

    def test_4d_sciany_i_podest(self):
        sciany = [c for c in self.cz if c["r"] == "Arena/Mury" and c["n"].startswith("Sciana")]
        self.assertEqual(len(sciany), 4)
        for c in sciany:
            self.assertGreaterEqual(c["s"][1], 12)
            self.assertTrue(c.get("kol", True))
        for gra in D["gry"]:
            p = D["swiat"][gra]["podest"]
            y0 = p[1] + 0.3
            if gra == "kondycja":  # biegacz stoi na taśmie
                W = D["swiat"][gra]
                y0 = W["tasma_srodek"][1] + W["tasma_rozmiar"][1] / 2 + 0.05
            self.assertIsNone(self._wolne([p[0], y0, p[2]], [p[0], p[1] + 5.5, p[2]]), "miejsce gracza wolne: %s" % gra)


# ============================================================================================== 5. telefon
def _argumenty(tekst):
    """Argumenty wywołania do nawiasu zamykającego (z zagnieżdżeniem)."""
    argi, glebokosc, biezacy = [], 0, ""
    for z in tekst:
        if z in "([{":
            glebokosc += 1
        elif z in ")]}":
            if glebokosc == 0:
                break
            glebokosc -= 1
        if z == "," and glebokosc == 0:
            argi.append(biezacy)
            biezacy = ""
        else:
            biezacy += z
    argi.append(biezacy)
    return argi


def _wartosc(arg, U):
    arg = arg.strip()
    if re.fullmatch(r"\d+(\.\d+)?", arg):
        return float(arg)
    m = re.fullmatch(r"U\.(\w+)", arg)
    if m:
        return float(U[m.group(1)])
    if arg == "b":
        return float(U["przycisk_px"])
    return None


class TestTelefonu(unittest.TestCase):
    def test_5a_rozmiary_z_danych(self):
        U = D["ui"]
        for skala in (LT.skala_ui(D, 667, 375), LT.skala_ui(D, 568, 320), U["skala_min"]):
            self.assertGreaterEqual(U["przycisk_maly_px"] * skala, U["wymog_przycisk_px"])
            self.assertGreaterEqual(min(U["tekst_px"].values()) * skala, U["wymog_tekst_pt"])
        self.assertEqual((U["wymog_przycisk_px"], U["wymog_tekst_pt"]), (44, 12))
        self.assertEqual(LT.skala_ui(D, 667, 375), 1.0)

    def test_5b_kazdy_przycisk_w_kliencie(self):
        U = D["ui"]
        kod = bez_komentarzy(KLIENT)
        wywolania = re.findall(r"\bprzycisk\(([^\n]*)", kod)
        policzone = 0
        for w in wywolania:
            if w.startswith("rodzic"):
                continue  # definicja funkcji
            argi = _argumenty(w)
            szer, wys = _wartosc(argi[5], U), _wartosc(argi[6], U)
            self.assertIsNotNone(szer, w)
            self.assertIsNotNone(wys, w)
            self.assertGreaterEqual(min(szer, wys) * U["skala_min"], U["wymog_przycisk_px"], w)
            policzone += 1
        self.assertGreaterEqual(policzone, 11)
        for rozmiar in re.findall(r'\bnapis\([^\n]*?"(maly|sredni|duzy|seria|wielki)"', kod):
            self.assertIn(rozmiar, U["tekst_px"])
        self.assertNotRegex(kod, r"TextSize\s*=\s*\d")

    def test_5c_panele_mieszcza_sie(self):
        U = D["ui"]
        # (szer, wys) bazowo — te same liczby co w KlientTreningu (panel(...)); ekran bez paska górnego Robloxa (36)
        panele = {"Wybor": (478, 304), "Podsumowanie": (400, 244), "Start": (400, 132), "Status": (268, 92)}
        for nazwa, (w, h) in panele.items():
            self.assertRegex(KLIENT, r'panel\("%s", %d, %d' % (nazwa, w, h))
        for ekran in ((667, 375), (568, 320), (812, 375)):
            s = LT.skala_ui(D, *ekran)
            for nazwa, (w, h) in panele.items():
                self.assertLessEqual(w * s, ekran[0] - 16, (nazwa, ekran))
                self.assertLessEqual(h * s, ekran[1] - 36 - 8, (nazwa, ekran))
            # prostokąty w czasie rundy (bez paska górnego): status, przycisk przerwania, sterowanie każdej gry — bez
            # nachodzenia (sterowanie różnych gier nie jest widoczne naraz; HUD jest schowany na stanowisku)
            w, h = ekran[0], ekran[1] - 36
            g = U["odstep_px"]
            krzyz = 3 * U["przycisk_px"] + 2 * g
            runy = 3 * U["runa_px"] + 2 * g
            prawa = w * (1 - U["sterowanie_od_prawej"])

            def prawy(sz, wy):
                return (prawa - sz * s, h - 8 - wy * s, prawa, h - 8)

            def lewy(sz, wy):
                return (8, h - 8 - wy * s, 8 + sz * s, h - 8)
            wspolne = {"status": (w - 8 - 268 * s, 8, w - 8, 8 + 92 * s),
                       "przerwij": (w - 16 - (268 + U["przycisk_maly_px"]) * s, 8, w - 16 - 268 * s, 8 + U["przycisk_maly_px"] * s)}
            gry = {"sila": {"krzyz": prawy(krzyz, krzyz)}, "pancerz": {"blok": prawy(U["blok_px"], U["blok_px"])},
                   "kondycja": {"stopaL": lewy(U["stopa_px"], U["stopa_px"]), "stopaP": prawy(U["stopa_px"], U["stopa_px"])},
                   "zrecznosc": {"unik": prawy(U["unik_px"], 2 * U["unik_px"] + 2 * g)},
                   "inteligencja": {"runy": prawy(runy, runy), "postep": (8, 8, 8 + 216 * s, 8 + 30 * s)},
                   "szczescie": {"torL": lewy(U["tor_px"], U["tor_px"]), "torP": prawy(U["tor_px"], U["tor_px"])}}
            for gra, wlasne in gry.items():
                pr = dict(wspolne, **wlasne)
                for a in pr:
                    x0, y0, x1, y1 = pr[a]
                    self.assertTrue(x0 >= 0 and y0 >= 0 and x1 <= w and y1 <= h, (gra, a, ekran))
                    for b2 in pr:
                        if a < b2:
                            X0, Y0, X1, Y1 = pr[b2]
                            self.assertTrue(x1 <= X0 or X1 <= x0 or y1 <= Y0 or Y1 <= y0, (gra, a, b2, ekran))
                # przyciski w zasięgu kciuka: dolna połowa ekranu
                for a, (x0, y0, x1, y1) in wlasne.items():
                    if a != "postep":
                        self.assertGreater(y0, h * 0.25, (gra, a, ekran))
            # na stanowisku (przed rundą i w odliczaniu): podpowiedź obrazkowa nad panelem startu, pod statusem
            ob = U["obrazek_px"]
            start = (w / 2 - 200 * s, h - 8 - 132 * s, w / 2 + 200 * s, h - 8)
            obrazek = (w / 2 - ob[0] / 2 * s, start[1] - 8 * s - ob[1] * s, w / 2 + ob[0] / 2 * s, start[1] - 8 * s)
            for nazwa, (X0, Y0, X1, Y1) in (("status", wspolne["status"]), ("start", start)):
                x0, y0, x1, y1 = obrazek
                self.assertTrue(x1 <= X0 or X1 <= x0 or y1 <= Y0 or Y1 <= y0, ("obrazek", nazwa, ekran))
            self.assertGreaterEqual(obrazek[1], 0)
        self.assertIn("-8 - (ui.status.Size.X.Offset + 8) * s", KLIENT)
        self.assertIn("-8 - (ui.start.Size.Y.Offset + 8) * s", KLIENT)
        self.assertIn("and not stan.przedStartem", KLIENT, "przyciski gry schowane w odliczaniu (tam jest podpowiedź)")

    def test_5d_teksty_dla_gracza(self):
        # wybór jest dalej tymczasowy (WyborTymczasowy / WybierzGre dla okna Pawła), ale na ekranie gracza nie ma
        # napisów dla twórców (raport przejścia gry 17.11.2026: „Docelowe okno 2D robi Paweł (D-093)”, „bez zapisu”)
        T = D["teksty"]
        self.assertIn("w projekcie", T["w_projekcie"])
        self.assertIn("WyborTymczasowy", KLIENT)
        self.assertIn("WybierzGre", KLIENT)
        tworcy = re.compile(r"D-0\d\d|Paweł|TYMCZASOW|\(próba\)|bez zapisu|atrybut|PlayerStatsDefaults", re.I)
        def plaskie(v):
            if isinstance(v, dict):
                for x in v.values():
                    yield from plaskie(x)
            elif isinstance(v, list):
                for x in v:
                    yield from plaskie(x)
            else:
                yield v
        for klucz, tekst in T.items():
            for t in plaskie(tekst):
                self.assertIsNone(tworcy.search(t), (klucz, t))
        napisy = re.findall(r'string\.format\("([^"]*)"', bez_komentarzy(KLIENT))
        for t in napisy:
            self.assertIsNone(tworcy.search(t), t)
        for p in ZB.PODPOWIEDZI:
            self.assertIsNone(tworcy.search(p[4]), p)
        self.assertIn("schowajInneEkrany()", KLIENT)
        self.assertIn("przywrocInneEkrany()", KLIENT)


# ============================================================================================== 6. styki
class TestStykow(unittest.TestCase):
    def test_6a_wiadomosci_zdalne(self):
        s, k = bez_komentarzy(SERWER), bez_komentarzy(KLIENT)
        do_serwera = set(re.findall(r'FireServer\(\s*"(\w+)"', k))
        obsluga_serwera = set(re.findall(r'rodzaj == "(\w+)"', s))
        self.assertEqual(do_serwera - obsluga_serwera, set())
        self.assertEqual(do_serwera, {"akcja", "wejdz", "start", "przerwij", "wyjdz"})
        do_klienta = set(re.findall(r'FireClient\(\s*\w+,\s*"(\w+)"', s))
        obsluga_klienta = set(re.findall(r'rodzaj == "(\w+)"', k))
        self.assertEqual(do_klienta - obsluga_klienta, set())
        self.assertEqual(do_klienta, {"odmowa", "koniec", "wynik", "przybycie", "runda", "wyjscie", "wybor"})

    def test_6b_nazwy_instancji(self):
        tworzone = set(ZB.FOLDERY) | {p.split("/")[-1] for _, p in ZB.INNE} | {p.split("/")[-1] for _, _, p, _ in ZB.SKRYPTY}
        for tekst in (SERWER, KLIENT):
            for n in re.findall(r'WaitForChild\("(\w+)"\)', tekst):
                if n != "PlayerGui":
                    self.assertIn(n, tworzone)
        for tekst in (ZB.kod_areny(D), ZB.kod_tablicy(D)):
            self.assertIn('ModelStreamingMode.Persistent', tekst)

    def test_6c_atrybuty_gracza_tylko_sesyjne(self):
        s = bez_komentarzy(SERWER)
        ustawiane = set(re.findall(r'gracz:SetAttribute\(\s*("?[\w.]+"?)', s))
        self.assertEqual(ustawiane, {"st.atrybut_sesji", '"TreningGra"', '"TreningSeria"'})
        for st in D["statystyki"]:
            self.assertNotIn('"%s"' % st["atrybut"], s)
        self.assertNotIn("DataStore", s + KLIENT + LOGIKA)
        self.assertIn("przyrostE:Fire(", s)

    def test_6d_zakazy_i_dzwieki(self):
        pliki = [os.path.join(PAKIET, n) for n in ("dane.py", "scena.py", "zbuduj.py", "logika_treningu.py")]
        for plik in pliki + glob.glob(os.path.join(ZR, "*.luau")):
            tekst = czytaj(plik)
            if plik.endswith(".luau"):
                tekst = bez_komentarzy(tekst)
            if os.path.basename(plik) == SLT.ADRES_ARKUSZA_PLIK:
                # jedyny wyjątek: adres arkusza efektów z identyfikatora w katalogu swiat/dzwiek_gra (żadnej liczby w kodzie)
                self.assertEqual(tekst.count(SLT.ADRES_ARKUSZA), 1)
                tekst = tekst.replace(SLT.ADRES_ARKUSZA, "")
                self.assertIn("kat.arkusz.id", tekst)
            for z in ("rbxassetid://", "InsertService", "Lighting.", 'GetService("Lighting")', "MarketplaceService"):
                self.assertNotIn(z, tekst, "%s: %s" % (os.path.basename(plik), z))
        # zdarzenia arkusza z pakietu dźwięku (tylko istniejące) i dźwięk wbudowany, gdy arkusza nie ma
        znane = DANE.zdarzenia_dzwieku()
        DK = D["dzwieki_katalog"]
        for z in list(DK["trafienie"].values()) + [DK[k] for k in ("punkt", "koniec", "zlota", "zaklecie", "przycisk")]:
            self.assertIn(z, znane)
        self.assertEqual(DK["kontener"], "DzwiekGra")
        self.assertIn("if not grajZdarzenie(", KLIENT)
        self.assertEqual(len(re.findall(r"grajZdarzenie\(DK\.(\w+)\)", KLIENT)) >= 5, True)
        for n, d in D["dzwieki"].items():
            if isinstance(d, dict):
                self.assertIn(d["plik"], DANE.DZWIEKI_WBUDOWANE, n)
        walka = czytaj(REPO, "swiat", "test_walki2", "zrodla", "Ustawienia.luau")
        for plik in DANE.DZWIEKI_WBUDOWANE:
            self.assertIn(plik.split(".")[0], walka)
        self.assertIn('"rbxasset://sounds/" .. d.plik', KLIENT)

    def test_6e_place_id_punkty_historii_sucho(self):
        sys.path.insert(0, os.path.join(REPO, "swiat", "test_walki_roblox"))
        import cel_studio  # noqa: E402
        self.assertEqual(cel_studio.MIEJSCE, ZB.MIEJSCE)
        self.assertEqual(ZB.START.count("SetWaypoint"), 3)  # przed usunięciem, usunięto, przed budową
        self.assertEqual(ZB.KONIEC.count("SetWaypoint"), 1)
        for kod in ZB.wszystkie_kody(D).values():
            self.assertNotIn("Lighting", kod)
        r = subprocess.run([sys.executable, "-B", os.path.join(PAKIET, "zbuduj.py"), "--sucho"], capture_output=True)
        out = r.stdout.decode("utf-8", "replace")
        self.assertEqual(r.returncode, 0, out + r.stderr.decode("utf-8", "replace"))
        self.assertIn("sucho: OK", out)
        r = subprocess.run([sys.executable, "-B", "-c", "import sys; sys.path.insert(0, %r); import zbuduj; "
                            "print('studio_mcp' in sys.modules, 'cel_studio' in sys.modules)" % PAKIET], capture_output=True)
        self.assertEqual(r.stdout.decode().strip(), "False False")

    def test_6f_proba_play(self):
        plik = os.path.join(TU, "proba_play.py")
        py_compile.compile(plik, doraise=True, cfile=os.path.join(tempfile.gettempdir(), "proba_play_trening.pyc"))
        tekst = czytaj(plik)
        for i in range(1, 23):
            self.assertIn("T%02d" % i, tekst)
        r = subprocess.run([sys.executable, "-B", plik], capture_output=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("LISTA KONTROLNA", r.stderr.decode("utf-8", "replace") + r.stdout.decode("utf-8", "replace"))
        # --sprawdz: każdy kawałek Luau próby parsuje się w luau_mini (bez Studio)
        r = subprocess.run([sys.executable, "-B", plik, "--sprawdz"], capture_output=True)
        out = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
        self.assertEqual(r.returncode, 0, out)
        self.assertIn("OK", out)
        for g in ("kondycja", "zrecznosc", "inteligencja", "szczescie"):
            self.assertIn('"%s"' % g, tekst)
        z = os.path.join(TU, "zrzuty_gry.py")
        py_compile.compile(z, doraise=True, cfile=os.path.join(tempfile.gettempdir(), "zrzuty_gry_trening.pyc"))
        r = subprocess.run([sys.executable, "-B", z, "--sprawdz"], capture_output=True)
        self.assertEqual(r.returncode, 0, r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace"))

    def test_6h_podglad_stanowisk(self):
        """podglad.py (render brył bez Studio) importuje się bez numpy na starcie i zna sześć gier i widok areny."""
        tekst = czytaj(PAKIET, "podglad.py")
        self.assertNotIn("studio_mcp", tekst)
        for g in GRY:
            self.assertIn('"%s"' % g, tekst)
        r = subprocess.run([sys.executable, "-B", "-c", "import sys; sys.path.insert(0, %r); import podglad; "
                            "print('numpy' in sys.modules)" % PAKIET], capture_output=True)
        self.assertEqual(r.stdout.decode().strip(), "False", r.stderr.decode("utf-8", "replace"))

    def test_6g_straznik_i_samousuniecie(self):
        for plik in glob.glob(os.path.join(ZR, "*.luau")):
            self.assertTrue(SLT.SL.pierwsza_instrukcja(czytaj(plik)).startswith(ZB.STRAZNIK), plik)
        self.assertIn("script.Parent:Destroy()", SERWER.split("IsStudio()")[1][:80])
        self.assertIn("OknoMiejsca", KLIENT)
        self.assertIn("D.id_miejsca_bazaru", KLIENT)


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    unittest.main(verbosity=1)
