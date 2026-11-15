# -*- coding: utf-8 -*-
"""Teren biomu Las z klocków: płyta, plamy podbiomów, poziomy (pryzmaty z klinów), skały na krawędziach, kopce,
rampy, woda (cienka tafla), ścieżki z krawężnikami i kamieniami-kodami, Mur Pni, tło i chmury.

Wszystko w układzie lasu (generuj.py nakłada przesunięcie i obrót kontenera). Wysokości z geo.Teren — ta sama funkcja
steruje kontrolą, więc ścieżka leży dokładnie tam, gdzie sprawdz.py jej szuka.
Poziomy nawierzchni nad gruntem (odstęp ≥ 0,05 między płaszczyznami różnych kolorów): plamy podbiomów 0,06; podkładki
stref walki 0,10; brzeg wody 0,14; woda 0,18 (stawy 0,20 / 0,22); ścieżki 0,30; krawężniki 0,42; kamienie-kody 0,5.
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biblioteka.scena import katy_z_macierzy  # noqa: E402
from swiat.biom_las import geo, rosliny, skaly  # noqa: E402
from swiat.biom_las.paleta import cien, KOD_PODBIOMU  # noqa: E402
from swiat.krzywe_miasteczko import zestaw  # noqa: E402

Y_PLAMA, Y_PODKLADKA, Y_BRZEG, Y_WODA, Y_SCIEZKA, Y_KRAWEZNIK = 0.06, 0.10, 0.14, 0.18, 0.30, 0.42
KOLOR_PODBIOMU = {"laka": "trawa", "kapeluszowo": "runo_ciemne", "serce": "runo", "ostepy": "runo", "wawoz": "ziemia",
                  "korona": "runo"}
KOLOR_POZIOMU = {"polka_zach": "bruk_ciemny", "polka_pd": "bruk_ciemny", "polka_wsch": "bruk_ciemny", "tama": "kamien_cokol",
                 "jezioro_dno": "woda_gleboka", "korona_t1": "runo_ciemne", "korona_t2": "trawa", "korona_p": "runo_ciemne",
                 "gran": "runo_ciemne"}
SKALA_POZIOMU = {"gran": ("kamien_lochu", "Slate"), "korona_t1": ("kamien_cieply", "SmoothPlastic"),
                 "korona_t2": ("kamien_cieply", "SmoothPlastic"), "korona_p": ("kamien_cieply", "SmoothPlastic"),
                 "polka_zach": ("kamien_cieply", "SmoothPlastic"), "polka_pd": ("kamien_cieply", "SmoothPlastic"),
                 "polka_wsch": ("kamien_cieply", "SmoothPlastic")}
Y_DROGI = {"glowna": 0.32, "polana": 0.30, "sekretna": 0.28, "boczna": 0.26, "labirynt": 0.26}   # różne płaszczyzny na skrzyżowaniach
KOD_SCIEZKI = {"szlak_uklonu_pld": "pomarancz", "szlak_uklonu_pln": "biel", "wilczy_trakt": "dach_sklep",
               "trakt_wawozem": "dach_brama"}


# =========================================================================== prymitywy płaskie
def _prostokatny(s, nazwa, F, K, R, y_gora, grub, kolor, mat):
    vx, vz = K[0] - F[0], K[1] - F[1]
    d = math.hypot(vx, vz)
    ux, uz = R[0] - F[0], R[1] - F[1]
    h = math.hypot(ux, uz)
    if d < 0.05 or h < 0.05:
        return
    v, u = (vx / d, vz / d), (ux / h, uz / h)
    Y = (u[0], 0.0, u[1])
    Zz = (-v[0], 0.0, -v[1])
    X = (0.0, u[0] * v[1] - u[1] * v[0], 0.0)
    m = ((X[0], Y[0], Zz[0]), (X[1], Y[1], Zz[1]), (X[2], Y[2], Zz[2]))
    rx, ry, rz = katy_z_macierzy(m)
    cx = F[0] + u[0] * h / 2.0 + v[0] * d / 2.0
    cz = F[1] + u[1] * h / 2.0 + v[1] * d / 2.0
    s.klin(nazwa, (cx, y_gora - grub / 2.0, cz), (grub, h, d), kolor, mat, (rx, ry, rz))


def trojkat(s, nazwa, A, B, C, y_gora, grub, kolor, mat="SmoothPlastic"):
    """Płaski trójkąt (x, z) z dwóch klinów leżących na boku; grub = grubość w dół od y_gora (pryzmat, gdy duża)."""
    p = [A, B, C]
    i, j, k = max(((0, 1, 2), (1, 2, 0), (2, 0, 1)), key=lambda e: (p[e[0]][0] - p[e[1]][0]) ** 2 + (p[e[0]][1] - p[e[1]][1]) ** 2)
    P, Q, R = p[i], p[j], p[k]
    ex, ez = Q[0] - P[0], Q[1] - P[1]
    l2 = ex * ex + ez * ez
    if l2 < 1e-6:
        return
    t = ((R[0] - P[0]) * ex + (R[1] - P[1]) * ez) / l2
    F = (P[0] + t * ex, P[1] + t * ez)
    _prostokatny(s, nazwa, F, P, R, y_gora, grub, kolor, mat)
    _prostokatny(s, nazwa, F, Q, R, y_gora, grub, kolor, mat)


def wielokat(s, nazwa, w, y_gora, grub, kolor, mat="SmoothPlastic"):
    for a, b, c in geo.triangulacja(w):
        trojkat(s, nazwa, a, b, c, y_gora, grub, kolor, mat)


def wstega(s, nazwa, a, b, szer, grub, kolor, mat="SmoothPlastic", rot_dod=0.0):
    """Blok od a do b (punkty 3D wierzchu), szerokość szer, grubość w dół grub — pochyla się z terenem."""
    dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    dl = math.sqrt(dx * dx + dy * dy + dz * dz)
    if dl < 0.05:
        return
    rx = math.degrees(math.asin(max(-1.0, min(1.0, -dy / dl))))
    ry = math.degrees(math.atan2(dx, dz))
    with s.uklad(pos=((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0, (a[2] + b[2]) / 2.0), obrot=(rx, ry, 0)):
        s.blok(nazwa, (0, -grub / 2.0, 0), (szer, grub, dl), kolor, mat, rot=(0, rot_dod, 0))


def dysk(s, nazwa, x, y_gora, z, r, grub, kolor, mat="SmoothPlastic", alfa=0.0):
    s.walec(nazwa, (x, y_gora - grub / 2.0, z), r, grub, kolor, mat, os="y", alfa=alfa)


# =========================================================================== grunt i poziomy
def grunt(s, G):
    U = G.U
    with s.grupa("Teren/Grunt"), s.cechy(cien=False):
        s.blok("Płyta", (0, -1.0, 0), (1400.0, 2.0, 1400.0), "runo")
        for b in U["podbiomy"]:
            kol = KOLOR_PODBIOMU[b["id"]]
            if kol == "runo":
                continue
            wielokat(s, "Plama " + b["id"], b["wielokat"], Y_PLAMA, 0.3, kol)
    # poziomy: pryzmaty od −1 do y (kolor wierzchu), skały na krawędziach, gdzie na zewnątrz jest niżej
    for e in G.T.poziomy:
        with s.grupa("Teren/Poziomy/" + e["id"]):
            sciana = SKALA_POZIOMU.get(e["id"], ("kamien_cieply", "SmoothPlastic"))
            if e["id"] in ("jezioro_dno", "tama"):
                wielokat(s, "Poziom", e["wielokat"], e["y"], e["y"] + 1.0, KOLOR_POZIOMU[e["id"]])
                continue
            # pryzmat w kolorze skały (ściany urwisk czyta się jak kamień, nie jak zielony mur) i cienki wierzch
            wielokat(s, "Poziom", e["wielokat"], e["y"] - 0.05, e["y"] + 0.95, sciana[0], sciana[1])
            with s.cechy(cien=False):
                wielokat(s, "Poziom wierzch", e["wielokat"], e["y"] + Y_PLAMA, 0.3, KOLOR_POZIOMU.get(e["id"], "runo"))
    skaly_krawedzi(s, G)
    # kopce: walec + pierścień klinów
    for e in G.T.kopce:
        cx, cz = e["srodek"]
        kol = "runo" if e["id"] == "polana_uklonu" else "trawa"
        with s.grupa("Teren/Kopce/" + e["id"]), s.cechy(cien=False):
            s.walec("Kopiec", (cx, (e["y"] - 1.0) / 2.0, cz), e["r"] + 0.6, e["y"] + 1.0, kol, os="y")
            n = 28 if e["r_stopy"] > 60 else 18
            r_in, r_out = e["r"] - 0.4, e["r_stopy"]
            szer = 2 * r_out * math.tan(math.pi / n) + 1.0
            for k in range(n):
                a = 2 * math.pi * (k + 0.5) / n
                dx, dz = math.cos(a), math.sin(a)
                ry = math.degrees(math.atan2(-dx, -dz))
                with s.uklad(pos=(cx, 0, cz), obrot=(0, ry, 0)):
                    s.klin("Zbocze", (0, e["y"] / 2.0, -(r_in + r_out) / 2.0), (szer, e["y"], r_out - r_in), kol)
    # rampy
    with s.grupa("Teren/Rampy"):
        for e in G.T.rampy:
            (ax, az, ay), (bx, bz, by) = e["od"], e["do"]
            L = math.hypot(bx - ax, bz - az)
            ry = math.degrees(math.atan2(bx - ax, bz - az))
            with s.uklad(pos=((ax + bx) / 2.0, ay, (az + bz) / 2.0), obrot=(0, ry, 0)):
                s.klin("Rampa", (0, (by - ay) / 2.0, 0), (e["szer"], by - ay, L), "kamien_cieply")
                with s.cechy(kolizja=False):
                    for zn in (-1, 1):
                        s.klin("Rampa policzek", (zn * (e["szer"] / 2.0 + 0.3), (by - ay) / 2.0 + 0.25, 0),
                               (0.6, by - ay + 0.5, L), "tusz")


def _krawedzie(w):
    """Krawędzie wielokąta z normalną na zewnątrz: [(a, b, (nx, nz)), …]."""
    pts = [tuple(p) for p in w]
    ccw = geo.pole(pts) > 0
    wyn = []
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        dx, dz = b[0] - a[0], b[1] - a[1]
        dl = math.hypot(dx, dz)
        if dl < 1e-6:
            continue
        nx, nz = (dz / dl, -dx / dl) if ccw else (-dz / dl, dx / dl)
        wyn.append((a, b, (nx, nz)))
    return wyn


def skaly_krawedzi(s, G):
    """Skały wzdłuż krawędzi poziomów tam, gdzie na zewnątrz jest niżej o ≥ 3 (urwiska). Pomija rampy, koronę tamy
    (tama ma własne głazy) i krawędzie poza murem."""
    T, rnd = G.T, G.rnd_teren
    for e in T.poziomy:
        if e["id"] in ("tama", "jezioro_dno"):
            continue
        kolor, mat = SKALA_POZIOMU.get(e["id"], ("kamien_cieply", "SmoothPlastic"))
        pb = e.get("podbiom", "wawoz")
        with s.grupa("%s/Urwiska/%s" % (G.GRUPA_PODBIOMU[pb], e["id"])):
            for a, b, (nx, nz) in _krawedzie(e["wielokat"]):
                dl = math.hypot(b[0] - a[0], b[1] - a[1])
                n = max(1, int(round(dl / 12.5)))
                for k in range(n):
                    t = (k + 0.5) / n
                    p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                    if max(abs(p[0]), abs(p[1])) > 462:
                        continue
                    h_out = T.H(p[0] + nx * 4.0, p[1] + nz * 4.0)
                    h_in = T.H(p[0] - nx * 4.0, p[1] - nz * 4.0)
                    if h_in - h_out < 3.0:
                        continue
                    if T.rampa_w(p[0] + nx * 3.0, p[1] + nz * 3.0, zapas=7.0) or T.rampa_w(p[0], p[1], zapas=7.0):
                        continue
                    ry = math.degrees(math.atan2(nx, nz))
                    skaly.skala_urwiska(s, rnd, p, ry, h_out - 0.5, h_in, kolor, mat, dl=dl / n + rnd.uniform(1.5, 4.0))


# =========================================================================== woda
def woda(s, G):
    U, rnd = G.U, G.rnd_woda
    with s.grupa("Woda/Struga"), s.cechy(kolizja=False, cien=False):
        for w in U["woda"]:
            if w["rodzaj"] != "struga":
                continue
            pts = geo.wygladz(w["pts"], 3)
            w0, w1 = w["szer"]
            szer = [w0 + (w1 - w0) * (0.5 + 0.5 * math.sin(i * 0.7)) for i in range(len(pts))]
            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i + 1]
                sz = (szer[i] + szer[i + 1]) / 2.0
                wstega(s, "Brzeg wody", (a[0], Y_BRZEG, a[1]), (b[0], Y_BRZEG, b[1]), sz + (2.4 if sz > 6 else 0.8), 0.2, "woda_gleboka")
                wstega(s, "Woda", (a[0], Y_WODA, a[1]), (b[0], Y_WODA, b[1]), sz, 0.2, "woda")
            for i, p in enumerate(pts[1:-1], 1):
                dysk(s, "Brzeg wody", p[0], Y_BRZEG, p[1], szer[i] / 2.0 + (1.2 if szer[i] > 6 else 0.4), 0.2, "woda_gleboka")
                dysk(s, "Woda", p[0], Y_WODA, p[1], szer[i] / 2.0, 0.2, "woda")
            if w["id"] != "kreta_struga":
                continue
            # bliki, kamienie brzegu i trzcina
            for i in range(2, len(pts) - 2, 2):
                a, b = pts[i], pts[i + 1]
                dx, dz = b[0] - a[0], b[1] - a[1]
                dl = math.hypot(dx, dz) or 1.0
                nx, nz = -dz / dl, dx / dl
                zn = 1 if i % 4 == 0 else -1
                if G.przy_przeprawie(a[0], a[1], 14) or G.na_sciezce(a[0], a[1], 6):
                    continue
                if i % 6 == 0:
                    s.blok("Blik", (a[0] + nx * 1.5, Y_WODA + 0.05, a[1] + nz * 1.5), (0.6, 0.1, 2.6), "biel",
                           rot=(0, math.degrees(math.atan2(dx, dz)), 0))
                bx, bz = a[0] + zn * nx * (szer[i] / 2.0 + 2.2), a[1] + zn * nz * (szer[i] / 2.0 + 2.2)
                if G.na_sciezce(bx, bz, 3):
                    continue
                with s.cechy(kolizja=True, cien=True):
                    skaly.kanciak(s, rnd, (bx, 0.0, bz), rnd.uniform(0.8, 1.4), rnd.uniform(0, 360))
                G.zajmij(bx, bz, 2.5)
                if i % 3 == 0:
                    tx, tz = a[0] - zn * nx * (szer[i] / 2.0 + 1.6), a[1] - zn * nz * (szer[i] / 2.0 + 1.6)
                    if not G.na_sciezce(tx, tz, 3):
                        rosliny.trzcina(s, rnd, (tx, 0.0, tz))
                        rosliny.trzcina(s, rnd, (tx + 0.9, 0.0, tz - 0.6))
    with s.grupa("Woda/Stawy"), s.cechy(kolizja=False, cien=False):
        for w in U["woda"]:
            if w["rodzaj"] != "staw":
                continue
            cx, cz = w["srodek"]
            r = w["r"]
            dysk(s, "Brzeg stawu", cx, Y_BRZEG, cz, r + 1.6, 0.2, "woda_gleboka")
            dysk(s, "Staw", cx, Y_WODA + 0.02, cz, r, 0.2, "woda")
            dysk(s, "Staw głębia", cx, Y_WODA + 0.04, cz, r * 0.55, 0.2, "woda_gleboka")
            n = int(2 * math.pi * r / 7.0)
            for k in range(n):
                a = 2 * math.pi * k / n + rnd.uniform(-0.1, 0.1)
                x, z = cx + (r + 2.0) * math.cos(a), cz + (r + 2.0) * math.sin(a)
                if G.na_sciezce(x, z, 2) or G.przy_przeprawie(x, z, 8):
                    continue
                with s.cechy(kolizja=True, cien=True):              # płaskie (≤ 1): wokół stawu są place walki
                    s.blok("Kamień brzegu", (x, 0.3, z), (rnd.uniform(2.4, 3.6), 0.8, rnd.uniform(1.8, 2.6)),
                           "kamien_cieply" if k % 2 else cien(s, "kamien_cieply", 0.85), rot=(0, rnd.uniform(0, 180), rnd.uniform(-4, 4)))
    with s.grupa("Woda/Jezioro"), s.cechy(kolizja=False, cien=False):
        jez = next(w for w in U["woda"] if w["id"] == "jezioro")
        wielokat(s, "Jezioro", jez["wielokat"], jez["y"], 0.3, "woda")
        for a, b, _ in _krawedzie(jez["wielokat"]):
            dl = math.hypot(b[0] - a[0], b[1] - a[1])
            for k in range(int(dl / 7.0)):
                t = (k + 0.5) / max(1, int(dl / 7.0))
                x, z = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                if max(abs(x), abs(z)) > 440:
                    continue
                rosliny.trzcina(s, rnd, (x, jez["dno"], z))


# =========================================================================== ścieżki
def sciezki(s, G):
    U, T, rnd = G.U, G.T, G.rnd_sciezki
    kolor = {"glowna": "bruk", "boczna": "ziemia", "polana": "ziemia", "labirynt": "ziemia", "sekretna": "kamien_cieply"}
    most = next(p for p in U["przeprawy"] if p["id"] == "most_rechotek")
    czapki = set()
    for sc in U["sciezki"]:
        szer = sc["szer"]
        kol = kolor[sc["rodzaj"]]
        with s.grupa("Sciezki/" + sc["id"]), s.cechy(cien=False):
            pts = sc["pts"]
            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i + 1]
                dl = math.dist(a, b)
                n = max(1, int(math.ceil(dl / 6.0)))
                hs = [T.H(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n + 1)]
                plaska = max(hs) - min(hs) < 0.05
                kroki = [(0, n)] if plaska else [(k, k + 1) for k in range(n)]
                for k0, k1 in kroki:
                    p0 = (a[0] + (b[0] - a[0]) * k0 / n, a[1] + (b[1] - a[1]) * k0 / n)
                    p1 = (a[0] + (b[0] - a[0]) * k1 / n, a[1] + (b[1] - a[1]) * k1 / n)
                    if math.hypot((p0[0] + p1[0]) / 2 - most["x"], (p0[1] + p1[1]) / 2 - most["z"]) < 9:
                        continue
                    wstega(s, "Ścieżka", (p0[0], hs[k0] + Y_DROGI[sc["rodzaj"]], p0[1]), (p1[0], hs[k1] + Y_DROGI[sc["rodzaj"]], p1[1]),
                           szer, 0.5, kol)
            # po przeglądzie: kanciasty koniec szlaku na skrzyżowaniu (np. przy bramie) wystawał trójkątem na dróżkę —
            # końce też dostają okrągłą czapkę
            for i in range(0, len(pts)):
                x, z = pts[i]
                klucz = (round(x, 1), round(z, 1), sc["rodzaj"], szer)
                if klucz in czapki:                             # pętla albo dwie ścieżki z tym samym węzłem
                    continue
                czapki.add(klucz)
                if T.rampa_w(x, z, 1.0) is None and math.hypot(x - most["x"], z - most["z"]) > 9:
                    dysk(s, "Ścieżka", x, T.H(x, z) + Y_DROGI[sc["rodzaj"]], z, szer / 2.0, 0.5, kol)
            # krawężniki: szlaki główne wszędzie na płaskim, dróżki tylko na trawie Łąki
            if sc["rodzaj"] in ("glowna", "boczna"):
                kraweznik(s, G, sc)
            if sc["id"] in KOD_SCIEZKI:
                kamienie_kody(s, G, sc, KOD_SCIEZKI[sc["id"]])


def kraweznik(s, G, sc):
    T = G.T
    szer = sc["szer"]
    pol = szer / 2.0 + 0.3
    laka = G.pod["laka"]["wielokat"]
    with s.cechy(kolizja=False, cien=False):
        for zn in (-1, 1):
            bieg = []
            for x, z, dx, dz in geo.punkty_co(sc["pts"], 1.0):
                px, pz = x - dz * zn * pol, z + dx * zn * pol
                ok = (T.rampa_w(px, pz, 1.0) is None and abs(T.H(px, pz) - T.H(x, z)) < 0.05 and G.woda_odl(px, pz) > 0.5
                      and not G.na_sciezce(px, pz, 0.6, pomin=sc)
                      and (sc["rodzaj"] == "glowna" or geo.w_wielokacie((px, pz), laka)))
                if ok:
                    bieg.append((px, pz))
                else:
                    if len(bieg) >= 2:
                        _odcinki_kraweznika(s, T, bieg)
                    bieg = []
            if len(bieg) >= 2:
                _odcinki_kraweznika(s, T, bieg)


def _odcinki_kraweznika(s, T, bieg):
    """Łamana krawężnika uproszczona do odcinków ≤ 12, z wierzchem na Y_KRAWEZNIK nad gruntem."""
    i = 0
    while i < len(bieg) - 1:
        j = min(len(bieg) - 1, i + 12)
        a, b = bieg[i], bieg[j]
        if math.dist(a, b) >= 0.8:
            ha, hb = T.H(*a), T.H(*b)
            wstega(s, "Krawężnik", (a[0], ha + Y_KRAWEZNIK, a[1]), (b[0], hb + Y_KRAWEZNIK, b[1]), 0.6, 0.35, "tusz")
        i = j


def kamienie_kody(s, G, sc, kod):
    """Kamień-kod 1 × 0,4 × 1 w kolorze celu szlaku co 20 st, na przemian po obu stronach, za krawężnikiem."""
    T = G.T
    pol = sc["szer"] / 2.0 + 1.6
    zn = 1
    with s.cechy(kolizja=False, cien=False):
        for i, (x, z, dx, dz) in enumerate(geo.punkty_co(sc["pts"], 20.0)):
            if i == 0:
                continue
            px, pz = x - dz * zn * pol, z + dx * zn * pol
            zn = -zn
            if T.rampa_w(px, pz, 2.0) or G.na_sciezce(px, pz, 0.8, pomin=sc) or G.woda_odl(px, pz) < 1:
                continue
            s.blok("Kamień-kod", (px, T.H(px, pz) + 0.3, pz), (1.1, 0.5, 1.1), kod, rot=(0, math.degrees(math.atan2(dx, dz)) + 45, 0))


# =========================================================================== mur, tło, chmury
def mur(s, G):
    """Mur Pni: pas 436–466 z dużymi skałami-kulisami co ok. 24 i dwoma rzędami ciemnych kulis-drzew; niewidzialna
    ściana na 470. Nad urwiskiem pod Ławką (płaskowyż 32) i nad jeziorem tylko niskie skały — widok zostaje otwarty."""
    T, rnd = G.T, G.rnd_mur
    with s.grupa("Mur/Sciana"), s.cechy(cien=False):
        for x, z, sx, sz in ((0, -471, 944, 2), (0, 471, 944, 2), (-471, 0, 2, 944), (471, 0, 2, 944)):
            s.blok("Niewidzialna ściana", (x, 90.0, z), (sx, 200.0, sz), "biel", alfa=1.0)
    obwod = []
    for bok in range(4):
        for k in range(0, 940, 4):
            t = -470 + k
            obwod.append({0: (t, -450), 1: (450, t), 2: (-t, 450), 3: (-450, -t)}[bok] + (bok,))
    with s.grupa("Mur/Skaly"):
        for i in range(0, len(obwod), 6):
            x, z, bok = obwod[i]
            x += rnd.uniform(-8, 8) if bok in (1, 3) else 0
            z += rnd.uniform(-8, 8) if bok in (0, 2) else 0
            if G.w_przerwie_muru(x, z):
                continue
            h0 = T.H(x, z)
            niski = h0 >= 30 or h0 == 9.5
            h = rnd.uniform(3, 7) if niski else rnd.uniform(16, 30)
            ry = {0: 0, 1: 90, 2: 180, 3: 270}[bok] + rnd.uniform(-20, 20)
            kol = "kamien_lochu" if bok == 0 and x < -150 else ("kamien_cieply" if rnd.random() < 0.6 else cien(s, "kamien_cieply", 0.85))
            with s.uklad(pos=(x, h0, z), obrot=(rnd.uniform(-8, 8), ry, rnd.uniform(-10, 10))):
                s.blok("Skała muru", (0, h / 2.0 - 1.0, 0), (rnd.uniform(14, 22), h + 2.0, rnd.uniform(10, 16)), kol,
                       "Slate" if kol == "kamien_lochu" else "SmoothPlastic")
                with s.cechy(kolizja=False):
                    s.naroznik("Skała muru wierzch", (0, h + 1.2, 0), (rnd.uniform(9, 13), 2.6, rnd.uniform(7, 10)),
                               cien(s, kol, 1.05) if kol != "kamien_lochu" else "dach_dom_lupek", rot=(0, rnd.choice((0, 90, 180, 270)), 0))
    with s.grupa("Mur/Drzewa"):
        for rzad, (off, krok) in enumerate(((440, 3), (458, 3))):
            for i in range(rzad, len(obwod), krok):
                x, z, bok = obwod[i]
                d = off - 450
                x, z = {0: (x, z - d), 1: (x + d, z), 2: (x, z + d), 3: (x - d, z)}[bok]
                x += rnd.uniform(-3, 3)
                z += rnd.uniform(-3, 3)
                if G.w_przerwie_muru(x, z):
                    continue
                h0 = T.H(x, z)
                if h0 >= 30 or h0 == 9.5:
                    continue
                kol = "sylweta_1" if rzad == 0 else cien(s, "sylweta_1", 0.85)
                with s.cechy(kolizja=False, cien=False):       # pnie muru bez kolizji: zatrzymuje niewidzialna ściana i skały
                    rosliny.kulisa(s, rnd, (x, h0, z), rnd.uniform(1.0, 1.4), rnd.uniform(0, 90), kol, wys=rnd.uniform(24, 38))


def tlo(s, G):
    rnd = G.rnd_tlo
    with s.grupa("Tlo/Las"), s.cechy(kolizja=False, cien=False):
        for bok in range(4):
            for t in range(-540, 541, 18):
                off = rnd.uniform(482, 528)
                x, z = {0: (t, -off), 1: (off, t), 2: (t, off), 3: (-off, t)}[bok]
                if z < -470 and -40 < x < 140:
                    continue                                  # przerwa: z Ławki widać sylwetkę miasteczka
                rosliny.kulisa(s, rnd, (x, 0.0, z), rnd.uniform(1.3, 1.8), rnd.uniform(0, 90), "sylweta_2", "sylweta_1",
                               wys=rnd.uniform(32, 46))
    with s.grupa("Tlo/Wzgorza"), s.cechy(kolizja=False, cien=False):
        kolory = ["sylweta_2", "sylweta_3", "sylweta_2", "sylweta_1", "sylweta_3"]
        for i in range(22):
            a = math.radians(i * (360.0 / 22) + rnd.uniform(-4, 4))
            x, z = 640 * math.cos(a), 640 * math.sin(a)
            if z < -500 and -120 < x < 200:
                continue
            R, h = rnd.uniform(70, 95), rnd.uniform(45, 80)
            kol = kolory[i % len(kolory)]
            ry0 = -math.degrees(a) - 90.0 + rnd.uniform(-10, 10)
            with s.uklad(pos=(x, 0, z), obrot=(0, ry0, 0)):
                s.blok("Wzgórze", (0, (0.5 * h) / 2.0, 0), (1.9 * R, 0.5 * h, 1.2 * R), kol)
                with s.uklad(pos=(rnd.uniform(-0.1, 0.1) * R, 0.5 * h - 1.0, 0), obrot=(0, 12.0, rnd.choice((-4.0, 4.0)))):
                    s.blok("Wzgórze", (0, (0.3 * h + 1.0) / 2.0, 0), (1.25 * R, 0.3 * h + 1.0, 0.85 * R), cien(s, kol, 1.04))
                    with s.uklad(pos=(rnd.uniform(-0.12, 0.12) * R, 0.3 * h, 0.0), obrot=(0, -21.0, 0)):
                        s.blok("Wzgórze", (0, (0.2 * h + 1.0) / 2.0, 0), (0.65 * R, 0.2 * h + 1.0, 0.5 * R), "sylweta_3")
    with s.grupa("Tlo/Miasteczko"), s.cechy(kolizja=False, cien=False):
        # atrapa Krzywego Miasteczka na horyzoncie (w stronę prawdziwego miasta): mur, wieże, czerwony dach karczmy,
        # fioletowy kapelusz sklepu — widać ją z Ławki z Widokiem
        with s.uklad(pos=(40, 0, -720)):
            s.blok("Mur miasta", (0, 9, 0), (170, 18, 8), "kamien_cieply")
            for x in (-85, -30, 30, 85):
                s.blok("Wieża", (x, 15, 0), (12, 30, 12), "kamien_cieply", rot=(0, 0, 4 if x > 0 else -4))
                s.naroznik("Wieża dach", (x, 34, 0), (14, 8, 14), "dach_twierdza", rot=(0, 45, 0))
            s.blok("Karczma", (-10, 26, 18), (34, 18, 22), "tynk_krem", rot=(0, 8, 3))
            s.klin("Karczma dach", (-10, 41, 12), (38, 12, 12), "dach_karczma", rot=(0, 8, 3))
            s.klin("Karczma dach", (-10, 41, 24), (38, 12, 12), "dach_karczma", rot=(0, 188, -3))
            s.walec("Sklep", (40, 26, 22), 8, 24, "tynk_lawenda", os="y")
            s.naroznik("Sklep kapelusz", (42, 45, 22), (22, 18, 22), "dach_sklep", rot=(0, 30, 6))
            s.blok("Wieża twierdzy", (-55, 30, 30), (16, 50, 16), "kamien_cokol", rot=(0, 10, -3))
            s.blok("Chorągiew", (-55, 60, 30), (0.6, 10, 0.6), "drewno")
            s.blok("Chorągiew płat", (-51, 62, 30), (7, 4, 0.4), "dach_twierdza")
    with s.grupa("Chmury"):
        for i in range(12):
            a = math.radians(i * 30 + rnd.uniform(-10, 10))
            r = rnd.uniform(560, 700)
            zestaw.chmura(s, (r * math.cos(a), rnd.uniform(120, 170), r * math.sin(a)), rnd, rnd.uniform(1.8, 2.6))
