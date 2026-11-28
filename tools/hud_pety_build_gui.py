#!/usr/bin/env python3
"""HUD + okno petów (Paweł 25.11): przerabia src/gui/HUD.model.json (5 podłużnych przycisków w jednej kolumnie po
lewej — ikona i napis, bez gildii; Index zamiast Quests, wysuwana szuflada questów po prawej) i buduje src/gui/OknoPetow.model.json.
Grafiki z jednej generacji (tools/hud_pety_ui.py, ID w assets/manifest.json); pozycje slotów i przycisków to ułamki
obrazów zmierzone po kolorach 25.11. Skrypty: src/client/HUDClient, QuestyClient, OknoPetowClient.

Użycie: python tools/hud_pety_build_gui.py     (można uruchamiać wielokrotnie)
"""
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shop_build_gui as S  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HUD = ROOT / "src/gui/HUD.model.json"
node, text, hit, ud, c3, corner = S.node, S.text, S.hit, S.ud, S.c3, S.corner
CREAM, WHITE, GOLD, DARK = "FCE3B0", "FFFFFF", "FFD65A", "4A2E1A"
GOTHAM = {"Font": {"family": "rbxasset://fonts/families/GothamSSm.json", "weight": "Bold", "style": "Normal"}}


def img(name):
    i = S.MAN.get(name, {}).get("roblox_image")
    return f"rbxassetid://{i}" if i else ""


def ciemny(name, r, s, mx, z=5, x_align="Left", gruby=False):
    t = text(name, r, s, DARK, mx, 0, z)
    t["Properties"]["TextXAlignment"] = x_align
    t["Properties"]["TextWrapped"] = True
    if not gruby:
        t["Properties"]["FontFace"] = GOTHAM
    t["Children"] = [c for c in t["Children"] if c["ClassName"] != "UIStroke"]
    return t


# ------------------------------------------------------------------------------------------------ HUD
SRODEK_SZUFLADY = 0.46  # środek szuflady questów (i jej zakładki ze strzałką) na wysokości ekranu
# Paweł 25.11 (noc): pięć podłużnych przycisków jeden pod drugim (ikona po lewej, napis po prawej), bez gildii.
# Grafiki: tools/hud_podluzne_ui.py (HudWide*, proporcje 3,064). Wszystko w Scale: kolumna trzyma proporcje,
# siatka dzieli ją na komórki. Na telefonie (HUDClient) ta sama kolumna staje tuż pod panelem gracza i jest wyższa
# względem ekranu, żeby przyciski dało się trafić palcem (Paweł 26.11: jeden pod drugim także na telefonie).
PROP_PRZYCISKU = 3.0638
ODSTEP = 0.12  # odstęp między przyciskami jako ułamek wysokości przycisku
WYS_KOLUMNY = 0.45  # ułamek ekranu: przycisk ok. 89 × 272 px przy 1080p; góra kolumny tuż pod panelem gracza
PRZYCISKI = ["Teleport", "Equipment", "Pets", "Index", "Shop"]
NAPIS_ZOLTY, NAPIS_BIALY = ("FFE95A", "F7A81B"), ("FFFFFF", "D5DAE8")  # gradient góra -> dół, jak na starych ikonach
POLE_NAPISU = (0.35, 0.24, 0.615, 0.52)  # ułamek przycisku, na prawo od ikony (jak w hud_podluzne_napisy.py)


def znajdz(n, nazwa):
    if n.get("Name") == nazwa:
        return n
    for c in n.get("Children", []):
        w = znajdz(c, nazwa)
        if w:
            return w
    return None


def napis(nazwa, tekst, kolory, cien=False):
    """Napis natywny w stylu starych ikon: kanciasty Luckiest Guy, gradient, gruby czarny obrys, ciemny cień od dołu."""
    x, y, w, h = POLE_NAPISU
    t = node(nazwa, "TextLabel", {**ud(x, y + (0.075 if cien else 0), w, h), "BackgroundTransparency": 1,
                                  "Text": tekst, "TextColor3": c3("2A1608" if cien else "FFFFFF"), "FontFace": S.FONT,
                                  "TextScaled": True, "TextXAlignment": "Center", "TextYAlignment": "Center",
                                  "Active": False, "ZIndex": 2 if cien else 3},
             [node("UIStroke", "UIStroke", {"Color": c3("1A1008"), "Thickness": 4, "LineJoinMode": "Round",
                                            "ApplyStrokeMode": "Contextual"})])
    if not cien:
        t["Children"].append(node("UIGradient", "UIGradient", {"Rotation": 90, "Color": {"ColorSequence": {"keypoints": [
            {"time": 0, "color": c3(kolory[0])}, {"time": 1, "color": c3(kolory[1])}]}}}))
    return t


