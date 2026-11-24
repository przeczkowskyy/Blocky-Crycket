#!/usr/bin/env python3
"""Okna UI z jednej generacji (Paweł 24.11): okno kowala, okno jajka, okno mistrza gier — jak okna sklepów
(tools/sklep_okno.py): białe tło połączone z brzegiem -> przezroczyste, pełny obraz + podgląd + kafelki 2 × 2
(po 1024 px szerokości) do Roblox. Napisy, liczby i przyciski z tekstem dokłada GUI natywnie.

Użycie: python tools/okna_ui.py
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
OKNA = {  # nazwa w Roblox: (surowy plik, folder wyjścia)
    "OknoKowala": ("assets/raw/OknoKowala/okno_kowala_v1.png", "assets/processed/OknoKowala"),
    "OknoJajka": ("assets/raw/OknoJajka/okno_jajka_v1.png", "assets/processed/OknoJajka"),
    "OknoMistrzaGier": ("assets/raw/OknoMistrzaGier/okno_mistrza_v1.png", "assets/processed/OknoMistrzaGier"),
}


def bez_tla(im, prog=232):
    a = np.array(im.convert("RGBA"))
    biale = a[..., :3].min(axis=2) > prog
    lab, _ = ndimage.label(biale)
    brzeg = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    tlo = np.isin(lab, list(brzeg))
    a[..., 3] = np.where(tlo, 0, 255).astype(np.uint8)
    out = Image.fromarray(a)
    return out.crop(out.getbbox())


def main():
    for nazwa, (src, dst) in OKNA.items():
        out = ROOT / dst
        out.mkdir(parents=True, exist_ok=True)
        im = bez_tla(Image.open(ROOT / src))
        im.save(out / f"{nazwa}.png", optimize=True)
        im.convert("RGB").resize((1600, round(1600 * im.height / im.width)), Image.LANCZOS).save(
            out / f"{nazwa}_podglad.jpg", quality=88)
        w, h = im.size
        for i, (cx, cy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)], 1):
            kaf = im.crop((cx * w // 2, cy * h // 2, (cx + 1) * w // 2, (cy + 1) * h // 2))
            kaf.resize((1024, round(1024 * kaf.height / kaf.width)), Image.LANCZOS).save(out / f"{nazwa}{i}.png",
                                                                                         optimize=True)
        print("ok", nazwa, im.size, "proporcje", round(w / h, 4))


if __name__ == "__main__":
    main()
