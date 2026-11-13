# -*- coding: utf-8 -*-
"""PIES — pet: brązowy kanciasty pies na czterech łapach (ok. 2,2 studa w kłębie), duża klockowa głowa
z ciemniejszym pyskiem, klapnięte uszy, czarny nos, wywieszony język, czerwona obroża ze złotą zawieszką, ogon do góry.

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/pies.py --wyj <folder> --klip idle

Status: propozycja (kanon wyglądu: B&C/Gra/Pety.md — „brązowy, kanciasty”; obraz referencyjny
assets/processed/KeyArt.png — pies biegnący obok Kota-Maga).

Budowa (typ="stwor", własne kości, 1 jednostka = 1 stud, pies patrzy w +Z, jego lewa strona = +X):
- Root > Tulow > {Glowa > {Szczeka, UchoL, UchoP}, LapaPrzodL/P_Gora > _Dol, LapaTylL/P_Gora > _Dol, Ogon};
- `Szczeka` (żuchwa z językiem) to kość dodatkowa względem zamówienia — bez niej pysk nie otworzy się przy
  szczekaniu (sztywne bryły ruszają się tylko z kością);
- obroża siedzi na kości `Glowa` (na szyi), więc kiwa się razem z głową;
- klipy: `idle` (merdanie ogonem, oddech, uszy), `bieg` (galop: przednie łapy razem, tylne razem, tułów faluje),
  `szczek` (przysiad → podskok z otwartym pyskiem → lądowanie).
"""
from swiat.postacie.biblioteka.postac import Postac

ID = "pies"

PALETA = {
    "siersc": "C27532", "siersc_jasna": "E3A866", "siersc_ciemna": "8E4E22",
    "pysk": "7A4120", "nos": "141010", "jezyk": "F06A86", "jezyk_ciemny": "C9435F",
    "obroza": "C7302B", "obroza_ciemna": "8E1E1B", "oko": "1A1210", "gardlo": "7A1A26",
}

# --- wymiary (studs)
KLAB = 2.2                    # wysokość w kłębie = górna ściana tułowia
TUL = (1.3, 1.0, 2.1)         # tułów: szer, wys, dł
Y_TUL = KLAB - TUL[1] / 2     # środek tułowia
GLOWA = (1.5, 1.3, 1.35)      # przerysowana, duża głowa
X_LAP, Z_PRZOD, Z_TYL = 0.42, 0.72, -0.72
GORA_LAPY = 0.8


