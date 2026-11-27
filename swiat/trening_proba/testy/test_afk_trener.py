# -*- coding: utf-8 -*-
"""Testy offline wejścia do sali treningu AFK przez trenera (26.11.2026, zlecenie Karola) — bez Studio.

    python -B swiat/trening_proba/testy/test_afk_trener.py

Tylko odczyt: skrypty Pawła src/server/TreningAFK.server.luau, src/client/TreningAFKClient.client.luau,
src/shared/TreningAFKDane.luau, dane pakietów bazaru (miejsca.json, DaneBazaru.luau), tego pakietu (ustawienia.json,
DaneTreningu.luau, KlientTreningu) i mapy (uklad.json, czesci.json, znaczniki.json).

  1. serwer: bez tabliczek (Tabliczka, SurfaceGui); "wybierz" obsłużone przed sprawdzeniem „trenuje”, odległość od
     trenera, limit częstości, odmowa przy zajętym i przy trwającym treningu, atrybut Zajete na stanowiskach;
  2. klient: okno TreningAFKMenu z nazwami, których używają próby (Tlo, Okno, Tytul, Zamknij, Cwiczenia/<id>),
     zdarzenie OknoMiejsca z atrybutem miejsca (bez dymka bazaru), zamykanie (X, tło, ButtonB, odejście), napisy po
     angielsku wielkimi literami;
  3. dane: D.trener zgodne z bazarem (id miejsca, zdarzenie, punkt E, położenie trenera ze znaczników, zasięg większy
     niż przyjmuje bazar), sześć stanowisk z ikoną i czynnością;
  4. układ okna — te same wzory co uloz() w kliencie, stałe czytane z pliku: kafelki ≥ 44 px i w oknie, okno na
     ekranie, X ≥ 44 px — telefon 667 × 375 (pasek 36 i 58), pionowo 375 × 667, 568 × 320, tablet, monitor;
  5. bazar: podpowiedź trenera „Train”, dymek bez mini-gier; ten pakiet: wybor_od_trenera = false w ustawieniach,
     w DaneTreningu i w kliencie mini-gier;
  6. mapa (siatka chodzenia z czesci.json): przed wejściem do sali Training Center pas 8 st na 10 st w głąb bez
     przeszkód, studnia i ławki poza tym pasem, każde stanowisko AFK i trener osiągalne ze startu;
     od 27.11.2026 (duża sala, polecenie Pawła): rekwizyty z kolizją nie wystają za matę w stronę korytarza, krawędzie
     mat w rzędzie na jednej linii, korytarz ≥ 9 st, maty co ≥ 9 st, zejście w korytarzu i wolne, NPC Pancerza na
     placyku, trener widoczny z wejścia do sali, D.miejsca = znaczniki mapy; zasięg E (model: korzeń postaci 3,54 nad
     ziemią — R15, HipHeight 2,0 — do zaczepu podpowiedzi D.podpowiedzWysokosc nad matą): z krawędzi maty od strony
     korytarza zapas ≥ 0,5 st, z 5,5 st i z osi korytarza — nic, sąsiednie maty poza zasięgiem;
  8. sklep trenera (27.11.2026, polecenie Pawła): dane D.sklep, kolejność sprawdzeń na serwerze, cena tylko z danych,
     jedno miejsce przyznania, bez Robuxów, stan gracza przyjmuje wydatek i dane pakietu, zakładki i przyciski ≥ 44 px,
     rachunek ekonomia_sklepu_afk.py zgodny z danymi.
 10. kości Szczęścia (27.11.2026, Karol): liczby D.kosci (1 k6, pasek 3,5×, średnio jak inne statystyki), ścianki
     prawdziwej kości (przeciwne = 7, oczek tyle co wartość), obrót klienta kładzie ściankę wyniku do góry (lustro),
     serwer losuje i liczy przyrost = suma oczek × przyrost przed stanem gracza i limitem, klient bierze wynik z serwera;
 11. animacje (27.11.2026, Karol: bieżnia i sztanga): Animator awatara odpięty, pozy także w PreSimulation, stawy
     AnimationConstraint z zaczepów, kot Pawła jako szkielet z lustrem na awatarze, bieg bez klipu bohatera, rytm
     wyciskania.
"""
import json
import math
import os
import re
import sys
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
if REPO not in sys.path:
    sys.path.insert(0, REPO)


def czytaj(*sciezka):
    with open(os.path.join(REPO, *sciezka), encoding="utf-8-sig") as f:
        return f.read()


def json_(*sciezka):
    return json.loads(czytaj(*sciezka))


SERWER = czytaj("src", "server", "TreningAFK.server.luau")
KLIENT = czytaj("src", "client", "TreningAFKClient.client.luau")
DANE = czytaj("src", "shared", "TreningAFKDane.luau")
MENU_KOD = KLIENT[KLIENT.index("okno trenera (agent Karola"):]


def dane_trenera():
    blok = re.search(r"D\.trener = \{(.*?)\n\}", DANE, re.S).group(1)
    T = {}
    for k, v in re.findall(r"^\s*(\w+) = (.+?),(?:\s*--.*)?$", blok, re.M):
        if v.startswith('"'):
            T[k] = v.strip('"')
        elif v.startswith("Vector3.new("):
            T[k] = [float(x) for x in v[len("Vector3.new("):-1].split(",")]
        else:
            T[k] = float(v)
    return T


def stale_menu():
    m = re.search(r"local MENU = \{([^}]*)\}", KLIENT)
    return {k: float(v) for k, v in re.findall(r"(\w+) = ([\d.]+)", m.group(1))}


def uloz(ekran_x, ekran_y, M, n=6):
    """Lustro uloz() z klienta: rozmiar okna i kafelka w pikselach; od 27.11.2026 też zakładki i przyciski sklepu."""
    kol = 3 if ekran_x >= ekran_y else 2
    rzedy = math.ceil(n / kol)
    w = math.floor(min(ekran_x - 2 * M["brzegX"], M["maksSzer"]))
    h = math.floor(min(ekran_y - 2 * M["brzegY"], M["maksWys"]))
    sw, sh = w - 2 * M["margines"], h - M["pasek"] - 2 - M["margines"]
    cw = math.floor((sw - (kol - 1) * M["odstep"]) / kol)
    ch = math.floor((sh - (rzedy - 1) * M["odstep"]) / rzedy)
    zw = math.floor(min(M["zakladka"], (w - 2 * M["margines"] - M["pasek"] - 8) / 3))
    tx = M["margines"] + 2 * (zw + 6) + 4
    bh = min(max(math.floor(ch * 0.42), M["przycisk"]), 56)
    bw = math.floor((cw - 18) / 2)
    return {"okno": (w, h), "kafel": (cw, ch), "kolumny": kol, "rzedy": rzedy, "siatka": (sw, sh), "x": M["pasek"] - 4,
            "zakladka": (zw, M["pasek"] - 6), "tytul": (w - tx - M["pasek"] - 8, M["pasek"] - 18), "przycisk": (bw, bh),
            "gora_kafla": ch - bh - 12}


