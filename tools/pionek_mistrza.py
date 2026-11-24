#!/usr/bin/env python3
"""Pionek mistrza gier (Paweł 24.11: „żeby po planszy ten pionek rzeczywiście się poruszał”, nie ikona gracza).
Dwie generacje tej samej grafiki: z pionkiem (okno_mistrza_v1.png) i bez pionka (okno_mistrza_bez_pionka.png,
edycja Higgsfield, job b4a34a31). Dopasowanie (ORB + RANSAC, jak tools/sklep_sprzedawca.py), różnica w okolicy pola
startowego = pionek:
  - PionekMistrza.png — pionek z przezroczystym tłem (piksele z wersji z pionkiem tam, gdzie obrazy się różnią);
  - w gotowym assets/processed/OknoMistrzaGier/OknoMistrzaGier.png pole startowe bez pionka (fragment z drugiej
    wersji), potem kafelki 2 × 2 od nowa (zmienia się tylko kafelek 3, lewy dolny).

Użycie: python tools/pionek_mistrza.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sklep_sprzedawca import dopasuj  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RAW_Z = ROOT / "assets/raw/OknoMistrzaGier/okno_mistrza_v1.png"
RAW_BEZ = ROOT / "assets/raw/OknoMistrzaGier/okno_mistrza_bez_pionka.png"
OUT = ROOT / "assets/processed/OknoMistrzaGier"
# okolica pionka w ułamkach gotowego okna (podgląd 1200 × 872: pionek ok. x 95–170, y 670–790)
OBSZAR = (0.06, 0.74, 0.16, 0.93)


def main():
    gotowe = Image.open(OUT / "OknoMistrzaGier.png").convert("RGBA")
    a = np.array(gotowe)
    H, W = a.shape[:2]
    z = dopasuj(gotowe, Image.open(RAW_Z))    # wersja z pionkiem, w układzie gotowego okna
    bez = dopasuj(gotowe, Image.open(RAW_BEZ))
    x0, y0, x1, y1 = (int(OBSZAR[0] * W), int(OBSZAR[1] * H), int(OBSZAR[2] * W), int(OBSZAR[3] * H))
    roz = np.abs(z[y0:y1, x0:x1].astype(int) - bez[y0:y1, x0:x1].astype(int)).sum(axis=2) > 70
    roz = ndimage.binary_opening(roz, iterations=2)
    lab, n = ndimage.label(roz)
    if n == 0:
        raise SystemExit("nie widać pionka w różnicy")
    najw = 1 + int(np.argmax(ndimage.sum(roz, lab, range(1, n + 1))))
    maska = ndimage.binary_fill_holes(ndimage.binary_dilation(lab == najw, iterations=4))
    ys, xs = np.nonzero(maska)
    by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    pion = np.zeros((by1 - by0, bx1 - bx0, 4), np.uint8)
    pion[..., :3] = z[y0 + by0:y0 + by1, x0 + bx0:x0 + bx1]
    alfa = Image.fromarray((maska[by0:by1, bx0:bx1] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    pion[..., 3] = np.array(alfa)
    Image.fromarray(pion).save(OUT / "PionekMistrza.png", optimize=True)
    # pole startowe bez pionka w gotowym oknie (miękko w obrębie maski + zapas)
    m = Image.fromarray((ndimage.binary_dilation(maska, iterations=10) * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(4))
    mm = np.array(m, dtype=float)[..., None] / 255
    a[y0:y1, x0:x1, :3] = (a[y0:y1, x0:x1, :3] * (1 - mm) + bez[y0:y1, x0:x1] * mm).astype(np.uint8)
    out = Image.fromarray(a)
    out.save(OUT / "OknoMistrzaGier.png", optimize=True)
    out.convert("RGB").resize((1600, round(1600 * H / W)), Image.LANCZOS).save(OUT / "OknoMistrzaGier_podglad.jpg",
                                                                              quality=88)
    for i, (cx, cy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)], 1):
        kaf = out.crop((cx * W // 2, cy * H // 2, (cx + 1) * W // 2, (cy + 1) * H // 2))
        kaf.resize((1024, round(1024 * kaf.height / kaf.width)), Image.LANCZOS).save(OUT / f"OknoMistrzaGier{i}.png",
                                                                                     optimize=True)
    # środek dolnej krawędzi pionka względem środka pola startowego — klient stawia go na polu (AnchorPoint 0.5, 0.85)
    print("pionek", pion.shape[1], "x", pion.shape[0], "px; ułamek okna:", round((bx1 - bx0) / W, 4), round((by1 - by0) / H, 4))


if __name__ == "__main__":
    main()
