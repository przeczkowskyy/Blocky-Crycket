#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy próby ubierania postaci (D-071) BEZ Studio (unittest).

    python -B swiat/stroje_proba/testy/test_strojow.py         # wszystkie testy
    python -B swiat/stroje_proba/testy/test_strojow.py -v

1. Dane: DaneStrojow.luau aktualny i powtarzalny; przedmioty = katalog swiat/postacie/przedmioty.json (te same id,
   nazwy, sloty); strój odniesienia złożony z naszych danych = szablon walki (dane/<klasa>.json, co do bryły);
   KAŻDY dopuszczalny strój (wszystkie podzbiory przedmiotów klasy) złożony z naszych danych = biblioteczne
   ubierz() modułu bohatera (ta sama zasada co Ubieranie.luau: powłoka, włosy, segmenty, korekty chwytu kota).
2. Logika: przypadki wzorcowe (część zbroi, inna klasa, dwa w slocie, dwie powłoki, zestawy, oferta okna) w obu
   ustawieniach spodni i obu doborach; ten sam plik LogikaStrojow.luau w interpreterze luau_mini = lustro w Pythonie
   na tysiącach losowych wywołań; zepsuta logika wykryta.
3. Klipy: w każdym dopuszczalnym stroju, w każdej klatce każdego klipu walki nic nie schodzi pod ziemię głębiej niż
   strój odniesienia; w ostatniej klatce upadku kapelusz i kostur kota leżą na ziemi; zawis gołego ciała (sprawa
   „do ustalenia”) wypisany i nie większy niż znany (Rycerz 0,25, kot 0,20, Zwiadowca 0).
4. Kod: kontrola Luau pakietu; haczyk w swiat/test_walki2/zrodla/Aktorzy.luau (zapas: dawny szablon); zbuduj.py
   --sucho; kod wysyłany do Studio parsuje się.
