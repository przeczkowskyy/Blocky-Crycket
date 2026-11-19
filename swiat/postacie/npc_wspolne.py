# -*- coding: utf-8 -*-
"""Wspólne ciało i zestaw części postaci niezależnych (NPC, decyzja D-109) — biblioteka modułów npc_<id>.py.

NPC to ludzik R15 na klockach ciała „czlowiek” (te same wymiary, kości i stawy co goły Rycerz, 5,3 studa wzrostu),
więc wspólne klipy pasują na każdego, a przedmioty typu „czlowiek” da się na niego kiedyś założyć. Postacie różnią
twarz, włosy, zarost, strój i rekwizyt (bryły na kościach dłoni — rig z klocków ma je od razu w rękach, jak kowal).

    p = ludzik("npc_x", "Nazwa", PALETA, {"tulow": "kolor", ...})      # szkielet i klocki ciała
    twarz(p, oczy="duze", brew="wlos", usta="usmiech")                 # oczy, brwi, nos, usta, uszy, rumieniec
    wlosy(p, "wlos", fryzura="krotkie") · broda(p, "wlos") · wasy(p, "wlos")
    buty(p, "but") · pas(p, "pas", klamra="zloto") · fartuch(p, "skora") · spodnica(p, "szata", brzeg="zloto")
    klipy(p, baza, wolna="Left", gest=funkcja, siedzi=False)           # spoczynek, powitanie, gest

Klipy wspólne (nazwy stałe, czyta je swiat/npc_gra): spoczynek (2 s, pętla: oddech), powitanie (1,6 s, raz: machanie
wolną ręką), gest (gest roli, raz; każda postać ma własny). Obrót głowy i tułowia ku graczowi dokłada gra.
Status: propozycja (własne projekty, nie kanon). Konwencje: 1 jednostka = 1 stud, Y w górę, postać patrzy w +Z,
jej LEWA strona to +X; obroty w stopniach: rx < 0 unosi zwisającą rękę albo nogę do przodu, rz > 0 odchyla ją ku +X.
"""
from swiat.postacie import rycerz as _rycerz
from swiat.postacie.biblioteka.postac import Postac

CIALO_TYP = "czlowiek"
WYMIARY = dict(_rycerz.WYMIARY)             # klocki ciała „czlowiek” (EKWIPUNEK.md pkt 1) — tylko odczyt
WZROST = 5.3                                # czubek głowy bez włosów i nakrycia
KLIPY = ("spoczynek", "powitanie", "gest")
PALETA = {"skora": "F2C49C", "skora_cien": "D9A37C", "skora_ciemna": "B9794F", "skora_ciemna_cien": "9A6040",
          "usta": "7A2E2A", "jezyk": "D9534A", "podeszwa": "22150B"}
SLABOSCI = [
    "Rekwizyt to bryły na kościach dłoni (nie osobne akcesorium) — w FBX postaci jest częścią dłoni.",
    "Strój, zarost i ręce to sztywne bryły na kościach: przy dużych ruchach (machanie, gest) lekko się przenikają.",
    "Klipy to szkice (1–2 s), nie gotowa animacja; obrót głowy ku graczowi dokłada dopiero gra (swiat/npc_gra).",
]


def ludzik(id, nazwa, paleta, kolory, wymiary=None, rozstaw_rak=None):
    """Postać R15 na klockach ciała „czlowiek” z paletą wspólną + własną i kolorami klocków ciała."""
    pal = dict(PALETA)
    pal.update(paleta or {})
    w = dict(WYMIARY)
    w.update(wymiary or {})
    p = Postac(id, nazwa, typ="r15", faza=0.05, paleta=pal, wymiary=w, rozstaw_rak=rozstaw_rak)
    p.cialo(kolory)
    return p


