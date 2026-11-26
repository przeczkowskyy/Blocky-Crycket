#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator zrodla/DaneStanu.luau — liczby i nazwy pakietu „stan gracza” dla serwera i klienta w Studio.

    python -B swiat/stan_gracza/dane.py               # zapisuje zrodla/DaneStanu.luau
    python -B swiat/stan_gracza/dane.py --sprawdz     # kod 1, gdy plik w zrodla/ jest nieaktualny

JEDNA PRAWDA LICZB (tylko odczyt, nic tu nie jest przepisane ręcznie z cudzych plików):
  • tools/walka/wzorcowe.py — pula punktów (30 + 10 na poziom), rozkłady klas, umiejętności i sloty (1/2/3 od poziomów
    1/5/10), broń i pancerz z przedmiotów (wzór od poziomu), tarcza Wojownika;
  • tools/walka/tempo.py — krzywa doświadczenia A × L^B (A = DOMYSLNE_A, B = 1,6: las ok. 30 min, propozycja);
  • src/server/Walka/Statystyki.luau — Statystyki.ATRYBUTY_GRACZA (atrybuty gracza Strength… → statystyki silnika).
Rozkłady klas są też w src/shared/ClassData.luau (Paweł, procent puli); serwer czyta je stamtąd, a testy pilnują, że
są równe wzorcowym. Przypadki wzorcowe liczy lustro logika_stanu.py.
"""
import hashlib
import inspect
import json
import os
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
WALKA = os.path.join(REPO, "tools", "walka")
for _s in (TU, WALKA):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import logika_stanu as LS  # noqa: E402
import tempo  # noqa: E402
import wzorcowe  # noqa: E402

PLIK_LUAU = "DaneStanu.luau"
ZRODLA = os.path.join(TU, "zrodla")
STATYSTYKI_LUAU = os.path.join(REPO, "src", "server", "Walka", "Statystyki.luau")

# atrybut gracza Class (src/server/ClassSelect.server.luau, ClassData.id) → klasa silnika walki
KLASY_GRACZA = {"Warrior": "wojownik", "Scout": "zwiadowca", "Mage": "mag"}

# JEDNO MIEJSCE: które pakiety mogą rozmawiać ze stanem gracza (nazwy kontenerów w Workspace). Jak dodać pakiet:
# dopisz nazwę jego kontenera tutaj, uruchom `python -B swiat/stan_gracza/dane.py` i testy, przebuduj StanGracza
# (`zbuduj.py --skrypty` wystarcza — DaneStanu to moduł). Nazwy niezbudowanych jeszcze kontenerów nic nie psują.
#  • BIOMY — kontenery z walkami biomu (kod SerwerPotworow): ich łup przyjmuje Sygnaly/PrzyznajLup i tylko w ich
#    walkach działa kara za przegraną (tablica próby TestWalki2 łupu nie wysyła);
#  • WYDATKI — kontenery, które mogą wydawać Złoto gracza (Sygnaly/WydajZloto, Pety "kup");
#  • PRZYCHODY — kontenery, które mogą DOPISAĆ Złoto (Rybki, D-146) poza walką (Sygnaly/Pety "przychod"; 25.11.2026:
#    zagroda petów — pety stojące w zagrodzie dają Rybki na sekundę, kwotę liczy serwer petów).
PAKIETY_BIOMOW = ["LasPotwory", "LasPasGra", "BagnoPasGra", "DzunglaPasGra"]   # 18.11: Dżungla (trzeci biom)
PAKIETY_WYDATKOW = ["PetyProba", "KowalProba"]                                # 18.11: Kowal (D-102)
PAKIETY_PRZYCHODOW = ["PetyProba"]                                            # 25.11: zagroda petów (Rybki/s)

# punkty statystyk za poziom (D-097 ✅ 17.11: „5 punktów do rozdania za poziom”). PUNKTY_SAMO_NA_POZIOM = ile
# punktów na poziom rozdziela się SAMO rozkładem klasy: 5 = wariant b (odstępstwo przyjęte roboczo dla balansu — suma
# 10 jak przy strojeniu potworów); 0 = czysty wariant a z D-097 (las ok. 61 zamiast 31 min — punkty_statystyk.py)
PUNKTY_DO_ROZDANIA = 5
PUNKTY_SAMO_NA_POZIOM = 5

# Gemy bez płacenia (D-099 ✅ 17.11; liczby „do zmiany”, tools/walka/REBIRTH_1711.md część 1): za każdy awans i za
# pierwsze pokonanie strażnika każdego biomu (gatunek zaczyna się od PREFIKS_STRAZNIKA); za co dziesiątą wygraną
# i z kopalni — jeszcze nie (README)
# zapis postępu między sesjami (18.11.2026; WŁĄCZONY 19.11.2026 decyzją D-110 Karola, czeka na potwierdzenie Pawła):
# False = wyłączony dla wszystkich; atrybut kontenera ZapisPostepu = false wyłącza go w jednym miejscu (README „Zapis
# postępu”). Próby gry w Play zaczynają od świeżego gracza bez zapisu (znacznik próby, tools/zapis_prob.py).
ZAPIS_WLACZONY = True

# „szczęście początkującego” (18.11.2026): dopóki gracz nie ma żadnej wygranej, jego sześć statystyk w walce ×(1 + tyle)
# (pole silnika pet przez źródło w Modyfikatory); 0 = wyłączone. 1,75 (×2,75) = najmniejszy mnożnik, przy którym
# każda klasa (rozkłady wzorcowe, 1. poziom) wygrywa ze slime'em 3. poziomu w ≥ 95% walk (96/96/95%; slime 1. i 2.
# poziomu 99–100%) — po D-096 w pierwszej zagrodzie chodzą slime'y 1.–3. poziomu (README, punkt 2b)
SZCZESCIE_POCZATKUJACEGO = 1.75

GEMY_ZA_POZIOM = 10
GEMY_ZA_STRAZNIKA = 100
PREFIKS_STRAZNIKA = "straznik_"

# rozkłady statystyk klas (pytanie 56, odpowiedź Karola 17.11: „b” — czeka na potwierdzenie Pawła): "wzorcowe" =
# walka i punkty według tools/walka/wzorcowe.py, profil z src/shared/ClassData.luau tylko na karcie wyboru klasy;
# "classdata" = jak przed 18.11 (punkty według ClassData). Atrybut kontenera RozkladyKlas przełącza w Studio.
ROZKLADY_KLAS = "wzorcowe"

# kara za przegraną (propozycja D-098): ułamek posiadanego Złota; 0 = wyłączona. Liczby: kara_przegranej.py, README.
KARA_PROCENT = 0.05
ZWYKLY_POTWOR = "cierniowy_wilk"   # łup zwykłego potwora (limit kary); zwykłe potwory Bagna mają ten sam łup


def silnik_stala(nazwa):
    import silnik  # noqa: E402  (tools/walka — tylko odczyt)
    return silnik.STALE[nazwa]


def pasywki_silnika():
    """Pasywki, które silnik zna i które działają przez modyfikatory (pole premie opisu postaci): pasywne umiejętności
    klas (silnik.PASYWNE) i pasywki broni (silnik.PASYWKI_BRONI); bez tych bez modyfikatorów (Wskrzeszenie działa
    tylko ze slotu). → {nazwa: {klasa, modyfikatory, rodzaj}}"""
    import silnik  # noqa: E402
    w = {}
    for rodzaj, zrodlo in (("umiejetnosc", silnik.PASYWNE), ("bron", silnik.PASYWKI_BRONI)):
        for n in sorted(zrodlo):
            d = zrodlo[n]
            if d.get("modyfikatory"):
                w[n] = {"klasa": d["klasa"], "modyfikatory": dict(d["modyfikatory"]), "rodzaj": rodzaj}
    return w


def zaklecia_silnika():
    import silnik  # noqa: E402
    return sorted(silnik.ZAKLECIA)


def granice_modyfikatorow():
    import silnik  # noqa: E402
    return {m["id"]: [m["min"], m["max"]] for m in silnik.MODYFIKATORY}


def limit_lupu_zwyklego():
    """Złoto zwykłego potwora z silnika (tools/walka/silnik.py, PRZECIWNICY[…].lup.zloto = [baza, przyrost])."""
    import silnik  # noqa: E402  (tools/walka — tylko odczyt)
    para = silnik.PRZECIWNICY[ZWYKLY_POTWOR]["lup"]["zloto"]
    if len(para) != 2 or any(isinstance(x, bool) or not isinstance(x, int) or x < 0 for x in para):
        raise BladDanych("łup Złota %s w silniku nie jest parą liczb całkowitych: %s" % (ZWYKLY_POTWOR, para))
    return {"baza": para[0], "na_poziom": para[1]}


class BladDanych(Exception):
    pass


def atrybuty_gracza_silnika():
    """Statystyki.ATRYBUTY_GRACZA z src/server/Walka/Statystyki.luau → {statystyka silnika: atrybut gracza}."""
    with open(STATYSTYKI_LUAU, encoding="utf-8") as f:
        tekst = f.read()
    m = re.search(r"Statystyki\.ATRYBUTY_GRACZA = \{(.*?)\n\}", tekst, re.S)
    if not m:
        raise BladDanych("brak Statystyki.ATRYBUTY_GRACZA w %s" % STATYSTYKI_LUAU)
    pary = re.findall(r"(\w+) = \"(\w+)\"", m.group(1))
    w = {silnik: atr for atr, silnik in pary}
    if sorted(w) != sorted(wzorcowe.STATYSTYKI):
        raise BladDanych("ATRYBUTY_GRACZA nie pokrywa sześciu statystyk: %s" % w)
    return {s: w[s] for s in wzorcowe.STATYSTYKI}


def progi_slotow():
    """wzorcowe.sloty(poziom) → lista progów { od, n } od najwyższego (sprawdzane do 200. poziomu)."""
    progi, poprzedni = [], None
    for L in range(1, 201):
        n = wzorcowe.sloty(L)
        if n != poprzedni:
            progi.append({"od": L, "n": n})
            poprzedni = n
    return list(reversed(progi))


def podstawa():
    """Dane bez przypadków i skrótu."""
    # broń i pancerz z przedmiotów: wzory liniowe od poziomu (baza = wartość dla 0, przyrost = różnica 1 − 0)
    bron0, bron1 = wzorcowe.bron(0), wzorcowe.bron(1)
    panc0, panc1 = wzorcowe.pancerz_przedmiotow(0), wzorcowe.pancerz_przedmiotow(1)
    for L in (2, 7, 33):
        if wzorcowe.bron(L) != bron0 + (bron1 - bron0) * L or wzorcowe.pancerz_przedmiotow(L) != panc0 + (panc1 - panc0) * L:
            raise BladDanych("wzorcowe.bron / pancerz_przedmiotow nie są liniowe — zmień dane.py")
    # tarcza: postać wzorcowa klasy ma pole tarcza
    tarcza = {k: True for k in wzorcowe.KLASY if "tarcza" in wzorcowe.postac(k, 1)}
    if inspect.signature(tempo.xp_do_nastepnego).parameters.keys() != {"L", "A", "B"}:
        raise BladDanych("tempo.xp_do_nastepnego ma inną sygnaturę — sprawdź krzywą")
    D = {
        "wersja": 1,
        "kontener": "StanGracza",
        "prefiks": "[StanGracza] ",
        # 2 (17.11.2026): pety i licznik wydatków w profilu (swiat/pety_proba); 3 (18.11.2026): dane pakietów
        # (Sygnaly/DanePakietu — pole pakiety; profil 2 dostaje puste pakiety)
        # 4 (18.11.2026, zapis postępu): idKlasy i atrybuty innych pakietów (przeloty, strażnicy biomów, strój)
        "wersja_profilu": 4,
        "krzywa": {"a": tempo.DOMYSLNE_A, "b": 1.6},
        "pula": {"baza": wzorcowe.PUNKTY_START, "na_poziom": wzorcowe.PUNKTY_NA_POZIOM},
        "sloty": progi_slotow(),
        "wzor": {"bron_baza": bron0, "bron_na_poziom": bron1 - bron0, "pancerz_baza": panc0,
                 "pancerz_na_poziom": panc1 - panc0, "blok_tarczy": wzorcowe.BLOK_TARCZY},
        "statystyki": list(wzorcowe.STATYSTYKI),
        "klasy": list(wzorcowe.KLASY),
        "klasa_domyslna": wzorcowe.KLASY[0],
        "klasy_gracza": dict(KLASY_GRACZA),
        "nazwy_klas": {k: wzorcowe.postac(k, 1)["nazwa"] for k in wzorcowe.KLASY},
        "rozklady": {k: dict(wzorcowe.ROZKLADY[k]) for k in wzorcowe.KLASY},
        "umiejetnosci": {k: list(wzorcowe.UMIEJETNOSCI[k]) for k in wzorcowe.KLASY},
        "tarcza": tarcza,
        "atrybuty_statystyk": atrybuty_gracza_silnika(),
        # atrybuty gracza: pięć pierwszych ustawia dziś src/server/PlayerStatsDefaults (Paweł), Class — ClassSelect;
        # ShardyEwolucji i TokenyKrainy_<kraina> są tego pakietu (HUD ich jeszcze nie pokazuje)
        "atrybuty": {"klasa": "Class", "poziom": "Level", "xp": "XP", "xp_max": "XPMax", "zloto": "Gold", "gemy": "Gems",
                     "shardy": "ShardyEwolucji", "tokeny_prefiks": "TokenyKrainy_"},
        "pola_lupu": ["zloto", "doswiadczenie", "tokeny_krainy", "gemy", "shard_ewolucji"],
        "limity": {
            "poziom_maks": 999,             # silnik przyjmuje do 1000
            "statystyka_maks": 9999,        # jak MAX_VALUE w src/server/StatPoints.server.luau
            "waluta_maks": 999999999999,
            "przyrost_maks": 100,           # jeden przyrost z Training Center
            "dlugosc_nazwy": 24,            # kraina w łupie
            "czas_walki_maks": 900,         # s — walka.czas od lasu
            "oczekujace_maks": 20,          # łupy czekające na pokazanie u jednego gracza
            "lup": {"zloto": 1000000, "doswiadczenie": 1000000, "tokeny_krainy": 100, "gemy": 100, "shard_ewolucji": 10},
        },
        # łup przyznaje się od razu do profilu, a do atrybutów (HUD) — po walce: gdy klient zgłosi, że HUD znów widać
        # (koniec ekranu walki), albo najpóźniej po czasie walki + zapas_s; zgłoszenie klienta pokazuje tylko łupy
        # starsze niż min_s (żeby spóźnione zgłoszenie nie pokazało łupu kolejnej walki w jej trakcie)
        "publikacja": {"zapas_s": 6, "min_s": 1.5, "odstep_pokaz_s": 0.5},
        # kontenery z kodem potworów, których łup przyjmujemy (każdy nowy biom: dopisać jego kontener; 17.11.2026 Bagno)
        "zrodla": list(PAKIETY_BIOMOW),
        # wydawanie Złota (Sygnaly/WydajZloto i Sygnaly/Pety "kup", 17.11.2026): kto może wydawać (nazwy kontenerów
        # pakietów) i największa jedna kwota; licznik wydatków na cel (np. kupione jajka) jest w profilu
        "wydatki": {"zrodla": list(PAKIETY_WYDATKOW), "kwota_maks": 1000000},
        # przychody spoza walki (Sygnaly/Pety "przychod", 25.11.2026 — zagroda petów): kto może dopisać Złoto i
        # największa jedna kwota (naliczanie co kilka sekund — setki, nie tysiące); bez premii i bez licznika walk
        "przychody": {"zrodla": list(PAKIETY_PRZYCHODOW), "kwota_maks": 100000},
        # pety w profilu (swiat/pety_proba): kopie każdego peta (kopia = shard peta, D-058), aktywny pet i jego premia
        # do łupu z walk (wartości premii przysyła pakiet petów — tu tylko granice); atrybuty gracza dla klientów
        "pety": {"rodzajow_maks": 100, "kopii_maks": 1000000, "premia_maks": 0.5,
                 "atrybut_aktywnego": "PetAktywny", "atrybut_liczby": "PetyLiczba"},
        # kara za przegraną (17.11.2026, realizacja propozycji D-098 — czeka na zatwierdzenie w panelu): `procent`
        # posiadanego Złota (0 = kara wyłączona; JEDNA liczba do zmiany), najwyżej łup zwykłego potwora na poziomie
        # przeciwnika (limit_lupu = łup Cierniowego Wilka z silnika, jak zwykłe potwory Bagna); tylko walki z kontenerów
        # `zrodla` (las-pas, stary las, Bagno — nie tablica próby, nie tryb testowy TestBohater, który łupu nie wysyła);
        # atrybut kontenera StanGracza `atrybut_wylacznika` = false wyłącza karę w czasie gry (próby, testy)
        "kara": {"procent": KARA_PROCENT, "limit_lupu": limit_lupu_zwyklego(), "zrodla": list(PAKIETY_BIOMOW),
                 "atrybut_wylacznika": "KaraPrzegranej", "komunikat": "Przegrana: −%s, +%d doświadczenia",
                 "komunikat_bez_zlota": "Przegrana: +%d doświadczenia", "czas_s": 3.5,
                 # waluta to Rybki (atrybut Gold, D-146): odmiana przy liczbie — 1 Rybka, 2–4 / 22–24… Rybki, reszta Rybek
                 "formy_rybki": ["Rybka", "Rybki", "Rybek"]},
        # modyfikatory bohatera (18.11.2026, Sygnaly/Modyfikatory — pety D-101, Kowal D-102): granice jednego wpisu
        # źródła i złożenia; pasywki = nazwy z silnika z ich modyfikatorami (pole premie opisu postaci)
        "modyfikatory": {"zrodel_maks": 16, "statystyka_maks": 1000, "procent_maks": 1, "procent_suma_maks": 3,
                         "lup_maks_zrodla": 0.5, "lup_suma_maks": 1, "bron_maks": 1000, "pancerz_maks": 1000,
                         "tarcza_maks": 0.5, "pasywek_maks": 6, "blok_maks": silnik_stala("blok_maks"),
                         "zrodlo_pety": "pety"},
        "pasywki_silnika": pasywki_silnika(),
        # zaklęcia broni, które zna silnik (silnik.ZAKLECIA; pole bron.zaklecie opisu postaci) — pole `zaklecie` wpisu
        "zaklecia_silnika": zaklecia_silnika(),
        "granice_modyfikatorow": granice_modyfikatorow(),
        # dane pakietów w profilu (Sygnaly/DanePakietu): tylko wartości dające się zapisać, z limitem rozmiaru
        "pakiety": {"wartosci_maks": 2000, "glebokosc_maks": 8, "napis_maks": 200, "pakietow_maks": 32},
        # punkty statystyk (18.11.2026, realizacja propozycji D-097 — czeka na zatwierdzenie): za poziom 5 do rozdania
        # przez gracza + 5 rozdawanych samo rozkładem klasy (suma jak dziś: pula.na_poziom = 10); „+” w oknie ekwipunku
        # (StatPoints Pawła — pliki nietknięte) zdejmuje punkt z puli, bez punktu zmiana jest cofana z komunikatem.
        # Atrybut kontenera `atrybut_wylacznika` = false: jak przed D-097 (10 samo, darmowy „+”).
        "punkty": {"na_poziom": PUNKTY_DO_ROZDANIA, "auto_na_poziom": PUNKTY_SAMO_NA_POZIOM,
                   "atrybut": "PunktyDoRozdania", "atrybut_wylacznika": "PunktyStatystyk",
                   "komunikat_brak": "Brak punktów — zdobądź poziom", "licznik": "Punkty do rozdania: %d"},
        "poczatek": {"procent": SZCZESCIE_POCZATKUJACEGO, "zrodlo": "szczescie_poczatkujacego",
                     "atrybut_wylacznika": "SzczesciePoczatkujacego"},
        "gemy": {"za_poziom": GEMY_ZA_POZIOM, "za_straznika": GEMY_ZA_STRAZNIKA, "prefiks_straznika": PREFIKS_STRAZNIKA,
                 "komunikat_straznika": "+%d Gemów za pierwsze pokonanie strażnika!"},
        # zapis postępu między sesjami (18.11.2026; włączony 19.11.2026, D-110 — ZAPIS_WLACZONY; atrybut kontenera
        # `atrybut` = false wyłącza): DataStore z blokadą sesji (zapisywana w rekordzie), UpdateAsync z ponawianiem; README.
        # `proba` (19.11.2026): znacznik próby gry w Play — atrybut kontenera `atrybut_do` = os.time(), do którego trwa
        # (ustawia go tools/zapis_prob.py w trybie Edit tuż przed Play, zdejmuje po Stop; najwyżej `czas_s` naprzód, sam
        # wygasa). Przy znaczniku serwer NIE czyta i NIE pisze prawdziwego zapisu (gracz jak dawniej: świeży, w pamięci),
        # a z `atrybut_magazynu` = true pracuje na osobnym magazynie próby (magazyn + przyrostek_studio + `przyrostek`) —
        # tylko tam działa atrapa błędów usługi (`atrybut_bledow` = ile kolejnych wywołań ma paść)
        "zapis": {"wlaczony": ZAPIS_WLACZONY, "atrybut": "ZapisPostepu", "magazyn": "BC_StanGracza_v1",
                  "proba": {"atrybut_do": "ZapisProbaDo", "atrybut_magazynu": "ZapisProbaMagazyn",
                            "atrybut_bledow": "ZapisProbaBledy", "przyrostek": "_Proba", "czas_s": 900},
                  "przyrostek_studio": "_Studio", "klucz": "player_",
                  "pola": ["wersja", "klasa", "idKlasy", "poziom", "xp", "zloto", "gemy", "tokeny", "shardy", "wytrenowane",
                           "walki", "awanse", "pety", "wydatki", "pakiety", "punkty", "straznicy", "atrybuty"],
                  "atrybuty_prefiksy": ["WidzialPrzelot", "PokonalStraznika", "StrojProba_"],
                  "limity": {"wartosci_maks": 70000, "glebokosc_maks": 10, "napis_maks": 200, "bajty_maks": 3000000},
                  "proby": 4, "odstep_s": 1, "proby_blokady": 6, "czekaj_blokada_s": 5, "blokada_s": 600,
                  "co_s": 120, "rozrzut_s": 30, "zamkniecie_s": 25, "budzet_min": 2,
                  # nowy gracz z włączonym zapisem: wartości startowe zamiast testowych z PlayerStatsDefaults (Paweł)
                  "start": {"gemy": 0, "zloto": 0}},
        "rozklady_klas": {"tryb": ROZKLADY_KLAS, "atrybut": "RozkladyKlas", "tryby": ["wzorcowe", "classdata"]},
        "klasy_pawla": {"folder": "Shared", "modul": "ClassData", "czekaj_s": 10},
        "trening": {"kontener": "TreningProba", "sygnal": "PrzyrostStatystyki"},
        "hud": {"gui": "HUD", "czekaj_s": 60},
        "baner": {"gui": "StanGraczaBaner", "tekst": "POZIOM %d", "podpis": "AWANS!", "podpis_wiele": "AWANS x%d!",
                  "czas_s": 2.6, "opoznienie_po_hud_s": 0.5, "wysokosc": 0.24, "szer_px": 460, "wys_px": 130,
                  "kolor_tekstu": "FFD23F", "kolor_obrysu": "17121F", "kolor_podpisu": "FFFFFF", "kolejnosc": 30},
        "dzwiek": {"kontener": "DzwiekGra", "modul": "KatalogDzwiekow", "zdarzenie": "awans",
                   "wbudowany": "rbxasset://sounds/volume_slider.ogg", "nuty": [1, 1.26, 1.5, 2], "odstep_s": 0.11,
                   "glosnosc": 0.5},
    }
    return D


def przypadki(D):
    """Przypadki wzorcowe z lustra (LogikaStanu.sprawdzPrzypadki porównuje je w Studio). None → false."""
    def nil(v):
        return False if v is None else v
    P = {}
    P["xp"] = [{"poziom": L, "wynik": LS.xp_do_nastepnego(D, L)} for L in (1, 2, 3, 5, 10, 11, 20, 50, 100, 998, 999)]
    P["awans"] = []
    for poziom, xp, dodaj in ((1, 0, 0), (1, 0, 11), (1, 0, 12), (1, 5, 100), (2, 34, 1), (3, 10, 5000),
                              (998, 0, 10 ** 9), (999, 7, 50), (5, 153, 1)):
        p, x, i = LS.awans(D, poziom, xp, dodaj)
        P["awans"].append({"poziom": poziom, "xp": xp, "dodaj": dodaj, "wynik": [p, x, i]})
    P["rozdziel"] = []
    for k in D["klasy"]:
        for punkty in (0, 30, 40, 130, 1000, 2017):
            P["rozdziel"].append({"klasa": k, "punkty": punkty, "wynik": LS.rozdziel(D, D["rozklady"][k], punkty)})
    P["opis"] = []
    for k, L, extra in (("wojownik", 1, {}), ("mag", 5, {"inteligencja": 7}), ("zwiadowca", 10, {"sila": 3, "pancerz": 1})):
        st = LS.rozdziel(D, D["rozklady"][k], LS.pula(D, L))
        for s, v in extra.items():
            st[s] += v
        P["opis"].append({"klasa": k, "poziom": L, "st": st, "wynik": LS.opis_bohatera(D, k, L, st)})
    P["nowe"] = []
    cel1 = LS.rozdziel(D, D["rozklady"]["mag"], LS.pula(D, 1))
    cel2 = LS.rozdziel(D, D["rozklady"]["mag"], LS.pula(D, 2))
    celw = LS.rozdziel(D, D["rozklady"]["wojownik"], LS.pula(D, 2))
    wytr = {s: 0 for s in D["statystyki"]}
    wytr["sila"] = 4
    obecne = {"sila": 20, "kondycja": 16, "inteligencja": 18, "zrecznosc": 12, "szczescie": 7, "pancerz": 57}
    po = {s: cel1[s] + wytr[s] for s in D["statystyki"]}
    po_plus = dict(po)
    po_plus["szczescie"] += 2
    for obc, baza, cel in ((obecne, None, cel1), (po, cel1, cel2), (po_plus, cel1, cel2), (po_plus, cel2, celw)):
        P["nowe"].append({"obecne": obc, "baza": nil(baza), "cel": cel, "wytrenowane": wytr,
                          "wynik": LS.nowe_statystyki(D, obc, baza, cel, wytr)})
    P["lup"] = []
    dobry = {"zloto": 21, "doswiadczenie": 12, "tokeny_krainy": 1, "gemy": 0, "shard_ewolucji": 0, "kraina": "las"}
    zle = [dict(dobry, zloto=-1), dict(dobry, doswiadczenie=2.5), dict(dobry, gemy=101), dict(dobry, kraina="la s"),
           dict(dobry, kraina="x" * 25), dict(dobry, tokeny_krainy="1"), dict(dobry, kraina="")]
    for lup in [dobry] + zle:
        w, powod = LS.czysty_lup(D, lup)
        P["lup"].append({"lup": lup, "wynik": nil(w), "powod": powod})
    P["przyrost"] = []
    for info in ({"statystyka": "sila", "atrybut": "Strength", "przyrost": 2}, {"atrybut": "Armor", "przyrost": 1},
                 {"statystyka": "zrecznosc", "przyrost": 3}, {"atrybut": "Mana", "przyrost": 1},
                 {"atrybut": "Luck", "przyrost": 0}, {"atrybut": "Luck", "przyrost": 1.5}, {"atrybut": "Luck", "przyrost": 101}):
        w, powod = LS.czysty_przyrost(D, info)
        P["przyrost"].append({"info": info, "wynik": nil(list(w) if w else None), "powod": powod})
    P["poziom_z"] = [{"v": v, "wynik": LS.poziom_z(D, v)} for v in (1, 0, -3, 2.7, 5, 999, 1000, 1e9)]
    P["statystyka_z"] = [{"v": v, "wynik": nil(LS.statystyka_z(D, v))} for v in (0, -2, 7.9, 57, 9999, 12000)]
    P["rozklad"] = []
    for stats in ([26, 30, 12, 8, 10, 14], [27, 27, 10, 14, 13, 9], [24, 22, 24, 10, 10, 10], [26, 30, 12, 8, 10],
                  [26, 30, 12, 8, 10, 15], [26, 30, 12, 8, -10, 34]):
        w, powod = LS.rozklad_z_class_data(D, stats)
        P["rozklad"].append({"stats": stats, "wynik": nil(w), "powod": powod})
    # wydatki i pety (17.11.2026, swiat/pety_proba)
    P["wydatek"] = []
    dobry_w = {"ile": 300, "zrodlo": D["wydatki"]["zrodla"][0], "cel": "jajko_lesne"}
    for info in (dobry_w, dict(dobry_w, zrodlo="KowalProba", cel="ulepszenie"), dict(dobry_w, zrodlo="KowalProba",
                                                                                      cel="zakup_przedmiotu"), dict(dobry_w, ile=0), dict(dobry_w, ile=-5), dict(dobry_w, ile=2.5),
                 dict(dobry_w, ile=D["wydatki"]["kwota_maks"] + 1), dict(dobry_w, ile="300"), dict(dobry_w, zrodlo="Haker"),
                 dict(dobry_w, cel=""), dict(dobry_w, cel="jajko lesne"), dict(dobry_w, cel="x" * 25)):
        w, powod = LS.czysty_wydatek(D, info)
        P["wydatek"].append({"info": info, "wynik": nil(w), "powod": powod})
    P["przychod"] = []
    dobry_p = {"ile": 3, "zrodlo": D["przychody"]["zrodla"][0], "cel": "zagroda"}
    for info in (dobry_p, dict(dobry_p, ile=1), dict(dobry_p, ile=0), dict(dobry_p, ile=-2), dict(dobry_p, ile=1.5),
                 dict(dobry_p, ile=D["przychody"]["kwota_maks"]), dict(dobry_p, ile=D["przychody"]["kwota_maks"] + 1),
                 dict(dobry_p, ile="3"), dict(dobry_p, zrodlo="KowalProba"), dict(dobry_p, zrodlo=None),
                 dict(dobry_p, cel="zagroda petow"), dict(dobry_p, cel=None), "x"):
        w, powod = LS.czysty_przychod(D, info)
        P["przychod"].append({"info": info, "wynik": nil(w), "powod": powod})
    P["wydaj"] = [{"zloto": z, "ile": i, "wynik": list(LS.wydaj(D, z, i))}
                  for z, i in ((500, 300), (300, 300), (299, 300), (0, 300), (-40, 10), (12.7, 12), (None, 5), ("9", 5))]
    P["premia"] = []
    for pr in ({"zloto": 0.05, "doswiadczenie": 0}, {"zloto": 0.2, "doswiadczenie": 0.2}, {"doswiadczenie": 0.08}, None,
               {"zloto": -0.1}, {"zloto": D["pety"]["premia_maks"] + 0.01}, {"zloto": "0.1"}, "x"):
        w, powod = LS.czysta_premia(D, pr)
        P["premia"].append({"premia": nil(pr), "wynik": nil(w), "powod": powod})
    P["premia_lupu"] = []
    for lz, lx, pz, px in ((21, 12, 0.05, 0), (9, 30, 0.05, 0.08), (10, 10, 0.05, 0.05), (0, 3, 0.2, 0.2),
                           (180, 95, 0.2, 0.2), (7, 4, 0, 0)):
        lup = dict(dobry, zloto=lz, doswiadczenie=lx)
        P["premia_lupu"].append({"lup": lup, "premia": {"zloto": pz, "doswiadczenie": px},
                                 "wynik": LS.premia_lupu(D, lup, {"zloto": pz, "doswiadczenie": px})})
    # kara za przegraną (17.11.2026, propozycja D-098): zero Złota, mało, dużo (limit), wyłącznik, złe dane
    P["kara"] = []
    for z, poziom, procent in ((0, 1, 0.05), (19, 1, 0.05), (20, 1, 0.05), (300, 3, 0.05), (299, 9, 0.1),
                               (100000, 1, 0.05), (100000, 11, 0.05), (2000, 8, 0.05), (500, 1, 0), (500, 1, None),
                               (500, 1, -0.1), (500, 1, 1.5), (None, 4, 0.05), (-30, 4, 0.05), (12.9, 2, 0.5),
                               (500, 0, 0.05), (500, 2.7, 0.05), (10 ** 6, 999, 0.05), (777, 5, "0.05")):
        P["kara"].append({"zloto": nil(z), "poziom": poziom, "procent": nil(procent),
                          "wynik": LS.kara_przegranej(D, z, poziom, procent)})
    # modyfikatory bohatera i dane pakietów (18.11.2026)
    P["mod"] = []
    for mod in ({"statystyki": {"Strength": 5, "Luck": -2}, "procent": {"Strength": 0.1}, "lup": {"zloto": 0.05},
                 "bron": 3, "pancerz": 2.5, "tarcza": 0.05, "pasywki": ["furia", "luk_wiatru", "furia"]},
                {}, {"lup": {"zloto": 0.6}}, {"statystyki": {"Mana": 1}}, {"statystyki": {"Strength": 1.5}},
                {"procent": {"Luck": -0.1}}, {"bron": 5000}, {"pasywki": ["wskrzeszenie"]}, {"pasywki": ["nie_ma"]},
                {"pasywki": ["a", "b", "c", "d", "e", "f", "g"]}, {"cos": 1}, {"statystyki": {"Armor": 0}},
                {"zaklecie": "podpalenie"}, {"zaklecie": "lod"}, {"zaklecie": 5}):
        w, powod = LS.czysty_modyfikator(D, mod)
        P["mod"].append({"mod": mod, "wynik": nil(w), "powod": powod})
    m1 = LS.czysty_modyfikator(D, {"statystyki": {"Strength": 5}, "procent": {"Strength": 0.1, "Armor": 0.9},
                                   "lup": {"zloto": 0.3}, "bron": 4, "pasywki": ["furia", "seria"]})[0]
    m2 = LS.czysty_modyfikator(D, {"statystyki": {"Strength": 3, "Luck": 2}, "procent": {"Armor": 0.9},
                                   "lup": {"zloto": 0.5, "doswiadczenie": 0.1}, "pancerz": 6, "tarcza": 0.3,
                                   "pasywki": ["seria", "mur_tarczy", "kolos"]})[0]
    m3 = LS.czysty_modyfikator(D, {"procent": {"Armor": 1}, "tarcza": 0.4, "bron": -1000, "zaklecie": "trucizna"})[0]
    m4 = LS.czysty_modyfikator(D, {"zaklecie": "podpalenie", "lup": {"doswiadczenie": 0.05}})[0]
    P["zloz"], P["opis_mod"] = [], []
    for lista in ([], [m1], [m1, m2], [m2, m1, m3], [m4, m3], [m3, m4]):
        zl = LS.zloz_modyfikatory(D, lista)
        P["zloz"].append({"mody": lista, "wynik": zl})
        for k, L in (("wojownik", 1), ("zwiadowca", 5), ("mag", 10)):
            st = LS.rozdziel(D, D["rozklady"][k], LS.pula(D, L))
            opis = LS.opis_bohatera(D, k, L, st)
            P["opis_mod"].append({"opis": opis, "z": zl, "wynik": LS.opis_z_modyfikatorami(D, opis, zl)})
    P["dane_pakietu"] = []
    for v in ({"poziom": 3, "przedmioty": [{"id": "miecz", "plus": 2}, {"id": "tarcza", "plus": 0}], "ok": True},
              [1, 2, "trzy"], {}, "napis", 5, {"x": "y" * 201}, {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": 1}}}}}}}},
              {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": {"i": 1}}}}}}}}}, {"tak": True, "n": -3.5}):
        w, powod = LS.czyste_dane_pakietu(D, v)
        P["dane_pakietu"].append({"v": v, "wynik": nil(w), "powod": powod})
    # zapis postępu (18.11.2026): migracja, sprawdzanie profilu, kopia do zapisu
    stary1 = {"klasa": "mag", "poziom": 7, "xp": 12, "zloto": 340, "gemy": 5, "tokeny": {"las": 3}, "shardy": 0,
              "wytrenowane": {s: (2 if s == "sila" else 0) for s in D["statystyki"]}, "walki": {"wygrane": 9, "przegrane": 2},
              "awanse": 6, "baza": {"klasa": "mag"}}
    stary2 = dict(stary1, wersja=2, pety={"kopie": {"zoledziak": 1}, "aktywny": "zoledziak",
                                          "premia": {"zloto": 0.05, "doswiadczenie": 0}}, wydatki={"jajko_lesne": 1})
    stary3 = dict(stary2, wersja=3, pakiety={"kowal": {"plus": 2}})
    P["migruj"] = []
    for dane_ in (None, "x", 7, stary1, stary2, stary3, dict(stary3, wersja=99), dict(stary3, wersja="3"),
                  dict(stary3, wersja=4, punkty={"pula": 3, "rozdane": {s: 1 for s in D["statystyki"]}, "poziom": 7},
                       straznicy={"straznik_lasu": True}, idKlasy="Mage", atrybuty={"PokonalStraznikaLasu": True})):
        w, powod = LS.migruj_profil(D, dane_)
        P["migruj"].append({"dane": nil(dane_), "wynik": nil(w), "powod": powod})
    dobry = LS.migruj_profil(D, stary3)[0]
    P["czysty_profil"] = []
    for prof in (dobry, dict(dobry, poziom=0), dict(dobry, poziom=2.5), dict(dobry, zloto=-1), dict(dobry, klasa="lucznik"),
                 dict(dobry, idKlasy="Rogue"), dict(dobry, xp="5"), dict(dobry, tokeny={"las": 1.5}),
                 dict(dobry, atrybuty={"Haker": True}), dict(dobry, atrybuty={"StrojProba_mag": "a,b"}),
                 dict(dobry, straznicy={"straznik_lasu": 1}), dict(dobry, wersja=3),
                 dict(dobry, punkty={"pula": -1, "rozdane": {}, "poziom": 1}), dict(dobry, wytrenowane={"sila": 1}),
                 dict(dobry, pety={"kopie": {"a": 1}, "premia": {"zloto": 0.9}}), dict(dobry, pakiety={"k": {"x": "y" * 201}})):
        w, powod = LS.czysty_profil(D, prof)
        P["czysty_profil"].append({"p": prof, "wynik": nil(w), "powod": powod})
    P["do_zapisu"] = [{"p": prof, "wynik": LS.profil_do_zapisu(D, prof)}
                      for prof in (dict(dobry, oczekujace=[1], baza={"klasa": "mag"}), LS.nowy_profil(D))]
    # Gemy za strażnika (18.11.2026, D-099)
    P["straznik"] = [{"gatunek": nil(g), "wynik": LS.czy_straznik(D, g)}
                     for g in ("straznik_lasu", "straznik_topieli", "lesny_slime", "straznik", "", None, 7, "xstraznik_lasu")]
    # punkty statystyk do rozdania (18.11.2026)
    P["pula_sama"] = [{"poziom": L, "wl": wl, "wynik": LS.pula_sama(D, L, wl)} for L in (1, 2, 5, 11, 999) for wl in (True, False)]
    P["zmiana"] = []
    for znana, nowa, pula in ((20, 21, 5), (20, 21, 0), (20, 25, 5), (20, 26, 5), (20, 19, 5), (20, 20, 0), (20, None, 3),
                              (None, 3, 5), (20, 22.7, 5), (20, 21, -1), (20, 21, None), (9999, 10000, 5)):
        P["zmiana"].append({"znana": nil(znana), "nowa": nil(nowa), "pula": nil(pula),
                            "wynik": list(LS.zmiana_statystyki(D, znana, nowa, pula))})
    return P


def dane_z_przypadkami():
    D = podstawa()
    D["przypadki"] = przypadki(D)
    bez = {k: v for k, v in D.items() if k != "skrot"}
    D["skrot"] = hashlib.sha1(json.dumps(bez, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]
    return None, D


# ------------------------------------------------------------------------------------------------ zapis Luau
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SLOWA = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in", "local", "nil", "not",
          "or", "repeat", "return", "then", "true", "until", "while", "continue", "export", "type"}


def _napis(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def _liczba(x):
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, int):
        return str(x)
    r = repr(float(x))
    return r[:-2] if r.endswith(".0") else r


def _klucz(k):
    if isinstance(k, int):
        return "[%d]" % k
    return k if (_IDENT.match(k) and k not in _SLOWA) else "[%s]" % _napis(k)


def _luau(v, wciecie=1):
    if v is None:
        return "nil"
    if isinstance(v, (bool, int, float)):
        return _liczba(v)
    if isinstance(v, str):
        return _napis(v)
    tab = "\t" * wciecie
    if isinstance(v, (list, tuple)):
        czesci = [_luau(x, wciecie + 1) for x in v]
    elif isinstance(v, dict):
        czesci = ["%s = %s" % (_klucz(k), _luau(x, wciecie + 1)) for k, x in v.items() if x is not None]
    else:
        raise TypeError(repr(v))
    jedna = "{ " + ", ".join(czesci) + " }" if czesci else "{}"
    if len(jedna) <= 110 and "\n" not in jedna:
        return jedna
    return "{\n" + "".join(tab + c + ",\n" for c in czesci) + "\t" * (wciecie - 1) + "}"


def luau_tekst(D):
    naglowek = ("--[[\n\tDaneStanu — WYGENEROWANE przez swiat/stan_gracza/dane.py z tools/walka/wzorcowe.py, tools/walka/tempo.py\n"
                "\ti src/server/Walka/Statystyki.luau. NIE EDYTUJ RĘCZNIE: zmień źródło i uruchom\n"
                "\tpython -B swiat/stan_gracza/dane.py (testy i zbuduj.py --sucho pilnują aktualności).\n"
                "\tLiczby to propozycja (krzywa doświadczenia, pula, sloty) — lista „przyjęte, do zmiany” w README pakietu.\n]]\n")
    return (naglowek + 'if not game:GetService("RunService"):IsStudio() then\n\treturn {}\nend\n\nreturn '
            + _luau(D) + "\n")


def zapisz(folder):
    _, D = dane_z_przypadkami()
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, PLIK_LUAU), "w", encoding="utf-8", newline="\n") as f:
        f.write(luau_tekst(D))
    return D


def aktualny():
    _, D = dane_z_przypadkami()
    sciezka = os.path.join(ZRODLA, PLIK_LUAU)
    if not os.path.isfile(sciezka):
        return False, D
    with open(sciezka, encoding="utf-8") as f:
        return f.read() == luau_tekst(D), D


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    try:
        if "--sprawdz" in argv:
            ok, D = aktualny()
            print("DaneStanu.luau: %s (skrót %s, przypadków: %d)" % ("aktualny" if ok else "NIEAKTUALNY", D["skrot"],
                                                                     sum(len(v) for v in D["przypadki"].values())))
            return 0 if ok else 1
        D = zapisz(ZRODLA)
        print("zapisano swiat/stan_gracza/zrodla/%s (skrót %s)" % (PLIK_LUAU, D["skrot"]))
        return 0
    except BladDanych as e:
        print("BŁĄD DANYCH: %s" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
