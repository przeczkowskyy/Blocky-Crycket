# -*- coding: utf-8 -*-
"""Lustro w Pythonie modułu zrodla/LogikaKowala.luau (te same nazwy w snake_case, te same zaokrąglenia i teksty).

Czysta logika kowala — bez Roblox. D = dane z dane.py (te same klucze co DaneKowala.luau). „dane gracza” = tabela
pakietu „kowal” w profilu StanGracza (Sygnaly/DanePakietu):
    { wersja = 1, przedmioty = { [id] = { poziom = 0..maks, zapas = 0.. } }, materialy = 0.., bezLupu = 0..,
      klasy = { [klasa] = true } }        -- klasy, które dostały już podstawowy zestaw
Jeden egzemplarz przedmiotu na id (z poziomem ulepszenia) + liczba zapasowych egzemplarzy (`zapas`) z łupu. Rozbiórka
bierze tylko zapas (gracz nigdy nie traci przedmiotu, który ma). Funkcje zmieniające zwracają NOWĄ tabelę (kopię) —
serwer podmienia swoją dopiero, gdy zapis do profilu się uda.

testy/test_kowala.py porównuje to lustro z LogikaKowala.luau w interpreterze tools/walka/luau_mini.py; przypadki
wzorcowe (D["przypadki"]) liczy ten plik, a LogikaKowala.sprawdzPrzypadki sprawdza je w Studio (atrybut kontenera
ZgodnoscLogikiKowala).
"""
import copy
import math

POLA_BOJOWE = ("bron", "pancerz", "tarcza")


def _calkowita(v, lo=0, hi=None):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or v != v or math.floor(v) != v or v < lo:
        return False
    return hi is None or v <= hi


def zaokr4(v):
    """Ułamek do 4 miejsc (jak w Luau: math.floor(v · 10⁴ + 0,5) / 10⁴)."""
    return math.floor(v * 10000 + 0.5) / 10000


def nowe(D):
    return {"wersja": D["wersjaDanych"], "przedmioty": {}, "materialy": 0, "bezLupu": 0, "klasy": {}}


def czyste(D, dane):
    """Tabela z profilu (albo nil) → czysta kopia: znane przedmioty, poziomy 0..maks, liczby całkowite ≥ 0;
    śmieci odpadają (zła tabela = nowe dane)."""
    w = nowe(D)
    if not isinstance(dane, dict):
        return w
    p = dane.get("przedmioty")
    if isinstance(p, dict):
        for pid, v in p.items():
            if pid in D["przedmioty"] and isinstance(v, dict):
                poz = v.get("poziom")
                zap = v.get("zapas")
                w["przedmioty"][pid] = {
                    "poziom": int(poz) if _calkowita(poz, 0, D["ulepszenie"]["maks"]) else 0,
                    "zapas": int(zap) if _calkowita(zap, 0, 999) else 0,
                }
    for k in ("materialy", "bezLupu"):
        v = dane.get(k)
        w[k] = int(v) if _calkowita(v, 0, 999999) else 0
    k = dane.get("klasy")
    if isinstance(k, dict):
        for nazwa, v in k.items():
            if nazwa in D["klasy"] and v is True:
                w["klasy"][nazwa] = True
    return w


def klasa_z(D, id_klasy):
    """Atrybut Class gracza (Warrior / Scout / Mage) → klasa silnika; brak albo nieznana → klasa domyślna."""
    if isinstance(id_klasy, str) and id_klasy in D["klasyGracza"]:
        return D["klasyGracza"][id_klasy]
    return D["klasaDomyslna"]


def posiada(dane, pid):
    return pid in dane["przedmioty"]


