#!/usr/bin/env python3
"""Arkusz UI umiejętności i porównania (Paweł 26.11, jedna generacja: assets/raw/SkilleUI/arkusz_v1.png) -> 5 elementów,
od lewej: ramka slotu umiejętności, placeholder kuli ognia, kłódka, strzałka listy, przycisk porównania (lupa).
Białe tło połączone z brzegiem -> przezroczyste (tools/hud_pety_ui.bez_tla), elementy rozdzielane po spójnych obszarach.

Użycie: python tools/skille_ui.py
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

from hud_pety_ui import bez_tla

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/raw/SkilleUI/arkusz_v1.png"
OUT = ROOT / "assets/processed/SkilleUI"
NAZWY = ["SkillSlotRama", "SkillFireball", "SkillKlodka", "SkillStrzalka", "PrzyciskPorownaj"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    a = bez_tla(Image.open(SRC))
    lab, _ = ndimage.label(a[..., 3] > 0)
    el = []
    for i, s in enumerate(ndimage.find_objects(lab), 1):
        h, w = s[0].stop - s[0].start, s[1].stop - s[1].start
        if h * w > 200_000:
            wyc = a[s].copy()
            wyc[..., 3] = np.where(lab[s] == i, wyc[..., 3], 0)
            el.append((s[1].start, Image.fromarray(wyc)))
    el.sort(key=lambda e: e[0])
    assert len(el) == 5, len(el)
    for (_, im), n in zip(el, NAZWY):
        if n == "SkillKlodka":  # zamknięte białe okno pod kabłąkiem (górna połowa) -> przezroczyste
            b = np.array(im)
            h = b.shape[0]
            biale = (b[..., :3].min(axis=2) > 228) & (np.arange(h)[:, None] < h * 0.55)
            lab2, n2 = ndimage.label(biale)
            if n2:
                najw = 1 + int(np.argmax(ndimage.sum(np.ones_like(lab2), lab2, range(1, n2 + 1))))
                b[..., 3] = np.where(lab2 == najw, 0, b[..., 3])  # tylko otwór pod kabłąkiem, połysk zostaje
            im = Image.fromarray(b)
        im.thumbnail((256, 256), Image.LANCZOS)
        im.save(OUT / f"{n}.png", optimize=True)
        print("ok", n, im.size)


if __name__ == "__main__":
    main()
