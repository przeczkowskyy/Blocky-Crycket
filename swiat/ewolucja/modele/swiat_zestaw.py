# -*- coding: utf-8 -*-
"""Zestaw świata w języku „Żarołuski”: klockowe, fazowane bryły, ciemne opaski-dachówki, żar tam, gdzie coś jest
gorące albo magiczne, kryształowe akcenty. Każdy rekwizyt to statyczny rig z części (jedna kość „Podstawa”)
w formacie rekwizyt_<id>_rig.json. Budżety części: drobiazgi ≤ 8, drzewa i skały ≤ 20, punkty charakterystyczne ≤ 80.

    from swiat.ewolucja.modele import swiat_zestaw
    swiat_zestaw.wszystkie()        # [(Postac, strefa, limit części), …]; ZESTAW = spis id

Jednostka = stud, ziemia y = 0, przód +Z (jak cała biblioteka). Chorągiew ma płat w regionie „cialo” (kolor gracza).
"""
import math
import random

from swiat.ewolucja.modele.smok_model import Smok, zbuduj_stadium_lod

PAL = {
    "trawa": "5DB84A", "trawa_c": "3E9440", "trawa_j": "8AD65C", "lisc": "4FAE46", "lisc_c": "2F7F3A", "lisc_j": "7CCB52",
    "pien": "8A5A3A", "pien_c": "5A3828", "pien_j": "C09A6A", "kamien": "8C8AA0", "kamien_c": "544E6A", "kamien_j": "B4B2C4",
    "mech": "6FB04A", "czerwony": "FF4D5E", "zolty": "FFD23F", "niebieski": "5AA8FF", "bialy": "FFFDF5", "srodek": "FFB52E",
    "kapelusz": "E8443A", "trzon": "F2E6CF", "rozowy": "FFB8D6", "igly": "1F5A46", "igly_c": "174438", "igly_j": "2E7A5A",
    "pien_l": "4A3340", "fiolet": "7A3FC9", "fiolet_c": "55289A", "grzyb_sw": "5CF2D6", "bazalt": "3A3648", "bazalt_c": "26222F",
    "zar": "FF7A2A", "zar_j": "FFD98A", "lilia": "4FB868", "lilia_j": "7ED68A", "trzcina": "7CA84A", "palka": "7A4A2A",
    "kosc": "EDE4CF", "kosc_c": "CFC3A8", "mrok": "2A2230", "zloto": "FFC934", "zloto_c": "E09A1A", "zloto_j": "FFE680",
    "krysztal": "7FF8FF", "rubin": "FF3D6A", "szmaragd": "35DD8A", "szafir": "4FA8FF", "magia": "FF4DD8", "cialo": "E3412B",
    "kula1": "FFE14D", "kula2": "4FD0FF", "kula3": "FF4DD8", "drewno": "A8703E",
}
ZESTAW = []          # [(id, nazwa, strefa, limit części, funkcja)]


def rekwizyt(id, nazwa, strefa, limit):
    def dekorator(fn):
        ZESTAW.append((id, nazwa, strefa, limit, fn))
        return fn
    return dekorator


def _nowy(id, nazwa, faza=0.1, skala=1.0):
    p = Smok(id, nazwa, typ="stwor", skala=skala, faza=faza, paleta=PAL)
    p.kosc("Podstawa", "Root", (0, 0, 0), czesc=(2, 1, 2), srodek=(0, 0.5, 0))
    p._ctx = p.na("Podstawa")
    p._ctx.__enter__()                                         # wszystkie bryły rekwizytu wiszą na jednej kości
    return p


# --------------------------------------------------------------------------- łąka
def _trawa(id, n):
    p = _nowy(id, "Kępka trawy", faza=0.0)
    for i in range(n):
        a = 360.0 * i / n
        p.klin("Zdzblo", (0.3 * math.sin(math.radians(a)), 0.4 + 0.08 * (i % 3), 0.3 * math.cos(math.radians(a))),
               (0.22, 0.8 + 0.16 * (i % 3), 0.32), ("trawa", "trawa_j", "trawa_c")[i % 3], "matowy", rot=(0, a + 180, 0))
    return p


rekwizyt("trawa_1", "Kępka trawy mała", "laka", 8)(lambda: _trawa("trawa_1", 3))
rekwizyt("trawa_2", "Kępka trawy duża", "laka", 8)(lambda: _trawa("trawa_2", 5))


def _kwiat(id, kolor):
    p = _nowy(id, "Kwiat", faza=0.04)
    p.blok("Lodyga", (0, 0.5, 0), (0.14, 1.0, 0.14), "trawa_c", "matowy")
    p.klin("Lisc", (0.2, 0.3, 0), (0.1, 0.4, 0.4), "trawa", "matowy", rot=(0, 90, 0), faza=0.0)
    p.blok("Platki", (0, 1.05, 0), (0.7, 0.22, 0.7), kolor, "matowy")
    p.blok("Platki 2", (0, 1.07, 0), (0.7, 0.2, 0.7), kolor, "matowy", rot=(0, 45, 0))
    p.blok("Srodek", (0, 1.2, 0), (0.3, 0.2, 0.3), "srodek", "matowy")
    return p


for _k in ("czerwony", "zolty", "niebieski", "bialy"):
    rekwizyt("kwiat_" + _k, "Kwiat " + _k, "laka", 8)(lambda _k=_k: _kwiat("kwiat_" + _k, _k))


@rekwizyt("kamyk", "Kamyk", "laka", 8)
def kamyk():
    p = _nowy("kamyk", "Kamyk", faza=0.14)
    p.blok("Kamyk", (0, 0.35, 0), (1.3, 0.8, 1.0), "kamien", "matowy", rot=(0, 20, 6))
    p.blok("Kamyk 2", (0.6, 0.22, 0.3), (0.7, 0.5, 0.8), "kamien_j", "matowy", rot=(0, -30, 0))
    return p


