# -*- coding: utf-8 -*-
"""Wspólne kawałki pięciu petów z leśnego jajka (próba „jajka i pety”, swiat/pety_proba, 17.11.2026, propozycja).

To NIE jest model — moduły modeli to zoledziak.py, mchowy_slimak.py, lisciolis.py, swietlikowka.py, jelonek_gaju.py
i jajko_lesne.py. Tu są tylko:
  • klip_wyklucie(p, kosc, …)  — 30 kl. bez pętli: pet siedzi w jajku (kość głównego ciała niżej), wyskakuje
    z obrotem wokół pionu, ląduje z przysiadem; w grze gra go klient po pęknięciu jajka;
  • klip_radosc(p, kosc, …)    — 36 kl. bez pętli: przysiad, podskok z obrotem, lądowanie (po wykluciu, po wyborze
    peta w zagrodzie, gdy gracz skacze);
  • oczy(p, …)                 — duże „błyszczące” oczy z odblaskiem (2–3 bryły na oko), wspólny styl petów.
Klipy nie mają kanału skali (Roblox przenosi tylko położenie i obrót kości). Obrót 360° wokół pionu kończy się
w tej samej pozie co spoczynek, więc przejście do następnego klipu jest bez szwu.
"""

WYKLUCIE_KLATEK = 30
RADOSC_KLATEK = 36


def klip_wyklucie(p, kosc, glebokosc=0.9, wyskok=0.9, obrot=360.0, dodatki=None):
    """Wyklucie: kl. 0–5 w jajku (przes. w dół o `glebokosc`), kl. 12 najwyżej (`wyskok`) w pół obrotu,
    kl. 18 ląduje, kl. 21 przysiad, kl. 25 odbicie, kl. 30 spoczynek. dodatki(k) dopisuje ruchy innych kości."""
    k = p.klip("wyklucie", WYKLUCIE_KLATEK, petla=False)
    k.klucz(0, kosc, przes=(0, -glebokosc, 0), obrot=(0, 0, 0))
    k.klucz(5, kosc, przes=(0, -glebokosc * 0.7, 0), obrot=(-8, 0, 0))
    k.klucz(12, kosc, przes=(0, wyskok, 0), obrot=(6, obrot * 0.55, 0))
    k.klucz(18, kosc, przes=(0, 0.05, 0), obrot=(0, obrot, 0))
    k.klucz(21, kosc, przes=(0, -0.09, 0), obrot=(4, obrot, 0))
    k.klucz(25, kosc, przes=(0, 0.04, 0), obrot=(-2, obrot, 0))
    k.klucz(30, kosc, przes=(0, 0, 0), obrot=(0, obrot, 0))
    if dodatki:
        dodatki(k)
    return k


def klip_radosc(p, kosc, wysokosc=0.7, obrot=360.0, dodatki=None):
    """Radość: kl. 0 spoczynek, kl. 6 przysiad, kl. 15 najwyżej w pół obrotu, kl. 24 lądowanie, kl. 28 przysiad,
    kl. 36 spoczynek (obrót pełny — ta sama poza co na początku)."""
    k = p.klip("radosc", RADOSC_KLATEK, petla=False)
    k.klucz(0, kosc, przes=(0, 0, 0), obrot=(0, 0, 0))
    k.klucz(6, kosc, przes=(0, -0.1, 0), obrot=(6, 0, 0))
    k.klucz(15, kosc, przes=(0, wysokosc, 0), obrot=(-8, obrot * 0.5, 0))
    k.klucz(24, kosc, przes=(0, 0.02, 0), obrot=(0, obrot, 0))
    k.klucz(28, kosc, przes=(0, -0.08, 0), obrot=(5, obrot, 0))
    k.klucz(36, kosc, przes=(0, 0, 0), obrot=(0, obrot, 0))
    if dodatki:
        dodatki(k)
    return k


def oczy(p, x, y, z, szer=0.26, wys=0.32, kolor="tusz", teczowka=None, odstep=None):
    """Para oczu na ścianie z = `z` (układ bieżącego bloku `p.na`): czarne (albo `teczowka` z czarną źrenicą) z białym
    odblaskiem u góry od strony środka twarzy. x = odległość środka oka od osi."""
    for zn, s in ((1, "L"), (-1, "P")):
        if teczowka:
            p.blok("Teczowka " + s, (zn * x, y, z + 0.02), (szer, wys, 0.05), teczowka, "swiecacy", faza=0.02)
            p.blok("Zrenica " + s, (zn * x, y - 0.02, z + 0.05), (szer * 0.5, wys * 0.62, 0.04), kolor, "polysk",
                   faza=0.0)
        else:
            p.blok("Oko " + s, (zn * x, y, z + 0.02), (szer, wys, 0.05), kolor, "polysk", faza=0.03)
        p.blok("Blysk " + s, (zn * x - zn * szer * 0.2, y + wys * 0.22, z + 0.075), (szer * 0.36, wys * 0.3, 0.03),
               "bialy", "swiecacy", faza=0.0)
