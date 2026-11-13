# -*- coding: utf-8 -*-
"""SLIME (pet) — świecąca błękitno-turkusowa kostka galarety z wesołą buzią.

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/slime.py --wyj <folder> --klip skok

Status: propozycja (kanon wyglądu: B&C/Gra/Pety.md — „świecący, niebieski (cyjanowy), w kształcie kostki”;
obraz referencyjny assets/processed/KeyArt.png — szklista kostka ze ściętymi krawędziami, białym odblaskiem
w rogu i dużymi czarnymi oczami).

Wygląd: jasna, lekko świecąca skorupka (6FF3FF, emisja 0,6) na ściętych krawędziach, ciemniejszy rdzeń galarety
(1FB8C9) na płaskich ścianach — czyta się jak szkło: jasne krawędzie, głębia w środku. Twarz leży na przedniej
ścianie, oczy wystają 0,03.

Animacja BEZ kanału skali (animacje Roblox przenoszą pozycję i obrót kości, skali raczej nie): cała galareta
(z oczami i buzią) to jedna siatka Dol_Geo SKÓROWANA na dwóch kościach — Dol (y = 0) i Gora (y = 2,25); waga
wierzchołka do Gora = jego wysokość / 2,25. Przesunięcie Gora o y −0,6 zgniata kostkę równo od ziemi, +0,4 ją
rozciąga. Poszerzenie = cztery kości boczne (BokL, BokP, Przod, Tyl) z „brzuszkami” schowanymi w bryle, które przy
zgnieceniu wysuwają się o 0,2. Mrugnięcie i zmrużenie = powieki (kość Powieki) zjeżdżają na oczy; krzyk w ataku =
otwarte usta (kość UstaO) wysuwają się zza ściany. Powieki i krzyk jadą z zgnieceniem proporcjonalnie do wysokości.

Szkielet (własny, typ „stwor”):
    Root
    ├── Cialo          staw na ziemi pod środkiem — skok (przes) i przechył (obrót) całej galarety
    │   ├── Dol        cała galareta (siatka Dol_Geo, wagi Dol/Gora)
    │   ├── Gora       góra galarety (bez własnej siatki) — zgniatanie i rozciąganie
    │   ├── Powieki, UstaO               mrugnięcie / krzyk
    │   └── BokL, BokP, Przod, Tyl       brzuszki boczne (poszerzenie przy zgnieceniu)
    └── KroplaL, KroplaP, KroplaT        krople galarety przy podstawie
Klipy: idle (oddech, mrugnięcie), skok (zgniecenie → wybicie → rozciągnięcie → lądowanie), atak (rozpłaszcza się
i strzela do przodu, zmrużone oczy, otwarta buzia).
"""
from swiat.postacie.biblioteka.postac import Postac

ID = "slime"

# Wymiary kostki (studs): szer X, wys Y, głęb Z — lekko przysadzista, żeby wyglądała miękko.
W, H, D = 2.4, 2.25, 2.35
FAZA = 0.26            # mocne ścięcie krawędzi = „zaokrąglona” kostka
YO, YU = H / 2 + 0.24, H / 2 - 0.36      # wysokość oczu i ust (od ziemi, w spoczynku)

PALETA = {
    "skorupka": "6FF3FF",       # jasna, lekko świecąca skorupka (krawędzie)
    "rdzen": "1FB8C9",          # rdzeń galarety na płaskich ścianach
    "rdzen_cien": "1597AE",     # boki i tył rdzenia (trochę ciemniej)
    "odblask": "F2FFFF",        # biały odblask
    "buzia": "13283A",          # wnętrze ust (granatowy tusz)
    "jezyk": "FF7FA8",          # różowy język
}

SLABOSCI = [
    "Galareta jest skórowana na dwóch kościach (Dol, Gora) — import wag do Roblox nie był testowany; brzuszki, "
    "powieki i krzyk to sztywne bryły na własnych kościach.",
    "Brak prawdziwej przezroczystości: szkło udają jasna skorupka i ciemniejszy rdzeń; poświatę w grze dać "
    "materiałem Neon albo PointLight.",
    "Kości petów nie są R15 — klipy importuje się na własny rig (nie testowane w Studio).",
]


