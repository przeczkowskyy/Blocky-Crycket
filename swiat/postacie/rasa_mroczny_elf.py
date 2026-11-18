# -*- coding: utf-8 -*-
"""MROCZNY ELF — rasa postaci (D-079, D-104) z rzutu assets/processed/RaceTurnarounds/mroczny_elf.jpg: ciało „czlowiek” w stroju bazowym.

Te same bryły co elf (rasy.py: twarz „lagodna”, długie uszy, długie włosy) w innej palecie: skóra
lawendowo-szara, długie srebrne włosy do łopatek z przedziałkiem (akcesorium rasa_mroczny_elf_wlosy — hełm je
chowa), fioletowe oczy, lniana koszula, fioletowe spodenki, brązowe buty. Klocki, kości, zaczepy i klipy (idle,
chod, wiwat) są te same co u gołego Rycerza, więc każdy przedmiot „czlowiek” pasuje.
Wspólny kod i dane wszystkich ras: swiat/postacie/rasy.py; opis, wybory i pytania: swiat/postacie/RASY.md.

    python -B swiat/postacie/przebuduj.py rasa_mroczny_elf --bez-filmow
    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/rasa_mroczny_elf.py --wyj <folder>

  zbuduj()     [Mroczny elf w stroju bazowym (id „rasa_mroczny_elf”), poza spoczynku]
  cialo()      to samo ciało jako „rasa_mroczny_elf_cialo” (z zaczepy_ekwipunku=True: + 15 zaczepów Ekw<Kosc>Attachment)
  warianty()   przymiarki dla przebuduj.py: strój bazowy, komplet Rycerza, komplet Zwiadowcy (wynik/…/ekwipunek/)
  po_przebudowie()  plansza porównawcza z rzutem i plansza skali (rasy_plansze.py)
Status: propozycja (nie kanon) — do oceny przez Karola i Pawła.
"""
import os
import sys

if __name__ == "__main__":                                       # uruchomienie wprost: korzeń repozytorium na ścieżce
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from swiat.postacie import rasy

RASA = "mroczny_elf"
ID = rasy.id_rasy(RASA)
NAZWA = rasy.RASY[RASA]["nazwa"]
CIALO_TYP = rasy.CIALO_TYP
STROJE = rasy.STROJE
NAZWY_STROJOW = rasy.NAZWY_STROJOW
PLANSZA_ZBIORCZA = rasy.PLANSZA_ZBIORCZA


def cialo(zaczepy_ekwipunku=False):
    """Ciało rasy „rasa_mroczny_elf_cialo” z klipami idle, chod, wiwat (skopiowane z ciała odniesienia człowieka)."""
    return rasy.cialo(RASA, zaczepy_ekwipunku)


def przedmioty():
    """Rasa nie ma własnych przedmiotów (włosy to akcesorium ciała); przymiarki biorą przedmioty bohaterów."""
    return []


def stroj(nazwa):
    """Mroczny elf w stroju ze STROJE: postać „rasa_mroczny_elf_<strój>”."""
    return rasy.stroj(RASA, nazwa)


def zbuduj():
    """[Mroczny elf w stroju bazowym (id „rasa_mroczny_elf”)] — ten sam kształt co inne moduły postaci."""
    return [rasy.model(RASA)]


def warianty(rodzaj="plansze"):
    """Modele dla przebuduj.py (wynik/rasa_mroczny_elf/ekwipunek/): przymiarki albo ciało z zaczepami Ekw…"""
    return rasy.warianty(RASA, rodzaj)


def ekwipunek_json():
    return rasy.ekwipunek_json(RASA)


def po_przebudowie(cel):
    """Po ułożeniu wynik/rasa_mroczny_elf/: plansza porównawcza z rzutem i plansza skali (zwraca nazwy plików)."""
    from swiat.postacie import rasy_plansze
    return rasy_plansze.po_przebudowie(RASA, cel)


SLABOSCI = rasy.slabosci(RASA) + [
    "Mroczny elf względem rzutu: te same bryły co elf, więc te same uproszczenia — włosy z płaskich brył bez "
    "fal, uszy to ostrosłupy 0,92 studa. Na rzucie oczy są węższe (przymknięte) niż u elfa; model ma oczy elfa "
    "w fiolecie.",
    "Mroczny elf w przymiarkach: jak elf — hełm i kaptur chowają długie włosy w całości, uszy przechodzą przez "
    "ścianki hełmu i kaptura, bez kaptura tył włosów przecina kołczan Zwiadowcy. W rękawicach Zwiadowcy dłonie "
    "mają kolor skóry człowieka (przy lawendowej skórze widać to wyraźnie).",
]


if __name__ == "__main__":
    p = zbuduj()[0]
    print("%s: %d kości, %d brył, %d zaczepów, klipy: %s, skala rasy %.2f"
          % (p.id, len(p.kosci), len(p.czesci), len(p.zaczepy), ", ".join(k.nazwa for k in p.klipy), p.skala_rasy))
