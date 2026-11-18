# -*- coding: utf-8 -*-
"""Paski klatek cyklu biegu bez Studio: rzut brył bohatera (strój odniesienia) z boku i z przodu, osiem klatek cyklu
przy zwykłej prędkości postaci, dawny cykl („było”) nad nowym („jest”). Wynik: podglady/bieg_<klasa>.png.

    python -B swiat/bohater_swiat/podglad_biegu.py

To schemat z brył (prostokąty w rzucie równoległym, bez światła i tekstur) — do oceny pozy przed próbą w Studio.
„Było” to cykl sprzed zmiany (wzór i liczby zapisane niżej), „jest” liczy dane.poza_biegu, czyli to samo, co klient.
"""
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import dane as DN  # noqa: E402
import logika_bohatera as LB  # noqa: E402

KLATKI = 8
PX = 30.0                       # pikseli na stud
KAFEL = (250, 250)              # szerokość i wysokość jednej klatki
STARE = {"krok": 1.0, "biodra": 0.82, "podskok": 0.05, "unoszenie": 0.32, "podpor": 0.32, "kadencja": 2.5, "noga_wz": 1.55,
         "stopa": {"mag": -8.0}, "rece": {"wojownik": (30, 10), "mag": (26, 8)}, "lokcie": {"wojownik": (18, 0)}, "pochyl": -9.0}


def stara_poza(rig, d, K, klucz, faza, v):
    """Cykl biegu sprzed zmiany: (pozy kości, CFrame brył)."""
    from geometria import cf, orientacja, razy
    B = K["bieg"]
    noga = B["noga"]
    krok = STARE["krok"] * noga
    f = max(1.2, min(STARE["kadencja"] * math.sqrt(STARE["noga_wz"] / noga), v * STARE["podpor"] / krok))
    pod = max(0.1, min(STARE["podpor"], krok * f / v))
    S = dict(B, krok=krok)

    def tor(fz):
        if fz < pod:
            return krok / 2 - krok * (fz / pod), B["kostka"], 0.0
        u = (fz - pod) / (1 - pod)
        s = math.sin(math.pi * u)
        return (-(krok / 2) * math.cos(math.pi * u), B["kostka"] + STARE["unoszenie"] * noga * s,
                math.radians(STARE["stopa"].get(klucz, -22.0)) * s)

    biodra = B["kostka"] + STARE["biodra"] * noga - STARE["podskok"] * noga * math.cos(4 * math.pi * (faza - pod / 2))
    t = dict(rig.transformy(K["klipy"]["spoczynek"], 0))
    t[rig.indeks["LowerTorso"]] = cf((0.0, biodra - B["biodro"], 0.0))
    for strona, przes in (("Left", 0.0), ("Right", 0.5)):
        przod, wys, stopa = tor((faza + przes) % 1.0)
        udo, lydka = LB._noga_ik(S, przod, wys - biodra)
        for kosc, kat in (("UpperLeg", udo), ("LowerLeg", lydka), ("Foot", stopa - udo - lydka)):
            t[rig.indeks[strona + kosc]] = cf((0.0, 0.0, 0.0), orientacja(kat, 0.0, 0.0))
    c = math.cos(2 * math.pi * faza)
    rece = STARE["rece"].get(klucz, (28, 28))
    lokcie = STARE["lokcie"].get(klucz, (0, 0))
    for kosc, kat in (("LeftUpperArm", -rece[0] * c), ("RightUpperArm", rece[1] * c), ("LeftLowerArm", lokcie[0]),
                      ("RightLowerArm", lokcie[1])):
        i = rig.indeks[kosc]
        t[i] = razy(t.get(i, cf()), cf((0.0, 0.0, 0.0), orientacja(math.radians(kat), 0.0, 0.0)))
    t[rig.indeks["UpperTorso"]] = cf((0.0, 0.0, 0.0), orientacja(math.radians(STARE["pochyl"]), 0.0, 0.0))   # poza „pochyl”
    pozy = rig.pozy(t)
    return pozy, [rig.czesc_cf(cz, pozy) for cz in d["czesci"]]


def _otoczka(p):
    p = sorted(set(p))
    if len(p) < 3:
        return p

    def pol(lista):
        w = []
        for q in lista:
            while len(w) >= 2 and (w[-1][0] - w[-2][0]) * (q[1] - w[-2][1]) - (w[-1][1] - w[-2][1]) * (q[0] - w[-2][0]) <= 0:
                w.pop()
            w.append(q)
        return w
    dol, gora = pol(p), pol(reversed(p))
    return dol[:-1] + gora[:-1]


