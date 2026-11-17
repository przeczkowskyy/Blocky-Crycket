#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Liczbowa kontrola przenikania broni w głowę i tułów we WSZYSTKICH klipach aktorów walki (bez Studio).

    python -B swiat/postacie/przenikanie/przenikanie.py                    # wszyscy aktorzy z bronią, tabela
    python -B swiat/postacie/przenikanie/przenikanie.py --aktor mag,wojownik
    python -B swiat/postacie/przenikanie/przenikanie.py --md               # wiersze tabeli do WYNIKI.md
    python -B swiat/postacie/przenikanie/przenikanie.py --kamera           # + „broń zasłania twarz” z kamery finału
    python -B swiat/postacie/przenikanie/przenikanie.py --podglad <folder> # PNG najgorszych chwil (rzuty brył)
    python -B swiat/postacie/przenikanie/przenikanie.py --dane <plik.json> --aktor <klucz>   # inny plik rigu

Dane: swiat/test_walki2/dane/<klucz>.json (to, co gra odtwarza) albo dowolny plik z roblox_klocki.rig(). Pozy
liczy lustro modułu Klipy.luau (pozy.py), pomiar — pomiar.py (opis miar i progów), kamera — kamera.py.
Kod wyjścia 1, gdy którykolwiek scenariusz przekracza próg (także znane przypadki — pilnuje ich test pakietu).
Test, który pilnuje tego odtąd przy każdej zmianie: swiat/test_walki2/testy/test_przenikania.py. Wyniki: WYNIKI.md.
"""
import argparse
import json
import math
import os
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TU)))
WALKA = os.path.join(REPO, "swiat", "test_walki2")
for _s in (TU, WALKA):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import pomiar as PM  # noqa: E402

RODZAJE = {"klip": "klip", "wejscie": "spoczynek → klip (0,12 s)", "wyjscie": "klip → spoczynek (0,15 s)",
           "upadek": "→ upadek (0,08 s)", "wskrzeszenie": "upadek → spoczynek (wskrzeszenie, 0,45 s)",
           "radosc": "spoczynek → radość (0,2 s)"}


def tabela_aktorow():
    import aktorzy as A
    return A


def wczytaj(klucz, dane=None):
    if dane:
        with open(dane, encoding="utf-8") as f:
            return json.load(f)
    return tabela_aktorow().wczytaj(klucz)


def aktorzy_z_bronia():
    """Klucze aktorów walki, którzy trzymają broń (SPEC albo wykryci z nazw), i lista pominiętych z powodem."""
    A = tabela_aktorow()
    z, bez = [], []
    for w in A.AKTORZY:
        try:
            d = A.wczytaj(w["klucz"])
        except FileNotFoundError:
            bez.append((w["klucz"], "brak danych"))
            continue
        if PM.spec_aktora(w["klucz"], d):
            z.append(w["klucz"])
        else:
            bez.append((w["klucz"], "bez broni w ręku"))
    return z, bez


def zbadaj(klucz, d=None, gestosc=1.0, postep=None):
    """Pełny pomiar aktora -> (Pomiar, wyniki scenariuszy)."""
    A = tabela_aktorow()
    d = d or A.wczytaj(klucz)
    spec = PM.spec_aktora(klucz, d)
    if not spec:
        return None, []
    pm = PM.Pomiar(d, spec)
    sc = PM.scenariusze(pm.a, A.PO_KLUCZU.get(klucz), gestosc)
    return pm, PM.zmierz(pm, sc, postep)


def zle(pm, w):
    """Strefy scenariusza przekraczające próg: [(strefa, głębokość)]."""
    wyn = []
    for z in pm.strefy:
        s = w["strefy"][z.nazwa]
        if -s["m"] > z.prog:
            wyn.append((z.nazwa, -s["m"]))
    return wyn


def opis_strefy(s, prog):
    m = s["m"]
    if m >= PM.ODCIECIE:
        return "≥ %.2f" % PM.ODCIECIE
    if m >= 0:
        return "odstęp %.3f" % m
    tekst = "**%.3f**" % -m if -m > prog else "dotyk %.3f" % -m
    return tekst


def _l(x):
    return ("%.3f" % x).replace(".", ",")


def wiersz_md(klucz, pm, w):
    """Wiersz tabeli: aktor | scenariusz | najgorsza chwila | głowa | tułów | (nakrycie) | wynik."""
    st = w["strefy"]
    najg = min(st.values(), key=lambda s: s["m"])
    t = najg["t"] or 0.0
    kl = w["klip"]
    fps = pm.a.klipy[kl]["fps"] if kl in pm.a.klipy else 30.0
    chwila = "%.3f s (kl. %.1f)" % (t, t * fps) if w["rodzaj"] == "klip" else "%.3f s przejścia" % t
    kom = []
    for z in pm.strefy:
        s = st[z.nazwa]
        if s["m"] >= PM.ODCIECIE:
            kom.append("≥ " + _l(PM.ODCIECIE).rstrip("0"))
            continue
        if s["m"] >= 0:
            kom.append("odstęp " + _l(s["m"]))
        else:
            g = -s["m"]
            kom.append(("**głęb. %s**" if g > z.prog else "dotyk %s") % _l(g))
    bledy = zle(pm, w)
    wynik = "OBLANY (%s)" % ", ".join("%s %s" % (n, _l(g)) for n, g in bledy) if bledy else "OK"
    gdzie = ""
    if najg["bron"]:
        gdzie = " — %s → %s" % (najg["bron"].split("/")[-1], najg["cialo"].split("/")[-1])
    return "| %s | %s | %s | %s | %s |" % (klucz, w["nazwa"], chwila + gdzie, " | ".join(kom), wynik)


def kamera_aktora(klucz, pm, kroki=2):
    """Zasłonięcie twarzy z kamery: radość (objazd finału, |kąt| ≤ 35°) i spoczynek z przodu (|kąt| ≤ 35°) — bramka;
    spoczynek i radość 40–70° (ujęcia naSiebie / efekt / zbliżenie) — informacja. -> lista wyników."""
    import kamera as K
    A = tabela_aktorow()
    wpis = A.PO_KLUCZU.get(klucz)
    if not wpis or wpis["rola"] != "klasa":
        return []
    tw = K.Twarz(pm, rozdz=80)
    wys = pm.d["wymiary"]["wysokosc"]
    wyn = []
    # początek finału: zwycięzca obraca się do kamery (kąt twarzy z kat_start do 35° w 0,45 s), radość wchodzi ze
    # spoczynku przez 0,2 s — kąt i poza liczone w tej samej chwili; obie strony (gracz: kamera z prawej, lustro: z lewej)
    spocz, rad = wpis["klipy"].get("spoczynek"), wpis["klipy"].get("radosc")
    if spocz in pm.a.klipy and rad in pm.a.klipy:
        naj = (0.0, None)
        for kat_start in (62.0, 90.0, 120.0, 150.0):
            for tau, kat in K.przebieg_finalu(kat_start, do=0.6):
                w = min(1.0, tau / 0.2)
                _, Wb = pm.a.poza([(spocz, tau, 1.0 - w), (rad, tau, w)])
                for znak in (1, -1):
                    r = tw.zmierz(Wb, K.kamera_objazdu(wys, kat, znak))
                    s = tw.ocena(r)
                    if naj[1] is None or s > naj[0]:
                        naj = (s, (round(tau * 30, 1), round(kat * znak), r))
        wyn.append({"akcja": "finał (obrót do kamery)", "klip": rad, "bramka": True, "ocena": naj[0],
                    "klatka": naj[1][0], "kat": naj[1][1], "r": naj[1][2]})
    for akcja in ("radosc", "spoczynek"):
        kl = wpis["klipy"].get(akcja)
        if not kl or kl not in pm.a.klipy:
            continue
        for zakres, bramka in ((range(-35, 36, 5), True), (list(range(-70, -35, 5)) + list(range(40, 71, 5)), False)):
            naj = (0.0, None)
            for f in range(0, pm.a.klipy[kl]["dl"] + 1, kroki):
                _, Wb = pm.a.poza([(kl, f / pm.a.klipy[kl]["fps"], 1.0)])
                for kat in zakres:
                    r = tw.zmierz(Wb, K.kamera_objazdu(wys, kat))
                    s = tw.ocena(r)
                    if naj[1] is None or s > naj[0]:
                        naj = (s, (f, kat, r))
            wyn.append({"akcja": akcja, "klip": kl, "bramka": bramka, "ocena": naj[0], "klatka": naj[1][0],
                        "kat": naj[1][1], "r": naj[1][2]})
    return wyn


def podglad(klucz, pm, wyniki, folder, tylko_zle=True):
    """PNG najgorszej chwili każdego oblanego scenariusza: przód, prawy bok, góra; czerwone kółko = bryła broni."""
    from PIL import Image, ImageDraw
    import kamera as K
    os.makedirs(folder, exist_ok=True)
    pliki = []
    for w in wyniki:
        if tylko_zle and not zle(pm, w):
            continue
        najg = min(w["strefy"].values(), key=lambda s: s["m"])
        tory = najg.get("tory")
        if not tory:
            continue
        _, Wb = pm.a.poza(tory)
        r = pm.pomiar_pozy(Wb)
        pk = [(Wb[r[z.nazwa][1], :3, 3], (220, 0, 0)) for z in pm.strefy if r[z.nazwa][0] < 0 and r[z.nazwa][1] >= 0]
        kafle = []
        for v in ((0, 0, 1), (-1, 0, 0), (0, -1, 0.001)):
            im = K.obraz(pm, Wb, v, rozmiar=300, podswietl=pm.bron, punkty=pk)
            kafle.append(im)
        ark = Image.new("RGB", (900, 324), (255, 255, 255))
        for i, im in enumerate(kafle):
            ark.paste(im, (i * 300, 24))
        # domyślna czcionka PIL nie ma polskich liter ani strzałek — napis w ASCII
        ImageDraw.Draw(ark).text((6, 6), "%s / %s, t = %.3f s: %s" % (
            klucz, w["nazwa"].replace("→", "->"), najg["t"] or 0,
            ", ".join("%s %.3f" % (z.nazwa, -r[z.nazwa][0]) for z in pm.strefy)), fill=(0, 0, 0))
        nazwa = "%s_%s.png" % (klucz, "".join(c if c.isalnum() else "_" for c in w["nazwa"]).strip("_"))
        ark.save(os.path.join(folder, nazwa))
        pliki.append(nazwa)
    return pliki


def main():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Przenikanie broni w głowę i tułów w klipach aktorów walki")
    ap.add_argument("--aktor", default="", help="klucze po przecinku (domyślnie wszyscy z bronią)")
    ap.add_argument("--dane", default="", help="plik rigu zamiast swiat/test_walki2/dane/<klucz>.json")
    ap.add_argument("--gestosc", type=float, default=1.0, help="1 = 120 próbek/s i 8 faz spoczynku (domyślnie)")
    ap.add_argument("--md", action="store_true", help="wiersze tabeli Markdown")
    ap.add_argument("--kamera", action="store_true", help="także zasłonięcie twarzy z kamery finału")
    ap.add_argument("--podglad", default="", help="folder na PNG najgorszych chwil oblanych scenariuszy")
    ap.add_argument("--json", default="", help="zapisz wyniki do pliku JSON")
    a = ap.parse_args()
    if a.aktor:
        klucze = [k for k in a.aktor.split(",") if k]
    else:
        klucze, bez = aktorzy_z_bronia()
        for k, pow_ in bez:
            print("pomijam %-15s (%s)" % (k, pow_))
    bledow = 0
    zrzut = {}
    for k in klucze:
        t0 = time.time()
        d = wczytaj(k, a.dane or None)
        pm, wyniki = zbadaj(k, d, a.gestosc)
        if pm is None:
            print("%s: bez broni — nic do mierzenia" % k)
            continue
        print("== %s (%d scenariuszy, %d próbek, %.1f s; strefy: %s)" % (
            k, len(wyniki), sum(w["probek"] for w in wyniki), time.time() - t0,
            ", ".join("%s %d brył, próg %.2f" % (z.nazwa, len(z.bryly), z.prog) for z in pm.strefy)))
        for w in wyniki:
            if a.md:
                print(wiersz_md(k, pm, w))
            else:
                b = zle(pm, w)
                print("  %-36s %-12s %s %s" % (w["nazwa"], w["rodzaj"], "  ".join(
                    "%s %s" % (z.nazwa, opis_strefy(w["strefy"][z.nazwa], z.prog)) for z in pm.strefy),
                    "OBLANY" if b else ""))
            bledow += bool(zle(pm, w))
        zrzut[k] = [{"nazwa": w["nazwa"], "rodzaj": w["rodzaj"], "klip": w["klip"], "strefy": {
            n: {kk: vv for kk, vv in s.items() if kk != "tory"} for n, s in w["strefy"].items()}} for w in wyniki]
        if a.kamera:
            for r in kamera_aktora(k, pm):
                zakres = ("τ 0–0,6 s, kąt 62…150 → 35°" if r["akcja"].startswith("finał") else
                          "przód |kąt| ≤ 35°" if r["bramka"] else "ukos 40–70°      ")
                print("  kamera %-9s %-6s %s: najgorzej ocena %.2f (kl. %s, kąt %+d°: oczy %.0f%%, rysy %.0f%%, głowa %.0f%%)%s"
                      % (r["akcja"], r["klip"], zakres, r["ocena"],
                         r["klatka"], r["kat"], 100 * r["r"]["oczy"], 100 * r["r"]["rysy"], 100 * r["r"]["glowa"],
                         "  ZASŁONIĘTA" if r["bramka"] and r["ocena"] > 1 else ""))
                bledow += bool(r["bramka"] and r["ocena"] > 1)
        if a.podglad:
            for p in podglad(k, pm, wyniki, a.podglad):
                print("  podgląd:", p)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(zrzut, f, ensure_ascii=False, indent=1, default=lambda x: None if x == math.inf else str(x))
    print("scenariuszy ponad próg: %d" % bledow)
    sys.exit(1 if bledow else 0)


if __name__ == "__main__":
    main()
