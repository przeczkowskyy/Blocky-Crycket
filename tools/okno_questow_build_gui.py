#!/usr/bin/env python3
"""Okno tablicy questów (Paweł 25.11) -> src/gui/OknoQuestow.model.json. Grafika: tools/okno_questow_ui.py
(ID obrazów z assets/manifest.json; przed wgraniem obrazów pola mają rbxassetid://0). Wiersze, karty kategorii
i przyciski to osobne obrazki, więc nic nie jest wypalone w tle poza ramką, tabliczką tytułu i X.
Skrypt okna: src/client/OknoQuestowClient.client.luau. Konwencje jak tools/okna_build_gui.py.

Użycie: python tools/okno_questow_build_gui.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shop_build_gui as S  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROPORCJE = 3076 / 2858
WIERSZY = 6
node, text, ud, c3 = S.node, S.text, S.ud, S.c3
CREAM, WHITE, GOLD, DARK = "FCE3B0", "FFFFFF", "FFD65A", "4A2E1A"


def img(name):
    i = S.MAN.get(name, {}).get("roblox_image")
    return f"rbxassetid://{i}" if i else "rbxassetid://0"


def obraz(name, r, plik, z, cls="ImageLabel", **extra):
    p = {**ud(*r), "BackgroundTransparency": 1, "Image": img(plik), "ScaleType": "Stretch", "ZIndex": z, **extra}
    if cls == "ImageButton":
        p["AutoButtonColor"] = False
    return node(name, cls, p)


def ciemny(name, r, s, mx, z, x_align="Left"):
    t = text(name, r, s, DARK, mx, 0, z)
    t["Properties"]["TextXAlignment"] = x_align
    t["Children"] = [c for c in t["Children"] if c["ClassName"] != "UIStroke"]
    return t


def karta(nazwa, y, plik, ikona, napis):
    k = obraz(nazwa, (0.06, y, 0.215, 0.19), plik, 5, "ImageButton")
    k["Children"] = [
        node("UIScale", "UIScale", {"Scale": 1}),
        obraz("Icon", (0.3, 0.1, 0.4, 0.5), ikona, 6, ScaleType="Fit"),
        text("Label", (0.06, 0.62, 0.88, 0.28), napis, WHITE, 20, 2, 6),
    ]
    return k


def wiersz(i):
    y = 0.15 + (i - 1) * 0.128
    w = obraz(f"Row{i}", (0.3, y, 0.645, 0.1085), "QuestWiersz", 5, Visible=False)
    przycisk = obraz("Button", (0.755, 0.22, 0.228, 0.56), "QuestPrzyciskZielony", 6, "ImageButton")
    przycisk["Children"] = [node("UIScale", "UIScale", {"Scale": 1}), text("Label", (0.06, 0.14, 0.88, 0.68), "TRACK", WHITE, 18, 2, 7)]
    w["Children"] = [
        obraz("Icon", (0.036, 0.24, 0.078, 0.56), "QuestIkonaDzienne", 6, ScaleType="Fit"),
        text("Check", (0.03, 0.18, 0.09, 0.68), "", "8CE865", 34, 2.5, 7),
        ciemny("QuestName", (0.145, 0.1, 0.4, 0.44), "", 22, 6),
        ciemny("Progress", (0.145, 0.54, 0.4, 0.34), "", 16, 6),
        text("Reward", (0.545, 0.22, 0.12, 0.56), "", GOLD, 22, 2, 6),
        node("RewardIcon", "ImageLabel", {**ud(0.668, 0.25, 0.07, 0.5), "BackgroundTransparency": 1, "Image": "", "ScaleType": "Fit",
                                          "ZIndex": 6}),
        przycisk,
    ]
    w["Children"][4]["Properties"]["TextXAlignment"] = "Right"
    return w


def main():
    kafelki = [node(f"Tile{i}", "ImageLabel", {**ud(cx * 0.5, cy * 0.5, 0.5, 0.5), "BackgroundTransparency": 1,
                                               "Image": img(f"OknoQuestow{i}"), "ScaleType": "Stretch", "ZIndex": 1})
               for i, (cx, cy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)], 1)]
    panel = node("Panel", "Frame", {"AnchorPoint": [0.5, 0.5], **ud(0.5, 0.5, 0.86, 0.9), "BackgroundTransparency": 1}, [
        node("UIAspectRatioConstraint", "UIAspectRatioConstraint", {"AspectRatio": round(PROPORCJE, 5),
                                                                     "AspectType": "FitWithinMaxSize", "DominantAxis": "Width"}),
        node("UIScale", "UIScale", {"Scale": 1}),
        node("InputBlocker", "TextButton", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "Text": "", "AutoButtonColor": False}),
        node("Art", "Frame", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "ZIndex": 1}, kafelki),
        S.hit("CloseButton", (0.918, 0.022, 0.085, 0.095)),
        text("Title", (0.32, 0.028, 0.4, 0.08), "QUEST BOARD", CREAM, 40),
        karta("TabDaily", 0.155, "QuestKartaDzienne", "QuestIkonaDzienne", "DAILY"),
        karta("TabAchievements", 0.365, "QuestKartaOsiagniecia", "QuestIkonaOsiagniecia", "GOALS"),
        text("Tracked", (0.06, 0.585, 0.215, 0.045), "TRACKED 0/3", WHITE, 20, 2),
        text("Reset", (0.06, 0.635, 0.215, 0.04), "", CREAM, 16, 2),
        text("Message", (0.06, 0.7, 0.215, 0.2), "", GOLD, 18, 2),
        *[wiersz(i) for i in range(1, WIERSZY + 1)],
        obraz("GoldButtonArt", (0, 0, 0.01, 0.01), "QuestPrzyciskZloty", 1, Visible=False),
    ])
    panel["Children"][-WIERSZY - 2]["Properties"]["TextWrapped"] = True
    gui = {"ClassName": "ScreenGui",
           "Properties": {"Enabled": False, "ResetOnSpawn": False, "IgnoreGuiInset": True, "ZIndexBehavior": "Sibling",
                          "DisplayOrder": 25},
           "Children": [node("Backdrop", "TextButton", {**ud(0, 0, 1, 1), "BackgroundColor3": [0, 0, 0],
                                                        "BackgroundTransparency": 0.45, "Text": "", "AutoButtonColor": False}),
                        panel]}
    out = ROOT / "src/gui/OknoQuestow.model.json"
    out.write_text(json.dumps(gui, indent=1, ensure_ascii=False), encoding="utf-8")
    print("ok", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
