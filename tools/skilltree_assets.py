#!/usr/bin/env python3
"""Grafiki okna drzewka umiejętności: kopiuje oryginały, tnie arkusze ikon, obrabia tła i okno.

Wejście:  folder z obrazami z Higgsfield (domyślnie ~/Desktop/skill tree) albo assets/raw/<Nazwa>/v1.png
Wyjście:  assets/processed/SkillTree/*.png + assets/processed/SkillTree/layout.json + podgląd contact.png

Arkusze: ikony to okrągłe medaliony na białym tle. Komponenty (nie-biel) -> filtr „okrągłe i duże”
(odpada np. napis dopisany przez model) -> kolejność czytania (rzędy, potem lewo->prawo) -> wycięcie tła
flood fill (tools/process_image.py) -> kwadrat 256 px.

Okno: tło dookoła przezroczyste (flood), skala do 1024 px szerokości (limit Roblox), z tego wycięte
3 zakładki i X jako osobne sprite'y (stan aktywny / hover) oraz prostokąt treści (beżowe wnętrze).

Użycie: python tools/skilltree_assets.py [--src "C:/Users/<ty>/Desktop/skill tree"]
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import process_image as PI  # noqa: E402

OUT = ROOT / "assets/processed/SkillTree"
RAW = ROOT / "assets/raw"

# plik źródłowy (nazwa z Higgsfield, znacznik czasu) -> nazwa assetu
SOURCES = {
    "133040": "SkillTreeButtons", "133441": "SkillTreeFrame",
    "133742": "SkillTreeBgPlayer", "133816": "SkillTreeBgFortress", "133842": "SkillTreeBgPets",
    "134002": "IconsPlayerStats", "134020": "IconsPlayerIncome", "134035": "IconsPlayerSkills",
    "134044": "IconsFortressTraining", "134224": "IconsFortressIncome", "134239": "IconsFortressTimer",
    "134253": "IconsPetsStats", "134303": "IconsPetsEggs", "134313": "IconsPetsLuck", "134352": "IconsPetsCapacity",
    "134430": "IconsPetsStats_v2",  # drugi wariant Pet Stats (nieużywany)
}

# arkusz -> nazwy ikon w kolejności czytania
SHEETS = {
    "SkillTreeButtons": ["SkillTreeButton", "SkillTreeAlert"],
    # węzły startowe zakładek + zakryty węzeł „?” (dogenerowane 15.11, jeden wariant)
    "SkillTreeRoots": ["NodeRootPlayer", "NodeRootFortress", "NodeRootPets", "NodeHidden"],
    "IconsPlayerStats": ["NodeStatStr", "NodeStatConst", "NodeStatInt", "NodeStatDex", "NodeStatLuck", "NodeStatArmor", "NodeStatAll"],
    "IconsPlayerIncome": ["NodeIncGold", "NodeIncExp", "NodeIncGems", "NodeIncPouch", "NodeIncChest", "NodeIncOffline"],
    "IconsPlayerSkills": ["NodeSkillPowerSlash", "NodeSkillCrushingBlow", "NodeSkillStoneSkin", "NodeSkillShieldBlock", "NodeSkillWarCry", "NodeSkillSlot"],
    "IconsFortressTraining": ["NodeFortTrainDummy", "NodeFortTrainWeights", "NodeFortTrainSwords", "NodeFortTrainTarget", "NodeFortTrainAnvil", "NodeFortTrainGain"],
    "IconsFortressIncome": ["NodeFortIncOre", "NodeFortIncWood", "NodeFortIncStone", "NodeFortIncCrystal", "NodeFortIncCart", "NodeFortIncTimed"],
    "IconsFortressTimer": ["NodeFortTimeHourglass", "NodeFortTimeHammer", "NodeFortTimeStopwatch", "NodeFortTimeScaffold", "NodeFortTimeCrane", "NodeFortTimeGears"],
    "IconsPetsStats": ["NodePetStatAtk", "NodePetStatHp", "NodePetStatDef", "NodePetStatSpeed", "NodePetStatLuck", "NodePetStatAll"],
    "IconsPetsEggs": ["NodePetEggFast", "NodePetEggMulti", "NodePetEggTimer", "NodePetEggCrack", "NodePetEggIncubator", "NodePetEggBasket"],
    "IconsPetsLuck": ["NodePetLuckGolden", "NodePetLuckRainbow", "NodePetLuckClover", "NodePetLuckDice", "NodePetLuckStar", "NodePetLuckCrown"],
    "IconsPetsCapacity": ["NodePetCapSlots", "NodePetCapCollar", "NodePetCapBed", "NodePetCapBackpack", "NodePetCapCrates", "NodePetCapHouse"],
}
BACKGROUNDS = ["SkillTreeBgPlayer", "SkillTreeBgFortress", "SkillTreeBgPets"]
ICON_PX = 256
BG_W = 1024
FRAME_W = 1024


def copy_sources(src: Path):
    for f in sorted(src.glob("*.png")):
        name = next((n for k, n in SOURCES.items() if f"_{k}_" in f.name), None)
        if not name:
            print("pomijam (nieznany plik):", f.name)
            continue
        dst = RAW / name / "v1.png"
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copy2(f, dst)


def load(name) -> Image.Image:
    return Image.open(RAW / name / "v1.png").convert("RGB")


def round_components(im: Image.Image):
    a = np.asarray(im).astype(int)
    fg = a.min(-1) < 232
    fg = ndimage.binary_closing(fg, iterations=3)
    fg = ndimage.binary_fill_holes(fg)
    lab, _ = ndimage.label(fg)
    H, W = fg.shape
    boxes = []
    for sl in ndimage.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if h * w < 0.004 * H * W:
            continue
        if not 0.75 < w / h < 1.33:  # napis, smuga
            continue
        boxes.append((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop))
    # kolejność czytania: rzędy po środku y
    boxes.sort(key=lambda b: (b[1] + b[3]) / 2)
    rows, cur = [], []
    for b in boxes:
        if cur and (b[1] + b[3]) / 2 - (cur[-1][1] + cur[-1][3]) / 2 > (b[3] - b[1]) * 0.5:
            rows.append(cur)
            cur = []
        cur.append(b)
    if cur:
        rows.append(cur)
    return [b for r in rows for b in sorted(r, key=lambda b: b[0])]


def cut_icon(im: Image.Image, box) -> Image.Image:
    x0, y0, x1, y1 = box
    pad = 14
    crop = im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))
    rgba = PI.remove_bg_flood(crop.convert("RGBA"), 30)
    rgba = PI.trim(rgba)
    rgba = PI.to_square(rgba, 2)
    return PI.fit(rgba, ICON_PX)


def do_sheets(report):
    for sheet, names in SHEETS.items():
        im = load(sheet)
        boxes = round_components(im)
        if len(boxes) != len(names):
            raise SystemExit(f"{sheet}: znaleziono {len(boxes)} ikon, oczekiwano {len(names)}")
        for n, b in zip(names, boxes):
            cut_icon(im, b).save(OUT / f"{n}.png")
            report.append(n)


def do_backgrounds(report):
    for n in BACKGROUNDS:
        im = load(n)
        h = round(im.height * BG_W / im.width)
        im.resize((BG_W, h), Image.LANCZOS).save(OUT / f"{n}.png")
        report.append(n)


def defringe(rgba: Image.Image, band: int = 3) -> Image.Image:
    """Zewnętrzny brzeg po wycięciu z białego tła: jasne piksele przy przezroczystości (biała obwódka 1–2 px
    widoczna na ciemnym tle gry) -> usunięte; pozostałe półprzezroczyste -> kolor czarnego obrysu."""
    a = np.array(rgba)
    trans = a[..., 3] == 0
    edge = ndimage.binary_dilation(trans, iterations=band) & ~trans
    light = a[..., :3].min(-1) > 120
    a[edge & light, 3] = 0
    soft = edge & (a[..., 3] > 0) & (a[..., 3] < 255)
    a[soft, :3] = np.minimum(a[soft, :3], 40)
    return Image.fromarray(a)


def do_frame(report):
    im = load("SkillTreeFrame")
    h = round(im.height * FRAME_W / im.width)
    small = im.resize((FRAME_W, h), Image.LANCZOS)
    rgba = PI.remove_bg_flood(small.convert("RGBA"), 30)
    bbox = rgba.getbbox()
    rgba = defringe(rgba.crop(bbox))
    rgba.save(OUT / "SkillTreeFrame.png")
    report.append("SkillTreeFrame")
    W, H = rgba.size
    a = np.asarray(rgba).astype(int)
    rgb, al = a[..., :3], a[..., 3] > 128

    def frac(x0, y0, x1, y1):
        return [round(x0 / W, 5), round(y0 / H, 5), round((x1 - x0) / W, 5), round((y1 - y0) / H, 5)]

    # wnętrze: beżowy panel aż do złotej obwódki. Skan od środka w 4 strony (bbox maski z „opening”
    # był za ciasny — tło karty nie sięgało dolnej krawędzi, uwaga Pawła 15.11)
    def is_beige(p):
        return p.min() > 150 and 10 < p[0] - p[2] < 110

    def scan(x, y, dx, dy):
        last, miss = (x, y), 0
        while 0 <= x < W and 0 <= y < H and miss < 3:
            if is_beige(rgb[y, x]):
                last, miss = (x, y), 0
            else:
                miss += 1
            x, y = x + dx, y + dy
        return last
    cx, cy = W // 2, int(H * 0.6)
    x0, x1 = scan(cx, cy, -1, 0)[0], scan(cx, cy, 1, 0)[0]
    y0, y1 = scan(cx, cy, 0, -1)[1], scan(cx, cy, 0, 1)[1]
    content = frac(x0, y0, x1 + 1, y1 + 1)
    ys = np.array([y0])

    # zakładki: konkretne kolory (drewno ramki też jest nasycone, więc nie wystarczy samo nasycenie)
    r_, g_, b_ = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    colors = {
        "TabPlayer": (r_ > 200) & (g_ > 120) & (g_ < 215) & (b_ < 130) & (r_ - b_ > 110),   # pomarańcz
        "TabFortress": (b_ > 170) & (r_ > 130) & (g_ < 160) & (b_ - g_ > 50),               # fiolet
        "TabPets": (g_ > 160) & (g_ - r_ > 40) & (g_ - b_ > 15),                            # zieleń
    }
    tboxes = []
    for name, m in colors.items():
        m = m & al
        m[: int(H * 0.1), :] = False
        m[int(H * 0.4):, :] = False
        lab_t, _ = ndimage.label(ndimage.binary_opening(m, iterations=2))
        if lab_t.max() == 0:
            raise SystemExit(f"okno: brak zakładki {name}")
        sizes = ndimage.sum(m, lab_t, range(1, lab_t.max() + 1))
        sl = ndimage.find_objects(lab_t)[int(np.argmax(sizes))]
        tboxes.append((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop))
    import eq_slice  # segmentacja jak w oknie ekwipunku (tryb tight: obrys bez tła)
    arr = np.asarray(rgba)
    tabs = {}
    for name, (x0, y0, x1, y1) in zip(["TabPlayer", "TabFortress", "TabPets"], tboxes):
        g = 10
        rect = (max(0, x0 - g), max(0, y0 - g), min(W, x1 + g), min(H, y1 + 2))
        seed = ((x0 + x1) // 2, (y0 + y1) // 2)
        sp = eq_slice.utwardz(eq_slice.segment(arr, rect, seed, 55, 8, tight=True))  # twardy brzeg (Paweł 17.11)
        sp.save(OUT / f"SkillTree{name}.png")
        report.append(f"SkillTree{name}")
        tabs[name] = frac(*rect)

    # X: czerwony przycisk w prawym górnym rogu
    red = al & (rgb[..., 0] > 170) & (rgb[..., 1] < 110) & (rgb[..., 2] < 110)
    red[int(H * 0.14):, :] = False
    red[:, : int(W * 0.86)] = False
    ys_r, xs_r = np.nonzero(red)
    g = 8
    xr = (max(0, xs_r.min() - g), max(0, ys_r.min() - g), min(W, xs_r.max() + g), min(H, ys_r.max() + g))
    seed = ((xr[0] + xr[2]) // 2, int(ys_r.min() + (ys_r.max() - ys_r.min()) * 0.3))
    sp = eq_slice.segment(arr, xr, seed, 60, 7, tight=False)
    sp.save(OUT / "SkillTreeClose.png")
    report.append("SkillTreeClose")

    # tabliczka nagłówka: brązowe drewno u góry na środku
    wood = al & (rgb[..., 0] > 110) & (rgb[..., 0] < 220) & (rgb[..., 2] < 110) & (rgb[..., 0] - rgb[..., 2] > 50)
    wood[int(H * 0.12):, :] = False
    wood[:, : int(W * 0.3)] = False
    wood[:, int(W * 0.7):] = False
    ys_w, xs_w = np.nonzero(wood)
    title = frac(xs_w.min(), ys_w.min(), xs_w.max() + 1, ys_w.max() + 1)

    return {"frame_px": [W, H], "aspect": round(W / H, 5), "content": content, "tabs": tabs,
            "close": frac(*xr), "title": title}


def contact(names):
    tiles = [Image.open(OUT / f"{n}.png").convert("RGBA") for n in names if n.startswith(("Node", "SkillTreeButton", "SkillTreeAlert"))]
    cols = 10
    sz = 110
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * sz, rows * sz), (52, 40, 30, 255))
    for i, t in enumerate(tiles):
        t = t.copy()
        t.thumbnail((sz - 8, sz - 8))
        sheet.alpha_composite(t, ((i % cols) * sz + 4, (i // cols) * sz + 4))
    sheet.save(OUT / "contact.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(Path.home() / "Desktop/skill tree"))
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    src = Path(args.src)
    if src.exists():
        copy_sources(src)
    report = []
    do_sheets(report)
    do_backgrounds(report)
    layout = do_frame(report)
    layout["icons"] = {k: v for k, v in SHEETS.items()}
    (OUT / "layout.json").write_text(json.dumps(layout, indent=1, ensure_ascii=False), encoding="utf-8")
    contact(report)
    print(f"ok: {len(report)} plików w {OUT.relative_to(ROOT)}")
    print(json.dumps({k: layout[k] for k in ("frame_px", "content", "tabs", "close", "title")}))


if __name__ == "__main__":
    main()
