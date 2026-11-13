# -*- coding: utf-8 -*-
"""Zestaw wspólny mapy v2 „Krzywe Miasteczko” — elementy powtarzalne dla budowniczych i generatora miasta.

Kontrakt: swiat/krzywe_miasteczko/PROJEKT.md, rozdz. 1 (przykazania stylu) i 6 (elementy wspólne).
Status: propozycja (noc 13.11.2026), nie kanon.

Zasady wspólne dla WSZYSTKICH funkcji:
- pierwszy argument to scena `s` (swiat.biblioteka.scena.Scena); funkcja buduje w BIEŻĄCYM układzie lokalnym wywołującego
  i w jego bieżącej grupie (sama grup nie zakłada — wyjątek: punkt_interakcji);
- `pos` = (x, y, z) punktu zaczepienia w układzie wywołującego (opis w docstringu), `ry` = obrót wokół pionu w stopniach
  (ry = θ kieruje lokalny front +Z elementu w stronę (sin θ, cos θ));
- elementy ścienne (okno, drzwi, łata, wnęka klocka) stoją na licu ściany: lokalne +Z = na zewnątrz ściany;
- kolory to klucze palety (paleta.py); brakujące klucze funkcje same dopisują do s.paleta, więc zestaw działa też w scenie
  bez palety; ciemniejszy ton = cien(s, klucz);
- dekoracje mają kolizję wyłączoną, a drobiazgi (< 2 study w każdym wymiarze) i płaskie łaty także cień — wg rzemioslo.md;
- żadnych liter, żadnych skojarzeń z alkoholem (beczka = woda albo jabłka), części ≥ 0,2 studa, płaszczyzny różnych
  kolorów rozsunięte o ≥ 0,05 (zwykle 0,1).

Liczby części podane w docstringach dotyczą wariantu domyślnego; ściąga dla budowniczych: na końcu pliku (SCIAGA).
"""
import contextlib
import math
import os
import random
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko.paleta import PALETA, cien  # noqa: E402

# dachy ciemne: kalenica i deski czołowe jasne (przykazanie 6)
CIEMNE_DACHY = {"dach_zbrojownia", "dach_twierdza", "dach_gildia", "dach_sklep", "dach_arena", "dach_dom_lupek"}


# =========================================================================== narzędzia
def _pal(s):
    """Dopisz do sceny klucze palety, których jeszcze nie ma (zestaw działa w każdej scenie)."""
    for k, v in PALETA.items():
        if k not in s.paleta:
            s.paleta[k] = v


def _mat_szyby(kolor):
    return "Neon" if str(kolor).startswith("neon_") else "SmoothPlastic"


def _rnd(rnd):
    return rnd if rnd is not None else random.Random(0)


def lamana(s, nazwa, segmenty, kolor, mat="SmoothPlastic", start=(0.0, 0.0), z=0.0, glebokosc=None):
    """Krzywy słup / komin / pień z bloków w płaszczyźnie XY (zgięcia wokół osi Z).

    segmenty = [(długość, grubość, kąt_względny°), …] — każdy segment rośnie z końca poprzedniego; kąt > 0 = góra ucieka
    w lewo (ku −X), < 0 = w prawo. Zakładka na zgięciu liczona sama ((grub/2)·tan kąta + 0,05), więc nie ma szpar.
    kolor = klucz albo lista kluczy (na przemian). Punkt zaczepienia: `start` = (x, y) środka podstawy, z = płaszczyzna.
    Zwraca (x, y, kąt_bezwzględny°) końca ostatniego segmentu. Części: len(segmenty)."""
    _pal(s)
    x, y = start
    kat = 0.0
    for i, (dl, g, k) in enumerate(segmenty):
        kat += k
        zak = ((g / 2.0) * math.tan(math.radians(abs(k))) + 0.05) if i else 0.0
        a = math.radians(kat)
        dx, dy = -math.sin(a), math.cos(a)
        kol = kolor[i % len(kolor)] if isinstance(kolor, (list, tuple)) else kolor
        s.blok(nazwa, (x + dx * (dl - zak) / 2.0, y + dy * (dl - zak) / 2.0, z), (g, dl + zak, glebokosc or g), kol, mat, (0, 0, kat))
        x, y = x + dx * dl, y + dy * dl
    return x, y, kat


def punkt_interakcji(s, nazwa_grupy, pos):
    """Niewidzialny zaczep ProximityPrompt (PROJEKT 5.0 p. 5): blok 2 × 0,2 × 2, alfa 1, bez kolizji i cienia, w podgrupie
    „<nazwa_grupy>/_Interakcja”. pos = (x, z) albo (x, y, z) na ziemi w układzie budynku. Części: 1."""
    _pal(s)
    x, y, z = (pos[0], 0.0, pos[1]) if len(pos) == 2 else pos
    with s.grupa(nazwa_grupy + "/_Interakcja"), s.cechy(kolizja=False, cien=False):
        s.blok("Punkt interakcji", (x, y + 0.1, z), (2.0, 0.2, 2.0), "biel", alfa=1.0)


# =========================================================================== okna i drzwi
def okno(s, pos, szer=3.0, wys=4.0, ksztalt="prostokat", przechyl=5.0, swiatlo="neon_okno", szprosy=True, parapet=True,
         okiennica=None, strona_okiennicy=1, ry=0.0, tanie=False):
    """Okno na ścianie: ciemna rama-podkładka, świecąca szyba Neon, szprosy, parapet, opcjonalnie zwisająca okiennica.

    pos = środek okna NA LICU ściany; lokalne +Z = na zewnątrz. Warstwy od lica: rama tusz (+0,40) → szyba (+0,50) →
    szprosy (+0,60) → parapet (+1,10). ksztalt: "prostokat" (3 × 4, 4 × 5…), "luk" (prostokąt + półkole; wys = część
    prosta), "okragle" (Ø = szer, bez parapetu). przechyl = obrót w płaszczyźnie ściany (przykazanie 12: 4–8°, każde okno
    inne). swiatlo = klucz koloru szyby: neon_* → materiał Neon; inny klucz (np. "woda_gleboka") → ciemna szyba bez
    świecenia (domy mają Neon tylko w 1–2 oknach). okiennica = klucz koloru jednej okiennicy (zwisa 12° na jednym zawiasie,
    z podkładką tusz), strona_okiennicy = +1 prawa / −1 lewa. tanie = tylko rama + szyba.
    Bez kolizji; szyba bez cienia.
    Części: prostokąt 5 (+2 okiennica), łuk 7, okrągłe 4, tanie 2 (łuk tanie 4)."""
    _pal(s)
    mat = _mat_szyby(swiatlo)
    with s.uklad(pos=pos, obrot=(0, ry, przechyl)), s.cechy(kolizja=False):
        if ksztalt == "okragle":
            r = szer / 2.0
            s.walec("Okno rama", (0, 0, 0.15), r + 0.6, 0.5, "tusz", os="z")
            with s.cechy(cien=False):
                s.walec("Okno szyba", (0, 0, 0.3), r, 0.4, swiatlo, mat, os="z")
            if szprosy and not tanie:
                s.blok("Okno szpros", (0, 0, 0.45), (0.35, 2 * r - 0.1, 0.3), "tusz")
                s.blok("Okno szpros", (0, 0, 0.47), (2 * r - 0.1, 0.35, 0.3), "tusz")
            return
        s.blok("Okno rama", (0, 0, 0.15), (szer + 1.2, wys + 1.2, 0.5), "tusz")
        with s.cechy(cien=False):
            s.blok("Okno szyba", (0, 0, 0.3), (szer, wys, 0.4), swiatlo, mat)
        gora = wys / 2.0
        if ksztalt == "luk":
            s.walec("Okno rama", (0, wys / 2.0, 0.15), szer / 2.0 + 0.6, 0.5, "tusz", os="z")
            with s.cechy(cien=False):
                s.walec("Okno szyba", (0, wys / 2.0, 0.3), szer / 2.0, 0.4, swiatlo, mat, os="z")
            gora = wys / 2.0 + szer / 2.0
        if tanie:
            return
        if szprosy:
            s.blok("Okno szpros", (0, (gora - wys / 2.0) / 2.0, 0.45), (0.35, gora + wys / 2.0 - 0.1, 0.3), "tusz")
            s.blok("Okno szpros", (0, wys * 0.1, 0.47), (szer - 0.1, 0.35, 0.3), "tusz")
        if parapet:
            s.blok("Okno parapet", (0, -wys / 2.0 - 0.65, 0.5), (szer + 2.1, 0.55, 1.2), "drewno_jasne")
        if okiennica:
            st = 1 if strona_okiennicy >= 0 else -1
            sz = szer * 0.5 + 0.3
            with s.uklad(pos=(st * (szer / 2.0 + 0.6), 0.1, 0.25), obrot=(0, -st * 14, -st * 12)), s.cechy(cien=False):
                s.blok("Okiennica", (st * (sz / 2.0 + 0.15), 0, 0.2), (sz, wys + 0.4, 0.3), okiennica)
                s.blok("Okiennica obrys", (st * (sz / 2.0 + 0.15), 0, 0.0), (sz + 0.6, wys + 1.0, 0.25), "tusz")