def _glaz(id, wys):
    p = _nowy(id, "Głaz", faza=0.4)
    p.blok("Glaz", (0, wys * 0.42, 0), (4.4, wys * 0.9, 3.8), "kamien", "matowy", rot=(0, 18, 4))
    p.blok("Opaska", (0, wys * 0.42, 0), (4.62, 0.6, 4.0), "kamien_c", "matowy", rot=(0, 18, 4), faza=0.1)
    p.blok("Glaz 2", (2.0, wys * 0.24, 1.1), (2.6, wys * 0.5, 2.6), "kamien_j", "matowy", rot=(0, -24, -5))
    p.blok("Glaz 3", (-1.9, 0.5, -1.2), (2.0, 1.1, 1.8), "kamien", "matowy", rot=(0, 40, 0))
    p.blok("Mech", (-0.2, wys * 0.87, 0.1), (2.8, 0.22, 2.4), "mech", "matowy", rot=(0, 18, 4), faza=0.08)
    if wys > 4:
        p.klin("Krysztal", (1.2, wys * 0.95, -0.6), (0.5, 1.6, 0.9), "krysztal", "polysk", rot=(8, 30, -12), faza=0.02)
        p.klin("Krysztal 2", (0.5, wys * 0.9, -1.0), (0.4, 1.0, 0.6), "krysztal", "polysk", rot=(-6, 80, 10), faza=0.02)
    return p


rekwizyt("glaz_1", "Głaz niski", "laka", 20)(lambda: _glaz("glaz_1", 3.0))
rekwizyt("glaz_2", "Głaz wysoki z kryształem", "laka", 20)(lambda: _glaz("glaz_2", 6.5))


@rekwizyt("krzak", "Krzak z jagodami", "laka", 8)
def krzak():
    p = _nowy("krzak", "Krzak", faza=0.3)
    p.blok("Krzak", (0, 1.0, 0), (3.2, 2.0, 2.8), "lisc", "matowy", rot=(0, 15, 0))
    p.blok("Krzak 2", (1.3, 0.8, 0.6), (2.0, 1.6, 2.0), "lisc_j", "matowy", rot=(0, -20, 0))
    p.blok("Krzak 3", (-1.2, 0.7, -0.5), (1.9, 1.4, 1.9), "lisc_c", "matowy", rot=(0, 35, 0))
    p.blok("Krzak 4", (0.2, 1.9, -0.1), (1.8, 1.0, 1.6), "lisc_j", "matowy", rot=(0, 50, 0))
    for x, y, z in ((1.0, 1.5, 1.5), (-0.6, 1.2, 1.42), (1.9, 0.9, 1.3)):
        p.blok("Jagoda", (x, y, z), (0.36, 0.36, 0.36), "czerwony", "polysk", faza=0.1)
    return p


def _drzewo(id, wys, korona, kor_j, kor_c, pietra):
    p = _nowy(id, "Drzewo", faza=0.5)
    hp = wys * 0.42
    p.walec("Pien", (0, hp / 2, 0), (1.7, hp, 1.7), "pien", "matowy", segm=8)
    p.walec("Opaska", (0, hp * 0.55, 0), (1.94, 0.7, 1.94), "pien_c", "matowy", segm=8)      # ciemna opaska jak łuska
    for i, a in enumerate((20, 200)):
        p.klin("Korzen", (0.9 * math.sin(math.radians(a)), 0.45, 0.9 * math.cos(math.radians(a))), (0.7, 0.9, 1.3), "pien_c",
               "matowy", rot=(0, a + 180, 0), faza=0.04)
    y = hp
    for i, (sz, h) in enumerate(pietra):
        p.blok("Korona %d" % i, ((0.5 if i == 1 else 0), y + h / 2 - 0.4, (-0.4 if i == 2 else 0)), (sz, h, sz * 0.92),
               (korona, kor_j, kor_c)[i % 3], "matowy", rot=(0, 28 * i + 10, 0))
        y += h * 0.72
    p.blok("Korona bok", (pietra[0][0] * 0.42, hp + 1.2, 1.4), (pietra[0][0] * 0.5, 2.4, pietra[0][0] * 0.5), kor_j, "matowy",
           rot=(0, 40, 0))
    p.blok("Korona bok 2", (-pietra[0][0] * 0.4, hp + 1.8, -1.2), (pietra[0][0] * 0.46, 2.2, pietra[0][0] * 0.46), kor_c, "matowy",
           rot=(0, -25, 0))
    return p


rekwizyt("drzewo_1", "Drzewo krępe", "laka", 20)(
    lambda: _drzewo("drzewo_1", 15, "lisc", "lisc_j", "lisc_c", ((9.0, 5.0), (7.0, 4.2), (4.6, 3.2))))
rekwizyt("drzewo_2", "Drzewo wysokie", "laka", 20)(
    lambda: _drzewo("drzewo_2", 21, "lisc_c", "lisc", "lisc_j", ((7.6, 5.4), (6.4, 5.0), (5.0, 4.4), (3.4, 3.6))))
rekwizyt("drzewo_3", "Drzewo kwitnące", "laka", 20)(
    lambda: _drzewo("drzewo_3", 13, "rozowy", "bialy", "rozowy", ((8.0, 4.4), (6.0, 3.6), (3.8, 2.8))))


@rekwizyt("grzyb", "Grzyb", "laka", 8)
def grzyb():
    p = _nowy("grzyb", "Grzyb", faza=0.08)
    p.walec("Trzon", (0, 0.45, 0), (0.5, 0.9, 0.5), "trzon", "matowy", segm=8)
    p.walec("Kapelusz", (0, 1.05, 0), (1.5, 0.5, 1.5), "kapelusz", "matowy", segm=8)
    p.walec("Czubek", (0, 1.38, 0), (0.9, 0.3, 0.9), "kapelusz", "matowy", segm=8)
    for x, z in ((0.4, 0.3), (-0.35, -0.2)):
        p.blok("Kropka", (x, 1.32, z), (0.26, 0.1, 0.26), "bialy", "matowy", faza=0.02)
    return p


@rekwizyt("kloda", "Zwalona kłoda", "laka", 8)
def kloda():
    p = _nowy("kloda", "Kłoda", faza=0.1)
    p.walec("Kloda", (0, 0.9, 0), (1.8, 6.4, 1.8), "pien", "matowy", rot=(0, 0, 90), segm=8)
    for x in (3.22, -3.22):
        p.walec("Sloje", (x, 0.9, 0), (1.5, 0.1, 1.5), "pien_j", "matowy", rot=(0, 0, 90), segm=8)
    p.walec("Opaska", (-1.2, 0.9, 0), (1.98, 0.8, 1.98), "pien_c", "matowy", rot=(0, 0, 90), segm=8)
    p.blok("Mech", (1.0, 1.78, 0), (2.4, 0.2, 1.2), "mech", "matowy", faza=0.06)
    p.walec("Grzybek trzon", (2.2, 2.0, 0.3), (0.3, 0.5, 0.3), "trzon", "matowy", segm=8)
    p.walec("Grzybek", (2.2, 2.34, 0.3), (0.8, 0.3, 0.8), "kapelusz", "matowy", segm=8)
    return p


