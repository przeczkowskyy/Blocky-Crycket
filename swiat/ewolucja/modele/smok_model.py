# -*- coding: utf-8 -*-
"""Smok ewolucji — JEDEN parametryczny model, osiem stadiów z danych (STADIA). Styl „Żarołuska”.

    from swiat.ewolucja.modele.smok_model import zbuduj_stadium, STADIA
    p = zbuduj_stadium(4)                      # Postac biblioteki (swiat/postacie/biblioteka/postac.py)

Styl: klockowa bryła w kolorze ciała, na grzbiecie od karku po ogon ciemne łuski-dachówki, w szczelinach między nimi
ŻAR (świeci, z wiekiem coraz szerzej), rogi / kolce / pazury jako kryształowe ostrza, błona skrzydeł w kontrastowym
kolorze. Wszystko, co ma być czytelne z kamery gry (z tyłu, z góry), leży na grzbiecie i w planie skrzydeł.

Konwencje biblioteki: 1 jednostka = 1 stud, Y w górę, smok patrzy w +Z, jego lewa strona to +X, ziemia y = 0.
Wszystkie stadia mają TEN SAM szkielet (KOSCI) — klipy i kod gry używają tych samych nazw stawów.
Wymiary w STADIA są w „jednostkach projektu”; Postac.skala przelicza je na studsy tak, żeby odległość nos–zad
wynosiła 2 × promień formy z gry (pole "r").

Regiony koloru (REGIONY; każda bryła ma region w p.regiony()): cialo, luski (ciemny akcent: łuski, stopy, hełm),
brzuch, blona, kolce (rogi, kolce, pazury, kryształy), zar, oko, stale (zęby, język, skorupka — nie przemalowywać).
Wariant albo linia żywiołu = inny słownik pięciu kolorów w paleta_stadium(nr, zmiany).

Style "zabawka" i "krysztal" zostają tylko do odtworzenia planszy porównawczej (generuj.py styl).
"""
import math

from swiat.postacie.biblioteka.postac import Postac, macierz_obrotu, razy_wektor

NOGI = ("NogaPL", "NogaPP", "NogaTL", "NogaTP")          # przednia lewa / prawa, tylna lewa / prawa
KOSCI = (["Tulow", "Szyja1", "Szyja2", "Glowa", "Szczeka", "SkrzydloL1", "SkrzydloL2", "SkrzydloP1", "SkrzydloP2",
          "Ogon1", "Ogon2", "Ogon3", "Ogon4"] + [n + s for n in NOGI for s in ("1", "2", "3")] + ["Powieki"])
ZACZEPY = ("PyskAttachment", "GlowaAttachment", "OgonKoniecAttachment", "SkrzydloLKoniecAttachment",
           "SkrzydloPKoniecAttachment", "BrzuchAttachment", "GrzbietAttachment",
           # miejsca na światło i cząsteczki żaru: gardło, pierś, trzy punkty wzdłuż grzbietu, ogon
           "GardloAttachment", "PiersAttachment", "Zar1Attachment", "Zar2Attachment", "Zar3Attachment",
           "ZarOgonAttachment")
REGIONY = ("cialo", "luski", "brzuch", "blona", "kolce", "zar", "oko", "stale", "zar_rdzen")
_REGION_KLUCZA = {"cialo": "cialo", "cialo_j": "cialo", "cialo_c": "luski", "brzuch": "brzuch", "brzuch_c": "brzuch",
                  "blona": "blona", "blona_c": "blona", "kolce": "kolce", "kolce_c": "kolce", "zar": "zar",
                  "zar_c": "zar", "zar_j": "zar_rdzen", "oko": "oko"}

# --------------------------------------------------------------------------- kolory
PALETY = {   # pięć regionów + oko; wariant albo linia żywiołu = inny słownik
    1: {"cialo": "FFC02E", "brzuch": "FFF3C4", "blona": "FF6A4A", "kolce": "FFFDF5", "zar": "FF4A2A", "oko": "2A1A12"},
    2: {"cialo": "22BFD8", "brzuch": "EAFBEA", "blona": "FFC738", "kolce": "FFFDF5", "zar": "FFE14D", "oko": "10303A"},
    3: {"cialo": "3A80EA", "brzuch": "D9EAFF", "blona": "FF6B57", "kolce": "F2F8FF", "zar": "9FF4FF", "oko": "FFD23F"},
    4: {"cialo": "E3412B", "brzuch": "FFC76B", "blona": "FFB02E", "kolce": "3A1C1C", "zar": "FFC21F", "oko": "FFE066"},
    5: {"cialo": "8448E0", "brzuch": "EAD9FF", "blona": "35DDB4", "kolce": "F6ECCB", "zar": "7CFFE0", "oko": "7CFFE0"},
    6: {"cialo": "4A5266", "brzuch": "A98A70", "blona": "C9362E", "kolce": "E9E1CC", "zar": "FF6A2A", "oko": "FF8A3D"},
    7: {"cialo": "EEE6D0", "brzuch": "FFF9EA", "blona": "3878E0", "kolce": "DCA536", "zar": "2FB4FF", "oko": "2FB4FF"},
    8: {"cialo": "2B2238", "brzuch": "4E3C66", "blona": "8A2BE2", "kolce": "7FF8FF", "zar": "FF4DD8", "oko": "FF4DD8"},
}
STALE = {"tusz": "1B1625", "bialy": "FFFDF4", "jezyk": "F06E86", "pysk": "4A1220", "skorupa": "FFF6E0",
         "skorupa_c": "E9DCC0", "rumieniec": "FF9AA8"}


def _rgb(h):
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def _mix(a, b, t):
    ra, rb = _rgb(a), _rgb(b)
    return "%02X%02X%02X" % tuple(int(round(ra[i] + (rb[i] - ra[i]) * t)) for i in range(3))


def paleta_stadium(nr, zmiany=None):
    """Pełna paleta modelu z pięciu regionów (zmiany: {"cialo": "RRGGBB", …} — wariant / linia żywiołu)."""
    b = dict(PALETY[nr])
    b.update(zmiany or {})
    p = dict(STALE)
    p.update(b)
    p["cialo_c"] = _mix(b["cialo"], "140A1E", 0.3 if nr <= 2 else 0.42)    # łuski maluchów łagodniejsze
    p["cialo_j"] = _mix(b["cialo"], "FFFFFF", 0.22)
    p["brzuch_c"] = _mix(b["brzuch"], b["cialo"], 0.30)
    p["blona_c"] = _mix(b["blona"], "140A1E", 0.32)
    p["kolce_c"] = _mix(b["kolce"], "140A1E", 0.25)
    p["zar_c"] = _mix(b["zar"], p["cialo_c"], 0.28)             # miękka zewnętrzna poświata żaru
    p["zar_j"] = _mix(b["zar"], "FFFFFF", 0.6)                  # jasny rdzeń żaru
    return p