# ------------------------------------------------------------------------------------------------ głowa
def twarz(p, oczy="duze", brew="tusz", brew_kat=8, usta="usmiech", skora_cien="skora_cien", rumieniec=True,
          piegi=None, teczowka=None, nos=0.3):
    """Twarz na klocku głowy. oczy: "duze" (prostokąty z błyskiem), "usmiech" (zamknięte łuki), "waskie" (kreski),
    "swiecace" (golem — materiał świecący w kolorze `teczowka`). usta: "usmiech", "kreska", "otwarte", None.
    brew_kat > 0 = wewnętrzne końce brwi wyżej (pogodnie), < 0 = niżej (surowo)."""
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        z = d / 2
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * 0.34
            if oczy == "usmiech":
                p.blok("Oko a " + s, (x - 0.08, 0.1, z + 0.02), (0.2, 0.07, 0.06), "tusz", faza=0.0, rot=(0, 0, 28))
                p.blok("Oko b " + s, (x + 0.08, 0.1, z + 0.02), (0.2, 0.07, 0.06), "tusz", faza=0.0, rot=(0, 0, -28))
            elif oczy == "waskie":
                p.blok("Oko " + s, (x, 0.1, z + 0.02), (0.3, 0.1, 0.06), "tusz", faza=0.0)
            elif oczy == "swiecace":
                p.blok("Oczodol " + s, (x, 0.08, z + 0.01), (0.42, 0.3, 0.06), "tusz", faza=0.0)
                p.blok("Oko " + s, (x, 0.08, z + 0.03), (0.3, 0.18, 0.06), teczowka or "bialy", "swiecacy", faza=0.0)
            else:
                p.blok("Oko " + s, (x, 0.08, z + 0.02), (0.24, 0.36, 0.08), teczowka or "tusz", "polysk", faza=0.03)
                p.blok("Blysk " + s, (x + 0.05, 0.17, z + 0.07), (0.08, 0.1, 0.03), "bialy", faza=0.0)
            if brew:
                p.blok("Brew " + s, (x, 0.4, z + 0.03), (0.4, 0.1, 0.08), brew, "matowy", rot=(0, 0, -zn * brew_kat),
                       faza=0.0)
            if rumieniec:
                p.blok("Policzek " + s, (zn * 0.55, -0.16, z + 0.005), (0.24, 0.13, 0.04), "rumieniec", "matowy",
                       faza=0.0)
            if piegi:
                for i, (dx, dy) in enumerate(((0.0, 0.0), (0.12, 0.07), (-0.1, 0.08))):
                    p.blok("Pieg %s%d" % (s, i), (zn * 0.52 + dx, -0.05 + dy, z + 0.012), (0.06, 0.06, 0.03), piegi,
                           "matowy", faza=0.0)
            p.blok("Ucho " + s, (zn * (w / 2 + 0.07), 0.02, -0.02), (0.14, 0.36, 0.28), skora_cien, "matowy")
        if nos:
            p.blok("Nos", (0, -0.08, z + nos / 2), (0.26, 0.26, nos), skora_cien, "matowy", faza=0.06)
        if usta == "usmiech":
            p.blok("Usta", (0, -0.4, z + 0.02), (0.46, 0.08, 0.05), "usta", faza=0.0)
            for zn in (1, -1):
                p.blok("Kacik " + ("L" if zn > 0 else "P"), (zn * 0.26, -0.35, z + 0.02), (0.08, 0.14, 0.05), "usta",
                       faza=0.0, rot=(0, 0, zn * 25))
        elif usta == "otwarte":
            p.blok("Usta", (0, -0.42, z + 0.02), (0.44, 0.2, 0.05), "usta", faza=0.0)
            p.blok("Zeby", (0, -0.35, z + 0.035), (0.36, 0.06, 0.04), "bialy", faza=0.0)
            p.blok("Jezyk", (0, -0.48, z + 0.035), (0.22, 0.06, 0.04), "jezyk", faza=0.0)
        elif usta == "kreska":
            p.blok("Usta", (0, -0.42, z + 0.02), (0.4, 0.07, 0.05), "usta", faza=0.0)


