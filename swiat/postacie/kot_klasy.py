# -*- coding: utf-8 -*-
"""KOCI RYCERZ i KOCI ZWIADOWCA — stroje klas Rycerza i Zwiadowcy przerobione na kota (Paweł 24.11, D-145:
„ubrania z rycerza przerzucamy, żeby pasowały na kotka, no i tak samo łucznika”). Status: propozycja.

Zasada jak w kot_demon.py: TEN SAM model co Kot-Mag (swiat/postacie/kot_mag.py — wymiary, kości, klipy), rudy kot
rasy Człowiek. Plików Karola (kot_mag.py, rycerz.py, zwiadowca.py) nie zmieniamy: wczytujemy WŁASNĄ kopię kot_mag
z dopisanymi kolorami, a stroje budujemy od nowa na kościach kota według projektu Karola (te same elementy i kolory,
wymiary policzone z klocków kota — przedmioty Karola mają liczby ludzika, więc wprost nie pasują):
  rycerz()     stalowy hełm z otwartą twarzą (uszy przebijają kopułę jak rondo kapelusza Kota-Maga), napierśnik
               z obojczykiem i niebieskim tabardem ze złotą lamówką i godłem, naramienniki, karwasze, stalowe
               rękawice, brązowy pas z klamrą, poły tabardu, nagolenniki i trzewiki;
  zwiadowca()  zielony kaptur z ogonkiem (uszy na wierzchu) i krótka peleryna, pomarańczowa chusta, skórzany kirys
               na zielonej tunice, pas z sakwą, kołczan na plecach z pasem na skos, karwasze, rękawice, zielone
               spodnie, buty z wywiniętą cholewą.
Broń: domyślnie bez — w selektorze klas kot dostaje w łapkę kocią broń startową klasy (ClassSelectClient.holdWeapon,
WyborKlasyModele.Weapon_<klasa>_Kot), jak w wyborze rasy. bron=True dokłada miecz / łuk Karola przez kocia()
(do podglądu; chwyt nie jest jeszcze dopasowany).
Klipy: te same co Kota-Maga (stroje nie zmieniają ruchu).

    python -B swiat/postacie/kot_klasy.py --kontrola       # sprawdzian biblioteki (bez Blendera)
"""
import importlib.util
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(TU)))

KOLORY = {
    # rycerz (paleta rycerz.py + złoto)
    "stal": "A8B4C8", "stal_cien": "75839C", "stal_ciemna": "4D576D", "niebieski": "2C6BE0",
    "niebieski_ciemny": "1B3F8F", "zloto": "E8B93A", "brazowy": "6B4325", "brazowy_ciemny": "472B16",
    # zwiadowca (paleta zwiadowca.py)
    "lisc": "3F9B4A", "lisc_ciemny": "26633A", "skorzany": "8A5530", "skorzany_ciemny": "553319",
    "skorzany_jasny": "C49A62", "akcent": "FF9F1C", "drewno_luku": "A8692E",
}


