#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy pakietu „bohater w świecie” BEZ Studio (unittest).

    python -B swiat/bohater_swiat/testy/test_bohatera.py         # wszystkie testy
    python -B swiat/bohater_swiat/testy/test_bohatera.py -v

1. Dane: DaneBohatera.luau aktualny i powtarzalny; klasy = klasy gry (src/shared/ClassData.luau) i ta sama mapa co
   w przymierzalni; klipy z tabeli aktorów walki są w danych walki; prędkość naturalna chodu policzona niezależnie;
   stopy na ziemi w spoczynku i w chodzie (po podniesieniu rigu); pozy proceduralne sprawdzone kinematyką w przód
   (ręce w górze, przysiad ze stopami na ziemi, podkurczone nogi w skoku); liczby brył i spód nóg w KAŻDYM
   dopuszczalnym stroju.
2. Logika (lustro w Pythonie): chód / spoczynek z histerezą, skok → spadanie → lądowanie, schodek to nie skok,
   śmierć, klipy wymuszone umową, cudza postać, wagi póz, tempo, przesunięcie, zasięg i wybór najbliższych, umowa.
3. Ten sam plik LogikaBohatera.luau w interpreterze luau_mini = lustro na tysiącach losowych kroków; zepsuta logika
   wykryta.
4. Kod: kontrola Luau pakietu; zbuduj.py --sucho; kod wysyłany do Studio parsuje się; proba_play.py --sprawdz;
   umowa RuchBohatera w kliencie i w budowie; moduły, z których korzystamy (Klipy, Ubieranie), mają używane wejścia;
   każda lokalna funkcja i zmienna z poziomu pliku zdefiniowana przed pierwszym użyciem; bez danych prywatnych.
