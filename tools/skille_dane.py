#!/usr/bin/env python3
"""Dane podpowiedzi umiejętności (Paweł 26.11) -> src/shared/SkilleDane.luau.

Umiejętność gracz zdobywa w drzewku (SkillTreeData, gałąź SKILLS: węzły ze stat PowerSlash, CrushingBlow, …), a jej
działanie w walce opisują dane silnika walki Karola (tools/walka/dane_walki.json: umiejetnosci / pasywne / efekty).
Tu łączymy jedno z drugim: stat węzła drzewka -> id w silniku walki, i wypisujemy po angielsku to, co podpowiedź
pokazuje: rodzaj (aktywna / pasywna), koszt many, obrażenia (mnożnik ciosu, fizyczne / magiczne), efekty z szansą
i czasem trwania, premie pasywki. Plików Karola nie zmienia — tylko czyta.

PRZYPISANIE (propozycja agenta, do potwierdzenia — pytanie w sejfie): PowerSlash = ciecie, CrushingBlow =
miazdzacy_cios, StoneSkin = kamienna_skora, ShieldBlock = mur_tarczy (pasywka), WarCry = furia (pasywka).

Użycie: python tools/skille_dane.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WALKA = ROOT / "tools/walka/dane_walki.json"
OUT = ROOT / "src/shared/SkilleDane.luau"

PRZYPISANIE = {"PowerSlash": "ciecie", "CrushingBlow": "miazdzacy_cios", "StoneSkin": "kamienna_skora",
               "ShieldBlock": "mur_tarczy", "WarCry": "furia"}
EFEKTY_EN = {"zdarcie_pancerza": "Armor break", "ogluszenie": "Stun", "podpalenie": "Burn", "trucizna": "Poison",
             "spowolnienie": "Slow", "krwawienie": "Bleed", "kamienna_skora": "Stone Skin shield", "bariera": "Barrier",
             "skupienie": "Focus"}
MOD_EN = {"blok": "Block chance", "pancerz": "Armor", "cios_zwykly": "Basic attack damage", "zycie": "Max HP",
          "cios": "Damage", "unik": "Dodge", "krytyk": "Crit chance", "mnoznik_krytyka": "Crit damage",
          "pancerz_wroga": "Enemy armor"}


def lua_str(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def procent(v):
    p = round(v * 100, 1)
    return f"{p:g}%"


def main():
    d = json.loads(WALKA.read_text(encoding="utf-8"))
    linie = ["-- WYGENEROWANE przez tools/skille_dane.py z danych walki Karola (tools/walka/dane_walki.json) — nie edytuj ręcznie.",
             "-- Podpowiedź umiejętności w oknie ekwipunku: stat węzła drzewka (SkillTreeData) -> opis działania w walce.",
             "return {"]
    for stat, wid in PRZYPISANIE.items():
        if wid in d["umiejetnosci"]:
            u = d["umiejetnosci"][wid]
            wiersze = []
            if u["mnoznik"] > 0:
                rodzaj = {"fizyczne": "physical", "magiczne": "magic"}.get(u["rodzaj"], u["rodzaj"])
                wiersze.append(f"Damage: {procent(u['mnoznik'])} of a hit ({rodzaj})")
            for e in u["efekty"]:
                ef = d["efekty"].get(e["efekt"], {})
                tury = ef.get("trwa", 0)
                szansa = "" if e["szansa"] >= 1 else f"{procent(e['szansa'])} chance: "
                wiersze.append(f"{szansa}{EFEKTY_EN.get(e['efekt'], e['efekt'])}" + (f" for {tury} turns" if tury else ""))
            if u["premia_krytyka"]:
                wiersze.append(f"Crit chance +{procent(u['premia_krytyka'])}")
            linie.append(f"\t{stat} = {{ walka = {lua_str(wid)}, rodzaj = \"ACTIVE\", mana = {u['koszt_many']}, "
                         f"cel = {lua_str('enemy' if u['cel'] == 'wrog' else 'self')}, "
                         f"opis = {{ {', '.join(lua_str(w) for w in wiersze)} }} }},")
        elif wid in d["pasywne"]:
            p = d["pasywne"][wid]
            wiersze = [f"{MOD_EN.get(k, k)} +{procent(v)}" if v > 0 else f"{MOD_EN.get(k, k)} {procent(v)}"
                       for k, v in p["modyfikatory"].items()]
            linie.append(f"\t{stat} = {{ walka = {lua_str(wid)}, rodzaj = \"PASSIVE\", mana = 0, cel = \"self\", "
                         f"opis = {{ {', '.join(lua_str(w) for w in wiersze)} }} }},")
    linie += ["}", ""]
    OUT.write_text("\n".join(linie), encoding="utf-8")
    print("ok", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
