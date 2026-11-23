# -*- coding: utf-8 -*-
"""Zestaw świata — runda 7 (mapa v2): NOWE rekwizyty w języku „Żarołuski” dla rzeźby terenu, bram rozmiaru,
kryjówek, rzeczy do rozbicia, sekretów i prądów wznoszących. Ten sam format co swiat_zestaw.py (jedna kość
„Podstawa”, przód +Z, ziemia y = 0, jednostka = stud), osobny spis ZESTAW2 — swiat_zestaw.ZESTAW zostaje bez zmian.

    from swiat.ewolucja.modele import swiat_zestaw2
    swiat_zestaw2.wszystkie()        # [(Postac, strefa, limit części), …]

Kolor = znaczenie (czytelne z kamery gry):
- żar (FF7A2A) w pęknięciach = „rozbij mnie” (tylko duże smoki, od stadium 6);
- żółta łapka (FFE14D) nad przejściem = brama „mała” (stadia 1–3), błękitna (7FF8FF) = „średnia” (stadia 1–5);
- białobłękitne wiry = prąd wznoszący (WING GLIDE);
- latarnie: błękit — las, żar — kanion i kaldera, róż — zapieczętowana brama, złoto — jezioro i wodospad.
"""
import math

from swiat.ewolucja.modele.swiat_zestaw import PAL as _PAL0, _nowy as _nowy0

PAL = dict(_PAL0)
PAL.update({
    "trawa_w": "9ACD4A", "trawa_wc": "5E9E36", "trawa_wj": "C4E46A", "klos": "E8D36A",
    "paproc": "2F8A4E", "paproc_c": "1E6A3C", "paproc_j": "4FB06A",
    "martwe": "B8A994", "martwe_c": "5A4A3E", "martwe_j": "D8CDB8",
    "ziemia": "7A5A3E", "ziemia_c": "4E3828", "dziura": "1A1424",
    "woda": "3E8FD8", "woda_j": "9FE3FF", "piana": "F4FBFF",
    "kanion": "C78F5E", "kanion_c": "6B3F33", "kanion_j": "E0AE7A",
    "lapka_mala": "FFE14D", "lapka_srednia": "7FF8FF", "wiatr": "9FE6FF", "wiatr_j": "FFFFFF",
    "tkanina": "E3412B", "jajo": "FFF1C8",
})


def _nowy(id, nazwa, faza=0.1, skala=1.0):
    p = _nowy0(id, nazwa, faza=faza, skala=skala)
    p.paleta.update(PAL)
    return p


ZESTAW2 = []          # [(id, nazwa, strefa, limit części, funkcja)]


def rekwizyt(id, nazwa, strefa, limit):
    def dekorator(fn):
        ZESTAW2.append((id, nazwa, strefa, limit, fn))
        return fn
    return dekorator


def _katy(n, start=0.0):
    return [math.radians(start + 360.0 * i / n) for i in range(n)]


# --------------------------------------------------------------------------- kryjówki
@rekwizyt("trawa_wysoka", "Wysoka trawa (kryjówka, ok. 6 × 6)", "kryjowka", 10)
def trawa_wysoka():
    """Gęsta kępa wysokich źdźbeł z kłosami — z góry żółtozielona plama, wyraźnie inna niż zwykła trawa."""
    p = _nowy("trawa_wysoka", "Wysoka trawa", faza=0.0)
    p.blok("Kepa", (0, 0.5, 0), (5.2, 1.0, 5.0), "trawa_wc", "matowy", rot=(0, 20, 0))
    for i, a in enumerate(_katy(7, 10)):
        r_ = 1.0 + 1.2 * (i % 3) / 2.0
        h = 3.0 + 0.5 * (i % 3)
        p.klin("Zdzblo", (r_ * math.sin(a), h / 2, r_ * math.cos(a)), (0.9, h, 1.4),
               ("trawa_w", "trawa_wj", "trawa_w")[i % 3], "matowy", rot=(0, math.degrees(a) + 180, 6 - 4 * (i % 3)))
    p.blok("Klosy", (0.3, 3.5, -0.2), (2.4, 0.3, 2.2), "klos", "matowy", rot=(0, 35, 0), faza=0.04)
    return p


@rekwizyt("paproc", "Kępa paproci (kryjówka w lesie, ok. 6 × 6)", "kryjowka", 10)
def paproc():
    p = _nowy("paproc", "Paproć", faza=0.04)
    p.blok("Srodek", (0, 0.6, 0), (1.6, 1.2, 1.6), "paproc_c", "matowy", rot=(0, 45, 0))
    for i, a in enumerate(_katy(6, 15)):
        p.klin("Lisc", (2.0 * math.sin(a), 1.25, 2.0 * math.cos(a)), (1.3, 2.3, 3.6),
               ("paproc", "paproc_j", "paproc_c")[i % 3], "matowy", rot=(-24, math.degrees(a), 0), faza=0.0)
    return p


