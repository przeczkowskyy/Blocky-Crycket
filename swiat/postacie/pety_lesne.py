# -*- coding: utf-8 -*-
"""Wspólne kawałki pięciu petów z leśnego jajka (próba „jajka i pety”, swiat/pety_proba, 17.11.2026, propozycja).

To NIE jest model — moduły modeli to zoledziak.py, mchowy_slimak.py, lisciolis.py, swietlikowka.py, jelonek_gaju.py
i jajko_lesne.py. Tu są tylko:
  • klip_wyklucie(p, kosc, …)  — 30 kl. bez pętli: pet siedzi w jajku (kość głównego ciała niżej), wyskakuje
    z obrotem wokół pionu, ląduje z przysiadem; w grze gra go klient po pęknięciu jajka;
  • klip_radosc(p, kosc, …)    — 36 kl. bez pętli: przysiad, podskok z obrotem, lądowanie (po wykluciu, po wyborze
    peta w zagrodzie, gdy gracz skacze);
  • oczy(p, …)                 — duże „błyszczące” oczy z odblaskiem (2–3 bryły na oko), wspólny styl petów;
  • jajko_gladkie, klipy_jajka, tablica_szans — wspólny kształt i klipy jajek (las, Bagno) i tablica szans
    inkubatora (od 17.11 używają ich też pety Bagna: palkus, nenufarek, wazeczka, ognik, perlowa_wydra);
  • na_elipsoidzie, naklejka, oczy_okragle, usmiech, model, lata — obłe ciała z elipsoid (przebudowa petów lasu według
    arkuszy obrotów Pawła, noc 25/26.11.2026): oko, rumieniec czy łatka „przyklejone” do elipsoidy wzdłuż normalnej.
Klipy nie mają kanału skali (Roblox przenosi tylko położenie i obrót kości). Obrót 360° wokół pionu kończy się
w tej samej pozie co spoczynek, więc przejście do następnego klipu jest bez szwu.
"""

WYKLUCIE_KLATEK = 30
RADOSC_KLATEK = 36


def klip_wyklucie(p, kosc, glebokosc=0.9, wyskok=0.9, obrot=360.0, dodatki=None):
    """Wyklucie: kl. 0–5 w jajku (przes. w dół o `glebokosc`), kl. 12 najwyżej (`wyskok`) w pół obrotu,
    kl. 18 ląduje, kl. 21 przysiad, kl. 25 odbicie, kl. 30 spoczynek. dodatki(k) dopisuje ruchy innych kości."""
    k = p.klip("wyklucie", WYKLUCIE_KLATEK, petla=False)
    k.klucz(0, kosc, przes=(0, -glebokosc, 0), obrot=(0, 0, 0))
    k.klucz(5, kosc, przes=(0, -glebokosc * 0.7, 0), obrot=(-8, 0, 0))
    k.klucz(12, kosc, przes=(0, wyskok, 0), obrot=(6, obrot * 0.55, 0))
    k.klucz(18, kosc, przes=(0, 0.05, 0), obrot=(0, obrot, 0))
    k.klucz(21, kosc, przes=(0, -0.09, 0), obrot=(4, obrot, 0))
    k.klucz(25, kosc, przes=(0, 0.04, 0), obrot=(-2, obrot, 0))
    k.klucz(30, kosc, przes=(0, 0, 0), obrot=(0, obrot, 0))
    if dodatki:
        dodatki(k)
    return k


def klip_radosc(p, kosc, wysokosc=0.7, obrot=360.0, dodatki=None):
    """Radość: kl. 0 spoczynek, kl. 6 przysiad, kl. 15 najwyżej w pół obrotu, kl. 24 lądowanie, kl. 28 przysiad,
    kl. 36 spoczynek (obrót pełny — ta sama poza co na początku)."""
    k = p.klip("radosc", RADOSC_KLATEK, petla=False)
    k.klucz(0, kosc, przes=(0, 0, 0), obrot=(0, 0, 0))
    k.klucz(6, kosc, przes=(0, -0.1, 0), obrot=(6, 0, 0))
    k.klucz(15, kosc, przes=(0, wysokosc, 0), obrot=(-8, obrot * 0.5, 0))
    k.klucz(24, kosc, przes=(0, 0.02, 0), obrot=(0, obrot, 0))
    k.klucz(28, kosc, przes=(0, -0.08, 0), obrot=(5, obrot, 0))
    k.klucz(36, kosc, przes=(0, 0, 0), obrot=(0, obrot, 0))
    if dodatki:
        dodatki(k)
    return k