def podstawowe(D, dane, klasa):
    """Podstawowy zestaw klasy (raz na klasę) → (nowe dane, lista dodanych id)."""
    if klasa not in D["klasy"] or dane["klasy"].get(klasa):
        return dane, []
    w = copy.deepcopy(dane)
    dodane = []
    for pid in D["klasy"][klasa]["podstawowe"]:
        if pid not in w["przedmioty"]:
            w["przedmioty"][pid] = {"poziom": 0, "zapas": 0}
            dodane.append(pid)
    w["klasy"][klasa] = True
    return w, dodane


def statystyki(D, pid, poziom):
    """{statystyka: wartość} przedmiotu na poziomie ulepszenia (baza + poziom × krok); kolejność D["statystyki"]."""
    P = D["przedmioty"][pid]
    w = {}
    for s in D["statystyki"]:
        k = s["id"]
        v = P["baza"].get(k, 0) + poziom * P["krok"].get(k, 0)
        if v != 0:
            w[k] = zaokr4(v) if k == "tarcza" else int(v)
    return w


def koszt(D, pid, poziom):
    """Koszt ulepszenia z poziomu `poziom` na następny → {zloto, materialy} albo None (najwyższy poziom)."""
    if poziom >= D["ulepszenie"]["maks"]:
        return None
    K = D["przedmioty"][pid]["koszt"]
    return {"zloto": K["zloto"][poziom], "materialy": K["materialy"][poziom]}


def z_napisu(napis):
    if not isinstance(napis, str):
        return None
    return [x for x in napis.split(",") if x != ""]


def na_napis(ids):
    return ",".join(ids)


def zalozone(D, klasa, dane, napis):
    """Przedmioty, które liczą się w walce: posiadane całe przedmioty klasy założone w przymierzalni (atrybut
    StrojProba_<klasa> = napis); napis None (brak przymierzalni albo stroju) = wszystkie posiadane przedmioty klasy
    (każda klasa ma najwyżej jeden przedmiot na slot)."""
    lista = D["klasy"][klasa]["przedmioty"]
    if napis is None:
        return [pid for pid in lista if posiada(dane, pid)]
    zb = set(z_napisu(napis) or [])
    return [pid for pid in lista if pid in zb and posiada(dane, pid)]


def mod(D, klasa, dane, zal):
    """Wpis źródła „kowal” dla Sygnaly/Modyfikatory: dodatki z założonych przedmiotów (baza + ulepszenia). Tarcza:
    blok ze wzoru (D["blokTarczy"]) należy do tarczy — klasa z tarczą bez założonej tarczy dostaje −blokTarczy."""
    suma = {}
    for pid in zal:
        for k, v in statystyki(D, pid, dane["przedmioty"][pid]["poziom"]).items():
            suma[k] = suma.get(k, 0) + v
    K = D["klasy"][klasa]
    if K["tarcza"]:
        if not any(D["przedmioty"][pid]["slot"] == "OffHand" for pid in zal):
            suma["tarcza"] = suma.get("tarcza", 0) - D["blokTarczy"]
    w = {}
    st = {}
    for s in D["statystyki"]:
        k = s["id"]
        v = suma.get(k, 0)
        if k in POLA_BOJOWE:
            if k == "tarcza":
                v = zaokr4(v)
                if v != 0 and K["tarcza"]:
                    w[k] = v
            elif v != 0:
                w[k] = int(v)
        elif v != 0:
            st[k] = int(v)
    if st:
        w["statystyki"] = st
    return w


def dostepne(D, dane):
    """Napis atrybutu gracza KowalDostepne: posiadane całe przedmioty (kolejność danych), dla przymierzalni."""
    return na_napis([pid for pid in D["kolejnosc"] if posiada(dane, pid)])


