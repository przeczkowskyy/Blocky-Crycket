# -*- coding: utf-8 -*-
"""Wygląd areny Training Center: dekoracje z części Roblox (bez zasobów z zewnątrz) i ładniejsze figury trenerów.

    python -B swiat/trening_proba/dekoracje.py        # liczba części wg grup, budżet i kontrola (pola gry, kadry, E)

Wszystko tutaj jest TYLKO wyglądem: zasady gier, położenia stanowisk, kamery i części animowane przez klienta
(dane.NAZWY) zostają bez zmian. scena.czesci(D) woła stąd:
    figura(...)        — trener z klocków w stylu sprzedawców bazaru (duża głowa, oczy ze źrenicami, brwi, nos, uśmiech,
                         uszy, buty, pas, dłonie); części animowane (RamieP miotacza i trenera Bieżni) to nadal jeden klocek
    golem_dodatki(...) — kamienne szczegóły golema (pięść, oczy i ramię zostają, jak były)
    dodaj(S, D, K)     — dekoracje areny w grupie „Arena/Dekoracje/…” (bez kolizji, poza kilkoma dużymi bryłami)
Reguły, których pilnuje kontrola(D) i testy 4g–4j:
    * pola gry (POLA_GRY, koło Kłód, korytarz lobby z podpowiedziami E) wolne od dekoracji wyższych niż próg płaskości,
    * żadna dekoracja nie przecina promienia oko kamery → pole gry / postać (kamera gry z kołysaniem, początek i droga
      odliczania, zbliżenie po rundzie dla każdego miejsca postaci),
    * przedpole kadru czyste: w kadrze (także telefonu) nic nie stoi bliżej oka niż postać / cel kamery,
    * budżet: przyrost części, udział części bez kolizji, zero świateł.
Układ: lokalny areny (x na wschód, z na południe — strona kamer, y = 0 to wierzch podłogi); _Scena dodaje środek areny.
"""
import math
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))

TUSZ, KREM = "17121F", "FFF6E0"
DREWNO, DREWNO_S, DREWNO_J = "6B4A2F", "8B5A2E", "D49A5A"
SKORA, SKORA_C = "E8B98A", "D6A473"
ZLOTO, CZERWIEN, POMARANCZ = "F2B630", "E5392B", "F08A24"
NIEBIESKI, ZIELEN, FIOLET, TURKUS, ROZ = "2659B3", "1E6E43", "7B4FB5", "1C9886", "D93A8C"
METAL, METAL_C, KAMIEN, KAMIEN_C = "9AA0A8", "4A5368", "8A8F99", "6A6E79"
SLOMA, LAMPION, LISC, LISC_C = "E8C872", "FFB030", "72BF3A", "3F8F35"
PASY = (CZERWIEN, KREM, ZLOTO, NIEBIESKI, KREM, ZIELEN)
NAPIS_ARENY = "TRAINING CENTER"
PLASKIE = 0.25          # części o wierzchu do tej wysokości nad podłogą to wzór podłogi (nie przeszkoda, nie przesłona)
PRZYROST_MAX = 1500     # budżet: najwyżej tyle części ponad arenę bez dekoracji
BEZ_KOLIZJI_MIN = 0.85  # co najmniej taki ułamek dekoracji bez kolizji

# pola gry względem podestu stanowiska: (min, max) — tu nie stoi żadna dekoracja wyższa niż PLASKIE
POLA_GRY = {
    "sila": ([-7.5, PLASKIE, -14.8], [7.5, 11.0, 4.0]),          # gracz, strefy ciosu i tory lotu od miotacza
    "pancerz": ([-4.5, PLASKIE, -7.2], [6.5, 12.0, 4.0]),        # gracz z tarczą i droga pięści golema
    "kondycja": ([-4.2, PLASKIE, -6.2], [3.6, 9.0, 11.0]),       # taśma z poręczami
    "inteligencja": ([-4.5, PLASKIE, -7.4], [9.0, 11.0, 4.0]),   # gracz i przedpole kamieni run
    "szczescie": ([-6.2, PLASKIE, -3.2], [6.2, 15.5, 3.5]),      # trzy tory i spadające koniczyny
}
POLE_LOBBY = ([-5.0, PLASKIE, 3.0], [5.0, 7.0, 22.4])            # przybycie, tablica wyboru (E), dojście do wyjścia (E)
# obramowania pól stanowisk na podłodze (układ areny): x0, x1, z0, z1
RAMY = {"zrecznosc": (-119, -91, -12.5, 14.5), "kondycja": (-72, -53, 0, 20.5), "sila": (-33.5, -14.5, -11.5, 13.5),
        "pancerz": (14.5, 33.5, -6, 13.5), "inteligencja": (52, 76, -3.5, 13.5), "szczescie": (91, 118, -10.5, 13.5)}


def _plus(a, b):
    return [a[i] + b[i] for i in range(3)]


def _obroc(v, kat):
    a = math.radians(kat)
    return [round(v[0] * math.cos(a) + v[2] * math.sin(a), 4), v[1], round(-v[0] * math.sin(a) + v[2] * math.cos(a), 4)]


class _G:
    """Grupa części w układzie (początek, obrót wokół Y); nazwy numerowane w obrębie rodzica; domyślnie bez kolizji."""

    def __init__(self, S, r, baza=(0, 0, 0), ry=0.0):
        self.S, self.r, self.baza, self.ry = S, r, list(baza), ry
        if not hasattr(S, "nazwy"):
            S.nazwy = {}

    def w(self, baza, ry=0.0, r=None):
        return _G(self.S, self.r + ("/" + r if r else ""), baza, ry)

    def _n(self, n):
        k = (self.r, n)
        i = self.S.nazwy.get(k, 0) + 1
        self.S.nazwy[k] = i
        return n if i == 1 else "%s%d" % (n, i)

    def _p(self, v):
        return _plus(self.baza, _obroc(v, self.ry))

    def kl(self, n, v, s, c, m="SmoothPlastic", t=0.0, kol=False, rz=0.0, rx=0.0, ry=0.0, napis=None):
        o = [rx, round(self.ry + ry, 3), rz]
        return self.S.klocek(self.r, self._n(n), self._p(v), s, c, m=m, t=t, kol=kol, o=o if any(o) else None, napis=napis)

    def wa(self, n, v, dl, sr, c, os_="y", m="SmoothPlastic", t=0.0, kol=False):
        o = {"y": [0, 0, 90], "x": [0, self.ry, 0], "z": [0, self.ry + 90, 0]}[os_]
        d = self.S.klocek(self.r, self._n(n), self._p(v), [dl, sr, sr], c, m=m, t=t, kol=kol, o=o if any(o) else None)
        d["k"] = "C"
        return d

    def ku(self, n, v, sr, c, m="SmoothPlastic", t=0.0, kol=False):
        d = self.S.klocek(self.r, self._n(n), self._p(v), [sr, sr, sr], c, m=m, t=t, kol=kol)
        d["k"] = "K"
        return d

    def belka(self, n, a, b, gr, c, m="SmoothPlastic", kol=False):
        """Klocek od punktu a do b (układ grupy): długa oś X, obrót = kierunek w poziomie i pochylenie."""
        A, B = self._p(a), self._p(b)
        dx, dy, dz = B[0] - A[0], B[1] - A[1], B[2] - A[2]
        h = math.hypot(dx, dz)
        o = [0, round(math.degrees(math.atan2(-dz, dx)), 3), round(math.degrees(math.atan2(dy, h)), 3)]
        return self.S.klocek(self.r, self._n(n), [(A[i] + B[i]) / 2 for i in range(3)], [math.sqrt(h * h + dy * dy), gr, gr],
                             c, m=m, kol=kol, o=o if any(o) else None)

    def proporczyk(self, n, v, kier, c, s=(0.15, 1.3, 1.1)):
        """Trójkątna chorągiewka (klin) pod punktem v sznurka; kier = (dx, dz) sznurka w układzie areny."""
        p = self._p(v)
        p[1] -= s[1] / 2
        d = self.S.klocek(self.r, self._n(n), p, list(s), c, m="Fabric", kol=False,
                          o=[180, round(math.degrees(math.atan2(kier[0], -kier[1])), 2), 0])
        d["k"] = "W"
        return d


def girlanda(g, a, b, kolory=PASY, n=6, ugiecie=1.2, lampiony=False):
    """Sznurek z trzech odcinków ugięty w łuk i n chorągiewek (albo lampionów-kul Neon)."""
    def p(t):
        return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t - ugiecie * 4 * t * (1 - t), a[2] + (b[2] - a[2]) * t]
    for i in range(3):
        g.belka("Sznurek", p(i / 3.0), p((i + 1) / 3.0), 0.12, TUSZ)
    kier = _obroc([b[0] - a[0], 0, b[2] - a[2]], g.ry)
    for i in range(n):
        q = p((i + 0.5) / n)
        if lampiony:
            g.ku("Lampion", [q[0], q[1] - 0.55, q[2]], 0.9, kolory[i % len(kolory)], m="Neon")
        else:
            g.proporczyk("Proporczyk", q, (kier[0], kier[2]), kolory[i % len(kolory)])


