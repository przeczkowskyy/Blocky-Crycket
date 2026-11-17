#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiedy gracz kupi jajko — Złoto z walk w lesie-pasie albo w Bagnie przy dzisiejszym łupie. Propozycja, NIE kanon.

    python -B swiat/pety_proba/ekonomia_jajek.py                 # las: warianty ceny × 1.–5. jajko (Markdown)
    python -B swiat/pety_proba/ekonomia_jajek.py --biom bagno    # Bagno: gracz po lesie (do Strażnika Gaju) w Bagnie
    python -B swiat/pety_proba/ekonomia_jajek.py --graczy 200 --md wynik.md

Bagno (17.11 wieczór): gracz przechodzi las jak niżej do wygranej ze Strażnikiem Gaju, z tym poziomem i doświadczeniem
wchodzi do Bagna (przegrody swiat/bagno_pas_gra/zrodla/DanePotworowBagna.luau, przeciwnicy Bagna z przeciwnicy.py
dopisani do silnika w pamięci, Ropucha z Chatką jak Leśny Troll); liczy się tylko Złoto z Bagna (licznik ceny jajka
Bagna jest osobny — zakupy w lesie go nie podnoszą).

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


def gracz(D, P, klasa, los, x0, przelot, po_strazniku=True, limit_min=LIMIT_MIN, L0=1, xp0=0, troll="lesny_troll",
          dojscie=None, koniec=None):
    """Jeden gracz: lista (czas s, Złoto łącznie z walk) po każdej walce + wynik jak symulacja_lasu.jeden_gracz
    (czas wygranej ze Strażnikiem albo None). Ta sama kolejność losowań co tam. Bagno: L0, xp0 = poziom
    i doświadczenie z lasu, troll = rzadki potwór z odrodzeniem, dojscie = sekundy dojścia per gatunek;
    koniec (słownik) dostaje L i xp w chwili końca pętli (po wygranej ze Strażnikiem, gdy po_strazniku=False)."""
    dojscie = dojscie or SL.DOJSCIE
    L, xp, czas = L0, xp0, przelot + abs(P[0]["x"] - x0) / SL.PREDKOSC
    i = 0
    z_rzedu = farma = 0
    troll_od = 0.0
    zloto = 0
    os_czasu = []
    wygrana_straznika = None
    while czas <= limit_min * 60:
        p = P[i]
        cel = p
        if p["gatunek"] == troll and czas < troll_od:
            cel = P[i - 1]
        hi = cel["do"] if cel["straznik"] else max(cel["od"], min(cel["do"], L + 1))
        pz = los.randint(cel["od"], hi)
        r = silnik.symuluj(SL.bohater(D, klasa, L), {"potwor": cel["gatunek"], "poziom": pz}, los.randrange(1, 2 ** 31 - 1))
        czas += r["czas"] + SL.EKRAN_WYNIKU + dojscie[cel["gatunek"]]
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
            if cel is p and p["gatunek"] == troll:
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
    if koniec is not None:
        koniec.update(L=L, xp=xp, czas=czas)
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


def jajek_do(os_czasu, wariant, t_konca):
    """Ile jajek gracz kupi do chwili t_konca (s) — np. do wygranej ze Strażnikiem biomu."""
    return sum(1 for t in zakupy(os_czasu, wariant, 1000) if t is not None and t <= t_konca)


def wszyscy_gracze(graczy, ziarno=1, z_wygrana=False):
    """Lista os_czasu graczy lasu; z_wygrana=True: pary (os_czasu, czas wygranej ze Strażnikiem Gaju albo None)."""
    _, D = DANE_STANU.dane_z_przypadkami()
    P = SL.przegrody()
    x0, przelot = SL.przybycie_i_przelot()
    w = []
    for k in D["klasy"]:
        los = random.Random("jajka-%s-%d" % (k, ziarno))
        for _ in range(graczy):
            os_czasu, wygrana = gracz(D, P, k, los, x0, przelot)
            w.append((os_czasu, wygrana) if z_wygrana else os_czasu)
    return w


