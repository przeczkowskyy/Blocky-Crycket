# -*- coding: utf-8 -*-
"""TRENER SIŁY — siłacz przy mini-grze Siły („Rozbijanie”) w Training Center (NPC, D-109).
Łysy siłacz z podkręconym czarnym wąsem: granatowy trykot zapaśniczy z żółtym pasem na piersi (bez czerwieni i bieli —
wąsacz w czerwieni za bardzo przypominałby znaną postać z cudzych gier), szeroki pas mistrza ze złotą klamrą, gołe grube ramiona w skórzanych karwaszach, czarne buty; w prawej dłoni żelazna hantla.

    python -B swiat/postacie/przebuduj.py npc_trener_sila --bez-filmow

Klipy: spoczynek, powitanie (macha lewą ręką), gest (wyciska hantlę nad głowę i stęka — dwa powtórzenia),
akcja (jeden rzut prawą ręką — krótki ruch dla mini-gry Siły).
Status: propozycja (własny projekt, nie kanon). Ciało i klipy wspólne: npc_wspolne.py.
"""
from swiat.postacie import npc_wspolne as N

ID = "npc_trener_sila"
PALETA = {"was": "1F1B24", "trykot": "27406B", "trykot_cien": "1B2E50", "pas_bialy": "F2B630", "pas_mistrza": "3A2A1C",
          "karwasz": "6B4226", "but": "22202A", "zelazo": "4A5368", "zelazo_jasne": "8E98A8"}
BAZA = {"RightUpperArm": (-6, 0, -12), "RightLowerArm": (-8, 0, 0), "LeftUpperArm": (6, 0, 32), "LeftLowerArm": (0, 0, -68),
        "LeftHand": (0, 0, -8)}


def _gest(p, start):
    k = p.klip("gest", 60, petla=False)
    k.poza(0, start)
    bark = {"RightUpperArm": (-20, 0, -80), "RightLowerArm": (0, 0, -100), "Head": (0, -8, 0), "UpperTorso": (0, 0, -3)}
    gora = {"RightUpperArm": (-8, 0, -168), "RightLowerArm": (0, 0, -6), "Head": (-10, -6, 0), "UpperTorso": (-3, 0, 3)}
    k.poza(10, bark)
    k.poza(20, gora)
    k.poza(30, bark)
    k.poza(40, gora)
    k.poza(48, bark)
    k.poza(60, start)


def _akcja(p, start):
    """Jeden rzut prawą ręką (ruch mini-gry Siły): zamach w tył ze skrętem tułowia, wyrzut przed siebie, powrót.
    18 klatek; czas w grze ustawia swiat/npc_gra (trenerzy.akcja_s)."""
    k = p.klip("akcja", 18, petla=False)
    k.poza(0, start)
    k.poza(5, {"RightUpperArm": (42, 0, -18), "RightLowerArm": (-62, 0, 0), "UpperTorso": (-3, -14, 0), "Head": (0, 10, 0)})
    k.poza(9, {"RightUpperArm": (-98, 0, -4), "RightLowerArm": (-10, 0, 0), "UpperTorso": (7, 12, 0), "Head": (2, -8, 0)},
           wyg="liniowo")
    k.poza(12, {"RightUpperArm": (-74, 0, 4), "RightLowerArm": (-18, 0, 0), "UpperTorso": (5, 8, 0), "Head": (2, -5, 0)})
    k.poza(18, start)


