# -*- coding: utf-8 -*-
"""JAJKO DŻUNGLI i INKUBATOR DŻUNGLI — jajko Dżungli (próba swiat/pety_proba, 18.11.2026; status: propozycja).

Dwa modele w jednym module:
  • jajko_dzungli     — gładkie jajko z elipsoid (2,6 × 1,75 studa; pety_lesne.jajko_gladkie) w kolorze turkusowej wody
                        Dżungli, w ciemnozielone, bursztynowe i czerwone cętki, na czubku dwa wielkie liście i czerwony
                        kwiat hibiskusa z żółtym pręcikiem. Czubek odskakuje przy pęknięciu; pod nim świecące „Wnetrze”
                        (kolor rzadkości w grze). Klipy jak jajko leśne: spoczynek, trzesienie, pekniecie.
  • inkubator_dzungli — PODGLĄD stanowiska na Tarasie Przybycia Dżungli: kamienna płyta z korzeniami, gniazdo z mchem
                        (to stoi na mapie swiat/dzungla_pas — w grze tego nie budujemy), wielkie jajko na mchu (×1,8),
                        **kamienny totem ruin** z runami, owinięty lianą, ze świecącym różowym kwiatem na czubku (kość
                        Totem) i tablica szans z liśćmi na daszku (kość Tablica). W grze stawiamy kości Totem i Tablica
                        jako stałe bryły, a jajko jako rig z klipami.

    python -B swiat/postacie/przebuduj.py jajko_dzungli --bez-filmow

Pomysł inny niż jajko leśne i Bagna (zlecenie 18.11): turkusowe jajko z hibiskusem, totem z ruin zamiast lampionu
i gniazda na palach. Kolory pasków tablicy i szanse tylko do podglądu — w grze z swiat/pety_proba/ustawienia.json.
Położenia totemu i tablicy omijają rzeczy z mapy (świecące kwiaty, lampion, wiaderka — swiat/dzungla_pas/krotki).
"""
import math

from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import jajko_gladkie, klipy_jajka, tablica_szans

ID = "jajko_dzungli"

PALETA = {
    "skorupka": "35C7B5", "cetka": "1E7A5E", "cetka_bursztyn": "F2B030", "cetka_czerwona": "E5392B",
    "lisc": "2FA34A", "lisc_jasny": "6CCB4A", "kwiat": "E5392B", "kwiat_srodek": "FFD84A", "wnetrze": "E8FFF8",
    "kamien": "8F8A7A", "kamien_ciemny": "6B6658", "run": "2EC4B6", "liana": "3E7D2E", "kwiat_jarzacy": "FF5FA2",
    "tablica": "6B4A2E", "rama": "4A3220", "papier": "F2EAD2", "plyta": "B69272", "korzen": "5C3A22",
    "gniazdo": "8B5A2E", "mech": "8CC63F",
    "r_pospolity": "B8C2CC", "r_zwykly": "6BD66B", "r_rzadki": "4FB3FF", "r_epicki": "C27BFF", "r_legendarny": "FFC23D",
}
PASKI = [("r_pospolity", 0.50), ("r_zwykly", 0.25), ("r_rzadki", 0.15), ("r_epicki", 0.08), ("r_legendarny", 0.02)]

WYS = 2.6
SZER = 1.75
CZUBEK_Y = 1.5
WYS_CZUBKA = WYS - CZUBEK_Y
SKALA_INKUBATORA = 1.8
Y_JAJKA = 0.92            # spód jajka na mchu gniazda z mapy (jak w lesie — to samo stanowisko)
CETKI = (("dol", 30, 0.9, 0.36, "cetka"), ("dol", -45, 0.45, 0.26, "cetka_bursztyn"), ("dol", 100, 1.1, 0.3, "cetka"),
         ("dol", -110, 0.75, 0.34, "cetka_czerwona"), ("dol", 185, 1.15, 0.32, "cetka"),
         ("dol", -15, 1.6, 0.24, "cetka_czerwona"), ("dol", 145, 1.75, 0.22, "cetka_bursztyn"),
         ("dol", 70, 0.35, 0.22, "cetka_bursztyn"), ("gora", 35, 2.3, 0.24, "cetka"), ("gora", -130, 2.36, 0.2, "cetka"))


