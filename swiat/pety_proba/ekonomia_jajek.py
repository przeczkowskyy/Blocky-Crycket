#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiedy nowy gracz kupi jajko leśne — Złoto z walk w lesie-pasie przy dzisiejszym łupie. Propozycja liczb, NIE kanon.

    python -B swiat/pety_proba/ekonomia_jajek.py                 # tabela: warianty ceny × 1.–5. jajko (Markdown)
    python -B swiat/pety_proba/ekonomia_jajek.py --graczy 200 --md wynik.md

Gracz jak w swiat/stan_gracza/symulacja_lasu.py (ta sama polityka, przegrody, bohater z danych gracza, krzywa
doświadczenia, łup z silnika tools/walka/silnik.py; test pilnuje, że do wygranej ze Strażnikiem pętla daje to samo co
symulacja_lasu.jeden_gracz). Dwie rzeczy dochodzą:
  • Złoto z łupu (walka.lup.zloto) — liczone od wejścia do lasu; jajko kupuje się od razu, gdy Złota wystarcza
    (bez czasu na dojście do inkubatora — ok. 1,7 s od przybycia, a w trakcie walk gracz i tak przechodzi obok);
  • po Strażniku gracz dalej walczy w przegrodzie przed nim (las nie ma dziś dalszego celu na Złoto), do LIMIT_MIN.
