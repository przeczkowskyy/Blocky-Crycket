# -*- coding: utf-8 -*-
"""Lustro modułu zrodla/LogikaPasa.luau w Pythonie — te same funkcje (nazwy snake_case), ta sama kolejność argumentów,
te same wzory. Czysta logika: bez instancji, zegara i losowości; liczby, napisy, wartości logiczne, słowniki i listy.

Testy (testy/test_pasa.py) porównują te funkcje z planem (sprawdz_plan.py) i — gdy w repozytorium jest interpreter
tools/walka/luau_mini.py — wykonują ten sam zestaw wywołań na pliku Luau i porównują wyniki jeden do jednego.

Konwencje (takie same w Luau):
  • prostokąt w poziomie świata to słownik {"x1", "x2", "z1", "z2"} (x1 ≤ x2, z1 ≤ z2);
  • punkt przelotu to {"t": s, "poz": [x, y, z], "patrz": [x, y, z]} w układzie świata;
  • brama to {"x", "z1", "z2", "tolerancja", "glebokosc"}: linia bramy x, pas z1…z2, za bramą = x + tolerancja < X < x + glebokosc;
  • stan przelotu gracza to {"faza", "id", "od", "doKiedy", "nastepny", "wolnyOd"}; krok_przelotu go zmienia i zwraca
    listę akcji (napisów), które wykonuje serwer — kolejność akcji jest częścią umowy;
  • klucze słowników są takie same jak pola tabel w Luau (camelCase), bo testy podają te same dane obu stronom.
"""
import math


# ------------------------------------------------------------------------------------------------ prostokąty i mgła
def w_prostokacie(x, z, r):
    return r["x1"] <= x <= r["x2"] and r["z1"] <= z <= r["z2"]


def odleglosc_od_prostokata(x, z, r):
    """0 w środku; poza nim odległość w poziomie od najbliższego punktu brzegu."""
    dx = max(r["x1"] - x, 0, x - r["x2"])
    dz = max(r["z1"] - z, 0, z - r["z2"])
    return math.sqrt(dx * dx + dz * dz)


def waga_mgly(x, z, r, pas):
    """1 w prostokącie pasa, maleje liniowo do 0 w odległości `pas` od brzegu (łagodne wejście i wyjście)."""
    d = odleglosc_od_prostokata(x, z, r)
    if pas <= 0:
        return 1.0 if d <= 0 else 0.0
    return min(1.0, max(0.0, 1.0 - d / pas))


def krok_wagi(waga, cel, tempo, dt):
    """Waga idzie do celu najwyżej o tempo · dt (płynne przejście)."""
    k = tempo * dt
    if cel > waga:
        return min(cel, waga + k)
    return max(cel, waga - k)


# ------------------------------------------------------------------------------------------------ brama i ratunek
def za_brama(x, z, b):
    return b["z1"] <= z <= b["z2"] and b["x"] + b["tolerancja"] < x < b["x"] + b["glebokosc"]


def decyzja_bramy(x, z, uprawniony, b):
    """„cofnij”, gdy nieuprawniony gracz jest za bramą; inaczej „wolno”."""
    if not uprawniony and za_brama(x, z, b):
        return "cofnij"
    return "wolno"


def potrzeba_ratunku(x, y, z, r):
    """Gracz spadł poniżej r["yMin"] w pudle r (las-pas i okolice) — trzeba go przenieść."""
    return y < r["yMin"] and w_prostokacie(x, z, r)


def cel_ratunku(x, z, uprawniony, b):
    """Dokąd przenieść spadającego: za bramą — uprawnionego za bramę, nieuprawnionego przed bramę; inaczej przybycie."""
    if b["z1"] <= z <= b["z2"] and x > b["x"]:
        return "za_brama" if uprawniony else "przed_brama"
    return "przybycie"


def otwiera_brame(info):
    """Wynik walki z SerwerPotworow (Sygnaly/WynikWalki) otwiera bramę tylko po wygranej ze Strażnikiem."""
    return isinstance(info, dict) and info.get("straznik") is True and info.get("wynik") == "wygrana"