def wlosy(p, kolor, fryzura="krotkie", jasne=None, wstazka=None):
    """Fryzura: "krotkie" (czapa, grzywka na bok, boki), "czub" (płaski czub do góry), "kucyk" (czapa i kucyk z tyłu),
    "warkocze" (czapa i dwa warkocze po bokach, wstążki), "kok" (czapa i kok na czubku), "wianek" (łysina z wiankiem
    włosów nad uszami i z tyłu)."""
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        z = d / 2
        if fryzura != "wianek":
            p.blok("Wlosy czapa", (0, h / 2 + 0.1, -0.03), (w + 0.1, 0.32, d + 0.08), kolor, "matowy", faza=0.08)
            if jasne:
                p.blok("Wlosy pasmo", (0.15, h / 2 + 0.27, 0.0), (w - 0.6, 0.08, d - 0.4), jasne, "matowy", faza=0.03)
        p.blok("Wlosy tyl", (0, 0.08, -z - 0.06), (w + 0.1, h - 0.3, 0.16), kolor, "matowy", faza=0.05)
        for zn in (1, -1):
            s = "L" if zn > 0 else "P"
            p.blok("Wlosy bok " + s, (zn * (w / 2 + 0.05), 0.32, -0.2), (0.14, 0.62, d - 0.3), kolor, "matowy")
        if fryzura == "krotkie":
            p.klin("Grzywka", (0.28, h / 2 - 0.07, z + 0.06), (0.8, 0.28, 0.18), kolor, "matowy", rot=(0, 0, -12),
                   faza=0.04)
            p.blok("Grzywka nasada", (-0.25, h / 2 - 0.02, z + 0.02), (1.0, 0.16, 0.12), kolor, "matowy", faza=0.03)
        elif fryzura == "czub":
            p.blok("Czub", (0, h / 2 + 0.42, 0.0), (w - 0.1, 0.4, d - 0.15), kolor, "matowy", faza=0.06)
            p.blok("Czub przod", (0, h / 2 + 0.05, z + 0.03), (w - 0.1, 0.2, 0.1), kolor, "matowy", faza=0.03)
        elif fryzura == "kucyk":
            p.blok("Grzywka", (0, h / 2 - 0.04, z + 0.03), (w + 0.06, 0.2, 0.12), kolor, "matowy", rot=(0, 0, 4))
            p.blok("Kucyk gumka", (0, 0.4, -z - 0.2), (0.3, 0.22, 0.2), wstazka or kolor, "matowy", faza=0.03)
            p.blok("Kucyk", (0, -0.1, -z - 0.36), (0.42, 0.95, 0.3), kolor, "matowy", rot=(18, 0, 0), faza=0.08)
        elif fryzura == "warkocze":
            p.blok("Grzywka", (0, h / 2 - 0.04, z + 0.03), (w + 0.06, 0.22, 0.12), kolor, "matowy")
            for zn in (1, -1):
                s = "L" if zn > 0 else "P"
                p.blok("Warkocz " + s, (zn * (w / 2 + 0.16), -0.5, 0.1), (0.3, 1.1, 0.3), kolor, "matowy",
                       rot=(0, 0, zn * 6), faza=0.06)
                p.blok("Wstazka " + s, (zn * (w / 2 + 0.2), -0.98, 0.1), (0.36, 0.16, 0.36), wstazka or kolor,
                       "matowy", faza=0.03)
        elif fryzura == "kok":
            p.blok("Grzywka", (0.2, h / 2 - 0.04, z + 0.03), (w - 0.3, 0.2, 0.12), kolor, "matowy", rot=(0, 0, -6))
            p.blok("Kok", (0, h / 2 + 0.5, -0.25), (0.7, 0.55, 0.7), kolor, "matowy", faza=0.12)
            p.blok("Kok szpilka", (0.1, h / 2 + 0.6, -0.25), (1.0, 0.07, 0.07), wstazka or "zloto", "metal", rot=(0, 30, 20),
                   faza=0.0)


