#!/usr/bin/env python3
"""Makieta ekranu walki i ekranu zwycięstwa z elementów assets/processed/WalkaUI (Paweł 28.11: „UI walk i ekran
zwycięstwa w naszym stylu, paski życia natywne, ramki ras jako portrety”). Sam obraz poglądowy — nic nie trafia do gry.
Tło i postacie to szkic; paski życia, napisy i liczby są rysowane tak, jak będą natywne w Roblox (Frame + TextLabel).

    python tools/walka_ui_makieta.py        # -> build/walka_makieta.jpg
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "assets", "processed")
W, H = 1600, 900
CZARNY = (34, 26, 40)


def el(nazwa, szer=None, wys=None, folder="WalkaUI"):
    im = Image.open(os.path.join(P, folder, nazwa + ".png") if folder else os.path.join(P, nazwa + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    if szer and wys:
        return im.resize((szer, wys), Image.LANCZOS)
    if szer:
        return im.resize((szer, round(im.height * szer / im.width)), Image.LANCZOS)
    if wys:
        return im.resize((round(im.width * wys / im.height), wys), Image.LANCZOS)
    return im


def font(r):
    return ImageFont.truetype(os.path.join(ROOT, "assets", "fonts", "LuckiestGuy-Regular.ttf"), r)


def napis(d, xy, tekst, r, kolor=(255, 255, 255), kotwica="mm", obrys=None):
    d.text(xy, tekst, font=font(r), fill=kolor, anchor=kotwica, stroke_width=obrys if obrys is not None else max(2, r // 9), stroke_fill=CZARNY)


def wklej(tlo, im, x, y, kotwica="lt"):
    if kotwica == "mm":
        x, y = x - im.width // 2, y - im.height // 2
    tlo.alpha_composite(im, (round(x), round(y)))


def pasek(d, x, y, szer, wys, ile, kolor, tekst):
    d.rounded_rectangle((x, y, x + szer, y + wys), wys // 2, fill=CZARNY)
    d.rounded_rectangle((x + 5, y + 5, x + szer - 5, y + wys - 5), wys // 2 - 4, fill=(74, 62, 84))
    d.rounded_rectangle((x + 5, y + 5, x + 5 + round((szer - 10) * ile), y + wys - 5), wys // 2 - 4, fill=kolor)
    d.rounded_rectangle((x + 12, y + 8, x + 5 + round((szer - 10) * ile) - 8, y + 14), 3, fill=tuple(min(255, c + 60) for c in kolor))
    napis(d, (x + szer / 2, y + wys / 2 + 1), tekst, round(wys * 0.56))


def tlo_areny():
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line((0, y, W, y), fill=(round(58 + 40 * t), round(120 + 50 * t), round(150 - 60 * t), 255))
    d.ellipse((-200, 560, W + 200, 1300), fill=(96, 158, 88, 255))
    d.ellipse((330, 640, 1270, 860), fill=(120, 182, 100, 255))
    for x, y, s in ((120, 430, 150), (1380, 410, 170), (760, 380, 110)):
        d.rectangle((x - s * 0.08, y, x + s * 0.08, y + s * 1.2), fill=(92, 66, 50, 255))
        d.polygon(((x - s * 0.6, y + s * 0.3), (x, y - s * 0.9), (x + s * 0.6, y + s * 0.3)), fill=(60, 118, 82, 255))
    return im


def postac(d, x, y, kolor, podpis):
    d.ellipse((x - 95, y + 150, x + 95, y + 190), fill=(40, 70, 50))
    d.rounded_rectangle((x - 70, y - 10, x + 70, y + 170), 40, fill=kolor, outline=CZARNY, width=6)
    d.ellipse((x - 85, y - 150, x + 85, y + 20), fill=kolor, outline=CZARNY, width=6)
    napis(d, (x, y + 222), podpis, 22, (255, 244, 200))


def ekran_walki():
    im = tlo_areny()
    d = ImageDraw.Draw(im)
    postac(d, 520, 440, (150, 196, 96), "kot gracza (model wybranej rasy)")
    postac(d, 1080, 440, (150, 110, 190), "potwór")
    napis(d, (1010, 330), "-18", 64, (255, 92, 80))
    # gracz: portret w ramce rasy, nazwa, natywny pasek życia
    wklej(im, el("PortraitGoblin_v2", wys=150, folder="RacePortraits"), 36, 30)
    napis(d, (204, 60), "GOBLIN MAGE", 34, kotwica="lm")
    napis(d, (204, 96), "LV 3", 24, (255, 214, 92), "lm")
    pasek(d, 200, 118, 420, 46, 0.7, (98, 204, 84), "84 / 120")
    # przeciwnik lustrzanie
    wklej(im, el("WalkaKafelSzary", wys=150), W - 36 - 150, 30)
    napis(d, (W - 36 - 75, 106), "?", 80)
    napis(d, (W - 204, 60), "FOREST SLIME", 34, kotwica="rm")
    napis(d, (W - 204, 96), "LV 2 · RARE", 24, (150, 214, 255), "rm")
    pasek(d, W - 200 - 420, 118, 420, 46, 0.42, (232, 84, 78), "38 / 90")
    wklej(im, el("WalkaVs", wys=150), W // 2, 100, "mm")
    napis(d, (W // 2, 102), "VS", 58)
    napis(d, (W // 2, 198), "TURN 3", 30, (255, 244, 200))
    # tempo, dźwięk, pomiń
    x = W - 36
    szer = el("WalkaBtnSzerokiZolty", wys=96)
    x -= szer.width
    wklej(im, szer, x, H - 132)
    napis(d, (x + szer.width / 2, H - 132 + 44), "SKIP", 40)
    for nazwa, tekst in (("WalkaBtnDzwiek", ""), ("WalkaBtnSzary", "×4"), ("WalkaBtnZolty", "×2"), ("WalkaBtnSzary", "×1")):
        b = el(nazwa, wys=96)
        x -= b.width + 14
        wklej(im, b, x, H - 132)
        if tekst:
            napis(d, (x + b.width / 2, H - 132 + 44), tekst, 40)
    napis(d, (36, H - 40), "EKRAN WALKI — makieta", 26, (255, 255, 255), "lm")
    return im


def ekran_zwyciestwa():
    im = tlo_areny()
    im.alpha_composite(Image.new("RGBA", (W, H), (20, 14, 30, 150)))
    d = ImageDraw.Draw(im)
    okno = el("WalkaOkno", 900, 520)
    wklej(im, okno, W // 2, 480, "mm")
    baner = el("WalkaBaner", szer=760)
    wklej(im, baner, W // 2, 210, "mm")
    napis(d, (W // 2, 204), "VICTORY!", 76)
    napis(d, (W // 2, 330), "REWARDS", 36, (255, 232, 150))
    nagrody = (("GoldFish", "+120", None), ("Gem", "+2", None), (None, "+45", "XP"), (None, "", "—"))
    k = 150
    x0 = W // 2 - (4 * k + 3 * 24) // 2
    for i, (ikona, ile, znak) in enumerate(nagrody):
        x = x0 + i * (k + 24)
        wklej(im, el("WalkaKafelSzary" if znak == "—" else "WalkaKafel", k, k), x, 370)
        if ikona:
            wklej(im, el(ikona, wys=84, folder=None), x + k // 2, 370 + 62, "mm")
        elif znak:
            napis(d, (x + k / 2, 370 + 64), znak, 50, (150, 214, 255) if znak == "XP" else (200, 200, 210))
        if ile:
            napis(d, (x + k / 2, 370 + k - 28), ile, 32)
    b = el("WalkaBtnSzerokiZolty", wys=104)
    wklej(im, b, W // 2 - b.width - 14, 580)
    napis(d, (W // 2 - b.width / 2 - 14, 580 + 48), "NEXT", 42)
    c = el("WalkaBtnSzerokiCzerwony", wys=104)
    wklej(im, c, W // 2 + 14, 580)
    napis(d, (W // 2 + 14 + c.width / 2, 580 + 48), "CLOSE", 42)
    napis(d, (36, H - 40), "EKRAN ZWYCIĘSTWA — makieta", 26, (255, 255, 255), "lm")
    return im


def main():
    a, b = ekran_walki(), ekran_zwyciestwa()
    plansza = Image.new("RGB", (W, 2 * H + 12), (20, 14, 30))
    plansza.paste(a.convert("RGB"), (0, 0))
    plansza.paste(b.convert("RGB"), (0, H + 12))
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    cel = os.path.join(ROOT, "build", "walka_makieta.jpg")
    plansza.save(cel, quality=88)
    print(cel, plansza.size)


if __name__ == "__main__":
    main()
