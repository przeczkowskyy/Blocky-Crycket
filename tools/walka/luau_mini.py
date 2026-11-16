# -*- coding: utf-8 -*-
"""Maly interpreter PODZBIORU Luau w Pythonie — tylko po to, zeby bez Roblox Studio uruchomic moduly silnika walki
(src/server/Walka/*.luau, src/shared/Walka/Dziennik.luau) i porownac ich dzienniki z portem w Pythonie.

    python -B tools/walka/zgodnosc_studio.py --offline     # te same wzorce co w Studio, ale tym interpreterem

To NIE jest pelny Luau i NIE zastepuje sprawdzenia w Studio: obsluguje skladnie i biblioteke, ktorej uzywaja moduly
silnika (local, function, if/elseif/else, wyrazenie if, while, repeat, for liczbowy i uogolniona iteracja po tabelach,
+= i podobne, tabele, domkniecia, wiele wartosci zwracanych, adnotacje typow — pomijane, string/math/table w zakresie
uzywanym przez silnik, error, pcall, next, type, tostring). Liczby sa liczbami double (float w Pythonie), dzialania
w tej samej kolejnosci co w zrodle, wiec wyniki arytmetyki sa takie jak w Luau. Kolejnosc iteracji po czesci
slownikowej tabeli jest tu kolejnoscia wstawiania (w Luau jest nieokreslona) — silnik iteruje po slownikach tylko
w walidacji, gdzie kolejnosc nie zmienia wyniku (pilnuje tego test w test_walki.py).
Nieznana konstrukcja = wyjatek BladSkladni (lepiej glosno niz po cichu inaczej niz Luau).
"""
import math
import re

__all__ = ["BladSkladni", "BladLuau", "Tabela", "Interpreter"]


class BladSkladni(Exception):
    pass


class BladLuau(Exception):
    """Blad zgloszony w kodzie Luau (error(...)) albo blad wykonania (np. indeksowanie nil)."""

    def __init__(self, wartosc):
        super().__init__(wartosc)
        self.wartosc = wartosc


# ------------------------------------------------------------------------------------------------ wartosci
class Tabela:
    __slots__ = ("d",)

    def __init__(self):
        self.d = {}

    def get(self, k):
        return self.d.get(_klucz(k))

    def set(self, k, v):
        k = _klucz(k)
        if k is None:
            raise BladLuau("table index is nil")
        if v is None:
            self.d.pop(k, None)
        else:
            self.d[k] = v

    def dlugosc(self):
        n = 0
        while (float(n + 1)) in self.d:
            n += 1
        return float(n)

    def klucze(self):
        n = int(self.dlugosc())
        tablicowe = [float(i) for i in range(1, n + 1)]
        reszta = [k for k in self.d if not (isinstance(k, float) and k == math.floor(k) and 1 <= k <= n)]
        return tablicowe + reszta


def _klucz(k):
    if isinstance(k, bool):
        return k
    if isinstance(k, int):
        return float(k)
    return k


class Funkcja:
    __slots__ = ("parametry", "wariadyczna", "cialo", "zasieg", "nazwa")

    def __init__(self, parametry, wariadyczna, cialo, zasieg, nazwa):
        self.parametry, self.wariadyczna, self.cialo, self.zasieg, self.nazwa = parametry, wariadyczna, cialo, zasieg, nazwa


def typ(v):
    if v is None:
        return "nil"
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, float):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, Tabela):
        return "table"
    if isinstance(v, Funkcja) or callable(v):
        return "function"
    raise BladLuau("nieznany typ wartosci %r" % (v,))


def prawda(v):
    return v is not None and v is not False


def napis_liczby(x):
    if x != x:
        return "nan"
    if x in (math.inf, -math.inf):
        return "inf" if x > 0 else "-inf"
    if x == math.floor(x) and abs(x) < 1e15:
        return str(int(x))
    return "%.14g" % x


def tostring(v):
    t = typ(v)
    if t == "nil":
        return "nil"
    if t == "boolean":
        return "true" if v else "false"
    if t == "number":
        return napis_liczby(v)
    if t == "string":
        return v
    return "%s: 0x%08x" % (t, id(v) & 0xFFFFFFFF)


def rowne(a, b):
    ta, tb = typ(a), typ(b)
    if ta != tb:
        return False
    if ta in ("table", "function"):
        return a is b
    return a == b


# ------------------------------------------------------------------------------------------------ lekser
SLOWA = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in", "local", "nil",
         "not", "or", "repeat", "return", "then", "true", "until", "while", "continue"}
OPERATORY = ["...", "..=", "//=", "==", "~=", "<=", ">=", "+=", "-=", "*=", "/=", "%=", "^=", "->", "::", "//", "..",
             "+", "-", "*", "/", "%", "^", "#", "<", ">", "=", "(", ")", "{", "}", "[", "]", ";", ":", ",", ".",
             "?", "|", "&"]