def broda(p, kolor, dl=0.45, szer=None, cien=None):
    """Broda pod klockiem głowy: boki od uszu, podbródek i część zwisająca o długości dl (0 = sam zarost)."""
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        z = d / 2
        szer = szer or (w - 0.2)
        for zn in (1, -1):
            p.blok("Broda bok " + ("L" if zn > 0 else "P"), (zn * (w / 2 - 0.1), -0.32, z - 0.2), (0.24, 0.6, 0.5), kolor,
                   "matowy", faza=0.05)
        p.blok("Broda", (0, -h / 2 + 0.04, z - 0.02), (szer, 0.4, 0.26), kolor, "matowy", faza=0.06)
        if dl > 0:
            p.blok("Broda dol", (0, -h / 2 - dl / 2 + 0.02, z - 0.1), (szer * 0.7, dl, 0.34), cien or kolor, "matowy",
                   faza=0.06)


def wasy(p, kolor, podkrecone=False):
    with p.na("Head", od="srodek"):
        z = p.wymiary("Head")[2] / 2
        for zn in (1, -1):
            s = "L" if zn > 0 else "P"
            p.blok("Was " + s, (zn * 0.24, -0.27, z + 0.07), (0.42, 0.15, 0.12), kolor, "matowy", rot=(0, 0, zn * 14))
            if podkrecone:
                p.blok("Was koniec " + s, (zn * 0.5, -0.14, z + 0.06), (0.12, 0.22, 0.1), kolor, "matowy",
                       rot=(0, 0, zn * -18))


def okulary(p, kolor="tusz", szklo=None):
    """Okulary w prostokątnych oprawkach (same ramki — oczy widać), mostek i zauszniki."""
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        z = d / 2 + 0.09
        for zn in (1, -1):
            s = "L" if zn > 0 else "P"
            x, y = zn * 0.34, 0.09
            for dy in (-0.26, 0.26):
                p.blok("Okular poziom %s%+d" % (s, dy > 0), (x, y + dy, z), (0.5, 0.06, 0.05), kolor, "metal", faza=0.0)
            for dx in (-0.22, 0.22):
                p.blok("Okular pion %s%+d" % (s, dx > 0), (x + dx, y, z), (0.06, 0.58, 0.05), kolor, "metal", faza=0.0)
            if szklo:
                p.blok("Okular szklo " + s, (x, y, z - 0.03), (0.4, 0.48, 0.02), szklo, "polysk", faza=0.0)
            p.blok("Okular zausznik " + s, (zn * (w / 2 + 0.03), y + 0.1, d / 4), (0.05, 0.06, d / 2 + 0.1), kolor,
                   "metal", faza=0.0)
        p.blok("Okular mostek", (0, 0.14, z), (0.2, 0.06, 0.05), kolor, "metal", faza=0.0)


# ------------------------------------------------------------------------------------------------ strój
def buty(p, kolor, jasny=None, cholewa=0.2, okucie=None):
    """Buty na klockach stóp i łydek: podeszwa, czubek, wywinięta cholewa (cholewa = wysokość wywinięcia, 0 = brak)."""
    for s in ("Left", "Right"):
        with p.na(s + "Foot", od="srodek"):
            w, h, d = p.wymiary(s + "Foot")
            p.blok("Podeszwa", (0, -h / 2 + 0.05, 0), (w + 0.06, 0.1, d + 0.06), "podeszwa", "matowy")
            p.blok("Czubek", (0, 0.0, d / 2 - 0.12), (w - 0.08, h - 0.05, 0.3), okucie or jasny or kolor,
                   "metal" if okucie else "matowy")
        if cholewa:
            with p.na(s + "LowerLeg", od="srodek"):
                w, h, d = p.wymiary(s + "LowerLeg")
                p.blok("Cholewa", (0, h / 2 - cholewa / 2, 0), (w + 0.12, cholewa, d + 0.12), jasny or kolor, "matowy")