Premii petów (+% Złota) tu NIE liczę — to dolna granica tempa.
"""
import argparse
import os
import random
import statistics
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (TU, os.path.join(REPO, "swiat", "stan_gracza"), os.path.join(REPO, "tools", "walka")):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import dane as DANE_STANU  # noqa: E402  (swiat/stan_gracza/dane.py — tylko odczyt)
import logika_stanu as LS  # noqa: E402
import silnik  # noqa: E402
import symulacja_lasu as SL  # noqa: E402

LIMIT_MIN = 60.0
JAJEK = 5


def gracz(D, P, klasa, los, x0, przelot, po_strazniku=True, limit_min=LIMIT_MIN):
    """Jeden gracz: lista (czas s, Złoto łącznie z walk) po każdej walce + wynik jak symulacja_lasu.jeden_gracz
    (czas wygranej ze Strażnikiem albo None). Ta sama kolejność losowań co tam."""
    L, xp, czas = 1, 0, przelot + abs(P[0]["x"] - x0) / SL.PREDKOSC
    i = 0
    z_rzedu = farma = 0
    troll_od = 0.0
    zloto = 0
    os_czasu = []
    wygrana_straznika = None
    while czas <= limit_min * 60:
        p = P[i]
        cel = p
        if p["gatunek"] == "lesny_troll" and czas < troll_od:
            cel = P[i - 1]
        hi = cel["do"] if cel["straznik"] else max(cel["od"], min(cel["do"], L + 1))
        pz = los.randint(cel["od"], hi)
        r = silnik.symuluj(SL.bohater(D, klasa, L), {"potwor": cel["gatunek"], "poziom": pz}, los.randrange(1, 2 ** 31 - 1))
        czas += r["czas"] + SL.EKRAN_WYNIKU + SL.DOJSCIE[cel["gatunek"]]
        zloto += r["lup"]["zloto"]
        os_czasu.append((czas, zloto))
        L, xp, _ = LS.awans(D, L, xp, r["lup"]["doswiadczenie"])
        wygrana = r["wynik"] == "wygrana"
        if wygrana:
            z_rzedu = 0
            if p["straznik"]:
                if wygrana_straznika is None:
                    wygrana_straznika = czas
                if not po_strazniku:
                    break
                czas += abs(P[i - 1]["x"] - p["x"]) / SL.PREDKOSC
                i -= 1
                farma = 10 ** 9                       # zostaje w przegrodzie przed Strażnikiem
                continue
            if cel is p and p["gatunek"] == "lesny_troll":
                troll_od = czas + p["odrodzenie"]
            if farma > 0:
                farma -= 1
                if farma == 0:
                    czas += abs(P[i + 1]["x"] - p["x"]) / SL.PREDKOSC
                    i += 1
                continue
            if i + 1 < len(P) and L >= P[i + 1]["od"]:
                czas += abs(P[i + 1]["x"] - p["x"]) / SL.PREDKOSC
                i += 1
            continue
        z_rzedu += 1
        if p["straznik"]:
            czas += abs(P[i - 1]["x"] - p["x"]) / SL.PREDKOSC
            i -= 1
            farma = SL.ZAPAS_FARMY
        elif z_rzedu >= 2 and i > 0:
            czas += abs(P[i - 1]["x"] - p["x"]) / SL.PREDKOSC
            i -= 1
            z_rzedu = 0
    return os_czasu, wygrana_straznika


def ceny(wariant, n):
    """Cena n-tego jajka (n = 0, 1, …) dla wariantu {"tryb": "stala", "cena"} albo {"tryb": "rosnaca", start, krok, maks}."""
    if wariant["tryb"] == "stala":
        return wariant["cena"]
    return min(wariant["maks"], wariant["start"] + wariant["krok"] * n)


def zakupy(os_czasu, wariant, jajek=JAJEK):
    """Chwile zakupu kolejnych jajek (s) — kupuje od razu, gdy Złota wystarcza; None, gdy nie zdążył."""
    wydane, wynik = 0, []
    for t, z in os_czasu:
        while len(wynik) < jajek and z - wydane >= ceny(wariant, len(wynik)):
            wydane += ceny(wariant, len(wynik))
            wynik.append(t)
    return wynik + [None] * (jajek - len(wynik))


def wszyscy_gracze(graczy, ziarno=1):
    _, D = DANE_STANU.dane_z_przypadkami()
    P = SL.przegrody()
    x0, przelot = SL.przybycie_i_przelot()
    w = []
    for k in D["klasy"]:
        los = random.Random("jajka-%s-%d" % (k, ziarno))
        for _ in range(graczy):
            w.append(gracz(D, P, k, los, x0, przelot)[0])
    return w


def tabela(gracze, warianty):
    """{nazwa wariantu: [(mediana, p10, p90, ilu nie zdążyło) dla jajka 1..JAJEK]} w minutach."""
    wynik = {}
    for nazwa, wariant in warianty:
        kol = [[] for _ in range(JAJEK)]
        for os_czasu in gracze:
            for j, t in enumerate(zakupy(os_czasu, wariant)):
                kol[j].append(None if t is None else t / 60.0)
        wiersz = []
        for j in range(JAJEK):
            ok = sorted(x for x in kol[j] if x is not None)
            if not ok:
                wiersz.append((None, None, None, len(kol[j])))
                continue
            wiersz.append((statistics.median(ok), SL.kwantyl(ok, 0.1), SL.kwantyl(ok, 0.9), len(kol[j]) - len(ok)))
        wynik[nazwa] = wiersz
    return wynik


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Kiedy gracz kupi jajko leśne (Złoto z lasu-pasa)")
    ap.add_argument("--graczy", type=int, default=100, help="graczy na klasę")
    ap.add_argument("--ziarno", type=int, default=1)
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    t0 = time.time()
    import json
    with open(os.path.join(TU, "ustawienia.json"), encoding="utf-8") as f:
        U = json.load(f)
    c = U["jajka"][0]["cena"]
    warianty = [
        ("kalkulator: stała %d" % c["kalkulator"], {"tryb": "stala", "cena": c["kalkulator"]}),
        ("stała %d" % c["start"], {"tryb": "stala", "cena": c["start"]}),
        ("rosnąca %d +%d do %d (propozycja)" % (c["start"], c["krok"], c["maks"]),
         {"tryb": "rosnaca", "start": c["start"], "krok": c["krok"], "maks": c["maks"]}),
    ]
    gracze = wszyscy_gracze(a.graczy, a.ziarno)
    T = tabela(gracze, warianty)

    def f(x):
        return "—" if x is None else ("%.1f" % x).replace(".", ",")
    w = ["## Kiedy nowy gracz kupi jajko leśne — propozycja liczb (nie kanon)", "",
         "Złoto z walk w lesie-pasie, gracz jak w `swiat/stan_gracza/symulacja_lasu.py` (%d graczy na klasę, trzy klasy); "
         "po Strażniku walczy dalej w przegrodzie przed nim. Minuty od wejścia do lasu: mediana (10%%–90%% graczy)." %
         a.graczy, "",
         "| Cena | " + " | ".join("%d. jajko" % (j + 1) for j in range(JAJEK)) + " |",
         "|---|" + "---|" * JAJEK]
    for nazwa, _w in warianty:
        w.append("| %s | " % nazwa + " | ".join(
            "%s (%s–%s)%s" % (f(m), f(lo), f(hi), (" · %d bez" % n) if n else "") for m, lo, hi, n in T[nazwa]) + " |")
    w.append("")
    for nazwa, _w in warianty:
        med = [m for m, _lo, _hi, _n in T[nazwa]]
        if all(x is not None for x in med):
            odstepy = [med[0]] + [med[j] - med[j - 1] for j in range(1, JAJEK)]
            w.append("- %s: odstępy między zakupami (mediany) %s min" % (nazwa, " → ".join(f(x) for x in odstepy)))
    w.append("")
    w.append("_python -B swiat/pety_proba/ekonomia_jajek.py --graczy %d --ziarno %d (%.0f s)_" % (a.graczy, a.ziarno,
                                                                                                   time.time() - t0))
    tekst = "\n".join(w) + "\n"
    print(tekst)
    if a.md:
        with open(a.md, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(tekst)


if __name__ == "__main__":
    main()
