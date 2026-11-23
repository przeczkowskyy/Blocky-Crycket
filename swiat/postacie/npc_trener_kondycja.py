# -*- coding: utf-8 -*-
"""TRENERKA KONDYCJI — biegaczka z bębnem przy mini-grze Kondycji („Bieżnia”) w Training Center (NPC, D-109).
Wysportowana kobieta o ciemnej karnacji: kasztanowy kucyk, pomarańczowa opaska na czole, zielona koszulka z numerem
(pasek, bez cyfr), granatowe legginsy z lampasem, kremowe buty do biegania, stoper na szyi; w prawej dłoni pałka
do bębna, którym nadaje tempo.

    python -B swiat/postacie/przebuduj.py npc_trener_kondycja --bez-filmow

Klipy: spoczynek, powitanie (macha lewą ręką), gest (trzy uderzenia pałką w rytm i krok w miejscu),
akcja (jedno uderzenie pałką — krótki ruch dla mini-gry Kondycji).
Status: propozycja (własny projekt, nie kanon). Ciało i klipy wspólne: npc_wspolne.py.
"""
from swiat.postacie import npc_wspolne as N

ID = "npc_trener_kondycja"
PALETA = {"wlos": "5A2E1A", "opaska": "F08A24", "koszulka": "2E8B57", "koszulka_cien": "226B43", "legginsy": "264653",
          "lampas": "F08A24", "but": "F2E8D0", "but_cien": "D9422E", "stoper": "C9CED6", "palka": "C9A26A",
          "palka_glowka": "E5533D"}
BAZA = {"RightUpperArm": (-14, 0, -8), "RightLowerArm": (-70, 0, 0), "LeftUpperArm": (6, 0, 32), "LeftLowerArm": (0, 0, -68),
        "LeftHand": (0, 0, -8)}


def _gest(p, start):
    k = p.klip("gest", 54, petla=False)
    k.poza(0, N._zera(start, ("LeftUpperLeg", "LeftLowerLeg", "RightUpperLeg", "RightLowerLeg")))
    for i, f in enumerate((6, 20, 34)):
        lewa = i % 2 == 0
        k.poza(f, {"RightUpperArm": (-40, 0, -10), "RightLowerArm": (-100, 0, 0), "Head": (-4, 0, 0),
                   ("LeftUpperLeg" if lewa else "RightUpperLeg"): (-40, 0, 0),
                   ("LeftLowerLeg" if lewa else "RightLowerLeg"): (55, 0, 0),
                   ("RightUpperLeg" if lewa else "LeftUpperLeg"): (0, 0, 0),
                   ("RightLowerLeg" if lewa else "LeftLowerLeg"): (0, 0, 0)})
        k.poza(f + 6, {"RightUpperArm": (-22, 0, -8), "RightLowerArm": (-48, 0, 0), "Head": (5, 0, 0),
                       "LeftUpperLeg": (0, 0, 0), "LeftLowerLeg": (0, 0, 0), "RightUpperLeg": (0, 0, 0),
                       "RightLowerLeg": (0, 0, 0)}, wyg="liniowo")
    k.poza(54, N._zera(start, ("LeftUpperLeg", "LeftLowerLeg", "RightUpperLeg", "RightLowerLeg")))


def _akcja(p, start):
    """Jedno uderzenie pałką (ruch mini-gry Kondycji): uniesienie, uderzenie w dół, odbicie, powrót.
    18 klatek; czas w grze ustawia swiat/npc_gra (trenerzy.akcja_s)."""
    k = p.klip("akcja", 18, petla=False)
    k.poza(0, start)
    k.poza(5, {"RightUpperArm": (-42, 0, -10), "RightLowerArm": (-102, 0, 0), "Head": (-4, 0, 0), "UpperTorso": (-2, 0, 0)})
    k.poza(8, {"RightUpperArm": (-20, 0, -8), "RightLowerArm": (-44, 0, 0), "Head": (6, 0, 0), "UpperTorso": (3, 0, 0)},
           wyg="liniowo")
    k.poza(11, {"RightUpperArm": (-26, 0, -8), "RightLowerArm": (-64, 0, 0), "Head": (3, 0, 0), "UpperTorso": (1, 0, 0)})
    k.poza(18, start)


def zbuduj():
    p = N.ludzik(ID, "Trenerka Kondycji", PALETA,
                 {"glowa": "skora_ciemna", "tulow": "koszulka", "pas": "legginsy", "ramiona": "skora_ciemna",
                  "dlonie": "skora_ciemna", "nogi": "legginsy", "stopy": "but"})
    N.twarz(p, oczy="duze", brew="wlos", brew_kat=8, usta="otwarte", skora_cien="skora_ciemna_cien", rumieniec=False)
    N.wlosy(p, "wlos", fryzura="kucyk", wstazka="opaska")
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        p.blok("Opaska", (0, h / 2 - 0.24, 0), (w + 0.12, 0.2, d + 0.12), "opaska", "matowy", faza=0.03)
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.blok("Pasek numeru", (0, -0.05, z + 0.03), (1.1, 0.5, 0.05), "but", "matowy", faza=0.02)
        p.blok("Pasek numeru kreska", (0, -0.05, z + 0.06), (0.7, 0.12, 0.03), "koszulka_cien", "matowy", faza=0.0)
        p.blok("Dekolt", (0, h / 2 - 0.1, z + 0.02), (0.6, 0.22, 0.05), "skora_ciemna", faza=0.0)
        p.blok("Stoper sznurek", (-0.2, 0.36, z + 0.07), (0.05, 0.5, 0.04), "legginsy", "matowy", rot=(0, 0, -20), faza=0.0)
        p.walec("Stoper", (-0.32, 0.1, z + 0.1), (0.3, 0.08, 0.3), "stoper", "metal", rot=(90, 0, 0), segm=8)
    N.rekawy(p, "koszulka", mankiet="koszulka_cien")
    for s in ("Left", "Right"):
        zn = 1 if s == "Left" else -1
        for kosc in ("UpperLeg", "LowerLeg"):
            with p.na(s + kosc, od="srodek"):
                w, h, d = p.wymiary(s + kosc)
                p.blok("Lampas", (zn * (w / 2 + 0.01), 0, 0), (0.04, h, 0.3), "lampas", "matowy", faza=0.0)
        with p.na(s + "LowerArm", od="srodek"):
            w, h, d = p.wymiary(s + "LowerArm")
            p.blok("Frotka", (0, -h / 2 + 0.12, 0), (w + 0.1, 0.22, d + 0.1), "opaska", "matowy", faza=0.03)
    N.pas(p, "koszulka_cien", klamra=None)
    N.buty(p, "but", jasny="but_cien", cholewa=0)
    N.piesc(p, "Right", "skora_ciemna")
    with p.na("RightHand", od="srodek"):
        # pałka do bębna wzdłuż −Y dłoni (przedłuża przedramię), z miękką główką
        p.blok("Palka", (0, -0.75, 0.05), (0.12, 1.3, 0.12), "palka", "matowy", faza=0.03)
        p.kula("Palka glowka", (0, -1.45, 0.05), 0.34, "palka_glowka", "matowy", segm=8)
    _akcja(p, N.klipy(p, BAZA, wolna="Left", gest=_gest))
    p.ustaw_poze_renderu("powitanie", 24)
    return [p]


SLABOSCI = N.SLABOSCI + [
    "Bębna nie ma w modelu — to rekwizyt stanowiska (stoi przed trenerką, uderzenia pałki kończą się ok. 1,6 studa "
    "przed nią na wysokości pasa).",
]
