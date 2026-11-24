#!/usr/bin/env python3
"""Okna kowala, jajka i mistrza gier (Paweł 24.11) -> src/gui/OknoKowala.model.json, OknoJajka.model.json,
OknoMistrzaGier.model.json. Grafika z jednej generacji (tools/okna_ui.py, kafelki 2 × 2, ID w assets/manifest.json),
na niej natywne napisy i niewidzialne pola kliknięć w miejscach wypalonych slotów i przycisków (ułamki obrazu,
zmierzone 24.11 na podglądach z siatką). Konwencje jak tools/shop_build_gui.py (te same pomocnicze funkcje).
Skrypty: src/client/OknoKowalaClient, OknoJajkaClient, OknoMistrzaGierClient.

Użycie: python tools/okna_build_gui.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shop_build_gui as S  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROPORCJE = 4615 / 3355
node, text, hit, ud, c3, corner = S.node, S.text, S.hit, S.ud, S.c3, S.corner
CREAM, WHITE, GOLD, DARK = "FCE3B0", "FFFFFF", "FFD65A", "4A2E1A"


def img(name):
    i = S.MAN.get(name, {}).get("roblox_image")
    return f"rbxassetid://{i}" if i else "rbxassetid://0"


def art(nazwa):
    tiles = [node(f"Tile{i}", "ImageLabel", {**ud(cx * 0.5, cy * 0.5, 0.5, 0.5), "BackgroundTransparency": 1,
                                             "Image": img(f"{nazwa}{i}"), "ScaleType": "Stretch", "ZIndex": 1})
             for i, (cx, cy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)], 1)]
    return node("Art", "Frame", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "ZIndex": 1}, tiles)


def ciemny(name, r, s, mx, z=5, x_align="Center"):
    """Ciemny napis bez obrysu (na pergaminie)."""
    t = text(name, r, s, DARK, mx, 0, z)
    t["Properties"]["TextXAlignment"] = x_align
    t["Properties"]["TextWrapped"] = True
    t["Children"] = [c for c in t["Children"] if c["ClassName"] != "UIStroke"]
    return t


def okno(nazwa, dzieci, kolejnosc):
    panel = node("Panel", "Frame", {"AnchorPoint": [0.5, 0.5], **ud(0.5, 0.5, 0.86, 0.9), "BackgroundTransparency": 1}, [
        node("UIAspectRatioConstraint", "UIAspectRatioConstraint", {"AspectRatio": round(PROPORCJE, 5),
                                                                     "AspectType": "FitWithinMaxSize", "DominantAxis": "Width"}),
        node("UIScale", "UIScale", {"Scale": 1}),
        node("InputBlocker", "TextButton", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "Text": "", "AutoButtonColor": False}),
        art(nazwa),
        hit("CloseButton", (0.94, 0.014, 0.053, 0.073)),
        *dzieci,
    ])
    gui = {"ClassName": "ScreenGui",
           "Properties": {"Enabled": False, "ResetOnSpawn": False, "IgnoreGuiInset": True, "ZIndexBehavior": "Sibling",
                          "DisplayOrder": kolejnosc},
           "Children": [node("Backdrop", "TextButton", {**ud(0, 0, 1, 1), "BackgroundColor3": [0, 0, 0],
                                                        "BackgroundTransparency": 0.45, "Text": "", "AutoButtonColor": False}),
                        panel]}
    out = ROOT / f"src/gui/{nazwa}.model.json"
    out.write_text(json.dumps(gui, indent=1, ensure_ascii=False), encoding="utf-8")
    print("ok", out.relative_to(ROOT))


# ------------------------------------------------------------------------------------------------ kowal
def slot_przedmiotu(i, r):
    return node(f"Item{i:02d}", "ImageButton", {**ud(*r), "BackgroundTransparency": 1, "Image": "", "AutoButtonColor": False,
                                                "ZIndex": 6}, [
        node("Select", "Frame", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "Visible": False, "ZIndex": 6},
             [corner(0.15), node("UIStroke", "UIStroke", {"Color": c3("FFD65A"), "Thickness": 3})]),
        text("ItemName", (0.06, 0.18, 0.88, 0.5), "", WHITE, 13, 1.5, 7),
        text("Lvl", (0.05, 0.66, 0.9, 0.28), "", GOLD, 15, 1.5, 8),
        text("Spare", (0.5, 0.02, 0.48, 0.26), "", "8CE865", 13, 1.5, 8),
    ])


def kowal():
    kol = [0.075, 0.152, 0.227]
    rzedy_a = [0.135, 0.239, 0.342, 0.447]
    rzedy_b = [0.614, 0.717, 0.82]
    wh = (0.068, 0.094)
    sloty, i = [], 1
    for rz in rzedy_a + rzedy_b:
        for x in kol:
            sloty.append(slot_przedmiotu(i, (x, rz, *wh)))
            i += 1
    przed_po = []
    for nazwa, x in (("Before", 0.369), ("After", 0.534)):
        przed_po.append(node(nazwa, "Frame", {**ud(x, 0.151, 0.081, 0.141), "BackgroundTransparency": 1, "ZIndex": 6}, [
            text("ItemName", (0.05, 0.12, 0.9, 0.5), "", WHITE, 14, 1.5, 7),
            text("Lvl", (0.0, 0.6, 1.0, 0.34), "", GOLD, 22, 2, 7),
        ]))
    kolka = [text(f"Circle{n}", (x, 0.575, 0.073, 0.101), "", WHITE, 22, 2, 6) for n, x in ((1, 0.372), (2, 0.453), (3, 0.537))]
    podpisy = [text(f"CircleLabel{n}", (x - 0.01, 0.676, 0.093, 0.022), s, CREAM, 11, 1.2, 6)
               for n, x, s in ((1, 0.372, "LEVEL"), (2, 0.453, "MATERIALS"), (3, 0.537, "SPARE"))]
    okno("OknoKowala", [
        text("Title", (0.108, 0.006, 0.292, 0.08), "BLACKSMITH", CREAM, 40),
        *sloty,
        *przed_po,
        ciemny("Stats", (0.39, 0.36, 0.205, 0.175), "Pick an item on the left", 18),
        *kolka, *podpisy,
        text("Price", (0.407, 0.695, 0.167, 0.071), "", GOLD, 20, 2),
        hit("UpgradeButton", (0.36, 0.789, 0.122, 0.128)),
        hit("ScrapButton", (0.502, 0.789, 0.122, 0.128)),
        text("UpgradeLabel", (0.36, 0.905, 0.122, 0.03), "UPGRADE", WHITE, 14, 1.5, 7),
        text("ScrapLabel", (0.502, 0.905, 0.122, 0.03), "SCRAP", WHITE, 14, 1.5, 7),
        text("Message", (0.655, 0.085, 0.3, 0.07), "", WHITE, 20, 2, 8),
        text("Materials", (0.655, 0.85, 0.3, 0.05), "", CREAM, 18, 2, 8),
    ], 25)


# ------------------------------------------------------------------------------------------------ jajko
def jajko():
    kol = [0.542, 0.682, 0.821]
    rzedy = [0.14, 0.415]
    tabliczki = [0.333, 0.61]
    sloty, i = [], 1
    for rz, tb in zip(rzedy, tabliczki):
        for x in kol:
            sloty.append(node(f"Pet{i}", "Frame", {**ud(x, rz, 0.118, 0.172), "BackgroundTransparency": 1, "ZIndex": 6}, [
                node("PetView", "ViewportFrame", {**ud(0.08, 0.05, 0.84, 0.7), "BackgroundTransparency": 1, "ZIndex": 6,
                                                  "Ambient": c3("C8C8C8"), "LightColor": c3("FFFFFF")}),
                text("PetName", (0.04, 0.68, 0.92, 0.28), "", WHITE, 14, 1.5, 7),
                text("Chance", (0.0, 0.0, 1.0, 0.24), "", GOLD, 16, 1.5, 8),
            ]))
            sloty.append(text(f"Rarity{i}", (x + 0.004, tb, 0.11, 0.048), "", WHITE, 13, 1.5, 6))
            i += 1
    przyciski = []
    for nazwa, x, s in (("Buy1", 0.538, "OPEN"), ("Buy3", 0.679, "OPEN x3"), ("Auto", 0.821, "AUTO")):
        przyciski.append(hit(nazwa, (x, 0.757, 0.123, 0.155)))
        przyciski.append(text(f"{nazwa}Label", (x + 0.01, 0.79, 0.103, 0.09), s, WHITE, 22, 2, 7))
    okno("OknoJajka", [
        text("TitleLeft", (0.108, 0.006, 0.296, 0.08), "FOREST EGG", CREAM, 40),
        text("TitleRight", (0.6, 0.006, 0.275, 0.08), "PETS", CREAM, 40),
        node("EggView", "ViewportFrame", {**ud(0.035, 0.065, 0.452, 0.74), "BackgroundTransparency": 1, "ZIndex": 3,
                                          "Ambient": c3("9FB8A0"), "LightColor": c3("FFFFFF")}),
        text("Price", (0.123, 0.819, 0.28, 0.101), "", GOLD, 30, 2),
        *sloty, *przyciski,
        node("Result", "Frame", {**ud(0.06, 0.12, 0.4, 0.2), "BackgroundColor3": c3("2B1D14"), "BackgroundTransparency": 0.1,
                                 "Visible": False, "ZIndex": 20}, [
            corner(0.12),
            node("UIStroke", "UIStroke", {"Color": c3("FFD65A"), "Thickness": 3}),
            text("ResultTitle", (0.05, 0.05, 0.9, 0.4), "", WHITE, 34, 2.5, 21),
            text("ResultSub", (0.05, 0.5, 0.9, 0.4), "", GOLD, 22, 2, 21),
        ]),
        text("Message", (0.06, 0.08, 0.4, 0.05), "", WHITE, 18, 2, 8),
    ], 26)


# ------------------------------------------------------------------------------------------------ mistrz gier
# środki pól ścieżki (piksele podglądu 1200 × 872), od pionka (start) wężykiem do złotej gwiazdy
POLA = [(132, 750), (140, 660), (170, 598), (245, 575), (335, 590), (420, 612), (502, 642), (590, 665), (668, 645),
        (695, 573), (665, 500), (590, 470), (497, 465), (408, 465), (312, 465), (215, 448), (160, 393), (165, 310),
        (232, 262), (338, 262), (420, 300), (497, 345), (585, 365), (665, 350), (690, 290), (690, 205)]


def mistrz():
    pola = []
    for i, (x, y) in enumerate(POLA, 1):
        fx, fy = x / 1200, y / 872
        pola.append(text(f"Field{i:02d}", (fx - 0.03, fy - 0.028, 0.06, 0.05), "", WHITE, 15, 1.8, 6))
    okno("OknoMistrzaGier", [
        text("Title", (0.108, 0.006, 0.494, 0.08), "GAME MASTER", CREAM, 40),
        node("Fields", "Frame", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "ZIndex": 6}, pola),
        node("Pawn", "ImageLabel", {"AnchorPoint": [0.5, 0.85], **ud(POLA[0][0] / 1200, POLA[0][1] / 872, 0.062, 0.085),
                                    "BackgroundTransparency": 1, "Image": "", "ScaleType": "Fit", "ZIndex": 12}),
        node("Dice", "Frame", {**ud(0.742, 0.698, 0.068, 0.097), "BackgroundColor3": c3("FBF7EC"), "ZIndex": 8}, [
            corner(0.18),
            node("UIStroke", "UIStroke", {"Color": c3("1A1410"), "Thickness": 3}),
            text("Face", (0.05, 0.05, 0.9, 0.9), "?", "1A1410", 48, 0, 9),
        ]),
        hit("RollButton", (0.85, 0.686, 0.096, 0.106)),
        text("RollLabel", (0.845, 0.79, 0.106, 0.03), "ROLL!", WHITE, 16, 1.5, 7),
        text("Price", (0.711, 0.826, 0.152, 0.092), "", GOLD, 26, 2),
        text("Timer", (0.879, 0.83, 0.071, 0.07), "", "1A1410", 18, 0, 7),
        text("Message", (0.09, 0.1, 0.55, 0.055), "", WHITE, 22, 2, 14),
        text("Board", (0.42, 0.1, 0.24, 0.05), "", CREAM, 18, 2, 14),
        text("Reward", (0.3, 0.45, 0.2, 0.1), "", GOLD, 48, 3, 15),
    ], 27)


if __name__ == "__main__":
    kowal()
    # jajko() — Paweł 24.11 wieczorem: bez okna jajka; panel petów z tej grafiki jest podpowiedzią nad jajkiem
    # (src/client/JajkoKoroweClient.client.luau)
    mistrz()