# --------------------------------------------------------------------------- do rozbicia (od stadium 6)
@rekwizyt("skala_lamliwa", "Pękająca skała (rozbij: stadium 6+)", "lamliwe", 14)
def skala_lamliwa():
    """Głazowisko z żarzącymi się pęknięciami — żar w szczelinach mówi „to da się rozbić”. Ok. 9 × 7 × 7."""
    p = _nowy("skala_lamliwa", "Pękająca skała", faza=0.4)
    p.blok("Rdzen zaru", (0, 2.6, 0), (6.0, 4.4, 4.6), "zar", "swiecacy", rot=(0, 12, 0), faza=0.0)
    p.blok("Glaz", (-1.6, 2.8, 0.2), (4.4, 5.6, 5.2), "kamien", "matowy", rot=(0, 12, 4))
    p.blok("Glaz 2", (2.0, 2.4, -0.3), (4.0, 4.8, 5.0), "kamien_j", "matowy", rot=(0, 12, -5))
    p.blok("Glaz 3", (0.4, 5.6, 0.1), (5.2, 2.0, 3.6), "kamien", "matowy", rot=(0, 30, 3))
    p.blok("Opaska", (-1.6, 3.4, 0.2), (4.7, 0.7, 5.5), "kamien_c", "matowy", rot=(0, 12, 4), faza=0.1)
    p.blok("Pekniecie", (0.2, 3.2, 2.6), (0.4, 4.6, 0.3), "zar_j", "swiecacy", rot=(0, 12, 8), faza=0.0)
    p.blok("Odlamek", (3.8, 0.7, 2.0), (1.8, 1.4, 1.6), "kamien_j", "matowy", rot=(10, 40, 6))
    p.blok("Odlamek 2", (-3.9, 0.6, -1.6), (1.6, 1.2, 1.8), "kamien", "matowy", rot=(0, -20, 8))
    p.blok("Mech", (-1.4, 5.66, 0.6), (2.6, 0.2, 2.0), "mech", "matowy", rot=(0, 12, 4), faza=0.06)
    return p


@rekwizyt("drzewo_martwe", "Martwe drzewo (rozbij: stadium 6+)", "lamliwe", 14)
def drzewo_martwe():
    p = _nowy("drzewo_martwe", "Martwe drzewo", faza=0.3)
    p.walec("Pien", (0, 4.5, 0), (2.2, 9.0, 2.2), "martwe", "matowy", segm=8)
    p.walec("Opaska", (0, 3.4, 0), (2.46, 0.8, 2.46), "martwe_c", "matowy", segm=8)
    p.blok("Konar", (1.9, 8.6, 0), (4.2, 0.9, 0.9), "martwe", "matowy", rot=(0, 0, 32))
    p.blok("Konar 2", (-1.6, 10.2, 0.4), (3.6, 0.8, 0.8), "martwe_j", "matowy", rot=(0, 30, -38))
    p.blok("Konar 3", (0.3, 11.2, -1.2), (0.7, 3.2, 0.7), "martwe", "matowy", rot=(-14, 0, 8))
    p.blok("Pekniecie", (0, 5.0, 1.12), (0.36, 4.6, 0.12), "zar", "swiecacy", rot=(0, 0, 6), faza=0.0)
    for a in (40, 170, 290):
        p.klin("Korzen", (1.2 * math.sin(math.radians(a)), 0.5, 1.2 * math.cos(math.radians(a))), (0.8, 1.0, 1.6),
               "martwe_c", "matowy", rot=(0, a + 180, 0), faza=0.04)
    return p


@rekwizyt("kloda_martwa", "Zwalone martwe drzewo — zapora (rozbij: stadium 6+)", "lamliwe", 14)
def kloda_martwa():
    """Leżący pień z konarami, ok. 14 × 4 — zagradza przejście; środek w (0, 0)."""
    p = _nowy("kloda_martwa", "Zwalone martwe drzewo", faza=0.3)
    p.walec("Pien", (0, 1.4, 0), (2.6, 13.0, 2.6), "martwe", "matowy", rot=(0, 0, 90), segm=8)
    p.walec("Opaska", (-2.6, 1.4, 0), (2.9, 0.9, 2.9), "martwe_c", "matowy", rot=(0, 0, 90), segm=8)
    p.walec("Sloje", (6.55, 1.4, 0), (2.2, 0.1, 2.2), "martwe_j", "matowy", rot=(0, 0, 90), segm=8)
    p.blok("Konar", (-3.6, 2.8, 1.4), (0.8, 3.6, 0.8), "martwe", "matowy", rot=(40, 0, 20))
    p.blok("Konar 2", (2.6, 3.0, -1.2), (0.8, 3.4, 0.8), "martwe_j", "matowy", rot=(-35, 0, -15))
    p.blok("Bryla korzeni", (-6.8, 2.2, 0), (1.2, 4.4, 4.2), "martwe_c", "matowy", rot=(0, 0, 8))
    p.blok("Pekniecie", (0.8, 2.72, 0), (3.4, 0.14, 0.4), "zar", "swiecacy", faza=0.0)
    return p


