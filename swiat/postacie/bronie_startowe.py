# -*- coding: utf-8 -*-
"""BRONIE STARTOWE — trzy skromne bronie, które gracz dostaje po wyborze klasy (polecenie Pawła 2026-11-18).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/bronie_startowe.py --wyj <folder>

Wzór: arkusz Pawła (Higgsfield, dolny rząd = widoki dla modelarza) — `assets/raw/BronieStartowe_arkusz.jpg`.
Ikony do ekwipunku to górny rząd tego arkusza (assets/processed/WeaponClub.png, WeaponStaff.png, WeaponSlingshot.png).

    kij_z_kamieniem  — Wojownik (Warrior): krzywy kij z szarym kamieniem przywiązanym sznurkiem na krzyż
    kostur_spiralny  — Mag (Mage): sękaty kostur, u góry drewno zwija się w spiralę, jeden zielony listek
    proca            — Zwiadowca (Scout): proca z rozwidlonej gałęzi, skórzana owijka, czerwona guma, kamyk w skórce

Konwencja jak w bronie.py (zaczep RightGripAttachment): (0, 0, 0) = środek dłoni, rękojeść wzdłuż Y, głowica w +Y,
lico do przodu (+Z), X = bok. Poniżej dłoni (−Y) wszystko cieńsze niż 1 stud w osi X.
W grze te same bryły stają się częściami Roblox (biblioteka/roblox_klocki.py → tools/studio/deploy_classselect.py):
broń trzyma figura rasy na ekranie wyboru rasy. Status: propozycja (nie kanon).
"""
import math

from swiat.postacie.biblioteka.postac import Akcesorium, manekin_r15, klip_trzymanie_r15, klip_spoczynek_r15

FILMY = []
EKSPORT_MODELI = False
SLABOSCI = [
    "Spirala kostura to łańcuch walców i kul — w Roblox ok. 40 części; na ekranie wyboru to nie przeszkadza.",
    "Sznurek na kamieniu to płaskie paski na licu i plecach kamienia, nie prawdziwe owinięcie.",
]

ZACZEP = "RightGripAttachment"

PALETA = {
    "drewno": "8E5A2E", "drewno_jasne": "B9824C", "drewno_ciemne": "5E3A1A",
    "drewno_procy": "C79A5E", "drewno_procy_cien": "9C7442",
    "kamien": "B3B6C2", "kamien_cien": "8A87A6", "kamien_jasny": "D7DAE2",
    "sznurek": "D2AE73", "sznurek_cien": "A88552",
    "skora": "8A5530", "skora_ciemna": "5C3820",
    "guma": "D23A2E", "lisc": "5DBE47", "kamyk": "6E5A4C",
}

# Opis dla gry / ekwipunku: id przedmiotu w src/shared/Items.luau i klasa, która dostaje broń na start.
PRZEDMIOTY = [
    {"id": "kij_z_kamieniem", "nazwa": "Kij z kamieniem", "klasa": "Warrior", "item": "StarterClub"},
    {"id": "kostur_spiralny", "nazwa": "Kostur spiralny", "klasa": "Mage", "item": "StarterStaff"},
    {"id": "proca", "nazwa": "Proca", "klasa": "Scout", "item": "StarterSlingshot"},
]
for _p in PRZEDMIOTY:
    _p.update({"slot": "Weapon", "kategoria": "Weapons", "zaczep": ZACZEP})


def _akc(id, ikona_obrot=(0, 0, -40), chwyt=None):
    nazwa = next(p["nazwa"] for p in PRZEDMIOTY if p["id"] == id)
    return Akcesorium(id, nazwa, zaczep=ZACZEP, typ="Bron", paleta=PALETA, ikona_obrot=ikona_obrot, chwyt=chwyt)