def drzwi(s, pos, szer=8.0, wys=10.0, kolor="drewno_ciemne", luk=False, nadproze="drewno", przechyl_nadproza=5.0,
          prog="kamien_cokol", ry=0.0, tanie=False, gleb=1.0):
    """Drzwi-portal: gruba rama tusz (1,0) wysunięta przed lico, skrzydło cofnięte o `gleb` (udana wnęka bez wycinania
    ściany), próg, listwy, okucia, gałka, krzywe nadproże.

    pos = środek progu NA LICU ściany, y = poziom podłogi (ziemi przed drzwiami); lokalne +Z = na zewnątrz.
    szer × wys = światło otworu (budynek główny ≥ 8 × 10, dom 6 × 8). Rama sięga od lica do +gleb+0,4, skrzydło
    (`kolor`, WoodPlanks) ma lico na +0,4. luk=True: górna część to półkole o średnicy szer (wys = całość, łącznie z łukiem;
    bez nadproża). nadproze = klucz koloru belki nad drzwiami (None = bez), szersza od ramy o 0,6 z każdej strony, przechylona.
    prog = klucz koloru progu (None = bez) — próg ma kolizję (0,4 wys.), reszta bez kolizji.
    Części: 11 (łuk 11), tanie 7 (bez listew i okuć; tanie + nadproze=None: 6)."""
    _pal(s)
    D = gleb + 0.6
    zc = (gleb + 0.2) / 2.0                                    # rama od z = −0,2 do z = gleb + 0,4
    hp = wys - szer / 2.0 if luk else wys                     # wysokość części prostej
    with s.uklad(pos=pos, obrot=(0, ry, 0)):
        if prog:                                               # próg od z = −0,1 do gleb + 1,0, od y = −0,1 do 0,4
            s.blok("Drzwi próg", (0, 0.15, (gleb + 0.9) / 2.0), (szer + 2.4, 0.5, gleb + 1.1), prog)
        with s.cechy(kolizja=False):
            for znak in (-1, 1):
                s.blok("Drzwi rama", (znak * (szer / 2.0 + 0.5), (hp + 0.1) / 2.0, zc), (1.0, hp - 0.1, D), "tusz")
            if luk:
                s.walec("Drzwi rama", (0, hp, 0.05), szer / 2.0 + 1.0, 0.5, "tusz", os="z")
                s.blok("Drzwi skrzydło", (0, (hp + 0.3) / 2.0, 0.2), (szer + 0.2, hp - 0.3, 0.4), kolor, "WoodPlanks")
                s.walec("Drzwi skrzydło", (0, hp, 0.2), szer / 2.0, 0.4, kolor, "WoodPlanks", os="z")
                gora = hp + szer / 2.0
            else:
                s.blok("Drzwi rama", (0, hp + 0.5, zc), (szer + 2.0, 1.0, D), "tusz")
                s.blok("Drzwi skrzydło", (0, (hp + 0.4) / 2.0, 0.2), (szer + 0.2, hp - 0.2, 0.4), kolor, "WoodPlanks")
                gora = hp + 1.0
            if not tanie:
                with s.cechy(cien=False):
                    for y in (0.25 * hp, 0.72 * hp):
                        s.blok("Drzwi listwa", (0, y, 0.5), (szer - 0.6, 0.6, 0.3), "drewno")
                        s.blok("Drzwi okucie", (-szer / 2.0 + 1.1, y, 0.6), (1.8, 0.45, 0.3), "metal_ciemny")
            with s.cechy(cien=False):
                s.blok("Drzwi gałka", (szer * 0.3, 0.45 * hp + 0.4, 0.7), (0.8, 0.8, 0.5), "zloto", rot=(0, 0, 45))
            if nadproze and not luk:
                s.blok("Drzwi nadproże", (0, gora + 0.1, zc + 0.2), (szer + 3.2, 1.2, D + 0.4), nadproze, "Wood",
                       rot=(0, 0, przechyl_nadproza))


# =========================================================================== rekwizyty uliczne
def latarnia(s, pos, wys=9.0, ry=0.0, swiatlo="neon_okno", plama=True, lustro=False, plama_r=4.0):
    """Krzywa latarnia: słup łamany z 3 segmentów (+5°, −9°, wysięgnik −38°) w tuszu, klatka (daszek-romb, świecąca kostka
    Neon 1,3 × 1,7, spód) na haku i ciepła plama Ø 2·plama_r (domyślnie 8) na ziemi pod światłem (bez kolizji i cienia).

    pos = środek podstawy słupa na nawierzchni (y = wierzch bruku/ulicy); wysięgnik wychodzi ku +X (lustro=True: ku −X),
    ry obraca całość. wys ≈ wysokość wierzchołka (domyślnie 9). Bez kolizji (rekwizyt na ścieżce: przekrój 0,6,
    gracz przechodzi przez słup zamiast się o niego potykać — PROJEKT 4.9). Części: 8 (bez plamy 7)."""
    _pal(s)
    zn = -1.0 if lustro else 1.0
    with s.uklad(pos=pos, obrot=(0, ry, 0)), s.cechy(kolizja=False):
        xe, ye, _ = lamana(s, "Latarnia słup", [(wys * 0.55, 0.6, 5 * zn), (wys * 0.3, 0.5, -9 * zn), (wys * 0.26, 0.45, -38 * zn)],
                           "tusz")
        s.blok("Latarnia hak", (xe, ye - 0.35, 0), (0.3, 0.9, 0.3), "tusz")
        s.blok("Latarnia daszek", (xe, ye - 0.95, 0), (2.0, 0.5, 2.0), "tusz", rot=(0, 45, 0))
        with s.cechy(cien=False):
            s.blok("Latarnia światło", (xe, ye - 2.05, 0), (1.3, 1.7, 1.3), swiatlo, _mat_szyby(swiatlo))
        s.blok("Latarnia spód", (xe, ye - 3.05, 0), (1.7, 0.4, 1.7), "tusz", rot=(0, 45, 0))
        if plama:
            with s.cechy(cien=False):
                s.walec("Latarnia plama", (xe, 0.06, 0), plama_r, 0.1, "tynk_krem", os="y")


def skrzynia(s, pos, ry=0.0, dl=4.0, a=3.5, przechyl=7.0, kolor="drewno", kolizja=True):
    """Skrzynia: korpus dl × a × a (WoodPlanks), 4 listwy narożne drewno_ciemne 0,5 wystające 0,1, ukośna listwa na froncie,
    wieko drewno_jasne większe o 0,4; przechylona o `przechyl`° na bok i wtopiona w ziemię (wyższy dolny róg na y = 0).
    pos = środek podstawy na ziemi; front (ukośna listwa) = +Z. Kolizję ma korpus (wys. 3,5 ≥ 2,5 — wolno na ścieżce),
    listwy i wieko nie. Części: 7."""
    _pal(s)
    p = math.radians(abs(przechyl))
    yc = (a / 2.0) * math.cos(p) - (dl / 2.0) * math.sin(p)
    with s.uklad(pos=(pos[0], pos[1] + yc, pos[2]), obrot=(0, ry, przechyl)):
        with s.cechy(kolizja=kolizja):
            s.blok("Skrzynia", (0, 0, 0), (dl, a, a), kolor, "WoodPlanks")
        with s.cechy(kolizja=False):
            for sx in (-1, 1):
                for sz in (-1, 1):
                    s.blok("Skrzynia listwa", (sx * (dl / 2.0 - 0.15), 0, sz * (a / 2.0 - 0.15)), (0.5, a + 0.1, 0.5), "drewno_ciemne")
            s.belka("Skrzynia ukos", (-dl / 2.0 + 0.4, -a / 2.0 + 0.35, a / 2.0 + 0.05), (dl / 2.0 - 0.4, a / 2.0 - 0.45, a / 2.0 + 0.05),
                    0.55, "drewno_ciemne", "SmoothPlastic", 0.3)
            s.blok("Skrzynia wieko", (0, a / 2.0 + 0.12, 0), (dl + 0.4, 0.45, a + 0.4), "drewno_jasne")