# ------------------------------------------------------------------------------------------------ figury
def figura(S, r, baza, kat, ubranie, spodnie, buty=TUSZ, rekaw=None, skora=SKORA, pas=DREWNO, cale_ramie_p=False,
           dodatki=()):
    """Trener z klocków twarzą do +z, obrócony o kat wokół Y. cale_ramie_p: prawe ramię jako jeden klocek „RamieP”
    (animuje je klient — bez osobnej dłoni). dodatki: (nazwa, przesunięcie, rozmiar, kolor[, materiał[, obrót z]])."""
    g = _G(S, r, baza, kat)
    rekaw = rekaw or ubranie
    for sx, b in ((-1, "L"), (1, "P")):
        g.kl("But" + b, [sx * 0.65, 0.35, 0.2], [1.15, 0.7, 1.7], buty)
        g.kl("Noga" + b, [sx * 0.65, 1.55, 0], [1.0, 1.7, 1.0], spodnie, kol=True)
        g.kl("Ucho" + b, [sx * 1.42, 6.5, -0.05], [0.3, 0.7, 0.55], SKORA_C if skora == SKORA else skora)
        g.kl("Oko" + b, [sx * 0.56, 6.8, 1.22], [0.64, 0.74, 0.1], KREM)
        g.kl("Zrenica" + b, [sx * 0.56 + 0.06, 6.74, 1.28], [0.3, 0.42, 0.06], TUSZ)
        g.kl("Brew" + b, [sx * 0.58, 7.32, 1.24], [0.82, 0.2, 0.1], TUSZ, rz=-sx * 9)
        g.kl("Usta" + b, [sx * 0.27, 5.95, 1.23], [0.62, 0.18, 0.08], TUSZ, rz=sx * 12)
    g.kl("Pas", [0, 2.6, 0], [3.12, 0.45, 1.72], pas)
    g.kl("Tulow", [0, 4.05, 0], [3.0, 2.7, 1.6], ubranie, kol=True)
    g.kl("Glowa", [0, 6.6, 0], [2.6, 2.4, 2.4], skora)
    g.kl("Nos", [0, 6.42, 1.36], [0.5, 0.56, 0.36], SKORA_C if skora == SKORA else skora)
    g.kl("RamieL", [-2.05, 4.3, 0], [1.0, 2.4, 1.0], rekaw)
    g.kl("DlonL", [-2.05, 2.75, 0], [0.9, 0.8, 0.9], skora)
    if cale_ramie_p:
        g.kl("RamieP", [2.0, 4.3, 0], [1.0, 2.8, 1.0], rekaw)
    else:
        g.kl("RamieP", [2.05, 4.3, 0], [1.0, 2.4, 1.0], rekaw)
        g.kl("DlonP", [2.05, 2.75, 0], [0.9, 0.8, 0.9], skora)
    for d in dodatki:
        g.kl(d[0], d[1], d[2], d[3], m=d[4] if len(d) > 4 else "SmoothPlastic", rz=d[5] if len(d) > 5 else 0.0)
    return g


def golem_dodatki(S, r, g0):
    """Kamienne szczegóły golema Pancerza (bez kolizji; pięść, oczy i prawe ramię — bez zmian)."""
    g = _G(S, r, g0)
    for sx, b in ((-1, "L"), (1, "P")):
        g.kl("Stopa" + b, [sx * 1.4, 0.4, 0.5], [2.4, 0.8, 3.0], "7C7C88", m="Slate")
        g.kl("Brew" + b, [sx * 0.75, 8.85, 1.5], [1.1, 0.35, 0.3], "6E6E7A", rz=sx * 12)
        g.kl("Mech" + b, [sx * 1.7, 7.05, 0.2], [1.5, 0.3, 2.6], LISC_C)
    g.kl("Szczeka", [0, 7.25, 1.45], [2.4, 0.7, 0.5], "8C8C99", m="Slate")
    for i, dx in enumerate((-0.7, 0, 0.7)):
        g.kl("Zab%d" % (i + 1), [dx, 7.7, 1.72], [0.4, 0.4, 0.12], KREM)
    g.kl("NaramiennikL", [-3.3, 7.25, 0], [2.2, 0.7, 2.2], "7C7C88", m="Slate")
    g.kl("Kolec", [-3.3, 7.95, 0], [0.8, 0.8, 0.8], "6E6E7A", rz=45)
    g.kl("Klamra", [0, 3.2, 1.65], [1.2, 0.9, 0.2], ZLOTO)
    for i, (dx, dy, rz, dl) in enumerate(((-1.2, 5.6, 35, 1.6), (0.9, 4.6, -30, 1.3), (1.5, 6.1, 60, 1.0))):
        g.kl("Rysa%d" % (i + 1), [dx, dy, 1.53], [dl, 0.14, 0.06], TUSZ, rz=rz)
    g.kl("MechGlowa", [-0.6, 9.5, 0.2], [1.6, 0.25, 1.8], LISC)
    g.kl("Grzbiet", [0, 6.2, -1.7], [3.4, 2.2, 0.6], "7C7C88", m="Slate")


# ------------------------------------------------------------------------------------------------ rekwizyty
def miecz(g, v, dl=3.4, kolor=METAL, pion=True, rz=0.0):
    """Miecz ostrzem w górę (pion) w punkcie v = środek jelca."""
    u = g.w(g._p(v), g.ry)
    u.kl("Ostrze", [0, dl / 2 + 0.15, 0], [0.45, dl, 0.14], kolor, m="Metal", rz=rz)
    u.kl("Jelec", [0, 0, 0], [1.3, 0.3, 0.3], ZLOTO, rz=rz)
    u.kl("Rekojesc", [0, -0.6, 0], [0.3, 0.9, 0.3], DREWNO, rz=rz)


def beczka(g, v, kolor=DREWNO_S, wys=2.4, sr=2.2, kol=True):
    g.wa("Beczka", [v[0], v[1] + wys / 2, v[2]], wys, sr, kolor, m="WoodPlanks", kol=kol)
    for dy in (0.5, wys - 0.5):
        g.wa("Obrecz", [v[0], v[1] + dy, v[2]], 0.2, sr + 0.12, METAL_C, m="Metal")


def skrzynia(g, v, a=1.8, kolor=DREWNO_J, ry=0.0):
    g.kl("Skrzynia", [v[0], v[1] + a / 2, v[2]], [a, a, a], kolor, m="WoodPlanks", kol=True, ry=ry)
    g.kl("Listwa", [v[0], v[1] + a / 2, v[2]], [a + 0.1, 0.25, a + 0.1], DREWNO, ry=ry)


def hantel(g, v, dl=2.0, sr=1.0, kolor=METAL_C, os_="x"):
    g.wa("Gryf", v, dl, 0.25, METAL, os_=os_, m="Metal")
    for s in (-1, 1):
        d = [s * (dl / 2 - 0.25) if os_ == "x" else 0, 0, s * (dl / 2 - 0.25) if os_ == "z" else 0]
        g.wa("Talerz", _plus(v, d), 0.45, sr, kolor, os_=os_)


def lawka(g, v, szer=6.0, kolor=DREWNO_J):
    u = g.w(g._p(v), g.ry)
    u.kl("Siedzisko", [0, 1.4, 0], [szer, 0.35, 1.6], kolor, m="WoodPlanks", kol=True)
    u.kl("Oparcie", [0, 2.6, -0.7], [szer, 0.9, 0.3], kolor, m="WoodPlanks")
    for sx in (-1, 1):
        u.kl("Noga", [sx * (szer / 2 - 0.5), 0.7, 0], [0.4, 1.4, 1.4], DREWNO)
        u.kl("Slupek", [sx * (szer / 2 - 0.5), 2.2, -0.7], [0.35, 1.7, 0.35], DREWNO)


def latarnia(g, v, wys=8.5, kolor=LAMPION):
    u = g.w(g._p(v), g.ry)
    u.kl("Cokol", [0, 0.4, 0], [1.4, 0.8, 1.4], KAMIEN_C, kol=True)
    u.wa("Slup", [0, wys / 2, 0], wys, 0.5, DREWNO, kol=True)
    u.kl("Wysiegnik", [0, wys - 0.3, 1.0], [0.3, 0.3, 2.4], DREWNO)
    u.kl("Sznur", [0, wys - 0.8, 1.9], [0.1, 0.8, 0.1], TUSZ)
    u.kl("Daszek", [0, wys - 1.25, 1.9], [1.5, 0.25, 1.5], CZERWIEN)
    u.kl("Lampion", [0, wys - 2.05, 1.9], [1.1, 1.4, 1.1], kolor, m="Neon")
    u.kl("Denko", [0, wys - 2.85, 1.9], [0.8, 0.2, 0.8], TUSZ)


def choragiew(g, v, kolor, wys=9.0, znak=KREM):
    """Słup z poprzeczką i sztandarem w kolorze statystyki (front ku +z)."""
    u = g.w(g._p(v), g.ry)
    u.wa("Maszt", [0, wys / 2, 0], wys, 0.4, DREWNO, kol=True)
    u.kl("Poprzeczka", [0, wys - 0.6, 0.1], [3.4, 0.3, 0.3], DREWNO)
    u.kl("Sztandar", [0, wys - 3.0, 0.3], [3.0, 4.4, 0.15], kolor, m="Fabric")
    u.kl("Znak", [0, wys - 2.8, 0.42], [1.3, 1.3, 0.1], znak, rz=45)
    u.ku("Galka", [0, wys + 0.2, 0], 0.7, ZLOTO)


def manekin(g, v, ry=0.0):
    """Manekin treningowy: słomiany korpus na palu, ramiona z belki, tarcza na piersi, stary hełm."""
    u = g.w(g._p(v), g.ry + ry)
    u.wa("Podstawa", [0, 0.2, 0], 0.4, 2.6, DREWNO, kol=True)
    u.wa("Pal", [0, 2.0, 0], 4.0, 0.5, DREWNO_S, kol=True)
    u.kl("Korpus", [0, 4.0, 0], [2.2, 2.8, 1.5], SLOMA, kol=True)
    u.kl("Ramiona", [0, 4.9, 0], [5.0, 0.5, 0.5], DREWNO_S)
    u.ku("Glowa", [0, 6.3, 0], 1.8, SLOMA)
    u.kl("Helm", [0, 7.0, 0], [2.0, 0.6, 2.0], METAL_C, m="Metal")
    u.wa("Tarcza", [0, 4.1, 0.8], 0.12, 1.6, CZERWIEN, os_="z")
    u.wa("Srodek", [0, 4.1, 0.86], 0.12, 0.7, KREM, os_="z")
    for i, dy in enumerate((3.0, 5.1)):
        u.kl("Powroz%d" % (i + 1), [0, dy, 0], [2.3, 0.2, 1.6], DREWNO)