def _jajko(p, kosc_jajka, kosc_czubka, k=1.0):
    jajko_gladkie(p, kosc_jajka, kosc_czubka, k, CZUBEK_Y, WYS, SZER, "skorupka", cetki=CETKI)
    with p.na(kosc_czubka, od="staw"):
        y = k * (WYS_CZUBKA - 0.02)
        for zn in (1, -1):                                             # dwa wielkie liście rozłożone na boki
            with p.uklad(pos=(0, y, 0), obrot=(0, 20, zn * 28)):
                p.blok("Lisc czubka", (zn * k * 0.32, k * 0.02, 0), (k * 0.66, k * 0.05, k * 0.36), "lisc", "matowy",
                       faza=0.0)
                p.blok("Lisc czubka zylka", (zn * k * 0.32, k * 0.05, 0), (k * 0.56, k * 0.02, k * 0.05), "lisc_jasny",
                       "matowy", faza=0.0)
        for i in range(5):                                             # hibiskus: pięć płatków i pręcik
            a = math.radians(i * 72 + 10)
            p.blok("Platek", (k * 0.13 * math.cos(a), y + k * 0.1, k * 0.13 * math.sin(a)), (k * 0.2, k * 0.06, k * 0.16),
                   "kwiat", "matowy", rot=(0, -math.degrees(a), 24), faza=0.0)
        p.blok("Precik", (0, y + k * 0.22, 0), (k * 0.05, k * 0.22, k * 0.05), "kwiat_srodek", "matowy", rot=(0, 0, 12),
               faza=0.0)


def jajko():
    p = Postac(ID, "Jajko Dżungli", typ="stwor", skala=1.0, faza=0.05, paleta=PALETA)
    p.kosc("Jajko", "Root", staw=(0, 0, 0), czesc=(SZER, CZUBEK_Y, SZER), srodek=(0, CZUBEK_Y / 2, 0))
    p.kosc("Czubek", "Jajko", staw=(0, CZUBEK_Y, 0), czesc=(1.55, WYS_CZUBKA, 1.55), srodek=(0, WYS_CZUBKA / 2, 0))
    _jajko(p, "Jajko", "Czubek", 1.0)
    p.zaczep("RootAttachment", "Jajko", (0, 0, 0))
    p.zaczep("GlowaAttachment", "Czubek", (0, WYS_CZUBKA + 0.5, 0))
    klipy_jajka(p, "Jajko", "Czubek")
    p.ustaw_poze_renderu("spoczynek", 0)
    return p


def _totem(p):
    """Kamienny totem ruin z runami, owinięty lianą, ze świecącym kwiatem na czubku (kość Totem, staw = podstawa)."""
    with p.na("Totem", od="staw"):
        p.blok("Kolumna podstawa", (0, 0.2, 0), (1.3, 0.4, 1.3), "kamien_ciemny", "matowy", faza=0.05)
        p.blok("Kolumna", (0, 2.0, 0), (0.95, 3.3, 0.95), "kamien", "matowy", faza=0.08)
        p.blok("Kolumna glowica", (0, 3.8, 0), (1.3, 0.35, 1.3), "kamien_ciemny", "matowy", faza=0.05)
        for i, y in enumerate((1.2, 2.0, 2.8)):                        # runy na czterech ścianach
            for a in (0, 90, 180, 270):
                with p.uklad(obrot=(0, a, 0)):
                    p.blok("Run", (0, y, 0.485), (0.34 if i != 1 else 0.08, 0.08 if i != 1 else 0.4, 0.03), "run",
                           "swiecacy", faza=0.0)
        for i in range(5):                                             # liana owinięta spiralą
            a = math.radians(i * 80)
            p.blok("Liana", (0.52 * math.sin(a), 0.8 + i * 0.6, 0.52 * math.cos(a)), (0.6, 0.12, 0.12), "liana",
                   "matowy", rot=(0, math.degrees(a) + 90, 18), faza=0.0)
            p.blok("Listek liany", (0.6 * math.sin(a), 0.95 + i * 0.6, 0.6 * math.cos(a)), (0.24, 0.05, 0.16),
                   "lisc_jasny", "matowy", rot=(0, math.degrees(a), 30), faza=0.0)
        for i in range(6):                                             # świecący kwiat w czaszy
            a = math.radians(i * 60)
            p.blok("Kwiat jarzacy", (0.28 * math.cos(a), 4.15, 0.28 * math.sin(a)), (0.42, 0.12, 0.3), "kwiat_jarzacy",
                   "swiecacy", rot=(0, -math.degrees(a), 28), faza=0.0)
        p.blok("Kwiat srodek", (0, 4.3, 0), (0.18, 0.2, 0.18), "kwiat_srodek", "swiecacy", faza=0.0)


