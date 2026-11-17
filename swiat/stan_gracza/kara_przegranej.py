#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ile Złota zabierać za przegraną (propozycja D-098, sesja główna 17.11.2026, temat 3). Propozycja liczb, NIE kanon.

    python -B swiat/stan_gracza/kara_przegranej.py                 # las i Bagno, Markdown na ekran
    python -B swiat/stan_gracza/kara_przegranej.py --graczy 100 --md wynik.md

Gracze i walki: swiat/pety_proba/ekonomia_jajek.py (tylko uruchamiany — ta sama polityka co
swiat/stan_gracza/symulacja_lasu.py, przegrody z plików pasów, łup z silnika tools/walka/silnik.py; gracz kupuje
jajko od razu, gdy Złota wystarcza; ceny jajek z swiat/pety_proba/ustawienia.json). Każdą walkę zapisuje opakowanie
silnik.symuluj w TYM procesie (plik pakietu petów zostaje bez zmian). Kara nie zmienia przebiegu walk (polityka
gracza nie zależy od Złota), więc warianty liczy się na tych samych walkach:
  • Złoto po walce: + łup za wygraną, − kara za przegraną (od Złota w tej chwili, nigdy poniżej zera), potem zakup
    jajka, gdy Złota wystarcza („kupujący”); drugi gracz nie kupuje nic („oszczędzający” — najgorszy przypadek kary
    od posiadanego Złota);
  • „tuż przed zakupem” = przegrana, gdy kupujący ma już ≥ 80% ceny jajka; „walk do odrobienia” = kara ÷ łup
    zwykłego potwora na poziomie gracza (logika_stanu.lup_zwyklego);
  • las liczony od wejścia do wygranej ze Strażnikiem Gaju; Bagno — od wejścia do Bagna (po Strażniku Gaju) przez
    LIMIT_MIN ekonomii jajek, Złoto z lasu nie wchodzi (jak w ekonomii jajek).