# --------------------------------------------------------------------------- bramy rozmiaru
@rekwizyt("luk_niski", "Niski kamienny łuk — brama rozmiaru (prześwit 7 × 5,5)", "brama", 12)
def luk_niski():
    """Łuk nad przejściem: prześwit 7 studów szerokości i 5,5 wysokości; nad środkiem świecący znak łapki
    (żółty = „mała”, region `zar_j` — gra może przemalować na błękit dla bramy „średniej”)."""
    p = _nowy("luk_niski", "Niski łuk", faza=0.25)
    for zn in (1, -1):
        p.blok("Filar", (zn * 4.6, 2.9, 0), (2.2, 5.8, 3.0), "kamien", "matowy", rot=(0, 0, -zn * 2))
        p.blok("Opaska", (zn * 4.6, 2.6, 0), (2.46, 0.6, 3.26), "kamien_c", "matowy", faza=0.08)
    p.blok("Nadproze", (0, 6.5, 0), (11.6, 1.6, 3.4), "kamien_j", "matowy", faza=0.3)
    p.blok("Mech", (0.6, 7.38, 0), (6.0, 0.24, 2.8), "mech", "matowy", faza=0.06)
    p.blok("Lapka", (0, 6.5, 1.74), (1.2, 0.9, 0.12), "lapka_mala", "swiecacy", faza=0.0)
    for x in (-0.75, 0.0, 0.75):
        p.blok("Palec", (x, 7.1, 1.74), (0.42, 0.42, 0.12), "lapka_mala", "swiecacy", faza=0.0)
    return p


@rekwizyt("nora", "Wejście do nory (kopiec z ciemnym otworem)", "brama", 12)
def nora():
    """Kopiec ziemi z ciemnym otworem 6 × 4 — znak wejścia do tunelu dla małych; przód (+Z) = wejście."""
    p = _nowy("nora", "Nora", faza=0.3)
    p.blok("Kopiec", (0, 2.2, -1.2), (10.0, 4.4, 6.0), "ziemia", "matowy", rot=(-6, 0, 0))
    p.klin("Zbocze", (-4.4, 1.6, 1.6), (2.6, 3.2, 3.6), "ziemia_c", "matowy", rot=(0, 180, 0))
    p.klin("Zbocze 2", (4.4, 1.6, 1.6), (2.6, 3.2, 3.6), "ziemia_c", "matowy", rot=(0, 180, 0))
    p.blok("Otwor", (0, 1.9, 1.82), (5.4, 3.8, 0.4), "dziura", "matowy", faza=0.2)
    p.blok("Prog", (0, 0.2, 2.6), (6.4, 0.4, 1.4), "ziemia_c", "matowy", faza=0.1)
    p.blok("Trawa", (0.4, 4.5, -1.0), (8.0, 0.3, 5.0), "trawa_c", "matowy", rot=(-6, 0, 0), faza=0.08)
    p.walec("Korzen", (-2.6, 4.0, 1.4), (0.5, 3.0, 0.5), "pien_c", "matowy", rot=(0, 0, 70), segm=8)
    p.blok("Lapka", (0, 4.5, 1.9), (1.0, 0.8, 0.12), "lapka_mala", "swiecacy", faza=0.0)
    return p


# --------------------------------------------------------------------------- sekrety
@rekwizyt("skrzynia_ukryta", "Ukryta skrzynia (sekret)", "sekret", 16)
def skrzynia_ukryta():
    p = _nowy("skrzynia_ukryta", "Ukryta skrzynia", faza=0.12)
    p.blok("Skrzynia", (0, 0.9, 0), (3.4, 1.8, 2.3), "drewno", "matowy")
    p.blok("Wieko", (0, 2.05, 0), (3.5, 0.6, 2.4), "pien", "matowy", faza=0.2)
    p.blok("Okucie", (-1.1, 1.2, 0), (0.36, 2.0, 2.5), "zloto", "metal", faza=0.04)
    p.blok("Okucie 2", (1.1, 1.2, 0), (0.36, 2.0, 2.5), "zloto", "metal", faza=0.04)
    p.blok("Opaska", (0, 1.7, 0), (3.6, 0.3, 2.5), "mrok", "matowy", faza=0.04)
    p.blok("Zamek", (0, 1.65, 1.26), (0.7, 0.8, 0.2), "krysztal", "swiecacy", faza=0.0)
    p.blok("Blask", (0, 2.32, 0), (2.8, 0.12, 1.8), "zloto_j", "swiecacy", faza=0.0)
    for i, (x, z) in enumerate(((1.9, 1.3), (-2.0, 0.9), (1.5, -1.5))):
        p.walec("Moneta", (x, 0.08 + 0.05 * i, z), (0.8, 0.14, 0.8), "zloto_j", "metal", segm=8)
    p.zaczep("SkrzyniaAttachment", "Podstawa", (0, 2.6, 0))
    return p