def slot_podluzny(nazwa, kolejnosc):
    # Napis: obrazek wycięty ze starej ikony (tools/hud_podluzne_napisy.py) — identyczne liternictwo jak dotąd.
    # Dopóki obrazka nie ma w Roblox, stoi napis natywny (Luckiest Guy), żeby przycisk nie był pusty.
    if img("HudLabel" + nazwa):
        x, y, w, h = POLE_NAPISU
        napisy = [node("Label", "ImageLabel", {**ud(x, y, w, h), "BackgroundTransparency": 1, "Active": False,
                                               "Image": img("HudLabel" + nazwa), "ScaleType": "Fit", "ZIndex": 3})]
    else:
        kolory = NAPIS_BIALY if nazwa == "Equipment" else NAPIS_ZOLTY  # Equipment był biały także na starej ikonie
        napisy = [napis("LabelShadow", nazwa.upper(), kolory, True), napis("Label", nazwa.upper(), kolory)]
    return node(nazwa + "Slot", "Frame", {"BackgroundTransparency": 1, "LayoutOrder": kolejnosc}, [
        node(nazwa, "ImageButton", {"AnchorPoint": [0.5, 0.5], **ud(0.5, 0.5, 1, 1), "BackgroundTransparency": 1,
                                    "Image": img("HudWide" + nazwa), "ScaleType": "Stretch", "AutoButtonColor": False},
             [node("UIScale", "UIScale", {"Scale": 1}), *napisy])])


def szuflada_questow():
    rzedy = [0.2216, 0.4605, 0.6995]
    dzieci = [
        node("UIAspectRatioConstraint", "UIAspectRatioConstraint", {"AspectRatio": 1.107, "AspectType": "FitWithinMaxSize",
                                                                     "DominantAxis": "Height"}),
        node("Panel", "ImageLabel", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "Image": img("PanelQuestow"),
                                     "ScaleType": "Stretch", "ZIndex": 2}),
        text("Title", (0.25, 0.035, 0.5, 0.105), "QUESTS", CREAM, 34, 2.5, 4),
        node("TabOpenArt", "ImageLabel", {**ud(0, 0, 0, 0), "BackgroundTransparency": 1, "Visible": False,
                                          "Image": img("ZakladkaQuestowSchowaj")}),
        node("Tab", "ImageButton", {"AnchorPoint": [1, 0.5], "Position": {"UDim2": [[0.03, 0], [0.5, 0]]},
                                    "Size": {"UDim2": [[0.2, 0], [0.34, 0]]}, "BackgroundTransparency": 1,
                                    "Image": img("ZakladkaQuestowWysun"), "ScaleType": "Fit", "AutoButtonColor": False,
                                    "ZIndex": 1}, [node("UIScale", "UIScale", {"Scale": 1})]),
    ]
    for i, y in enumerate(rzedy, 1):
        dzieci.append(node(f"Quest{i}", "Frame", {**ud(0.0977, y, 0.7627, 0.19), "BackgroundTransparency": 1, "ZIndex": 3}, [
            text("Check", (0.011, 0.22, 0.12, 0.56), "", "3FAE4F", 30, 2, 5),
            ciemny("Name", (0.16, 0.12, 0.62, 0.4), "", 20, 5, "Left", True),
            ciemny("Progress", (0.16, 0.54, 0.62, 0.32), "", 15, 5),
            node("RewardIcon", "ImageLabel", {**ud(0.8, 0.27, 0.085, 0.46), "BackgroundTransparency": 1, "Image": "",
                                              "ScaleType": "Fit", "ZIndex": 5}),
            text("Reward", (0.885, 0.27, 0.15, 0.46), "", GOLD, 18, 1.5, 5),
        ]))
    return node("QuestDrawer", "Frame", {"AnchorPoint": [1, 0.5], "Position": {"UDim2": [[1, 0], [SRODEK_SZUFLADY, 0]]},
                                         "Size": {"UDim2": [[0.34, 0], [0.38, 0]]}, "BackgroundTransparency": 1}, dzieci)


