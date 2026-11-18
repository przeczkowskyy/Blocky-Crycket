#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dane gry Dżungli (Workspace/DzunglaPasGra) — TEN SAM generator co las-pas i Bagno (swiat/las_pas_gra/generuj_dane.py)
na konfiguracji Dżungli. Bez Studio.

    python -B swiat/dzungla_pas_gra/generuj_dane.py               # zapisuje trzy moduły i drukuje tabelę stref
    python -B swiat/dzungla_pas_gra/generuj_dane.py --sprawdz     # tylko sprawdza, czy pliki są aktualne (kod 1, gdy nie)
    python -B swiat/dzungla_pas_gra/generuj_dane.py --wyjscie DIR # zapis do innego folderu (testy determinizmu)
    python -B swiat/dzungla_pas_gra/generuj_dane.py --bez-mapy    # tylko plan (udaje, że swiat/dzungla_pas nie ma mapy)

Wyjście (wygenerowane — nie edytować ręcznie):
  zrodla/DanePotworowDzungli.luau — strefy potworów Dżungli w formacie DanePotworow (w Studio Moduly/DanePotworow);
  zrodla/DaneDzungli.luau         — liczby świata Dżungli w formacie DanePasa (w Studio Moduly/DanePasa) + pole biom;
  silnik/DaneWalkiDzungli.luau    — kopia danych silnika walki (tools/walka/dane_walki.json) z dopisanymi
                                    przeciwnikami Dżungli (przeciwnicy.py); w Studio Moduly/Walka/Dane kontenera.

Wejścia (tylko odczyt): swiat/dzungla_pas/krotki (krótka mapa Dżungli: plan, znaczniki, części), swiat/las_pas_gra
(generator), swiat/bagno_pas_gra (dane Bagna: punkt przed bramą Bagna dla graczy bez prawa wejścia), przeciwnicy.py,
tools/walka/dane_walki.json, swiat/test_walki2/aktorzy.py i aktorzy_dzungli.py.

Ustawienia przyjęte, do zmiany (opis w README): poziomy stref POZIOMY_STREF (kalkulator balansu zamiast poziomów
z planu Dżungli — patrz niżej), mgła MGLA_CEL, prostokąt wejścia od bramy Bagna (WEJSCIE_U), teksty bramy.
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
GEN = _modul("generuj_dane_las_pas_gra_dla_dzungli", os.path.join(PAS, "generuj_dane.py"))
GD_WALKI = _modul("generuj_dane_walki_dla_dzungli", os.path.join(REPO, "tools", "walka", "generuj_dane.py"))


def _modul_bagna():
    """Generator Bagna z JEGO przeciwnikami (oba pakiety mają moduł „przeciwnicy” — na czas wczytania podmiana)."""
    nasz = sys.modules.pop("przeciwnicy", None)
    sciezka = os.path.join(REPO, "swiat", "bagno_pas_gra")
    sys.path.insert(0, sciezka)
    try:
        return _modul("generuj_dane_bagna_dla_dzungli", os.path.join(sciezka, "generuj_dane.py"))
    finally:
        sys.path.remove(sciezka)
        sys.modules.pop("przeciwnicy", None)
        if nasz is not None:
            sys.modules["przeciwnicy"] = nasz


# dane Bagna (poprzedni biom): punkt przed bramą Bagna i atrybut jej otwarcia
BAG = _modul_bagna()
zrodlo_mapy = GEN.zrodlo_mapy

# D-096: gra czyta KRÓTKĄ mapę Dżungli (przycięta z projektu swiat/dzungla_pas przez swiat/biomy/przycinarka.py)
MAPA_DZUNGLI = os.path.join(REPO, "swiat", "dzungla_pas", "krotki")
CEL_POTWOROW = os.path.join(TU, "zrodla", "DanePotworowDzungli.luau")
CEL_PASA = os.path.join(TU, "zrodla", "DaneDzungli.luau")
CEL_WALKI = os.path.join(TU, "silnik", "DaneWalkiDzungli.luau")

GATUNKI = {
    "Zwijogon": "zwijogon",
    "Gębokwiat": "gebokwiat",
    "Kokosowy Siłacz": "kokosowy_silacz",
    "Pancernik Ruin": "pancernik_ruin",
    "Wąż Stu Lian": "waz_stu_lian",
}

