# -*- coding: utf-8 -*-
"""Wylęgarnia petów (mapa v2 „Krzywe Miasteczko”, karta PROJEKT.md 5.4) — budynek-jajo, które właśnie się wykluwa.

Skorupa `biel` z 4 walców o pionowej osi (środek (0; −2)), czwarty walec przechylony −5° (pochylenie „−” z karty),
pod nim zygzak pęknięcia w tuszu i ułamane zęby skorupy. Kapsel `dach_wylegarnia` uchylony łącznie o −25° (karta: −20°;
więcej, żeby slime 4 × 4 × 4 zmieścił się pod krawędzią przy wysokości ≤ 28) — spod niego wygląda świecący pet-slime
i głową podpiera kapsel. U podstawy gniazdo z 16 belek z przerwą ≥ 11 przed drzwiami i trzy klockowe jajka. Szyld:
dwustronna pomarańczowa łapa na czarnym medalionie, na krzywym wysięgniku po lewej. Echo: wielka miska z kością
przy prawym boku. Odstępstwa od karty: kapsel niższy (walce 2,6 i 1,4, kopuła Ø 8,4), drzwi w ganku-wykuszu skręconym
o −14° (dolny walec Ø 16 jest węższy niż portal), wysięgnik szyldu sięga 3,8 poza działkę (powyżej 9).
Części: 154 (walce 38, kule 1, Neon 3, z kolizją 9).

Konwencja (PROJEKT.md 5.0): (0, 0, 0) = środek działki na ziemi, front z wejściem ku +Z, działka 30 × 28.
Podgląd:  python -B swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/wylegarnia.py --wyj <folder> --szer 1000
"""
import math
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402

NAZWA = "Wylegarnia"
OBRYS = (30, 28)                 # szer (lokalne X) × gł (lokalne Z)
WYSOKOSC = 28
BUDZET = 300
INTERAKCJA = (-5.0, 18.0)        # przed drzwiami, 4 study przed krawędzią działki
OBRYS_SYLWETKI = False           # PROJEKT 5.0 p. 4: Highlight w budynkach zakazany — obrys robimy z klocków (tusz)

SKORUPA, KOD = "biel", "dach_wylegarnia"
CZ = -2.0                        # środek jaja (z)
# walce skorupy: (x środka, promień, y0, y1); co drugi przesunięty o 0,6 w bok
WALCE = ((0.0, 8.0, 0.0, 4.0), (0.6, 10.0, 4.0, 10.0), (0.0, 10.5, 10.0, 15.0))
C4_X, C4_R, C4_Y0, C4_H, C4_RZ = 0.6, 9.5, 14.2, 4.5, -5.0
DRZWI_X, DRZWI_Z, DRZWI_RY = -5.0, 7.4, -14.0


def _na_walcu(cx, r, phi, y, wsuw=0.0):
    """Punkt na licu walca skorupy (środek (cx; CZ)) pod kątem phi° od +Z (ku +X), wysunięty o wsuw; zwraca (pos, ry)."""
    a = math.radians(phi)
    rr = r + wsuw
    return (cx + rr * math.sin(a), y, CZ + rr * math.cos(a)), phi


def buduj(s, rnd):
    _skorupa(s)
    _gora(s, rnd)
    _drzwi_i_okna(s)
    _gniazdo(s, rnd)
    _szyld_lapa(s)
    _miska(s)
    _znaki_i_rekwizyty(s, rnd)
    zestaw.punkt_interakcji(s, NAZWA, INTERAKCJA)
    if OBRYS_SYLWETKI:
        s.obrys_sylwetki()


# --------------------------------------------------------------------------- skorupa
def _skorupa(s):
    for i, (cx, r, y0, y1) in enumerate(WALCE):
        s.walec("Skorupa", (cx, (y0 + y1) / 2.0, CZ), r, y1 - y0, SKORUPA if i != 1 else cien(s, SKORUPA, 0.95), os="y")
    # kropki — płaskie walce o osi promieniowej
    with s.cechy(kolizja=False, cien=False):
        for (ci, phi, y, d) in ((2, -62, 13.0, 3.6), (1, 24, 6.6, 3.0), (1, 105, 8.0, 4.0), (2, 150, 12.4, 3.2),
                                (1, 212, 7.0, 3.6), (2, 262, 12.2, 2.6)):
            cx, r, _, _ = WALCE[ci]
            pos, ry = _na_walcu(cx, r, phi, y, 0.08)
            s.walec("Kropka", pos, d / 2.0, 0.7, KOD, os="z", rot=(0, ry, 0))


