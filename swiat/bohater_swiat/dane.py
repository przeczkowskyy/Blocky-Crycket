#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator zrodla/DaneBohatera.luau — liczby pakietu „bohater w świecie” (propozycja, prototyp w Studio).

    python -B swiat/bohater_swiat/dane.py               # zapisuje zrodla/DaneBohatera.luau
    python -B swiat/bohater_swiat/dane.py --sprawdz     # kod 1, gdy plik w zrodla/ jest nieaktualny albo dane się nie zgadzają
    python -B swiat/bohater_swiat/dane.py --wyjscie DIR # zapis do innego folderu (test powtarzalności)

Źródła (TYLKO ODCZYT — pakiet niczego tam nie zmienia, walki zostają bajt w bajt takie same):
  ustawienia.json                         liczby, pozy proceduralne i nazwy tego pakietu;
  swiat/test_walki2/aktorzy.py            która akcja (spoczynek, ruch, radosc, upadek) to który klip bohatera;
  swiat/test_walki2/dane/<klasa>.json     rig i klipy bohatera (te same, które gra walka) — stąd prędkość naturalna
                                          chodu, podniesienie rigu w chodzie i opuszczenie bioder w pozach;
  swiat/stroje_proba/dane.py              nazwa atrybutu stroju gracza i liczby brył bohatera w stroju (do raportu).

Co liczy generator (reszta to przepisane ustawienia):
  predkoscChodu       2 · (zakres ruchu stopy przód–tył) / okres klipu chodu — przy tej prędkości postaci klip gra w
                      tempie 1 (klient skaluje tempo prawdziwą prędkością poziomą);
  podniesienieChodu   o ile najniższa bryła nóg schodzi w klipie chodu pod ziemię — o tyle klient unosi rig, gdy gra chód;
  pozy                kąty z ustawień → Transform stawów (radiany); dla póz z „przysiad” opuszczenie bioder takie, żeby
                      najniższa bryła nóg stała na ziemi (kinematyka w przód: swiat/test_walki2/geometria.py).
