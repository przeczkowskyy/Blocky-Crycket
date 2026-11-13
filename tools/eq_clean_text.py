#!/usr/bin/env python3
"""Usuwa wypalony tekst z grafiki panelu ekwipunku (assets/raw/EquipmentPanel/source.png).

Tekst trafia potem natywnie do Roblox (Luckiest Guy), więc obraz tła musi być bez napisów.
Metoda: w każdym prostokącie wykrywamy piksele tekstu (kolor + obrys przez dylatację),
a następnie wypełniamy je wiersz po wierszu interpolacją liniową między pikselami tła
po lewej i prawej stronie (zakładki, karty i tabliczki mają poziomo jednolite tło).

Użycie: python tools/eq_clean_text.py IN.png OUT.png [MASK_DEBUG.png]
"""
import sys

import numpy as np
from PIL import Image, ImageFilter

# (nazwa, (x0, y0, x1, y1), reguła maski, dylatacja px) — współrzędne w pikselach source.png (2752x1536)
REGIONS = [
    # tabliczki tytułów: kremowy tekst na drewnie
    ("TitleCharacter", (515, 80, 1035, 194), "cream", 7),
    ("TitleBackpack", (1750, 80, 2225, 194), "cream", 7),
    # zakładki lewe (białe napisy)
    ("TabAttributes", (240, 836, 485, 892), "white", 6),
    ("TabDescription", (505, 836, 760, 892), "white", 6),
    ("TabInfo", (790, 836, 1010, 892), "white", 6),
    ("TabInteractions", (1030, 836, 1310, 892), "white", 6),
    # zakładki prawe
    ("TabWeapons", (1475, 266, 1720, 324), "white", 6),
    ("TabArmor", (1745, 266, 1975, 324), "white", 6),
    ("TabAmulets", (2005, 266, 2245, 324), "white", 6),
    ("TabOthers", (2270, 266, 2510, 324), "white", 6),
    # karty statystyk: górny pasek (granat) — nazwa + wartość, bez ikony
    ("Card1Top", (306, 943, 568, 996), "bright", 4),
    ("Card2Top", (676, 943, 940, 996), "bright", 4),
    ("Card3Top", (1042, 943, 1300, 996), "bright", 4),
    ("Card4Top", (306, 1129, 568, 1184), "bright", 4),
    ("Card5Top", (676, 1129, 940, 1184), "bright", 4),
    ("Card6Top", (1042, 1129, 1300, 1184), "bright", 4),
    # karty statystyk: dolny pasek (beż) — ciemny tekst, bez przycisku +
    ("Card1Bottom", (242, 1016, 478, 1070), "dark", 3),
    ("Card2Bottom", (612, 1016, 848, 1070), "dark", 3),
    ("Card3Bottom", (978, 1016, 1214, 1070), "dark", 3),
    ("Card4Bottom", (242, 1198, 478, 1254), "dark", 3),
    ("Card5Bottom", (612, 1198, 848, 1254), "dark", 3),
    ("Card6Bottom", (978, 1198, 1214, 1254), "dark", 3),
    # plakietka poziomu
    ("LevelBadge", (700, 530, 858, 596), "pale", 6, "copyleft"),
]


def hsv(arr):
    rgb = arr[..., :3].astype(np.float32) / 255.0
    mx = rgb.max(-1)
    mn = rgb.min(-1)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    return s, mx


def text_mask(crop, rule):
    s, v = hsv(crop)
    if rule == "cream":
        m = (v > 0.80) & (s < 0.55)
    elif rule == "white":
        m = (v > 0.78) & (s < 0.28)
    elif rule == "bright":  # wszystko jasne na ciemnym granacie (białe nazwy, żółte liczby)
        m = v > 0.45
    elif rule == "dark":  # ciemny tekst na beżu
        m = v < 0.55
    elif rule == "pale":  # jasnozielony tekst na zielonej plakietce
        m = (v > 0.70) & (s < 0.55)
    else:
        raise ValueError(rule)
    return m


