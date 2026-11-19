# -*- coding: utf-8 -*-
"""Figury trenerów z klocków i KONTROLA wyglądu scenerii mini-gier Training Center (D-108).

    python -B swiat/trening_proba/dekoracje.py        # liczba części wg grup, budżet i kontrola (pola gry, kadry, tło)

Do 18.11.2026 ten plik stawiał też dekoracje placu w murach (trybuny, girlandy, tablica wyników). Od D-108 mini-gry
stoją w sceneriach krain — części scenerii generuje scenerie.py (grupa „Arena/Dekoracje/<Gra>/…”), a tu zostało:
    figura(...)        — trener z klocków w stylu sprzedawców bazaru (duża głowa, oczy ze źrenicami, brwi, nos, uśmiech,
                         uszy, buty, pas, dłonie); części animowane (RamieP miotacza i trenera Bieżni) to nadal jeden klocek.
                         Figury stoją w punktach trenera (stanowiska.<gra>.trener_npc) do czasu podmiany na postacie NPC
    golem_dodatki(...) — kamienne szczegóły golema (pięść, oczy i ramię zostają, jak były)
    kontrola(D, cz)    — usterki scenerii (pusta lista = dobrze), liczone bez Studio (numpy):
        * pola gry (POLA_GRY, koło Kłód) wolne od części scenerii wyższych niż próg płaskości,
        * żadna część scenerii nie przecina promienia oko kamery → pole gry / postać (kamera gry z kołysaniem, początek
          i droga odliczania, zbliżenie po rundzie dla każdego miejsca postaci),
        * przedpole kadru czyste: w kadrze (16:9, telefon 844 × 390, 4:3) nic nie stoi bliżej oka niż postać / cel kamery
    kontrola_tla(D, cz) — tło kadrów: promienie przez siatkę każdego kadru (te same ujęcia) muszą trafić w część sceny;
        promień, który nie trafia w nic i nie idzie wyraźnie w górę (ponad kulisy), to „pustka w kadrze”; do tego udział
        nieba w kadrze gry (statystyka do oceny)
    budzet(cz), grupy(cz) — liczby części.
Układ: lokalny areny (x na wschód, z na południe — strona kamer, y = 0 to poziom podestów); _Scena dodaje środek areny.
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


# ------------------------------------------------------------------------------------------------ kontrola
PLASKIE = 0.25          # części o wierzchu do tej wysokości nad poziomem podestów to wzór podłoża (nie przeszkoda)
BEZ_KOLIZJI_MIN = 0.98  # co najmniej taki ułamek części scenerii bez kolizji
CZESCI_MAX = 3000       # budżet części całej areny (elementy gier + scenerie)
NEON_MAX = 60           # części Neon w sceneriach (świecące kwiaty, ogniki, okna chat) — świateł nie ma wcale
KAT_NIEBA = 1.5         # promień bez trafienia musi iść w górę co najmniej o tyle stopni — inaczej to pustka w kadrze
NIEBO_MAX = 0.35        # największy udział nieba w kadrze gry (kamera patrzy lekko w górę, więc niebo nad kulisami jest)
ASPEKTY = (16 / 9.0, 844 / 390.0, 4 / 3.0)

# pola gry względem podestu stanowiska: (min, max) — tu nie stoi żadna część scenerii wyższa niż PLASKIE
POLA_GRY = {
    "sila": ([-7.5, PLASKIE, -14.8], [7.5, 11.0, 4.0]),          # gracz, strefy ciosu i tory lotu od miotacza
    "pancerz": ([-4.5, PLASKIE, -7.2], [6.5, 12.0, 4.0]),        # gracz z tarczą i droga pięści golema
    "kondycja": ([-4.2, PLASKIE, -6.2], [3.6, 9.0, 11.0]),       # grobla z poręczami
    "inteligencja": ([-4.5, PLASKIE, -7.4], [9.0, 11.0, 4.0]),   # gracz i przedpole kamiennych tablic
    "szczescie": ([-6.2, PLASKIE, -3.2], [6.2, 15.5, 3.5]),      # trzy tory i spadające koniczyny
}


def dekoracja(c):
    """Część scenerii (sam wygląd) — wszystko w grupie Arena/Dekoracje."""
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
    """Części scenerii, które nie są wzorem podłoża: (ścieżka, min, max) w świecie."""
    y0 = D["arena"]["srodek"][1]
    wynik = []
    for c in cz:
        if dekoracja(c) and c.get("t", 0) < 0.95:
            mn, mx = _pudlo(c)
            if mx[1] - y0 > PLASKIE + 1e-6:
                wynik.append((c["r"] + "/" + c["n"], mn, mx))
    return wynik


def pola_gry(D):
    """Pola gry w świecie: {gra: ("pudlo", min, max) | ("kolo", środek, promień, y0, y1)}."""
    P = {}
    for gra, (a, b) in POLA_GRY.items():
        pd = D["swiat"][gra]["podest"]
        P[gra] = ("pudlo", _plus(pd, a), _plus(pd, b))
    W = D["swiat"]["zrecznosc"]
    P["zrecznosc"] = ("kolo", W["slup"], W["ramie"] + W["kloda_srednica"] / 2 + 0.4, W["podest"][1] + PLASKIE, W["podest"][1] + 9.0)
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


def cele(D, gra, miejsca):
    """Punkty, które kamera musi widzieć: pole gry (scena.pole_gry) i postać w każdym z miejsc."""
    import scena as SCENA
    P = [p[:3] for p in SCENA.pole_gry(D, gra)]
    for b in miejsca:
        for dx, dy in ((0, 0.5), (0, 2.7), (0, 5.2), (-1.2, 3.4), (1.2, 3.4)):
            P.append([b[0] + dx, b[1] + dy, b[2]])
    return P


def _baza(u):
    """Osie kamery ujęcia (CFrame.lookAt(oko, cel)): w prawo, w górę, w przód."""
    f = [u["cel"][i] - u["oko"][i] for i in range(3)]
    d = math.sqrt(sum(x * x for x in f))
    f = [x / d for x in f]
    r = [-f[2], 0.0, f[0]]
    d = math.sqrt(sum(x * x for x in r))
    r = [x / d for x in r]
    g = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    return r, g, f


def _promien(u, fx, fy, asp):
    """Kierunek promienia przez punkt ekranu (fx, fy ∈ 0–1) dla ujęcia u i proporcji asp."""
    r, g, f = _baza(u)
    th = math.tan(math.radians(u["kat"]) / 2)
    v = [f[i] + r[i] * (2 * fx - 1) * th * asp + g[i] * (1 - 2 * fy) * th for i in range(3)]
    d = math.sqrt(sum(x * x for x in v))
    return [x / d for x in v]


def siatka_promieni(np, u, asp, nx=13, ny=7):
    """Kierunki promieni przez siatkę nx × ny punktów kadru (jednostkowe) → tablica (nx·ny, 3)."""
    r, g, f = (np.array(v, dtype=float) for v in _baza(u))
    th = math.tan(math.radians(u["kat"]) / 2)
    fx = np.repeat(np.linspace(0, 1, nx), ny)
    fy = np.tile(np.linspace(0, 1, ny), nx)
    v = f[None, :] + r[None, :] * ((2 * fx - 1) * th * asp)[:, None] + g[None, :] * ((1 - 2 * fy) * th)[:, None]
    return v / np.linalg.norm(v, axis=1)[:, None]


def odcinki_w_pudlach(np, A, B, MN, MX):
    """Które odcinki A[i]–B[i] przecinają które pudła osiowe (MN[j], MX[j]) → tablica logiczna (odcinki, pudła)."""
    A, B = np.asarray(A, dtype=float), np.asarray(B, dtype=float)
    wynik = np.zeros((len(A), len(MN)), dtype=bool)
    if not len(A) or not len(MN):
        return wynik
    d = B - A
    d = np.where(np.abs(d) < 1e-9, 1e-9, d)
    for i0 in range(0, len(A), 400):
        a, dd = A[i0:i0 + 400, None, :], d[i0:i0 + 400, None, :]
        u0, u1 = (MN[None] - a) / dd, (MX[None] - a) / dd
        t0 = np.minimum(u0, u1).max(axis=2)
        t1 = np.maximum(u0, u1).min(axis=2)
        wynik[i0:i0 + 400] = np.maximum(t0, 0.0) <= np.minimum(t1, 1.0)
    return wynik


class Straznik:
    """Wolna przestrzeń jednej gry: pole gry, promienie oko → cele i przedpole kadrów (wszystkie ujęcia, trzy proporcje).
    zle(pudła) zwraca opisy usterek — tej samej kontroli używa generator scenerii (przed postawieniem rekwizytu)
    i kontrola() na gotowej scenie."""

    def __init__(self, D, gra, np):
        self.np, self.gra = np, gra
        self.pole = pola_gry(D)[gra]
        A, B, opisy = [], [], []
        widziane = set()
        self.oczy = []
        self.kadry = []  # (opis, proporcja, zasięg, ujęcie)
        for opis, u, miejsca, zblizenie in ujecia(D, gra):
            oko = u["oko"]
            klucz = tuple(round(x, 3) for x in oko)
            if klucz not in widziane:
                widziane.add(klucz)
                self.oczy.append((opis, oko))
                for cel in cele(D, gra, miejsca):
                    A.append(oko)
                    B.append(cel)
                    opisy.append((opis, cel))
            zasieg = min(math.dist(oko, [b[0], b[1] + 2.7, b[2]]) for b in miejsca)
            if not zblizenie:
                zasieg = min(zasieg, math.dist(oko, u["cel"]))
            for asp in ((u["aspekt"],) if zblizenie else ASPEKTY):
                self.kadry.append((opis, asp, zasieg, u))
        self.A, self.B, self.opisy = np.array(A, dtype=float), np.array(B, dtype=float), opisy
        self.O = np.array([o for _, o in self.oczy], dtype=float)
        # przedpole: promienie siatki kadru do zasięgu (odcinki) i rzut rogów pudeł
        PA, PB, self.kadr_promienia = [], [], []
        osie = []
        for i, (opis, asp, zasieg, u) in enumerate(self.kadry):
            k = siatka_promieni(np, u, asp)
            oko = np.array(u["oko"], dtype=float)
            PA.append(np.repeat(oko[None, :], len(k), axis=0))
            PB.append(oko[None, :] + k * zasieg)
            self.kadr_promienia += [i] * len(k)
            osie.append(_baza(u))
        self.PA, self.PB = np.concatenate(PA), np.concatenate(PB)
        self.K_oko = np.array([k[3]["oko"] for k in self.kadry], dtype=float)
        self.K_r = np.array([o[0] for o in osie], dtype=float)
        self.K_g = np.array([o[1] for o in osie], dtype=float)
        self.K_f = np.array([o[2] for o in osie], dtype=float)
        th = np.array([math.tan(math.radians(k[3]["kat"]) / 2) for k in self.kadry], dtype=float)
        self.K_thy = th
        self.K_thx = th * np.array([k[1] for k in self.kadry], dtype=float)
        self.K_zasieg = np.array([k[2] for k in self.kadry], dtype=float)

    def zle(self, pudla, wszystkie=False):
        """pudla: lista (ścieżka, min, max) w świecie (już bez wzoru podłoża). → lista opisów usterek (pierwsza albo
        wszystkie). Pudła dalej niż 60 st (w poziomie) od każdego oka tej gry są pomijane."""
        np = self.np
        usterki = []
        if not pudla:
            return usterki
        MN = np.array([p[1] for p in pudla], dtype=float)
        MX = np.array([p[2] for p in pudla], dtype=float)
        S = (MN + MX) / 2
        blisko = (np.hypot(S[:, None, 0] - self.O[None, :, 0], S[:, None, 2] - self.O[None, :, 2]) < 60).any(axis=1)
        if not blisko.any():
            return usterki
        pudla = [p for p, b in zip(pudla, blisko) if b]
        MN, MX = MN[blisko], MX[blisko]
        for sciezka, mn, mx in pudla:
            if w_polu(self.pole, mn, mx):
                usterki.append("pole gry %s: %s" % (self.gra, sciezka))
                if not wszystkie:
                    return usterki
        for opis, oko in self.oczy:
            w = np.all((MN <= np.array(oko)) & (np.array(oko) <= MX), axis=1)
            if w.any():
                usterki.append("%s %s: oko kamery w dekoracji %s" % (self.gra, opis, pudla[int(np.argmax(w))][0]))
                if not wszystkie:
                    return usterki
        T = odcinki_w_pudlach(np, self.A, self.B, MN, MX)
        for i in np.nonzero(T.any(axis=1))[0]:
            opis, cel = self.opisy[int(i)]
            usterki.append("%s %s: %s zasłania punkt (%.1f, %.1f, %.1f)" % (self.gra, opis, pudla[int(np.argmax(T[i]))][0],
                                                                         cel[0], cel[1], cel[2]))
            if not wszystkie:
                return usterki
        # przedpole: rogi i środki pudeł w kadrze bliżej oka niż postać / cel kamery, potem promienie siatki kadru
        zle_kadr = {}
        rogi = [np.stack([(MN, MX)[i][:, 0], (MN, MX)[j][:, 1], (MN, MX)[k][:, 2]], axis=1)
                for i in (0, 1) for j in (0, 1) for k in (0, 1)] + [S[blisko]]
        R = np.stack(rogi, axis=1)                                                                 # (pudła, 9, 3)
        q = R[None, :, :, :] - self.K_oko[:, None, None, :]                                        # (kadry, pudła, 9, 3)
        z = np.einsum("kpcj,kj->kpc", q, self.K_f)
        x = np.einsum("kpcj,kj->kpc", q, self.K_r)
        y = np.einsum("kpcj,kj->kpc", q, self.K_g)
        odl = np.linalg.norm(q, axis=3)
        zs = np.where(z > 0.1, z, 1.0)
        w_kadrze = ((z > 0.1) & (np.abs(x / zs) <= self.K_thx[:, None, None]) & (np.abs(y / zs) <= self.K_thy[:, None, None])
                    & (odl < self.K_zasieg[:, None, None]))
        trafione = w_kadrze.any(axis=2)                                                            # (kadry, pudła)
        for ki in np.nonzero(trafione.any(axis=1))[0]:
            zle_kadr[int(ki)] = pudla[int(np.argmax(trafione[ki]))][0]
        T = odcinki_w_pudlach(np, self.PA, self.PB, MN, MX)
        for i in np.nonzero(T.any(axis=1))[0]:
            zle_kadr.setdefault(self.kadr_promienia[int(i)], pudla[int(np.argmax(T[i]))][0])
        for ki in sorted(zle_kadr):
            usterki.append("%s %s (%.2f): %s w przedpolu kadru" % (self.gra, self.kadry[ki][0], self.kadry[ki][1], zle_kadr[ki]))
            if not wszystkie:
                return usterki
        return usterki


def kontrola(D, cz=None):
    """Lista usterek wyglądu (pusta = dobrze): pola gry, promienie do pól gry i postaci, przedpole kadrów."""
    import numpy as np
    import scena as SCENA
    cz = cz if cz is not None else SCENA.czesci(D)
    P = przeszkody(D, cz)
    usterki = []
    for gra in D["gry"]:
        usterki += Straznik(D, gra, np).zle(P, wszystkie=True)
    return usterki


def kontrola_tla(D, cz=None, nx=17, ny=9):
    """Tło kadrów. Promienie przez siatkę nx × ny każdego kadru (te same ujęcia i proporcje co w kontroli) rzucane na
    WSZYSTKIE nieprzezroczyste części areny (bryły obrócone — nie pudła osiowe). Usterka „pustka w kadrze”: promień nie
    trafia w nic, a idzie w dół, poziomo albo mniej niż KAT_NIEBA stopni w górę (pod linią kulis byłoby widać nic).
    Zwraca (usterki, {gra: {"niebo": największy udział nieba w kadrze gry, "niebo_sr": średni, "pustka": liczba
    promieni w pustkę, "kadry": liczba kadrów}})."""
    import numpy as np
    import scena as SCENA
    cz = cz if cz is not None else SCENA.czesci(D)
    lite = [c for c in cz if c.get("t", 0) < 0.5]
    P = np.array([c["p"] for c in lite], dtype=float)
    H = np.array([c["s"] for c in lite], dtype=float) / 2.0
    R = np.array([SCENA.macierz(c.get("o")) for c in lite], dtype=float)
    prog = math.sin(math.radians(KAT_NIEBA))
    usterki, stat = [], {}
    for gra in D["gry"]:
        niebo, pustka, kadry = [], 0, 0
        for opis, u, miejsca, zblizenie in ujecia(D, gra):
            oko = np.array(u["oko"], dtype=float)
            blisko = np.hypot(P[:, 0] - oko[0], P[:, 2] - oko[2]) < 170
            Pb, Hb, Rb = P[blisko], H[blisko], R[blisko]
            ol = np.einsum("nj,nji->ni", oko[None, :] - Pb, Rb)
            for asp in ((u["aspekt"],) if zblizenie else ASPEKTY):
                k = siatka_promieni(np, u, asp, nx, ny)
                dl = np.einsum("mj,nji->mni", k, Rb)
                dl = np.where(np.abs(dl) < 1e-9, 1e-9, dl)
                t1, t2 = (-Hb[None] - ol[None]) / dl, (Hb[None] - ol[None]) / dl
                tmin = np.minimum(t1, t2).max(axis=2)
                tmax = np.maximum(t1, t2).min(axis=2)
                trafia = (tmax >= np.maximum(tmin, 0.0)).any(axis=1)
                w_pustke = (~trafia) & (k[:, 1] < prog)
                kadry += 1
                if w_pustke.any():
                    pustka += int(w_pustke.sum())
                    i = int(np.argmax(w_pustke))
                    usterki.append("%s %s (%.2f): pustka w kadrze — %d promieni, np. punkt kadru (%.2f, %.2f)" % (
                        gra, opis, asp, int(w_pustke.sum()), (i // ny) / (nx - 1.0), (i % ny) / (ny - 1.0)))
                if not zblizenie and opis == "gra":
                    niebo.append(float((~trafia).mean()))
        stat[gra] = {"niebo": round(max(niebo), 3), "niebo_sr": round(sum(niebo) / len(niebo), 3), "pustka": pustka, "kadry": kadry}
        if max(niebo) > NIEBO_MAX:
            usterki.append("%s gra: nieba w kadrze %.0f%% (najwyżej %.0f%%)" % (gra, max(niebo) * 100, NIEBO_MAX * 100))
    return usterki, stat


def budzet(cz):
    """Liczby do budżetu: części razem, scenerie, elementy gier, scenerie bez kolizji, kliny, napisy, neon."""
    dek = [c for c in cz if dekoracja(c)]
    return {"razem": len(cz), "dekoracje": len(dek), "gra": len(cz) - len(dek),
            "bez_kolizji": len([c for c in dek if c.get("kol") is False]),
            "kliny": len([c for c in cz if c.get("k") == "W"]), "narozniki": len([c for c in cz if c.get("k") == "N"]),
            "napisy": len([c for c in cz if c.get("napis")]),
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
    print("kontrola: %s" % ("OK (pola gry wolne, kadry niezasłonięte)" if not u_ else "%d usterek" % len(u_)))
    for x_ in u_[:40]:
        print("  -", x_)
    t_, s_ = kontrola_tla(D_, cz_)
    print("tło kadrów: %s" % ("OK (bez pustki)" if not t_ else "%d usterek" % len(t_)))
    for g_, w_ in s_.items():
        print("  %-13s niebo w kadrze gry do %2.0f%% (średnio %2.0f%%), promieni w pustkę %d, kadrów %d" % (
            g_, w_["niebo"] * 100, w_["niebo_sr"] * 100, w_["pustka"], w_["kadry"]))
    for x_ in t_[:40]:
        print("  -", x_)
    sys.exit(1 if (u_ or t_) else 0)
