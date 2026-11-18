# -*- coding: utf-8 -*-
"""ELF — rasa postaci (D-079, D-104) z rzutu assets/processed/RaceTurnarounds/elf.jpg: ciało „czlowiek” w stroju bazowym.

Jasna skóra, długie spiczaste uszy na boki, długie złote włosy do łopatek z przedziałkiem (akcesorium
rasa_elf_wlosy — hełm je chowa), zielone oczy, lniana koszula, jasnozielone spodenki, brązowe buty. Klocki, kości,
zaczepy i klipy (idle, chod, wiwat) są te same co u gołego Rycerza, więc każdy przedmiot „czlowiek” pasuje.
Wspólny kod i dane wszystkich ras: swiat/postacie/rasy.py; opis, wybory i pytania: swiat/postacie/RASY.md.

    python -B swiat/postacie/przebuduj.py rasa_elf --bez-filmow
    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/rasa_elf.py --wyj <folder>

  zbuduj()     [Elf w stroju bazowym (id „rasa_elf”), poza spoczynku]
  cialo()      to samo ciało jako „rasa_elf_cialo” (z zaczepy_ekwipunku=True: + 15 zaczepów Ekw<Kosc>Attachment)
  warianty()   przymiarki dla przebuduj.py: strój bazowy, komplet Rycerza, komplet Zwiadowcy (wynik/…/ekwipunek/)
  po_przebudowie()  plansza porównawcza z rzutem i plansza skali (rasy_plansze.py)
Status: propozycja (nie kanon) — pilotaż do oceny przez Karola i Pawła.
"""
import os
import sys

if __name__ == "__main__":                                       # uruchomienie wprost: korzeń repozytorium na ścieżce
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from swiat.postacie import rasy

RASA = "elf"
ID = rasy.id_rasy(RASA)
NAZWA = rasy.RASY[RASA]["nazwa"]
CIALO_TYP = rasy.CIALO_TYP
STROJE = rasy.STROJE
NAZWY_STROJOW = rasy.NAZWY_STROJOW
PLANSZA_ZBIORCZA = rasy.PLANSZA_ZBIORCZA


def cialo(zaczepy_ekwipunku=False):
    """Ciało elfa „rasa_elf_cialo” z klipami idle, chod, wiwat (skopiowane z ciała odniesienia człowieka)."""
    return rasy.cialo(RASA, zaczepy_ekwipunku)


def przedmioty():
    """Rasa nie ma własnych przedmiotów (włosy to akcesorium ciała); przymiarki biorą przedmioty bohaterów."""
    return []


def stroj(nazwa):
    """Elf w stroju ze STROJE: postać „rasa_elf_<strój>”."""
    return rasy.stroj(RASA, nazwa)


def zbuduj():
    """[Elf w stroju bazowym (id „rasa_elf”)] — ten sam kształt co inne moduły postaci."""
    return [rasy.model(RASA)]


def warianty(rodzaj="plansze"):
    """Modele dla przebuduj.py (wynik/rasa_elf/ekwipunek/): przymiarki albo ciało z zaczepami Ekw…"""
    return rasy.warianty(RASA, rodzaj)


def ekwipunek_json():
    return rasy.ekwipunek_json(RASA)


def po_przebudowie(cel):
    """Po ułożeniu wynik/rasa_elf/: plansza porównawcza z rzutem i plansza skali (zwraca nazwy plików)."""
    from swiat.postacie import rasy_plansze
    return rasy_plansze.po_przebudowie(RASA, cel)


SLABOSCI = rasy.slabosci(RASA) + [
    "Elf względem rzutu: włosy są z płaskich brył (czapa, grzywka na boki, kurtyny ze skosem przy skroni, pasma "
    "wzdłuż żuchwy i na pierś, tył ze szpicem) — bez miękkich fal i objętości z rysunku; pasma na piersi są "
    "krótsze niż na rzucie i wiszą ok. 0,06 studa przed koszulą. "
    "Uszy to ostrosłupy 0,92 studa, odchylone 24° w górę i 14° do tyłu.",
    "Elf w przymiarkach: hełm i kaptur chowają długie włosy w całości (elf wygląda wtedy na łysego pod hełmem); "
    "ok. 40% objętości ucha siedzi w ściance hełmu, czubek wystaje 0,51 studa poza hełm i 0,59 poza kaptur. "
    "Bez kaptura tył włosów przecina kołczan Zwiadowcy na plecach.",
]


if __name__ == "__main__":
    p = zbuduj()[0]
    print("%s: %d kości, %d brył, %d zaczepów, klipy: %s, skala rasy %.2f"
          % (p.id, len(p.kosci), len(p.czesci), len(p.zaczepy), ", ".join(k.nazwa for k in p.klipy), p.skala_rasy))
