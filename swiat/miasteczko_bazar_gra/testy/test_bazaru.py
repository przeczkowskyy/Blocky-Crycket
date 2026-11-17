# -*- coding: utf-8 -*-
"""Testy offline pakietu swiat/miasteczko_bazar_gra („miasteczko-bazar w grze”). Bez Studio, bez sieci.

    python -B swiat/miasteczko_bazar_gra/testy/test_bazaru.py        (unittest; kod 1 przy błędzie)

1. Dane: dane.py deterministyczny i aktualny, bez dat i ścieżek lokalnych; błędne ustawienia → BladDanych;
   przesunięcie starego miasteczka zgodne z jego README; przyciski HUD zgodne z src/gui/HUD.model.json.
2. Znaczniki: każdy punkt z podpowiedzią ze swiat/miasteczko_bazar/znaczniki.json ma E (albo jest na liście
   „pominiete” z powodem), położenia 1:1 ze znaczników, identyfikatory unikalne, wszystkie okna z zadania; ze stoiska
   widać tylko własną podpowiedź; przejście „Stare miasteczko” na wolnym miejscu siatki, poza zasięgiem ze startu;
   tablica na powierzchni ze znacznika; czasy biegu planu w celach; żadnych liczb położeń w kodzie.
3. Logika (lustro w Pythonie): akcje wszystkich miejsc, odległość, spam, lochy (flaga, poziom), chmury, Las,
   blokada czasu (symulacja 400 przebiegów), odmowy uchwytu Lasu, ranking, kandydaci w starym miasteczku, dymek.
4. Luau w luau_mini (tools/walka/luau_mini.py, gdy jest): pliki parsują się; przypadki wzorcowe OK; losowe
   wywołania dają to samo co lustro; DaneBazaru w Luau = dane z Pythona; kod wysyłany do Studio parsuje się.
5. Punkty styku (czytane jak tekst): nazwy instancji, wiadomości zdalne, atrybuty, uchwyty LasPasGra i TeleportChmury,
   sygnał HUD, uchwyt startu dla przejścia przez chmury, strażnik Studio i PlaceId, punkty historii, bez Lighting,
   bez ścieżek lokalnych; zbuduj.py --sucho (bez importu studio_mcp); proba_play.py się kompiluje.
"""
import copy
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

import importlib.util  # noqa: E402


def _modul(nazwa, plik):
    """Moduł pakietu z jego pliku (w repo jest kilka zbuduj.py — nie polegamy na kolejności sys.path)."""
    spec = importlib.util.spec_from_file_location(nazwa, os.path.join(PAKIET, plik))
    m = importlib.util.module_from_spec(spec)
    sys.modules[nazwa] = m
    spec.loader.exec_module(m)
    return m


LB = _modul("logika_bazaru", "logika_bazaru.py")
DANE = _modul("dane", "dane.py")
SLB = _modul("sprawdz_luau_bazaru", "sprawdz_luau_bazaru.py")
ZB = _modul("zbuduj_bazaru", "zbuduj.py")
czasy_biegu = _modul("czasy_biegu", "czasy_biegu.py")

K, ZN, D = DANE.dane_z_przypadkami()
M = D["miejsca"]
ZR = os.path.join(PAKIET, "zrodla")
LM = SLB.luau_mini()


