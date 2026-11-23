# -*- coding: utf-8 -*-
"""MAG-SKLEPIKARZ — sprzedawca sklepu magicznego w bazarze (NPC, D-109; miejsce bazaru „sklep_magiczny”).
Starszy człowiek (nie kot — Kot-Mag to bohater gracza): fioletowa szata do kostek ze złotym brzegiem i złotym pasem,
biała broda do piersi, krzaczaste białe brwi, spiczasty kapelusz zgięty w czubku ze złotą gwiazdką; w prawej dłoni
kostur z turkusowym kryształem, oparty o ziemię.

    python -B swiat/postacie/przebuduj.py npc_mag --bez-filmow

Klipy: spoczynek, powitanie (macha lewą ręką), gest (unosi kostur, lewą dłonią zatacza krąg nad kryształem).
Status: propozycja (własny projekt, nie kanon). Ciało i klipy wspólne: npc_wspolne.py.
"""
from swiat.postacie import npc_wspolne as N

ID = "npc_mag"
PALETA = {"szata": "6A3FB5", "szata_cien": "4E2C8C", "zloto_szaty": "E8B93A", "broda": "F1EEE6", "broda_cien": "D6D0C2",
          "kapelusz": "5A34A0", "drewno": "8B5A2E", "krysztal": "4FE3D0", "but": "2E2238"}
# prawa ręka: przedramię poziomo do przodu (razem −90°), więc kostur wzdłuż osi Z dłoni stoi pionowo
BAZA = {"RightUpperArm": (-10, 0, -8), "RightLowerArm": (-80, 0, 0), "LeftUpperArm": (0, 0, 6), "LeftLowerArm": (-10, 0, 0)}


def _gest(p, start):
    k = p.klip("gest", 60, petla=False)
    k.poza(0, start)
    gora = {"RightUpperArm": (-38, 0, -12), "RightLowerArm": (-62, 0, 0), "LeftUpperArm": (-75, 0, -22),
            "LeftLowerArm": (-45, 0, 0), "Head": (-8, -8, 0), "UpperTorso": (-4, -5, 0)}
    k.poza(14, gora)
    for f, (rx, rz) in ((22, (-88, -34)), (30, (-70, -12)), (38, (-88, -34)), (46, (-75, -22))):
        k.poza(f, {"LeftUpperArm": (rx, 0, rz)})
    k.poza(46, {"RightUpperArm": (-38, 0, -12), "RightLowerArm": (-62, 0, 0), "LeftLowerArm": (-45, 0, 0),
                "Head": (-8, -8, 0), "UpperTorso": (-4, -5, 0)})
    k.poza(60, start)


def zbuduj():
    p = N.ludzik(ID, "Mag", PALETA,
                 {"glowa": "skora", "tulow": "szata", "pas": "szata", "ramiona": "szata", "dlonie": "skora",
                  "nogi": "szata_cien", "stopy": "but"})
    N.twarz(p, oczy="duze", brew=None, usta=None, rumieniec=True)
    N.broda(p, "broda", dl=0.95, cien="broda_cien")
    N.wasy(p, "broda")
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        z = d / 2
        for zn in (1, -1):
            s = "L" if zn > 0 else "P"
            p.blok("Brew krzak " + s, (zn * 0.36, 0.42, z + 0.06), (0.5, 0.18, 0.14), "broda", "matowy",
                   rot=(0, 0, zn * 16), faza=0.04)
            p.blok("Wlosy bok " + s, (zn * (w / 2 + 0.05), 0.0, -0.2), (0.14, 0.9, d - 0.3), "broda", "matowy")
        p.blok("Wlosy tyl", (0, -0.1, -z - 0.06), (w + 0.1, h - 0.1, 0.16), "broda", "matowy", faza=0.05)
        with p.uklad(pos=(0, h / 2 + 0.02, 0)):
            p.walec("Kapelusz rondo", (0, 0.06, 0), (2.5, 0.14, 2.5), "szata_cien", "matowy", segm=8)
            p.walec("Kapelusz opaska", (0, 0.24, 0), (1.5, 0.24, 1.5), "zloto_szaty", "matowy", segm=8)
            with p.uklad(pos=(0, 0.3, 0), obrot=(-6, 0, 5)):
                p.stozek("Kapelusz stozek", (0, 0.55, 0), (1.44, 1.1, 1.44), "kapelusz", "matowy", gora=0.34, segm=8)
                with p.uklad(pos=(0, 1.05, 0), obrot=(-38, 0, 0)):
                    p.stozek("Kapelusz czubek", (0, 0.32, 0), (0.52, 0.7, 0.52), "kapelusz", "matowy", segm=8)
                    p.blok("Gwiazdka a", (0, 0.74, 0.04), (0.42, 0.42, 0.1), "zloto", "metal", rot=(0, 0, 45), faza=0.0)
                    p.blok("Gwiazdka b", (0, 0.74, 0.06), (0.42, 0.42, 0.1), "zloto", "metal", faza=0.0)
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.blok("Szata plisa", (0, -0.05, z + 0.03), (0.3, h - 0.1, 0.06), "zloto_szaty", "matowy", faza=0.0)
        for zn in (1, -1):
            p.klin("Kolnierz " + ("L" if zn > 0 else "P"), (zn * 0.42, h / 2 + 0.05, z - 0.15), (0.5, 0.24, 0.36),
                   "szata_cien", "matowy", rot=(0, 0, zn * -12))
    N.rekawy(p, "szata", mankiet="zloto_szaty", dlugie=True)
    N.pas(p, "zloto_szaty", klamra="krysztal")
    N.spodnica(p, "szata", brzeg="zloto_szaty", dl=1.7, szer=0.7, rozciecie=True)
    N.buty(p, "but", cholewa=0)
    N.piesc(p, "Right")
    with p.na("RightHand", od="srodek"):
        # kostur wzdłuż osi Z dłoni: dół 2,35 pod dłonią (ziemia), góra 2,7 nad nią; kryształ w widełkach
        p.blok("Kostur", (0, 0, 0.2), (0.2, 0.2, 5.0), "drewno", "matowy", faza=0.04)
        p.blok("Kostur okucie", (0, 0, -2.2), (0.26, 0.26, 0.3), "zloto_szaty", "metal", faza=0.03)
        for zn in (1, -1):
            p.blok("Kostur widelki " + ("L" if zn > 0 else "P"), (zn * 0.24, 0, 2.85), (0.12, 0.18, 0.7), "drewno",
                   "matowy", rot=(0, zn * 16, 0), faza=0.03)
        p.blok("Krysztal", (0, 0, 3.1), (0.42, 0.42, 0.62), "krysztal", "swiecacy", rot=(0, 0, 45), faza=0.1)
    N.klipy(p, BAZA, wolna="Left", gest=_gest)
    p.ustaw_poze_renderu("powitanie", 24)
    return [p]


SLABOSCI = N.SLABOSCI + [
    "Dół szaty jest sztywnym dzwonem na kości bioder — nogi są pod nim, mag stoi, nie chodzi.",
    "Kostur jest ustawiony na pozę spoczynku (przedramię poziomo): stoi pionowo i sięga ziemi tylko w tej pozie.",
]
