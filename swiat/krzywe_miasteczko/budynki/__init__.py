# -*- coding: utf-8 -*-
"""Budynki mapy v2 „Krzywe Miasteczko” — jeden moduł na budynek (kontrakt: ../PROJEKT.md rozdz. 5.0, wzór: _wzor.py).

Każdy moduł ma stałe NAZWA (nazwa grupy, ASCII PascalCase) i OBRYS = (szer, gl) oraz funkcję buduj(s, rnd), która buduje
wokół (0, 0, 0) frontem ku +Z, bez własnej grupy głównej — grupę i miejsce w mieście nadaje generator:
    with s.uklad(pos=(x, y_podstawy, z), obrot=(0, obrot_y, 0), grupa=modul.NAZWA): modul.buduj(s, rnd)
"""
