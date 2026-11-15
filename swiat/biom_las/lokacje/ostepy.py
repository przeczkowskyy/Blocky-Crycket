# -*- coding: utf-8 -*-
"""Lokacje Ciernistych Ostępów: Wilcza Skała, Jeżynowy Labirynt, Szumiący Próg (wodospad i sekretna szczelina),
Wrota Bagna."""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_TU)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import geo, skaly  # noqa: E402
from swiat.biom_las.lokacje import wspolne  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402
from swiat.krzywe_miasteczko import zestaw  # noqa: E402


def wilcza_skala(s, G, rnd, L):
    """Łupkowa iglica 50 jak wilcze ucho: trzy bryły zwężające się ku górze, każda przechylona mocniej, jasny rant od
    słońca, czubek-ucho z klina narożnego, dwie bursztynowe szczeliny-oczy; półki-stopnie na szczyt (co 4,5)."""
    x, z = L["x"], L["z"]
    ry0 = math.degrees(math.atan2(-35 - x, -35 - z))           # oczy patrzą ku polanie
    with s.grupa("Punkty/WilczaSkala"), s.uklad(pos=(x, 0, z), obrot=(0, ry0, 0)):
        with s.uklad(obrot=(0, 0, 5)):
            s.blok("Skała", (0, 7.0, 0), (22.0, 16.0, 18.0), "kamien_lochu", "Slate")
            with s.uklad(pos=(-1.0, 14.0, 0.5), obrot=(0, 14, 6)):
                s.blok("Skała", (0, 7.5, 0), (15.0, 15.0, 12.5), "kamien_lochu", "Slate")
                with s.uklad(pos=(-1.0, 14.0, 0), obrot=(4, -10, 8)):
                    s.blok("Skała", (0, 6.5, 0), (9.5, 13.0, 8.0), "kamien_lochu", "Slate")
                    s.naroznik("Wilcze ucho", (0, 16.5, 0), (8.0, 8.0, 6.0), "kamien_lochu", "Slate", rot=(0, 90, 0))
                    with s.cechy(kolizja=False):
                        s.blok("Rant", (4.85, 6.5, 0), (0.4, 12.0, 8.1), "kamien_cieply", "Slate")
                with s.cechy(kolizja=False):
                    s.blok("Rant", (7.6, 7.5, 0), (0.4, 14.0, 12.6), "kamien_cieply", "Slate")
                    with s.cechy(cien=False):
                        for xx in (-3.2, 3.2):
                            s.blok("Oko", (xx, 9.5, 6.3), (2.8, 0.9, 0.4), "neon_okno", "Neon", rot=(0, 0, -xx * 3))
            with s.cechy(kolizja=False):
                s.blok("Rant", (11.1, 7.0, 0), (0.4, 15.0, 18.1), "kamien_cieply", "Slate")
    with s.grupa("Ostepy/Lokacje/WilczaSkala"), s.uklad(pos=(x, 0, z), obrot=(0, ry0, 0)):
        for i in range(9):
            a = math.radians(-60 + 46 * i)
            r = 12.5 - 0.6 * i
            y = 4.5 * (i + 1)
            s.blok("Półka", (r * math.cos(a), y - 0.6, r * math.sin(a)), (6.0, 1.2, 4.2), "kamien_cokol", "Slate",
                   rot=(0, -math.degrees(a) + 90, rnd.uniform(-3, 3)))
    wspolne.ognisko(s, rnd, (-252, 0, -45))
    G.zajmij(x, z, 16)


