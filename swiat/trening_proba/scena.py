# -*- coding: utf-8 -*-
"""Arena próby Training Center z prostych części (klocki, jak reszta świata; bez Toolboxa i bez zasobów generowanych).

    python -B swiat/trening_proba/scena.py        # wypisuje liczbę części, obrys i stanowiska

czesci(D) → lista części w układzie świata (środek areny z ustawienia.json + układ lokalny):
    {"n": nazwa, "r": rodzic w kontenerze ("Arena/Sila/Miotacz"), "k": "B" klocek | "C" walec | "K" kula,
     "p": [x, y, z] środek, "s": [x, y, z] rozmiar Roblox, "o": [rx, ry, rz] stopnie (walec: oś już w obrocie),
     "c": kolor hex, "m": materiał, "t": przezroczystość, "kol": CanCollide, "napis": {...} SurfaceGui (opcjonalnie)}
Kolory: nasycone barwy jak w kierunku artystycznym (D-041), tusz do oczu i napisów. Nazwy części, które klient animuje
lokalnie (ramię miotacza, pięść golema, oczy, strefy), pochodzą z dane.NAZWY.
"""
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
if not sys.path or sys.path[0] != TU:
    sys.path.insert(0, TU)
import dane as DANE  # noqa: E402

TUSZ, KREM = "17121F", "FFF6E0"
DREWNO, DREWNO_C = "6B4A2F", "7A5C44"


class _Scena:
    def __init__(self, srodek):
        self.c = srodek
        self.lista = []

    def _sw(self, p):
        return [round(self.c[i] + p[i], 4) for i in range(3)]

    def klocek(self, r, n, p, s, c, m="SmoothPlastic", t=0.0, kol=True, o=None, napis=None, swiat=False):
        d = {"n": n, "r": r, "k": "B", "p": p if swiat else self._sw(p), "s": [round(x, 4) for x in s], "c": c, "m": m}
        if t:
            d["t"] = t
        if not kol:
            d["kol"] = False
        if o:
            d["o"] = o
        if napis:
            d["napis"] = napis
        self.lista.append(d)
        return d

    def walec(self, r, n, p, dl, sr, c, os_="y", m="SmoothPlastic", t=0.0, kol=True, swiat=False):
        o = {"x": None, "y": [0, 0, 90], "z": [0, 90, 0]}[os_]
        d = self.klocek(r, n, p, [dl, sr, sr], c, m, t, kol, o, swiat=swiat)
        d["k"] = "C"
        return d


def _napis(tekst, strona="Back", px=40, kolor=TUSZ):
    return {"tekst": tekst, "strona": strona, "px": px, "kolor": kolor}


def _plus(a, b):
    return [a[i] + b[i] for i in range(3)]


