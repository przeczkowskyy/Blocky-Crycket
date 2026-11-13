# -*- coding: utf-8 -*-
"""WZÓR modułu budynku mapy v2 „Krzywe Miasteczko” — mała budka kartografa (nie stoi w mieście; to ściąga dla budowniczych).

Konwencja (PROJEKT.md rozdz. 5.0):
- stałe modułu: NAZWA (nazwa grupy, ASCII PascalCase), OBRYS = (szer, gl) działki; tu także WYSOKOSC, BUDZET, INTERAKCJA;
- buduj(s, rnd) buduje wokół (0, 0, 0) = środek działki na ziemi, front z wejściem ku +Z, działka x ∈ ±szer/2, z ∈ ±gl/2;
  okapy i szyld mogą wystawać ≤ 2,5 i tylko powyżej 10 nad ziemią;
- bez własnej grupy głównej i bez przesuwania/obracania całości — robi to generator (jeden budynek = jedna grupa);
  jedyna podgrupa to techniczny punkt interakcji „<NAZWA>/_Interakcja” (zestaw.punkt_interakcji);
- kolory tylko kluczami palety (paleta.py) albo cien(s, klucz); dekoracje w s.cechy(kolizja=False), drobiazgi także cien=False;
- elementy powtarzalne bierzemy z zestaw.py (okno, drzwi, dach_czapa, komin, latarnia, beczka, skrzynia, łata…);
- rnd tylko do drobnej losowości (wynik powtarzalny).

Podgląd:  python -B swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/_wzor.py --wyj <folder> --szer 1000
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402

NAZWA = "WzorBudka"
OBRYS = (14, 12)                 # szer (lokalne X) × gł (lokalne Z)
WYSOKOSC = 21                    # szczyt dachu; komin z dymem wyżej
BUDZET = 140                     # twardy limit części
INTERAKCJA = (1.5, 10.0)         # punkt lokalny (x, z): 4 study przed krawędzią działki, na osi drzwi
OBRYS_SYLWETKI = False           # PROJEKT 5.0 p. 4: nie wołamy s.obrys_sylwetki() — Highlight w budynkach zakazany,
                                 # obrys robimy z klocków (tusz); flaga zostaje, gdyby Game Director zdecydował inaczej

SCIANA, DACH = "tynk_brzoskwinia", "dach_dom_ceglasty"


def buduj(s, rnd):
    W0, D0, zp = 10.0, 8.0, -0.5                               # parter 10 × 8, front w z = +3,5
    H0 = 11.5                                                  # parter 11–12 (przykazanie 3/4); dach w kontrze nie schodzi poniżej 10
    with s.uklad(pos=(0, 0, zp), obrot=(0, 4, 0)):            # parter prosty (przykazanie 3), tylko skręt ry
        # --- bryła: cokół, parter, narożniki tuszem (kolizję mają cokół i ściany)
        s.blok("Cokół", (0, 0.6, 0), (W0 + 0.8, 1.2, D0 + 0.8), "kamien_cokol", "Cobblestone")
        with s.cechy(kolizja=False):
            s.blok("Cokół rant", (0, 1.25, 0), (W0 + 1.0, 0.4, D0 + 1.0), "tusz")
        s.blok("Parter", (0, H0 / 2.0, 0), (W0, H0, D0), SCIANA)
        with s.cechy(kolizja=False):
            for sx in (-1, 1):
                for sz in (-1, 1):
                    s.blok("Narożnik", (sx * (W0 / 2.0 - 0.25), H0 / 2.0 + 0.4, sz * (D0 / 2.0 - 0.25)), (1.3, H0 - 0.6, 1.3), "tusz")
            s.blok("Pas cienia", (0, H0 - 0.75, D0 / 2.0 + 0.05), (W0 - 1.6, 1.3, 0.2), cien(s, SCIANA))
        # --- otwory: drzwi przesunięte od osi (20 % szerokości), okno po drugiej stronie, okrągłe okno z boku
        zestaw.drzwi(s, (1.5, 0, D0 / 2.0 + 0.25), 6.0, 8.0, przechyl_nadproza=-5)
        zestaw.okno(s, (-2.5, 6.4, D0 / 2.0), 2.8, 3.4, przechyl=6)
        zestaw.okno(s, (W0 / 2.0, 6.4, -0.8), 2.4, ksztalt="okragle", przechyl=0, ry=90, swiatlo="woda_gleboka")
        zestaw.lata(s, (-W0 / 2.0, 4.0, 1.0), 2.4, 2.0, "pomarancz", ry=-90)
        zestaw.wypadniety_klocek(s, (-W0 / 2.0 + 1.6, 2.2, D0 / 2.0), (-W0 / 2.0 + 0.8, 0, D0 / 2.0 + 0.8), SCIANA)
        # --- dach-czapa w kontrze: przechył −7°; kolanko (kolor ściany) zakrywa szczelinę nad wyższym końcem ścian
        with s.uklad(pos=(0, H0, 0), obrot=(0, 0, -7)):
            with s.cechy(kolizja=False):
                s.blok("Kolanko", (0, -0.55, 0), (W0 - 0.8, 1.2, D0 - 0.8), SCIANA)
            info = zestaw.dach_czapa(s, W0, D0, 9.0, DACH, okap=2.2, okap_bok=1.6, podzial=0.64, szczyt=SCIANA)
            zestaw.komin(s, (-2.6, 3.4, info["z_kalenicy"] - 1.6), kolor=("kamien_cokol", None))
            zestaw.choragiewka_duetu(s, (3.5, 9.2, info["z_kalenicy"]), "kot", przechyl=-12)
            # --- szyld-rekwizyt: zwój mapy oparty o połać frontową po prawej, wystaje ponad okap i za narożnik
            #     (≥ 25 % poza bryłą), przechył 12° w bok i 14° ku ulicy; skala 0,85 (odstępy warstw ≥ 0,085)
            with s.uklad(pos=(2.6, 3.0, D0 / 2.0 + 1.5), obrot=(-14, -12, 12), skala=0.85), s.cechy(kolizja=False):
                _szyld_mapa(s)
    # --- rekwizyty przy wejściu (trójka duży–średni–mały) — wszystko w działce
    zestaw.beczka(s, (5.0, 0, 3.6), "woda", przechyl=(0, 6))
    zestaw.skrzynia(s, (5.0, 0, 0.0), ry=12, dl=3.0, a=2.6, przechyl=9)
    zestaw.kwiaty(s, (-2.4, 0, 4.4), ry=4, kolory=("czerwien", "biel"))
    # latarni tu nie ma: klatka latarni (romb 2,8) nie mieści się w działce 14 × 12 obok ściany — latarnie stawia generator
    zestaw.punkt_interakcji(s, NAZWA, INTERAKCJA)
    if OBRYS_SYLWETKI:
        s.obrys_sylwetki()


def _szyld_mapa(s):
    """Zwój mapy 9 × 6 w płaszczyźnie XY (front +Z): arkusz `biel` z płetwą tusz, zwinięte końce, czerwony krzyżyk-cel
    i kropkowana ścieżka. 12 części."""
    for i, (x, k) in enumerate(((-2.2, 6.0), (2.2, -6.0))):    # arkusz z 2 płatów lekko zgiętych (jak papier)
        s.blok("Mapa arkusz", (x, 0, 0.1 * i), (4.6, 5.6, 0.4), "biel", rot=(0, k, 0))
    s.blok("Mapa płetwa", (0, 0, -0.35), (9.8, 6.4, 0.3), "tusz")
    for x in (-4.6, 4.6):
        s.walec("Mapa zwój", (x, 0, 0.0), 0.75, 6.6, "drewno_jasne", os="y")
    with s.cechy(cien=False):
        for k in (45, -45):
            s.blok("Mapa cel", (2.0, 0.8, 0.55), (2.4, 0.6, 0.3), "czerwien", rot=(0, 0, k))
        for x, y in ((-2.8, -1.6), (-1.5, -0.9), (-0.3, -1.4), (0.9, -0.3)):
            s.blok("Mapa ścieżka", (x, y, 0.45), (0.6, 0.6, 0.3), "tusz", rot=(0, 0, 30))