# --------------------------------------------------------------------------- czubek: pęknięcie, zęby, kapsel, slime
def _gora(s, rnd):
    with s.uklad(pos=(C4_X, C4_Y0, CZ), obrot=(0, 0, C4_RZ)):
        s.walec("Skorupa czubek", (0, C4_H / 2.0, 0), C4_R, C4_H, SKORUPA, os="y")
        H = C4_H
        with s.cechy(kolizja=False):
            # ciemne wnętrze skorupy widoczne pod uchylonym kapslem
            s.walec("Wnętrze jaja", (0, H + 0.1, 0), C4_R - 0.6, 0.4, "tusz", os="y")
            # zygzak pęknięcia: 10 belek tusz po obwodzie
            R = (C4_R + 0.25) / math.cos(math.radians(18))
            pkt = []
            for k in range(11):
                a = math.radians(9 + 36 * k)
                y = H - (0.45 if k % 2 == 0 else 2.7)
                pkt.append((R * math.sin(a), y, R * math.cos(a)))
            for p1, p2 in zip(pkt, pkt[1:]):
                s.belka("Pęknięcie", p1, p2, 0.6, "tusz", "SmoothPlastic", 0.6)
            # kapsel: zawias przy prawej krawędzi, uchylony o −20° względem czubka (razem −25°); lewą krawędź
            # podpiera głową slime
            PX, KAT = 8.4, 20.0
            tg = math.tan(math.radians(KAT))
            lid_c = (PX - 7.5, 0.3)                            # środek kapsla na czubku (x, z)
            SX, SZ = -6.2, 3.6                                 # slime (środek podstawy w układzie czubka)
            # zęby ułamanej skorupy na krawędzi — tylko tam, gdzie kapsel jest dość wysoko i nie zasłaniają slime'a
            phi_s = math.degrees(math.atan2(SX, SZ))
            for k in range(12):
                phi = 15 + 30 * k + rnd.uniform(-6, 6)
                if abs((phi - phi_s + 180) % 360 - 180) < 22:
                    continue
                a = math.radians(phi)
                rr = C4_R - 0.4
                x, z = rr * math.sin(a), rr * math.cos(a)
                h = 2.4 if k % 2 else 1.6
                if math.hypot(x - lid_c[0], z - lid_c[1]) < 8.3:
                    h = min(h, (PX - x) * tg - 0.5)
                if h < 0.8:
                    continue
                with s.uklad(pos=(x, H - 0.1, z), obrot=(0, phi, 0)):
                    s.klin("Ząb skorupy", (0, h / 2.0, 0), (0.6, h, 2.6), SKORUPA, rot=(0, -90 if k % 3 else 90, 0))
            with s.uklad(pos=(PX, H + 0.05, 0.3), obrot=(0, 0, -KAT)):
                s.walec("Kapsel rant", (-7.5, 0.3, 0), 7.9, 0.6, "tusz", os="y")
                s.walec("Kapsel", (-7.5, 0.4 + 1.3, 0), 7.5, 2.6, KOD, os="y")
                s.walec("Kapsel", (-6.6, 3.0 + 0.7, 0.3), 5.0, 1.4, KOD, os="y")
                with s.cechy(cien=False):                      # białe kropki: kapsel to kawałek skorupy
                    for (x, z, r) in ((-12.6, 2.4, 1.3), (-3.6, -4.8, 1.1)):
                        s.walec("Kapsel kropka", (x, 3.05, z), r, 0.3, SKORUPA, os="y")
                # ułamana krawędź kapsla: zęby w dół (tylko tam, gdzie kapsel jest wysoko nad skorupą i nie ma slime'a)
                for phi in (-162, -128, -18, 12, 168):
                    a = math.radians(phi)
                    h = 1.5 if phi % 2 else 1.2
                    with s.uklad(pos=(-7.5 + 7.15 * math.sin(a), 0.5, 7.15 * math.cos(a)), obrot=(0, phi, 0)):
                        s.klin("Kapsel ząb", (0, -h / 2.0, 0), (0.6, h, 2.4), KOD, rot=(0, -90, 180))
            # gałka-kopuła: liczona ręcznie i dodana bez obrotu (zakres podglądu liczy obróconą kulę jak sześcian)
            gx, gy = -6.0, 3.3                                 # w układzie kapsla
            ka = math.radians(-KAT)
            px = PX + gx * math.cos(ka) - gy * math.sin(ka)
            py = H + 0.05 + gx * math.sin(ka) + gy * math.cos(ka)
            with s.uklad(pos=(px, py, 0.6), obrot=(0, 0, -C4_RZ)):
                s.kula("Kapsel kopuła", (0, 0, 0), 8.4, KOD)
            # pet-slime wyglądający spod kapsla (z przodu, po lewej) — głową podpiera uchyloną krawędź
            with s.uklad(pos=(SX, H + 0.35, SZ), obrot=(0, 22, 0)):
                with s.cechy(cien=False):
                    s.blok("Slime", (0, 2.0, 0), (4.0, 4.0, 4.0), "neon_slime", "Neon")
                    for sx in (-1, 1):
                        s.blok("Slime oko", (sx * 0.95, 2.5, 2.1), (0.9, 1.4, 0.3), "tusz")
                        s.blok("Slime blik", (sx * 0.95 + 0.2, 2.85, 2.3), (0.35, 0.35, 0.2), "biel")
                    s.blok("Slime uśmiech", (0, 1.25, 2.1), (1.4, 0.35, 0.3), "tusz", rot=(0, 0, -6))