def zbuduj():
    p = Postac(ID, "Pies", typ="stwor", skala=1.0, faza=0.06, paleta=PALETA)

    # ------------------------------------------------------------------ szkielet
    p.kosc("Tulow", "Root", staw=(0, Y_TUL, 0), czesc=TUL, srodek=(0, 0, 0))
    szyja = (0, KLAB - 0.15, TUL[2] / 2 - 0.15)
    SG = (0, 0.8, 0.55)                                                 # środek głowy względem stawu szyi
    p.kosc("Glowa", "Tulow", staw=szyja, czesc=GLOWA, srodek=SG)
    sg = (szyja[0], szyja[1] + SG[1], szyja[2] + SG[2])                  # środek głowy w układzie modelu
    p.kosc("Szczeka", "Glowa", staw=(0, sg[1] - 0.52, sg[2] + 0.45), czesc=(0.72, 0.2, 0.86),
           srodek=(0, -0.08, 0.52))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Ucho" + s, "Glowa", staw=(zn * 0.66, sg[1] + 0.58, sg[2] - 0.05), czesc=(0.26, 0.85, 0.6),
               srodek=(zn * 0.16, -0.36, 0))
    y_bark = Y_TUL - 0.1
    y_kolano = y_bark - GORA_LAPY + 0.04
    for s, zn in (("L", 1), ("P", -1)):
        for przod, z in (("Przod", Z_PRZOD), ("Tyl", Z_TYL)):
            g, d = "Lapa%s%s_Gora" % (przod, s), "Lapa%s%s_Dol" % (przod, s)
            p.kosc(g, "Tulow", staw=(zn * X_LAP, y_bark, z), czesc=(0.46, GORA_LAPY, 0.5),
                   srodek=(0, -GORA_LAPY / 2 + 0.04, 0))
            p.kosc(d, g, staw=(zn * X_LAP, y_kolano, z), czesc=(0.42, y_kolano, 0.46),
                   srodek=(0, -y_kolano / 2, 0))
    p.kosc("Ogon", "Tulow", staw=(0, KLAB - 0.2, -TUL[2] / 2 + 0.05), czesc=(0.26, 0.9, 0.26),
           srodek=(0, 0.42, 0))

    # ------------------------------------------------------------------ tułów
    with p.na("Tulow", od="srodek"):
        w, h, d = TUL
        p.blok("Tulow", (0, 0, 0), TUL, "siersc")
        # głęboka klatka piersiowa: klin wyższy o 0,15 i szerszy o 0,1 z przodu, opada ku zadowi (nie „stolik”)
        p.klin("Klatka", (0, 0.06, d / 2 - 0.55), (w + 0.1, h + 0.12, 1.2), "siersc", faza=0.06)
        p.blok("Piers", (0, -0.12, d / 2 + 0.02), (0.86, 0.66, 0.1), "siersc_jasna", "matowy", faza=0.03)
        p.blok("Brzuch", (0, -h / 2 - 0.02, 0.1), (0.8, 0.1, 1.3), "siersc_jasna", "matowy", faza=0.03)
        p.blok("Grzbiet", (0, h / 2 + 0.03, -0.15), (0.9, 0.1, 1.5), "siersc_ciemna", "matowy", faza=0.03)
        p.blok("Zad", (0, 0.02, -d / 2 - 0.02), (0.9, 0.7, 0.1), "siersc_ciemna", "matowy", faza=0.03)

    # ------------------------------------------------------------------ głowa
    with p.na("Glowa", od="srodek"):
        w, h, d = GLOWA
        z = d / 2
        p.blok("Glowa", (0, 0, 0), GLOWA, "siersc", faza=0.08)
        p.blok("Czolo", (0, h / 2 + 0.03, -0.05), (1.0, 0.1, 0.9), "siersc_ciemna", "matowy", faza=0.03)
        # pysk (górna szczęka) — ciemniejszy klocek wysunięty do przodu
        # pysk wysunięty o ok. 0,7 przed twarz i obniżony; nos 0,3 × 0,2 na czubku
        p.blok("Pysk", (0, -0.34, z + 0.38), (0.84, 0.46, 0.86), "pysk", "matowy", faza=0.07)
        p.blok("Pysk grzbiet", (0, -0.1, z + 0.2), (0.7, 0.2, 0.5), "siersc", "matowy", faza=0.06)
        p.blok("Nos", (0, -0.16, z + 0.8), (0.32, 0.2, 0.14), "nos", "polysk", faza=0.05)
        p.blok("Nos blysk", (0.07, -0.09, z + 0.875), (0.08, 0.04, 0.02), "bialy", faza=0.0)
        p.blok("Rozdzielenie", (0, -0.36, z + 0.82), (0.05, 0.14, 0.03), "nos", faza=0.0)
        p.blok("Usmiech", (0, -0.5, z + 0.82), (0.5, 0.05, 0.03), "nos", faza=0.0)
        # wnętrze pyska: schowane w żuchwie, widać je dopiero przy otwartym pysku (klip szczek)
        p.blok("Gardlo", (0, -0.6, z + 0.35), (0.6, 0.17, 0.6), "gardlo", "matowy", faza=0.02)
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * 0.36
            p.blok("Bialko " + s, (x, 0.27, z + 0.01), (0.32, 0.4, 0.06), "bialy", "polysk", faza=0.03)
            p.blok("Zrenica " + s, (x - zn * 0.03, 0.24, z + 0.04), (0.24, 0.3, 0.06), "oko", "polysk", faza=0.03)
            p.blok("Blysk " + s, (x - zn * 0.03 + 0.06, 0.32, z + 0.08), (0.07, 0.07, 0.03), "bialy", faza=0.0)
            p.blok("Brew " + s, (zn * 0.38, 0.53, z + 0.03), (0.32, 0.08, 0.08), "siersc_ciemna", "matowy",
                   rot=(0, 0, zn * 7), faza=0.0)
        # szyja + obroża ze złotą zawieszką
        p.blok("Szyja", (0, -0.8, -0.3), (0.9, 0.5, 0.72), "siersc", faza=0.05)
        with p.uklad(pos=(0, -0.76, -0.26), obrot=(-10, 0, 0)):
            p.blok("Obroza", (0, 0, 0), (1.0, 0.3, 0.86), "obroza", "zwykly", faza=0.04)
            p.blok("Obroza brzeg", (0, -0.13, 0), (1.02, 0.05, 0.88), "obroza_ciemna", "matowy", faza=0.0)
            p.walec("Kolko", (0, -0.16, 0.45), (0.14, 0.16, 0.05), "zloto_ciemne", "metal", rot=(90, 0, 0),
                    segm=8, faza=0.0)
            p.blok("Zawieszka", (0, -0.34, 0.47), (0.28, 0.28, 0.07), "zloto", "metal", rot=(0, 0, 45), faza=0.02)

    # ------------------------------------------------------------------ żuchwa i język
    with p.na("Szczeka", od="srodek"):
        p.blok("Zuchwa", (0, 0, 0), (0.72, 0.2, 0.86), "pysk", "matowy", faza=0.05)
        p.blok("Podniebienie", (0, 0.09, 0.02), (0.6, 0.04, 0.72), "jezyk_ciemny", "matowy", faza=0.0)
        with p.uklad(pos=(0.12, 0.02, 0.3), obrot=(-22, 0, -8)):
            p.blok("Jezyk", (0, -0.16, 0.0), (0.3, 0.42, 0.08), "jezyk", "polysk", faza=0.03)
            p.blok("Jezyk bruzda", (0, -0.12, 0.045), (0.04, 0.26, 0.02), "jezyk_ciemny", faza=0.0)

    # ------------------------------------------------------------------ uszy (klapnięte)
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Ucho" + s, od="srodek"):
            p.blok("Ucho", (0, 0, 0), (0.26, 0.85, 0.6), "siersc_ciemna", "matowy", rot=(0, 0, zn * 10), faza=0.05)
            p.blok("Ucho koniec", (zn * 0.04, -0.4, 0), (0.28, 0.14, 0.5), "pysk", "matowy", rot=(0, 0, zn * 10),
                   faza=0.03)

    # ------------------------------------------------------------------ łapy
    for s in ("L", "P"):
        for przod in ("Przod", "Tyl"):
            g, dd = "Lapa%s%s_Gora" % (przod, s), "Lapa%s%s_Dol" % (przod, s)
            kol = "siersc" if przod == "Przod" else "siersc_ciemna"
            with p.na(g, od="srodek"):
                p.blok("Lapa gora", (0, 0, 0), (0.46, GORA_LAPY, 0.5), kol)
            with p.na(dd, od="srodek"):
                hh = p.wymiary(dd)[1]
                p.blok("Lapa dol", (0, 0.06, 0), (0.42, hh - 0.12, 0.46), "siersc")
                p.blok("Stopa", (0, -hh / 2 + 0.11, 0.06), (0.5, 0.22, 0.6), "siersc_jasna", "matowy")
                for i in (-1, 1):
                    p.blok("Palec", (i * 0.12, -hh / 2 + 0.1, 0.37), (0.06, 0.14, 0.04), "siersc_ciemna", faza=0.0)

    # ------------------------------------------------------------------ ogon (do góry, lekko do tyłu)
    with p.na("Ogon", obrot=(-35, 0, 0)):
        p.blok("Ogon", (0, 0.36, 0), (0.26, 0.78, 0.26), "siersc", faza=0.05)
        with p.uklad(pos=(0, 0.72, 0), obrot=(40, 0, 0)):                # końcówka zakrzywiona ku głowie
            p.blok("Ogon zagiecie", (0, 0.12, 0), (0.26, 0.3, 0.26), "siersc", faza=0.05)
            p.blok("Ogon koniec", (0, 0.32, 0.0), (0.3, 0.22, 0.3), "siersc_jasna", "matowy", faza=0.05)

    # punkty zaczepienia dla gry: korzeń (podążanie), czubek głowy (tabliczka z imieniem)
    p.zaczep("RootAttachment", "Tulow", (0, -Y_TUL, 0))
    p.zaczep("GlowaAttachment", "Glowa", (SG[0], SG[1] + GLOWA[1] / 2, SG[2]))

    _klipy(p)
    p.ustaw_poze_renderu("idle", 8)
    return p