def beczka(s, pos, zawartosc="woda", r=1.8, h=4.4, przechyl=(0.0, 6.0), ry=0.0, kolizja=True):
    """Beczka na wodę albo jabłka — nigdy kran ani korek. Walec Ø 3,6 × 4,4 `drewno`, brzuch Ø +0,4 na 42 % wysokości,
    2 obręcze `metal_ciemny` Ø +0,6; w środku tafla `woda` ("woda"), 3 jabłka-kostki `czerwien` ("jablka") albo wieko
    `drewno_jasne` (None). pos = środek podstawy na ziemi; przechyl = (rx, rz)° — beczka jest wtopiona tak, by nie wisiała.
    Kolizję ma korpus. Części: woda 5, jabłka 7, pusta 5."""
    _pal(s)
    p = max(abs(przechyl[0]), abs(przechyl[1]))
    zag = r * math.sin(math.radians(p))
    with s.uklad(pos=(pos[0], pos[1] - zag, pos[2]), obrot=(przechyl[0], ry, przechyl[1])):
        with s.cechy(kolizja=kolizja):
            s.walec("Beczka", (0, h / 2.0, 0), r, h, "drewno", os="y")
        with s.cechy(kolizja=False):
            s.walec("Beczka brzuch", (0, h / 2.0, 0), r + 0.2, h * 0.42, "drewno", os="y")
            for y in (h * 0.17, h * 0.83):
                s.walec("Beczka obręcz", (0, y, 0), r + 0.3, 0.45, "metal_ciemny", os="y")
            if zawartosc == "woda":
                with s.cechy(cien=False):
                    s.walec("Beczka woda", (0, h - 0.02, 0), r - 0.3, 0.2, "woda", os="y")
            elif zawartosc == "jablka":
                for i, (x, z, d, k) in enumerate(((-0.6, 0.3, 1.2, 15), (0.6, -0.2, 1.2, -25), (0.0, 0.0, 1.1, 40))):
                    s.blok("Beczka jabłko", (x, h + 0.35 + 0.55 * (i == 2), z), (d, d, d), "czerwien", rot=(12, k, 8))
            else:
                s.walec("Beczka wieko", (0, h - 0.02, 0), r - 0.25, 0.2, "drewno_jasne", os="y")


def lawka(s, pos, ry=0.0, dl=6.0, kolizja=True):
    """Ławka: siedzisko dl × 0,6 × 1,6 `drewno_jasne` na wys. 1,9, 2 boczki-nogi `tusz` rozchylone o 5°, oparcie odchylone
    10° do tyłu. pos = środek pod ławką na ziemi; front (siedzi się twarzą) = +Z. Kolizję ma siedzisko.
    Części: 4."""
    _pal(s)
    with s.uklad(pos=pos, obrot=(0, ry, 0)):
        with s.cechy(kolizja=kolizja):
            s.blok("Ławka siedzisko", (0, 1.9, 0), (dl, 0.6, 1.6), "drewno_jasne", "Wood")
        with s.cechy(kolizja=False):
            for sx in (-1, 1):
                s.blok("Ławka noga", (sx * (dl / 2.0 - 0.9), 0.85, 0), (0.6, 1.9, 1.3), "tusz", rot=(0, 0, sx * 5))
            s.blok("Ławka oparcie", (0, 2.85, -0.62), (dl - 0.4, 1.4, 0.4), "drewno_jasne", "Wood", rot=(-10, 0, 0))


def stragan(s, pos, ry=0.0, kolory=("dach_karczma", "biel"), towar="jablka", tani=False):
    """Stragan 10 × 7, wys. 10: 4 krzywe słupy (odchylone 3–4° na zewnątrz), lada `drewno_jasne` z blatem, markiza z 7 pasów
    w dwóch kolorach pod 11° z ząbkami i rantem tusz, towar ×1,5 na blacie.

    pos = środek obrysu na ziemi; lada (front) od strony +Z. kolory = (pas 1, pas 2) — kod z tabeli 4.7 + "biel".
    towar: "jablka" (jabłka i dynie), "chleby" (bochny i ser), "krysztaly" (kryształki i gwiazdki), "tkaniny" (bele
    i chorągiewki), "klocki" (zabawki-klocki). Kolizję ma lada. tani = 3 pasy bez ząbków.
    Części: 25 (tani 13)."""
    _pal(s)
    with s.uklad(pos=pos, obrot=(0, ry, 0)):
        with s.cechy(kolizja=False):
            for sx in (-1, 1):
                for sz in (-1, 1):
                    h = 9.4 if sz < 0 else 7.9
                    with s.uklad(pos=(sx * 4.6, 0, sz * 3.0), obrot=(sz * 3, 0, -sx * 4)):
                        s.blok("Stragan słup", (0, h / 2.0, 0), (0.7, h, 0.7), "drewno", "Wood")
        s.blok("Stragan lada", (0, 1.7, 2.0), (9.6, 3.4, 2.6), "drewno_jasne", "WoodPlanks")
        with s.cechy(kolizja=False):
            s.blok("Stragan blat", (0, 3.55, 2.0), (10.4, 0.4, 3.2), "drewno")
            n = 3 if tani else 7
            Wm, Dm = 11.6, 9.4
            pas = Wm / n
            with s.uklad(pos=(0, 8.65, 0), obrot=(11, 0, 0)):
                for i in range(n):
                    x = -Wm / 2.0 + pas * (i + 0.5)
                    kol = kolory[i % len(kolory)]
                    s.blok("Stragan markiza", (x, 0.06 * (i % 2), 0), (pas, 0.4, Dm), kol, "Fabric")
                    if not tani:
                        with s.cechy(cien=False):
                            s.blok("Stragan ząbek", (x, -0.6, Dm / 2.0 + 0.05), (pas - 0.35, 1.0, 0.3), kol, "Fabric")
                s.blok("Stragan markiza rant", (0, -0.25, 0), (Wm + 0.6, 0.25, Dm + 0.6), "tusz")
            _towar(s, towar, 3.75, 2.0, tani)


def _towar(s, towar, y, z, tani):
    """Towar na blacie straganu (y = wierzch blatu, z = środek blatu). 3–4 części."""
    with s.cechy(kolizja=False):
        if towar == "chleby":
            s.blok("Towar chleb", (-3.0, y + 0.7, z), (3.0, 1.4, 1.7), "drewno_jasne", rot=(0, 18, 0))
            s.blok("Towar chleb", (-0.4, y + 0.6, z + 0.2), (2.6, 1.2, 1.5), cien(s, "drewno_jasne"), rot=(0, -12, 0))
            s.klin("Towar ser", (2.6, y + 0.85, z), (2.4, 1.7, 2.2), "zloto", rot=(0, 160, 0))
            if not tani:
                s.blok("Towar ser plaster", (3.9, y + 0.35, z + 0.5), (1.2, 0.7, 1.2), "zloto", rot=(0, 30, 0))
        elif towar == "krysztaly":
            s.blok("Towar kryształ", (-3.0, y + 1.2, z), (1.7, 1.7, 1.7), "dach_sklep", rot=(35, 45, 0))
            s.blok("Towar kryształ", (-1.0, y + 1.0, z + 0.3), (1.3, 1.3, 1.3), "tynk_lawenda", rot=(35, 20, 10))
            s.blok("Towar gwiazdka", (1.8, y + 1.2, z), (2.2, 2.2, 0.5), "zloto", rot=(0, 0, 45))
            if not tani:
                s.blok("Towar gwiazdka", (1.8, y + 1.2, z), (2.2, 2.2, 0.5), "zloto", rot=(0, 0, 0))
        elif towar == "tkaniny":
            s.walec("Towar bela", (-2.8, y + 0.75, z), 0.75, 3.2, "dach_twierdza", os="z")
            s.walec("Towar bela", (-1.0, y + 0.75, z), 0.75, 3.0, "zloto", os="z", rot=(0, 10, 0))
            s.blok("Towar sterta", (2.4, y + 0.6, z), (3.2, 1.2, 2.2), "biel", "Fabric", rot=(0, -8, 0))
            if not tani:
                s.blok("Towar sterta", (2.4, y + 1.45, z), (2.8, 0.6, 2.0), "dach_twierdza", "Fabric", rot=(0, 14, 0))
        elif towar == "klocki":
            s.blok("Towar klocek", (-3.0, y + 0.6, z), (2.4, 1.2, 1.2), "dach_kolo", rot=(0, 15, 0))
            s.blok("Towar klocek", (-0.8, y + 0.6, z + 0.2), (1.2, 1.2, 1.2), "zloto", rot=(0, -20, 0))
            s.blok("Towar klocek", (1.6, y + 0.6, z), (2.4, 1.2, 1.2), "dach_twierdza", rot=(0, 8, 0))
            if not tani:
                s.blok("Towar klocek", (-2.4, y + 1.8, z), (1.2, 1.2, 2.4), "dach_wylegarnia", rot=(0, 30, 6))
        else:                                                  # jabłka i dynie
            s.blok("Towar jabłko", (-3.3, y + 0.7, z + 0.3), (1.4, 1.4, 1.4), "czerwien", rot=(10, 25, 6))
            s.blok("Towar jabłko", (-1.8, y + 0.65, z - 0.3), (1.3, 1.3, 1.3), "czerwien", rot=(-8, 50, 0))
            s.blok("Towar dynia", (1.3, y + 0.95, z), (2.6, 1.9, 2.6), "pomarancz", rot=(0, 20, 0))
            if not tani:
                s.blok("Towar dynia ogonek", (1.3, y + 2.15, z), (0.5, 0.8, 0.5), "lisc_ciemny", rot=(0, 20, 10))


