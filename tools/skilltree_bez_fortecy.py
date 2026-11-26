#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ramka drzewka bez środkowej zakładki (Fortress) — polecenie Pawła 25.11.2026: na razie tylko PLAYER i PETS.

    python tools/skilltree_bez_fortecy.py

Czyta assets/processed/SkillTree/SkillTreeFrame.png (zakładki są wypalone w grafice) i zapisuje
assets/processed/SkillTree/SkillTreeFrameDwie.png: fioletowa zakładka zamalowana kolorem tła ramki, obrysy
sąsiednich zakładek (pomarańczowej i zielonej) zostają. Oryginał bez zmian — powrót do trzech zakładek to
podmiana obrazu w src/gui/SkillTree.model.json.
"""
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

KATALOG = Path(__file__).resolve().parent.parent / "assets" / "processed" / "SkillTree"
WE = KATALOG / "SkillTreeFrame.png"
WY = KATALOG / "SkillTreeFrameDwie.png"
OBSZAR = (300, 100, 680, 187)   # prostokąt wokół środkowej zakładki; y=187 to już obrys panelu
OBRYS = 6                       # grubość czarnego obrysu zakładki z zapasem
SASIAD = 4                      # tyle pikseli obrysu zostaje przy sąsiednich zakładkach


def maska(obraz, warunek):
    r, g, b = obraz.split()[:3]
    dane = [255 if warunek(p) else 0 for p in zip(r.getdata(), g.getdata(), b.getdata())]
    m = Image.new("L", obraz.size)
    m.putdata(dane)
    return m


def main():
    im = Image.open(WE).convert("RGBA")
    wycinek = im.crop(OBSZAR)
    rgb = wycinek.convert("RGB")
    fiolet = maska(rgb, lambda p: p[2] > 95 and p[2] - p[1] > 40 and p[0] > 60 and p[0] < p[2] + 30 and p[1] < 190)
    sasiedzi = maska(rgb, lambda p: (p[0] > 180 and p[1] > 110 and p[2] < 140 and p[0] - p[2] > 80)      # pomarańcz
                     or (p[1] > 120 and p[1] - p[0] > 25 and p[1] - p[2] > 10))                             # zieleń
    do_zamalowania = fiolet.filter(ImageFilter.MaxFilter(2 * OBRYS + 1))
    chronione = sasiedzi.filter(ImageFilter.MaxFilter(2 * SASIAD + 1))
    do_zamalowania = ImageChops.subtract(do_zamalowania, chronione)
    # tło: kolor ramki z lekkim szumem jak w oryginale (rastrowe kropki są tylko w rogach)
    tlo = Image.new("RGBA", wycinek.size, (105, 65, 49, 255))
    miekka = do_zamalowania.filter(ImageFilter.GaussianBlur(0.6))
    wynik = Image.composite(tlo, wycinek, miekka)
    im.paste(wynik, OBSZAR[:2])
    im.save(WY)
    print("zapisano", WY, im.size)


if __name__ == "__main__":
    main()
