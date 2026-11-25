# -*- coding: utf-8 -*-
"""PULA WOJOWNIKA Lv 1–10 — arkusz Targowy (kolumna 2) na kocie-wojowniku. Status: propozycja.

Cienkie opakowanie dla przebuduj.py; cała geometria jest w swiat/postacie/pula_wojownika.py.

    python -B swiat/postacie/przebuduj.py pula_wojownika_targowy --bez-filmow

Wynik (wynik/pula_wojownika_targowy/): kot w komplecie (GLB/FBX, plansza 3/4-przód-bok-tył), miecz jako osobny
przedmiot (przedmioty/), ekwipunek/ (segmenty kostne GLB/FBX, ikony, ekwipunek.json), plansze noc2511_* w
wynik/_pula_wojownika/.
"""
import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from swiat.postacie import pula_wojownika as PW  # noqa: E402

ZESTAW = "targowy"
ID = "pula_wojownika_" + ZESTAW
NAZWA = "Kot-wojownik — " + PW.ZESTAWY[ZESTAW]["nazwa"]
STROJE = {"golas": (), "komplet": PW.komplet(ZESTAW)}
NAZWY_STROJOW = {"golas": "goły kot", "komplet": PW.ZESTAWY[ZESTAW]["nazwa"]}
PLANSZA_ZBIORCZA = ("golas", "komplet")
FILMY = []
FILMY_EKWIPUNKU = ()
KOREKTY_CHWYTU = PW.KOREKTY_CHWYTU
SLABOSCI = PW.SLABOSCI


def cialo(zaczepy_ekwipunku=False):
    return PW.cialo(zaczepy_ekwipunku)


def przedmioty():
    return PW.przedmioty(ZESTAW)


def warianty(rodzaj="plansze"):
    return PW.warianty(ZESTAW, ID, rodzaj)


def ekwipunek_json():
    return PW.ekwipunek_json(ZESTAW, ID)


def zbuduj():
    return PW.modele(ZESTAW, ID)


def po_przebudowie(cel):
    return PW.plansze(ZESTAW, cel, ID)
