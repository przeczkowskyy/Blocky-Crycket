#!/usr/bin/env python3
"""Tnie oczyszczony panel ekwipunku na elementy dla Figmy i Roblox.

Wejście:  assets/raw/EquipmentPanel/clean.png (wynik tools/eq_clean_text.py)
Wyjście:  assets/processed/EquipmentPanel/*.png  + assets/processed/EquipmentPanel/layout.json

- EqBg1..EqBg4: tło panelu (bez tekstu) przeskalowane do szer. 2048 i pocięte 2x2
  (Roblox zmniejsza każdy obraz do 1024 px, więc jeden plik byłby rozmyty).
- EqClose, EqPlus, EqTab*: osobne elementy z przezroczystym tłem (segmentacja koloru),
  nakładane dokładnie na swoje miejsce w tle; w Roblox dostają hover / stan aktywny.
- layout.json: pozycje wszystkich elementów (także hotspotów: sloty, mikstury, plecak, teksty)
  w ułamkach rozmiaru panelu (0–1) – wprost do Scale w Roblox i do Figmy.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/raw/EquipmentPanel/final.png"  # tło (po tools/eq_paint.py)
SPRITE_SRC = ROOT / "assets/raw/EquipmentPanel/clean.png"  # elementy (tu jeszcze jest wypalony +)
OUT = ROOT / "assets/processed/EquipmentPanel"
TARGET_W = 2048

# --- elementy z osobną grafiką: nazwa -> (prostokąt w source px, punkt startowy segmentacji, tolerancja, dylatacja obrysu)
SPRITES = {
    "EqClose": ((2518, 86, 2634, 196), (2575, 112), 60, 9),
    "EqPlus": ((476, 1000, 572, 1086), (500, 1016), 70, 7),
    "EqTabAttributes": ((222, 810, 496, 898), (300, 850), 55, 8),
    "EqTabDescription": ((490, 822, 772, 898), (560, 856), 55, 8),
    "EqTabInfo": ((774, 822, 1022, 898), (850, 856), 55, 8),
    "EqTabInteractions": ((1018, 822, 1326, 898), (1100, 856), 55, 8),
    "EqTabWeapons": ((1458, 246, 1732, 338), (1530, 290), 55, 8),
    "EqTabArmor": ((1728, 254, 1992, 338), (1800, 290), 55, 8),
    "EqTabAmulets": ((1988, 254, 2262, 338), (2060, 290), 55, 8),
    "EqTabOthers": ((2256, 254, 2528, 338), (2330, 290), 55, 8),
}

# przyciski + na kartach (grafika EqPlus, natywnie mniejsza): 27 px od prawego obrysu karty, 64x57 px
PLUS_W, PLUS_H, PLUS_RIGHT_GAP, PLUS_TOP = 64, 57, 27, 1011
CARD_DY = [0, 185]
PLUS_KEYS = ["Strength", "Constitution", "Intelligence", "Dexterity", "Luck", "Armor"]

# hotspoty (bez własnej grafiki) w source px
SLOTS = {
    "Helmet": (330, 245, 465, 372), "Chest": (330, 385, 465, 510),
    "Gloves": (330, 522, 465, 647), "Boots": (330, 660, 465, 787),
    "Amulet": (1080, 245, 1215, 372), "Belt": (1080, 385, 1215, 510),
    "Ring": (1080, 522, 1215, 647), "Trinket": (1080, 660, 1215, 787),
    "Weapon": (705, 635, 849, 779),
}
COVER_INSET = 0.10  # zasłonka sylwetki w slocie: wnętrze slotu = 10% od krawędzi hotspotu
PORTRAIT = (642, 260, 920, 516)
LEVEL_BADGE = (668, 532, 890, 596)
POTIONS = {"Potion1": (570, 1390), "Potion2": (767, 1390), "Potion3": (965, 1390)}
POTION_R = 66  # wnętrze złotego pierścienia (obrys hover 3 px leży na pierścieniu)

# teksty natywne (source px): nazwa -> (prostokąt, tekst, wyrównanie, rola)
CARD_COLS = [(229, 580), (591, 952), (963, 1315)]  # zewnętrzny obrys kart (351 / 361 / 352 px)
CARD_ROWS = [(925, 1085), (1110, 1270)]
CARD_ICON_W = [76, 76, 76]
STATS = [("Strength", "STR", "DMG ~12", "20"), ("Constitution", "CONST", "HP 192", "16"),
         ("Intelligence", "INT", "DEF 9", "18"), ("Dexterity", "DEX", "DEF 6", "12"),
         ("Luck", "LUCK", "CRIT 8.75%", "7"), ("Armor", "ARMOR", "DMG RED 25%", "57")]


def segment(arr, rect, seed, tol, grow):
    x0, y0, x1, y1 = rect
    crop = arr[y0:y1, x0:x1, :3].astype(np.int32)
    sx, sy = seed[0] - x0, seed[1] - y0
    ref = crop[sy, sx]
    sim = np.abs(crop - ref).sum(-1) < tol * 3
    lab, _ = ndimage.label(sim)
    body = lab == lab[sy, sx]
    body = ndimage.binary_fill_holes(body)
    body = ndimage.binary_closing(body, iterations=4)
    body = ndimage.binary_fill_holes(body)
    mask = ndimage.binary_dilation(body, iterations=grow)  # obrys
    alpha = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    rgba = Image.fromarray(arr[y0:y1, x0:x1, :3].astype(np.uint8)).convert("RGBA")
    rgba.putalpha(alpha)
    return rgba


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    im = Image.open(SRC).convert("RGBA")
    arr = np.array(im)
    sprite_arr = np.array(Image.open(SPRITE_SRC).convert("RGBA"))

    # tło poza ramką -> przezroczyste (flood fill bieli od krawędzi)
    rgb = arr[..., :3].astype(np.int32)
    white = (rgb.min(-1) > 236)
    lab, _ = ndimage.label(white)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    outside = np.isin(lab, list(border))
    outside = ndimage.binary_dilation(outside, iterations=1)
    arr[..., 3] = np.where(outside, 0, 255).astype(np.uint8)
    ys, xs = np.nonzero(arr[..., 3])
    bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    PW, PH = bx1 - bx0, by1 - by0

    def norm(r):
        x0, y0, x1, y1 = r
        return [round((x0 - bx0) / PW, 5), round((y0 - by0) / PH, 5), round((x1 - x0) / PW, 5), round((y1 - y0) / PH, 5)]

    panel = Image.fromarray(arr).crop((bx0, by0, bx1, by1))
    scale = TARGET_W / PW
    TH = round(PH * scale)
    TH += TH % 2
    panel_s = panel.resize((TARGET_W, TH), Image.LANCZOS)
    hw, hh = TARGET_W // 2, TH // 2
    tiles = {}
    for i, (cx, cy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)], 1):
        name = f"EqBg{i}"
        panel_s.crop((cx * hw, cy * hh, (cx + 1) * hw, (cy + 1) * hh)).save(OUT / f"{name}.png")
        tiles[name] = [cx * 0.5, cy * 0.5, 0.5, 0.5]

    sprites = {}
    for name, (rect, seed, tol, grow) in SPRITES.items():
        img = segment(sprite_arr, rect, seed, tol, grow)
        img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)
        img.save(OUT / f"{name}.png")
        sprites[name] = norm(rect)

    plus = {}
    for i, k in enumerate(PLUS_KEYS):
        right, dy = CARD_COLS[i % 3][1], CARD_DY[i // 3]
        x1 = right - PLUS_RIGHT_GAP
        plus[k] = norm((x1 - PLUS_W, PLUS_TOP + dy, x1, PLUS_TOP + PLUS_H + dy))

    # sloty plecaka: wykrywanie niebieskich kafelków
    hsvlike = rgb
    blue = (hsvlike[..., 2] > 150) & (hsvlike[..., 2] - hsvlike[..., 0] > 70)
    blue[:, :1380] = False
    blue[:380] = False
    blue = ndimage.binary_opening(blue, iterations=3)
    lab, n = ndimage.label(blue)
    boxes = []
    for sl in ndimage.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if 120 < w < 260 and 120 < h < 260:
            boxes.append((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop))
    boxes.sort(key=lambda b: (round(b[1] / 60), b[0]))
    backpack = [norm(b) for b in boxes]

    texts = {
        "TitleCharacter": [norm((540, 88, 1010, 182)), "CHARACTER", "Center", "title"],
        "TitleBackpack": [norm((1770, 88, 2205, 182)), "BACKPACK", "Center", "title"],
        "LevelText": [norm((700, 536, 860, 592)), "LV 2", "Center", "level"],
    }
    for name, (r, label) in {
        "TabAttributes": ((240, 838, 485, 890), "ATTRIBUTES"), "TabDescription": ((505, 838, 760, 890), "DESCRIPTION"),
        "TabInfo": ((790, 838, 1010, 890), "INFO"), "TabInteractions": ((1030, 838, 1310, 890), "INTERACTIONS"),
        "TabWeapons": ((1478, 268, 1716, 322), "WEAPONS"), "TabArmor": ((1748, 268, 1972, 322), "ARMOR"),
        "TabAmulets": ((2008, 268, 2242, 322), "AMULETS"), "TabOthers": ((2272, 268, 2508, 322), "OTHERS"),
    }.items():
        # wyśrodkuj napis na KOLOROWEJ części zakładki (obrazek ma niesymetryczny obrys/cień, np. OTHERS)
        sx0, _, sx1, _ = SPRITES["Eq" + name][0]
        spr = np.array(Image.open(OUT / f"Eq{name}.png").convert("RGBA")).astype(int)
        body = (spr[..., 3] > 128) & ((spr[..., :3].max(-1) - spr[..., :3].min(-1)) > 40) & (spr[..., :3].max(-1) > 90)
        ys, _ = np.nonzero(body)
        row = np.nonzero(body[int(np.median(ys))])[0]
        frac = (row.min() + row.max()) / 2 / spr.shape[1]
        cx = sx0 + frac * (sx1 - sx0)
        half = (r[2] - r[0]) / 2
        r = (cx - half, r[1], cx + half, r[3])
        texts[name + "Label"] = [norm(r), label, "Center", "tab"]

    cards = {}
    for i, (key, nm, sub, val) in enumerate(STATS):
        (cx0, cx1), (cy0, cy1) = CARD_COLS[i % 3], CARD_ROWS[i // 3]
        name_r = (cx0 + CARD_ICON_W[i % 3] + 8, cy0 + 22, cx1 - 100, cy0 + 72)
        val_r = (cx1 - 100, cy0 + 22, cx1 - 22, cy0 + 72)
        sub_r = (cx0 + 26, cy0 + 96, cx1 - 97, cy0 + 138)  # od wewn. obrysu do przycisku „+” (zapas na „DMG RED 25%”)
        cards[key] = {"card": norm((cx0, cy0, cx1, cy1)), "name": [norm(name_r), nm], "value": [norm(val_r), val],
                      "sub": [norm(sub_r), sub], "plus": plus[key]}

    # zasłonki sylwetek (hełm, sakiewka…) pod ikoną przedmiotu: dokładne wnętrze slotu (od wewnętrznej krawędzi
    # ciemnego obrysu) + dwa kolory: faz (ciemniejszy pas przy obrysie) i środek. Mierzone w oryginale (source.png).
    orig = np.array(Image.open(ROOT / "assets/raw/EquipmentPanel/source.png").convert("RGB")).astype(np.int32)
    lum = orig.sum(-1)

    def edge_in(line):
        """Indeks pierwszego piksela wnętrza: za jasnym obrzeżem i ciemnym obrysem."""
        i, n = 0, len(line)
        while i < n and line[i] < 400:  # do jasnego obrzeża
            i += 1
        while i < n and line[i] >= 100:  # obrzeże
            i += 1
        while i < n and line[i] < 180:  # ciemny obrys
            i += 1
        return i

    hexc = lambda c: "%02X%02X%02X" % tuple(int(v) for v in c)
    covers = {}
    for k, (x0, y0, x1, y1) in SLOTS.items():
        cx, cy, m = (x0 + x1) // 2, (y0 + y1) // 2, 14
        L = x0 - m + edge_in(lum[cy, x0 - m:cx])
        R = x1 + m - edge_in(lum[cy, cx:x1 + m][::-1])
        T = y0 - m + edge_in(lum[y0 - m:cy, cx])
        B = y1 + m - edge_in(lum[cy:y1 + m, cx][::-1])
        w, h = x1 - x0, y1 - y0
        bevel = np.concatenate([orig[cy - 20:cy + 20, L + 1:L + 4].reshape(-1, 3), orig[cy - 20:cy + 20, R - 4:R - 1].reshape(-1, 3)])
        base = np.concatenate([orig[cy - 20:cy + 20, L + 10:L + 16].reshape(-1, 3), orig[cy - 20:cy + 20, R - 16:R - 10].reshape(-1, 3)])
        covers[k] = {"rect": [round((L - x0) / w, 4), round((T - y0) / h, 4), round((R - L) / w, 4), round((B - T) / h, 4)],
                     "bevel_px": 6, "size_px": [int(R - L), int(B - T)],
                     "bevel": np.median(bevel, 0), "base": np.median(base, 0)}
    # kolory wspólne dla wszystkich slotów (mediana) – pojedynczy slot może złapać sylwetkę (np. pas przez całą szerokość)
    gb = np.median([c["bevel"] for c in covers.values()], 0)
    gm = np.median([c["base"] for c in covers.values()], 0)
    for c in covers.values():
        c["bevel"], c["base"] = hexc(gb), hexc(gm)

    layout = {
        "source_px": [int(PW), int(PH)], "aspect": round(PW / PH, 5), "bg_tiles": tiles, "sprites": sprites,
        "slots": {k: norm(v) for k, v in SLOTS.items()}, "slot_covers": covers, "portrait": norm(PORTRAIT), "level_badge": norm(LEVEL_BADGE),
        "potions": {k: norm((x - POTION_R, y - POTION_R, x + POTION_R, y + POTION_R)) for k, (x, y) in POTIONS.items()},
        "backpack": backpack, "texts": texts, "cards": cards,
    }
    (OUT / "layout.json").write_text(json.dumps(layout, indent=1), encoding="utf-8")
    print(f"panel {PW}x{PH} -> {TARGET_W}x{TH}; backpack slots: {len(backpack)}; sprites: {len(sprites)}")


if __name__ == "__main__":
    main()
