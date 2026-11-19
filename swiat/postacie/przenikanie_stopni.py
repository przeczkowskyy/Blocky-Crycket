#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Przenikanie broni w głowę i tułów w klipach walki dla KOMPLETÓW STOPNI (D-106) — sam pomiar, bez poprawek.

    python -B swiat/postacie/przenikanie_stopni.py                 # 3 klasy × (start + 3 stopnie), tabela tekstowa
    python -B swiat/postacie/przenikanie_stopni.py --md            # tabela Markdown
    python -B swiat/postacie/przenikanie_stopni.py --klasa mag --stopien las,dzungla
    python -B swiat/postacie/przenikanie_stopni.py --wszystko      # każdy scenariusz i strefa (domyślnie tylko miejsca
                                                                   # ponad próg albo gorsze niż komplet startowy)
    python -B swiat/postacie/przenikanie_stopni.py --gestosc 0.5   # rzadsze próbki (szybciej, mniej dokładnie)

Jak liczy (nic nie zapisuje — wynik tylko na ekran):
  * narzędzie swiat/postacie/przenikanie (pomiar.py, pozy.py — tylko import): te same scenariusze co dla aktorów
    walki (każdy klip, wejścia i wyjścia ze spoczynku, upadek, wskrzeszenie, radość), te same progi (głowa i nakrycie
    0,02, tułów 0,10 studa);
  * aktor = dane walki klasy (swiat/test_walki2/dane/<klasa>.json: kości i klipy takie, jak odtwarza gra) z bryłami
    bohatera w komplecie stopnia (stopnie.postac → roblox_klocki.rig); kości muszą być te same co w danych walki;
  * komplet startowy mierzony tą samą drogą jest odniesieniem — kolumna „gorzej o” to różnica głębokości;
  * broń = przedmioty kompletu na miejscach dzisiejszej broni klasy (miecz i tarcza, łuk i sztylet, kostur);
  * strefy: głowa i tułów (bryły ciała i powłok zbroi na tych kościach) oraz „nakrycie” — u kota kapelusz (kość
    HatPivot, jak w narzędziu), u ludzi DOLICZONE tutaj: wszystko na kości głowy razem z hełmem / kapturem i włosami.

