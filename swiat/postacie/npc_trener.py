# -*- coding: utf-8 -*-
"""TRENER — gospodarz Training Center w bazarze, zaprasza na mini-gry (NPC, D-109; miejsce bazaru „training_center”).
Barczysty: czarny płaski czub, niebieska opaska na czole, biały podkoszulek z ukośnym czerwonym pasem, gołe ramiona,
granatowe spodenki, białe buty z czerwonym paskiem, złoty gwizdek na sznurku; w lewej dłoni podkładka z listą.

    python -B swiat/postacie/przebuduj.py npc_trener --bez-filmow

Klipy: spoczynek, powitanie (macha prawą ręką), gest (napina oba bicepsy i kiwa głową — „dasz radę”).
Status: propozycja (własny projekt, nie kanon). Ciało i klipy wspólne: npc_wspolne.py.
"""
from swiat.postacie import npc_wspolne as N

ID = "npc_trener"
PALETA = {"wlos": "1F1B24", "opaska": "2C6BE0", "koszulka": "F6F2E8", "pas_koszulki": "D9422E", "spodenki": "27406B",
          "but": "F4F0E6", "gwizdek": "E8B93A", "sznurek": "2A2530", "podkladka": "9A6B3C", "kartka": "FBF7EC"}
BAZA = {"LeftUpperArm": (-16, 0, 6), "LeftLowerArm": (-72, 0, 0), "RightUpperArm": (4, 0, -30), "RightLowerArm": (0, 0, 64),
        "RightHand": (0, 0, 8)}


def _gest(p, start):
    k = p.klip("gest", 50, petla=False)
    k.poza(0, start)
    flex = {"LeftUpperArm": (0, 0, 92), "LeftLowerArm": (0, 0, 78), "RightUpperArm": (0, 0, -92),
            "RightLowerArm": (0, 0, -78), "RightHand": (0, 0, 0), "Head": (-6, 0, 0), "UpperTorso": (-5, 0, 0)}
    k.poza(12, flex)
    k.poza(19, {**flex, "LeftLowerArm": (0, 0, 96), "RightLowerArm": (0, 0, -96), "Head": (8, 0, 0)})
    k.poza(26, {**flex, "Head": (-6, 0, 0)})
    k.poza(33, {**flex, "LeftLowerArm": (0, 0, 96), "RightLowerArm": (0, 0, -96), "Head": (8, 0, 0)})
    k.poza(50, start)


def zbuduj():
    p = N.ludzik(ID, "Trener", PALETA,
                 {"glowa": "skora", "tulow": "koszulka", "pas": "spodenki", "ramiona": "skora", "dlonie": "skora",
                  "LeftUpperLeg": "spodenki", "RightUpperLeg": "spodenki", "LeftLowerLeg": "skora",
                  "RightLowerLeg": "skora", "stopy": "but"})
    N.twarz(p, oczy="duze", brew="wlos", brew_kat=-4, usta="otwarte", nos=0.32)
    N.wlosy(p, "wlos", fryzura="czub")
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        p.blok("Opaska", (0, h / 2 - 0.2, 0), (w + 0.1, 0.22, d + 0.1), "opaska", "matowy", faza=0.03)
        p.blok("Opaska wezel", (0.3, h / 2 - 0.3, -d / 2 - 0.12), (0.3, 0.4, 0.14), "opaska", "matowy", rot=(0, 0, 20))
        p.blok("Podbrodek", (0, -h / 2 + 0.06, d / 2 - 0.1), (0.9, 0.2, 0.3), "skora_cien", "matowy", faza=0.06)
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.blok("Pas koszulki", (0, 0.05, z + 0.03), (w - 0.1, 0.34, 0.06), "pas_koszulki", "matowy", rot=(0, 0, -14),
               faza=0.0)
        p.blok("Dekolt", (0, h / 2 - 0.1, z + 0.02), (0.7, 0.22, 0.05), "skora", faza=0.0)
        p.blok("Sznurek", (0.18, 0.3, z + 0.07), (0.06, 0.7, 0.05), "sznurek", "matowy", rot=(0, 0, 22), faza=0.0)
        p.blok("Gwizdek", (0.34, -0.08, z + 0.12), (0.3, 0.22, 0.16), "gwizdek", "metal", faza=0.05)
        for zn in (1, -1):
            p.blok("Bark " + ("L" if zn > 0 else "P"), (zn * (w / 2 + 0.2), h / 2 - 0.2, 0), (0.7, 0.4, d + 0.1), "skora",
                   faza=0.12)
    for s in ("Left", "Right"):
        with p.na(s + "UpperArm", od="srodek"):
            w, h, d = p.wymiary(s + "UpperArm")
            p.blok("Biceps", (0, 0.0, 0.03), (w + 0.16, h - 0.25, d + 0.16), "skora", faza=0.1)
        with p.na(s + "LowerArm", od="srodek"):
            w, h, d = p.wymiary(s + "LowerArm")
            p.blok("Frotka", (0, -h / 2 + 0.12, 0), (w + 0.1, 0.22, d + 0.1), "opaska", "matowy", faza=0.03)
        with p.na(s + "UpperLeg", od="srodek"):
            w, h, d = p.wymiary(s + "UpperLeg")
            p.blok("Nogawka", (0, -h / 2 + 0.08, 0), (w + 0.1, 0.16, d + 0.1), "spodenki", "matowy")
        with p.na(s + "Foot", od="srodek"):
            w, h, d = p.wymiary(s + "Foot")
            p.blok("Pasek buta", (0, 0.03, 0.05), (w + 0.04, 0.12, d - 0.3), "pas_koszulki", "matowy", faza=0.0)
        with p.na(s + "LowerLeg", od="srodek"):
            w, h, d = p.wymiary(s + "LowerLeg")
            p.blok("Skarpeta", (0, -h / 2 + 0.14, 0), (w + 0.06, 0.28, d + 0.06), "but", "matowy")
    N.pas(p, "sznurek", klamra=None)
    N.buty(p, "but", cholewa=0)
    with p.na("LeftHand", od="srodek"):
        # podkładka z listą: leży na dłoni przy przedramieniu poziomo (oś Z dłoni = pion świata)
        p.blok("Podkladka", (0, -0.3, 0.26), (0.9, 1.1, 0.07), "podkladka", "matowy", rot=(18, 0, 0), faza=0.02)
        p.blok("Kartka", (0, -0.32, 0.31), (0.74, 0.9, 0.03), "kartka", "matowy", rot=(18, 0, 0), faza=0.0)
        p.blok("Klips", (0, 0.1, 0.2), (0.4, 0.14, 0.08), "gwizdek", "metal", rot=(18, 0, 0), faza=0.0)
    N.klipy(p, BAZA, wolna="Right", gest=_gest)
    p.ustaw_poze_renderu("gest", 19)
    return [p]


SLABOSCI = N.SLABOSCI + [
    "W geście (napięte bicepsy) podkładka zostaje w lewej dłoni i obraca się razem z ręką.",
]
