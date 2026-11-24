#!/usr/bin/env python3
"""Tekstury jajka korowego (Paweł 24.11: „wygeneruj nowe stricte pod to jajko, jak najbliżej referencji”).
Arkusz 2 × 2 (Higgsfield, Nano Banana 2.1, job 78b52b6f, referencja jajka od Pawła) -> 4 kafelki 1024 px:
z każdego kwadratu bierzemy wnętrze bez czarnej ramki i bez połysku w lewym górnym rogu (dolne prawe 62%),
bez odbić lustrzanych (dawały „kalejdoskop”). Ściany części jajka są mniejsze niż jedno powtórzenie tekstury
(StudsPerTile w tools/studio/jajko_korowe_studio.py), więc szwów nie widać.

Użycie: python tools/jajko_tekstury.py
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "assets/raw/JajkoTekstury/tekstury_v1.png"
OUT = ROOT / "assets/processed/JajkoTekstury"
NAZWY = ["JajkoKora", "JajkoKorzen", "JajkoMech", "JajkoSkorupa"]  # kolejność: rzędami od lewej


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    a = np.array(Image.open(RAW).convert("RGB"))
    tresc = a.min(axis=2) < 225
    lab, _ = ndimage.label(ndimage.binary_closing(tresc, iterations=4))
    obiekty = sorted(ndimage.find_objects(lab), key=lambda s: -(s[0].stop - s[0].start) * (s[1].stop - s[1].start))[:4]
    obiekty = sorted(obiekty, key=lambda s: (round(s[0].start / 800), s[1].start))
    for nazwa, s in zip(NAZWY, obiekty):
        y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
        w, h = x1 - x0, y1 - y0
        bok = int(min(w, h) * 0.62)
        zapas = int(min(w, h) * 0.035)  # za czarną ramką
        kaw = Image.fromarray(a[y1 - zapas - bok:y1 - zapas, x1 - zapas - bok:x1 - zapas])
        k = kaw.resize((1024, 1024), Image.LANCZOS)
        k.save(OUT / f"{nazwa}.png", optimize=True)
        print("ok", nazwa, (x0, y0, w, h))


if __name__ == "__main__":
    main()