class TestSerwera(unittest.TestCase):
    def test_1a_bez_tabliczek(self):
        for slowo in ("Tabliczka", "SurfaceGui", "LuckiestGuy"):
            self.assertNotIn(slowo, SERWER, slowo)

    def test_1b_wybierz_przed_straznikiem_treningu(self):
        h = SERWER[SERWER.index("Z.OnServerEvent:Connect"):]
        self.assertLess(h.index('if akcja == "wybierz" then'), h.index("local t = trwa[gracz]"))

    def test_1c_sprawdzenia_prosby(self):
        f = SERWER[SERWER.index("local function wybierzOdTrenera"):SERWER.index("Z.OnServerEvent:Connect")]
        for kawalek in ("D.trener.odstep", "D.trener.zasieg", 'typeof(id) ~= "string"', "D.stanowisko(id)",
                        '"odmowa", "trening"', '"odmowa", "daleko"', '"odmowa", "zajete"', "zacznij(gracz, id)",
                        "hum.Health > 0"):
            self.assertIn(kawalek, f, kawalek)
        # kolejność: limit → typ → trwa → odległość → zajęte → start
        kol = [f.index(k) for k in ("D.trener.odstep", 'typeof(id)', "if trwa[gracz]", "D.trener.zasieg",
                                    '"zajete"', "zacznij(gracz, id)")]
        self.assertEqual(kol, sorted(kol))

    def test_1d_atrybut_zajete(self):
        self.assertIn('m:SetAttribute("Zajete", false)', SERWER)
        self.assertEqual(len(re.findall(r"^\s+oznaczZajete\(\)\s*$", SERWER, re.M)), 3)   # zacznij, zakoncz, PlayerRemoving
        self.assertIn('m:SetAttribute("Zajete", zajete[m.Name] == true)', SERWER)

    def test_1e_start_jak_e_przy_macie(self):
        # i E przy macie, i okno trenera kończą się tym samym zacznij(): teleport na matę, kotwica, "start"
        z = SERWER[SERWER.index("local function zacznij"):SERWER.index("local function punktTrenera")]
        for kawalek in ("hrp.CFrame = pozaKorzenia(id, hum, hrp)", "hrp.Anchored = true", 'Z:FireClient(gracz, "start"'):
            self.assertIn(kawalek, z)
        self.assertIn("zacznij(gracz, id)", SERWER[SERWER.index("pp.Triggered:Connect"):])


class TestKlienta(unittest.TestCase):
    def test_2a_nazwy_dla_prob(self):
        for kawalek in ('menu.Name = "TreningAFKMenu"', 'tlo.Name = "Tlo"', 'okno.Name = "Okno"', 'napis(okno, "Tytul"',
                        'zamknijB.Name = "Zamknij"', 'cwiczenia.Name = "Cwiczenia"', "b.Name = s.id",
                        'menu:SetAttribute("Otwarte", true)', 'menu:SetAttribute("Otwarte", false)',
                        'kf.b:SetAttribute("Zajete", zajete)',
                        # 27.11.2026: zakładki i sklep (nazwy, których używa próba proba_afk_trener.py)
                        'zakladkaB("ZakladkaTrening", "TRAIN")', 'zakladkaB("ZakladkaSklep", NAPIS_SKLEPU)',
                        'sklepF.Name = "Sklep"', "f.Name = s.id", 'przyciskSklepu(f, "Ulepsz"', 'przyciskSklepu(f, "Wzmacniacz"',
                        'k.f:SetAttribute("Poziom", lv)', 'k.f:SetAttribute("Wzmacniacz"', 'menu:SetAttribute("Sklep", sklep)'):
            self.assertIn(kawalek, MENU_KOD, kawalek)

    def test_2b_zdarzenie_i_atrybut(self):
        okna = json_("swiat", "miasteczko_bazar_gra", "miejsca.json")["zdarzenie_okien"]
        self.assertIn('local okna = bindable("%s")' % okna, MENU_KOD)
        self.assertIn('Instance.new("BindableEvent")', MENU_KOD)
        self.assertNotIn(okna, DANE)        # nazwa zdarzenia tylko tam, gdzie się je tworzy (test_bazaru 5e)
        self.assertIn("okna:SetAttribute(D.trener.miejsce, true)", MENU_KOD)
        self.assertIn("if id == D.trener.miejsce then", MENU_KOD)
        self.assertIn('Z:FireServer("wybierz", kf.s.id)', MENU_KOD)

    def test_2c_zamykanie(self):
        for kawalek in ("tlo.Activated:Connect(zamknijMenu)", "zamknijB.Activated:Connect(zamknijMenu)",
                        "Enum.KeyCode.ButtonB", "D.trener.zasieg then", 'if akcja == "start" then',
                        "player.CharacterAdded:Connect(zamknijMenu)"):
            self.assertIn(kawalek, MENU_KOD, kawalek)

    def test_2d_napisy_po_angielsku(self):
        napisy = re.findall(r'"([^"]*)"', MENU_KOD[MENU_KOD.index("local NAPIS_MENU"):MENU_KOD.index("local MENU =")])
        napisy += re.findall(r'(?:then|else)\s+"([^"]+)"', MENU_KOD)
        napisy += re.findall(r'\.Text = "([^"]+)"', MENU_KOD)
        napisy += re.findall(r'komunikatMenu\((?:[\w.]+ \.\. )?"([^"\n]+)"', MENU_KOD)
        self.assertGreaterEqual(len(napisy), 7, napisy)
        for t in napisy:
            self.assertRegex(t, r"^[A-Z0-9 !?']+$", t)

    def test_2e_bez_nowych_zasobow(self):
        self.assertNotIn("rbxassetid://", MENU_KOD)           # ikony tylko z TreningAFKDane (s.ikona)
        self.assertIn("ik.Image = s.ikona", MENU_KOD)


class TestDanych(unittest.TestCase):
    def test_3a_trener_zgodny_z_bazarem(self):
        T = dane_trenera()
        M = json_("swiat", "miasteczko_bazar_gra", "miejsca.json")
        self.assertIn(T["miejsce"], [m["id"] for m in M["miejsca"]])
        K = json_("swiat", "trening_proba", "ustawienia.json")
        self.assertEqual(T["punkt"], K["bazar"]["kontener"] + "/" + K["bazar"]["podpowiedz"])
        self.assertEqual(T["punkt"].split("/")[0], M["kontener"])
        zn = json_("swiat", "miasteczko_bazar", "znaczniki.json")["training_center"]["podpowiedz"]
        self.assertLess(max(abs(a - b) for a, b in zip(T["pozycja"], zn)), 0.01, (T["pozycja"], zn))
        P = M["podpowiedz"]
        self.assertGreater(T["zasieg"], P["zasieg"] + P.get("zapas_serwera", 0))
        self.assertGreater(T["odstep"], 0)

    def test_3b_szesc_stanowisk(self):
        ids = re.findall(r'\{ id = "(\w+)", ikona = "rbxassetid://\d+", atrybut = "\w+", nazwa = "[A-Z ]+", skrot = "\w+", '
                         r'czynnosc = "[A-Z ]+"', DANE)
        self.assertEqual(sorted(ids), sorted(["Sila", "Kondycja", "Pancerz", "Zrecznosc", "Inteligencja", "Szczescie"]))


