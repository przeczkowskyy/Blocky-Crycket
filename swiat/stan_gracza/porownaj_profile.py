#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Profil klas Pawła (src/shared/ClassData.luau) czy wzorcowy (tools/walka/wzorcowe.py) — liczby do pytania 56.
Propozycja liczb, NIE kanon: decyzja należy do ludzi.

    python -B swiat/stan_gracza/porownaj_profile.py                # Markdown na ekran
    python -B swiat/stan_gracza/porownaj_profile.py --graczy 200 --walk 400 --md wynik.md

To samo co swiat/stan_gracza/symulacja_lasu.py (bohater z danych gracza = rozkład klasy dla puli poziomu, bez treningu;
przegrody lasu-pasa z pliku w drzewie — po D-096 jedna strefa na przegrodę; ta sama polityka gracza), tylko dwa razy:
z rozkładami wzorcowymi i z rozkładami z ClassData (procent puli, jak czyta je SerwerStanu w grze). Liczy:
  • szansę wygranej na poziomie wejścia do każdej przegrody (poziom = najniższy poziom przegrody, potwór z zakresu, jaki
    gracz tam spotyka: do poziomu gracza + 1; Strażnik — jego poziom);
  • przejście lasu do wygranej ze Strażnikiem: mediana czasu, przegrane, poziom przy Strażniku, próby Strażnika;
  • rozrzut między klasami (największa − najmniejsza) — zasada D-069: klasy różnią się stylem, nie skutecznością.
