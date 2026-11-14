# -*- coding: utf-8 -*-
"""Geometria rigu z klocków bez Studio: kinematyka w przód (stawy Motor6D + klipy z danych) w układzie Roblox.

Te same wzory co w Studio (budowa/szablon.luau i zrodla/Klipy.luau):
    staw:  Part1.CFrame = Part0.CFrame * C0 * Transform * C1:Inverse()
           C0 = CFrame.new(staw - srodek_rodzica), C1 = CFrame.new(staw - srodek_kosci)
    bryła: przyspawana do części kości w spoczynku, więc  bryła = kość * CFrame.new(-srodek_kosci) * bryła_spoczynek
Klatka klipu dla kości: Transform = CFrame.new(x, y, z) * CFrame.fromOrientation(rx, ry, rz).
Służy do policzenia wzrostu, zasięgu, chwil trafienia w klipach i testu „broń nie przechodzi przez głowę ani tułów”.
"""
import math

# CFrame jako (R, t): R = krotka 3 wierszy, t = (x, y, z)
I3 = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def _mm(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def _mv(a, v):
    return tuple(sum(a[i][k] * v[k] for k in range(3)) for i in range(3))


def _rx(a):
    c, s = math.cos(a), math.sin(a)
    return ((1.0, 0.0, 0.0), (0.0, c, -s), (0.0, s, c))


def _ry(a):
    c, s = math.cos(a), math.sin(a)
    return ((c, 0.0, s), (0.0, 1.0, 0.0), (-s, 0.0, c))


def _rz(a):
    c, s = math.cos(a), math.sin(a)
    return ((c, -s, 0.0), (s, c, 0.0), (0.0, 0.0, 1.0))


def orientacja(rx, ry, rz):
    """CFrame.fromOrientation(rx, ry, rz) (radiany): R = Ry · Rx · Rz."""
    return _mm(_ry(ry), _mm(_rx(rx), _rz(rz)))


def cf(t=(0.0, 0.0, 0.0), R=I3):
    return (R, tuple(float(v) for v in t))


def razy(a, b):
    """a * b (złożenie CFrame)."""
    return (_mm(a[0], b[0]), tuple(a[1][i] + _mv(a[0], b[1])[i] for i in range(3)))


def punkt(a, v):
    """a * v (punkt w układzie a → świat)."""
    p = _mv(a[0], v)
    return tuple(a[1][i] + p[i] for i in range(3))


def odwrotnosc(a):
    Rt = tuple(tuple(a[0][j][i] for j in range(3)) for i in range(3))
    t = _mv(Rt, a[1])
    return (Rt, (-t[0], -t[1], -t[2]))


def przesun(v):
    return cf(v)


# --------------------------------------------------------------------------- rig
class Rig:
    """Rig z danych roblox_klocki.rig() (układ Roblox, początek = ziemia pod postacią, przód −Z)."""

    def __init__(self, dane):
        self.d = dane
        self.kosci = dane["kosci"]                     # [nazwa, rodzic(1-based, 0 = HRP), staw xyz, srodek xyz, rozmiar xyz, staw]
        self.hrp = tuple(dane["hrp"])
        self.indeks = {k[0]: i + 1 for i, k in enumerate(self.kosci)}
        self.klipy = {k["n"]: k for k in dane.get("klipy", [])}

    def srodek(self, i):
        if i == 0:
            return self.hrp
        return tuple(self.kosci[i - 1][5:8])

    def pozy(self, transformy=None):
        """Słownik indeks kości -> CFrame części kości w układzie modelu dla podanych Transform (indeks -> CFrame)."""
        transformy = transformy or {}
        wynik = {0: przesun(self.hrp)}
        for i, k in enumerate(self.kosci, start=1):
            rodzic = k[1]
            staw = tuple(k[2:5])
            sr_r = self.srodek(rodzic)
            sr = self.srodek(i)
            c0 = przesun(tuple(staw[j] - sr_r[j] for j in range(3)))
            c1 = przesun(tuple(staw[j] - sr[j] for j in range(3)))
            T = transformy.get(i, cf())
            wynik[i] = razy(razy(razy(wynik[rodzic], c0), T), odwrotnosc(c1))
        return wynik

    def transformy(self, klip, klatka):
        """Transform każdej animowanej kości w klatce klipu (klatka całkowita 0…dl)."""
        kl = self.klipy[klip]
        w = kl["klatki"][max(0, min(int(klatka), kl["dl"]))]
        t = {}
        for j, idx in enumerate(kl["kosci"]):
            o = j * 6
            t[idx] = cf((w[o], w[o + 1], w[o + 2]), orientacja(w[o + 3], w[o + 4], w[o + 5]))
        return t

    def czesc_cf(self, c, pozy):
        """CFrame bryły (wiersz z dane["czesci"]) dla póz kości."""
        i = c[0]
        sr = self.srodek(i)
        spocz = cf((c[3], c[4], c[5]), orientacja(c[6], c[7], c[8]))
        return razy(razy(pozy[i], przesun((-sr[0], -sr[1], -sr[2]))), spocz)

    def zaczep_cf(self, nazwa, pozy):
        for z in self.d["zaczepy"]:
            if z[0] == nazwa:
                return razy(pozy[z[1]], cf((z[2], z[3], z[4]), orientacja(z[5], z[6], z[7])))
        raise KeyError("brak zaczepu %s" % nazwa)


def narozniki(c_cf, rozmiar):
    hx, hy, hz = (v / 2.0 for v in rozmiar)
    return [punkt(c_cf, (sx * hx, sy * hy, sz * hz)) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]


def punkty_probne(c_cf, rozmiar, n=3):
    """Siatka n×n×n punktów w bryle (z rogami) — do wykrywania przenikania."""
    wyn = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                u = (i / (n - 1.0) - 0.5, j / (n - 1.0) - 0.5, k / (n - 1.0) - 0.5)
                wyn.append(punkt(c_cf, (u[0] * rozmiar[0], u[1] * rozmiar[1], u[2] * rozmiar[2])))
    return wyn


def w_pudle(p, c_cf, rozmiar, margines=0.0):
    """Czy punkt p jest wewnątrz pudła (CFrame, rozmiar) zmniejszonego o margines z każdej strony."""
    lok = punkt(odwrotnosc(c_cf), p)
    return all(abs(lok[i]) < rozmiar[i] / 2.0 - margines for i in range(3))


def obwiednia(rig, pozy=None):
    """(min xyz, max xyz) wszystkich brył dla póz (domyślnie spoczynek)."""
    pozy = pozy or rig.pozy()
    mn, mx = [1e9] * 3, [-1e9] * 3
    for c in rig.d["czesci"]:
        for p in narozniki(rig.czesc_cf(c, pozy), c[9:12]):
            for i in range(3):
                mn[i], mx[i] = min(mn[i], p[i]), max(mx[i], p[i])
    return mn, mx
