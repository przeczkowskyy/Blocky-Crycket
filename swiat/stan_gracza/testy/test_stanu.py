# -*- coding: utf-8 -*-
"""Testy pakietu „stan gracza” — bez Studio, bez sieci.

    python -B swiat/stan_gracza/testy/test_stanu.py        (unittest; kod 1 przy błędzie)

1. Dane: zrodla/DaneStanu.luau aktualny; liczby równe źródłom (tools/walka/wzorcowe.py, tempo.py, Statystyki.luau).
2. Klasy Pawła: src/shared/ClassData.luau (tylko odczyt) — id klas = klucze mapy, paski statystyk = rozkłady wzorcowe.
3. Lustro w Pythonie = tools/walka: krzywa (tempo.xp_do_nastepnego), rozdziel i opis bohatera (wzorcowe.postac z
   dodatkowymi punktami).
4. Luau w luau_mini = lustro: przypadki wzorcowe OK (zepsute wykryte), losowe wywołania wszystkich funkcji.
5. Silnik: opis bohatera z Luau przechodzi walidację silnika Luau (luau_mini) i daje ten sam wynik co silnik w
   Pythonie z postacią wzorcową.
6. Styk z innymi pakietami: nazwy Sygnaly w zbuduj.py = stałe w Stale.luau lasu, wywołania w SerwerPotworow i
   KlientPotworow, nazwy atrybutów Pawła, sygnał treningu, wiadomości klient–serwer, próby w Play z TestBohater.
7. Kontrola Luau pakietu (z wykryciem zepsutego pliku), zbuduj.py --sucho, brak ścieżek lokalnych.
8. PRAWDZIWY SerwerStanu.server.luau w luau_mini z atrapą Roblox (testy/atrapa_roblox.py): start, klasa, łup po walce,
   awans, „+” Pawła zostaje, "pokaz" od klienta, Gemy z drzewka, przegrana, zły łup, trening, wyłącznik statystyk.
9. PRAWDZIWY KlientStanu.client.luau w atrapie: "pokaz" przy włączeniu HUD, baner dopiero przy widocznym HUD.
"""
import json
import os
import random
import re
import subprocess
import sys
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
WALKA = os.path.join(REPO, "tools", "walka")
for _s in (PAKIET, WALKA):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import dane as DANE  # noqa: E402
import logika_stanu as LS  # noqa: E402
import sprawdz_luau_stanu as SLS  # noqa: E402
import zbuduj as ZB  # noqa: E402
import silnik  # noqa: E402
import tempo  # noqa: E402
import wzorcowe  # noqa: E402

LM = SLS.luau_mini()
_, D = DANE.dane_z_przypadkami()