def bbox_dark(crop, base, pad_x, pad_y, thr):
    """Ciemny obrys/cień liter: ciemne piksele tylko w obrębie bboxa jasnego tekstu (+margines)."""
    ys, xs = np.nonzero(base)
    out = np.zeros_like(base)
    if ys.size == 0:
        return out
    _, v = hsv(crop)
    y0, y1 = max(ys.min() - pad_y, 0), min(ys.max() + pad_y + 1, base.shape[0])
    x0, x1 = max(xs.min() - pad_x, 0), min(xs.max() + pad_x + 1, base.shape[1])
    out[y0:y1, x0:x1] = v[y0:y1, x0:x1] < thr
    return out


def dilate(mask, r):
    img = Image.fromarray((mask * 255).astype(np.uint8))
    img = img.filter(ImageFilter.MaxFilter(2 * r + 1))
    return np.array(img) > 127


def fill_cols(arr, mask, box):
    """Jak fill_rows, ale pionowo (dla elementów dwukolorowych w poziomie)."""
    x0, y0, x1, y1 = box
    sub = arr[y0:y1, x0:x1].transpose(1, 0, 2).copy()
    fill_rows_arr(sub, mask.T)
    arr[y0:y1, x0:x1] = sub.transpose(1, 0, 2)


def fill_rows_arr(sub, mask):
    # sub: wycinek z 1 px marginesem nieobecnym, endpointy brane z brzegu wycinka
    H, W = mask.shape
    for yy in range(H):
        row = mask[yy]
        xx = 0
        while xx < W:
            if not row[xx]:
                xx += 1
                continue
            start = xx
            while xx < W and row[xx]:
                xx += 1
            end = xx
            a = sub[yy, max(start - 1, 0)].astype(np.float32)
            b = sub[yy, min(end, W - 1)].astype(np.float32)
            n = end - start
            t = (np.arange(1, n + 1, dtype=np.float32) / (n + 1))[:, None]
            sub[yy, start:end] = (a * (1 - t) + b * t).astype(np.uint8)


def fill_rows(arr, mask, box):
    x0, y0, x1, y1 = box
    W = arr.shape[1]
    for yy in range(y1 - y0):
        row = mask[yy]
        xx = 0
        while xx < row.size:
            if not row[xx]:
                xx += 1
                continue
            start = xx
            while xx < row.size and row[xx]:
                xx += 1
            end = xx  # exclusive
            lx = max(x0 + start - 1, 0)
            rx = min(x0 + end, W - 1)
            a = arr[y0 + yy, lx].astype(np.float32)
            b = arr[y0 + yy, rx].astype(np.float32)
            n = end - start
            t = (np.arange(1, n + 1, dtype=np.float32) / (n + 1))[:, None]
            arr[y0 + yy, x0 + start:x0 + end] = (a * (1 - t) + b * t).astype(np.uint8)


def main():
    src, out = sys.argv[1], sys.argv[2]
    dbg = sys.argv[3] if len(sys.argv) > 3 else None
    im = Image.open(src).convert("RGBA")
    arr = np.array(im)
    full_mask = np.zeros(arr.shape[:2], bool)
    for name, box, rule, r, *mode in REGIONS:
        x0, y0, x1, y1 = box
        crop = arr[y0:y1, x0:x1]
        base = text_mask(crop, rule)
        m = dilate(base, r)
        if rule == "cream":  # obrys + cień pod literami
            m |= dilate(bbox_dark(crop, base, 6, 14, 0.42), 2)
        elif rule == "white":
            m |= dilate(bbox_dark(crop, base, 3, 8, 0.45), 2)
        if mode and mode[0] == "copyleft":  # wypełnij kolorem czystego piksela z lewej (gradient pionowy zostaje)
            for yy in range(y1 - y0):
                cols = np.nonzero(m[yy])[0]
                if cols.size:
                    arr[y0 + yy, x0 + cols] = arr[y0 + yy, x0 - 1]
        elif mode and mode[0] == "cols":
            fill_cols(arr, m, box)
        else:
            fill_rows(arr, m, box)
        full_mask[y0:y1, x0:x1] |= m
    # lekkie pionowe wygładzenie tylko w wypełnionych miejscach (usuwa poziome smugi)
    blurred = np.array(Image.fromarray(arr).filter(ImageFilter.BoxBlur(2)))
    arr = np.where(full_mask[..., None], blurred, arr)
    Image.fromarray(arr).save(out)
    if dbg:
        Image.fromarray((full_mask * 255).astype(np.uint8)).save(dbg)
    print("ok", out)


if __name__ == "__main__":
    main()
