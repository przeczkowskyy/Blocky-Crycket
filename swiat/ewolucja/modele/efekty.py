# -*- coding: utf-8 -*-
"""Efekty jako rigi z części: stożek ognia (bryła języków ognia z jasnym rdzeniem, klip migotania) i przypalenie ziemi.

    from swiat.ewolucja.modele import efekty
    efekty.ogien_stozek()      # Postac: stawy Podstawa > Rdzen, Pierscien1, Pierscien2, Pierscien3; klip „migotanie”
    efekty.przypalenie()       # statyczny krąg sadzy z żarem (INFERNO), promień 10

Stożek: punkt obrotu w pysku (początek układu), długość 10 studów wzdłuż przodu (−Z rigu), największa średnica ok. 4,6.
Gra skaluje model do zasięgu zionięcia (skala = zasięg / 10) i przypina do PyskAttachment.
"""
import math

from swiat.ewolucja.modele import swiat_zestaw as sz
from swiat.ewolucja.modele.smok_klipy import petla
from swiat.ewolucja.modele.smok_model import Smok

DLUGOSC_STOZKA = 10.0
PROMIEN_PRZYPALENIA = 10.0


def ogien_stozek():
    p = Smok("ogien_stozek", "Stożek ognia", typ="stwor", skala=1.0, faza=0.0, paleta={})
    p.kosc("Podstawa", "Root", (0, 0, 0), czesc=(1, 1, 1))
    p.kosc("Rdzen", "Podstawa", (0, 0, 0.2), czesc=(1, 1, 4), srodek=(0, 0, 2))
    # Wachlarz ok. 60° (jak stożek zionięcia w grze): trzy rzędy języków coraz dalej od pyska; rzędy 2 i 3 mają też
    # warstwę uniesioną ku górze, żeby ogień był bryłą, a nie wstążką. (odległość, szer., wys., dł., kąty, kolory)
    rzedy = ((1.2, 0.8, 0.7, 3.2, (-14, 0, 14), ("FFE680", "FFD050")), (3.6, 1.3, 1.0, 3.8, (-24, -12, 0, 12, 24), ("FFA62E", "FF8A2A")),
             (6.2, 1.8, 1.3, 4.0, (-30, -20, -10, 0, 10, 20, 30), ("FF6A1A", "E8381A")))
    for i, rzad in enumerate(rzedy):
        p.kosc("Pierscien%d" % (i + 1), "Podstawa", (0, 0, rzad[0]), czesc=(1, 1, 3), srodek=(0, 0, 1.5))
    with p.na("Rdzen"):                                         # jasny rdzeń: trzy spłaszczone bryły od białej do żółtej
        for z, sx, sy, dl, kol in ((1.6, 1.2, 0.8, 3.4, "FFFDF0"), (4.4, 2.6, 1.1, 3.8, "FFF2B0"), (7.2, 4.2, 1.3, 3.6, "FFE070")):
            p.kula("Rdzen", (0, 0, z - 0.2), (sx, sy, dl), kol, "swiecacy", segm=12)
    for i, (z, w, h, dl, katy, kolory) in enumerate(rzedy):
        with p.na("Pierscien%d" % (i + 1), pos=(0, 0, -z)):     # układ w pysku: języki rozchodzą się promieniście
            for j, a in enumerate(katy):
                with p.uklad(obrot=(0, a, 0)):
                    # klin położony na boku: z góry (kamera gry) widać trójkąt zwężający się od pyska
                    p.klin("Jezyk ognia", (0, 0, z + dl / 2), (h, w * 1.3, dl), kolory[j % 2], "swiecacy",
                           rot=(0, 180, 90 if j % 2 else -90), faza=0.0)
            if i > 0:                                           # warstwa górna
                for j, a in enumerate(katy[1:-1:2] if i == 1 else katy[::2]):
                    with p.uklad(obrot=(-16, a + 5, 0)):
                        p.klin("Jezyk gorny", (0, 0, z + dl / 2), (h * 0.8, w * 1.1, dl * 0.9), kolory[(j + 1) % 2], "swiecacy",
                               rot=(0, 180, -90 if j % 2 else 90), faza=0.0)
            if i == 2:
                for j, a in enumerate((-26, -8, 9, 27)):        # iskry na końcu
                    p.blok("Iskra", (10.4 * math.sin(math.radians(a)), 0.6 + 0.3 * (j % 2), 10.4 * math.cos(math.radians(a))),
                           (0.34, 0.34, 0.34), "FFE680", "swiecacy", rot=(45, 0, 45), faza=0.0)
    p.zaczep("KoniecAttachment", "Podstawa", (0, 0, DLUGOSC_STOZKA))
    petla(p, "migotanie", 12, {}, [
        ("Pierscien1", "obrot", (4, 4, 20), 1, 0.0), ("Pierscien2", "obrot", (5, -4, -24), 1, 0.3),
        ("Pierscien3", "obrot", (-5, 5, 28), 1, 0.6), ("Rdzen", "przes", (0, 0, 0.25), 2, 0.0),
        ("Pierscien3", "przes", (0, 0, 0.3), 1, 0.2)])
    return p


def przypalenie():
    """Przypalona ziemia pod INFERNO: krąg sadzy, żar pośrodku, świecące pęknięcia. Promień 10 — gra skaluje do zasięgu."""
    p = sz._nowy("przypalenie", "Przypalenie ziemi", faza=0.0)
    R = PROMIEN_PRZYPALENIA
    p.walec("Sadza", (0, 0.05, 0), (2 * R, 0.1, 2 * R), "1E1822", "matowy", segm=8)
    p.walec("Sadza srodek", (0, 0.07, 0), (1.2 * R, 0.14, 1.2 * R), "120E16", "matowy", segm=8)
    p.walec("Zar", (0, 0.09, 0), (0.6 * R, 0.18, 0.6 * R), "FF7A2A", "swiecacy", segm=8)
    p.walec("Zar rdzen", (0, 0.11, 0), (0.26 * R, 0.22, 0.26 * R), "FFD98A", "swiecacy", segm=8)
    for i in range(8):                                          # pęknięcia rozchodzące się od środka
        a = 45 * i + 12 * (i % 3)
        dl = R * (0.42 + 0.14 * (i % 3))
        r_ = R * 0.28 + dl / 2
        p.blok("Pekniecie", (r_ * math.sin(math.radians(a)), 0.1, r_ * math.cos(math.radians(a))), (0.45, 0.16, dl),
               "FF7A2A" if i % 2 else "FFB52E", "swiecacy", rot=(0, a, 0), faza=0.0)
    return p
