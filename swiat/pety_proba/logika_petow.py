# -*- coding: utf-8 -*-
"""Lustro w Pythonie modułu zrodla/LogikaPetow.luau (te same nazwy w snake_case, te same zaokrąglenia i teksty).

Czysta logika petów — bez Roblox: cena jajka (rosnąca z liczbą kupionych; licznik osobny dla każdego jajka albo
wspólny — przełącznik D["licznik_ceny"]["tryb"]), losowanie peta z jawnymi szansami (r ∈ [0, 1) podaje serwer
z Random), teksty szans, skilli i braku Złota, premia peta, wiersze tablicy zagrody (z jajkiem peta), decyzja serwera
przed zakupem. testy/test_petow.py porównuje to lustro z LogikaPetow.luau w interpreterze tools/walka/luau_mini.py;
przypadki wzorcowe (D["przypadki"]) liczy ten plik, a LogikaPetow.sprawdzPrzypadki sprawdza je w Studio (atrybut
kontenera ZgodnoscLogikiPetow).
"""
import math


def pet(D, pid):
    for p in D["pety"]:
        if p["id"] == pid:
            return p
    return None


def jajko(D, jid):
    for j in D["jajka"]:
        if j["id"] == jid:
            return j
    return None


def jajko_peta(D, pid):
    """Jajko, z którego wykluwa się pet (każdy pet jest w puli jednego jajka)."""
    for j in D["jajka"]:
        for x in j["pula"]:
            if x == pid:
                return j
    return None


def jajko_krainy(D, kraina):
    """Jajko inkubatora w danym biomie ("las", "bagno") albo None."""
    for j in D["jajka"]:
        if j["kraina"] == kraina:
            return j
    return None


def rzadkosc(D, rid):
    for r in D["rzadkosci"]:
        if r["id"] == rid:
            return r
    return None


def _calkowita_nieujemna(v):
    return (not isinstance(v, bool)) and isinstance(v, (int, float)) and v == v and v >= 0 and math.floor(v) == v


def kupione(D, j, wydatki, tryb=None):
    """Ile jajek liczy się do ceny jajka `j` (wydatki = licznik wydatków na cel z profilu StanGracza, cel = id jajka):
    tryb "osobny" — kupione jajka `j`; "wspolny" — kupione jajka wszystkich biomów. Śmieci liczą się jak 0."""
    tryb = tryb or D["licznik_ceny"]["tryb"]
    w = wydatki if isinstance(wydatki, dict) else {}

    def n(jid):
        v = w.get(jid)
        return int(v) if _calkowita_nieujemna(v) else 0
    if tryb == "wspolny":
        return sum(n(x["id"]) for x in D["jajka"])
    return n(j["id"])


def cena(D, j, kupione, tryb=None):
    """Cena NASTĘPNEGO jajka. Tryb (z jajka albo podany): "stala" (decyzja Karola 17.11 — domyślny: cena nie rośnie
    z zakupami, rośnie tylko między biomami), "rosnaca" (start + krok × kupione do maks; kupione = kupione(D, j, …)),
    "kalkulator" (stała z tools/walka/progresja.py)."""
    c = j["cena"]
    tryb = tryb or c["tryb"]
    n = kupione if _calkowita_nieujemna(kupione) else 0
    if tryb == "stala":
        return c["stala"]
    if tryb == "kalkulator":
        return c["kalkulator"]
    return min(c["maks"], c["start"] + c["krok"] * int(n))


def forma(formy, n):
    """Odmiana przy liczbie: formy = [1, 2–4, 5+]; 0 i 12–14 jak 5+, 22–24, 32–34… jak 2–4."""
    n = int(abs(n))
    if n == 1:
        return formy[0]
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return formy[1]
    return formy[2]


_PRZYPADKI_RYBEK = {"m": "formy_rybki", "b": "formy_rybki_biernik", "d": "formy_rybki_dopelniacz"}


def ile_rybek(D, n, przypadek="m"):
    """Waluta Rybki (atrybut Gold, D-146) przy liczbie: przypadek "m" (mianownik: „cena: 1 Rybka / 3 Rybki / 5 Rybek”),
    "b" (biernik: „Kup za 1 Rybkę / 3 Rybki / 5 Rybek”), "d" (dopełniacz: „Brakuje ci 1 Rybki / 3 Rybek”, „od …”)."""
    return "%d %s" % (n, forma(D["teksty"][_PRZYPADKI_RYBEK[przypadek]], n))


def opis_ceny(D, j, tryb=None):
    """Napis ceny na tablicy i nad jajkiem: „cena: 300 Rybek” (stała, kalkulator) albo „od 300 Rybek · rośnie z każdym
    jajkiem” (rosnąca)."""
    T = D["teksty"]
    tryb = tryb or j["cena"]["tryb"]
    if tryb == "rosnaca":
        return (T["cena_od"] % ile_rybek(D, cena(D, j, 0, tryb), "d")) + " · " + T["rosnie"]
    return T["cena_tablica"] % ile_rybek(D, cena(D, j, 0, tryb))