# --------------------------------------------------------------------------- wejście i okna
def _drzwi_i_okna(s):
    with s.uklad(pos=(DRZWI_X, 0, DRZWI_Z), obrot=(0, DRZWI_RY, 0)):
        # ganek-wykusz w skorupie: blok + półwalec, w nim portal łukowy
        s.blok("Ganek", (0, 3.0, -3.0), (11.2, 6.0, 6.0), SKORUPA)
        with s.cechy(kolizja=False):
            s.walec("Ganek łuk", (0, 6.0, -3.0), 5.6, 6.0, SKORUPA, os="z")
        zestaw.drzwi(s, (0, 0, 0), 8.0, 10.0, kolor=KOD, luk=True, prog="kamien_cokol")
    # okna okrągłe Neon po prawej stronie (drzwi po lewej — asymetria)
    for ci, phi, y, d, prz in ((2, 34, 12.4, 4.0, 0), (1, 62, 6.6, 3.0, 0)):
        cx, r, _, _ = WALCE[ci]
        pos, ry = _na_walcu(cx, r, phi, y, -0.15)
        zestaw.okno(s, pos, d, ksztalt="okragle", przechyl=prz, swiatlo="neon_slime", ry=ry)


# --------------------------------------------------------------------------- gniazdo
def _gniazdo(s, rnd):
    phi_drzwi = math.degrees(math.atan2(DRZWI_X, DRZWI_Z - CZ))
    # przerwa przed drzwiami liczona między KOŃCAMI belek: wolna cięciwa ≥ 11 na promieniu 10,6 plus pół belki (3,5)
    przerwa = 2.0 * (math.degrees(math.asin(5.5 / 10.6)) + math.degrees(3.5 / 10.6))
    luk = 360.0 - przerwa
    with s.cechy(kolizja=False):
        for i in range(16):
            warstwa = i % 2
            phi = phi_drzwi + przerwa / 2.0 + luk * i / 15.0
            a = math.radians(phi)
            rr = 10.6 + rnd.uniform(-0.3, 0.3) - 0.9 * warstwa
            x, z = rr * math.sin(a), CZ + rr * math.cos(a)
            dl = rnd.uniform(6.0, 7.0)
            g = rnd.uniform(1.3, 1.6)
            y = 0.6 + 1.2 * warstwa + rnd.uniform(-0.05, 0.15)
            kol = "drewno_jasne" if i % 3 == 1 else "drewno"
            s.blok("Gniazdo belka", (x, y, z), (g, g, dl), kol, "Wood",
                   rot=(rnd.uniform(-7, 7) + (10 if warstwa else 0), phi + 90 + rnd.uniform(-14, 14),
                        rnd.uniform(-6, 6) + (rnd.choice((-8, 8)) if warstwa else 0)))


# --------------------------------------------------------------------------- szyld: łapa na wysięgniku
def _szyld_lapa(s):
    with s.cechy(kolizja=False):
        xe, ye, _ = zestaw.lamana(s, "Wysięgnik", [(2.6, 1.0, 80), (2.2, 0.9, -40), (1.4, 0.8, -30)], "drewno_ciemne", "Wood",
                                  start=(-9.4, 10.8), z=-0.1)
        # łapa dwustronna: poduszka i palce przechodzą przez płetwę, więc z tyłu też widać łapę;
        # wysięgnik kończy się tuż za tylnym licem poduszki (nie przebija jej)
        with s.uklad(pos=(xe + 0.3, ye + 0.6, 1.3), obrot=(10, 18, 12)):
            s.walec("Łapa płetwa", (0, 0, 0), 5.0, 0.4, "tusz", os="z")
            s.walec("Łapa poduszka", (0, -1.3, 0), 3.0, 1.4, "pomarancz", os="z")
            for a in (-55, -20, 20, 55):
                r = math.radians(a)
                s.walec("Łapa palec", (3.95 * math.sin(r), -1.3 + 4.0 * math.cos(r), 0), 1.05, 1.4, "pomarancz", os="z")
            # chorągiewka duetu (znak miasteczka) zatknięta na medalionie
            zestaw.choragiewka_duetu(s, (1.2, 4.6, 0), "kot", przechyl=3)


