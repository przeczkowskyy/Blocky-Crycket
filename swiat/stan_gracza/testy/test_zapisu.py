# -*- coding: utf-8 -*-
"""Testy zapisu postępu (18.11.2026, propozycja; zapis DOMYŚLNIE WYŁĄCZONY) — bez Studio, bez sieci.

    python -B swiat/stan_gracza/testy/test_zapisu.py

PRAWDZIWY SerwerStanu.server.luau + Moduly/ZapisStanu w luau_mini, z atrapą DataStore (testy/atrapa_roblox.Magazyn)
wspólną dla kilku serwerów: zapis i odczyt między sesjami, migracja, dwa serwery naraz (blokada sesji), błąd usługi
przy wczytaniu, zapisie i zamknięciu serwera, zepsuty i przyszły profil, limit rozmiaru, wyjście gracza w trakcie
zapisu i wczytywania, liczba zapytań w czasie, Studio bez dostępu do usług danych, zapis domyślnie wyłączony,
pamięć biomu (PamiecGracza) z zapisu. Lustro logiki (migracja, sprawdzanie profilu) jest w test_stanu.py (przypadki).
"""
import os
import sys
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
if TU not in sys.path:
    sys.path.insert(0, TU)
import test_stanu as T  # noqa: E402
import atrapa_roblox as AR  # noqa: E402

LM, D, LS, ZB = T.LM, T.D, T.LS, T.ZB
ZAPIS = T.czytaj(T.ZR, "ZapisStanu.luau")
G = D["zapis"]
PAWEL = dict(T.TestSerweraOffline.PAWEL)
LUP = dict(T.TestSerweraOffline.LUP)


class Serwer:
    """Jeden serwer z kontenerem StanGracza i wspólnym magazynem."""

    def __init__(self, magazyn, wlaczony=True):
        sw = AR.Swiat()
        if magazyn is not None:
            magazyn.dodaj_do(sw)
        k, inne = AR.kontener_stanu(sw, {"DaneStanu": T.czytaj(T.ZR, "DaneStanu.luau"), "LogikaStanu": T.LOGIKA,
                                         "ZapisStanu": ZAPIS}, ZB.INNE)
        k.ustaw(D["poczatek"]["atrybut_wylacznika"], False)
        if wlaczony:
            k.ustaw(G["atrybut"], True)
        shared = AR.Inst(sw, "Shared", "Folder", sw.replicated)
        sw.modul(shared, "ClassData", wartosc=LM.do_luau({"Classes": [{"id": i, "stats": s} for i, s in T.klasy_pawla()]}))
        sw.it.wykonaj(T.SERWER, "SerwerStanu.server.luau")
        self.sw, self.k, self.inne = sw, k, inne

    def dolacz(self, uid=101, atrybuty=None):
        g = self.sw.gracz("Gracz%d" % uid, dict(PAWEL if atrybuty is None else atrybuty))
        g.t.set("UserId", float(uid))
        self.sw.dolaczyl.odpal(g.t)
        return g

    def wyjdz(self, g):
        self.sw.wyszedl.odpal(g.t)
        g.t.set("Parent", None)
        if g in self.sw.players.dzieci:
            self.sw.players.dzieci.remove(g)

    def wywolaj(self, sygnal, *argi):
        fn = self.inne[sygnal].t.get("OnInvoke")
        w = self.sw.wolaj(fn, *[LM.do_luau(a) if isinstance(a, (dict, list)) else a for a in argi])
        return LM.z_luau(w[0]) if w else None

    def lup(self, g, wynik="wygrana", **zmiany):
        w = self.wywolaj("PrzyznajLup", g.t, {"lup": dict(LUP, **zmiany), "wynik": wynik, "czas": 0, "zrodlo": "LasPasGra",
                                              "gatunek": "lesny_slime", "poziom": 1})
        self.sw.krok(D["publikacja"]["zapas_s"] + 0.5)
        return w

    def zamknij(self):
        for fn in self.sw.zamkniecie:
            self.sw.wolaj(fn)

    def atr(self, g, n):
        v = g.atrybuty.get(n)
        return int(v) if isinstance(v, float) and v == int(v) else v

    def ostrzezenia(self):
        return T.bez_ostrzezenia_rozkladow(self.sw.ostrzezenia)


