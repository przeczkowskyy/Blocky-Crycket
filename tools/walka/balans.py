#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tabela balansu silnika walki v2 — ma WYKAZAC, ze klasy sa rowne (U10), a nie pokazac, kto kogo kontruje.

    python -B tools/walka/balans.py                       # 2000 ziaren, poziomy 1-10, 12, 15, 20 (kilka minut)
    python -B tools/walka/balans.py --ziaren 500          # szybciej, mniej dokladnie
    python -B tools/walka/balans.py --start 50001         # inne ziarna (50001..), kontrola, czy wynik nie jest
                                                          # dopasowany do ziaren 1..N, na ktorych liczy test
    python -B tools/walka/balans.py --md wynik.md         # zapisz tabele Markdown do pliku

Wszystkie klasy dostaja na danym poziomie te sama pule punktow statystyk, te sama bron, ten sam pancerz
z przedmiotow i tyle samo slotow umiejetnosci (tools/walka/wzorcowe.py); roznia sie stylem rozkladu punktow
i cecha klasy (tarcza Wojownika). Kazda para liczy sie na tych samych ziarnach start..start+N-1.

  (a) klasa przeciw kazdemu potworowi lasu: procent wygranych, tury (srednia, najkrotsza-mediana-najdluzsza),
      sredni czas walki — pelne tabele dla poziomow --szczegoly, a dla WSZYSTKICH poziomow zestawienie
      najwiekszej roznicy klas; cel: roznica miedzy klasami przy tym samym potworze najwyzej ok. 5 pp
      (test w test_walki.py pilnuje 7 pp na kazdym poziomie);
  (b) macierz klasa na klase (Arena, test lustrzany); cel: 45-55% w kazdej parze na kazdym poziomie;
  (c) wrazliwosc: ile procent wygranych daje kazda z szesciu statystyk kazdej klasie (+20% puli w jedna statystyke);
  (d) Wojownik z tarcza i wysoka Zrecznoscia (pytanie 40 z sesji) na tle zwyklych postaci.