"""
import collections
import hashlib
import importlib.util
import json
import math
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
WALKA = os.path.join(REPO, "swiat", "test_walki2")
STROJE = os.path.join(REPO, "swiat", "stroje_proba")
# cudze foldery NA KOŃCU ścieżki: mają swoje dane.py i zbuduj.py, a pierwsze muszą zostać moduły tego pakietu
for _s in (REPO, os.path.join(REPO, "tools"), WALKA, STROJE):
    if _s not in sys.path:
        sys.path.append(_s)

USTAWIENIA = os.path.join(TU, "ustawienia.json")
ZRODLA = os.path.join(TU, "zrodla")
PLIK_LUAU = "DaneBohatera.luau"
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then\n\treturn {}\nend\n'
STOPY = ("LeftFoot", "RightFoot")
AKCJE = ("spoczynek", "ruch", "radosc", "upadek")
KLIPY_KONTRAKTU = ["bieg", "skok", "padnij", "rece_gora", "radosc"]   # umowa z pakietem mini-gier (README)


class BladDanych(Exception):
    pass


def _czytaj_json(sciezka):
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def _r(x, n=4):
    v = round(float(x), n)
    return 0.0 if v == 0 else v


def _modul(nazwa, sciezka):
    if nazwa in sys.modules:
        return sys.modules[nazwa]
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nazwa] = m
    spec.loader.exec_module(m)
    return m


def dane_strojow():
    """Moduł swiat/stroje_proba/dane.py pod własną nazwą (ten pakiet też ma dane.py) — tylko odczyt."""
    return _modul("bohater_swiat__dane_strojow", os.path.join(STROJE, "dane.py"))


# --------------------------------------------------------------------------------------------- ustawienia
def ustawienia():
    U = _czytaj_json(USTAWIENIA)
    R = U["ruch"]
    if not 0 < R["prog_ruchu_stop"] < R["prog_ruchu_start"]:
        raise BladDanych("ustawienia.ruch: 0 < prog_ruchu_stop < prog_ruchu_start")
    if not 0 < R["tempo_min"] <= 1 <= R["tempo_max"]:
        raise BladDanych("ustawienia.ruch: 0 < tempo_min ≤ 1 ≤ tempo_max")
    if not R["pochylenie_od"] < R["pochylenie_do"]:
        raise BladDanych("ustawienia.ruch: pochylenie_od < pochylenie_do")
    if U["kontrakt"]["klipy"] != KLIPY_KONTRAKTU:
        raise BladDanych("ustawienia.kontrakt.klipy: umowa z mini-grami to dokładnie %s" % KLIPY_KONTRAKTU)
    # pozy, po które sięga automat ruchu (LogikaBohatera.krok): lot, lądowanie, bieg i trzy klipy umowy grane pozą
    for n in ("skok", "spadanie", "ladowanie", "pochyl", "padnij", "rece_gora"):
        if n not in U["pozy"]:
            raise BladDanych("ustawienia.pozy: brak pozy „%s” (używa jej automat ruchu)" % n)
    W = U["widocznosc"]
    if W["histereza"] < 1 or W["maks_bohaterow"] < 1 or W["okres_daleko"] < 1 or W["budowy_na_klatke"] < 1:
        raise BladDanych("ustawienia.widocznosc: histereza ≥ 1, maks_bohaterow ≥ 1, okres_daleko ≥ 1, budowy_na_klatke ≥ 1")
    B = U["bieg"]
    for k in B["klasy"]:
        if k not in U["klasy_gracza"].values():
            raise BladDanych("ustawienia.bieg.klasy: nieznana klasa %s" % k)
    for k in list(U["klasy_gracza"].values()):
        Bk = bieg_klasy(U, k)
        if not (0 < Bk["podpor_min"] < 0.5 and 0 < Bk["lot_min"] <= 1 and Bk["pasmo"] > 0 and Bk["kadencja_pelna"] > 0
                and 0 < Bk["skala_min"] <= 1 <= Bk["skala_maks"] and Bk["predkosc_min"] > 0):
            raise BladDanych("ustawienia.bieg (%s): 0 < podpor_min < 0,5; 0 < lot_min ≤ 1; pasmo, kadencja_pelna, "
                             "predkosc_min > 0; skala_min ≤ 1 ≤ skala_maks" % k)
        if not (0 < Bk["krok_na_noge"] / 2 < Bk["zasieg_nogi"] < 0.999):
            raise BladDanych("ustawienia.bieg (%s): pół kroku musi być krótsze niż zasieg_nogi < 0,999" % k)
        P = Bk["poly"]
        if not 0 <= P["dzwon_fala_st"] <= P["dzwon_unies_st"]:
            raise BladDanych("ustawienia.bieg.poly: 0 ≤ dzwon_fala_st ≤ dzwon_unies_st (przód szaty nie schodzi pod ziemię)")
        for kosc, wpisy in Bk["dodatki"].items():
            for w in wpisy:
                if len(w) != 8 or w[6] not in (1, 2):
                    raise BladDanych("ustawienia.bieg.dodatki (%s, %s): wpis = 3 stałe, 3 wymachy, harmoniczna 1 | 2, "
                                     "przesunięcie fazy" % (k, kosc))
    if sorted(U["akcje"]) != sorted(AKCJE):
        raise BladDanych("ustawienia.akcje: dokładnie %s" % (AKCJE,))
    return U


def bieg_klasy(U, klucz):
    """Ustawienia biegu jednej klasy: wspólne liczby z nadpisami z bieg.klasy (dodatki: kość klasy zastępuje wspólną)."""
    B = U["bieg"]
    nadpis = B["klasy"].get(klucz, {})
    wynik = {k: v for k, v in B.items() if k != "klasy"}
    for k, v in nadpis.items():
        if k == "dodatki":
            wynik["dodatki"] = collections.OrderedDict(list(B["dodatki"].items()) + list(v.items()))
        elif isinstance(v, dict):
            wynik[k] = dict(B[k], **v)
        else:
            wynik[k] = v
    return wynik


# --------------------------------------------------------------------------------------------- geometria rigu
def najnizej(rig, d, transformy, kosci):
    """Najniższy punkt (y w układzie modelu, ziemia = 0) brył na podanych kościach dla Transform stawów."""
    from geometria import narozniki
    pozy = rig.pozy(transformy)
    idx = {rig.indeks[n] for n in kosci}
    return min(p[1] for c in d["czesci"] if c[0] in idx for p in narozniki(rig.czesc_cf(c, pozy), c[9:12]))


def obwiednia_pozy(rig, transformy):
    from geometria import obwiednia
    return obwiednia(rig, rig.pozy(transformy))


def transformy_pozy(rig, wiersze):
    """Wiersze pozy [kość, x, y, z, rx, ry, rz] → {indeks kości: CFrame} (jak Motor6D.Transform w kliencie)."""
    from geometria import cf, orientacja
    return {rig.indeks[w[0]]: cf((w[1], w[2], w[3]), orientacja(w[4], w[5], w[6])) for w in wiersze}


def _chod(rig, d, klip, kosci_nog):
    """(prędkość naturalna chodu [studs/s], podniesienie rigu [studs]) z klipu chodu."""
    kl = rig.klipy[klip]
    okres = kl["dl"] / float(kl["fps"])
    zakresy, dno = [], 1e9
    for stopa in STOPY:
        i = rig.indeks[stopa]
        zs = []
        for f in range(kl["dl"] + 1):
            t = rig.transformy(klip, f)
            zs.append(rig.pozy(t)[i][1][2])
            dno = min(dno, najnizej(rig, d, t, kosci_nog))
        zakresy.append(max(zs) - min(zs))
    krok = sum(zakresy) / len(zakresy)
    if krok <= 0.05 or okres <= 0:
        raise BladDanych("klip chodu %s: stopy się nie ruszają (zakres %.3f)" % (klip, krok))
    return 2.0 * krok / okres, max(0.0, -dno)


def _poza(nazwa, opis, rig, d, kosci_nog):
    """Poza z ustawień → wiersze [kość, x, y, z, rx, ry, rz] (radiany) i opuszczenie bioder (0 bez „przysiad”)."""
    wiersze = []
    for kosc, katy in opis["kosci"].items():
        if kosc not in rig.indeks:
            raise BladDanych("poza %s: w rigu %s nie ma kości %s" % (nazwa, d["klucz"], kosc))
        if kosc == "LowerTorso" and opis.get("przysiad"):
            raise BladDanych("poza %s: przy „przysiad” biodra (LowerTorso) ustawia generator" % nazwa)
        wiersze.append([kosc, 0.0, 0.0, 0.0] + [_r(math.radians(k), 5) for k in katy])
    przysiad = 0.0
    if opis.get("przysiad"):
        przysiad = najnizej(rig, d, transformy_pozy(rig, wiersze), kosci_nog)
        wiersze.insert(0, ["LowerTorso", 0.0, _r(-przysiad), 0.0, 0.0, 0.0, 0.0])
    return wiersze, _r(przysiad)


def _pion(rig, klip, dodatki, kosc):
    """Dodatek dla kości trzymanej w pionie (kostur): znosi obroty ramienia i tułowia z `dodatki`, tak żeby kość miała
    w biegu ten sam kierunek co w klipie spoczynku. Dwa wpisy: stała i wymach raz na cykl, z kinematyki w przód."""
    import logika_bohatera as LB
    from geometria import cf, odwrotnosc, orientacja, razy
    i = rig.indeks[kosc]
    rodzic = rig.kosci[i - 1][1]
    t0 = dict(rig.transformy(klip, 0))
    obrot = lambda c: cf((0.0, 0.0, 0.0), c[0])                 # sama orientacja
    spocz = obrot(rig.pozy(t0)[rodzic])
    wlasny = obrot(t0[i]) if i in t0 else cf()
    def potrzebny(faza):
        t = dict(t0)
        for w in dodatki:
            j = rig.indeks[w[0]]
            t[j] = razy(t.get(j, cf()), cf((0.0, 0.0, 0.0), orientacja(*LB.dodatek(w, faza, 1.0))))
        bieg = obrot(rig.pozy(t)[rodzic])
        return razy(razy(odwrotnosc(wlasny), razy(odwrotnosc(bieg), spocz)), wlasny)

    def katy(M):
        M = M[0]
        return [_r(math.asin(max(-1.0, min(1.0, -M[1][2]))), 5), _r(math.atan2(M[0][2], M[2][2]), 5), _r(math.atan2(M[1][0], M[1][1]), 5)]

    # stała część dokładnie (faza 0,25: wymachy raz na cykl są w zerze), wymach jako drugi, mały obrót po niej
    staly = potrzebny(0.25)
    wymach = razy(odwrotnosc(staly), potrzebny(0.0))
    return [[kosc] + katy(staly) + [0.0, 0.0, 0.0, 1, 0], [kosc, 0.0, 0.0, 0.0] + katy(wymach) + [1, 0]]


def _bieg(U, d, rig, klucz, predkosc_chodu, klip_spoczynku):
    """Liczby cyklu biegu jednej klasy z jej nóg (stawy biodra, kolana i kostki z rigu) i ustawień."""
    B = U["bieg"]
    kosci = {k[0]: k for k in d["kosci"]}
    wymiary = []
    for strona in ("Left", "Right"):
        biodro, kolano, kostka = (kosci[strona + n][2:5] for n in ("UpperLeg", "LowerLeg", "Foot"))
        if max(abs(biodro[2] - kolano[2]), abs(kolano[2] - kostka[2]), abs(biodro[0] - kolano[0]), abs(kolano[0] - kostka[0])) > 1e-6:
            raise BladDanych("klasa %s: noga %s nie jest w spoczynku pionowa (cykl biegu tego zakłada)" % (klucz, strona))
        for n, rodzic in (("UpperLeg", "LowerTorso"), ("LowerLeg", strona + "UpperLeg"), ("Foot", strona + "LowerLeg")):
            if kosci[strona + n][1] != rig.indeks[rodzic]:
                raise BladDanych("klasa %s: łańcuch nogi %s ma innych rodziców niż biodra → udo → łydka → stopa" % (klucz, strona))
        wymiary.append((biodro[1] - kolano[1], kolano[1] - kostka[1], kostka[1], biodro[1]))
    if max(abs(a - b) for a, b in zip(*wymiary)) > 1e-6:
        raise BladDanych("klasa %s: nogi nie są jednakowe" % klucz)
    udo, lydka, kostka, biodro = wymiary[0]
    noga = udo + lydka
    spod = najnizej(rig, d, {}, STOPY)
    if abs(spod) > 0.01:
        raise BladDanych("klasa %s: stopy w spoczynku nie stoją na ziemi (%.3f)" % (klucz, spod))
    B = bieg_klasy(U, klucz)
    v_do = U["ruch"]["tempo_max"] * predkosc_chodu
    v_pelna = float(U["ruch"]["bieg_predkosc"])
    krok = B["krok_na_noge"] * noga
    # biodra w skrajach podporu: najwyżej, jak pozwala zasięg nogi przy tym kroku (krótszy krok = prostsze kolano)
    biodra = math.sqrt((B["zasieg_nogi"] * noga) ** 2 - (krok / 2) ** 2)
    ugiecie = B["ugiecie_na_noge"] * noga
    lot = 1.0 / (2 * B["kadencja_pelna"]) - krok / v_pelna
    if lot <= 0.01:
        raise BladDanych("klasa %s: przy kadencja_pelna %.2f i kroku %.2f st nie ma lotu" % (klucz, B["kadencja_pelna"], krok))
    P, S = B["poly"], B["skret_ciala"]
    dodatki = []
    for kosc, wpisy in B["dodatki"].items():
        if kosc not in rig.indeks:
            raise BladDanych("klasa %s: bieg.dodatki — w rigu nie ma kości %s" % (klucz, kosc))
        for w in wpisy:
            if any(w[:6]):
                dodatki.append([kosc] + [_r(math.radians(x), 5) for x in w[:6]] + [w[6], w[7]])
    for kosc in B.get("pion", []):
        if kosc not in rig.indeks or kosc in B["dodatki"]:
            raise BladDanych("klasa %s: bieg.pion — kość %s musi być w rigu i nie może mieć własnych dodatków" % (klucz, kosc))
        dodatki.extend(_pion(rig, klip_spoczynku, list(dodatki), kosc))
    wynik = collections.OrderedDict([
        ("udo", _r(udo)), ("lydka", _r(lydka)), ("kostka", _r(kostka)), ("biodro", _r(biodro)), ("noga", _r(noga)),
        ("krok", _r(krok)), ("biodraPodpor", _r(biodra)), ("ugiecie", _r(ugiecie)),
        ("wzlotMaks", _r(B["wzlot_maks_na_ugiecie"] * ugiecie)), ("wzlotRazy", B["wzlot_razy"]), ("unoszenie", _r(B["unoszenie_na_noge"] * noga)),
        ("skosUnoszenia", B["skos_unoszenia"]), ("wybieg", _r(B["wybieg_na_krok"] * krok)),
        ("lot", _r(lot, 5)), ("lotMin", B["lot_min"]), ("vPelna", v_pelna), ("vMin", B["predkosc_min"]),
        ("podporMin", B["podpor_min"]), ("skalaMin", B["skala_min"]), ("skalaMaks", B["skala_maks"]),
        ("vOd", _r(v_do * (1 + B["pasmo"]), 3)), ("vDo", _r(v_do, 3)), ("czas", B["czas_przejscia_s"]),
        ("stopaWymach", _r(math.radians(B["stopa_w_wymachu_st"]), 5)), ("skosStopy", B["skos_stopy"]),
        ("wygladzanie", B["wygladzanie_predkosci_s"]), ("vMaks", B["predkosc_maks"]),
        ("poly", bool(P["wlaczone"])), ("polaProg", P["prog_st"]), ("polaSrodek", P["srodek_st"]), ("polaUdo", P["udo"]),
        ("dzwonUnies", _r(math.radians(P["dzwon_unies_st"]), 5)), ("dzwonFala", _r(math.radians(P["dzwon_fala_st"]), 5)),
        ("dzwonSkret", _r(math.radians(P["dzwon_skret_st"]), 5)), ("dzwonZwloka", P["dzwon_zwloka"]),
        ("skretCiala", collections.OrderedDict([
            ("przechyl", _r(math.radians(S["przechyl_st"]), 5)), ("obrot", _r(math.radians(S["obrot_st"]), 5)),
            ("pelny", S["pelny_rad_s"]), ("wygladzanie", S["wygladzanie_s"])])),
        ("dodatki", dodatki)])
    # pochylenie stopy w wymachu (czubek w dół): u bohatera z długą stopą na krótkiej nodze czubek wszedłby w ziemię —
    # kąt maleje co 2°, aż w całym wymachu (przy każdej skali ruchu) najniższa bryła stopy jest nad ziemią
    import logika_bohatera as LB
    kat = float(B["stopa_w_wymachu_st"])
    while True:
        wynik["stopaWymach"] = _r(math.radians(kat), 5)
        zapas = 1e9
        for v in (v_do, v_pelna, 1.5 * v_pelna):
            podpor = LB.kadencja(wynik, v)[1]
            for s in (B["skala_min"], 1.0, B["skala_maks"]):
                for n in range(0, 60):
                    faza = n / 60.0
                    if faza >= podpor:
                        dno = najnizej(rig, d, transformy_biegu(rig, LB.bieg(wynik, faza, podpor, s)), ["LeftFoot"])
                        zapas = min(zapas, dno - 0.2 * (LB.tor_kostki(wynik, faza, podpor, s)[1] - kostka))
        if zapas >= -0.005 or kat >= 0:
            break
        kat = min(0.0, kat + 2.0)
    return wynik


def transformy_biegu(rig, c):
    """Wynik logika_bohatera.bieg() → {indeks kości: CFrame} dla kości, które cykl biegu ustawia bezwzględnie
    (biodra i nogi — jak w kliencie; ręce i tułów dostają tylko dodatek do klipu, więc tu ich nie ma)."""
    from geometria import cf, orientacja
    t = {rig.indeks["LowerTorso"]: cf((0.0, c["biodraY"], 0.0))}
    for strona, s in (("Left", "L"), ("Right", "P")):
        t[rig.indeks[strona + "UpperLeg"]] = cf((0.0, 0.0, 0.0), orientacja(c["udo" + s], 0.0, 0.0))
        t[rig.indeks[strona + "LowerLeg"]] = cf((0.0, 0.0, 0.0), orientacja(c["lydka" + s], 0.0, 0.0))
        t[rig.indeks[strona + "Foot"]] = cf((0.0, 0.0, 0.0), orientacja(c["stopa" + s], 0.0, 0.0))
    return t


def poly_rigu(rig, d, B):
    """Poły stroju odniesienia — to samo, co klient zbiera przy budowie (zbierzPoly): bryły wiszące na kości bioder
    z rodzajem, wagą i zawiasem w układzie modelu."""
    import logika_bohatera as LB
    from geometria import narozniki
    if not B["poly"]:
        return []
    spocz = rig.pozy()
    kandydaci = []
    for c in d["czesci"]:
        if c[0] == rig.indeks["LowerTorso"]:
            pts = narozniki(rig.czesc_cf(c, spocz), c[9:12])
            ys, zs = [p[1] for p in pts], [p[2] for p in pts]
            r = LB.rodzaj_poly(B, min(ys), min(zs), max(zs))
            if r is not None:
                kandydaci.append((c, r, min(ys), max(ys), min(zs), max(zs)))
    if not kandydaci:
        return []
    dzwon = any(k[1] == "dzwon" for k in kandydaci)
    dno, tyl = min(k[2] for k in kandydaci), max(k[5] for k in kandydaci)
    wynik = []
    for c, r, dol, gora, zp, zt in kandydaci:
        if dzwon:
            wynik.append({"c": c, "dzwon": True, "waga": LB.waga_dzwonu(B, (dol + gora) / 2, dno), "zawias": (0.0, dno, tyl)})
        else:
            grupa = [k for k in kandydaci if k[1] == r]
            wynik.append({"c": c, "dzwon": False, "przod": r == "przod",
                          "zawias": (0.0, max(k[3] for k in grupa), sum((k[4] + k[5]) / 2 for k in grupa) / len(grupa))})
    return wynik


def cf_poly(rig, p, pozy, spocz, c_bieg, B, faza, s):
    """CFrame bryły poły w cyklu biegu (klient robi to samo spawem bryły): obrót wokół zawiasu w układzie modelu
    w spoczynku, niesiony kością bioder."""
    import logika_bohatera as LB
    from geometria import cf, odwrotnosc, orientacja, przesun, razy
    H = p["zawias"]
    wstecz = przesun((-H[0], -H[1], -H[2]))
    if p["dzwon"]:
        unies, skret = LB.dzwon(B, faza, s, p["waga"])
        M = razy(razy(razy(przesun(H), cf((0, 0, 0), orientacja(unies, 0.0, 0.0))), wstecz), cf((0, 0, 0), orientacja(0.0, skret, 0.0)))
        M = razy(przesun((0.0, max(0.0, -c_bieg["biodraY"]) * p["waga"], 0.0)), M)
    else:
        kat = c_bieg["polaPrzod"] if p["przod"] else c_bieg["polaTyl"]
        M = razy(razy(przesun(H), cf((0, 0, 0), orientacja(kat, 0.0, 0.0))), wstecz)
    i = p["c"][0]
    return razy(razy(razy(pozy[i], odwrotnosc(spocz[i])), M), rig.czesc_cf(p["c"], spocz))


def poza_biegu(rig, d, K, faza, v):
    """Pełna poza bohatera w cyklu biegu jak w kliencie: klip spoczynku (klatka 0), biodra i nogi z cyklu, dodatki
    (ręce, tułów, głowa, ogon…), poły. → (wynik L.bieg, pozy kości, lista CFrame brył w kolejności d["czesci"])."""
    import logika_bohatera as LB
    from geometria import cf, orientacja, razy
    B = K["bieg"]
    pod = LB.kadencja(B, v)[1]
    s = LB.skala_biegu(B, v)
    c = LB.bieg(B, faza, pod, s)
    t = dict(rig.transformy(K["klipy"]["spoczynek"], 0))
    t.update(transformy_biegu(rig, c))
    for w in B["dodatki"]:
        i = rig.indeks[w[0]]
        t[i] = razy(t.get(i, cf()), cf((0.0, 0.0, 0.0), orientacja(*LB.dodatek(w, faza, s))))
    pozy, spocz = rig.pozy(t), rig.pozy()
    pola = {id(p["c"]): cf_poly(rig, p, pozy, spocz, c, B, faza, s) for p in poly_rigu(rig, d, B)}
    return c, pozy, [pola.get(id(cz)) or rig.czesc_cf(cz, pozy) for cz in d["czesci"]]


def _bryly_stroju(DS, Ds, klucz, ids, kosci_nog):
    """(liczba brył, najniższy punkt nóg w spoczynku) bohatera w stroju `ids` — dane przymierzalni (tylko odczyt)."""
    import logika_strojow as LS
    from geometria import cf, narozniki, orientacja
    ok, plan = LS.plan(Ds, klucz, list(ids))
    if not ok:
        raise BladDanych("klasa %s: strój %s odrzucony przez logikę przymierzalni (%s)" % (klucz, ids, plan))
    wiersze = DS.zloz(Ds, klucz, plan)
    nogi = {i + 1 for i, k in enumerate(Ds["klasy"][klucz]["kosci"]) if k[0] in kosci_nog}
    spod = min(p[1] for w in wiersze if w[0] in nogi
               for p in narozniki(cf((w[3], w[4], w[5]), orientacja(w[6], w[7], w[8])), w[9:12]))
    return len(wiersze), _r(spod)


# --------------------------------------------------------------------------------------------- całość
def zbierz():
    """Słownik danych pakietu (to, co trafia do DaneBohatera.luau)."""
    import aktorzy as A
    from geometria import Rig
    U = ustawienia()
    DS = dane_strojow()
    try:
        Ds, _ = DS.zbierz()
    except DS.BladDanych as e:
        raise BladDanych("dane przymierzalni (swiat/stroje_proba): %s" % e)
    odwrotnie = {v: k for k, v in U["klasy_gracza"].items()}
    if len(odwrotnie) != len(U["klasy_gracza"]):
        raise BladDanych("ustawienia.klasy_gracza: dwie klasy gry na jednego bohatera")
    kosci_nog = list(U["kosci_nog"])
    klasy = collections.OrderedDict()
    for klucz in U["klasy_gracza"].values():
        wpis = A.PO_KLUCZU.get(klucz)
        if wpis is None or wpis["rola"] != "klasa":
            raise BladDanych("klasa %s: nie ma takiego bohatera w swiat/test_walki2/aktorzy.py" % klucz)
        if klucz not in Ds["klasy"]:
            raise BladDanych("klasa %s: nie ma jej w danych przymierzalni" % klucz)
        try:
            d = A.wczytaj(klucz)
        except FileNotFoundError as e:
            raise BladDanych(str(e))
        rig = Rig(d)
        if [k[0] for k in d["kosci"]] != [k[0] for k in Ds["klasy"][klucz]["kosci"]]:
            raise BladDanych("klasa %s: kości danych walki ≠ kości przymierzalni" % klucz)
        for n in kosci_nog + list(STOPY):
            if n not in rig.indeks:
                raise BladDanych("klasa %s: rig nie ma kości %s" % (klucz, n))
        klipy, dlugosci = collections.OrderedDict(), collections.OrderedDict()
        for akcja in AKCJE:
            nazwa = wpis["klipy"].get(U["akcje"][akcja])
            if not nazwa or nazwa not in rig.klipy:
                raise BladDanych("klasa %s: akcja %s nie ma klipu w danych walki" % (klucz, akcja))
            klipy[akcja] = nazwa
            dlugosci[akcja] = _r(rig.klipy[nazwa]["dl"] / float(rig.klipy[nazwa]["fps"]), 3)
        predkosc, podniesienie = _chod(rig, d, klipy["ruch"], kosci_nog)
        pozy, przysiady = collections.OrderedDict(), collections.OrderedDict()
        for nazwa, opis in U["pozy"].items():
            pozy[nazwa], przysiady[nazwa] = _poza(nazwa, opis, rig, d, kosci_nog)
        odniesienie = Ds["klasy"][klucz]["odniesienie"]
        n_gol, spod_gol = _bryly_stroju(DS, Ds, klucz, [], kosci_nog)
        n_odn, spod_odn = _bryly_stroju(DS, Ds, klucz, odniesienie, kosci_nog)
        if n_odn != len(d["czesci"]):
            raise BladDanych("klasa %s: strój odniesienia ma %d brył, szablon walki %d" % (klucz, n_odn, len(d["czesci"])))
        klasy[klucz] = collections.OrderedDict([
            ("klucz", klucz), ("nazwa", wpis["nazwa"]), ("klasaGry", odwrotnie[klucz]),
            ("klipy", klipy), ("dlugosci", dlugosci),
            ("predkoscChodu", _r(predkosc, 3)), ("podniesienieChodu", _r(podniesienie, 3)),
            ("wysokosc", _r(d["wymiary"]["wysokosc"], 3)), ("hrp", [_r(v) for v in d["hrp"]]),
            ("czesci", collections.OrderedDict([("golas", n_gol), ("odniesienie", n_odn)])),
            ("spod", collections.OrderedDict([("golas", spod_gol), ("odniesienie", spod_odn)])),
            ("bieg", _bieg(U, d, rig, klucz, predkosc, klipy["spoczynek"])),
            ("przysiady", przysiady), ("pozy", pozy)])
    D = collections.OrderedDict()
    D["wersja"] = 1
    for k in ("kontener", "prefiks", "atrybut_wlacznika", "atrybut_klasy"):
        D[k] = U[k]
    D["atrybut_stroju"] = Ds["atrybut"]
    for k in ("klasy_gracza", "kontener_walki", "kontener_strojow", "folder_lokalny", "ruch", "widocznosc", "awatar",
              "kontrakt", "pomiar", "limity"):
        D[k] = U[k]
    D["kosciNog"] = kosci_nog
    D["kolejnoscPoz"] = list(U["pozy"])
    D["czasyPoz"] = collections.OrderedDict((n, o["czas_s"]) for n, o in U["pozy"].items())
    D["kolejnoscKlas"] = list(klasy)
    D["klasy"] = klasy
    tekst = json.dumps(D, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    D["skrot"] = hashlib.sha1(tekst.encode("utf-8")).hexdigest()[:12]
    return D


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


def luau_tekst(D):
    glowa = ("--[[\n\tDaneBohatera — WYGENEROWANE przez swiat/bohater_swiat/dane.py (nie edytuj ręcznie), skrót %s.\n"
             "\tŹródła: ustawienia.json, swiat/test_walki2 (aktorzy.py, dane/<klasa>.json — tylko odczyt),\n"
             "\tswiat/stroje_proba/dane.py (atrybut stroju, liczby brył).\n"
             "\tPoza = lista { kość, x, y, z, rx, ry, rz } — Motor6D.Transform stawu tej kości:\n"
             "\t       CFrame.new(x, y, z) * CFrame.fromOrientation(rx, ry, rz) (radiany).\n"
             "]]\n" % D["skrot"])
    linie = [glowa + STRAZNIK, "local D = {}"]
    for k, v in D.items():
        if k != "klasy":
            linie.append("D.%s = %s" % (k, _luau(v, 1)))
    linie.append("D.klasy = {}")
    for klucz, K in D["klasy"].items():
        meta = collections.OrderedDict((k, v) for k, v in K.items() if k != "pozy")
        linie.append("D.klasy[%s] = %s" % (_napis(klucz), _luau(meta, 1)))
        linie.append("D.klasy[%s].pozy = {}" % _napis(klucz))
        for nazwa, wiersze in K["pozy"].items():
            w = "".join("\t{ " + ", ".join(_luau(x) for x in wiersz) + " },\n" for wiersz in wiersze)
            linie.append("D.klasy[%s].pozy[%s] = {\n%s}" % (_napis(klucz), _napis(nazwa), w))
    linie.append("return D\n")
    return "\n".join(linie)


def zapisz(folder):
    D = zbierz()
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, PLIK_LUAU), "w", encoding="utf-8", newline="\n") as f:
        f.write(luau_tekst(D))
    return D


def aktualny():
    D = zbierz()
    sciezka = os.path.join(ZRODLA, PLIK_LUAU)
    if not os.path.isfile(sciezka):
        return False, D
    with open(sciezka, encoding="utf-8") as f:
        return f.read() == luau_tekst(D), D


def podsumowanie(D):
    linie = []
    for klucz, K in D["klasy"].items():
        linie.append("  %-10s (%s) klipy %s · chód %.2f st/s (tempo przy %g st/s: %.2f), podniesienie %.3f · wzrost %.2f"
                     % (klucz, K["klasaGry"], "/".join(K["klipy"].values()), K["predkoscChodu"],
                        D["ruch"]["bieg_predkosc"],
                        min(D["ruch"]["tempo_max"], max(D["ruch"]["tempo_min"], D["ruch"]["bieg_predkosc"] / K["predkoscChodu"])),
                        K["podniesienieChodu"], K["wysokosc"]))
        Bg = K["bieg"]
        import logika_bohatera as LB
        v = D["ruch"]["bieg_predkosc"]
        f, pod = LB.kadencja(Bg, v)
        linie.append("  %-10s bieg od %.1f st/s (chód wraca poniżej %.1f): noga %.2f st, krok %.2f st; przy %g st/s kadencja %.2f "
                     "cyklu/s, podpór %.0f%% cyklu, lot %.3f s na krok" % ("", Bg["vOd"], Bg["vDo"], Bg["noga"], Bg["krok"], v, f,
                                                                         100 * pod, Bg["lot"]))
        linie.append("  %-10s bryły: goły %d, strój odniesienia %d (limit %d) · spód nóg: goły %.3f, w stroju %.3f · "
                     "przysiad: %s" % ("", K["czesci"]["golas"], K["czesci"]["odniesienie"],
                                       D["limity"]["maks_czesci_bohatera"], K["spod"]["golas"], K["spod"]["odniesienie"],
                                       ", ".join("%s %.2f" % (n, v) for n, v in K["przysiady"].items() if v)))
    return linie


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    try:
        if "--sprawdz" in argv:
            ok, D = aktualny()
            print("%s: %s (skrót %s, %d znaków)" % (PLIK_LUAU, "aktualny" if ok else "NIEAKTUALNY", D["skrot"],
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
        return 0
    except BladDanych as e:
        print("BŁĄD DANYCH: %s" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