def _kropla(p, nazwa, pos, r, kolor="skorupka"):
    """Kropla galarety: kulka + ścięty szpic do góry (łezka), z białym błyskiem."""
    x, y, z = pos
    p.kula(nazwa + " kulka", (x, y, z), r, kolor, "poswiata", segm=8)
    p.stozek(nazwa + " szpic", (x, y + r * 0.62, z), (r * 0.62, r * 0.75, r * 0.62), kolor, "poswiata", segm=8)
    p.blok(nazwa + " blysk", (x - r * 0.18, y + r * 0.12, z + r * 0.47), (r * 0.18, r * 0.24, 0.03),
           "odblask", "swiecacy", faza=0.0)


def zbuduj():
    p = Postac(ID, "Slime", typ="stwor", skala=1.0, faza=0.05, paleta=PALETA)

    # --- szkielet
    p.kosc("Cialo", "Root", staw=(0, 0, 0), dl=0.6)
    p.kosc("Dol", "Cialo", staw=(0, 0, 0), czesc=(W, H, D), srodek=(0, H / 2, 0), dl=0.8)
    p.kosc("Gora", "Cialo", staw=(0, H, 0), dl=0.5)
    p.kosc("Powieki", "Cialo", staw=(0, YO, D / 2), dl=0.3)
    p.kosc("UstaO", "Cialo", staw=(0, YU, D / 2), dl=0.3)
    boki = {"BokL": ((W / 2, H / 2, 0), (1, 0, 0)), "BokP": ((-W / 2, H / 2, 0), (-1, 0, 0)),
            "Przod": ((0, H / 2 - 0.62, D / 2), (0, 0, 1)), "Tyl": ((0, H / 2, -D / 2), (0, 0, -1))}
    for n, (st, _) in boki.items():
        p.kosc(n, "Cialo", staw=st, dl=0.3)
    krople = {"KroplaL": (1.55, 0.16, 0.75, 0.30), "KroplaP": (-1.45, 0.13, 0.95, 0.24),
              "KroplaT": (0.9, 0.12, -1.45, 0.22)}
    for n, (x, y, z, r) in krople.items():
        p.kosc(n, "Root", staw=(x, 0, z), dl=0.25)
    p.skoruj("Dol", "Gora", 0.0, H)                      # waga do Gora = wysokość / H (równe zgniecenie od ziemi)

    # --- galareta z twarzą (układ: środek kostki)
    with p.na("Dol", od="srodek"):
        p.blok("Galareta", (0, 0, 0), (W, H, D), "skorupka", "poswiata", faza=FAZA)
        sx, sy, sz = W - 2 * FAZA + 0.06, H - 2 * FAZA + 0.06, D - 2 * FAZA + 0.06
        p.blok("Rdzen przod", (0, 0, D / 2 + 0.01), (sx, sy, 0.02), "rdzen", "poswiata", faza=0.0)
        p.blok("Rdzen tyl", (0, 0, -D / 2 - 0.01), (sx, sy, 0.02), "rdzen_cien", "poswiata", faza=0.0)
        for zn in (1, -1):
            p.blok("Rdzen bok", (zn * (W / 2 + 0.01), 0, 0), (0.02, sy, sz), "rdzen_cien", "poswiata", faza=0.0)
        p.blok("Wierzch", (0, H / 2 + 0.01, 0), (sx, 0.02, sz), "rdzen", "poswiata", faza=0.0)
        # jeden ukośny odblask w lewym górnym rogu przodu (od widza) — znak stylu Glossy Ink
        zf = D / 2 + 0.03
        p.blok("Odblask", (-W / 2 + FAZA + 0.34, H / 2 - FAZA - 0.24, zf), (0.66, 0.15, 0.03), "odblask",
               "swiecacy", rot=(0, 0, 40), faza=0.0)
        p.blok("Odblask kropka", (-W / 2 + FAZA + 0.76, H / 2 - FAZA - 0.04, zf), (0.13, 0.13, 0.03), "odblask",
               "swiecacy", faza=0.0)
        p.blok("Babel 1", (W / 2 + 0.03, 0.3, -0.45), (0.04, 0.16, 0.16), "odblask", "poswiata", faza=0.0)
        p.blok("Babel 2", (-W / 2 - 0.03, 0.35, 0.4), (0.04, 0.12, 0.12), "odblask", "poswiata", faza=0.0)
        # oczy na przedniej ścianie (wystają 0,03) — zgniatają się razem z galaretą
        yo, yu, zp = YO - H / 2, YU - H / 2, D / 2 + 0.02
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * 0.44
            p.walec("Oko " + s, (x, yo, zp + 0.015), (0.46, 0.03, 0.74), "tusz", "polysk", rot=(90, 0, 0),
                    faza=0.0, segm=12)
            p.walec("Blysk " + s, (x - 0.07, yo + 0.15, zp + 0.04), (0.18, 0.02, 0.24), "odblask", "swiecacy",
                    rot=(90, 0, 0), faza=0.0, segm=8)
            p.walec("Blysk maly " + s, (x + 0.1, yo - 0.18, zp + 0.04), (0.09, 0.02, 0.09), "odblask", "swiecacy",
                    rot=(90, 0, 0), faza=0.0, segm=8)
        # buzia: otwarty uśmiech z językiem
        p.ostroslup("Usta", (0, yu - 0.08, zp + 0.01), (0.86, 0.4, 0.03), "buzia", "polysk", rot=(0, 0, 180),
                    gora=(0.38, 0.03), faza=0.02)
        p.walec("Jezyk", (0.05, yu - 0.16, zp + 0.03), (0.32, 0.02, 0.18), "jezyk", "zwykly", rot=(90, 0, 0),
                faza=0.0, segm=8)

    # --- brzuszki boczne: schowane 0,02 pod ścianą, przy zgnieceniu wysuwają się o 0,2
    for n, (st, (nx, _, nz)) in boki.items():
        with p.na(n):
            if nx:
                p.blok("Brzuszek " + n, (-nx * 0.2, 0, 0), (0.36, 0.7, D - 2 * FAZA - 0.1), "skorupka", "poswiata",
                       faza=0.1)
            else:
                p.blok("Brzuszek " + n, (0, 0, -nz * 0.2), (W - 2 * FAZA - 0.1, 0.36 if nz > 0 else 0.7, 0.36),
                       "skorupka", "poswiata", faza=0.1)
    # --- powieki: w spoczynku schowane w bryle nad oczami; mrugnięcie = zjazd w dół i do przodu
    with p.na("Powieki"):
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Powieka " + s, (zn * 0.44, 0.6, -0.3), (0.56, 0.44, 0.04), "rdzen", "poswiata", faza=0.0)
    # --- krzyk w ataku: duża otwarta buzia schowana w bryle, wysuwa się na przód
    with p.na("UstaO"):
        p.ostroslup("Usta krzyk", (0, -0.14, -0.12), (0.92, 0.62, 0.04), "buzia", "polysk", rot=(0, 0, 180),
                    gora=(0.5, 0.04), faza=0.02)
        p.walec("Jezyk krzyk", (0.0, -0.3, -0.095), (0.36, 0.02, 0.2), "jezyk", "zwykly", rot=(90, 0, 0), faza=0.0,
                segm=8)
    # --- krople przy podstawie (własne kości)
    for n, (x, y, z, r) in krople.items():
        with p.na(n):
            _kropla(p, n, (0, r * 0.5, 0), r)

    # ===================================================================== klipy (tylko przes i obrót)
    BRAK, MRUG, MRUZ = (0.0, 0.0), (-0.48, 0.35), (-0.31, 0.35)     # powieki: (y, z) — mrugnięcie / zmrużenie

    def galareta(k, kl, gora=0.0, bok=0.0, powieki=BRAK, krzyk=0.0):
        """gora = przesunięcie góry (− zgniecenie, + rozciągnięcie); bok = wysunięcie brzuszków; powieki/krzyk
        dokładają się do ruchu twarzy, która jedzie z galaretą proporcjonalnie do wysokości."""
        k.klucz(kl, "Gora", przes=(0, gora, 0))
        for n, (st, (nx, _, nz)) in boki.items():
            k.klucz(kl, n, przes=(nx * bok, gora * st[1] / H, nz * bok))
        k.klucz(kl, "Powieki", przes=(0, gora * YO / H + powieki[0], powieki[1]))
        k.klucz(kl, "UstaO", przes=(0, gora * YU / H, krzyk))

    # idle: oddech galarety (niżej-szerzej / wyżej-węziej), mrugnięcie, krople podskakują na zmianę
    k = p.klip("idle", 48, petla=True)
    for kl, g, b, pw in ((0, 0.0, 0.0, BRAK), (12, -0.1, 0.06, BRAK), (24, 0.0, 0.0, BRAK), (31, 0.04, -0.01, BRAK),
                         (33, 0.05, -0.015, MRUG), (35, 0.06, -0.02, BRAK), (48, 0.0, 0.0, BRAK)):
        galareta(k, kl, g, b, pw)
    k.cykl("Cialo", "obrot", (0, 0, 1.5), czestosc=1, faza=0.25)
    k.cykl("KroplaL", "przes", (0, 0.1, 0), czestosc=2, faza=0.0, srodek=(0, 0.1, 0))
    k.cykl("KroplaP", "przes", (0, 0.08, 0), czestosc=2, faza=0.33, srodek=(0, 0.08, 0))
    k.cykl("KroplaT", "przes", (0, 0.08, 0), czestosc=2, faza=0.66, srodek=(0, 0.08, 0))

    # skok: zgniecenie → wybicie (rozciągnięcie) → szczyt → opadanie → lądowanie (zgniecenie) → odbicie
    k = p.klip("skok", 40, petla=True)
    fazy = [  # klatka, góra, brzuszki, skok y, obrót rx, powieki
        (0, 0.0, 0.0, 0.0, 0, BRAK),
        (7, -0.6, 0.2, 0.0, 4, MRUZ),           # przykucnięcie
        (11, 0.4, -0.05, 0.55, -4, BRAK),       # wybicie
        (19, 0.1, 0.0, 2.1, -2, BRAK),          # szczyt
        (26, 0.3, -0.03, 0.6, 3, BRAK),         # opadanie
        (29, -0.6, 0.2, 0.0, 0, MRUZ),          # lądowanie
        (33, 0.15, 0.0, 0.0, -2, BRAK),         # odbicie
        (37, -0.05, 0.03, 0.0, 0, BRAK),
    ]
    for kl, g, b, py, rx, pw in fazy:
        galareta(k, kl, g, b, pw)
        k.klucz(kl, "Cialo", przes=(0, py, 0), obrot=(rx, 0, 0))
    for n, (x, y, z, r) in krople.items():
        dx, dz = (0.25 if x > 0 else -0.25), (0.25 if z > 0 else -0.25)
        k.klucz(0, n, przes=(0, 0, 0))
        k.klucz(9, n, przes=(0, 0, 0))
        k.klucz(17, n, przes=(0, 1.1 * (0.8 + r), 0))
        k.klucz(27, n, przes=(0, 0, 0))
        k.klucz(31, n, przes=(dx, 0.35, dz))
        k.klucz(36, n, przes=(0, 0, 0))

    # atak: rozpłaszcza się (zamach), strzela do przodu, uderza, wraca; oczy zmrużone, buzia otwarta w krzyku
    k = p.klip("atak", 36, petla=False)
    ataki = [  # klatka, góra, brzuszki, przes (x, y, z), obrot, powieki, krzyk (UstaO z)
        (0, 0.0, 0.0, (0, 0, 0), (0, 0, 0), BRAK, 0.0),
        (8, -0.55, 0.2, (0, 0, -0.35), (6, 0, 0), MRUZ, 0.0),
        (12, 0.3, -0.05, (0, 0.35, 1.4), (-8, 0, 0), MRUZ, 0.17),
        (15, -0.3, 0.15, (0, 0.15, 2.0), (-3, 0, 0), MRUZ, 0.17),
        (20, 0.05, 0.0, (0, 0.0, 1.6), (2, 0, 0), MRUZ, 0.17),
        (28, 0.0, 0.0, (0, 0, 0.3), (0, 0, 0), BRAK, 0.0),
        (36, 0.0, 0.0, (0, 0, 0), (0, 0, 0), BRAK, 0.0),
    ]
    for kl, g, b, pr, ob, pw, kr in ataki:
        galareta(k, kl, g, b, pw, kr)
        k.klucz(kl, "Cialo", przes=pr, obrot=ob)

    # punkty zaczepienia dla gry: podążanie, tabliczka z imieniem, efekty
    p.zaczep("RootAttachment", "Cialo", (0, 0, 0))
    p.zaczep("GlowaAttachment", "Gora", (0, 0.05, 0))
    p.zaczep("PyskAttachment", "UstaO", (0, 0, 0.05))

    p.ustaw_poze_renderu("idle", 0)
    return p