Liczy pojedynczo, w jednym procesie (bez wielu rdzeni).
"""
import argparse
import os
import random
import re
import statistics
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (TU, os.path.join(REPO, "tools", "walka")):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import dane as DANE  # noqa: E402
import logika_stanu as LS  # noqa: E402
import silnik  # noqa: E402
import symulacja_lasu as SL  # noqa: E402

CLASSDATA = os.path.join(REPO, "src", "shared", "ClassData.luau")


def rozklady_pawla(D):
    """ClassData.luau (tylko odczyt) → {klasa silnika: rozkład} (LogikaStanu.rozkladZClassData, jak w grze)."""
    with open(CLASSDATA, encoding="utf-8") as f:
        tekst = f.read()
    w = {}
    for idk, s in re.findall(r'\{ id = "(\w+)".*?stats = \{ ([\d, ]+) \}', tekst, re.S):
        r, powod = LS.rozklad_z_class_data(D, [int(x) for x in s.split(",")])
        if r is None:
            raise SystemExit("ClassData %s: %s" % (idk, powod))
        w[D["klasy_gracza"][idk]] = r
    return w


def szansa(D, klasa, p, ziaren, los):
    L = p["od"]
    hi = p["do"] if p["straznik"] else max(p["od"], min(p["do"], L + 1))
    wyg = 0
    g = SL.bohater(D, klasa, L)
    for _ in range(ziaren):
        r = silnik.symuluj(g, {"potwor": p["gatunek"], "poziom": los.randint(p["od"], hi)}, los.randrange(1, 2 ** 31 - 1))
        wyg += r["wynik"] == "wygrana"
    return 100.0 * wyg / ziaren


def przejscie(D, P, klasa, graczy, ziarno, x0, przelot):
    class A:
        tempo = 1.0
    los = random.Random("%s-%d" % (klasa, ziarno))
    gr = [SL.jeden_gracz(D, P, klasa, los, A, x0, przelot) for _ in range(graczy)]
    ok = [g for g in gr if g is not None]
    return {"czas": statistics.median(g["czas"] / 60 for g in ok), "czas90": SL.kwantyl([g["czas"] / 60 for g in ok], 0.9),
            "przegrane": statistics.median(g["przegrane"] for g in ok), "poziom": statistics.median(g["poziom"] for g in ok),
            "proby": statistics.median(g["proby"] for g in ok), "walk": statistics.median(g["walki"] for g in ok),
            "nie": len(gr) - len(ok)}


def f0(x):
    return "%.0f" % x


def f1(x):
    return ("%.1f" % x).replace(".", ",")


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Profil klas Pawła vs wzorcowy w lesie-pasie (pytanie 56)")
    ap.add_argument("--graczy", type=int, default=200, help="graczy na klasę i profil")
    ap.add_argument("--walk", type=int, default=400, help="walk na komórkę szans")
    ap.add_argument("--ziarno", type=int, default=1)
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    t0 = time.time()
    _, D = DANE.dane_z_przypadkami()
    P = SL.przegrody()
    x0, przelot = SL.przybycie_i_przelot()
    profile = {"wzorcowy": {k: dict(D["rozklady"][k]) for k in D["klasy"]}, "Pawła": rozklady_pawla(D)}
    wyniki = {}
    for nazwa, rozklady in profile.items():
        Dp = dict(D, rozklady=rozklady)
        for k in D["klasy"]:
            los = random.Random("szanse-%s-%d" % (k, a.ziarno))
            sz = {p["id"]: szansa(Dp, k, p, a.walk, los) for p in P}
            wyniki[(nazwa, k)] = {"szanse": sz, "las": przejscie(Dp, P, k, a.graczy, a.ziarno, x0, przelot)}
    S = D["statystyki"]
    w = ["## Profil klas Pawła czy wzorcowy — liczby do pytania 56 (propozycja, nie kanon)", "",
         "Rozkłady (procent puli: %s):" % ", ".join(S), ""]
    for k in D["klasy"]:
        w.append("- %s: wzorcowy %s, Pawła (ClassData) %s" % (
            D["nazwy_klas"][k], [round(profile["wzorcowy"][k][s] * 100) for s in S],
            [round(profile["Pawła"][k][s] * 100) for s in S]))
    w += ["", "Przegrody: " + "; ".join("%s %s poz. %d–%d" % (p["id"], silnik.PRZECIWNICY[p["gatunek"]]["nazwa"], p["od"], p["do"])
                                         for p in P) + ".", ""]
    w.append("### Szansa wygranej na poziomie wejścia do przegrody (%%, %d walk na komórkę)" % a.walk)
    w.append("")
    w.append("| Klasa | Profil | " + " | ".join("%s (L%d)" % (p["id"], p["od"]) for p in P) + " |")
    w.append("|---|---|" + "---:|" * len(P))
    for k in D["klasy"]:
        for nazwa in profile:
            w.append("| %s | %s | " % (D["nazwy_klas"][k], nazwa) + " | ".join(
                f0(wyniki[(nazwa, k)]["szanse"][p["id"]]) for p in P) + " |")
    w.append("")
    w.append("### Przejście lasu do wygranej ze Strażnikiem (%d graczy na klasę i profil)" % a.graczy)
    w.append("")
    w.append("| Klasa | Profil | Czas (mediana / 90%) | Przegrane | Walk | Poziom przy Strażniku | Prób Strażnika | Nie skończyło |")
    w.append("|---|---|---|---:|---:|---:|---:|---:|")
    for k in D["klasy"]:
        for nazwa in profile:
            r = wyniki[(nazwa, k)]["las"]
            w.append("| %s | %s | %s / %s min | %s | %s | %s | %s | %d |" % (
                D["nazwy_klas"][k], nazwa, f1(r["czas"]), f1(r["czas90"]), f0(r["przegrane"]), f0(r["walk"]),
                f0(r["poziom"]), f0(r["proby"]), r["nie"]))
    w.append("")
    w.append("### Rozrzut między klasami (D-069: styl, nie skuteczność)")
    w.append("")
    w.append("| Profil | " + " | ".join("szansa %s" % p["id"] for p in P) + " | czas lasu | przegrane |")
    w.append("|---|" + "---:|" * (len(P) + 2))
    for nazwa in profile:
        komorki = []
        for p in P:
            v = [wyniki[(nazwa, k)]["szanse"][p["id"]] for k in D["klasy"]]
            komorki.append("%s pp" % f0(max(v) - min(v)))
        cz = [wyniki[(nazwa, k)]["las"]["czas"] for k in D["klasy"]]
        pr = [wyniki[(nazwa, k)]["las"]["przegrane"] for k in D["klasy"]]
        komorki.append("%s min" % f1(max(cz) - min(cz)))
        komorki.append(f0(max(pr) - min(pr)))
        w.append("| %s | " % nazwa + " | ".join(komorki) + " |")
    w.append("")
    # największe rozjazdy: profil Pawła vs wzorcowy, ta sama klasa
    roz = []
    for k in D["klasy"]:
        for p in P:
            a1, b1 = wyniki[("Pawła", k)]["szanse"][p["id"]], wyniki[("wzorcowy", k)]["szanse"][p["id"]]
            roz.append((abs(a1 - b1), "%s z profilem Pawła ma %s%% zamiast %s%% wygranych w %s (%s, poziom %d)." % (
                D["nazwy_klas"][k], f0(a1), f0(b1), p["id"], silnik.PRZECIWNICY[p["gatunek"]]["nazwa"], p["od"])))
        c1, c0 = wyniki[("Pawła", k)]["las"]["czas"], wyniki[("wzorcowy", k)]["las"]["czas"]
        roz.append((abs(c1 - c0) * 3, "%s z profilem Pawła przechodzi las w %s min zamiast %s min (przegranych %s zamiast %s)." % (
            D["nazwy_klas"][k], f1(c1), f1(c0), f0(wyniki[("Pawła", k)]["las"]["przegrane"]),
            f0(wyniki[("wzorcowy", k)]["las"]["przegrane"]))))
    w.append("Największe rozjazdy (profil Pawła vs wzorcowy, ta sama klasa):")
    w.append("")
    for _d, zdanie in sorted(roz, key=lambda x: -x[0])[:8]:
        w.append("- " + zdanie)
    w.append("")
    w.append("_python -B swiat/stan_gracza/porownaj_profile.py --graczy %d --walk %d --ziarno %d (%.0f s)_" % (
        a.graczy, a.walk, a.ziarno, time.time() - t0))
    tekst = "\n".join(w) + "\n"
    print(tekst)
    if a.md:
        with open(a.md, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(tekst)


if __name__ == "__main__":
    main()
