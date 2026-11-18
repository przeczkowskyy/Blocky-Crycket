#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wpływ skilli petów (D-101) na walki — liczby z silnika walki, nie z głowy. Propozycja liczb, NIE kanon.

    python -B swiat/pety_proba/skille_petow.py                 # tabela: szansa wygranej ze strażnikami, czas, dochód
    python -B swiat/pety_proba/skille_petow.py --ziaren 400 --graczy 20 --md wynik.md

Bohater jak w grze: swiat/stan_gracza (logika_stanu.opis_bohatera — rozkład klasy dla puli poziomu, bez treningu) +
modyfikator peta przez te same funkcje, którymi Sygnaly/Modyfikatory składa premie (czysty_modyfikator,
zloz_modyfikatory, opis_z_modyfikatorami): `procent` → pole silnika `pet` (mnożnik statystyk, D-059), `pasywki` → pole
`premie` (tylko pasywki klasy gracza), `lup` → premia do łupu. Silnik: tools/walka/silnik.py (+ przeciwnicy Bagna
z swiat/bagno_pas_gra/przeciwnicy.py w pamięci). Tylko odczyt cudzych pakietów.

CZĘŚĆ 1 — szansa wygranej (ziarna 1…N) ze Strażnikiem Gaju (poziom 10), Strażnikiem Topieli (poziom 16) i Wężem Stu
Lian (poziom 23, Dżungla — przeciwnicy z swiat/dzungla_pas_gra/przeciwnicy.py w pamięci silnika), gracz na poziomie
strażnika i o jeden niżej, każda klasa: bez peta i z każdym petem.
CZĘŚĆ 2 — przejście (ekonomia_jajek.gracz z bohaterem z petem i premią do łupu jak w stanie gracza): minuty do
wygranej ze Strażnikiem Gaju, (od wejścia do Bagna) ze Strażnikiem Topieli i (od wejścia do Dżungli) z Wężem Stu Lian;
dochód = Złoto na minutę do tej chwili.
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
STAN = os.path.join(REPO, "swiat", "stan_gracza")
for _s in (TU, STAN, os.path.join(REPO, "tools", "walka"), os.path.join(REPO, "swiat", "bagno_pas_gra")):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import dane_petow as DP  # noqa: E402
import logika_petow as LP  # noqa: E402
import ekonomia_jajek as EJ  # noqa: E402

STRAZNICY = (("straznik_lasu", 10, "Strażnik Gaju"), ("straznik_topieli", 16, "Strażnik Topieli"),
             ("waz_stu_lian", 23, "Wąż Stu Lian"))


def stan():
    """Dane stanu gracza (tylko odczyt) i logika stanu."""
    import logika_stanu as LS
    _, Ds = EJ.DANE_STANU.dane_z_przypadkami()
    return Ds, LS


def opis_z_petem(Ds, LS, klasa, L, mod):
    """Bohater dla silnika z modyfikatorem peta (jak Sygnaly/Modyfikatory) — mod None = bez peta."""
    import symulacja_lasu as SL
    opis = getattr(SL, "_bohater_bez_peta", SL.bohater)(Ds, klasa, L)   # część 2 podmienia SL.bohater
    if not mod:
        return opis
    czysty, powod = LS.czysty_modyfikator(Ds, mod)
    if czysty is None:
        raise ValueError("modyfikator peta odrzucony przez stan gracza: %s (%s)" % (powod, mod))
    return LS.opis_z_modyfikatorami(Ds, opis, LS.zloz_modyfikatory(Ds, [czysty]))


def szansa(Ds, LS, klasa, L, mod, potwor, poziom, ziaren):
    import silnik
    opis = opis_z_petem(Ds, LS, klasa, L, mod)
    wyg = sum(silnik.symuluj(opis, {"potwor": potwor, "poziom": poziom}, z)["wynik"] == "wygrana"
              for z in range(1, ziaren + 1))
    return 100.0 * wyg / ziaren


def mody(D):
    """[(etykieta, pet | None, mod | None)] — „bez peta” i każdy pet z danych (mod = LogikaPetow.mod_peta)."""
    w = [("bez peta", None, None)]
    for p in D["pety"]:
        w.append((p["nazwa"], p, LP.mod_peta(D, p["id"])))
    return w


def czesc1(D, ziaren):
    EJ.zaladuj_przeciwnikow()
    Ds, LS = stan()
    wynik = {}
    for etykieta, p, mod in mody(D):
        wiersz = {}
        for potwor, Lp, _n in STRAZNICY:
            for klasa in Ds["klasy"]:
                for Lg in (Lp - 1, Lp):
                    wiersz[(potwor, klasa, Lg)] = szansa(Ds, LS, klasa, Lg, mod, potwor, Lp, ziaren)
        wynik[etykieta] = wiersz
    return wynik, Ds