# --------------------------------------------------------------------------- dane stadiów (jednostki projektu)
# T tułów (szer, wys, dł) · nog prześwit · lw grubość nogi · gl czaszka · pysk (szer, wys, dł) · zuch grubość żuchwy
# oczy (typ, wielkość) · szyja (dł1, dł2, kąt1, kąt2, grubość) · ogon (4 długości, grubość, 4 kąty wzniosu, koniec)
# skrz (ramię, dłoń, cięciwa) · skrz_spocz (pochylenie, odchylenie w tył, wznios, złożenie dłoni)
# kolce (ile, wysokość, typ) · plyty łuski grzbietu · zar 0…1 · rogi typ · dodatki · waga 0 (pisklę) … 1 (prastary)
STADIA = [
    {"nr": 1, "id": "smok_1", "nazwa": "HATCHLING", "r": 1.6, "waga": 0.0,
     "T": (1.5, 1.25, 1.55), "nog": 0.42, "lw": 0.5, "gl": (1.75, 1.45, 1.5), "pysk": (0.74, 0.62, 0.64), "zuch": 0.3,
     "oczy": ("dziecko", 1.0), "szyja": (0.22, 0.2, 62, 40, 0.8),
     "ogon": ((0.5, 0.45, 0.4, 0.34), 0.72, (-18, -4, 14, 30), "grot_maly"),
     "skrz": (0.62, 0.86, 0.86), "skrz_spocz": (-10, 16, 46, 34),
     "kolce": (3, 0.26, "kolce"), "plyty": 2, "zar": 0.15, "rogi": "guzki", "dodatki": ("skorupka", "rumieniec")},
    {"nr": 2, "id": "smok_2", "nazwa": "WHELP", "r": 2.2, "waga": 0.12,
     "T": (1.5, 1.2, 1.95), "nog": 0.6, "lw": 0.5, "gl": (1.5, 1.25, 1.4), "pysk": (0.74, 0.6, 0.84), "zuch": 0.3,
     "oczy": ("dziecko", 0.86), "szyja": (0.36, 0.3, 58, 36, 0.78),
     "ogon": ((0.7, 0.62, 0.52, 0.45), 0.72, (-16, -4, 10, 24), "grot"),
     "skrz": (0.9, 1.25, 1.15), "skrz_spocz": (-12, 18, 40, 36),
     "kolce": (3, 0.32, "kolce"), "plyty": 3, "zar": 0.25, "rogi": "male", "dodatki": ("rumieniec",)},
    {"nr": 3, "id": "smok_3", "nazwa": "DRAKE", "r": 3.0, "waga": 0.3,
     "T": (1.35, 1.15, 2.35), "nog": 0.98, "lw": 0.46, "gl": (1.2, 1.0, 1.25), "pysk": (0.8, 0.5, 1.0), "zuch": 0.38,
     "oczy": ("mlody", 0.7), "szyja": (0.7, 0.6, 54, 30, 0.7),
     "ogon": ((0.95, 0.88, 0.78, 0.66), 0.7, (-14, -4, 6, 16), "grot"),
     "skrz": (0.95, 2.5, 1.2), "skrz_spocz": (-14, 36, 30, 44),
     "kolce": (4, 0.4, "kolce"), "plyty": 3, "zar": 0.4, "rogi": "wstecz", "dodatki": ("kolnierz",)},
    {"nr": 4, "id": "smok_4", "nazwa": "FIRE DRAKE", "r": 4.0, "waga": 0.42,
     "T": (1.6, 1.32, 2.45), "nog": 1.0, "lw": 0.56, "gl": (1.3, 1.06, 1.32), "pysk": (0.9, 0.56, 1.1), "zuch": 0.4,
     "oczy": ("dorosly", 0.6), "szyja": (0.8, 0.7, 56, 30, 0.8),
     "ogon": ((1.05, 0.95, 0.85, 0.72), 0.8, (-12, -2, 8, 20), "plomien"),
     "skrz": (1.7, 2.35, 1.9), "skrz_spocz": (-16, 24, 36, 38),
     "kolce": (5, 0.78, "plomienie"), "plyty": 4, "zar": 0.65, "rogi": "wgore", "dodatki": ("ogniste_skrzydla",)},
    {"nr": 5, "id": "smok_5", "nazwa": "DRAGON", "r": 5.2, "waga": 0.55,
     "T": (1.75, 1.45, 2.75), "nog": 1.12, "lw": 0.62, "gl": (1.42, 1.12, 1.45), "pysk": (1.0, 0.62, 1.38), "zuch": 0.46,
     "oczy": ("dorosly", 0.62), "szyja": (1.0, 0.9, 54, 28, 0.9),
     "ogon": ((1.25, 1.12, 1.0, 0.86), 0.86, (-12, -3, 6, 14), "dwa_ostrza"),
     "skrz": (2.5, 3.7, 2.9), "skrz_spocz": (-16, 12, 30, 28),
     "kolce": (5, 0.6, "kolce"), "plyty": 4, "zar": 0.6, "rogi": "klasyczne", "dodatki": ("szpony",)},
    {"nr": 6, "id": "smok_6", "nazwa": "WAR DRAGON", "r": 6.8, "waga": 0.72,
     "T": (2.8, 1.9, 2.9), "nog": 1.0, "lw": 0.95, "gl": (1.78, 1.3, 1.5), "pysk": (1.32, 0.86, 1.28), "zuch": 0.62,
     "oczy": ("dorosly", 0.6), "szyja": (0.8, 0.7, 42, 20, 1.34),
     "ogon": ((1.2, 1.05, 0.9, 0.7), 1.15, (-10, -2, 4, 10), "maczuga"),
     "skrz": (2.3, 3.0, 2.7), "skrz_spocz": (-16, 24, 32, 38),
     "kolce": (4, 0.7, "kolce"), "plyty": 4, "zar": 0.7, "rogi": "byk", "dodatki": ("naramienniki", "kly")},
    {"nr": 7, "id": "smok_7", "nazwa": "ELDER DRAGON", "r": 9.0, "waga": 0.85,
     "T": (1.75, 1.5, 3.05), "nog": 1.42, "lw": 0.62, "gl": (1.36, 1.06, 1.45), "pysk": (0.9, 0.56, 1.62), "zuch": 0.42,
     "oczy": ("dorosly", 0.6), "szyja": (1.6, 1.4, 64, 36, 0.78),
     "ogon": ((1.55, 1.45, 1.25, 1.05), 0.8, (-12, -4, 4, 12), "wachlarz"),
     "skrz": (2.9, 4.1, 3.0), "skrz_spocz": (-16, 24, 36, 40),
     "kolce": (5, 0.62, "kolce"), "plyty": 5, "zar": 0.8, "rogi": "korona", "dodatki": ("pletwy_szyi", "wasy", "broda")},
    {"nr": 8, "id": "smok_8", "nazwa": "ANCIENT DRAGON", "r": 15.0, "waga": 1.0,
     "T": (3.1, 2.25, 3.5), "nog": 1.9, "lw": 1.1, "gl": (2.1, 1.5, 1.8), "pysk": (1.5, 0.95, 1.78), "zuch": 0.62,
     "oczy": ("dorosly", 0.74), "szyja": (1.5, 1.3, 54, 28, 1.5),
     "ogon": ((1.7, 1.5, 1.3, 1.1), 1.4, (-10, -2, 6, 14), "krysztaly"),
     "skrz": (3.7, 5.1, 4.0), "skrz_spocz": (-16, 24, 36, 40),
     "kolce": (5, 1.7, "krysztaly"), "plyty": 4, "zar": 1.0, "rogi": "prastare",
     "dodatki": ("naramienniki", "broda", "kly")},
]


def stadium(nr):
    return STADIA[int(nr) - 1]


class Smok(Postac):
    """Postac, która pamięta region koloru każdej bryły (klucz palety użyty przy jej dodaniu)."""

    def _dodaj(self, ksztalt, nazwa, pos, size, kolor, mat, rot, faza, **dodatki):
        c = super()._dodaj(ksztalt, nazwa, pos, size, kolor, mat, rot, faza, **dodatki)
        c["reg"] = _REGION_KLUCZA.get(kolor, "stale")
        return c

    def regiony(self):
        """Region każdej bryły, w kolejności p.json()["czesci"]."""
        return [c.get("reg", "stale") for c in self.czesci]


def _lus(rot, zn):
    """Odbicie obrotu względem płaszczyzny YZ: (rx, ry, rz) -> (rx, zn·ry, zn·rz)."""
    return (rot[0], zn * rot[1], zn * rot[2])


