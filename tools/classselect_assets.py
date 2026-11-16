#!/usr/bin/env python3
"""Grafiki ekranu wyboru klasy (po ekranie ładowania): tnie arkusz elementów i tło.

Wejście:  assets/raw/ClassSelectUI/v1.png (arkusz 8 elementów), assets/raw/ClassSelectBg/v1.png (tło 16:9)
Wyjście:  assets/processed/ClassSelect/*.png
  - CsArrowLeft, CsArrowRight, CsPlayButton, CsTitlePlank, CsStatsPanel, CsEmblemWarrior, CsEmblemScout, CsEmblemMage
  - CsBg1..CsBg4: tło 2048x1152 pocięte 2x2 (Roblox zmniejsza każdy obraz do 1024 px)
Elementy arkusza rozpoznawane po położeniu (układ z wygenerowanego obrazu, Higgsfield 16.11.2026).

Użycie: python tools/classselect_assets.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import process_image as PI  # noqa: E402

RAW = ROOT / "assets/raw"
OUT = ROOT / "assets/processed/ClassSelect"


def components(im: Image.Image):
    a = np.asarray(im).astype(int)
    fg = a.min(-1) < 232
    fg = ndimage.binary_fill_holes(ndimage.binary_closing(fg, iterations=3))
    lab, _ = ndimage.label(fg)
    H, W = fg.shape
    out = []
    for sl in ndimage.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if h * w > 0.005 * H * W:
            out.append(((sl[1].start + sl[1].stop) / 2 / W, (sl[0].start + sl[0].stop) / 2 / H,
                        (sl[1].start, sl[0].start, sl[1].stop, sl[0].stop)))
    return out


def name_of(cx, cy, box, W, H):
    w, h = (box[2] - box[0]) / W, (box[3] - box[1]) / H
    if cy < 0.35:
        if cx < 0.25:
            return "CsArrowLeft"
        if cx < 0.5:
            return "CsArrowRight"
        return "CsPlayButton"
    if cx < 0.32 and h > w:
        return "CsStatsPanel"
    if cy < 0.65:
        return "CsTitlePlank"
    return {0: "CsEmblemWarrior", 1: "CsEmblemScout", 2: "CsEmblemMage"}[min(2, int((cx - 0.3) / 0.233))]


SIZES = {"CsArrowLeft": 256, "CsArrowRight": 256, "CsPlayButton": 640, "CsTitlePlank": 768, "CsStatsPanel": 640,
         "CsEmblemWarrior": 256, "CsEmblemScout": 256, "CsEmblemMage": 256}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.open(RAW / "ClassSelectUI/v1.png").convert("RGB")
    W, H = sheet.size
    seen = []
    for cx, cy, box in components(sheet):
        n = name_of(cx, cy, box, W, H)
        pad = 14
        crop = sheet.crop((max(0, box[0] - pad), max(0, box[1] - pad), min(W, box[2] + pad), min(H, box[3] + pad)))
        rgba = PI.trim(PI.remove_bg_flood(crop.convert("RGBA"), 30))
        PI.fit(rgba, SIZES[n]).save(OUT / f"{n}.png")
        seen.append(n)
    missing = set(SIZES) - set(seen)
    if missing or len(seen) != len(SIZES):
        raise SystemExit(f"arkusz: znaleziono {sorted(seen)}, brak {sorted(missing)}")

    bg = Image.open(RAW / "ClassSelectBg/v1.png").convert("RGB").resize((2048, 1152), Image.LANCZOS)
    for i, (cx, cy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)], 1):
        bg.crop((cx * 1024, cy * 576, (cx + 1) * 1024, (cy + 1) * 576)).save(OUT / f"CsBg{i}.png")
    print("ok:", ", ".join(sorted(seen)), "+ CsBg1..4")


if __name__ == "__main__":
    main()
