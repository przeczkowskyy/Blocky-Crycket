#!/usr/bin/env python3
"""Grafiki ekranu wyboru rasy (D-079, polecenie Pawła 17.11).

1. Ikony ras: arkusz 3 × 2 okrągłych przycisków (assets/raw/RaceSelect/ikony_v1.png) + osobny emblemat Półboga
   (assets/raw/RaceSelect/polbog_v1.png) -> assets/processed/RaceSelect/Race<Id>.png (białe tło przezroczyste,
   przycięte do koła, 512 px).
2. Rzuty ras dla modelarza (Karol): assets/raw/RaceTurnarounds/<rasa>_v1.png -> assets/processed/RaceTurnarounds/<rasa>.jpg
   (2400 px szerokości, do podglądu i do Blendera jako tło referencyjne).
3. src/shared/RaceIcons.luau z ID z assets/manifest.json (brak ID = rbxassetid://0).

Użycie: python tools/raceselect_assets.py
"""
import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "assets/raw/RaceSelect", ROOT / "assets/processed/RaceSelect"
TRAW, TOUT = ROOT / "assets/raw/RaceTurnarounds", ROOT / "assets/processed/RaceTurnarounds"
SHEET_ORDER = ["Human", "Demon", "DarkElf", "Elf", "Orc", "Goblin"]   # kolejność w arkuszu (rzędami)
ALL = SHEET_ORDER + ["Demigod"]


def bez_tla(im):
    """Białe tło połączone z brzegiem obrazu -> przezroczyste; przycięcie do treści."""
    a = np.array(im.convert("RGBA"))
    white = a[..., :3].min(axis=2) > 232
    h, w = white.shape
    seen = np.zeros_like(white)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if white[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if white[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and white[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((ny, nx))
    a[..., 3] = np.where(seen, 0, 255).astype(np.uint8)
    out = Image.fromarray(a)
    return out.crop(out.getbbox())


def kola(im):
    """Prostokąty sześciu kół w arkuszu: kolumny i wiersze bez białego tła."""
    g = np.asarray(im.convert("RGB")).astype(int).min(axis=2) <= 232

    def seg(frac):
        on, out, s = frac > 0.02, [], None
        for i, v in enumerate(on):
            if v and s is None:
                s = i
            if not v and s is not None:
                if i - s > 200:
                    out.append((s, i))
                s = None
        if s is not None:
            out.append((s, len(on)))
        return out
    cols, rows = seg(g.mean(axis=0)), seg(g.mean(axis=1))
    if len(cols) != 3 or len(rows) != 2:
        raise SystemExit(f"arkusz ikon: oczekiwane 3 × 2, jest {len(cols)} × {len(rows)}")
    return [(c0, r0, c1, r1) for (r0, r1) in rows for (c0, c1) in cols]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.open(RAW / "ikony_v1.png")
    for name, box in zip(SHEET_ORDER, kola(sheet)):
        x0, y0, x1, y1 = box
        icon = bez_tla(sheet.crop((x0 - 8, y0 - 8, x1 + 8, y1 + 8)))
        icon.thumbnail((512, 512), Image.LANCZOS)
        icon.save(OUT / f"Race{name}.png")
        print("ikona", f"Race{name}.png", icon.size)
    p = RAW / "polbog_v1.png"
    if p.exists():
        icon = bez_tla(Image.open(p))
        icon.thumbnail((512, 512), Image.LANCZOS)
        icon.save(OUT / "RaceDemigod.png")
        print("ikona RaceDemigod.png", icon.size)
    TOUT.mkdir(parents=True, exist_ok=True)
    for f in sorted(TRAW.glob("*_v1.png")):
        im = Image.open(f).convert("RGB")
        im = im.resize((2400, round(2400 * im.height / im.width)), Image.LANCZOS)
        im.save(TOUT / (f.stem.replace("_v1", "") + ".jpg"), quality=90)
        print("rzut", f.stem.replace("_v1", ""))
    man = json.loads((ROOT / "assets/manifest.json").read_text(encoding="utf-8"))["assets"]
    lines = ["-- WYGENEROWANE przez tools/raceselect_assets.py z assets/manifest.json — nie edytuj ręcznie.", "return {"]
    for n in ALL:
        i = man.get(f"Race{n}", {}).get("roblox_image")
        lines.append(f'\tRace{n} = "rbxassetid://{i or 0}",')
    lines.append("}")
    (ROOT / "src/shared/RaceIcons.luau").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("ok src/shared/RaceIcons.luau")


if __name__ == "__main__":
    main()