def _odcinek(a, nazwa, p0, p1, gr, kolor, z=0.0, kula=True):
    """Walec od p0 do p1 (płaszczyzna XY, na głębokości z) + kula w p1, żeby zgięcia nie miały szczelin."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    dl = math.hypot(dx, dy)
    rz = math.degrees(math.atan2(-dx, dy))
    a.walec(nazwa, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, z), (gr, dl, gr), kolor, "matowy", rot=(0, 0, rz),
            segm=8, faza=0.0)
    if kula:
        a.kula(nazwa + " staw", (p1[0], p1[1], z), (gr, gr, gr), kolor, "matowy", segm=8)


# --------------------------------------------------------------------------- 1. kij z kamieniem (Wojownik)
def kij_z_kamieniem():
    """Krzywy kij z sękiem; na górze szary, kanciasty kamień przywiązany sznurkiem na krzyż (z przodu i z tyłu),
    pod kamieniem trzy zwoje sznurka, nad kamieniem wystaje ścięty koniec kija."""
    a = _akc("kij_z_kamieniem", ikona_obrot=(0, 0, -40))
    # rękojeść: lekko krzywa, ciemniejsza u dołu
    a.walec("Uchwyt", (0, -0.1, 0), (0.3, 1.3, 0.3), "drewno", "matowy", segm=8)
    a.walec("Koniec", (0.02, -0.8, 0), (0.26, 0.14, 0.26), "drewno_ciemne", "matowy", segm=8, faza=0.0)
    with a.uklad(pos=(0, 0.5, 0), obrot=(0, 0, 6)):
        a.ostroslup("Trzon", (0, 0.55, 0), (0.32, 1.1, 0.32), "drewno", "matowy", gora=(0.42, 0.42), faza=0.04)
        a.blok("Slad kory", (0.17, 0.3, 0.0), (0.04, 0.5, 0.12), "drewno_ciemne", "matowy", faza=0.0)
    # sęk po boku (ścięta gałązka)
    with a.uklad(pos=(-0.14, 0.25, 0), obrot=(0, 0, 50)):
        a.walec("Sek", (0, 0.14, 0), (0.17, 0.3, 0.17), "drewno", "matowy", segm=8, faza=0.0)
        a.walec("Sek ciecie", (0, 0.3, 0), (0.13, 0.03, 0.13), "drewno_jasne", "matowy", segm=8, faza=0.0)
    yk = 1.95                                                     # środek kamienia
    with a.uklad(pos=(0.13, 0, 0), obrot=(0, 0, 6)):
        # kamień: dwa przenikające się klocki dają ośmiokątny, „ciosany” zarys
        a.blok("Kamien", (0, yk, 0), (1.25, 0.86, 0.82), "kamien", "matowy", rot=(0, 8, 0), faza=0.1)
        a.blok("Kamien 2", (0, yk, 0), (0.86, 1.15, 0.74), "kamien", "matowy", rot=(0, 8, 0), faza=0.1)
        a.blok("Kamien cien", (0.05, yk - 0.3, 0.0), (1.1, 0.36, 0.78), "kamien_cien", "matowy", rot=(0, 8, 0),
               faza=0.08)
        a.blok("Kamien blask", (-0.24, yk + 0.28, 0.25), (0.28, 0.12, 0.3), "kamien_jasny", "matowy", faza=0.03)
        # kij przechodzi przez wiązanie i wystaje nad kamieniem
        a.blok("Czubek kija", (-0.02, yk + 0.66, 0), (0.34, 0.42, 0.34), "drewno", "matowy", rot=(0, 10, 0), faza=0.04)
        a.blok("Czubek ciecie", (-0.02, yk + 0.88, 0), (0.28, 0.04, 0.28), "drewno_jasne", "matowy", rot=(0, 10, 0),
               faza=0.0)
        # sznurek na krzyż: lico (+Z) i plecy (−Z)
        for zn in (1, -1):
            for i, rz in enumerate((38, -38)):
                a.blok("Sznurek %s%d" % ("p" if zn > 0 else "t", i), (0, yk, zn * 0.44), (0.1, 1.35, 0.05), "sznurek",
                       "matowy", rot=(0, 0, rz), faza=0.0)
        # zwoje pod kamieniem
        for i, y in enumerate((yk - 0.5, yk - 0.62, yk - 0.74)):
            a.walec("Zwoj %d" % i, (-0.02, y, 0), (0.46, 0.09, 0.46), "sznurek" if i != 1 else "sznurek_cien",
                    "matowy", segm=8, faza=0.0)
        a.blok("Koniec sznurka", (0.16, yk - 0.9, 0.2), (0.06, 0.28, 0.05), "sznurek", "matowy", rot=(0, 0, -12),
               faza=0.0)
    return a


# --------------------------------------------------------------------------- 2. kostur spiralny (Mag)
def kostur_spiralny():
    """Cienki, sękaty kostur: na dole cienki, ku górze grubszy; u góry drewno skręca w prawo, przechodzi łukiem nad
    głową kostura i zwija się do środka w spiralę. Z boku gałązka z jednym zielonym listkiem. Bez kamienia i blasku."""
    a = _akc("kostur_spiralny", ikona_obrot=(0, 0, -35), chwyt="drzewce")
    # drzewce: kilka lekko łamanych odcinków (sękate), od cienkiego dołu do grubszej góry
    pkt = [(0.0, -1.9), (0.04, -1.1), (-0.03, -0.3), (0.02, 0.5), (-0.04, 1.3), (0.03, 2.05), (0.0, 2.6)]
    for i in range(len(pkt) - 1):
        gr = 0.22 + 0.13 * i / (len(pkt) - 2)
        _odcinek(a, "Drzewce %d" % i, pkt[i], pkt[i + 1], gr, "drewno")
    a.kula("Stopka", (0, -1.9, 0), (0.22, 0.22, 0.22), "drewno_ciemne", "matowy", segm=8)
    a.walec("Sek", (-0.02, 0.9, 0.0), (0.36, 0.13, 0.36), "drewno_ciemne", "matowy", segm=8, faza=0.0)
    # spirala: z wierzchołka drzewca w prawo (−X — prawa strona patrząc na lico) i do góry, łukiem nad środkiem,
    # w dół po drugiej stronie i do środka; promień maleje, grubość też
    cx, cy = -0.18, 3.35
    x0, y0 = pkt[-1]
    r0 = math.hypot(x0 - cx, y0 - cy)
    f0 = math.atan2(y0 - cy, x0 - cx)
    # kierunek: od dołu po stronie −X w górę → obrót zgodny z ruchem wskazówek zegara patrząc na +Z?
    # f maleje: (dół) → strona −X? Liczymy wprost: zaczynamy przy f0 ≈ −80° i zmniejszamy kąt (−80 → −180 → −270…),
    # czyli punkt idzie najpierw w stronę −X i w górę, potem nad środek (+90° = −270°) i w dół po stronie +X.
    kroki, obrot = 22, 1.55 * 2 * math.pi
    poprz = (x0, y0)
    for k in range(1, kroki + 1):
        u = k / kroki
        f = f0 - obrot * u
        r = r0 * (1.0 - 0.78 * u)
        p = (cx + r * math.cos(f), cy + r * math.sin(f))
        gr = 0.35 - 0.16 * u
        _odcinek(a, "Spirala %d" % k, poprz, p, gr, "drewno" if k % 5 else "drewno_jasne")
        poprz = p
    # gałązka z listkiem (strona +X, niżej spirali)
    with a.uklad(pos=(0.04, 2.2, 0), obrot=(0, 0, -55)):
        a.walec("Galazka", (0, 0.2, 0), (0.1, 0.4, 0.1), "drewno", "matowy", segm=6, faza=0.0)
        with a.uklad(pos=(0, 0.48, 0), obrot=(0, 0, 25)):
            a.kula("Lisc", (0, 0.14, 0), (0.28, 0.48, 0.08), "lisc", "polysk", segm=8)
            a.blok("Lisc zylka", (0, 0.12, 0.035), (0.025, 0.32, 0.02), "drewno_jasne", "matowy", faza=0.0)
    return a


# --------------------------------------------------------------------------- 3. proca (Zwiadowca)
def proca():
    """Proca z rozwidlonej gałęzi: rękojeść owinięta skórą, dwa ramiona w kształcie Y z czerwonymi owijkami na
    końcach, czerwona guma opada do skórki z kamykiem (przed licem)."""
    a = _akc("proca", ikona_obrot=(0, 0, -30))
    a.walec("Uchwyt", (0, 0.0, 0), (0.3, 1.5, 0.3), "drewno_procy", "matowy", segm=8)
    a.walec("Stopka", (0, -0.78, 0), (0.32, 0.08, 0.32), "drewno_procy_cien", "matowy", segm=8, faza=0.0)
    for i, (y, rz) in enumerate(((-0.45, 10), (-0.22, -8), (0.0, 10), (0.22, -8), (0.42, 8))):
        a.blok("Owijka %d" % i, (0, y, 0), (0.36, 0.13, 0.36), "skora" if i % 2 else "skora_ciemna", "matowy",
               rot=(0, 0, rz), faza=0.02)
    a.kula("Rozwidlenie", (0, 0.78, 0), (0.36, 0.36, 0.32), "drewno_procy", "matowy", segm=8)
    konce = []
    for zn in (1, -1):                                          # +X i −X
        p0, p1 = (zn * 0.06, 0.78), (zn * 0.62, 1.95)
        _odcinek(a, "Ramie %s" % ("l" if zn > 0 else "p"), p0, p1, 0.27, "drewno_procy", kula=False)
        a.walec("Ramie koniec %s" % ("l" if zn > 0 else "p"), (p1[0], p1[1] + 0.02, 0), (0.25, 0.06, 0.25),
                "drewno_procy_cien", "matowy", segm=8, faza=0.0)
        # czerwone owijki pod końcem ramienia (pochylone jak ramię)
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        rz = math.degrees(math.atan2(-dx, dy))
        for j, t in enumerate((0.78, 0.86)):
            a.walec("Guma owijka %s%d" % ("l" if zn > 0 else "p", j), (p0[0] + dx * t, p0[1] + dy * t, 0),
                    (0.31, 0.07, 0.31), "guma", "polysk", rot=(0, 0, rz), segm=8, faza=0.0)
        konce.append((p0[0] + dx * 0.82, p0[1] + dy * 0.82))
    # guma: z obu ramion do skórki, która wisi przed licem (+Z), lekko poniżej rozwidlenia
    sk = (0.0, 1.05, 0.34)
    for i, (x, y) in enumerate(konce):
        d = (sk[0] - x, sk[1] - y, sk[2] - 0.12)
        dl = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
        rz = math.degrees(math.atan2(d[0], -d[1]))              # oś Y paska: od skórki w górę do ramienia
        rx = math.degrees(math.asin(-d[2] / dl))
        a.blok("Guma %d" % i, ((x + sk[0]) / 2, (y + sk[1]) / 2, (0.12 + sk[2]) / 2), (0.07, dl, 0.05), "guma",
               "polysk", rot=(rx, 0, rz), faza=0.0)
    a.blok("Skorka", sk, (0.36, 0.22, 0.12), "skora_ciemna", "matowy", faza=0.03)
    a.kula("Kamyk", (sk[0], sk[1] + 0.02, sk[2] + 0.08), (0.2, 0.2, 0.18), "kamyk", "matowy", segm=8)
    return a


BUDOWNICZE = [kij_z_kamieniem, kostur_spiralny, proca]


def akcesoria():
    return [f() for f in BUDOWNICZE]


def przymiarka(a):
    """Szary manekin R15 z jedną bronią w prawej dłoni (poza „trzymanie”)."""
    p = manekin_r15("przym_" + a.id, "Przymiarka: " + a.nazwa, klipy=False)
    klip_spoczynek_r15(p)
    klip_trzymanie_r15(p)
    p.zaloz(a)
    p.ustaw_poze_renderu("trzymanie", 0)
    return p


def zbuduj():
    akc = akcesoria()
    return [przymiarka(a) for a in akc] + akc