# ------------------------------------------------------------------------------------------------ Bagno
BAGNO = os.path.join(REPO, "swiat", "bagno_pas_gra")
PLIK_PRZEGROD_BAGNA = os.path.join(BAGNO, "zrodla", "DanePotworowBagna.luau")
PLIK_BAGNA = os.path.join(BAGNO, "zrodla", "DaneBagna.luau")
TROLL_BAGNA = "ropucha_z_chatka"     # rzadki potwór Bagna z odrodzeniem (jak Leśny Troll)
# s między walkami: jak u odpowiednika w lesie (przeciwnicy.py — baza gatunku; Strażnik stoi)
DOJSCIE_BAGNA = {"rechotek": 10, "bulgotnik": 10, "klodoklap": 10, "ropucha_z_chatka": 15, "straznik_topieli": 6}
LIMIT_BAGNA_MIN = 120.0   # przejście Bagna trwa dłużej niż lasu (mediana ok. 46 min, część graczy > 60 min)


def przegrody_bagna():
    d = SL.wczytaj_luau(PLIK_PRZEGROD_BAGNA)
    return [{"id": s["id"], "gatunek": s["gatunek"], "od": s["poziomy"][0], "do": s["poziomy"][1], "x": s["srodek"][0],
             "straznik": s["straznik"] is True, "odrodzenie": s["odrodzenieS"],
             "stale": s.get("odrodzenieStale") is True, "naraz": s["naraz"]} for s in d["strefy"]]


def przybycie_i_przelot_bagna():
    d = SL.wczytaj_luau(PLIK_BAGNA)
    return d["przybycie"]["punkt"][0], d["przelot"]["czas"]


