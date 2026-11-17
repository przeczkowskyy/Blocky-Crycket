#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Punkty statystyk za poziom (propozycja D-097: 5 do rozdania) — warianty i gracz, który rozdaje „źle”.
Propozycja liczb, NIE kanon.

    python -B swiat/stan_gracza/punkty_statystyk.py                 # Markdown na ekran (kilka minut, jeden proces)
    python -B swiat/stan_gracza/punkty_statystyk.py --graczy 60 --md wynik.md

Bohater na poziomie L = rozkład klasy dla puli 30 + AUTO × (L − 1) (rozdzielane samo, jak dziś) + RĘKA × (L − 1)
punktów rozdanych przez gracza według strategii:
  • „klasa” — tak jak rozkład klasy (gracz rozsądny),
  • „po równo” — po równo w sześć statystyk (gracz, który klika wszystko po kolei),
  • „w główną” — wszystko w najmocniejszą statystykę klasy,
  • „w nieswoją” — wszystko w najsłabszą statystykę klasy (najgorszy przypadek).
Warianty: dziś (AUTO 10, RĘKA 0), a (0 + 5), b (5 + 5), c (0 + 10). Profile klas: wzorcowy (tools/walka/wzorcowe.py)
i ClassData Pawła (to, co dziś czyta gra; pytanie 56). Las: swiat/stan_gracza/symulacja_lasu.py (jeden_gracz —
przegrody lasu-pasa z drzewa, po D-096). Bagno: gracz po wygranej ze Strażnikiem Gaju wchodzi do Bagna z tym poziomem
(swiat/pety_proba/ekonomia_jajek.py, tylko uruchamiany; walki zapisywane jak w kara_przegranej.py).
„1. podejście” = ilu graczy wygrało ze strażnikiem w pierwszej walce z nim.
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
for _s in (TU, os.path.join(REPO, "tools", "walka")):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import dane as DANE  # noqa: E402
import logika_stanu as LS  # noqa: E402
import silnik  # noqa: E402
import symulacja_lasu as SL  # noqa: E402
import porownaj_profile as PPF  # noqa: E402
import kara_przegranej as KP  # noqa: E402  (zapis walk i gracze ekonomii jajek)

EJ = KP.EJ
WARIANTY = [("dziś: 10 samo", 10, 0), ("a: 5 do rozdania", 0, 5), ("b: 5 samo + 5 do rozdania", 5, 5),
            ("c: 10 do rozdania", 0, 10)]
STRATEGIE = ["klasa", "po równo", "w główną", "w nieswoją"]

USTAWIENIE = {}
_BOHATER = SL.bohater


def bohater(D, klasa, L):
    """Zastępuje symulacja_lasu.bohater na czas liczenia (ekonomia jajek woła SL.bohater w chwili walki)."""
    auto, reka, strategia = USTAWIENIE["auto"], USTAWIENIE["reka"], USTAWIENIE["strategia"]
    r = D["rozklady"][klasa]
    st = LS.rozdziel(D, r, D["pula"]["baza"] + auto * (L - 1))
    pkt = reka * (L - 1)
    if pkt > 0:
        if strategia == "klasa":
            dod = LS.rozdziel(D, r, pkt)
        elif strategia == "po równo":
            dod = LS.rozdziel(D, {s: 1.0 / 6 for s in D["statystyki"]}, pkt)
        else:
            kolejnosc = sorted(D["statystyki"], key=lambda s: (r[s], -D["statystyki"].index(s)))
            cel = kolejnosc[-1] if strategia == "w główną" else kolejnosc[0]
            dod = {s: (pkt if s == cel else 0) for s in D["statystyki"]}
        for s in D["statystyki"]:
            st[s] += dod[s]
    return LS.opis_bohatera(D, klasa, L, st)


def pierwsze_podejscie(walki, gatunek):
    for f in walki:
        if f["gatunek"] == gatunek:
            return f["wygrana"]
    return None


def licz(D, graczy, ziarno):
    P, Pb = SL.przegrody(), EJ.przegrody_bagna()
    x0, przelot = SL.przybycie_i_przelot()
    xb, przelot_b = EJ.przybycie_i_przelot_bagna()
    w = {"las_czas": [], "las_przeg": [], "las_1": [], "las_L": [], "bag_czas": [], "bag_przeg": [], "bag_1": [],
         "bag_nie": 0}
    for k in D["klasy"]:
        los = random.Random("punkty-%s-%d" % (k, ziarno))
        for _ in range(graczy):
            stan = {}
            walki, wyg = KP.walki_gracza(EJ.gracz, D, P, k, los, x0, przelot, po_strazniku=False, limit_min=SL.LIMIT_MIN,
                                         koniec=stan)
            if wyg is None:
                continue
            w["las_czas"].append(wyg / 60)
            w["las_przeg"].append(sum(1 for f in walki if not f["wygrana"]))
            w["las_1"].append(pierwsze_podejscie(walki, "straznik_lasu"))
            w["las_L"].append(stan["L"])
            walki_b, wyg_b = KP.walki_gracza(EJ.gracz, D, Pb, k, los, xb, przelot_b, L0=stan["L"], xp0=stan["xp"],
                                             troll=EJ.TROLL_BAGNA, dojscie=EJ.DOJSCIE_BAGNA, po_strazniku=False,
                                             limit_min=SL.LIMIT_MIN)
            if wyg_b is None:
                w["bag_nie"] += 1
                continue
            w["bag_czas"].append(wyg_b / 60)
            w["bag_przeg"].append(sum(1 for f in walki_b if not f["wygrana"]))
            w["bag_1"].append(pierwsze_podejscie(walki_b, "straznik_topieli"))
    return w


