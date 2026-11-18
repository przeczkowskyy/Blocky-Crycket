#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Podgląd do raportu: pięć petów jajka obok siebie (portrety z Blendera) z rzadkością, szansą i skillem, a pod nimi
podgląd inkubatora i jajka. Ten sam układ dla każdego jajka; przy jajku dalszego biomu pod skillem stoi skill peta tej
samej rzadkości z jajka leśnego (porównanie). Tylko składa gotowe obrazy z swiat/postacie/wynik/ (Pillow) — Blender
niepotrzebny.

    python -B swiat/pety_proba/podglad.py        # → swiat/pety_proba/podglad/pety_lesne.jpg, pety_bagna.jpg, pety_dzungli.jpg

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
PODGLAD = os.path.join(TU, "podglad")
PLIKI = {"las": "pety_lesne.jpg", "bagno": "pety_bagna.jpg", "dzungla": "pety_dzungli.jpg"}   # inne: pety_<kraina>.jpg


def czcionka(rozmiar):
    from PIL import ImageFont
    for nazwa in ("arialbd.ttf", "DejaVuSans-Bold.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(nazwa, rozmiar)
        except OSError:
            continue
    return ImageFont.load_default()


def zawin(rys, tekst, font, szer):
    """Tekst w wiersze nie szersze niż szer px (po słowach)."""
    wiersze, biezacy = [], ""
    for slowo in tekst.split(" "):
        proba = (biezacy + " " + slowo).strip()
        if biezacy and rys.textlength(proba, font=font) > szer:
            wiersze.append(biezacy)
            biezacy = slowo
        else:
            biezacy = proba
    if biezacy:
        wiersze.append(biezacy)
    return wiersze


def podglad_jajka(D, U, j, lesne):
    from PIL import Image, ImageDraw
    ju = next(x for x in U["jajka"] if x["id"] == j["id"])
    M = ju["model"]
    wiersze = LP.wiersze_szans(D, j)
    porownanie = lesne is not None and lesne["id"] != j["id"]
    bok = 360
    szer = bok * len(wiersze)
    wys_opis = 250 if porownanie else 190   # skille D-101 bywają dłuższe — zawijane w kolumnie
    ink = Image.open(os.path.join(WYNIK, M["modul"], M["inkubator"] + "_bohater.jpg")).convert("RGB")
    ink = ink.resize((520, 520), Image.LANCZOS)
    jaj = Image.open(os.path.join(WYNIK, M["modul"], M["jajko"] + "_bohater.jpg")).convert("RGB").resize((520, 520),
                                                                                                         Image.LANCZOS)
    obraz = Image.new("RGB", (szer, 70 + bok + wys_opis + 540), (43, 33, 24))
    rys = ImageDraw.Draw(obraz)
    # cena stała (decyzja 17.11): „cena 300 Złota”; przy przełączniku „rosnaca”: „cena od 300 Złota”
    cena = ("cena od %d Złota" if j["cena"]["tryb"] == "rosnaca" else "cena %d Złota") % LP.cena(D, j, 0)
    rys.text((20, 18), "Pety: %s (próba, propozycja) — szanse jawne, %s, %s" % (
        j["nazwa"][0].lower() + j["nazwa"][1:], cena, j["opis_miejsca"]), fill=(255, 201, 74), font=czcionka(28))
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
        yy = y + 94
        for linia in zawin(rys, w["skill"], czcionka(20), bok - 28):
            rys.text((x + 14, yy), linia, fill=(220, 210, 190), font=czcionka(20))
            yy += 25
        if porownanie:
            p_las = LP.pet(D, lesne["pula"][i])
            skill = LP.opis_skilla(D, p_las).replace(" z walk", "").replace("doświadczenia", "dośw.")
            yy += 6
            for linia in zawin(rys, "las: %s — %s" % (p_las["nazwa"], skill), czcionka(17), bok - 28):
                rys.text((x + 14, yy), linia, fill=(160, 150, 135), font=czcionka(17))
                yy += 21
    y = 70 + bok + wys_opis + 10
    obraz.paste(ink, (szer // 2 - 540, y))
    obraz.paste(jaj, (szer // 2 + 20, y))
    rys.text((szer // 2 - 530, y + 6), "Inkubator (podgląd z Blendera)", fill=(43, 33, 24), font=czcionka(20))
    rys.text((szer // 2 + 30, y + 6), "%s (pęka przy wykluciu)" % j["nazwa"], fill=(43, 33, 24), font=czcionka(20))
    cel = os.path.join(PODGLAD, PLIKI.get(j["kraina"], "pety_%s.jpg" % j["kraina"]))
    os.makedirs(PODGLAD, exist_ok=True)
    obraz.save(cel, "JPEG", quality=88)
    print("zapisano %s (%d × %d)" % (os.path.relpath(cel, REPO), obraz.width, obraz.height))


def main():
    D = DP.podstawa()
    U = DP.ustawienia()
    lesne = LP.jajko_krainy(D, "las")
    for j in D["jajka"]:
        podglad_jajka(D, U, j, lesne)


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    main()