def jezynowy_labirynt(s, G, rnd, L):
    """Ściany jeżyn 10 z jasnymi kolcami: kratka 6 × 6 w kole r 45 wycięta wzdłuż korytarza (szer. 14) i polanki
    środka (r 17), sklejona w długie bloki. W środku pogryziona skrzynia i stos kości-klocków (E: skrzynia raz na dobę)."""
    cx, cz, R = L["x"], L["z"], L["r"]
    kor = next(sc for sc in G.U["sciezki"] if sc["id"] == "korytarz_labiryntu")["pts"]
    kom = 6.0
    n = int(2 * R / kom) + 1
    siatka = {}
    for i in range(n):
        for j in range(n):
            px, pz = cx - R + (i + 0.5) * kom, cz - R + (j + 0.5) * kom
            if math.hypot(px - cx, pz - cz) > R:
                continue
            if geo.odl_lamana((px, pz), kor) < 7.0 + kom * 0.5 or math.hypot(px - cx, pz - cz) < 17.0 + kom * 0.5:
                continue
            siatka[(i, j)] = (px, pz)
    with s.grupa("Ostepy/Lokacje/JezynowyLabirynt"):
        uzyte = set()
        for j in range(n):
            i = 0
            while i < n:
                if (i, j) not in siatka or (i, j) in uzyte:
                    i += 1
                    continue
                k = i
                while (k + 1, j) in siatka and (k + 1, j) not in uzyte and k - i < 6:
                    k += 1
                for q in range(i, k + 1):
                    uzyte.add((q, j))
                x0 = cx - R + i * kom
                x1 = cx - R + (k + 1) * kom
                pz = cz - R + (j + 0.5) * kom
                h = rnd.uniform(9.0, 10.5)
                kol = "jezyna" if (i + j) % 2 else cien(s, "jezyna", 1.15)
                s.blok("Ściana jeżyn", ((x0 + x1) / 2.0, h / 2.0 - 0.5, pz), (x1 - x0, h + 1.0, kom), kol)
                # po przeglądzie: gładkie fioletowe bloki → ściana ma garbaty wierzch z kęp liści (ciemna zieleń na
                # fioletowych pędach), jagody i kolce; kępy nie wychodzą poza lico ściany więcej niż 0,6 (korytarz 14)
                dl = x1 - x0
                nk = max(1, int(round(dl / 9.0)))
                with s.cechy(kolizja=False, cien=False):
                    for q in range(nk):
                        qx = x0 + (q + 0.5) * dl / nk + rnd.uniform(-1.0, 1.0)
                        kh = rnd.uniform(2.2, 4.0)
                        s.blok("Jeżyna liście", (qx, h + kh / 2.0 - 0.2, pz), (min(dl / nk + 1.0, 9.5), kh, kom + 1.2),
                               rnd.choice(("lisc_ciemny", "runo_ciemne", cien(s, "jezyna", 1.3))), rot=(0, rnd.choice((-12, -6, 6, 12)), rnd.uniform(-6, 6)))
                        if rnd.random() < 0.55:
                            s.blok("Jagoda", (qx + rnd.uniform(-2.5, 2.5), h + kh - 0.1, pz + rnd.choice((-1, 1)) * rnd.uniform(1.0, 2.6)),
                                   (1.0, 1.0, 1.0), cien(s, "jezyna", 0.75), rot=(20, 45, 10))
                    if (i + j) % 2 == 0:
                        s.naroznik("Kolec", ((x0 + x1) / 2.0 + rnd.uniform(-2, 2), h + 0.6, pz + kom / 2.0 + 0.2), (1.0, 1.8, 1.0),
                                   "jezyna_kolec", rot=(0, rnd.choice((0, 90, 180, 270)), 90))
                i = k + 1
        # środek: pogryziona skrzynia (≥ 13 od środka, żeby plac walki r 12 został czysty) i kości
        with s.uklad(pos=(cx, 0, cz)):
            zestaw.skrzynia(s, (0.0, 0, -14.5), ry=12, dl=3.6, a=3.0, przechyl=10, kolor="drewno")
            wspolne.punkt_e(s, "Ostepy/Lokacje/JezynowyLabirynt", (0.0, 0, -11.5))
            with s.cechy(kolizja=False, cien=False):
                for k in range(7):
                    a = rnd.uniform(0, 2 * math.pi)
                    r = rnd.uniform(4, 9)
                    s.blok("Kość-klocek", (r * math.cos(a), 0.35, r * math.sin(a)), (2.2, 0.5, 0.6), "biel", rot=(0, rnd.uniform(0, 180), 0))
    G.zajmij(cx, cz, R + 2)