class TestUkladuOkna(unittest.TestCase):
    EKRANY = {"telefon 667×375, pasek 36": (667, 375 - 36), "telefon 667×375, pasek 58": (667, 375 - 58),
              "telefon pionowo 375×667": (375, 667 - 36), "mały telefon 568×320": (568, 320 - 36),
              "tablet 1024×768": (1024, 768 - 36), "monitor 1920×1080": (1920, 1080 - 36)}

    def test_4a_kafelki_dotykowe(self):
        M = stale_menu()
        self.assertGreaterEqual(M["pasek"] - 4, 44)            # X
        self.assertGreaterEqual(M["pasek"] - 6, 44)            # zakładki TRAIN / SHOP (27.11.2026)
        for nazwa, (ex, ey) in self.EKRANY.items():
            u = uloz(ex, ey, M)
            cw, ch = u["kafel"]
            self.assertGreaterEqual(min(cw, ch), 44, (nazwa, u))
            # sklep: dwa przyciski ≥ 44 × 44 px w kafelku i miejsce nad nimi na ikonę z nazwą (≥ 30 px)
            bw, bh = u["przycisk"]
            self.assertGreaterEqual(min(bw, bh), 44, (nazwa, u))
            self.assertLessEqual(2 * bw + 18, cw, nazwa)
            self.assertGreaterEqual(u["gora_kafla"], 30, (nazwa, u))
            self.assertGreaterEqual(u["zakladka"][0], 44, (nazwa, u))
            self.assertLessEqual(u["okno"][0], ex, nazwa)
            self.assertLessEqual(u["okno"][1], ey, nazwa)
            self.assertLessEqual(u["kolumny"] * cw + (u["kolumny"] - 1) * M["odstep"], u["siatka"][0], nazwa)
            self.assertLessEqual(u["rzedy"] * ch + (u["rzedy"] - 1) * M["odstep"], u["siatka"][1], nazwa)

    def test_4b_telefon_667x375_liczby_z_opisu(self):
        # 27.11.2026: nagłówek 48 → 52 px (zakładki ≥ 44 px), kafelki o 2–4 px niższe
        M = stale_menu()
        self.assertEqual(uloz(667, 339, M)["okno"], (635, 315))
        self.assertEqual(uloz(667, 339, M)["kafel"], (199, 121))
        self.assertEqual(uloz(667, 317, M)["kafel"], (199, 110))
        self.assertEqual(uloz(375, 631, M)["kafel"], (157, 100))
        self.assertIn("okno 635 × 315, kafelek 199 × 121 px; przy pasku 58 — 199 × 110; pionowo 375 × 667 — 157 × 100", KLIENT)

    def test_4c_telefon_844x390(self):
        # drugi telefon z polecenia (844 × 390, pasek 36): okno 640 × 330, kafelek 201 × 129, przyciski sklepu 91 × 54
        u = uloz(844, 390 - 36, stale_menu())
        self.assertEqual(u["okno"], (640, 330))
        self.assertEqual(u["kafel"], (201, 129))
        self.assertEqual(u["przycisk"], (91, 54))
        self.assertGreaterEqual(u["tytul"][0], 250)          # tytuł z saldem Rybek obok zakładek


class TestBazaruIMiniGier(unittest.TestCase):
    def test_5a_podpowiedz_trenera(self):
        M = json_("swiat", "miasteczko_bazar_gra", "miejsca.json")
        m = [x for x in M["miejsca"] if x["id"] == "training_center"][0]
        self.assertEqual(m["akcja_tekst"], "Train")
        self.assertNotIn("mini", m["dymek"].lower())
        dane_bazaru = czytaj("swiat", "miasteczko_bazar_gra", "zrodla", "DaneBazaru.luau")
        tc = dane_bazaru[dane_bazaru.index("training_center = {"):]
        tc = tc[:tc.index("},")]
        self.assertIn('akcja_tekst = "Train"', tc)

    def test_5b_wybor_mini_gry_nie_od_trenera(self):
        K = json_("swiat", "trening_proba", "ustawienia.json")
        self.assertIs(K["bazar"]["wybor_od_trenera"], False)
        self.assertIn("wybor_od_trenera = false", czytaj("swiat", "trening_proba", "zrodla", "DaneTreningu.luau"))
        kl = czytaj("swiat", "trening_proba", "zrodla", "KlientTreningu.client.luau")
        h = kl[kl.index("local function podepnijOkna"):]
        h = h[:h.index("for _, c in ReplicatedStorage:GetChildren()")]
        self.assertEqual(h.count("wyborOdTrenera()"), 2)
        self.assertNotIn("tymczasowyWlaczony()", h)