SLABOSCI = [
    "Kości psa nie są R15 — klipy importuje się na własny rig (nie testowane w Studio).",
    "Sztywne bryły na kościach: przy galopie łapy przenikają brzuch, a przy szczeknięciu szyja chowa się w obrożę.",
    "Bieg to szkic galopu (16 klatek) z jedną fazą lotu; brak kurzu i śladów.",
]


# ---------------------------------------------------------------------- animacje
LAPY = [("Przod", "L"), ("Przod", "P"), ("Tyl", "L"), ("Tyl", "P")]


def _klipy(p):
    # --- idle: merdanie ogonem, oddech, przechylanie głowy, uszy
    k = p.klip("idle", 60, petla=True)
    k.cykl("Ogon", "obrot", (0, 0, 32), czestosc=6)
    k.cykl("Ogon", "obrot", (6, 0, 0), czestosc=2, faza=0.25)
    k.cykl("Tulow", "przes", (0, 0.025, 0), czestosc=2)              # oddech bez kanału skali
    k.cykl("Tulow", "obrot", (0, 0, 2.5), czestosc=6, faza=0.5)       # biodra kiwają się z merdaniem
    k.cykl("Glowa", "obrot", (3, 0, 6), czestosc=1, faza=0.1)
    k.cykl("UchoL", "obrot", (0, 0, 6), czestosc=2)
    k.cykl("UchoP", "obrot", (0, 0, -6), czestosc=2, faza=0.1)
    k.cykl("Szczeka", "obrot", (4, 0, 0), czestosc=4, srodek=(6, 0, 0))   # dyszenie

    # --- bieg: galop (przednie łapy razem, tylne razem z przesunięciem), 16 klatek
    k = p.klip("bieg", 16, petla=True)
    for przod, s in LAPY:
        g, d = "Lapa%s%s_Gora" % (przod, s), "Lapa%s%s_Dol" % (przod, s)
        f = 0.0 if przod == "Przod" else 0.5
        f += 0.06 if s == "L" else 0.0                                    # lekko rozstrzelone łapy
        if przod == "Przod":
            k.cykl(g, "obrot", (-45, 0, 0), faza=f)                          # wymach do przodu
            k.cykl(d, "obrot", (32, 0, 0), faza=f + 0.25, srodek=(28, 0, 0))   # podgięcie przy powrocie
        else:
            k.cykl(g, "obrot", (42, 0, 0), faza=f)                           # odbicie do tyłu
            k.cykl(d, "obrot", (-30, 0, 0), faza=f - 0.25, srodek=(-24, 0, 0))
    k.cykl("Tulow", "obrot", (9, 0, 0), faza=0.0)                            # kołyska galopu
    # faza lotu: tułów najwyżej (+0,3), gdy przednie łapy są pod brzuchem z tyłu, a tylne zebrane pod spodem
    k.cykl("Tulow", "przes", (0, 0.18, 0), faza=0.5, czestosc=1, srodek=(0, 0.12, 0))
    k.cykl("Glowa", "obrot", (-8, 0, 0), faza=0.1, srodek=(-6, 0, 0))
    k.cykl("UchoL", "obrot", (-25, 0, 18), faza=0.35, srodek=(-20, 0, 15))
    k.cykl("UchoP", "obrot", (-25, 0, -18), faza=0.35, srodek=(-20, 0, -15))
    k.cykl("Ogon", "obrot", (-12, 0, 8), faza=0.5, srodek=(-35, 0, 0))
    k.cykl("Szczeka", "obrot", (5, 0, 0), czestosc=2, srodek=(8, 0, 0))

    # --- szczek: przysiad → podskok z otwartym pyskiem → lądowanie (30 klatek)
    k = p.klip("szczek", 30, petla=True)
    k.klucz(0, "Tulow", przes=(0, 0, 0), obrot=(0, 0, 0))
    k.klucz(6, "Tulow", przes=(0, -0.18, 0), obrot=(6, 0, 0))
    k.klucz(12, "Tulow", przes=(0, 0.55, 0), obrot=(-10, 0, 0))
    k.klucz(18, "Tulow", przes=(0, 0.1, 0), obrot=(-3, 0, 0))
    k.klucz(22, "Tulow", przes=(0, -0.1, 0), obrot=(3, 0, 0))
    k.klucz(30, "Tulow", przes=(0, 0, 0), obrot=(0, 0, 0))
    for przod, s in LAPY:
        g, d = "Lapa%s%s_Gora" % (przod, s), "Lapa%s%s_Dol" % (przod, s)
        zn = 1 if przod == "Przod" else -1
        k.poza(0, {g: (0, 0, 0), d: (0, 0, 0)})
        k.poza(6, {g: (zn * -14, 0, 0), d: (zn * 26, 0, 0)})                  # przysiad: łapy się uginają
        k.poza(12, {g: (zn * -26, 0, 0), d: (zn * 16, 0, 0)})                 # w powietrzu: łapy do przodu / tyłu
        k.poza(18, {g: (zn * -6, 0, 0), d: (zn * 6, 0, 0)})
        k.poza(22, {g: (zn * -10, 0, 0), d: (zn * 18, 0, 0)})                # amortyzacja
        k.poza(30, {g: (0, 0, 0), d: (0, 0, 0)})
    k.poza(0, {"Glowa": (0, 0, 0), "Szczeka": (0, 0, 0), "Ogon": (0, 0, 0)})
    k.poza(6, {"Glowa": (8, 0, 0), "Szczeka": (0, 0, 0), "Ogon": (-10, 0, 0)})
    k.poza(10, {"Glowa": (-18, 0, 0), "Szczeka": (40, 0, 0), "Ogon": (8, 0, 18)})   # HAU! pysk szeroko
    k.poza(15, {"Glowa": (-14, 0, 0), "Szczeka": (36, 0, 0), "Ogon": (8, 0, -18)})
    k.poza(20, {"Glowa": (-4, 0, 0), "Szczeka": (4, 0, 0), "Ogon": (4, 0, 14)})
    k.poza(25, {"Glowa": (2, 0, 0), "Szczeka": (0, 0, 0), "Ogon": (0, 0, -10)})
    k.poza(30, {"Glowa": (0, 0, 0), "Szczeka": (0, 0, 0), "Ogon": (0, 0, 0)})
    for s, zn in (("L", 1), ("P", -1)):
        k.poza(0, {"Ucho" + s: (0, 0, 0)})
        k.poza(8, {"Ucho" + s: (10, 0, -zn * 8)})
        k.poza(12, {"Ucho" + s: (-30, 0, zn * 40)})                           # uszy fruwają w podskoku
        k.poza(20, {"Ucho" + s: (6, 0, -zn * 10)})
        k.poza(30, {"Ucho" + s: (0, 0, 0)})
