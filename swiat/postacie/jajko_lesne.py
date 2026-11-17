# -*- coding: utf-8 -*-
"""JAJKO LEŚNE i INKUBATOR LEŚNY — próba „jajka i pety” (swiat/pety_proba, 17.11.2026; status: propozycja).

Dwa modele w jednym module:
  • jajko_lesne     — kanciaste jajko (ok. 2,85 studa z kiełkiem, 1,7 szerokości) w kremowe i zielone łaty mchu, z kiełkiem na czubku. Czubek to
                      osobna kość (odskakuje przy pęknięciu); w środku dolnej skorupki leży płytka „Wnetrze” (w grze
                      klient barwi ją kolorem rzadkości wyklutego peta — widać ją dopiero po odskoczeniu czubka).
                      Klipy: spoczynek (lekkie kołysanie, pętla), trzesienie (coraz mocniej, z podskokami),
                      pekniecie (czubek odskakuje i odlatuje).
  • inkubator_lesny — PODGLĄD stanowiska do pokazania ludziom: gniazdo z korzeni i mchu (jak na mapie lasu-pasa,
                      swiat/las_pas/punkty.py, stanowisko_jajka), wielkie jajko (to samo, ×1,8), tablica na dwóch
                      słupkach z pięcioma paskami w kolorach rzadkości (długość paska ~ szansa; napisy i liczby dokłada
                      gra — modele są bez liter) i lampion. W grze gniazdo jest z mapy, a jajko i tablica z tego modułu.

    python -B swiat/postacie/przebuduj.py jajko_lesne --bez-filmow

Kolory rzadkości i szanse pasków są tu tylko do podglądu — w grze liczby i kolory pochodzą z
swiat/pety_proba/ustawienia.json (test pakietu pilnuje, że paski mają te same proporcje).
"""
import math

from swiat.postacie.biblioteka.postac import Postac

ID = "jajko_lesne"

PALETA = {
    "skorupka": "F0DCAE", "skorupka_cien": "DCCDA6", "mech": "6FAE4A", "mech_ciemny": "4C8A35", "kielek": "5DBB4A",
    "wnetrze": "FFF6C8", "drewno": "6B4A2E", "drewno_ciemne": "4A3220", "mech_gniazda": "5E9B3A",
    "tablica": "8A6440", "rama": "4A3220", "papier": "F5EBD2", "lampion": "FFC94A",
    "r_pospolity": "B8C2CC", "r_zwykly": "6BD66B", "r_rzadki": "4FB3FF", "r_epicki": "C27BFF", "r_legendarny": "FFC23D",
}

# podgląd tablicy: szanse jajka leśnego (pospolity → legendarny), kolory rzadkości
PASKI = [("r_pospolity", 0.50), ("r_zwykly", 0.25), ("r_rzadki", 0.15), ("r_epicki", 0.08), ("r_legendarny", 0.02)]
SKALA_INKUBATORA = 1.8
CZUBEK_Y = 1.5        # wysokość pęknięcia (przy skali 1)


WARSTWY_DOLU = (("Spod", 1.0, 0.0, 0.16), ("Dol", 1.42, 0.16, 0.42), ("Brzuch", 1.7, 0.42, 1.1),
                ("Obrecz", 1.62, 1.1, CZUBEK_Y))
WARSTWY_CZUBKA = (("Czubek dol", 1.48, 0.0, 0.36), ("Czubek srodek", 1.22, 0.36, 0.66), ("Czubek gora", 0.88, 0.66, 0.9),
                  ("Szczyt", 0.46, 0.9, 1.04))
WYS_CZUBKA = 1.04
# łaty mchu: ("przod" | "tyl", x, y, szer, wys, połowa szerokości warstwy) albo ("bok", znak, z, y, szer, wys, połowa)
LATY_DOLU = (("przod", 0.3, 0.8, 0.5, 0.34, 0.85), ("przod", -0.42, 0.3, 0.32, 0.2, 0.71), ("bok", 1, -0.25, 0.75, 0.42,
             0.3, 0.85), ("bok", -1, 0.2, 0.95, 0.3, 0.26, 0.85), ("tyl", 0.1, 0.7, 0.48, 0.32, 0.85))
LATY_CZUBKA = (("przod", -0.25, 0.18, 0.44, 0.24, 0.74), ("bok", 1, 0.15, 0.22, 0.38, 0.22, 0.74))


def _laty(p, laty, k, kolor):
    for lata in laty:
        if lata[0] == "bok":
            _, zn, z, y, sz, sy, pol = lata
            p.blok("Lata mchu", (k * zn * (pol + 0.025), k * y, k * z), (k * 0.05, k * sy, k * sz), kolor, "matowy",
                   faza=0.0)
        else:
            strona, x, y, sx, sy, pol = lata
            zn = 1 if strona == "przod" else -1
            p.blok("Lata mchu", (k * x, k * y, k * zn * (pol + 0.025)), (k * sx, k * sy, k * 0.05), kolor, "matowy",
                   faza=0.0)


