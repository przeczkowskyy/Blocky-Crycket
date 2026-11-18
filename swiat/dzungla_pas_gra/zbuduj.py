#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buduje w Roblox Studio kontener Workspace/DzunglaPasGra — „Dżungla w grze”: TEN SAM budowniczy i ten sam kod gry co
las-pas i Bagno (swiat/las_pas_gra/zbuduj.py, swiat/las_potwory), uruchomiony na danych Dżungli.

    python -B swiat/dzungla_pas_gra/zbuduj.py --sucho      # bez Studio: dane aktualne, kontrola Luau, strażniki, plan
    python -B swiat/dzungla_pas_gra/zbuduj.py              # buduje / odbudowuje Workspace/DzunglaPasGra (tryb Edit)
    python -B swiat/dzungla_pas_gra/zbuduj.py --skrypty    # tylko skrypty, moduły, zdalne i atrybuty Stale_*
    python -B swiat/dzungla_pas_gra/zbuduj.py --usun       # usuwa Workspace/DzunglaPasGra (las i Bagno zostają)
    python -B swiat/dzungla_pas_gra/zbuduj.py --studio <studio_id>

Co jest inne niż w lesie (wszystko przez ustaw_konfiguracje budowniczego lasu):
  • kontener DzunglaPasGra, mapa Workspace/DzunglaPas (swiat/dzungla_pas/krotki), szablony DzunglaPasGraSzablony
    (5 gatunków Dżungli z Workspace/TestWalki2/Aktorzy), osobne GUI i prefiks komunikatów, tytuł banera po Wężu;
  • Moduly/DanePotworow ← zrodla/DanePotworowDzungli.luau, Moduly/DanePasa ← zrodla/DaneDzungli.luau,
    Moduly/Walka/Dane ← silnik/DaneWalkiDzungli.luau (dane silnika + przeciwnicy Dżungli; reszta silnika to kopia src/);
  • uchwyt Sygnaly/PrzeniesDoDzungli zamiast PrzeniesDoLasu (przejście przez chmury);
  • poziomy bohatera w panelu testowym: auto, 17, 20, 23.
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
ZB = _modul("zbuduj_las_pas_gra_dla_dzungli", os.path.join(PAS, "zbuduj.py"))

KONTENER = "DzunglaPasGra"
ZRODLO = "swiat/dzungla_pas_gra"
MAPA = "DzunglaPas"
SZABLONY = ["zwijogon", "gebokwiat", "kokosowy_silacz", "pancernik_ruin", "waz_stu_lian"]
DANE_POTWOROW = "swiat/dzungla_pas_gra/zrodla/DanePotworowDzungli.luau"
DANE_PASA = "swiat/dzungla_pas_gra/zrodla/DaneDzungli.luau"
DANE_WALKI = "swiat/dzungla_pas_gra/silnik/DaneWalkiDzungli.luau"
UCHWYT = "PrzeniesDoDzungli"

STALE = dict(ZB.STALE)
STALE.update({
    "NAZWA_KONTENERA": KONTENER,
    "NAZWA_BIOMU": MAPA,
    "NAZWA_SZABLONOW": "DzunglaPasGraSzablony",
    "SZABLONY": ",".join(SZABLONY),
    "PREFIKS": "[DzunglaPasGra] ",
    "GUI_BOHATERA": "DzunglaPasGraBohater",
    "GUI_BANERA": "DzunglaPasGraBaner",
    "PANEL_Y": 8,
    "PANEL_PREFIKS": "Dżungla · ",
    # panel bohatera tylko w swoim biomie: płyta Bagna sięga za jego bramę (+ 40 zapasu) — ujemny zapas zwęża prostokąt
    # Dżungli o 40 st, więc przy bramie Bagna nigdy nie widać dwóch paneli naraz (jak między lasem a Bagnem)
    "PANEL_ZAPAS": -40,
    "POZIOMY_BOHATERA": "auto,17,20,23,30",   # 30: próba wygranej z Wężem (J10)
    "TYTUL_BANERA_STRAZNIKA": "WĄŻ STU LIAN POKONANY!",
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
