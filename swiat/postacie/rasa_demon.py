# -*- coding: utf-8 -*-
"""DEMON — rasa postaci (D-079, D-104) z rzutu assets/processed/RaceTurnarounds/demon.jpg: ciało „czlowiek” w stroju bazowym.

Czerwona skóra, głowa-klocek bez włosów i bez uszu (tak jak na rzucie), czarne rogi w łuk, złote świecące
skośne oczy, skośne brwi, szeroki uśmiech z jednym kłem, ogon z grotem — sztywna łamana z klocków na kości
bioder (bez nowych kości, nie znika pod spodniami), lniana koszula, czarne spodenki, brązowe buty. Klocki, kości,
zaczepy i klipy (idle, chod, wiwat) są te same co u gołego Rycerza, więc każdy przedmiot „czlowiek” pasuje.
Wspólny kod i dane wszystkich ras: swiat/postacie/rasy.py; opis, wybory i pytania: swiat/postacie/RASY.md.

    python -B swiat/postacie/przebuduj.py rasa_demon --bez-filmow
    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/rasa_demon.py --wyj <folder>

  zbuduj()     [Demon w stroju bazowym (id „rasa_demon”), poza spoczynku]
  cialo()      to samo ciało jako „rasa_demon_cialo” (z zaczepy_ekwipunku=True: + 15 zaczepów Ekw<Kosc>Attachment)
  warianty()   przymiarki dla przebuduj.py: strój bazowy, komplet Rycerza, komplet Zwiadowcy (wynik/…/ekwipunek/)
  po_przebudowie()  plansza porównawcza z rzutem i plansza skali (rasy_plansze.py)
Status: propozycja (nie kanon) — do oceny przez Karola i Pawła.
"""
import os
import sys

if __name__ == "__main__":                                       # uruchomienie wprost: korzeń repozytorium na ścieżce
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from swiat.postacie import rasy

RASA = "demon"
ID = rasy.id_rasy(RASA)
NAZWA = rasy.RASY[RASA]["nazwa"]
CIALO_TYP = rasy.CIALO_TYP
STROJE = rasy.STROJE
NAZWY_STROJOW = rasy.NAZWY_STROJOW
PLANSZA_ZBIORCZA = rasy.PLANSZA_ZBIORCZA


def cialo(zaczepy_ekwipunku=False):
    """Ciało rasy „rasa_demon_cialo” z klipami idle, chod, wiwat (skopiowane z ciała odniesienia człowieka)."""
    return rasy.cialo(RASA, zaczepy_ekwipunku)


def przedmioty():
    """Rasa nie ma własnych przedmiotów (włosy to akcesorium ciała); przymiarki biorą przedmioty bohaterów."""
    return []


def stroj(nazwa):
    """Demon w stroju ze STROJE: postać „rasa_demon_<strój>”."""
    return rasy.stroj(RASA, nazwa)


def zbuduj():
    """[Demon w stroju bazowym (id „rasa_demon”)] — ten sam kształt co inne moduły postaci."""
    return [rasy.model(RASA)]


def warianty(rodzaj="plansze"):
    """Modele dla przebuduj.py (wynik/rasa_demon/ekwipunek/): przymiarki albo ciało z zaczepami Ekw…"""
    return rasy.warianty(RASA, rodzaj)


def ekwipunek_json():
    return rasy.ekwipunek_json(RASA)


def po_przebudowie(cel):
    """Po ułożeniu wynik/rasa_demon/: plansza porównawcza z rzutem i plansza skali (zwraca nazwy plików)."""
    from swiat.postacie import rasy_plansze
    return rasy_plansze.po_przebudowie(RASA, cel)


SLABOSCI = rasy.slabosci(RASA) + [
    "Demon względem rzutu: rogi są z dwóch klocków i szpica (łuk kanciasty), ogon to sztywna łamana z sześciu "
    "klocków z płaskim grotem — nie wije się i nie rusza się w klipach; na rzucie ogon jest cieńszy i ma miękki "
    "łuk. Oczy świecą przez emisję w teksturze-palecie (w grze trzeba ją podpiąć albo dać Neon).",
    "Ogon siedzi na biodrach i wychodzi w lewą stronę postaci poza obrys nogi. Z tylną połą tabardu Rycerza się "
    "nie przecina (wychodzi tuż nad nią), przechodzi przez pas Zwiadowcy z tyłu i dotyka liścia jego peleryny; "
    "w chodzie i wiwacie nie był sprawdzany (RASY.md pkt 8).",
    "Rogi przebijają górę hełmu Rycerza i czubek kaptura Zwiadowcy: ok. połowa objętości rogów siedzi w nakryciu "
    "głowy, czubki wystają ponad nie (RASY.md pkt 8). Ikona wyboru rasy ma spiczaste uszy, model według rzutu "
    "ich nie ma.",
]


if __name__ == "__main__":
    p = zbuduj()[0]
    print("%s: %d kości, %d brył, %d zaczepów, klipy: %s, skala rasy %.2f"
          % (p.id, len(p.kosci), len(p.czesci), len(p.zaczepy), ", ".join(k.nazwa for k in p.klipy), p.skala_rasy))
