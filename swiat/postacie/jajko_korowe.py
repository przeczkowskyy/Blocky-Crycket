# -*- coding: utf-8 -*-
"""JAJKO KOROWE — nowy model leśnego jajka według referencji Pawła (24.11, obrazki w rozmowie: mszysta skorupa z kory
poprzecinana świecącymi szmaragdowymi szczelinami, osadzona w kanciastych korzeniach z niebieskimi grzybkami
i kryształkami) i jego wyklucie w trzech klatkach. Status: propozycja. Plik Karola jajko_lesne.py zostaje bez zmian.

Budowa (te same proporcje jajka co jajko_lesne: 2,54 × 1,7, pety_lesne.jajko_gladkie):
  - skorupa z dwóch elipsoid w kolorze ciemnego mchu z płytami kory (pionowe, lekko skręcone) i kępkami mchu;
  - świecące szmaragdowe szczeliny (Neon) w zygzakach między płytami kory;
  - czubek (pokrywa) i cztery odłamki przodu na osobnych kościach — odpadają przy wykluciu;
  - w środku świecący rdzeń („Wnetrze” — w grze klient barwi go kolorem rzadkości peta) i słup światła (kość Promien,
    w spoczynku skala 0);
  - podstawa: osiem kanciastych korzeni z mchem, trzy niebieskie świecące grzybki, kryształki (kość Krysztaly unosi się
    przy otwarciu).

Klipy (30 kl./s):
  spoczynek  lekkie kołysanie (pętla);
  napiecie   klatka 1 z referencji: narastające drżenie i podskoki, odłamki przodu lekko odstają (szczeliny „pracują”);
  pekniecie  klatki 2 i 3: odłamki przodu odpadają na boki, potem pokrywa odrywa się w górę, rdzeń zostaje w korzeniach,
             wyrasta słup światła i unoszą się kryształki.

    python -B swiat/postacie/przebuduj.py jajko_korowe --bez-filmow
    python -B swiat/postacie/jajko_korowe.py --kontrola
"""
import math
import os
import sys

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from swiat.postacie.biblioteka.postac import Postac  # noqa: E402
from swiat.postacie.pety_lesne import jajko_gladkie, promien_jajka  # noqa: E402

ID = "jajko_korowe"
NAZWA = "Jajko korowe (leśne)"

PALETA = {
    "kora": "4E6B2A", "kora_ciemna": "3A4A22", "kora_brazowa": "5A4426", "mech": "6E9E2E", "mech_jasny": "8DBA3C",
    "szczelina": "2BE36B", "rdzen": "B8FFD2", "promien": "7DFFB0",
    "korzen": "4A3520", "korzen_ciemny": "33241A", "mech_korzeni": "5E8F2A",
    "grzyb": "4FC3F7", "grzyb_trzon": "BFE9F7", "krysztal": "5CF2D6",
}

WYS, SZER, CZUBEK_Y = 2.54, 1.7, 1.62
WYS_CZUBKA = WYS - CZUBEK_Y
PODSTAWA = 0.35          # wysokość, na której jajko siedzi w korzeniach
# szczeliny: azymuty pionowych zygzaków (0 = przód +Z); na odłamkach przodu leżą ich górne części
SZCZELINY = (-150, -95, -45, 0, 40, 100, 160)
# odłamki przodu (kość, azymut środka, y od spodu jajka) — odpadają w klatce 2
ODLAMKI = (("Odlamek1", -28, 1.25), ("Odlamek2", 22, 1.3), ("Odlamek3", -12, 1.0), ("Odlamek4", 55, 1.15))


def _na_powierzchni(y, azymut, ks=None, wglab=0.0):
    r = promien_jajka(y, WYS, SZER, ks) - wglab
    a = math.radians(azymut)
    return r * math.sin(a), r * math.cos(a)


def _plyta(p, nazwa, y, azymut, wys, szer, kolor, skret=0.0, ks=None, y0=0.0):
    """Płyta kory przyklejona do skorupy (zwrócona na zewnątrz), y od spodu jajka; y0 = wysokość stawu kości."""
    x, z = _na_powierzchni(y, azymut, ks, wglab=0.045)
    p.blok(nazwa, (x, y - y0, z), (szer, wys, 0.07), kolor, "matowy", rot=(0, azymut, skret), faza=0.025)


def _szczelina(p, y, azymut, dl, kat, ks=None, y0=0.0, gr=0.05):
    x, z = _na_powierzchni(y, azymut, ks, wglab=-0.045)  # na wierzchu płyt kory
    p.blok("Szczelina", (x, y - y0, z), (gr, dl, 0.04), "szczelina", "swiecacy", rot=(0, azymut, kat), faza=0.0)