def stroj_do_ustawienia(D, klasa, dane, napis):
    """Strój, który serwer kowala ustawia w przymierzalni (napis albo None = bez zmian): brak stroju → posiadane
    przedmioty klasy; strój z nieposiadanym przedmiotem → bez niego. Części zbroi (np. nogawice) są dozwolone, gdy
    ich całość jest posiadana i założona (przymierzalnia sama je dokłada)."""
    if napis is None:
        return na_napis(zalozone(D, klasa, dane, None))
    ids = z_napisu(napis) or []
    zb = set(ids)
    dobre, zle = [], False
    for pid in ids:
        if pid in D["czesci"]:
            calosc = D["czesci"][pid]
            if calosc in zb and posiada(dane, calosc):
                continue
            zle = True
        elif pid in D["przedmioty"] and D["przedmioty"][pid]["klasa"] == klasa and posiada(dane, pid):
            dobre.append(pid)
        else:
            zle = True
    if not zle:
        return None
    return na_napis([pid for pid in D["klasy"][klasa]["przedmioty"] if pid in set(dobre)])


def _przedmiot_klasy(D, klasa, pid):
    return isinstance(pid, str) and pid in D["przedmioty"] and D["przedmioty"][pid]["klasa"] == klasa


def rozbierz(D, dane, klasa, pid):
    """Rozbiórka jednego zapasowego egzemplarza → (True, nowe dane, zysk) albo (False, powód, 0)."""
    if not _przedmiot_klasy(D, klasa, pid):
        return False, "nieznany_przedmiot", 0
    if not posiada(dane, pid):
        return False, "nie_masz", 0
    if dane["przedmioty"][pid]["zapas"] < 1:
        return False, "brak_zapasu", 0
    w = copy.deepcopy(dane)
    w["przedmioty"][pid]["zapas"] -= 1
    zysk = D["rozbiorka"]["materialy"]
    w["materialy"] += zysk
    return True, w, zysk


def plan_ulepszenia(D, dane, klasa, pid):
    """Sprawdzenie przed wydaniem Złota → (True, koszt) albo (False, powód, brakuje materiałów)."""
    if not _przedmiot_klasy(D, klasa, pid):
        return False, "nieznany_przedmiot", 0
    if not posiada(dane, pid):
        return False, "nie_masz", 0
    k = koszt(D, pid, dane["przedmioty"][pid]["poziom"])
    if k is None:
        return False, "najwyzszy", 0
    if dane["materialy"] < k["materialy"]:
        return False, "za_malo_materialow", k["materialy"] - dane["materialy"]
    return True, k, 0


def ulepsz(D, dane, pid, k):
    """Po wydaniu Złota (StanGracza): materiały w dół, poziom w górę → nowe dane."""
    w = copy.deepcopy(dane)
    w["materialy"] -= k["materialy"]
    w["przedmioty"][pid]["poziom"] += 1
    return w


def mozna_ulepszyc(D, klasa, dane, zloto):
    """Czy gracz ma Złoto i materiały na ulepszenie któregoś posiadanego przedmiotu klasy (atrybut KowalMoznaUlepszyc —
    wskazówka celu „kowal”)."""
    for pid in D["klasy"][klasa]["przedmioty"]:
        if posiada(dane, pid):
            k = koszt(D, pid, dane["przedmioty"][pid]["poziom"])
            if k is not None and dane["materialy"] >= k["materialy"] and zloto >= k["zloto"]:
                return True
    return False


def suma_poziomow(dane):
    """Suma poziomów ulepszeń wszystkich przedmiotów (atrybut KowalUlepszen; 0 = jeszcze żadnego ulepszenia)."""
    return sum(v["poziom"] for v in dane["przedmioty"].values())


def ranga(D, roznica):
    """Przyrost tokenów krainy po pokazaniu łupu → ranga wygranej ("zwykly" / "rzadki" / "straznik") albo None."""
    G = D["lup"]["progi"]
    if not _calkowita(roznica, 1, G["maks"]):
        return None
    if roznica >= G["straznik"]:
        return "straznik"
    if roznica >= G["rzadki"]:
        return "rzadki"
    return "zwykly"


