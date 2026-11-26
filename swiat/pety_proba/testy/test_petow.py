# -*- coding: utf-8 -*-
"""Testy pakietu „jajka i pety na próbę” — bez Studio, bez sieci.

    python -B swiat/pety_proba/testy/test_petow.py        (unittest; kod 1 przy błędzie)

1. Dane: zrodla/ aktualne; szanse każdego jajka i cena kalkulatora = tools/walka/progresja.py; każdy pet w puli
   jednego jajka; położenia = znaczniki map (las-pas, Bagno); obrót stanowiska = swiat/las_pas/punkty.py; teksty bez
   napisów dla twórców; paski podglądu tablic = szanse; skille: pet Bagna trochę lepszy od leśnego tej samej
   rzadkości, ale słabszy od leśnego o stopień rzadszego (leśny legendarny zostaje ważny).
2. Modele: dziesięć petów i dwa jajka budują się (bez błędów), mają klipy spoczynek / chod / radosc / wyklucie (jajka:
   spoczynek / trzesienie / pekniecie), są tanie w częściach, plansze i portrety z Blendera leżą w wynik/; stałe bryły
   inkubatorów (tablica; w Bagnie gniazdo na palach i latarenka).
3. Logika: 100 000 losowań na jajko daje szanse z danych; cena stała domyślnie (decyzja 17.11), rosnąca do maksimum
   i kalkulator jako przełącznik; licznik ceny osobny / wspólny (liczy się tylko przy rosnącej);
   Luau w luau_mini = lustro w Pythonie (przypadki wzorcowe, zepsuty przypadek wykryty, losowe wywołania).
4. Ekonomia: pętla gracza z ekonomia_jajek.py = symulacja_lasu.jeden_gracz; pierwsze jajko po 5–10 min lasu,
   pierwsze jajko Bagna po 5–10 min Bagna.
5. PRAWDZIWY SerwerPetow.server.luau + PRAWDZIWY SerwerStanu.server.luau w luau_mini (atrapa Roblox): zakup bez
   Złota odrzucony z kwotą braku, zakup prawdziwym E (podpowiedź) przy obu inkubatorach, podwójny zakup naraz,
   nieznane jajko, Złoto nigdy poniżej zera, stała cena każdego jajka (rosnąca i wspólny licznik po przełączeniu
   w danych), wybór peta
   (tylko posiadany i przy zagrodzie), odstawienie, „czekaj”, limit zdarzeń, brak StanGracza.
6. Styki: StanGracza (sygnał Pety, atrybuty, lista wydatków), bazar (OknoMiejsca, id zagrody), ukrycie (BlokadaWalki,
   TreningGra, Trwa chmur, ekrany), wiadomości klient–serwer w obie strony, pola danych używane przez klienta.
7. Kontrola Luau (z wykryciem zepsutego pliku), zbuduj.py --sucho, kod do Studio parsuje się, proba_play --sprawdz,
   brak ścieżek lokalnych.
"""
import json
import math
import os
import random
import re
import subprocess
import sys
import unittest

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
STAN = os.path.join(REPO, "swiat", "stan_gracza")
for _s in (os.path.join(STAN, "testy"), STAN, os.path.join(REPO, "tools", "walka"), PAKIET, REPO):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import dane_petow as DP  # noqa: E402
import logika_petow as LP  # noqa: E402
import sprawdz_luau_petow as SLP  # noqa: E402
import zbuduj as ZB  # noqa: E402
import progresja  # noqa: E402

LM = SLP.luau_mini()
D = DP.dane_z_przypadkami()
U = DP.ustawienia()
ZR = os.path.join(PAKIET, "zrodla")


