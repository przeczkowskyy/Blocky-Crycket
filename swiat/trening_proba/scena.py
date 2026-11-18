# -*- coding: utf-8 -*-
"""Arena próby Training Center z prostych części (klocki, jak reszta świata; bez Toolboxa i bez zasobów generowanych).

    python -B swiat/trening_proba/scena.py        # wypisuje liczbę części, obrys i stanowiska

czesci(D) → lista części w układzie świata (środek areny z ustawienia.json + układ lokalny):
    {"n": nazwa, "r": rodzic w kontenerze ("Arena/Sila/Miotacz"), "k": "B" klocek | "C" walec | "K" kula,
     "p": [x, y, z] środek, "s": [x, y, z] rozmiar Roblox, "o": [rx, ry, rz] stopnie (walec: oś już w obrocie),
     "c": kolor hex, "m": materiał, "t": przezroczystość, "kol": CanCollide, "napis": {...} SurfaceGui (opcjonalnie)}
Kolory: nasycone barwy jak w kierunku artystycznym (D-041), tusz do oczu i napisów. Nazwy części, które klient animuje
lokalnie (ramię miotacza, pięść golema, oczy, strefy, pasy taśmy Bieżni, cele stóp, bęben i pałka trenera, ramię
z kłodą, znaki run, kula maga, tory Koniczyn), pochodzą z dane.NAZWY. Stanowiska stoją w jednym rzędzie (x od −104 do
+104 st od środka), kamery patrzą na północ (−z); zapowiedź „w projekcie” powstaje tylko dla statystyki bez gry.
"""
import math
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
if not sys.path or sys.path[0] != TU:
    sys.path.insert(0, TU)
import dane as DANE  # noqa: E402

TUSZ, KREM = "17121F", "FFF6E0"
DREWNO, DREWNO_C = "6B4A2F", "7A5C44"
SKORA = "E8B98A"
# kolor znaku runy w spoczynku (jaśniejszy w czasie świecenia — klient); kształty różne, żeby nie liczyć tylko na kolor
ZNAKI_RUN = {"gora": "2A6FB0", "lewo": "A8382A", "prawo": "2A8A40", "dol": "B88A20"}


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

    def kula(self, r, n, p, sr, c, m="SmoothPlastic", t=0.0, kol=True):
        d = self.klocek(r, n, p, [sr, sr, sr], c, m, t, kol)
        d["k"] = "K"
        return d


def _obroc(v, kat):
    """Przesunięcie (x, y, z) obrócone o kat stopni wokół osi Y (jak CFrame.Angles(0, kat, 0) w Roblox)."""
    a = math.radians(kat)
    return [round(v[0] * math.cos(a) + v[2] * math.sin(a), 4), v[1], round(-v[0] * math.sin(a) + v[2] * math.cos(a), 4)]


