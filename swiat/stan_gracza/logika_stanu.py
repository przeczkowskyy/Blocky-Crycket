# -*- coding: utf-8 -*-
"""Lustro w Pythonie modułu zrodla/LogikaStanu.luau (te same nazwy funkcji, snake_case; te same zaokrąglenia).

Czysta logika stanu gracza — bez Roblox: krzywa doświadczenia i awans, pula i rozkład statystyk klasy, opis bohatera
dla silnika walki, sprawdzanie łupu i przyrostu z treningu. Testy (testy/test_stanu.py) porównują:
  • to lustro z tools/walka (tempo.xp_do_nastepnego, wzorcowe.rozdziel / postac) — jedna prawda liczb;
  • to lustro z prawdziwym LogikaStanu.luau wykonanym w interpreterze tools/walka/luau_mini.py.
Przypadki wzorcowe (D["przypadki"] w zrodla/DaneStanu.luau) liczy ten plik; LogikaStanu.sprawdzPrzypadki sprawdza
je w Studio (atrybut kontenera ZgodnoscLogikiStanu).
"""
import math


def xp_do_nastepnego(D, poziom):
    """Doświadczenie z poziomu L na L+1: max(1, zaokrąglij(A × L^B)) — krzywa z tools/walka/tempo.py."""
    k = D["krzywa"]
    return max(1, int(math.floor(k["a"] * float(poziom) ** k["b"] + 0.5)))


def awans(D, poziom, xp, dodaj):
    """(poziom, xp) + dodane doświadczenie → (nowy poziom, reszta xp, ile awansów). Na poziomie maks. xp stoi."""
    maks = D["limity"]["poziom_maks"]
    poziom = poziom_z(D, poziom)
    xp = max(0, xp) + max(0, dodaj)
    ile = 0
    while poziom < maks:
        potrzeba = xp_do_nastepnego(D, poziom)
        if xp < potrzeba:
            break
        xp -= potrzeba
        poziom += 1
        ile += 1
    if poziom >= maks:
        xp = min(xp, xp_do_nastepnego(D, poziom))
    return poziom, xp, ile


def pula(D, poziom):
    return D["pula"]["baza"] + D["pula"]["na_poziom"] * (poziom - 1)


def sloty(D, poziom):
    for prog in D["sloty"]:
        if poziom >= prog["od"]:
            return prog["n"]
    return 0


def rozdziel(D, rozklad, punkty):
    """Udziały → całe punkty o sumie `punkty` (metoda największych reszt, jak tools/walka/wzorcowe.rozdziel)."""
    S = D["statystyki"]
    dokladne = {s: rozklad[s] * punkty for s in S}
    st = {s: int(math.floor(dokladne[s] + 1e-9)) for s in S}
    reszta = punkty - sum(st.values())
    kolejnosc = sorted(S, key=lambda s: (-(dokladne[s] - st[s]), -rozklad[s], S.index(s)))
    i = 0
    while reszta > 0:
        st[kolejnosc[i % len(kolejnosc)]] += 1
        reszta -= 1
        i += 1
    return st


def poziom_z(D, v):
    """Atrybut Level → poziom całkowity 1..poziom_maks (zły albo brak → 1)."""
    if isinstance(v, bool) or not isinstance(v, (int, float)) or v != v:
        return 1
    if v >= D["limity"]["poziom_maks"]:
        return D["limity"]["poziom_maks"]
    if v < 1:
        return 1
    return int(math.floor(v))


def statystyka_z(D, v):
    """Atrybut statystyki → całe punkty 0..statystyka_maks albo None (nie liczba)."""
    if isinstance(v, bool) or not isinstance(v, (int, float)) or v != v:
        return None
    if v <= 0:
        return 0
    if v >= D["limity"]["statystyka_maks"]:
        return D["limity"]["statystyka_maks"]
    return int(math.floor(v))


def klasa_silnika(D, id_klasy):
    """Atrybut Class („Warrior” …) → (klasa silnika, czy znana). Nieznana → klasa domyślna."""
    if isinstance(id_klasy, str) and id_klasy in D["klasy_gracza"]:
        return D["klasy_gracza"][id_klasy], True
    return D["klasa_domyslna"], False


def rozklad_z_class_data(D, stats):
    """ClassData.Classes[i].stats (sześć procentów puli, suma 100) → rozkład (ułamki) albo (None, powód)."""
    S = D["statystyki"]
    if not isinstance(stats, list) or len(stats) != len(S):
        return None, "zla_lista"
    suma = 0
    for v in stats:
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v != v or v < 0 or v > 100:
            return None, "zla_liczba"
        suma += v
    if abs(suma - 100) > 1e-9:
        return None, "suma_nie_100"
    return {s: stats[i] / 100 for i, s in enumerate(S)}, "ok"