def stojak_mieczy(g, v, ry=0.0, ile=4):
    u = g.w(g._p(v), g.ry + ry)
    szer = 1.5 * ile + 1
    for sx in (-1, 1):
        u.kl("Noga", [sx * szer / 2, 1.6, 0], [0.4, 3.2, 1.4], DREWNO, kol=True)
    u.kl("BelkaDol", [0, 0.9, 0], [szer, 0.4, 0.8], DREWNO_S, kol=True)
    u.kl("BelkaGora", [0, 3.0, 0], [szer, 0.3, 0.5], DREWNO_S)
    for i in range(ile):
        miecz(u, [-szer / 2 + 1.25 + 1.5 * i, 1.7, 0.35], dl=2.6 + 0.3 * (i % 2), kolor=METAL if i % 2 else DREWNO_J, rz=180)


def stojak_tarcz(g, v, kolory, ry=0.0):
    u = g.w(g._p(v), g.ry + ry)
    szer = 2.6 * len(kolory) + 0.6
    for sx in (-1, 1):
        u.kl("Noga", [sx * szer / 2, 2.0, 0], [0.4, 4.0, 1.4], DREWNO, kol=True)
    u.kl("Belka", [0, 3.7, 0], [szer, 0.4, 0.5], DREWNO_S)
    u.kl("Polka", [0, 0.8, 0], [szer, 0.3, 1.2], DREWNO_S, kol=True)
    for i, c in enumerate(kolory):
        x = -szer / 2 + 1.6 + 2.6 * i
        if i % 2:
            u.kl("Tarcza", [x, 2.3, 0.4], [1.9, 2.5, 0.25], c)
            u.kl("Pas", [x, 2.3, 0.55], [0.4, 2.5, 0.08], KREM)
        else:
            u.wa("Tarcza", [x, 2.3, 0.4], 0.25, 2.2, c, os_="z")
            u.wa("Pas", [x, 2.3, 0.55], 0.08, 1.4, KREM, os_="z")
        u.ku("Umbo", [x, 2.3, 0.6], 0.6, METAL, m="Metal")


def zbroja(g, v, ry=0.0, kolor=METAL):
    u = g.w(g._p(v), g.ry + ry)
    u.wa("Podstawa", [0, 0.2, 0], 0.4, 2.4, DREWNO, kol=True)
    u.kl("Pal", [0, 2.6, 0], [0.4, 5.2, 0.4], DREWNO_S)
    u.kl("Napiersnik", [0, 3.9, 0], [2.4, 2.4, 1.4], kolor, m="Metal", kol=True)
    u.kl("Pas", [0, 2.8, 0], [2.5, 0.35, 1.5], DREWNO)
    for sx in (-1, 1):
        u.kl("Naramiennik", [sx * 1.6, 4.8, 0], [1.0, 0.8, 1.5], METAL_C, m="Metal")
    u.kl("Helm", [0, 6.0, 0], [1.7, 1.5, 1.7], kolor, m="Metal")
    u.kl("Wizjer", [0, 6.0, 0.86], [1.2, 0.25, 0.06], TUSZ)
    u.kl("Pioropusz", [0, 7.1, -0.1], [0.3, 0.9, 1.4], CZERWIEN, m="Fabric")


def stos_klod(g, v, ry=0.0, dl=5.0, sr=1.3):
    u = g.w(g._p(v), g.ry + ry)
    for rzad, ile in enumerate((3, 2, 1)):
        for i in range(ile):
            x = (i - (ile - 1) / 2.0) * (sr + 0.05)
            u.wa("Kloda", [0, sr / 2 + rzad * (sr * 0.87), x], dl, sr, "8C5A3C" if (i + rzad) % 2 else "7A4C30", os_="x",
                 m="WoodPlanks", kol=rzad == 0)
            u.wa("Sloj", [dl / 2 + 0.03, sr / 2 + rzad * (sr * 0.87), x], 0.06, sr - 0.35, DREWNO_J, os_="x")
    for s in (-1, 1):
        u.kl("Kolek", [s * (dl / 2 - 0.8), 0.8, 2.25], [0.35, 1.6, 0.35], DREWNO)


def pien_z_siekiera(g, v, ry=0.0):
    u = g.w(g._p(v), g.ry + ry)
    u.wa("Pien", [0, 0.8, 0], 1.6, 2.2, "8C5A3C", m="WoodPlanks", kol=True)
    u.wa("Sloje", [0, 1.62, 0], 0.05, 1.7, DREWNO_J)
    u.kl("Stylisko", [0.2, 2.8, 0], [0.25, 2.6, 0.25], DREWNO, rz=-22)
    u.kl("Ostrze", [-0.15, 1.95, 0], [1.0, 0.8, 0.15], "D8DEE9", m="Metal", rz=-22)


def kwiat(g, v, kolor, wys=1.1):
    g.kl("Lodyga", [v[0], v[1] + wys / 2, v[2]], [0.15, wys, 0.15], LISC_C)
    g.kl("Kwiat", [v[0], v[1] + wys + 0.2, v[2]], [0.6, 0.45, 0.6], kolor)


def krysztal(g, v, kolor="B85CFF"):
    u = g.w(g._p(v), g.ry)
    u.kl("Skala", [0, 0.3, 0], [2.0, 0.6, 1.6], KAMIEN_C, m="Slate")
    for i, (dx, dz, h, rz) in enumerate(((0, 0, 2.6, 0), (-0.6, 0.2, 1.6, 18), (0.6, -0.1, 1.9, -15))):
        u.kl("Krysztal", [dx, 0.5 + h / 2, dz], [0.6, h, 0.6], kolor, m="Neon", t=0.15, rz=rz)


def widz(g, v, ubranie, wlosy):
    g.kl("Korpus", [v[0], v[1] + 0.8, v[2]], [1.5, 1.6, 1.0], ubranie)
    g.kl("Glowa", [v[0], v[1] + 2.2, v[2]], [1.2, 1.2, 1.2], SKORA)
    g.kl("Wlosy", [v[0], v[1] + 2.9, v[2] - 0.1], [1.3, 0.3, 1.2], wlosy)
    g.kl("Oczy", [v[0], v[1] + 2.3, v[2] + 0.62], [0.8, 0.22, 0.06], TUSZ)


def trybuna(g, v, szer=20.0, dach=(CZERWIEN, KREM)):
    """Trybunka z trzema stopniami, dachem w pasy i kilkoma widzami; przód ku +z (ku stanowiskom)."""
    u = g.w(g._p(v), g.ry)
    for i in range(3):
        u.kl("Stopien", [0, 0.6 * (i + 1), -1.3 - 2.6 * i], [szer, 1.2 * (i + 1), 2.6], DREWNO_S, m="WoodPlanks", kol=True)
        u.kl("Lawa", [0, 1.2 * (i + 1) + 0.1, -0.9 - 2.6 * i], [szer - 0.8, 0.2, 1.1], (ZLOTO, NIEBIESKI, CZERWIEN)[i])
    u.kl("Tyl", [0, 3.4, -8.1], [szer, 6.8, 0.6], DREWNO, m="WoodPlanks", kol=True)
    for sx in (-1, 1):
        u.kl("Bok", [sx * (szer / 2 - 0.3), 2.2, -4.2], [0.6, 4.4, 7.2], DREWNO, m="WoodPlanks", kol=True)
        u.kl("Slup", [sx * (szer / 2 - 0.4), 4.2, -0.4], [0.6, 8.4, 0.6], DREWNO, kol=True)
        u.ku("Galka", [sx * (szer / 2 - 0.4), 8.9, -0.4], 0.9, ZLOTO)
    n = 8
    for i in range(n):
        u.kl("Dach", [-szer / 2 + (i + 0.5) * szer / n, 8.6, -4.2], [szer / n, 0.25, 9.2], dach[i % 2], m="Fabric", rx=7)
    u.kl("Okap", [0, 7.85, 0.35], [szer + 0.4, 0.5, 0.3], ZLOTO)
    kolory = (CZERWIEN, NIEBIESKI, ZIELEN, FIOLET, POMARANCZ, TURKUS)
    for i, (dx, rzad) in enumerate(((-7.5, 0), (-3.2, 1), (-0.5, 0), (2.4, 2), (5.8, 1), (8.0, 0), (-6.0, 2))):
        widz(u, [dx, 1.2 * (rzad + 1) + 0.2, -1.0 - 2.6 * rzad], kolory[i % 6], (TUSZ, DREWNO, ZLOTO)[i % 3])


# ------------------------------------------------------------------------------------------------ arena
def _podloga(g, sz, gl):
    a = 8.0
    for i in range(int(sz / a)):
        for j in range(int(gl / a)):
            if (i + j) % 2 == 0:
                g.kl("Plytka", [-sz / 2 + (i + 0.5) * a, 0.025, -gl / 2 + (j + 0.5) * a], [a, 0.05, a], "CBB188")
    for n, p, s in (("PasN", [0, 0.03, -gl / 2 + 2.2], [sz - 2, 0.06, 0.8]), ("PasS", [0, 0.03, gl / 2 - 2.2], [sz - 2, 0.06, 0.8])):
        g.kl(n, p, s, "A98C63")
    for i in range(8):  # róża kierunków wokół punktu przybycia
        k = math.radians(45 * i)
        g.kl("Promien", [math.sin(k) * 6.4, 0.11, 14 + math.cos(k) * 6.4], [1.3, 0.06, 1.3], ZLOTO if i % 2 else KREM, ry=45)