# --------------------------------------------------------------------------- echo: miska z kością
def _miska(s):
    with s.uklad(pos=(10.6, 0, 9.6)):
        s.walec("Miska", (0, 0.9, 0), 3.5, 1.8, KOD, os="y")
        with s.cechy(kolizja=False):
            s.walec("Miska wnętrze", (0, 1.65, 0), 2.8, 0.5, "tusz", os="y")
            with s.uklad(pos=(0.3, 2.3, 0.2), obrot=(0, 25, 14)):
                s.blok("Kość", (0, 0, 0), (4.6, 0.9, 0.9), SKORUPA)
                for sx in (-1, 1):
                    for sz in (-1, 1):
                        s.blok("Kość głowa", (sx * 2.45, 0.05 * sz, sz * 0.55), (1.2, 1.2, 1.2), SKORUPA, rot=(0, 0, 45))


# --------------------------------------------------------------------------- znaki miasteczka i rekwizyty
def _znaki_i_rekwizyty(s, rnd):
    # wypadnięty klocek z dolnej skorupy (prawy bok)
    cx, r, _, _ = WALCE[1]
    pos, ry = _na_walcu(cx, r, 92, 6.0)
    zestaw.wypadniety_klocek(s, pos, (13.4, 0, -4.0), SKORUPA, ry=ry)
    # łaty-plastry na skorupie (tył i lewy bok)
    cx, r, _, _ = WALCE[2]
    pos, ry = _na_walcu(cx, r, 172, 13.0, 0.05)
    zestaw.lata(s, pos, 2.8, 2.2, "pomarancz", ry=ry, przechyl=-14)
    cx, r, _, _ = WALCE[1]
    pos, ry = _na_walcu(cx, r, 245, 6.4, 0.05)
    zestaw.lata(s, pos, 2.6, 2.2, "pomarancz", ry=ry, przechyl=9)
    # trzy klockowe jajka w gnieździe (duże–średnie–małe), każde przechylone inaczej
    with s.cechy(kolizja=False):
        for (phi, rr, y0, k, kol, kropka, rot) in ((40, 9.7, 0.9, 1.2, KOD, SKORUPA, (8, 20, -10)),
                                                    (64, 10.0, 0.7, 1.0, SKORUPA, "pomarancz", (-6, -15, 9)),
                                                    (22, 9.8, 0.5, 0.8, "pomarancz", SKORUPA, (10, 35, 6))):
            a = math.radians(phi)
            with s.uklad(pos=(rr * math.sin(a), y0, CZ + rr * math.cos(a)), obrot=rot):
                s.blok("Jajko", (0, 0.5 * k, 0), (2.2 * k, 1.0 * k, 2.2 * k), kol)
                s.blok("Jajko", (0, 1.9 * k, 0), (3.0 * k, 1.8 * k, 3.0 * k), kol)
                s.blok("Jajko", (0, 3.4 * k, 0), (2.0 * k, 1.2 * k, 2.0 * k), kol)
                with s.cechy(cien=False):
                    s.blok("Jajko kropka", (0.3 * k, 2.0 * k, 1.5 * k + 0.1), (1.1 * k, 1.0 * k, 0.3), kropka)
    # rekwizyty: beczka z wodą i skrzynia (lewy przód), kwiaty przy wejściu, ślady łap
    zestaw.beczka(s, (-12.2, 0, 9.6), "woda", przechyl=(0, -7))
    zestaw.skrzynia(s, (-12.6, 0, 4.6), ry=-70, dl=3.6, a=3.0, przechyl=8)
    zestaw.kwiaty(s, (3.6, 0, 11.6), ry=-8, kolory=("pomarancz", "biel"))
    with s.cechy(kolizja=False, cien=False):
        for i, (x, z, k) in enumerate(((-3.6, 10.8, -20), (-6.4, 12.6, -8))):
            with s.uklad(pos=(x, 0, z), obrot=(0, k, 0)):
                s.blok("Ślad łapy", (0, 0.1, 0.2), (1.6, 0.2, 1.4), "drewno_ciemne")
                for dx in (-0.6, 0.0, 0.6):
                    s.blok("Ślad palec", (dx, 0.1, -0.85 - 0.2 * (dx == 0.0)), (0.45, 0.2, 0.5), "drewno_ciemne")