def leksuj(tekst):
    tok = []  # (rodzaj, wartosc, linia)
    i, n, linia = 0, len(tekst), 1
    while i < n:
        c = tekst[i]
        if c == "\n":
            linia += 1
            i += 1
            continue
        if c in " \t\r":
            i += 1
            continue
        if tekst.startswith("--", i):
            m = re.match(r"--\[(=*)\[", tekst[i:])
            if m:
                koniec = tekst.find("]" + m.group(1) + "]", i)
                if koniec < 0:
                    raise BladSkladni("niedomkniety komentarz w linii %d" % linia)
                linia += tekst.count("\n", i, koniec)
                i = koniec + len(m.group(1)) + 2
            else:
                while i < n and tekst[i] != "\n":
                    i += 1
            continue
        m = re.match(r"\[(=*)\[", tekst[i:])
        if m:
            start = i + len(m.group(0))
            koniec = tekst.find("]" + m.group(1) + "]", start)
            if koniec < 0:
                raise BladSkladni("niedomkniety dlugi napis w linii %d" % linia)
            s = tekst[start:koniec]
            if s.startswith("\n"):
                s = s[1:]
            tok.append(("napis", s, linia))
            linia += tekst.count("\n", i, koniec)
            i = koniec + len(m.group(1)) + 2
            continue
        if c in "\"'":
            j = i + 1
            czesci = []
            while True:
                if j >= n or tekst[j] == "\n":
                    raise BladSkladni("niedomkniety napis w linii %d" % linia)
                ch = tekst[j]
                if ch == c:
                    break
                if ch == "\\":
                    e = tekst[j + 1]
                    if e == "n":
                        czesci.append("\n")
                        j += 2
                    elif e == "t":
                        czesci.append("\t")
                        j += 2
                    elif e in "\\\"'":
                        czesci.append(e)
                        j += 2
                    elif e.isdigit():
                        m2 = re.match(r"\d{1,3}", tekst[j + 1:])
                        czesci.append(chr(int(m2.group(0))))
                        j += 1 + len(m2.group(0))
                    else:
                        raise BladSkladni("nieobslugiwana sekwencja \\%s w linii %d" % (e, linia))
                    continue
                czesci.append(ch)
                j += 1
            tok.append(("napis", "".join(czesci), linia))
            i = j + 1
            continue
        if c == "`":
            raise BladSkladni("napisy z odwrotnym apostrofem nie sa obslugiwane (linia %d)" % linia)
        m = re.match(r"0[xX][0-9a-fA-F_]+|(\d[\d_]*\.?[\d_]*|\.\d[\d_]*)([eE][-+]?\d+)?", tekst[i:])
        if m and m.group(0) and (c.isdigit() or (c == "." and i + 1 < n and tekst[i + 1].isdigit())):
            s = m.group(0).replace("_", "")
            v = float(int(s, 16)) if s[:2].lower() == "0x" else float(s)
            tok.append(("liczba", v, linia))
            i += len(m.group(0))
            continue
        m = re.match(r"[A-Za-z_][A-Za-z0-9_]*", tekst[i:])
        if m:
            s = m.group(0)
            tok.append(("slowo" if s in SLOWA else "nazwa", s, linia))
            i += len(s)
            continue
        for op in OPERATORY:
            if tekst.startswith(op, i):
                tok.append(("op", op, linia))
                i += len(op)
                break
        else:
            raise BladSkladni("nieznany znak %r w linii %d" % (c, linia))
    tok.append(("koniec", None, linia))
    return tok


# ------------------------------------------------------------------------------------------------ parser -> domkniecia
PRIORYTETY = {"or": (1, 1), "and": (2, 2), "<": (3, 3), ">": (3, 3), "<=": (3, 3), ">=": (3, 3), "~=": (3, 3),
              "==": (3, 3), "..": (5, 4), "+": (6, 6), "-": (6, 6), "*": (7, 7), "/": (7, 7), "//": (7, 7),
              "%": (7, 7), "^": (10, 9)}
PRIORYTET_UNARNY = 8


class Zasieg:
    __slots__ = ("z", "rodzic")

    def __init__(self, rodzic):
        self.z = {}
        self.rodzic = rodzic

    def znajdz(self, nazwa):
        s = self
        while s is not None:
            if nazwa in s.z:
                return s
            s = s.rodzic
        return None


class _Przerwij(Exception):
    pass


class _Kontynuuj(Exception):
    pass


class _Zwroc(Exception):
    def __init__(self, wartosci):
        self.wartosci = wartosci


def _arytm(op, a, b):
    if not isinstance(a, float) or not isinstance(b, float):
        raise BladLuau("attempt to perform arithmetic (%s) on %s and %s" % (op, typ(a), typ(b)))
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        if b == 0:
            if a == 0 or a != a:
                return math.nan
            return math.inf if (a > 0) == (math.copysign(1, b) > 0) else -math.inf
        return a / b
    if op == "%":
        if b == 0:
            return math.nan
        return a - math.floor(a / b) * b
    if op == "//":
        return float(math.floor(a / b))
    if op == "^":
        return math.pow(a, b)
    raise BladLuau("nieznany operator " + op)


def _porownaj(op, a, b):
    if isinstance(a, float) and isinstance(b, float) or isinstance(a, str) and isinstance(b, str):
        if op == "<":
            return a < b
        if op == "<=":
            return a <= b
        if op == ">":
            return a > b
        return a >= b
    raise BladLuau("attempt to compare %s and %s" % (typ(a), typ(b)))