def pas(p, kolor, klamra="zloto", sakwa=None):
    with p.na("LowerTorso", od="srodek"):
        w, h, d = p.wymiary("LowerTorso")
        p.blok("Pas", (0, 0.04, 0), (w + 0.08, 0.26, d + 0.08), kolor, "matowy")
        if klamra:
            p.blok("Klamra", (0, 0.04, d / 2 + 0.06), (0.34, 0.3, 0.06), klamra, "metal", faza=0.03)
        if sakwa:
            p.blok("Sakwa", (-0.75, -0.2, d / 2 + 0.1), (0.5, 0.5, 0.26), sakwa, "matowy", faza=0.06)


def fartuch(p, kolor, cien=None, szelki=None, kieszen=True, dol=1.1):
    """Fartuch z przodu: napierśnik na tułowiu, płat do kolan na pasie (dol = długość płata pod pasem), szelki."""
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.blok("Fartuch przod", (0, -0.12, z + 0.05), (w - 0.6, h - 0.2, 0.1), kolor, "matowy")
        if kieszen:
            p.blok("Kieszen", (0, -0.36, z + 0.11), (0.7, 0.42, 0.06), cien or kolor, "matowy", faza=0.0)
        if szelki:
            for zn in (1, -1):
                s = "L" if zn > 0 else "P"
                p.blok("Szelka " + s, (zn * 0.55, 0.4, z + 0.06), (0.2, h - 0.75, 0.08), szelki, "matowy", faza=0.0)
                p.blok("Szelka bark " + s, (zn * 0.55, h / 2 + 0.03, 0), (0.2, 0.08, d + 0.08), szelki, "matowy",
                       faza=0.0)
                p.blok("Szelka tyl " + s, (zn * 0.55, 0.05, -z - 0.04), (0.2, h - 0.1, 0.08), szelki, "matowy", faza=0.0)
    with p.na("LowerTorso", od="srodek"):
        w, h, d = p.wymiary("LowerTorso")
        p.blok("Fartuch dol", (0, -dol / 2 - 0.05, d / 2 + 0.1), (w - 0.6, dol + 0.3, 0.1), kolor, "matowy")
        p.blok("Fartuch rabek", (0, -dol - 0.14, d / 2 + 0.11), (w - 0.58, 0.1, 0.11), cien or kolor, "matowy", faza=0.0)


def spodnica(p, kolor, brzeg=None, dl=1.45, szer=0.5, rozciecie=False):
    """Dół szaty albo spódnica na kości bioder: dzwon od pasa w dół (dl = długość, szer = poszerzenie u dołu).
    Sztywna — nogi chowają się pod nią, więc postać w szacie stoi, a nie chodzi."""
    with p.na("LowerTorso", od="srodek"):
        w, h, d = p.wymiary("LowerTorso")
        p.ostroslup("Szata dol", (0, -h / 2 - dl / 2 + 0.05, 0), (w + szer, dl, d + szer + 0.25), kolor, "matowy",
                    gora=(w + 0.1, d + 0.12))
        if brzeg:
            p.blok("Szata brzeg", (0, -h / 2 - dl + 0.12, 0), (w + szer + 0.06, 0.16, d + szer + 0.31), brzeg, "matowy",
                   faza=0.03)
        if rozciecie:
            p.blok("Szata rozciecie", (0, -h / 2 - dl / 2 + 0.05, (d + szer) / 2 + 0.06), (0.16, dl - 0.1, 0.06),
                   brzeg or kolor, "matowy", faza=0.0)


def rekawy(p, kolor, mankiet=None, dlugie=False):
    """Rękaw na ramieniu (bufka u barku) i — przy długich — także na przedramieniu, z mankietem."""
    for s in ("Left", "Right"):
        with p.na(s + "UpperArm", od="srodek"):
            w, h, d = p.wymiary(s + "UpperArm")
            p.blok("Bufka", (0, h / 2 - 0.22, 0), (w + 0.12, 0.46, d + 0.1), kolor, "matowy", faza=0.08)
            if not dlugie and mankiet:
                p.blok("Mankiet", (0, -h / 2 + 0.1, 0), (w + 0.1, 0.2, d + 0.1), mankiet, "matowy")
        if dlugie:
            with p.na(s + "LowerArm", od="srodek"):
                w, h, d = p.wymiary(s + "LowerArm")
                p.blok("Rekaw", (0, 0.04, 0), (w + 0.06, h - 0.08, d + 0.06), kolor, "matowy")
                if mankiet:
                    p.blok("Mankiet", (0, -h / 2 + 0.1, 0), (w + 0.14, 0.2, d + 0.14), mankiet, "matowy")


