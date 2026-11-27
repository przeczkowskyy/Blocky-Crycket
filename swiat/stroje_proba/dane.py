#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator zrodla/DaneStrojow*.luau — gołe ciała bohaterów i przedmioty z katalogu jako części Roblox (D-071, próba;
od 19.11.2026 także 60 przedmiotów do kupienia w trzech stopniach — D-106).

    python -B swiat/stroje_proba/dane.py               # zapisuje zrodla/DaneStrojow.luau i moduły stopni
    python -B swiat/stroje_proba/dane.py --sprawdz     # kod 1, gdy pliki w zrodla/ są nieaktualne albo dane się nie zgadzają
    python -B swiat/stroje_proba/dane.py --wyjscie DIR # zapis do innego folderu (test powtarzalności)

Pliki wynikowe (jeden moduł Roblox ma granicę ok. 200 000 znaków Source, więc dane są w kilku):
  DaneStrojow.luau          ustawienia, klasy (szkielet, gołe ciało), 20 dzisiejszych przedmiotów i SCALENIE modułów
                            stopni — każdy czytelnik (Ubieranie, serwer, klient, kowal, sklep) dalej bierze jedno D;
  DaneStrojow<Stopien>.luau przedmioty jednego stopnia (Las, Bagno, Dzungla) wszystkich klas: { [id] = przedmiot }.

Źródła (tylko odczyt, nic tam nie zmieniamy):
  swiat/postacie/przedmioty.json        katalog: id, nazwa, slot, klasy, typ ciała, czesc_od, ukrywa, segmenty;
  swiat/postacie/sklep_przedmioty.json  katalog sklepu: te same pola dla przedmiotów stopni (klasa, stopień);
  swiat/postacie/stopnie.py             geometria przedmiotów stopni: przedmioty(klasa, stopień), komplet(…);
  swiat/postacie/<bohater>.py           geometria: cialo() (gołe ciało z włosami), przedmioty() (segmenty), ubierz();
  swiat/test_walki2/aktorzy.py          który moduł gra którą klasę i w jakim stroju (postać odniesienia walki);
  swiat/test_walki2/dane/<klasa>.json   szablon walki: kości, zaczepy i bryły — sprawdzamy, że strój odniesienia
                                        złożony z NASZYCH danych daje dokładnie te same bryły (inaczej BŁĄD DANYCH);
  ustawienia.json                       liczby i teksty pakietu.