def _zygzak(p, azymut, y_od, y_do, ks=None, y0=0.0, faza=0):
    """Ciągła pionowa szczelina: odcinki na przemian w lewo i w prawo, stykające się końcami (świecący zygzak)."""
    krok, kat = 0.2, 24
    dl = krok / math.cos(math.radians(kat)) + 0.03
    y, i = y_od, faza
    przes = 0.0
    while y + krok <= y_do + 0.01:
        k = kat if i % 2 == 0 else -kat
        # środek odcinka: azymut przesunięty o pół kroku w bok (w stopniach, przybliżenie przy promieniu ~0,8)
        boczne = math.degrees(krok * math.tan(math.radians(k)) / 2 / 0.8)
        _szczelina(p, y + krok / 2, azymut + przes + boczne, dl, k, ks, y0)
        if i % 3 == 1:  # krótka boczna odnoga
            _szczelina(p, y + krok / 2, azymut + przes + boczne + (9 if k > 0 else -9), 0.16, 65 if k > 0 else -65,
                       ks, y0, gr=0.04)
        przes += 2 * boczne
        y += krok
        i += 1


KOLORY_KORY = ("kora_ciemna", "kora", "kora_brazowa", "mech", "kora_ciemna", "kora_brazowa")


def _skorupa(p):
    # elipsoidy skorupy i rdzeń (pety_lesne.jajko_gladkie: dół na kości Jajko, kopułka na kości Czubek)
    jajko_gladkie(p, "Jajko", "Czubek", 1.0, CZUBEK_Y, WYS, SZER, "kora_ciemna", kolor_wnetrza="rdzen")
    with p.na("Jajko", od="staw"):
        # płyty kory i mchu na całej skorupie (rzędy przesunięte o pół płyty), poza miejscami odłamków
        for r, y in enumerate((0.3, 0.68, 1.04, 1.38)):
            for c in range(12):
                az = c * 30 + (15 if r % 2 else 0)
                if any(abs(((az - a + 180) % 360) - 180) < 20 and abs(y - yy) < 0.3 for _, a, yy in ODLAMKI):
                    continue
                szer = (0.34, 0.36, 0.32, 0.22)[r]
                _plyta(p, "Kora", y, az, 0.4, szer, KOLORY_KORY[(c + r) % len(KOLORY_KORY)], skret=(-1) ** c * 7,
                       ks="dol")
        for i, az in enumerate(SZCZELINY):
            _zygzak(p, az, 0.12, CZUBEK_Y - 0.02, ks="dol", faza=i)
        for i, az in enumerate((-120, 15, 130, -60, 75)):
            x, z = _na_powierzchni(0.35 + 0.22 * i, az, "dol", wglab=-0.02)
            p.kula("Mech", (x, 0.35 + 0.22 * i, z), (0.3, 0.16, 0.3), "mech_jasny", "matowy", segm=8)
    # czubek (pokrywa): płyty kory i szczeliny na kopułce
    with p.na("Czubek", od="staw"):
        for r, y in enumerate((CZUBEK_Y + 0.18, CZUBEK_Y + 0.5)):
            for c in range(10 if r == 0 else 6):
                az = c * (36 if r == 0 else 60) + (18 if r else 0)
                _plyta(p, "Kora czubka", y, az, 0.34, 0.3 if r == 0 else 0.26, KOLORY_KORY[(c + r) % 6],
                       skret=(-1) ** c * 8, ks="gora", y0=CZUBEK_Y)
        for i, az in enumerate(SZCZELINY):
            _zygzak(p, az, CZUBEK_Y + 0.02, WYS - 0.2, ks="gora", y0=CZUBEK_Y, faza=i)
        p.kula("Mech czubka", (0.1, WYS - CZUBEK_Y - 0.06, -0.05), (0.5, 0.18, 0.46), "mech_jasny", "matowy", segm=8)
    # odłamki przodu: płyta kory ze szczeliną na własnej kości (staw kości = punkt na skorupie)
    for kosc, az, y in ODLAMKI:
        with p.na(kosc, od="staw"):
            p.blok("Odlamek kora", (0, 0, 0), (0.42, 0.44, 0.13), "kora_brazowa", "matowy", rot=(0, az, 10), faza=0.04)
            a = math.radians(az)
            p.blok("Odlamek szczelina", (0.08 * math.sin(a), 0, 0.08 * math.cos(a)), (0.05, 0.4, 0.04), "szczelina",
                   "swiecacy", rot=(0, az, 28), faza=0.0)


