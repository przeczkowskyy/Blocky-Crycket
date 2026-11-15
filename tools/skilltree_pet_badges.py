#!/usr/bin/env python3
"""Ikony PET INTELLIGENCE i PET DEXTERITY (polecenie Pawła 15.11): łapa peta ze znaczkiem książki / buta.

Bierze ikony NodePetStatAll (łapa + gwiazdka) i NodePetStatSpeed (łapa + piorun), zamalowuje znaczek
(gwiazdkę / piorun) kolorem otoczenia, a w jego miejsce wkleja książkę z NodeStatInt i but z NodeStatDex
(symbol wycięty z fioletowej tarczy). Wynik: assets/processed/SkillTree/NodePetStatInt.png, NodePetStatDex.png.

Użycie: python tools/skilltree_pet_badges.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "assets/processed/SkillTree"


def load(n):
    return np.asarray(Image.open(D / f"{n}.png").convert("RGBA")).astype(np.int32)


def erase_badge(a):
    """Zamalowuje żółty znaczek (gwiazdka / piorun) z obrysem: każdy piksel dostaje kolor najbliższego piksela spoza znaczka."""
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    h, w = r.shape
    yy, xx = np.mgrid[0:h, 0:w]
    inner = (xx - w / 2) ** 2 + (yy - h / 2) ** 2 < (w * 0.40) ** 2  # bez złotej obwódki medalionu
    # rozmiar i środek: główna żółta część znaczka
    yellow = (r > 190) & (g > 140) & (b < 120) & (al > 200) & inner
    lab, k = ndimage.label(yellow)
    big = int(np.argmax(ndimage.sum(yellow, lab, range(1, k + 1)))) + 1
    badge = ndimage.binary_fill_holes(lab == big)
    ys, xs = np.nonzero(badge)
    center, size = ((xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2), max(np.ptp(xs), np.ptp(ys))
    # zamalowanie: też pomarańczowe krawędzie i czubki przy znaczku (czerwona tarcza ma g < 90, łapa r < 120)
    warm = (r > 180) & (g > 95) & (b < 120) & (r - b > 90) & inner
    erase = badge | (warm & ndimage.binary_dilation(badge, iterations=10))
    dark = a[..., :3].max(-1) < 90
    ring = ndimage.binary_dilation(erase, iterations=7) & dark  # czarny obrys znaczka
    mask = ndimage.binary_dilation(erase | ring, iterations=2) & inner
    _, (iy, ix) = ndimage.distance_transform_edt(mask, return_indices=True)
    out = a.copy()
    out[mask] = a[iy[mask], ix[mask]]
    return out, center, size


def cut_symbol(a):
    """Symbol z fioletowej tarczy: wszystko w środku koła, co nie jest fioletem tła, największa spójna część."""
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    inner = (xx - w / 2) ** 2 + (yy - h / 2) ** 2 < (w * 0.39) ** 2
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    purple = (b > 120) & (r > 95) & (r - g > 35) & (b - g > 50)
    cand = inner & ~purple & (a[..., 3] > 200)
    cand = ndimage.binary_opening(cand, iterations=2)  # kropki rastra tła odpadają
    lab, k = ndimage.label(cand)
    big = int(np.argmax(ndimage.sum(cand, lab, range(1, k + 1)))) + 1
    m = ndimage.binary_fill_holes(lab == big)
    m = ndimage.binary_dilation(m, iterations=1)
    m &= ~((r - g > 25) & (b - g > 35) & (b > 100))  # fioletowa obwódka tła przy brzegu symbolu
    m = ndimage.binary_opening(m, iterations=1) | ndimage.binary_erosion(m, iterations=2)
    out = a.copy()
    out[..., 3] = np.where(m, 255, 0)
    img = Image.fromarray(out.astype(np.uint8))
    alpha = img.getchannel("A").filter(ImageFilter.GaussianBlur(0.7))
    img.putalpha(alpha)
    return img.crop(img.getbbox())


def make(base_name, symbol_name, out_name, scale=1.25):
    base, (cx, cy), size = erase_badge(load(base_name))
    sym = cut_symbol(load(symbol_name))
    s = size * scale / max(sym.size)
    sym = sym.resize((round(sym.width * s), round(sym.height * s)), Image.LANCZOS)
    img = Image.fromarray(base.astype(np.uint8))
    img.alpha_composite(sym, (round(cx - sym.width / 2), round(cy - sym.height / 2)))
    img.save(D / f"{out_name}.png")
    print("ok", out_name, img.size)


if __name__ == "__main__":
    make("NodePetStatAll", "NodeStatInt", "NodePetStatInt")
    make("NodePetStatSpeed", "NodeStatDex", "NodePetStatDex")
