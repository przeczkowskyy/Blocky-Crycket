# -*- coding: utf-8 -*-
"""Lokacje biomu Las — jeden plik na podbiom (Stary Ukłon osobno). Rejestr: id lokacji z uklad.json → funkcja
f(s, G, rnd, L)."""
from swiat.biom_las.lokacje import kapeluszowo, korona, laka, ostepy, serce, stary_uklon, wawoz

REJESTR = {}
for _m in (laka, kapeluszowo, stary_uklon, serce, ostepy, wawoz, korona):
    REJESTR.update(_m.LOKACJE)
