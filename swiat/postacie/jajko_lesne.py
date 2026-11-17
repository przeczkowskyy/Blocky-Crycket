# -*- coding: utf-8 -*-
"""JAJKO LEŚNE i INKUBATOR LEŚNY — próba „jajka i pety” (swiat/pety_proba, 17.11.2026; status: propozycja).

Dwa modele w jednym module:
  • jajko_lesne     — gładkie jajko z elipsoid (ok. 2,85 studa z kiełkiem, 1,7 szerokości), kremowe w zielone plamki
                      mchu, z kiełkiem na czubku. Czubek (kopułka) to osobna kość — odskakuje przy pęknięciu; pod nim
                      świecąca elipsoida „Wnetrze” (w grze klient barwi ją kolorem rzadkości wyklutego peta — widać ją
                      dopiero po odskoczeniu czubka).
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
from swiat.postacie.pety_lesne import jajko_gladkie, klipy_jajka, tablica_szans

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


WYS = 2.54            # wysokość skorupki (bez kiełka)
SZER = 1.7            # najszersze miejsce
WYS_CZUBKA = WYS - CZUBEK_Y
# plamki mchu: (kość, azymut °, y od spodu, średnica, kolor) — wtopione kulki (pety_lesne.jajko_gladkie);
# na czubku tylko powyżej szwu (ok. 2,1), niżej czubek jest schowany w skorupce
CETKI = (("dol", 20, 0.85, 0.44, "mech"), ("dol", -35, 0.35, 0.3, "mech"), ("dol", 100, 0.75, 0.4, "mech"),
         ("dol", -95, 1.0, 0.32, "mech"), ("dol", 180, 0.65, 0.44, "mech"), ("dol", 55, 1.5, 0.3, "mech_ciemny"),
         ("dol", -150, 1.7, 0.28, "mech"), ("gora", -30, 2.22, 0.28, "mech_ciemny"), ("gora", 140, 2.3, 0.24, "mech"))


def _jajko(p, kosc_jajka, kosc_czubka, k=1.0):
    """Bryły jajka na dwóch kościach (staw kości jajka = środek spodu; skala k). Od 17.11 (wieczór) gładkie jajko
    z elipsoid (pety_lesne.jajko_gladkie) — wcześniej schodki z klocków przypominały ul."""
    jajko_gladkie(p, kosc_jajka, kosc_czubka, k, CZUBEK_Y, WYS, SZER, "skorupka", cetki=CETKI)
    with p.na(kosc_czubka, od="staw"):
        p.blok("Kielek", (0, k * (WYS_CZUBKA + 0.12), 0), (k * 0.1, k * 0.3, k * 0.1), "kielek", "matowy", faza=0.0)
        for zn in (1, -1):
            p.blok("Kielek listek", (zn * k * 0.16, k * (WYS_CZUBKA + 0.24), 0), (k * 0.32, k * 0.05, k * 0.18), "kielek",
                   "matowy", rot=(0, 0, zn * 25), faza=0.0)


def _klipy_jajka(p, kosc_jajka, kosc_czubka, z_peknieciem=True):
    klipy_jajka(p, kosc_jajka, kosc_czubka, z_peknieciem)


def jajko():
    p = Postac(ID, "Jajko leśne", typ="stwor", skala=1.0, faza=0.06, paleta=PALETA)
    p.kosc("Jajko", "Root", staw=(0, 0, 0), czesc=(1.7, CZUBEK_Y, 1.7), srodek=(0, CZUBEK_Y / 2, 0))
    p.kosc("Czubek", "Jajko", staw=(0, CZUBEK_Y, 0), czesc=(1.5, WYS_CZUBKA, 1.5), srodek=(0, WYS_CZUBKA / 2, 0))
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
    tablica_szans(p, "Tablica", [k for k, _ in PASKI], [s for _, s in PASKI], "tablica", "rama", "papier")
    p.zaczep("RootAttachment", "Podstawa", (0, -0.5, 0))
    p.zaczep("GlowaAttachment", "Czubek", (0, 1.4 * k, 0))
    _klipy_jajka(p, "Jajko", "Czubek", z_peknieciem=False)
    p.ustaw_poze_renderu("spoczynek", 0)
    return p


def zbuduj():
    return [jajko(), inkubator()]


SLABOSCI = [
    "Jajko z trzech elipsoid: na styku skorupki i czubka widać delikatny szew (to też linia pęknięcia).",
    "Inkubator to podgląd: w grze gniazdo stoi na mapie lasu-pasa, a napisy na tablicy dokłada SurfaceGui.",
]