def _plus(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def geometria(P):
    """Stawy szkieletu i wymiary pomocnicze stadium (jednostki projektu, przed skalą)."""
    W, H, L = P["T"]
    nog = P["nog"]
    yb = nog + H / 2
    G = {"yb": yb, "Tulow": (0.0, yb, 0.0)}
    l1, l2, a1, a2, gr = P["szyja"]
    s1 = (0.0, yb + H * 0.18, L / 2 - 0.12 * L)
    d1 = (0.0, math.sin(math.radians(a1)), math.cos(math.radians(a1)))
    d2 = (0.0, math.sin(math.radians(a2)), math.cos(math.radians(a2)))
    s2 = _plus(s1, tuple(v * l1 for v in d1))
    gs = _plus(s2, tuple(v * l2 for v in d2))
    G.update(Szyja1=s1, Szyja2=s2, Glowa=gs)
    gw, gh, gd = P["gl"]
    G["cz"] = (0.0, gh * 0.30, gd * 0.22)                       # środek czaszki względem stawu głowy
    zf = G["cz"][2] + gd / 2
    G["zf"] = zf
    ph = P["pysk"][1]                                           # środek pyska: u maluchów na środku twarzy (pysk, nie dziób)
    G["ys"] = (G["cz"][1] - gh * 0.17) if P["oczy"][0] == "dziecko" else (G["cz"][1] - gh / 2 + ph / 2 + 0.02 * gh)
    G["Szczeka"] = _plus(gs, (0.0, G["ys"] - ph / 2 + 0.06, zf - 0.18 * gd))
    lens, gro, katy, _ = P["ogon"]
    pt = (0.0, yb + H * 0.08, -L / 2 + 0.1)
    for i in range(4):                                           # ogon: łańcuch w tył (−Z), wznios z kątów
        G["Ogon%d" % (i + 1)] = pt
        b = math.radians(katy[i])
        pt = _plus(pt, (0.0, lens[i] * math.sin(b), -lens[i] * math.cos(b)))
    G["OgonKoniec"] = pt
    L1, L2, C = P["skrz"]
    pit, swp, dih, fold = P["skrz_spocz"]
    for strona, zn in (("L", 1.0), ("P", -1.0)):
        j1 = (zn * W * 0.36, yb + H / 2 - 0.02, L * 0.22)
        R1 = macierz_obrotu(*_lus((pit, swp, dih), zn))
        j2 = _plus(j1, razy_wektor(R1, (zn * L1, 0.0, 0.0)))
        G["Skrzydlo%s1" % strona], G["Skrzydlo%s2" % strona] = j1, j2
    G["rot1"], G["rot2"] = (pit, swp, dih), (pit * 0.8, swp + fold, dih * 0.8)
    lw = P["lw"]
    ya = 0.2 + 0.05 * lw                                        # wysokość kostki (staw stopy)
    G["ya"] = ya
    for n, zn, z, dx in (("NogaPL", 1, L * 0.32, 0.12), ("NogaPP", -1, L * 0.32, 0.12),
                         ("NogaTL", 1, -L * 0.3, 0.02), ("NogaTP", -1, -L * 0.3, 0.02)):
        x = zn * (W / 2 - lw * dx)
        bio = (x, nog + H * 0.3, z)
        D = bio[1] - ya
        if n.startswith("NogaP"):                               # przednia: łokieć w tył, nadgarstek pod barkiem
            kolano, kostka = (x, bio[1] - 0.52 * D, z - 0.26 * D), (x, ya, z + 0.05 * D)
        else:                                                   # tylna: kolano w przód, pęcina w tył
            kolano, kostka = (x, bio[1] - 0.46 * D, z + 0.32 * D), (x, ya, z - 0.1 * D)
        G[n + "1"], G[n + "2"], G[n + "3"] = bio, kolano, kostka
    return G


def dlugosc_nos_zad(P, G=None):
    G = G or geometria(P)
    return G["Glowa"][2] + G["zf"] + P["pysk"][2] + P["T"][2] / 2


def skala_stadium(P):
    return round(2.0 * P["r"] / dlugosc_nos_zad(P), 4)


# --------------------------------------------------------------------------- budowa
def _szkielet(p, P, G):
    """Ten sam szkielet w każdym stadium i w wersji uproszczonej (kolejność = KOSCI)."""
    W, H, L = P["T"]
    gw, gh, gd = P["gl"]
    pw, ph, pl = P["pysk"]
    lw, ya = P["lw"], G["ya"]
    l1, l2, a1, a2, gr = P["szyja"]
    p.kosc("Tulow", "Root", G["Tulow"], czesc=(W, H, L))
    p.kosc("Szyja1", "Tulow", G["Szyja1"], czesc=(gr, gr, max(0.2, l1)), dl=0.3)
    p.kosc("Szyja2", "Szyja1", G["Szyja2"], czesc=(gr * 0.9, gr * 0.9, max(0.2, l2)), dl=0.3)
    p.kosc("Glowa", "Szyja2", G["Glowa"], czesc=(gw, gh, gd), srodek=G["cz"])
    p.kosc("Szczeka", "Glowa", G["Szczeka"], czesc=(pw * 0.9, 0.2, pl + 0.3), srodek=(0, -0.08, pl / 2), dl=0.25)
    for s in ("L", "P"):
        p.kosc("Skrzydlo%s1" % s, "Tulow", G["Skrzydlo%s1" % s], czesc=(0.3, 0.3, 0.3), dl=0.3)
        p.kosc("Skrzydlo%s2" % s, "Skrzydlo%s1" % s, G["Skrzydlo%s2" % s], czesc=(0.3, 0.3, 0.3), dl=0.3)
    lens, gro = P["ogon"][0], P["ogon"][1]
    for i in range(4):
        p.kosc("Ogon%d" % (i + 1), "Ogon%d" % i if i else "Tulow", G["Ogon%d" % (i + 1)],
               czesc=(gro * (1 - 0.18 * i), gro * (1 - 0.18 * i), lens[i]), dl=0.25)
    for n in NOGI:
        p.kosc(n + "1", "Tulow", G[n + "1"], czesc=(lw, 0.4, lw), srodek=(0, -0.2, 0), dl=0.25)
        p.kosc(n + "2", n + "1", G[n + "2"], czesc=(lw * 0.8, 0.4, lw * 0.8), srodek=(0, -0.2, 0), dl=0.25)
        p.kosc(n + "3", n + "2", G[n + "3"], czesc=(lw, ya, lw * 1.4), srodek=(0, -ya / 2, lw * 0.2), dl=0.2)
    p.kosc("Powieki", "Glowa", _plus(G["Glowa"], _powieki_staw(P, G)), czesc=(gw, 0.2, 0.2), dl=0.2)


def _powieki_staw(P, G):
    return (0.0, G["cz"][1] + P["gl"][1] * 0.3, G["zf"] - 0.2)


def _wzdluz(p, nazwa, a, b, gr1, gr2, kolor="cialo", nadl=0.0, faza=None, mat="zwykly"):
    """Klocek wzdłuż odcinka a → b w płaszczyźnie YZ (układ stawu a): noga jako kość, nie słupek."""
    dy, dz = b[1] - a[1], b[2] - a[2]
    dl_ = math.hypot(dy, dz)
    with p.uklad(obrot=(-math.degrees(math.atan2(dz, -dy)), 0, 0)):
        p.blok(nazwa, (0, -dl_ / 2, 0), (gr1, dl_ + nadl, gr2), kolor, mat, faza=faza)


def zbuduj_stadium(nr, styl="zar", zmiany_kolorow=None, id=None, skala=None, nadpisz=None):
    P = dict(stadium(nr), **(nadpisz or {}))                    # nadpisz: zmiany danych stadium dla wariantu modelu
    G = geometria(P)
    pal = paleta_stadium(P["nr"], zmiany_kolorow)
    fz = {"zar": 0.06, "zabawka": 0.15, "krysztal": 0.0}[styl]
    p = Smok(id or P["id"], P["nazwa"].title(), typ="stwor", skala=skala or skala_stadium(P), faza=fz, paleta=pal)
    p.dane_stadium, p.geometria, p.styl = P, G, styl
    W, H, L = P["T"]
    nog, lw, yb, ya, N = P["nog"], P["lw"], G["yb"], G["ya"], P["nr"]
    ZAR = styl == "zar"
    g = P["zar"] if styl != "zabawka" else 0.0
    gw, gh, gd = P["gl"]
    pw, ph, pl = P["pysk"]
    KR = styl == "krysztal"
    MC = "polysk" if KR else "zwykly"                           # materiał ciała
    MK = "polysk"                                               # materiał kolców / kryształów
    dod = P["dodatki"]
    nk, hk, typ_k = P["kolce"]
    swiec_k = "swiecacy" if typ_k in ("plomienie", "krysztaly") else MK
    kol_k = "zar" if typ_k == "plomienie" else "kolce"

    _szkielet(p, P, G)
    l1, l2, a1, a2, gr = P["szyja"]
    L1, L2, C = P["skrz"]
    lens, gro, katy, koniec = P["ogon"]

    def cialo(nazwa, pos, size, kolor="cialo", os_="z", faza=None, mat=None, t=0.5):
        """Bryła ciała: klocek; w stylu „krysztal” — dwie ścięte piramidy podstawami do siebie (fasety)."""
        if not KR:
            return p.blok(nazwa, pos, size, kolor, mat or MC, faza=faza)
        sx, sy, sz = size
        if os_ == "z":
            for zn, rx in ((1, 90), (-1, -90)):
                p.ostroslup(nazwa, (pos[0], pos[1], pos[2] + zn * sz / 4), (sx, sz / 2, sy), kolor, MC,
                            rot=(rx, 0, 0), gora=(sx * t, sy * t), faza=0)
        else:
            for zn, rx in ((1, 0), (-1, 180)):
                p.ostroslup(nazwa, (pos[0], pos[1] + zn * sy / 4, pos[2]), (sx, sy / 2, sz), kolor, MC,
                            rot=(rx, 0, 0), gora=(sx * t, sz * t), faza=0)

    def kolec(nazwa, pos, size, kolor="kolce", mat=MK, rot=(0, 180, 0)):
        """Kolec-ostrze: klin (1 część Roblox), pionowa krawędź z tyłu, skos opada do przodu."""
        if styl == "zabawka":
            return p.ostroslup(nazwa, pos, size, kolor, "zwykly", gora=(0, 0), przes_gory=(0, -size[2] * 0.3))
        return p.klin(nazwa, pos, size, kolor, mat, rot=rot, faza=0.0 if KR else 0.02)

    def luska(nazwa, dl_, szer, y, z, gr_=0.2):
        """Łuska-dachówka: tylna krawędź uniesiona, okap szerszy niż ciało."""
        with p.uklad(pos=(0, y + gr_ * 0.5 + 0.03, z), obrot=(10, 0, 0)):
            p.blok(nazwa, (0, 0, 0), (szer, gr_, dl_), "cialo_c", "matowy", faza=0.05)

    # ---------------------------------------------------------------- tułów
    with p.na("Tulow"):
        cialo("Tulow", (0, 0, 0), (W, H, L), faza=0.26 if N <= 2 and ZAR else fz * 2.2)
        p.blok("Brzuch", (0, -H / 2 - 0.02, 0.0), (W * 0.74, 0.14, L * 0.88), "brzuch", "matowy", faza=0.03)
        p.blok("Piers", (0, -H * 0.1, L / 2 + 0.02), (W * 0.74, H * 0.72, 0.14), "brzuch", "matowy", faza=0.03)
        if styl == "zabawka":
            for y in (0.16, -0.08):
                p.blok("Pas piersi", (0, y * H - H * 0.1, L / 2 + 0.1), (W * 0.62, 0.05, 0.03), "brzuch_c", "matowy", faza=0)
        if g > 0.3:                                              # serce-żar na piersi
            sw = W * (0.16 + 0.26 * g)
            p.blok("Serce", (0, -H * 0.06, L / 2 + 0.1), (sw, sw * 0.9, 0.06), "zar", "swiecacy", faza=0.0,
                   rot=(0, 0, 45))
        if KR:                                                   # rdzeń: świecący pas w talii między fasetami
            p.blok("Rdzen", (0, 0, 0), (W * 1.03, H * 1.03, 0.1 + 0.3 * g), "zar", "swiecacy", faza=0)
        if ZAR:
            n = P["plyty"]
            p.blok("Zar grzbietu", (0, H / 2 + 0.03, 0.0), (W * (0.8 + 0.2 * g), 0.12, L * 0.97), "zar_c", "swiecacy",
                   faza=0.0)
            p.blok("Zar rdzen", (0, H / 2 + 0.05, 0.0), (W * (0.2 + 0.16 * g), 0.12, L * 0.99), "zar_j", "swiecacy",
                   faza=0.0)
            for i in range(n):                                   # szczelina rośnie z żarem
                luska("Luska grzbietu", L / n * (0.86 - 0.22 * g), W * (1.16 - 0.03 * i), H / 2,
                      L / 2 - (i + 0.5) * L / n, 0.22)
        ygr = H / 2 + (0.24 if ZAR else 0.0)
        gk = max(0.2, W * 0.17)                                  # grubość ostrza: ma być widać z góry
        for i in range(nk):
            f = (i + 0.5) / nk
            z = L / 2 - 0.08 * L - f * L * 0.86
            fala = 1.0 - 0.5 * abs(f - 0.3)                      # najwyższe nad barkami
            if typ_k == "plomienie":
                wys = hk * (1.0 if i % 2 == 0 else 0.66) * fala
                kolec("Plomien", (0, ygr + wys / 2 - 0.05, z), (gk * (1.0 if i % 2 == 0 else 0.7), wys, wys * 0.72),
                      "zar" if i % 2 == 0 else "kolce", "swiecacy" if i % 2 == 0 else MK)
            elif typ_k == "krysztaly":
                wys = hk * fala * (1.0 if i % 2 == 0 else 0.72)
                zn = 1 if i % 2 == 0 else -1                     # na przemian rozchylone w lewo i w prawo
                with p.uklad(pos=(zn * W * 0.12, ygr - 0.08, z), obrot=(-6, 0, -zn * 18)):
                    kolec("Krysztal grzbietu", (0, wys / 2, 0), (gk, wys, wys * 0.62),
                          "kolce", "swiecacy" if i % 2 == 0 else MK)
            else:
                wys = hk * fala
                kolec("Kolec grzbietu", (0, ygr + wys / 2 - 0.05, z), (gk, wys, wys * 0.95))
        if "naramienniki" in dod and ZAR:
            for zn in (1, -1):
                with p.uklad(pos=(zn * (W / 2 + 0.04), H * 0.3, L * 0.3), obrot=(0, 0, -zn * 28)):
                    p.blok("Naramiennik", (0, 0, 0), (0.26, H * 0.66, L * 0.42), "cialo_c", "matowy", faza=0.06)
                    kolec("Kolec naramiennika", (zn * 0.04, H * 0.5, -0.02), (0.24, H * 0.52, L * 0.26),
                          "kolce", "swiecacy" if N == 8 else MK)
        p.zaczep("BrzuchAttachment", "Tulow", (0, -H / 2 - 0.1, 0))
        p.zaczep("GrzbietAttachment", "Tulow", (0, H / 2 + 0.3, 0))
        p.zaczep("PiersAttachment", "Tulow", (0, -H * 0.06, L / 2 + 0.25))
        for i, z in enumerate((L * 0.3, 0.0, -L * 0.3)):
            p.zaczep("Zar%dAttachment" % (i + 1), "Tulow", (0, H / 2 + 0.2, z))

    # ---------------------------------------------------------------- szyja (dwa segmenty)
    for i, (nazwa, dl_, kat) in enumerate((("Szyja1", l1, a1), ("Szyja2", l2, a2))):
        gs = gr * (1.0 - 0.1 * i)
        with p.na(nazwa, obrot=(-kat, 0, 0)):                   # +Z biegnie wzdłuż szyi
            cialo(nazwa, (0, 0, dl_ / 2), (gs, gs, dl_ + gs * 0.55), faza=fz * 1.4)
            if i == 1:
                p.zaczep("GardloAttachment", "Szyja2",
                         razy_wektor(macierz_obrotu(-kat, 0, 0), (0, -gs / 2 - 0.1, dl_ * 0.6)))
            if "pletwy_szyi" in dod and styl != "zabawka":      # ELDER: pary poziomych płetw wzdłuż długiej szyi
                for zn in (1, -1):
                    p.klin("Pletwa szyi", (zn * gs * 1.2, gs * 0.12, dl_ * 0.5), (0.08, gs * 1.4, dl_ * 0.9), "blona",
                           "matowy", rot=(0, 180, zn * 90), faza=0.0)
            if ZAR and dl_ > 0.3:
                luska("Luska szyi", dl_ * 0.7, gs * 1.18, gs / 2, dl_ * 0.5, 0.16)
                if g >= 0.5 and dl_ > 0.5:
                    p.blok("Zar szyi", (0, gs / 2 + 0.02, dl_ * 0.5), (gs * 0.86, 0.1, dl_ * 1.02), "zar_c", "swiecacy",
                           faza=0.0)
            if False:
                p.blok("Szyja spod", (0, -gs / 2 - 0.02, dl_ / 2), (gs * 0.66, 0.08, dl_ * 0.96), "brzuch", "matowy",
                       faza=0.0)
            if dl_ > 0.5 and nk and styl != "zabawka" and N == 4:
                h_ = hk * 0.6
                kolec("Kolec szyi", (0, gs / 2 + 0.16 + h_ / 2 - 0.05, dl_ * 0.45), (max(0.16, gs * 0.2), h_, h_ * 0.9),
                      kol_k, swiec_k)

    # ---------------------------------------------------------------- głowa
    cz, zf = G["cz"], G["zf"]
    top, tyl = cz[1] + gh / 2, cz[2] - gd / 2
    typ_oczu, eo = P["oczy"]
    with p.na("Glowa"):
        cialo("Czaszka", cz, (gw, gh, gd), faza=0.3 if N <= 2 and ZAR else fz * 2.0, t=0.62)
        ys = G["ys"]
        p.blok("Pysk", (0, ys, zf + pl / 2 - 0.06), (pw, ph, pl + 0.12), "cialo", MC, faza=0.16 if N <= 2 else fz * 1.5)
        if True:  # skos czoła do nosa (także u maluchów)
            p.klin("Grzbiet nosa", (0, ys + ph / 2 + ph * 0.2 - 0.01, zf + pl * 0.42), (pw * 0.62, ph * 0.4, pl * 0.84),
                   "cialo_j", MC, rot=(0, 180, 0), faza=0.02)
        for zn in ((1, -1) if N <= 3 else ()):
            p.blok("Nozdrze", (zn * pw * 0.22, ys + ph / 2 + 0.005, zf + pl - 0.1), (pw * 0.14, 0.03, pw * 0.14),
                   "tusz", "matowy", faza=0.0)
        p.blok("Paszcza", (0, ys - ph / 2 + 0.0, zf + pl / 2 - 0.1), (pw * 0.86, 0.05, pl * 0.9),
               "zar" if g >= 0.95 else "pysk", "swiecacy" if g >= 0.95 else "matowy", faza=0.0)
        if typ_oczu == "dziecko":
            # oko w narożniku czaszki: białko wystaje z przodu, z boku i z GÓRY, źrenica zawija się z przodu na górę
            e = 0.66 * eo
            xo, yo, zo = gw / 2 - e * 0.42, top - e * 0.38, zf - e * 0.3
            for zn in (1, -1):
                p.blok("Bialko", (zn * xo, yo, zo), (e, e, e * 0.9), "bialy", "polysk", faza=0.05)
                p.blok("Zrenica", (zn * (xo - e * 0.08), yo + e * 0.14, zo + e * 0.16), (e * 0.5, e * 0.78, e * 0.64),
                       "oko", "polysk", faza=0.03)
                p.blok("Zrenica bok", (zn * (xo + e * 0.5), yo, zo + 0.02), (0.05, e * 0.5, e * 0.46), "oko", "polysk",
                       faza=0.0)
                p.blok("Blysk", (zn * (xo - e * 0.08) + e * 0.1, yo + e * 0.3, zo + e * 0.49), (e * 0.18, e * 0.18, 0.04),
                       "bialy", faza=0.0)
                if "lagodne_brwi" in dod:                       # wariant łagodny: krótka jasna brew uniesiona na zewnątrz
                    p.blok("Brew", (zn * (xo - e * 0.06), yo + e * 0.6, zo + e * 0.4), (e * 0.4, 0.06, 0.1), "cialo_j", MC,
                           rot=(0, 0, zn * 12), faza=0.02)
                else:
                    p.blok("Brew", (zn * (xo - e * 0.14), yo + e * 0.56, zo + e * 0.38), (e * 0.5, 0.07, 0.12), "cialo_c", MC,
                           rot=(0, 0, -zn * 18), faza=0.02)
                if "rumieniec" in dod:
                    p.blok("Rumieniec", (zn * gw * 0.34, G["ys"] - 0.02, zf + 0.02), (e * 0.34, e * 0.2, 0.04),
                           "rumieniec", "matowy", faza=0.0)
        elif typ_oczu == "mlody":
            ye, e = cz[1] + gh * 0.08, 0.62 * eo
            for zn in (1, -1):
                with p.uklad(pos=(zn * gw * 0.34, ye, zf - 0.02), obrot=(0, zn * 28, 0)):
                    p.blok("Bialko", (0, 0, 0.05), (e * 0.8, e * 0.8, 0.06), "bialy", "polysk", faza=0.03)
                    p.blok("Zrenica", (-zn * 0.02, -0.01, 0.085), (e * 0.36, e * 0.62, 0.04), "tusz", "polysk", faza=0.0)
                    p.blok("Brew", (0, e * 0.5, 0.08), (e * 1.0, e * 0.22, 0.16), "cialo_c", MC, rot=(0, 0, -zn * 12),
                           faza=0.02)
        else:
            ye, e = cz[1] + gh * 0.12, 0.62 * eo
            for zn in (1, -1):
                with p.uklad(pos=(zn * (gw / 2 + 0.01), ye, cz[2] + gd * 0.2), obrot=(0, zn * 90, 0)):
                    p.blok("Oko", (0, 0, 0.0), (e * 1.05, e * 0.42, 0.06), "oko", "swiecacy", rot=(0, 0, zn * 14),
                           faza=0.0)
            # hełm: łuska na czaszce z okapem nad oczami (groźne spojrzenie, czytelna z góry)
            with p.uklad(pos=(0, top + 0.06, cz[2] + gd * 0.06), obrot=(9, 0, 0)):
                p.blok("Helm", (0, 0, 0), (gw * 1.12, 0.2, gd * 0.86), "cialo_c", "matowy" if ZAR else MC, faza=0.05)
        for zn in (1, -1):                                       # kły górne
            if typ_oczu == "dziecko":
                if True:
                    p.klin("Zabek", (zn * pw * 0.3, ys - ph / 2 - 0.05, zf + pl - 0.05), (0.1, 0.12, 0.08), "bialy",
                           "polysk", rot=(180, 0, 0), faza=0.0)
            elif "kly" not in dod:
                p.klin("Kiel", (zn * pw * 0.38, ys - ph / 2 - ph * 0.22, zf + pl - 0.1 - ph * 0.1),
                       (0.12, ph * 0.5, ph * 0.36), "bialy", "polysk", rot=(180, 0, 0), faza=0.0)
        _rogi(p, P, styl, cz, top, tyl, zf)
        if "skorupka" in dod:
            with p.uklad(pos=(-gw * 0.12, top + 0.06, cz[2] - gd * 0.12), obrot=(-8, 20, 9)):
                p.blok("Skorupka", (0, 0, 0), (gw * 0.5, 0.16, gd * 0.5), "skorupa", "matowy", faza=0.04)
                p.klin("Skorupka zab", (0.1 * gw, 0.17, 0.12 * gd), (gw * 0.2, 0.2, gd * 0.2), "skorupa", "matowy",
                       faza=0.0)
        if "kolnierz" in dod and styl != "zabawka":             # DRAKE: płaski kołnierz za głową, czytelny z góry
            for zn in (1, -1):
                with p.uklad(pos=(zn * gw * 0.34, cz[1] + gh * 0.16, tyl + 0.12), obrot=(-14, zn * 24, zn * 10)):
                    p.klin("Kolnierz", (zn * gw * 0.62, 0, -gd * 0.62), (0.1, gw * 1.24, gd * 1.5), "blona", "matowy",
                           rot=(0, 180, zn * 90), faza=0.0)
                    p.klin("Kolec kolnierza", (zn * gw * 1.2, 0.04, -gd * 1.0), (0.14, gw * 0.36, gd * 0.9), "kolce", MK,
                           rot=(0, 180, zn * 90), faza=0.0)
        if "wasy" in dod and styl != "zabawka":                 # ELDER: dwa długie wąsy od pyska w tył
            for zn in (1, -1):
                p.blok("Was", (zn * (pw / 2 + pl * 0.36), ys - ph * 0.1, zf + pl * 0.42), (0.1, 0.1, pl * 1.5), "kolce", MK,
                       rot=(8, zn * 148, 0), faza=0.02)
        p.zaczep("PyskAttachment", "Glowa", (0, ys - ph * 0.2, zf + pl + 0.1))
        p.zaczep("GlowaAttachment", "Glowa", (0, top + 0.3, cz[2]))

    # ---------------------------------------------------------------- powieki (maluchy mrugają: staw „Powieki”)
    if typ_oczu == "dziecko":
        # płytki w kolorze ciała schowane w głowie; przesunięcie stawu o (0, 0.2, 0.2) zakrywa przód i górę oczu
        e = 0.66 * eo
        xo, yo, zo = gw / 2 - e * 0.42, top - e * 0.38, zf - e * 0.3
        sx, sy, sz = _powieki_staw(P, G)
        with p.na("Powieki"):
            for zn in (1, -1):
                p.blok("Powieka przod", (zn * (xo - e * 0.05), yo - 0.2 - sy, zo + e * 0.45 - 0.14 - sz),
                       (e * 0.9, e * 1.02, 0.05), "cialo", MC, faza=0.0)
                p.blok("Powieka gora", (zn * (xo - e * 0.05), yo + e * 0.5 - 0.14 - sy, zo - 0.2 - sz),
                       (e * 0.9, 0.05, e * 0.92), "cialo", MC, faza=0.0)

    # ---------------------------------------------------------------- żuchwa
    with p.na("Szczeka"):
        zl = zf + pl - (zf - 0.18 * gd)                          # długość żuchwy od zawiasu do końca pyska
        zh = ph * P["zuch"]
        yz = -0.05 - zh * 0.3
        p.blok("Zuchwa", (0, yz, zl / 2 - 0.02), (pw * 0.9, zh, zl), "cialo", MC, faza=fz)
        if N <= 3:
            p.blok("Jezyk", (0, yz + zh / 2 + 0.01, zl * 0.5), (pw * 0.5, 0.04, zl * 0.74), "jezyk", "matowy", faza=0.0)
        if typ_oczu != "dziecko" and "kly" not in dod:
            p.blok("Zeby dolne", (0, yz + zh / 2 + 0.03, zl - 0.14), (pw * 0.82, 0.12, 0.12), "bialy", "polysk",
                   faza=0.0)
        if "kly" in dod:                                         # kły dolne wystające ku górze (ciężka szczęka)
            for zn in (1, -1):
                p.klin("Kiel dolny", (zn * pw * 0.5, yz + zh / 2 + ph * 0.3, zl - 0.3 - ph * 0.2),
                       (0.16, ph * 0.72, ph * 0.44), "bialy", "polysk", rot=(0, 180, 0), faza=0.0)
        if "broda" in dod and styl != "zabawka":
            p.klin("Broda", (0, yz - zh / 2 - ph * 0.42, zl * 0.5), (0.18, ph * 0.9, ph * 0.9), "kolce", MK,
                   rot=(180, 180, 0), faza=0.0)

    # ---------------------------------------------------------------- skrzydła (palce + pola błony, lekko załamane)
    t = 0.07
    MB = "poswiata" if KR else "matowy"
    npal = 2 if N <= 2 else (4 if "szpony" in dod else 3)
    katy_p = (0.0, 34.0, 70.0) if npal == 2 else ((0.0, 26.0, 52.0, 78.0, 100.0) if npal == 4 else (0.0, 30.0, 60.0, 88.0))
    dl_p = (L2, L2 * 0.9, L2 * 0.76, L2 * 0.6)
    zebro, mzeb = ("zar", "swiecacy") if g >= 0.95 else ("cialo_c", MC)
    ogn = "ogniste_skrzydla" in dod and ZAR
    for strona, zn in (("L", 1.0), ("P", -1.0)):
        with p.na("Skrzydlo%s1" % strona, obrot=_lus(G["rot1"], zn)):
            p.blok("Ramie", (zn * L1 / 2, 0.02, 0), (L1 + 0.16, 0.24, 0.24), "cialo", MC, faza=0.04)
            p.blok("Blona ramienia", (zn * L1 / 2, -0.03, -C * 0.47), (L1, t, C * 0.9), "blona", MB, rot=(5, 0, 0), faza=0.0)
        with p.na("Skrzydlo%s2" % strona, obrot=_lus(G["rot2"], zn)):
            for i in range(npal):
                szer = dl_p[i] * math.tan(math.radians(katy_p[i + 1] - katy_p[i]))
                kb, mb = ("zar", "swiecacy") if (ogn and i == npal - 1) else (("blona_c" if i % 2 else "blona"), MB)
                with p.uklad(obrot=(6 if i % 2 else -5, zn * katy_p[i], 0)):     # pole błony przechylone wokół palca
                    p.klin("Blona %d" % i, (zn * dl_p[i] / 2, 0.0, -szer / 2), (t, dl_p[i], szer), kb, mb,
                           rot=(0, 0, zn * 90), faza=0.0)
                with p.uklad(obrot=(0, zn * katy_p[i], 0)):                     # kość palca na wierzchu błony
                    gp = 0.2 if i == 0 else 0.11
                    p.blok("Palec %d" % i, (zn * (dl_p[i] + 0.1) / 2, 0.03 if i == 0 else 0.07, 0),
                           (dl_p[i] + 0.1, gp, gp), "cialo" if i == 0 else zebro, MC if i == 0 else mzeb, faza=0.03)
                    if (N >= 3 and i == 0) or ("szpony" in dod and i < 2):
                        p.klin("Szpon", (zn * (dl_p[i] + 0.24), 0.02, 0.0), (0.16, 0.42, 0.26), "kolce", MK,
                               rot=(90, 0, 0), faza=0.0)
            p.zaczep("Skrzydlo%sKoniecAttachment" % strona, "Skrzydlo%s2" % strona,
                     razy_wektor(macierz_obrotu(*_lus(G["rot2"], zn)), (zn * L2, 0, 0)))

    # ---------------------------------------------------------------- ogon
    for i in range(4):
        gt = gro * (1.0 - 0.19 * i)
        with p.na("Ogon%d" % (i + 1), obrot=(-katy[i], 180, 0)):   # +Z biegnie wzdłuż ogona (w tył)
            cialo("Ogon%d" % (i + 1), (0, 0, lens[i] / 2), (gt, gt * 0.92, lens[i] + gt * 0.4), faza=fz * 1.3)
            if ZAR and i < 3:
                luska("Luska ogona", lens[i] * 0.66, gt * 1.2, gt * 0.46, lens[i] * 0.5, 0.15)
                if g >= 0.35:
                    p.blok("Zar ogona", (0, gt * 0.46 + 0.01, lens[i] * 0.5), (gt * 0.86, 0.1, lens[i] * 1.0), "zar_c",
                           "swiecacy", faza=0.0)
            if i == 0 and N <= 2:
                p.blok("Ogon spod", (0, -gt * 0.46 - 0.02, lens[i] / 2), (gt * 0.62, 0.06, lens[i]), "brzuch", "matowy",
                       faza=0.0)
            if nk and i < 2 and styl != "zabawka" and N == 4:
                h_ = hk * (0.62 - 0.14 * i)
                kolec("Kolec ogona", (0, gt * 0.46 + 0.14 + h_ / 2 - 0.05, lens[i] * 0.5),
                      (max(0.16, gt * 0.22), h_, h_ * 0.95), kol_k, swiec_k, rot=(0, 0, 0))
            if i == 3:
                _koniec_ogona(p, P, styl, koniec, lens[i], gt, g)
                p.zaczep("ZarOgonAttachment", "Ogon4", (0, gt * 0.6, 0))
                p.zaczep("OgonKoniecAttachment", "Ogon4",
                         razy_wektor(macierz_obrotu(-katy[i], 180, 0), (0, 0, lens[i] + 0.3)))

    # ---------------------------------------------------------------- nogi (udo / podudzie / stopa wzdłuż kości)
    for n in NOGI:
        przod = n.startswith("NogaP")
        j1, j2, j3 = G[n + "1"], G[n + "2"], G[n + "3"]
        with p.na(n + "1"):
            if N >= 3 or not przod:
                _wzdluz(p, "Udo", j1, j2, lw * (1.0 if przod else 1.2), lw * (1.2 if przod else 1.75), nadl=lw * 0.55,
                        faza=fz * 1.5, mat=MC)
        with p.na(n + "2"):
            _wzdluz(p, "Podudzie", j2, j3, lw * 0.76, lw * (0.82 if przod else 0.9), nadl=lw * 0.3, faza=fz, mat=MC)
        with p.na(n + "3"):
            p.blok("Stopa", (0, -ya / 2, lw * 0.3), (lw * 1.1, ya, lw * 1.6), "cialo_c", MC, faza=0.05)
            if N >= 3 and przod:
                p.blok("Pazury", (0, -ya * 0.66, lw * 1.16), (lw * 0.98, ya * 0.6, 0.18), "kolce", MK, faza=0.03)
    return p


def _rogi(p, P, styl, cz, top, tyl, zf):
    gw, gh, gd = P["gl"]
    typ = P["rogi"]
    MK = "polysk"
    swiec = "swiecacy" if P["zar"] >= 0.95 and styl != "zabawka" else MK

    def rog(x, y, z, rx, rz, dl, gr, kolor="kolce", mat=MK, zagiecie=0.5, tani=False):
        for zn in (1, -1):
            with p.uklad(pos=(zn * x, y, z), obrot=(rx, 0, -zn * rz)):
                if tani:                                         # klin: 1 część Roblox (ostrze)
                    p.klin("Rog", (0, dl / 2, 0), (gr * 0.8, dl, gr), kolor, mat, rot=(0, 180, 0), faza=0.02)
                else:                                            # ostrosłup ze szpicem przy tylnej krawędzi: 2 części
                    p.ostroslup("Rog", (0, dl / 2, 0), (gr, dl, gr), kolor, mat, gora=(0.0, 0.0),
                                przes_gory=(0.0, -gr * zagiecie), faza=0.0 if styl == "krysztal" else 0.02)

    def rog_nosa(dl):
        p.klin("Rog nosa", (0, cz[1] - gh / 2 + P["pysk"][1] + dl * 0.42, zf + P["pysk"][2] * 0.62),
               (0.3, dl, dl * 0.72), "kolce", MK, rot=(0, 180, 0), faza=0.02)

    if typ == "guzki":
        rog(gw * 0.3, top - 0.04, tyl + gd * 0.3, -20, 8, 0.32, 0.32, tani=True)
    elif typ == "male":
        rog(gw * 0.3, top - 0.04, tyl + gd * 0.28, -32, 12, 0.62, 0.34, tani=True)
    elif typ == "wstecz":
        rog(gw * 0.32, top - 0.06, tyl + gd * 0.2, -58, 18, 1.25, 0.34)
    elif typ == "wgore":
        rog(gw * 0.36, top - 0.06, tyl + gd * 0.22, -30, 26, 1.5, 0.36)
        rog(gw * 0.5, cz[1] - gh * 0.1, tyl + gd * 0.25, -78, 34, 0.7, 0.26, tani=True)
    elif typ == "klasyczne":
        rog(gw * 0.34, top - 0.06, tyl + gd * 0.2, -54, 20, 2.2, 0.42)
        rog(gw * 0.5, cz[1] - gh * 0.12, tyl + gd * 0.2, -80, 36, 1.1, 0.3, tani=True)
    elif typ == "byk":
        for zn in (1, -1):                                       # rogi byka: w bok i do przodu
            with p.uklad(pos=(zn * gw * 0.46, top - gh * 0.2, tyl + gd * 0.3), obrot=(0, 0, -zn * 78)):
                p.blok("Rog nasada", (0, 0.42, 0), (0.46, 0.84, 0.46), "kolce_c", MK, faza=0.04)
                with p.uklad(pos=(0, 0.8, 0), obrot=(58, 0, 0)):
                    p.ostroslup("Rog", (0, 0.62, 0), (0.44, 1.24, 0.44), "kolce", MK, gora=(0, 0), przes_gory=(0, 0.14),
                                faza=0.02)
        rog_nosa(0.86)
    elif typ == "korona":
        rog(gw * 0.32, top - 0.06, tyl + gd * 0.22, -62, 16, 3.6, 0.44)
        if styl != "zabawka":                                    # grzebień-wachlarz na czubku głowy
            p.klin("Grzebien", (0, top + gh * 0.5, cz[2] - gd * 0.2), (0.1, gh * 0.9, gd * 1.0), "blona", "matowy",
                   rot=(0, 180, 0), faza=0.0)
    elif typ == "prastare":
        rog(gw * 0.3, top - 0.06, tyl + gd * 0.25, -50, 14, 3.0, 0.54, mat=swiec)
        rog(gw * 0.48, top - gh * 0.16, tyl + gd * 0.2, -66, 36, 2.2, 0.4, tani=True)
        rog(gw * 0.5, cz[1] - gh * 0.3, tyl + gd * 0.3, -84, 52, 1.4, 0.34, mat=swiec, tani=True)
        rog_nosa(0.8)


def _koniec_ogona(p, P, styl, typ, dl_, gt, g):
    MK = "polysk"
    z0 = dl_ + gt * 0.1
    s = max(gt, 0.34)
    swiec = "swiecacy" if g >= 0.6 and styl != "zabawka" else MK
    kol = "zar" if (typ == "plomien" and styl != "zabawka") else "kolce"

    def grot(sz, dl, y=0.0, kolor=kol, mat=swiec, gr=0.16, dz=0.0):
        for zn in (1, -1):                                       # pozioma strzała: czytelna z kamery gry
            p.klin("Grot", (zn * sz / 4, y, z0 + dz + dl / 2), (gr, sz / 2, dl), kolor, mat, rot=(0, 180, zn * 90), faza=0.0)

    if typ == "grot_maly":
        grot(s * 1.7, s * 1.5, mat=MK)
    elif typ == "grot":
        grot(s * 2.6, s * 2.4, mat=MK)
    elif typ == "dwa_ostrza":                                    # DRAGON: dwie strzały jedna za drugą
        grot(s * 2.4, s * 1.9, mat=MK, dz=-s * 2.3)
        grot(s * 3.6, s * 2.8, mat=MK, dz=s * 0.1)
    elif typ == "plomien":
        grot(s * 2.9, s * 2.9)
        p.klin("Plomien ogona", (0, s * 0.55, z0 + s * 0.9), (0.2, s * 1.4, s * 1.6), "kolce", MK, rot=(0, 0, 0), faza=0.0)
    elif typ == "maczuga":
        p.blok("Maczuga", (0, 0, z0 + s * 0.5), (s * 1.7, s * 1.4, s * 1.7), "cialo_c", "matowy", rot=(0, 45, 0), faza=0.08)
        for rz in (0, 90, -90):
            with p.uklad(pos=(0, 0, z0 + s * 0.5), obrot=(0, 0, rz)):
                p.klin("Kolec maczugi", (0, s * 1.15, 0), (s * 0.5, s * 0.9, s * 0.7), "kolce", MK, rot=(0, 0, 0), faza=0.02)
        p.blok("Zar maczugi", (0, 0, z0 + s * 0.5), (s * 1.25, s * 0.3, s * 1.84), "zar", swiec, rot=(0, 45, 0), faza=0.0)
    elif typ == "wachlarz":
        grot(s * 4.0, s * 3.0, kolor="blona", mat="matowy", gr=0.09)
        p.klin("Promien wachlarza", (0, s * 0.42, z0 + s * 1.4), (0.16, s * 0.9, s * 2.8), "kolce", MK, rot=(0, 0, 0), faza=0.0)
        for zn in (1, -1):
            p.blok("Promien", (zn * s * 1.0, 0.03, z0 + s * 0.3), (0.16, 0.16, s * 1.9), "kolce", MK,
                   rot=(0, zn * 58, 0), faza=0.02)
    elif typ == "krysztaly":
        grot(s * 3.2, s * 3.0, gr=0.24)
        for rz, k_, m_ in ((24, "zar", swiec), (-24, "zar", swiec)):
            with p.uklad(pos=(0, 0, z0), obrot=(0, 0, rz)):
                p.klin("Krysztal ogona", (0, s * 0.9, s * 0.95), (0.26, s * 1.8, s * 2.0), k_, m_, rot=(0, 0, 0), faza=0.0)


# --------------------------------------------------------------------------- wersja uproszczona (dalekie smoki)
ROGI_LOD = {1: 0.32, 2: 0.6, 3: 1.2, 4: 1.5, 5: 2.2, 6: 1.6, 7: 3.4, 8: 3.0}


def zbuduj_stadium_lod(nr, zmiany_kolorow=None, id=None):
    """Wersja uproszczona (dzikie i dalekie smoki): najwyżej ok. 35 części, TE SAME stawy, zaczepy i klipy co pełna."""
    P = stadium(nr)
    G = geometria(P)
    p = Smok(id or P["id"] + "_lod", P["nazwa"].title() + " (uproszczony)", typ="stwor", skala=skala_stadium(P),
             faza=0.08, paleta=paleta_stadium(P["nr"], zmiany_kolorow))
    p.dane_stadium, p.geometria, p.styl = P, G, "zar"
    _szkielet(p, P, G)
    W, H, L = P["T"]
    gw, gh, gd = P["gl"]
    pw, ph, pl = P["pysk"]
    lw, ya, N, g = P["lw"], G["ya"], P["nr"], P["zar"]
    l1, l2, a1, a2, gr = P["szyja"]
    L1, L2, C = P["skrz"]
    lens, gro, katy, koniec = P["ogon"]
    cz, zf = G["cz"], G["zf"]
    top, tyl = cz[1] + gh / 2, cz[2] - gd / 2
    maly = P["oczy"][0] == "dziecko"
    with p.na("Tulow"):
        p.blok("Tulow", (0, 0, 0), (W, H, L), "cialo", faza=0.2)
        p.blok("Zar grzbietu", (0, H / 2 + 0.03, 0), (W * (0.8 + 0.2 * g), 0.12, L * 0.97), "zar_c", "swiecacy", faza=0)
        for z in (L * 0.25, -L * 0.25):
            p.blok("Luska grzbietu", (0, H / 2 + 0.14, z), (W * 1.14, 0.22, L * (0.42 - 0.1 * g)), "cialo_c", "matowy",
                   rot=(8, 0, 0))
        p.zaczep("BrzuchAttachment", "Tulow", (0, -H / 2 - 0.1, 0))
        p.zaczep("GrzbietAttachment", "Tulow", (0, H / 2 + 0.3, 0))
        p.zaczep("PiersAttachment", "Tulow", (0, -H * 0.06, L / 2 + 0.25))
        for i, z in enumerate((L * 0.3, 0.0, -L * 0.3)):
            p.zaczep("Zar%dAttachment" % (i + 1), "Tulow", (0, H / 2 + 0.2, z))
    for i, (nazwa, dl_, kat) in enumerate((("Szyja1", l1, a1), ("Szyja2", l2, a2))):
        gs = gr * (1.0 - 0.1 * i)
        with p.na(nazwa, obrot=(-kat, 0, 0)):
            p.blok(nazwa, (0, 0, dl_ / 2), (gs, gs, dl_ + gs * 0.55), "cialo")
            if i == 1:
                p.zaczep("GardloAttachment", "Szyja2",
                         razy_wektor(macierz_obrotu(-kat, 0, 0), (0, -gs / 2 - 0.1, dl_ * 0.6)))
    with p.na("Glowa"):
        p.blok("Czaszka", cz, (gw, gh, gd), "cialo", faza=0.2)
        p.blok("Pysk", (0, G["ys"], zf + pl / 2 - 0.06), (pw, ph, pl + 0.12), "cialo")
        e = 0.66 * P["oczy"][1]
        for zn in (1, -1):
            if maly:
                p.blok("Bialko", (zn * (gw / 2 - e * 0.42), top - e * 0.38, zf - e * 0.3), (e, e, e * 0.9), "bialy", "polysk")
                p.blok("Zrenica", (zn * (gw / 2 - e * 0.5), top - e * 0.24, zf - e * 0.14), (e * 0.5, e * 0.78, e * 0.64),
                       "oko", "polysk")
            else:
                p.blok("Oko", (zn * (gw / 2 + 0.01), cz[1] + gh * 0.12, cz[2] + gd * 0.2), (0.06, e * 0.42, e * 1.05), "oko",
                       "swiecacy", faza=0)
            with p.uklad(pos=(zn * gw * 0.32, top - 0.06, tyl + gd * 0.22),
                         obrot=(-52 if N > 2 else -25, 0, -zn * (72 if N == 6 else 16))):
                p.klin("Rog", (0, ROGI_LOD[N] / 2, 0), (0.3, ROGI_LOD[N], 0.38), "kolce", "polysk", rot=(0, 180, 0), faza=0.02)
        if not maly:
            p.blok("Helm", (0, top + 0.06, cz[2] + gd * 0.06), (gw * 1.12, 0.2, gd * 0.86), "cialo_c", "matowy", rot=(9, 0, 0))
        p.zaczep("PyskAttachment", "Glowa", (0, G["ys"] - ph * 0.2, zf + pl + 0.1))
        p.zaczep("GlowaAttachment", "Glowa", (0, top + 0.3, cz[2]))
    with p.na("Szczeka"):
        zl, zh = pl + 0.18 * gd, ph * P["zuch"]
        p.blok("Zuchwa", (0, -0.05 - zh * 0.3, zl / 2 - 0.02), (pw * 0.9, zh, zl), "cialo")
    for strona, zn in (("L", 1.0), ("P", -1.0)):
        with p.na("Skrzydlo%s1" % strona, obrot=_lus(G["rot1"], zn)):
            p.blok("Blona ramienia", (zn * L1 / 2, 0, -C * 0.46), (L1, 0.09, C * 0.92), "blona", "matowy", faza=0)
        with p.na("Skrzydlo%s2" % strona, obrot=_lus(G["rot2"], zn)):
            p.blok("Palec", (zn * L2 / 2, 0.03, 0), (L2 + 0.1, 0.2, 0.2), "cialo", faza=0.03)
            p.klin("Blona dloni", (zn * L2 / 2, 0, -C * 0.5), (0.09, L2, C * 1.0), "blona", "matowy", rot=(0, 0, -zn * 90),
                   faza=0)
            p.zaczep("Skrzydlo%sKoniecAttachment" % strona, "Skrzydlo%s2" % strona,
                     razy_wektor(macierz_obrotu(*_lus(G["rot2"], zn)), (zn * L2, 0, 0)))
    for i in range(4):
        gt = gro * (1.0 - 0.19 * i)
        with p.na("Ogon%d" % (i + 1), obrot=(-katy[i], 180, 0)):
            p.blok("Ogon%d" % (i + 1), (0, 0, lens[i] / 2), (gt, gt * 0.92, lens[i] + gt * 0.4), "cialo")
            if i == 0 and g >= 0.35:
                p.blok("Zar ogona", (0, gt * 0.46 + 0.01, lens[i] * 0.5), (gt * 0.86, 0.1, lens[i]), "zar_c", "swiecacy", faza=0)
            if i == 3:
                s_ = max(gt, 0.34)
                for zn in (1, -1):
                    p.klin("Grot", (zn * s_ * 0.6, 0, lens[i] + s_ * 1.2), (0.16, s_ * 1.2, s_ * 2.2), "kolce", "polysk",
                           rot=(0, 180, zn * 90), faza=0)
                p.zaczep("ZarOgonAttachment", "Ogon4", (0, gt * 0.6, 0))
                p.zaczep("OgonKoniecAttachment", "Ogon4",
                         razy_wektor(macierz_obrotu(-katy[i], 180, 0), (0, 0, lens[i] + 0.3)))
    for n in NOGI:
        with p.na(n + "2"):
            _wzdluz(p, "Podudzie", G[n + "2"], G[n + "3"], lw * 0.9, lw * 1.0, nadl=lw * 0.9)
        with p.na(n + "3"):
            p.blok("Stopa", (0, -ya / 2, lw * 0.3), (lw * 1.1, ya, lw * 1.6), "cialo_c", faza=0.05)
    return p


# --------------------------------------------------------------------------- jajo (osobny rig do klipu wyklucia)
def zbuduj_jajo(nr=1, id="smok_jajo"):
    """Jajo dopasowane do zwiniętego pisklęcia stadium `nr` (dla innych stadiów gra skaluje model). Niska miska „Dol”
    zostaje na ziemi, wysoka czapka „Gora” odlatuje, dwa odłamki opadają."""
    P = stadium(nr)
    pal = paleta_stadium(nr)
    p = Smok(id, "Jajo smoka", typ="stwor", skala=skala_stadium(P), faza=0.05, paleta=pal)
    D = 3.5                                                     # średnica jaja (jednostki projektu)
    zs = 0.2                                                    # jajo wysunięte ku przodowi: obejmuje głowę pisklęcia
    yp = 1.3                                                    # wysokość pęknięcia
    p.kosc("Dol", "Root", (0, 0, zs), czesc=(D, yp, D), srodek=(0, yp / 2, 0))
    p.kosc("Gora", "Dol", (0, yp, zs), czesc=(D, 2.8, D), srodek=(0, 1.4, 0))
    p.kosc("OdlamekL", "Dol", (1.3, yp, zs + 0.6), czesc=(0.6, 0.6, 0.3), dl=0.2)
    p.kosc("OdlamekP", "Dol", (-1.3, yp, zs - 0.5), czesc=(0.6, 0.6, 0.3), dl=0.2)
    with p.na("Dol"):
        p.walec("Jajo dol 1", (0, 0.34, 0), (D * 0.72, 0.68, D * 0.72), "skorupa", "matowy", segm=8)
        p.walec("Jajo dol 2", (0, 0.96, 0), (D * 0.94, 0.68, D * 0.94), "skorupa", "matowy", segm=8)
        p.walec("Zar pekniecia", (0, yp + 0.02, 0), (D * 0.88, 0.08, D * 0.88), "zar", "swiecacy", segm=8)
    with p.na("Gora"):
        p.walec("Jajo gora 1", (0, 0.42, 0), (D, 0.84, D), "skorupa", "matowy", segm=8)
        p.walec("Plama 1", (0, 0.5, 0), (D * 1.02, 0.24, D * 1.02), "cialo", "matowy", segm=8)
        p.walec("Jajo gora 2", (0, 1.2, 0), (D * 0.94, 0.76, D * 0.94), "skorupa", "matowy", segm=8)
        p.walec("Jajo gora 3", (0, 1.9, 0), (D * 0.76, 0.68, D * 0.76), "skorupa", "matowy", segm=8)
        p.walec("Plama 2", (0, 1.86, 0), (D * 0.78, 0.18, D * 0.78), "cialo", "matowy", segm=8)
        p.walec("Jajo gora 4", (0, 2.44, 0), (D * 0.46, 0.44, D * 0.46), "skorupa", "matowy", segm=8)
    for n, zn in (("OdlamekL", 1), ("OdlamekP", -1)):
        with p.na(n):
            p.klin("Odlamek", (0, 0.2, 0), (0.5, 0.5, 0.12), "skorupa_c", "matowy", rot=(0, zn * 40, 0), faza=0.0)
    return p


def liczba_czesci_roblox(p):
    """Ile części Roblox da ścieżka z klocków (po rozkładzie brył), bez niewidzialnych części kości."""
    from swiat.postacie.biblioteka.roblox_klocki import rozloz
    return sum(len([1 for x in rozloz(c) if min(x[3]) >= 0.001]) for c in p.json()["czesci"])
