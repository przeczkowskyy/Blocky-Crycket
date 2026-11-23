#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Przejście gry w liczbach (D-106): gracz od 1. poziomu przez las, Bagno i Dżunglę do wygranej ze Strażnikiem Dżungli.

    python -B swiat/przejscie_gry/symulacja_przejscia.py                     # całość: JSON + tabele w raporcie (kilka minut)
    python -B swiat/przejscie_gry/symulacja_przejscia.py --przebiegow 10 --bez-propozycji --bez-zapisu   # szybka próba
    python -B swiat/przejscie_gry/symulacja_przejscia.py --jeden mag wszystko po_zmianie 7   # jeden gracz na ekran (JSON)

PROPOZYCJA LICZB, NIE KANON. Bez Roblox Studio. Wynik każdej walki liczy port silnika (tools/walka/silnik.py), a WSZYSTKIE
liczby gry są czytane z plików gry przy każdym uruchomieniu — po zmianach danych wystarczy puścić symulację jeszcze raz:
  • potwory, łup, stałe walki            — tools/walka/dane_walki.json + swiat/{bagno,dzungla}_pas_gra/przeciwnicy.py
  • zagrody, poziomy, odradzanie, bramy  — swiat/{las,bagno,dzungla}_pas_gra/zrodla/Dane*.luau (interpreter luau_mini)
  • doświadczenie, punkty, kara, start   — swiat/stan_gracza/dane.py + logika_stanu.py
  • mini-gry (przyrost, pasek)           — swiat/trening_proba/dane.py + logika_treningu.py
  • kowal (przedmioty, ulepszanie, łup)  — swiat/kowal_proba/dane.py + logika_kowala.py
  • jajka i pety                         — swiat/pety_proba/dane_petow.py + logika_petow.py
  • sklep w trzech stopniach             — plik z listy KATALOG_SKLEPU, gdy powstanie (opis formatu: wczytaj_katalog)
