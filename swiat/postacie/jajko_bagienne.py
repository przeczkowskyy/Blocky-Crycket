# -*- coding: utf-8 -*-
"""JAJKO BAGIENNE i INKUBATOR BAGIENNY — jajko Bagna (próba swiat/pety_proba, 17.11.2026; status: propozycja).

Dwa modele w jednym module:
  • jajko_bagienne     — gładkie jajko z elipsoid (2,7 × 1,8 studa; pety_lesne.jajko_gladkie) w kolorze miętowej
                         wody, w ciemnozielone i turkusowe cętki, z liściem grzybienia i różowym kwiatkiem na czubku.
                         Czubek odskakuje przy pęknięciu; pod nim świecące „Wnetrze” (kolor rzadkości w grze). Klipy jak
                         jajko leśne: spoczynek, trzesienie, pekniecie (pety_lesne.klipy_jajka).
  • inkubator_bagienny — PODGLĄD stanowiska na Pomoście Przybycia Bagna: pomost i kamienna płyta z korzeniami (to stoi
                         na mapie swiat/bagno_pas — w grze tego nie budujemy), na tym **błotne gniazdo z trzcin na
                         czterech palach** (kość Gniazdo), wielkie jajko (×1,7), **latarenka z ognikiem** na wygiętej
                         tyczce (kość Latarnia) i tablica szans z mchem na daszku (kość Tablica). W grze stawiamy kości
                         Gniazdo, Latarnia i Tablica jako stałe bryły, a jajko jako rig z klipami.

    python -B swiat/postacie/przebuduj.py jajko_bagienne --bez-filmow

Pomysł inny niż jajko leśne (zlecenie 17.11): nie przemalowane leśne — gniazdo na palach nad wodą, trzciny, ognik.
Kolory pasków tablicy i szanse tylko do podglądu — w grze z swiat/pety_proba/ustawienia.json.
"""
import math

from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import jajko_gladkie, klipy_jajka, tablica_szans

ID = "jajko_bagienne"

PALETA = {
    "skorupka": "86C6AB", "cetka": "2F6B57", "cetka_jasna": "5FA88D", "grzybien": "4E9A3E", "grzybien_jasny": "79C25E",
    "kwiat": "F59AC0", "kwiat_srodek": "FFE066", "wnetrze": "E8FFF4",
    "pal": "4A3A2A", "pomost": "6E5638", "bloto": "4B3A26", "bloto_jasne": "6A553A", "trzcina": "8DA65A",
    "trzcina_ciemna": "5E7A3A", "palka": "6A4326", "ognik": "C8FF6A", "klatka": "3A2E22",
    "tablica": "5E4A34", "rama": "3A2E22", "papier": "EDE6CF", "mech": "5E8F45",
    "plyta": "7F7A6C", "korzen": "3E2E22", "deska": "5A4A36",
    "r_pospolity": "B8C2CC", "r_zwykly": "6BD66B", "r_rzadki": "4FB3FF", "r_epicki": "C27BFF", "r_legendarny": "FFC23D",
}
PASKI = [("r_pospolity", 0.50), ("r_zwykly", 0.25), ("r_rzadki", 0.15), ("r_epicki", 0.08), ("r_legendarny", 0.02)]

WYS = 2.7
SZER = 1.8
CZUBEK_Y = 1.55
WYS_CZUBKA = WYS - CZUBEK_Y
SKALA_INKUBATORA = 1.7
Y_GNIAZDA = 1.95          # wierzch platformy gniazda (nad korzeniami stanowiska z mapy, których wierzch to ok. 1,8)
Y_JAJKA = Y_GNIAZDA + 0.1  # spód jajka w błocie
# cętki: (kość, azymut °, y od spodu, średnica, kolor) — pety_lesne.jajko_gladkie; czubek widać od ok. 2,22
CETKI = (("dol", 25, 0.9, 0.34, "cetka"), ("dol", -40, 0.4, 0.24, "cetka_jasna"), ("dol", 95, 1.1, 0.3, "cetka"),
         ("dol", -100, 0.7, 0.36, "cetka_jasna"), ("dol", 190, 1.2, 0.3, "cetka"), ("dol", -20, 1.7, 0.26, "cetka"),
         ("dol", 150, 1.9, 0.22, "cetka_jasna"), ("dol", 60, 0.35, 0.2, "cetka"), ("gora", 40, 2.36, 0.24, "cetka"),
         ("gora", -120, 2.42, 0.2, "cetka_jasna"))


