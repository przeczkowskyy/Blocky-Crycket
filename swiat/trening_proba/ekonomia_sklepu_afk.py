#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rachunek sklepu trenera (ulepszenia stanowisk AFK i wzmacniacze) — liczby z src/shared/TreningAFKDane.luau (D.sklep),
bez Studio. 27.11.2026, polecenie Pawła: „u trenera … panel sklepu/ulepszeń, gdzie np. gracz może ulepszyć bieżnię,
żeby dawała więcej na powtórzenie, albo kupić jakieś wzmacniacze na trening, np. siła ×2 na 10 min”. LICZBY ROBOCZE.

    python -B swiat/trening_proba/ekonomia_sklepu_afk.py                 # tabele ceny / tempa (sekundy)
    python -B swiat/trening_proba/ekonomia_sklepu_afk.py --walka         # + strażnicy Bagna i Dżungli (silnik walki, ok. 1 min)
    python -B swiat/trening_proba/ekonomia_sklepu_afk.py --walka --ziaren 400 --md wynik.md

Wzory jak w kalkulatorze skilla roblox-simulator-economy (scripts/balance.luau: cena poziomu, suma, czas zarobku przy
danym przychodzie) — Lune nie jest zainstalowany na tym komputerze, więc rachunek jest tu, w Pythonie (te same wzory;
ceny są listą w danych, nie wzorem baseCost × growth^n).
Przychód Rybek: swiat/pety_proba/ekonomia_zagrody.py (uruchomienie 27.11.2026, mediany 30 graczy na klasę): walki las
7927/h, Bagno 10133/h, Dżungla 16281/h; zagroda pełna, typowa 288 / 1008 / 2349 na godzinę (--przelicz liczy od nowa).
Walka: tools/walka/silnik.py (port silnika) + przeciwnicy Bagna i Dżungli (swiat/bagno_pas_gra, swiat/dzungla_pas_gra),
postacie wzorcowe (tools/walka/wzorcowe.py) z punktami treningu ponad pulę w proporcjach klasy (jak „polityka klasa”
w tools/walka/progresja.py). „Potrzeba” = najmniej punktów treningu, przy których średnia z trzech klas wygrywa ze
strażnikiem ≥ 50% (gracz na poziomie strażnika + 1).
"""
import argparse
import importlib.util
import math
import os
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
PLIK_DANYCH = os.path.join(REPO, "src", "shared", "TreningAFKDane.luau")

PRZYCHOD_WALK_H = {"las": 7927, "bagno": 10133, "dzungla": 16281}          # ekonomia_zagrody.py, 27.11.2026
PRZYCHOD_ZAGRODY_H = {"las": 288, "bagno": 1008, "dzungla": 2349}           # typowa pełna zagroda, ta sama tabela
NAZWY_BIOMOW = {"las": "Las", "bagno": "Bagno", "dzungla": "Dżungla"}
STRAZNICY = [("bagno", "straznik_topieli", 16, 17, "Strażnik Topieli"), ("dzungla", "waz_stu_lian", 23, 24, "Wąż Stu Lian")]
PUNKTY_SIATKA = (0, 15, 30, 45, 60, 80, 100, 130, 160, 200, 250, 300)


def _liczba(blok, nazwa):
    m = re.search(r"\b%s = ([\d.]+)" % nazwa, blok)
    if not m:
        raise ValueError("brak %s w TreningAFKDane.luau" % nazwa)
    return float(m.group(1))


def wczytaj(plik=PLIK_DANYCH):
    """Liczby treningu i sklepu z TreningAFKDane.luau (jedno źródło — serwer i klient czytają ten sam moduł)."""
    with open(plik, encoding="utf-8") as f:
        t = f.read()
    s = t[t.index("D.sklep = {"):]
    s = s[:s.index("\n}\n") if "\n}\n" in s else s.index("\r\n}\r\n")]
    u = s[s.index("ulepszenia = {"):s.index("wzmacniacze = {")]
    w = s[s.index("wzmacniacze = {"):]
    ceny = [int(x) for x in re.search(r"ceny = \{([^}]*)\}", u).group(1).replace(" ", "").split(",") if x]
    return {
        "powtorzen": _liczba(t, r"D\.powtorzenNaPasek"),
        "czas_powtorzenia": _liczba(t, r"D\.czasPowtorzenia"),
        "przyrost": _liczba(t, r"D\.przyrostNaPasek"),
        "skill_min": _liczba(t, r"D\.skillCheckCoMin"), "skill_maks": _liczba(t, r"D\.skillCheckCoMaks"),
        "skill_mnoznik": _liczba(t, r"D\.mnoznikSkillCheck"), "skill_czas": _liczba(t, r"D\.czasPrzyspieszenia"),
        "maks": int(_liczba(u, "maks")), "premia": _liczba(u, "premia"), "ceny": ceny,
        "mnoznik": _liczba(w, "mnoznik"), "czas_w": _liczba(w, "czas"), "cena_w": int(_liczba(w, "cena")),
        "odstep": _liczba(s, "odstep"),
    }


def powtorzen_dla(E, poziom):
    """Lustro D.powtorzenDla: pasek przy danym poziomie ulepszenia."""
    p = max(0, min(int(poziom), E["maks"]))
    return E["powtorzen"] / (1 + E["premia"] * p)


def tempo_h(E, poziom=0, wzmacniacz=False, skill=False):
    """Punkty statystyki na godzinę na jednym stanowisku (AFK; skill=True — każdy skill check trafiony po 0,5 s)."""
    pasek_s = powtorzen_dla(E, poziom) * E["czas_powtorzenia"]
    ile = E["przyrost"] * (E["mnoznik"] if wzmacniacz else 1)
    m = 1.0
    if skill:
        cykl = (E["skill_min"] + E["skill_maks"]) / 2.0 + 0.5      # od trafienia do następnego + reakcja
        m = 1.0 + (E["skill_mnoznik"] - 1.0) * E["skill_czas"] / cykl
    return 3600.0 / pasek_s * ile * m


def tabela_ulepszen(E):
    """[(poziom, cena, suma, tempo %, punkty/h AFK, minuty walk las/Bagno/Dżungla na cenę, zwrot)]"""
    w, suma = [], 0
    for i, c in enumerate(E["ceny"]):
        suma += c
        lv = i + 1
        w.append({"poziom": lv, "cena": c, "suma": suma, "premia": round(100 * E["premia"] * lv),
                  "pasek": round(powtorzen_dla(E, lv), 3), "na_h": round(tempo_h(E, lv)),
                  "min_walk": {b: round(60.0 * c / v, 1) for b, v in PRZYCHOD_WALK_H.items()},
                  "min_zagrody": {b: round(60.0 * c / v) for b, v in PRZYCHOD_ZAGRODY_H.items()}})
    return w


def tekst_ceny(E):
    L = ["### Ulepszenie stanowiska (każde z sześciu osobno, poziomy 0–%d)" % E["maks"], "",
         "| Poziom | Cena | Razem | Tempo | Pasek (powt.) | Punkty/h AFK | Cena = minut walk las / Bagno / Dżungla | = minut samej zagrody (typowej) las / Bagno / Dżungla |",
         "|---:|---:|---:|---:|---:|---:|---|---|",
         "| 0 | — | — | 100%% | %s | %d | — | — |" % (_l(E["powtorzen"], 2), round(tempo_h(E, 0)))]
    for r in tabela_ulepszen(E):
        L.append("| %d | %d | %d | %d%% | %s | %d | %s | %s |" % (
            r["poziom"], r["cena"], r["suma"], 100 + r["premia"], _l(r["pasek"], 2), r["na_h"],
            " / ".join(_l(r["min_walk"][b], 1) for b in ("las", "bagno", "dzungla")),
            " / ".join(str(r["min_zagrody"][b]) for b in ("las", "bagno", "dzungla"))))
    suma = sum(E["ceny"])
    L += ["", "Wszystkie poziomy jednego stanowiska: **%d Rybek**; sześciu stanowisk: **%d** (%s h walk w lesie, %s h "
          "w Bagnie, %s h w Dżungli)." % (suma, 6 * suma, _l(6 * suma / PRZYCHOD_WALK_H["las"], 1),
                                          _l(6 * suma / PRZYCHOD_WALK_H["bagno"], 1), _l(6 * suma / PRZYCHOD_WALK_H["dzungla"], 1)),
          "", "### Wzmacniacz", "",
          "×%g statystyki za pasek jednego stanowiska przez %d min (czas rzeczywisty), jeden na statystykę: **%d Rybek** "
          "(%s min walk w lesie, %s w Dżungli). Bez przerwy przez godzinę: %d Rybek/h — więcej niż daje typowa zagroda "
          "w każdym biomie (%s/h), więc wzmacniacze trzeba opłacać walką."
          % (E["mnoznik"], E["czas_w"] / 60, E["cena_w"], _l(60.0 * E["cena_w"] / PRZYCHOD_WALK_H["las"], 1),
             _l(60.0 * E["cena_w"] / PRZYCHOD_WALK_H["dzungla"], 1), round(E["cena_w"] * 3600 / E["czas_w"]),
             " / ".join(str(v) for v in PRZYCHOD_ZAGRODY_H.values())),
          "", "Tempo jednego stanowiska (punkty statystyki na godzinę): AFK %d; z pełnym ulepszeniem %d (×%s); "
          "z wzmacniaczem %d; oba %d (×%s). Z trafianiem każdego skill checku: ×%s więcej."
          % (round(tempo_h(E)), round(tempo_h(E, E["maks"])), _l(tempo_h(E, E["maks"]) / tempo_h(E), 2),
             round(tempo_h(E, 0, True)), round(tempo_h(E, E["maks"], True)),
             _l(tempo_h(E, E["maks"], True) / tempo_h(E), 2), _l(tempo_h(E, 0, False, True) / tempo_h(E), 2))]
    return "\n".join(L)


def _l(v, n=0):
    return ("%%.%df" % n % v).replace(".", ",")


def _modul(nazwa, sciezka):
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def wygrane(ziaren=200):
    """{(gatunek, klasa, punkty): % wygranych} — gracz na poziomie strażnika + 1, punkty treningu w proporcjach klasy."""
    walka = os.path.join(REPO, "tools", "walka")
    if walka not in sys.path:
        sys.path.insert(0, walka)
    import silnik  # noqa: E402
    import wzorcowe  # noqa: E402
    for biom, kat in (("bagno", "bagno_pas_gra"), ("dzungla", "dzungla_pas_gra")):
        _modul("przeciwnicy_" + biom, os.path.join(REPO, "swiat", kat, "przeciwnicy.py")).zaladuj_do_silnika(silnik)
    W = {}
    for _, gat, Lp, Lg, _ in STRAZNICY:
        for kl in wzorcowe.KLASY:
            for X in PUNKTY_SIATKA:
                dod = wzorcowe.rozdziel(wzorcowe.ROZKLADY[kl], X) if X else None
                g = wzorcowe.postac(kl, Lg, dodatkowe=dod)
                n = sum(silnik.symuluj(g, {"potwor": gat, "poziom": Lp}, z)["wynik"] == "wygrana" for z in range(1, ziaren + 1))
                W[(gat, kl, X)] = 100.0 * n / ziaren
    return W


def potrzeba(W, gat, prog=50.0):
    """Najmniej punktów treningu (interpolacja liniowa), przy których średnia z trzech klas ≥ prog %."""
    klasy = sorted({k for (g, k, _) in W if g == gat})
    sr = [(X, sum(W[(gat, k, X)] for k in klasy) / len(klasy)) for X in PUNKTY_SIATKA]
    for (x0, y0), (x1, y1) in zip(sr, sr[1:]):
        if y0 >= prog:
            return x0, sr
        if y1 >= prog:
            return x0 + (x1 - x0) * (prog - y0) / (y1 - y0), sr
    return None, sr


def tekst_walki(E, W):
    L = ["### Strażnicy: ile treningu do 50% wygranych i ile to minut na stanowiskach", "",
         "| Strażnik (poziom, gracz) | Bez treningu | Potrzeba punktów | AFK | Pełne ulepszenia | Wzmacniacz | Oba (najgorszy przypadek) |",
         "|---|---:|---:|---:|---:|---:|---:|"]
    warianty = [tempo_h(E), tempo_h(E, E["maks"]), tempo_h(E, 0, True), tempo_h(E, E["maks"], True)]
    for _, gat, Lp, Lg, nazwa in STRAZNICY:
        X, sr = potrzeba(W, gat)
        zero = sr[0][1]
        if X is None:
            L.append("| %s (%d, %d) | %s%% | > %d | — | — | — | — |" % (nazwa, Lp, Lg, _l(zero), PUNKTY_SIATKA[-1]))
            continue
        L.append("| %s (%d, %d) | %s%% | %d | %s | %s | %s | %s |" % (
            nazwa, Lp, Lg, _l(zero), round(X), *("%s min" % _l(60.0 * X / v, 1) for v in warianty)))
    L += ["", "Średnia z trzech klas (Wojownik, Zwiadowca, Mag) przy punktach ponad pulę poziomu:", "",
          "| Punkty treningu | " + " | ".join(n for *_, n in STRAZNICY) + " |", "|---:|" + "---:|" * len(STRAZNICY)]
    for X in PUNKTY_SIATKA:
        L.append("| %d | %s |" % (X, " | ".join(
            _l(sum(W[(g, k, X)] for k in ("wojownik", "zwiadowca", "mag")) / 3.0) + "%" for _, g, *_r in STRAZNICY)))
    return "\n".join(L)


def main(argv):
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--walka", action="store_true", help="strażnicy Bagna i Dżungli (silnik walki)")
    ap.add_argument("--ziaren", type=int, default=200)
    ap.add_argument("--przelicz", action="store_true", help="przychód Rybek od nowa z swiat/pety_proba/ekonomia_zagrody.py")
    ap.add_argument("--md", default=None)
    a = ap.parse_args(argv)
    if a.przelicz:
        Z = _modul("ekonomia_zagrody", os.path.join(REPO, "swiat", "pety_proba", "ekonomia_zagrody.py"))
        print("przeliczenie: %s" % (Z.rachunek(30, 1)[1],))
    E = wczytaj()
    tekst = tekst_ceny(E)
    if a.walka:
        tekst += "\n\n" + tekst_walki(E, wygrane(a.ziaren))
    print(tekst)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write(tekst + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
