# -*- coding: utf-8 -*-
"""GOBLIN — rasa postaci (D-079, D-104) z rzutu assets/processed/RaceTurnarounds/goblin.jpg: ciało „czlowiek” w stroju bazowym.

Według pierwszego rzutu (goblin.jpg): żółtozielona skóra, głowa-klocek bez włosów, wielkie uszy na boki,
grube skośne brwi, małe czarne oczy, długi nos z żółtawym czubkiem opadający nad usta, szeroki uśmiech z rzędem
zębów, lniana koszula, pomarańczowe spodenki, brązowe buty. Klocki, kości, zaczepy i klipy (idle, chod, wiwat) są
te same co u gołego Rycerza, więc każdy przedmiot „czlowiek” pasuje; mały wzrost to skala rasy 0,88 (dana,
niewypieczona w klocki — plansza rasa_goblin_skala.jpg).
Wspólny kod i dane wszystkich ras: swiat/postacie/rasy.py; opis, wybory i pytania: swiat/postacie/RASY.md.

    python -B swiat/postacie/przebuduj.py rasa_goblin --bez-filmow
    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/rasa_goblin.py --wyj <folder>

  zbuduj()     [Goblin w stroju bazowym (id „rasa_goblin”), poza spoczynku]
  cialo()      to samo ciało jako „rasa_goblin_cialo” (z zaczepy_ekwipunku=True: + 15 zaczepów Ekw<Kosc>Attachment)
  warianty()   przymiarki dla przebuduj.py: strój bazowy, komplet Rycerza, komplet Zwiadowcy (wynik/…/ekwipunek/)
  po_przebudowie()  plansza porównawcza z rzutem i plansza skali (rasy_plansze.py)
Status: propozycja (nie kanon) — do oceny przez Karola i Pawła.
"""
import os
import sys

if __name__ == "__main__":                                       # uruchomienie wprost: korzeń repozytorium na ścieżce
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from swiat.postacie import rasy

RASA = "goblin"
ID = rasy.id_rasy(RASA)
NAZWA = rasy.RASY[RASA]["nazwa"]
CIALO_TYP = rasy.CIALO_TYP
STROJE = rasy.STROJE
NAZWY_STROJOW = rasy.NAZWY_STROJOW
PLANSZA_ZBIORCZA = rasy.PLANSZA_ZBIORCZA


def cialo(zaczepy_ekwipunku=False):
    """Ciało rasy „rasa_goblin_cialo” z klipami idle, chod, wiwat (skopiowane z ciała odniesienia człowieka)."""
    return rasy.cialo(RASA, zaczepy_ekwipunku)


def przedmioty():
    """Rasa nie ma własnych przedmiotów (włosy to akcesorium ciała); przymiarki biorą przedmioty bohaterów."""
    return []


def stroj(nazwa):
    """Goblin w stroju ze STROJE: postać „rasa_goblin_<strój>”."""
    return rasy.stroj(RASA, nazwa)


def zbuduj():
    """[Goblin w stroju bazowym (id „rasa_goblin”)] — ten sam kształt co inne moduły postaci."""
    return [rasy.model(RASA)]


def warianty(rodzaj="plansze"):
    """Modele dla przebuduj.py (wynik/rasa_goblin/ekwipunek/): przymiarki albo ciało z zaczepami Ekw…"""
    return rasy.warianty(RASA, rodzaj)


def ekwipunek_json():
    return rasy.ekwipunek_json(RASA)


def po_przebudowie(cel):
    """Po ułożeniu wynik/rasa_goblin/: plansza porównawcza z rzutem i plansza skali (zwraca nazwy plików)."""
    from swiat.postacie import rasy_plansze
    return rasy_plansze.po_przebudowie(RASA, cel)


SLABOSCI = rasy.slabosci(RASA) + [
    "Goblin względem rzutu: cienkie ręce i nogi oraz duża głowa na małym ciele NIE są oddane — klocki ciała są "
    "takie jak u człowieka (żeby pasował ekwipunek); mały wzrost niesie tylko skala 0,88 z danych rasy. Nos to "
    "trzy klocki (nasada, grzbiet, czubek), bez haczykowatego łuku z rysunku; zęby to prosty rząd.",
    "Goblin w przymiarkach: wielkie uszy przechodzą przez ścianki hełmu Rycerza i kaptura Zwiadowcy i wystają "
    "daleko poza nie, a nos wystaje przed hełm (liczby w RASY.md pkt 8). W rękawicach Zwiadowcy dłonie mają "
    "kolor skóry człowieka.",
]


if __name__ == "__main__":
    p = zbuduj()[0]
    print("%s: %d kości, %d brył, %d zaczepów, klipy: %s, skala rasy %.2f"
          % (p.id, len(p.kosci), len(p.czesci), len(p.zaczepy), ", ".join(k.nazwa for k in p.klipy), p.skala_rasy))
