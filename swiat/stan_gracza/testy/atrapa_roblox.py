# -*- coding: utf-8 -*-
"""Atrapa kawałka Roblox dla interpretera tools/walka/luau_mini.py — żeby uruchomić PRAWDZIWY SerwerStanu.server.luau
bez Studio (testy/test_stanu.py, klasa TestSerweraOffline).

Atrapy: instancje z atrybutami (GetAttribute / SetAttribute / GetAttributeChangedSignal — sygnał od razu, nie
odroczony: ostrzejszy test ponownego wejścia), dzieci (FindFirstChild / WaitForChild / GetChildren), zdarzenia
(Connect / Disconnect), Players, ReplicatedStorage, RunService (IsStudio = true), workspace z zegarem serwera, task
(delay do kolejki, spawn od razu), os.clock, warn, typeof, require. To NIE jest Roblox — sprawdza logikę skryptu
i styk z sygnałami, a nie zachowanie silnika Roblox (to robi część B w Studio).
"""
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TU)))
WALKA = os.path.join(REPO, "tools", "walka")
if WALKA not in sys.path:
    sys.path.insert(0, WALKA)
import luau_mini as LM  # noqa: E402


def lista(elementy):
    t = LM.Tabela()
    for i, e in enumerate(elementy):
        t.set(float(i + 1), e)
    return t


def py(v):
    """Wartość z Luau → Python (liczby całkowite jako int)."""
    return LM.z_luau(v)


class Zdarzenie:
    def __init__(self, swiat):
        self.swiat = swiat
        self.funkcje = []
        self.t = LM.Tabela()
        self.t.set("Connect", self._connect)

    def _connect(self, _s, fn):
        self.funkcje.append(fn)
        c = LM.Tabela()
        c.set("Disconnect", lambda _c: self.funkcje.remove(fn) if fn in self.funkcje else None)
        return c

    def odpal(self, *argi):
        for fn in list(self.funkcje):
            self.swiat.wolaj(fn, *argi)


class Inst:
    def __init__(self, swiat, nazwa, klasa, rodzic=None):
        self.swiat = swiat
        self.klasa = klasa
        self.atrybuty = {}
        self.sygnaly = {}
        self.dzieci = []
        self.t = t = LM.Tabela()
        swiat.instancje[id(t)] = self
        t.set("Name", nazwa)
        t.set("ClassName", klasa)
        t.set("GetAttribute", lambda _s, n: self.atrybuty.get(n))
        t.set("GetAttributes", lambda _s: LM.do_luau(dict(self.atrybuty)) if self.atrybuty else LM.Tabela())
        t.set("SetAttribute", lambda _s, n, v=None: self.ustaw(n, v))
        t.set("GetAttributeChangedSignal", lambda _s, n: self.sygnal(n).t)
        t.set("FindFirstChild", lambda _s, n, *_: self.dziecko(n))
        t.set("WaitForChild", lambda _s, n, *_: self.dziecko(n))
        t.set("GetChildren", lambda _s: lista([d.t for d in self.dzieci]))
        t.set("IsA", lambda _s, k: k == klasa or k == "Instance")
        t.set("GetFullName", lambda _s: nazwa)
        t.set("Destroy", lambda _s: self.usun())
        self.destroying = Zdarzenie(swiat)
        self.dodane = Zdarzenie(swiat)
        t.set("Destroying", self.destroying.t)
        t.set("ChildAdded", self.dodane.t)
        if rodzic:
            rodzic.dodaj(self)

    @property
    def nazwa(self):
        return self.t.get("Name")

    def dodaj(self, d):
        self.dzieci.append(d)
        d.t.set("Parent", self.t)
        self.dodane.odpal(d.t)

    def usun(self):
        self.destroying.odpal()
        rodzic = self.swiat.instancje.get(id(self.t.get("Parent"))) if self.t.get("Parent") else None
        if rodzic and self in rodzic.dzieci:
            rodzic.dzieci.remove(self)
        self.t.set("Parent", None)

    def dziecko(self, n):
        for d in self.dzieci:
            if d.nazwa == n:
                return d.t
        return None

    def sygnal(self, n):
        if n not in self.sygnaly:
            self.sygnaly[n] = Zdarzenie(self.swiat)
        return self.sygnaly[n]

    def ustaw(self, n, v):
        if isinstance(v, int) and not isinstance(v, bool):
            v = float(v)
        stara = self.atrybuty.get(n)
        if v is None:
            self.atrybuty.pop(n, None)
        else:
            self.atrybuty[n] = v
        if stara != v and n in self.sygnaly:
            self.sygnaly[n].odpal()


