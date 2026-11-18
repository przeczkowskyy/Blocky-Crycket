#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Podglądy stanowisk Training Center bez Studio: bryły z scena.py (te same części, które stawia zbuduj.py) widziane
z kamery mini-gry (oko / cel / kąt widzenia z ustawienia.json — pionowy, jak Camera.FieldOfView w Roblox) i przykładowa
chwila gry (postać gracza, przedmioty, które w grze rysuje klient). To RENDER BRYŁ do oceny układu i czytelności, nie
zrzut z gry.

    python -B swiat/trening_proba/podglad.py                     # wszystkie podglądy do swiat/trening_proba/podglady/
    python -B swiat/trening_proba/podglad.py --tylko kondycja     # jeden (sila, pancerz, kondycja, zrecznosc,
                                                                  #  inteligencja, szczescie, arena)
    python -B swiat/trening_proba/podglad.py --wyj <folder>      # inny folder
    python -B swiat/trening_proba/podglad.py --ujecie start       # ujęcie: gra (domyślnie) | start (początek odliczania)
                                                                  #  | final (zbliżenie na postać po rundzie)
    python -B swiat/trening_proba/podglad.py --ekran 667x375      # kadr telefonu (domyślnie 1280x720)

Rysowanie: numpy, bufor głębi z interpolacją 1/z, obcinanie przy bliskiej płaszczyźnie, cieniowanie płaskie (słońce +
światło otoczenia), Neon bez cienia, części półprzezroczyste nakładane po nieprzezroczystych, obrys krawędzi brył,
napisy szyldów (SurfaceGui) rzutowane na ścianę deski. Proces ma najniższy priorytet (Windows) — komputer jest słaby.
Na podglądach jest też zarys sterowania dotykowego (przyciski z KlientTreningu, rozmiary z ustawień, skala 1280 × 720).
"""
import argparse
import math
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
if not sys.path or sys.path[0] != TU:
    sys.path.insert(0, TU)
import dane as DANE  # noqa: E402
import scena as SCENA  # noqa: E402

W, H = 1280, 720  # rozmiar podglądu (zmienia --ekran)
TLO_GORA, TLO_DOL = (126, 186, 236), (206, 230, 247)
SLONCE = (-0.45, 0.8, 0.4)
GRACZ = "D8CBB5"  # postać gracza na podglądzie (w grze — awatar)


def najnizszy_priorytet():
    if os.name == "nt":
        try:
            import ctypes
            k = ctypes.windll.kernel32
            k.SetPriorityClass(k.GetCurrentProcess(), 0x40)  # IDLE_PRIORITY_CLASS
        except Exception:  # noqa: BLE001
            pass


# ------------------------------------------------------------------------------------------------ siatki brył
def _siatka(c, np):
    """Trójkąty części (świat): klocek 12, walec 2 × 16 + 32, kula 12 × 8 → tablica (n, 3, 3)."""
    s = c["s"]
    R = np.array(SCENA.macierz(c.get("o")))
    p = np.array(c["p"], dtype=float)
    k = c.get("k", "B")
    tr = []
    if k == "B":
        hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
        v = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz), (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz),
             (-hx, hy, hz)]
        sciany = [(0, 1, 2, 3), (5, 4, 7, 6), (4, 0, 3, 7), (1, 5, 6, 2), (3, 2, 6, 7), (4, 5, 1, 0)]
        for a, b, cc, d in sciany:
            tr.append((v[a], v[b], v[cc]))
            tr.append((v[a], v[cc], v[d]))
    elif k == "C":
        n = 16
        hl, r = s[0] / 2, min(s[1], s[2]) / 2
        kolo = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]
        for i in range(n):
            (y0, z0), (y1, z1) = kolo[i], kolo[(i + 1) % n]
            tr.append(((-hl, y0, z0), (hl, y0, z0), (hl, y1, z1)))
            tr.append(((-hl, y0, z0), (hl, y1, z1), (-hl, y1, z1)))
            tr.append(((hl, 0, 0), (hl, y1, z1), (hl, y0, z0)))
            tr.append(((-hl, 0, 0), (-hl, y0, z0), (-hl, y1, z1)))
    else:
        r = s[0] / 2
        nu, nv = 14, 9
        pk = []
        for j in range(nv + 1):
            th = math.pi * j / nv
            pk.append([(r * math.sin(th) * math.cos(2 * math.pi * i / nu), r * math.cos(th),
                        r * math.sin(th) * math.sin(2 * math.pi * i / nu)) for i in range(nu)])
        for j in range(nv):
            for i in range(nu):
                a, b = pk[j][i], pk[j][(i + 1) % nu]
                cc, d = pk[j + 1][(i + 1) % nu], pk[j + 1][i]
                tr.append((a, cc, b))
                tr.append((a, d, cc))
    t = np.array(tr, dtype=float)
    return t @ R.T + p


class Kamera:
    def __init__(self, oko, cel, np, kat):
        self.np = np
        self.oko = np.array(oko, dtype=float)
        f = np.array(cel, dtype=float) - self.oko
        f /= np.linalg.norm(f)
        r = np.cross(f, [0.0, 1.0, 0.0])
        r /= np.linalg.norm(r)
        u = np.cross(r, f)
        self.B = np.stack([r, u, f])
        self.f = (H / 2) / math.tan(math.radians(kat / 2))

    def widok(self, P):
        return (P - self.oko) @ self.B.T

    def ekran(self, V):
        z = V[..., 2]
        return W / 2 + V[..., 0] / z * self.f, H / 2 - V[..., 1] / z * self.f, z


def _obetnij(tri, blisko=0.15):
    """Obcięcie trójkąta (widok) przy bliskiej płaszczyźnie z = blisko → lista trójkątów."""
    pk = list(tri)
    wynik = []
    for i in range(len(pk)):
        a, b = pk[i], pk[(i + 1) % len(pk)]
        wa, wb = a[2] >= blisko, b[2] >= blisko
        if wa:
            wynik.append(a)
        if wa != wb:
            t = (blisko - a[2]) / (b[2] - a[2])
            wynik.append(a + (b - a) * t)
    if len(wynik) < 3:
        return []
    return [(wynik[0], wynik[i], wynik[i + 1]) for i in range(1, len(wynik) - 1)]


class Plotno:
    def __init__(self, np):
        self.np = np
        y = np.linspace(0, 1, H)[:, None, None]
        gora, dol = np.array(TLO_GORA, float), np.array(TLO_DOL, float)
        self.obraz = np.broadcast_to(gora * (1 - y) + dol * y, (H, W, 3)).copy()
        self.z = np.zeros((H, W))  # 1/z (większe = bliżej); 0 = tło
        self.id = np.full((H, W), -1, dtype=np.int32)

    def trojkat(self, xs, ys, ws, kolor, nr, alfa=1.0):
        np = self.np
        x0, x1 = max(int(math.floor(min(xs))), 0), min(int(math.ceil(max(xs))), W - 1)
        y0, y1 = max(int(math.floor(min(ys))), 0), min(int(math.ceil(max(ys))), H - 1)
        if x0 > x1 or y0 > y1:
            return
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        (ax, bx, cx), (ay, by, cy) = xs, ys
        d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(d) < 1e-9:
            return
        l1 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / d
        l2 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / d
        l3 = 1 - l1 - l2
        m = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        if not m.any():
            return
        w = l1 * ws[0] + l2 * ws[1] + l3 * ws[2]
        zb = self.z[y0:y1 + 1, x0:x1 + 1]
        m &= w > zb * (1 + 1e-7)
        if not m.any():
            return
        ob = self.obraz[y0:y1 + 1, x0:x1 + 1]
        if alfa >= 1:
            zb[m] = w[m]
            self.id[y0:y1 + 1, x0:x1 + 1][m] = nr
            ob[m] = kolor
        else:
            ob[m] = ob[m] * (1 - alfa) + np.array(kolor) * alfa


def _kolor(h):
    return tuple(int(h[i:i + 2], 16) for i in range(0, 6, 2))


def rysuj(czesci, oko, cel, np, kat):
    kam = Kamera(oko, cel, np, kat)
    pl = Plotno(np)
    sl = np.array(SLONCE) / np.linalg.norm(SLONCE)
    przezr = []
    for nr, c in enumerate(czesci):
        t = c.get("t", 0)
        if t >= 0.95:
            continue
        if t > 0:
            przezr.append((nr, c))
            continue
        _czesc(pl, kam, c, nr, sl, np, 1.0)
    for nr, c in przezr:
        _czesc(pl, kam, c, nr, sl, np, 1 - c.get("t", 0))
    return kam, pl


def _czesc(pl, kam, c, nr, sl, np, alfa):
    tri = _siatka(c, np)
    baza = np.array(_kolor(c["c"]), dtype=float)
    neon = c.get("m") == "Neon"
    V = kam.widok(tri.reshape(-1, 3)).reshape(-1, 3, 3)
    for k in range(len(tri)):
        n = np.cross(tri[k][1] - tri[k][0], tri[k][2] - tri[k][0])
        dl = np.linalg.norm(n)
        if dl < 1e-12:
            continue
        n /= dl
        do_oka = kam.oko - tri[k][0]
        if alfa >= 1 and np.dot(n, do_oka) < 0 and c.get("k") != "K":
            continue  # tył ściany (bryły są zamknięte)
        if neon:
            kol = np.minimum(255, baza * 1.08 + 18)
        else:
            sw = 0.58 + 0.5 * max(0.0, float(np.dot(n, sl)))
            kol = np.minimum(255, baza * sw)
        for t3 in _obetnij(V[k]):
            t3 = np.array(t3)
            xs, ys, zs = kam.ekran(t3)
            pl.trojkat(xs, ys, 1 / zs, kol, nr, alfa)


def obrysy(pl, np):
    i = pl.id
    kraw = np.zeros_like(i, dtype=bool)
    kraw[:, 1:] |= i[:, 1:] != i[:, :-1]
    kraw[1:, :] |= i[1:, :] != i[:-1, :]
    pl.obraz[kraw] = pl.obraz[kraw] * 0.45


# ------------------------------------------------------------------------------------------------ napisy szyldów
def _czcionka(px, ImageFont):
    for n in ("arialbd.ttf", "DejaVuSans-Bold.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(n, px)
        except OSError:
            continue
    return ImageFont.load_default()


def napisy(pl, kam, czesci, np, Image, ImageDraw, ImageFont):
    """Napis SurfaceGui na ścianie części (Back = +z, Front = −z w układzie części), tylko na pikselach tej części."""
    obraz = Image.fromarray(pl.obraz.clip(0, 255).astype("uint8"))
    for nr, c in enumerate(czesci):
        nap = c.get("napis")
        if not nap:
            continue
        s = c["s"]
        R = np.array(SCENA.macierz(c.get("o")))
        zn = s[2] / 2 + 0.01 if nap["strona"] == "Back" else -s[2] / 2 - 0.01
        hx, hy = s[0] / 2 * 0.94, s[1] / 2 * 0.9
        if nap["strona"] == "Back":
            rogi = [(-hx, hy, zn), (hx, hy, zn), (hx, -hy, zn), (-hx, -hy, zn)]
        else:
            rogi = [(hx, hy, zn), (-hx, hy, zn), (-hx, -hy, zn), (hx, -hy, zn)]
        P = np.array(rogi) @ R.T + np.array(c["p"])
        V = kam.widok(P)
        if (V[:, 2] < 0.3).any():
            continue
        xs, ys, _ = kam.ekran(V)
        n_sw = R @ np.array([0, 0, 1.0 if nap["strona"] == "Back" else -1.0])
        if np.dot(n_sw, kam.oko - np.array(c["p"])) <= 0:
            continue
        sw, sh = 600, max(60, int(600 * hy / hx))
        tekst = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        dr = ImageDraw.Draw(tekst)
        linie = nap["tekst"].split("\n")
        px = int(min(sh / (len(linie) * 1.25), 70))
        f = _czcionka(px, ImageFont)
        while px > 10 and max(dr.textlength(x, font=f) for x in linie) > sw * 0.96:
            px -= 2
            f = _czcionka(px, ImageFont)
        y = (sh - len(linie) * px * 1.2) / 2
        for x in linie:
            dr.text(((sw - dr.textlength(x, font=f)) / 2, y), x, font=f, fill=_kolor(nap["kolor"]) + (255,))
            y += px * 1.2
        cel_pk = [(xs[i], ys[i]) for i in range(4)]
        wsp = _perspektywa(cel_pk, [(0, 0), (sw, 0), (sw, sh), (0, sh)], np)
        warstwa = tekst.transform((W, H), Image.PERSPECTIVE, wsp, Image.BILINEAR)
        maska = Image.fromarray(((pl.id == nr) * 255).astype("uint8"))
        alfa = Image.fromarray((np.array(warstwa.split()[3]) * (np.array(maska) > 0)).astype("uint8"))
        obraz.paste(warstwa.convert("RGB"), (0, 0), alfa)
    return obraz


def _perspektywa(z_pk, do_pk, np):
    """Współczynniki Image.PERSPECTIVE: piksel wyjścia (z_pk) → piksel źródła (do_pk)."""
    A, b = [], []
    for (x, y), (u, v) in zip(z_pk, do_pk):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        b += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(b, float)).tolist()


# ------------------------------------------------------------------------------------------------ chwila gry
SKALA_GRACZA = 0.7  # postać z klocków ma 7,7 st (jak miotacz); awatar gracza w Roblox ok. 5,4 st


def _gracz(lista, baza, kat=0, uniesienie=0.0, przezr=0.0):
    """Postać gracza (klocki, wzrost awatara) w punkcie baza (grunt), twarzą do −z (jak na stanowisku); kat = obrót
    wokół Y (180 = twarzą do kamery, jak na Bieżni)."""
    S = SCENA._Scena([0, 0, 0])
    SCENA._postac(S, "Gracz", [0, 0, 0], 180 + kat, "8FA6C8", "4A4E69",
                  [("Wlosy", [0, 7.7, 0], [2.1, 0.5, 2.1], "6B3A1F")], kol=False)
    k = SKALA_GRACZA
    for c in S.lista:
        p = c["p"]
        c["s"] = [x * k for x in c["s"]]
        c["p"] = [baza[0] + p[0] * k, baza[1] + p[1] * k + uniesienie, baza[2] + p[2] * k]
        if przezr:
            c["t"] = przezr
        lista.append(c)


def _cz(lista, n, p, s, kolor, k="B", m="SmoothPlastic", t=0.0, o=None):
    d = {"n": n, "r": "Chwila", "k": k, "p": list(p), "s": list(s), "c": kolor, "m": m}
    if t:
        d["t"] = t
    if o:
        d["o"] = o
    lista.append(d)


def chwila(D, gra):
    """Przedmioty, które w tej chwili rysuje klient (te same położenia co w KlientTreningu)."""
    W_ = D["swiat"][gra]
    L = []
    pd = W_["podest"]
    if gra == "sila":
        _gracz(L, pd, przezr=0.55)
        z = W_["strefy"]["prawo"]
        _cz(L, "Skrzynka", z, [1.6, 1.6, 1.6], "D9822B", m="WoodPlanks")
        z2 = W_["strefy"]["gora"]
        _cz(L, "Dzban", [z2[0], z2[1] + 3.2, z2[2] - 4], [1.7, 1.7, 1.7], "B07A45", k="K")
    elif gra == "pancerz":
        _gracz(L, pd)  # kamera z boku: postać nie zasłania pola gry, więc w grze jest pełna (nie półprzezroczysta)
        _cz(L, "Tarcza", W_["tarcza_blok"], [2.6, 2.9, 0.35], "3D7BE5")
    elif gra == "kondycja":
        gora_t = W_["tasma_srodek"][1] + W_["tasma_rozmiar"][1] / 2
        _gracz(L, [pd[0], gora_t, pd[2]], kat=180)
        v = W_["slad_predkosc"]
        for i, (stopa, dt) in enumerate((("lewa", 0.0), ("prawa", 0.8), ("lewa", 1.6))):
            p = W_["stopy"][stopa]
            z = p[2] + v * dt
            kol = D["ui"]["kolory"]["zloto"] if dt == 0 else D["statystyki"][1]["kolor"]
            _cz(L, "Slad%d" % i, [p[0], gora_t + 0.06, z], [0.9, 0.08, 1.5], kol, m="Neon" if dt == 0 else "SmoothPlastic")
            _cz(L, "Palce%d" % i, [p[0], gora_t + 0.06, z - 0.95], [0.75, 0.08, 0.35], kol)
        p = W_["stopy"]["lewa"]
        _cz(L, "CelSwieci", [p[0], gora_t + 0.05, p[2]], [0.06, 1.5, 1.5], D["ui"]["kolory"]["zloto"], k="C", m="Neon",
            o=[0, 0, 90], t=0.2)
    elif gra == "zrecznosc":
        _gracz(L, pd, uniesienie=2.4)  # skok nad niską kłodą (ramię obraca podglad(): kłoda tuż przed graczem)
    elif gra == "inteligencja":
        _gracz(L, pd)
        p = W_["kamienie"]["prawo"]
        ks = W_["kamien_rozmiar"]
        _cz(L, "Swiecenie", [p[0], p[1], p[2] + ks[2] / 2 + 0.08], [1.5, 1.5, 0.08], D["ui"]["kolory"]["runa_prawo"], m="Neon",
            o=[0, 0, 45])
        _cz(L, "Poswiata", [p[0], p[1], p[2] + 0.1], [ks[0] + 0.5, ks[1] + 0.5, ks[2]], D["ui"]["kolory"]["runa_prawo"],
            m="Neon", t=0.6)
    elif gra == "szczescie":
        tory = W_["tory"]
        kosz = [W_["koszyk"][i] - pd[i] for i in range(3)]
        b = tory["srodek"]
        _gracz(L, b)
        kp = [b[0] + kosz[0], b[1] + kosz[1], b[2] + kosz[2]]
        _cz(L, "KoszDno", [kp[0], kp[1] - 0.5, kp[2]], [2.6, 0.2, 2.0], "8C5A3C", m="WoodPlanks")
        for n, dx, dz, sx, sz in (("KoszL", -1.25, 0, 0.15, 2.0), ("KoszP", 1.25, 0, 0.15, 2.0), ("KoszT", 0, -0.95, 2.6, 0.15),
                                  ("KoszF", 0, 0.95, 2.6, 0.15)):
            _cz(L, n, [kp[0] + dx, kp[1], kp[2] + dz], [sx, 1.0, sz], "A86B3C", m="WoodPlanks")
        bark, dno = b[1] + 3.9, kp[1] - 0.5
        for n, dx in (("RekaL", -1.0), ("RekaP", 1.0)):
            _cz(L, n, [b[0] + dx, (bark + dno) / 2, b[2] - 0.15], [0.5, dno - bark, 0.5], "8FA6C8")
        y0, yb = W_["spad_y"] + pd[1], kp[1]
        for n, tor, a, rodzaj in (("K1", "lewy", 0.82, "koniczyna"), ("K2", "prawy", 0.35, "zlota"), ("K3", "srodek", 0.6, "kamien")):
            p = tory[tor]
            y = y0 - (y0 - yb) * a * a
            if rodzaj == "kamien":
                _cz(L, n, [p[0], y, kp[2]], [1.3, 1.3, 1.3], D["ui"]["kolory"]["kamien"], k="K")
            else:
                kol = D["ui"]["kolory"]["zloto"] if rodzaj == "zlota" else D["ui"]["kolory"]["koniczyna"]
                for j, (dx, dy) in enumerate(((-0.35, 0.2), (0.35, 0.2), (0, -0.3)) + (((0, 0.62),) if rodzaj == "zlota" else ())):
                    _cz(L, n + "L%d" % j, [p[0] + dx, y + dy, kp[2]], [0.72, 0.72, 0.72], kol, k="K", m="Neon" if rodzaj == "zlota" else "SmoothPlastic")
            _cz(L, n + "Cien", [p[0], pd[1] + 0.16, kp[2]], [0.05, 1.2 + 0.6 * a, 1.2 + 0.6 * a], "3A4A2A", k="C", o=[0, 0, 90], t=0.45)
    return L


def obroc_ramie(D, cz, kat_stopnie):
    """Ramię z kłodą (Arena/Zrecznosc/Ramie, zbudowane w stronę −x) obrócone wokół słupa tak, żeby wskazywało kąt θ
    (0° = +x, 90° = +z — gracz): obrót wokół Y o π − θ, jak w KlientTreningu."""
    W_ = D["swiat"]["zrecznosc"]
    sl = W_["slup"]
    a = 180 - kat_stopnie
    wynik = []
    for c in cz:
        if c["r"] != D["nazwy"]["ramie_klody"]:
            wynik.append(c)
            continue
        c = dict(c)
        p = c["p"]
        v = SCENA._obroc([p[0] - sl[0], p[1], p[2] - sl[2]], a)
        c["p"] = [sl[0] + v[0], v[1], sl[2] + v[2]]
        if not c.get("o"):
            c["o"] = [0, a, 0]
        wynik.append(c)
    return wynik


# ------------------------------------------------------------------------------------------------ zarys sterowania
def sterowanie(obraz, D, gra, ImageDraw, ImageFont):
    """Zarys panelu rundy i przycisków z tego samego układu co klient (logika_treningu.uklad_ui) przy 1280 × 720;
    obszar GUI zaczyna się pod paskiem Robloxa (36 px)."""
    import logika_treningu as LT
    U = D["ui"]
    sk = LT.skala_ui(D, W, H)
    gora = U["pasek_gorny_pt"]
    R = LT.uklad_ui(D, gra, W, H - gora, sk)
    dr = ImageDraw.Draw(obraz, "RGBA")
    f = _czcionka(int(15 * sk), ImageFont)
    st = [s for s in D["statystyki"] if s["id"] == gra][0]
    kol = st["kolor"]

    def prost(nazwa):
        x0, y0, x1, y1 = R[nazwa]
        return x0, y0 + gora, x1, y1 + gora

    def przycisk(x0, y0, x1, y1, tekst, kolor, okragly=False):
        k = _kolor(kolor) + (225,)
        if okragly:
            dr.ellipse([x0, y0, x1, y1], fill=k, outline=(23, 18, 31, 255), width=2)
        else:
            dr.rounded_rectangle([x0, y0, x1, y1], radius=10 * sk, fill=k, outline=(23, 18, 31, 255), width=2)
        tw = dr.textlength(tekst, font=f)
        dr.text(((x0 + x1 - tw) / 2, (y0 + y1) / 2 - 9 * sk), tekst, font=f, fill=(255, 246, 224, 255))
    x0, y0, x1, y1 = prost("status")
    dr.rounded_rectangle([x0, y0, x1, y1], radius=12 * sk, fill=(255, 246, 224, 225), outline=(23, 18, 31, 255), width=3)
    dr.text((x0 + 8 * sk, y0 + 4 * sk), "0:34     SERIA 7    ×1,25", font=_czcionka(int(18 * sk), ImageFont), fill=(23, 18, 31, 255))
    dr.rounded_rectangle([x0 + 8 * sk, y0 + 34 * sk, x1 - 8 * sk, y0 + 43 * sk], radius=3, fill=_kolor(U["kolory"]["zloto"]) + (255,))
    przycisk(*prost("przerwij"), "X", "E5533D")

    def krzyz(nazwa, rozmiar, kolory, napisy):
        x0, y0, _, _ = prost(nazwa)
        b, g = rozmiar * sk, U["odstep_px"] * sk
        for i, (cx, cy) in enumerate(((1, 0), (0, 1), (2, 1), (1, 2))):
            przycisk(x0 + cx * (b + g), y0 + cy * (b + g), x0 + cx * (b + g) + b, y0 + cy * (b + g) + b, napisy[i], kolory[i])
    if gra == "sila":
        krzyz("krzyz", U["przycisk_px"], [kol] * 4, ["W", "A", "D", "S"])
    elif gra == "pancerz":
        przycisk(*prost("blok"), "BLOK", kol, True)
    elif gra == "kondycja":
        przycisk(*prost("stopaL"), "LEWA  A", kol)
        przycisk(*prost("stopaP"), "PRAWA  D", kol)
    elif gra == "zrecznosc":
        x0, y0, x1, y1 = prost("unik")
        b = U["unik_px"] * sk
        przycisk(x0, y0, x1, y0 + b, "SKOK", kol)
        przycisk(x0, y1 - b, x1, y1, "PADNIJ", kol)
    elif gra == "inteligencja":
        krzyz("runy", U["runa_px"], [U["kolory"]["runa_" + k] for k in ("gora", "lewo", "prawo", "dol")], [""] * 4)
        x0, y0, x1, y1 = prost("postep")
        dr.rounded_rectangle([x0, y0, x1, y1], radius=10 * sk, fill=(23, 18, 31, 225))
    elif gra == "szczescie":
        przycisk(*prost("torL"), "LEWO A", kol)
        przycisk(*prost("torP"), "PRAWO D", kol)
    # miejsce dużych napisów stanowiska („SERIA 10!”, „+1 Siła!”): zarys największego słowa z gwiazdą
    KX = U["komiks"]
    tekst = D["teksty"]["punkt"] % (1, st["nazwa"])
    wys = KX["rozmiary_px"][KX["style"]["punkt"]["rozmiar"]]
    szer = wys * max(1.2, len(tekst) * KX["szerokosc_znaku"] * 1.12)
    bok = KX["gwiazda"]["bok"] * wys * math.sqrt(2)
    w2, h2 = (szer + 10) * sk, (max(wys, bok) + 10) * sk
    n = D["swiat"][gra]["napis"]
    cx, cy = W * n[0], gora + (H - gora) * n[1]
    mg = KX["margines_px"]
    cx = min(max(cx, mg + w2 / 2), W - mg - w2 / 2)  # długi napis przesuwa się w bok, żeby zmieścić się na ekranie (jak w grze)
    dr.rectangle([cx - w2 / 2, cy - h2 / 2, cx + w2 / 2, cy + h2 / 2], outline=(232, 54, 79, 255), width=2)
    for i, kolor_g in enumerate(KX["gwiazda"]["kolory"]):
        r = KX["gwiazda"]["bok"] * wys * sk / 2
        a = math.radians(KX["gwiazda"]["obrot"][i])
        rogi = [(cx + r * math.sqrt(2) * math.cos(a + math.pi / 4 + j * math.pi / 2),
                 cy + r * math.sqrt(2) * math.sin(a + math.pi / 4 + j * math.pi / 2)) for j in range(4)]
        dr.polygon(rogi, fill=_kolor(kolor_g) + (235,), outline=(23, 18, 31, 255))
    fk = _czcionka(int(wys * 0.62 * sk), ImageFont)
    tw = dr.textlength(tekst.upper(), font=fk)
    for dx, dy, barwa in ((2 * sk, 3 * sk, (23, 18, 31, 255)), (0, 0, _kolor(KX["kolory"]["krytyk"]) + (255,))):
        dr.text((cx - tw / 2 + dx, cy - wys * 0.36 * sk + dy), tekst.upper(), font=fk, fill=barwa, stroke_width=2,
                stroke_fill=(23, 18, 31, 255))
    dr.text((10, H - 22), "Podgląd brył (render bez Studio, nie zrzut z gry)", font=_czcionka(14, ImageFont),
            fill=(23, 18, 31, 200))


# ------------------------------------------------------------------------------------------------ główna
def ujecie_podgladu(D, gra, ujecie):
    """Ujęcie kamery do podglądu (ten sam rachunek co w grze — kamera_treningu.py): gra | start | final."""
    import kamera_treningu as KT
    import logika_treningu as LT
    if ujecie == "start":
        return KT.odliczanie(D, gra, D["runda"]["odliczanie_s"])
    if ujecie == "final":
        U = D["ui"]
        s = LT.skala_ui(D, W, H)
        fx = KT.ulamek_postaci(D, 0, W, W, s)
        baza = KT.miejsca_postaci(D, gra)[0]
        korzen = [baza[0], baza[1] + U["kamera"]["final"]["korzen_nad_ziemia"], baza[2]]
        return KT.final(D, gra, korzen, fx, W / H, U["kamera"]["final"]["dojazd_s"])
    return KT.gra(D, gra)


def karta(obraz, D, gra, ImageDraw, ImageFont):
    """Zarys karty podsumowania (prawa część ekranu) na podglądzie zbliżenia po rundzie."""
    import kamera_treningu as KT
    import logika_treningu as LT
    U = D["ui"]
    sk = LT.skala_ui(D, W, H)
    gora = U["pasek_gorny_pt"]
    x0, y0, x1, y1 = KT.karta_podsumowania(D, W, H - gora, sk)
    dr = ImageDraw.Draw(obraz, "RGBA")
    dr.rounded_rectangle([x0, y0 + gora, x1, y1 + gora], radius=14 * sk, fill=(255, 246, 224, 235), outline=(23, 18, 31, 255),
                         width=3)
    dr.rounded_rectangle([x0 - 8 * sk, y0 + gora - 14 * sk, x1 + 8 * sk, y0 + gora + 34 * sk], radius=10 * sk,
                         fill=_kolor(U["komiks"]["kolory"]["pomarancz"]) + (255,), outline=(23, 18, 31, 255), width=3)
    f = _czcionka(int(24 * sk), ImageFont)
    tekst = D["teksty"]["koniec"]
    dr.text(((x0 + x1 - dr.textlength(tekst, font=f)) / 2, y0 + gora - 6 * sk), tekst, font=f,
            fill=_kolor(U["komiks"]["kolory"]["zolty"]) + (255,))
    dr.text((10, H - 22), "Podgląd brył (render bez Studio, nie zrzut z gry)", font=_czcionka(14, ImageFont),
            fill=(23, 18, 31, 200))


def podglad(D, gra, np, Image, ImageDraw, ImageFont, ujecie="gra"):
    cz = SCENA.czesci(D)
    if gra == "arena":
        A = D["arena"]
        c = A["srodek"]
        oko = [c[0], c[1] + 70, c[2] + 92]
        cel = [c[0], c[1], c[2] - 6]
        kat = 70.0
        lista = cz
    else:
        u = ujecie_podgladu(D, gra, ujecie)
        oko, cel, kat = u["oko"], u["cel"], u["kat"]
        if gra == "zrecznosc" and ujecie != "final":
            cz = obroc_ramie(D, cz, 90 + 24)
        lista = cz + (postac_finalu(D, gra) if ujecie == "final" else chwila(D, gra))
    kam, pl = rysuj(lista, oko, cel, np, kat)
    obrysy(pl, np)
    obraz = napisy(pl, kam, lista, np, Image, ImageDraw, ImageFont)
    if gra != "arena" and ujecie == "gra":
        sterowanie(obraz, D, gra, ImageDraw, ImageFont)
    elif gra != "arena" and ujecie == "final":
        karta(obraz, D, gra, ImageDraw, ImageFont)
    return obraz


def postac_finalu(D, gra):
    """Postać gracza po rundzie: obrócona twarzą do kamery zbliżenia, ręce w górze (radość)."""
    import kamera_treningu as KT
    baza = KT.miejsca_postaci(D, gra)[0]
    kier = KT.kierunek_finalu(D, gra, 0)
    kat = math.degrees(math.atan2(kier[0], kier[2]))  # obrót wokół Y: twarz (+z postaci z klocków) w stronę kamery
    L = []
    S = SCENA._Scena([0, 0, 0])
    SCENA._postac(S, "Gracz", [0, 0, 0], kat, "8FA6C8", "4A4E69", [("Wlosy", [0, 7.7, 0], [2.1, 0.5, 2.1], "6B3A1F")], kol=False)
    k = SKALA_GRACZA
    for c in S.lista:
        if c["n"] in ("RamieL", "RamieP"):  # ręce w górę
            dx = -2.0 if c["n"] == "RamieL" else 2.0
            v = SCENA._obroc([dx, 6.9, 0], kat)
            c["p"] = [v[0], v[1], v[2]]
        p = c["p"]
        c["s"] = [x * k for x in c["s"]]
        c["p"] = [baza[0] + p[0] * k, baza[1] + p[1] * k, baza[2] + p[2] * k]
        L.append(c)
    return L


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Podglądy stanowisk Training Center (render brył)")
    ap.add_argument("--tylko", default=None)
    ap.add_argument("--wyj", default=os.path.join(TU, "podglady"))
    ap.add_argument("--ujecie", default="gra", choices=("gra", "start", "final"))
    ap.add_argument("--ekran", default=None, help="rozmiar kadru, np. 667x375 (domyślnie 1280x720)")
    a = ap.parse_args()
    najnizszy_priorytet()
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    global W, H
    if a.ekran:
        W, H = [int(x) for x in a.ekran.lower().split("x")]
    _, D = DANE.wczytaj()
    gry = [a.tylko] if a.tylko else ["kondycja", "zrecznosc", "inteligencja", "szczescie", "sila", "pancerz", "arena"]
    if a.ujecie != "gra":
        gry = [g for g in gry if g != "arena"]
    os.makedirs(a.wyj, exist_ok=True)
    for g in gry:
        obraz = podglad(D, g, np, Image, ImageDraw, ImageFont, a.ujecie)
        przyrostek = ("" if a.ujecie == "gra" else "_" + a.ujecie) + ("_%s" % a.ekran.lower() if a.ekran else "")
        nazwa = os.path.join(a.wyj, "podglad_%s%s.jpg" % (g, przyrostek))
        obraz.convert("RGB").save(nazwa, "JPEG", quality=88)
        print("zapisano", os.path.relpath(nazwa, os.path.dirname(os.path.dirname(TU))).replace("\\", "/"))


if __name__ == "__main__":
    main()