def choragiew(s, pos, kolor="dach_twierdza", kolor2=None, wys=14.0, ry=0.0, dl=6.0, szer=3.4):
    """Chorągiew: maszt 0,6 × wys `tusz` z gałką `zloto`, płat z 3 pasów skręconych kolejno +14° / −26° / +22° (Fabric,
    środkowy w kolorze kolor2, domyślnie ciemniejszy ton) i ogon „jaskółczy” z 2 klinów. Płat wieje ku +X.
    pos = podstawa masztu na ziemi. Kolizję ma maszt. Części: 7."""
    _pal(s)
    k2 = kolor2 or cien(s, kolor, 0.8)
    with s.uklad(pos=pos, obrot=(0, ry, 0)):
        s.blok("Chorągiew maszt", (0, wys / 2.0, 0), (0.6, wys, 0.6), "tusz")
        with s.cechy(kolizja=False):
            s.blok("Chorągiew gałka", (0, wys + 0.35, 0), (1.0, 1.0, 1.0), "zloto", rot=(45, 0, 45))
            with contextlib.ExitStack() as st:
                st.enter_context(s.uklad(pos=(0.3, wys - szer / 2.0 - 0.6, 0)))
                pas = dl / 3.0
                for i, skret in enumerate((14, -26, 22)):
                    st.enter_context(s.uklad(obrot=(0, skret, 0)))
                    s.blok("Chorągiew płat", (pas / 2.0, 0, 0), (pas + 0.15, szer - 0.25 * i, 0.3), kolor if i != 1 else k2, "Fabric")
                    st.enter_context(s.uklad(pos=(pas, 0, 0)))
                h2 = (szer - 0.5) / 2.0
                s.klin("Chorągiew ogon", (0.9, -h2 / 2.0, 0), (0.3, h2, 1.8), kolor, "Fabric", rot=(0, -90, 0))
                s.klin("Chorągiew ogon", (0.9, h2 / 2.0, 0), (0.3, h2, 1.8), kolor, "Fabric", rot=(0, -90, 180))


def choragiewka_duetu(s, pos, kto="rycerz", ry=0.0, przechyl=12.0):
    """Chorągiewka duetu (znak miasteczka, przykazanie 15): maszt 0,4 × 4 `tusz` i trójkąt 3 × 2 z 2 klinów, przechylona
    o `przechyl`° (10–15). kto: "rycerz" (błękit tabardu `dach_twierdza` + `zloto`) albo "kot" (`pomarancz` + `dach_sklep`).
    pos = podstawa masztu (np. na kalenicy albo szczycie wieży); trójkąt wskazuje +X. Bez kolizji. Części: 3."""
    _pal(s)
    k1, k2 = ("dach_twierdza", "zloto") if kto == "rycerz" else ("pomarancz", "dach_sklep")
    with s.uklad(pos=pos, obrot=(0, ry, przechyl)), s.cechy(kolizja=False, cien=False):
        s.blok("Chorągiewka maszt", (0, 2.0, 0), (0.4, 4.0, 0.4), "tusz")
        s.klin("Chorągiewka", (1.7, 3.3 + 0.5, 0), (0.3, 1.0, 3.0), k1, "Fabric", rot=(0, -90, 0))
        s.klin("Chorągiewka", (1.7, 3.3 - 0.5, 0), (0.3, 1.0, 3.0), k2, "Fabric", rot=(0, -90, 180))


def tabliczka_wkrotce(s, pos, ry=0.0):
    """„Wkrótce” bez liter: dwa krzywe słupy z belką, krzywo wisząca tablica `drewno_jasne` z podkładką tusz i złotą
    klepsydrą, a pod nią łańcuch z kłódką rozpięty między słupami — „zamknięte, ale już niedługo”.
    pos = środek między słupami na ziemi; front +Z. Wys. ok. 7,5, szer. ok. 8. Kolizję mają słupy. Części: 18."""
    _pal(s)
    with s.uklad(pos=pos, obrot=(0, ry, 0)):
        for x, k in ((-3.4, 6), (3.4, -5)):
            s.blok("Tabliczka słup", (x, 3.4, 0), (0.8, 7.4, 0.8), "drewno", "Wood", rot=(0, 0, k))
        with s.cechy(kolizja=False):
            s.blok("Tabliczka belka", (0, 7.0, 0), (9.0, 0.8, 1.0), "drewno_ciemne", "Wood", rot=(0, 0, 4))
            with s.uklad(pos=(0.2, 4.6, 0.2), obrot=(0, 0, -8)):
                for x in (-2.2, 2.2):
                    s.blok("Tabliczka łańcuszek", (x, 1.85, 0), (0.3, 1.4, 0.3), "tusz")
                s.blok("Tabliczka", (0, 0, 0.15), (6.0, 3.8, 0.5), "drewno_jasne", "WoodPlanks")
                s.blok("Tabliczka obrys", (0, 0, -0.05), (7.0, 4.8, 0.3), "tusz")
                # klepsydra: dwa trójkąty z klinów (wierzchołkami do siebie) między dwiema belkami
                with s.uklad(pos=(0, 0, 0.55)):
                    for zn in (-1, 1):
                        s.klin("Tabliczka klepsydra", (zn * 0.6, 0.75, 0), (0.4, 1.3, 1.2), "zloto", rot=(0, -zn * 90, 180))
                        s.klin("Tabliczka klepsydra", (zn * 0.6, -0.75, 0), (0.4, 1.3, 1.2), "zloto", rot=(0, -zn * 90, 0))
                    s.blok("Tabliczka klepsydra rama", (0, 1.55, 0), (2.8, 0.4, 0.5), "tusz")
                    s.blok("Tabliczka klepsydra rama", (0, -1.55, 0), (2.8, 0.4, 0.5), "tusz")
            # łańcuch z trzech ogniw zwisający między słupami + kłódka
            for x, y, k in ((-2.2, 2.35, -16), (0.0, 1.85, 0), (2.2, 2.35, 16)):
                s.blok("Tabliczka łańcuch", (x, y, 0.6), (2.4, 0.5, 0.35), "metal_ciemny", rot=(0, 0, k))
            s.blok("Tabliczka kłódka", (0.0, 0.95, 0.75), (1.4, 1.5, 0.6), "zloto")
            s.blok("Tabliczka kłódka pałąk", (0.0, 1.85, 0.75), (0.9, 0.7, 0.4), "tusz")


