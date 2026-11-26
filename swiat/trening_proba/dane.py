#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator zrodla/DaneTreningu.luau — dane mini-gier Training Center (próba) dla serwera i klienta w Studio.

    python -B swiat/trening_proba/dane.py               # zapisuje zrodla/DaneTreningu.luau
    python -B swiat/trening_proba/dane.py --sprawdz     # kod 1, gdy plik w zrodla/ jest nieaktualny
    python -B swiat/trening_proba/dane.py --wyjscie DIR # zapis do innego folderu (test powtarzalności)

Źródła (tylko odczyt): ustawienia.json (jedyne źródło liczb pakietu), swiat/miasteczko_bazar/znaczniki.json (punkt
trenera w bazarze — zapas, gdy w Studio nie ma kontenera bazaru), swiat/miasteczko_bazar_gra/miejsca.json (id miejsca
i nazwa zdarzenia OknoMiejsca). Położenia w świecie liczy się tu (środek areny + układ lokalny stanowisk), więc w kodzie
Luau nie ma żadnej liczby położenia. Przypadki wzorcowe liczy lustro logika_treningu.py. Od D-108 każde stanowisko stoi
w swojej scenerii krainy (ustawienia „scenerie”), a w swiat.<gra>.trener_npc jest punkt trenera dla postaci NPC.
"""
import copy
import hashlib
import json
import math
import os
import random
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if not sys.path or sys.path[0] != TU:
    sys.path.insert(0, TU)
import logika_treningu as LT  # noqa: E402

USTAWIENIA = os.path.join(TU, "ustawienia.json")
ZNACZNIKI = os.path.join(REPO, "swiat", "miasteczko_bazar", "znaczniki.json")
MIEJSCA_BAZARU = os.path.join(REPO, "swiat", "miasteczko_bazar_gra", "miejsca.json")
PLIK_LUAU = "DaneTreningu.luau"
ZRODLA = os.path.join(TU, "zrodla")

# 11 plików dźwięku wbudowanych w klienta Roblox (content/sounds; lista z swiat/test_walki2/zrodla/Ustawienia.luau)
DZWIEKI_WBUDOWANE = {"action_falling.ogg", "action_footsteps_plastic.mp3", "action_get_up.mp3", "action_jump.mp3",
                     "action_jump_land.mp3", "action_swim.mp3", "impact_explosion_03.mp3", "impact_water.mp3",
                     "oof.ogg", "ouch.ogg", "volume_slider.ogg"}
KLAWISZE = {"Up", "Down", "Left", "Right", "W", "A", "S", "D", "F", "Q", "E", "Space", "Return", "Thumbstick1",
            "DPadUp", "DPadDown", "DPadLeft", "DPadRight", "ButtonA", "ButtonB", "ButtonX", "ButtonY", "ButtonR1",
            "ButtonR2", "ButtonL1", "ButtonSelect"}
TYPY = ("kierunki", "blok", "rytm", "unik", "sekwencja", "lapanie")
CZASOWE = ("kierunki", "blok", "rytm", "unik")  # okno czasu wokół zdarzenia, rozdzielność zdarzeń
# zdarzenia arkusza efektów pakietu swiat/dzwiek_gra (tylko odczyt) — dzwieki_katalog może wskazywać tylko je
DZWIEK_GRA = os.path.join(REPO, "swiat", "dzwiek_gra", "ustawienia.json")

# nazwy instancji areny, które klient animuje lokalnie (scena.py buduje je pod tymi nazwami)
NAZWY = {
    "arena": "Arena",
    "miotacz_ramie": "Arena/Sila/Miotacz/RamieP",
    "strefy": "Arena/Sila/Strefy",
    "golem_piesc": "Arena/Pancerz/Golem/Piesc",
    "golem_oczy": ["Arena/Pancerz/Golem/OkoL", "Arena/Pancerz/Golem/OkoP"],
    "tasma_pasy": "Arena/Kondycja/Tasma",
    "cele_stop": "Arena/Kondycja/Cele",
    "podest_klody": "Arena/Zrecznosc/Podest",
    "beben": "Arena/Kondycja/Trener/Beben",
    "palka": "Arena/Kondycja/Trener/RamieP",
    "ramie_klody": "Arena/Zrecznosc/Ramie",
    "runy": "Arena/Inteligencja/Runy",
    "kula_maga": "Arena/Inteligencja/Mag/Kula",
    "tory": "Arena/Szczescie/Tory",
    "tablica_wejscia": "TablicaWejscia/E",
}


class BladDanych(Exception):
    pass


def _czytaj_json(sciezka):
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def _dodaj(a, b):
    return [round(a[i] + b[i], 4) for i in range(3)]


def _w(x, a, b):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and a <= x <= b


def _sprawdz_gre(K, gid, G):
    """Reguły jednej mini-gry (zależne od typu) → BladDanych."""
    typ = G.get("typ")
    if typ not in TYPY:
        raise BladDanych("%s: typ %s" % (gid, typ))
    poz = G["poziomy"]
    if not poz or poz[0]["od_s"] != 0:
        raise BladDanych("%s: pierwszy poziom musi zaczynać się od 0 s" % gid)
    for a, b in zip(poz, poz[1:]):
        if b["od_s"] <= a["od_s"]:
            raise BladDanych("%s: poziomy nie rosną" % gid)
    if not _w(G.get("rozrzut", 0), 0, 0.4999):
        raise BladDanych("%s: rozrzut" % gid)
    if not _w(G.get("waga", 1), 0.05, 10):
        raise BladDanych("%s: waga (mnożnik jednostek paska) poza 0,05–10" % gid)
    kub = G.get("kubelek")
    if kub is not None and not (_w(kub.get("pojemnosc"), 1, 50) and _w(kub.get("uzupelnianie_na_s"), 0.1, 50)):
        raise BladDanych("%s: kubelek" % gid)
    for a in G.get("przyciski", G["akcje"]):
        if a not in K["sterowanie"] or isinstance(K["sterowanie"][a], list):
            raise BladDanych("%s: akcja %s bez wpisu w sterowanie" % (gid, a))
    if len(set(G["akcje"])) != len(G["akcje"]):
        raise BladDanych("%s: powtórzone akcje" % gid)
    if typ in CZASOWE:
        for p in poz:
            if not (0 < p["okno_s"] < 1):
                raise BladDanych("%s: okno %s" % (gid, p["okno_s"]))
            # rozdzielność: najkrótszy odstęp dłuższy niż dwa okna + 0,05 s — zgłoszenie zawsze wskazuje jedno zdarzenie
            najkrotszy = p["odstep_s"] * (1 - G["rozrzut"])
            if typ == "rytm" and p["podbiegi"] > 0:
                najkrotszy = najkrotszy * G["podbieg"]["mnoznik"]
            if najkrotszy <= 2 * p["okno_s"] + 0.05:
                raise BladDanych("%s: odstęp %s za krótki przy oknie %s" % (gid, p["odstep_s"], p["okno_s"]))
    if typ == "kierunki":
        for p in poz:
            if not (1 <= p["kierunki"] <= len(G["kierunki"])):
                raise BladDanych("%s: kierunki %s" % (gid, p["kierunki"]))
        if sorted(G["akcje"]) != sorted(G["kierunki"]):
            raise BladDanych("%s: akcje ≠ kierunki" % gid)
    elif typ == "blok":
        for p in poz:
            if not (0 <= p["zmylki"] <= 0.5):
                raise BladDanych("%s: zmyłki %s" % (gid, p["zmylki"]))
        if G["akcje"] != ["blok"]:
            raise BladDanych("%s: akcja bloku" % gid)
    elif typ == "rytm":
        if len(G["kierunki"]) != 2 or sorted(G["akcje"]) != sorted(G["kierunki"]):
            raise BladDanych("%s: rytm ma dwie stopy (akcje = kierunki)" % gid)
        if not (_w(G["podbieg"]["kroki"], 2, 8) and _w(G["podbieg"]["mnoznik"], 0.5, 1)):
            raise BladDanych("%s: podbieg" % gid)
        for p in poz:
            if not _w(p["podbiegi"], 0, 0.3):
                raise BladDanych("%s: podbiegi %s" % (gid, p["podbiegi"]))
    elif typ == "unik":
        o = G["odpowiedz"]
        if sorted(o) != sorted(G["wartosci"]) or sorted(o.values()) != sorted(G["akcje"]):
            raise BladDanych("%s: odpowiedz ma łączyć każdą wartość z inną akcją" % gid)
        if not _w(G["wyprzedzenie_s"], 0, 0.4):
            raise BladDanych("%s: wyprzedzenie_s" % gid)
        for p in poz:
            if not (1 <= p["wartosci"] <= len(G["wartosci"])) or not _w(p["zmiany"], 0, 0.5):
                raise BladDanych("%s: wartosci / zmiany" % gid)
    elif typ == "sekwencja":
        if sorted(G["runy"]) != sorted(G["akcje"]) or len(G["runy"]) < 2:
            raise BladDanych("%s: runy = akcje" % gid)
        if not (2 <= G["min_dlugosc"] <= G["start_dlugosc"] <= G["maks_dlugosc"] <= 12) or not _w(G["kara"], 1, 6):
            raise BladDanych("%s: długości sekwencji (2 ≤ min ≤ start ≤ maks ≤ 12) albo kara" % gid)
        if G["baza"] < 4 * G["maks_dlugosc"]:
            raise BladDanych("%s: baza run za krótka" % gid)
        for k in ("przerwa_s", "przerwa_bledu_s", "bezczynnosc_s"):
            if not _w(G[k], 0.05, 20):
                raise BladDanych("%s: %s" % (gid, k))
        for p in poz:
            if not (_w(p["pokaz_s"], 0.15, 2) and _w(p["przerwa_s"], 0.05, 1)):
                raise BladDanych("%s: pokaz_s / przerwa_s" % gid)
    elif typ == "lapanie":
        if G["tory"] != G["akcje"] or len(G["tory"]) != 3 or G["start_tor"] not in G["tory"]:
            raise BladDanych("%s: trzy tory = akcje, tor startowy z listy" % gid)
        if not (_w(G["lot_s"], 0.3, 4) and G["pierwsze_s"] >= G["lot_s"] and _w(G["zlota_mnoznik"], 1, 4)):
            raise BladDanych("%s: lot_s / pierwsze_s / zlota_mnoznik" % gid)
        if not _w(G["zlapanie_s"], 0, 0.5):
            raise BladDanych("%s: zlapanie_s (koszyk pod koniczyną przed upadkiem) poza 0–0,5 s" % gid)
        for p in poz:
            if p["odstep_s"] * (1 - G["rozrzut"]) < 0.6:
                raise BladDanych("%s: odstęp %s — upadki za gęsto" % (gid, p["odstep_s"]))
            if not (_w(p["kamienie"], 0, 0.5) and _w(p["zlote"], 0, 0.5) and _w(p["wiatr"], 0, 0.5)):
                raise BladDanych("%s: kamienie / zlote / wiatr" % gid)


def zdarzenia_dzwieku():
    """Zdarzenia arkusza efektów z pakietu swiat/dzwiek_gra (tylko odczyt)."""
    return set(_czytaj_json(DZWIEK_GRA)["zdarzenia"])


def _sprawdz(K):
    """Reguły ustawień → BladDanych z opisem."""
    st = K["statystyki"]
    ids = [s["id"] for s in st]
    if len(ids) != 6 or len(set(ids)) != 6:
        raise BladDanych("statystyk ma być sześć, bez powtórzeń: %s" % ids)
    for s in st:
        if s["stan"] not in ("grywalna", "w_projekcie"):
            raise BladDanych("zły stan %s: %s" % (s["id"], s["stan"]))
        if (s["stan"] == "grywalna") != (s["id"] in K["gry"]):
            raise BladDanych("%s: stan „grywalna” wymaga wpisu w gry (i odwrotnie)" % s["id"])
        if s["stan"] == "grywalna" and s["id"] not in K["stanowiska"]:
            raise BladDanych("%s: brak stanowiska" % s["id"])
        if not re.fullmatch(r"[0-9A-F]{6}", s["kolor"]):
            raise BladDanych("%s: kolor %s" % (s["id"], s["kolor"]))
    for gid, G in K["gry"].items():
        _sprawdz_gre(K, gid, G)
    P = K["przyrost"]
    if len(P["za_trafienie"]) != len(P["progi_serii"]) + 1:
        raise BladDanych("przyrost: za_trafienie ma mieć o jeden wpis więcej niż progi_serii")
    if P["progi_serii"] != sorted(set(P["progi_serii"])) or P["za_trafienie"] != sorted(P["za_trafienie"]):
        raise BladDanych("przyrost: progi i przyrosty mają rosnąć")
    if any((not isinstance(x, int)) or x < 1 for x in P["za_trafienie"]):
        raise BladDanych("przyrost: jednostki za trafienie — liczby całkowite ≥ 1")
    if not P["mnoznik_centrum"] >= 1 or not P["prog_paska"] > 0 or not P["polowa_udzialu"] > 0:
        raise BladDanych("przyrost: mnoznik_centrum ≥ 1, prog_paska > 0, polowa_udzialu > 0")
    if not P["pula_baza"] > 0 or P["pula_na_poziom"] < 0 or not isinstance(P["malejacy_zysk"], bool):
        raise BladDanych("przyrost: pula_baza > 0, pula_na_poziom ≥ 0, malejacy_zysk true/false")
    O = K["ochrona"]
    for k in ("pojemnosc", "uzupelnianie_na_s", "max_opoznienie_s", "przypisanie_s", "odstep_wejsc_s",
              "odstep_startu_s", "zasieg_wejscia", "wiadomosci_pojemnosc", "wiadomosci_na_s", "tik_s"):
        if not O[k] > 0:
            raise BladDanych("ochrona.%s ma być > 0" % k)
    if O["pojemnosc"] < 1:
        raise BladDanych("ochrona.pojemnosc < 1")
    U = K["ui"]
    if U["przycisk_maly_px"] * U["skala_min"] < U["wymog_przycisk_px"]:
        raise BladDanych("ui: najmniejszy przycisk przy skali minimalnej < %d px" % U["wymog_przycisk_px"])
    if min(U["tekst_px"].values()) * U["skala_min"] < U["wymog_tekst_pt"]:
        raise BladDanych("ui: najmniejszy tekst przy skali minimalnej < %d pt" % U["wymog_tekst_pt"])
    for n, d in K["dzwieki"].items():
        if isinstance(d, dict) and d["plik"] not in DZWIEKI_WBUDOWANE:
            raise BladDanych("dźwięk %s: %s nie jest wbudowany w klienta Roblox" % (n, d["plik"]))
    for n, s in K["sterowanie"].items():
        klawisze = s if isinstance(s, list) else s["klawisze"] + s["pad"]
        for k in klawisze:
            if k not in KLAWISZE:
                raise BladDanych("sterowanie %s: nieznany klawisz %s" % (n, k))
    DK = K["dzwieki_katalog"]
    znane = zdarzenia_dzwieku()
    wpisy = list(DK["trafienie"].values()) + [DK[k] for k in ("punkt", "koniec", "zlota", "zaklecie", "przycisk")]
    for z in wpisy:
        if z not in znane:
            raise BladDanych("dzwieki_katalog: zdarzenia %s nie ma w arkuszu swiat/dzwiek_gra" % z)
    for g in DK["trafienie"]:
        if g not in K["gry"]:
            raise BladDanych("dzwieki_katalog: nieznana gra %s" % g)
    _sprawdz_wyglad(K)
    _sprawdz_scenerie(K)


KRAINY = ("las", "bagno", "dzungla")


def _sprawdz_scenerie(K):
    """Scenerie krain (D-108): każda gra ma scenerię, po dwie na krainę, podesty w środkach komórek pasa, punkt trenera
    w każdej scenerii → BladDanych."""
    A, SC = K["arena"], K["scenerie"]
    kol = SC["kolejnosc"]
    if sorted(kol) != sorted(K["gry"]):
        raise BladDanych("scenerie.kolejnosc: każda gra dokładnie raz")
    for g in kol:
        if SC.get(g, {}).get("kraina") not in KRAINY or not SC[g].get("nazwa"):
            raise BladDanych("scenerie.%s: kraina (%s) i nazwa" % (g, ", ".join(KRAINY)))
    for kr in KRAINY:
        if len([g for g in kol if SC[g]["kraina"] == kr]) != 2:
            raise BladDanych("scenerie: po dwie gry na krainę (%s)" % kr)
    km = A["komorka"]
    if not (_w(km, 48, 120) and _w(A["polnoc"], -80, -30) and _w(A["poludnie"], 20, 60) and _w(A["woda_y"], -4, -0.5)):
        raise BladDanych("arena: komorka 48–120, polnoc −80…−30, poludnie 20–60, woda_y −4…−0,5")
    z0 = None
    for i, g in enumerate(kol):
        pd = K["stanowiska"][g]["podest"]
        if abs(pd[0] - (i - (len(kol) - 1) / 2.0) * km) > 1e-6 or pd[1] != 0:
            raise BladDanych("%s: podest ma stać w środku swojej komórki pasa (x = %g)" % (g, (i - (len(kol) - 1) / 2.0) * km))
        z0 = pd[2] if z0 is None else z0
        if pd[2] != z0:
            raise BladDanych("%s: podesty w jednej linii (z = %g)" % (g, z0))
        T = K["stanowiska"][g].get("trener_npc")
        if T is None and "golem" in K["stanowiska"][g]:
            continue  # Pancerz: golem gry jest przeciwnikiem i trenerem naraz — osobnego punktu trenera nie ma
        if not (isinstance(T, dict) and _punkt(T.get("miejsce")) and _w(T.get("obrot_y"), -180, 180)
                and isinstance(T.get("figura"), str) and re.fullmatch(r"Arena/\w+/\w+", T["figura"])):
            raise BladDanych("%s: trener_npc — miejsce [x, y, z], obrot_y w stopniach, figura (ścieżka)" % g)
        if max(abs(T["miejsce"][0]), abs(T["miejsce"][2])) > km / 2.0 - 6:
            raise BladDanych("%s: trener_npc poza polaną scenerii" % g)
    if len(kol) * km + 16 > A["rozmiar"][0] or z0 + A["poludnie"] > A["rozmiar"][1] / 2.0 or z0 + A["polnoc"] < -A["rozmiar"][1] / 2.0:
        raise BladDanych("arena.rozmiar nie mieści pasa scenerii")
    for g, klucz in (("sila", "miotacz"), ("inteligencja", "mag"), ("szczescie", "ogrodnik"), ("kondycja", "trener"),
                     ("zrecznosc", "trener")):
        if K["stanowiska"][g]["trener_npc"]["miejsce"] != K["stanowiska"][g][klucz]:
            raise BladDanych("%s: trener_npc.miejsce = miejsce dzisiejszej figury (%s)" % (g, klucz))


# nazwy wybuchów z modułu efektów walki (swiat/test_walki2/zrodla/Efekty3D.luau, tylko odczyt) — ui.efekty może
# wskazywać tylko je; własny moduł EfektyTreningu ma te same (pilnuje tego test 6j)
EFEKTY_WALKI = os.path.join(REPO, "swiat", "test_walki2", "zrodla", "Efekty3D.luau")


def wybuchy_walki():
    with open(EFEKTY_WALKI, encoding="utf-8") as f:
        return set(re.findall(r"^Wybuch\.(\w+)\s*=", f.read(), re.M))


def komiks_pokrywa(K, tekst):
    """Czy czcionka komiksowa ma wszystkie litery napisu (ASCII drukowalne + ui.komiks.znaki)."""
    znaki = K["ui"]["komiks"]["znaki"]
    return all(32 <= ord(z) <= 126 or z in znaki for z in tekst)


def napisy_komiksowe(K):
    """Wszystkie napisy, które klient rysuje komiksową czcionką (wyskakujące słowa, tytuł karty podsumowania)."""
    T = K["teksty"]
    lista = []
    for k in ("trafienia", "trafienia_blok", "trafienia_rytm", "trafienia_unik", "trafienia_runy", "trafienia_lapanie"):
        lista += T[k]
    lista += list(T["pudlo"].values())
    for d in T["pudla_gier"].values():
        lista += list(d.values())
    lista += [T[k] for k in ("zmylka_ok", "patrz", "twoja_kolej", "zaklecie", "nowe_zaklecie", "zlota", "podbieg", "koniec",
                             "przerwana", "bez_pudla")]
    lista += [T["seria"] % n for n in K["przyrost"]["progi_serii"]]
    lista += [T["punkt"] % (9, s["nazwa"]) for s in K["statystyki"]]
    lista += [K["sterowanie"]["start"]["napis"] + "!"] + [str(n) for n in range(1, int(K["runda"]["odliczanie_s"]) + 2)]
    return lista


def _sprawdz_wyglad(K):
    """Kamery w stylu walki, komiksowe napisy, efekty i haczyk bohatera → BladDanych."""
    U = K["ui"]
    KA = U["kamera"]
    if not (20 <= KA["kat_min"] < KA["kat_max"] <= 70):
        raise BladDanych("ui.kamera: kat_min / kat_max")
    for k in ("uderzenie", "mocne", "seria"):
        if not (_w(KA[k]["kat"], 0, 6) and _w(KA[k]["czas_s"], 0.05, 1.5)):
            raise BladDanych("ui.kamera.%s: kat 0–6°, czas_s 0,05–1,5" % k)
    if not (KA["uderzenie"]["kat"] <= KA["mocne"]["kat"] <= KA["seria"]["kat"]):
        raise BladDanych("ui.kamera: zawężenie kąta ma rosnąć: uderzenie ≤ mocne ≤ seria")
    if not (_w(KA["odliczanie_koniec_s"], 0, K["runda"]["odliczanie_s"] - 0.5) and _w(KA["wstrzas_zanik"], 1, 40)):
        raise BladDanych("ui.kamera: odliczanie_koniec_s / wstrzas_zanik")
    for gid, st in K["stanowiska"].items():
        kam = st["kamera"]
        for nazwa, u in (("kamera", kam), ("kamera.start", kam.get("start") or {})):
            if not (_punkt(u.get("oko")) and _punkt(u.get("cel")) and _w(u.get("kat"), KA["kat_min"], KA["kat_max"])):
                raise BladDanych("%s: %s — oko, cel i kat w %s–%s°" % (gid, nazwa, KA["kat_min"], KA["kat_max"]))
            if sum((u["oko"][i] - u["cel"][i]) ** 2 for i in range(3)) < 9:
                raise BladDanych("%s: %s — oko za blisko celu" % (gid, nazwa))
        f = kam.get("final") or {}
        if not (_w(f.get("azymut"), -80, 80) and _w(f.get("dystans"), 6, 20) and _w(f.get("wysokosc"), 0.5, 8)
                and _w(f.get("cel_wysokosc"), 1, 6) and _w(f.get("kat"), 30, KA["kat_max"])):
            raise BladDanych("%s: kamera.final (azymut, dystans, wysokosc, cel_wysokosc, kat)" % gid)
        n = st.get("napis")
        if not (isinstance(n, list) and len(n) == 2 and all(_w(x, 0.05, 0.95) for x in n)):
            raise BladDanych("%s: napis — miejsce dużych napisów jako ułamki obszaru GUI [x, y]" % gid)
    KO = U["komiks"]
    if KO["czcionka"] != "Bangers" or KO["czcionka_naglowka"] not in ("LuckiestGuy", "Bangers"):
        raise BladDanych("ui.komiks: czcionki wbudowane walki (Bangers, LuckiestGuy)")
    if min(KO["rozmiary_px"].values()) * U["skala_min"] < U["wymog_tekst_pt"]:
        raise BladDanych("ui.komiks: najmniejszy napis przy skali minimalnej < %d pt" % U["wymog_tekst_pt"])
    for n in ("trafienie", "mocne", "pudlo", "seria", "punkt", "licznik", "start", "info", "zloto"):
        if n not in KO["style"]:
            raise BladDanych("ui.komiks.style: brak stylu %s" % n)
    for n, st in KO["style"].items():
        if st["kolor"] not in KO["kolory"] or st["rozmiar"] not in KO["rozmiary_px"] or not _w(st["zycie_s"], 0.2, 3):
            raise BladDanych("ui.komiks.style.%s: kolor / rozmiar / zycie_s" % n)
    if sorted(KO["kolor_trafienia"]) != sorted(K["gry"]) or any(v not in KO["kolory"] for v in KO["kolor_trafienia"].values()):
        raise BladDanych("ui.komiks.kolor_trafienia: po jednym kolorze z ui.komiks.kolory na grę")
    for h in list(KO["kolory"].values()) + KO["gwiazda"]["kolory"] + U["efekty"]["konfetti"]["kolory"]:
        if not re.fullmatch(r"[0-9A-F]{6}", h):
            raise BladDanych("ui.komiks / ui.efekty: kolor %s" % h)
    if not (_w(KO["obrot_max"], 0, 15) and _w(KO["nadmiar"], 1, 1.3) and _w(KO["zanik_od"], 0.3, 0.95)
            and _w(KO["mocne_co"], 2, 20) and _w(KO["naraz"], 2, 12)):
        raise BladDanych("ui.komiks: obrot_max / nadmiar / zanik_od / mocne_co / naraz")
    E = U["efekty"]
    znane = wybuchy_walki()
    wpisy = list(E["trafienie"].values()) + [E[k] for k in ("mocne", "kamien", "oberwanie", "zaklecie")]
    for z in wpisy:
        if z not in znane:
            raise BladDanych("ui.efekty: wybuchu %s nie ma w module efektów walki" % z)
    if sorted(E["trafienie"]) != sorted(K["gry"]):
        raise BladDanych("ui.efekty.trafienie: po jednym wybuchu na grę")
    KF = E["konfetti"]
    if not (1 <= KF["zwykle"]["ile"] < KF["wielkie"]["ile"] <= 160 and 1 <= KF["zwykle"]["salwy"] <= KF["wielkie"]["salwy"] <= 6
            and _w(KF["zycie_s"], 1, 6) and _w(KF["predkosc"], 5, 60) and _w(KF["grawitacja"], 1, 60) and _w(KF["opor"], 0, 6)
            and _w(KF["rozrzut"], 0.5, 10) and _punkt(KF["rozmiar"])):
        raise BladDanych("ui.efekty.konfetti: zwykłe mniejsze od wielkiego, najwyżej 160 kawałków, 1–6 salw, życie 1–6 s, "
                         "prędkość 5–60, grawitacja 1–60, opór 0–6, rozrzut 0,5–10, rozmiar [x, y, z]")
    B = U["bohater"]
    if sorted(B["klipy"]) != ["bieg", "padnij", "radosc", "rece", "skok"] or not re.fullmatch(r"[\w/]+", B["sciezka"]):
        raise BladDanych("ui.bohater: klipy (bieg, skok, padnij, rece, radosc) i sciezka")
    # żaden napis wyskakujący nie może dostać zastępczej czcionki (FredokaOne nie miała ę, ż, ś — README 17.11)
    for tekst in napisy_komiksowe(K):
        if not komiks_pokrywa(K, tekst):
            raise BladDanych("napis „%s” ma literę spoza ui.komiks.znaki — dopisz ją po sprawdzeniu czcionki albo zmień napis"
                             % tekst)


def _swiat(K):
    """Położenia w świecie: środek areny + układ lokalny (Y w górę, gracz na stanowisku patrzy na −Z)."""
    c = K["arena"]["srodek"]
    S = {}
    for gid, st in K["stanowiska"].items():
        p = _dodaj(c, st["podest"])
        kam = st["kamera"]
        # kamera gry (oko, cel, kąt widzenia), ujęcie początku odliczania (start → dojazd do kamery gry) i parametry
        # zbliżenia na postać po rundzie (final: względem postaci, liczy klient); napis = miejsce dużych napisów
        w = {"podest": p, "patrz": _dodaj(p, st.get("patrz", [0, 0, -10])),
             "oko": _dodaj(p, kam["oko"]), "cel": _dodaj(p, kam["cel"]), "kat": kam["kat"],
             "start": {"oko": _dodaj(p, kam["start"]["oko"]), "cel": _dodaj(p, kam["start"]["cel"]), "kat": kam["start"]["kat"]},
             "final": kam["final"], "napis": st["napis"]}
        # punkt trenera dla postaci NPC (D-108/D-109): miejsce w świecie, obrót wokół Y (0 = twarzą na +z), punkt, na
        # który patrzy, i ścieżka dzisiejszej figury z klocków do podmiany; Pancerz punktu nie ma (trenerem jest golem)
        T = st.get("trener_npc")
        if T:
            m = _dodaj(p, T["miejsce"])
            a = math.radians(T["obrot_y"])
            w["trener_npc"] = {"miejsce": m, "obrot_y": T["obrot_y"], "patrz": _dodaj(m, [10 * math.sin(a), 0, 10 * math.cos(a)]),
                               "figura": T["figura"]}
        if gid == "sila":
            w["miotacz"] = _dodaj(p, st["miotacz"])
            w["reka"] = _dodaj(w["miotacz"], st["reka"])
            w["strefy"] = {k: _dodaj(p, v) for k, v in st["strefy"].items()}
            w["luki"] = st["luki"]
            w["miecz"] = _dodaj(p, st["miecz"])
        elif gid == "pancerz":
            g = _dodaj(p, st["golem"])
            w["golem"] = g
            for k in ("piesc_spoczynek", "piesc_zamach"):
                w[k] = _dodaj(g, st[k])
            for k in ("piesc_cel", "tarcza", "tarcza_blok"):
                w[k] = _dodaj(p, st[k])
        else:
            # nowe stanowiska: każdy punkt [x, y, z] (i słownik punktów) względem podestu → świat; liczby, słowniki
            # liczb i klucze *_rozmiar bez zmian
            for k, v in st.items():
                if k in ("podest", "kamera", "patrz", "napis", "trener_npc"):
                    continue
                if _punkt(v) and not k.endswith("_rozmiar"):
                    w[k] = _dodaj(p, v)
                elif isinstance(v, dict) and v and all(_punkt(x) for x in v.values()):
                    w[k] = {a: _dodaj(p, x) for a, x in v.items()}
                else:
                    w[k] = v
        S[gid] = w
    return S


def _punkt(v):
    return isinstance(v, list) and len(v) == 3 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)


def _bez_opisow(v):
    """Kopia bez pól „opis” (objaśnienia dla ludzi w ustawienia.json nie idą do gry)."""
    if isinstance(v, dict):
        return {k: _bez_opisow(x) for k, x in v.items() if k != "opis"}
    if isinstance(v, list):
        return [_bez_opisow(x) for x in v]
    return v


def _trener():
    """Punkt podpowiedzi E trenera w bazarze (znaczniki.json) i nazwa zdarzenia okien z pakietu bazaru."""
    z = _czytaj_json(ZNACZNIKI)["training_center"]
    m = _czytaj_json(MIEJSCA_BAZARU)
    ids = [x.get("id") for x in m["miejsca"]]
    return z, m, ids


def wczytaj():
    K = _czytaj_json(USTAWIENIA)
    _sprawdz(K)
    z, m, ids = _trener()
    if K["id_miejsca_bazaru"] not in ids:
        raise BladDanych("w miejsca.json bazaru nie ma miejsca %s" % K["id_miejsca_bazaru"])
    if [s["id"] for s in K["statystyki"]] != z["statystyki"]:
        raise BladDanych("kolejność statystyk ≠ znaczniki.json bazaru (%s)" % z["statystyki"])
    D = {
        "wersja": 1,
        "kontener": K["kontener"],
        "prefiks": K["prefiks"],
        "zdarzenie_okien": K["zdarzenie_okien"],
        "id_miejsca_bazaru": K["id_miejsca_bazaru"],
        "bazar": {"kontener": K["bazar"]["kontener"], "podpowiedz": K["bazar"]["podpowiedz"],
                  "punkt_zapasowy": z["podpowiedz"],
                  # 26.11.2026: false = E przy trenerze otwiera okno stanowisk AFK, nie tymczasowy wybór mini-gry
                  "wybor_od_trenera": K["bazar"].get("wybor_od_trenera", True) is not False},
        "arena": K["arena"],
        "scenerie": {g: {"kraina": K["scenerie"][g]["kraina"], "nazwa": K["scenerie"][g]["nazwa"]} for g in K["scenerie"]["kolejnosc"]},
        "kolejnosc_scenerii": K["scenerie"]["kolejnosc"],
        "statystyki": K["statystyki"],
        "runda": K["runda"],
        "przyrost": K["przyrost"],
        "ochrona": K["ochrona"],
        "gry": K["gry"],
        "swiat": _swiat(K),
        "podpowiedz": K["podpowiedz"],
        "ui": _bez_opisow(K["ui"]),
        "sterowanie": K["sterowanie"],
        "dzwieki": K["dzwieki"],
        "dzwieki_katalog": {k: v for k, v in K["dzwieki_katalog"].items() if k != "opis"},
        "teksty": K["teksty"],
        "nazwy": NAZWY,
        "tablica_wejscia": K["tablica_wejscia"],
    }
    return K, D


# ------------------------------------------------------------------------------------------------ przypadki wzorcowe
def _sekwencja(D, gra, z, t0, rnd, ile=16):
    """Kroki próby: trafienia, pudła, spam, złe wartości, czasy spoza zakresu, przeterminowanie i koniec rundy."""
    O = D["ochrona"]
    G = D["gry"][gra]
    pl = LT.plan(D, gra, z)
    kroki = []
    teraz = t0
    for e in pl[:ile]:
        cel = t0 + e["t"]
        rodzaj = rnd.choice(["traf", "traf", "traf", "brzeg", "zle", "wczesnie", "pozno", "pomin", "spam", "zla",
                             "przyszlosc", "stary", "podwojne"])
        if rodzaj == "pomin":
            teraz = max(teraz, cel + e["okno"] + O["max_opoznienie_s"] + 0.05)
            kroki.append({"typ": "p", "teraz": round(teraz, 3)})
            continue
        if rodzaj == "traf":
            tk = cel + round(rnd.uniform(-0.8, 0.8) * e["okno"], 3)
        elif rodzaj == "brzeg":
            tk = cel + e["okno"]
        elif rodzaj == "wczesnie":
            tk = cel - e["okno"] - 0.1
        elif rodzaj == "pozno":
            tk = cel + e["okno"] + 0.08
        else:
            tk = cel + round(rnd.uniform(-0.5, 0.5) * e["okno"], 3)
        przybycie = round(max(teraz, tk + rnd.uniform(0.02, 0.2)), 3)
        teraz = przybycie
        if G["typ"] == "blok":
            dobra, zla = "blok", "blok"
        else:
            dobra = LT.odpowiedz(G, e["wartosc"])
            zla = [k for k in G["akcje"] if k != dobra][rnd.randrange(len(G["akcje"]) - 1)]
        w = zla if rodzaj == "zle" else dobra
        if rodzaj == "zla":
            kroki.append({"typ": "z", "w": "miecz", "tk": round(tk, 3), "teraz": teraz})
        elif rodzaj == "przyszlosc":
            kroki.append({"typ": "z", "w": w, "tk": round(teraz + 5, 3), "teraz": teraz})
        elif rodzaj == "stary":
            kroki.append({"typ": "z", "w": w, "tk": round(teraz - 3, 3), "teraz": teraz})
        elif rodzaj == "spam":
            for _ in range(7):
                kroki.append({"typ": "z", "w": w, "tk": round(tk, 3), "teraz": teraz})
        elif rodzaj == "podwojne":
            kroki.append({"typ": "z", "w": w, "tk": round(tk, 3), "teraz": teraz})
            kroki.append({"typ": "z", "w": w, "tk": round(tk + 0.05, 3), "teraz": round(teraz + 0.05, 3)})
            teraz = round(teraz + 0.05, 3)
        else:
            kroki.append({"typ": "z", "w": w, "tk": round(tk, 3), "teraz": teraz})
        if rnd.random() < 0.3:
            kroki.append({"typ": "p", "teraz": teraz})
    kroki.append({"typ": "p", "teraz": round(t0 + D["runda"]["dlugosc_s"] + 1, 3)})
    kroki.append({"typ": "z", "w": G["akcje"][0], "tk": round(t0 + D["runda"]["dlugosc_s"] + 1, 3),
                  "teraz": round(t0 + D["runda"]["dlugosc_s"] + 1, 3)})
    return kroki


def _sekwencja_runy(D, gra, z, t0, rnd, ile=26):
    """Kroki Run: trafienia po pokazie, zła runa, naciśnięcie w czasie pokazu, dubel, spam, zła wartość, czasy spoza
    zakresu i bezczynność (ponowny pokaz). Stan pomocniczy liczy ta sama logika (te same wywołania co przy odtworzeniu)."""
    G = D["gry"][gra]
    R = LT.nowa_runda(D, gra, 1, t0, LT.plan(D, gra, z))
    kroki = []

    def z_(w, tk, tn):
        k = {"typ": "z", "w": w, "tk": round(tk, 3), "teraz": round(tn, 3)}
        kroki.append(k)
        LT.zgloszenie(D, R, k["w"], k["tk"], k["teraz"])

    def p_(tn):
        k = {"typ": "p", "teraz": round(tn, 3)}
        kroki.append(k)
        LT.przeterminowane(D, R, k["teraz"])

    teraz = t0
    for _ in range(ile):
        if R["koniec"] or teraz - t0 > D["runda"]["dlugosc_s"] - 2:
            break
        rodzaj = rnd.choice(["traf"] * 6 + ["zle", "pokaz", "dubel", "spam", "zla", "przyszlosc", "stary", "czekaj"])
        if rodzaj == "pokaz":
            teraz = max(teraz, t0 + R["pokazOd"] + 0.05)
            z_(rnd.choice(G["akcje"]), teraz, teraz)
            teraz += rnd.uniform(0.1, 0.3)
            continue
        if teraz < t0 + R["pokazDo"]:
            teraz = t0 + R["pokazDo"] + rnd.uniform(0.05, 0.6)
        i = R["offset"] + R["poz"]
        dobra = R["plan"][i]["wartosc"]
        zla = [k for k in G["akcje"] if k != dobra][rnd.randrange(len(G["akcje"]) - 1)]
        if rodzaj == "traf":
            z_(dobra, teraz - rnd.uniform(0, 0.2), teraz)
        elif rodzaj == "zle":
            z_(zla, teraz, teraz)
        elif rodzaj == "dubel":
            z_(dobra, teraz, teraz)
            z_(dobra, teraz + 0.05, teraz + 0.05)
        elif rodzaj == "spam":
            for _ in range(9):
                z_(dobra, teraz, teraz)
        elif rodzaj == "zla":
            z_("miecz", teraz, teraz)
        elif rodzaj == "przyszlosc":
            z_(dobra, teraz + 5, teraz)
        elif rodzaj == "stary":
            z_(dobra, teraz - 3, teraz)
        else:  # czekaj: bezczynność → ten sam pokaz od początku
            teraz += G["bezczynnosc_s"] + rnd.uniform(0.2, 1.0)
            p_(teraz)
        teraz += rnd.uniform(0.15, 0.5)
    koniec = t0 + D["runda"]["dlugosc_s"] + 1
    p_(koniec)
    kroki.append({"typ": "z", "w": G["akcje"][0], "tk": round(koniec, 3), "teraz": round(koniec, 3)})
    return kroki


def _sekwencja_lapania(D, gra, z, t0, rnd, ile=16):
    """Kroki Koniczyn: ruchy koszyka (do koniczyny, z dala od kamienia, w złą stronę), spam, zła wartość, czasy spoza
    zakresu, upadki rozstrzygane z zapasem serwera albo od razu (zapas 0, jak u klienta)."""
    G = D["gry"][gra]
    R = LT.nowa_runda(D, gra, 1, t0, LT.plan(D, gra, z))
    kroki = []

    def z_(w, tk, tn):
        k = {"typ": "z", "w": w, "tk": round(tk, 3), "teraz": round(tn, 3)}
        kroki.append(k)
        LT.zgloszenie(D, R, k["w"], k["tk"], k["teraz"])

    teraz = t0
    for e in R["plan"][:ile]:
        start = t0 + e["t"] - G["lot_s"]
        teraz = max(teraz, start + rnd.uniform(0.05, 0.9))
        k, _ = LT.tory_zdarzenia(D, copy.deepcopy(R), e)
        b = LT.tor_w(D, R, teraz - t0)
        rodzaj = rnd.choice(["traf"] * 5 + ["zle", "spam", "zla", "przyszlosc", "stary", "nic"])
        if e["wartosc"] == "kamien":
            cel = [i for i in (1, 2, 3) if i != k][rnd.randrange(2)] if rodzaj == "traf" else k
        else:
            cel = k if rodzaj in ("traf", "spam", "przyszlosc") else [i for i in (1, 2, 3) if i != k][rnd.randrange(2)]
        nazwa = G["tory"][cel - 1]
        if rodzaj == "nic":
            pass
        elif rodzaj == "spam":
            for _ in range(9):
                z_(nazwa, teraz, teraz)
        elif rodzaj == "zla":
            z_("gora", teraz, teraz)
        elif rodzaj == "przyszlosc":
            z_(nazwa, teraz + 5, teraz)
        elif rodzaj == "stary":
            z_(nazwa, teraz - 3, teraz)
        elif cel != b or rnd.random() < 0.3:
            z_(nazwa, teraz - rnd.uniform(0, 0.3), teraz)
        teraz += rnd.uniform(0.05, 0.3)
        if rnd.random() < 0.5:
            kroki.append({"typ": "p", "teraz": round(t0 + e["t"] + rnd.choice([0.01, 0.2, 0.4]), 3),
                          "zapas": rnd.choice([None, 0])})
            LT.przeterminowane(D, R, kroki[-1]["teraz"], kroki[-1]["zapas"])
            teraz = max(teraz, kroki[-1]["teraz"])
    koniec = t0 + D["runda"]["dlugosc_s"] + 1
    kroki.append({"typ": "p", "teraz": round(koniec, 3)})
    kroki.append({"typ": "z", "w": G["akcje"][0], "tk": round(koniec, 3), "teraz": round(koniec, 3)})
    return kroki


def sekwencja_krokow(D, gra, z, t0, rnd, ile=None):
    typ = D["gry"][gra]["typ"]
    if typ == "sekwencja":
        return _sekwencja_runy(D, gra, z, t0, rnd, ile or 26)
    if typ == "lapanie":
        return _sekwencja_lapania(D, gra, z, t0, rnd, ile or 16)
    return _sekwencja(D, gra, z, t0, rnd, ile or 16)


def przypadki(D):
    rnd = random.Random(17112026)
    P = {"plany": [], "sekwencje": [], "przyrosty": [], "wejscia": [], "skale": []}
    for gra in sorted(D["gry"]):
        for z in (1, 7, 12345, 99999, 2147483000, 31337):
            pl = LT.plan(D, gra, z)
            P["plany"].append({"gra": gra, "ziarno": z, "n": len(pl), "suma_t": round(sum(e.get("t", 0) for e in pl), 6),
                               "pierwsze": [[e.get("t", 0), e["wartosc"]] for e in pl[:6]]})
        for _ in range(6):
            z = rnd.randrange(1, 2 ** 31 - 2)
            t0 = round(rnd.uniform(10, 5000), 3)
            kroki = sekwencja_krokow(D, gra, z, t0, rnd)
            s0 = {"pasek": round(rnd.uniform(0, 30), 3), "W": rnd.randrange(0, 40), "pula": LT.pula(D, rnd.randrange(1, 66))}
            kod, R = LT.wykonaj_kroki(D, gra, z, t0, kroki, s0)
            P["sekwencje"].append({"gra": gra, "ziarno": z, "t0": t0, "kroki": kroki, "s0": s0, "wynik": {
                "kod": kod, "trafienia": R["trafienia"], "pudla": R["pudla"], "puste": R["puste"], "spam": R["spam"],
                "najdluzsza": R["najdluzsza"], "suma": R["suma"], "koniec": R["koniec"], "jednostki": R["jednostki"],
                "W": R["W"], "pasek": round(R["pasek"], 9)}})
    for seria in range(0, 26):
        P["przyrosty"].append([seria, LT.przyrost(D, seria)])
    O = D["ochrona"]
    zas = O["zasieg_wejscia"]
    for gra, ost, runda, teraz, odl, wa in [
        ("sila", LT.NIGDY, False, 100.0, 5.0, False), ("pancerz", LT.NIGDY, False, 100.0, zas, False),
        ("sila", LT.NIGDY, False, 100.0, zas + 0.01, False), ("sila", LT.NIGDY, False, 100.0, None, False),
        ("sila", LT.NIGDY, False, 100.0, None, True), ("sila", 99.0, False, 100.0, 1.0, False),
        ("sila", 100.0 - O["odstep_wejsc_s"], False, 100.0, 1.0, False), ("kondycja", LT.NIGDY, False, 100.0, 1.0, False),
        ("szczescie", LT.NIGDY, False, 100.0, 1.0, True), ("nic", LT.NIGDY, False, 100.0, 1.0, False),
        ("pancerz", LT.NIGDY, True, 100.0, 1.0, True), ("pancerz", LT.NIGDY, True, 100.0, 1.0, False)]:
        S = LT.nowy_gracz()
        S["ostatnieWejscie"] = ost
        if runda:
            S["runda"] = {"koniec": False}
        w = LT.wejscie(D, gra, S, teraz, odl, wa)
        c = {"gra": gra, "ostatnie": ost, "runda": runda, "teraz": teraz, "wArenie": wa, "ok": w["ok"], "powod": w["powod"]}
        if odl is not None:
            c["odl"] = odl
        P["wejscia"].append(c)
    for w, h in [(667, 375), (568, 320), (812, 375), (1280, 720), (1920, 1080), (2560, 1440), (480, 270), (1024, 768)]:
        P["skale"].append([w, h, LT.skala_ui(D, w, h)])
    return P


def dane_z_przypadkami():
    K, D = wczytaj()
    D = copy.deepcopy(D)
    D["przypadki"] = przypadki(D)
    D["skrot"] = hashlib.sha1(json.dumps(D, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]
    return K, D


# ------------------------------------------------------------------------------------------------ zapis Luau
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SLOWA = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in", "local", "nil",
          "not", "or", "repeat", "return", "then", "true", "until", "while", "continue"}


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
    if isinstance(v, list):
        czesci = [_luau(x, wciecie + 1) for x in v]
        jedna = "{ " + ", ".join(czesci) + " }" if czesci else "{}"
        if len(jedna) <= 110 and "\n" not in jedna:
            return jedna
        return "{\n" + "".join(tab + c + ",\n" for c in czesci) + "\t" * (wciecie - 1) + "}"
    if isinstance(v, dict):
        czesci = ["%s = %s" % (_klucz(k), _luau(x, wciecie + 1)) for k, x in v.items() if x is not None]
        jedna = "{ " + ", ".join(czesci) + " }" if czesci else "{}"
        if len(jedna) <= 110 and "\n" not in jedna:
            return jedna
        return "{\n" + "".join(tab + c + ",\n" for c in czesci) + "\t" * (wciecie - 1) + "}"
    raise TypeError(repr(v))


def luau_tekst(D):
    naglowek = ("--[[\n\tDaneTreningu — WYGENEROWANE przez swiat/trening_proba/dane.py z ustawienia.json (oraz punktu\n"
                "\ttrenera ze swiat/miasteczko_bazar/znaczniki.json). Nie edytuj ręcznie: zmień ustawienia i uruchom dane.py.\n"
                "\tSkrót danych: %s\n]]\n" % D["skrot"])
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
            print("DaneTreningu.luau: %s (skrót %s, przypadków: plany %d, sekwencje %d)"
                  % ("aktualny" if ok else "NIEAKTUALNY", D["skrot"], len(D["przypadki"]["plany"]),
                     len(D["przypadki"]["sekwencje"])))
            return 0 if ok else 1
        folder = argv[argv.index("--wyjscie") + 1] if "--wyjscie" in argv else ZRODLA
        D = zapisz(folder)
        print("zapisano %s (skrót %s)" % (os.path.join(os.path.relpath(folder, REPO) if folder == ZRODLA else folder,
                                                       PLIK_LUAU), D["skrot"]))
        return 0
    except BladDanych as e:
        print("BŁĄD DANYCH: %s" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
