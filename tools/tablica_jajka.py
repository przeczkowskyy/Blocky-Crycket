#!/usr/bin/env python3
"""Tablica szans jajka (Paweł 24.11: zamiast wyciętego okna — osobne, proste okienko jak podpowiedź Karola: pety
z paskami szans w kolorach rzadkości, na dole klawisz E, cena i rybka). Higgsfield job 457636d8 (jedna wersja).
Generator wpisał na deskę tytułu „BLOCKY & CRYCKET” — zamalowujemy napis drewnem z lewego końca tej samej deski
(każdy wiersz wnętrza deski = mediana koloru z jej końca — słoje są poziome), potem białe tło ->
przezroczyste. Wynik: assets/processed/SzanseJajka/TablicaSzansJajka.png.

Użycie: python tools/tablica_jajka.py
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "assets/raw/SzanseJajka/tablica_v1.png"
OUT = ROOT / "assets/processed/SzanseJajka"
# piksele obrazu 1792 × 2400 (podgląd 520 px × 3,446)
NAPIS = (520, 70, 1325, 460)      # x0, y0, x1, y1 — całe wnętrze deski między obrysami (litery 112–413)
PASEK = (372, 512)                # x0, x1 — czyste drewno na lewym końcu deski


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    a = np.array(Image.open(RAW).convert("RGB"))
    x0, y0, x1, y1 = NAPIS
    px0, px1 = PASEK
    # każdy wiersz wnętrza = mediana koloru drewna z lewego końca deski (poziome słoje, bez powtarzanego wzoru
    # i bez połysków z końca deski), z lekkim przejściem do oryginału przy brzegach napisu
    pas = a[y0:y1, px0:px1].astype(float)
    wiersze = np.median(pas, axis=1)  # (wysokość, 3)
    for i, y in enumerate(range(y0, y1)):
        a[y, x0:x1] = wiersze[i].astype(np.uint8)
    rgba = np.dstack([a, np.full(a.shape[:2], 255, np.uint8)])
    biale = a.min(axis=2) > 232
    lab, _ = ndimage.label(biale)
    brzeg = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    rgba[..., 3] = np.where(np.isin(lab, list(brzeg)), 0, 255).astype(np.uint8)
    out = Image.fromarray(rgba)
    out = out.crop(out.getbbox())
    out.save(OUT / "TablicaSzansJajka.png", optimize=True)
    print("ok", out.size, "proporcje", round(out.width / out.height, 4))


if __name__ == "__main__":
    main()