def czesci(D):
    K = DANE._czytaj_json(DANE.USTAWIENIA)
    A = K["arena"]
    sz, gl = A["rozmiar"]
    S = _Scena(A["srodek"])
    kolory = {s["id"]: s["kolor"] for s in D["statystyki"]}

    # --- podłoga, murki, niewidzialne ściany, słupy narożne
    S.klocek("Arena/Podloga", "Plyta", [0, -1, 0], [sz, 2, gl], "BFA37A")
    S.klocek("Arena/Podloga", "Sciezka", [0, 0.05, 10], [60, 0.1, 4], "A98C63")
    for n, p, s in [("MurekN", [0, 1.25, -gl / 2 + 0.5], [sz, 2.5, 1]), ("MurekS", [0, 1.25, gl / 2 - 0.5], [sz, 2.5, 1]),
                    ("MurekW", [-sz / 2 + 0.5, 1.25, 0], [1, 2.5, gl - 2]), ("MurekE", [sz / 2 - 0.5, 1.25, 0], [1, 2.5, gl - 2])]:
        S.klocek("Arena/Mury", n, p, s, DREWNO_C)
    for n, p, s in [("ScianaN", [0, 7, -gl / 2 - 0.5], [sz + 2, 14, 1]), ("ScianaS", [0, 7, gl / 2 + 0.5], [sz + 2, 14, 1]),
                    ("ScianaW", [-sz / 2 - 0.5, 7, 0], [1, 14, gl + 2]), ("ScianaE", [sz / 2 + 0.5, 7, 0], [1, 14, gl + 2])]:
        S.klocek("Arena/Mury", n, p, s, KREM, t=1.0)
    for i, (x, z) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
        px, pz = x * (sz / 2 - 2), z * (gl / 2 - 2)
        S.klocek("Arena/Mury", "Slup%d" % (i + 1), [px, 4, pz], [3, 8, 3], DREWNO_C)
        S.klocek("Arena/Mury", "Czapa%d" % (i + 1), [px, 8.4, pz], [3.6, 0.8, 3.6], "F2B630")

    # --- lobby: punkt przybycia, tablica wyboru (E), wyjście (E)
    pr = A["przybycie"]
    S.walec("Arena/Lobby", "Przybycie", [pr[0], 0.1, pr[2]], 0.2, 5, "F2B630")
    tw = [0, 0, 6]
    for i, dx in enumerate((-3.2, 3.2)):
        S.klocek("Arena/Lobby/TablicaWyboru", "Noga%d" % (i + 1), _plus(tw, [dx, 2.5, 0]), [0.6, 5, 0.6], DREWNO)
    S.klocek("Arena/Lobby/TablicaWyboru", "Deska", _plus(tw, [0, 4.2, 0]), [7, 3, 0.4], KREM,
             napis=_napis(D["teksty"]["tablica_wyboru"]))
    S.klocek("Arena/Lobby/TablicaWyboru", "E", _plus(tw, [0, 3, 0.7]), [0.6, 0.6, 0.6], KREM, t=1.0, kol=False)
    wy = [0, 0, 24]
    for i, dx in enumerate((-3.5, 3.5)):
        S.klocek("Arena/Lobby/Wyjscie", "Filar%d" % (i + 1), _plus(wy, [dx, 3.5, 0]), [1.2, 7, 1.2], DREWNO_C)
    S.klocek("Arena/Lobby/Wyjscie", "Belka", _plus(wy, [0, 7.4, 0]), [8.2, 1.2, 1.4], "E5533D")
    S.klocek("Arena/Lobby/Wyjscie", "Szyld", _plus(wy, [0, 5.6, -0.3]), [5.8, 1.4, 0.3], KREM,
             napis=_napis(D["teksty"]["wyjscie"], "Front"))
    S.klocek("Arena/Lobby/Wyjscie", "E", _plus(wy, [0, 3, -0.8]), [0.6, 0.6, 0.6], KREM, t=1.0, kol=False)

    # --- stanowisko Siły: podest, strefy ciosu, miotacz, stos skrzynek, szyld
    st = K["stanowiska"]["sila"]
    pd = st["podest"]
    S.walec("Arena/Sila", "Podest", _plus(pd, [0, 0.1, 0]), 0.2, 6, kolory["sila"])
    for k, v in st["strefy"].items():
        S.walec("Arena/Sila/Strefy", k, _plus(pd, v), 0.15, 1.8, KREM, os_="z", m="Neon", t=0.7, kol=False)
    m = _plus(pd, st["miotacz"])
    r = "Arena/Sila/Miotacz"
    S.walec(r, "Mata", _plus(m, [0, 0.1, 0]), 0.2, 5, "C9B184")
    for n, p, s, c in [("NogaL", [-0.6, 1.3, 0], [1, 2.6, 1], "4A4E69"), ("NogaP", [0.6, 1.3, 0], [1, 2.6, 1], "4A4E69"),
                       ("Tulow", [0, 4.1, 0], [3, 3, 1.6], "F28C28"), ("Fartuch", [0, 3.6, 0.86], [2.4, 2.2, 0.12], DREWNO),
                       ("Glowa", [0, 6.6, 0], [2, 2, 2], "E8B98A"), ("Opaska", [0, 7.25, 0], [2.1, 0.45, 2.1], "3DBE5A"),
                       ("OkoL", [-0.45, 6.75, 1.02], [0.3, 0.4, 0.05], TUSZ), ("OkoP", [0.45, 6.75, 1.02], [0.3, 0.4, 0.05], TUSZ),
                       ("Usmiech", [0, 6.15, 1.02], [0.9, 0.15, 0.05], TUSZ), ("RamieL", [-2, 4.3, 0], [1, 2.8, 1], "E8B98A"),
                       ("RamieP", [2, 4.3, 0], [1, 2.8, 1], "E8B98A")]:
        S.klocek(r, n, _plus(m, p), s, c, kol=n.startswith("Noga") or n == "Tulow")
    for i, (p, s, c) in enumerate([([3.8, 0.8, -0.6], 1.6, "B07A45"), ([3.8, 2.3, -0.6], 1.4, "C48A52"),
                                   ([5.5, 0.8, -0.2], 1.6, "B07A45")]):
        S.klocek("Arena/Sila/Skrzynie", "Skrzynia%d" % (i + 1), _plus(m, p), [s, s, s], c)
    for i, dx in enumerate((-5.2, 5.2)):
        S.klocek("Arena/Sila/Szyld", "Slupek%d" % (i + 1), _plus(m, [dx, 5.2, -1.5]), [0.5, 10.4, 0.5], DREWNO)
    st_s = [s for s in D["statystyki"] if s["id"] == "sila"][0]
    S.klocek("Arena/Sila/Szyld", "Deska", _plus(m, [0, 10.5, -1.5]), [10, 2, 0.4], KREM,
             napis=_napis("%s — %s" % (st_s["nazwa"].upper(), st_s["gra"].upper())))

    # --- stanowisko Pancerza: podest, golem z pięścią w rękawicy, szyld
    st = K["stanowiska"]["pancerz"]
    pd = st["podest"]
    S.walec("Arena/Pancerz", "Podest", _plus(pd, [0, 0.1, 0]), 0.2, 6, kolory["pancerz"])
    g = _plus(pd, st["golem"])
    r = "Arena/Pancerz/Golem"
    S.walec(r, "Mata", _plus(g, [0, 0.1, 0]), 0.2, 7, "C9B184")
    for n, p, s, c, extra in [("NogaL", [-1.4, 1.5, 0], [2, 3, 2], "8C8C99", {}), ("NogaP", [1.4, 1.5, 0], [2, 3, 2], "8C8C99", {}),
                              ("Tulow", [0, 5, 0], [5, 4, 3], "9A9AA8", {}), ("Pas", [0, 3.2, 0], [5.2, 0.6, 3.2], DREWNO, {}),
                              ("Glowa", [0, 8.2, 0.2], [3, 2.4, 2.6], "A8A8B6", {}),
                              ("OkoL", [-0.7, 8.4, 1.53], [0.6, 0.4, 0.06], "3DA5FF", {"m": "Neon", "kol": False}),
                              ("OkoP", [0.7, 8.4, 1.53], [0.6, 0.4, 0.06], "3DA5FF", {"m": "Neon", "kol": False}),
                              ("RamieL", [-3.3, 5.2, 0], [1.6, 3.6, 1.6], "8C8C99", {}),
                              ("PiescL", [-3.3, 3, 0.3], [2, 2, 2], "9A9AA8", {}),
                              ("RamieP", [3.3, 6, 0], [1.6, 2.4, 1.6], "8C8C99", {})]:
        S.klocek(r, n, _plus(g, p), s, c, m=extra.get("m", "SmoothPlastic"), kol=extra.get("kol", True))
    S.klocek(r, "Piesc", _plus(g, st["piesc_spoczynek"]), [2.4, 2.4, 2.4], "E5533D", kol=False)
    for i, dx in enumerate((-5.2, 5.2)):
        S.klocek("Arena/Pancerz/Szyld", "Slupek%d" % (i + 1), _plus(g, [dx, 6.2, -2.5]), [0.5, 12.4, 0.5], DREWNO)
    st_p = [s for s in D["statystyki"] if s["id"] == "pancerz"][0]
    S.klocek("Arena/Pancerz/Szyld", "Deska", _plus(g, [0, 12.5, -2.5]), [10, 2, 0.4], KREM,
             napis=_napis("%s — %s" % (st_p["nazwa"].upper(), st_p["gra"].upper())))

    # --- cztery zapowiedzi „w projekcie” pod tylnym murkiem
    w_projekcie = [s for s in D["statystyki"] if s["stan"] != "grywalna"]
    for i, s in enumerate(w_projekcie):
        x = -12 + 8 * i
        r = "Arena/Zapowiedzi/%s" % s["id"]
        S.walec(r, "Podest", [x, 0.1, -20], 0.2, 6.5, s["kolor"])
        for j, dx in enumerate((-3.2, 3.2)):
            S.klocek(r, "Noga%d" % (j + 1), [x + dx, 1.5, -23], [0.5, 3, 0.5], DREWNO)
        S.klocek(r, "Deska", [x, 3.1, -23], [7, 3.2, 0.4], KREM,
                 napis=_napis("%s\n%s\n%s" % (s["nazwa"].upper(), s["gra"], D["teksty"]["w_projekcie"]), px=34))
    return S.lista


