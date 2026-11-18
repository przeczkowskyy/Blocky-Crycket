#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Podglądy tras cutscenki z góry i z boku (Pillow, bez Blendera i bez Studio).

    python -B swiat/cutscenka_biomu/podglad.py            # podglady/trasa_<biom>.jpg dla wszystkich biomów
    python -B swiat/cutscenka_biomu/podglad.py las        # tylko wybrany biom

Na obrazie: u góry mapa z góry (bryły mapy w swoich kolorach, niższe pod wyższymi) z trasą kamery — kolor linii to
prędkość (czerwony wolno, żółty szybko), kreski co 0,5 s pokazują, dokąd kamera patrzy, kółka z numerami to
przystanki; niżej przekrój z boku: sylwetka brył w korytarzu trasy (ciemna) i w całym pasie (jasna), wysokość
kamery i celu. Trasa na obrazie to ta sama krzywa, którą gra klient (dane.krzywa_probek).
"""
import math
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
if TU not in sys.path:
    sys.path.insert(0, TU)
import dane as DN  # noqa: E402

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

SKALA = 2.6          # pikseli na stud (poziomo)
SKALA_Y = 4.2        # pikseli na stud wysokości (przekrój)
MARGINES = 46
WYS_PRZEKROJU = 44   # studów wysokości na przekroju
TLO = (24, 22, 30)


def czcionka(rozmiar):
    for nazwa in ("arial.ttf", "DejaVuSans.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(nazwa, rozmiar)
        except OSError:
            pass
    return ImageFont.load_default()


def kolor_predkosci(v, vmax):
    f = max(0.0, min(1.0, v / vmax))
    return (255, int(70 + 170 * f), int(60 * (1 - f)))


def rysuj(b, U, sciezka):
    M = b["_mapa"]
    tr = b["trasa"]
    m = DN.miary_trasy(tr, M, U)
    pas = M.z["pas"]
    u1, u2 = pas["zakres_czesci_u"][0], pas["zakres_czesci_u"][1]
    v1, v2 = -48.0, 48.0
    szer = int((u2 - u1) * SKALA) + 2 * MARGINES
    wys_mapy = int((v2 - v1) * SKALA)
    wys_prz = int(WYS_PRZEKROJU * SKALA_Y)
    wys = MARGINES + wys_mapy + 34 + wys_prz + 96
    obraz = Image.new("RGB", (szer, wys), TLO)
    r = ImageDraw.Draw(obraz, "RGBA")
    f_m, f_s, f_d = czcionka(13), czcionka(11), czcionka(20)

    def xy(x, z):
        return (MARGINES + (x - M.X0 - u1) * SKALA, MARGINES + (z - M.Z0 - v1) * SKALA)

    y0 = MARGINES + wys_mapy + 34 + wys_prz

    def xh(x, y):
        return (MARGINES + (x - M.X0 - u1) * SKALA, y0 - y * SKALA_Y)

    # --- mapa z góry: bryły od najniższego wierzchu
    bryly = []
    prog = U["trasa"]["przezroczystosc_przeszkody_do"]
    for p in M.czesci:
        if float(p[13]) >= prog:
            continue
        R = DN._macierz(p[5], p[6], p[7])
        hx, hy, hz = p[8] / 2.0, p[9] / 2.0, p[10] / 2.0
        if R is None:
            ax, az, gora = (hx, 0.0), (0.0, hz), p[3] + hy
        else:
            ax, az = (R[0][0] * hx, R[2][0] * hx), (R[0][2] * hz, R[2][2] * hz)
            gora = p[3] + abs(R[1][0]) * hx + abs(R[1][1]) * hy + abs(R[1][2]) * hz
            # pochylona bryła: do rzutu dochodzi cień osi pionowej
            ax = (ax[0] + R[0][1] * hy * 0.0, ax[1])
        bryly.append((gora, p, ax, az))
    bryly.sort(key=lambda t: t[0])
    kolumny_kor = {}
    kolumny_pas = {}
    for gora, p, ax, az in bryly:
        cx, cz = p[2], p[4]
        rogi = [xy(cx + sx * ax[0] + sz * az[0], cz + sx * ax[1] + sz * az[1]) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        try:
            kolor = tuple(int(p[11][i:i + 2], 16) for i in (0, 2, 4))
        except (ValueError, IndexError):
            kolor = (120, 120, 120)
        r.polygon(rogi, fill=kolor + (255,))
        zasieg = abs(ax[0]) + abs(az[0])
        polz = abs(ax[1]) + abs(az[1])
        for k in range(int(math.floor(cx - zasieg)), int(math.ceil(cx + zasieg)) + 1):
            if abs(cz - M.Z0) - polz <= 32:
                kolumny_pas[k] = max(kolumny_pas.get(k, 0.0), gora)
            kolumny_kor.setdefault(k, []).append((cz - polz, cz + polz, gora))
    # bryły kulis wystają poza okno mapy — zasłaniamy wszystko nad i pod nim
    r.rectangle([0, 0, szer, MARGINES - 1], fill=TLO + (255,))
    r.rectangle([0, MARGINES + wys_mapy, szer, wys], fill=TLO + (255,))
    # granice pola gry
    for v in (-32, 32):
        r.line([xy(M.X0 + u1, M.Z0 + v), xy(M.X0 + u2, M.Z0 + v)], fill=(255, 255, 255, 70), width=1)

    # --- próbki trasy
    dt = 1 / 30.0
    ile = int(round(tr["czas"] / dt))
    P = [DN.krzywa_probek(tr["poz"], tr["n"], tr["krok"], i * dt) for i in range(ile + 1)]
    C = [DN.krzywa_probek(tr["patrz"], tr["n"], tr["krok"], i * dt) for i in range(ile + 1)]
    vmax = m["predkosc_maks"]
    # przekrój: sylwetki
    for k in sorted(kolumny_pas):
        x = float(k)
        a, bb = xh(x, kolumny_pas[k]), xh(x + 1, 0)
        r.rectangle([a[0], min(a[1], bb[1]), bb[0], bb[1]], fill=(92, 96, 110, 255))
    for i in range(ile):
        k = int(math.floor(P[i][0]))
        szczyt = 0.0
        for z1, z2, gora in kolumny_kor.get(k, []):
            if z1 - 6 <= P[i][2] <= z2 + 6:
                szczyt = max(szczyt, gora)
        a, bb = xh(float(k), szczyt), xh(float(k) + 1, 0)
        r.rectangle([a[0], min(a[1], bb[1]), bb[0], bb[1]], fill=(38, 40, 52, 255))
    r.line([xh(M.X0 + u1, 0), xh(M.X0 + u2, 0)], fill=(255, 255, 255, 120), width=1)
    for y in (10, 20, 30, 40):
        r.line([xh(M.X0 + u1, y), xh(M.X0 + u2, y)], fill=(255, 255, 255, 34), width=1)
        r.text((6, xh(0, y)[1] - 7), "%d st" % y, font=f_s, fill=(200, 200, 210, 255))
    # strażnik
    pd = tr["pudlo"]
    a, bb = xh(pd["x"] - pd["szer"] / 2, pd["y"] + pd["wys"]), xh(pd["x"] + pd["szer"] / 2, pd["y"])
    r.rectangle([a[0], a[1], bb[0], bb[1]], outline=(255, 90, 200, 255), width=2)
    sx, sy = xy(pd["x"], pd["z"])
    pr = pd["szer"] / 2 * SKALA
    r.ellipse([sx - pr, sy - pr, sx + pr, sy + pr], outline=(255, 90, 200, 255), width=3)
    r.text((sx - pr, sy + pr + 2), b["straznik"]["nazwa"], font=f_m, fill=(255, 150, 220, 255))
    # trasa
    for i in range(ile):
        v = math.dist(P[i + 1], P[i]) / dt
        k = kolor_predkosci(v, vmax)
        r.line([xy(P[i][0], P[i][2]), xy(P[i + 1][0], P[i + 1][2])], fill=k + (255,), width=3)
        r.line([xh(P[i][0], P[i][1]), xh(P[i + 1][0], P[i + 1][1])], fill=k + (255,), width=3)
        r.line([xh(C[i][0], C[i][1]), xh(C[i + 1][0], C[i + 1][1])], fill=(120, 200, 255, 150), width=1)
    for i in range(0, ile + 1, 15):
        d = [C[i][k] - P[i][k] for k in range(3)]
        dl = math.hypot(d[0], d[2]) or 1.0
        koniec = (P[i][0] + d[0] / dl * 9, P[i][2] + d[2] / dl * 9)
        r.line([xy(P[i][0], P[i][2]), xy(*koniec)], fill=(120, 200, 255, 230), width=1)
        r.ellipse([xy(P[i][0], P[i][2])[0] - 2, xy(P[i][0], P[i][2])[1] - 2, xy(P[i][0], P[i][2])[0] + 2,
                   xy(P[i][0], P[i][2])[1] + 2], fill=(255, 255, 255, 255))
    # przystanki
    for nr, p in enumerate(m["przystanki"], 1):
        i = min(int(round(p["t"] / dt)), ile)
        cx, cy = xy(P[i][0], P[i][2])
        r.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 255, 255, 255), outline=(20, 20, 20, 255), width=2)
        r.text((cx - 4, cy - 7), str(nr), font=f_m, fill=(20, 20, 20, 255))
        hx_, hy_ = xh(P[i][0], P[i][1])
        r.ellipse([hx_ - 5, hy_ - 5, hx_ + 5, hy_ + 5], fill=(255, 255, 255, 255), outline=(20, 20, 20, 255))
        r.text((cx - 30, MARGINES + wys_mapy + 4), "%d. %s" % (nr, p["nazwa"]), font=f_s, fill=(235, 235, 240, 255))
        r.text((cx - 30, MARGINES + wys_mapy + 17), "%.1f s · %.0f st/s" % (p["t"], p["predkosc"]), font=f_s,
               fill=(190, 190, 200, 255))
    # start i przybycie gracza
    uk = tr["uklad"]
    px, py = xy(M.X0 + uk["przybycie"][0], M.Z0 + uk["przybycie"][2])
    r.rectangle([px - 4, py - 4, px + 4, py + 4], fill=(80, 220, 255, 255), outline=(0, 0, 0, 255))
    r.text((px - 20, py + 7), "gracz", font=f_s, fill=(160, 235, 255, 255))
    ix, iy = xy(M.X0 + uk["inkubator"]["u"], M.Z0 + uk["inkubator"]["v"])
    r.ellipse([ix - 5, iy - 5, ix + 5, iy + 5], outline=(255, 255, 255, 255), width=2)
    r.text((ix + 8, iy - 6), "inkubator", font=f_s, fill=(255, 255, 255, 255))
    # opisy
    r.text((MARGINES, 12), "Cutscenka biomu: %s — trasa kamery z góry (D-077, propozycja)" % b["nazwa"], font=f_d,
           fill=(255, 255, 255, 255))
    dol = y0 + 12
    r.text((MARGINES, dol), "czas %.1f s (lot %.1f s + postój na strażniku %.1f s) · droga %.0f st · prędkość przelotowa %.0f st/s, "
           "największa %.0f st/s · przyspieszenie do %.0f st/s² · obrót do %.0f°/s"
           % (m["czas"], m["lot"], m["czas"] - m["lot"], m["dlugosc"], m["przelotowa"], m["predkosc_maks"],
              m["przyspieszenie_maks"], m["obrot_maks"]), font=f_m, fill=(235, 235, 240, 255))
    r.text((MARGINES, dol + 18), "najmniejszy odstęp od bryły mapy %.2f st (%s, t = %.2f s) · wysokość kamery %.1f–%.1f st · "
           "strażnik zajmuje %.0f%% wysokości kadru między pasami"
           % (m["odstep_min"], m["odstep_gdzie"][1], m["odstep_gdzie"][0], m["wysokosc_min"], m["wysokosc_maks"],
              m["kadry"]["16x9"]["udzial"] * 100), font=f_m, fill=(235, 235, 240, 255))
    r.text((MARGINES, dol + 36), "linia: czerwona = wolno, żółta = szybko; niebieskie kreski co 0,5 s = kierunek patrzenia; "
           "przekrój: ciemne = bryły w korytarzu trasy (±6 st), szare = cały pas gry; niebieska linia = wysokość celu kamery",
           font=f_s, fill=(190, 190, 200, 255))
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    obraz.save(sciezka, quality=88)
    return m


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    wybrane = [a for a in argv if not a.startswith("--")]
    D = DN.wszystko()
    for b in D["biomy"]:
        if wybrane and b["id"] not in wybrane:
            continue
        sciezka = os.path.join(TU, "podglady", "trasa_%s.jpg" % b["id"])
        rysuj(b, D["U"], sciezka)
        print("zapisano podglady/trasa_%s.jpg" % b["id"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