@rekwizyt("drogowskaz", "Drogowskaz", "laka", 8)
def drogowskaz():
    p = _nowy("drogowskaz", "Drogowskaz", faza=0.06)
    p.blok("Kamien", (0, 0.3, 0), (1.3, 0.6, 1.3), "kamien", "matowy", rot=(0, 20, 0), faza=0.14)
    p.blok("Slup", (0, 2.4, 0), (0.42, 4.4, 0.42), "pien_c", "matowy")
    for y, zn in ((3.6, 1), (2.6, -1)):
        p.blok("Deska", (zn * 0.9, y, 0.1), (1.9, 0.7, 0.16), "drewno", "matowy", faza=0.04)
        p.klin("Grot deski", (zn * 2.1, y, 0.1), (0.16, 0.7, 0.6), "drewno", "matowy", rot=(0, zn * 90, 90), faza=0.0)
    p.klin("Krysztal", (0, 5.0, 0), (0.36, 0.9, 0.5), "krysztal", "polysk", rot=(0, 30, 0), faza=0.02)
    return p


@rekwizyt("sciana_skalna", "Skalna ściana (odcinek obrzeża łąki)", "laka", 20)
def sciana_skalna():
    # Odcinek obrzeża ok. 24 studów: skały różnej wysokości, ciemna opaska, mech na szczycie. Przód (+Z) ku łące.
    p = _nowy("sciana_skalna", "Skalna ściana", faza=0.5)
    for i, (x, h, d) in enumerate(((-8.6, 7.0, 5.6), (-2.8, 10.0, 6.4), (3.2, 8.0, 5.8), (9.0, 11.0, 6.2))):
        p.blok("Skala", (x, h / 2, -0.4 * (i % 2)), (6.6, h, d), "kamien" if i % 2 else "kamien_j", "matowy", rot=(0, 6 * (i % 3) - 6, 0))
    p.blok("Opaska", (0.2, 4.2, 0.1), (24.4, 0.9, 6.6), "kamien_c", "matowy", faza=0.12)
    p.blok("Mech", (-2.8, 10.1, 0.2), (5.6, 0.3, 5.0), "mech", "matowy", faza=0.1)
    p.blok("Mech 2", (9.0, 11.1, 0.2), (5.4, 0.3, 4.8), "mech", "matowy", faza=0.1)
    return p


# --------------------------------------------------------------------------- głęboki las
def _sosna(id, wys, pietra):
    p = _nowy(id, "Ciemna sosna", faza=0.3)
    hp = wys * 0.26
    p.walec("Pien", (0, hp / 2, 0), (1.9, hp, 1.9), "pien_l", "matowy", segm=8)
    p.walec("Opaska", (0, hp * 0.5, 0), (2.14, 0.8, 2.14), "mrok", "matowy", segm=8)
    y = hp - 0.6
    for i, (sz, h) in enumerate(pietra):                        # piętra igieł: klocki na przemian obrócone o 45°
        p.blok("Pietro %d" % i, (0, y + h / 2, 0), (sz, h, sz), ("igly", "igly_c", "igly_j")[i % 3], "matowy", rot=(0, 45 * (i % 2), 0))
        y += h * 0.8
    p.klin("Czubek", (0, y + 1.0, 0), (1.2, 2.6, 1.6), "igly_j", "matowy", rot=(0, 30, 0), faza=0.04)
    return p


rekwizyt("sosna_1", "Ciemna sosna", "las", 20)(lambda: _sosna("sosna_1", 26, ((10.5, 4.6), (8.6, 4.4), (6.6, 4.2), (4.6, 4.0))))
rekwizyt("sosna_2", "Ciemna sosna wysoka", "las", 20)(
    lambda: _sosna("sosna_2", 34, ((10.0, 5.0), (8.6, 4.8), (7.2, 4.6), (5.6, 4.4), (4.0, 4.0))))


@rekwizyt("grzyb_wielki", "Wielki grzyb z poświatą", "las", 20)
def grzyb_wielki():
    p = _nowy("grzyb_wielki", "Wielki grzyb", faza=0.3)
    p.walec("Trzon", (0, 4.6, 0), (2.8, 9.2, 2.8), "trzon", "matowy", segm=8)
    p.walec("Opaska", (0, 6.4, 0), (3.1, 0.8, 3.1), "fiolet_c", "matowy", segm=8)
    p.walec("Blaszki", (0, 9.1, 0), (10.0, 0.3, 10.0), "grzyb_sw", "swiecacy", segm=8)      # poświata pod kapeluszem
    p.walec("Kapelusz", (0, 10.0, 0), (11.6, 1.7, 11.6), "fiolet", "matowy", segm=8)
    p.walec("Kapelusz 2", (0, 11.3, 0), (8.0, 1.4, 8.0), "fiolet", "matowy", segm=8)
    p.walec("Kapelusz 3", (0, 12.3, 0), (4.4, 1.0, 4.4), "fiolet_c", "matowy", segm=8)
    for a, r_, y in ((20, 4.4, 10.92), (140, 4.0, 10.92), (250, 4.6, 10.92), (80, 2.6, 12.06), (300, 2.4, 12.06)):
        p.blok("Plama", (r_ * math.sin(math.radians(a)), y, r_ * math.cos(math.radians(a))), (1.2, 0.16, 1.2), "grzyb_sw",
               "swiecacy", rot=(0, a, 0), faza=0.04)
    return p


@rekwizyt("grzyby_swiecace", "Świecące grzybki", "las", 8)
def grzyby_swiecace():
    p = _nowy("grzyby_swiecace", "Świecące grzybki", faza=0.06)
    p.blok("Mech", (0, 0.1, 0), (2.2, 0.2, 1.8), "igly", "matowy", rot=(0, 25, 0))
    for x, z, h in ((0, 0, 1.5), (0.7, 0.4, 0.9), (-0.6, 0.3, 1.1)):
        p.walec("Trzon", (x, h / 2, z), (0.26, h, 0.26), "trzon", "matowy", segm=8)
        p.walec("Kapelusz", (x, h + 0.14, z), (0.9, 0.34, 0.9), "grzyb_sw", "swiecacy", segm=8)
    return p


