# -*- coding: utf-8 -*-
"""Smok ewolucji jako moduł biblioteki postaci: osiem stadiów z klipami + jajo.

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/ewolucja/modele/smoki.py --wyj <folder>
           [--tylko smok_4] [--klip chod] [--eksport]

Model: smok_model.py, klipy: smok_klipy.py, wszystko naraz: generuj.py (opis w README.md obok).
"""
from swiat.ewolucja.modele import smok_klipy as sk
from swiat.ewolucja.modele import smok_model as sm

FILMY = ["spoczynek", "chod", "gryz3", "ogien_petla", "ryk"]
SLABOSCI = [
    "Nogi nie mają odwrotnej kinematyki: przy pochyleniu i podskoku tułowia stopy lekko ślizgają się po ziemi.",
    "Błona skrzydła to płaskie płyty — z boku skrzydło jest cienkie.",
    "Oczy piskląt są na przedniej ścianie głowy: z boku i z kamery gry ich nie widać.",
]


def zbuduj():
    modele = [sk.dodaj_klipy(sm.zbuduj_stadium(nr)) for nr in range(1, 9)]
    n = next(k.dlugosc for k in modele[0].klipy if k.nazwa == "wyklucie")
    return modele + [sk.klipy_jaja(sm.zbuduj_jajo(1), n)]
