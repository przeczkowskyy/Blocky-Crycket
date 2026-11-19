#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rachunek tempa BONK (bez Studio): kiedy gracz bez dodatków (bez pałek i petów) robi pierwszy BONK i otwiera bramy.

    python -B swiat/bonk/tempo.py            # przebieg minuta po minucie i czasy bram; kod 1, gdy poza celami
    python -B swiat/bonk/tempo.py --krotko   # same czasy

Model (liczby w ustawienia.json → tempo_model): gracz uderza `klikow_na_s` razy na sekundę, na dojście do kolejnego
potwora traci `narzut_s`; w każdej chwili stoi w tej zagrodzie otwartych krain, w której Moc rośnie najszybciej
(z rzadkim potworem liczonym jako wartość oczekiwana); zmiana zagrody kosztuje `zmiana_zagrody_s`, przejście bramy
`zmiana_krainy_s`. Odrodzenie (2–4 s przy 4–5 potworach w zagrodzie) nie ogranicza tempa przy tym narzucie.
To ten sam rachunek co L.moc / L.nagroda / L.zycie w zrodla/LogikaBonk.luau (test_bonk.py porównuje oba).
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
    """[(nr krainy od 0, gatunek, życie, Moc za BONK)] w kolejności krain i zagród."""
    w = []
    for i, K in enumerate(U["krainy"]):
        for z in K["zagrody"]:
            G = U["gatunki"][z["gatunek"]]
            w.append((i, z["gatunek"], G["hp"], G["moc"]))
    return w


def tempo_zysku(U, moc, hp, zysk):
    """Oczekiwany przyrost Mocy na sekundę w zagrodzie (z rzadkim potworem)."""
    T, R = U["tempo_model"], U["rzadki"]
    t = T["narzut_s"] + math.ceil(hp / moc) / T["klikow_na_s"]
    tr = T["narzut_s"] + math.ceil(hp * R["hp_x"] / moc) / T["klikow_na_s"]
    s = R["szansa"]
    return ((1 - s) * zysk + s * zysk * R["moc_x"]) / ((1 - s) * t + s * tr)


def przebieg(U, limit_s=7200):
    """Symulacja co krok_s. Zwraca (zdarzenia [(czas s, opis, Moc)], czasy bram [s], pierwszy BONK [s])."""
    T = U["tempo_model"]
    Z = zagrody(U)
    bramy = [K["brama"]["wymagana_moc"] for K in U["krainy"]]
    moc, t, kraina, gdzie = float(U["moc"]["start"]), 0.0, 0, None
    zdarzenia, czasy = [], []
    # pierwszy BONK: od startu do pierwszej zagrody (dojście) + jeden cios w potwora o życiu 1
    pierwszy = T["narzut_s"] * 3 + 1 / T["klikow_na_s"]
    while t < limit_s and kraina < len(bramy):
        kand = [(tempo_zysku(U, moc, hp, z), g) for k, g, hp, z in Z if k <= kraina]
        r, g = max(kand)
        if g != gdzie:
            if gdzie is not None:
                t += T["zmiana_zagrody_s"]
            zdarzenia.append((t, "zagroda " + g, moc))
            gdzie = g
        moc += r * T["krok_s"]
        t += T["krok_s"]
        if moc >= bramy[kraina]:
            zdarzenia.append((t, "BRAMA %d (%s)" % (kraina + 1, U["krainy"][kraina]["brama"]["dokad"]), moc))
            czasy.append(t)
            kraina += 1
            t += T["zmiana_krainy_s"]
    return zdarzenia, czasy, pierwszy


def w_celach(U, czasy, pierwszy):
    C = U["tempo_model"]["cele_min"]
    zle = []
    if pierwszy / 60 > C["pierwszy_bonk"]:
        zle.append("pierwszy BONK po %.0f s (cel ≤ %.0f s)" % (pierwszy, C["pierwszy_bonk"] * 60))
    for i, klucz in enumerate(("brama_1", "brama_2", "brama_3")):
        od, do = C[klucz]
        if i >= len(czasy):
            zle.append("%s: nie otwarta w limicie" % klucz)
        elif not od <= czasy[i] / 60 <= do:
            zle.append("%s po %.1f min (cel %g–%g min)" % (klucz, czasy[i] / 60, od, do))
    return zle


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    U = ustawienia()
    zdarzenia, czasy, pierwszy = przebieg(U)
    if "--krotko" not in sys.argv:
        for t, opis, moc in zdarzenia:
            print("%6.1f min  %-34s Moc %s" % (t / 60, opis, format(int(moc), ",").replace(",", " ")))
    print("pierwszy BONK: %.0f s; bramy: %s" % (pierwszy, ", ".join("%.1f min" % (c / 60) for c in czasy)))
    zle = w_celach(U, czasy, pierwszy)
    print("cele: " + ("w celach" if not zle else "POZA CELAMI: " + "; ".join(zle)))
    return 1 if zle else 0


if __name__ == "__main__":
    sys.exit(main())