def szansa_pierwszej(D, ziaren=600):
    """Pierwsza walka: bohater 1. poziomu z Leśnym Slime'em 1. poziomu (pierwsza przegroda po przybyciu)."""
    w = {}
    for k in D["klasy"]:
        los = random.Random("pierwsza-%s" % k)
        g = _BOHATER(D, k, 1)
        wyg = sum(silnik.symuluj(g, {"potwor": "lesny_slime", "poziom": 1}, los.randrange(1, 2 ** 31 - 1))["wynik"] == "wygrana"
                  for _ in range(ziaren))
        w[k] = 100.0 * wyg / ziaren
    return w


def f1(x):
    return ("%.1f" % x).replace(".", ",")


def f0(x):
    return "%.0f" % x


def proc(xs):
    xs = [x for x in xs if x is not None]
    return 100.0 * sum(1 for x in xs if x) / len(xs) if xs else 0


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Punkty statystyk za poziom: warianty × strategie × profile")
    ap.add_argument("--graczy", type=int, default=50, help="graczy na klasę w każdej komórce")
    ap.add_argument("--ziarno", type=int, default=1)
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    t0 = time.time()
    _, D0 = DANE.dane_z_przypadkami()
    if EJ.BAGNO not in sys.path:
        sys.path.insert(0, EJ.BAGNO)
    import przeciwnicy  # noqa: E402  (swiat/bagno_pas_gra — tylko odczyt)
    przeciwnicy.zaladuj_do_silnika(silnik)
    profile = {"ClassData (gra)": PPF.rozklady_pawla(D0), "wzorcowy": {k: dict(D0["rozklady"][k]) for k in D0["klasy"]}}
    out = ["## Punkty statystyk za poziom — propozycja liczb (nie kanon, D-097)", "",
           "%d graczy na klasę w komórce (trzy klasy razem). Las do wygranej ze Strażnikiem Gaju (przegrody po D-096), Bagno "
           "od wejścia do wygranej ze Strażnikiem Topieli (limit %d min). Czas = mediana minut; przegrane = mediana; "
           "„1. podejście” = %% graczy, którzy wygrali pierwszą walkę ze strażnikiem." % (a.graczy, SL.LIMIT_MIN), ""]
    silnik_symuluj = silnik.symuluj
    SL.bohater = bohater
    silnik.symuluj = KP._symuluj
    try:
        for nazwa_p, rozklady in profile.items():
            D = dict(D0, rozklady=rozklady)
            pierwsza = szansa_pierwszej(D)
            out.append("### Profil klas: %s" % nazwa_p)
            out.append("")
            out.append("Pierwsza walka (1. poziom, Leśny Slime poz. 1): " + ", ".join(
                "%s %s%%" % (D["nazwy_klas"][k], f0(v)) for k, v in pierwsza.items()) + ".")
            out.append("")
            out.append("| Wariant | Gracz rozdaje | Las: czas | Las: przegrane | Gaj: 1. podejście | Poziom po lesie | "
                       "Bagno: czas | Bagno: przegrane | Topiel: 1. podejście | Nie skończyło Bagna |")
            out.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
            for nazwa_w, auto, reka in WARIANTY:
                for strategia in (STRATEGIE if reka > 0 else ["—"]):
                    USTAWIENIE.update(auto=auto, reka=reka, strategia=strategia)
                    r = licz(D, a.graczy, a.ziarno)
                    out.append("| %s | %s | %s | %s | %s%% | %s | %s | %s | %s%% | %d |" % (
                        nazwa_w, strategia, f1(statistics.median(r["las_czas"])), f0(statistics.median(r["las_przeg"])),
                        f0(proc(r["las_1"])), f0(statistics.median(r["las_L"])),
                        f1(statistics.median(r["bag_czas"])) if r["bag_czas"] else "—",
                        f0(statistics.median(r["bag_przeg"])) if r["bag_przeg"] else "—", f0(proc(r["bag_1"])), r["bag_nie"]))
                    print(out[-1], flush=True)
            out.append("")
    finally:
        SL.bohater = _BOHATER
        silnik.symuluj = silnik_symuluj
    out.append("_python -B swiat/stan_gracza/punkty_statystyk.py --graczy %d --ziarno %d (%.0f s)_" % (
        a.graczy, a.ziarno, time.time() - t0))
    tekst = "\n".join(out) + "\n"
    print(tekst)
    if a.md:
        with open(a.md, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(tekst)


if __name__ == "__main__":
    main()