W tym pliku są tylko ZAŁOŻENIA o graczu i o czasie (CZAS, STYLE, TRYBY) oraz dwa warianty świata (WARIANTY).
"""
import argparse
import copy
import importlib.util
import json
import math
import os
import random
import re
import statistics
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
SWIAT = os.path.join(REPO, "swiat")
WALKA = os.path.join(REPO, "tools", "walka")
STAN = os.path.join(SWIAT, "stan_gracza")
for _s in (os.path.join(SWIAT, "las_potwory"), os.path.join(SWIAT, "pety_proba"), os.path.join(SWIAT, "kowal_proba"),
           os.path.join(SWIAT, "trening_proba"), STAN, WALKA):
    if _s not in sys.path:
        sys.path.insert(0, _s)


def _modul(nazwa, sciezka):
    """Moduł spod własnej nazwy (w repo jest kilka plików dane.py i przeciwnicy.py)."""
    if nazwa in sys.modules:
        return sys.modules[nazwa]
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nazwa] = m
    spec.loader.exec_module(m)
    return m


import silnik  # noqa: E402
import luau_mini as LM  # noqa: E402
import logika_stanu as LS  # noqa: E402
import logika_treningu as LT  # noqa: E402
import logika_kowala as LK  # noqa: E402
import logika_petow as LP  # noqa: E402
import logika as LPOT  # noqa: E402  (swiat/las_potwory/logika.py: ile potworów, czas odrodzenia)

# ====================================================================================================================
# PARAMETRY — JEDNO MIEJSCE. Tu nie ma liczb gry, tylko założenia o graczu, o czasie i o świecie „po zmianie”.
# ====================================================================================================================
# Dwa warianty świata (D-107). „po_zmianie” = dokładnie to, co jest w plikach gry (19.11 inny agent wpisał do nich
# liczby D-107: więcej potworów, szybkie odradzanie, brak czekania po walce). „przed_zmiana” = stan z 18.11, zapisany
# tutaj, bo w plikach gry już go nie ma. None = wartość z plików gry.
WARIANTY = {
    "przed_zmiana": {
        "nazwa": "przed zmianą (stan z 18.11)",
        "tempo_blokady": 1,              # serwer trzymał gracza do końca pełnego czasu walki ×1 (także po przegranej)
        "zagroda": {"naraz": 3, "max": 4, "odrodzenie_s": 15},   # zwykła zagroda: 2 potwory dla jednego gracza, 12–18 s
        "rzadki_odrodzenie_s": 150,      # Leśny Troll, Ropucha z Chatką, Pancernik Ruin
        "straznik_odrodzenie_s": 120,
    },
    "po_zmianie": {
        "nazwa": "po zmianie D-107 (pliki gry)",
        "tempo_blokady": None,           # z plików gry: S.TEMPO_POKAZU_MAKS w swiat/las_potwory/zrodla/Stale.luau
        "zagroda": None,
        "rzadki_odrodzenie_s": None,
        "straznik_odrodzenie_s": None,
    },
}

CZAS = {
    "predkosc": 16.0,            # studów/s — domyślny bieg postaci Roblox
    "ekran_wyniku_s": 3.0,       # karta wyniku i powrót do świata
    "dojscie_s": {"zwykly": 9.0, "rzadki": 15.0, "straznik": 6.0},   # podejście do potwora i E (jak tools/walka/tempo.py)
    "pominiecie_s": 1.5,         # walka pominięta (znany gatunek): klik POMIŃ i karta
    "wizyta_miasto_s": 40.0,     # Kamień Powrotu → bazar → z powrotem (jak swiat/kowal_proba/balans_kowala.py)
    "wizyta_co_s": 300.0,        # do kowala najwyżej raz na 5 minut
    "jajko_s": 25.0,             # kupno i wyklucie jajka przy wejściu do krainy (bez dojścia)
    "przerwa_rundy_s": 6.0,      # podsumowanie rundy mini-gry i start następnej
    "okres_treningu_min": 30.0,  # co ile minut gracz robi przerwę na mini-gry
    "run_na_runde": 26,          # mini-gra Runy: ile run gracz zdąży w rundzie (swiat/trening_proba/PROJEKT.md)
    "graczy_na_serwerze": 1,     # od tego zależy liczba potworów i tempo odradzania (dane gry)
    "limit_min": 720.0,          # dłużej nie liczymy: gracz „nie skończył”
    "utknal_od_prob": 5,         # tyle przegranych prób z jednym Strażnikiem = „utknął”
}

# Styl gry. tempo_* = tempo oglądania (1, 2, 4); pomija_znane = jak często pomija walkę ze znanym gatunkiem;
# margines_poziomu = bije potwory do poziomu własnego + tyle; zapas_wejscia = idzie do następnej zagrody na poziomie
# jej najsłabszego potwora + tyle; zapas_straznika = pierwsza próba ze Strażnikiem na jego poziomie + tyle;
# celnosc = udział trafień w mini-grze (77% zmierzone w przejściu gry 17.11.2026)
STYLE = {
    "cale": {"tempo_nowe": 1, "tempo_znane": 1, "pomija_znane": 0.0, "tempo_straznika": 1, "pomija_straznika": False,
             "margines_poziomu": 1, "zapas_wejscia": 0, "zapas_straznika": 0, "przegrane_do_cofniecia": 2,
             "farma_po_strazniku": 3, "poziomy_po_strazniku": 0, "celnosc": 0.77, "jajek_na_biom": 3},
    "zwykly": {"tempo_nowe": 1, "tempo_znane": 2, "pomija_znane": 0.5, "tempo_straznika": 1, "pomija_straznika": False,
               "margines_poziomu": 1, "zapas_wejscia": 0, "zapas_straznika": 0, "przegrane_do_cofniecia": 2,
               "farma_po_strazniku": 3, "poziomy_po_strazniku": 0, "celnosc": 0.77, "jajek_na_biom": 3},
    "ostrozny": {"tempo_nowe": 1, "tempo_znane": 2, "pomija_znane": 0.2, "tempo_straznika": 1, "pomija_straznika": False,
                 "margines_poziomu": 0, "zapas_wejscia": 1, "zapas_straznika": 1, "przegrane_do_cofniecia": 1,
                 "farma_po_strazniku": 3, "poziomy_po_strazniku": 1, "celnosc": 0.85, "jajek_na_biom": 5},
    "niecierpliwy": {"tempo_nowe": 4, "tempo_znane": 4, "pomija_znane": 1.0, "tempo_straznika": 4, "pomija_straznika": True,
                     "margines_poziomu": 2, "zapas_wejscia": -1, "zapas_straznika": -1, "przegrane_do_cofniecia": 3,
                     "farma_po_strazniku": 1, "poziomy_po_strazniku": 0, "celnosc": 0.65, "jajek_na_biom": 1},
}

# Sposoby gry (kolejność = kolejność w raporcie)
TRYBY = {
    "walki_cale": {"nazwa": "Tylko walki, każda oglądana w całości", "styl": "cale", "trening_min_na_h": 0,
                   "pety": False, "kowal": False, "sklep": False},
    "walki": {"nazwa": "Tylko walki", "styl": "zwykly", "trening_min_na_h": 0, "pety": False, "kowal": False,
              "sklep": False},
    "walki_minigry": {"nazwa": "Walki + mini-gry (10 min na godzinę)", "styl": "zwykly", "trening_min_na_h": 10,
                      "pety": False, "kowal": False, "sklep": False},
    "wszystko": {"nazwa": "Walki + mini-gry + pety + kowal", "styl": "zwykly", "trening_min_na_h": 10, "pety": True,
                 "kowal": True, "sklep": False},
    # sklep liczy się tylko wtedy, gdy istnieje plik katalogu (KATALOG_SKLEPU); bez pliku = to samo co „wszystko”
    "ze_sklepem": {"nazwa": "Wszystko + sklep z przedmiotami", "styl": "zwykly", "trening_min_na_h": 10, "pety": True,
                   "kowal": True, "sklep": True},
    "ostrozny": {"nazwa": "Ostrożny (bez sklepu, z zapasem poziomu)", "styl": "ostrozny", "trening_min_na_h": 15,
                 "pety": True, "kowal": True, "sklep": False},
    "niecierpliwy": {"nazwa": "Niecierpliwy (pomija walki, pcha do przodu)", "styl": "niecierpliwy",
                     "trening_min_na_h": 0, "pety": False, "kowal": False, "sklep": False},
}

# Katalog przedmiotów do kupienia w trzech stopniach — jeszcze go nie ma. Pierwszy istniejący plik z listy jest
# wczytywany (ścieżki względem korzenia repo); brak pliku = gracz niczego nie kupuje w sklepie.
KATALOG_SKLEPU = [
    "swiat/postacie/sklep_liczby.json",          # powstaje 19.11 (swiat/postacie/sklep_ceny.py)
    "swiat/przejscie_gry/katalog_sklepu.json",   # własny plik próbny, gdyby był potrzebny
]

BIOMY = [  # kolejność krain i ich pliki (dane gry)
    {"id": "las", "pakiet": "las_pas_gra", "potwory": "DanePotworowPasa.luau", "pas": "DanePasa.luau", "przeciwnicy": None},
    {"id": "bagno", "pakiet": "bagno_pas_gra", "potwory": "DanePotworowBagna.luau", "pas": "DaneBagna.luau",
     "przeciwnicy": "przeciwnicy.py"},
    {"id": "dzungla", "pakiet": "dzungla_pas_gra", "potwory": "DanePotworowDzungli.luau", "pas": "DaneDzungli.luau",
     "przeciwnicy": "przeciwnicy.py"},
]

# Propozycje zmian liczb, liczone na KOPII danych (pliki gry zostają nietknięte). Opis pól: zastosuj_zmiany.
# Życie Strażnika Topieli i Węża Stu Lian −15% jest już w plikach gry (D-111, 19.11) — propozycje −15% / −30% i „razem”
# z tym życiem zniknęły z listy; „xp_dzungli” liczy się teraz na Strażnikach po D-111.
PROPOZYCJE = {
    "bez_zmian": {"nazwa": "Bez zmian (liczby z plików gry)", "zmiany": {}},
    "xp_dzungli": {"nazwa": "Doświadczenie z potworów Dżungli +25%",
                   "zmiany": {"lup": {"dzungla": {"doswiadczenie": 1.25}}}},
    "krzywa_b": {"nazwa": "Krzywa doświadczenia: wykładnik 1,5 zamiast 1,6", "zmiany": {"krzywa_b": 1.5}},
    "dluzsza": {"nazwa": "Dla porównania: krzywa doświadczenia +25% (dłuższa gra)", "zmiany": {"krzywa_a": 1.25}},
}
PROPOZYCJE_TRYBY = ["walki", "wszystko", "niecierpliwy"]
PROPOZYCJE_WARIANT = "po_zmianie"
STOPNIE_SKLEPU = {"start": 0, "las": 1, "bagno": 2, "dzungla": 3}   # nazwy stopni z sklep_ceny.py → numer


# ====================================================================================================================
# WCZYTANIE DANYCH GRY
# ====================================================================================================================
def wczytaj_luau(sciezka):
    """Moduł danych Luau → słowniki Pythona (interpreter tools/walka/luau_mini.py, jak swiat/stan_gracza/symulacja_lasu.py)."""
    it = LM.Interpreter()
    rs = LM.Tabela()
    rs.set("IsStudio", lambda _s: True)
    game = LM.Tabela()
    game.set("GetService", lambda _s, _n: rs)
    it.globalne.z["game"] = game
    with open(sciezka, encoding="utf-8") as f:
        return LM.z_luau(it.wykonaj(f.read(), os.path.basename(sciezka))[0])


def _mod_z_bazy(baza):
    """Statystyki przedmiotu {bron, pancerz, tarcza, Strength…} → wpis jak w StanGracza/Sygnaly/Modyfikatory."""
    m, st = {}, {}
    for k, v in baza.items():
        if v == 0:
            continue
        if k in ("bron", "pancerz"):
            m[k] = int(v)
        elif k == "tarcza":
            m[k] = round(v, 4)
        else:
            st[k] = int(v)
    if st:
        m["statystyki"] = st
    return m


def wczytaj_katalog(sciezki=None):
    """Katalog sklepu (przedmioty do kupienia w stopniach) albo None, gdy pliku jeszcze nie ma. Dwa formaty:
      a) słownik sklep_ceny.py: {"przedmioty": {"rycerz_las_helm": {"klasa": "wojownik", "stopien": "las",
         "slot": "Helmet", "cena": 400, "poziom": 5, "baza": {"pancerz": 4, "Constitution": 2}}}} — stopień „start”
         jest pomijany: te rzeczy gracz ma od kowala;
      b) lista: {"przedmioty": [{"id": "helm_1", "klasa": "wojownik" albo "*", "slot": "Helmet", "stopien": 1,
         "cena": 400, "poziom": 1, "mod": {"statystyki": {"Constitution": 3}, "pancerz": 4}}]}.
    Każdy „mod” przechodzi w symulacji przez prawdziwe sprawdzenie logika_stanu.czysty_modyfikator. Kupiony przedmiot
    zajmuje swój slot (zastępuje przedmiot kowala z tego slotu). Jedno miejsce do zmiany, gdy format się zmieni."""
    for s in (sciezki if sciezki is not None else KATALOG_SKLEPU):
        p = s if os.path.isabs(s) else os.path.join(REPO, s)
        if not os.path.isfile(p):
            continue
        with open(p, encoding="utf-8") as f:
            K = json.load(f)
        surowe = K.get("przedmioty") if isinstance(K, dict) else None
        if isinstance(surowe, dict):
            surowe = [dict(v, id=k) for k, v in surowe.items()]
        if not isinstance(surowe, list):
            raise ValueError("katalog sklepu: brak pola „przedmioty”")
        lista = []
        for it in surowe:
            for pole in ("id", "slot", "stopien", "cena"):
                if pole not in it:
                    raise ValueError("katalog sklepu: przedmiot bez pola %s" % pole)
            st = STOPNIE_SKLEPU.get(it["stopien"], it["stopien"]) if isinstance(it["stopien"], str) else it["stopien"]
            if not isinstance(st, int) or isinstance(st, bool):
                raise ValueError("katalog sklepu: nieznany stopień %r" % (it["stopien"],))
            if st < 1:
                continue
            mod = it["mod"] if "mod" in it else _mod_z_bazy(it.get("baza") or {})
            lista.append({"id": it["id"], "klasa": it.get("klasa", "*"), "slot": it["slot"], "stopien": st,
                          "cena": it["cena"], "poziom": it.get("poziom", 1), "mod": mod})
        return {"plik": s if not os.path.isabs(s) else os.path.basename(s), "przedmioty": lista}
    return None


def _stala_luau(sciezka, nazwa, domyslna):
    try:
        with open(sciezka, encoding="utf-8") as f:
            m = re.search(r"\b%s\s*=\s*([0-9.]+)" % re.escape(nazwa), f.read())
        return float(m.group(1)) if m else domyslna
    except OSError:
        return domyslna


_BAZA = {}


def baza():
    """Dane gry wczytane raz na proces (tylko odczyt — eksperymenty dostają kopię z gra())."""
    if _BAZA:
        return _BAZA
    DS = _modul("dane_stanu_przejscie", os.path.join(STAN, "dane.py"))
    Ds = DS.dane_z_przypadkami()[1]
    biomy = []
    for b in BIOMY:
        pak = os.path.join(SWIAT, b["pakiet"])
        if b["przeciwnicy"]:
            _modul("przeciwnicy_" + b["id"], os.path.join(pak, b["przeciwnicy"])).zaladuj_do_silnika(silnik)
        dp = wczytaj_luau(os.path.join(pak, "zrodla", b["potwory"]))
        dpa = wczytaj_luau(os.path.join(pak, "zrodla", b["pas"]))
        strefy = []
        for s in dp["strefy"]:
            strefy.append({"id": s["id"], "gatunek": s["gatunek"], "od": s["poziomy"][0], "do": s["poziomy"][1],
                           "x": s["srodek"][0], "straznik": s["straznik"] is True, "odrodzenie": s["odrodzenieS"],
                           "stale": s.get("odrodzenieStale") is True, "naraz": s["naraz"], "max": s["max"],
                           "po_miejscach": s.get("poziomyPoMiejscach") is True})
        if not strefy or not strefy[-1]["straznik"]:
            raise ValueError("%s: ostatnia zagroda nie jest areną Strażnika" % b["id"])
        biomy.append({"id": b["id"], "nazwa": dpa["biom"]["nazwa"], "strefy": strefy,
                      "x_przybycia": dpa["przybycie"]["punkt"][0], "przelot_s": dpa["przelot"]["czas"],
                      "brama_x": dpa["brama"]["x"]})
    # mini-gry: prosto z ustawień pakietu (jedyne źródło jego liczb); logika_treningu czyta z nich gry, rundę i przyrost
    with open(os.path.join(SWIAT, "trening_proba", "ustawienia.json"), encoding="utf-8") as f:
        Dt = json.load(f)
    Dk = _modul("dane_kowala_przejscie", os.path.join(SWIAT, "kowal_proba", "dane.py")).dane_z_przypadkami()[0]
    Dp = _modul("dane_petow_przejscie", os.path.join(SWIAT, "pety_proba", "dane_petow.py")).dane_z_przypadkami()
    if not isinstance(Dp, dict):
        Dp = next(x for x in Dp if isinstance(x, dict))
    _BAZA.update({
        "Ds": Ds, "biomy": biomy, "Dt": Dt, "Dk": Dk, "Dp": Dp, "katalog": wczytaj_katalog(),
        "przeciwnicy": copy.deepcopy(silnik.PRZECIWNICY),
        "final_s": silnik.STALE["czas_finalu"] / 100.0,
        "zapas_sesji_s": _stala_luau(os.path.join(SWIAT, "las_potwory", "zrodla", "Stale.luau"), "S.ZAPAS_SESJI", 0.4),
        # blokada po walce: czas walki ÷ ta liczba (1 = pełny czas ×1, jak przed D-107; brak stałej w pliku = 1)
        "tempo_blokady": _stala_luau(os.path.join(SWIAT, "las_potwory", "zrodla", "Stale.luau"), "S.TEMPO_POKAZU_MAKS", 1.0),
    })
    return _BAZA


def zastosuj_zmiany(G, zmiany):
    """Zmiany liczb na kopii danych (propozycje „przed / po”). Pola (wszystkie opcjonalne):
        "krzywa_a": 0.85            — mnożnik stałej A krzywej doświadczenia (mniej = szybsze poziomy)
        "krzywa_b": 1.5             — nowy wykładnik krzywej
        "poziomy": {"dzungla/straznik": -1, "bagno/t1": [15, 15]} — przesunięcie albo nowe poziomy zagrody
        "potwor": {"waz_stu_lian": {"zycie": -0.10, "bron": 0.9}}   — życie: dodatek do modyfikatora, broń: mnożnik
        "lup": {"dzungla": {"doswiadczenie": 1.2, "zloto": 1.0}}     — mnożnik łupu potworów krainy (albo id potwora)
        "cena_jajka": {"jajko_dzungli": 900}                          — nowa cena stała jajka
        "kara_procent": 0.0                                           — kara Złota za przegraną"""
    for k in zmiany:
        if k not in ("krzywa_a", "krzywa_b", "poziomy", "potwor", "lup", "cena_jajka", "kara_procent"):
            raise ValueError("nieznana zmiana: %s" % k)
    if "krzywa_a" in zmiany:
        G["Ds"]["krzywa"]["a"] = G["Ds"]["krzywa"]["a"] * zmiany["krzywa_a"]
    if "krzywa_b" in zmiany:
        G["Ds"]["krzywa"]["b"] = zmiany["krzywa_b"]
    if "kara_procent" in zmiany:
        G["Ds"]["kara"]["procent"] = zmiany["kara_procent"]
    for klucz, v in (zmiany.get("poziomy") or {}).items():
        bid, sid = klucz.split("/")
        s = next(s for b in G["biomy"] if b["id"] == bid for s in b["strefy"] if s["id"] == sid)
        if isinstance(v, list):
            s["od"], s["do"] = v
        else:
            s["od"], s["do"] = max(1, s["od"] + v), max(1, s["do"] + v)
    for pid, z in (zmiany.get("potwor") or {}).items():
        p = G["przeciwnicy"][pid]
        if "zycie" in z:
            p["modyfikatory"]["zycie"] = round(p["modyfikatory"].get("zycie", 0) + z["zycie"], 4)
        if "bron" in z:
            p["bron"] = [round(x * z["bron"], 4) for x in p["bron"]]
    for cel, z in (zmiany.get("lup") or {}).items():
        for p in G["przeciwnicy"].values():
            if p["id"] == cel or p["kraina"] == cel:
                for pole, mn in z.items():
                    p["lup"][pole] = [round(x * mn, 4) for x in p["lup"][pole]]
    for jid, cena in (zmiany.get("cena_jajka") or {}).items():
        next(j for j in G["Dp"]["jajka"] if j["id"] == jid)["cena"]["stala"] = cena
    return G


def gra(zmiany=None):
    """Kopia danych gry (ze zmianami albo bez) gotowa do symulacji. Ustawia też potwory w porcie silnika."""
    B = baza()
    G = {k: (copy.deepcopy(v) if k in ("Ds", "biomy", "Dp", "przeciwnicy") else v) for k, v in B.items()}
    if zmiany:
        zastosuj_zmiany(G, zmiany)
    silnik.PRZECIWNICY.clear()
    silnik.PRZECIWNICY.update(G["przeciwnicy"])
    for b in G["biomy"]:
        for s in b["strefy"]:
            s["ranga"] = G["przeciwnicy"][s["gatunek"]]["ranga"]
    return G


# ====================================================================================================================
# GRACZ
# ====================================================================================================================
def runda_minigry(G, stat, poziom, W, pasek, celnosc, los):
    """Jedna runda mini-gry statystyki `stat`: prawdziwy plan rundy i prawdziwy wzór paska (logika_treningu).
    → (nowe W = punkty wytrenowane, nowy pasek, trafienia, zdarzenia)."""
    Dt = G["Dt"]
    Gm = Dt["gry"][stat]
    n = len(LT.plan(Dt, stat, los.randrange(1, 2 ** 31 - 1)))
    if Gm["typ"] == "sekwencja":
        n = min(n, CZAS["run_na_runde"])
    pula = LT.pula(Dt, poziom)
    seria = traf = 0
    for _ in range(n):
        if los.random() < celnosc:
            seria += 1
            traf += 1
            pasek += LT.przyrost(Dt, seria, Gm)
            pr = LT.prog(Dt, W, pula)
            while pasek >= pr:
                pasek -= pr
                W += 1
                pr = LT.prog(Dt, W, pula)
        else:
            seria = 0
    return W, pasek, traf, n


def opis_bohatera(G, klasa, L, wytrenowane=None, mody=None):
    """Bohater dla silnika: rozkład klasy dla puli poziomu + punkty z mini-gier + modyfikatory (kowal, pet, sklep,
    szczęście początkującego) złożone prawdziwą logiką stanu gracza. → (opis, premia łupu)."""
    Ds = G["Ds"]
    st = LS.rozdziel(Ds, Ds["rozklady"][klasa], LS.pula(Ds, L))
    for s, v in (wytrenowane or {}).items():
        st[s] = min(st[s] + v, Ds["limity"]["statystyka_maks"])
    o = LS.opis_bohatera(Ds, klasa, L, st)
    z = LS.zloz_modyfikatory(Ds, mody or [])
    return LS.opis_z_modyfikatorami(Ds, o, z), z["lup"]


def _czysty(G, mod, skad):
    c, powod = LS.czysty_modyfikator(G["Ds"], mod)
    if c is None:
        raise ValueError("modyfikator %s odrzucony przez stan gracza: %s (%s)" % (skad, powod, mod))
    return c


def _miejsca(strefa, W, los):
    """Potwory zagrody dla jednego gracza: [{poziom, od}] (od = od kiedy potwór jest na miejscu) i czas odrodzenia.
    Liczba potworów i skracanie odrodzenia: prawdziwe wzory swiat/las_potwory/logika.py."""
    naraz, maks, odr, stale = strefa["naraz"], strefa["max"], strefa["odrodzenie"], strefa["stale"]
    if strefa["straznik"]:
        odr = W["straznik_odrodzenie_s"] if W["straznik_odrodzenie_s"] is not None else odr
        stale = True
    elif strefa["ranga"] == "rzadki":
        odr = W["rzadki_odrodzenie_s"] if W["rzadki_odrodzenie_s"] is not None else odr
        stale = True
    elif W["zagroda"] is not None:
        naraz, maks, odr, stale = W["zagroda"]["naraz"], W["zagroda"]["max"], W["zagroda"]["odrodzenie_s"], False
    n = max(1, LPOT.cel(naraz, maks, CZAS["graczy_na_serwerze"]))
    zakres = strefa["do"] - strefa["od"] + 1
    w = []
    for i in range(n):
        pz = strefa["od"] + (i % zakres) if strefa["po_miejscach"] else los.randint(strefa["od"], strefa["do"])
        w.append({"poziom": pz, "od": 0.0})
    if not stale:
        odr = LPOT.czas_odrodzenia(odr, CZAS["graczy_na_serwerze"])
    return {"lista": w, "odrodzenie": odr}


def _wybierz(miejsca, L, margines, czas):
    dost = [m for m in miejsca["lista"] if m["od"] <= czas]
    if not dost:
        return None
    dobre = [m for m in dost if m["poziom"] <= L + margines]
    return max(dobre, key=lambda m: m["poziom"]) if dobre else min(dost, key=lambda m: m["poziom"])


def przejscie(G, klasa, tryb, wariant, ziarno, limit_min=None, sledz=None):
    """Jeden gracz od 1. poziomu do wygranej ze Strażnikiem ostatniej krainy (albo do limitu czasu) → słownik wyników.
    sledz = lista, do której trafia zapis każdej walki (testy)."""
    T, W = TRYBY[tryb], WARIANTY[wariant]
    S = STYLE[T["styl"]]
    Ds, Dk, Dp = G["Ds"], G["Dk"], G["Dp"]
    los = random.Random("%s|%s|%s|%d" % (klasa, tryb, wariant, ziarno))
    limit_s = (limit_min if limit_min is not None else CZAS["limit_min"]) * 60.0
    v = CZAS["predkosc"]
    biomy = G["biomy"]
    M = [[_miejsca(s, W, los) for s in b["strefy"]] for b in biomy]
    tempo_blokady = max(1.0, W["tempo_blokady"] if W["tempo_blokady"] is not None else G["tempo_blokady"])

    L, xp, zloto = 1, 0, 0
    zarobione = wydane = stracone = 0
    walki = wygrane = przegrane = 0
    znane = set()
    wytren = {s: 0 for s in Ds["statystyki"]}
    pasek = {s: 0.0 for s in Ds["statystyki"]}
    glowne = sorted(Ds["statystyki"], key=lambda s: -Ds["rozklady"][klasa][s])[:3]
    kowal = LK.podstawowe(Dk, LK.nowe(Dk), klasa)[0] if T["kowal"] else None
    ulepszen = lupow = 0
    pety, aktywny, jajka = {}, None, {}
    ranga_peta = {p["id"]: i for i, p in enumerate(Dp["pety"])}
    rzadkosc_nr = {r["id"]: i for i, r in enumerate(Dp["rzadkosci"])}
    sklep = {}
    katalog = G["katalog"] if T["sklep"] else None
    pocz = Ds["poczatek"]["procent"]
    pamiec = {"klucz": None, "opis": None, "lup": None}
    wersja = [0]

    def bohater():
        klucz = (L, wersja[0], wygrane == 0)
        if pamiec["klucz"] != klucz:
            mody = []
            if kowal is not None:
                zal = [q for q in LK.zalozone(Dk, klasa, kowal, None) if Dk["przedmioty"][q].get("slot") not in sklep]
                mk = LK.mod(Dk, klasa, kowal, zal)
                if Dk["klasy"][klasa]["tarcza"] and "OffHand" in sklep and not any(
                        Dk["przedmioty"][q].get("slot") == "OffHand" for q in zal):
                    # tarcza kupiona w sklepie dalej jest tarczą: blok ze wzoru zostaje (LK.mod odjął go za „brak tarczy”)
                    mk["tarcza"] = round(mk.get("tarcza", 0) + Dk["blokTarczy"], 4)
                    if mk["tarcza"] == 0:
                        del mk["tarcza"]
                mody.append(_czysty(G, mk, "kowala"))
            if aktywny:
                mody.append(_czysty(G, LP.mod_peta(Dp, aktywny) or {}, "peta"))
            for it in sklep.values():
                mody.append(_czysty(G, it["mod"], "sklepu"))
            if wygrane == 0 and pocz > 0:   # szczęście początkującego: do pierwszej wygranej (SerwerStanu)
                mody.append({"procent": {a: pocz for a in Ds["atrybuty_statystyk"].values()}})
            pamiec["opis"], pamiec["lup"] = opis_bohatera(G, klasa, L, wytren, mody)
            pamiec["klucz"] = klucz
        return pamiec["opis"], pamiec["lup"]

    b = i = 0
    B = biomy[0]
    czas = B["przelot_s"] + abs(B["strefy"][0]["x"] - B["x_przybycia"]) / v
    x = B["strefy"][0]["x"]
    wolny_od = 0.0
    kamienie = {}
    strefy = {}
    straznicy = {bm["id"]: {"proby": 0, "przegrane": 0, "poziom_pierwszej": None} for bm in biomy}
    min_wejscia = {}
    farma = 0
    wymagany = 0
    z_rzedu = 0
    chce_wzmocnienia = False
    ost_trening = ost_wizyta = 0.0
    t_trening = t_miasto = t_blokada = t_odrodzenie = t_walk = 0.0
    ost_awans, bez_awansu, bez_awansu_gdzie = 0.0, 0.0, ""
    ost_nowosc, bez_nowosci, bez_nowosci_gdzie = 0.0, 0.0, ""
    seria_gat, seria_n, seria_max, seria_max_gat = None, 0, 0, ""
    walki_gat = {}
    okres_s = CZAS["okres_treningu_min"] * 60.0
    sesja_s = okres_s * T["trening_min_na_h"] / 60.0

    def gdzie(bi, si):
        return "%s/%s" % (biomy[bi]["id"], biomy[bi]["strefy"][si]["id"])

    def kamien(nazwa):
        kamienie[nazwa] = {"min": czas / 60.0, "poziom": L, "walki": walki, "przegrane": przegrane,
                           "zarobione": zarobione, "wydane": wydane}

    def nowosc(etykieta):
        nonlocal ost_nowosc, bez_nowosci, bez_nowosci_gdzie
        if czas - ost_nowosc > bez_nowosci:
            bez_nowosci, bez_nowosci_gdzie = czas - ost_nowosc, etykieta
        ost_nowosc = czas

    def wejscie(bi, si):
        k = gdzie(bi, si)
        if k not in strefy:
            strefy[k] = {"wejscie_min": czas / 60.0, "poziom": L, "walki": 0, "przegrane": 0}
            if len(strefy) > 1:
                nowosc(poprzednia[0])
            poprzednia[0] = k

    poprzednia = [gdzie(0, 0)]
    wejscie(0, 0)

    def moc(st):
        """Jedna liczba „ile daje przedmiot”: suma dodatków (blok tarczy liczony w procentach)."""
        st = dict(st)
        w = sum((st.pop("statystyki", None) or {}).values())
        return w + sum(100 * v if k == "tarcza" else v for k, v in st.items())

    def moc_slotu(slot):
        if slot in sklep:
            return moc(sklep[slot]["mod"])
        if kowal is not None:
            for q in LK.zalozone(Dk, klasa, kowal, None):
                if Dk["przedmioty"][q].get("slot") == slot:
                    return moc(LK.statystyki(Dk, q, kowal["przedmioty"][q]["poziom"]))
        return 0

    def kandydaci_sklepu():
        """Przedmioty sklepu dla tej klasy, na które gracza stać, ma poziom i które są lepsze od tego, co nosi."""
        if not katalog:
            return []
        return [it for it in katalog["przedmioty"]
                if it["klasa"] in ("*", klasa) and it["poziom"] <= L and it["cena"] <= zloto
                and moc(it["mod"]) > moc_slotu(it["slot"])]

    def miasto():
        """Wizyta w miasteczku: kowal (rozbiórka zapasu, ulepszenia od najtańszego) i sklep. → czy coś kupiono."""
        nonlocal kowal, zloto, wydane, ulepszen
        kupiono = False
        if kowal is not None:
            for pid in Dk["klasy"][klasa]["przedmioty"]:
                while LK.posiada(kowal, pid) and kowal["przedmioty"][pid]["zapas"] > 0:
                    _ok, kowal, _z = LK.rozbierz(Dk, kowal, klasa, pid)
            while True:
                kand = []
                for pid in LK.zalozone(Dk, klasa, kowal, None):
                    if Dk["przedmioty"][pid].get("slot") in sklep:
                        continue                 # w tym slocie gracz nosi już przedmiot ze sklepu
                    ok, k, _ile = LK.plan_ulepszenia(Dk, kowal, klasa, pid)
                    if ok and k["zloto"] <= zloto:
                        kand.append((k["zloto"], pid, k))
                if not kand:
                    break
                kand.sort(key=lambda t: (t[0], t[1]))
                c, pid, k = kand[0]
                zloto -= c
                wydane += c
                kowal = LK.ulepsz(Dk, kowal, pid, k)
                ulepszen += 1
                kupiono = True
        if katalog:
            while True:
                kand = kandydaci_sklepu()
                if not kand:
                    break
                it = min(kand, key=lambda t: (t["cena"], t["id"]))
                zloto -= it["cena"]
                wydane += it["cena"]
                sklep[it["slot"]] = it
                kupiono = True
        if kupiono:
            wersja[0] += 1
        return kupiono

    def stac_na_cos():
        if kowal is not None:
            mat = kowal["materialy"] + Dk["rozbiorka"]["materialy"] * sum(p["zapas"] for p in kowal["przedmioty"].values())
            for pid in LK.zalozone(Dk, klasa, kowal, None):
                pz = kowal["przedmioty"][pid]["poziom"]
                if pz < Dk["ulepszenie"]["maks"] and Dk["przedmioty"][pid].get("slot") not in sklep:
                    k = LK.koszt(Dk, pid, pz + 1)
                    if k and k["zloto"] <= zloto and k["materialy"] <= mat:
                        return True
        return bool(kandydaci_sklepu())

    while czas <= limit_s:
        # ------------------------------------------------------------ poza walką: mini-gry, kowal i sklep, jajko
        if T["trening_min_na_h"] > 0 and wygrane > 0 and czas - ost_trening >= okres_s - sesja_s:
            t0 = czas
            czas += CZAS["wizyta_miasto_s"]
            koniec = czas + sesja_s
            runda_s = G["Dt"]["runda"]["dlugosc_s"] + G["Dt"]["runda"]["odliczanie_s"] + CZAS["przerwa_rundy_s"]
            while czas + runda_s <= koniec + 1e-9:
                stat = min(glowne, key=lambda s: (LT.prog(G["Dt"], wytren[s], LT.pula(G["Dt"], L))
                                                  / G["Dt"]["gry"][s].get("waga", 1), s))
                wytren[stat], pasek[stat], _t, _n = runda_minigry(G, stat, L, wytren[stat], pasek[stat], S["celnosc"], los)
                czas += runda_s
            wersja[0] += 1
            if T["kowal"] or katalog:
                miasto()
                ost_wizyta = czas
            t_trening += czas - t0
            ost_trening = czas
        elif (kowal is not None or katalog) and (chce_wzmocnienia or czas - ost_wizyta >= CZAS["wizyta_co_s"]) and stac_na_cos():
            t0 = czas
            if miasto():
                czas += CZAS["wizyta_miasto_s"]
                t_miasto += czas - t0
            ost_wizyta = czas
        chce_wzmocnienia = False
        if T["pety"]:
            j = LP.jajko_krainy(Dp, biomy[b]["id"])
            if j is not None and jajka.get(j["id"], 0) < S["jajek_na_biom"]:
                c = LP.cena(Dp, j, jajka.get(j["id"], 0))
                if zloto >= c:
                    t0 = czas
                    czas += 2 * abs(x - biomy[b]["x_przybycia"]) / v + CZAS["jajko_s"]
                    zloto -= c
                    wydane += c
                    jajka[j["id"]] = jajka.get(j["id"], 0) + 1
                    pid = LP.losuj(Dp, j, los.random())
                    if pid not in pety:
                        nowosc(poprzednia[0])
                    pety[pid] = pety.get(pid, 0) + 1
                    naj = max(pety, key=lambda q: (rzadkosc_nr[LP.pet(Dp, q)["rzadkosc"]], ranga_peta[q]))
                    if naj != aktywny:
                        aktywny = naj
                        wersja[0] += 1
                    t_miasto += czas - t0
        # ------------------------------------------------------------ wybór potwora
        strefa = biomy[b]["strefy"][i]
        cel_i = i
        m = _wybierz(M[b][i], L, S["margines_poziomu"], czas)
        if m is None and strefa["ranga"] == "rzadki" and i > 0:
            cel_i = i - 1                      # rzadki potwór jeszcze nie wrócił — walki w poprzedniej zagrodzie
            m = _wybierz(M[b][cel_i], L, S["margines_poziomu"], czas)
        if m is None:
            t = min(q["od"] for q in M[b][cel_i]["lista"])
            t_odrodzenie += t - czas
            czas = t
            continue
        cel = biomy[b]["strefy"][cel_i]
        gat = cel["gatunek"]
        czas += CZAS["dojscie_s"][cel["ranga"]]
        if czas < wolny_od:                    # blokada po walce oglądanej szybciej niż ×1
            t_blokada += wolny_od - czas
            czas = wolny_od
        # ------------------------------------------------------------ walka (port silnika)
        opis, premia = bohater()
        ziarno_walki = los.randrange(1, 2 ** 31 - 1)
        r = silnik.symuluj(opis, {"potwor": gat, "poziom": m["poziom"]}, ziarno_walki)
        wygrana = r["wynik"] == "wygrana"
        znany = gat in znane
        if cel["straznik"]:
            pomin, tempo = znany and S["pomija_straznika"], S["tempo_straznika"]
        else:
            pomin = znany and los.random() < S["pomija_znane"]
            tempo = S["tempo_znane"] if znany else S["tempo_nowe"]
        start = czas
        if pomin:
            t_widok = CZAS["pominiecie_s"]
        else:
            t_widok = r["czas"] if tempo <= 1 else (r["czas"] - G["final_s"]) / tempo + G["final_s"]
        czas += t_widok + CZAS["ekran_wyniku_s"]
        t_walk += t_widok
        # serwer nie zacznie następnej walki przed końcem „blokady sesji” (pominięcie znanego potwora zwalnia od razu)
        wolny_od = 0.0 if pomin else start + r["czas"] / tempo_blokady - G["zapas_sesji_s"]
        walki += 1
        znane.add(gat)
        walki_gat[gat] = walki_gat.get(gat, 0) + 1
        if gat == seria_gat:
            seria_n += 1
        else:
            seria_gat, seria_n = gat, 1
        if seria_n > seria_max:
            seria_max, seria_max_gat = seria_n, gat
        ks = strefy[gdzie(b, cel_i)]
        ks["walki"] += 1
        lup = r["lup"]
        dod = LS.premia_lupu(Ds, lup, premia)
        xp_walki = lup["doswiadczenie"] + dod["doswiadczenie"]
        L, xp, awanse = LS.awans(Ds, L, xp, xp_walki)
        if awanse:
            if czas - ost_awans > bez_awansu:
                bez_awansu, bez_awansu_gdzie = czas - ost_awans, gdzie(b, cel_i)
            ost_awans = czas
        zloto_walki = kara = 0
        if cel["straznik"]:
            sg = straznicy[biomy[b]["id"]]
            sg["proby"] += 1
            if sg["poziom_pierwszej"] is None:
                sg["poziom_pierwszej"] = opis["poziom"]
        if wygrana:
            wygrane += 1
            zloto_walki = lup["zloto"] + dod["zloto"]
            zloto += zloto_walki
            zarobione += zloto_walki
            m["od"] = czas + M[b][cel_i]["odrodzenie"]
            if kowal is not None:
                kowal, wyn = LK.lup(Dk, kowal, klasa, cel["ranga"], los.random(), los.random())
                if wyn:
                    lupow += 1
                    if wyn["nowy"]:
                        wersja[0] += 1
            if wygrane == 1:
                kamien("pierwsza_wygrana")
        else:
            przegrane += 1
            ks["przegrane"] += 1
            kara = LS.kara_przegranej(Ds, zloto, m["poziom"], Ds["kara"]["procent"])
            zloto -= kara
            stracone += kara
        if sledz is not None:
            sledz.append({"opis": opis, "potwor": gat, "poziom": m["poziom"], "ziarno": ziarno_walki, "wynik": r["wynik"],
                          "lup": dict(lup), "xp": xp_walki, "zloto": zloto_walki, "kara": kara, "czas": czas,
                          "biom": biomy[b]["id"], "strefa": cel["id"], "pominieta": pomin, "tempo": tempo,
                          "poziom_po": L, "xp_po": xp, "zloto_po": zloto})
        # ------------------------------------------------------------ dokąd dalej
        strefy_b = biomy[b]["strefy"]
        if wygrana:
            z_rzedu = 0
            if cel["straznik"]:
                kamien("straznik_" + biomy[b]["id"])
                nowosc(gdzie(b, i))
                czas += abs(biomy[b]["brama_x"] - cel["x"]) / v
                kamien("brama_" + biomy[b]["id"])
                if b + 1 >= len(biomy):
                    break
                b += 1
                i = 0
                czas += biomy[b]["przelot_s"] + abs(biomy[b]["strefy"][0]["x"] - biomy[b - 1]["brama_x"]) / v
                x = biomy[b]["strefy"][0]["x"]
                wejscie(b, 0)
                continue
            nastepna = strefy_b[i + 1]
            prog = nastepna["od"] + (S["zapas_straznika"] if nastepna["straznik"] else S["zapas_wejscia"])
            prog = max(prog, min_wejscia.get((b, i + 1), 0), wymagany if nastepna["straznik"] else 0)
            if farma > 0:
                farma -= 1
                if farma > 0:
                    continue
            if L >= prog:
                czas += abs(nastepna["x"] - x) / v
                x = nastepna["x"]
                i += 1
                wejscie(b, i)
            continue
        z_rzedu += 1
        if cel["straznik"]:
            straznicy[biomy[b]["id"]]["przegrane"] += 1
            farma = S["farma_po_strazniku"]
            wymagany = L + S["poziomy_po_strazniku"] if S["poziomy_po_strazniku"] > 0 else 0
            chce_wzmocnienia = True
            czas += abs(strefy_b[i - 1]["x"] - x) / v
            x = strefy_b[i - 1]["x"]
            i -= 1
            z_rzedu = 0
        elif cel_i == i and z_rzedu >= S["przegrane_do_cofniecia"] and i > 0:
            min_wejscia[(b, i)] = L + 1
            czas += abs(strefy_b[i - 1]["x"] - x) / v
            x = strefy_b[i - 1]["x"]
            i -= 1
            z_rzedu = 0

    ukonczone = ("straznik_" + biomy[-1]["id"]) in kamienie
    if czas - ost_awans > bez_awansu:
        bez_awansu, bez_awansu_gdzie = czas - ost_awans, gdzie(b, i)
    if not ukonczone and czas - ost_nowosc > bez_nowosci:
        bez_nowosci, bez_nowosci_gdzie = czas - ost_nowosc, gdzie(b, i)
    klucze = list(strefy)
    for n, k in enumerate(klucze):
        koniec = strefy[klucze[n + 1]]["wejscie_min"] if n + 1 < len(klucze) else czas / 60.0
        strefy[k]["czas_min"] = koniec - strefy[k]["wejscie_min"]
    return {
        "ukonczone": ukonczone, "czas_min": czas / 60.0, "poziom": L, "walki": walki, "wygrane": wygrane,
        "przegrane": przegrane, "zloto": zloto, "zarobione": zarobione, "wydane": wydane, "stracone": stracone,
        "kamienie": kamienie, "strefy": strefy, "straznicy": straznicy, "utknal_w": gdzie(b, i) if not ukonczone else "",
        "wytrenowane": sum(wytren.values()), "ulepszen": ulepszen, "lupow_przedmiotow": lupow,
        "jajek": sum(jajka.values()), "pet": aktywny or "", "sklep": len(sklep),
        "min_trening": t_trening / 60.0, "min_miasto": t_miasto / 60.0, "min_walk": t_walk / 60.0,
        "min_blokady": t_blokada / 60.0, "min_odrodzenia": t_odrodzenie / 60.0,
        "bez_awansu_min": bez_awansu / 60.0, "bez_awansu_gdzie": bez_awansu_gdzie,
        "bez_nowosci_min": bez_nowosci / 60.0, "bez_nowosci_gdzie": bez_nowosci_gdzie,
        "seria_potwora": seria_max, "seria_potwora_kto": seria_max_gat, "walki_gatunku": walki_gat,
    }


# ====================================================================================================================
# ZBIERANIE WYNIKÓW
# ====================================================================================================================
def kwantyl(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    j = (len(xs) - 1) * q
    lo, hi = int(math.floor(j)), int(math.ceil(j))
    return xs[lo] + (xs[hi] - xs[lo]) * (j - lo)


def rozklad(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return {"med": round(statistics.median(xs), 2), "p10": round(kwantyl(xs, 0.1), 2), "p90": round(kwantyl(xs, 0.9), 2),
            "n": len(xs)}


def _najczestszy(xs):
    xs = [x for x in xs if x]
    return max(sorted(set(xs)), key=xs.count) if xs else ""


def podsumuj(wyniki):
    """Lista przebiegów → mediany i rozrzut (10%–90%)."""
    n = len(wyniki)
    ok = [w for w in wyniki if w["ukonczone"]]
    P = {"przebiegow": n, "ukonczylo_proc": round(100.0 * len(ok) / n, 1),
         "utknal_w": _najczestszy([w["utknal_w"] for w in wyniki])}
    for pole in ("czas_min", "poziom", "walki", "przegrane", "zarobione", "wydane", "stracone", "zloto", "wytrenowane",
                 "ulepszen", "jajek", "min_trening", "min_miasto", "min_walk", "min_blokady", "min_odrodzenia"):
        P[pole] = rozklad([w[pole] for w in ok])
    for pole in ("bez_awansu_min", "bez_nowosci_min", "seria_potwora"):
        P[pole] = rozklad([w[pole] for w in wyniki])
    P["bez_awansu_gdzie"] = _najczestszy([w["bez_awansu_gdzie"] for w in wyniki])
    P["bez_nowosci_gdzie"] = _najczestszy([w["bez_nowosci_gdzie"] for w in wyniki])
    P["seria_potwora_kto"] = _najczestszy([w["seria_potwora_kto"] for w in wyniki])
    nazwy = []
    for w in wyniki:
        for k in w["kamienie"]:
            if k not in nazwy:
                nazwy.append(k)
    P["kamienie"] = {}
    for k in nazwy:
        maja = [w["kamienie"][k] for w in wyniki if k in w["kamienie"]]
        P["kamienie"][k] = {"dotarlo_proc": round(100.0 * len(maja) / n, 1)}
        for pole in ("min", "poziom", "walki", "przegrane", "zarobione", "wydane"):
            P["kamienie"][k][pole] = rozklad([m[pole] for m in maja])
    P["strefy"] = {}
    for w in wyniki:
        for k in w["strefy"]:
            P["strefy"].setdefault(k, None)
    for k in P["strefy"]:
        maja = [w["strefy"][k] for w in wyniki if k in w["strefy"]]
        P["strefy"][k] = {pole: round(statistics.median(m[pole] for m in maja), 2)
                          for pole in ("wejscie_min", "poziom", "walki", "przegrane", "czas_min")}   # same mediany
    P["straznicy"] = {}
    for bid in wyniki[0]["straznicy"]:
        byli = [w["straznicy"][bid] for w in wyniki if w["straznicy"][bid]["proby"] > 0]
        if not byli:
            continue
        P["straznicy"][bid] = {
            "proby": rozklad([s["proby"] for s in byli]),
            "poziom_pierwszej": rozklad([s["poziom_pierwszej"] for s in byli]),
            "za_pierwszym_proc": round(100.0 * sum(1 for w in wyniki if w["straznicy"][bid]["proby"] == 1
                                                    and ("straznik_" + bid) in w["kamienie"]) / len(byli), 1),
            "utknelo_proc": round(100.0 * sum(1 for s in byli if s["przegrane"] >= CZAS["utknal_od_prob"]) / len(byli), 1)}
    gat = {}
    for w in wyniki:
        for g, ile in w["walki_gatunku"].items():
            gat.setdefault(g, []).append(ile)
    P["walki_gatunku"] = {g: round(statistics.median(v), 1) for g, v in gat.items()}
    return P


def _zadanie(arg):
    klasa, tryb, wariant, zmiany, ziarna = arg
    G = gra(zmiany)
    return (klasa, tryb, wariant), podsumuj([przejscie(G, klasa, tryb, wariant, z) for z in ziarna])


def policz(zadania, procesy):
    if procesy <= 1:
        return [_zadanie(z) for z in zadania]
    import multiprocessing
    with multiprocessing.Pool(procesy) as pula:
        return pula.map(_zadanie, zadania, chunksize=1)


def szanse_straznikow(G, ziaren, ziarno):
    """Szansa wygranej ze Strażnikiem krainy na poziomach wokół jego poziomu: sam bohater i bohater z dodatkami
    (przykład: po 6 punktów z mini-gier w trzech głównych statystykach + pełny zestaw kowala ulepszony o 2)."""
    Ds, Dk = G["Ds"], G["Dk"]
    w = {}
    for bm in G["biomy"]:
        s = bm["strefy"][-1]
        for klasa in Ds["klasy"]:
            glowne = sorted(Ds["statystyki"], key=lambda q: -Ds["rozklady"][klasa][q])[:3]
            zestaw = LK.nowe(Dk)
            for pid in Dk["klasy"][klasa]["przedmioty"]:
                zestaw["przedmioty"][pid] = {"poziom": 2, "zapas": 0}
            mod = _czysty(G, LK.mod(Dk, klasa, zestaw, LK.zalozone(Dk, klasa, zestaw, None)), "kowala")
            for d in (-1, 0, 1, 2, 3):
                L = max(1, s["od"] + d)
                for nazwa, wytren, mody in (("sam", None, None), ("z_dodatkami", {q: 6 for q in glowne}, [mod])):
                    opis, _ = opis_bohatera(G, klasa, L, wytren, mody)
                    los = random.Random("straznik|%s|%s|%d|%d" % (bm["id"], klasa, d, ziarno))
                    wyg = sum(silnik.symuluj(opis, {"potwor": s["gatunek"], "poziom": s["od"]},
                                             los.randrange(1, 2 ** 31 - 1))["wynik"] == "wygrana" for _ in range(ziaren))
                    w.setdefault(bm["id"], {}).setdefault(klasa, {}).setdefault(nazwa, {})[str(d)] = round(100.0 * wyg / ziaren)
    return w


# ====================================================================================================================
# TABELE (Markdown)
# ====================================================================================================================
ZNACZNIK_OD, ZNACZNIK_DO = "<!-- TABELE:START -->", "<!-- TABELE:KONIEC -->"


def fm(x):
    """Minuty: do 10 z jednym miejscem po przecinku, dalej całe."""
    if x is None:
        return "—"
    return ("%.1f" % x).replace(".", ",") if x < 10 else "%.0f" % x


def fl(x):
    return "—" if x is None else ("%.0f" % x)


def _med(d, *sciezka):
    for k in sciezka:
        if d is None:
            return None
        d = d.get(k)
    return d.get("med") if isinstance(d, dict) else d


def tabele(R):
    """Wynik (słownik jak w JSON) → tekst Markdown z tabelami."""
    G = gra()
    Ds = G["Ds"]
    nk = Ds["nazwy_klas"]
    klasy = R["meta"]["klasy"]
    biomy = [b["id"] for b in G["biomy"]]
    nazwy_b = {b["id"]: b["nazwa"] for b in G["biomy"]}
    nazwa_potwora = {k: p["nazwa"] for k, p in G["przeciwnicy"].items()}
    w = []
    for wid in R["meta"]["warianty"]:
        W = R["wyniki"][wid]
        w.append("### Czasy do kamieni milowych — świat „%s” (minuty gry, mediana)" % WARIANTY[wid]["nazwa"])
        w.append("")
        w.append("| Sposób gry | Klasa | 1. wygrana | " + " | ".join("Strażnik: %s" % nazwy_b[b] for b in biomy)
                 + " | Koniec: 10%–90% graczy | Skończyło |")
        w.append("|---|---|---:|" + "---:|" * len(biomy) + "---|---:|")
        for tid in R["meta"]["tryby"]:
            for k in klasy:
                P = W[tid][k]
                kon = P["kamienie"].get("straznik_" + biomy[-1], {})
                w.append("| %s | %s | %s | %s | %s | %s%% |" % (
                    TRYBY[tid]["nazwa"], nk[k], fm(_med(P, "kamienie", "pierwsza_wygrana", "min")),
                    " | ".join(fm(_med(P, "kamienie", "straznik_" + b, "min")) for b in biomy),
                    ("%s–%s" % (fm(kon["min"]["p10"]), fm(kon["min"]["p90"]))) if kon.get("min") else "—",
                    fl(P["ukonczylo_proc"])))
        w.append("")
        w.append("Brama otwiera się od razu po wygranej ze Strażnikiem; dojście do niej to kilka sekund "
                 "(dokładne czasy bram są w pliku JSON, pola `brama_…`).")
        w.append("")
        w.append("### Poziom, walki i Złoto — świat „%s” (mediana)" % WARIANTY[wid]["nazwa"])
        w.append("")
        w.append("| Sposób gry | Klasa | Poziom przy bramach | Walk | Przegranych | Złoto zarobione | Złoto wydane | "
                 "Złoto stracone po przegranych | Punkty z mini-gier |")
        w.append("|---|---|---|---:|---:|---:|---:|---:|---:|")
        for tid in R["meta"]["tryby"]:
            for k in klasy:
                P = W[tid][k]
                w.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                    TRYBY[tid]["nazwa"], nk[k],
                    " / ".join(fl(_med(P, "kamienie", "brama_" + b, "poziom")) for b in biomy),
                    fl(_med(P, "walki")), fl(_med(P, "przegrane")), fl(_med(P, "zarobione")), fl(_med(P, "wydane")),
                    fl(_med(P, "stracone")), fl(_med(P, "wytrenowane"))))
        w.append("")
        w.append("### Strażnicy — świat „%s”" % WARIANTY[wid]["nazwa"])
        w.append("")
        w.append("Dla każdej krainy: poziom przy pierwszej próbie · prób do wygranej (mediana / co dziesiąty gracz) · "
                 "ilu graczy utknęło (co najmniej %d przegranych prób)." % CZAS["utknal_od_prob"])
        w.append("")
        w.append("| Sposób gry | Klasa | " + " | ".join(nazwy_b[b] for b in biomy) + " |")
        w.append("|---|---|" + "---|" * len(biomy))
        for tid in R["meta"]["tryby"]:
            for k in klasy:
                P = W[tid][k]
                kom = []
                for b in biomy:
                    s = P["straznicy"].get(b)
                    kom.append("—" if not s else "poz. %s · %s / %s · %s%%" % (
                        fl(s["poziom_pierwszej"]["med"]), fl(s["proby"]["med"]), fl(s["proby"]["p90"]), fl(s["utknelo_proc"])))
                w.append("| %s | %s | %s |" % (TRYBY[tid]["nazwa"], nk[k], " | ".join(kom)))
        w.append("")
        w.append("### Nuda i przestoje — świat „%s” (mediana)" % WARIANTY[wid]["nazwa"])
        w.append("")
        w.append("| Sposób gry | Klasa | Najdłużej bez awansu | Najdłużej bez nowej zagrody | Najdłuższa seria jednego "
                 "potwora | Czekanie (odradzanie + blokada) |")
        w.append("|---|---|---|---|---|---:|")
        for tid in R["meta"]["tryby"]:
            for k in klasy:
                P = W[tid][k]
                czek = (_med(P, "min_odrodzenia") or 0) + (_med(P, "min_blokady") or 0)
                w.append("| %s | %s | %s min (%s) | %s min (%s) | %s × %s | %s min |" % (
                    TRYBY[tid]["nazwa"], nk[k], fm(_med(P, "bez_awansu_min")), P["bez_awansu_gdzie"],
                    fm(_med(P, "bez_nowosci_min")), P["bez_nowosci_gdzie"], fl(_med(P, "seria_potwora")),
                    nazwa_potwora.get(P["seria_potwora_kto"], P["seria_potwora_kto"]), fm(czek)))
        w.append("")
    # zagrody: gdzie schodzi czas (jeden sposób gry, średnio po klasach)
    wid = R["meta"]["warianty"][-1]
    for tid in [t for t in ("walki", "wszystko") if t in R["meta"]["tryby"]]:
        w.append("### Gdzie schodzi czas — „%s”, świat „%s” (mediana, średnio z klas)" % (TRYBY[tid]["nazwa"],
                                                                                      WARIANTY[wid]["nazwa"]))
        w.append("")
        w.append("Minuty liczą się od pierwszego wejścia do zagrody do pierwszego wejścia do następnej (przy Strażniku: "
                 "razem z cofaniem się po przegranej). Walki — razem z powrotami do tej zagrody.")
        w.append("")
        w.append("| Zagroda | Potwór (poziomy) | Poziom na wejściu | Minut | Walk | Przegranych |")
        w.append("|---|---|---:|---:|---:|---:|")
        for bm in G["biomy"]:
            for s in bm["strefy"]:
                klucz = "%s/%s" % (bm["id"], s["id"])
                kom = []
                for pole in ("poziom", "czas_min", "walki", "przegrane"):
                    xs = [_med(R["wyniki"][wid][tid][k], "strefy", klucz, pole) for k in klasy]
                    xs = [x for x in xs if x is not None]
                    kom.append(statistics.mean(xs) if xs else None)
                w.append("| %s | %s (%d–%d) | %s | %s | %s | %s |" % (
                    klucz, nazwa_potwora[s["gatunek"]], s["od"], s["do"], fl(kom[0]), fm(kom[1]), fl(kom[2]), fm(kom[3])))
        w.append("")
    if R.get("szanse_straznikow"):
        w.append("### Szansa wygranej ze Strażnikiem (%), bohater na poziomie Strażnika −1 … +3")
        w.append("")
        w.append("„Sam” = bohater bez niczego. „Z dodatkami” = po 6 punktów z mini-gier w trzech głównych statystykach "
                 "i pełny zestaw kowala ulepszony o 2.")
        w.append("")
        w.append("| Strażnik | Klasa | Sam: −1 / 0 / +1 / +2 / +3 | Z dodatkami: −1 / 0 / +1 / +2 / +3 |")
        w.append("|---|---|---|---|")
        for bm in G["biomy"]:
            s = bm["strefy"][-1]
            for k in klasy:
                X = R["szanse_straznikow"][bm["id"]][k]
                w.append("| %s (poz. %d) | %s | %s | %s |" % (
                    nazwa_potwora[s["gatunek"]], s["od"], nk[k],
                    " / ".join(str(X["sam"][str(d)]) for d in (-1, 0, 1, 2, 3)),
                    " / ".join(str(X["z_dodatkami"][str(d)]) for d in (-1, 0, 1, 2, 3))))
        w.append("")
    if R.get("propozycje"):
        w.append("### Propozycje zmian liczb — „przed / po” (świat „%s”, mediana z trzech klas)" %
                 WARIANTY[R["meta"]["propozycje_wariant"]]["nazwa"])
        w.append("")
        w.append("Liczone na kopii danych; pliki gry bez zmian. Kolumny: minuty do końca · różnica między klasami "
                 "(najwolniejsza − najszybsza) · przegranych · prób ze Strażnikami i ilu graczy na nich utknęło "
                 "(%s) · najdłużej bez awansu." % " / ".join(nazwy_b[b] for b in biomy))
        w.append("")
        for tid in R["meta"]["propozycje_tryby"]:
            w.append("**%s**" % TRYBY[tid]["nazwa"])
            w.append("")
            w.append("| Zmiana | Koniec (min) | Różnica klas (min) | Przegranych | Prób ze Strażnikami | "
                     "Utknęło (%) | Bez awansu (min) |")
            w.append("|---|---:|---:|---:|---|---|---:|")
            for pid, X in R["propozycje"].items():
                Y = X["wyniki"][tid]
                czasy = [_med(Y[k], "czas_min") for k in klasy]
                czasy = [c for c in czasy if c is not None]

                def sr(*sc):
                    xs = [_med(Y[k], *sc) for k in klasy]
                    xs = [q for q in xs if q is not None]
                    return statistics.mean(xs) if xs else None
                w.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                    X["nazwa"], fm(statistics.mean(czasy)) if czasy else "—",
                    fm(max(czasy) - min(czasy)) if czasy else "—", fl(sr("przegrane")),
                    " / ".join(fm(sr("straznicy", b, "proby")) for b in biomy),
                    " / ".join(fl(sr("straznicy", b, "utknelo_proc")) for b in biomy), fm(sr("bez_awansu_min"))))
            w.append("")
    w.append("_Uruchomienie: `python -B swiat/przejscie_gry/symulacja_przejscia.py --przebiegow %d --ziarno %d` · "
             "%d przebiegów na komórkę · krzywa doświadczenia %s × L^%s · katalog sklepu: %s · liczone %s._" % (
                 R["meta"]["przebiegow"], R["meta"]["ziarno"], R["meta"]["przebiegow"],
                 ("%.2f" % Ds["krzywa"]["a"]).replace(".", ","), ("%.1f" % Ds["krzywa"]["b"]).replace(".", ","),
                 R["meta"]["katalog_sklepu"] or "jeszcze go nie ma", R["meta"]["data"]))
    return "\n".join(w) + "\n"


def wstaw_tabele(sciezka, tekst):
    """Podmienia tabele między znacznikami w raporcie; reszta raportu (wnioski pisane ręcznie) zostaje."""
    blok = ZNACZNIK_OD + "\n\n" + tekst + "\n" + ZNACZNIK_DO
    if os.path.isfile(sciezka):
        with open(sciezka, encoding="utf-8") as f:
            stary = f.read()
        if ZNACZNIK_OD in stary and ZNACZNIK_DO in stary:
            nowy = stary[:stary.index(ZNACZNIK_OD)] + blok + stary[stary.index(ZNACZNIK_DO) + len(ZNACZNIK_DO):]
        else:
            nowy = stary.rstrip("\n") + "\n\n" + blok + "\n"
    else:
        nowy = "# Przejście gry w liczbach\n\n" + blok + "\n"
    with open(sciezka, "w", encoding="utf-8", newline="\n") as f:
        f.write(nowy)


def main(argv=None):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Przejście gry w liczbach: od 1. poziomu do Strażnika Dżungli")
    ap.add_argument("--przebiegow", type=int, default=40, help="graczy na klasę, sposób gry i wariant świata")
    ap.add_argument("--ziarno", type=int, default=1)
    ap.add_argument("--procesy", type=int, default=3)
    ap.add_argument("--tryby", default=",".join(TRYBY))
    ap.add_argument("--warianty", default=",".join(WARIANTY))
    ap.add_argument("--klasy", default="")
    ap.add_argument("--bez-propozycji", action="store_true")
    ap.add_argument("--bez-zapisu", action="store_true", help="tylko tabele na ekran")
    ap.add_argument("--json", default=os.path.join(TU, "przejscie_w_liczbach.json"))
    ap.add_argument("--md", default=os.path.join(TU, "PRZEJSCIE_W_LICZBACH.md"))
    ap.add_argument("--jeden", nargs=4, metavar=("KLASA", "TRYB", "WARIANT", "ZIARNO"))
    a = ap.parse_args(argv)
    t0 = time.time()
    G = gra()
    if a.jeden:
        w = przejscie(G, a.jeden[0], a.jeden[1], a.jeden[2], int(a.jeden[3]))
        print(json.dumps(w, ensure_ascii=False, indent=1))
        return 0
    klasy = [k for k in a.klasy.split(",") if k] or list(G["Ds"]["klasy"])
    tryby = [t for t in a.tryby.split(",") if t]
    warianty = [x for x in a.warianty.split(",") if x]
    ziarna = [a.ziarno * 1000 + n for n in range(a.przebiegow)]
    zadania = [(k, t, wr, None, ziarna) for wr in warianty for t in tryby for k in klasy]
    prop = {} if a.bez_propozycji else PROPOZYCJE
    for pid, X in prop.items():
        zadania += [(k, t, PROPOZYCJE_WARIANT, X["zmiany"], ziarna) for t in PROPOZYCJE_TRYBY for k in klasy]
    wyn = policz(zadania, a.procesy)
    R = {"meta": {"opis": "Przejście gry w liczbach (D-106) — propozycja, nie kanon. Czasy w minutach gry.",
                  "data": time.strftime("%Y-%m-%d"), "przebiegow": a.przebiegow, "ziarno": a.ziarno, "klasy": klasy,
                  "tryby": tryby, "warianty": warianty, "parametry_czasu": CZAS, "style": STYLE,
                  "sposoby_gry": TRYBY, "warianty_swiata": WARIANTY, "propozycje_tryby": PROPOZYCJE_TRYBY,
                  "propozycje_wariant": PROPOZYCJE_WARIANT,
                  "katalog_sklepu": G["katalog"]["plik"] if G["katalog"] else None,
                  "krzywa": G["Ds"]["krzywa"],
                  "zagrody": {b["id"]: [{k: s[k] for k in ("id", "gatunek", "od", "do", "odrodzenie", "naraz")}
                                        for s in b["strefy"]] for b in G["biomy"]}},
         "wyniki": {}, "propozycje": {}}
    n = 0
    for wr in warianty:
        for t in tryby:
            for k in klasy:
                R["wyniki"].setdefault(wr, {}).setdefault(t, {})[k] = wyn[n][1]
                n += 1
    for pid, X in prop.items():
        R["propozycje"][pid] = {"nazwa": X["nazwa"], "zmiany": X["zmiany"], "wyniki": {}}
        for t in PROPOZYCJE_TRYBY:
            for k in klasy:
                R["propozycje"][pid]["wyniki"].setdefault(t, {})[k] = {a_: b_ for a_, b_ in wyn[n][1].items()
                                                                       if a_ not in ("strefy", "walki_gatunku")}
                n += 1
    R["szanse_straznikow"] = szanse_straznikow(gra(), 300, a.ziarno)
    tekst = tabele(R)
    if a.bez_zapisu:
        print(tekst)
    else:
        tekst_json = json.dumps(R, ensure_ascii=False, indent=1, sort_keys=True)
        # słowniki samych liczb (mediana i rozrzut) w jednej linii — plik kilka razy krótszy
        tekst_json = re.sub(r'\{\s*((?:"[^"\n]+": (?:-?[0-9][0-9.eE+-]*|"[^"\n]*"|null|true|false),?\s*)+)\}',
                            lambda m: "{" + re.sub(r"\s+", " ", m.group(1)).strip() + "}", tekst_json)
        with open(a.json, "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst_json + "\n")
        wstaw_tabele(a.md, tekst)
        print("zapisano: %s, %s" % (os.path.relpath(a.json, REPO), os.path.relpath(a.md, REPO)))
    print("czas liczenia: %.0f s" % (time.time() - t0), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
