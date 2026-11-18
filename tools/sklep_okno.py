#!/usr/bin/env python3
"""Okna sklepów 4:3 (Paweł 18.11): poprawka ramki bohatera i cięcie do Roblox.

1. Ramka bohatera ma proporcje jak w oknie ekwipunku (ok. 1,06 : 1 zamiast 0,88 : 1): ekran portretu jest
   skracany o wycinek ze środka (gładki granat), górna część ramki zjeżdża w dół, pasek poziomu i slot broni
   zostają. Pasy nad ramką są uzupełniane tłem z wiersza wyżej; szwy wypadają na krawędziach kolumn ekwipunku.
2. Wynik: assets/processed/Sklepy/sklep_<rodzaj>.png (4800 × 3584) + podgląd JPG.
3. Kafelki do Roblox 2 × 2 (każdy 1024 px szerokości): assets/processed/Sklepy/Sklep<Rodzaj><n>.png
   oraz uklad_sklepow.json — prostokąty elementów (ułamki okna) do GUI.

Użycie: python tools/sklep_okno.py
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "assets/raw/Sklepy"
OUT = ROOT / "assets/processed/Sklepy"
RODZAJE = {"bron": "Bron", "magia": "Magia"}

# px okna 4800 × 3584 (zmierzone na sklep_magia_4x3_v1.png; sklep z bronią ma ten sam układ)
PASEK_X = (790, 1828)      # między kolumnami slotów ekwipunku
RAMKA_GORA = 557           # górna krawędź złotej ramki portretu
CIECIE = (1030, 1177)      # wycinany pas gładkiego granatu (147 px)
TLO_Z = 410                # skąd brać tło na odsłonięty pas nad ramką

# elementy (ułamki okna) do napisów i przycisków w GUI — zmierzone na grafice
UKLAD = {
    "tytul_lewy": [0.133, 0.042, 0.273, 0.08],
    "tytul_prawy": [0.594, 0.042, 0.278, 0.08],
    "zamknij": [0.926, 0.055, 0.05, 0.052],
    "portret": [0.194, 0.198, 0.156, 0.192],
    "poziom": [0.211, 0.39, 0.122, 0.042],
    "zakladki": [[0.087, 0.563, 0.088, 0.03], [0.18, 0.563, 0.089, 0.03], [0.274, 0.563, 0.087, 0.03],
                 [0.367, 0.563, 0.089, 0.03]],
    "plecak": [0.089, 0.61, 0.361, 0.28],
    "tabliczka": [0.591, 0.561, 0.279, 0.071],
    "odswiez": [0.87, 0.562, 0.052, 0.069],
    "sloty_sklepu": [[0.578, 0.655, 0.083, 0.107], [0.692, 0.655, 0.083, 0.107], [0.807, 0.655, 0.083, 0.107],
                     [0.578, 0.781, 0.083, 0.109], [0.692, 0.781, 0.083, 0.109], [0.807, 0.781, 0.083, 0.109]],
    "sprzedawca": [0.6, 0.15, 0.3, 0.38],
}


def popraw_ramke(im):
    a = np.array(im.convert("RGBA"))
    x0, x1 = PASEK_X
    c0, c1 = CIECIE
    d = c1 - c0
    nowy = a.copy()
    # górna część ramki (od krawędzi ramki do początku cięcia) zjeżdża o d w dół
    nowy[RAMKA_GORA + d:c1, x0:x1] = a[RAMKA_GORA:c0, x0:x1]
    # odsłonięty pas nad ramką: tło z wierszy powyżej
    nowy[RAMKA_GORA:RAMKA_GORA + d, x0:x1] = a[TLO_Z:TLO_Z + d, x0:x1]
    return Image.fromarray(nowy)


def bez_tla(im, prog=232):
    """Białe tło połączone z brzegiem obrazu -> przezroczyste (zalewanie od krawędzi; biel wewnątrz okna zostaje)."""
    from scipy import ndimage
    a = np.array(im.convert("RGBA"))
    white = a[..., :3].min(axis=2) > prog
    lab, _ = ndimage.label(white)
    brzeg = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    poza = ndimage.binary_dilation(np.isin(lab, list(brzeg)), iterations=1)
    a[..., 3] = np.where(poza, 0, a[..., 3]).astype(np.uint8)
    return Image.fromarray(a)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for rodzaj, nazwa in RODZAJE.items():
        src = RAW / f"sklep_{rodzaj}_4x3_v1.png"
        im = bez_tla(popraw_ramke(Image.open(src)))
        im.save(OUT / f"sklep_{rodzaj}.png", optimize=True)
        im.convert("RGB").resize((1600, round(1600 * im.height / im.width)), Image.LANCZOS).save(
            OUT / f"sklep_{rodzaj}_podglad.jpg", quality=88)
        w, h = im.size
        for i, (cx, cy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)], 1):
            kaf = im.crop((cx * w // 2, cy * h // 2, (cx + 1) * w // 2, (cy + 1) * h // 2))
            kaf.resize((1024, round(1024 * kaf.height / kaf.width)), Image.LANCZOS).save(OUT / f"Sklep{nazwa}{i}.png", optimize=True)
        print("ok", rodzaj, im.size)
    (OUT / "uklad_sklepow.json").write_text(json.dumps({"proporcje": round(4800 / 3584, 5), **UKLAD}, indent=1),
                                            encoding="utf-8")


if __name__ == "__main__":
    main()