def inkubator():
    k = SKALA_INKUBATORA
    p = Postac("inkubator_dzungli", "Inkubator Dżungli (podgląd)", typ="stwor", skala=1.0, faza=0.05, paleta=PALETA)
    p.kosc("Podstawa", "Root", staw=(0, 0.5, 0), czesc=(12.0, 0.5, 12.0), srodek=(0, -0.25, 0))
    p.kosc("Jajko", "Podstawa", staw=(0, Y_JAJKA, 0), czesc=(SZER * k, CZUBEK_Y * k, SZER * k),
           srodek=(0, CZUBEK_Y * k / 2, 0))
    p.kosc("Czubek", "Jajko", staw=(0, Y_JAJKA + CZUBEK_Y * k, 0), czesc=(1.55 * k, WYS_CZUBKA * k, 1.55 * k),
           srodek=(0, WYS_CZUBKA * k / 2, 0))
    # tablica z przodu po lewej (patrząc od punktu E), przed świecącym kwiatem mapy — ten zostaje za tablicą
    p.kosc("Tablica", "Podstawa", staw=(3.6, 0.5, 5.45), czesc=(4.4, 4.4, 0.4), srodek=(0, 2.2, 0))
    # totem z boku gniazda po prawej, przed wiaderkami z mapy (lampion mapy stoi z tyłu po lewej)
    p.kosc("Totem", "Podstawa", staw=(-5.7, 0.5, 0.2), czesc=(1.3, 4.5, 1.3), srodek=(0, 2.2, 0))
    # to, co stoi na mapie Dżungli (posadzka, płyta, korzenie, gniazdo z mchem) — tylko podgląd
    with p.na("Podstawa", od="staw"):
        p.blok("Posadzka", (0, -0.4, 0), (15.0, 0.2, 15.0), "kamien_ciemny", "matowy", rot=(0, 8, 0), faza=0.05)
        p.blok("Plyta", (0, -0.25, 0), (12.0, 0.5, 12.0), "plyta", "matowy", faza=0.1)
        for i in range(6):
            a = math.radians(i * 60 + 15)
            p.blok("Korzen gniazda", (3.2 * math.cos(a), 0.65, 3.2 * math.sin(a)), (3.6, 1.3, 1.4), "korzen", "matowy",
                   rot=(0, -math.degrees(a) + 90, (-1) ** i * 8), faza=0.15)
        p.blok("Gniazdo dno", (0, 0.15, 0), (4.6, 0.3, 4.6), "gniazdo", "matowy", faza=0.1)
        p.blok("Mech", (0, 0.36, 0), (3.9, 0.12, 3.9), "mech", "matowy", faza=0.04)
    _jajko(p, "Jajko", "Czubek", k)
    _totem(p)
    tablica_szans(p, "Tablica", [c for c, _ in PASKI], [s for _, s in PASKI], "tablica", "rama", "papier",
                  mech="lisc")
    p.zaczep("RootAttachment", "Podstawa", (0, -0.5, 0))
    p.zaczep("GlowaAttachment", "Czubek", (0, (WYS_CZUBKA + 0.5) * k, 0))
    klipy_jajka(p, "Jajko", "Czubek", z_peknieciem=False)
    p.ustaw_poze_renderu("spoczynek", 0)
    return p


def zbuduj():
    return [jajko(), inkubator()]


SLABOSCI = [
    "Jajko z trzech elipsoid: na styku skorupki i czubka widać delikatny szew (to też linia pęknięcia).",
    "Inkubator to podgląd: płyta, korzenie i gniazdo z mchem stoją na mapie Dżungli; totem i tablicę stawia gra "
    "(napisy tablicy w SurfaceGui).",
]