@rekwizyt("kamien_runiczny", "Kamień runiczny (zestaw 6 do zebrania)", "sekret", 10)
def kamien_runiczny():
    p = _nowy("kamien_runiczny", "Kamień runiczny", faza=0.25)
    p.blok("Kamien", (0, 2.6, 0), (2.4, 5.2, 1.6), "kamien_j", "matowy", rot=(0, 0, 3))
    p.klin("Czubek", (0.05, 5.8, 0), (2.2, 1.2, 1.5), "kamien_j", "matowy", rot=(0, 90, 0), faza=0.1)
    p.blok("Opaska", (0, 1.6, 0), (2.6, 0.6, 1.8), "kamien_c", "matowy", faza=0.08)
    p.blok("Runa", (0, 3.4, 0.82), (1.2, 1.8, 0.1), "krysztal", "swiecacy", rot=(0, 0, 3), faza=0.0)
    p.blok("Runa tyl", (0, 3.4, -0.82), (1.2, 1.8, 0.1), "krysztal", "swiecacy", rot=(0, 0, 3), faza=0.0)
    p.blok("Cokol", (0, 0.3, 0), (3.6, 0.6, 2.8), "kamien_c", "matowy", rot=(0, 15, 0))
    p.blok("Mech", (-0.4, 0.66, 0.6), (1.8, 0.14, 1.2), "mech", "matowy", faza=0.04)
    p.zaczep("RunaAttachment", "Podstawa", (0, 3.4, 0.9))
    return p


@rekwizyt("gniazdo_orle", "Gniazdo na półce skalnej z jajami-skarbem", "sekret", 12)
def gniazdo_orle():
    p = _nowy("gniazdo_orle", "Gniazdo na półce", faza=0.15)
    for i, a in enumerate(_katy(4, 20)):
        p.blok("Galazki", (2.0 * math.sin(a), 0.6, 2.0 * math.cos(a)), (4.0, 1.2, 1.2), ("pien", "pien_c")[i % 2], "matowy",
               rot=(0, math.degrees(a) + 90, 6 * (i % 2)))
    p.walec("Wysciolka", (0, 0.5, 0), (3.4, 0.6, 3.4), "klos", "matowy", segm=8)
    p.kula("Jajo", (-0.6, 1.4, 0.2), (1.4, 1.8, 1.4), "zloto_j", "metal", segm=10)
    p.kula("Jajo 2", (0.7, 1.3, -0.3), (1.2, 1.6, 1.2), "krysztal", "swiecacy", segm=10)
    p.klin("Pioro", (1.8, 1.4, 1.2), (0.2, 0.6, 1.8), "bialy", "matowy", rot=(20, 40, 0), faza=0.0)
    p.zaczep("SkrzyniaAttachment", "Podstawa", (0, 2.4, 0))
    return p


@rekwizyt("punkt_widokowy", "Punkt widokowy: kopiec, ognisko-latarnia, luneta", "sekret", 16)
def punkt_widokowy():
    p = _nowy("punkt_widokowy", "Punkt widokowy", faza=0.25)
    p.blok("Kopiec", (0, 0.9, 0), (5.6, 1.8, 5.6), "kamien_c", "matowy", rot=(0, 20, 0))
    p.blok("Kopiec 2", (0, 2.4, 0), (4.0, 1.4, 4.0), "kamien", "matowy", rot=(0, 50, 0))
    p.walec("Misa", (0, 3.6, 0), (3.6, 1.0, 3.6), "zloto_c", "metal", segm=8)
    p.klin("Plomien", (0, 5.4, 0), (1.8, 3.0, 2.2), "zar", "swiecacy", rot=(0, 30, 0), faza=0.0)
    p.klin("Plomien 2", (0.2, 5.0, 0.3), (1.2, 2.2, 1.4), "zar_j", "swiecacy", rot=(0, 120, 0), faza=0.0)
    for a in (0, 120, 240):
        p.blok("Noga lunety", (4.4 + 0.8 * math.sin(math.radians(a)), 1.3, 0.8 * math.cos(math.radians(a))), (0.3, 2.8, 0.3),
               "pien_c", "matowy", rot=(10 * math.cos(math.radians(a)), 0, -10 * math.sin(math.radians(a))))
    p.walec("Luneta", (4.4, 2.9, 0.4), (0.6, 3.2, 0.6), "zloto", "metal", rot=(70, 0, 0), segm=8)
    p.walec("Szklo", (4.4, 3.45, 1.9), (0.5, 0.1, 0.5), "krysztal", "swiecacy", rot=(70, 0, 0), segm=8)
    p.blok("Proporzec", (-3.0, 5.2, 0), (0.3, 7.0, 0.3), "pien_c", "matowy")
    p.blok("Plat", (-2.0, 7.4, 0), (2.0, 1.6, 0.12), "tkanina", "matowy", faza=0.0)
    p.zaczep("SkrzyniaAttachment", "Podstawa", (0, 1.0, 3.6))
    return p


