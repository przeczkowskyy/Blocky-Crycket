#!/usr/bin/env python3
"""Arkusz okna Index i awansu (Paweł 26.11, jedna generacja: assets/raw/OknoIndeksu/arkusz_v1.png) -> elementy:
okno (pełny obraz + kafelki 2 × 2 do Roblox), zakładka jasna i ciemna, złota wstęga awansu, wybuch światła.
Okno, zakładki i wstęga: białe tło połączone z brzegiem -> przezroczyste (tools/hud_pety_ui.bez_tla).
Wybuch światła: miękki blask na białym, więc przezroczystość liczona z „bieli” (biel -> 0, kolor -> pełny).
Wypisuje też ułamki pola pergaminu w oknie (do tools/okno_indeksu_build_gui.py).

Użycie: python tools/okno_indeksu_ui.py
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

from hud_pety_ui import bez_tla

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/raw/OknoIndeksu/arkusz_v1.png"
OUT = ROOT / "assets/processed/OknoIndeksu"
# obszary na arkuszu 5504 × 3072 (x0, y0, x1, y1) — z podglądu 1/4
OBSZARY = {
    "Okno": (60, 100, 3220, 2960),
    "ZakladkaJasna": (3500, 180, 5220, 700),
    "ZakladkaCiemna": (3500, 790, 5220, 1300),
    "AwansWstega": (3340, 1380, 5380, 2090),
    "AwansBlask": (3780, 1960, 4920, 3060),
}


def przytnij(a):
    ys, xs = np.where(a[..., 3] > 8)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def blask(a):
    """Przezroczystość z bieli (biel -> 0, nasycony kolor -> pełny), a biały środek wybuchu dostaje własny miękki,
    biały blask od środka (inaczej środek byłby dziurą)."""
    rgb = a[..., :3].astype(np.float32) / 255
    alfa = np.clip((1 - rgb.min(axis=2)) * 1.6, 0, 1)
    kol = np.where(alfa[..., None] > 0.01, (rgb - (1 - alfa[..., None])) / np.maximum(alfa[..., None], 0.01), 0)
    kol = np.clip(kol, 0, 1)
    h, w = alfa.shape
    ys, xs = np.where(alfa > 0.3)
    cy, cx = ys.mean(), xs.mean()
    r = np.hypot(*np.mgrid[0:h, 0:w] - np.array([cy, cx])[:, None, None])
    rdz = np.clip(1 - r / (0.2 * min(h, w)), 0, 1) ** 1.3  # rdzeń: 1 w środku, 0 przy 20% rozmiaru
    nowa = np.maximum(alfa, rdz) * (r < 0.5 * min(h, w))  # poza kołem wybuchu nic (końce wstęgi nad nim)
    udzial = np.where(nowa > 0, rdz / np.maximum(nowa, 1e-3), 0)[..., None]
    kol = kol * (1 - udzial) + np.array([1.0, 0.98, 0.85]) * udzial
    return np.dstack([kol * 255, nowa * 255]).astype(np.uint8)


def zapisz(a, nazwa, szer=None):
    im = Image.fromarray(a)
    if szer and im.width > szer:
        im = im.resize((szer, round(szer * im.height / im.width)), Image.LANCZOS)
    im.save(OUT / f"{nazwa}.png", optimize=True)
    print("ok", nazwa, im.size, "proporcje", round(im.width / im.height, 4))
    return im


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ark = np.array(Image.open(SRC).convert("RGBA"))
    for nazwa, (x0, y0, x1, y1) in OBSZARY.items():
        kaw = ark[y0:y1, x0:x1].copy()
        if nazwa == "AwansBlask":
            a = przytnij(blask(kaw))
            zapisz(a, nazwa, 512)
            continue
        a = bez_tla(Image.fromarray(kaw))
        if nazwa == "AwansWstega":  # gwiazdki obok wstęgi zostają, promienie wybuchu od dołu (zaczynają się niżej) — nie
            lab, n = ndimage.label(a[..., 3] > 0)
            for i, sl in enumerate(ndimage.find_objects(lab), 1):
                if sl[0].start > 540:
                    a[..., 3] = np.where(lab == i, 0, a[..., 3])
        else:  # reszta: tylko największy element
            lab, n = ndimage.label(a[..., 3] > 0)
            if n > 1:
                najw = 1 + int(np.argmax(ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))))
                a[..., 3] = np.where(lab == najw, a[..., 3], 0)
        a = przytnij(a)
        if nazwa == "Okno":
            im = zapisz(a, nazwa, 2048)
            w, h = im.size
            pol = [(0, 0), (1, 0), (0, 1), (1, 1)]
            for i, (cx, cy) in enumerate(pol, 1):
                im.crop((cx * w // 2, cy * h // 2, (cx + 1) * w // 2, (cy + 1) * h // 2)).save(OUT / f"OknoIndeksu{i}.png", optimize=True)
            # pole pergaminu: największy jasny, ciepły obszar
            b = np.array(im).astype(int)
            jasne = (b[..., 0] > 225) & (b[..., 1] > 200) & (b[..., 2] > 150) & (b[..., 3] > 200)
            lab, n = ndimage.label(jasne)
            najw = 1 + int(np.argmax(ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))))
            ys, xs = np.where(lab == najw)
            print("pergamin (x, y, szer, wys):", round(xs.min() / w, 4), round(ys.min() / h, 4),
                  round((xs.max() - xs.min()) / w, 4), round((ys.max() - ys.min()) / h, 4))
            # tabliczka tytułu i X: górny pas
            print("okno w*h", w, h)
        else:
            zapisz(a, nazwa, 640)
    podglad = Image.new("RGBA", (1400, 900), (58, 92, 64, 255))
    x = 10
    for n in ["Okno", "ZakladkaJasna", "ZakladkaCiemna", "AwansWstega", "AwansBlask"]:
        im = Image.open(OUT / f"{n}.png")
        im.thumbnail((700 if n == "Okno" else 330, 640))
        podglad.alpha_composite(im, (x, 10) if n == "Okno" else (x, 10 + 160 * ["ZakladkaJasna", "ZakladkaCiemna", "AwansWstega", "AwansBlask"].index(n)))
        if n == "Okno":
            x = 740
    podglad.convert("RGB").save(OUT / "podglad.jpg", quality=88)


if __name__ == "__main__":
    main()