def lup(D, dane, klasa, rg, los1, los2):
    """Los przedmiotu po wygranej: los1, los2 ∈ [0, 1) z serwera. Szansa z D["lup"]["szansa"][rg]; po
    D["lup"]["ochrona"] wygranych bez przedmiotu następna daje przedmiot na pewno. Przedmiot: równa szansa każdego
    przedmiotu klasy. → (nowe dane, {"id", "nowy"} albo None)."""
    w = copy.deepcopy(dane)
    szansa = D["lup"]["szansa"].get(rg, 0)
    if los1 >= szansa and w["bezLupu"] + 1 < D["lup"]["ochrona"]:
        w["bezLupu"] += 1
        return w, None
    w["bezLupu"] = 0
    lista = D["klasy"][klasa]["przedmioty"]
    i = min(len(lista) - 1, int(math.floor(los2 * len(lista))))
    pid = lista[i]
    if pid in w["przedmioty"]:
        w["przedmioty"][pid]["zapas"] += 1
        return w, {"id": pid, "nowy": False}
    w["przedmioty"][pid] = {"poziom": 0, "zapas": 0}
    return w, {"id": pid, "nowy": True}


# ------------------------------------------------------------------------------------------------ teksty okna
def forma(formy, n):
    """Odmiana rzeczownika przy liczbie: formy = [1, 2–4, 5+] (np. materiał / materiały / materiałów); 12–14 i 0
    jak 5+, 22–24, 32–34… jak 2–4."""
    n = int(abs(n))
    if n == 1:
        return formy[0]
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return formy[1]
    return formy[2]


def ile_materialow(D, n):
    """„1 materiał”, „3 materiały”, „5 materiałów” (mianownik / biernik: koszt, zysk z rozbiórki)."""
    return "%d %s" % (n, forma(D["teksty"]["formy_materialu"], n))


def ile_materialow_dop(D, n):
    """„1 materiału”, „3 materiałów” (dopełniacz: „Brakuje ci …”)."""
    return "%d %s" % (n, forma(D["teksty"]["formy_materialu_dopelniacz"], n))


def liczba_tekst(v):
    """Liczba całkowita jako tekst (statystyki przedmiotów są całkowite; opis bohatera zaokrąglamy wcześniej)."""
    return "%d" % int(v)


def tekst_stat(D, k, v):
    nazwa = D["nazwyStatystyk"][k]
    if k == "tarcza":
        p = int(math.floor(abs(v) * 100 + 0.5))
        return "%s %s%d%%" % (nazwa, "+" if v >= 0 else "−", p)
    return "%s %s%s" % (nazwa, "+" if v >= 0 else "−", liczba_tekst(abs(v)))


def tekst_stat_lista(D, st):
    return " · ".join(tekst_stat(D, s["id"], st[s["id"]]) for s in D["statystyki"] if s["id"] in st)


def wiersz(D, dane, klasa, pid, zal, zloto):
    """Wiersz okna dla przedmiotu klasy (liczby i teksty liczy serwer — klient tylko pokazuje)."""
    T = D["teksty"]
    P = D["przedmioty"][pid]
    w = {"id": pid, "nazwa": P["nazwa"], "slot": D["sloty"][P["slot"]], "posiadany": posiada(dane, pid),
         "zalozony": pid in zal, "poziom": 0, "zapas": 0, "staty": "", "nastepny": "", "koszt": "", "ulepsz": False,
         "powod": "", "rozbierz": False, "rozbiorka": ""}
    if not w["posiadany"]:
        w["staty"] = T["nie_masz"]
        return w
    s = dane["przedmioty"][pid]
    w["poziom"], w["zapas"] = s["poziom"], s["zapas"]
    st = statystyki(D, pid, s["poziom"])
    opis = tekst_stat_lista(D, st)
    if P["slot"] == "OffHand" and D["klasy"][klasa]["tarcza"]:
        wz = T["blok_wzoru"] % int(math.floor(D["blokTarczy"] * 100 + 0.5))
        opis = wz if opis == "" else wz + " · " + opis
    w["staty"] = opis if opis != "" else T["bez_statystyk"]
    k = koszt(D, pid, s["poziom"])
    if k is None:
        w["nastepny"] = T["maks"]
    else:
        przyrost = {}
        for x in D["statystyki"]:
            v = P["krok"].get(x["id"], 0)
            if v != 0:
                przyrost[x["id"]] = v
        w["nastepny"] = T["nastepny"] % tekst_stat_lista(D, przyrost)
        w["koszt"] = T["koszt"] % (k["zloto"], ile_materialow(D, k["materialy"]))
        if dane["materialy"] < k["materialy"]:
            w["powod"] = T["za_malo_materialow"] % ile_materialow_dop(D, k["materialy"] - dane["materialy"])
        elif zloto < k["zloto"]:
            w["powod"] = T["za_malo_zlota"] % (k["zloto"] - zloto)
        else:
            w["ulepsz"] = True
    if s["zapas"] > 0:
        w["rozbierz"] = True
        w["rozbiorka"] = T["rozbiorka"] % ile_materialow(D, D["rozbiorka"]["materialy"])
    return w


