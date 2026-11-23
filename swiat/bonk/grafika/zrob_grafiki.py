#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ikona i miniatury BONK do strony gry w Roblox (etap 3) — napisy dodane lokalnie (Pillow), bez usług zewnętrznych.

    python -B swiat/bonk/grafika/zrob_grafiki.py swiat/bonk/grafika/szkice

Szkice (Higgsfield, bez napisów; kopie w `szkice/`): ikona.png (1024 × 1024), miniatura_home_run_1920.jpg, miniatura_pety_1920.jpg,
miniatura_straznik_1920.jpg (1920 × 1080). Wynik w tym folderze: ikona_512.png (512 × 512, tytuł „BONK!”),
miniatura_home_run.jpg, miniatura_pety.jpg, miniatura_straznik.jpg (1920 × 1080, krótkie hasło po angielsku — D-045)
i podglad.jpg (wszystko na jednej planszy, ikona także w 150 px — tak małą widać ją na liście gier).
Krój: Luckiest Guy (ten sam co w interfejsie gry, licencja Apache 2.0) z instalacji Roblox; gdy go nie ma — Impact.
Nic tu nie wgrywa do Roblox (to decyzja ludzi przy publikacji, README → „Publikacja jako osobna gra”).
"""
import glob
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

TU = os.path.dirname(os.path.abspath(__file__))
TUSZ = (27, 20, 36, 255)            # jak w grze (ui.kolory.tusz)
ZOLTY = ((255, 236, 120), (255, 176, 28))    # wypełnienie z góry na dół
BIALY = ((255, 255, 255), (255, 238, 205))
CZERWONY = ((255, 120, 96), (232, 52, 52))


def kroj():
    wzory = [os.path.join(os.environ.get("LOCALAPPDATA", ""), "Roblox", "Versions", "*", "content", "fonts", "LuckiestGuy-Regular.ttf"),
             r"C:\Program Files (x86)\Roblox\Versions\*\content\fonts\LuckiestGuy-Regular.ttf"]
    for w in wzory:
        z = sorted(glob.glob(w))
        if z:
            return z[-1]
    for z in (r"C:\Windows\Fonts\impact.ttf", r"C:\Windows\Fonts\ariblk.ttf"):
        if os.path.isfile(z):
            return z
    sys.exit("brak grubego kroju (Luckiest Guy z Roblox albo Impact)")


KROJ = kroj()


def napis(tekst, wys_px, kolory, obrys=None, cien=None, odstep=0.0):
    """Warstwa RGBA z napisem: wypełnienie gradientem, gruby obrys tuszem, twardy cień w dół-prawo."""
    f = ImageFont.truetype(KROJ, wys_px)
    obrys = obrys or max(3, int(wys_px * 0.11))
    cien = cien if cien is not None else max(2, int(wys_px * 0.07))
    linie = tekst.split("\n")
    rozm = [f.getbbox(l, stroke_width=obrys) for l in linie]
    szer = max(b[2] - b[0] for b in rozm)
    wl = int(wys_px * (1.05 + odstep))
    W, H = szer + 2 * obrys + cien + 20, wl * len(linie) + 2 * obrys + cien + 20
    maska = Image.new("L", (W, H), 0)
    kontur = Image.new("L", (W, H), 0)
    dm, dk = ImageDraw.Draw(maska), ImageDraw.Draw(kontur)
    for i, (l, b) in enumerate(zip(linie, rozm)):
        x = (W - cien - (b[2] - b[0])) // 2 - b[0]
        y = 10 + obrys + i * wl - b[1] + obrys
        dk.text((x, y), l, font=f, fill=255, stroke_width=obrys, stroke_fill=255)
        dm.text((x, y), l, font=f, fill=255)
    gora, dol = kolory
    grad = Image.new("RGBA", (1, H))
    for y in range(H):
        t = y / max(1, H - 1)
        grad.putpixel((0, y), tuple(int(gora[k] + (dol[k] - gora[k]) * t) for k in range(3)) + (255,))
    grad = grad.resize((W, H))
    warstwa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cienw = Image.new("RGBA", (W, H), TUSZ[:3] + (0,))
    cienw.putalpha(kontur)
    warstwa.alpha_composite(cienw, (cien, cien))
    tusz = Image.new("RGBA", (W, H), TUSZ)
    warstwa.paste(tusz, (0, 0), kontur)
    # połysk: jaśniejszy pasek w górnej części liter
    warstwa.paste(grad, (0, 0), maska)
    return warstwa


def poloz(tlo, warstwa, srodek, kat=0.0, szer_max=None):
    if szer_max and warstwa.width > szer_max:
        warstwa = warstwa.resize((szer_max, int(warstwa.height * szer_max / warstwa.width)), Image.LANCZOS)
    if kat:
        warstwa = warstwa.rotate(kat, resample=Image.BICUBIC, expand=True)
    x, y = int(srodek[0] - warstwa.width / 2), int(srodek[1] - warstwa.height / 2)
    tlo.alpha_composite(warstwa, (x, y))
    return tlo


def winieta(tlo, gdzie, sila=0.45):
    """Delikatne przyciemnienie pod napisem (czytelność na jasnym tle)."""
    W, H = tlo.size
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    x0, y0, x1, y1 = gdzie
    d.ellipse((x0, y0, x1, y1), fill=int(255 * sila))
    m = m.filter(ImageFilter.GaussianBlur(min(W, H) * 0.06))
    ciem = Image.new("RGBA", (W, H), TUSZ[:3] + (0,))
    ciem.putalpha(m)
    tlo.alpha_composite(ciem)
    return tlo


def ikona(src):
    im = Image.open(os.path.join(src, "ikona.png")).convert("RGBA").resize((1024, 1024), Image.LANCZOS)
    im = winieta(im, (60, 700, 980, 1160), 0.5)
    t = napis("BONK!", 300, ZOLTY, obrys=30, cien=20)
    poloz(im, t, (512, 845), kat=7, szer_max=900)
    out = im.resize((512, 512), Image.LANCZOS).convert("RGB")
    out.save(os.path.join(TU, "ikona_512.png"), optimize=True)
    return out


def miniatura(src, plik, wyj, hasla):
    im = Image.open(os.path.join(src, plik)).convert("RGBA")
    if im.size != (1920, 1080):
        im = im.resize((1920, 1080), Image.LANCZOS)
    for h in hasla:
        if h.get("winieta"):
            winieta(im, h["winieta"], h.get("sila", 0.45))
        poloz(im, napis(h["tekst"], h["wys"], h.get("kolory", ZOLTY), odstep=h.get("odstep", 0.0)), h["srodek"],
              kat=h.get("kat", 0), szer_max=h.get("szer"))
    out = im.convert("RGB")
    out.save(os.path.join(TU, wyj), quality=90, optimize=True)
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    ik = ikona(src)
    logo = dict(tekst="BONK!", wys=150, kolory=ZOLTY, kat=6, szer=430)
    m1 = miniatura(src, "miniatura_home_run_1920.jpg", "miniatura_home_run.jpg", [
        dict(tekst="BONK THEM\nTO THE SKY!", wys=165, kolory=BIALY, srodek=(560, 215), kat=4, szer=1000,
             winieta=(-200, -150, 1250, 560), sila=0.5, odstep=-0.05),
        dict(logo, srodek=(1640, 965), winieta=(1350, 840, 1960, 1120), sila=0.35)])
    m2 = miniatura(src, "miniatura_pety_1920.jpg", "miniatura_pety.jpg", [
        dict(tekst="HATCH\nPETS!", wys=230, kolory=ZOLTY, srodek=(1550, 300), kat=-5, szer=700,
             winieta=(1100, -100, 2050, 680), sila=0.5, odstep=-0.08),
        dict(logo, srodek=(1660, 960), winieta=(1380, 840, 1960, 1120), sila=0.35)])
    m3 = miniatura(src, "miniatura_straznik_1920.jpg", "miniatura_straznik.jpg", [
        dict(tekst="BEAT GUARDIANS\nTOGETHER!", wys=150, kolory=CZERWONY, srodek=(500, 190), kat=-4, szer=880,
             winieta=(-250, -150, 1050, 560), sila=0.5, odstep=-0.05),
        dict(logo, srodek=(1650, 965), winieta=(1360, 840, 1960, 1120), sila=0.35)])
    # plansza podglądu: miniatury, ikona 512 i 150 px
    pl = Image.new("RGB", (1920 + 40, 1120), (40, 36, 48))
    for i, m in enumerate((m1, m2, m3)):
        pl.paste(m.resize((640, 360), Image.LANCZOS), (10 + i * 650, 10))
    pl.paste(ik, (10, 400))
    pl.paste(ik.resize((150, 150), Image.LANCZOS), (540, 400))
    pl.paste(ik.resize((100, 100), Image.LANCZOS), (540, 570))
    pl = pl.crop((0, 0, 1960, 930))
    pl.save(os.path.join(TU, "podglad.jpg"), quality=85)
    print("kroj:", os.path.basename(KROJ))
    for n in ("ikona_512.png", "miniatura_home_run.jpg", "miniatura_pety.jpg", "miniatura_straznik.jpg", "podglad.jpg"):
        p = os.path.join(TU, n)
        print("%s  %s  %d kB" % (n, Image.open(p).size, os.path.getsize(p) // 1024))


if __name__ == "__main__":
    main()