@rekwizyt("luk_korzeni", "Łuk z korzeni", "las", 20)
def luk_korzeni():
    p = _nowy("luk_korzeni", "Łuk z korzeni", faza=0.3)
    for zn in (1, -1):
        p.blok("Korzen dol", (zn * 6.2, 2.2, 0), (2.6, 4.8, 2.6), "pien_l", "matowy", rot=(0, 0, zn * 10))
        p.blok("Korzen srodek", (zn * 5.0, 6.2, 0), (2.3, 4.4, 2.3), "pien", "matowy", rot=(0, 0, zn * 32))
        p.blok("Korzen gora", (zn * 2.6, 8.8, 0), (4.6, 2.1, 2.1), "pien_l", "matowy", rot=(0, 0, -zn * 16))
        p.klin("Korzen stopa", (zn * 7.6, 0.8, 0.6), (1.6, 1.6, 2.6), "pien", "matowy", rot=(0, zn * 70, 0), faza=0.04)
        p.blok("Opaska", (zn * 6.0, 3.4, 0), (2.9, 0.8, 2.9), "mrok", "matowy", rot=(0, 0, zn * 10), faza=0.1)
    p.blok("Zwornik", (0, 9.6, 0), (2.6, 2.3, 2.4), "pien", "matowy", rot=(0, 0, 45))
    p.blok("Mech", (0.4, 10.9, 0), (3.6, 0.3, 2.2), "igly_j", "matowy", faza=0.08)
    p.walec("Grzybek trzon", (6.6, 5.1, 1.0), (0.3, 0.7, 0.3), "trzon", "matowy", segm=8)
    p.walec("Grzybek", (6.6, 5.5, 1.0), (1.0, 0.36, 1.0), "grzyb_sw", "swiecacy", segm=8)
    return p


@rekwizyt("filar_ruin", "Filar ruin", "las", 20)
def filar_ruin():
    p = _nowy("filar_ruin", "Filar ruin", faza=0.16)
    p.blok("Cokol", (0, 0.6, 0), (4.0, 1.2, 4.0), "kamien_c", "matowy")
    p.walec("Trzon", (0, 4.6, 0), (2.6, 6.8, 2.6), "kamien", "matowy", segm=8)
    for y in (2.2, 6.6):
        p.walec("Opaska", (0, y, 0), (2.9, 0.6, 2.9), "kamien_c", "matowy", segm=8)
    p.walec("Runa", (0, 4.4, 0), (2.66, 0.18, 2.66), "grzyb_sw", "swiecacy", segm=8)        # magia jeszcze się tli
    p.klin("Ulomek", (0, 8.6, 0), (2.4, 1.6, 2.4), "kamien", "matowy", rot=(0, 30, 0), faza=0.06)
    p.blok("Gruz", (2.8, 0.5, 1.4), (1.8, 1.0, 1.4), "kamien_j", "matowy", rot=(10, 35, 6))
    p.blok("Mech", (-0.6, 1.26, 0.8), (2.0, 0.16, 1.6), "igly_j", "matowy", faza=0.06)
    return p


@rekwizyt("krag_kamienny", "Kamienny krąg", "las", 80)
def krag_kamienny():
    p = _nowy("krag_kamienny", "Kamienny krąg", faza=0.3)
    p.walec("Plyta", (0, 0.2, 0), (9.0, 0.4, 9.0), "kamien_c", "matowy", segm=8)
    p.walec("Runy", (0, 0.42, 0), (7.0, 0.1, 7.0), "grzyb_sw", "swiecacy", segm=8)
    p.walec("Plyta srodka", (0, 0.5, 0), (5.6, 0.2, 5.6), "kamien", "matowy", segm=8)
    for i in range(7):
        a = math.radians(i * 360 / 7.0 + 12)
        h = 6.5 + 1.6 * (i % 3)
        p.blok("Menhir", (9.5 * math.sin(a), h / 2, 9.5 * math.cos(a)), (2.6, h, 1.9), "kamien" if i % 2 else "kamien_j", "matowy",
               rot=(4 * (i % 2), math.degrees(a), 3 - 3 * (i % 3)))
        if i % 2 == 0:
            p.blok("Opaska", (9.5 * math.sin(a), h * 0.62, 9.5 * math.cos(a)), (2.86, 0.7, 2.1), "kamien_c", "matowy",
                   rot=(0, math.degrees(a), 3 - 3 * (i % 3)), faza=0.1)
    p.klin("Krysztal", (0, 1.9, 0), (0.9, 2.8, 1.3), "krysztal", "swiecacy", rot=(0, 20, 0), faza=0.02)
    p.klin("Krysztal 2", (0.7, 1.2, 0.3), (0.6, 1.5, 0.9), "krysztal", "polysk", rot=(0, 110, 14), faza=0.02)
    return p


# --------------------------------------------------------------------------- legowisko
@rekwizyt("legowisko_krag", "Skalny krąg legowiska", "legowisko", 80)
def legowisko_krag():
    """Podkowa skał o promieniu 13 (jak legowisko w grze), otwarta ku +Z; z tyłu wyższa, z okapem — rama dla cokołów i skarbu."""
    p = _nowy("legowisko_krag", "Skalny krąg legowiska", faza=0.5)
    for i in range(11):
        a = math.radians(-125 + i * 25)                         # −125° … +125° wokół tyłu (−Z)
        tyl = math.cos(a)                                       # 1 = sam tył
        h = 4.0 + 6.5 * max(0.0, tyl) + 1.2 * (i % 2)
        x, z = 13.5 * math.sin(a), -13.5 * math.cos(a)
        p.blok("Skala", (x, h / 2, z), (6.6, h, 4.6), "kamien" if i % 2 else "kamien_j", "matowy", rot=(0, -math.degrees(a), 3 * (i % 3) - 3))
        if i % 2 == 0:
            p.blok("Opaska", (x, h * 0.6, z), (6.9, 0.8, 4.9), "kamien_c", "matowy", rot=(0, -math.degrees(a), 3 * (i % 3) - 3), faza=0.1)
    p.blok("Okap", (0, 11.4, -11.4), (15.0, 1.6, 7.0), "kamien_c", "matowy", rot=(8, 0, 0), faza=0.3)
    p.blok("Okap 2", (0, 12.6, -12.6), (9.0, 1.2, 5.0), "kamien", "matowy", rot=(8, 0, 0), faza=0.3)
    for x in (-5.2, 0.0, 5.2):                                  # żar w szczelinach tylnej ściany
        p.blok("Zar", (x, 4.6, -11.7), (0.5, 6.4, 0.4), "zar", "swiecacy", faza=0.0)
    for x, zn in ((-12.2, 1), (12.2, -1)):
        p.klin("Krysztal", (x, 7.2, 5.4), (0.8, 2.6, 1.2), "krysztal", "polysk", rot=(0, zn * 40, zn * 8), faza=0.02)
        p.klin("Krysztal 2", (x * 0.52, 12.6, -11.2), (0.7, 2.2, 1.0), "krysztal", "polysk", rot=(0, zn * 20, -zn * 10), faza=0.02)
    return p


