#!/usr/bin/env python3
"""Wymazuje starą, pustą ramkę portretu z tła okien (Paweł 23.11: „usuwamy totalnie stare i wgrywamy w miejsce nowe”).

W oknie ekwipunku i w oknach sklepów ramka portretu (złota, z paskiem doświadczenia) jest wypalona w grafice tła.
Gra kładzie w jej prostokąt ramkę z portretem rasy (Shared.RacePortraitUI), a tu stara ramka znika z tła:
obszar (zaokrąglony prostokąt z małym zapasem) wypełnia się otaczającym tłem — średnią z interpolacji w poziomie
i w pionie między krawędziami obszaru, potem lekkie rozmycie. Nowa ramka zakrywa to miejsce w całości.

- Ekwipunek: assets/processed/EquipmentPanel/EqBg1.png (kopia sprzed wymazania: assets/raw/EquipmentPanel/EqBg1_z_ramka.png)
- Sklepy: funkcja `wymaz` jest wołana w tools/sklep_okno.py (po poprawce proporcji ramki, przed cięciem na kafelki).
Użycie: python tools/wymaz_stare_ramki.py   (tylko ekwipunek; sklepy: python tools/sklep_okno.py)
"""
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
EQ = ROOT / "assets/processed/EquipmentPanel/EqBg1.png"
EQ_KOPIA = ROOT / "assets/raw/EquipmentPanel/EqBg1_z_ramka.png"
EQ_RAMKA = (405, 145, 670, 437)  # px w EqBg1 (1024 × 583): stara ramka z paskiem


def maska(h, w, box, zapas, promien):
    x0, y0, x1, y1 = box[0] - zapas, box[1] - zapas, box[2] + zapas, box[3] + zapas
    yy, xx = np.mgrid[0:h, 0:w]
    m = (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
    for cx, cy in ((x0 + promien, y0 + promien), (x1 - promien, y0 + promien), (x0 + promien, y1 - promien), (x1 - promien, y1 - promien)):
        rog = ((xx < x0 + promien) if cx < (x0 + x1) / 2 else (xx > x1 - promien)) & \
              ((yy < y0 + promien) if cy < (y0 + y1) / 2 else (yy > y1 - promien))
        m &= ~(rog & ((xx - cx) ** 2 + (yy - cy) ** 2 > promien ** 2))
    return m


def wymaz(im, box, zapas=None):
    """Zwraca kopię obrazu (RGB/RGBA) z wymazaną ramką w prostokącie `box` (x0, y0, x1, y1)."""
    tryb = im.mode
    a = np.array(im.convert("RGBA")).astype(float)
    h, w = a.shape[:2]
    bw = box[2] - box[0]
    zapas = zapas if zapas is not None else max(3, round(bw * 0.02))
    m = maska(h, w, box, zapas, promien=round(bw * 0.12))
    wynik = a.copy()
    ys, xs = np.where(m)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    poz = np.zeros_like(a)
    pion = np.zeros_like(a)
    wp = np.zeros((h, w))
    wv = np.zeros((h, w))
    for y in range(y0, y1 + 1):
        kol = np.where(m[y])[0]
        if len(kol) == 0:
            continue
        l, r = kol.min() - 1, kol.max() + 1
        t = (np.arange(l + 1, r) - l) / (r - l)
        poz[y, l + 1:r] = (1 - t)[:, None] * a[y, l] + t[:, None] * a[y, r]
        wp[y, l + 1:r] = 1 / np.minimum(np.arange(l + 1, r) - l, r - np.arange(l + 1, r))
    for x in range(x0, x1 + 1):
        wie = np.where(m[:, x])[0]
        if len(wie) == 0:
            continue
        t0, b = wie.min() - 1, wie.max() + 1
        t = (np.arange(t0 + 1, b) - t0) / (b - t0)
        pion[t0 + 1:b, x] = (1 - t)[:, None] * a[t0, x] + t[:, None] * a[b, x]
        wv[t0 + 1:b, x] = 1 / np.minimum(np.arange(t0 + 1, b) - t0, b - np.arange(t0 + 1, b))
    suma = (wp + wv)[..., None]
    suma[suma == 0] = 1
    wypel = (poz * wp[..., None] + pion * wv[..., None]) / suma
    wynik[m] = wypel[m]
    out = Image.fromarray(wynik.clip(0, 255).astype(np.uint8))
    rozmyte = out.filter(ImageFilter.GaussianBlur(max(2, bw // 60)))
    out = Image.composite(rozmyte, out, Image.fromarray((m * 255).astype(np.uint8)))
    return out.convert(tryb) if tryb in ("RGB", "RGBA") else out


def main():
    if not EQ_KOPIA.exists():
        EQ_KOPIA.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(EQ, EQ_KOPIA)
    im = Image.open(EQ_KOPIA)
    wymaz(im, EQ_RAMKA).save(EQ, optimize=True)
    print("ok", EQ.relative_to(ROOT))


if __name__ == "__main__":
    main()
