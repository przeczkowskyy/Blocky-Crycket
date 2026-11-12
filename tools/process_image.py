#!/usr/bin/env python3
"""Obrobka grafik AI pod Figme/Roblox: wyciecie tla, trim, kwadrat, rozmiar, podglady.

Przyklady:
  python tools/process_image.py raw.png assets/processed/IconArena.png --category icon
  python tools/process_image.py raw.png out.png --bg flood --tolerance 40 --size 512
  python tools/process_image.py keyart.png assets/processed/KeyArt.png --category background
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path

from PIL import Image

# kategoria -> (max rozmiar dluzszego boku, kwadrat?, padding %, wycinanie tla?)
CATEGORY = {
    "icon": (512, True, 4, True),
    "button": (512, True, 2, True),
    "item": (512, True, 4, True),
    "pet": (512, True, 4, True),
    "currency": (256, True, 4, True),
    "frame": (1024, False, 0, True),
    "background": (2752, False, 0, False),
    "keyart": (2752, False, 0, False),
}
PREVIEW_SIZES = (128, 64)


def remove_bg_rembg(im: Image.Image) -> Image.Image:
    from rembg import remove  # import leniwy – opcjonalna zaleznosc

    return remove(im.convert("RGBA"))


def remove_bg_flood(im: Image.Image, tolerance: int) -> Image.Image:
    """Zalewa tlo od krawedzi kadru. Dziala swietnie przy jednolitym tle + grubym obrysie."""
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    # referencyjne kolory tla: probki z rogow i srodkow krawedzi
    samples = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]
    refs = [px[x, y][:3] for x, y in samples if px[x, y][3] > 0]

    def is_bg(c) -> bool:
        if c[3] == 0:
            return True
        return any(abs(c[0] - r[0]) + abs(c[1] - r[1]) + abs(c[2] - r[2]) <= tolerance for r in refs)

    seen = bytearray(w * h)
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        q.append((x, 0)); q.append((x, h - 1))
    for y in range(h):
        q.append((0, y)); q.append((w - 1, y))
    while q:
        x, y = q.popleft()
        i = y * w + x
        if seen[i]:
            continue
        seen[i] = 1
        c = px[x, y]
        if not is_bg(c):
            continue
        px[x, y] = (c[0], c[1], c[2], 0)
        if x > 0: q.append((x - 1, y))
        if x < w - 1: q.append((x + 1, y))
        if y > 0: q.append((x, y - 1))
        if y < h - 1: q.append((x, y + 1))

    # defringe: jasne, prawie-tlowe piksele graniczace z przezroczystoscia -> polprzezroczyste
    out = im.copy()
    opx = out.load()
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            c = px[x, y]
            if c[3] == 0:
                continue
            if any(px[nx, ny][3] == 0 for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))):
                d = min(abs(c[0] - r[0]) + abs(c[1] - r[1]) + abs(c[2] - r[2]) for r in refs)
                if d <= tolerance * 3:
                    opx[x, y] = (c[0], c[1], c[2], int(255 * d / (tolerance * 3)))
    return out


def trim(im: Image.Image, alpha_threshold: int = 8) -> Image.Image:
    a = im.getchannel("A").point(lambda v: 255 if v > alpha_threshold else 0)
    bbox = a.getbbox()
    return im.crop(bbox) if bbox else im


def to_square(im: Image.Image, pad_pct: float) -> Image.Image:
    side = max(im.size)
    side = int(round(side * (1 + 2 * pad_pct / 100)))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2), im)
    return canvas


def fit(im: Image.Image, max_side: int) -> Image.Image:
    if max(im.size) <= max_side:
        return im
    s = max_side / max(im.size)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--category", choices=sorted(CATEGORY), default="icon")
    ap.add_argument("--bg", choices=["auto", "rembg", "flood", "none"], default=None,
                    help="wycinanie tla (domyslnie wg kategorii: auto albo none)")
    ap.add_argument("--tolerance", type=int, default=30, help="tolerancja flood fill (suma |dR|+|dG|+|dB|)")
    ap.add_argument("--size", type=int, default=None, help="max dlugosc dluzszego boku (nadpisuje kategorie)")
    ap.add_argument("--pad", type=float, default=None, help="padding %% przy kwadracie (nadpisuje kategorie)")
    ap.add_argument("--no-square", action="store_true")
    ap.add_argument("--no-previews", action="store_true")
    args = ap.parse_args()

    max_side, square, pad, cut = CATEGORY[args.category]
    max_side = args.size or max_side
    pad = args.pad if args.pad is not None else pad
    square = square and not args.no_square
    bg = args.bg or ("auto" if cut else "none")

    src = Path(args.input)
    dst = Path(args.output)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGBA")
    orig = im.size

    method = "none"
    if bg in ("auto", "rembg"):
        try:
            im = remove_bg_rembg(im)
            method = "rembg"
        except ImportError:
            if bg == "rembg":
                print("rembg nie jest zainstalowany: pip install 'rembg[cpu]'", file=sys.stderr)
                return 2
            bg = "flood"
    if bg == "flood":
        im = remove_bg_flood(im, args.tolerance)
        method = "flood"

    if method != "none":
        im = trim(im)
        if square:
            im = to_square(im, pad)
    im = fit(im, max_side)
    im.save(dst, optimize=True)

    previews = []
    if not args.no_previews and method != "none":
        for s in PREVIEW_SIZES:
            p = dst.with_name(f"{dst.stem}@{s}{dst.suffix}")
            fit(im, s).save(p, optimize=True)
            previews.append(str(p))

    # proste QA: ile pikseli przezroczystych, czy obiekt nie dotyka krawedzi
    alpha = im.getchannel("A")
    transparent = alpha.histogram()[0] / (im.width * im.height)
    touches_edge = False
    if method != "none":
        bbox = alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
        touches_edge = bool(bbox) and (bbox[0] == 0 or bbox[1] == 0 or bbox[2] == im.width or bbox[3] == im.height) and not square

    print(json.dumps({
        "input": str(src), "output": str(dst), "previews": previews,
        "original_size": orig, "final_size": im.size, "bg_method": method,
        "transparent_ratio": round(transparent, 3), "touches_edge": touches_edge,
        "warnings": ([] if method == "none" or 0.15 < transparent < 0.95 else
                     ["podejrzany odsetek przezroczystosci – sprawdz wycinanie tla"]),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
