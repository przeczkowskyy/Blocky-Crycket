#!/usr/bin/env python3
"""Usuwa zakładki wypalone w tle okna ekwipunku i odbudowuje to miejsce z czystych kawałków tej samej grafiki
(Paweł 23–24.11: animacja przycisków; ATTRIBUTES najeżdżało na ramkę; bez rozmazań, bez uciętego rogu ramki).

Zakładki postaci (ATTRIBUTES, DESCRIPTION, INFO, INTERACTIONS) i plecaka (WEAPONS, ARMOR, AMULETS, OTHERS) były
w tle jako kolorowe kształty; na nich leżą osobne przyciski (EqTab*.png), które teraz się animują. Odbudowa:
1. ŚCIANA: cały kształt każdej zakładki (poszerzony o kilka px) znika aż do górnego brzegu ramki pod nią; deski ściany
   są pionowe, więc każda kolumna dostaje kolor piksela tuż nad zakładką (deski biegną dalej, bez rozmazań).
2. BRZEG RAMKI: pas od górnej czarnej linii w dół wklejony na całej długości z czystego wzorca (spod DESCRIPTION
   / ARMOR, gdzie brzeg ma prawidłowy wygląd), kolumny powtarzane — jeden równy brzeg bez pomarańczu po starych
   ATTRIBUTES / WEAPONS.
3. LEWY RÓG RAMKI: lustrzane odbicie czystego prawego rogu tej samej ramki (tylko piksele ramki w obrębie łuku).

Wejście: kopie oryginałów assets/raw/EquipmentPanel/EqBg<n>_z_zakladkami.png (n = 2, 3, 4) + EqBg1.png.
Wyjście: assets/processed/EquipmentPanel/EqBg2.png, EqBg3.png, EqBg4.png (przezroczystość bez zmian) + podgląd JPG.
Użycie: python tools/eq_wymaz_zakladki.py
"""
import shutil
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "assets/processed/EquipmentPanel"
RAW = ROOT / "assets/raw/EquipmentPanel"
KAFEL = 0.5008  # każdy kafelek EqBg zajmuje 0,5008 × 0,5008 okna
W, H = 1024 / KAFEL, 583 / KAFEL  # px okna w skali kafelków (2047 × 1166)
POZ = {1: (0, 0), 2: (0.5, 0), 3: (0, 0.5), 4: (0.5, 0.5)}
POSZERZ = 4  # px poszerzenia kształtu zakładki (obrys i miękki brzeg kopii w tle)

