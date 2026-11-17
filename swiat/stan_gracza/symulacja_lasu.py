#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Czy gra da się zacząć: bohater z danych gracza (prawdziwy poziom) w przegrodach lasu-pasa. Propozycja liczb, NIE kanon.

    python -B swiat/stan_gracza/symulacja_lasu.py                  # tabela szans + przejście lasu, Markdown na ekran
    python -B swiat/stan_gracza/symulacja_lasu.py --graczy 300 --ziaren 300 --md wynik.md
    python -B swiat/stan_gracza/symulacja_lasu.py --tempo 2        # walki oglądane w tempie ×2

Liczy pojedynczo (bez wielu procesów). Silnik: tools/walka/silnik.py (port w Pythonie, zgodny z Luau w Studio
592/592 dzienników). Bohater: logika_stanu.opis_bohatera = to samo, co Sygnaly/Bohater w Studio przy włączonych
StatystykiKlasy i bez treningu (rozkład klasy dla puli poziomu; test_stanu.py pilnuje równości z wzorcowe.postac).
Przegrody: swiat/las_pas_gra/zrodla/DanePotworowPasa.luau (wczytane interpreterem luau_mini — jedno źródło).
Krzywa doświadczenia i awans: zrodla/DaneStanu.luau (dane.py, = tools/walka/tempo.py).

CZĘŚĆ 1 — szansa wygranej bohatera na poziomie L z potworem przegrody (poziom potwora losowy z zakresu przegrody).
CZĘŚĆ 2 — przejście lasu gracz po graczu (polityka jawna, jak w tools/walka/tempo.py, ale na prawdziwych przegrodach):
  • start na 1. poziomie w pierwszej przegrodzie; walczy z potworem przegrody o poziomie nie wyższym niż własny + 1;
  • idzie dalej, gdy jego poziom ≥ najniższy poziom następnej przegrody; po dwóch przegranych z rzędu cofa się o jedną;
  • Leśny Troll (jeden, wraca 150 s po wygranej): gdy go nie ma, gracz walczy z wilkami poprzedniej przegrody;
  • Strażnik: próbuje od jego poziomu; po przegranej wraca o przegrodę na ZAPAS_FARMY walk i próbuje znowu;
  • czas = walka (dziennik silnika ÷ tempo) + ekran wyniku + dojście do następnego potwora + przejścia między
    przegrodami (16 studów/s) + przelot kamery przy pierwszym wejściu. Przegrana nic nie zabiera, daje 20% XP.