"""
import argparse
import os
import statistics
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import silnik  # noqa: E402
import wzorcowe  # noqa: E402

KLASY = wzorcowe.KLASY
NAZWY = {k: silnik.KLASY[k]["nazwa"] for k in KLASY}
MONSTRY = [p["id"] for p in silnik.PRZECIWNICY_LISTA]
RANGI = {"zwykly": "zwykły", "rzadki": "rzadki", "straznik": "strażnik"}
NAZWY_STAT = {"sila": "Siła", "kondycja": "Kondycja", "inteligencja": "Inteligencja", "zrecznosc": "Zręczność",
              "szczescie": "Szczęście", "pancerz": "Pancerz"}
CEL_KLAS_PP = 5.0
CEL_PVP = (45.0, 55.0)


def przeciwnik(nazwa, poziom):
    if nazwa in KLASY:
        return {"postac": wzorcowe.postac(nazwa, poziom)}
    return {"potwor": nazwa, "poziom": poziom}


START = 1


def seria(gracz, prz, n):
    wygrane, tury, czasy = 0, [], []
    for z in range(START, START + n):
        w = silnik.symuluj(gracz, prz, z)
        wygrane += w["wynik"] == "wygrana"
        tury.append(w["tury"])
        czasy.append(w["czas"])
    return {"proc": 100.0 * wygrane / n, "tury": tury, "czas": statistics.mean(czasy), "czas_maks": max(czasy)}


def pp(x):
    return ("%+.1f" % x).replace(".", ",")


def proc(x):
    return ("%.1f%%" % x).replace(".", ",")


def liczba(x, n=1):
    return ("%.*f" % (n, x)).replace(".", ",")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Tabela balansu silnika walki v2")
    ap.add_argument("--ziaren", type=int, default=2000)
    ap.add_argument("--start", type=int, default=1, help="pierwsze ziarno (domyslnie 1, jak w testach)")
    ap.add_argument("--poziomy", default="1,2,3,4,5,6,7,8,9,10,12,15,20")
    ap.add_argument("--szczegoly", default="1,5,10", help="poziomy z pelnymi tabelami (a) i (b)")
    ap.add_argument("--md", default=None, help="zapisz wynik (Markdown) do pliku")
    a = ap.parse_args()
    global START
    START = a.start
    poziomy = [int(x) for x in a.poziomy.split(",")]
    szczegoly = [L for L in (int(x) for x in a.szczegoly.split(",")) if L in poziomy]
    N = a.ziaren
    t0 = time.time()

    # (a) i (b)
    wyniki = {}
    for L in poziomy:
        for k in KLASY:
            g = wzorcowe.postac(k, L)
            for p in MONSTRY + KLASY:
                wyniki[(L, k, p)] = seria(g, przeciwnik(p, L), N)
    najw_roznica, gdzie_roznica = 0.0, ""
    pvp_min, pvp_maks = 100.0, 0.0
    for L in poziomy:
        for p in MONSTRY:
            r = [wyniki[(L, k, p)]["proc"] for k in KLASY]
            if max(r) - min(r) > najw_roznica:
                najw_roznica, gdzie_roznica = max(r) - min(r), "%s, poziom %d" % (silnik.PRZECIWNICY[p]["nazwa"], L)
        for k in KLASY:
            for b in KLASY:
                if k != b:
                    pvp_min = min(pvp_min, wyniki[(L, k, b)]["proc"])
                    pvp_maks = max(pvp_maks, wyniki[(L, k, b)]["proc"])

    # (c) wrazliwosc na poziomie srodkowym
    Lw = 5 if 5 in poziomy else poziomy[len(poziomy) // 2]
    dodatek = max(1, round(0.2 * wzorcowe.pula(Lw)))
    nw = max(200, N // 2)
    wrazliwosc = {}
    for k in KLASY:
        def srednia(g):
            return statistics.mean(seria(g, przeciwnik(p, Lw), nw)["proc"] for p in MONSTRY + KLASY)
        baza = srednia(wzorcowe.postac(k, Lw))
        for s in wzorcowe.STATYSTYKI:
            wrazliwosc[(k, s)] = srednia(wzorcowe.postac(k, Lw, dodatkowe={s: dodatek})) - baza
    najslabsza = min(wrazliwosc.items(), key=lambda kv: kv[1])

    # (d) Wojownik z tarcza i wysoka Zrecznoscia
    Ld = Lw
    rozklad = dict(wzorcowe.ROZKLADY["wojownik"])
    rozklad["zrecznosc"] += 0.15
    rozklad["kondycja"] -= 0.08
    rozklad["sila"] -= 0.07
    warianty = [
        ("Wojownik wzorcowy (tarcza)", wzorcowe.postac("wojownik", Ld)),
        ("Wojownik zwinny (tarcza, +15% puli w Zręczność)", wzorcowe.postac("wojownik", Ld, rozklad=rozklad)),
        ("Wojownik zwinny bez tarczy", wzorcowe.postac("wojownik", Ld, rozklad=rozklad, tarcza=False)),
        ("Zwiadowca wzorcowy", wzorcowe.postac("zwiadowca", Ld)),
        ("Mag wzorcowy", wzorcowe.postac("mag", Ld)),
    ]
    tabela_d = []
    for nazwa, g in warianty:
        v = silnik.wartosci_postaci(g)
        pot = statistics.mean(seria(g, przeciwnik(p, Ld), nw)["proc"] for p in MONSTRY)
        kl = statistics.mean(seria(g, przeciwnik(b, Ld), nw)["proc"] for b in KLASY)
        tabela_d.append((nazwa, v["unik"], v["blok"], pot, kl))

    # Markdown
    w = []
    klasy_ok = najw_roznica <= CEL_KLAS_PP
    pvp_ok = CEL_PVP[0] <= pvp_min and pvp_maks <= CEL_PVP[1]
    if klasy_ok and pvp_ok:
        wniosek = ("**Wniosek: klasy są równe** — przy tym samym potworze różnią się najwyżej o %s pp (cel ≤ %s), "
                   "a pojedynki klasa na klasę mieszczą się w %s–%s (cel 45–55%%)."
                   % (liczba(najw_roznica), liczba(CEL_KLAS_PP, 0), proc(pvp_min), proc(pvp_maks)))
    else:
        braki = []
        if not klasy_ok:
            braki.append("przy tym samym potworze różnica dochodzi do %s pp (%s; cel ≤ %s)"
                         % (liczba(najw_roznica), gdzie_roznica, liczba(CEL_KLAS_PP, 0)))
        if not pvp_ok:
            braki.append("pojedynki klasa na klasę %s–%s (cel 45–55%%)" % (proc(pvp_min), proc(pvp_maks)))
        wniosek = "**Wniosek: klasy są blisko równości, ale cel nie jest w pełni spełniony** — " + "; ".join(braki) + "."
    w.append(wniosek)
    w.append("")
    w.append("Każda komórka: %d walk na tych samych ziarnach %d–%d. Wymiana = tura jednej strony. "
             "Pula punktów statystyk: %d na 1. poziomie + %d za każdy kolejny. Sloty umiejętności: 1 (poziom 1–4), "
             "2 (5–9), 3 (od 10)." % (N, START, START + N - 1, wzorcowe.PUNKTY_START, wzorcowe.PUNKTY_NA_POZIOM))
    w.append("")
    w.append("### (a) Różnica klas przy tym samym potworze — wszystkie poziomy")
    w.append("")
    w.append("Komórka: największa różnica procentu wygranych między klasami (pp), w nawiasie Wojownik / Zwiadowca / Mag.")
    w.append("")
    w.append("| Poziom | " + " | ".join(silnik.PRZECIWNICY[p]["nazwa"] for p in MONSTRY) + " |")
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
        w.append("| Przeciwnik | Ranga | " + " | ".join(NAZWY[k] for k in KLASY) + " | Różnica klas | Tury: średnio (najkrótsza–mediana–najdłuższa) | Średni czas |")
        w.append("|---|---|" + "---:|" * len(KLASY) + "---:|---|---:|")
        for p in MONSTRY:
            r = [wyniki[(L, k, p)]["proc"] for k in KLASY]
            tury = [t for k in KLASY for t in wyniki[(L, k, p)]["tury"]]
            czas = statistics.mean(wyniki[(L, k, p)]["czas"] for k in KLASY)
            w.append("| %s | %s | %s | %s pp | %s (%d–%s–%d) | %s s |" % (
                silnik.PRZECIWNICY[p]["nazwa"], RANGI[silnik.PRZECIWNICY[p]["ranga"]], " | ".join(proc(x) for x in r),
                liczba(max(r) - min(r)), liczba(statistics.mean(tury)), min(tury), liczba(statistics.median(tury), 0),
                max(tury), liczba(czas)))
    w.append("")
    w.append("### (b) Klasa na klasę — wszystkie poziomy")
    w.append("")
    w.append("Procent wygranych pierwszej klasy z pary (cel 45–55%).")
    w.append("")
    pary = [(a_, b_) for i, a_ in enumerate(KLASY) for b_ in KLASY[i + 1:]]
    w.append("| Poziom | " + " | ".join("%s – %s" % (NAZWY[a_], NAZWY[b_]) for a_, b_ in pary) + " |")
    w.append("|---:|" + "---:|" * len(pary))
    for L in poziomy:
        w.append("| %d | %s |" % (L, " | ".join("%s / %s" % (proc(wyniki[(L, a_, b_)]["proc"]), proc(100 - wyniki[(L, b_, a_)]["proc"]))
                                             for a_, b_ in pary)))
    w.append("")
    w.append("W komórce: wynik pierwszej klasy, gdy to ona jest graczem / gdy jest przeciwnikiem (100% − wynik drugiej).")
    w.append("")
    w.append("### (b) Klasa na klasę — szczegóły (procent wygranych klasy z wiersza)")
    for L in szczegoly:
        w.append("")
        w.append("**Poziom %d**" % L)
        w.append("")
        w.append("| Gracz \\ Przeciwnik | " + " | ".join(NAZWY[k] for k in KLASY) + " | Tury (najkrótsza–mediana–najdłuższa) |")
        w.append("|---|" + "---:|" * len(KLASY) + "---|")
        for k in KLASY:
            tury = [t for b in KLASY for t in wyniki[(L, k, b)]["tury"]]
            w.append("| %s | %s | %d–%s–%d |" % (NAZWY[k], " | ".join(proc(wyniki[(L, k, b)]["proc"]) for b in KLASY),
                                              min(tury), liczba(statistics.median(tury), 0), max(tury)))
    w.append("")
    w.append("### (c) Czy każda statystyka coś daje (poziom %d, +%d punktów w jedną statystykę)" % (Lw, dodatek))
    w.append("")
    w.append("Zmiana średniego procentu wygranych z pięcioma potworami i trzema klasami (%d walk na parę)." % nw)
    w.append("")
    w.append("| Klasa | " + " | ".join(NAZWY_STAT[s] for s in wzorcowe.STATYSTYKI) + " |")
    w.append("|---|" + "---:|" * len(wzorcowe.STATYSTYKI))
    for k in KLASY:
        w.append("| %s | %s |" % (NAZWY[k], " | ".join(pp(wrazliwosc[(k, s)]) + " pp" for s in wzorcowe.STATYSTYKI)))
    w.append("")
    w.append("Najmniej daje: %s u klasy %s (%s pp)." % (NAZWY_STAT[najslabsza[0][1]], NAZWY[najslabsza[0][0]],
                                                         pp(najslabsza[1])))
    w.append("")
    w.append("### (d) Wojownik z tarczą i wysoką Zręcznością (poziom %d)" % Ld)
    w.append("")
    w.append("| Postać | Unik | Blok | Śr. wygrane z potworami | Śr. wygrane z klasami |")
    w.append("|---|---:|---:|---:|---:|")
    for nazwa, unik, blok, pot, kl in tabela_d:
        w.append("| %s | %s | %s | %s | %s |" % (nazwa, proc(100 * unik), proc(100 * blok), proc(pot), proc(kl)))
    w.append("")
    w.append("_Policzone w %.0f s (%s)._" % (time.time() - t0, "python -B tools/walka/balans.py --ziaren %d --start %d"
                                               % (N, START)))
    tekst = "\n".join(w) + "\n"
    print(tekst)
    if a.md:
        with open(a.md, "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst)


if __name__ == "__main__":
    main()