def czytaj(*czesci):
    with open(os.path.join(*czesci), encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def bez_komentarzy(tekst):
    return SLS.SL.rozbierz(tekst)[0]


ZR = os.path.join(PAKIET, "zrodla")
SERWER = czytaj(ZR, "SerwerStanu.server.luau")
KLIENT = czytaj(ZR, "KlientStanu.client.luau")
LOGIKA = czytaj(ZR, "LogikaStanu.luau")
STALE_LASU = czytaj(REPO, "swiat", "las_potwory", "zrodla", "Stale.luau")
SERWER_LASU = czytaj(REPO, "swiat", "las_potwory", "zrodla", "SerwerPotworow.server.luau")
KLIENT_LASU = czytaj(REPO, "swiat", "las_potwory", "zrodla", "KlientPotworow.client.luau")


# ============================================================================================== 1. dane
class TestDanych(unittest.TestCase):
    def test_1a_plik_aktualny(self):
        ok, _ = DANE.aktualny()
        self.assertTrue(ok, "uruchom python -B swiat/stan_gracza/dane.py")

    def test_1b_liczby_ze_zrodel(self):
        self.assertEqual(D["krzywa"], {"a": tempo.DOMYSLNE_A, "b": 1.6})
        self.assertEqual(D["pula"], {"baza": wzorcowe.PUNKTY_START, "na_poziom": wzorcowe.PUNKTY_NA_POZIOM})
        self.assertEqual(D["rozklady"], wzorcowe.ROZKLADY)
        self.assertEqual(D["umiejetnosci"], wzorcowe.UMIEJETNOSCI)
        self.assertEqual(D["statystyki"], wzorcowe.STATYSTYKI)
        self.assertEqual(D["wzor"]["blok_tarczy"], wzorcowe.BLOK_TARCZY)
        for L in range(1, 201):
            self.assertEqual(LS.sloty(D, L), wzorcowe.sloty(L), L)
        walka = json.loads(czytaj(WALKA, "dane_walki.json"))
        self.assertEqual(D["statystyki"], walka["statystyki"])
        # Statystyki.ATRYBUTY_GRACZA w silniku (src/server/Walka) — ta sama mapa
        stat = czytaj(REPO, "src", "server", "Walka", "Statystyki.luau")
        blok = stat.split("Statystyki.ATRYBUTY_GRACZA = {", 1)[1].split("}", 1)[0]
        self.assertEqual({a: s for a, s in re.findall(r'(\w+) = "(\w+)"', blok)},
                         {a: s for s, a in D["atrybuty_statystyk"].items()})

    def test_1c_atrybuty_pawla_istnieja(self):
        domyslne = czytaj(REPO, "src", "server", "PlayerStatsDefaults.server.luau")
        for klucz in ("poziom", "xp", "xp_max", "zloto", "gemy"):
            self.assertRegex(domyslne, r"\b%s = " % D["atrybuty"][klucz], klucz)
        for s, a in D["atrybuty_statystyk"].items():
            self.assertRegex(domyslne, r"\b%s = \d+" % a, s)
        self.assertIn('player:SetAttribute("%s", id)' % D["atrybuty"]["klasa"],
                      czytaj(REPO, "src", "server", "ClassSelect.server.luau"))
        # PlayerStatsDefaults ustawia tylko brakujące atrybuty — nie nadpisze tego, co wpisze SerwerStanu
        self.assertIn("if player:GetAttribute(key) == nil then", domyslne)
        # StatPoints dopisuje do tych samych atrybutów (darmowy „+”), limit jak nasz
        punkty = czytaj(REPO, "src", "server", "StatPoints.server.luau")
        self.assertIn("local MAX_VALUE = %d" % D["limity"]["statystyka_maks"], punkty)

    def test_1d_hud_pawla(self):
        # ScreenGui HUD (Rojo: nazwa z pliku src/gui/HUD.model.json); HUDClient słucha zmian atrybutów, które piszemy
        self.assertTrue(os.path.isfile(os.path.join(REPO, "src", "gui", D["hud"]["gui"] + ".model.json")))
        hud = czytaj(REPO, "src", "client", "HUDClient.client.luau")
        self.assertIn('WaitForChild("%s")' % D["hud"]["gui"], hud)
        for a in ("xp", "xp_max", "poziom", "zloto", "gemy"):
            self.assertIn('GetAttributeChangedSignal("%s")' % D["atrybuty"][a], hud, a)


# ============================================================================================== 2. klasy Pawła
class TestKlasPawla(unittest.TestCase):
    def test_2a_classdata_rowne_wzorcowym(self):
        cd = czytaj(REPO, "src", "shared", "ClassData.luau")
        klasy = re.findall(r'\{ id = "(\w+)".*?stats = \{ ([\d, ]+) \}', cd, re.S)
        self.assertEqual(sorted(k for k, _ in klasy), sorted(D["klasy_gracza"]))
        for idk, staty in klasy:
            liczby = [int(x) for x in staty.split(",")]
            r, powod = LS.rozklad_z_class_data(D, liczby)
            self.assertEqual(powod, "ok", idk)
            self.assertEqual(r, wzorcowe.ROZKLADY[D["klasy_gracza"][idk]],
                             "%s: paski ClassData ≠ rozkład wzorcowy — balans walki by się zmienił" % idk)


# ============================================================================================== 3. lustro = tools/walka
class TestLustra(unittest.TestCase):
    def test_3a_krzywa(self):
        for L in range(1, 1000):
            self.assertEqual(LS.xp_do_nastepnego(D, L), tempo.xp_do_nastepnego(L, tempo.DOMYSLNE_A, 1.6), L)

    def test_3b_rozdziel_i_monotonia(self):
        for k in D["klasy"]:
            poprzednie = None
            for punkty in range(0, 3001):
                st = LS.rozdziel(D, D["rozklady"][k], punkty)
                self.assertEqual(st, wzorcowe.rozdziel(wzorcowe.ROZKLADY[k], punkty), (k, punkty))
                if poprzednie and punkty % 10 == 0:
                    # awans (+10 punktów) nigdy nie zabiera punktu żadnej statystyce
                    for s in D["statystyki"]:
                        self.assertGreaterEqual(st[s], poprzednie[s], (k, punkty, s))
                if punkty % 10 == 0:
                    poprzednie = st

    def test_3c_opis_jak_wzorcowa(self):
        los = random.Random(7)
        for k in D["klasy"]:
            for L in list(range(1, 31)) + [50, 120, 999]:
                dodatkowe = {s: los.randint(0, 30) for s in D["statystyki"]}
                st = LS.rozdziel(D, D["rozklady"][k], LS.pula(D, L))
                for s, v in dodatkowe.items():
                    st[s] += v
                self.assertEqual(LS.opis_bohatera(D, k, L, st), wzorcowe.postac(k, L, dodatkowe=dodatkowe), (k, L))

    def test_3d_awans(self):
        self.assertEqual(LS.awans(D, 1, 0, 11), (1, 11, 0))
        self.assertEqual(LS.awans(D, 1, 0, 12), (2, 0, 1))
        p, x, i = LS.awans(D, 1, 0, 12 + 35 + 68 + 5)
        self.assertEqual((p, x, i), (4, 5, 3))
        self.assertEqual(LS.awans(D, 999, 0, 10 ** 9)[0], 999)
        self.assertEqual(LS.awans(D, "x", -5, -3), (1, 0, 0))

    def test_3e_nowe_statystyki_zachowuja_cudze(self):
        cel1 = LS.rozdziel(D, D["rozklady"]["mag"], 30)
        cel2 = LS.rozdziel(D, D["rozklady"]["mag"], 40)
        wytr = {s: 0 for s in D["statystyki"]}
        wytr["sila"] = 5
        pierwsze = LS.nowe_statystyki(D, {"sila": 20, "kondycja": 16, "inteligencja": 18, "zrecznosc": 12, "szczescie": 7,
                                          "pancerz": 57}, None, cel1, wytr)
        self.assertEqual(pierwsze, {s: cel1[s] + wytr[s] for s in D["statystyki"]})
        z_plusem = dict(pierwsze)
        z_plusem["szczescie"] += 3  # darmowy „+” Pawła
        po_awansie = LS.nowe_statystyki(D, z_plusem, cel1, cel2, wytr)
        for s in D["statystyki"]:
            self.assertEqual(po_awansie[s], z_plusem[s] + cel2[s] - cel1[s], s)


# ============================================================================================== 4. Luau w luau_mini
def luau_modul():
    it = LM.Interpreter()
    rs = LM.Tabela()
    rs.set("IsStudio", lambda _self: True)
    game = LM.Tabela()
    game.set("GetService", lambda _self, _n: rs)
    it.globalne.z["game"] = game
    Dl = it.wykonaj(czytaj(ZR, "DaneStanu.luau"), "DaneStanu.luau")[0]
    Ll = it.wykonaj(LOGIKA, "LogikaStanu.luau")[0]
    return it, Dl, Ll


def norm(v):
    if isinstance(v, dict):
        return {k: norm(x) for k, x in v.items() if x is not None} if v else "pusty"
    if isinstance(v, (list, tuple)):
        return [norm(x) for x in v] if v else "pusty"
    if isinstance(v, bool) or v is None or isinstance(v, str):
        return v
    return round(float(v), 9)


@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py — Luau nie wykonany")
class TestLuau(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.it, cls.Dl, cls.L = luau_modul()

    def wolaj(self, nazwa, *argi):
        return [LM.z_luau(x) for x in self.it.wywolaj(self.L.get(nazwa), [LM.do_luau(a) if not isinstance(a, LM.Tabela)
                                                                         else a for a in argi])]

    def test_4a_przypadki_wzorcowe(self):
        ok, n, bledy = self.it.wywolaj(self.L.get("sprawdzPrzypadki"), [self.Dl])
        self.assertTrue(ok, LM.z_luau(bledy))
        self.assertEqual(int(n), sum(len(v) for v in D["przypadki"].values()))

    def test_4b_zepsuty_przypadek_wykryty(self):
        it, Dl, Ll = luau_modul()
        Dl.get("przypadki").get("xp").d[1.0].set("wynik", 13.0)
        Dl.get("przypadki").get("awans").d[3.0].set("wynik", LM.do_luau([2, 1, 1]))
        ok, n, bledy = it.wywolaj(Ll.get("sprawdzPrzypadki"), [Dl])
        self.assertFalse(ok)
        self.assertEqual(LM.z_luau(bledy), ["xp #1", "awans #3"])

    def test_4c_losowe_wywolania_jak_lustro(self):
        los = random.Random(17)
        for _ in range(300):
            L = los.randint(1, 1000)
            self.assertEqual(self.wolaj("xpDoNastepnego", self.Dl, L)[0], LS.xp_do_nastepnego(D, L))
            p, x, d = los.randint(1, 999), los.randint(0, 5000), los.choice([0, 1, 50, 12345, 10 ** 7])
            self.assertEqual(self.wolaj("awans", self.Dl, p, x, d), list(LS.awans(D, p, x, d)))
            k = los.choice(D["klasy"])
            punkty = los.randint(0, 3000)
            self.assertEqual(self.wolaj("rozdziel", self.Dl, self.Dl.get("rozklady").get(k), punkty)[0],
                             LS.rozdziel(D, D["rozklady"][k], punkty))
            st = {s: los.randint(0, 500) for s in D["statystyki"]}
            poz = los.randint(1, 999)
            self.assertEqual(norm(self.wolaj("opisBohatera", self.Dl, k, poz, st)[0]), norm(LS.opis_bohatera(D, k, poz, st)))
            v = los.choice([None, -4, 0, 0.5, 3, 7.9, 999, 1000, 12000, "7", True])
            self.assertEqual(self.wolaj("poziomZ", self.Dl, v)[0], LS.poziom_z(D, v))
            self.assertEqual((self.wolaj("statystykaZ", self.Dl, v) or [None])[0], LS.statystyka_z(D, v))
            idk = los.choice(["Warrior", "Scout", "Mage", "Rogue", None, 3])
            self.assertEqual(self.wolaj("klasaSilnika", self.Dl, idk), list(LS.klasa_silnika(D, idk)))
            obecne = {s: los.choice([los.randint(0, 80), None]) for s in D["statystyki"]}
            baza = los.choice([None, LS.rozdziel(D, D["rozklady"][k], LS.pula(D, poz))])
            cel = LS.rozdziel(D, D["rozklady"][k], LS.pula(D, min(poz + 1, 999)))
            wytr = {s: los.randint(0, 9) for s in D["statystyki"]}
            argi = [self.Dl, LM.do_luau({s: v for s, v in obecne.items() if v is not None}),
                    LM.do_luau(baza) if baza else None, LM.do_luau(cel), LM.do_luau(wytr)]
            self.assertEqual(LM.z_luau(self.it.wywolaj(self.L.get("noweStatystyki"), argi)[0]),
                             LS.nowe_statystyki(D, obecne, baza, cel, wytr))

    def test_4d_lup_i_przyrost_jak_lustro(self):
        los = random.Random(23)
        pola = D["pola_lupu"]
        for _ in range(300):
            lup = {p: los.choice([0, 1, 7, 99, 100, 101, -1, 2.5, 10 ** 6, 10 ** 6 + 1]) for p in pola if los.random() < 0.9}
            lup["kraina"] = los.choice(["las", "", "bagno_2", "la s", "x" * 25, "Las"])
            w, powod = LS.czysty_lup(D, lup)
            wl = self.wolaj("czystyLup", self.Dl, lup)
            self.assertEqual((wl[0] if wl and wl[0] != {} else None, wl[1] if len(wl) > 1 else None),
                             (w, powod), lup)
            info = {"atrybut": los.choice(["Strength", "Armor", "Luck", "Mana", None]),
                    "statystyka": los.choice(["sila", "pancerz", "x", None]),
                    "przyrost": los.choice([0, 1, 2, 1.5, 100, 101, -1, None])}
            info = {k: v for k, v in info.items() if v is not None}
            w, powod = LS.czysty_przyrost(D, info)
            wl = self.wolaj("czystyPrzyrost", self.Dl, info)
            self.assertEqual((wl[0] if wl[0] is not None else None, wl[1]), (list(w) if w else None, powod), info)

    def test_4e_suma_lupow_i_profil(self):
        lupy = [{"zloto": 21, "doswiadczenie": 12, "tokeny_krainy": 1, "gemy": 0, "shard_ewolucji": 0, "kraina": "las"},
                {"zloto": 5, "doswiadczenie": 2, "tokeny_krainy": 2, "gemy": 1, "shard_ewolucji": 1, "kraina": "bagno"},
                {"zloto": 0, "doswiadczenie": 3, "tokeny_krainy": 0, "gemy": 0, "shard_ewolucji": 0, "kraina": ""}]
        self.assertEqual(self.wolaj("sumaLupow", self.Dl, lupy)[0], LS.suma_lupow(D, lupy))
        pl = self.wolaj("nowyProfil", self.Dl)[0]
        pp = LS.nowy_profil(D)
        pp = {k: v for k, v in pp.items() if v is not None}
        self.assertEqual(norm(pl), norm(pp))
        self.assertEqual(pl["wersja"], D["wersja_profilu"])


# ============================================================================================== 5. silnik walki
@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py — Luau nie wykonany")
class TestSilnika(unittest.TestCase):
    def test_5a_opis_z_luau_w_silniku_luau_i_pythona(self):
        it, Dl, Ll = luau_modul()
        for nazwa in ("Dane", "Los", "Statystyki", "Przeciwnicy", "Umiejetnosci", "Silnik"):
            it.laduj(nazwa, czytaj(REPO, "src", "server", "Walka", nazwa + ".luau"))
        S = it.wymagaj("Silnik")
        los = random.Random(5)
        przypadki = [("wojownik", 1, "lesny_slime", 1), ("mag", 4, "muchomornik", 4), ("zwiadowca", 7, "cierniowy_wilk", 7),
                     ("wojownik", 10, "straznik_lasu", 10), ("mag", 9, "lesny_troll", 9)]
        for klasa, L, potwor, pz in przypadki:
            dodatkowe = {s: los.randint(0, 12) for s in D["statystyki"]}
            st = LS.rozdziel(D, D["rozklady"][klasa], LS.pula(D, L))
            for s, v in dodatkowe.items():
                st[s] += v
            opis = it.wywolaj(Ll.get("opisBohatera"), [Dl, klasa, float(L), LM.do_luau(st)])[0]
            for ziarno in (1, 99):
                wl = LM.z_luau(it.wywolaj(S.get("symuluj"), [opis, LM.do_luau({"potwor": potwor, "poziom": pz}),
                                                             float(ziarno)])[0])
                wp = silnik.symuluj(wzorcowe.postac(klasa, L, dodatkowe=dodatkowe), {"potwor": potwor, "poziom": pz}, ziarno)
                self.assertEqual((wl["wynik"], wl["tury"], round(wl["czas"], 6), wl["lup"]),
                                 (wp["wynik"], wp["tury"], round(wp["czas"], 6), wp["lup"]), (klasa, L, potwor, ziarno))


# ============================================================================================== 6. styk z innymi pakietami
class TestStyku(unittest.TestCase):
    def stala(self, nazwa):
        m = re.search(r'^S\.%s = "(\w+)"' % nazwa, STALE_LASU, re.M)
        self.assertIsNotNone(m, "brak S.%s w Stale.luau lasu" % nazwa)
        return m.group(1)

    def test_6a_nazwy_sygnalow(self):
        self.assertEqual(self.stala("KONTENER_STANU"), D["kontener"])
        self.assertEqual(ZB.KONTENER, D["kontener"])
        for stala in ("SYGNAL_BOHATERA", "SYGNAL_LUPU"):
            self.assertIn(("BindableFunction", "Sygnaly/" + self.stala(stala)), ZB.INNE)
        self.assertEqual(self.stala("ATRYBUT_KLASY_GRACZA"), D["atrybuty"]["klasa"])
        self.assertEqual(self.stala("ATRYBUT_POZIOMU_GRACZA"), D["atrybuty"]["poziom"])
        mapa = re.search(r"^S\.KLASY_GRACZA = \{([^}]*)\}", STALE_LASU, re.M).group(1)
        self.assertEqual(dict(re.findall(r'(\w+) = "(\w+)"', mapa)), D["klasy_gracza"])
        # serwer stanu czeka na te same nazwy, które buduje zbuduj.py
        for klasa, sciezka in ZB.INNE:
            self.assertIn('WaitForChild("%s")' % sciezka.split("/")[1], SERWER, sciezka)

    def test_6b_las_wola_stan(self):
        kod = bez_komentarzy(SERWER_LASU)
        cialo = kod.split("zdalna.OnServerInvoke = function", 1)[1].split("\nend\n", 1)[0]
        self.assertIn("local zeStanu = bohaterZeStanu(gracz)", cialo)
        self.assertIn("local bohater = zeStanu or Wzorcowe.postac(klasa, poziomBohatera)", cialo)
        i_zajety, i_lup = cialo.find("p.zajety = {"), cialo.find("nagrodaZaWalke(gracz, p, walka)")
        self.assertTrue(0 < i_zajety < i_lup, "łup dopiero po przyjęciu walki")
        self.assertIn("if zeStanu then\n\t\tnagrodaZaWalke(gracz, p, walka)", cialo)
        pomocnicze = kod.split("local function sygnalStanu", 1)[1].split("zdalna.OnServerInvoke", 1)[0]
        for k in ("Stale.ATRYBUT_TESTU_BOHATERA) == true", "Stale.KONTENER_STANU", '"Wygenerowane"', "pcall(",
                  "Stale.SYGNAL_BOHATERA", "Stale.SYGNAL_LUPU", "zrodlo = kontener.Name", "lup = walka.lup",
                  "czas = walka.czas", "wynik = walka.wynik"):
            self.assertIn(k, pomocnicze, k)
        # zrodlo z lasu jest na liście przyjmowanych źródeł (oba kontenery lasu)
        self.assertEqual(sorted(D["zrodla"]), ["LasPasGra", "LasPotwory"])

    def test_6c_klient_lasu(self):
        kod = bez_komentarzy(KLIENT_LASU)
        self.assertIn("{ klasa = bohater.klasa, przeciwnik = id, poziom = bohater.poziom }", kod)
        cialo = kod.split("local function zacznijWalke", 1)[1].split("\nend\n", 1)[0]
        self.assertLess(cialo.find("zsynchronizujBohatera()"), cialo.find("task.spawn(Odtwarzacz.uruchom"))
        for k in ("Stale.KLASY_GRACZA[id]", "Stale.ATRYBUT_KLASY_GRACZA", "Stale.ATRYBUT_POZIOMU_GRACZA",
                  "Stale.ATRYBUT_TESTU_BOHATERA", "Twój bohater: %s · poziom %d"):
            self.assertIn(k, kod, k)
        for zakazane in ("InvokeServer", "FireServer", "RemoteEvent", "RemoteFunction"):
            self.assertNotIn(zakazane, kod)

    def test_6d_trening(self):
        zb = czytaj(REPO, "swiat", "trening_proba", "zbuduj.py")
        self.assertIn('("BindableEvent", "Sygnaly/%s")' % D["trening"]["sygnal"], zb)
        self.assertIn('D["kontener"]', zb)
        ust = json.loads(czytaj(REPO, "swiat", "trening_proba", "ustawienia.json"))
        self.assertEqual(ust.get("kontener", D["trening"]["kontener"]), D["trening"]["kontener"])
        st = czytaj(REPO, "swiat", "trening_proba", "zrodla", "SerwerTreningu.server.luau")
        self.assertIn("przyrostE:Fire(gracz, {", st)
        for pole in ("statystyka = st.id", "atrybut = st.atrybut", "przyrost = w.przyrost"):
            self.assertIn(pole, st, pole)
        dt = czytaj(REPO, "swiat", "trening_proba", "zrodla", "DaneTreningu.luau")
        for s, a in D["atrybuty_statystyk"].items():
            self.assertIn('atrybut = "%s"' % a, dt, a)

    def test_6e_wiadomosci_klient_serwer(self):
        do_klienta = set(re.findall(r'zdarzenia:FireClient\(gracz, "(\w+)"', bez_komentarzy(SERWER)))
        do_serwera = set(re.findall(r'zdarzenia:FireServer\("(\w+)"\)', bez_komentarzy(KLIENT)))
        self.assertEqual(do_klienta, {"awans"})
        self.assertEqual(do_serwera, {"pokaz"})
        self.assertIn('polecenie ~= "awans"', KLIENT)
        self.assertIn('polecenie ~= "pokaz"', SERWER)
        # klient nie wysyła liczb: FireServer tylko z jednym napisem
        self.assertEqual(re.findall(r"zdarzenia:FireServer\(([^)]*)\)", bez_komentarzy(KLIENT)), ['"pokaz"', '"pokaz"'])
        self.assertIn("D.publikacja.odstep_pokaz_s", SERWER)

    def test_6f_proby_play_wlaczaja_tryb_testowy(self):
        for sciezka in (("las_potwory", "testy", "proba_play.py"), ("las_potwory", "testy", "kontrola_play.py"),
                        ("las_pas_gra", "testy", "proba_play.py"), ("las_pas_gra", "testy", "proba_dodatkowa.py")):
            tekst = czytaj(REPO, "swiat", *sciezka)
            self.assertIn('SetAttribute("%s", true)' % self.stala("ATRYBUT_TESTU_BOHATERA"), tekst, "/".join(sciezka))
            # tuż po starcie Play (zanim próba ustawi bohatera haczykiem "bohater" i zacznie walki)
            i_play = tekst.find('"is_start": True')
            i_test = tekst.find('SetAttribute("TestBohater", true)')
            self.assertTrue(0 < i_play < i_test < i_play + 2500, sciezka)

    def test_6g_paweł_nietkniety(self):
        # pakiet nie zapisuje do plików Pawła i nie wysyła jego zdarzeń
        for kod in (SERWER, KLIENT):
            for z in ("AddStatPoint", "ChooseClass", "SkillTreeBuy"):
                self.assertNotIn(z, bez_komentarzy(kod))
        self.assertNotIn("SetAttribute(A.klasa", SERWER)


# ============================================================================================== 8. SerwerStanu offline
@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py — Luau nie wykonany")
class TestSerweraOffline(unittest.TestCase):
    """Prawdziwy SerwerStanu.server.luau w luau_mini z atrapą Roblox (testy/atrapa_roblox.py). Gracz zaczyna z
    wartościami testowymi PlayerStatsDefaults (Paweł), jakby jego skrypt zadziałał pierwszy."""

    PAWEL = {"Level": 1, "XP": 0, "XPMax": 100, "Gold": 0, "Gems": 1000, "Fish": 0, "Strength": 20, "Constitution": 16,
             "Intelligence": 18, "Dexterity": 12, "Luck": 7, "Armor": 57}
    LUP = {"zloto": 21, "doswiadczenie": 12, "tokeny_krainy": 1, "gemy": 0, "shard_ewolucji": 0, "kraina": "las"}

    def uruchom(self, statystyki_klasy=True, trening=True):
        if TU not in sys.path:
            sys.path.insert(0, TU)
        import atrapa_roblox as AR  # noqa: E402
        sw = AR.Swiat()
        k, inne = AR.kontener_stanu(sw, {"DaneStanu": czytaj(ZR, "DaneStanu.luau"), "LogikaStanu": LOGIKA}, ZB.INNE)
        k.ustaw("StatystykiKlasy", statystyki_klasy)
        cd = czytaj(REPO, "src", "shared", "ClassData.luau")
        klasy = [{"id": i, "stats": [int(x) for x in s.split(",")]}
                 for i, s in re.findall(r'\{ id = "(\w+)".*?stats = \{ ([\d, ]+) \}', cd, re.S)]
        shared = AR.Inst(sw, "Shared", "Folder", sw.replicated)
        sw.modul(shared, "ClassData", wartosc=LM.do_luau({"Classes": klasy}))
        self.przyrost = None
        if trening:
            tp = AR.Inst(sw, "TreningProba", "Folder", sw.workspace)
            sg = AR.Inst(sw, "Sygnaly", "Folder", tp)
            ev = AR.Inst(sw, "PrzyrostStatystyki", "BindableEvent", sg)
            self.przyrost = AR.Zdarzenie(sw)
            ev.t.set("Event", self.przyrost.t)
        g = sw.gracz("Gracz1", self.PAWEL)
        sw.it.wykonaj(SERWER, "SerwerStanu.server.luau")
        self.sw, self.k, self.inne, self.g = sw, k, inne, g
        return sw

    def atr(self, n):
        v = self.g.atrybuty.get(n)
        return int(v) if isinstance(v, float) and v == int(v) else v

    def staty(self):
        return {s: self.atr(a) for s, a in D["atrybuty_statystyk"].items()}

    def wywolaj(self, sygnal, *argi):
        fn = self.inne[sygnal].t.get("OnInvoke")
        self.assertIsNotNone(fn, sygnal + ".OnInvoke nie ustawione")
        w = self.sw.wolaj(fn, *[LM.do_luau(a) if isinstance(a, (dict, list)) else a for a in argi])
        return LM.z_luau(w[0]) if w else None

    def lup(self, czas=20.0, zrodlo="LasPasGra", wynik="wygrana", **zmiany):
        return self.wywolaj("PrzyznajLup", self.g.t, {"lup": dict(self.LUP, **zmiany), "wynik": wynik, "czas": czas,
                                                       "zrodlo": zrodlo, "gatunek": "lesny_slime", "poziom": 1})

    def test_8a_start(self):
        self.uruchom()
        n = sum(len(v) for v in D["przypadki"].values())
        self.assertEqual(self.k.atrybuty["SerwerStanuGotowy"], True)
        self.assertEqual(self.k.atrybuty["ZgodnoscLogikiStanu"], "OK %d/%d" % (n, n))
        self.assertEqual(self.k.atrybuty["RozkladyZ"], "ClassData (3 klas)")
        self.assertEqual(self.k.atrybuty["TreningPodlaczony"], True)
        self.assertEqual(self.sw.ostrzezenia, [])
        # XPMax z krzywej (nie 100 Pawła); bez klasy — rozkład klasy domyślnej zamiast wartości testowych
        self.assertEqual(self.atr("XPMax"), LS.xp_do_nastepnego(D, 1))
        self.assertEqual(self.staty(), LS.rozdziel(D, D["rozklady"]["wojownik"], 30))
        self.assertEqual(self.atr("Gems"), 1000)

    def test_8b_klasa_lup_awans_i_plus_pawla(self):
        self.uruchom()
        self.g.ustaw("Class", "Mage")
        self.assertEqual(self.staty(), LS.rozdziel(D, D["rozklady"]["mag"], 30))
        self.g.ustaw("Luck", self.atr("Luck") + 1)  # darmowy „+” w oknie ekwipunku (StatPoints Pawła)
        opis = self.wywolaj("Bohater", self.g.t)
        self.assertEqual(norm(opis), norm(LS.opis_bohatera(D, "mag", 1, self.staty())))
        self.assertEqual(self.lup(czas=20.0), {"ok": True})
        self.assertEqual((self.atr("Gold"), self.atr("XP"), self.atr("Level")), (0, 0, 1), "łup widać dopiero po walce")
        self.sw.krok(20 + D["publikacja"]["zapas_s"] + 0.5)
        self.assertEqual((self.atr("Gold"), self.atr("XP"), self.atr("Level"), self.atr("XPMax")),
                         (21, 0, 2, LS.xp_do_nastepnego(D, 2)))
        self.assertEqual(self.atr("TokenyKrainy_las"), 1)
        self.assertEqual(self.sw.do_klienta[-1][1], ["awans", 2, 1])
        oczek = LS.rozdziel(D, D["rozklady"]["mag"], 40)
        oczek["szczescie"] += 1
        self.assertEqual(self.staty(), oczek, "awans dopisał różnicę, „+” Pawła został")

    def test_8c_pokaz_od_klienta_i_gemy_drzewka(self):
        self.uruchom()
        ev = self.inne["ZdarzeniaStanu"]
        self.assertEqual(self.lup(czas=40.0, gemy=1, zloto=5, doswiadczenie=3), {"ok": True})
        self.sw.krok(0.5)
        ev.na_serwer.odpal(self.g.t, "pokaz")  # za wcześnie (< min_s) — nic
        self.assertEqual(self.atr("Gold"), 0)
        self.g.ustaw("Gems", 990)  # drzewko Pawła odjęło 10 Gemów w tym czasie
        self.sw.krok(D["publikacja"]["min_s"] + D["publikacja"]["odstep_pokaz_s"])
        ev.na_serwer.odpal(self.g.t, "pokaz")
        self.assertEqual((self.atr("Gold"), self.atr("Gems"), self.atr("XP")), (5, 991, 3))
        ev.na_serwer.odpal(self.g.t, 12345.0)  # obce polecenie — pominięte
        self.sw.krok(60)
        self.assertEqual((self.atr("Gold"), self.atr("Gems")), (5, 991), "łup pokazany tylko raz")

    def test_8d_przegrana_i_kilka_awansow(self):
        self.uruchom()
        self.lup(czas=0.0, wynik="przegrana", zloto=0, tokeny_krainy=0, doswiadczenie=2)
        self.lup(czas=0.0, doswiadczenie=12 + 35 + 68)
        self.sw.krok(D["publikacja"]["zapas_s"] + 0.5)
        self.assertEqual((self.atr("Level"), self.atr("XP")), (4, 2))
        self.assertEqual(sum(x[1][2] for x in self.sw.do_klienta if x[1][0] == "awans"), 3)
        stan = self.wywolaj("SterowanieSerwera", "stan", self.g.t)
        self.assertEqual(stan["walki"], {"wygrane": 1, "przegrane": 1})
        self.assertEqual(stan["wersja"], D["wersja_profilu"])
        self.assertEqual(stan["poziom"], 4)

    def test_8e_zly_lup_odrzucony(self):
        self.uruchom()
        self.assertEqual(self.lup(zrodlo="Haker"), {"ok": False, "powod": "zle_zrodlo"})
        self.assertEqual(self.lup(zloto=-5), {"ok": False, "powod": "zle_zloto"})
        self.assertEqual(self.lup(doswiadczenie=2.5), {"ok": False, "powod": "zle_doswiadczenie"})
        self.assertEqual(self.wywolaj("PrzyznajLup", "nie-gracz", {"lup": self.LUP, "zrodlo": "LasPasGra"}),
                         {"ok": False, "powod": "zly_gracz"})
        self.sw.krok(100)
        self.assertEqual((self.atr("Gold"), self.atr("XP")), (0, 0))

    def test_8f_trening_wzmacnia_i_zostaje_po_awansie(self):
        self.uruchom()
        self.g.ustaw("Class", "Warrior")
        przed = self.staty()
        self.przyrost.odpal(self.g.t, LM.do_luau({"statystyka": "sila", "atrybut": "Strength", "przyrost": 2}))
        self.przyrost.odpal(self.g.t, LM.do_luau({"atrybut": "Mana", "przyrost": 5}))  # nieznana — pominięta
        self.assertEqual(self.atr("Strength"), przed["sila"] + 2)
        self.g.ustaw("Level", 5)  # np. tester w pasku poleceń
        cel = LS.rozdziel(D, D["rozklady"]["wojownik"], LS.pula(D, 5))
        self.assertEqual(self.atr("Strength"), cel["sila"] + 2)
        self.assertEqual(self.atr("XPMax"), LS.xp_do_nastepnego(D, 5))
        opis = self.wywolaj("Bohater", self.g.t)
        dodatkowe = {s: 0 for s in D["statystyki"]}
        dodatkowe["sila"] = 2
        self.assertEqual(norm(opis), norm(wzorcowe.postac("wojownik", 5, dodatkowe=dodatkowe)))
        self.assertEqual(self.k.atrybuty["LicznikTreningu"], 1)

    def test_8g_wylacznik_statystyk(self):
        self.uruchom(statystyki_klasy=False)
        self.assertEqual(self.staty()["sila"], 20, "wyłączone: zostają wartości testowe Pawła")
        self.g.ustaw("Class", "Scout")
        self.g.ustaw("Level", 3)
        self.assertEqual(self.staty(), {"sila": 20, "kondycja": 16, "inteligencja": 18, "zrecznosc": 12, "szczescie": 7,
                                        "pancerz": 57})
        self.przyrost.odpal(self.g.t, LM.do_luau({"atrybut": "Armor", "przyrost": 1}))
        self.assertEqual(self.atr("Armor"), 58)
        opis = self.wywolaj("Bohater", self.g.t)
        self.assertEqual((opis["klasa"], opis["poziom"], opis["statystyki"]["pancerz"]), ("zwiadowca", 3, 58))
        # włączenie w czasie gry: od razu rozkład klasy (cel + trening)
        self.k.ustaw("StatystykiKlasy", True)
        cel = LS.rozdziel(D, D["rozklady"]["zwiadowca"], LS.pula(D, 3))
        self.assertEqual(self.atr("Armor"), cel["pancerz"] + 1)

    def test_8h_bez_treningu_i_wyjscie_gracza(self):
        self.uruchom(trening=False)
        self.assertEqual(self.k.atrybuty["TreningPodlaczony"], False)
        self.lup(czas=10.0)
        self.sw.wyszedl.odpal(self.g.t)
        self.g.t.set("Parent", None)
        self.sw.krok(60)  # zadanie pokazu po wyjściu gracza nie wybucha
        self.assertEqual(self.sw.ostrzezenia, [])


# ============================================================================================== 9. KlientStanu offline
@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py — Luau nie wykonany")
class TestKlientaOffline(unittest.TestCase):
    """Prawdziwy KlientStanu.client.luau w luau_mini z atrapą: HUD Pawła (Enabled), zdalne zdarzenie, Instance.new.
    Sprawdza: "pokaz" przy każdym włączeniu HUD, baner „POZIOM N” dopiero, gdy HUD widać, i jeden baner na kilka
    awansów. Wygląd banera ocenia się w Studio (część B)."""

    def uruchom(self, z_hudem=True, hud_wlaczony=False):
        if TU not in sys.path:
            sys.path.insert(0, TU)
        import atrapa_roblox as AR  # noqa: E402
        sw = AR.Swiat()
        k, inne = AR.kontener_stanu(sw, {"DaneStanu": czytaj(ZR, "DaneStanu.luau"), "LogikaStanu": LOGIKA}, ZB.INNE)
        ev = inne["ZdarzeniaStanu"]
        self.wyslane = []
        ev.t.set("FireServer", lambda _s, *a: self.wyslane.append([AR.py(x) for x in a]))
        self.do_klienta = AR.Zdarzenie(sw)
        ev.t.set("OnClientEvent", self.do_klienta.t)
        gracz = sw.gracz("Gracz1", {})
        pg = AR.Inst(sw, "PlayerGui", "PlayerGui", gracz)
        self.hud = None
        if z_hudem:
            self.hud = AR.Inst(sw, "HUD", "ScreenGui", pg)
            self.hud_wl = AR.Zdarzenie(sw)
            self.hud.t.set("Enabled", hud_wlaczony)
            self.hud.t.set("GetPropertyChangedSignal", lambda _s, n: self.hud_wl.t)
        sw.players.t.set("LocalPlayer", gracz.t)
        self.nowe = []

        def nowa(klasa):
            o = AR.Inst(sw, klasa, klasa)
            for m in ("Play", "Stop"):
                o.t.set(m, lambda _s: None)
            self.nowe.append(o)
            return o.t
        g = sw.it.globalne.z
        g["Instance"] = LM.do_luau({})
        g["Instance"].set("new", nowa)
        tween = LM.Tabela()
        tw = LM.Tabela()
        tw.set("Play", lambda _s: None)
        zak = LM.Tabela()
        zak.set("Wait", lambda _s: None)
        tw.set("Completed", zak)
        tween.set("Create", lambda _s, *a: tw)
        uslugi = {"TweenService": tween, "SoundService": AR.Inst(sw, "SoundService", "SoundService").t}
        stary = g["game"].get("GetService")
        g["game"].set("GetService", lambda s, n: uslugi[n] if n in uslugi else stary(s, n))
        dowolne = lambda *a: LM.Tabela()  # noqa: E731
        for nazwa, pola in (("UDim2", ("fromScale", "fromOffset", "new")), ("Vector2", ("new",)), ("Color3", ("fromHex",)),
                            ("NumberRange", ("new",)), ("TweenInfo", ("new",))):
            t = LM.Tabela()
            for p in pola:
                t.set(p, dowolne)
            g[nazwa] = t
        enum = LM.Tabela()
        for nazwa, wart in (("EasingStyle", ("Back", "Quad")), ("EasingDirection", ("Out", "In")), ("Font", ("LuckiestGuy",))):
            t = LM.Tabela()
            for w in wart:
                t.set(w, nazwa + "." + w)
            enum.set(nazwa, t)
        g["Enum"] = enum
        skrypt = LM.Tabela()
        skrypt.set("Parent", k.t)
        g["script"] = skrypt
        sw.it.wykonaj(KLIENT, "KlientStanu.client.luau")
        self.sw, self.pg = sw, pg
        return sw

    def banery(self):
        return [o for o in self.nowe if o.klasa == "ScreenGui" and o.t.get("Name") == D["baner"]["gui"]]

    def napisy(self):
        return [o.t.get("Text") for o in self.nowe if o.klasa == "TextLabel"]

    def wlacz_hud(self, wl):
        self.hud.t.set("Enabled", wl)
        self.hud_wl.odpal()

    def test_9a_pokaz_przy_wlaczeniu_hud(self):
        self.uruchom(hud_wlaczony=False)
        self.assertEqual(self.wyslane, [], "HUD wyłączony (ładowanie, wybór klasy, walka) — bez zgłoszenia")
        self.wlacz_hud(True)
        self.assertEqual(self.wyslane, [["pokaz"]])
        self.wlacz_hud(False)
        self.wlacz_hud(True)
        self.assertEqual(self.wyslane, [["pokaz"], ["pokaz"]])

    def test_9b_baner_czeka_na_hud(self):
        self.uruchom(hud_wlaczony=False)
        self.do_klienta.odpal("awans", 3.0, 1.0)
        self.do_klienta.odpal("awans", 4.0, 1.0)  # dwa awanse w czasie walki → jeden baner
        self.do_klienta.odpal("oszust", 99.0, 1.0)
        self.sw.krok(5)
        self.assertEqual(self.banery(), [], "HUD schowany — baner czeka")
        self.wlacz_hud(True)
        self.sw.krok(D["baner"]["opoznienie_po_hud_s"] + 0.1)
        b = self.banery()
        self.assertEqual(len(b), 1)
        self.assertIs(b[0].t.get("Parent"), self.pg.t)
        self.assertIn(D["baner"]["tekst"] % 4, self.napisy())
        self.assertIn(D["baner"]["podpis_wiele"] % 2, self.napisy())
        self.sw.krok(10)
        self.assertEqual(len(self.banery()), 1, "drugiego banera nie ma")
        self.assertEqual(self.sw.ostrzezenia, [])
        self.assertTrue(any(o.klasa == "Sound" for o in self.nowe), "dźwięk awansu (wbudowany — bez katalogu)")

    def test_9c_bez_hud(self):
        self.uruchom(z_hudem=False)
        self.assertEqual(self.wyslane, [["pokaz"]])
        self.do_klienta.odpal("awans", 2.0, 1.0)
        self.assertEqual(len(self.banery()), 1)
        self.assertTrue(any("brak PlayerGui.HUD" in o for o in self.sw.ostrzezenia))


# ============================================================================================== 7. kontrola, budowa, prywatność
class TestKontroli(unittest.TestCase):
    def test_7a_kontrola_luau(self):
        bledy, parser = SLS.sprawdz_pliki(SLS.pliki_pakietu(), wypisz=lambda *_: None)
        self.assertTrue(parser)
        self.assertEqual(bledy, [])
        self.assertEqual(len(SLS.pliki_pakietu()), 4)

    def test_7b_kontrola_wykrywa_bledy(self):
        zly = 'if not game:GetService("RunService"):IsStudio() then\n\treturn {}\nend\nlocal L = {}\nlocal x = workspace\nreturn L\n'
        self.assertTrue(any("czysta logika" in b for b in SLS.sprawdz_tekst(zly, "LogikaStanu.luau", LM)))
        zly2 = 'local a = 1\nif a then\n'
        self.assertTrue(SLS.sprawdz_tekst(zly2, "SerwerStanu.server.luau", LM))
        zly3 = ('if not game:GetService("RunService"):IsStudio() then\n\treturn\nend\n'
                'workspace.Cos:SetAttribute("X", 1)\n')
        self.assertTrue(any("SetAttribute" in b for b in SLS.sprawdz_tekst(zly3, "SerwerStanu.server.luau", LM)))

    def test_7c_zbuduj_sucho(self):
        r = subprocess.run([sys.executable, "-B", os.path.join(PAKIET, "zbuduj.py"), "--sucho"], capture_output=True,
                           text=True, encoding="utf-8", timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("sucho: OK", r.stdout)
        for kod in ZB.wszystkie_kody().values():
            self.assertIn("StanGracza", kod)
        self.assertIn('f:SetAttribute("Wygenerowane", true)', ZB.kod_start(czas="x", skrot="x"))

    def test_7e_proba_play_parsuje_sie(self):
        r = subprocess.run([sys.executable, "-B", os.path.join(TU, "proba_play.py"), "--sprawdz"], capture_output=True,
                           text=True, encoding="utf-8", timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_7d_bez_sciezek_lokalnych(self):
        for korzen, _, pliki in os.walk(PAKIET):
            if "__pycache__" in korzen:
                continue
            for p in pliki:
                if p.endswith((".py", ".luau", ".md", ".json")):
                    tekst = czytaj(korzen, p)
                    # wzorce składane z kawałków, żeby ten test sam ich nie zawierał
                    for z in ("C:" + "\\Users", "C:" + "/Users", "/" + "Users/", "App" + "Data", "One" + "Drive"):
                        self.assertNotIn(z, tekst, "%s/%s" % (os.path.basename(korzen), p))


if __name__ == "__main__":
    unittest.main()