@rekwizyt("legowisko_brama", "Brama legowiska", "legowisko", 20)
def legowisko_brama():
    p = _nowy("legowisko_brama", "Brama legowiska", faza=0.3)
    for zn in (1, -1):
        p.blok("Filar", (zn * 4.6, 3.6, 0), (2.4, 7.2, 2.4), "kamien", "matowy", rot=(0, 0, -zn * 3))
        p.blok("Opaska", (zn * 4.56, 4.6, 0), (2.66, 0.8, 2.66), "kamien_c", "matowy", rot=(0, 0, -zn * 3), faza=0.1)
        p.blok("Stopa", (zn * 4.8, 0.5, 0.2), (3.2, 1.0, 3.2), "kamien_j", "matowy", rot=(0, zn * 14, 0))
        p.klin("Krysztal", (zn * 4.4, 9.4, 0), (0.7, 2.0, 1.0), "krysztal", "polysk", rot=(0, 90, zn * 10), faza=0.02)
    p.blok("Nadproze", (0, 7.9, 0), (12.6, 1.5, 2.8), "kamien_c", "matowy", rot=(0, 0, 2), faza=0.2)
    p.blok("Zar", (0, 7.08, 0), (8.6, 0.18, 2.2), "zar", "swiecacy", faza=0.0)
    return p


@rekwizyt("sztandar", "Chorągiew w kolorze gracza", "legowisko", 8)
def sztandar():
    p = _nowy("sztandar", "Chorągiew", faza=0.05)
    p.blok("Kamien", (0, 0.4, 0), (1.5, 0.8, 1.5), "kamien", "matowy", rot=(0, 25, 0), faza=0.16)
    p.blok("Drzewce", (0, 4.8, 0), (0.4, 9.0, 0.4), "pien_c", "matowy")
    p.blok("Poprzeczka", (1.3, 8.6, 0), (3.0, 0.3, 0.3), "pien_c", "matowy")
    p.blok("Plat", (1.5, 6.9, 0), (2.4, 3.0, 0.14), "cialo", "matowy", faza=0.0)             # region „cialo” = kolor gracza
    p.klin("Plat dol", (1.5, 4.8, 0), (0.14, 2.4, 1.2), "cialo", "matowy", rot=(90, 0, 90), faza=0.0)
    p.blok("Znak", (1.5, 7.0, 0.1), (0.9, 0.9, 0.08), "zar_j", "swiecacy", rot=(0, 0, 45), faza=0.0)
    p.klin("Krysztal", (0, 9.8, 0), (0.4, 1.0, 0.6), "krysztal", "polysk", rot=(0, 30, 0), faza=0.02)
    return p


# --------------------------------------------------------------------------- wyspa lawy
def _bazalt(id, n):
    p = _nowy(id, "Słupy bazaltu", faza=0.12)
    los = random.Random(len(id) + n)
    for i in range(n):
        a = math.radians(i * 360.0 / n + 15)
        r_ = 0.0 if i == 0 else 2.3
        h = (9.0 if i == 0 else 3.0 + 5.0 * los.random())
        p.blok("Slup", (r_ * math.sin(a), h / 2, r_ * math.cos(a)), (2.2, h, 2.2), "bazalt" if i % 2 else "bazalt_c", "matowy",
               rot=(0, 30 * i, 0))
    p.walec("Zar", (0, 0.12, 0), (6.2, 0.24, 6.2), "zar", "swiecacy", segm=8)
    return p


rekwizyt("bazalt_1", "Słupy bazaltu (5)", "lawa", 20)(lambda: _bazalt("bazalt_1", 5))
rekwizyt("bazalt_2", "Słupy bazaltu (7)", "lawa", 20)(lambda: _bazalt("bazalt_2", 7))


@rekwizyt("skala_lawy", "Skała z żarem w szczelinach", "lawa", 20)
def skala_lawy():
    p = _nowy("skala_lawy", "Skała lawy", faza=0.4)
    p.blok("Rdzen", (0, 1.5, 0), (4.0, 2.6, 3.6), "zar", "swiecacy", rot=(0, 20, 0), faza=0.0)   # żar widać w szczelinach
    p.blok("Skala", (-1.2, 1.5, 0.2), (2.6, 3.2, 4.2), "bazalt", "matowy", rot=(0, 20, 3))
    p.blok("Skala 2", (1.4, 1.3, -0.3), (2.6, 2.8, 4.0), "bazalt_c", "matowy", rot=(0, 20, -4))
    p.blok("Skala 3", (0.1, 2.9, 0.9), (3.2, 1.2, 1.8), "bazalt", "matowy", rot=(0, 20, 0))
    p.blok("Skala 4", (0.2, 2.8, -1.2), (2.8, 1.1, 1.6), "bazalt_c", "matowy", rot=(0, 20, 0))
    p.blok("Rdzen jasny", (0.1, 3.0, -0.1), (1.6, 1.0, 0.3), "zar_j", "swiecacy", rot=(0, 20, 0), faza=0.0)
    p.blok("Odlamek", (2.9, 0.5, 1.6), (1.4, 1.0, 1.2), "bazalt", "matowy", rot=(0, 50, 8))
    return p