def _indeksuj(obj, k):
    if isinstance(obj, Tabela):
        return obj.get(k)
    if isinstance(obj, str):
        raise BladLuau("indeksowanie napisu nie jest obslugiwane")
    raise BladLuau("attempt to index %s with %s" % (typ(obj), tostring(k) if isinstance(k, (str, float)) else typ(k)))


class Parser:
    def __init__(self, tekst, nazwa, interp):
        self.t = leksuj(tekst)
        self.i = 0
        self.nazwa = nazwa
        self.interp = interp

    # -- pomocnicze
    def pk(self, przes=0):
        return self.t[self.i + przes]

    def jest(self, wartosc, rodzaj=None):
        r, w, _ = self.t[self.i]
        return w == wartosc and (rodzaj is None or r == rodzaj) and r in ("op", "slowo")

    def bierz(self):
        x = self.t[self.i]
        self.i += 1
        return x

    def oczekuj(self, wartosc):
        r, w, linia = self.bierz()
        if w != wartosc or r not in ("op", "slowo"):
            raise BladSkladni("%s:%d: oczekiwano %r, jest %r" % (self.nazwa, linia, wartosc, w))

    def nazwa_t(self):
        r, w, linia = self.bierz()
        if r != "nazwa":
            raise BladSkladni("%s:%d: oczekiwano nazwy, jest %r" % (self.nazwa, linia, w))
        return w

    def blad(self, tekst):
        raise BladSkladni("%s:%d: %s" % (self.nazwa, self.pk()[2], tekst))

    # -- typy (pomijane)
    def typ_(self):
        r, w, _ = self.pk()
        if w == "(" and r == "op":
            self.nawiasy("(", ")")
            if self.jest("->"):
                self.bierz()
                self.typ_()
        elif w == "{" and r == "op":
            self.nawiasy("{", "}")
        elif r == "nazwa" or (r == "slowo" and w in ("nil", "true", "false")) or r == "napis":
            self.bierz()
            while self.jest("."):
                self.bierz()
                self.nazwa_t()
            if self.jest("<"):
                self.nawiasy("<", ">")
            if self.jest("("):  # typeof(...)
                self.nawiasy("(", ")")
        else:
            self.blad("nieznany typ %r" % w)
        while self.jest("?"):
            self.bierz()
        if self.jest("|") or self.jest("&"):
            self.bierz()
            self.typ_()

    def nawiasy(self, otw, zam):
        glebokosc = 0
        while True:
            r, w, _ = self.bierz()
            if r == "koniec":
                self.blad("niedomkniety typ")
            if r == "op" and w == otw:
                glebokosc += 1
            elif r == "op" and w == zam:
                glebokosc -= 1
                if glebokosc == 0:
                    return

    # -- bloki
    def program(self):
        cialo = self.blok(("koniec",))
        if self.pk()[0] != "koniec":
            self.blad("nadmiarowy kod")
        return cialo

    def blok(self, zakonczenia):
        instr = []
        while True:
            r, w, _ = self.pk()
            if r == "koniec" or (r == "slowo" and w in zakonczenia):
                break
            if self.jest(";"):
                self.bierz()
                continue
            if r == "slowo" and w == "return":
                self.bierz()
                wyr = []
                r2, w2, _ = self.pk()
                if not (r2 == "koniec" or (r2 == "slowo" and w2 in ("end", "else", "elseif", "until")) or w2 == ";"):
                    wyr = self.lista_wyrazen()
                if self.jest(";"):
                    self.bierz()
                instr.append(self._zwroc(wyr))
                break
            instr.append(self.instrukcja())
        return self._wykonaj_blok(instr)

    @staticmethod
    def _wykonaj_blok(instr):
        def blok(z):
            for f in instr:
                f(z)
        return blok

    @staticmethod
    def _zwroc(wyr):
        def f(z):
            raise _Zwroc(Parser.wartosci(wyr, z))
        return f

    @staticmethod
    def wartosci(wyr, z):
        """Lista wyrazen -> lista wartosci (ostatnie wyrazenie rozwija wiele wartosci, jesli to wywolanie)."""
        wynik = []
        for i, (f, wiele) in enumerate(wyr):
            if i == len(wyr) - 1 and wiele is not None:
                wynik.extend(wiele(z))
            else:
                wynik.append(f(z))
        return wynik

    def instrukcja(self):
        r, w, linia = self.pk()
        if r == "slowo":
            if w == "local":
                self.bierz()
                if self.jest("function"):
                    self.bierz()
                    nazwa = self.nazwa_t()
                    cialo_f = self.funkcja(nazwa)

                    def f(z):
                        z.z[nazwa] = None
                        z.z[nazwa] = cialo_f(z)
                    return f
                nazwy = [self.nazwa_t()]
                if self.jest(":"):
                    self.bierz()
                    self.typ_()
                while self.jest(","):
                    self.bierz()
                    nazwy.append(self.nazwa_t())
                    if self.jest(":"):
                        self.bierz()
                        self.typ_()
                wyr = []
                if self.jest("="):
                    self.bierz()
                    wyr = self.lista_wyrazen()

                def f(z):
                    v = Parser.wartosci(wyr, z)
                    for i, nz in enumerate(nazwy):
                        z.z[nz] = v[i] if i < len(v) else None
                return f
            if w == "function":
                self.bierz()
                sciezka = [self.nazwa_t()]
                metoda = False
                while self.jest(".") or self.jest(":"):
                    metoda = self.bierz()[1] == ":"
                    sciezka.append(self.nazwa_t())
                    if metoda:
                        break
                cialo_f = self.funkcja(".".join(sciezka), metoda)
                if len(sciezka) == 1:
                    nazwa = sciezka[0]

                    def f(z):
                        self.interp.przypisz(z, nazwa, cialo_f(z))
                    return f

                def f(z):
                    obj = self.interp.zmienna(z, sciezka[0])
                    for k in sciezka[1:-1]:
                        obj = _indeksuj(obj, k)
                    if not isinstance(obj, Tabela):
                        raise BladLuau("function: %s nie jest tabela" % sciezka[0])
                    obj.set(sciezka[-1], cialo_f(z))
                return f
            if w == "if":
                return self.instr_if()
            if w == "while":
                self.bierz()
                war = self.wyrazenie()
                self.oczekuj("do")
                cialo = self.blok(("end",))
                self.oczekuj("end")

                def f(z):
                    while prawda(war(z)):
                        try:
                            cialo(Zasieg(z))
                        except _Przerwij:
                            break
                        except _Kontynuuj:
                            continue
                return f
            if w == "repeat":
                self.bierz()
                cialo = self.blok(("until",))
                self.oczekuj("until")
                war = self.wyrazenie()

                def f(z):
                    while True:
                        zz = Zasieg(z)
                        try:
                            cialo(zz)
                        except _Przerwij:
                            break
                        except _Kontynuuj:
                            pass
                        if prawda(war(zz)):
                            break
                return f
            if w == "for":
                return self.instr_for()
            if w == "do":
                self.bierz()
                cialo = self.blok(("end",))
                self.oczekuj("end")
                return lambda z: cialo(Zasieg(z))
            if w == "break":
                self.bierz()

                def f(z):
                    raise _Przerwij()
                return f
            if w == "continue":
                self.bierz()

                def f(z):
                    raise _Kontynuuj()
                return f
            if w not in ("nil", "true", "false", "not", "function"):
                self.blad("nieobslugiwana instrukcja %r" % w)
        if r == "nazwa" and w in ("type", "export") and self.pk(1)[0] == "nazwa":
            self.blad("deklaracje typow nie sa obslugiwane")
        # przypisanie albo wywolanie
        cel = self.wyrazenie_przyrostkowe()
        if self.jest("=") or self.jest(","):
            cele = [cel]
            while self.jest(","):
                self.bierz()
                cele.append(self.wyrazenie_przyrostkowe())
            self.oczekuj("=")
            wyr = self.lista_wyrazen()
            przypisania = [self.cel_przypisania(c) for c in cele]

            def f(z):
                v = Parser.wartosci(wyr, z)
                for i, p in enumerate(przypisania):
                    p(z, v[i] if i < len(v) else None)
            return f
        for op in ("+=", "-=", "*=", "/=", "%=", "^=", "..=", "//="):
            if self.jest(op):
                self.bierz()
                prawa = self.wyrazenie()
                return self.przypisanie_zlozone(cel, op[:-1], prawa)
        if cel[0] != "wywolanie":
            self.blad("instrukcja nie jest wywolaniem ani przypisaniem")
        wiele = cel[2]
        return lambda z: wiele(z)

    def cel_przypisania(self, c):
        if c[0] == "nazwa":
            nazwa = c[1]
            return lambda z, v: self.interp.przypisz(z, nazwa, v)
        if c[0] == "indeks":
            obj_f, klucz_f = c[1], c[2]

            def p(z, v):
                obj = obj_f(z)
                if not isinstance(obj, Tabela):
                    raise BladLuau("attempt to index %s" % typ(obj))
                obj.set(klucz_f(z), v)
            return p
        self.blad("nie mozna przypisac do wyrazenia")

    def przypisanie_zlozone(self, cel, op, prawa):
        if cel[0] == "nazwa":
            nazwa = cel[1]

            def f(z):
                stara = self.interp.zmienna(z, nazwa)
                nowa = Parser.konkatenacja(stara, prawa(z)) if op == ".." else _arytm(op, stara, prawa(z))
                self.interp.przypisz(z, nazwa, nowa)
            return f
        if cel[0] == "indeks":
            obj_f, klucz_f = cel[1], cel[2]

            def f(z):
                obj = obj_f(z)
                k = klucz_f(z)
                stara = _indeksuj(obj, k)
                nowa = Parser.konkatenacja(stara, prawa(z)) if op == ".." else _arytm(op, stara, prawa(z))
                obj.set(k, nowa)
            return f
        self.blad("zle przypisanie zlozone")

    def instr_if(self):
        galezie = []
        self.oczekuj("if")
        war = self.wyrazenie()
        self.oczekuj("then")
        galezie.append((war, self.blok(("elseif", "else", "end"))))
        inaczej = None
        while True:
            if self.jest("elseif"):
                self.bierz()
                war = self.wyrazenie()
                self.oczekuj("then")
                galezie.append((war, self.blok(("elseif", "else", "end"))))
            elif self.jest("else"):
                self.bierz()
                inaczej = self.blok(("end",))
                self.oczekuj("end")
                break
            else:
                self.oczekuj("end")
                break

        def f(z):
            for w_, b in galezie:
                if prawda(w_(z)):
                    b(Zasieg(z))
                    return
            if inaczej is not None:
                inaczej(Zasieg(z))
        return f

    def instr_for(self):
        self.oczekuj("for")
        n1 = self.nazwa_t()
        if self.jest(":"):
            self.bierz()
            self.typ_()
        if self.jest("="):
            self.bierz()
            od = self.wyrazenie()
            self.oczekuj(",")
            do = self.wyrazenie()
            krok = None
            if self.jest(","):
                self.bierz()
                krok = self.wyrazenie()
            self.oczekuj("do")
            cialo = self.blok(("end",))
            self.oczekuj("end")

            def f(z):
                a, b = od(z), do(z)
                s = krok(z) if krok else 1.0
                if not all(isinstance(x, float) for x in (a, b, s)):
                    raise BladLuau("'for' wymaga liczb")
                i = a
                while (s > 0 and i <= b) or (s < 0 and i >= b):
                    zz = Zasieg(z)
                    zz.z[n1] = i
                    try:
                        cialo(zz)
                    except _Przerwij:
                        break
                    except _Kontynuuj:
                        pass
                    i = i + s
            return f
        nazwy = [n1]
        while self.jest(","):
            self.bierz()
            nazwy.append(self.nazwa_t())
            if self.jest(":"):
                self.bierz()
                self.typ_()
        self.oczekuj("in")
        wyr = self.lista_wyrazen()
        self.oczekuj("do")
        cialo = self.blok(("end",))
        self.oczekuj("end")

        def f(z):
            v = Parser.wartosci(wyr, z)
            pierwszy = v[0] if v else None
            if isinstance(pierwszy, Tabela):
                # uogolniona iteracja Luau: najpierw czesc tablicowa 1..n, potem reszta (tu: kolejnosc wstawiania)
                for k in pierwszy.klucze():
                    wart = pierwszy.d.get(k)
                    if wart is None:
                        continue
                    zz = Zasieg(z)
                    zz.z[nazwy[0]] = k
                    if len(nazwy) > 1:
                        zz.z[nazwy[1]] = wart
                    for nz in nazwy[2:]:
                        zz.z[nz] = None
                    try:
                        cialo(zz)
                    except _Przerwij:
                        break
                    except _Kontynuuj:
                        pass
                return
            fn = pierwszy
            stan = v[1] if len(v) > 1 else None
            ster = v[2] if len(v) > 2 else None
            while True:
                r = self.interp.wywolaj(fn, [stan, ster])
                if not r or r[0] is None:
                    break
                ster = r[0]
                zz = Zasieg(z)
                for i, nz in enumerate(nazwy):
                    zz.z[nz] = r[i] if i < len(r) else None
                try:
                    cialo(zz)
                except _Przerwij:
                    break
                except _Kontynuuj:
                    pass
        return f

    def funkcja(self, nazwa, metoda=False):
        self.oczekuj("(")
        parametry, wariadyczna = (["self"] if metoda else []), False
        if not self.jest(")"):
            while True:
                if self.jest("..."):
                    self.bierz()
                    wariadyczna = True
                    if self.jest(":"):
                        self.bierz()
                        self.typ_()
                    break
                parametry.append(self.nazwa_t())
                if self.jest(":"):
                    self.bierz()
                    self.typ_()
                if not self.jest(","):
                    break
                self.bierz()
        self.oczekuj(")")
        if self.jest(":"):
            self.bierz()
            self.typ_()
        cialo = self.blok(("end",))
        self.oczekuj("end")
        return lambda z: Funkcja(parametry, wariadyczna, cialo, z, nazwa)

    # -- wyrazenia: kazde wyrazenie to (funkcja jednej wartosci); wywolania maja tez wersje wielu wartosci
    def lista_wyrazen(self):
        wyr = [self.wyrazenie_wiele()]
        while self.jest(","):
            self.bierz()
            wyr.append(self.wyrazenie_wiele())
        return wyr

    def wyrazenie_wiele(self):
        e = self.podwyrazenie(0)
        return (e, getattr(e, "wiele", None))

    def wyrazenie(self):
        return self.podwyrazenie(0)

    @staticmethod
    def konkatenacja(a, b):
        if isinstance(a, (str, float)) and isinstance(b, (str, float)):
            return tostring(a) + tostring(b)
        raise BladLuau("attempt to concatenate %s with %s" % (typ(a), typ(b)))

    def podwyrazenie(self, limit):
        r, w, _ = self.pk()
        if (r == "slowo" and w == "not") or (r == "op" and w in ("-", "#")):
            self.bierz()
            arg = self.podwyrazenie(PRIORYTET_UNARNY)
            if w == "not":
                e = lambda z: not prawda(arg(z))
            elif w == "-":
                def e(z):
                    v = arg(z)
                    if not isinstance(v, float):
                        raise BladLuau("attempt to perform arithmetic (unm) on %s" % typ(v))
                    return -v
            else:
                def e(z):
                    v = arg(z)
                    if isinstance(v, Tabela):
                        return v.dlugosc()
                    if isinstance(v, str):
                        return float(len(v.encode("utf-8")))
                    raise BladLuau("attempt to get length of %s" % typ(v))
        else:
            e = self.wyrazenie_proste()
        while True:
            r, w, _ = self.pk()
            if r in ("op", "slowo") and w in PRIORYTETY and PRIORYTETY[w][0] > limit:
                self.bierz()
                prawa = self.podwyrazenie(PRIORYTETY[w][1])
                e = self.dwuargumentowe(w, e, prawa)
            else:
                break
        return e

    @staticmethod
    def dwuargumentowe(op, a, b):
        if op == "and":
            return lambda z: (lambda x: b(z) if prawda(x) else x)(a(z))
        if op == "or":
            return lambda z: (lambda x: x if prawda(x) else b(z))(a(z))
        if op == "==":
            return lambda z: rowne(a(z), b(z))
        if op == "~=":
            return lambda z: not rowne(a(z), b(z))
        if op in ("<", "<=", ">", ">="):
            return lambda z: _porownaj(op, a(z), b(z))
        if op == "..":
            return lambda z: Parser.konkatenacja(a(z), b(z))
        return lambda z: _arytm(op, a(z), b(z))

    def wyrazenie_proste(self):
        r, w, linia = self.pk()
        if r == "liczba":
            self.bierz()
            return lambda z: w
        if r == "napis":
            self.bierz()
            return lambda z: w
        if r == "slowo":
            if w == "nil":
                self.bierz()
                return lambda z: None
            if w == "true":
                self.bierz()
                return lambda z: True
            if w == "false":
                self.bierz()
                return lambda z: False
            if w == "function":
                self.bierz()
                f = self.funkcja("(anonimowa)")
                return f
            if w == "if":
                self.bierz()
                galezie = []
                war = self.wyrazenie()
                self.oczekuj("then")
                galezie.append((war, self.wyrazenie()))
                while self.jest("elseif"):
                    self.bierz()
                    war = self.wyrazenie()
                    self.oczekuj("then")
                    galezie.append((war, self.wyrazenie()))
                self.oczekuj("else")
                inaczej = self.wyrazenie()

                def e(z):
                    for w_, v in galezie:
                        if prawda(w_(z)):
                            return v(z)
                    return inaczej(z)
                return e
        if r == "op" and w == "{":
            return self.konstruktor()
        if r == "op" and w == "...":
            self.blad("... poza funkcja nie jest obslugiwane")
        p = self.wyrazenie_przyrostkowe()
        return p[3]

    def konstruktor(self):
        self.oczekuj("{")
        pola = []  # (rodzaj, klucz_f, wartosc_f, wiele)
        while not self.jest("}"):
            if self.jest("["):
                self.bierz()
                k = self.wyrazenie()
                self.oczekuj("]")
                self.oczekuj("=")
                pola.append(("k", k, self.wyrazenie(), None))
            elif self.pk()[0] == "nazwa" and self.pk(1)[1] == "=" and self.pk(1)[0] == "op":
                nazwa = self.bierz()[1]
                self.bierz()
                pola.append(("k", (lambda n: (lambda z: n))(nazwa), self.wyrazenie(), None))
            else:
                e, wiele = self.wyrazenie_wiele()
                pola.append(("p", None, e, wiele))
            if self.jest(",") or self.jest(";"):
                self.bierz()
            else:
                break
        self.oczekuj("}")

        def e(z):
            t = Tabela()
            n = 0
            for i, (rodz, k, v, wiele) in enumerate(pola):
                if rodz == "k":
                    t.set(k(z), v(z))
                elif i == len(pola) - 1 and wiele is not None:
                    for x in wiele(z):
                        n += 1
                        t.set(float(n), x)
                else:
                    n += 1
                    t.set(float(n), v(z))
            return t
        return e

    def wyrazenie_przyrostkowe(self):
        """-> ("nazwa", n, None, f) | ("indeks", obj_f, klucz_f, f) | ("wywolanie", None, wiele_f, f1) | ("inne", .., f)"""
        r, w, linia = self.pk()
        if r == "nazwa":
            self.bierz()
            nazwa = w
            f = lambda z: self.interp.zmienna(z, nazwa)
            wynik = ("nazwa", nazwa, None, f)
        elif r == "op" and w == "(":
            self.bierz()
            e = self.wyrazenie()
            self.oczekuj(")")
            wynik = ("inne", None, None, (lambda f_: (lambda z: f_(z)))(e))  # nawias obcina do jednej wartosci
        else:
            self.blad("nieoczekiwane %r" % (w,))
        while True:
            r, w, linia = self.pk()
            f = wynik[3] if wynik[0] != "wywolanie" else wynik[3]
            if r == "op" and w == ".":
                self.bierz()
                k = self.nazwa_t()
                obj_f = f
                kf = (lambda kk: (lambda z: kk))(k)
                wynik = ("indeks", obj_f, kf, (lambda o, kk: (lambda z: _indeksuj(o(z), kk)))(obj_f, k))
            elif r == "op" and w == "[":
                self.bierz()
                kf = self.wyrazenie()
                self.oczekuj("]")
                obj_f = f
                wynik = ("indeks", obj_f, kf, (lambda o, kk: (lambda z: _indeksuj(o(z), kk(z))))(obj_f, kf))
            elif r == "op" and w == ":":
                self.bierz()
                m = self.nazwa_t()
                argi = self.argumenty()
                obj_f = f

                def wiele(z, o=obj_f, m=m, argi=argi):
                    obj = o(z)
                    fn = _indeksuj(obj, m)
                    return self.interp.wywolaj(fn, [obj] + Parser.wartosci(argi, z))
                wynik = ("wywolanie", None, wiele, (lambda wl: (lambda z: (lambda r_: r_[0] if r_ else None)(wl(z))))(wiele))
            elif (r == "op" and w in ("(", "{")) or r == "napis":
                argi = self.argumenty()
                fn_f = f

                def wiele(z, fn_f=fn_f, argi=argi):
                    return self.interp.wywolaj(fn_f(z), Parser.wartosci(argi, z))
                wynik = ("wywolanie", None, wiele, (lambda wl: (lambda z: (lambda r_: r_[0] if r_ else None)(wl(z))))(wiele))
            else:
                break
            wynik[3].wiele = wynik[2] if wynik[0] == "wywolanie" else None
        return wynik

    def argumenty(self):
        r, w, _ = self.pk()
        if r == "napis":
            self.bierz()
            return [((lambda s: (lambda z: s))(w), None)]
        if w == "{":
            return [(self.konstruktor(), None)]
        self.oczekuj("(")
        if self.jest(")"):
            self.bierz()
            return []
        argi = self.lista_wyrazen()
        self.oczekuj(")")
        return argi