"""
import itertools
import json
import math
import os
import random
import re
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
if not sys.path or sys.path[0] != PAKIET:
    sys.path.insert(0, PAKIET)
import dane as DN  # noqa: E402
import logika_bohatera as L  # noqa: E402
import sprawdz_luau_bohatera as SLB  # noqa: E402
import zbuduj as ZB  # noqa: E402

LM = SLB.luau_mini()
ZR = os.path.join(PAKIET, "zrodla")
D = DN.zbierz()
R = D["ruch"]
W = D["widocznosc"]
DT = 1.0 / 60.0
KLASY = {"Warrior": "wojownik", "Scout": "zwiadowca", "Mage": "mag"}
KLIPY_UMOWY = ["bieg", "skok", "padnij", "rece_gora", "radosc"]


def czytaj(plik):
    with open(os.path.join(ZR, plik), encoding="utf-8") as f:
        return f.read()


def czytaj_repo(*sciezka):
    with open(os.path.join(REPO, *sciezka), encoding="utf-8") as f:
        return f.read()


def rig_klasy(klucz):
    import aktorzy as A
    from geometria import Rig
    d = A.wczytaj(klucz)
    return d, Rig(d)


def we(**k):
    w = {"zyje": True, "stan": "Running", "naZiemi": True, "vpoz": 0.0, "vpion": 0.0, "zdalny": False, "wymuszony": None}
    w.update(k)
    return w


# ============================================================================================== 1. dane
class TestDane(unittest.TestCase):
    def test_1a_plik_aktualny_i_powtarzalny(self):
        ok, _ = DN.aktualny()
        self.assertTrue(ok, "zrodla/DaneBohatera.luau nieaktualny — python -B swiat/bohater_swiat/dane.py")
        with tempfile.TemporaryDirectory() as tmp:
            DN.zapisz(tmp)
            with open(os.path.join(tmp, DN.PLIK_LUAU), encoding="utf-8") as f:
                self.assertEqual(f.read(), czytaj(DN.PLIK_LUAU))
        self.assertLess(len(czytaj(DN.PLIK_LUAU)), 199000)
        self.assertIn(D["skrot"], czytaj(DN.PLIK_LUAU))

    def test_1b_klasy_gry_i_klipy(self):
        import aktorzy as A
        self.assertEqual(D["klasy_gracza"], KLASY)
        self.assertEqual(D["kolejnoscKlas"], list(KLASY.values()))
        self.assertEqual(D["atrybut_klasy"], "Class")
        # te same id co ekran wyboru klasy (tylko odczyt cudzego pliku) i ta sama mapa co przymierzalnia
        ids = re.findall(r'\{\s*id\s*=\s*"(\w+)"', czytaj_repo("src", "shared", "ClassData.luau"))
        self.assertEqual(sorted(ids), sorted(KLASY))
        self.assertIn('KLASY_GRACZA = { Warrior = "wojownik", Scout = "zwiadowca", Mage = "mag" }',
                      czytaj_repo("swiat", "stroje_proba", "zrodla", "KlientStrojow.client.luau"))
        self.assertIn('player:SetAttribute("Class", id)', czytaj_repo("src", "server", "ClassSelect.server.luau"))
        for gra, klucz in KLASY.items():
            K = D["klasy"][klucz]
            wpis = A.PO_KLUCZU[klucz]
            d, rig = rig_klasy(klucz)
            self.assertEqual(K["klasaGry"], gra)
            self.assertEqual(K["klipy"], {"spoczynek": wpis["klipy"]["spoczynek"], "ruch": wpis["klipy"]["ruch"],
                                          "radosc": wpis["klipy"]["radosc"], "upadek": wpis["klipy"]["upadek"]})
            self.assertEqual(K["klipy"]["radosc"], "wiwat")      # umowa: „radosc” = klip wiwat bohatera
            for akcja, nazwa in K["klipy"].items():
                self.assertIn(nazwa, rig.klipy, (klucz, akcja))
                self.assertAlmostEqual(K["dlugosci"][akcja], rig.klipy[nazwa]["dl"] / rig.klipy[nazwa]["fps"], places=3)
            self.assertTrue(rig.klipy[K["klipy"]["spoczynek"]]["petla"])
            self.assertTrue(rig.klipy[K["klipy"]["ruch"]]["petla"])
            self.assertFalse(rig.klipy[K["klipy"]["upadek"]]["petla"])
            self.assertEqual(K["hrp"], [round(v, 4) + 0.0 for v in d["hrp"]])

    def test_1c_dane_przymierzalni(self):
        DS = DN.dane_strojow()
        Ds, _ = DS.zbierz()
        self.assertEqual(D["atrybut_stroju"], Ds["atrybut"])
        self.assertEqual(D["atrybut_stroju"], "StrojProba_")
        self.assertEqual(D["kontener_strojow"], Ds["kontener"])
        for klucz, K in D["klasy"].items():
            d, _ = rig_klasy(klucz)
            self.assertEqual(K["hrp"], Ds["klasy"][klucz]["hrp"], klucz)
            self.assertEqual([k[0] for k in d["kosci"]], [k[0] for k in Ds["klasy"][klucz]["kosci"]], klucz)
            for n in D["kosciNog"]:
                self.assertIn(n, [k[0] for k in d["kosci"]])

    def test_1d_predkosc_chodu(self):
        oczekiwane = {"wojownik": 3.06, "zwiadowca": 7.11, "mag": 1.16}
        for klucz, K in D["klasy"].items():
            d, rig = rig_klasy(klucz)
            kl = rig.klipy[K["klipy"]["ruch"]]
            # niezależnie: średnia z obu stóp zakresu z środka stopy, ·2 / okres
            zakres = []
            for stopa in ("LeftFoot", "RightFoot"):
                zs = [rig.pozy(rig.transformy(kl["n"], f))[rig.indeks[stopa]][1][2] for f in range(kl["dl"] + 1)]
                zakres.append(max(zs) - min(zs))
            v = 2 * (sum(zakres) / 2) / (kl["dl"] / kl["fps"])
            self.assertAlmostEqual(K["predkoscChodu"], v, places=2, msg=klucz)
            self.assertAlmostEqual(K["predkoscChodu"], oczekiwane[klucz], delta=0.05, msg=klucz)
            t = L.tempo(R["bieg_predkosc"], K["predkoscChodu"], R)
            self.assertTrue(R["tempo_min"] <= t <= R["tempo_max"])

    def test_1e_stopy_na_ziemi_w_klipach(self):
        for klucz, K in D["klasy"].items():
            d, rig = rig_klasy(klucz)
            kl = rig.klipy[K["klipy"]["spoczynek"]]
            dno = [DN.najnizej(rig, d, rig.transformy(kl["n"], f), D["kosciNog"]) for f in range(kl["dl"] + 1)]
            self.assertAlmostEqual(min(dno), 0.0, delta=0.01, msg="%s spoczynek" % klucz)
            self.assertAlmostEqual(max(dno), 0.0, delta=0.01, msg="%s spoczynek" % klucz)
            kl = rig.klipy[K["klipy"]["ruch"]]
            dno = [DN.najnizej(rig, d, rig.transformy(kl["n"], f), D["kosciNog"]) for f in range(kl["dl"] + 1)]
            # po podniesieniu rigu najniższy punkt nóg w chodzie dotyka ziemi (nie wchodzi w nią i nie wisi)
            self.assertAlmostEqual(min(dno) + K["podniesienieChodu"], 0.0, delta=0.002, msg="%s chód" % klucz)
            self.assertGreaterEqual(K["podniesienieChodu"], 0.0)
            self.assertLess(K["podniesienieChodu"], 0.3)
            self.assertAlmostEqual(L.wysokosc_rigu(0.0, K["podniesienieChodu"], 1.0), K["podniesienieChodu"])

    def test_1f_pozy_proceduralne(self):
        from geometria import obwiednia
        self.assertEqual(D["kolejnoscPoz"], ["skok", "spadanie", "ladowanie", "padnij", "rece_gora", "pochyl"])
        for klucz, K in D["klasy"].items():
            d, rig = rig_klasy(klucz)
            p0 = rig.pozy()
            i = rig.indeks
            biodro = K["hrp"][1]
            dno0 = DN.najnizej(rig, d, {}, D["kosciNog"])
            self.assertAlmostEqual(dno0, 0.0, delta=0.005)
            for nazwa, wiersze in K["pozy"].items():
                self.assertEqual(len({w[0] for w in wiersze}), len(wiersze), "%s/%s: kość dwa razy" % (klucz, nazwa))
                for w in wiersze:
                    self.assertIn(w[0], i, (klucz, nazwa))
                    self.assertEqual(len(w), 7)
            poza = {n: rig.pozy(DN.transformy_pozy(rig, w)) for n, w in K["pozy"].items()}
            dno = {n: DN.najnizej(rig, d, DN.transformy_pozy(rig, w), D["kosciNog"]) for n, w in K["pozy"].items()}
            # ręce w górze: obie dłonie wyraźnie nad barkami (o więcej niż pół długości ręki), symetrycznie
            bark = d["kosci"][i["LeftUpperArm"] - 1][3]
            reka = bark - p0[i["LeftHand"]][1][1]
            for dlon in ("LeftHand", "RightHand"):
                self.assertGreater(poza["rece_gora"][i[dlon]][1][1], bark + 0.5 * reka, (klucz, dlon))
            self.assertAlmostEqual(poza["rece_gora"][i["LeftHand"]][1][1], poza["rece_gora"][i["RightHand"]][1][1], places=3)
            self.assertAlmostEqual(poza["rece_gora"][i["LeftHand"]][1][0], -poza["rece_gora"][i["RightHand"]][1][0], places=3)
            # padnij: stopy na ziemi, głowa niżej o co najmniej 0,6 wysokości bioder, biodra opuszczone
            self.assertAlmostEqual(dno["padnij"], 0.0, delta=0.002, msg=klucz)
            self.assertLess(poza["padnij"][i["Head"]][1][1], p0[i["Head"]][1][1] - 0.6 * biodro, klucz)
            self.assertGreater(K["przysiady"]["padnij"], 0.4 * biodro, klucz)
            self.assertLess(K["przysiady"]["padnij"], biodro, klucz)
            # lądowanie: lekki przysiad, stopy na ziemi
            self.assertAlmostEqual(dno["ladowanie"], 0.0, delta=0.002, msg=klucz)
            self.assertGreater(K["przysiady"]["ladowanie"], 0.0)
            self.assertLess(K["przysiady"]["ladowanie"], K["przysiady"]["padnij"])
            # skok: lewa stopa podkurczona (wyżej niż w spoczynku), ręce odwiedzione; spadanie: ręce wyżej niż barki
            self.assertGreater(poza["skok"][i["LeftFoot"]][1][1], p0[i["LeftFoot"]][1][1] + 0.1 * biodro, klucz)
            self.assertGreater(poza["skok"][i["RightHand"]][1][0], p0[i["RightHand"]][1][0] + 0.2 * reka, klucz)
            self.assertGreater(poza["spadanie"][i["LeftHand"]][1][1], bark, klucz)
            # pochylenie: głowa do przodu (przód rigu = −Z), stopy bez zmian
            self.assertLess(poza["pochyl"][i["Head"]][1][2], p0[i["Head"]][1][2] - 0.1, klucz)
            self.assertAlmostEqual(dno["pochyl"], 0.0, delta=0.002)
            # pozy bez przysiadu nie ruszają bioder; żadna poza nie wkłada postaci głęboko w ziemię
            for nazwa, wiersze in K["pozy"].items():
                if not K["przysiady"][nazwa]:
                    self.assertNotIn("LowerTorso", [w[0] for w in wiersze], (klucz, nazwa))
                mn, _ = obwiednia(rig, poza[nazwa])
                self.assertGreater(mn[1], -0.5, "%s/%s: bryły %.2f pod ziemią" % (klucz, nazwa, -mn[1]))

    def test_1g_bryly_i_spod_w_kazdym_stroju(self):
        import logika_strojow as LS
        from geometria import cf, narozniki, orientacja
        DS = DN.dane_strojow()
        Ds, _ = DS.zbierz()
        oczekiwane = {"wojownik": (74, 127), "zwiadowca": (109, 182), "mag": (107, 166)}
        limit = D["limity"]["maks_czesci_bohatera"]
        for klucz, K in D["klasy"].items():
            self.assertEqual((K["czesci"]["golas"], K["czesci"]["odniesienie"]), oczekiwane[klucz], klucz)
            nogi = {n + 1 for n, k in enumerate(Ds["klasy"][klucz]["kosci"]) if k[0] in D["kosciNog"]}
            ids = Ds["klasy"][klucz]["przedmioty"]
            stroje, najwiecej, spody = 0, 0, []
            for r in range(len(ids) + 1):
                for sub in itertools.combinations(ids, r):
                    ok, plan = LS.plan(Ds, klucz, list(sub))
                    if not ok or plan["przedmioty"] != list(sub):
                        continue
                    wiersze = DS.zloz(Ds, klucz, plan)
                    stroje += 1
                    najwiecej = max(najwiecej, len(wiersze))
                    spody.append(min(p[1] for w in wiersze if w[0] in nogi
                                     for p in narozniki(cf((w[3], w[4], w[5]), orientacja(w[6], w[7], w[8])), w[9:12])))
            self.assertGreater(stroje, 10, klucz)
            self.assertLessEqual(najwiecej, limit, "%s: %d brył w najcięższym stroju (limit %d)" % (klucz, najwiecej, limit))
            # w każdym stroju spód nóg leży na ziemi (klient i tak mierzy spód zbudowanego modelu)
            self.assertGreater(min(spody), -0.05, klucz)
            self.assertLess(max(spody), 0.05, klucz)

    def test_1i_dane_biegu(self):
        for klucz, K in D["klasy"].items():
            d, rig = rig_klasy(klucz)
            B, U = K["bieg"], DN.bieg_klasy(DN.ustawienia(), klucz)
            kosci = {k[0]: k for k in d["kosci"]}
            self.assertAlmostEqual(B["udo"], kosci["LeftUpperLeg"][3] - kosci["LeftLowerLeg"][3], places=4)
            self.assertAlmostEqual(B["lydka"], kosci["LeftLowerLeg"][3] - kosci["LeftFoot"][3], places=4)
            self.assertAlmostEqual(B["kostka"], kosci["LeftFoot"][3], places=4)
            self.assertAlmostEqual(B["biodro"], kosci["LeftUpperLeg"][3], places=4)
            self.assertAlmostEqual(B["noga"], B["udo"] + B["lydka"], places=4)
            # krok z długości nóg bohatera; bieg zaczyna się tam, gdzie klip chodu przestaje nadążać
            self.assertAlmostEqual(B["krok"], U["krok_na_noge"] * B["noga"], places=3)
            self.assertAlmostEqual(B["vDo"], R["tempo_max"] * K["predkoscChodu"], places=2)
            self.assertAlmostEqual(L.tempo(B["vDo"], K["predkoscChodu"], R), R["tempo_max"], places=3)
            self.assertGreater(B["vOd"], B["vDo"])
            self.assertLess(B["vOd"], R["bieg_predkosc"], "%s: przy zwykłej prędkości postaci ma już biec" % klucz)
            # w skrajach podporu noga sięga ziemi z zapasem; przy zwykłej prędkości kadencja z ustawień i wyraźny lot
            self.assertAlmostEqual(math.hypot(B["krok"] / 2, B["biodraPodpor"]), U["zasieg_nogi"] * B["noga"], places=3)
            f, pod = L.kadencja(B, R["bieg_predkosc"])
            self.assertAlmostEqual(f, U["kadencja_pelna"], places=2)
            self.assertLess(pod, 0.3, klucz)
            self.assertGreater(B["lot"], 0.06, klucz)
            for w in B["dodatki"]:
                self.assertIn(w[0], rig.indeks)
        kl = D["klasy"]
        # krótsze nogi = krótszy krok i szybsza kadencja; Zwiadowca lżej i szybciej niż Wojownik
        self.assertLess(kl["mag"]["bieg"]["krok"], kl["wojownik"]["bieg"]["krok"])
        v = R["bieg_predkosc"]
        self.assertGreater(L.kadencja(kl["mag"]["bieg"], v)[0], L.kadencja(kl["zwiadowca"]["bieg"], v)[0])
        self.assertGreater(L.kadencja(kl["zwiadowca"]["bieg"], v)[0], L.kadencja(kl["wojownik"]["bieg"], v)[0])
        self.assertGreater(kl["zwiadowca"]["bieg"]["unoszenie"], kl["wojownik"]["bieg"]["unoszenie"])

    def symulacja(self, klucz, predkosci, dts=None):
        """Bieg klatka po klatce z kinematyką w przód: prędkość postaci z listy (jedna na klatkę), cykl jak w kliencie
        (prędkość rzeczywista z drogi, faza z L.krok_biegu). → największy dryf stopy w podporze i pomiary."""
        K = D["klasy"][klucz]
        d, rig = rig_klasy(klucz)
        B = K["bieg"]
        faza, d_poprz, x, v_rz = 0.0, None, 0.0, predkosci[0]
        start = {"Left": None, "Right": None}
        w = {"dryf": 0.0, "podpory": 0, "dno_podporu": [], "dno_wymachu": [], "skok_kata": 0.0, "biodra": [],
             "kolano": [], "kolano_podpor": [], "fazy": []}
        poprzednie = None
        for n, v in enumerate(predkosci):
            dt = dts[n] if dts else DT
            droga = v * dt
            x += droga
            v_rz = L.predkosc(v_rz, droga, dt, B["wygladzanie"], B["vMaks"])
            f, pod = L.kadencja(B, abs(v_rz))
            faza = L.krok_biegu(B, faza, d_poprz, f, pod, dt, droga, False)
            d_poprz = pod
            c = L.bieg(B, faza, pod, L.skala_biegu(B, abs(v_rz)))
            t = DN.transformy_biegu(rig, c)
            pozy = rig.pozy(t)
            w["biodra"].append(c["biodraY"])
            w["fazy"].append(faza)
            w["kolano"].append(-math.degrees(c["lydkaL"]))
            for strona, przes in (("Left", 0.0), ("Right", 0.5)):
                fz = (faza + przes) % 1.0
                swiat = x - pozy[rig.indeks[strona + "Foot"]][1][2]       # przód = −Z
                dno = DN.najnizej(rig, d, t, [strona + "Foot"])
                if fz < pod:
                    if start[strona] is None:
                        start[strona] = swiat
                        w["podpory"] += 1
                    w["dryf"] = max(w["dryf"], abs(swiat - start[strona]))
                    w["dno_podporu"].append(dno)
                    if strona == "Left" and abs(fz / pod - 0.5) < 0.15:
                        w["kolano_podpor"].append(-math.degrees(c["lydkaL"]))
                else:
                    start[strona] = None
                    w["dno_wymachu"].append(dno)
            katy = [c[k] for k in ("udoL", "lydkaL", "stopaL", "udoP", "lydkaP", "stopaP")]
            if poprzednie is not None:
                w["skok_kata"] = max(w["skok_kata"], max(abs(a - b) for a, b in zip(katy, poprzednie)))
            poprzednie = katy
            # noga nigdy nie jest wyprostowana do granicy (odwrotna kinematyka nie przycina toru kostki)
            self.assertLess(c["lydkaL"], -math.radians(4), (klucz, v, faza))
        return w

    def test_1j_cykl_biegu_stopa_stoi_w_miejscu(self):
        """Kinematyka w przód na rigu klasy: przy prędkości v ciało jedzie do przodu, a stopa w podporze ma stać."""
        wyniki = {}
        for klucz, K in D["klasy"].items():
            B = K["bieg"]
            for v in (B["vOd"] + 0.05, 9.0, R["bieg_predkosc"], 20.0):
                f, pod = L.kadencja(B, v)
                self.assertAlmostEqual(B["krok"] * f / pod, v, places=6, msg=(klucz, v))   # umowa próby B19
                self.assertLess(pod, 0.5)
                w = self.symulacja(klucz, [v] * 200)
                self.assertGreater(w["podpory"], 4, (klucz, v))
                self.assertLess(w["dryf"], 0.005, "%s przy %.1f st/s: stopa w podporze przesunęła się o %.4f st" % (klucz, v, w["dryf"]))
                self.assertLess(max(abs(y) for y in w["dno_podporu"]), 0.01, (klucz, v))
                self.assertGreater(min(w["dno_wymachu"]), -0.02, (klucz, v))               # w wymachu stopa nad ziemią
                self.assertGreater(max(w["dno_wymachu"]), 0.08 * B["noga"] * L.skala_biegu(B, v), (klucz, v))   # uniesiona
                self.assertLess(w["skok_kata"], math.radians(75), (klucz, v))               # bez szarpnięć
                # biodra: ugięcie w podporze i wzlot w locie (wyraźna faza lotu)
                self.assertGreater(max(w["biodra"]) - min(w["biodra"]), (2.0 if v >= 16 else 1.02) * B["ugiecie"], (klucz, v))
                wyniki[(klucz, round(v, 1))] = (round(f, 2), round(pod, 3), round(w["dryf"], 5))
            # nogi symetryczne: prawa = lewa pół cyklu później
            a, b2 = L.bieg(B, 0.2, 0.25), L.bieg(B, 0.7, 0.25)
            for n in ("udo", "lydka", "stopa"):
                self.assertAlmostEqual(a[n + "L"], b2[n + "P"], places=9)
                self.assertAlmostEqual(a[n + "P"], b2[n + "L"], places=9)
            self.assertGreater(L.bieg(B, 0.0, 0.25)["udoL"], L.bieg(B, 0.0, 0.25)["udoP"])    # faza 0: lewa stopa z przodu
        self.assertEqual(len(wyniki), 12)

    def test_1k_przeszkoda_i_zmienna_predkosc(self):
        """Postać zwalnia na przeszkodzie, staje, rusza, klatki są nierówne — stopa w podporze dalej stoi w miejscu
        (faza idzie drogą postaci, zmiana udziału podporu nie rusza stopy)."""
        for klucz in D["klasy"]:
            # bez odbicia stopa stoi co do 0,005 st; z odbiciem (postać cofa się po uderzeniu o kilka setnych — faza idzie
            # wstecz) zostaje mały ślizg tylko wtedy, gdy stopa dopiero co stanęła (nie ma dokąd wrócić)
            for odbicie, prog in ((False, 0.005), (True, 0.06)):
                rnd = random.Random(5)
                v, lista, dts = 16.0, [], []
                for n in range(900):
                    m = n % 150
                    if m == 60:
                        v = rnd.choice([0.0, 0.3, 3.0, 7.0])          # przeszkoda: prędkość spada w jednej klatce
                    elif odbicie and m in (61, 63):
                        v = -2.0
                    elif odbicie and m in (62, 64):
                        v = 1.0
                    elif m == 110:
                        v = rnd.choice([12.0, 16.0, 22.0])
                    else:
                        v = max(0.0, v + rnd.uniform(-0.8, 0.8))
                    lista.append(v)
                    dts.append(rnd.choice([1 / 60.0, 1 / 60.0, 1 / 30.0, 1 / 144.0, 0.05]))
                w = self.symulacja(klucz, lista, dts)
                self.assertGreater(w["podpory"], 10, klucz)
                self.assertLess(w["dryf"], prog, "%s (odbicie %s): stopa w podporze przesunęła się o %.4f st" % (klucz, odbicie, w["dryf"]))
                self.assertGreater(min(w["dno_wymachu"]), -0.02, klucz)
        # prędkość rzeczywista: stojąca postać z wciśniętym klawiszem → zero, a z nim koniec biegu
        v_rz = 16.0
        for _ in range(60):
            v_rz = L.predkosc(v_rz, 0.0, DT, D["klasy"]["wojownik"]["bieg"]["wygladzanie"], 64)
        self.assertLess(v_rz, R["prog_ruchu_stop"])
        self.assertAlmostEqual(L.predkosc(3.0, 1e6, DT, 0.1, 64), 3.0 + (64 - 3.0) * DT / (DT + 0.1))    # teleport przycięty

    def test_1l_zakresy_stawow_i_dodatki(self):
        """Naturalniejszy zakres kolan (bieg mniej przykucnięty niż dawny cykl: 79° w połowie podporu), praca rąk."""
        v = R["bieg_predkosc"]
        kolana = {}
        for klucz, K in D["klasy"].items():
            B = K["bieg"]
            w = self.symulacja(klucz, [v] * 240)
            kolana[klucz] = (sum(w["kolano_podpor"]) / len(w["kolano_podpor"]), max(w["kolano"]), min(w["kolano"]))
            if klucz != "mag":                       # kot ma nogi pod szatą i długi krok — kolan nie widać
                self.assertLess(kolana[klucz][0], 62, klucz)
            self.assertGreater(kolana[klucz][1], 75, klucz)      # w wymachu pięta idzie wysoko
            self.assertLess(kolana[klucz][1], 150, klucz)
            self.assertLess(kolana[klucz][2], 30, klucz)         # przy postawieniu i odbiciu noga prawie prosta
            wym = {}
            for wp in B["dodatki"]:
                wym.setdefault(wp[0], []).append(wp)
            for kosc in ("LeftUpperArm", "RightUpperArm", "UpperTorso", "Head"):
                self.assertIn(kosc, wym, klucz)
            # faza 0 (lewa stopa z przodu): lewa ręka z tyłu, prawa z przodu; tułów pochylony, głowa go wyrównuje
            self.assertLess(L.dodatek(wym["LeftUpperArm"][0], 0.0, 1)[0], 0)
            self.assertGreater(L.dodatek(wym["RightUpperArm"][0], 0.0, 1)[0], 0)
            self.assertLess(wym["UpperTorso"][0][1], 0)
            self.assertGreater(wym["Head"][0][1], 0)
            self.assertLess(abs(wym["Head"][0][1] + wym["UpperTorso"][0][1]), math.radians(6))
        self.assertLess(kolana["zwiadowca"][0], kolana["wojownik"][0])       # Zwiadowca lżej: prostsza noga w podporze
        woj = {w[0]: w for w in D["klasy"]["wojownik"]["bieg"]["dodatki"]}
        # ręka z mieczem (prawa): mniejszy, ale widoczny wymach; ręka z tarczą (lewa) prawie nieruchoma
        self.assertTrue(math.radians(12) <= woj["RightUpperArm"][4] <= math.radians(20))
        self.assertLessEqual(abs(woj["LeftUpperArm"][4]), math.radians(8))
        mag = {}
        for w in D["klasy"]["mag"]["bieg"]["dodatki"]:
            mag.setdefault(w[0], w)
        for kosc in ("Tail", "TailTip", "HatPivot", "StaffPivot"):
            self.assertIn(kosc, mag)
        # kostur zostaje w biegu tak ustawiony jak w spoczynku (dodatek policzony przez generator znosi ruch ramienia)
        K = D["klasy"]["mag"]
        d, rig = rig_klasy("mag")
        i = rig.indeks["StaffPivot"]
        R0 = rig.pozy(rig.transformy(K["klipy"]["spoczynek"], 0))[i][0]
        for n in range(8):
            Rb = DN.poza_biegu(rig, d, K, n / 8.0, v)[1][i][0]
            for os_ in (1, 2):                                   # oś kostura (Y) i jego przód (Z)
                iloczyn = sum(R0[w][os_] * Rb[w][os_] for w in range(3))
                self.assertLess(math.degrees(math.acos(max(-1.0, min(1.0, iloczyn)))), 4.0, (n, os_))

    def test_1m_poly_i_przenikanie(self):
        """Pełna poza biegu na bryłach (klip spoczynku + cykl + dodatki + poły): nic nie schodzi pod ziemię, poły się
        ruszają, a broń, tarcza i kostur nie wchodzą w nogi ani tułów bardziej niż w spoczynku."""
        from geometria import narozniki, punkty_probne, w_pudle
        v = R["bieg_predkosc"]
        for klucz, K in D["klasy"].items():
            d, rig = rig_klasy(klucz)
            B = K["bieg"]
            pola = DN.poly_rigu(rig, d, B)
            if klucz == "mag":                      # szata dookoła: wszystko, co wisi, idzie razem
                self.assertGreater(len(pola), 5)
                self.assertTrue(all(p["dzwon"] for p in pola))
                self.assertGreater(max(p["waga"] for p in pola), 0.7)
            elif klucz == "wojownik":               # pasy tabardu z przodu i z tyłu
                self.assertGreater(len([p for p in pola if not p["dzwon"] and p["przod"]]), 3)
                self.assertGreater(len([p for p in pola if not p["dzwon"] and not p["przod"]]), 3)
            ids_pol = {id(p["c"]) for p in pola}
            cialo = {rig.indeks[n] for n in ("LowerTorso", "UpperTorso", "LeftUpperLeg", "LeftLowerLeg", "LeftFoot",
                                             "RightUpperLeg", "RightLowerLeg", "RightFoot")}
            bron = [n for n, c in enumerate(d["czesci"]) if c[14] != 0 and id(c) not in ids_pol]      # grupy broni, tarczy, kostura
            self.assertGreater(len(bron), 5, klucz)

            def wnikanie(cfs):
                ile = 0
                for n in bron:
                    for p in punkty_probne(cfs[n], d["czesci"][n][9:12]):
                        for m, c in enumerate(d["czesci"]):
                            if c[0] in cialo and c[14] == 0 and id(c) not in ids_pol and w_pudle(p, cfs[m], c[9:12], 0.03):
                                ile += 1
                                break
                return ile

            t0 = rig.transformy(K["klipy"]["spoczynek"], 0)
            pozy0 = rig.pozy(t0)
            spoczynek = wnikanie([rig.czesc_cf(c, pozy0) for c in d["czesci"]])
            najgorzej, ruch_pol, dno = 0, 0.0, 1e9
            for n in range(16):
                c, pozy, cfs = DN.poza_biegu(rig, d, K, n / 16.0, v)
                najgorzej = max(najgorzej, wnikanie(cfs))
                for m, cz in enumerate(d["czesci"]):
                    naroza = narozniki(cfs[m], cz[9:12])
                    # nasada ogona kota siedzi pod trenem szaty i schodzi z biodrami (dawny cykl: −0,066 st) — osobny próg
                    if d["kosci"][cz[0] - 1][0] == "Tail":
                        self.assertGreater(min(p[1] for p in naroza), -0.07, klucz)
                    else:
                        dno = min(dno, min(p[1] for p in naroza))
                    if id(cz) in ids_pol:
                        stale = narozniki(rig.czesc_cf(cz, pozy), cz[9:12])
                        ruch_pol = max(ruch_pol, max(math.dist(a, b) for a, b in zip(naroza, stale)))
            self.assertGreater(dno, -0.03, "%s: bryła pod ziemią w biegu (%.3f)" % (klucz, dno))
            if len(pola) > 3:
                self.assertGreater(ruch_pol, 0.12, "%s: poły stroju stoją w biegu" % klucz)
            print("  przenikanie %s: w spoczynku %d punktów, w biegu najwyżej %d (z %d brył broni)" % (klucz, spoczynek, najgorzej, len(bron)))
            self.assertLessEqual(najgorzej, spoczynek + 2, "%s: broń wchodzi w ciało w biegu (%d punktów, w spoczynku %d)"
                                 % (klucz, najgorzej, spoczynek))

    def test_1h_umowa_w_danych(self):
        self.assertEqual(D["kontrakt"]["klipy"], KLIPY_UMOWY)
        self.assertEqual(D["kontrakt"]["sygnal"], "RuchBohatera")
        self.assertEqual(D["kontener"], "BohaterSwiat")
        self.assertEqual(D["atrybut_wlacznika"], "BohaterWSwiecie")
        for n in ("skok", "padnij", "rece_gora"):
            for K in D["klasy"].values():
                self.assertIn(n, K["pozy"])
        self.assertEqual(D["kontrakt"]["wymuszenie_maks_s"], 0)     # „do zmiany” = bez limitu czasu (umowa)
        self.assertGreater(D["kontrakt"]["przesun_maks"], 5)


# ============================================================================================== 2. logika
class TestLogika(unittest.TestCase):
    def przebieg(self, kroki, pam=None):
        pam = pam or L.nowa_pamiec()
        wyniki = []
        for w, n in kroki:
            for _ in range(n):
                wyniki.append(L.krok(pam, w, R, DT))
        return wyniki, pam

    def test_2a_klasa_i_stroj(self):
        for gra, klucz in KLASY.items():
            self.assertEqual(L.klasa(D, gra), klucz)
        for zle in (None, "", "warrior", "Paladin", 5, True, "wojownik"):
            self.assertIsNone(L.klasa(D, zle))
        self.assertEqual(L.klucz_stroju(None), "~")
        self.assertEqual(L.klucz_stroju(""), "")           # pusty napis = goły bohater, nie „dawny”
        self.assertEqual(L.klucz_stroju("a,b"), "a,b")

    def test_2b_tempo_i_pochylenie(self):
        self.assertEqual(L.tempo(0, 3.0, R), R["tempo_min"])
        self.assertEqual(L.tempo(3.0, 3.0, R), 1.0)
        self.assertEqual(L.tempo(1000, 3.0, R), R["tempo_max"])
        self.assertEqual(L.tempo(5, 0, R), 1)
        poprzednie = 0
        for v in [x * 0.25 for x in range(0, 120)]:
            t = L.tempo(v, 3.0, R)
            self.assertGreaterEqual(t, poprzednie)
            poprzednie = t
        self.assertEqual(L.pochylenie(R["pochylenie_od"], R), 0)
        self.assertEqual(L.pochylenie(R["pochylenie_do"], R), 1)
        self.assertEqual(L.pochylenie(0, R), 0)
        self.assertEqual(L.pochylenie(99, R), 1)
        self.assertAlmostEqual(L.pochylenie((R["pochylenie_od"] + R["pochylenie_do"]) / 2, R), 0.5)

    def test_2c_chod_i_spoczynek_z_histereza(self):
        w, pam = self.przebieg([(we(), 5)])
        self.assertEqual(w[-1], {"tryb": "idle", "baza": "spoczynek", "petla": True, "v": 0.0})
        # między progami zostaje to, co było
        srodek = (R["prog_ruchu_start"] + R["prog_ruchu_stop"]) / 2
        w, pam = self.przebieg([(we(vpoz=srodek), 3)], pam)
        self.assertEqual(w[-1]["tryb"], "idle")
        w, pam = self.przebieg([(we(vpoz=16.0), 1)], pam)
        self.assertEqual(w[-1], {"tryb": "chod", "baza": "ruch", "petla": True, "v": 16.0})
        w, pam = self.przebieg([(we(vpoz=srodek), 3)], pam)
        self.assertEqual(w[-1]["tryb"], "chod")
        w, pam = self.przebieg([(we(vpoz=0.1), 1)], pam)
        self.assertEqual(w[-1]["tryb"], "idle")
        # wspinanie i pływanie liczą prędkość pionową; siedzenie = spoczynek
        w, _ = self.przebieg([(we(stan="Climbing", vpoz=0.0, vpion=8.0, naZiemi=False), 2)])
        self.assertEqual((w[-1]["tryb"], w[-1]["v"]), ("chod", 8.0))
        w, _ = self.przebieg([(we(stan="Swimming", vpoz=3.0, vpion=4.0, naZiemi=False), 2)])
        self.assertEqual((w[-1]["tryb"], w[-1]["v"]), ("chod", 5.0))
        w, _ = self.przebieg([(we(stan="Seated", vpoz=10.0, naZiemi=False), 2)])
        self.assertEqual((w[-1]["tryb"], w[-1]["v"]), ("idle", 0))

    def test_2d_skok_spadanie_ladowanie(self):
        w, pam = self.przebieg([(we(vpoz=16.0), 10)])
        # skok: stan Jumping od pierwszej klatki, bez czekania
        w, pam = self.przebieg([(we(stan="Jumping", naZiemi=False, vpoz=16.0, vpion=50.0), 1)], pam)
        self.assertEqual(w[-1], {"tryb": "skok", "baza": "spoczynek", "petla": True, "poza": "skok", "v": 0})
        w, pam = self.przebieg([(we(stan="Freefall", naZiemi=False, vpoz=16.0, vpion=20.0), 6)], pam)
        self.assertEqual({x["tryb"] for x in w}, {"skok"})
        w, pam = self.przebieg([(we(stan="Freefall", naZiemi=False, vpoz=16.0, vpion=-30.0), 6)], pam)
        self.assertEqual({x["tryb"] for x in w}, {"spadanie"})
        self.assertEqual(w[-1]["poza"], "spadanie")
        # odbicie przy lądowaniu (mała prędkość w górę, gdy postać już spadała) nie wraca do pozy skoku
        w, pam = self.przebieg([(we(stan="Freefall", naZiemi=False, vpoz=16.0, vpion=4.0), 2)], pam)
        self.assertEqual({x["tryb"] for x in w}, {"spadanie"})
        w, pam = self.przebieg([(we(stan="Freefall", naZiemi=False, vpoz=16.0, vpion=30.0), 1),
                                (we(stan="Freefall", naZiemi=False, vpoz=16.0, vpion=-30.0), 2)], pam)
        self.assertEqual([x["tryb"] for x in w], ["skok", "spadanie", "spadanie"])     # wyraźne wznoszenie — tak
        # ziemia: po min_czas_na_ziemi_s lądowanie przez czas_ladowania_s, potem chód (postać dalej biegnie)
        ile_ziemi = int(math.ceil(R["min_czas_na_ziemi_s"] / DT))
        ile_lad = int(math.ceil(R["czas_ladowania_s"] / DT))
        w, pam = self.przebieg([(we(stan="Landed", vpoz=16.0), ile_ziemi + ile_lad + 4)], pam)
        tryby = [x["tryb"] for x in w]
        self.assertEqual(tryby[0], "spadanie" if ile_ziemi > 1 else "ladowanie")
        self.assertIn("ladowanie", tryby)
        n_lad = tryby.count("ladowanie")
        self.assertTrue(ile_lad - 1 <= n_lad <= ile_lad + 1, (n_lad, ile_lad))
        self.assertEqual(tryby[-1], "chod")
        lad = [x for x in w if x["tryb"] == "ladowanie"][0]
        self.assertEqual((lad["baza"], lad["poza"]), ("ruch", "ladowanie"))
        self.assertFalse(pam["lot"])

    def test_2e_schodek_to_nie_skok(self):
        w, pam = self.przebieg([(we(vpoz=16.0), 10)])
        krotko = int(R["min_czas_w_powietrzu_s"] / DT) - 1
        self.assertGreater(krotko, 1)
        w, pam = self.przebieg([(we(stan="Freefall", naZiemi=False, vpoz=16.0, vpion=-5.0), krotko)], pam)
        self.assertEqual({x["tryb"] for x in w}, {"chod"})
        w, pam = self.przebieg([(we(vpoz=16.0), 5)], pam)
        self.assertEqual({x["tryb"] for x in w}, {"chod"})        # bez lądowania: lotu nie było
        # dłużej niż próg → spadanie
        w, pam = self.przebieg([(we(stan="Freefall", naZiemi=False, vpoz=16.0, vpion=-5.0), krotko + 4)], pam)
        self.assertEqual(w[-1]["tryb"], "spadanie")
        # w powietrzu bez stanu lotu (krawędź: podłoże Air przy stanie Running) też liczy się jako powietrze
        w, _ = self.przebieg([(we(naZiemi=False, vpion=-5.0), krotko + 4)])
        self.assertEqual(w[-1]["tryb"], "spadanie")

    def test_2f_smierc_i_wymuszenie(self):
        w, pam = self.przebieg([(we(vpoz=16.0), 5), (we(zyje=False, vpoz=16.0), 2)])
        self.assertEqual(w[-1], {"tryb": "upadek", "baza": "upadek", "petla": False, "v": 0})
        oczekiwane = {
            "bieg": {"tryb": "bieg", "baza": "ruch", "petla": True, "v": R["bieg_predkosc"]},
            "skok": {"tryb": "skok", "baza": "spoczynek", "petla": True, "poza": "skok", "v": 0},
            "padnij": {"tryb": "padnij", "baza": "spoczynek", "petla": True, "poza": "padnij", "v": 0},
            "rece_gora": {"tryb": "rece_gora", "baza": "spoczynek", "petla": True, "poza": "rece_gora", "v": 0},
            "radosc": {"tryb": "radosc", "baza": "radosc", "petla": False, "v": 0},
        }
        self.assertEqual(sorted(oczekiwane), sorted(KLIPY_UMOWY))
        for klip, wynik in oczekiwane.items():
            # wymuszenie wygrywa z ruchem postaci (bieg w miejscu, skok na ziemi), ale nie ze śmiercią
            for stan in (we(wymuszony=klip), we(wymuszony=klip, vpoz=16.0),
                         we(wymuszony=klip, stan="Freefall", naZiemi=False, vpion=-30.0)):
                w, pam = self.przebieg([(stan, 3)])
                self.assertEqual(w[-1], wynik, klip)
            w, pam = self.przebieg([(we(wymuszony=klip, zyje=False), 1)])
            self.assertEqual(w[-1]["tryb"], "upadek")
            if "poza" in wynik:
                self.assertIn(wynik["poza"], D["kolejnoscPoz"])
        # po zdjęciu wymuszenia od razu ruch samoczynny, bez lądowania
        w, pam = self.przebieg([(we(wymuszony="skok"), 20), (we(), 1)])
        self.assertEqual(w[-1]["tryb"], "idle")

    def test_2l_bieg(self):
        B = D["klasy"]["wojownik"]["bieg"]
        pam = L.nowa_pamiec()

        def kroki(w, n=3):
            wynik = None
            for _ in range(n):
                wynik = L.krok(pam, w, R, DT, B)
            return wynik
        srodek = (B["vOd"] + B["vDo"]) / 2
        self.assertEqual(kroki(we(vpoz=B["vDo"] - 0.5)), {"tryb": "chod", "baza": "ruch", "petla": True, "v": B["vDo"] - 0.5})
        self.assertEqual(kroki(we(vpoz=srodek))["tryb"], "chod")                 # w paśmie zostaje chód
        w = kroki(we(vpoz=16.0))
        self.assertEqual(w, {"tryb": "bieg", "baza": "spoczynek", "petla": True, "v": 16.0, "bieg": True})
        self.assertEqual(kroki(we(vpoz=srodek))["tryb"], "bieg")                 # i zostaje bieg (histereza)
        self.assertEqual(kroki(we(vpoz=B["vDo"] - 0.5))["tryb"], "chod")
        self.assertEqual(kroki(we(vpoz=0.0)), {"tryb": "idle", "baza": "spoczynek", "petla": True, "v": 0.0})
        # skok w biegu: w locie cyklu biegu nie ma; lądowanie w biegu wraca do biegu
        kroki(we(vpoz=16.0))
        w = kroki(we(stan="Jumping", naZiemi=False, vpoz=16.0, vpion=40.0), 1)
        self.assertEqual((w["tryb"], w.get("bieg")), ("skok", None))
        w = kroki(we(stan="Landed", vpoz=16.0), 6)
        self.assertEqual((w["tryb"], w["baza"], w.get("bieg")), ("ladowanie", "spoczynek", True))
        self.assertEqual(kroki(we(vpoz=16.0), 20)["tryb"], "bieg")
        # klip umowy „bieg”: bieg w miejscu cyklem proceduralnym (bez danych biegu — klip chodu, jak dawniej)
        self.assertEqual(L.krok(L.nowa_pamiec(), we(wymuszony="bieg"), R, DT, B),
                         {"tryb": "bieg", "baza": "spoczynek", "petla": True, "v": R["bieg_predkosc"], "bieg": True})
        self.assertEqual(L.krok(L.nowa_pamiec(), we(wymuszony="bieg"), R, DT),
                         {"tryb": "bieg", "baza": "ruch", "petla": True, "v": R["bieg_predkosc"]})
        # bez danych biegu szybki ruch to dalej chód
        self.assertEqual(L.krok(L.nowa_pamiec(), we(vpoz=16.0), R, DT)["tryb"], "chod")
        # kadencja rośnie z prędkością, podpór skraca się (dłuższy lot) i zawsze jest krótszy niż pół cyklu
        f1, d1 = L.kadencja(B, B["vOd"])
        f2, d2 = L.kadencja(B, 16.0)
        f3, d3 = L.kadencja(B, 40.0)
        self.assertLess(f1, f2)
        self.assertLess(f2, f3)
        self.assertLess(d2, d1)
        self.assertLess(d1, 0.5)
        self.assertLessEqual(d3, d2)
        self.assertGreaterEqual(d3, B["podporMin"])
        self.assertEqual(L.kadencja(B, 0.0), L.kadencja(B, B["vMin"]))
        self.assertLess(L.skala_biegu(B, B["vOd"]), L.skala_biegu(B, 16.0))           # trucht: mniejszy ruch
        # faza: w podporze idzie drogą postaci (pół kroku drogi = pół podporu), w locie zegarem, zawija się w 0…1
        self.assertAlmostEqual(L.krok_biegu(B, 0.0, d2, f2, d2, 0.5, B["krok"] / 2, False), d2 / 2)
        self.assertAlmostEqual(L.krok_biegu(B, 0.0, d2, f2, d2, 0.5, 0.0, False), 0.0)          # postać stoi: stopa też
        self.assertAlmostEqual(L.krok_biegu(B, 0.45, d2, f2, d2, 0.01, 0.0, False), 0.45 + f2 * 0.01)
        self.assertAlmostEqual(L.krok_biegu(B, 0.99, d2, 3.0, d2, 0.1, 0.0, True), 0.29)        # w miejscu — zegar
        # zmiana udziału podporu: stopa zostaje w tym samym ułamku podporu
        self.assertAlmostEqual(L.krok_biegu(B, 0.5 + d2 / 4, d2, f2, d2 / 2, 0.01, 0.0, False), 0.5 + d2 / 8)
        # przechył w zakręcie: w lewo dodatni, ograniczony, wygładzony
        S = B["skretCiala"]
        x = 0.0
        for _ in range(120):
            x = L.skret_ciala(x, 50.0, DT, S)
        self.assertAlmostEqual(x, 1.0, places=2)
        self.assertLess(L.skret_ciala(0.0, -3.0, DT, S), 0)

    def test_2g_cudza_postac(self):
        # podłoże cudzej postaci nie jest pewne: lot poznajemy po stanie albo po dużej prędkości pionowej
        w, pam = self.przebieg([(we(zdalny=True, naZiemi=False, vpoz=10.0), 30)])
        self.assertEqual({x["tryb"] for x in w}, {"chod"})
        w, pam = self.przebieg([(we(zdalny=True, vpion=40.0, vpoz=10.0), 12)], pam)
        self.assertEqual(w[-1]["tryb"], "skok")
        # wierzchołek skoku (mała prędkość pionowa przez chwilę krótszą niż min_czas_na_ziemi_s) nie przerywa lotu
        w, pam = self.przebieg([(we(zdalny=True, vpion=2.0, vpoz=10.0), 2)], pam)
        self.assertEqual({x["tryb"] for x in w}, {"skok"})
        w, pam = self.przebieg([(we(zdalny=True, vpion=-40.0, vpoz=10.0), 6)], pam)
        self.assertEqual(w[-1]["tryb"], "spadanie")
        w, pam = self.przebieg([(we(zdalny=True, vpion=0.0, vpoz=10.0), 40)], pam)
        self.assertEqual(w[-1]["tryb"], "chod")

    def test_2h_wagi_poz(self):
        kol, czasy = D["kolejnoscPoz"], D["czasyPoz"]
        wagi = {}
        n = 0
        while wagi.get("skok", 0) < 1 and n < 1000:
            L.krok_wag(wagi, {"skok": 1}, DT, czasy, kol)
            n += 1
        self.assertAlmostEqual(n * DT, czasy["skok"], delta=DT * 1.01)
        self.assertEqual(wagi, {"skok": 1})
        # przejście skok → spadanie: jedna gaśnie, druga rośnie, żadna nie wychodzi poza 0…1
        for _ in range(200):
            L.krok_wag(wagi, {"spadanie": 1}, DT, czasy, kol)
            for w in wagi.values():
                self.assertTrue(0 < w <= 1)
        self.assertEqual(wagi, {"spadanie": 1})
        for _ in range(200):
            L.krok_wag(wagi, {}, DT, czasy, kol)
        self.assertEqual(wagi, {})
        # cel ułamkowy (pochylenie w biegu) i czas 0 = od razu
        for _ in range(200):
            L.krok_wag(wagi, {"pochyl": 0.4}, DT, czasy, kol)
        self.assertAlmostEqual(wagi["pochyl"], 0.4)
        self.assertEqual(L.krok_wag({}, {"x": 1}, DT, {}, ["x"]), {"x": 1})

    def test_2i_stopy_i_przesuniecie(self):
        self.assertEqual(L.pod_stopami(2.0, 2.0, 0), 3.0)          # R15: HipHeight + pół HumanoidRootPart
        self.assertEqual(L.pod_stopami(0.0, 2.0, 2.0), 3.0)        # R6: nogi 2 studs
        self.assertAlmostEqual(L.wysokosc_rigu(0.05, 0.2, 0.0), -0.05)
        self.assertAlmostEqual(L.wysokosc_rigu(0.05, 0.2, 1.0), 0.15)
        self.assertEqual(L.przesun(1, 2, 3, 30), (1, 2, 3))
        x, y, z = L.przesun(0, 100, 0, 30)
        self.assertEqual((x, y, z), (0, 30, 0))
        x, y, z = L.przesun(300, 400, 0, 30)
        self.assertAlmostEqual(math.sqrt(x * x + y * y + z * z), 30)
        for zle in ((float("nan"), 0, 0), (0, float("inf"), 0), ("a", 0, 0), (None, 0, 0), (True, 0, 0)):
            self.assertEqual(L.przesun(*zle, 30), (0, 0, 0))

    def test_2j_zasieg_i_wybor(self):
        self.assertTrue(L.widoczny(W["promien"], False, W))
        self.assertFalse(L.widoczny(W["promien"] + 1, False, W))
        self.assertTrue(L.widoczny(W["promien"] + 1, True, W))       # histereza: już widoczny zostaje trochę dłużej
        self.assertFalse(L.widoczny(W["promien"] * W["histereza"] + 1, True, W))
        self.assertEqual(L.okres(0, W), 1)
        self.assertEqual(L.okres(W["promien_pelnej_animacji"], W), 1)
        self.assertEqual(L.okres(W["promien_pelnej_animacji"] + 1, W), W["okres_daleko"])
        kandydaci = [{"id": "a", "odl": 50, "lokalny": False}, {"id": "ja", "odl": 0, "lokalny": True},
                     {"id": "b", "odl": 10, "lokalny": False}, {"id": "c", "odl": 30, "lokalny": False}]
        self.assertEqual(L.wybierz(kandydaci, 3), {"ja": True, "b": True, "c": True})
        self.assertEqual(L.wybierz(kandydaci, 1), {"ja": True})
        self.assertEqual(L.wybierz(kandydaci, 10), {"ja": True, "a": True, "b": True, "c": True})
        self.assertEqual(L.wybierz([], 5), {})
        # lokalny zawsze, nawet przy limicie 0 (własnego bohatera nie zabiera limit)
        self.assertEqual(L.wybierz(kandydaci, 0), {"ja": True})

    def test_2k_umowa(self):
        wym = L.nowy_ruch()
        boh = {"klasa": "wojownik", "tryb": "idle"}
        # bez bohatera: stan nil, reszta false (nic nie zostaje zapamiętane)
        self.assertIsNone(L.polecenie_ruchu(D, wym, None, "stan"))
        self.assertIs(L.polecenie_ruchu(D, wym, None, "klip", "bieg"), False)
        self.assertIs(L.polecenie_ruchu(D, wym, None, "przesun", True, 0, 1, 0), False)
        self.assertEqual(wym, {"licznik": 0})
        # z bohaterem
        self.assertEqual(L.polecenie_ruchu(D, wym, boh, "stan"),
                         {"aktywny": True, "klasa": "wojownik", "klip": "idle", "wymuszony": None})
        for klip in KLIPY_UMOWY:
            self.assertIs(L.polecenie_ruchu(D, wym, boh, "klip", klip), True)
            self.assertEqual(wym["klip"], klip)
        for zle in ("taniec", "", "Bieg", 5, True, {}):
            self.assertIs(L.polecenie_ruchu(D, wym, boh, "klip", zle), False)
            self.assertEqual(wym["klip"], "radosc")               # zły klip nie zmienia poprzedniego
        licznik = wym["licznik"]
        self.assertIs(L.polecenie_ruchu(D, wym, boh, "klip", "radosc"), True)
        self.assertEqual(wym["licznik"], licznik + 1)              # każde wywołanie = wiwat od nowa
        self.assertIs(L.polecenie_ruchu(D, wym, boh, "klip", None), True)
        self.assertNotIn("klip", wym)
        self.assertIs(L.polecenie_ruchu(D, wym, boh, "przesun", True, 0, 2.5, -1), True)
        self.assertEqual((wym["px"], wym["py"], wym["pz"]), (0, 2.5, -1))
        self.assertIs(L.polecenie_ruchu(D, wym, boh, "przesun", True, 0, 1e9, 0), True)
        self.assertAlmostEqual(wym["py"], D["kontrakt"]["przesun_maks"])
        self.assertIs(L.polecenie_ruchu(D, wym, boh, "przesun", None), True)
        self.assertNotIn("px", wym)
        self.assertIsNone(L.polecenie_ruchu(D, wym, boh, "nieznane"))
        L.polecenie_ruchu(D, wym, boh, "klip", "padnij")
        L.polecenie_ruchu(D, wym, boh, "przesun", True, 1, 1, 1)
        L.zeruj_ruch(wym)
        self.assertEqual(set(wym), {"licznik"})


# ============================================================================================== 3. Luau = lustro
def _interpreter():
    it = LM.Interpreter()
    rs = LM.Tabela()
    rs.set("IsStudio", lambda _self: True)
    game = LM.Tabela()
    game.set("GetService", lambda _self, _n: rs)
    it.globalne.z["game"] = game
    # funkcje kątowe, których interpreter nie ma, a cykl biegu używa (w Roblox to zwykła biblioteka math)
    m = it.globalne.z["math"]
    m.set("sin", lambda x: math.sin(x))
    m.set("cos", lambda x: math.cos(x))
    m.set("acos", lambda x: math.acos(x))
    m.set("atan2", lambda y, x: math.atan2(y, x))
    m.set("pi", math.pi)
    return it


def _luau(tekst_logiki=None):
    it = _interpreter()
    Dl = it.wykonaj(czytaj(DN.PLIK_LUAU), DN.PLIK_LUAU)[0]
    Ll = it.wykonaj(tekst_logiki or czytaj("LogikaBohatera.luau"), "LogikaBohatera.luau")[0]
    return it, Dl, Ll


def _norm(v):
    """Wynik Luau/Pythona w jednej postaci: bez pól nil / None, puste tabele jako {}, liczby jako float."""
    if isinstance(v, dict):
        return {k: _norm(x) for k, x in v.items() if x is not None}
    if isinstance(v, (list, tuple)):
        return {} if len(v) == 0 else [_norm(x) for x in v]
    if isinstance(v, bool) or v is None or isinstance(v, str):
        return v
    return round(float(v), 9)


@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py — Luau nie wykonany")
class TestLuau(unittest.TestCase):
    STANY = ["Running", "Jumping", "Freefall", "Landed", "Climbing", "Swimming", "Seated", "GettingUp", "None",
             "PlatformStanding", "Dead", "RunningNoPhysics"]

    def wolaj(self, it, Ll, nazwa, *argi):
        return [LM.z_luau(x) for x in it.wywolaj(Ll.get(nazwa), list(argi))]

    def losowe_kroki(self, it, Dl, Ll, ile_ciagow, dlugosc, ziarno, cicho=False):
        rnd = random.Random(ziarno)
        Rl = Dl.get("ruch")
        zle = 0
        for _ in range(ile_ciagow):
            pam_py = L.nowa_pamiec()
            pam_lu = it.wywolaj(Ll.get("nowaPamiec"), [])[0]
            zdalny = rnd.random() < 0.3
            klasa_b = rnd.choice([None, "wojownik", "zwiadowca", "mag"])       # z cyklem biegu klasy albo bez
            b_py = D["klasy"][klasa_b]["bieg"] if klasa_b else None
            b_lu = Dl.get("klasy").get(klasa_b).get("bieg") if klasa_b else None
            stan, na_ziemi, wym = "Running", True, None
            for _ in range(dlugosc):
                if rnd.random() < 0.2:
                    stan = rnd.choice(self.STANY)
                if rnd.random() < 0.25:
                    na_ziemi = rnd.random() < 0.6
                if rnd.random() < 0.05:
                    wym = rnd.choice([None, None] + KLIPY_UMOWY)
                w = {"zyje": rnd.random() > 0.03, "stan": stan, "naZiemi": na_ziemi,
                     "vpoz": rnd.choice([0.0, 0.2, 0.5, 0.9, 4.0, 16.0, rnd.uniform(0, 20)]),
                     "vpion": rnd.choice([0.0, 0.5, 1.5, -3.0, 9.0, -9.0, 50.0, rnd.uniform(-60, 60)]),
                     "zdalny": zdalny, "wymuszony": wym}
                dt = rnd.choice([1 / 60.0, 1 / 30.0, 0.1, 0.004])
                py = L.krok(pam_py, w, R, dt, b_py)
                lu = it.wywolaj(Ll.get("krok"), [pam_lu, LM.do_luau(w), Rl, dt, b_lu])[0]
                if _norm(py) != _norm(LM.z_luau(lu)) or _norm(pam_py) != _norm(LM.z_luau(pam_lu)):
                    zle += 1
                    if zle <= 3 and not cicho:
                        print("ROZJAZD krok", w, py, LM.z_luau(lu), pam_py, LM.z_luau(pam_lu))
        return zle

    def losowe_inne(self, it, Dl, Ll, n, ziarno, cicho=False):
        rnd = random.Random(ziarno)
        Rl, Wl = Dl.get("ruch"), Dl.get("widocznosc")
        kol = D["kolejnoscPoz"]
        zle = 0
        wagi_py, wagi_lu = {}, LM.Tabela()
        wym_py, wym_lu = L.nowy_ruch(), it.wywolaj(Ll.get("nowyRuch"), [])[0]
        for _ in range(n):
            co = rnd.choice(["klasa", "stroj", "tempo", "pochyl", "wagi", "stopy", "rig", "przesun", "widoczny", "okres",
                             "wybierz", "ruch", "zeruj", "kadencja", "faza", "bieg", "bieg", "dodatek", "poly", "predkosc"])
            klasa_b = rnd.choice(list(D["klasy"]))
            b_py, b_lu = D["klasy"][klasa_b]["bieg"], Dl.get("klasy").get(klasa_b).get("bieg")
            if co == "kadencja":
                v = rnd.choice([0.0, 2.0, 16.0, rnd.uniform(0, 45)])
                py, lu = list(L.kadencja(b_py, v)), self.wolaj(it, Ll, "kadencja", b_lu, v)
                py.append(L.skala_biegu(b_py, v))
                lu += self.wolaj(it, Ll, "skalaBiegu", b_lu, v)
            elif co == "faza":
                v = rnd.choice([0.5, 6.0, 16.0, rnd.uniform(0, 30)])
                f, pod = L.kadencja(b_py, v)
                a = [rnd.random(), rnd.choice([None, pod, rnd.uniform(0.06, 0.49)]), f, pod, rnd.choice([1 / 60.0, 0.1]),
                     rnd.choice([0.0, v / 60.0, -0.05, rnd.uniform(-1, 3)]), rnd.random() < 0.2]
                py, lu = [L.krok_biegu(b_py, *a)], self.wolaj(it, Ll, "krokBiegu", b_lu, *a)
            elif co == "bieg":
                a = [rnd.choice([0.0, 0.25, 0.5, 0.999, rnd.random()]), rnd.uniform(b_py["podporMin"], 0.49)]
                if rnd.random() < 0.7:
                    a.append(rnd.uniform(0.4, 1.2))
                py, lu = [L.bieg(b_py, *a)], self.wolaj(it, Ll, "bieg", b_lu, *a)
            elif co == "dodatek":
                n = rnd.randrange(len(b_py["dodatki"]))
                a = [rnd.random(), rnd.uniform(0.4, 1.2)]
                py = list(L.dodatek(b_py["dodatki"][n], *a))
                lu = self.wolaj(it, Ll, "dodatek", b_lu.get("dodatki").get(n + 1), *a)
            elif co == "poly":
                a = [rnd.uniform(-0.2, 2.5), rnd.uniform(-1.5, 0.5), rnd.uniform(-0.5, 1.5)]
                w = rnd.random()
                py = [L.rodzaj_poly(b_py, *a), L.waga_dzwonu(b_py, a[0], a[1])] + list(L.dzwon(b_py, a[2], 1.0, w))
                lu = (self.wolaj(it, Ll, "rodzajPoly", b_lu, *a) or [None]) + self.wolaj(it, Ll, "wagaDzwonu", b_lu, a[0], a[1]) \
                    + self.wolaj(it, Ll, "dzwon", b_lu, a[2], 1.0, w)
            elif co == "predkosc":
                a = [rnd.uniform(0, 20), rnd.choice([0.0, 0.27, 5.0]), rnd.choice([0.0, 1 / 60.0, 0.1]), 0.1, 64.0]
                om = rnd.uniform(-9, 9)
                py = [L.predkosc(*a), L.skret_ciala(a[0] / 20 - 0.5, om, a[2], b_py["skretCiala"])]
                lu = self.wolaj(it, Ll, "predkosc", *a) + self.wolaj(it, Ll, "skretCiala", a[0] / 20 - 0.5, om, a[2],
                                                                    b_lu.get("skretCiala"))
            elif co == "klasa":
                a = rnd.choice(list(KLASY) + ["x", "", None, 3.0, True, "wojownik"])
                py, lu = [L.klasa(D, a)], self.wolaj(it, Ll, "klasa", Dl, a)
            elif co == "stroj":
                a = rnd.choice([None, "", "a,b", 5.0, False])
                py, lu = [L.klucz_stroju(a)], self.wolaj(it, Ll, "kluczStroju", a)
            elif co == "tempo":
                v, nat = rnd.uniform(0, 40), rnd.choice([0.0, -1.0, 1.16, 3.06, 7.11, rnd.uniform(0.1, 9)])
                py, lu = [L.tempo(v, nat, R)], self.wolaj(it, Ll, "tempo", v, nat, Rl)
            elif co == "pochyl":
                v = rnd.uniform(-5, 40)
                py, lu = [L.pochylenie(v, R)], self.wolaj(it, Ll, "pochylenie", v, Rl)
            elif co == "wagi":
                cele = {}
                if rnd.random() < 0.8:
                    cele[rnd.choice(kol)] = rnd.choice([1.0, 1.0, 0.3, 0.0, rnd.random()])
                dt = rnd.choice([1 / 60.0, 1 / 30.0, 0.5])
                L.krok_wag(wagi_py, cele, dt, D["czasyPoz"], kol)
                it.wywolaj(Ll.get("krokWag"), [wagi_lu, LM.do_luau(cele), dt, Dl.get("czasyPoz"), Dl.get("kolejnoscPoz")])
                py, lu = [dict(wagi_py)], [LM.z_luau(wagi_lu)]
            elif co == "stopy":
                a = [rnd.uniform(0, 3), rnd.uniform(1, 3), rnd.choice([0.0, 2.0])]
                py, lu = [L.pod_stopami(*a)], self.wolaj(it, Ll, "podStopami", *a)
            elif co == "rig":
                a = [rnd.uniform(-0.1, 0.1), rnd.uniform(0, 0.3), rnd.random()]
                py, lu = [L.wysokosc_rigu(*a)], self.wolaj(it, Ll, "wysokoscRigu", *a)
            elif co == "przesun":
                a = [rnd.choice([0.0, 1.5, -40.0, 1e6, float("nan"), float("inf"), "x", None, rnd.uniform(-50, 50)])
                     for _ in range(3)]
                py, lu = list(L.przesun(a[0], a[1], a[2], 30.0)), self.wolaj(it, Ll, "przesun", a[0], a[1], a[2], 30.0)
            elif co == "widoczny":
                odl, byl = rnd.uniform(0, 400), rnd.random() < 0.5
                py, lu = [L.widoczny(odl, byl, W)], self.wolaj(it, Ll, "widoczny", odl, byl, Wl)
            elif co == "okres":
                odl = rnd.uniform(0, 400)
                py, lu = [L.okres(odl, W)], self.wolaj(it, Ll, "okres", odl, Wl)
            elif co == "wybierz":
                k = [{"id": "g%d" % i, "odl": rnd.choice([0.0, 10.0, 10.0, rnd.uniform(0, 300)]), "lokalny": i == 0 and rnd.random() < 0.8}
                     for i in range(rnd.randint(0, 9))]
                rnd.shuffle(k)
                maks = float(rnd.randint(0, 8))
                py, lu = [L.wybierz(k, maks)], self.wolaj(it, Ll, "wybierz", LM.do_luau(k), maks)
            elif co == "ruch":
                boh = rnd.choice([None, {"klasa": "mag", "tryb": "chod"}])
                pol = rnd.choice(["stan", "klip", "klip", "przesun", "przesun", "inne"])
                a = None
                xyz = [None, None, None]
                if pol == "klip":
                    a = rnd.choice(KLIPY_UMOWY + [None, "taniec", 4.0, True])
                elif pol == "przesun":
                    a = rnd.choice([True, True, None, False, "x"])
                    xyz = [rnd.choice([0.0, 2.0, -100.0, float("nan"), rnd.uniform(-9, 9)]) for _ in range(3)]
                py = [L.polecenie_ruchu(D, wym_py, boh, pol, a, *xyz)]
                lu = self.wolaj(it, Ll, "polecenieRuchu", Dl, wym_lu, LM.do_luau(boh) if boh else None, pol, a, *xyz)
                lu = lu or [None]
                py.append(dict(wym_py))
                lu.append(LM.z_luau(wym_lu))
            else:
                L.zeruj_ruch(wym_py)
                it.wywolaj(Ll.get("zerujRuch"), [wym_lu])
                py, lu = [dict(wym_py)], [LM.z_luau(wym_lu)]
            if _norm(py) != _norm(lu or [None]):
                zle += 1
                if zle <= 3 and not cicho:
                    print("ROZJAZD", co, py, lu)
        return zle

    def test_3a_luau_rowna_lustru(self):
        it, Dl, Ll = _luau()
        self.assertEqual(self.losowe_kroki(it, Dl, Ll, 60, 150, 11), 0)
        self.assertEqual(self.losowe_inne(it, Dl, Ll, 4000, 12), 0)

    def test_3b_umowa_w_luau(self):
        """Dokładnie to, co dostanie pakiet mini-gier (wynik z Luau, nie z lustra)."""
        it, Dl, Ll = _luau()
        wym = it.wywolaj(Ll.get("nowyRuch"), [])[0]
        boh = LM.do_luau({"klasa": "zwiadowca", "tryb": "idle"})

        def wolaj(*argi):
            w = it.wywolaj(Ll.get("polecenieRuchu"), [Dl, wym] + list(argi))
            return LM.z_luau(w[0]) if w else None

        self.assertIsNone(wolaj(None, "stan"))
        self.assertIs(wolaj(None, "klip", "bieg"), False)
        self.assertEqual(wolaj(boh, "stan"), {"aktywny": True, "klasa": "zwiadowca", "klip": "idle"})
        for klip in KLIPY_UMOWY:
            self.assertIs(wolaj(boh, "klip", klip), True)
            self.assertEqual(wolaj(boh, "stan")["wymuszony"], klip)
        self.assertIs(wolaj(boh, "klip", "salto"), False)
        self.assertIs(wolaj(boh, "klip", None), True)
        self.assertNotIn("wymuszony", wolaj(boh, "stan"))
        self.assertIs(wolaj(boh, "przesun", True, 0.0, 3.0, 0.0), True)
        self.assertEqual(LM.z_luau(wym)["py"], 3)
        self.assertIs(wolaj(boh, "przesun", None), True)
        self.assertNotIn("py", LM.z_luau(wym))
        # automat w Luau: każdy klip umowy daje tryb o tej samej nazwie
        pam = it.wywolaj(Ll.get("nowaPamiec"), [])[0]
        for klip in KLIPY_UMOWY:
            wy = LM.z_luau(it.wywolaj(Ll.get("krok"), [pam, LM.do_luau(we(wymuszony=klip)), Dl.get("ruch"), DT])[0])
            self.assertEqual(wy["tryb"], klip)

    def test_3c_zepsuta_logika_wykryta(self):
        zepsute = [
            ("if pam.lot and not powietrze and pam.naZiemi >= R.min_czas_na_ziemi_s then", "if false then"),  # bez lądowania
            ("elseif v > R.prog_ruchu_start then", "elseif v > 0 then"),                                 # bez histerezy
            ('local tryb = if we.vpion > prog then "skok" else "spadanie"', 'local tryb = "skok"'),
            ("local prog = if pam.spada then R.prog_ponownego_wznoszenia else R.prog_wznoszenia",
             "local prog = R.prog_wznoszenia"),                                                         # odbicie = skok
            ("return ogranicz(v / naturalna, R.tempo_min, R.tempo_max)", "return v / naturalna"),         # tempo bez granic
            ("if k.lokalny and wynik[k.id] == nil then", "if false then"),                               # lokalny bez pierwszeństwa
            ("if not klipUmowy(D, a) then", "if false then"),                                            # umowa przyjmuje wszystko
            ("w = math.max(cel, w - krok)", "w = cel"),                                                  # pozy gasną skokiem
            ("elseif v > B.vOd then", "elseif v > 0 then"),                                              # bieg od zera
            ("return f, math.max(B.podporMin, podpor * f)", "return f, 0.3"),                            # podpór nie skraca się
            ("fz = math.max(0, fz + d * ogranicz(droga, -B.krok, B.krok) / B.krok)", "fz += f * dt"),                              # faza zegarem
            ("fz = fz * d / dPoprz", "fz = fz"),                                                         # stopa skacze przy zmianie podporu
            ("return poprzednia + (chwilowa - poprzednia) * (dt / (dt + stala))", "return chwilowa"),    # prędkość bez wygładzania
            ("return B.krok / 2 - B.krok * (fz / d), B.kostka, 0", "return B.krok / 2, B.kostka, 0"),    # stopa nie cofa się
            ("return doKostki + odchylenie, kolano - math.pi", "return doKostki, kolano - math.pi"),     # zła kinematyka
        ]
        tekst = czytaj("LogikaBohatera.luau")
        for stare, nowe in zepsute:
            self.assertIn(stare, tekst)
            it, Dl, Ll = _luau(tekst.replace(stare, nowe, 1))
            wykryte = self.losowe_kroki(it, Dl, Ll, 30, 150, 21, cicho=True) + self.losowe_inne(it, Dl, Ll, 3000, 22, cicho=True)
            self.assertGreater(wykryte, 0, "nie wykryto: " + stare)


# ============================================================================================== 4. kod
class TestKod(unittest.TestCase):
    def test_4a_kontrola_luau(self):
        pliki = SLB.pliki_pakietu()
        self.assertEqual([os.path.basename(p) for p in pliki],
                         ["DaneBohatera.luau", "KlientBohatera.client.luau", "LogikaBohatera.luau", "SerwerBohatera.server.luau"])
        bledy, parser = SLB.sprawdz_pliki(pliki, wypisz=lambda *_: None)
        self.assertEqual(bledy, [])
        self.assertTrue(parser or LM is None)
        self.assertEqual(SLB.SL.sprawdz_pliki(pliki, wypisz=lambda *_: None), [])
        # kontrola łapie to, czego pilnuje: spaw do postaci, zmianę ruchu postaci, cudze SetAttribute, zasób Animation
        k = czytaj("KlientBohatera.client.luau")
        for dopisek in ('\nlocal w = Instance.new("WeldConstraint")\n', "\nlocal h = nil\nh.WalkSpeed = 0\n",
                        '\ngracz:SetAttribute("X", 1)\n', "\nlocal a = nil\na:LoadAnimation(nil)\n",
                        "\nlocal p = nil\np.Anchored = true\n", "\nlocal v = Vector3.new(0, 250, 0)\n"):
            self.assertNotEqual(SLB.sprawdz_tekst(k + dopisek, "swiat/bohater_swiat/zrodla/KlientBohatera.client.luau", LM), [],
                                dopisek)

    def test_4b_sucho_i_kod_dla_studio(self):
        r = subprocess.run([sys.executable, "-B", os.path.join(PAKIET, "zbuduj.py"), "--sucho"], capture_output=True,
                           text=True, encoding="utf-8", cwd=REPO)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("sucho: OK", r.stdout)
        if LM is not None:
            for nazwa, kod in ZB.wszystkie_kody(D).items():
                LM.Parser(ZB.NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", "1") + kod, nazwa, LM.Interpreter()).program()
        z = czytaj_repo("swiat", "bohater_swiat", "zbuduj.py")
        self.assertNotIn("studio_mcp", z.split("if a.sucho")[0].split("def main")[1])
        self.assertEqual(ZB.MIEJSCE, 129485428021967)
        self.assertIn(("BindableFunction", "Sygnaly/RuchBohatera"), ZB.INNE)
        for kod in ZB.wszystkie_kody(D).values():
            self.assertNotIn("Lighting", kod)
        # każdy kod budowy zaczyna od kontroli własności kontenera, a budowa i usuwanie mają punkty historii
        self.assertIn('GetAttribute("Wygenerowane") ~= true', ZB.START)
        self.assertEqual(ZB.START.count("SetWaypoint"), 3)
        self.assertIn("SetWaypoint", ZB.KONIEC)

    def test_4c_proba_play(self):
        r = subprocess.run([sys.executable, "-B", os.path.join(TU, "proba_play.py"), "--sprawdz"], capture_output=True,
                           text=True, encoding="utf-8", cwd=REPO)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("OK", r.stdout)
        t = czytaj_repo("swiat", "bohater_swiat", "testy", "proba_play.py")
        for kod in ["B%02d" % i for i in range(0, 20)]:
            self.assertIn('punkt("%s"' % kod, t, kod)
        # haczyki, z których korzysta próba, istnieją w kliencie i serwerze
        k = czytaj("KlientBohatera.client.luau")
        for polecenie in ("stan", "pomiar", "ruch", "przezroczystosc", "manekin", "manekin_usun", "faza_biegu", "nagraj",
                          "nagranie"):
            self.assertIn('polecenie == "%s"' % polecenie, k)
        s = czytaj("SerwerBohatera.server.luau")
        for polecenie in ("stan", "wlacz"):
            self.assertIn('polecenie == "%s"' % polecenie, s)
        # próba nie zapisuje wyników (nazwa konta) w repozytorium
        self.assertIn("Folder wyników leży w repozytorium", t)

    def test_4d_umowa_w_kliencie(self):
        k = czytaj("KlientBohatera.client.luau")
        # OnInvoke umowy ustawione przed wczytaniem danych (Invoke bez OnInvoke czeka bez końca)
        self.assertLess(k.index("sygnalRuchu.OnInvoke = function"), k.index('require(moduly:WaitForChild("DaneBohatera"))'))
        self.assertIn('sygnaly:WaitForChild("RuchBohatera")', k)
        self.assertIn("L.polecenieRuchu(D, wym, opis, polecenie, a)", k)
        self.assertIn('typeof(a) == "Vector3"', k)
        self.assertIn("pcall(ruch, polecenie, a)", k)
        # odpowiedź od razu: obsługa umowy nigdzie nie czeka (mini-gra liczy tylko odpowiedź daną bez zwłoki)
        obsluga = k[k.index("local function ruch(polecenie, a)"):k.index("------------------------------------------------------------------ dane")]
        for czekanie in ("WaitForChild", "task.wait", ":Wait()", "require(", "InvokeServer", "task.delay"):
            self.assertNotIn(czekanie, obsluga, czekanie)
        self.assertIn("sygnalRuchu.OnInvoke = function(polecenie, a)", obsluga)
        # wyłącznik czytany co klatkę, bohater bez Humanoida, bez połączeń z postacią
        self.assertIn("kontener:GetAttribute(D.atrybut_wlacznika) ~= false", k)
        self.assertNotIn('Instance.new("Humanoid")', k)
        self.assertIn("c.CanCollide = false", k)
        self.assertIn("c.CanQuery = false", k)
        self.assertIn("c.CanTouch = false", k)
        self.assertIn("c.Massless = true", k)
        self.assertIn("korzen.Anchored = true", k)
        # awatara nie chowamy przez LocalTransparencyModifier (inne pakiety i ich próby czytają go u awatara)
        bez_kom = SLB.SL.rozbierz(k)[0]
        self.assertEqual(re.findall(r"\bo\.LocalTransparencyModifier\s*=", bez_kom), [])
        self.assertEqual(len(re.findall(r"LocalTransparencyModifier\s*=[^=]", bez_kom)), 1)   # tylko części bohatera
        # serwer poza Studio usuwa kontener, klient nic nie robi
        self.assertIn("script.Parent:Destroy()", czytaj("SerwerBohatera.server.luau"))

    def test_4e_uzywane_wejscia_cudzych_modulow(self):
        """Moduły, które pakiet tylko czyta, mają to, czego używa klient (zmiana u sąsiada = ten test, nie błąd w grze)."""
        klipy = czytaj_repo("swiat", "test_walki2", "zrodla", "Klipy.luau")
        for napis in ("function Klipy.nowy(model: Model, dane, opcje: any?)", "opcje.reczny == true", "function Klipy:graj(",
                      "function Klipy:krok(dt: number)", "function Klipy:zastosuj()", "function Klipy:maKlip(",
                      "function Klipy:zniszcz()", "opcje.przejscie", "opcje.petla", "opcje.predkosc", "t.potem = opcje.potem",
                      "local krok = dt * t.predkosc * self.tempo", "staw.Transform = koncowe[idx]"):
            self.assertIn(napis, klipy, napis)
        ub = czytaj_repo("swiat", "stroje_proba", "zrodla", "Ubieranie.luau")
        for napis in ("U.D = D", "U.L = L", "function U.atrybut(klasa)", "function U.zbuduj(klasa, plan, wzor)",
                      'w.Name = "SpawStroju"', "w.Part0 = kosc", "model.PrimaryPart = hrp", "hrp.Anchored = true",
                      'm = Instance.new("Motor6D")', "m.Parent = kosci[i]", 'model:SetAttribute("Stroj"',
                      'model:SetAttribute("StrojBryly", n)'):
            self.assertIn(napis, ub, napis)
        lg = czytaj_repo("swiat", "stroje_proba", "zrodla", "LogikaStrojow.luau")
        for napis in ("function L.plan(D, klasa, ids)", "function L.zNapisu(napis)"):
            self.assertIn(napis, lg, napis)
        self.assertIn("odniesienie", czytaj_repo("swiat", "stroje_proba", "dane.py"))
        k = czytaj("KlientBohatera.client.luau")
        for napis in ("zal.klipy.nowy, model, dane, { reczny = true }", "U.L.zNapisu(napis) or KS.odniesienie",
                      "U.zbuduj(klasa, plan, nil)", "zal.ubieranie.atrybut(klasa)", 'c:FindFirstChild("SpawStroju")'):
            self.assertIn(napis, k, napis)

    def test_4h_miara_dryfu_stop_w_probie(self):
        """Miara z próby w Play (dryf_stop): nagranie złożone z cyklu biegu daje dryf ~0, a ślizg stopy — wyraźny."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("bohater_swiat__proba_play", os.path.join(TU, "proba_play.py"))
        PP = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(PP)
        d, rig = rig_klasy("wojownik")
        B = D["klasy"]["wojownik"]["bieg"]
        v = R["bieg_predkosc"]
        f, pod = L.kadencja(B, v)

        def nagranie(slizg):
            klatki, faza, z, poprzednia = [], 0.0, 0.0, 0.0
            for n in range(150):
                # w grze stawy mają pozę z poprzedniej klatki, a korzeń — z bieżącej
                pozy = rig.pozy(DN.transformy_biegu(rig, L.bieg(B, poprzednia, pod)))
                lewa = pozy[rig.indeks["LeftFoot"]][1]
                prawa = pozy[rig.indeks["RightFoot"]][1]
                klatki.append([n * DT, "bieg", 1.0, faza, pod, v, 0.0, lewa[1], z + lewa[2], 0.0, prawa[1], z + prawa[2],
                               0.0, 3.0, z])
                poprzednia = faza
                faza = (faza + f * slizg * DT) % 1.0
                z -= v * DT                                   # postać biegnie do przodu (−Z)
            return klatki
        dryf, podpory, klatek = PP.dryf_stop(nagranie(1.0))
        self.assertLess(dryf, 0.01)
        self.assertGreater(podpory, 8)
        self.assertGreater(klatek, 30)
        self.assertGreater(PP.dryf_stop(nagranie(0.6))[0], 0.25)          # cykl za wolny o 40% = stopy jadą po ziemi
        self.assertEqual(PP.dryf_stop([]), (0.0, 0, 0))

    def test_4g_nazwy_przed_uzyciem(self):
        """Prawdziwy Luau widzi lokalną funkcję i zmienną dopiero OD jej definicji (wcześniej to globalna nil), a parser
        luau_mini tego nie pilnuje — każda funkcja lokalna i każda zmienna z poziomu pliku przed pierwszym użyciem."""
        for plik in ("KlientBohatera.client.luau", "SerwerBohatera.server.luau", "LogikaBohatera.luau"):
            linie = SLB.SL.rozbierz(czytaj(plik))[1].split("\n")
            definicje = {}
            for i, l in enumerate(linie):
                m = re.match(r"\s*local function (\w+)", l)
                if m:
                    definicje.setdefault(m.group(1), i)
                m = re.match(r"local ([\w, ]+?)\s*(=|$)", l)          # tylko poziom pliku (bez wcięcia)
                if m:
                    for n in m.group(1).split(","):
                        definicje.setdefault(n.strip(), i)
            self.assertGreater(len(definicje), 3, plik)
            for nazwa, d in definicje.items():
                if nazwa == "_":
                    continue
                for i in range(d):
                    # użycie = samodzielna nazwa (nie pole .x / :x, nie klucz tabeli „x =”, nie parametr ani inny local)
                    for m in re.finditer(r"(?<![\w.:])%s\b(?!\s*=[^=])" % re.escape(nazwa), linie[i]):
                        przed = linie[i][:m.start()]
                        if re.search(r"\blocal\s+[\w, ]*$", przed) or re.search(r"function\s*[\w.:]*\([\w, ]*$", przed) \
                                or re.search(r"\bfor\s+[\w, ]*$", przed):
                            continue
                        self.fail("%s: „%s” użyte w linii %d przed definicją (linia %d)" % (plik, nazwa, i + 1, d + 1))

    def test_4f_bez_danych_prywatnych(self):
        # ścieżki lokalne (dysk, katalog użytkownika, katalog tymczasowy) — wzorce składane, żeby nie trafiały same w siebie
        wzorce = [r"[A-Za-z]:\\" + "Users", "/" + "Users/", "App" + "Data", r"\\" + "Temp" + r"\\", "scratch" + "pad"]
        pliki = [os.path.join(PAKIET, n) for n in os.listdir(PAKIET) if n.endswith((".py", ".json", ".md"))]
        pliki += SLB.pliki_pakietu() + [os.path.join(TU, n) for n in os.listdir(TU) if n.endswith((".py", ".json"))]
        self.assertGreater(len(pliki), 8)
        for sciezka in pliki:
            with open(sciezka, encoding="utf-8") as f:
                tekst = f.read()
            for w in wzorce:
                self.assertIsNone(re.search(w, tekst), "%s: %s" % (os.path.basename(sciezka), w))
        # żadnych wyników prób w pakiecie (mogą zawierać nazwę konta)
        self.assertEqual([n for n in os.listdir(TU) if n.endswith(".json")], [])


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    unittest.main()