Czego NIE mierzy: broń w ręce, nogi i naramienniki poza kośćmi tułowia; ozdoby (pióra, rogi) wchodzące w ciało bez
udziału broni; przedmiot w przedmiot poza powyższymi strefami; zasłanianie twarzy z kamery (przenikanie.py --kamera).
"""
import argparse
import collections
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
WALKA = os.path.join(REPO, "swiat", "test_walki2")
for _s in (REPO, os.path.join(REPO, "tools"), WALKA, os.path.join(TU, "przenikanie")):
    if _s not in sys.path:
        sys.path.insert(0, _s)

PROG_GORZEJ = 0.02          # studa — o tyle głębiej niż komplet startowy uznajemy za „gorzej”


def _l(x):
    return ("%.3f" % x).replace(".", ",")


def dane_kompletu(klasa, stopien):
    """Dane aktora walki klasy z bryłami bohatera w komplecie stopnia (w pamięci) + specyfikacja broni i stref."""
    import aktorzy as A
    import pomiar as PM
    from swiat.postacie import stopnie as ST
    from swiat.postacie.biblioteka import roblox_klocki as RK
    wpis = A.PO_KLUCZU[klasa]
    d0 = A.wczytaj(klasa)
    p = ST.postac(klasa, stopien)
    if wpis.get("skala"):
        p.skala = float(wpis["skala"])
    r = RK.rig(p)
    if [k[0] for k in r["kosci"]] != [k[0] for k in d0["kosci"]] or r["kosci"] != d0["kosci"]:
        raise SystemExit("%s / %s: kości bohatera w komplecie ≠ kości danych walki" % (klasa, stopien))
    d = dict(d0)
    d["czesci"], d["grupy"], d["materialy"] = r["czesci"], r["grupy"], r["materialy"]
    wzor = PM.SPEC[klasa]
    start = list(ST.komplet(klasa, "start"))
    komplet = list(ST.komplet(klasa, stopien))
    bron = [komplet[start.index(g)] for g in wzor["bron_grupy"]]
    brak = [g for g in bron if g not in d["grupy"]]
    if brak:
        raise SystemExit("%s / %s: w rigu nie ma grup broni %s" % (klasa, stopien, ", ".join(brak)))
    spec = {"bron_grupy": bron, "glowa": list(wzor["glowa"]), "tulow": list(wzor["tulow"]),
            "nakrycie": list(wzor.get("nakrycie") or wzor["glowa"])}
    return wpis, d0, d, spec


def zgodny_ze_startem(d0, d):
    """Czy bryły kompletu startowego z tej drogi są tymi samymi bryłami co dane walki (kość, kształt, miejsce, rozmiar)."""
    def klucz(c):
        return (c[0], c[1]) + tuple(round(v, 3) for v in c[3:12])
    return collections.Counter(klucz(c) for c in d0["czesci"]) == collections.Counter(klucz(c) for c in d["czesci"])


def zmierz(klasa, stopien, gestosc):
    import pomiar as PM
    wpis, d0, d, spec = dane_kompletu(klasa, stopien)
    pm = PM.Pomiar(d, spec)
    wyniki = PM.zmierz(pm, PM.scenariusze(pm.a, wpis, gestosc))
    progi = {z.nazwa: z.prog for z in pm.strefy}
    ktora = {pm.nazwy[b]: pm.grupa_broni[b] for b in pm.bron}        # bryła broni → miecz / tarcza / łuk / sztylet / kostur
    tab = collections.OrderedDict()
    for w in wyniki:
        for strefa, s in w["strefy"].items():
            bron = "%s: %s" % (ktora.get(s["bron"], "?"), s["bron"].split("/")[-1]) if s["bron"] else ""
            tab[(w["nazwa"], strefa)] = {"rodzaj": w["rodzaj"], "klip": w["klip"], "m": s["m"],
                                         "glebokosc": max(0.0, -s["m"]), "t": s["t"] or 0.0,
                                         "bron": bron, "cialo": s["cialo"], "prog": progi[strefa]}
    return tab, (zgodny_ze_startem(d0, d) if stopien == "start" else None), len(d["czesci"])


def wiersze(klasa, stopien, tab, odn, wszystko):
    """Wiersze tabeli kompletu: (klasa, stopień, scenariusz, strefa, głębokość, gorzej o, co w co, chwila, ocena)."""
    wynik = []
    for (nazwa, strefa), s in tab.items():
        o = odn.get((nazwa, strefa))
        roznica = s["glebokosc"] - (o["glebokosc"] if o else 0.0)
        ponad = s["glebokosc"] > s["prog"]
        gorzej = stopien != "start" and roznica > PROG_GORZEJ
        if not (wszystko or ponad or gorzej):
            continue
        ocena = "PONAD PRÓG" if ponad else ("gorzej" if gorzej else "ok")
        wynik.append({"klasa": klasa, "stopien": stopien, "scenariusz": nazwa, "strefa": strefa,
                      "glebokosc": s["glebokosc"], "roznica": roznica, "prog": s["prog"],
                      "co": ("%s → %s" % (s["bron"], s["cialo"])) if s["glebokosc"] > 0 else "-",
                      "t": s["t"], "ocena": ocena, "start": o["glebokosc"] if o else 0.0})
    return wynik


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    from swiat.postacie import stopnie as ST
    ap = argparse.ArgumentParser(description="Przenikanie broni w klipach walki dla kompletów stopni (pomiar)")
    ap.add_argument("--klasa", default=",".join(ST.MODULY), help="klasy po przecinku (domyślnie wszystkie)")
    ap.add_argument("--stopien", default=",".join(ST.STOPNIE), help="stopnie po przecinku (start liczony zawsze)")
    ap.add_argument("--gestosc", type=float, default=1.0, help="gęstość próbek czasu (1 = jak narzędzie przenikania)")
    ap.add_argument("--md", action="store_true", help="tabela Markdown")
    ap.add_argument("--wszystko", action="store_true", help="wszystkie scenariusze i strefy, nie tylko złe miejsca")
    ap.add_argument("--ile", type=int, default=15, help="ile najgorszych miejsc wypisać na końcu")
    a = ap.parse_args()
    klasy = [k for k in a.klasa.split(",") if k]
    stopnie = [s for s in a.stopien.split(",") if s]
    for k in klasy:
        if k not in ST.MODULY:
            ap.error("klasa: %s" % ", ".join(ST.MODULY))
    for s in stopnie:
        if s not in ST.STOPNIE:
            ap.error("stopień: %s" % ", ".join(ST.STOPNIE))

    wszystkie, uwagi = [], []
    t0 = time.time()
    for klasa in klasy:
        odn, zgodny, n = zmierz(klasa, "start", a.gestosc)
        if not zgodny:
            uwagi.append("%s: komplet startowy z stopnie.postac() ma inne bryły niż dane walki — odniesienie liczone "
                         "z bohatera, nie z pliku aktora" % klasa)
        wszystkie += wiersze(klasa, "start", odn, odn, a.wszystko)
        print("# %s start: %d brył, %d pomiarów (%.0f s)" % (klasa, n, len(odn), time.time() - t0), file=sys.stderr,
              flush=True)
        for st in stopnie:
            tab, _, n = zmierz(klasa, st, a.gestosc)
            wszystkie += wiersze(klasa, st, tab, odn, a.wszystko)
            print("# %s %s: %d brył, %d pomiarów (%.0f s)" % (klasa, st, n, len(tab), time.time() - t0),
                  file=sys.stderr, flush=True)

    naglowek = ["klasa", "stopień", "scenariusz (klip)", "strefa", "głębokość", "start", "gorzej o", "co w co",
                "chwila [s]", "ocena"]

    def pola(w):
        return [w["klasa"], w["stopien"], w["scenariusz"], w["strefa"], _l(w["glebokosc"]), _l(w["start"]),
                ("%+.3f" % w["roznica"]).replace(".", ",") if w["stopien"] != "start" else "-", w["co"], _l(w["t"]),
                w["ocena"]]

    def tabela(lista):
        if a.md:
            print("| " + " | ".join(naglowek) + " |")
            print("|" + "|".join(["---"] * len(naglowek)) + "|")
            for w in lista:
                print("| " + " | ".join(pola(w)) + " |")
        else:
            szer = [9, 7, 30, 8, 9, 6, 8, 58, 9, 10]
            print("  ".join(h.ljust(s) for h, s in zip(naglowek, szer)))
            for w in lista:
                print("  ".join(str(x).ljust(s) for x, s in zip(pola(w), szer)))

    print("Przenikanie broni w głowę, nakrycie i tułów — komplety stopni (progi: głowa i nakrycie 0,02, tułów 0,10; "
          "„gorzej” = głębiej niż komplet startowy o ponad %s)" % _l(PROG_GORZEJ))
    print()
    tabela(wszystkie)
    nowe = sorted([w for w in wszystkie if w["stopien"] != "start" and w["ocena"] != "ok"],
                  key=lambda w: (-(w["glebokosc"] - w["prog"]), -w["roznica"]))
    # jedno miejsce = (klasa, stopień, strefa, co w co): najgłębszy scenariusz + w ilu scenariuszach się powtarza
    miejsca = collections.OrderedDict()
    for w in nowe:
        m = miejsca.setdefault((w["klasa"], w["stopien"], w["strefa"], w["co"]), dict(w, ile=0))
        m["ile"] += 1
    najgorsze = []
    for m in miejsca.values():
        if m["ile"] > 1:
            m = dict(m, scenariusz="%s (+%d innych)" % (m["scenariusz"], m["ile"] - 1))
        najgorsze.append(m)
    print()
    print("Najgorsze miejsca nowych kompletów — jedno na parę „broń → bryła” (głębokość ponad próg, potem różnica "
          "względem startowego; w nawiasie liczba dalszych scenariuszy z tym samym miejscem):")
    print()
    tabela(najgorsze[:a.ile])
    print()
    licz = collections.Counter((w["klasa"], w["stopien"], w["ocena"]) for w in wszystkie)
    for klasa in klasy:
        for st in ["start"] + stopnie:
            print("%s / %s: ponad próg %d, gorzej niż start (pod progiem) %d"
                  % (klasa, st, licz[(klasa, st, "PONAD PRÓG")], licz[(klasa, st, "gorzej")]))
    for u in uwagi:
        print("uwaga:", u)
    return 0


if __name__ == "__main__":
    sys.exit(main())
