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
  6. mapa (siatka chodzenia z czesci.json): przed frontem sali Training Center pas 8 st na 10 st w głąb bez przeszkód,
     studnia i ławki poza tym pasem, każde stanowisko AFK i trener osiągalne ze startu.
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
    """Lustro uloz() z klienta: rozmiar okna i kafelka w pikselach."""
    kol = 3 if ekran_x >= ekran_y else 2
    rzedy = math.ceil(n / kol)
    w = math.floor(min(ekran_x - 2 * M["brzegX"], M["maksSzer"]))
    h = math.floor(min(ekran_y - 2 * M["brzegY"], M["maksWys"]))
    sw, sh = w - 2 * M["margines"], h - M["pasek"] - 2 - M["margines"]
    cw = math.floor((sw - (kol - 1) * M["odstep"]) / kol)
    ch = math.floor((sh - (rzedy - 1) * M["odstep"]) / rzedy)
    return {"okno": (w, h), "kafel": (cw, ch), "kolumny": kol, "rzedy": rzedy, "siatka": (sw, sh), "x": M["pasek"] - 4}


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
                        'kf.b:SetAttribute("Zajete", zajete)'):
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
        for nazwa, (ex, ey) in self.EKRANY.items():
            u = uloz(ex, ey, M)
            cw, ch = u["kafel"]
            self.assertGreaterEqual(min(cw, ch), 44, (nazwa, u))
            self.assertLessEqual(u["okno"][0], ex, nazwa)
            self.assertLessEqual(u["okno"][1], ey, nazwa)
            self.assertLessEqual(u["kolumny"] * cw + (u["kolumny"] - 1) * M["odstep"], u["siatka"][0], nazwa)
            self.assertLessEqual(u["rzedy"] * ch + (u["rzedy"] - 1) * M["odstep"], u["siatka"][1], nazwa)

    def test_4b_telefon_667x375_liczby_z_opisu(self):
        M = stale_menu()
        self.assertEqual(uloz(667, 339, M)["okno"], (635, 315))
        self.assertEqual(uloz(667, 339, M)["kafel"], (199, 123))
        self.assertEqual(uloz(667, 317, M)["kafel"], (199, 112))
        self.assertEqual(uloz(375, 631, M)["kafel"], (157, 101))
        self.assertIn("okno 635 × 315, kafelek 199 × 123 px", KLIENT)


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
        self.assertEqual(T, {"kontener": self.D["kontener"], "sygnal": "PrzyrostStatystyki"})
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
        cls.front = bazar(TC.LAMPY_SALI[0], TC.SALA_Z[1])          # środek frontu sali na osi przejścia
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


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    unittest.main(verbosity=1)