def czytaj(*czesci):
    with open(os.path.join(*czesci), encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


SERWER = czytaj(ZR, "SerwerBazaru.server.luau")
KLIENT = czytaj(ZR, "KlientBazaru.client.luau")
LOGIKA = czytaj(ZR, "LogikaBazaru.luau")


def bez_komentarzy(tekst):
    return SLB.SL.rozbierz(tekst)[0]


def napisy(tekst, metoda):
    """Napisy-argumenty wywołań metoda("…") — tylko całe literały (bez "W" .. i)."""
    return set(re.findall(r'%s\(\s*"([^"]+)"\s*[,)]' % metoda, bez_komentarzy(tekst)))


def odl(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def luau_modul(plik):
    it = LM.Interpreter()
    rs = LM.Tabela()
    rs.set("IsStudio", lambda _self: True)
    game = LM.Tabela()
    game.set("GetService", lambda _self, _n: rs)
    it.globalne.z["game"] = game
    return it, it.wykonaj(czytaj(ZR, plik), plik)[0]


def do_luau(a):
    if isinstance(a, (dict, list)):
        return LM.do_luau(a)
    if isinstance(a, (int, float)) and not isinstance(a, bool):
        return float(a)
    return a


def wolaj(it, modul, nazwa, *argi):
    return it.wywolaj(modul.get(nazwa), [do_luau(a) for a in argi])


def norm(v):
    """Do porównań Luau ↔ Python: liczby zaokrąglone, puste kontenery jednakowe."""
    if isinstance(v, dict):
        return {k: norm(x) for k, x in v.items()} if v else "pusty"
    if isinstance(v, list):
        return [norm(x) for x in v] if v else "pusty"
    if isinstance(v, bool) or v is None or isinstance(v, str):
        return v
    return round(float(v), 6)


# ============================================================================================== 1. dane
class TestDanych(unittest.TestCase):
    def test_1a_generator_deterministyczny_i_aktualny(self):
        skrypt = os.path.join(PAKIET, "dane.py")
        tresci = []
        with tempfile.TemporaryDirectory() as tmp:
            for nr in (1, 2):
                folder = os.path.join(tmp, str(nr))
                r = subprocess.run([sys.executable, "-B", skrypt, "--wyjscie", folder], capture_output=True)
                self.assertEqual(r.returncode, 0, r.stdout.decode("utf-8", "replace"))
                with open(os.path.join(folder, DANE.PLIK_LUAU), "rb") as f:
                    tresci.append(f.read())
        self.assertEqual(tresci[0], tresci[1])
        r = subprocess.run([sys.executable, "-B", skrypt, "--sprawdz"], capture_output=True)
        self.assertEqual(r.returncode, 0, r.stdout.decode("utf-8", "replace"))
        tekst = tresci[0].decode("utf-8")
        self.assertFalse(tresci[0].startswith(b"\xef\xbb\xbf"), "BOM")
        self.assertNotIn("\r", tekst)
        self.assertIsNone(re.search(r"\b20\d\d-\d\d-\d\d\b", tekst), "data w pliku")
        self.assertIsNone(re.search(r"[A-Za-z]:\\|/Users/|/home/", tekst), "ścieżka lokalna")
        self.assertIn('skrot = "%s"' % D["skrot"], tekst)
        self.assertTrue(SLB.SL.pierwsza_instrukcja(tekst).startswith(SLB.SL.STRAZNIK))
        with open(os.path.join(ZR, DANE.PLIK_LUAU), "rb") as f:
            self.assertEqual(f.read(), tresci[0], "zrodla/DaneBazaru.luau ≠ świeżo wygenerowany")

    def test_1b_bledne_ustawienia_to_blad(self):
        def z_konfiguracja(zmien):
            k = copy.deepcopy(K)
            zmien(k)
            with tempfile.TemporaryDirectory() as tmp:
                sciezka = os.path.join(tmp, "miejsca.json")
                with open(sciezka, "w", encoding="utf-8") as f:
                    json.dump(k, f, ensure_ascii=False)
                stary = DANE.KONFIG
                DANE.KONFIG = sciezka
                try:
                    DANE.wszystko()
                finally:
                    DANE.KONFIG = stary

        def zly_znacznik(k):
            k["miejsca"][0]["znacznik"] = "sklepy/nie_ma_takiego"

        def powtorzone(k):
            k["miejsca"][1]["id"] = k["miejsca"][0]["id"]

        def zly_hud(k):
            k["miejsca"][0]["hud"] = "Sklepik"

        def zla_blokada(k):
            k["lochy"]["blokada"] = "Workspace/MiasteczkoBazar/Inna/Blokada"

        for zmien in (zly_znacznik, powtorzone, zly_hud, zla_blokada):
            with self.subTest(zmiana=zmien.__name__):
                with self.assertRaises(DANE.BladDanych):
                    z_konfiguracja(zmien)

    def test_1c_przesuniecie_starego_miasteczka_z_jego_dokumentacji(self):
        readme = czytaj(REPO, "swiat", "krzywe_miasteczko", "README.md")
        m = re.search(r"--przesun\s+(-?[\d.]+),(-?[\d.]+),(-?[\d.]+)", readme)
        self.assertIsNotNone(m)
        self.assertEqual([float(x) for x in m.groups()], [float(x) for x in K["stare_miasteczko"]["przesuniecie"]])
        uk = json.loads(czytaj(REPO, "swiat", "krzywe_miasteczko", "uklad.json"))
        self.assertEqual(D["stare"]["znacznik"], [uk["spawn"][0], 0.0, uk["spawn"][1] - 700.0])
        # kierunki: pierwszy = patrzenie + 45°, wszystkie jednostkowe i różne
        for k in D["stare"]["kierunki"]:
            self.assertAlmostEqual(k[0] ** 2 + k[1] ** 2, 1.0, delta=1e-5)
        self.assertEqual(len({tuple(k) for k in D["stare"]["kierunki"]}), len(D["stare"]["kierunki"]))
        a = math.radians(uk["patrz"] + 45)
        self.assertAlmostEqual(D["stare"]["kierunki"][0][0], math.sin(a), delta=1e-6)

    def test_1d_przyciski_hud_jak_w_gui_pawla(self):
        hud = json.loads(czytaj(REPO, "src", "gui", "HUD.model.json"))
        przyciski = set()

        def chodz(w):
            if w.get("ClassName") == "ImageButton":
                przyciski.add(w.get("Name"))
            for c in w.get("Children", []):
                chodz(c)
        chodz(hud)
        self.assertEqual(przyciski, set(K["przyciski_hud"]))
        for mid in D["kolejnosc"]:
            if M[mid].get("hud"):
                self.assertIn(M[mid]["hud"], przyciski, mid)


# ============================================================================================== 2. znaczniki
class TestZnacznikow(unittest.TestCase):
    def test_2a_kazdy_punkt_z_podpowiedzia_ma_E_albo_powod(self):
        uzyte = {M[m]["znacznik_id"] for m in M if M[m].get("znacznik_id")}
        z_podpowiedzia = {z["id"] for z in ZN["wszystkie"] if "podpowiedz" in z}
        pominiete = set(K["pominiete"])
        self.assertEqual(sorted(z_podpowiedzia - uzyte - pominiete), [], "punkt E bez podpowiedzi i bez powodu")
        self.assertEqual(sorted(uzyte), sorted({"karczma", "mistrz_gier", "sklep_magiczny", "zbrojownia", "training_center",
                                                "zagroda_petow", "tablica", "brama_twierdzy", "brama_lochow",
                                                "portal_krain", "brama_lesna"}))
        # każdy znacznik jest użyty, pominięty z powodem albo jest wejściem do budynku
        rozliczone = uzyte | {"start", "tablica_ranking", "lochy_klodka"}
        for z in ZN["wszystkie"]:
            with self.subTest(znacznik=z["id"]):
                ok = (z["id"] in rozliczone or z["id"] in pominiete or z["typ"] == "wejscie"
                      or (z["typ"] == "miejsce_peta" and "zagroda_miejsce_1..6" in pominiete))
                self.assertTrue(ok)

    def test_2b_polozenia_jeden_do_jednego_ze_znacznikow(self):
        for mid in D["kolejnosc"]:
            m = M[mid]
            if not m.get("znacznik") or m["znacznik"] == "start":
                continue
            z = DANE.znajdz(ZN, m["znacznik"])
            with self.subTest(miejsce=mid):
                self.assertEqual(m["punkt"], [float(x) for x in z["podpowiedz"]])
                self.assertEqual(m["stoisko"], [float(x) for x in z["stoisko"]])
                if z.get("czesc_podpowiedzi"):
                    self.assertEqual(m["czesc_mapy"], z["grupa_zaczepu"] + "/" + z["czesc_podpowiedzi"])
                if z.get("model"):
                    self.assertEqual(m["model"], z["model"])
        st = ZN["start"]
        self.assertEqual(D["start"]["punkt"], [float(x) for x in st["swiat"]])
        self.assertEqual(M["stare_miasteczko"]["stoisko"],
                         [st["swiat"][i] + K["miejsca"][[x["id"] for x in K["miejsca"]].index("stare_miasteczko")]["od_startu_bazar"][i]
                          for i in range(3)])

    def test_2c_identyfikatory_unikalne_i_wszystkie_okna(self):
        self.assertEqual(len(D["kolejnosc"]), len(set(D["kolejnosc"])))
        self.assertEqual(len(D["kolejnosc"]), 13)
        okna = {mid for mid in M if M[mid]["akcja"] in ("okno", "lochy")}
        self.assertEqual(okna, {"karczma", "mistrz_gier", "sklep_magiczny", "zbrojownia", "training_center",
                                "zagroda_petow", "tablica", "dzialka", "lochy"})
        self.assertEqual({mid for mid in M if M[mid]["akcja"] == "chmury"}, {"portal_krain"})
        self.assertEqual({mid for mid in M if M[mid]["akcja"] == "las"}, {"brama_lesna"})
        self.assertEqual({mid: M[mid].get("cel") for mid in M if M[mid]["akcja"] == "przenies"},
                         {"stare_miasteczko": "stare", "nowe_miasteczko": "bazar"})
        for mid in M:
            self.assertRegex(mid, r"^[a-z_]+$")

    def test_2d_ze_stoiska_widac_tylko_wlasna_podpowiedz(self):
        h = D["podpowiedz"]["wysokosc_korzenia"]
        ids = [i for i in D["kolejnosc"] if M[i].get("stoisko")]
        for a in ids:
            s = M[a]["stoisko"]
            korzen = [s[0], s[1] + h, s[2]]
            with self.subTest(miejsce=a):
                self.assertLessEqual(odl(korzen, M[a]["punkt"]), M[a]["zasieg"] - 1)
                for b in ids:
                    if b != a:
                        self.assertGreater(odl(korzen, M[b]["punkt"]), M[b]["zasieg"], "%s widzi E %s" % (a, b))

    def test_2e_przejscie_stare_miasteczko_w_bazarze(self):
        m = M["stare_miasteczko"]
        B = D["bazar"]
        self.assertTrue(B["pole_x"][0] + 2 < m["stoisko"][0] < B["pole_x"][1] - 2)
        self.assertTrue(B["pole_z"][0] + 2 < m["stoisko"][2] < B["pole_z"][1] - 2)
        # gracz, który przyszedł ze starego miasteczka, nie stoi od razu w zasięgu powrotu
        self.assertGreater(odl(D["start"]["korzen"], m["punkt"]), m["zasieg"])
        wolne = czasy_biegu.wolne_w_siatce(m["stoisko"][0], m["stoisko"][2])
        if wolne is None:
            self.skipTest("brak numpy/Pillow — siatka chodzenia mapy niedostępna")
        self.assertTrue(wolne, "punkt „Stare miasteczko” w przeszkodzie siatki")

    def test_2f_tablica_na_powierzchni_ze_znacznika(self):
        T = D["tablica"]
        z = DANE.znajdz(ZN, K["tablica"]["znacznik"])
        self.assertEqual(T["srodek"], [float(x) for x in z["swiat"]])
        self.assertEqual(T["rozmiar"], [float(x) for x in z["rozmiar"]])
        self.assertAlmostEqual(sum(x * x for x in T["normalna"]), 1.0, delta=1e-3)
        self.assertGreater(T["odsuniecie"], T["grubosc"] / 2, "płytka wchodziłaby w deskę mapy")
        self.assertLess(odl(T["srodek"], M["tablica"]["punkt"]), 3, "E tablicy daleko od powierzchni")
        self.assertIn("SurfaceGui", ZB.CZESCI)
        self.assertIn("CFrame.lookAt(poz, poz + nrm)", ZB.CZESCI)
        self.assertIn("Enum.NormalId.Front", ZB.CZESCI)

    def test_2g_czasy_biegu_planu_w_celach(self):
        p = czasy_biegu.plan(D)
        if p is None:
            self.skipTest("brak numpy/Pillow — siatka chodzenia mapy niedostępna")
        self.assertEqual(set(p), {i for i in D["kolejnosc"] if M[i].get("stoisko")})
        for mid, w in p.items():
            with self.subTest(miejsce=mid):
                self.assertIsNotNone(w["czas"], "nieosiągalny ze startu")
                if w["cel"] is not None:
                    self.assertLessEqual(w["czas"], w["cel"])

    def test_2h_bez_liczb_polozen_w_kodzie(self):
        for nazwa, kod in (("SPRAWDZ", ZB.SPRAWDZ), ("START", ZB.START), ("PUNKT", ZB.PUNKT), ("CZESCI", ZB.CZESCI),
                           ("STARE", ZB.STARE), ("KONIEC", ZB.KONIEC)):
            with self.subTest(kod=nazwa):
                bez = SLB.SL.rozbierz(kod)[1]
                duze = [x for x in re.findall(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])", bez) if float(x) >= 100]
                self.assertEqual(duze, [])
        bledy, _ = SLB.sprawdz_pliki(SLB.pliki_pakietu(), wypisz=lambda *_: None)
        self.assertEqual([b for b in bledy if "liczba" in b], [])


# ============================================================================================== 3. logika
def swiat(**kw):
    w = {"odleglosc": 5, "chmury": True, "las": True, "poziom": 1, "cel": True}
    for k, v in kw.items():
        if v is None:
            w.pop(k, None)
        else:
            w[k] = v
    return w


class TestLogiki(unittest.TestCase):
    def test_3a_akcje_wszystkich_miejsc(self):
        oczekiwane = {"okno": "okno", "lochy": "dymek", "chmury": "chmury", "las": "las", "przenies": "przenies"}
        for mid in D["kolejnosc"]:
            w = LB.decyzja(D, mid, LB.nowy_stan(), 10.0, swiat())
            with self.subTest(miejsce=mid):
                self.assertEqual(w["akcja"], oczekiwane[M[mid]["akcja"]])
                self.assertEqual(w["id"], mid)
        self.assertEqual(LB.decyzja(D, "lochy", LB.nowy_stan(), 10.0, swiat())["tekst"], "Zamknięte")
        self.assertEqual(M["dzialka"]["dymek"], "Działka — wkrótce")
        self.assertEqual(M["zbrojownia"]["dymek"], "Zbrojmistrz: sklep w budowie")

    def test_3b_odleglosc_i_spam(self):
        z = M["zbrojownia"]["zasieg"] + D["podpowiedz"]["zapas"]
        self.assertEqual(LB.decyzja(D, "zbrojownia", LB.nowy_stan(), 10.0, swiat(odleglosc=z + 0.01))["powod"], "za_daleko")
        self.assertEqual(LB.decyzja(D, "zbrojownia", LB.nowy_stan(), 10.0, swiat(odleglosc=z))["akcja"], "okno")
        self.assertEqual(LB.decyzja(D, "zbrojownia", LB.nowy_stan(), 10.0, swiat(odleglosc=None))["akcja"], "okno")
        s = LB.nowy_stan()
        self.assertEqual(LB.decyzja(D, "karczma", s, 10.0, swiat())["akcja"], "okno")
        self.assertEqual(LB.decyzja(D, "karczma", s, 10.0 + D["czasy"]["odstep_e_s"] / 2, swiat())["powod"], "spam")
        self.assertEqual(LB.decyzja(D, "karczma", s, 10.0 + D["czasy"]["odstep_e_s"], swiat())["akcja"], "okno")
        # odrzucone E (za daleko) nie zabiera odstępu
        s = LB.nowy_stan()
        LB.decyzja(D, "karczma", s, 10.0, swiat(odleglosc=99))
        self.assertEqual(s["ostatnieE"], LB.NIGDY)
        self.assertEqual(LB.decyzja(D, "nie_ma", LB.nowy_stan(), 1.0, swiat())["powod"], "nieznane_miejsce")

    def test_3c_lochy_osobno_dla_gracza(self):
        s = LB.nowy_stan()
        self.assertEqual(LB.decyzja(D, "lochy", s, 10.0, swiat(poziom=500))["akcja"], "dymek", "bez progu poziom nie otwiera")
        s2 = LB.nowy_stan()
        s2["lochy"] = True
        self.assertEqual(LB.decyzja(D, "lochy", s2, 10.0, swiat())["akcja"], "okno")
        D2 = copy.deepcopy(D)
        D2["lochy"]["wymagany_poziom"] = 8
        for poziom, otwarte in ((7, False), (8, True), (50, True), (None, False), ("8", False), (True, False)):
            with self.subTest(poziom=poziom):
                self.assertEqual(LB.lochy_otwarte(D2, LB.nowy_stan(), poziom), otwarte)
        self.assertIsNone(K["lochy"]["wymagany_poziom"], "poziom lochów nie jest ustalony — tylko haczyk")

    def test_3d_portal_i_brama_lesna_bez_celu(self):
        w = LB.decyzja(D, "portal_krain", LB.nowy_stan(), 10.0, swiat(chmury=False))
        self.assertEqual((w["akcja"], w["powod"], w["tekst"]), ("dymek", "brak_chmur", M["portal_krain"]["dymek"]))
        w = LB.decyzja(D, "brama_lesna", LB.nowy_stan(), 10.0, swiat(las=False))
        self.assertEqual((w["akcja"], w["powod"]), ("dymek", "brak_lasu"))
        self.assertIn("Las", w["tekst"])
        w = LB.decyzja(D, "stare_miasteczko", LB.nowy_stan(), 10.0, swiat(cel=False))
        self.assertEqual(w["powod"], "brak_celu")

    def test_3e_odmowy_uchwytu_lasu_maja_tekst(self):
        serwer_pasa = bez_komentarzy(czytaj(REPO, "swiat", "las_pas_gra", "zrodla", "SerwerPasa.server.luau"))
        cialo = serwer_pasa.split("local function przeniesDoLasu", 1)[1].split("przeniesF.OnInvoke", 1)[0]
        powody = set(re.findall(r'powod = "(\w+)"', cialo))
        przenies = serwer_pasa.split("local function przenies(", 1)[1].split("\nend\n", 1)[0]
        powody |= set(re.findall(r'return false, "(\w+)"', przenies))
        self.assertTrue({"brak_mapy", "za_szybko", "brak_postaci"} <= powody, powody)
        self.assertEqual(sorted(powody - set(D["teksty"])), [])
        for p in powody | {"trwa", "brak_lasu", "brak_celu", "blad"}:
            self.assertTrue(LB.tekst_odmowy(D, p, 1.2))
        self.assertEqual(LB.tekst_odmowy(D, "cos_nowego"), D["teksty"]["blad"])
        self.assertEqual(LB.tekst_odmowy(D, "za_szybko", 2.2), "Chwila… jeszcze 3 s")
        self.assertEqual(LB.tekst_odmowy(D, "za_szybko", 0.01), "Chwila… jeszcze 1 s")
        self.assertEqual(LB.tekst_odmowy(D, "za_szybko", 0), "Chwila… jeszcze 1 s")

    def test_3f_blokada_czasu_symulacja(self):
        """400 losowych przebiegów: E co chwila w trzech przejściach; przejście trwa losowo i czasem się nie udaje.
        Nigdy dwa przejścia naraz, a między udanym końcem a kolejnym startem ≥ odstep_przejsc_s."""
        rnd = random.Random(7)
        odstep = D["czasy"]["odstep_przejsc_s"]
        for _ in range(400):
            s = LB.nowy_stan()
            t, koniec_przejscia, ostatni_udany = 0.0, None, None
            for _ in range(rnd.randint(5, 40)):
                t += rnd.choice([0.1, 0.3, 0.5, 1.0, 2.0, 3.5])
                if koniec_przejscia is not None and t >= koniec_przejscia[0]:
                    LB.koniec_przejscia(s, koniec_przejscia[1], koniec_przejscia[0])
                    if koniec_przejscia[1]:
                        ostatni_udany = koniec_przejscia[0]
                    koniec_przejscia = None
                mid = rnd.choice(["brama_lesna", "stare_miasteczko", "nowe_miasteczko", "zbrojownia"])
                w = LB.decyzja(D, mid, s, t, swiat())
                if w["akcja"] in ("las", "przenies"):
                    self.assertIsNone(koniec_przejscia, "dwa przejścia naraz")
                    if ostatni_udany is not None:
                        self.assertGreaterEqual(t - ostatni_udany, odstep - 1e-9)
                    LB.poczatek_przejscia(s)
                    koniec_przejscia = (t + rnd.choice([0.05, 0.4, 1.2, 4.0]), rnd.random() < 0.8)
                elif w["akcja"] == "dymek":
                    self.assertIn(w["powod"], ("trwa", "za_szybko"))

    def test_3g_ranking(self):
        rnd = random.Random(5)
        for _ in range(200):
            gracze = []
            for i in range(rnd.randint(0, 14)):
                g = {"nazwa": "Gracz%02d" % rnd.randint(0, 99) + str(i)}
                if rnd.random() < 0.85:
                    g["poziom"] = rnd.randint(0, 12)
                if rnd.random() < 0.8:
                    g["xp"] = rnd.choice([0, 10, 40, 99])
                if rnd.random() < 0.8:
                    g["moc"] = rnd.choice([10, 130, 131.5])
                gracze.append(g)
            n = rnd.choice([0, 3, 8])
            w = LB.ranking(gracze, n)
            self.assertEqual(len(w), min(n, len(gracze)))
            self.assertEqual([x["miejsce"] for x in w], list(range(1, len(w) + 1)))
            klucz = [(-(g.get("poziom") if g.get("poziom") is not None else -1), -(g.get("xp") or 0),
                      -(g.get("moc") or 0), g["nazwa"]) for g in gracze]
            pelny = LB.ranking(gracze, 99)
            self.assertEqual([x["nazwa"] for x in pelny], [gracze[i]["nazwa"] for i in sorted(range(len(gracze)), key=lambda i: klucz[i])])
        self.assertEqual(LB.wiersz({"miejsce": 1, "nazwa": "Ala", "poziom": 3, "moc": 130}), "1. Ala — poz. 3 · moc 130")
        self.assertEqual(LB.wiersz({"miejsce": 2, "nazwa": "Duch"}), "2. Duch — poz. — · moc —")
        self.assertEqual(LB.liczba(131.5), "131.5")
        # tablica czyta prawdziwe atrybuty gracza z src/ (PlayerStatsDefaults — placeholder do czasu DataStore)
        domyslne = czytaj(REPO, "src", "server", "PlayerStatsDefaults.server.luau")
        blok = domyslne.split("local DEFAULTS = {", 1)[1].split("\n}", 1)[0]
        klucze = set(re.findall(r"\b([A-Z][A-Za-z]+)\s*=", blok))
        self.assertTrue({"Level", "XP"} <= klucze)
        self.assertEqual(sorted(set(D["tablica"]["statystyki"]) - klucze), [])
        self.assertIn("PLACEHOLDER", domyslne)

    def test_3h_kandydaci_w_starym_miasteczku(self):
        S = D["stare"]
        rnd = random.Random(9)
        sp = {"x": S["znacznik"][0], "z": S["znacznik"][2]}
        bez = LB.kandydaci(D, sp, None)
        self.assertEqual(len(bez), len(S["promienie"]) * len(S["kierunki"]))
        self.assertAlmostEqual(math.hypot(bez[0]["x"] - sp["x"], bez[0]["z"] - sp["z"]), S["promienie"][0], delta=1e-4)
        for _ in range(300):
            spawn = {"x": rnd.uniform(-200, 300), "z": rnd.uniform(-900, -500)}
            a = rnd.uniform(0, math.tau)
            r = rnd.uniform(14, 34)
            portal = {"x": spawn["x"] + math.sin(a) * r, "z": spawn["z"] + math.cos(a) * r}
            k = LB.kandydaci(D, spawn, portal)
            self.assertGreater(len(k), 0)
            for c in k:
                self.assertGreaterEqual(math.hypot(c["x"] - spawn["x"], c["z"] - spawn["z"]), S["min_od_startu"] - 1e-9)
                self.assertGreaterEqual(math.hypot(c["x"] - portal["x"], c["z"] - portal["z"]), S["min_od_portalu"] - 1e-9)
                self.assertGreaterEqual(LB.odl_od_odcinka(c["x"], c["z"], spawn["x"], spawn["z"], portal["x"], portal["z"]),
                                        S["min_od_odcinka"] - 1e-9)
        # portal LasTeleport stoi na pierwszym wolnym miejscu kręgu 16 wokół startu (swiat/biom_las/teleport.py: kąt 0
        # = +Z): pierwszy kandydat nie może leżeć obok niego
        teleport = czytaj(REPO, "swiat", "biom_las", "teleport.py")
        self.assertIn("for _, promien in { 16, 20, 24, 28, 34 } do", teleport)
        k = LB.kandydaci(D, sp, {"x": sp["x"], "z": sp["z"] + 16})
        self.assertGreaterEqual(math.hypot(k[0]["x"] - sp["x"], k[0]["z"] - (sp["z"] + 16)), S["min_od_portalu"])

    def test_3i_dymek_okna(self):
        self.assertTrue(LB.dymek_okna("zbrojownia", None, None, None, None))
        self.assertFalse(LB.dymek_okna("zbrojownia", "EquipmentPanel", None, None, None))
        self.assertFalse(LB.dymek_okna("zbrojownia", None, True, None, None))
        self.assertFalse(LB.dymek_okna("zbrojownia", None, None, True, None))
        self.assertFalse(LB.dymek_okna("zbrojownia", None, None, None, " karczma , zbrojownia "))
        self.assertTrue(LB.dymek_okna("zbrojownia", None, None, None, "zbrojowniaX,karczma"))


# ============================================================================================== 4. Luau w luau_mini
@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py (interpreter nie jest w git) — Luau nie wykonany")
class TestLuau(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.it, cls.L = luau_modul("LogikaBazaru.luau")
        _, cls.D = luau_modul(DANE.PLIK_LUAU)

    def py(self, v):
        return LM.z_luau(v)

    def test_4a_pliki_parsuja_sie_i_przechodza_kontrole(self):
        bledy, parser = SLB.sprawdz_pliki(SLB.pliki_pakietu(), wypisz=lambda *_: None)
        self.assertTrue(parser)
        self.assertEqual(bledy, [])
        self.assertEqual(len(SLB.pliki_pakietu()), 4)

    def test_4b_przypadki_wzorcowe_w_luau(self):
        ok, n, bledy = wolaj(self.it, self.L, "sprawdzPrzypadki", self.D)
        self.assertIn(self.py(bledy), ({}, []))
        self.assertTrue(ok)
        self.assertEqual(int(n), len(D["przypadki"]))
        self.assertGreaterEqual(len(D["przypadki"]), 60)
        # zepsuty przypadek musi zostać wykryty
        Dz = copy.deepcopy(D)
        Dz["przypadki"][0]["wynik"]["akcja"] = "cos_innego"
        ok2, _, bledy2 = wolaj(self.it, self.L, "sprawdzPrzypadki", Dz)
        self.assertFalse(ok2)
        self.assertEqual(len(self.py(bledy2)), 1)

    def test_4c_losowe_wywolania_takie_same(self):
        rnd = random.Random(3)
        ids = D["kolejnosc"] + ["nie_ma"]
        for _ in range(400):
            mid = rnd.choice(ids)
            teraz = rnd.uniform(0, 20)
            stan = {"ostatnieE": rnd.choice([LB.NIGDY, teraz - rnd.uniform(0, 1)]),
                    "ostatniePrzejscie": rnd.choice([LB.NIGDY, teraz - rnd.uniform(0, 5)]),
                    "wTrakcie": rnd.random() < 0.2, "lochy": rnd.random() < 0.3}
            sw = {}
            for k, gen in (("odleglosc", lambda: rnd.uniform(0, 18)), ("chmury", lambda: rnd.random() < 0.7),
                           ("las", lambda: rnd.random() < 0.7), ("cel", lambda: rnd.random() < 0.8),
                           ("poziom", lambda: rnd.randint(0, 20))):
                if rnd.random() < 0.85:
                    sw[k] = gen()
            sp = copy.deepcopy(stan)
            oczek = LB.decyzja(D, mid, sp, teraz, sw)
            sl = LM.do_luau(stan)
            lu = wolaj(self.it, self.L, "decyzja", self.D, mid, sl, teraz, sw)[0]
            self.assertEqual(norm(self.py(lu)), norm(oczek), (mid, stan, sw))
            self.assertEqual(norm(self.py(sl)), norm(sp))
        for _ in range(200):
            gracze = [{"nazwa": "G%03d" % rnd.randint(0, 999) + str(i), "poziom": rnd.choice([None, 1, 2, 5]),
                       "xp": rnd.choice([None, 0, 7]), "moc": rnd.choice([None, 10, 12.5])} for i in range(rnd.randint(0, 12))]
            gracze = [{k: v for k, v in g.items() if v is not None} for g in gracze]
            n = rnd.choice([0, 2, 8])
            self.assertEqual(norm(self.py(wolaj(self.it, self.L, "ranking", gracze, n)[0])), norm(LB.ranking(gracze, n)))
            for w in LB.ranking(gracze, n):
                self.assertEqual(wolaj(self.it, self.L, "wiersz", w)[0], LB.wiersz(w))
        for _ in range(150):
            sp = {"x": rnd.uniform(-300, 300), "z": rnd.uniform(-900, -500)}
            portal = rnd.choice([None, {"x": sp["x"] + rnd.uniform(-30, 30), "z": sp["z"] + rnd.uniform(-30, 30)}])
            argi = [self.D, sp] + ([portal] if portal else [])
            lu = self.it.wywolaj(self.L.get("kandydaci"), [do_luau(a) if not isinstance(a, LM.Tabela) else a for a in argi])[0]
            self.assertEqual(norm(self.py(lu)), norm(LB.kandydaci(D, sp, portal)))
            c = [rnd.uniform(-10, 10) for _ in range(6)]
            self.assertAlmostEqual(wolaj(self.it, self.L, "odlegloscOdOdcinka", *c)[0], LB.odl_od_odcinka(*c), delta=1e-9)
        for _ in range(150):
            powod = rnd.choice(sorted(D["teksty"]) + ["inne"])
            z = rnd.uniform(0, 6)
            self.assertEqual(wolaj(self.it, self.L, "tekstOdmowy", self.D, powod, z)[0], LB.tekst_odmowy(D, powod, z))
            bez = rnd.choice([None, "", "zbrojownia", "karczma, zbrojownia", "a,b,,zbrojownia ,", "zbrojowniaa"])
            otw, zg, wyl = rnd.choice([None, False, "X"]), rnd.choice([None, True, False]), rnd.choice([None, True, False])
            mid = rnd.choice(["zbrojownia", "karczma"])
            self.assertEqual(wolaj(self.it, self.L, "dymekOkna", mid, otw, zg, wyl, bez)[0], LB.dymek_okna(mid, otw, zg, wyl, bez))

    def test_4d_dane_w_luau_rowne_pythonowi(self):
        self.assertEqual(norm(LM.z_luau(self.D, pusta_jako_lista=True)), norm(json.loads(json.dumps(D))))

    def test_4e_lochy_z_progiem_poziomu(self):
        it, L = luau_modul("LogikaBazaru.luau")
        _, Dl = luau_modul(DANE.PLIK_LUAU)
        Dl.get("lochy").set("wymagany_poziom", 8.0)
        D2 = copy.deepcopy(D)
        D2["lochy"]["wymagany_poziom"] = 8
        for poziom in (None, 0, 7, 8, 9, 40):
            for flaga in (False, True):
                s = LB.nowy_stan()
                s["lochy"] = flaga
                self.assertEqual(bool(wolaj(it, L, "lochyOtwarte", Dl, s, poziom)[0]), LB.lochy_otwarte(D2, s, poziom))

    def test_4f_kod_wysylany_do_studio_parsuje_sie(self):
        kody = {"sprawdz": ZB.kod_sprawdz(D), "start": ZB.kod_start(D, czas="x", skrot="x"), "usun": ZB.kod_start(D, True),
                "czesci": ZB.kod_czesci(D), "stare": ZB.kod_stare(D), "koniec": ZB.kod_konca(D),
                "skrypt": ZB.kod_skryptu(D, "Moduly/DaneBazaru", "ModuleScript", None, "return {}")}
        for nazwa, kod in kody.items():
            with self.subTest(kod=nazwa):
                for znak in re.findall(r"__[A-Z_]+__", kod):
                    self.fail("niewstawione %s" % znak)
                LM.Parser(ZB.NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", str(ZB.MIEJSCE)) + kod, nazwa, LM.Interpreter()).program()


# ============================================================================================== 5. punkty styku
class TestStyku(unittest.TestCase):
    def test_5a_nazwy_instancji_istnieja(self):
        plan = {"Punkty", "Podpowiedz", "Tablica", "Ekran", "Ranking", "Tlo", "HumanoidRootPart", "PlayerGui"}
        for sciezka in ZB.FOLDERY:
            plan.update(sciezka.split("/"))
        for _, sciezka in ZB.INNE:
            plan.update(sciezka.split("/"))
        for _, _, sciezka, _ in ZB.SKRYPTY:
            plan.update(sciezka.split("/"))
        for nazwa, tekst in (("SerwerBazaru", SERWER), ("KlientBazaru", KLIENT)):
            uzyte = napisy(tekst, r":WaitForChild") | napisy(tekst, r":FindFirstChild")
            with self.subTest(plik=nazwa):
                self.assertEqual(sorted(uzyte - plan), [])
        for n in ('"Podpowiedz"', '"Tablica"', '"Ekran"', '"Ranking"', '"Tlo"', '"W" .. i', '"E " .. id', '"Miejsce"'):
            self.assertIn(n, ZB.PUNKT + ZB.CZESCI)
        self.assertIn('"W" .. i', SERWER)
        self.assertIn('"E " .. id', KLIENT)
        self.assertIn('"E nowe_miasteczko"', ZB.STARE)

    def test_5b_wiadomosci_zdalne_zgodne(self):
        do_klienta = set(re.findall(r'zdarzenia:FireClient\(gracz, "(\w+)"', bez_komentarzy(SERWER)))
        obsluga = bez_komentarzy(KLIENT).split("zdarzenia.OnClientEvent", 1)[1]
        obslugiwane = set(re.findall(r'polecenie == "(\w+)"', obsluga.split("sterowanie.OnInvoke", 1)[0]))
        self.assertEqual(do_klienta, {"okno", "dymek", "chmury", "przeniesiono"})
        self.assertEqual(do_klienta, obslugiwane)
        kl = bez_komentarzy(KLIENT)
        for zakaz in ("FireServer", "InvokeServer", "RemoteFunction", "PivotTo", "CFrame ="):
            self.assertNotIn(zakaz, kl, zakaz)
        self.assertIn('type(polecenie) ~= "string" or type(id) ~= "string" or not D.miejsca[id]', kl)
        self.assertNotIn("OnServerEvent", bez_komentarzy(SERWER), "klient nic nie wysyła — serwer nie ma czego słuchać")

    def test_5c_atrybuty_ktos_ustawia(self):
        serwer_ustawia = napisy(SERWER, r"kontener:SetAttribute")
        budowa_ustawia = set(re.findall(r':SetAttribute\("(\w+)"', ZB.START + ZB.PUNKT + ZB.STARE))
        klient_ustawia = napisy(KLIENT, r"kontener:SetAttribute")
        testowe = set(ZB.ATRYBUTY_TESTOWE)
        domyslne = czytaj(REPO, "src", "server", "PlayerStatsDefaults.server.luau")
        gracza = set(re.findall(r"\b([A-Z][A-Za-z]+)\s*=", domyslne.split("local DEFAULTS = {", 1)[1].split("\n}", 1)[0]))
        self.assertEqual(sorted(napisy(KLIENT, "GetAttribute") - klient_ustawia - serwer_ustawia - testowe), [])
        self.assertEqual(sorted(napisy(SERWER, "GetAttribute") - serwer_ustawia - budowa_ustawia - gracza), [])
        for a in ("PunktPowrotuStare", "PatrzPowrotuStare", "PunktStartuBazaru", "PatrzStartuBazaru", "Miejsce"):
            self.assertIn(a, budowa_ustawia)
        # atrybut gracza z lochami ustawia serwer, a czyta klient (oba przez D.lochy.atrybut_gracza)
        self.assertIn("gracz:SetAttribute(D.lochy.atrybut_gracza, otwarte)", SERWER)
        self.assertIn("gracz:GetAttribute(D.lochy.atrybut_gracza) == true", KLIENT)

    def test_5d_uchwyty_las_pas_gra_i_teleport_chmury(self):
        zb_pasa = czytaj(REPO, "swiat", "las_pas_gra", "zbuduj.py")
        self.assertIn('KONTENER = "LasPasGra"', zb_pasa)
        self.assertIn('("BindableFunction", "Sygnaly/PrzeniesDoLasu")', zb_pasa)
        self.assertEqual(D["las"]["uchwyt"], "LasPasGra/Sygnaly/PrzeniesDoLasu")
        serwer_pasa = czytaj(REPO, "swiat", "las_pas_gra", "zrodla", "SerwerPasa.server.luau")
        self.assertIn("local PUNKTY_UCHWYTU = { las = true", serwer_pasa)
        self.assertEqual(D["las"]["punkt"], "las")
        self.assertIn("przeniesF.OnInvoke = przeniesDoLasu", serwer_pasa)
        self.assertIn("f:Invoke(gracz, { punkt = D.las.punkt, przelotPo = 0 })", SERWER)
        krainy = json.loads(czytaj(REPO, "swiat", "teleport_chmury", "krainy.json"))
        self.assertEqual(krainy["kontener"], D["chmury"]["kontener"])
        zb_chmur = czytaj(REPO, "swiat", "teleport_chmury", "zbuduj.py")
        self.assertIn('nowy("BindableEvent", "%s", f)' % D["chmury"]["zdarzenie"], zb_chmur)
        kl_chmur = czytaj(REPO, "swiat", "teleport_chmury", "zrodla", "KlientTeleportu.client.luau")
        self.assertIn('kontener:SetAttribute("%s", true)' % D["chmury"]["atrybut_trwa"], kl_chmur)
        self.assertIn("zdarzenieOtworz.Event:Connect", kl_chmur)

    def test_5e_sygnal_hud_i_zdarzenie_okien(self):
        hud = czytaj(REPO, "src", "client", "HUDClient.client.luau")
        self.assertIn('pressed.Name = "%s"' % D["sygnal_hud"], hud)
        self.assertIn("pressed:Fire(b.Name)", hud)
        eq = czytaj(REPO, "src", "client", "EquipmentPanelClient.client.luau")
        self.assertIn('local hudPressed = bindable("HUDButtonPressed")', eq)
        # nazwa zdarzenia okien nie koliduje z niczym w src/ ani w innych pakietach Studio
        for korzen in (os.path.join(REPO, "src"), os.path.join(REPO, "swiat", "teleport_chmury"),
                       os.path.join(REPO, "swiat", "las_pas_gra")):
            for sciezka, _, pliki in os.walk(korzen):
                for n in pliki:
                    if n.endswith(".luau"):
                        self.assertNotIn(D["zdarzenie_okien"], czytaj(sciezka, n), n)
        self.assertIn("ReplicatedStorage:FindFirstChild(D.zdarzenie_okien)", KLIENT)
        self.assertIn("okna:Fire(id,", KLIENT)
        self.assertIn("h:Fire(m.hud)", KLIENT)

    def test_5f_uchwyt_startu_dla_przejscia_przez_chmury(self):
        serwer_chmur = czytaj(REPO, "swiat", "teleport_chmury", "zrodla", "SerwerTeleportu.server.luau")
        # wpis { atrybut = { kontener, punkt, patrz } } czyta atrybuty Vector3 z kontenera w Workspace
        self.assertIn("local k = workspace:FindFirstChild(p.atrybut[1])", serwer_chmur)
        self.assertIn('typeof(punkt) == "Vector3" and typeof(patrz) == "Vector3"', serwer_chmur)
        self.assertIn('f:SetAttribute("PunktStartuBazaru", Vector3.new(__START_KORZEN__))', ZB.START)
        self.assertIn('kontener:SetAttribute("PunktStartuBazaru", v3(D.start.korzen))', SERWER)
        self.assertAlmostEqual(D["start"]["korzen"][1] - D["start"]["punkt"][1], D["podpowiedz"]["wysokosc_korzenia"])
        # gdy przejście przez chmury dostanie uchwyty pakietów (zmiana innego agenta w toku), kształt jest ten sam
        if "przezUchwyt" in serwer_chmur:
            self.assertIn('k:FindFirstChild("Sygnaly")', serwer_chmur)
            self.assertIn("{ punkt = p.punkt, przelotPo = p.przelot_po_s or 0 }", serwer_chmur)
        self.assertIn('opcje.punkt ~= "start"', SERWER)
        self.assertIn("return { ok = true, punkt = punkt, patrz = cel.patrz }", SERWER)
        # wpis z README (jednolinijkowa zmiana w krainy.json) ma kształt, który czyta SerwerTeleportu
        readme = czytaj(PAKIET, "README.md")
        m = re.search(r'(\{"atrybut": \["MiasteczkoBazarGra", "PunktStartuBazaru", "PatrzStartuBazaru"\]\})', readme)
        self.assertIsNotNone(m, "README nie podaje wpisu do krainy.json")
        wpis = json.loads(m.group(1))
        self.assertEqual(wpis["atrybut"][0], D["kontener"])
        mi = next(k for k in krainy_json()["krainy"] if k["id"] == "miasteczko")
        self.assertTrue(any("atrybut" in p for p in mi["przybycie"]), "miasteczko w krainy.json bez wpisów „atrybut”")

    def test_5g_straznik_studio_placeid_i_punkty_historii(self):
        for nazwa in os.listdir(ZR):
            if nazwa.endswith(".luau"):
                self.assertTrue(SLB.SL.pierwsza_instrukcja(czytaj(ZR, nazwa)).startswith(SLB.SL.STRAZNIK), nazwa)
        po = [x.strip() for x in SLB.SL.pierwsza_instrukcja(SERWER).split("\n")[1:6] if x.strip() and not x.strip().startswith("--")]
        self.assertEqual(po[:2], ["script.Parent:Destroy()", "return"])
        self.assertEqual(ZB.MIEJSCE, 129485428021967)
        cel = czytaj(REPO, "swiat", "test_walki_roblox", "cel_studio.py")
        self.assertIn("MIEJSCE = %d" % ZB.MIEJSCE, cel)
        self.assertIn("game.PlaceId ~= __MIEJSCE__", ZB.NAGLOWEK_MIEJSCA)
        self.assertIn("IsRunning()", ZB.NAGLOWEK_MIEJSCA)
        self.assertIn('if d:GetAttribute("Wygenerowane") ~= true then', ZB.START)
        self.assertIn('f:SetAttribute("Wygenerowane", true)', ZB.START)
        self.assertEqual(ZB.START.count("SetWaypoint"), 3)  # przed usunięciem, usunięto, przed budową
        self.assertIn("SetWaypoint", ZB.KONIEC)
        self.assertIn("for _, d in stare do d:Destroy() end", ZB.START)
        self.assertNotIn("workspace:ClearAllChildren", ZB.START + ZB.CZESCI + ZB.STARE)
        zb = czytaj(PAKIET, "zbuduj.py")
        self.assertIn('"Current Studio Mode: Edit" not in stan', zb)
        self.assertIn('"datamodel_type": "Edit"', zb)
        for zakaz in ("SavePlace", "save_place", "Publish", "publish"):
            self.assertNotIn(zakaz, zb.split("def main", 1)[1])

    def test_5h_bez_lighting_i_cudzych_zmian(self):
        for kod in (SERWER, KLIENT, LOGIKA, ZB.SPRAWDZ, ZB.START, ZB.PUNKT, ZB.CZESCI, ZB.STARE, ZB.KONIEC):
            self.assertNotIn("Lighting", bez_komentarzy(kod))
        # budowa tworzy tylko w kontenerze f (Parent = f / jego potomkowie / własne obiekty)
        for nazwa, kod in (("START", ZB.START), ("CZESCI", ZB.CZESCI), ("STARE", ZB.STARE), ("PUNKT", ZB.PUNKT)):
            for m in re.finditer(r"(\w+)\.Parent = (\w[\w.]*)", bez_komentarzy(kod)):
                with self.subTest(kod=nazwa, linia=m.group(0)):
                    self.assertIn(m.group(2), {"f", "workspace", "rodzic", "p", "b", "t", "tlo", "sg", "e", "model",
                                               "punkty", "f:FindFirstChild(czesci[1])"})
            self.assertNotIn("MiasteczkoBazar.", kod)
        self.assertIn("f.Parent = workspace", ZB.START)

    def test_5i_bez_sciezek_lokalnych(self):
        wzor = re.compile(r"[A-Za-z]:\\\\?Users|/Users/|/home/|AppData|@[a-z0-9-]+\.(?:com|pl)\b", re.I)
        for korzen, _, pliki in os.walk(PAKIET):
            if "__pycache__" in korzen:
                continue
            for nazwa in pliki:
                if nazwa == "test_bazaru.py":
                    continue  # ten plik zawiera sam wzorzec
                if nazwa.endswith((".py", ".luau", ".md", ".json")):
                    with self.subTest(plik=nazwa):
                        self.assertIsNone(wzor.search(czytaj(korzen, nazwa)))

    def test_5j_zbuduj_sucho_bez_studio(self):
        r = subprocess.run([sys.executable, "-B", os.path.join(PAKIET, "zbuduj.py"), "--sucho"], capture_output=True, cwd=REPO)
        wyj = r.stdout.decode("utf-8", "replace")
        self.assertEqual(r.returncode, 0, wyj[-2000:])
        self.assertIn("sucho: OK", wyj)
        self.assertIn("Workspace/MiasteczkoBazarGra", wyj)
        self.assertIn("129485428021967", wyj)
        kod = ("import sys; sys.argv = ['zbuduj.py', '--sucho']; sys.path.insert(0, %r); import zbuduj; zbuduj.main(); "
               "print('IMPORTY', 'studio_mcp' in sys.modules, 'cel_studio' in sys.modules)" % PAKIET)
        r = subprocess.run([sys.executable, "-B", "-c", kod], capture_output=True, cwd=REPO)
        self.assertIn("IMPORTY False False", r.stdout.decode("utf-8", "replace"))

    def test_5k_proba_play_kompiluje_sie_i_ma_liste(self):
        plik = os.path.join(TU, "proba_play.py")
        with tempfile.TemporaryDirectory() as tmp:
            py_compile.compile(plik, cfile=os.path.join(tmp, "p.pyc"), doraise=True)
        tekst = czytaj(plik)
        for kod in ["B%02d" % i for i in range(1, 15)]:
            self.assertIn(kod, tekst.split('"""', 2)[1], kod)
        zrzuty = re.findall(r"\b0[1-8]_\w+", tekst.split('"""', 2)[1])
        self.assertGreaterEqual(len(set(zrzuty)), 6)
        self.assertLessEqual(len(set(zrzuty)), 8)
        self.assertNotIn("mp4", tekst)
        r = subprocess.run([sys.executable, "-B", plik], capture_output=True, cwd=REPO)
        self.assertNotEqual(r.returncode, 0, "bez argumentów próba ma tylko wypisać sposób użycia")
        self.assertNotIn("Traceback", r.stderr.decode("utf-8", "replace"))


def krainy_json():
    return json.loads(czytaj(REPO, "swiat", "teleport_chmury", "krainy.json"))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    unittest.main(verbosity=2)