def hud():
    g = json.loads(HUD.read_text(encoding="utf-8"))
    n = len(PRZYCISKI)
    jedn = n + (n - 1) * ODSTEP  # wysokość kolumny w wysokościach przycisku
    # Kolumna nazywa się nadal „LeftColumn”, bo wskazówki Karola (swiat/wskazowki_gry) szukają przycisku pod ścieżką
    # HUD/LeftColumn/TeleportSlot/Teleport.
    dz = [
        node("UIAspectRatioConstraint", "UIAspectRatioConstraint", {"AspectRatio": round(PROP_PRZYCISKU / jedn, 4),
                                                                     "AspectType": "ScaleWithParentSize",
                                                                     "DominantAxis": "Height"}),
        node("UIGridLayout", "UIGridLayout", {"FillDirection": "Vertical", "FillDirectionMaxCells": n,
                                              "SortOrder": "LayoutOrder", "StartCorner": "TopLeft",
                                              "HorizontalAlignment": "Left", "VerticalAlignment": "Top",
                                              "CellSize": {"UDim2": [[1, 0], [round(1 / jedn, 5), 0]]},
                                              "CellPadding": {"UDim2": [[0, 0], [round(ODSTEP / jedn, 5), 0]]}}),
    ]
    dz += [slot_podluzny(nazwa, k) for k, nazwa in enumerate(PRZYCISKI, 1)]
    # Gildie wyłączone „na razie” (Paweł 25.11): przycisk zostaje w modelu, ukryty — siatka pomija ukryte elementy.
    gildie = znajdz(g, "GuildsSlot")
    if gildie:
        gildie = copy.deepcopy(gildie)
        gildie["Properties"].update({"Visible": False, "LayoutOrder": 99})
        dz.append(gildie)
    kolumna = node("LeftColumn", "Frame", {"BackgroundTransparency": 1, "AnchorPoint": [0, 0.5],
                                           "Position": {"UDim2": [[0.02083, 0], [SRODEK_SZUFLADY, 0]]},
                                           "Size": {"UDim2": [[1, 0], [WYS_KOLUMNY, 0]]}}, dz)
    g["Children"] = [c for c in g["Children"]
                     if c.get("Name") not in ("LeftColumn", "RightColumn", "BottomRow", "ButtonGrid", "QuestDrawer")]
    g["Children"] += [kolumna, szuflada_questow()]
    HUD.write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ok", HUD.relative_to(ROOT))


# ------------------------------------------------------------------------------------------------ okno petów
PROPORCJE = 3382 / 2826
PLECAK_X0, PLECAK_DX, PLECAK_W, PLECAK_H = 0.0967, 0.102, 0.0866, 0.1026
PLECAK_Y = [0.4597, 0.5807, 0.7013]
ZALOZONE = [(0.0863, 0.1872, 0.135, 0.168), (0.2614, 0.1872, 0.135, 0.168), (0.4365, 0.1872, 0.135, 0.168),
            (0.6116, 0.1872, 0.135, 0.168)]


def widok_peta(z=7):
    return node("View", "ViewportFrame", {**ud(0.08, 0.08, 0.84, 0.84), "BackgroundTransparency": 1, "ZIndex": z,
                                          "Ambient": c3("C8C8C8"), "LightColor": c3("FFFFFF")})


def obwodka(kolor="FFD65A", grubosc=3):
    return node("Rim", "Frame", {**ud(0.03, 0.03, 0.94, 0.94), "BackgroundTransparency": 1, "Visible": False, "ZIndex": 6},
                [corner(0.16), node("UIStroke", "UIStroke", {"Color": c3(kolor), "Thickness": grubosc})])


def slot_zalozony(i, r):
    return node(f"Equipped{i}", "ImageButton", {**ud(*r), "BackgroundTransparency": 1, "Image": "", "AutoButtonColor": False,
                                                "ZIndex": 6}, [
        obwodka(), widok_peta(),
        text("PetName", (0.02, 0.76, 0.96, 0.2), "", WHITE, 15, 1.5, 9),
    ])


def slot_peta(i, x, y):
    return node(f"Pet{i:02d}", "ImageButton", {**ud(x, y, PLECAK_W, PLECAK_H), "BackgroundTransparency": 1, "Image": "",
                                               "AutoButtonColor": False, "ZIndex": 6}, [
        obwodka(), widok_peta(),
        text("Count", (0.5, 0.02, 0.46, 0.3), "", WHITE, 15, 1.5, 9),
        text("PetName", (0.03, 0.72, 0.94, 0.25), "", WHITE, 12, 1.5, 9),
        text("Mark", (0.04, 0.02, 0.4, 0.34), "", "8CE865", 18, 2, 9),
    ])


