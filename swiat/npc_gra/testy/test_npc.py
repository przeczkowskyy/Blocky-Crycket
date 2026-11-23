#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy pakietu swiat/npc_gra bez Studio (D-109).

    python -B swiat/npc_gra/testy/test_npc.py

1. Dane: obsada, rigi z modułów postaci (klipy, kości wzroku, stopy na ziemi, rozmiary źródeł), pliki w zrodla/
   aktualne, zapis deterministyczny.
2. Bazar: stanowiska = miejsca bazaru z polem „npc”; stopy i kierunek = część „Korzeń” figury z mapy; rola na
   tabliczce z miejsca bazaru; dane i skrypty bazaru bez zmian (DaneBazaru.luau aktualny).
3. Logika na lustrze w Pythonie: podejście gracza (budowa, usypianie, histereza), powitanie raz i ponownie po
   powrocie, gesty w odstępach, wzrok (granice, znak, gracz za plecami), numer klatki klipu.
4. LogikaNpc.luau wykonana interpreterem tools/walka/luau_mini.py = lustro (losowe wywołania); zepsute wersje
   logiki są wykrywane.
5. Punkty styku i zasady (czytane jak tekst): strażnik Studio, miejsce gry, tryb Edit, punkty historii, brak kolizji
   części NPC, tylko własny kontener, kotwica, brak ścieżek z dysku w plikach pakietu.
