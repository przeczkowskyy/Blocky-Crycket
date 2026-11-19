# -*- coding: utf-8 -*-
"""GOLEM — kamienny trener Pancerza („Blok”) w Training Center (NPC, D-109: golem przy Pancerzu zostaje golemem).
Przysadzisty kamienny olbrzym na kościach R15: mała głowa wciśnięta w barki, świecące turkusowe oczy i znak (romb) na
piersi, wielkie przedramiona i pięści (prawa w skórzanej rękawicy treningowej), mech na barkach, krótkie nogi.

    python -B swiat/postacie/przebuduj.py npc_golem --bez-filmow

Klipy: spoczynek (ciężki oddech), powitanie (unosi lewą pięść i macha), gest (zamach i cios prawą pięścią przed
siebie — ruch mini-gry Pancerza). Status: propozycja (własny projekt, nie kanon). Klipy wspólne: npc_wspolne.py.
"""
from swiat.postacie import npc_wspolne as N
from swiat.postacie.biblioteka.postac import Postac

ID = "npc_golem"
PALETA = {"kamien": "8C8F99", "kamien_jasny": "A9ADB8", "kamien_cien": "666A75", "kamien_ciemny": "4B4E58",
          "mech": "5E9B46", "mech_cien": "437A34", "runa": "4FE3D0", "rekawica": "A85A2A", "rekawica_cien": "7E411C",
          "szew": "F0E2C0"}
WYMIARY = {"Head": (1.5, 1.15, 1.4), "UpperTorso": (3.3, 1.9, 2.0), "LowerTorso": (2.4, 0.6, 1.6),
           "UpperArm": (1.3, 1.15, 1.3), "LowerArm": (1.55, 1.25, 1.55), "Hand": (1.7, 1.0, 1.7),
           "UpperLeg": (1.3, 0.65, 1.3), "LowerLeg": (1.4, 0.65, 1.4), "Foot": (1.6, 0.5, 1.9)}
BAZA = {"RightUpperArm": (-8, 0, -8), "RightLowerArm": (-18, 0, 0), "LeftUpperArm": (-6, 0, 8), "LeftLowerArm": (-14, 0, 0)}


def _gest(p, start):
    k = p.klip("gest", 48, petla=False)
    k.poza(0, start)
    zamach = {"RightUpperArm": (40, 0, -24), "RightLowerArm": (-110, 0, 0), "UpperTorso": (-4, -22, 0), "Head": (0, 14, 0),
              "LeftUpperArm": (-40, 0, 14), "LeftLowerArm": (-60, 0, 0)}
    cios = {"RightUpperArm": (-92, 0, 6), "RightLowerArm": (-6, 0, 0), "UpperTorso": (8, 16, 0), "Head": (-4, -10, 0),
            "LeftUpperArm": (20, 0, 12), "LeftLowerArm": (-70, 0, 0)}
    k.poza(14, zamach)
    k.poza(18, zamach, wyg="liniowo")
    k.poza(23, cios)
    k.poza(30, {**cios, "RightUpperArm": (-86, 0, 6), "UpperTorso": (6, 13, 0)})
    k.poza(48, start)