class Swiat:
    """Jeden serwer z kontenerem StanGracza; czas płynie tylko przez krok()."""

    def __init__(self):
        self.it = LM.Interpreter()
        self.instancje = {}
        self.moduly = {}
        self.ostrzezenia = []
        self.czas = 1000.0
        self.zadania = []
        self.do_klienta = []
        g = self.it.globalne.z
        self.workspace = Inst(self, "Workspace", "Workspace")
        self.workspace.t.set("GetServerTimeNow", lambda _s: self.czas)
        self.players = Inst(self, "Players", "Players")
        self.dolaczyl = Zdarzenie(self)
        self.wyszedl = Zdarzenie(self)
        self.players.t.set("PlayerAdded", self.dolaczyl.t)
        self.players.t.set("PlayerRemoving", self.wyszedl.t)
        self.players.t.set("GetPlayers", lambda _s: lista([d.t for d in self.players.dzieci]))
        self.replicated = Inst(self, "ReplicatedStorage", "ReplicatedStorage")
        run = Inst(self, "RunService", "RunService")
        run.t.set("IsStudio", lambda _s: True)
        http = Inst(self, "HttpService", "HttpService")
        self._guid = [0]

        def guid(_s, *_a):
            self._guid[0] += 1
            return "serwer-%d-%d" % (id(self) % 10000, self._guid[0])
        http.t.set("GenerateGUID", guid)
        self.uslugi = {"Players": self.players, "ReplicatedStorage": self.replicated, "RunService": run, "HttpService": http}
        self.zamkniecie = []
        game = LM.Tabela()
        game.set("GetService", lambda _s, n: self.uslugi[n].t)
        game.set("BindToClose", lambda _s, fn: self.zamkniecie.append(fn))
        g["game"] = game
        g["workspace"] = self.workspace.t
        task = LM.Tabela()
        task.set("delay", lambda t, fn, *a: self.zadania.append((self.czas + t, fn, a)))
        task.set("spawn", lambda fn, *a: self.wolaj(fn, *a))
        task.set("wait", lambda s=0.03: self.krok(float(s)) or float(s))  # tylko BindToClose: czas płynie, zadania idą
        g["task"] = task
        os_ = LM.Tabela()
        os_.set("clock", lambda: self.czas)
        os_.set("time", lambda: float(int(self.czas)))
        g["os"] = os_
        g["warn"] = lambda *a: self.ostrzezenia.append(" ".join(LM.tostring(x) for x in a))
        g["typeof"] = lambda v: "Instance" if isinstance(v, LM.Tabela) and v.get("ClassName") else LM.typ(v)
        g["require"] = self.wymagaj
        g["math"].set("huge", float("inf"))
        g["string"].set("upper", lambda s: s.upper())  # luau_mini nie ma string.upper (Roblox ma)
        g["table"].set("remove", self._usun_z_listy)  # luau_mini nie ma table.remove (Roblox ma)

    @staticmethod
    def _usun_z_listy(t, poz=None):
        n = int(t.dlugosc())
        if n == 0:
            return None
        i = n if poz is None else int(poz)
        w = t.get(float(i))
        for j in range(i, n):
            t.set(float(j), t.get(float(j + 1)))
        t.set(float(n), None)
        return w

    def wolaj(self, fn, *argi):
        return self.it.wywolaj(fn, list(argi))

    def modul(self, rodzic, nazwa, tekst=None, wartosc=None):
        m = Inst(self, nazwa, "ModuleScript", rodzic)
        self.moduly[id(m.t)] = (tekst, wartosc, nazwa)
        return m

    def wymagaj(self, m):
        tekst, wartosc, nazwa = self.moduly[id(m)]
        if wartosc is None:
            wartosc = self.it.wykonaj(tekst, nazwa)[0]
            self.moduly[id(m)] = (tekst, wartosc, nazwa)
        return wartosc

    def krok(self, s):
        """Przesuwa zegar o s sekund i wykonuje zadania task.delay, których czas minął (po kolei)."""
        koniec = self.czas + s
        while True:
            gotowe = sorted((z for z in self.zadania if z[0] <= koniec), key=lambda z: z[0])
            if not gotowe:
                break
            z = gotowe[0]
            self.zadania.remove(z)
            self.czas = max(self.czas, z[0])
            self.wolaj(z[1], *z[2])
        self.czas = koniec

    def gracz(self, nazwa, atrybuty):
        g = Inst(self, nazwa, "Player", self.players)
        for k, v in atrybuty.items():
            g.ustaw(k, v)
        return g


