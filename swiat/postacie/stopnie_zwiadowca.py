# -*- coding: utf-8 -*-
"""STOPNIE EKWIPUNKU — Zwiadowca w komplecie startowym i w trzech kompletach do kupienia: las, Bagno, Dżungla (D-106).

Cienkie opakowanie dla przebuduj.py; cała geometria jest w swiat/postacie/stopnie.py (własne projekty, propozycja).
zbuduj() zwraca bohatera w czterech kompletach (tylko klip idle — ruch jest wspólny z modułem bohatera) i ikony
nowych przedmiotów; po przebudowie powstaje plansza „cztery stopnie obok siebie”.

    python -B swiat/postacie/przebuduj.py stopnie_zwiadowca --bez-filmow

Wynik (wynik/stopnie_zwiadowca/): stopnie_zwiadowca_cztery_stopnie.jpg, stopnie_zwiadowca_ikony_arkusz.jpg,
stopnie_zwiadowca_<stopień>.glb / .fbx / .blend (komplet na bohaterze), przedmioty/<id>.glb (cały przedmiot), ikony/.
"""
import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from swiat.postacie import stopnie  # noqa: E402

KLASA = "zwiadowca"
ID = "stopnie_zwiadowca"
NAZWA = "Zwiadowca — stopnie ekwipunku"
SLABOSCI = stopnie.SLABOSCI


def zbuduj():
    return stopnie.modele(KLASA)


def po_przebudowie(cel):
    return stopnie.plansza_stopni(cel, KLASA)
