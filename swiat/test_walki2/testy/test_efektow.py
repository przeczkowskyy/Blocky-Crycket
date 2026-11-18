#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Efekty 3D walki BEZ Studio: prawdziwy kod zrodla/Efekty3D.luau wykonany interpreterem tools/walka/luau_mini.py
na atrapach Roblox (unittest).

    python -B swiat/test_walki2/testy/test_efektow.py            # testy
    python -B swiat/test_walki2/testy/test_efektow.py --tabela   # tabela kosztu efektów (do README)

Co to sprawdza (i czego NIE):
  • każdy pocisk, wybuch, ozdoba statusu i efekt dodatkowy (fala, pazury, kły, obłok drobin, chmura, korzenie, kałuża,
    parada, wskrzeszenie) da się utworzyć i przejść krok po kroku bez błędu wykonania (indeksowanie nil, działanie
    na nil, brak funkcji) — przy kroku czasu sceny ×1, ×2 i ×4;
  • LICZNIK: ile instancji (części, emiterów, smug, zaczepów, świateł) tworzy każdy efekt; własne efekty Dżungli
    mają budżet (≤ 16 instancji, ≤ 1 emiter, bez świateł) i dokładne liczby z tabeli KOSZT_DZUNGLI;
  • SPRZĄTANIE: po końcu efektu nie zostaje żadna jego instancja (poza iskrami w puli), a po fx:wyczysc() — także
    w połowie lotu i z ozdobami na postaciach (pominięcie walki) — nie zostaje nic; licznik fx:licznik() = 0.
  • NIE sprawdza wyglądu ani geometrii: wektory i układy współrzędnych to atrapy bez matematyki (każde działanie
    daje atrapę). Jak efekt wygląda i czy trafia w cel, pokazuje dopiero próba w Studio (testy/proba_play.py).

