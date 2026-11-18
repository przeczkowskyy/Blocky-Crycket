#!/usr/bin/env python3
"""Ikony broni startowych z arkusza Pawła (2026-11-18): górny rząd = ikony do ekwipunku.

Arkusz ma narysowaną szachownicę (JPG, nie prawdziwą przezroczystość), więc tło wycinamy wypełnieniem od krawędzi:
piksele szare/białe (bez nasycenia) połączone z brzegiem kadru. Gruby czarny obrys przedmiotu zatrzymuje
wypełnienie, więc szary kamień w środku zostaje. Potem dwa przejścia zdejmują szarą obwódkę po kompresji JPG,
przycięcie do przedmiotu, margines 4%, kwadrat 512 px.

    python tools/bronie_startowe_ikony.py          # assets/raw/BronieStartowe_arkusz.jpg -> assets/processed/Weapon*.png
"""
from collections import deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets/raw/BronieStartowe_arkusz.jpg"
# (nazwa assetu, kadr górnego rzędu w pikselach arkusza 2048 × 2048)
IKONY = [("WeaponClub", (60, 120, 700, 640)), ("WeaponStaff", (700, 120, 1340, 640)),
         ("WeaponSlingshot", (1340, 120, 1990, 640))]
SIZE, PAD = 512, 0.04


def tlo(px):
    r, g, b = px[:3]
    return max(r, g, b) - min(r, g, b) < 24 and min(r, g, b) > 135


def wytnij(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    w, h = im.size
    pix = im.load()
    bg = [[False] * w for _ in range(h)]
    q = deque()
    for x in range(w):
        q.extend(((x, 0), (x, h - 1)))
    for y in range(h):
        q.extend(((0, y), (w - 1, y)))
    while q:
        x, y = q.popleft()
        if bg[y][x] or not tlo(pix[x, y]):
            continue
        bg[y][x] = True
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not bg[ny][nx]:
                q.append((nx, ny))
    # zamknięte pola szachownicy (np. między gumą a ramieniem procy): spójny obszar pikseli „tła”, w którym prawie
    # wszystko ma dokładnie jeden z dwóch odcieni szachownicy (ok. 160 i 226) — kamień ma płynne cienie, więc zostaje
    widziane = [[False] * w for _ in range(h)]
    for sy in range(h):
        for sx in range(w):
            if bg[sy][sx] or widziane[sy][sx] or not tlo(pix[sx, sy]):
                continue
            pole, q2 = [], deque([(sx, sy)])
            widziane[sy][sx] = True
            while q2:
                x, y = q2.popleft()
                pole.append((x, y))
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < w and 0 <= ny < h and not widziane[ny][nx] and not bg[ny][nx] and tlo(pix[nx, ny]):
                        widziane[ny][nx] = True
                        q2.append((nx, ny))
            szach = sum(1 for x, y in pole if min(abs(pix[x, y][0] - 160), abs(pix[x, y][0] - 226)) <= 9)
            if len(pole) > 150 and szach > 0.8 * len(pole):
                for x, y in pole:
                    bg[y][x] = True
    # obwódka JPG: szare piksele przy tle (jaśniejsze niż obrys) też są tłem
    for _ in range(2):
        nowe = []
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                if bg[y][x]:
                    continue
                r, g, b, _a = pix[x, y]
                if max(r, g, b) - min(r, g, b) < 30 and min(r, g, b) > 95 and (
                        bg[y][x - 1] or bg[y][x + 1] or bg[y - 1][x] or bg[y + 1][x]):
                    nowe.append((x, y))
        for x, y in nowe:
            bg[y][x] = True
    for y in range(h):
        for x in range(w):
            if bg[y][x]:
                pix[x, y] = (0, 0, 0, 0)
    return im


def kwadrat(im: Image.Image) -> Image.Image:
    box = im.getbbox()
    im = im.crop(box)
    bok = max(im.size)
    bok = int(bok * (1 + 2 * PAD))
    out = Image.new("RGBA", (bok, bok), (0, 0, 0, 0))
    out.paste(im, ((bok - im.width) // 2, (bok - im.height) // 2))
    return out.resize((SIZE, SIZE), Image.LANCZOS)


def main():
    arkusz = Image.open(SRC)
    dst = ROOT / "assets/processed"
    for nazwa, kadr in IKONY:
        ik = kwadrat(wytnij(arkusz.crop(kadr)))
        ik.save(dst / f"{nazwa}.png")
        print(nazwa, "->", dst / f"{nazwa}.png", ik.size)


if __name__ == "__main__":
    main()
