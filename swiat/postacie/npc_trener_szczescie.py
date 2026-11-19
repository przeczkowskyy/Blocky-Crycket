# -*- coding: utf-8 -*-
"""TRENER SZCZĘŚCIA — ogrodnik koniczyn przy mini-grze Szczęścia („Koniczyny”) w Training Center (NPC, D-109).
Pogodny ogrodnik: zielony kapelusz z rondem i czterolistną koniczyną, rude baki i wąs, biała koszula, zielona
kamizelka ze złotymi guzikami, brązowe spodnie, żółte kalosze; w prawej dłoni blaszana konewka.

    python -B swiat/postacie/przebuduj.py npc_trener_szczescie --bez-filmow

Klipy: spoczynek, powitanie (uchyla kapelusza lewą ręką — macha), gest (podlewa koniczyny: unosi i przechyla konewkę).
Status: propozycja (własny projekt, nie kanon). Ciało i klipy wspólne: npc_wspolne.py.
"""
from swiat.postacie import npc_wspolne as N

ID = "npc_trener_szczescie"
PALETA = {"wlos": "C8551E", "kapelusz": "2E8B57", "kapelusz_cien": "226B43", "koniczyna": "6FD15A", "koszula": "F6F2E8",
          "kamizelka": "3C9A5F", "kamizelka_cien": "2A7446", "spodnie": "6B4A2E", "kalosz": "F2C230",
          "kalosz_cien": "C99A1C", "blacha": "9FB0BF", "blacha_cien": "6E7F90"}
BAZA = {"RightUpperArm": (-8, 0, -10), "RightLowerArm": (-12, 0, 0), "LeftUpperArm": (6, 0, 32), "LeftLowerArm": (0, 0, -68),
        "LeftHand": (0, 0, -8)}


def _gest(p, start):
    k = p.klip("gest", 60, petla=False)
    k.poza(0, N._zera(start, ("RightHand",)))
    gora = {"RightUpperArm": (-58, 0, -6), "RightLowerArm": (-34, 0, 0), "RightHand": (0, 0, 0), "Head": (10, -8, 0),
            "UpperTorso": (5, -5, 0)}
    k.poza(12, gora)
    k.poza(20, {**gora, "RightHand": (52, 0, 0)})
    k.poza(30, {**gora, "RightHand": (46, 0, 0), "RightUpperArm": (-58, 0, 6)})
    k.poza(40, {**gora, "RightHand": (52, 0, 0), "RightUpperArm": (-58, 0, -14)})
    k.poza(48, gora)
    k.poza(60, N._zera(start, ("RightHand",)))