def podpowiedz():
    """Podpowiedź przy najechaniu na peta: nazwa, rzadkość, co daje graczowi (premie i pasywy z danych Karola)."""
    return node("Tooltip", "ImageLabel", {"AnchorPoint": [0, 0], "Position": {"UDim2": [[0.6, 0], [0.3, 0]]},
                                          "Size": {"UDim2": [[0.25, 0], [0.4, 0]]}, "BackgroundTransparency": 1,
                                          "Image": img("PodpowiedzPeta"), "ScaleType": "Stretch",
                                          "Visible": False, "ZIndex": 40}, [
        node("UIAspectRatioConstraint", "UIAspectRatioConstraint", {"AspectRatio": 1.6842, "AspectType": "FitWithinMaxSize",
                                                                     "DominantAxis": "Width"}),
        node("UISizeConstraint", "UISizeConstraint", {"MinSize": [250, 148], "MaxSize": [480, 285]}),
        text("PetName", (0.08, 0.1, 0.84, 0.19), "", WHITE, 30, 2, 41),
        text("Rarity", (0.08, 0.3, 0.84, 0.13), "", GOLD, 20, 1.5, 41),
        {**ciemny("Skill", (0.1, 0.46, 0.8, 0.3), "", 17, 41), "Properties": {
            **ciemny("Skill", (0.1, 0.46, 0.8, 0.3), "", 17, 41)["Properties"], "TextColor3": c3(CREAM),
            "TextYAlignment": "Top"}},
        text("Copies", (0.08, 0.77, 0.84, 0.11), "", "9FD7FF", 15, 1.5, 41),
    ])


def okno_petow():
    sloty, i = [], 1
    for y in PLECAK_Y:
        for k in range(8):
            sloty.append(slot_peta(i, PLECAK_X0 + k * PLECAK_DX, y))
            i += 1
    panel = node("Panel", "Frame", {"AnchorPoint": [0.5, 0.5], **ud(0.5, 0.5, 0.86, 0.9), "BackgroundTransparency": 1}, [
        node("UIAspectRatioConstraint", "UIAspectRatioConstraint", {"AspectRatio": round(PROPORCJE, 5),
                                                                     "AspectType": "FitWithinMaxSize", "DominantAxis": "Width"}),
        node("UIScale", "UIScale", {"Scale": 1}),
        node("InputBlocker", "TextButton", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "Text": "", "AutoButtonColor": False}),
        node("Art", "Frame", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "ZIndex": 1}, [
            node(f"Tile{n}", "ImageLabel", {**ud(cx * 0.5, cy * 0.5, 0.5, 0.5), "BackgroundTransparency": 1,
                                            "Image": img(f"OknoPetow{n}"), "ScaleType": "Stretch", "ZIndex": 1})
            for n, (cx, cy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)], 1)]),
        hit("CloseButton", (0.9305, 0.0343, 0.0645, 0.0672)),
        text("Title", (0.33, 0.022, 0.34, 0.078), "PETS", CREAM, 44),
        *[slot_zalozony(n, r) for n, r in enumerate(ZALOZONE, 1)],
        text("EquippedLabel", (0.775, 0.195, 0.14, 0.04), "EQUIPPED", CREAM, 16, 1.5, 6),
        text("EquippedCount", (0.7907, 0.2403, 0.1082, 0.0548), "0/2", GOLD, 26, 2, 6),
        text("OwnedLabel", (0.075, 0.378, 0.5, 0.04), "MY PETS", CREAM, 20, 2, 6),
        text("Message", (0.42, 0.378, 0.5, 0.04), "", "FFB0A0", 18, 2, 8),
        *sloty,
        hit("EquipBestButton", (0.0819, 0.8843, 0.3143, 0.0832)),
        hit("UnequipButton", (0.4361, 0.8811, 0.21, 0.077)),
        hit("DeleteButton", (0.6863, 0.8808, 0.215, 0.0775)),
        text("EquipBestLabel", (0.0919, 0.894, 0.2943, 0.058), "EQUIP BEST", WHITE, 26, 2, 7),
        text("UnequipLabel", (0.4461, 0.892, 0.19, 0.054), "UNEQUIP ALL", WHITE, 20, 2, 7),
        text("DeleteLabel", (0.6963, 0.892, 0.195, 0.054), "DELETE", WHITE, 22, 2, 7),
    ])
    for n in ("OwnedLabel",):
        znajdz(panel, n)["Properties"]["TextXAlignment"] = "Left"
    znajdz(panel, "Message")["Properties"]["TextXAlignment"] = "Right"
    gui = {"ClassName": "ScreenGui",
           "Properties": {"Enabled": False, "ResetOnSpawn": False, "IgnoreGuiInset": True, "ZIndexBehavior": "Sibling",
                          "DisplayOrder": 25},
           "Children": [node("Backdrop", "TextButton", {**ud(0, 0, 1, 1), "BackgroundColor3": [0, 0, 0],
                                                        "BackgroundTransparency": 0.45, "Text": "", "AutoButtonColor": False}),
                        panel, podpowiedz()]}
    out = ROOT / "src/gui/OknoPetow.model.json"
    out.write_text(json.dumps(gui, indent=1, ensure_ascii=False), encoding="utf-8")
    print("ok", out.relative_to(ROOT))


if __name__ == "__main__":
    hud()
    okno_petow()