def dym(s, pos, n=3, skala=1.0, kolor="biel", alfa=0.0, dryf=(0.7, 0.3), ksztalt="kula"):
    """Kłęby dymu albo pary rosnące w górę i odpływające z wiatrem: kule Ø (2,5 + i)·skala co ok. 2,2·skala w górę
    (ksztalt="klocek" = obrócone kostki, tańsze w trójkątach). pos = środek pierwszego kłębu; dryf = przesunięcie (x, z)
    na każdy kolejny kłąb. Bez kolizji i cienia; alfa ≤ 0,3 (PROJEKT: lepiej 0). Części: n."""
    _pal(s)
    x, y, z = pos
    with s.cechy(kolizja=False, cien=False):
        for i in range(n):
            d = (2.5 + 1.0 * i) * skala
            p = (x + dryf[0] * i * skala, y + (2.0 + 0.3 * i) * i * skala, z + dryf[1] * i * skala)
            if ksztalt == "klocek":
                s.blok("Dym", p, (d * 0.8, d * 0.8, d * 0.8), kolor, alfa=alfa, rot=(20 * i + 10, 35 * i, 15))
            else:
                s.kula("Dym", p, d, kolor, alfa=alfa)


def komin(s, pos, segmenty=((4.0, 2.8, 7.0), (3.0, 2.5, -11.0), (2.2, 2.3, 8.0)), kolor=("kamien_cokol", None), mat="Brick",
          czapa="tusz", dym_n=3, ry=0.0, dym_skala=0.8):
    """Komin łamany (przykazanie 1: 8–12° na segment): segmenty = [(wys, bok, kąt_względny°), …] z lamana(), na przemian
    kolor i jego cień (None w krotce = cien(pierwszego)), czapa tusz szersza o 1, dym z `dym_n` kul (Ø 2 / 2,8 / 3,6 przy
    dym_skala 0,8).
    pos = środek podstawy komina (zwykle wpuszczony 1–2 w połać, żeby nie wisiał). Bez kolizji. Części: len(segmenty) + 1 + dym_n."""
    _pal(s)
    kol = [k if k else cien(s, kolor[0]) for k in kolor]
    with s.uklad(pos=pos, obrot=(0, ry, 0)), s.cechy(kolizja=False):
        xe, ye, kat = lamana(s, "Komin", list(segmenty), kol, mat)
        g = segmenty[-1][1]
        s.blok("Komin czapa", (xe, ye + 0.15, 0), (g + 1.0, 0.6, g + 1.0), czapa, rot=(0, 0, kat))
        if dym_n:
            dym(s, (xe + 0.3 * dym_skala, ye + 0.6 + 1.6 * dym_skala, 0.2), dym_n, dym_skala)


# =========================================================================== znaki miasteczka (przykazanie 15)
def lata(s, pos, szer=2.6, wys=2.2, kolor="dach_twierdza", ry=0.0, przechyl=8.0):
    """Łata z fastrygą: prostokąt w kolorze akcentu na licu ściany + 4 szwy tusz 0,3 × 0,8 przechodzące przez jej krawędź.
    pos = środek łaty na licu ściany; lokalne +Z = na zewnątrz. Bez kolizji i cienia. Części: 5."""
    _pal(s)
    with s.uklad(pos=pos, obrot=(0, ry, przechyl)), s.cechy(kolizja=False, cien=False):
        s.blok("Łata", (0, 0, 0.1), (szer, wys, 0.3), kolor)
        for x, y, sx, sy in ((-szer * 0.22, wys / 2.0, 0.3, 0.8), (szer * 0.25, wys / 2.0, 0.3, 0.8),
                             (szer / 2.0, -wys * 0.1, 0.8, 0.3), (-szer * 0.05, -wys / 2.0, 0.3, 0.8)):
            s.blok("Łata szew", (x, y, 0.3), (sx, sy, 0.2), "tusz")


def wypadniety_klocek(s, pos_wneki, pos_ziemi, kolor, ry=0.0, obrot_klocka=22.0, wypustki=True):
    """„Wypadnięty klocek”: ciemna wnęka 2 × 2 na licu ściany (pos_wneki = środek na licu, +Z = na zewnątrz, ry = obrót
    ściany) i ten sam klocek 2 × 1 × 2 w kolorze ściany leżący obok na ziemi (pos_ziemi = środek podstawy, w tym samym
    układzie co wywołujący), obrócony o obrot_klocka° i przechylony 8°, z 2 wypustkami-walcami Ø 0,8.
    Bez kolizji. Części: 4 (bez wypustek 2)."""
    _pal(s)
    with s.cechy(kolizja=False):
        with s.uklad(pos=pos_wneki, obrot=(0, ry, 0)), s.cechy(cien=False):
            s.blok("Klocek wnęka", (0, 0, 0.05), (2.0, 2.0, 0.3), "tusz")
        with s.uklad(pos=pos_ziemi, obrot=(0, ry + obrot_klocka, 8)):
            s.blok("Klocek wypadnięty", (0, 0.4, 0), (2.0, 1.0, 2.0), kolor)
            if wypustki:
                for x in (-0.5, 0.5):
                    s.walec("Klocek wypustka", (x, 1.05, 0), 0.4, 0.4, kolor, os="y")


# =========================================================================== zieleń, kamienie, chmury, płoty
def drzewo_lisciaste(s, pos, rnd=None, skala=1.0, owoce=False, ry=None):
    """Drzewo klockowe: krzywy pień z 2 bloków `drewno` (Wood) 1,8 → 1,4 (+6° / −10°) i korona z 4 brył obróconych do ±12°:
    dół `lisc_ciemny`, środek `lisc`, góra `lisc_jasny` (udawane światło). owoce=True: 3 jabłka-kostki `czerwien` (sad).
    pos = podstawa pnia na ziemi. Wys. ok. 14,5·skala (w mieście ≤ 15). Kolizję ma tylko pień.
    Części: 6 (z owocami 9)."""
    _pal(s)
    r = _rnd(rnd)
    k = skala
    with s.uklad(pos=pos, obrot=(0, r.uniform(0, 360) if ry is None else ry, 0)):
        with s.cechy(kolizja=True):
            xe, ye, _ = lamana(s, "Drzewo pień", [(3.6 * k, 1.8 * k, 6), (3.0 * k, 1.4 * k, -16)], "drewno", "Wood",
                               start=(0.0, -0.3))
        with s.cechy(kolizja=False):
            j = lambda a: r.uniform(-a, a)                    # noqa: E731
            s.blok("Drzewo korona", (xe, ye + 2.2 * k, 0), (8.5 * k, 5.6 * k, 8.5 * k), "lisc_ciemny", rot=(j(6), r.uniform(0, 90), j(6)))
            s.blok("Drzewo korona", (xe - 0.8 * k, ye + 5.3 * k, 0.6 * k), (6.0 * k, 4.6 * k, 6.0 * k), "lisc", rot=(j(10), r.uniform(0, 90), j(10)))
            s.blok("Drzewo korona", (xe + 0.9 * k, ye + 7.9 * k, -0.4 * k), (4.2 * k, 3.4 * k, 4.2 * k), "lisc_jasny", rot=(j(12), r.uniform(0, 90), j(12)))
            s.blok("Drzewo korona", (xe + 3.4 * k, ye + 3.3 * k, 1.8 * k), (3.8 * k, 3.4 * k, 3.8 * k), "lisc", rot=(j(12), r.uniform(0, 90), j(12)))
            if owoce:
                with s.cechy(cien=False):
                    for x, y, z in ((-3.6, 2.0, 2.6), (2.2, 5.0, 2.9), (-1.5, 4.4, -3.4)):
                        s.blok("Drzewo jabłko", (xe + x * k, ye + y * k, z * k), (1.1 * k, 1.1 * k, 1.1 * k), "czerwien", rot=(20, 30, 10))


def drzewo_iglaste(s, pos, rnd=None, skala=1.0, ry=None):
    """Drzewo iglaste (klockowe, tło): pień 1,6 `drewno`, 3 bloki 8 × 4 × 8 / 6 × 4 × 6 / 4 × 4 × 4 skręcone naprzemiennie
    o 45° (dół ciemniejszy: cien(igla)), każdy wyżej o 3,2, czubek — klin narożny `lisc_ciemny` (krzywy wierzchołek).
    pos = podstawa pnia na ziemi. Wys. ok. 17·skala (14–18). Kolizję ma pień. Części: 5."""
    _pal(s)
    r = _rnd(rnd)
    k = skala
    with s.uklad(pos=pos, obrot=(r.uniform(-3, 3), r.uniform(0, 90) if ry is None else ry, r.uniform(-3, 3))):
        s.blok("Iglak pień", (0, 1.6 * k, 0), (1.6 * k, 3.2 * k, 1.6 * k), "drewno", "Wood")
        with s.cechy(kolizja=False):
            for i, (a, kol) in enumerate(((8.0, cien(s, "igla", 0.85)), (6.0, "igla"), (4.0, "igla"))):
                s.blok("Iglak igły", (0, (4.6 + 3.2 * i) * k, 0), (a * k, 4.0 * k, a * k), kol, rot=(0, 45 * i + r.uniform(-6, 6), 0))
            s.naroznik("Iglak czubek", (0, 13.9 * k, 0), (3.2 * k, 4.4 * k, 3.2 * k), "lisc_ciemny", rot=(0, r.uniform(0, 360), 0))