def piesc(p, strona, kolor="skora"):
    """Zaciśnięta dłoń trzymająca rekwizyt (kciuk z przodu)."""
    with p.na(strona + "Hand", od="srodek"):
        w, h, d = p.wymiary(strona + "Hand")
        p.blok("Piesc", (0, 0, 0), (w + 0.04, h + 0.06, d + 0.04), kolor, faza=0.06)


# ------------------------------------------------------------------------------------------------ klipy
SIEDZI = {"LeftUpperLeg": (-86, 0, 4), "RightUpperLeg": (-86, 0, -4), "LeftLowerLeg": (80, 0, 0),
          "RightLowerLeg": (80, 0, 0)}


def _zera(poza, kosci):
    w = dict(poza)
    for k in kosci:
        w.setdefault(k, (0, 0, 0))
    return w


def klipy(p, baza, wolna="Left", gest=None, siedzi=False, machanie=150):
    """Wspólny zestaw klipów NPC na pozie bazowej `baza` ({kość: (rx, ry, rz)} — ręce z rekwizytem, ręka na biodrze…):
    spoczynek (oddech, lekki ruch wolnej ręki; siedzący macha nogami), powitanie (wolna ręka w górę i trzy machnięcia
    przedramieniem, kiwnięcie głową), gest (funkcja gest(p, baza) → dodaje klip „gest”; bez niej: ukłon głową)."""
    zn = 1 if wolna == "Left" else -1
    baza = dict(baza)
    if siedzi:
        baza.update(SIEDZI)
    start = _zera(baza, ("Head", "UpperTorso", wolna + "UpperArm", wolna + "LowerArm", wolna + "Hand"))

    k = p.klip("spoczynek", 60, petla=True)
    k.poza(0, start)
    k.cykl("UpperTorso", "obrot", (-1.4, 0, 0))
    k.cykl("UpperTorso", "przes", (0, 0.025, 0), faza=0.25)
    k.cykl("Head", "obrot", (1.5, 0, 1.0), faza=0.1)
    k.cykl(wolna + "LowerArm", "obrot", (-2.5, 0, 0), faza=0.2)
    if siedzi:
        k.cykl("LeftLowerLeg", "obrot", (9, 0, 0))
        k.cykl("RightLowerLeg", "obrot", (9, 0, 0), faza=0.5)

    k = p.klip("powitanie", 48, petla=False)
    k.poza(0, start)
    gora = dict(start)
    gora.update({wolna + "UpperArm": (-12, 0, zn * machanie), wolna + "LowerArm": (0, 0, zn * 14),
                 wolna + "Hand": (0, 0, 0), "Head": (-5, 0, -zn * 7), "UpperTorso": (-2, 0, -zn * 3)})
    k.poza(10, gora)
    for f, kat in ((17, -24), (24, 22), (31, -24), (38, 14)):
        k.poza(f, {wolna + "LowerArm": (0, 0, zn * kat)})
    k.poza(38, {wolna + "UpperArm": (-12, 0, zn * machanie), "Head": (-5, 0, -zn * 7), "UpperTorso": (-2, 0, -zn * 3)})
    k.poza(48, start)

    if gest is not None:
        gest(p, start)
    else:
        k = p.klip("gest", 40, petla=False)
        k.poza(0, start)
        k.poza(12, {"Head": (14, 0, 0), "UpperTorso": (6, 0, 0)})
        k.poza(24, {"Head": (10, 0, 0), "UpperTorso": (5, 0, 0)})
        k.poza(40, start)
    brak = [n for n in KLIPY if n not in [kl.nazwa for kl in p.klipy]]
    if brak:
        raise ValueError("%s: brak klipów %s" % (p.id, ", ".join(brak)))
    return start