# ------------------------------------------------------------------ jajka (las, Bagno — wspólny kształt i klipy)
# Gładkie jajko z elipsoid (17.11 wieczorem; wcześniej warstwy klocków — z bliska nadal „ul”). W Robloksie elipsoida
# to Part ze SpecialMesh „Sphere” (roblox_klocki.rozloz), więc sylwetka jest naprawdę gładka, a brył jest mniej.
# Elipsoidy jako ułamki wysokości jajka (w) i połowy szerokości (R): (środek y, połowa wysokości, połowa szerokości).
# Dobrane do profilu jajka r(y) = R·sqrt(1 − ((y − 0,42w)/h)²), h = 0,42w niżej i 0,58w wyżej (odchyłka < 0,1R).
ELIPSOIDY_JAJKA = {
    "Skorupka": ("dol", 0.42, 0.42, 1.00),       # dół: najszersza, spód na ziemi
    "Skorupka gora": ("dol", 0.60, 0.34, 0.88),  # bark: węższa i wyższa (to zostaje po odskoczeniu czubka)
    "Czubek": ("gora", 0.78, 0.22, 0.68),        # czubek: mała kopułka — odskakuje przy pęknięciu
    "Wnetrze": ("dol", 0.86, 0.09, 0.60),        # świecące wnętrze pod czubkiem (w grze kolor rzadkości)
}


def promien_jajka(y, wys, szer, kosc=None):
    """Promień sylwetki jajka na wysokości y (od spodu; bez „Wnetrza”); kosc = "dol" | "gora" | None (obie)."""
    import math as _m
    R = szer / 2.0
    r = 0.0
    for nazwa, (ks, c, h, rr) in ELIPSOIDY_JAJKA.items():
        if nazwa == "Wnetrze" or (kosc and ks != kosc):
            continue
        d = (y - c * wys) / (h * wys)
        if abs(d) < 1.0:
            r = max(r, rr * R * _m.sqrt(1.0 - d * d))
    return r


def jajko_gladkie(p, kosc_dol, kosc_gora, k, y_peku, wys, szer, kolor, cetki=(), kolor_wnetrza="wnetrze", segm=24):
    """Jajko na dwóch kościach (staw dolnej = środek spodu, staw górnej = wysokość `y_peku`; skala k): dwie elipsoidy
    skorupki na dolnej kości, kopułka czubka na górnej, w środku świecąca elipsoida „Wnetrze” (zakryta czubkiem;
    widać ją, gdy czubek odskoczy). cetki: (kość "dol" | "gora", azymut w stopniach — 0 = przód +Z, 90 = lewo +X,
    y od spodu jajka, średnica, kolor) — wtopione kulki, z zewnątrz okrągłe plamki."""
    import math as _m
    R = szer / 2.0
    for nazwa, (ks, c, h, rr) in ELIPSOIDY_JAJKA.items():
        kosc = kosc_dol if ks == "dol" else kosc_gora
        y0 = 0.0 if ks == "dol" else y_peku
        with p.na(kosc, od="staw"):
            swieci = nazwa == "Wnetrze"
            p.kula(nazwa, (0, k * (c * wys - y0), 0), (k * 2 * rr * R, k * 2 * h * wys, k * 2 * rr * R),
                   kolor_wnetrza if swieci else kolor, "swiecacy" if swieci else "zwykly", segm=segm)
    for ks, azymut, y, d, kol in cetki:
        r = promien_jajka(y, wys, szer, ks) - 0.3 * d
        a = _m.radians(azymut)
        y0 = 0.0 if ks == "dol" else y_peku
        with p.na(kosc_dol if ks == "dol" else kosc_gora, od="staw"):
            p.kula("Cetka", (k * r * _m.sin(a), k * (y - y0), k * r * _m.cos(a)), (k * d, k * d * 0.8, k * d), kol,
                   "matowy", segm=8)