class TestBezMiniGier(unittest.TestCase):
    """26.11.2026 (Karol: „usuń placeholdery”): Workspace/TreningProba bez areny i skryptów mini-gier — zostaje tylko
    sygnał, którym przyrosty ze stanowisk AFK idą do stanu gracza (zapis)."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        if PAKIET not in sys.path:
            sys.path.insert(0, PAKIET)
        import zbuduj as ZB  # noqa: E402 — buduje tylko w main(); import niczego nie wysyła
        import dane as DT  # noqa: E402
        cls.ZB = ZB
        cls.D = DT.wczytaj()[1]
        sg = os.path.join(REPO, "swiat", "stan_gracza")
        if sg not in sys.path:
            sys.path.append(sg)
        spec = importlib.util.spec_from_file_location("dane_stanu_afk", os.path.join(sg, "dane.py"))
        cls.DS_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.DS_mod)
        cls.DS = cls.DS_mod.dane_z_przypadkami()[1]
        import logika_stanu as LS  # noqa: E402
        cls.LS = LS

    def test_7a_przelacznik(self):
        K = json_("swiat", "trening_proba", "ustawienia.json")
        self.assertIs(K["mini_gry"]["w_grze"], False)
        self.assertFalse(self.ZB.mini_gry_w_grze(self.D))
        self.assertIn("w_grze = false", czytaj("swiat", "trening_proba", "zrodla", "DaneTreningu.luau")
                      [czytaj("swiat", "trening_proba", "zrodla", "DaneTreningu.luau").index("mini_gry = {"):][:60])

    def test_7b_budowa_tylko_sygnal(self):
        ZB, D = self.ZB, self.D
        self.assertEqual(ZB.foldery(D), ["Sygnaly"])
        self.assertEqual(ZB.inne(D), [("BindableEvent", "Sygnaly/PrzyrostStatystyki")])
        self.assertEqual(ZB.skrypty_w_grze(D, ["x"]), [])
        start = ZB.kod_start(D, czas="x", skrot="x")
        self.assertIn('{"BindableEvent", "Sygnaly/PrzyrostStatystyki"}', start)
        self.assertIn('f:SetAttribute("MiniGry", false)', start)
        for zbedne in ("SterowanieKlienta", "SterowanieSerwera", "WybierzGre", "ZdarzeniaTreningu", '"Moduly"'):
            self.assertNotIn(zbedne, start, zbedne)       # haczyk bez odbiorcy wstrzymałby wywołującego
        self.assertFalse([k for k in ZB.wszystkie_kody(D) if k.startswith("arena")])
        self.assertIn("nie powstaje", ZB.plan(D)[0])

    def test_7c_ten_sam_sygnal_co_stan_gracza_i_trening_afk(self):
        T = self.DS["trening"]
        # 27.11.2026: + prefiks atrybutów wytrenowanych punktów (limit treningu, TestLimitu)
        self.assertEqual(T, {"kontener": self.D["kontener"], "sygnal": "PrzyrostStatystyki",
                             "prefiks_wytrenowanych": "Wytrenowane"})
        # skrypt Pawła: szuka Workspace/TreningProba/Sygnaly/PrzyrostStatystyki i strzela { atrybut, przyrost, … }
        f = SERWER[SERWER.index("local function dodajStatystyke"):SERWER.index("local function losujCheck")]
        for kawalek in ('workspace:FindFirstChild("%s")' % T["kontener"], 'FindFirstChild("Sygnaly")',
                        'FindFirstChild("%s")' % T["sygnal"], 'e:IsA("BindableEvent")', 'workspace:FindFirstChild("StanGracza")',
                        "e:Fire(gracz, { atrybut = s.atrybut, przyrost = ile"):
            self.assertIn(kawalek, f, kawalek)
        # stan gracza słucha tego zdarzenia (bez skryptów mini-gier) i każdy przyrost AFK przyjmuje
        serwer_stanu = czytaj("swiat", "stan_gracza", "zrodla", "SerwerStanu.server.luau")
        self.assertIn('k:WaitForChild("Sygnaly", 15)', serwer_stanu)
        self.assertIn("e.Event:Connect(function(gracz: any, info: any)", serwer_stanu)
        for s in re.findall(r'atrybut = "(\w+)"', DANE[DANE.index("D.stanowiska = {"):]):
            w, powod = self.LS.czysty_przyrost(self.DS, {"atrybut": s, "przyrost": 1, "zrodlo": "TreningAFK", "gra": "afk_x"})
            self.assertEqual(powod, "ok", s)
            self.assertEqual(w[1], 1)

    def test_7d_mini_gry_nie_sa_wolane_z_gry(self):
        # w kodzie gry (src/) kontener treningu zna tylko skrypt Pawła TreningAFK i używa z niego tylko sygnału przyrostu
        uzywa = []
        for sciezka, _, pliki in os.walk(os.path.join(REPO, "src")):
            for n in pliki:
                if n.endswith(".luau") and self.D["kontener"] in czytaj(os.path.relpath(os.path.join(sciezka, n), REPO)):
                    uzywa.append(n)
        self.assertEqual(uzywa, ["TreningAFK.server.luau"])
        for haczyk in ("WybierzGre", "SterowanieSerwera", "SterowanieKlienta", "ZdarzeniaTreningu", "Moduly"):
            self.assertNotIn(haczyk, SERWER, haczyk)


class TestMapy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from swiat.miasteczko_bazar import siatka
            from swiat.miasteczko_bazar.budynki import training_center as TC
        except ImportError as e:           # bez numpy / Pillow
            raise unittest.SkipTest("siatka chodzenia niedostępna: %s" % e)
        cls.U = json_("swiat", "miasteczko_bazar", "uklad.json")
        cls.D = json_("swiat", "miasteczko_bazar", "czesci.json")
        cls.Z = json_("swiat", "miasteczko_bazar", "znaczniki.json")
        cls.S = siatka.Siatka(cls.D, cls.U)
        cls.TC = TC
        b = [x for x in cls.U["budynki"] if x["id"] == "training_center"][0]
        r = math.radians(b["ry"])

        def bazar(xm, zm):
            return (b["x"] + xm * math.cos(r) + zm * math.sin(r), b["z"] - xm * math.sin(r) + zm * math.cos(r))
        cls.bazar = staticmethod(bazar)
        cls.front = bazar((TC.WEJSCIE_SALI[0] + TC.WEJSCIE_SALI[1]) / 2.0, TC.SALA_Z[1])   # środek wejścia z placyku
        cls.n = (math.sin(r), math.cos(r))                           # na zewnątrz sali (ku placykowi)
        cls.t = (math.cos(r), -math.sin(r))                          # wzdłuż frontu

    def test_6a_pas_przed_sala(self):
        zajete = []
        for i in range(1, 21):                       # 0,5 … 10 st przed frontem
            d = i * 0.5
            for j in range(-8, 9):                   # 8 st szerokości
                w = j * 0.5
                x = self.front[0] + d * self.n[0] + w * self.t[0]
                z = self.front[1] + d * self.n[1] + w * self.t[1]
                iz, ix = self.S.komorka(x, z)
                if self.S.surowe[iz, ix]:
                    zajete.append((round(x, 1), round(z, 1)))
        self.assertEqual(zajete, [], "przeszkody w pasie 8 × 10 st przed salą: %s" % zajete[:6])

    def test_6b_studnia_i_lawki_poza_pasem(self):
        def poza(nazwa_grupy, nazwa=None):
            for c in self.D["czesci"]:
                g = self.D["grupy"][c[1]]
                if nazwa_grupy in g and (nazwa is None or c[14] == nazwa):
                    dx, dz = c[2] - self.U["swiat"]["X0"] - self.front[0], c[4] - self.U["swiat"]["Z0"] - self.front[1]
                    d = dx * self.n[0] + dz * self.n[1]
                    w = dx * self.t[0] + dz * self.t[1]
                    yield d, w
        for d, w in poza("StudniaPomnik"):
            self.assertFalse(-1 < d < 10.5 and abs(w) < 9, ("studnia", d, w))
        lawki = list(poza("Rekwizyty/Placyk", "Ławka siedzisko"))
        self.assertEqual(len(lawki), 2)
        for d, w in lawki:
            self.assertGreater(d, 14, ("ławka przed salą", d, w))

    def test_6c_stanowiska_i_trener_osiagalne(self):
        st = self.U["start"]
        self.S.z_punktu(st["x"], st["z"])
        X0, Z0 = self.U["swiat"]["X0"], self.U["swiat"]["Z0"]
        cele = {s["id"]: (s["pozycja"][0] - X0, s["pozycja"][2] - Z0) for s in self.Z["trening_afk"]["stanowiska"]}
        cele["trener"] = tuple(self.Z["training_center"]["stoisko_bazar"][i] for i in (0, 2))
        self.assertEqual(len(cele), 7)
        for k, (x, z) in cele.items():
            self.assertTrue(math.isfinite(self.S.droga_do(x, z, tolerancja=2.5)), k)

    def test_6d_start_wolny(self):
        st = self.U["start"]
        iz, ix = self.S.komorka(st["x"], st["z"])
        self.assertFalse(self.S.zajete[iz, ix])

    # ------------------------------------------------------------ duża sala (27.11.2026, polecenie Pawła)
    @staticmethod
    def lok(st, lx, lz):
        """Punkt w układzie stanowiska (gracz patrzy w −Z) → układ budynku (x, z)."""
        _, x, z, o, _ = st
        a = math.radians(o)
        return x + lx * math.cos(a) + lz * math.sin(a), z - lx * math.sin(a) + lz * math.cos(a)

    def test_6e_wymiary_sali(self):
        TC = self.TC
        self.assertGreaterEqual(TC.SALA_X[1] - TC.SALA_X[0], 40.0)             # sala sięga do zachodniego brzegu
        self.assertGreaterEqual(TC.PRZEJSCIE[1] - TC.PRZEJSCIE[0], 9.0)         # szeroki korytarz
        self.assertGreaterEqual(TC.WEJSCIE_SALI[1] - TC.WEJSCIE_SALI[0], 10.0)  # wejście z placyku ≥ 10 st
        rzedy = {}
        for st in TC.STANOWISKA:
            rzedy.setdefault(st[2], []).append(st)
        self.assertEqual(sorted(len(v) for v in rzedy.values()), [3, 3])        # D-158: dwa rzędy po trzy
        for z, rz in rzedy.items():
            xs = sorted(s[1] for s in rz)
            self.assertGreaterEqual(min(b - a for a, b in zip(xs, xs[1:])), 9.0, ("odstęp mat", z))
            # krawędź maty od strony korytarza — ta sama dla całego rzędu (problem Pancerza z 26.11)
            krawedz = z + (TC.MATA_POL if z < 0 else -TC.MATA_POL)
            self.assertAlmostEqual(krawedz, TC.PRZEJSCIE[0] if z < 0 else TC.PRZEJSCIE[1])

    def test_6f_rekwizyty_nie_wchodza_w_korytarz_ani_w_sciany(self):
        TC = self.TC
        T = TC.T_SALI
        x_sc, z_tyl, z_front = TC.SALA_X[0] + T, TC.SALA_Z[0] + T, TC.SALA_Z[1] - T
        prostokaty = {}
        for st in TC.STANOWISKA:
            x0, x1, z0, z1 = TC.REKWIZYTY[st[0]]
            pkt = [self.lok(st, a, b) for a in (x0, x1) for b in (z0, z1)]
            pkt += [self.lok(st, a, b) for a in (-TC.MATA_POL, TC.MATA_POL) for b in (-TC.MATA_POL, TC.MATA_POL)]
            xs, zs = [p[0] for p in pkt], [p[1] for p in pkt]
            prostokaty[st[0]] = (min(xs), max(xs), min(zs), max(zs))
            # nic z kolizją nie wystaje za matę w stronę korytarza (gracz staje na równej posadzce)
            if st[2] < 0:
                self.assertLessEqual(max(zs), TC.PRZEJSCIE[0] + 1e-6, st[0])
            else:
                self.assertGreaterEqual(min(zs), TC.PRZEJSCIE[1] - 1e-6, st[0])
            self.assertGreater(min(xs), x_sc + 0.3, ("zachodnia ściana", st[0]))
            self.assertGreater(min(zs), z_tyl + 0.3, ("tylna ściana", st[0]))
            self.assertLess(max(zs), z_front - 0.3, ("przedni bok", st[0]))
            self.assertLess(max(xs), TC.WEJSCIE_SALI[0], ("przedsionek wolny", st[0]))
        ids = sorted(prostokaty)
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                A, B = prostokaty[a], prostokaty[b]
                nachodzi = A[0] < B[1] - 0.5 and B[0] < A[1] - 0.5 and A[2] < B[3] - 0.5 and B[2] < A[3] - 0.5
                self.assertFalse(nachodzi, (a, b))

    def test_6g_zejscie_w_korytarz_i_wolne(self):
        TC = self.TC
        for st in TC.STANOWISKA:
            x, z = self.lok(st, *st[4])
            self.assertTrue(TC.PRZEJSCIE[0] + 0.5 < z < TC.PRZEJSCIE[1] - 0.5, (st[0], z))
            bx, bz = self.bazar(x, z)
            iz, ix = self.S.komorka(bx, bz)
            self.assertFalse(self.S.surowe[iz, ix], st[0])

    def test_6h_npc_pancerza_na_placyku(self):
        TC = self.TC
        st = [s for s in TC.STANOWISKA if s[0] == "Pancerz"][0]
        nx, nz = self.lok(st, 0, -11)                                 # 11 st przed graczem (skrypt Pawła)
        bx, bz = self.bazar(nx, nz)
        g = self.U["granice"]
        self.assertTrue(g["pole_gry_x"][0] < bx < g["pole_gry_x"][1] and nz > TC.SALA_Z[1], (bx, bz))
        # tor rzutu przez okno w przednim boku sali
        self.assertTrue(TC.OKNO_PANCERZA[0] < st[1] < TC.OKNO_PANCERZA[1])
        iz, ix = self.S.komorka(bx, bz)
        self.assertFalse(self.S.surowe[iz, ix])                      # NPC nie stoi w murze ani w studni

    def test_6i_trener_widoczny_z_wejscia(self):
        # linia wzroku na wysokości oczu (5 st) od środka wejścia do sali do głowy trenera: żadna nieprzezroczysta część
        from swiat.miasteczko_bazar import siatka
        X0, Z0 = self.U["swiat"]["X0"], self.U["swiat"]["Z0"]
        a = self.bazar((self.TC.WEJSCIE_SALI[0] + self.TC.WEJSCIE_SALI[1]) / 2.0, self.TC.SALA_Z[1] + 1.0)
        b = self.bazar(*self.TC.TRENER)
        zaslony = []
        for c in self.D["czesci"]:
            if c[13] >= 0.5:
                continue
            W = siatka.wierzcholki(c)
            if not (W[:, 1].min() < 5.0 < W[:, 1].max()):
                continue
            xs, zs = W[:, 0] - X0, W[:, 2] - Z0
            for k in range(1, 40):                                    # próbki co ok. 0,7 st, bez końców
                px, pz = a[0] + (b[0] - a[0]) * k / 40.0, a[1] + (b[1] - a[1]) * k / 40.0
                if xs.min() < px < xs.max() and zs.min() < pz < zs.max():
                    if "Trener" not in self.D["grupy"][c[1]]:
                        zaslony.append(c[14])
                    break
        self.assertEqual(zaslony, [])

    def test_6j_dane_pawla_zgodne_z_mapa(self):
        Z = {s["id"]: s for s in self.Z["trening_afk"]["stanowiska"]}
        blok = DANE[DANE.index("D.miejsca = {"):]
        blok = blok[:blok.index("\n}")]
        wpisy = re.findall(r"(\w+) = \{ pozycja = Vector3\.new\(([-\d., ]+)\), obrot = ([-\d.]+), "
                           r"zejscie = Vector3\.new\(([-\d., ]+)\) \}", blok)
        self.assertEqual(sorted(w[0] for w in wpisy), sorted(Z))
        for id_, poz, obrot, zj in wpisy:
            p = [float(v) for v in poz.split(",")]
            self.assertLess(max(abs(a - b) for a, b in zip(p, Z[id_]["pozycja"])), 0.01, id_)
            self.assertAlmostEqual(float(obrot), Z[id_]["obrot"], places=1)
            v = [float(x) for x in zj.split(",")]
            self.assertEqual([v[0], v[2]], Z[id_]["zejscie"], id_)
        self.assertEqual(self.Z["trening_afk"]["przejscie"]["szer"], round(self.TC.PRZEJSCIE[1] - self.TC.PRZEJSCIE[0], 2))

    def test_6k_zasieg_e_z_krawedzi_maty(self):
        """Model zasięgu podpowiedzi (diagnoza 27.11.2026 w Play): Roblox liczy 3-D od korzenia postaci (R15, HipHeight
        2,0, korzeń 2 × 2 × 1 → 3,54 w świecie, posadzka 0,5) do zaczepu podpowiedzi. Zaczep: środek maty (0,65) +
        D.podpowiedzWysokosc. Gracz stoi na posadzce przy macie od strony korytarza: korzeń 0,5 … 1,3 st za krawędzią
        maty (2,7 … 3,5 od środka), także przesunięty wzdłuż rzędu do 1 st — zapas do 4,5 ≥ 0,5 st."""
        TC = self.TC
        zasieg = float(re.search(r"pp\.MaxActivationDistance = ([\d.]+)", SERWER).group(1))
        self.assertEqual(zasieg, 4.5)                                   # D-158: zasięg bez zmian
        wys = float(re.search(r"D\.podpowiedzWysokosc = ([\d.]+)", DANE).group(1))
        self.assertIn("zaczep.Position = Vector3.new(0, D.podpowiedzWysokosc or 0, 0)", SERWER)
        self.assertIn("pp.Parent = zaczep", SERWER)
        dy = 3.54 - (0.65 + wys)
        for st in TC.STANOWISKA:
            for d in (2.7, 3.0, 3.5):
                for bok in (-1.0, 0.0, 1.0):
                    odl = math.sqrt(d * d + bok * bok + dy * dy)
                    self.assertLessEqual(odl, zasieg - 0.5, (st[0], d, bok, round(odl, 2)))
            self.assertGreater(math.sqrt(5.5 ** 2 + dy * dy), zasieg)    # z 5,5 st — nic (próba A2x)
        # oś korytarza — żadna podpowiedź (gracz idzie korytarzem i nic się samo nie proponuje)
        os_z = (TC.PRZEJSCIE[0] + TC.PRZEJSCIE[1]) / 2.0
        for st in TC.STANOWISKA:
            self.assertGreater(math.sqrt((st[2] - os_z) ** 2 + dy * dy), zasieg + 0.5, st[0])
        # gracz przy macie (3,5 st od środka) jest daleko od każdej innej maty
        for st in TC.STANOWISKA:
            kx, kz = self.lok(st, *[3.5 * v / math.hypot(*st[4]) for v in st[4]])
            for inna in TC.STANOWISKA:
                if inna is not st:
                    self.assertGreater(math.sqrt((inna[1] - kx) ** 2 + (inna[2] - kz) ** 2 + dy * dy), zasieg + 0.5,
                                       (st[0], inna[0]))


class TestSklepu(unittest.TestCase):
    """Sklep trenera (27.11.2026, polecenie Pawła: ulepszenia stanowisk i wzmacniacze ×2)."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location("ekonomia_sklepu_afk", os.path.join(PAKIET, "ekonomia_sklepu_afk.py"))
        cls.E_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.E_mod)
        cls.E = cls.E_mod.wczytaj()
        cls.KUP = SERWER[SERWER.index("local function kup("):SERWER.index("local ostatniStanSklepu")]

    def test_8a_dane(self):
        E = self.E
        self.assertEqual(len(E["ceny"]), E["maks"])
        self.assertEqual(E["ceny"], sorted(E["ceny"]))
        self.assertTrue(all(c >= 1 for c in E["ceny"]))
        self.assertLessEqual(E["premia"] * E["maks"], 0.5)                  # najwyżej +50% tempa
        self.assertEqual(E["mnoznik"], 2)                                    # Paweł: „siła ×2 na 10 min”
        self.assertEqual(E["czas_w"], 600)
        self.assertGreater(E["odstep"], 0)
        self.assertIn('zrodlo = "TreningAFK"', DANE)

    def test_8b_kolejnosc_sprawdzen(self):
        f = self.KUP
        kol = [f.index(k) for k in ("D.sklep.odstep", '"ulepszenie" and rodzaj ~= "wzmacniacz"', "D.stanowisko(id",
                                    'sygnalStanu("WydajZloto")', "wczytajSklep(gracz)", "sk.zajety then", "D.trener.zasieg",
                                    '"odmowa", "maks"', '"odmowa", "aktywny"', 'wolajStan("WydajZloto"', "przyznajUlepszenie(",
                                    '"kupiono"')]
        self.assertEqual(kol, sorted(kol))
        for powod in ('"sklep"', '"wczytywanie"', '"daleko"', '"maks"', '"aktywny"', '"za_malo"'):
            self.assertIn(powod, f, powod)
        # cena tylko z danych: zdalne zdarzenie niesie rodzaj i id, nigdy kwotę
        self.assertIn("local function kup(gracz: Player, rodzaj: unknown, id: unknown)", SERWER)
        self.assertIn("ile = cena, zrodlo = D.sklep.zrodlo", f)
        self.assertIn("D.cenaUlepszenia(sk.u[s.id] or 0)", f)
        self.assertIn("cena = D.sklep.wzmacniacze.cena", f)
        self.assertIn('elseif akcja == "kup" then', SERWER)
        h = SERWER[SERWER.index("Z.OnServerEvent:Connect"):]
        self.assertLess(h.index('akcja == "kup"'), h.index("local t = trwa[gracz]"))

    def test_8c_jedno_miejsce_przyznania(self):
        # poza odczytem profilu (czystySklep) poziom i wzmacniacz zmienia tylko przyznajUlepszenie / przyznajWzmacniacz
        f = SERWER[SERWER.index("local function czystySklep"):SERWER.index("local function wczytajSklep")]
        bez = SERWER.replace(f, "")
        self.assertEqual(len(re.findall(r"sk\.u\[[^\]]+\] = ", bez)), 1)
        self.assertEqual(len(re.findall(r"sk\.w\[[^\]]+\] = ", bez)), 1)
        self.assertEqual(len(re.findall(r"przyznajUlepszenie\(gracz, ", SERWER)), 1)
        self.assertEqual(len(re.findall(r"przyznajWzmacniacz\(gracz, ", SERWER)), 1)
        # pasek i przyrost liczy serwer z poziomu i wzmacniacza
        self.assertIn("if t.postep >= t.pasek then", SERWER)
        self.assertIn("local ile = przyrostNaPasek(gracz, s)", SERWER)
        self.assertIn('Z:FireClient(gracz, "start", id, p, przyrostNaPasek(gracz, s), pasek, zostaloW(gracz, s.atrybut), '
                      'ponad)', SERWER)

    def test_8d_bez_robuxow(self):
        for kod in (SERWER, KLIENT, DANE):
            for zakaz in ("MarketplaceService", "ProcessReceipt =", "PromptProductPurchase", "PromptGamePassPurchase",
                          "DeveloperProduct"):
                self.assertNotIn(zakaz, kod, zakaz)

    def test_8e_profil_stare_zapisy(self):
        f = SERWER[SERWER.index("local function czystySklep"):SERWER.index("local function wczytajSklep")]
        for kawalek in ('type(v) ~= "table"', "math.min(math.floor(n), D.sklep.ulepszenia.maks)", "n >= 1",
                        "k > teraz and k <= teraz + D.sklep.wzmacniacze.czas + 60"):
            self.assertIn(kawalek, f, kawalek)
        w = SERWER[SERWER.index("local function wczytajSklep"):SERWER.index("local function zapiszSklep")]
        self.assertIn('gracz:GetAttribute("StanGraczaWczytany") == false', w)
        self.assertIn('wolajStan("DanePakietu", "czytaj", gracz, D.sklep.pakiet)', w)

    def test_8f_stan_gracza_przyjmuje(self):
        import importlib.util
        sg = os.path.join(REPO, "swiat", "stan_gracza")
        if sg not in sys.path:
            sys.path.append(sg)
        spec = importlib.util.spec_from_file_location("dane_stanu_sklep", os.path.join(sg, "dane.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        DS = m.dane_z_przypadkami()[1]
        import logika_stanu as LS  # noqa: E402
        self.assertIn("TreningAFK", m.PAKIETY_WYDATKOW)
        for cel, ile in (("trening_ulepszenie", self.E["ceny"][-1]), ("trening_wzmacniacz", self.E["cena_w"])):
            w, powod = LS.czysty_wydatek(DS, {"ile": ile, "zrodlo": "TreningAFK", "cel": cel})
            self.assertEqual(powod, "ok", cel)
        w, powod = LS.czyste_dane_pakietu(DS, {"u": {s: 5 for s in ("Sila", "Kondycja", "Pancerz", "Zrecznosc",
                                                                    "Inteligencja", "Szczescie")},
                                               "w": {"Strength": 1795000000, "Luck": 1795000600}})
        self.assertEqual(powod, "ok")
        self.assertTrue(LS.nazwa_ok(DS, "TreningAFK"))

    def test_8g_klient_sklepu(self):
        for kawalek in ('Z:FireServer("kup", rodzaj, k.s.id)', 'Z:FireServer("sklep")', "D.cenaUlepszenia(lv)",
                        'akcja == "sklep" and typeof(powod) == "table"', 'akcja == "kupiono"', "pasekReps = if typeof(d)",
                        "postep / pasekReps", "pasekReps - 0.001", "hum:ChangeState(Enum.HumanoidStateType.GettingUp)"):
            self.assertIn(kawalek, KLIENT, kawalek)
        self.assertNotIn("D.powtorzenNaPasek - 0.001", KLIENT)

    def test_8h_rachunek(self):
        E, M = self.E, self.E_mod
        self.assertAlmostEqual(M.tempo_h(E, E["maks"]) / M.tempo_h(E), 1 + E["premia"] * E["maks"])
        self.assertAlmostEqual(M.tempo_h(E, 0, True) / M.tempo_h(E), E["mnoznik"])
        # odpływ Rybek: wzmacniacz bez przerwy kosztuje więcej, niż daje typowa zagroda; pełne stanowisko ≥ 30 min walk
        # w najbogatszym biomie
        self.assertGreater(E["cena_w"] * 3600 / E["czas_w"], max(M.PRZYCHOD_ZAGRODY_H.values()))
        self.assertGreaterEqual(60.0 * sum(E["ceny"]) / max(M.PRZYCHOD_WALK_H.values()), 30.0)
        self.assertLessEqual(60.0 * E["ceny"][0] / M.PRZYCHOD_WALK_H["las"], 5.0)     # pierwszy poziom szybko



class TestLimitu(unittest.TestCase):
    """Limit treningu zależny od poziomu (27.11.2026, Karol: „A + B”, swiat/przejscie_gry/BALANS_2711.md, pytanie 117):
    wytrenowane w statystyce ≥ limitNaPoziom × poziom → pasek ÷ ponadLimitem; wytrenowane punkty pisze stan gracza."""

    @staticmethod
    def liczba(nazwa):
        return float(re.search(r"\bD\.%s = ([\d.]+)" % nazwa, DANE).group(1))

    def pasek(self, pasek, wytrenowane, poziom):
        """Lustro D.pasekPrzyLimicie."""
        lim, ponad = self.liczba("limitNaPoziom"), self.liczba("ponadLimitem")
        if lim <= 0 or wytrenowane < lim * max(poziom, 1):
            return pasek, False
        return pasek / max(ponad, 0.001), True

    def test_9a_dane(self):
        self.assertEqual(self.liczba("limitNaPoziom"), 2)
        self.assertEqual(self.liczba("ponadLimitem"), 0.1)
        self.assertIn("function D.pasekPrzyLimicie(pasek: number, wytrenowane: number, poziom: number)", DANE)
        tekst = re.search(r'D\.tekstLimitu = "([^"]+)"', DANE).group(1)
        self.assertEqual(tekst, tekst.upper())
        self.assertTrue(all(ord(c) < 128 for c in tekst), "napis po angielsku, bez znaków spoza ASCII")
        self.assertLessEqual(len(tekst), len("HIT THE SKILL CHECKS FOR 2X SPEED!"), "mieści się w miejscu podpowiedzi")
        # prefiks taki sam jak w stanie gracza (ten pisze atrybuty)
        sg = os.path.join(REPO, "swiat", "stan_gracza")
        if sg not in sys.path:
            sys.path.append(sg)
        import importlib.util
        spec = importlib.util.spec_from_file_location("dane_stanu_limit", os.path.join(sg, "dane.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        DS = m.dane_z_przypadkami()[1]
        pref = re.search(r'D\.prefiksWytrenowanych = "([^"]+)"', DANE).group(1)
        self.assertEqual(pref, DS["trening"]["prefiks_wytrenowanych"])
        serwer_stanu = czytaj("swiat", "stan_gracza", "zrodla", "SerwerStanu.server.luau")
        self.assertIn("gracz:SetAttribute(D.trening.prefiks_wytrenowanych .. D.atrybuty_statystyk[s], p.wytrenowane[s])",
                      serwer_stanu)
        self.assertIn("pokazWytrenowane(gracz, p)", serwer_stanu)

    def test_9b_wzor(self):
        self.assertEqual(self.pasek(4, 0, 1), (4, False))
        self.assertEqual(self.pasek(4, 19, 10), (4, False))
        self.assertAlmostEqual(self.pasek(4, 20, 10)[0], 40.0)
        self.assertTrue(self.pasek(4, 20, 10)[1])
        self.assertEqual(self.pasek(4, 20, 11), (4, False), "awans podnosi limit")
        # symulator przejścia czyta te same liczby (jedna prawda)
        sp = os.path.join(REPO, "swiat", "przejscie_gry")
        if sp not in sys.path:
            sys.path.append(sp)
        import symulacja_przejscia as SP  # noqa: E402
        G = SP.gra()
        self.assertEqual((G["afk"]["limit_na_poziom"], G["afk"]["ponad_limit"]), (2, 0.1))
        self.assertEqual(SP.afk_limit(G, 10), 20)

    def test_9c_serwer(self):
        f = SERWER[SERWER.index("local function pasekDla"):SERWER.index("local function przyrostNaPasek")]
        self.assertIn("D.pasekPrzyLimicie(D.powtorzenStanowiska(", f)  # 27.11: pasek Szczęścia × D.kosci.mnoznikPaska
        self.assertIn('gracz:GetAttribute("Level")', f)
        z = SERWER[SERWER.index("local function zacznij"):SERWER.index("-- wejście przez trenera")]
        self.assertIn("wartosc(gracz, D.prefiksWytrenowanych .. s.atrybut)", z)
        self.assertIn("wytrenowane = wytr", z)
        petla = SERWER[SERWER.index("if t.postep >= t.pasek then"):]
        petla = petla[:petla.index("else")]
        kol = [petla.index(x) for x in ("dodajStatystyke(gracz, s, ile)", "t.wytrenowane += ile",
                                         "t.pasek, ponad = pasekDla(gracz, t.id, t.wytrenowane)",
                                         'Z:FireClient(gracz, "punkt", s.atrybut, ile, t.postep, t.pasek, ponad, rzut)')]
        self.assertEqual(kol, sorted(kol))
        self.assertIn('gracz:SetAttribute("TreningAFKLimit", nil)', SERWER)

    def test_9d_klient(self):
        self.assertIn("Z.OnClientEvent:Connect(function(akcja, a, b, c, d, e, f)", KLIENT)
        self.assertIn("podp.Text = if ponad then D.tekstLimitu else PODPOWIEDZ", KLIENT)
        self.assertIn("pokazLimit(f == true)", KLIENT)
        p = KLIENT[KLIENT.index('elseif akcja == "punkt" then'):KLIENT.index('elseif akcja == "skillcheck" then')]
        self.assertIn("pasekReps = d", p)
        self.assertIn("pokazLimit(e == true)", p)


def wektor(t):
    """Vector3.yAxis / -Vector3.zAxis … → (x, y, z)."""
    znak = -1 if t.startswith("-") else 1
    os_ = t.lstrip("-").split(".")[1]
    return tuple(znak * (1 if os_ == c + "Axis" else 0) for c in "xyz")


def obrot_osi(v, os_, kat):
    """Obrót wektora v wokół osi jednostkowej os_ o kąt (wzór Rodriguesa) — lustro CFrame.fromAxisAngle."""
    c, s = math.cos(kat), math.sin(kat)
    k = os_
    kxv = (k[1] * v[2] - k[2] * v[1], k[2] * v[0] - k[0] * v[2], k[0] * v[1] - k[1] * v[0])
    kv = sum(a * b for a, b in zip(k, v))
    return tuple(v[i] * c + kxv[i] * s + k[i] * kv * (1 - c) for i in range(3))


class TestKosci(unittest.TestCase):
    """Kości Szczęścia (27.11.2026, Karol: „niech też rzuca się prawdziwymi kośćmi, wypadają prawdziwe wyniki — i tyle
    szczęścia dostajemy, ile wypadnie”; liczby Karola: 1 kość k6, pasek 3,5× dłuższy)."""

    @classmethod
    def setUpClass(cls):
        blok = re.search(r"D\.kosci = \{(.*?)\n\}", DANE, re.S).group(1)
        cls.K = {k: float(v) for k, v in re.findall(r"^\t(liczba|scianki|mnoznikPaska|bok) = ([\d.]+)", blok, re.M)}
        cls.SCIANY = [(int(w), wektor(n), wektor(u), wektor(v)) for w, n, u, v in re.findall(
            r"\{ w = (\d), n = (-?Vector3\.\wAxis), u = (-?Vector3\.\wAxis), v = (-?Vector3\.\wAxis) \}", blok)]
        cls.OCZKA = {int(w): len(re.findall(r"\{ -?\d, -?\d \}", r)) for w, r in re.findall(r"\[(\d)\] = \{ (.*?) \},\n", blok)}

    def test_10a_liczby_karola(self):
        self.assertEqual((self.K["liczba"], self.K["scianki"], self.K["mnoznikPaska"]), (1, 6, 3.5))
        self.assertIn('stanowisko = "Szczescie"', DANE)
        # średnio tyle samo punktów na sekundę co inne statystyki: E[suma oczek] / mnożnik paska = 1
        srednia = self.K["liczba"] * (self.K["scianki"] + 1) / 2
        self.assertAlmostEqual(srednia / self.K["mnoznikPaska"], 1.0)

    def test_10b_scianki_prawdziwej_kosci(self):
        self.assertEqual(sorted(w for w, _, _, _ in self.SCIANY), [1, 2, 3, 4, 5, 6])
        normalne = {w: n for w, n, _, _ in self.SCIANY}
        for w, n, u, v in self.SCIANY:
            self.assertEqual(tuple(-x for x in n), normalne[7 - w], "przeciwne ścianki dają 7")
            for a, b in ((n, u), (n, v), (u, v)):
                self.assertEqual(sum(x * y for x, y in zip(a, b)), 0, "osie ścianki prostopadłe")
            self.assertEqual(self.OCZKA[w], w, "oczek tyle, ile wartość")

    def test_10c_obrot_klienta_kladzie_wynik_do_gory(self):
        # lustro obrotWyniku(w) z klienta: n.Y > 0,5 → bez obrotu; n.Y < −0,5 → π wokół X; inaczej π/2 wokół n × Y
        self.assertIn("CFrame.fromAxisAngle(sc.n:Cross(Vector3.yAxis).Unit, math.pi / 2)", KLIENT)
        for w, n, _, _ in self.SCIANY:
            if n[1] > 0.5:
                gora = n
            elif n[1] < -0.5:
                gora = obrot_osi(n, (1, 0, 0), math.pi)
            else:
                os_ = (n[1] * 0 - n[2] * 1, n[2] * 0 - n[0] * 0, n[0] * 1 - n[1] * 0)
                gora = obrot_osi(n, os_, math.pi / 2)
            for a, b in zip(gora, (0, 1, 0)):
                self.assertAlmostEqual(a, b, msg="ścianka %d do góry" % w)

    def test_10d_serwer_losuje_i_liczy(self):
        self.assertIn("losKosci:NextInteger(1, scianki)", SERWER)
        self.assertIn("local liczba, scianki = D.kosciRzutu()", SERWER)
        petla = SERWER[SERWER.index("if t.postep >= t.pasek then"):]
        petla = petla[:petla.index("else\n\t\t\tZ:FireClient")]
        kol = [petla.index(x) for x in ("local ile = przyrostNaPasek(gracz, s)", "if t.id == D.kosci.stanowisko then",
                                         "ile *= suma", "dodajStatystyke(gracz, s, ile)", "t.wytrenowane += ile",
                                         'Z:FireClient(gracz, "punkt", s.atrybut, ile, t.postep, t.pasek, ponad, rzut)')]
        self.assertEqual(kol, sorted(kol), "przyrost = suma oczek × przyrost, zanim pójdzie do stanu gracza i limitu")
        # kości z klocków (bez SurfaceGui — test_1a), tyle, ile rzuca serwer
        self.assertIn("local liczba = D.kosciRzutu()", SERWER)
        self.assertIn('grupa(m, "Kosc_" .. i, cf)', SERWER)
        self.assertIn("for _, sc in ipairs(D.kosci.sciany) do", SERWER)

    def test_10e_pasek_szczescia(self):
        self.assertIn("function D.powtorzenStanowiska(id: string, poziom: number): number", DANE)
        self.assertIn("p *= math.max(D.kosci.mnoznikPaska, 0.05)", DANE)
        self.assertIn("math.clamp(math.floor(D.kosci.scianki), 2, 6)", DANE)

    def test_10f_klient_rzuca_wynikiem_z_serwera(self):
        p = KLIENT[KLIENT.index('elseif akcja == "punkt" then'):KLIENT.index('elseif akcja == "skillcheck" then')]
        self.assertIn("rzucKosciU(kosci, b or suma)", p)
        self.assertIn('typeof(f) == "table"', p)  # f = rzut (7. wartość zdarzenia "punkt")
        f = KLIENT[KLIENT.index("local function rzucKosciU"):KLIENT.index("local function pokazWynikKosci")]
        self.assertIn("* obrotWyniku(w)", f)
        self.assertNotIn("math.random(1, 6)", KLIENT, "wynik tylko z serwera")
        self.assertIn('wyskok("+" .. tostring(rz.ile)', KLIENT)
        # obrót w locie gaśnie do zera: na końcu lotu kość ma dokładnie obrót celu
        self.assertIn("local rem = (1 - k) ^ 2", KLIENT)
        self.assertIn("CFrame.Angles(a.X * rem, a.Y * rem, a.Z * rem)", KLIENT)


class TestAnimacji(unittest.TestCase):
    """Bieżnia i sztanga (27.11.2026, Karol: „bieżnia się rusza, ale ludek stoi w miejscu. Tak samo ze sztangą — słabo się
    podnosi”). Próba w Play 27.11: awatar ma stawy AnimationConstraint, a Animator nadpisuje ich Transform."""

    def test_11a_animator_odpiety_i_presimulation(self):
        f = KLIENT[KLIENT.index("local function przejmijAwatara"):KLIENT.index("local function zerujStawy")]
        self.assertIn("an.Parent = nil", f)
        o = KLIENT[KLIENT.index("local function oddajSzkielet"):KLIENT.index("agent Karola, sesja 25.11: nic w łapach")]
        self.assertLess(o.index("animatorOdpiety.Parent = animatorHum"), o.index("animateWylaczony.Disabled = false"),
                        "Animator wraca przed włączeniem Animate")
        self.assertIn("RunService.PreSimulation:Connect(function()", KLIENT)
        self.assertIn('if j:IsA("AnimationConstraint") then', KLIENT)

    def test_11b_stawy_z_zaczepow(self):
        f = KLIENT[KLIENT.index("local function staw(r: Rig"):KLIENT.index("local function dlugosciRamienia")]
        self.assertIn("return { C0 = j.Attachment0.CFrame, C1 = j.Attachment1.CFrame }", f)

    def test_11c_kot_pawla_i_lustro(self):
        self.assertIn('workspace:FindFirstChild("KotyRasSwiatLokalne")', KLIENT)
        self.assertIn('model, rodzaj, lustro = kot, "kot", zbierzStawy(char)', KLIENT)
        self.assertIn("for n, j in pairs(r.lustro or {}) do", KLIENT)

    def test_11d_bieg_na_kazdym_szkielecie(self):
        self.assertNotIn('ruch:Invoke("klip", "bieg")', KLIENT)
        self.assertNotIn('not (r.rodzaj == "bohater" and aktywne == "Zrecznosc")', KLIENT)
        # taśma i kroki z tej samej prędkości
        self.assertIn("drogaTasmy = (drogaTasmy + dt * TASMA * tempo) % 6", KLIENT)
        self.assertIn("fazaBiegu = (fazaBiegu + dt * math.pi * 2 * KADENCJA * tempo)", KLIENT)

    def test_11e_wyciskanie(self):
        # lustro wyciskanie(f): góra przytrzymana, opuszczanie wolniejsze niż wyciśnięcie
        def h(f):
            if f < 0.3:
                return 1 - (1 - f / 0.3) ** 2
            if f < 0.45:
                return 1
            if f < 0.9:
                return 0.5 + 0.5 * math.cos(math.pi * (f - 0.45) / 0.45)
            return 0
        self.assertIn("return 0.5 + 0.5 * math.cos(math.pi * (f - 0.45) / 0.45)", KLIENT)
        self.assertEqual((h(0), h(0.3), h(0.4), h(0.95)), (0, 1, 1, 0))
        self.assertGreater(0.45, 0.3 * 1.4, "opuszczanie (0,45 cyklu) dłuższe niż wyciśnięcie (0,3)")
        self.assertIn("local gora = math.max(dol + 0.6, M.zasieg * 0.97)", KLIENT)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    unittest.main(verbosity=1)
