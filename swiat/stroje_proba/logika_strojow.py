# -*- coding: utf-8 -*-
"""Lustro zrodla/LogikaStrojow.luau w Pythonie (testy: te same wyniki w interpreterze luau_mini i tutaj).

Strój = lista id przedmiotów z katalogu (swiat/postacie/przedmioty.json) założonych na bohatera danej klasy.
Zasady (PROJEKT.md, „przyjęte, do zmiany”):
- przedmiot pasuje do klasy, gdy klasa jest w jego `klasy` (D.dobor == "klasa") albo typ ciała się zgadza
  (D.dobor == "cialo": `cialo` przedmiotu = ciało klasy albo "dowolne");
- spodnie (`czesc_od`): przy D.spodnie == "czesc_zbroi" są częścią zbroi — nie wybiera się ich osobno, zakładają się
  i zdejmują razem z nią; przy "osobny_slot" mają własny slot okna „Legs”;
- w jednym slocie okna najwyżej jeden przedmiot; dwie powłoki na jednej kości = błąd (EKWIPUNEK.md pkt 4);
- wynik zawsze w kolejności K.przedmioty (strój odniesienia walki, potem reszta).
Funkcje zwracają (ok, wynik) — wynik albo powód odmowy (napis z POWODY).
"""

POWODY = ("zla_klasa", "zly_stroj", "nieznany_przedmiot", "przedmiot_innej_klasy", "czesc_bez_calosci",
          "czesc_zbroi", "dwa_w_slocie", "dwie_powloki", "zly_slot", "nieznany_zestaw")
MAKS_PRZEDMIOTOW = 24


def dostepny(D, klasa, i):
    K = D["klasy"].get(klasa)
    P = D["przedmioty"].get(i)
    if K is None or P is None:
        return False
    if D["dobor"] == "cialo":
        return P["cialo"] == K["cialo"] or P["cialo"] == "dowolne"
    return klasa in P["klasy"]


def slot_okna(D, i):
    P = D["przedmioty"][i]
    if P["czescOd"] and D["spodnie"] == "osobny_slot":
        return "Legs"
    return P["slot"]


def wybieralny(D, klasa, i):
    """Czy przedmiot ma własny wybór w oknie (część zbroi przy „czesc_zbroi” — nie)."""
    if not dostepny(D, klasa, i):
        return False
    return not (D["przedmioty"][i]["czescOd"] and D["spodnie"] == "czesc_zbroi")


def _kolejnosc(D, klasa):
    K = D["klasy"][klasa]
    lista = list(K["przedmioty"])
    if D["dobor"] == "cialo":
        for k in D["kolejnoscKlas"]:
            if k != klasa:
                lista += list(D["klasy"][k]["przedmioty"])
    return lista


def oferta(D, klasa):
    """[{slot, nazwa, przedmioty: [id…]}] — sloty okna (kolejność D.sloty) z przedmiotami do wyboru."""
    if klasa not in D["klasy"]:
        return []
    wynik = []
    lista = _kolejnosc(D, klasa)
    for s in D["sloty"]:
        ids = [i for i in lista if wybieralny(D, klasa, i) and slot_okna(D, i) == s["id"]]
        if ids:
            wynik.append({"slot": s["id"], "nazwa": s["nazwa"], "przedmioty": ids})
    return wynik


def normalizuj(D, klasa, ids):
    """Sprawdza strój i doprowadza go do postaci kanonicznej (bez powtórzeń, z częściami zbroi, w kolejności)."""
    if klasa not in D["klasy"]:
        return False, "zla_klasa"
    if not isinstance(ids, list) or len(ids) > MAKS_PRZEDMIOTOW:
        return False, "zly_stroj"
    zbior = set()
    for i in ids:
        if not isinstance(i, str):
            return False, "zly_stroj"
        if i not in D["przedmioty"]:
            return False, "nieznany_przedmiot"
        if not dostepny(D, klasa, i):
            return False, "przedmiot_innej_klasy"
        zbior.add(i)
    if D["spodnie"] == "czesc_zbroi":
        for i in list(zbior):
            c = D["przedmioty"][i]["czescOd"]
            if c and c not in zbior:
                return False, "czesc_bez_calosci"
        for i in _kolejnosc(D, klasa):
            c = D["przedmioty"][i]["czescOd"]
            if c and c in zbior and dostepny(D, klasa, i):
                zbior.add(i)
    sloty, kosci = {}, {}
    for i in _kolejnosc(D, klasa):
        if i not in zbior:
            continue
        P = D["przedmioty"][i]
        if not (P["czescOd"] and D["spodnie"] == "czesc_zbroi"):
            s = slot_okna(D, i)
            if s in sloty:
                return False, "dwa_w_slocie"
            sloty[s] = i
        for seg in P["segmenty"]:
            if seg["zakrywa"]:
                if seg["kosc"] in kosci:
                    return False, "dwie_powloki"
                kosci[seg["kosc"]] = i
    return True, [i for i in _kolejnosc(D, klasa) if i in zbior]


def _bez_slotu(D, stroj, slot):
    """Strój bez przedmiotów slotu okna (przy „czesc_zbroi” razem z ich częściami zbroi)."""
    czesci = D["spodnie"] == "czesc_zbroi"
    zdjete = {i for i in stroj if not (D["przedmioty"][i]["czescOd"] and czesci) and slot_okna(D, i) == slot}
    return [i for i in stroj if i not in zdjete and not (czesci and D["przedmioty"][i]["czescOd"] in zdjete)]


def zaloz(D, klasa, stroj, i):
    ok, st = normalizuj(D, klasa, stroj)
    if not ok:
        return ok, st
    if not isinstance(i, str) or i not in D["przedmioty"]:
        return False, "nieznany_przedmiot"
    if not dostepny(D, klasa, i):
        return False, "przedmiot_innej_klasy"
    if not wybieralny(D, klasa, i):
        return False, "czesc_zbroi"
    return normalizuj(D, klasa, _bez_slotu(D, st, slot_okna(D, i)) + [i])


def zdejmij(D, klasa, stroj, slot):
    ok, st = normalizuj(D, klasa, stroj)
    if not ok:
        return ok, st
    if not isinstance(slot, str) or slot not in [s["id"] for s in D["sloty"]]:
        return False, "zly_slot"
    return normalizuj(D, klasa, _bez_slotu(D, st, slot))


def zestaw(D, klasa, nazwa):
    K = D["klasy"].get(klasa)
    if K is None:
        return False, "zla_klasa"
    z = next((z for z in K["zestawy"] if z["id"] == nazwa), None)
    if z is None:
        return False, "nieznany_zestaw"
    return normalizuj(D, klasa, list(z["przedmioty"]))


def plan(D, klasa, ids):
    """Co złożyć: {przedmioty: [id…], zakryte: {kość}, ukryte: {znacznik}}."""
    ok, st = normalizuj(D, klasa, ids)
    if not ok:
        return ok, st
    zakryte, ukryte = set(), set()
    for i in st:
        P = D["przedmioty"][i]
        for seg in P["segmenty"]:
            if seg["zakrywa"]:
                zakryte.add(seg["kosc"])
        ukryte.update(P["ukrywa"])
    return True, {"przedmioty": st, "zakryte": zakryte, "ukryte": ukryte}


def na_napis(ids):
    return ",".join(ids)


def z_napisu(s):
    """Atrybut gracza -> lista id (None = brak stroju: dawny szablon walki)."""
    if s is None:
        return None
    if not isinstance(s, str):
        return None
    return [x for x in s.split(",") if x != ""]
