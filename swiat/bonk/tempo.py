#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rachunek tempa BONK (bez Studio): pierwszy BONK, pierwsza pałka, pierwsze jajko, Strażnicy i bramy.

    python -B swiat/bonk/tempo.py            # przebieg (zakupy, wyklucia, Strażnicy, bramy); kod 1, gdy poza celami
    python -B swiat/bonk/tempo.py --krotko   # same czasy
    python -B swiat/bonk/tempo.py --bez-dodatkow   # etap 1: bez pałek, petów i Strażników (dla porównania)

Model (liczby w ustawienia.json → tempo_model): gracz uderza `klikow_na_s` razy na sekundę, na dojście do kolejnego
potwora traci `narzut_s`; w każdej chwili stoi w tej zagrodzie otwartych krain, w której Moc rośnie najszybciej
(z rzadkim potworem jako wartością oczekiwaną). Moc = floor(Moc z uderzeń × mnożnik pałki × mnożnik petów) — jak
L.moc. Zakupy: gdy gracza stać, kupuje to (następną pałkę albo jajko najdalszej otwartej krainy), co daje największy
przyrost mnożnika (log) na monetę; zakup kosztuje `zakup_s`. Wyklucia „średnim szczęściem”: k-te jajko daje rzadkość
o największym niedoborze k × szansa − dotąd wyklute (deterministycznie, zgodnie z szansami). Mnożnik petów jak
L.mnoznikPetow: 1 + suma premii najlepszych `maks_aktywnych`. Strażnik: gdy Moc ≥ wymagana Moc bramy, gracz idzie na
arenę (`dojscie_do_straznika_s`) i bije go sam (życie / (Moc × klikow_na_s)), dostaje całą nagrodę, potem przechodzi
bramę (`zmiana_krainy_s`). Brama 3 prowadzi do „COMING SOON” — symulacja kończy się w Dżungli.
"""
import json
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))


def ustawienia():
    with open(os.path.join(TU, "ustawienia.json"), encoding="utf-8") as f:
        return json.load(f)


def zagrody(U):
    """[(nr krainy od 0, gatunek, życie, Moc za BONK, monety)] w kolejności krain i zagród."""
    w = []
    for i, K in enumerate(U["krainy"]):
        for z in K["zagrody"]:
            G = U["gatunki"][z["gatunek"]]
            w.append((i, z["gatunek"], G["hp"], G["moc"], G["monety"]))
    return w


def tempo_zysku(U, moc, hp, zysk, monety=0):
    """Oczekiwany przyrost (Mocy, monet) na sekundę w zagrodzie (z rzadkim potworem). Bez `monety` — sama Moc."""
    T, R = U["tempo_model"], U["rzadki"]
    t = T["narzut_s"] + math.ceil(hp / moc) / T["klikow_na_s"]
    tr = T["narzut_s"] + math.ceil(hp * R["hp_x"] / moc) / T["klikow_na_s"]
    s = R["szansa"]
    czas = (1 - s) * t + s * tr
    r_moc = ((1 - s) * zysk + s * zysk * R["moc_x"]) / czas
    if not monety:
        return r_moc
    return r_moc, ((1 - s) * monety + s * monety * R["monety_x"]) / czas


def rzadkosc_wyklucia(k, wyklute, szanse):
    """k-te wyklucie (od 1) „średnim szczęściem”: rzadkość o największym niedoborze k × szansa − wyklute."""
    return max(range(len(szanse)), key=lambda i: (k * szanse[i] - wyklute[i], -i))


def mnoznik_petow(premie, maks):
    return 1 + sum(sorted(premie, reverse=True)[:maks])


def mnoznik_palki(U, stopien):
    return U["palki"]["lista"][stopien - 1]["mnoznik"] if stopien > 0 else U["moc"]["mnoznik_palki"]


def przebieg(U, limit_s=7200, dodatki=True):
    """Symulacja co krok_s. Zwraca (zdarzenia [(czas s, opis, Moc)], czasy {nazwa: s}, pierwszy BONK [s])."""
    T = U["tempo_model"]
    Z = zagrody(U)
    bramy = [K["brama"]["wymagana_moc"] for K in U["krainy"]]
    palki = U["palki"]["lista"]
    szanse = [r["szansa"] for r in U["rzadkosci"]]
    maks = U["pety"]["maks_aktywnych"]
    straz = {s["kraina"]: s for s in U["straznicy"]}
    baza, monety, t, kraina, palka, gdzie = float(U["moc"]["start"]), 0.0, 0.0, 0, 0, None
    premie, wyklute, nr_jajka = [], [0] * len(szanse), 0
    zdarzenia, czasy = [], {}
    # pierwszy BONK: od startu do pierwszej zagrody (dojście) + jeden cios w potwora o życiu 1
    pierwszy = T["narzut_s"] * 3 + 1 / T["klikow_na_s"]

    def moc():
        return max(1, math.floor(baza * mnoznik_palki(U, palka) * mnoznik_petow(premie, maks) + 1e-9))

    while t < limit_s and kraina < len(bramy) - 1:
        M = moc()
        kand = [(tempo_zysku(U, M, hp, z, m), g) for k, g, hp, z, m in Z if k <= kraina]
        (r_moc, r_mon), g = max(kand)
        if g != gdzie:
            if gdzie is not None:
                t += T["zmiana_zagrody_s"]
            zdarzenia.append((t, "zagroda " + g, M))
            gdzie = g
        baza += r_moc * T["krok_s"]
        monety += r_mon * T["krok_s"]
        t += T["krok_s"]
        while dodatki:
            opcje = []
            if palka < len(palki) and monety >= palki[palka]["cena"]:
                zysk = palki[palka]["mnoznik"] / mnoznik_palki(U, palka)
                opcje.append((math.log(zysk) / palki[palka]["cena"], "palka"))
            J = U["jajka"][kraina]
            if monety >= J["cena"]:
                r = rzadkosc_wyklucia(nr_jajka + 1, wyklute, szanse)
                zysk = mnoznik_petow(premie + [J["premie"][r]], maks) / mnoznik_petow(premie, maks)
                if zysk > 1 + 1e-9:
                    opcje.append((math.log(zysk) / J["cena"], "jajko"))
            if not opcje:
                break
            if max(opcje)[1] == "palka":
                monety -= palki[palka]["cena"]
                palka += 1
                zdarzenia.append((t, "PAŁKA %d (%s ×%g)" % (palka, palki[palka - 1]["nazwa"], palki[palka - 1]["mnoznik"]), moc()))
                czasy.setdefault("pierwsza_palka", t)
            else:
                monety -= J["cena"]
                nr_jajka += 1
                r = rzadkosc_wyklucia(nr_jajka, wyklute, szanse)
                wyklute[r] += 1
                premie.append(J["premie"][r])
                zdarzenia.append((t, "JAJKO %s → %s (+%g)" % (J["nazwa"], U["rzadkosci"][r]["nazwa"], J["premie"][r]), moc()))
                czasy.setdefault("pierwsze_jajko", t)
            t += T["zakup_s"]
        M = moc()
        if M >= bramy[kraina]:
            if dodatki:
                S = straz[U["krainy"][kraina]["id"]]
                walka = S["hp"] / (M * T["klikow_na_s"])
                t += T["dojscie_do_straznika_s"] + walka
                baza += S["moc"]
                monety += S["monety"]
                zdarzenia.append((t, "STRAŻNIK %s (%.0f s walki)" % (S["nazwa"], walka), moc()))
            zdarzenia.append((t, "BRAMA %d (%s)" % (kraina + 1, U["krainy"][kraina]["brama"]["dokad"]), moc()))
            czasy["brama_%d" % (kraina + 1)] = t
            kraina += 1
            t += T["zmiana_krainy_s"]
    return zdarzenia, czasy, pierwszy


def czas_solo_straznika(U, nr):
    """Sekundy walki samotnego gracza z Mocą bramy krainy nr (od 0) przeciw Strażnikowi tej krainy."""
    K = U["krainy"][nr]
    S = next(s for s in U["straznicy"] if s["kraina"] == K["id"])
    return S["hp"] / (K["brama"]["wymagana_moc"] * U["tempo_model"]["klikow_na_s"])


def w_celach(U, czasy, pierwszy):
    C = U["tempo_model"]["cele_min"]
    zle = []
    if pierwszy / 60 > C["pierwszy_bonk"]:
        zle.append("pierwszy BONK po %.0f s (cel ≤ %.0f s)" % (pierwszy, C["pierwszy_bonk"] * 60))
    for klucz in ("pierwsza_palka", "pierwsze_jajko", "brama_1", "brama_2"):
        od, do = C[klucz]
        if klucz not in czasy:
            zle.append("%s: nie w limicie" % klucz)
        elif not od <= czasy[klucz] / 60 <= do:
            zle.append("%s po %.1f min (cel %g–%g min)" % (klucz, czasy[klucz] / 60, od, do))
    lo, hi = U["straznik"]["czas_solo_s"]
    for nr in range(len(U["krainy"])):
        c = czas_solo_straznika(U, nr)
        if not lo <= c <= hi:
            zle.append("Strażnik %d sam w %.0f s (cel %g–%g s)" % (nr + 1, c, lo, hi))
    return zle


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    U = ustawienia()
    dodatki = "--bez-dodatkow" not in sys.argv
    zdarzenia, czasy, pierwszy = przebieg(U, dodatki=dodatki)
    if "--krotko" not in sys.argv:
        for t, opis, moc in zdarzenia:
            print("%6.1f min  %-44s Moc %s" % (t / 60, opis, format(int(moc), ",").replace(",", " ")))
    print("pierwszy BONK: %.0f s; %s" % (pierwszy, ", ".join("%s %.1f min" % (k, v / 60) for k, v in sorted(czasy.items(), key=lambda x: x[1]))))
    print("Strażnicy sami (Moc bramy): %s" % ", ".join("%.0f s" % czas_solo_straznika(U, i) for i in range(len(U["krainy"]))))
    if not dodatki:
        return 0
    zle = w_celach(U, czasy, pierwszy)
    print("cele: " + ("w celach" if not zle else "POZA CELAMI: " + "; ".join(zle)))
    return 1 if zle else 0


if __name__ == "__main__":
    sys.exit(main())
