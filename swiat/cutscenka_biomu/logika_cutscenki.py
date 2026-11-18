# -*- coding: utf-8 -*-
"""Lustro zrodla/LogikaCutscenki.luau w Pythonie (te same funkcje i wzory). Test bez Studio porównuje oba pliki
wywołanie po wywołaniu (Luau wykonuje interpreter tools/walka/luau_mini.py). Zmieniasz wzór tutaj — zmień go tam."""
import math


def w_prostokacie(x, z, r):
    return r["x1"] <= x <= r["x2"] and r["z1"] <= z <= r["z2"]


def biom_punktu(biomy, x, y, z):
    for i, b in enumerate(biomy, 1):
        if y > b["yMin"] and w_prostokacie(x, z, b["prostokat"]):
            return i
    return 0


def _catmull(p0, p1, p2, p3, f):
    return 0.5 * (2 * p1 + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (-p0 + 3 * p1 - 3 * p2 + p3) * f * f * f)


def krzywa(tab, n, krok, t):
    q = t / krok
    if q <= 0:
        return (tab[0], tab[1], tab[2])
    if q >= n - 1:
        return (tab[3 * n - 3], tab[3 * n - 2], tab[3 * n - 1])
    i = int(math.floor(q))
    f = q - i
    a, b, c, d = 3 * max(i - 1, 0), 3 * i, 3 * (i + 1), 3 * min(i + 2, n - 1)
    return tuple(_catmull(tab[a + k], tab[b + k], tab[c + k], tab[d + k], f) for k in range(3))


def widocznosc(t, od, pelna_od, pelna_do, do_kiedy):
    if t <= od or t >= do_kiedy:
        return 0
    if t < pelna_od:
        return (t - od) / (pelna_od - od)
    if t <= pelna_do:
        return 1
    return (do_kiedy - t) / (do_kiedy - pelna_do)


def wstrzas(t, od, czas, sila):
    if t < od or t >= od + czas or czas <= 0:
        return 0
    f = 1 - (t - od) / czas
    return sila * f * f


def _ogranicz(x, a, b):
    return min(b, max(a, x))


def uklad(w, h, lewo, gora, prawo, dol, k):
    m = k["margines"]
    pas = math.floor(h * k["pasy"] + 0.5)
    pw = _ogranicz(w * k["pomin"]["szer"], k["pomin"]["minSzer"], k["pomin"]["maksSzer"])
    ph = _ogranicz(h * k["pomin"]["wys"], k["pomin"]["minWys"], k["pomin"]["maksWys"])
    pomin = {"x": w - prawo - m - pw, "y": h - dol - m - ph, "w": pw, "h": ph,
             "tekst": max(k["pomin"]["tekstMin"], math.floor(ph * k["pomin"]["tekst"]))}
    szer = w - lewo - prawo - 2 * m
    tn = _ogranicz(h * k["nazwa"]["wys"], k["nazwa"]["min"], k["nazwa"]["maks"])
    nazwa = {"x": lewo + m, "y": math.floor(h * k["nazwa"]["y"] - tn / 2), "w": szer, "h": tn, "tekst": math.floor(tn * 0.9)}
    td = _ogranicz(h * k["nadtytul"]["wys"], k["nadtytul"]["min"], k["nadtytul"]["maks"])
    nadtytul = {"x": lewo + m, "y": nazwa["y"] - td - 4, "w": szer, "h": td, "tekst": math.floor(td)}
    tp = _ogranicz(h * k["podpis"]["wys"], k["podpis"]["min"], k["podpis"]["maks"])
    wolne = pomin["x"] - m - (lewo + m)
    podpis = {"x": lewo + m, "y": min(h - pas, pomin["y"]) - tp - 8, "w": wolne, "h": tp, "tekst": math.floor(tp)}
    ts = _ogranicz(h * k["straznik"]["wys"], k["straznik"]["min"], k["straznik"]["maks"])
    straznik = {"x": lewo + m, "y": min(h - pas, h - dol - m) - ts - 6, "w": wolne, "h": ts, "tekst": math.floor(ts * 0.9)}
    return {"pas": pas, "pomin": pomin, "nazwa": nazwa, "nadtytul": nadtytul, "podpis": podpis, "straznik": straznik}


def nowy_stan():
    return {"faza": "brak", "id": 0, "biom": "", "wymuszony": False, "od": 0, "doKiedy": 0, "nastepny": 0, "wolnyOd": 0,
            "proby": 0, "wynik": ""}


def _zakoncz(s, akcje, wynik):
    akcje.append("odblokuj")
    s["faza"] = "brak"
    s["wynik"] = wynik


