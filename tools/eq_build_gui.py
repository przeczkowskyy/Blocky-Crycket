#!/usr/bin/env python3
"""Generuje src/gui/EquipmentPanel.model.json (Rojo) z assets/processed/EquipmentPanel/layout.json.

Struktura i nazwy = ramka Figmy „EquipmentPanel” (plik BbLd4jDnvxAmOWZN1hAZQJ, strona „Equipment Panel”, node 23:74).
ID obrazów bierze z assets/manifest.json (pole roblox_image); brak ID -> rbxassetid://0 + atrybut FigmaAsset.
Po uploadzie do Roblox wystarczy uruchomić skrypt ponownie.

Użycie: python tools/eq_build_gui.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
L = json.loads((ROOT / "assets/processed/EquipmentPanel/layout.json").read_text(encoding="utf-8"))
MAN = json.loads((ROOT / "assets/manifest.json").read_text(encoding="utf-8"))["assets"]
OUT = ROOT / "src/gui/EquipmentPanel.model.json"

FONT = {"Font": {"family": "rbxasset://fonts/families/LuckiestGuy.json", "weight": "Regular", "style": "Normal"}}


def c3(h):
    return [round(int(h[i:i + 2], 16) / 255, 4) for i in (0, 2, 4)]


def udim2(xs, ys, w, h):
    return {"Position": {"UDim2": [[round(xs, 5), 0], [round(ys, 5), 0]]},
            "Size": {"UDim2": [[round(w, 5), 0], [round(h, 5), 0]]}}


def rel(r, parent=None):
    """r = [x, y, w, h] w ułamkach panelu -> pozycja/rozmiar względem rodzica (też w ułamkach panelu)."""
    if parent is None:
        return udim2(*r)
    px, py, pw, ph = parent
    return udim2((r[0] - px) / pw, (r[1] - py) / ph, r[2] / pw, r[3] / ph)


def image(name):
    a = MAN.get(name, {})
    img = a.get("roblox_image")
    return (f"rbxassetid://{img}" if img else "rbxassetid://0"), ({} if img else {"FigmaAsset": f"assets/processed/EquipmentPanel/{name}.png"})


def node(name, cls, props, children=None, attrs=None):
    base = {} if cls.startswith("UI") else {"BorderSizePixel": 0}
    n = {"Name": name, "ClassName": cls, "Properties": {**base, **props}}
    if attrs:
        n["Attributes"] = attrs
    if children:
        n["Children"] = children
    return n


def corner(scale=0.0, off=0):
    return node("UICorner", "UICorner", {"CornerRadius": {"UDim": [scale, off]}})


# styl tekstu: kolor, obrys, grubość (px przy panelu 1376 px szerokości – skalowane w EquipmentPanelClient), max rozmiar
TEXT = {
    "title": ("FCE3B0", "2B1A10", 4, 70),
    # max rozmiary wg Game Directora (14.11): statystyki 15, zakładki postaci 16, zakładki plecaka 20
    "tab": ("FFFFFF", "1A1410", 3, 16),
    "tab_bag": ("FFFFFF", "1A1410", 3, 20),
    "name": ("F4F1E8", "0E1220", 2, 15),
    "value": ("FFD23F", "0E1220", 2, 15),
    "sub": ("3A2412", None, 0, 15),
    "level": ("E6FFC9", "0E3B12", 3, 36),
}


def text(name, r, s, style, parent=None, align="Center"):
    fill, stroke, sw, mx = TEXT[style]
    kids = [node("UITextSizeConstraint", "UITextSizeConstraint", {"MaxTextSize": mx, "MinTextSize": 6})]
    if stroke:
        kids.append(node("UIStroke", "UIStroke", {"Color": c3(stroke), "Thickness": sw, "LineJoinMode": "Round",
                                                  "ApplyStrokeMode": "Contextual"}))
    return node(name, "TextLabel", {
        **rel(r, parent), "BackgroundTransparency": 1, "Text": s, "TextColor3": c3(fill), "FontFace": FONT,
        "TextScaled": True, "TextXAlignment": align, "TextYAlignment": "Center", "TextWrapped": False,
    }, kids)


def cover(c):
    """Zasłonka wypalonej sylwetki slotu (widoczna tylko, gdy w slocie leży przedmiot): całe wnętrze slotu,
    ciemniejszy faz przy obrysie + jaśniejszy środek, jak w grafice."""
    x, y, w, h = c["rect"]
    bw, bh = c["bevel_px"] / c["size_px"][0], c["bevel_px"] / c["size_px"][1]
    return node("Cover", "Frame", {**udim2(x, y, w, h), "BackgroundColor3": c3(c["bevel"]),
                                   "Visible": False, "ZIndex": 1}, [
        corner(0.12),
        node("Inner", "Frame", {**udim2(bw, bh, 1 - 2 * bw, 1 - 2 * bh), "BackgroundColor3": c3(c["base"]),
                                "ZIndex": 1}, [corner(0.1)]),
    ])


def hotspot(name, r, parent=None, round_=0.12, circle=False, cover_=None):
    return node(name, "TextButton", {
        **rel(r, parent), "BackgroundTransparency": 1, "Text": "", "AutoButtonColor": False,
    }, ([cover(cover_)] if cover_ else []) + [
        corner(0.5 if circle else round_),
        node("Icon", "ImageLabel", {**udim2(0.12, 0.12, 0.76, 0.76), "BackgroundTransparency": 1, "Image": "", "ZIndex": 2,
                                    "ScaleType": "Fit"}),
    ])


def sprite_button(name, r, img_name, children=None, parent=None, anchor=(0.5, 0.5)):
    """anchor = punkt, wokół którego UIScale powiększa przycisk przy hoverze (Roblox skaluje względem AnchorPoint).
    Domyślnie środek; zakładki: środek dolnej krawędzi, żeby podstawa nie odjeżdżała od panelu."""
    img, attrs = image(img_name)
    kids = [node("UIScale", "UIScale", {"Scale": 1})] + (children or [])
    props = rel(r, parent)
    (xs, _), (ys, _) = props["Position"]["UDim2"]
    (ws, _), (hs, _) = props["Size"]["UDim2"]
    props["Position"] = {"UDim2": [[round(xs + ws * anchor[0], 5), 0], [round(ys + hs * anchor[1], 5), 0]]}
    return node(name, "ImageButton", {**props, "AnchorPoint": list(anchor), "BackgroundTransparency": 1, "Image": img,
                                      "ScaleType": "Stretch", "AutoButtonColor": False}, kids, attrs)


def full(name, children):
    return node(name, "Frame", {**udim2(0, 0, 1, 1), "BackgroundTransparency": 1}, children)


def main():
    S = L["sprites"]
    # tło: 4 kafelki (lekka zakładka 0.0008, żeby nie było szczelin przy zaokrągleniach)
    bg = []
    for n, (x, y, w, h) in L["bg_tiles"].items():
        img, attrs = image(n)
        bg.append(node(n, "ImageLabel", {**udim2(x, y, w + 0.0008, h + 0.0008), "BackgroundTransparency": 1,
                                         "Image": img, "ScaleType": "Stretch"}, None, attrs))

    lb = L["level_badge"]
    character = full("Character", [
        node("Portrait", "ViewportFrame", {**rel(L["portrait"]), "BackgroundTransparency": 1}),
        node("LevelBadge", "Frame", {**rel(lb), "BackgroundTransparency": 1}, [
            text("LevelText", L["texts"]["LevelText"][0], "LV 1", "level", lb)]),
        full("EquipSlots", [hotspot("Slot_" + k, r, cover_=L["slot_covers"][k]) for k, r in L["slots"].items()]),
    ])

    def tabs(names, group, style):
        out = []
        for i, n in enumerate(names):
            lab = L["texts"][n.replace("Eq", "") + "Label"]
            btn = sprite_button(n.replace("Eq", ""), S[n], n, [text("Label", lab[0], lab[1], style, S[n])],
                                anchor=(0.5, 1))
            btn["Properties"]["LayoutOrder"] = i + 1
            out.append(btn)
        return full(group, out)

    char_tabs = tabs(["EqTabAttributes", "EqTabDescription", "EqTabInfo", "EqTabInteractions"], "CharacterTabs", "tab")
    bag_tabs = tabs(["EqTabWeapons", "EqTabArmor", "EqTabAmulets", "EqTabOthers"], "BackpackTabs", "tab_bag")

    cards = []
    for k, c in L["cards"].items():
        cr = c["card"]
        cards.append(node("Card_" + k, "Frame", {**rel(cr), "BackgroundTransparency": 1}, [
            text("StatName", c["name"][0], c["name"][1], "name", cr, "Left"),
            text("StatValue", c["value"][0], c["value"][1], "value", cr, "Right"),
            text("StatSub", c["sub"][0], c["sub"][1], "sub", cr, "Left"),
            sprite_button("PlusButton", c["plus"], "EqPlus", parent=cr),
        ], {"Stat": k}))

    gui = {
        "ClassName": "ScreenGui",
        "Properties": {"Enabled": False, "ResetOnSpawn": False, "IgnoreGuiInset": True,
                       "ZIndexBehavior": "Sibling", "DisplayOrder": 20},
        "Children": [
            node("Backdrop", "TextButton", {**udim2(0, 0, 1, 1), "BackgroundColor3": [0, 0, 0],
                                            "BackgroundTransparency": 0.45, "Text": "", "AutoButtonColor": False}),
            node("Panel", "Frame", {"AnchorPoint": [0.5, 0.5], **udim2(0.5, 0.5, 0.94, 0.94),
                                    "BackgroundTransparency": 1}, [
                node("UIAspectRatioConstraint", "UIAspectRatioConstraint",
                     {"AspectRatio": L["aspect"], "AspectType": "FitWithinMaxSize", "DominantAxis": "Width"}),
                node("UIScale", "UIScale", {"Scale": 1}),
                # łapie kliknięcia w pusty obszar panelu, żeby nie trafiały do Backdrop (zamykanie)
                node("InputBlocker", "TextButton", {**udim2(0, 0, 1, 1), "BackgroundTransparency": 1, "Text": "",
                                                    "AutoButtonColor": False}),
                full("Background", bg),
                character,
                char_tabs,
                bag_tabs,
                full("Stats", cards),
                full("Potions", [hotspot(k, r, circle=True) for k, r in L["potions"].items()]),
                full("BackpackGrid", [hotspot(f"BagSlot{i + 1:02d}", r, round_=0.16) for i, r in enumerate(L["backpack"])]),
                full("Titles", [text("TitleCharacter", *L["texts"]["TitleCharacter"][:2], "title"),
                                text("TitleBackpack", *L["texts"]["TitleBackpack"][:2], "title")]),
                sprite_button("CloseButton", S["EqClose"], "EqClose"),
            ]),
        ],
    }
    OUT.write_text(json.dumps(gui, indent=1, ensure_ascii=False), encoding="utf-8")
    missing = [n for n in list(L["bg_tiles"]) + list(S) if not MAN.get(n, {}).get("roblox_image")]
    print(f"ok {OUT.relative_to(ROOT)}; brak ID Roblox: {len(missing)} ({', '.join(missing) if missing else '-'})")


if __name__ == "__main__":
    main()
