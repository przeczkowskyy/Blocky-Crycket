#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tabela balansu silnika walki v3 — ma WYKAZAC, ze klasy i buildy sa rowne, a nie pokazac, kto kogo kontruje.

    python -B tools/walka/balans.py                       # 2000 ziaren, poziomy 1-10, 12, 15, 20 (kilka minut)
    python -B tools/walka/balans.py --ziaren 500          # szybciej, mniej dokladnie
    python -B tools/walka/balans.py --start 50001         # inne ziarna (kontrola dopasowania do ziaren 1..N)
    python -B tools/walka/balans.py --md wynik.md         # zapisz tabele Markdown do pliku
    python -B tools/walka/balans.py --czesci a,b,c        # tylko wybrane czesci (a..l, opis nizej)
    python -B tools/walka/balans.py --procesy 1           # bez rownoleglosci (domyslnie 3 procesy)

Kazda para liczy sie na TYCH SAMYCH ziarnach start..start+N-1, wiec porownywane strony graja te same losowania.
Postacie wzorcowe i buildy: tools/walka/wzorcowe.py. Opis zasad: tools/walka/ZMIANY_SESJA_1611.md.

  (a) klasa przeciw kazdemu potworowi lasu: roznica klas (cel <= 5 pp, granica 7 pp) i szczegoly na wybranych poziomach;
  (b) klasa na klase (cel 45-55%, oba miejsca: gracz i przeciwnik);
  (c) ile procent wygranych daje PUNKT kazdej statystyki kazdej klasie (+20% puli w jedna statystyke);
  (d) ile razy w walce pada umiejetnosc: postac wzorcowa i build pod mane (pierwsze uzycie: ktora wlasna akcja);
  (e) buildy: kazdy z postacia wzorcowa swojej klasy (cel 45-55%) i z kazdym potworem wzgledem wzorcowej;
  (f) blok: wariant 25% i 0% ciosu przez blok (roznica klas, pojedynki, ile daje tarcza);
  (g) sloty: 3 aktywne / mieszanki / 3 pasywne (czy pasywka jest warta tyle co aktywna);
  (h) nabijanie jednej statystyki kontra rozklad wzorcowy;
  (i) wysokie poziomy (30-100): roznica klas, dlugosc walki, uzycia umiejetnosci, nasycenie krzywych;
  (j) Pancerz: limit redukcji i przelicznik klasy;
  (k) wskrzeszenie (propozycja D-094) w slocie zamiast zwyklej umiejetnosci: ile jest warte przy roznym zyciu po powrocie;
  (l) przeszukanie WSZYSTKICH zestawow slotow kontra wzorcowa (zaden darmowy wybor slotow nie moze wyraznie dominowac).
