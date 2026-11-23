# -*- coding: utf-8 -*-
"""Mapa v2 (runda 7, propozycja): rzeźba terenu z fazowanych klocków, bramy rozmiaru, kryjówki, rzeczy do rozbicia,
sekrety, prądy wznoszące i strefy zagrożenia według stadium. Pisze TYLKO do dane_nastepne/ (mapa_v2.json + rigi
nowych rekwizytów), podglad/27–31 i folderu wyników poza repozytorium. dane/ tylko czyta (rigi starych rekwizytów).

    python -B swiat/ewolucja/modele/generuj.py mapa2          # dane + szkic + rendery (Blender)
    python -B swiat/ewolucja/modele/generuj.py mapa2 szkic    # tylko dane i szybki szkic z góry (bez Blendera)

Układ GRY jak w mapa.py: środek łąki = (0, 0), DEEP WOODS w +Z, studs, obrót o wokół pionu w stopniach
(CFrame.Angles(0, rad(o), 0)): lokalne +Z części → świat (sin o, cos o). Na ekranie gry +Z jest u góry, a −X po prawej.
"""
import json
import math
import os
import random

from swiat.ewolucja.modele import mapa as m1
from swiat.ewolucja.modele import smok_model as sm
from swiat.ewolucja.modele import swiat_zestaw as sz
from swiat.ewolucja.modele import swiat_zestaw2 as sz2

LAKA_R, LAS, LAS_R = 150.0, (0.0, 240.0), 115.0
LEGOWISKA = m1.LEGOWISKA
KROK = 2.0                      # największy próg, na który smok wchodzi bez rampy (studs)
WYS = {"L0": 0.0, "L1": 6.0, "L2": 14.0, "szczyt": 26.0}
KALDERA, LAWA_R, WYSPA_R, KALDERA_R = (-318.0, -96.0), 44.0, 16.0, 66.0
JEZIORO, JEZIORO_R = (8.0, -214.0), 30.0
STAWEK = (-167.0, 121.0, 8.0)                   # jeziorko pod wodospadem (głębokie)
KAM = {"wys": 34.0, "na_r": 5.2, "nachylenie": 58.0, "fov": 50.0}
PROMIEN = [1.6, 2.2, 3.0, 4.0, 5.2, 6.8, 9.0, 15.0]

C = {   # kolory terenu
    "trawa": "5FB04C", "trawa_c": "4E9A40", "trawa_j": "7CC25A", "trawa_w": "79B04A", "wrzos": "9A7BC4",
    "skala": "8C8AA0", "skala_c": "544E6A", "skala_j": "B4B2C4", "mech": "6FB04A",
    "kanion": "C78F5E", "kanion_c": "6B3F33", "kanion_j": "E0AE7A", "piach": "D9B07A", "piach_c": "C49A6C",
    "bazalt": "3A3648", "bazalt_c": "26222F", "popiol": "4B4352", "lawa": "FF6A1F", "lawa_j": "FFB347",
    "woda": "3E8FD8", "woda_j": "6FB8F0", "brzeg": "D8C38E", "sciezka": "C7B285", "sciezka_c": "B49C6E",
    "las": "2B5C44", "ziemia": "7A5A3E",
}


def _deg(dx, dz):
    """o, przy którym lokalne +Z części patrzy w kierunku (dx, dz)."""
    return math.degrees(math.atan2(dx, dz))


def _obrot_ku(dx, dz):
    """o rekwizytu (przód = lokalne −Z rigu… jak w mapa.py), przy którym przód patrzy w kierunku (dx, dz)."""
    return math.degrees(math.atan2(-dx, -dz))


def _lok(x, z, cx, cz, o):
    """Punkt świata -> układ lokalny części (lx wzdłuż lokalnego X, lz wzdłuż lokalnego Z)."""
    a = math.radians(o)
    dx, dz = x - cx, z - cz
    return dx * math.cos(a) - dz * math.sin(a), dx * math.sin(a) + dz * math.cos(a)