@rekwizyt("oltarz_kul", "Ołtarz wielkich kul", "lawa", 80)
def oltarz_kul():
    p = _nowy("oltarz_kul", "Ołtarz wielkich kul", faza=0.3)
    p.walec("Stopien 1", (0, 0.5, 0), (15.0, 1.0, 15.0), "bazalt_c", "matowy", segm=8)
    p.walec("Zar", (0, 1.06, 0), (13.0, 0.16, 13.0), "zar", "swiecacy", segm=8)
    p.walec("Stopien 2", (0, 1.5, 0), (11.0, 1.0, 11.0), "bazalt", "matowy", segm=8)
    p.walec("Zar rdzen", (0, 2.06, 0), (8.4, 0.14, 8.4), "zar_j", "swiecacy", segm=8)
    p.walec("Plyta", (0, 2.4, 0), (7.0, 0.7, 7.0), "kamien_c", "matowy", segm=8)
    p.walec("Gniazdo kuli", (0, 2.9, 0), (3.6, 0.4, 3.6), "zloto", "metal", segm=8)
    for i in range(4):
        a = math.radians(45 + 90 * i)
        x, z = 6.4 * math.sin(a), 6.4 * math.cos(a)
        p.blok("Pylon", (x, 4.0, z), (1.7, 6.0, 1.7), "bazalt", "matowy", rot=(0, math.degrees(a), 0))
        p.blok("Opaska", (x, 5.0, z), (1.94, 0.7, 1.94), "bazalt_c", "matowy", rot=(0, math.degrees(a), 0), faza=0.1)
        p.klin("Krysztal", (x, 8.2, z), (0.8, 2.6, 1.2), "krysztal", "swiecacy", rot=(0, math.degrees(a) + 180, 0), faza=0.02)
        p.blok("Kanal zaru", (x * 0.62, 1.04, z * 0.62), (0.6, 0.14, 4.2), "zar_j", "swiecacy", rot=(0, math.degrees(a), 0), faza=0.0)
    p.zaczep("KulaAttachment", "Podstawa", (0, 4.9, 0))
    return p


# --------------------------------------------------------------------------- woda
@rekwizyt("lilia", "Liść lilii z kwiatem", "woda", 8)
def lilia():
    p = _nowy("lilia", "Lilia", faza=0.03)
    p.walec("Lisc", (0, 0.07, 0), (2.6, 0.14, 2.6), "lilia", "matowy", segm=8)
    p.walec("Lisc srodek", (0.2, 0.1, 0.1), (1.5, 0.14, 1.5), "lilia_j", "matowy", segm=8)
    p.blok("Kwiat", (-0.5, 0.36, 0.3), (0.8, 0.3, 0.8), "rozowy", "matowy")
    p.blok("Kwiat 2", (-0.5, 0.4, 0.3), (0.8, 0.26, 0.8), "bialy", "matowy", rot=(0, 45, 0))
    p.blok("Srodek", (-0.5, 0.58, 0.3), (0.3, 0.2, 0.3), "srodek", "matowy")
    return p


@rekwizyt("trzcina", "Trzciny", "woda", 8)
def trzcina():
    p = _nowy("trzcina", "Trzciny", faza=0.03)
    for i, (x, z, h, rz) in enumerate(((0, 0, 4.6, 3), (0.5, 0.3, 3.8, -6), (-0.4, 0.4, 3.2, 8), (0.2, -0.5, 4.0, -3))):
        p.blok("Zdzblo", (x, h / 2, z), (0.16, h, 0.16), "trzcina", "matowy", rot=(0, 0, rz))
        if i < 3:
            p.blok("Palka", (x - rz * 0.035, h - 0.5, z), (0.3, 0.9, 0.3), "palka", "matowy", rot=(0, 0, rz), faza=0.08)
    return p


# --------------------------------------------------------------------------- punkty charakterystyczne
@rekwizyt("czaszka_smoka", "Olbrzymia czaszka smoka", "znak", 80)
def czaszka_smoka():
    p = _nowy("czaszka_smoka", "Czaszka smoka", faza=0.5)
    p.blok("Czaszka", (0, 5.2, -2.0), (11.0, 7.6, 9.6), "kosc", "matowy", rot=(-8, 0, 0))
    p.blok("Pysk", (0, 3.9, 6.6), (7.6, 4.6, 10.4), "kosc", "matowy", rot=(6, 0, 0))
    p.klin("Grzbiet nosa", (0, 6.5, 5.6), (4.6, 1.8, 8.0), "kosc_c", "matowy", rot=(6, 180, 0), faza=0.1)
    p.blok("Pekniecie", (1.6, 9.0, -2.4), (0.4, 0.3, 6.0), "mrok", "matowy", rot=(-8, 14, 0), faza=0.0)
    for zn in (1, -1):
        p.blok("Oczodol", (zn * 3.9, 5.6, 1.9), (2.6, 2.6, 2.4), "mrok", "matowy", rot=(-8, zn * 14, 0), faza=0.2)
        p.blok("Zar oczodolu", (zn * 3.6, 5.5, 1.5), (1.1, 1.1, 1.0), "magia", "swiecacy", faza=0.0)     # coś tam jeszcze świeci
        p.blok("Brew", (zn * 4.2, 7.5, 2.2), (4.0, 1.0, 3.4), "kosc_c", "matowy", rot=(-8, zn * 14, -zn * 12), faza=0.2)
        p.blok("Rog nasada", (zn * 4.4, 9.2, -5.0), (2.2, 2.2, 4.0), "kosc_c", "matowy", rot=(-38, zn * 14, 0), faza=0.2)
        p.klin("Rog", (zn * 5.3, 12.2, -9.0), (1.7, 2.2, 7.0), "kosc", "matowy", rot=(-38, zn * 14, 0), faza=0.06)
        p.klin("Rog policzka", (zn * 6.6, 3.6, -3.4), (1.2, 1.6, 4.6), "kosc", "matowy", rot=(-6, zn * 40, zn * 90), faza=0.06)
        p.blok("Nozdrze", (zn * 1.4, 6.0, 10.6), (1.0, 0.5, 1.4), "mrok", "matowy", rot=(6, 0, 0), faza=0.1)
        for j in range(3):
            p.klin("Zab", (zn * 3.5, 1.1, 4.0 + j * 2.8), (0.7, 1.9, 1.2), "bialy", "polysk", rot=(180, 0, 0), faza=0.04)
        p.blok("Zuchwa", (zn * 3.4, 0.7, 4.0), (1.8, 1.4, 12.0), "kosc_c", "matowy", rot=(0, zn * 9, 0), faza=0.2)
        p.klin("Zab dolny", (zn * 3.8, 2.1, 8.6), (0.7, 1.6, 1.1), "bialy", "polysk", rot=(0, 180, 0), faza=0.04)
        p.blok("Mech", (zn * 2.6, 9.1 - 0.4 * zn, -3.0 - zn), (3.4, 0.3, 3.0), "mech", "matowy", rot=(-8, 0, 0), faza=0.1)
    for j, (z, s_) in enumerate(((-9.0, 4.4), (-13.4, 3.6), (-17.2, 2.8))):                  # kręgi szyi za czaszką
        p.blok("Krag", (0.6 * j, s_ * 0.45, z), (s_ * 1.2, s_ * 0.9, 3.2), "kosc_c" if j % 2 else "kosc", "matowy",
               rot=(0, 8 * j, 5 * j))
    return p