def zbuduj():
    p = N.ludzik(ID, "Trener Siły", PALETA,
                 {"glowa": "skora", "tulow": "trykot", "pas": "trykot", "ramiona": "skora", "dlonie": "skora",
                  "LeftUpperLeg": "trykot", "RightUpperLeg": "trykot", "LeftLowerLeg": "skora", "RightLowerLeg": "skora",
                  "stopy": "but"})
    N.twarz(p, oczy="duze", brew="was", brew_kat=-10, usta=None, nos=0.34)
    N.wasy(p, "was", podkrecone=True)
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        p.blok("Lysina blik", (0.3, h / 2 + 0.01, 0.15), (0.5, 0.03, 0.34), "bialy", rot=(0, 20, 0), faza=0.0)
        p.blok("Usta", (0, -0.47, d / 2 + 0.02), (0.3, 0.07, 0.05), "usta", faza=0.0)
        p.blok("Podbrodek", (0, -h / 2 + 0.06, d / 2 - 0.1), (1.0, 0.22, 0.3), "skora_cien", "matowy", faza=0.06)
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.blok("Pas trykotu", (0, 0.15, z + 0.03), (w + 0.04, 0.3, 0.06), "pas_bialy", "matowy", faza=0.0)
        p.blok("Dekolt", (0, h / 2 - 0.2, z + 0.02), (1.0, 0.42, 0.05), "skora", faza=0.0)
        p.blok("Klatka", (0, 0.42, z + 0.01), (w - 0.5, 0.3, 0.1), "skora_cien", "matowy", faza=0.04)
        for zn in (1, -1):
            s = "L" if zn > 0 else "P"
            p.blok("Ramiaczko " + s, (zn * 0.72, h / 2 - 0.18, 0), (0.34, 0.4, d + 0.06), "trykot", "matowy", faza=0.03)
            p.blok("Bark " + s, (zn * (w / 2 + 0.25), h / 2 - 0.2, 0), (0.8, 0.44, d + 0.16), "skora", faza=0.12)
    with p.na("LowerTorso", od="srodek"):
        w, h, d = p.wymiary("LowerTorso")
        p.blok("Pas mistrza", (0, 0.1, 0), (w + 0.12, 0.44, d + 0.12), "pas_mistrza", "matowy", faza=0.04)
        p.blok("Klamra mistrza", (0, 0.1, d / 2 + 0.09), (0.7, 0.52, 0.08), "zloto", "metal", faza=0.08)
        p.blok("Klamra srodek", (0, 0.1, d / 2 + 0.14), (0.3, 0.26, 0.04), "trykot", "polysk", rot=(0, 0, 45), faza=0.0)
    for s in ("Left", "Right"):
        with p.na(s + "UpperArm", od="srodek"):
            w, h, d = p.wymiary(s + "UpperArm")
            p.blok("Biceps", (0, 0.0, 0.04), (w + 0.22, h - 0.2, d + 0.22), "skora", faza=0.12)
        with p.na(s + "LowerArm", od="srodek"):
            w, h, d = p.wymiary(s + "LowerArm")
            p.blok("Karwasz", (0, -0.08, 0), (w + 0.12, h - 0.3, d + 0.12), "karwasz", "matowy", faza=0.04)
        with p.na(s + "UpperLeg", od="srodek"):
            w, h, d = p.wymiary(s + "UpperLeg")
            p.blok("Nogawka", (0, -h / 2 + 0.07, 0), (w + 0.08, 0.14, d + 0.08), "trykot_cien", "matowy")
    N.buty(p, "but", jasny="zelazo", cholewa=0.3)
    N.piesc(p, "Right")
    with p.na("RightHand", od="srodek"):
        # hantla: gryf wzdłuż osi Z dłoni (przód–tył przy zwisającej ręce), po dwa talerze na końcach
        p.blok("Gryf", (0, -0.05, 0), (0.18, 0.18, 1.7), "zelazo_jasne", "metal", faza=0.03)
        for zn in (1, -1):
            p.walec("Talerz %d" % zn, (0, -0.05, zn * 0.72), (0.9, 0.34, 0.9), "zelazo", "metal", rot=(90, 0, 0), segm=8)
            p.walec("Talerz maly %d" % zn, (0, -0.05, zn * 1.0), (0.6, 0.22, 0.6), "zelazo", "metal", rot=(90, 0, 0),
                    segm=8)
    _akcja(p, N.klipy(p, BAZA, wolna="Left", gest=_gest))
    p.ustaw_poze_renderu("gest", 20)
    return [p]


SLABOSCI = N.SLABOSCI + [
    "Hantla jest bryłą dłoni — przy wyciskaniu gryf nie obraca się w dłoni, tylko idzie za nadgarstkiem.",
]
