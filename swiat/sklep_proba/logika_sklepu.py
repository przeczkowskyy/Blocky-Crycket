# -*- coding: utf-8 -*-
"""Lustro w Pythonie modułu zrodla/LogikaSklepu.luau (te same nazwy w snake_case, te same zaokrąglenia i teksty).

Czysta strona sklepu: układ okna z rozmiaru ekranu, teksty stanów i odmów, grupowanie oferty po stopniach. Sklep NIE
decyduje o kupnie — robi to kowal (swiat/kowal_proba, LogikaKowala.kup); tutaj jest tylko to, co pokazuje okno.
D = dane z dane.py (te same klucze co DaneSklepu.luau). „oferta” = lista wierszy z KowalProba/Sygnaly/Sklep:
    { id, nazwa, slot, slotNazwa, stopien, nrStopnia, cena, poziom, stan, brakuje, ulepszenie, staty }
"""
import math

STANY = ("kup", "za_drogie", "za_niski_poziom", "masz", "zalozone")


def _zakres(v, lo, hi):
    return max(lo, min(hi, v))


def uklad(D, W, H):
    """Rozmiary okna w pikselach ekranu W × H (telefon 667 × 375 i duży ekran): okno, nagłówek, zakładki stopni,
    wiersz listy (lista się przewija), przycisk w wierszu, pasek komunikatu, rozmiar tekstu."""
    U = D["ui"]
    szer = math.floor(min(W * (U["okno_x"][1] - U["okno_x"][0]), U["okno_maks_px"][0]))
    wys = math.floor(min(H * (U["okno_y"][1] - U["okno_y"][0]), U["okno_maks_px"][1]))
    naglowek = _zakres(math.floor(wys * 0.1), U["naglowek_px"][0], U["naglowek_px"][1])
    zakladka = _zakres(math.floor(wys * 0.1), U["zakladka_px"][0], U["zakladka_px"][1])
    wiersz = _zakres(math.floor(wys * 0.115), U["wiersz_px"][0], U["wiersz_px"][1])
    komunikat = _zakres(math.floor(wys * 0.06), U["komunikat_px"][0], U["komunikat_px"][1])
    lista = wys - naglowek - zakladka - komunikat
    tekst = _zakres(math.floor(wiersz * 0.3), U["tekst_min"], U["tekst_maks"])
    return {"x": math.floor((W - szer) / 2), "y": math.floor(H * U["okno_y"][0]), "szer": szer, "wys": wys,
            "naglowek": naglowek, "zakladka": zakladka, "wiersz": wiersz, "komunikat": komunikat, "lista": lista,
            "przycisk": wiersz - 4, "przyciskSzer": math.floor(szer * U["przycisk_szer"]), "zamknij": naglowek,
            "tekst": tekst, "widoczne": math.floor(lista / wiersz * 10) / 10}


def grupy(D, oferta):
    """Oferta → stopnie w kolejności danych (startowy, leśny, bagienny, Dżungli) z wierszami w kolejności oferty."""
    w = []
    for s in D["stopnie"]:
        wiersze = [o for o in oferta if o["stopien"] == s["id"]]
        w.append({"id": s["id"], "nazwa": s["nazwa"], "kolor": s["kolor"], "wiersze": wiersze,
                  "doKupienia": sum(1 for o in wiersze if o["stan"] == "kup")})
    return w


def pierwsza_zakladka(D, oferta):
    """Zakładka na start: pierwszy stopień, w którym coś da się kupić; inaczej najwyższy z posiadanym przedmiotem;
    inaczej pierwszy."""
    g = grupy(D, oferta)
    for s in g:
        if s["doKupienia"] > 0:
            return s["id"]
    wynik = g[0]["id"] if g else ""
    for s in g:
        if any(o["stan"] in ("masz", "zalozone") for o in s["wiersze"]):
            wynik = s["id"]
    return wynik


def wiersz(D, o):
    """Teksty jednego wiersza okna: nazwa (z poziomem ulepszenia, gdy posiadany), opis (slot · statystyki), wymagania
    (poziom · cena), stan po polsku i przycisk ({tekst, akcja} albo brak)."""
    T = D["teksty"]
    posiadany = o["stan"] in ("masz", "zalozone")
    nazwa = o["nazwa"]
    if posiadany and o["ulepszenie"] > 0:
        nazwa = "%s %s" % (nazwa, T["ulepszenie"] % o["ulepszenie"])
    staty = o["staty"] if o["staty"] != "" else T["bez_dodatkow"]
    cena = (T["cena"] % o["cena"]) if o["cena"] > 0 else T["cena_zero"]
    w = {"id": o["id"], "nazwa": nazwa, "opis": "%s · %s" % (o["slotNazwa"], staty),
         "wymaga": "%s · %s" % (T["wymaga"] % o["poziom"], cena), "stan": T["stan_" + o["stan"]], "akcja": "",
         "przycisk": "", "aktywny": False, "powod": ""}
    if o["stan"] == "kup":
        w["akcja"], w["przycisk"], w["aktywny"] = "kup", T["kup"], True
    elif o["stan"] == "masz":
        w["akcja"], w["przycisk"], w["aktywny"] = "zaloz", T["zaloz"], True
    elif o["stan"] == "za_drogie":
        w["przycisk"], w["powod"] = T["kup"], T["za_malo_zlota"] % o["brakuje"]
    elif o["stan"] == "za_niski_poziom":
        w["przycisk"], w["powod"] = T["kup"], T["za_niski_poziom"] % o["poziom"]
    return w


def naglowek(D, zloto, poziom):
    T = D["teksty"]
    return {"tytul": T["tytul"], "zloto": T["zloto"] % zloto, "poziom": T["poziom"] % poziom}


_MAPA = {"masz": "masz", "inna_klasa": "inna_klasa", "czesc_zbroi": "czesc_zbroi",
         "nieznany_przedmiot": "nieznany_przedmiot", "nie_masz": "nie_masz", "nie_zalozono": "nie_zalozono",
         "brak_przymierzalni": "nie_zalozono", "daleko": "podejdz", "za_szybko": "za_szybko",
         "brak_stanu": "nieczynny", "nieczynny": "nieczynny"}


def komunikat(D, akcja, r):
    """Odpowiedź wejścia kowala (albo odmowa serwera sklepu) → pełne zdanie dla gracza."""
    T = D["teksty"]
    if not isinstance(r, dict):
        return T["nieczynny"]
    if r.get("ok") is True:
        nazwa = r.get("nazwa") if isinstance(r.get("nazwa"), str) else ""
        if akcja == "kup":
            return (T["ok_kup_zalozony"] if r.get("zalozony") is True else T["ok_kup_schowany"]) % nazwa
        if akcja == "zaloz":
            return T["ok_zaloz"] % nazwa
        return ""
    powod = r.get("powod")
    ile = r.get("brakuje") if isinstance(r.get("brakuje"), (int, float)) and not isinstance(r.get("brakuje"), bool) else 0
    if powod == "za_malo_zlota":
        return T["za_malo_zlota"] % ile
    if powod == "za_niski_poziom":
        wymagany = r.get("wymagany")
        return T["za_niski_poziom"] % (wymagany if isinstance(wymagany, (int, float)) else ile)
    return T[_MAPA.get(powod, "blad")]
