# -*- coding: utf-8 -*-
"""Wspólne klocki bazaru: skorupa sklepu z wnętrzem, lada, półki, markiza, lampa, girlanda, punkty E i rejestr znaczników.

Zasady stylu bez zmian (D-041): przykazania z swiat/krzywe_miasteczko/PROJEKT.md rozdz. 1, kolory tylko z paleta.py,
elementy powtarzalne z zestaw.py (import, nie kopia). Nowe jest tylko to, czego stare miasteczko nie miało: WNĘTRZA
(D-084 — do sklepu się wchodzi, E na sprzedawcy otwiera okno 2D).

Skorupa sklepu (układ budynku: środek obrysu na ziemi, front z wejściem ku +Z, y = 0 = poziom bruku uliczki):
- parter H0 = 15 (ściany pionowe od ziemi do stropu — przykazanie 3), ściany 1,2, posadzka na 0,2;
- front od strony uliczki to SZEROKI OTWÓR (14–16 × 13) między wąskimi filarami — kamera gracza stoi wtedy za plecami
  postaci w otworze albo pod markizą na uliczce, a nie za ścianą (Roblox przysuwa kamerę, gdy coś ją zasłania);
- strop na 14,7 (płaski, z belkami), nad nim pełne, przechylone piętro z nawisem i dach-czapa (zestaw.dach_czapa) —
  krzywizna jest NAD wnętrzem, więc w środku nic nie wisi nisko;
- sprzedawca stoi za ladą przy tylnej ścianie, twarzą do wejścia; gracz staje przed ladą (punkt E) — kamera 12,5 za
  nim wypada w otworze wejścia.
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biblioteka.scena import razy_wektor  # noqa: E402
from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402

Y_PODLOGI = 0.2           # wierzch posadzki sklepu nad poziomem bruku
H_LADY = 3.0              # wierzch lady nad posadzką (dłonie sprzedawcy ×0,85 leżą na ladzie)

# --------------------------------------------------------------------------- rejestr znaczników (świat Studio)
ZNACZNIKI = []


def swiat(s, p):
    """Punkt z bieżącego układu lokalnego sceny → świat (ten sam rachunek co Scena.dodaj)."""
    R, t, k = s._stos[-1]
    q = razy_wektor(R, p)
    return [round(t[i] + k * q[i], 3) for i in range(3)]


def kierunek(s, d):
    R, _, _ = s._stos[-1]
    q = razy_wektor(R, d)
    n = math.sqrt(sum(v * v for v in q)) or 1.0
    return [round(v / n, 4) for v in q]


def znacznik(s, typ, id_, pos, **pola):
    """Zapisz znacznik: typ (start, sklep, portal, dzialka, zagroda, tablica, training_center, las, lochy, …),
    id i punkt w bieżącym układzie; reszta pól (np. kier=(x,y,z) w układzie lokalnym) trafia do znaczniki.json."""
    z = {"typ": typ, "id": id_, "swiat": swiat(s, pos)}
    for k, v in pola.items():
        if k in ("kier", "normalna") and v is not None:
            z[k] = kierunek(s, v)
        elif k in ("punkt", "podpowiedz", "stoisko") and v is not None:
            z[k] = swiat(s, v)
        else:
            z[k] = v
    ZNACZNIKI.append(z)
    return z


def punkt_e(s, grupa, id_, stoisko, podpowiedz, **pola):
    """Dwa niewidzialne zaczepy w podgrupie `<grupa>/_Interakcja` (bez kolizji i cienia):
    „Punkt E <id>” — płytka 2 × 0,2 × 2 na posadzce tam, gdzie staje gracz (stoisko = (x, z) albo (x, y, z));
    „Podpowiedź E <id>” — kostka 1 × 1 × 1 na wysokości piersi sprzedawcy (tu skrypt wstawia ProximityPrompt).
    Rejestruje znacznik typu pola["typ"] (domyślnie „sklep”)."""
    st = (stoisko[0], Y_PODLOGI, stoisko[1]) if len(stoisko) == 2 else stoisko
    with s.grupa(grupa + "/_Interakcja"), s.cechy(kolizja=False, cien=False):
        s.blok("Punkt E " + id_, (st[0], st[1] + 0.1, st[2]), (2.0, 0.2, 2.0), "biel", alfa=1.0)
        s.blok("Podpowiedź E " + id_, podpowiedz, (1.0, 1.0, 1.0), "biel", alfa=1.0)
    typ = pola.pop("typ", "sklep")
    if "model" in pola:
        pola["model"] = s.korzen + "/" + pola["model"]          # pełna ścieżka Modelu sprzedawcy w Studio
    return znacznik(s, typ, id_, st, stoisko=st, podpowiedz=podpowiedz, grupa_zaczepu=s.korzen + "/" + grupa + "/_Interakcja",
                    czesc_stoiska="Punkt E " + id_, czesc_podpowiedzi="Podpowiedź E " + id_, **pola)


# --------------------------------------------------------------------------- skorupa sklepu
def skorupa(s, rnd, W, D, sciana, dach, H0=15.0, T=1.2, otwor=14.0, otwor_x=0.0, H_otw=13.0,
            posadzka=("drewno_jasne", "WoodPlanks"), hp=7.0, nawis=(2.4, 0.6, 1.0, 0.8), rz_p=5.0, ry_p=4.0,
            dach_h=10.0, rz_d=-9.0, okap=2.4, okap_bok=1.4, podzial=0.62, markiza=None, okna_pietra=("prostokat", "okragle"),
            swiatlo="neon_okno", okna_boczne=(1, 1), szczyt=True, kalenica=None, komin=None, duet="rycerz",
            na_pietrze=None, na_dachu=None):
    """Pusty w środku budynek-sklep (patrz docstring modułu). Zwraca słownik z wymiarami wnętrza i otworu, wysokością
    szczytu i układem dachu (do szyldów): {"wn": (x0, x1, z0, z1), "otwor": (xa, xb, H_otw), "H0", "front", "W1", "D1",
    "top", "dach": (pos, obrot, info)}."""
    xa, xb = otwor_x - otwor / 2.0, otwor_x + otwor / 2.0
    zf, zb = D / 2.0, -D / 2.0
    nazwa = s._grupy[-1]
    znacznik(s, "wejscie", "wejscie_" + nazwa, (otwor_x, 0.0, zf), kier=(0, 0, 1), szer=round(otwor - 0.2, 2),
             wys=round(H_otw - 0.1 - Y_PODLOGI, 2), budynek=nazwa,
             opis="światło wejścia (szerokość × wysokość nad posadzką) — jedno wejście do budynku")
    xl, xr = -W / 2.0, W / 2.0
    # --- posadzka, cokół, ściany (kolizja)
    # spody na różnych wysokościach (−0,15 / −0,05 / −0,1 / 0): żadne dwie płaszczyzny różnych kolorów się nie pokrywają
    s.blok("Posadzka", (0, (Y_PODLOGI - 0.15) / 2.0, 0), (W - 0.2, Y_PODLOGI + 0.15, D - 0.2), posadzka[0], posadzka[1])
    s.blok("Próg", (otwor_x, 0.125, zf - T / 2.0), (otwor - 0.2, 0.35, T + 0.3), "kamien_cokol", "Cobblestone")
    s.blok("Cokół", (0, 0.6, zb + T / 2.0), (W + 0.5, 1.4, T + 0.5), "kamien_cokol", "Cobblestone")
    for sx in (-1, 1):
        s.blok("Cokół", (sx * (W / 2.0 - T / 2.0), 0.6, 0), (T + 0.5, 1.4, D + 0.5), "kamien_cokol", "Cobblestone")
    s.blok("Ściana tył", (0, H0 / 2.0, zb + T / 2.0), (W - 2 * T, H0, T), sciana)
    for sx in (-1, 1):
        s.blok("Ściana bok", (sx * (W / 2.0 - T / 2.0), H0 / 2.0, 0), (T, H0, D), sciana)
    for a, b in ((xl + T, xa), (xb, xr - T)):
        if b - a > 0.05:
            s.blok("Filar", ((a + b) / 2.0, H0 / 2.0, zf - T / 2.0), (b - a, H0, T), sciana)
            ca, cb = (a - 0.2, b - 0.15) if b <= xa + 1e-6 else (a + 0.15, b + 0.2)      # cokół filara kończy się przed otworem
            s.blok("Cokół", ((ca + cb) / 2.0, 0.6, zf - T / 2.0), (cb - ca, 1.4, T + 0.5), "kamien_cokol", "Cobblestone")
    s.blok("Nadproże", (otwor_x, (H_otw + H0) / 2.0, zf - T / 2.0), (otwor, H0 - H_otw, T), sciana)
    s.blok("Strop", (0, H0 - 0.25, 0), (W - 2 * T, 0.5, D - 2 * T), "drewno_jasne", "Wood")
    with s.cechy(kolizja=False):
        for z in (-D / 4.0, D / 4.0):
            s.blok("Belka stropu", (0, H0 - 0.85, z), (W - 2 * T, 0.7, 0.8), "drewno_ciemne", "Wood")
        # --- tusz: narożniki, rama otworu, rant cokołu, pas cienia
        for sx in (-1, 1):
            for sz in (-1, 1):
                s.blok("Narożnik", (sx * (W / 2.0 - 0.5), (1.3 + H0 + 0.3) / 2.0, sz * (D / 2.0 - 0.5)), (1.3, H0 - 1.0, 1.3), "tusz")
        for x in (xa - 0.35, xb + 0.35):                      # rama wystaje 0,1 w otwór (inna płaszczyzna niż filar)
            s.blok("Rama otworu", (x, (Y_PODLOGI + H_otw) / 2.0, zf - T / 2.0), (0.9, H_otw - Y_PODLOGI, T + 0.7), "tusz")
        s.blok("Rama otworu", (otwor_x, H_otw + 0.35, zf - T / 2.0), (otwor + 1.8, 0.9, T + 0.7), "tusz")
        with s.cechy(cien=False):
            s.blok("Pas cienia", (0, H0 - 0.6, zf + 0.1), (W - 2.8, 0.9, 0.2), cien(s, sciana))
    # --- okna w bocznych ścianach (na zewnątrz) + poświata od środka
    for sx, n in ((-1, okna_boczne[0]), (1, okna_boczne[1])):
        for i in range(n):
            z = (-D * 0.12 if n == 1 else (-D * 0.25 + i * D * 0.32)) + rnd.uniform(-0.8, 0.8)
            zestaw.okno(s, (sx * W / 2.0, 7.5 + rnd.uniform(-0.4, 0.4), z), 3.0, 4.0, przechyl=sx * rnd.choice((5, 6, 7)),
                        swiatlo=swiatlo, ry=90 * sx, okiennica=(dach if i == 0 and sx < 0 else None), strona_okiennicy=1)
            with s.cechy(kolizja=False, cien=False):
                s.blok("Okno od środka", (sx * (W / 2.0 - T - 0.1), 7.5, z), (0.2, 3.6, 2.6), swiatlo,
                       "Neon" if swiatlo.startswith("neon_") else "SmoothPlastic")
    # --- markiza nad wejściem (spód ≥ 12,4: kamera i głowa przechodzą pod nią)
    if markiza:
        markiza_pasy(s, (otwor_x, H_otw + 1.15, zf + 0.25), otwor + 2.0, 3.2, markiza)
    # --- piętro: nawis, przechył, skręt (kontra z dachem) — pełna bryła NAD wnętrzem
    nf, nb, nl, nr = nawis
    W1, D1 = W + nl + nr, D + nf + nb
    x1, z1 = (nr - nl) / 2.0, (nf - nb) / 2.0
    # piętro uniesione o e: najniższy punkt jego spodu (strona opuszczona przechyłem) leży 0,05 nad wierzchem ścian, więc
    # nic z piętra nie wchodzi pod strop do wnętrza; szczelinę nad ścianami po stronie uniesionej wypełnia „kolanko”
    e = (W1 / 2.0) * math.sin(math.radians(abs(rz_p))) + 0.05
    wynik = {"wn": (xl + T, xr - T, zb + T, zf - T), "otwor": (xa, xb, H_otw), "H0": H0, "front": zf, "W1": W1, "D1": D1}
    with s.cechy(kolizja=False):
        s.blok("Kolanko", (0, H0 + e, 0), (W - 0.3, 2.0 * e, D - 0.3), sciana)
    with s.uklad(pos=(x1, H0 + e, z1), obrot=(0, ry_p, rz_p)):
        with s.cechy(kolizja=False):
            s.blok("Wieniec", (0, 0.35, 0), (W1 + 0.6, 0.9, D1 + 0.6), "tusz")
        s.blok("Piętro", (0, hp / 2.0, 0), (W1, hp, D1), sciana)
        with s.cechy(kolizja=False):
            for sx in (-1, 1):
                for sz in (-1, 1):
                    s.blok("Narożnik", (sx * (W1 / 2.0 - 0.25), (0.8 + hp + 0.2) / 2.0, sz * (D1 / 2.0 - 0.25)),
                           (1.2, hp - 0.6, 1.2), "tusz")
            s.blok("Pas cienia", (0, hp - 0.7, D1 / 2.0 + 0.05), (W1 - 1.6, 1.1, 0.2), cien(s, sciana))
            # szachulec: belki na froncie piętra (pion przy narożnikach i środku, dwa skosy) — rytm fasady bez napisów
            zf1 = D1 / 2.0 + 0.12
            for x in (-W1 * 0.39, W1 * 0.02, W1 * 0.39):
                s.blok("Belka szachulca", (x, (0.8 + hp - 1.25) / 2.0, zf1), (0.7, hp - 2.05, 0.25), "drewno_ciemne", "Wood")
            for x0, x1 in ((-W1 * 0.39, -W1 * 0.12), (W1 * 0.39, W1 * 0.12)):
                s.belka("Belka szachulca", (x0, 0.9, zf1), (x1, hp - 1.35, zf1), 0.6, "drewno_ciemne", "Wood", 0.25)
            # wiszące banery w kolorze kodu po bokach frontu piętra (Fabric)
            for zn in (-1, 1):
                with s.uklad(pos=(zn * (W1 / 2.0 + 0.45), hp * 0.55, D1 / 2.0 - 1.2), obrot=(0, 0, zn * 4)):
                    s.blok("Baner", (0, 0, 0), (0.3, hp * 0.7, 2.0), dach, "Fabric")
                    s.klin("Baner ogon", (0, -hp * 0.35 - 0.6, 0), (0.3, 1.2, 2.0), dach, "Fabric", rot=(180, 0, 0))
        yo = 0.8 + (hp - 0.8) * 0.48
        for i, k in enumerate(okna_pietra):
            x = (-0.27 + 0.5 * i) * W1 if len(okna_pietra) > 1 else -0.24 * W1
            if k == "okragle":
                zestaw.okno(s, (x, yo, D1 / 2.0), 3.0, ksztalt="okragle", swiatlo=swiatlo, przechyl=0)
            else:
                zestaw.okno(s, (x, yo, D1 / 2.0), 3.2, 3.6, przechyl=(-6 if i else 7), swiatlo=swiatlo,
                            okiennica=(dach if i == 0 else None), strona_okiennicy=-1)
        if na_pietrze:
            na_pietrze(s, {"W1": W1, "D1": D1, "hp": hp})
        ext = (W1 / 2.0) * math.sin(math.radians(abs(rz_d))) + 0.25
        with s.uklad(pos=(0, hp, 0), obrot=(0, 0, rz_d)):
            with s.cechy(kolizja=False):
                s.blok("Kolanko", (0, -ext / 2.0 + 0.05, 0), (W1 - 0.8, ext, D1 - 0.8), sciana)
            info = None
            if dach_h > 0:
                info = zestaw.dach_czapa(s, W1, D1, dach_h, dach, okap=okap, okap_bok=okap_bok, podzial=podzial,
                                         kalenica=kalenica, szczyt=sciana if szczyt else None)
                wynik["dach"] = info
                if komin:
                    zk = info["z_kalenicy"] - (1 - podzial) * D1 * 0.45
                    yk = dach_h * (1 - 0.45 * (1 - podzial) * D1 / ((1 - podzial) * D1 + okap)) - 1.6
                    zestaw.komin(s, (komin * W1 * 0.28, yk, zk), zestaw.KOMIN_DOMU, ("kamien_cokol", None), dym_n=2,
                                 dym_ksztalt="klocek", dym_kolor=cien(s, "biel", 0.9))
                if duet:
                    zestaw.choragiewka_duetu(s, (-0.3 * W1, dach_h - 0.1, info["z_kalenicy"]), duet, przechyl=12)
            if na_dachu:
                na_dachu(s, {"W1": W1, "D1": D1, "dach_h": dach_h, "okap": okap, "podzial": podzial, "info": info})
            wynik["swiat_dachu"] = swiat(s, (0, 0, 0))
    wynik["top"] = H0 + hp + dach_h
    return wynik


# --------------------------------------------------------------------------- elementy wnętrz i fasad
def markiza_pasy(s, pos, szer, wysiegnik, kolory, kat=22.0, n=None):
    """Markiza w pasy nad wejściem: pos = środek górnej krawędzi przy ścianie (+Z na zewnątrz), wysięgnik ku +Z, opada
    o `kat`°. kolory = (kolor kodu, "biel"). Bez kolizji. Części: n + 3 (n pasów, rant, 2 wsporniki)."""
    n = n or max(5, int(round(szer / 2.2)) | 1)
    pas = szer / n
    with s.uklad(pos=pos, obrot=(kat, 0, 0)), s.cechy(kolizja=False):
        for i in range(n):
            x = -szer / 2.0 + pas * (i + 0.5)
            s.blok("Markiza", (x, 0.05 * (i % 2), wysiegnik / 2.0), (pas + 0.02, 0.35, wysiegnik), kolory[i % 2], "Fabric")
        with s.cechy(cien=False):
            s.blok("Markiza ząbki", (0, -0.45, wysiegnik - 0.15), (szer - 0.3, 0.8, 0.3), kolory[0], "Fabric")
        s.blok("Markiza rant", (0, -0.25, wysiegnik / 2.0), (szer + 0.5, 0.25, wysiegnik + 0.5), "tusz")
    with s.cechy(kolizja=False, cien=False):
        for sx in (-1, 1):
            s.belka("Markiza wspornik", (pos[0] + sx * (szer / 2.0 - 0.6), pos[1] - 1.4, pos[2]),
                    (pos[0] + sx * (szer / 2.0 - 0.6), pos[1] - wysiegnik * math.sin(math.radians(kat)) - 0.2,
                     pos[2] + wysiegnik * math.cos(math.radians(kat)) - 0.3), 0.3, "tusz", "SmoothPlastic", 0.3)


def lada(s, pos, dl, kolor="drewno_jasne", blat="drewno", akcent=None, gl=2.4, ry=0.0):
    """Lada sklepowa: korpus dl × H_LADY × gl (WoodPlanks, z kolizją) na posadzce, blat wysunięty, listwy i obrys tuszem,
    pas w kolorze kodu. pos = środek podstawy (y = posadzka). Części: 6."""
    with s.uklad(pos=pos, obrot=(0, ry, 0)):
        s.blok("Lada", (0, H_LADY / 2.0, 0), (dl, H_LADY - 0.2, gl), kolor, "WoodPlanks")
        with s.cechy(kolizja=False):
            s.blok("Lada blat", (0, H_LADY - 0.05, 0.1), (dl + 0.6, 0.4, gl + 0.5), blat, "Wood")
            s.blok("Lada rant", (0, H_LADY - 0.3, 0.1), (dl + 0.8, 0.25, gl + 0.7), "tusz")
            s.blok("Lada cokół", (0, 0.3, 0.05), (dl + 0.2, 0.6, gl + 0.2), "tusz")
            if akcent:
                s.blok("Lada pas", (0, 1.6, gl / 2.0 + 0.05), (dl - 1.2, 0.8, 0.2), akcent)
            for x in (-dl / 2.0 + 1.2, dl / 2.0 - 1.2):
                s.blok("Lada listwa", (x, 1.4, gl / 2.0 + 0.06), (0.5, 2.0, 0.2), cien(s, kolor, 0.8))


def polka(s, pos, dl, ry=0.0, kolor="drewno", wsporniki="tusz"):
    """Półka ścienna: deska dl × 0,4 × 1,4 i dwa wsporniki; pos = środek deski przy ścianie (+Z od ściany). Części: 3."""
    with s.uklad(pos=pos, obrot=(0, ry, 0)), s.cechy(kolizja=False):
        s.blok("Półka", (0, 0, 0.7), (dl, 0.4, 1.4), kolor, "Wood")
        with s.cechy(cien=False):
            for x in (-dl / 2.0 + 0.8, dl / 2.0 - 0.8):
                s.blok("Półka wspornik", (x, -0.55, 0.45), (0.3, 0.8, 0.8), wsporniki)


def lampa(s, pos, swiatlo="neon_okno", lancuch=2.0):
    """Lampa wisząca ze stropu: łańcuszek, daszek-romb tuszem, świecąca kostka Neon. pos = punkt zawieszenia. Części: 4."""
    x, y, z = pos
    with s.cechy(kolizja=False):
        s.blok("Lampa łańcuch", (x, y - lancuch / 2.0, z), (0.25, lancuch, 0.25), "tusz")
        s.blok("Lampa daszek", (x, y - lancuch - 0.2, z), (1.8, 0.45, 1.8), "tusz", rot=(0, 45, 0))
        with s.cechy(cien=False):
            s.blok("Lampa światło", (x, y - lancuch - 1.15, z), (1.2, 1.5, 1.2), swiatlo,
                   "Neon" if swiatlo.startswith("neon_") else "SmoothPlastic")
        s.blok("Lampa spód", (x, y - lancuch - 2.05, z), (1.4, 0.35, 1.4), "tusz", rot=(0, 45, 0))


def girlanda(s, a, b, kolory, ugiecie=1.6, n=9):
    """Girlanda chorągiewek nad uliczką od punktu a do b (świat lokalny bazaru): sznurek z 4 odcinków ugiętych w łuk
    i n trójkątnych chorągiewek z klinów (Fabric). Bez kolizji i cienia. Części: 4 + n."""
    def p(t):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t - ugiecie * 4 * t * (1 - t), a[2] + (b[2] - a[2]) * t)
    kier = math.degrees(math.atan2(b[0] - a[0], b[2] - a[2]))
    with s.cechy(kolizja=False, cien=False):
        for i in range(4):
            s.belka("Girlanda sznurek", p(i / 4.0), p((i + 1) / 4.0), 0.2, "drewno_ciemne", "SmoothPlastic", 0.2)
        for i in range(n):
            t = (i + 0.5) / n
            x, y, z = p(t)
            s.klin("Girlanda chorągiewka", (x, y - 1.0, z), (0.25, 1.9, 1.6), kolory[i % len(kolory)], "Fabric",
                   rot=(180, kier + 90, 0))


def szyld_na_pietrze(s, p, x, rysuj, skala=1.0, ry=20.0, rz=-8.0, wysun=2.0, y=None, rx=-6.0):
    """Szyld-rekwizyt przed frontem piętra (wywołanie w układzie piętra, p = słownik z na_pietrze): krótki wysięgnik
    z dwóch belek tuszem od lica do górnej krawędzi szyldu i sam szyld rysowany funkcją rysuj(s) w płaszczyźnie XY
    (front +Z), obrócony o ry ku placowi i pochylony o rz w bok (przykazanie 7). Bez kolizji."""
    D1, hp = p["D1"], p["hp"]
    yc = hp * 0.42 if y is None else y
    zc = D1 / 2.0 + wysun
    with s.cechy(kolizja=False):
        for dx in (-1.6, 1.6):
            s.belka("Wysięgnik", (x + dx, yc + 2.6, D1 / 2.0 - 0.2), (x + dx * 0.8, yc + 2.2, zc), 0.6, "tusz", "SmoothPlastic", 0.6)
        with s.uklad(pos=(x, yc, zc), obrot=(rx, ry, rz), skala=skala):
            rysuj(s)


def wysiegnik(s, p0, dl, kolor="tusz", grub=0.9):
    """Wysięgnik szyldu: belka od punktu mocowania p0 ku +Z o długości dl, zastrzał pod spodem i złota gałka na końcu.
    Bez kolizji. Zwraca punkt końca (x, y, z). Części: 3."""
    x, y, z = p0
    b = (x, y, z + dl)
    with s.cechy(kolizja=False):
        s.belka("Wysięgnik", p0, b, grub, kolor, "SmoothPlastic", grub)
        s.belka("Wysięgnik zastrzał", (x, y - 3.0, z + 0.2), (x, y - 0.2, z + dl * 0.6), grub * 0.7, kolor, "SmoothPlastic",
                grub * 0.7)
        s.blok("Wysięgnik gałka", (x, y, z + dl + 0.3), (1.3, 1.3, 1.3), "zloto", rot=(45, 0, 45))
    return b


def scianka(s, pos, dl, wys=10.0, ry=0.0, kolor="kamien_cieply", gl=1.6):
    """Ścianka-łącznik między budynkami (zamyka szczelinę, w którą nie zmieściłby się gracz): korpus z kolizją, cokół,
    czapa tuszem. pos = środek podstawy. Części: 3."""
    with s.uklad(pos=pos, obrot=(0, ry, 0)):
        s.blok("Ścianka", (0, wys / 2.0, 0), (dl, wys, gl), kolor)
        with s.cechy(kolizja=False):
            s.blok("Ścianka cokół", (0, 0.6, 0), (dl + 0.3, 1.2, gl + 0.4), "kamien_cokol", "Cobblestone")
            s.blok("Ścianka czapa", (0, wys + 0.25, 0), (dl + 0.5, 0.5, gl + 0.5), "tusz")