def _podstawa(p):
    with p.na("Podstawa", od="staw"):
        for i in range(8):
            a = math.radians(i * 45 + 10)
            r = 0.95 + 0.12 * (i % 2)
            dl, wy = (0.75, 0.55) if i % 2 == 0 else (0.6, 0.42)
            p.blok("Korzen", (r * math.sin(a), wy / 2 - 0.05, r * math.cos(a)), (0.5, wy, dl),
                   "korzen" if i % 3 else "korzen_ciemny", "matowy", rot=(0, math.degrees(a), (-1) ** i * 9), faza=0.08)
            p.blok("Mech korzenia", (r * math.sin(a), wy - 0.02, r * math.cos(a)), (0.46, 0.08, dl - 0.1),
                   "mech_korzeni", "matowy", rot=(0, math.degrees(a), (-1) ** i * 9), faza=0.02)
        for i, (az, r, h) in enumerate(((-55, 1.05, 0.42), (40, 1.2, 0.34), (150, 1.1, 0.38))):
            a = math.radians(az)
            x, z = r * math.sin(a), r * math.cos(a)
            p.walec("Grzyb trzon", (x, 0.35 + h / 2, z), (0.1, h, 0.1), "grzyb_trzon", "matowy", segm=6)
            p.kula("Grzyb kapelusz", (x, 0.35 + h + 0.05, z), (0.36, 0.18, 0.36), "grzyb", "swiecacy", segm=8)
    with p.na("Krysztaly", od="staw"):
        for i, (az, r, s) in enumerate(((-20, 1.3, 0.22), (70, 1.35, 0.16), (115, 1.25, 0.2), (-100, 1.3, 0.18),
                                        (-160, 1.2, 0.15), (200, 1.45, 0.12))):
            a = math.radians(az)
            s *= 0.6
            p.blok("Krysztal", (r * math.sin(a), 0.15 + s, r * math.cos(a)), (s * 0.7, s * 1.8, s * 0.7), "krysztal",
                   "swiecacy", rot=(10 * (-1) ** i, az, 15 * (-1) ** i), faza=0.0)
    with p.na("Promien", od="staw"):
        p.walec("Slup swiatla", (0, 3.0, 0), (1.1, 6.0, 1.1), "promien", "swiecacy", segm=12)


