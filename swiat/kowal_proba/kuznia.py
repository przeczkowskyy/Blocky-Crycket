# -*- coding: utf-8 -*-
"""Kuźnia z klocków (próba D-102) — scena biblioteki v2 (swiat/biblioteka/scena.py), ta sama dla Studio (zbuduj.py),
Blendera (tools/blender/klocki.py, podglądy) i panelu. Własny projekt w stylu bazaru (paleta Krzywego Miasteczka).

Układ lokalny kuźni: (0, 0, 0) = środek obrysu na poziomie bruku, FRONT (strona gracza) = +Z, szerokość wzdłuż X.
W bazarze kuźnia stoi frontem ku uliczce i zbrojowni (ry z ustawień). Elementy: kamienna podłoga, palenisko z żarem,
okapem i kominem, miech, kowadło na pniu z rozżarzoną sztabą (tam trafia młot kowala — klip „kucie”), kadź z wodą,
stojak z bronią i tarczą, kupka złomu (materiały z rozbiórki), daszek na słupach z falbaną w kolorach zbrojowni
i szyld „KUŹNIA” (napis dokłada Studio — SurfaceGui na części „Szyld”). Części nazwane „Żar” dostają w Studio
światło i ogień, „Sztaba” — iskry.
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biblioteka.scena import Scena  # noqa: E402
from swiat.krzywe_miasteczko.paleta import PALETA  # noqa: E402

KOLORY = dict(PALETA)
KOLORY.update({
    "wegiel": "2B2522", "zar_zolty": "FFC34A", "cegla": "A04E2C", "cegla_ciemna": "7C3A21", "skora_miecha": "8A5A2C",
    "stal": "AEB8C6", "stal_ciemna": "566070", "sadza": "3A3330", "podloga": "8C7B6B", "podloga_jasna": "A69584",
})

PODLOGA = 0.35          # wierzch kamiennej podłogi nad brukiem (kowal stoi na niej)


def buduj(s):
    """Wszystkie części kuźni w bieżącym układzie sceny (lokalny układ kuźni)."""
    with s.grupa("Kuznia/Podloga"):
        s.blok("Podłoga", (0, PODLOGA / 2, 0), (9.0, PODLOGA, 8.5), "podloga", "Slate")
        with s.cechy(cien=False):
            for i, (x, z, kol) in enumerate(((-3.0, -2.6, "podloga_jasna"), (1.6, -2.9, "kamien_cokol"),
                                             (-1.2, 2.9, "kamien_cokol"), (3.2, 1.4, "podloga_jasna"),
                                             (0.3, 0.2, "podloga_jasna"))):
                s.blok("Płyta", (x, PODLOGA + 0.03, z), (2.2, 0.06, 1.8), kol, "Slate", rot=(0, (i * 13) % 20 - 10, 0))
        s.blok("Obrzeże przód", (0, 0.2, 4.2), (9.0, 0.4, 0.2), "kamien_cokol", "Slate")

    # --- palenisko z żarem, okap i komin (tył, po lewej patrząc od gracza: −X)
    with s.grupa("Kuznia/Palenisko"):
        hx, hz = -2.6, -2.45
        s.blok("Palenisko", (hx, PODLOGA + 1.1, hz), (3.4, 2.2, 2.6), "cegla", "Brick")
        s.blok("Palenisko wieniec", (hx, PODLOGA + 2.3, hz), (3.6, 0.2, 2.8), "kamien_cokol", "Slate")
        s.blok("Wnęka", (hx, PODLOGA + 0.75, hz + 1.31), (2.0, 0.9, 0.06), "wegiel")
        for dx in (-1.55, 1.55):
            s.blok("Rant", (hx + dx, PODLOGA + 2.55, hz), (0.3, 0.3, 2.6), "kamien_cokol", "Slate")
        s.blok("Rant tył", (hx, PODLOGA + 2.55, hz - 1.15), (2.8, 0.3, 0.3), "kamien_cokol", "Slate")
        with s.cechy(kolizja=False):
            for i, (dx, dz) in enumerate(((-0.6, -0.3), (0.5, 0.2), (0.0, -0.6), (-0.3, 0.5), (0.7, -0.5))):
                s.blok("Węgiel", (hx + dx, PODLOGA + 2.5, hz + dz), (0.7, 0.3, 0.6), "wegiel", rot=(0, i * 23, 0))
            s.blok("Żar", (hx, PODLOGA + 2.62, hz), (1.4, 0.18, 1.2), "neon_ogien", "Neon")
            s.blok("Żar jasny", (hx + 0.3, PODLOGA + 2.7, hz + 0.1), (0.6, 0.12, 0.5), "zar_zolty", "Neon")
            s.klin("Płomień", (hx - 0.2, PODLOGA + 3.05, hz), (0.4, 0.7, 0.4), "zar_zolty", "Neon", rot=(0, 30, 0))
            s.klin("Płomień", (hx + 0.35, PODLOGA + 2.95, hz - 0.2), (0.35, 0.5, 0.35), "neon_ogien", "Neon",
                   rot=(0, -60, 0))
            # okap na dwóch wspornikach i komin nad dachem
            for dx in (-1.4, 1.4):
                s.blok("Wspornik okapu", (hx + dx, PODLOGA + 3.45, hz - 1.0), (0.3, 1.9, 0.3), "metal_ciemny")
            s.blok("Okap", (hx, PODLOGA + 4.55, hz - 0.2), (3.6, 0.55, 2.6), "cegla_ciemna", "Brick")
            s.blok("Okap środek", (hx, PODLOGA + 5.1, hz - 0.35), (2.6, 0.55, 1.9), "cegla", "Brick")
        s.blok("Komin", (hx, PODLOGA + 8.0, hz - 0.45), (1.6, 5.4, 1.5), "cegla", "Brick")
        with s.cechy(kolizja=False):
            s.blok("Komin czapa", (hx, PODLOGA + 10.85, hz - 0.45), (2.0, 0.35, 1.9), "kamien_cokol", "Slate")
            s.blok("Sadza", (hx, PODLOGA + 11.06, hz - 0.45), (1.2, 0.08, 1.1), "sadza")

    # --- miech przy palenisku (dysza w stronę żaru)
    with s.grupa("Kuznia/Miech"):
        mx, mz = -3.55, -0.3
        s.blok("Kozioł miecha", (mx, PODLOGA + 0.45, mz), (1.0, 0.9, 1.6), "drewno_ciemne", "Wood")
        with s.cechy(kolizja=False):
            with s.uklad(pos=(mx, PODLOGA + 1.25, mz), obrot=(0, -20, 6)):
                s.blok("Miech deska", (0, 0.32, 0), (1.3, 0.12, 2.0), "drewno", "Wood")
                s.blok("Miech deska", (0, -0.32, 0), (1.3, 0.12, 2.0), "drewno", "Wood")
                s.blok("Miech skóra", (0, 0, 0.1), (1.15, 0.55, 1.7), "skora_miecha", "Fabric")
                s.blok("Miech fałda", (0, 0, 0.1), (1.22, 0.12, 1.75), "drewno_ciemne", "Fabric")
                s.walec("Miech dysza", (0, 0, -1.25), 0.16, 0.8, "metal_ciemny", "Metal", os="z")
                s.blok("Miech rączka", (0, 0.42, 1.25), (0.9, 0.14, 0.2), "drewno_ciemne", "Wood")
                s.blok("Miech drążek", (0, 0.9, 1.05), (0.14, 0.9, 0.14), "drewno_ciemne", "Wood", rot=(-20, 0, 0))

    # --- kowadło na pniu (blat ok. 2,9 nad brukiem = 2,58 nad stopami kowala) i rozżarzona sztaba
    with s.grupa("Kuznia/Kowadlo"):
        ax, az = 0.05, 1.45
        s.walec("Pień", (ax, PODLOGA + 0.79, az), 0.8, 1.58, "drewno", "Wood", os="y")
        with s.cechy(kolizja=False):
            s.walec("Pień obręcz", (ax, PODLOGA + 1.35, az), 0.83, 0.14, "metal_ciemny", "Metal", os="y")
        s.blok("Kowadło stopa", (ax, PODLOGA + 1.78, az), (1.6, 0.4, 1.1), "metal_ciemny", "Metal")
        s.blok("Kowadło", (ax, PODLOGA + 2.28, az), (3.0, 0.6, 1.3), "metal_ciemny", "Metal")
        with s.cechy(kolizja=False):
            s.blok("Kowadło blat", (ax, PODLOGA + 2.6, az), (3.02, 0.06, 1.32), "stal", "Metal")
            s.klin("Kowadło róg", (ax + 2.05, PODLOGA + 2.36, az), (1.3, 0.5, 1.1), "metal_ciemny", "Metal",
                   rot=(0, -90, 0))
            s.blok("Kowadło rant", (ax, PODLOGA + 1.99, az), (3.06, 0.08, 1.36), "tusz")
            with s.cechy(cien=False):
                s.blok("Sztaba", (ax - 0.05, PODLOGA + 2.72, az - 0.05), (2.0, 0.18, 0.3), "neon_ogien", "Neon",
                       rot=(0, 4, 0))
            # kupka złomu przy pniu — materiały z rozbiórki
            for i, (dx, dz, kol, r) in enumerate(((1.4, 0.6, "stal_ciemna", 20), (1.8, 0.1, "stal", -15),
                                                  (1.1, 1.0, "drewno_ciemne", 40), (1.6, 0.9, "metal_ciemny", 70))):
                s.blok("Złom", (ax + dx, PODLOGA + 0.15 + 0.08 * i, az + dz + 0.6), (0.7, 0.18, 0.35), kol, "Metal",
                       rot=(0, r, 8 * (i % 2)))
            s.blok("Złom hełm", (ax + 1.5, PODLOGA + 0.35, az + 1.55), (0.6, 0.45, 0.6), "stal_ciemna", "Metal",
                   rot=(10, 30, 0))

    # --- kadź z wodą i szczypce
    with s.grupa("Kuznia/Kadz"):
        kx, kz = -2.9, 2.35
        s.walec("Kadź", (kx, PODLOGA + 0.6, kz), 0.95, 1.2, "drewno", "Wood", os="y")
        with s.cechy(kolizja=False):
            for y in (0.25, 0.95):
                s.walec("Kadź obręcz", (kx, PODLOGA + y, kz), 0.98, 0.12, "metal_ciemny", "Metal", os="y")
            with s.cechy(cien=False):
                s.walec("Woda", (kx, PODLOGA + 1.12, kz), 0.82, 0.06, "woda", "Glass", os="y")
            s.blok("Szczypce", (kx + 0.7, PODLOGA + 1.0, kz - 0.2), (0.1, 1.6, 0.1), "metal_ciemny", "Metal",
                   rot=(0, 0, -18))
            s.blok("Szczypce", (kx + 0.82, PODLOGA + 1.0, kz - 0.2), (0.1, 1.6, 0.1), "metal_ciemny", "Metal",
                   rot=(0, 0, -24))

    # --- stojak z bronią (tył po prawej) i tarcza na ścianie stojaka
    with s.grupa("Kuznia/Stojak"):
        rz = -3.55
        for x in (1.3, 4.1):
            s.blok("Stojak słup", (x, PODLOGA + 2.1, rz), (0.3, 4.2, 0.3), "drewno_ciemne", "Wood")
        with s.cechy(kolizja=False):
            for y in (1.4, 3.6):
                s.blok("Stojak belka", (2.7, PODLOGA + y, rz), (3.2, 0.25, 0.35), "drewno", "Wood")
            s.blok("Stojak deska", (2.7, PODLOGA + 2.5, rz - 0.22), (3.0, 2.0, 0.12), "drewno_ciemne", "WoodPlanks")
            for i, x in enumerate((1.8, 2.5, 3.2)):
                with s.uklad(pos=(x, PODLOGA + 0.5, rz + 0.25), obrot=(0, 0, (-5, 4, -3)[i])):
                    s.blok("Miecz ostrze", (0, 1.8, 0), (0.32, 2.8, 0.1), "stal", "Metal")
                    s.blok("Miecz obrys", (0, 1.78, -0.05), (0.44, 2.95, 0.06), "tusz")
                    s.blok("Miecz jelec", (0, 0.3, 0.02), (0.9, 0.18, 0.2), "zloto", "Metal")
                    s.blok("Miecz rękojeść", (0, -0.05, 0.02), (0.18, 0.6, 0.18), "drewno", "Wood")
            with s.uklad(pos=(3.85, PODLOGA + 0.4, rz + 0.3), obrot=(0, 0, 6)):
                s.blok("Topór trzonek", (0, 1.4, 0), (0.18, 2.8, 0.18), "drewno", "Wood")
                s.klin("Topór ostrze", (-0.35, 2.55, 0), (0.12, 0.8, 0.6), "stal", "Metal", rot=(0, 90, 0))
            s.walec("Tarcza", (2.7, PODLOGA + 4.85, rz - 0.1), 0.95, 0.2, "dach_zbrojownia", os="z")
            s.walec("Tarcza rant", (2.7, PODLOGA + 4.85, rz - 0.05), 1.02, 0.12, "zloto", "Metal", os="z")
            s.blok("Tarcza guz", (2.7, PODLOGA + 4.85, rz + 0.08), (0.36, 0.36, 0.16), "zloto", "Metal", rot=(0, 0, 45))

    # --- daszek na czterech słupach z falbaną w kolorach zbrojowni, szyld na przedniej belce
    with s.grupa("Kuznia/Daszek"):
        for x, z in ((-4.25, -4.0), (4.25, -4.0), (-4.25, 0.9), (4.25, 0.9)):
            s.blok("Słup", (x, PODLOGA + 3.6, z), (0.4, 7.2, 0.4), "drewno_ciemne", "Wood")
        with s.cechy(kolizja=False):
            s.blok("Belka przód", (0, PODLOGA + 7.0, 0.9), (9.2, 0.4, 0.45), "drewno_ciemne", "Wood")
            s.blok("Belka tył", (0, PODLOGA + 8.0, -4.0), (9.2, 0.4, 0.45), "drewno_ciemne", "Wood")
            for i in range(5):
                z = -3.95 + i * 1.3
                y = PODLOGA + 8.35 - i * 0.24
                s.blok("Dach deska", (0, y, z), (9.2, 0.22, 1.42), "dach_zbrojownia", "WoodPlanks", rot=(-10, 0, 0))
            s.blok("Dach kalenica", (0, PODLOGA + 8.55, -4.15), (9.3, 0.3, 0.4), "zloto", "Metal")
            for i in range(9):
                x = -4.0 + i * 1.0
                s.blok("Falbana", (x, PODLOGA + 6.65, 1.25), (1.0, 0.7, 0.08), "dach_zbrojownia" if i % 2 == 0 else "biel",
                       "Fabric")
            for x in (0.25, 2.95):
                s.blok("Łańcuszek", (x, PODLOGA + 6.35, 1.0), (0.08, 0.9, 0.08), "metal_ciemny", "Metal")
            s.blok("Szyld", (1.6, PODLOGA + 5.45, 1.0), (3.6, 1.15, 0.16), "drewno_jasne", "Wood")
            s.blok("Szyld rama", (1.6, PODLOGA + 5.45, 0.94), (3.8, 1.35, 0.06), "drewno_ciemne", "Wood")
            s.blok("Szyld kowadełko", (1.6, PODLOGA + 6.25, 1.0), (0.8, 0.3, 0.2), "metal_ciemny", "Metal")


def scena(srodek, ry, korzen="Workspace/KowalProba"):
    """Scena kuźni w świecie: srodek = (x, y, z) świata (środek obrysu na bruku), ry = obrót frontu w stopniach."""
    s = Scena(korzen, paleta=KOLORY)
    with s.uklad(pos=srodek, obrot=(0, ry, 0)):
        buduj(s)
    return s
