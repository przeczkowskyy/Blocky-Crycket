# -*- coding: utf-8 -*-
"""PÓŁBÓG — rasa postaci (D-080, D-104) z rzutu assets/processed/RaceTurnarounds/polbog.jpg: ciało „czlowiek” w stroju bazowym.

Złota skóra, świecąca aureola nad głową (pierścień z dwunastu belek, pochylony do przodu), jasne falowane
włosy do karku (akcesorium rasa_polbog_wlosy — hełm je chowa), świecące niebieskie oczy bez źrenic, lniana
koszula, białe spodenki ze złotą lamówką, brązowe buty. Świecenie oczu i aureoli to emisja w teksturze-palecie.
Klocki, kości, zaczepy i klipy (idle, chod, wiwat) są te same co u gołego Rycerza, więc każdy przedmiot
„czlowiek” pasuje. Wygląd premium zależy od pytania 47 (D-080).
Wspólny kod i dane wszystkich ras: swiat/postacie/rasy.py; opis, wybory i pytania: swiat/postacie/RASY.md.

    python -B swiat/postacie/przebuduj.py rasa_polbog --bez-filmow
    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/rasa_polbog.py --wyj <folder>

  zbuduj()     [Półbóg w stroju bazowym (id „rasa_polbog”), poza spoczynku]
  cialo()      to samo ciało jako „rasa_polbog_cialo” (z zaczepy_ekwipunku=True: + 15 zaczepów Ekw<Kosc>Attachment)
  warianty()   przymiarki dla przebuduj.py: strój bazowy, komplet Rycerza, komplet Zwiadowcy (wynik/…/ekwipunek/)
  po_przebudowie()  plansza porównawcza z rzutem i plansza skali (rasy_plansze.py)
Status: propozycja (nie kanon) — do oceny przez Karola i Pawła.
"""
import os
import sys

if __name__ == "__main__":                                       # uruchomienie wprost: korzeń repozytorium na ścieżce
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from swiat.postacie import rasy

RASA = "polbog"
ID = rasy.id_rasy(RASA)
NAZWA = rasy.RASY[RASA]["nazwa"]
CIALO_TYP = rasy.CIALO_TYP
STROJE = rasy.STROJE
NAZWY_STROJOW = rasy.NAZWY_STROJOW
PLANSZA_ZBIORCZA = rasy.PLANSZA_ZBIORCZA


def cialo(zaczepy_ekwipunku=False):
    """Ciało rasy „rasa_polbog_cialo” z klipami idle, chod, wiwat (skopiowane z ciała odniesienia człowieka)."""
    return rasy.cialo(RASA, zaczepy_ekwipunku)


def przedmioty():
    """Rasa nie ma własnych przedmiotów (włosy to akcesorium ciała); przymiarki biorą przedmioty bohaterów."""
    return []


def stroj(nazwa):
    """Półbóg w stroju ze STROJE: postać „rasa_polbog_<strój>”."""
    return rasy.stroj(RASA, nazwa)


def zbuduj():
    """[Półbóg w stroju bazowym (id „rasa_polbog”)] — ten sam kształt co inne moduły postaci."""
    return [rasy.model(RASA)]


def warianty(rodzaj="plansze"):
    """Modele dla przebuduj.py (wynik/rasa_polbog/ekwipunek/): przymiarki albo ciało z zaczepami Ekw…"""
    return rasy.warianty(RASA, rodzaj)


def ekwipunek_json():
    return rasy.ekwipunek_json(RASA)


def po_przebudowie(cel):
    """Po ułożeniu wynik/rasa_polbog/: plansza porównawcza z rzutem i plansza skali (zwraca nazwy plików)."""
    from swiat.postacie import rasy_plansze
    return rasy_plansze.po_przebudowie(RASA, cel)


SLABOSCI = rasy.slabosci(RASA) + [
    "Półbóg względem rzutu: poświata wokół całej postaci nie jest oddana (to efekt do zrobienia w grze), włosy "
    "to kanciaste fale z klocków, aureola jest pierścieniem z dwunastu belek. Świecenie oczu i aureoli to emisja "
    "w teksturze-palecie — w grze trzeba ją podpiąć (albo Neon / PointLight).",
    "Półbóg w przymiarkach: środek aureoli wisi 0,68 studa nad głową — przód pierścienia jest 0,05 studa nad "
    "grzebieniem hełmu Rycerza, a kaptur Zwiadowcy sięga najwyżej do poziomu przodu pierścienia i go nie dotyka "
    "(RASY.md pkt 8); hełm i kaptur chowają włosy w całości. W rękawicach Zwiadowcy dłonie mają kolor skóry "
    "człowieka.",
]


if __name__ == "__main__":
    p = zbuduj()[0]
    print("%s: %d kości, %d brył, %d zaczepów, klipy: %s, skala rasy %.2f"
          % (p.id, len(p.kosci), len(p.czesci), len(p.zaczepy), ", ".join(k.nazwa for k in p.klipy), p.skala_rasy))