def klipy_jajka(p, kosc_jajka, kosc_czubka, z_peknieciem=True):
    """Klipy jajka: spoczynek (kołysanie, pętla); trzesienie (coraz mocniej, z podskokami) i pekniecie (czubek
    odskakuje i odlatuje) — te same klatki dla wszystkich jajek, więc wyklucie w grze trwa tak samo."""
    k = p.klip("spoczynek", 60, petla=True)
    k.cykl(kosc_jajka, "obrot", (1.5, 0, 2.5), czestosc=1)
    k.cykl(kosc_czubka, "obrot", (0, 0, 1.2), czestosc=2, faza=0.2)
    if not z_peknieciem:
        return
    k = p.klip("trzesienie", 36, petla=False)
    for f, kat in ((0, 0), (3, 4), (6, -4), (9, 6), (12, -6), (15, 8), (18, -8), (21, 10), (24, -11), (27, 13),
                   (30, -13), (33, 6), (36, 0)):
        k.klucz(f, kosc_jajka, obrot=(0, 0, kat))
    for f, y in ((0, 0), (13, 0), (15, 0.12), (17, 0), (25, 0), (27, 0.16), (29, 0), (36, 0)):
        k.klucz(f, kosc_jajka, przes=(0, y, 0))
    for f, kat in ((0, 0), (20, 0), (22, -5), (24, 4), (26, -6), (28, 5), (30, -4), (36, 0)):
        k.klucz(f, kosc_czubka, obrot=(kat, 0, 0))
    k = p.klip("pekniecie", 18, petla=False)
    k.klucz(0, kosc_czubka, przes=(0, 0, 0), obrot=(0, 0, 0))
    k.klucz(4, kosc_czubka, przes=(0, 0.18, 0), obrot=(-6, 0, 4))
    k.klucz(10, kosc_czubka, przes=(0.5, 1.6, 0.25), obrot=(-40, 30, 25), wyg="liniowo")
    k.klucz(18, kosc_czubka, przes=(1.1, 2.3, 0.5), obrot=(-85, 70, 55))
    k.klucz(0, kosc_jajka, przes=(0, 0, 0))
    k.klucz(3, kosc_jajka, przes=(0, -0.06, 0))
    k.klucz(8, kosc_jajka, przes=(0, 0.03, 0))
    k.klucz(18, kosc_jajka, przes=(0, 0, 0))


def tablica_szans(p, kosc, kolory_paskow, szanse, kolor_tablicy, kolor_ramy, kolor_papieru, mech=None):
    """Tablica na dwóch słupkach z paskami szans (podgląd w Blenderze; w grze napisy dokłada SurfaceGui na bryle
    „Papier”, a paski z modelu są pomijane). Układ: staw kości = środek spodu tablicy; obrót −20° ku patrzącemu."""
    with p.na(kosc, od="staw"), p.uklad(obrot=(0, -20, 0)):
        for zn in (1, -1):
            p.blok("Slupek", (zn * 1.9, 1.6, 0), (0.3, 3.2, 0.3), kolor_ramy, "matowy", faza=0.05)
        p.blok("Tablica", (0, 2.6, 0), (4.2, 2.8, 0.2), kolor_tablicy, "matowy", faza=0.06)
        p.blok("Papier", (0, 2.55, 0.12), (3.7, 2.4, 0.04), kolor_papieru, "matowy", faza=0.0)
        p.blok("Daszek", (0, 4.12, 0), (4.6, 0.25, 0.6), kolor_ramy, faza=0.05)
        if mech:
            p.blok("Daszek mech", (0.4, 4.3, 0.05), (3.2, 0.12, 0.5), mech, "matowy", faza=0.03)
        for i, (kolor, szansa) in enumerate(zip(kolory_paskow, szanse)):
            dl = 0.35 + 2.6 * szansa / szanse[0]
            y = 3.35 - i * 0.42
            p.blok("Pasek szansy", (-1.55 + 0.35 + dl / 2, y, 0.15), (dl, 0.26, 0.04), kolor, "matowy", faza=0.0)
            p.blok("Znak peta", (-1.55 + 0.12, y, 0.15), (0.24, 0.26, 0.04), kolor, "swiecacy", faza=0.0)