def zbuduj():
    pal = dict(N.PALETA)
    pal.update(PALETA)
    p = Postac(ID, "Golem", typ="r15", faza=0.07, paleta=pal, wymiary=WYMIARY, rozstaw_rak=2.5)
    p.cialo({"glowa": "kamien", "tulow": "kamien", "pas": "kamien_cien", "ramiona": "kamien_cien", "LeftLowerArm": "kamien",
             "RightLowerArm": "kamien", "LeftHand": "kamien_jasny", "RightHand": "rekawica", "nogi": "kamien_cien",
             "LeftLowerLeg": "kamien", "RightLowerLeg": "kamien", "stopy": "kamien_ciemny"})
    N.twarz(p, oczy="swiecace", brew="kamien_ciemny", brew_kat=-14, usta=None, rumieniec=False, teczowka="runa", nos=0,
            skora_cien="kamien_cien")
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        z = d / 2
        p.blok("Czolo", (0, h / 2 - 0.08, z + 0.05), (w + 0.1, 0.3, 0.2), "kamien_cien", "matowy", faza=0.06)
        p.blok("Szczeka", (0, -h / 2 + 0.16, z + 0.04), (w - 0.2, 0.36, 0.2), "kamien_jasny", "matowy", faza=0.06)
        p.blok("Usta", (0, -0.24, z + 0.15), (0.7, 0.07, 0.05), "kamien_ciemny", faza=0.0)
        p.blok("Mech glowa", (-0.2, h / 2 + 0.06, -0.1), (1.0, 0.16, 0.9), "mech", "matowy", rot=(0, 15, 0), faza=0.05)
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.blok("Plyta piersi", (0, 0.15, z + 0.06), (w - 0.9, h - 0.5, 0.16), "kamien_jasny", "matowy", faza=0.08)
        # znak umowny, nie litera: duży romb z ciemnym środkiem i dwa małe romby nad i pod nim
        p.blok("Znak romb", (0, 0.15, z + 0.15), (0.62, 0.62, 0.05), "runa", "swiecacy", rot=(0, 0, 45), faza=0.0)
        p.blok("Znak romb srodek", (0, 0.15, z + 0.17), (0.3, 0.3, 0.04), "kamien_ciemny", "matowy", rot=(0, 0, 45), faza=0.0)
        for dy in (-0.62, 0.62):
            p.blok("Znak romb maly %+d" % (dy > 0), (0, 0.15 + dy, z + 0.15), (0.2, 0.2, 0.05), "runa", "swiecacy",
                   rot=(0, 0, 45), faza=0.0)
        p.blok("Kark", (0, h / 2 + 0.1, -0.2), (w - 0.4, 0.4, d - 0.3), "kamien_cien", "matowy", faza=0.1)
        p.blok("Pekniecie", (0.9, -0.3, z + 0.02), (0.08, 0.9, 0.04), "kamien_ciemny", rot=(0, 0, 22), faza=0.0)
        for zn in (1, -1):
            s = "L" if zn > 0 else "P"
            p.blok("Glaz barku " + s, (zn * (w / 2 + 0.25), h / 2 - 0.1, 0), (1.5, 0.9, d + 0.3), "kamien", "matowy",
                   rot=(0, 0, zn * -10), faza=0.14)
            p.blok("Mech barku " + s, (zn * (w / 2 + 0.2), h / 2 + 0.38, -0.1), (1.1, 0.14, 1.3), "mech" if zn > 0 else
                   "mech_cien", "matowy", rot=(0, 0, zn * -10), faza=0.04)
    with p.na("LowerTorso", od="srodek"):
        w, h, d = p.wymiary("LowerTorso")
        p.blok("Biodra", (0, -0.05, 0), (w + 0.2, h + 0.2, d + 0.2), "kamien_ciemny", "matowy", faza=0.1)
    for s in ("Left", "Right"):
        with p.na(s + "LowerArm", od="srodek"):
            w, h, d = p.wymiary(s + "LowerArm")
            p.blok("Opaska kamienna", (0, h / 2 - 0.14, 0), (w + 0.14, 0.24, d + 0.14), "kamien_ciemny", "matowy", faza=0.04)
        with p.na(s + "Foot", od="srodek"):
            w, h, d = p.wymiary(s + "Foot")
            for i in (-1, 0, 1):
                p.blok("Palec %d" % i, (i * 0.5, -0.05, d / 2 + 0.06), (0.42, h - 0.1, 0.3), "kamien_jasny", "matowy", faza=0.06)
    with p.na("LeftHand", od="srodek"):
        w, h, d = p.wymiary("LeftHand")
        p.blok("Knykcie", (0, -h / 2 + 0.2, d / 2 - 0.1), (w + 0.06, 0.5, 0.3), "kamien", "matowy", faza=0.08)
    with p.na("RightHand", od="srodek"):
        w, h, d = p.wymiary("RightHand")
        p.blok("Rekawica", (0, -0.1, 0), (w + 0.2, h + 0.3, d + 0.2), "rekawica", "matowy", faza=0.16)
        p.blok("Rekawica mankiet", (0, h / 2 + 0.05, 0), (w + 0.1, 0.3, d + 0.1), "rekawica_cien", "matowy", faza=0.05)
        p.blok("Rekawica szew", (0, -0.1, d / 2 + 0.11), (w - 0.3, 0.08, 0.04), "szew", "matowy", faza=0.0)
        p.blok("Rekawica kciuk", (0.6, 0.0, d / 2 - 0.2), (0.5, 0.6, 0.5), "rekawica_cien", "matowy", faza=0.1)
    N.klipy(p, BAZA, wolna="Left", gest=_gest, machanie=128)
    p.ustaw_poze_renderu("gest", 23)
    return [p]


SLABOSCI = N.SLABOSCI[1:] + [
    "Golem ma własne klocki ciała (nie „czlowiek”): przedmioty bohaterów na niego nie pasują.",
    "Cios kończy się ok. 2,6 studa przed golemem na wysokości barku (skala 1); pole gry Pancerza trzeba dobrać "
    "do skali golema na stanowisku.",
]