# ------------------------------------------------------------------------------------------------ krzywa przelotu
def _rowne(a, b):
    return a[0] == b[0] and a[1] == b[1] and a[2] == b[2]


def _krzywa(punkty, t, pole):
    """Catmull-Rom przez punkty[i][pole] w czasach punkty[i]["t"] — dokładnie jak sprawdz_plan.krzywa_kamery:
    odcinek o tych samych końcach to postój; sąsiad za postojem albo za końcem listy = koniec odcinka."""
    n = len(punkty)
    if n == 0:
        return 0.0, 0.0, 0.0
    if n == 1 or t <= punkty[0]["t"]:
        p = punkty[0][pole]
        return float(p[0]), float(p[1]), float(p[2])
    for i in range(n - 1):
        a, b = punkty[i], punkty[i + 1]
        dt = b["t"] - a["t"]
        if dt > 0 and (t <= b["t"] or i == n - 2):
            f = min(1.0, max(0.0, (t - a["t"]) / dt))
            p1, p2 = a[pole], b[pole]
            if _rowne(p1, p2):
                return float(p1[0]), float(p1[1]), float(p1[2])
            p0 = punkty[i - 1][pole] if i > 0 and not _rowne(punkty[i - 1][pole], p1) else p1
            p3 = punkty[i + 2][pole] if i + 2 < n and not _rowne(punkty[i + 2][pole], p2) else p2
            wynik = []
            for j in range(3):
                wynik.append(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * f + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * f * f
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * f * f * f))
            return wynik[0], wynik[1], wynik[2]
    p = punkty[-1][pole]
    return float(p[0]), float(p[1]), float(p[2])


def punkt_krzywej(punkty, t):
    """Położenie kamery w chwili t (s od startu przelotu)."""
    return _krzywa(punkty, t, "poz")


def cel_krzywej(punkty, t):
    """Punkt, na który kamera patrzy w chwili t (ta sama krzywa po polach „patrz”)."""
    return _krzywa(punkty, t, "patrz")


def czas_krzywej(punkty):
    return float(punkty[-1]["t"]) if punkty else 0.0


def punkt_wyprzedzenia(punkty, t, wyprzedzenie):
    """Gdzie kamera będzie za `wyprzedzenie` s (do prośby o wczytanie mapy przed kamerą)."""
    return punkt_krzywej(punkty, min(czas_krzywej(punkty), t + wyprzedzenie))


# ------------------------------------------------------------------------------------------------ przelot: flaga i fazy
def czy_zaczac_przelot(widzial, faza, w_pasie, klient_gotowy, teraz, wolny_od):
    """Pierwsze wejście: gracz w lesie, nie widział przelotu, nic nie trwa, klient gotowy, minął czas wolny_od."""
    return (not widzial) and faza == "brak" and w_pasie and klient_gotowy and teraz >= wolny_od


def termin_przelotu(start, czas, zapas):
    """Najpóźniej wtedy serwer kończy przelot sam (klient nie odpowiedział)."""
    return start + czas + zapas


def nowy_stan_przelotu():
    return {"faza": "brak", "id": 0, "od": 0.0, "doKiedy": 0.0, "nastepny": 0.0, "wolnyOd": 0.0}


def _zakoncz(s, akcje, teraz, przerwij, k):
    akcje.append("odblokuj")
    if przerwij == "odmowa":
        akcje.append("zapomnij")
        s["wolnyOd"] = teraz + k["ponowPoOdmowie"]
    elif przerwij == "reset":
        akcje.append("zapomnij")
        s["wolnyOd"] = teraz
    s["faza"] = "brak"


