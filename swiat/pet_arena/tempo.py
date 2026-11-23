#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rachunek tempa Pet Areny (etap 2, bez Studio): kiedy pierwsze kupione jajko, pierwszy Rare, pierwszy Epic.

    python -B swiat/pet_arena/tempo.py [--prob 2000]

Model (przybliżony, do strojenia po graniu): dochód na minutę = za_stopien × średni stopień trzech najlepszych petów
(+ gwiazdki i poziom trenera pomijamy) + wydarzenia (boss co 2 × co_s: pula × szansa pokonania w pojedynkę, złoty pet:
premia + kilka ciosów). za_stopien z symulacji logiki (gracz z Common-ami, odpoczynek 30 s: ok. 150–190 G/min, część to
premie za wybicia). Strategia: najpierw darmowe jajko, potem najdroższe jajko, którego cena ≤ okno_min minut dochodu.
Losowanie rzadkości i peta jak w LogikaPetArena.losujZJajka (te same szanse z ustawienia.json).
"""
import argparse
import json
import os
import random
import statistics
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
ZA_STOPIEN = 150          # G/min na średni stopień drużyny (symulacja logiki, Common-y: ok. 150–190)
SZANSA_BOSSA = 0.6        # samotny gracz pokonuje bossa (pozostali to dzikie pety)
OKNO_MIN = 3.0            # kupuje najdroższe jajko, na które zbiera najwyżej tyle minut


def ustawienia():
    with open(os.path.join(TU, "ustawienia.json"), encoding="utf-8") as f:
        return json.load(f)


def przebieg(U, los, minut=45, krok_s=10):
    pety = U["pety"]
    stopnie = {}
    for P in U["gracz"]["pety_startowe"]:
        stopnie[P] = next(p["stopien"] for p in pety if p["id"] == P)
    J = U["jajka"]
    W = U["wydarzenia"]
    zloto, t = 0.0, 0.0
    pierwsze_kupione = pierwszy_rare = pierwszy_epic = None
    darmowe = True
    nast_wyd, nr_wyd = W["pierwsze_s"], 0
    while t < minut * 60:
        najlepsze = sorted(stopnie.values(), reverse=True)[:3]
        dochod = ZA_STOPIEN * sum(najlepsze) / len(najlepsze)
        zloto += dochod * krok_s / 60
        if t >= nast_wyd:
            if W["kolejnosc"][nr_wyd % 2] == "boss":
                zloto += U["boss"]["pula"] * (1 if los.random() < SZANSA_BOSSA else 0)
            else:
                zloto += U["zloty"]["premia"] * 0.5 + U["zloty"]["za_cios"] * 6
            nr_wyd += 1
            nast_wyd += W["co_s"]
        while True:
            if darmowe:
                nr, cena = 0, 0
            else:
                stac = [i for i, j in enumerate(J) if j["cena"] <= dochod * OKNO_MIN]
                if not stac:
                    break
                nr = max(stac)
                cena = J[nr]["cena"]
                if zloto < cena:
                    break
            zloto -= cena
            x = los.random()
            rz = len(J[nr]["szanse"])
            for i, s in enumerate(J[nr]["szanse"], 1):
                x -= s
                if x < 0:
                    rz = i
                    break
            kandydaci = [p for p in pety if p["stopien"] == rz]
            p = los.choice(kandydaci)
            stopnie[p["id"]] = p["stopien"]
            if not darmowe and pierwsze_kupione is None:
                pierwsze_kupione = t
            darmowe = False
            if rz >= 3 and pierwszy_rare is None:
                pierwszy_rare = t
            if rz >= 4 and pierwszy_epic is None:
                pierwszy_epic = t
        t += krok_s
    return pierwsze_kupione, pierwszy_rare, pierwszy_epic


def mediana_min(w):
    w = [x for x in w if x is not None]
    return round(statistics.median(w) / 60, 1) if w else None


def tabela(U, prob=2000, ziarno=1):
    los = random.Random(ziarno)
    wyniki = [przebieg(U, los) for _ in range(prob)]
    k, r, e = zip(*wyniki)
    return {"pierwsze_kupione_min": mediana_min(k), "pierwszy_rare_min": mediana_min(r), "pierwszy_epic_min": mediana_min(e),
            "rare_do_10_min_proc": round(100 * sum(1 for x in r if x is not None and x <= 600) / prob),
            "epic_do_30_min_proc": round(100 * sum(1 for x in e if x is not None and x <= 1800) / prob)}


def main():
    for s in (sys.stdout,):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--prob", type=int, default=2000)
    a = ap.parse_args()
    print(json.dumps(tabela(ustawienia(), a.prob), ensure_ascii=False))


if __name__ == "__main__":
    main()
