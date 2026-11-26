#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zagroda petów (25.11.2026, sesja główna; propozycja — LICZBY ROBOCZE, NIE kanon): ile Rybek na godzinę daje
zagroda na każdym poziomie (2 / 4 / 6 / 8 miejsc) w porównaniu z Rybkami z walk, ile minut walk kosztuje ulepszenie
i po ilu godzinach w grze się zwraca. Cel: zagroda ma być miłym dodatkiem, nie głównym źródłem Rybek.

    python -B swiat/pety_proba/ekonomia_zagrody.py                 # Markdown na ekran (30 graczy na klasę)
    python -B swiat/pety_proba/ekonomia_zagrody.py --graczy 100 --md wynik.md

Rybki z walk: te same symulacje graczy co ekonomia_jajek.py (las-pas do Strażnika Gaju, Bagno do Strażnika Topieli,
Dżungla do Węża Stu Lian; łup z silnika tools/walka/silnik.py, gracz jak w swiat/stan_gracza/symulacja_lasu.py) —
mediana Rybek na godzinę walki w biomie (od wejścia do wygranej ze strażnikiem). Premii petów i kowala nie liczę, a
symulacja nie zna D-107 (walka bez przestojów) w całości — to przybliżenie, nie pomiar z gry.

Zagroda „typowa”: gracz u strażnika biomu ma jajka kupione za całe Rybki z tego biomu (stała cena jajka, jak
ekonomia_jajek.zakupy) i z wcześniejszych biomów; pety losowane z jawnych szans (1000 losowań), najrzadszy idzie za
graczem, w zagrodzie stoją kolejne według wyboru domyślnego (LogikaPetow.w_zagrodzie). „Najwięcej”: najlepsze pety
dostępne do tego biomu (bez jednego za graczem). Rybki z zagrody liczą się tylko w grze (bez przychodu offline).
"""
import argparse
import os
import random
import statistics
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
if TU not in sys.path:
    sys.path.insert(0, TU)
import dane_petow as DP  # noqa: E402
import ekonomia_jajek as EJ  # noqa: E402
import logika_petow as LP  # noqa: E402

BIOMY = [("las", "Las (do Strażnika Gaju)"), ("bagno", "Bagno (do Strażnika Topieli)"),
         ("dzungla", "Dżungla (do Węża Stu Lian)")]
LOSOWAN = 1000


def _gracze(biom, n):
    if biom == "las":
        return EJ.wszyscy_gracze(n, z_wygrana=True)
    if biom == "bagno":
        return EJ.wszyscy_gracze_bagna(n, z_wygrana=True)[0]
    return EJ.wszyscy_gracze_dzungli(n, z_wygrana=True)[0]


def _koniec(os_czasu, wygrana):
    return wygrana if wygrana is not None else (os_czasu[-1][0] if os_czasu else 0.0)


def walki(biom, n):
    """→ {rybki_h (mediana), minut (mediana czasu biomu), jajek (mediana jajek biomu za całe Rybki), rybki_min}."""
    gr = _gracze(biom, n)
    stawki, minuty, jajka = [], [], []
    D = DP.podstawa()
    j = LP.jajko_krainy(D, biom)
    wariant = {"tryb": "stala", "cena": j["cena"]["stala"]}
    for os_czasu, wygrana in gr:
        t = _koniec(os_czasu, wygrana)
        if t <= 60:
            continue
        stawki.append(EJ.zloto_do(os_czasu, t) / t * 3600.0)
        minuty.append(t / 60.0)
        jajka.append(EJ.jajek_do(os_czasu, wariant, t))
    return {"rybki_h": statistics.median(stawki), "minut": statistics.median(minuty),
            "jajek": int(statistics.median(jajka)), "graczy": len(stawki)}


def typowa(D, jajek_biomow, miejsc, los):
    """Mediana Rybek/s zagrody: jajek_biomow = [(jajko, ile)], najrzadszy pet za graczem, reszta według wyboru
    domyślnego na `miejsc` miejscach."""
    wyniki = []
    for _ in range(LOSOWAN):
        kopie = {}
        for j, ile in jajek_biomow:
            for _ in range(ile):
                p = LP.losuj(D, j, los.random())
                kopie[p] = kopie.get(p, 0) + 1
        naj = LP.w_zagrodzie(D, kopie, None, None, 1)
        akt = naj[0] if naj else None
        wyniki.append(LP.przychod_s(D, LP.w_zagrodzie(D, kopie, akt, None, miejsc)))
    return statistics.median(wyniki)


def najwiecej(D, jajka, miejsc):
    pula = [x for j in jajka for x in j["pula"]]
    kopie = {x: 1 for x in pula}
    naj = LP.w_zagrodzie(D, kopie, None, None, 1)
    return LP.przychod_s(D, LP.w_zagrodzie(D, kopie, naj[0], None, miejsc))


def rachunek(n=30, ziarno=1):
    D = DP.podstawa()
    poz = D["zagroda"]["poziomy"]
    los = random.Random("zagroda-%d" % ziarno)
    W, wiersze, jajka_do = {}, [], []
    for biom, nazwa in BIOMY:
        w = walki(biom, n)
        W[biom] = w
        j = LP.jajko_krainy(D, biom)
        jajka_do.append((j, max(1, w["jajek"])))
        komorki = []
        for p in poz:
            t = typowa(D, jajka_do, p["miejsc"], los) * 3600.0
            m = najwiecej(D, [x for x, _ in jajka_do], p["miejsc"]) * 3600.0
            komorki.append((t, m))
        wiersze.append((biom, nazwa, w, komorki))
    return D, W, wiersze


def _l(v, n=0):
    s = ("%." + str(n) + "f") % v
    return s.replace(".", ",")


def markdown(D, W, wiersze, n):
    poz = D["zagroda"]["poziomy"]
    Z = D["zagroda"]
    o = []
    o.append("### Stawki petów w zagrodzie (Rybki na sekundę; liczby robocze)")
    o.append("")
    o.append("| Rzadkość | " + " | ".join("%s (×%s)" % (j["id"], _l(Z["mnozniki_jajek"][j["id"]], 1)) for j in D["jajka"])
             + " |")
    o.append("|---|" + "---:|" * len(D["jajka"]))
    for r in D["rzadkosci"]:
        kom = []
        for j in D["jajka"]:
            p = next(LP.pet(D, x) for x in j["pula"] if LP.pet(D, x)["rzadkosc"] == r["id"])
            kom.append("%s: %s/s = %s/h" % (p["nazwa"], _l(p["rybki_s"], 3), _l(p["rybki_s"] * 3600)))
        o.append("| %s | %s |" % (r["nazwa"], " | ".join(kom)))
    o.append("")
    o.append("### Rybki z walk (symulacja, %d graczy na klasę, mediany)" % n)
    o.append("")
    o.append("| Biom | czas biomu | Rybki/h z walk | jajek biomu za całe Rybki |")
    o.append("|---|---:|---:|---:|")
    for biom, nazwa, w, _k in wiersze:
        o.append("| %s | %s min | %s | %d |" % (nazwa, _l(w["minut"]), _l(w["rybki_h"]), w["jajek"]))
    o.append("")
    o.append("### Zagroda pełna na każdym poziomie: Rybki/h (typowa · najwięcej) i udział względem walk")
    o.append("")
    o.append("| Biom | " + " | ".join("%d miejsc" % p["miejsc"] for p in poz) + " |")
    o.append("|---|" + "---|" * len(poz))
    for biom, nazwa, w, kom in wiersze:
        cz = []
        for t, m in kom:
            cz.append("%s (%s%%) · %s (%s%%)" % (_l(t), _l(100 * t / w["rybki_h"]), _l(m), _l(100 * m / w["rybki_h"])))
        o.append("| %s | %s |" % (nazwa, " | ".join(cz)))
    o.append("")
    o.append("### Ulepszenia: koszt w minutach walk i zwrot (typowa zagroda)")
    o.append("")
    o.append("| Ulepszenie | cena | minut walk w lesie / Bagnie / Dżungli | zwrot w godzinach gry (las / Bagno / Dżungla) |")
    o.append("|---|---:|---|---|")
    for i in range(1, len(poz)):
        c = poz[i]["cena"]
        minuty = " / ".join(_l(c / (w["rybki_h"] / 60.0), 1) for _b, _n, w, _k in wiersze)
        zwroty = []
        for _b, _n, w, kom in wiersze:
            dodatek = kom[i][0] - kom[i - 1][0]
            zwroty.append(_l(c / dodatek, 1) if dodatek > 0 else "—")
        o.append("| %d → %d miejsc | %d | %s | %s |" % (poz[i - 1]["miejsc"], poz[i]["miejsc"], c, minuty,
                                                       " / ".join(zwroty)))
    return "\n".join(o) + "\n"


def main(argv):
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--graczy", type=int, default=30, help="graczy na klasę")
    ap.add_argument("--ziarno", type=int, default=1)
    ap.add_argument("--md", default=None)
    a = ap.parse_args(argv)
    D, W, wiersze = rachunek(a.graczy, a.ziarno)
    tekst = markdown(D, W, wiersze, a.graczy)
    print(tekst)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write(tekst)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