Każda bryła jest zapisana w układzie ŚRODKA CZĘŚCI KOŚCI rigu Roblox (przód −Z), czyli tak, jak trzyma się kości
w szablonie walki (budowa/szablon.luau: WeldConstraint do części kości w spoczynku). Dzięki temu klient może złożyć
postać z dowolnego zestawu przedmiotów na tym samym szkielecie i tych samych klipach (EKWIPUNEK.md zasada 0.2).
"""
import collections
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (REPO, os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki2"), TU):
    if _s not in sys.path:
        sys.path.insert(0, _s)

USTAWIENIA = os.path.join(TU, "ustawienia.json")
KATALOG = os.path.join(REPO, "swiat", "postacie", "przedmioty.json")
KATALOG_SKLEPU = os.path.join(REPO, "swiat", "postacie", "sklep_przedmioty.json")
# 27.11.2026 (UI broni, D-167): bronie puli Lv 1–10 Maga i Zwiadowcy — bez brył przymierzalni (czesci = []), na postaci
# akcesorium z ReplicatedStorage/BronieKlas (Ubieranie.luau); przymierzalnia zna je, żeby kowal mógł je założyć
KATALOG_BRONI = os.path.join(REPO, "swiat", "postacie", "bronie_klas_sklep.json")
EKWIPUNEK_BRONI = os.path.join(REPO, "swiat", "postacie", "wynik", "bronie_klas", "ekwipunek.json")  # korekty kota
ID_PULI = "pula"
NAZWA_PULI = "broń Lv 1–10"
ZRODLA = os.path.join(TU, "zrodla")
PLIK_LUAU = "DaneStrojow.luau"
LIMIT_MODULU = 199000        # znaków w jednym module (Roblox: Source do 200 000)
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then\n\treturn {}\nend\n'
SLOTY_GRY = {"Helmet", "Chest", "Gloves", "Boots", "Amulet", "Belt", "Ring", "Trinket", "Weapon"}  # src/shared/Items.luau


class BladDanych(Exception):
    pass


def _czytaj_json(sciezka):
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def _r(x, n=4):
    v = round(float(x), n)
    return 0.0 if v == 0 else v


def modul_stopnia(stopien):
    """Nazwa modułu Roblox z przedmiotami stopnia (las → DaneStrojowLas)."""
    return "DaneStrojow" + stopien[:1].upper() + stopien[1:]


def plik_stopnia(stopien):
    return modul_stopnia(stopien) + ".luau"


def pliki_luau():
    """Wszystkie wygenerowane pliki pakietu (moduł główny pierwszy)."""
    from swiat.postacie import stopnie as ST
    return [PLIK_LUAU] + [plik_stopnia(st) for st in ST.STOPNIE]


# --------------------------------------------------------------------------------------------- ustawienia
def ustawienia():
    U = _czytaj_json(USTAWIENIA)
    if U.get("dobor") not in ("klasa", "cialo"):
        raise BladDanych("ustawienia.dobor: „klasa” albo „cialo”")
    if U.get("spodnie") not in ("czesc_zbroi", "osobny_slot"):
        raise BladDanych("ustawienia.spodnie: „czesc_zbroi” albo „osobny_slot”")
    sloty = [s[0] for s in U["sloty"]]
    if len(set(sloty)) != len(sloty) or "Legs" not in sloty:
        raise BladDanych("ustawienia.sloty: bez powtórzeń, z „Legs” (spodnie jako osobny slot)")
    if not U["klasy"]:
        raise BladDanych("ustawienia.klasy: pusta lista")
    return U


# --------------------------------------------------------------------------------------------- bryły w układzie kości
class _Materialy:
    """Wspólna lista materiałów biblioteki (nazwy jak w postac.py); w Luau — pary (materiał Roblox, Reflectance)."""

    def __init__(self):
        self.lista = []

    def roblox(self):
        from swiat.postacie.biblioteka.roblox_klocki import MATERIALY_ROBLOX
        return [[MATERIALY_ROBLOX[m][0], MATERIALY_ROBLOX[m][1]] for m in self.lista]


def _wiersze(czesci_json, indeks, mat, uwagi, skad):
    """Bryły biblioteki (Postac.json()["czesci"]) -> wiersze rigu Roblox (roblox_klocki._czesci, ta sama zamiana
    układów i rozkład na prymitywy co w szablonie walki). Zwraca listę [kość(1…), kształt, nazwa, x, y, z, rx, ry, rz,
    sx, sy, sz, kolor, materiał biblioteki, grupa, siatka] — położenie jak w rig() (spoczynek, początek = ziemia)."""
    from swiat.postacie.biblioteka import roblox_klocki as RK
    lokalne = []
    wynik = RK._czesci(czesci_json, indeks, 0, lokalne, uwagi, skad)
    for w in wynik:
        m = lokalne[w[13]]
        if m not in mat.lista:
            mat.lista.append(m)
        w[13] = m
    return wynik


def _wzgledem(w, srodek, mat):
    """Wiersz rigu -> bryła w układzie środka części kości: [kształt, nazwa, x, y, z, rx, ry, rz, sx, sy, sz, kolor,
    materiał (1…), siatka] (kąty w radianach jak CFrame.fromOrientation)."""
    return [w[1], w[2], _r(w[3] - srodek[0]), _r(w[4] - srodek[1]), _r(w[5] - srodek[2]),
            _r(w[6], 5), _r(w[7], 5), _r(w[8], 5), _r(w[9]), _r(w[10]), _r(w[11]), w[12].upper(),
            mat.lista.index(w[13]) + 1, w[15]]


# --------------------------------------------------------------------------------------------- jedna klasa
def _klasa(klucz, U, katalog, mat, uwagi):
    import aktorzy as A
    from swiat.postacie.biblioteka import roblox_klocki as RK
    from swiat.postacie.ekwipunek import ubierz
    if klucz not in A.PO_KLUCZU:
        raise BladDanych("klasa %s: nie ma aktora w swiat/test_walki2/aktorzy.py" % klucz)
    wpis = A.PO_KLUCZU[klucz]
    if wpis["rola"] != "klasa":
        raise BladDanych("klasa %s: aktor nie jest klasą gracza" % klucz)
    mod = A._modul(wpis)
    for nazwa in ("cialo", "przedmioty", "wybierz", "KANON", "STROJE", "CIALO_TYP"):
        if not hasattr(mod, nazwa):
            raise BladDanych("moduł %s nie ma %s (kontrakt EKWIPUNEK.md pkt 4)" % (wpis["model"], nazwa))
    korekty = getattr(mod, "KOREKTY_CHWYTU", None)
    cialo = mod.cialo()
    if wpis.get("skala"):
        cialo.skala = float(wpis["skala"])
    prz = mod.przedmioty()
    po_id = {p.id: p for p in prz}
    odniesienie = list(mod.STROJE[wpis["stroj"]] if wpis.get("stroj") else mod.KANON)
    for i in odniesienie:
        if i not in po_id:
            raise BladDanych("klasa %s: strój odniesienia ma nieznany przedmiot %s" % (klucz, i))

    r0 = RK.rig(cialo)
    kosci = r0["kosci"]
    indeks = {k[0]: i + 1 for i, k in enumerate(kosci)}
    for n in cialo.kosci:
        indeks.setdefault(n, 0)
    srodki = {k[0]: k[5:8] for k in kosci}
    nazwa_kosci = {i + 1: k[0] for i, k in enumerate(kosci)}

    def wzgledem(wiersze):
        grupy = collections.OrderedDict()
        for w in wiersze:
            kosc = nazwa_kosci[w[0]]
            grupy.setdefault(kosc, []).append(_wzgledem(w, srodki[kosc], mat))
        return grupy

    # --- gołe ciało: bryły (wszystkie z polem golas — zdejmuje je powłoka na tej kości) i akcesoria ciała (włosy)
    cj = cialo.json()
    if len(cj["czesci"]) != len(cialo.czesci):
        raise BladDanych("klasa %s: Postac.json() zmienił liczbę brył" % klucz)
    nie_gole = [c["n"] for c in cialo.czesci if not c.get("golas")]
    if nie_gole:
        raise BladDanych("klasa %s: bryły ciała bez pola golas: %s" % (klucz, ", ".join(nie_gole[:5])))
    golas = [{"kosc": k, "czesci": v}
             for k, v in wzgledem(_wiersze(cj["czesci"], indeks, mat, uwagi, "ciało %s" % klucz)).items()]
    znaczniki = {z[0].id: getattr(z[0], "znacznik", None) for z in cialo.zalozone}
    akcesoria = []
    for a in cj["akcesoria"]:
        wiersze = _wiersze(a["czesci"], indeks, mat, uwagi, "akcesorium ciała %s" % a["id"])
        gr = wzgledem(wiersze)
        if list(gr) != [a["kosc"]]:
            raise BladDanych("akcesorium ciała %s: bryły na kościach %s" % (a["id"], list(gr)))
        akcesoria.append({"id": a["id"], "znacznik": znaczniki.get(a["id"]), "kosc": a["kosc"],
                          "czesci": gr[a["kosc"]]})

    # --- przedmioty: każdy osobno zakładany na gołe ciało (ubierz z korektami chwytu bohatera)
    def opisz(p, kat):
        """Jeden przedmiot (dzisiejszy albo stopnia) jako wpis danych: pola katalogu + segmenty w układzie kości."""
        opis = p.opis(korekty)
        for pole in ("slot", "cialo", "klasy", "czesc_od", "ukrywa"):
            if kat.get(pole) != opis.get(pole):
                raise BladDanych("przedmiot %s: pole %s w katalogu (%r) ≠ moduł (%r) — katalog nieaktualny"
                                 % (p.id, pole, kat.get(pole), opis.get(pole)))
        seg_kat = [(c["id"], c.get("kosc"), c.get("zakrywa")) for c in kat["czesci"]]
        if p.segmenty and opis["czesci"]:
            # katalog zapisuje zaczep standardowy (bez korekty kota), więc porównujemy id, a kość i powłokę tylko
            # dla segmentów kostnych
            seg_mod = [(c["id"], c["kosc"] if s["kosc"] else None, c["zakrywa"])
                       for c, s in zip(opis["czesci"], p.segmenty)]
            seg_kat2 = [(i, k if s["kosc"] else None, z) for (i, k, z), s in zip(seg_kat, p.segmenty)]
            if seg_mod != seg_kat2 or len(seg_kat) != len(p.segmenty):
                raise BladDanych("przedmiot %s: segmenty w katalogu ≠ moduł (%s ≠ %s)" % (p.id, seg_kat, seg_mod))
        ubrany = ubierz(cialo, [p], korekty=korekty)
        uj = ubrany.json()
        n_kostne = sum(len(s["akc"].czesci) for s in p.segmenty if s["kosc"])
        kostne = uj["czesci"][len(uj["czesci"]) - n_kostne:] if n_kostne else []
        segmenty = []
        k = 0
        for s in p.segmenty:
            if s["kosc"]:
                lista = kostne[k:k + len(s["akc"].czesci)]
                k += len(s["akc"].czesci)
                if [c["n"] for c in lista] != [c["n"] for c in s["akc"].czesci]:
                    raise BladDanych("przedmiot %s: kolejność brył po ubierz() inna niż w segmencie" % p.id)
                gr = wzgledem(_wiersze(lista, indeks, mat, uwagi, "przedmiot %s" % p.id))
                if list(gr) != [s["kosc"]]:
                    raise BladDanych("przedmiot %s: segment %s ma bryły na kościach %s" % (p.id, s["akc"].id, list(gr)))
                segmenty.append({"id": s["akc"].id, "kosc": s["kosc"], "zakrywa": s["zakrywa"], "grupa": None,
                                 "czesci": gr[s["kosc"]]})
            else:
                a = next((x for x in uj["akcesoria"] if x["id"] == s["akc"].id), None)
                if a is None:
                    raise BladDanych("przedmiot %s: po ubierz() brak akcesorium %s" % (p.id, s["akc"].id))
                gr = wzgledem(_wiersze(a["czesci"], indeks, mat, uwagi, "przedmiot %s" % p.id))
                if list(gr) != [a["kosc"]]:
                    raise BladDanych("przedmiot %s: akcesorium na kościach %s" % (p.id, list(gr)))
                segmenty.append({"id": s["akc"].id, "kosc": a["kosc"], "zakrywa": False, "grupa": a["id"],
                                 "zaczep": a["zaczep"], "czesci": gr[a["kosc"]]})
        return collections.OrderedDict([
            ("nazwa", kat["nazwa"]), ("slot", kat["slot"]), ("kategoria", kat["kategoria"]), ("cialo", kat["cialo"]),
            ("klasy", list(kat["klasy"])), ("czescOd", kat["czesc_od"]), ("ukrywa", list(kat["ukrywa"])),
            ("zestaw", kat["zestaw"]), ("segmenty", segmenty)])

    przedmioty = collections.OrderedDict()
    po_katalogu = {p["id"]: p for p in katalog["przedmioty"]}
    for p in prz:
        if p.id not in po_katalogu:
            raise BladDanych("przedmiot %s (moduł %s) nie ma wpisu w swiat/postacie/przedmioty.json — "
                             "uruchom zestawienie.py --tylko json" % (p.id, wpis["model"]))
        przedmioty[p.id] = opisz(p, po_katalogu[p.id])

    # kolejność przedmiotów: najpierw strój odniesienia (jak w szablonie walki), potem reszta jak w module
    kolejnosc = odniesienie + [p.id for p in prz if p.id not in odniesienie]
    nazwy = getattr(mod, "NAZWY_STROJOW", {})
    zestawy = [{"id": n, "nazwa": nazwy.get(n, n), "przedmioty": list(v)} for n, v in mod.STROJE.items()]
    zestawy.append({"id": "komplet", "nazwa": "komplet (wygląd z walki)", "przedmioty": list(odniesienie)})

    # wzrost postaci odniesienia w spoczynku (kamera przymierzalni)
    from geometria import Rig, obwiednia
    ref = RK.rig(ubierz(cialo, [po_id[i] for i in odniesienie], korekty=korekty))
    mn, mx = obwiednia(Rig(ref))
    K = {"klucz": klucz, "nazwa": wpis["nazwa"], "model": wpis["model"], "cialo": mod.CIALO_TYP,
         "odniesienie": odniesienie, "przedmioty": kolejnosc, "zestawy": zestawy,
         "wysokosc": _r(mx[1], 3), "szerokosc": _r(mx[0] - mn[0], 3),
         "hrp": [_r(v) for v in r0["hrp"]],
         "kosci": [[k[0], k[1]] + [_r(v) for v in k[2:11]] + [k[11]] for k in kosci],
         "zaczepy": [[z[0], z[1]] + [_r(v) for v in z[2:5]] + [_r(v, 5) for v in z[5:8]] for z in r0["zaczepy"]],
         "golas": golas, "akcesoria": akcesoria}
    return K, przedmioty, {"wpis": wpis, "mod": mod, "cialo": cialo, "przedmioty": prz, "korekty": korekty, "rig0": r0,
                           "opisz": opisz}


def _stopnie_klasy(klucz, K, pom, sklep):
    """Przedmioty trzech stopni klasy (swiat/postacie/stopnie.py, wpisy z sklep_przedmioty.json) — te same kontrole
    pól i ten sam zapis brył co dzisiejsze. Wołane PO wszystkich klasach, żeby materiały dzisiejszych brył zachowały
    swoje numery. Dopisuje do K: stopnie (lista {id, nazwa, przedmioty}) i zestawy kompletów stopni."""
    from swiat.postacie import stopnie as ST
    if ST.BOHATER.get(klucz) != pom["wpis"]["model"]:
        raise BladDanych("klasa %s: stopnie.py ma dla niej inny moduł bohatera niż aktor walki" % klucz)
    po_sklepie = {p["id"]: p for p in sklep["przedmioty"]}
    wynik = collections.OrderedDict()
    K["stopnie"] = []
    zajete = {z["id"] for z in K["zestawy"]}
    for st in ST.STOPNIE:
        prz = ST.przedmioty(klucz, st)
        ids = [p.id for p in prz]
        komplet = list(ST.komplet(klucz, st))
        if set(komplet) - set(ids) or len(set(ids)) != len(ids):
            raise BladDanych("klasa %s, stopień %s: komplet ≠ przedmioty stopnia" % (klucz, st))
        for p in prz:
            kat = po_sklepie.get(p.id)
            if kat is None:
                raise BladDanych("przedmiot %s (stopnie.py) nie ma wpisu w swiat/postacie/sklep_przedmioty.json" % p.id)
            if kat.get("klasa") != klucz or kat.get("stopien") != st:
                raise BladDanych("przedmiot %s: katalog sklepu ma klasę %r i stopień %r, a stopnie.py %s / %s"
                                 % (p.id, kat.get("klasa"), kat.get("stopien"), klucz, st))
            P = pom["opisz"](p, kat)
            P["stopien"] = st
            wynik[p.id] = P
        if st in zajete:
            raise BladDanych("klasa %s: zestaw o nazwie stopnia %s już istnieje" % (klucz, st))
        kolejnosc = komplet + [i for i in ids if i not in komplet]
        K["stopnie"].append({"id": st, "nazwa": ST.NAZWY_STOPNI[st], "przedmioty": kolejnosc})
        K["zestawy"].append({"id": st, "nazwa": "komplet %s" % ST.NAZWY_STOPNI[st], "przedmioty": komplet})
        pom.setdefault("stopnie", {})[st] = prz
    return wynik


def _bronie_puli(klucz, K):
    """Bronie puli klasy z bronie_klas_sklep.json → przedmioty bez segmentów z polem „akcesorium” (nazwa modelu
    w BronieKlas, zaczep dłoni, rodzaj chwytu); w K.stopnie dochodzi stopień „pula” (kolejność według poziomu)."""
    if not os.path.isfile(KATALOG_BRONI):
        return collections.OrderedDict()
    wpisy = sorted((p for p in _czytaj_json(KATALOG_BRONI)["przedmioty"] if p["klasa"] == klucz),
                   key=lambda p: (p["poziom"], p["id"]))
    kot = {}
    if os.path.isfile(EKWIPUNEK_BRONI):
        for e in _czytaj_json(EKWIPUNEK_BRONI)["przedmioty"]:
            c = e["czesci"][0]
            kot[e["id"]] = collections.OrderedDict([("zaczep", c["zaczep"]), ("pos", list(c["pos"])),
                                                    ("rot", list(c["rot"]))])
    wynik = collections.OrderedDict()
    for p in wpisy:
        if p["id"] not in kot:
            raise BladDanych("broń puli %s: brak korekty chwytu kota w %s" % (p["id"], os.path.relpath(EKWIPUNEK_BRONI, REPO)))
        if p["slot"] != "Weapon" or p.get("czesci") or not p.get("akcesorium"):
            raise BladDanych("broń puli %s: slot Weapon, bez brył, z akcesorium" % p["id"])
        wynik[p["id"]] = collections.OrderedDict([
            ("nazwa", p["nazwa"]), ("slot", p["slot"]), ("kategoria", p["kategoria"]), ("cialo", p["cialo"]),
            ("klasy", list(p["klasy"])), ("czescOd", None), ("ukrywa", []), ("zestaw", p["zestaw"]),
            ("segmenty", []),
            ("akcesorium", collections.OrderedDict([("nazwa", p["akcesorium"]), ("zaczep", p["zaczep"]),
                                                    ("chwyt", p["chwyt"]), ("lapa", p["lapa"]),
                                                    ("kot", kot[p["id"]])]))])
    if wynik:
        if ID_PULI in [s["id"] for s in K.get("stopnie", [])]:
            raise BladDanych("klasa %s: stopień %s już istnieje" % (klucz, ID_PULI))
        K.setdefault("stopnie", []).append({"id": ID_PULI, "nazwa": NAZWA_PULI, "przedmioty": list(wynik)})
    return wynik


# --------------------------------------------------------------------------------------------- całość
def zbierz():
    """Słownik danych pakietu (to, co trafia do DaneStrojow.luau) + pomocnicze obiekty Pythona (do testów)."""
    from swiat.postacie import stopnie as ST
    U = ustawienia()
    katalog = _czytaj_json(KATALOG)
    sklep = _czytaj_json(KATALOG_SKLEPU)
    mat = _Materialy()
    uwagi = []
    klasy, przedmioty, py = collections.OrderedDict(), collections.OrderedDict(), {}
    for klucz in U["klasy"]:
        K, P, pom = _klasa(klucz, U, katalog, mat, uwagi)
        for i in P:
            if i in przedmioty:
                raise BladDanych("przedmiot %s w dwóch klasach (%s)" % (i, klucz))
        klasy[klucz] = K
        przedmioty.update(P)
        py[klucz] = pom
    # przedmioty stopni (D-106) — po dzisiejszych, żeby dzisiejsze bryły i numery ich materiałów zostały bez zmian
    for klucz in klasy:
        P = _stopnie_klasy(klucz, klasy[klucz], py[klucz], sklep)
        for i in P:
            if i in przedmioty:
                raise BladDanych("przedmiot stopnia %s powtarza istniejący (%s)" % (i, klucz))
        przedmioty.update(P)
    for klucz in klasy:
        P = _bronie_puli(klucz, klasy[klucz])
        for i in P:
            if i in przedmioty:
                raise BladDanych("broń puli %s powtarza istniejący przedmiot (%s)" % (i, klucz))
        przedmioty.update(P)
    for z in U["zestawy_okna"]:
        for klucz, K in klasy.items():
            if z not in [x["id"] for x in K["zestawy"]]:
                raise BladDanych("ustawienia.zestawy_okna: klasa %s nie ma zestawu %s" % (klucz, z))
    sloty_ok = {s[0] for s in U["sloty"]}
    for i, P in przedmioty.items():
        if P["slot"] not in sloty_ok:
            raise BladDanych("przedmiot %s: slot %s spoza ustawienia.sloty" % (i, P["slot"]))
        if P["czescOd"] and P["czescOd"] not in przedmioty:
            raise BladDanych("przedmiot %s: czesc_od %s nie istnieje" % (i, P["czescOd"]))
    D = collections.OrderedDict()
    D["wersja"] = 1
    D["kontener"] = U["kontener"]
    D["atrybut"] = U["atrybut_gracza"]
    D["dobor"] = U["dobor"]
    D["spodnie"] = U["spodnie"]
    D["sloty"] = [{"id": s[0], "nazwa": s[1]} for s in U["sloty"]]
    D["slotyGry"] = sorted(SLOTY_GRY)
    D["zestawyOkna"] = list(U["zestawy_okna"])
    D["limit"] = U["limit_zapytan_s"]
    D["klipyPodgladu"] = list(U["klipy_podgladu"])
    D["nazwyRuchow"] = U["nazwy_ruchow"]
    D["stojak"] = U["stojak"]
    D["kamera"] = U["kamera"]
    D["ui"] = U["ui"]
    D["teksty"] = U["teksty"]
    D["materialy"] = mat.roblox()
    D["kolejnoscKlas"] = list(klasy)
    D["modulyStopni"] = [{"id": st, "modul": modul_stopnia(st)} for st in ST.STOPNIE]
    D["brakStopni"] = []
    D["klasy"] = klasy
    D["przedmioty"] = przedmioty
    D["uwagi"] = uwagi
    tekst = json.dumps(D, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    D["skrot"] = hashlib.sha1(tekst.encode("utf-8")).hexdigest()[:12]
    sprawdz_z_walka(D, py)
    return D, py


# --------------------------------------------------------------------------------------------- składanie (lustro Luau)
def zloz(D, klucz, plan):
    """Bryły postaci z planu stroju (logika_strojow.plan) jako wiersze rigu walki — to samo, co robi Ubieranie.luau:
    gołe bryły kości bez powłoki, akcesoria ciała bez schowanych znaczników, segmenty przedmiotów. Wiersz:
    [kość(1…), kształt, nazwa, x, y, z, rx, ry, rz, sx, sy, sz, kolor, materiał (Roblox, Reflectance), grupa, siatka],
    położenie w układzie modelu (spoczynek), grupa = nazwa grupy („Cialo” dla brył na kościach)."""
    K = D["klasy"][klucz]
    indeks = {k[0]: i + 1 for i, k in enumerate(K["kosci"])}
    srodki = {k[0]: k[5:8] for k in K["kosci"]}

    def wiersz(c, kosc, grupa):
        s = srodki[kosc]
        return [indeks[kosc], c[0], c[1], _r(s[0] + c[2]), _r(s[1] + c[3]), _r(s[2] + c[4]), c[5], c[6], c[7],
                c[8], c[9], c[10], c[11], tuple(D["materialy"][c[12] - 1]), grupa, c[13]]

    wynik = []
    for g in K["golas"]:
        if g["kosc"] not in plan["zakryte"]:
            wynik += [wiersz(c, g["kosc"], "Cialo") for c in g["czesci"]]
    for a in K["akcesoria"]:
        if not (a["znacznik"] and a["znacznik"] in plan["ukryte"]):
            wynik += [wiersz(c, a["kosc"], a["id"]) for c in a["czesci"]]
    for i in plan["przedmioty"]:
        for s in D["przedmioty"][i]["segmenty"]:
            wynik += [wiersz(c, s["kosc"], s["grupa"] or "Cialo") for c in s["czesci"]]
    return wynik


def klucz_bryly(w):
    """Porównanie brył bez kolejności: (kość, kształt, nazwa, położenie, kąty, rozmiar, kolor, materiał, grupa, siatka)."""
    return (w[0], w[1], w[2], tuple(round(v, 3) for v in w[3:6]), tuple(round(v, 4) for v in w[6:9]),
            tuple(round(v, 4) for v in w[9:12]), w[12].upper(), tuple(w[13]), w[14], w[15])


def wiersze_walki(d):
    """Bryły z swiat/test_walki2/dane/<klasa>.json w formacie zloz() (materiał i grupa po nazwie)."""
    return [list(c[:13]) + [tuple(d["materialy"][c[13]]), d["grupy"][c[14]], c[15]] for c in d["czesci"]]


def sprawdz_z_walka(D, py):
    """Szkielet i strój odniesienia z naszych danych = szablon walki (dane/<klasa>.json): kości, zaczepy, HRP i
    multizbiór brył. Rozjazd = BladDanych (dane walki albo moduł bohatera zmieniły się bez przebudowy)."""
    import aktorzy as A
    import logika_strojow as L
    for klucz, K in D["klasy"].items():
        try:
            d = A.wczytaj(klucz)
        except FileNotFoundError as e:
            raise BladDanych(str(e))
        r0 = py[klucz]["rig0"]
        if r0["kosci"] != d["kosci"]:
            raise BladDanych("klasa %s: kości gołego ciała ≠ szablon walki (dane/%s.json)" % (klucz, klucz))
        if r0["zaczepy"] != d["zaczepy"] or r0["hrp"] != d["hrp"]:
            raise BladDanych("klasa %s: zaczepy albo HRP gołego ciała ≠ szablon walki" % klucz)
        ok, plan = L.plan(D, klucz, K["odniesienie"])
        if not ok:
            raise BladDanych("klasa %s: strój odniesienia odrzucony przez logikę (%s)" % (klucz, plan))
        nasze = collections.Counter(klucz_bryly(w) for w in zloz(D, klucz, plan))
        walki = collections.Counter(klucz_bryly(w) for w in wiersze_walki(d))
        if nasze != walki:
            brak = list((walki - nasze).elements())[:3]
            nadmiar = list((nasze - walki).elements())[:3]
            raise BladDanych("klasa %s: strój odniesienia z danych ≠ szablon walki (brak %d: %s; nadmiar %d: %s)"
                             % (klucz, sum((walki - nasze).values()), brak, sum((nasze - walki).values()), nadmiar))


# --------------------------------------------------------------------------------------------- Luau
def _napis(s):
    return json.dumps(s, ensure_ascii=False)


def _liczba(x):
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, int):
        return str(x)
    v = round(float(x), 5)
    if v == int(v) and abs(v) < 1e9:
        return str(int(v))
    return repr(v)


def _klucz(k):
    import re
    return k if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", k) else "[%s]" % _napis(k)


def _luau(v, wciecie=1):
    if v is None:
        return "nil"
    if isinstance(v, (bool, int, float)):
        return _liczba(v)
    if isinstance(v, str):
        return _napis(v)
    tab = "\t" * wciecie
    if isinstance(v, (list, tuple)):
        czesci = [_luau(x, wciecie + 1) for x in v]
        jedna = "{ " + ", ".join(czesci) + " }" if czesci else "{}"
        if len(jedna) <= 150 and "\n" not in jedna:
            return jedna
        return "{\n" + "".join(tab + c + ",\n" for c in czesci) + "\t" * (wciecie - 1) + "}"
    if isinstance(v, dict):
        czesci = ["%s = %s" % (_klucz(k), _luau(x, wciecie + 1)) for k, x in v.items() if x is not None]
        jedna = "{ " + ", ".join(czesci) + " }" if czesci else "{}"
        if len(jedna) <= 150 and "\n" not in jedna:
            return jedna
        return "{\n" + "".join(tab + c + ",\n" for c in czesci) + "\t" * (wciecie - 1) + "}"
    raise TypeError(repr(v))


def _bryly_luau(lista, wciecie):
    """Bryły jedna w wierszu (zwięźle: bez spacji)."""
    tab = "\t" * wciecie
    return "{\n" + "".join(tab + "{" + ",".join(_luau(x) for x in c) + "},\n" for c in lista) + "\t" * (wciecie - 1) + "}"


def _przedmiot_luau(tab, i, P):
    """Dwie instrukcje Luau jednego przedmiotu: pola i segmenty (bryły jedna w wierszu). tab = „D.przedmioty” | „P”."""
    meta = collections.OrderedDict((k, v) for k, v in P.items() if k != "segmenty")
    segs = []
    for s in P["segmenty"]:
        pola = "id = %s, kosc = %s, zakrywa = %s" % (_napis(s["id"]), _napis(s["kosc"]), _luau(s["zakrywa"]))
        if s["grupa"]:
            pola += ", grupa = %s, zaczep = %s" % (_napis(s["grupa"]), _napis(s["zaczep"]))
        segs.append("\t{ %s, czesci = %s }" % (pola, _bryly_luau(s["czesci"], 2)))
    if not segs:   # broń puli Lv 1–10: bez brył (akcesorium z BronieKlas)
        return ["%s[%s] = %s" % (tab, _napis(i), _luau(meta, 1)), "%s[%s].segmenty = {}" % (tab, _napis(i))]
    return ["%s[%s] = %s" % (tab, _napis(i), _luau(meta, 1)),
            "%s[%s].segmenty = {\n%s,\n}" % (tab, _napis(i), ",\n".join(segs))]


SCALENIE = """-- Przedmioty stopni (D-106) leżą w osobnych modułach obok (granica długości jednego modułu). Scalenie jest TUTAJ, więc
-- każdy czytelnik dalej bierze jedno D. Moduł szukany obok tego modułu, a gdy go tam nie ma — w
-- Workspace/<kontener>/Moduly. Gdy modułu stopnia nie ma wcale (np. test wczytujący sam ten plik), stopnia po prostu
-- nie ma w danych: znika z list klas i z zestawów, a jego nazwa trafia do D.brakStopni.
local function modulStopnia(nazwa)
	local obok = script and script.Parent
	local m = obok and obok:FindFirstChild(nazwa)
	if m == nil then
		local kontener = workspace and workspace:FindFirstChild(D.kontener)
		local folder = kontener and kontener:FindFirstChild("Moduly")
		m = folder and folder:WaitForChild(nazwa, 5)
	end
	return m
