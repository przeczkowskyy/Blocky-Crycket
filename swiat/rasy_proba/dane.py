# -*- coding: utf-8 -*-
"""Dane wystawy ras (bez Studio): figury sześciu ras i człowieka jako rigi z części Roblox.

    python -B swiat/rasy_proba/dane.py            # tabela figur (części, skala, wzrost)

Źródła: swiat/postacie/rasy.py (model rasy pomnożony przez skalę z danych rasy — rasy.w_skali), goły Rycerz
(rycerz.cialo()) jako człowiek dla porównania, rozkład brył na części Roblox: swiat/postacie/biblioteka/
roblox_klocki.rig (ta sama droga co swiat/postacie/roblox_postac.py, bez wgrywania czegokolwiek). Figury nie mają
klipów w danych — spoczynek liczy skrypt zrodla/SpoczynekRas.server.luau z kątów z ustawienia.json.
Status: propozycja (D-104, etap B).
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.postacie import rasy, rycerz  # noqa: E402
from swiat.postacie.biblioteka.roblox_klocki import rig  # noqa: E402

CZLOWIEK = "czlowiek"


def ustawienia():
    with open(os.path.join(TU, "ustawienia.json"), encoding="utf-8") as f:
        return json.load(f)


def postac(fid):
    """Postać figury w skali rasy (człowiek: goły Rycerz w skali 1), bez klipów."""
    if fid == CZLOWIEK:
        p = rycerz.cialo()
        p.id = "figura_czlowiek"
    else:
        p = rasy.w_skali(rasy.model(fid), id="figura_" + fid)
    p.klipy = []
    p.poza_renderu = None
    return p


def figury(U=None):
    """Lista figur w kolejności z ustawień: id, nazwa, skala, wzrost (czubek głowy), poz, patrz i dane rigu
    (kości, części, materiały, hrp) w układzie Roblox — początek = ziemia pod figurą, przód −Z."""
    U = U or ustawienia()
    wynik = []
    for wpis in U["figury"]:
        fid = wpis["id"]
        skala = 1.0 if fid == CZLOWIEK else float(rasy.RASY[fid]["skala"])
        nazwa = U["nazwa_czlowieka"] if fid == CZLOWIEK else rasy.RASY[fid]["nazwa"]
        r = rig(postac(fid))
        wynik.append({"id": fid, "nazwa": nazwa, "skala": skala, "wzrost": round(U["wzrost_ciala"] * skala, 4),
                      "poz": [float(v) for v in wpis["poz"]], "patrz": [float(v) for v in U["patrz"]],
                      "hrp": r["hrp"], "kosci": r["kosci"], "czesci": r["czesci"], "materialy": r["materialy"],
                      "swiecace": sum(1 for c in r["czesci"] if r["materialy"][c[13]][0] == "Neon"),
                      "uwagi": r["uwagi"]})
    return wynik


def spoczynek(U=None):
    """Kąty szczytu oddechu w układzie rigu Roblox (radiany): {kość: [rx, ry, rz]} — to samo przeliczenie co
    w roblox_klocki (sprzężenie obrotem o 180° wokół pionu): (rx, ry, rz) -> (−rx, ry, −rz)."""
    U = U or ustawienia()
    return {k: [round(math.radians(-v[0]), 5), round(math.radians(v[1]), 5), round(math.radians(-v[2]), 5)]
            for k, v in U["spoczynek"]["kosci"].items()}


def luau(v):
    """Wartość Pythona jako literał Luau (słownik -> tabela z kluczami-nazwami)."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, (list, tuple)):
        return "{" + ",".join(luau(x) for x in v) + "}"
    if isinstance(v, dict):
        return "{" + ",".join("%s=%s" % (k, luau(x)) for k, x in v.items()) + "}"
    raise TypeError(type(v))


def liczba_czesci(f):
    """Ile części BasePart ma figura w Studio: bryły + 15 niewidzialnych części kości + korzeń + tabliczka."""
    return len(f["czesci"]) + len(f["kosci"]) + 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    F = figury()
    for f in F:
        print("%-12s %-12s skala %.2f  wzrost %.2f  bryły %3d  części w Studio %3d  świecące %2d  poz %s"
              % (f["id"], f["nazwa"], f["skala"], f["wzrost"], len(f["czesci"]), liczba_czesci(f), f["swiecace"], f["poz"]))
    print("razem części w Studio: %d" % sum(liczba_czesci(f) for f in F))
