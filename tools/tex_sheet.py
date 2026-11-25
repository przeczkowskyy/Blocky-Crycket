#!/usr/bin/env python3
"""Tnie arkusz tekstur 4 × 4 (kafelki na białym tle z odstępami) na osobne pliki 1024 × 1024.

Użycie: python tools/tex_sheet.py <arkusz.png> <folder_wyjścia> <prefiks> nazwa1 nazwa2 … nazwa16 [--wciecie 14]
Przykład (drobne rekwizyty sali wyboru klasy):
  python tools/tex_sheet.py assets/raw/ClassSelectProps/v1.png assets/processed/ClassSelectTextures CsProp \\
      Wosk Jablko Kamionka Porcelana Skora Glina Chleb Ser Liscie Stal Owijka Tarcza Korek KamienWneki Szklo Wiklina
Wynik: <prefiks>NN_<nazwa>.png + _arkusz_<prefiks>.jpg (podgląd). Wypisuje kafelki z białymi rogami (ramka do docięcia).
Tło szare zamiast białego (np. arkusz v2 sali, arkusz miasteczka 25.11): --prog 212 (próg jasności tła, domyślnie 235).
"""
import argparse
import os

import numpy as np
from PIL import Image


def segmenty(frac, min_len=200):
    on = frac < 0.9
    out, s = [], None
    for i, v in enumerate(on):
        if v and s is None:
            s = i
        if not v and s is not None:
            if i - s > min_len:
                out.append((s, i))
            s = None
    if s is not None and len(on) - s > min_len:
        out.append((s, len(on)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arkusz")
    ap.add_argument("wyj")
    ap.add_argument("prefiks")
    ap.add_argument("nazwy", nargs=16)
    ap.add_argument("--wciecie", type=int, default=14)
    ap.add_argument("--prog", type=int, default=235, help="próg jasności tła (szare tło: ok. 212)")
    a = ap.parse_args()
    im = Image.open(a.arkusz).convert("RGB")
    arr = np.asarray(im).astype(int)
    white = arr.min(axis=2) > a.prog
    cols, rows = segmenty(white.mean(axis=0)), segmenty(white.mean(axis=1))
    if len(cols) != 4 or len(rows) != 4:
        raise SystemExit(f"nie widzę siatki 4 × 4: kolumny {cols}, wiersze {rows}")
    os.makedirs(a.wyj, exist_ok=True)
    for i, n in enumerate(a.nazwy):
        r, c = divmod(i, 4)
        (x0, x1), (y0, y1) = cols[c], rows[r]
        k = a.wciecie
        t = im.crop((x0 + k, y0 + k, x1 - k, y1 - k)).resize((1024, 1024), Image.LANCZOS)
        q = np.asarray(t).astype(int)
        rogi = sum(int((b.min(axis=2) > a.prog).mean() > 0.3) for b in (q[:20, :20], q[:20, -20:], q[-20:, :20], q[-20:, -20:]))
        fn = f"{a.prefiks}{i + 1:02d}_{n}.png"
        t.save(os.path.join(a.wyj, fn), optimize=True)
        print(fn, "(białe rogi: %d)" % rogi if rogi else "")
    im.save(os.path.join(a.wyj, f"_arkusz_{a.prefiks}.jpg"), quality=90)


if __name__ == "__main__":
    main()
