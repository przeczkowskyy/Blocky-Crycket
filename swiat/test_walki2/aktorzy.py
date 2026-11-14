#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TABELA AKTORÓW prototypu walki v2 i przygotowanie ich danych (rig z klocków + klipy) — bez Studio.

    python -B swiat/test_walki2/aktorzy.py                 # przygotuj wszystkich aktorów (Blender pod wspólną blokadą)
    python -B swiat/test_walki2/aktorzy.py --tylko wojownik,mag
    python -B swiat/test_walki2/aktorzy.py --liniowo       # bez Blendera (klipy liniowo między kluczami — kanciaste)
    python -B swiat/test_walki2/aktorzy.py --lista         # tylko wypisz tabelę

Wynik: dane/<klucz>.json (rig w układzie Roblox, klipy co klatkę, wzrost, zasięg, punkty, chwile trafień).
zbuduj.py czyta te pliki i robi z nich szablony w Workspace/TestWalki2/Aktorzy oraz moduły danych dla klienta.
Blender jest potrzebny tylko tutaj (próbki krzywych klipów); budowa w Studio już go nie woła.

DODANIE AKTORA = wpis w AKTORZY (niżej) + `python -B swiat/test_walki2/aktorzy.py --tylko <klucz>` + zbuduj.py.
Pola wpisu:
  klucz       identyfikator aktora = id klasy albo przeciwnika w silniku walki (tools/walka/dane_walki.json)
  rola        "klasa" albo "przeciwnik"
  nazwa       nazwa na ekranie
  model       moduł postaci w swiat/postacie/<model>.py
  przerobka   nazwa funkcji w przerobki.py (dodatki i klipy zastępcze) albo None
  zastepczy   None albo opis, czym model zastępuje docelowy (pokazywane w galerii i w README)
  kolory      {"RRGGBB": "RRGGBB"} — przemalowanie brył (np. zastępczy slime na zielono)
  klipy       akcja -> nazwa klipu (albo None = brak klipu, odtwarzacz robi ruch proceduralny); akcje: AKCJE niżej
  umiejetnosci  id umiejętności z silnika -> nazwa klipu (None = proceduralnie)
  punkty      nazwa -> (zaczep, przesunięcie w układzie zaczepu, studs) — powstają jako Attachment „Punkt_<nazwa>”;
              Bron = czubek broni / pysk, Pocisk = skąd wylatuje pocisk lub czar, Piers = cel trafienia
  chwile      {klip: sekundy} — ręczna chwila trafienia / wypuszczenia pocisku; reszta liczy się sama (klatka, w której
              punkt Bron najdalej wysuwa się do przodu)
  zastepcze_klipy  klipy dorobione w przerobki.py (szkice), dla porządku i README