def _postac(S, r, baza, kat, ubranie, spodnie, dodatki=(), kol=True):
    """Postać z klocków (jak miotacz Siły) twarzą do +z, obrócona o kat stopni wokół Y; dodatki: (nazwa, przesunięcie,
    rozmiar, kolor[, materiał]) w tym samym układzie postaci."""
    czesci = [("NogaL", [-0.6, 1.3, 0], [1, 2.6, 1], spodnie), ("NogaP", [0.6, 1.3, 0], [1, 2.6, 1], spodnie),
              ("Tulow", [0, 4.1, 0], [3, 3, 1.6], ubranie), ("Glowa", [0, 6.6, 0], [2, 2, 2], SKORA),
              ("OkoL", [-0.45, 6.75, 1.02], [0.3, 0.4, 0.05], TUSZ), ("OkoP", [0.45, 6.75, 1.02], [0.3, 0.4, 0.05], TUSZ),
              ("Usmiech", [0, 6.15, 1.02], [0.9, 0.15, 0.05], TUSZ), ("RamieL", [-2, 4.3, 0], [1, 2.8, 1], ubranie),
              ("RamieP", [2, 4.3, 0], [1, 2.8, 1], ubranie)]
    for d in dodatki:
        czesci.append(d)
    for c in czesci:
        n, v, s, kolor = c[0], c[1], c[2], c[3]
        m = c[4] if len(c) > 4 else "SmoothPlastic"
        S.klocek(r, n, _plus(baza, _obroc(v, kat)), s, kolor, m=m, kol=kol and n in ("NogaL", "NogaP", "Tulow"),
                 o=[0, kat, 0] if kat else None)


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

    st_k = {s["id"]: s for s in D["statystyki"]}

    def szyld(r, srodek, wys, gid, szer=10):
        for i, dx in enumerate((-szer / 2 - 0.2, szer / 2 + 0.2)):
            S.klocek(r, "Slupek%d" % (i + 1), _plus(srodek, [dx, wys / 2, 0]), [0.5, wys, 0.5], DREWNO)
        S.klocek(r, "Deska", _plus(srodek, [0, wys, 0]), [szer, 2, 0.4], KREM,
                 napis=_napis("%s — %s" % (st_k[gid]["nazwa"].upper(), st_k[gid]["gra"].upper())))

    # --- stanowiska, które są tylko w PROJEKT.md (stan „w_projekcie”) — zapowiedź pod tylnym murkiem
    w_projekcie = [s for s in D["statystyki"] if s["stan"] != "grywalna"]
    for i, s in enumerate(w_projekcie):
        x = -12 + 8 * i
        r = "Arena/Zapowiedzi/%s" % s["id"]
        S.walec(r, "Podest", [x, 0.1, -20], 0.2, 6.5, s["kolor"])
        for j, dx in enumerate((-3.2, 3.2)):
            S.klocek(r, "Noga%d" % (j + 1), [x + dx, 1.5, -23], [0.5, 3, 0.5], DREWNO)
        S.klocek(r, "Deska", [x, 3.1, -23], [7, 3.2, 0.4], KREM,
                 napis=_napis("%s\n%s\n%s" % (s["nazwa"].upper(), s["gra"], D["teksty"]["w_projekcie"]), px=34))

    # --- Kondycja „Bieżnia”: biegacz twarzą do kamery; ślady stóp jadą na taśmie od przodu (strona kamery) do linii przed
    #     palcami — nic nie stoi między kamerą a śladami; poręcze po bokach, z tyłu tablica, z boku trener z bębnem
    if "kondycja" in K["stanowiska"]:
        st = K["stanowiska"]["kondycja"]
        pd = st["podest"]
        r = "Arena/Kondycja"
        ts, tr = _plus(pd, st["tasma_srodek"]), st["tasma_rozmiar"]
        S.klocek(r + "/Tasma", "Plyta", ts, tr, "2E2A33")
        z0, z1 = ts[2] - tr[2] / 2, ts[2] + tr[2] / 2
        gora_t = ts[1] + tr[1] / 2
        for i in range(st["pasy"]):
            z = z0 + (i + 0.5) * tr[2] / st["pasy"]
            S.klocek(r + "/Tasma", "Pas%d" % (i + 1), [ts[0], gora_t + 0.02, z], [tr[0] - 0.3, 0.05, 0.35], "4A4552", kol=False)
        for n, dx in (("BokL", -tr[0] / 2 - 0.3), ("BokP", tr[0] / 2 + 0.3)):
            S.klocek(r + "/Rama", n, [ts[0] + dx, 0.5, ts[2]], [0.6, 1.0, tr[2] + 0.4], kolory["kondycja"])
        for n, z in (("WalekP", z1 + 0.2), ("WalekT", z0 - 0.2)):
            S.walec(r + "/Rama", n, [ts[0], 0.5, z], tr[0], 1.0, "9AA0A8", os_="x", m="Metal")
        li = _plus(pd, st["linia"])
        S.klocek(r, "Linia", [li[0], gora_t + 0.03, li[2]], [tr[0] - 0.4, 0.05, 0.25], KREM, m="Neon", kol=False)
        for k, v in st["stopy"].items():
            p = _plus(pd, v)
            S.klocek(r + "/Prowadnice", k, [p[0], gora_t + 0.025, (z1 - 0.4 + p[2]) / 2], [0.12, 0.05, z1 - 0.4 - p[2]],
                     KREM, t=0.55, kol=False)
            S.walec(r + "/Cele", k, [p[0], gora_t + 0.04, p[2]], 0.06, 1.4, KREM, os_="y", m="Neon", t=0.55, kol=False)
        for n, dx in (("SlupekL", -tr[0] / 2 - 0.3), ("SlupekP", tr[0] / 2 + 0.3)):
            S.klocek(r + "/Porecze", n, _plus(pd, [dx, 2.1, 1.6]), [0.4, 3.0, 0.4], "9AA0A8", m="Metal")
            S.klocek(r + "/Porecze", n.replace("Slupek", "Drazek"), _plus(pd, [dx, 3.5, -0.2]), [0.35, 0.35, 3.6], "9AA0A8",
                     m="Metal")
        szyld(r + "/Szyld", [ts[0], 0, z0 - 1.0], 4.6, "kondycja", 10)
        tn = _plus(pd, st["trener"])
        _postac(S, r + "/Trener", tn, -50, "2E8B57", "264653",
                [("Opaska", [0, 7.25, 0], [2.1, 0.45, 2.1], "F2B630"), ("Gwizdek", [0.3, 5.3, 0.86], [0.3, 0.3, 0.15], "D8DEE9")])
        bb = _plus(pd, st["beben"])
        S.walec(r + "/Trener", "BebenKorpus", _plus(bb, [0, 2.0, 0]), 1.3, 2.0, "E5533D")
        S.walec(r + "/Trener", "Beben", _plus(bb, [0, 2.7, 0]), 0.08, 2.05, KREM, kol=False)
        for i, (dx, dz) in enumerate(((-0.7, -0.4), (0.7, -0.4), (0, 0.8))):
            S.klocek(r + "/Trener", "NogaBebna%d" % (i + 1), _plus(bb, [dx, 0.7, dz]), [0.2, 1.4, 0.2], DREWNO)

    # --- Zręczność „Kłody”: okrągły plac, słup, ramię z kłodą (obraca klient), drwal
    if "zrecznosc" in K["stanowiska"]:
        st = K["stanowiska"]["zrecznosc"]
        pd = st["podest"]
        r = "Arena/Zrecznosc"
        sl = _plus(pd, st["slup"])
        S.walec(r, "Plac", [sl[0], 0.08, sl[2]], 0.16, 2 * st["ramie"] + 3, "D8C08A")
        S.walec(r, "Podest", _plus(pd, [0, 0.18, 0]), 0.2, 4.6, kolory["zrecznosc"])
        S.walec(r + "/Slup", "Pal", [sl[0], 3.6, sl[2]], 7.2, 1.2, DREWNO, m="WoodPlanks")
        S.kula(r + "/Slup", "Czapa", [sl[0], 7.3, sl[2]], 1.6, "F2B630")
        h = st["wysokosci"]["nisko"]
        sr = st["kloda_srednica"]
        dl = st["ramie"] - 0.6
        S.walec(r + "/Ramie", "Piasta", [sl[0], h, sl[2]], 0.9, 1.9, "9AA0A8", m="Metal", kol=False)
        S.walec(r + "/Ramie", "Kloda", [sl[0] - 0.6 - dl / 2, h, sl[2]], dl, sr, "8C5A3C", os_="x", m="WoodPlanks", kol=False)
        for i, rr in enumerate((3.0, 6.0, st["ramie"] - 0.5)):
            S.walec(r + "/Ramie", "Pas%d" % (i + 1), [sl[0] - rr, h, sl[2]], 0.28, sr + 0.1, "F2B630", os_="x", kol=False)
        S.walec(r + "/Ramie", "Koniec", [sl[0] - st["ramie"] - 0.03, h, sl[2]], 0.06, sr - 0.3, "C48A52", os_="x", kol=False)
        szyld(r + "/Szyld", [sl[0], 0, sl[2] - st["ramie"] - 2.2], 7.6, "zrecznosc")
        tn = _plus(pd, st["trener"])
        _postac(S, r + "/Trener", tn, 54, "C0392B", "264653",
                [("Broda", [0, 6.0, 0.95], [1.6, 0.9, 0.2], "6B3A1F"), ("Czapka", [0, 7.7, 0], [2.1, 0.6, 2.1], "C0392B"),
                 ("Krata1", [0, 4.8, 0.82], [3.02, 0.2, 0.05], TUSZ), ("Krata2", [0, 3.6, 0.82], [3.02, 0.2, 0.05], TUSZ),
                 ("Stylisko", [2.3, 2.4, 0.9], [0.25, 3.6, 0.25], DREWNO), ("Ostrze", [2.3, 4.2, 1.25], [0.15, 0.9, 0.9], "D8DEE9",
                                                                             "Metal")])

    # --- Inteligencja „Runy”: kamienna ściana, cztery kamienie w krzyżu ze znakami (kolor + kształt), mag
    if "inteligencja" in K["stanowiska"]:
        st = K["stanowiska"]["inteligencja"]
        pd = st["podest"]
        r = "Arena/Inteligencja"
        S.walec(r, "Podest", _plus(pd, [0, 0.1, 0]), 0.2, 6, kolory["inteligencja"])
        sc, sr_ = _plus(pd, st["sciana"]), st["sciana_rozmiar"]
        S.klocek(r + "/Luk", "Sciana", sc, sr_, "4A4E69", m="Slate")
        for n, dx in (("KolumnaL", -sr_[0] / 2 - 0.5), ("KolumnaP", sr_[0] / 2 + 0.5)):
            S.klocek(r + "/Luk", n, [sc[0] + dx, sr_[1] / 2 + 0.3, sc[2]], [1.0, sr_[1] + 0.6, 1.2], "6A6E89", m="Slate")
        S.klocek(r + "/Luk", "Belka", [sc[0], sr_[1] + 0.9, sc[2]], [sr_[0] + 2.2, 0.8, 1.3], "6A6E89", m="Slate")
        S.klocek(r + "/Luk", "Deska", [sc[0], sr_[1] + 2.2, sc[2] + 0.2], [10, 1.8, 0.4], KREM,
                 napis=_napis("%s — %s" % (st_k["inteligencja"]["nazwa"].upper(), st_k["inteligencja"]["gra"].upper())))
        ks = st["kamien_rozmiar"]
        for k, v in st["kamienie"].items():
            p = _plus(pd, v)
            rk = r + "/Runy/" + k
            S.klocek(rk, "Kamien", p, ks, "8A8F99", m="Slate")
            zf = p[2] + ks[2] / 2 + 0.03
            c = ZNAKI_RUN[k]
            if k == "gora":  # pierścień
                S.walec(rk, "Znak1", [p[0], p[1], zf], 0.06, 1.8, c, os_="z", kol=False)
                S.walec(rk, "Srodek", [p[0], p[1], zf + 0.02], 0.06, 1.05, "8A8F99", os_="z", kol=False)
            elif k == "lewo":  # kwadrat
                for i, (dx, dy, sx, sy) in enumerate(((0, 0.7, 1.7, 0.32), (0, -0.7, 1.7, 0.32), (-0.7, 0, 0.32, 1.7),
                                                      (0.7, 0, 0.32, 1.7))):
                    S.klocek(rk, "Znak%d" % (i + 1), [p[0] + dx, p[1] + dy, zf], [sx, sy, 0.06], c, kol=False)
            elif k == "prawo":  # romb
                S.klocek(rk, "Znak1", [p[0], p[1], zf], [1.35, 1.35, 0.06], c, kol=False, o=[0, 0, 45])
                S.klocek(rk, "Srodek", [p[0], p[1], zf + 0.02], [0.72, 0.72, 0.06], "8A8F99", kol=False, o=[0, 0, 45])
            else:  # krzyż
                S.klocek(rk, "Znak1", [p[0], p[1], zf], [1.8, 0.42, 0.06], c, kol=False)
                S.klocek(rk, "Znak2", [p[0], p[1], zf], [0.42, 1.8, 0.06], c, kol=False)
        mg = _plus(pd, st["mag"])
        kat_maga = 35
        _postac(S, r + "/Mag", mg, kat_maga, "6C3FB5", "4B2C82",
                [("Szata", [0, 2.0, 0], [3.2, 1.6, 1.8], "6C3FB5"), ("Broda", [0, 5.9, 0.95], [1.4, 1.2, 0.2], "F2F2F2"),
                 ("Kapelusz1", [0, 7.8, 0], [2.6, 0.5, 2.6], "4B2C82"), ("Kapelusz2", [0, 8.4, 0], [1.6, 0.8, 1.6], "4B2C82"),
                 ("Kapelusz3", [0, 9.1, 0], [0.9, 0.7, 0.9], "4B2C82"), ("Laska", [2.4, 3.6, 0.6], [0.3, 7.2, 0.3], DREWNO)])
        S.kula(r + "/Mag", "Kula", _plus(mg, _plus(_obroc([2.4, 0, 0.6], kat_maga), [0, 7.6, 0])), 0.9, "C9A7FF", m="Neon",
               kol=False)

    # --- Szczęście „Koniczyny”: trawa, trzy tory, drzewo z koroną, ogrodnik
    if "szczescie" in K["stanowiska"]:
        st = K["stanowiska"]["szczescie"]
        pd = st["podest"]
        r = "Arena/Szczescie"
        S.klocek(r, "Trawa", _plus(pd, [0, 0.05, -3.5]), [15, 0.1, 13], "7BC24F", kol=False)
        kosz = st["koszyk"]
        for k, v in st["tory"].items():
            S.klocek(r + "/Tory", k, _plus(pd, [v[0], 0.13, kosz[2]]), [2.6, 0.05, 2.6], KREM, t=0.45, kol=False)
        # drzewo z tyłu, korona i gałąź nad torami: koniczyny wypadają spod korony nad koszem trzymanym nad głową
        dz = _plus(pd, st["drzewo"])
        wys = st["spad_y"] + 1.6
        S.klocek(r + "/Drzewo", "Pien", _plus(dz, [0, wys / 2, 0]), [2.4, wys, 2.4], DREWNO, m="WoodPlanks")
        S.klocek(r + "/Drzewo", "Galaz", [dz[0], wys - 0.4, pd[2] + kosz[2] - 2.4], [13.5, 0.8, 0.8], DREWNO, m="WoodPlanks")
        S.klocek(r + "/Drzewo", "Konar", [dz[0], wys - 0.4, (dz[2] + pd[2] + kosz[2] - 2.4) / 2],
                 [0.9, 0.9, pd[2] + kosz[2] - 2.4 - dz[2]], DREWNO, m="WoodPlanks")
        zp = pd[2] + kosz[2] - dz[2]
        for i, (dx, dy, dzz, srn) in enumerate(((-5.2, 3.2, zp - 3.2, 6.0), (0, 3.6, zp - 3.0, 6.6), (5.2, 3.2, zp - 3.2, 6.0),
                                               (-2.6, 5.0, zp - 6.0, 6.0), (2.6, 5.0, zp - 6.0, 6.0), (0, 4.0, 0, 6.4))):
            S.kula(r + "/Drzewo", "Korona%d" % (i + 1), _plus(dz, [dx, wys + dy - 1.2, dzz]), srn, "3E9B3A")
        for i, dx in enumerate((-4.2, 1.0, 4.6)):
            S.kula(r + "/Drzewo", "Owoc%d" % (i + 1), _plus(dz, [dx, wys + 0.2, zp - 1.0]), 0.7, "F2B630", kol=False)
        szyld(r + "/Szyld", _plus(pd, [-9.6, 0, -6.5]), 5.0, "szczescie", 6.2)
        og = _plus(pd, st["ogrodnik"])
        _postac(S, r + "/Ogrodnik", og, -30, "2EC4B6", "6B4A2F",
                [("Fartuch", [0, 3.6, 0.86], [2.4, 2.2, 0.12], "3DBE5A"),
                 ("Konewka", [2.3, 2.6, 0.9], [1.0, 1.0, 0.8], "9AA0A8", "Metal")])
        S.walec(r + "/Ogrodnik", "Kapelusz", _plus(og, [0, 7.65, 0]), 0.3, 3.2, "E8C872", kol=False)
    return S.lista