# Poziomy stref (PRZYJĘTE, DO ZMIANY): kalkulator balansu (tools/walka/BALANS_1711.md, część 1, plan rosnący) —
# Dżungla 17 → 23: wejście z Bagna na ok. 17. poziomie; w scalonych strefach (D-096) poziomy całej przegrody,
# rozdawane po miejscach (SerwerPotworow, poziomyPoMiejscach); rzadki potwór i strażnik na 23 (strażnik „trudny”,
# jak Strażnik Topieli: ok. 22% wygranych klas wzorcowych na wejściu — przeciwnicy.py)
POZIOMY_STREF = {"z1": [17, 19], "g1": [19, 21], "o1": [21, 23], "t1": [23, 23]}
POZIOM_STRAZNIKA = 23
with open(os.path.join(MAPA_DZUNGLI, "plan_dzungli.json"), encoding="utf-8") as _f:
    _PLAN_KROTKI = json.load(_f)
with open(os.path.join(MAPA_DZUNGLI, "znaczniki.json"), encoding="utf-8") as _f:
    _ZN_KROTKIE = json.load(_f)
PUNKTY_STRUMIENIA_U = list(_PLAN_KROTKI["przelot_kamery"]["streaming_u"])
# mgła Dżungli: ciepła zieleń (plan biomów FogColor 7FBF8A; arena Dżungli 8FC79A — ten sam kolor, żeby mapa i arena
# wyglądały jak jedno miejsce), lżejsza niż na Bagnie
MGLA_CEL = {"Density": 0.38, "Offset": 0.1, "Haze": 1.8, "Glare": 0.1, "Color": "8FC79A", "Decay": "4E7A52"}
# „gracz jest w Dżungli” zaczyna się 2 st za bramą Bagna (jak Bagno za bramą lasu)
_U_OD = _PLAN_KROTKI["pas"]["u_od"]                      # brama Bagna (krótki pas)
_U_CZESCI = _ZN_KROTKIE["pas"]["zakres_czesci_u"][1]
WEJSCIE_U = (round(_U_OD + 2, 2), round(_U_CZESCI + 10, 2))
RATUNEK_U = (_U_OD, round(_U_CZESCI + 150, 2))  # ratunek tylko od bramy Bagna w głąb Dżungli


def _wymaganie():
    """Gracz bez otwartej bramy Bagna (atrybut gracza z serwera Bagna) jest odsyłany przed bramę Bagna."""
    _, _, dpa_bagna = BAG.wszystko()
    p, q = dpa_bagna["przedBrama"]["punkt"], dpa_bagna["przedBrama"]["patrz"]
    wys = dpa_bagna["przybycie"]["wysokosc"]
    b = dpa_bagna["brama"]
    return {
        "atrybut": BAG.BIOM_BAGNA["atrybutStraznik"],
        # cofanie nieuprawnionych Bagna sięga x bramy + głębokość — Dżungla pilnuje dopiero dalej (jedno pilnowanie)
        "odX": round(b["x"] + b["glebokosc"], 2),
        "punkt": [p[0], round(p[1] + wys, 2), p[2]], "patrz": [q[0], round(q[1] + wys, 2), q[2]],
        "komunikat": "Dżungla jest za bramą Bagna — najpierw pokonaj Strażnika Topieli.",
    }


BIOM_DZUNGLI = {
    "id": "dzungla", "nazwa": "Dżungla",
    "uchwyt": "PrzeniesDoDzungli",
    "pamiecPrzelot": "widzialPrzelotDzungli", "pamiecStraznik": "pokonalStraznikaDzungli",
    "atrybutPrzelot": "WidzialPrzelotDzungli", "atrybutStraznik": "PokonalStraznikaDzungli",
    "atrybutPunktu": "PunktPrzybyciaDzungli", "atrybutPatrz": "PatrzPrzybyciaDzungli",
    "straznik": "Węża Stu Lian",
    "komunikatBramy": "Brama do Pustyni jest zamknięta — pokonaj Węża Stu Lian.",
    "przekieruj": False,
    "podpisBramy": "Brama do Pustyni otwarta — Pustynia wkrótce",
    "banerBramy": "BRAMA DO PUSTYNI OTWARTA!",
    "podpisBanera": "Idź za Krąg Stu Lian — dalej Pustynia",
    "podpisBaneraWkrotce": "Za Kręgiem Stu Lian — Pustynia (wkrótce)",
    "nastepny": {"mapa": "PustyniaPas", "nazwa": "Pustynia"},
}

MAPA = dict(zrodlo_mapy.LAS)
MAPA.update({
    "plik_planu": os.path.join(MAPA_DZUNGLI, "plan_dzungli.json"),
    "plik_znacznikow": os.path.join(MAPA_DZUNGLI, "znaczniki.json"),
    "plik_czesci": os.path.join(MAPA_DZUNGLI, "czesci.json"),
    "kontener": "DzunglaPas", "klucz_bramy": "brama_pustyni", "nazwa_bramy": "brama do Pustyni",
    "grupa_wrot": "BramaPustyni/Wrota", "grupa_palisady": "BramaPustyni/Palisada", "zapowiedz": "ZapowiedzPustyni",
    "opis_mapy": "swiat/dzungla_pas/krotki", "opis_planu": "plan_dzungli.json (krótki)",
})

