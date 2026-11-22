# -*- coding: utf-8 -*-
"""Obrazy strony gry: ikona 512 × 512 i trzy miniatury 1920 × 1080. Postacie i sceny renderuje Blender (biblioteka,
wspólna blokada), tło, czarną sylwetkę ze znakiem zapytania i napis z własnych klockowych liter składa PIL.

    python -B swiat/ewolucja/modele/generuj.py obrazy       # wymaga wcześniejszego „dane”

Pełne pliki: %LOCALAPPDATA%/BlockyCrycket/modele/smok_ewolucja/obrazy/ (PNG), małe podglądy: podglad/13–16.
Jedyny tekst na obrazach to tytuł DRAGON LAIR EVOLUTION i „?”.
"""
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

GLIFY = {  # własne litery 5 × 7 z klocków
    "D": "11110 10001 10001 10001 10001 10001 11110", "R": "11110 10001 10001 11110 10100 10010 10001",
    "A": "01110 10001 10001 11111 10001 10001 10001", "G": "01111 10000 10000 10111 10001 10001 01111",
    "O": "01110 10001 10001 10001 10001 10001 01110", "N": "10001 11001 10101 10011 10001 10001 10001",
    "L": "10000 10000 10000 10000 10000 10000 11111", "I": "11111 00100 00100 00100 00100 00100 11111",
    "E": "11111 10000 10000 11110 10000 10000 11111", "V": "10001 10001 10001 10001 10001 01010 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "?": "01110 10001 00001 00010 00100 00000 00100",
}


def napis(tekst, kom, gora=(255, 244, 140), dol=(255, 138, 24), obrys=(52, 18, 76), cien=(16, 6, 28)):
    """Napis z klocków: gruby obrys, cień, pionowy gradient, jasna krawędź u góry każdego klocka."""
    szer = sum(4 if ch == " " else 6 for ch in tekst) - 1
    gr = max(3, kom // 3)
    pad = gr + kom
    W, H = szer * kom + 2 * pad, 7 * kom + 2 * pad
    maska, blask = Image.new("L", (W, H), 0), Image.new("L", (W, H), 0)
    d, db = ImageDraw.Draw(maska), ImageDraw.Draw(blask)
    x = pad
    for ch in tekst:
        if ch == " ":
            x += 4 * kom
            continue
        for r, wiersz in enumerate(GLIFY[ch].split()):
            for c, bit in enumerate(wiersz):
                if bit == "1":
                    x0, y0 = x + c * kom, pad + r * kom
                    d.rectangle((x0, y0, x0 + kom - 1, y0 + kom - 1), fill=255)
                    db.rectangle((x0 + kom // 8, y0 + kom // 8, x0 + kom - 1 - kom // 8, y0 + kom // 3), fill=110)
        x += 6 * kom
    obr = maska.filter(ImageFilter.MaxFilter(2 * gr + 1))
    wyn = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wyn.paste(Image.new("RGBA", (W, H), cien + (210,)), (gr, gr + kom // 3), obr)
    wyn.paste(Image.new("RGBA", (W, H), obrys + (255,)), (0, 0), obr)
    grad = ImageOps.colorize(Image.linear_gradient("L").resize((W, 7 * kom)), black=gora, white=dol).convert("RGBA")
    pelny = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pelny.paste(grad, (0, pad))
    wyn.paste(pelny, (0, 0), maska)
    wyn.paste(Image.new("RGBA", (W, H), (255, 255, 255, 255)), (0, 0), blask)
    return wyn


def tlo(w, h, srodek, kolory, promienie=0, kolor_p=(255, 244, 170), sila=44):
    """Tło promieniste: kolory (środek, pośredni, brzeg) i opcjonalne promienie światła ze środka."""
    g = Image.radial_gradient("L").resize((int(w * 2.4), int(h * 2.4)))
    x0, y0 = int(g.width / 2 - srodek[0] * w), int(g.height / 2 - srodek[1] * h)
    t = ImageOps.colorize(g.crop((x0, y0, x0 + w, y0 + h)), black=kolory[0], white=kolory[2], mid=kolory[1]).convert("RGB")
    if promienie:
        war = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(war)
        cx, cy, R = srodek[0] * w, srodek[1] * h, 2.0 * (w + h)
        for i in range(promienie):
            a0 = 2 * math.pi * i / promienie
            a1 = a0 + math.pi / promienie * 0.85
            d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))],
                      fill=sila)
        t.paste(Image.new("RGB", (w, h), kolor_p), (0, 0), war.filter(ImageFilter.GaussianBlur(3)))
    return t


def wytnij(sciezka, wys=None, szer=None):
    im = Image.open(sciezka).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    k = (wys / float(im.height)) if wys else (szer / float(im.width))
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)