def obrys(D):
    """(min, max) części areny w świecie (bez obrotu walców — walce mają równe średnice w obu osiach poprzecznych)."""
    mn, mx = [1e9] * 3, [-1e9] * 3
    for c in czesci(D):
        s = c["s"]
        if c["k"] == "C" and c.get("o") == [0, 0, 90]:
            s = [s[1], s[0], s[2]]
        elif c["k"] == "C" and c.get("o") == [0, 90, 0]:
            s = [s[2], s[1], s[0]]
        for i in range(3):
            mn[i] = min(mn[i], c["p"][i] - s[i] / 2)
            mx[i] = max(mx[i], c["p"][i] + s[i] / 2)
    return mn, mx


def rozmiar_osiowy(c):
    s = c["s"]
    if c["k"] == "C" and c.get("o") == [0, 0, 90]:
        return [s[1], s[0], s[2]]
    if c["k"] == "C" and c.get("o") == [0, 90, 0]:
        return [s[2], s[1], s[0]]
    return s


if __name__ == "__main__":
    for strumien in (sys.stdout,):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    _, D = DANE.wczytaj()
    cz = czesci(D)
    mn, mx = obrys(D)
    print("części: %d, obrys %s – %s" % (len(cz), [round(x, 1) for x in mn], [round(x, 1) for x in mx]))