def _jajko(p, kosc_jajka, kosc_czubka, k=1.0):
    """Bryły jajka na dwóch kościach (układ: staw kości jajka = środek spodu jajka; skala k). Jajko jest wyższe niż
    szersze (1,7 × 2,54), warstwy z małą fazą — z daleka czyta się jako jajko, nie jako tort."""
    with p.na(kosc_jajka, od="staw"):
        for nazwa, szer, y0, y1 in WARSTWY_DOLU:
            p.blok(nazwa, (0, k * (y0 + y1) / 2, 0), (k * szer, k * (y1 - y0), k * szer), "skorupka", faza=0.03 * k)
        p.blok("Wnetrze", (0, k * (CZUBEK_Y - 0.06), 0), (k * 1.3, k * 0.08, k * 1.3), "wnetrze", "swiecacy", faza=0.0)
        _laty(p, LATY_DOLU, k, "mech")
    with p.na(kosc_czubka, od="staw"):
        for nazwa, szer, y0, y1 in WARSTWY_CZUBKA:
            p.blok(nazwa, (0, k * (y0 + y1) / 2, 0), (k * szer, k * (y1 - y0), k * szer), "skorupka", faza=0.03 * k)
        _laty(p, LATY_CZUBKA, k, "mech_ciemny")
        p.blok("Kielek", (0, k * (WYS_CZUBKA + 0.14), 0), (k * 0.1, k * 0.3, k * 0.1), "kielek", "matowy", faza=0.0)
        for zn in (1, -1):
            p.blok("Kielek listek", (zn * k * 0.16, k * (WYS_CZUBKA + 0.26), 0), (k * 0.32, k * 0.05, k * 0.18), "kielek",
                   "matowy", rot=(0, 0, zn * 25), faza=0.0)


def _klipy_jajka(p, kosc_jajka, kosc_czubka, z_peknieciem=True):
    k = p.klip("spoczynek", 60, petla=True)
    k.cykl(kosc_jajka, "obrot", (1.5, 0, 2.5), czestosc=1)
    k.cykl(kosc_czubka, "obrot", (0, 0, 1.2), czestosc=2, faza=0.2)
    if not z_peknieciem:
        return
    k = p.klip("trzesienie", 36, petla=False)
    for f, kat in ((0, 0), (3, 4), (6, -4), (9, 6), (12, -6), (15, 8), (18, -8), (21, 10), (24, -11), (27, 13),
                   (30, -13), (33, 6), (36, 0)):
        k.klucz(f, kosc_jajka, obrot=(0, 0, kat))
    for f, y in ((0, 0), (13, 0), (15, 0.12), (17, 0), (25, 0), (27, 0.16), (29, 0), (36, 0)):
        k.klucz(f, kosc_jajka, przes=(0, y, 0))
    for f, kat in ((0, 0), (20, 0), (22, -5), (24, 4), (26, -6), (28, 5), (30, -4), (36, 0)):
        k.klucz(f, kosc_czubka, obrot=(kat, 0, 0))
    k = p.klip("pekniecie", 18, petla=False)
    k.klucz(0, kosc_czubka, przes=(0, 0, 0), obrot=(0, 0, 0))
    k.klucz(4, kosc_czubka, przes=(0, 0.18, 0), obrot=(-6, 0, 4))
    k.klucz(10, kosc_czubka, przes=(0.5, 1.6, 0.25), obrot=(-40, 30, 25), wyg="liniowo")
    k.klucz(18, kosc_czubka, przes=(1.1, 2.3, 0.5), obrot=(-85, 70, 55))
    k.klucz(0, kosc_jajka, przes=(0, 0, 0))
    k.klucz(3, kosc_jajka, przes=(0, -0.06, 0))
    k.klucz(8, kosc_jajka, przes=(0, 0.03, 0))
    k.klucz(18, kosc_jajka, przes=(0, 0, 0))


def jajko():
    p = Postac(ID, "Jajko leśne", typ="stwor", skala=1.0, faza=0.06, paleta=PALETA)
    p.kosc("Jajko", "Root", staw=(0, 0, 0), czesc=(1.7, CZUBEK_Y, 1.7), srodek=(0, CZUBEK_Y / 2, 0))
    p.kosc("Czubek", "Jajko", staw=(0, CZUBEK_Y, 0), czesc=(1.48, WYS_CZUBKA, 1.48), srodek=(0, WYS_CZUBKA / 2, 0))
    _jajko(p, "Jajko", "Czubek", 1.0)
    p.zaczep("RootAttachment", "Jajko", (0, 0, 0))
    p.zaczep("GlowaAttachment", "Czubek", (0, 1.4, 0))
    _klipy_jajka(p, "Jajko", "Czubek")
    p.ustaw_poze_renderu("spoczynek", 0)
    return p