# ------------------------------------------------------------------------------------------------ interpreter
class Interpreter:
    def __init__(self):
        self.globalne = Zasieg(None)
        self.moduly = {}
        self.zrodla = {}
        self._biblioteka()

    def zmienna(self, z, nazwa):
        s = z.znajdz(nazwa)
        if s is None:
            return None
        return s.z[nazwa]

    def przypisz(self, z, nazwa, v):
        s = z.znajdz(nazwa)
        if s is None:
            s = self.globalne
        s.z[nazwa] = v

    def wywolaj(self, fn, argi):
        if isinstance(fn, Funkcja):
            z = Zasieg(fn.zasieg)
            for i, p in enumerate(fn.parametry):
                z.z[p] = argi[i] if i < len(argi) else None
            try:
                fn.cialo(z)
            except _Zwroc as r:
                return r.wartosci
            return []
        if callable(fn):
            r = fn(*argi)
            if r is None:
                return []
            return list(r) if isinstance(r, tuple) else [r]
        raise BladLuau("attempt to call a %s value" % typ(fn))

    def laduj(self, nazwa, tekst):
        # require(script.Parent.X) -> modul X z tej samej paczki (tak jak skladanie w zgodnosc_studio.py)
        tekst = re.sub(r"require\(script\.Parent\.([A-Za-z_][A-Za-z0-9_]*)\)", r'wymagaj("\1")', tekst)
        self.zrodla[nazwa] = tekst

    def wymagaj(self, nazwa):
        if nazwa not in self.moduly:
            cialo = Parser(self.zrodla[nazwa], nazwa, self).program()
            try:
                cialo(Zasieg(self.globalne))
                wynik = None
            except _Zwroc as r:
                wynik = r.wartosci[0] if r.wartosci else None
            self.moduly[nazwa] = wynik
        return self.moduly[nazwa]

    def wykonaj(self, tekst, nazwa="kod"):
        cialo = Parser(tekst, nazwa, self).program()
        try:
            cialo(Zasieg(self.globalne))
        except _Zwroc as r:
            return r.wartosci
        return []

    # -- biblioteka
    def _biblioteka(self):
        g = self.globalne.z
        interp = self

        def blad(wiad=None, poziom=None):
            raise BladLuau(wiad)

        def pcall(fn, *argi):
            try:
                return tuple([True] + interp.wywolaj(fn, list(argi)))
            except BladLuau as e:
                return False, e.wartosc
            except RecursionError:
                return False, "stack overflow"

        def nastepny(t, k=None):
            klucze = t.klucze()
            if k is None:
                i = 0
            else:
                k = _klucz(k)
                i = klucze.index(k) + 1
            while i < len(klucze):
                kk = klucze[i]
                if t.d.get(kk) is not None:
                    return kk, t.d[kk]
                i += 1
            return None

        def pary(t):
            return nastepny, t, None

        g["error"] = blad
        g["pcall"] = pcall
        g["type"] = typ
        g["tostring"] = tostring
        g["next"] = nastepny
        g["pairs"] = pary
        g["print"] = lambda *a: None
        g["wymagaj"] = lambda nazwa: self.wymagaj(nazwa)
        g["tonumber"] = lambda v, b=None: v if isinstance(v, float) else (_tonumber(v) if isinstance(v, str) else None)

        m = Tabela()
        m.set("floor", lambda x: float(math.floor(_liczba(x))) if math.isfinite(_liczba(x)) else x)
        m.set("ceil", lambda x: float(math.ceil(_liczba(x))) if math.isfinite(_liczba(x)) else x)
        m.set("abs", lambda x: abs(_liczba(x)))
        m.set("sqrt", lambda x: math.sqrt(_liczba(x)))
        m.set("huge", math.inf)

        def mmin(*a):
            w = _liczba(a[0])
            for x in a[1:]:
                if _liczba(x) < w:
                    w = x
            return w

        def mmax(*a):
            w = _liczba(a[0])
            for x in a[1:]:
                if _liczba(x) > w:
                    w = x
            return w
        m.set("min", mmin)
        m.set("max", mmax)
        g["math"] = m

        t = Tabela()

        def tinsert(tab, *a):
            if len(a) == 1:
                tab.set(tab.dlugosc() + 1, a[0])
            else:
                raise BladLuau("table.insert z pozycja nie jest obslugiwane")

        def tfind(tab, v, start=None):
            n = int(tab.dlugosc())
            for i in range(1 if start is None else int(start), n + 1):
                if rowne(tab.d.get(float(i)), v):
                    return float(i)
            return None

        def tconcat(tab, sep=""):
            n = int(tab.dlugosc())
            return sep.join(tostring(tab.d[float(i)]) for i in range(1, n + 1))
        t.set("insert", tinsert)
        t.set("find", tfind)
        t.set("concat", tconcat)
        g["table"] = t

        s = Tabela()

        def sformat(fmt, *a):
            wynik, i, j = [], 0, 0
            while i < len(fmt):
                c = fmt[i]
                if c != "%":
                    wynik.append(c)
                    i += 1
                    continue
                m2 = re.match(r"%([-0-9.]*)([dsfgx%])", fmt[i:])
                if not m2:
                    raise BladLuau("string.format: nieobslugiwany wzorzec")
                spec, rodz = m2.group(1), m2.group(2)
                if rodz == "%":
                    wynik.append("%")
                elif rodz == "d":
                    x = _liczba(a[j])
                    if x != math.floor(x):
                        raise BladLuau("string.format %d: liczba nie jest calkowita")
                    wynik.append(("%" + spec + "d") % int(x))
                    j += 1
                elif rodz == "s":
                    wynik.append(("%" + spec + "s") % tostring(a[j]))
                    j += 1
                else:
                    wynik.append(("%" + spec + rodz) % _liczba(a[j]))
                    j += 1
                i += len(m2.group(0))
            return "".join(wynik)

        def ssub(st, i, j=None):
            b = st.encode("utf-8")
            n = len(b)
            i = int(i)
            j = n if j is None else int(j)
            if i < 0:
                i = max(n + i + 1, 1)
            elif i == 0:
                i = 1
            if j < 0:
                j = n + j + 1
            elif j > n:
                j = n
            return b[i - 1:j].decode("utf-8", errors="replace") if i <= j else ""

        def sfind(st, wzor, start=None, zwykly=None):
            if not zwykly:
                raise BladLuau("string.find bez trybu zwyklego nie jest obslugiwane")
            b, w = st.encode("utf-8"), wzor.encode("utf-8")
            k = b.find(w, (int(start) - 1) if start else 0)
            if k < 0:
                return None
            return float(k + 1), float(k + len(w))
        s.set("format", sformat)
        s.set("sub", ssub)
        s.set("find", sfind)
        s.set("lower", lambda st: st.lower())
        s.set("byte", lambda st, i=1.0: float(st.encode("utf-8")[int(i) - 1]))
        g["string"] = s


