#!/usr/bin/env python3
"""Generuje src/gui/ClassSelect.model.json — warstwa 2D ekranu wyboru klasy (scena 3D: swiat/wybor_klasy).

Elementy (polecenie Pawła 16.11.2026; bez emblematów po prawej): tabliczka z tytułem, karta statystyk po lewej
(emblemat, nazwa klasy, podtytuł, 6 pasków natywnych), strzałki przy podeście, PLAY na dole. Klasy i liczby
wypełnia src/client/ClassSelectClient.client.luau. Grafiki: assets/processed/ClassSelect (tools/classselect_assets.py),
ID z assets/manifest.json. Projekt: B&C/UI/Selektor bohatera.md.

Użycie: python tools/classselect_build_gui.py
"""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MAN = json.loads((ROOT / "assets/manifest.json").read_text(encoding="utf-8"))["assets"]
D = ROOT / "assets/processed/ClassSelect"
OUT = ROOT / "src/gui/ClassSelect.model.json"
FONT = {"Font": {"family": "rbxasset://fonts/families/LuckiestGuy.json", "weight": "Regular", "style": "Normal"}}
STATS = ["STRENGTH", "CONSTITUTION", "INTELLIGENCE", "DEXTERITY", "LUCK", "ARMOR"]


def c3(h):
    return [round(int(h[i:i + 2], 16) / 255, 4) for i in (0, 2, 4)]


def img(name):
    i = MAN.get(name, {}).get("roblox_image")
    return f"rbxassetid://{i}" if i else "rbxassetid://0"


def img_or(name, fallback):
    """Nowa grafika, a dopóki nie ma ID w Roblox — poprzednia (żeby wdrożenie nie zostawiło pustego obrazka)."""
    return img(name) if not img(name).endswith("//0") else img(fallback)


def aspect(name):
    w, h = Image.open(D / f"{name}.png").size
    return round(w / h, 4)


def ud(xs, ys, w, h):
    return {"Position": {"UDim2": [[xs, 0], [ys, 0]]}, "Size": {"UDim2": [[w, 0], [h, 0]]}}


def node(name, cls, props, children=None):
    base = {} if cls.startswith("UI") else {"BorderSizePixel": 0}
    n = {"Name": name, "ClassName": cls, "Properties": {**base, **props}}
    if children:
        n["Children"] = children
    return n


def ar(a):
    # wysokość liczona z szerokości (Size Y = 0): tryb ScaleWithParentSize, oś dominująca = szerokość
    return node("UIAspectRatioConstraint", "UIAspectRatioConstraint",
                {"AspectRatio": a, "AspectType": "ScaleWithParentSize", "DominantAxis": "Width"})


def stroke(t=3, mode="Contextual", color="1A1410"):
    return node("UIStroke", "UIStroke", {"Color": c3(color), "Thickness": t, "LineJoinMode": "Round", "ApplyStrokeMode": mode})


def text(name, pos, s, fill, mx, align="Center", st=3, z=3):
    return node(name, "TextLabel", {**pos, "BackgroundTransparency": 1, "Text": s, "TextColor3": c3(fill), "FontFace": FONT,
                                    "TextScaled": True, "TextXAlignment": align, "TextYAlignment": "Center", "ZIndex": z},
                [node("UITextSizeConstraint", "UITextSizeConstraint", {"MaxTextSize": mx, "MinTextSize": 6})] + ([stroke(st)] if st else []))


def image_button(name, anchor, pos, w, img_name, kids=None, z=3):
    return node(name, "ImageButton", {"AnchorPoint": anchor, **ud(pos[0], pos[1], w, 0), "BackgroundTransparency": 1,
                                      "Image": img(img_name), "ScaleType": "Fit", "AutoButtonColor": False, "ZIndex": z},
                [ar(aspect(img_name)), node("UIScale", "UIScale", {"Scale": 1})] + (kids or []))