end

local function bezStopnia(lista, stopien)
	local wynik = {}
	for _, x in lista do
		if x.id ~= stopien then
			table.insert(wynik, x)
		end
	end
	return wynik
end

for _, s in D.modulyStopni do
	local m = modulStopnia(s.modul)
	if m ~= nil then
		for id, P in require(m) do
			D.przedmioty[id] = P
		end
	else
		table.insert(D.brakStopni, s.id)
		for _, K in D.klasy do
			K.stopnie = bezStopnia(K.stopnie, s.id)
			K.zestawy = bezStopnia(K.zestawy, s.id)
		end
	end
end
"""


def luau_teksty(D):
    """{plik: tekst} — moduł główny (dane bez brył zwykłym zapisem, bryły jedna w wierszu, dzisiejsze przedmioty,
    scalenie) i po jednym module na stopień (same przedmioty stopnia)."""
    glowa = ("--[[\n\tDaneStrojow — WYGENEROWANE przez swiat/stroje_proba/dane.py (nie edytuj ręcznie), skrót %s.\n"
             "\tŹródła: swiat/postacie/przedmioty.json, moduły bohaterów (cialo(), przedmioty()), ustawienia.json;\n"
             "\tprzedmioty stopni (swiat/postacie/stopnie.py, sklep_przedmioty.json) w modułach %s — scalane na końcu.\n"
             "\tBryła = { kształt (0 klocek, 1 kula, 2 walec, 3 klin, 4 narożnik), nazwa, x, y, z, rx, ry, rz, sx, sy, sz,\n"
             "\t          kolor, materiał (indeks w materialy), siatka (\"\" albo SpecialMesh) } — w układzie środka\n"
             "\t          części kości (kąty w radianach dla CFrame.fromOrientation).\n"
             "\tKość = { nazwa, rodzic (0 = HumanoidRootPart), staw xyz, środek xyz, rozmiar xyz, nazwa stawu Motor6D }.\n"
             "]]\n" % (D["skrot"], ", ".join(s["modul"] for s in D["modulyStopni"])))
    linie = [glowa + STRAZNIK, "local D = {}"]
    for k in ("wersja", "skrot", "kontener", "atrybut", "dobor", "spodnie", "sloty", "slotyGry", "zestawyOkna", "limit",
              "klipyPodgladu", "nazwyRuchow", "stojak", "kamera", "ui", "teksty", "materialy", "kolejnoscKlas",
              "modulyStopni", "brakStopni"):
        linie.append("D.%s = %s" % (k, _luau(D[k], 1)))
    linie.append("D.klasy = {}")
    for klucz, K in D["klasy"].items():
        meta = collections.OrderedDict((k, v) for k, v in K.items() if k not in ("golas", "akcesoria", "kosci", "zaczepy"))
        linie.append("D.klasy[%s] = %s" % (_napis(klucz), _luau(meta, 1)))
        linie.append("D.klasy[%s].kosci = %s" % (_napis(klucz), _bryly_luau(K["kosci"], 1)))
        linie.append("D.klasy[%s].zaczepy = %s" % (_napis(klucz), _bryly_luau(K["zaczepy"], 1)))
        g = ",\n".join("\t{ kosc = %s, czesci = %s }" % (_napis(x["kosc"]), _bryly_luau(x["czesci"], 2)) for x in K["golas"])
        linie.append("D.klasy[%s].golas = {\n%s,\n}" % (_napis(klucz), g))
        a = ",\n".join("\t{ id = %s, znacznik = %s, kosc = %s, czesci = %s }"
                       % (_napis(x["id"]), _luau(x["znacznik"]), _napis(x["kosc"]), _bryly_luau(x["czesci"], 2))
                       for x in K["akcesoria"])
        linie.append("D.klasy[%s].akcesoria = {%s}" % (_napis(klucz), ("\n" + a + ",\n") if a else ""))
    linie.append("D.przedmioty = {}")
    for i, P in D["przedmioty"].items():
        if not P.get("stopien"):
            linie += _przedmiot_luau("D.przedmioty", i, P)
    linie.append(SCALENIE + "return D\n")
    teksty = collections.OrderedDict()
    teksty[PLIK_LUAU] = "\n".join(linie)
    for s in D["modulyStopni"]:
        ids = [i for i, P in D["przedmioty"].items() if P.get("stopien") == s["id"]]
        gl = ("--[[\n\t%s — WYGENEROWANE przez swiat/stroje_proba/dane.py (nie edytuj ręcznie), skrót %s.\n"
              "\tPrzedmioty stopnia „%s” (D-106, swiat/postacie/stopnie.py): %d sztuk, zapis jak w DaneStrojow.\n"
              "\tNie czytaj tego modułu wprost — scala go DaneStrojow (materiały brył to indeksy w jego D.materialy).\n"
              "]]\n" % (s["modul"], D["skrot"], s["id"], len(ids)))
        l2 = [gl + STRAZNIK, "local P = {}"]
        for i in ids:
            l2 += _przedmiot_luau("P", i, D["przedmioty"][i])
        l2.append("return P\n")
        teksty[s["modul"] + ".luau"] = "\n".join(l2)
    for plik, tekst in teksty.items():
        if len(tekst) > LIMIT_MODULU:
            raise BladDanych("%s ma %d znaków — ponad granicę %d (podziel dane na więcej modułów)"
                             % (plik, len(tekst), LIMIT_MODULU))
    return teksty


def luau_tekst(D):
    """Tekst modułu głównego (DaneStrojow.luau)."""
    return luau_teksty(D)[PLIK_LUAU]


def zapisz(folder):
    """Zapisuje wszystkie moduły danych jednym przebiegiem (najpierw moduły stopni, na końcu moduł główny)."""
    D, _ = zbierz()
    teksty = luau_teksty(D)
    os.makedirs(folder, exist_ok=True)
    for plik in list(teksty)[1:] + [PLIK_LUAU]:
        with open(os.path.join(folder, plik), "w", encoding="utf-8", newline="\n") as f:
            f.write(teksty[plik])
    return D


def aktualny():
    D, py = zbierz()
    for plik, tekst in luau_teksty(D).items():
        sciezka = os.path.join(ZRODLA, plik)
        if not os.path.isfile(sciezka):
            return False, D
        with open(sciezka, encoding="utf-8") as f:
            if f.read() != tekst:
                return False, D
    return True, D


def rozmiary(D):
    return ", ".join("%s %d" % (plik, len(tekst)) for plik, tekst in luau_teksty(D).items())


def podsumowanie(D):
    linie = []
    for klucz, K in D["klasy"].items():
        n_g = sum(len(g["czesci"]) for g in K["golas"])
        n_a = sum(len(a["czesci"]) for a in K["akcesoria"])
        n_p = sum(len(s["czesci"]) for i in K["przedmioty"] for s in D["przedmioty"][i]["segmenty"])
        linie.append("  %-10s %-10s ciało %-8s kości %2d · gołe bryły %3d (+%d akcesoria ciała) · przedmioty %d (%d brył)"
                     " · odniesienie: %s" % (klucz, K["model"], K["cialo"], len(K["kosci"]), n_g, n_a,
                                              len(K["przedmioty"]), n_p, ", ".join(K["odniesienie"])))
        for st in K.get("stopnie", []):
            n_s = sum(len(s["czesci"]) for i in st["przedmioty"] for s in D["przedmioty"][i]["segmenty"])
            linie.append("  %-10s stopień %-8s przedmioty %d (%d brył)" % ("", st["id"], len(st["przedmioty"]), n_s))
    return linie


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    try:
        if "--sprawdz" in argv:
            ok, D = aktualny()
            print("DaneStrojow*.luau: %s (skrót %s, %d przedmiotów; znaków: %s)"
                  % ("aktualny" if ok else "NIEAKTUALNY", D["skrot"], len(D["przedmioty"]), rozmiary(D)))
            for linia in podsumowanie(D):
                print(linia)
            return 0 if ok else 1
        folder = argv[argv.index("--wyjscie") + 1] if "--wyjscie" in argv else ZRODLA
        D = zapisz(folder)
        print("zapisano w %s (skrót %s, %d przedmiotów; znaków: %s)"
              % (os.path.relpath(folder, REPO) if folder == ZRODLA else folder, D["skrot"], len(D["przedmioty"]),
                 rozmiary(D)))
        for linia in podsumowanie(D):
            print(linia)
        for u in D["uwagi"]:
            print("  uwaga:", u)
        return 0
    except BladDanych as e:
        print("BŁĄD DANYCH: %s" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