def krok_przelotu(s, w, teraz, k):
    """Jeden krok automatu przelotu jednego gracza (serwer woła go co tyknięcie).

    s — stan (zmieniany w miejscu); w — wejście: {"widzial", "wPasie", "gotowy", "postac", "strumienie", "koniec",
    "przerwij"}; k — stałe: {"uspokojenie", "ladowanie", "czas", "zapas", "strumienCo", "ponowPoOdmowie"}.
    Fazy: brak → uspokaja (postać staje po teleporcie) → laduje (zablokowana, mapa wczytuje się wokół trasy) → trwa
    (klient gra przelot) → brak. Flaga „widział” jest ustawiana NA STARCIE, więc przelot nigdy się nie zapętla (także
    po błędzie albo braku odpowiedzi klienta); kasują ją tylko odmowa klienta (np. trwa walka — ponowienie za 5 s) i
    uchwyt testowy „odtwórz ponownie” (reset)."""
    akcje = []
    f = s["faza"]
    if f == "brak":
        if w["postac"] and czy_zaczac_przelot(w["widzial"], f, w["wPasie"], w["gotowy"], teraz, s["wolnyOd"]):
            s["id"] += 1
            s["faza"] = "uspokaja"
            s["od"] = teraz
            akcje.append("widzial")
        return akcje
    przerwij = w["przerwij"]
    if przerwij is None and not w["postac"]:
        przerwij = "postac"
    if przerwij is not None:
        if f in ("laduje", "trwa"):
            akcje.append("przerwij")
        _zakoncz(s, akcje, teraz, przerwij, k)
        return akcje
    if f == "uspokaja":
        if teraz - s["od"] >= k["uspokojenie"]:
            s["faza"] = "laduje"
            s["od"] = teraz
            akcje.extend(["zablokuj", "przygotuj", "laduj"])
    elif f == "laduje":
        if w["strumienie"] <= 0 or teraz - s["od"] >= k["ladowanie"]:
            s["faza"] = "trwa"
            s["od"] = teraz
            s["doKiedy"] = termin_przelotu(teraz, k["czas"], k["zapas"])
            s["nastepny"] = teraz + k["strumienCo"]
            akcje.append("start")
    elif f == "trwa":
        if w["koniec"]:
            _zakoncz(s, akcje, teraz, None, k)
        elif teraz >= s["doKiedy"]:
            akcje.append("przerwij")
            _zakoncz(s, akcje, teraz, None, k)
        elif teraz >= s["nastepny"]:
            s["nastepny"] = teraz + k["strumienCo"]
            akcje.append("podtrzymaj")
    return akcje


# ------------------------------------------------------------------------------------------------ przypadki wzorcowe
# Te same wywołania i wyniki są w LogikaPasa.sprawdzPrzypadki() (Luau); test sprawdza zgodność obu list.
_R = {"x1": 0, "x2": 10, "z1": -5, "z2": 5}
_B = {"x": 100, "z1": -40, "z2": 40, "tolerancja": 1.5, "glebokosc": 200}
_RAT = {"x1": -100, "x2": 400, "z1": -60, "z2": 60, "yMin": -30}
_P = [{"t": 0, "poz": [0, 0, 0], "patrz": [10, 0, 0]}, {"t": 1, "poz": [10, 0, 0], "patrz": [20, 0, 0]},
      {"t": 2, "poz": [20, 10, 0], "patrz": [30, 0, 0]}, {"t": 3, "poz": [20, 10, 0], "patrz": [30, 0, 0]}]

