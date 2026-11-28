#!/usr/bin/env python3
"""Okno Index (Paweł 26.11) -> src/gui/OknoIndeksu.model.json.

Grafika: tools/okno_indeksu_ui.py (kafelki OknoIndeksu1–4, zakładki ZakladkaJasna/Ciemna). Na pergaminie przewijana
lista budowana w kliencie (src/client/OknoIndeksuClient): sekcje według krain, kafelki petów (podobizny 3D) albo
przedmiotów klasy gracza. Zakładki PETS / ITEMS na dolnej desce okna, licznik zebranych nad listą.
Ułamki pozycji zmierzone na Okno.png 26.11 (pergamin, X, tabliczka, dolna deska).

Do tego ekran awansu na poziom -> src/gui/Awans.model.json (złota wstęga z napisem LEVEL UP!, wybuch światła, warstwa
na konfetti; animację robi src/client/AwansClient.client.luau).

Użycie: python tools/okno_indeksu_build_gui.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shop_build_gui as S  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/gui/OknoIndeksu.model.json"
node, text, hit, ud, c3 = S.node, S.text, S.hit, S.ud, S.c3
CREAM, WHITE, GOLD, DARK = "FCE3B0", "FFFFFF", "FFD65A", "4A2E1A"
PROPORCJE = 2048 / 1840
PERGAMIN = (0.063, 0.1543, 0.8652, 0.6853)


def img(name):
    i = S.MAN.get(name, {}).get("roblox_image")
    return f"rbxassetid://{i}" if i else ""


def zakladka(nazwa, x, tekst):
    return node(nazwa, "ImageButton", {**ud(x, 0.872, 0.27, 0.085), "BackgroundTransparency": 1,
                                       "Image": img("IndeksZakladkaCiemna"), "ScaleType": "Stretch",
                                       "AutoButtonColor": False, "ZIndex": 6}, [
        node("UIScale", "UIScale", {"Scale": 1}),
        text("Label", (0.08, 0.14, 0.84, 0.66), tekst, WHITE, 30, 2.5, 7),
    ])


def main():
    x, y, w, h = PERGAMIN
    panel = node("Panel", "Frame", {"AnchorPoint": [0.5, 0.5], **ud(0.5, 0.5, 0.86, 0.9), "BackgroundTransparency": 1}, [
        node("UIAspectRatioConstraint", "UIAspectRatioConstraint", {"AspectRatio": round(PROPORCJE, 5),
                                                                     "AspectType": "FitWithinMaxSize", "DominantAxis": "Width"}),
        node("UIScale", "UIScale", {"Scale": 1}),
        node("InputBlocker", "TextButton", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "Text": "", "AutoButtonColor": False}),
        node("Art", "Frame", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "ZIndex": 1}, [
            node(f"Tile{n}", "ImageLabel", {**ud(cx * 0.5, cy * 0.5, 0.5, 0.5), "BackgroundTransparency": 1,
                                            "Image": img(f"OknoIndeksu{n}"), "ScaleType": "Stretch", "ZIndex": 1})
            for n, (cx, cy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)], 1)]),
        hit("CloseButton", (0.9292, 0.0321, 0.0649, 0.0647)),
        text("Title", (0.32, 0.018, 0.36, 0.072), "INDEX", CREAM, 44),
        text("Progress", (x + 0.02, y + 0.012, w * 0.6, 0.045), "", DARK, 22, 0, 5),
        text("Hint", (x + w * 0.45, y + 0.012, w * 0.53, 0.045), "", DARK, 16, 0, 5),
        node("List", "ScrollingFrame", {**ud(x + 0.012, y + 0.065, w - 0.024, h - 0.08), "BackgroundTransparency": 1,
                                        "BorderSizePixel": 0, "ScrollBarThickness": 8,
                                        "ScrollBarImageColor3": c3("8A5A32"), "CanvasSize": {"UDim2": [[0, 0], [0, 0]]},
                                        "AutomaticCanvasSize": "Y", "ScrollingDirection": "Y", "ZIndex": 5}, [
            node("UIListLayout", "UIListLayout", {"SortOrder": "LayoutOrder", "Padding": {"UDim": [0, 10]},
                                                  "HorizontalAlignment": "Center"}),
            node("UIPadding", "UIPadding", {"PaddingRight": {"UDim": [0, 10]}, "PaddingBottom": {"UDim": [0, 10]}}),
        ]),
        zakladka("TabPets", 0.2, "PETS"),
        zakladka("TabItems", 0.53, "ITEMS"),
    ])
    for n in ("Progress",):
        for c in panel["Children"]:
            if c.get("Name") == n:
                c["Properties"]["TextXAlignment"] = "Left"
                c["Properties"]["FontFace"] = S.FONT
                c["Children"] = [k for k in c["Children"] if k["ClassName"] != "UIStroke"]
    for c in panel["Children"]:
        if c.get("Name") == "Hint":
            c["Properties"]["TextXAlignment"] = "Right"
            c["Properties"]["FontFace"] = {"Font": {"family": "rbxasset://fonts/families/GothamSSm.json", "weight": "Bold",
                                                    "style": "Normal"}}
            c["Children"] = [k for k in c["Children"] if k["ClassName"] != "UIStroke"]
    gui = {"ClassName": "ScreenGui",
           "Properties": {"Enabled": False, "ResetOnSpawn": False, "IgnoreGuiInset": True, "ZIndexBehavior": "Sibling",
                          "DisplayOrder": 25},
           "Children": [node("Backdrop", "TextButton", {**ud(0, 0, 1, 1), "BackgroundColor3": [0, 0, 0],
                                                        "BackgroundTransparency": 0.45, "Text": "", "AutoButtonColor": False}),
                        panel,
                        {"Name": "Art", "ClassName": "Folder", "Children": [
                            {"Name": "TabActive", "ClassName": "StringValue", "Properties": {"Value": img("IndeksZakladkaJasna")}},
                            {"Name": "TabIdle", "ClassName": "StringValue", "Properties": {"Value": img("IndeksZakladkaCiemna")}},
                        ]}]}
    OUT.write_text(json.dumps(gui, indent=1, ensure_ascii=False), encoding="utf-8")
    print("ok", OUT.relative_to(ROOT))


def awans():
    banner = node("Banner", "Frame", {"AnchorPoint": [0.5, 0.5], **ud(0.5, 0.3, 0.5, 0.3), "BackgroundTransparency": 1,
                                      "Visible": False, "ZIndex": 2}, [
        node("UIAspectRatioConstraint", "UIAspectRatioConstraint", {"AspectRatio": 2.2, "AspectType": "FitWithinMaxSize",
                                                                     "DominantAxis": "Width"}),
        node("UIScale", "UIScale", {"Scale": 1}),
        node("Glow", "ImageLabel", {"AnchorPoint": [0.5, 0.5], **ud(0.5, 0.42, 0.62, 1.36), "BackgroundTransparency": 1,
                                    "Image": img("AwansBlask"), "ScaleType": "Fit", "ZIndex": 2}),
        node("Ribbon", "ImageLabel", {"AnchorPoint": [0.5, 0.5], **ud(0.5, 0.42, 1, 0.66), "BackgroundTransparency": 1,
                                      "Image": img("AwansWstega"), "ScaleType": "Fit", "ZIndex": 3}),
        text("Title", (0.22, 0.25, 0.56, 0.3), "LEVEL UP!", WHITE, 64, 4, 4),
        text("Level", (0.25, 0.74, 0.5, 0.22), "LEVEL 2", GOLD, 48, 4, 4),
    ])
    gui = {"ClassName": "ScreenGui",
           "Properties": {"Enabled": True, "ResetOnSpawn": False, "IgnoreGuiInset": True, "ZIndexBehavior": "Sibling",
                          "DisplayOrder": 40},
           "Children": [node("Confetti", "Frame", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "ZIndex": 1}), banner]}
    out = ROOT / "src/gui/Awans.model.json"
    out.write_text(json.dumps(gui, indent=1, ensure_ascii=False), encoding="utf-8")
    print("ok", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
    awans()