@rekwizyt("krysztaly_skupisko", "Skupisko świecących kryształów", "krysztal", 12)
def krysztaly_skupisko():
    p = _nowy("krysztaly_skupisko", "Skupisko kryształów", faza=0.3)
    p.blok("Skala", (0, 0.8, 0), (5.0, 1.6, 4.2), "kamien_c", "matowy", rot=(0, 20, 0))
    p.blok("Skala 2", (1.6, 0.5, 1.2), (2.4, 1.0, 2.2), "kamien", "matowy", rot=(0, -15, 4))
    for i, (x, z, h, rx, rz) in enumerate(((0, 0, 6.0, 0, 4), (-1.4, 0.6, 4.2, 10, -16), (1.3, -0.5, 3.6, -8, 18),
                                            (0.4, 1.4, 2.6, 18, 6), (-0.6, -1.3, 3.0, -16, -8))):
        p.klin("Krysztal", (x, 1.2 + h / 2, z), (0.9 + 0.12 * h, h, 1.2 + 0.1 * h), "magia" if i == 3 else "krysztal",
               "swiecacy", rot=(rx, 35 * i, rz), faza=0.03)
    p.walec("Blask", (0, 0.05, 0), (8.0, 0.1, 8.0), "krysztal", "poswiata", segm=8)
    return p


@rekwizyt("grota_wejscie", "Wejście do groty (ciemny otwór 9 × 8 w skale, kryształy)", "krysztal", 16)
def grota_wejscie():
    """Rama skał wokół ciemnego otworu 9 szerokości i 8 wysokości (brama „średnia”); przód (+Z) = na zewnątrz."""
    p = _nowy("grota_wejscie", "Wejście do groty", faza=0.4)
    p.blok("Otwor", (0, 4.0, -0.6), (9.4, 8.0, 1.2), "dziura", "matowy", faza=0.3)
    for zn in (1, -1):
        p.blok("Skala", (zn * 6.6, 5.0, 0), (4.2, 10.0, 4.4), "kamien", "matowy", rot=(0, zn * 8, -zn * 3))
        p.blok("Opaska", (zn * 6.6, 5.6, 0), (4.5, 0.8, 4.7), "kamien_c", "matowy", rot=(0, zn * 8, -zn * 3), faza=0.1)
        p.klin("Krysztal", (zn * 4.8, 1.6, 2.0), (0.9, 3.2, 1.3), "krysztal", "swiecacy", rot=(0, zn * 30, zn * 12), faza=0.02)
    p.blok("Nadproze", (0, 9.4, 0.2), (14.0, 3.0, 4.6), "kamien_j", "matowy", rot=(4, 0, 2))
    p.blok("Mech", (0.4, 11.0, 0.2), (9.0, 0.3, 3.6), "mech", "matowy", faza=0.08)
    p.blok("Lapka", (0, 8.0, 2.52), (1.2, 0.9, 0.12), "lapka_srednia", "swiecacy", faza=0.0)
    p.blok("Blask", (0, 0.08, 1.6), (7.0, 0.16, 3.0), "krysztal", "poswiata", faza=0.0)
    return p


# --------------------------------------------------------------------------- woda
@rekwizyt("wodospad", "Wodospad (spadek 14 studów)", "woda", 16)
def wodospad():
    """Strumień spada z krawędzi na wysokości 14 do tafli w y = 0; przód (+Z) = w stronę jeziorka.
    Środek układu = podstawa wodospadu na linii skały."""
    p = _nowy("wodospad", "Wodospad", faza=0.2)
    p.blok("Struga", (0, 7.2, 0.6), (8.0, 14.4, 1.0), "woda_j", "poswiata", faza=0.1)
    p.blok("Struga srodek", (0.4, 7.0, 1.2), (4.0, 14.0, 0.5), "piana", "poswiata", faza=0.0)
    p.blok("Krawedz", (0, 14.3, -0.6), (9.4, 0.6, 3.0), "woda", "polysk", faza=0.1)
    for zn in (1, -1):
        p.blok("Struga boczna", (zn * 5.2, 5.0, 0.8), (1.6, 10.0, 0.6), "woda_j", "poswiata", faza=0.0)
        p.blok("Glaz", (zn * 6.6, 1.2, 2.6), (3.2, 2.4, 3.0), "kamien", "matowy", rot=(0, zn * 20, zn * 6), faza=0.4)
    p.blok("Piana", (0, 0.4, 2.8), (10.0, 0.8, 4.0), "piana", "polysk", faza=0.3)
    p.blok("Piana 2", (0.8, 0.9, 2.4), (5.0, 0.8, 2.6), "piana", "polysk", rot=(0, 15, 0), faza=0.3)
    p.blok("Mgielka", (0, 2.6, 3.2), (11.0, 3.2, 1.4), "woda_j", "poswiata", faza=0.4)
    return p


