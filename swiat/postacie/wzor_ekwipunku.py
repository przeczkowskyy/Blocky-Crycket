# -*- coding: utf-8 -*-
"""WZÓR EKWIPUNKU — hełm i miecz jako sztywne akcesoria. podglad_postaci.py zakłada je na szarego manekina R15
(model „przymiarka”) i robi ikony 512 px każdego przedmiotu.

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/wzor_ekwipunku.py --wyj <folder> --klip atak

Konwencje akcesoriów (pełna ściąga: biblioteka/README.md):
- model w układzie PUNKTU ZACZEPIENIA: (0, 0, 0) = zaczep, Y w górę, Z do przodu;
- HatAttachment = środek górnej ściany głowy; głowa manekina to sześcian 1,25 studa, więc jej środek leży
  w (0, −0,625, 0), a przednia ściana na z = +0,625;
- broń na RightGripAttachment (środek dłoni): rękojeść w (0, 0, 0), ostrze w +Y, płaz do przodu (+Z);
  gdy ręka zwisa, ostrze celuje do przodu, a w pozie „trzymanie” manekina sterczy w górę;
- jedno akcesorium = jedna siatka (wymóg Roblox), ≤ 4000 trójkątów, mieści się w pudełku swojego typu.
"""
from swiat.postacie.biblioteka.postac import Akcesorium

GLOWA = 1.25                     # głowa manekina R15 (do dopasowania hełmu)


def helm():
    a = Akcesorium("wzor_helm", "Wzorcowy hełm", zaczep="HatAttachment", typ="Hat")
    yg = -GLOWA / 2                                           # środek głowy względem zaczepu
    zp = GLOWA / 2                                            # przednia ściana głowy
    a.blok("Kopula", (0, -0.03, 0), (1.5, 0.46, 1.5), "stal", "metal")
    a.ostroslup("Czubek", (0, 0.35, 0), (1.5, 0.3, 1.5), "stal", "metal", gora=(0.9, 0.9))
    a.blok("Rant", (0, -0.27, 0), (1.6, 0.2, 1.6), "zloto", "metal")
    a.blok("Tyl", (0, yg - 0.12, -0.68), (1.5, 1.05, 0.16), "stal", "metal")
    for zn in (1, -1):
        a.blok("Bok", (zn * 0.68, yg - 0.12, -0.04), (0.16, 1.05, 1.42), "stal", "metal")
        a.blok("Policzek", (zn * 0.56, yg - 0.32, zp + 0.06), (0.38, 0.6, 0.14), "stal", "metal")
        a.blok("Nit", (zn * 0.77, yg + 0.12, 0.3), (0.06, 0.14, 0.14), "zloto", "metal", faza=0.02)
    a.blok("Nosal", (0, yg + 0.02, zp + 0.08), (0.18, 0.56, 0.12), "stal_cien", "metal")
    a.blok("Grzebien", (0, 0.62, -0.05), (0.2, 0.34, 1.15), "niebieski", "matowy")
    a.klin("Grzebien tyl", (0, 0.5, -0.78), (0.2, 0.5, 0.36), "niebieski", "matowy")   # skos opada do tyłu
    return a


def miecz():
    a = Akcesorium("wzor_miecz", "Wzorcowy miecz", zaczep="RightGripAttachment", typ="Bron",
                   ikona_obrot=(0, 0, -45))                    # ikona po skosie
    a.walec("Rekojesc", (0, 0, 0), (0.26, 1.1, 0.26), "brazowy_ciemny", "matowy", segm=8)
    a.blok("Glowica", (0, -0.7, 0), (0.44, 0.32, 0.44), "zloto", "metal")
    a.blok("Jelec", (0, 0.68, 0), (1.3, 0.26, 0.34), "zloto", "metal")
    for zn in (1, -1):
        a.blok("Jelec koniec", (zn * 0.66, 0.74, 0), (0.22, 0.42, 0.38), "zloto", "metal")
    a.blok("Klejnot", (0, 0.68, 0.19), (0.2, 0.18, 0.08), "niebieski_jasny", "swiecacy", faza=0.02)
    a.blok("Klinga", (0, 2.11, 0), (0.5, 2.6, 0.16), "stal", "metal")
    a.blok("Zbrocze", (0, 1.95, 0), (0.12, 2.1, 0.2), "stal_cien", "metal", faza=0.02)
    a.ostroslup("Sztych", (0, 3.685, 0), (0.5, 0.55, 0.16), "stal", "metal", gora=(0.0, 0.16))
    return a


def zbuduj():
    return [helm(), miecz()]
