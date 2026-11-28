#!/usr/bin/env python3
"""Zestaw elementów okienka podpowiedzi interakcji („E · Zagraj”) z jednej generacji Higgsfield (Paweł 28.11: „okna
interakcji pod nasz kreskowy styl, z lekką ciemną obwódką”; nano_banana_2_1, 1 wariant, ref KeyArt; job 382d9be8):
tnie arkusz assets/raw/PodpowiedzE/v1_1.png na pięć elementów, wycina tło i składa makietę okienka.
Litery klawisza i napisy są w grze natywne — elementy są puste.

    python tools/podpowiedz_e.py     # -> assets/processed/PodpowiedzE/<Nazwa>.png + build/podpowiedz_e_makieta.jpg
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARKUSZ = os.path.join(ROOT, "assets", "raw", "PodpowiedzE", "v1_1.png")
WYJ = os.path.join(ROOT, "assets", "processed", "PodpowiedzE")
K = 2752 / 1100  # współrzędne zmierzone na podglądzie 1100 px
ELEMENTY = [  # nazwa, (x0, y0, x1, y1) na podglądzie, do czego
    ("PodpowiedzTabliczka", (38, 46, 646, 288), "tabliczka akcji (9-slice)"),
    ("PodpowiedzPlakietka", (676, 94, 1058, 238), "plakietka z nazwą obiektu (9-slice)"),
    ("PodpowiedzKlawisz", (50, 316, 296, 562), "klawisz — litera natywna"),
    ("PodpowiedzDotyk", (338, 316, 604, 566), "przycisk dotyku na telefonie"),
    ("PodpowiedzPierscien", (738, 300, 1006, 572), "pierścień przytrzymania"),
]
CZARNY = (46, 32, 34)


def el(nazwa, wys):
    im = Image.open(os.path.join(WYJ, nazwa + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((round(im.width * wys / im.height), wys), Image.LANCZOS)


def font(r):
    return ImageFont.truetype(os.path.join(ROOT, "assets", "fonts", "LuckiestGuy-Regular.ttf"), r)


def makieta():
    tlo = Image.new("RGBA", (1100, 420), (96, 150, 104, 255))
    d = ImageDraw.Draw(tlo)
    for i, (obiekt, akcja, dotyk) in enumerate((("GAME MASTER", "PLAY", False), ("BLACKSMITH", "FORGE", True))):
        x0 = 60 + i * 540
        tab = el("PodpowiedzTabliczka", 150)
        tab = tab.resize((430, 150), Image.LANCZOS)
        plak = el("PodpowiedzPlakietka", 70).resize((290, 70), Image.LANCZOS)
        tlo.alpha_composite(tab, (x0, 190))
        tlo.alpha_composite(plak, (x0 + 70, 130))
        d.text((x0 + 215, 166), obiekt, font=font(30), fill=(252, 236, 200), anchor="mm")
        k = el("PodpowiedzDotyk" if dotyk else "PodpowiedzKlawisz", 104)
        tlo.alpha_composite(k, (x0 + 26, 213))
        if not dotyk:
            d.text((x0 + 26 + k.width / 2, 213 + 48), "E", font=font(58), fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=CZARNY)
        d.text((x0 + 160, 268), akcja, font=font(56), fill=CZARNY, anchor="lm")
    d.text((30, 40), "OKIENKO PODPOWIEDZI — makieta (klawiatura / telefon)", font=font(26), fill=(255, 255, 255), anchor="lm", stroke_width=3, stroke_fill=CZARNY)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    tlo.convert("RGB").save(os.path.join(ROOT, "build", "podpowiedz_e_makieta.jpg"), quality=88)


def main():
    os.makedirs(WYJ, exist_ok=True)
    im = Image.open(ARKUSZ).convert("RGB")
    for nazwa, (x0, y0, x1, y1), _ in ELEMENTY:
        surowy = os.path.join(os.path.dirname(ARKUSZ), "v1_1_%s.png" % nazwa)
        im.crop(tuple(round(v * K) for v in (x0, y0, x1, y1))).save(surowy)
        cel = os.path.join(WYJ, nazwa + ".png")
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "process_image.py"), surowy, cel, "--category", "button"],
                       capture_output=True)
        print(nazwa, Image.open(cel).size if os.path.exists(cel) else "BŁĄD")
    makieta()


if __name__ == "__main__":
    main()