@rekwizyt("most", "Kamienny most (pomost 22 × 8, wierzch na 1,6)", "woda", 16)
def most():
    """Most wzdłuż osi X (rzeka płynie wzdłuż Z); pomost od x = −11 do 11, wierzch na wysokości 1,6."""
    p = _nowy("most", "Kamienny most", faza=0.2)
    p.blok("Pomost", (0, 1.1, 0), (22.0, 1.0, 8.0), "kamien_j", "matowy")
    p.blok("Nawierzchnia", (0, 1.62, 0), (21.0, 0.1, 6.0), "drewno", "matowy", faza=0.0)
    for zn in (1, -1):
        p.blok("Balustrada", (0, 2.3, zn * 3.6), (20.0, 1.4, 0.8), "kamien", "matowy", faza=0.15)
        p.blok("Opaska", (0, 1.4, zn * 3.9), (22.2, 0.5, 0.4), "kamien_c", "matowy", faza=0.06)
        for x in (-10.0, 10.0):
            p.blok("Slupek", (x, 2.8, zn * 3.6), (1.4, 2.4, 1.4), "kamien_c", "matowy", faza=0.15)
            p.klin("Krysztal", (x, 4.4, zn * 3.6), (0.5, 1.0, 0.7), "krysztal", "swiecacy", rot=(0, 45, 0), faza=0.02)
    p.blok("Luk", (-5.0, 0.3, 0), (2.2, 0.6, 7.0), "kamien_c", "matowy", faza=0.1)
    p.blok("Luk 2", (5.0, 0.3, 0), (2.2, 0.6, 7.0), "kamien_c", "matowy", faza=0.1)
    return p


@rekwizyt("kamien_brodu", "Kamień brodu", "woda", 4)
def kamien_brodu():
    p = _nowy("kamien_brodu", "Kamień brodu", faza=0.3)
    p.blok("Kamien", (0, 0.35, 0), (3.2, 0.7, 2.8), "kamien_j", "matowy", rot=(0, 20, 0))
    p.blok("Mech", (0.3, 0.74, 0.2), (1.6, 0.1, 1.4), "mech", "matowy", rot=(0, 20, 0), faza=0.04)
    return p


# --------------------------------------------------------------------------- skały, łuki, ruiny
@rekwizyt("luk_skalny", "Naturalny łuk skalny (prześwit 22 × 18)", "skala", 16)
def luk_skalny():
    p = _nowy("luk_skalny", "Łuk skalny", faza=0.6)
    for zn in (1, -1):
        p.blok("Noga", (zn * 14.0, 6.0, 0), (6.0, 12.0, 7.0), "kanion", "matowy", rot=(0, zn * 6, -zn * 4))
        p.blok("Noga gora", (zn * 12.4, 15.6, 0), (5.4, 8.0, 6.4), "kanion_j", "matowy", rot=(0, zn * 6, -zn * 16))
        p.blok("Opaska", (zn * 13.8, 9.0, 0), (6.4, 1.2, 7.4), "kanion_c", "matowy", rot=(0, zn * 6, -zn * 4), faza=0.15)
    p.blok("Grzbiet", (0, 21.0, 0), (22.0, 4.4, 6.0), "kanion", "matowy", rot=(0, 0, 2))
    p.blok("Grzbiet 2", (3.0, 23.6, 0.4), (12.0, 2.2, 4.6), "kanion_j", "matowy", rot=(0, 8, -3))
    p.blok("Opaska grzbietu", (0, 20.0, 0), (22.4, 0.9, 6.3), "kanion_c", "matowy", rot=(0, 0, 2), faza=0.12)
    p.blok("Mech", (-2.0, 24.8, 0.2), (8.0, 0.3, 4.2), "mech", "matowy", rot=(0, 8, -3), faza=0.08)
    p.klin("Krysztal", (-6.0, 24.6, 1.0), (0.9, 3.0, 1.4), "krysztal", "swiecacy", rot=(0, 30, -10), faza=0.02)
    p.klin("Krysztal 2", (14.6, 20.4, 2.0), (0.7, 2.4, 1.1), "krysztal", "swiecacy", rot=(0, -20, 14), faza=0.02)
    return p


@rekwizyt("iglica_skalna", "Skalna iglica kanionu (ok. 18 wysokości)", "skala", 10)
def iglica_skalna():
    p = _nowy("iglica_skalna", "Iglica skalna", faza=0.5)
    p.blok("Podstawa", (0, 3.0, 0), (7.0, 6.0, 6.4), "kanion", "matowy", rot=(0, 15, 0))
    p.blok("Srodek", (0.4, 9.0, 0.2), (5.2, 6.4, 4.8), "kanion_j", "matowy", rot=(0, 35, 2))
    p.blok("Szczyt", (0.2, 14.6, 0), (3.4, 5.2, 3.2), "kanion", "matowy", rot=(0, 55, -3))
    for y, s in ((5.8, (7.3, 0.9, 6.7)), (12.2, (5.4, 0.8, 5.0))):
        p.blok("Opaska", (0.2, y, 0.1), s, "kanion_c", "matowy", rot=(0, 15 if y < 8 else 35, 0), faza=0.1)
    p.blok("Mech", (0.2, 17.3, 0), (2.8, 0.3, 2.6), "mech", "matowy", rot=(0, 55, -3), faza=0.06)
    p.klin("Krysztal", (2.4, 7.2, 1.6), (0.6, 2.0, 0.9), "krysztal", "swiecacy", rot=(0, 40, -20), faza=0.02)
    return p


