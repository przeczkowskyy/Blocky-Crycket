#!/usr/bin/env python3
"""Portrety ras do ramek portretu gracza (Paweł 23.11): HUD, okno ekwipunku, okna sklepów.

Wersja 2 (Paweł 23.11: „kwadratowe głowy jak u nas, tło za sobą i czarne obramowanie, żeby łatwiej się wycięło”):
1. Arkusz assets/raw/RacePortraits/portrety_v3.png — 7 kwadratowych kafelków z czarną ramką i malowanym tłem
   na białej stronie, 4 + 3, kolejność jak w RaceData: Human, Demon, DarkElf, Elf / Orc, Goblin, Demigod.
   Higgsfield (Nano Banana 2.1, 16:9, 4k, job 9b30d4e2-f61b-49bb-a8cb-b96ee1ed59d3 — wersja bardziej kreskówkowa; v2: dfbca51e), referencja: rendery
   modeli ras Karola (głowy i ramiona z swiat/postacie/wynik/rasa_*/..._ikona.png).
2. Każdy kafelek: wykrycie po ciemnym obramowaniu, wycięcie WNĘTRZA (bez czarnej ramki, z małym zapasem),
   kwadrat 512 px -> assets/processed/RacePortraits/Portrait<Id>.png (pełne tło — w grze wypełnia ekran ramki).
3. src/shared/RacePortraits.luau z ID z assets/manifest.json (brak ID = rbxassetid://0).
Wersja 1 (popiersia bez tła z okrągłymi głowami) została zastąpiona — Paweł chciał głów jak w modelach.
Użycie: python tools/raceportraits_assets.py
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "assets/raw/RacePortraits/portrety_v3.png"
OUT = ROOT / "assets/processed/RacePortraits"
KOLEJNOSC = ["Human", "Demon", "DarkElf", "Elf", "Orc", "Goblin", "Demigod"]
ROZMIAR = 512
ZAPAS = 0.012  # dodatkowe cięcie za czarną ramką (ułamek boku), żeby nie został ciemny brzeg


def kafelki(a):
    """Prostokąty 7 kafelków: wszystko, co nie jest białą stroną, w spójnych blokach."""
    tresc = a.min(axis=2) < 225
    tresc = ndimage.binary_closing(tresc, iterations=3)
    lab, n = ndimage.label(ndimage.binary_fill_holes(tresc))
    obiekty = ndimage.find_objects(lab)
    pola = sorted(((s[0].stop - s[0].start) * (s[1].stop - s[1].start), i) for i, s in enumerate(obiekty))
    wybrane = [obiekty[i] for _, i in pola[-7:]]
    srodek_y = a.shape[0] / 2
    gora = sorted((s for s in wybrane if (s[0].start + s[0].stop) / 2 < srodek_y), key=lambda s: s[1].start)
    dol = sorted((s for s in wybrane if (s[0].start + s[0].stop) / 2 >= srodek_y), key=lambda s: s[1].start)
    if len(gora) != 4 or len(dol) != 3:
        raise SystemExit(f"oczekiwany układ 4 + 3, jest {len(gora)} + {len(dol)}")
    return gora + dol


def grubosc_ramki(k):
    """Ile pikseli od krawędzi kafelka zajmuje czarna ramka (mediana z czterech boków)."""
    ciemne = k.max(axis=2) < 70
    h, w = ciemne.shape
    pomiary = []
    for linia in (ciemne[h // 2, :], ciemne[h // 2, ::-1], ciemne[:, w // 2], ciemne[::-1, w // 2]):
        i = 0
        while i < len(linia) // 4 and not linia[i]:
            i += 1  # biały brzeg przed ramką
        while i < len(linia) // 4 and linia[i]:
            i += 1
        pomiary.append(i)
    return int(np.median(pomiary))


RAW_RAMKI = ROOT / "assets/raw/RacePortraits/ramki_v2.png"  # job db82bfd6 — ramka z portretem i pustym paskiem doświadczenia (v1 bez paska: 1d3b8d51)


# Zielony pasek w torze każdej ramki (px obrazka 512 × 556): prostokąty „ExpBar” ułożone w Figmie (plik gry, strona 9:74,
# ramki RaceFrame<Id>) — wnętrze toru do złotego brzegu, zmierzone na grafice, minus 4 px (w grze ok. 1 px).
TOR_FIGMA = {
    "Human": (79, 456, 354, 81), "Demon": (79, 456, 356, 81), "DarkElf": (78, 456, 355, 80), "Elf": (79, 456, 355, 80),
    "Orc": (79, 455, 350, 82), "Goblin": (83, 455, 347, 82), "Demigod": (81, 455, 351, 82),
}


def ramki():
    """Ramki z portretem (Paweł 23.11: „podmienimy całe ramki”): białe tło -> przezroczyste (zalewanie od brzegu),
    7 ramek w układzie 4 + 3 -> assets/processed/RacePortraits/RaceFrame<Id>.png (szerokość 512 px, własne proporcje)."""
    if not RAW_RAMKI.exists():
        return
    a = np.array(Image.open(RAW_RAMKI).convert("RGBA"))
    white = a[..., :3].min(axis=2) > 228
    lab, _ = ndimage.label(white)
    brzeg = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    tlo = np.isin(lab, list(brzeg))
    obwodka = ndimage.binary_dilation(tlo, iterations=1) & ~tlo
    a[..., 3] = np.where(tlo, 0, np.where(obwodka, 140, 255)).astype(np.uint8)
    for nazwa, s in zip(KOLEJNOSC, kafelki(a[..., :3] * (a[..., 3:] > 0) + 255 * (a[..., 3:] == 0))):
        k = Image.fromarray(a[s])
        k = k.crop(Image.fromarray(a[s][..., 3]).getbbox())
        k = k.resize((512, 556), Image.LANCZOS)  # jeden rozmiar dla wszystkich (generator dał 530–556 px wysokości)
        k.save(OUT / f"RaceFrame{nazwa}.png", optimize=True)
        print("ramka", nazwa, k.size)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ramki()
    a = np.array(Image.open(RAW).convert("RGB"))
    for nazwa, s in zip(KOLEJNOSC, kafelki(a)):
        k = a[s]
        g = grubosc_ramki(k)
        h, w = k.shape[:2]
        z = g + round(ZAPAS * min(h, w))
        wnetrze = Image.fromarray(k[z:h - z, z:w - z])
        bok = min(wnetrze.size)
        wnetrze = wnetrze.crop(((wnetrze.width - bok) // 2, wnetrze.height - bok, (wnetrze.width + bok) // 2, wnetrze.height))
        wnetrze.resize((ROZMIAR, ROZMIAR), Image.LANCZOS).save(OUT / f"Portrait{nazwa}.png", optimize=True)
        print("portret", nazwa, f"kafelek {w}×{h}, ramka {g} px")
    man = json.loads((ROOT / "assets/manifest.json").read_text(encoding="utf-8"))["assets"]
    lines = ["-- WYGENEROWANE przez tools/raceportraits_assets.py z assets/manifest.json — nie edytuj ręcznie.",
             "-- Ramki z portretem rasy (RaceFrame<Id>) dla HUD, ekwipunku i sklepów; użycie: Shared.RacePortraitUI.", "return {"]
    for n in KOLEJNOSC:
        rid = man.get(f"RaceFrame{n}", {}).get("roblox_image")  # ramki z portretem (v4)
        lines.append(f'\t{n} = "rbxassetid://{rid or 0}",')
    lines.append("\t-- pasek doświadczenia w torze ramki: {x, y, w, h} jako ułamki obrazka 512 × 556 — z Figmy (prostokąty ExpBar")
    lines.append("\t-- w ramkach RaceFrame<Id>, strona 9:74, Paweł 23.11: „dopasuj w Figmie co do piksela”), 4 px od złota")
    lines.append("\tTor = {")
    for n in KOLEJNOSC:
        x, y, w, h = TOR_FIGMA[n]
        lines.append(f"\t\t{n} = {{ {x / 512:.5f}, {y / 556:.5f}, {w / 512:.5f}, {h / 556:.5f} }},")
    lines.append("\t},")
    lines.append("}")
    (ROOT / "src/shared/RacePortraits.luau").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("ok src/shared/RacePortraits.luau")


if __name__ == "__main__":
    main()
