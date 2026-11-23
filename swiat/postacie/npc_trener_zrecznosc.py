# -*- coding: utf-8 -*-
"""TRENER ZRĘCZNOŚCI — drwal przy mini-grze Zręczności („Kłody”) w Training Center (NPC, D-109).
Żylasty drwal: czerwona wełniana czapka z pomponem, krótka brązowa broda, koszula w czerwono-czarną kratę z
podwiniętymi rękawami, szelki, granatowe spodnie, ciężkie brązowe buty; w prawej dłoni siekiera głowicą w dół.

    python -B swiat/postacie/przebuduj.py npc_trener_zrecznosc --bez-filmow

Klipy: spoczynek, powitanie (macha lewą ręką), gest (zamach siekierą nad bark i cięcie w dół przed siebie).
Status: propozycja (własny projekt, nie kanon). Ciało i klipy wspólne: npc_wspolne.py.
"""
from swiat.postacie import npc_wspolne as N

ID = "npc_trener_zrecznosc"
PALETA = {"wlos": "6B4226", "czapka": "C0392B", "czapka_cien": "962A20", "pompon": "F4F0E6", "krata": "C0392B",
          "krata_cien": "2A2530", "szelki": "5A3418", "spodnie": "264653", "but": "5A3418", "but_jasny": "7E4E26",
          "trzonek": "B57E47", "ostrze": "C9CED6", "ostrze_cien": "5B6470"}
BAZA = {"RightUpperArm": (-6, 0, -8), "RightLowerArm": (-6, 0, 0), "LeftUpperArm": (6, 0, 32), "LeftLowerArm": (0, 0, -68),
        "LeftHand": (0, 0, -8)}


def _gest(p, start):
    k = p.klip("gest", 50, petla=False)
    k.poza(0, N._zera(start, ("RightHand",)))
    gora = {"RightUpperArm": (-165, 0, 6), "RightLowerArm": (-35, 0, 0), "RightHand": (10, 0, 0),
            "UpperTorso": (-8, -8, 0), "Head": (-6, 0, 0)}
    k.poza(14, gora)
    k.poza(20, {**gora, "RightUpperArm": (-174, 0, 6)}, wyg="liniowo")
    ciecie = {"RightUpperArm": (-62, 0, 12), "RightLowerArm": (-30, 0, 0), "RightHand": (40, 0, 0),
              "UpperTorso": (12, 5, 0), "Head": (8, 0, 0)}
    k.poza(25, ciecie)
    k.poza(32, {**ciecie, "RightUpperArm": (-56, 0, 12), "UpperTorso": (10, 5, 0)})
    k.poza(50, N._zera(start, ("RightHand",)))


def zbuduj():
    p = N.ludzik(ID, "Trener Zręczności", PALETA,
                 {"glowa": "skora", "tulow": "krata", "pas": "spodnie", "ramiona": "krata", "LeftLowerArm": "skora",
                  "RightLowerArm": "skora", "dlonie": "skora", "nogi": "spodnie", "stopy": "but"})
    N.twarz(p, oczy="waskie", brew="wlos", brew_kat=6, usta="usmiech", nos=0.34)
    N.broda(p, "wlos", dl=0.25)
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        p.blok("Czapka", (0, h / 2 + 0.14, -0.02), (w + 0.12, 0.5, d + 0.1), "czapka", "matowy", faza=0.14)
        p.blok("Czapka otok", (0, h / 2 - 0.16, -0.02), (w + 0.2, 0.26, d + 0.18), "czapka_cien", "matowy", faza=0.05)
        p.blok("Pompon", (0.1, h / 2 + 0.5, -0.1), (0.36, 0.36, 0.36), "pompon", "matowy", faza=0.1)
        for zn in (1, -1):
            p.blok("Wlosy bok %d" % zn, (zn * (w / 2 + 0.04), -0.1, -0.25), (0.12, 0.5, d - 0.45), "wlos", "matowy")
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        for i, x in enumerate((-0.7, 0.0, 0.7)):
            p.blok("Krata pion %d" % i, (x, 0, z + 0.02), (0.14, h - 0.04, 0.04), "krata_cien", "matowy", faza=0.0)
        for i, y in enumerate((-0.45, 0.05, 0.5)):
            p.blok("Krata poziom %d" % i, (0, y, z + 0.025), (w - 0.04, 0.12, 0.04), "krata_cien", "matowy", faza=0.0)
        p.blok("Krata tyl", (0, 0.05, -z - 0.02), (w - 0.04, 0.12, 0.04), "krata_cien", "matowy", faza=0.0)
        for zn in (1, -1):
            s = "L" if zn > 0 else "P"
            p.blok("Szelka " + s, (zn * 0.5, 0.0, z + 0.06), (0.2, h, 0.06), "szelki", "matowy", faza=0.0)
            p.blok("Szelka tyl " + s, (zn * 0.5, 0.0, -z - 0.05), (0.2, h, 0.06), "szelki", "matowy", faza=0.0)
            p.blok("Szelka bark " + s, (zn * 0.5, h / 2 + 0.03, 0), (0.2, 0.08, d + 0.1), "szelki", "matowy", faza=0.0)
    N.rekawy(p, "krata", mankiet="krata_cien")
    N.pas(p, "szelki", klamra="ostrze")
    N.buty(p, "but", jasny="but_jasny", cholewa=0.26)
    N.piesc(p, "Right")
    with p.na("RightHand", od="srodek"):
        # siekiera: trzonek przedłuża rękę (−Y dłoni), głowica na końcu, ostrze ku przodowi (+Z)
        p.blok("Trzonek", (0, -0.85, 0), (0.18, 1.7, 0.22), "trzonek", "matowy", faza=0.04)
        p.blok("Glowica", (0, -1.5, 0.12), (0.2, 0.5, 0.6), "ostrze_cien", "metal", faza=0.04)
        p.klin("Ostrze", (0, -1.5, 0.56), (0.2, 0.7, 0.4), "ostrze", "metal", rot=(0, 180, 0), faza=0.0)
        p.blok("Obuch", (0, -1.5, -0.2), (0.24, 0.36, 0.14), "ostrze_cien", "metal", faza=0.03)
    N.klipy(p, BAZA, wolna="Left", gest=_gest)
    p.ustaw_poze_renderu("gest", 20)
    return [p]


SLABOSCI = N.SLABOSCI + [
    "Cięcie siekierą kończy się ok. 2 studów przed postacią na wysokości kolan — pieniek stanowiska trzeba postawić "
    "tam albo dalej, żeby ostrze w niego nie wchodziło.",
]
