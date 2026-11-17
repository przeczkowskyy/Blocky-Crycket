# -*- coding: utf-8 -*-
"""Testy punktów styku pakietu „potwory w ruchu” (dopisane przy recenzji, 15.11.2026). Bez Studio, bez sieci.

    python -B swiat/las_potwory/testy/test_styku.py        (unittest; kod 1 przy błędzie)

Luau nie da się tu uruchomić, więc te testy czytają źródła jak tekst i pilnują, żeby obie połowy i prototyp walki
mówiły tym samym językiem. Wykrywają rozjazd, zanim zobaczy go osoba w Studio:

1. Ścieżki: każda dosłowna nazwa z WaitForChild / FindFirstChild w serwerze i kliencie istnieje w planie zbuduj.py
   (foldery, zdalna funkcja, haczyki, moduły) albo w prototypie (Workspace/TestWalki2) i w ReplicatedStorage.
2. Atrybuty: każdy atrybut, który klient czyta, ktoś ustawia (serwer albo odtwarzacz prototypu); serwer czyta tylko
   swoje atrybuty i atrybuty testowe, które przenosi zbuduj.py.
3. Zdalna funkcja (D-016): odtwarzacz wysyła dokładnie trzy pola, serwer czyta dokładnie te trzy przez rawget;
   każdy powód odmowy serwera jest na liście POWODY_CICHE odtwarzacza (poza blad_silnika); klient sam niczego nie
   wysyła i nie ma RemoteEventów.
4. Prototyp (czytany TERAZ, bo zmienia go inny agent): API odtwarzacza, Klipy, pola TabelaAktorow, atrybut Skora,
   Wzorcowe.KLASY, wynik silnika, położenie areny.
5. Wspólne miejsce: strażnik Studio, samousunięcie serwera, brak Lighting, brak ścieżek lokalnych w plikach pakietu.
"""
import json
import os
import re
import sys
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
sys.path.insert(0, PAKIET)
import sprawdz_luau  # noqa: E402
import zbuduj  # noqa: E402  (bez Studio: import studio_mcp jest dopiero w main(), po gałęzi --sucho)

PROTO = os.path.join(REPO, "swiat", "test_walki2")


