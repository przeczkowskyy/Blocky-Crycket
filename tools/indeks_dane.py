#!/usr/bin/env python3
"""Dane okna Index (Paweł 26.11) i ikony przedmiotów Karola.

1. src/shared/IndeksPrzedmioty.luau — 80 przedmiotów z katalogu Karola (swiat/postacie/sklep_przedmioty.json):
   id, nazwa, klasa (wojownik / zwiadowca / mag), slot, stopień (start / las / bagno / dżungla), poziom, cena.
   Okno Index pokazuje graczowi tylko przedmioty jego klasy, pogrupowane według krain (stopni).
2. assets/processed/IkonyPrzedmiotow/<id>.png — ikony z Blendera (pole `ikona` w katalogu) przycięte i zmniejszone
   do 256 px, gotowe do wgrania (po „tak”), plus podglad.jpg — wszystkie na jednym arkuszu do akceptacji.

Plików Karola nie zmienia — tylko czyta. Użycie: python tools/indeks_dane.py
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
KATALOG = ROOT / "swiat/postacie/sklep_przedmioty.json"
LUAU = ROOT / "src/shared/IndeksPrzedmioty.luau"
IKONY = ROOT / "assets/processed/IkonyPrzedmiotow"
KLASA_GRY = {"wojownik": "Warrior", "zwiadowca": "Scout", "mag": "Mage"}


NAZWY_STAT = {"bron": "Damage", "pancerz": "Armor", "tarcza": "Block", "Strength": "Strength", "Constitution": "Constitution",
              "Intelligence": "Intelligence", "Dexterity": "Dexterity", "Luck": "Luck"}


def lua_tab(d):
    return "{ " + ", ".join(f"{k} = {v}" for k, v in d.items()) + " }"


def obraz(nazwa):
    m = json.loads((ROOT / "assets/manifest.json").read_text(encoding="utf-8"))["assets"]
    i = m.get(nazwa, {}).get("roblox_image")
    return f"rbxassetid://{i}" if i else ""


def lua_str(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    d = json.loads(KATALOG.read_text(encoding="utf-8"))
    it = d["przedmioty"]
    it = list(it.values()) if isinstance(it, dict) else it
    stopnie = {s["id"]: s for s in d["stopnie"]}
    linie = [
        "-- WYGENEROWANE przez tools/indeks_dane.py z katalogu Karola swiat/postacie/sklep_przedmioty.json — nie edytuj ręcznie.",
        "-- Okno Index (src/client/OknoIndeksuClient) pokazuje graczowi przedmioty jego klasy według krain (stopni).",
        "return {",
        "\tstopnie = {",
    ]
    for s in sorted(d["stopnie"], key=lambda s: s["nr"]):
        linie.append(f"\t\t{{ id = {lua_str(s['id'])}, nazwa = {lua_str(s['nazwa'])}, kraina = {lua_str(s.get('kraina') or '')}, "
                     f"poziom = {s['poziom']}, poziomDo = {s['poziom_do']} }},")
    linie += ["\t},", "\t-- kolejność i nazwy statystyk w podpowiedzi (wartość = baza + poziom ulepszenia × krok, jak u kowala Karola)",
              "\tstatystyki = {"]
    for k, _ in d["statystyki"]:
        linie.append(f"\t\t{{ id = {lua_str(k)}, nazwa = {lua_str(NAZWY_STAT.get(k, k))} }},")
    linie += ["\t},", f"\tobrazy = {{ podpowiedz = {lua_str(obraz('PodpowiedzPeta'))}, rybka = {lua_str(obraz('GoldFish'))} }},",
              "\tprzedmioty = {"]
    for x in it:
        klasy = x.get("klasy") or [x["klasa"]]
        linie.append(
            f"\t\t{{ id = {lua_str(x['id'])}, nazwa = {lua_str(x['nazwa'])}, "
            f"klasy = {{ {', '.join(lua_str(KLASA_GRY.get(k, k)) for k in klasy)} }}, slot = {lua_str(x['slot'])}, "
            f"stopien = {lua_str(x['stopien'])}, poziom = {x.get('poziom', 1)}, cena = {x.get('cena', 0)}, "
            f"sprzedawany = {'true' if x.get('sprzedawany') else 'false'}, "
            f"baza = {lua_tab(x.get('baza') or {})}, krok = {lua_tab(x.get('krok') or {})} }},")
    linie += ["\t},", "}", ""]
    LUAU.write_text("\n".join(linie), encoding="utf-8")
    print("ok", LUAU.relative_to(ROOT), len(it), "przedmiotów")

    IKONY.mkdir(parents=True, exist_ok=True)
    gotowe = []
    for x in it:
        src = ROOT / "swiat/postacie" / x["ikona"]
        im = Image.open(src).convert("RGBA")
        bb = im.getbbox()
        if bb:
            im = im.crop(bb)
        bok = max(im.size)
        kw = Image.new("RGBA", (bok, bok), (0, 0, 0, 0))
        kw.paste(im, ((bok - im.width) // 2, (bok - im.height) // 2))
        kw = kw.resize((256, 256), Image.LANCZOS)
        kw.save(IKONY / f"{x['id']}.png", optimize=True)
        gotowe.append((x, kw))
    # arkusz do akceptacji: wiersze = klasa × kraina
    kol, k = 10, 112
    try:
        f = ImageFont.truetype("arial.ttf", 11)
    except OSError:
        f = ImageFont.load_default()
    rzedy = (len(gotowe) + kol - 1) // kol
    ark = Image.new("RGB", (kol * k, rzedy * (k + 16)), (222, 196, 150))
    gotowe.sort(key=lambda g: (g[0]["klasa"], stopnie[g[0]["stopien"]]["nr"], g[0]["slot"]))
    dr = ImageDraw.Draw(ark)
    for i, (x, ikona) in enumerate(gotowe):
        cx, cy = (i % kol) * k, (i // kol) * (k + 16)
        ark.paste(ikona.resize((k - 8, k - 8), Image.LANCZOS), (cx + 4, cy + 2), ikona.resize((k - 8, k - 8), Image.LANCZOS))
        dr.text((cx + 4, cy + k - 4), x["id"][:18], fill=(50, 30, 15), font=f)
    ark.save(IKONY / "podglad.jpg", quality=88)
    print("ok ikony", len(gotowe), "arkusz", ark.size)


if __name__ == "__main__":
    main()
