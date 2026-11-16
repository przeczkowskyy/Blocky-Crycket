#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model tempa (propozycja liczb, NIE kanon): ile minut zajmuje nowemu graczowi las i ile cala gra do 8. biomu.

    python -B tools/walka/tempo.py                         # las + model biomow, wynik Markdown na ekran
    python -B tools/walka/tempo.py --md tempo.md            # z zapisem do pliku
    python -B tools/walka/tempo.py --graczy 300 --trening 6 # wiecej symulowanych graczy, trening 6 pkt/min
    python -B tools/walka/tempo.py --dopasuj                # dobierz krzywa doswiadczenia pod cel lasu (30 min)

CZESC 1 — LAS (jedyny biom z danymi potworow): symulacja gracz po graczu, walka po walce, prawdziwym silnikiem
(tools/walka/silnik.py). Gracz zaczyna na 1. poziomie i idzie przegrodami lasu: Lesny Slime -> Muchomorniki ->
Cierniowe Wilki -> Lesny Troll (brama: trzeba go pokonac) -> Straznik Gaju (koniec). Czas walki = czas z dziennika
(naturalne czasy zdarzen przy tempie x1, albo podzielony przez --tempo-odtwarzania), do tego dojscie do potwora
i czekanie na odrodzenie (parametr przegrody), odrodzenie gracza po przegranej i rozdanie punktow po awansie.
Doswiadczenie z lupu silnika (20% za przegrana). Polityka gracza (prosta, jawna):
  - w zwyklej przegrodzie walczy z potworem o losowym poziomie z zakresu przegrody, ale nie wyzszym niz wlasny + 1;
  - idzie dalej, gdy jego poziom >= najnizszy poziom nastepnej przegrody;
  - po dwoch przegranych z rzedu w zwyklej przegrodzie cofa sie o jedna (farmienie);
  - przy bramie (troll, straznik) probuje; po przegranej wraca do poprzedniej przegrody na --farmienie walk albo,
    z --trening > 0, trenuje --trening-min minut w Training Center, i probuje znowu;
  - punkty z poziomu rozdaje rozkladem swojej klasy (postac wzorcowa), punkty z treningu dostaje statystyka
    najbardziej ponizej swojego udzialu (mini-gra daje punkty JEDNEJ statystyki; malejacy zysk: tempo treningu
    = trening / (1 + wytrenowane / --trening-polowa)).