PRZYPADKI = [
    ("wProstokacie(5,0)", lambda: w_prostokacie(5, 0, _R), True),
    ("wProstokacie(11,0)", lambda: w_prostokacie(11, 0, _R), False),
    ("wProstokacie(10,5)", lambda: w_prostokacie(10, 5, _R), True),
    ("odleglosc(13,9)", lambda: odleglosc_od_prostokata(13, 9, _R), 5.0),
    ("wagaMgly(5,0,pas 20)", lambda: waga_mgly(5, 0, _R, 20), 1.0),
    ("wagaMgly(20,0,pas 20)", lambda: waga_mgly(20, 0, _R, 20), 0.5),
    ("wagaMgly(40,0,pas 20)", lambda: waga_mgly(40, 0, _R, 20), 0.0),
    ("krokWagi(0,1,0.8,0.5)", lambda: krok_wagi(0, 1, 0.8, 0.5), 0.4),
    ("krokWagi(0.9,0,0.8,2)", lambda: krok_wagi(0.9, 0, 0.8, 2), 0.0),
    ("zaBrama(102,0)", lambda: za_brama(102, 0, _B), True),
    ("zaBrama(101,0)", lambda: za_brama(101, 0, _B), False),
    ("zaBrama(102,50)", lambda: za_brama(102, 50, _B), False),
    ("decyzjaBramy(110,0,nie)", lambda: decyzja_bramy(110, 0, False, _B), "cofnij"),
    ("decyzjaBramy(110,0,tak)", lambda: decyzja_bramy(110, 0, True, _B), "wolno"),
    ("decyzjaBramy(90,0,nie)", lambda: decyzja_bramy(90, 0, False, _B), "wolno"),
    ("potrzebaRatunku(50,-40,0)", lambda: potrzeba_ratunku(50, -40, 0, _RAT), True),
    ("potrzebaRatunku(50,0,0)", lambda: potrzeba_ratunku(50, 0, 0, _RAT), False),
    ("potrzebaRatunku(900,-40,0)", lambda: potrzeba_ratunku(900, -40, 0, _RAT), False),
    ("celRatunku(150,0,nie)", lambda: cel_ratunku(150, 0, False, _B), "przed_brama"),
    ("celRatunku(150,0,tak)", lambda: cel_ratunku(150, 0, True, _B), "za_brama"),
    ("celRatunku(50,0,tak)", lambda: cel_ratunku(50, 0, True, _B), "przybycie"),
    ("otwieraBrame(straznik wygrana)", lambda: otwiera_brame({"straznik": True, "wynik": "wygrana"}), True),
    ("otwieraBrame(straznik przegrana)", lambda: otwiera_brame({"straznik": True, "wynik": "przegrana"}), False),
    ("otwieraBrame(slime wygrana)", lambda: otwiera_brame({"straznik": False, "wynik": "wygrana"}), False),
    ("punktKrzywej(0).x", lambda: punkt_krzywej(_P, 0)[0], 0.0),
    ("punktKrzywej(1).x", lambda: punkt_krzywej(_P, 1)[0], 10.0),
    ("punktKrzywej(0.5).x", lambda: punkt_krzywej(_P, 0.5)[0], 4.375),
    ("punktKrzywej(1.5).y", lambda: punkt_krzywej(_P, 1.5)[1], 5.0),
    ("punktKrzywej(2.5).x", lambda: punkt_krzywej(_P, 2.5)[0], 20.0),
    ("punktKrzywej(9).y", lambda: punkt_krzywej(_P, 9)[1], 10.0),
    ("celKrzywej(0.5).x", lambda: cel_krzywej(_P, 0.5)[0], 14.375),
    ("punktWyprzedzenia(2.6,2).y", lambda: punkt_wyprzedzenia(_P, 2.6, 2)[1], 10.0),
    ("czyZaczac(nie widzial)", lambda: czy_zaczac_przelot(False, "brak", True, True, 5, 0), True),
    ("czyZaczac(widzial)", lambda: czy_zaczac_przelot(True, "brak", True, True, 5, 0), False),
    ("czyZaczac(trwa)", lambda: czy_zaczac_przelot(False, "trwa", True, True, 5, 0), False),
    ("czyZaczac(poza lasem)", lambda: czy_zaczac_przelot(False, "brak", False, True, 5, 0), False),
    ("czyZaczac(klient niegotowy)", lambda: czy_zaczac_przelot(False, "brak", True, False, 5, 0), False),
    ("czyZaczac(przed wolnyOd)", lambda: czy_zaczac_przelot(False, "brak", True, True, 5, 6), False),
    ("terminPrzelotu(10,13.4,6)", lambda: termin_przelotu(10, 13.4, 6), 29.4),
]
