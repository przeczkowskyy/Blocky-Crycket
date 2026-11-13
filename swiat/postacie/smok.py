# -*- coding: utf-8 -*-
"""SMOK — pet: mały czerwony kanciasty smok (ok. 2,6 studa wysokości ze skrzydłami w górze).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/smok.py --wyj <folder> --klip idle_lot

Status: propozycja (kanon: B&C/Gra/Pety.md — „mały, czerwony, kanciasty”; obraz referencyjny
assets/processed/KeyArt.png — mały czerwono-pomarańczowy smok z błoniastymi skrzydłami).

Budowa (typ="stwor", własne kości, jedna sztywna siatka na kość):
- Root (na ziemi, bez brył) > Tulow > {Szyja > Glowa > Szczeka; SkrzydloL1 > SkrzydloL2; SkrzydloP1 > SkrzydloP2;
  Ogon1 > Ogon2 > Ogon3; LapaPL, LapaPP (przednie), LapaTL, LapaTP (tylne)};  L = lewa = +X, P = prawa = −X;
- przerysowane proporcje: głowa prawie tak duża jak tułów, krótkie łapy, małe skrzydła, ogon z kolcem-grotem;
- skrzydła mają błonę w płaszczyźnie „rozpiętość × wysokość” (widać ją z przodu i z tyłu — czytelna sylwetka
  w miniaturze), w spoczynku uniesione i lekko odchylone do tyłu;
- twarz z brył: żółte oczy z pionową źrenicą i odblaskiem, brwi, nozdrza, kły, język w szczęce (widoczny przy
  otwarciu pyska w klipie „zioniecie”).

Klipy: idle_lot (unosi się w miejscu i macha skrzydłami), lot (pochylony do przodu, szybsze machanie),
zioniecie (odchylenie głowy, wyrzut do przodu z otwartym pyskiem — sam ruch, płomień/cząsteczki dorobić w grze).
"""
import math

from swiat.postacie.biblioteka.postac import Postac, macierz_obrotu, razy_wektor

ID = "smok"

PALETA = {
    "smok": "E0402C", "smok_ciemny": "A3261B", "smok_jasny": "F2643A",
    "brzuch": "FFC23F", "brzuch_ciemny": "EE9A26",
    "blona": "F58B3A", "blona_ciemna": "D9662A",
    "rog": "F8E2AE", "oko_zolte": "FFD21F", "jezyk": "F06E86", "pysk": "5A1214",
}

# --- wymiary (studs, układ modelu: Y w górę, przód +Z, lewa +X)
TULOW_STAW = (0.0, 0.8, 0.0)
TULOW = (1.05, 0.86, 1.2)
SZYJA_STAW = (0.0, 1.08, 0.42)
GLOWA_STAW = (0.0, 1.32, 0.6)
SZCZEKA_STAW_REL = (0.0, 0.14, 0.38)            # względem stawu głowy
SKRZ_STAW = (0.44, 1.12, -0.12)                 # lewe; prawe = lustro
SKRZ_ROT = (0.0, 25.0, 24.0)                    # spoczynek lewego: uniesione (rz) i odchylone do tyłu (ry)
SKRZ_S = 1.4                                    # skrzydła ×1,4 względem pierwszej wersji (rozpiętość ok. 3,6 studa)
SKRZ_L1o, SKRZ_L2o = 0.64, 0.86                 # długości w układzie skrzydła przed skalą
SKRZ_L1, SKRZ_L2 = SKRZ_L1o * SKRZ_S, SKRZ_L2o * SKRZ_S
ZAWIS = 1.2                                     # wysokość zawisu (przesunięcie tułowia w górę w klipach lotu)
# ogon: punkty osi (staw Ogon1, Ogon2, Ogon3, koniec) — zawija się w lewo (+X) i zadziera koniec do góry,
# żeby grot był widoczny w kadrze 3/4 i z boku
OGON = ((0.0, 0.72, -0.48), (0.1, 0.58, -1.0), (0.5, 0.52, -1.32), (0.92, 0.7, -1.3))
OGON_PRZEKROJ = ((0.52, 0.44), (0.38, 0.33), (0.27, 0.24))     # (szer, wys) segmentów ogona
LAPY = {"LapaPL": (0.34, 0.46, 0.34), "LapaPP": (-0.34, 0.46, 0.34),
        "LapaTL": (0.38, 0.5, -0.32), "LapaTP": (-0.38, 0.5, -0.32)}