def wszyscy_gracze_bagna(graczy, ziarno=1, z_wygrana=False):
    """Gracz przechodzi las do wygranej ze Strażnikiem Gaju (poziom i doświadczenie z tej pętli), potem wchodzi do Bagna:
    lista (czas od wejścia do Bagna, Złoto z walk w Bagnie) — Złoto z lasu NIE wchodzi (dolna granica tempa);
    z_wygrana=True: pary (os_czasu, czas wygranej ze Strażnikiem Topieli od wejścia do Bagna albo None)."""
    if BAGNO not in sys.path:
        sys.path.insert(0, BAGNO)
    import przeciwnicy  # noqa: E402  (swiat/bagno_pas_gra/przeciwnicy.py — tylko odczyt, przeciwnicy w pamięci silnika)
    przeciwnicy.zaladuj_do_silnika(silnik)
    _, D = DANE_STANU.dane_z_przypadkami()
    P, Pb = SL.przegrody(), przegrody_bagna()
    x0, przelot = SL.przybycie_i_przelot()
    xb, przelot_b = przybycie_i_przelot_bagna()
    w, poziomy = [], []
    for k in D["klasy"]:
        los = random.Random("jajka-bagno-%s-%d" % (k, ziarno))
        for _ in range(graczy):
            stan = {}
            _os, wygrana = gracz(D, P, k, los, x0, przelot, po_strazniku=False, limit_min=SL.LIMIT_MIN, koniec=stan)
            if wygrana is None:
                continue
            poziomy.append(stan["L"])
            os_czasu, wygrana_b = gracz(D, Pb, k, los, xb, przelot_b, L0=stan["L"], xp0=stan["xp"], troll=TROLL_BAGNA,
                                        dojscie=DOJSCIE_BAGNA, limit_min=LIMIT_BAGNA_MIN)
            w.append((os_czasu, wygrana_b) if z_wygrana else os_czasu)
    return w, poziomy


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
    ap = argparse.ArgumentParser(description="Kiedy gracz kupi jajko (Złoto z lasu-pasa albo z Bagna)")
    ap.add_argument("--graczy", type=int, default=100, help="graczy na klasę")
    ap.add_argument("--ziarno", type=int, default=1)
    ap.add_argument("--biom", choices=("las", "bagno"), default="las")
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    t0 = time.time()
    import json
    with open(os.path.join(TU, "ustawienia.json"), encoding="utf-8") as f:
        U = json.load(f)
    j = next(x for x in U["jajka"] if x["kraina"] == a.biom)
    c = j["cena"]
    # pierwszy wariant = tryb z ustawień (od 17.11 stała cena — decyzja Karola), potem przełączniki do porównania
    stala = {"tryb": "stala", "cena": c["stala"]}
    rosnaca = {"tryb": "rosnaca", "start": c["start"], "krok": c["krok"], "maks": c["maks"]}
    warianty = [("stała %d%s" % (c["stala"], " (decyzja 17.11)" if c["tryb"] == "stala" else ""), stala),
                ("rosnąca %d +%d do %d%s" % (c["start"], c["krok"], c["maks"],
                                             " (ustawienia)" if c["tryb"] == "rosnaca" else " (przełącznik)"), rosnaca)]
    if c.get("kalkulator"):
        warianty.append(("kalkulator: stała %d" % c["kalkulator"], {"tryb": "stala", "cena": c["kalkulator"]}))
    for wariant in c.get("porownanie", []):
        warianty.append(("rosnąca %d +%d do %d" % (wariant["start"], wariant["krok"], wariant["maks"]),
                         dict(wariant, tryb="rosnaca")))
    if a.biom == "las":
        pary = wszyscy_gracze(a.graczy, a.ziarno, z_wygrana=True)
        opis = ("Złoto z walk w lesie-pasie, gracz jak w `swiat/stan_gracza/symulacja_lasu.py` (%d graczy na klasę, trzy "
                "klasy); po Strażniku walczy dalej w przegrodzie przed nim. Minuty od wejścia do lasu: mediana "
                "(10%%–90%% graczy)." % a.graczy)
    else:
        pary, poziomy = wszyscy_gracze_bagna(a.graczy, a.ziarno, z_wygrana=True)
        poziomy.sort()
        opis = ("Złoto z walk w Bagnie (swiat/bagno_pas_gra: przegrody, przeciwnicy.py w silniku), gracz jak w lesie: "
                "przechodzi las do wygranej ze Strażnikiem Gaju (wchodzi do Bagna na poziomie %d, 10%%–90%%: %d–%d), "
                "potem Bagno; Złoto z lasu nie wchodzi. %d graczy (trzy klasy). Minuty od wejścia do Bagna: mediana "
                "(10%%–90%% graczy)." % (statistics.median(poziomy), SL.kwantyl(poziomy, 0.1), SL.kwantyl(poziomy, 0.9),
                                         len(pary)))
    gracze = [o for o, _w in pary]
    T = tabela(gracze, warianty)

    def f(x):
        return "—" if x is None else ("%.1f" % x).replace(".", ",")
    w = ["## Kiedy gracz kupi %s — propozycja liczb (nie kanon)" % j["nazwa"].lower(), "", opis, "",
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
    # ile jajek do wygranej ze Strażnikiem biomu (las: od wejścia do lasu; Bagno: od wejścia do Bagna)
    wygrane = [(o, t) for o, t in pary if t is not None]
    straznik = "Strażnikiem Gaju" if a.biom == "las" else "Strażnikiem Topieli"
    if wygrane:
        czasy = sorted(t / 60.0 for _o, t in wygrane)
        w.append("")
        w.append("Do wygranej ze %s (mediana %s min, 10–90%%: %s–%s; %d z %d graczy wygrało w limicie):" % (
            straznik, f(statistics.median(czasy)), f(SL.kwantyl(czasy, 0.1)), f(SL.kwantyl(czasy, 0.9)), len(wygrane),
            len(pary)))
        for nazwa, wariant in warianty:
            ile = sorted(jajek_do(o, wariant, t) for o, t in wygrane)
            w.append("- %s: %s jajek (10–90%%: %s–%s)" % (nazwa, f(statistics.median(ile)), f(SL.kwantyl(ile, 0.1)),
                                                         f(SL.kwantyl(ile, 0.9))))
    w.append("")
    w.append("_python -B swiat/pety_proba/ekonomia_jajek.py --biom %s --graczy %d --ziarno %d (%.0f s)_" % (
        a.biom, a.graczy, a.ziarno, time.time() - t0))
    tekst = "\n".join(w) + "\n"
    print(tekst)
    if a.md:
        with open(a.md, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(tekst)


if __name__ == "__main__":
    main()
