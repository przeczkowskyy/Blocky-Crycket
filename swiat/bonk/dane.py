#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dane gry BONK (D-112, propozycja) → zrodla/DaneBonk.luau (wygenerowany) i dane wzorców potworów do budowy.

    python -B swiat/bonk/dane.py              # zapisuje DaneBonk.luau, gdy się zmienił, i wypisuje tabelę
    python -B swiat/bonk/dane.py --sprawdz    # kod 1, gdy plik jest nieaktualny (nic nie zapisuje)

Źródła (tylko odczyt): ustawienia.json; mapy pasów <kraina.mapa>/znaczniki.json (strefy potworów: środek, promień,
węzły; Strażnik i arena — na etap 2), <kraina.mapa>/czesci.json (mapa — buduje ją zbuduj.py); modele potworów
swiat/test_walki2/dane/<gatunek>.json (kości, bryły w pozie spoczynku, wymiary); dźwięki: swiat/dzwiek_gra/
identyfikatory.json i assets/audio/arkusz/sfx_arkusz_a.json. Układ świata map pasów: (1100 + u; y; −700 + v),
w BONK dodatkowo przesunięty o `przesuniecie` z ustawień. Żadnych liczb położeń w kodzie Luau.
"""
import argparse
import hashlib
import json
import math
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
ZRODLA = os.path.join(TU, "zrodla")
PLIK_DANYCH = "DaneBonk.luau"
X0, Z0 = 1100.0, -700.0            # układ map pasów (znaczniki.json → kontener.wzor)
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
SLOWA_LUAU = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in", "local", "nil",
              "not", "or", "repeat", "return", "then", "true", "until", "while", "continue"}


class BladDanych(Exception):
    pass


def czytaj_json(sciezka):
    with open(sciezka, encoding="utf-8-sig") as f:
        return json.load(f)


def sciezka_repo(wzgledna):
    return os.path.join(REPO, *wzgledna.split("/"))


def ustawienia():
    return czytaj_json(os.path.join(TU, "ustawienia.json"))


def _r(v, n=2):
    x = round(float(v), n)
    return 0 if x == 0 else x


def swiat(U, u, y, v):
    """Punkt pasa (u, y, v) → świat BONK [X, Y, Z]."""
    p = U["przesuniecie"]
    return [_r(X0 + u + p[0]), _r(y + p[1]), _r(Z0 + v + p[2])]


def model_potwora(klucz):
    s = sciezka_repo("swiat/test_walki2/dane/%s.json" % klucz)
    if not os.path.isfile(s):
        raise BladDanych("brak modelu potwora %s (swiat/test_walki2/dane/%s.json)" % (klucz, klucz))
    return czytaj_json(s)


def wzorzec(klucz):
    """Wzorzec potwora do budowy w Studio: bryły w pozie spoczynku (układ rigu: stopy na y = 0, przód = −Z).
    Bryła: [kształt, x, y, z, rx, ry, rz, sx, sy, sz, kolor, materiał, połysk, siatka]."""
    d = model_potwora(klucz)
    bryly = []
    for c in d["czesci"]:
        mat = d["materialy"][int(c[13])]
        bryly.append([int(c[1]), _r(c[3], 4), _r(c[4], 4), _r(c[5], 4), _r(c[6], 5), _r(c[7], 5), _r(c[8], 5),
                      _r(c[9], 4), _r(c[10], 4), _r(c[11], 4), c[12], mat[0], _r(mat[1], 3), c[15] or ""])
    return {"klucz": klucz, "nazwa": d["nazwa"], "bryly": bryly, "wymiary": d["wymiary"]}


def dzwieki(U):
    ident = czytaj_json(sciezka_repo("swiat/dzwiek_gra/identyfikatory.json"))
    mapa = czytaj_json(sciezka_repo("assets/audio/arkusz/sfx_arkusz_a.json"))
    efekty = {}
    for rola, nazwa in U["dzwieki"].items():
        if rola in ("glosnosc", "opis"):
            continue
        e = mapa["efekty"].get(nazwa)
        if e is None:
            raise BladDanych("dźwięk %s → %s: brak w mapie arkusza" % (rola, nazwa))
        start = e["poczatek"] + max(0.0, float(e.get("atak", 0)) - 0.04)
        efekty[rola] = {"od": _r(start, 3), "koniec": _r(e["koniec"], 3),
                        "glosnosc": U["dzwieki"]["glosnosc"].get(rola, 0.5)}
    muzyka = {}
    for k in U["krainy"]:
        n = k["muzyka"]
        idn = int(ident["muzyka"].get(n) or 0)
        if n.startswith(("muzyka_06", "muzyka_07")):
            raise BladDanych("muzyka %s: Bagno i Dżungla nie mają praw gry — nie używać" % n)
        muzyka[k["id"]] = idn
    return {"arkusz": int(ident["arkusz"] or 0), "efekty": efekty, "muzyka": muzyka,
            "glosnosc_muzyki": U["dzwieki"]["glosnosc"].get("muzyka", 0.3)}


def kraina(U, K, nr):
    zn = czytaj_json(sciezka_repo(K["mapa"] + "/znaczniki.json"))
    if zn["kontener"]["X0"] != X0 or zn["kontener"]["Z0"] != Z0 or zn["kontener"].get("obrot_y", 0) != 0:
        raise BladDanych("%s: inny układ mapy niż (1100 + u; y; −700 + v)" % K["id"])
    strefy = {s["id"]: s for s in zn["strefy"]}
    zagrody = []
    for z in K["zagrody"]:
        s = strefy.get(z["strefa"])
        if s is None:
            raise BladDanych("%s: brak strefy %s w znaczniki.json" % (K["id"], z["strefa"]))
        if z["gatunek"] not in U["gatunki"]:
            raise BladDanych("%s/%s: gatunek %s bez liczb w ustawieniach" % (K["id"], z["strefa"], z["gatunek"]))
        wezly = [swiat(U, w[0], w[1], w[2]) for w in s["wezly"]] + [swiat(U, *s["srodek"])]
        zagrody.append({"id": "%s_%s" % (K["id"], z["strefa"]), "strefa": z["strefa"], "gatunek": z["gatunek"],
                        "ile": int(z["ile"]), "srodek": swiat(U, *s["srodek"]), "r": s["r"],
                        "wezly": wezly, "nazwa_mapy": s["potwor"]})
    st = zn["straznik"]
    br = K["brama"]
    p = U["przesuniecie"]
    return {"nr": nr, "id": K["id"], "nazwa": K["nazwa"], "folder": K["folder"],
            "xOd": _r(X0 + K["u"][0] + p[0]), "xDo": _r(X0 + K["u"][1] + p[0]),
            "start": swiat(U, K["start_u"], 0, 0), "patrz": swiat(U, K["start_u"] + 30, 0, 0),
            "brama": {"x": _r(X0 + br["u"] + p[0]), "z": _r(Z0 + p[2]), "wymagana": br["wymagana_moc"],
                      "dokad": br["dokad"], "wrota": br["wrota"], "szerokosc": 80, "wysokosc": 40},
            "zagrody": zagrody,
            "straznik": {"nazwa_mapy": st["potwor"], "miejsce": swiat(U, st["miejsce"][0], st.get("y", 0), st["miejsce"][1]),
                         "arena": swiat(U, st["arena"]["srodek"][0], 0, st["arena"]["srodek"][1]), "r": st["arena"]["r"]}}


def dane(U):
    krainy = [kraina(U, K, i + 1) for i, K in enumerate(U["krainy"])]
    gatunki = {}
    uzyte = {z["gatunek"] for k in krainy for z in k["zagrody"]}
    for g in sorted(uzyte):
        m = model_potwora(g)
        w = m["wymiary"]
        G = U["gatunki"][g]
        gatunki[g] = {"nazwa": G["nazwa"], "hp": G["hp"], "moc": G["moc"], "monety": G["monety"],
                      "promien": _r(max(1.2, min(w["promien"], max(w["szerokosc"], w["glebokosc"]) / 2))),
                      "wysokosc": _r(w["wysokosc"]), "czesci": len(m["czesci"])}
    pow_ = U["powrot"]
    D = {
        "wersja": 1,
        "kontener": U["kontener"], "prefiks": U["prefiks"], "wylacznik": U["wylacznik"], "autostart": U["autostart"],
        "folderWzorcow": U["folder_wzorcow_rs"],
        "przesuniecie": U["przesuniecie"],
        "krainy": krainy, "gatunki": gatunki,
        "potwory": {k: v for k, v in U["potwory"].items() if k != "opis"},
        "rzadki": {k: v for k, v in U["rzadki"].items() if k != "opis"},
        "bonk": {k: v for k, v in U["bonk"].items() if k != "opis"},
        "moc": {k: v for k, v in U["moc"].items() if k != "opis"},
        "lot": {k: v for k, v in U["lot"].items() if k != "opis"},
        "zapis": {k: v for k, v in U["zapis"].items() if k != "opis"},
        "portal": {k: v for k, v in U["portal"].items() if k != "opis"},
        "powrot": swiat(U, pow_["u"], 0, pow_["v"]),
        "widok": {k: v for k, v in U["widok"].items() if k != "opis"},
        "ui": {k: v for k, v in U["ui"].items() if k != "opis"},
        "dzwieki": dzwieki(U),
    }
    tekst = json.dumps(D, sort_keys=True, ensure_ascii=False)
    D["skrot"] = hashlib.sha1(tekst.encode("utf-8")).hexdigest()[:12]
    return D


# ------------------------------------------------------------------------------------------------ Luau
def luau(v, wciecie=0):
    """Wartość Pythona jako literał Luau (słowniki z kluczami-identyfikatorami jako pola)."""
    if v is None:
        return "nil"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if v == int(v) and abs(v) < 1e15:
            return str(int(v))
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, (list, tuple)):
        if all(not isinstance(x, (dict, list, tuple)) for x in v):
            return "{ " + ", ".join(luau(x) for x in v) + " }" if v else "{}"
        w = "\t" * (wciecie + 1)
        return "{\n" + "".join(w + luau(x, wciecie + 1) + ",\n" for x in v) + "\t" * wciecie + "}"
    if isinstance(v, dict):
        if not v:
            return "{}"
        w = "\t" * (wciecie + 1)
        czesci = []
        for k in sorted(v):
            klucz = k if (isinstance(k, str) and k.isidentifier() and k.isascii() and k not in SLOWA_LUAU) else "[%s]" % luau(k)
            czesci.append("%s%s = %s,\n" % (w, klucz, luau(v[k], wciecie + 1)))
        return "{\n" + "".join(czesci) + "\t" * wciecie + "}"
    raise TypeError(type(v))


def tekst_danych(D):
    return ("--[[\n\tDaneBonk — WYGENEROWANE przez swiat/bonk/dane.py z swiat/bonk/ustawienia.json, map pasów (znaczniki.json)\n"
            "\ti modeli potworów (swiat/test_walki2/dane). NIE EDYTUJ RĘCZNIE: zmień ustawienia i uruchom\n"
            "\tpython -B swiat/bonk/dane.py. Położenia w układzie świata BONK (mapa przesunięta o `przesuniecie`).\n]]\n"
            + STRAZNIK + "\n\treturn {}\nend\n\nreturn " + luau(D) + "\n")


def wszystkie_pliki():
    U = ustawienia()
    D = dane(U)
    return U, D, {PLIK_DANYCH: tekst_danych(D)}


def nieaktualne(pliki):
    zle = []
    for nazwa, tekst in pliki.items():
        s = os.path.join(ZRODLA, nazwa)
        try:
            with open(s, encoding="utf-8") as f:
                if f.read().replace("\r\n", "\n") != tekst:
                    zle.append(nazwa)
        except OSError:
            zle.append(nazwa)
    return zle


def tabela(U, D):
    w = ["BONK — dane %s: %d krainy, %d gatunków" % (D["skrot"], len(D["krainy"]), len(D["gatunki"]))]
    for k in D["krainy"]:
        w.append("  %-10s x %.0f…%.0f  brama x %.0f: Moc %s → %s" % (k["nazwa"], k["xOd"], k["xDo"], k["brama"]["x"],
                                                                    k["brama"]["wymagana"], k["brama"]["dokad"]))
        for z in k["zagrody"]:
            g = D["gatunki"][z["gatunek"]]
            w.append("    %-10s %-16s ×%d  życie %-8s Moc +%-5s monety %-5s brył %d" % (
                z["id"], g["nazwa"], z["ile"], g["hp"], g["moc"], g["monety"], g["czesci"]))
    return w


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Dane BONK → zrodla/DaneBonk.luau")
    ap.add_argument("--sprawdz", action="store_true")
    a = ap.parse_args()
    try:
        U, D, pliki = wszystkie_pliki()
    except BladDanych as e:
        print("BŁĄD danych:", e)
        return 2
    for linia in tabela(U, D):
        print(linia)
    zle = nieaktualne(pliki)
    if a.sprawdz:
        print("dane: %s" % ("aktualne" if not zle else "NIEAKTUALNE: " + ", ".join(zle)))
        return 1 if zle else 0
    os.makedirs(ZRODLA, exist_ok=True)
    for nazwa in zle:
        with open(os.path.join(ZRODLA, nazwa), "w", encoding="utf-8", newline="\n") as f:
            f.write(pliki[nazwa])
        print("zapisano zrodla/%s" % nazwa)
    if not zle:
        print("bez zmian")
    return 0


if __name__ == "__main__":
    sys.exit(main())