CZESC 2 — MODEL BIOMOW 1-7 (bez wymyslania potworow): ta sama krzywa doswiadczenia, cykl walki (walka + dojscie
+ przegrane) i doswiadczenie za walke jak w lesie, przeskalowane do poziomu gracza (potwory lasu jako zastepcze).
Plan czasu na biomy jest parametrem (--plan), domyslnie rosnacy 30/45/60/75/95/125/170 min (= 600) i wariant rowny.
Wynik: na jakim poziomie gracz konczy kazdy biom, ile poziomow i walk na biom, i na jakim poziomie dochodzi do 8.
"""
import argparse
import math
import os
import random
import statistics
import sys

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import silnik  # noqa: E402
import wzorcowe  # noqa: E402

# przegrody lasu: (potwor, poziom od, poziom do, sekundy miedzy walkami: dojscie + czekanie na odrodzenie, brama?)
# poziomy wzorowane na swiat/las_potwory (slime 1-3, muchomorniki 3-5, wilki 5-8, straznik 10); troll dodany przed
# straznikiem (w pakiecie lasu go nie ma) — to propozycja do decyzji
PRZEGRODY = [
    ("lesny_slime", 1, 3, 8, False),
    ("muchomornik", 3, 5, 10, False),
    ("cierniowy_wilk", 5, 8, 10, False),
    ("lesny_troll", 9, 9, 25, True),
    ("straznik_lasu", 10, 10, 40, True),
]
PLAN_ROSNACY = [30, 45, 60, 75, 95, 125, 170]
NAZWY_BIOMOW = ["Las", "Bagno", "Dżungla", "Pustynia", "Góry z tundrą", "Lodowiec", "Wulkaniczny"]


def xp_do_nastepnego(L, A, B):
    """Doswiadczenie potrzebne z poziomu L na L+1 (propozycja krzywej: A * L^B, zaokraglone)."""
    return max(1, int(round(A * L ** B)))


def postac_gracza(klasa, L, wytrenowane):
    return wzorcowe.postac(klasa, L, dodatkowe=wytrenowane or None)


def trenuj(klasa, L, wytrenowane, punkty):
    """Punkty z mini-gry do JEDNEJ statystyki naraz: tej, ktorej udzial w calej puli najbardziej odstaje od rozkladu."""
    for _ in range(punkty):
        rozklad = wzorcowe.ROZKLADY[klasa]
        baza = wzorcowe.rozdziel(rozklad, wzorcowe.pula(L))
        razem = sum(baza.values()) + sum(wytrenowane.values())
        brak = {s: rozklad[s] * (razem + 1) - (baza[s] + wytrenowane.get(s, 0)) for s in wzorcowe.STATYSTYKI}
        s = max(wzorcowe.STATYSTYKI, key=lambda x: (brak[x], -wzorcowe.STATYSTYKI.index(x)))
        wytrenowane[s] = wytrenowane.get(s, 0) + 1


def jeden_gracz(klasa, los, a):
    """Symulacja jednego gracza w lesie -> slownik z czasem (s), przegranymi, poziomem itd."""
    L, xp, czas = 1, 0, 0.0
    wytrenowane = {}
    trening_razem = 0.0
    strefa = 0
    przegrane = walki = przegrane_z_rzedu = proby_bram = 0
    czasy = {"walki": 0.0, "dojscie": 0.0, "odrodzenie": 0.0, "punkty": 0.0, "trening": 0.0}
    farmienie = 0
    while True:
        if czas > a.limit_min * 60:
            return None
        potwor, od, do, miedzy, brama = PRZEGRODY[strefa]
        # gracz wybiera potwory nie wyzsze niz jego poziom + 1 (o ile przegroda takie ma)
        poziom_potwora = los.randint(od, max(od, min(do, L + 1)))
        g = postac_gracza(klasa, L, wytrenowane)
        w = silnik.symuluj(g, {"potwor": potwor, "poziom": poziom_potwora}, los.randrange(2 ** 31))
        walki += 1
        t_walki = w["czas"] / a.tempo_odtwarzania
        czas += t_walki + miedzy
        czasy["walki"] += t_walki
        czasy["dojscie"] += miedzy
        xp += w["lup"]["doswiadczenie"]
        wygrana = w["wynik"] == "wygrana"
        while xp >= xp_do_nastepnego(L, a.xp_a, a.xp_b):
            xp -= xp_do_nastepnego(L, a.xp_a, a.xp_b)
            L += 1
            czas += a.punkty_s
            czasy["punkty"] += a.punkty_s
        if brama:
            proby_bram += 1
        if wygrana:
            przegrane_z_rzedu = 0
            if brama and strefa == len(PRZEGRODY) - 1:
                return {"czas": czas, "przegrane": przegrane, "poziom": L, "walki": walki, "proby_bram": proby_bram,
                        "trening": trening_razem, "czasy": czasy, "wytrenowane": sum(wytrenowane.values())}
            if brama:
                strefa += 1
                continue
            if farmienie > 0:
                farmienie -= 1
                if farmienie == 0:
                    strefa = min(strefa + 1, len(PRZEGRODY) - 1)
                continue
            nast = PRZEGRODY[strefa + 1]
            if L >= nast[1] or (nast[4] and L >= nast[1] - a.odwaga):
                strefa += 1
            continue
        # przegrana
        przegrane += 1
        przegrane_z_rzedu += 1
        czas += a.odrodzenie_s
        czasy["odrodzenie"] += a.odrodzenie_s
        if brama:
            if a.trening > 0:
                minuty = a.trening_min
                punkty = 0.0
                for _ in range(int(minuty * 10)):
                    punkty += a.trening / 10 / (1 + (sum(wytrenowane.values()) + punkty) / a.trening_polowa)
                trenuj(klasa, L, wytrenowane, int(punkty))
                trening_razem += minuty
                czas += minuty * 60
                czasy["trening"] += minuty * 60
            else:
                strefa -= 1
                farmienie = a.farmienie
        elif przegrane_z_rzedu >= 2 and strefa > 0:
            strefa -= 1
            przegrane_z_rzedu = 0


def las(a, klasy, graczy, ziarno):
    wynik = {}
    for k in klasy:
        los = random.Random("%s-%d" % (k, ziarno))
        gr = [jeden_gracz(k, los, a) for _ in range(graczy)]
        wynik[k] = gr
    return wynik


def kwantyl(xs, q):
    xs = sorted(xs)
    i = (len(xs) - 1) * q
    lo, hi = int(math.floor(i)), int(math.ceil(i))
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)


def podsumuj(gr):
    ok = [g for g in gr if g is not None]
    t = [g["czas"] / 60 for g in ok]
    return {"n": len(gr), "ukonczone": len(ok), "mediana": statistics.median(t), "p10": kwantyl(t, 0.1),
            "p90": kwantyl(t, 0.9), "przegrane": statistics.median(g["przegrane"] for g in ok),
            "przegrane_p90": kwantyl([g["przegrane"] for g in ok], 0.9),
            "bez_przegranej": 100.0 * sum(1 for g in ok if g["przegrane"] == 0) / len(ok),
            "poziom": statistics.median(g["poziom"] for g in ok), "walki": statistics.median(g["walki"] for g in ok),
            "proby_bram": statistics.median(g["proby_bram"] for g in ok),
            "udzial_walk": 100 * statistics.mean(g["czasy"]["walki"] for g in ok) / statistics.mean(g["czas"] for g in ok),
            "trening": statistics.median(g["trening"] for g in ok), "wytrenowane": statistics.median(g["wytrenowane"] for g in ok)}


def cykl_na_poziomie(L, a, ziaren=60):
    """Model ogolny: sredni czas jednego cyklu (walka + dojscie + przegrane) i doswiadczenie za walke na poziomie L —
    gracz wzorcowy (srednia klas) kontra zwykle potwory lasu przeskalowane do jego poziomu (zastepczo)."""
    t, xp, n = 0.0, 0.0, 0
    zwykle = [p for p, *_ in PRZEGRODY[:3]]
    for k in wzorcowe.KLASY:
        g = wzorcowe.postac(k, L)
        for p in zwykle:
            miedzy = next(x[3] for x in PRZEGRODY if x[0] == p)
            for z in range(1, ziaren + 1):
                w = silnik.symuluj(g, {"potwor": p, "poziom": L}, z)
                t += w["czas"] / a.tempo_odtwarzania + miedzy + (a.odrodzenie_s if w["wynik"] != "wygrana" else 0)
                xp += w["lup"]["doswiadczenie"]
                n += 1
    return t / n, xp / n


def model_biomow(a, plan):
    """Na jakim poziomie gracz konczy kolejne biomy przy krzywej A*L^B, jesli kazdy biom trwa tyle, ile w planie."""
    cykle = {}

    def cykl(L):
        klucz = min(L, 200)
        if klucz not in cykle:
            cykle[klucz] = cykl_na_poziomie(klucz, a, ziaren=20)
        return cykle[klucz]
    granice = []
    suma = 0
    for m in plan:
        suma += m
        granice.append(suma * 60)
    L, xp_w, czas, walki = 1, 0.0, 0.0, 0.0
    wynik = []
    i = 0
    poz_start, walki_start = 1, 0.0
    while i < len(granice):
        t_c, xp_c = cykl(L)
        potrzeba = xp_do_nastepnego(L, a.xp_a, a.xp_b) - xp_w
        n = potrzeba / xp_c
        if czas + n * t_c <= granice[i]:
            czas += n * t_c
            walki += n
            xp_w = 0.0
            L += 1
            continue
        # biom konczy sie w trakcie poziomu L
        reszta = (granice[i] - czas) / t_c
        xp_w += reszta * xp_c
        walki += reszta
        czas = granice[i]
        wynik.append({"biom": NAZWY_BIOMOW[i] if i < len(NAZWY_BIOMOW) else str(i + 1), "minuty": plan[i],
                      "poziom_start": poz_start, "poziom_koniec": L, "poziomy": L - poz_start,
                      "walki": walki - walki_start})
        poz_start, walki_start = L, walki
        i += 1
    return wynik, L


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Model tempa: las i biomy do 8. (propozycja liczb)")
    ap.add_argument("--graczy", type=int, default=200, help="symulowanych graczy na klase")
    ap.add_argument("--ziarno", type=int, default=1)
    ap.add_argument("--xp-a", type=float, default=None, help="krzywa: doswiadczenie na poziom = A * L^B")
    ap.add_argument("--xp-b", type=float, default=1.6)
    ap.add_argument("--cel-lasu", type=float, default=30.0, help="cel mediany czasu lasu w minutach (do --dopasuj)")
    ap.add_argument("--dopasuj", action="store_true", help="dobierz A pod --cel-lasu (bisekcja, mniejsza proba)")
    ap.add_argument("--tempo-odtwarzania", type=float, default=1.0, help="1 = walka w tempie x1 (najdluzej)")
    ap.add_argument("--odrodzenie-s", type=float, default=15.0, help="odrodzenie gracza i powrot po przegranej")
    ap.add_argument("--punkty-s", type=float, default=8.0, help="rozdanie punktow po awansie")
    ap.add_argument("--farmienie", type=int, default=3, help="walk w poprzedniej przegrodzie po przegranej z brama")
    ap.add_argument("--odwaga", type=int, default=0, help="ile poziomow ponizej bramy gracz juz ja probuje")
    ap.add_argument("--trening", type=float, default=0.0, help="Training Center: punkty statystyk na minute (0 = brak)")
    ap.add_argument("--trening-min", type=float, default=2.0, help="ile minut trenuje po przegranej z brama")
    ap.add_argument("--trening-polowa", type=float, default=40.0, help="po tylu wytrenowanych punktach tempo spada o polowe")
    ap.add_argument("--limit-min", type=float, default=240.0, help="gracz, ktory nie skonczy lasu w tym czasie, odpada")
    ap.add_argument("--plan", default=",".join(map(str, PLAN_ROSNACY)), help="minuty na biomy 1-7")
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    if a.xp_a is None:
        a.xp_a = DOMYSLNE_A
    if a.dopasuj:
        lo, hi = 1.0, 200.0
        for _ in range(12):
            a.xp_a = (lo + hi) / 2
            gr = las(a, wzorcowe.KLASY, max(30, a.graczy // 4), a.ziarno)
            med = statistics.median(g["czas"] / 60 for k in gr for g in gr[k] if g is not None)
            if med < a.cel_lasu:
                lo = a.xp_a
            else:
                hi = a.xp_a
        a.xp_a = round((lo + hi) / 2, 2)
    w = []
    w.append("## Model tempa — propozycja liczb (nie kanon)")
    w.append("")
    w.append("Krzywa doświadczenia: **na poziom L → L+1 potrzeba %s × L^%s** (zaokrąglone). Tempo odtwarzania ×%s, "
             "odrodzenie gracza %s s, rozdanie punktów %s s, farmienie po przegranej z bramą: %d walk, trening: %s."
             % (str(a.xp_a).replace(".", ","), str(a.xp_b).replace(".", ","), str(a.tempo_odtwarzania).replace(".", ","),
                str(a.odrodzenie_s).replace(".", ","), str(a.punkty_s).replace(".", ","), a.farmienie,
                ("%s pkt/min przez %s min po przegranej z bramą, połowa tempa po %s pkt" % (a.trening, a.trening_min, a.trening_polowa)
                 if a.trening > 0 else "brak").replace(".", ",")))
    w.append("")
    w.append("| Poziom | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 15 | 20 | 30 | 50 | 70 |")
    w.append("|---|" + "---:|" * 15)
    w.append("| Doświadczenie do następnego | " + " | ".join(str(xp_do_nastepnego(L, a.xp_a, a.xp_b))
                                                       for L in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 50, 70)) + " |")
    w.append("")
    w.append("Przegrody lasu (propozycja): " + "; ".join("%s poz. %d–%d%s, %d s między walkami" % (
        silnik.PRZECIWNICY[p]["nazwa"], od, do, " (brama)" if br else "", m) for p, od, do, m, br in PRZEGRODY) + ".")
    w.append("")
    gr = las(a, wzorcowe.KLASY, a.graczy, a.ziarno)
    w.append("### Las: czas do pokonania Strażnika Gaju (%d graczy na klasę)" % a.graczy)
    w.append("")
    w.append("| Klasa | Mediana | 10%–90% graczy | Przegrane po drodze (mediana / 90%) | Bez żadnej przegranej | "
             "Poziom przy Strażniku | Walk | Prób bram (troll + strażnik) | Czas samych walk | Trening |")
    w.append("|---|---:|---|---|---:|---:|---:|---:|---:|---|")
    wszyscy = []
    for k in wzorcowe.KLASY:
        s = podsumuj(gr[k])
        wszyscy += [g for g in gr[k] if g is not None]
        w.append("| %s | %s min | %s–%s min | %s / %s | %s | %s | %s | %s | %s | %s |" % (
            silnik.KLASY[k]["nazwa"], f1(s["mediana"]), f1(s["p10"]), f1(s["p90"]), f0(s["przegrane"]),
            f0(s["przegrane_p90"]), f1(s["bez_przegranej"]) + "%", f0(s["poziom"]), f0(s["walki"]), f0(s["proby_bram"]),
            f0(s["udzial_walk"]) + "%", ("%s min, %s pkt" % (f1(s["trening"]), f0(s["wytrenowane"]))) if a.trening > 0 else "—"))
        if s["ukonczone"] < s["n"]:
            w.append("| (%s: %d z %d graczy nie skończyło w %s min) | | | | | | | | | |" % (
                silnik.KLASY[k]["nazwa"], s["n"] - s["ukonczone"], s["n"], f0(a.limit_min)))
    w.append("")
    med = statistics.median(g["czas"] / 60 for g in wszyscy)
    w.append("Wszystkie klasy razem: mediana **%s min**, poziom przy Strażniku **%s**." % (
        f1(med), f0(statistics.median(g["poziom"] for g in wszyscy))))
    w.append("")
    plany = [("rosnący (propozycja)", [float(x) for x in a.plan.split(",")]), ("równy", [600 / 7.0] * 7)]
    for nazwa, plan in plany:
        wyn, L8 = model_biomow(a, plan)
        w.append("### Model biomów 1–7: plan %s, razem %s min" % (nazwa, f0(sum(plan))))
        w.append("")
        w.append("| Biom | Minuty | Poziom na wejściu | Poziom na końcu | Poziomów | Walk (ok.) |")
        w.append("|---|---:|---:|---:|---:|---:|")
        for x in wyn:
            w.append("| %s | %s | %d | %d | %d | %s |" % (x["biom"], f0(x["minuty"]), x["poziom_start"], x["poziom_koniec"],
                                                        x["poziomy"], f0(x["walki"])))
        w.append("")
        w.append("Do 8. biomu (Kryształowy) gracz dochodzi na poziomie **%d**." % L8)
        w.append("")
    w.append("_python -B tools/walka/tempo.py --graczy %d --xp-a %s --xp-b %s --trening %s_" % (
        a.graczy, a.xp_a, a.xp_b, a.trening))
    tekst = "\n".join(w) + "\n"
    print(tekst)
    if a.md:
        with open(a.md, "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst)


def f1(x):
    return ("%.1f" % x).replace(".", ",")


def f0(x):
    return "%.0f" % x


DOMYSLNE_A = 11.71  # dopasowane --dopasuj pod 30 min lasu (silnik v3, 16.11.2026)

if __name__ == "__main__":
    main()
