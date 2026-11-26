#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator danych sklepu zbrojmistrza na próbę (swiat/sklep_proba) — z ustawienia.json, stopni katalogu sklepu
(swiat/postacie/sklep_przedmioty.json: nazwy stopni) i znacznika zbrojowni w bazarze (swiat/miasteczko_bazar/
znaczniki.json, swiat/miasteczko_bazar_gra/miejsca.json — tylko odczyt).

    python -B swiat/sklep_proba/dane.py            # zapisuje zrodla/DaneSklepu.luau
    python -B swiat/sklep_proba/dane.py --sprawdz  # tylko sprawdza, czy plik jest aktualny (kod 1, gdy nie)

Cen, poziomów ani statystyk przedmiotów tu NIE ma: ma je kowal (swiat/kowal_proba/dane.py bierze je z katalogu),
a sklep dostaje gotową ofertę z jego wejścia Sygnaly/Sklep. Co sprawdza (błąd = BladDanych): miejsce bazaru istnieje
i otwiera okno, znacznik ma położenie stoiska, każdy stopień katalogu ma kolor, teksty stanów są kompletne.
"""
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if TU not in sys.path:
    sys.path.insert(0, TU)
import logika_sklepu as LS  # noqa: E402

ZRODLA = os.path.join(TU, "zrodla")
PLIK_DANYCH = "DaneSklepu.luau"
KATALOG_SKLEPU = os.path.join(REPO, "swiat", "postacie", "sklep_przedmioty.json")
ZNACZNIKI = os.path.join(REPO, "swiat", "miasteczko_bazar", "znaczniki.json")
MIEJSCA = os.path.join(REPO, "swiat", "miasteczko_bazar_gra", "miejsca.json")


class BladDanych(Exception):
    pass


def _json(sciezka):
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def ustawienia():
    return _json(os.path.join(TU, "ustawienia.json"))


def miejsce(U):
    M = U["miejsce"]
    m = next((x for x in _json(MIEJSCA)["miejsca"] if x.get("id") == M["id"]), None)
    if m is None or m.get("akcja") != "okno" or m.get("znacznik") != M["znacznik"]:
        raise BladDanych("miejsce bazaru %s: brak, nie otwiera okna albo inny znacznik" % M["id"])
    if _json(MIEJSCA).get("zdarzenie_okien") != M["zdarzenie_okien"]:
        raise BladDanych("zdarzenie okien bazaru ≠ %s" % M["zdarzenie_okien"])
    a, b = M["znacznik"].split("/")
    grupa = _json(ZNACZNIKI)[a]
    z = next((x for x in grupa if x.get("id") == b), None) if isinstance(grupa, list) else grupa.get(b)
    if z is None or not isinstance(z.get("swiat"), list):
        raise BladDanych("znacznik %s bez położenia" % M["znacznik"])
    if not (0 < M["zasieg"] <= M["zasieg_okna"]) or M["zapas_serwera"] < 0:
        raise BladDanych("miejsce: zasięgi")
    return {"id": M["id"], "zdarzenie": M["zdarzenie_okien"], "punkt": [round(float(v), 3) for v in z["swiat"]],
            "zasieg": M["zasieg"], "zapasSerwera": M["zapas_serwera"], "zasiegOkna": M["zasieg_okna"],
            "postac": m.get("postac") or ""}


def stopnie(U):
    kolory = U["kolory_stopni"]
    w = []
    for s in _json(KATALOG_SKLEPU)["stopnie"]:
        if s["id"] not in kolory:
            raise BladDanych("stopień %s bez koloru w ustawienia.kolory_stopni" % s["id"])
        w.append({"id": s["id"], "nr": s["nr"], "nazwa": s["nazwa"], "kolor": kolory[s["id"]]})
    if [s["nr"] for s in w] != list(range(len(w))):
        raise BladDanych("stopnie katalogu nie idą po kolei")
    return w


def podstawa():
    U = ustawienia()
    for stan in LS.STANY:
        if "stan_" + stan not in U["teksty"]:
            raise BladDanych("brak tekstu stanu %s" % stan)
    for k in set(LS._MAPA.values()) | {"blad", "za_malo_zlota", "za_niski_poziom", "formy_rybki", "formy_rybki_dopelniacz"}:
        if k not in U["teksty"]:
            raise BladDanych("brak tekstu %s" % k)
    return {
        "wersja": 1, "status": U["status"], "kontener": U["kontener"], "prefiks": U["prefiks"],
        "kowal": {"kontener": U["kowal"]["kontener"], "sygnal": U["kowal"]["sygnal"], "coIleS": U["kowal"]["co_ile_s"]},
        "miejsce": miejsce(U), "limit": U["limit_zapytan_s"], "stopnie": stopnie(U), "ui": U["ui"],
        "teksty": U["teksty"],
    }


# ------------------------------------------------------------------------------------------------ przypadki wzorcowe
def _oferta_probna(D, zmiana=0):
    """Mała oferta ze wszystkimi stanami (układ wiersza jak z wejścia kowala)."""
    stany = list(LS.STANY)
    w = []
    for i, s in enumerate(D["stopnie"]):
        for j, slot in enumerate(("Weapon", "Chest", "Helmet")):
            stan = stany[(i * 3 + j + zmiana) % len(stany)]
            w.append({"id": "probny_%s_%d" % (s["id"], j), "nazwa": "Przedmiot %d" % (i * 3 + j), "slot": slot,
                      "slotNazwa": ("Broń", "Zbroja", "Hełm")[j], "stopien": s["id"], "nrStopnia": s["nr"],
                      "cena": 0 if (i == 0 and j < 2) else 100 * (i + 1) + 50 * j, "poziom": 1 + i * 6 + j,
                      "stan": stan, "brakuje": (i + 1) * 25 if stan in ("za_drogie", "za_niski_poziom") else 0,
                      "ulepszenie": (i + j) % 3 if stan in ("masz", "zalozone") else 0,
                      "staty": "" if j == 1 and i == 0 else "Broń +%d · Siła +%d" % (i + 1, j + 1)})
    return w


def przypadki(D):
    P = {"uklad": [], "oferta": [], "komunikat": [], "naglowek": [], "odmiana": []}
    for W, H in ((667, 375), (812, 375), (1024, 768), (1366, 768), (1920, 1080), (2560, 1440), (320, 240)):
        P["uklad"].append({"W": W, "H": H, "wynik": LS.uklad(D, W, H)})
    for zmiana in (0, 2, 3):
        of = _oferta_probna(D, zmiana)
        P["oferta"].append({"oferta": of, "grupy": LS.grupy(D, of), "zakladka": LS.pierwsza_zakladka(D, of),
                            "wiersze": [LS.wiersz(D, o) for o in of]})
    P["oferta"].append({"oferta": [], "grupy": LS.grupy(D, []), "zakladka": LS.pierwsza_zakladka(D, []), "wiersze": []})
    odp = [("kup", {"ok": True, "nazwa": "Dębowa Tarcza", "zalozony": True}),
           ("kup", {"ok": True, "nazwa": "Dębowa Tarcza", "zalozony": False}),
           ("zaloz", {"ok": True, "nazwa": "Dębowa Tarcza", "zalozony": True}),
           ("oferta", {"ok": True}),
           ("kup", {"ok": False, "powod": "za_malo_zlota", "brakuje": 150}),
           ("kup", {"ok": False, "powod": "za_malo_zlota", "brakuje": 1}),
           ("kup", {"ok": False, "powod": "za_malo_zlota", "brakuje": 22}),
           ("kup", {"ok": False, "powod": "za_niski_poziom", "brakuje": 4, "wymagany": 13}),
           ("kup", {"ok": False, "powod": "za_niski_poziom", "brakuje": 4}),
           ("kup", "zle")]
    for powod in sorted(LS._MAPA) + ["blad", "cos_nowego"]:
        odp.append(("kup", {"ok": False, "powod": powod}))
    for akcja, r in odp:
        P["komunikat"].append({"akcja": akcja, "r": r, "wynik": LS.komunikat(D, akcja, r)})
    for zloto, poziom in ((0, 1), (1234, 17)):
        P["naglowek"].append({"zloto": zloto, "poziom": poziom, "wynik": LS.naglowek(D, zloto, poziom)})
    for n in (0, 1, 2, 4, 5, 11, 12, 14, 21, 22, 25, 100, 101, 102, 112):
        P["odmiana"].append({"n": n, "rybki": LS.ile_rybek(D, n), "rybkiDop": LS.ile_rybek_dop(D, n)})
    return P


def dane_z_przypadkami():
    D = podstawa()
    D["przypadki"] = przypadki(D)
    D["skrot"] = hashlib.sha1(json.dumps(D, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]
    return D


# ------------------------------------------------------------------------------------------------ zapis Luau
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SLOWA = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in", "local", "nil", "not",
          "or", "repeat", "return", "then", "true", "until", "while", "continue", "export", "type"}


def _napis(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def _liczba(x):
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, int):
        return str(x)
    r = repr(float(x))
    return r[:-2] if r.endswith(".0") else r


def _klucz(k):
    return k if (_IDENT.match(k) and k not in _SLOWA) else "[%s]" % _napis(k)


def _luau(v, wciecie=1):
    if isinstance(v, (bool, int, float)):
        return _liczba(v)
    if isinstance(v, str):
        return _napis(v)
    tab = "\t" * wciecie
    if isinstance(v, (list, tuple)):
        czesci = [_luau(x, wciecie + 1) for x in v]
    elif isinstance(v, dict):
        czesci = ["%s = %s" % (_klucz(k), _luau(x, wciecie + 1)) for k, x in v.items() if x is not None]
    else:
        raise TypeError(repr(v))
    jedna = "{ " + ", ".join(czesci) + " }" if czesci else "{}"
    if len(jedna) <= 110 and "\n" not in jedna:
        return jedna
    return "{\n" + "".join(tab + c + ",\n" for c in czesci) + "\t" * (wciecie - 1) + "}"


STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then\n\treturn {}\nend\n\nreturn '


def luau_danych(D):
    naglowek = ("--[[\n\tDaneSklepu — WYGENEROWANE przez swiat/sklep_proba/dane.py z ustawienia.json, stopni katalogu sklepu\n"
                "\ti znacznika zbrojowni w bazarze. NIE EDYTUJ RĘCZNIE: zmień źródło i uruchom\n"
                "\tpython -B swiat/sklep_proba/dane.py (testy i zbuduj.py --sucho pilnują aktualności). Status: propozycja.\n]]\n")
    return naglowek + STRAZNIK + _luau(D) + "\n"


def aktualny():
    D = dane_z_przypadkami()
    tekst = luau_danych(D)
    sciezka = os.path.join(ZRODLA, PLIK_DANYCH)
    zle = []
    if not os.path.isfile(sciezka):
        zle.append("zrodla/" + PLIK_DANYCH)
    else:
        with open(sciezka, encoding="utf-8") as f:
            if f.read() != tekst:
                zle.append("zrodla/" + PLIK_DANYCH)
    return zle, D, tekst


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    try:
        zle, D, tekst = aktualny()
    except BladDanych as e:
        print("BŁĄD DANYCH:", e)
        return 2
    if "--sprawdz" in argv:
        print("dane sklepu: %s (skrót %s)" % ("aktualne" if not zle else "NIEAKTUALNE: " + ", ".join(zle), D["skrot"]))
        return 1 if zle else 0
    os.makedirs(ZRODLA, exist_ok=True)
    with open(os.path.join(ZRODLA, PLIK_DANYCH), "w", encoding="utf-8", newline="\n") as f:
        f.write(tekst)
    m = D["miejsce"]
    print("zapisano: swiat/sklep_proba/zrodla/%s (skrót %s)" % (PLIK_DANYCH, D["skrot"]))
    print("  miejsce %s: stoisko %s, zasięg %s (serwer +%s), okno do %s; stopnie: %s; przypadków wzorcowych: %d"
          % (m["id"], m["punkt"], m["zasieg"], m["zapasSerwera"], m["zasiegOkna"],
             ", ".join(s["nazwa"] for s in D["stopnie"]), sum(len(v) for v in D["przypadki"].values())))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