def krok(s, w, teraz, k):
    """w: cel, wymus, postac, odpowiedz, strumienie, czas, koniec, pominieta, przerwij (brak klucza = nil)."""
    akcje = []
    f = s["faza"]
    wymus, cel = w.get("wymus"), w.get("cel")
    if f == "brak":
        biom = wymus if wymus is not None else cel
        if w.get("postac") and biom is not None and (wymus is not None or teraz >= s["wolnyOd"]):
            s["id"] += 1
            s["biom"] = biom
            s["wymuszony"] = wymus is not None
            s["faza"] = "uspokaja"
            s["od"] = teraz
            s["wynik"] = ""
        return akcje
    przerwij = w.get("przerwij")
    if przerwij is None and not w.get("postac"):
        przerwij = "postac"
    if przerwij is not None:
        if f != "uspokaja":
            akcje.append("przerwij")
        _zakoncz(s, akcje, przerwij)
        if przerwij == "reset":
            s["wolnyOd"] = teraz
        return akcje
    if f == "uspokaja":
        if teraz - s["od"] >= k["uspokojenie"]:
            if not s["wymuszony"] and cel != s["biom"]:
                s["faza"] = "brak"
                s["wynik"] = "wyszedl"
            else:
                s["faza"] = "pyta"
                s["od"] = teraz
                akcje += ["blokuj_walke", "pytaj"]
    elif f == "pyta":
        if w.get("odpowiedz") == "gotowe":
            s["faza"] = "laduje"
            s["od"] = teraz
            s["proby"] = 0
            akcje += ["widzial", "zakotwicz", "laduj"]
        elif w.get("odpowiedz") == "odmowa":
            _zakoncz(s, akcje, "odmowa")
            s["wolnyOd"] = teraz + k["ponowPoOdmowie"]
        elif teraz - s["od"] >= k["odpowiedz"]:
            s["proby"] += 1
            akcje.append("przerwij")
            if s["proby"] >= k["probMaks"]:
                akcje.append("poddaj")
                s["proby"] = 0
            _zakoncz(s, akcje, "cisza")
            s["wolnyOd"] = teraz + k["ponowPoCiszy"]
    elif f == "laduje":
        if w.get("strumienie", 0) <= 0 or teraz - s["od"] >= k["ladowanie"]:
            s["faza"] = "trwa"
            s["od"] = teraz
            s["doKiedy"] = teraz + w["czas"] + k["zapas"]
            s["nastepny"] = teraz + k["strumienCo"]
            akcje.append("start")
    elif f == "trwa":
        if w.get("koniec"):
            _zakoncz(s, akcje, "pominieta" if w.get("pominieta") else "koniec")
        elif teraz >= s["doKiedy"]:
            akcje.append("przerwij")
            _zakoncz(s, akcje, "czas")
        elif teraz >= s["nastepny"]:
            s["nastepny"] = teraz + k["strumienCo"]
            akcje.append("podtrzymaj")
    return akcje


_R = {"x1": 0, "x2": 10, "z1": -5, "z2": 5}
_BIOMY = [{"yMin": -30, "prostokat": _R}, {"yMin": -30, "prostokat": {"x1": 12, "x2": 20, "z1": -5, "z2": 5}}]
_TAB = [0, 0, 0, 10, 0, 0, 20, 10, 0, 20, 10, 0]

PRZYPADKI = [
    ("wProstokacie(5,0)", lambda: w_prostokacie(5, 0, _R), True),
    ("wProstokacie(11,0)", lambda: w_prostokacie(11, 0, _R), False),
    ("biomPunktu(5,0,0)", lambda: biom_punktu(_BIOMY, 5, 0, 0), 1),
    ("biomPunktu(15,0,0)", lambda: biom_punktu(_BIOMY, 15, 0, 0), 2),
    ("biomPunktu(11,0,0)", lambda: biom_punktu(_BIOMY, 11, 0, 0), 0),
    ("biomPunktu(5,-40,0)", lambda: biom_punktu(_BIOMY, 5, -40, 0), 0),
    ("krzywa(0).x", lambda: krzywa(_TAB, 4, 1, 0)[0], 0),
    ("krzywa(1).x", lambda: krzywa(_TAB, 4, 1, 1)[0], 10),
    ("krzywa(0.5).x", lambda: krzywa(_TAB, 4, 1, 0.5)[0], 4.375),
    ("krzywa(1.5).y", lambda: krzywa(_TAB, 4, 1, 1.5)[1], 5),
    ("krzywa(9).y", lambda: krzywa(_TAB, 4, 1, 9)[1], 10),
    ("krzywa(krok 0.5, t 0.5).x", lambda: krzywa(_TAB, 4, 0.5, 0.5)[0], 10),
    ("widocznosc(przed)", lambda: widocznosc(0, 0.1, 0.4, 1.5, 1.9), 0),
    ("widocznosc(wejscie)", lambda: widocznosc(0.25, 0.1, 0.4, 1.5, 1.9), 0.5),
    ("widocznosc(pelna)", lambda: widocznosc(1, 0.1, 0.4, 1.5, 1.9), 1),
    ("widocznosc(zejscie)", lambda: widocznosc(1.7, 0.1, 0.4, 1.5, 1.9), 0.5),
    ("widocznosc(po)", lambda: widocznosc(2, 0.1, 0.4, 1.5, 1.9), 0),
    ("wstrzas(przed)", lambda: wstrzas(1, 2, 1, 0.4), 0),
    ("wstrzas(start)", lambda: wstrzas(2, 2, 1, 0.4), 0.4),
    ("wstrzas(polowa)", lambda: wstrzas(2.5, 2, 1, 0.4), 0.1),
    ("wstrzas(po)", lambda: wstrzas(3, 2, 1, 0.4), 0),
]


def sprawdz_przypadki():
    bledy = []
    for opis, f, oczekiwane in PRZYPADKI:
        wynik = f()
        zgodne = wynik == oczekiwane
        if isinstance(wynik, (int, float)) and not isinstance(wynik, bool) and not isinstance(oczekiwane, bool):
            zgodne = abs(wynik - oczekiwane) < 1e-9
        if not zgodne:
            bledy.append("%s: %r zamiast %r" % (opis, wynik, oczekiwane))
    return not bledy, len(PRZYPADKI), bledy
