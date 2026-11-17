#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Przenikanie broni w głowę i tułów — LICZBOWO, we wszystkich klipach aktorów walki i w przejściach (bez Studio).

    python -B swiat/test_walki2/testy/test_przenikania.py            # ok. 2 min (4 rdzenie)
    python -B swiat/test_walki2/testy/test_przenikania.py -v

Uwaga Karola z panelu (13.11): broń trzymana w ręku nie może nachodzić na twarz w żadnej animacji ani po wygranej
walce. Narzędzie: swiat/postacie/przenikanie/ (opis miar i progów w pomiar.py, wyniki w WYNIKI.md).

Pilnuje, żeby:
- lustro gry (pozy.py: Klipy.luau + stawy Motor6D) dawało te same pozy co swiat/test_walki2/geometria.py i liczby
  zmierzone w Studio (Bariera Maga, blok i unik Wojownika);
- w KAŻDYM klipie każdego aktora z bronią w ręku (dane/<klucz>.json — także w nowych klipach i u nowych aktorów,
  których broń da się rozpoznać po nazwie grupy albo kości), próbkowanym 120 razy na sekundę z Lerp między klatkami jak
  w grze, oraz w przejściach, które gra robi (spoczynek → akcja, akcja → spoczynek, → upadek, wskrzeszenie, →
  radość), broń nie wchodziła w głowę głębiej niż PROG_GLOWA (0,02 studa) ani w tułów głębiej niż PROG_TULOW (0,10);
- z kamery finału broń nie zasłaniała oczu ani rysów twarzy klasy: w radości i postawie z przodu (kąt twarzy do 35°)
  i na początku objazdu, gdy zwycięzca kończy obrót do kamery (OBROT_ZWYCIEZCY czytane z odtwarzacza);