def _ramy(g, kolory):
    for gra, (x0, x1, z0, z1) in RAMY.items():
        u = g.w([0, 0, 0], 0, gra)
        c = kolory[gra]
        u.kl("RamaN", [(x0 + x1) / 2, 0.07, z0], [x1 - x0, 0.1, 0.7], c)
        u.kl("RamaS", [(x0 + x1) / 2, 0.07, z1], [x1 - x0, 0.1, 0.7], c)
        u.kl("RamaW", [x0, 0.07, (z0 + z1) / 2], [0.7, 0.1, z1 - z0], c)
        u.kl("RamaE", [x1, 0.07, (z0 + z1) / 2], [0.7, 0.1, z1 - z0], c)
        for x in (x0, x1):
            for z in (z0, z1):
                u.kl("Naroznik", [x, 0.09, z], [1.7, 0.14, 1.7], KREM)


def _ogrodzenie(g, sz, gl):
    """Słupki z daszkami na murkach, poręcz między nimi, girlandy chorągiewek wzdłuż muru północnego i bocznych,
    flagi na słupach narożnych."""
    krok = 16.0
    xs = [-sz / 2 + 8 + krok * i for i in range(int((sz - 16) / krok) + 1)]
    for strona, z in (("N", -gl / 2 + 0.5), ("S", gl / 2 - 0.5)):
        u = g.w([0, 0, 0], 0, "Mur" + strona)
        for x in xs:
            u.kl("Slupek", [x, 3.7, z], [0.8, 2.4, 0.8], DREWNO)
            u.kl("Daszek", [x, 5.05, z], [1.2, 0.3, 1.2], ZLOTO)
        for a, b in zip(xs, xs[1:]):
            u.kl("Porecz", [(a + b) / 2, 4.3, z], [krok - 0.8, 0.3, 0.3], DREWNO_S)
            if strona == "N":
                girlanda(u, [a, 4.9, z + 0.2], [b, 4.9, z + 0.2], n=6, ugiecie=0.9)
    zs = [-gl / 2 + 14, 0, gl / 2 - 14]
    for strona, x in (("W", -sz / 2 + 0.5), ("E", sz / 2 - 0.5)):
        u = g.w([0, 0, 0], 0, "Mur" + strona)
        for z in zs:
            u.kl("Slupek", [x, 3.7, z], [0.8, 2.4, 0.8], DREWNO)
            u.kl("Daszek", [x, 5.05, z], [1.2, 0.3, 1.2], ZLOTO)
        for a, b in zip(zs, zs[1:]):
            u.kl("Porecz", [x, 4.3, (a + b) / 2], [0.3, 0.3, b - a - 0.8], DREWNO_S)
            girlanda(u, [x, 4.9, a], [x, 4.9, b], n=5, ugiecie=0.8)
    u = g.w([0, 0, 0], 0, "Flagi")
    for i, (sx, sz_) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        px, pz = sx * (sz / 2 - 2), sz_ * (gl / 2 - 2)
        u.kl("Maszt", [px, 11.2, pz], [0.3, 5.0, 0.3], DREWNO)
        u.kl("Flaga", [px - sx * 1.35, 12.7, pz], [2.4, 1.6, 0.12], (CZERWIEN, NIEBIESKI, ZIELEN, FIOLET)[i], m="Fabric")
        u.ku("Galka", [px, 13.9, pz], 0.6, ZLOTO)


def _brama(g):
    """Brama przy wyjściu (istniejące filary i belka zostają): pylony z flagami, szyld z nazwą, skrzyżowane miecze,
    lampiony pod belką, girlandy do muru. Przejście i podpowiedź E wolne."""
    for sx in (-1, 1):
        g.kl("Pylon", [sx * 5.6, 4.5, 24.6], [1.8, 9.0, 1.8], "7A5C44", kol=True)
        g.kl("Cokol", [sx * 5.6, 0.5, 24.6], [2.2, 1.0, 2.2], KAMIEN_C, kol=True)
        g.kl("Czapa", [sx * 5.6, 9.3, 24.6], [2.3, 0.6, 2.3], ZLOTO)
        g.kl("Maszt", [sx * 5.6, 11.4, 24.6], [0.3, 3.6, 0.3], DREWNO)
        g.kl("Flaga", [sx * 5.6 + sx * 1.2, 12.4, 24.6], [2.1, 1.4, 0.12], CZERWIEN if sx < 0 else NIEBIESKI, m="Fabric")
        g.kl("Hak", [sx * 5.6, 7.6, 23.4], [0.2, 0.2, 0.9], TUSZ)
        g.kl("Lampion", [sx * 5.6, 6.8, 23.2], [0.9, 1.2, 0.9], LAMPION, m="Neon")
        girlanda(g, [sx * 5.6, 9.0, 24.6], [sx * 24, 5.0, 27.4], n=7, ugiecie=1.0)
    g.kl("Luk", [0, 9.4, 24.6], [11.2, 0.8, 1.2], CZERWIEN)
    g.kl("Szyld", [0, 11.0, 24.6], [9.6, 2.4, 0.5], KREM,
         napis={"tekst": NAPIS_ARENY, "strona": "Front", "px": 30, "kolor": TUSZ})
    g.kl("RamaSzyldu", [0, 11.0, 24.75], [10.2, 3.0, 0.3], DREWNO)
    g.kl("MieczA", [0, 13.6, 24.6], [0.4, 3.4, 0.2], METAL, m="Metal", rz=40)
    g.kl("MieczB", [0, 13.6, 24.6], [0.4, 3.4, 0.2], METAL, m="Metal", rz=-40)
    g.wa("Herb", [0, 13.4, 24.45], 0.2, 1.6, ZLOTO, os_="z")


def _tablica_wynikow(g, D):
    """Tablica wyników jako dekoracja pod murem północnym: nazwa areny i sześć statystyk z kolorowymi paskami
    (same nazwy i kolory z danych — bez liczb, żeby nie udawała żywych wyników)."""
    u = g.w([0, 0, -25.4], 0)
    for sx in (-1, 1):
        u.kl("Slup", [sx * 8.6, 6.0, 0], [0.9, 12.0, 0.9], DREWNO, kol=True)
        u.ku("Galka", [sx * 8.6, 12.4, 0], 1.1, ZLOTO)
        u.kl("Lampion", [sx * 8.6, 9.4, 0.9], [0.9, 1.2, 0.9], LAMPION, m="Neon")
    u.kl("Plyta", [0, 7.6, 0], [16.4, 8.4, 0.5], "3A2E3F", kol=True)
    u.kl("Rama", [0, 7.6, -0.2], [17.2, 9.2, 0.3], DREWNO)
    u.kl("Tytul", [0, 10.7, 0.3], [13.0, 1.6, 0.2], ZLOTO, napis={"tekst": NAPIS_ARENY, "strona": "Back", "px": 30, "kolor": TUSZ})
    for i, s in enumerate(D["statystyki"]):
        y = 9.0 - i * 0.95
        u.kl("Kolor", [-6.9, y, 0.3], [0.9, 0.7, 0.2], s["kolor"])
        u.kl("Nazwa", [-3.4, y, 0.3], [5.4, 0.7, 0.2], KREM, napis={"tekst": s["nazwa"].upper(), "strona": "Back", "px": 30,
                                                                    "kolor": TUSZ})
        u.kl("Pasek", [0.2 + (2.0 + (i * 37 % 5) * 0.8) / 2, y, 0.3], [2.0 + (i * 37 % 5) * 0.8, 0.5, 0.2], s["kolor"], m="Neon")
        u.kl("Gwiazdka", [7.0, y, 0.3], [0.5, 0.5, 0.2], ZLOTO, rz=45)
    u.kl("Daszek", [0, 12.2, 0.4], [18.0, 0.4, 2.0], CZERWIEN, m="Fabric", rx=12)


