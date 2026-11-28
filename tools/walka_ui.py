#!/usr/bin/env python3
"""Zestaw elementów ekranu walki z jednej generacji Higgsfield (Paweł 28.11: „UI walk w naszym stylu”; nano_banana_2_1,
1 wariant, ref KeyArt; job be5dcec8): tnie arkusz assets/raw/WalkaUI/v1_1.png na dziesięć elementów i wycina tło.
Napisy, cyfry i paski życia są w grze natywne (Paweł: paski nie z tekstur) — elementy są puste.

    python tools/walka_ui.py            # -> assets/processed/WalkaUI/<Nazwa>.png + podgląd build/walka_ui_podglad.jpg
"""
import os
import subprocess
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARKUSZ = os.path.join(ROOT, "assets", "raw", "WalkaUI", "v1_1.png")
WYJ = os.path.join(ROOT, "assets", "processed", "WalkaUI")
K = 2752 / 1100  # współrzędne zmierzone na podglądzie 1100 px
ELEMENTY = [  # nazwa, (x0, y0, x1, y1) na podglądzie, do czego
    ("WalkaBtnZolty", (40, 28, 177, 162), "tempo ×1/×2/×4 — wybrane"),
    ("WalkaBtnSzary", (200, 28, 337, 162), "tempo — niewybrane"),
    ("WalkaBtnDzwiek", (360, 28, 497, 162), "dźwięk"),
    ("WalkaBtnSzerokiZolty", (515, 38, 787, 152), "POMIŃ"),
    ("WalkaBtnSzerokiCzerwony", (795, 38, 1067, 152), "ZAMKNIJ"),
    ("WalkaVs", (30, 172, 217, 358), "plakietka VS / tura"),
    ("WalkaBaner", (235, 202, 677, 332), "baner ZWYCIĘSTWO"),
    ("WalkaKafel", (708, 182, 882, 352), "kafel nagrody"),
    ("WalkaKafelSzary", (888, 182, 1062, 352), "kafel nagrody — brak"),
    ("WalkaOkno", (30, 362, 1070, 594), "okno wyniku (9-slice)"),
]


def main():
    os.makedirs(WYJ, exist_ok=True)
    im = Image.open(ARKUSZ).convert("RGB")
    for nazwa, (x0, y0, x1, y1), _ in ELEMENTY:
        surowy = os.path.join(os.path.dirname(ARKUSZ), "v1_1_%s.png" % nazwa)
        im.crop(tuple(round(v * K) for v in (x0, y0, x1, y1))).save(surowy)
        cel = os.path.join(WYJ, nazwa + ".png")
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "process_image.py"), surowy, cel, "--category", "button"],
                       capture_output=True)
        print(nazwa, Image.open(cel).size if os.path.exists(cel) else "BŁĄD")
    plansza = Image.new("RGB", (1500, 620), (70, 110, 160))
    x = y = 12
    wiersz = 0
    for nazwa, _, _ in ELEMENTY:
        p = os.path.join(WYJ, nazwa + ".png")
        if not os.path.exists(p):
            continue
        a = Image.open(p).convert("RGBA")
        a.thumbnail((440, 180))
        if x + a.width > 1490:
            x, y, wiersz = 12, y + wiersz + 14, 0
        plansza.paste(a, (x, y), a)
        x += a.width + 14
        wiersz = max(wiersz, a.height)
    plansza.save(os.path.join(ROOT, "build", "walka_ui_podglad.jpg"), quality=88)


if __name__ == "__main__":
    main()
