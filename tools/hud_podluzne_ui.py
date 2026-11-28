#!/usr/bin/env python3
"""Arkusz podłużnych przycisków HUD (Paweł 25.11, jedna generacja: assets/raw/HudPodluzne/arkusz_v1.png) -> pięć
osobnych przycisków do Roblox: ikona po lewej, puste miejsce na napis po prawej (napis natywnie w Roblox).
Białe tło połączone z brzegiem -> przezroczyste; przyciski rozdzielane po spójnych obszarach, od góry do dołu.
Wszystkie pięć dostają ten sam rozmiar pliku (wspólne proporcje), żeby w kolumnie HUD były identyczne.

Użycie: python tools/hud_podluzne_ui.py            (pliki + podgląd z napisami)
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

from hud_pety_ui import bez_tla

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/raw/HudPodluzne/arkusz_v1.png"
OUT = ROOT / "assets/processed/HudPodluzne"
NAZWY = ["Teleport", "Equipment", "Pets", "Index", "Shop"]  # kolejność na arkuszu, od góry
SZER = 1024  # szerokość pliku do Roblox
# Pole napisu jako ułamek przycisku (x, y, szer, wys) — na prawo od ikony; używa go też tools/hud_pety_build_gui.py
POLE_NAPISU = (0.34, 0.2, 0.6, 0.6)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    a = bez_tla(Image.open(SRC))
    lab, _ = ndimage.label(a[..., 3] > 0)
    el = []
    for i, s in enumerate(ndimage.find_objects(lab), 1):
        h, w = s[0].stop - s[0].start, s[1].stop - s[1].start
        if h * w > 150_000:
            wyc = a[s].copy()
            wyc[..., 3] = np.where(lab[s] == i, wyc[..., 3], 0)
            el.append((s[0].start, w, h, Image.fromarray(wyc)))
    el.sort(key=lambda e: e[0])
    assert len(el) == 5, [e[:3] for e in el]
    prop = sum(e[1] / e[2] for e in el) / 5  # wspólne proporcje: różnice między przyciskami to 1–2 px
    wys = round(SZER / prop)
    gotowe = []
    for (_, w, h, im), n in zip(el, NAZWY):
        im = im.resize((SZER, wys), Image.LANCZOS)
        im.save(OUT / f"HudWide{n}.png", optimize=True)
        print("ok", f"HudWide{n}", im.size, "z", (w, h), "proporcje", round(w / h, 4))
        gotowe.append(im)
    print("proporcje wspólne", round(prop, 4))
    podglad(gotowe, wys)


def podglad(przyciski, wys):
    """Podgląd dla człowieka: kolumna na ciemnym tle z napisami tak, jak wstawi je Roblox (Luckiest Guy, obrys)."""
    font = None
    for p in (ROOT / "assets/fonts/LuckiestGuy-Regular.ttf", Path("C:/Windows/Fonts/LuckiestGuy-Regular.ttf"),
              Path("C:/Windows/Fonts/impact.ttf")):
        if p.exists():
            font = p
            break
    odstep = 28
    tlo = Image.new("RGBA", (SZER + 120, 5 * wys + 6 * odstep), (58, 92, 64, 255))
    for i, (im, n) in enumerate(zip(przyciski, NAZWY)):
        im = im.copy()
        d = ImageDraw.Draw(im)
        x, y, w, h = (POLE_NAPISU[0] * SZER, POLE_NAPISU[1] * wys, POLE_NAPISU[2] * SZER, POLE_NAPISU[3] * wys)
        rozm = int(h * 0.78)
        while True:
            f = ImageFont.truetype(str(font), rozm) if font else ImageFont.load_default()
            b = d.textbbox((0, 0), n.upper(), font=f, stroke_width=max(2, rozm // 12))
            if not font or b[2] - b[0] <= w or rozm < 20:
                break
            rozm -= 4
        tx, ty = x + (w - (b[2] - b[0])) / 2 - b[0], y + (h - (b[3] - b[1])) / 2 - b[1]
        d.text((tx, ty + rozm // 14), n.upper(), font=f, fill=(40, 24, 10, 255), stroke_width=max(2, rozm // 12),
               stroke_fill=(20, 12, 6, 255))
        d.text((tx, ty), n.upper(), font=f, fill=(255, 214, 64, 255), stroke_width=max(2, rozm // 12),
               stroke_fill=(20, 12, 6, 255))
        tlo.alpha_composite(im, (60, odstep + i * (wys + odstep)))
    tlo = tlo.convert("RGB")
    tlo.thumbnail((700, 1400))
    tlo.save(OUT / "podglad_z_napisami.jpg", quality=88)
    print("ok podglad", tlo.size, "czcionka", font.name if font else "domyślna")


if __name__ == "__main__":
    main()
