#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TABELA AKTORÓW prototypu walki v2 i przygotowanie ich danych (rig z klocków + klipy) — bez Studio.

    python -B swiat/test_walki2/aktorzy.py                 # przygotuj wszystkich aktorów (Blender pod wspólną blokadą)
    python -B swiat/test_walki2/aktorzy.py --tylko wojownik,mag
    python -B swiat/test_walki2/aktorzy.py --liniowo       # bez Blendera (klipy liniowo między kluczami — kanciaste)
    python -B swiat/test_walki2/aktorzy.py --lista         # tylko wypisz tabelę

Wynik: dane/<klucz>.json (rig w układzie Roblox, klipy co klatkę, wzrost, zasięg, punkty, chwile trafień).
zbuduj.py czyta te pliki i robi z nich szablony w Workspace/TestWalki2/Aktorzy oraz moduły danych dla klienta.
Blender jest potrzebny tylko tutaj (próbki krzywych klipów); budowa w Studio już go nie woła.

DODANIE AKTORA = wpis w AKTORZY (niżej) + `python -B swiat/test_walki2/aktorzy.py --tylko <klucz>` + zbuduj.py.
Pola wpisu:
  klucz       identyfikator aktora = id klasy albo przeciwnika w silniku walki (tools/walka/dane_walki.json)
  rola        "klasa" albo "przeciwnik"
  nazwa       nazwa na ekranie
  model       moduł postaci w swiat/postacie/<model>.py
  stroj       (opcjonalnie) strój z modułu (`<model>.stroj(nazwa)`, D-071: ekwipunek widać na modelu); brak = pierwsza
              postać z `zbuduj()` (pełny strój kanoniczny)
  przerobka   nazwa funkcji w przerobki.py (dodatki i klipy zastępcze) albo None
  zastepczy   None albo opis, czym model zastępuje docelowy (pokazywane w galerii i w README)
  kolory      {"RRGGBB": "RRGGBB"} — przemalowanie brył (tylko w prototypie; dziś nikt go nie używa)
  klipy       akcja -> nazwa klipu (albo None = brak klipu, odtwarzacz robi ruch proceduralny); akcje: AKCJE niżej
  umiejetnosci  id umiejętności z silnika -> nazwa klipu (None = proceduralnie)
  punkty      nazwa -> (zaczep, przesunięcie w układzie zaczepu, studs) — powstają jako Attachment „Punkt_<nazwa>”;
              Bron = czubek broni / pysk, Pocisk = skąd wylatuje pocisk lub czar, Piers = cel trafienia
  chwile      {klip: sekundy} — ręczna chwila trafienia / wypuszczenia pocisku; reszta liczy się sama (klatka, w której
              punkt Bron najdalej wysuwa się do przodu)
  chwile_modulu  (opcjonalnie) True = chwile ze słownika CHWILE modułu modelu ({klip: klatka}, przeliczone na sekundy
              z kl./s klipu) — ważniejsze od policzonych, słabsze od ręcznych `chwile`; tak autorzy klipów podają
              trafienie, wypuszczenie pocisku, uderzenie w tarczę i szarpnięcie przy trafieniu
  ruch_w_klipie  (opcjonalnie) klipy, które same przesuwają całą postać (kość LowerTorso: odskok, odepchnięcie na
              tarczy, wypad przy czarze, tupnięcie, wyskok) — odtwarzacz nie dokłada wtedy swojego ruchu proceduralnego
              (ślizg uniku, odrzut bloku, odrzut po wypuszczeniu pocisku, podskok przy krytyku i przy umiejętności na
              siebie); doskok do celu i odrzut po trafieniu zostają (to odległość i reakcja na cios, nie ruch klipu)
  celowanie   (opcjonalnie) klipy ciosu wręcz, w których broń w chwili trafienia jest daleko z boku osi aktora (np.
              miażdżący cios Rycerza: sztych 2,6 studa w prawo) — na czas doskoku odtwarzacz obraca atakującego o kąt
              atan(bok / przód) w stronę broni, więc sztych spada na oś celu (kąt i zasięg liczy zbuduj.py z punktu Bron)
  skala       (opcjonalnie) skala modelu w prototypie; brak = skala z modułu modelu
  zasiegi     (opcjonalnie) {klip: studs} — ręczny zasięg w chwili trafienia (zamiast punktu Bron): jak daleko przed
              aktorem klip „trafia” (np. kałuża kwasu, środek uścisku korzeni)
  wydluzenia  (opcjonalnie) {klip: [{"kosci": [...], "klatki": [[klatka, ułamek], ...], "luk": studs}]} — kości, które
              odtwarzacz przesuwa w biegu do przodu (układ aktora), żeby efekt z klipu (bańka, kałuża, korzenie) trafił
              w cel stojący dalej niż w klipie; ułamek liniowo między klatkami, luk = dodatkowe uniesienie w połowie
  zastepcze_klipy  klipy dorobione w przerobki.py (szkice), dla porządku i README

