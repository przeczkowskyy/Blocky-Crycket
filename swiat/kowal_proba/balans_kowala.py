#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kalkulator kowala (propozycja liczb, NIE kanon): siła bohatera z przedmiotami, koszty ulepszeń, łup przedmiotów
i tempo w lesie i w Bagnie. Liczby z ustawienia.json (przez dane.py), logika z logika_kowala.py, bohater i modyfikatory
z swiat/stan_gracza (opis_bohatera, czysty_modyfikator, opis_z_modyfikatorami — to samo, co Sygnaly/Bohater w Studio),
walki z tools/walka/silnik.py, przegrody lasu-pasa i Bagna jak swiat/stan_gracza/symulacja_lasu.py
i swiat/pety_proba/ekonomia_jajek.py (tylko odczyt).

    python -B swiat/kowal_proba/balans_kowala.py                 # wszystkie tabele (Markdown na ekran), ok. 2–4 min
    python -B swiat/kowal_proba/balans_kowala.py --szybko        # mniej walk i graczy (ok. 40 s)
    python -B swiat/kowal_proba/balans_kowala.py --md wynik.md

Liczy pojedynczo (bez wielu procesów).
CZĘŚĆ 1 — siła bohatera: szansa wygranej w każdej przegrodzie lasu i Bagna (bohater na najniższym poziomie przegrody,
  potwór z jej zakresu): dziś (wzór), podstawowy zestaw, pełny zestaw +0 / +3 / +5 / +10, Wojownik bez tarczy.
CZĘŚĆ 2 — gracz w lesie i w Bagnie (polityka jak w symulacja_lasu.py) z łupem przedmiotów: po każdej wygranej los
  przedmiotu (logika_kowala.lup, ranga potwora z silnika), zapas od razu rozebrany, ulepszenia przy wizycie u kowala
  (najwyżej co WIZYTA_CO_S gry, najtańsze najpierw, wizyta = WIZYTA_S s). Warianty: bez kowala (dziś), całe Złoto
  na kowala, połowa Złota na kowala (reszta np. na jajka). Czas do Strażników, ulepszenia, materiały, Złoto.