def _zaplecze(g, kolory):
    """Pas pod murem północnym (tło kadrów): trybunki, stojaki z bronią i ciężarkami, latarnie z lampionami, sztandary
    w kolorach statystyk, beczki i skrzynie; ławki pod murem południowym w przerwach między stanowiskami."""
    trybuna(g.w([-44, 0, -16.6], 0, "TrybunaW"), [0, 0, 0], dach=(CZERWIEN, KREM))
    trybuna(g.w([44, 0, -16.6], 0, "TrybunaE"), [0, 0, 0], dach=(NIEBIESKI, KREM))
    u = g.w([0, 0, 0], 0, "Zbrojownia")
    stojak_mieczy(u, [-13.5, 0, -25.0], ile=4)
    stojak_mieczy(u, [13.5, 0, -25.0], ile=4)
    for sx in (-1, 1):  # stojak z ciężarkami: trzy hantle na półkach, sztanga i odważniki na ziemi
        w = u.w([sx * 22.5, 0, -24.6], 0)
        for s2 in (-1, 1):
            w.kl("Bok", [s2 * 2.6, 1.7, 0], [0.4, 3.4, 1.6], METAL_C, m="Metal", kol=True)
        for i in range(3):
            w.kl("Polka", [0, 0.8 + i * 1.1, 0], [5.2, 0.2, 1.4], DREWNO_S)
            for j in range(2):
                hantel(w, [-1.2 + 2.4 * j, 1.25 + i * 1.1, 0.1], dl=1.9, sr=0.7 + 0.12 * i, kolor=(CZERWIEN, NIEBIESKI, ZLOTO)[i])
        hantel(w, [0, 0.75, 2.6], dl=6.0, sr=1.5, kolor=TUSZ)
        for j, dx in enumerate((-3.6, 3.7)):
            w.ku("Odwaznik", [dx, 0.7, 1.6], 1.4, METAL_C, m="Metal", kol=True)
            w.kl("Ucho", [dx, 1.55, 1.6], [0.9, 0.3, 0.3], METAL_C, m="Metal")
    u = g.w([0, 0, 0], 0, "Latarnie")
    xs = (-112, -84, -60, -29, 29, 60, 84, 124)
    for x in xs:
        latarnia(u, [x, 0, -21.5])
    u = g.w([0, 0, 0], 0, "Sztandary")
    for gra, (x0, x1, _z0, _z1) in RAMY.items():
        for x in (x0 + 2.5, x1 - 2.5):
            if abs(x) < 20 or 31 < abs(x) < 56:   # miejsce trybun i tablicy wyników
                continue
            choragiew(u, [x, 0, -26.0], kolory[gra])
    u = g.w([0, 0, 0], 0, "Zapasy")
    for i, (x, z) in enumerate(((-75, -24.5), (78, -24.5), (-108, -24.5), (100, -24.5))):
        beczka(u, [x, 0, z], kolor=DREWNO_S if i % 2 else "A0522D")
        skrzynia(u, [x + 2.6, 0, z + 0.2], a=1.8, ry=12 * (1 if i % 2 else -1))
        skrzynia(u, [x + 2.5, 1.8, z + 0.1], a=1.3, kolor="C48A52", ry=-20)
        u.kl("Siano", [x - 2.8, 0.7, z], [2.6, 1.4, 1.8], SLOMA, kol=True)
        u.kl("Powroz", [x - 2.8, 0.7, z], [0.3, 1.5, 1.9], DREWNO)
    u = g.w([0, 0, 0], 0, "Lawki")
    for i, x in enumerate((-81.5, -41.5, 46.5, 86.5)):
        w = u.w([x, 0, 25.4], 180)
        lawka(w, [0, 0, 0], szer=5.4)
        w.kl("Recznik", [1.2, 1.62, 0.1], [1.2, 0.12, 1.4], (CZERWIEN, NIEBIESKI, ZIELEN, FIOLET)[i], m="Fabric")
        w.wa("Wiadro", [-3.9, 0.6, 0], 1.2, 1.3, METAL, m="Metal")
        w.wa("Woda", [-3.9, 1.18, 0], 0.06, 1.1, "2389D0")


# ------------------------------------------------------------------------------------------------ stanowiska
def _sila(g, pd):
    """Siła „Ciosy”: stojak z mieczami, dwa manekiny treningowe, beczka z drewnianymi mieczami, bele siana, kowadło."""
    x0 = pd[0]
    stojak_mieczy(g, [x0 - 12.5, 0, -11.0], ry=20, ile=3)
    manekin(g, [x0 - 13.5, 0, 1.0], ry=60)   # z boku kadru: tarcza manekina nie może stać za strefą ciosu „lewo”
    manekin(g, [x0 + 12.0, 0, -9.0], ry=-20)
    u = g.w([x0 + 10.5, 0, -13.5], -15)
    beczka(u, [0, 0, 0], sr=2.0, wys=2.2)
    for i, (dx, dz, rz) in enumerate(((-0.4, 0.2, 8), (0.35, -0.2, -10), (0, 0.4, 3))):
        u.kl("MieczDrewniany", [dx, 3.2, dz], [0.35, 2.6, 0.14], DREWNO_J, m="WoodPlanks", rz=rz)
        u.kl("Jelec", [dx, 2.5, dz], [1.0, 0.25, 0.25], DREWNO, rz=rz)
    for i, (dx, dz, ry) in enumerate(((-15.0, -7.0, 10), (-17.0, -6.4, -8), (-15.9, -6.7, 4))):
        g.kl("Siano", [x0 + dx, 0.7 + (1.4 if i == 2 else 0), dz], [2.4, 1.4, 1.6], SLOMA, kol=i < 2, ry=ry)
    u = g.w([x0 + 9.5, 0, -5.0], 30)
    u.kl("Pniak", [0, 0.6, 0], [1.6, 1.2, 1.6], DREWNO, m="WoodPlanks", kol=True)
    u.kl("Kowadlo", [0, 1.55, 0], [2.2, 0.7, 1.0], METAL_C, m="Metal", kol=True)
    u.kl("Rog", [1.4, 1.65, 0], [0.9, 0.4, 0.6], METAL_C, m="Metal")
    u.kl("Mlot", [-0.3, 2.1, 0], [1.0, 0.5, 0.6], METAL, m="Metal")
    u.kl("Trzonek", [0.5, 2.1, 0.6], [0.2, 0.2, 1.8], DREWNO)
    for sx in (-1, 1):  # proporce na słupkach szyldu
        g.kl("Proporzec", [x0 + sx * 6.3, 8.6, -9.5], [1.6, 2.4, 0.12], CZERWIEN, m="Fabric")


def _pancerz(g, pd):
    """Pancerz „Blok”: stojak z tarczami, dwie zbroje na stojakach, ruiny kolumn i głazy przy golemie, łańcuchy."""
    x0 = pd[0]
    stojak_tarcz(g, [x0 - 14.5, 0, -8.5], (NIEBIESKI, CZERWIEN, ZLOTO), ry=15)
    zbroja(g, [x0 + 11.5, 0, -7.5], ry=-20)
    zbroja(g, [x0 - 11.0, 0, -2.0], ry=30, kolor="B08D57")
    for i, (dx, wys) in enumerate(((-8.6, 5.0), (8.6, 3.2))):
        u = g.w([x0 + dx, 0, -8.5], 0, "Kolumna%d" % (i + 1))
        u.kl("Baza", [0, 0.4, 0], [2.6, 0.8, 2.6], KAMIEN_C, m="Slate", kol=True)
        u.wa("Trzon", [0, 0.8 + wys / 2, 0], wys, 1.8, KAMIEN, m="Slate", kol=True)
        u.kl("Odlamek", [1.9, 0.5, 1.2], [1.4, 1.0, 1.2], KAMIEN, m="Slate", ry=25, kol=True)
        u.kl("Mech", [0, 0.8 + wys + 0.1, 0], [1.5, 0.2, 1.5], LISC_C)
    for i, (dx, dz, a) in enumerate(((-6.0, -10.5, 1.8), (-4.4, -11.2, 1.2), (5.6, -11.0, 2.0), (7.4, -10.2, 1.1), (0.5, -12.0, 1.5))):
        g.kl("Glaz", [x0 + dx, a / 2, dz - 1], [a * 1.2, a, a], KAMIEN if i % 2 else KAMIEN_C, m="Slate", ry=17 * i, kol=True)
    xs = (-9.5, -4.5, 4.5, 9.5)
    for dx in xs:
        g.wa("Pacholek", [x0 + dx, 0.9, -13.6], 1.8, 0.7, METAL_C, m="Metal", kol=True)
        g.ku("Kula", [x0 + dx, 2.0, -13.6], 0.9, ZLOTO)
    for a, b in ((xs[0], xs[1]), (xs[2], xs[3])):
        girlanda(g, [x0 + a, 1.8, -13.6], [x0 + b, 1.8, -13.6], n=0, ugiecie=0.5)
    for sx in (-1, 1):
        g.kl("Proporzec", [x0 + sx * 6.3, 10.6, -3.5], [1.6, 2.4, 0.12], NIEBIESKI, m="Fabric")


def _kondycja(g, pd, kolor):
    """Kondycja „Bieżnia”: za stanowiskiem tor biegowy z bandami, płotkami, pachołkami i bramą startu; z boku beczka
    z wodą, wieszak z ręcznikami, klepsydra i hantle."""
    x0 = pd[0]
    u = g.w([x0, 0, -8.5], 0, "Tor")
    dl, sz = 34.0, 9.0
    u.kl("Nawierzchnia", [0, 0.045, 0], [dl, 0.09, sz], "C4623A")
    for i in range(4):
        u.kl("Linia", [0, 0.11, -sz / 2 + i * sz / 3], [dl, 0.05, 0.25], KREM)
    for i in range(6):
        u.kl("Meta", [dl / 2 - 2.0 + (i % 2) * 0.6, 0.12, -3.75 + i * 1.5], [0.6, 0.05, 1.5], TUSZ if i % 2 else KREM)
    n = 8
    for strona, z in (("N", -sz / 2 - 0.5), ("S", sz / 2 + 0.5)):
        for i in range(n):
            u.kl("Banda" + strona, [-dl / 2 + (i + 0.5) * dl / n, 0.45, z], [dl / n, 0.9, 0.5], CZERWIEN if i % 2 else KREM,
                 kol=True)
    for i, x in enumerate((-9.0, 0.0, 9.0)):
        for z in (-3.0, 0.0, 3.0)[i % 2:i % 2 + 2]:
            for s in (-1, 1):
                u.kl("PlotekNoga", [x, 0.9, z + s * 1.2], [0.25, 1.8, 0.25], KREM)
            u.kl("PlotekPoprzeczka", [x, 1.75, z], [0.3, 0.35, 2.7], CZERWIEN if i % 2 else NIEBIESKI)
    for i in range(6):
        px, pz = -dl / 2 + 3 + i * 5.6, (-1.5, 1.5)[i % 2]
        u.kl("PacholekPodstawa", [px, 0.2, pz], [1.0, 0.16, 1.0], POMARANCZ)
        u.kl("Pacholek", [px, 0.75, pz], [0.55, 1.0, 0.55], POMARANCZ)
        u.kl("PacholekPas", [px, 0.85, pz], [0.6, 0.25, 0.6], KREM)
    for s in (-1, 1):
        u.kl("BramaSlup", [-dl / 2 + 1.2, 3.6, s * (sz / 2 + 0.5)], [0.6, 7.2, 0.6], DREWNO, kol=True)
    u.kl("BramaBaner", [-dl / 2 + 1.2, 6.6, 0], [0.3, 1.6, sz + 1.6], kolor, m="Fabric")
    for i in range(8):
        u.kl("BramaKratka", [-dl / 2 + 1.38, 6.2 + (i % 2) * 0.8, -3.85 + i * 1.1], [0.1, 0.8, 1.1], TUSZ if i % 2 else KREM)
    u = g.w([x0 - 12.0, 0, 5.0], 20, "Zaplecze")
    beczka(u, [0, 0, 0], kolor="2E6FA8")
    u.wa("Woda", [0, 2.42, 0], 0.06, 1.9, "2389D0")
    u.kl("Chochla", [0.5, 2.9, 0], [0.2, 1.2, 0.2], DREWNO, rz=-20)
    for s in (-1, 1):
        u.kl("WieszakNoga", [s * 1.6, 1.6, 3.0], [0.3, 3.2, 0.3], DREWNO, kol=True)
    u.kl("WieszakDrazek", [0, 3.1, 3.0], [3.6, 0.25, 0.25], DREWNO_S)
    for i, c in enumerate((CZERWIEN, KREM, NIEBIESKI)):
        u.kl("Recznik", [-1.0 + i, 2.4, 3.0], [0.8, 1.5, 0.35], c, m="Fabric")
    u.kl("KlepsydraDol", [3.4, 0.2, 0.4], [1.6, 0.4, 1.6], DREWNO, kol=True)
    u.kl("KlepsydraSzklo", [3.4, 1.5, 0.4], [1.0, 2.2, 1.0], "BFE9FF", t=0.45)
    u.kl("KlepsydraPiasek", [3.4, 0.9, 0.4], [0.8, 0.9, 0.8], ZLOTO, m="Neon")
    u.kl("KlepsydraGora", [3.4, 2.8, 0.4], [1.6, 0.4, 1.6], DREWNO)
    hantel(u, [2.4, 0.5, -2.2], dl=2.2, sr=1.0, kolor=CZERWIEN)
    hantel(u, [3.2, 0.5, -3.6], dl=2.2, sr=1.0, kolor=NIEBIESKI, os_="z")


