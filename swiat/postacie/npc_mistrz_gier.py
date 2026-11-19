# -*- coding: utf-8 -*-
"""MISTRZ GIER — prowadzi grę w kostkę przy stole w karczmie (NPC, D-109; miejsce bazaru „mistrz_gier”, D-053).
Chudy ludzik na wysokim stołku: okulary w srebrnych oprawkach, kozia bródka bez wąsów, fioletowy beret ze złotą kostką,
biała koszula, kamizelka w żółto-fioletową szachownicę, ciemne spodnie; w prawej dłoni biała kostka do gry.

    python -B swiat/postacie/przebuduj.py npc_mistrz_gier --bez-filmow

Klipy: spoczynek (siedzi, macha nogami), powitanie (macha lewą ręką), gest (potrząsa kostką i rzuca ją przed siebie).
Status: propozycja (własny projekt, nie kanon). Ciało i klipy wspólne: npc_wspolne.py.
"""
from swiat.postacie import npc_wspolne as N

ID = "npc_mistrz_gier"
PALETA = {"wlos": "4A3020", "beret": "7B4FBF", "beret_cien": "5C3A94", "koszula": "F4F0E6", "kam_a": "F2B630",
          "kam_b": "7B4FBF", "spodnie": "2E2A3A", "but": "3A2414", "kostka": "FBF7EC", "oprawka": "C9CED6"}
BAZA = {"LeftUpperArm": (-38, 0, 8), "LeftLowerArm": (-52, 0, 0), "RightUpperArm": (-42, 0, -8),
        "RightLowerArm": (-56, 0, 0)}


def _gest(p, start):
    k = p.klip("gest", 54, petla=False)
    k.poza(0, start)
    trzes = {"RightUpperArm": (-70, 0, -14), "RightLowerArm": (-95, 0, 0), "Head": (0, -10, 6), "UpperTorso": (-3, -6, 0)}
    k.poza(8, trzes)
    for f, kat in ((13, -80), (18, -104), (23, -80), (28, -104)):
        k.poza(f, {"RightLowerArm": (kat, 0, 0)})
    k.poza(28, {"RightUpperArm": (-70, 0, -14), "RightHand": (0, 0, 0), "Head": (0, -10, 6), "UpperTorso": (-3, -6, 0)})
    k.poza(36, {"RightUpperArm": (-88, 0, -4), "RightLowerArm": (-12, 0, 0), "RightHand": (-30, 0, 0),
                "Head": (10, 0, 0), "UpperTorso": (8, 0, 0)}, wyg="liniowo")
    k.poza(44, {"RightUpperArm": (-80, 0, -4), "RightLowerArm": (-20, 0, 0), "RightHand": (-20, 0, 0),
                "Head": (12, 0, 0), "UpperTorso": (7, 0, 0)})
    k.poza(54, N._zera(start, ("RightHand",)))
    k.poza(0, {"RightHand": (0, 0, 0)})


def zbuduj():
    p = N.ludzik(ID, "Mistrz gier", PALETA,
                 {"glowa": "skora", "tulow": "koszula", "pas": "spodnie", "ramiona": "koszula", "dlonie": "skora",
                  "nogi": "spodnie", "stopy": "but"})
    N.twarz(p, oczy="duze", brew="wlos", brew_kat=10, usta="usmiech")
    N.wlosy(p, "wlos", fryzura="krotkie")
    N.okulary(p, "oprawka")
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        z = d / 2
        p.blok("Brodka", (0, -h / 2 - 0.1, z - 0.02), (0.36, 0.4, 0.22), "wlos", "matowy", faza=0.06)
        with p.uklad(pos=(0.2, h / 2 + 0.42, -0.05), obrot=(0, 0, -10)):
            p.walec("Beret", (0, 0, 0), (2.0, 0.34, 1.9), "beret", "matowy", segm=8)
            p.walec("Beret otok", (0, -0.2, 0), (1.5, 0.16, 1.45), "beret_cien", "matowy", segm=8)
            p.blok("Beret ogonek", (0, 0.24, 0), (0.14, 0.2, 0.14), "beret", "matowy", faza=0.03)
            p.blok("Beret kostka", (0.6, 0.02, 0.8), (0.34, 0.34, 0.34), "zloto", "metal", rot=(20, 30, 0), faza=0.04)
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        for i, (x, y) in enumerate(((-0.52, -0.38), (0.52, -0.38), (-0.52, 0.2), (0.52, 0.2))):
            p.blok("Kamizelka %d" % i, (x, y, z + 0.04), (0.66, 0.58, 0.08), "kam_a" if i in (0, 3) else "kam_b",
                   "matowy", faza=0.0)
        p.blok("Kamizelka tyl", (0, -0.08, -z - 0.03), (w - 0.1, h - 0.3, 0.06), "kam_b", "matowy", faza=0.0)
        p.blok("Muszka", (0, h / 2 - 0.14, z + 0.07), (0.5, 0.2, 0.08), "tusz", "matowy", rot=(0, 0, 4), faza=0.03)
    N.rekawy(p, "koszula", mankiet="kam_b", dlugie=True)
    N.pas(p, "but", klamra="zloto")
    N.buty(p, "but", cholewa=0)
    N.piesc(p, "Right")
    with p.na("RightHand", od="srodek"):
        with p.uklad(pos=(0, -0.42, 0.05), obrot=(15, 25, 10)):
            p.blok("Kostka", (0, 0, 0), (0.52, 0.52, 0.52), "kostka", faza=0.07)
            for i, (x, y, zz, s) in enumerate(((0, 0, 0.27, (0.12, 0.12, 0.03)), (0.27, 0.12, 0.1, (0.03, 0.1, 0.1)),
                                               (0.27, -0.12, -0.1, (0.03, 0.1, 0.1)), (0, -0.27, 0, (0.12, 0.03, 0.12)))):
                p.blok("Oczko %d" % i, (x, y, zz), s, "tusz", faza=0.0)
    N.klipy(p, BAZA, wolna="Left", gest=_gest, siedzi=True)
    p.ustaw_poze_renderu("powitanie", 24)
    return [p]


SLABOSCI = N.SLABOSCI + [
    "Siedzi: uda w poziomie, łydki zwisają — wysokość bioder nad stołkiem ustawia gra (swiat/npc_gra, przesunięcie "
    "stanowiska); w Blenderze i na planszy siedzi w powietrzu.",
    "Kostka zostaje w dłoni także po rzucie (bryła na kości dłoni).",
]
