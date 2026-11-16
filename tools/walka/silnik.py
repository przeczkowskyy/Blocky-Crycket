#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Silnik walki v3 (zmiany po sesji glownej 16.11.2026) — doslowny port w Pythonie modulow Luau z src/server/Walka/.

    python -B tools/walka/silnik.py                      # jedna przykladowa walka (JSON)
    python -B tools/walka/silnik.py --ziarno 7 --klasa mag --wrog straznik_lasu --poziom 5

Port jest DOSLOWNY: ten sam generator liczb (Park-Miller), ta sama kolejnosc rzutow, te same wzory
i zaokraglenia, wiec dla tych samych danych i ziarna daje ten sam dziennik co Luau. Sekcje tego pliku
odpowiadaja modulom Luau (Los, Statystyki, Przeciwnicy, Umiejetnosci, Silnik) i maja te same nazwy funkcji.
Dane (klasy, umiejetnosci, pasywki, efekty, modyfikatory, przeciwnicy, stale) sa w dane_walki.json — jednym
zrodle dla obu jezykow. Opis zasad: tools/walka/ZMIANY_SESJA_1611.md.

Zasady, ktorych silnik pilnuje:
- walka trwa, az zycie jednej strony spadnie do zera; dlugosc wynika tylko ze statystyk i losowosci;
- zadnej minimalnej liczby tur, ostatniego dechu, ciosu rozstrzygajacego ani sciskania czasu;
- ten sam wzor dla gracza, postaci-przeciwnika i potwora (potwor ma klase i punkty statystyk jak postac);
- umiejetnosci aktywne odpalaja sie z MANY (pasek 0..mana_maks), a nie z odnowienia ani z losu;
- jedyny bezpiecznik to bardzo wysoki limit tur (stale.maks_tur), w praktyce nieosiagalny.
"""
import json
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
SCIEZKA_DANYCH = os.path.join(TU, "dane_walki.json")

with open(SCIEZKA_DANYCH, encoding="utf-8") as _plik:
    DANE = json.load(_plik)

STALE = DANE["stale"]
KLASY = DANE["klasy"]
KLASY_POTWOROW = DANE["klasy_potworow"]
EFEKTY = DANE["efekty"]
ZAKLECIA = DANE["zaklecia"]
UMIEJETNOSCI = DANE["umiejetnosci"]
PASYWNE = DANE["pasywne"]
PASYWKI_BRONI = DANE["pasywki_broni"]
MODYFIKATORY = DANE["modyfikatory"]
MODYFIKATORY_PO_ID = {m["id"]: m for m in MODYFIKATORY}
STATYSTYKI = DANE["statystyki"]
PRZECIWNICY_LISTA = DANE["przeciwnicy"]
PRZECIWNICY = {p["id"]: p for p in PRZECIWNICY_LISTA}

WERSJA_DZIENNIKA = 3
NIESKONCZONOSC = float("inf")
# zamkniete listy pol wejscia (te same w Statystyki.luau i Przeciwnicy.luau)
POLA_POSTACI = ["nazwa", "klasa", "poziom", "statystyki", "bron", "pancerz_przedmiotow", "tarcza", "umiejetnosci",
                "pasywki", "pet", "premie"]
POLA_BRONI = ["obrazenia", "zaklecie", "pasywka"]
POLA_TARCZY = ["blok"]
POLA_PRZECIWNIKA = ["potwor", "poziom", "postac"]


# ---------------------------------------------------------------- Los.luau
MODUL = 2147483647
ZIARNO_GRANICA = 2147483648  # 2^31: dozwolone ziarna to liczby calkowite 0 .. 2^31 - 1


def nowy_los(ziarno):
    stan = int(math.floor(abs(ziarno))) % MODUL
    if stan == 0:
        stan = 20261113

    def los():
        nonlocal stan
        stan = (stan * 48271) % MODUL
        return (stan - 1) / (MODUL - 1)

    for _ in range(8):
        los()
    return los


def zaokraglij(x):
    return int(math.floor(x + 0.5))


def premia(x, polowa):
    # rosnie od 0 do 1 coraz wolniej; przy x == polowa daje 0.5 — kazdy punkt cos daje, ale nic nie przekracza limitu
    return x / (x + polowa)


def miedzy(x, od, do):
    return min(do, max(od, x))


def blad(tekst):
    raise ValueError("Walka: " + tekst)


def liczba(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v and v != NIESKONCZONOSC and v != -NIESKONCZONOSC


def calkowita(v):
    return liczba(v) and math.floor(v) == v


# ---------------------------------------------------------------- Statystyki.luau
def sprawdz_premie(premie, co, strona):
    # pasywki z drzewka i pet: procentowe premie do SZESCIU statystyk (D-055, D-059)
    if premie is None:
        return
    if not isinstance(premie, dict):
        blad("%s strony %s musza byc tabela" % (co, strona))
    for klucz, wartosc in premie.items():
        if klucz not in STATYSTYKI:
            blad("%s strony %s: nieznana statystyka %s" % (co, strona, klucz))
        if not liczba(wartosc) or wartosc < 0 or wartosc > STALE["premia_maks"]:
            blad("%s strony %s: zla wartosc dla %s" % (co, strona, klucz))


def sprawdz_modyfikatory(mod, strona):
    # premie z przedmiotow i wezlow drzewka (sumuje je serwer): zamknieta lista kluczy z granicami z danych
    if mod is None:
        return
    if not isinstance(mod, dict):
        blad("premie strony %s musza byc tabela" % strona)
    for klucz, wartosc in mod.items():
        spec = MODYFIKATORY_PO_ID.get(klucz) if isinstance(klucz, str) else None
        if spec is None:
            blad("premie strony %s: nieznany modyfikator %s" % (strona, klucz))
        if not liczba(wartosc) or wartosc < spec["min"] or wartosc > spec["max"]:
            blad("premie strony %s: zla wartosc dla %s" % (strona, klucz))


def sprawdz_klucze(t, dozwolone, co, strona):
    # zamknieta lista pol: literowka (np. "premia" zamiast "premie", "pasywki" w broni) nie moze przejsc po cichu —
    # bez tego postac walczylaby bez przedmiotow albo slotow i nikt by tego nie zauwazyl (kontrola 16/17.11)
    for klucz in t:
        if klucz not in dozwolone:
            blad("nieznane pole %s w %s strony %s" % (klucz, co, strona))


def sprawdz_postac(p, strona):
    if not isinstance(p, dict):
        blad("brak opisu postaci strony %s" % strona)
    sprawdz_klucze(p, POLA_POSTACI, "opisie postaci", strona)
    klasa = KLASY.get(p.get("klasa")) if isinstance(p.get("klasa"), str) else None
    if klasa is None:
        blad("nieznana klasa strony %s" % strona)
    poziom = p.get("poziom")
    if not calkowita(poziom) or poziom < 1 or poziom > STALE["poziom_maks"]:
        blad("zly poziom strony %s" % strona)
    st = p.get("statystyki")
    if not isinstance(st, dict):
        blad("brak statystyk strony %s" % strona)
    for nazwa in STATYSTYKI:
        v = st.get(nazwa)
        if not liczba(v) or v < 0 or v > STALE["statystyka_maks"]:
            blad("zla statystyka %s strony %s" % (nazwa, strona))
    for klucz in st:
        if klucz not in STATYSTYKI:
            blad("nieznana statystyka %s strony %s" % (klucz, strona))
    bron = p.get("bron")
    if not isinstance(bron, dict) or not liczba(bron.get("obrazenia")) or bron["obrazenia"] <= 0 \
            or bron["obrazenia"] > STALE["statystyka_maks"]:
        blad("bron strony %s musi miec dodatnie obrazenia" % strona)
    sprawdz_klucze(bron, POLA_BRONI, "broni", strona)
    zaklecie = bron.get("zaklecie")
    if zaklecie is not None and (not isinstance(zaklecie, str) or zaklecie not in ZAKLECIA):
        blad("nieznane zaklecie broni strony %s" % strona)
    pb = bron.get("pasywka")
    if pb is not None:
        d = PASYWKI_BRONI.get(pb) if isinstance(pb, str) else None
        if d is None:
            blad("nieznana pasywka broni strony %s" % strona)
        if d["klasa"] != "" and d["klasa"] != p["klasa"]:
            blad("pasywka broni %s nie pasuje do klasy strony %s" % (pb, strona))
    pp = p.get("pancerz_przedmiotow")
    if pp is not None and (not liczba(pp) or pp < 0 or pp > STALE["statystyka_maks"]):
        blad("zly pancerz z przedmiotow strony %s" % strona)
    tarcza = p.get("tarcza")
    if tarcza is not None:
        if not klasa["tarcza"]:
            blad("klasa %s nie nosi tarczy (strona %s)" % (klasa["nazwa"], strona))
        if not isinstance(tarcza, dict) or not liczba(tarcza.get("blok")) or tarcza["blok"] < 0 \
                or tarcza["blok"] > STALE["blok_maks"]:
            blad("zla szansa bloku tarczy strony %s" % strona)
        sprawdz_klucze(tarcza, POLA_TARCZY, "tarczy", strona)
    um = p.get("umiejetnosci")
    if um is not None:
        if not isinstance(um, list):
            blad("umiejetnosci strony %s musza byc lista" % strona)
        if len(um) > STALE["maks_slotow"]:
            blad("strona %s ma %d umiejetnosci, a slotow jest najwyzej %d" % (strona, len(um), STALE["maks_slotow"]))
        for i in range(len(um)):
            # slot = umiejetnosc aktywna ALBO pasywna klasy (3 aktywne, 3 pasywne albo dowolna mieszanka)
            u = None
            if isinstance(um[i], str):
                u = UMIEJETNOSCI.get(um[i])
                if u is None:
                    u = PASYWNE.get(um[i])
            if u is None:
                blad("nieznana umiejetnosc strony %s" % strona)
            if u["klasa"] != "" and u["klasa"] != p["klasa"]:
                blad("umiejetnosc %s nie nalezy do klasy strony %s" % (um[i], strona))
            for j in range(i):
                if um[j] == um[i]:
                    blad("umiejetnosc %s dwa razy u strony %s" % (um[i], strona))
    sprawdz_premie(p.get("pasywki"), "pasywki", strona)
    sprawdz_premie(p.get("pet"), "premie peta", strona)
    sprawdz_modyfikatory(p.get("premie"), strona)
    nazwa = p.get("nazwa")
    if nazwa is not None and not isinstance(nazwa, str):
        blad("nazwa strony %s musi byc napisem" % strona)


def zbierz_modyfikatory(zrodla):
    """Suma modyfikatorow z kolejnych zrodel (premie, pasywka broni, pasywki w slotach — w tej kolejnosci), liczona
    po LISCIE kluczy z danych (ta sama kolejnosc dodawania w obu portach), przycieta do granic z danych."""
    m = {}
    for spec in MODYFIKATORY:
        s = 0
        for z in zrodla:
            v = z.get(spec["id"])
            if v is not None:
                s = s + v
        m[spec["id"]] = miedzy(s, spec["min"], spec["max"])
    return m


def podziel_umiejetnosci(um):
    # sloty w kolejnosci: aktywne ida do rotacji many, pasywne daja stale modyfikatory
    lista, aktywne, pasywne = [], [], []
    for i in range(len(um)):
        lista.append(um[i])
        if um[i] in PASYWNE:
            pasywne.append(um[i])
        else:
            aktywne.append(um[i])
    return lista, aktywne, pasywne


def bojowe(klasa, poziom, e, obrazenia_broni, zaklecie, pancerz_przedmiotow, blok_tarczy, zrodla, um):
    """Wspolny wzor dla gracza, postaci-przeciwnika i potwora: efektywne statystyki + przedmioty + modyfikatory
    -> wartosci bojowe. `zrodla` to lista tabel modyfikatorow (bez pasywek ze slotow — te dokladamy tu)."""
    lista, aktywne, pasywne = podziel_umiejetnosci(um)
    wszystkie = []
    for z in zrodla:
        wszystkie.append(z)
    for u in pasywne:
        wszystkie.append(PASYWNE[u]["modyfikatory"])
    m = zbierz_modyfikatory(wszystkie)
    # wskrzeszenie (legendarna pasywka, propozycja D-094) — TYLKO ze slotu: nie ma go wsrod modyfikatorow,
    # wiec nie da go ani pasywka broni, ani premia z przedmiotow czy drzewka
    wsk = 0
    for u in pasywne:
        wsk = max(wsk, PASYWNE[u]["wskrzeszenie"])
    polowa = STALE["polowa_baza"] + STALE["polowa_na_poziom"] * poziom
    zycie = zaokraglij(klasa["mnoznik_zycia"] * (STALE["zycie_baza"] + STALE["zycie_na_poziom"] * poziom
                                                 + STALE["zycie_za_kondycje"] * e["kondycja"]) * (1 + m["zycie"]))
    p_zr = premia(e["zrecznosc"], polowa)
    zysk = 1 + m["zysk_many"] + STALE["mana_premia_za_aktywna"] * max(0, len(aktywne) - 1)
    return {
        "zycie": max(1, zycie),
        "cios": klasa["mnoznik_ciosu"] * (obrazenia_broni + STALE["sila_za_punkt"] * e["sila"]) * (1 + m["cios"]),
        "cios_zwykly": max(0, 1 + m["cios_zwykly"]),
        "rodzaj_ciosu": klasa["rodzaj_ciosu"],
        "pancerz": klasa["mnoznik_pancerza"] * (STALE["pancerz_za_punkt"] * e["pancerz"] + pancerz_przedmiotow)
                   * (1 + m["pancerz"]),
        "odpornosc": klasa["mnoznik_odpornosci"] * STALE["odpornosc_za_inteligencje"] * e["inteligencja"]
                     * (1 + m["odpornosc"]),
        "unik": miedzy(klasa["unik_baza"] + (klasa["unik_limit"] - klasa["unik_baza"]) * p_zr + m["unik"],
                       0, STALE["unik_maks"]),
        "krytyk": miedzy(STALE["krytyk_baza"] + (STALE["krytyk_limit"] - STALE["krytyk_baza"])
                         * premia(e["szczescie"], polowa) + m["krytyk"], 0, STALE["krytyk_maks"]),
        "mnoznik_krytyka": max(1, klasa["mnoznik_krytyka"] + klasa["kryt_za_zrecznosc"] * p_zr + m["mnoznik_krytyka"]),
        "blok": miedzy(klasa["blok"] + blok_tarczy + m["blok"], 0, STALE["blok_maks"]),
        "moc": max(0, 1 + STALE["moc_maks"] * premia(e["inteligencja"], polowa) + m["moc"]),
        "umiejetnosci": lista,
        "aktywne": aktywne,
        "pasywne": pasywne,
        "zaklecie": zaklecie,
        "zysk_many": max(0, zysk),
        "koszt_many": m["koszt_many"],
        "mana_start": miedzy(zaokraglij(m["mana_startowa"]), 0, STALE["mana_maks"]),
        "wskrzeszenie": wsk,
        "mod": m,
        "efektywne": e,
    }


def wartosci_postaci(p):
    """Szesc statystyk + przedmioty + pasywki + pet + premie -> wartosci bojowe (gracz i postac-przeciwnik)."""
    klasa = KLASY[p["klasa"]]
    poziom = p["poziom"]
    st = p["statystyki"]
    pasywki = p.get("pasywki") or {}
    pet = p.get("pet") or {}
    e = {}
    for nazwa in STATYSTYKI:
        # pasywki z drzewka i pet tylko mnoza statystyki (D-055, D-059)
        e[nazwa] = zaokraglij(st[nazwa] * (1 + pasywki.get(nazwa, 0)) * (1 + pet.get(nazwa, 0)))
    bron = p["bron"]
    tarcza = p.get("tarcza")
    zrodla = []
    if p.get("premie") is not None:
        zrodla.append(p["premie"])
    if bron.get("pasywka") is not None:
        zrodla.append(PASYWKI_BRONI[bron["pasywka"]]["modyfikatory"])
    um = p.get("umiejetnosci") or []
    w = bojowe(klasa, poziom, e, bron["obrazenia"], bron.get("zaklecie") or "", p.get("pancerz_przedmiotow") or 0,
               tarcza["blok"] if tarcza is not None else 0, zrodla, um)
    w["nazwa"] = p.get("nazwa") or klasa["nazwa"]
    w["rodzaj"] = "postac"
    w["id"] = p["klasa"]
    w["ranga"] = "gracz"
    w["poziom"] = poziom
    return w


# ---------------------------------------------------------------- Przeciwnicy.luau
def skala(para, poziom):
    return para[0] + para[1] * (poziom - 1)


def klasa_potwora(d):
    # potwor ma klase gracza (zwiadowca, mag, wojownik) albo klase tylko dla potworow (np. straznik biomu)
    k = KLASY.get(d["klasa"])
    if k is None:
        k = KLASY_POTWOROW[d["klasa"]]
    return k


def wartosci_potwora(identyfikator, poziom):
    d = PRZECIWNICY[identyfikator]
    e = {}
    for nazwa in STATYSTYKI:
        e[nazwa] = max(0, zaokraglij(skala(d["statystyki"][nazwa], poziom)))
    w = bojowe(klasa_potwora(d), poziom, e, skala(d["bron"], poziom), "", skala(d["pancerz_przedmiotow"], poziom),
               d["tarcza"], [d["modyfikatory"]], d["umiejetnosci"])
    w["nazwa"] = d["nazwa"]
    w["rodzaj"] = "potwor"
    w["id"] = d["id"]
    w["ranga"] = d["ranga"]
    w["poziom"] = poziom
    return w


def wartosci_przeciwnika(przeciwnik):
    if not isinstance(przeciwnik, dict):
        blad("brak opisu przeciwnika")
    sprawdz_klucze(przeciwnik, POLA_PRZECIWNIKA, "opisie przeciwnika", "wrog")
    potwor = przeciwnik.get("potwor")
    postac = przeciwnik.get("postac")
    if potwor is not None and postac is not None:
        blad("przeciwnik to potwor ALBO postac, nie oba")
    if potwor is not None:
        if not isinstance(potwor, str) or potwor not in PRZECIWNICY:
            blad("nieznany przeciwnik")
        poziom = przeciwnik.get("poziom")
        if not calkowita(poziom) or poziom < 1 or poziom > STALE["poziom_maks"]:
            blad("zly poziom przeciwnika")
        return wartosci_potwora(potwor, poziom)
    if postac is not None:
        sprawdz_postac(postac, "wrog")
        return wartosci_postaci(postac)
    blad("przeciwnik musi miec pole potwor albo postac")


def losuj_lup(strona, wygrana, los):
    # zawsze piec rzutow w tej samej kolejnosci, niezaleznie od wyniku (powtarzalnosc i zgodnosc portow)
    r_zloto, r_dosw, r_token, r_gemy, r_shard = los(), los(), los(), los(), los()
    lup = {"zloto": 0, "doswiadczenie": 0, "tokeny_krainy": 0, "gemy": 0, "shard_ewolucji": 0, "kraina": ""}
    if strona["rodzaj"] != "potwor":
        return lup  # Arena (PvP): nagrody poza zakresem silnika
    d = PRZECIWNICY[strona["id"]]
    L = d["lup"]
    poziom = strona["poziom"]
    lup["kraina"] = d["kraina"]
    dosw = skala(L["doswiadczenie"], poziom)
    if wygrana:
        lup["zloto"] = zaokraglij(skala(L["zloto"], poziom) * (0.8 + 0.4 * r_zloto))
        lup["doswiadczenie"] = zaokraglij(dosw * (0.9 + 0.2 * r_dosw))
        lup["tokeny_krainy"] = L["tokeny"] + (1 if r_token < L["szansa_tokenu"] else 0)
        lup["gemy"] = 1 if r_gemy < L["szansa_gemow"] else 0
        # Shard Ewolucji wypada wylacznie ze straznika biomu (D-058); jajek z potworow nie ma wcale (D-060)
        if d["ranga"] == "straznik" and r_shard < L["szansa_sharda"]:
            lup["shard_ewolucji"] = 1
    else:
        lup["doswiadczenie"] = zaokraglij(dosw * STALE["udzial_doswiadczenia_przy_przegranej"])
    return lup


# ---------------------------------------------------------------- Umiejetnosci.luau (mana, ciosy, umiejetnosci, efekty)
def inna(strona):
    return "wrog" if strona == "gracz" else "gracz"


def ma_efekt(stan_strony, typ):
    for ef in stan_strony["efekty"]:
        if ef["typ"] == typ:
            return True
    return False


def wzmocnienie(stan_strony):
    m = 1
    for ef in stan_strony["efekty"]:
        if ef["typ"] == "wzmocnienie":
            m = m + ef["wartosc"]
    return m


def oslona(stan_strony):
    # tarcza z umiejetnosci (Kamienna skora, Bariera): ulamek obrazen, ktory PRZECHODZI (1 - redukcja)
    m = 1
    for ef in stan_strony["efekty"]:
        if ef["typ"] == "oslona":
            m = m * (1 - ef["wartosc"])
    return m


def pancerz_efektywny(walczacy, stan_strony):
    p = walczacy["pancerz"]
    for ef in stan_strony["efekty"]:
        if ef["typ"] == "zdarcie":
            p = p * (1 - ef["wartosc"])
    return p


def unik_efektywny(walczacy, stan_strony):
    u = walczacy["unik"]
    for ef in stan_strony["efekty"]:
        if ef["typ"] == "spowolnienie":
            u = u * (1 - ef["wartosc"])
    return u


def mnoznik_many(w, strona):
    m = w["strony"][strona]["zysk_many"]
    for ef in w["stan"][strona]["efekty"]:
        if ef["typ"] == "spowolnienie":
            m = m * (1 - ef["mana_kara"])
    return m


def dodaj_mane(w, strona, ile):
    s = w["stan"][strona]
    s["mana"] = min(STALE["mana_maks"], s["mana"] + ile)


def po_obronie(w, surowe, rodzaj, cel):
    # Pancerz (fizyczne) i odpornosc na magie (magiczne) to PUNKTY odejmowane od ciosu (D-062), ale obrona nigdy nie
    # zatrzymuje wiecej niz limit_redukcji surowego ciosu — zawsze przechodzi co najmniej (1 - limit) ciosu
    if rodzaj == "fizyczne":
        obrona = pancerz_efektywny(w["strony"][cel], w["stan"][cel])
    else:
        obrona = w["strony"][cel]["odpornosc"]
    return max(surowe * (1 - STALE["limit_redukcji"]), surowe - obrona)


def obrazenia_trafienia(w, cel, surowe, rodzaj, zablokowane):
    """Surowy cios -> (obrazenia, pochloniete): obrona, blok (czesc_przez_blok), tarcza procentowa celu.
    pochloniete = ile zatrzymala tarcza procentowa (do napisu „TARCZA −n”)."""
    wynik = po_obronie(w, surowe, rodzaj, cel)
    if zablokowane:
        if STALE["czesc_przez_blok"] <= 0:
            return 0, 0
        wynik = wynik * STALE["czesc_przez_blok"]
    obrazenia = max(1, zaokraglij(wynik * oslona(w["stan"][cel])))
    pochloniete = max(0, zaokraglij(wynik) - obrazenia)
    return obrazenia, pochloniete


def wskrzes(w, strona):
    """Wskrzeszenie (propozycja D-094): gdy zycie strony spadlo do zera, a ma w slocie wskrzeszenie, ktorego jeszcze
    nie uzyla — wraca z ulamkiem maks. zycia (bez losowania) i zdarzeniem "wskrzeszenie" zaraz po smiertelnym.
    Dziala raz na walke, takze po smiertelnym tyknieciu trucizny, podpalenia albo krwawienia."""
    s = w["stan"][strona]
    if s["hp"] <= 0 and s["wskrzeszenie"] > 0:
        s["hp"] = max(1, zaokraglij(w["strony"][strona]["zycie"] * s["wskrzeszenie"]))
        s["wskrzeszenie"] = 0
        zdarzenie(w, "wskrzeszenie", strona, strona, STALE["czasy"]["wskrzeszenie"], {"wartosc": s["hp"]})


def przyjmij(w, cel, obrazenia):
    # zycie schodzi o obrazenia; zywy cel laduje mane proporcjonalnie do utraconego ULAMKA maks. zycia
    s = w["stan"][cel]
    stracone = min(s["hp"], obrazenia)
    s["hp"] = s["hp"] - stracone
    if stracone > 0 and s["hp"] > 0:
        zycie = w["strony"][cel]["zycie"]
        dodaj_mane(w, cel, zaokraglij(STALE["mana_za_obrazenia"] * 100 * stracone / zycie * mnoznik_many(w, cel)))
    return stracone


def zdarzenie(w, typ, kto, cel, trwa, pola):
    z = {
        "typ": typ, "kto": kto, "cel": cel,
        "obrazenia": 0, "pochloniete": 0, "rodzaj": "", "umiejetnosc": "", "efekt": "",
        "krytyk": False, "wartosc": 0, "tury": 0, "stosy": 0,
        "t": w["czas"] / 100, "trwa": trwa / 100,
    }
    for k in ("obrazenia", "pochloniete", "rodzaj", "umiejetnosc", "efekt", "krytyk", "wartosc", "tury", "stosy"):
        if k in pola:
            z[k] = pola[k]
    z["hp_gracz"] = w["stan"]["gracz"]["hp"]
    z["hp_wrog"] = w["stan"]["wrog"]["hp"]
    z["mana_gracz"] = w["stan"]["gracz"]["mana"]
    z["mana_wrog"] = w["stan"]["wrog"]["mana"]
    w["czas"] = w["czas"] + trwa
    w["dziennik"].append(z)
    return z


def naloz_efekt(w, zrodlo, cel, id_efektu, moc, trafienie):
    E = EFEKTY[id_efektu]
    A = w["strony"][zrodlo]
    D = w["strony"][cel]
    s = w["stan"][cel]
    trwa = E["trwa"]
    if E["mod_trwania"] != "":
        trwa = trwa + zaokraglij(A["mod"][E["mod_trwania"]])
    stary = -1
    for i in range(len(s["efekty"])):
        if stary == -1 and s["efekty"][i]["id"] == id_efektu:
            stary = i
    nowy = {"id": id_efektu, "typ": E["typ"], "trwa": trwa, "od_tury": w["tura"], "wartosc": E["wartosc"],
            "tick": 0, "stosy": 1, "rodzaj": E["rodzaj"], "mana_kara": E["mana_kara"]}
    pokaz = 0
    if E["typ"] == "obrazenia_w_czasie":
        sila = 1
        if E["mod_sily"] != "":
            sila = sila + A["mod"][E["mod_sily"]]
        if E["sila"] == "cios":
            jeden = A["cios"] * E["udzial"] * moc * sila           # trucizna: od ciosu atakujacego
        elif E["sila"] == "zycie_celu":
            jeden = min(D["zycie"] * E["udzial"] * moc, A["cios"] * E["limit_ciosu"]) * sila  # podpalenie: od zycia celu
        else:
            jeden = trafienie * E["udzial"] * sila                 # krwawienie: od ciosu, ktory je nalozyl
        nowy["tick"] = max(1, zaokraglij(jeden))
        maks = E["stosy_maks"]
        if E["mod_stosow"] != "":
            maks = maks + math.floor(A["mod"][E["mod_stosow"]])
        if stary != -1:
            nowy["stosy"] = min(maks, s["efekty"][stary]["stosy"] + 1)
        pokaz = nowy["tick"] * nowy["stosy"]
    elif E["typ"] == "oslona" or E["typ"] == "wzmocnienie":
        nowy["wartosc"] = min(E["limit"], E["wartosc"] * moc)
        pokaz = zaokraglij(nowy["wartosc"] * 100)
    else:
        pokaz = zaokraglij(E["wartosc"] * 100)
    if stary != -1:
        s["efekty"][stary] = nowy  # ten sam efekt odswieza sile i czas (trucizna dodaje przy tym stos)
    else:
        s["efekty"].append(nowy)
    zdarzenie(w, "efekt_nalozony", zrodlo, cel, STALE["czasy"]["efekt_nalozony"],
              {"efekt": id_efektu, "wartosc": pokaz, "tury": trwa, "stosy": nowy["stosy"]})


def zwykly_cios(w, kto, cel):
    A = w["strony"][kto]
    D = w["strony"][cel]
    # zawsze piec rzutow w tej samej kolejnosci
    r_rozrzut, r_unik, r_blok, r_kryt, r_zakl = w["los"](), w["los"](), w["los"](), w["los"](), w["los"]()
    rozrzut = STALE["rozrzut_min"] + STALE["rozrzut_zakres"] * r_rozrzut
    if r_unik < unik_efektywny(D, w["stan"][cel]):
        typ = "unik"
    elif r_blok < D["blok"]:
        typ = "blok"
    elif r_kryt < A["krytyk"]:
        typ = "krytyk"
    else:
        typ = "cios"
    zysk = zaokraglij(STALE["mana_za_cios"] * mnoznik_many(w, kto))
    if typ == "unik":
        dodaj_mane(w, kto, zysk)
        zdarzenie(w, "unik", kto, cel, STALE["czasy"]["unik"], {"rodzaj": A["rodzaj_ciosu"]})
        return
    surowe = A["cios"] * A["cios_zwykly"] * rozrzut * wzmocnienie(w["stan"][kto])
    if typ == "krytyk":
        surowe = surowe * A["mnoznik_krytyka"]
    obrazenia, pochloniete = obrazenia_trafienia(w, cel, surowe, A["rodzaj_ciosu"], typ == "blok")
    przyjmij(w, cel, obrazenia)
    dodaj_mane(w, kto, zysk)
    zdarzenie(w, typ, kto, cel, STALE["czasy"][typ],
              {"obrazenia": obrazenia, "pochloniete": pochloniete, "rodzaj": A["rodzaj_ciosu"], "krytyk": typ == "krytyk"})
    wskrzes(w, cel)
    if w["stan"][cel]["hp"] > 0 and A["zaklecie"] != "" and typ != "blok":
        z = ZAKLECIA[A["zaklecie"]]
        if r_zakl < z["szansa"] + A["mod"]["szansa_zaklecia"]:
            naloz_efekt(w, kto, cel, z["efekt"], 1, obrazenia)


def uzyj_umiejetnosci(w, kto, cel, id_um, koszt):
    U = UMIEJETNOSCI[id_um]
    A = w["strony"][kto]
    # zawsze cztery rzuty + jeden na kazdy efekt, w tej samej kolejnosci
    r_rozrzut, r_unik, r_blok, r_kryt = w["los"](), w["los"](), w["los"](), w["los"]()
    r_efekty = []
    for _ in U["efekty"]:
        r_efekty.append(w["los"]())
    if U["cel"] == "sam":
        zdarzenie(w, "umiejetnosc", kto, kto, U["czas"], {"umiejetnosc": id_um, "wartosc": koszt})
        for i in range(len(U["efekty"])):
            wpis = U["efekty"][i]
            if r_efekty[i] < wpis["szansa"]:
                naloz_efekt(w, kto, kto, wpis["efekt"], A["moc"], 0)
        return
    D = w["strony"][cel]
    # umiejetnosc na przeciwnika to atak jak kazdy inny: mozna jej uniknac i przyjac ja na blok
    if r_unik < unik_efektywny(D, w["stan"][cel]):
        zdarzenie(w, "unik", kto, cel, U["czas"], {"umiejetnosc": id_um, "rodzaj": U["rodzaj"], "wartosc": koszt})
        return
    zablokowana = r_blok < D["blok"]
    obrazenia, pochloniete, krytyk = 0, 0, False
    if U["mnoznik"] > 0:
        rozrzut = STALE["rozrzut_min"] + STALE["rozrzut_zakres"] * r_rozrzut
        surowe = A["cios"] * U["mnoznik"] * A["moc"] * rozrzut * wzmocnienie(w["stan"][kto])
        krytyk = not zablokowana and r_kryt < A["krytyk"] + U["premia_krytyka"]
        if krytyk:
            surowe = surowe * A["mnoznik_krytyka"]
        obrazenia, pochloniete = obrazenia_trafienia(w, cel, surowe, U["rodzaj"], zablokowana)
        przyjmij(w, cel, obrazenia)
    zdarzenie(w, "blok" if zablokowana else "umiejetnosc", kto, cel, U["czas"],
              {"umiejetnosc": id_um, "obrazenia": obrazenia, "pochloniete": pochloniete,
               "rodzaj": U["rodzaj"], "krytyk": krytyk, "wartosc": koszt})
    wskrzes(w, cel)
    if w["stan"][cel]["hp"] > 0 and not zablokowana:
        for i in range(len(U["efekty"])):
            wpis = U["efekty"][i]
            if r_efekty[i] < wpis["szansa"]:
                naloz_efekt(w, kto, cel, wpis["efekt"], A["moc"], obrazenia)


def koszt_umiejetnosci(walczacy, id_um):
    return miedzy(zaokraglij(UMIEJETNOSCI[id_um]["koszt_many"] * (1 - walczacy["koszt_many"])), 1, STALE["mana_maks"])


def akcja(w, kto, cel):
    """MANA: strona ma pasek 0..mana_maks, ktory rosnie za kazdy wlasny zwykly cios (takze chybiony) i za utracone
    zycie. Na swojej turze: jesli mana >= koszt NASTEPNEJ aktywnej umiejetnosci w rotacji slotow — uzywa jej zamiast
    zwyklego ciosu i placi koszt; inaczej zwykly cios. Rotacja idzie po aktywnych w kolejnosci slotow i wraca na
    poczatek. Pasywne umiejetnosci nie biora udzialu w rotacji (daja stale modyfikatory)."""
    A = w["strony"][kto]
    s = w["stan"][kto]
    n = len(A["aktywne"])
    if n > 0:
        id_um = A["aktywne"][s["nastepna"]]
        koszt = koszt_umiejetnosci(A, id_um)
        if s["mana"] >= koszt:
            s["mana"] = s["mana"] - koszt
            s["nastepna"] = (s["nastepna"] + 1) % n
            uzyj_umiejetnosci(w, kto, cel, id_um, koszt)
            return
    zwykly_cios(w, kto, cel)


def tykniecia(w, kto):
    # obrazenia w czasie (trucizna, podpalenie, krwawienie) na poczatku tury nosiciela; omijaja Pancerz, odpornosc
    # i tarcze procentowa, nie da sie ich uniknac ani zablokowac
    s = w["stan"][kto]
    for ef in s["efekty"]:
        if ef["typ"] == "obrazenia_w_czasie" and s["hp"] > 0:
            obr = ef["tick"] * ef["stosy"]
            przyjmij(w, kto, obr)
            zdarzenie(w, "efekt_tick", kto, kto, STALE["czasy"]["efekt_tick"],
                      {"efekt": ef["id"], "obrazenia": obr, "rodzaj": ef["rodzaj"], "stosy": ef["stosy"]})
            wskrzes(w, kto)


def koniec_tury(w, kto):
    # efekt trwa N tur NOSICIELA: na koncu kazdej jego tury traci 1 (oprocz tury, w ktorej go nalozono)
    s = w["stan"][kto]
    zostaja = []
    for ef in s["efekty"]:
        if ef["od_tury"] != w["tura"]:
            ef["trwa"] = ef["trwa"] - 1
        if ef["trwa"] <= 0:
            zdarzenie(w, "efekt_koniec", kto, kto, STALE["czasy"]["efekt_koniec"], {"efekt": ef["id"]})
        else:
            zostaja.append(ef)
    s["efekty"] = zostaja


# ---------------------------------------------------------------- Silnik.luau
def nowy_stan(walczacy):
    return {"hp": walczacy["zycie"], "efekty": [], "mana": walczacy["mana_start"], "nastepna": 0,
            "wskrzeszenie": walczacy["wskrzeszenie"]}


def opis_strony(walczacy):
    return {"nazwa": walczacy["nazwa"], "rodzaj": walczacy["rodzaj"], "id": walczacy["id"], "ranga": walczacy["ranga"],
            "poziom": walczacy["poziom"], "zycie": walczacy["zycie"], "mana": walczacy["mana_start"],
            "mana_maks": STALE["mana_maks"]}


def symuluj(gracz, przeciwnik, ziarno):
    """symuluj(gracz, przeciwnik, ziarno) -> walka (dziennik v3). Gracz: opis postaci; przeciwnik:
    {"potwor": id, "poziom": n} albo {"postac": opis postaci} (Arena, test lustrzany)."""
    sprawdz_postac(gracz, "gracz")
    A = wartosci_postaci(gracz)
    B = wartosci_przeciwnika(przeciwnik)
    # tylko calkowite ziarno w [0, 2^31): powyzej 2^53 Luau (liczby double) i Python (dokladne int) licza
    # reszte z dzielenia inaczej i dalyby rozne walki — takie ziarno odrzucamy czytelnym bledem
    if not calkowita(ziarno) or ziarno < 0 or ziarno >= ZIARNO_GRANICA:
        blad("ziarno musi byc liczba calkowita od 0 do %d" % (ZIARNO_GRANICA - 1))
    # pasywki „na starcie walki” dzialajace na przeciwnika: zdarcie czesci jego Pancerza na cala walke
    pa, pb = A["pancerz"], B["pancerz"]
    A["pancerz"] = pa * (1 + B["mod"]["pancerz_wroga"])
    B["pancerz"] = pb * (1 + A["mod"]["pancerz_wroga"])
    los = nowy_los(ziarno)
    w = {
        "strony": {"gracz": A, "wrog": B},
        "stan": {"gracz": nowy_stan(A), "wrog": nowy_stan(B)},
        "dziennik": [],
        "czas": STALE["czas_wstepu"],
        "tura": 0,
        "los": los,
    }
    kolej = "gracz" if los() < STALE["szansa_pierwszego_ruchu"] else "wrog"
    zwyciezca = ""
    bezpiecznik = False
    while zwyciezca == "":
        if w["tura"] >= STALE["maks_tur"]:
            # TECHNICZNY bezpiecznik przeciw petli bez konca — w praktyce nieosiagalny (test na wielu ziarnach);
            # rozstrzyga wiekszy procent pozostalego zycia (mnozenie na krzyz, bez dzielenia), remis -> gracz
            bezpiecznik = True
            # float(): Luau mnozy liczby double — przy zyciu rzedu 10^8 iloczyn przekracza 2^53 i jest zaokraglany;
            # dokladne int Pythona mogloby wtedy dac inny znak porownania niz Luau (kontrola 16/17.11)
            if float(w["stan"]["gracz"]["hp"]) * B["zycie"] >= float(w["stan"]["wrog"]["hp"]) * A["zycie"]:
                zwyciezca = "gracz"
            else:
                zwyciezca = "wrog"
            break
        w["tura"] = w["tura"] + 1
        kto = kolej
        cel = inna(kto)
        tykniecia(w, kto)
        if w["stan"][kto]["hp"] <= 0:
            zwyciezca = cel
            break
        if ma_efekt(w["stan"][kto], "ogluszenie"):
            zdarzenie(w, "utrata_tury", kto, kto, STALE["czasy"]["utrata_tury"], {})
        else:
            akcja(w, kto, cel)
            if w["stan"][cel]["hp"] <= 0:
                zwyciezca = kto
                break
        koniec_tury(w, kto)
        kolej = cel
    wygrana = zwyciezca == "gracz"
    lup = losuj_lup(B, wygrana, los)
    czas = w["czas"] + STALE["czas_finalu"]
    return {
        "wersja": WERSJA_DZIENNIKA,
        "ziarno": ziarno,
        "strony": {"gracz": opis_strony(A), "wrog": opis_strony(B)},
        "dziennik": w["dziennik"],
        "wynik": "wygrana" if wygrana else "przegrana",
        "tury": w["tura"],
        "bezpiecznik": bezpiecznik,
        "lup": lup,
        "czesc_przez_blok": STALE["czesc_przez_blok"],
        "czas_wstepu": STALE["czas_wstepu"] / 100,
        "czas_finalu": STALE["czas_finalu"] / 100,
        "czas": czas / 100,
    }


def main():
    import argparse
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, TU)
    import wzorcowe
    ap = argparse.ArgumentParser(description="Jedna walka silnika v3 (JSON)")
    ap.add_argument("--ziarno", type=int, default=1)
    ap.add_argument("--klasa", default="wojownik", choices=sorted(KLASY))
    ap.add_argument("--wrog", default="lesny_slime", help="id potwora albo klasa (walka postac na postac)")
    ap.add_argument("--poziom", type=int, default=5)
    a = ap.parse_args()
    gracz = wzorcowe.postac(a.klasa, a.poziom)
    if a.wrog in KLASY:
        przeciwnik = {"postac": wzorcowe.postac(a.wrog, a.poziom)}
    else:
        przeciwnik = {"potwor": a.wrog, "poziom": a.poziom}
    print(json.dumps(symuluj(gracz, przeciwnik, a.ziarno), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
