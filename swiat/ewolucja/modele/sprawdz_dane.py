#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sprawdzian danych gry BEZ Studio: odtwarza klipy z dane/*.json tak, jak zrobi to gra (Motor6D: C0 · Transform · C1⁻¹),
i sprawdza zdrowy rozsądek: komplet stawów i klipów, zdarzenia w zakresie, pysk idzie do przodu przy ugryzieniu,
stopy nie wchodzą głęboko pod ziemię w chodzie, pętle się domykają.

    python -B swiat/ewolucja/modele/sprawdz_dane.py
"""
import json
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TU)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.postacie.biblioteka.postac import macierz_obrotu, mnoz, razy_wektor, I3  # noqa: E402
from swiat.ewolucja.modele import smok_klipy as sk, smok_model as sm  # noqa: E402

DANE = os.path.join(TU, "dane")


def wczytaj(nazwa):
    with open(os.path.join(DANE, nazwa), encoding="utf-8") as f:
        return json.load(f)


def poza(rig, klip, nr_probki):
    """{indeks kości: (R, t)} — układ części kości w świecie dla próbki klipu (None = spoczynek)."""
    tr = {}
    if klip is not None:
        w, o = klip["probki"][nr_probki], 0
        for i in klip["stawy"]:
            p = (0.0, 0.0, 0.0)
            if i in klip["przes"]:
                p = tuple(v / 1000.0 for v in w[o:o + 3])
                o += 3
            r = [v / 10.0 for v in w[o:o + 3]]
            o += 3
            tr[i] = (macierz_obrotu(*r), p)                    # fromOrientation = Ry · Rx · Rz, jak macierz_obrotu
        assert o == len(w), "długość wiersza próbki nie pasuje do listy stawów"
    swiat = {0: (I3, tuple(rig["hrp"]))}
    for i, k in enumerate(rig["kosci"], 1):
        Rp, tp = swiat[k[1]]
        srodek_rodzica = tuple(rig["hrp"]) if k[1] == 0 else tuple(rig["kosci"][k[1] - 1][5:8])
        staw, srodek = k[2:5], k[5:8]
        c0 = tuple(staw[j] - srodek_rodzica[j] for j in range(3))
        c1 = tuple(staw[j] - srodek[j] for j in range(3))
        R, p = tr.get(i, (I3, (0.0, 0.0, 0.0)))
        Rw = mnoz(Rp, R)
        a = razy_wektor(Rp, tuple(c0[j] + p[j] for j in range(3)))
        b = razy_wektor(Rw, c1)
        swiat[i] = (Rw, tuple(tp[j] + a[j] - b[j] for j in range(3)))
    return swiat


def punkt_zaczepu(rig, swiat, nazwa):
    z = next(x for x in rig["zaczepy"] if x[0] == nazwa)
    R, t = swiat[z[1]]
    v = razy_wektor(R, z[2:5])
    return tuple(t[j] + v[j] for j in range(3))


def najnizszy(rig, swiat):
    """Najniższy punkt części nóg (przybliżenie: środek części minus pół przekątnej pionowej)."""
    nogi = {i for i, k in enumerate(rig["kosci"], 1) if k[0].startswith("Noga")}
    srodki = {i: tuple(k[5:8]) for i, k in enumerate(rig["kosci"], 1)}
    y = 1e9
    for c in rig["czesci"]:
        if c[0] in nogi:
            R, t = swiat[c[0]]
            v = razy_wektor(R, tuple(c[3 + j] - srodki[c[0]][j] for j in range(3)))
            y = min(y, t[1] + v[1] - c[10] / 2.0)
    return y


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    indeks = wczytaj("indeks.json")
    klipy_wszystkie = set(sk.KLIPY_PODSTAWOWE) | set(sk.KLIPY_DODATKOWE)
    bledy = 0
    for s in indeks["stadia"]:
        if not s["id"].startswith("smok_") or s["id"] == "smok_jajo":
            continue
        rig, kl = wczytaj(s["id"] + "_rig.json"), wczytaj(s["id"] + "_klipy.json")
        uwagi = []
        if [k[0] for k in rig["kosci"]] != list(sm.KOSCI):
            uwagi.append("stawy inne niż KOSCI")
        if set(kl["klipy"]) != klipy_wszystkie:
            uwagi.append("brak klipów: %s" % sorted(klipy_wszystkie - set(kl["klipy"])))
        if {z[0] for z in rig["zaczepy"]} != set(sm.ZACZEPY):
            uwagi.append("zaczepy inne niż ZACZEPY")
        for n, k in kl["klipy"].items():
            if len(k["probki"]) != k["dl"] // kl["krok"] + 1:
                uwagi.append("%s: liczba próbek" % n)
            if any(not 0 <= f <= k["dl"] for f in k["zdarzenia"].values()):
                uwagi.append("%s: zdarzenie poza klipem" % n)
            if k["petla"] and max(abs(a - b) for a, b in zip(k["probki"][0], k["probki"][-1])) > 2:
                uwagi.append("%s: pętla się nie domyka" % n)
        spocz = poza(rig, None, 0)
        pysk0 = punkt_zaczepu(rig, spocz, "PyskAttachment")
        g = kl["klipy"]["gryz3"]
        pysk1 = punkt_zaczepu(rig, poza(rig, g, g["zdarzenia"]["ugryzienie"] // kl["krok"]), "PyskAttachment")
        wypad = pysk0[2] - pysk1[2]                              # przód to −Z
        if wypad < 0.15 * s["promien_gry"]:
            uwagi.append("gryz3: pysk nie idzie do przodu (%.2f)" % wypad)
        ch = kl["klipy"]["chod"]
        dol = min(najnizszy(rig, poza(rig, ch, i)) for i in range(len(ch["probki"])))
        if dol < -0.12 * s["promien_gry"] - 0.15:
            uwagi.append("chod: stopy %.2f pod ziemią" % -dol)
        z = kl["klipy"]["ogon_zamach"]
        konce = [punkt_zaczepu(rig, poza(rig, z, i), "OgonKoniecAttachment") for i in range(len(z["probki"]))]
        zasieg = max(math.hypot(p[0], p[2]) for p in konce)
        print("%-10s części %3d  klipy %2d  wypad pyska %.2f  stopy min %.2f  zasięg ogona %.1f  (promień gry %.1f)%s" % (
            s["id"], rig["liczba_czesci"], len(kl["klipy"]), wypad, dol, zasieg, s["promien_gry"],
            ("  UWAGI: " + "; ".join(uwagi)) if uwagi else "  OK"))
        bledy += len(uwagi)
    print("RAZEM uwag: %d" % bledy)
    return 1 if bledy else 0


if __name__ == "__main__":
    sys.exit(main())
