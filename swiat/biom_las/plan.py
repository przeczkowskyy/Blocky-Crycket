# -*- coding: utf-8 -*-
"""Plan biomu Las z góry (dla ludzi) — rysuje swiat/biom_las/podglad/plan.png z uklad.json i potwory.json.

    python -B swiat/biom_las/plan.py [--wyj swiat/biom_las/podglad/plan.png] [--szer 1600]

Kolorowe podbiomy, woda, ścieżki z czasem biegu, lokacje z numerami i legendą, strefy potworów (litera, liczba,
poziomy), trasa trolla, strażnik, piny teleportu, strefy spokoju, wejście z miasteczka, skala w studach
i ludzik z czasem biegu. Wymaga Pillow.
"""
import argparse
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import geo  # noqa: E402

GLOWNE = {"brama_pniakow": "Brama Pniaków", "oczko_galaretek": "Oczko Galaretek", "stary_uklon": "Stary Ukłon",
          "wielki_kapelusz": "Wielki Kapelusz", "wilcza_skala": "Wilcza Skała", "trollowa_tama": "Trollowa Tama",
          "kamienny_krag": "Kamienny Krąg", "szumiacy_prog": "Szumiący Próg"}
KOLOR_POZIOMU = {12: (214, 190, 150), 22: (196, 200, 178), 32: (170, 176, 196), 9.5: (70, 155, 220)}
BIEG = 16.0
K = 2  # rysujemy w podwójnej rozdzielczości i zmniejszamy (gładkie krawędzie)

POTWOR = {  # litera, kolor
    "Leśny Slime": ("S", (46, 170, 60)),
    "Muchomornik": ("M", (214, 52, 42)),
    "Cierniowy Wilk": ("W", (104, 72, 160)),
    "Leśny Troll": ("T", (130, 82, 40)),
    "Strażnik Gaju": ("G", (20, 140, 125)),
}
TUSZ = (29, 25, 22)
WODA = (70, 155, 220)
WODA_BRZEG = (23, 88, 154)


def czcionka(rozmiar, gruba=False):
    kandydaci = (["segoeuib.ttf", "arialbd.ttf"] if gruba else ["segoeui.ttf", "arial.ttf"])
    for n in kandydaci:
        for d in (r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu", "/Library/Fonts"):
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, rozmiar * K)
    for n in (["DejaVuSans-Bold.ttf"] if gruba else ["DejaVuSans.ttf"]):
        try:
            return ImageFont.truetype(n, rozmiar * K)
        except OSError:
            pass
    return ImageFont.load_default()


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def poziomy(pp):
    return str(pp[0]) if pp[0] == pp[1] else "%d–%d" % (pp[0], pp[1])


