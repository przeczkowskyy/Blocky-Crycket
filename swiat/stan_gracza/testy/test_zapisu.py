# -*- coding: utf-8 -*-
"""Testy zapisu postępu (18.11.2026; włączony 19.11.2026 decyzją D-110) — bez Studio, bez sieci.

    python -B swiat/stan_gracza/testy/test_zapisu.py

PRAWDZIWY SerwerStanu.server.luau + Moduly/ZapisStanu w luau_mini, z atrapą DataStore (testy/atrapa_roblox.Magazyn)
wspólną dla kilku serwerów: zapis i odczyt między sesjami, migracja, dwa serwery naraz (blokada sesji), błąd usługi
przy wczytaniu, zapisie i zamknięciu serwera, zepsuty i przyszły profil, limit rozmiaru, wyjście gracza w trakcie
zapisu i wczytywania, liczba zapytań w czasie, Studio bez dostępu do usług danych, zapis domyślnie włączony i wyłącznik
atrybutem, pamięć biomu (PamiecGracza) z zapisu, dane treningu w profilu; 19.11.2026 (D-110): próby gry ze znacznikiem
tools/zapis_prob.py nie otwierają magazynu (prawdziwy rekord nietknięty), magazyn próby zapisu i atrapa błędów usługi,
znacznik z „trybu Edit” do serwera i kolejność wywołań MCP (StudioMCP.call → zapis_prob). Lustro logiki (migracja, sprawdzanie profilu) jest w test_stanu.py (przypadki).
"""
import os
import sys
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
for _s in (TU, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(TU))), "tools")):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import test_stanu as T  # noqa: E402
import atrapa_roblox as AR  # noqa: E402

LM, D, LS, ZB = T.LM, T.D, T.LS, T.ZB
ZAPIS = T.czytaj(T.ZR, "ZapisStanu.luau")
G = D["zapis"]
PR = G["proba"]  # znacznik próby gry (19.11.2026, D-110; tools/zapis_prob.py)
PAWEL = dict(T.TestSerweraOffline.PAWEL)
LUP = dict(T.TestSerweraOffline.LUP)