"""
import argparse
import os
import statistics
import sys
import time
from multiprocessing import Pool

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import silnik  # noqa: E402
import wzorcowe  # noqa: E402

KLASY = wzorcowe.KLASY
NAZWY = {k: silnik.KLASY[k]["nazwa"] for k in KLASY}
MONSTRY = [p["id"] for p in silnik.PRZECIWNICY_LISTA]
NAZWY_M = {p["id"]: p["nazwa"] for p in silnik.PRZECIWNICY_LISTA}
RANGI = {"zwykly": "zwykły", "rzadki": "rzadki", "straznik": "strażnik"}
NAZWY_STAT = {"sila": "Siła", "kondycja": "Kondycja", "inteligencja": "Inteligencja", "zrecznosc": "Zręczność",
              "szczescie": "Szczęście", "pancerz": "Pancerz"}
CEL_KLAS_PP = 5.0
GRANICA_KLAS_PP = 7.0
CEL_PVP = (45.0, 55.0)


def przeciwnik(nazwa, poziom):
    if nazwa in KLASY:
        return {"postac": wzorcowe.postac(nazwa, poziom)}
    return {"potwor": nazwa, "poziom": poziom}


def seria(gracz, prz, start, n, zmiany=None):
    """Walki na ziarnach start..start+n-1 -> statystyki. zmiany = [(sciezka w silnik.STALE, wartosc)] na czas serii."""
    stare = []
    for k, v in (zmiany or []):
        if k == "wskrzeszenie":  # ulamek zycia po wskrzeszeniu (czesc k)
            stare.append((k, silnik.PASYWNE["wskrzeszenie"]["wskrzeszenie"]))
            silnik.PASYWNE["wskrzeszenie"]["wskrzeszenie"] = v
        else:
            stare.append((k, silnik.STALE[k]))
            silnik.STALE[k] = v
    try:
        wygrane, tury, czasy, uzycia, pierwsze, akcje = 0, [], [], [], [], []
        for z in range(start, start + n):
            w = silnik.symuluj(gracz, prz, z)
            wygrane += w["wynik"] == "wygrana"
            tury.append(w["tury"])
            czasy.append(w["czas"])
            nr, u, pierwsza = 0, 0, 0
            for e in w["dziennik"]:
                if e["kto"] == "gracz" and e["typ"] in ("cios", "krytyk", "blok", "unik", "umiejetnosc"):
                    nr += 1
                    if e["umiejetnosc"]:
                        u += 1
                        if pierwsza == 0:
                            pierwsza = nr
            uzycia.append(u)
            akcje.append(nr)
            if pierwsza:
                pierwsze.append(pierwsza)
    finally:
        for k, v in stare:
            if k == "wskrzeszenie":
                silnik.PASYWNE["wskrzeszenie"]["wskrzeszenie"] = v
            else:
                silnik.STALE[k] = v
    return {"proc": 100.0 * wygrane / n, "tury": tury, "czas": statistics.mean(czasy), "czas_maks": max(czasy),
            "uzycia": statistics.mean(uzycia), "pierwsza": statistics.median(pierwsze) if pierwsze else 0,
            "akcje": statistics.mean(akcje)}


def _zadanie(arg):
    klucz, gracz, prz, start, n, zmiany = arg
    return klucz, seria(gracz, prz, start, n, zmiany)


class Liczydlo:
    def __init__(self, procesy):
        self.pula = Pool(procesy) if procesy > 1 else None

    def licz(self, zadania):
        if self.pula is None:
            return dict(_zadanie(z) for z in zadania)
        return dict(self.pula.map(_zadanie, zadania, chunksize=2))


def pp(x):
    return ("%+.1f" % x).replace(".", ",")


def proc(x):
    return ("%.1f%%" % x).replace(".", ",")


def liczba(x, n=1):
    return ("%.*f" % (n, x)).replace(".", ",")


def obie_strony(wyniki, L, a, b):
    """Wynik klasy a w pojedynku z b, srednio z obu miejsc (a jako gracz i a jako przeciwnik)."""
    return (wyniki[(L, a, b)]["proc"] + 100 - wyniki[(L, b, a)]["proc"]) / 2


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Tabela balansu silnika walki v3")
    ap.add_argument("--ziaren", type=int, default=2000)
    ap.add_argument("--start", type=int, default=1, help="pierwsze ziarno (domyslnie 1, jak w testach)")
    ap.add_argument("--poziomy", default="1,2,3,4,5,6,7,8,9,10,12,15,20")
    ap.add_argument("--szczegoly", default="1,5,10", help="poziomy z pelnymi tabelami (a)")
    ap.add_argument("--czesci", default="a,b,c,d,e,f,g,h,i,j,k,l")
    ap.add_argument("--procesy", type=int, default=3)
    ap.add_argument("--md", default=None, help="zapisz wynik (Markdown) do pliku")
    a = ap.parse_args()
    poziomy = [int(x) for x in a.poziomy.split(",")]
    szczegoly = [L for L in (int(x) for x in a.szczegoly.split(",")) if L in poziomy]
    czesci = set(a.czesci.split(","))
    N, S = a.ziaren, a.start
    nm = max(200, N // 2)        # mniejsze proby w czesciach (c)-(j)
    t0 = time.time()
    L5 = 5 if 5 in poziomy else poziomy[len(poziomy) // 2]
    Lw = [L for L in (5, 10) if L in poziomy] or [L5]
    liczydlo = Liczydlo(a.procesy)
    w = []

    # ---------------------------------------------------------------- (a) i (b)
    wyniki = {}
    if "a" in czesci or "b" in czesci:
        zad = []
        for L in poziomy:
            for k in KLASY:
                g = wzorcowe.postac(k, L)
                for p in MONSTRY + KLASY:
                    zad.append(((L, k, p), g, przeciwnik(p, L), S, N, None))
        wyniki = liczydlo.licz(zad)
        najw, gdzie = 0.0, ""
        pvp_min, pvp_maks = 100.0, 0.0
        for L in poziomy:
            for p in MONSTRY:
                r = [wyniki[(L, k, p)]["proc"] for k in KLASY]
                if max(r) - min(r) > najw:
                    najw, gdzie = max(r) - min(r), "%s, poziom %d" % (NAZWY_M[p], L)
            for k in KLASY:
                for b in KLASY:
                    if k != b:
                        pvp_min = min(pvp_min, wyniki[(L, k, b)]["proc"])
                        pvp_maks = max(pvp_maks, wyniki[(L, k, b)]["proc"])
        ile_w_celu = sum(1 for L in poziomy for p in MONSTRY
                         if max(wyniki[(L, k, p)]["proc"] for k in KLASY) - min(wyniki[(L, k, p)]["proc"] for k in KLASY) <= CEL_KLAS_PP)
        w.append("**Wniosek (a, b):** największa różnica klas przy tym samym potworze %s pp (%s; cel ≤ %s, granica %s); "
                 "w celu %d z %d zestawień. Pojedynki klasa na klasę %s–%s (cel 45–55%%)."
                 % (liczba(najw), gdzie, liczba(CEL_KLAS_PP, 0), liczba(GRANICA_KLAS_PP, 0), ile_w_celu,
                    len(poziomy) * len(MONSTRY), proc(pvp_min), proc(pvp_maks)))
        w.append("")
        w.append("Każda komórka: %d walk na tych samych ziarnach %d–%d. Pula punktów: %d na 1. poziomie + %d za każdy "
                 "kolejny. Sloty umiejętności: 1 (poziom 1–4), 2 (5–9), 3 (od 10). Tura = ruch jednej strony."
                 % (N, S, S + N - 1, wzorcowe.PUNKTY_START, wzorcowe.PUNKTY_NA_POZIOM))
        w.append("")
    if "a" in czesci:
        w.append("### (a) Różnica klas przy tym samym potworze — wszystkie poziomy")
        w.append("")
        w.append("Komórka: największa różnica procentu wygranych między klasami (pp), w nawiasie Wojownik / Zwiadowca / Mag.")
        w.append("")
        w.append("| Poziom | " + " | ".join(NAZWY_M[p] for p in MONSTRY) + " |")
        w.append("|---:|" + "---|" * len(MONSTRY))
        for L in poziomy:
            kom = []
            for p in MONSTRY:
                r = [wyniki[(L, k, p)]["proc"] for k in KLASY]
                kom.append("%s (%s)" % (liczba(max(r) - min(r)), " / ".join("%.0f" % x for x in r)))
            w.append("| %d | %s |" % (L, " | ".join(kom)))
        w.append("")
        w.append("### (a) Klasa przeciw potworom lasu — szczegóły")
        for L in szczegoly:
            w.append("")
            w.append("**Poziom %d** (potwór tego samego poziomu)" % L)
            w.append("")
            w.append("| Przeciwnik | Ranga | " + " | ".join(NAZWY[k] for k in KLASY)
                     + " | Różnica | Tury: najkrótsza–mediana–najdłuższa | Średni czas | Umiejętności na walkę |")
            w.append("|---|---|" + "---:|" * len(KLASY) + "---:|---|---:|---:|")
            for p in MONSTRY:
                r = [wyniki[(L, k, p)]["proc"] for k in KLASY]
                tury = [t for k in KLASY for t in wyniki[(L, k, p)]["tury"]]
                czas = statistics.mean(wyniki[(L, k, p)]["czas"] for k in KLASY)
                uz = statistics.mean(wyniki[(L, k, p)]["uzycia"] for k in KLASY)
                w.append("| %s | %s | %s | %s pp | %d–%s–%d | %s s | %s |" % (
                    NAZWY_M[p], RANGI[silnik.PRZECIWNICY[p]["ranga"]], " | ".join(proc(x) for x in r),
                    liczba(max(r) - min(r)), min(tury), liczba(statistics.median(tury), 0), max(tury), liczba(czas),
                    liczba(uz)))
        w.append("")
    if "b" in czesci:
        w.append("### (b) Klasa na klasę — wszystkie poziomy")
        w.append("")
        w.append("Komórka: wynik pierwszej klasy jako gracza / jako przeciwnika (100% − wynik drugiej) — cel 45–55%.")
        w.append("")
        pary = [(a_, b_) for i, a_ in enumerate(KLASY) for b_ in KLASY[i + 1:]]
        w.append("| Poziom | " + " | ".join("%s – %s" % (NAZWY[a_], NAZWY[b_]) for a_, b_ in pary) + " | Lustro (ta sama klasa) |")
        w.append("|---:|" + "---:|" * len(pary) + "---|")
        for L in poziomy:
            w.append("| %d | %s | %s |" % (L, " | ".join("%s / %s" % (proc(wyniki[(L, a_, b_)]["proc"]),
                                                                       proc(100 - wyniki[(L, b_, a_)]["proc"]))
                                                         for a_, b_ in pary),
                                           " / ".join(proc(wyniki[(L, k, k)]["proc"]) for k in KLASY)))
        w.append("")

    # ---------------------------------------------------------------- (c) wartosc punktu statystyki
    if "c" in czesci:
        w.append("### (c) Ile daje PUNKT statystyki każdej klasie")
        w.append("")
        w.append("Zmiana średniego procentu wygranych (pięć potworów i trzy klasy, %d walk na parę) po dodaniu 20%% puli "
                 "w jedną statystykę, podzielona przez liczbę dodanych punktów (pp na punkt)." % nm)
        w.append("")
        zad = []
        for L in Lw:
            dod = max(1, round(0.2 * wzorcowe.pula(L)))
            for k in KLASY:
                for s in [None] + wzorcowe.STATYSTYKI:
                    g = wzorcowe.postac(k, L, dodatkowe={s: dod} if s else None)
                    for p in MONSTRY + KLASY:
                        zad.append(((L, k, s, p), g, przeciwnik(p, L), S, nm, None))
        r = liczydlo.licz(zad)
        w.append("| Poziom | Klasa | " + " | ".join(NAZWY_STAT[s] for s in wzorcowe.STATYSTYKI) + " | Najsłabsza / najmocniejsza |")
        w.append("|---:|---|" + "---:|" * len(wzorcowe.STATYSTYKI) + "---:|")
        for L in Lw:
            dod = max(1, round(0.2 * wzorcowe.pula(L)))
            for k in KLASY:
                baza = statistics.mean(r[(L, k, None, p)]["proc"] for p in MONSTRY + KLASY)
                v = [(statistics.mean(r[(L, k, s, p)]["proc"] for p in MONSTRY + KLASY) - baza) / dod
                     for s in wzorcowe.STATYSTYKI]
                w.append("| %d | %s | %s | %s |" % (L, NAZWY[k], " | ".join(pp(x) for x in v),
                                                   liczba(min(v) / max(v), 2) if max(v) > 0 else "—"))
        w.append("")

    # ---------------------------------------------------------------- (d) uzycia umiejetnosci
    if "d" in czesci:
        w.append("### (d) Ile razy w walce pada umiejętność")
        w.append("")
        w.append("Średnia liczba użyć umiejętności gracza na walkę i mediana numeru własnej akcji z pierwszym użyciem "
                 "(postać wzorcowa i build pod manę, %d walk na parę)." % nm)
        w.append("")
        zad = []
        for L in Lw:
            for k in KLASY:
                for b in ("wzorcowa", "mana"):
                    g = wzorcowe.build(b, k, L)
                    for p in MONSTRY + [k]:
                        zad.append(((L, k, b, p), g, przeciwnik(p, L), S, nm, None))
        r = liczydlo.licz(zad)
        w.append("| Poziom | Klasa | Postać | " + " | ".join(NAZWY_M[p] for p in MONSTRY) + " | Lustro | Pierwsze użycie (akcja) |")
        w.append("|---:|---|---|" + "---:|" * (len(MONSTRY) + 1) + "---:|")
        for L in Lw:
            for k in KLASY:
                for b in ("wzorcowa", "mana"):
                    kom = [liczba(r[(L, k, b, p)]["uzycia"]) for p in MONSTRY + [k]]
                    pierw = statistics.median(r[(L, k, b, p)]["pierwsza"] for p in MONSTRY + [k])
                    w.append("| %d | %s | %s | %s | %s |" % (L, NAZWY[k], wzorcowe.NAZWY_BUILDOW[b], " | ".join(kom),
                                                            liczba(pierw, 1)))
        w.append("")

    # ---------------------------------------------------------------- (e) buildy
    if "e" in czesci:
        w.append("### (e) Buildy: z postacią wzorcową swojej klasy i z potworami")
        w.append("")
        w.append("Pojedynek z wzorcową: wynik buildu średnio z obu miejsc (cel 45–55%%). Potwory: różnica procentu "
                 "wygranych buildu i postaci wzorcowej tej klasy przy tym samym potworze (pp; %d walk)." % nm)
        w.append("")
        Le = [L for L in (5, 10, 15) if L in poziomy] or Lw
        zad = []
        for L in Le:
            for k in KLASY:
                for b in ["wzorcowa"] + wzorcowe.BUILDY_KLAS[k]:
                    g = wzorcowe.build(b, k, L)
                    for p in MONSTRY:
                        zad.append(((L, k, b, p), g, przeciwnik(p, L), S, nm, None))
                    zad.append(((L, k, b, "wz_gracz"), g, {"postac": wzorcowe.postac(k, L)}, S, nm, None))
                    zad.append(((L, k, b, "wz_wrog"), wzorcowe.postac(k, L), {"postac": g}, S, nm, None))
        r = liczydlo.licz(zad)
        w.append("| Poziom | Klasa | Build | Z wzorcową | " + " | ".join(NAZWY_M[p] for p in MONSTRY) + " |")
        w.append("|---:|---|---|---:|" + "---:|" * len(MONSTRY))
        for L in Le:
            for k in KLASY:
                for b in wzorcowe.BUILDY_KLAS[k]:
                    duel = (r[(L, k, b, "wz_gracz")]["proc"] + 100 - r[(L, k, b, "wz_wrog")]["proc"]) / 2
                    kom = [pp(r[(L, k, b, p)]["proc"] - r[(L, k, "wzorcowa", p)]["proc"]) for p in MONSTRY]
                    w.append("| %d | %s | %s | %s | %s |" % (L, NAZWY[k], wzorcowe.NAZWY_BUILDOW[b], proc(duel), " | ".join(kom)))
        w.append("")

    # ---------------------------------------------------------------- (f) blok 25% i 0%
    if "f" in czesci:
        w.append("### (f) Blok zmniejsza obrażenia: przechodzi 25% (dziś), 50% albo 0% (blok zatrzymuje cały cios — tylko porównanie)")
        w.append("")
        Lf = Lw
        zad = []
        for wariant in (0.25, 0.5, 0.0):
            zm = [("czesc_przez_blok", wariant)]
            for L in Lf:
                for k in KLASY:
                    g = wzorcowe.postac(k, L)
                    for p in MONSTRY + KLASY:
                        zad.append(((wariant, L, k, p), g, przeciwnik(p, L), S, nm, zm))
                g = wzorcowe.postac("wojownik", L, tarcza=False)
                for p in MONSTRY:
                    zad.append(((wariant, L, "bez_tarczy", p), g, przeciwnik(p, L), S, nm, zm))
        r = liczydlo.licz(zad)
        w.append("| Wariant | Poziom | Największa różnica klas (potwory) | Pojedynki klas (najniżej–najwyżej) | "
                 "Wojownik: wygrane z potworami z tarczą / bez | Ile daje tarcza |")
        w.append("|---|---:|---:|---|---|---:|")
        for wariant in (0.25, 0.5, 0.0):
            for L in Lf:
                roz = max(max(r[(wariant, L, k, p)]["proc"] for k in KLASY) - min(r[(wariant, L, k, p)]["proc"] for k in KLASY)
                          for p in MONSTRY)
                pv = [r[(wariant, L, k, b)]["proc"] for k in KLASY for b in KLASY if k != b]
                zt = statistics.mean(r[(wariant, L, "wojownik", p)]["proc"] for p in MONSTRY)
                bt = statistics.mean(r[(wariant, L, "bez_tarczy", p)]["proc"] for p in MONSTRY)
                w.append("| %s przechodzi | %d | %s pp | %s–%s | %s / %s | %s pp |" % (
                    proc(100 * wariant), L, liczba(roz), proc(min(pv)), proc(max(pv)), proc(zt), proc(bt), pp(zt - bt)))
        w.append("")

    # ---------------------------------------------------------------- (g) sloty
    if "g" in czesci:
        w.append("### (g) Sloty: aktywne, pasywne i mieszanki")
        w.append("")
        w.append("Średni procent wygranych z pięcioma potworami i z wzorcową postacią tej klasy (%d walk na parę)." % nm)
        w.append("")
        Lg = [L for L in (10, 15) if L in poziomy] or Lw
        zestawy = {
            "wojownik": [["ciecie", "miazdzacy_cios", "kamienna_skora"], ["ciecie", "miazdzacy_cios", "kolos"],
                         ["ciecie", "kolos", "rozdzieracz"], ["kolos", "rozdzieracz", "furia"], ["ciecie"], ["kolos"]],
            "zwiadowca": [["uderzenie_z_gory", "zatruta_strzala", "skupienie"], ["uderzenie_z_gory", "skupienie", "oko_lowcy"],
                          ["uderzenie_z_gory", "oko_lowcy", "zwinnosc"], ["oko_lowcy", "zwinnosc", "seria"],
                          ["uderzenie_z_gory"], ["oko_lowcy"]],
            "mag": [["kula_ognia", "lodowy_pocisk", "bariera"], ["kula_ognia", "lodowy_pocisk", "skupiona_magia"],
                    ["kula_ognia", "skupiona_magia", "magiczny_pocisk"], ["skupiona_magia", "magiczny_pocisk", "przeplyw_many"],
                    ["kula_ognia"], ["skupiona_magia"]],
        }
        zad = []
        for L in Lg:
            for k in KLASY:
                for i, um in enumerate(zestawy[k]):
                    g = wzorcowe.postac(k, L, umiejetnosci=um)
                    for p in MONSTRY:
                        zad.append(((L, k, i, p), g, przeciwnik(p, L), S, nm, None))
                    zad.append(((L, k, i, "wz"), g, {"postac": wzorcowe.postac(k, L)}, S, nm, None))
        r = liczydlo.licz(zad)
        w.append("| Poziom | Klasa | Sloty | Aktywne / pasywne | Śr. z potworami | Z wzorcową | Umiejętności na walkę |")
        w.append("|---:|---|---|---|---:|---:|---:|")
        for L in Lg:
            for k in KLASY:
                for i, um in enumerate(zestawy[k]):
                    akt = sum(1 for u in um if u in silnik.UMIEJETNOSCI)
                    nazwy = ", ".join((silnik.UMIEJETNOSCI.get(u) or silnik.PASYWNE.get(u))["nazwa"] for u in um)
                    sr = statistics.mean(r[(L, k, i, p)]["proc"] for p in MONSTRY)
                    uz = statistics.mean(r[(L, k, i, p)]["uzycia"] for p in MONSTRY)
                    w.append("| %d | %s | %s | %d / %d | %s | %s | %s |" % (L, NAZWY[k], nazwy, akt, len(um) - akt, proc(sr),
                                                                       proc(r[(L, k, i, "wz")]["proc"]), liczba(uz)))
        w.append("")

    # ---------------------------------------------------------------- (h) nabijanie jednej statystyki
    if "h" in czesci:
        w.append("### (h) Nabijanie jednej statystyki")
        w.append("")
        w.append("Postać, która wkłada 60%% puli w jedną statystykę (reszta jak w rozkładzie klasy, przeskalowana), "
                 "kontra rozkład wzorcowy: średni procent wygranych z potworami i z wzorcową postacią (%d walk)." % nm)
        w.append("")
        zad = []
        for k in KLASY:
            for s in [None] + wzorcowe.STATYSTYKI:
                if s is None:
                    roz = None
                else:
                    reszta = {x: v for x, v in wzorcowe.ROZKLADY[k].items() if x != s}
                    suma = sum(reszta.values())
                    roz = {x: 0.4 * v / suma for x, v in reszta.items()}
                    roz[s] = 0.6
                g = wzorcowe.postac(k, L5, rozklad=roz)
                for p in MONSTRY:
                    zad.append(((k, s, p), g, przeciwnik(p, L5), S, nm, None))
                zad.append(((k, s, "wz"), g, {"postac": wzorcowe.postac(k, L5)}, S, nm, None))
        r = liczydlo.licz(zad)
        w.append("| Klasa | Wzorcowy rozkład | " + " | ".join("60% " + NAZWY_STAT[s] for s in wzorcowe.STATYSTYKI) + " |")
        w.append("|---|---:|" + "---:|" * len(wzorcowe.STATYSTYKI))
        for k in KLASY:
            kom = []
            for s in [None] + wzorcowe.STATYSTYKI:
                sr = statistics.mean(r[(k, s, p)]["proc"] for p in MONSTRY)
                kom.append("%s / %s" % (proc(sr), proc(r[(k, s, "wz")]["proc"])))
            w.append("| %s | %s |" % (NAZWY[k], " | ".join(kom)))
        w.append("")
        w.append("W komórce: średnio z potworami / z wzorcową postacią tej klasy (poziom %d)." % L5)
        w.append("")

    # ---------------------------------------------------------------- (i) wysokie poziomy
    if "i" in czesci:
        w.append("### (i) Wysokie poziomy")
        w.append("")
        w.append("Te same potwory lasu przeskalowane do wysokiego poziomu (zastępczo za potwory dalszych biomów — "
                 "sprawdzamy wzory, nie trudność biomu) i pojedynki klas; %d walk na parę." % nm)
        w.append("")
        Li = [30, 50, 75, 100]
        zad = []
        for L in Li:
            for k in KLASY:
                g = wzorcowe.postac(k, L)
                for p in MONSTRY + KLASY:
                    zad.append(((L, k, p), g, przeciwnik(p, L), S, nm, None))
        r = liczydlo.licz(zad)
        w.append("| Poziom | Największa różnica klas | Pojedynki klas | Tury: zwykły / strażnik (mediana) | "
                 "Czas walki: zwykły / strażnik | Umiejętności na walkę | Unik / krytyk / moc (Zwiadowca, Mag) |")
        w.append("|---:|---:|---|---|---|---:|---|")
        for L in Li:
            roz = max(max(r[(L, k, p)]["proc"] for k in KLASY) - min(r[(L, k, p)]["proc"] for k in KLASY) for p in MONSTRY)
            pv = [r[(L, k, b)]["proc"] for k in KLASY for b in KLASY if k != b]
            zw = [t for k in KLASY for p in MONSTRY if silnik.PRZECIWNICY[p]["ranga"] == "zwykly" for t in r[(L, k, p)]["tury"]]
            st = [t for k in KLASY for t in r[(L, k, "straznik_lasu")]["tury"]]
            czz = statistics.mean(r[(L, k, p)]["czas"] for k in KLASY for p in MONSTRY if silnik.PRZECIWNICY[p]["ranga"] == "zwykly")
            czs = statistics.mean(r[(L, k, "straznik_lasu")]["czas"] for k in KLASY)
            uz = statistics.mean(r[(L, k, p)]["uzycia"] for k in KLASY for p in MONSTRY)
            vz = silnik.wartosci_postaci(wzorcowe.postac("zwiadowca", L))
            vm = silnik.wartosci_postaci(wzorcowe.postac("mag", L))
            w.append("| %d | %s pp | %s–%s | %s / %s | %s s / %s s | %s | %s / %s / %s; %s / %s / %s |" % (
                L, liczba(roz), proc(min(pv)), proc(max(pv)), liczba(statistics.median(zw), 0), liczba(statistics.median(st), 0),
                liczba(czz), liczba(czs), liczba(uz), proc(100 * vz["unik"]), proc(100 * vz["krytyk"]), liczba(vz["moc"], 2),
                proc(100 * vm["unik"]), proc(100 * vm["krytyk"]), liczba(vm["moc"], 2)))
        w.append("")

    # ---------------------------------------------------------------- (j) Pancerz
    if "j" in czesci:
        w.append("### (j) Pancerz: limit redukcji i przelicznik klasy")
        w.append("")
        lim = silnik.STALE["limit_redukcji"]
        w.append("Obrona nigdy nie zatrzymuje więcej niż %s surowego ciosu (przechodzi zawsze co najmniej %s). "
                 "Pancerz każdej klasy na poziomie %d przy tej samej puli i tych samych przedmiotach, i ile zostaje z ciosu "
                 "Leśnego Trolla tego poziomu (bez krytyka, rozrzut 100%%):" % (proc(100 * lim), proc(100 - 100 * lim), L5))
        w.append("")
        troll = silnik.wartosci_potwora("lesny_troll", L5)
        w.append("| Klasa | Przelicznik Pancerza | Pancerz (punkty) | Cios trolla | Po Pancerzu | Redukcja | "
                 "+30 punktów Pancerza: redukcja |")
        w.append("|---|---:|---:|---:|---:|---:|---:|")
        for k in KLASY:
            v0 = silnik.wartosci_postaci(wzorcowe.postac(k, L5))
            v1 = silnik.wartosci_postaci(wzorcowe.postac(k, L5, dodatkowe={"pancerz": 30}))
            c = troll["cios"]
            po0 = max(c * (1 - lim), c - v0["pancerz"])
            po1 = max(c * (1 - lim), c - v1["pancerz"])
            w.append("| %s | %s | %s | %s | %s | %s | %s |" % (NAZWY[k], liczba(silnik.KLASY[k]["mnoznik_pancerza"], 2),
                                                           liczba(v0["pancerz"]), liczba(c), liczba(po0),
                                                           proc(100 * (1 - po0 / c)), proc(100 * (1 - po1 / c))))
        w.append("")

    # ---------------------------------------------------------------- (k) wskrzeszenie
    if "k" in czesci:
        w.append("### (k) Wskrzeszenie (propozycja D-094) zamiast zwykłej umiejętności w slocie")
        w.append("")
        w.append("Postać wzorcowa z wskrzeszeniem w ostatnim slocie (zamiast ostatniej aktywnej; na 1.–4. poziomie jedyny "
                 "slot) i dla porównania z pasywką Kolos / Oko łowcy / Skupiona magia w tym slocie. Komórka: pojedynek z "
                 "wzorcową (oba miejsca) / zmiana średnich wygranych z potworami względem wzorcowej (pp; %d walk)." % nm)
        w.append("")
        Lk = [L for L in (3, 5, 10) if L in poziomy] or Lw
        ulamki = (0.0001, 0.05, 0.1, 0.25, 0.5, 1.0)  # 0.0001 = 1 punkt zycia (jak dawny pomysl „Jeszcze stoje”)
        zwykla_pas = {"wojownik": "kolos", "zwiadowca": "oko_lowcy", "mag": "skupiona_magia"}
        zad = []
        for L in Lk:
            for k in KLASY:
                wz = wzorcowe.postac(k, L)
                n_sl = wzorcowe.sloty(L)
                warianty = [("wzorcowa", None, None), ("pasywka", zwykla_pas[k], None)] + [("wsk", "wskrzeszenie", u) for u in ulamki]
                for nazwa, pas, u in warianty:
                    if pas is None:
                        g = wz
                    else:
                        g = wzorcowe.postac(k, L, umiejetnosci=wzorcowe.UMIEJETNOSCI[k][:n_sl - 1] + [pas])
                    zm = [("wskrzeszenie", u)] if u is not None else None
                    for p in MONSTRY:
                        zad.append(((L, k, nazwa, u, p), g, przeciwnik(p, L), S, nm, zm))
                    zad.append(((L, k, nazwa, u, "wz_g"), g, {"postac": wz}, S, nm, zm))
                    zad.append(((L, k, nazwa, u, "wz_w"), wz, {"postac": g}, S, nm, zm))
        r = liczydlo.licz(zad)
        w.append("| Poziom | Klasa | Zwykła pasywka w slocie | " + " | ".join(
            "Wskrzeszenie: 1 HP" if u < 0.001 else "Wskrzeszenie %s życia" % proc(100 * u) for u in ulamki) + " |")
        w.append("|---:|---|---:|" + "---:|" * len(ulamki))
        for L in Lk:
            for k in KLASY:
                baza = statistics.mean(r[(L, k, "wzorcowa", None, p)]["proc"] for p in MONSTRY)

                def kom(nazwa, u):
                    duel = (r[(L, k, nazwa, u, "wz_g")]["proc"] + 100 - r[(L, k, nazwa, u, "wz_w")]["proc"]) / 2
                    mon = statistics.mean(r[(L, k, nazwa, u, p)]["proc"] for p in MONSTRY) - baza
                    return "%s / %s" % (proc(duel), pp(mon))
                w.append("| %d | %s | %s | %s |" % (L, NAZWY[k], kom("pasywka", None), " | ".join(kom("wsk", u) for u in ulamki)))
        w.append("")

    # ---------------------------------------------------------------- (l) przeszukanie zestawow slotow
    if "l" in czesci:
        import itertools
        w.append("### (l) Przeszukanie wszystkich zestawów slotów (bez broni z pasywką, zaklęcia i premii)")
        w.append("")
        n_sito, n_pot = max(100, nm // 5), nm
        w.append("Każdy zestaw 1–3 slotów klasy (aktywne w każdej kolejności, pasywne, bez wskrzeszenia) w pojedynku z "
                 "wzorcową tej klasy (oba miejsca): sito %d walk z każdej strony, trzy najlepsze potwierdzone na %d "
                 "innych ziarnach. Wybór slotów jest darmowy, więc żaden zestaw nie powinien wyraźnie bić wzorcowej "
                 "(kontrola 16/17.11: przed osłabieniem pasywek many najlepsze miały 63–67%%)." % (n_sito, n_pot))
        w.append("")

        def zestawy(k, n):
            akt = silnik.KLASY[k]["umiejetnosci"]
            pas = silnik.KLASY[k]["pasywne"]
            out = []
            for r_ in range(1, n + 1):
                for zb in itertools.combinations(akt + pas, r_):
                    a_ = [x for x in zb if x in akt]
                    for perm in itertools.permutations(a_):
                        out.append(list(perm) + [x for x in zb if x not in akt])
            return out
        w.append("| Poziom | Klasa | 1. zestaw | 2. zestaw | 3. zestaw |")
        w.append("|---:|---|---|---|---|")
        for L in Lw:
            for k in KLASY:
                wz = wzorcowe.postac(k, L)
                lista = zestawy(k, wzorcowe.sloty(L))
                zad = []
                for i, um in enumerate(lista):
                    g = wzorcowe.postac(k, L, umiejetnosci=um)
                    zad.append(((i, "g"), g, {"postac": wz}, S + 300000, n_sito, None))
                    zad.append(((i, "w"), wz, {"postac": g}, S + 300000, n_sito, None))
                r = liczydlo.licz(zad)
                sito = sorted(range(len(lista)), key=lambda i: -(r[(i, "g")]["proc"] + 100 - r[(i, "w")]["proc"]))[:3]
                zad = []
                for i in sito:
                    g = wzorcowe.postac(k, L, umiejetnosci=lista[i])
                    zad.append(((i, "g"), g, {"postac": wz}, S + 400000, n_pot, None))
                    zad.append(((i, "w"), wz, {"postac": g}, S + 400000, n_pot, None))
                r = liczydlo.licz(zad)
                kom = sorted(((r[(i, "g")]["proc"] + 100 - r[(i, "w")]["proc"]) / 2, i) for i in sito)[::-1]
                w.append("| %d | %s | %s |" % (L, NAZWY[k], " | ".join(
                    "%s: %s" % (", ".join((silnik.UMIEJETNOSCI.get(u) or silnik.PASYWNE.get(u))["nazwa"] for u in lista[i]),
                                proc(d)) for d, i in kom)))
        w.append("")

    w.append("_Policzone w %.0f s (python -B tools/walka/balans.py --ziaren %d --start %d --czesci %s)._"
             % (time.time() - t0, N, S, a.czesci))
    tekst = "\n".join(w) + "\n"
    print(tekst)
    if a.md:
        with open(a.md, "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst)


if __name__ == "__main__":
    main()
