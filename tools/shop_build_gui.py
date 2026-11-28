#!/usr/bin/env python3
"""Generuje src/gui/Shop.model.json — okno sklepu (sklep z bronią i sklep magiczny, Paweł 18.11).

Grafika: tools/sklep_okno.py → assets/processed/Sklepy/SklepBron1–4.png, SklepMagia1–4.png (kafelki 2 × 2, ID
w assets/manifest.json). Układ elementów: assets/processed/Sklepy/uklad_sklepow.json. Napisy natywne (Luckiest Guy).
Logika: src/client/ShopClient.client.luau (otwieranie zdarzeniem OknoMiejsca z pakietu Karola i kliknięciem
na sprzedawcy; lewa strona = kopia okna ekwipunku przez moduł src/client/EkwipunekStan.luau; towar i kupno przez
serwer sklepu Karola SklepProba/Zdalne/Sklep). Makieta: Figma, ramki ShopWeapon (46:115) i ShopMagic (46:125).
Projekt: B&C/UI/Sklepy i bronie startowe — prompty.md.

Użycie: python tools/shop_build_gui.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAN = json.loads((ROOT / "assets/manifest.json").read_text(encoding="utf-8"))["assets"]
L = json.loads((ROOT / "assets/processed/Sklepy/uklad_sklepow.json").read_text(encoding="utf-8"))
OUT = ROOT / "src/gui/Shop.model.json"
FONT = {"Font": {"family": "rbxasset://fonts/families/LuckiestGuy.json", "weight": "Regular", "style": "Normal"}}

# Sloty wyposażenia wypalone w grafice (ułamki całego obrazu 4800 × 3584, zmierzone 23.11 na obu sklepach — ten sam
# układ): lewa kolumna hełm, zbroja, rękawice, buty; prawa amulet, pas, pierścień, sakiewka; broń pod paskiem.
EQ_WIERSZE = [(0.161, 0.254), (0.260, 0.351), (0.359, 0.448), (0.456, 0.545)]
EQ_SLOTY = [(n, (0.093, y0, 0.066, y1 - y0)) for n, (y0, y1) in zip(["Helmet", "Chest", "Gloves", "Boots"], EQ_WIERSZE)] + \
           [(n, (0.384, y0, 0.068, y1 - y0)) for n, (y0, y1) in zip(["Amulet", "Belt", "Ring", "Trinket"], EQ_WIERSZE)] + \
           [("Weapon", (0.236, 0.450, 0.073, 0.100))]
# komórki plecaka 5 × 3 (wykryte po kolorze w obu grafikach): kolumny x, rzędy y, rozmiar
PLECAK_X = [0.0925, 0.1654, 0.2381, 0.3113, 0.3844]
PLECAK_Y = [0.6136, 0.709, 0.8055]
PLECAK_WH = (0.0645, 0.0838)
PASEK = (0.214, 0.392, 0.117, 0.036)  # zielony pasek pod portretem (doświadczenie)
KOLOR_SLOTU = "83513F"  # wnętrze brązowego slotu (zasłania wypaloną sylwetkę, gdy w slocie leży przedmiot)
# Paweł 26.11: plecak ma zakładki ITEMS i OTHERS (jak okno ekwipunku); w sklepie szerokie zakładki z grafiki EQ
# (EqTab2Orange / EqTab2Purple, 9-slice) zakrywają po dwie wymalowane zakładki z tła sklepu
ZAKLADKI = ["Items", "Others"]


def c3(h):
    return [round(int(h[i:i + 2], 16) / 255, 4) for i in (0, 2, 4)]


def img(name):
    # okna sklepów z NPC Karola (Paweł 24.11, tools/sklep_sprzedawca.py): wersja _v2, dopóki jej nie ma — stara
    i = MAN.get(name + "_v2", {}).get("roblox_image") or MAN.get(name, {}).get("roblox_image")
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


def mniejszy(r, k):
    """Prostokąt (x, y, w, h) zmniejszony w pionie do k wysokości, ze środkiem w tym samym miejscu."""
    x, y, w, h = r
    return (x, y + h * (1 - k) / 2, w, h * k)


def hit(name, r, z=6):
    """Niewidzialne pole kliknięcia nad elementem z grafiki (przycisk wypalony w tle — reakcję robi klient)."""
    return node(name, "ImageButton", {**ud(*r), "BackgroundTransparency": 1, "Image": "", "AutoButtonColor": False, "ZIndex": z})


def art(nazwa, widoczna):
    tiles = [node(f"Tile{i}", "ImageLabel", {**ud(cx * 0.5, cy * 0.5, 0.5, 0.5), "BackgroundTransparency": 1,
                                             "Image": img(f"Sklep{nazwa}{i}"), "ScaleType": "Stretch", "ZIndex": 1})
             for i, (cx, cy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)], 1)]
    return node(f"Art{nazwa}", "Frame", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "Visible": widoczna, "ZIndex": 1}, tiles)


def corner(r):
    return node("UICorner", "UICorner", {"CornerRadius": {"UDim": [r, 0]}})


def ikona(z=7):
    return node("Icon", "ImageLabel", {**ud(0.12, 0.12, 0.76, 0.76), "BackgroundTransparency": 1, "Image": "", "ZIndex": z,
                                         "ScaleType": "Fit"})


def slot_eq(nazwa, r):
    return node(f"Slot_{nazwa}", "ImageButton", {**ud(*r), "BackgroundTransparency": 1, "Image": "", "AutoButtonColor": False,
                                                 "ZIndex": 6}, [
        node("Cover", "Frame", {**ud(0.09, 0.08, 0.82, 0.84), "BackgroundColor3": c3(KOLOR_SLOTU), "Visible": False, "ZIndex": 6},
             [corner(0.12)]),
        ikona(),
    ])


def slot_plecaka(i, x, y):
    w, h = PLECAK_WH
    return node(f"BagSlot{i:02d}", "ImageButton", {**ud(x, y, w, h), "BackgroundTransparency": 1, "Image": "",
                                                   "AutoButtonColor": False, "ZIndex": 6}, [ikona()])


def slot_sklepu(i, r):
    """Slot towaru: ikona (albo kafelek stopnia), cena, kłódka poziomu, znacznik „masz”."""
    return node(f"ShopSlot{i}", "ImageButton", {**ud(*r), "BackgroundTransparency": 1, "Image": "", "AutoButtonColor": False,
                                                "ZIndex": 6}, [
        ikona(),
        # Paweł 26.11: rybka przed ceną (waluta = Rybki, D-146); cena przesunięta w prawo od ikony
        node("FishIcon", "ImageLabel", {**ud(0.02, 0.76, 0.3, 0.26), "BackgroundTransparency": 1, "Image": img("GoldFish"),
                                        "ScaleType": "Fit", "Visible": False, "ZIndex": 9}),
        text("Price", (0.3, 0.74, 0.7, 0.3), "", "FFD65A", 18, 2, 9),
        text("Lock", (0.0, 0.3, 1.0, 0.4), "", "FFFFFF", 20, 2.5, 10),
        text("Owned", (0.0, -0.06, 1.0, 0.28), "", "8CE865", 14, 2, 10),
    ])


def karta():
    """Karta wybranego towaru nad sprzedawcą: nazwa, statystyki, wymagany poziom, cena, przycisk BUY / EQUIP."""
    return node("Card", "Frame", {**ud(0.585, 0.135, 0.31, 0.405), "BackgroundColor3": c3("2B1D14"), "BackgroundTransparency": 0.06,
                                  "Visible": False, "ZIndex": 20}, [
        corner(0.06),
        node("UIStroke", "UIStroke", {"Color": c3("F2C14E"), "Thickness": 3}),
        text("ItemName", (0.06, 0.04, 0.8, 0.17), "", "FCE3B0", 30, 2.5, 21),
        text("Tier", (0.06, 0.2, 0.88, 0.09), "", "FFFFFF", 16, 1.5, 21),
        text("Stats", (0.06, 0.31, 0.88, 0.2), "", "FFFFFF", 18, 1.5, 21),
        text("Req", (0.06, 0.52, 0.88, 0.09), "", "FFFFFF", 16, 1.5, 21),
        node("FishIcon", "ImageLabel", {**ud(0.06, 0.615, 0.11, 0.11), "BackgroundTransparency": 1, "Image": img("GoldFish"),
                                        "ScaleType": "Fit", "Visible": False, "ZIndex": 21}),
        text("Price", (0.19, 0.62, 0.75, 0.1), "", "FFD65A", 22, 2, 21),
        node("BuyButton", "TextButton", {**ud(0.18, 0.76, 0.64, 0.18), "BackgroundColor3": c3("3F9B55"), "Text": "BUY",
                                         "TextColor3": c3("FFFFFF"), "FontFace": FONT, "TextScaled": True, "AutoButtonColor": True,
                                         "ZIndex": 22}, [
            corner(0.25),
            node("UIStroke", "UIStroke", {"Color": c3("1A1410"), "Thickness": 2.5, "ApplyStrokeMode": "Border"}),
            node("UITextSizeConstraint", "UITextSizeConstraint", {"MaxTextSize": 28, "MinTextSize": 8}),
            node("UIPadding", "UIPadding", {"PaddingTop": {"UDim": [0.15, 0]}, "PaddingBottom": {"UDim": [0.12, 0]}}),
        ]),
        node("CloseCard", "TextButton", {**ud(0.86, 0.02, 0.12, 0.12), "BackgroundTransparency": 1, "Text": "X",
                                         "TextColor3": c3("FFFFFF"), "FontFace": FONT, "TextScaled": True, "ZIndex": 22},
             [node("UIStroke", "UIStroke", {"Color": c3("1A1410"), "Thickness": 2})]),
    ])


def main():
    cream, white = "FCE3B0", "FFFFFF"
    zakladki = []
    zr = L["zakladki"]
    for nazwa, (a, b), s, grafika in zip(ZAKLADKI, [(zr[0], zr[1]), (zr[2], zr[3])], ["ITEMS", "OTHERS"],
                                         ["EqTab2Orange", "EqTab2Purple"]):
        x0, x1 = a[0] - 0.004, b[0] + b[2] + 0.004
        # Paweł 28.11: zakładki były za płaskie (153 × 25 px przy oknie 807 px) — napis się zlewał. Wyższe o tyle, ile
        # jest miejsca pod slotami wyposażenia (dół zostaje na ramce plecaka), większy napis, grubszy wycinek 9-slice.
        y0, h = a[1] - 0.019, a[3] + 0.025
        zakladki.append(node(f"Tab{nazwa}", "ImageButton", {**ud(x0, y0, x1 - x0, h), "BackgroundTransparency": 1,
                                                            "Image": img(grafika), "ScaleType": "Slice",
                                                            "ImageRectOffset": [0, 0], "ImageRectSize": [1024, 68],  # bez ciemnego paska na dole
                                                            "SliceCenter": {"Rect": [[60, 14], [964, 60]]}, "SliceScale": 0.44,
                                                            "AutoButtonColor": False, "ZIndex": 6}, [
            text("Label", (0.08, 0.18, 0.84, 0.64), s, white, 18, 2, 7),
        ]))
    pasek = node("ExpBar", "Frame", {**ud(*PASEK), "BackgroundColor3": c3("0E0A10"), "ZIndex": 3}, [
        corner(0.3),
        node("Fill", "Frame", {**ud(0, 0, 0, 1), "BackgroundColor3": c3("4BB247"), "ZIndex": 4}, [corner(0.3)]),
    ])
    portret = L["portret"]
    panel = node("Panel", "Frame", {"AnchorPoint": [0.5, 0.5], **ud(0.5, 0.5, 0.86, 0.9), "BackgroundTransparency": 1}, [
        node("UIAspectRatioConstraint", "UIAspectRatioConstraint", {"AspectRatio": L["proporcje"], "AspectType": "FitWithinMaxSize",
                                                                     "DominantAxis": "Width"}),
        node("UIScale", "UIScale", {"Scale": 1}),
        node("InputBlocker", "TextButton", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "Text": "", "AutoButtonColor": False}),
        art("Bron", True), art("Magia", False),
        # Paweł 28.11: tytuły dużo mniejsze (nieco ponad połowa dawnej wysokości; po pierwszej próbie 3/4 były dalej za duże)
        text("TitleLeft", mniejszy(L["tytul_lewy"], 0.54), "HERO", cream, 24, 2.5),
        text("TitleRight", mniejszy(L["tytul_prawy"], 0.54), "WEAPON SHOP", cream, 24, 2.5),
        node("ClassEmblem", "ImageLabel", {**ud(portret[0] + portret[2] * 0.15, portret[1] + portret[3] * 0.12, portret[2] * 0.7,
                                               portret[3] * 0.76), "BackgroundTransparency": 1, "Image": "", "ScaleType": "Fit",
                                           "ZIndex": 3}),
        pasek,
        text("Level", L["poziom"], "LV 1", white, 24, 2),
        # Paweł 28.11: stare zakładki wymalowane w tle sklepu (pomarańczowa, niebieska, zielona, fioletowa) wystawały
        # spod nowych. Zamazujemy je bez nowej grafiki: pasek tła znad zakładek (kafel 3, wiersze 86–92) rozciągnięty
        # w dół na cały pas starych zakładek (wiersze 92–140) — pod nowymi zakładkami jest już samo tło wnętrza.
        *[node(f"TabErase{nazwa}", "ImageLabel", {**ud(160 / 2048, 0.5 + 92 / 1530, (952 - 160) / 2048, (141 - 92) / 1530),
                                                  "BackgroundTransparency": 1, "Image": img(f"Sklep{nazwa}3"),
                                                  "ImageRectOffset": [160, 86], "ImageRectSize": [952 - 160, 6],  # pas sięga do obrysu ramki
                                                  "ScaleType": "Stretch", "Active": False, "Visible": nazwa == "Bron",
                                                  "ZIndex": 5}) for nazwa in ("Bron", "Magia")],
        node("Tabs", "Frame", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "ZIndex": 6}, zakladki),
        # Paweł 26.11: krawędź ramki plecaka nad zakładkami (wycinek kafla tła 3: wiersze 139–159, kafel 1024 × 765 px,
        # lewy dolny) — ramka przycina zakładki równo, boczne obrysy nie wchodzą na jej krawędź; osobno dla obu wyglądów
        # 28.11: wycinek zaczyna się POD obrysem ramki (wiersz 145, było 139) — w wierszach 139–144 siedziały resztki
        # dołu starych wymalowanych zakładek; sam obrys rysuje niżej TabCoverLine na całej szerokości zakładek
        *[node(f"TabCover{nazwa}", "ImageLabel", {**ud(160 / 2048, 0.5 + 145 / 1530, (952 - 160) / 2048, 14 / 1530),
                                                  "BackgroundTransparency": 1, "Image": img(f"Sklep{nazwa}3"),
                                                  "ImageRectOffset": [160, 145], "ImageRectSize": [952 - 160, 14],
                                                  "ScaleType": "Stretch", "Active": False, "Visible": nazwa == "Bron",
                                                  "ZIndex": 7}) for nazwa in ("Bron", "Magia")],
        # w tle sklepu pierwsza (pomarańczowa) wymalowana zakładka wtapia się w ramkę — czarny obrys góry ramki zaczyna
        # się dopiero za nią (kafel x 360). Brakujący odcinek obrysu (x 172–364, wiersze 140–144) dorysowany, żeby
        # linia pod zakładką ITEMS szła przez całą szerokość
        node("TabCoverLine", "Frame", {**ud(172 / 2048, 0.5 + 139.8 / 1530, (940 - 172) / 2048, 5.4 / 1530),
                                       "BackgroundColor3": [0.1, 0.05, 0.065], "BorderSizePixel": 0, "ZIndex": 8}),
        node("EquipSlots", "Frame", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "ZIndex": 6},
             [slot_eq(n, r) for n, r in EQ_SLOTY]),
        node("BackpackGrid", "Frame", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "ZIndex": 6},
             [slot_plecaka(ry * 5 + kx + 1, x, y) for ry, y in enumerate(PLECAK_Y) for kx, x in enumerate(PLECAK_X)]),
        # Paweł 28.11: mniejszy napis tabliczki; przy kwocie rybka PRZED liczbą zamiast słowa „FISH” (ustawia ją
        # ShopClient.rysujTabliczke — ikona jest dzieckiem tabliczki)
        node("Plate", "TextLabel", {**ud(*mniejszy(L["tabliczka"], 0.56)), "BackgroundTransparency": 1, "Text": "NEW GOODS",
                                    "TextColor3": c3(cream), "FontFace": FONT, "TextXAlignment": "Center",
                                    "TextYAlignment": "Center", "TextScaled": True, "ZIndex": 5}, [
            node("UITextSizeConstraint", "UITextSizeConstraint", {"MaxTextSize": 20, "MinTextSize": 6}),
            node("UIStroke", "UIStroke", {"Color": c3("1A1410"), "Thickness": 2.5, "LineJoinMode": "Round",
                                          "ApplyStrokeMode": "Contextual"}),
            node("UIPadding", "UIPadding", {}),
            node("FishIcon", "ImageLabel", {"AnchorPoint": [0, 0.5], **ud(0, 0.5, 0, 0.92), "BackgroundTransparency": 1,
                                            "Image": img("GoldFish"), "ScaleType": "Fit", "Visible": False, "ZIndex": 6},
                 [node("UIAspectRatioConstraint", "UIAspectRatioConstraint", {"AspectRatio": 1, "DominantAxis": "Height"})]),
        ]),
        hit("CloseButton", L["zamknij"]),
        hit("RerollButton", L["odswiez"]),
        # Paweł 26.11: przycisk porównania (lupa) — po włączeniu podpowiedź przedmiotu pokazuje +/−/0 względem założonego
        node("CompareButton", "ImageButton", {**ud(0.533, 0.562, 0.052, 0.069), "BackgroundTransparency": 1,
                                              "Image": img("PrzyciskPorownaj"), "ScaleType": "Fit", "AutoButtonColor": False,
                                              "ZIndex": 7}, [
            node("UIScale", "UIScale", {"Scale": 1}),
            node("On", "ImageLabel", {"AnchorPoint": [0.5, 0.5], **ud(0.5, 0.5, 1.25, 1.25), "BackgroundTransparency": 1,
                                      "Image": img("AwansBlask"), "ScaleType": "Fit", "Visible": False, "ZIndex": 6}),
        ]),
        *[slot_sklepu(i + 1, r) for i, r in enumerate(L["sloty_sklepu"])],
        # Paweł 26.11: strony plecaka jak w oknie ekwipunku (po 15 slotów na stronę sklepu)
        node("Pages", "Frame", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "ZIndex": 7}, [
            node("PrevPage", "ImageButton", {"AnchorPoint": [0.5, 0.5], **ud(0.15, 0.935, 0.052 / L["proporcje"], 0.052),
                                             "BackgroundTransparency": 1, "Image": img("EqStronaLewo"), "ScaleType": "Fit",
                                             "AutoButtonColor": False, "ZIndex": 8}),
            node("PageLabel", "ImageLabel", {"AnchorPoint": [0.5, 0.5], **ud(0.27, 0.935, 0.085, 0.085 * L["proporcje"] * 136 / 256),
                                             "BackgroundTransparency": 1, "Image": img("EqStronaTabliczka"), "ScaleType": "Fit",
                                             "ZIndex": 8}, [text("Text", (0.14, 0.2, 0.72, 0.6), "1 / 5", "FCE3B0", 20, 2, 9)]),
            node("NextPage", "ImageButton", {"AnchorPoint": [0.5, 0.5], **ud(0.39, 0.935, 0.052 / L["proporcje"], 0.052),
                                             "BackgroundTransparency": 1, "Image": img("EqStronaPrawo"), "ScaleType": "Fit",
                                             "AutoButtonColor": False, "ZIndex": 8}),
        ]),
        karta(),
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
