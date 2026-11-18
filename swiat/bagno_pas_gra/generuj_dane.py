#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dane gry Bagna (Workspace/BagnoPasGra) — TEN SAM generator co las-pas (swiat/las_pas_gra/generuj_dane.py) na
konfiguracji Bagna. Bez Studio.

    python -B swiat/bagno_pas_gra/generuj_dane.py               # zapisuje trzy moduły i drukuje tabelę stref
    python -B swiat/bagno_pas_gra/generuj_dane.py --sprawdz     # tylko sprawdza, czy pliki są aktualne (kod 1, gdy nie)
    python -B swiat/bagno_pas_gra/generuj_dane.py --wyjscie DIR # zapis do innego folderu (testy determinizmu)
    python -B swiat/bagno_pas_gra/generuj_dane.py --bez-mapy    # tylko plan (udaje, że swiat/bagno_pas nie ma mapy)

Wyjście (wygenerowane — nie edytować ręcznie):
  zrodla/DanePotworowBagna.luau — strefy potworów Bagna w formacie DanePotworow (w Studio Moduly/DanePotworow);
  zrodla/DaneBagna.luau         — liczby świata Bagna w formacie DanePasa (w Studio Moduly/DanePasa) + pole biom;
  silnik/DaneWalkiBagna.luau    — kopia danych silnika walki (tools/walka/dane_walki.json) z dopisanymi przeciwnikami
                                  Bagna (przeciwnicy.py); w Studio Moduly/Walka/Dane kontenera Bagna.

Wejścia (tylko odczyt): swiat/bagno_pas/plan_bagna.json, znaczniki.json i czesci.json (mapa Bagna),
swiat/las_pas_gra (generator i dane lasu: punkt przed bramą lasu dla graczy bez prawa wejścia), przeciwnicy.py,
tools/walka/dane_walki.json, swiat/test_walki2/aktorzy.py i aktorzy_bagna.py.