"""
import argparse
import math
import os
import random
import statistics
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
WALKA = os.path.join(REPO, "tools", "walka")
for _s in (TU, WALKA):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import dane as DANE  # noqa: E402
import logika_stanu as LS  # noqa: E402
import luau_mini as LM  # noqa: E402
import silnik  # noqa: E402

PLIK_PRZEGROD = os.path.join(REPO, "swiat", "las_pas_gra", "zrodla", "DanePotworowPasa.luau")
PLIK_PASA = os.path.join(REPO, "swiat", "las_pas_gra", "zrodla", "DanePasa.luau")
PREDKOSC = 16.0          # studów/s — domyślny WalkSpeed postaci Roblox
EKRAN_WYNIKU = 3.0       # s — panel wyniku i powrót do lasu po walce (założenie)
# s między walkami w przegrodzie: dojście do następnego potwora i E (założenie; jak tools/walka/tempo.py, Strażnik stoi)
DOJSCIE = {"lesny_slime": 8, "muchomornik": 10, "cierniowy_wilk": 10, "lesny_troll": 15, "straznik_lasu": 6}
ZAPAS_FARMY = 3          # walk w poprzedniej przegrodzie po przegranej ze Strażnikiem (jak tempo.py --farmienie)
LIMIT_MIN = 240.0
CEL_LASU_MIN = 30.0      # plan rosnący z tools/walka/tempo.py (Las ok. 30 min) — propozycja, nie kanon


def wczytaj_luau(sciezka):
    it = LM.Interpreter()
    rs = LM.Tabela()
    rs.set("IsStudio", lambda _s: True)
    game = LM.Tabela()
    game.set("GetService", lambda _s, _n: rs)
    it.globalne.z["game"] = game
    with open(sciezka, encoding="utf-8") as f:
        return LM.z_luau(it.wykonaj(f.read(), os.path.basename(sciezka))[0])


def przegrody():
    d = wczytaj_luau(PLIK_PRZEGROD)
    w = []
    for s in d["strefy"]:
        w.append({"id": s["id"], "gatunek": s["gatunek"], "od": s["poziomy"][0], "do": s["poziomy"][1],
                  "x": s["srodek"][0], "straznik": s["straznik"] is True, "odrodzenie": s["odrodzenieS"],
                  "stale": s.get("odrodzenieStale") is True, "naraz": s["naraz"]})
    return w


def przybycie_i_przelot():
    d = wczytaj_luau(PLIK_PASA)
    return d["przybycie"]["punkt"][0], d["przelot"]["czas"]


def bohater(D, klasa, L):
    st = LS.rozdziel(D, D["rozklady"][klasa], LS.pula(D, L))
    return LS.opis_bohatera(D, klasa, L, st)


# ------------------------------------------------------------------------------------------------ część 1
def szanse(D, P, poziomy, ziaren, ziarno):
    los = random.Random(ziarno)
    w = {}
    for k in D["klasy"]:
        for L in poziomy:
            g = bohater(D, k, L)
            for p in P:
                wyg = 0
                for _ in range(ziaren):
                    pz = los.randint(p["od"], p["do"])
                    r = silnik.symuluj(g, {"potwor": p["gatunek"], "poziom": pz}, los.randrange(1, 2 ** 31 - 1))
                    wyg += r["wynik"] == "wygrana"
                w[(k, L, p["id"])] = 100.0 * wyg / ziaren
    return w


# ------------------------------------------------------------------------------------------------ część 2
def jeden_gracz(D, P, klasa, los, a, x0, przelot):
    L, xp, czas = 1, 0, przelot + abs(P[0]["x"] - x0) / PREDKOSC
    i = 0
    walki = przegrane = z_rzedu = proby_straznika = 0
    farma = 0
    troll_od = 0.0
    przybycie = {P[0]["id"]: 1}
    pierwsze = {}  # id przegrody → [wyniki trzech pierwszych walk po wejściu]
    t_walk = 0.0
    while True:
        if czas > LIMIT_MIN * 60:
            return None
        p = P[i]
        cel = p
        if p["gatunek"] == "lesny_troll" and czas < troll_od:
            cel = P[i - 1]  # troll jeszcze nie wrócił — wilki z poprzedniej przegrody
        hi = cel["do"] if cel["straznik"] else max(cel["od"], min(cel["do"], L + 1))
        pz = los.randint(cel["od"], hi)
        r = silnik.symuluj(bohater(D, klasa, L), {"potwor": cel["gatunek"], "poziom": pz}, los.randrange(1, 2 ** 31 - 1))
        walki += 1
        t = r["czas"] / a.tempo
        t_walk += t
        czas += t + EKRAN_WYNIKU + DOJSCIE[cel["gatunek"]]
        wygrana = r["wynik"] == "wygrana"
        if cel is p and len(pierwsze.setdefault(p["id"], [])) < 3:
            pierwsze[p["id"]].append(wygrana)
        L, xp, _ = LS.awans(D, L, xp, r["lup"]["doswiadczenie"])
        if p["straznik"]:
            proby_straznika += 1
        if wygrana:
            z_rzedu = 0
            if p["straznik"]:
                return {"czas": czas, "poziom": L, "walki": walki, "przegrane": przegrane, "proby": proby_straznika,
                        "przybycie": przybycie, "pierwsze": pierwsze, "walka_s": t_walk}
            if cel is p and p["gatunek"] == "lesny_troll":
                troll_od = czas + p["odrodzenie"]
            if farma > 0:
                farma -= 1
                if farma == 0:
                    czas += abs(P[i + 1]["x"] - p["x"]) / PREDKOSC
                    i += 1
                continue
            if i + 1 < len(P) and L >= P[i + 1]["od"]:
                czas += abs(P[i + 1]["x"] - p["x"]) / PREDKOSC
                i += 1
                przybycie.setdefault(P[i]["id"], L)
            continue
        przegrane += 1
        z_rzedu += 1
        if p["straznik"]:
            czas += abs(P[i - 1]["x"] - p["x"]) / PREDKOSC
            i -= 1
            farma = ZAPAS_FARMY
        elif z_rzedu >= 2 and i > 0:
            czas += abs(P[i - 1]["x"] - p["x"]) / PREDKOSC
            i -= 1
            z_rzedu = 0


def kwantyl(xs, q):
    xs = sorted(xs)
    j = (len(xs) - 1) * q
    lo, hi = int(math.floor(j)), int(math.ceil(j))
    return xs[lo] + (xs[hi] - xs[lo]) * (j - lo)


def f1(x):
    return ("%.1f" % x).replace(".", ",")


def f0(x):
    return "%.0f" % x


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Bohater z danych gracza w lesie-pasie: szanse i czas do Strażnika")
    ap.add_argument("--graczy", type=int, default=300, help="symulowanych graczy na klasę (część 2)")
    ap.add_argument("--ziaren", type=int, default=300, help="walk na komórkę tabeli szans (część 1)")
    ap.add_argument("--ziarno", type=int, default=1)
    ap.add_argument("--tempo", type=float, default=1.0, help="tempo oglądania walk (1 = ×1, najdłużej)")
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    t0 = time.time()
    _, D = DANE.dane_z_przypadkami()
    P = przegrody()
    x0, przelot = przybycie_i_przelot()
    w = []
    w.append("## Bohater z danych gracza w lesie-pasie — propozycja liczb (nie kanon)")
    w.append("")
    w.append("Krzywa doświadczenia %s × L^%s (do następnego poziomu: %s). Bohater = rozkład klasy dla puli poziomu, "
             "bez treningu i drzewka; sloty %s." % (
                 f1(D["krzywa"]["a"]), f1(D["krzywa"]["b"]),
                 ", ".join("L%d→%d" % (L, LS.xp_do_nastepnego(D, L)) for L in (1, 2, 3, 5, 8, 10)),
                 ", ".join("%d od poz. %d" % (s["n"], s["od"]) for s in reversed(D["sloty"]))))
    w.append("")
    w.append("Przegrody (DanePotworowPasa.luau): " + "; ".join(
        "%s %s poz. %d–%d" % (p["id"], silnik.PRZECIWNICY[p["gatunek"]]["nazwa"], p["od"], p["do"]) for p in P) + ".")
    w.append("")
    poziomy = list(range(1, 13))
    sz = szanse(D, P, poziomy, a.ziaren, a.ziarno)
    w.append("### 1. Szansa wygranej (%%, %d walk na komórkę), bohater na poziomie L" % a.ziaren)
    w.append("")
    for k in D["klasy"]:
        w.append("**%s**" % D["nazwy_klas"][k])
        w.append("")
        w.append("| Przegroda | " + " | ".join("L%d" % L for L in poziomy) + " |")
        w.append("|---|" + "---:|" * len(poziomy))
        for p in P:
            w.append("| %s (poz. %d–%d) | " % (p["id"], p["od"], p["do"]) + " | ".join(
                f0(sz[(k, L, p["id"])]) for L in poziomy) + " |")
        w.append("")
    w.append("### 2. Przejście lasu do wygranej ze Strażnikiem (%d graczy na klasę, tempo ×%s)" % (a.graczy, f1(a.tempo)))
    w.append("")
    w.append("| Klasa | Mediana | 10%–90% graczy | Przegrane (mediana / 90%) | Bez przegranej | Poziom przy Strażniku | "
             "Walk | Prób Strażnika | Czas walk | Nie skończyło w 240 min |")
    w.append("|---|---:|---|---|---:|---:|---:|---:|---:|---:|")
    wszyscy = []
    przyb = {p["id"]: [] for p in P}
    pierwsze = {p["id"]: [] for p in P}
    for k in D["klasy"]:
        los = random.Random("%s-%d" % (k, a.ziarno))
        gr = [jeden_gracz(D, P, k, los, a, x0, przelot) for _ in range(a.graczy)]
        ok = [g for g in gr if g is not None]
        wszyscy += ok
        for g in ok:
            for pid, L in g["przybycie"].items():
                przyb[pid].append(L)
            for pid, wyn in g["pierwsze"].items():
                pierwsze[pid] += wyn
        t = [g["czas"] / 60 for g in ok]
        w.append("| %s | %s min | %s–%s min | %s / %s | %s%% | %s | %s | %s | %s%% | %d |" % (
            D["nazwy_klas"][k], f1(statistics.median(t)), f1(kwantyl(t, 0.1)), f1(kwantyl(t, 0.9)),
            f0(statistics.median(g["przegrane"] for g in ok)), f0(kwantyl([g["przegrane"] for g in ok], 0.9)),
            f0(100.0 * sum(1 for g in ok if g["przegrane"] == 0) / len(ok)), f0(statistics.median(g["poziom"] for g in ok)),
            f0(statistics.median(g["walki"] for g in ok)), f0(statistics.median(g["proby"] for g in ok)),
            f0(100 * statistics.mean(g["walka_s"] for g in ok) / statistics.mean(g["czas"] for g in ok)),
            len(gr) - len(ok)))
    w.append("")
    med = statistics.median(g["czas"] / 60 for g in wszyscy)
    w.append("Wszystkie klasy: mediana **%s min** (cel planu rosnącego z tools/walka/tempo.py: ok. %s min na Las)." % (
        f1(med), f0(CEL_LASU_MIN)))
    w.append("")
    w.append("Wejście do przegrody: poziom gracza (mediana) i wygrane w trzech pierwszych walkach po wejściu:")
    w.append("")
    w.append("| Przegroda | " + " | ".join(p["id"] for p in P) + " |")
    w.append("|---|" + "---:|" * len(P))
    w.append("| Poziom na wejściu | " + " | ".join(f0(statistics.median(przyb[p["id"]])) if przyb[p["id"]] else "—"
                                             for p in P) + " |")
    w.append("| Wygrane w 3 pierwszych walkach | " + " | ".join(
        (f0(100.0 * sum(pierwsze[p["id"]]) / len(pierwsze[p["id"]])) + "%") if pierwsze[p["id"]] else "—" for p in P) + " |")
    w.append("")
    w.append("_python -B swiat/stan_gracza/symulacja_lasu.py --graczy %d --ziaren %d --ziarno %d --tempo %s (%.0f s)_" % (
        a.graczy, a.ziaren, a.ziarno, a.tempo, time.time() - t0))
    tekst = "\n".join(w) + "\n"
    print(tekst)
    if a.md:
        with open(a.md, "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst)


if __name__ == "__main__":
    main()