Interpreter luau_mini nie zna metatabel ani działań na obiektach, więc ten plik podmienia w nim (tylko w pamięci
procesu testu) dwie funkcje: indeksowanie (metatabela __index, atrapy) i arytmetykę (atrapa pochłania działanie).
"""
import os
import sys
import unittest
from collections import Counter

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
KATALOG = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(KATALOG))
for _s in (os.path.join(REPO, "tools", "walka"), TU):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import luau_mini as LM  # noqa: E402

ZRODLO = os.path.join(KATALOG, "zrodla", "Efekty3D.luau")
LICZBY = {"X", "Y", "Z", "Magnitude"}          # pola atrapy, które są liczbami
CZESCI = {"Part", "WedgePart"}

# koszt własnych efektów Dżungli: rodzaj:nazwa → (wszystkich instancji, części, emiterów); iskry liczone jak przy
# pierwszym użyciu (pusta pula) — w walce wracają do puli i kolejne wybuchy biorą je stamtąd
KOSZT_DZUNGLI = {
    "pocisk:pylek": (5, 4, 1),
    "pocisk:jad": (8, 4, 1),
    "wybuch:pylek": (11, 10, 1),
    "wybuch:jad": (16, 15, 1),
    "wybuch:ukaszenie": (10, 10, 0),
    "wybuch:liscie": (11, 11, 0),
    "wybuch:kokos": (13, 13, 0),
    "wybuch:kamuflaz": (13, 13, 0),
    "wybuch:ruiny": (14, 14, 0),
    "ukaszenie:kly": (4, 4, 0),
    "pazury:krzyz": (6, 6, 0),
    "wyglad:sen": (11, 10, 1),
    "wyglad:kamuflaz": (8, 8, 0),
    "wyglad:ruiny": (10, 10, 0),
}
BUDZET = {"instancji": 16, "emiterow": 1}
# dawne efekty (bohaterowie, las, Bagno): liczba instancji zmierzona tym samym testem na źródle sprzed efektów Dżungli
# (18.11.2026) — pilnuje, że wspólne funkcje (pazury, wybuch, pocisk, wyglad) tworzą dla nich to samo co dotąd
KOSZT_DAWNY = {
    "pocisk:iskra": 6, "pocisk:strzala": 9, "pocisk:kula_ognia": 7, "pocisk:lod": 6, "pocisk:kwas": 5, "pazury:zwykle": 3,
    "fala": 2, "chmura": 8, "korzenie": 15, "kaluza": 8, "parada": 6, "wskrzeszenie": 6, "wybuch:iskra": 8,
    "wybuch:ogien": 16, "wybuch:lod": 13, "wybuch:kwas": 24, "wybuch:trucizna": 7, "wybuch:zarodniki": 11,
    "wybuch:kamien": 13, "wybuch:zloto": 13, "wybuch:bariera": 11, "wybuch:blask": 1, "wybuch:cios": 8,
    "wybuch:krytyk": 17, "wybuch:blok": 9, "wybuch:tarcza": 1, "wyglad:babelki": 2, "wyglad:ogien": 2,
    "wyglad:krople": 2, "wyglad:gwiazdki": 7, "wyglad:lod": 8, "wyglad:pnacza": 7, "wyglad:odlamki": 4,
    "wyglad:kamienie": 8, "wyglad:banka": 2, "wyglad:blask": 4,
}


class Atrapa:
    """Wektor, układ, kolor, wyliczenie… — pochłania każde działanie, pole i wywołanie."""

    def __call__(self, *a):
        return self


ATR = Atrapa()


def czytaj(sciezka):
    with open(sciezka, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def bez_rzutowan(tekst):
    """Usuwa rzutowania `:: typ` (jak w test_odtwarzacza.py)."""
    wynik, i, n = [], 0, len(tekst)
    while i < n:
        if tekst.startswith("::", i):
            j = i + 2
            while j < n and tekst[j] in " \t":
                j += 1
            glebokosc = 0
            while j < n:
                c = tekst[j]
                if c in "({[":
                    glebokosc += 1
                elif c in ")}]":
                    if glebokosc == 0:
                        break
                    glebokosc -= 1
                elif glebokosc == 0 and not (c.isalnum() or c in "_.?<>"):
                    if c == "-" and tekst.startswith("->", j):
                        j += 2
                        continue
                    break
                j += 1
            i = j
            continue
        wynik.append(tekst[i])
        i += 1
    return "".join(wynik)


class Swiat:
    """Interpreter z atrapami Roblox + rejestr wszystkich utworzonych instancji."""

    def __init__(self):
        self.inst = []
        self.ostrzezenia = []
        self.meta = {}
        self._arytm, self._indeksuj = LM._arytm, LM._indeksuj
        LM._arytm, LM._indeksuj = self.arytm, self.indeksuj
        I = self.I = LM.Interpreter()
        g = I.globalne.z
        gra, rs = LM.Tabela(), LM.Tabela()
        rs.set("IsStudio", lambda _s: True)
        gra.set("GetService", lambda _s, _n: rs)
        g["game"] = gra
        for nazwa in ("Vector3", "Vector2", "CFrame", "Color3", "ColorSequence", "NumberSequence", "NumberSequenceKeypoint",
                      "NumberRange", "Enum", "workspace"):
            g[nazwa] = ATR
        inst = LM.Tabela()
        inst.set("new", self.nowa)
        g["Instance"] = inst
        los = LM.Tabela()
        los.set("NextNumber", lambda _s, a, b: (a + b) / 2)
        los.set("NextInteger", lambda _s, a, b: float(a))
        rnd = LM.Tabela()
        rnd.set("new", lambda *a: los)
        g["Random"] = rnd
        zadanie = LM.Tabela()
        zadanie.set("spawn", lambda f, *a: I.wywolaj(f, list(a)) and None)
        g["task"] = zadanie
        g["warn"] = lambda *a: self.ostrzezenia.append(" ".join(str(x) for x in a))
        g["setmetatable"] = self.ustaw_meta
        m = g["math"]
        import math
        m.set("clamp", lambda x, lo, hi: min(max(x, lo), hi))
        m.set("sin", lambda x: math.sin(x))
        m.set("cos", lambda x: math.cos(x))
        m.set("exp", lambda x: math.exp(x))
        m.set("rad", lambda x: math.radians(x))
        m.set("pi", math.pi)
        t = g["table"]
        t.set("remove", self.usun_z_tabeli)
        t.set("clear", lambda tab: tab.d.clear())
        t.set("sort", self.sortuj)
        I.laduj("Efekty3D", bez_rzutowan(czytaj(ZRODLO)))
        self.E = I.wymagaj("Efekty3D")
        self.folder = self.nowa("Folder")
        self.fx = I.wywolaj(self.E.get("nowe"), [self.folder, LM.Tabela()])[0]

    def zamknij(self):
        LM._arytm, LM._indeksuj = self._arytm, self._indeksuj

    # -- podmiany w interpreterze
    def arytm(self, op, a, b):
        if isinstance(a, Atrapa) or isinstance(b, Atrapa):
            return ATR
        return self._arytm(op, a, b)

    def indeksuj(self, obj, k):
        if isinstance(obj, Atrapa):
            return 1.0 if k in LICZBY else ATR
        if isinstance(obj, LM.Tabela):
            v = obj.get(k)
            if v is None and id(obj) in self.meta:
                idx = self.meta[id(obj)][1].get("__index")
                if idx is not None:
                    return self.indeksuj(idx, k)
            return v
        return self._indeksuj(obj, k)

    def ustaw_meta(self, tab, mt):
        self.meta[id(tab)] = (tab, mt)
        return tab

    @staticmethod
    def usun_z_tabeli(tab, poz=None):
        n = int(tab.dlugosc())
        if n == 0:
            return None
        i = n if poz is None else int(poz)
        v = tab.d.get(float(i))
        for j in range(i, n):
            tab.d[float(j)] = tab.d[float(j + 1)]
        del tab.d[float(n)]
        return v

    @staticmethod
    def sortuj(tab, _cmp=None):
        n = int(tab.dlugosc())
        el = sorted(tab.d[float(i)] for i in range(1, n + 1))
        for i, v in enumerate(el):
            tab.d[float(i + 1)] = v

    # -- instancje
    def nowa(self, klasa):
        t = LM.Tabela()
        t.set("ClassName", klasa)
        t.set("Destroy", self.zniszcz)
        t.set("GetChildren", self.dzieci)
        t.set("IsA", lambda s, k: s.get("ClassName") == k or (k == "BasePart" and s.get("ClassName") in CZESCI)
              or (k == "Light" and s.get("ClassName").endswith("Light")))
        t.set("Emit", lambda _s, _n: None)
        t.set("FindFirstChild", lambda *_a: None)
        self.inst.append(t)
        return t

    def zniszcz(self, t):
        if t.get("Zniszczona"):
            return
        t.set("Zniszczona", True)
        for d in self.inst:
            if d.get("Parent") is t:
                self.zniszcz(d)

    def dzieci(self, t):
        lista = LM.Tabela()
        for d in self.inst:
            if d.get("Parent") is t and not d.get("Zniszczona"):
                lista.set(float(lista.dlugosc() + 1), d)
        return lista

    # -- wywołania
    def wolaj(self, nazwa, *argi):
        return self.I.wywolaj(self.indeksuj(self.fx, nazwa), [self.fx] + list(argi))

    def tab(self, **pola):
        t = LM.Tabela()
        for k, v in pola.items():
            t.set(k, v)
        return t

    def aktor(self, wysokosc=5.7):
        return self.tab(wpis=self.tab(wysokosc=wysokosc, szerokosc=2.4, glebokosc=1.6), cfZiemi=lambda _s: ATR,
                        punkt=lambda _s, _n: ATR, model=self.tab(FindFirstChild=lambda *_a: None))

    def zywe(self, od=0):
        """Instancje utworzone od miejsca `od` w rejestrze, które jeszcze istnieją i nie leżą w puli iskier."""
        pula = self.indeksuj(self.fx, "wolne")
        w_puli = {id(v) for v in pula.d.values()}
        return [t for t in self.inst[od:] if not t.get("Zniszczona") and id(t) not in w_puli and t is not self.folder]

    def kroki(self, d, limit=4000):
        """Krok czasu sceny d aż skończą się wszystkie efekty chwilowe; zwraca liczbę kroków."""
        for i in range(limit):
            if self.indeksuj(self.fx, "aktywne").dlugosc() == 0:
                return i
            self.wolaj("krok", d)
        raise AssertionError("efekt nie kończy się w %d krokach" % limit)

    def licznik(self):
        return LM.z_luau(self.wolaj("licznik")[0], pusta_jako_lista=True)


# efekty chwilowe: nazwa do tabeli → jak je wywołać (s = Swiat)
def _pocisk(nazwa, **opcje):
    return lambda s: s.wolaj("pocisk", nazwa, ATR, ATR, 0.5, s.tab(przyczep=lambda: ATR, **opcje))


def _wybuch(nazwa):
    return lambda s: s.wolaj("wybuch", nazwa, ATR, 1.2)


CHWILOWE_DZUNGLI = {
    "pocisk:pylek": _pocisk("pylek", grot=0.6),
    "pocisk:jad": _pocisk("jad", grot=0.5),
    "wybuch:pylek": _wybuch("pylek"),
    "wybuch:jad": _wybuch("jad"),
    "wybuch:ukaszenie": _wybuch("ukaszenie"),
    "wybuch:liscie": _wybuch("liscie"),
    "wybuch:kokos": _wybuch("kokos"),
    "wybuch:kamuflaz": _wybuch("kamuflaz"),
    "wybuch:ruiny": _wybuch("ruiny"),
    "ukaszenie:kly": lambda s: s.wolaj("ukaszenie", ATR, ATR, 2.0),
    "pazury:krzyz": lambda s: s.wolaj("pazury", ATR, ATR, 2.0, True),
}
CHWILOWE_DAWNE = {
    "pocisk:iskra": _pocisk("iskra", grot=0.35),
    "pocisk:strzala": _pocisk("strzala", grot=2.1, zostaw=0.75),
    "pocisk:kula_ognia": _pocisk("kula_ognia", grot=0.35),
    "pocisk:lod": _pocisk("lod", grot=0.85),
    "pocisk:kwas": _pocisk("kwas", grot=0.35),
    "pocisk:pylek (unik)": _pocisk("pylek", grot=0.6, chybiony=True),
    "pocisk:jad (unik)": _pocisk("jad", grot=0.5, chybiony=True),
    "pazury:zwykle": lambda s: s.wolaj("pazury", ATR, ATR, 2.0),
    "fala": lambda s: s.wolaj("fala", ATR, ATR, 4.0),
    "pyl": lambda s: s.wolaj("pyl", ATR, _lista(ATR, ATR), 20.0, 1.0, ATR, 0.4),
    "chmura": lambda s: s.wolaj("chmura", ATR, ATR, 0.5, ATR),
    "korzenie": lambda s: s.wolaj("korzenie", ATR, 2.0, ATR, 0.35, 1.0, 4.0),
    "kaluza": lambda s: s.wolaj("kaluza", ATR, 2.0, ATR, 1.0),
    "parada": lambda s: s.wolaj("parada", ATR, ATR, ATR, 1.0),
    "wskrzeszenie": lambda s: s.wolaj("wskrzeszenie", ATR, 2.4, 5.7, ATR, 1.5),
}
WYGLADY_DZUNGLI = ("sen", "kamuflaz", "ruiny")
WYGLADY_DAWNE = ("babelki", "ogien", "krople", "gwiazdki", "lod", "pnacza", "odlamki", "kamienie", "banka", "blask")
WYBUCHY_DAWNE = ("iskra", "ogien", "lod", "kwas", "trucizna", "zarodniki", "kamien", "zloto", "bariera", "blask", "cios",
                 "krytyk", "blok", "tarcza")
TEMPA = (1, 2, 4)


def _lista(*el):
    t = LM.Tabela()
    for i, v in enumerate(el):
        t.set(float(i + 1), v)
    return t


def koszt_efektu(nazwa):
    """(Counter klas instancji, licznik kroków ×1) dla jednego efektu w świeżym świecie (pusta pula iskier)."""
    s = Swiat()
    try:
        od = len(s.inst)
        if nazwa.startswith("wyglad:"):
            s.wolaj("wyglad", nazwa.split(":")[1], s.aktor())
            return Counter(t.get("ClassName") for t in s.inst[od:]), 0
        f = CHWILOWE_DZUNGLI.get(nazwa) or CHWILOWE_DAWNE.get(nazwa) or _wybuch(nazwa.split(":")[1])
        f(s)
        klasy = Counter(t.get("ClassName") for t in s.inst[od:])
        return klasy, s.kroki(1 / 60)
    finally:
        s.zamknij()


class TestEfektow(unittest.TestCase):
    def setUp(self):
        self.s = Swiat()

    def tearDown(self):
        self.s.zamknij()

    def test_1_modul_i_rejestry(self):
        for rejestr, nazwy in (("POCISKI", ("iskra", "strzala", "kula_ognia", "lod", "kwas", "pylek", "jad")),
                               ("WYBUCHY", WYBUCHY_DAWNE + ("pylek", "jad", "ukaszenie", "liscie", "kokos", "kamuflaz", "ruiny")),
                               ("WYGLADY", WYGLADY_DAWNE + WYGLADY_DZUNGLI)):
            self.assertEqual(set(self.s.E.get(rejestr).d), set(nazwy), rejestr)

    def test_2_efekty_chwilowe_przy_kazdym_tempie(self):
        """Każdy efekt chwilowy: tworzy się, kończy się sam przy kroku ×1 / ×2 / ×4 i nic po nim nie zostaje."""
        wszystkie = dict(CHWILOWE_DZUNGLI)
        wszystkie.update(CHWILOWE_DAWNE)
        wszystkie.update({"wybuch:" + n: _wybuch(n) for n in WYBUCHY_DAWNE})
        for nazwa, f in wszystkie.items():
            for tempo in TEMPA:
                with self.subTest(efekt=nazwa, tempo=tempo):
                    od = len(self.s.inst)
                    f(self.s)
                    self.assertGreater(len(self.s.inst) + self.s.licznik()["pula"], od, "efekt niczego nie utworzył")
                    kroki = self.s.kroki(tempo / 60)
                    self.assertGreater(kroki, 0)
                    self.assertLess(kroki * tempo / 60, 6.0, "efekt trwa ponad 6 s czasu sceny")
                    self.assertEqual(self.s.ostrzezenia, [], "błąd wykonania w kroku efektu")
                    zostalo = self.s.zywe(od)
                    self.assertEqual([t.get("Name") for t in zostalo], [], "po końcu efektu zostały instancje")

    def test_3_ozdoby_statusow(self):
        """Każda ozdoba statusu: tworzy się, idzie krokami (także z pulsem) i znika po zniszcz()."""
        for nazwa in WYGLADY_DAWNE + WYGLADY_DZUNGLI:
            for wysokosc in (1.8, 5.7, 17.0):   # mały potwór, bohater, Wąż Stu Lian
                with self.subTest(ozdoba=nazwa, wysokosc=wysokosc):
                    od = len(self.s.inst)
                    o = self.s.wolaj("wyglad", nazwa, self.s.aktor(wysokosc))[0]
                    for i in range(90):
                        if i == 30:
                            self.s.I.wywolaj(o.get("puls"), [o])
                        self.s.I.wywolaj(o.get("krok"), [o, TEMPA[i % 3] / 60])   # wprost: fx:krok połyka błędy ozdób
                    self.assertGreater(len(self.s.zywe(od)), 0)
                    self.s.I.wywolaj(o.get("zniszcz"), [o])
                    self.assertEqual([t.get("Name") for t in self.s.zywe(od)], [])
        self.s.wolaj("wyczysc")

    def test_4_koszt_efektow_dzungli(self):
        """Licznik: dokładne liczby instancji własnych efektów Dżungli, budżet, bez świateł."""
        for nazwa, (razem, czesci, emitery) in KOSZT_DZUNGLI.items():
            with self.subTest(efekt=nazwa):
                klasy, _ = koszt_efektu(nazwa)
                self.assertEqual(sum(klasy.values()), razem, dict(klasy))
                self.assertEqual(sum(n for k, n in klasy.items() if k in CZESCI), czesci, dict(klasy))
                self.assertEqual(klasy.get("ParticleEmitter", 0), emitery, dict(klasy))
                self.assertEqual(sum(n for k, n in klasy.items() if k.endswith("Light") or k == "Fire"), 0, dict(klasy))
                self.assertLessEqual(razem, BUDZET["instancji"])
                self.assertLessEqual(emitery, BUDZET["emiterow"])
        # licznik w samym module (atrybut OstatniKosztEfektow w grze) liczy to samo
        s = self.s
        for nazwa, f in CHWILOWE_DZUNGLI.items():
            f(s)
            s.kroki(1 / 60)
            s.wolaj("wyczysc")                      # pusta pula przed następnym efektem
        for nazwa in WYGLADY_DZUNGLI:
            s.wolaj("wyglad", nazwa, s.aktor())
        koszt = s.licznik()["koszt"]
        for nazwa, (razem, _, _) in KOSZT_DZUNGLI.items():
            # wybuch z obłokiem drobin: obłok liczy się w wybuchu, a iskry z puli tylko nowe
            self.assertEqual(koszt[nazwa], razem, nazwa)
        opis = s.wolaj("opisKosztu")[0]
        self.assertIn("pocisk:pylek=5", opis)
        self.assertIn("wyglad:sen=11", opis)

    def test_4b_dawne_efekty_bez_zmian(self):
        """Bohaterowie, las i Bagno: każdy dawny efekt tworzy tyle samo instancji co przed efektami Dżungli."""
        for nazwa, razem in KOSZT_DAWNY.items():
            with self.subTest(efekt=nazwa):
                klasy, _ = koszt_efektu(nazwa)
                self.assertEqual(sum(klasy.values()), razem, dict(klasy))

    def test_5_pominiecie_walki_nie_zostawia_niczego(self):
        """Pominięcie: fx:wyczysc() w połowie lotów, z ozdobami na obu stronach i iskrami w puli — nie zostaje nic."""
        s = self.s
        for tempo in TEMPA:
            with self.subTest(tempo=tempo):
                od = len(s.inst)
                for f in list(CHWILOWE_DZUNGLI.values()) + list(CHWILOWE_DAWNE.values()):
                    f(s)
                for nazwa in WYGLADY_DZUNGLI + WYGLADY_DAWNE:
                    s.wolaj("wyglad", nazwa, s.aktor())
                for _ in range(8):                     # 8 klatek: pociski w locie, część wybuchów już wróciła do puli
                    s.wolaj("krok", tempo / 60)
                self.assertEqual(s.ostrzezenia, [])
                lic = s.licznik()
                self.assertGreater(lic["aktywne"], 0)
                self.assertEqual(lic["ozdoby"], len(WYGLADY_DZUNGLI + WYGLADY_DAWNE))
                s.wolaj("wyczysc")
                lic = s.licznik()
                self.assertEqual((lic["aktywne"], lic["ozdoby"], lic["pula"]), (0, 0, 0))
                zostalo = [t for t in s.inst[od:] if not t.get("Zniszczona")]
                self.assertEqual([t.get("Name") for t in zostalo], [], "po wyczysc() zostały instancje")

    def test_6_pula_iskier_nie_rosnie(self):
        """Dziesięć wybuchów pod rząd bierze iskry z puli: instancji przybywa tylko przy pierwszym."""
        s = self.s
        _wybuch("kokos")(s)
        s.kroki(1 / 60)
        po_pierwszym = len(s.inst)
        for _ in range(10):
            _wybuch("kokos")(s)
            s.kroki(1 / 60)
        self.assertEqual(len(s.inst) - po_pierwszym, 10, "kolejny wybuch tworzy tylko swój rozbłysk (1 część)")
        self.assertEqual(s.licznik()["pula"], 12)


def tabela():
    print("| Efekt | Instancji | w tym części | emiterów | smug i zaczepów | trwa (s sceny) |")
    print("|---|---:|---:|---:|---:|---:|")
    for nazwa in KOSZT_DZUNGLI:
        klasy, kroki = koszt_efektu(nazwa)
        czesci = sum(n for k, n in klasy.items() if k in CZESCI)
        print("| `%s` | %d | %d | %d | %d | %s |" % (
            nazwa, sum(klasy.values()), czesci, klasy.get("ParticleEmitter", 0),
            klasy.get("Trail", 0) + klasy.get("Attachment", 0), ("%.2f" % (kroki / 60)) if kroki else "do końca statusu"))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--tabela" in sys.argv:
        tabela()
    else:
        unittest.main(verbosity=1)
