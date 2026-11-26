# -*- coding: utf-8 -*-
"""Czasy biegu ze startu bazaru do każdego punktu E według planu (siatka chodzenia mapy, bez Studio).

Tylko odczyt: swiat/miasteczko_bazar/siatka.py (ta sama siatka co sprawdz.py mapy: krok 0,5, promień postaci 2,
najkrótsza droga z omijaniem przeszkód), czesci.json i uklad.json mapy. Potrzebne numpy i Pillow — gdy ich nie ma,
plan() zwraca None (testy pomijają tę część z uwagą, próba w Studio porównuje wtedy tylko z celami czasu).

    from czasy_biegu import plan
    p = plan(D)   # → { id: { "droga": st, "czas": s, "cel": s albo None } }
"""
import json
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
MAPA = os.path.join(REPO, "swiat", "miasteczko_bazar")


def _siatka():
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    try:
        from swiat.miasteczko_bazar import siatka  # noqa: E402  (tylko odczyt)
    except Exception:  # noqa: BLE001 — brak numpy / Pillow albo zmieniony moduł mapy
        return None
    return siatka


def wczytaj_mape():
    with open(os.path.join(MAPA, "czesci.json"), encoding="utf-8") as f:
        dane = json.load(f)
    with open(os.path.join(MAPA, "uklad.json"), encoding="utf-8") as f:
        uklad = json.load(f)
    return dane, uklad


def siatka_mapy():
    """(moduł siatka, obiekt Siatka, uklad) albo (None, None, None)."""
    siatka = _siatka()
    if siatka is None:
        return None, None, None
    dane, uklad = wczytaj_mape()
    return siatka, siatka.Siatka(dane, uklad), uklad


def plan(D):
    siatka, S, U = siatka_mapy()
    if S is None:
        return None
    X0, Z0 = U["swiat"]["X0"], U["swiat"]["Z0"]
    st = D["start"]["punkt"]
    S.z_punktu(st[0] - X0, st[2] - Z0)
    v = U["bieg_st_s"]
    cele = U["cele_czasu"]
    wynik = {}
    for mid in D["kolejnosc"]:
        m = D["miejsca"][mid]
        if not m.get("stoisko"):
            continue
        d = float(S.droga_do(m["stoisko"][0] - X0, m["stoisko"][2] - Z0))
        cel = None
        if m["akcja"] == "chmury":
            cel = cele["portal_s"]
        elif m["akcja"] == "okno" and mid not in ("tablica", "dzialka"):
            cel = cele["sklep_s"]
        wynik[mid] = {"droga": round(d, 2) if math.isfinite(d) else None,
                      "czas": round(d / v, 2) if math.isfinite(d) else None, "cel": cel}
    return wynik


def punkty_przy_scianach(D):
    """Dla każdego brzegu pola gry osiągalny ze startu punkt świata najbliżej niewidzialnej ściany (dla próby
    w Studio: marsz na zewnątrz). → { "zachod" | "wschod" | "polnoc" | "poludnie": [x, y, z] } albo None."""
    siatka, S, U = siatka_mapy()
    if S is None:
        return None
    import numpy as np  # noqa: E402  (jest, skoro jest siatka)
    X0, Z0 = U["swiat"]["X0"], U["swiat"]["Z0"]
    st = D["start"]["punkt"]
    odl = S.z_punktu(st[0] - X0, st[2] - Z0)
    iz, ix = np.nonzero(np.isfinite(odl))
    xs = S.x0 + (ix + 0.5) * S.krok
    zs = S.z0 + (iz + 0.5) * S.krok
    g = U["granice"]
    wynik = {}
    for nazwa, do_sciany in (("zachod", xs - g["pole_gry_x"][0]), ("wschod", g["pole_gry_x"][1] - xs),
                             ("polnoc", zs - g["pole_gry_z"][0]), ("poludnie", g["pole_gry_z"][1] - zs)):
        i = int(np.argmin(do_sciany))
        wynik[nazwa] = [round(float(xs[i] + X0), 2), st[1], round(float(zs[i] + Z0), 2)]
    return wynik


def wolne_w_siatce(x_swiat, z_swiat):
    """Czy punkt świata jest wolny na siatce chodzenia (z promieniem postaci) — None, gdy brak siatki."""
    siatka, S, U = siatka_mapy()
    if S is None:
        return None
    iz, ix = S.komorka(x_swiat - U["swiat"]["X0"], z_swiat - U["swiat"]["Z0"])
    if not (0 <= iz < S.nz and 0 <= ix < S.nx):
        return False
    return not bool(S.zajete[iz, ix])
