#!/usr/bin/env python3
"""Arkusz HUD + pety (Paweł 25.11, jedna generacja: assets/raw/HudPety/arkusz_v1.png) -> osobne elementy do Roblox:
okno petów (pełny obraz + kafelki 2 × 2), panel questów, zakładka ze strzałką (otwarta / zamknięta), przycisk INDEX,
podpowiedź. Białe tło połączone z brzegiem -> przezroczyste, elementy rozdzielane po spójnych obszarach.

Użycie: python tools/hud_pety_ui.py
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/raw/HudPety/arkusz_v1.png"
OUT = ROOT / "assets/processed/HudPety"


def bez_tla(im, prog=232):
    a = np.array(im.convert("RGBA"))
    biale = a[..., :3].min(axis=2) > prog
    lab, _ = ndimage.label(biale)
    brzeg = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    tlo = np.isin(lab, list(brzeg))
    # wygładzenie krawędzi: 1 px przejścia zamiast schodków
    alfa = np.where(tlo, 0, 255).astype(np.float32)
    alfa = ndimage.uniform_filter(alfa, 3)
    alfa = np.where(tlo, 0, np.maximum(alfa, 0))
    a[..., 3] = alfa.astype(np.uint8)
    return a


def zapisz(im, nazwa, szer=None):
    if szer and im.width > szer:
        im = im.resize((szer, round(szer * im.height / im.width)), Image.LANCZOS)
    im.save(OUT / f"{nazwa}.png", optimize=True)
    print("ok", nazwa, im.size, "proporcje", round(im.width / im.height, 4))
    return im


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    a = bez_tla(Image.open(SRC))
    lab, n = ndimage.label(a[..., 3] > 0)
    obsz = ndimage.find_objects(lab)
    el = []
    for i, s in enumerate(obsz, 1):
        h, w = s[0].stop - s[0].start, s[1].stop - s[1].start
        if h * w > 150_000:
            wyc = a[s].copy()
            wyc[..., 3] = np.where(lab[s] == i, wyc[..., 3], 0)
            el.append((s[1].start, s[0].start, w, h, Image.fromarray(wyc)))
    el.sort(key=lambda e: -e[2] * e[3])
    assert len(el) == 5, [e[:4] for e in el]
    okno = el[0][4]
    reszta = el[1:]
    # panel questów: największy z pozostałych; INDEX: najbardziej kwadratowy; zakładka: wysoka; podpowiedź: pozioma mała
    questy = reszta[0][4]
    pozostale = reszta[1:]
    zakladka = min(pozostale, key=lambda e: e[2] / e[3])[4]
    pozostale = [e for e in pozostale if e[4] is not zakladka]
    index = min(pozostale, key=lambda e: abs(e[2] / e[3] - 1))[4]
    podp = [e for e in pozostale if e[4] is not index][0][4]

    okno.save(OUT / "OknoPetow.png", optimize=True)
    okno.convert("RGB").resize((1600, round(1600 * okno.height / okno.width)), Image.LANCZOS).save(
        OUT / "OknoPetow_podglad.jpg", quality=88)
    w, h = okno.size
    print("ok OknoPetow", okno.size, "proporcje", round(w / h, 4))
    for i, (cx, cy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)], 1):
        kaf = okno.crop((cx * w // 2, cy * h // 2, (cx + 1) * w // 2, (cy + 1) * h // 2))
        kaf.resize((1024, round(1024 * kaf.height / kaf.width)), Image.LANCZOS).save(OUT / f"OknoPetow{i}.png", optimize=True)
    zapisz(questy, "PanelQuestow", 1024)
    zapisz(index, "IconIndex", 512)
    zapisz(podp, "PodpowiedzPeta", 512)
    # zakładka: w arkuszu zaokrąglona z prawej, strzałka w lewo. Szuflada stoi przy prawej krawędzi ekranu, więc zakładka
    # wystaje w lewo: odbicie lustrzane (zaokrąglenie z lewej, strzałka w prawo = „schowaj”); wersja „wysuń” ma
    # samą strzałkę odbitą z powrotem (środkowy prostokąt).
    otw = zakladka.transpose(Image.FLIP_LEFT_RIGHT)
    zam = otw.copy()
    zw, zh = zam.size
    box = (round(zw * 0.1), round(zh * 0.2), round(zw * 0.9), round(zh * 0.8))
    wyc = zam.crop(box).transpose(Image.FLIP_LEFT_RIGHT)
    # miękki brzeg wklejki (strzałka w środku zostaje w całości, drewno przechodzi płynnie)
    mw, mh = wyc.size
    yy, xx = np.mgrid[0:mh, 0:mw]
    brzeg = np.minimum.reduce([xx, mw - 1 - xx, yy, mh - 1 - yy]).astype(np.float32)
    maska = Image.fromarray((np.clip(brzeg / (mw * 0.1), 0, 1) * 255).astype(np.uint8))
    zam.paste(wyc, box, maska)
    zapisz(otw, "ZakladkaQuestowSchowaj", 256)
    zapisz(zam, "ZakladkaQuestowWysun", 256)
    # podgląd wszystkich elementów na szarym tle
    arkusz = Image.new("RGB", (2000, 1250), (70, 74, 82))
    x = 20
    for im, wys in ((okno, 1100), (questy, 520), (otw, 300), (zam, 300), (index, 300), (podp, 220)):
        m = im.resize((round(im.width * wys / im.height), wys), Image.LANCZOS)
        if x + m.width > 1990:
            break
        arkusz.paste(m, (x, 20), m)
        x += m.width + 20
    arkusz.save(ROOT / "build/hudpety_elementy.jpg", quality=88)


if __name__ == "__main__":
    main()
