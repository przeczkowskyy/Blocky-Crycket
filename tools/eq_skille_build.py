#!/usr/bin/env python3
"""Przebudowa okna ekwipunku (Paweł 26.11, po konsultacji) — dopisuje do src/gui/EquipmentPanel.model.json
(po tools/eq_build_gui.py, który woła ten skrypt na końcu):

1. CHARACTER: dwie zakładki ATTRIBUTES i INFO rozciągnięte nad całą ramką statystyk (bez DESCRIPTION/SKILLS
   i INTERACTIONS).
2. BACKPACK: trzy zakładki ITEMS, OTHERS, SKILLS nad całą ramką plecaka; pod plecakiem strzałki stron i tabliczka
   z numerem strony (3 strony po 25 slotów w ITEMS i OTHERS; w SKILLS leżą zdobyte umiejętności).
3. Pas z trzema slotami umiejętności między postacią a plecakiem, pod lupą porównania — umiejętności przeciąga się
   z zakładki SKILLS na sloty. Zablokowany slot (drzewko: SKILL SLOT I–III): kłódka na placeholderze kuli ognia.
4. Lupa porównania między slotem amuletu a plecakiem.

Grafika: tools/eq_zakladki_ui.py (zakładki EqTab2*, strzałki EqStrona*, pas EqPasSkilli — jedna generacja
Higgsfield 26.11), tools/skille_ui.py (kula ognia, kłódka, lupa). Zakładki są rozciągane 9-slice (końce bez zmian).
Logika: src/client/EquipmentPanelClient.client.luau, serwer slotów: src/server/SkillSloty.server.luau.

Użycie: python tools/eq_skille_build.py   (można uruchamiać wielokrotnie)
"""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUI = ROOT / "src/gui/EquipmentPanel.model.json"
MAN = json.loads((ROOT / "assets/manifest.json").read_text(encoding="utf-8"))["assets"]
UKLAD = json.loads((ROOT / "assets/processed/EqZakladki2/uklad.json").read_text(encoding="utf-8"))
FONT = {"Font": {"family": "rbxasset://fonts/families/LuckiestGuy.json", "weight": "Regular", "style": "Normal"}}
PROP = 1.75657  # proporcje okna EQ (szer / wys)

# zakładki: (nazwa, napis, grafika); kotwica (0.5, 1) jak w oryginale, y = dół zakładki
ZAKL_POSTACI = {"y": 0.5806, "h": 0.05256, "x0": 0.054, "x1": 0.48,
                "tab": [("TabAttributes", "ATTRIBUTES", "EqTab2Orange"), ("TabInfo", "INFO", "EqTab2Blue")]}
ZAKL_PLECAKA = {"y": 0.19087, "h": 0.05809, "x0": 0.541, "x1": 0.953,
                "tab": [("TabItems", "ITEMS", "EqTab2Orange"), ("TabOthers", "OTHERS", "EqTab2Purple"),
                        ("TabSkills", "SKILLS", "EqTab2Green")]}
ODSTEP_ZAKL = 0.006
PAS = (0.483, 0.215, 0.295)  # środek x, góra, wysokość pasa slotów (ułamki okna)
STRONY_Y = 0.917  # środek strzałek i tabliczki stron (na dolnej krawędzi ramki plecaka)


def img(nazwa):
    i = MAN.get(nazwa, {}).get("roblox_image")
    return f"rbxassetid://{i}" if i else ""


def ud(x, y, w, h):
    return {"Position": {"UDim2": [[x, 0], [y, 0]]}, "Size": {"UDim2": [[w, 0], [h, 0]]}}


def n(name, cls, props, children=None):
    d = {"Name": name, "ClassName": cls, "Properties": props}
    if children:
        d["Children"] = children
    return d


def tekst(name, r, s, kolor, maks, obrys=2.5, z=8):
    return n(name, "TextLabel", {**ud(*r), "BackgroundTransparency": 1, "Text": s, "TextColor3": kolor, "FontFace": FONT,
                                 "TextScaled": True, "ZIndex": z}, [
        n("UITextSizeConstraint", "UITextSizeConstraint", {"MaxTextSize": maks, "MinTextSize": 6}),
        n("UIStroke", "UIStroke", {"Color": [0.102, 0.0784, 0.0627], "Thickness": obrys, "LineJoinMode": "Round"}),
    ])


def znajdz(w, nazwa):
    if w.get("Name") == nazwa:
        return w
    for c in w.get("Children", []):
        r = znajdz(c, nazwa)
        if r:
            return r
    return None


