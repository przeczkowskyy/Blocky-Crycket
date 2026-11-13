#!/usr/bin/env python3
"""Poprawki grafiki panelu ekwipunku (po tools/eq_clean_text.py, przed tools/eq_slice.py).

clean.png (+ source.png do próbkowania) -> final.png:
1. Karty statystyk, granatowy pasek nazwy: czyste wypełnienie (kolumna próbkowana tuż za ikoną, powielona w poziomie),
   bez resztek cienia usuniętych liter.
2. Karty statystyk, dół: beżowa część przedłużona na całą szerokość karty (wypalony „+” usunięty – w Roblox jest
   natywny), prawa krawędź z zaokrąglonym rogiem = lustrzane odbicie lewej, więc kolory nie wchodzą na ramkę.
3. Mikstury: flaszka z 2. slotu skopiowana do 1.

Użycie: python tools/eq_paint.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC_CLEAN = ROOT / "assets/raw/EquipmentPanel/clean.png"
SRC_ORIG = ROOT / "assets/raw/EquipmentPanel/source.png"
OUT = ROOT / "assets/raw/EquipmentPanel/final.png"

# karty mają różne szerokości (351 / 361 / 369 px), więc każda kolumna ma własne granice:
# (lewa, prawa) = zewnętrzny obrys karty zmierzony w source.png (-3 / +4 px marginesu, symetrycznie)
CARD_COLS = [(226, 584), (588, 956), (960, 1319)]  # kol. 3 kończy się na 1315 (1328–1332 to ramka panelu, nie karty)
CARD_TOP = 922
CARD_DY = [0, 185]
BAND_ROWS = (928, 1002)  # granatowy pasek nazwy (z obrysem)
# prawa krawędź karty dla każdej kolumny:
#  ("mirror", źródło_lewej_krawędzi_paska, szerokość) – odbicie lewej krawędzi (kol. 1: krawędź paska z CONST/LUCK,
#     bo miecz/but stoją za blisko krawędzi; kol. 2 własna),
#  ("orig", None, szerokość) – prawdziwa prawa krawędź z oryginału (kol. 3: karty szersze i niesymetryczne,
#     a ostatnie 30 px oryginału jest czyste – bez „+” i tekstu).
RIGHT_EDGE = [("mirror", 588, 24), ("mirror", 588, 24), ("mirror", 588, 24)]
BOTTOM_ROWS = (1000, 1092)  # dolna część karty: beż + obrys + obrzeże
EDGE_W = 30  # lewa krawędź karty z ORYGINAŁU (obrys, obrzeże, wewnętrzny obrys, kawałek beżu), odbijana na prawo
BEIGE_COL_X = 26  # kolumna czystego beżu w oryginale (tekst zaczyna się ~32 px od krawędzi)
POTION_SRC, POTION_DST, POTION_R = (767, 1390), (570, 1390), 64


def navy_like(px):
    """Granat paska: niebieski dominuje, ciemny. Odrzuca biały/żółty tekst, czarny cień i kolorowe ikony."""
    r, g, b = px[..., 0].astype(int), px[..., 1].astype(int), px[..., 2].astype(int)
    mx = np.maximum(np.maximum(r, g), b)
    return (b >= r + 8) & (b >= g + 2) & (mx < 110) & (mx >= 40)  # >=40: bez czarnego cienia liter


def icon_end(orig, x_from, x_to, y0, y1):
    """Pierwsza kolumna za ikoną, w której ≥90% pikseli paska to czysty granat."""
    for x in range(x_from, x_to):
        if navy_like(orig[y0 + 14:y1 - 10, x, :3]).mean() >= 0.9:
            return x
    return x_to


def main():
    clean = np.array(Image.open(SRC_CLEAN).convert("RGBA"))
    orig = np.array(Image.open(SRC_ORIG).convert("RGBA"))
    out = clean.copy()

    for dy in CARD_DY:
        for (l, r), (mode, edge_l, edge_w) in zip(CARD_COLS, RIGHT_EDGE):
            t = CARD_TOP + dy
            # 1) pasek nazwy
            by0, by1 = BAND_ROWS[0] + dy, BAND_ROWS[1] + dy
            cx = icon_end(orig, l + 55, l + 125, by0, by1) + 2
            x1 = r - edge_w
            seg = orig[by0:by1, cx:x1, :]
            ok = navy_like(seg[..., :3])
            H = by1 - by0
            meds = [None] * H
            for yy in range(H):
                if ok[yy].mean() > 0.10:  # mediana czystego granatu w wierszu
                    meds[yy] = np.median(seg[yy][ok[yy]], axis=0)
            valid = [i for i, m in enumerate(meds) if m is not None]
            if valid:
                for yy in range(valid[0], valid[-1] + 1):  # braki (wiersze z literami): interpolacja w pionie
                    if meds[yy] is None:
                        a = max(i for i in valid if i < yy)
                        c = min(i for i in valid if i > yy)
                        w = (yy - a) / (c - a)
                        meds[yy] = meds[a] * (1 - w) + meds[c] * w
                    out[by0 + yy, cx:x1] = meds[yy].astype(np.uint8)
            if mode == "mirror":
                out[t:by1, r - edge_w:r] = orig[t:by1, edge_l:edge_l + edge_w, :][:, ::-1, :]
            else:
                out[t:by1, r - edge_w:r] = orig[t:by1, r - edge_w:r, :]
            # 2) dół karty: beż na całą szerokość, prawa krawędź = odbicie lewej
            ry0, ry1 = BOTTOM_ROWS[0] + dy, BOTTOM_ROWS[1] + dy
            beige = orig[ry0:ry1, l + BEIGE_COL_X, :].copy()
            out[ry0:ry1, l + EDGE_W:r - EDGE_W] = beige[:, None, :]
            left_edge = orig[ry0:ry1, l:l + EDGE_W, :]
            out[ry0:ry1, l:l + EDGE_W] = left_edge  # clean.png miał tu wymazany obrys (czyszczenie tekstu)
            if mode == "mirror":
                out[ry0:ry1, r - EDGE_W:r] = left_edge[:, ::-1, :]
            else:
                out[ry0:ry1, r - EDGE_W:r] = orig[ry0:ry1, r - EDGE_W:r, :]

    im = Image.fromarray(out)
    # 3) mikstura: kopia wnętrza slotu 2 -> slot 1 (miękka krawędź)
    sx, sy = POTION_SRC
    tx, ty = POTION_DST
    rr = POTION_R
    patch = im.crop((sx - rr, sy - rr, sx + rr, sy + rr))
    m = Image.new("L", (2 * rr, 2 * rr), 0)
    ImageDraw.Draw(m).ellipse([3, 3, 2 * rr - 3, 2 * rr - 3], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(2))
    im.paste(patch, (tx - rr, ty - rr), m)

    im.save(OUT)
    print("ok", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