def dlugosc(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def punkt_w_polowie(pts):
    cel = dlugosc(pts) / 2
    for i in range(len(pts) - 1):
        d = math.dist(pts[i], pts[i + 1])
        if cel <= d:
            t = cel / d
            return (pts[i][0] + t * (pts[i + 1][0] - pts[i][0]), pts[i][1] + t * (pts[i + 1][1] - pts[i][1]))
        cel -= d
    return pts[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wyj", default=os.path.join(TU, "podglad", "plan.png"))
    ap.add_argument("--szer", type=int, default=1600)
    ap.add_argument("--telefon", action="store_true", help="sama mapa (bez legendy), duże napisy — do oglądania na telefonie")
    a = ap.parse_args()
    if a.telefon and a.wyj == os.path.join(TU, "podglad", "plan.png"):
        a.wyj = os.path.join(TU, "podglad", "plan_telefon.png")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    with open(os.path.join(TU, "uklad.json"), encoding="utf-8") as f:
        U = json.load(f)
    with open(os.path.join(TU, "potwory.json"), encoding="utf-8") as f:
        P = json.load(f)

    W = a.szer * K
    ZAKRES = 545.0                       # pokazujemy −545…+545 w obu osiach
    GORA = 150 * K                       # pas tytułu
    MAPA = W
    sk = MAPA / (2 * ZAKRES)

    def p(x, z):
        return ((x + ZAKRES) * sk, GORA + (z + ZAKRES) * sk)

    def ps(pts):
        return [p(x, z) for x, z in pts]

    lok_pkt = [(l["x"], l["z"]) for l in U["lokacje"] if not l.get("wewnatrz")]

    def ikona_strefy(zst):
        c = zst["srodek"]
        bliskie = [q for q in lok_pkt if math.dist(q, c) < 40]
        if not bliskie:
            return tuple(c)
        q = min(bliskie, key=lambda q: math.dist(q, c))
        dx, dz = c[0] - q[0], c[1] - q[1]
        n = math.hypot(dx, dz) or 1.0
        if n < 1.0:
            dx, dz = 0.0, 1.0
        r = zst["r"] * 0.62
        return (q[0] + dx / n * max(r, 30), q[1] + dz / n * max(r, 30))

    def najlepszy_punkt(pts, zajete):
        calosc = dlugosc(pts)
        best = None
        for k in range(15, 86, 5):
            cel = calosc * k / 100.0
            for i in range(len(pts) - 1):
                dd = math.dist(pts[i], pts[i + 1])
                if cel <= dd:
                    t = cel / dd
                    q = (pts[i][0] + t * (pts[i + 1][0] - pts[i][0]), pts[i][1] + t * (pts[i + 1][1] - pts[i][1]))
                    break
                cel -= dd
            else:
                q = tuple(pts[-1])
            m = min(math.dist(q, z) for z in zajete) if zajete else 1e9
            if best is None or m > best[0]:
                best = (m, q)
        return best[1]

    # --- legenda: liczymy wysokość wcześniej
    f_tyt, f_pod = czcionka(46, True), czcionka(26)
    f_bio, f_bio2 = czcionka(34, True), czcionka(24, True)
    f_nr, f_lab = czcionka(19, True), czcionka(21, True)
    f_leg, f_leg_b, f_leg_h = czcionka(27), czcionka(27, True), czcionka(32, True)
    f_strefa = czcionka(19, True)

    lok = U["lokacje"]
    pod = {b["id"]: b for b in U["podbiomy"]}
    wiersz = 40 * K
    kolumna_lok = (len(lok) + len(pod) + 1) // 2 + 2
    LEG = int(120 * K + kolumna_lok * wiersz + 1400 * K)
    H = GORA + MAPA + LEG
    img = Image.new("RGB", (W, H), (250, 247, 238))
    d = ImageDraw.Draw(img, "RGBA")

    def linia(pts, kolor, szer, przerywana=None):
        pts = ps(pts)
        if przerywana:
            kres, przerwa = przerywana
            for i in range(len(pts) - 1):
                (x0, y0), (x1, y1) = pts[i], pts[i + 1]
                dl = math.hypot(x1 - x0, y1 - y0)
                t = 0.0
                while t < dl:
                    t1 = min(dl, t + kres)
                    d.line([(x0 + (x1 - x0) * t / dl, y0 + (y1 - y0) * t / dl),
                            (x0 + (x1 - x0) * t1 / dl, y0 + (y1 - y0) * t1 / dl)], fill=kolor, width=int(szer))
                    t = t1 + przerwa
        else:
            d.line(pts, fill=kolor, width=int(szer), joint="curve")
            r = szer / 2
            for x, y in pts:
                d.ellipse([x - r, y - r, x + r, y + r], fill=kolor)

    def kolo(x, z, r, fill=None, outline=None, width=1):
        cx, cy = p(x, z)
        rr = r * sk
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=fill, outline=outline, width=int(width))

    def kolo_przerywane(x, z, r, kolor, szer, n=40):
        cx, cy = p(x, z)
        rr = r * sk
        for k in range(0, n, 2):
            a0, a1 = 360 * k / n, 360 * (k + 1) / n
            d.arc([cx - rr, cy - rr, cx + rr, cy + rr], a0, a1, fill=kolor, width=int(szer))

    def tekst(xy, s, f, kolor=TUSZ, srodek=True, obrys=None):
        x, y = xy
        if srodek:
            b = d.textbbox((0, 0), s, font=f)
            x -= (b[2] - b[0]) / 2
            y -= (b[3] - b[1]) / 2 + b[1]
        if obrys:
            for dx in (-2 * K, 0, 2 * K):
                for dy in (-2 * K, 0, 2 * K):
                    if dx or dy:
                        d.text((x + dx, y + dy), s, font=f, fill=obrys)
        d.text((x, y), s, font=f, fill=kolor)

    # --- tło poza płytą i pas Muru Pni
    d.rectangle([0, GORA, W, GORA + MAPA], fill=(196, 222, 200))
    x0, y0 = p(-500, -500)
    x1, y1 = p(500, 500)
    d.rectangle([x0, y0, x1, y1], fill=(111, 167, 122))
    m0, n0 = p(-470, -470)
    m1, n1 = p(470, 470)
    d.rectangle([m0, n0, m1, n1], fill=(63, 127, 74))
    # kropki pni w Murze
    import random
    rnd = random.Random(3)
    for _ in range(900):
        x = rnd.uniform(-468, 468)
        z = rnd.uniform(-468, 468)
        if max(abs(x), abs(z)) > 432:
            kolo(x, z, rnd.uniform(4, 8), fill=(44, 98, 56))

    # --- podbiomy
    for b in U["podbiomy"]:
        d.polygon(ps(b["wielokat"]), fill=hexrgb(b["kolor_planu"]))
    # teren: poziomy (pryzmaty) — kolor wg wysokości, krawędź z ząbkami urwiska; kopce; rampy (kreskowane)
    T = geo.Teren(U)
    for e in T.poziomy:
        if e["id"] == "jezioro_dno":
            continue
        d.polygon(ps(e["wielokat"]), fill=KOLOR_POZIOMU.get(e["y"], (200, 200, 200)))
    for e in T.poziomy:
        if e["id"] == "jezioro_dno":
            continue
        w = e["wielokat"]
        for i in range(len(w)):
            p0, p1 = w[i], w[(i + 1) % len(w)]
            dl = math.dist(p0, p1)
            n = max(1, int(dl / 9))
            for k in range(n):
                t = (k + 0.5) / n
                x, z = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
                nx, nz = (p1[1] - p0[1]) / dl, -(p1[0] - p0[0]) / dl
                if geo.pole(w) < 0:
                    nx, nz = -nx, -nz
                if T.H(x + nx * 3, z + nz * 3) < e["y"] - 3 and not T.rampa_w(x + nx * 3, z + nz * 3, 3):
                    d.line([p(x, z), p(x + nx * 5, z + nz * 5)], fill=(110, 84, 60), width=2 * K)
            if T.H((p0[0] + p1[0]) / 2 + (p1[1] - p0[1]) / dl * 3 * (1 if geo.pole(w) > 0 else -1),
                   (p0[1] + p1[1]) / 2 - (p1[0] - p0[0]) / dl * 3 * (1 if geo.pole(w) > 0 else -1)) < e["y"] - 3:
                d.line([p(*p0), p(*p1)], fill=(110, 84, 60), width=3 * K)
    for e in T.kopce:
        kolo(e["srodek"][0], e["srodek"][1], e["r_stopy"], fill=(186, 214, 130) if e["id"] == "pagorek" else (226, 200, 140))
        kolo(e["srodek"][0], e["srodek"][1], e["r"], fill=(170, 205, 100) if e["id"] == "pagorek" else (236, 205, 150),
             outline=(150, 120, 80), width=2 * K)
    for e in T.rampy:
        (ax, az, _), (bx, bz, _) = e["od"], e["do"]
        dl = math.hypot(bx - ax, bz - az)
        nx, nz = -(bz - az) / dl * e["szer"] / 2, (bx - ax) / dl * e["szer"] / 2
        d.polygon([p(ax + nx, az + nz), p(bx + nx, bz + nz), p(bx - nx, bz - nz), p(ax - nx, az - nz)], fill=(230, 214, 180),
                  outline=TUSZ, width=2 * K)
        for k in range(1, int(dl / 5)):
            t = k * 5 / dl
            x, z = ax + (bx - ax) * t, az + (bz - az) * t
            d.line([p(x + nx, z + nz), p(x - nx, z - nz)], fill=(120, 100, 80), width=K)
    # --- woda
    for w in U["woda"]:
        if w["rodzaj"] == "struga":
            sz = sum(w["szer"]) / 2
            linia(w["pts"], WODA_BRZEG, sz * sk + 4 * K)
            linia(w["pts"], WODA, sz * sk)
    for w in U["woda"]:
        if "wielokat" in w:
            d.polygon(ps(w["wielokat"]), fill=WODA, outline=WODA_BRZEG, width=3 * K)
        elif w["rodzaj"] in ("staw", "jezioro"):
            kolo(w["srodek"][0], w["srodek"][1], w["r"], fill=WODA, outline=WODA_BRZEG, width=3 * K)

    # --- ścieżki
    style = {"glowna": ((243, 226, 184), 12), "polana": ((240, 214, 160), 10), "boczna": ((226, 192, 142), 8),
             "labirynt": ((214, 196, 160), 14)}
    for rodzaj in ("boczna", "labirynt", "polana", "glowna"):
        for s in U["sciezki"]:
            if s["rodzaj"] != rodzaj:
                continue
            kolor, sz = style[rodzaj]
            linia(s["pts"], (75, 58, 107) if rodzaj == "labirynt" else TUSZ, sz * sk + 5 * K)
            linia(s["pts"], kolor, sz * sk)
    for s in U["sciezki"]:
        if s["rodzaj"] == "sekretna":
            linia(s["pts"], (255, 255, 255), 5 * K, przerywana=(12 * K, 8 * K))
            linia(s["pts"], TUSZ, 2 * K, przerywana=(12 * K, 8 * K))
    # przeprawy
    for pr in U["przeprawy"]:
        cx, cy = p(pr["x"], pr["z"])
        r = 7 * K
        d.rectangle([cx - r, cy - r, cx + r, cy + r], fill=(139, 90, 46), outline=TUSZ, width=2 * K)

    # --- strefy spokoju
    serce = pod["serce"]["wielokat"]
    pts = ps(serce + [serce[0]])
    for i in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        dl = math.hypot(bx - ax, by - ay)
        t = 0
        while t < dl:
            t1 = min(dl, t + 14 * K)
            d.line([(ax + (bx - ax) * t / dl, ay + (by - ay) * t / dl),
                    (ax + (bx - ax) * t1 / dl, ay + (by - ay) * t1 / dl)], fill=(40, 110, 200), width=4 * K)
            t = t1 + 9 * K
    for s in U["strefy_spokoju"]:
        if "srodek" in s and not s["id"].startswith("pin_"):
            kolo(s["srodek"][0], s["srodek"][1], s["r"], fill=(80, 150, 230, 40))
            kolo_przerywane(s["srodek"][0], s["srodek"][1], s["r"], (40, 110, 200), 3 * K)

    # --- trasa trolla
    lit, kol = POTWOR["Leśny Troll"]
    linia(P["troll"]["trasa"], kol + (255,), 4 * K, przerywana=(6 * K, 7 * K))

    for pat in P.get("patrole", []):
        lit, kol = POTWOR[pat["potwor"]]
        linia(pat["trasa"], kol + (255,), 5 * K, przerywana=(10 * K, 6 * K))
    # --- strefy potworów
    for zst in P["strefy"]:
        lit, kol = POTWOR[zst["potwor"]]
        x, z = zst["srodek"]
        kolo(x, z, zst["r"], fill=kol + (55,))
        kolo_przerywane(x, z, zst["r"], kol, 3 * K)
        for t in zst["trasa"]:
            kolo(t[0], t[1], 2.2, fill=kol)

    # --- lokacje
    numery = []
    for l in lok:
        if l.get("wewnatrz"):
            continue
        numery.append(l)

    # --- napisy podbiomów (kotwice ręczne — w miejscach bez lokacji)
    kotwice = {"laka": (262, 212), "kapeluszowo": (-345, 380), "serce": (-48, 112),
               "ostepy": (-335, 62), "wawoz": (392, -30), "korona": (-90, -335)}
    for k, (x, z) in kotwice.items():
        b = pod[k]
        cx, cy = p(x, z)
        poz = "strefa spokoju" if not b["poziomy"] else "poziomy %d–%d" % tuple(b["poziomy"])
        tekst((cx, cy), b["nazwa"].upper(), f_bio, obrys=(255, 255, 255))
        tekst((cx, cy + 34 * K), poz, f_bio2, kolor=(70, 60, 50), obrys=(255, 255, 255))

    # strefy: znaczek z literą, liczbą i poziomami (odsunięty od numerów lokacji)
    for zst in P["strefy"]:
        lit, kol = POTWOR[zst["potwor"]]
        cx, cy = p(*ikona_strefy(zst))
        r = 15 * K
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=kol, outline=(255, 255, 255), width=2 * K)
        tekst((cx, cy), lit, f_strefa, kolor=(255, 255, 255))
        ix, iz = ikona_strefy(zst)
        najbl = min(lok_pkt, key=lambda q: math.dist(q, (ix, iz)))
        w_gore = math.dist(najbl, (ix, iz)) < 60 and najbl[1] > iz  # numer lokacji pod znaczkiem → napis nad nim
        tekst((cx, cy + (-27 if w_gore else 27) * K), "×%d · %s" % (zst["naraz"], poziomy(zst["poziomy"])), f_strefa,
              kolor=TUSZ, obrys=(255, 255, 255))
    # troll i strażnik
    tr = P["troll"]
    cx, cy = p(*tr["dom"])
    r = 17 * K
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=POTWOR["Leśny Troll"][1], outline=(255, 255, 255), width=2 * K)
    tekst((cx, cy), "T", f_strefa, kolor=(255, 255, 255))
    tekst((cx + 22 * K, cy - 12 * K), "troll %d–%d" % tuple(tr["poziomy"]), f_strefa, srodek=False,
          obrys=(255, 255, 255))
    st = P["straznik"]
    cx, cy = p(st["miejsce"][0] - 38, st["miejsce"][1] - 6)
    gw = []
    for k in range(10):
        rr = (26 if k % 2 == 0 else 11) * K
        aa = math.radians(-90 + 36 * k)
        gw.append((cx + rr * math.cos(aa), cy + rr * math.sin(aa)))
    d.polygon(gw, fill=POTWOR["Strażnik Gaju"][1], outline=(255, 255, 255))
    tekst((cx, cy + 2 * K), "G", f_strefa, kolor=(255, 255, 255))
    tekst((cx - 70 * K, cy + 4 * K), "Strażnik %d" % st["poziom"], f_strefa, obrys=(255, 255, 255))

    # piny teleportu
    for pin in U["piny"]:
        cx, cy = p(*pin["punkt"])
        cy -= 26 * K
        r = 10 * K
        d.polygon([(cx - r * 0.85, cy + r * 0.5), (cx + r * 0.85, cy + r * 0.5), (cx, cy + r * 2.3)],
                  fill=(220, 40, 60), outline=TUSZ)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(220, 40, 60), outline=TUSZ, width=2 * K)
        d.ellipse([cx - r * 0.4, cy - r * 0.4, cx + r * 0.4, cy + r * 0.4], fill=(255, 255, 255))

    for l in numery:
        cx, cy = p(l["x"], l["z"])
        r = 16 * K
        if l["orientacyjny"]:
            d.ellipse([cx - r - 5 * K, cy - r - 5 * K, cx + r + 5 * K, cy + r + 5 * K], fill=(242, 176, 48))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=TUSZ, width=3 * K)
        tekst((cx, cy), str(l["nr"]), f_nr)
    # Bocianie Gniazdo — mały numer przy Ukłonie
    for l in lok:
        if l.get("wewnatrz"):
            cx, cy = p(l["x"], l["z"])
            cx += 30 * K
            cy -= 26 * K
            r = 12 * K
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=TUSZ, width=2 * K)
            tekst((cx, cy), str(l["nr"]), czcionka(15, True))

    # nazwy ośmiu najważniejszych miejsc z czasem biegu od bramy (po ścieżkach, 16 st/s)
    _, _, czas = geo.czasy_od_wejscia(U)
    przes = {"brama_pniakow": (95, 18), "oczko_galaretek": (-130, -42), "stary_uklon": (-20, -105), "wielki_kapelusz": (0, 68),
             "wilcza_skala": (10, 40), "trollowa_tama": (-118, -40), "kamienny_krag": (0, -62), "szumiacy_prog": (52, 24)}
    for l in lok:
        if l["id"] not in GLOWNE:
            continue
        t = czas(l)
        napis = GLOWNE[l["id"]] + ("" if l["id"] == "brama_pniakow" else " · od bramy %.0f s" % t)
        dx, dz = przes[l["id"]]
        cx, cy = p(l["x"] + dx, l["z"] + dz)
        b_ = d.textbbox((0, 0), napis, font=f_lab)
        wdt, hgt = b_[2] - b_[0] + 14 * K, b_[3] - b_[1] + 12 * K
        d.rounded_rectangle([cx - wdt / 2, cy - hgt / 2, cx + wdt / 2, cy + hgt / 2], radius=8 * K, fill=(255, 255, 255, 235),
                            outline=TUSZ, width=2 * K)
        tekst((cx, cy), napis, f_lab)

    # wejście z miasteczka
    bx, by = p(200, 418)
    ex, ey = p(200, 535)
    d.line([(ex, ey), (bx, by + 30 * K)], fill=(220, 40, 60), width=8 * K)
    d.polygon([(bx - 18 * K, by + 34 * K), (bx + 18 * K, by + 34 * K), (bx, by + 8 * K)], fill=(220, 40, 60))
    tekst((ex + 40 * K, ey - 22 * K), "przejście z Bramy Miejskiej (E, zaciemnienie)", f_lab, kolor=(180, 20, 40), obrys=(255, 255, 255))

    # róża kierunku i skala
    rx, ry = W - 70 * K, GORA + 80 * K
    d.polygon([(rx, ry - 40 * K), (rx - 16 * K, ry + 10 * K), (rx, ry), (rx + 16 * K, ry + 10 * K)], fill=TUSZ)
    tekst((rx, ry + 30 * K), "N", f_leg_b)
    sx, sy = 40 * K, GORA + MAPA - 70 * K
    dl100 = 100 * sk
    d.rectangle([sx - 10 * K, sy - 50 * K, sx + 3 * dl100 + 330 * K, sy + 40 * K], fill=(255, 255, 255, 225),
                outline=TUSZ, width=2 * K)
    for k in range(3):
        d.rectangle([sx + k * dl100, sy - 6 * K, sx + (k + 1) * dl100, sy + 6 * K],
                    fill=TUSZ if k % 2 == 0 else (255, 255, 255), outline=TUSZ, width=2 * K)
        tekst((sx + (k + 1) * dl100, sy - 25 * K), "%d" % ((k + 1) * 100), f_lab)
    tekst((sx, sy - 25 * K), "0", f_lab)
    tekst((sx + 3 * dl100 + 40 * K, sy - 32 * K), "studów", f_lab, srodek=False)
    tekst((sx + 3 * dl100 + 40 * K, sy - 4 * K), "100 st = 6 s biegu", f_lab, srodek=False)
    # ludzik
    lx, ly = sx + 3 * dl100 + 295 * K, sy - 6 * K
    d.ellipse([lx - 6 * K, ly - 34 * K, lx + 6 * K, ly - 22 * K], fill=TUSZ)
    d.line([(lx, ly - 22 * K), (lx - 3 * K, ly)], fill=TUSZ, width=4 * K)
    d.line([(lx - 3 * K, ly), (lx - 14 * K, ly + 16 * K)], fill=TUSZ, width=4 * K)
    d.line([(lx - 3 * K, ly), (lx + 10 * K, ly + 14 * K)], fill=TUSZ, width=4 * K)
    d.line([(lx - 1 * K, ly - 17 * K), (lx + 14 * K, ly - 9 * K)], fill=TUSZ, width=4 * K)
    d.line([(lx - 1 * K, ly - 17 * K), (lx - 14 * K, ly - 24 * K)], fill=TUSZ, width=4 * K)
    for k in range(3):
        d.line([(lx - (30 + 8 * k) * K, ly - (20 - 9 * k) * K), (lx - (18 + 8 * k) * K, ly - (20 - 9 * k) * K)],
               fill=TUSZ, width=2 * K)

    # --- tytuł
    tekst((30 * K, 22 * K), "Biom Las — Bór Pod Ukłonem · plan z góry", f_tyt, srodek=False)
    L_ = {l["id"]: l for l in lok}
    if a.telefon:
        pod = "v2 · 1000 × 1000 st · bieg 16 st/s · Ukłon %.0f s, Krąg %.0f s od bramy" % (czas(L_["stary_uklon"]), czas(L_["kamienny_krag"]))
    else:
        pod = ("propozycja v2 15.11.2026 · 1000 × 1000 studów, gra w 860 × 860 · gracz biegnie 16 st/s · "
               "od bramy do Ukłonu %.0f s, do Kręgu %.0f s" % (czas(L_["stary_uklon"]), czas(L_["kamienny_krag"])))
    tekst((30 * K, 92 * K), pod, f_pod, kolor=(80, 70, 60), srodek=False)

    # --- legenda
    y = GORA + MAPA + 40 * K
    tekst((30 * K, y), "Lokacje (numer na mapie)", f_leg_h, srodek=False)
    tekst((W / 2 + 10 * K, y), "Znaki", f_leg_h, srodek=False)
    y0 = y + 60 * K
    # kolumny lokacji pogrupowane po podbiomach
    kol_x = [30 * K, W / 2 + 10 * K]
    wiersze = []
    for b in U["podbiomy"]:
        wiersze.append(("h", b))
        for l in lok:
            if l["podbiom"] == b["id"]:
                wiersze.append(("l", l))
    # lewa kolumna: cztery pierwsze podbiomy; prawa: znaki i dwa ostatnie podbiomy
    podz = [i for i, (t, v) in enumerate(wiersze) if t == "h"][4]
    lewa = wiersze[:podz]
    prawa = wiersze[podz:]

    def rysuj_wiersze(lista, x, y):
        for typ, v in lista:
            if typ == "h":
                d.rounded_rectangle([x, y + 4 * K, x + 30 * K, y + 32 * K], radius=6 * K,
                                    fill=hexrgb(v["kolor_planu"]), outline=TUSZ, width=2 * K)
                poz = "spokój" if not v["poziomy"] else "poz. %d–%d" % tuple(v["poziomy"])
                tekst((x + 42 * K, y), "%s — %s" % (v["nazwa"], poz), f_leg_b, srodek=False)
            else:
                dop = []
                if v["pin"]:
                    dop.append("pin")
                if v["orientacyjny"]:
                    dop.append("widać z daleka")
                s = "%2d  %s%s" % (v["nr"], v["nazwa"], (" (" + ", ".join(dop) + ")") if dop else "")
                tekst((x + 10 * K, y), s, f_leg, srodek=False)
            y += wiersz
        return y

    y_lewa = rysuj_wiersze(lewa, kol_x[0], y0)

    # znaki (prawa kolumna, u góry)
    x = kol_x[1]
    yy = y0

    def znak_linii(kolor, sz, obrys=TUSZ, przer=False):
        if przer:
            for k in range(4):
                d.line([(x + k * 18 * K, yy + 20 * K), (x + k * 18 * K + 10 * K, yy + 20 * K)], fill=kolor,
                       width=sz * K)
        else:
            d.line([(x, yy + 20 * K), (x + 64 * K, yy + 20 * K)], fill=obrys, width=(sz + 4) * K)
            d.line([(x, yy + 20 * K), (x + 64 * K, yy + 20 * K)], fill=kolor, width=sz * K)

    pozycje = [
        (lambda: znak_linii(style["glowna"][0], 14), "szlak główny 12 st"),
        (lambda: znak_linii(style["boczna"][0], 9), "dróżka 8 st"),
        (lambda: znak_linii(TUSZ, 3, przer=True), "sekretna Grań i tunel"),
        (lambda: znak_linii(WODA, 12, obrys=WODA_BRZEG), "Kręta Struga, stawy, jezioro"),
        (lambda: d.rectangle([x + 24 * K, yy + 12 * K, x + 40 * K, yy + 28 * K], fill=(139, 90, 46),
                             outline=TUSZ, width=2 * K), "przeprawa (most, kładka, bród)"),
        (lambda: d.line([(x, yy + 20 * K), (x + 64 * K, yy + 20 * K)], fill=(110, 84, 60), width=6 * K),
         "urwisko ≥ 10 (bariera); półki 12, tarasy 22, płaskowyż 32"),
        (lambda: d.rectangle([x + 8 * K, yy + 10 * K, x + 56 * K, yy + 30 * K], fill=(230, 214, 180), outline=TUSZ, width=2 * K),
         "rampa (jedyne wejście na wyższy poziom)"),
        (lambda: d.rectangle([x, yy + 8 * K, x + 64 * K, yy + 32 * K], fill=(80, 150, 230, 60),
                             outline=(40, 110, 200), width=3 * K), "strefa spokoju (bez potworów)"),
        (lambda: (d.ellipse([x + 16 * K, yy + 2 * K, x + 48 * K, yy + 34 * K], fill=POTWOR["Leśny Slime"][1]),
                  tekst((x + 32 * K, yy + 18 * K), "S", f_strefa, kolor=(255, 255, 255))),
         "Leśny Slime  (×liczba naraz · poziomy)"),
        (lambda: (d.ellipse([x + 16 * K, yy + 2 * K, x + 48 * K, yy + 34 * K], fill=POTWOR["Muchomornik"][1]),
                  tekst((x + 32 * K, yy + 18 * K), "M", f_strefa, kolor=(255, 255, 255))), "Muchomornik"),
        (lambda: (d.ellipse([x + 16 * K, yy + 2 * K, x + 48 * K, yy + 34 * K], fill=POTWOR["Cierniowy Wilk"][1]),
                  tekst((x + 32 * K, yy + 18 * K), "W", f_strefa, kolor=(255, 255, 255))), "Cierniowy Wilk"),
        (lambda: d.line([(x, yy + 20 * K), (x + 64 * K, yy + 20 * K)], fill=POTWOR["Cierniowy Wilk"][1], width=5 * K),
         "patrol wędrowny po ścieżce"),
        (lambda: (d.line([(x, yy + 20 * K), (x + 64 * K, yy + 20 * K)], fill=POTWOR["Leśny Troll"][1],
                         width=4 * K), tekst((x + 32 * K, yy + 18 * K), "T", f_strefa, kolor=TUSZ,
                                             obrys=(255, 255, 255))),
         "Leśny Troll (rzadki) i jego trasa"),
        (lambda: (d.ellipse([x + 16 * K, yy + 2 * K, x + 48 * K, yy + 34 * K], fill=POTWOR["Strażnik Gaju"][1]),
                  tekst((x + 32 * K, yy + 18 * K), "G", f_strefa, kolor=(255, 255, 255))),
         "Strażnik Gaju (strażnik biomu)"),
        (lambda: (d.ellipse([x + 22 * K, yy + 6 * K, x + 42 * K, yy + 26 * K], fill=(220, 40, 60), outline=TUSZ),
                  d.polygon([(x + 24 * K, yy + 20 * K), (x + 40 * K, yy + 20 * K), (x + 32 * K, yy + 36 * K)],
                            fill=(220, 40, 60))), "pin mapy teleportacji"),
        (lambda: (d.ellipse([x + 13 * K, yy, x + 51 * K, yy + 38 * K], fill=(242, 176, 48)),
                  d.ellipse([x + 18 * K, yy + 5 * K, x + 46 * K, yy + 33 * K], fill=(255, 255, 255), outline=TUSZ,
                            width=2 * K)), "punkt orientacyjny (widać z daleka)"),
    ]
    for rys, opis in pozycje:
        rys()
        tekst((x + 80 * K, yy), opis, f_leg, srodek=False)
        yy += wiersz
    yy += 20 * K
    y_prawa = rysuj_wiersze(prawa, x, yy)

    # podsumowanie liczb
    y = max(y_lewa, y_prawa) + 30 * K
    suma = sum(z["naraz"] for z in P["strefy"])
    suma_max = sum(z["max"] for z in P["strefy"])
    b = U["budzet"]
    try:
        with open(os.path.join(TU, "czesci.json"), encoding="utf-8") as f_:
            razem = len(json.load(f_)["czesci"])
    except OSError:
        razem = sum(b["wspolne"].values()) + sum(v for k, v in b.items() if k not in ("limit", "wspolne", "opis"))
    linie = [
        "Potwory naraz (ok. 8 graczy): %d zwykłych w strefach (do %d przy tłoku) + %d patrole + troll + strażnik."
        % (suma, suma_max, len(P.get("patrole", []))),
        "Walkę zawsze zaczyna gracz: podchodzi, E, walka. Potwory chodzą po swoim terenie i wracają do domu.",
        "Zbudowane: %d części z %d (rezerwa %d) — czesci.json z generuj.py. Teren z klocków, bez Terrain i bez siatek."
        % (razem, b["limit"], b["limit"] - razem),
        "Plan w układzie lasu (północ lasu u góry). W Studio las stoi osobno, obrócony o 180°.",
    ]
    for s in linie:
        tekst((30 * K, y), s, f_leg, srodek=False)
        y += wiersz
    H2 = int(y + 30 * K)
    if a.telefon:                                     # sama mapa (bez legendy) — na ekran telefonu
        img = img.crop((0, 0, W, GORA + MAPA)).resize((a.szer, (GORA + MAPA) // K), Image.LANCZOS)
    else:
        img = img.crop((0, 0, W, H2)).resize((a.szer, H2 // K), Image.LANCZOS)
    os.makedirs(os.path.dirname(a.wyj), exist_ok=True)
    img.save(a.wyj, optimize=True)
    print("PLAN", a.wyj, img.size, "%.0f kB" % (os.path.getsize(a.wyj) / 1024))


if __name__ == "__main__":
    main()
