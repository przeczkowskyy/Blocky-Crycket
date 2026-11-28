#!/usr/bin/env python3
"""Napisy podłużnych przycisków HUD w stylu z Figmy (Paweł 26.11 wybrał „figma”).

Źródło projektu: plik Figmy „Blocky & Crycket — napisy przycisków HUD” (drugie konto Pawła, ramka „HUD Napisy”):
Luckiest Guy 120 pt, gradient z góry na dół (żółty FFED6B → FFD640 → F7A81C; EQUIPMENT biały → D9DEEB),
obrys 11 px na zewnątrz, czarny 120A05, cień od dołu 10 px bez rozmycia, brąz 29140 8.
Eksport z Figmy przez MCP nie mieści się w limicie odpowiedzi (48 KB), więc ten skrypt renderuje to samo lokalnie
z tej samej czcionki (assets/fonts/LuckiestGuy-Regular.ttf, licencja Apache 2.0) w 2× rozdzielczości Figmy.

Wynik: assets/processed/HudPodluzne/HudLabel<Nazwa>.png + podglad_z_napisami.jpg (napisy na przyciskach).
Użycie: python tools/hud_napisy_figma.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/processed/HudPodluzne"
FONT = ROOT / "assets/fonts/LuckiestGuy-Regular.ttf"
SKALA = 2  # względem Figmy (120 pt) -> litery ok. 240 px
ROZMIAR, OBRYS, CIEN = 120 * SKALA, 11 * SKALA, 10 * SKALA
CZARNY, BRAZ = (18, 10, 5), (41, 20, 8)
ZOLTY = [(0, (255, 237, 107)), (0.55, (255, 214, 64)), (1, (247, 168, 28))]
BIALY = [(0, (255, 255, 255)), (1, (217, 222, 235))]
NAZWY = ["Teleport", "Equipment", "Pets", "Index", "Shop"]
POLE = (0.35, 0.24, 0.615, 0.52)  # pole napisu na przycisku — to samo w tools/hud_pety_build_gui.py


def gradient(h, stopy):
    t = np.linspace(0, 1, h)[:, None]
    kan = []
    for c in range(3):
        kan.append(np.interp(t, [s[0] for s in stopy], [s[1][c] for s in stopy]))
    return np.concatenate(kan, axis=1)  # h × 3


def napis(tekst, stopy):
    f = ImageFont.truetype(str(FONT), ROZMIAR)
    l, t, r, b = f.getbbox(tekst)
    marg = OBRYS + 4
    w, h = r - l + 2 * marg, b - t + 2 * marg + CIEN
    poz = (marg - l, marg - t)
    litery = Image.new("L", (w, h), 0)
    ImageDraw.Draw(litery).text(poz, tekst, font=f, fill=255)
    z_obrysem = Image.new("L", (w, h), 0)
    ImageDraw.Draw(z_obrysem).text(poz, tekst, font=f, fill=255, stroke_width=OBRYS)
    # cień od dołu: kształt z obrysem przesunięty w dół (jak DROP_SHADOW y=10, bez rozmycia)
    cien = Image.new("L", (w, h), 0)
    cien.paste(z_obrysem, (0, CIEN))
    wynik = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    wynik.paste(Image.new("RGBA", (w, h), BRAZ + (255,)), (0, 0), cien)
    wynik.paste(Image.new("RGBA", (w, h), CZARNY + (255,)), (0, 0), z_obrysem)
    # gradient liczony na wysokość liter (jak w Figmie: na ramkę tekstu)
    g = gradient(b - t, stopy)
    pas = np.zeros((h, w, 3), np.uint8)
    pas[marg:marg + (b - t)] = g[:, None, :].astype(np.uint8)
    pas[:marg] = g[0].astype(np.uint8)
    pas[marg + (b - t):] = g[-1].astype(np.uint8)
    wynik.paste(Image.fromarray(pas, "RGB").convert("RGBA"), (0, 0), litery)
    return wynik.crop(wynik.getbbox())


def main():
    podglady = []
    for n in NAZWY:
        im = napis(n.upper(), BIALY if n == "Equipment" else ZOLTY)
        im.save(OUT / f"HudLabel{n}.png", optimize=True)
        print("ok", f"HudLabel{n}", im.size, "proporcje", round(im.width / im.height, 3))
        b = Image.open(OUT / f"HudWide{n}.png").convert("RGBA")
        x, y, w, h = POLE[0] * b.width, POLE[1] * b.height, POLE[2] * b.width, POLE[3] * b.height
        k = min(w / im.width, h / im.height)
        m = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        b.alpha_composite(m, (round(x + (w - m.width) / 2), round(y + (h - m.height) / 2)))
        podglady.append(b)
    odstep = 28
    tlo = Image.new("RGBA", (podglady[0].width + 120, sum(p.height for p in podglady) + 6 * odstep), (58, 92, 64, 255))
    for i, p in enumerate(podglady):
        tlo.alpha_composite(p, (60, odstep + i * (p.height + odstep)))
    tlo = tlo.convert("RGB")
    tlo.thumbnail((700, 1400))
    tlo.save(OUT / "podglad_z_napisami.jpg", quality=90)
    print("ok podglad", tlo.size)


if __name__ == "__main__":
    main()