def _klipy(p):
    k = p.klip("spoczynek", 60, petla=True)
    k.cykl("Jajko", "obrot", (1.2, 0, 2.0), czestosc=1)
    k.klucz(0, "Promien", skala=(0.01, 0.01, 0.01))
    k.klucz(60, "Promien", skala=(0.01, 0.01, 0.01))
    # klatka 1: narastające napięcie — drżenie coraz mocniej, podskoki, odłamki przodu lekko odstają
    k = p.klip("napiecie", 42, petla=False)
    for f, kat in ((0, 0), (4, 3), (8, -3), (12, 5), (16, -5), (20, 7), (24, -8), (28, 10), (32, -11), (36, 12),
                   (39, -8), (42, 0)):
        k.klucz(f, "Jajko", obrot=(0, 0, kat))
    for f, y in ((0, 0), (18, 0), (20, 0.1), (22, 0), (32, 0), (34, 0.16), (36, 0), (42, 0)):
        k.klucz(f, "Jajko", przes=(0, y, 0))
    for kosc, az, _y in ODLAMKI:
        a = math.radians(az)
        for f, d in ((0, 0), (24, 0.03), (30, 0.0), (36, 0.06), (42, 0.04)):
            k.klucz(f, kosc, przes=(d * math.sin(a), 0, d * math.cos(a)))
    k.klucz(0, "Promien", skala=(0.01, 0.01, 0.01))
    k.klucz(42, "Promien", skala=(0.01, 0.01, 0.01))
    # klatki 2 i 3: odłamki przodu odpadają, pokrywa odrywa się w górę, słup światła i unoszące się kryształki
    k = p.klip("pekniecie", 54, petla=False)
    for i, (kosc, az, _y) in enumerate(ODLAMKI):
        a = math.radians(az)
        bok = 1 if az >= 0 else -1
        k.klucz(0, kosc, przes=(0, 0, 0), obrot=(0, 0, 0))
        k.klucz(4 + i, kosc, przes=(0.08 * math.sin(a), 0.05, 0.08 * math.cos(a)), obrot=(-5, 0, bok * 5))
        k.klucz(16 + i, kosc, przes=(1.3 * math.sin(a) + bok * 0.5, 0.6, 1.3 * math.cos(a)), obrot=(-60, bok * 40, bok * 70),
                wyg="liniowo")
        k.klucz(30, kosc, przes=(2.2 * math.sin(a) + bok * 0.9, -0.4, 2.0 * math.cos(a)), obrot=(-110, bok * 70, bok * 120))
        k.klucz(54, kosc, przes=(2.2 * math.sin(a) + bok * 0.9, -0.4, 2.0 * math.cos(a)), obrot=(-110, bok * 70, bok * 120))
    k.klucz(0, "Czubek", przes=(0, 0, 0), obrot=(0, 0, 0))
    k.klucz(18, "Czubek", przes=(0, 0.05, 0), obrot=(-4, 0, 3))
    k.klucz(22, "Czubek", przes=(0, 0.25, 0.05), obrot=(-10, 6, 6))
    k.klucz(32, "Czubek", przes=(-0.9, 2.2, 0.3), obrot=(-35, 40, -45), wyg="liniowo")
    k.klucz(44, "Czubek", przes=(-1.8, 2.9, 0.5), obrot=(-70, 80, -80))
    k.klucz(54, "Czubek", przes=(-1.9, 2.8, 0.5), obrot=(-75, 85, -85))
    for f, y in ((0, 0), (20, -0.05), (24, 0.04), (30, 0), (54, 0)):
        k.klucz(f, "Jajko", przes=(0, y, 0))
    k.klucz(0, "Promien", skala=(0.01, 0.01, 0.01))
    k.klucz(22, "Promien", skala=(0.01, 0.01, 0.01))
    k.klucz(30, "Promien", skala=(0.6, 0.5, 0.6))
    k.klucz(38, "Promien", skala=(1.0, 1.0, 1.0))
    k.klucz(54, "Promien", skala=(0.9, 1.05, 0.9))
    for f, y in ((0, 0), (24, 0), (40, 0.7), (54, 1.0)):
        k.klucz(f, "Krysztaly", przes=(0, y, 0))
    k.klucz(0, "Krysztaly", obrot=(0, 0, 0))
    k.klucz(54, "Krysztaly", obrot=(0, 40, 0))


def jajko():
    p = Postac(ID, NAZWA, typ="stwor", skala=1.0, faza=0.05, paleta=PALETA)
    p.kosc("Podstawa", "Root", staw=(0, 0, 0), czesc=(2.6, PODSTAWA, 2.6), srodek=(0, PODSTAWA / 2, 0))
    p.kosc("Jajko", "Podstawa", staw=(0, PODSTAWA - 0.05, 0), czesc=(SZER, CZUBEK_Y, SZER), srodek=(0, CZUBEK_Y / 2, 0))
    p.kosc("Czubek", "Jajko", staw=(0, PODSTAWA - 0.05 + CZUBEK_Y, 0), czesc=(1.4, WYS_CZUBKA, 1.4),
           srodek=(0, WYS_CZUBKA / 2, 0))
    for kosc, az, y in ODLAMKI:
        x, z = _na_powierzchni(y, az, "dol")
        p.kosc(kosc, "Jajko", staw=(x, PODSTAWA - 0.05 + y, z), czesc=(0.44, 0.46, 0.12), srodek=(0, 0, 0))
    p.kosc("Krysztaly", "Podstawa", staw=(0, 0, 0), czesc=(2.8, 0.5, 2.8), srodek=(0, 0.25, 0))
    p.kosc("Promien", "Podstawa", staw=(0, PODSTAWA + 1.0, 0), czesc=(1.1, 6.0, 1.1), srodek=(0, 3.0, 0))
    _skorupa(p)
    _podstawa(p)
    p.zaczep("RootAttachment", "Podstawa", (0, 0, 0))
    p.zaczep("GlowaAttachment", "Czubek", (0, WYS_CZUBKA + 0.2, 0))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 0)
    return p


def zbuduj():
    return [jajko()]


SLABOSCI = [
    "Pulsowanie szczelin (zmiana jasności) robi klient w grze — klipy ruszają tylko kośćmi.",
    "Odłamki to płyty kory na wierzchu skorupy: po odpadnięciu pod spodem zostaje gładka skorupa i rdzeń.",
]

if __name__ == "__main__":
    if "--kontrola" in sys.argv:
        for p in zbuduj():
            b, u = p.sprawdz()
            print(p.id, "błędy:", len(b), "uwagi:", len(u))
            for x in b[:15]:
                print("  B", x)
            for x in u[:5]:
                print("  U", x)
