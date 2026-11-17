#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buduje w Roblox Studio kontener Workspace/BagnoPasGra — „Bagno w grze”: TEN SAM budowniczy i ten sam kod gry co
las-pas (swiat/las_pas_gra/zbuduj.py, swiat/las_potwory), uruchomiony na danych Bagna.

    python -B swiat/bagno_pas_gra/zbuduj.py --sucho      # bez Studio: dane aktualne, kontrola Luau, strażniki, plan
    python -B swiat/bagno_pas_gra/zbuduj.py              # buduje / odbudowuje Workspace/BagnoPasGra (tryb Edit)
    python -B swiat/bagno_pas_gra/zbuduj.py --skrypty    # tylko skrypty, moduły, zdalne i atrybuty Stale_*
    python -B swiat/bagno_pas_gra/zbuduj.py --usun       # usuwa Workspace/BagnoPasGra (las zostaje)
    python -B swiat/bagno_pas_gra/zbuduj.py --studio <studio_id>

Co jest inne niż w lesie (wszystko przez ustaw_konfiguracje budowniczego lasu):
  • kontener BagnoPasGra, mapa Workspace/BagnoPas (swiat/bagno_pas), szablony BagnoPasGraSzablony (5 gatunków Bagna
    z Workspace/TestWalki2/Aktorzy), osobne GUI i prefiks komunikatów, tytuł banera po Strażniku;
  • Moduly/DanePotworow ← zrodla/DanePotworowBagna.luau, Moduly/DanePasa ← zrodla/DaneBagna.luau,
    Moduly/Walka/Dane ← silnik/DaneWalkiBagna.luau (dane silnika + przeciwnicy Bagna; reszta silnika to kopia src/);
  • uchwyt Sygnaly/PrzeniesDoBagna zamiast PrzeniesDoLasu (przejście przez chmury);
  • poziomy bohatera w panelu testowym: auto, 10, 15, 20.
Zasady bezpieczeństwa te same co w lesie: jeden kontener z Wygenerowane, punkty historii, tylko tryb Edit, PlaceId
gry w każdym wysyłanym kodzie, niczego nie publikuje ani nie zapisuje, nie zmienia Lighting ani cudzych instancji.
"""
import importlib.util
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
PAS = os.path.join(REPO, "swiat", "las_pas_gra")


def _modul(nazwa, sciezka):
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# osobna kopia modułu budowniczego lasu (jego globalne podmieniamy tylko w tej kopii)
ZB = _modul("zbuduj_las_pas_gra_dla_bagna", os.path.join(PAS, "zbuduj.py"))

KONTENER = "BagnoPasGra"
ZRODLO = "swiat/bagno_pas_gra"
MAPA = "BagnoPas"
SZABLONY = ["rechotek", "bulgotnik", "klodoklap", "ropucha_z_chatka", "straznik_topieli"]
DANE_POTWOROW = "swiat/bagno_pas_gra/zrodla/DanePotworowBagna.luau"
DANE_PASA = "swiat/bagno_pas_gra/zrodla/DaneBagna.luau"
DANE_WALKI = "swiat/bagno_pas_gra/silnik/DaneWalkiBagna.luau"
UCHWYT = "PrzeniesDoBagna"

STALE = dict(ZB.STALE)
STALE.update({
    "NAZWA_KONTENERA": KONTENER,
    "NAZWA_BIOMU": MAPA,
    "NAZWA_SZABLONOW": "BagnoPasGraSzablony",
    "SZABLONY": ",".join(SZABLONY),
    "PREFIKS": "[BagnoPasGra] ",
    "GUI_BOHATERA": "BagnoPasGraBohater",
    "GUI_BANERA": "BagnoPasGraBaner",
    "PANEL_Y": 8,
    "PANEL_PREFIKS": "Bagno · ",
    # panel bohatera tylko w swoim biomie: płyta lasu sięga x 2066 (+ 40 zapasu), płyta Bagna zaczyna się na x 2066 —
    # ujemny zapas zwęża prostokąt Bagna o 40 st, więc przy bramie nigdy nie widać dwóch paneli naraz
    "PANEL_ZAPAS": -40,
    "POZIOMY_BOHATERA": "auto,10,15,20",
    "TYTUL_BANERA_STRAZNIKA": "STRAŻNIK TOPIELI POKONANY!",
})


def _skrypty():
    wynik = []
    for plik, klasa, sciezka, kontekst in ZB.SKRYPTY:
        if sciezka == "Moduly/DanePotworow":
            plik = DANE_POTWOROW
        elif sciezka == "Moduly/DanePasa":
            plik = DANE_PASA
        wynik.append((plik, klasa, sciezka, kontekst))
    return wynik


def _silnik():
    return [(DANE_WALKI if sciezka == "Moduly/Walka/Dane" else plik, sciezka) for plik, sciezka in ZB.SILNIK]


def _inne():
    return [(k, "Sygnaly/" + UCHWYT if p == "Sygnaly/PrzeniesDoLasu" else p) for k, p in ZB.INNE]


KONFIG = {
    "KONTENER": KONTENER, "ZRODLO": ZRODLO, "MAPA": MAPA, "SZABLONY": SZABLONY, "STALE": STALE,
    "SKRYPTY": _skrypty(), "SILNIK": _silnik(), "INNE": _inne(),
    "GENERATOR": os.path.join(TU, "generuj_dane.py"),
    "ZRODLA_LUAU": [os.path.join(PAS, "zrodla"), os.path.join(TU, "zrodla")],
}
ZB.ustaw_konfiguracje(KONFIG)

if __name__ == "__main__":
    ZB.main()