def krzak(s, pos, rnd=None, skala=1.0, jagody=("czerwien", "zloto")):
    """Krzak klockowy: 3 bryły 3,6 / 2,8 / 2,4 (`lisc_ciemny`, `lisc`, `lisc_jasny`) obrócone o 15–40° + 2 jagody 0,8.
    pos = środek na ziemi. Bez kolizji (jagody także bez cienia). Wys. ok. 3,8·skala. Części: 5 (jagody=None: 3)."""
    _pal(s)
    r = _rnd(rnd)
    k = skala
    with s.uklad(pos=pos, obrot=(0, r.uniform(0, 360), 0)), s.cechy(kolizja=False):
        s.blok("Krzak", (0, 1.3 * k, 0), (3.6 * k, 2.8 * k, 3.6 * k), "lisc_ciemny", rot=(r.uniform(-8, 8), r.uniform(15, 40), r.uniform(-8, 8)))
        s.blok("Krzak", (1.3 * k, 1.9 * k, 0.6 * k), (2.8 * k, 2.4 * k, 2.8 * k), "lisc", rot=(r.uniform(10, 25), r.uniform(15, 40), 0))
        s.blok("Krzak", (-0.6 * k, 2.7 * k, -0.4 * k), (2.4 * k, 2.2 * k, 2.4 * k), "lisc_jasny", rot=(0, r.uniform(15, 40), r.uniform(10, 25)))
        if jagody:
            with s.cechy(cien=False):
                s.blok("Krzak jagoda", (1.9 * k, 2.7 * k, 1.6 * k), (0.8, 0.8, 0.8), jagody[0], rot=(30, 30, 0))
                s.blok("Krzak jagoda", (-1.9 * k, 1.6 * k, 1.2 * k), (0.8, 0.8, 0.8), jagody[-1], rot=(0, 45, 30))


def kwiaty(s, pos, ry=0.0, kolory=("czerwien", "zloto")):
    """Kwiaty przy wejściu (≤ 2 na budynek): skrzynka-grządka 4 × 0,6 × 2 `ziemia` z rantem `drewno` i 4 kwiaty-kostki
    1 × 1 × 1 w dwóch kolorach (`czerwien`, `zloto`, `biel`, `dach_sklep`) na łodyżkach `lisc_ciemny`.
    pos = środek grządki na ziemi; dłuższy bok wzdłuż X. Bez kolizji. Części: 7."""
    _pal(s)
    with s.uklad(pos=pos, obrot=(0, ry, 0)), s.cechy(kolizja=False):
        s.blok("Kwiaty skrzynka", (0, 0.35, 0), (4.4, 0.7, 2.4), "drewno")
        s.blok("Kwiaty ziemia", (0, 0.45, 0), (4.0, 0.7, 2.0), "ziemia")
        with s.cechy(cien=False):
            s.blok("Kwiaty łodyżki", (0, 1.2, 0), (3.2, 0.9, 0.6), "lisc_ciemny", rot=(0, 6, 0))
            for i, (x, z, k) in enumerate(((-1.5, 0.3, 20), (-0.5, -0.4, 45), (0.6, 0.35, 10), (1.6, -0.2, 35))):
                s.blok("Kwiat", (x, 1.85 + 0.15 * (i % 2), z), (1.0, 1.0, 1.0), kolory[i % len(kolory)], rot=(15, k, 10))


def kamien(s, pos, rnd=None, rozmiar=3.0, kolor="kamien_cieply", mat="SmoothPlastic", dwa=True, kolizja=True):
    """Kamień fasetowy: niska bryła w ciemniejszym tonie (cien) z jaśniejszym, skośnym wierzchem z klina narożnego
    (udawane światło z góry) i drugi mniejszy kamień-klin obok; całość przechylona 10–20° i wtopiona w ziemię.
    Przy lochach: kolor="kamien_lochu", mat="Slate". pos = środek na ziemi; rozmiar 2–5. Części: 3 (dwa=False: 2)."""
    _pal(s)
    r = _rnd(rnd)
    a = rozmiar
    with s.uklad(pos=pos, obrot=(r.uniform(-14, 14), r.uniform(0, 360), r.choice((-1, 1)) * r.uniform(10, 18))), \
            s.cechy(kolizja=kolizja):
        s.blok("Kamień", (0, a * 0.15, 0), (a, a * 0.55, a * 0.85), cien(s, kolor, 0.8), mat)
        s.naroznik("Kamień wierzch", (0, a * 0.42 + 0.02, 0), (a * 0.9, a * 0.5, a * 0.78), kolor, mat, rot=(0, r.choice((0, 90, 180, 270)), 0))
        if dwa:
            s.klin("Kamień", (a * 0.62, a * 0.1, a * 0.35), (a * 0.5, a * 0.45, a * 0.6), kolor, mat,
                   rot=(0, r.uniform(0, 360), r.uniform(-12, 12)))


def chmura(s, pos, rnd=None, skala=1.0):
    """Chmura: 4 kule Ø 11 / 15 / 13 / 9 `biel` na płaskim spodzie 24 × 3,2 × 8 `tynk_blekit` (spód chmury). pos = środek
    chmury (y 110–150 w mieście). Bez kolizji i cienia. Części: 5 (4 kule)."""
    _pal(s)
    r = _rnd(rnd)
    k = skala
    with s.uklad(pos=pos, obrot=(0, r.uniform(0, 360), 0)), s.cechy(kolizja=False, cien=False):
        for x, y, d in ((-8.0, 0.0, 11.0), (-2.5, 2.2, 15.0), (4.5, 1.0, 13.0), (9.5, -0.6, 9.0)):
            s.kula("Chmura", (x * k, y * k, r.uniform(-1.2, 1.2) * k), d * k, "biel")
        s.blok("Chmura spód", (0.5 * k, -4.5 * k, 0), (24.0 * k, 3.2 * k, 8.0 * k), "tynk_blekit")


def plot(s, punkty, rnd=None, wys=3.0, przeslo=6.0, kolizja=True):
    """Płot wzdłuż łamanej `punkty` = [(x, z), …] na ziemi (y = 0 układu): przęsła ok. `przeslo` długie, w każdym 3 sztachety
    `drewno_jasne` 0,6 × 3 (wysokość ±0,3, przechył ±4°) i 2 żerdzie `drewno`. Kolizję mają sztachety (barierka do
    przeskoczenia, ≤ 6). Części: 5 na przęsło."""
    _pal(s)
    r = _rnd(rnd)
    for (x1, z1), (x2, z2) in zip(punkty, punkty[1:]):
        dl = math.hypot(x2 - x1, z2 - z1)
        n = max(1, int(round(dl / przeslo)))
        kier = math.degrees(math.atan2(x2 - x1, z2 - z1))
        for i in range(n):
            t0, t1 = i / float(n), (i + 1) / float(n)
            ax, az = x1 + (x2 - x1) * t0, z1 + (z2 - z1) * t0
            bx, bz = x1 + (x2 - x1) * t1, z1 + (z2 - z1) * t1
            with s.cechy(kolizja=kolizja):
                for t in (0.17, 0.5, 0.83):
                    h = wys + r.uniform(-0.3, 0.3)
                    with s.uklad(pos=(ax + (bx - ax) * t, 0, az + (bz - az) * t), obrot=(0, kier, r.uniform(-4, 4))):
                        s.blok("Płot sztacheta", (0, h / 2.0 - 0.2, 0), (0.6, h + 0.4, 0.6), "drewno_jasne")
            with s.cechy(kolizja=False):
                for y, dy in ((wys * 0.33, 0.12), (wys * 0.72, -0.12)):
                    s.belka("Płot żerdź", (ax, y + dy, az), (bx, y - dy, bz), 0.45, "drewno", "SmoothPlastic", 0.35)