def naklejka(im, grub, kolor=(255, 255, 255)):
    """Biały obrys wokół postaci (czytelność w małym rozmiarze)."""
    pad = grub + 2
    a = Image.new("L", (im.width + 2 * pad, im.height + 2 * pad), 0)
    a.paste(im.getchannel("A"), (pad, pad))
    wyn = Image.new("RGBA", a.size, (0, 0, 0, 0))
    wyn.paste(Image.new("RGBA", a.size, kolor + (255,)), (0, 0), a.filter(ImageFilter.MaxFilter(2 * grub + 1)))
    wyn.alpha_composite(im, (pad, pad))
    return wyn


def wklej(t, im, x_srodek, y_dol):
    t.paste(im, (int(x_srodek - im.width / 2), int(y_dol - im.height)), im)


def cien(t, x, y, w, h, moc=120):
    war = Image.new("L", t.size, 0)
    ImageDraw.Draw(war).ellipse((x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=moc)
    t.paste(Image.new("RGB", t.size, (14, 6, 24)), (0, 0), war.filter(ImageFilter.GaussianBlur(max(4, int(h / 5)))))


def poswiata(t, prog=178, r=16):
    """Rozświetlenie jasnych miejsc (żar, ogień, klejnoty)."""
    jasne = t.point(lambda v: max(0, v - prog) * 3).filter(ImageFilter.GaussianBlur(r))
    return ImageChops.screen(t, jasne)


def _font(rozmiar):
    """Gruba, czysta czcionka zainstalowana w systemie (Cooper Black; dalej zamienniki)."""
    from PIL import ImageFont
    for nazwa in ("COOPBL.TTF", "GILSANUB.TTF", "seguibl.ttf", "ariblk.ttf", "impact.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(nazwa, rozmiar)
        except OSError:
            continue
    return ImageFont.load_default()


def litery(tekst, wys, gora=(255, 248, 160), dol=(255, 146, 26), obrys=(58, 20, 88), cien=(18, 6, 30)):
    """Napis czcionką: gruby ciemny obrys, cień, pionowy gradient i jaśniejsza górna połowa (połysk)."""
    font = _font(int(wys))
    gr = max(4, int(wys * 0.09))
    l, g_, r, b = ImageDraw.Draw(Image.new("L", (8, 8))).textbbox((0, 0), tekst, font=font, stroke_width=gr)
    W, H = r - l + int(wys * 0.16), b - g_ + int(wys * 0.2)
    ox, oy = -l, -g_
    maska, obr = Image.new("L", (W, H), 0), Image.new("L", (W, H), 0)
    ImageDraw.Draw(maska).text((ox, oy), tekst, font=font, fill=255)
    ImageDraw.Draw(obr).text((ox, oy), tekst, font=font, fill=255, stroke_width=gr, stroke_fill=255)
    wyn = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wyn.paste(Image.new("RGBA", (W, H), cien + (225,)), (int(wys * 0.05), int(wys * 0.1)), obr)
    wyn.paste(Image.new("RGBA", (W, H), obrys + (255,)), (0, 0), obr)
    wyn.paste(ImageOps.colorize(Image.linear_gradient("L").resize((W, H)), black=gora, white=dol).convert("RGBA"), (0, 0), maska)
    polysk = Image.new("L", (W, H), 0)
    ImageDraw.Draw(polysk).rectangle((0, 0, W, int(oy + (b - g_) * 0.5)), fill=64)
    wyn.paste(Image.new("RGBA", (W, H), (255, 255, 255, 255)), (0, 0), ImageChops.multiply(maska, polysk))
    return wyn


def tytul(t, x_srodek, y, w1=150, w2=214):
    a, b = litery("DRAGON LAIR", w1), litery("EVOLUTION", w2)
    t.paste(a, (int(x_srodek - a.width / 2), int(y)), a)
    t.paste(b, (int(x_srodek - b.width / 2), int(y + a.height - w1 * 0.3)), b)


def zrob(g):
    """g = moduł generuj (pomocnicy: wyjscie, widoki, modele_pelne, PODGLAD)."""
    from swiat.ewolucja.modele import rekwizyty, sprawdz_dane as sd
    rob, cel = g.wyjscie("obrazy_robocze"), g.wyjscie("obrazy")
    smoki = g.modele_pelne(jajo=False)

    def kl(nr, nazwa, u):
        return [nazwa, int(round(next(k for k in smoki[nr - 1].klipy if k.nazwa == nazwa).dlugosc * u))]

    # wylot ognia napastnika (FIRE DRAKE zwrócony w +X): kinematyka z danych gry, układ rigu -> układ sceny
    rig, klipy = sd.wczytaj("smok_4_rig.json"), sd.wczytaj("smok_4_klipy.json")["klipy"]
    pr = sd.punkt_zaczepu(rig, sd.poza(rig, klipy["ogien_petla"], 0), "PyskAttachment")
    S4, X4, XO = 1.3, -9.5, 9.5
    pysk = (X4 - pr[2] * S4, pr[1] * S4, pr[0] * S4)
    from swiat.ewolucja.modele import swiat_zestaw
    ogien = rekwizyty.ogien2(max(4.0, XO - 3.4 - pysk[0]))
    dodatki = [swiat_zestaw.zbuduj("stos_zlota_3"), swiat_zestaw.zbuduj("stos_zlota_1"), swiat_zestaw.zbuduj("legowisko_krag"),
               rekwizyty.gniazdo(), rekwizyty.cokol(), ogien]
    zad = [{"typ": "scena", "plik": "ik_piskle.png", "rozmiar": [900, 900], "kierunek": [0.34, 0.24, 1.0],
            "modele": [{"id": "smok_1", "poza": ["cokol", 0]}]},
           {"typ": "scena", "plik": "ik_prastary.png", "rozmiar": [1400, 1400], "kierunek": [0.06, 0.05, 1.0],
            "modele": [{"id": "smok_8", "czarny": True, "poza": kl(8, "ryk", 0.5)}]}]
    zad += [{"typ": "scena", "plik": "m1_%d.png" % n, "rozmiar": [800, 800], "orto": True, "kierunek": [0.8, 0.18, 1.0],
             "modele": [{"id": "smok_%d" % n, "poza": ["cokol", 0], "czarny": n == 8}]} for n in range(1, 9)]
    zad.append({"typ": "scena", "plik": "m2.png", "rozmiar": [1920, 1080], "kierunek": [0.4, 0.2, 1.0], "margines": 1.04,
                "kadr": ["stos_zlota_3", "smok_5", "smok_1", "gniazdo", "stos_zlota_1"],
                "modele": [{"id": "legowisko_krag", "poz": [0, 0, -1.0]}, {"id": "stos_zlota_3"},
                           {"id": "smok_5", "poz": [0, 2.2, -0.8], "poza": ["cokol", 0]},
                           {"id": "smok_1", "poz": [7.6, 0, 6.4], "obrot_y": -35, "poza": ["spoczynek", 0]},
                           {"id": "gniazdo", "poz": [-8.6, 0, 5.4], "skala": 0.8}, {"id": "stos_zlota_1", "poz": [9.6, 0, 1.0]}]
                          + [{"id": "cokol", "poz": [x, 0, -7.4 + abs(x) * 0.25], "skala": 0.4} for x in (-7.0, 7.0)]})
    zad.append({"typ": "scena", "plik": "m3.png", "rozmiar": [1920, 1080], "kierunek": [0.0, 0.1, 1.0], "margines": 1.04,
                "modele": [{"id": "smok_4", "poz": [X4, 0, 0], "obrot_y": 90, "skala": S4, "poza": ["ogien_petla", 0]},
                           {"id": "smok_3", "poz": [XO, 0, 0], "obrot_y": -90, "skala": 1.6, "poza": kl(3, "trafienie", 0.25)},
                           {"id": "ogien", "poz": list(pysk), "obrot_y": 90}]})
    g.widoki(smoki + dodatki, zad, rob, "obrazy strony gry (%d scen)" % len(zad))

    def r(nazwa):
        return os.path.join(rob, nazwa)

    # ---- ikona: jasne pisklę przed wielką czarną sylwetką Prastarego ze znakiem zapytania
    W = 1024
    t = tlo(W, W, (0.5, 0.4), ((255, 232, 120), (255, 132, 44), (104, 26, 100)), promienie=16)
    wklej(t, wytnij(r("ik_prastary.png"), szer=int(W * 1.3)), W * 0.5, W * 0.92)
    q = litery("?", 330, gora=(255, 252, 200), dol=(255, 190, 40), obrys=(70, 22, 100))
    t.paste(q, (int(W * 0.5 - q.width / 2), int(W * 0.1)), q)
    ImageDraw.Draw(t).ellipse((-0.3 * W, 0.8 * W, 1.3 * W, 1.4 * W), fill=(58, 22, 72))
    cien(t, W * 0.5, W * 0.93, W * 0.6, W * 0.1)
    wklej(t, naklejka(wytnij(r("ik_piskle.png"), wys=int(W * 0.56)), 10), W * 0.5, W * 0.975)
    ikona = poswiata(t, 196, 14).resize((512, 512), Image.LANCZOS)
    ikona.save(os.path.join(cel, "ikona_512.png"))

    # ---- miniatura 1: osiem stadiów od małego do wielkiego, ostatnie jako sylwetka z „?”
    t = tlo(1920, 1080, (0.74, 0.6), ((255, 236, 150), (255, 150, 70), (64, 30, 110)), promienie=18)
    ImageDraw.Draw(t).ellipse((-400, 870, 2320, 1700), fill=(84, 160, 78))
    wklej(t, wytnij(r("m1_8.png"), wys=930), 1560, 1030)
    q = litery("?", 340, gora=(255, 252, 200), dol=(255, 190, 40), obrys=(70, 22, 100))
    t.paste(q, (1560 - q.width // 2, 400), q)
    for n, wys_, x in ((7, 470, 1215), (6, 380, 1000), (5, 330, 800), (4, 270, 615), (3, 220, 450), (2, 180, 300), (1, 150, 150)):
        im = naklejka(ImageOps.mirror(wytnij(r("m1_%d.png" % n), wys=wys_)), 5)
        cien(t, x, 992, im.width * 0.7, 36, 90)
        wklej(t, im, x, 1000)
    tytul(t, 760, 24)
    m1 = poswiata(t, 200, 12)

    # ---- miniatura 2: legowisko, kopiec złota i smok, który go pilnuje
    t = tlo(1920, 1080, (0.5, 0.74), ((255, 206, 96), (116, 50, 104), (20, 12, 38)))
    d = ImageDraw.Draw(t)
    for x, sz, dl_ in ((90, 150, 300), (330, 110, 210), (1480, 130, 260), (1760, 170, 340), (1140, 90, 150), (640, 80, 130)):
        d.polygon([(x - sz, -10), (x + sz, -10), (x + sz * 0.1, dl_)], fill=(15, 9, 30))
    d.ellipse((-300, 830, 2220, 1500), fill=(44, 30, 66))
    sc_ = wytnij(r("m2.png"), wys=720)
    cien(t, 960, 1010, sc_.width * 0.9, 90, 130)
    wklej(t, sc_, 960, 1050)
    tytul(t, 960, 6, 128, 184)
    m2 = poswiata(t, 186, 18)

    # ---- miniatura 3: walka — smok zieje ogniem w drugiego
    t = tlo(1920, 1080, (0.5, 0.66), ((150, 60, 96), (70, 28, 84), (18, 10, 34)), promienie=20, kolor_p=(255, 150, 70), sila=22)
    ImageDraw.Draw(t).ellipse((-300, 860, 2220, 1500), fill=(30, 18, 44))
    sc_ = wytnij(r("m3.png"), szer=1800)
    cien(t, 960, 1010, 1650, 80, 130)
    wklej(t, sc_, 960, 1045)
    tytul(t, 960, 6, 128, 184)
    m3 = poswiata(poswiata(t, 168, 26), 228, 8)

    for i, im in enumerate((m1, m2, m3), 1):
        im.save(os.path.join(cel, "miniatura_%d_1920x1080.png" % i))
        im.resize((640, 360), Image.LANCZOS).save(os.path.join(g.PODGLAD, "%d_miniatura_%d.jpg" % (13 + i, i)), quality=86)
    ikona.resize((256, 256), Image.LANCZOS).convert("RGB").save(os.path.join(g.PODGLAD, "13_ikona.jpg"), quality=88)
    # sprawdzian czytelności: ikona 150 i 64 px, miniatury 150 px szerokości
    spr = Image.new("RGB", (150 + 64 + 3 * 150 + 50, 170), (30, 30, 34))
    spr.paste(ikona.resize((150, 150), Image.LANCZOS), (10, 10))
    spr.paste(ikona.resize((64, 64), Image.LANCZOS), (170, 10))
    for i, im in enumerate((m1, m2, m3)):
        spr.paste(im.resize((150, 84), Image.LANCZOS), (244 + i * 160, 10))
    spr.save(os.path.join(cel, "sprawdzian_150px.png"))
    print("OBRAZY | ikona_512.png, miniatura_1..3_1920x1080.png, sprawdzian_150px.png w folderze wyników: obrazy")