def obrys(D):
    """(min, max) części areny w świecie (pudła osiowe obróconych części — rozmiar_osiowy)."""
    mn, mx = [1e9] * 3, [-1e9] * 3
    for c in czesci(D):
        s = rozmiar_osiowy(c)
        for i in range(3):
            mn[i] = min(mn[i], c["p"][i] - s[i] / 2)
            mx[i] = max(mx[i], c["p"][i] + s[i] / 2)
    return mn, mx


def macierz(o):
    """Macierz obrotu CFrame.Angles(rx, ry, rz) (stopnie) = Rx · Ry · Rz, jak w Roblox."""
    rx, ry, rz = [math.radians(a) for a in (o or [0, 0, 0])]
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    Rx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    Ry = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    Rz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]

    def mn(A, B):
        return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return mn(mn(Rx, Ry), Rz)


def rozmiar_osiowy(c):
    """Rozmiar pudła osiowego części po obrocie (walec: oś wzdłuż lokalnego X, jak w Roblox)."""
    s = c["s"]
    if not c.get("o"):
        return s
    R = macierz(c["o"])
    return [round(sum(abs(R[i][j]) * s[j] for j in range(3)), 6) for i in range(3)]


if __name__ == "__main__":
    for strumien in (sys.stdout,):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    _, D = DANE.wczytaj()
    cz = czesci(D)
    mn, mx = obrys(D)
    print("części: %d, obrys %s – %s" % (len(cz), [round(x, 1) for x in mn], [round(x, 1) for x in mx]))