def inkubator():
    k = SKALA_INKUBATORA
    p = Postac("inkubator_lesny", "Inkubator leśny (podgląd)", typ="stwor", skala=1.0, faza=0.06, paleta=PALETA)
    p.kosc("Podstawa", "Root", staw=(0, 0.5, 0), czesc=(12.0, 0.5, 12.0), srodek=(0, -0.25, 0))
    y_jajka = 0.92
    p.kosc("Jajko", "Podstawa", staw=(0, y_jajka, 0), czesc=(1.7 * k, CZUBEK_Y * k, 1.7 * k),
           srodek=(0, CZUBEK_Y * k / 2, 0))
    p.kosc("Czubek", "Jajko", staw=(0, y_jajka + CZUBEK_Y * k, 0), czesc=(1.48 * k, WYS_CZUBKA * k, 1.48 * k),
           srodek=(0, WYS_CZUBKA / 2 * k, 0))
    p.kosc("Tablica", "Podstawa", staw=(4.3, 0.5, 3.4), czesc=(4.4, 4.4, 0.4), srodek=(0, 2.2, 0))
    # gniazdo jak na mapie (kamienna płyta 12 × 12, sześć korzeni, dno i mech) — tylko podgląd
    with p.na("Podstawa", od="staw"):
        p.blok("Plyta", (0, -0.25, 0), (12.0, 0.5, 12.0), "8F8577", "matowy", faza=0.1)
        for i in range(6):
            a = math.radians(i * 60 + 15)
            p.blok("Korzen gniazda", (3.2 * math.cos(a), 0.65, 3.2 * math.sin(a)), (3.6, 1.3, 1.4), "drewno_ciemne",
                   "matowy", rot=(0, -math.degrees(a) + 90, (-1) ** i * 8), faza=0.15)
        p.blok("Gniazdo dno", (0, 0.15, 0), (4.6, 0.3, 4.6), "drewno", "matowy", faza=0.1)
        p.blok("Mech", (0, 0.36, 0), (3.9, 0.12, 3.9), "mech_gniazda", "matowy", faza=0.04)
        p.blok("Lampion slup", (-5.0, 2.5, 4.6), (0.4, 5.0, 0.4), "drewno_ciemne", faza=0.05)
        p.blok("Lampion ramie", (-4.1, 4.7, 4.6), (2.0, 0.3, 0.3), "drewno_ciemne", faza=0.04)
        p.blok("Lampion", (-3.3, 3.85, 4.6), (0.8, 1.2, 0.8), "lampion", "swiecacy", faza=0.06)
    _jajko(p, "Jajko", "Czubek", k)
    # tablica z paskami szans (długość ~ szansa, z minimum, żeby 2% było widać)
    with p.na("Tablica", od="staw"), p.uklad(obrot=(0, -20, 0)):
        for zn in (1, -1):
            p.blok("Slupek", (zn * 1.9, 1.6, 0), (0.3, 3.2, 0.3), "rama", "matowy", faza=0.05)
        p.blok("Tablica", (0, 2.6, 0), (4.2, 2.8, 0.2), "tablica", "matowy", faza=0.06)
        p.blok("Papier", (0, 2.55, 0.12), (3.7, 2.4, 0.04), "papier", "matowy", faza=0.0)
        p.blok("Daszek", (0, 4.12, 0), (4.6, 0.25, 0.6), "rama", faza=0.05)
        for i, (kolor, szansa) in enumerate(PASKI):
            dl = 0.35 + 2.6 * szansa / PASKI[0][1]
            y = 3.35 - i * 0.42
            p.blok("Pasek szansy", (-1.55 + 0.35 + dl / 2, y, 0.15), (dl, 0.26, 0.04), kolor, "matowy", faza=0.0)
            p.blok("Znak peta", (-1.55 + 0.12, y, 0.15), (0.24, 0.26, 0.04), kolor, "swiecacy", faza=0.0)
    p.zaczep("RootAttachment", "Podstawa", (0, -0.5, 0))
    p.zaczep("GlowaAttachment", "Czubek", (0, 1.4 * k, 0))
    _klipy_jajka(p, "Jajko", "Czubek", z_peknieciem=False)
    p.ustaw_poze_renderu("spoczynek", 0)
    return p


def zbuduj():
    return [jajko(), inkubator()]


SLABOSCI = [
    "Jajko jest schodkowe (cztery warstwy + czubek z czterech) — to styl klocków, nie gładka owalna skorupka.",
    "Inkubator to podgląd: w grze gniazdo stoi na mapie lasu-pasa, a napisy na tablicy dokłada SurfaceGui.",
]