def zakladki(grupa, wzor, uklad):
    """N szerokich zakładek nad całą ramką. Wzór: oryginalna zakładka (napis z obrysem, UIScale)."""
    k = len(uklad["tab"])
    w = (uklad["x1"] - uklad["x0"] - (k - 1) * ODSTEP_ZAKL) / k
    nowe = []
    for i, (nazwa, napis, grafika) in enumerate(uklad["tab"]):
        t = copy.deepcopy(wzor)
        t["Name"] = nazwa
        p = t["Properties"]
        p["Position"] = {"UDim2": [[round(uklad["x0"] + w / 2 + i * (w + ODSTEP_ZAKL), 5), 0], [uklad["y"], 0]]}
        p["Size"] = {"UDim2": [[round(w, 5), 0], [uklad["h"], 0]]}
        p["Image"] = img(grafika)
        p["ScaleType"] = "Slice"
        # Paweł 26.11: bez ciemnego paska na dole zakładki — z grafiki (1024 × 94) bierzemy tylko górne 68 px,
        # więc zakładka kończy się równo na ramce (jej obrys jest dolną krawędzią zakładki)
        p["ImageRectOffset"] = [0, 0]
        p["ImageRectSize"] = [1024, 68]
        p["SliceCenter"] = {"Rect": [[60, 14], [964, 60]]}  # skosy na końcach zostają, środek się rozciąga
        p["SliceScale"] = 0.42
        p["LayoutOrder"] = i + 1
        for c in t.get("Children", []):
            if c["Name"] == "Label":
                c["Properties"]["Text"] = napis
                c["Properties"]["Position"] = {"UDim2": [[0.05, 0], [0.18, 0]]}
                c["Properties"]["Size"] = {"UDim2": [[0.9, 0], [0.66, 0]]}
        nowe.append(t)
    grupa["Children"] = [c for c in grupa.get("Children", []) if not c["Name"].startswith("Tab")] + nowe


def krawedz_ramki(nazwa, kafel, x0, y0, px):
    """Paweł 26.11: zakładki mają kończyć się równo na ramce, bez bocznych obrysów wchodzących na jej krawędź.
    Zakładka wchodzi kilka pikseli POD krawędź ramki, a na wierzchu leży wycinek tej krawędzi z kafla tła
    (ImageRect) — dokładna kopia tła, więc widać tylko to, że ramka przycina zakładki.
    kafel = węzeł kafla tła (EqBgN, 1024 × 583 px), x0/y0 = jego początek w oknie, px = (x0, y0, x1, y1) w pikselach kafla.
    Kafle tła są rysowane z rozmiarem 0.5008 (zakładka na szwy), stąd ten sam mnożnik."""
    ax, ay, bx, by = px
    k = 0.5008
    return n(nazwa, "ImageLabel", {**ud(round(x0 + ax / 1024 * k, 5), round(y0 + ay / 583 * k, 5),
                                        round((bx - ax) / 1024 * k, 5), round((by - ay) / 583 * k, 5)),
                                   "BackgroundTransparency": 1, "Image": kafel["Properties"]["Image"],
                                   "ImageRectOffset": [ax, ay], "ImageRectSize": [bx - ax, by - ay],
                                   "ScaleType": "Stretch", "Active": False, "ZIndex": 2})


def slot_skilla(i, r):
    x, y, w, h = r
    return n(f"SkillSlot{i}", "ImageButton", {**ud(x, y, w, h), "BackgroundTransparency": 1, "Image": "",
                                             "AutoButtonColor": False, "ZIndex": 8}, [
        n("Icon", "ImageLabel", {**ud(0.04, 0.04, 0.92, 0.92), "BackgroundTransparency": 1, "Image": img("SkillFireball"),
                                 "ScaleType": "Fit", "ZIndex": 9}),
        n("Lock", "ImageLabel", {"AnchorPoint": [0.5, 0.5], **ud(0.5, 0.52, 0.62, 0.72), "BackgroundTransparency": 1,
                                 "Image": img("SkillKlodka"), "ScaleType": "Fit", "ZIndex": 10}),
    ])