def czesc2(D, graczy, ziarno=1):
    """Minuty do wygranej ze strażnikiem lasu i Bagna (mediana) dla każdego peta; ten sam los dla każdego wariantu."""
    import symulacja_lasu as SL
    EJ.zaladuj_przeciwnikow()
    Ds, LS = stan()
    P, Pb, Pd = SL.przegrody(), EJ.przegrody_bagna(), EJ.przegrody_dzungli()
    x0, przelot = SL.przybycie_i_przelot()
    xb, przelot_b = EJ.przybycie_i_przelot_bagna()
    xd, przelot_d = EJ.przybycie_i_przelot_dzungli()
    stary = SL.bohater
    SL._bohater_bez_peta = stary
    wynik = {}
    try:
        for etykieta, p, mod in mody(D):
            SL.bohater = (lambda Dd, k, L, _m=mod: opis_z_petem(Ds, LS, k, L, _m))
            premia = (mod or {}).get("lup")
            las, bagno, dzungla, zl_las, zl_bag, zl_dz = [], [], [], [], [], []
            for k in Ds["klasy"]:
                los = random.Random("skille-%s-%d" % (k, ziarno))
                for _ in range(graczy):
                    st = {}
                    o, w = EJ.gracz(Ds, P, k, los, x0, przelot, po_strazniku=False, limit_min=SL.LIMIT_MIN, koniec=st,
                                    premia=premia)
                    if w is None:
                        continue
                    las.append(w / 60.0)
                    zl_las.append(o[-1][1] / (w / 60.0))
                    st2 = {}
                    ob, wb = EJ.gracz(Ds, Pb, k, los, xb, przelot_b, po_strazniku=False, L0=st["L"], xp0=st["xp"],
                                      troll=EJ.TROLL_BAGNA, dojscie=EJ.DOJSCIE_BAGNA, limit_min=EJ.LIMIT_BAGNA_MIN,
                                      premia=premia, koniec=st2)
                    if wb is None:
                        continue
                    bagno.append(wb / 60.0)
                    zl_bag.append(ob[-1][1] / (wb / 60.0))
                    od, wd = EJ.gracz(Ds, Pd, k, los, xd, przelot_d, po_strazniku=False, L0=st2["L"], xp0=st2["xp"],
                                      troll=EJ.TROLL_DZUNGLI, dojscie=EJ.DOJSCIE_DZUNGLI, limit_min=EJ.LIMIT_DZUNGLI_MIN,
                                      premia=premia)
                    if wd is not None:
                        dzungla.append(wd / 60.0)
                        zl_dz.append(od[-1][1] / (wd / 60.0))
            med = (lambda xs: statistics.median(xs) if xs else None)
            wynik[etykieta] = (med(las), med(bagno), len(bagno), 3 * graczy, med(zl_las), med(zl_bag), med(dzungla),
                               len(dzungla), med(zl_dz))
    finally:
        SL.bohater = stary
    return wynik


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Wpływ skilli petów na walki (silnik walki)")
    ap.add_argument("--ziaren", type=int, default=300)
    ap.add_argument("--graczy", type=int, default=15, help="graczy na klasę w części 2")
    ap.add_argument("--bez-przejscia", action="store_true")
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    t0 = time.time()
    D = DP.podstawa()
    T, Ds = czesc1(D, a.ziaren)
    klasy = Ds["klasy"]

    def f(x):
        return "—" if x is None else ("%.0f" % x)

    def f1(x):
        return "—" if x is None else ("%.1f" % x).replace(".", ",")
    w = ["## Skille petów (D-101) a walki — propozycja liczb (nie kanon)", "",
         "Szansa wygranej (%%, %d ziaren) ze strażnikiem: gracz na poziomie strażnika / o jeden niżej. W nawiasie zmiana "
         "względem walki bez peta (pp)." % a.ziaren, ""]
    for potwor, Lp, nazwa in STRAZNICY:
        w.append("### %s (poziom %d)" % (nazwa, Lp))
        w.append("")
        w.append("| Pet | Skill | " + " | ".join("%s %d / %d" % (k, Lp, Lp - 1) for k in klasy) + " |")
        w.append("|---|---|" + "---|" * len(klasy))
        baza = T["bez peta"]
        for etykieta, p, _m in mody(D):
            kom = []
            for k in klasy:
                v1, v0 = T[etykieta][(potwor, k, Lp)], T[etykieta][(potwor, k, Lp - 1)]
                if p is None:
                    kom.append("%s / %s" % (f(v1), f(v0)))
                else:
                    d1, d0 = v1 - baza[(potwor, k, Lp)], v0 - baza[(potwor, k, Lp - 1)]
                    kom.append("%s (%+.0f) / %s (%+.0f)" % (f(v1), d1, f(v0), d0))
            w.append("| %s | %s | %s |" % (etykieta, LP.opis_skilla(D, p) if p else "—", " | ".join(kom)))
        w.append("")
    if not a.bez_przejscia:
        C = czesc2(D, a.graczy)
        w.append("### Przejście: minuty do wygranej ze strażnikiem (mediana, %d graczy na klasę) i dochód" % a.graczy)
        w.append("")
        w.append("| Pet | Las: min do Strażnika Gaju | Bagno: min do Strażnika Topieli | Dżungla: min do Węża Stu Lian | "
                 "Złoto/min las | Złoto/min Bagno | Złoto/min Dżungla |")
        w.append("|---|---|---|---|---|---|---|")
        b = C["bez peta"]
        for etykieta, p, mod in mody(D):
            las, bag, n, wszy, zl, zb, dz, nd, zd = C[etykieta]

            def zm(v, v0, fmt=" (%+.1f)"):
                return "" if p is None or v is None or v0 is None else (fmt % (v - v0)).replace(".", ",")
            w.append("| %s | %s%s | %s%s%s | %s%s%s | %s%s | %s%s | %s%s |" % (
                etykieta, f1(las), zm(las, b[0]), f1(bag), zm(bag, b[1]), "" if n == wszy else " · %d z %d" % (n, wszy),
                f1(dz), zm(dz, b[6]), "" if nd == n else " · %d z %d" % (nd, n),
                f(zl), zm(zl, b[4], " (%+.0f)"), f(zb), zm(zb, b[5], " (%+.0f)"), f(zd), zm(zd, b[8], " (%+.0f)")))
        w.append("")
    w.append("_python -B swiat/pety_proba/skille_petow.py --ziaren %d --graczy %d (%.0f s)_" % (a.ziaren, a.graczy,
                                                                                            time.time() - t0))
    tekst = "\n".join(w) + "\n"
    print(tekst)
    if a.md:
        with open(a.md, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(tekst)


if __name__ == "__main__":
    main()
