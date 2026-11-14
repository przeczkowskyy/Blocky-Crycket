#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Silnik walki v2 — doslowny port w Pythonie modulow Luau z src/server/Walka/.

    python -B tools/walka/silnik.py                      # jedna przykladowa walka (JSON)
    python -B tools/walka/silnik.py --ziarno 7 --klasa mag --wrog straznik_lasu --poziom 5

Port jest DOSLOWNY: ten sam generator liczb (Park-Miller), ta sama kolejnosc rzutow, te same wzory
i zaokraglenia, wiec dla tych samych danych i ziarna daje ten sam dziennik co Luau. Sekcje tego pliku
odpowiadaja modulom Luau (Los, Statystyki, Przeciwnicy, Umiejetnosci, Silnik) i maja te same nazwy funkcji.
Dane (klasy, umiejetnosci, efekty, przeciwnicy, stale) sa w dane_walki.json — jednym zrodle dla obu jezykow.

Zasady, ktorych silnik pilnuje (B&C/Gra/Walka v2 — silnik, klasy i umiejętności.md):
- walka trwa, az zycie jednej strony spadnie do zera; dlugosc wynika tylko ze statystyk i losowosci;
- zadnej minimalnej liczby tur, ostatniego dechu, ciosu rozstrzygajacego ani sciskania czasu;
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
EFEKTY = DANE["efekty"]
ZAKLECIA = DANE["zaklecia"]
UMIEJETNOSCI = DANE["umiejetnosci"]
STATYSTYKI = DANE["statystyki"]
PRZECIWNICY_LISTA = DANE["przeciwnicy"]
PRZECIWNICY = {p["id"]: p for p in PRZECIWNICY_LISTA}

WERSJA_DZIENNIKA = 2
NIESKONCZONOSC = float("inf")


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


def blad(tekst):
    raise ValueError("Walka: " + tekst)