Ustawienia przyjęte, do zmiany (opis w README): poziomy stref POZIOMY_STREF (kalkulator balansu zamiast poziomów
z planu Bagna — patrz niżej), mgła MGLA_CEL, prostokąt wejścia od bramy lasu (WEJSCIE_U), teksty bramy.
"""
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if TU not in sys.path:
    sys.path.insert(0, TU)
import przeciwnicy  # noqa: E402


def _modul(nazwa, sciezka):
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


PAS = os.path.join(REPO, "swiat", "las_pas_gra")
if PAS not in sys.path:
    sys.path.insert(0, PAS)
GEN = _modul("generuj_dane_las_pas_gra_dla_bagna", os.path.join(PAS, "generuj_dane.py"))
GD_WALKI = _modul("generuj_dane_walki_dla_bagna", os.path.join(REPO, "tools", "walka", "generuj_dane.py"))
zrodlo_mapy = GEN.zrodlo_mapy

# D-096 (17.11.2026): gra czyta KRÓTKĄ mapę Bagna (przycięta z projektu swiat/bagno_pas przez swiat/biomy/przycinarka.py)
MAPA_BAGNA = os.path.join(REPO, "swiat", "bagno_pas", "krotki")
CEL_POTWOROW = os.path.join(TU, "zrodla", "DanePotworowBagna.luau")
CEL_PASA = os.path.join(TU, "zrodla", "DaneBagna.luau")
CEL_WALKI = os.path.join(TU, "silnik", "DaneWalkiBagna.luau")

GATUNKI = {
    "Rechotek": "rechotek",
    "Bulgotnik": "bulgotnik",
    "Kłodokłap": "klodoklap",
    "Ropucha z Chatką": "ropucha_z_chatka",
    "Strażnik Topieli": "straznik_topieli",
}

# Poziomy stref (PRZYJĘTE, DO ZMIANY). Plan Bagna (swiat/bagno_pas) ma 11–19 / 11–25 z modelu tempa dla gracza bez
# treningu i z poziomem „auto”. Od 17.11 gracz walczy na swoim prawdziwym poziomie (swiat/stan_gracza), więc bierzemy
# kalkulator balansu (tools/walka/BALANS_1711.md, część 1, plan rosnący, gracz trenujący 20% czasu): wejście do
# Bagna na 10. poziomie, wyjście na 17.; rzadki potwór i strażnik o poziom niżej niż gracz na wyjściu.
# D-096: z każdej przegrody została jedna strefa (pierwszy kojec) z poziomami całej przegrody
POZIOMY_STREF = {"r1": [10, 12], "b1": [12, 14], "k1": [14, 16], "t1": [16, 16]}
POZIOM_STRAZNIKA = 16
# serwer przelotu prosi o wczytanie mapy wokół tych u — od D-096 z planu krótkiego (przelot_kamery.streaming_u)
with open(os.path.join(MAPA_BAGNA, "plan_bagna.json"), encoding="utf-8") as _f:
    _PLAN_KROTKI = json.load(_f)
with open(os.path.join(MAPA_BAGNA, "znaczniki.json"), encoding="utf-8") as _f:
    _ZN_KROTKIE = json.load(_f)
PUNKTY_STRUMIENIA_U = list(_PLAN_KROTKI["przelot_kamery"]["streaming_u"])
# mgła Bagna: gęstsza, niższa i szarozielona (plan biomów: FogColor 9AA58E; tu jako Atmosphere, jak w lesie-pasie)
MGLA_CEL = {"Density": 0.42, "Offset": 0.08, "Haze": 2.2, "Glare": 0, "Color": "9AA58E", "Decay": "5E6B4E"}
# „gracz jest w Bagnie” (przelot, prawo wejścia) zaczyna się 2 st za bramą lasu (u 934), nie od zakresu części
# (936 − 10) — inaczej gracz stojący PRZED bramą lasu dostałby przelot Bagna
_U_OD = _PLAN_KROTKI["pas"]["u_od"]                      # brama lasu (krótki pas)
_U_CZESCI = _ZN_KROTKIE["pas"]["zakres_czesci_u"][1]
WEJSCIE_U = (round(_U_OD + 2, 2), round(_U_CZESCI + 10, 2))
RATUNEK_U = (_U_OD, round(_U_CZESCI + 150, 2))  # ratunek tylko od bramy lasu w głąb Bagna (las ratuje sam do swojej bramy)


def _wymaganie():
    """Gracz bez otwartej bramy lasu (atrybut gracza z serwera lasu-pasa) jest odsyłany przed bramę lasu."""
    _, _, dpa_lasu = GEN.wszystko()
    p, q = dpa_lasu["przedBrama"]["punkt"], dpa_lasu["przedBrama"]["patrz"]
    wys = dpa_lasu["przybycie"]["wysokosc"]
    b = dpa_lasu["brama"]
    return {
        "atrybut": GEN.BIOM_LASU["atrybutStraznik"],
        # cofanie nieuprawnionych lasu sięga x bramy + głębokość — Bagno pilnuje dopiero dalej (jedno pilnowanie)
        "odX": round(b["x"] + b["glebokosc"], 2),
        "punkt": [p[0], round(p[1] + wys, 2), p[2]], "patrz": [q[0], round(q[1] + wys, 2), q[2]],
        "komunikat": "Bagno jest za bramą lasu — najpierw pokonaj Strażnika Gaju.",
    }


BIOM_BAGNA = {
    "id": "bagno", "nazwa": "Bagno",
    "uchwyt": "PrzeniesDoBagna",
    "pamiecPrzelot": "widzialPrzelotBagna", "pamiecStraznik": "pokonalStraznikaBagna",
    "atrybutPrzelot": "WidzialPrzelotBagna", "atrybutStraznik": "PokonalStraznikaBagna",
    "atrybutPunktu": "PunktPrzybyciaBagna", "atrybutPatrz": "PatrzPrzybyciaBagna",
    "straznik": "Strażnika Topieli",
    "komunikatBramy": "Brama do Dżungli jest zamknięta — pokonaj Strażnika Topieli.",
    "przekieruj": False,
    "podpisBramy": "Brama do Dżungli otwarta — idź za Topiel",   # 18.11.2026: Dżungla stoi (było „Dżungla wkrótce”)
    "banerBramy": "BRAMA DO DŻUNGLI OTWARTA!",
    "podpisBanera": "Idź za Topiel — dalej Dżungla",
    "podpisBaneraWkrotce": "Za Topielą — Dżungla (wkrótce)",
    "nastepny": {"mapa": "DzunglaPas", "nazwa": "Dżungla"},
}

MAPA = dict(zrodlo_mapy.LAS)
MAPA.update({
    "plik_planu": os.path.join(MAPA_BAGNA, "plan_bagna.json"),
    "plik_znacznikow": os.path.join(MAPA_BAGNA, "znaczniki.json"),
    "plik_czesci": os.path.join(MAPA_BAGNA, "czesci.json"),
    "kontener": "BagnoPas", "klucz_bramy": "brama_dzungli", "nazwa_bramy": "brama do Dżungli",
    "grupa_wrot": "BramaDzungli/Wrota", "grupa_palisady": "BramaDzungli/Palisada", "zapowiedz": "ZapowiedzDzungli",
    "opis_mapy": "swiat/bagno_pas/krotki", "opis_planu": "plan_bagna.json (krótki)",
})

NAGLOWEK_POTWOROW = """--[[
\tDanePotworow (BAGNO) — WYGENEROWANE przez swiat/bagno_pas_gra/generuj_dane.py z swiat/bagno_pas/plan_bagna.json
\t(i znaczniki.json + czesci.json mapy Bagna) oraz przeciwników Bagna (swiat/bagno_pas_gra/przeciwnicy.py).
\tNIE EDYTUJ RĘCZNIE: zmień plan, mapę albo konfigurację i uruchom python -B swiat/bagno_pas_gra/generuj_dane.py.

\tFormat jak swiat/las_potwory/zrodla/DanePotworow.luau — w Studio Workspace/BagnoPasGra/Moduly/DanePotworow; czytają
\tgo te same SerwerPotworow i KlientPotworow co w lesie. Współrzędne w układzie ŚWIATA (świat = (1100 + u; y; −700 + v)).
\tPoziomy stref z kalkulatora balansu (POZIOMY_STREF w generatorze), nie z planu.
]]
if not game:GetService("RunService"):IsStudio() then
\treturn {}
end
"""

NAGLOWEK_PASA = """--[[
\tDanePasa (BAGNO) — WYGENEROWANE przez swiat/bagno_pas_gra/generuj_dane.py z planu i mapy Bagna. NIE EDYTUJ RĘCZNIE.
\tLiczby świata dla SerwerPasa, KlientPasa i MglaPasa (te same skrypty co las-pas): przybycie, Kamień Powrotu, brama do
\tDżungli i to, co za nią, mgła Bagna, przelot kamery, Strażnik Topieli; pole biom — nazwy i teksty Bagna (uchwyt
\tPrzeniesDoBagna, klucze pamięci, prawo wejścia z bramy lasu).
\tProstokąty to { x1, x2, z1, z2 } w poziomie świata; punkty to { x, y, z }.
]]
if not game:GetService("RunService"):IsStudio() then
\treturn {}
end
"""

NAGLOWEK_WALKI = """--[[
\tDane silnika walki DLA KONTENERA BAGNA — WYGENEROWANE przez swiat/bagno_pas_gra/generuj_dane.py. NIE EDYTUJ RĘCZNIE.
\tTo tools/walka/dane_walki.json BEZ ZMIAN (ten sam plik co src/server/Walka/Dane.luau) z dopisanymi na końcu listy
\tprzeciwnikami Bagna z swiat/bagno_pas_gra/przeciwnicy.py. Silnik (Statystyki, Przeciwnicy, Umiejetnosci, Silnik) jest
\ttą samą kopią co w lesie — zmieniają się tylko dane.
]]
"""


def tekst_walki():
    return NAGLOWEK_WALKI + "\nreturn " + GD_WALKI.luau(przeciwnicy.dane_walki_bagna(), 0) + "\n"


def _dodatkowe(m, dp, dpa):
    return {CEL_WALKI: tekst_walki()}


def konfiguracja():
    k = dict(GEN.KONFIG)
    biom = dict(BIOM_BAGNA)
    biom["wymaganie"] = _wymaganie()
    k.update({
        "id": "bagno",
        "mapa": MAPA,
        "gatunki": GATUNKI,
        "straznik_gatunek": "straznik_topieli",
        "poziomy": (1, 30),
        "poziomy_stref": POZIOMY_STREF,
        "poziom_straznika": POZIOM_STRAZNIKA,
        "punkty_strumienia_u": PUNKTY_STRUMIENIA_U,
        "mgla_cel": MGLA_CEL,
        "wejscie_u": WEJSCIE_U,
        "ratunek_u": RATUNEK_U,
        "napis_bramy": ("ZAMKNIĘTE", "Pokonaj Strażnika Topieli"),
        "tabliczka": ("DŻUNGLA — WKRÓTCE", "tu zaczyna się następny biom"),
        "biom": biom,
        "cel_potworow": CEL_POTWOROW, "cel_pasa": CEL_PASA,
        "naglowek_potworow": NAGLOWEK_POTWOROW, "naglowek_pasa": NAGLOWEK_PASA,
        "polecenie": "python -B swiat/bagno_pas_gra/generuj_dane.py",
        "opis_walki": "tools/walka/dane_walki.json + swiat/bagno_pas_gra/przeciwnicy.py",
        "przeciwnicy_dodatkowi": [p["id"] for p in przeciwnicy.PRZEPISY],
        "pliki_aktorow": [os.path.join(REPO, "swiat", "test_walki2", "aktorzy_bagna.py")],
        "dodatkowe_pliki": _dodatkowe,
    })
    return k


KONFIG = konfiguracja()


def wszystko(bez_mapy=False):
    return GEN.wszystko(bez_mapy=bez_mapy, k=KONFIG)


def main():
    GEN.main(KONFIG)


if __name__ == "__main__":
    main()