def _jajko(p, kosc_jajka, kosc_czubka, k=1.0):
    jajko_gladkie(p, kosc_jajka, kosc_czubka, k, CZUBEK_Y, WYS, SZER, "skorupka", cetki=CETKI)
    with p.na(kosc_czubka, od="staw"):
        y = k * (WYS_CZUBKA + 0.02)
        with p.uklad(pos=(0, y, 0), obrot=(0, 25, 6)):
            p.blok("Lisc grzybienia", (0.05 * k, 0, 0), (k * 0.95, k * 0.05, k * 0.8), "grzybien", "matowy", faza=0.0)
            p.blok("Lisc grzybienia zylka", (0.05 * k, 0.03 * k, 0), (k * 0.06, k * 0.02, k * 0.7), "grzybien_jasny",
                   "matowy", faza=0.0)
            for i in range(4):
                a = math.radians(i * 90 + 45)
                p.blok("Platek", (k * 0.11 * math.cos(a), k * 0.11, k * 0.11 * math.sin(a)), (k * 0.16, k * 0.1, k * 0.16),
                       "kwiat", "matowy", rot=(0, -math.degrees(a), 20), faza=0.0)
            p.blok("Kwiat srodek", (0, k * 0.15, 0), (k * 0.1, k * 0.08, k * 0.1), "kwiat_srodek", "matowy", faza=0.0)


def jajko():
    p = Postac(ID, "Jajko bagienne", typ="stwor", skala=1.0, faza=0.05, paleta=PALETA)
    p.kosc("Jajko", "Root", staw=(0, 0, 0), czesc=(SZER, CZUBEK_Y, SZER), srodek=(0, CZUBEK_Y / 2, 0))
    p.kosc("Czubek", "Jajko", staw=(0, CZUBEK_Y, 0), czesc=(1.6, WYS_CZUBKA, 1.6), srodek=(0, WYS_CZUBKA / 2, 0))
    _jajko(p, "Jajko", "Czubek", 1.0)
    p.zaczep("RootAttachment", "Jajko", (0, 0, 0))
    p.zaczep("GlowaAttachment", "Czubek", (0, WYS_CZUBKA + 0.4, 0))
    klipy_jajka(p, "Jajko", "Czubek")
    p.ustaw_poze_renderu("spoczynek", 0)
    return p


def _gniazdo(p):
    """Błotne gniazdo z trzcin na czterech palach (kość Gniazdo, staw = środek na ziemi stanowiska)."""
    with p.na("Gniazdo", od="staw"):
        for x, z in ((-1.5, -1.5), (1.5, -1.5), (-1.5, 1.5), (1.5, 1.5)):
            p.walec("Pal", (x, Y_GNIAZDA / 2, z), (0.36, Y_GNIAZDA, 0.36), "pal", "matowy", segm=8, faza=0.0)
        p.blok("Platforma", (0, Y_GNIAZDA - 0.1, 0), (4.0, 0.2, 4.0), "pomost", "matowy", faza=0.04)
        p.blok("Platforma skos", (0, Y_GNIAZDA - 0.1, 0), (4.0, 0.2, 4.0), "pomost", "matowy", rot=(0, 45, 0), faza=0.04)
        p.blok("Bloto", (0, Y_GNIAZDA + 0.08, 0), (3.0, 0.2, 3.0), "bloto", "matowy", faza=0.05)
        p.blok("Bloto skos", (0, Y_GNIAZDA + 0.08, 0), (3.0, 0.2, 3.0), "bloto", "matowy", rot=(0, 45, 0), faza=0.05)
        p.blok("Bloto brzeg", (0, Y_GNIAZDA + 0.24, 0), (2.4, 0.12, 2.4), "bloto_jasne", "matowy", rot=(0, 22, 0),
               faza=0.03)
        for i in range(10):                                     # pęki trzcin wokół, odchylone na zewnątrz
            a = math.radians(i * 36 + 10)
            r = 1.75
            h = 1.5 + 0.35 * ((i * 7) % 3)
            with p.uklad(pos=(r * math.cos(a), Y_GNIAZDA, r * math.sin(a)), obrot=(0, -math.degrees(a) + 90, 0)):
                p.blok("Trzcina", (0, h / 2, 0.08), (0.2, h, 0.2), "trzcina" if i % 2 else "trzcina_ciemna", "matowy",
                       rot=(14, 0, 0), faza=0.0)
                if i % 3 == 0:
                    p.blok("Palka", (0, h + 0.12, 0.3), (0.24, 0.5, 0.24), "palka", "matowy", rot=(14, 0, 0), faza=0.03)


