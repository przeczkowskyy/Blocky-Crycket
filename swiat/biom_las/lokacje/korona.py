# -*- coding: utf-8 -*-
"""Lokacje Korony Gaju: Rozstaj pod Sową, Kamienny Krąg Korony (arena strażnika), Ławka z Widokiem."""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_TU)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import rosliny, skaly  # noqa: E402
from swiat.biom_las.lokacje import wspolne  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402


def rozstaj_pod_sowa(s, G, rnd, L):
    """Słup z drewnianą sową, która obraca głowę ku drogom, i pięć ramion-rekwizytów (galareta, kapelusz, wilcze ucho,
    maczuga, kryształ) wskazujących podbiomy."""
    x, z = L["x"], L["z"]
    with s.grupa("Korona/Lokacje/RozstajPodSowa"), s.uklad(pos=(x, 0, z)):
        s.walec("Słup", (0, 6.0, 0), 0.8, 12.0, "drewno", "Wood", os="y", rot=(0, 0, 4))
        with s.cechy(kolizja=False):
            with s.uklad(pos=(0.6, 12.0, 0), obrot=(0, 25, 0)):
                s.blok("Sowa", (0, 2.0, 0), (3.2, 4.0, 2.8), "drewno_jasne", rot=(0, 0, 4))
                s.blok("Sowa brzuch", (0, 1.7, 1.45), (2.2, 2.6, 0.2), "biel")
                with s.uklad(pos=(0, 4.9, 0), obrot=(0, 35, -6)):
                    s.blok("Sowa głowa", (0, 0, 0), (3.6, 2.6, 3.0), "drewno_jasne")
                    for xx in (-0.85, 0.85):
                        s.walec("Sowa oko", (xx, 0.2, 1.55), 0.75, 0.2, "biel", os="z")
                        s.walec("Sowa źrenica", (xx, 0.2, 1.7), 0.35, 0.15, "tusz", os="z")
                        s.naroznik("Sowa ucho", (xx * 1.4, 1.8, 0), (0.9, 1.4, 0.9), "drewno", rot=(0, 90 if xx > 0 else 0, 0))
                    s.naroznik("Sowa dziób", (0, -0.4, 1.7), (0.6, 0.8, 0.6), "zloto", rot=(0, 45, 180))
        cele = [((200, 400), "laka"), ((-290, 270), "kapeluszowo"), ((-300, -50), "ostepy"), ((250, -195), "wawoz"),
                ((0, -385), "korona")]
        for i, ((tx, tz), pb) in enumerate(cele):
            ry = math.degrees(math.atan2(tx - x, tz - z))
            with s.uklad(pos=(0, 10.2 - 1.6 * i, 0), obrot=(0, ry, rnd.choice((-5, 5)))), s.cechy(kolizja=False):
                s.blok("Ramię", (0, 0, 2.6), (0.5, 0.8, 4.6), "drewno_jasne")
                wspolne.rekwizyt(s, wspolne.REKWIZYT_RAMIENIA[pb], (0, 1.1, 4.8))
        wspolne.lampion(s, (2.5, 0, 2.0), 5.0)
    G.zajmij(x, z, 8)


