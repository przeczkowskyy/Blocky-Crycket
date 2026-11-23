# -*- coding: utf-8 -*-
"""TRENERKA INTELIGENCJI — uczona od run przy mini-grze Inteligencji („Runy”) w Training Center (NPC, D-109).
Uczona w okularach: ciemne włosy w koku ze złotą szpilką, granatowa szata do kostek ze złotym brzegiem i trzema
świecącymi znakami na piersi (umowne kształty, nie litery), złoty pas z sakwą; w lewej dłoni otwarta księga, prawa ręka wolna do kreślenia run.

    python -B swiat/postacie/przebuduj.py npc_trener_inteligencja --bez-filmow

Klipy: spoczynek, powitanie (macha prawą ręką), gest (kreśli prawą dłonią runę w powietrzu nad księgą).
Status: propozycja (własny projekt, nie kanon). Ciało i klipy wspólne: npc_wspolne.py.
"""
from swiat.postacie import npc_wspolne as N

ID = "npc_trener_inteligencja"
PALETA = {"wlos": "2A2233", "szata": "27406B", "szata_cien": "1B2E50", "zloto_szaty": "E8B93A", "runa": "4FE3D0",
          "ksiega": "8A2F3A", "ksiega_cien": "63202A", "kartki": "F6EED8", "but": "2A2233", "oprawka": "E8B93A"}
# lewa ręka: przedramię poziomo do przodu — księga leży na dłoni (oś Z dłoni = pion świata)
BAZA = {"LeftUpperArm": (-14, 0, 4), "LeftLowerArm": (-76, 0, 0), "RightUpperArm": (0, 0, -6), "RightLowerArm": (-10, 0, 0)}


def _gest(p, start):
    k = p.klip("gest", 60, petla=False)
    k.poza(0, N._zera(start, ("RightHand",)))
    k.poza(12, {"RightUpperArm": (-78, 0, 14), "RightLowerArm": (-40, 0, 0), "RightHand": (0, 0, 0), "Head": (8, 8, 0),
                "UpperTorso": (0, 5, 0)})
    for f, (rx, rz, lo) in ((20, (-96, 2, -20)), (28, (-78, -12, -48)), (36, (-62, 6, -30)), (44, (-84, 18, -40))):
        k.poza(f, {"RightUpperArm": (rx, 0, rz), "RightLowerArm": (lo, 0, 0)})
    k.poza(44, {"Head": (4, 8, 0), "UpperTorso": (0, 5, 0), "RightHand": (0, 0, 0)})
    k.poza(60, N._zera(start, ("RightHand",)))


def zbuduj():
    p = N.ludzik(ID, "Trenerka Inteligencji", PALETA,
                 {"glowa": "skora", "tulow": "szata", "pas": "szata", "ramiona": "szata", "dlonie": "skora",
                  "nogi": "szata_cien", "stopy": "but"})
    N.twarz(p, oczy="duze", brew="wlos", brew_kat=6, usta="usmiech", teczowka="3A2A5C")
    N.wlosy(p, "wlos", fryzura="kok", wstazka="zloto_szaty")
    N.okulary(p, "oprawka")
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        for zn in (1, -1):
            p.klin("Kolnierz " + ("L" if zn > 0 else "P"), (zn * 0.4, h / 2 + 0.05, z - 0.15), (0.5, 0.24, 0.36),
                   "zloto_szaty", "matowy", rot=(0, 0, zn * -12))
        # znaki umowne, nie litery: dwie ukośne kreski, romb, daszek
        for dx in (-0.08, 0.08):
            p.blok("Znak kreska %+d" % (dx > 0), (-0.58 + dx, 0.05, z + 0.03), (0.08, 0.46, 0.04), "runa", "swiecacy",
                   rot=(0, 0, -24), faza=0.0)
        p.blok("Znak romb", (0.0, 0.05, z + 0.03), (0.32, 0.32, 0.04), "runa", "swiecacy", rot=(0, 0, 45), faza=0.0)
        p.blok("Znak romb srodek", (0.0, 0.05, z + 0.045), (0.14, 0.14, 0.03), "szata_cien", "matowy", rot=(0, 0, 45),
               faza=0.0)
        for zn in (1, -1):
            p.blok("Znak daszek %+d" % zn, (0.58 + zn * 0.11, 0.08, z + 0.03), (0.08, 0.36, 0.04), "runa", "swiecacy",
                   rot=(0, 0, zn * 36), faza=0.0)
    N.rekawy(p, "szata", mankiet="zloto_szaty", dlugie=True)
    N.pas(p, "zloto_szaty", klamra="runa", sakwa="ksiega_cien")
    N.spodnica(p, "szata", brzeg="zloto_szaty", dl=1.7, szer=0.55)
    N.buty(p, "but", cholewa=0)
    with p.na("LeftHand", od="srodek"):
        # otwarta księga na dłoni: okładka płasko (cienka w osi Z dłoni), kartki, grzbiet wzdłuż ręki
        with p.uklad(pos=(0, -0.2, 0.3)):
            p.blok("Okladka", (0, 0, 0), (1.5, 1.0, 0.08), "ksiega", "matowy", faza=0.03)
            for zn in (1, -1):
                p.blok("Kartki %d" % zn, (zn * 0.37, 0, 0.09), (0.66, 0.9, 0.1), "kartki", "matowy", rot=(0, zn * 6, 0),
                       faza=0.02)
                p.blok("Linijki %d" % zn, (zn * 0.37, 0.05, 0.15), (0.4, 0.5, 0.02), "ksiega_cien", "matowy",
                       rot=(0, zn * 6, 0), faza=0.0)
            p.blok("Grzbiet", (0, 0, 0.04), (0.1, 1.0, 0.12), "ksiega_cien", "matowy", faza=0.0)
            p.blok("Zakladka", (0.05, -0.6, 0.1), (0.1, 0.3, 0.03), "zloto_szaty", "matowy", faza=0.0)
    N.klipy(p, BAZA, wolna="Right", gest=_gest)
    p.ustaw_poze_renderu("gest", 28)
    return [p]


SLABOSCI = N.SLABOSCI + [
    "Dół szaty jest sztywnym dzwonem na kości bioder — nogi są pod nim, uczona stoi, nie chodzi.",
    "Księga jest ustawiona na pozę spoczynku (lewe przedramię poziomo): leży płasko tylko w tej pozie.",
]
