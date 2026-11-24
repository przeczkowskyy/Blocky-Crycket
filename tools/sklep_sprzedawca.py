#!/usr/bin/env python3
"""Nowy sprzedawca w gotowym oknie sklepu (Paweł 24.11: w grafikach sklepów modele NPC Karola zamiast kota i rycerza).

Higgsfield przerysowuje całe okno, więc nowa grafika jest dopasowywana do obecnej (ORB + RANSAC, przekształcenie
podobieństwa), a do gotowego assets/processed/Sklepy/sklep_<rodzaj>.png trafia TYLKO obszar sprzedawcy w prawym
panelu (nad ladą) — miękko łączony tam, gdzie obrazy się różnią. Ramki, sloty, zakładki i przyciski zostają co do
piksela, więc uklad_sklepow.json i GUI (tools/shop_build_gui.py) się nie zmieniają.
Potem cięcie 2 × 2 jak w tools/sklep_okno.py -> Sklep<Rodzaj>1..4.png.

Użycie: python tools/sklep_sprzedawca.py bron assets/raw/Sklepy/sklep_bron_zbrojmistrz_v1.png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from skimage.feature import ORB, match_descriptors
from skimage.measure import ransac
from skimage.transform import SimilarityTransform, warp

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/processed/Sklepy"
OBSZAR = (0.535, 0.075, 0.945, 0.585)  # prawy panel od tabliczki tytułu do lady (ułamki okna)


def dopasuj(stary, nowy):
    k = 1200 / stary.width
    def szary(im):
        kk = 1200 / im.width
        return np.array(im.convert("L").resize((1200, int(im.height * kk))), dtype=float) / 255
    orb = ORB(n_keypoints=3000, fast_threshold=0.05)
    orb.detect_and_extract(szary(stary)); ks, ds = orb.keypoints, orb.descriptors
    orb.detect_and_extract(szary(nowy)); kn, dn = orb.keypoints, orb.descriptors
    m = match_descriptors(ds, dn, cross_check=True, max_ratio=0.8)
    src = kn[m[:, 1]][:, ::-1] * (nowy.width / 1200)
    dst = ks[m[:, 0]][:, ::-1] / k
    model, inl = ransac((src, dst), SimilarityTransform, min_samples=3, residual_threshold=6, max_trials=5000)
    print(f"dopasowanie: {inl.sum()}/{len(m)} punktów, skala {model.scale:.4f}, obrót {np.degrees(model.rotation):.3f}°")
    a = np.array(nowy.convert("RGB"), dtype=float) / 255
    w = warp(a, model.inverse, output_shape=(stary.height, stary.width), order=1, mode="edge")
    return (w * 255).astype(np.uint8)


def main():
    rodzaj, sciezka = sys.argv[1], Path(sys.argv[2])
    stary_plik = OUT / f"sklep_{rodzaj}.png"
    kopia = OUT / f"sklep_{rodzaj}_przed_npc.png"
    if not kopia.exists():
        Image.open(stary_plik).save(kopia)
    stary = Image.open(kopia).convert("RGBA")
    a = np.array(stary)
    n = dopasuj(stary, Image.open(sciezka))
    H, W = a.shape[:2]
    x0, y0, x1, y1 = (int(OBSZAR[0] * W), int(OBSZAR[1] * H), int(OBSZAR[2] * W), int(OBSZAR[3] * H))
    # maska: różnice w obszarze sprzedawcy, domknięte i rozmyte (bez ostrych szwów)
    roz = np.abs(n.astype(int) - a[..., :3].astype(int)).sum(axis=2) > 60
    maska = np.zeros((H, W), bool)
    maska[y0:y1, x0:x1] = roz[y0:y1, x0:x1]
    m = Image.fromarray((maska * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MaxFilter(41)).filter(ImageFilter.MinFilter(21)).filter(ImageFilter.GaussianBlur(10))
    mm = np.array(m, dtype=float)[..., None] / 255
    ramka = np.zeros((H, W, 1)); ramka[y0:y1, x0:x1] = 1
    mm = np.minimum(mm, np.array(Image.fromarray((ramka[..., 0] * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(6)), dtype=float)[..., None] / 255)
    wyn = a.copy()
    wyn[..., :3] = (a[..., :3] * (1 - mm) + n * mm).astype(np.uint8)
    out = Image.fromarray(wyn)
    out.save(stary_plik)
    podglad = out.convert("RGB"); podglad.thumbnail((1600, 1600)); podglad.save(OUT / f"sklep_{rodzaj}_podglad.jpg", quality=88)
    # kafelki 2 × 2 do Roblox (jak tools/sklep_okno.py)
    nazwa = {"bron": "Bron", "magia": "Magia"}[rodzaj]
    hw, hh = W // 2, H // 2
    for i, (cx, cy) in enumerate(((0, 0), (1, 0), (0, 1), (1, 1)), 1):
        kaf = out.crop((cx * hw, cy * hh, cx * hw + hw, cy * hh + hh))
        kaf = kaf.resize((1024, round(1024 * kaf.height / kaf.width)), Image.LANCZOS)
        kaf.save(OUT / f"Sklep{nazwa}{i}.png", optimize=True)
    print("zapisano", stary_plik.name, "i kafelki", nazwa)


if __name__ == "__main__":
    main()