def oczy(p, x, y, z, szer=0.26, wys=0.32, kolor="tusz", teczowka=None, odstep=None):
    """Para oczu na ścianie z = `z` (układ bieżącego bloku `p.na`): czarne (albo `teczowka` z czarną źrenicą) z białym
    odblaskiem u góry od strony środka twarzy. x = odległość środka oka od osi."""
    for zn, s in ((1, "L"), (-1, "P")):
        if teczowka:
            p.blok("Teczowka " + s, (zn * x, y, z + 0.02), (szer, wys, 0.05), teczowka, "swiecacy", faza=0.02)
            p.blok("Zrenica " + s, (zn * x, y - 0.02, z + 0.05), (szer * 0.5, wys * 0.62, 0.04), kolor, "polysk",
                   faza=0.0)
        else:
            p.blok("Oko " + s, (zn * x, y, z + 0.02), (szer, wys, 0.05), kolor, "polysk", faza=0.03)
        p.blok("Blysk " + s, (zn * x - zn * szer * 0.2, y + wys * 0.22, z + 0.075), (szer * 0.36, wys * 0.3, 0.03),
               "bialy", "swiecacy", faza=0.0)


# ------------------------------------------------------------------ obłe ciała (pety lasu według arkuszy Pawła, 25/26.11)
def model(p, kosc):
    """Układ kości z początkiem w punkcie (0, 0, 0) MODELU: bryły podaje się w układzie modelu (spoczynek), a i tak
    poruszają się z kością. with model(p, "Tulow"): p.kula(...)."""
    return p.na(kosc, pos=tuple(-v for v in p.staw(kosc)))


def na_elipsoidzie(el, x, y, z_znak=1.0):
    """Punkt powierzchni elipsoidy el = (środek, średnice) o danych x, y (strona z_znak: +1 przód, −1 tył), normalna
    i obrót (rx, ry) kładący lokalną oś Z bryły wzdłuż normalnej. Zwraca (punkt, normalna, (rx, ry))."""
    import math as _m
    (cx, cy, cz), (sx, sy, sz) = el
    a, b, c = sx / 2.0, sy / 2.0, sz / 2.0
    u = ((x - cx) / a) ** 2 + ((y - cy) / b) ** 2
    z = cz + z_znak * c * _m.sqrt(max(0.0, 1.0 - u))
    n = ((x - cx) / a ** 2, (y - cy) / b ** 2, (z - cz) / c ** 2)
    d = _m.sqrt(sum(v * v for v in n)) or 1.0
    n = tuple(v / d for v in n)
    return (x, y, z), n, (-_m.degrees(_m.asin(max(-1.0, min(1.0, n[1])))), _m.degrees(_m.atan2(n[0], n[2])))


def naklejka(p, nazwa, el, x, y, size, kolor, mat="matowy", ksztalt="kula", obrot=0.0, wysun=0.0, z_znak=1.0,
             segm=12):
    """Płaska bryła (oko, rumieniec, łatka, kreska buzi) na elipsoidzie el: oś Z bryły wzdłuż normalnej, środek na
    powierzchni (+ wysun wzdłuż normalnej), obrot = obrót wokół normalnej (stopnie). ksztalt: "kula" | "blok"."""
    pt, n, (rx, ry) = na_elipsoidzie(el, x, y, z_znak)
    pos = tuple(pt[i] + n[i] * (wysun - 0.004) for i in range(3))
    if ksztalt == "kula":
        return p.kula(nazwa, pos, size, kolor, mat, rot=(rx, ry, obrot), segm=segm)
    return p.blok(nazwa, pos, size, kolor, mat, rot=(rx, ry, obrot), faza=0.0)