"""
import argparse
import json
import math
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (REPO, os.path.join(REPO, "tools"), TU):
    if _s not in sys.path:
        sys.path.insert(0, _s)

DANE = os.path.join(TU, "dane")

# akcje, które odtwarzacz może zamówić u aktora (wspólne dla wszystkich)
AKCJE = ["spoczynek", "ruch", "atak", "krytyk", "blok", "unik", "trafienie", "upadek", "radosc"]

AKTORZY = [
    # ------------------------------------------------------------------ klasy gracza
    {"klucz": "wojownik", "rola": "klasa", "nazwa": "Wojownik", "model": "rycerz", "przerobka": "rycerz",
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "chod", "atak": "atak_miecz", "krytyk": "atak_miecz", "blok": "blok",
               "unik": "unik", "trafienie": "trafienie", "upadek": "upadek", "radosc": "wiwat"},
     "umiejetnosci": {"ciecie": "ciecie", "miazdzacy_cios": "miazdzacy_cios", "kamienna_skora": "kamienna_skora"},
     "punkty": {"Bron": ("RightGripAttachment", (0, 3.9, 0)), "Pocisk": ("RightGripAttachment", (0, 2.4, 0)),
                "Piers": ("BodyFrontAttachment", (0, 0, 0)), "Tarcza": ("TarczaAttachment", (0, 0, 0))},
     "chwile": {"kamienna_skora": 0.35},
     "zastepcze_klipy": ["blok", "unik", "trafienie", "upadek", "ciecie", "miazdzacy_cios", "kamienna_skora"]},
    {"klucz": "zwiadowca", "rola": "klasa", "nazwa": "Zwiadowca", "model": "zwiadowca", "przerobka": "zwiadowca",
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "wiwat"},
     "umiejetnosci": {"uderzenie_z_gory": "uderzenie_z_gory", "zatruta_strzala": "umiejetnosc", "skupienie": "skupienie"},
     "punkty": {"Bron": ("RightGripAttachment", (0, 1.3, 0)), "Pocisk": ("LeftGripAttachment", (0, 0, 0)),
                "Piers": ("BodyFrontAttachment", (0, 0, 0))},
     "chwile": {"umiejetnosc": 1.03, "skupienie": 0.4},
     "zastepcze_klipy": ["skupienie"]},
    {"klucz": "mag", "rola": "klasa", "nazwa": "Mag", "model": "kot_mag", "przerobka": "kot_mag",
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "chod", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "radosc"},
     "umiejetnosci": {"kula_ognia": "kula_ognia", "lodowy_pocisk": "lodowy_pocisk", "bariera": "bariera"},
     "punkty": {"Bron": ("RightGripAttachment", (0.08, 0.0, 2.15)), "Pocisk": ("RightGripAttachment", (0.08, 0.0, 2.15)),
                "Piers": ("BodyFrontAttachment", (0, 0, 0))},
     "chwile": {"kula_ognia": 1.23, "bariera": 0.35},
     "zastepcze_klipy": ["atak", "kula_ognia", "lodowy_pocisk", "bariera", "trafienie", "unik", "upadek", "radosc"]},
    # ------------------------------------------------------------------ przeciwnicy lasu
    {"klucz": "lesny_slime", "rola": "przeciwnik", "nazwa": "Leśny Slime", "model": "slime", "przerobka": "lesny_slime",
     "zastepczy": "ZASTĘPCZY: slime-pet przemalowany na zielono i powiększony ×1,5 (docelowy model Leśnego Slime'a powstaje)",
     "kolory": {"6FF3FF": "A8F07A", "1FB8C9": "4CB443", "1597AE": "37913A", "F2FFFF": "F4FFE8"},
     "klipy": {"spoczynek": "idle", "ruch": "skok", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "skok"},
     "umiejetnosci": {"kwasny_plusk": "atak"},
     "punkty": {"Bron": ("PyskAttachment", (0, 0, 0)), "Pocisk": ("PyskAttachment", (0, 0, -0.2)),
                "Piers": ("GlowaAttachment", (0, -1.2, -1.2))},
     "zastepcze_klipy": ["trafienie", "unik", "upadek"]},
    {"klucz": "cierniowy_wilk", "rola": "przeciwnik", "nazwa": "Cierniowy Wilk", "model": "cierniowy_wilk", "przerobka": None,
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "ryk"},
     "umiejetnosci": {"rozszarpanie": "umiejetnosc"},
     "punkty": {"Bron": ("PyskAttachment", (0, 0, 0)), "Pocisk": ("PyskAttachment", (0, 0, 0)),
                "Piers": ("GlowaAttachment", (0, -0.9, 0.6))},
     "zastepcze_klipy": []},
    {"klucz": "muchomornik", "rola": "przeciwnik", "nazwa": "Muchomornik", "model": "muchomornik", "przerobka": None,
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "wiwat"},
     "umiejetnosci": {"chmura_zarodnikow": "umiejetnosc"},
     "punkty": {"Bron": ("LaskaAttachment", (0, 0, 0)), "Pocisk": ("ChmuraAttachment", (0, 0, 0)),
                "Piers": ("GlowaAttachment", (0, -1.4, 0))},
     "zastepcze_klipy": []},
    {"klucz": "lesny_troll", "rola": "przeciwnik", "nazwa": "Leśny Troll", "model": "lesny_troll", "przerobka": None,
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "ryk"},
     "umiejetnosci": {"ogluszajace_uderzenie": "umiejetnosc"},
     "punkty": {"Bron": ("MaczugaAttachment", (0, 0, 0)), "Pocisk": ("PyskAttachment", (0, 0, 0)),
                "Piers": ("GlowaAttachment", (0, -2.0, 0.4))},
     "zastepcze_klipy": []},
    {"klucz": "straznik_lasu", "rola": "przeciwnik", "nazwa": "Strażnik Lasu", "model": "lesny_troll",
     "przerobka": "straznik_lasu",
     "zastepczy": "ZASTĘPCZY: Leśny Troll ×1,2 w kamiennych barwach z kryształem w piersi (docelowy model Strażnika powstaje)",
     "kolory": {"86704F": "8E949B", "52402C": "5D636B", "B49B72": "B9BEC4"},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "ryk"},
     "umiejetnosci": {"uscisk_korzeni": "umiejetnosc"},
     "punkty": {"Bron": ("MaczugaAttachment", (0, 0, 0)), "Pocisk": ("PiersAttachment", (0, 0, -0.4)),
                "Piers": ("PiersAttachment", (0, 0, 0))},
     "zastepcze_klipy": []},
]

PO_KLUCZU = {a["klucz"]: a for a in AKTORZY}


# --------------------------------------------------------------------------- przygotowanie danych
def postac_aktora(wpis):
    """Postać z modułu modelu + przeróbka prototypu (w pamięci)."""
    from swiat.postacie.roblox_postac import postacie_z_modulu
    import przerobki
    p = postacie_z_modulu(os.path.join(REPO, "swiat", "postacie", wpis["model"] + ".py"))[0]
    if wpis.get("przerobka"):
        przerobki.PRZEROBKI[wpis["przerobka"]](p)
    return p


def _hex(c):
    return c.upper()


def _punkty(rig_dane, wpis):
    """Punkty z tabeli -> [nazwa, indeks kości, x, y, z] względem środka części kości (układ rigu Roblox)."""
    from geometria import cf, orientacja, punkt
    zaczepy = {z[0]: z for z in rig_dane["zaczepy"]}
    wynik = []
    for nazwa, (zaczep, off) in wpis["punkty"].items():
        z = zaczepy.get(zaczep)
        if z is None:
            raise ValueError("%s: punkt %s — model nie ma zaczepu %s (są: %s)"
                             % (wpis["klucz"], nazwa, zaczep, ", ".join(sorted(zaczepy))))
        p = punkt(cf((z[2], z[3], z[4]), orientacja(z[5], z[6], z[7])), tuple(float(v) for v in off))
        wynik.append([nazwa, z[1]] + [round(v, 4) for v in p])
    return wynik


def _chwile(rig, dane, wpis):
    """Chwila trafienia w klipach ataku i umiejętności: klatka, w której punkt Bron najdalej wysuwa się do przodu
    (−Z rigu) względem spoczynku. Zwraca {klip: sekundy}."""
    from geometria import punkt, razy, cf
    bron = next((pk for pk in dane["punkty"] if pk[0] == "Bron"), None)
    if not bron:
        return {}
    i = bron[1]
    off = (bron[2], bron[3], bron[4])
    klipy = set()
    for akcja in ("atak", "krytyk"):
        if wpis["klipy"].get(akcja):
            klipy.add(wpis["klipy"][akcja])
    for kl in wpis["umiejetnosci"].values():
        if kl:
            klipy.add(kl)
    wynik = {}
    for nazwa in sorted(klipy):
        kl = rig.klipy[nazwa]
        najlepsza, z_min = 0, 1e9
        for f in range(kl["dl"] + 1):
            pozy = rig.pozy(rig.transformy(nazwa, f))
            p = punkt(pozy[i], off)
            if p[2] < z_min - 1e-6:
                najlepsza, z_min = f, p[2]
        wynik[nazwa] = round(najlepsza / float(kl["fps"]), 3)
    return wynik


def przygotuj(wpisy, liniowo=False):
    from swiat.postacie.biblioteka.roblox_klocki import probki_liniowe, rig
    from swiat.postacie.roblox_postac import probki_z_blendera
    from geometria import Rig, obwiednia
    postacie = []
    for w in wpisy:
        p = postac_aktora(w)
        p.id = w["klucz"]                                      # osobne próbki dla dwóch aktorów z jednego modelu
        bledy, uwagi = p.sprawdz()
        if bledy:
            sys.exit("%s: postać nie przeszła sprawdzianu:\n  %s" % (w["klucz"], "\n  ".join(bledy)))
        postacie.append((w, p))
    if liniowo:
        probki = {p.id: probki_liniowe(p) for _, p in postacie}
    else:
        print("próbki klipów z Blendera (wspólna blokada) dla: %s" % ", ".join(p.id for _, p in postacie), flush=True)
        probki = probki_z_blendera([p for _, p in postacie])
    os.makedirs(DANE, exist_ok=True)
    for w, p in postacie:
        d = rig(p, probki.get(p.id))
        for c in d["czesci"]:
            c[12] = _hex(w["kolory"].get(_hex(c[12]), c[12]))
        nazwy_klipow = {k["n"] for k in d["klipy"]}
        brak = [v for v in list(w["klipy"].values()) + list(w["umiejetnosci"].values()) if v and v not in nazwy_klipow]
        if brak:
            sys.exit("%s: tabela wskazuje klipy, których nie ma: %s (są: %s)"
                     % (w["klucz"], ", ".join(sorted(set(brak))), ", ".join(sorted(nazwy_klipow))))
        d["punkty"] = _punkty(d, w)
        r = Rig(d)
        mn, mx = obwiednia(r)
        promien = 0.0
        for c in d["czesci"]:
            from geometria import narozniki
            for q in narozniki(r.czesc_cf(c, r.pozy()), c[9:12]):
                promien = max(promien, math.hypot(q[0], q[2]))
        d["wymiary"] = {"wysokosc": round(mx[1], 3), "spod": round(mn[1], 3), "szerokosc": round(mx[0] - mn[0], 3),
                        "glebokosc": round(mx[2] - mn[2], 3), "przod": round(-mn[2], 3), "promien": round(promien, 3)}
        d["chwile"] = dict(_chwile(r, d, w), **w.get("chwile", {}))
        d["klucz"] = w["klucz"]
        d["model_modulu"] = w["model"]
        d["zrodlo_probek"] = "liniowo" if liniowo else "blender"
        sciezka = os.path.join(DANE, w["klucz"] + ".json")
        with open(sciezka, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, separators=(",", ":"))
        print("%-15s %3d części, %2d kości, wzrost %.2f, zasięg %.2f, klipy: %s"
              % (w["klucz"], len(d["czesci"]), len(d["kosci"]), d["wymiary"]["wysokosc"], d["wymiary"]["promien"],
                 ", ".join(k["n"] for k in d["klipy"])))
        if d["uwagi"]:
            for u in d["uwagi"]:
                print("                uwaga:", u)


def wczytaj(klucz):
    sciezka = os.path.join(DANE, klucz + ".json")
    if not os.path.isfile(sciezka):
        raise FileNotFoundError("brak %s — uruchom: python -B swiat/test_walki2/aktorzy.py --tylko %s" % (sciezka, klucz))
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Przygotowanie danych aktorów prototypu walki v2")
    ap.add_argument("--tylko", default="")
    ap.add_argument("--liniowo", action="store_true")
    ap.add_argument("--lista", action="store_true")
    a = ap.parse_args()
    if a.lista:
        for w in AKTORZY:
            print("%-15s %-10s %-15s model %-15s %s" % (w["klucz"], w["rola"], w["nazwa"], w["model"], w["zastepczy"] or ""))
        return
    wybrane = [x for x in a.tylko.split(",") if x] or [w["klucz"] for w in AKTORZY]
    for k in wybrane:
        if k not in PO_KLUCZU:
            sys.exit("nie ma aktora %r (są: %s)" % (k, ", ".join(PO_KLUCZU)))
    przygotuj([PO_KLUCZU[k] for k in wybrane], a.liniowo)


if __name__ == "__main__":
    main()