# =========================================================================== dachy
def dach_czapa(s, dl, gl, wys, kolor, okap=2.5, okap_bok=1.5, podzial=0.62, kalenica=None, rant="tusz", szczyt=None,
               ciemny_tyl=True, kolizja=True):
    """Dach dwuspadowy „czapa”: 2 pełne kliny leżące NA ścianach, kalenica wzdłuż X przesunięta ku tyłowi (połacie różnią
    się o ≥ 10°), okap poziomy z ciemnym rantem pod spodem, jasna albo ciemna kalenica, opcjonalne tynkowane szczyty
    (pasek koloru dachu dookoła działa jak gruba wiatrownica).

    Punkt zaczepienia (0, 0, 0) = środek GÓRNEJ krawędzi ścian; lico frontu w z = +gl/2, tyłu w z = −gl/2, ściany szczytowe
    w x = ±dl/2. wys = wysokość kalenicy nad krawędzią ścian. okap = wysięg poziomy przed front i tył, okap_bok = nad
    szczytami. podzial = część głębokości od kalenicy do frontu (0,62 → kalenica bliżej tyłu, połać frontowa łagodniejsza).
    kalenica = klucz koloru (None → `zloto` dla ciemnych dachów, inaczej `tusz`). szczyt = klucz koloru tynku szczytów
    (None = bez). ciemny_tyl → połać tylna w cien(kolor, 0,85). Kalenicę wzdłuż Z daje obrót wywołującego ry = 90.
    Zwraca dict(kat_przod, kat_tyl, z_kalenicy, wys). Części: 4 (+4 ze szczytami)."""
    _pal(s)
    L = dl + 2 * okap_bok
    zr = gl / 2.0 - podzial * gl
    Pf, Pb = podzial * gl + okap, (1.0 - podzial) * gl + okap
    kf, kb = math.atan2(wys, Pf), math.atan2(wys, Pb)
    kal = kalenica or ("zloto" if kolor in CIEMNE_DACHY else "tusz")
    with s.cechy(kolizja=kolizja):
        s.klin("Dach połać", (0, wys / 2.0, zr + Pf / 2.0), (L, wys, Pf), kolor, rot=(0, 180, 0))
        s.klin("Dach połać", (0, wys / 2.0, zr - Pb / 2.0), (L, wys, Pb), cien(s, kolor, 0.85) if ciemny_tyl else kolor)
    with s.cechy(kolizja=False):
        if rant:
            s.blok("Dach rant", (0, -0.2, 0), (L + 0.5, 0.45, gl + 2 * okap + 0.6), rant)
        s.blok("Dach kalenica", (0, wys - 0.1, zr), (L + 0.6, 0.9, 1.5), kal)
        if szczyt:
            m = 0.9
            for znak in (-1, 1):
                x = znak * (L / 2.0 + 0.15)
                for k, rot, zn in ((kf, (0, 180, 0), 1), (kb, (0, 0, 0), -1)):
                    yt = wys - m / math.cos(k)
                    h = yt - 0.3
                    d = h / math.tan(k)
                    s.klin("Dach szczyt", (x, 0.3 + h / 2.0, zr + zn * d / 2.0), (0.3, h, d), szczyt, rot=rot)
    return {"kat_przod": math.degrees(kf), "kat_tyl": math.degrees(kb), "z_kalenicy": zr, "wys": wys}