def liczba(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v and v != NIESKONCZONOSC and v != -NIESKONCZONOSC


def calkowita(v):
    return liczba(v) and math.floor(v) == v


# ---------------------------------------------------------------- Statystyki.luau
def sprawdz_premie(premie, co, strona):
    if premie is None:
        return
    if not isinstance(premie, dict):
        blad("%s strony %s musza byc tabela" % (co, strona))
    for klucz, wartosc in premie.items():
        if klucz not in STATYSTYKI:
            blad("%s strony %s: nieznana statystyka %s" % (co, strona, klucz))
        if not liczba(wartosc) or wartosc < 0 or wartosc > STALE["premia_maks"]:
            blad("%s strony %s: zla wartosc dla %s" % (co, strona, klucz))


def sprawdz_postac(p, strona):
    if not isinstance(p, dict):
        blad("brak opisu postaci strony %s" % strona)
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
    zaklecie = bron.get("zaklecie")
    if zaklecie is not None and (not isinstance(zaklecie, str) or zaklecie not in ZAKLECIA):
        blad("nieznane zaklecie broni strony %s" % strona)
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
    um = p.get("umiejetnosci")
    if um is not None:
        if not isinstance(um, list):
            blad("umiejetnosci strony %s musza byc lista" % strona)
        if len(um) > STALE["maks_slotow"]:
            blad("strona %s ma %d umiejetnosci, a slotow jest najwyzej %d" % (strona, len(um), STALE["maks_slotow"]))
        for i in range(len(um)):
            u = UMIEJETNOSCI.get(um[i]) if isinstance(um[i], str) else None
            if u is None:
                blad("nieznana umiejetnosc strony %s" % strona)
            if u["klasa"] != p["klasa"]:
                blad("umiejetnosc %s nie nalezy do klasy strony %s" % (um[i], strona))
            for j in range(i):
                if um[j] == um[i]:
                    blad("umiejetnosc %s dwa razy u strony %s" % (um[i], strona))
    sprawdz_premie(p.get("pasywki"), "pasywki", strona)
    sprawdz_premie(p.get("pet"), "premie peta", strona)
    nazwa = p.get("nazwa")
    if nazwa is not None and not isinstance(nazwa, str):
        blad("nazwa strony %s musi byc napisem" % strona)


def wartosci_postaci(p):
    """Szesc statystyk + przedmioty + pasywki + pet -> wartosci bojowe (te same wzory dla gracza i dla postaci-przeciwnika)."""
    klasa = KLASY[p["klasa"]]
    poziom = p["poziom"]
    st = p["statystyki"]
    pasywki = p.get("pasywki") or {}
    pet = p.get("pet") or {}
    e = {}
    for nazwa in STATYSTYKI:
        # pasywki z drzewka i pet tylko mnoza statystyki (D-055, D-059)
        e[nazwa] = zaokraglij(st[nazwa] * (1 + pasywki.get(nazwa, 0)) * (1 + pet.get(nazwa, 0)))
    polowa = STALE["polowa_baza"] + STALE["polowa_na_poziom"] * poziom
    bron = p["bron"]
    tarcza = p.get("tarcza")
    umiejetnosci = []
    um = p.get("umiejetnosci") or []
    for i in range(len(um)):  # po indeksach 1..n jak w Luau (sprawdz_postac pilnuje, ze to lista)
        umiejetnosci.append(um[i])
    zycie =zaokraglij(klasa["mnoznik_zycia"] * (STALE["zycie_baza"] + STALE["zycie_na_poziom"] * poziom
                                                 + STALE["zycie_za_kondycje"] * e["kondycja"]))
    return {
        "nazwa": p.get("nazwa") or klasa["nazwa"],
        "rodzaj": "postac",
        "id": p["klasa"],
        "ranga": "gracz",
        "poziom": poziom,
        "zycie": max(1, zycie),
        "cios": klasa["mnoznik_ciosu"] * (bron["obrazenia"] + STALE["sila_za_punkt"] * e["sila"]),
        "rodzaj_ciosu": klasa["rodzaj_ciosu"],
        "pancerz": STALE["pancerz_za_punkt"] * e["pancerz"] + (p.get("pancerz_przedmiotow") or 0),
        "odpornosc": STALE["odpornosc_za_inteligencje"] * e["inteligencja"],
        "unik": klasa["unik_baza"] + (klasa["unik_limit"] - klasa["unik_baza"]) * premia(e["zrecznosc"], polowa),
        "krytyk": STALE["krytyk_baza"] + (STALE["krytyk_limit"] - STALE["krytyk_baza"]) * premia(e["szczescie"], polowa),
        "mnoznik_krytyka": klasa["mnoznik_krytyka"],
        "blok": tarcza["blok"] if tarcza is not None else 0,
        "moc": 1 + STALE["moc_maks"] * premia(e["inteligencja"], polowa),
        "umiejetnosci": umiejetnosci,
        "zaklecie": bron.get("zaklecie") or "",
        "efektywne": e,
    }


# ---------------------------------------------------------------- Przeciwnicy.luau
def skala(para, poziom):
    return para[0] + para[1] * (poziom - 1)


def wartosci_potwora(identyfikator, poziom):
    d = PRZECIWNICY[identyfikator]
    umiejetnosci = []
    for u in d["umiejetnosci"]:
        umiejetnosci.append(u)
    return {
        "nazwa": d["nazwa"],
        "rodzaj": "potwor",
        "id": d["id"],
        "ranga": d["ranga"],
        "poziom": poziom,
        "zycie": max(1, zaokraglij(skala(d["zycie"], poziom))),
        "cios": skala(d["cios"], poziom),
        "rodzaj_ciosu": d["rodzaj_ciosu"],
        "pancerz": skala(d["pancerz"], poziom),
        "odpornosc": skala(d["odpornosc"], poziom),
        "unik": d["unik"],
        "krytyk": d["krytyk"],
        "mnoznik_krytyka": d["mnoznik_krytyka"],
        "blok": d["blok"],
        "moc": d["moc"],
        "umiejetnosci": umiejetnosci,
        "zaklecie": "",
    }


def wartosci_przeciwnika(przeciwnik):
    if not isinstance(przeciwnik, dict):
        blad("brak opisu przeciwnika")
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


# ---------------------------------------------------------------- Umiejetnosci.luau (efekty i umiejetnosci)
def inna(strona):
    return "wrog" if strona == "gracz" else "gracz"


def wzmocnienie(stan_strony):
    m = 1
    for ef in stan_strony["efekty"]:
        if ef["typ"] == "wzmocnienie":
            m = m + ef["wartosc"]
    return m


def pancerz_efektywny(walczacy, stan_strony):
    p = walczacy["pancerz"]
    for ef in stan_strony["efekty"]:
        if ef["typ"] == "zdarcie":
            p = p * (1 - ef["wartosc"])
    return p


def ma_efekt(stan_strony, typ):
    for ef in stan_strony["efekty"]:
        if ef["typ"] == typ:
            return True
    return False


def po_obronie(w, surowe, rodzaj, cel):
    # Pancerz (fizyczne) i odpornosc na magie (magiczne) to PUNKTY odejmowane od ciosu; dolna granica:
    # zawsze przechodzi co najmniej min_czesc_po_obronie surowych obrazen, wiec nikt nie jest nietykalny
    if rodzaj == "fizyczne":
        obrona = pancerz_efektywny(w["strony"][cel], w["stan"][cel])
    else:
        obrona = w["strony"][cel]["odpornosc"]
    return max(surowe * STALE["min_czesc_po_obronie"], surowe - obrona)


def przyjmij(w, cel, obrazenia):
    # najpierw tarcze pochlaniajace (w kolejnosci nalozenia), reszta schodzi z zycia
    s = w["stan"][cel]
    reszta = obrazenia
    pochloniete = 0
    for ef in s["efekty"]:
        if ef["typ"] == "tarcza" and reszta > 0 and ef["zostalo"] > 0:
            ile = min(ef["zostalo"], reszta)
            ef["zostalo"] = ef["zostalo"] - ile
            reszta = reszta - ile
            pochloniete = pochloniete + ile
    s["hp"] = max(0, s["hp"] - reszta)
    return reszta, pochloniete


def zdarzenie(w, typ, kto, cel, trwa, pola):
    z = {
        "typ": typ, "kto": kto, "cel": cel,
        "obrazenia": 0, "pochloniete": 0, "rodzaj": "", "umiejetnosc": "", "efekt": "",
        "krytyk": False, "wartosc": 0, "tury": 0,
        "t": w["czas"] / 100, "trwa": trwa / 100,
    }
    for k in ("obrazenia", "pochloniete", "rodzaj", "umiejetnosc", "efekt", "krytyk", "wartosc", "tury"):
        if k in pola:
            z[k] = pola[k]
    z["hp_gracz"] = w["stan"]["gracz"]["hp"]
    z["hp_wrog"] = w["stan"]["wrog"]["hp"]
    w["czas"] = w["czas"] + trwa
    w["dziennik"].append(z)
    return z


def usun_zuzyte_tarcze(w, cel):
    s = w["stan"][cel]
    if s["hp"] <= 0:
        return  # walka i tak sie konczy; po nokaucie nie ma juz zdarzen
    zostaja = []
    for ef in s["efekty"]:
        if ef["typ"] == "tarcza" and ef["zostalo"] <= 0:
            zdarzenie(w, "efekt_koniec", cel, cel, STALE["czasy"]["efekt_koniec"], {"efekt": ef["id"]})
        else:
            zostaja.append(ef)
    s["efekty"] = zostaja


def naloz_efekt(w, zrodlo, cel, id_efektu, moc):
    E = EFEKTY[id_efektu]
    A = w["strony"][zrodlo]
    nowy = {"id": id_efektu, "typ": E["typ"], "trwa": E["trwa"], "od_tury": w["tura"],
            "wartosc": E.get("wartosc", 0), "tick": 0, "zostalo": 0, "rodzaj": E["rodzaj"]}
    pokaz = 0
    if E["typ"] == "obrazenia_w_czasie":
        nowy["tick"] = max(1, zaokraglij(A["cios"] * E["udzial"] * moc))
        pokaz = nowy["tick"]
    elif E["typ"] == "tarcza":
        nowy["zostalo"] = max(1, zaokraglij(A["cios"] * E["udzial"] * moc))
        pokaz = nowy["zostalo"]
    else:
        pokaz = zaokraglij(nowy["wartosc"] * 100)
    s = w["stan"][cel]
    podmieniony = False
    for i in range(len(s["efekty"])):
        if s["efekty"][i]["id"] == id_efektu:
            s["efekty"][i] = nowy  # ten sam efekt nie kumuluje sie — odswieza sile i czas
            podmieniony = True
    if not podmieniony:
        s["efekty"].append(nowy)
    zdarzenie(w, "efekt_nalozony", zrodlo, cel, STALE["czasy"]["efekt_nalozony"],
              {"efekt": id_efektu, "wartosc": pokaz, "tury": nowy["trwa"]})


def zwykly_cios(w, kto, cel):
    A = w["strony"][kto]
    D = w["strony"][cel]
    # zawsze piec rzutow w tej samej kolejnosci
    r_rozrzut, r_unik, r_blok, r_kryt, r_zakl = w["los"](), w["los"](), w["los"](), w["los"](), w["los"]()
    rozrzut = STALE["rozrzut_min"] + STALE["rozrzut_zakres"] * r_rozrzut
    if r_unik < D["unik"]:
        typ = "unik"
    elif r_blok < D["blok"]:
        typ = "blok"
    elif r_kryt < A["krytyk"]:
        typ = "krytyk"
    else:
        typ = "cios"
    if typ == "unik":
        zdarzenie(w, "unik", kto, cel, STALE["czasy"]["unik"], {"rodzaj": A["rodzaj_ciosu"]})
        return
    surowe = A["cios"] * rozrzut * wzmocnienie(w["stan"][kto])
    if typ == "krytyk":
        surowe = surowe * A["mnoznik_krytyka"]
    wynik = po_obronie(w, surowe, A["rodzaj_ciosu"], cel)
    if typ == "blok":
        wynik = wynik * STALE["czesc_przez_blok"]
    obrazenia = max(1, zaokraglij(wynik))
    reszta, pochloniete = przyjmij(w, cel, obrazenia)
    zdarzenie(w, typ, kto, cel, STALE["czasy"][typ],
              {"obrazenia": reszta, "pochloniete": pochloniete, "rodzaj": A["rodzaj_ciosu"], "krytyk": typ == "krytyk"})
    usun_zuzyte_tarcze(w, cel)
    if w["stan"][cel]["hp"] > 0 and A["zaklecie"] != "" and typ != "blok":
        z = ZAKLECIA[A["zaklecie"]]
        if r_zakl < z["szansa"]:
            naloz_efekt(w, kto, cel, z["efekt"], 1)


def uzyj_umiejetnosci(w, kto, cel, id_um):
    U = UMIEJETNOSCI[id_um]
    A = w["strony"][kto]
    # zawsze cztery rzuty + jeden na kazdy efekt, w tej samej kolejnosci
    r_rozrzut, r_unik, r_blok, r_kryt = w["los"](), w["los"](), w["los"](), w["los"]()
    r_efekty = []
    for _ in U["efekty"]:
        r_efekty.append(w["los"]())
    if U["cel"] == "sam":
        zdarzenie(w, "umiejetnosc", kto, kto, U["czas"], {"umiejetnosc": id_um})
        for i in range(len(U["efekty"])):
            wpis = U["efekty"][i]
            if r_efekty[i] < wpis["szansa"]:
                naloz_efekt(w, kto, kto, wpis["efekt"], A["moc"])
        return
    D = w["strony"][cel]
    # umiejetnosc na przeciwnika to atak jak kazdy inny: mozna jej uniknac i przyjac ja na tarcze
    if r_unik < D["unik"]:
        zdarzenie(w, "unik", kto, cel, U["czas"], {"umiejetnosc": id_um, "rodzaj": U["rodzaj"]})
        return
    zablokowana = r_blok < D["blok"]
    reszta, pochloniete, krytyk = 0, 0, False
    if U["mnoznik"] > 0:
        rozrzut = STALE["rozrzut_min"] + STALE["rozrzut_zakres"] * r_rozrzut
        surowe = A["cios"] * U["mnoznik"] * A["moc"] * rozrzut * wzmocnienie(w["stan"][kto])
        krytyk = not zablokowana and r_kryt < A["krytyk"] + U["premia_krytyka"]
        if krytyk:
            surowe = surowe * A["mnoznik_krytyka"]
        wynik = po_obronie(w, surowe, U["rodzaj"], cel)
        if zablokowana:
            wynik = wynik * STALE["czesc_przez_blok"]
        reszta, pochloniete = przyjmij(w, cel, max(1, zaokraglij(wynik)))
    zdarzenie(w, "blok" if zablokowana else "umiejetnosc", kto, cel, U["czas"],
              {"umiejetnosc": id_um, "obrazenia": reszta, "pochloniete": pochloniete,
               "rodzaj": U["rodzaj"], "krytyk": krytyk})
    usun_zuzyte_tarcze(w, cel)
    if w["stan"][cel]["hp"] > 0 and not zablokowana:
        for i in range(len(U["efekty"])):
            wpis = U["efekty"][i]
            if r_efekty[i] < wpis["szansa"]:
                naloz_efekt(w, kto, cel, wpis["efekt"], A["moc"])


def akcja(w, kto, cel):
    """PROPOZYCJA mechanizmu umiejetnosci w walce automatycznej: kazda umiejetnosc w slocie ma odnowienie N
    wlasnych akcji; na swojej turze postac odlicza wszystkie sloty o 1 i uzywa PIERWSZEJ gotowej (licznik <= 0)
    w kolejnosci slotow ZAMIAST zwyklego ciosu; uzyta wraca do N. Pierwszy raz umiejetnosc odpala sie w N-tej akcji."""
    A = w["strony"][kto]
    s = w["stan"][kto]
    for i in range(len(A["umiejetnosci"])):
        s["liczniki"][i] = s["liczniki"][i] - 1
    wybrana = -1
    for i in range(len(A["umiejetnosci"])):
        if wybrana == -1 and s["liczniki"][i] <= 0:
            wybrana = i
    if wybrana != -1:
        id_um = A["umiejetnosci"][wybrana]
        s["liczniki"][wybrana] = UMIEJETNOSCI[id_um]["odnowienie"]
        uzyj_umiejetnosci(w, kto, cel, id_um)
    else:
        zwykly_cios(w, kto, cel)


def tykniecia(w, kto):
    # obrazenia rozlozone w czasie (trucizna, podpalenie, krwawienie) na poczatku tury nosiciela;
    # omijaja Pancerz i odpornosc, ale pochlania je tarcza
    s = w["stan"][kto]
    for ef in s["efekty"]:
        if ef["typ"] == "obrazenia_w_czasie" and s["hp"] > 0:
            reszta, pochloniete = przyjmij(w, kto, ef["tick"])
            zdarzenie(w, "efekt_tick", kto, kto, STALE["czasy"]["efekt_tick"],
                      {"efekt": ef["id"], "obrazenia": reszta, "pochloniete": pochloniete, "rodzaj": ef["rodzaj"]})
    usun_zuzyte_tarcze(w, kto)


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
    liczniki = []
    for u in walczacy["umiejetnosci"]:
        liczniki.append(UMIEJETNOSCI[u]["odnowienie"])
    return {"hp": walczacy["zycie"], "efekty": [], "liczniki": liczniki}


def opis_strony(walczacy):
    return {"nazwa": walczacy["nazwa"], "rodzaj": walczacy["rodzaj"], "id": walczacy["id"], "ranga": walczacy["ranga"],
            "poziom": walczacy["poziom"], "zycie": walczacy["zycie"]}


def symuluj(gracz, przeciwnik, ziarno):
    """symuluj(gracz, przeciwnik, ziarno) -> walka (dziennik v2). Gracz: opis postaci; przeciwnik:
    {"potwor": id, "poziom": n} albo {"postac": opis postaci} (Arena, test lustrzany)."""
    sprawdz_postac(gracz, "gracz")
    A = wartosci_postaci(gracz)
    B = wartosci_przeciwnika(przeciwnik)
    # tylko calkowite ziarno w [0, 2^31): powyzej 2^53 Luau (liczby double) i Python (dokladne int) licza
    # reszte z dzielenia inaczej i dalyby rozne walki — takie ziarno odrzucamy czytelnym bledem
    if not calkowita(ziarno) or ziarno < 0 or ziarno >= ZIARNO_GRANICA:
        blad("ziarno musi byc liczba calkowita od 0 do %d" % (ZIARNO_GRANICA - 1))
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
            if w["stan"]["gracz"]["hp"] * B["zycie"] >= w["stan"]["wrog"]["hp"] * A["zycie"]:
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
        if ma_efekt(w["stan"][kto], "spowolnienie"):
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
    ap = argparse.ArgumentParser(description="Jedna walka silnika v2 (JSON)")
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