def _kot_mag():
    """Świeża, prywatna kopia modułu kot_mag z dopisanymi kolorami strojów (paleta Kota-Maga bez zmian)."""
    spec = importlib.util.spec_from_file_location("kot_mag_dla_klas", os.path.join(TU, "kot_mag.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.PALETA.update(KOLORY)
    return m


KM = _kot_mag()
PALETA = KM.PALETA


def _bron(akc, korekta):
    """Broń klasy Karola w proporcjach kota (bronie_startowe.kocia), z paletą kota (kolory dopisane wyżej)."""
    from swiat.postacie import bronie_startowe as B
    a = B.kocia(akc)
    a.paleta = PALETA
    return a, korekta


# ------------------------------------------------------------------------------------------------ rycerz
def _rycerz_stroj(p):
    w, h, d = p.wymiary("Head")
    hw, hd, hh = w + 0.28, d + 0.28, h - 0.1
    with p.na("Head", od="srodek"):
        z = d / 2
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Helm bok " + s, (zn * (w / 2 + 0.07), 0.05, 0), (0.14, hh, hd), "stal", "metal")
            p.blok("Policzek " + s, (zn * (w / 2 - 0.02), -0.12, z + 0.06), (0.16, 0.74, 0.14), "stal", "metal")
            p.blok("Nit " + s, (zn * (w / 2 - 0.02), 0.16, z + 0.14), (0.07, 0.07, 0.04), "stal_ciemna", "metal",
                   faza=0.0)
            p.blok("Obrecz bok " + s, (zn * (w / 2 + 0.16), h / 2 - 0.14, 0), (0.05, 0.16, hd + 0.04),
                   "stal_cien", "metal", faza=0.0)
        p.blok("Helm tyl", (0, 0.05, -z - 0.07), (hw, hh, 0.14), "stal", "metal")
        p.blok("Obrecz tyl", (0, h / 2 - 0.14, -z - 0.16), (hw + 0.04, 0.16, 0.05), "stal_cien", "metal", faza=0.0)
        p.blok("Helm kopula", (0, h / 2 + 0.08, 0), (hw, 0.24, hd), "stal", "metal", faza=0.1)
        p.blok("Helm czubek", (0, h / 2 + 0.24, 0), (w - 0.5, 0.12, d - 0.3), "stal", "metal", faza=0.05)
        p.blok("Grzebien", (0, h / 2 + 0.3, -0.02), (0.18, 0.12, d), "stal_cien", "metal", faza=0.04)
        p.blok("Czolo", (0, h / 2 - 0.12, z + 0.07), (hw, 0.22, 0.14), "stal", "metal")
        p.blok("Czolo obrecz", (0, h / 2 - 0.14, z + 0.16), (hw + 0.04, 0.16, 0.05), "stal_cien", "metal", faza=0.0)

    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.blok("Napiersnik", (0, 0, 0), (w + 0.12, h + 0.04, d + 0.12), "stal", "metal")
        p.blok("Obojczyk", (0, h / 2 - 0.02, 0), (w - 0.05, 0.18, d + 0.02), "stal_cien", "metal")
        for zk, s in ((1, ""), (-1, " tyl")):
            p.blok("Tabard" + s, (0, -0.04, zk * (z + 0.08)), (w - 0.26, h - 0.12, 0.05), "niebieski", "matowy",
                   faza=0.0)
            for zn in (1, -1):
                p.blok("Lamowka" + s, (zn * (w / 2 - 0.13), -0.04, zk * (z + 0.09)), (0.07, h - 0.12, 0.05),
                       "zloto", "metal", faza=0.0)
        p.blok("Godlo", (0, 0.0, z + 0.12), (0.26, 0.26, 0.04), "zloto", "metal", rot=(0, 0, 45), faza=0.0)
        p.blok("Godlo srodek", (0, 0.0, z + 0.145), (0.12, 0.12, 0.03), "niebieski_ciemny", "polysk",
               rot=(0, 0, 45), faza=0.0)
    for strona, zn in (("Left", 1), ("Right", -1)):
        with p.na(strona + "UpperArm", od="srodek"):
            w, h, d = p.wymiary(strona + "UpperArm")
            p.blok("Naramiennik " + strona, (zn * 0.05, h / 2 - 0.02, 0), (w + 0.26, 0.18, d + 0.26), "stal",
                   "metal", faza=0.06)
            p.blok("Naramiennik lama " + strona, (zn * 0.07, h / 2 - 0.15, 0), (w + 0.2, 0.12, d + 0.2),
                   "stal_cien", "metal", faza=0.04)
            p.blok("Ramie " + strona, (0, -0.05, 0), (w + 0.06, h * 0.6, d + 0.06), "stal_ciemna", "metal")
        with p.na(strona + "LowerArm", od="srodek"):
            w, h, d = p.wymiary(strona + "LowerArm")
            p.blok("Karwasz " + strona, (0, 0, 0), (w + 0.08, h + 0.02, d + 0.08), "stal", "metal")
            p.blok("Nalokcica " + strona, (0, h / 2 - 0.02, -0.05), (w + 0.12, 0.1, d + 0.06), "stal_cien",
                   "metal", faza=0.03)
        with p.na(strona + "Hand", od="srodek"):
            w, h, d = p.wymiary(strona + "Hand")
            p.blok("Rekawica " + strona, (0, 0, 0), (w + 0.06, h + 0.04, d + 0.06), "stal_ciemna", "metal")
            p.blok("Mankiet " + strona, (0, h / 2 + 0.02, 0), (w + 0.12, 0.08, d + 0.12), "stal", "metal",
                   faza=0.02)
    with p.na("LowerTorso", od="srodek"):
        w, h, d = p.wymiary("LowerTorso")
        z = d / 2
        p.blok("Pas", (0, 0, 0), (w + 0.14, h + 0.04, d + 0.14), "brazowy", "matowy")
        p.blok("Klamra", (0, 0, z + 0.09), (0.26, 0.22, 0.05), "stal", "metal", faza=0.02)
        p.blok("Klamra srodek", (0, 0, z + 0.115), (0.12, 0.1, 0.03), "brazowy_ciemny", faza=0.0)
        for zk, s, kat in ((1, "", -12), (-1, " tyl", 12)):
            with p.uklad(pos=(0, -h / 2, zk * (z + 0.08)), obrot=(kat, 0, 0)):
                p.blok("Pola" + s, (0, -0.2, 0), (w - 0.4, 0.4, 0.05), "niebieski", "matowy", faza=0.0)
                for zn in (1, -1):
                    p.blok("Pola lamowka" + s, (zn * (w / 2 - 0.2), -0.2, 0), (0.07, 0.4, 0.07), "zloto", "metal",
                           faza=0.0)
                p.blok("Pola rabek" + s, (0, -0.39, 0), (w - 0.33, 0.06, 0.07), "zloto", "metal", faza=0.0)
    for strona in ("Left", "Right"):
        with p.na(strona + "UpperLeg", od="srodek"):
            w, h, d = p.wymiary(strona + "UpperLeg")
            p.blok("Nogawica " + strona, (0, 0, 0), (w + 0.06, h + 0.02, d + 0.06), "stal_ciemna", "metal")
        with p.na(strona + "LowerLeg", od="srodek"):
            w, h, d = p.wymiary(strona + "LowerLeg")
            p.blok("Nagolennik " + strona, (0, 0, 0), (w + 0.08, h + 0.02, d + 0.08), "stal", "metal")
            p.blok("Nakolannik " + strona, (0, h / 2 - 0.02, d / 2 + 0.06), (w - 0.05, 0.14, 0.1), "stal_cien",
                   "metal", faza=0.03)
        with p.na(strona + "Foot", od="srodek"):
            w, h, d = p.wymiary(strona + "Foot")
            p.blok("Trzewik " + strona, (0, 0.01, 0), (w + 0.06, h + 0.04, d + 0.06), "stal_ciemna", "metal")
            p.blok("Podeszwa " + strona, (0, -h / 2 + 0.02, 0), (w + 0.08, 0.05, d + 0.08), "brazowy_ciemny",
                   "matowy", faza=0.0)
    return p


def rycerz(bron=False):
    """Koci Rycerz: rudy Kot-Mag (rasa Człowiek) w zbroi Rycerza (bron=True: miecz Rycerza w prawej łapce)."""
    from swiat.postacie import rycerz as R
    p = KM.cialo()
    p.id, p.nazwa = "kot_rycerz", "Koci Rycerz"
    _rycerz_stroj(p)
    if not bron:
        return p
    a, (zaczep, pos, obr) = _bron(R.miecz(), KM.KOREKTY_CHWYTU["RightGripAttachment"])
    p.zaloz(a, zaczep="RightGripAttachment", pos=pos, obrot=obr)
    return p


# --------------------------------------------------------------------------------------------- zwiadowca
def _zwiadowca_stroj(p):
    w, h, d = p.wymiary("Head")
    hw, hd = w + 0.28, d + 0.28
    with p.na("Head", od="srodek"):
        z = d / 2
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Kaptur bok " + s, (zn * (w / 2 + 0.07), 0.02, -0.04), (0.14, h + 0.1, hd - 0.08), "lisc",
                   "matowy")
            p.blok("Kaptur brzeg " + s, (zn * (w / 2 + 0.02), -0.05, z + 0.06), (0.14, h - 0.1, 0.12),
                   "lisc_ciemny", "matowy")
        p.blok("Kaptur tyl", (0, 0.02, -z - 0.07), (hw, h + 0.1, 0.14), "lisc", "matowy")
        p.blok("Kaptur wierzch", (0, h / 2 + 0.1, -0.02), (hw, 0.2, hd - 0.04), "lisc", "matowy", faza=0.08)
        p.blok("Kaptur brzeg gora", (0, h / 2 - 0.04, z + 0.06), (hw - 0.04, 0.16, 0.12), "lisc_ciemny", "matowy")
        p.blok("Kaptur ogonek", (0, 0.3, -z - 0.26), (0.46, 0.46, 0.3), "lisc", "matowy", rot=(35, 0, 0), faza=0.05)
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.blok("Kirys", (0, 0, 0), (w + 0.12, h + 0.04, d + 0.12), "skorzany", "matowy")
        p.blok("Kirys szwy", (0, -0.02, z + 0.065), (0.06, h - 0.1, 0.02), "skorzany_ciemny", faza=0.0)
        p.blok("Chusta", (0, h / 2 - 0.02, 0), (w - 0.05, 0.18, d + 0.04), "akcent", "matowy")
        p.blok("Chusta wezel", (0.22, h / 2 - 0.18, z + 0.08), (0.16, 0.2, 0.06), "akcent", "matowy",
               rot=(0, 0, 15), faza=0.02)
        p.blok("Peleryna", (0, -0.05, -z - 0.1), (w + 0.1, h + 0.3, 0.06), "lisc", "matowy", rot=(-6, 0, 0),
               faza=0.0)
        # kołczan na plecach (na skos) i pas kołczanu przez pierś
        p.blok("Pas kolczanu", (0, 0, z + 0.075), (0.12, h + 0.35, 0.03), "skorzany_ciemny", "matowy",
               rot=(0, 0, 38), faza=0.0)
        with p.uklad(pos=(-0.22, 0.1, -z - 0.3), obrot=(0, 0, -22)):
            p.blok("Kolczan", (0, 0, 0), (0.3, 1.0, 0.3), "skorzany", "matowy", faza=0.03)
            p.blok("Kolczan obrecz", (0, 0.42, 0), (0.34, 0.08, 0.34), "skorzany_jasny", "matowy", faza=0.0)
            for i, dx in enumerate((-0.07, 0.0, 0.07)):
                p.blok("Strzala %d" % i, (dx, 0.55, 0.02 * i), (0.04, 0.3, 0.04), "drewno_luku", faza=0.0)
                p.blok("Lotka %d" % i, (dx, 0.66, 0.02 * i), (0.09, 0.12, 0.02), "akcent", faza=0.0)
    for strona, zn in (("Left", 1), ("Right", -1)):
        with p.na(strona + "UpperArm", od="srodek"):
            w, h, d = p.wymiary(strona + "UpperArm")
            p.blok("Rekaw " + strona, (0, 0.02, 0), (w + 0.08, h * 0.8, d + 0.08), "lisc", "matowy")
            p.blok("Naramiennik " + strona, (zn * 0.04, h / 2 - 0.02, 0), (w + 0.16, 0.1, d + 0.16), "skorzany",
                   "matowy", faza=0.03)
        with p.na(strona + "LowerArm", od="srodek"):
            w, h, d = p.wymiary(strona + "LowerArm")
            p.blok("Karwasz " + strona, (0, -0.02, 0), (w + 0.08, h * 0.8, d + 0.08), "skorzany", "matowy")
            p.blok("Karwasz rzemyk " + strona, (0, 0.02, 0), (w + 0.1, 0.05, d + 0.1), "skorzany_ciemny",
                   faza=0.0)
        with p.na(strona + "Hand", od="srodek"):
            w, h, d = p.wymiary(strona + "Hand")
            p.blok("Rekawica " + strona, (0, 0.03, 0), (w + 0.05, h * 0.7, d + 0.05), "skorzany_ciemny", "matowy")
    with p.na("LowerTorso", od="srodek"):
        w, h, d = p.wymiary("LowerTorso")
        z = d / 2
        p.blok("Pas", (0, 0.02, 0), (w + 0.16, 0.14, d + 0.16), "skorzany_ciemny", "matowy")
        p.blok("Klamra", (0, 0.02, z + 0.1), (0.16, 0.14, 0.04), "stal", "metal", faza=0.01)
        p.blok("Sakwa", (0.42, -0.08, z + 0.1), (0.26, 0.26, 0.12), "skorzany_jasny", "matowy", faza=0.03)
        p.blok("Tunika", (0, -0.12, 0), (w + 0.12, h + 0.06, d + 0.12), "lisc", "matowy")
        for zk, s in ((1, ""), (-1, " tyl")):
            p.blok("Pola tuniki" + s, (0, -0.32, zk * (z + 0.07)), (w - 0.3, 0.34, 0.05), "lisc", "matowy",
                   rot=(-zk * 10, 0, 0), faza=0.0)
    for strona in ("Left", "Right"):
        with p.na(strona + "UpperLeg", od="srodek"):
            w, h, d = p.wymiary(strona + "UpperLeg")
            p.blok("Spodnie " + strona, (0, 0, 0), (w + 0.06, h + 0.02, d + 0.06), "lisc_ciemny", "matowy")
        with p.na(strona + "LowerLeg", od="srodek"):
            w, h, d = p.wymiary(strona + "LowerLeg")
            p.blok("Cholewa " + strona, (0, 0, 0), (w + 0.08, h + 0.02, d + 0.08), "skorzany", "matowy")
            p.blok("Wywiniecie " + strona, (0, h / 2, 0), (w + 0.14, 0.08, d + 0.14), "skorzany_jasny", "matowy",
                   faza=0.02)
        with p.na(strona + "Foot", od="srodek"):
            w, h, d = p.wymiary(strona + "Foot")
            p.blok("But " + strona, (0, 0.01, 0), (w + 0.06, h + 0.04, d + 0.06), "skorzany_ciemny", "matowy")
    return p


def zwiadowca(bron=False):
    """Koci Zwiadowca: rudy Kot-Mag (rasa Człowiek) w stroju Zwiadowcy (bron=True: łuk w lewej łapce)."""
    from swiat.postacie import zwiadowca as Z
    p = KM.cialo()
    p.id, p.nazwa = "kot_zwiadowca", "Koci Zwiadowca"
    _zwiadowca_stroj(p)
    if not bron:
        return p
    luk = Z.luk()
    a, _ = _bron(luk, None)
    p.zaloz(a, zaczep=luk.zaczep)
    return p


def zbuduj():
    return [rycerz(), zwiadowca()]


if __name__ == "__main__":
    if "--kontrola" in sys.argv:
        for p in zbuduj():
            b, u = p.sprawdz()
            print(p.id, "błędy:", len(b), "uwagi:", len(u))
            for x in b[:10]:
                print("  B", x)
            for x in u[:5]:
                print("  U", x)
