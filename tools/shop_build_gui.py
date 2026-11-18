#!/usr/bin/env python3
"""Generuje src/gui/Shop.model.json — okno sklepu (sklep z bronią i sklep magiczny, Paweł 18.11).

Grafika: tools/sklep_okno.py → assets/processed/Sklepy/SklepBron1–4.png, SklepMagia1–4.png (kafelki 2 × 2, ID
w assets/manifest.json). Układ elementów: assets/processed/Sklepy/uklad_sklepow.json. Napisy natywne (Luckiest Guy).
Logika: src/client/ShopClient.client.luau (otwieranie zdarzeniem OknoMiejsca z pakietu Karola i kliknięciem
na sprzedawcy). Makieta: Figma, ramki ShopWeapon (46:115) i ShopMagic (46:125). Projekt: B&C/UI/Sklepy i bronie startowe — prompty.md.

Użycie: python tools/shop_build_gui.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAN = json.loads((ROOT / "assets/manifest.json").read_text(encoding="utf-8"))["assets"]
L = json.loads((ROOT / "assets/processed/Sklepy/uklad_sklepow.json").read_text(encoding="utf-8"))
OUT = ROOT / "src/gui/Shop.model.json"
FONT = {"Font": {"family": "rbxasset://fonts/families/LuckiestGuy.json", "weight": "Regular", "style": "Normal"}}


def c3(h):
    return [round(int(h[i:i + 2], 16) / 255, 4) for i in (0, 2, 4)]


def img(name):
    i = MAN.get(name, {}).get("roblox_image")
    return f"rbxassetid://{i}" if i else "rbxassetid://0"


def ud(x, y, w, h):
    return {"Position": {"UDim2": [[x, 0], [y, 0]]}, "Size": {"UDim2": [[w, 0], [h, 0]]}}


def node(name, cls, props, children=None):
    base = {} if cls.startswith("UI") else {"BorderSizePixel": 0}
    n = {"Name": name, "ClassName": cls, "Properties": {**base, **props}}
    if children:
        n["Children"] = children
    return n


def text(name, r, s, fill, mx, st=3, z=5):
    return node(name, "TextLabel", {**ud(*r), "BackgroundTransparency": 1, "Text": s, "TextColor3": c3(fill), "FontFace": FONT,
                                    "TextXAlignment": "Center", "TextYAlignment": "Center", "TextScaled": True, "ZIndex": z},
                [node("UITextSizeConstraint", "UITextSizeConstraint", {"MaxTextSize": mx, "MinTextSize": 6}),
                 node("UIStroke", "UIStroke", {"Color": c3("1A1410"), "Thickness": st, "LineJoinMode": "Round",
                                               "ApplyStrokeMode": "Contextual"})])


def hit(name, r, z=6):
    """Niewidzialne pole kliknięcia nad elementem z grafiki (przycisk wypalony w tle — reakcję robi klient)."""
    return node(name, "ImageButton", {**ud(*r), "BackgroundTransparency": 1, "Image": "", "AutoButtonColor": False, "ZIndex": z})


def art(nazwa, widoczna):
    tiles = [node(f"Tile{i}", "ImageLabel", {**ud(cx * 0.5, cy * 0.5, 0.5, 0.5), "BackgroundTransparency": 1,
                                             "Image": img(f"Sklep{nazwa}{i}"), "ScaleType": "Stretch", "ZIndex": 1})
             for i, (cx, cy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)], 1)]
    return node(f"Art{nazwa}", "Frame", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "Visible": widoczna, "ZIndex": 1}, tiles)


def main():
    cream, white = "FCE3B0", "FFFFFF"
    zakladki = [text(f"Tab{i + 1}", r, s, white, 11, 1.5) for i, (r, s) in
                enumerate(zip(L["zakladki"], ["WEAPONS", "ARMOR", "AMULETS", "OTHERS"]))]
    panel = node("Panel", "Frame", {"AnchorPoint": [0.5, 0.5], **ud(0.5, 0.5, 0.86, 0.9), "BackgroundTransparency": 1}, [
        node("UIAspectRatioConstraint", "UIAspectRatioConstraint", {"AspectRatio": L["proporcje"], "AspectType": "FitWithinMaxSize",
                                                                     "DominantAxis": "Width"}),
        node("UIScale", "UIScale", {"Scale": 1}),
        node("InputBlocker", "TextButton", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "Text": "", "AutoButtonColor": False}),
        art("Bron", True), art("Magia", False),
        text("TitleLeft", L["tytul_lewy"], "HERO", cream, 42),
        text("TitleRight", L["tytul_prawy"], "WEAPON SHOP", cream, 42),
        text("Level", L["poziom"], "LV 1", white, 24, 2),
        *zakladki,
        text("Plate", L["tabliczka"], "NEW GOODS", cream, 34),
        hit("CloseButton", L["zamknij"]),
        hit("RerollButton", L["odswiez"]),
        *[hit(f"ShopSlot{i + 1}", r) for i, r in enumerate(L["sloty_sklepu"])],
    ])
    gui = {"ClassName": "ScreenGui",
           "Properties": {"Enabled": False, "ResetOnSpawn": False, "IgnoreGuiInset": True, "ZIndexBehavior": "Sibling", "DisplayOrder": 24},
           "Children": [node("Backdrop", "TextButton", {**ud(0, 0, 1, 1), "BackgroundColor3": [0, 0, 0], "BackgroundTransparency": 0.45,
                                                        "Text": "", "AutoButtonColor": False}), panel]}
    OUT.write_text(json.dumps(gui, indent=1, ensure_ascii=False), encoding="utf-8")
    brak = [f"Sklep{n}{i}" for n in ("Bron", "Magia") for i in range(1, 5) if img(f"Sklep{n}{i}").endswith("//0")]
    print(f"ok {OUT.relative_to(ROOT)}; bez ID Roblox: {brak or '-'}")


if __name__ == "__main__":
    main()