def _zrecznosc(g, pd, st):
    """Zręczność „Kłody”: stosy kłód, pień z siekierą, kozioł z kłodą i piłą, kołki z czerwonymi czapami po stronie północnej placu,
    tor równowagi z pniaków, tarcza do rzutów pod murem."""
    sl = _plus(pd, st["slup"])
    stos_klod(g, [sl[0] + 15.0, 0, -15.5], ry=15)
    stos_klod(g, [sl[0] - 13.5, 0, -17.0], ry=-10, dl=4.2)
    pien_z_siekiera(g, [sl[0] - 16.5, 0, -9.0])
    pien_z_siekiera(g, [sl[0] + 13.5, 0, -8.0], ry=140)
    u = g.w([sl[0] + 8.0, 0, -18.5], -12, "Koziol")
    for sx in (-1, 1):
        u.kl("NogaA", [sx * 1.6, 1.0, 0], [0.3, 2.6, 0.3], DREWNO, rz=24)
        u.kl("NogaB", [sx * 1.6, 1.0, 0], [0.3, 2.6, 0.3], DREWNO, rz=-24)
    u.wa("Kloda", [0, 2.3, 0], 5.4, 1.1, "8C5A3C", os_="x", m="WoodPlanks")
    u.kl("Pila", [0.6, 3.2, 0], [2.6, 0.7, 0.08], "D8DEE9", m="Metal", rz=-10)
    u.kl("Uchwyt", [2.1, 3.1, 0], [0.5, 0.9, 0.25], DREWNO, rz=-10)
    r = st["ramie"] + 2.0
    for kat in (28, 50, 72, 108, 130, 152):  # same kołki — lina między nimi wchodziłaby pudłem w koło gry
        a = math.radians(kat)
        p = [sl[0] + math.cos(a) * r, 0, sl[2] - math.sin(a) * r]
        g.wa("Kolek", [p[0], 0.7, p[2]], 1.4, 0.6, DREWNO, m="WoodPlanks")
        g.wa("KolekCzapa", [p[0], 1.45, p[2]], 0.12, 0.75, CZERWIEN)
    u = g.w([sl[0] - 18.5, 0, -14.0], 0, "TorRownowagi")
    for i, (dz, h) in enumerate(((0, 0.8), (-2.6, 1.3), (-5.2, 1.8), (-10.6, 1.8))):
        u.wa("Pniak", [0, h / 2, dz], h, 1.6, "8C5A3C" if i % 2 else "7A4C30", m="WoodPlanks", kol=True)
    u.wa("Belka", [0, 2.1, -7.9], 5.6, 0.7, DREWNO_S, os_="z", m="WoodPlanks", kol=True)
    u = g.w([sl[0] + 4.0, 0, -26.2], 0, "TarczaRzutow")
    u.kl("Stojak", [0, 2.0, 0], [0.5, 4.0, 0.5], DREWNO)
    for i, (sr, c) in enumerate(((4.4, KREM), (3.0, CZERWIEN), (1.5, ZLOTO))):
        u.wa("Krag", [0, 4.2, 0.3 + i * 0.08], 0.2, sr, c, os_="z")
    u.kl("Toporek", [0.9, 4.9, 0.9], [0.2, 0.2, 1.4], DREWNO, rx=-20)
    u.kl("ToporekOstrze", [0.9, 4.75, 0.55], [0.12, 0.8, 0.6], "D8DEE9", m="Metal", rx=-20)


def _inteligencja(g, pd, st):
    """Inteligencja „Runy”: pulpit z księgą przy magu, regał z księgami i zwojami, kryształy, świece na kolumnach,
    krąg na podłodze wokół podestu, globus."""
    sc = _plus(pd, st["sciana"])
    mg = _plus(pd, st["mag"])
    u = g.w([mg[0] - 0.6, 0, mg[2] + 4.6], 40, "Pulpit")
    u.kl("Stopa", [0, 0.2, 0], [1.8, 0.4, 1.4], DREWNO, kol=True)
    u.kl("Noga", [0, 1.9, 0], [0.5, 3.2, 0.5], DREWNO_S, kol=True)
    u.kl("Blat", [0, 3.6, 0], [2.4, 0.25, 1.6], DREWNO)
    u.kl("Okladka", [0, 3.8, 0], [2.0, 0.14, 1.3], FIOLET)
    for sx in (-1, 1):
        u.kl("Strona", [sx * 0.5, 3.92, 0], [0.9, 0.1, 1.15], KREM, rz=-sx * 6)
    u.kl("Pioro", [1.0, 4.4, -0.3], [0.1, 1.0, 0.25], KREM, rz=-25)
    u.kl("Swieca", [-1.0, 4.1, -0.5], [0.3, 0.7, 0.3], KREM)
    u.kl("Plomyk", [-1.0, 4.65, -0.5], [0.22, 0.4, 0.22], LAMPION, m="Neon")
    u = g.w([sc[0] - 13.0, 0, sc[2] - 2.6], 25, "Regal")
    u.kl("Plecy", [0, 3.0, -0.6], [5.0, 6.0, 0.3], DREWNO, kol=True)
    for sx in (-1, 1):
        u.kl("Bok", [sx * 2.5, 3.0, 0], [0.3, 6.0, 1.5], DREWNO, kol=True)
    for i in range(4):
        u.kl("Polka", [0, 0.3 + i * 1.85, 0], [5.0, 0.25, 1.4], DREWNO_S)
    kol = (CZERWIEN, NIEBIESKI, ZIELEN, ZLOTO, FIOLET, TURKUS, POMARANCZ)
    for i in range(3):
        x = -2.0
        for j in range(5):
            szer = 0.5 + ((i * 3 + j * 5) % 3) * 0.2
            u.kl("Ksiega", [x + szer / 2, 0.45 + i * 1.85 + 0.65, 0.1], [szer, 1.3 - (j % 2) * 0.2, 1.0], kol[(i * 2 + j) % 7])
            x += szer + 0.12
        u.wa("Zwoj", [1.7, 0.75 + i * 1.85, 0.1], 1.1, 0.5, KREM, os_="z")
    u.ku("Globus", [0, 6.9, 0], 1.3, "2389D0")
    u.kl("GlobusLad", [0.1, 7.0, 0.5], [0.7, 0.5, 0.35], LISC)
    u.kl("GlobusStojak", [0, 6.25, 0], [0.9, 0.2, 0.9], ZLOTO)
    krysztal(g.w([0, 0, 0], 0, "Krysztaly"), [sc[0] + 9.5, 0, sc[2] - 3.0])
    krysztal(g.w([0, 0, 0], 0, "Krysztaly"), [sc[0] - 8.6, 0, sc[2] - 3.2], kolor="6CC8FF")
    krysztal(g.w([0, 0, 0], 0, "Krysztaly"), [sc[0] + 4.0, 0, sc[2] - 4.5], kolor="B85CFF")
    sr_ = st["sciana_rozmiar"]
    for sx in (-1, 1):
        x = sc[0] + sx * (sr_[0] / 2 + 0.5)
        g.kl("Swieca", [x, sr_[1] + 1.75, sc[2]], [0.4, 0.9, 0.4], KREM)
        g.kl("Plomyk", [x, sr_[1] + 2.45, sc[2]], [0.28, 0.5, 0.28], LAMPION, m="Neon")
    for i in range(8):  # krąg na podłodze wokół podestu
        a = math.radians(22.5 + 45 * i)
        g.kl("Krag", [pd[0] + math.cos(a) * 4.4, 0.09, pd[2] + math.sin(a) * 4.4], [0.9, 0.06, 0.9], "C9A7FF", ry=45)