# Pierwotne położenie zakładek wypalonych w tle (px okna) i obrazek z ich kształtem.
ZAKLADKI = [
    ("Attributes", 93, 602, 221, 71), ("Description", 308, 612, 227, 61), ("Info", 537, 612, 200, 61),
    ("Interactions", 733, 612, 248, 61), ("Weapons", 1088, 148, 221, 74), ("Armor", 1305, 155, 213, 68),
    ("Amulets", 1514, 155, 221, 68), ("Others", 1730, 155, 219, 68),
]
# Ramki pod zakładkami (px okna): gora = pierwszy wiersz górnej czarnej linii ramki (tu kończy się wymazywanie),
# pas = wysokość odbudowywanego brzegu, wzor = kolumny czystego brzegu (powtarzane), lewa/prawa = zewnętrzne
# krawędzie ramki, promien = promień zaokrąglenia rogu.
RAMKI = {
    "statystyki": {"gora": 670, "pas": 24, "wzor": (420, 520), "lewa": 70, "prawa": 1004, "promien": 30},
    "plecak": {"gora": 216, "pas": 24, "wzor": (1400, 1500), "lewa": 1073, "prawa": 1962, "promien": 30},
}
RAMKA_ZAKLADKI = {"Attributes": "statystyki", "Description": "statystyki", "Info": "statystyki", "Interactions": "statystyki",
                  "Weapons": "plecak", "Armor": "plecak", "Amulets": "plecak", "Others": "plecak"}


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    zrodla = {}
    for i in (2, 3, 4):
        kopia = RAW / f"EqBg{i}_z_zakladkami.png"
        if not kopia.exists():
            shutil.copy(P / f"EqBg{i}.png", kopia)
        zrodla[i] = Image.open(kopia).convert("RGBA")
    zrodla[1] = Image.open(P / "EqBg1.png").convert("RGBA")
    full = Image.new("RGBA", (round(W) + 2, round(H) + 2), (0, 0, 0, 0))
    for i, (fx, fy) in POZ.items():
        full.paste(zrodla[i], (round(fx * W), round(fy * H)))
    a = np.array(full).astype(float)
    wynik = a.copy()

    # 1. ściana: zakładki znikają do górnego brzegu ramki, kolumny = kolor piksela tuż nad zakładką
    for nazwa, x0, y0, sw, sh in ZAKLADKI:
        r = RAMKI[RAMKA_ZAKLADKI[nazwa]]
        spr = Image.open(P / f"EqTab{nazwa}.png").convert("RGBA")
        alfa = np.array(spr.resize((sw, sh), Image.LANCZOS))[..., 3] > 40
        m = np.zeros(a.shape[:2], bool)
        m[y0:y0 + sh, x0:x0 + sw] = alfa
        m = ndimage.binary_dilation(m, iterations=POSZERZ)
        m[r["gora"]:] = False
        for x in np.where(m.any(axis=0))[0]:
            kol = np.where(m[:, x])[0]
            wynik[kol.min():kol.max() + 1, x, :3] = a[kol.min() - 1, x, :3]
        print("zakładka", nazwa)

    # 2–3. brzeg ramki: prosty pas z wzorca, lewy róg = lustrzane odbicie prawego
    for nazwa, r in RAMKI.items():
        g, pas, (w0, w1), L, Rr, rad = r["gora"], r["pas"], r["wzor"], r["lewa"], r["prawa"], r["promien"]
        wzorzec = a[g:g + pas, w0:w1, :3].copy()
        for x in range(L + rad, Rr - rad + 1):
            wynik[g:g + pas, x, :3] = wzorzec[:, (x - L) % (w1 - w0)]
        cx, cy = Rr - rad, g + rad
        DL, PRZEJSCIE = 45, 30  # odbicie sięga 45 px za łuk; ostatnie 30 px płynnie przechodzi we wzorzec
        for y in range(g - 2, g + pas + rad):
            for x in range(Rr - rad - DL, Rr + 1):  # tylko do zewnętrznej krawędzi ramki (dalej jest kominek)
                xl = L + (Rr - x)
                if y < g and x <= cx:
                    continue  # nad prostym brzegiem po prawej leży dół fioletowej zakładki — tu zostaje ściana
                if y >= g + pas and x < Rr - pas:
                    continue  # niżej tylko pionowy brzeg ramki — wnętrze (karty statystyk / sloty) zostaje swoje
                wewn = x <= cx or y >= cy or (x - cx) ** 2 + (y - cy) ** 2 <= (rad + 2) ** 2
                if not wewn:
                    # poza łukiem: ściana (kolor znad rogu), żeby nie został kawałek starego, innego łuku
                    wynik[y, xl, :3] = wynik[g - 6, xl, :3]
                    continue
                odb = a[y, x, :3]
                odl = xl - (L + rad + DL - PRZEJSCIE)  # > 0: strefa przejścia w prosty brzeg
                if odl > 0 and g <= y < g + pas:
                    w = min(odl / PRZEJSCIE, 1)
                    wynik[y, xl, :3] = (1 - w) * odb + w * wynik[y, xl, :3]
                else:
                    wynik[y, xl, :3] = odb
        print("ramka", nazwa)

    wynik[..., 3] = a[..., 3]  # przezroczystość bez zmian
    out = Image.fromarray(wynik.clip(0, 255).astype(np.uint8), "RGBA")
    for i in (2, 3, 4):
        fx, fy = POZ[i]
        x0, y0 = round(fx * W), round(fy * H)
        out.crop((x0, y0, x0 + 1024, y0 + 583)).save(P / f"EqBg{i}.png", optimize=True)
        print("ok", f"EqBg{i}.png")
    out.convert("RGB").save(P / "podglad_bez_zakladek.jpg", quality=88)


if __name__ == "__main__":
    main()