@rekwizyt("posag_prastarego", "Zwietrzały posąg Prastarego Smoka", "znak", 80)
def posag_prastarego():
    """Posąg z brył uproszczonego ANCIENT DRAGON, cały w kamieniu, na cokole; żar zarósł mchem, oczy jeszcze świecą,
    jedno skrzydło odłamane leży obok."""
    lod = zbuduj_stadium_lod(8)
    p = _nowy("posag_prastarego", "Posąg Prastarego Smoka", faza=0.12, skala=2.1)
    p.blok("Cokol", (0, 0.9, -1.0), (8.6, 1.8, 14.0), "kamien_c", "matowy", faza=0.3)
    p.blok("Opaska cokolu", (0, 1.2, -1.0), (8.9, 0.5, 14.3), "mrok", "matowy", faza=0.1)
    p.blok("Cokol gora", (0, 2.0, -1.0), (7.4, 0.5, 12.6), "kamien", "matowy", faza=0.2)
    barwa = {"cialo": "kamien", "luski": "kamien_c", "blona": "kamien_j", "kolce": "kamien_j", "zar": "mech",
             "zar_rdzen": "mech", "oko": "krysztal", "brzuch": "kamien_j", "stale": "kamien"}
    for c in lod.czesci:
        if c["kosc"] == "SkrzydloP2" and c["n"] == "Blona dloni":
            continue                                            # odłamane skrzydło
        j = lod.kosci[c["kosc"]]["staw"]
        reg = c.get("reg", "stale")
        d = dict(c)
        d.update(kosc="Podstawa", p=(j[0] + c["p"][0], j[1] + c["p"][1] + 2.2, j[2] + c["p"][2]), c=PAL[barwa[reg]],
                 m="swiecacy" if reg == "oko" else "matowy", reg="stale")
        p.czesci.append(d)
    p.klin("Odlamek skrzydla", (-7.6, 0.3, 2.0), (0.3, 4.6, 3.6), "kamien_j", "matowy", rot=(0, 30, 90), faza=0.0)
    for x, y, z in ((1.2, 2.32, 3.4), (-2.2, 2.32, -4.0), (2.6, 2.32, -5.6)):
        p.blok("Mech", (x, y, z), (2.2, 0.16, 1.8), "mech", "matowy", rot=(0, 30 * x, 0), faza=0.06)
    return p


@rekwizyt("brama_zapieczetowana", "Zapieczętowana brama", "znak", 80)
def brama_zapieczetowana():
    p = _nowy("brama_zapieczetowana", "Zapieczętowana brama", faza=0.4)
    for zn in (1, -1):
        p.blok("Filar", (zn * 11.5, 14.0, 0), (7.0, 28.0, 7.0), "kamien", "matowy")
        for y in (7.0, 19.0):
            p.blok("Opaska", (zn * 11.5, y, 0), (7.5, 1.6, 7.5), "kamien_c", "matowy", faza=0.16)
        p.blok("Glowica", (zn * 11.5, 28.8, 0), (8.6, 1.8, 8.6), "kamien_c", "matowy", rot=(0, 0, zn * 2))
        p.klin("Krysztal", (zn * 11.5, 33.0, 0), (2.0, 7.0, 3.0), "krysztal", "swiecacy", rot=(0, 90, zn * 6), faza=0.04)
        p.blok("Wrota", (zn * 4.0, 12.0, -0.6), (8.0, 24.0, 2.0), "bazalt", "matowy", faza=0.2)
        p.blok("Lancuch", (zn * 4.2, 12.0, 0.7), (1.0, 20.0, 0.5), "mrok", "matowy", rot=(0, 0, zn * 34), faza=0.1)
        p.blok("Misa", (zn * 17.5, 1.6, 4.0), (3.4, 3.2, 3.4), "kamien_c", "matowy", rot=(0, 20, 0))
        p.blok("Ogien misy", (zn * 17.5, 3.5, 4.0), (2.2, 1.0, 2.2), "zar", "swiecacy", rot=(0, 45, 0), faza=0.0)
    p.blok("Nadproze", (0, 26.6, 0), (30.0, 5.0, 8.0), "kamien", "matowy", faza=0.3)
    p.blok("Dachowka nadproza", (0, 29.6, 0), (32.0, 1.4, 9.4), "kamien_c", "matowy", rot=(4, 0, 0), faza=0.2)
    p.walec("Pieczec", (0, 13.0, 0.6), (13.0, 0.6, 13.0), "mrok", "matowy", rot=(90, 0, 0), segm=8)
    p.walec("Pieczec zar", (0, 13.0, 0.8), (11.0, 0.5, 11.0), "magia", "swiecacy", rot=(90, 0, 0), segm=8)
    p.walec("Pieczec srodek", (0, 13.0, 1.0), (8.0, 0.5, 8.0), "mrok", "matowy", rot=(90, 0, 0), segm=8)
    p.blok("Klejnot pieczeci", (0, 13.0, 1.3), (3.2, 3.2, 0.6), "magia", "swiecacy", rot=(0, 0, 45), faza=0.0)
    for a in (0, 90, 180, 270):
        p.blok("Runa", (4.0 * math.sin(math.radians(a)), 13.0 + 4.0 * math.cos(math.radians(a)), 1.3), (0.7, 2.0, 0.3),
               "krysztal", "swiecacy", rot=(0, 0, -a), faza=0.0)
    p.blok("Stopien", (0, 0.5, 5.0), (20.0, 1.0, 6.0), "kamien_c", "matowy", faza=0.2)
    p.blok("Stopien 2", (0, 1.3, 3.4), (17.0, 0.8, 3.4), "kamien", "matowy", faza=0.2)
    return p


