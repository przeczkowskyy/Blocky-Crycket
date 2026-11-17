#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator zrodla/DaneStrojow.luau — gołe ciała bohaterów i przedmioty z katalogu jako części Roblox (D-071, próba).

    python -B swiat/stroje_proba/dane.py               # zapisuje zrodla/DaneStrojow.luau
    python -B swiat/stroje_proba/dane.py --sprawdz     # kod 1, gdy plik w zrodla/ jest nieaktualny albo dane się nie zgadzają
    python -B swiat/stroje_proba/dane.py --wyjscie DIR # zapis do innego folderu (test powtarzalności)

Źródła (tylko odczyt, nic tam nie zmieniamy):
  swiat/postacie/przedmioty.json        katalog: id, nazwa, slot, klasy, typ ciała, czesc_od, ukrywa, segmenty;
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
ZRODLA = os.path.join(TU, "zrodla")
PLIK_LUAU = "DaneStrojow.luau"
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
    przedmioty = collections.OrderedDict()
    po_katalogu = {p["id"]: p for p in katalog["przedmioty"]}
    for p in prz:
        if p.id not in po_katalogu:
            raise BladDanych("przedmiot %s (moduł %s) nie ma wpisu w swiat/postacie/przedmioty.json — "
                             "uruchom zestawienie.py --tylko json" % (p.id, wpis["model"]))
        kat = po_katalogu[p.id]
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
        przedmioty[p.id] = {"nazwa": kat["nazwa"], "slot": kat["slot"], "kategoria": kat["kategoria"],
                            "cialo": kat["cialo"], "klasy": list(kat["klasy"]), "czescOd": kat["czesc_od"],
                            "ukrywa": list(kat["ukrywa"]), "zestaw": kat["zestaw"], "segmenty": segmenty}

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
    return K, przedmioty, {"wpis": wpis, "mod": mod, "cialo": cialo, "przedmioty": prz, "korekty": korekty, "rig0": r0}


# --------------------------------------------------------------------------------------------- całość
def zbierz():
    """Słownik danych pakietu (to, co trafia do DaneStrojow.luau) + pomocnicze obiekty Pythona (do testów)."""
    U = ustawienia()
    katalog = _czytaj_json(KATALOG)
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


def luau_tekst(D):
    """Moduł Luau: dane bez brył zwykłym zapisem, bryły jedna w wierszu."""
    glowa = ("--[[\n\tDaneStrojow — WYGENEROWANE przez swiat/stroje_proba/dane.py (nie edytuj ręcznie), skrót %s.\n"
             "\tŹródła: swiat/postacie/przedmioty.json, moduły bohaterów (cialo(), przedmioty()), ustawienia.json.\n"
             "\tBryła = { kształt (0 klocek, 1 kula, 2 walec, 3 klin, 4 narożnik), nazwa, x, y, z, rx, ry, rz, sx, sy, sz,\n"
             "\t          kolor, materiał (indeks w materialy), siatka (\"\" albo SpecialMesh) } — w układzie środka\n"
             "\t          części kości (kąty w radianach dla CFrame.fromOrientation).\n"
             "\tKość = { nazwa, rodzic (0 = HumanoidRootPart), staw xyz, środek xyz, rozmiar xyz, nazwa stawu Motor6D }.\n"
             "]]\n" % D["skrot"])
    linie = [glowa + STRAZNIK, "local D = {}"]
    for k in ("wersja", "skrot", "kontener", "atrybut", "dobor", "spodnie", "sloty", "slotyGry", "zestawyOkna", "limit",
              "klipyPodgladu", "nazwyRuchow", "stojak", "kamera", "ui", "teksty", "materialy", "kolejnoscKlas"):
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
        meta = collections.OrderedDict((k, v) for k, v in P.items() if k != "segmenty")
        linie.append("D.przedmioty[%s] = %s" % (_napis(i), _luau(meta, 1)))
        segs = []
        for s in P["segmenty"]:
            pola = "id = %s, kosc = %s, zakrywa = %s" % (_napis(s["id"]), _napis(s["kosc"]), _luau(s["zakrywa"]))
            if s["grupa"]:
                pola += ", grupa = %s, zaczep = %s" % (_napis(s["grupa"]), _napis(s["zaczep"]))
            segs.append("\t{ %s, czesci = %s }" % (pola, _bryly_luau(s["czesci"], 2)))
        linie.append("D.przedmioty[%s].segmenty = {\n%s,\n}" % (_napis(i), ",\n".join(segs)))
    linie.append("return D\n")
    return "\n".join(linie)


def zapisz(folder):
    D, _ = zbierz()
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, PLIK_LUAU), "w", encoding="utf-8", newline="\n") as f:
        f.write(luau_tekst(D))
    return D


def aktualny():
    D, py = zbierz()
    sciezka = os.path.join(ZRODLA, PLIK_LUAU)
    if not os.path.isfile(sciezka):
        return False, D
    with open(sciezka, encoding="utf-8") as f:
        return f.read() == luau_tekst(D), D


def podsumowanie(D):
    linie = []
    for klucz, K in D["klasy"].items():
        n_g = sum(len(g["czesci"]) for g in K["golas"])
        n_a = sum(len(a["czesci"]) for a in K["akcesoria"])
        n_p = sum(len(s["czesci"]) for i in K["przedmioty"] for s in D["przedmioty"][i]["segmenty"])
        linie.append("  %-10s %-10s ciało %-8s kości %2d · gołe bryły %3d (+%d akcesoria ciała) · przedmioty %d (%d brył)"
                     " · odniesienie: %s" % (klucz, K["model"], K["cialo"], len(K["kosci"]), n_g, n_a,
                                              len(K["przedmioty"]), n_p, ", ".join(K["odniesienie"])))
    return linie


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    try:
        if "--sprawdz" in argv:
            ok, D = aktualny()
            print("DaneStrojow.luau: %s (skrót %s, %d znaków)" % ("aktualny" if ok else "NIEAKTUALNY", D["skrot"],
                                                                len(luau_tekst(D))))
            for linia in podsumowanie(D):
                print(linia)
            return 0 if ok else 1
        folder = argv[argv.index("--wyjscie") + 1] if "--wyjscie" in argv else ZRODLA
        D = zapisz(folder)
        print("zapisano %s (skrót %s, %d znaków)" % (os.path.join(os.path.relpath(folder, REPO) if folder == ZRODLA
                                                                   else folder, PLIK_LUAU), D["skrot"], len(luau_tekst(D))))
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