# =========================================================================== teren: bryły z wysokościami
class Teren:
    def __init__(self):
        self.bryly = []
        self.strefa = "laka"

    def dodaj(self, id, k, x, y, z, sx, sy, sz_, o=0.0, kolor="5FB04C", mat="matowy", chodzi=True, **fl):
        b = {"id": id, "k": k, "p": [round(x, 2), round(y, 3), round(z, 2)], "s": [round(sx, 2), round(sy, 3), round(sz_, 2)],
             "o": round(o % 360.0, 2), "kolor": kolor, "mat": mat, "chodzi": bool(chodzi), "strefa": self.strefa}
        for k_, v in fl.items():
            if v or (k_ == "widoczny" and v is False):
                b[k_] = v
        self.bryly.append(b)
        return b

    def pudlo(self, id, x0, x1, z0, z1, y0, y1, **kw):
        return self.dodaj(id, "blok", (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, x1 - x0, y1 - y0, z1 - z0, **kw)

    def plaskowyz(self, id, x0, x1, z0, z1, h, y0=-1.0, skala="skala", opaska="skala_c", wierzch="trawa_w", o=0.0, chodzi=True,
                  opaska_y=0.55, **kw):
        """Klocek-urwisko: skała do h − 0,5, ciemna opaska na ~55% wysokości (dachówka), czapa trawy do h."""
        cx, cz, sx, sz_ = (x0 + x1) / 2, (z0 + z1) / 2, x1 - x0, z1 - z0
        self.dodaj(id, "blok", cx, (y0 + h - 0.5) / 2, cz, sx, h - 0.5 - y0, sz_, o, C[skala], chodzi=chodzi, **kw)
        if h - y0 >= 5:
            yo = y0 + (h - y0) * opaska_y
            self.dodaj(id + "_opaska", "blok", cx, yo, cz, sx + 0.8, 1.0, sz_ + 0.8, o, C[opaska], chodzi=False, ozdoba=True, **kw)
        self.dodaj(id + "_czapa", "blok", cx, h - 0.25, cz, sx - 0.6, 0.5, sz_ - 0.6, o, C[wierzch], chodzi=chodzi, **kw)

    def rampa(self, id, x0, z0, x1, z1, szer, y0, y1, kolor="sciezka", podpora="skala", **kw):
        """Klin od (x0, z0) na wysokości y0 do (x1, z1) na y1 (WedgePart: wysoka ściana po lokalnym +Z)."""
        L = math.hypot(x1 - x0, z1 - z0)
        o = _deg(x1 - x0, z1 - z0)
        cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
        if y0 > 0.05:
            self.dodaj(id + "_podpora", "blok", cx, y0 / 2 - 0.5, cz, szer, y0 + 1.0, L, o, C[podpora], chodzi=True, **kw)
        return self.dodaj(id, "klin", cx, (y0 + y1) / 2, cz, szer, y1 - y0, L, o, C[kolor], chodzi=True, **kw)

    def skala(self, id, x, z, sx, sz_, h, o=0.0, kolor="skala", opaska="skala_c", mech=True, **kw):
        """Skała-przeszkoda (nie do chodzenia) z opaską i mchem."""
        self.dodaj(id, "blok", x, h / 2 - 0.5, z, sx, h + 1.0, sz_, o, C[kolor], chodzi=False, **kw)
        if h >= 5:
            self.dodaj(id + "_opaska", "blok", x, h * 0.55, z, sx + 0.7, 0.9, sz_ + 0.7, o, C[opaska], chodzi=False, ozdoba=True, **kw)
        if mech:
            a = math.radians(o)
            self.dodaj(id + "_mech", "blok", x + 0.12 * sx * math.cos(a), h + 0.65, z - 0.12 * sx * math.sin(a), sx * 0.5, 0.3, sz_ * 0.55,
                       o, C["mech"], chodzi=False, ozdoba=True, **kw)

    def wierzch(self, x, z):
        """Najwyższy wierzch brył do chodzenia w punkcie (do stawiania rekwizytów na wierzchu terenu)."""
        h = 0.0
        for b in self.bryly:
            if b["chodzi"] and not b.get("glebia") and not b.get("lawa"):
                t = _wierzch(b, x, z)
                if t is not None and t > h:
                    h = t
        return h

    def zajete(self, x, z):
        """Skała, woda, lawa albo krawędź — tu drobiazg nie rośnie."""
        for b in self.bryly:
            if _wierzch(b, x, z) is None:
                continue
            if b.get("woda") or b.get("glebia") or b.get("lawa") or (not b["chodzi"] and not b.get("ozdoba")):
                return True
        return False

    def wysokosc(self, x, z, y=0.0):
        """Ziemia pod punktem dla smoka stojącego na wysokości y (zasada z kontraktu: bryły, których spód jest
        wyżej niż y + KROK, są nad głową). Zwraca (h, blokada, woda, lawa)."""
        h, blok, woda, gleb = 0.0, False, False, []
        for b in self.bryly:
            t = _wierzch(b, x, z)
            if t is None or b.get("widoczny_tylko"):
                continue
            spod = b["p"][1] - b["s"][1] / 2
            if spod > y + KROK:
                continue
            if b.get("glebia") or b.get("lawa"):
                gleb.append((t, b))
                continue
            if b["chodzi"]:
                if t > h:
                    h, woda = t, bool(b.get("woda"))
            elif not b.get("ozdoba") and t > y + KROK:
                blok = True
        lawa = False
        for t, b in gleb:
            if t >= h - 0.01:                                    # nic do chodzenia nad taflą: głęboka woda / lawa
                blok = True
                lawa = lawa or bool(b.get("lawa"))
        return h, blok or (h - y > KROK), woda, lawa


def _wierzch(b, x, z):
    """Wysokość wierzchu bryły w punkcie (None = poza obrysem)."""
    cx, cy, cz = b["p"]
    sx, sy, sz_ = b["s"]
    if b["k"] == "walec":
        if math.hypot(x - cx, z - cz) > sx / 2:
            return None
        return cy + sy / 2
    lx, lz = _lok(x, z, cx, cz, b["o"])
    if abs(lx) > sx / 2 or abs(lz) > sz_ / 2:
        return None
    if b["k"] == "klin":
        return cy - sy / 2 + sy * (lz + sz_ / 2) / sz_
    return cy + sy / 2


# =========================================================================== rzeka
RZEKA = [(-166, 117, 9), (-146, 104, 10), (-124, 89, 11), (-96, 68, 12), (-68, 46, 13), (-46, 22, 13), (-37, -2, 13),
         (-34, -28, 13), (-28, -56, 12), (-18, -84, 12), (-8, -110, 11), (-1, -134, 10), (2, -158, 10), (5, -180, 11),
         (7, -192, 12)]


def _rzeka_pkt(t):
    """Punkt i kierunek na rzece dla t w [0, len−1]."""
    i = min(int(t), len(RZEKA) - 2)
    u = t - i
    (ax, az, aw), (bx, bz, bw) = RZEKA[i], RZEKA[i + 1]
    d = math.hypot(bx - ax, bz - az)
    return ax + (bx - ax) * u, az + (bz - az) * u, aw + (bw - aw) * u, ((bx - ax) / d, (bz - az) / d)


def _blisko_rzeki(x, z, zapas):
    for i in range(len(RZEKA) - 1):
        (ax, az, aw), (bx, bz, bw) = RZEKA[i], RZEKA[i + 1]
        dx, dz = bx - ax, bz - az
        u = max(0.0, min(1.0, ((x - ax) * dx + (z - az) * dz) / (dx * dx + dz * dz)))
        if math.hypot(x - ax - u * dx, z - az - u * dz) < (aw + (bw - aw) * u) / 2 + zapas:
            return True
    return False


def _odl_strefy(x, z):
    """Odległość punktu od obszaru gry (suma kształtów stref; 0 lub mniej = w środku)."""
    d = 1e9
    for st in STREFY:
        if st["id"] == "przyszla_kraina":
            continue
        for ks in st["obszar"]:
            if "kolo" in ks:
                a, c, r = ks["kolo"]
                d = min(d, math.hypot(x - a, z - c) - r)
            elif "prostokat" in ks:
                x0, x1, z0, z1 = ks["prostokat"]
                dx, dz = max(x0 - x, 0, x - x1), max(z0 - z, 0, z - z1)
                d = min(d, math.hypot(dx, dz) if dx or dz else -min(x - x0, x1 - x, z - z0, z1 - z))
            else:
                a, c, sx, sz_, o = ks["pas"]
                lx, lz = _lok(x, z, a, c, o)
                dx, dz = max(abs(lx) - sx / 2, 0), max(abs(lz) - sz_ / 2, 0)
                d = min(d, math.hypot(dx, dz) if dx or dz else -min(sx / 2 - abs(lx), sz_ / 2 - abs(lz)))
    return d


# =========================================================================== budowa świata
def zbuduj():
    T = Teren()
    I = {}                    # instancje {id: [[x, z, o, sk, y], …]}
    D = []                    # płaty ziemi [x, z, r, kolor, y, świeci]
    S = {"sekrety": [], "bramy_rozmiaru": [], "kryjowki": [], "lamliwe": [], "wiatry": [], "linie_latarni": []}
    zakazy = []               # (x, z, r) — miejsca zarezerwowane (drobiazg tu nie rośnie)
    RUNY = []                 # (id, x, z, y | None, obrót, gdzie)
    strefa_inst = {}          # (id, indeks) -> strefa

    def daj(id, x, z, o=0.0, sk=1.0, y=None, strefa=None, zakaz=0.0):
        if y is None:
            y = T.wierzch(x, z)
        I.setdefault(id, []).append([round(x, 1), round(z, 1), round(o % 360), round(sk, 2), round(y, 2)])
        strefa_inst[(id, len(I[id]) - 1)] = strefa or T.strefa
        if zakaz:
            zakazy.append((x, z, zakaz))
        return I[id][-1]

    def sekret(id, typ, nazwa, x, z, stadia, zloto, rekw=None, o=0.0, sk=1.0, wymaga=None, opis="", y=None, **dod):
        if rekw:
            e = daj(rekw, x, z, o, sk, y, zakaz=6.0)
            y = e[4]
        elif y is None:
            y = T.wierzch(x, z)
        S["sekrety"].append(dict({"id": id, "typ": typ, "nazwa": nazwa, "x": round(x, 1), "y": round(y, 2), "z": round(z, 1),
                                  "strefa": T.strefa, "stadia": stadia, "zloto": zloto, "rekwizyt": rekw, "wymaga": wymaga,
                                  "opis": opis}, **dod))

    def brama(id, klasa, x, z, o, szer, dl, prowadzi, opis, y=0.0):
        S["bramy_rozmiaru"].append({"id": id, "klasa": klasa, "r_maks": {"mala": 3.0, "srednia": 5.2}[klasa],
                                    "stadia_przechodza": {"mala": [1, 3], "srednia": [1, 5]}[klasa],
                                    "x": round(x, 1), "z": round(z, 1), "y": y, "o": round(o % 360, 1), "szer": szer, "dl": dl,
                                    "strefa": T.strefa, "prowadzi_do": prowadzi, "opis": opis})

    def kryj(typ, x, z, r, sk=None, ile=1):
        rid = {"trawa": "trawa_wysoka", "paproc": "paproc", "trzcina": "trzcina"}[typ]
        los = random.Random(int(x * 13 + z * 7))
        y = T.wierzch(x, z)
        for i in range(ile):
            a = los.uniform(0, 6.283)
            d_ = 0 if i == 0 else r * 0.55
            daj(rid, x + d_ * math.sin(a), z + d_ * math.cos(a), los.uniform(0, 360), sk or r / 4.0, y)
        S["kryjowki"].append({"id": "K%02d" % (len(S["kryjowki"]) + 1), "typ": typ, "x": round(x, 1), "z": round(z, 1), "y": round(y, 2),
                              "r": r, "r_maks_smoka": {"trawa": 5.2, "paproc": 6.8, "trzcina": 3.0}[typ], "strefa": T.strefa})
        zakazy.append((x, z, r))

    def lamliwe(id, rekw, x, z, o, sk, klasa, otwiera, kola):
        e = daj(rekw, x, z, o, sk, zakaz=sk * 6)
        hp = {"lekka": 200, "srednia": 420, "ciezka": 800}[klasa]
        S["lamliwe"].append({"id": id, "rekwizyt": rekw, "x": round(x, 1), "y": e[4], "z": round(z, 1), "o": round(o % 360, 1), "skala": sk,
                             "klasa": klasa, "hp": hp, "od_stadium": 6, "odrost_s": {"lekka": 120, "srednia": 180, "ciezka": 240}[klasa],
                             "zloto": {"lekka": 25, "srednia": 60, "ciezka": 120}[klasa], "strefa": T.strefa, "otwiera": otwiera,
                             "kola": [[round(a, 1), round(b, 1), round(r, 1)] for a, b, r in kola]})

    def wiatr(id, x, z, r, y_cel, opis):
        e = daj("wiatr_kolumna", x, z, 0, r / 4.0)
        S["wiatry"].append({"id": id, "x": round(x, 1), "z": round(z, 1), "y": e[4], "r": r, "y_cel": y_cel, "wznoszenie_s": 0.6,
                            "zasieg_x": 1.5, "od_stadium": 5, "strefa": T.strefa, "opis": opis})
        zakazy.append((x, z, r + 2))

    def plat(x, z, r, kolor, y=0.0, sw=False):
        D.append([round(x, 1), round(z, 1), round(r, 1), kolor, round(y, 3), sw])

    # ----------------------------------------------------------------------- tło i łąka (L0)
    plat(-60.0, 40.0, 560.0, "3D7A3A", -0.06)
    plat(0.0, 0.0, LAKA_R, C["trawa"], 0.0)
    plat(LAS[0], LAS[1], LAS_R, C["las"], 0.01)
    los = random.Random(23)
    for _ in range(18):                                          # plamy koloru łąki (bez pustych pól)
        a, rr = los.uniform(0, 6.283), los.uniform(25, 135)
        x, z = rr * math.sin(a), rr * math.cos(a)
        if not _blisko_rzeki(x, z, 4):
            plat(x, z, los.uniform(10, 20), los.choice((C["trawa_j"], "67B652", "58A848", C["trawa_c"])), 0.02)
    plat(0.0, 0.0, 17.0, C["sciezka"], 0.035)                    # plac startu
    plat(0.0, 0.0, 11.0, C["sciezka_c"], 0.04)
    for x, z in LEGOWISKA:
        plat(x, z, 13.0, "B9A47C", 0.04)
    zakazy += [(x, z, 21.0) for x, z in LEGOWISKA] + [(0.0, 0.0, 24.0)]

    # rzeka: tafla (płytka, spowalnia) + piaszczyste brzegi; od jeziorka pod wodospadem do jeziora na południu
    T.strefa = "rzeka"
    for i in range(len(RZEKA) - 1):
        (ax, az, aw), (bx, bz, bw) = RZEKA[i], RZEKA[i + 1]
        L = math.hypot(bx - ax, bz - az) + 3.0
        o = _deg(bx - ax, bz - az)
        w = (aw + bw) / 2
        T.dodaj("rzeka_%02d" % i, "blok", (ax + bx) / 2, 0.12, (az + bz) / 2, w, 0.24, L, o, C["woda"], "szklo", True, woda=True)
        T.dodaj("brzeg_%02d" % i, "blok", (ax + bx) / 2, 0.08, (az + bz) / 2, w + 5.0, 0.16, L, o, C["brzeg"], chodzi=True, ozdoba=True)
    # mosty (pomost do chodzenia: niewidoczna bryła danych na wysokości 1,6) i brody
    T.strefa = "laka"
    for nr, t in ((1, 6.0), (2, 3.55), (3, 8.2)):
        x, z, w, (dx, dz) = _rzeka_pkt(t)
        o = math.degrees(math.atan2(dx, dz))                    # lokalne X mostu ⟂ do nurtu: (cos o, −sin o)
        daj("most", x, z, o, 1.0, 0.0, "rzeka", zakaz=13)
        T.dodaj("most_%d_pomost" % nr, "blok", x, 1.1, z, 22.0, 1.0, 7.0, o, C["skala_j"], chodzi=True, widoczny=False)
    for t in (7.0, 4.6):
        x, z, w, (dx, dz) = _rzeka_pkt(t)
        for k in (-1, 0, 1):
            daj("kamien_brodu", x + k * 4.2 * dz, z - k * 4.2 * dx, 30 * k, 1.0, 0.24, "rzeka")
    zakazy.append((-172.0, 124.0, 14.0))

    # sekret S01: skrzynia pod Mostem Startowym (na brzegu, w cieniu pomostu)
    x, z, w, (dx, dz) = _rzeka_pkt(6.0)
    sekret("S01", "skrzynia", "Skrzynia pod Mostem Startowym", x + dz * (w / 2 + 1.6), z - dx * (w / 2 + 1.6), [1, 8], 150,
           "skrzynia_ukryta", o=_obrot_ku(-dz, dx), y=0.16, opis="Pod pomostem, od strony placu — widać tylko róg skrzyni.")

    # ----------------------------------------------------------------------- łąka: rzeźba i bramy rozmiaru
    # Kwietny Pagór (L1 = 5): wjazd od zachodu (od placu), z pozostałych stron uskok — ucieczka w dół w jedną stronę
    zakazy += [(71.0, -40.0, 24.0), (-82.0, -22.0, 22.0), (58.0, 24.0, 30.0)]
    T.plaskowyz("pagor_kwietny", 56, 86, -52, -30, 5.0, o=20, wierzch="trawa_j")
    T.plaskowyz("pagor_kwietny_2", 70, 88, -40, -20, 5.0, o=-12, wierzch="trawa_j")
    cx, cz = 71.0, -41.0
    a = math.radians(20)
    zach = (cx - 15 * math.cos(a), cz + 15 * math.sin(a))      # środek zachodniego boku (lokalne −X)
    T.rampa("pagor_kwietny_rampa", zach[0] - 12 * math.cos(a), zach[1] + 12 * math.sin(a), zach[0] + 0.8 * math.cos(a),
            zach[1] - 0.8 * math.sin(a), 9.0, 0.0, 5.0)
    kryj("trawa", 74.0, -38.0, 7.0, 1.9, 2)
    sekret("S03", "skrzynia", "Skrzynia w wysokiej trawie (Kwietny Pagór)", 76.0, -37.0, [1, 8], 200, "skrzynia_ukryta", o=200,
           opis="Na szczycie pagóra, schowana w kępie wysokiej trawy — z kamery widać tylko złoty błysk.")
    for k in ("kwiat_czerwony", "kwiat_zolty", "kwiat_bialy"):
        for i in range(4):
            daj(k, 66 + 4 * i + random.Random(i).uniform(-1, 1), -46 + 3 * (i % 2) + (k == "kwiat_zolty") * 3, 40 * i, 1.1)

    # Bazaltowy Stół (L1 = 6) za rzeką na zachodzie: wjazd od północy; na szczycie kamień runiczny R1
    T.plaskowyz("stol_zachodni", -95, -69, -32, -12, 6.0, o=-15)
    a = math.radians(-15)
    pn = (-82.0 + 10 * math.sin(a), -22.0 + 10 * math.cos(a))
    T.rampa("stol_zachodni_rampa", pn[0] + 13 * math.sin(a), pn[1] + 13 * math.cos(a), pn[0] - 0.8 * math.sin(a), pn[1] - 0.8 * math.cos(a),
            9.0, 0.0, 6.0)
    daj("drogowskaz", -76.0, -16.0, 250, 1.2)

    # Grzbiet Nory (skała 7, nie do chodzenia) z tunelem: skrót dla małych (B02) i Nora skarbów (S04)
    o = 8.0
    for nr, (z0, z1) in enumerate(((2.0, 19.0), (29.0, 46.0))):
        T.skala("grzbiet_nory_%d" % nr, 58.0, (z0 + z1) / 2, 10.0, z1 - z0, 7.0, o, mech=False)
        T.skala("grzbiet_nory_%d_glaz" % nr, 56.5 + 3 * nr, (z0 + z1) / 2 + (3 if nr else -3), 7.0, 9.0, 9.0, o + 25, kolor="skala_j")
    T.dodaj("grzbiet_nory_dach", "blok", 58.0 + 0.0, 6.0, 24.0, 10.0, 2.4, 10.2, o, C["skala_j"], chodzi=False, przenikalny=True)
    T.dodaj("grzbiet_nory_dach_mech", "blok", 58.0, 7.35, 24.0, 7.0, 0.3, 8.0, o, C["mech"], chodzi=False, ozdoba=True, przenikalny=True)
    daj("luk_niski", 52.4, 23.2, 90, 1.0)                         # wejście od placu (znak łapki na zachód)
    daj("luk_niski", 63.6, 24.8, 270, 1.0)
    brama("B02", "mala", 58.0, 24.0, o + 90, 8.0, 14.0, "skrót przez Grzbiet Nory (łąka wschód ↔ legowiska wschodnie)",
          "Tunel 8 × 5 pod grzbietem; duże smoki obchodzą grzbiet (ok. 50 studów).")
    sekret("S04", "skrzynia", "Nora skarbów (w tunelu Grzbietu Nory)", 58.0, 24.0, [1, 3], 250, "skrzynia_ukryta", o=90,
           wymaga="brama B02 (mała)", opis="W połowie tunelu, pod dachem — gra wygasza dach, gdy wejdziesz.")
    kryj("trawa", 46.0, 8.0, 5.0, 1.4)
    kryj("trawa", 70.0, 40.0, 5.0, 1.4)

    # Olbrzymia czaszka z otwartą paszczą (B01, S02) — znak widoczny z placu dla średnich stadiów
    cx, cz = 44.0, 88.0
    oc = _obrot_ku(-cx, -cz)
    daj("czaszka_wielka", cx, cz, oc, 1.0, 0.0, "znak", zakaz=22)
    fx, fz = -math.sin(math.radians(oc)), -math.cos(math.radians(oc))    # przód rekwizytu (paszcza) w świecie
    brama("B01", "mala", cx + fx * 14.0, cz + fz * 14.0, oc, 7.6, 4.0, "wnętrze czaszki (kieszeń z S02)",
          "Prześwit między żuchwą a podniebieniem 7,6 × 5.")
    sekret("S02", "skrzynia", "Skrzynia w paszczy czaszki", cx + fx * 11.0, cz + fz * 11.0, [1, 3], 300, "skrzynia_ukryta", o=oc + 180,
           wymaga="brama B01 (mała)", opis="Skrzynia stoi w paszczy — widać ją z zewnątrz, ale wejdzie tylko mały smok.")

    # wysoka trawa na łące (kryjówki: nazwa nad głową znika, boty gubią cel)
    for x, z, r in ((22, 28, 6.0), (-12, 56, 6.5), (30, -24, 5.5), (14, -66, 6.5), (-58, -70, 6.0), (92, -78, 6.0),
                    (-100, 30, 6.0), (86, 62, 5.5), (-8, 100, 6.0), (-62, -106, 5.5)):
        kryj("trawa", x, z, r, r / 3.6, 2 if r >= 6 else 1)

    # Ukryta Polana (poza murem na 54,5°): wejście tylko norą przez mur (B03), kamień runiczny R2
    a = math.radians(54.5)
    wx, wz = 158 * math.sin(a), 158 * math.cos(a)
    T.strefa = "polana"
    daj("luk_niski", wx, wz, _obrot_ku(-wx, -wz), 1.0)
    brama("B03", "mala", wx, wz, _obrot_ku(-wx, -wz), 9.0, 6.0, "Ukryta Polana za murem (kieszeń z kamieniem runicznym R2)",
          "Niski łuk w murze łąki między legowiskami 1 i 2.")
    px, pz = 182 * math.sin(a), 182 * math.cos(a)
    plat(px, pz, 19.0, "6FBF55", 0.03)
    for i in range(7):                                         # wysokie skały zamykające polanę od zewnątrz
        b = a + math.radians(-80 + i * 27)
        T.skala("polana_skala_%d" % i, px + 22 * math.sin(b), pz + 22 * math.cos(b), 9.0, 8.0, 9.0 + 2 * (i % 2), math.degrees(b) + 90)
    RUNY.append(("R2", px + 4, pz + 3, None, _obrot_ku(-px, -pz), "Ukryta Polana za murem — tylko mały smok (brama B03)"))
    daj("krysztaly_skupisko", px - 6, pz + 5, 30, 0.9)
    for i in range(5):
        daj(("kwiat_niebieski", "kwiat_bialy", "grzyby_swiecace")[i % 3], px - 3 + 3 * i, pz - 7 + (i % 2) * 2, 50 * i, 1.1)

    # ----------------------------------------------------------------------- plac startu i linie latarni (osie widoku)
    T.strefa = "laka"
    linie = {
        "las": ("latarnia_las", [(0, 22), (0, 46), (0, 70), (0, 94), (0, 117)]),
        "kanion": ("latarnia_zar", [(-19, 3), (-58, 6), (-84, 12), (-110, 18), (-136, 24)]),
        "wodospad": ("latarnia_zlota", [(-16, 21), (-30, 42), (-50, 64), (-74, 84), (-104, 104)]),
        "brama": ("latarnia_magia", [(21, -6), (46, -14), (98, -26), (122, -32), (146, -38)]),
    }
    for cel, (rid, pkt) in linie.items():
        for x, z in pkt:
            daj(rid, x, z, 0, 1.0, zakaz=3)
        S["linie_latarni"].append({"cel": cel, "rekwizyt": rid, "punkty": [list(p) for p in pkt]})

    # mur łąki z przerwami: las (0°), brama (104,7°), kanion (280,4°), rzeka NW (306°), rzeka S (180°), nora (54,5°),
    # wyłom do Szlaku Popiołu (230,2°, zasypany głazami do rozbicia)
    przerwy = ((0, 14), (104.7, 9), (280.4, 10), (306.3, 9), (180, 9), (54.5, 6), (230.2, 7))
    for k in range(40):
        kat = 4.5 + 9 * k
        if min(abs((kat - b + 180) % 360 - 180) - w for b, w in przerwy) < 0:
            continue
        x, z = 158.0 * math.sin(math.radians(kat)), 158.0 * math.cos(math.radians(kat))
        daj("sciana_skalna", x, z, _obrot_ku(-x, -z) + 180, random.Random(k).uniform(0.95, 1.15), 0.0, "laka")
    # L06: wyłom w murze zasypany głazami — rozbicie otwiera Szlak Popiołu prosto do kaldery
    a = math.radians(230.2)
    lamliwe("L06", "skala_lamliwa", 160 * math.sin(a), 160 * math.cos(a), _obrot_ku(-math.sin(a), -math.cos(a)), 1.5, "srednia",
            "Szlak Popiołu: legowiska południowo-zachodnie → kaldera (skrót ok. 200 studów)",
            [(160 * math.sin(a), 160 * math.cos(a), 7.5)])

    # ----------------------------------------------------------------------- Wodospad (kotlina NW poza murem, L0)
    T.strefa = "wodospad"
    plat(-164.0, 126.0, 46.0, "5AA64A", 0.015)
    plat(-170.0, 64.0, 30.0, "6A9A4A", 0.016)                    # przejście do wylotu kanionu
    T.dodaj("stawek", "walec", STAWEK[0], 0.15, STAWEK[1], 2 * STAWEK[2], 0.3, 2 * STAWEK[2], 0, C["woda"], "szklo", True,
            glebia=True)
    plat(STAWEK[0], STAWEK[1], STAWEK[2] + 3.0, C["brzeg"], 0.02)
    # Ostroga wyżyny wysunięta w kotlinę: wodospad spada z jej POŁUDNIOWEGO lica (kamera gry patrzy z południa, więc
    # widać go z przodu), za kurtyną wody wejście do jaskini, obok półka z gniazdem
    for nr, (x0, x1, z0, z1) in enumerate(((-190, -150, 150, 172), (-190, -176, 136, 150), (-160, -150, 136, 150))):
        T.plaskowyz("ostroga_%d" % nr, x0, x1, z0, z1, WYS["L2"])
    T.plaskowyz("dach_jaskini_wodospadu", -176, -160, 136, 150, WYS["L2"], y0=9.0, przenikalny=True)
    daj("grota_wejscie", -168.0, 136.0, 0, 0.95, 0.0)              # o = 0: przód rekwizytu patrzy na południe (−Z)
    daj("wodospad", -168.0, 136.3, 0, 1.0, 0.0)                    # kurtyna wody przed wejściem
    for i in range(6):
        b = math.radians(110 + i * 28)
        daj(("trzcina", "lilia")[i % 2], STAWEK[0] + (STAWEK[2] + (1.0 if i % 2 == 0 else -3.0)) * math.sin(b),
            STAWEK[1] + (STAWEK[2] + (1.0 if i % 2 == 0 else -3.0)) * math.cos(b), 60 * i, 1.0, 0.2 if i % 2 else 0.0)
    kryj("trzcina", -150.0, 108.0, 4.0, 1.2, 2)
    # półka z gniazdem na licu ostrogi (y 8): tylko szybowaniem z prądu W03 albo zeskokiem z ostrogi
    T.plaskowyz("polka_gniazda", -158, -150, 130.5, 136.5, 8.0, y0=4.0, chodzi=True, opaska_y=0.4)
    sekret("S06", "gniazdo", "Gniazdo na półce skalnej", -154.0, 133.0, [5, 8], 900, "gniazdo_orle", o=0,
           wymaga="WING GLIDE z prądu W03 albo zeskok z ostrogi", opis="Złote i kryształowe jajo na półce obok wodospadu.")
    wiatr("W03", -143.0, 122.0, 4.5, 20.0, "Kotlina: unosi szybującego na półkę z gniazdem (8) albo na ostrogę (14).")
    brama("B04", "srednia", -168.0, 136.5, 0, 9.0, 3.0, "Jaskinia za wodospadem (S05, kamień runiczny R3)",
          "Wejście 9 × 8 za kurtyną wody; między jeziorkiem a skałą ścieżka 6 studów.")
    sekret("S05", "jaskinia", "Jaskinia za wodospadem", -165.0, 145.0, [1, 5], 600, "skrzynia_ukryta", o=180, y=0.0,
           wymaga="brama B04 (średnia)", opis="Za kurtyną wody: kryształy, świecące grzyby, skrzynia i kamień runiczny.")
    daj("krysztaly_skupisko", -173.0, 146.0, 20, 0.7, 0.0)
    daj("grzyby_swiecace", -162.5, 140.0, 0, 1.0, 0.0)
    RUNY.append(("R3", -171.0, 140.5, 0.0, 180, "jaskinia za wodospadem — brama średnia B04"))
    # rampa z kotliny na ostrogę (od wschodu)
    T.rampa("rampa_kotliny", -125.0, 164.0, -150.6, 164.0, 12.0, 0.0, 14.0)
    for i, (x, z) in enumerate(((-138, 146), (-132, 128), (-136, 178), (-200, 60), (-176, 44), (-146, 104))):
        daj(("krzak", "glaz_1", "drzewo_1", "glaz_2", "krzak", "kwiat_zolty")[i], x, z, 40 * i, 1.0)

    # ----------------------------------------------------------------------- Wyżyna Wichrów (L2 = 14) i punkt widokowy
    T.strefa = "wyzyna"
    h = WYS["L2"]
    for nr, (x0, x1, z0, z1) in enumerate(((-330, -254, 52, 116), (-238, -206, 52, 116), (-254, -238, 70, 116), (-206, -188, 52, 116),
                                           (-330, -188, 116, 132), (-330, -188, 132, 196))):
        T.plaskowyz("wyzyna_%d" % nr, x0, x1, z0, z1, h)
    T.plaskowyz("wyzyna_polnoc", -318, -200, 196, 256, WYS["L2"] + 4.0, wierzch="trawa_j")     # wyższy stopień 18 (na północy)
    T.rampa("wyzyna_polnoc_rampa", -214.0, 184.0, -214.0, 196.6, 10.0, 14.0, 18.0, podpora="skala")
    T.plaskowyz("dach_groty_kanionu", -254, -238, 52, 70, h, y0=10.0, przenikalny=True)
    # wrzos i jaśniejsze płaty na wierzchu (bez pustych pól)
    los = random.Random(5)
    for i in range(16):
        x, z = los.uniform(-322, -196), los.uniform(58, 192)
        plat(x, z, los.uniform(4, 9), (C["wrzos"], "88B84E", "6E9E44", "A9C85A")[i % 4], h + 0.03)
    for i in range(6):
        plat(los.uniform(-312, -206), los.uniform(200, 252), los.uniform(4, 8), ("88B84E", C["wrzos"], "6E9E44")[i % 3], h + 4.03)
    # wychodnie skalne na wierzchu (nie do chodzenia) — rzeźba widoczna z punktu widokowego
    for i, (x, z, sx_, sz_, hh, o) in enumerate(((-300, 72, 14, 10, 6, 20), (-212, 88, 10, 14, 5, -15), (-312, 160, 12, 16, 7, 8),
                                                 (-236, 236, 16, 10, 6, 35), (-290, 244, 10, 10, 5, -10), (-268, 132, 8, 10, 4, 50))):
        T.skala("wychodnia_%d" % i, x, z, sx_, sz_, h + (4 if z > 196 else 0) + hh, o, kolor=("skala", "skala_j")[i % 2])
    daj("krag_kamienny", -292.0, 98.0, 0, 1.0)
    daj("ruiny_mur", -248.0, 222.0, 90, 1.0)
    daj("ruiny_mur", -238.0, 212.0, 30, 0.9)
    daj("filar_ruin", -300.0, 186.0, 0, 1.0)
    # głazy wzdłuż urwisk (łamią prostą krawędź klocków)
    for i, (x, z, o) in enumerate(((-188, 70, 0), (-188, 100, 10), (-152, 178, -8), (-188, 196, 4), (-205, 52, 85),
                                    (-226, 52, 95), (-270, 52, 80), (-300, 52, 92), (-322, 52, 90), (-330, 90, 0),
                                    (-330, 170, 5), (-318, 240, -4), (-260, 256, 90), (-205, 230, 3))):
        T.skala("urwisko_glaz_%d" % i, x, z, 7.0 + 3 * (i % 3), 9.0 + 2 * (i % 2), 9.0 + 3 * ((i + 1) % 3), o, mech=False)
    # punkt widokowy: dwa stopnie (20, 26) z rampami
    T.plaskowyz("wzgorze_1", -292, -252, 180, 220, 20.0, y0=13.0, wierzch="trawa_w")
    T.plaskowyz("wzgorze_szczyt", -284, -264, 198, 216, 26.0, y0=19.0, wierzch="mech")
    T.rampa("wzgorze_rampa_1", -262.0, 165.5, -262.0, 180.6, 10.0, 14.0, 20.0, podpora="skala")
    T.rampa("wzgorze_rampa_2", -252.5, 207.0, -264.6, 207.0, 8.0, 20.0, 26.0, podpora="skala")
    sekret("S10", "punkt_widokowy", "Skarb punktu widokowego", -274.0, 207.0, [1, 8], 1200, "punkt_widokowy", o=_obrot_ku(274, -207),
           opis="Na szczycie: ognisko-latarnia i luneta. Kamera odjeżdża i pokazuje całą mapę (strefa kamery `panorama`).")
    wiatr("W04", -246.0, 178.0, 4.5, 30.0, "U stóp wzgórza: wynosi szybującego na szczyt (26).")
    # przełęcz martwych drzew: skały z wąskim przejściem zagrodzonym dwoma martwymi drzewami (L05)
    T.skala("przelecz_skala_1", -230.0, 160.0, 12.0, 26.0, 8.0, 10)
    T.skala("przelecz_skala_2", -230.0, 196.0, 12.0, 26.0, 8.0, -6)
    lamliwe("L05", "drzewo_martwe", -229.0, 178.0, 0, 1.0, "lekka", "przełęcz: rampa z kotliny → wzgórze (skrót ok. 60 studów)",
            [(-229.0, 178.0, 1.4)])
    daj("drzewo_martwe", -233.0, 174.5, 120, 0.9)
    S["lamliwe"][-1]["dodatkowe"] = [[-233.0, 174.5, 120, 0.9]]
    n = 0
    for i in range(200):                                        # sosny na wyżynie (bez wzgórza, przełęczy i ramp)
        b = random.Random(100 + i)
        x, z = b.uniform(-325, -195), b.uniform(58, 250)
        if n < 20 and T.wierzch(x, z) in (h, h + 4) and not T.zajete(x, z) and not (-298 < x < -246 and 158 < z < 226) \
                and not (-246 < x < -208 and 150 < z < 205) and all(math.hypot(x - a, z - c) > 9 for a, c, _ in zakazy[-40:]):
            daj(("sosna_1", "sosna_2")[i % 2], x, z, b.uniform(0, 360), b.uniform(0.8, 1.1))
            zakazy.append((x, z, 5.0))
            n += 1
    for i in range(24):
        b = random.Random(200 + i)
        x, z = b.uniform(-320, -200), b.uniform(60, 250)
        if T.wierzch(x, z) in (h, h + 4) and not T.zajete(x, z):
            daj(("glaz_1", "krzak", "kwiat_niebieski", "glaz_2", "trawa_2")[i % 5], x, z, b.uniform(0, 360), 1.0)

    # ----------------------------------------------------------------------- Kanion Wichrów (L0, ściany 14–16)
    T.strefa = "kanion"
    T.pudlo("kanion_dno", -268, -158, 10, 52, -0.2, 0.04, kolor=C["piach"], chodzi=True)
    T.dodaj("kanion_dno_luk", "blok", -284.0, -0.08, -2.0, 40.0, 0.24, 66.0, 34.0, C["piach"], chodzi=True)
    for i, (x, z, sx_, sz_, o) in enumerate(((-200, 24, 40, 5, 4), (-238, 38, 30, 4, -6), (-280, 8, 26, 4, 36), (-176, 38, 22, 4, -10),
                                             (-262, 20, 18, 3, 12), (-220, 16, 26, 3, 0))):
        T.dodaj("kanion_pas_%d" % i, "blok", x, 0.06, z, sx_, 0.1, sz_, 90 + o, C["piach_c"], chodzi=True, ozdoba=True)
    # południowa grań (16; wierzch tylko dla szybujących z prądu W05)
    # zasada kamery: kamera gry patrzy z południa, więc ściana po południowej stronie przejścia jest NISKA (8–12),
    # a wysoka, prążkowana ściana stoi na północy (widać jej lico)
    for nr, (x0, x1, z0, z1, hh) in enumerate(((-246, -214, -20, 10, 9.0), (-214, -184, -24, 10, 10.0), (-184, -166, -30, 8, 8.0),
                                               (-246, -166, -52, -20, 12.0))):
        T.plaskowyz("gran_poludniowa_%d" % nr, x0, x1, z0, z1, hh, skala="kanion", opaska="kanion_c", wierzch="kanion_c")
    T.plaskowyz("gran_poludniowa_4", -270, -246, -24, 10, 9.0, skala="kanion", opaska="kanion_c", wierzch="kanion_c", o=8)
    T.plaskowyz("zachodnia_sciana", -360, -318, -30, 52, 20.0, skala="kanion", opaska="kanion_c", wierzch="kanion_c", chodzi=False)
    for nr, (x0, x1) in enumerate(((-330, -254), (-238, -205), (-196, -188))):          # prążkowane lico północnej ściany
        T.pudlo("kanion_lico_%d" % nr, x0, x1, 51.4, 53.4, -0.5, 13.4, kolor=C["kanion"], chodzi=False)
        for j, (y0, y1, k) in enumerate(((3.0, 4.2, "kanion_c"), (7.4, 8.2, "kanion_j"), (10.6, 11.6, "kanion_c"))):
            T.pudlo("kanion_lico_%d_pas_%d" % (nr, j), x0, x1, 51.1, 53.0, y0, y1, kolor=C[k], chodzi=False, ozdoba=True)
    for i, (x, z, sk) in enumerate(((-232, -6, 0.8), (-196, -14, 0.7), (-176, -42, 0.9), (-258, -10, 0.6))):
        daj("iglica_skalna", x, z, 53 * i, sk)
    for i, (x, z) in enumerate(((-240, 2), (-222, -14), (-200, 4), (-190, -18), (-172, -4), (-228, -40), (-196, -44), (-262, 0))):
        daj(("glaz_2", "krzak", "glaz_1", "drzewo_martwe", "glaz_2", "krzak", "glaz_1", "kamyk")[i], x, z, 61 * i,
            (1.0, 1.2, 1.3, 0.6, 0.8, 1.0, 1.1, 2.0)[i])
    for i, (x, z) in enumerate(((-186, 30), (-242, 24), (-262, 40), (-200, 42), (-288, 6), (-170, 22), (-226, 14))):
        daj(("glaz_1", "kamyk", "glaz_2", "kamyk", "glaz_1", "kamyk", "drzewo_martwe")[i], x, z, 47 * i,
            (1.0, 1.6, 0.9, 1.8, 1.1, 1.5, 0.7)[i], 0.0)
    RUNY.append(("R5", -206.0, -20.0, None, 0, "południowa grań kanionu — tylko szybowaniem z prądu W05"))
    wiatr("W05", -205.0, 15.0, 4.5, 22.0, "Pod południową granią: wynosi szybującego na grań (10) — kamień runiczny R5.")
    wiatr("W01", -228.0, 47.0, 4.5, 20.0, "Pod północną ścianą: wynosi szybującego na wyżynę (14).")
    # naturalny łuk nad kanionem, iglice
    daj("luk_skalny", -214.0, 31.0, 90, 1.0, 0.0, zakaz=16)
    for i, (x, z, sk) in enumerate(((-178, 14, 0.9), (-252, 16, 1.1), (-188, 47, 0.8), (-296, 22, 1.0), (-266, 47, 0.7))):
        daj("iglica_skalna", x, z, 37 * i, sk, 0.0)
    # rampa z kanionu na wyżynę — u stóp osypisko (L01, ciężka)
    T.rampa("rampa_kanionu", -168.0, 48.0, -197.0, 48.0, 8.0, 0.0, 14.0, podpora="skala")
    T.pudlo("rampa_kanionu_ladowisko", -205, -196, 44, 52, -1.0, 14.0, kolor=C["skala"], chodzi=True)
    lamliwe("L01", "skala_lamliwa", -168.0, 48.0, 90, 1.25, "ciezka", "rampa z kanionu na Wyżynę Wichrów (skrót ok. 250 studów)",
            [(-168.0, 48.0, 5.5)])
    # kryształowa grota kanionu (S09), zamknięta pękającą skałą (L02)
    daj("grota_wejscie", -246.0, 52.0, 0, 0.95, 0.0)             # przód (+Z) w stronę kanionu = −Z świata… patrz obrót niżej
    I["grota_wejscie"][-1][2] = 0                              # wejście patrzy na południe, do kanionu
    lamliwe("L02", "skala_lamliwa", -246.0, 46.5, 0, 1.15, "ciezka", "Kryształowa grota kanionu (S09)", [(-246.0, 46.5, 5.0)])
    sekret("S09", "jaskinia", "Kryształowa grota kanionu", -246.0, 62.0, [6, 8], 1800, "skrzynia_ukryta", o=180, y=0.0,
           wymaga="rozbij L02 (stadium 6+)", opis="Grota pełna kryształów za pękającą skałą; świeci przez szczeliny.")
    daj("krysztaly_skupisko", -250.5, 66.0, 10, 0.9, 0.0)
    daj("krysztaly_skupisko", -241.0, 64.5, 200, 0.7, 0.0)

    # ----------------------------------------------------------------------- Kaldera i SKY NEST (wyspa tylko szybowaniem)
    T.strefa = "kaldera"
    kx, kz = KALDERA
    plat(kx, kz, KALDERA_R + 2, C["popiol"], 0.02)
    T.dodaj("lawa", "walec", kx, 0.15, kz, 2 * LAWA_R, 0.3, 2 * LAWA_R, 0, "C2410F", "swiecacy", True, lawa=True)
    plat(kx, kz, LAWA_R + 1.6, "FF7A2A", 0.025, True)
    los = random.Random(9)
    for i in range(9):                                          # kra zastygłej lawy (ozdoba)
        b, rr = math.radians(i * 40 + los.uniform(-10, 10)), los.uniform(21, 39)
        T.dodaj("kra_%d" % i, "blok", kx + rr * math.sin(b), 0.36, kz + rr * math.cos(b), los.uniform(3, 7), 0.22, los.uniform(3, 6),
                los.uniform(0, 90), C["bazalt_c"], chodzi=False, ozdoba=True)
    T.dodaj("sky_nest", "walec", kx, 0.1, kz, 2 * WYSPA_R, 2.2, 2 * WYSPA_R, 0, C["bazalt"], chodzi=True)
    T.dodaj("sky_nest_wierzch", "walec", kx, 1.3, kz, 2 * WYSPA_R - 2, 0.2, 2 * WYSPA_R - 2, 0, C["popiol"], chodzi=True)
    daj("oltarz_kul", kx, kz, 0, 0.7)
    for i in range(6):
        b = math.radians(30 + 60 * i)
        daj(("bazalt_1", "bazalt_2")[i % 2], kx + 12.5 * math.sin(b), kz + 12.5 * math.cos(b), 40 * i, 0.8)
    RUNY.append(("R6", kx + 6.0, kz - 9.0, None, 0, "SKY NEST — tylko szybowaniem nad lawą"))
    sekret("S12", "wyspa", "Ołtarz SKY NEST", kx, kz, [5, 8], 500, None, wymaga="WING GLIDE nad lawą",
           opis="Wielkie kule na wyspie (jak dotąd w grze); pierwsza wizyta: premia i zadanie dnia „Visit the lava island”.")
    # urwiska wokół kaldery (bez wejść: północ = kanion, wschód = Szlak Popiołu)
    for i in range(9):
        kat = 180 + 40 * i
        if any(abs((kat - w + 180) % 360 - 180) < 26 for w in (20, 75)):
            continue
        b = math.radians(kat)
        T.plaskowyz("kaldera_sciana_%d" % i, kx + 80 * math.sin(b) - 16, kx + 80 * math.sin(b) + 16, kz + 80 * math.cos(b) - 15,
                    kz + 80 * math.cos(b) + 15, 18.0 if math.cos(b) > -0.2 else 9.0, skala="bazalt", opaska="bazalt_c", wierzch="popiol",
                    o=kat, chodzi=False)
    # półka startowa (L1 = 7) z prądem W02 — skok na wyspę
    b = math.radians(330)
    lx, lz = kx + 56 * math.sin(b), kz + 56 * math.cos(b)
    T.plaskowyz("polka_startowa", lx - 8, lx + 8, lz - 7, lz + 7, 7.0, o=330, skala="bazalt", opaska="bazalt_c", wierzch="popiol")
    T.rampa("polka_startowa_rampa", lx + 22 * math.sin(math.radians(60)), lz + 22 * math.cos(math.radians(60)),
            lx + 7.6 * math.sin(math.radians(60)), lz + 7.6 * math.cos(math.radians(60)), 8.0, 0.0, 7.0, kolor="popiol")
    wiatr("W02", kx + 47 * math.sin(b), kz + 47 * math.cos(b), 4.0, 24.0, "Czubek półki startowej: wynosi nad lawę — szybowanie na SKY NEST.")
    for i in range(7):
        b = math.radians(80 + 47 * i)
        daj("szczelina_lawy", kx + 55 * math.sin(b), kz + 55 * math.cos(b), 30 * i, 1.0)
        daj(("skala_lawy", "bazalt_1")[i % 2], kx + 62 * math.sin(b + 0.2), kz + 62 * math.cos(b + 0.2), 50 * i, 1.0)

    # Szlak Popiołu: wyłom w murze łąki (L06) → wschodnie wejście kaldery
    T.strefa = "szlak_popiolu"
    T.dodaj("szlak_popiolu_dno", "blok", -191.0, 0.03, -102.0, 18.0, 0.06, 148.0, 90.0, C["popiol"], chodzi=True)
    for i, x in enumerate((-150, -175, -205, -232)):
        daj(("szczelina_lawy", "bazalt_2", "skala_lawy", "bazalt_1")[i], x, -104 + (14 if i % 2 else -14), 40 * i, 0.9)
    for i, x in enumerate((-140, -165, -190, -215, -240)):
        T.skala("szlak_sciana_s_%d" % i, x, -126.0, 22.0, 10.0, 12.0 + 2 * (i % 2), 92, kolor="bazalt", opaska="bazalt_c", mech=False)

    # ----------------------------------------------------------------------- Droga do zapieczętowanej bramy (wschód)
    T.strefa = "brama"
    a = math.radians(104.7)
    g0 = (150 * math.sin(a), 150 * math.cos(a))
    gx, gz = 226.0, -62.0
    od = _deg(gx - g0[0], gz - g0[1])
    L = math.hypot(gx - g0[0], gz - g0[1])
    T.dodaj("droga_bramy", "blok", (g0[0] + gx) / 2, 0.03, (g0[1] + gz) / 2, 12.0, 0.06, L, od, C["sciezka"], chodzi=True)
    nx, nz = math.cos(math.radians(od)), -math.sin(math.radians(od))
    for zn in (1, -1):
        T.plaskowyz("droga_sciana_%d" % (zn > 0), (g0[0] + gx) / 2 + zn * 24 * nx - 6 - L / 2 + 20, (g0[0] + gx) / 2 + zn * 24 * nx + 6 + L / 2 - 20,
                    (g0[1] + gz) / 2 + zn * 24 * nz - 9, (g0[1] + gz) / 2 + zn * 24 * nz + 9, 12.0, o=od + 90, chodzi=False)
    daj("brama_zapieczetowana", gx, gz, _obrot_ku(-(gx - g0[0]), -(gz - g0[1])), 1.0, 0.0, "brama", zakaz=20)
    sekret("S13", "zapowiedz", "Zapieczętowana brama (zapowiedź nowej krainy)", gx - 8 * math.sin(math.radians(od)),
           gz - 8 * math.cos(math.radians(od)), [1, 8], 150, None, wymaga="dojdź do bramy",
           opis="Pieczęć ma 6 gniazd — każdy zebrany kamień runiczny zapala jedno. Za bramą strefa na aktualizację.")
    for i, t in enumerate((0.25, 0.45, 0.65, 0.82)):
        x, z = g0[0] + (gx - g0[0]) * t, g0[1] + (gz - g0[1]) * t
        zn = 1 if i % 2 else -1
        daj(("ruiny_mur", "filar_ruin", "ruiny_mur", "krysztaly_skupisko")[i], x + zn * 11 * nx, z + zn * 11 * nz, od + 90 * zn, 1.0)
        daj(("filar_ruin", "krysztaly_skupisko", "filar_ruin", "filar_ruin")[i], x - zn * 11 * nx, z - zn * 11 * nz, od, 0.9)
    T.strefa = "przyszla_kraina"
    T.plaskowyz("przyszla_kraina_mur", 236, 252, -110, -14, 22.0, skala="bazalt", opaska="bazalt_c", wierzch="mech", o=od - 90,
                chodzi=False)

    # ----------------------------------------------------------------------- Jezioro (południe) z wysepką i brodem
    T.strefa = "jezioro"
    jx, jz = JEZIORO
    plat(jx, jz, JEZIORO_R + 6, C["brzeg"], 0.015)
    plat(jx, jz, JEZIORO_R + 16, "5AA64A", 0.01)
    T.dodaj("jezioro", "walec", jx, 0.12, jz, 2 * JEZIORO_R, 0.24, 2 * JEZIORO_R, 0, C["woda"], "szklo", True, glebia=True)
    T.dodaj("wysepka", "walec", jx + 2, 0.35, jz - 10, 14.0, 0.7, 14.0, 0, C["trawa_j"], chodzi=True)
    b0, b1 = (jx + 25.0, jz + 25.0), (jx + 4.0, jz - 6.0)            # bród od północno-wschodniego brzegu na wysepkę
    T.dodaj("brod_jeziora", "blok", (b0[0] + b1[0]) / 2, 0.15, (b0[1] + b1[1]) / 2, 5.0, 0.3, math.hypot(b1[0] - b0[0], b1[1] - b0[1]) + 2,
            _deg(b1[0] - b0[0], b1[1] - b0[1]), C["woda_j"], "szklo", True, woda=True)
    for i in range(5):
        daj("kamien_brodu", b0[0] + (b1[0] - b0[0]) * (i + 0.5) / 5, b0[1] + (b1[1] - b0[1]) * (i + 0.5) / 5, 25 * i, 1.0, 0.3)
    sekret("S11", "skrzynia", "Skrzynia na wysepce", jx + 3, jz - 11, [1, 8], 300, "skrzynia_ukryta", o=0,
           wymaga="bród z kamieni od północnego wschodu", opis="Wysepka z drzewem; płytki bród z kamieniami od brzegu przy murze łąki.")
    daj("drzewo_3", jx + 0, jz - 14, 40, 0.9)
    for i in range(12):
        b = math.radians(i * 30 + 10)
        rr = JEZIORO_R + (1.0 if i % 2 == 0 else -4.0)
        daj(("trzcina", "lilia")[i % 2], jx + rr * math.sin(b), jz + rr * math.cos(b), 30 * i, 1.0, 0.0 if i % 2 == 0 else 0.24)
    for i in range(9):                                          # drzewa i skały zamykające jezioro od południa
        b = math.radians(100 + i * 20)
        daj(("drzewo_1", "drzewo_2", "glaz_2")[i % 3], jx + (JEZIORO_R + 18) * math.sin(b), jz + (JEZIORO_R + 18) * math.cos(b), 50 * i,
            1.1, 0.0)

    # ----------------------------------------------------------------------- DEEP WOODS (L0) z grotą i barykadami
    T.strefa = "las"
    lx, lz = LAS
    los = random.Random(41)
    for _ in range(9):
        a, rr = los.uniform(0, 6.283), los.uniform(0, 95)
        plat(lx + rr * math.sin(a), lz + rr * math.cos(a), los.uniform(9, 16), los.choice(("24503C", "32694C")), 0.03)
    plat(0.0, 140.0, 6.0, C["sciezka"], 0.035)
    daj("luk_korzeni", 0.0, 131.0, 0, 1.3, 0.0, zakaz=12)
    daj("krag_kamienny", 46.0, 214.0, 0, 1.0, 0.0, zakaz=16)
    daj("posag_prastarego", 0.0, 300.0, 0, 1.0, 0.0, zakaz=18)
    for i, (x, z) in enumerate(((-24, 312), (22, 318), (30, 286), (-30, 284))):
        daj(("filar_ruin", "ruiny_mur")[i % 2], x, z, 40 * i, 1.0)
    RUNY.append(("R4", 10.0, 282.0, None, 180, "DEEP WOODS — przy posągu Prastarego"))
    # Wzgórze Mchu z kryształową grotą (B05, S07)
    gx0, gz0 = -58.0, 282.0
    T.skala("wzgorze_mchu_pn", gx0 - 2, gz0 + 13, 30.0, 10.0, 11.0, 0, kolor="skala", mech=True)
    T.skala("wzgorze_mchu_pd", gx0 - 2, gz0 - 13, 30.0, 10.0, 10.0, 0, kolor="skala_j", mech=True)
    T.skala("wzgorze_mchu_zach", gx0 - 13, gz0, 8.0, 16.0, 12.0, 0, kolor="skala", mech=True)
    T.dodaj("wzgorze_mchu_dach", "blok", gx0 + 1, 10.0, gz0, 20.0, 3.0, 17.0, 0, C["skala"], chodzi=False, przenikalny=True)
    T.dodaj("wzgorze_mchu_dach_mech", "blok", gx0 + 1, 11.7, gz0, 16.0, 0.4, 14.0, 0, C["mech"], chodzi=False, ozdoba=True, przenikalny=True)
    daj("grota_wejscie", gx0 + 11.5, gz0, _obrot_ku(-1, 0) + 180, 0.95, 0.0)
    I["grota_wejscie"][-1][2] = round(_obrot_ku(1, 0)) % 360   # wejście patrzy na wschód
    brama("B05", "srednia", gx0 + 11.5, gz0, 90, 9.0, 4.0, "Kryształowa grota Wzgórza Mchu (S07)", "Wejście od wschodu, 9 × 8.")
    sekret("S07", "jaskinia", "Kryształowa grota Wzgórza Mchu", gx0 - 3, gz0, [1, 5], 800, "skrzynia_ukryta", o=90, y=0.0,
           wymaga="brama B05 (średnia)", opis="Grota pod wzgórzem: kryształy i grzyby świecą na niebiesko.")
    daj("krysztaly_skupisko", gx0 - 6, gz0 + 5, 0, 0.8, 0.0)
    daj("krysztaly_skupisko", gx0 + 2, gz0 - 5, 140, 0.7, 0.0)
    daj("grzyby_swiecace", gx0 - 7, gz0 - 4, 0, 1.0, 0.0)
    # skalny próg w poprzek lasu z przejściem zawalonym martwym drzewem (L03): skrót brama lasu → posąg
    T.skala("prog_lasu_zach", -26.0, 252.0, 40.0, 8.0, 4.5, 0, kolor="skala_j")
    T.skala("prog_lasu_wsch", 26.0, 252.0, 40.0, 8.0, 4.5, 0, kolor="skala")
    lamliwe("L03", "kloda_martwa", 0.0, 252.0, 0, 0.95, "srednia", "skrót: brama lasu → posąg Prastarego (ok. 50 studów mniej)",
            [(-4.6, 252.0, 1.6), (-1.5, 252.0, 1.6), (1.6, 252.0, 1.6), (4.7, 252.0, 1.6)])
    # zakątek ze skrzynią za zwalonym drzewem (L04, S08)
    nx0, nz0 = 74.0, 292.0
    T.skala("zakatek_pn", nx0, nz0 + 10, 22.0, 6.0, 9.0, 0)
    T.skala("zakatek_wsch", nx0 + 11, nz0, 6.0, 22.0, 9.0, 0)
    T.skala("zakatek_pd", nx0 + 2, nz0 - 10, 18.0, 6.0, 4.0, 0)
    lamliwe("L04", "kloda_martwa", nx0 - 9.5, nz0, 90, 0.75, "srednia", "zakątek ze skrzynią S08", [(nx0 - 9.5, nz0 - 3, 1.6), (nx0 - 9.5, nz0 + 3, 1.6)])
    sekret("S08", "skrzynia", "Skrzynia za martwym drzewem", nx0 + 2, nz0, [6, 8], 1000, "skrzynia_ukryta", o=270,
           wymaga="rozbij L04 (stadium 6+)", opis="Zakątek w skałach; martwe drzewo z żarem w pęknięciach mówi „rozbij”.")
    for x, z, r in ((-40, 200, 6.0), (36, 170, 6.0), (70, 240, 6.5), (-70, 230, 6.0), (-20, 330, 6.0), (40, 330, 5.5),
                    (-88, 290, 5.0), (20, 210, 5.0)):
        kryj("paproc", x, z, r, r / 3.4, 2 if r >= 6 else 1)

    # ----------------------------------------------------------------------- dekoracja (deterministycznie)
    def wolne(x, z, zapas=0.0):
        if any(math.hypot(x - a, z - b) < r + zapas for a, b, r in zakazy):
            return False
        if _blisko_rzeki(x, z, 3.0 + zapas):
            return False
        if T.zajete(x, z):
            return False
        hh = T.wierzch(x, z)
        return all(abs(T.wierzch(x + dx, z + dz) - hh) < 0.3 and not T.zajete(x + dx, z + dz)
                   for dx, dz in ((2.5, 0), (-2.5, 0), (0, 2.5), (0, -2.5)))

    los = random.Random(7)

    def siej(id, n, srodek, r0, r1, skale=(0.85, 1.2), kat=None, strefa="laka", zapas=0.0):
        proby = 0
        while n > 0 and proby < 6000:
            proby += 1
            a = math.radians(los.uniform(*kat) if kat else los.uniform(0, 360))
            rr = math.sqrt(los.uniform(r0 * r0, r1 * r1))
            x, z = srodek[0] + rr * math.sin(a), srodek[1] + rr * math.cos(a)
            if not wolne(x, z, zapas):
                continue
            daj(id, x, z, los.uniform(0, 360), los.uniform(*skale), strefa=strefa)
            n -= 1

    def kepy(id, ile_kep, w_kepie, srodek, r0, r1, rozrzut, strefa="laka"):
        proby = 0
        while ile_kep > 0 and proby < 400:
            proby += 1
            a, rr = math.radians(los.uniform(0, 360)), math.sqrt(los.uniform(r0 * r0, r1 * r1))
            cx_, cz_ = srodek[0] + rr * math.sin(a), srodek[1] + rr * math.cos(a)
            if not wolne(cx_, cz_, 3.0):
                continue
            ile_kep -= 1
            zakazy.append((cx_, cz_, rozrzut + 1.0))
            for _ in range(w_kepie):
                b, d_ = math.radians(los.uniform(0, 360)), los.uniform(0.6, rozrzut)
                daj(id, cx_ + d_ * math.sin(b), cz_ + d_ * math.cos(b), los.uniform(0, 360), los.uniform(0.85, 1.25), strefa=strefa)

    T.strefa = "laka"
    siej("trawa_1", 46, (0, 0), 0, 146)
    kepy("trawa_2", 12, 4, (0, 0), 0, 140, 4.5)
    for k in ("czerwony", "zolty", "niebieski", "bialy"):
        kepy("kwiat_" + k, 3, 6, (0, 0), 20, 140, 4.5)
    siej("kamyk", 16, (0, 0), 0, 146)
    siej("glaz_1", 4, (0, 0), 30, 135, zapas=3)
    siej("glaz_2", 3, (0, 0), 40, 130, zapas=3)
    siej("krzak", 16, (0, 0), 95, 146, zapas=2)
    siej("krzak", 8, (0, 0), 30, 95, zapas=2)
    for i, id in enumerate(("drzewo_1", "drzewo_2", "drzewo_3")):
        siej(id, (3, 2, 3)[i], (0, 0), 45, 138, (0.9, 1.15), zapas=3)
        for j in range((6, 6, 5)[i]):                           # za murem (poza bramami i strefami)
            b = random.Random(300 + 10 * i + j)
            kat = b.uniform(0, 360)
            if any(abs((kat - w + 180) % 360 - 180) < 22 for w in (0, 104.7, 180, 230.2, 280.4, 306.3, 54.5)):
                continue
            rr = b.uniform(166, 186)
            x, z = rr * math.sin(math.radians(kat)), rr * math.cos(math.radians(kat))
            if math.hypot(x - LAS[0], z - LAS[1]) > LAS_R + 6 and not (-200 < x < -110 and 40 < z < 200):
                daj(id, x, z, b.uniform(0, 360), b.uniform(1.0, 1.4), 0.0, "laka")
    siej("grzyb", 10, (0, 0), 20, 146)
    siej("kloda", 3, (0, 0), 50, 135, zapas=3)
    daj("drogowskaz", 9.0, 15.0, 200, 1.2)
    daj("gniazdo", 0.0, 0.0, 200, 1.5, 0.04)
    daj("drogowskaz", 140.0, -30.0, 285, 1.2)
    T.strefa = "las"
    siej("sosna_1", 5, LAS, 30, 100, (0.9, 1.1), strefa="las", zapas=2)
    siej("sosna_2", 3, LAS, 30, 100, (0.9, 1.1), strefa="las", zapas=2)
    for id in ("sosna_1", "sosna_2"):
        for j in range(13):
            b = random.Random(500 + j + (id == "sosna_2") * 50)
            kat = b.uniform(-140, 140)
            rr = b.uniform(118, 142)
            daj(id, LAS[0] + rr * math.sin(math.radians(kat)), LAS[1] + rr * math.cos(math.radians(kat)), b.uniform(0, 360),
                b.uniform(1.0, 1.3), 0.0, "las")
    siej("grzyb_wielki", 8, LAS, 20, 105, (0.8, 1.25), strefa="las", zapas=3)
    siej("grzyby_swiecace", 16, LAS, 0, 110, strefa="las")
    siej("luk_korzeni", 2, LAS, 40, 95, (0.9, 1.1), strefa="las", zapas=4)
    siej("filar_ruin", 3, (46.0, 214.0), 14, 22, strefa="las")
    # sosny między kotliną a lasem (zamykają świat) i wokół kaldery
    for j in range(12):
        b = random.Random(700 + j)
        daj(("sosna_1", "sosna_2")[j % 2], b.uniform(-185, -118), b.uniform(196, 300), b.uniform(0, 360), b.uniform(1.0, 1.3), 0.0, "wodospad")

    # obramowanie: poza sumą stref, ale blisko niej (7–40 studów) — sosny i drzewa liściaste, plus płaty koloru
    T.strefa = "obramowanie"
    b = random.Random(77)
    n = 0
    for _ in range(4000):
        if n >= 46:
            break
        x, z = b.uniform(-385, 265), b.uniform(-275, 375)
        d_ = _odl_strefy(x, z)
        if not (7.0 < d_ < 40.0) or any(math.hypot(x - a, z - c) < 11 for a, c, _ in zakazy[-80:]):
            continue
        if T.wierzch(x, z) > 0.1 or T.zajete(x, z):
            continue
        iglaste = math.hypot(x - LAS[0], z - LAS[1]) < 200 or x < -150
        daj(("sosna_1", "sosna_2")[n % 2] if iglaste else ("drzewo_1", "drzewo_2", "drzewo_3", "sosna_1")[n % 4], x, z, b.uniform(0, 360),
            b.uniform(1.0, 1.35), 0.0)
        zakazy.append((x, z, 6.0))
        n += 1
    for i in range(10):
        x, z = b.uniform(-380, 260), b.uniform(-270, 370)
        if _odl_strefy(x, z) > 25:
            plat(x, z, b.uniform(40, 80), ("397238", "417C3D", "3A7540", "447F3F")[i % 4], -0.05 + 0.002 * i)

    # ----------------------------------------------------------------------- legowiska (bez zmian: 12 miejsc, r 126)
    T.strefa = "legowiska"
    for x, z in LEGOWISKA:
        o = _obrot_ku(-x, -z)
        c, s_ = math.cos(math.radians(o)), math.sin(math.radians(o))
        for id, dx, dz, do in m1.SZABLON_LEGOWISKA:
            daj(id, x + dx * c - dz * s_, z - dx * s_ - dz * c, o + do, 1.0, 0.0, "legowiska")

    # kamienie runiczne (zestaw S14): stawiane na końcu, gdy cały teren już stoi
    RUNY.append(("R1", -84.0, -24.0, None, 75, "łąka — Bazaltowy Stół (rampa od północy)"))
    kamienie = []
    for r, x, z, y, o, gdzie in sorted(RUNY):
        T.strefa = {"R1": "laka", "R2": "polana", "R3": "wodospad", "R4": "las", "R5": "kanion", "R6": "kaldera"}[r]
        e = daj("kamien_runiczny", x, z, o, 1.0 if r != "R3" else 0.8, y)
        kamienie.append({"id": r, "x": round(x, 1), "y": e[4], "z": round(z, 1), "gdzie": gdzie})
    S["sekrety"].append({"id": "S14", "typ": "zestaw_run", "nazwa": "Sześć kamieni runicznych", "strefa": "caly_swiat", "stadia": [1, 8],
                         "zloto": 5000, "rekwizyt": "kamien_runiczny", "kamienie": kamienie,
                         "wymaga": "wszystkie 6 (od małego smoka po szybującego)",
                         "opis": "Każdy kamień gaśnie po dotknięciu i zapala gniazdo na pieczęci bramy. Komplet: 5000 złota i tytuł RUNE SEEKER."})
    return T, I, D, S, strefa_inst


# =========================================================================== strefy, kontrakt, liczenie
STREFY = [
    {"id": "laka", "nazwa": "MEADOW", "obszar": [{"kolo": [0, 0, 150]}], "stadia": [1, 3], "zagrozenie": 1,
     "opis": "Start i żłobek: boty 1–6 jak dziś, rzeka z mostami, Kwietny Pagór, Grzbiet Nory, czaszka.",
     "nastroj": {}},
    {"id": "polana", "nazwa": "HIDDEN GLADE", "obszar": [{"kolo": [148.2, 105.6, 18]}, {"pas": [134.3, 95.8, 10, 40, 54.5]}],
     "stadia": [1, 3], "zagrozenie": 0, "opis": "Kieszeń za murem tylko dla małych (B03).", "nastroj": {"ColorCorrection.TintColor": [240, 255, 236]}},
    {"id": "wodospad", "nazwa": "WATERFALL BASIN", "obszar": [{"kolo": [-164, 126, 46]}, {"kolo": [-170, 64, 30]}, {"pas": [-133.6, 94.8, 18, 44, 306.3]},
                                                              {"pas": [-132, 164, 22, 40, 90]}, {"prostokat": [-190, -150, 136, 172]}],
     "stadia": [1, 5], "zagrozenie": 2, "opis": "Kotlina pod urwiskiem: wodospad, jaskinia za wodą, gniazdo na półce.",
     "nastroj": {"Atmosphere.Density": 0.36, "Atmosphere.Color": [200, 230, 255], "Atmosphere.Haze": 2.2}},
    {"id": "las", "nazwa": "DEEP WOODS", "obszar": [{"kolo": [0, 240, 115]}], "stadia": [4, 6], "zagrozenie": 3,
     "opis": "Bez zmian w zasadach (otwarty od formy 4); dochodzi grota, paprocie, barykady do rozbicia.",
     "nastroj": {"Atmosphere.Density": 0.42, "Atmosphere.Color": [120, 150, 140], "Lighting.Brightness": 1.9}},
    {"id": "wyzyna", "nazwa": "WINDY HIGHLANDS", "obszar": [{"prostokat": [-330, -188, 52, 256]}], "stadia": [5, 7], "zagrozenie": 3,
     "opis": "Płaskowyż na 14 i wzgórze widokowe (20, 26). Wejście: rampa z kotliny, rampa z kanionu (za L01), prądy.",
     "nastroj": {"Atmosphere.Density": 0.22, "Atmosphere.Color": [220, 235, 255], "Atmosphere.Haze": 1.0, "ColorCorrection.Saturation": 0.15}},
    {"id": "kanion", "nazwa": "WIND CANYON", "obszar": [{"prostokat": [-268, -150, 10, 52]}, {"pas": [-284, -2, 40, 76, 34]}, {"prostokat": [-270, -166, -52, 10]},
                                                        {"pas": [-153, 27.5, 30, 16, 280.4]}],
     "stadia": [6, 8], "zagrozenie": 4, "opis": "Przełom 42 szerokości między ścianami 14–16: łuk skalny, grota za skałą, prądy.",
     "nastroj": {"Atmosphere.Density": 0.32, "Atmosphere.Color": [255, 196, 140], "Atmosphere.Decay": [150, 90, 80]}},
    {"id": "kaldera", "nazwa": "LAVA CALDERA", "obszar": [{"kolo": [-318, -96, 66]}], "stadia": [7, 8], "zagrozenie": 5,
     "opis": "Popielny brzeg wokół jeziora lawy; SKY NEST pośrodku (tylko szybowanie, fosa 28 < 34).",
     "nastroj": {"Atmosphere.Density": 0.38, "Atmosphere.Color": [255, 130, 80], "Bloom.Intensity": 0.6}},
    {"id": "szlak_popiolu", "nazwa": "ASH TRAIL", "obszar": [{"pas": [-187, -102, 22, 156, 90]}], "stadia": [6, 8], "zagrozenie": 4,
     "opis": "Korytarz z wyłomu w murze (L06) do wschodniego wejścia kaldery.", "nastroj": {"Atmosphere.Color": [235, 160, 120]}},
    {"id": "jezioro", "nazwa": "LILY LAKE", "obszar": [{"kolo": [8, -214, 46]}, {"pas": [1, -165, 22, 30, 0]}], "stadia": [1, 8],
     "zagrozenie": 0, "opis": "Spokojne jezioro za murem; bród na wysepkę ze skrzynią.", "nastroj": {"Atmosphere.Haze": 2.0}},
    {"id": "brama", "nazwa": "SEALED GATE", "obszar": [{"pas": [181.7, -48.9, 30, 96, 105.7]}], "stadia": [1, 8], "zagrozenie": 1,
     "opis": "Wąwóz z ruinami do zapieczętowanej bramy (zapowiedź aktualizacji).",
     "nastroj": {"Atmosphere.Color": [220, 170, 255], "Atmosphere.Decay": [90, 60, 160], "Atmosphere.Density": 0.34}},
    {"id": "przyszla_kraina", "nazwa": "???", "obszar": [{"prostokat": [240, 440, -180, 60]}], "stadia": None, "zagrozenie": None,
     "opis": "Zarezerwowane na aktualizację: za bramą nic nie stoi, mapa i budżet części czekają.", "nastroj": {}},
    {"id": "punkt_widokowy", "nazwa": "LOOKOUT", "obszar": [{"prostokat": [-284, -264, 198, 216]}], "stadia": [1, 8], "zagrozenie": 3,
     "opis": "Strefa kamery: na szczycie kamera odjeżdża i patrzy na łąkę.",
     "kamera": {"nachylenie_st": 30, "odl_x": 1.8, "patrz_na": [0, 60], "czas_s": 1.2}, "nastroj": {}},
]

KOLIZJE_NOWE = {   # koła blokujące w układzie rekwizytu (x, z, r) — przód −Z rigu, jak w swiat_mapa.KOLA
    "skala_lamliwa": [(0, 0, 4.2)], "drzewo_martwe": [(0, 0, 1.3)],
    "kloda_martwa": [(-5.0, 0, 1.6), (-1.6, 0, 1.6), (1.8, 0, 1.6), (5.2, 0, 1.6)],
    "luk_niski": [(-4.6, 0, 1.4), (4.6, 0, 1.4)], "nora": [(-3.6, 1.2, 2.6), (3.6, 1.2, 2.6), (0, 2.6, 2.6)],
    "kamien_runiczny": [(0, 0, 1.4)], "krysztaly_skupisko": [(0, 0, 2.4)], "grota_wejscie": [(-6.6, 0, 2.4), (6.6, 0, 2.4)],
    "wodospad": [(-6.6, -2.6, 1.6), (6.6, -2.6, 1.6)], "luk_skalny": [(-14.0, 0, 3.4), (14.0, 0, 3.4)],
    "iglica_skalna": [(0, 0, 3.6)], "ruiny_mur": [(-3.0, 0, 1.2), (0, 0, 1.2), (3.0, 0, 1.2)], "punkt_widokowy": [(0, 0, 2.8)],
    "czaszka_wielka": [(0, 5.0, 8.6), (0, 15.0, 3.5), (0, 21.0, 2.8), (0, 26.4, 2.2), (-5.6, -3.0, 1.6), (-5.6, -9.0, 1.6),
                       (-5.6, -14.0, 1.4), (5.6, -3.0, 1.6), (5.6, -9.0, 1.6), (5.6, -14.0, 1.4)],
    "gniazdo_orle": [(0, 0, 2.2)],
}
BEZ_KOLIZJI = sorted({"trawa_1", "trawa_2", "kwiat_czerwony", "kwiat_zolty", "kwiat_niebieski", "kwiat_bialy", "kamyk", "krzak", "grzyb",
                      "lilia", "trzcina", "grzyby_swiecace", "drogowskaz", "sztandar", "trawa_wysoka", "paproc", "wiatr_kolumna",
                      "kamien_brodu", "szczelina_lawy", "latarnia_las", "latarnia_zar", "latarnia_magia", "latarnia_zlota",
                      "skrzynia_ukryta", "most", "gniazdo"})
INTERAKTYWNE = ("skrzynia_ukryta", "kamien_runiczny", "gniazdo_orle", "punkt_widokowy", "wiatr_kolumna", "skala_lamliwa",
                "drzewo_martwe", "kloda_martwa")

KONTRAKT = {
    "wysokosc": "Ziemia pod środkiem smoka: h(x, z, y) = max(0, wierzchy brył `teren` z chodzi=true, których obrys zawiera (x, z) "
                "i których spód ≤ y + krok). Blok: wierzch = p.y + s.y/2. Klin (WedgePart): wierzch rośnie liniowo od p.y − s.y/2 "
                "na lokalnym −Z do p.y + s.y/2 na lokalnym +Z (lokalne z = (x−px)·sin o + (z−pz)·cos o). Walec: koło średnicy s.x. "
                "Bryły ze spodem wyżej niż y + krok są nad głową (dach tunelu, grota) i nie liczą się.",
    "ruch": "Ruch do punktu jest zablokowany, gdy h − y > krok (urwisko), gdy bryła chodzi=false i bez `ozdoba` ma wierzch > y + krok "
            "i spód ≤ y + krok (skała), gdy punkt leży na `glebia`/`lawa`, nad którymi nie ma wyższej bryły do chodzenia (most, bród), "
            "albo poza sumą obszarów `strefy`. Zejście w dół wolno zawsze (spadek bez obrażeń) — uskoki to ucieczki w jedną stronę.",
    "woda": "`woda`=true: płytka woda, prędkość × 0,7 (boty też); `glebia`=true: nie wejdziesz. Lawa: jak głębia, plus kontakt w "
            "szybowaniu nad nią nic nie robi.",
    "kamera": "Cel kamery na (x, h, z) z wygładzeniem ok. 0,15 s. Części `przenikalny`=true (dachy tuneli i grot) między kamerą a własnym "
              "smokiem — LocalTransparencyModifier 0,65. Strefa `punkt_widokowy` ma własne `kamera` (nachylenie 30°, odległość × 1,8, "
              "patrzy na łąkę).",
    "bramy_rozmiaru": "Prostokąt (x, z, szer, dl, o) jest przeszkodą dla smoka, którego promień > r_maks: mała 3,0 (stadia 1–3), "
                      "średnia 5,2 (stadia 1–5). Boty też. Komunikat przy odbiciu: „TOO BIG!”.",
    "lamliwe": "Do rozbicia od stadium 6: BITE i zdolności zadają rany jak stworkowi bez mnożnika rozmiaru (TAIL, METEOR × 2). "
               "Po zerze: rozsypka, `kola` przestają blokować, złoto `zloto` dla rozbijającego; odrost po `odrost_s` (smok w środku "
               "zostaje wypchnięty). Mniejsze stadia: odbicie i napis „STAGE 6 TO SMASH”.",
    "kryjowki": "Środek smoka w kole (x, z, r) i promień smoka ≤ r_maks_smoka: nazwa nad głową znika dla innych, boty, które nie "
                "są bliżej niż 8 studów, gubią cel i nie wybierają go na nowy; atak albo zdolność odkrywa na 1,5 s.",
    "wiatry": "Prąd wznoszący (od stadium 5, WING GLIDE): środek w kole (x, z, r) podczas szybowania — wysokość lotu rośnie do y_cel "
              "w wznoszenie_s, pozostały zasięg = d × zasieg_x (raz na szybowanie). Stojąc w prądzie, POWER startuje szybowanie od razu "
              "z y_cel. Szybowanie przelatuje nad wszystkim niższym niż bieżąca wysokość lotu i ląduje na h(x, z).",
    "sekrety": "Skrzynia/gniazdo/punkt widokowy: dotknięcie = złoto `zloto`, raz na gracza na dzień UTC (pętla dzienna). Kamienie "
               "runiczne: raz na zawsze; komplet 6 = 5000 złota + tytuł. `stadia` = dla kogo projektowane (nie blokada).",
    "strefy": "Obszar gry = suma kształtów `obszar` (kolo [x, z, r], prostokat [x0, x1, z0, z1], pas [x, z, szer, dl, o]). "
              "`stadia` i `zagrozenie` (0–5) to zalecenie dla botów i tablic, nie blokada (las nadal od formy 4 jak dziś).",
}


def _do_szkicu(T, I, D, S, plik):
    """Szybki szkic z góry (PIL, bez Blendera): wysokości terenu, woda, lawa, rekwizyty, znaczniki."""
    from PIL import Image, ImageDraw, ImageFont
    X0, X1, Z0, Z1, sk = -380.0, 270.0, -270.0, 370.0, 2.0
    W, H = int((X1 - X0) * sk), int((Z1 - Z0) * sk)
    im = Image.new("RGB", (W, H), (40, 90, 50))
    d = ImageDraw.Draw(im)

    def P(x, z):                                               # ekran gry: −X w prawo, +Z w górę
        return (X1 - x) * sk, (Z1 - z) * sk

    for x, z, r, k, y, sw in D:
        a, b = P(x - r, z + r), P(x + r, z - r)
        d.ellipse((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])), fill="#" + k)
    for b in sorted(T.bryly, key=lambda b: b["p"][1] + b["s"][1] / 2):
        if b.get("widoczny") is False:
            continue
        cx, cy, cz = b["p"]
        sx, sy, sz_ = b["s"]
        if b["k"] == "walec":
            a1, a2 = P(cx - sx / 2, cz + sx / 2), P(cx + sx / 2, cz - sx / 2)
            d.ellipse((min(a1[0], a2[0]), min(a1[1], a2[1]), max(a1[0], a2[0]), max(a1[1], a2[1])), fill="#" + b["kolor"])
            continue
        o = math.radians(b["o"])
        ex, ez = (math.cos(o), -math.sin(o)), (math.sin(o), math.cos(o))
        rogi = [P(cx + ex[0] * u * sx / 2 + ez[0] * v * sz_ / 2, cz + ex[1] * u * sx / 2 + ez[1] * v * sz_ / 2)
                for u, v in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        d.polygon(rogi, fill="#" + b["kolor"], outline=(20, 16, 28) if not b.get("ozdoba") else None)
    for id, lista in I.items():
        for x, z, o, s_, y in lista:
            q = P(x, z)
            r = 1.2 if id.startswith(("trawa_", "kwiat", "kamyk", "grzyb")) else 2.4
            d.ellipse((q[0] - r, q[1] - r, q[0] + r, q[1] + r), fill=(250, 250, 240) if y > 0.5 else (30, 30, 30))
    f = ImageFont.truetype("arialbd.ttf", 18)
    for e in S["sekrety"]:
        if "x" in e:
            q = P(e["x"], e["z"])
            d.text((q[0] + 4, q[1] - 10), e["id"], fill=(255, 230, 80), font=f, stroke_width=3, stroke_fill=(0, 0, 0))
    for e in S["bramy_rozmiaru"]:
        q = P(e["x"], e["z"])
        d.text((q[0] + 4, q[1] + 2), e["id"], fill=(255, 255, 255), font=f, stroke_width=3, stroke_fill=(0, 0, 0))
    for e in S["lamliwe"]:
        q = P(e["x"], e["z"])
        d.text((q[0] + 4, q[1] + 2), e["id"], fill=(255, 140, 60), font=f, stroke_width=3, stroke_fill=(0, 0, 0))
    for e in S["wiatry"]:
        q = P(e["x"], e["z"])
        d.text((q[0] + 4, q[1] + 2), e["id"], fill=(160, 240, 255), font=f, stroke_width=3, stroke_fill=(0, 0, 0))
    im.save(plik)
    return plik


# =========================================================================== zapis danych, szkic, rendery
MAT_ROBLOX = {"matowy": "SmoothPlastic", "szklo": "Glass", "swiecacy": "Neon"}
MAT_BIB = {"matowy": "matowy", "szklo": "polysk", "swiecacy": "swiecacy"}
KSZTALT = {"blok": 0, "walec": 2, "klin": 3}


def czesci_rekwizytow():
    """{id: części Roblox} starego zestawu (swiat_zestaw) i nowego (swiat_zestaw2) + modele (do renderu)."""
    from swiat.ewolucja.modele import rekwizyty
    modele = {m.id: m for m, _, _ in sz.wszystkie()}
    modele["gniazdo"] = rekwizyty.gniazdo()                  # gniazdo z jajami na placu startu (rig w dane/)
    nowe = {m.id: m for m, _, _ in sz2.wszystkie()}
    czesci = {i: sm.liczba_czesci_roblox(m) for i, m in list(modele.items()) + list(nowe.items())}
    return czesci, modele, nowe


def policz(T, I, D, si, czesci):
    """Części statyczne na strefę (teren + rekwizyty), płaty ziemi osobno."""
    wyn = {}
    for b in T.bryly:
        if b.get("widoczny") is False:
            continue
        wyn.setdefault(b["strefa"], {"teren": 0, "rekwizyty": 0})["teren"] += 1
    for id, lista in I.items():
        for n in range(len(lista)):
            wyn.setdefault(si[(id, n)], {"teren": 0, "rekwizyty": 0})["rekwizyty"] += czesci[id]
    wyn["platy_ziemi"] = {"teren": len(D), "rekwizyty": 0}
    razem = sum(v["teren"] + v["rekwizyty"] for v in wyn.values())
    return wyn, razem


def kontrola(T):
    """Punkty kontrolne wysokości dla gry: [x, z, y smoka, h, zablokowane, woda, lawa] — test zgodności z kontraktem."""
    pkt = [(0, 0, 0), (74, -38, 0), (74, -38, 5.0), (52, -32, 2.0), (-82, -22, 0), (-82, -22, 6.0), (-262, 172, 16.0),
           (-274, 207, 26.0), (-260, 90, 0.0), (-260, 90, 14.0), (-174, 176, 7.0), (58, 24, 0.0), (58, 24, 7.0), (-200, 124, 0.0),
           (-197, 124, 14.0), (-36, -2, 0.24), (-37, -2, 0.0), (-172, 124, 0.0), (8, -200, 0.3), (8, -230, 0.0), (-318, -96, 1.3),
           (-318, -130, 0.0), (-246, 62, 0.0), (-246, 62, 14.0), (-180, 48, 5.5), (-206, -20, 16.0), (-205, 0, 0.0)]
    wyn = []
    for x, z, y in pkt:
        h, blok, woda, lawa = T.wysokosc(x, z, y)
        wyn.append([x, z, y, round(h, 2), blok, woda, lawa])
    return wyn


SCIEZKI = [   # (nazwa, punkty, czy ma przejść) — przejście pieszo po zasadach kontraktu (bez kolizji rekwizytów i bram)
    ("rampa Kwietnego Pagóra", [(40, -28), (60, -35), (74, -38)], True),
    ("uskok pagóra pod górę (bez rampy)", [(96, -60), (80, -44)], False),
    ("rampa Bazaltowego Stołu (od północy)", [(-88, 2), (-82, -22)], True),
    ("rampa z kotliny na ostrogę i dalej na wyżynę", [(-130, 150), (-118, 164), (-170, 160), (-260, 150)], True),
    ("wzgórze widokowe: dwie rampy na szczyt 26", [(-262, 158), (-262, 190), (-250, 207), (-274, 207)], True),
    ("wyżyna 14 → stopień północny 18", [(-214, 176), (-214, 210)], True),
    ("z dna kanionu w północną ścianę", [(-230, 30), (-230, 70)], False),
    ("rampa z kanionu na wyżynę (gdy L01 rozbite)", [(-160, 48), (-200, 48), (-200, 64)], True),
    ("tunel Grzbietu Nory (dalej decyduje brama B02)", [(40, 24), (80, 24)], True),
    ("przez Grzbiet Nory obok tunelu", [(40, 10), (80, 10)], False),
    ("Most Startowy", [(-15, -2), (-60, -4)], True),
    ("bród na wysepkę jeziora", [(36, -186), (12, -221)], True),
    ("przez głębokie jezioro obok brodu", [(-14, -186), (-14, -232)], False),
    ("ścieżka za wodospadem do jaskini", [(-146, 131), (-168, 131), (-168, 146)], True),
    ("pieszo na SKY NEST", [(-318, -36), (-318, -96)], False),
    ("rampa półki startowej kaldery", [(-318, -40), (-327, -36.5), (-346, -47.5)], True),
    ("łąka → kanion → kaldera (północne wejście)", [(-120, 22), (-200, 30), (-262, 30), (-300, -26), (-310, -50)], True),
    ("łąka → wyłom L06 → Szlak Popiołu → kaldera", [(-96, -80), (-121, -101), (-262, -102), (-268, -124)], True),
    ("łąka → brama E → zapieczętowana brama", [(120, -32), (150, -40), (214, -58)], True),
    ("łąka → nora B03 → Ukryta Polana", [(110, 80), (128.6, 91.7), (148, 106)], True),
    ("łąka → brama S → brzeg jeziora", [(0, -120), (0, -160), (30, -182)], True),
    ("łąka → przerwa NW → kotlina wodospadu", [(-100, 60), (-130, 96), (-150, 110)], True),
]


def idz(T, pkt, krok=0.5):
    """Pieszo od punktu do punktu po zasadach kontraktu: (doszedł, x, z, y w miejscu zatrzymania)."""
    x, z = pkt[0]
    y = T.wysokosc(x, z, 0.0)[0]
    for (ax, az), (bx, bz) in zip(pkt, pkt[1:]):
        n = max(1, int(math.hypot(bx - ax, bz - az) / krok))
        for i in range(1, n + 1):
            nx_, nz_ = ax + (bx - ax) * i / n, az + (bz - az) * i / n
            h, blok, _, _ = T.wysokosc(nx_, nz_, y)
            if blok or _odl_strefy(nx_, nz_) > 0:
                return False, x, z, y
            x, z, y = nx_, nz_, h
    return True, x, z, y


def sprawdz_sciezki(T):
    wyn = []
    for nazwa, pkt, ma in SCIEZKI:
        ok, x, z, y = idz(T, pkt)
        wyn.append({"nazwa": nazwa, "punkty": [list(p) for p in pkt], "przechodzi": ma, "wynik": ok, "koniec": [round(x, 1), round(z, 1), round(y, 2)]})
    return wyn


def dane_json(T, I, D, S, si, czesci, nowe):
    strefy_cz, razem = policz(T, I, D, si, czesci)
    teren = []
    for b in T.bryly:
        e = dict(b)
        e["ksztalt"] = KSZTALT[b["k"]]
        e["material"] = MAT_ROBLOX[b["mat"]]
        e.pop("mat")
        teren.append(e)
    return {
        "format": "smok-ewolucji-mapa/2",
        "status": "propozycja (runda 7, 23.11.2026) — nic z tego nie jest wpięte w grę; dane/mapa_propozycja.json bez zmian",
        "uklad": "gra: środek łąki = (0, 0), DEEP WOODS w +Z, studs; obrót o w stopniach = CFrame.Angles(0, rad(o), 0) "
                 "(lokalne +Z → (sin o, cos o)); na ekranie gry +Z u góry, −X po prawej",
        "nadzbior": "Klucze z mapa_propozycja.json (strefy.laka_r/las/wyspa_lawy/jezioro_r/stawy, szablon_legowiska, platy_ziemi, "
                    "instancje, czesci_*) mają ten sam układ; instancja ma piąty element y (wysokość podstawy, domyślnie 0).",
        "parametry": {"krok": KROK, "poziomy": WYS, "woda_v_x": 0.7, "kamera": KAM, "promienie_stadiow": PROMIEN},
        "kontrakt": KONTRAKT,
        "strefy": {"laka_r": LAKA_R, "las": list(LAS) + [LAS_R], "wyspa_lawy": list(KALDERA) + [WYSPA_R], "jezioro_r": JEZIORO_R,
                   "stawy": [[STAWEK[0], STAWEK[1], STAWEK[2]], [JEZIORO[0], JEZIORO[1], JEZIORO_R]], "lista": STREFY},
        "wyspa": {"nazwa": "SKY NEST", "x": KALDERA[0], "z": KALDERA[1], "r_wew": WYSPA_R, "r_zew": LAWA_R,
                  "uwaga": "Nowe miejsce wyspy (dziś w grze: −36, −42, r 12/21 na łące). Fosa 28 < WING GLIDE 34."},
        "teren": teren,
        "kontrola_wysokosci": {"opis": "[x, z, y smoka, h oczekiwane, zablokowane, woda, lawa]", "punkty": kontrola(T)},
        "sciezki_kontrolne": {"opis": "Przejście pieszo krokiem 0,5 studa po zasadach kontraktu (bez rekwizytów i bram); "
                                      "`przechodzi` = zamiar projektu, `wynik` = co wyszło", "lista": sprawdz_sciezki(T)},
        "sekrety": S["sekrety"], "bramy_rozmiaru": S["bramy_rozmiaru"], "kryjowki": S["kryjowki"], "lamliwe": S["lamliwe"],
        "wiatry": S["wiatry"], "linie_latarni": S["linie_latarni"],
        "spawn": {"x": 0, "z": 0, "r": 17, "punkty": [[round(9 * math.sin(math.radians(45 * i)), 1), round(9 * math.cos(math.radians(45 * i)), 1)]
                                                      for i in range(8)],
                  "opis": "Plac startu jak dziś; z placu wychodzą cztery linie latarni (osie widoku) do lasu, kanionu, wodospadu i bramy."},
        "punkty_gry": {"ranking": [22.0, -58.0], "rampage_start": [0.0, 55.0],
                       "owce_stada": [[30.0, 52.0], [62.0, -8.0], [-74.0, 34.0], [26.0, -96.0]],
                       "uwaga": "Ranking (−18, −96) i stado (−20, 35) z ustawień stoją w nurcie rzeki lub tuż przy niej — tu nowe miejsca."},
        "szablon_legowiska": [list(x) for x in m1.SZABLON_LEGOWISKA],
        "legowiska": [[round(x, 1), round(z, 1), round(_obrot_ku(-x, -z) % 360, 1)] for x, z in LEGOWISKA],
        "kolizje_rekwizytow": {k: [list(c) for c in v] for k, v in KOLIZJE_NOWE.items()},
        "kolizje_stare": "swiat/ewolucja/swiat_mapa.py → KOLA (bez zmian dla starych rekwizytów)",
        "bez_kolizji": BEZ_KOLIZJI,
        "interaktywne": list(INTERAKTYWNE),
        "rekwizyty_nowe": [{"id": i, "plik": "rekwizyt_%s_rig.json" % i, "czesci": czesci[i]} for i in nowe],
        "czesci_rekwizytu": {k: czesci[k] for k in sorted(I)},
        "czesci_stref": strefy_cz, "czesci_razem": razem,
        "platy_ziemi": D,
        "instancje": {i: v for i, v in sorted(I.items())},
    }, strefy_cz, razem


def model_terenu(T, id, przenikalne):
    """Teren jako jeden statyczny model biblioteki (do renderu): bryły w układzie biblioteki (x, z) -> (−x, −z),
    obrót o + 180 (część zdefiniowana w układzie Roblox, patrz README)."""
    p = sz._nowy(id, "Teren mapy v2", faza=0.0)
    for b in T.bryly:
        if b.get("widoczny") is False or bool(b.get("przenikalny")) != przenikalne:
            continue
        x, y, z = b["p"]
        sx, sy, sz_ = b["s"]
        f = min(0.9, 0.1 * min(sx, sz_), 0.3 * sy)
        if b["k"] == "walec":
            p.walec(b["id"], (-x, y, -z), (sx, sy, sz_), b["kolor"], MAT_BIB[b["mat"]], segm=24, faza=min(f, 0.3))
        elif b["k"] == "klin":
            p.klin(b["id"], (-x, y, -z), (sx, sy, sz_), b["kolor"], MAT_BIB[b["mat"]], rot=(0, b["o"] + 180, 0), faza=0.15)
        else:
            p.blok(b["id"], (-x, y, -z), (sx, sy, sz_), b["kolor"], MAT_BIB[b["mat"]], rot=(0, b["o"] + 180, 0), faza=f)
    return p


def zrob(g, *opcje):
    """g = moduł generuj. Zapisuje dane_nastepne/mapa_v2.json i rigi nowych rekwizytów, szkic i rendery."""
    cel_dane = os.path.join(g.TU, "dane_nastepne")
    os.makedirs(cel_dane, exist_ok=True)
    rob, cel = g.wyjscie("mapa2_robocze"), g.wyjscie("mapa")
    czesci, stare, nowe = czesci_rekwizytow()
    for i, m in nowe.items():
        g._zapisz(g.rig_modelu(m), os.path.join(cel_dane, "rekwizyt_%s_rig.json" % i))
    T, I, D, S, si = zbuduj()
    dane, strefy_cz, razem = dane_json(T, I, D, S, si, czesci, nowe)
    rozm = g._zapisz(dane, os.path.join(cel_dane, "mapa_v2.json"))
    print("MAPA2 | części statycznych razem %d (teren %d, płaty %d); %d kB" % (
        razem, sum(1 for b in T.bryly if b.get("widoczny") is not False), len(D), rozm // 1024))
    for k, v in sorted(strefy_cz.items(), key=lambda kv: -(kv[1]["teren"] + kv[1]["rekwizyty"])):
        print("   %-16s %5d  (teren %3d, rekwizyty %4d)" % (k, v["teren"] + v["rekwizyty"], v["teren"], v["rekwizyty"]))
    for x, z, y, h, blok, woda, lawa in dane["kontrola_wysokosci"]["punkty"]:
        print("   wysokość (%7.1f, %7.1f) y=%5.1f -> h=%5.2f%s%s%s" % (x, z, y, h, " BLOKADA" if blok else "", " woda" if woda else "",
                                                                  " lawa" if lawa else ""))
    for e in dane["sciezki_kontrolne"]["lista"]:
        print("   ścieżka %-48s %s%s" % (e["nazwa"], "przechodzi" if e["wynik"] else "zablokowana",
                                       "" if e["wynik"] == e["przechodzi"] else "   <-- NIE TAK MIAŁO BYĆ (koniec %s)" % e["koniec"]))
    _do_szkicu(T, I, D, S, os.path.join(cel, "mapa2_szkic.png"))
    if "szkic" in opcje:
        return dane
    renderuj(g, T, I, D, S, stare, nowe, rob, cel, [o for o in opcje if o != "szkic"])
    return dane


# --------------------------------------------------------------------------- rendery (Blender)
def _aktor(smoki, nr, x, z, kier, klip, u, T, y=None, sk=1.0):
    m = smoki[nr]
    k = next(c for c in m.klipy if c.nazwa == klip)
    if y is None:
        y = T.wierzch(x, z)
    return {"id": m.id, "poz": [-x, y, -z], "obrot_y": _obrot_ku(*kier), "poza": [klip, int(k.dlugosc * u)], "skala": sk}


def renderuj(g, T, I, D, S, stare, nowe, rob, cel, tylko=()):
    from PIL import Image
    from swiat.ewolucja.modele import stwory
    smoki = {int(m.id.split("_")[1]): m for m in g.modele_pelne([1, 2, 3, 4, 5, 6, 7], jajo=False)}
    owca = stwory.owca()
    teren = model_terenu(T, "teren_v2", False)
    dachy = model_terenu(T, "teren_v2_dachy", True)
    uzyte = {i for i in I} | {"kula_mala", "kula_duza", "kula_wielka", "stos_zlota_2"}
    rekw = [m for i, m in list(stare.items()) + list(nowe.items()) if i in uzyte]

    # życie: kule, owce, złoto w legowiskach
    los = random.Random(11)
    zycie = {"kula_mala": [], "kula_duza": [], "kula_wielka": [], "stos_zlota_2": []}
    for id, n, r0, r1 in (("kula_mala", 90, 18, 140), ("kula_duza", 14, 20, 140)):
        while n > 0:
            a, rr = los.uniform(0, 6.283), math.sqrt(los.uniform(r0 * r0, r1 * r1))
            x, z = rr * math.sin(a), rr * math.cos(a)
            if T.zajete(x, z) or _blisko_rzeki(x, z, 2):
                continue
            zycie[id].append([x, z, 0, 1.0, T.wierzch(x, z)])
            n -= 1
    for i in range(8):
        a = i * 0.8
        zycie["kula_wielka"].append([KALDERA[0] + 9 * math.sin(a), KALDERA[1] + 9 * math.cos(a), 0, 1.0, 1.3])
    for x, z in LEGOWISKA[::3]:
        zycie["stos_zlota_2"].append([x * 0.97, z * 0.97, _obrot_ku(-x, -z), 0.8, 0.0])
    owce = []
    for sx_, sz_ in ((30.0, 52.0), (62.0, -8.0), (-74.0, 34.0), (26.0, -96.0)):
        for k in range(3):
            owce.append({"id": "owca", "poz": [-(sx_ + 3 * k), 0.0, -(sz_ + 2 * (k % 2))], "obrot_y": 60 * k, "poza": ["chod", 4 * k]})

    def inst(slownik):
        return [{"id": i, "m": [[-x, y, -z, o, sk] for x, z, o, sk, y in v]} for i, v in slownik.items() if v]

    wsp = {"instancje": inst(I) + inst(zycie), "dyski": [{"x": -x, "z": -z, "r": r, "kolor": k, "y": y, "swieci": sw}
                                                         for x, z, r, k, y, sw in D]}
    baza = [{"id": "teren_v2", "poz": [0, 0, 0]}, {"id": "teren_v2_dachy", "poz": [0, 0, 0]}] + owce

    def gra(nr, x, z):
        d = KAM["wys"] + PROMIEN[nr - 1] * KAM["na_r"]
        return {"typ": "gra", "cel": [-x, T.wierzch(x, z), -z], "odl": d, "nachylenie": KAM["nachylenie"], "fov": KAM["fov"]}

    W, H = 1920, 888                                             # telefon poziomo (2,16 : 1)
    zad = [
        dict(wsp, typ="scena2", plik="mapa2_z_gory.png", rozmiar=[2000, 1940], kamera={"typ": "orto", "srodek": [55.0, -50.0],
                                                                                         "szer": 660.0},
             modele=baza + [_aktor(smoki, 7, -230, 30, (1, 0), "chod", 0.3, T), _aktor(smoki, 5, 20, 60, (0, -1), "bieg", 0.4, T)]),
        dict(wsp, typ="scena2", plik="mapa2_spawn.png", rozmiar=[W, H], kamera=gra(1, -4, 4),
             modele=baza + [_aktor(smoki, 1, -4, 4, (-1, 0.15), "bieg", 0.25, T), _aktor(smoki, 1, 8, -8, (0.3, 1), "chod", 0.5, T),
                            _aktor(smoki, 2, 18, 18, (-1, -0.4), "bieg", 0.6, T), _aktor(smoki, 3, -14, -18, (1, 0.2), "chod", 0.1, T),
                            _aktor(smoki, 1, 22, 28, (0, 1), "spoczynek", 0.3, T)]),
        dict(wsp, typ="scena2", plik="mapa2_nora.png", rozmiar=[W, H], kamera=gra(1, 58, 24), alfa={"teren_v2_dachy": 0.28},
             modele=baza + [_aktor(smoki, 1, 59.5, 22.5, (1, 0.05), "bieg", 0.5, T, y=0.0),
                            _aktor(smoki, 4, 43, 27, (1, -0.1), "gryz3", 0.45, T), _aktor(smoki, 2, 72, 30, (1, 0.4), "bieg", 0.2, T)]),
        dict(wsp, typ="scena2", plik="mapa2_punkt_widokowy.png", rozmiar=[W, H],
             kamera={"typ": "panorama", "cel": [274.0, 26.0, -207.0], "patrz_na": [0.0, 0.0, -40.0],
                     "odl": (KAM["wys"] + PROMIEN[6] * KAM["na_r"]) * 1.8, "nachylenie": 30.0, "fov": 50.0},
             modele=baza + [_aktor(smoki, 7, -274, 205, (1, -0.4), "ryk", 0.5, T)]),
        dict(wsp, typ="scena2", plik="mapa2_kanion.png", rozmiar=[W, H], kamera=gra(7, -206, 30),
             modele=baza + [_aktor(smoki, 7, -206, 30, (-1, 0.05), "chod", 0.2, T), _aktor(smoki, 6, -177, 44, (-1, 0.3), "gryz3", 0.5, T),
                            _aktor(smoki, 5, -226, 44, (-0.6, 0.6), "szybowanie_petla", 0.3, T, y=9.0),
                            _aktor(smoki, 6, -240, 20, (1, 0.2), "bieg", 0.6, T)]),
    ]
    zad += [
        dict(wsp, typ="scena2", plik="mapa2_wodospad.png", rozmiar=[W, H], kamera=gra(3, -180, 118),
             modele=baza + [_aktor(smoki, 3, -184, 112, (0, 1), "chod", 0.3, T), _aktor(smoki, 2, -165, 104, (-1, 0.2), "bieg", 0.4, T),
                            _aktor(smoki, 5, -176, 152, (-1, 0), "szybowanie_petla", 0.5, T, y=8.0)]),
        dict(wsp, typ="scena2", plik="mapa2_kaldera.png", rozmiar=[W, H], kamera=gra(7, -322, -84),
             modele=baza + [_aktor(smoki, 7, -340, -52, (0.4, -1), "chod", 0.4, T), _aktor(smoki, 5, -326, -76, (0.2, -1), "szybowanie_petla", 0.4, T, y=10.0),
                            _aktor(smoki, 6, -300, -136, (-1, 0.5), "bieg", 0.3, T)]),
    ]
    if tylko:
        zad = [z for z in zad if any(t in z["plik"] for t in tylko)]
    modele = [teren, dachy, owca] + rekw + list(smoki.values())
    _widoki(g, modele, zad, rob, "mapa v2: %d widoków" % len(zad))
    opisy = {"mapa2_spawn.png": "Kamera gry: HATCHLING na placu startu (telefon 2,16 : 1)",
             "mapa2_nora.png": "Kamera gry w tunelu Grzbietu Nory (dach wygaszony; FIRE DRAKE nie wejdzie)",
             "mapa2_punkt_widokowy.png": "Panorama z punktu widokowego (kamera strefy: 30°, odległość × 1,8, patrzy na łąkę)",
             "mapa2_kanion.png": "Kamera gry: ELDER DRAGON w Kanionie Wichrów (łuk skalny, osypisko L01, prądy W01 i W05)"}
    for src in ("mapa2_wodospad.png", "mapa2_kaldera.png"):
        if any(z["plik"] == src for z in zad):
            _podpis(g, Image.open(os.path.join(rob, src)).convert("RGB"), {"mapa2_wodospad.png": "Kamera gry: DRAKE w kotlinie wodospadu",
                                                                         "mapa2_kaldera.png": "Kamera gry: ELDER DRAGON nad kalderą"}[src]
                    ).save(os.path.join(cel, src))
    for src, jpg, roz in (("mapa2_z_gory.png", "27_mapa2_z_gory.jpg", (1000, 970)), ("mapa2_spawn.png", "28_mapa2_spawn.jpg", (1280, 592)),
                          ("mapa2_nora.png", "29_mapa2_nora.jpg", (1280, 592)),
                          ("mapa2_punkt_widokowy.png", "30_mapa2_punkt_widokowy.jpg", (1280, 592)),
                          ("mapa2_kanion.png", "31_mapa2_kanion.jpg", (1280, 592))):
        if not any(z["plik"] == src for z in zad):
            continue
        im = Image.open(os.path.join(rob, src)).convert("RGB")
        im = _opisz_gore(g, im, S) if src == "mapa2_z_gory.png" else _podpis(g, im, opisy[src])
        im.save(os.path.join(cel, src))
        im.resize(roz, Image.LANCZOS).save(os.path.join(g.PODGLAD, jpg), quality=82, optimize=True)
        print("MAPA2 | %s -> podglad/%s" % (src, jpg))


def _widoki(g, modele, zadania, folder, opis):
    """Jak generuj.widoki, ale skryptem blender_mapa2.py (teren, wysokości instancji, kamera gry)."""
    from swiat.postacie.biblioteka.postac import pakiet, zapisz_json
    for m in modele:
        for x in m.sprawdz()[0]:
            raise SystemExit("BŁĄD danych: " + x)
    pj, zj = os.path.join(folder, "_pakiet.json"), os.path.join(folder, "_zadania.json")
    zapisz_json(pakiet(modele), pj)
    with open(zj, "w", encoding="utf-8") as f:
        json.dump(zadania, f)
    g.blender(os.path.join(g.TU, "blender_mapa2.py"), [pj, zj, folder], opis, limit_s=40 * 60)


def _podpis(g, im, tekst):
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    d.text((24, 18), tekst, fill=(255, 255, 255), font=g._czcionka(30, True), stroke_width=4, stroke_fill=(20, 16, 28))
    return im


def _opisz_gore(g, im, S):
    """Napisy stref i znaczniki sekretów (S), kamieni (R), bram (B), rzeczy do rozbicia (L) i prądów (W)."""
    from PIL import ImageDraw
    W, H = im.size
    sk = W / 660.0
    cx, cz = -55.0, 50.0

    def P(x, z):                                               # ekran gry: −X w prawo, +Z w górę
        return W / 2 + (cx - x) * sk, H / 2 - (z - cz) * sk

    d = ImageDraw.Draw(im)
    f, fm = g._czcionka(34, True), g._czcionka(22, True)
    for t, x, z in (("MEADOW", 40, -40), ("DEEP WOODS", 0, 330), ("WATERFALL", -150, 175), ("WINDY HIGHLANDS", -255, 240),
                    ("WIND CANYON", -205, 0), ("LAVA CALDERA", -318, -175), ("ASH TRAIL", -175, -140), ("LILY LAKE", 72, -222),
                    ("SEALED GATE", 200, -20), ("HIDDEN GLADE", 160, 140)):
        q = P(x, z)
        w = d.textlength(t, font=f)
        d.text((q[0] - w / 2, q[1]), t, fill=(255, 255, 255), font=f, stroke_width=5, stroke_fill=(20, 16, 28))
    kol = {"S": (255, 214, 64), "B": (255, 255, 255), "L": (255, 130, 50), "W": (150, 235, 255), "R": (127, 248, 255)}
    pkt = [(e["id"], e["x"], e["z"]) for e in S["sekrety"] if "x" in e]
    pkt += [(e["id"], e["x"], e["z"]) for e in S["bramy_rozmiaru"]] + [(e["id"], e["x"], e["z"]) for e in S["lamliwe"]]
    pkt += [(e["id"], e["x"], e["z"]) for e in S["wiatry"]]
    pkt += [(k["id"], k["x"], k["z"]) for e in S["sekrety"] if e["id"] == "S14" for k in e["kamienie"]]
    for id, x, z in pkt:
        q = P(x, z)
        c = kol[id[0]]
        d.ellipse((q[0] - 7, q[1] - 7, q[0] + 7, q[1] + 7), fill=c, outline=(20, 16, 28), width=3)
        d.text((q[0] + 9, q[1] - 14), id, fill=c, font=fm, stroke_width=4, stroke_fill=(20, 16, 28))
    leg = "S sekret · R kamień runiczny · B brama rozmiaru · L do rozbicia (stadium 6+) · W prąd wznoszący"
    d.text((20, H - 44), leg, fill=(255, 255, 255), font=fm, stroke_width=4, stroke_fill=(20, 16, 28))
    d.text((20, 16), "Mapa v2 (propozycja) — z góry; północ (+Z) u góry, −X w prawo jak na ekranie gry", fill=(255, 255, 255),
           font=g._czcionka(30, True), stroke_width=4, stroke_fill=(20, 16, 28))
    return im