def main():
    g = json.loads(GUI.read_text(encoding="utf-8"))
    panel = znajdz(g, "Panel")
    # usuń poprzednie wersje dodatków (zakładka SKILLS z 26.11 rano, pas, strony, lupa)
    panel["Children"] = [c for c in panel["Children"]
                         if c.get("Name") not in ("Skills", "CompareButton", "SkillStrip", "Pages",
                                                  "TabCoverBackpack", "TabCoverCharacter")]
    # 1–2. zakładki (wzór: pierwsza zakładka postaci z eq_build_gui)
    char_tabs, bag_tabs = znajdz(panel, "CharacterTabs"), znajdz(panel, "BackpackTabs")
    wzor = copy.deepcopy(next(c for c in char_tabs["Children"] if c["Name"].startswith("Tab")))
    zakladki(char_tabs, wzor, ZAKL_POSTACI)
    zakladki(bag_tabs, wzor, ZAKL_PLECAKA)
    # strzałki stron i tabliczka
    bok = 0.07  # wysokość strzałki; szerokość = bok / PROP
    pt_w, pt_h = UKLAD["EqStronaTabliczka"]
    strony = n("Pages", "Frame", {**ud(0, 0, 1, 1), "BackgroundTransparency": 1, "ZIndex": 7}, [
        n("PrevPage", "ImageButton", {"AnchorPoint": [0.5, 0.5], **ud(0.655, STRONY_Y, bok / PROP, bok),
                                      "BackgroundTransparency": 1, "Image": img("EqStronaLewo"), "ScaleType": "Fit",
                                      "AutoButtonColor": False, "ZIndex": 8}, [n("UIScale", "UIScale", {"Scale": 1})]),
        n("PageLabel", "ImageLabel", {"AnchorPoint": [0.5, 0.5], **ud(0.747, STRONY_Y, 0.085, round(0.085 * PROP * pt_h / pt_w, 5)),
                                      "BackgroundTransparency": 1, "Image": img("EqStronaTabliczka"), "ScaleType": "Fit",
                                      "ZIndex": 8}, [tekst("Text", (0.14, 0.2, 0.72, 0.6), "1 / 3", [0.988, 0.89, 0.69], 22, 2, 9)]),
        n("NextPage", "ImageButton", {"AnchorPoint": [0.5, 0.5], **ud(0.839, STRONY_Y, bok / PROP, bok),
                                      "BackgroundTransparency": 1, "Image": img("EqStronaPrawo"), "ScaleType": "Fit",
                                      "AutoButtonColor": False, "ZIndex": 8}, [n("UIScale", "UIScale", {"Scale": 1})]),
    ])
    # 3. pas z trzema slotami umiejętności
    pw, ph = UKLAD["EqPasSkilli"]
    cx, top, h = PAS
    w = h * (pw / ph) / PROP
    pas = n("SkillStrip", "ImageLabel", {**ud(round(cx - w / 2, 5), top, round(w, 5), h), "BackgroundTransparency": 1,
                                         "Image": img("EqPasSkilli"), "ScaleType": "Stretch", "ZIndex": 7},
            [slot_skilla(i + 1, r) for i, r in enumerate(UKLAD["sloty_pasa"][1:4])])
    # 4. lupa porównania między slotem amuletu a plecakiem
    porownaj = n("CompareButton", "ImageButton", {**ud(0.462, 0.138, 0.04, 0.04 * PROP), "BackgroundTransparency": 1,
                                                  "Image": img("PrzyciskPorownaj"), "ScaleType": "Fit",
                                                  "AutoButtonColor": False, "ZIndex": 7}, [
        n("UIScale", "UIScale", {"Scale": 1}),
        n("On", "ImageLabel", {"AnchorPoint": [0.5, 0.5], **ud(0.5, 0.5, 1.3, 1.3), "BackgroundTransparency": 1,
                               "Image": img("AwansBlask"), "ScaleType": "Fit", "Visible": False, "ZIndex": 6}),
    ])
    # krawędzie ramek nad zakładkami (góra ramki plecaka: wiersze 216–238 tła; ramki statystyk: 671–689)
    okladki = [krawedz_ramki("TabCoverBackpack", znajdz(panel, "EqBg2"), 0.5, 0.0, (74, 215, 938, 240)),
               krawedz_ramki("TabCoverCharacter", znajdz(panel, "EqBg3"), 0.0, 0.5, (100, 87, 993, 108))]
    panel["Children"] += [*okladki, strony, pas, porownaj]
    GUI.write_text(json.dumps(g, indent=1, ensure_ascii=False), encoding="utf-8")
    print("ok", GUI.relative_to(ROOT), "— zakładki 2 + 3, strony plecaka, pas slotów umiejętności, lupa")


if __name__ == "__main__":
    main()
