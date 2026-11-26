#!/usr/bin/env python3
"""Arkusz interfejsu stołu mistrza gier (Paweł 25.11, jedna generacja: assets/raw/MistrzGierUI/arkusz_v1.png,
Higgsfield job 012c7adf) -> osobne elementy w assets/processed/MistrzGierUI/: tabliczka tytułu, przycisk ROLL
z kostką, przycisk LEAVE, plakietka ceny z gniazdem na ikonę waluty, wstęga komunikatu, gwiazda nagrody
(druga, krótsza wstęga z arkusza zostaje jako zapas). Makieta ekranu: build/mistrz_gier_ui_makieta.jpg
(tło: build/mistrz_tlo.jpg — zrzut stołu z gry bez interfejsu).

Użycie: python tools/mistrz_gier_ui.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

import hud_pety_ui as H

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/raw/MistrzGierUI/arkusz_v1.png"
OUT = ROOT / "assets/processed/MistrzGierUI"
# układ nakładki na ekranie 1366 × 670 (ułamki ekranu: x, y, szer, wys) — te same liczby bierze skrypt gry
UKLAD = {
    "MistrzTytul": (0.018, 0.03, 0.30, None),
    "MistrzLeave": (0.845, 0.125, 0.135, None),
    "MistrzCena": (0.765, 0.545, 0.215, None),
    "MistrzRoll": (0.755, 0.675, 0.225, None),
    "MistrzWstega": (0.02, 0.80, 0.33, None),
}


def zapisz(im, nazwa, szer):
    if im.width > szer:
        im = im.resize((szer, round(szer * im.height / im.width)), Image.LANCZOS)
    im.save(OUT / f"{nazwa}.png", optimize=True)
    print("ok", nazwa, im.size, "proporcje", round(im.width / im.height, 4))
    return im


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    zrodlo = Image.open(SRC)
    W, Hh = zrodlo.size
    a = H.bez_tla(zrodlo)
    lab, _ = ndimage.label(a[..., 3] > 0)
    el = []
    for i, s in enumerate(ndimage.find_objects(lab), 1):
        h, w = s[0].stop - s[0].start, s[1].stop - s[1].start
        if h * w > 60_000:
            wyc = a[s].copy()
            wyc[..., 3] = np.where(lab[s] == i, wyc[..., 3], 0)
            el.append(((s[1].start + w / 2) / W, (s[0].start + h / 2) / Hh, Image.fromarray(wyc)))
    assert len(el) == 7, [(round(x, 2), round(y, 2)) for x, y, _ in el]
    gora = sorted([e for e in el if e[1] < 0.33], key=lambda e: e[0])
    srodek = sorted([e for e in el if 0.33 <= e[1] < 0.64], key=lambda e: e[0])
    dol = sorted([e for e in el if e[1] >= 0.64], key=lambda e: e[0])
    assert (len(gora), len(srodek), len(dol)) == (3, 2, 2), (len(gora), len(srodek), len(dol))
    cz = {
        "MistrzTytul": zapisz(gora[0][2], "MistrzTytul", 1024),
        "MistrzRoll": zapisz(gora[1][2], "MistrzRoll", 768),
        "MistrzLeave": zapisz(gora[2][2], "MistrzLeave", 512),
        "MistrzCena": zapisz(srodek[0][2], "MistrzCena", 768),
        "MistrzWstegaKrotka": zapisz(srodek[1][2], "MistrzWstegaKrotka", 768),
        "MistrzWstega": zapisz(dol[0][2], "MistrzWstega", 1024),
        "MistrzGwiazda": zapisz(dol[1][2], "MistrzGwiazda", 384),
    }

    # --- makieta na zrzucie z gry
    tlo_plik = ROOT / "build/mistrz_tlo.jpg"
    if not tlo_plik.exists():
        return
    SK = 2
    tlo = Image.open(tlo_plik).convert("RGBA")
    tlo = tlo.resize((tlo.width * SK, tlo.height * SK), Image.LANCZOS)
    EW, EH = tlo.size
    d = ImageDraw.Draw(tlo)
    try:
        font = lambda r: ImageFont.truetype(str(ROOT / "assets/fonts/LuckiestGuy-Regular.ttf"), r)
        font(20)
    except OSError:
        font = lambda r: ImageFont.truetype("C:/Windows/Fonts/impact.ttf", r)

    def napis(tekst, srodek_xy, rozmiar, kolor, obrys=5):
        f = font(rozmiar * SK)
        d.text(srodek_xy, tekst, font=f, fill=kolor, anchor="mm", stroke_width=obrys * SK // 2, stroke_fill=(26, 20, 16))

    pola = {}
    for nazwa, (x, y, w, _) in UKLAD.items():
        im = cz[nazwa]
        sw = round(w * EW)
        m = im.resize((sw, round(sw * im.height / im.width)), Image.LANCZOS)
        px, py = round(x * EW), round(y * EH)
        tlo.alpha_composite(m, (px, py))
        pola[nazwa] = (px, py, m.width, m.height)
    x, y, w, h = pola["MistrzTytul"]
    napis("GAME MASTER · BOARD 1", (x + w / 2, y + h / 2), 24, (252, 227, 176))
    x, y, w, h = pola["MistrzLeave"]
    napis("LEAVE", (x + w * 0.62, y + h / 2), 22, (255, 255, 255))
    x, y, w, h = pola["MistrzRoll"]
    napis("ROLL", (x + w * 0.64, y + h / 2), 44, (255, 255, 255), 7)
    x, y, w, h = pola["MistrzCena"]
    napis("FREE ROLL", (x + w * 0.62, y + h / 2), 22, (255, 214, 90))
    ryba = ROOT / "assets/processed/GoldFish.png"
    if ryba.exists():
        r = Image.open(ryba).convert("RGBA")
        bok = round(h * 0.5)
        r = r.resize((bok, round(bok * r.height / r.width)), Image.LANCZOS)
        tlo.alpha_composite(r, (round(x + h * 0.52 - r.width / 2), round(y + h / 2 - r.height / 2)))
    x, y, w, h = pola["MistrzWstega"]
    napis("BOARD 1 DONE! NEW BOARD", (x + w / 2, y + h * 0.42), 17, (74, 46, 26), 0)
    # nagroda nad polem pionka
    g = cz["MistrzGwiazda"]
    bok = round(0.085 * EW)
    g = g.resize((bok, round(bok * g.height / g.width)), Image.LANCZOS)
    gx, gy = round(0.521 * EW - bok / 2), round(0.60 * EH)
    tlo.alpha_composite(g, (gx, gy))
    napis("+34", (gx + bok / 2, gy + g.height / 2), 24, (255, 255, 255))
    tlo.convert("RGB").resize((EW // SK * 1, EH // SK * 1), Image.LANCZOS).save(ROOT / "build/mistrz_gier_ui_makieta.jpg", quality=90)
    print("ok makieta", ROOT / "build/mistrz_gier_ui_makieta.jpg")


if __name__ == "__main__":
    main()
