# -*- coding: utf-8 -*-
"""OPIEKUNKA — opiekunka zagrody petów w bazarze (NPC, D-109; miejsce bazaru „zagroda_petow”).
Młoda kobieta: słomkowy kapelusz z turkusową wstążką, rude warkocze z kokardami, piegi, biała koszula z podwiniętymi
rękawami, turkusowe ogrodniczki, brązowe buty; w lewej dłoni drewniane wiadro z kością dla petów.

    python -B swiat/postacie/przebuduj.py npc_opiekunka --bez-filmow

Klipy: spoczynek, powitanie (macha prawą ręką), gest (unosi wiadro i potrząsa nim — woła pety).
Status: propozycja (własny projekt, nie kanon). Ciało i klipy wspólne: npc_wspolne.py.
"""
from swiat.postacie import npc_wspolne as N

ID = "npc_opiekunka"
PALETA = {"wlos": "D2601F", "slomka": "E6C86A", "slomka_cien": "C9A84C", "wstazka": "2FB7A6", "koszula": "F6F2E8",
          "ogrodniczki": "2A9D8F", "ogrodniczki_cien": "1F776C", "but": "6B4226", "wiadro": "A9743F",
          "obrecz": "5B6470", "kosc": "F4EEDC", "pieg": "B9683A"}
BAZA = {"LeftUpperArm": (-6, 0, 10), "LeftLowerArm": (-14, 0, 0), "RightUpperArm": (4, 0, -30), "RightLowerArm": (0, 0, 64),
        "RightHand": (0, 0, 8)}


def _gest(p, start):
    k = p.klip("gest", 54, petla=False)
    k.poza(0, start)
    gora = {"LeftUpperArm": (-78, 0, 6), "LeftLowerArm": (-30, 0, 0), "Head": (-6, 10, 0), "UpperTorso": (-3, 6, 0)}
    k.poza(12, gora)
    for f, kat in ((18, -18), (24, -42), (30, -18), (36, -42), (42, -30)):
        k.poza(f, {"LeftLowerArm": (kat, 0, 0)})
    k.poza(42, {"LeftUpperArm": (-78, 0, 6), "Head": (-6, 10, 0), "UpperTorso": (-3, 6, 0)})
    k.poza(54, start)


def zbuduj():
    p = N.ludzik(ID, "Opiekunka", PALETA,
                 {"glowa": "skora", "tulow": "koszula", "pas": "ogrodniczki", "ramiona": "koszula",
                  "LeftLowerArm": "skora", "RightLowerArm": "skora", "dlonie": "skora",
                  "nogi": "ogrodniczki", "stopy": "but"})
    N.twarz(p, oczy="duze", brew="wlos", brew_kat=10, usta="otwarte", piegi="pieg", teczowka="1F5E4A")
    N.wlosy(p, "wlos", fryzura="warkocze", wstazka="wstazka")
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        with p.uklad(pos=(0, h / 2 + 0.26, 0), obrot=(0, 0, 5)):
            p.walec("Kapelusz rondo", (0, 0, 0), (2.7, 0.12, 2.7), "slomka", "matowy", segm=8)
            p.walec("Kapelusz glowka", (0, 0.3, 0), (1.5, 0.5, 1.5), "slomka", "matowy", segm=8)
            p.walec("Kapelusz wstazka", (0, 0.14, 0), (1.56, 0.18, 1.56), "wstazka", "matowy", segm=8)
            p.blok("Kapelusz plecionka", (0, 0.57, 0), (1.0, 0.04, 1.0), "slomka_cien", "matowy", rot=(0, 45, 0), faza=0.0)
    N.fartuch(p, "ogrodniczki", cien="ogrodniczki_cien", szelki="ogrodniczki", dol=0.0)
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        for zn in (1, -1):
            p.blok("Guzik " + ("L" if zn > 0 else "P"), (zn * 0.55, 0.28, d / 2 + 0.11), (0.2, 0.2, 0.05), "zloto", "metal",
                   faza=0.03)
    N.rekawy(p, "koszula", mankiet="slomka_cien")
    N.buty(p, "but", jasny="wiadro", cholewa=0.2)
    N.piesc(p, "Left")
    with p.na("LeftHand", od="srodek"):
        # wiadro wisi pod dłonią na kabłąku; kość wystaje ponad brzeg
        p.blok("Kablak", (0, -0.42, 0), (1.0, 0.08, 0.08), "obrecz", "metal", faza=0.0)
        for zn in (1, -1):
            p.blok("Kablak bok " + ("L" if zn > 0 else "P"), (zn * 0.5, -0.66, 0), (0.08, 0.5, 0.08), "obrecz", "metal",
                   faza=0.0)
        p.walec("Wiadro", (0, -1.3, 0), (1.1, 0.9, 1.1), "wiadro", "matowy", segm=8)
        p.walec("Wiadro obrecz", (0, -1.0, 0), (1.16, 0.14, 1.16), "obrecz", "metal", segm=8)
        p.walec("Wiadro obrecz dol", (0, -1.62, 0), (1.14, 0.12, 1.14), "obrecz", "metal", segm=8)
        with p.uklad(pos=(0.1, -0.84, 0.1), obrot=(0, 30, 24)):
            p.blok("Kosc", (0, 0, 0), (1.0, 0.18, 0.18), "kosc", "matowy", faza=0.05)
            for zn in (1, -1):
                p.blok("Kosc koniec %d" % zn, (zn * 0.5, 0, 0), (0.2, 0.34, 0.2), "kosc", "matowy", faza=0.06)
    N.klipy(p, BAZA, wolna="Right", gest=_gest)
    p.ustaw_poze_renderu("powitanie", 24)
    return [p]


SLABOSCI = N.SLABOSCI + [
    "Wiadro wisi sztywno pod dłonią (bryły na kości dłoni) — przy potrząsaniu nie kołysze się osobno.",
]