class Magazyn:
    """Atrapa DataStore wspólna dla kilku serwerów (Swiat): UpdateAsync(klucz, przekształcenie) jak w Roblox —
    przekształcenie dostaje kopię starego rekordu, nil = anuluj; błędy na żądanie (bledy = ile kolejnych wywołań rzuca),
    zapis wywołań (czas, klucz, serwer, rodzaj) do sprawdzania limitów; podczas = funkcja wołana w trakcie wywołania
    (np. wyjście gracza w trakcie zapisu)."""

    def __init__(self):
        self.rekordy = {}
        self.bledy = 0
        self.blad_tekst = "502: usługa niedostępna (atrapa)"
        self.wywolania = []
        self.podczas = None
        self.budzet = 100

    def dodaj_do(self, sw):
        dss = Inst(sw, "DataStoreService", "DataStoreService")
        magazyn = self

        def update(_s, klucz, fn):
            magazyn.wywolania.append((sw.czas, klucz, id(sw)))
            if magazyn.bledy > 0:
                magazyn.bledy -= 1
                raise LM.BladLuau(magazyn.blad_tekst)
            stary = magazyn.rekordy.get(klucz)
            wynik = sw.wolaj(fn, LM.do_luau(stary) if stary is not None else None)
            nowy = wynik[0] if wynik else None
            if magazyn.podczas:
                h, magazyn.podczas = magazyn.podczas, None
                h()
            if nowy is None:
                return None
            magazyn.rekordy[klucz] = LM.z_luau(nowy)
            return LM.do_luau(magazyn.rekordy[klucz])
        ds = LM.Tabela()
        ds.set("UpdateAsync", update)
        dss.t.set("GetDataStore", lambda _s, nazwa, *_: (magazyn.nazwy.append(nazwa), ds)[1])
        dss.t.set("GetRequestBudgetForRequestType", lambda _s, *_: float(magazyn.budzet))
        self.nazwy = getattr(self, "nazwy", [])
        sw.uslugi["DataStoreService"] = dss
        return dss


def kontener_stanu(sw, zrodla, nazwy_inne):
    """Workspace/StanGracza jak po zbuduj.py: moduły, zdalne, sygnały; skrypt serwera trzeba uruchomić osobno."""
    k = Inst(sw, "StanGracza", "Folder", sw.workspace)
    k.ustaw("Wygenerowane", True)
    k.ustaw("StatystykiKlasy", True)
    foldery = {n: Inst(sw, n, "Folder", k) for n in ("Moduly", "Zdalne", "Sygnaly")}
    sw.modul(foldery["Moduly"], "DaneStanu", zrodla["DaneStanu"])
    sw.modul(foldery["Moduly"], "LogikaStanu", zrodla["LogikaStanu"])
    if "ZapisStanu" in zrodla:
        sw.modul(foldery["Moduly"], "ZapisStanu", zrodla["ZapisStanu"])
    inne = {}
    for klasa, sciezka in nazwy_inne:
        f, n = sciezka.split("/")
        o = Inst(sw, n, klasa, foldery[f])
        if klasa == "RemoteEvent":
            o.na_serwer = Zdarzenie(sw)
            o.t.set("OnServerEvent", o.na_serwer.t)
            o.t.set("FireClient", lambda _s, gracz, *a: sw.do_klienta.append((gracz, [py(x) for x in a])))
        inne[n] = o
    skrypt = LM.Tabela()
    skrypt.set("Parent", k.t)
    sw.it.globalne.z["script"] = skrypt
    return k, inne