def klucz(uid):
    return G["klucz"] + str(uid)


@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py")
class TestZapisu(unittest.TestCase):
    def test_z1_domyslnie_wylaczony(self):
        self.assertFalse(D["zapis"]["wlaczony"], "zapis ma być domyślnie wyłączony (decyzja ludzi)")
        m = AR.Magazyn()
        s = Serwer(m, wlaczony=False)
        g = s.dolacz()
        self.assertEqual((s.k.atrybuty["ZapisAktywny"], s.k.atrybuty["ZapisStan"]), (False, "wyłączony"))
        self.assertIsNone(g.atrybuty.get("StanGraczaWczytany"), "bez zapisu nic się nie zmienia")
        self.assertEqual(s.atr(g, "Gems"), 1000)
        s.lup(g)
        s.wyjdz(g)
        s.zamknij()
        self.assertEqual((m.wywolania, m.rekordy), ([], {}))
        self.assertEqual(s.ostrzezenia(), [])

    def test_z2_zapis_i_odczyt_miedzy_sesjami(self):
        m = AR.Magazyn()
        a = Serwer(m)
        g = a.dolacz()
        self.assertEqual(a.atr(g, "StanGraczaWczytany"), True)
        self.assertEqual((a.atr(g, "Gems"), a.atr(g, "Gold"), a.atr(g, "StanGraczaZapis")), (G["start"]["gemy"], 0, "aktywny"),
                         "nowy gracz: wartości startowe zamiast testowych 1000 Gemów")
        self.assertEqual(m.rekordy[klucz(101)]["sesja"]["czas"] > 0, True, "sesja wzięta przy wczytaniu")
        g.ustaw("Class", "Mage")
        a.lup(g, zloto=500, doswiadczenie=12 + 35)  # → 3. poziom, 10 punktów
        self.assertEqual(a.atr(g, "Level"), 3)
        for _ in range(4):
            g.ustaw("Luck", a.atr(g, "Luck") + 1)
        kup = {"ile": 300, "zrodlo": "PetyProba", "cel": "jajko_lesne", "pet": "zoledziak", "premia": {"zloto": 0.05}}
        self.assertTrue(a.wywolaj("Pety", "kup", g.t, kup)["ok"])
        self.assertEqual(a.wywolaj("DanePakietu", "zapisz", g.t, "kowal", {"plus": {"miecz": 2}}), {"ok": True})
        g.ustaw("StrojProba_mag", "mag_kaptur,mag_szata")
        g.ustaw("PokonalStraznikaLasu", True)
        g.ustaw("Haker", 5)  # obcy atrybut — nie trafia do zapisu
        przed = {n: a.atr(g, n) for n in ("Level", "XP", "Gold", "Gems", "Class", "PunktyDoRozdania", "PetAktywny",
                                          "TokenyKrainy_las")}
        staty = {s: a.atr(g, at) for s, at in D["atrybuty_statystyk"].items()}
        a.wyjdz(g)
        r = m.rekordy[klucz(101)]
        self.assertIsNone(r.get("sesja"), "wyjście zwalnia sesję")
        self.assertEqual(r["profil"]["wersja"], D["wersja_profilu"])
        self.assertNotIn("Haker", r["profil"]["atrybuty"])
        # drugi serwer (inna sesja gry): gracz wchodzi z wartościami testowymi Pawła — wraca zapisany stan
        b = Serwer(m)
        g2 = b.dolacz()
        po = {n: b.atr(g2, n) for n in przed}
        self.assertEqual(po, przed)
        self.assertEqual({s: b.atr(g2, at) for s, at in D["atrybuty_statystyk"].items()}, staty,
                         "statystyki = rozkład klasy dla poziomu + trening + rozdane punkty")
        self.assertEqual((b.atr(g2, "StrojProba_mag"), b.atr(g2, "PokonalStraznikaLasu")), ("mag_kaptur,mag_szata", True))
        self.assertIsNone(g2.atrybuty.get("Haker"))
        self.assertEqual(b.wywolaj("DanePakietu", "czytaj", g2.t, "kowal"), {"plus": {"miecz": 2}})
        stan = b.wywolaj("Pety", "stan", g2.t)
        self.assertEqual((stan["kopie"], stan["aktywny"], stan["wydatki"]), ({"zoledziak": 1}, "zoledziak", {"jajko_lesne": 1}))
        self.assertEqual((a.ostrzezenia(), b.ostrzezenia()), ([], []))

    def test_z3_migracja_starego_profilu(self):
        m = AR.Magazyn()
        stary = next(c["dane"] for c in D["przypadki"]["migruj"] if isinstance(c["dane"], dict) and c["dane"].get("wersja") == 2)
        m.rekordy[klucz(7)] = {"profil": stary, "zapisano": 1}
        s = Serwer(m)
        g = s.dolacz(7)
        self.assertEqual((s.atr(g, "Level"), s.atr(g, "Gold"), s.atr(g, "PunktyDoRozdania")), (7, 340, 0),
                         "poziomy sprzed punktów do rozdania nie dają punktów wstecz")
        self.assertEqual(s.atr(g, "PetAktywny"), "zoledziak")
        s.wyjdz(g)
        self.assertEqual(m.rekordy[klucz(7)]["profil"]["wersja"], D["wersja_profilu"])
        self.assertEqual(m.rekordy[klucz(7)]["profil"]["pakiety"], {})

    def test_z4_blokada_sesji_dwa_serwery(self):
        m = AR.Magazyn()
        a = Serwer(m)
        ga = a.dolacz()
        a.lup(ga, zloto=50)
        # drugi serwer: świeża cudza sesja — czeka i próbuje, potem gra bez zapisu (nie przejmuje)
        b = Serwer(m)
        gb = b.dolacz()
        self.assertEqual(b.atr(gb, "StanGraczaWczytany"), False)
        b.sw.krok(G["czekaj_blokada_s"] * (G["proby_blokady"] + 1))
        self.assertEqual((b.atr(gb, "StanGraczaWczytany"), b.atr(gb, "StanGraczaZapis")), (True, "bez_zapisu"))
        sesja_a = m.rekordy[klucz(101)]["sesja"]["serwer"]
        b.lup(gb, zloto=999)
        b.wyjdz(gb)
        b.zamknij()
        self.assertEqual(m.rekordy[klucz(101)]["sesja"]["serwer"], sesja_a, "B nie ruszył rekordu A")
        # A zapisuje dalej (co co_s)
        n = len(m.wywolania)
        a.sw.krok(G["co_s"] + G["rozrzut_s"] + 1)
        self.assertGreater(len(m.wywolania), n)
        self.assertEqual(m.rekordy[klucz(101)]["profil"]["zloto"], 50)
        # A „padł” (bez zwolnienia); po blokada_s sesja jest przeterminowana — C przejmuje
        m.rekordy[klucz(101)]["sesja"]["czas"] -= G["blokada_s"] + 1
        c = Serwer(m)
        c.sw.czas = a.sw.czas  # zegary serwerów (os.time) wspólne
        gc = c.dolacz()
        self.assertEqual((c.atr(gc, "StanGraczaZapis"), c.atr(gc, "Gold")), ("aktywny", 50))
        sesja_c = m.rekordy[klucz(101)]["sesja"]["serwer"]
        self.assertNotEqual(sesja_c, sesja_a)
        # A ożywa i próbuje zapisać: utracona blokada — nie pisze i przestaje zapisywać tego gracza
        a.sw.krok(G["co_s"] + G["rozrzut_s"] + 1)
        self.assertEqual(m.rekordy[klucz(101)]["sesja"]["serwer"], sesja_c)
        self.assertTrue(any("utracona_blokada" in o for o in a.ostrzezenia()))
        self.assertEqual(a.atr(ga, "StanGraczaZapis"), "bez_zapisu")

    def test_z5_bledy_uslugi(self):
        m = AR.Magazyn()
        m.bledy = 2  # dwa pierwsze wywołania padają — wczytanie po ponowieniach
        s = Serwer(m)
        g = s.dolacz()
        s.sw.krok(10)
        self.assertEqual(s.atr(g, "StanGraczaZapis"), "aktywny")
        self.assertEqual(len(m.wywolania), 3)
        # zapis co jakiś czas: jeden błąd, ponowienie się udaje
        s.lup(g, zloto=77)
        m.bledy = 1
        s.sw.krok(G["co_s"] + G["rozrzut_s"] + G["odstep_s"] * 2 + 1)
        self.assertEqual(m.rekordy[klucz(101)]["profil"]["zloto"], 77)
        # zamknięcie serwera z błędami: ponawia w czasie BindToClose
        s.lup(g, zloto=3)
        m.bledy = 2
        s.zamknij()
        self.assertEqual(m.rekordy[klucz(101)]["profil"]["zloto"], 80)
        self.assertIsNone(m.rekordy[klucz(101)].get("sesja"))
        # wczytanie pada zawsze: gracz gra w pamięci, istniejący rekord NIE zostaje nadpisany
        m2 = AR.Magazyn()
        m2.rekordy[klucz(5)] = {"profil": dict(m.rekordy[klucz(101)]["profil"]), "zapisano": 1}
        m2.bledy = 100
        s2 = Serwer(m2)
        g2 = s2.dolacz(5)
        s2.sw.krok(60)
        self.assertEqual(s2.atr(g2, "StanGraczaZapis"), "bez_zapisu")
        self.assertEqual(s2.atr(g2, "Gems"), 1000, "bez zapisu — jak dziś (wartości Pawła)")
        m2.bledy = 0
        s2.lup(g2, zloto=1)
        s2.wyjdz(g2)
        s2.zamknij()
        self.assertEqual(m2.rekordy[klucz(5)]["profil"]["zloto"], 80, "stary rekord nietknięty")
        self.assertTrue(any("nie powiodło się" in o for o in s2.ostrzezenia()))

    def test_z6_zepsuty_i_przyszly_profil(self):
        for zepsuty, powod in (({"wersja": 4, "poziom": "x"}, "zla_wersja"), ({"wersja": 99, "poziom": 3}, "przyszla"),
                               ("tekst", "zly_profil")):
            m = AR.Magazyn()
            m.rekordy[klucz(9)] = {"profil": zepsuty, "zapisano": 1}
            s = Serwer(m)
            g = s.dolacz(9)
            self.assertEqual(s.atr(g, "StanGraczaZapis"), "bez_zapisu", zepsuty)
            self.assertEqual(s.atr(g, "Level"), 1)
            s.lup(g)
            s.wyjdz(g)
            s.zamknij()
            self.assertEqual(m.rekordy[klucz(9)]["profil"], zepsuty, "zepsuty / przyszły rekord nie jest nadpisany")
            self.assertIsNone(m.rekordy[klucz(9)].get("sesja"))
            self.assertTrue(any("odrzucony" in o for o in s.ostrzezenia()), powod)

    def test_z7_limit_rozmiaru(self):
        m = AR.Magazyn()
        s = Serwer(m)
        g = s.dolacz()
        s.lup(g, zloto=10)
        s.sw.krok(G["co_s"] + G["rozrzut_s"] + 1)
        self.assertEqual(m.rekordy[klucz(101)]["profil"]["zloto"], 10)
        duzy = {"w%d" % i: "x" * 190 for i in range(1500)}
        for i in range(12):
            self.assertEqual(s.wywolaj("DanePakietu", "zapisz", g.t, "pakiet%d" % i, duzy), {"ok": True})
        s.lup(g, zloto=5)
        s.sw.krok(G["co_s"] + G["rozrzut_s"] + 1)
        self.assertEqual(m.rekordy[klucz(101)]["profil"]["zloto"], 10, "za duży profil — bez zapisu częściowego")
        self.assertTrue(any("za_duzy" in o for o in s.ostrzezenia()))

    def test_z8_wyjscie_w_trakcie_zapisu_i_wczytywania(self):
        m = AR.Magazyn()
        s = Serwer(m)
        g = s.dolacz()
        s.lup(g, zloto=20)
        # gracz wychodzi DOKŁADNIE w trakcie zapisu co jakiś czas: ostatni zapis czeka w kolejce i idzie po nim
        g.ustaw("PokonalStraznikaLasu", True)
        m.podczas = lambda: s.wyjdz(g)
        s.sw.krok(G["co_s"] + G["rozrzut_s"] + 1)
        r = m.rekordy[klucz(101)]
        self.assertIsNone(r.get("sesja"))
        self.assertEqual((r["profil"]["zloto"], r["profil"]["atrybuty"].get("PokonalStraznikaLasu")), (20, True))
        # wyjście w trakcie wczytywania: sesja oddana, profil bez zmian
        m.podczas = None
        s3 = Serwer(m)
        g3 = s3.sw.gracz("Gracz101", dict(PAWEL))
        g3.t.set("UserId", 101.0)
        m.podczas = lambda: s3.wyjdz(g3)
        s3.sw.dolaczyl.odpal(g3.t)
        r = m.rekordy[klucz(101)]
        self.assertIsNone(r.get("sesja"))
        self.assertEqual(r["profil"]["zloto"], 20)
        self.assertEqual((s.ostrzezenia(), s3.ostrzezenia()), ([], []))

    def test_z9_zapytania_w_limitach(self):
        m = AR.Magazyn()
        s = Serwer(m)
        gracze = [s.dolacz(200 + i) for i in range(10)]
        s.sw.krok(2 * 3600)
        for g in gracze:
            s.wyjdz(g)
        s.zamknij()
        wyw = m.wywolania
        # na serwer: najwyżej 60 + 40 × gracze na minutę (UpdateAsync liczy się i do odczytów, i do zapisów)
        na_minute = {}
        for czas, _k, _s in wyw:
            na_minute[int(czas // 60)] = na_minute.get(int(czas // 60), 0) + 1
        self.assertLessEqual(max(na_minute.values()), 60 + 40 * 10)
        # jeden klucz: najwyżej jeden zapis na 6 s (ograniczenie DataStore na klucz)
        po_kluczu = {}
        for czas, k, _s in wyw:
            po_kluczu.setdefault(k, []).append(czas)
        for k, czasy in po_kluczu.items():
            odstepy = [b - a for a, b in zip(czasy, czasy[1:])]
            self.assertGreaterEqual(min(odstepy[:-1] or [99]), 6, k)  # ostatni: wyjście zaraz po zapisie — wolno
        srednio = len(wyw) / 10 / 120.0
        self.assertLess(srednio, 1.5, "ok. jeden zapis gracza na 2–2,5 min")

    def test_z10_studio_bez_dostepu(self):
        m = AR.Magazyn()
        m.blad_tekst = "StudioAccessToApisNotAllowed: Studio access to APIs is not allowed (atrapa)"
        m.bledy = 1000
        s = Serwer(m)
        g1 = s.dolacz(1)
        g2 = s.dolacz(2)
        self.assertEqual((s.atr(g1, "StanGraczaZapis"), s.atr(g2, "StanGraczaWczytany")), ("bez_zapisu", None))
        self.assertEqual(s.k.atrybuty["ZapisAktywny"], False)
        self.assertEqual(len(m.wywolania), 1, "po pierwszej odmowie dostępu nikt już nie pyta usługi")
        self.assertEqual(sum("wyłączony do końca sesji" in o for o in s.sw.ostrzezenia), 1)
        s.lup(g2)
        self.assertEqual(s.atr(g2, "Gold"), 21, "gra działa w pamięci")

    def test_z11_pamiec_biomu_z_zapisu(self):
        # PamiecGracza (las-pas, Bagno, Dżungla): przy aktywnym zapisie czyta atrybut gracza przywrócony z zapisu;
        # przy wyłączonym — dokładnie jak dawniej (tylko pamięć serwera)
        kod = T.czytaj(T.REPO, "swiat", "las_pas_gra", "zrodla", "PamiecGracza.luau")
        sw = AR.Swiat()
        stan = AR.Inst(sw, "StanGracza", "Folder", sw.workspace)
        modul = sw.it.wykonaj(kod, "PamiecGracza.luau")[0]
        g = sw.gracz("Gracz1", {"PokonalStraznikaLasu": True})
        g.t.set("UserId", 1.0)
        czytaj = modul.get("czytaj")
        self.assertFalse(sw.wolaj(czytaj, g.t, "pokonalStraznikaLasu")[0], "zapis nieaktywny — jak dawniej")
        stan.ustaw("ZapisAktywny", True)
        self.assertTrue(sw.wolaj(czytaj, g.t, "pokonalStraznikaLasu")[0])
        self.assertFalse(sw.wolaj(czytaj, g.t, "widzialPrzelotLasu")[0])
        sw.wolaj(modul.get("ustaw"), g.t, "widzialPrzelotLasu", True)
        self.assertTrue(sw.wolaj(czytaj, g.t, "widzialPrzelotLasu")[0])


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    unittest.main()