def _szczescie(g, pd, st):
    """Szczęście „Koniczyny”: polanka — trawa za drzewem, płotek z tyłu i po bokach, kwiaty, krzaki, grzyby, kępy
    koniczyny, studnia, taczka ogrodnika, podkowa nad szyldem. Tory i miejsce postaci wolne."""
    x0, z0 = pd[0], pd[2]
    g.kl("TrawaTyl", [x0, 0.04, z0 - 14.2], [24, 0.08, 8.4], "6DB33F")
    g.kl("TrawaL", [x0 - 9.6, 0.04, z0 - 5.2], [4.6, 0.08, 9.6], "6DB33F")
    g.kl("TrawaP", [x0 + 9.7, 0.04, z0 - 5.2], [4.4, 0.08, 9.6], "6DB33F")
    u = g.w([x0, 0, z0 - 18.4], 0, "Plotek")
    xs = [-12 + 4 * i for i in range(7)]
    for x in xs:
        u.kl("Slupek", [x, 1.0, 0], [0.45, 2.0, 0.45], KREM, kol=True)
        u.kl("Szpic", [x, 2.15, 0], [0.45, 0.45, 0.45], KREM, rz=45)
    for y in (0.7, 1.5):
        u.kl("Zerdz", [0, y, 0], [24.4, 0.25, 0.2], KREM)
    for sx in (-1, 1):
        for i, dz in enumerate((3.5, 7.0)):
            u.kl("Slupek", [sx * 12, 1.0, dz], [0.45, 2.0, 0.45], KREM, kol=True)
            u.kl("Szpic", [sx * 12, 2.15, dz], [0.45, 0.45, 0.45], KREM, rz=45)
        for y in (0.7, 1.5):
            u.kl("ZerdzBok", [sx * 12, y, 3.5], [0.2, 0.25, 7.2], KREM)
    u = g.w([x0, 0, z0], 0, "Kwiaty")
    kol = (CZERWIEN, ZLOTO, ROZ, KREM, FIOLET, POMARANCZ)
    for i, (dx, dz) in enumerate(((-9.8, -3.2), (-10.6, -5.4), (-8.8, -7.0), (-10.2, -9.0), (9.2, -9.2), (10.6, -7.2),
                                  (8.8, -11.6), (-6.4, -12.4), (-3.4, -14.6), (2.8, -15.2), (6.2, -13.0), (-9.4, -15.4),
                                  (9.8, -15.8), (0.2, -17.0), (-11.0, -12.0), (11.2, -13.4))):
        kwiat(u, [dx, 0.08, dz], kol[i % 6], wys=0.9 + (i % 3) * 0.25)
    u = g.w([x0, 0, z0], 0, "Zielen")
    for i, (dx, dz, sr) in enumerate(((-10.6, -16.4, 3.0), (10.4, -16.6, 3.4), (-7.6, -16.8, 2.2), (6.4, -17.0, 2.4))):
        u.ku("Krzak", [dx, sr * 0.38, dz], sr, LISC_C if i % 2 else LISC, kol=i < 2)
        u.ku("Jagoda", [dx + 0.6, sr * 0.75, dz + sr * 0.38], 0.5, CZERWIEN)
    for i, (dx, dz) in enumerate(((-9.0, -11.0), (8.4, -5.0), (4.4, -16.2), (-4.8, -17.0))):
        u.wa("GrzybNozka", [dx, 0.45, dz], 0.8, 0.45, KREM)
        u.wa("GrzybKapelusz", [dx, 1.0, dz], 0.4, 1.3, CZERWIEN if i % 2 else "B8283A")
    for i, (dx, dz) in enumerate(((-9.4, -1.0), (9.6, -2.4), (-2.6, -12.8), (3.6, -11.6), (-6.2, -15.6))):
        for j, (ex, ez) in enumerate(((0, 0.42), (0.42, 0), (0, -0.42), (-0.42, 0))):
            u.wa("Koniczyna", [dx + ex, 0.13, dz + ez], 0.06, 0.8, "2E9B3A")
    u = g.w([x0 + 15.5, 0, z0 - 15.0], 0, "Studnia")
    u.wa("Krag", [0, 0.9, 0], 1.8, 3.4, KAMIEN, m="Slate", kol=True)
    u.wa("Woda", [0, 1.82, 0], 0.05, 2.6, "2389D0")
    for sx in (-1, 1):
        u.kl("Slup", [sx * 1.9, 2.6, 0], [0.4, 5.2, 0.4], DREWNO, kol=True)
        u.kl("Dach", [sx * 1.15, 5.7, 0], [2.7, 0.25, 3.4], CZERWIEN, rz=-sx * 28)
    u.wa("Walek", [0, 4.4, 0], 3.8, 0.45, DREWNO_S, os_="x")
    u.kl("Lina", [0.4, 3.5, 0], [0.1, 1.8, 0.1], SLOMA)
    u.wa("Wiadro", [0.4, 2.4, 0], 0.9, 0.9, DREWNO_J, m="WoodPlanks")
    og = _plus(pd, st["ogrodnik"])
    u = g.w([og[0] + 3.8, 0, og[2] + 0.6], -35, "Taczka")
    u.kl("Skrzynia", [0, 1.3, 0], [2.0, 1.0, 2.8], DREWNO_J, m="WoodPlanks", kol=True)
    u.kl("Ziemia", [0, 1.85, 0], [1.7, 0.2, 2.5], "6B4A2F")
    u.wa("Kolo", [0, 0.6, 1.9], 0.3, 1.2, TUSZ, os_="x")
    for sx in (-1, 1):
        u.kl("Raczka", [sx * 0.8, 1.3, -2.2], [0.2, 0.2, 2.0], DREWNO)
        u.kl("Nozka", [sx * 0.8, 0.4, -1.0], [0.2, 0.8, 0.2], DREWNO)
    kwiat(u, [0.3, 1.9, 0.4], ROZ, wys=0.8)
    kwiat(u, [-0.4, 1.9, -0.5], ZLOTO, wys=0.6)
    # podkowa nad szyldem (deska szyldu: podest + (−9,6; 5; −6,5), wysokość 2)
    u = g.w(_plus(pd, [-9.6, 6.3, -6.5]), 0, "Podkowa")
    for i, (dx, dy, rz, dl) in enumerate(((-0.75, 0.75, 90, 1.5), (0.75, 0.75, 90, 1.5), (0, 1.45, 0, 1.9), (-0.75, 0.1, 0, 0.6),
                                          (0.75, 0.1, 0, 0.6))):
        u.kl("Podkowa", [dx, dy, 0.1], [dl, 0.4, 0.3], ZLOTO, m="Metal", rz=rz)


def dodaj(S, D, K):
    """Dokłada dekoracje areny do sceny S (po częściach gry). Zwraca liczbę dołożonych części."""
    n0 = len(S.lista)
    A = K["arena"]
    sz, gl = A["rozmiar"]
    kolory = {s["id"]: s["kolor"] for s in D["statystyki"]}
    G = _G(S, "Arena/Dekoracje")
    _podloga(G.w([0, 0, 0], 0, "Podloga"), sz, gl)
    _ramy(G.w([0, 0, 0], 0, "Pola"), kolory)
    _ogrodzenie(G.w([0, 0, 0], 0, "Ogrodzenie"), sz, gl)
    _brama(G.w([0, 0, 0], 0, "Brama"))
    _tablica_wynikow(G.w([0, 0, 0], 0, "TablicaWynikow"), D)
    _zaplecze(G.w([0, 0, 0], 0, "Zaplecze"), kolory)
    ST = K["stanowiska"]
    if "sila" in ST:
        _sila(G.w([0, 0, 0], 0, "Sila"), ST["sila"]["podest"])
    if "pancerz" in ST:
        _pancerz(G.w([0, 0, 0], 0, "Pancerz"), ST["pancerz"]["podest"])
    if "kondycja" in ST:
        _kondycja(G.w([0, 0, 0], 0, "Kondycja"), ST["kondycja"]["podest"], kolory["kondycja"])
    if "zrecznosc" in ST:
        _zrecznosc(G.w([0, 0, 0], 0, "Zrecznosc"), ST["zrecznosc"]["podest"], ST["zrecznosc"])
    if "inteligencja" in ST:
        _inteligencja(G.w([0, 0, 0], 0, "Inteligencja"), ST["inteligencja"]["podest"], ST["inteligencja"])
    if "szczescie" in ST:
        _szczescie(G.w([0, 0, 0], 0, "Szczescie"), ST["szczescie"]["podest"], ST["szczescie"])
    return len(S.lista) - n0


# ------------------------------------------------------------------------------------------------ kontrola
def dekoracja(c):
    return c["r"].startswith("Arena/Dekoracje")


def _pudlo(c):
    import scena as SCENA
    s = SCENA.rozmiar_osiowy(c)
    return [c["p"][i] - s[i] / 2 for i in range(3)], [c["p"][i] + s[i] / 2 for i in range(3)]


def odcinek_w_pudle(a, b, mn, mx):
    t0, t1 = 0.0, 1.0
    for i in range(3):
        d = b[i] - a[i]
        if abs(d) < 1e-9:
            if a[i] < mn[i] or a[i] > mx[i]:
                return False
            continue
        u0, u1 = (mn[i] - a[i]) / d, (mx[i] - a[i]) / d
        if u0 > u1:
            u0, u1 = u1, u0
        t0, t1 = max(t0, u0), min(t1, u1)
        if t0 > t1:
            return False
    return True


def _nachodza(mn, mx, a, b):
    return all(mn[i] < b[i] and mx[i] > a[i] for i in range(3))


def przeszkody(D, cz):
    """Dekoracje, które nie są wzorem podłogi: (ścieżka, min, max) w świecie."""
    y0 = D["arena"]["srodek"][1]
    wynik = []
    for c in cz:
        if dekoracja(c) and c.get("t", 0) < 0.95:
            mn, mx = _pudlo(c)
            if mx[1] - y0 > PLASKIE + 1e-6:
                wynik.append((c["r"] + "/" + c["n"], mn, mx))
    return wynik