def _lustro_rot(rot, zn):
    """Obrót odbity względem płaszczyzny YZ (dla zn = −1): (rx, ry, rz) -> (rx, −ry, −rz)."""
    return (rot[0], zn * rot[1], zn * rot[2])


def _plus(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def _minus(a, b):
    return tuple(a[i] - b[i] for i in range(3))


def _kierunek(a, b):
    """(rx, ry, długość): obrót (kolejność Ry·Rx), który kieruje oś +Z z punktu a do punktu b."""
    d = _minus(b, a)
    poziom = math.hypot(d[0], d[2])
    return (-math.degrees(math.atan2(d[1], poziom)), math.degrees(math.atan2(d[0], d[2])),
            math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2))


def zbuduj():
    p = Postac(ID, "Smok", typ="stwor", skala=1.0, faza=0.05, paleta=PALETA)

    # ------------------------------------------------------------------ szkielet
    p.kosc("Tulow", "Root", TULOW_STAW, czesc=TULOW, srodek=(0, 0, 0))
    p.kosc("Szyja", "Tulow", SZYJA_STAW, czesc=(0.62, 0.55, 0.55), srodek=(0, 0.2, 0.08))
    p.kosc("Glowa", "Szyja", GLOWA_STAW, czesc=(1.26, 0.96, 1.0), srodek=(0, 0.5, 0.15))
    p.kosc("Szczeka", "Glowa", _plus(GLOWA_STAW, SZCZEKA_STAW_REL), czesc=(0.84, 0.2, 0.62), srodek=(0, -0.08, 0.28))
    for strona, zn in (("L", 1.0), ("P", -1.0)):
        s1 = (zn * SKRZ_STAW[0], SKRZ_STAW[1], SKRZ_STAW[2])
        R = macierz_obrotu(*_lustro_rot(SKRZ_ROT, zn))
        s2 = _plus(s1, razy_wektor(R, (zn * SKRZ_L1, 0.0, 0.0)))
        p.kosc("Skrzydlo" + strona + "1", "Tulow", s1, czesc=(SKRZ_L1, 0.16, 0.16), dl=0.3)
        p.kosc("Skrzydlo" + strona + "2", "Skrzydlo" + strona + "1", s2, czesc=(SKRZ_L2, 0.14, 0.14), dl=0.3)
    for i, (w, h) in enumerate(OGON_PRZEKROJ):
        dl_ = _kierunek(OGON[i], OGON[i + 1])[2]
        p.kosc("Ogon%d" % (i + 1), "Ogon%d" % i if i else "Tulow", OGON[i], czesc=(w, h, dl_),
               srodek=tuple(0.5 * v for v in _minus(OGON[i + 1], OGON[i])), dl=0.25)
    for n, st in LAPY.items():
        p.kosc(n, "Tulow", st, czesc=(0.32, 0.4, 0.34), srodek=(0, -0.2, 0), dl=0.25)

    # ------------------------------------------------------------------ tułów
    with p.na("Tulow"):
        w, h, d = TULOW
        p.blok("Tulow", (0, 0, 0), TULOW, "smok", faza=0.1)
        # jaśniejszy brzuch: płyta z przodu + spód, z poziomymi pasami łusek
        p.blok("Brzuch przod", (0, -0.04, d / 2 + 0.02), (0.72, 0.7, 0.06), "brzuch", "matowy", faza=0.03)
        p.blok("Brzuch spod", (0, -h / 2 - 0.02, 0.1), (0.7, 0.06, 0.95), "brzuch", "matowy", faza=0.02)
        for i, y in enumerate((0.16, -0.06, -0.28)):
            p.blok("Pas brzucha %d" % i, (0, y, d / 2 + 0.055), (0.62, 0.05, 0.03), "brzuch_ciemny", "matowy",
                   faza=0.0)
        p.blok("Pas grzbietu", (0, h / 2 + 0.015, -0.05), (0.34, 0.04, 1.0), "smok_ciemny", faza=0.0)
        # kolce grzbietowe
        for i, z in enumerate((0.3, -0.05, -0.4)):
            p.ostroslup("Kolec grzbietu %d" % i, (0, h / 2 - 0.02 + 0.13, z), (0.08, 0.26, 0.3), "brzuch",
                        gora=(0.0, 0.0), przes_gory=(0.0, -0.1))

    # ------------------------------------------------------------------ szyja
    with p.na("Szyja", od="srodek"):
        p.blok("Szyja", (0, 0, 0), (0.62, 0.55, 0.55), "smok", faza=0.06)
        p.blok("Szyja brzuch", (0, -0.04, 0.29), (0.42, 0.42, 0.04), "brzuch", "matowy", faza=0.0)

    # ------------------------------------------------------------------ głowa (układ: staw głowy)
    with p.na("Glowa"):
        cz = (0, 0.5, 0.15)                     # środek czaszki
        W, H, D = 1.26, 0.96, 1.0
        zf = cz[2] + D / 2                      # przednia ściana czaszki (0,65)
        p.blok("Czaszka", cz, (W, H, D), "smok", faza=0.1)
        # pysk (górna szczęka) — wystaje do przodu
        zp = zf + 0.5                           # przód pyska
        p.blok("Pysk", (0, 0.29, zf + 0.22), (0.86, 0.42, 0.56), "smok", faza=0.08)
        p.blok("Pysk grzbiet", (0, 0.5, zf + 0.16), (0.56, 0.06, 0.4), "smok_jasny", faza=0.0)
        for zn in (1, -1):
            p.blok("Nozdrze", (zn * 0.15, 0.44, zp + 0.01), (0.1, 0.05, 0.04), "pysk", "matowy", faza=0.0)
            # uśmiech: dwie kreski pod kątem ±12° (kąciki w górę), bez czarnej krechy przez cały pysk
            p.blok("Usmiech", (zn * 0.17, 0.13, zp - 0.02), (0.36, 0.05, 0.06), "tusz", faza=0.0, rot=(0, 0, zn * 12))
        # jeden mały kieł (zadziornie, ale wesoło)
        p.ostroslup("Kiel", (0.2, 0.08, zp - 0.04), (0.1, 0.1, 0.06), "bialy", "polysk", rot=(180, 0, 0), gora=(0.0, 0.0))
        # wnętrze paszczy (widać przy otwarciu)
        p.blok("Paszcza", (0, 0.13, zf + 0.12), (0.72, 0.08, 0.5), "pysk", "matowy", faza=0.0)
        # oczy: duże żółte z pionową źrenicą
        ye = 0.73
        for zn in (1, -1):
            x = zn * 0.3
            # oko jak u psa: białko, żółta tęczówka 0,35, czarna źrenica 0,2 i odblask
            p.blok("Bialko", (x, ye, zf + 0.01), (0.42, 0.44, 0.06), "bialy", "polysk", faza=0.03)
            p.blok("Teczowka", (x - zn * 0.02, ye - 0.02, zf + 0.035), (0.35, 0.35, 0.04), "oko_zolte", "polysk",
                   faza=0.02)
            p.blok("Zrenica", (x - zn * 0.03, ye - 0.03, zf + 0.055), (0.2, 0.22, 0.04), "tusz", "polysk", faza=0.0)
            p.blok("Blysk", (x - zn * 0.03 + 0.05, ye + 0.04, zf + 0.075), (0.07, 0.07, 0.03), "bialy", faza=0.0)
            p.blok("Brew", (zn * 0.32, ye + 0.22, zf + 0.03), (0.3, 0.07, 0.1), "smok_ciemny",
                   rot=(0, 0, zn * 4), faza=0.0)
            # rogi: kanciaste, zagięte do tyłu
            with p.uklad(pos=(zn * 0.36, cz[1] + H / 2 - 0.04, cz[2] - 0.2), obrot=(-38, 0, -zn * 10)):
                p.ostroslup("Rog", (0, 0.27, 0), (0.24, 0.54, 0.26), "rog", gora=(0.0, 0.0), przes_gory=(0.0, -0.06))
            # płetwy-uszy po bokach
            with p.uklad(pos=(zn * (W / 2 + 0.02), cz[1] + 0.05, cz[2] - 0.15), obrot=(0, 0, -zn * 70)):
                p.ostroslup("Ucho", (0, 0.15, 0), (0.24, 0.32, 0.06), "smok_ciemny", gora=(0.0, 0.06),
                            przes_gory=(0.0, 0.0))
        # kolec na potylicy (grzebień schodzi na kark)
        with p.uklad(pos=(0, cz[1] + 0.12, cz[2] - D / 2), obrot=(-100, 0, 0)):
            p.ostroslup("Kolec potylicy", (0, 0.1, 0), (0.07, 0.2, 0.22), "brzuch", gora=(0.0, 0.0))
        # grzebień na czubku głowy
        for i, (z, hh) in enumerate(((cz[2] + 0.05, 0.22), (cz[2] - 0.25, 0.18))):
            p.ostroslup("Grzebien %d" % i, (0, cz[1] + H / 2 + hh / 2 - 0.02, z), (0.07, hh, 0.22), "brzuch",
                        gora=(0.0, 0.0), przes_gory=(0.0, -0.06))

    # ------------------------------------------------------------------ żuchwa (układ: staw szczęki)
    with p.na("Szczeka"):
        p.blok("Zuchwa", (0, -0.07, 0.33), (0.8, 0.2, 0.66), "smok", faza=0.06)
        p.blok("Zuchwa spod", (0, -0.18, 0.28), (0.6, 0.04, 0.5), "brzuch", "matowy", faza=0.0)
        p.blok("Jezyk", (0, 0.04, 0.26), (0.42, 0.04, 0.4), "jezyk", "matowy", faza=0.0)

    # ------------------------------------------------------------------ skrzydła
    for strona, zn in (("L", 1.0), ("P", -1.0)):
        rot = _lustro_rot(SKRZ_ROT, zn)
        with p.na("Skrzydlo" + strona + "1", obrot=rot), p.uklad(skala=SKRZ_S):
            p.blok("Ramie", (zn * SKRZ_L1o / 2, 0, 0), (SKRZ_L1o + 0.12, 0.16, 0.16), "smok_ciemny", faza=0.04)
            p.blok("Blona 1", (zn * (SKRZ_L1o / 2 + 0.03), -0.23, 0), (SKRZ_L1o - 0.02, 0.44, 0.06), "blona",
                   "matowy", faza=0.02)
            p.ostroslup("Blona 1 zab", (zn * 0.36, -0.45, 0), (0.52, 0.24, 0.06), "blona", "matowy",
                        rot=(180, 0, 0), gora=(0.0, 0.06), przes_gory=(zn * 0.12, 0.0))
        with p.na("Skrzydlo" + strona + "2", obrot=rot), p.uklad(skala=SKRZ_S):
            with p.uklad(obrot=_lustro_rot((0, 0, 14), zn)):
                p.blok("Palec", (zn * SKRZ_L2o / 2, 0, 0), (SKRZ_L2o + 0.06, 0.13, 0.13), "smok_ciemny", faza=0.04)
                p.ostroslup("Pazur skrzydla", (zn * (SKRZ_L2o + 0.1), 0, 0), (0.12, 0.2, 0.12), "rog",
                            rot=(0, 0, -zn * 90), gora=(0.0, 0.0))
                p.blok("Blona 2", (zn * 0.24, -0.17, 0), (0.48, 0.34, 0.06), "blona", "matowy", faza=0.02)
                p.ostroslup("Blona 2 zab", (zn * 0.22, -0.34, 0), (0.42, 0.2, 0.06), "blona", "matowy",
                            rot=(180, 0, 0), gora=(0.0, 0.06), przes_gory=(zn * 0.1, 0.0))
                # koniec błony: trójkąt zwężający się ku pazurowi
                p.ostroslup("Blona 2 koniec", (zn * 0.66, -0.17, 0), (0.34, 0.36, 0.06), "blona", "matowy",
                            rot=(0, 0, -zn * 90), gora=(0.0, 0.06), przes_gory=(0.0, 0.0))
                p.blok("Zebro", (zn * 0.48, -0.16, 0.0), (0.05, 0.32, 0.08), "blona_ciemna", "matowy", faza=0.0)

    # ------------------------------------------------------------------ ogon z kolcem
    for i, (w, h) in enumerate(OGON_PRZEKROJ):
        rx, ry, L = _kierunek(OGON[i], OGON[i + 1])
        with p.na("Ogon%d" % (i + 1), obrot=(rx, ry, 0)):          # w tym układzie +Z biegnie wzdłuż ogona
            p.blok("Ogon%d" % (i + 1), (0, 0, L / 2), (w, h, L + 0.12), "smok", faza=0.06 - 0.01 * i)
            p.blok("Ogon spod %d" % (i + 1), (0, -h / 2 - 0.015, L / 2), (w * 0.62, 0.04, L), "brzuch", "matowy",
                   faza=0.0)
            if i < 2:
                p.ostroslup("Kolec ogona %d" % (i + 1), (0, h / 2 + 0.09 - 0.01 * i, L * 0.45),
                            (0.07, 0.22 - 0.04 * i, 0.24 - 0.03 * i), "brzuch", gora=(0, 0), przes_gory=(0, -0.08))
            else:
                # grot-kolec na końcu: pionowy płaski romb (widać go z boku i w kadrze 3/4)
                with p.uklad(pos=(0, 0, L + 0.02), obrot=(-25, 0, 0)):
                    p.ostroslup("Grot", (0, 0, 0.17), (0.1, 0.34, 0.52), "smok_ciemny", rot=(90, 0, 0),
                                gora=(0.0, 0.0))
                    p.ostroslup("Grot nasada", (0, 0, -0.06), (0.1, 0.12, 0.52), "smok_ciemny", rot=(-90, 0, 0),
                                gora=(0.0, 0.0))

    # ------------------------------------------------------------------ łapy (krótkie, z pazurami)
    for n, (x, y, z) in LAPY.items():
        tyl = n.startswith("LapaT")
        zn = 1.0 if x > 0 else -1.0
        with p.na(n):
            if tyl:
                p.blok("Udo", (zn * 0.02, -0.04, 0), (0.36, 0.42, 0.46), "smok", faza=0.06)
            p.blok("Noga", (0, -0.22 if not tyl else -0.3, 0.02), (0.3, 0.36, 0.3), "smok", faza=0.05)
            p.blok("Stopa", (0, -y + 0.07, 0.08), (0.34, 0.14, 0.42), "smok_ciemny", faza=0.04)
            for i, dx in enumerate((-0.11, 0.0, 0.11)):
                p.ostroslup("Pazur %d" % i, (dx, -y + 0.05, 0.33), (0.07, 0.1, 0.08), "rog",
                            rot=(90, 0, 0), gora=(0.0, 0.0))

    # ------------------------------------------------------------------ klipy
    # punkty zaczepienia dla gry: korzeń, czubek głowy (tabliczka z imieniem), pysk (płomień zionięcia)
    p.zaczep("RootAttachment", "Tulow", tuple(-v for v in TULOW_STAW))
    p.zaczep("GlowaAttachment", "Glowa", (0, 0.5 + 0.48, 0.15))
    p.zaczep("PyskAttachment", "Glowa", (0, 0.25, 0.65 + 0.52))

    _klipy(p)
    p.ustaw_poze_renderu("idle_lot", 6)
    return p


