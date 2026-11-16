# -*- coding: utf-8 -*-
"""Budynki bazaru — jeden moduł na budynek, ten sam kontrakt co swiat/krzywe_miasteczko/budynki (PROJEKT.md 5.0):
stałe NAZWA (grupa, ASCII PascalCase), OBRYS = (szer, gł), WYSOKOSC, BUDZET i funkcja buduj(s, rnd), która buduje wokół
(0, 0, 0) frontem ku +Z (y = 0 = bruk uliczki); miejsce i obrót nadaje generator. Nowe względem starego kontraktu:
budynki-sklepy mają WNĘTRZE i sprzedawcę (D-084), a punkty E i znaczniki zapisują przez wspolne.punkt_e().
"""