CZĘŚĆ 3 — tabela ulepszeń: koszt, przyrost, ile walk na jedno ulepszenie w lesie i w Bagnie (z części 2).
"""
import argparse
import copy
import math
import os
import random
import statistics
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
STAN = os.path.join(REPO, "swiat", "stan_gracza")
PETY = os.path.join(REPO, "swiat", "pety_proba")
for _s in (TU, STAN, PETY, os.path.join(REPO, "tools", "walka")):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import importlib.util  # noqa: E402


def _modul(nazwa, sciezka):
    if nazwa in sys.modules:
        return sys.modules[nazwa]
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nazwa] = m
    spec.loader.exec_module(m)
    return m


DANE_KOWALA = _modul("dane_kowala", os.path.join(TU, "dane.py"))         # ten pakiet (nazwa „dane” jest też w stanie)
import logika_kowala as LK  # noqa: E402
DS = _modul("dane_stanu_kowal", os.path.join(STAN, "dane.py"))            # swiat/stan_gracza/dane.py — tylko odczyt
LS = _modul("logika_stanu", os.path.join(STAN, "logika_stanu.py"))
import silnik  # noqa: E402
import symulacja_lasu as SL  # noqa: E402
import ekonomia_jajek as EJ  # noqa: E402

WIZYTA_S = 40.0        # s: Kamień Powrotu → bazar → kowal → teleport z powrotem (założenie)
WIZYTA_CO_S = 300.0    # najwyżej jedna wizyta u kowala na 5 min gry (założenie; gracz nie biega po każdej walce)
_PAMIEC = {}


def dane():
    if "D" not in _PAMIEC:
        _PAMIEC["D"] = DANE_KOWALA.dane_z_przypadkami()[0]
        _PAMIEC["DS"] = DS.dane_z_przypadkami()[1]
    return _PAMIEC["D"], _PAMIEC["DS"]


def bohater(Ds, D, klasa, L, stan=None):
    """Opis bohatera dla silnika: wzór poziomu (logika_stanu) + wpis „kowal” (logika_kowala.mod) złożony przez
    prawdziwą logikę stanu gracza. stan = dane gracza kowala albo None (dziś, bez kowala)."""
    st = LS.rozdziel(Ds, Ds["rozklady"][klasa], LS.pula(Ds, L))
    o = LS.opis_bohatera(Ds, klasa, L, st)
    if stan is None:
        return o
    m = LK.mod(D, klasa, stan, LK.zalozone(D, klasa, stan, None))
    czysty, powod = LS.czysty_modyfikator(Ds, m)
    if czysty is None:
        raise ValueError("Modyfikatory odrzuciłyby wpis kowala: %s %s" % (powod, m))
    return LS.opis_z_modyfikatorami(Ds, o, LS.zloz_modyfikatory(Ds, [czysty]))


def zestaw(D, klasa, poziom=0, tylko_podstawowy=False, bez=()):
    s = LK.nowe(D)
    for pid in D["klasy"][klasa]["przedmioty"]:
        if (tylko_podstawowy and not D["przedmioty"][pid]["podstawowy"]) or pid in bez:
            continue
        s["przedmioty"][pid] = {"poziom": poziom, "zapas": 0}
    return s


# ------------------------------------------------------------------------------------------------ część 1
def bagno():
    if "bagno" not in _PAMIEC:
        if EJ.BAGNO not in sys.path:
            sys.path.insert(0, EJ.BAGNO)
        import przeciwnicy  # noqa: E402
        przeciwnicy.zaladuj_do_silnika(silnik)
        _PAMIEC["bagno"] = EJ.przegrody_bagna()
    return _PAMIEC["bagno"]


def szansa(o, gatunek, od, do, n, ziarno):
    los = random.Random(ziarno)
    w = 0
    for _ in range(n):
        r = silnik.symuluj(o, {"potwor": gatunek, "poziom": los.randint(od, do)}, los.randrange(1, 2 ** 31 - 1))
        w += r["wynik"] == "wygrana"
    return 100.0 * w / n


def warianty(D):
    w = [("dziś (wzór poziomu)", lambda k: None), ("podstawowy zestaw +0", lambda k: zestaw(D, k, 0, True)),
         ("pełny zestaw +0", lambda k: zestaw(D, k, 0)), ("pełny +2", lambda k: zestaw(D, k, 2)),
         ("pełny +%d (najwyższy)" % D["ulepszenie"]["maks"], lambda k: zestaw(D, k, D["ulepszenie"]["maks"]))]
    return w


def czesc1(n, ziarno, wyjscie):
    D, Ds = dane()
    P = [("las", p) for p in SL.przegrody()] + [("bagno", p) for p in bagno()]
    wyjscie.append("### 1. Siła bohatera — szansa wygranej (%%, %d walk na komórkę; bohater na najniższym poziomie "
                   "przegrody, potwór z jej zakresu)" % n)
    wyjscie.append("")
    wyjscie.append("| Klasa | Wariant | " + " | ".join("%s %s (L%d)" % (b, p["id"], p["od"]) for b, p in P) + " | średnio |")
    wyjscie.append("|---|---|" + "---:|" * (len(P) + 1))
    srednie = {}
    for k in D["klasy"]:
        lista = list(warianty(D))
        if D["klasy"][k]["tarcza"]:
            tarcza = next(pid for pid in D["klasy"][k]["podstawowe"] if D["przedmioty"][pid]["slot"] == "OffHand")
            lista.append(("podstawowy bez tarczy", lambda kk, t=tarcza: zestaw(D, kk, 0, True, bez=(t,))))
        for nazwa, f in lista:
            stan = f(k)
            wiersz = []
            for i, (_b, p) in enumerate(P):
                o = bohater(Ds, D, k, p["od"], stan)
                wiersz.append(szansa(o, p["gatunek"], p["od"], p["do"], n, (ziarno, k, i).__hash__() & 0xFFFFFF))
            srednie[(k, nazwa)] = statistics.mean(wiersz)
            wyjscie.append("| %s | %s | %s | **%.0f** |" % (D["nazwyKlas"][k], nazwa, " | ".join("%.0f" % x for x in wiersz),
                                                         srednie[(k, nazwa)]))
    wyjscie.append("")
    wyjscie.append("Różnica między klasami (średnio po przegrodach, pp): " + "; ".join(
        "%s %.1f" % (nazwa, max(srednie[(k, nazwa)] for k in D["klasy"]) - min(srednie[(k, nazwa)] for k in D["klasy"]))
        for nazwa, _f in warianty(D)) + ".")
    wyjscie.append("")
    # opis bohatera na kilku poziomach (liczby, które zobaczy gracz w oknie)
    wyjscie.append("Bohater na 1., 5. i 10. poziomie (broń / pancerz z przedmiotów / blok tarczy; dziś → podstawowy → "
                   "pełny +0 → pełny +%d):" % D["ulepszenie"]["maks"])
    wyjscie.append("")
    for k in D["klasy"]:
        cz = []
        for L in (1, 5, 10):
            opisy = []
            for stan in (None, zestaw(D, k, 0, True), zestaw(D, k, 0), zestaw(D, k, D["ulepszenie"]["maks"])):
                o = bohater(Ds, D, k, L, stan)
                opisy.append("%g/%g%s" % (o["bron"]["obrazenia"], o["pancerz_przedmiotow"],
                                          ("/%d%%" % round(o["tarcza"]["blok"] * 100)) if "tarcza" in o else ""))
            cz.append("L%d: %s" % (L, " → ".join(opisy)))
        wyjscie.append("- %s — %s" % (D["nazwyKlas"][k], "; ".join(cz)))
    wyjscie.append("")
    return srednie


# ------------------------------------------------------------------------------------------------ część 2
def ulepszenia_przy_wizycie(D, klasa, stan, zloto):
    """Rozbiórka całego zapasu i ulepszenia najtańsze najpierw, dopóki starcza Złota i materiałów → (stan, zloto, n)."""
    s = copy.deepcopy(stan)
    for pid in D["klasy"][klasa]["przedmioty"]:
        while LK.posiada(s, pid) and s["przedmioty"][pid]["zapas"] > 0:
            ok, s, _z = LK.rozbierz(D, s, klasa, pid)
    n = 0
    while True:
        kand = []
        for pid in LK.zalozone(D, klasa, s, None):
            ok, k, _ile = LK.plan_ulepszenia(D, s, klasa, pid)
            if ok and k["zloto"] <= zloto:
                kand.append((k["zloto"] / D["przedmioty"][pid]["waga"], pid, k))
        if not kand:
            return s, zloto, n
        kand.sort()
        _c, pid, k = kand[0]
        zloto -= k["zloto"]
        s = LK.ulepsz(D, s, pid, k)
        n += 1


def gracz(D, Ds, P, klasa, los, x0, przelot, udzial, L0=1, xp0=0, troll="lesny_troll", dojscie=None,
          limit_min=SL.LIMIT_MIN, stan0=None, zloto0=0):
    """Jeden gracz do wygranej ze Strażnikiem biomu (polityka symulacja_lasu.jeden_gracz). udzial = część Złota
    z łupu na kowala (0 = bez kowala: bohater ze wzoru jak dziś). → słownik wyników albo None (limit)."""
    dojscie = dojscie or SL.DOJSCIE
    L, xp, czas = L0, xp0, przelot + abs(P[0]["x"] - x0) / SL.PREDKOSC
    stan = copy.deepcopy(stan0) if stan0 is not None else LK.podstawowe(D, LK.nowe(D), klasa)[0]
    zloto = zloto0
    i = z_rzedu = farma = 0
    troll_od = 0.0
    wizyta = -1e9
    walki = przegrane = wizyt = ulepszen = lupow = nowych = 0
    zloto_lacznie = 0
    materialy_lacznie = 0
    pierwsze_ulepszenie = None
    while czas <= limit_min * 60:
        p = P[i]
        cel = p
        if p["gatunek"] == troll and czas < troll_od:
            cel = P[i - 1]
        hi = cel["do"] if cel["straznik"] else max(cel["od"], min(cel["do"], L + 1))
        pz = los.randint(cel["od"], hi)
        o = bohater(Ds, D, klasa, L, stan if udzial > 0 else None)
        r = silnik.symuluj(o, {"potwor": cel["gatunek"], "poziom": pz}, los.randrange(1, 2 ** 31 - 1))
        walki += 1
        czas += r["czas"] + SL.EKRAN_WYNIKU + dojscie[cel["gatunek"]]
        L, xp, _ = LS.awans(Ds, L, xp, r["lup"]["doswiadczenie"])
        wygrana = r["wynik"] == "wygrana"
        if wygrana:
            zl = r["lup"]["zloto"]
            zloto_lacznie += zl
            zloto += zl * udzial
            if udzial > 0:
                rg = silnik.PRZECIWNICY[cel["gatunek"]]["ranga"]
                przed = sum(v["zapas"] for v in stan["przedmioty"].values()) * D["rozbiorka"]["materialy"]
                stan, wyn = LK.lup(D, stan, klasa, rg, los.random(), los.random())
                if wyn:
                    lupow += 1
                    nowych += wyn["nowy"]
                    if not wyn["nowy"]:
                        materialy_lacznie += D["rozbiorka"]["materialy"]
                _ = przed
            if udzial > 0 and czas - wizyta >= WIZYTA_CO_S:
                s2, z2, n = ulepszenia_przy_wizycie(D, klasa, stan, zloto)
                if n > 0:
                    stan, zloto = s2, z2
                    ulepszen += n
                    wizyt += 1
                    wizyta = czas
                    czas += WIZYTA_S
                    if pierwsze_ulepszenie is None:
                        pierwsze_ulepszenie = czas
            z_rzedu = 0
            if p["straznik"]:
                poziomy = [stan["przedmioty"][pid]["poziom"] for pid in stan["przedmioty"]]
                return {"czas": czas, "poziom": L, "xp": xp, "walki": walki, "przegrane": przegrane, "wizyt": wizyt,
                        "ulepszen": ulepszen, "lupow": lupow, "nowych": nowych, "stan": stan, "zloto": zloto,
                        "zloto_lacznie": zloto_lacznie, "materialy_lacznie": materialy_lacznie,
                        "suma_poziomow": sum(poziomy), "pierwsze": pierwsze_ulepszenie,
                        "posiadane": len(stan["przedmioty"])}
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
        przegrane += 1
        z_rzedu += 1
        if p["straznik"]:
            czas += abs(P[i - 1]["x"] - p["x"]) / SL.PREDKOSC
            i -= 1
            farma = SL.ZAPAS_FARMY
        elif z_rzedu >= 2 and i > 0:
            czas += abs(P[i - 1]["x"] - p["x"]) / SL.PREDKOSC
            i -= 1
            z_rzedu = 0
    return None


def czesc2(graczy, ziarno, wyjscie):
    D, Ds = dane()
    P = SL.przegrody()
    x0, przelot = SL.przybycie_i_przelot()
    Pb = bagno()
    xb, przelot_b = EJ.przybycie_i_przelot_bagna()
    W = [("bez kowala (dziś)", 0.0), ("całe Złoto na kowala", 1.0), ("połowa Złota na kowala", 0.5)]
    wyniki = {}
    for nazwa, udzial in W:
        for k in D["klasy"]:
            los = random.Random("kowal-%s-%s-%d" % (k, udzial, ziarno))
            for _ in range(graczy):
                g = gracz(D, Ds, P, k, los, x0, przelot, udzial)
                if g is None:
                    continue
                gb = gracz(D, Ds, Pb, k, los, xb, przelot_b, udzial, L0=g["poziom"], xp0=g["xp"],
                           troll=EJ.TROLL_BAGNA, dojscie=EJ.DOJSCIE_BAGNA, limit_min=EJ.LIMIT_BAGNA_MIN,
                           stan0=g["stan"], zloto0=g["zloto"])
                wyniki.setdefault((nazwa, "las"), []).append(g)
                if gb is not None:
                    wyniki.setdefault((nazwa, "bagno"), []).append(gb)

    def med(lista, pole, dziel=1.0):
        xs = [x[pole] / dziel for x in lista if x[pole] is not None]
        return statistics.median(xs) if xs else float("nan")

    wyjscie.append("### 2. Gracz w lesie i w Bagnie z łupem przedmiotów (%d graczy na klasę; wizyta u kowala najwyżej "
                   "co %.0f min, %.0f s; zapas rozbierany od razu)" % (graczy, WIZYTA_CO_S / 60, WIZYTA_S))
    wyjscie.append("")
    wyjscie.append("| Wariant | Biom | Czas do Strażnika (mediana, 10–90%) | Przegrane | Przedmiotów z łupu (nowych) | "
                   "Posiadane na końcu | Ulepszeń (wizyt) | Suma poziomów ulepszeń | 1. ulepszenie po | Złoto z walk | "
                   "Materiały z rozbiórki |")
    wyjscie.append("|---|---|---|---:|---|---:|---|---:|---:|---:|---:|")
    for nazwa, _u in W:
        for biom in ("las", "bagno"):
            lista = wyniki.get((nazwa, biom), [])
            if not lista:
                continue
            t = sorted(x["czas"] / 60 for x in lista)
            pierwsze = [x["pierwsze"] / 60 for x in lista if x["pierwsze"] is not None]
            wyjscie.append("| %s | %s | %.1f min (%.1f–%.1f) | %.0f | %.0f (%.0f) | %.0f | %.0f (%.0f) | %.0f | %s | %.0f | %.0f |" % (
                nazwa, biom, statistics.median(t), SL.kwantyl(t, 0.1), SL.kwantyl(t, 0.9), med(lista, "przegrane"),
                med(lista, "lupow"), med(lista, "nowych"), med(lista, "posiadane"), med(lista, "ulepszen"),
                med(lista, "wizyt"), med(lista, "suma_poziomow"),
                ("%.1f min" % statistics.median(pierwsze)) if pierwsze else "—", med(lista, "zloto_lacznie"),
                med(lista, "materialy_lacznie")))
    wyjscie.append("")
    # klasy osobno (całe Złoto na kowala): czy żadna nie odjeżdża
    for biom in ("las", "bagno"):
        cz = []
        for k in D["klasy"]:
            for nazwa, u in W[:2]:
                lista = [x for x in wyniki.get((nazwa, biom), []) if x["stan"]["przedmioty"] and
                         next(iter(x["stan"]["przedmioty"])) in D["klasy"][k]["przedmioty"]]
                if lista:
                    cz.append("%s/%s %.1f" % (D["nazwyKlas"][k], "kowal" if u else "dziś",
                                              statistics.median(x["czas"] / 60 for x in lista)))
        wyjscie.append("- %s, mediana czasu do Strażnika (min): %s" % (biom, "; ".join(cz)))
    wyjscie.append("")
    return wyniki


def czesc3(wyniki, wyjscie):
    D, _Ds = dane()
    G = D["ulepszenie"]
    przyklad = {k: next(pid for pid in D["klasy"][k]["przedmioty"] if D["przedmioty"][pid]["slot"] == "Weapon")
                for k in D["klasy"]}
    tempo = {}
    for biom in ("las", "bagno"):
        lista = wyniki.get(("całe Złoto na kowala", biom), [])
        if lista:
            walk = sum(x["walki"] for x in lista)
            tempo[biom] = (sum(x["zloto_lacznie"] for x in lista) / walk, sum(x["materialy_lacznie"] for x in lista) / walk)
    wyjscie.append("### 3. Ulepszenia: koszt, przyrost, ile walk na jedno ulepszenie")
    wyjscie.append("")
    wyjscie.append("Złoto i materiały na walkę (średnio, wariant „całe Złoto na kowala”): " + "; ".join(
        "%s: %.0f Złota, %.2f materiału" % (b, z, m) for b, (z, m) in tempo.items()) + ". Walk na ulepszenie = więcej "
        "z dwóch: koszt w Złocie ÷ Złoto na walkę albo materiały ÷ materiały na walkę.")
    wyjscie.append("")
    wyjscie.append("| Poziom | Złoto (Mag ×1,75) | Materiały (Mag) | Przyrost miecza / sztyletu | Przyrost kostura | "
                   "Walk w lesie: za Złoto / za materiały → ulepszenie | Walk w Bagnie: Złoto / materiały → ulepszenie | "
                   "Razem do tego poziomu: Złoto / materiały |")
    wyjscie.append("|---|---:|---:|---|---|---|---|---|")
    sz, sm = 0, 0
    kostur = przyklad["mag"]
    miecz = przyklad["wojownik"]
    for p in range(G["maks"]):
        k = LK.koszt(D, miecz, p)
        km = LK.koszt(D, kostur, p)
        sz += k["zloto"]
        sm += k["materialy"]
        kol = []
        for b in ("las", "bagno"):
            if b not in tempo:
                kol.append("—")
                continue
            z, m = tempo[b]
            wz, wm = k["zloto"] / z, (k["materialy"] / m if m > 0 else float("inf"))
            kol.append("%.1f / %.1f → **%.1f**" % (wz, wm, max(wz, wm)))
        wyjscie.append("| +%d | %d (%d) | %d (%d) | %s | %s | %s | %s | %d / %d |" % (
            p + 1, k["zloto"], km["zloto"], k["materialy"], km["materialy"],
            LK.tekst_stat_lista(D, D["przedmioty"][miecz]["krok"]), LK.tekst_stat_lista(D, D["przedmioty"][kostur]["krok"]),
            kol[0], kol[1], sz, sm))
    wyjscie.append("")
    wyjscie.append("Cały zestaw klasy do +%d: Wojownik i Zwiadowca po %d Złota i %d materiałów, Mag %d Złota i %d materiałów "
                   "(4 przedmioty o wadze 1,75)." % (
                       G["maks"], sum(sum(D["przedmioty"][i]["koszt"]["zloto"]) for i in D["klasy"]["wojownik"]["przedmioty"]),
                       sum(sum(D["przedmioty"][i]["koszt"]["materialy"]) for i in D["klasy"]["wojownik"]["przedmioty"]),
                       sum(sum(D["przedmioty"][i]["koszt"]["zloto"]) for i in D["klasy"]["mag"]["przedmioty"]),
                       sum(sum(D["przedmioty"][i]["koszt"]["materialy"]) for i in D["klasy"]["mag"]["przedmioty"])))
    wyjscie.append("")


def tabela_przedmiotow(wyjscie):
    D, _Ds = dane()
    wyjscie.append("### 0. Przedmioty (baza +0, przyrost za poziom ulepszenia)")
    wyjscie.append("")
    wyjscie.append("| Klasa | Przedmiot | Slot | Start | +0 | Za poziom | +%d (najwyższy) |" % D["ulepszenie"]["maks"])
    wyjscie.append("|---|---|---|---|---|---|---|")
    for k in D["klasy"]:
        for pid in D["klasy"][k]["przedmioty"]:
            P = D["przedmioty"][pid]
            b = LK.tekst_stat_lista(D, LK.statystyki(D, pid, 0)) or "—"
            if P["slot"] == "OffHand" and D["klasy"][k]["tarcza"]:
                b = "blok %d%% (wzór)" % round(D["blokTarczy"] * 100) + ("" if b == "—" else " · " + b)
            wyjscie.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                D["nazwyKlas"][k], P["nazwa"], D["sloty"][P["slot"]], "tak" if P["podstawowy"] else "łup",
                b, LK.tekst_stat_lista(D, P["krok"]), LK.tekst_stat_lista(D, LK.statystyki(D, pid, D["ulepszenie"]["maks"]))))
    wyjscie.append("")


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Kalkulator kowala: siła bohatera z przedmiotami, ulepszenia, łup")
    ap.add_argument("--walk", type=int, default=400, help="walk na komórkę tabeli siły (część 1)")
    ap.add_argument("--graczy", type=int, default=60, help="graczy na klasę i wariant (część 2)")
    ap.add_argument("--ziarno", type=int, default=1)
    ap.add_argument("--szybko", action="store_true")
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    if a.szybko:
        a.walk, a.graczy = 120, 15
    t0 = time.time()
    w = ["## Kowal na próbę — kalkulator (propozycja liczb, nie kanon)", ""]
    tabela_przedmiotow(w)
    czesc1(a.walk, a.ziarno, w)
    wyniki = czesc2(a.graczy, a.ziarno, w)
    czesc3(wyniki, w)
    w.append("_python -B swiat/kowal_proba/balans_kowala.py --walk %d --graczy %d --ziarno %d (%.0f s)_" % (
        a.walk, a.graczy, a.ziarno, time.time() - t0))
    tekst = "\n".join(w) + "\n"
    print(tekst)
    if a.md:
        with open(a.md, "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst)


if __name__ == "__main__":
    main()