Doświadczenie za przegraną: dziś 20% (silnik, udzial_doswiadczenia_przy_przegranej) — tabela porównuje XP na minutę
z celowej przegranej ze Strażnikiem z wygranymi w przegrodzie przed nim (pytanie 54).
"""
import argparse
import json
import os
import random
import statistics
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
PETY = os.path.join(REPO, "swiat", "pety_proba")
for _s in (TU, os.path.join(REPO, "tools", "walka"), PETY):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import dane as DANE  # noqa: E402
import logika_stanu as LS  # noqa: E402
import silnik  # noqa: E402
import symulacja_lasu as SL  # noqa: E402
import ekonomia_jajek as EJ  # noqa: E402  (swiat/pety_proba — tylko odczyt)

PRZED_ZAKUPEM = 0.8

# warianty: (nazwa, {tryb, …}) — tryb "procent" (procent, limit = "zwykly" | None) albo "stala" (udzial łupu zwykłego
# potwora na poziomie przeciwnika)
WARIANTY = [
    ("bez kary", {"tryb": "procent", "procent": 0.0, "limit": None}),
    ("2% Złota", {"tryb": "procent", "procent": 0.02, "limit": None}),
    ("5% Złota", {"tryb": "procent", "procent": 0.05, "limit": None}),
    ("10% Złota", {"tryb": "procent", "procent": 0.10, "limit": None}),
    ("5%, najwyżej 1 wygrana", {"tryb": "procent", "procent": 0.05, "limit": "zwykly"}),
    ("10%, najwyżej 1 wygrana", {"tryb": "procent", "procent": 0.10, "limit": "zwykly"}),
    ("stała: ½ wygranej", {"tryb": "stala", "udzial": 0.5}),
]


def kara(D, wariant, zloto, poziom_potwora):
    """Kara w Złocie dla wariantu; wariant procentowy z limitem = logika_stanu.kara_przegranej (to wdrażamy)."""
    if wariant["tryb"] == "procent":
        if wariant["limit"] == "zwykly":
            return LS.kara_przegranej(D, zloto, poziom_potwora, wariant["procent"])
        return min(zloto, int(zloto * wariant["procent"]))
    return min(zloto, int(LS.lup_zwyklego(D, poziom_potwora) * wariant["udzial"]))


# ------------------------------------------------------------------------------------------------ walki graczy
ZAPIS = []
_SYMULUJ = silnik.symuluj


def _symuluj(bohater, przeciwnik, ziarno):
    r = _SYMULUJ(bohater, przeciwnik, ziarno)
    ZAPIS.append({"gatunek": przeciwnik["potwor"], "pz": przeciwnik["poziom"], "L": bohater["poziom"],
                  "wygrana": r["wynik"] == "wygrana", "zloto": r["lup"]["zloto"], "xp": r["lup"]["doswiadczenie"],
                  "czas_walki": r["czas"]})
    return r


def walki_gracza(fn, *argi, **kw):
    """Wywołuje EJ.gracz z zapisem walk → (walki z czasem t po walce, czas wygranej ze Strażnikiem albo None)."""
    ZAPIS.clear()
    os_czasu, wygrana = fn(*argi, **kw)
    if len(os_czasu) != len(ZAPIS):
        raise RuntimeError("zapis walk nie zgadza się z ekonomią jajek")
    w = []
    for (t, _z), f in zip(os_czasu, ZAPIS):
        w.append(dict(f, t=t))
    return w, wygrana


def gracze_lasu(D, graczy, ziarno):
    P = SL.przegrody()
    x0, przelot = SL.przybycie_i_przelot()
    w = []
    for k in D["klasy"]:
        los = random.Random("jajka-%s-%d" % (k, ziarno))  # te same ziarna co ekonomia_jajek.wszyscy_gracze
        for _ in range(graczy):
            walki, wygrana = walki_gracza(EJ.gracz, D, P, k, los, x0, przelot)
            if wygrana is not None:
                w.append((k, [f for f in walki if f["t"] <= wygrana], wygrana))
    return w


def gracze_bagna(D, graczy, ziarno):
    if EJ.BAGNO not in sys.path:
        sys.path.insert(0, EJ.BAGNO)
    import przeciwnicy  # noqa: E402  (swiat/bagno_pas_gra — tylko odczyt)
    przeciwnicy.zaladuj_do_silnika(silnik)
    P, Pb = SL.przegrody(), EJ.przegrody_bagna()
    x0, przelot = SL.przybycie_i_przelot()
    xb, przelot_b = EJ.przybycie_i_przelot_bagna()
    w = []
    for k in D["klasy"]:
        los = random.Random("jajka-bagno-%s-%d" % (k, ziarno))  # jak ekonomia_jajek.wszyscy_gracze_bagna
        for _ in range(graczy):
            stan = {}
            _w, wygrana = walki_gracza(EJ.gracz, D, P, k, los, x0, przelot, po_strazniku=False, limit_min=SL.LIMIT_MIN,
                                       koniec=stan)
            if wygrana is None:
                continue
            walki, wyg_b = walki_gracza(EJ.gracz, D, Pb, k, los, xb, przelot_b, L0=stan["L"], xp0=stan["xp"],
                                        troll=EJ.TROLL_BAGNA, dojscie=EJ.DOJSCIE_BAGNA)
            w.append((k, walki, wyg_b))
    return w


# ------------------------------------------------------------------------------------------------ jeden wariant
def przebieg(D, walki, wariant, cena, kupuje):
    z, kupione, straty, przed_zakupem = 0, [], [], []
    for f in walki:
        if f["wygrana"]:
            z = min(z + f["zloto"], D["limity"]["waluta_maks"])
        else:
            k = kara(D, wariant, z, f["pz"])
            if kupuje and cena and z >= PRZED_ZAKUPEM * cena:
                przed_zakupem.append((k, k / max(1, LS.lup_zwyklego(D, f["L"]))))
            straty.append(k)
            z -= k
        while kupuje and z >= cena:
            z -= cena
            kupione.append(f["t"])
    return {"straty": straty, "kupione": kupione, "zloto": z, "przed_zakupem": przed_zakupem}


def med(xs):
    return statistics.median(xs) if xs else 0


def f1(x):
    return ("%.1f" % x).replace(".", ",")


def f0(x):
    return "%.0f" % x


def tabela(D, gracze, cena, opis_konca):
    w = ["| Wariant | Kara za 1 przegraną (kupujący: mediana / maks.) | Razem %s (mediana / 90%%) | "
         "1. jajko (min, mediana) | Przesunięcie 1. jajka | Tuż przed zakupem: kara (walk do odrobienia) | "
         "Oszczędzający: razem / największa |" % opis_konca,
         "|---|---|---|---:|---:|---|---|"]
    baza = {}
    for nazwa, wariant in WARIANTY:
        jedna, razem, pierwsze, przes, przed, osz_razem, osz_maks = [], [], [], [], [], [], []
        for i, (_k, walki, _wyg) in enumerate(gracze):
            r = przebieg(D, walki, wariant, cena, True)
            o = przebieg(D, walki, wariant, cena, False)
            jedna += r["straty"]
            razem.append(sum(r["straty"]))
            t1 = r["kupione"][0] / 60 if r["kupione"] else None
            if nazwa == "bez kary":
                baza[i] = t1
            if t1 is not None:
                pierwsze.append(t1)
                if baza.get(i) is not None:
                    przes.append(t1 - baza[i])
            przed += r["przed_zakupem"]
            osz_razem.append(sum(o["straty"]))
            osz_maks.append(max(o["straty"]) if o["straty"] else 0)
        w.append("| %s | %s / %s | %s / %s | %s | +%s min (90%%: %s) | %s | %s / %s |" % (
            nazwa, f0(med(jedna)), f0(max(jedna) if jedna else 0), f0(med(razem)), f0(SL.kwantyl(razem, 0.9)),
            f1(med(pierwsze)), f1(med(przes) if przes else 0), f1(SL.kwantyl(przes, 0.9) if przes else 0),
            ("%s Złota (%s), %d przegranych" % (f0(med([k for k, _ in przed])), f1(med([x for _, x in przed])), len(przed))
             if przed else "—"),
            f0(med(osz_razem)), f0(max(osz_maks) if osz_maks else 0)))
    return w


def statystyki_przegranych(gracze):
    n = [sum(1 for f in walki if not f["wygrana"]) for _k, walki, _w in gracze]
    wszystkie = [len(walki) for _k, walki, _w in gracze]
    xp_przeg = [sum(f["xp"] for f in walki if not f["wygrana"]) for _k, walki, _w in gracze]
    xp_all = [sum(f["xp"] for f in walki) for _k, walki, _w in gracze]
    straznik = [sum(1 for f in walki if not f["wygrana"] and f["gatunek"].startswith("straznik")) for _k, walki, _w in gracze]
    return {"przegrane": med(n), "przegrane90": SL.kwantyl(n, 0.9), "walk": med(wszystkie),
            "bez": 100.0 * sum(1 for x in n if x == 0) / len(n), "udzial_xp": 100.0 * sum(xp_przeg) / max(1, sum(xp_all)),
            "u_straznika": med(straznik)}


def xp_na_minute(gracze, dojscie):
    """XP/min: przegrane ze Strażnikiem vs wygrane z ostatnią przegrodą przed nim (ten sam gracz, ten sam poziom ±1)."""
    przeg, wyg = [], []
    for _k, walki, _w in gracze:
        for f in walki:
            s = f["czas_walki"] + SL.EKRAN_WYNIKU + dojscie.get(f["gatunek"], 10)
            if f["gatunek"].startswith("straznik") and not f["wygrana"]:
                przeg.append((f["xp"], s))
            elif not f["gatunek"].startswith("straznik") and f["wygrana"] and f["L"] >= 9:
                wyg.append((f["xp"], s))

    def tempo(lista):
        return 60.0 * sum(x for x, _ in lista) / max(1e-9, sum(s for _, s in lista)) if lista else 0
    return tempo(przeg), tempo(wyg), len(przeg), len(wyg)


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Kara za przegraną: warianty na walkach z ekonomii jajek")
    ap.add_argument("--graczy", type=int, default=100, help="graczy na klasę")
    ap.add_argument("--ziarno", type=int, default=1)
    ap.add_argument("--md", default=None)
    ap.add_argument("--profil", choices=("wzorcowy", "pawla"), default="wzorcowy",
                    help="rozkłady klas: wzorcowe albo z src/shared/ClassData.luau (to, co dziś czyta gra; pytanie 56)")
    a = ap.parse_args()
    t0 = time.time()
    _, D = DANE.dane_z_przypadkami()
    if a.profil == "pawla":
        import porownaj_profile  # noqa: E402
        D = dict(D, rozklady=porownaj_profile.rozklady_pawla(D))
    with open(os.path.join(PETY, "ustawienia.json"), encoding="utf-8") as fh:
        U = json.load(fh)
    cena = {j["kraina"]: j["cena"]["stala"] for j in U["jajka"]}
    silnik.symuluj = _symuluj
    try:
        las = gracze_lasu(D, a.graczy, a.ziarno)
        bagno = gracze_bagna(D, a.graczy, a.ziarno)
    finally:
        silnik.symuluj = _SYMULUJ
    w = ["## Kara za przegraną — propozycja liczb (nie kanon, D-098), profil klas: %s" % a.profil, ""]
    for nazwa, gracze, c, koniec, dojscie in (
            ("Las (do wygranej ze Strażnikiem Gaju)", las, cena["las"], "w lesie", SL.DOJSCIE),
            ("Bagno (%d min od wejścia)" % EJ.LIMIT_MIN, bagno, cena["bagno"], "w Bagnie", EJ.DOJSCIE_BAGNA)):
        s = statystyki_przegranych(gracze)
        w.append("### %s — %d graczy, jajko %d Złota" % (nazwa, len(gracze), c))
        w.append("")
        w.append("Walk: mediana %s; przegranych: mediana %s (90%% graczy ≤ %s), bez żadnej %s%%, ze Strażnikiem %s; "
                 "doświadczenie z przegranych to %s%% całego." % (f0(s["walk"]), f0(s["przegrane"]), f0(s["przegrane90"]),
                                                                 f0(s["bez"]), f0(s["u_straznika"]), f1(s["udzial_xp"])))
        xp_p, xp_w, n_p, n_w = xp_na_minute(gracze, dojscie)
        w.append("XP na minutę: celowa przegrana ze Strażnikiem %s (%d walk), wygrane od 9. poziomu w przegrodach %s "
                 "(%d walk)." % (f0(xp_p), n_p, f0(xp_w), n_w))
        w.append("")
        w += tabela(D, gracze, c, koniec)
        w.append("")
    w.append("_python -B swiat/stan_gracza/kara_przegranej.py --graczy %d --ziarno %d --profil %s (%.0f s)_" % (
        a.graczy, a.ziarno, a.profil, time.time() - t0))
    tekst = "\n".join(w) + "\n"
    print(tekst)
    if a.md:
        with open(a.md, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(tekst)


if __name__ == "__main__":
    main()