def czytaj(*czesci):
    with open(os.path.join(*czesci), encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def bez_komentarzy(tekst):
    return sprawdz_luau.rozbierz(tekst)[0]


def napisy(tekst, metoda):
    return set(re.findall(r'%s\(\s*"([^"]+)"' % metoda, bez_komentarzy(tekst)))


SERWER = czytaj(PAKIET, "zrodla", "SerwerPotworow.server.luau")
KLIENT = czytaj(PAKIET, "zrodla", "KlientPotworow.client.luau")
STALE = czytaj(PAKIET, "zrodla", "Stale.luau")
ODTW = czytaj(PROTO, "zrodla", "OdtwarzaczWalki2.luau")


class TestSciezek(unittest.TestCase):
    def test_nazwy_z_waitforchild_istnieja(self):
        plan = set()
        for sciezka in zbuduj.FOLDERY:
            plan.update(sciezka.split("/"))
        for _, sciezka in zbuduj.INNE:
            plan.update(sciezka.split("/"))
        for _, _, sciezka, _, _ in zbuduj.SKRYPTY:
            plan.update(sciezka.split("/"))
        for _, sciezka in zbuduj.SILNIK:
            plan.update(sciezka.split("/"))
        # prototyp (Workspace/TestWalki2), części szablonów i własne GUI klienta
        prototyp = {"Moduly", "Klipy", "TabelaAktorow", "DaneAktorow", "OdtwarzaczWalki2", "Aktorzy"}
        inne = {"HumanoidRootPart", "PlayerGui", "LasPotworyBaner", "LasPotworyBohater"}
        for nazwa, tekst in (("serwer", SERWER), ("klient", KLIENT)):
            uzyte = napisy(tekst, r":WaitForChild") | napisy(tekst, r":FindFirstChild")
            with self.subTest(plik=nazwa):
                self.assertEqual(sorted(uzyte - plan - prototyp - inne), [], "nazwy bez pokrycia w zbuduj.py / prototypie")

    def test_prototyp_tworzy_to_co_czytamy(self):
        zb = czytaj(PROTO, "zbuduj.py")
        for sciezka in ("Moduly/Klipy", "Moduly/OdtwarzaczWalki2", "Moduly/TabelaAktorow", "Moduly/DaneAktorow/",
                        "Moduly/Dziennik", "Zdalne/RozpocznijWalke2"):
            self.assertIn('"%s' % sciezka, zb, sciezka)
        self.assertIn('"Aktorzy"', zb.split("FOLDERY = ", 1)[1].split("\n", 1)[0])
        self.assertIn('KONTENER = "TestWalki2"', zb)
        self.assertIn('S.NAZWA_PROTOTYPU = "TestWalki2"', STALE)
        # klucze szablonów: aktorzy prototypu i przeciwnicy silnika
        akt = czytaj(PROTO, "aktorzy.py")
        walka = json.loads(czytaj(REPO, "tools", "walka", "dane_walki.json"))
        silnik = {p["id"] for p in walka["przeciwnicy"]}
        klucze = re.search(r"S\.SZABLONY = \{([^}]*)\}", STALE).group(1)
        for k in re.findall(r'"(\w+)"', klucze):
            self.assertIn('"klucz": "%s"' % k, akt, k)
            self.assertIn(k, silnik, k)

    def test_plan_zbuduj_jak_w_kontrakcie(self):
        self.assertEqual(zbuduj.FOLDERY, ["Moduly", "Moduly/Walka", "Stan", "Zdalne", "Sygnaly"])
        self.assertEqual(zbuduj.INNE, [("RemoteFunction", "Zdalne/RozpocznijWalke2"),
                                       ("BindableFunction", "Sygnaly/SterowanieSerwera"),
                                       ("BindableFunction", "Sygnaly/SterowanieKlienta"),
                                       ("BindableEvent", "Sygnaly/WynikWalki"),
                                       ("BindableFunction", "Sygnaly/ZwolnijPoPominieciu")])
        konteksty = {s[2]: s[3] for s in zbuduj.SKRYPTY}
        self.assertEqual(konteksty["SerwerPotworow"], "Server")
        self.assertEqual(konteksty["KlientPotworow"], "Client")
        self.assertIn('S.NAZWA_KONTENERA = "LasPotwory"', STALE)
        self.assertEqual(zbuduj.KONTENER, "LasPotwory")

    def test_pomijanie_walk_most_z_prototypem(self):
        """D-078 (przyjęte na noc 17.11.2026): stary las ma Sygnaly/WynikWalki (mostek pomijania w SerwerWalki2) i
        Sygnaly/ZwolnijPoPominieciu (po pominięciu gracz i potwór wolni od razu) — te same nazwy co w prototypie."""
        proto = czytaj(PROTO, "zrodla", "SerwerWalki2.server.luau")
        sygnal = re.search(r'S\.SYGNAL_WYNIKU = "(\w+)"', STALE).group(1)
        self.assertIn(("BindableEvent", "Sygnaly/" + sygnal), zbuduj.INNE)
        self.assertIn('WaitForChild("%s"' % sygnal, proto)
        self.assertIn(("BindableFunction", "Sygnaly/ZwolnijPoPominieciu"), zbuduj.INNE)
        self.assertIn('FindFirstChild("ZwolnijPoPominieciu")', proto)
        self.assertIn('FindFirstChild("ZwolnijPoPominieciu")', SERWER)
        blok = SERWER.split('FindFirstChild("ZwolnijPoPominieciu")', 1)[1].split("\nend\n", 1)[0]
        for kawalek in ("zwolnij.OnInvoke = function(gracz: Player)", 'gracz:IsA("Player")', "walkaDo[gracz] = czas",
                        "p.zajety.gracz == gracz", "p.zajety.koniec = czas", "return true"):
            self.assertIn(kawalek, blok, kawalek)
        # zwalnianie kończy zajętość przez zwykłą pętlę ruchu (koniec <= czas), nie usuwa potwora bezpośrednio
        self.assertIn("if p.zajety and czas >= p.zajety.koniec then", SERWER)
        self.assertEqual(zbuduj.ATRYBUTY_TESTOWE, ["ZiarnoTestowe", "TestBezSesji", "TestGraczy", "TestBezBiomu"])


class TestAtrybutow(unittest.TestCase):
    def test_klient_czyta_tylko_ustawiane(self):
        serwer = napisy(SERWER, "SetAttribute")
        odtwarzacz = set(re.findall(r'self:atrybut\("(\w+)"', ODTW))
        szablon = napisy(czytaj(PROTO, "budowa", "szablon.luau"), "SetAttribute")
        # 17.11.2026: podpis banera po Strażniku może podmienić klient lasu-pasa (lokalny atrybut kontenera LasPasGra)
        pas = czytaj(REPO, "swiat", "las_pas_gra", "zrodla", "KlientPasa.client.luau")
        self.assertIn('kontener:SetAttribute("PodpisBaneraStraznika", PODPIS_BRAMY)', pas)
        brak = napisy(KLIENT, "GetAttribute") - serwer - odtwarzacz - szablon - {"PodpisBaneraStraznika"}
        self.assertEqual(sorted(brak), [])
        self.assertIn("OstatniWynik", odtwarzacz)
        self.assertIn("Skora", szablon)

    def test_serwer_czyta_swoje_i_testowe(self):
        dozwolone = napisy(SERWER, "SetAttribute") | set(zbuduj.ATRYBUTY_TESTOWE) | {"Wygenerowane"}
        self.assertEqual(sorted(napisy(SERWER, "GetAttribute") - dozwolone), [])

    def test_kolejnosc_gotowosci(self):
        # klient czeka na SerwerGotowy po SzablonyGotowe: serwer ustawia SzablonyGotowe (z kopii) przed SerwerGotowy = true
        i_szablony = SERWER.find('kontener:SetAttribute("SzablonyGotowe", kopiujSzablony())')
        i_gotowy = SERWER.rfind('kontener:SetAttribute("SerwerGotowy", true)')
        i_biom = SERWER.find('kontener:SetAttribute("StanBiomu", stanBiomu)')
        self.assertTrue(0 < i_biom < i_szablony < i_gotowy)


class TestZdalnej(unittest.TestCase):
    def test_ladunek_trzy_napisy(self):
        self.assertIn('self.kontener:WaitForChild("Zdalne"):WaitForChild("RozpocznijWalke2")', ODTW)
        self.assertIn("InvokeServer({ klasa = self.wybor.klasa, przeciwnik = self.wybor.przeciwnik, "
                      "poziom = self.wybor.poziom })", ODTW)
        self.assertIn('rawget(wybor, "klasa"), rawget(wybor, "przeciwnik"), rawget(wybor, "poziom")', SERWER)
        self.assertIn("{ klasa = bohater.klasa, przeciwnik = id, poziom = bohater.poziom }", KLIENT)
        # odpowiedź: pola, które odtwarzacz czyta
        self.assertIn("return { ok = true, walka = walka, nastepnaOd = walkaDo[gracz] }", SERWER)
        for pole in ("odpowiedz.walka", "odpowiedz.nastepnaOd", "odpowiedz.powod", "odpowiedz.ponowZa"):
            self.assertIn(pole, ODTW)

    def test_powody_odmowy_znane_odtwarzaczowi(self):
        ciche = re.search(r"local POWODY_CICHE = \{([^}]*)\}", ODTW).group(1)
        ciche = set(re.findall(r"(\w+) = true", ciche))
        powody = set(re.findall(r'odmowa\("(\w+)"', SERWER))
        self.assertTrue(powody, "nie znalazłem odmów w serwerze")
        self.assertEqual(sorted(powody - ciche), ["blad_silnika"])

    def test_klient_nic_nie_wysyla(self):
        kod = bez_komentarzy(KLIENT)
        for zakazane in ("InvokeServer", "FireServer", "RemoteEvent", "RemoteFunction"):
            self.assertNotIn(zakazane, kod, zakazane)
        self.assertNotIn("RemoteEvent", bez_komentarzy(SERWER))

    def test_serwer_sprawdza_wszystko_sam(self):
        kod = bez_komentarzy(SERWER)
        cialo = kod.split("zdalna.OnServerInvoke = function", 1)[1].split("\nend\n", 1)[0]
        # liczby z ładunku nie są używane: poziom to napis z listy, przeciwnik to klucz rejestru
        for kontrola in ("Stale.ODSTEP_PROSB", "potwory[id]", "hum.Health <= 0", "walkaDo[gracz]", "p.zajety",
                         "Stale.ZASIEG_E + promien + Stale.ZAPAS_E_SERWER", "Stale.MAKS_ROZNICA_WYSOKOSCI",
                         "Silnik.symuluj", "p.poziom"):
            self.assertIn(kontrola, cialo, kontrola)
        # kolejność kontroli jak w rozdz. 5.1 (1 → 9)
        kolejnosc = [cialo.find(k) for k in ("Stale.ODSTEP_PROSB", "sprawdzWybor(wybor)", "hum.Health <= 0",
                                               "walkaDo[gracz]", "p.zajety and", "Stale.ZASIEG_E", "Wzorcowe.postac",
                                               "pcall(Silnik.symuluj", "p.zajety = {")]
        self.assertNotIn(-1, kolejnosc)
        self.assertEqual(kolejnosc, sorted(kolejnosc))
        self.assertIn('string.match(przeciwnik, "^[%w_]+%-%d+$")', cialo + kod)


class TestPrototypu(unittest.TestCase):
    """Punkty styku z swiat/test_walki2 (rozdz. 10 kontraktu) — czytane z plików, które są w repozytorium TERAZ."""

    def test_api_odtwarzacza(self):
        for sygnatura in ("function Odtwarzacz.uruchom(kontener: Instance, wybor: any, opcje: any?): boolean",
                          "function Odtwarzacz.czyTrwa(): boolean", "function Odtwarzacz.wolnaZa(): number",
                          'self:atrybut("OstatniWynik", self.walka.wynik)', "local moduly = script.Parent"):
            self.assertIn(sygnatura, ODTW, sygnatura)
        self.assertIn("task.spawn(Odtwarzacz.uruchom, kontener,", KLIENT)
        # P1 wgrana: chowanie obcych wyklucza arenę, szablony i galerię z podanego kontenera I z TestWalki2, a szablony
        # do schowania są zawsze z kontenera modułu (TestWalki2)
        self.assertIn('for _, korzen in { self.kontener, moduly.Parent } do', ODTW)
        self.assertIn('local szablony = moduly.Parent:FindFirstChild("Aktorzy")', ODTW)

    def test_api_klipow_i_aktorow(self):
        klipy = czytaj(PROTO, "zrodla", "Klipy.luau")
        for s in ("function Klipy.nowy(model: Model, dane, opcje: any?)", "function Klipy:graj(nazwa: string, opcje: any?)",
                  "function Klipy:krok(dt: number)", "function Klipy:zastosuj()", "function Klipy:zniszcz()",
                  "self.reczny = opcje.reczny == true"):
            self.assertIn(s, klipy, s)
        aktorzy = czytaj(PROTO, "zrodla", "Aktorzy.luau")
        # nasz klient powtarza kroki Aktorzy.nowy: kotwica korzenia, PivotTo, przesunięcie hrp, punkt „Pasek”
        for s in ("hrp.Anchored = true", "model:PivotTo(cfZiemi)",
                  "CFrame.new(wpis.hrp[1], wpis.hrp[2], wpis.hrp[3])",
                  "return self:cfZiemi() * CFrame.new(0, self.wpis.pasek, 0)"):
            self.assertIn(s, aktorzy, s)
        zb = czytaj(PROTO, "zbuduj.py")
        for pole in ('"hrp": d["hrp"]', '"pasek": round(', '"liczbaCzesci": len(d["czesci"])',
                     '"klipy": {a: w["klipy"].get(a) or False for a in A.AKCJE}'):
            self.assertIn(pole, zb, pole)
        self.assertIn('AKCJE = ["spoczynek", "ruch"', czytaj(PROTO, "aktorzy.py"))

    def test_wzorcowe_silnik_arena(self):
        wz = czytaj(PROTO, "zrodla", "Wzorcowe.luau")
        self.assertIn('W.KLASY = { "wojownik", "zwiadowca", "mag" }', wz)
        self.assertIn('S.KLASY = { "wojownik", "zwiadowca", "mag" }', STALE)
        self.assertIn("function W.postac(klasa: string, poziom: number)", wz)
        self.assertIn("p.tarcza = { blok = W.BLOK_TARCZY }", wz)  # D-071: tarcza tylko u Wojownika wzorcowego
        silnik = czytaj(REPO, "src", "server", "Walka", "Silnik.luau")
        self.assertIn("function Silnik.symuluj(gracz: any, przeciwnik: any, ziarno: any)", silnik)
        self.assertIn('wynik = if wygrana then "wygrana" else "przegrana"', silnik)
        us = czytaj(PROTO, "zrodla", "Ustawienia.luau")
        srodek = [float(x) for x in re.search(r"U\.SRODEK = Vector3\.new\(([^)]*)\)", us).group(1).split(",")]
        podest = float(re.search(r"U\.WYSOKOSC_PODESTU = ([0-9.]+)", us).group(1))
        arena = [float(x) for x in re.search(r"S\.ARENA_PROTOTYPU = Vector3\.new\(([^)]*)\)", STALE).group(1).split(",")]
        self.assertEqual(arena, [srodek[0], srodek[1] + podest, srodek[2]])


class TestWspolnegoMiejsca(unittest.TestCase):
    def test_straznik_i_samousuniecie(self):
        for nazwa in os.listdir(os.path.join(PAKIET, "zrodla")):
            if nazwa.endswith(".luau"):
                tekst = czytaj(PAKIET, "zrodla", nazwa)
                self.assertTrue(sprawdz_luau.pierwsza_instrukcja(tekst).startswith(sprawdz_luau.STRAZNIK), nazwa)
        po = sprawdz_luau.pierwsza_instrukcja(SERWER).split("\n")
        kod = [linia.strip() for linia in po[1:6] if linia.strip() and not linia.strip().startswith("--")]
        self.assertEqual(kod[:2], ["script.Parent:Destroy()", "return"])
        self.assertIn('folder:SetAttribute("Wygenerowane", true)', SERWER)
        self.assertIn('f:SetAttribute("Wygenerowane", true)', zbuduj.START)
        self.assertIn('GetAttribute("Wygenerowane") ~= true then\n\t\t\treturn "STOP', zbuduj.START)

    def test_bez_lighting_i_bez_sciezek_lokalnych(self):
        wzor = re.compile(r"[A-Za-z]:\\\\?Users|/Users/|/home/|AppData|@[a-z0-9-]+\.(?:com|pl)\b", re.I)
        for korzen, _, pliki in os.walk(PAKIET):
            # testy pomijamy: same zawierają te wzorce jako wyrażenia regularne
            if "__pycache__" in korzen or os.path.basename(korzen) == "testy":
                continue
            for nazwa in pliki:
                if not nazwa.endswith((".py", ".luau", ".md", ".json")):
                    continue
                tekst = czytaj(korzen, nazwa)
                with self.subTest(plik=nazwa):
                    self.assertIsNone(wzor.search(tekst), "ścieżka lokalna albo adres w pliku")
                    if nazwa.endswith(".luau"):
                        self.assertNotIn("Lighting", bez_komentarzy(tekst))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    unittest.main(verbosity=2)