@rekwizyt("ruiny_mur", "Mur ruin z oknem (ok. 9 × 7)", "ruiny", 10)
def ruiny_mur():
    p = _nowy("ruiny_mur", "Mur ruin", faza=0.15)
    p.blok("Mur dol", (0, 1.5, 0), (9.0, 3.0, 1.8), "kamien", "matowy")
    p.blok("Mur lewy", (-3.2, 4.6, 0), (2.6, 3.2, 1.8), "kamien_j", "matowy")
    p.blok("Mur prawy", (3.0, 5.2, 0), (3.0, 4.4, 1.8), "kamien", "matowy")
    p.klin("Ulom", (3.0, 7.9, 0), (3.0, 1.0, 1.8), "kamien", "matowy", rot=(0, 90, 0), faza=0.05)
    p.blok("Nadproze okna", (-0.2, 6.6, 0), (4.0, 0.8, 1.9), "kamien_c", "matowy", rot=(0, 0, -6))
    p.blok("Opaska", (0, 2.9, 0), (9.2, 0.5, 2.0), "kamien_c", "matowy", faza=0.06)
    p.blok("Runa", (-3.2, 4.6, 0.92), (0.8, 1.4, 0.1), "grzyb_sw", "swiecacy", faza=0.0)
    p.blok("Gruz", (1.0, 0.4, 1.8), (2.0, 0.8, 1.4), "kamien_j", "matowy", rot=(8, 30, 6))
    p.blok("Mech", (-2.0, 3.06, 0.2), (3.0, 0.14, 1.4), "mech", "matowy", faza=0.04)
    return p


# --------------------------------------------------------------------------- prąd wznoszący, lawa, latarnie
@rekwizyt("wiatr_kolumna", "Prąd wznoszący — znacznik (wiry, bez kolizji)", "wiatr", 10)
def wiatr_kolumna():
    """Świecący wir na ziemi i liście-pióra wznoszące się spiralą do ok. 14 studów; gra obraca całość.
    Bez kolizji. Skala = promień prądu / 4."""
    p = _nowy("wiatr_kolumna", "Prąd wznoszący", faza=0.0)
    p.walec("Wir", (0, 0.08, 0), (6.4, 0.16, 6.4), "wiatr", "poswiata", segm=8)
    p.walec("Wir 2", (0, 0.14, 0), (4.6, 0.16, 4.6), "wiatr_j", "swiecacy", segm=8)
    for i in range(5):
        a = math.radians(i * 137.0)
        y = 2.0 + 2.6 * i
        r_ = 3.0 - 0.25 * i
        p.klin("Pioro", (r_ * math.sin(a), y, r_ * math.cos(a)), (0.3, 0.9, 1.8), "wiatr_j", "swiecacy",
               rot=(30, math.degrees(a) + 90, 0), faza=0.0)
    p.walec("Pierscien", (0, 6.0, 0), (6.4, 0.16, 6.4), "wiatr", "poswiata", rot=(6, 0, 4), segm=8)
    return p


@rekwizyt("szczelina_lawy", "Szczelina lawy w ziemi (płonąca ziemia)", "lawa", 8)
def szczelina_lawy():
    p = _nowy("szczelina_lawy", "Szczelina lawy", faza=0.2)
    p.blok("Plyta", (0, 0.2, 0), (7.0, 0.4, 4.6), "bazalt_c", "matowy", rot=(0, 10, 0))
    p.blok("Szczelina", (0, 0.32, 0), (5.6, 0.2, 0.9), "zar", "swiecacy", rot=(0, 24, 0), faza=0.0)
    p.blok("Szczelina 2", (1.4, 0.34, 0.8), (2.4, 0.2, 0.6), "zar_j", "swiecacy", rot=(0, -30, 0), faza=0.0)
    p.blok("Krawedz", (-2.2, 0.6, -1.0), (2.0, 0.8, 1.8), "bazalt", "matowy", rot=(0, 30, 6))
    p.blok("Krawedz 2", (2.6, 0.5, 1.2), (1.6, 0.6, 1.4), "bazalt", "matowy", rot=(0, -20, -6))
    return p


def _latarnia(id, kolor):
    p = _nowy(id, "Latarnia runiczna", faza=0.12)
    p.blok("Slup", (0, 1.4, 0), (1.0, 2.8, 1.0), "kamien", "matowy", rot=(0, 45, 0))
    p.blok("Opaska", (0, 1.0, 0), (1.2, 0.4, 1.2), "kamien_c", "matowy", rot=(0, 45, 0), faza=0.04)
    p.klin("Krysztal", (0, 3.4, 0), (0.8, 1.6, 0.8), kolor, "swiecacy", rot=(0, 45, 0), faza=0.0)
    p.walec("Blask", (0, 0.04, 0), (2.6, 0.08, 2.6), kolor, "poswiata", segm=8)
    return p


for _id, _k, _opis in (("latarnia_las", "krysztal", "las"), ("latarnia_zar", "zar", "kanion i kaldera"),
                       ("latarnia_magia", "magia", "zapieczętowana brama"), ("latarnia_zlota", "zloto_j", "jezioro i wodospad")):
    rekwizyt(_id, "Latarnia runiczna (%s)" % _opis, "sciezka", 6)(lambda _id=_id, _k=_k: _latarnia(_id, _k))


