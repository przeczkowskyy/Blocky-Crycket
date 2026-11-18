# -*- coding: utf-8 -*-
"""ORK — rasa postaci (D-079, D-104) z rzutu assets/processed/RaceTurnarounds/ork.jpg: ciało „czlowiek” w stroju bazowym.

Oliwkowa skóra, masywna wysunięta szczęka, dwa kły z dolnej szczęki, wał brwiowy z grubymi brwiami, krótkie
spiczaste uszy, czarne włosy z kokiem na czubku (akcesorium rasa_ork_wlosy — hełm je chowa), lniana koszula,
brązowe spodenki (wybór z zamówienia; na rzucie wyszły wielokolorowe), brązowe buty. Klocki, kości, zaczepy
i klipy (idle, chod, wiwat) są te same co u gołego Rycerza, więc każdy przedmiot „czlowiek” pasuje; masywność
oddaje głowa i skala rasy 1,08 (dana, niewypieczona w klocki — plansza rasa_ork_skala.jpg).
Wspólny kod i dane wszystkich ras: swiat/postacie/rasy.py; opis, wybory i pytania: swiat/postacie/RASY.md.

    python -B swiat/postacie/przebuduj.py rasa_ork --bez-filmow
    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/rasa_ork.py --wyj <folder>

  zbuduj()     [Ork w stroju bazowym (id „rasa_ork”), poza spoczynku]
  cialo()      to samo ciało jako „rasa_ork_cialo” (z zaczepy_ekwipunku=True: + 15 zaczepów Ekw<Kosc>Attachment)
  warianty()   przymiarki dla przebuduj.py: strój bazowy, komplet Rycerza, komplet Zwiadowcy (wynik/…/ekwipunek/)
  po_przebudowie()  plansza porównawcza z rzutem i plansza skali (rasy_plansze.py)
Status: propozycja (nie kanon) — pilotaż do oceny przez Karola i Pawła.
"""
import os
import sys

if __name__ == "__main__":                                       # uruchomienie wprost: korzeń repozytorium na ścieżce
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from swiat.postacie import rasy

RASA = "ork"
ID = rasy.id_rasy(RASA)
NAZWA = rasy.RASY[RASA]["nazwa"]
CIALO_TYP = rasy.CIALO_TYP
STROJE = rasy.STROJE
NAZWY_STROJOW = rasy.NAZWY_STROJOW
PLANSZA_ZBIORCZA = rasy.PLANSZA_ZBIORCZA


def cialo(zaczepy_ekwipunku=False):
    """Ciało orka „rasa_ork_cialo” z klipami idle, chod, wiwat (skopiowane z ciała odniesienia człowieka)."""
    return rasy.cialo(RASA, zaczepy_ekwipunku)


def przedmioty():
    """Rasa nie ma własnych przedmiotów (włosy to akcesorium ciała); przymiarki biorą przedmioty bohaterów."""
    return []


def stroj(nazwa):
    """Ork w stroju ze STROJE: postać „rasa_ork_<strój>”."""
    return rasy.stroj(RASA, nazwa)


def zbuduj():
    """[Ork w stroju bazowym (id „rasa_ork”)] — ten sam kształt co inne moduły postaci."""
    return [rasy.model(RASA)]


def warianty(rodzaj="plansze"):
    """Modele dla przebuduj.py (wynik/rasa_ork/ekwipunek/): przymiarki albo ciało z zaczepami Ekw…"""
    return rasy.warianty(RASA, rodzaj)


def ekwipunek_json():
    return rasy.ekwipunek_json(RASA)


def po_przebudowie(cel):
    """Po ułożeniu wynik/rasa_ork/: plansza porównawcza z rzutem i plansza skali (zwraca nazwy plików)."""
    from swiat.postacie import rasy_plansze
    return rasy_plansze.po_przebudowie(RASA, cel)


SLABOSCI = rasy.slabosci(RASA) + [
    "Ork względem rzutu: masywny tułów, grube ręce i szeroki kark z rysunku NIE są oddane — klocki ciała są takie "
    "jak u człowieka (żeby pasował ekwipunek). Masywność niesie głowa (szczęka szersza o 0,1 i wysunięta 0,075 "
    "studa, wał brwiowy, kły 0,27 studa) i skala 1,08 z danych rasy.",
    "Spodenki brązowe według zamówienia (rzut ma wielokolorowe) — wybór do potwierdzenia (RASY.md).",
    "Kok to obły węzeł (kula z ośmiu ścian) związany rzemieniem, z kosmykiem z trzech klocków opadającym łukiem "
    "za głowę (do ok. 0,9 studa nad głową); hełm i kaptur chowają włosy razem z kokiem. Uszy są krótkie "
    "i odchylone 44° w górę: ponad połowa objętości ucha siedzi w ściance hełmu albo kaptura, czubek wystaje "
    "0,07 studa poza hełm i 0,15 poza kaptur. Kły, szczęka i wał brwiowy mieszczą się w otworze twarzy hełmu. "
    "W rękawicach Zwiadowcy dłonie orka mają kolor skóry człowieka.",
]


if __name__ == "__main__":
    p = zbuduj()[0]
    print("%s: %d kości, %d brył, %d zaczepów, klipy: %s, skala rasy %.2f"
          % (p.id, len(p.kosci), len(p.czesci), len(p.zaczepy), ", ".join(k.nazwa for k in p.klipy), p.skala_rasy))