def widok(D, dane, klasa, zal, zloto, bohater):
    """Całe okno: nagłówek, materiały, Złoto, opis bohatera (z Sygnaly/Bohater, tekst gotowy) i wiersze przedmiotów
    klasy (najpierw posiadane, w kolejności danych)."""
    T = D["teksty"]
    lista = D["klasy"][klasa]["przedmioty"]
    kol = [pid for pid in lista if posiada(dane, pid)] + [pid for pid in lista if not posiada(dane, pid)]
    uwaga = ""
    if D["klasy"][klasa]["tarcza"] and not any(D["przedmioty"][p]["slot"] == "OffHand" for p in zal):
        uwaga = T["bez_tarczy"]
    return {"tytul": T["tytul"], "klasa": D["nazwyKlas"][klasa], "materialy": T["materialy"] % dane["materialy"],
            "zloto": T["zloto"] % zloto, "bohater": (T["bohater"] % bohater) if bohater else "", "uwaga": uwaga,
            "wiersze": [wiersz(D, dane, klasa, pid, zal, zloto) for pid in kol]}


def opis_bohatera(D, opis):
    """Opis postaci z Sygnaly/Bohater (już z modyfikatorami) → „Broń 30 · Pancerz 13 · Blok tarczy 28%” albo ""."""
    if not isinstance(opis, dict):
        return ""
    czesci = []
    b = opis.get("bron")
    if isinstance(b, dict) and isinstance(b.get("obrazenia"), (int, float)):
        czesci.append("%s %s" % (D["nazwyStatystyk"]["bron"], liczba_tekst(math.floor(b["obrazenia"] + 0.5))))
    p = opis.get("pancerz_przedmiotow")
    if isinstance(p, (int, float)):
        czesci.append("%s %s" % (D["nazwyStatystyk"]["pancerz"], liczba_tekst(math.floor(p + 0.5))))
    t = opis.get("tarcza")
    if isinstance(t, dict) and isinstance(t.get("blok"), (int, float)):
        czesci.append("%s %d%%" % (D["nazwyStatystyk"]["tarcza"], int(math.floor(t["blok"] * 100 + 0.5))))
    return " · ".join(czesci)


def komunikat(D, powod, ile=0):
    """Powód odmowy → tekst dla gracza (bez języka twórców)."""
    T = D["teksty"]
    if powod == "za_malo_materialow":
        return T["za_malo_materialow"] % ile_materialow_dop(D, ile)
    if powod == "za_malo_zlota":
        return T["za_malo_zlota"] % ile
    mapa = {"brak_zapasu": "brak_zapasu", "nie_masz": "nie_masz_przedmiotu", "najwyzszy": "najwyzszy",
            "daleko": "podejdz", "za_szybko": "za_szybko", "brak_stanu": "nieczynna"}
    return T[mapa.get(powod, "blad")]