def opis_bohatera(D, klasa, poziom, st):
    """Opis postaci dla silnika walki (wejście Silnik.symuluj): to samo co tools/walka/wzorcowe.postac(klasa, poziom,
    dodatkowe=…) — statystyki z gracza, broń, pancerz z przedmiotów i sloty umiejętności ze wzoru dla poziomu."""
    W = D["wzor"]
    n = sloty(D, poziom)
    p = {
        "nazwa": D["nazwy_klas"][klasa],
        "klasa": klasa,
        "poziom": poziom,
        "statystyki": {s: st[s] for s in D["statystyki"]},
        "bron": {"obrazenia": W["bron_baza"] + W["bron_na_poziom"] * poziom},
        "pancerz_przedmiotow": W["pancerz_baza"] + W["pancerz_na_poziom"] * poziom,
        "umiejetnosci": list(D["umiejetnosci"][klasa][:n]),
    }
    if D["tarcza"].get(klasa):
        p["tarcza"] = {"blok": W["blok_tarczy"]}
    return p


def nowe_statystyki(D, obecne, stara_baza, cel, wytrenowane):
    """Wartości sześciu atrybutów po zmianie klasy albo poziomu.
    Bez starej bazy (pierwsze wpisanie): cel + wytrenowane. Z bazą: obecne + (cel − stara baza) — dzięki temu zostaje
    wszystko, co dopisał ktoś inny (np. „+” w oknie ekwipunku), a trening jest już w obecnych."""
    w = {}
    for s in D["statystyki"]:
        if stara_baza is None or statystyka_z(D, obecne.get(s)) is None:
            v = cel[s] + wytrenowane.get(s, 0)
        else:
            v = statystyka_z(D, obecne[s]) + cel[s] - stara_baza[s]
        w[s] = statystyka_z(D, v)
    return w


def _calkowita(v, maks):
    return (not isinstance(v, bool)) and isinstance(v, (int, float)) and v == v and 0 <= v <= maks and math.floor(v) == v


def _znak_nazwy(c):
    b = ord(c)
    return 48 <= b <= 57 or 65 <= b <= 90 or 97 <= b <= 122 or b == 95


def nazwa_ok(D, t):
    return isinstance(t, str) and 0 < len(t) <= D["limity"]["dlugosc_nazwy"] and all(_znak_nazwy(c) for c in t)


def czysty_lup(D, lup):
    """Łup z silnika (walka.lup) → kopia z samymi znanymi polami albo (None, powód). Bez zaufania do wołającego:
    liczby całkowite, nieujemne, w limitach; kraina z liter, cyfr i „_”."""
    if not isinstance(lup, dict):
        return None, "zly_lup"
    w = {}
    for pole in D["pola_lupu"]:
        maks = D["limity"]["lup"][pole]
        v = lup.get(pole, 0)
        if v is None:
            v = 0
        if not _calkowita(v, maks):
            return None, "zle_" + pole
        w[pole] = int(v)
    kraina = lup.get("kraina", "")
    if kraina in (None, ""):
        kraina = ""
    elif not nazwa_ok(D, kraina):
        return None, "zla_kraina"
    w["kraina"] = kraina
    return w, "ok"


def czysty_przyrost(D, info):
    """Sygnał PrzyrostStatystyki z Training Center → (statystyka silnika, przyrost) albo (None, powód)."""
    if not isinstance(info, dict):
        return None, "zly_przyrost"
    s = None
    atr = info.get("atrybut")
    for nazwa, a in D["atrybuty_statystyk"].items():
        if a == atr:
            s = nazwa
    if s is None and info.get("statystyka") in D["atrybuty_statystyk"]:
        s = info.get("statystyka")
    if s is None:
        return None, "zla_statystyka"
    n = info.get("przyrost")
    if not _calkowita(n, D["limity"]["przyrost_maks"]) or n < 1:
        return None, "zly_przyrost"
    return (s, int(n)), "ok"


def suma_lupow(D, lista):
    """Kilka łupów czekających na pokazanie → jedna suma (tokeny osobno dla każdej krainy)."""
    w = {p: 0 for p in D["pola_lupu"]}
    tokeny = {}
    for lup in lista:
        for p in D["pola_lupu"]:
            w[p] += lup[p]
        if lup["tokeny_krainy"] > 0 and lup["kraina"] != "":
            tokeny[lup["kraina"]] = tokeny.get(lup["kraina"], 0) + lup["tokeny_krainy"]
    w["tokeny"] = tokeny
    return w


def nowy_profil(D):
    """Profil gracza: JEDNA tabela z polem wersji (pod przyszły zapis; dziś tylko pamięć serwera)."""
    return {
        "wersja": D["wersja_profilu"],
        "klasa": D["klasa_domyslna"],
        "poziom": 1,
        "xp": 0,
        "zloto": 0,
        "gemy": 0,
        "tokeny": {},
        "shardy": 0,
        "wytrenowane": {s: 0 for s in D["statystyki"]},
        "baza": None,
        "walki": {"wygrane": 0, "przegrane": 0},
        "awanse": 0,
    }