"""
import collections
import copy
import itertools
import json
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
for _s in (REPO, os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki2"), PAKIET):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import dane as DN  # noqa: E402
import logika_strojow as L  # noqa: E402
import sprawdz_luau_strojow as SLS  # noqa: E402
import zbuduj as ZB  # noqa: E402

LM = SLS.luau_mini()
ZR = os.path.join(PAKIET, "zrodla")
D, PY = DN.zbierz()
KATALOG = json.load(open(DN.KATALOG, encoding="utf-8"))


def czytaj(plik):
    with open(os.path.join(ZR, plik), encoding="utf-8") as f:
        return f.read()


def wszystkie_stroje(klasa, D_=None):
    """Wszystkie podzbiory przedmiotów klasy przyjęte przez logikę (strój kanoniczny)."""
    D_ = D_ or D
    wynik = []
    ids = D_["klasy"][klasa]["przedmioty"]
    for r in range(len(ids) + 1):
        for sub in itertools.combinations(ids, r):
            ok, plan = L.plan(D_, klasa, list(sub))
            if ok and plan["przedmioty"] == list(sub):
                wynik.append(plan)
    return wynik


# ============================================================================================== 1. dane
class TestDane(unittest.TestCase):
    def test_1a_plik_aktualny_i_powtarzalny(self):
        ok, _ = DN.aktualny()
        self.assertTrue(ok, "zrodla/DaneStrojow.luau nieaktualny — python -B swiat/stroje_proba/dane.py")
        with tempfile.TemporaryDirectory() as tmp:
            DN.zapisz(tmp)
            with open(os.path.join(tmp, DN.PLIK_LUAU), encoding="utf-8") as f:
                self.assertEqual(f.read(), czytaj(DN.PLIK_LUAU))
        self.assertLess(len(czytaj(DN.PLIK_LUAU)), 199000)

    def test_1b_przedmioty_z_katalogu(self):
        bohaterowie = {"rycerz", "zwiadowca", "kot_mag"}
        z_katalogu = {p["id"]: p for p in KATALOG["przedmioty"] if p.get("zestaw") in bohaterowie}
        self.assertEqual(set(z_katalogu), set(D["przedmioty"]))
        self.assertEqual(len(D["przedmioty"]), 20)
        for i, P in D["przedmioty"].items():
            k = z_katalogu[i]
            self.assertEqual((P["nazwa"], P["slot"], P["kategoria"], P["cialo"], P["klasy"], P["czescOd"], P["ukrywa"]),
                             (k["nazwa"], k["slot"], k["kategoria"], k["cialo"], k["klasy"], k["czesc_od"], k["ukrywa"]), i)
            self.assertEqual([s["id"] for s in P["segmenty"]], [c["id"] for c in k["czesci"]], i)
        sloty = {s["id"] for s in D["sloty"]}
        for P in D["przedmioty"].values():
            self.assertIn(P["slot"], sloty)

    def test_1c_odniesienie_rowne_szablonowi_walki(self):
        import aktorzy as A
        oczekiwane = {"wojownik": 127, "zwiadowca": 182, "mag": 166}
        for klasa, K in D["klasy"].items():
            d = A.wczytaj(klasa)
            ok, plan = L.plan(D, klasa, K["odniesienie"])
            self.assertTrue(ok)
            nasze = DN.zloz(D, klasa, plan)
            self.assertEqual(len(nasze), len(d["czesci"]), klasa)
            self.assertEqual(len(nasze), oczekiwane[klasa], klasa)
            self.assertEqual(collections.Counter(DN.klucz_bryly(w) for w in nasze),
                             collections.Counter(DN.klucz_bryly(w) for w in DN.wiersze_walki(d)), klasa)
            self.assertEqual([k[0] for k in K["kosci"]], [k[0] for k in d["kosci"]])

    def test_1d_kazdy_stroj_rowny_bibliotecznemu_ubierz(self):
        from swiat.postacie.biblioteka import roblox_klocki as RK
        from swiat.postacie.ekwipunek import ubierz
        razem = 0
        for klasa in D["klasy"]:
            pom = PY[klasa]
            po_id = {p.id: p for p in pom["przedmioty"]}
            for plan in wszystkie_stroje(klasa):
                lib = RK.rig(ubierz(pom["cialo"], [po_id[i] for i in plan["przedmioty"]], korekty=pom["korekty"]))
                lw = [list(c[:13]) + [tuple(lib["materialy"][c[13]]), lib["grupy"][c[14]], c[15]] for c in lib["czesci"]]
                self.assertEqual(collections.Counter(DN.klucz_bryly(w) for w in DN.zloz(D, klasa, plan)),
                                 collections.Counter(DN.klucz_bryly(w) for w in lw), (klasa, plan["przedmioty"]))
                razem += 1
        # spodnie są częścią zbroi: 7 niezależnych wyborów u Wojownika i Zwiadowcy (2^7), 4 u Maga (2^4)
        self.assertEqual(razem, 128 + 128 + 16)

    def test_1e_powloka_i_wlosy(self):
        # hełm chowa włosy, zbroja zdejmuje gołe bryły tułowia i rąk, a goły Rycerz ma włosy
        ok, p0 = L.plan(D, "wojownik", [])
        ok2, p1 = L.plan(D, "wojownik", ["rycerz_helm", "rycerz_zbroja"])
        self.assertTrue(ok and ok2)
        g0 = {w[14] for w in DN.zloz(D, "wojownik", p0)}
        g1 = {w[14] for w in DN.zloz(D, "wojownik", p1)}
        self.assertIn("rycerz_wlosy", g0)
        self.assertNotIn("rycerz_wlosy", g1)
        self.assertEqual(p1["zakryte"], {"UpperTorso", "LeftUpperArm", "RightUpperArm", "LeftLowerArm", "RightLowerArm",
                                         "LowerTorso", "LeftUpperLeg", "RightUpperLeg"})
        self.assertEqual(p1["ukryte"], {"Wlosy"})

    def test_1f_segmenty_na_kosciach_szkieletu(self):
        for klasa, K in D["klasy"].items():
            kosci = {k[0] for k in K["kosci"]}
            for i in K["przedmioty"]:
                for s in D["przedmioty"][i]["segmenty"]:
                    self.assertIn(s["kosc"], kosci, (i, s["id"]))
                    self.assertTrue(s["czesci"], (i, s["id"]))
        # kapelusz i kostur kota na kościach nośnych (spadają w upadku), broń człowieka w dłoni
        seg = {i: D["przedmioty"][i]["segmenty"] for i in D["przedmioty"]}
        self.assertEqual(seg["kot_mag_kapelusz"][0]["kosc"], "HatPivot")
        self.assertEqual(seg["kot_mag_kostur"][0]["kosc"], "StaffPivot")
        self.assertEqual(seg["rycerz_miecz"][0]["kosc"], "RightHand")
        self.assertEqual(seg["rycerz_tarcza"][0]["kosc"], "LeftHand")
        self.assertEqual([s["kosc"] for s in seg["zwiadowca_luk"]], ["UpperTorso", "LeftHand"])


# ============================================================================================== 2. logika
def wariant(spodnie=None, dobor=None):
    D2 = copy.deepcopy(D)
    if spodnie:
        D2["spodnie"] = spodnie
    if dobor:
        D2["dobor"] = dobor
    return D2


class TestLogika(unittest.TestCase):
    def test_2a_przypadki_wzorcowe(self):
        ok, st = L.zaloz(D, "wojownik", [], "rycerz_helm")
        self.assertEqual((ok, st), (True, ["rycerz_helm"]))
        ok, st = L.zaloz(D, "wojownik", ["rycerz_helm"], "rycerz_zbroja")
        self.assertEqual(st, ["rycerz_helm", "rycerz_zbroja", "rycerz_nogawice"])      # spodnie razem ze zbroją
        ok, st = L.zdejmij(D, "wojownik", st, "Chest")
        self.assertEqual(st, ["rycerz_helm"])                                           # i zdjęte razem z nią
        self.assertEqual(L.zaloz(D, "wojownik", [], "rycerz_nogawice"), (False, "czesc_zbroi"))
        self.assertEqual(L.normalizuj(D, "wojownik", ["rycerz_nogawice"]), (False, "czesc_bez_calosci"))
        self.assertEqual(L.zaloz(D, "wojownik", [], "kot_mag_kapelusz"), (False, "przedmiot_innej_klasy"))
        self.assertEqual(L.zaloz(D, "mag", [], "rycerz_miecz"), (False, "przedmiot_innej_klasy"))
        self.assertEqual(L.zaloz(D, "wojownik", [], "nie_ma"), (False, "nieznany_przedmiot"))
        self.assertEqual(L.zaloz(D, "lucznik", [], "rycerz_helm"), (False, "zla_klasa"))
        self.assertEqual(L.zdejmij(D, "wojownik", [], "Plecy"), (False, "zly_slot"))
        self.assertEqual(L.zestaw(D, "mag", "golas"), (True, []))
        self.assertEqual(L.zestaw(D, "mag", "komplet")[1], D["klasy"]["mag"]["odniesienie"])
        self.assertEqual(L.zestaw(D, "mag", "nie_ma"), (False, "nieznany_zestaw"))
        # wymiana w slocie: drugi przedmiot tego samego slotu zastępuje pierwszy (dobór po ciele: kaptur za hełm)
        Dc = wariant(dobor="cialo")
        ok, st = L.zaloz(Dc, "wojownik", ["rycerz_helm", "rycerz_miecz"], "zwiadowca_kaptur")
        self.assertEqual(st, ["rycerz_miecz", "zwiadowca_kaptur"])
        self.assertEqual(L.normalizuj(Dc, "wojownik", ["rycerz_helm", "zwiadowca_kaptur"]), (False, "dwa_w_slocie"))
        self.assertEqual(L.zaloz(Dc, "wojownik", [], "kot_mag_szata"), (False, "przedmiot_innej_klasy"))
        self.assertTrue(L.zaloz(Dc, "mag", [], "rycerz_miecz")[0])                      # broń w dłoni: „dowolne”
        # dwie powłoki na jednej kości (sztucznie: pas, który zakrywa tułów)
        Dp = copy.deepcopy(D)
        Dp["przedmioty"]["rycerz_pas"]["segmenty"][0]["kosc"] = "UpperTorso"
        Dp["przedmioty"]["rycerz_pas"]["segmenty"][0]["zakrywa"] = True
        self.assertEqual(L.normalizuj(Dp, "wojownik", ["rycerz_zbroja", "rycerz_pas"]), (False, "dwie_powloki"))

    def test_2b_oferta_okna(self):
        sloty = {k: [o["slot"] for o in L.oferta(D, k)] for k in D["klasy"]}
        self.assertEqual(sloty["wojownik"], ["Helmet", "Chest", "Gloves", "Boots", "Belt", "Weapon", "OffHand"])
        self.assertEqual(sloty["zwiadowca"], ["Helmet", "Chest", "Gloves", "Boots", "Belt", "Weapon", "OffHand"])
        self.assertEqual(sloty["mag"], ["Helmet", "Chest", "Belt", "Weapon"])
        Ds = wariant(spodnie="osobny_slot")
        self.assertEqual([o["slot"] for o in L.oferta(Ds, "wojownik")],
                         ["Helmet", "Chest", "Legs", "Gloves", "Boots", "Belt", "Weapon", "OffHand"])
        self.assertEqual(L.zaloz(Ds, "wojownik", [], "rycerz_nogawice"), (True, ["rycerz_nogawice"]))
        ok, st = L.zdejmij(Ds, "wojownik", ["rycerz_zbroja", "rycerz_nogawice"], "Chest")
        self.assertEqual(st, ["rycerz_nogawice"])
        self.assertEqual(L.oferta(D, "nie_ma"), [])

    def test_2c_napis(self):
        self.assertIsNone(L.z_napisu(None))
        self.assertEqual(L.z_napisu(""), [])
        self.assertEqual(L.z_napisu(",a,,b,"), ["a", "b"])
        self.assertEqual(L.na_napis(["a", "b"]), "a,b")


def _luau_dane_i_logika(D_=None):
    it = LM.Interpreter()
    rs = LM.Tabela()
    rs.set("IsStudio", lambda _self: True)
    game = LM.Tabela()
    game.set("GetService", lambda _self, _n: rs)
    it.globalne.z["game"] = game
    Dl = it.wykonaj(czytaj(DN.PLIK_LUAU), DN.PLIK_LUAU)[0]
    if D_ is not None:
        Dl.set("spodnie", D_["spodnie"])
        Dl.set("dobor", D_["dobor"])
    Ll = it.wykonaj(czytaj("LogikaStrojow.luau"), "LogikaStrojow.luau")[0]
    return it, Dl, Ll


def _norm(v):
    """Wynik Luau/Pythona w jednej postaci (zbiory jako posortowane listy, puste tabele jako [])."""
    if isinstance(v, set):
        return sorted(v)
    if isinstance(v, dict):
        if v and all(x is True for x in v.values()):
            return sorted(v)
        return {k: _norm(x) for k, x in v.items()} if v else []
    if isinstance(v, (list, tuple)):
        return [_norm(x) for x in v]
    return v


@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py — Luau nie wykonany")
class TestLuau(unittest.TestCase):
    def wolaj(self, it, Ll, nazwa, *argi):
        return [LM.z_luau(x, pusta_jako_lista=True) for x in it.wywolaj(Ll.get(nazwa), list(argi))]

    def losowe(self, D_, it, Dl, Ll, n, ziarno):
        rnd = random.Random(ziarno)
        wszystkie = list(D_["przedmioty"]) + ["nie_ma", "", "Rycerz_Helm"]
        klasy = list(D_["klasy"]) + ["nie_ma"]
        sloty = [s["id"] for s in D_["sloty"]] + ["Plecy"]
        zestawy = sorted({z["id"] for K in D_["klasy"].values() for z in K["zestawy"]}) + ["brak"]
        zle = 0
        for _ in range(n):
            klasa = rnd.choice(klasy)
            pula = D_["klasy"][klasa]["przedmioty"] if klasa in D_["klasy"] and rnd.random() < 0.7 else wszystkie
            stroj = [rnd.choice(pula) for _ in range(rnd.randint(0, 6))]
            lstroj = LM.do_luau(stroj)
            co = rnd.choice(["normalizuj", "zaloz", "zdejmij", "zestaw", "plan", "oferta", "napis"])
            if co == "normalizuj":
                py, lu = L.normalizuj(D_, klasa, stroj), self.wolaj(it, Ll, "normalizuj", Dl, klasa, lstroj)
            elif co == "zaloz":
                i = rnd.choice(wszystkie)
                py, lu = L.zaloz(D_, klasa, stroj, i), self.wolaj(it, Ll, "zaloz", Dl, klasa, lstroj, i)
            elif co == "zdejmij":
                s = rnd.choice(sloty)
                py, lu = L.zdejmij(D_, klasa, stroj, s), self.wolaj(it, Ll, "zdejmij", Dl, klasa, lstroj, s)
            elif co == "zestaw":
                z = rnd.choice(zestawy)
                py, lu = L.zestaw(D_, klasa, z), self.wolaj(it, Ll, "zestaw", Dl, klasa, z)
            elif co == "plan":
                py, lu = L.plan(D_, klasa, stroj), self.wolaj(it, Ll, "plan", Dl, klasa, lstroj)
            elif co == "oferta":
                py, lu = [L.oferta(D_, klasa)], self.wolaj(it, Ll, "oferta", Dl, klasa)
            else:
                napis = ",".join(rnd.choice(["a", "", "rycerz_helm", "x_y"]) for _ in range(rnd.randint(0, 5)))
                py, lu = [L.z_napisu(napis)], self.wolaj(it, Ll, "zNapisu", napis)
            if _norm(list(py)) != _norm(lu):
                zle += 1
                if zle <= 3:
                    print("ROZJAZD", co, klasa, stroj, py, lu)
        return zle

    def test_2d_luau_rowna_lustru(self):
        for i, (spodnie, dobor) in enumerate([(None, None), ("osobny_slot", None), (None, "cialo"),
                                              ("osobny_slot", "cialo")]):
            D_ = wariant(spodnie, dobor)
            it, Dl, Ll = _luau_dane_i_logika(D_)
            self.assertEqual(self.losowe(D_, it, Dl, Ll, 900, 17 + i), 0, (spodnie, dobor))

    def test_2e_luau_kazdy_stroj_klasy(self):
        it, Dl, Ll = _luau_dane_i_logika()
        for klasa in D["klasy"]:
            ids = D["klasy"][klasa]["przedmioty"]
            for r in range(len(ids) + 1):
                for sub in itertools.combinations(ids, r):
                    py = L.plan(D, klasa, list(sub))
                    lu = self.wolaj(it, Ll, "plan", Dl, klasa, LM.do_luau(list(sub)))
                    self.assertEqual(_norm(list(py)), _norm(lu), (klasa, sub))

    def test_2f_zepsuta_logika_wykryta(self):
        zepsute = [
            ("if zbior[id] and c ~= nil and not zbior[c] then", "if false then"),          # brak „część bez całości”
            ("if sloty[s] then", "if false then"),                                          # dwa w slocie
            ("return table.find(P.klasy, klasa) ~= nil", "return true"),                    # przedmiot innej klasy
            ("zakryte[seg.kosc] = true", "zakryte[seg.kosc] = nil"),                       # powłoka nic nie chowa
        ]
        tekst = czytaj("LogikaStrojow.luau")
        for stare, nowe in zepsute:
            self.assertIn(stare, tekst)
            wykryte = 0
            # dwa w slocie zdarza się tylko przy doborze po ciele (u każdej klasy jeden przedmiot na slot)
            for D_ in (D, wariant(dobor="cialo")):
                it, Dl, _ = _luau_dane_i_logika(D_)
                Ll = it.wykonaj(tekst.replace(stare, nowe, 1), "zepsuta")[0]
                wykryte += self.losowe(D_, it, Dl, Ll, 900, 99)
            self.assertGreater(wykryte, 0, "nie wykryto: " + stare)


# ============================================================================================== 3. klipy
def _najnizej_brył(d):
    """Dla każdej klatki każdego klipu: {klucz bryły: najniższy punkt} dla wszystkich brył z listy d["czesci"].
    Najniższy punkt pudła = t_y − Σ |R[1][j]| · h_j (bez liczenia 8 rogów)."""
    from geometria import Rig, cf, orientacja, razy, przesun
    r = Rig(d)
    lok = []
    for c in d["czesci"]:
        sr = r.srodek(c[0])
        l = razy(przesun((-sr[0], -sr[1], -sr[2])), cf((c[3], c[4], c[5]), orientacja(c[6], c[7], c[8])))
        lok.append((c[0], l, (c[9] / 2.0, c[10] / 2.0, c[11] / 2.0)))
    wynik = {}
    for nazwa, kl in r.klipy.items():
        for f in range(kl["dl"] + 1):
            pozy = r.pozy(r.transformy(nazwa, f))
            wiersz = []
            for i, l, h in lok:
                Rb, tb = pozy[i]
                Rl, tl = l
                rz = [sum(Rb[1][k] * Rl[k][j] for k in range(3)) for j in range(3)]
                ty = tb[1] + sum(Rb[1][k] * tl[k] for k in range(3))
                wiersz.append(ty - abs(rz[0]) * h[0] - abs(rz[1]) * h[1] - abs(rz[2]) * h[2])
            wynik[(nazwa, f)] = wiersz
    return wynik


class TestKlipy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import aktorzy as A
        cls.dane = {}
        for klasa in D["klasy"]:
            d = A.wczytaj(klasa)
            # wszystkie bryły, jakie mogą się pojawić (ciało, akcesoria ciała, każdy przedmiot) — każda raz
            K = D["klasy"][klasa]
            wszystko = {"zakryte": set(), "ukryte": set(), "przedmioty": []}
            unia = DN.zloz(D, klasa, wszystko)
            for i in K["przedmioty"]:
                unia += DN.zloz(D, klasa, {"zakryte": {k[0] for k in K["kosci"]}, "ukryte": {"Wlosy"}, "przedmioty": [i]})
            indeks = {}
            for w in unia:
                indeks.setdefault(DN.klucz_bryly(w), len(indeks))
            jedne = [None] * len(indeks)
            for w in unia:
                jedne[indeks[DN.klucz_bryly(w)]] = w
            dd = dict(d)
            dd["czesci"] = jedne
            cls.dane[klasa] = (d, indeks, _najnizej_brył(dd), jedne)

    def nizej(self, klasa, plan):
        d, indeks, tab, jedne = self.dane[klasa]
        idx = [indeks[DN.klucz_bryly(w)] for w in DN.zloz(D, klasa, plan)]
        return {k: min(v[i] for i in idx) for k, v in tab.items()}, idx

    def test_3a_nic_glebiej_niz_odniesienie(self):
        for klasa, K in D["klasy"].items():
            ok, ref = L.plan(D, klasa, K["odniesienie"])
            ref_n, _ = self.nizej(klasa, ref)
            najgorzej = (0.0, None)
            for plan in wszystkie_stroje(klasa):
                n, _ = self.nizej(klasa, plan)
                for k, v in n.items():
                    roznica = ref_n[k] - v
                    if roznica > najgorzej[0]:
                        najgorzej = (roznica, (plan["przedmioty"], k))
            print("\n  %s: największe zejście niżej niż odniesienie: %.3f %s" % (klasa, najgorzej[0], najgorzej[1] or ""))
            self.assertLessEqual(najgorzej[0], 0.035, klasa)   # gołe dłonie Zwiadowcy: 0,030 (EKWIPUNEK.md pkt 11)

    def test_3b_upadek_przedmioty_na_ziemi_i_zawis_ciala(self):
        zawis_maks = {"wojownik": 0.26, "zwiadowca": 0.03, "mag": 0.21}
        for klasa, K in D["klasy"].items():
            d, indeks, tab, jedne = self.dane[klasa]
            ost = ("upadek", next(k["dl"] for k in d["klipy"] if k["n"] == "upadek"))
            spadajace = {"HatPivot", "StaffPivot"}
            kosci = [k[0] for k in K["kosci"]]
            najwiekszy = (0.0, None)
            for plan in wszystkie_stroje(klasa):
                _, idx = self.nizej(klasa, plan)
                cialo = [tab[ost][i] for i in idx if kosci[jedne[i][0] - 1] not in spadajace]
                zawis = min(cialo)
                if zawis > najwiekszy[0]:
                    najwiekszy = (zawis, plan["przedmioty"])
                self.assertGreaterEqual(zawis, -0.06, (klasa, plan["przedmioty"]))
                for i in plan["przedmioty"]:
                    for s in D["przedmioty"][i]["segmenty"]:
                        if s["kosc"] in spadajace:
                            ys = [tab[ost][j] for j in idx if kosci[jedne[j][0] - 1] == s["kosc"]]
                            # przedmiot, który spada w upadku, leży na ziemi (nie wisi, nie wchodzi w nią)
                            self.assertLessEqual(min(ys), 0.05, (klasa, i))
                            self.assertGreaterEqual(min(ys), -0.06, (klasa, i))
            print("\n  %s: największy zawis ciała w ostatniej klatce upadku: %.3f studa (%s)"
                  % (klasa, najwiekszy[0], ", ".join(najwiekszy[1]) if najwiekszy[1] is not None else "-"))
            self.assertLessEqual(najwiekszy[0], zawis_maks[klasa], klasa)

    def test_3c_klipy_ruszaja_tylko_koscmi_szkieletu(self):
        for klasa, K in D["klasy"].items():
            d = self.dane[klasa][0]
            n = len(K["kosci"])
            for kl in d["klipy"]:
                self.assertTrue(all(1 <= i <= n for i in kl["kosci"]), (klasa, kl["n"]))


# ============================================================================================== 4. kod
class TestKod(unittest.TestCase):
    def test_4a_kontrola_luau(self):
        bledy, parser = SLS.sprawdz_pliki(SLS.pliki_pakietu(), wypisz=lambda *_: None)
        self.assertEqual(bledy, [])
        self.assertTrue(parser or LM is None)
        nazwy = {os.path.basename(p) for p in SLS.pliki_pakietu()}
        self.assertEqual(nazwy, {s[0] for s in ZB.SKRYPTY})

    def test_4b_haczyk_w_aktorach_walki(self):
        with open(ZB.AKTORZY_WALKI, encoding="utf-8") as f:
            t = f.read()
        self.assertIn("local model = zeStrojem(klucz, wzor, opcje.stroj) or wzor:Clone()", t)
        cialo = t[t.index("local function zeStrojem"):t.index("function Aktorzy.obrys")]
        self.assertIn('workspace:FindFirstChild("StrojeProba")', cialo)
        self.assertIn('GetAttribute("Wygenerowane") == true', cialo)
        self.assertIn("pcall(", cialo)
        self.assertIn("if stroj == false then", cialo)
        self.assertNotIn("[TestWalki2]", cialo)       # ostrzeżenie stroju nie myli prób konsoli walki
        bledy = SLS.SL.sprawdz_pliki([ZB.AKTORZY_WALKI])
        self.assertEqual(bledy, [])
        if LM is not None:
            bez = re.sub(r"\s*::\s*[A-Za-z_][A-Za-z0-9_?]*", "", t)
            LM.Parser(bez, "Aktorzy.luau", LM.Interpreter()).program()
        # Ubieranie: dawny szablon, gdy klasy nie ma w danych albo gracz nie ma stroju
        u = czytaj("Ubieranie.luau")
        self.assertIn('if type(klasa) ~= "string" or D.klasy[klasa] == nil or stroj == false then\n\t\treturn nil', u)
        self.assertIn("if ids == nil then\n\t\t\treturn nil", u)

    def test_4c_serwer_jest_zrodlem_prawdy(self):
        s = czytaj("SerwerStrojow.server.luau")
        k = czytaj("KlientStrojow.client.luau")
        o = czytaj("OknoStrojow.luau")
        self.assertIn("script.Parent:Destroy()", s.split("IsStudio()")[1][:60])
        self.assertIn("gracz:SetAttribute(nazwa", s)
        for plik, tekst in (("klient", k), ("okno", o), ("ubieranie", czytaj("Ubieranie.luau"))):
            self.assertNotRegex(tekst, r"gracz:SetAttribute|LocalPlayer:SetAttribute", plik)
        self.assertIn("InvokeServer", k)
        for akcja in ("zaloz", "zdejmij", "zestaw", "dawny", "stan"):
            self.assertIn("%s = true" % akcja, s)
        self.assertIn("D.limit", s)

    def test_4d_sucho_i_kod_dla_studio(self):
        r = subprocess.run([sys.executable, "-B", os.path.join(PAKIET, "zbuduj.py"), "--sucho"], capture_output=True,
                           text=True, encoding="utf-8", cwd=REPO)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("sucho: OK", r.stdout)
        if LM is not None:
            for nazwa, kod in ZB.wszystkie_kody(D).items():
                LM.Parser(ZB.NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", "1") + kod, nazwa, LM.Interpreter()).program()
        with open(os.path.join(PAKIET, "zbuduj.py"), encoding="utf-8") as f:
            self.assertNotIn("studio_mcp", f.read().split("if a.sucho")[0].split("def main")[1])

    def test_4f_proba_play_kompiluje_sie(self):
        import py_compile
        py_compile.compile(os.path.join(TU, "proba_play.py"), doraise=True,
                           cfile=os.path.join(tempfile.gettempdir(), "proba_play_strojow.pyc"))
        with open(os.path.join(TU, "proba_play.py"), encoding="utf-8") as f:
            t = f.read()
        for kod in ("S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09", "S10"):
            self.assertIn('punkt("%s"' % kod, t)
        # haczyki, z których korzysta próba, istnieją w kliencie i serwerze
        k = czytaj("KlientStrojow.client.luau")
        for polecenie in ("stan", "otworz", "zamknij", "klasa", "graj", "zmien", "pomiar", "przebieg"):
            self.assertIn('polecenie == "%s"' % polecenie, k)
        self.assertIn('polecenie == "ustaw"', czytaj("SerwerStrojow.server.luau"))

    def test_4g_okno_na_klasie_gracza(self):
        # 17.11.2026: okno otwiera się na klasie z atrybutu Class (Mag → zakładka Maga), bez klasy — jak dawniej;
        # mapa nazw ta sama co w Stale lasu (swiat/las_potwory) i w danych swiat/stan_gracza
        k = czytaj("KlientStrojow.client.luau")
        wzor = r"local KLASY_GRACZA = (\{[^}]*\})"
        m = re.search(wzor, k)
        self.assertIsNotNone(m)
        with open(os.path.join(REPO, "swiat", "las_potwory", "zrodla", "Stale.luau"), encoding="utf-8") as f:
            stale = re.search(r"S\.KLASY_GRACZA = (\{[^}]*\})", f.read())
        self.assertIsNotNone(stale)
        mapa = dict(re.findall(r'(\w+) = "(\w+)"', m.group(1)))
        self.assertEqual(mapa, dict(re.findall(r'(\w+) = "(\w+)"', stale.group(1))))
        self.assertEqual(set(mapa.values()), set(D["klasy"]))
        self.assertIn('gracz:GetAttribute("Class")', k)
        cialo = k[k.index("local function otworz()"):]
        cialo = cialo[:cialo.index("stan.okno = Okno.nowe")]
        self.assertIn("local mojaKlasa = klasaGracza()", cialo)
        self.assertIn("if mojaKlasa and mojaKlasa ~= stan.klasa then", cialo)
        self.assertIn("stan.klasa = mojaKlasa", cialo)
        if LM is not None:  # klasaGracza w luau_mini: Mage → mag, nieznana / brak → nil
            f = k[k.index("local function klasaGracza()"):k.index("local function otworz()")]
            for klasa, oczek in (("Mage", "mag"), ("Warrior", "wojownik"), ("Scout", "zwiadowca"), ("Nie", None),
                                 (None, None)):
                atr = "nil" if klasa is None else '"%s"' % klasa
                kod = ('local KLASY_GRACZA = %s local D = { klasy = { wojownik = {}, zwiadowca = {}, mag = {} } } '
                       'local gracz = { GetAttribute = function(_, n) if n == "Class" then return %s end return nil end } '
                       '%s return klasaGracza()' % (m.group(1), atr, f))
                wynik = LM.Interpreter().wykonaj(kod, "klasaGracza")
                self.assertEqual(LM.z_luau(wynik[0]) if wynik else None, oczek, klasa)

    def test_4e_bez_danych_prywatnych(self):
        # ścieżki lokalne (dysk, katalog użytkownika, katalog tymczasowy) — wzorce składane, żeby nie trafiały same w siebie
        wzorce = [r"[A-Za-z]:\\" + "Users", "/" + "Users/", "App" + "Data", r"\\" + "Temp" + r"\\"]
        for sciezka in [os.path.join(PAKIET, n) for n in os.listdir(PAKIET) if n.endswith((".py", ".json", ".md"))] + \
                SLS.pliki_pakietu() + [os.path.join(TU, n) for n in os.listdir(TU) if n.endswith((".py", ".json"))]:
            with open(sciezka, encoding="utf-8") as f:
                tekst = f.read()
            for w in wzorce:
                self.assertIsNone(re.search(w, tekst), "%s: %s" % (os.path.basename(sciezka), w))


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    unittest.main()