# --------------------------------------------------------------------------- kule (małe, duże, wielkie)
def _kula(id, r, kolor, pierscienie, kolce):
    """Kula do zebrania: świecąca kula nad ziemią, ciemna opaska (styl), złote pierścienie = stopień (0, 1, 2)."""
    p = _nowy(id, "Kula", faza=0.02)
    y = r + 0.6
    p.walec("Blask na ziemi", (0, 0.04, 0), (r * 3.0, 0.08, r * 3.0), kolor, "swiecacy", segm=8)
    p.kula("Kula", (0, y, 0), 2 * r, kolor, "swiecacy", segm=12)
    p.walec("Opaska", (0, y, 0), (2 * r * 1.03, r * 0.28, 2 * r * 1.03), "mrok", "matowy", segm=8)
    for i in range(pierscienie):
        p.walec("Pierscien", (0, y, 0), (r * 3.1 + 0.5 * i, 0.16 + 0.04 * r, r * 3.1 + 0.5 * i), "zloto", "metal",
                rot=(24 if i == 0 else -30, 60 * i, 12), segm=8)
    for i in range(kolce):
        a = math.radians(i * 360.0 / max(1, kolce) + 45)
        p.klin("Krysztal", (r * 1.7 * math.sin(a), y + r * 0.2, r * 1.7 * math.cos(a)), (r * 0.22, r * 0.9, r * 0.36), "krysztal",
               "swiecacy", rot=(0, math.degrees(a), 0), faza=0.0)
    return p


rekwizyt("kula_mala", "Kula mała", "kule", 8)(lambda: _kula("kula_mala", 0.6, "kula1", 0, 0))
rekwizyt("kula_duza", "Kula duża", "kule", 8)(lambda: _kula("kula_duza", 1.15, "kula2", 1, 0))
rekwizyt("kula_wielka", "Kula wielka", "kule", 8)(lambda: _kula("kula_wielka", 1.6, "kula3", 2, 3))


# --------------------------------------------------------------------------- stos złota (nowy skarb: monety i klejnoty)
def _stos_zlota(rozmiar):
    """Stos złota jako usypany kopiec monet: obłe bryły złota, na nich monety pochylone zgodnie ze zboczem, klejnoty,
    stosiki monet u podnóża. Rozmiar 1–3 (ok. 17 / 34 / 70 części)."""
    R = {1: 2.4, 2: 3.8, 3: 5.8}[rozmiar]
    p = _nowy("stos_zlota_%d" % rozmiar, "Stos złota %d" % rozmiar, faza=0.04)
    los = random.Random(70 + rozmiar)
    kopce = [(0.0, 0.0, R, R * 0.52)] + [(R * 0.5 * math.cos(2.1 * i + 0.4), R * 0.5 * math.sin(2.1 * i + 0.4), R * 0.62, R * 0.3)
                                         for i in range(rozmiar)]
    for i, (x, z, r_, h) in enumerate(kopce):
        p.kula("Kopiec", (x, 0.0, z), (2 * r_, 2 * h, 2 * r_), "zloto" if i else "zloto_c", "metal", segm=12)
    for i in range({1: 10, 2: 20, 3: 40}[rozmiar]):
        az, el = los.uniform(0, 360), los.uniform(8, 78)
        a, e = math.radians(az), math.radians(el)
        pos = (R * 0.98 * math.cos(e) * math.cos(a), R * 0.52 * math.sin(e) + 0.02, R * 0.98 * math.cos(e) * math.sin(a))
        with p.uklad(pos=pos, obrot=(90 - el, 90 - az, 0)):
            if i % 5 == 4:
                p.blok("Klejnot", (0, 0.22, 0), (0.5, 0.5, 0.5), ("rubin", "szmaragd", "szafir", "magia")[i // 5 % 4], "swiecacy",
                       rot=(45, 20, 45), faza=0.0)
            else:
                p.walec("Moneta", (0, 0.07, 0), (0.86, 0.14, 0.86), ("zloto_j", "zloto", "zloto_j", "zloto_c")[i % 4], "metal",
                        rot=(los.uniform(-10, 10), 0, los.uniform(-10, 10)), segm=8)
    for i in range(rozmiar * 2):
        a = math.radians(los.uniform(0, 360))
        rr = R * los.uniform(1.02, 1.2)
        p.walec("Stosik monet", (rr * math.cos(a), 0.16 + 0.1 * (i % 2), rr * math.sin(a)), (0.8, 0.32 + 0.2 * (i % 2), 0.8), "zloto_j",
                "metal", segm=8)
    if rozmiar == 3:                                            # korona i kielich na szczycie
        p.walec("Korona", (0.6, R * 0.52 + 0.3, 0.2), (1.5, 0.5, 1.5), "zloto_j", "metal", rot=(8, 0, -10), segm=8)
        for a in (0, 120, 240):
            p.klin("Zab korony", (0.6 + 0.6 * math.sin(math.radians(a)), R * 0.52 + 0.8, 0.2 + 0.6 * math.cos(math.radians(a))),
                   (0.3, 0.6, 0.3), "zloto_j", "metal", rot=(0, a, 0), faza=0.0)
        p.blok("Klejnot korony", (0.6, R * 0.52 + 0.72, 0.9), (0.4, 0.4, 0.2), "rubin", "swiecacy", rot=(0, 0, 45), faza=0.0)
        p.walec("Kielich", (-1.6, R * 0.44 + 0.5, 0.8), (0.9, 1.0, 0.9), "zloto_j", "metal", rot=(30, 0, 20), segm=8)
    p.zaczep("SzczytAttachment", "Podstawa", (0, R * 0.52 + 0.1, 0))
    return p


for _r in (1, 2, 3):
    rekwizyt("stos_zlota_%d" % _r, "Stos złota %d (monety i klejnoty)" % _r, "legowisko", (20, 40, 80)[_r - 1])(
        lambda _r=_r: _stos_zlota(_r))


def zbuduj(id):
    return next(fn for i, _, _, _, fn in ZESTAW if i == id)()


def wszystkie():
    """[(Postac, strefa, limit części), …] w kolejności spisu."""
    return [(fn(), strefa, limit) for _, _, strefa, limit, fn in ZESTAW]
