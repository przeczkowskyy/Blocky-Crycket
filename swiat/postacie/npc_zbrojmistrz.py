# -*- coding: utf-8 -*-
"""ZBROJMISTRZ — sprzedawca broni i zbroi w bazarze (NPC, D-109; miejsce bazaru „zbrojownia”).
Krępy, szeroki w barach: stalowy hełm z nosalem i złotym rantem, ruda broda do piersi i wąsy, granatowa koszula,
ciemny skórzany fartuch, stalowe karwasze i naramienniki; w prawej dłoni miecz ostrzem w górę, lewa ręka na biodrze.
Inny niż kowal (chustka, gogle, czarna broda, młot i szczypce).

    python -B swiat/postacie/przebuduj.py npc_zbrojmistrz --bez-filmow

Klipy: spoczynek, powitanie (macha lewą ręką), gest (unosi miecz przed twarz, ogląda klingę i salutuje nim).
Status: propozycja (własny projekt, nie kanon). Ciało i klipy wspólne: npc_wspolne.py.
"""
from swiat.postacie import npc_wspolne as N

ID = "npc_zbrojmistrz"
PALETA = {"broda": "C8551E", "broda_cien": "A3421A", "helm": "8E98A8", "helm_cien": "5E6878", "koszula": "34507A",
          "fartuch": "5A3418", "fartuch_cien": "3E2410", "spodnie": "4A3A2C", "but": "33200F", "klinga": "D5DCE6",
          "jelec": "E0A93A", "rekojesc": "5A2E1A"}
BAZA = {"RightUpperArm": (-10, 0, -10), "RightLowerArm": (-80, 0, 0),
        "LeftUpperArm": (6, 0, 32), "LeftLowerArm": (0, 0, -68), "LeftHand": (0, 0, -8)}


def _gest(p, start):
    k = p.klip("gest", 60, petla=False)
    k.poza(0, start)
    ogl = {"RightUpperArm": (-55, 0, 22), "RightLowerArm": (-70, 0, 0), "RightHand": (0, 0, -25),
           "Head": (6, -14, 0), "UpperTorso": (0, -6, 0)}
    k.poza(14, ogl)
    k.poza(24, {**ogl, "RightHand": (0, 0, 25), "Head": (2, -10, 4)})
    k.poza(34, {**ogl, "RightHand": (0, 0, -10), "Head": (6, -14, 0)})
    salut = {"RightUpperArm": (-120, 0, -8), "RightLowerArm": (-40, 0, 0), "RightHand": (0, 0, 0), "Head": (-6, 0, 0),
             "UpperTorso": (-4, 0, 0)}
    k.poza(42, salut, wyg="liniowo")
    k.poza(50, salut)
    k.poza(60, N._zera(start, ("RightHand",)))
    k.poza(0, {"RightHand": (0, 0, 0)})


def zbuduj():
    p = N.ludzik(ID, "Zbrojmistrz", PALETA,
                 {"glowa": "skora", "tulow": "koszula", "pas": "spodnie", "ramiona": "koszula",
                  "LeftLowerArm": "helm_cien", "RightLowerArm": "helm_cien", "dlonie": "skora",
                  "nogi": "spodnie", "stopy": "but"})
    N.twarz(p, oczy="duze", brew="broda", brew_kat=-8, usta=None, nos=0.34)
    N.broda(p, "broda", dl=0.8, cien="broda_cien")
    N.wasy(p, "broda", podkrecone=True)
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        z = d / 2
        p.blok("Helm", (0, h / 2 + 0.16, -0.03), (w + 0.14, 0.6, d + 0.12), "helm", "metal", faza=0.12)
        p.blok("Helm rant", (0, h / 2 - 0.1, -0.03), (w + 0.22, 0.2, d + 0.2), "jelec", "metal", faza=0.04)
        p.blok("Helm czubek", (0, h / 2 + 0.5, -0.03), (0.6, 0.24, 0.6), "helm_cien", "metal", rot=(0, 45, 0), faza=0.05)
        p.blok("Nosal", (0, h / 2 - 0.4, z + 0.1), (0.2, 0.62, 0.12), "helm", "metal", faza=0.03)
        p.blok("Helm kark", (0, 0.1, -z - 0.08), (w + 0.1, 0.9, 0.14), "helm_cien", "metal", faza=0.04)
    N.fartuch(p, "fartuch", cien="fartuch_cien", szelki="fartuch_cien", dol=1.0)
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        for zn in (1, -1):
            p.blok("Bark " + ("L" if zn > 0 else "P"), (zn * (w / 2 + 0.3), h / 2 - 0.12, 0), (0.9, 0.34, d + 0.2), "helm",
                   "metal", faza=0.1)
    for s in ("Left", "Right"):
        with p.na(s + "UpperArm", od="srodek"):
            w, h, d = p.wymiary(s + "UpperArm")
            p.blok("Biceps", (0, -0.12, 0), (w + 0.1, h - 0.3, d + 0.1), "skora", faza=0.06)
        with p.na(s + "LowerArm", od="srodek"):
            w, h, d = p.wymiary(s + "LowerArm")
            p.blok("Karwasz", (0, 0.0, 0), (w + 0.12, h - 0.15, d + 0.12), "helm", "metal", faza=0.05)
            p.blok("Karwasz rant", (0, -h / 2 + 0.12, 0), (w + 0.18, 0.12, d + 0.18), "jelec", "metal", faza=0.0)
    N.pas(p, "fartuch_cien", klamra="jelec")
    N.buty(p, "but", cholewa=0.22, okucie="helm")
    N.piesc(p, "Right")
    with p.na("RightHand", od="srodek"):
        # miecz wzdłuż osi Z dłoni (pionowo przy przedramieniu poziomo): głowica w dół, klinga w górę
        p.blok("Rekojesc", (0, 0, 0.0), (0.18, 0.18, 0.7), "rekojesc", "matowy", faza=0.03)
        p.blok("Glowica", (0, 0, -0.45), (0.28, 0.28, 0.24), "jelec", "metal", faza=0.06)
        p.blok("Jelec", (0, 0, 0.45), (0.9, 0.2, 0.16), "jelec", "metal", faza=0.04)
        p.blok("Klinga", (0, 0, 1.6), (0.36, 0.1, 2.2), "klinga", "metal", faza=0.03)
        p.blok("Klinga zbrocze", (0, 0, 1.5), (0.1, 0.12, 1.8), "helm", "metal", faza=0.0)
        p.blok("Klinga sztych", (0, 0, 2.78), (0.26, 0.1, 0.26), "klinga", "metal", rot=(0, 45, 0), faza=0.0)
    N.klipy(p, BAZA, wolna="Left", gest=_gest)
    p.ustaw_poze_renderu("powitanie", 24)
    return [p]


SLABOSCI = N.SLABOSCI + [
    "Miecz jest ustawiony na pozę spoczynku (przedramię poziomo): klinga stoi pionowo tylko w tej pozie.",
    "Lewa ręka na biodrze: przedramię lekko wchodzi w fartuch i pas.",
]