def _liczba(x):
    if not isinstance(x, float):
        raise BladLuau("oczekiwano liczby, jest %s" % typ(x))
    return x


def _tonumber(s):
    try:
        return float(s)
    except ValueError:
        return None


# ------------------------------------------------------------------------------------------------ Python <-> Luau
def do_luau(v):
    """Wartosc z JSON/Pythona -> wartosc interpretera (listy -> tabele 1..n, liczby -> float)."""
    if v is None or isinstance(v, (bool, str)):
        return v
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, (list, tuple)):
        t = Tabela()
        for i, x in enumerate(v):
            t.set(float(i + 1), do_luau(x))
        return t
    if isinstance(v, dict):
        t = Tabela()
        for k, x in v.items():
            t.set(float(k) if isinstance(k, int) and not isinstance(k, bool) else k, do_luau(x))
        return t
    raise TypeError("nie umiem zamienic %r" % (v,))


def z_luau(v, pusta_jako_lista=False):
    """Wartosc interpretera -> Python (tabela z kluczami 1..n bez dziur -> lista, inna -> slownik). Pusta tabela ->
    {} albo [] (pusta_jako_lista=True — tak koduje ja HttpService:JSONEncode w Roblox)."""
    if isinstance(v, Tabela):
        n = int(v.dlugosc())
        if n > 0 and len(v.d) == n:
            return [z_luau(v.d[float(i)], pusta_jako_lista) for i in range(1, n + 1)]
        if not v.d:
            return [] if pusta_jako_lista else {}
        return {(int(k) if isinstance(k, float) and k == int(k) else k): z_luau(x, pusta_jako_lista) for k, x in v.d.items()}
    if isinstance(v, float) and v == math.floor(v) and abs(v) < 2 ** 53:
        return int(v)
    return v
