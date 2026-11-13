#!/usr/bin/env python3
"""Rysuje testową ikonę przedmiotu „Scrap” w pixel-arcie (32x32 -> 256x256, skalowanie bez wygładzania).

Zardzewiałe kółko zębate + śrubka, czarny obrys 1 px (Style Lock: ikony UI w ostrym pixel-arcie).
Użycie: python tools/make_item_scrap.py  ->  assets/processed/ItemScrap.png
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/processed/ItemScrap.png"
N = 32
OUTLINE = (26, 20, 16)
METAL = [(95, 100, 112), (141, 146, 158), (185, 190, 200), (232, 236, 242)]  # ciemny -> połysk
RUST = [(122, 58, 24), (176, 92, 40), (214, 128, 58)]


def main():
    img = np.zeros((N, N, 4), np.uint8)
    cx, cy = 13.0, 13.5
    body = np.zeros((N, N), bool)
    shade = np.zeros((N, N))
    for y in range(N):
        for x in range(N):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            tooth = (math.cos(ang * 8) > 0.35)
            outer = 10.2 if tooth else 8.4
            if r <= outer and r >= 3.0:
                body[y, x] = True
                shade[y, x] = -(dx + dy) / 14  # światło z lewej góry
    # śrubka (sześciokąt) w prawym dolnym rogu
    bolt = np.zeros((N, N), bool)
    bx, by = 23.5, 23.5
    for y in range(N):
        for x in range(N):
            dx, dy = x + 0.5 - bx, y + 0.5 - by
            if max(abs(dx), abs(dx) * 0.5 + abs(dy) * 0.866) <= 4.6:
                bolt[y, x] = True
    for y in range(N):
        for x in range(N):
            if body[y, x]:
                s = shade[y, x]
                c = METAL[3] if s > 0.55 else METAL[2] if s > 0.1 else METAL[1] if s > -0.45 else METAL[0]
                # plamy rdzy (deterministyczne)
                if ((x * 7 + y * 13) % 11 == 0) or (x > 15 and y > 12 and (x + y) % 3 == 0):
                    c = RUST[1] if s > -0.2 else RUST[0]
                img[y, x] = c + (255,)
            elif bolt[y, x]:
                s = -((x + 0.5 - bx) + (y + 0.5 - by)) / 6
                c = RUST[2] if s > 0.3 else RUST[1] if s > -0.3 else RUST[0]
                img[y, x] = c + (255,)
    # rowek w łbie śrubki
    for i in range(-2, 3):
        img[int(by) + i, int(bx) - i] = OUTLINE + (255,)
    # obrys 1 px
    filled = img[..., 3] > 0
    ring = ndimage.binary_dilation(filled) & ~filled
    hole = ndimage.binary_fill_holes(filled) & ~filled  # otwór w środku kółka
    hole_ring = ndimage.binary_dilation(hole) & filled
    img[ring] = OUTLINE + (255,)
    img[hole_ring] = OUTLINE + (255,)
    Image.fromarray(img).resize((256, 256), Image.NEAREST).save(OUT)
    print("ok", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