def main():
    rows = []
    for i, s in enumerate(STATS):
        y = 0.25 + i * 0.112
        rows.append(text(f"Label{i + 1}", ud(0.09, y, 0.82, 0.048), s, "FFFFFF", 18, "Left", 2))
        rows.append(node(f"Bar{i + 1}", "Frame", {**ud(0.09, y + 0.052, 0.82, 0.03), "BackgroundColor3": c3("0E1220"), "ZIndex": 3}, [
            node("UICorner", "UICorner", {"CornerRadius": {"UDim": [0.5, 0]}}), stroke(2, "Border"),
            node("Fill", "Frame", {**ud(0, 0, 0.5, 1), "BackgroundColor3": [1, 1, 1], "ZIndex": 4}, [
                node("UICorner", "UICorner", {"CornerRadius": {"UDim": [0.5, 0]}}),
                node("UIGradient", "UIGradient", {"Rotation": 90, "Color": {"ColorSequence": {"keypoints": [
                    {"time": 0, "color": [1, 0.94, 0.48]}, {"time": 1, "color": [0.95, 0.66, 0.12]}]}}}),
            ]),
        ]))
    # sama ramka karty, środek przezroczysty (Paweł 17.11): CsStatsFrame = CsStatsPanel bez granatowego wnętrza
    # karta = kontener: pod ramką półprzezroczyste ciemne tło (Paweł 17.11: sama ramka była nieczytelna na scenie 3D),
    # na nim ramka CsStatsFrame (środek przezroczysty), na wierzchu napisy i paski
    card = node("StatsCard", "Frame", {"AnchorPoint": [0, 0.5], **ud(0.025, 0.53, 0.23, 0), "BackgroundTransparency": 1,
                                       "ZIndex": 2}, [
        ar(aspect("CsStatsFrame")), node("UIScale", "UIScale", {"Scale": 1}),
        node("Back", "Frame", {**ud(0.05, 0.033, 0.9, 0.934), "BackgroundColor3": c3("141A2E"), "BackgroundTransparency": 0.4,
                               "ZIndex": 2}, [node("UICorner", "UICorner", {"CornerRadius": {"UDim": [0.06, 0]}})]),
        node("FrameArt", "ImageLabel", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1,
                                        "Image": img_or("CsStatsFrame", "CsStatsPanel"), "ScaleType": "Fit", "ZIndex": 2}),
        node("Emblem", "ImageLabel", {**ud(0.07, 0.045, 0.25, 0), "BackgroundTransparency": 1, "Image": img("CsEmblemWarrior"),
                                      "ScaleType": "Fit", "ZIndex": 3}, [ar(1)]),
        text("ClassTitle", ud(0.36, 0.055, 0.6, 0.085), "WARRIOR", "FFD23F", 40, "Left", 3),
        text("Subtitle", ud(0.36, 0.14, 0.6, 0.045), "SHIELD & SWORD", "8AF0FF", 18, "Left", 2),
        *rows,
    ])
    plank = node("TitlePlank", "ImageLabel", {"AnchorPoint": [0.5, 0], **ud(0.5, 0.012, 0.36, 0), "BackgroundTransparency": 1,
                                              "Image": img("CsTitlePlank"), "ScaleType": "Fit", "ZIndex": 2}, [
        ar(aspect("CsTitlePlank")),
        text("Title", ud(0.14, 0.3, 0.72, 0.4), "CHOOSE YOUR CLASS", "FCE3B0", 46, st=3),
    ])
    gui = {
        "ClassName": "ScreenGui",
        "Properties": {"Enabled": False, "ResetOnSpawn": False, "IgnoreGuiInset": True, "ZIndexBehavior": "Sibling", "DisplayOrder": 30},
        "Children": [
            # przyciemnienie brzegów (winieta), żeby napisy i karta były czytelne na scenie 3D
            node("Vignette", "Frame", {**ud(0, 0, 1, 1), "BackgroundColor3": [0, 0, 0], "BackgroundTransparency": 1, "ZIndex": 1}),
            plank, card,
            image_button("ArrowLeft", [0.5, 0.5], (0.335, 0.79), 0.075, "CsArrowLeft"),
            image_button("ArrowRight", [0.5, 0.5], (0.665, 0.79), 0.075, "CsArrowRight"),
            image_button("PlayButton", [0.5, 1], (0.5, 0.975), 0.23, "CsPlayButton",
                         [text("Label", ud(0.1, 0.18, 0.8, 0.56), "PLAY", "FFFFFF", 60, st=4, z=4)]),
        ],
    }
    OUT.write_text(json.dumps(gui, indent=1, ensure_ascii=False), encoding="utf-8")
    ikony = ["-- WYGENEROWANE przez tools/classselect_build_gui.py z assets/manifest.json — nie edytuj ręcznie.",
             "return {"] + [f'\t{n} = "{img(n)}",' for n in ("CsEmblemWarrior", "CsEmblemScout", "CsEmblemMage")] + ["}"]
    (ROOT / "src/shared/ClassSelectIcons.luau").write_text("\n".join(ikony) + "\n", encoding="utf-8")
    missing = [n for n in ("CsTitlePlank", "CsStatsFrame", "CsArrowLeft", "CsArrowRight", "CsPlayButton",
                           "CsEmblemWarrior", "CsEmblemScout", "CsEmblemMage") if img(n).endswith("//0")]
    print(f"ok {OUT.relative_to(ROOT)}; bez ID Roblox: {missing or '-'}")


if __name__ == "__main__":
    main()