SLABOSCI = [
    "Kości smoka nie są R15 — klipy importuje się na własny rig (nie testowane w Studio).",
    "Zianie to sam ruch (otwarty pysk); płomień dorobić w grze (ParticleEmitter na PyskAttachment).",
    "Błona skrzydeł to płaskie płyty — z boku skrzydło jest cienką kreską.",
]


def _skrzydla(k, amp, czest, srodek_rz=0.0, faza=0.0):
    """Machanie: L1 i L2 (z opóźnieniem — „bicz”), prawe lustrzanie."""
    for strona, zn in (("L", 1.0), ("P", -1.0)):
        k.cykl("Skrzydlo" + strona + "1", "obrot", (0, 0, zn * amp), czestosc=czest, faza=faza,
               srodek=(0, 0, zn * srodek_rz))
        k.cykl("Skrzydlo" + strona + "2", "obrot", (0, 0, zn * amp * 0.6), czestosc=czest, faza=faza - 0.08)


def _klipy(p):
    # --- idle_lot: unosi się w miejscu, spokojne machanie skrzydłami (pętla 1,6 s)
    k = p.klip("idle_lot", 48, petla=True)
    k.cykl("Tulow", "przes", (0, 0.15, 0), czestosc=2, faza=0.5, srodek=(0, ZAWIS, 0))   # w górę przy machnięciu w dół
    k.cykl("Tulow", "obrot", (3, 0, 0), czestosc=1, faza=0.25)
    _skrzydla(k, 32, 2, srodek_rz=4, faza=0.25)
    k.cykl("Glowa", "obrot", (-4, 0, 3), czestosc=1, faza=0.1)
    for i, n in enumerate(("Ogon1", "Ogon2", "Ogon3")):
        k.cykl(n, "obrot", (0, 10 + 4 * i, 0), czestosc=1, faza=-0.12 * i)
        k.cykl(n, "obrot", (5, 0, 0), czestosc=2, faza=0.1 - 0.1 * i, srodek=(-6, 0, 0))
    for n in ("LapaPL", "LapaPP"):                                          # łapy podkulone w locie
        k.cykl(n, "obrot", (6, 0, 0), czestosc=2, faza=0.35, srodek=(-25, 0, 0))
    for n in ("LapaTL", "LapaTP"):
        k.cykl(n, "obrot", (5, 0, 0), czestosc=2, faza=0.4, srodek=(35, 0, 0))

    # --- lot: pochylony do przodu, szybsze i szersze machanie, łapy podkulone (pętla 0,8 s)
    k = p.klip("lot", 24, petla=True)
    k.cykl("Tulow", "obrot", (3, 0, 0), czestosc=2, faza=0.5, srodek=(28, 0, 0))
    k.cykl("Tulow", "przes", (0, 0.1, 0), czestosc=2, faza=0.0, srodek=(0, ZAWIS + 0.15, 0))
    k.cykl("Szyja", "obrot", (2, 0, 0), czestosc=2, faza=0.6, srodek=(-12, 0, 0))
    k.cykl("Glowa", "obrot", (3, 0, 0), czestosc=2, faza=0.7, srodek=(-16, 0, 0))
    _skrzydla(k, 42, 2, srodek_rz=0, faza=0.25)
    for i, n in enumerate(("Ogon1", "Ogon2", "Ogon3")):
        k.cykl(n, "obrot", (6, 0, 0), czestosc=2, faza=0.5 - 0.12 * i, srodek=(-14 + 4 * i, 0, 0))
        k.cykl(n, "obrot", (0, 6, 0), czestosc=1, faza=-0.15 * i)
    for n in ("LapaPL", "LapaPP"):
        k.cykl(n, "obrot", (4, 0, 0), czestosc=2, faza=0.4, srodek=(40, 0, 0))
    for n in ("LapaTL", "LapaTP"):
        k.cykl(n, "obrot", (4, 0, 0), czestosc=2, faza=0.45, srodek=(55, 0, 0))

    # --- zioniecie: zawis, odchylenie głowy (nabranie powietrza), wyrzut do przodu z otwartym pyskiem (1,6 s)
    k = p.klip("zioniecie", 48, petla=False)
    T = (0, 10, 20, 24, 36, 48)               # start, wdech, szczyt, wyrzut, trzymanie, powrót
    zawis = (0, ZAWIS, 0)
    k.klucz(T[0], "Tulow", przes=zawis, obrot=(0, 0, 0))
    k.klucz(T[1], "Tulow", przes=(0, ZAWIS + 0.05, -0.05), obrot=(-8, 0, 0))
    k.klucz(T[2], "Tulow", przes=(0, ZAWIS + 0.1, -0.12), obrot=(-16, 0, 0), wyg="liniowo")
    k.klucz(T[3], "Tulow", przes=(0, ZAWIS - 0.01, 0.18), obrot=(6, 0, 0))
    k.klucz(T[4], "Tulow", przes=(0, ZAWIS - 0.01, 0.15), obrot=(5, 0, 0))
    k.klucz(T[5], "Tulow", przes=zawis, obrot=(0, 0, 0))
    poz = {  # kość: (start, wdech, szczyt, wyrzut, trzymanie)
        # głowa: odchylenie w tył (wdech), potem wyrzut szyi do przodu, a sama głowa lekko w górę — pysk celuje
        # przed siebie (inaczej przy wyrzucie widać czubek głowy zamiast otwartej paszczy)
        "Szyja": ((0, 0, 0), (-10, 0, 0), (-24, 0, 0), (12, 0, 0), (10, 0, 0)),
        "Glowa": ((0, 0, 0), (-10, 0, 0), (-22, 0, 0), (-8, 0, 0), (-6, 0, 0)),
        "Szczeka": ((0, 0, 0), (0, 0, 0), (6, 0, 0), (50, 0, 0), (46, 0, 0)),
        "Ogon1": ((0, 0, 0), (8, 0, 0), (14, 0, 0), (-16, 0, 0), (-12, 0, 0)),
        "Ogon2": ((0, 0, 0), (6, 0, 0), (12, 0, 0), (-14, 0, 0), (-10, 0, 0)),
        "Ogon3": ((0, 0, 0), (4, 0, 0), (10, 0, 0), (-12, 0, 0), (-8, 0, 0)),
        "LapaPL": ((-25, 0, 0), (-30, 0, 0), (-36, 0, 0), (-10, 0, 0), (-14, 0, 0)),
        "LapaPP": ((-25, 0, 0), (-30, 0, 0), (-36, 0, 0), (-10, 0, 0), (-14, 0, 0)),
        "LapaTL": ((35, 0, 0), (28, 0, 0), (20, 0, 0), (42, 0, 0), (38, 0, 0)),
        "LapaTP": ((35, 0, 0), (28, 0, 0), (20, 0, 0), (42, 0, 0), (38, 0, 0)),
    }
    for strona, zn in (("L", 1.0), ("P", -1.0)):
        poz["Skrzydlo" + strona + "1"] = tuple((0, 0, zn * a) for a in (4, 26, 40, -24, -14))
        poz["Skrzydlo" + strona + "2"] = tuple((0, 0, zn * a) for a in (0, 14, 26, -20, -10))
    for kosc, wart in poz.items():
        for i, w in enumerate(wart):
            k.klucz(T[i], kosc, obrot=w, wyg="liniowo" if i == 2 else "gladko")
        k.klucz(T[5], kosc, obrot=wart[0])