NAGLOWEK_POTWOROW = """--[[
\tDanePotworow (DŻUNGLA) — WYGENEROWANE przez swiat/dzungla_pas_gra/generuj_dane.py z krótkiej mapy Dżungli
\t(swiat/dzungla_pas/krotki: plan_dzungli.json, znaczniki.json, czesci.json) i przeciwników Dżungli
\t(swiat/dzungla_pas_gra/przeciwnicy.py). NIE EDYTUJ RĘCZNIE: zmień plan, mapę albo konfigurację i uruchom
\tpython -B swiat/dzungla_pas_gra/generuj_dane.py.

\tFormat jak swiat/las_potwory/zrodla/DanePotworow.luau — w Studio Workspace/DzunglaPasGra/Moduly/DanePotworow; czytają
\tgo te same SerwerPotworow i KlientPotworow co w lesie. Współrzędne w układzie ŚWIATA (świat = (1100 + u; y; −700 + v)).
\tPoziomy stref z kalkulatora balansu (POZIOMY_STREF w generatorze), nie z planu.
]]
if not game:GetService("RunService"):IsStudio() then
\treturn {}
end
"""

NAGLOWEK_PASA = """--[[
\tDanePasa (DŻUNGLA) — WYGENEROWANE przez swiat/dzungla_pas_gra/generuj_dane.py z planu i mapy Dżungli. NIE EDYTUJ
\tRĘCZNIE. Liczby świata dla SerwerPasa, KlientPasa i MglaPasa (te same skrypty co las-pas i Bagno): przybycie, Kamień
\tPowrotu, brama do Pustyni i to, co za nią, mgła Dżungli, przelot kamery, Wąż Stu Lian; pole biom — nazwy i teksty
\tDżungli (uchwyt PrzeniesDoDzungli, klucze pamięci, prawo wejścia z bramy Bagna).
\tProstokąty to { x1, x2, z1, z2 } w poziomie świata; punkty to { x, y, z }.
]]
if not game:GetService("RunService"):IsStudio() then
\treturn {}
end
"""

NAGLOWEK_WALKI = """--[[
\tDane silnika walki DLA KONTENERA DŻUNGLI — WYGENEROWANE przez swiat/dzungla_pas_gra/generuj_dane.py. NIE EDYTUJ RĘCZNIE.
\tTo tools/walka/dane_walki.json BEZ ZMIAN (ten sam plik co src/server/Walka/Dane.luau) z dopisanymi na końcu listy
\tprzeciwnikami Dżungli z swiat/dzungla_pas_gra/przeciwnicy.py. Silnik (Statystyki, Przeciwnicy, Umiejetnosci, Silnik)
\tjest tą samą kopią co w lesie — zmieniają się tylko dane.
]]
"""


def tekst_walki():
    return NAGLOWEK_WALKI + "\nreturn " + GD_WALKI.luau(przeciwnicy.dane_walki_dzungli(), 0) + "\n"


def _dodatkowe(m, dp, dpa):
    return {CEL_WALKI: tekst_walki()}


def konfiguracja():
    k = dict(GEN.KONFIG)
    biom = dict(BIOM_DZUNGLI)
    biom["wymaganie"] = _wymaganie()
    k.update({
        "id": "dzungla",
        "mapa": MAPA,
        "gatunki": GATUNKI,
        "straznik_gatunek": "waz_stu_lian",
        "poziomy": (1, 30),
        "poziomy_stref": POZIOMY_STREF,
        "poziom_straznika": POZIOM_STRAZNIKA,
        "punkty_strumienia_u": PUNKTY_STRUMIENIA_U,
        "mgla_cel": MGLA_CEL,
        "wejscie_u": WEJSCIE_U,
        "ratunek_u": RATUNEK_U,
        "napis_bramy": ("ZAMKNIĘTE", "Pokonaj Węża Stu Lian"),
        "tabliczka": ("PUSTYNIA — WKRÓTCE", "tu zaczyna się następny biom"),
        "biom": biom,
        "cel_potworow": CEL_POTWOROW, "cel_pasa": CEL_PASA,
        "naglowek_potworow": NAGLOWEK_POTWOROW, "naglowek_pasa": NAGLOWEK_PASA,
        "polecenie": "python -B swiat/dzungla_pas_gra/generuj_dane.py",
        "opis_walki": "tools/walka/dane_walki.json + swiat/dzungla_pas_gra/przeciwnicy.py",
        "przeciwnicy_dodatkowi": [p["id"] for p in przeciwnicy.PRZEPISY],
        "pliki_aktorow": [os.path.join(REPO, "swiat", "test_walki2", "aktorzy_dzungli.py")],
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
