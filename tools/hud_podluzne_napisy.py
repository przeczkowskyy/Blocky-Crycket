#!/usr/bin/env python3
"""Napisy podłużnych przycisków HUD wycięte ze starych kwadratowych ikon (Paweł 26.11: „popraw czcionki tak jak te
tutaj” — liternictwo starych ikon jest rysowane, żadna czcionka Roblox go nie odda). Z każdej starej ikony bierze
sam napis (czarny obrys + wypełnienie liter, bez tła przycisku) i zapisuje go jako osobny obrazek HudLabel*.png;
w grze leży on na podłużnym przycisku jako ImageLabel (tools/hud_pety_build_gui.py).

Jak: ciemne piksele (obrys) w dolnej części ikony łączone w obszary; obszary napisu = te poniżej ikony, które nie są
obwódką przycisku; do nich dochodzi wszystko, co obrys zamyka (wypełnienie liter); zamknięte „oczka” liter w kolorze
tła przycisku (środek O, P, R…) robią się przezroczyste.

Użycie: python tools/hud_podluzne_napisy.py     (pliki + podgląd na przyciskach)
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/processed/HudPodluzne"
STARE = {"Teleport": "assets/processed/Teleport.png", "Equipment": "assets/processed/Equipment.png",
         "Pets": "assets/processed/Pets.png", "Index": "assets/processed/HudPety/IconIndex.png",
         "Shop": "assets/processed/Shop.png"}
POLE = (0.35, 0.24, 0.615, 0.52)  # pole napisu na przycisku (x, y, szer, wys) — to samo w hud_pety_build_gui.py
GORA_NAPISU = 0.68  # napis leży poniżej tej części wysokości starej ikony


def wytnij(sciezka):
    im = Image.open(ROOT / sciezka).convert("RGBA")
    a = np.array(im).astype(np.int32)
    h, w = a.shape[:2]
    jasnosc = a[..., :3].max(axis=2)
    ciemne = (jasnosc < 70) & (a[..., 3] > 128)
    lab, n = ndimage.label(ciemne, structure=np.ones((3, 3)))
    napis = np.zeros((h, w), bool)
    for i, s in enumerate(ndimage.find_objects(lab), 1):
        y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
        if (x1 - x0) > 0.9 * w or (y1 - y0) > 0.6 * h:
            continue  # obwódka przycisku
        if y0 < GORA_NAPISU * h or (y1 - y0) < 0.04 * h:
            continue  # obrys ikony powyżej napisu albo drobina
        # litera ma w środku jasne wypełnienie; ciemna plama cienia albo rastra (np. pod wózkiem w Shop) — nie
        wyp = ndimage.binary_fill_holes(lab[s] == i)
        if (jasnosc[s][wyp] > 180).mean() < 0.15:
            continue
        napis |= lab == i
    assert napis.any(), sciezka
    pelne = ndimage.binary_fill_holes(napis)
    # Cień albo raster ze starej ikony potrafi skleić się z obrysem skrajnej litery (Shop: plama pod wózkiem przy „S”).
    # Dlatego napis przycinamy do jasnego wypełnienia liter + grubość obrysu (i ciemne „dno” liter od dołu).
    jy, jx = np.where(pelne & (jasnosc > 180))
    brzeg, dno = round(0.02 * h), round(0.055 * h)
    ramka = np.zeros((h, w), bool)
    ramka[max(0, jy.min() - brzeg):jy.max() + dno, max(0, jx.min() - brzeg):jx.max() + brzeg + 1] = True
    napis &= ramka
    pelne = ndimage.binary_fill_holes(napis)
    # oczka liter w kolorze tła przycisku -> przezroczyste
    ys, xs = np.where(pelne)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    okolica = np.zeros((h, w), bool)
    okolica[max(0, y0 - 6):y1 + 4, max(0, x0 - 6):x1 + 6] = True
    tlo = np.median(a[okolica & ~ndimage.binary_dilation(pelne, iterations=3) & (a[..., 3] > 128) & ~ciemne][:, :3], axis=0)
    # Zamknięte obszary: wypełnienie liter zostaje, ciemne „dno” liter zostaje, oczka w kolorze tła przycisku znikają
    # (porównanie: bliżej koloru tła niż koloru wypełnienia liter).
    wyp = np.median(a[pelne & (jasnosc > 180)][:, :3], axis=0)
    wnetrza, m = ndimage.label(pelne & ~napis)
    for i in range(1, m + 1):
        obszar = wnetrza == i
        sr = a[obszar][:, :3].mean(axis=0)
        if sr.max() > 110 and np.abs(sr - tlo).sum() < np.abs(sr - wyp).sum():
            pelne &= ~ndimage.binary_dilation(obszar, iterations=1)
    # drobiny rastra przy brzegu (kropki 1–3 px) i luźne okruchy
    pelne = ndimage.binary_opening(pelne, structure=np.ones((3, 3)))
    okruchy, m = ndimage.label(pelne)
    for i in range(1, m + 1):
        if (okruchy == i).sum() < 0.0008 * h * w:
            pelne &= okruchy != i
    # resztki rastra przy lewym albo prawym brzegu: kolumny, w których napis zajmuje mniej niż 18% swojej wysokości
    ys, xs = np.where(pelne)
    kol = pelne.sum(axis=0)
    dobre = np.where(kol >= 0.18 * (ys.max() + 1 - ys.min()))[0]
    pelne[:, :dobre.min()] = False
    pelne[:, dobre.max() + 1:] = False
    ys, xs = np.where(pelne)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    alfa = ndimage.uniform_filter(np.where(pelne, 255.0, 0.0), 3)
    alfa = np.where(pelne, np.maximum(alfa, 200), np.minimum(alfa, 110))
    out = a.copy()
    out[..., 3] = alfa
    # piksele poza napisem przyciemnij do czerni obrysu, żeby półprzezroczysty brzeg nie miał koloru starego tła
    out[~pelne, :3] = (20, 12, 8)
    return Image.fromarray(out.astype(np.uint8)).crop((x0 - 2, y0 - 2, x1 + 2, y1 + 2))


def main():
    podglady = []
    for nazwa, sciezka in STARE.items():
        n = wytnij(sciezka)
        n.save(OUT / f"HudLabel{nazwa}.png", optimize=True)
        print("ok", f"HudLabel{nazwa}", n.size, "proporcje", round(n.width / n.height, 3))
        b = Image.open(OUT / f"HudWide{nazwa}.png").convert("RGBA")
        x, y, w, h = POLE[0] * b.width, POLE[1] * b.height, POLE[2] * b.width, POLE[3] * b.height
        k = min(w / n.width, h / n.height)
        m = n.resize((round(n.width * k), round(n.height * k)), Image.LANCZOS)
        b.alpha_composite(m, (round(x + (w - m.width) / 2), round(y + (h - m.height) / 2)))
        podglady.append(b)
    odstep = 28
    tlo = Image.new("RGBA", (podglady[0].width + 120, sum(p.height for p in podglady) + 6 * odstep), (58, 92, 64, 255))
    for i, p in enumerate(podglady):
        tlo.alpha_composite(p, (60, odstep + i * (p.height + odstep)))
    tlo = tlo.convert("RGB")
    tlo.thumbnail((700, 1400))
    tlo.save(OUT / "podglad_z_napisami.jpg", quality=90)
    print("ok podglad", tlo.size)


if __name__ == "__main__":
    main()