Bohaterowie (15.11, etap 8): Wojownik i Mag grają WŁASNE klipy walki z modułów rycerz.py i kot_mag.py (klipy
zaakceptowane przez właściciela, chwile z CHWILE modułów) — szkice z przerobki.py dla nich usunięte. Wojownik to strój
„bojowy” (pełny strój z tarczą rycerz_tarcza na LeftGripAttachment): postać wzorcowa silnika nosi tarczę (D-071).
Mag to pełny strój z zbuduj(): kapelusz na kości HatPivot, kostur na StaffPivot (w upadku spadają).

Skórowanie (`Postac.skoruj`, np. galareta Leśnego Slime'a na kościach Dol/Gora): klocki go nie oddają, więc dane
dostają opis skóry (`skora`) i numer skóry przy każdej bryle tej kości (kolumna 17 w `czesci`). W Studio bryły skóry
mają SpecialMesh, a moduł Klipy co klatkę przesuwa i rozciąga ich siatkę w pionie wg przesunięcia kości górnej
(to samo, co liniowe wagi Blendera dla brył w całości między y0 i y1).
"""
import argparse
import json
import math
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (REPO, os.path.join(REPO, "tools"), TU):
    if _s not in sys.path:
        sys.path.insert(0, _s)

DANE = os.path.join(TU, "dane")

# akcje, które odtwarzacz może zamówić u aktora (wspólne dla wszystkich)
AKCJE = ["spoczynek", "ruch", "atak", "krytyk", "blok", "unik", "trafienie", "upadek", "radosc"]

AKTORZY = [
    # ------------------------------------------------------------------ klasy gracza
    # Wojownik: Rycerz w stroju „bojowy” (pełny strój + tarcza rycerz_tarcza na LeftGripAttachment) — postać wzorcowa
    # silnika nosi tarczę (tools/walka/wzorcowe.py: tarcza = {blok: BLOK_TARCZY}), więc tarczę widać (D-071); jedna
    # tarcza: ta z modułu (dawna tarcza prototypu na TarczaAttachment usunięta). Wszystkie klipy z modułu, chwile z
    # rycerz.CHWILE: atak_miecz kl. 15, blok kl. 11 (cios w tarczę), trafienie kl. 4, ciecie kl. 18, miazdzacy_cios
    # kl. 22, kamienna_skora kl. 14 (tupnięcie; wcześniej ręczne 0,35 s).
    {"klucz": "wojownik", "rola": "klasa", "nazwa": "Wojownik", "model": "rycerz", "stroj": "bojowy", "przerobka": None,
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "chod", "atak": "atak_miecz", "krytyk": "atak_miecz", "blok": "blok",
               "unik": "unik", "trafienie": "trafienie", "upadek": "upadek", "radosc": "wiwat"},
     "umiejetnosci": {"ciecie": "ciecie", "miazdzacy_cios": "miazdzacy_cios", "kamienna_skora": "kamienna_skora"},
     # Bron = sztych miecza; Tarcza = godło na licu tarczy. Przesunięcie w układzie zaczepu RIGU ROBLOX (przód −Z):
     # w układzie modułu (przód +Z) to (0,89, 0,02, −0,42) — x i z mają odwrotny znak (sprawdzone na danych: punkt
     # leży na bryle „Godlo” w spoczynku i w bloku)
     "punkty": {"Bron": ("RightGripAttachment", (0, 3.9, 0)), "Pocisk": ("RightGripAttachment", (0, 2.4, 0)),
                "Piers": ("BodyFrontAttachment", (0, 0, 0)), "Tarcza": ("LeftGripAttachment", (-0.89, 0.02, 0.42))},
     "chwile_modulu": True,
     "chwile": {"unik": round(14 / 30.0, 3)},  # największy odskok w klipie unik (kl. 14, 1,7 studa w lewo)
     # klipy z własnym ruchem całej postaci: unik (odskok 1,7 studa w lewo i powrót), blok (0,41 studa w tył przy ciosie
     # w tarczę), miazdzacy_cios (wyskok 1,2 studa i wypad 0,9), kamienna_skora (tupnięcie kl. 14: biodra −0,11 studa —
     # podskok odtwarzacza unosiłby Rycerza w powietrze dokładnie w chwili tupnięcia)
     "ruch_w_klipie": ["unik", "blok", "miazdzacy_cios", "kamienna_skora"],
     # miażdżący cios: klinga w kl. 20–24 jest 1,4–3,3 studa w prawo od osi Rycerza — w Studio (15.11) mijała Cierniowego
     # Wilka i Muchomornika z boku i spadała obok nich; obrót o ok. 21° w lewo na czas doskoku kładzie sztych na osi celu
     "celowanie": ["miazdzacy_cios"],
     "zastepcze_klipy": []},
    {"klucz": "zwiadowca", "rola": "klasa", "nazwa": "Zwiadowca", "model": "zwiadowca", "przerobka": "zwiadowca",
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "wiwat"},
     "umiejetnosci": {"uderzenie_z_gory": "uderzenie_z_gory", "zatruta_strzala": "umiejetnosc", "skupienie": "skupienie"},
     "punkty": {"Bron": ("RightGripAttachment", (0, 1.3, 0)), "Pocisk": ("LeftGripAttachment", (0, 0, 0)),
                "Piers": ("BodyFrontAttachment", (0, 0, 0))},
     "chwile": {"umiejetnosc": 1.03, "skupienie": 0.4},
     "zastepcze_klipy": ["skupienie"]},
    # Mag: Kot-Mag w pełnym stroju z zbuduj() — kapelusz na kości HatPivot (KapeluszAttachment), kostur na StaffPivot
    # (KosturAttachment), więc w klipie upadek spadają. Wszystkie klipy z modułu, chwile z kot_mag.CHWILE: atak kl. 9,
    # kula_ognia kl. 27, lodowy_pocisk kl. 21 (wypuszczenie), bariera kl. 10 (krąg), trafienie kl. 4. Bez chwil z modułu
    # _chwile wybrałby klatkę z kryształem najdalej z przodu = dobicie po wypuszczeniu (dawne 1,23 s kuli ognia było złe).
    # Bloku nie ma (Mag nie nosi tarczy; silnik nie daje mu zdarzenia blok).
    {"klucz": "mag", "rola": "klasa", "nazwa": "Mag", "model": "kot_mag", "przerobka": None,
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "chod", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "wiwat"},
     "umiejetnosci": {"kula_ognia": "kula_ognia", "lodowy_pocisk": "lodowy_pocisk", "bariera": "bariera"},
     # Bron i Pocisk = kryształ kostura na KosturAttachment (kość StaffPivot): idzie za kosturem także w upadku
     # (na RightGripAttachment zostawałby w łapie, gdy kostur wypada — 4,3 studa od kryształu)
     "punkty": {"Bron": ("KosturAttachment", (0.08, 0.0, 2.15)), "Pocisk": ("KosturAttachment", (0.08, 0.0, 2.15)),
                "Piers": ("BodyFrontAttachment", (0, 0, 0))},
     "chwile_modulu": True,
     "chwile": {"unik": round(11 / 30.0, 3)},  # największy odskok w klipie unik (kl. 11, ok. 1,6 studa w tył i w lewo)
     # klipy z własnym ruchem całej postaci: unik (odskok i powrót), atak / kula_ognia / lodowy_pocisk (wypad 0,20 /
     # 0,30 / 0,38 studa do przodu wokół wypuszczenia — odrzut odtwarzacza 0,35 w tył ciągnąłby stopy po ziemi),
     # bariera (biodra w górę o 0,20 studa dokładnie w chwili kręgu, kl. 10)
     "ruch_w_klipie": ["unik", "atak", "kula_ognia", "lodowy_pocisk", "bariera"],
     "zastepcze_klipy": []},
    # ------------------------------------------------------------------ przeciwnicy lasu
    # Leśny Slime: właściwy model (swiat/postacie/lesny_slime.py, wersja 3 — sześcian 2,7 studa z kiełkiem).
    # Kwaśny plusk: bańka (kość Kula) i kałuża (kość Plusk) są w klipie — odtwarzacz nie puszcza osobnego pocisku,
    # tylko wydłuża w biegu tor bańki i miejsce kałuży do celu (WYDLUZENIA). Chwile z notatki modelu: pacnięcie
    # brzuszkiem kl. 13, plusk kałuży kl. 31.
    {"klucz": "lesny_slime", "rola": "przeciwnik", "nazwa": "Leśny Slime", "model": "lesny_slime", "przerobka": None,
     "zastepczy": None, "kolory": {}, "skala": 1.0,
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "wiwat"},
     "umiejetnosci": {"kwasny_plusk": "umiejetnosc"},
     # przód kostki (rig Roblox: przód = −Z): Bron = dolna połowa przedniej ściany (pacnięcie brzuszkiem),
     # Piers = środek przedniej ściany, Pocisk = buzia (start bańki), Plusk = środek kałuży
     "punkty": {"Bron": ("RootAttachment", (0, 1.0, -1.35)), "Pocisk": ("PyskAttachment", (0, 0, 0)),
                "Piers": ("RootAttachment", (0, 1.35, -1.35)), "Plusk": ("PluskAttachment", (0, 0, 0))},
     "chwile": {"atak": round(13 / 30.0, 3), "umiejetnosc": round(31 / 30.0, 3)},
     "zasiegi": {"umiejetnosc": 4.3},           # kałuża ok. 4,3 studa przed slime'em (PLUSK_Z w module modelu)
     "wydluzenia": {"umiejetnosc": [
         # bańka leci kl. 21–31 (ułamek wydłużenia rośnie z lotem, łuk wyżej), w kl. 32 wraca do schowka
         {"kosci": ["Kula"], "klatki": [[21, 0.0], [31, 1.0], [32, 0.0]], "luk": 1.2},
         # kałuża stoi kl. 31–65 (w kl. 30 i 66 jest w schowku w podstawie)
         {"kosci": ["Plusk"], "klatki": [[30, 0.0], [31, 1.0], [65, 1.0], [66, 0.0]]}]},
     # brzuszki schowane tuż pod ścianą (0,03 studa): na rigu z klocków prześwitywały jak soczewki — widoczne dopiero,
     # gdy klip wysuwa je na zewnątrz o więcej niż próg (kierunek w układzie kości Cialo, przód rigu = −Z)
     "chowane": {"BokL": ((-1, 0, 0), 0.05), "BokP": ((1, 0, 0), 0.05), "Przod": ((0, 0, -1), 0.05),
                 "Tyl": ((0, 0, 1), 0.05)},
     # galareta i kropelki: materiał Glass na rigu z klocków jest ciemny i szklisty (z przodu prawie butelkowy) —
     # w prototypie gładki plastik i jaśniejsza, soczysta zieleń jak na renderach (plik modelu bez zmian)
     "wyglad_roblox": {"materialy": {"Glass": ("SmoothPlastic", 0.0)},
                       "kolory": {"7EDB57": "8CE865", "B4F07F": "BDF58F"}},
     "zastepcze_klipy": []},
    {"klucz": "cierniowy_wilk", "rola": "przeciwnik", "nazwa": "Cierniowy Wilk", "model": "cierniowy_wilk", "przerobka": None,
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "ryk"},
     "umiejetnosci": {"rozszarpanie": "umiejetnosc"},
     "punkty": {"Bron": ("PyskAttachment", (0, 0, 0)), "Pocisk": ("PyskAttachment", (0, 0, 0)),
                "Piers": ("GlowaAttachment", (0, -0.9, 0.6))},
     "zastepcze_klipy": []},
    {"klucz": "muchomornik", "rola": "przeciwnik", "nazwa": "Muchomornik", "model": "muchomornik", "przerobka": None,
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "wiwat"},
     "umiejetnosci": {"chmura_zarodnikow": "umiejetnosc"},
     "punkty": {"Bron": ("LaskaAttachment", (0, 0, 0)), "Pocisk": ("ChmuraAttachment", (0, 0, 0)),
                "Piers": ("GlowaAttachment", (0, -1.4, 0))},
     "zastepcze_klipy": []},
    {"klucz": "lesny_troll", "rola": "przeciwnik", "nazwa": "Leśny Troll", "model": "lesny_troll", "przerobka": None,
     "zastepczy": None, "kolory": {},
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "ryk"},
     "umiejetnosci": {"ogluszajace_uderzenie": "umiejetnosc"},
     "punkty": {"Bron": ("MaczugaAttachment", (0, 0, 0)), "Pocisk": ("PyskAttachment", (0, 0, 0)),
                "Piers": ("GlowaAttachment", (0, -2.0, 0.4))},
     "zastepcze_klipy": []},
    # Strażnik Gaju (id silnika straznik_lasu): właściwy model (swiat/postacie/straznik_gaju.py, kolos 14,5 studa).
    # Uścisk korzeni: pięć korzeni (kości K1A…K5C) jest w klipie — odtwarzacz nie dokłada własnych, tylko przesuwa
    # w biegu korzenie pod cel (WYDLUZENIA). Chwile z notatki modelu: pięść kl. 17, zaciśnięcie korzeni kl. 50.
    {"klucz": "straznik_lasu", "rola": "przeciwnik", "nazwa": "Strażnik Gaju", "model": "straznik_gaju",
     "przerobka": None, "zastepczy": None, "kolory": {}, "skala": 1.0,
     "klipy": {"spoczynek": "idle", "ruch": "ruch", "atak": "atak", "krytyk": "atak", "blok": None, "unik": "unik",
               "trafienie": "trafienie", "upadek": "upadek", "radosc": "ryk"},
     "umiejetnosci": {"uscisk_korzeni": "umiejetnosc"},
     # Bron = prawa pięść (cios młotem z prawego barku), Piers = kryształ, Korzenie = środek uścisku na ziemi
     "punkty": {"Bron": ("PiescPAttachment", (0, 0, 0)), "Pocisk": ("KrysztalAttachment", (0, 0, 0)),
                "Piers": ("KrysztalAttachment", (0, 0, 0)), "Korzenie": ("KorzenieAttachment", (0, 0, 0))},
     "chwile": {"atak": round(17 / 30.0, 3), "umiejetnosc": round(50 / 30.0, 3)},
     "zasiegi": {"umiejetnosc": 6.6},           # środek uścisku 6,6 studa przed strażnikiem (UCISK w module modelu)
     "wydluzenia": {"umiejetnosc": [
         # korzenie są pod ziemią przed strażnikiem w kl. 31–79 (poza tym schowane w tułowiu)
         {"kosci": ["K1A", "K2A", "K3A", "K4A", "K5A"], "klatki": [[30, 0.0], [31, 1.0], [79, 1.0], [80, 0.0]]}]},
     "zastepcze_klipy": []},
]

PO_KLUCZU = {a["klucz"]: a for a in AKTORZY}


# --------------------------------------------------------------------------- przygotowanie danych
def _modul(wpis):
    from swiat.postacie.roblox_postac import wczytaj_modul
    return wczytaj_modul(os.path.join(REPO, "swiat", "postacie", wpis["model"] + ".py"))


def postac_aktora(wpis):
    """Postać z modułu modelu (strój `stroj` albo pierwsza postać z zbuduj()) + przeróbka prototypu (w pamięci)."""
    from swiat.postacie.roblox_postac import postacie_z_modulu
    import przerobki
    if wpis.get("stroj"):
        p = _modul(wpis).stroj(wpis["stroj"])
    else:
        p = postacie_z_modulu(os.path.join(REPO, "swiat", "postacie", wpis["model"] + ".py"))[0]
    if wpis.get("skala"):
        p.skala = float(wpis["skala"])
    if wpis.get("przerobka"):
        przerobki.PRZEROBKI[wpis["przerobka"]](p)
    return p


def _hex(c):
    return c.upper()


def _punkty(rig_dane, wpis):
    """Punkty z tabeli -> [nazwa, indeks kości, x, y, z] względem środka części kości (układ rigu Roblox)."""
    from geometria import cf, orientacja, punkt
    zaczepy = {z[0]: z for z in rig_dane["zaczepy"]}
    wynik = []
    for nazwa, (zaczep, off) in wpis["punkty"].items():
        z = zaczepy.get(zaczep)
        if z is None:
            raise ValueError("%s: punkt %s — model nie ma zaczepu %s (są: %s)"
                             % (wpis["klucz"], nazwa, zaczep, ", ".join(sorted(zaczepy))))
        p = punkt(cf((z[2], z[3], z[4]), orientacja(z[5], z[6], z[7])), tuple(float(v) for v in off))
        wynik.append([nazwa, z[1]] + [round(v, 4) for v in p])
    return wynik


def _chwile(rig, dane, wpis):
    """Chwila trafienia w klipach ataku i umiejętności: klatka, w której punkt Bron najdalej wysuwa się do przodu
    (−Z rigu) względem spoczynku. Zwraca {klip: sekundy}."""
    from geometria import punkt, razy, cf
    bron = next((pk for pk in dane["punkty"] if pk[0] == "Bron"), None)
    if not bron:
        return {}
    i = bron[1]
    off = (bron[2], bron[3], bron[4])
    klipy = set()
    for akcja in ("atak", "krytyk"):
        if wpis["klipy"].get(akcja):
            klipy.add(wpis["klipy"][akcja])
    for kl in wpis["umiejetnosci"].values():
        if kl:
            klipy.add(kl)
    wynik = {}
    for nazwa in sorted(klipy):
        kl = rig.klipy[nazwa]
        najlepsza, z_min = 0, 1e9
        for f in range(kl["dl"] + 1):
            pozy = rig.pozy(rig.transformy(nazwa, f))
            p = punkt(pozy[i], off)
            if p[2] < z_min - 1e-6:
                najlepsza, z_min = f, p[2]
        wynik[nazwa] = round(najlepsza / float(kl["fps"]), 3)
    return wynik


def _chwile_modulu(dane, wpis):
    """CHWILE modułu modelu ({klip: klatka}) -> {klip: sekundy} (kl./s klipu z danych). Klip spoza danych = błąd."""
    if not wpis.get("chwile_modulu"):
        return {}
    klipy = {k["n"]: k for k in dane["klipy"]}
    wynik = {}
    for klip, klatka in sorted(getattr(_modul(wpis), "CHWILE", {}).items()):
        if klip not in klipy:
            raise ValueError("%s: CHWILE modułu %s wskazuje klip %s, którego nie ma" % (wpis["klucz"], wpis["model"], klip))
        # ściśle wewnątrz klipu: chwila w klatce 0 albo w ostatniej to błąd w module (klip ma zamach i powrót)
        if not 0 < klatka < klipy[klip]["dl"]:
            raise ValueError("%s/%s: chwila kl. %s nie leży wewnątrz klipu (1…%d)"
                             % (wpis["klucz"], klip, klatka, klipy[klip]["dl"] - 1))
        wynik[klip] = round(klatka / float(klipy[klip]["fps"]), 3)
    return wynik


def _skora(p, d):
    """Skórowanie z modelu (p.skora: kość -> (kość górna, y0, y1)) -> d["skora"] = [{kosc, gora, y0, y1}] (indeksy kości
    rigu, wysokości w studach) i numer skóry (1, 2, …; 0 = brak) jako 17. kolumna każdej bryły."""
    indeks = {k[0]: i + 1 for i, k in enumerate(d["kosci"])}
    d["skora"] = []
    nr_kosci = {}
    for kosc, (gora, y0, y1) in sorted(getattr(p, "skora", {}).items()):
        if kosc not in indeks or gora not in indeks:
            raise ValueError("%s: skóra na kościach %s/%s, których nie ma w rigu" % (p.id, kosc, gora))
        d["skora"].append({"kosc": indeks[kosc], "gora": indeks[gora], "y0": round(y0 * p.skala, 4),
                           "y1": round(y1 * p.skala, 4)})
        nr_kosci[indeks[kosc]] = len(d["skora"])
    for c in d["czesci"]:
        c.append(nr_kosci.get(c[0], 0))
    if d["skora"]:
        d["uwagi"] = [u for u in d["uwagi"] if not u.startswith("skórowanie na dwóch kościach")]
        d["uwagi"].append("skórowanie (%s): w Studio siatki brył skóry przesuwa i rozciąga w pionie moduł Klipy"
                          % ", ".join(sorted(getattr(p, "skora", {}))))


def _wydluzenia(d, w):
    """Tabela WYDLUZENIA wpisu -> d["wydluzenia"] = {klip: [{kosci: [indeksy], klatki: [[f, ułamek]], luk}]}."""
    indeks = {k[0]: i + 1 for i, k in enumerate(d["kosci"])}
    klipy = {k["n"]: k for k in d["klipy"]}
    d["wydluzenia"] = {}
    for klip, lista in (w.get("wydluzenia") or {}).items():
        if klip not in klipy:
            raise ValueError("%s: wydłużenie dla klipu %s, którego nie ma" % (w["klucz"], klip))
        wyn = []
        for s in lista:
            brak = [n for n in s["kosci"] if n not in indeks or indeks[n] not in klipy[klip]["kosci"]]
            if brak:
                raise ValueError("%s/%s: wydłużenie kości %s, których nie ma w rigu albo w klipie" % (w["klucz"], klip, brak))
            klatki = [[float(f), float(u)] for f, u in s["klatki"]]
            if any(klatki[i][0] >= klatki[i + 1][0] for i in range(len(klatki) - 1)):
                raise ValueError("%s/%s: klatki wydłużenia nie rosną" % (w["klucz"], klip))
            wyn.append({"kosci": [indeks[n] for n in s["kosci"]], "klatki": klatki, "luk": float(s.get("luk", 0.0))})
        d["wydluzenia"][klip] = wyn


def przygotuj(wpisy, liniowo=False):
    from swiat.postacie.biblioteka.roblox_klocki import probki_liniowe, rig
    from swiat.postacie.roblox_postac import probki_z_blendera
    from geometria import Rig, obwiednia
    postacie = []
    for w in wpisy:
        p = postac_aktora(w)
        p.id = w["klucz"]                                      # osobne próbki dla dwóch aktorów z jednego modelu
        bledy, uwagi = p.sprawdz()
        if bledy:
            sys.exit("%s: postać nie przeszła sprawdzianu:\n  %s" % (w["klucz"], "\n  ".join(bledy)))
        postacie.append((w, p))
    if liniowo:
        probki = {p.id: probki_liniowe(p) for _, p in postacie}
    else:
        print("próbki klipów z Blendera (wspólna blokada) dla: %s" % ", ".join(p.id for _, p in postacie), flush=True)
        probki = probki_z_blendera([p for _, p in postacie])
    os.makedirs(DANE, exist_ok=True)
    for w, p in postacie:
        d = rig(p, probki.get(p.id))
        for c in d["czesci"]:
            c[12] = _hex(w["kolory"].get(_hex(c[12]), c[12]))
        nazwy_klipow = {k["n"] for k in d["klipy"]}
        brak = [v for v in list(w["klipy"].values()) + list(w["umiejetnosci"].values()) + w.get("ruch_w_klipie", [])
                + w.get("celowanie", [])
                if v and v not in nazwy_klipow]
        if brak:
            sys.exit("%s: tabela wskazuje klipy, których nie ma: %s (są: %s)"
                     % (w["klucz"], ", ".join(sorted(set(brak))), ", ".join(sorted(nazwy_klipow))))
        d["punkty"] = _punkty(d, w)
        _skora(p, d)
        _wydluzenia(d, w)
        r = Rig(d)
        mn, mx = obwiednia(r)
        promien = 0.0
        for c in d["czesci"]:
            from geometria import narozniki
            for q in narozniki(r.czesc_cf(c, r.pozy()), c[9:12]):
                promien = max(promien, math.hypot(q[0], q[2]))
        d["wymiary"] = {"wysokosc": round(mx[1], 3), "spod": round(mn[1], 3), "szerokosc": round(mx[0] - mn[0], 3),
                        "glebokosc": round(mx[2] - mn[2], 3), "przod": round(-mn[2], 3), "promien": round(promien, 3)}
        d["chwile"] = dict(_chwile(r, d, w), **_chwile_modulu(d, w))
        d["chwile"].update(w.get("chwile", {}))
        d["klucz"] = w["klucz"]
        d["model_modulu"] = w["model"]
        d["zrodlo_probek"] = "liniowo" if liniowo else "blender"
        sciezka = os.path.join(DANE, w["klucz"] + ".json")
        with open(sciezka, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, separators=(",", ":"))
        print("%-15s %3d części, %2d kości, wzrost %.2f, zasięg %.2f, klipy: %s"
              % (w["klucz"], len(d["czesci"]), len(d["kosci"]), d["wymiary"]["wysokosc"], d["wymiary"]["promien"],
                 ", ".join(k["n"] for k in d["klipy"])))
        print("                chwile: %s" % ", ".join("%s %.3f" % kv for kv in sorted(d["chwile"].items())))
        if d["uwagi"]:
            for u in d["uwagi"]:
                print("                uwaga:", u)


def wczytaj(klucz):
    sciezka = os.path.join(DANE, klucz + ".json")
    if not os.path.isfile(sciezka):
        raise FileNotFoundError("brak %s — uruchom: python -B swiat/test_walki2/aktorzy.py --tylko %s" % (sciezka, klucz))
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Przygotowanie danych aktorów prototypu walki v2")
    ap.add_argument("--tylko", default="")
    ap.add_argument("--liniowo", action="store_true")
    ap.add_argument("--lista", action="store_true")
    a = ap.parse_args()
    if a.lista:
        for w in AKTORZY:
            print("%-15s %-10s %-15s model %-15s %s" % (w["klucz"], w["rola"], w["nazwa"], w["model"], w["zastepczy"] or ""))
        return
    wybrane = [x for x in a.tylko.split(",") if x] or [w["klucz"] for w in AKTORZY]
    for k in wybrane:
        if k not in PO_KLUCZU:
            sys.exit("nie ma aktora %r (są: %s)" % (k, ", ".join(PO_KLUCZU)))
    przygotuj([PO_KLUCZU[k] for k in wybrane], a.liniowo)


if __name__ == "__main__":
    main()