def losuj(D, j, r):
    """r ∈ [0, 1) (Random:NextNumber na serwerze) → id peta z puli jajka; szanse po kolei (pospolity … legendarny)."""
    if isinstance(r, bool) or not isinstance(r, (int, float)) or r != r or r < 0:
        r = 0.0
    suma = 0.0
    for s in j["szanse"]:
        suma += s["szansa"]
        if r < suma:
            return s["pet"]
    return j["szanse"][-1]["pet"]


def procent(szansa):
    """0.5 → „50%”, 0.02 → „2%”, 0.005 → „0,5%”."""
    p = szansa * 100.0
    calk = math.floor(p + 0.5)
    if abs(p - calk) < 1e-9:
        return "%d%%" % calk
    dz = math.floor(p * 10 + 0.5)
    return "%d,%d%%" % (dz // 10, dz % 10)


def _proc(v):
    return int(math.floor(v * 100 + 0.5))


def _lista(nazwy):
    """["Siły"] → „Siły”; ["Siły", "Zręczności", "Inteligencji"] → „Siły, Zręczności i Inteligencji”."""
    if len(nazwy) == 1:
        return nazwy[0]
    return ", ".join(nazwy[:-1]) + " i " + nazwy[-1]


def czesci_skilla(D, p):
    """Części opisu skilla (D-101): żywioł („Ogień: mocniejsze zwykłe ciosy”), premie do statystyk (równe wartości
    razem, w stałej kolejności statystyk) i premia do łupu — np. „+8% Zręczności”, „+2% Rybek z walk”."""
    s = p["skill"]
    T = D["teksty"]
    m = s["mod"]
    czesci = []
    if s.get("zywiol"):
        Z = D["zywioly"][s["zywiol"]]
        czesci.append(Z["nazwa"] + ": " + Z["opis"])
    proc = m.get("procent") or {}
    grupy = []
    for a in D["kolejnosc_statystyk"]:
        v = proc.get(a)
        if v:
            n = _proc(v)
            znaleziona = False
            for g in grupy:
                if g[0] == n:
                    g[1].append(D["statystyki"][a])
                    znaleziona = True
                    break
            if not znaleziona:
                grupy.append((n, [D["statystyki"][a]]))
    for n, nazwy in grupy:
        czesci.append("+%d%% %s" % (n, _lista(nazwy)))
    lup = m.get("lup") or {}
    z, x = _proc(lup.get("zloto", 0)), _proc(lup.get("doswiadczenie", 0))
    if z > 0 and x > 0 and z == x:
        czesci.append(T["skill_oba"] % z)
    else:
        if z > 0:
            czesci.append(T["skill_zloto"] % z)
        if x > 0:
            czesci.append(T["skill_xp"] % x)
    return czesci


def opis_skilla(D, p):
    """Skill peta jednym krótkim zdaniem (tablica szans, okno zagrody, napis po wykluciu)."""
    return ", ".join(czesci_skilla(D, p))


def opis_skilla_krotki(D, p):
    """Najkrócej (tablica zagrody): nazwa żywiołu albo pierwsza premia — „Ogień”, „+15% Zręczności i Szczęścia”."""
    if p["skill"].get("zywiol"):
        return D["zywioly"][p["skill"]["zywiol"]]["nazwa"]
    return czesci_skilla(D, p)[0]


def mod_peta(D, pid):
    """Modyfikator bohatera od aktywnego peta dla StanGracza/Sygnaly/Modyfikatory (źródło "pety"): procent (mnożnik
    statystyk, D-059), lup (premia do łupu), pasywki żywiołu (pasywki silnika — liczą się tylko te klasy gracza),
    zaklecie żywiołu (podpalenie / trucizna przy ciosie gracza — każda klasa).
    Tylko niepuste pola; nieznany pet → None."""
    p = pet(D, pid)
    if not p:
        return None
    m = p["skill"]["mod"]
    w = {}
    if m.get("procent"):
        w["procent"] = dict(m["procent"])
    if m.get("lup"):
        w["lup"] = dict(m["lup"])
    if p["skill"].get("zywiol"):
        Z = D["zywioly"][p["skill"]["zywiol"]]
        if Z["pasywki"]:
            w["pasywki"] = list(Z["pasywki"])
        if Z.get("zaklecie"):
            w["zaklecie"] = Z["zaklecie"]     # zaklęcie broni silnika: podpalenie / trucizna przy ciosie gracza
    return w


def premia_peta(D, pid):
    """Premia do łupu peta {zloto, doswiadczenie} — dla Pety("kup" / "aktywny") (zgodność wstecz stanu gracza)."""
    p = pet(D, pid)
    lup = (p["skill"]["mod"].get("lup") or {}) if p else {}
    return {"zloto": lup.get("zloto", 0), "doswiadczenie": lup.get("doswiadczenie", 0)}


def tekst_braku(D, brakuje, zloto, c):
    return D["teksty"]["za_malo"] % (ile_rybek(D, brakuje, "d"), zloto, c)


def wiersze_szans(D, j):
    """Tablica przy inkubatorze: pet, rzadkość, kolor, szansa tekstem, skill — w kolejności puli."""
    w = []
    for s in j["szanse"]:
        p = pet(D, s["pet"])
        r = rzadkosc(D, p["rzadkosc"])
        w.append({"pet": p["id"], "nazwa": p["nazwa"], "rzadkosc": r["nazwa"], "kolor": r["kolor"],
                  "szansa": procent(s["szansa"]), "skill": opis_skilla(D, p)})
    return w


def wiersze_zagrody(D, kopie, aktywny, stoja=None):
    """Tablica, okno zagrody i okno Pets: posiadane pety w kolejności katalogu (jajko po jajku), z liczbą kopii
    (= shardy peta, D-058) i id jajka peta (klient dzieli listę na jajka). 26.11.2026: też Rybki na sekundę peta
    w zagrodzie (rybki_s — ta sama liczba, którą płaci serwer; rybki — napis „+0.04/s”), czy pet stoi teraz w zagrodzie
    (w_zagrodzie — `stoja` = lista id ze stanu zagrody, bez niej False) i cena sprzedaży jednej kopii (sprzedaz)."""
    w = []
    st = stoja if isinstance(stoja, list) else []
    for p in D["pety"]:
        n = (kopie or {}).get(p["id"])
        if _calkowita_nieujemna(n) and n > 0:
            r = rzadkosc(D, p["rzadkosc"])
            w.append({"pet": p["id"], "nazwa": p["nazwa"], "rzadkosc": r["nazwa"], "kolor": r["kolor"],
                      "kopie": int(n), "skill": opis_skilla(D, p), "krotko": opis_skilla_krotki(D, p),
                      "aktywny": p["id"] == aktywny, "jajko": p["jajko"], "rybki_s": p["rybki_s"],
                      "rybki": rybki_tekst(p["rybki_s"]), "w_zagrodzie": p["id"] in st,
                      "sprzedaz": cena_sprzedazy(D, p["id"])})
    return w


def decyzja(D, stan):
    """Serwer przed zakupem: stan = {stan_gracza (bool), zajety (bool), jajko (id)} → {ok, powod, tekst}."""
    T = D["teksty"]
    if not stan.get("stan_gracza"):
        return {"ok": False, "powod": "brak_stanu", "tekst": T["brak_stanu"]}
    if jajko(D, stan.get("jajko")) is None:
        return {"ok": False, "powod": "nieznane_jajko", "tekst": T["nieznane"]}
    if stan.get("zajety"):
        return {"ok": False, "powod": "trwa_wyklucie", "tekst": T["trwa"]}
    return {"ok": True, "powod": "ok", "tekst": ""}


# ------------------------------------------------------------------------------------------------ zagroda: Rybki
# 25.11.2026 (sesja główna, propozycja): pety stojące w zagrodzie dają Rybki (atrybut Gold, D-146) na sekundę; pet
# idący za graczem daje swój skill i NIE stoi w zagrodzie; pety na wyprawie (`poza` — wypraw jeszcze nie ma) też nie.
# Miejsca 2 → 4 → 6 → 8 (zagroda.poziomy), ulepszenie u opiekunki za Rybki; licznik ulepszeń = wydatki na cel
# zagroda.cel_ulepszenia w profilu StanGracza (zakup i poziom w jednym wywołaniu WydajZloto). Liczby robocze.
def stawka(D, pid):
    """Rybki na sekundę peta stojącego w zagrodzie (0 dla nieznanego)."""
    p = pet(D, pid)
    return p["rybki_s"] if p else 0


def poziom_zagrody(D, wydatki):
    """Poziom zagrody 1..len(poziomy) z licznika kupionych ulepszeń (wydatki[cel_ulepszenia]); śmieci = 0 ulepszeń."""
    v = (wydatki if isinstance(wydatki, dict) else {}).get(D["zagroda"]["cel_ulepszenia"])
    n = int(v) if _calkowita_nieujemna(v) else 0
    return min(1 + n, len(D["zagroda"]["poziomy"]))


def miejsca_zagrody(D, poziom):
    poz = D["zagroda"]["poziomy"]
    i = int(poziom) if _calkowita_nieujemna(poziom) else 1
    return poz[max(1, min(i, len(poz))) - 1]["miejsc"]


def cena_ulepszenia(D, poziom):
    """Cena NASTĘPNEGO poziomu zagrody albo None (najwyższy poziom)."""
    poz = D["zagroda"]["poziomy"]
    i = int(poziom) if _calkowita_nieujemna(poziom) else 1
    if i >= len(poz):
        return None
    return poz[max(1, i)]["cena"]


def czysty_wybor(D, wybor):
    """Wybór gracza z DanePakietu → lista znanych id bez powtórzeń (najwyżej tyle, ile petów w katalogu) albo None
    (= wybór domyślny: najrzadsze). Słownik z kluczami 1, 2, … (tablica Luau po zapisie) też jest listą."""
    if isinstance(wybor, dict):
        if len(wybor) == 0:
            return []
        if not all(isinstance(k, int) for k in wybor):
            return None
        elementy = [wybor[k] for k in sorted(wybor)]
    elif isinstance(wybor, list):
        elementy = wybor
    else:
        return None
    w = []
    for x in elementy:
        if isinstance(x, str) and pet(D, x) is not None and x not in w and len(w) < len(D["pety"]):
            w.append(x)
    return w


def _nr_rzadkosci(D, pid):
    p = pet(D, pid)
    for i, r in enumerate(D["rzadkosci"]):
        if p and r["id"] == p["rzadkosc"]:
            return i + 1
    return 0


def _przed(D, a, b, kolejnosc):
    """Kolejność domyślna zagrody: rzadszy pierwszy, przy tej samej rzadkości wyższa stawka, potem katalog."""
    ra, rb = _nr_rzadkosci(D, a), _nr_rzadkosci(D, b)
    if ra != rb:
        return ra > rb
    sa, sb = stawka(D, a), stawka(D, b)
    if sa != sb:
        return sa > sb
    return kolejnosc[a] < kolejnosc[b]


def w_zagrodzie(D, kopie, aktywny, wybor, miejsc, poza=None):
    """Pety, które STOJĄ w zagrodzie (dają Rybki): posiadane (kopie > 0), bez aktywnego i bez petów `poza` (wyprawa);
    wybór gracza (lista) w jego kolejności, a bez wyboru — najrzadsze; najwyżej `miejsc`."""
    kopie = kopie if isinstance(kopie, dict) else {}
    poza = poza if isinstance(poza, dict) else {}
    kolejnosc, kandydaci = {}, []
    for i, p in enumerate(D["pety"]):
        kolejnosc[p["id"]] = i
        n = kopie.get(p["id"])
        if _calkowita_nieujemna(n) and n > 0 and p["id"] != aktywny and not poza.get(p["id"]):
            kandydaci.append(p["id"])
    m = int(miejsc) if _calkowita_nieujemna(miejsc) else 0
    czysty = czysty_wybor(D, wybor)
    if czysty is not None:
        return [x for x in czysty if x in kandydaci][:m]
    lista = []
    for x in kandydaci:          # wstawianie (Luau bez table.sort w luau_mini) — ta sama kolejność co w lustrze
        i = len(lista)
        while i > 0 and _przed(D, x, lista[i - 1], kolejnosc):
            i -= 1
        lista.insert(i, x)
    return lista[:m]


def przychod_s(D, lista):
    """Rybki na sekundę petów z listy (suma w kolejności listy)."""
    s = 0.0
    for x in lista or []:
        s += stawka(D, x)
    return s


def opis_przychodu(D, stawka_s):
    """Rybki na sekundę → „+2,4 Rybki/min”, „+3 Rybki/min”, „+12 Rybek/min” (do 10 na minutę z jednym miejscem po
    przecinku, wyżej całe; przy ułamku dopełniacz liczby pojedynczej „Rybki”, przy całej liczbie odmiana jak zwykle)."""
    dobra = isinstance(stawka_s, (int, float)) and not isinstance(stawka_s, bool) and stawka_s > 0
    v = stawka_s * 60.0 if dobra else 0.0
    if v >= 10:
        t = "%d" % int(math.floor(v + 0.5))
    else:
        dz = int(math.floor(v * 10 + 0.5))
        t = "%d" % (dz // 10) if dz % 10 == 0 else "%d,%d" % (dz // 10, dz % 10)
    T = D["teksty"]
    slowo = T["formy_rybki_dopelniacz"][0] if "," in t else forma(T["formy_rybki"], int(t))
    return T["przychod_min"] % (t, slowo)


def stan_zagrody(D, kopie, aktywny, wybor, wydatki, poza=None):
    """Wszystko o zagrodzie gracza dla serwera (naliczanie) i okna: poziom, miejsca, kto stoi, Rybki na sekundę, opis,
    cena następnego poziomu (None na najwyższym), czy wybór jest ręczny."""
    poziom = poziom_zagrody(D, wydatki)
    miejsc = miejsca_zagrody(D, poziom)
    stoja = w_zagrodzie(D, kopie, aktywny, wybor, miejsc, poza)
    s = przychod_s(D, stoja)
    return {"poziom": poziom, "miejsc": miejsc, "miejsc_maks": D["zagroda"]["poziomy"][-1]["miejsc"], "stoja": stoja,
            "stawka_s": s, "opis": opis_przychodu(D, s), "cena": cena_ulepszenia(D, poziom),
            "reczny": czysty_wybor(D, wybor) is not None}


def zmien_wybor(D, kopie, aktywny, wybor, wydatki, poza, pid, tak):
    """„Do zagrody” (tak) / „Z zagrody” peta → (nowy wybór — lista, ręczny, od tego, co dziś stoi; powód).
    Powody: ok, nie_masz, aktywny (pet idący za graczem nie stoi w zagrodzie), pelna, juz, nie_stoi."""
    st = stan_zagrody(D, kopie, aktywny, wybor, wydatki, poza)
    stoja = list(st["stoja"])
    n = (kopie if isinstance(kopie, dict) else {}).get(pid) if isinstance(pid, str) else None
    if pet(D, pid) is None or not (_calkowita_nieujemna(n) and n > 0):
        return czysty_wybor(D, wybor), "nie_masz"
    if tak:
        if pid == aktywny:
            return czysty_wybor(D, wybor), "aktywny"
        if pid in stoja:
            return stoja, "juz"
        if len(stoja) >= st["miejsc"]:
            return czysty_wybor(D, wybor), "pelna"
        return stoja + [pid], "ok"
    if pid not in stoja:
        return czysty_wybor(D, wybor), "nie_stoi"
    return [x for x in stoja if x != pid], "ok"


def po_wyborze(D, wybor, stary, nowy):
    """Ręczny wybór po zmianie aktywnego peta: nowy aktywny zwalnia swoje miejsce w zagrodzie dla starego (zamiana
    miejscami); wybór domyślny (None) zostaje domyślny."""
    w = czysty_wybor(D, wybor)
    if w is None:
        return None
    if nowy in w:
        i = w.index(nowy)
        if isinstance(stary, str) and pet(D, stary) is not None and stary not in w:
            w[i] = stary
        else:
            w.pop(i)
    return w


def po_odstawieniu(D, wybor, stary):
    """Ręczny wybór po „Odstaw peta”: odstawiony pet wraca na koniec listy zagrody (stanie, jeśli jest miejsce)."""
    w = czysty_wybor(D, wybor)
    if w is None:
        return None
    if isinstance(stary, str) and pet(D, stary) is not None and stary not in w:
        w.append(stary)
    return w


def _skonczona(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v and abs(v) != float("inf")


def tik(D, reszta, stawka_s, dt):
    """Naliczanie co zagroda.tik_s: (całe Rybki do dopisania, reszta ułamka na następny raz). dt przycięte do
    0..tik_maks_s (przerwa serwera nie daje zaległych Rybek; przychodu offline nie ma)."""
    d = min(max(dt if _skonczona(dt) else 0.0, 0.0), D["zagroda"]["tik_maks_s"])
    r = reszta if _skonczona(reszta) and 0 <= reszta < 1 else 0.0
    s = stawka_s if _skonczona(stawka_s) and stawka_s > 0 else 0.0
    suma = r + s * d
    ile = int(math.floor(suma + 1e-9))
    return ile, max(0.0, suma - ile)


def tekst_braku_ulepszenia(D, brakuje, zloto, c):
    return D["teksty"]["za_malo_ulepszenie"] % (ile_rybek(D, brakuje, "d"), zloto, c)


# ------------------------------------------------------------------------------------------------ sprzedaż (26.11.2026)
def rybki_tekst(v):
    """Rybki na sekundę peta w zagrodzie jako krótki napis na kafelek okna (HUD po angielsku, kropka dziesiętna):
    „+0.015/s”, „+0.04/s”, „+0.25/s”, „+1.2/s” — do 0,1: tysięczne, do 1: setne, wyżej dziesiąte, bez zer na końcu."""
    if not _skonczona(v) or v <= 0:
        return "+0/s"
    t = None
    if v < 0.1:
        m = int(math.floor(v * 1000 + 0.5))
        if m < 100:
            t = "0.%03d" % m
    if t is None and v < 1:
        h = int(math.floor(v * 100 + 0.5))
        if h < 100:
            t = "0.%02d" % h
    if t is None:
        d = int(math.floor(v * 10 + 0.5))
        t = "%d.%d" % (d // 10, d % 10)
    while t.endswith("0"):
        t = t[:-1]
    if t.endswith("."):
        t = t[:-1]
    return "+%s/s" % t


def cena_sprzedazy(D, pid):
    """Rybki za jedną kopię peta (policzone przez dane_petow.py z podłogi ceny jajka i rzadkości); obcy pet = 0."""
    p = pet(D, pid)
    return p["sprzedaz"] if p else 0


def sprzedaz(D, kopie, aktywny, stoja, lista):
    """Decyzja sprzedaży (serwer; StanGracza i tak sprawdza kopie jeszcze raz). lista = [id | {"pet": id, "ile": n}]
    (1..D["sprzedaz"]["maks_pozycji"] pozycji; samo id = jedna kopia). Pozycje po kolei, z kopiami, które zostały:
    nieznany pet, za mało kopii, ostatnia kopia aktywnego peta, ostatnia kopia peta stojącego w zagrodzie (`stoja`),
    ostatni pet gracza i suma ponad maks_kwoty — odmowa tej pozycji, reszta przechodzi.
    → {"ok", "powod", "pozycje": {id: ile}, "suma", "sztuk", "wyniki": [{"pet", "ile", "ok", "powod", "cena"}]}."""
    S = D["sprzedaz"]
    if not isinstance(lista, list) or not 1 <= len(lista) <= S["maks_pozycji"]:
        return {"ok": False, "powod": "zla_lista", "pozycje": {}, "suma": 0, "sztuk": 0, "wyniki": []}
    zostalo = {}
    for k, v in (kopie if isinstance(kopie, dict) else {}).items():
        if isinstance(k, str) and _calkowita_nieujemna(v) and v > 0:
            zostalo[k] = int(v)
    razem = sum(zostalo.values())
    st = stoja if isinstance(stoja, list) else []
    pozycje, wyniki, suma, sztuk = {}, [], 0, 0
    for x in lista:
        if isinstance(x, str):
            pid, ile = x, 1
        elif isinstance(x, dict) and isinstance(x.get("pet"), str):
            pid, ile = x["pet"], x.get("ile")
        else:
            wyniki.append({"pet": "", "ile": 0, "ok": False, "powod": "zly_wpis", "cena": 0})
            continue
        if not (_calkowita_nieujemna(ile) and ile >= 1):
            wyniki.append({"pet": pid, "ile": 0, "ok": False, "powod": "zly_wpis", "cena": 0})
            continue
        ile = int(ile)
        ma = zostalo.get(pid, 0)
        cena1 = cena_sprzedazy(D, pid)
        powod = "ok"
        if pet(D, pid) is None:
            powod = "nieznany"
        elif ma < ile:
            powod = "nie_masz"
        elif ma == ile and pid == aktywny:
            powod = "aktywny"
        elif ma == ile and pid in st:
            powod = "w_zagrodzie"
        elif razem - ile < 1:
            powod = "ostatni"
        elif suma + cena1 * ile > S["maks_kwoty"]:
            powod = "za_duzo"
        if powod != "ok":
            wyniki.append({"pet": pid, "ile": ile, "ok": False, "powod": powod, "cena": 0})
            continue
        zostalo[pid] = ma - ile
        razem -= ile
        pozycje[pid] = pozycje.get(pid, 0) + ile
        suma += cena1 * ile
        sztuk += ile
        wyniki.append({"pet": pid, "ile": ile, "ok": True, "powod": "ok", "cena": cena1 * ile})
    return {"ok": sztuk > 0, "powod": "ok" if sztuk > 0 else (wyniki[0]["powod"] if wyniki else "zla_lista"),
            "pozycje": pozycje, "suma": suma, "sztuk": sztuk, "wyniki": wyniki}


# ------------------------------------------------------------------------------------------------ przypadki
def przypadki(D):
    P = {"cena": [], "opis_ceny": [], "kupione": [], "losuj": [], "procent": [], "skill": [], "jajko_peta": [],
         "zagroda": [], "decyzja": [], "szanse": []}
    for j in D["jajka"]:
        # tryb podany wprost: przełączenie trybu w danych (ustawienia.json) nie psuje zgodności przypadków
        tryby = ["stala", "rosnaca"] + (["kalkulator"] if "kalkulator" in j["cena"] else [])
        for tryb in tryby:
            for n in (0, 1, 2, 3, 4, 5, 10, -1, 2.5, None):
                P["cena"].append({"jajko": j["id"], "kupione": n, "tryb": tryb, "wynik": cena(D, j, n, tryb)})
            P["opis_ceny"].append({"jajko": j["id"], "tryb": tryb, "wynik": opis_ceny(D, j, tryb)})
        granice = []
        suma = 0.0
        for s in j["szanse"]:
            suma += s["szansa"]
            granice.append(suma)
        for r in [0.0, 0.25, 0.4999, 0.5, 0.74, 0.75, 0.899, 0.9, 0.979, 0.98, 0.999999, -1, None] + granice:
            P["losuj"].append({"jajko": j["id"], "r": r, "wynik": losuj(D, j, r)})
        P["szanse"].append({"jajko": j["id"], "wynik": wiersze_szans(D, j)})
        st = {"stan_gracza": True, "jajko": j["id"]}
        for zmiana in ({}, {"stan_gracza": False}, {"zajety": True}):
            P["decyzja"].append({"stan": dict(st, **zmiana), "wynik": decyzja(D, dict(st, **zmiana))})
    ids = [j["id"] for j in D["jajka"]]
    wydatki = ({}, {ids[0]: 3}, {ids[-1]: 2}, {ids[0]: 4, ids[-1]: 1, "inny_cel": 7}, {ids[0]: -1, ids[-1]: 2.5},
               {ids[0]: "3"})
    for j in D["jajka"]:
        for w in wydatki:
            for tryb in ("osobny", "wspolny"):
                P["kupione"].append({"jajko": j["id"], "wydatki": w, "tryb": tryb, "wynik": kupione(D, j, w, tryb)})
    for s in (0.5, 0.25, 0.15, 0.08, 0.02, 0.005, 0.125, 1.0):
        P["procent"].append({"szansa": s, "wynik": procent(s)})
    for p in D["pety"]:
        P["skill"].append({"pet": p["id"], "wynik": opis_skilla(D, p), "krotko": opis_skilla_krotki(D, p),
                           "premia": premia_peta(D, p["id"]), "mod": mod_peta(D, p["id"])})
        P["jajko_peta"].append({"pet": p["id"], "wynik": jajko_peta(D, p["id"])["id"]})
    pierwsze = [j["pula"][0] for j in D["jajka"]]
    ostatnie = [j["pula"][-1] for j in D["jajka"]]
    for kopie, akt in (({}, None), ({pierwsze[0]: 3, ostatnie[0]: 1}, ostatnie[0]),
                       ({pierwsze[-1]: 2, pierwsze[0]: 1, "obcy": 5}, pierwsze[-1]),
                       ({pierwsze[0]: 0, ostatnie[-1]: -1}, None),
                       (dict({p["id"]: 1 + i for i, p in enumerate(D["pety"])}), ostatnie[-1])):
        P["zagroda"].append({"kopie": kopie, "aktywny": akt, "wynik": wiersze_zagrody(D, kopie, akt)})
    for st in ({"stan_gracza": True, "jajko": "jajko_smoka"}, {"stan_gracza": True}):
        P["decyzja"].append({"stan": st, "wynik": decyzja(D, st)})
    P["kraina"] = []
    for k in [j["kraina"] for j in D["jajka"]] + ["dzungla", None]:
        j = jajko_krainy(D, k)
        P["kraina"].append({"kraina": k, "wynik": j["id"] if j else None})
    przypadki_zagrody(D, P)
    return P


def _bez_none(v):
    """Przypadek dla Luau: None w słowniku = brak klucza (nil), więc go nie zapisujemy."""
    if isinstance(v, dict):
        return {k: _bez_none(x) for k, x in v.items() if x is not None}
    if isinstance(v, list):
        return [_bez_none(x) for x in v]
    return v


def przypadki_zagrody(D, P):
    """Przypadki wzorcowe zagrody (Rybki, miejsca, wybór) — lustro Luau sprawdza je w testach i w Studio."""
    cel = D["zagroda"]["cel_ulepszenia"]
    ids = [p["id"] for p in D["pety"]]
    P["stawka"] = [{"pet": x, "wynik": stawka(D, x)} for x in ids + ["obcy"]]
    P["poziom_zagrody"] = [{"wydatki": w, "wynik": poziom_zagrody(D, w)}
                           for w in ({}, {cel: 1}, {cel: 2}, {cel: 3}, {cel: 7}, {cel: -1}, {cel: 1.5}, {cel: "2"},
                                     {"jajko_lesne": 3})]
    P["miejsca_zagrody"] = [_bez_none({"poziom": v, "wynik": miejsca_zagrody(D, v), "cena": cena_ulepszenia(D, v)})
                            for v in (1, 2, 3, 4, 5, 0, -2, 2.5)]
    P["opis_przychodu"] = [{"s": s, "wynik": opis_przychodu(D, s)}
                           for s in (0, 0.02, 0.05, 0.1, 0.1234, 0.16666, 0.5, 1.0, 2.75, -1, 1 / 60.0, 2 / 60.0,
                                     0.2, 22 / 60.0, 0.25)]
    # waluta Rybki (D-146): odmiana przy liczbie w trzech przypadkach i oba teksty braku
    P["rybki"] = [{"n": n, "m": ile_rybek(D, n), "b": ile_rybek(D, n, "b"), "d": ile_rybek(D, n, "d"),
                   "brak": tekst_braku(D, n, 7, 300), "brakUlepszenia": tekst_braku_ulepszenia(D, n, 7, 1000)}
                  for n in (0, 1, 2, 4, 5, 11, 12, 14, 21, 22, 25, 100, 101, 102, 112)]
    wszystkie = {x: 1 + i % 3 for i, x in enumerate(ids)}
    las = {x: 1 for x in ids[:5]}
    scen = [({}, None, None, {}), (las, ids[4], None, {}), (las, None, None, {cel: 1}),
            (wszystkie, ids[-1], None, {cel: 3}), (wszystkie, None, [ids[0], ids[0], "obcy", ids[7]], {cel: 1}),
            (wszystkie, ids[7], [ids[7], ids[1]], {}), (las, None, [], {cel: 2}),
            (dict(las, **{ids[2]: 0}), None, None, {cel: 1}), (wszystkie, None, None, {cel: 2})]
    P["stan_zagrody"] = []
    for kopie, akt, wyb, wyd in scen:
        for poza in (None, {ids[-1]: True, ids[4]: True}):
            P["stan_zagrody"].append(_bez_none({"kopie": kopie, "aktywny": akt, "wybor": wyb, "wydatki": wyd,
                                                "poza": poza, "wynik": stan_zagrody(D, kopie, akt, wyb, wyd, poza)}))
    P["zmien_wybor"] = []
    for kopie, akt, wyb, wyd in scen[1:7]:
        for pid, tak in ((ids[0], True), (ids[4], True), (ids[3], False), (ids[1], False), (ids[9], True),
                         ("obcy", True)):
            nowy, powod = zmien_wybor(D, kopie, akt, wyb, wyd, None, pid, tak)
            P["zmien_wybor"].append(_bez_none({"kopie": kopie, "aktywny": akt, "wybor": wyb, "wydatki": wyd,
                                               "pet": pid, "tak": tak, "wynik": nowy, "powod": powod}))
    P["po_wyborze"] = []
    for wyb, st, nw in ((None, ids[0], ids[1]), ([ids[1], ids[2]], ids[0], ids[1]), ([ids[1], ids[2]], None, ids[2]),
                        ([ids[1], ids[0]], ids[0], ids[1]), ([ids[3]], ids[0], ids[1])):
        P["po_wyborze"].append(_bez_none({"wybor": wyb, "stary": st, "nowy": nw, "wynik": po_wyborze(D, wyb, st, nw),
                                          "odstaw": po_odstawieniu(D, wyb, st)}))
    P["tik"] = []
    for r, s, dt in ((0, 0.05, 5), (0.9, 0.05, 5), (0.5, 0.25, 4), (0, 0.4, 100), (0, 1.3, -3), (2, 0.1, 5),
                     (0.3, 0, 5), (0.999, 0.0002, 5), (0, 0.29, 5)):
        ile, reszta = tik(D, r, s, dt)
        P["tik"].append({"r": r, "s": s, "dt": dt, "ile": ile, "reszta": reszta})
    # sprzedaż (26.11.2026): napis Rybek na sekundę, cena kopii i decyzja serwera
    P["rybki_tekst"] = [{"v": v, "wynik": rybki_tekst(v)}
                        for v in [p["rybki_s"] for p in D["pety"]] + [0, -1, 0.0995, 0.1, 0.999, 1.0, 1.25, 12.34]]
    P["cena_sprzedazy"] = [{"pet": x, "wynik": cena_sprzedazy(D, x)} for x in ids + ["obcy"]]
    P["sprzedaz"] = []
    kop = {ids[0]: 3, ids[4]: 1, ids[9]: 2, ids[7]: 1}
    maks = D["sprzedaz"]["maks_pozycji"]
    for kopie, akt, stoja, lista in (
            (kop, ids[0], [ids[4]], [ids[0], {"pet": ids[9], "ile": 2}]),
            (kop, ids[0], [ids[4]], [{"pet": ids[0], "ile": 3}]),
            (kop, ids[0], [ids[4]], [ids[4]]),
            (kop, ids[0], [], [ids[4], ids[7], {"pet": ids[9], "ile": 2}, {"pet": ids[0], "ile": 2}]),
            (kop, None, [], [ids[4], ids[7], {"pet": ids[9], "ile": 2}, {"pet": ids[0], "ile": 3}]),
            (kop, ids[0], [], [ids[1], "obcy", {"pet": ids[9], "ile": 0}, {"pet": ids[9], "ile": 1.5}, 7, {"ile": 1}]),
            (kop, ids[0], [], [ids[9], ids[9], ids[9]]),
            (kop, ids[0], [], []), (kop, ids[0], [], "x"), (kop, ids[0], [], [ids[9]] * (maks + 1)),
            ({ids[14]: 500}, None, [], [{"pet": ids[14], "ile": 499}]),
            ({}, None, None, [ids[0]])):
        P["sprzedaz"].append(_bez_none({"kopie": kopie, "aktywny": akt, "stoja": stoja, "lista": lista,
                                        "wynik": sprzedaz(D, kopie, akt, stoja, lista)}))