def zbuduj():
    p = N.ludzik(ID, "Trener Szczęścia", PALETA,
                 {"glowa": "skora", "tulow": "kamizelka", "pas": "spodnie", "ramiona": "koszula", "dlonie": "skora",
                  "LeftUpperLeg": "spodnie", "RightUpperLeg": "spodnie", "LeftLowerLeg": "kalosz",
                  "RightLowerLeg": "kalosz", "stopy": "kalosz"})
    N.twarz(p, oczy="usmiech", brew="wlos", brew_kat=10, usta="otwarte", piegi="wlos")
    N.wasy(p, "wlos")
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        for zn in (1, -1):
            s = "L" if zn > 0 else "P"
            p.blok("Bak " + s, (zn * (w / 2 + 0.04), -0.1, 0.3), (0.12, 0.7, 0.3), "wlos", "matowy")
            p.blok("Wlosy bok " + s, (zn * (w / 2 + 0.05), 0.2, -0.2), (0.14, 0.6, d - 0.3), "wlos", "matowy")
        p.blok("Wlosy tyl", (0, 0.05, -d / 2 - 0.06), (w + 0.1, h - 0.4, 0.16), "wlos", "matowy", faza=0.05)
        with p.uklad(pos=(0, h / 2 + 0.04, 0), obrot=(0, 0, -4)):
            p.walec("Kapelusz rondo", (0, 0.05, 0), (2.4, 0.12, 2.4), "kapelusz", "matowy", segm=8)
            p.walec("Kapelusz glowka", (0, 0.42, 0), (1.5, 0.66, 1.5), "kapelusz", "matowy", segm=8)
            p.walec("Kapelusz tasma", (0, 0.2, 0), (1.56, 0.16, 1.56), "kapelusz_cien", "matowy", segm=8)
            with p.uklad(pos=(0.5, 0.42, 0.72), obrot=(0, 30, 0)):
                for i, (x, y) in enumerate(((0.11, 0.11), (-0.11, 0.11), (0.11, -0.11), (-0.11, -0.11))):
                    p.blok("Koniczyna %d" % i, (x, y, 0.05), (0.2, 0.2, 0.06), "koniczyna", "matowy", faza=0.05)
                p.blok("Koniczyna lodyzka", (0.06, -0.3, 0.04), (0.05, 0.24, 0.04), "kapelusz_cien", "matowy",
                       rot=(0, 0, 15), faza=0.0)
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.blok("Koszula przod", (0, 0.05, z + 0.02), (0.6, h - 0.1, 0.05), "koszula", "matowy", faza=0.0)
        for i, y in enumerate((0.4, 0.0, -0.4)):
            p.blok("Guzik %d" % i, (0.42, y, z + 0.06), (0.14, 0.14, 0.04), "zloto", "metal", faza=0.03)
        p.blok("Kamizelka rabek", (0, -h / 2 + 0.06, 0), (w + 0.08, 0.12, d + 0.08), "kamizelka_cien", "matowy", faza=0.0)
        p.blok("Kieszonka", (-0.6, 0.3, z + 0.05), (0.4, 0.3, 0.05), "kamizelka_cien", "matowy", faza=0.0)
        p.blok("Koniczynka w kieszeni", (-0.6, 0.5, z + 0.07), (0.2, 0.2, 0.04), "koniczyna", "matowy", rot=(0, 0, 45),
               faza=0.0)
    N.rekawy(p, "koszula", mankiet="kamizelka_cien", dlugie=True)
    N.pas(p, "kalosz_cien", klamra="zloto")
    N.buty(p, "kalosz", jasny="kalosz_cien", cholewa=0.2)
    N.piesc(p, "Right")
    with p.na("RightHand", od="srodek"):
        # konewka pod dłonią: zbiornik, kabłąk w dłoni, dziobek ku przodowi (+Z) z sitkiem
        p.blok("Konewka uchwyt", (0, -0.34, 0), (0.1, 0.1, 0.9), "blacha_cien", "metal", faza=0.0)
        for zn in (1, -1):
            p.blok("Konewka wspornik %d" % zn, (0, -0.52, zn * 0.42), (0.1, 0.4, 0.1), "blacha_cien", "metal", faza=0.0)
        p.walec("Konewka zbiornik", (0, -1.1, 0), (1.0, 0.9, 1.0), "blacha", "metal", segm=8)
        p.walec("Konewka rant", (0, -0.68, 0), (1.06, 0.1, 1.06), "blacha_cien", "metal", segm=8)
        p.blok("Konewka dziobek", (0, -0.95, 0.85), (0.16, 0.16, 0.9), "blacha", "metal", rot=(-28, 0, 0), faza=0.03)
        p.walec("Konewka sitko", (0, -0.72, 1.28), (0.36, 0.1, 0.36), "blacha_cien", "metal", rot=(62, 0, 0), segm=8)
    N.klipy(p, BAZA, wolna="Left", gest=_gest)
    p.ustaw_poze_renderu("powitanie", 24)
    return [p]


SLABOSCI = N.SLABOSCI + [
    "Z konewki nic nie leci — wodę (cząsteczki) może dołożyć gra; w modelu jest sam ruch podlewania.",
]
