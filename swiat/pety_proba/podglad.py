#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Podgląd do raportu: pięć petów leśnego jajka obok siebie (portrety z Blendera) z rzadkością, szansą i skillem,
a pod nimi podgląd inkubatora. Tylko składa gotowe obrazy z swiat/postacie/wynik/ (Pillow) — Blender niepotrzebny.

    python -B swiat/pety_proba/podglad.py        # → swiat/pety_proba/podglad/pety_lesne.jpg

Najpierw: python -B swiat/postacie/przebuduj.py <moduły> --bez-filmow (portrety <id>_bohater.jpg).
"""
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if TU not in sys.path:
    sys.path.insert(0, TU)
import dane_petow as DP  # noqa: E402
import logika_petow as LP  # noqa: E402

WYNIK = os.path.join(REPO, "swiat", "postacie", "wynik")
CEL = os.path.join(TU, "podglad", "pety_lesne.jpg")


def czcionka(rozmiar):
    from PIL import ImageFont
    for nazwa in ("arialbd.ttf", "DejaVuSans-Bold.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(nazwa, rozmiar)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    from PIL import Image, ImageDraw
    D = DP.podstawa()
    j = D["jajka"][0]
    wiersze = LP.wiersze_szans(D, j)
    bok = 360
    szer = bok * len(wiersze)
    wys_opis = 150
    ink = Image.open(os.path.join(WYNIK, "jajko_lesne", "inkubator_lesny_bohater.jpg")).convert("RGB")
    ink = ink.resize((520, 520), Image.LANCZOS)
    jaj = Image.open(os.path.join(WYNIK, "jajko_lesne", "jajko_lesne_bohater.jpg")).convert("RGB").resize((520, 520),
                                                                                                         Image.LANCZOS)
    obraz = Image.new("RGB", (szer, 70 + bok + wys_opis + 540), (43, 33, 24))
    rys = ImageDraw.Draw(obraz)
    rys.text((20, 18), "Pety leśnego jajka (próba, propozycja) — szanse jawne, cena od %d Złota" % LP.cena(D, j, 0),
             fill=(255, 201, 74), font=czcionka(30))
    for i, w in enumerate(wiersze):
        x = i * bok
        im = Image.open(os.path.join(WYNIK, w["pet"], w["pet"] + "_bohater.jpg")).convert("RGB").resize((bok, bok),
                                                                                                       Image.LANCZOS)
        obraz.paste(im, (x, 70))
        kolor = tuple(int(w["kolor"][k:k + 2], 16) for k in (0, 2, 4))
        y = 70 + bok
        rys.rectangle([x, y, x + bok - 1, y + 10], fill=kolor)
        rys.text((x + 14, y + 18), w["nazwa"], fill=kolor, font=czcionka(30))
        rys.text((x + 14, y + 58), "%s · %s" % (w["rzadkosc"], w["szansa"]), fill=(255, 246, 224), font=czcionka(24))
        rys.text((x + 14, y + 94), w["skill"], fill=(220, 210, 190), font=czcionka(20))
    y = 70 + bok + wys_opis + 10
    obraz.paste(ink, (szer // 2 - 540, y))
    obraz.paste(jaj, (szer // 2 + 20, y))
    rys.text((szer // 2 - 530, y + 6), "Inkubator (podgląd z Blendera)", fill=(43, 33, 24),
             font=czcionka(20))
    rys.text((szer // 2 + 30, y + 6), "Jajko leśne (pęka przy wykluciu)", fill=(43, 33, 24), font=czcionka(20))
    os.makedirs(os.path.dirname(CEL), exist_ok=True)
    obraz.save(CEL, "JPEG", quality=88)
    print("zapisano %s (%d × %d)" % (os.path.relpath(CEL, REPO), obraz.width, obraz.height))


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    main()