def oczy_okragle(p, el, x, y, szer=0.18, wys=0.22, kolor="tusz", grub=0.07, teczowka=None, mat_teczowki="swiecacy",
                 blysk_maly=True):
    """Para okrągłych oczu na elipsoidzie el (x = odległość środka oka od osi): ciemne oko (albo `teczowka` z czarną
    źrenicą) i białe odblaski „Blysk L/P” u góry od strony +X obrazu, mniejszy u dołu — jak na arkuszach Pawła."""
    for zn, s in ((1, "L"), (-1, "P")):
        ox = zn * x
        if teczowka:
            naklejka(p, "Teczowka " + s, el, ox, y, (szer, wys, grub), teczowka, mat_teczowki)
            naklejka(p, "Zrenica " + s, el, ox, y - wys * 0.04, (szer * 0.48, wys * 0.56, grub * 0.8), kolor, "polysk",
                     wysun=grub * 0.42)
        else:
            naklejka(p, "Oko " + s, el, ox, y, (szer, wys, grub), kolor, "polysk")
        naklejka(p, "Blysk " + s, el, ox + szer * 0.2, y + wys * 0.2, (szer * 0.36, wys * 0.32, grub * 0.5), "bialy",
                 "swiecacy", wysun=grub * 0.45)
        if blysk_maly:
            naklejka(p, "Blysk " + s, el, ox - szer * 0.22, y - wys * 0.24, (szer * 0.18, wys * 0.15, grub * 0.4),
                     "bialy", "swiecacy", wysun=grub * 0.4)


def usmiech(p, el, y, szer=0.16, kolor="tusz", grub=0.035, x=0.0):
    """Uśmiech „◡” z trzech kresek przyklejonych do elipsoidy el (środek kreski dolnej na wysokości y)."""
    naklejka(p, "Buzia", el, x, y, (szer * 0.5, grub, grub), kolor, "matowy", ksztalt="blok")
    for zn in (1, -1):
        naklejka(p, "Buzia", el, x + zn * szer * 0.36, y + szer * 0.1, (szer * 0.36, grub, grub), kolor, "matowy",
                 ksztalt="blok", obrot=zn * 35.0)


def lata(el, n, d, s=0.1):
    """Łata innego koloru na elipsoidzie el (jasny brzuszek, pyszczek, maska): elipsoida, która wystaje z el dokładnie
    za płaszczyzną n·p = d w układzie znormalizowanym (el = kula jednostkowa; n = wektor jednostkowy ku łacie,
    d = 0 → pół elipsoidy, d → 1 → mała łata). Wystaje najwyżej o ok. s/2 promienia (s małe = płasko).
    Zwraca (środek, średnice) do p.kula(...)."""
    import math as _m
    (cx, cy, cz), (sx, sy, sz) = el
    dl = _m.sqrt(sum(v * v for v in n)) or 1.0
    n = tuple(v / dl for v in n)
    k = _m.sqrt(max(1e-6, 1.0 + s * s - 2.0 * d * s))   # skala kopii sfery jednostkowej przesuniętej o s wzdłuż n
    a, b, c = sx / 2.0, sy / 2.0, sz / 2.0
    return (cx + s * a * n[0], cy + s * b * n[1], cz + s * c * n[2]), (sx * k, sy * k, sz * k)


def lata_przez(el, p1, p2, s=0.1, bok=None):
    """Łata, której granica przechodzi przez dwa punkty powierzchni el leżące w płaszczyźnie symetrii x = 0
    (p1, p2 = (y, z_znak): wysokość i strona +1 przód / −1 tył), z łatą po stronie `bok` (wektor w układzie
    modelu wskazujący łatę, np. (0, −1, 1) = dół-przód). Zwraca (środek, średnice)."""
    import math as _m
    (cx, cy, cz), (sx, sy, sz) = el
    b, c = sy / 2.0, sz / 2.0
    pts = []
    for y, zn in (p1, p2):
        yy = (y - cy) / b
        pts.append((yy, zn * _m.sqrt(max(0.0, 1.0 - yy * yy))))
    (y1, z1), (y2, z2) = pts
    # n = (0, ny, nz) z n·P1 = n·P2: ny (y1 − y2) = −nz (z1 − z2)
    ny, nz = -(z1 - z2), (y1 - y2)
    dl = _m.hypot(ny, nz)
    ny, nz = ny / dl, nz / dl
    if bok is not None and ny * bok[1] + nz * bok[2] < 0:
        ny, nz = -ny, -nz
    d = ny * y1 + nz * z1
    return lata(el, (0.0, ny, nz), d, s)