def pola_gry(D):
    """Pola gry w świecie: {gra: ("pudlo", min, max) | ("kolo", środek, promień, y0, y1)} + lobby."""
    P = {}
    c = D["arena"]["srodek"]
    for gra, (a, b) in POLA_GRY.items():
        pd = D["swiat"][gra]["podest"]
        P[gra] = ("pudlo", _plus(pd, a), _plus(pd, b))
    W = D["swiat"]["zrecznosc"]
    P["zrecznosc"] = ("kolo", W["slup"], W["ramie"] + W["kloda_srednica"] / 2 + 0.4, W["podest"][1] + PLASKIE, W["podest"][1] + 9.0)
    P["lobby"] = ("pudlo", _plus(c, POLE_LOBBY[0]), _plus(c, POLE_LOBBY[1]))
    return P


def w_polu(pole, mn, mx):
    if pole[0] == "pudlo":
        return _nachodza(mn, mx, pole[1], pole[2])
    _, s, r, y0, y1 = pole
    dx = max(mn[0] - s[0], 0, s[0] - mx[0])
    dz = max(mn[2] - s[2], 0, s[2] - mx[2])
    return math.hypot(dx, dz) < r and mn[1] < y1 and mx[1] > y0


def ujecia(D, gra):
    """Ujęcia kamery stanowiska do kontroli: (opis, ujęcie, miejsca postaci, czy zbliżenie)."""
    import kamera_treningu as KT
    W = D["swiat"][gra]
    KA = D["ui"]["kamera"]
    O = KA["final"]
    miejsca = KT.miejsca_postaci(D, gra)
    L = [("gra", KT.gra(D, gra), miejsca, False)]
    for znak in (-1, 1):
        L.append(("kołysanie %+d" % znak, KT.stanowisko(D, gra, znak * KA["kolysanie"]["okres_s"] / 4.0), miejsca, False))
    L.append(("start", {"oko": W["start"]["oko"], "cel": W["start"]["cel"], "kat": W["start"]["kat"]}, miejsca, False))
    for u in (0.25, 0.5, 0.75):
        L.append(("odliczanie %.2f" % u, KT.przejscie(W["start"], KT.gra(D, gra), u), miejsca, False))
    for i, baza in enumerate(miejsca):
        korzen = [baza[0], baza[1] + O["korzen_nad_ziemia"], baza[2]]
        for czas in (0, O["dojazd_s"], 60):
            for fx in (0.2, 0.35):
                for asp in ASPEKTY:
                    L.append(("zbliżenie m%d %ss fx%.2f %.2f" % (i + 1, czas, fx, asp),
                              dict(KT.final(D, gra, korzen, fx, asp, czas), aspekt=asp), [baza], True))
    return L


ASPEKTY = (16 / 9.0, 844 / 390.0, 4 / 3.0)


def cele(D, gra, miejsca):
    """Punkty, które kamera musi widzieć: pole gry (scena.pole_gry) i postać w każdym z miejsc."""
    import scena as SCENA
    P = [p[:3] for p in SCENA.pole_gry(D, gra)]
    for b in miejsca:
        for dx, dy in ((0, 0.5), (0, 2.7), (0, 5.2), (-1.2, 3.4), (1.2, 3.4)):
            P.append([b[0] + dx, b[1] + dy, b[2]])
    return P


def _promien(u, fx, fy, asp):
    """Kierunek promienia przez punkt ekranu (fx, fy ∈ 0–1) dla ujęcia u i proporcji asp."""
    f = [u["cel"][i] - u["oko"][i] for i in range(3)]
    d = math.sqrt(sum(x * x for x in f))
    f = [x / d for x in f]
    r = [-f[2], 0.0, f[0]]
    d = math.sqrt(sum(x * x for x in r))
    r = [x / d for x in r]
    g = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    th = math.tan(math.radians(u["kat"]) / 2)
    v = [f[i] + r[i] * (2 * fx - 1) * th * asp + g[i] * (1 - 2 * fy) * th for i in range(3)]
    d = math.sqrt(sum(x * x for x in v))
    return [x / d for x in v]


def kontrola(D, cz=None):
    """Lista usterek wyglądu (pusta = dobrze): pola gry, promienie do pól gry i postaci, przedpole kadrów, E."""
    import kamera_treningu as KT
    import scena as SCENA
    cz = cz if cz is not None else SCENA.czesci(D)
    P = przeszkody(D, cz)
    usterki = []
    for nazwa, pole in pola_gry(D).items():
        for sciezka, mn, mx in P:
            if w_polu(pole, mn, mx):
                usterki.append("pole gry %s: %s" % (nazwa, sciezka))
    for gra in D["gry"]:
        U = ujecia(D, gra)
        oczy = [u["oko"] for _, u, _, _ in U]
        blisko = [p for p in P if min(math.hypot((p[1][0] + p[2][0]) / 2 - o[0], (p[1][2] + p[2][2]) / 2 - o[2]) for o in oczy) < 60]
        widziane = set()
        for opis, u, miejsca, zblizenie in U:
            oko = u["oko"]
            klucz = tuple(round(x, 3) for x in oko)
            if klucz not in widziane:  # promienie zależą tylko od oka
                widziane.add(klucz)
                for sciezka, mn, mx in blisko:
                    if all(mn[i] <= oko[i] <= mx[i] for i in range(3)):
                        usterki.append("%s %s: oko kamery w dekoracji %s" % (gra, opis, sciezka))
                for cel in cele(D, gra, miejsca):
                    for sciezka, mn, mx in blisko:
                        if odcinek_w_pudle(oko, cel, mn, mx):
                            usterki.append("%s %s: %s zasłania punkt (%.1f, %.1f, %.1f)" % (gra, opis, sciezka, cel[0], cel[1], cel[2]))
                            break
            # przedpole: nic w kadrze bliżej oka niż postać / cel kamery
            zasieg = min(math.dist(oko, [b[0], b[1] + 2.7, b[2]]) for b in miejsca)
            if not zblizenie:
                zasieg = min(zasieg, math.dist(oko, u["cel"]))
            for asp in ((u["aspekt"],) if zblizenie else ASPEKTY):
                vw, vh = 1000.0 * asp, 1000.0
                zle = None
                for sciezka, mn, mx in blisko:
                    rogi = [[(mn, mx)[i][0], (mn, mx)[j][1], (mn, mx)[k][2]] for i in (0, 1) for j in (0, 1) for k in (0, 1)]
                    rogi.append([(mn[i] + mx[i]) / 2 for i in range(3)])
                    for p in rogi:
                        if math.dist(oko, p) >= zasieg:
                            continue
                        e = KT.rzut(u, p, vw, vh)
                        if e and 0 <= e[0] <= vw and 0 <= e[1] <= vh:
                            zle = sciezka
                            break
                    if zle:
                        break
                if not zle:
                    for ix in range(13):
                        for iy in range(7):
                            k = _promien(u, ix / 12.0, iy / 6.0, asp)
                            koniec = [oko[i] + k[i] * zasieg for i in range(3)]
                            for sciezka, mn, mx in blisko:
                                if odcinek_w_pudle(oko, koniec, mn, mx):
                                    zle = sciezka
                                    break
                            if zle:
                                break
                        if zle:
                            break
                if zle:
                    usterki.append("%s %s (%.2f): %s w przedpolu kadru" % (gra, opis, asp, zle))
    # podpowiedzi E: z punktu przybycia widać obie części E, a wokół nich nie stoi dekoracja
    c = D["arena"]["srodek"]
    pr = D["swiat"]["przybycie"]
    oko = [pr[0], pr[1] + 5.0, pr[2]]
    for x in cz:
        if x["n"] == "E" and x["r"].startswith("Arena/Lobby"):
            for sciezka, mn, mx in P:
                if odcinek_w_pudle(oko, x["p"], mn, mx):
                    usterki.append("podpowiedź %s: zasłania %s" % (x["r"], sciezka))
                if _nachodza(mn, mx, [x["p"][0] - 4.5, c[1] + PLASKIE, x["p"][2] - 3.0], [x["p"][0] + 4.5, c[1] + 6.5, x["p"][2] + 3.0]):
                    usterki.append("podpowiedź %s: za blisko %s" % (x["r"], sciezka))
    return usterki


def budzet(cz):
    """Liczby do budżetu: części razem, dekoracje, bez dekoracji, dekoracje bez kolizji, kliny, napisy."""
    dek = [c for c in cz if dekoracja(c)]
    return {"razem": len(cz), "dekoracje": len(dek), "gra": len(cz) - len(dek),
            "bez_kolizji": len([c for c in dek if c.get("kol") is False]),
            "kliny": len([c for c in cz if c.get("k") == "W"]), "napisy": len([c for c in cz if c.get("napis")]),
            "neon": len([c for c in dek if c.get("m") == "Neon"]), "swiatla": 0}


def grupy(cz, poziom=3):
    G = {}
    for c in cz:
        k = "/".join(c["r"].split("/")[:poziom])
        G[k] = G.get(k, 0) + 1
    return G


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if TU not in sys.path:
        sys.path.insert(0, TU)
    import dane as DANE
    import scena as SCENA
    _, D_ = DANE.wczytaj()
    cz_ = SCENA.czesci(D_)
    for k_, n_ in sorted(grupy(cz_).items()):
        print("  %-34s %4d" % (k_, n_))
    print("budżet:", budzet(cz_))
    u_ = kontrola(D_, cz_)
    print("kontrola: %s" % ("OK (pola gry wolne, kadry niezasłonięte, E odsłonięte)" if not u_ else "%d usterek" % len(u_)))
    for x_ in u_[:40]:
        print("  -", x_)
    sys.exit(1 if u_ else 0)
