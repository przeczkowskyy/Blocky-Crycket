#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Symulacja walki (walka1) na prawdziwej logice gry (zrodla/LogikaEwolucji.luau w interpreterze luau_mini, bez kulek).

    python -B swiat/ewolucja/testy/walka_sim.py [--pojedynkow 40] [--json]

Drukuje: czas pojedynku równych stadiów (mediana), odsetek wygranych o stadium większego, liczbę ugryzień na zabicie
o dwa stadia mniejszego, czas pokonania bossa na każdym stopniu (gracz na stadium stopnia, z umiejętnościami), oraz
rany na sekundę każdej zdolności na manekinie względem samego BITE (ta sama forma, odnowa wliczona).
Model gracza w pojedynku: oba stworki gryzą od razu, gdy cel jest w zasięgu, z ludzkim opóźnieniem 0–0,35 s po każdym
ciosie (losowe) — bez uników. Losowość: krytyki i opóźnienia. Tych samych funkcji używają testy (test_ewolucji.py).
"""
import argparse
import json
import math
import os
import random
import statistics
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import test_ewolucji as T  # noqa: E402

LM = T.LM
D = T.D
KROK = 0.05


def dane_bez_kulek():
    d = dict(D)
    d["kulkiPoz"] = []
    return LM.do_luau(d)


DB = None


def swiat(ziarno):
    global DB
    if DB is None:
        DB = dane_bez_kulek()
    return T.jeden("nowyStan", DB, T.Los(ziarno))


def stworek(S, forma, x, z, slot=0):
    b = T.byt(S, slot, forma, x, z)
    T.ustaw(b, tarczaDo=0, laskaDo=0, myslDo=1e9, maxForma=forma)
    return b


def pojedynek(forma_a, forma_b, ziarno, maks_s=40.0):
    """Dwa stworki (boty bez myślenia) idą na siebie i gryzą; zwraca (zwycięzca 'a'/'b'/None, czas od pierwszego ciosu)."""
    los = random.Random(ziarno)
    S = swiat(ziarno * 7 + 1)
    ra, rb = D["formy"][forma_a - 1]["r"], D["formy"][forma_b - 1]["r"]
    a = stworek(S, forma_a, 0.0, 0.0)
    b = stworek(S, forma_b, ra + rb + 1.0, 0.0)
    T.ustaw(a, cel=T.g(b, "id"), kier=math.pi / 2)
    T.ustaw(b, cel=T.g(a, "id"), kier=-math.pi / 2)
    # kto zaczyna — losowo (ludzie nie startują równo)
    T.ustaw(a, gryzGotowy=los.random() * 0.4)
    T.ustaw(b, gryzGotowy=los.random() * 0.4)
    t, t0 = 0.0, None
    gotA, gotB = 0.0, 0.0
    while t < maks_s:
        for p, q in ((a, b), (b, a)):
            dx, dz = T.g(q, "x") - T.g(p, "x"), T.g(q, "z") - T.g(p, "z")
            d = max(0.01, math.hypot(dx, dz))
            T.ustaw(p, wx=dx / d, wz=dz / d)
        zd = T.krok(S, 1, KROK)
        t += KROK
        for z in zd:
            if z["t"] == "gryz":
                if t0 is None and z.get("trafil"):
                    t0 = t
                # ludzkie opóźnienie po ciosie
                kto = a if z["id"] == T.g(a, "id") else b
                T.ustaw(kto, gryzGotowy=T.g(kto, "gryzGotowy") + los.random() * 0.35)
            if z["t"] == "zjedz":
                return ("a" if z["a"] == T.g(a, "id") else "b"), t - (t0 or t)
    return None, maks_s


def ugryzien_na_zabicie(forma_a, forma_b):
    """Ile ugryzień (łańcuch od pierwszego ciosu, bez krytyków) potrzeba, by forma_a zabiła forma_b."""
    W = D["walka"]
    sila = W["gryz_baza"] * W["gryz_wzrost"] ** (forma_a - 1)
    roz = W["rozmiar_x"][max(-3, min(3, forma_a - forma_b)) + 3]
    hp = W["hp_baza"] * W["hp_wzrost"] ** (forma_b - 1)
    n, k = 0, 0
    while hp > 0 and n < 99:
        hp -= max(1, math.floor(sila * W["lancuch_x"][k] * roz + 0.5))
        k = (k + 1) % 3
        n += 1
    return n


def manekin(forma, linia, czas_s=30.0, ziarno=5):
    """Rany na sekundę na stojącym manekinie (ta sama forma): linia None = sam BITE, inaczej tylko ta zdolność."""
    S = swiat(ziarno)
    r = D["formy"][forma - 1]["r"]
    A = next((x for x in D["zdolnosci"].get(linia or "", []) if x["od"] == forma), None)
    mx = A["d"] if A and A["typ"] in ("lot", "meteor") else r * 2 + 0.6
    a = stworek(S, forma, 0.0, 0.0)
    m = stworek(S, forma, mx, 0.0)
    T.ustaw(a, kier=math.pi / 2, cel=T.g(m, "id"))
    suma, t = 0.0, 0.0
    lista = LM.Tabela()
    while t < czas_s:
        T.ustaw(a, wx=0.0, wz=0.0, kier=math.pi / 2)
        T.ustaw(m, x=mx, z=0.0, vx=0.0, vz=0.0, ogluszonyDo=0, hp=1e9, gryzGotowy=1e9)
        if a.get("skok") is None:
            T.ustaw(a, x=0.0, z=0.0)
        if linia:
            T.ustaw(a, gryzGotowy=1e9)
            lista = LM.Tabela()
            T.jeden("zdolnosc", S, a, linia, lista)
            zd = LM.z_luau(lista, True)
        else:
            zd = []
        zd += T.krok(S, 1, KROK)
        t += KROK
        for z in zd:
            if z["t"] == "rana" and z["id"] == T.g(m, "id"):
                suma += z["ile"]
            if z["t"] == "rana" and z["id"] == T.g(m, "id") and z.get("kr"):
                # bez krytyków w porównaniu (oba z tą samą szansą)
                suma -= z["ile"] - z["ile"] / D["walka"]["kryt_x"]
    return suma / czas_s


def boss_walka(stopien, forma, szczeka, ziarno, maks_s=120.0):
    """Gracz (stadium forma, Szczęka) z umiejętnościami przeciw bossowi na stopniu; zwraca (wygrał, czas, życie gracza na końcu)."""
    los = random.Random(ziarno)
    S = swiat(ziarno * 3 + 2)
    boss = T.jeden("dodajBossa", S)
    T.ustaw(S, bossStopien=stopien)
    hpB = D["boss"]["stopnie_hp"][stopien - 1]
    T.ustaw(boss, hp=float(hpB), hpMaks=float(hpB))
    bx, bz = T.g(boss, "x"), T.g(boss, "z")
    rB = D["formy"][D["boss"]["forma"] - 1]["r"]
    r = D["formy"][forma - 1]["r"]
    gr = T.byt(S, 1, forma, bx + rB + r + 1, bz)
    T.ustaw(gr, tarczaDo=0, laskaDo=0, maxForma=forma)
    gr.get("poziomy").set("szczeka", float(szczeka))
    t = 0.0
    while t < maks_s:
        dx, dz = T.g(boss, "x") - T.g(gr, "x"), T.g(boss, "z") - T.g(gr, "z")
        d = max(0.01, math.hypot(dx, dz))
        hp = T.g(gr, "hp") / T.g(gr, "hpMaks")
        if hp < 0.3 and d < rB + r + 12:
            # gracz odchodzi, gdy mało życia (regeneracja), wraca po chwili
            T.ustaw(gr, wx=-dx / d, wz=-dz / d)
        else:
            T.ustaw(gr, wx=dx / d, wz=dz / d)
            lista = LM.Tabela()
            if los.random() < 0.5:
                T.jeden("gryz", S, gr, lista)
            for linia in ("ogien", "moc"):
                if los.random() < 0.1:
                    T.jeden("zdolnosc", S, gr, linia, lista)
            for z in LM.z_luau(lista, True):
                if z["t"] == "boss_pokonany":
                    return True, t, hp
        zd = T.krok(S, 1, KROK)
        t += KROK
        for z in zd:
            if z["t"] == "boss_pokonany":
                return True, t, T.g(gr, "hp") / T.g(gr, "hpMaks")
            if z["t"] == "zjedz" and z["b"] == T.g(gr, "id"):
                return False, t, 0.0
    return False, maks_s, T.g(gr, "hp") / T.g(gr, "hpMaks")


def tabela(pojedynkow=40):
    W = {"rowne": {}, "o_jedno": {}, "o_dwa_ugryzien": {}, "boss": {}, "zdolnosci": {}}
    nf = len(D["formy"])
    for f in range(1, nf + 1):
        czasy = [pojedynek(f, f, 100 + i)[1] for i in range(pojedynkow // 2)]
        W["rowne"][f] = round(statistics.median(czasy), 2)
    for f in range(2, nf + 1):
        wyg = 0
        for i in range(pojedynkow):
            kto, _ = pojedynek(f, f - 1, 500 + i)
            wyg += kto == "a"
        W["o_jedno"][f] = round(wyg / pojedynkow, 2)
    for f in range(3, nf + 1):
        W["o_dwa_ugryzien"][f] = ugryzien_na_zabicie(f, f - 2)
    for st in range(1, len(D["boss"]["stopnie_hp"]) + 1):
        forma, szczeka = min(nf, 3 + st), min(5, st)
        wyniki = [boss_walka(st, forma, szczeka, 900 + i) for i in range(6)]
        W["boss"][st] = {"forma": forma, "szczeka": szczeka, "wygrane": sum(1 for w in wyniki if w[0]),
                         "czas_s": round(statistics.median([w[1] for w in wyniki if w[0]] or [0]), 1),
                         "zycie_gracza": round(statistics.median([w[2] for w in wyniki if w[0]] or [0]), 2)}
    for linia in ("ogien", "moc"):
        for A in D["zdolnosci"][linia]:
            f = A["od"]
            bite = manekin(f, None)
            ab = manekin(f, linia)
            W["zdolnosci"][A["id"]] = {"forma": f, "bite_dps": round(bite, 1), "dps": round(ab, 1), "x_bite": round(ab / bite, 2)}
    return W


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pojedynkow", type=int, default=40)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    W = tabela(a.pojedynkow)
    if a.json:
        print(json.dumps(W, ensure_ascii=False))
        return
    nazwy = [f["nazwa"] for f in D["formy"]]
    print("Walka (walka1) — symulacja na logice gry, %d pojedynków na parę" % a.pojedynkow)
    print("%-15s %10s %12s %12s" % ("stadium", "równe: s", "o 1 wyżej", "o 2: ugryzień"))
    for f in range(1, len(nazwy) + 1):
        print("%-15s %10s %12s %12s" % (nazwy[f - 1], W["rowne"].get(f, "-"), W["o_jedno"].get(f, "-"), W["o_dwa_ugryzien"].get(f, "-")))
    print("Boss (gracz na stadium 3 + stopień, Szczęka = stopień, BITE + FIRE + POWER, 6 prób):")
    for st, w in W["boss"].items():
        print("  stopień %d: stadium %d, Szczęka %d — wygrane %d/6, mediana %.1f s, życie gracza na końcu %d%%" % (
            st, w["forma"], w["szczeka"], w["wygrane"], w["czas_s"], w["zycie_gracza"] * 100))
    print("Zdolności na manekinie (rany/s względem samego BITE tej formy):")
    for k, w in W["zdolnosci"].items():
        print("  %-8s stadium %d: %5.1f/s vs BITE %5.1f/s = x%.2f" % (k, w["forma"], w["dps"], w["bite_dps"], w["x_bite"]))


if __name__ == "__main__":
    main()