def rysuj(obraz, x0, y0, d, cfs, widok):
    """Rzut brył w kaflu o lewym górnym rogu (x0, y0): widok „bok” (przód postaci w prawo) albo „przod”."""
    from PIL import ImageDraw
    from geometria import narozniki
    r = ImageDraw.Draw(obraz)
    ziemia = y0 + KAFEL[1] - 22
    sx = x0 + KAFEL[0] / 2
    r.line([(x0 + 4, ziemia), (x0 + KAFEL[0] - 4, ziemia)], fill=(120, 120, 120), width=1)
    bryly = []
    for cz, c in zip(d["czesci"], cfs):
        if len(cz) > 12 and isinstance(cz[12], str) and len(cz[12]) == 6:
            kolor = tuple(int(cz[12][i:i + 2], 16) for i in (0, 2, 4))
        else:
            kolor = (170, 170, 170)
        pts = narozniki(c, cz[9:12])
        if widok == "bok":       # patrzymy z prawej strony postaci: przód (−Z) w prawo, bliżej = większe X
            rzut = [(sx - p[2] * PX, ziemia - p[1] * PX) for p in pts]
            glebia = sum(p[0] for p in pts)
        else:                    # patrzymy z przodu: prawa ręka postaci po lewej, bliżej = mniejsze Z
            rzut = [(sx - p[0] * PX, ziemia - p[1] * PX) for p in pts]
            glebia = -sum(p[2] for p in pts)
        bryly.append((glebia, rzut, kolor))
    for _, rzut, kolor in sorted(bryly, key=lambda b: b[0]):
        o = _otoczka([(round(a, 1), round(b, 1)) for a, b in rzut])
        if len(o) >= 3:
            r.polygon(o, fill=kolor, outline=tuple(int(k * 0.55) for k in kolor))


def pasek(klucz, folder):
    from PIL import Image, ImageDraw, ImageFont
    import aktorzy as A
    from geometria import Rig
    D = DN.zbierz()
    K = D["klasy"][klucz]
    d = A.wczytaj(klucz)
    rig = Rig(d)
    v = D["ruch"]["bieg_predkosc"]
    wiersze = [("było — z boku", "stare", "bok"), ("jest — z boku", "nowe", "bok"),
               ("było — z przodu", "stare", "przod"), ("jest — z przodu", "nowe", "przod")]
    margines = 26
    obraz = Image.new("RGB", (KLATKI * KAFEL[0], len(wiersze) * (KAFEL[1] + margines) + 30), (238, 240, 244))
    r = ImageDraw.Draw(obraz)
    f, pod = LB.kadencja(K["bieg"], v)
    czcionka = None
    for nazwa in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            czcionka = ImageFont.truetype(nazwa, 13)
            break
        except OSError:
            pass
    r.text((8, 6), "%s — cykl biegu przy %g st/s, klatki co 1/8 cyklu (faza 0 = lewa stopa staje z przodu); jest: kadencja %.2f "
           "cyklu/s, podpór %.0f%% cyklu" % (K["nazwa"], v, f, 100 * pod), fill=(20, 20, 20), font=czcionka)
    for w, (napis, ktore, widok) in enumerate(wiersze):
        y0 = 30 + w * (KAFEL[1] + margines)
        r.text((8, y0), napis, fill=(20, 20, 20), font=czcionka)
        for n in range(KLATKI):
            faza = n / float(KLATKI)
            if ktore == "stare":
                cfs = stara_poza(rig, d, K, klucz, faza, v)[1]
            else:
                cfs = DN.poza_biegu(rig, d, K, faza, v)[2]
            rysuj(obraz, n * KAFEL[0], y0 + margines - 8, d, cfs, widok)
            r.text((n * KAFEL[0] + 8, y0 + 14), "%d/8" % n, fill=(90, 90, 90))
    os.makedirs(folder, exist_ok=True)
    sciezka = os.path.join(folder, "bieg_%s.png" % klucz)
    obraz.save(sciezka, optimize=True)
    return sciezka


def main():
    for klucz in ("wojownik", "zwiadowca", "mag"):
        print("zapisano", os.path.relpath(pasek(klucz, os.path.join(TU, "podglady")), DN.REPO))


if __name__ == "__main__":
    main()