class Serwer:
    """Jeden serwer z kontenerem StanGracza i wspólnym magazynem."""

    def __init__(self, magazyn, wlaczony=True, atrybuty=None):
        """wlaczony: True / False = atrybut kontenera ZapisPostepu, None = bez atrybutu (domyślnie z DaneStanu);
        atrybuty: inne atrybuty kontenera przed startem serwera (np. znacznik próby — jak skopiowany z trybu Edit)."""
        sw = AR.Swiat()
        if magazyn is not None:
            magazyn.dodaj_do(sw)
        k, inne = AR.kontener_stanu(sw, {"DaneStanu": T.czytaj(T.ZR, "DaneStanu.luau"), "LogikaStanu": T.LOGIKA,
                                         "ZapisStanu": ZAPIS}, ZB.INNE)
        k.ustaw(D["poczatek"]["atrybut_wylacznika"], False)
        k.ustaw(G["atrybut"], wlaczony)
        for n, v in (atrybuty or {}).items():
            k.ustaw(n, v)
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
    def test_z1_domyslnie_wlaczony_wylacznik_atrybutem(self):
        self.assertTrue(D["zapis"]["wlaczony"], "zapis włączony decyzją D-110 (19.11.2026)")
        # bez atrybutu kontenera: domyślnie z DaneStanu — włączony, magazyn Studio
        m0 = AR.Magazyn()
        s0 = Serwer(m0, wlaczony=None)
        g0 = s0.dolacz()
        self.assertEqual((s0.k.atrybuty["ZapisAktywny"], s0.k.atrybuty["ZapisStan"], s0.k.atrybuty["ZapisMagazyn"]),
                         (True, "włączony", G["magazyn"] + G["przyrostek_studio"]))
        self.assertEqual((s0.atr(g0, "StanGraczaWczytany"), s0.atr(g0, "StanGraczaZapis")), (True, "aktywny"))
        self.assertEqual(m0.nazwy, [G["magazyn"] + G["przyrostek_studio"]])
        self.assertIsInstance(s0.atr(g0, "StanGraczaWczytanieMs"), int, "czas wczytania dla próby zapisu")
        # wyłącznik: ZapisPostepu = false — jak przed zapisem, magazyn nietknięty
        m = AR.Magazyn()
        s = Serwer(m, wlaczony=False)
        g = s.dolacz()
        self.assertEqual((s.k.atrybuty["ZapisAktywny"], s.k.atrybuty["ZapisStan"]), (False, "wyłączony"))
        self.assertIsNone(s.k.atrybuty.get("ZapisMagazyn"))
        self.assertIsNone(g.atrybuty.get("StanGraczaWczytany"), "bez zapisu nic się nie zmienia")
        self.assertEqual(s.atr(g, "Gems"), 1000)
        s.lup(g)
        s.wyjdz(g)
        s.zamknij()
        self.assertEqual((m.wywolania, m.rekordy, m.nazwy), ([], {}, []))
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
        # 19.11.2026: trening (pasek malejącego zysku) przez DanePakietu — pakiet „trening” (SerwerTreningu)
        TR = {"w": {"TreningSila": 7}, "paski": {"sila": 2.5}}
        self.assertEqual(a.wywolaj("DanePakietu", "zapisz", g.t, "trening", TR), {"ok": True})
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
        self.assertEqual(b.wywolaj("DanePakietu", "czytaj", g2.t, "trening"), TR)
        stan = b.wywolaj("Pety", "stan", g2.t)
        self.assertEqual((stan["kopie"], stan["aktywny"], stan["wydatki"]), ({"zoledziak": 1}, "zoledziak", {"jajko_lesne": 1}))
        self.assertEqual((a.ostrzezenia(), b.ostrzezenia()), ([], []))

    def test_z2b_rasa_miedzy_sesjami(self):
        """27.11.2026 (Karol: „Tak, zapisuj rasę”): Race wraca razem z Class; profil bez rasy = gracz bez rasy (ekran
        wyboru jak dotąd); rasa spoza RaceData nie trafia do zapisu."""
        self.assertIn("idRasy", G["pola"])
        self.assertEqual(D["atrybuty"]["rasa"], "Race")
        self.assertIn("Elf", D["rasy_gracza"])
        m = AR.Magazyn()
        a = Serwer(m)
        g = a.dolacz()
        g.ustaw("Class", "Scout")
        g.ustaw("Race", "Elf")
        a.wyjdz(g)
        prof = m.rekordy[klucz(101)]["profil"]
        self.assertEqual((prof.get("idKlasy"), prof.get("idRasy"), prof["wersja"]), ("Scout", "Elf", D["wersja_profilu"]))
        b = Serwer(m)
        g2 = b.dolacz()
        self.assertEqual((b.atr(g2, "Class"), b.atr(g2, "Race")), ("Scout", "Elf"), "rasa i klasa wracają z zapisu")
        b.wyjdz(g2)
        # stary profil (przed 27.11) bez pola idRasy: klasa wraca, rasy nie ma — jak dotąd
        stary = dict(m.rekordy[klucz(101)]["profil"])
        del stary["idRasy"]
        m.rekordy[klucz(101)] = {"profil": stary, "zapisano": 1}
        c = Serwer(m)
        g3 = c.dolacz()
        self.assertEqual((c.atr(g3, "Class"), g3.atrybuty.get("Race")), ("Scout", None))
        self.assertEqual(c.atr(g3, "StanGraczaZapis"), "aktywny", "stary profil przyjęty")
        # rasa spoza listy (atrybut ustawiony obok serwera wyboru) — do zapisu nie idzie
        g3.ustaw("Race", "Robot")
        c.wyjdz(g3)
        self.assertIsNone(m.rekordy[klucz(101)]["profil"].get("idRasy"))
        self.assertEqual((a.ostrzezenia(), b.ostrzezenia(), c.ostrzezenia()), ([], [], []))

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

    # ---------------------------------------------------------------- próby gry bez prawdziwego zapisu (19.11.2026, D-110)
    def prawdziwy_rekord(self):
        """Magazyn z prawdziwym zapisem człowieka (gracz 101: 3. poziom, 500 Złota, Strażnik Lasu) po zwykłej sesji."""
        m = AR.Magazyn()
        s = Serwer(m, wlaczony=None)
        g = s.dolacz()
        s.lup(g, zloto=500, doswiadczenie=47)
        g.ustaw("PokonalStraznikaLasu", True)
        s.wyjdz(g)
        s.zamknij()
        self.assertEqual(m.rekordy[klucz(101)]["profil"]["poziom"], 3)
        return m, LM.z_luau(LM.do_luau(m.rekordy))

    def test_z12_proba_gry_nie_czyta_i_nie_pisze_prawdziwego_zapisu(self):
        m, kopia = self.prawdziwy_rekord()
        m.wywolania, m.nazwy = [], []
        teraz = AR.Swiat().czas
        s = Serwer(m, wlaczony=None, atrybuty={PR["atrybut_do"]: teraz + PR["czas_s"]})
        self.assertEqual((s.k.atrybuty["ZapisAktywny"], s.k.atrybuty["ZapisStan"]), (False, "wyłączony (próba gry)"))
        self.assertIsNone(s.k.atrybuty.get("ZapisMagazyn"))
        g = s.dolacz(101)
        self.assertIsNone(g.atrybuty.get("StanGraczaWczytany"), "próba: gracz od razu, bez wczytywania")
        self.assertEqual((s.atr(g, "Level"), s.atr(g, "Gems"), g.atrybuty.get("PokonalStraznikaLasu")), (1, 1000, None),
                         "świeży gracz jak przed D-110 (wartości testowe Pawła), nie zapis człowieka")
        s.lup(g, zloto=999, doswiadczenie=500)
        s.sw.krok(3 * (G["co_s"] + G["rozrzut_s"]))
        s.wyjdz(g)
        s.zamknij()
        self.assertEqual((m.wywolania, m.nazwy), ([], []), "próba nawet nie otworzyła magazynu")
        self.assertEqual(m.rekordy, kopia, "prawdziwy zapis nietknięty")
        self.assertEqual(s.ostrzezenia(), [])
        # znacznik przeterminowany (próba padła przed Stop, minął kwadrans): zwykła gra człowieka — zapis wraca
        s2 = Serwer(m, wlaczony=None, atrybuty={PR["atrybut_do"]: teraz - 1})
        g2 = s2.dolacz(101)
        self.assertEqual((s2.atr(g2, "Level"), s2.atr(g2, "Gold"), s2.atr(g2, "PokonalStraznikaLasu")), (3, 500, True))
        self.assertEqual(m.nazwy, [G["magazyn"] + G["przyrostek_studio"]])
        # sam „magazyn próby” bez znacznika nic nie zmienia (stary atrybut po padniętej próbie zapisu)
        m.nazwy = []
        s2.wyjdz(g2)
        s3 = Serwer(m, wlaczony=None, atrybuty={PR["atrybut_magazynu"]: True, PR["atrybut_bledow"]: 50})
        g3 = s3.dolacz(101)
        self.assertEqual((m.nazwy, s3.atr(g3, "Level"), s3.atr(g3, "StanGraczaZapis")),
                         ([G["magazyn"] + G["przyrostek_studio"]], 3, "aktywny"))
        self.assertEqual(s3.k.atrybuty.get(PR["atrybut_bledow"]), 50, "atrapa błędów działa tylko w magazynie próby")

    def test_z13_magazyn_proby_zapisu_i_bledy(self):
        m, kopia = self.prawdziwy_rekord()
        teraz = AR.Swiat().czas
        nazwa = G["magazyn"] + G["przyrostek_studio"] + PR["przyrostek"]
        znacznik = {PR["atrybut_do"]: teraz + PR["czas_s"], PR["atrybut_magazynu"]: True}
        # magazyn próby: osobna nazwa (atrapa trzyma rekordy po kluczu, więc nazwę sprawdzamy wprost)
        mp = AR.Magazyn()
        s = Serwer(mp, wlaczony=False, atrybuty=znacznik)  # ZapisPostepu = false człowieka nie blokuje próby zapisu
        self.assertEqual((s.k.atrybuty["ZapisStan"], s.k.atrybuty["ZapisMagazyn"]), ("włączony (magazyn próby)", nazwa))
        g = s.dolacz(101)
        self.assertEqual((s.atr(g, "StanGraczaZapis"), s.atr(g, "Gold"), s.atr(g, "Gems")), ("aktywny", 0, G["start"]["gemy"]))
        s.lup(g, zloto=40)
        s.wyjdz(g)
        self.assertEqual(mp.nazwy, [nazwa])
        self.assertEqual(mp.rekordy[klucz(101)]["profil"]["zloto"], 40)
        # błąd usługi przy wczytaniu: 2 wywołania padają — wczytanie po ponowieniach
        s2 = Serwer(mp, wlaczony=None, atrybuty=dict(znacznik, **{PR["atrybut_bledow"]: 2}))
        g2 = s2.dolacz(101)
        s2.sw.krok(10)
        self.assertEqual((s2.atr(g2, "StanGraczaZapis"), s2.atr(g2, "Gold")), ("aktywny", 40))
        self.assertEqual(s2.k.atrybuty[PR["atrybut_bledow"]], 0)
        s2.wyjdz(g2)
        zapisano = mp.rekordy[klucz(101)]["zapisano"]
        # usługa pada cały czas: gra w pamięci, rekord NIE nadpisany pustym profilem
        s3 = Serwer(mp, wlaczony=None, atrybuty=dict(znacznik, **{PR["atrybut_bledow"]: 1000}))
        g3 = s3.dolacz(101)
        s3.sw.krok(60)
        self.assertEqual((s3.atr(g3, "StanGraczaWczytany"), s3.atr(g3, "StanGraczaZapis")), (True, "bez_zapisu"))
        zl0 = s3.atr(g3, "Gold")
        s3.lup(g3, zloto=7)
        self.assertEqual(s3.atr(g3, "Gold"), zl0 + 7, "gra działa w pamięci")
        s3.wyjdz(g3)
        s3.zamknij()
        self.assertEqual((mp.rekordy[klucz(101)]["profil"]["zloto"], mp.rekordy[klucz(101)]["zapisano"]), (40, zapisano))
        self.assertTrue(any("nie powiodło się" in o for o in s3.ostrzezenia()))

    def test_z14_znacznik_z_tools_zapis_prob(self):
        """Całość jak w Studio: tools/zapis_prob.py ustawia znacznik w „trybie Edit”, Play kopiuje atrybuty kontenera,
        serwer stanu nie dotyka prawdziwego zapisu; po Stop znacznik zdjęty — i kolejność wywołań MCP."""
        import zapis_prob as ZP
        self.assertEqual((ZP.ATR_DO, ZP.ATR_MAGAZYNU, ZP.ATR_BLEDOW, ZP.CZAS_S, ZP.KONTENER),
                         (PR["atrybut_do"], PR["atrybut_magazynu"], PR["atrybut_bledow"], PR["czas_s"], D["kontener"]))
        self.assertIn(PR["atrybut_do"], ZB.ATRYBUTY_TESTOWE, "znacznik przechodzi na odbudowany kontener")
        # „Edit”: kontener jak po zbuduj.py
        edit = AR.Swiat()
        edit.uslugi["RunService"].t.set("IsRunning", lambda _s: False)
        k, _ = AR.kontener_stanu(edit, {"DaneStanu": "", "LogikaStanu": ""}, [])
        k.ustaw("ZapisPostepu", None)
        w = edit.it.wykonaj(ZP.LUAU_START, "start")[0]
        self.assertTrue(w.startswith("OK"), w)
        self.assertEqual(k.atrybuty[PR["atrybut_do"]], int(edit.czas) + PR["czas_s"])
        # Play: kopia atrybutów kontenera z Edit → serwer
        m, kopia = self.prawdziwy_rekord()
        m.wywolania, m.nazwy = [], []
        s = Serwer(m, wlaczony=None, atrybuty={n: v for n, v in k.atrybuty.items() if n.startswith("Zapis")})
        g = s.dolacz(101)
        s.lup(g, zloto=5)
        s.wyjdz(g)
        s.zamknij()
        self.assertEqual((m.wywolania, m.nazwy, m.rekordy), ([], [], kopia))
        # próba zapisu: magazyn próby (kod_magazynu) — i Stop zdejmuje wszystkie trzy znaczniki
        self.assertEqual(edit.it.wykonaj(ZP.kod_magazynu(3), "magazyn")[0], "OK")
        self.assertEqual((k.atrybuty[PR["atrybut_magazynu"]], k.atrybuty[PR["atrybut_bledow"]]), (True, 3))
        self.assertEqual(edit.it.wykonaj(ZP.LUAU_KONIEC, "koniec")[0], "OK")
        self.assertFalse(any(n.startswith("ZapisProba") for n in k.atrybuty), k.atrybuty)
        # bez kontenera: nic do zrobienia; w trybie Play: STOP
        k.usun()
        self.assertEqual(edit.it.wykonaj(ZP.LUAU_START, "start")[0], "BRAK")
        edit.uslugi["RunService"].t.set("IsRunning", lambda _s: True)
        self.assertTrue(edit.it.wykonaj(ZP.LUAU_START, "start")[0].startswith("STOP"))

        # kolejność wywołań MCP (atrapa mostka): znacznik → Play; Stop → zdjęcie; błąd znacznika → Play NIE startuje
        def mostek(odpowiedzi):
            log = []

            def wywolaj(n, a, t=None):
                log.append((n, a.get("datamodel_type"), a.get("is_start"), a.get("studio_id")))
                return odpowiedzi(n, a)
            return log, wywolaj
        log, wyw = mostek(lambda n, a: {"text": "OK 1" if n == "execute_luau" else "ok", "is_error": False})
        ZP.play(wyw, {"is_start": True, "studio_id": "S1"})
        ZP.play(wyw, {"is_start": False, "studio_id": "S1"})
        self.assertEqual([(n, dm, sid) for n, dm, _, sid in log],
                         [("execute_luau", "Edit", "S1"), ("start_stop_play", None, "S1"), ("execute_luau", "Server", "S1"),
                          ("start_stop_play", None, "S1"), ("execute_luau", "Edit", "S1")])
        log, wyw = mostek(lambda n, a: {"text": "STOP: znacznik próby się nie ustawił", "is_error": False}
                          if n == "execute_luau" else {"text": "ok", "is_error": False})
        with self.assertRaises(RuntimeError):
            ZP.play(wyw, {"is_start": True})
        self.assertEqual([n for n, *_ in log], ["execute_luau"], "bez znacznika Play nie startuje")
        log, wyw = mostek(lambda n, a: {"text": "Studio nie odpowiada", "is_error": True}
                          if n == "execute_luau" else {"text": "ok", "is_error": False})
        with self.assertRaises(RuntimeError):
            ZP.play(wyw, {"is_start": True})
        self.assertEqual([n for n, *_ in log], ["execute_luau"])
        # StudioMCP.call kieruje start_stop_play przez zapis_prob (bez mostka: podmieniamy _call)
        import studio_mcp as SM
        klient = SM.StudioMCP()
        log, wyw = mostek(lambda n, a: {"text": "OK 1" if n == "execute_luau" else "ok", "is_error": False})
        klient._call = wyw
        klient.call("start_stop_play", {"is_start": True})
        klient.call("get_studio_state", {})
        self.assertEqual([n for n, *_ in log], ["execute_luau", "start_stop_play", "execute_luau", "get_studio_state"],
                         "znacznik → Play → odczyt ZapisStan z serwera do dziennika → dalej bez opakowania")


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    unittest.main()