- broń nie obracała się wokół własnej osi szybciej niż PM.PROG_SKRETU (70°) na klatkę w żadnym klipie;
- celowo zepsuty klip (miecz przez hełm) oblewał test.
Wskrzeszenie i finał liczone są tak, jak robi to dzisiejszy odtwarzacz (narzędzie czyta jego kod; test pilnuje, że
wzorzec pasuje). Znane przypadki z sufitem (ZNANE) — dziś żadnych.
"""
import os
import sys
import unittest

import numpy as np

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
KATALOG = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(KATALOG))
NARZEDZIE = os.path.join(REPO, "swiat", "postacie", "przenikanie")
for _s in (KATALOG, REPO, NARZEDZIE):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import aktorzy as A  # noqa: E402
import bryly as B  # noqa: E402
import kamera as K  # noqa: E402
import pomiar as PM  # noqa: E402
from geometria import Rig  # noqa: E402
from pozy import Aktor  # noqa: E402

GESTOSC = 0.5      # przejścia: 4 fazy spoczynku, 60 próbek/s, prędkość ×1 (klipy zawsze 120/s) — pełne: przenikanie.py

# Znane przypadki z sufitem: {(klucz, rodzaj scenariusza): {strefa: największa dopuszczalna głębokość}} — gorzej =
# błąd, a wpis, którego przypadek zniknął, też jest błędem (test_znane_wpisy_nadal_potrzebne). Do 17.11.2026 były tu
# dwa wskrzeszenia (Wojownik tułów 0,181, Mag głowa 0,219 / tułów 0,154) — mieszanie leżenia ze spoczynkiem
# w odtwarzaczu; od 17.11.2026 Obsluga.wskrzeszenie gra upadek wstecz i wpisy są zbędne.
ZNANE = {}

_WYNIKI = {}


def zbadaj(klucz):
    if klucz not in _WYNIKI:
        d = A.wczytaj(klucz)
        pm = PM.Pomiar(d, PM.spec_aktora(klucz, d))
        sc = PM.scenariusze(pm.a, A.PO_KLUCZU.get(klucz), GESTOSC)
        _WYNIKI[klucz] = (pm, PM.zmierz(pm, sc))
    return _WYNIKI[klucz]


def aktorzy_z_bronia():
    wyn = []
    for w in A.AKTORZY:
        try:
            d = A.wczytaj(w["klucz"])
        except FileNotFoundError:
            continue
        if PM.spec_aktora(w["klucz"], d):
            wyn.append(w["klucz"])
    return wyn


class LustroGry(unittest.TestCase):
    def test_pozy_jak_geometria(self):
        # pozy.py (numpy) = geometria.py (istniejące lustro szablon.luau + Klipy.luau) w klatkach danych
        for w in A.AKTORZY:
            d = A.wczytaj(w["klucz"])
            a, r = Aktor(d), Rig(d)
            mx = 0.0
            for kl in d["klipy"]:
                for f in range(0, kl["dl"] + 1, 5):
                    Wk, Wb = a.poza([(kl["n"], f / float(kl["fps"]), 1.0)])
                    pz = r.pozy(r.transformy(kl["n"], f))
                    for i in range(1, a.nk + 1):
                        mx = max(mx, np.abs(np.array(pz[i][0]) - Wk[i, :3, :3]).max(),
                                 np.abs(np.array(pz[i][1]) - Wk[i, :3, 3]).max())
                    for b in range(0, a.nb, 11):
                        R, t = r.czesc_cf(d["czesci"][b], pz)
                        mx = max(mx, np.abs(np.array(t) - Wb[b, :3, 3]).max())
            self.assertLess(mx, 1e-9, "%s: pozy.py ≠ geometria.py (%.2e)" % (w["klucz"], mx))

    def test_mieszanie_torow_jak_klipy_luau(self):
        # dwa tory: waga nowego 0 = stary klip, 1 = nowy klip; Lerp w połowie klatki leży między klatkami
        a = Aktor(A.wczytaj("wojownik"))
        p0, q0 = a.transformy([("idle", 0.3, 1.0), ("atak_miecz", 0.2, 0.0)])
        p1, q1 = a.transformy([("idle", 0.3, 1.0)])
        self.assertLess(np.abs(p0 - p1).max() + np.abs(np.abs(np.sum(q0 * q1, axis=1)) - 1).max(), 1e-9)
        p0, q0 = a.transformy([("idle", 0.3, 0.0), ("atak_miecz", 0.2, 1.0)])
        p1, q1 = a.transformy([("atak_miecz", 0.2, 1.0)])
        self.assertLess(np.abs(p0 - p1).max() + np.abs(np.abs(np.sum(q0 * q1, axis=1)) - 1).max(), 1e-9)
        pa, _ = a.transformy([("atak_miecz", 10 / 30.0, 1.0)])
        pb, _ = a.transformy([("atak_miecz", 11 / 30.0, 1.0)])
        pm_, _ = a.transformy([("atak_miecz", 10.5 / 30.0, 1.0)])
        self.assertLess(np.abs(pm_ - (pa + pb) / 2).max(), 1e-9)

    def test_liczby_ze_studio(self):
        # pomiary z prób w Studio (README pakietu, etap 9 i 17.11.2026) liczone tym samym lustrem
        d = A.wczytaj("mag")
        a = Aktor(d)
        lt = a.indeks["LowerTorso"]
        W0, _ = a.poza([("idle", 0.0, 1.0)])
        biodra, najnizej = 0.0, 9.0
        for f in range(a.klipy["bariera"]["dl"] + 1):
            W, Wb = a.poza([("bariera", f / 30.0, 1.0)])
            biodra = max(biodra, W[lt, 1, 3] - W0[lt, 1, 3])
            for b in range(a.nb):
                h = np.array(d["czesci"][b][9:12]) / 2
                rogi = np.array([[x * h[0], y * h[1], z * h[2]] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)])
                najnizej = min(najnizej, float((rogi @ Wb[b, :3, :3].T + Wb[b, :3, 3])[:, 1].min()))
        self.assertAlmostEqual(biodra, 0.20, delta=0.02, msg="Bariera: biodra w Studio +0,20")
        self.assertLess(abs(najnizej), 0.02, "Bariera: najniższy punkt brył w Studio na ziemi (±0,011)")
        a = Aktor(A.wczytaj("wojownik"))
        lt = a.indeks["LowerTorso"]
        W0, _ = a.poza([("idle", 0.0, 1.0)])
        tyl = max(a.poza([("blok", f / 30.0, 1.0)])[0][lt, 2, 3] - W0[lt, 2, 3] for f in range(31))
        self.assertAlmostEqual(tyl, 0.41, delta=0.03, msg="blok: biodra w tył (klip 0,41, Play 0,37–0,40)")
        W, _ = a.poza([("unik", 14 / 30.0, 1.0)])
        self.assertAlmostEqual(-(W[lt, 0, 3] - W0[lt, 0, 3]), 1.70, delta=0.05, msg="unik: odskok 1,70 w lewo")


class Miara(unittest.TestCase):
    def test_ksztalty_jak_w_studio(self):
        # punkty kontrolne z panel/luau/KSZTALTY.md (części 4×4×4): powierzchnia klina y = hy·z/hz, narożnika
        # y = min(hy·x/hx, −hy·z/hz), walec wzdłuż X o promieniu min(sy, sz)/2
        h = np.array([2.0, 2.0, 2.0])
        e = 1e-3
        for z, y in ((-1.5, -1.5), (0.0, 0.0), (1.5, 1.5)):
            self.assertLess(B.sdf(B.KLIN, h, np.array([0.0, y - e, z])), 0)
            self.assertGreater(B.sdf(B.KLIN, h, np.array([0.0, y + e, z])), 0)
        for (x, z), y in (((1.5, -1.5), 1.5), ((0.0, -1.5), 0.0), ((1.5, 0.0), 0.0), ((0.0, 1.5), -1.5)):
            self.assertLess(B.sdf(B.NAROZNIK, h, np.array([x, y - e, z])), 0)
            self.assertGreater(B.sdf(B.NAROZNIK, h, np.array([x, y + e, z])), 0)
        w = np.array([3.0, 1.0, 2.0])                                       # walec Size (6, 2, 4): promień 1
        self.assertAlmostEqual(float(B.sdf(B.WALEC, w, np.array([0.0, 1.5, 0.0]))), 0.5, places=9)
        self.assertAlmostEqual(float(B.sdf(B.BLOK, h, np.array([0.0, 0.0, 0.0]))), -2.0, places=9)
        # głębokość w sumie brył: punkt w środku stosu dwóch cienkich płyt = połowa grubości stosu, nie jednej płyty
        R = np.eye(3)
        bs = [(B.BLOK, np.array([1.0, 0.1, 1.0]), R, np.array([0, 0.1, 0])),
              (B.BLOK, np.array([1.0, 0.1, 1.0]), R, np.array([0, -0.1, 0]))]
        g = B.glebokosc_w_sumie(np.array([[0.0, 0.0, 0.0]]), np.array([R]), bs)
        self.assertAlmostEqual(float(g[0]), 0.2, places=6)

    def test_zepsuty_klip_oblewa(self):
        # nowy klip, w którym prawa ręka z mieczem wjeżdża w hełm: pomiar musi go znaleźć (klipy z danych są brane
        # wszystkie, także nowe)
        d = A.wczytaj("wojownik")
        a = Aktor(d)
        idle = next(k for k in d["klipy"] if k["n"] == "idle")
        W, Wb = a.poza([("idle", 0.0, 1.0)])
        nazwy = [c[2] for c in d["czesci"]]
        klinga = next(i for i, c in enumerate(d["czesci"]) if c[2] == "Klinga")
        glowa = nazwy.index("Head")
        # przesunięcie przedramienia (Transform w układzie stawu = obrót ramienia) tak, by środek klingi doszedł do
        # środka głowy w kl. 10
        delta = Wb[glowa, :3, 3] - Wb[klinga, :3, 3]
        t = W[a.indeks["RightUpperArm"], :3, :3].T @ delta
        j = idle["kosci"].index(a.indeks["RightLowerArm"])
        zly = {"n": "test_zly", "fps": 30, "petla": False, "dl": 10, "kosci": idle["kosci"], "klatki": []}
        for f in range(11):
            w = list(idle["klatki"][0])
            for i in range(3):
                w[j * 6 + i] += float(t[i]) * f / 10.0
            zly["klatki"].append(w)
        d = dict(d, klipy=d["klipy"] + [zly])
        pm = PM.Pomiar(d, PM.spec_aktora("wojownik", d))
        sc = [s for s in PM.scenariusze(pm.a, A.PO_KLUCZU["wojownik"], 0.25) if s["klip"] == "test_zly"]
        self.assertTrue(sc, "nowy klip nie trafił do scenariuszy")
        w = PM.zmierz(pm, sc)[0]
        self.assertGreater(-w["strefy"]["glowa"]["m"], 0.2, "miecz w hełmie nie został wykryty")
        self.assertGreater(w["strefy"]["glowa"]["zle"], 0)


class Klipy(unittest.TestCase):
    def test_znani_aktorzy_z_bronia_sa_mierzeni(self):
        z = aktorzy_z_bronia()
        for k in ("wojownik", "zwiadowca", "mag", "lesny_troll", "muchomornik"):
            if k in A.PO_KLUCZU:
                self.assertIn(k, z, "%s trzyma broń, a pomiar go pomija" % k)
        for k in PM.SPEC:
            if k in A.PO_KLUCZU:
                d = A.wczytaj(k)
                pm = PM.Pomiar(d, PM.spec_aktora(k, d))
                self.assertTrue(pm.bron, "%s: SPEC wskazuje broń, której nie ma w danych" % k)
                self.assertIn("glowa", [s.nazwa for s in pm.strefy], "%s: brak strefy głowy" % k)

    def test_bron_nie_wchodzi_w_glowe_ani_tulow(self):
        bledy, znane = [], []
        for k in aktorzy_z_bronia():
            pm, wyniki = zbadaj(k)
            for w in wyniki:
                for z in pm.strefy:
                    s = w["strefy"][z.nazwa]
                    g = -s["m"]
                    if g <= z.prog:
                        continue
                    sufit = ZNANE.get((k, w["rodzaj"]), {}).get(z.nazwa)
                    opis = "%s / %s: %s %.3f studa (t = %.3f s, %s → %s, %d próbek ponad próg %.2f)" % (
                        k, w["nazwa"], z.nazwa, g, s["t"] or 0, s["bron"], s["cialo"], s["zle"], z.prog)
                    if sufit is not None and g <= sufit:
                        znane.append(opis)
                    else:
                        bledy.append(opis)
        if znane:
            print("\n  znane przejścia odtwarzacza (WYNIKI.md, „Nie poprawione”):\n    " + "\n    ".join(znane))
        self.assertFalse(bledy, "broń w ciele:\n  " + "\n  ".join(bledy))

    def test_znane_wpisy_nadal_potrzebne(self):
        # wpis w ZNANE, którego przypadek zniknął, trzeba usunąć (inaczej zasłaniałby przyszły błąd)
        for (k, rodzaj), strefy in ZNANE.items():
            if k not in A.PO_KLUCZU:
                continue
            pm, wyniki = zbadaj(k)
            for nazwa in strefy:
                prog = next(z.prog for z in pm.strefy if z.nazwa == nazwa)
                g = max(-w["strefy"][nazwa]["m"] for w in wyniki if w["rodzaj"] == rodzaj)
                self.assertGreater(g, prog, "%s/%s/%s: już bez przenikania (%.3f) — usuń wpis z ZNANE"
                                   % (k, rodzaj, nazwa, g))


class Skret(unittest.TestCase):
    def test_bron_nie_obraca_sie_wokol_osi_w_jednej_klatce(self):
        # obrót broni wokół jej długiej osi na klatkę (droga gry: klatka → pół klatki → klatka) ≤ PM.PROG_SKRETU
        # (70°, uzasadnienie w pomiar.py); kostur Maga przed poprawką z 17.11.2026: 84–156° (kryształ „migał”)
        bledy = []
        for k in aktorzy_z_bronia():
            pm, _ = zbadaj(k)
            for (bron, klip), (s, f) in sorted(PM.skret_broni(pm).items()):
                if s > PM.PROG_SKRETU and (k, klip) not in PM.WYJATKI_SKRETU:
                    bledy.append("%s / %s / %s: %.0f° w kl. %d→%d" % (k, bron, klip, s, f, f + 1))
        self.assertFalse(bledy, "broń obraca się wokół własnej osi szybciej niż %.0f° na klatkę:\n  %s"
                         % (PM.PROG_SKRETU, "\n  ".join(bledy)))

    def test_model_przejsc_czytany_z_kodu_gry(self):
        # narzędzie liczy wskrzeszenie i finał tak, jak robi to dzisiejszy odtwarzacz (czyta jego kod) — gdyby wzorzec
        # przestał pasować, pomiar po cichu liczyłby coś innego niż gra
        self.assertEqual(PM.model_wskrzeszenia()[0], "wstecz", "Obsluga.wskrzeszenie nie gra już upadku wstecz")
        przed, czas = K.obrot_zwyciezcy()
        self.assertGreaterEqual(przed, czas, "obrót zwycięzcy ma się skończyć przed radością (OBROT_ZWYCIEZCY)")


class Kamera(unittest.TestCase):
    def test_final_obrot_do_kamery(self):
        # początek finału: kąt objazdu i obrót zwycięzcy w czasie (OBROT_ZWYCIEZCY z kodu gry), radość wchodzi ze
        # spoczynku przez 0,2 s; kąt startu 62° (zwykle) i 90–150° (duży leżący pokonany), kamera z prawej (gracz)
        # i z lewej (przeciwnik-lustro). Przed 17.11.2026 (obrót razem z radością): Wojownik oczy 100%, Zwiadowca 77%.
        for w in A.AKTORZY:
            if w["rola"] != "klasa":
                continue
            d = A.wczytaj(w["klucz"])
            pm = PM.Pomiar(d, PM.spec_aktora(w["klucz"], d))
            tw = K.Twarz(pm, rozdz=64)
            sp, rad = w["klipy"]["spoczynek"], w["klipy"]["radosc"]
            for kat_start in (62.0, 90.0, 120.0, 150.0):
                for tau, kat in K.przebieg_finalu(kat_start, do=0.6, krok=1.0 / 30):
                    u = min(1.0, tau / 0.2)
                    _, Wb = pm.a.poza([(sp, tau, 1.0 - u), (rad, tau, u)])
                    for znak in (1, -1):
                        r = tw.zmierz(Wb, K.kamera_objazdu(d["wymiary"]["wysokosc"], kat, znak))
                        self.assertLessEqual(tw.ocena(r), 1.0, "%s: finał τ = %.2f s, kąt %+.0f°: oczy %.0f%%, rysy %.0f%%"
                                             % (w["klucz"], tau, kat * znak, 100 * r["oczy"], 100 * r["rysy"]))

    def test_bron_nie_zaslania_twarzy_z_przodu(self):
        # kamera objazdu finału (kąt twarzy 0–35°, obie strony: gracz i przeciwnik-lustro), radość i postawa
        for w in A.AKTORZY:
            if w["rola"] != "klasa":
                continue
            d = A.wczytaj(w["klucz"])
            pm = PM.Pomiar(d, PM.spec_aktora(w["klucz"], d))
            tw = K.Twarz(pm, rozdz=64)
            for akcja in ("radosc", "spoczynek"):
                kl = w["klipy"][akcja]
                n = pm.a.klipy[kl]["dl"]
                for f in range(0, n + 1, 4):
                    _, Wb = pm.a.poza([(kl, f / 30.0, 1.0)])
                    for kat in range(-35, 36, 7):
                        r = tw.zmierz(Wb, K.kamera_objazdu(d["wymiary"]["wysokosc"], kat))
                        self.assertLessEqual(tw.ocena(r), 1.0, "%s/%s kl. %d, kąt %d°: oczy %.0f%%, rysy %.0f%% pod bronią"
                                             % (w["klucz"], kl, f, kat, 100 * r["oczy"], 100 * r["rysy"]))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    unittest.main()