def _latarnia(p):
    """Wygięta tyczka z klatką i ognikiem (kość Latarnia, staw = podstawa tyczki)."""
    with p.na("Latarnia", od="staw"), p.uklad(obrot=(0, 180, 0)):   # ramię ku jajku (−X)
        p.blok("Tyczka", (0, 2.4, 0), (0.28, 4.8, 0.28), "pal", "matowy", faza=0.03)
        p.blok("Tyczka luk", (0.55, 4.85, 0), (1.3, 0.24, 0.24), "pal", "matowy", rot=(0, 0, -18), faza=0.03)
        p.blok("Sznur", (1.15, 4.35, 0), (0.05, 0.7, 0.05), "klatka", "matowy", faza=0.0)
        p.blok("Klatka gora", (1.15, 3.95, 0), (0.8, 0.12, 0.8), "klatka", "matowy", faza=0.02)
        p.blok("Klatka dol", (1.15, 3.1, 0), (0.8, 0.12, 0.8), "klatka", "matowy", faza=0.02)
        for x, z in ((-0.34, -0.34), (0.34, -0.34), (-0.34, 0.34), (0.34, 0.34)):
            p.blok("Klatka pret", (1.15 + x, 3.52, z), (0.08, 0.8, 0.08), "klatka", "matowy", faza=0.0)
        p.blok("Ognik", (1.15, 3.52, 0), (0.42, 0.5, 0.42), "ognik", "swiecacy", rot=(0, 45, 0), faza=0.05)


def inkubator():
    k = SKALA_INKUBATORA
    p = Postac("inkubator_bagienny", "Inkubator bagienny (podgląd)", typ="stwor", skala=1.0, faza=0.05, paleta=PALETA)
    p.kosc("Podstawa", "Root", staw=(0, 0.5, 0), czesc=(12.0, 0.5, 12.0), srodek=(0, -0.25, 0))
    p.kosc("Gniazdo", "Podstawa", staw=(0, 0.5, 0), czesc=(4.0, Y_GNIAZDA, 4.0), srodek=(0, Y_GNIAZDA / 2, 0))
    p.kosc("Jajko", "Gniazdo", staw=(0, Y_JAJKA, 0), czesc=(SZER * k, CZUBEK_Y * k, SZER * k),
           srodek=(0, CZUBEK_Y * k / 2, 0))
    p.kosc("Czubek", "Jajko", staw=(0, Y_JAJKA + CZUBEK_Y * k, 0), czesc=(1.6 * k, WYS_CZUBKA * k, 1.6 * k),
           srodek=(0, WYS_CZUBKA * k / 2, 0))
    # tablica bliżej punktu E (próba 17.11: z daleka zasłaniały ją kępy trzcin z mapy); 18.11: krok przed kępę trzcin
    # stanowiska (z bliska zasłaniała prawy brzeg tablicy) i trochę na zewnątrz — trzcina zostaje za tablicą
    p.kosc("Tablica", "Podstawa", staw=(3.8, 0.5, 5.8), czesc=(4.4, 4.4, 0.4), srodek=(0, 2.2, 0))
    # latarenka z boku gniazda, za tablicą (próba 17.11: z przodu po prawej zasłaniała jajko z boku); ramię ku jajku;
    # z tyłu stanowiska stoją lampion i wiaderka z mapy
    p.kosc("Latarnia", "Podstawa", staw=(5.2, 0.5, -0.4), czesc=(1.6, 5.0, 0.8), srodek=(-0.6, 2.5, 0))
    # to, co stoi na mapie Bagna (pomost, płyta, korzenie stanowiska) — tylko podgląd
    with p.na("Podstawa", od="staw"):
        p.blok("Pomost", (0, -0.4, 0), (15.0, 0.2, 15.0), "deska", "matowy", rot=(0, 8, 0), faza=0.05)
        p.blok("Plyta", (0, -0.25, 0), (12.0, 0.5, 12.0), "plyta", "matowy", faza=0.1)
        for i in range(6):
            a = math.radians(i * 60 + 15)
            p.blok("Korzen gniazda", (3.2 * math.cos(a), 0.65, 3.2 * math.sin(a)), (3.6, 1.3, 1.4), "korzen", "matowy",
                   rot=(0, -math.degrees(a) + 90, (-1) ** i * 8), faza=0.15)
    _gniazdo(p)
    _jajko(p, "Jajko", "Czubek", k)
    _latarnia(p)
    tablica_szans(p, "Tablica", [c for c, _ in PASKI], [s for _, s in PASKI], "tablica", "rama", "papier", mech="mech")
    p.zaczep("RootAttachment", "Podstawa", (0, -0.5, 0))
    p.zaczep("GlowaAttachment", "Czubek", (0, (WYS_CZUBKA + 0.4) * k, 0))
    klipy_jajka(p, "Jajko", "Czubek", z_peknieciem=False)
    p.ustaw_poze_renderu("spoczynek", 0)
    return p


def zbuduj():
    return [jajko(), inkubator()]


SLABOSCI = [
    "Jajko z trzech elipsoid: na styku skorupki i czubka widać delikatny szew (to też linia pęknięcia).",
    "Inkubator to podgląd: pomost, płyta i korzenie stoją na mapie Bagna; gniazdo na palach, latarenka i tablica "
    "stawia gra (napisy tablicy w SurfaceGui).",
]