def kamienny_krag(s, G, rnd, L):
    """Siedem pochylonych menhirów wokół kamiennego filara z zieloną iglicą kryształu (razem ok. 63, czubek ok. 95 n.p.m.) — uśpiony Strażnik Gaju
    rozsypany na kamienie. Wejście serpentyną od południa, Traktem od wschodu i Granią od zachodu."""
    x, z = L["x"], L["z"]
    y = 32.0
    with s.grupa("Punkty/KamiennyKrag"), s.uklad(pos=(x, y, z)):
        for k in range(7):
            a = math.radians(k * 360 / 7 + 8)
            mx, mz = 23.0 * math.cos(a), 23.0 * math.sin(a)
            if (mz > 18 and abs(mx) < 10) or (mx > 18 and abs(mz) < 9) or (mx < -18 and abs(mz) < 9):
                a += math.radians(20)
                mx, mz = 23.0 * math.cos(a), 23.0 * math.sin(a)
            h = rnd.uniform(12, 17)
            skaly.menhir(s, rnd, (mx, 0, mz), h, math.degrees(math.atan2(mx, mz)), "dach_dom_lupek", przechyl=10)
            with s.cechy(kolizja=False, cien=False):           # czapa mchu: menhiry nie zlewają się z jasną posadzką
                s.blok("Menhir mech", (mx, h + 0.2, mz), (3.0, 0.7, 2.4), "mech", rot=(0, math.degrees(math.atan2(mx, mz)), 0))
        # po przeglądzie: kryształ był za mały (czubek ok. 58 n.p.m.) — z Rozstaju i z Łąki go nie było widać.
        # Teraz filar z łupku i iglica kryształu do ok. 95 n.p.m. (prawie jak Ukłon): zielony znak Korony widoczny nad brzózkami z całego lasu.
        for i, (a, h, rz) in enumerate(((8.0, 7.0, 0), (6.6, 7.0, 4), (5.2, 6.0, -5))):
            s.blok("Filar", (0, 3.5 + 7.0 * i - 0.5 * i, 0), (a, h + 0.6, a), cien(s, "dach_dom_lupek", 0.9 + 0.08 * i), "Slate",
                   rot=(0, 20 * i, rz))
        with s.cechy(kolizja=False):
            s.blok("Kryształ", (0.3, 36.0, 0), (6.0, 34.0, 6.0), "neon_portal", "Neon", rot=(5, 45, 4))
            s.naroznik("Kryształ czubek", (1.6, 57.5, 0), (5.8, 10.0, 5.8), "neon_portal", "Neon", rot=(0, 45, 4))
            s.blok("Kryształ odłamek", (4.6, 27.0, 2.0), (3.0, 16.0, 3.0), "neon_portal", "Neon", rot=(18, 10, -24))
            s.blok("Kryształ odłamek", (-4.0, 25.0, -1.8), (2.6, 12.0, 2.6), "neon_portal", "Neon", rot=(-16, 30, 22))
    with s.grupa("Korona/Lokacje/KamiennyKrag"), s.uklad(pos=(x, y, z)):
        with s.cechy(kolizja=False, cien=False):
            s.walec("Krąg posadzka", (0, 0.1, 0), 27.0, 0.2, "kamien_cieply", os="y")
            s.walec("Krąg posadzka środek", (0, 0.16, 0), 9.0, 0.2, cien(s, "kamien_cieply", 0.85), os="y")
    wspolne.ognisko(s, rnd, (-8.0, y, -364.0))
    G.zajmij(x, z, 30)


def lawka_z_widokiem(s, G, rnd, L):
    """Krzywa ławka z dwóch pniaków i deski oraz luneta na trójnogu, wycelowana w sylwetkę miasteczka na horyzoncie."""
    x, z = L["x"], L["z"]
    y = G.T.H(x, z)
    with s.grupa("Korona/Lokacje/LawkaZWidokiem"), s.uklad(pos=(x, y, z), obrot=(0, 180, 0)):
        rosliny.pniak(s, rnd, (-2.6, 0, 0), 0.8, 0)
        rosliny.pniak(s, rnd, (2.6, 0, 0), 0.7, 40)
        s.blok("Ławka deska", (0, 2.0, 0), (7.4, 0.5, 2.2), "drewno_jasne", "WoodPlanks", rot=(0, 0, 3))
        with s.cechy(kolizja=False):
            for a in (0, 120, 240):
                aa = math.radians(a)
                s.belka("Trójnóg", (5.5 + 1.4 * math.cos(aa), 0, 1.5 + 1.4 * math.sin(aa)), (5.5, 3.6, 1.5), 0.3, "drewno_ciemne", "Wood")
            s.walec("Luneta", (5.5, 4.0, 2.3), 0.5, 3.4, "metal_ciemny", os="z", rot=(-8, 0, 0))
            s.walec("Luneta szkło", (5.5, 4.25, 4.0), 0.55, 0.3, "zloto", os="z", rot=(-8, 0, 0))
    # po przeglądzie: korytarz widoku bez drzew dawał pusty, ciemny pierwszy plan — niskie kwiaty i dwa płaskie głazy
    # po bokach korytarza (nic nie wystaje ponad ok. 3, więc widok na Ukłon i las zostaje)
    with s.grupa("Korona/Lokacje/LawkaZWidokiem"):
        for t, bok in ((14, -9), (20, 10), (27, -12), (33, 8), (40, -6), (46, 13), (24, -2), (37, 1)):
            px, pz = x - 0.155 * t + bok * 0.99, z + 0.99 * t + bok * 0.155
            py = G.T.H(px, pz)
            if abs(py - y) > 0.05:
                continue
            rosliny.kwiaty(s, rnd, (px, py, pz), rnd.choice((("biel", "zloto"), ("biel", "dach_sklep"), ("zloto", "czerwien"))))
        for t, bok, k in ((18, -15, 0.9), (31, 15, 0.7)):
            px, pz = x - 0.155 * t + bok * 0.99, z + 0.99 * t + bok * 0.155
            if abs(G.T.H(px, pz) - y) < 0.05:
                skaly.glaz(s, rnd, (px, y, pz), k, rnd.uniform(0, 90), "kamien_cieply", mech=True)
    G.zajmij(x, z, 6)


LOKACJE = {"rozstaj_pod_sowa": rozstaj_pod_sowa, "kamienny_krag": kamienny_krag, "lawka_z_widokiem": lawka_z_widokiem}