"""
import math
import os
import random
import re
import subprocess
import sys
import unittest

sys.dont_write_bytecode = True
TESTY = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TESTY)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (REPO, os.path.join(REPO, "tools", "walka")):
    if _s not in sys.path:
        sys.path.append(_s)
if PAKIET in sys.path:
    sys.path.remove(PAKIET)
sys.path.insert(0, PAKIET)
import dane as DN  # noqa: E402
import logika_npc as LN  # noqa: E402
import sprawdz_luau_npc as SPR  # noqa: E402
import zbuduj as ZB  # noqa: E402

try:
    import luau_mini as LM  # noqa: E402
except ImportError:                                     # interpreter może nie być w kopii repozytorium
    LM = None

U, D, R, PLIKI = DN.wszystkie_pliki()
ZR = os.path.join(PAKIET, "zrodla")
NOWE = [n for n in D["kolejnosc"] if n in R and n != "karczmarz"]      # postacie na wspólnym zestawie klipów


def czytaj(*czesci):
    with open(os.path.join(*czesci), encoding="utf-8") as f:
        return f.read()


# ============================================================================================== 1. dane
class TestDane(unittest.TestCase):
    def test_obsada(self):
        self.assertEqual(len(D["kolejnosc"]), 13)
        self.assertEqual(len(R), 12)                     # kowal ma rig w swoim pakiecie
        for nid in D["kolejnosc"]:
            n = D["npc"][nid]
            self.assertTrue(n["imie"] and n["rola"], nid)
            self.assertTrue(set(DN.LOGICZNE) <= set(n["klipy"]) <= set(DN.LOGICZNE) | {"akcja"}, nid)
        # Pancerz nie ma trenera-NPC: golem gry jest tam przeciwnikiem i trenerem naraz; postać golema zostaje zapasem
        self.assertEqual(sorted(D["trenerzy"]["gry"]), ["inteligencja", "kondycja", "sila", "szczescie", "zrecznosc"])
        self.assertNotIn("golem", D["trenerzy"]["gry"].values())
        self.assertIn("golem", R)
        self.assertEqual(D["npc"]["golem"]["skala"], U["trenerzy"]["skala_golema"])
        self.assertEqual(sorted(n for n in D["kolejnosc"] if "akcja" in D["npc"][n]["klipy"]), ["trener_kondycja", "trener_sila"])
        for nid in ("trener_sila", "trener_kondycja"):
            self.assertAlmostEqual(D["npc"][nid]["dlugosci"]["akcja"], U["trenerzy"]["akcja_s"], places=3)
        self.assertEqual(len(set(D["npc"][n]["imie"] for n in D["kolejnosc"])), 13, "imiona się powtarzają")

    def test_rigi(self):
        for nid, r in R.items():
            with self.subTest(npc=nid):
                n = D["npc"][nid]
                self.assertEqual(len(r["kosci"]), 15)
                self.assertEqual(r["kosci"][r["glowa"] - 1][0], "Head")
                self.assertEqual(r["kosci"][r["tulow"] - 1][0], "UpperTorso")
                self.assertLessEqual(abs(r["spod"]), 0.02, "stopy nie stoją na ziemi")
                self.assertTrue(40 <= len(r["czesci"]) <= 130, len(r["czesci"]))
                self.assertGreater(n["czubek"], 5.0)
                for rola in DN.LOGICZNE:
                    kl = r["klipy"][n["klipy"][rola]]
                    self.assertGreaterEqual(kl["fps"], 15)
                    for wiersz in kl["klatki"]:
                        self.assertEqual(len(wiersz), 6 * len(kl["kosci"]))
                    self.assertIn(r["glowa"], kl["kosci"], "klip %s nie rusza głowy (wzrok dokłada się do klipu)" % rola)
                    self.assertTrue(0.8 <= n["dlugosci"][rola] <= 4.0, (rola, n["dlugosci"][rola]))
                self.assertTrue(r["klipy"][n["klipy"]["spoczynek"]]["petla"])
                for c in r["czesci"]:
                    self.assertTrue(1 <= c[0] <= 15 and re.fullmatch(r"[0-9A-F]{6}", c[12]), c[:3])

    def test_klipy_wracaja_do_spoczynku(self):
        """Powitanie i gest nowych postaci kończą się w pozie, od której zaczynają (powrót bez skoku)."""
        for nid in NOWE:
            for rola in [r for r in ("powitanie", "gest", "akcja") if r in D["npc"][nid]["klipy"]]:
                kl = R[nid]["klipy"][D["npc"][nid]["klipy"][rola]]
                self.assertFalse(kl["petla"], (nid, rola))
                roznica = max(abs(a - b) for a, b in zip(kl["klatki"][0], kl["klatki"][-1]))
                self.assertLess(roznica, 1e-6, (nid, rola))
                ruch = max(abs(a - b) for w in kl["klatki"] for a, b in zip(w, kl["klatki"][0]))
                # „akcja” to jeden krótki ruch (uderzenie pałką ma mały zamach), więc próg jest niższy
                self.assertGreater(ruch, 0.3 if rola == "akcja" else 0.5, "%s %s: klip prawie się nie rusza" % (nid, rola))

    def test_pliki_aktualne_i_male(self):
        self.assertEqual(DN.nieaktualne(PLIKI), [])
        for nazwa, tekst in PLIKI.items():
            self.assertLess(len(tekst), U["limit_zrodla"], nazwa)
            self.assertTrue(tekst.startswith("--[["), nazwa)
            self.assertIn(DN.STRAZNIK.split("\n")[0], tekst, nazwa)
        self.assertIn(D["skrot"], PLIKI[DN.PLIK_DANYCH])

    def test_zapis_deterministyczny(self):
        _, D2, _, P2 = DN.wszystkie_pliki()
        self.assertEqual(D2["skrot"], D["skrot"])
        self.assertEqual(P2, PLIKI)

    def test_moduly_postaci(self):
        """Nowe postacie stoją na wspólnym ciele człowieka i mają wspólny zestaw klipów."""
        from swiat.postacie import npc_wspolne, rycerz
        self.assertEqual(npc_wspolne.WYMIARY, rycerz.WYMIARY)
        for w in U["npc"]:
            if w["modul"].startswith("npc_") and w["id"] != "golem":
                p = DN.postac_modulu(w)
                self.assertEqual(sorted(k.nazwa for k in p.klipy if k.nazwa != "akcja"), sorted(npc_wspolne.KLIPY), w["id"])
                self.assertEqual(p.wymiary("Head"), tuple(rycerz.WYMIARY["Head"]), w["id"])


# ============================================================================================== 2. bazar
class TestBazar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.S = DN.stanowiska_bazaru(U)
        cls.M = {m["id"]: m for m in DN.czytaj_json(DN.sciezka_repo(U["bazar"]["miejsca"]))["miejsca"]}
        cls.ZN = DN.czytaj_json(DN.sciezka_repo(U["bazar"]["znaczniki"]))

    def test_stanowiska_z_bazaru(self):
        self.assertEqual([s["klucz"] for s in self.S], [m for m in self.M if self.M[m].get("npc")])
        self.assertEqual(len(self.S), 6)
        self.assertEqual(len({s["npc"] for s in self.S}), 6)
        for s in self.S:
            m = self.M[s["klucz"]]
            self.assertEqual(s["npc"], m["npc"])
            self.assertEqual(s["rola"], "%s · %s" % (m["obiekt"], m["akcja_tekst"]))
            self.assertEqual(m["akcja"], "okno")
            self.assertIn(s["npc"], R)

    def test_miejsce_figury(self):
        """NPC stoi tam, gdzie figura: blisko punktu podpowiedzi E (ta jest przy figurze), twarzą jak znacznik."""
        for s in self.S:
            with self.subTest(miejsce=s["klucz"]):
                z = DN._znajdz(self.ZN, self.M[s["klucz"]]["znacznik"])
                self.assertEqual(z["model"], s["zastepuje"])
                pp = z["podpowiedz"]
                self.assertLess(math.hypot(pp[0] - s["poz"][0], pp[2] - s["poz"][2]), 1.5)
                self.assertTrue(0.3 <= s["poz"][1] <= 0.7, s["poz"])
                self.assertAlmostEqual(math.hypot(*s["kier"]), 1.0, places=3)
                # twarzą do miejsca, gdzie staje gracz
                st = z["stoisko"]
                dx, dz = st[0] - s["poz"][0], st[2] - s["poz"][2]
                self.assertGreater((dx * s["kier"][0] + dz * s["kier"][1]) / math.hypot(dx, dz), 0.7)
                # podpowiedź E zostaje w zasięgu gracza na stoisku i NPC jej nie zasłania częścią z kolizją
                n = D["npc"][s["npc"]]
                self.assertTrue(5.5 <= n["czubek"] * s["skala"] <= 10.5, n["czubek"] * s["skala"])

    def test_bazar_bez_zmian(self):
        r = subprocess.run([sys.executable, "-B", os.path.join(REPO, "swiat", "miasteczko_bazar_gra", "dane.py"), "--sprawdz"],
                           capture_output=True)
        self.assertEqual(r.returncode, 0, r.stdout.decode("utf-8", "replace"))
        tekst = czytaj(REPO, "swiat", "miasteczko_bazar_gra", "zrodla", "DaneBazaru.luau")
        self.assertNotIn("npc =", tekst, "pole npc nie powinno trafiać do DaneBazaru.luau")


# ============================================================================================== 3. logika (lustro)
N1 = D["npc"]["zbrojmistrz"]
Z, C, W = D["zasiegi"], D["czasy"], D["wzrok"]


def symuluj(odleglosci, dt=0.05, ziarno=1):
    """Kroki zachowania przy kolejnych odległościach gracza → lista (czas, polecenie)."""
    rnd = random.Random(ziarno)
    stan = LN.nowy_stan(rnd.random(), C)
    t, w = 0.0, []
    for odl in odleglosci:
        p = LN.krok(stan, odl, dt, rnd.random(), D, N1)
        if p:
            w.append((round(t, 2), p))
        t += dt
    return w, stan


class TestLogika(unittest.TestCase):
    def test_zasiegi_spojne(self):
        self.assertLess(Z["budowa"], Z["usuniecie"])
        self.assertLess(Z["animacja"], Z["uspienie"])
        self.assertLess(Z["blisko"], Z["animacja"])
        self.assertLess(Z["powitanie"], Z["pozegnanie"])
        self.assertLessEqual(Z["pozegnanie"], Z["gest"])
        self.assertLessEqual(Z["gest"], Z["animacja"])
        self.assertLessEqual(Z["uspienie"], Z["budowa"])
        self.assertLess(C["gest_min_s"], C["gest_max_s"])
        self.assertLessEqual(W["tulow_maks"] + W["glowa_maks"], math.radians(90), "głowa z tułowiem nie skręcą za plecy")

    def test_podejscie_i_odejscie(self):
        tryb, widziane = "brak", []
        for odl in [200 - i for i in range(196)] + [5 + i for i in range(196)]:
            nowy = LN.tryb(odl, tryb, Z)
            if nowy != tryb:
                widziane.append((odl, nowy))
                tryb = nowy
        self.assertEqual(widziane, [(Z["budowa"], "uspiony"), (Z["animacja"], "daleko"), (Z["blisko"], "blisko"),
                                    (Z["blisko"] + 1, "daleko"), (Z["uspienie"] + 1, "uspiony"),
                                    (Z["usuniecie"] + 1, "brak")])
        self.assertEqual(LN.tryb(None, "brak", Z), "brak")
        self.assertEqual(LN.tryb(None, "blisko", Z), "uspiony")
        self.assertEqual([LN.co_ile(t) for t in ("brak", "uspiony", "daleko", "blisko")], [0, 0, 2, 1])

    def test_histereza_bez_migotania(self):
        tryb, zmian = "uspiony", 0
        for i in range(400):
            odl = (Z["animacja"] + Z["uspienie"]) / 2 + (3 if i % 2 else -3)
            nowy = LN.tryb(odl, tryb, Z)
            zmian += nowy != tryb
            tryb = nowy
        self.assertEqual(zmian, 0)

    def test_powitanie_raz(self):
        w, _ = symuluj([40 - i * 0.5 for i in range(70)] + [5] * 100)
        powitania = [x for x in w if x[1] == "powitanie"]
        self.assertEqual(len(powitania), 1)
        # po powitaniu wraca do spoczynku dokładnie po długości klipu
        i = w.index(powitania[0])
        self.assertEqual(w[i + 1][1], "spoczynek")
        self.assertAlmostEqual(w[i + 1][0] - w[i][0], N1["dlugosci"]["powitanie"], delta=0.06)

    def test_powitanie_po_powrocie(self):
        blisko, daleko = [6] * 40, [35] * 40                                  # po 2 s
        w, _ = symuluj(blisko + daleko + blisko)                               # powrót po 2 s: bez drugiego powitania
        self.assertEqual(sum(1 for x in w if x[1] == "powitanie"), 1)
        dlugo = [35] * int((C["powitanie_odstep_s"] + 1) / 0.05)
        w, _ = symuluj(blisko + dlugo + blisko)
        self.assertEqual(sum(1 for x in w if x[1] == "powitanie"), 2)

    def test_gesty_w_odstepach(self):
        w, _ = symuluj([20] * int(120 / 0.05), ziarno=7)
        gesty = [t for t, p in w if p == "gest"]
        self.assertTrue(5 <= len(gesty) <= 12, gesty)
        for a, b in zip(gesty, gesty[1:]):
            przerwa = b - a - N1["dlugosci"]["gest"]
            self.assertTrue(C["gest_min_s"] - 0.1 <= przerwa <= C["gest_max_s"] + 0.1, przerwa)
        w, _ = symuluj([Z["gest"] + 5] * int(60 / 0.05))
        self.assertEqual(w, [], "gest bez widza")
        w, _ = symuluj([None] * 400)
        self.assertEqual(w, [])

    def test_wymus(self):
        stan = LN.nowy_stan(0.5, C)
        self.assertTrue(LN.wymus(stan, "gest", N1))
        self.assertEqual((stan["klip"], stan["zostalo"]), ("gest", N1["dlugosci"]["gest"]))
        self.assertIsNone(LN.krok(stan, 5, 0.1, 0.5, D, N1))
        self.assertEqual(LN.krok(stan, 5, N1["dlugosci"]["gest"], 0.5, D, N1), "spoczynek")
        self.assertFalse(LN.wymus(stan, "taniec", N1))
        self.assertFalse(LN.wymus(stan, "akcja", N1), "zbrojmistrz nie ma klipu akcja")
        sila = D["npc"]["trener_sila"]
        self.assertTrue(LN.wymus(stan, "akcja", sila))
        self.assertEqual((stan["klip"], stan["zostalo"]), ("akcja", sila["dlugosci"]["akcja"]))
        self.assertEqual(LN.krok(stan, 5, sila["dlugosci"]["akcja"], 0.5, D, sila), "spoczynek")

    def test_wzrok(self):
        self.assertEqual(LN.wzrok(0.0, 0.0, 10, W), (0, 0, 0))
        t, g, p = LN.wzrok(math.radians(40), math.radians(-10), 8, W)
        self.assertAlmostEqual(t + g, math.radians(40), places=6)
        self.assertTrue(0 < t <= W["tulow_maks"] and 0 < g <= W["glowa_maks"])
        self.assertAlmostEqual(p, math.radians(-10), places=6)
        t2, g2, _ = LN.wzrok(math.radians(-40), 0, 8, W)
        self.assertAlmostEqual(t2, -t, places=9)
        self.assertAlmostEqual(g2, -g, places=9)
        t, g, p = LN.wzrok(math.radians(110), math.radians(80), 8, W)
        self.assertAlmostEqual(t, W["tulow_maks"])
        self.assertAlmostEqual(g, W["glowa_maks"])
        self.assertAlmostEqual(p, W["pochyl_maks"])
        self.assertEqual(LN.wzrok(math.radians(150), 0, 8, W), (0, 0, 0))            # za plecami
        self.assertEqual(LN.wzrok(0.3, 0, W["zasieg"] + 1, W), (0, 0, 0))            # za daleko
        a = 0.0
        for _ in range(60):
            a = LN.wygladz(a, 1.0, 1 / 60, W["tempo"])
        self.assertTrue(0.98 < a <= 1.0)
        self.assertEqual(LN.wygladz(0.0, 1.0, 5.0, W["tempo"]), 1.0)                 # długa klatka nie przestrzeliwuje

    def test_klatka(self):
        self.assertEqual(LN.klatka(0, 15, 31, True), (0, 1, 0))
        self.assertEqual(LN.klatka(2.0, 15, 31, True), (0, 1, 0))                    # pętla 2 s wraca na początek
        i0, i1, a = LN.klatka(0.1, 15, 31, True)
        self.assertEqual((i0, i1), (1, 2))
        self.assertAlmostEqual(a, 0.5)
        self.assertEqual(LN.klatka(9.0, 15, 31, False), (30, 30, 0))                 # bez pętli staje na końcu
        self.assertEqual(LN.klatka(1.0, 15, 1, True), (0, 0, 0))


# ============================================================================================== 4. Luau = lustro
def luau_logika(tekst=None):
    it = LM.Interpreter()
    rs = LM.Tabela()
    rs.set("IsStudio", lambda _self: True)
    game = LM.Tabela()
    game.set("GetService", lambda _self, _n: rs)
    it.globalne.z["game"] = game
    return it, it.wykonaj(tekst if tekst is not None else czytaj(ZR, "LogikaNpc.luau"), "LogikaNpc.luau")[0]


def przebieg(wolaj, ziarno, ile=1500):
    """Losowe wywołania logiki przez `wolaj(nazwa, argumenty)` → lista wyników (porównywalna między językami)."""
    rnd = random.Random(ziarno)
    wyniki = []
    tryby = ["brak", "uspiony", "daleko", "blisko"]
    stany = [wolaj("nowy_stan", [rnd.random(), C]) for _ in range(4)]
    for _ in range(ile):
        co = rnd.randrange(6)
        if co == 0:
            odl = None if rnd.random() < 0.1 else rnd.choice([rnd.uniform(0, 220), rnd.choice(list(Z.values()))])
            wyniki.append(wolaj("tryb", [odl, rnd.choice(tryby), Z]))
        elif co in (1, 2):
            i = rnd.randrange(4)
            odl = None if rnd.random() < 0.05 else rnd.uniform(0, 70)
            n = D["npc"][rnd.choice(list(R))]
            wyniki.append(("krok", i, wolaj("krok", [stany[i], odl, rnd.choice([1 / 60, 1 / 30, 0.25, 3.0]), rnd.random(), D, n], stan=stany[i])))
        elif co == 3:
            wyniki.append(wolaj("wzrok", [rnd.uniform(-3.2, 3.2), rnd.uniform(-1.5, 1.5), rnd.uniform(0, 60), W]))
        elif co == 4:
            wyniki.append(wolaj("klatka", [rnd.uniform(-1, 12), rnd.choice([15, 30]), rnd.choice([1, 2, 21, 31]), rnd.random() < 0.5]))
        else:
            i = rnd.randrange(4)
            n = D["npc"][rnd.choice(["zbrojmistrz", "trener_sila"])]
            wyniki.append(("wymus", wolaj("wymus", [stany[i], rnd.choice(["gest", "powitanie", "spoczynek", "akcja", "x"]), n], stan=stany[i])))
    return wyniki


def wolaj_python(nazwa, argi, stan=None):
    w = getattr(LN, nazwa)(*argi)
    if nazwa == "nowy_stan":
        return w
    return (w, dict(stan)) if stan is not None else w


def _okragl(v):
    if isinstance(v, float):
        return round(v, 9)
    if isinstance(v, (list, tuple)):
        return [_okragl(x) for x in v]
    if isinstance(v, dict):
        return {k: _okragl(x) for k, x in v.items()}
    return v


@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py — Luau nie wykonany")
class TestLuau(unittest.TestCase):
    def _wolaj_luau(self, it, modul):
        def wolaj(nazwa, argi, stan=None):
            w = it.wywolaj(modul.get(nazwa), [a if isinstance(a, LM.Tabela) else LM.do_luau(a) for a in argi])
            if nazwa == "nowy_stan":
                return w[0]
            wynik = [LM.z_luau(x) for x in w]
            wynik = wynik[0] if len(wynik) == 1 else (None if not wynik else tuple(wynik))
            return (wynik, LM.z_luau(stan)) if stan is not None else wynik
        return wolaj

    def _porownaj(self, a, b):
        if isinstance(a, LM.Tabela):
            a = LM.z_luau(a)
        return _okragl(list(a) if isinstance(a, tuple) else a) == _okragl(list(b) if isinstance(b, tuple) else b)

    def test_luau_rowne_lustru(self):
        it, modul = luau_logika()
        for ziarno in (1, 2, 3):
            wl = przebieg(self._wolaj_luau(it, modul), ziarno)
            wp = przebieg(wolaj_python, ziarno)
            self.assertEqual(len(wl), len(wp))
            for i, (a, b) in enumerate(zip(wl, wp)):
                self.assertTrue(self._porownaj(a, b), "ziarno %d, wywołanie %d: Luau %r ≠ Python %r" % (ziarno, i, a, b))

    def test_zepsuta_logika_wykryta(self):
        """Każda z celowo zepsutych wersji LogikaNpc.luau musi dać inny wynik niż lustro."""
        dobry = czytaj(ZR, "LogikaNpc.luau")
        psucia = [("if odl > Z.uspienie then", "if odl > Z.animacja then"),
                  ("elseif odl <= Z.powitanie and not stan.powitany then", "elseif odl <= Z.powitanie then"),
                  ("stan.zostalo = n.dlugosci.gest\n\t\t\treturn \"gest\"", "stan.zostalo = 0\n\t\t\treturn \"gest\""),
                  ("local glowa = ogranicz(kat - tulow, -W.glowa_maks, W.glowa_maks)", "local glowa = ogranicz(kat, -W.glowa_maks, W.glowa_maks)"),
                  ("f = f - math.floor(f / ost) * ost", "f = f - math.floor(f / n) * n"),
                  ("if odl > Z.pozegnanie then", "if odl > Z.powitanie then"),
                  ("return a + (cel - a) * math.min(1, tempo * dt)", "return a + (cel - a) * tempo * dt")]
        wp = [_okragl(list(x) if isinstance(x, tuple) else x) for x in przebieg(wolaj_python, 5, 2500)]
        for stare, nowe in psucia:
            with self.subTest(psucie=nowe[:40]):
                self.assertEqual(dobry.count(stare), 1, "wzorzec psucia nie pasuje: " + stare)
                it, modul = luau_logika(dobry.replace(stare, nowe))
                try:
                    wl = przebieg(self._wolaj_luau(it, modul), 5, 2500)
                    rozne = any(not self._porownaj(a, b) for a, b in zip(wl, wp))
                except Exception:                      # zepsuta wersja może się wysypać — też wykryta
                    rozne = True
                if "tempo * dt" in nowe and not rozne:  # wygladz nie jest w losowych wywołaniach: sprawdź wprost
                    w = it.wywolaj(modul.get("wygladz"), [0.0, 1.0, 5.0, 5.0])[0]
                    rozne = abs(w - LN.wygladz(0.0, 1.0, 5.0, 5.0)) > 1e-9
                self.assertTrue(rozne, "zepsuta logika nieodróżnialna od dobrej")

    def test_zrodla_parsuja_sie(self):
        for nazwa in ("RigNpc.luau", "KlientNpc.client.luau", "SerwerNpc.server.luau", "LogikaNpc.luau", "DaneNpc.luau"):
            with self.subTest(plik=nazwa):
                LM.Parser(czytaj(ZR, nazwa), nazwa, LM.Interpreter()).program()

    def test_dane_w_luau_rowne_pythonowi(self):
        it, dane = luau_logika(PLIKI[DN.PLIK_DANYCH])
        d = LM.z_luau(dane)
        self.assertEqual(d["skrot"], D["skrot"])
        self.assertEqual(d["kolejnosc"], D["kolejnosc"])
        self.assertEqual(_okragl(d["zasiegi"]), _okragl({k: float(v) if isinstance(v, float) else v for k, v in Z.items()}))
        self.assertEqual([s["klucz"] for s in d["stanowiska"]], [s["klucz"] for s in D["stanowiska"]])
        _, rig = luau_logika(PLIKI["rigi/Rig_golem.luau"])
        r = LM.z_luau(rig)
        self.assertEqual(len(r["czesci"]), len(R["golem"]["czesci"]))
        self.assertEqual(sorted(r["klipy"]), sorted(R["golem"]["klipy"]))


# ============================================================================================== 5. styki i zasady
class TestZasady(unittest.TestCase):
    def test_kontrola_luau(self):
        self.assertEqual(SPR.sprawdz(), [])

    def test_czesci_bez_fizyki(self):
        rig = czytaj(ZR, "RigNpc.luau")
        for wlasnosc in ("CanCollide = false", "CanTouch = false", "CanQuery = false", "CastShadow = false", "Massless = true"):
            self.assertIn(wlasnosc, rig)
        self.assertEqual(rig.count("bezFizyki(") - 1, 3, "korzeń, kości i bryły bez fizyki")
        self.assertNotIn("Humanoid", rig)

    def test_klient_lokalny(self):
        kl = czytaj(ZR, "KlientNpc.client.luau")
        self.assertIn("LocalTransparencyModifier = 1", kl)
        self.assertIn("LocalTransparencyModifier = 0", kl)
        self.assertNotIn(".Transparency = ", kl.replace("p.Transparency = 1", ""), "figury chowamy tylko lokalnym modyfikatorem")
        for zakazane in ("FireServer", "InvokeServer", ":Destroy()\n\tend\n\ts.figura", "ProximityPrompt"):
            self.assertNotIn(zakazane, kl)
        for styk in ("D.tag_kotwicy", "D.wylacznik", '"Polecenie"', '"SterowanieKlienta"', "GetInstanceAddedSignal"):
            self.assertIn(styk, kl)
        ser = czytaj(ZR, "SerwerNpc.server.luau")
        self.assertIn("script.Parent:Destroy()", ser)
        self.assertNotIn("Instance.new", ser, "serwer niczego nie buduje")

    def test_budowniczy(self):
        zb = czytaj(PAKIET, "zbuduj.py")
        for wymagane in ("game.PlaceId ~= __MIEJSCE__", "IsRunning()", 'GetAttribute("Wygenerowane")', "SetWaypoint", "cel_studio"):
            self.assertIn(wymagane, zb)
        for zakazane in ("SavePlace", "PublishToRoblox", "game.Lighting", "upload", "InsertService"):
            self.assertNotIn(zakazane, zb)
        self.assertEqual([n for _, n, _, _, _ in ZB.zrodla(PLIKI)][:3], ["DaneNpc", "LogikaNpc", "RigNpc"])
        self.assertEqual(len(ZB.zrodla(PLIKI)), 3 + len(R) + 2)

    def test_kotwica(self):
        kod = ZB.kotwica_luau(U, "trener_sila", "trening_sila", (1, 0.5, 2), (1, 9), "workspace.X", skala=1.2)
        for wymagane in ('a:SetAttribute("Npc", "trener_sila")', 'a:SetAttribute("NpcKlucz", "trening_sila")',
                         'a:SetAttribute("NpcSkala", 1.2)', 'a:AddTag("%s")' % U["tag_kotwicy"], "a.CanCollide = false",
                         "a.Transparency = 1", "local rodzic = workspace.X"):
            self.assertIn(wymagane, kod)
        with self.assertRaises(DN.BladDanych):
            ZB.kotwica_luau(U, "nie_ma", "k", (0, 0, 0), (0, 1), "workspace")

    def test_trenerzy_z_pakietu_treningu(self):
        """Punkty trenerów pochodzą z danych pakietu treningu; kod budowniczego najpierw sprawdza arenę w Studio."""
        bez_punktu = []
        T = DN.punkty_trenerow(U, bez_punktu)
        self.assertEqual(bez_punktu, [])
        self.assertEqual({t["gra"]: t["npc"] for t in T}, U["trenerzy"]["gry"])
        self.assertEqual(len({t["klucz"] for t in T}), 5)
        self.assertNotIn("pancerz", [t["gra"] for t in T])
        # gra bez punktu w danych treningu jest pomijana, a pozostali trenerzy stają
        U2 = dict(U, trenerzy=dict(U["trenerzy"], gry=dict(U["trenerzy"]["gry"], pancerz="golem")))
        bez_punktu = []
        T2 = DN.punkty_trenerow(U2, bez_punktu)
        self.assertEqual(bez_punktu, ["pancerz"])
        self.assertEqual([t["gra"] for t in T2], [t["gra"] for t in T])
        for t in T:
            with self.subTest(gra=t["gra"]):
                self.assertIn(t["npc"], R)
                self.assertEqual(t["klucz"], "trening_" + t["gra"])
                self.assertGreater(math.hypot(t["patrz"][0] - t["poz"][0], t["patrz"][1] - t["poz"][2]), 5)
                self.assertTrue(1.0 <= t["skala"] <= 1.6)
                if t["zastepuje"]:
                    self.assertTrue(t["zastepuje"].startswith("Workspace/%s/Arena/" % t["kontener"]))
        self.assertEqual(next(t for t in T if t["gra"] == "kondycja")["zostaw"], ["Beben*", "NogaBebna*"])
        self.assertEqual(next(t for t in T if t["gra"] == "inteligencja")["zostaw"], ["Kula"])
        _, kod = ZB.kod_trenerow(U, dict(MIEJSCE="1", KONTENER=U["kontener"]))
        self.assertNotIn("__", kod)
        self.assertLess(kod.index("STOP: arena w Studio nie zgadza się"), kod.index('SetWaypoint("NpcGra: przed trenerami")'))
        for wymagane in ('a:SetAttribute("NpcZastepuje", t.zastepuje)', 'a:SetAttribute("NpcZostaw", t.zostaw)', "D.tylko_stan",
                         'zostaw = "Beben*,NogaBebna*"', 'npc = "trener_sila"'):
            self.assertIn(wymagane, kod)
        self.assertNotIn('"golem"', kod)
        if LM is not None:
            LM.Parser(kod, "TRENERZY", LM.Interpreter()).program()
        kl = czytaj(ZR, "KlientNpc.client.luau")
        self.assertIn('a:GetAttribute("NpcZostaw")', kl)
        self.assertIn("not zostaje(s, p.Name)", kl)

    def test_bez_sciezek_z_dysku(self):
        wzor = re.compile(r"[A-Za-z]:[\\/](?!/)|\\Users\\|/Users/|AppData|OneDrive", re.I)
        pliki = []
        for korzen, _, nazwy in os.walk(PAKIET):
            if "__pycache__" in korzen:
                continue
            pliki += [os.path.join(korzen, n) for n in nazwy if n.endswith((".py", ".luau", ".json", ".md"))]
        pliki += [os.path.join(REPO, "swiat", "postacie", n) for n in os.listdir(os.path.join(REPO, "swiat", "postacie"))
                  if n.startswith("npc_") and n.endswith(".py")]
        self.assertGreater(len(pliki), 25)
        for p in pliki:
            if os.path.abspath(p) == os.path.abspath(__file__):
                continue
            m = wzor.search(czytaj(p))
            self.assertIsNone(m, "%s: %r" % (os.path.relpath(p, REPO), m.group(0) if m else ""))


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    unittest.main(verbosity=1)