def czytaj(*czesci):
    with open(os.path.join(*czesci), encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def bez_komentarzy(tekst):
    return SLP.SL.rozbierz(tekst)[0]


SERWER = czytaj(ZR, "SerwerPetow.server.luau")
KLIENT = czytaj(ZR, "KlientPetow.client.luau")
LOGIKA = czytaj(ZR, "LogikaPetow.luau")
DANE_LUAU = czytaj(ZR, "DanePetow.luau")


def _modul_stanu(nazwa, plik):
    import importlib.util
    if nazwa in sys.modules:
        return sys.modules[nazwa]
    spec = importlib.util.spec_from_file_location(nazwa, os.path.join(STAN, plik))
    m = importlib.util.module_from_spec(spec)
    sys.modules[nazwa] = m
    spec.loader.exec_module(m)
    return m


# ============================================================================================== 1. dane
class TestDanych(unittest.TestCase):
    def test_1a_aktualne(self):
        zle, _, pliki = DP.aktualny()
        self.assertEqual(zle, [], "uruchom python -B swiat/pety_proba/dane_petow.py")
        self.assertEqual(len(pliki), 1 + len(U["pety"]) + len(U["jajka"]))

    def test_1b_szanse_i_cena_z_kalkulatora(self):
        rz = [r["id"] for r in U["rzadkosci"]]
        w_pulach = []
        for j in D["jajka"]:
            self.assertEqual([s["szansa"] for s in j["szanse"]], list(progresja.ZALOZENIA["szanse_jajka"]), j["id"])
            self.assertAlmostEqual(sum(s["szansa"] for s in j["szanse"]), 1.0, places=12)
            # rzadkości w kolejności puli (pospolity … legendarny) — rzadszy pet = mniejsza szansa
            self.assertEqual([LP.pet(D, s["pet"])["rzadkosc"] for s in j["szanse"]], rz, j["id"])
            w_pulach += [s["pet"] for s in j["szanse"]]
        self.assertEqual(sorted(w_pulach), sorted(p["id"] for p in U["pety"]), "każdy pet w puli dokładnie jednego jajka")
        self.assertEqual(D["jajka"][0]["cena"]["kalkulator"], progresja.ZALOZENIA["ceny_jajek"][0])
        self.assertEqual([j["kraina"] for j in D["jajka"]], ["las", "bagno", "dzungla"])
        self.assertIn(D["licznik_ceny"]["tryb"], ("osobny", "wspolny"))
        for p in D["pety"]:
            self.assertEqual(LP.jajko_peta(D, p["id"])["id"], p["jajko"])

    def test_1d_wybieg_z_legowisk(self):
        """26.11.2026: pety chodzą luzem — prostokąt wybiegu z miejsc petów na mapie i marginesów; klient ma spacer
        i wyłącznik; od decyzji Pawła „legowiska znikają” pet nie wraca na swoje miejsce, tylko odpoczywa, gdzie stoi."""
        G, W = D["polozenia"], U["zagroda"]["wybieg"]
        wb = G["wybieg"]
        s, ox, oz = wb["srodek"], wb["os_x"], wb["os_z"]
        self.assertAlmostEqual(ox[0] * oz[0] + ox[2] * oz[2], 0.0, places=3)        # osie prostopadłe
        self.assertAlmostEqual(oz[0], G["zagroda_kier"][0], places=3)                # oś z = przód zagrody (ku bramce)
        ab = [((m[0] - s[0]) * ox[0] + (m[2] - s[2]) * ox[2], (m[0] - s[0]) * oz[0] + (m[2] - s[2]) * oz[2])
              for m in G["miejsca_petow"]]
        for a, b in ab:                                                             # każde legowisko w wybiegu
            self.assertLessEqual(abs(a), wb["pol_x"] + 0.01)
            self.assertLessEqual(abs(b), wb["pol_z"] + 0.01)
        # boki = rozpiętość legowisk + marginesy (z dokładnością zaokrąglenia znaczników)
        self.assertAlmostEqual(2 * wb["pol_x"], max(a for a, _ in ab) - min(a for a, _ in ab) + 2 * W["margines_bok"],
                               delta=0.02)
        self.assertAlmostEqual(2 * wb["pol_z"], max(b for _, b in ab) - min(b for _, b in ab) + W["margines_tyl"]
                               + W["margines_przod"], delta=0.02)
        # przód (bramka, miski) dalej od legowisk niż tył (koryto): większy margines z przodu
        self.assertAlmostEqual(max(b for _, b in ab), wb["pol_z"] - W["margines_przod"], delta=0.02)
        # w wybiegu mieści się tyle petów, ile jest miejsc: koła o średnicy odstępu nie zajmują więcej niż pół pola
        n = len(G["miejsca_petow"])
        self.assertLess(n * math.pi * (W["odstep"] / 2.0) ** 2, 0.5 * 4 * wb["pol_x"] * wb["pol_z"])
        self.assertLess(W["mijanie"], W["odstep"])
        for para in ("predkosc", "start_s", "postoj_s", "drzemka_s", "mijanie_s"):
            self.assertTrue(0 < W[para][0] <= W[para][1], para)
        self.assertTrue(0 <= W["drzemka_szansa"] <= 1)
        k = bez_komentarzy(KLIENT)
        for pole in set(re.findall(r"\bust\.(\w+)", k)) | set(re.findall(r"Wybieg\.ust\.(\w+)", k)):
            self.assertIn(pole, W, "wybieg.%s" % pole)
        for pole in set(re.findall(r"\bo\.(\w+)", k.split("local Wybieg = {", 1)[1].split("local function ustawPetyZagrody", 1)[0])):
            self.assertIn(pole, wb, "polozenia.wybieg.%s" % pole)
        self.assertIn("pcall(Wybieg.krok, dt, t)", k)
        self.assertIn("if Wybieg.czynny then", k)
        self.assertNotIn("cel = z.dom", k)                                          # bez powrotu na legowisko (26.11)
        # bez ustawień wybiegu dane nie mają prostokąta (klient zostawia pety na legowiskach)
        stare = U["zagroda"].pop("wybieg")
        try:
            self.assertNotIn("wybieg", DP.polozenia(U))
        finally:
            U["zagroda"]["wybieg"] = stare

    def test_1c_polozenia_ze_znacznikow(self):
        for j, ju in zip(D["jajka"], U["jajka"]):
            z = json.loads(czytaj(REPO, *ju["stanowisko"]["znaczniki"].split("/")))
            m = next(x for x in z["miejsca"] if x["id"] == "jajko")
            e = next(x for x in z["punkty_e"] if x["grupa"] == "Punkty/StanowiskoJajka")
            G = j["polozenie"]
            self.assertEqual(G["gniazdo"], [round(v, 3) for v in m["punkt_swiat"]], j["id"])
            self.assertEqual(G["e"], [round(v, 3) for v in e["punkt_swiat"]], j["id"])
            # stanowisko przy miejscu przybycia biomu, w prostokącie strefy spokoju „wejscie”
            przyb = z["przybycie"]["punkt_swiat"]
            self.assertLess(((G["gniazdo"][0] - przyb[0]) ** 2 + (G["gniazdo"][2] - przyb[2]) ** 2) ** 0.5, 40)
            wej = next(s for s in z["strefy_spokoju"] if s["id"] == "wejscie")["prostokat_swiat"]
            self.assertTrue(wej["x"][0] <= G["gniazdo"][0] <= wej["x"][1] and wej["z"][0] <= G["gniazdo"][2] <= wej["z"][1])
            # obrót stanowiska jak w mapie (swiat/las_pas/punkty.py, stanowisko_jajka — Bagno stawia to samo)
            punkty = czytaj(REPO, "swiat", "las_pas", "punkty.py")
            cialo = punkty.split("def stanowisko_jajka", 1)[1].split("\ndef ", 1)[0]
            self.assertIn("obrot=(0, %d, 0)" % G["obrot"], cialo)
        self.assertIn("punkty_lasu.stanowisko_jajka(s, K)", czytaj(REPO, "swiat", "bagno_pas", "miejsca.py"))
        G = D["polozenia"]
        baz = json.loads(czytaj(REPO, "swiat", "miasteczko_bazar", "znaczniki.json"))["zagroda"]
        self.assertEqual(G["zagroda_e"], [round(v, 3) for v in baz["punkt_e"]["swiat"]])
        # 25.11.2026: tyle miejsc, ile znaczników zagroda_miejsce_N ma mapa (było 6, przebudowa miasta daje 8)
        self.assertEqual(len(G["miejsca_petow"]), len(baz["miejsca_petow"]))
        self.assertIn(len(G["miejsca_petow"]), (6, 8))

    def test_1d_teksty_dla_gracza(self):
        tworcy = re.compile(r"D-0\d\d|Paweł|Karol|\btest|placeholder|atrybut|lorem|TODO", re.I)
        for k, t in U["teksty"].items():
            for x in (t if isinstance(t, list) else [t]):
                self.assertIsNone(tworcy.search(x), (k, x))
        for p in U["pety"]:
            self.assertIsNone(tworcy.search(p["nazwa"] + p["skill"]["nazwa"]), p["id"])
        self.assertEqual(U["zagroda"]["napis_proby"], "PRÓBA")
        # nazwy własne petów — nie z innych gier (lista znanych nazw, których unikamy)
        obce = {"pikachu", "eevee", "bulbasaur", "chikorita", "vulpix", "dragonite", "huge cat", "dominus"}
        for p in U["pety"]:
            self.assertNotIn(p["nazwa"].lower(), obce)

    def test_1e_paski_podgladu_tablicy_jak_szanse(self):
        for j in U["jajka"]:
            modul = czytaj(REPO, "swiat", "postacie", j["model"]["modul"] + ".py")
            paski = re.search(r"PASKI = \[(.*?)\]\n", modul, re.S).group(1)
            self.assertEqual([float(x) for x in re.findall(r", ([\d.]+)\)", paski)],
                             list(progresja.ZALOZENIA["szanse_jajka"]), j["id"])

    def test_1f_skille_d101_w_granicach_stanu_gracza(self):
        # D-101: różne premie i żywioły; pospolite i zwykłe tylko mała pasywka; każdy skill przechodzi
        # przez Sygnaly/Modyfikatory stanu gracza (czysty_modyfikator) bez odmowy
        DS = _modul_stanu("dane_stanu_test_petow", "dane.py")
        LS = _modul_stanu("logika_stanu", "logika_stanu.py")
        _, Ds = DS.dane_z_przypadkami()
        rodzaje = set()
        for p in D["pety"]:
            mod = LP.mod_peta(D, p["id"])
            czysty, powod = LS.czysty_modyfikator(Ds, mod)
            self.assertIsNotNone(czysty, (p["id"], powod, mod))
            wartosci = list((mod.get("procent") or {}).values()) + list((mod.get("lup") or {}).values())
            if p["rzadkosc"] in ("pospolity", "zwykly"):
                self.assertNotIn("pasywki", mod, p["id"])
                self.assertTrue(wartosci and max(wartosci) <= 0.03, (p["id"], mod))
            else:
                self.assertTrue("pasywki" in mod or max(wartosci) >= 0.15, (p["id"], mod))
            for n in mod.get("pasywki", []):
                self.assertIn(n, Ds["pasywki_silnika"], (p["id"], n))
            rodzaje |= {"lup_" + k for k in mod.get("lup", {})} | {"stat_" + k for k in mod.get("procent", {})}
            if p["skill"].get("zywiol"):
                rodzaje.add("zywiol_" + p["skill"]["zywiol"])
            # jedno krótkie zdanie (tablica, okno, napis po wykluciu)
            self.assertLessEqual(len(LP.opis_skilla(D, p)), 80, p["id"])
        self.assertTrue({"lup_zloto", "lup_doswiadczenie"} <= rodzaje, rodzaje)
        self.assertGreaterEqual(len([r for r in rodzaje if r.startswith("stat_")]), 5, rodzaje)
        self.assertGreaterEqual(len([r for r in rodzaje if r.startswith("zywiol_")]), 3, rodzaje)
        # każdy żywioł działa dla każdej klasy: zaklęcie broni (podpalenie / trucizna przy ciosie — każda klasa) albo
        # pasywka dla każdej klasy (stan gracza liczy tylko pasywki klasy gracza)
        for zid, z in D["zywioly"].items():
            klasy = {Ds["pasywki_silnika"][n]["klasa"] for n in z["pasywki"]}
            self.assertTrue(z.get("zaklecie") in Ds["zaklecia_silnika"] if z.get("zaklecie") else klasy == set(Ds["klasy"]),
                            (zid, klasy))
        self.assertIn(D["kontener"], Ds["wydatki"]["zrodla"])
        self.assertEqual(Ds["modyfikatory"]["zrodlo_pety"], U["stan_gracza"]["zrodlo_modyfikatora"])


# ============================================================================================== 2. modele
class TestModeli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rigi = DP.rigi(U)

    def test_2a_klipy_i_czesci(self):
        for p in U["pety"]:
            R = self.rigi[p["id"]]
            self.assertEqual(set(R["klipy"]), {"spoczynek", "chod", "radosc", "wyklucie"}, p["id"])
            self.assertTrue(R["klipy"]["spoczynek"]["petla"] and R["klipy"]["chod"]["petla"])
            self.assertFalse(R["klipy"]["wyklucie"]["petla"] or R["klipy"]["radosc"]["petla"])
            self.assertLessEqual(len(R["czesci"]), 45, "%s: za dużo części dla peta przy graczu" % p["id"])
            self.assertLessEqual(len(R["kosci"]), 12, p["id"])
            self.assertIsNotNone(R["glowa"], p["id"])
            self.assertTrue(1.4 <= R["wysokosc"] <= 3.4, (p["id"], R["wysokosc"]))
        for j in U["jajka"]:
            J = self.rigi[j["model"]["jajko"]]
            self.assertEqual(set(J["klipy"]), {"spoczynek", "trzesienie", "pekniecie"}, j["id"])
            self.assertTrue(any(c[2] == "Wnetrze" for c in J["czesci"]), "jajko bez świecącego Wnetrza (kolor rzadkości)")
            self.assertLessEqual(len(J["czesci"]), 30, j["id"])
            # gładkie jajko (17.11): skorupka i czubek to elipsoidy (SpecialMesh Sphere albo kula Ball), nie schodki
            kule = [c for c in J["czesci"] if c[14] == "Sphere" or c[1] == 1]
            self.assertGreaterEqual(len([c for c in kule if c[2] in ("Skorupka", "Skorupka gora", "Czubek")]), 3, j["id"])

    def test_2b_rozne_sylwetki_i_efektowniejsze_rzadsze(self):
        wymiary = []
        for j in D["jajka"]:
            neony = []
            for pid in j["pula"]:
                R = self.rigi[pid]
                xs = [abs(c[3]) + c[9] / 2 for c in R["czesci"]]
                zs = [c[5] for c in R["czesci"]]
                wymiary.append((round(R["wysokosc"], 1), round(2 * max(xs), 1), round(max(zs) - min(zs), 1)))
                neon = R["materialy"].index(["Neon", 0.0]) if ["Neon", 0.0] in R["materialy"] else -1
                neony.append(sum(1 for c in R["czesci"] if c[13] == neon and c[2] not in ("Blysk L", "Blysk P")))
            self.assertEqual(neony[:3], [0, 0, 0], "%s: pospolite, zwykłe i rzadkie bez świecenia (poza odblaskiem oczu)"
                             % j["id"])
            # epicki i legendarny świecą (Neon); legendarny od 17.11 tylko kryształy i klejnot — cały Neon poroża zlewał
            # się w grze w plamę; przy wykluciu oba dostają słup światła (KlientPetow, nr rzadkości ≥ 4)
            self.assertTrue(neony[3] >= 3 and neony[4] >= 3, (j["id"], neony))
        self.assertEqual(len(set(wymiary)), len(wymiary), wymiary)

    def test_2c_plansze_i_portrety_z_blendera(self):
        modele = [(p["id"], p["id"]) for p in U["pety"]]
        modele += [(j["model"]["modul"], m) for j in U["jajka"] for m in (j["model"]["jajko"], j["model"]["inkubator"])]
        for folder, mid in modele:
            for przyrostek in ("_plansza.jpg", "_bohater.jpg", "_ikona.png", ".glb", ".fbx"):
                sciezka = os.path.join(REPO, "swiat", "postacie", "wynik", folder, mid + przyrostek)
                self.assertTrue(os.path.isfile(sciezka), "brak %s — python -B swiat/postacie/przebuduj.py %s --bez-filmow"
                                % (os.path.relpath(sciezka, REPO), folder))

    def test_2d_stale_bryly_inkubatorow(self):
        for j, ju in zip(D["jajka"], U["jajka"]):
            T = j["stale"]
            kosci = {c[0] for c in T["czesci"]}
            nazwy = [c[2] for c in T["czesci"]]
            self.assertEqual(kosci, set(ju["model"]["kosci_stale"]), j["id"])
            self.assertIn(U["modele"]["papier"], nazwy, j["id"])
            self.assertFalse(any(n.startswith(("Pasek szansy", "Znak peta")) for n in nazwy), "paski rysuje SurfaceGui")
            self.assertLessEqual(len(T["czesci"]), 60, j["id"])
        las, bagno = D["jajka"][:2]
        self.assertAlmostEqual(las["y_jajka"], 0.92, places=2)    # jajko na mchu gniazda z mapy lasu
        self.assertTrue(las["jajko_na_mchu"] and not bagno["jajko_na_mchu"])
        # Bagno: gniazdo na palach nad korzeniami stanowiska z mapy (wierzch korzeni ok. 1,8) — jajko wyżej
        self.assertGreater(bagno["y_jajka"], 1.8)
        for n in ("Pal", "Platforma", "Trzcina", "Ognik", "Tyczka"):
            self.assertIn(n, [c[2] for c in bagno["stale"]["czesci"]])


# ============================================================================================== 3. logika
class TestLogiki(unittest.TestCase):
    def test_3a_sto_tysiecy_losowan(self):
        for j in D["jajka"]:
            los = random.Random("1711-" + j["id"])
            n = 100000
            licz = {s["pet"]: 0 for s in j["szanse"]}
            for _ in range(n):
                licz[LP.losuj(D, j, los.random())] += 1
            for s in j["szanse"]:
                p = s["szansa"]
                sigma = (p * (1 - p) / n) ** 0.5
                self.assertLess(abs(licz[s["pet"]] / n - p), 4.5 * sigma, (j["id"], s, licz))
            self.assertGreater(licz[j["pula"][-1]], 0)
            self.assertEqual(set(licz), set(j["pula"]), "z jajka tylko pety jego puli")

    def test_3b_cena(self):
        # decyzja Karola 17.11: cena stała dla każdego jajka (domyślny tryb), rośnie tylko między biomami
        for j in D["jajka"]:
            c = j["cena"]
            self.assertEqual(c["tryb"], "stala", j["id"])
            self.assertEqual({LP.cena(D, j, n) for n in list(range(15)) + [-1, 2.5, None, "3"]}, {c["stala"]}, j["id"])
            # przełącznik „rosnaca” (w danych zostaje): od startu, nie maleje, do maks
            ceny = [LP.cena(D, j, n, "rosnaca") for n in range(15)]
            self.assertEqual(ceny[0], c["start"])
            self.assertEqual(ceny, sorted(ceny), "cena nie maleje")
            self.assertEqual(max(ceny), c["maks"])
            self.assertEqual(LP.cena(D, dict(j, cena=dict(c, tryb="rosnaca")), 2), c["start"] + 2 * c["krok"])
            for zle in (-1, 2.5, None, "3"):
                self.assertEqual(LP.cena(D, j, zle, "rosnaca"), c["start"])
        las, bagno = D["jajka"][:2]
        self.assertEqual((las["cena"]["stala"], bagno["cena"]["stala"]), (300, 750))
        self.assertLess(las["cena"]["stala"], las["cena"]["kalkulator"], "tańsza niż kalkulator (1000)")
        self.assertEqual(LP.cena(D, dict(las, cena=dict(las["cena"], tryb="kalkulator")), 3), las["cena"]["kalkulator"])
        self.assertGreater(bagno["cena"]["stala"], las["cena"]["stala"], "w Bagnie więcej Złota — droższe jajko")
        # napis ceny na tablicy i nad jajkiem
        self.assertEqual(LP.opis_ceny(D, las), "cena: 300 Rybek")
        self.assertEqual(LP.opis_ceny(D, bagno), "cena: 750 Rybek")
        self.assertEqual(LP.opis_ceny(D, las, "rosnaca"), "od 300 Rybek · rośnie z każdym jajkiem")

    def test_3b2_licznik_osobny_i_wspolny(self):
        las, bagno = D["jajka"][:2]
        w = {las["id"]: 4, bagno["id"]: 1, "inny_cel": 9}
        self.assertEqual((LP.kupione(D, las, w, "osobny"), LP.kupione(D, bagno, w, "osobny")), (4, 1))
        self.assertEqual((LP.kupione(D, las, w, "wspolny"), LP.kupione(D, bagno, w, "wspolny")), (5, 5))
        self.assertEqual(LP.kupione(D, las, w), LP.kupione(D, las, w, D["licznik_ceny"]["tryb"]))
        for zle in (None, "x", {las["id"]: -2}, {las["id"]: 1.5}, {las["id"]: "3"}):
            self.assertEqual(LP.kupione(D, las, zle, "wspolny"), 0, zle)
        # przy cenie stałej (domyślnej) licznik nie zmienia ceny; przy rosnącej: osobny — jajka z lasu nie podnoszą
        # ceny jajka Bagna, wspólny — podnoszą
        for tryb in ("osobny", "wspolny"):
            self.assertEqual(LP.cena(D, bagno, LP.kupione(D, bagno, {las["id"]: 5}, tryb)), bagno["cena"]["stala"])
        self.assertEqual(LP.cena(D, bagno, LP.kupione(D, bagno, {las["id"]: 5}, "osobny"), "rosnaca"), bagno["cena"]["start"])
        self.assertGreater(LP.cena(D, bagno, LP.kupione(D, bagno, {las["id"]: 5}, "wspolny"), "rosnaca"),
                           bagno["cena"]["start"])

    def test_3c_decyzja_i_teksty(self):
        self.assertEqual(LP.decyzja(D, {"stan_gracza": False, "jajko": "jajko_lesne"})["powod"], "brak_stanu")
        self.assertEqual(LP.decyzja(D, {"stan_gracza": True, "jajko": "xx"})["powod"], "nieznane_jajko")
        self.assertEqual(LP.decyzja(D, {"stan_gracza": True, "jajko": "jajko_lesne", "zajety": True})["powod"],
                         "trwa_wyklucie")
        self.assertEqual(LP.tekst_braku(D, 120, 180, 300), "Brakuje ci 120 Rybek (masz 180, jajko kosztuje 300)")
        self.assertEqual(LP.tekst_braku(D, 1, 299, 300), "Brakuje ci 1 Rybki (masz 299, jajko kosztuje 300)")
        self.assertEqual(LP.tekst_braku_ulepszenia(D, 1, 999, 1000),
                         "Brakuje ci 1 Rybki (masz 999, ulepszenie kosztuje 1000)")
        self.assertEqual([LP.procent(x) for x in (0.5, 0.02, 0.005)], ["50%", "2%", "0,5%"])
        self.assertEqual(LP.opis_skilla(D, LP.pet(D, "zoledziak")), "+2% Rybek z walk")
        self.assertEqual(LP.opis_skilla(D, LP.pet(D, "lisciolis")), "+15% Zręczności i Szczęścia")
        self.assertEqual(LP.opis_skilla(D, LP.pet(D, "ognik")), "Ogień: podpala wroga przy ciosie (25%)")
        self.assertEqual(LP.opis_skilla(D, LP.pet(D, "wazeczka")), "Jad: zatruwa wroga przy ciosie (30%)")
        self.assertEqual(LP.opis_skilla(D, LP.pet(D, "jelonek_gaju")),
                         "Kryształ: ciosy mocniej trafiają, +20% Siły, +5% Rybek i doświadczenia z walk")
        # waluta to Rybki (D-146, atrybut Gold): odmiana przy liczbie w mianowniku, bierniku i dopełniaczu
        oczek = {0: ("Rybek", "Rybek", "Rybek"), 1: ("Rybka", "Rybkę", "Rybki"), 2: ("Rybki", "Rybki", "Rybek"),
                 4: ("Rybki", "Rybki", "Rybek"), 5: ("Rybek", "Rybek", "Rybek"), 11: ("Rybek", "Rybek", "Rybek"),
                 12: ("Rybek", "Rybek", "Rybek"), 14: ("Rybek", "Rybek", "Rybek"), 21: ("Rybek", "Rybek", "Rybek"),
                 22: ("Rybki", "Rybki", "Rybek"), 25: ("Rybek", "Rybek", "Rybek"), 100: ("Rybek", "Rybek", "Rybek"),
                 101: ("Rybek", "Rybek", "Rybek"), 102: ("Rybki", "Rybki", "Rybek"), 112: ("Rybek", "Rybek", "Rybek")}
        for n, (m, b, d) in oczek.items():
            self.assertEqual([LP.ile_rybek(D, n), LP.ile_rybek(D, n, "b"), LP.ile_rybek(D, n, "d")],
                             ["%d %s" % (n, m), "%d %s" % (n, b), "%d %s" % (n, d)], n)
        T = D["teksty"]
        self.assertEqual(D["inkubator"]["napis_akcja_cena"] % LP.ile_rybek(D, 1, "b"), "Kup za 1 Rybkę")
        self.assertEqual(D["inkubator"]["napis_akcja_cena"] % LP.ile_rybek(D, 750, "b"), "Kup za 750 Rybek")
        self.assertEqual(T["ulepsz"] % (4, LP.ile_rybek(D, 1000, "b")), "Więcej miejsc: 4 za 1000 Rybek")
        self.assertEqual([LP.opis_przychodu(D, s) for s in (0, 1 / 60.0, 0.05, 0.1, 0.04, 0.2, 22 / 60.0, 0.25)],
                         ["+0 Rybek/min", "+1 Rybka/min", "+3 Rybki/min", "+6 Rybek/min", "+2,4 Rybki/min",
                          "+12 Rybek/min", "+22 Rybki/min", "+15 Rybek/min"])
        teksty = [x for t in list(T.values()) + [D["inkubator"]["napis_akcja_cena"]]
                  for x in (t if isinstance(t, list) else [t])]
        self.assertFalse([t for t in teksty if "Złot" in t or "złot" in t], "waluta to Rybki, nie Złoto")
        self.assertEqual((LP.opis_skilla_krotki(D, LP.pet(D, "ognik")), LP.opis_skilla_krotki(D, LP.pet(D, "lisciolis"))),
                         ("Ogień", "+15% Zręczności i Szczęścia"))
        self.assertEqual(LP.mod_peta(D, "ognik"), {"pasywki": ["ognista_rozdzka"], "zaklecie": "podpalenie"})
        self.assertEqual(LP.mod_peta(D, "wazeczka"), {"pasywki": ["kumulowanie_trucizny"], "zaklecie": "trucizna"})
        self.assertEqual(LP.premia_peta(D, "lisciolis"), {"zloto": 0, "doswiadczenie": 0})
        self.assertIsNone(LP.mod_peta(D, "obcy"))
        self.assertEqual(LP.decyzja(D, {"stan_gracza": True, "jajko": "jajko_bagienne"})["ok"], True)
        self.assertEqual(LP.jajko_krainy(D, "bagno")["id"], "jajko_bagienne")
        self.assertEqual(LP.jajko_krainy(D, "dzungla")["id"], "jajko_dzungli")
        self.assertIsNone(LP.jajko_krainy(D, "pustynia"))


def luau_logika():
    it = LM.Interpreter()
    rs = LM.Tabela()
    rs.set("IsStudio", lambda _s: True)
    game = LM.Tabela()
    game.set("GetService", lambda _s, _n: rs)
    it.globalne.z["game"] = game
    Dl = it.wykonaj(DANE_LUAU, "DanePetow.luau")[0]
    Ll = it.wykonaj(LOGIKA, "LogikaPetow.luau")[0]
    return it, Dl, Ll


@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py — Luau nie wykonany")
class TestZagrody(unittest.TestCase):
    """Zagroda petów (25.11.2026): stawki, miejsca, wybór — lustro w Pythonie (Luau: przypadki wzorcowe)."""

    def test_3g_stawki_rosna_z_rzadkoscia_i_biomem(self):
        Z = D["zagroda"]
        for j in D["jajka"]:
            st = [LP.stawka(D, x) for x in j["pula"]]
            self.assertEqual(st, sorted(st), j["id"])
            for x in j["pula"]:
                p = LP.pet(D, x)
                self.assertAlmostEqual(p["rybki_s"], Z["stawki_s"][p["rzadkosc"]] * Z["mnozniki_jajek"][j["id"]], 4)
        self.assertEqual([p["miejsc"] for p in Z["poziomy"]], [2, 4, 6, 8])
        self.assertEqual(LP.stawka(D, "obcy"), 0)

    def test_3h_kto_stoi_w_zagrodzie(self):
        ids = [p["id"] for p in D["pety"]]
        kopie = {x: 1 for x in ids}
        # najrzadsze: legendarne trzech jajek, potem epickie; przy tej samej rzadkości wyższa stawka (dalszy biom)
        st = LP.w_zagrodzie(D, kopie, None, None, 8)
        self.assertEqual(st[:3], ["jaguarek", "perlowa_wydra", "jelonek_gaju"])
        self.assertEqual(st[3:6], ["posazek", "ognik", "swietlikowka"])
        # aktywny i pety na wyprawie nie stoją; kopie 0 = nieposiadany
        st = LP.w_zagrodzie(D, dict(kopie, perlowa_wydra=0), "jaguarek", None, 8, {"jelonek_gaju": True})
        self.assertNotIn("jaguarek", st)
        self.assertNotIn("perlowa_wydra", st)
        self.assertNotIn("jelonek_gaju", st)
        self.assertEqual(len(st), 8)
        # wybór ręczny w kolejności gracza, bez powtórzeń i obcych, najwyżej tyle, ile miejsc
        self.assertEqual(LP.w_zagrodzie(D, kopie, None, ["zoledziak", "zoledziak", "obcy", "palkus", "ognik"], 2),
                         ["zoledziak", "palkus"])
        self.assertEqual(LP.w_zagrodzie(D, kopie, None, [], 8), [])
        # tik: tylko całe Rybki, reszta czeka; długa przerwa nie daje zaległości
        self.assertEqual(LP.tik(D, 0, 0.3, 5), (1, 0.5))
        ile, r = LP.tik(D, 0.5, 0.3, 5)
        self.assertEqual((ile, round(r, 9)), (2, 0.0))
        self.assertEqual(LP.tik(D, 0, 1, 10 ** 6)[0], D["zagroda"]["tik_maks_s"])

    def test_3i_szesc_albo_osiem_znacznikow(self):
        """Mapa może mieć 6 albo 8 znaczników zagroda_miejsce_N: dane biorą tyle, ile jest; logika miejsc (2–8) od mapy
        nie zależy, a klient stawia najwyżej tyle modeli, ile znaczników."""
        stary = DP._znaczniki
        for n in (6, 8):
            def podmiana(sciezka, n=n):
                z = stary(sciezka)
                if "zagroda" in z:
                    m = z["zagroda"]["miejsca_petow"]
                    while len(m) < n:
                        m.append(dict(m[-1]))
                    z["zagroda"]["miejsca_petow"] = m[:n]
                return z
            DP._znaczniki = podmiana
            try:
                Dn = DP.podstawa()
            finally:
                DP._znaczniki = stary
            self.assertEqual(len(Dn["polozenia"]["miejsca_petow"]), n)
            self.assertEqual(LP.miejsca_zagrody(Dn, 4), 8)
        k = bez_komentarzy(KLIENT)
        self.assertIn("local miejsca = D.polozenia.miejsca_petow", k)
        self.assertIn("if i < #miejsca then", k)


class TestLuau(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.it, cls.Dl, cls.L = luau_logika()

    def wolaj(self, nazwa, *argi):
        return [LM.z_luau(x) for x in self.it.wywolaj(self.L.get(nazwa), [LM.do_luau(a) if not isinstance(a, LM.Tabela)
                                                                         else a for a in argi])]

    def test_3d_przypadki_wzorcowe(self):
        ok, n, bledy = self.it.wywolaj(self.L.get("sprawdzPrzypadki"), [self.Dl])
        self.assertTrue(ok, LM.z_luau(bledy))
        self.assertEqual(int(n), sum(len(v) for v in D["przypadki"].values()))
        it, Dl, Ll = luau_logika()
        Dl.get("przypadki").get("losuj").d[1.0].set("wynik", "jelonek_gaju")
        ok, _, bledy = it.wywolaj(Ll.get("sprawdzPrzypadki"), [Dl])
        self.assertFalse(ok)
        self.assertEqual(LM.z_luau(bledy), ["losuj #1"])

    def test_3e_losowanie_luau_jak_python(self):
        los = random.Random(3)
        for i, jp in enumerate(D["jajka"]):
            j = self.Dl.get("jajka").get(float(i + 1))
            for _ in range(2000):
                r = los.random()
                self.assertEqual(self.wolaj("losuj", self.Dl, j, r)[0], LP.losuj(D, jp, r), r)
            for n in range(15):
                for tryb in (None, "stala", "rosnaca"):
                    self.assertEqual(self.wolaj("cena", self.Dl, j, n, tryb)[0], LP.cena(D, jp, n, tryb), (n, tryb))
            for tryb in (None, "stala", "rosnaca"):
                self.assertEqual(self.wolaj("opisCeny", self.Dl, j, tryb)[0], LP.opis_ceny(D, jp, tryb), tryb)
            for _ in range(200):
                w = {x["id"]: los.choice([0, 1, 3, 8]) for x in D["jajka"] if los.random() < 0.7}
                for tryb in ("osobny", "wspolny"):
                    self.assertEqual(self.wolaj("kupione", self.Dl, j, w, tryb)[0], LP.kupione(D, jp, w, tryb), (w, tryb))

    def test_3f_zagroda_jak_python(self):
        los = random.Random(9)
        ids = [p["id"] for p in U["pety"]] + ["obcy"]
        for _ in range(200):
            kopie = {i: los.choice([0, 1, 2, 7]) for i in ids if los.random() < 0.6}
            akt = los.choice([None] + ids)
            wl = self.wolaj("wierszeZagrody", self.Dl, kopie, akt)[0]
            wp = LP.wiersze_zagrody(D, kopie, akt)
            self.assertEqual(wl if wl != {} else [], wp, (kopie, akt))


# ============================================================================================== 4. ekonomia
class TestEkonomii(unittest.TestCase):
    def test_4a_petla_jak_symulacja_lasu_i_pierwsze_jajko(self):
        import ekonomia_jajek as EJ
        import symulacja_lasu as SL
        DS = _modul_stanu("dane_stanu_test_petow", "dane.py")
        _, Ds = DS.dane_z_przypadkami()
        P = SL.przegrody()
        x0, przelot = SL.przybycie_i_przelot()

        class A:
            tempo = 1.0
        for k in Ds["klasy"]:
            a, b = random.Random("z-" + k), random.Random("z-" + k)
            for _ in range(3):
                os_czasu, wygrana = EJ.gracz(Ds, P, k, a, x0, przelot, po_strazniku=False, limit_min=SL.LIMIT_MIN)
                wzor = SL.jeden_gracz(Ds, P, k, b, A, x0, przelot)
                self.assertAlmostEqual(wygrana, wzor["czas"], places=6)
                self.assertEqual(len(os_czasu), wzor["walki"])
        pary = EJ.wszyscy_gracze(15, 2, z_wygrana=True)
        gracze = [o for o, _w in pary]
        c = U["jajka"][0]["cena"]
        stala = {"tryb": "stala", "cena": c["stala"]}
        T = EJ.tabela(gracze, [("s", stala),
                               ("p", {"tryb": "rosnaca", "start": c["start"], "krok": c["krok"], "maks": c["maks"]}),
                               ("k", {"tryb": "stala", "cena": c["kalkulator"]})])
        med = [m for m, _lo, _hi, _n in T["s"]]
        self.assertTrue(5.0 <= med[0] <= 10.0, "pierwsze jajko (cena stała): %.1f min (cel 5–10)" % med[0])
        rosn = [m for m, _lo, _hi, _n in T["p"]]
        self.assertGreater(rosn[2] - rosn[1], rosn[1] - rosn[0] - 1.0, "przełącznik „rosnaca”: kolejne nie częściej")
        self.assertGreater(T["k"][0][0], 10.0, "cena kalkulatora daje pierwsze jajko później niż 10 min")
        # do wygranej ze Strażnikiem Gaju gracz kupi kilka jajek po stałej cenie (premie petów poza symulacją)
        ile = sorted(EJ.jajek_do(o, stala, t) for o, t in pary if t is not None)
        self.assertTrue(4 <= ile[len(ile) // 2] <= 20, ile)

    def test_4c_skille_w_walce(self):
        # D-101: liczby z silnika (skille_petow.py) — pospolite i zwykłe prawie nic nie zmieniają, legendarne wyraźnie
        # pomagają, ale bez peta strażnicy dalej są do pokonania (żaden pet nie jest obowiązkowy)
        import skille_petow as SK
        T, Ds = SK.czesc1(D, 120)
        baza = T["bez peta"]

        def zysk(nazwa, potwor):
            return sum(T[nazwa][(potwor, k, L)] - baza[(potwor, k, L)] for k in Ds["klasy"]
                       for L in (dict((x[0], x[1]) for x in SK.STRAZNICY)[potwor] - 1,
                                 dict((x[0], x[1]) for x in SK.STRAZNICY)[potwor])) / 6.0
        for p in D["pety"]:
            z = zysk(p["nazwa"], "straznik_lasu")
            if p["rzadkosc"] in ("pospolity", "zwykly"):
                self.assertLess(z, 4.0, (p["id"], z))
            if p["rzadkosc"] == "legendarny":
                self.assertGreater(z, 5.0, (p["id"], z))
        for k in Ds["klasy"]:
            self.assertGreater(baza[("straznik_lasu", k, 10)], 20.0, k)

    def test_4b_pierwsze_jajko_bagna(self):
        import ekonomia_jajek as EJ
        gracze, poziomy = EJ.wszyscy_gracze_bagna(12, 2)
        self.assertGreater(len(gracze), 30)
        self.assertTrue(9 <= sorted(poziomy)[len(poziomy) // 2] <= 13, "wejście do Bagna ok. 10.–12. poziomu")
        c = next(j for j in U["jajka"] if j["kraina"] == "bagno")["cena"]
        T = EJ.tabela(gracze, [("s", {"tryb": "stala", "cena": c["stala"]}),
                               ("p", {"tryb": "rosnaca", "start": c["start"], "krok": c["krok"], "maks": c["maks"]})])
        med = [m for m, _lo, _hi, _n in T["s"]]
        self.assertTrue(5.0 <= med[0] <= 10.0, "pierwsze jajko Bagna (cena stała): %.1f min Bagna (cel 5–10)" % med[0])
        rosn = [m for m, _lo, _hi, _n in T["p"]]
        self.assertGreater(rosn[2] - rosn[1], rosn[1] - rosn[0] - 1.5, "przełącznik „rosnaca”: kolejne nie częściej")


# ============================================================================================== 5. serwery offline
class _Wywolanie:
    """BindableFunction:Invoke w atrapie — woła OnInvoke drugiej strony (pierwszy wynik)."""

    def __init__(self, sw, inst):
        self.sw, self.inst = sw, inst

    def __call__(self, _s, *argi):
        fn = self.inst.t.get("OnInvoke")
        if fn is None:
            return None
        w = self.sw.wolaj(fn, *argi)
        return w[0] if w else None


@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py — Luau nie wykonany")
class TestSerweraOffline(unittest.TestCase):
    """Prawdziwy SerwerPetow i prawdziwy SerwerStanu w jednym interpreterze z atrapą Roblox."""

    def uruchom(self, stan_gracza=True, zloto=0, tryb=None, cena=None):
        import atrapa_roblox as AR
        dane = DANE_LUAU
        if tryb:   # przełącznik licznika ceny w danych (jak zmiana ustawienia.json → dane_petow.py)
            stary = 'licznik_ceny = { tryb = "%s" }' % D["licznik_ceny"]["tryb"]
            self.assertEqual(dane.count(stary), 1)
            dane = dane.replace(stary, 'licznik_ceny = { tryb = "%s" }' % tryb)
        if cena:   # przełącznik trybu ceny wszystkich jajek (przypadki wzorcowe podają tryb wprost — zgodność zostaje)
            stary = 'cena = { tryb = "stala",'
            self.assertEqual(dane.count(stary), len(D["jajka"]))
            dane = dane.replace(stary, 'cena = { tryb = "%s",' % cena)
        ZBS = _modul_stanu("zbuduj_stanu_test_petow", "zbuduj.py")
        sw = AR.Swiat()
        g = sw.it.globalne.z
        g["task"].set("wait", lambda *a: None)
        rnd = random.Random(5)
        losy = LM.Tabela()

        def nowy(*_):
            t = LM.Tabela()
            t.set("NextNumber", lambda _s: rnd.random())
            return t
        losy.set("new", nowy)
        g["Random"] = losy
        self.usuniete = AR.Zdarzenie(sw)
        sw.workspace.t.set("ChildRemoved", self.usuniete.t)
        self.inne = {}
        if stan_gracza:
            k, inne = AR.kontener_stanu(sw, {"DaneStanu": czytaj(STAN, "zrodla", "DaneStanu.luau"),
                                             "LogikaStanu": czytaj(STAN, "zrodla", "LogikaStanu.luau")}, ZBS.INNE)
            for o in inne.values():
                if o.klasa == "BindableFunction":
                    o.t.set("Invoke", _Wywolanie(sw, o))
            shared = AR.Inst(sw, "Shared", "Folder", sw.replicated)
            sw.modul(shared, "ClassData", wartosc=LM.do_luau({"Classes": []}))
            self.inne = inne
            self.kstan = k
            self.gracz = sw.gracz("Gracz1", {"Level": 1, "XP": 0, "Gold": zloto, "Gems": 0})
            sw.it.wykonaj(czytaj(STAN, "zrodla", "SerwerStanu.server.luau"), "SerwerStanu.server.luau")
        else:
            self.gracz = sw.gracz("Gracz1", {"Gold": zloto})
        kp = AR.Inst(sw, "PetyProba", "Folder", sw.workspace)
        kp.ustaw("Wygenerowane", True)
        f = {n: AR.Inst(sw, n, "Folder", kp) for n in ("Moduly", "Zdalne", "Sygnaly", "Punkty", "Zagroda")}
        sw.modul(f["Moduly"], "DanePetow", dane)
        sw.modul(f["Moduly"], "LogikaPetow", LOGIKA)
        ev = AR.Inst(sw, "ZdarzeniaPetow", "RemoteEvent", f["Zdalne"])
        ev.na_serwer = AR.Zdarzenie(sw)
        ev.t.set("OnServerEvent", ev.na_serwer.t)
        ev.t.set("FireClient", lambda _s, gracz, *a: sw.do_klienta.append((gracz, [AR.py(x) for x in a])))
        self.ster = AR.Inst(sw, "SterowanieSerwera", "BindableFunction", f["Sygnaly"])
        self.prompty = {}
        for folder, nazwa in [("Punkty", j["punkt_e"]) for j in D["jajka"]] + [("Zagroda", "E wybor")]:
            cz = AR.Inst(sw, nazwa, "BasePart", f[folder])
            pp = AR.Inst(sw, "Podpowiedz", "ProximityPrompt", cz)
            pp.t.set("Enabled", False)
            wyzw = AR.Zdarzenie(sw)
            pp.t.set("Triggered", wyzw.t)
            self.prompty[nazwa] = (pp, wyzw)
        skrypt = LM.Tabela()
        skrypt.set("Parent", kp.t)
        g["script"] = skrypt
        sw.it.wykonaj(SERWER, "SerwerPetow.server.luau")
        self.sw, self.kp, self.ev = sw, kp, ev
        return sw

    def atr(self, n):
        v = self.gracz.atrybuty.get(n)
        return int(v) if isinstance(v, float) and v == int(v) else v

    def od_serwera(self, polecenie):
        return [a for gr, a in self.sw.do_klienta if a and a[0] == polecenie]

    def e_jajka(self, nr=0, stoi_przy=None):
        """Prawdziwe E przy inkubatorze jajka nr (gracz stoi przy nim — serwer sprawdza zasięg; stoi_przy = nr innego
        inkubatora, przy którym gracz naprawdę stoi — podpowiedź odpalona „z daleka”)."""
        e = D["jajka"][nr if stoi_przy is None else stoi_przy]["polozenie"]["e"]
        self.postaw(e[0] + 1.5, e[2] - 1.0)
        self.prompty[D["jajka"][nr]["punkt_e"]][1].odpal(self.gracz.t)

    def hak(self, *argi):
        w = self.sw.wolaj(self.ster.t.get("OnInvoke"), *[a if isinstance(a, LM.Tabela) else LM.do_luau(a) for a in argi])
        return LM.z_luau(w[0]) if w else None

    def postaw(self, x, z):
        import atrapa_roblox as AR
        postac = AR.Inst(self.sw, "Postac", "Model")
        hrp = AR.Inst(self.sw, "HumanoidRootPart", "BasePart", postac)
        hrp.t.set("Position", LM.do_luau({"X": x, "Y": 3, "Z": z}))
        self.gracz.t.set("Character", postac.t)

    def test_5a_start(self):
        self.uruchom()
        n = sum(len(v) for v in D["przypadki"].values())
        self.assertEqual(self.kp.atrybuty["SerwerPetowGotowy"], True)
        self.assertEqual(self.kp.atrybuty["ZgodnoscLogikiPetow"], "OK %d/%d" % (n, n))
        for j in D["jajka"]:
            self.assertTrue(self.prompty[j["punkt_e"]][0].t.get("Enabled"), j["id"])
            self.assertEqual(self.atr(j["atrybuty"]["cena"]), j["cena"]["stala"], j["id"])
            self.assertEqual(self.atr(j["atrybuty"]["kupione"]), 0, j["id"])
        self.assertTrue(self.prompty["E wybor"][0].t.get("Enabled"), "bez MiasteczkoBazarGra — zapasowe E włączone")
        self.assertEqual(self.sw.ostrzezenia, [])

    def test_5p_zapis_postepu_czeka_na_wczytanie_profilu(self):
        # D-110 (19.11.2026): gracz wchodzi, StanGracza jeszcze wczytuje profil (StanGraczaWczytany = false — Pety
        # i Modyfikatory odmawiają); pety nie ustawiają skilla od razu, tylko gdy atrybut zmieni się na true
        self.uruchom()
        n0 = self.kp.atrybuty.get("LicznikModyfikatorow", 0)
        g2 = self.sw.gracz("Gracz2", {"Level": 1, "XP": 0, "Gold": 0, "Gems": 0, "StanGraczaWczytany": False})
        self.sw.dolaczyl.odpal(g2.t)
        self.assertEqual(self.kp.atrybuty.get("LicznikModyfikatorow", 0), n0, "w trakcie wczytywania nic nie wysłane")
        self.assertEqual(g2.atrybuty.get(D["jajka"][0]["atrybuty"]["cena"]), D["jajka"][0]["cena"]["stala"])
        g2.ustaw("StanGraczaWczytany", True)
        self.assertEqual(self.kp.atrybuty.get("LicznikModyfikatorow", 0), n0 + 1)
        self.assertEqual(self.kp.atrybuty.get("OstatniModyfikator"), "Gracz2:brak")
        self.assertEqual([o for o in self.sw.ostrzezenia if "Gracz2" in o or "Modyfikatory" in o], [])

    def test_5b_bez_zlota_odmowa_z_kwota(self):
        self.uruchom(zloto=120)
        self.e_jajka()
        odm = self.od_serwera("odmowa")
        self.assertEqual(odm, [["odmowa", "Brakuje ci 180 Rybek (masz 120, jajko kosztuje 300)", "za_malo"]])
        self.assertEqual((self.atr("Gold"), self.atr("PetyLiczba"), self.atr("PetAktywny")), (120, 0, None))
        self.assertEqual(self.od_serwera("wyklucie"), [])
        # od razu można spróbować znowu (blokada zdjęta po odmowie)
        self.e_jajka()
        self.assertEqual(len(self.od_serwera("odmowa")), 2)

    def test_5c0_cena_stala(self):
        # domyślnie (decyzja 17.11): każde jajko leśne za 300, cena nie rośnie z zakupami
        self.uruchom(zloto=700)
        c = U["jajka"][0]["cena"]["stala"]
        self.e_jajka()
        info = self.od_serwera("wyklucie")[-1][1]
        self.assertEqual((info["cena"], info["nastepna"]), (c, c))
        self.assertEqual(self.atr(D["jajka"][0]["atrybuty"]["cena"]), c)
        self.sw.krok(D["wyklucie"]["blokada_s"] + 0.1)
        self.e_jajka()
        self.assertEqual((self.atr("Gold"), self.atr(D["jajka"][0]["atrybuty"]["cena"])), (700 - 2 * c, c))
        self.sw.krok(D["wyklucie"]["blokada_s"] + 0.1)
        self.e_jajka()
        odm = self.od_serwera("odmowa")[-1]
        self.assertNotEqual(3 * c - 700, 1)
        self.assertEqual(odm[1:], ["Brakuje ci %d Rybek (masz %d, jajko kosztuje %d)" % (3 * c - 700, 700 - 2 * c, c),
                                   "za_malo"])
        self.assertEqual((self.atr("PetyLiczba"), self.atr(D["jajka"][0]["atrybuty"]["kupione"])), (2, 2))
        self.assertEqual(self.sw.ostrzezenia, [])

    def test_5c1_dwa_inkubatory_gracz_przy_drugim(self):
        # 17.11 (próba w Studio): E przy inkubatorze Bagna — serwer kupuje jajko TEJ podpowiedzi i sam sprawdza, że
        # gracz przy niej stoi; podpowiedź odpalona spod drugiego inkubatora (albo bez postaci) → odmowa, Złoto bez zmian
        self.uruchom(zloto=3000)
        las, bagno = D["jajka"][:2]
        self.e_jajka(1)
        info = self.od_serwera("wyklucie")[-1][1]
        self.assertEqual((info["jajko"], info["cena"]), (bagno["id"], bagno["cena"]["stala"]))
        self.assertIn(info["pet"], bagno["pula"])
        self.assertEqual((self.atr(bagno["atrybuty"]["kupione"]), self.atr(las["atrybuty"]["kupione"])), (1, 0))
        zloto = self.atr("Gold")
        self.assertEqual(zloto, 3000 - bagno["cena"]["stala"])
        self.sw.krok(D["wyklucie"]["blokada_s"] + 0.1)
        self.e_jajka(1, stoi_przy=0)          # podpowiedź Bagna, gracz w lesie
        self.assertEqual(self.od_serwera("odmowa")[-1][1:], [U["teksty"]["za_daleko_jajko"], "za_daleko_jajko"])
        self.e_jajka(0, stoi_przy=1)          # podpowiedź lasu, gracz w Bagnie
        self.assertEqual(self.od_serwera("odmowa")[-1][2], "za_daleko_jajko")
        self.gracz.t.set("Character", None)   # bez postaci (np. w trakcie odrodzenia)
        self.prompty[bagno["punkt_e"]][1].odpal(self.gracz.t)
        self.assertEqual(self.od_serwera("odmowa")[-1][2], "za_daleko_jajko")
        self.assertEqual((self.atr("Gold"), self.atr(bagno["atrybuty"]["kupione"]), self.atr(las["atrybuty"]["kupione"])),
                         (zloto, 1, 0))
        # haczyk testowy (próby w Play) kupuje bez sprawdzania zasięgu
        self.assertTrue(self.hak("kup", self.gracz.t, las["id"], 0.1)["ok"])
        self.assertEqual(self.sw.ostrzezenia, [])

    def test_5c_kupno_e_podwojne_naraz_i_cena_rosnaca(self):
        self.uruchom(zloto=1200, cena="rosnaca")   # przełącznik „rosnaca” w danych
        c = U["jajka"][0]["cena"]
        self.e_jajka()
        self.e_jajka()  # drugi E w tej samej chwili (w trakcie wyklucia)
        wyk = self.od_serwera("wyklucie")
        self.assertEqual(len(wyk), 1)
        info = wyk[0][1]
        self.assertEqual((info["cena"], info["nastepna"], info["nowy"], info["kopie"], info["zloto"]),
                         (c["start"], c["start"] + c["krok"], True, 1, 1200 - c["start"]))
        self.assertEqual(self.od_serwera("odmowa")[0][2], "trwa_wyklucie")
        self.assertEqual((self.atr("Gold"), self.atr("PetyLiczba"), self.atr("PetAktywny")),
                         (1200 - c["start"], 1, info["pet"]))
        self.assertEqual(self.atr(D["jajka"][0]["atrybuty"]["cena"]), c["start"] + c["krok"])
        # po wykluciu: drugie jajko po nowej cenie, trzecie — za mało Złota
        self.sw.krok(D["wyklucie"]["blokada_s"] + 0.1)
        self.e_jajka()
        self.assertEqual(self.atr("Gold"), 1200 - 2 * c["start"] - c["krok"])
        self.sw.krok(D["wyklucie"]["blokada_s"] + 0.1)
        self.e_jajka()
        odm = self.od_serwera("odmowa")[-1]
        self.assertEqual(odm[2], "za_malo")
        self.assertIn("kosztuje %d" % (c["start"] + 2 * c["krok"]), odm[1])
        self.assertEqual(self.atr("PetyLiczba"), 2)
        self.assertEqual(self.kp.atrybuty["LicznikZakupow"], 2)
        self.assertEqual(self.sw.ostrzezenia, [])

    def test_5d_nieznane_jajko_i_zloto_nigdy_ponizej_zera(self):
        self.uruchom(zloto=5000)
        self.assertEqual(self.hak("kup", self.gracz.t, "jajko_smoka")["powod"], "nieznane_jajko")
        self.assertEqual(self.hak("kup", self.gracz.t, 12345)["powod"], "nieznane_jajko")
        kupione = 0
        for _ in range(40):
            w = self.hak("kup", self.gracz.t, "jajko_lesne")
            self.hak("zwolnij", self.gracz.t)
            kupione += 1 if w["ok"] else 0
            self.assertGreaterEqual(self.atr("Gold"), 0)
        self.assertEqual(self.atr("PetyLiczba"), kupione)
        ceny = sum(LP.cena(D, D["jajka"][0], n) for n in range(kupione))
        self.assertEqual(self.atr("Gold"), 5000 - ceny)
        self.assertLess(5000 - ceny, LP.cena(D, D["jajka"][0], kupione), "kupował, dopóki starczało")

    def test_5e_wymuszony_los_wybor_odstawienie_czekaj(self):
        self.uruchom(zloto=5000)
        w = self.hak("kup", self.gracz.t, "jajko_lesne", 0.995)   # r = 0,995 → legendarny (ostatnie 2%)
        self.assertEqual((w["pet"], w["nowy"]), ("jelonek_gaju", True))
        self.hak("zwolnij", self.gracz.t)
        self.assertEqual(self.hak("kup", self.gracz.t, "jajko_lesne", 0.1)["pet"], "zoledziak")
        self.assertEqual(self.atr("PetAktywny"), "jelonek_gaju", "pierwszy pet idzie za graczem")
        # wybór: daleko od zagrody → odmowa; przy zagrodzie → zmiana; nieposiadany → odmowa
        e = D["polozenia"]["zagroda_e"]
        self.postaw(e[0] + 200, e[2])
        self.ev.na_serwer.odpal(self.gracz.t, "wybierz", "zoledziak")
        self.assertEqual(self.od_serwera("odmowa")[-1][2], "za_daleko")
        self.postaw(e[0] + 3, e[2] - 2)
        self.sw.krok(1)
        self.ev.na_serwer.odpal(self.gracz.t, "wybierz", "zoledziak")
        self.assertEqual(self.atr("PetAktywny"), "zoledziak")
        self.assertEqual(self.od_serwera("wybrany")[-1], ["wybrany", "zoledziak"])
        lista = self.od_serwera("lista")[-1][1]
        self.assertEqual([(x["pet"], x["kopie"], x["aktywny"]) for x in lista["wiersze"]],
                         [("zoledziak", 1, True), ("jelonek_gaju", 1, False)])
        self.sw.krok(1)
        self.ev.na_serwer.odpal(self.gracz.t, "wybierz", "lisciolis")
        self.assertEqual(self.od_serwera("odmowa")[-1][2], "nie_masz")
        self.sw.krok(1)
        self.ev.na_serwer.odpal(self.gracz.t, "wybierz", "x" * 300)
        self.assertEqual(self.atr("PetAktywny"), "zoledziak")
        self.sw.krok(1)
        self.ev.na_serwer.odpal(self.gracz.t, "odstaw")
        self.assertIsNone(self.atr("PetAktywny"))
        # „czekaj” (walka, przelot…) — atrybut dla innych klientów
        self.ev.na_serwer.odpal(self.gracz.t, "czekaj", True)
        self.assertTrue(self.atr(U["atrybuty_gracza"]["czeka"]))
        self.ev.na_serwer.odpal(self.gracz.t, "czekaj", "tak")
        self.assertIsNone(self.atr(U["atrybuty_gracza"]["czeka"]))
        # limit zdarzeń: dwie prośby o listę naraz → jedna odpowiedź
        przed = len(self.od_serwera("lista"))
        self.sw.krok(1)
        self.ev.na_serwer.odpal(self.gracz.t, "lista")
        self.ev.na_serwer.odpal(self.gracz.t, "lista")
        self.assertEqual(len(self.od_serwera("lista")) - przed, 1)
        self.ev.na_serwer.odpal(self.gracz.t, 42.0, 43.0)  # śmieci — pominięte
        self.assertEqual(self.sw.ostrzezenia, [])

    def test_5e2_jajko_bagna_cena_stala(self):
        self.uruchom(zloto=1500)
        las, bagno = D["jajka"][:2]
        cl, cb = las["cena"]["stala"], bagno["cena"]["stala"]
        for _ in range(2):                     # dwa jajka leśne: ceny obu jajek bez zmian
            self.e_jajka(0)
            self.sw.krok(D["wyklucie"]["blokada_s"] + 0.1)
        self.assertEqual((self.atr(las["atrybuty"]["cena"]), self.atr(bagno["atrybuty"]["cena"])), (cl, cb))
        self.e_jajka(1)                        # E przy inkubatorze Bagna
        info = self.od_serwera("wyklucie")[-1][1]
        self.assertEqual((info["jajko"], info["cena"], info["nastepna"]), (bagno["id"], cb, cb))
        self.assertIn(info["pet"], bagno["pula"])
        self.assertEqual(self.atr("Gold"), 1500 - 2 * cl - cb)
        self.assertEqual((self.atr(las["atrybuty"]["kupione"]), self.atr(bagno["atrybuty"]["kupione"])), (2, 1))
        self.assertEqual((self.atr(las["atrybuty"]["cena"]), self.atr(bagno["atrybuty"]["cena"])), (cl, cb))
        # drugie jajko Bagna: za mało Złota — odmowa z kwotą braku
        self.sw.krok(D["wyklucie"]["blokada_s"] + 0.1)
        self.assertEqual(self.hak("kup", self.gracz.t, bagno["id"], 0.995)["powod"], "za_malo")
        self.assertNotEqual(cb - self.atr("Gold"), 1)
        self.assertEqual(self.od_serwera("odmowa")[-1][1], "Brakuje ci %d Rybek (masz %d, jajko kosztuje %d)" % (
            cb - self.atr("Gold"), self.atr("Gold"), cb))
        self.assertEqual(self.sw.ostrzezenia, [])

    def test_5e2b_jajko_bagna_licznik_osobny_przy_rosnacej(self):
        self.uruchom(zloto=2500, cena="rosnaca")
        las, bagno = D["jajka"][:2]
        cl, cb = las["cena"], bagno["cena"]
        for _ in range(2):                     # dwa jajka leśne: cena leśnego rośnie, Bagna — nie
            self.e_jajka(0)
            self.sw.krok(D["wyklucie"]["blokada_s"] + 0.1)
        self.assertEqual(self.atr(las["atrybuty"]["cena"]), cl["start"] + 2 * cl["krok"])
        self.assertEqual(self.atr(bagno["atrybuty"]["cena"]), cb["start"])
        self.e_jajka(1)
        info = self.od_serwera("wyklucie")[-1][1]
        self.assertEqual((info["jajko"], info["cena"], info["nastepna"]), (bagno["id"], cb["start"], cb["start"] + cb["krok"]))
        self.assertEqual(self.atr(las["atrybuty"]["cena"]), cl["start"] + 2 * cl["krok"], "Bagno nie podnosi ceny lasu")
        n = sum(len(v) for v in D["przypadki"].values())
        self.assertEqual(self.kp.atrybuty["ZgodnoscLogikiPetow"], "OK %d/%d" % (n, n), "przełącznik nie psuje zgodności")
        self.assertEqual(self.sw.ostrzezenia, [])

    def test_5e3_licznik_wspolny_po_przelaczeniu(self):
        self.uruchom(zloto=5000, tryb="wspolny", cena="rosnaca")
        las, bagno = D["jajka"][:2]
        cl, cb = las["cena"], bagno["cena"]
        self.e_jajka(0)
        self.assertEqual(self.atr(bagno["atrybuty"]["cena"]), cb["start"] + cb["krok"], "wspólny: las podnosi Bagno")
        self.sw.krok(D["wyklucie"]["blokada_s"] + 0.1)
        w = self.hak("kup", self.gracz.t, bagno["id"], 0.995)
        self.assertEqual((w["pet"], w["cena"]), ("perlowa_wydra", cb["start"] + cb["krok"]))
        self.assertEqual(self.atr(las["atrybuty"]["cena"]), cl["start"] + 2 * cl["krok"])
        self.assertEqual((self.atr(las["atrybuty"]["kupione"]), self.atr(bagno["atrybuty"]["kupione"])), (1, 1))
        self.assertEqual(self.atr("Gold"), 5000 - cl["start"] - cb["start"] - cb["krok"])
        self.assertEqual(self.sw.ostrzezenia, [])

    def test_5f_premia_peta_przy_lupie(self):
        self.uruchom(zloto=1000)
        self.hak("kup", self.gracz.t, "jajko_lesne", 0.9)   # r = 0,9 → epicka Świetlikówka (+5% doświadczenia)
        self.assertEqual(self.atr("PetAktywny"), "swietlikowka")
        lup = {"zloto": 20, "doswiadczenie": 40, "tokeny_krainy": 0, "gemy": 0, "shard_ewolucji": 0, "kraina": "las"}
        fn = self.inne["PrzyznajLup"].t.get("OnInvoke")
        self.sw.wolaj(fn, self.gracz.t, LM.do_luau({"lup": lup, "wynik": "wygrana", "czas": 0, "zrodlo": "LasPasGra"}))
        self.sw.krok(10)
        premie = [a for _g, a in self.sw.do_klienta if a and a[0] == "premia"]
        self.assertEqual(premie, [["premia", 0, 2, "swietlikowka"]], "premia tylko ze skilla (Modyfikatory), bez podwójnej")

    def test_5i_modyfikatory_stanu_gracza(self):
        # D-101: skill aktywnego peta trafia do StanGracza/Sygnaly/Modyfikatory jako źródło "pety" (przy wejściu
        # gracza, po zakupie, wyborze, odstawieniu); złożenie = dokładnie modyfikator peta; premia do łupu tylko z niego
        self.uruchom(zloto=5000)
        # stan gracza (18.11): „szczęście początkującego” to osobne źródło do pierwszej wygranej — tu sprawdzamy tylko peta
        self.kstan.ustaw("SzczesciePoczatkujacego", False)
        zr = U["stan_gracza"]["zrodlo_modyfikatora"]
        st = self.hak("stan", self.gracz.t)["modyfikatory"]
        self.assertTrue(st["ok"])
        self.assertNotIn(zr, st.get("zrodla") or [], "bez peta — źródło zdjęte (i przejęte) już przy wejściu")
        self.assertEqual(self.kp.atrybuty["LicznikModyfikatorow"], 1)
        w = self.hak("kup", self.gracz.t, "jajko_bagienne", 0.9)  # r = 0,9 → epicki Ognik: podpalenie przy ciosie
        self.assertEqual(w["pet"], "ognik")
        m = self.hak("stan", self.gracz.t)["modyfikatory"]
        self.assertEqual(m["zrodla"], [zr])
        self.assertEqual((m["pasywki"], m["zaklecie"]), (LP.mod_peta(D, "ognik")["pasywki"], "podpalenie"))
        self.assertEqual((m["lup"]["zloto"], m["lup"]["doswiadczenie"]), (0, 0))
        # bohater walki (stan gracza) dostaje premie żywiołu klasy gracza
        self.hak("zwolnij", self.gracz.t)
        self.assertEqual(self.hak("kup", self.gracz.t, "jajko_lesne", 0.995)["pet"], "jelonek_gaju")
        e = D["polozenia"]["zagroda_e"]
        self.postaw(e[0] + 2, e[2] - 1)
        self.sw.krok(1)
        self.ev.na_serwer.odpal(self.gracz.t, "wybierz", "jelonek_gaju")
        m = self.hak("stan", self.gracz.t)["modyfikatory"]
        self.assertEqual((m["procent"], m["pasywki"]), ({"Strength": 0.2}, LP.mod_peta(D, "jelonek_gaju")["pasywki"]))
        self.assertAlmostEqual(m["lup"]["zloto"], 0.05)
        self.sw.krok(1)
        self.ev.na_serwer.odpal(self.gracz.t, "odstaw")
        m = self.hak("stan", self.gracz.t)["modyfikatory"]
        self.assertNotIn(zr, m.get("zrodla") or [])
        self.assertEqual((m["lup"]["zloto"], m["lup"]["doswiadczenie"]), (0, 0))
        self.assertFalse(m["pasywki"])   # pusta tabela z Luau
        # łup po odstawieniu: bez premii (dawna premia z profilu już się nie liczy — źródło przejęte)
        lup = {"zloto": 100, "doswiadczenie": 40, "tokeny_krainy": 0, "gemy": 0, "shard_ewolucji": 0, "kraina": "las"}
        fn = self.inne["PrzyznajLup"].t.get("OnInvoke")
        self.sw.wolaj(fn, self.gracz.t, LM.do_luau({"lup": lup, "wynik": "wygrana", "czas": 0, "zrodlo": "LasPasGra"}))
        self.sw.krok(10)
        self.assertEqual([a for _g, a in self.sw.do_klienta if a and a[0] == "premia"], [])
        self.assertEqual(self.sw.ostrzezenia, [])

    def test_5g_bez_stanu_gracza(self):
        self.uruchom(stan_gracza=False, zloto=5000)
        self.e_jajka()
        odm = self.od_serwera("odmowa")
        self.assertEqual(odm, [["odmowa", U["teksty"]["brak_stanu"], "brak_stanu"]])
        self.assertEqual(self.atr("Gold"), 5000)
        self.ev.na_serwer.odpal(self.gracz.t, "lista")
        self.assertEqual(self.od_serwera("lista")[-1][1], {"brak": True, "tekst": U["teksty"]["brak_stanu"]})
        self.assertEqual(self.sw.ostrzezenia, [])

    # ------------------------------------------------------------------ zagroda: Rybki (25.11.2026)
    def kup_las(self, *losy):
        for r in losy:
            w = self.hak("kup", self.gracz.t, "jajko_lesne", r)
            self.assertTrue(w and w.get("ok"), w)
            self.hak("zwolnij", self.gracz.t)

    def zagroda(self):
        return self.hak("zagroda", self.gracz.t)

    def test_5j_zagroda_daje_rybki_aktywny_nie(self):
        """Pety stojące w zagrodzie dają Rybki co tik_s przez StanGracza Pety("przychod"); pet za graczem nie stoi
        w zagrodzie; dopisane tylko całe Rybki, ułamek czeka na następny raz."""
        Z = D["zagroda"]
        self.uruchom(zloto=5000)
        self.kup_las(0.0, 0.95, 0.99)            # Żołędziak (idzie za graczem), Świetlikówka, Jelonek Gaju
        self.assertEqual(self.atr("PetAktywny"), "zoledziak")
        st = self.zagroda()
        self.assertTrue(st["wczytany"])
        self.assertEqual((st["stan"]["poziom"], st["stan"]["miejsc"], st["stan"]["stoja"], st["stan"]["reczny"]),
                         (1, Z["poziomy"][0]["miejsc"], ["jelonek_gaju", "swietlikowka"], False))
        s = LP.stawka(D, "jelonek_gaju") + LP.stawka(D, "swietlikowka")
        self.assertAlmostEqual(st["stan"]["stawka_s"], s)
        zloto0 = self.atr("Gold")
        self.sw.krok(Z["tik_s"])                 # pierwszy tik: tylko punkt startu (bez zaległości)
        self.assertEqual(self.atr("Gold"), zloto0)
        self.sw.krok(Z["tik_s"] * 12)            # 60 s
        oczek = int(s * Z["tik_s"] * 12 + 1e-9)
        self.assertEqual(self.atr("Gold"), zloto0 + oczek)
        plusy = self.od_serwera("zagroda_plus")
        self.assertEqual(sum(a[1] for a in plusy), oczek)
        self.assertEqual(self.kstan.atrybuty.get("LicznikPrzychodow"), len(plusy))
        # aktywny pet zmienia się na Jelonka: Jelonek wychodzi z zagrody, wchodzi Żołędziak (wybór domyślny)
        self.assertTrue(self.hak("wybierz", self.gracz.t, "jelonek_gaju", True)["ok"])
        st = self.zagroda()["stan"]
        self.assertEqual(st["stoja"], ["swietlikowka", "zoledziak"])
        self.assertEqual(self.od_serwera("lista")[-1][1]["zagroda"]["stoja"], ["swietlikowka", "zoledziak"])
        # bez przychodu offline i bez zaległości po przerwie serwera: dt przycięte do tik_maks_s
        self.sw.zadania.clear()
        self.sw.krok(600)
        zl = self.atr("Gold")
        w = self.hak("nalicz", self.gracz.t)
        s2 = LP.stawka(D, "swietlikowka") + LP.stawka(D, "zoledziak")
        reszta = self.zagroda()["reszta"]
        self.assertEqual(self.atr("Gold") - zl, w or 0)
        self.assertLessEqual(self.atr("Gold") - zl, int(s2 * Z["tik_maks_s"] + 1))
        self.assertLess(reszta, 1)
        self.assertEqual(self.sw.ostrzezenia, [])

    def test_5k_miejsca_ulepszenie_za_rybki(self):
        """Więcej miejsc u opiekunki: cena z poziomu, Rybki przez WydajZloto (licznik ulepszeń = poziom), za mało =
        odmowa z kwotą bez zmian, najwyższy poziom = odmowa; z daleka — odmowa; pety ponad miejsca nic nie dają."""
        Z = D["zagroda"]
        poz = Z["poziomy"]
        self.uruchom(zloto=300 * 6)
        self.kup_las(0.0, 0.6, 0.8, 0.95, 0.99)  # pięć petów lasu, pierwszy za graczem → 4 chętne do zagrody
        self.assertEqual(self.atr("Gold"), 300)
        st = self.zagroda()["stan"]
        self.assertEqual(len(st["stoja"]), poz[0]["miejsc"], "pety ponad liczbę miejsc nie stoją")
        # z daleka: odmowa
        e = D["polozenia"]["zagroda_e"]
        self.postaw(e[0] + 200, e[2])
        self.ev.na_serwer.odpal(self.gracz.t, "ulepsz_zagrode")
        self.assertEqual(self.od_serwera("odmowa")[-1][2], "za_daleko")
        # za mało Rybek
        w = self.hak("ulepsz", self.gracz.t)
        self.assertEqual((w["ok"], w["powod"]), (False, "za_malo"))
        self.assertEqual(w["tekst"], LP.tekst_braku_ulepszenia(D, poz[1]["cena"] - 300, 300, poz[1]["cena"]))
        self.assertEqual(self.atr("Gold"), 300)
        # po kolei do najwyższego poziomu (prawdziwe zdarzenie od klienta przy zagrodzie)
        self.postaw(e[0] + 3, e[2] - 2)
        for i in range(1, len(poz)):
            self.gracz.ustaw("Gold", poz[i]["cena"] + 7)
            self.sw.krok(1)
            self.ev.na_serwer.odpal(self.gracz.t, "ulepsz_zagrode")
            self.assertEqual(self.atr("Gold"), 7, i)
            self.assertEqual(self.od_serwera("zagroda_ulepszona")[-1], ["zagroda_ulepszona", poz[i]["miejsc"]])
            st = self.zagroda()["stan"]
            self.assertEqual((st["poziom"], st["miejsc"]), (i + 1, poz[i]["miejsc"]))
        self.assertEqual(len(st["stoja"]), 4, "4 chętne pety, 8 miejsc — stoją wszystkie")
        self.assertNotIn("cena", st)
        self.gracz.ustaw("Gold", 10 ** 6)
        w = self.hak("ulepsz", self.gracz.t)
        self.assertEqual((w["ok"], w["powod"]), (False, "max"))
        self.assertEqual(self.atr("Gold"), 10 ** 6)
        stan = self.hak("stan", self.gracz.t)["pety"]
        self.assertEqual(stan["wydatki"][Z["cel_ulepszenia"]], len(poz) - 1)
        self.assertEqual(self.kp.atrybuty.get("LicznikUlepszen"), len(poz) - 1)
        self.assertEqual(self.sw.ostrzezenia, [])

    def test_5l_wybor_do_zagrody_i_zapis(self):
        """„Do zagrody” / „Z zagrody” (wybór ręczny w DanePakietu), pet za graczem nie wchodzi do zagrody, pełna zagroda,
        „Najrzadsze” wraca do wyboru domyślnego; po ponownym wczytaniu profilu wybór zostaje."""
        self.uruchom(zloto=300 * 4)
        self.kup_las(0.0, 0.6, 0.8, 0.95)        # Żołędziak (za graczem), Ślimak, Liściolis, Świetlikówka
        self.assertEqual(self.zagroda()["stan"]["stoja"], ["swietlikowka", "lisciolis"])
        w = self.hak("zagroda_zmien", self.gracz.t, "lisciolis", False)
        self.assertEqual((w["ok"], w["powod"], w["wybor"]), (True, "ok", ["swietlikowka"]))
        w = self.hak("zagroda_zmien", self.gracz.t, "mchowy_slimak", True)
        self.assertEqual(w["wybor"], ["swietlikowka", "mchowy_slimak"])
        self.assertEqual(self.hak("zagroda_zmien", self.gracz.t, "lisciolis", True)["powod"], "pelna")
        self.assertEqual(self.hak("zagroda_zmien", self.gracz.t, "zoledziak", True)["powod"], "aktywny")
        self.assertEqual(self.hak("zagroda_zmien", self.gracz.t, "jelonek_gaju", True)["powod"], "nie_masz")
        st = self.zagroda()
        self.assertEqual((st["stan"]["stoja"], st["stan"]["reczny"]), (["swietlikowka", "mchowy_slimak"], True))
        dane = self.sw.wolaj(self.inne["DanePakietu"].t.get("OnInvoke"), "czytaj", self.gracz.t,
                             D["zagroda"]["pakiet_danych"])
        self.assertEqual(LM.z_luau(dane[0])["zagroda"], ["swietlikowka", "mchowy_slimak"])
        # zamiana miejscami: Ślimak idzie za graczem, Żołędziak staje na jego miejscu
        self.assertTrue(self.hak("wybierz", self.gracz.t, "mchowy_slimak", True)["ok"])
        self.assertEqual(self.zagroda()["stan"]["stoja"], ["swietlikowka", "zoledziak"])
        # ponowne wczytanie profilu (zapis postępu): wybór z DanePakietu
        self.gracz.ustaw("StanGraczaWczytany", False)
        self.gracz.ustaw("StanGraczaWczytany", True)
        self.assertEqual(self.zagroda()["wybor"], ["swietlikowka", "zoledziak"])
        # „Najrzadsze”
        self.assertEqual(self.hak("zagroda_auto", self.gracz.t), {"ok": True})
        st = self.zagroda()
        self.assertEqual((st["stan"]["stoja"], st["stan"]["reczny"]), (["swietlikowka", "lisciolis"], False))
        # w trakcie wczytywania profilu zagroda nic nie nalicza
        self.gracz.ustaw("StanGraczaWczytany", False)
        zl = self.atr("Gold")
        self.sw.krok(60)
        self.assertEqual(self.atr("Gold"), zl)
        self.assertEqual(self.sw.ostrzezenia, [])

    def test_5m_bez_przychodu_w_stanie_gracza(self):
        """Starszy stan gracza (Pety bez "przychod"): zagroda nie daje Rybek, jedno ostrzeżenie, bez błędów."""
        self.uruchom(zloto=900)
        self.kup_las(0.0, 0.99)
        fn = self.inne["Pety"].t.get("OnInvoke")

        def stary(polecenie, *argi):
            if polecenie == "przychod":
                return LM.do_luau({"ok": False, "powod": "nieznane_polecenie"})
            return self.sw.wolaj(fn, polecenie, *argi)[0]
        self.inne["Pety"].t.set("OnInvoke", stary)
        zl = self.atr("Gold")
        self.sw.krok(120)
        self.assertEqual(self.atr("Gold"), zl)
        self.assertEqual(len([o for o in self.sw.ostrzezenia if "przychod" in o]), 1)

    def test_5h_wyjscie_gracza_i_bazar(self):
        import atrapa_roblox as AR
        self.uruchom(zloto=500)
        self.e_jajka()
        self.sw.wyszedl.odpal(self.gracz.t)
        b = AR.Inst(self.sw, "MiasteczkoBazarGra", "Folder", self.sw.workspace)
        self.assertFalse(self.prompty["E wybor"][0].t.get("Enabled"), "z bazarem E opiekunki — zapasowe wyłączone")
        b.usun()
        self.usuniete.odpal(b.t)
        self.assertTrue(self.prompty["E wybor"][0].t.get("Enabled"))
        self.assertEqual(self.sw.ostrzezenia, [])


# ============================================================================================== 6. styki
class TestStykow(unittest.TestCase):
    def test_6a_stan_gracza(self):
        ZBS = _modul_stanu("zbuduj_stanu_test_petow", "zbuduj.py")
        DS = _modul_stanu("dane_stanu_test_petow", "dane.py")
        _, Ds = DS.dane_z_przypadkami()
        S = U["stan_gracza"]
        self.assertEqual(ZBS.KONTENER, S["kontener"])
        self.assertIn(("BindableFunction", "Sygnaly/" + S["sygnal_petow"]), ZBS.INNE)
        self.assertIn(("RemoteEvent", "Zdalne/" + S["zdarzenia"]), ZBS.INNE)
        self.assertEqual(Ds["pety"]["atrybut_aktywnego"], S["atrybut_aktywnego"])
        self.assertEqual(Ds["pety"]["atrybut_liczby"], S["atrybut_liczby"])
        self.assertEqual(Ds["atrybuty"]["zloto"], S["atrybut_zlota"])
        serwer_stanu = czytaj(STAN, "zrodla", "SerwerStanu.server.luau")
        self.assertIn('zdarzenia:FireClient(gracz, "premia", premiaZ, premiaXp, premiaPet)', serwer_stanu)
        self.assertIn('if polecenie ~= "premia" then', KLIENT)

    def test_6b_bazar_i_ukrycie(self):
        DB = json.loads(czytaj(REPO, "swiat", "miasteczko_bazar_gra", "miejsca.json"))
        self.assertIn(U["zagroda"]["id_okna"], [m["id"] for m in DB["miejsca"]])
        self.assertIn('zdarzenie_okien = "%s"' % U["zagroda"]["zdarzenie_okna"],
                      czytaj(REPO, "swiat", "miasteczko_bazar_gra", "zrodla", "DaneBazaru.luau"))
        self.assertEqual(DB["kontener"], U["zagroda"]["kontener_bazaru"])
        self.assertIn('okna:GetAttribute(id)', czytaj(REPO, "swiat", "miasteczko_bazar_gra", "zrodla",
                                                     "KlientBazaru.client.luau"))
        Uk = U["ukrycie"]
        self.assertIn('S.ATRYBUT_BLOKADY = "%s"' % Uk["atrybut_blokady"],
                      czytaj(REPO, "swiat", "las_potwory", "zrodla", "Stale.luau"))
        self.assertIn('gracz:SetAttribute("%s"' % Uk["atrybut_treningu"],
                      czytaj(REPO, "swiat", "trening_proba", "zrodla", "SerwerTreningu.server.luau"))
        self.assertIn('SetAttribute("%s"' % Uk["chmury_trwa"],
                      czytaj(REPO, "swiat", "teleport_chmury", "zrodla", "KlientTeleportu.client.luau"))
        self.assertIn('Name = "%s"' % Uk["ekran_walki"], czytaj(REPO, "swiat", "test_walki2", "zrodla", "InterfejsWalki2.luau"))
        self.assertTrue(os.path.isfile(os.path.join(REPO, "src", "gui", Uk["hud"] + ".model.json")))
        cialo = bez_komentarzy(KLIENT).split("local function ukryteLokalnie()", 1)[1].split("\nend\n", 1)[0]
        for wymog in ("U.hud", "U.ekran_walki", "U.ekran_klasy", "CameraType.Custom", "U.atrybut_treningu",
                      "U.atrybut_blokady", "U.chmury_trwa"):
            self.assertIn(wymog, cialo)

    def test_6c_wiadomosci_klient_serwer(self):
        s, k = bez_komentarzy(SERWER), bez_komentarzy(KLIENT)
        do_klienta = set(re.findall(r'zdarzenia:FireClient\(gracz, "(\w+)"', s))
        self.assertEqual(do_klienta, {"wyklucie", "odmowa", "lista", "wybrany", "okno", "zagroda_plus",
                                      "zagroda_ulepszona"})
        for p in do_klienta:
            self.assertIn('polecenie == "%s"' % p, k, p)
        do_serwera = set(re.findall(r'zdarzenia:FireServer\("(\w+)"', k))
        self.assertEqual(do_serwera, {"lista", "wybierz", "odstaw", "czekaj", "zagroda_dodaj", "zagroda_zdejmij",
                                      "zagroda_auto", "ulepsz_zagrode"})
        for p in do_serwera:
            self.assertIn('polecenie == "%s"' % p, s, p)
        # klient nie podaje ceny ani losu: FireServer najwyżej z id peta / tak-nie
        self.assertNotIn("NextNumber", k)
        self.assertNotIn("math.random", s)
        self.assertNotIn('SetAttribute("Gold"', s + k)

    def test_6d_pola_danych_klienta_istnieja(self):
        k = bez_komentarzy(KLIENT) + bez_komentarzy(SERWER)
        for przedr, slownik in (("T", "teksty"), ("PP", "pet_przy_graczu"), ("W", "wyklucie"), ("S", "stan_gracza"),
                                ("AG", "atrybuty_gracza"), ("U", "ukrycie")):
            for pole in set(re.findall(r"\b%s\.(\w+)" % przedr, k)):
                self.assertIn(pole, D[slownik], "%s.%s" % (przedr, pole))
        for sekcja in ("inkubator", "zagroda", "wyklucie", "limity", "polozenia", "licznik_ceny", "modele", "teksty"):
            for pole in set(re.findall(r"\bD\.%s\.(\w+)" % sekcja, k)):
                self.assertIn(pole, D[sekcja], "D.%s.%s" % (sekcja, pole))
        cz = bez_komentarzy(ZB.CZESCI)
        for przedr, slownik in (("G", "polozenia"), ("I", "inkubator"), ("Z", "zagroda")):
            for pole in set(re.findall(r"\b%s\.(\w+)" % przedr, cz)):
                self.assertIn(pole, D[slownik], "%s.%s (zbuduj.py)" % (przedr, pole))
        # pola jajka (j. w klientcie i serwerze, J. i PJ. w budowie) — każde jajko ma te same
        for tekst, przedr in ((k, "j"), (cz, "J")):
            for pole in set(re.findall(r"\b%s\.(\w+)" % przedr, tekst)):
                for j in D["jajka"]:
                    self.assertIn(pole, j, "%s.%s" % (przedr, pole))
        for pole in set(re.findall(r"\bPJ\.(\w+)", cz)):
            self.assertIn(pole, D["jajka"][0]["polozenie"], "PJ.%s" % pole)
        for pole in set(re.findall(r"\b(?:atrybuty)\.(\w+)", k)):
            self.assertIn(pole, D["jajka"][0]["atrybuty"], "atrybuty.%s" % pole)


# ============================================================================================== 7. kontrola i budowa
class TestKontroli(unittest.TestCase):
    def test_7a_kontrola_luau(self):
        bledy, parser = SLP.sprawdz_pliki(SLP.pliki_pakietu(), wypisz=lambda *_: None)
        self.assertTrue(parser)
        self.assertEqual(bledy, [])
        self.assertEqual(len(SLP.pliki_pakietu()), 5 + len(U["pety"]) + len(U["jajka"]))

    def test_7b_kontrola_wykrywa_bledy(self):
        zly = 'if not game:GetService("RunService"):IsStudio() then\n\treturn {}\nend\nlocal L = {}\nlocal x = workspace\nreturn L\n'
        self.assertTrue(any("czysta logika" in b for b in SLP.sprawdz_tekst(zly, "LogikaPetow.luau", LM)))
        zly2 = ('if not game:GetService("RunService"):IsStudio() then\n\treturn\nend\n'
                'local g = game:GetService("Players").LocalPlayer\ng:SetAttribute("Gold", 5)\n')
        self.assertTrue(SLP.sprawdz_tekst(zly2, "KlientPetow.client.luau", LM))
        zly3 = ('if not game:GetService("RunService"):IsStudio() then\n\treturn\nend\n'
                'local z = nil\nz:FireServer("kup", 300, 1)\n')
        self.assertTrue(any("więcej niż jednym" in b for b in SLP.sprawdz_tekst(zly3, "KlientPetow.client.luau", LM)))

    def test_7c_zbuduj_sucho_i_kod_do_studio(self):
        r = subprocess.run([sys.executable, "-B", os.path.join(PAKIET, "zbuduj.py"), "--sucho"], capture_output=True,
                           text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("sucho: OK", r.stdout)
        for nazwa, kod in ZB.wszystkie_kody().items():
            pelny = ZB.NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", str(ZB.MIEJSCE)) + kod
            LM.Parser(pelny, nazwa, LM.Interpreter()).program()
            self.assertIsNone(re.search(r"__[A-Z_]+__", kod), nazwa)
            self.assertIn("PetyProba", kod)
        self.assertIn('f:SetAttribute("Wygenerowane", true)', ZB.kod_start(czas="x", skrot="x"))
        self.assertIn("ChangeHistoryService", ZB.kod_start())
        self.assertNotIn("Lighting", "".join(ZB.wszystkie_kody().values()))

    def test_7d_proby_w_play_parsuja_sie(self):
        for plik in ("proba_play.py", "proba_ludzka.py"):
            r = subprocess.run([sys.executable, "-B", os.path.join(TU, plik), "--sprawdz"], capture_output=True,
                               text=True, encoding="utf-8", timeout=120)
            self.assertEqual(r.returncode, 0, plik + ": " + r.stdout + r.stderr)

    def test_7e_bez_sciezek_lokalnych(self):
        for korzen, _, pliki in os.walk(PAKIET):
            if "__pycache__" in korzen:
                continue
            for p in pliki:
                if p.endswith((".py", ".luau", ".md", ".json")):
                    tekst = czytaj(korzen, p)
                    for z in ("C:" + "\\Users", "C:" + "/Users", "/" + "Users/", "App" + "Data", "One" + "Drive"):
                        self.assertNotIn(z, tekst, "%s/%s" % (os.path.basename(korzen), p))


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    unittest.main()
