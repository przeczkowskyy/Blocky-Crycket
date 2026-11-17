#!/usr/bin/env python3
"""Generuje okno drzewka umiejętności dla Rojo:
  - src/gui/SkillTree.model.json  (ScreenGui „SkillTree”: ramka, zakładki, obszar mapy, pasek szczegółów)
  - src/shared/SkillTreeIcons.luau (nazwa grafiki -> rbxassetid z assets/manifest.json)

Układ z assets/processed/SkillTree/layout.json (tools/skilltree_assets.py). Węzły mapy rysuje klient
(src/client/SkillTreeClient.client.luau) z ReplicatedStorage.Shared.SkillTreeData.
Projekt: B&C/UI/Okno drzewka umiejętności.md (makieta Figma: strona „Equipment Panel”, ramka 33:78).

Użycie: python tools/skilltree_build_gui.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
L = json.loads((ROOT / "assets/processed/SkillTree/layout.json").read_text(encoding="utf-8"))
MAN = json.loads((ROOT / "assets/manifest.json").read_text(encoding="utf-8"))["assets"]
OUT = ROOT / "src/gui/SkillTree.model.json"
ICONS_OUT = ROOT / "src/shared/SkillTreeIcons.luau"

FONT = {"Font": {"family": "rbxasset://fonts/families/LuckiestGuy.json", "weight": "Regular", "style": "Normal"}}
INK = "1A1410"


def c3(h):
    return [round(int(h[i:i + 2], 16) / 255, 4) for i in (0, 2, 4)]


def img(name):
    i = MAN.get(name, {}).get("roblox_image")
    return f"rbxassetid://{i}" if i else "rbxassetid://0"


def ud(xs, ys, w, h):
    return {"Position": {"UDim2": [[round(xs, 5), 0], [round(ys, 5), 0]]},
            "Size": {"UDim2": [[round(w, 5), 0], [round(h, 5), 0]]}}


def node(name, cls, props, children=None):
    base = {} if cls.startswith("UI") else {"BorderSizePixel": 0}
    n = {"Name": name, "ClassName": cls, "Properties": {**base, **props}}
    if children:
        n["Children"] = children
    return n


def corner(s=0.0, o=0):
    return node("UICorner", "UICorner", {"CornerRadius": {"UDim": [s, o]}})


def stroke(color=INK, t=3, mode="Contextual"):
    return node("UIStroke", "UIStroke", {"Color": c3(color), "Thickness": t, "LineJoinMode": "Round", "ApplyStrokeMode": mode})


def text(name, pos, s, fill, mx, align="Center", st=3, z=1):
    return node(name, "TextLabel", {**pos, "BackgroundTransparency": 1, "Text": s, "TextColor3": c3(fill), "FontFace": FONT,
                                    "TextScaled": True, "TextXAlignment": align, "TextYAlignment": "Center", "ZIndex": z},
                [node("UITextSizeConstraint", "UITextSizeConstraint", {"MaxTextSize": mx, "MinTextSize": 6})]
                + ([stroke(t=st)] if st else []))


def rel(r, parent):
    """r i parent = [x, y, w, h] w ułamkach okna -> pozycja względem rodzica."""
    px, py, pw, ph = parent
    return ud((r[0] - px) / pw, (r[1] - py) / ph, r[2] / pw, r[3] / ph)


def main():
    W, H = L["frame_px"]
    C = L["content"]
    tabs = []
    for i, (key, label) in enumerate([("TabPlayer", "PLAYER"), ("TabFortress", "FORTRESS"), ("TabPets", "PETS")]):
        x, y, w, h = L["tabs"][key]
        # zakładki i X są wymazane z grafiki ramki (tools/skilltree_assets.py, Paweł 17.11) — pod przyciskiem nic nie leży
        # kotwica = środek dolnej krawędzi: przy hoverze zakładka rośnie w górę, podstawa zostaje przy oknie
        tabs.append(node(key, "ImageButton", {
            "AnchorPoint": [0.5, 1], **ud(x + w / 2, y + h, w, h), "BackgroundTransparency": 1,
            "Image": img("SkillTree" + key), "ScaleType": "Stretch", "AutoButtonColor": False, "LayoutOrder": i + 1, "ZIndex": 3,
        }, [node("UIScale", "UIScale", {"Scale": 1}),
            # środek korpusu zakładki ~0.52; Luckiest Guy rysuje litery wyżej niż środek pola, więc pole niżej (środek 0.57)
            text("Label", ud(0.12, 0.33, 0.76, 0.48), label, "FFFFFF", 20, z=4)]))

    cw, ch = C[2] * W, C[3] * H  # obszar treści w px makiety (836 x 442)
    bar_h = 56 / ch
    content = node("Content", "Frame", {**ud(*C), "BackgroundTransparency": 1, "ClipsDescendants": True, "ZIndex": 2}, [
        corner(0, 10),
        # jedno tło dla wszystkich zakładek: gwiazdozbiory rycerza i kota-maga (Paweł 17.11)
        node("Bg", "ImageLabel", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "Image": img("SkillTreeBgStars") if not img("SkillTreeBgStars").endswith("//0") else img("SkillTreeBgPlayer"),
                                  "ScaleType": "Crop", "ZIndex": 1}),
        node("Shade", "Frame", {**ud(0, 0, 1, 1), "BackgroundColor3": c3("140D08"), "BackgroundTransparency": 0.85, "ZIndex": 2}),
        # mapa: rozmiar 0, węzły jako dzieci z pozycją w px makiety; UIScale = skala ekranu × zoom (klient)
        node("Map", "Frame", {"AnchorPoint": [0, 0], **ud(0.5, 0.42, 0, 0), "BackgroundTransparency": 1, "ZIndex": 3},
             [node("UIScale", "UIScale", {"Scale": 1})]),
        # krótka podpowiedź w poprzedniej wielkości (dłuższy tekst zmniejszał czcionkę — uwaga Pawła 17.11);
        # „HOLD TO UPGRADE” pokazuje pasek szczegółów na dole
        text("Hint", ud(0.3, 0.025, 0.4, 0.045), "DRAG TO EXPLORE", "FFFFFF", 14, z=6),
        node("DetailBar", "Frame", {**ud(0.01, 1 - bar_h - 0.012, 0.98, bar_h), "BackgroundColor3": c3("1A1410"),
                                    "BackgroundTransparency": 0.25, "Visible": False, "ZIndex": 7}, [
            corner(0, 14),
            text("NodeName", ud(0.025, 0.1, 0.6, 0.42), "", "FFD23F", 18, "Left", z=8),
            text("NodeDesc", ud(0.025, 0.54, 0.7, 0.36), "", "FFFFFF", 14, "Left", 2, z=8),
            # bez przycisku UNLOCK (Paweł 17.11): ulepszenie = przytrzymanie kółka; tu tylko podpowiedź
            text("HoldHint", ud(0.74, 0.22, 0.24, 0.56), "HOLD TO UPGRADE", "8AF0FF", 16, "Right", z=8),
        ]),
    ])

    # X: niewidoczne pole kliknięcia dokładnie nad czerwonym korpusem X wypalonego w ramce (px makiety 974 × 717).
    # Wcześniej leżał tu X z ekwipunku — inna grafika, spod której wychodził jasny róg (uwaga Pawła 17.11)
    cx, cy, cw_, ch_ = 891 / W, 11 / H, 81 / W, 84 / H
    gui = {
        "ClassName": "ScreenGui",
        "Properties": {"Enabled": False, "ResetOnSpawn": False, "IgnoreGuiInset": True, "ZIndexBehavior": "Sibling", "DisplayOrder": 25},
        "Children": [
            node("Backdrop", "TextButton", {**ud(0, 0, 1, 1), "BackgroundColor3": [0, 0, 0], "BackgroundTransparency": 0.45,
                                            "Text": "", "AutoButtonColor": False}),
            node("Panel", "Frame", {"AnchorPoint": [0.5, 0.5], **ud(0.5, 0.5, 0.92, 0.88), "BackgroundTransparency": 1}, [
                node("UIAspectRatioConstraint", "UIAspectRatioConstraint", {"AspectRatio": L["aspect"], "AspectType": "FitWithinMaxSize",
                                                                             "DominantAxis": "Width"}),
                node("UIScale", "UIScale", {"Scale": 1}),
                node("InputBlocker", "TextButton", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "Text": "", "AutoButtonColor": False}),
                node("FrameArt", "ImageLabel", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "Image": img("SkillTreeFrame"),
                                                "ScaleType": "Stretch", "ZIndex": 1}),
                content,
                node("Tabs", "Frame", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "ZIndex": 3}, tabs),
                # napis na środku drewnianej tabliczki (deska: y 6–80 px z 717), z zapasem, żeby nie wystawał
                text("Title", ud(L["title"][0] + L["title"][2] * 0.1, 0.034, L["title"][2] * 0.8, 0.072), "SKILL TREE", "FCE3B0", 30, st=3, z=4),
                node("CloseButton", "ImageButton", {"AnchorPoint": [0.5, 0.5], **ud(cx + cw_ / 2, cy + ch_ / 2, cw_, ch_),
                                                    "BackgroundTransparency": 1, "Image": "", "ScaleType": "Fit",
                                                    "AutoButtonColor": False, "ZIndex": 5},
                     [node("UIScale", "UIScale", {"Scale": 1})]),
            ]),
        ],
    }
    OUT.write_text(json.dumps(gui, indent=1, ensure_ascii=False), encoding="utf-8")

    names = sorted({n for n in MAN if n.startswith(("Node", "SkillTree"))} | {"Gem", "EqClose"})
    lines = ["-- WYGENEROWANE przez tools/skilltree_build_gui.py z assets/manifest.json — nie edytuj ręcznie.",
             "-- Ikony drzewka umiejętności: nazwa grafiki -> asset id (ReplicatedStorage.Shared.SkillTreeIcons).", "return {"]
    lines += [f'\t{n} = "{img(n)}",' for n in names]
    lines.append("}")
    ICONS_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    missing = [n for n in names if img(n).endswith("//0")]
    print(f"ok {OUT.relative_to(ROOT)}, {ICONS_OUT.relative_to(ROOT)} ({len(names)} ikon); bez ID: {missing or '-'}")


if __name__ == "__main__":
    main()