# =========================================================================== dom mieszkalny (wzorzec)
KOMIN_DOMU = ((3.6, 2.6, 7.0), (2.6, 2.3, -11.0), (1.8, 2.1, 8.0))
def dom_mieszkalny(s, rnd=None, wariant="a", kolor_dachu="dach_dom_ceglasty", kolor_sciany="tynk_krem", szer=16.0, gl=14.0,
                   wys=26.0, pochyl=1, neon_okna=1, okiennica=None, znak="lata"):
    """Krzywy domek tła wg PROJEKT rozdz. 6: prosty cokół i parter (10,5, pionowy, skręt ±4°), piętro-poddasze (5,5–6)
    z nawisem (front 2, jeden bok 1) przechylone rz 5° i skręcone ry 4–5° w kontrze do parteru, dach-czapa w kontrze
    (abs. −4°, kalenica przesunięta 64/36 → połacie różnią się o ≥ 10°), komin łamany po stronie przeciwnej do nawisu,
    drzwi 6 × 8 przy krawędzi frontu, okna różne (Neon tylko w `neon_okna` z nich, reszta ciemna szyba), znak miasteczka.
    Bryła ma zapas na skręty i portal drzwi: wszystko poniżej 10 mieści się w szer × gl (sprawdzone dla 14–16 × 12–16).

    Punkt zaczepienia: środek obrysu na ziemi = (0, 0, 0), front z drzwiami ku +Z; mieści się w szer × gl (okap i komin
    wystają ≤ 2,5 powyżej 10). wys = wysokość kalenicy (22–28 z tabeli 4.7). pochyl = +1/−1 — strona przechyłu piętra
    (naprzemiennie u sąsiadów; drzwi zawsze po stronie wyższej). wariant:
      "a" — kalenica wzdłuż frontu, nawis z boku, okrągłe okno w szczycie;
      "b" — szczyt do ulicy (kalenica wzdłuż Z), okrągłe okno w trójkącie szczytu, daszek nad drzwiami;
      "c" — jak „a” + wieżyczka narożna (3 walce, hełm-ostrosłup, chorągiewka duetu).
    okiennica = klucz koloru jednej okiennicy (None = kolor dachu). znak = "lata" albo "klocek" (wypadnięty klocek).
    Front węższy niż 12 (parter = szer − 3,7) i wariant „c”: okno parteru przechodzi na bok, front = drzwi + znak.
    Kolizję mają cokół, parter, piętro i połacie (6–7 części). Neon: neon_okna (1–2). Komin + dym sięgają ok. wys + 8.
    Zwraca dict z liczbą części i wysokościami. Części: a 66–67, b 65–66, c 72–73."""
    _pal(s)
    r = _rnd(rnd)
    n0 = len(s.czesci)
    sg = 1 if pochyl >= 0 else -1
    W, D = float(szer), float(gl)
    wb = 3.6 if wariant == "c" else 0.0                        # wariant c: bryła węższa o 3,6, róg oddany wieżyczce
    W0, D0 = W - 3.7 - wb, D - 3.8                            # parter (zapas na skręt, portal drzwi i nawis)
    zp = -0.85                                                 # parter: z od −D/2+1,05 do D/2−2,75
    bok = -sg                                                  # nawis boczny po stronie niższej
    W1, D1 = W0 + 1.5, D0 + 2.0                                # piętro: nawis front 2, bok 1 / 0,5
    x1, z1 = bok * 0.25, 1.0
    H0 = 10.5                                                  # parter z cokołem
    hp1 = 5.5 if wys < 25 else 6.0                             # piętro (poddasze)
    ry0 = 4.0 * r.choice((-1, 1))
    rz1, ry1 = 5.0 * sg, -math.copysign(r.uniform(4.0, 5.0), ry0)   # skręt piętra w kontrze do parteru (R8)
    rz_dach = -9.0 * sg                                        # względem piętra → bezwzględnie −4°·sg (kontra)
    hr = wys - H0 - hp1                                        # wysokość dachu nad piętrem
    okn = okiennica or kolor_dachu
    szyby = ["neon_okno" if i < neon_okna else "woda_gleboka" for i in range(5)]
    r.shuffle(szyby)
    zag2 = (W1 / 2.0) * math.tan(math.radians(abs(rz1))) + 0.1
    with s.uklad(pos=(-bok * wb / 2.0, 0, zp), obrot=(0, ry0, 0)):
        # --- cokół i parter (proste, z kolizją)
        s.blok("Cokół", (0, 0.6, 0), (W0 + 0.8, 1.2, D0 + 0.8), "kamien_cokol", "Cobblestone")
        with s.cechy(kolizja=False):
            s.blok("Cokół rant", (0, 1.25, 0), (W0 + 1.0, 0.4, D0 + 1.0), "tusz")
        s.blok("Parter", (0, H0 / 2.0, 0), (W0, H0, D0), kolor_sciany)
        with s.cechy(kolizja=False):
            for sx in (-1, 1):
                for sz in (-1, 1):
                    s.blok("Narożnik", (sx * (W0 / 2.0 - 0.25), H0 / 2.0 + 0.4, sz * (D0 / 2.0 - 0.25)), (1.2, H0 - 0.6, 1.2), "tusz")
            s.blok("Pas cienia", (0, H0 - 0.75, D0 / 2.0 + 0.05), (W0 - 1.6, 1.3, 0.2), cien(s, kolor_sciany))
        # drzwi po stronie wyższej, okno po drugiej
        okno_z_przodu = wariant != "c" and W0 >= 12.0           # portal drzwi (8) + okno (4,2) mieszczą się obok siebie
        xd = sg * (W0 / 2.0 - 4.3 if okno_z_przodu else 0.6)
        drzwi(s, (xd, 0, D0 / 2.0 + 0.25), 6.0, 8.0, nadproze="drewno" if wariant == "a" else None, przechyl_nadproza=-5 * sg,
              prog="kamien_cokol",
              tanie=(wariant == "c"))
        if okno_z_przodu:
            okno(s, (-sg * (W0 / 2.0 - 2.1), 6.0, D0 / 2.0), 2.6, 3.6, przechyl=6 * sg, swiatlo=szyby[0])
            okno(s, (sg * W0 / 2.0, 6.2, -D0 * 0.1), 2.6, 3.0, przechyl=-5, ry=90 * sg, swiatlo=szyby[1], tanie=True)
        else:                                                  # wąski front: okno parteru na boku
            okno(s, (sg * W0 / 2.0, 6.0, -0.4), 3.0, 3.6, przechyl=6 * sg, ry=90 * sg, swiatlo=szyby[0])
        okno(s, (sg * W0 * 0.15, 6.0, -D0 / 2.0), 3.0, 3.4, przechyl=5, ry=180, swiatlo=szyby[2], tanie=True)
        if wariant == "b":                                     # daszek nad drzwiami
            with s.uklad(pos=(xd, 10.0, D0 / 2.0), obrot=(0, 0, -6 * sg)), s.cechy(kolizja=False):
                s.klin("Daszek", (0, 0.7, 1.0), (8.4, 1.4, 2.0), kolor_dachu, rot=(0, 180, 0))
                s.blok("Daszek rant", (0, -0.15, 1.05), (9.0, 0.4, 2.3), "tusz")
        # znak miasteczka
        if znak == "klocek":
            wypadniety_klocek(s, (-sg * W0 * 0.35, 2.2, D0 / 2.0),(-sg * (W0 / 2.0 - 1.0), 0, D0 / 2.0 + 1.0), kolor_sciany)
        else:
            lata(s, (-W0 / 2.0 * sg, 3.6, D0 * 0.15), 2.6, 2.2, "dach_twierdza" if r.random() < 0.5 else "pomarancz", ry=-90 * sg)

        # --- piętro: nawis, przechył, skręt
        with s.uklad(pos=(x1, H0, z1), obrot=(0, ry1, rz1)):
            with s.cechy(kolizja=False):
                s.blok("Wieniec", (0, (0.8 - zag2 - 0.1) / 2.0, 0), (W1 + 0.6, zag2 + 0.9, D1 + 0.6), "tusz")
            s.blok("Piętro", (0, (hp1 - zag2) / 2.0, 0), (W1, hp1 + zag2, D1), kolor_sciany)
            # dach: kontra względem piętra; kolanko (kolor ściany) wypełnia klin szczeliny nad wyższym końcem
            ext = (W1 / 2.0) * math.sin(math.radians(abs(rz_dach))) + 0.25
            with s.cechy(kolizja=False):
                for sx in (-1, 1):
                    lift = (sx * W1 / 2.0) * math.sin(math.radians(rz_dach))
                    top = hp1 + max(0.0, lift) + 0.2
                    for sz in (-1, 1):
                        s.blok("Narożnik", (sx * (W1 / 2.0 - 0.25), (0.8 + top) / 2.0, sz * (D1 / 2.0 - 0.25)), (1.2, top - 0.8, 1.2), "tusz")
            # okna piętra
            yo = 0.8 + (hp1 - 0.8) * 0.5
            okno(s, (sg * W1 * 0.24, yo, D1 / 2.0), 2.8, 2.8, przechyl=-7 * sg, swiatlo=szyby[3],
                 okiennica=okn if wariant != "c" else None, strona_okiennicy=sg)
            if wariant != "b":
                okno(s, (-sg * W1 * 0.2, yo + 0.2, D1 / 2.0), 2.8, ksztalt="okragle", swiatlo=szyby[4])
            # dach
            with s.uklad(pos=(0, hp1, 0), obrot=(0, 0, rz_dach)):
                with s.cechy(kolizja=False):
                    s.blok("Kolanko", (0, -ext / 2.0 + 0.05, 0), (W1 - 0.8, ext, D1 - 0.8), kolor_sciany)
                if wariant == "b":
                    with s.uklad(obrot=(0, 90, 0)):
                        info = dach_czapa(s, D1, W1, hr + 0.6, kolor_dachu, okap=2.0, okap_bok=1.2, podzial=0.6,
                                          szczyt=kolor_sciany)
                    # szczyt frontowy jest teraz po stronie +Z: okrągłe okno w trójkącie
                    zf = D1 / 2.0 + 1.2 + 0.3
                    xk = W1 / 2.0 - 0.6 * W1                   # oś kalenicy po obrocie (z' → x)
                    okno(s, (xk + 0.4 * sg, hr * 0.32, zf), 2.6, ksztalt="okragle", swiatlo=szyby[4], przechyl=8)
                    komin(s, (-bok * W1 * 0.3, hr * 0.35, -D1 * 0.25), KOMIN_DOMU, ("kamien_cokol", None), dym_n=2)
                else:
                    info = dach_czapa(s, W1, D1, hr, kolor_dachu, okap=2.0, okap_bok=1.2, podzial=0.64, szczyt=kolor_sciany)
                    with s.uklad(pos=(-bok * (W1 / 2.0 + 1.2 + 0.3), hr * 0.3, info["z_kalenicy"] + 0.6), obrot=(0, 90 * (-bok), 0)):  # okienko w bocznym szczycie
                        okno(s, (0, 0, 0), 2.2, ksztalt="okragle", swiatlo="woda_gleboka", tanie=True)
                    zk = info["z_kalenicy"] - (1 - 0.64) * D1 * 0.45
                    yk = hr * (1 - 0.45 * (1 - 0.64) * D1 / ((1 - 0.64) * D1 + 2.0)) - 1.6
                    komin(s, (-bok * W1 * 0.3, yk, zk), KOMIN_DOMU, ("kamien_cokol", None), dym_n=2)
    if wariant == "c":                                         # wieżyczka narożna (prosta do 10, wyżej krzywa)
        xt, zt = bok * (W / 2.0 - 2.95), D / 2.0 - 2.95
        rt = r.uniform(0, 30)
        with s.uklad(pos=(xt, 0, zt)):
            s.walec("Wieżyczka", (0, 6.0, 0), 2.6, 12.0, cien(s, kolor_sciany, 0.92), os="y")
            with s.cechy(kolizja=False):
                s.walec("Wieżyczka cokół", (0, 0.6, 0), 2.85, 1.2, "kamien_cokol", "Cobblestone", os="y")
                s.walec("Wieżyczka gzyms", (0, 12.1, 0), 3.0, 0.6, "tusz", os="y")
                with s.uklad(pos=(0, 12.0, 0), obrot=(0, rt, -6 * bok)):
                    ht = max(4.0, wys - 12.0 - 4.0)
                    s.walec("Wieżyczka", (0, ht / 2.0 + 0.1, 0), 2.2, ht, kolor_sciany, os="y")
                    s.walec("Wieżyczka gzyms", (0, ht + 0.3, 0), 2.9, 0.6, "tusz", os="y")
                    with s.uklad(obrot=(0, -rt, 0)):            # okienko zawsze ku frontowi
                        okno(s, (0, ht * 0.5, 2.15), 1.8, ksztalt="okragle", tanie=True,
                             swiatlo="neon_okno" if neon_okna > 1 else "woda_gleboka")
                    with s.uklad(pos=(0, ht + 0.55, 0), obrot=(0, 45, 8 * bok)):
                        s.ostroslup("Wieżyczka hełm", (0, 0, 0), 2.8, 2.8, 6.5, kolor_dachu)
                        s.blok("Wieżyczka gałka", (-0.0, 6.4, 0), (0.9, 0.9, 0.9), "zloto", rot=(45, 0, 45))
                        choragiewka_duetu(s, (0, 6.6, 0), "kot" if bok > 0 else "rycerz", ry=-45)
    return {"czesci": len(s.czesci) - n0, "wys": wys, "dach": hr}