# --------------------------------------------------------------------------- olbrzymia czaszka z otwartą paszczą
@rekwizyt("czaszka_wielka", "Olbrzymia czaszka z otwartą paszczą (grota dla małych)", "znak", 60)
def czaszka_wielka():
    """Czaszka leży na ziemi z otwartą paszczą: między żuchwą (na ziemi) a podniebieniem jest prześwit
    7 × 5 — wejście do wnętrza czaszki (brama „mała”). Przód (+Z) = paszcza. Ok. 22 × 18 × 36."""
    p = _nowy("czaszka_wielka", "Olbrzymia czaszka", faza=0.6)
    # żuchwa na ziemi (dwie gałęzie) i zęby dolne
    for zn in (1, -1):
        p.blok("Zuchwa", (zn * 5.6, 1.0, 8.0), (2.8, 2.0, 18.0), "kosc_c", "matowy", rot=(0, zn * 10, 0), faza=0.3)
        for j in range(3):
            p.klin("Zab dolny", (zn * (4.4 - 0.4 * j), 2.6, 13.6 - 3.2 * j), (0.9, 1.6, 1.2), "bialy", "polysk", faza=0.04)
    # mózgoczaszka i podniebienie uniesione nad paszczą
    p.blok("Czaszka", (0, 9.4, -5.0), (17.0, 12.0, 15.0), "kosc", "matowy", rot=(-6, 0, 0))
    p.blok("Podniebienie", (0, 7.6, 7.4), (12.0, 3.0, 14.0), "kosc", "matowy", rot=(8, 0, 0))
    p.klin("Grzbiet nosa", (0, 9.8, 7.0), (7.0, 2.4, 12.0), "kosc_c", "matowy", rot=(8, 180, 0), faza=0.2)
    p.blok("Wnetrze", (0, 2.8, 2.0), (8.0, 5.6, 14.0), "dziura", "matowy", faza=0.0)   # ciemny środek paszczy
    p.blok("Pekniecie", (2.4, 15.5, -4.0), (0.6, 0.4, 9.0), "mrok", "matowy", rot=(-6, 14, 0), faza=0.0)
    for zn in (1, -1):
        for j in range(4):
            p.klin("Zab", (zn * (4.8 - 0.3 * j), 5.2, 13.0 - 2.8 * j), (0.9, 2.2, 1.3), "bialy", "polysk", rot=(180, 0, 0), faza=0.04)
        p.blok("Oczodol", (zn * 6.2, 10.2, 2.6), (4.0, 4.0, 3.4), "mrok", "matowy", rot=(-6, zn * 14, 0), faza=0.3)
        p.blok("Zar oczodolu", (zn * 5.8, 10.0, 2.4), (1.6, 1.6, 1.4), "magia", "swiecacy", faza=0.0)
        p.blok("Brew", (zn * 6.6, 13.2, 3.0), (6.0, 1.6, 5.0), "kosc_c", "matowy", rot=(-6, zn * 14, -zn * 12), faza=0.3)
        p.blok("Rog nasada", (zn * 6.8, 15.4, -8.0), (3.4, 3.4, 6.0), "kosc_c", "matowy", rot=(-38, zn * 14, 0), faza=0.3)
        p.klin("Rog", (zn * 8.2, 19.6, -14.0), (2.6, 3.2, 10.0), "kosc", "matowy", rot=(-38, zn * 14, 0), faza=0.1)
        p.klin("Rog policzka", (zn * 9.8, 6.0, -4.0), (1.8, 2.4, 7.0), "kosc", "matowy", rot=(-6, zn * 40, zn * 90), faza=0.1)
        p.blok("Mech", (zn * 4.0, 15.6 - 0.6 * zn, -5.0 - zn), (5.0, 0.4, 4.6), "mech", "matowy", rot=(-6, 0, 0), faza=0.1)
        p.blok("Nozdrze", (zn * 2.0, 10.4, 13.6), (1.4, 0.8, 1.8), "mrok", "matowy", rot=(8, 0, 0), faza=0.1)
    for j, (z, s_) in enumerate(((-15.0, 6.6), (-21.0, 5.4), (-26.4, 4.2))):            # kręgi szyi
        p.blok("Krag", (0.8 * j, s_ * 0.45, z), (s_ * 1.2, s_ * 0.9, 4.6), "kosc_c" if j % 2 else "kosc", "matowy",
               rot=(0, 8 * j, 5 * j))
    p.blok("Lapka", (0, 6.0, 14.6), (1.2, 0.9, 0.12), "lapka_mala", "swiecacy", faza=0.0)
    return p


def zbuduj(id):
    return next(fn for i, _, _, _, fn in ZESTAW2 if i == id)()


def wszystkie():
    """[(Postac, strefa, limit części), …] w kolejności spisu."""
    return [(fn(), strefa, limit) for _, _, strefa, limit, fn in ZESTAW2]
