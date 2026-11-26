#!/usr/bin/env python3
"""Arkusz tablicy questów (Paweł 25.11, jedna generacja: assets/raw/OknoQuestow/arkusz_v1.png, Higgsfield job ef96b5ac)
-> osobne elementy do Roblox w assets/processed/OknoQuestow/: okno tablicy (pełny obraz + kafelki 2 × 2), wiersz
questa (pergamin wydłużony do proporcji 6,4 : 1 — środek bez wzoru rozciągnięty w pliku, końce bez zmian), dwie karty
kategorii (pomarańczowa, turkusowa), dwa przyciski (zielony, złoty), ikony słońca i pucharu.

Użycie: python tools/okno_questow_ui.py
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

import hud_pety_ui as H

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/raw/OknoQuestow/arkusz_v1.png"
OUT = ROOT / "assets/processed/OknoQuestow"
PROPORCJE_WIERSZA = 6.4


def zapisz(im, nazwa, szer=None):
    if szer and im.width > szer:
        im = im.resize((szer, round(szer * im.height / im.width)), Image.LANCZOS)
    im.save(OUT / f"{nazwa}.png", optimize=True)
    print("ok", nazwa, im.size, "proporcje", round(im.width / im.height, 4))
    return im


def wydluz(wiersz):
    """Lewy koniec (pinezka + pole ikony) i prawy koniec bez zmian, gładki środek pergaminu rozciągnięty."""
    w, h = wiersz.size
    lewy, prawy = round(w * 0.34), round(w * 0.9)
    cel = round(h * PROPORCJE_WIERSZA)
    srodek = wiersz.crop((lewy, 0, prawy, h)).resize((cel - lewy - (w - prawy), h), Image.LANCZOS)
    wynik = Image.new("RGBA", (cel, h), (0, 0, 0, 0))
    wynik.paste(wiersz.crop((0, 0, lewy, h)), (0, 0))
    wynik.paste(srodek, (lewy, 0))
    wynik.paste(wiersz.crop((prawy, 0, w, h)), (cel - (w - prawy), 0))
    return wynik


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    a = H.bez_tla(Image.open(SRC))
    lab, _ = ndimage.label(a[..., 3] > 0)
    el = []
    for i, s in enumerate(ndimage.find_objects(lab), 1):
        h, w = s[0].stop - s[0].start, s[1].stop - s[1].start
        if h * w > 60_000:
            wyc = a[s].copy()
            wyc[..., 3] = np.where(lab[s] == i, wyc[..., 3], 0)
            el.append((s[1].start, s[0].start, w, h, Image.fromarray(wyc)))
    assert len(el) == 8, [e[:4] for e in el]
    el.sort(key=lambda e: -e[2] * e[3])
    okno = el[0][4]
    reszta = sorted(el[1:], key=lambda e: (round(e[1] / 400), e[0]))   # rzędami od góry, w rzędzie od lewej
    wiersz, karta_a, karta_b, zielony, zloty, slonce, puchar = [e[4] for e in reszta]

    okno.save(OUT / "OknoQuestow.png", optimize=True)
    okno.convert("RGB").resize((1400, round(1400 * okno.height / okno.width)), Image.LANCZOS).save(
        OUT / "OknoQuestow_podglad.jpg", quality=88)
    w, h = okno.size
    print("ok OknoQuestow", okno.size, "proporcje", round(w / h, 4))
    for i, (cx, cy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)], 1):
        kaf = okno.crop((cx * w // 2, cy * h // 2, (cx + 1) * w // 2, (cy + 1) * h // 2))
        kaf.resize((1024, round(1024 * kaf.height / kaf.width)), Image.LANCZOS).save(OUT / f"OknoQuestow{i}.png", optimize=True)
    wiersz = zapisz(wydluz(wiersz), "QuestWiersz", 1024)
    karta_a = zapisz(karta_a, "QuestKartaDzienne", 512)
    karta_b = zapisz(karta_b, "QuestKartaOsiagniecia", 512)
    zielony = zapisz(zielony, "QuestPrzyciskZielony", 512)
    zloty = zapisz(zloty, "QuestPrzyciskZloty", 512)
    slonce = zapisz(slonce, "QuestIkonaDzienne", 256)
    puchar = zapisz(puchar, "QuestIkonaOsiagniecia", 256)
    # podgląd elementów na szarym tle
    arkusz = Image.new("RGB", (2000, 900), (70, 74, 82))
    x, y = 20, 20
    for im, wys in ((okno, 860), (wiersz, 150), (karta_a, 260), (karta_b, 260), (zielony, 110), (zloty, 110), (slonce, 160),
                    (puchar, 160)):
        m = im.resize((round(im.width * wys / im.height), wys), Image.LANCZOS)
        if x + m.width > 1990:
            x, y = 1000, y + 290
        arkusz.paste(m, (x, y), m)
        x += m.width + 20
    arkusz.save(ROOT / "build/oknoquestow_elementy.jpg", quality=88)


if __name__ == "__main__":
    main()