def szumiacy_prog(s, G, rnd, L):
    """Biały wodospad z grani (32) przed sekretną szczeliną: trzy płyty bez kolizji (da się przejść na wylot), mgiełka,
    tęczowy łuk z trzech pasów nad misą, wypadnięty niebieski klocek w wodzie."""
    mx, mz = -345.0, -398.0                                   # usta szczeliny w ścianie grani
    with s.grupa("Punkty/SzumiacyProg"), s.cechy(kolizja=False):
        for i, (y0, y1, dz, sz) in enumerate(((32.5, 22.0, 0.0, 11.0), (22.4, 11.0, 0.9, 12.0), (11.4, 0.2, 1.8, 13.0))):
            s.blok("Wodospad", (mx, (y0 + y1) / 2.0, mz + 1.2 + dz), (sz, y0 - y1, 1.0), "biel", rot=(4, 0, (-1) ** i * 2))
            s.blok("Wodospad pasmo", (mx - 2.5, (y0 + y1) / 2.0, mz + 1.8 + dz), (1.2, y0 - y1 - 1.0, 0.3), "woda", rot=(4, 0, 0))
        s.blok("Próg", (mx, 32.4, mz - 2.0), (13.0, 1.2, 6.0), "kamien_lochu", "Slate")
        s.blok("Woda na grani", (mx, 32.6, mz - 9.0), (9.0, 0.2, 14.0), "woda")
    with s.grupa("Ostepy/Lokacje/SzumiacyProg"), s.cechy(kolizja=False, cien=False):
        for k in range(5):
            s.kula("Mgiełka", (mx + rnd.uniform(-7, 7), rnd.uniform(1.5, 4.0), mz + rnd.uniform(4, 10)), rnd.uniform(4, 6.5), "biel",
                   alfa=0.35)
        # tęcza: trzy łuki z czterech odcinków nad misą
        for j, kol in enumerate(("czerwien", "zloto", "dach_twierdza")):
            r = 16.0 - 1.2 * j
            pts = [(-r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in (8, 50, 90, 130, 172)]
            for (a0, b0), (a1, b1) in zip(pts, pts[1:]):
                s.belka("Tęcza", (mx + a0 + 4, 5.0 + b0, mz + 16.0), (mx + a1 + 4, 5.0 + b1, mz + 16.0), 1.1, kol, "SmoothPlastic", 0.5)
        s.blok("Klocek w wodzie", (mx + 4.0, 0.7, mz + 14.0), (2.0, 1.0, 2.0), "dach_twierdza", rot=(10, 30, 8))
    G.zajmij(mx, mz + 14, 16)


def wrota_bagna(s, G, rnd, L):
    """Brama z omszałych pali w przerwie Muru Pni, spięta łańcuchem z kłódką; za nią mgła z białych kul (zapowiedź
    drugiego biomu, D-061; wybór dla ludzi nr 5)."""
    x, z = L["x"], L["z"]
    with s.grupa("Ostepy/Lokacje/WrotaBagna"), s.uklad(pos=(x, 0, z), obrot=(0, 90, 0)):
        for xx in (-7.5, 7.5):
            s.walec("Pal", (xx, 7.5, 0), 1.4, 16.0, "drewno_ciemne", "Wood", os="y", rot=(0, 0, -xx * 0.8))
            with s.cechy(kolizja=False):
                s.walec("Pal mech", (xx - xx * 0.12, 15.8, 0), 1.7, 1.0, "mech", os="y")
        s.belka("Belka bramy", (-9.5, 14.0, 0), (9.5, 15.2, 0), 1.4, "drewno", "Wood")
        with s.cechy(kolizja=False):
            for k in range(5):
                s.blok("Łańcuch", (-5.6 + 2.8 * k, 7.0 - 0.8 * math.sin(k * 0.8), 0), (2.0, 0.6, 0.6), "metal_ciemny",
                       rot=(0 if k % 2 else 90, 0, 6 * (k - 2)))
            s.blok("Kłódka", (0, 5.6, 0.3), (2.2, 2.4, 0.9), "zloto")
            s.blok("Kłódka dziurka", (0, 5.3, 0.8), (0.5, 1.0, 0.1), "tusz")
        with s.cechy(kolizja=False, cien=False):
            for k in range(6):
                s.kula("Mgła bagna", (rnd.uniform(-14, 14), rnd.uniform(2, 7), rnd.uniform(-30, -12)), rnd.uniform(7, 12), "biel", alfa=0.3)
            s.blok("Ślad bagna", (0, 0.07, -20.0), (30.0, 0.2, 26.0), "lisc_ciemny")
    G.zajmij(x, z, 12)


LOKACJE = {"wilcza_skala": wilcza_skala, "jezynowy_labirynt": jezynowy_labirynt, "szumiacy_prog": szumiacy_prog,
           "wrota_bagna": wrota_bagna}
