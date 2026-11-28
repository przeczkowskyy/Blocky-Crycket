#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dane pakietu „miasteczko-bazar w grze” → zrodla/DaneBazaru.luau (wygenerowany, nie edytować ręcznie).

    python -B swiat/miasteczko_bazar_gra/dane.py              # zapisuje zrodla/DaneBazaru.luau (gdy się zmienił)
    python -B swiat/miasteczko_bazar_gra/dane.py --sprawdz    # kod 1, gdy plik jest nieaktualny (nic nie zapisuje)
    python -B swiat/miasteczko_bazar_gra/dane.py --wyjscie DIR   # zapis do innego folderu (testy determinizmu)

Źródła (tylko odczyt):
  miejsca.json                              — ustawienia pakietu: akcje, teksty, sygnały, czasy, zasięgi (bez położeń)
  swiat/miasteczko_bazar/znaczniki.json     — WSZYSTKIE położenia w bazarze (start, punkty E, tablica, granice)
  swiat/miasteczko_bazar/uklad.json         — granice pola gry i części bazaru
Żadnych liczb położeń w kodzie. Od 26.11.2026 bez przejść stare ↔ nowe miasteczko: starego miasteczka
i starego startu nie ma już w miejscu gry, więc pakiet nie czyta swiat/krzywe_miasteczko.

Do danych dopisywane są przypadki wzorcowe logiki (logika_bazaru.przypadki): wynik liczy lustro w Pythonie,
a SerwerBazaru przy starcie i test offline (luau_mini) sprawdzają, że LogikaBazaru.luau daje to samo.
"""
import argparse
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if not sys.path or sys.path[0] != TU:  # własny folder pierwszy (w repo jest kilka zbuduj.py i dane*.py)
    sys.path.insert(0, TU)
import logika_bazaru as LB  # noqa: E402

KONFIG = os.path.join(TU, "miejsca.json")
ZRODLA = os.path.join(TU, "zrodla")
PLIK_LUAU = "DaneBazaru.luau"
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'


def czytaj_json(sciezka):
    with open(sciezka, encoding="utf-8-sig") as f:
        return json.load(f)


def sciezka_repo(wzgledna):
    return os.path.join(REPO, *wzgledna.split("/"))


class BladDanych(Exception):
    pass


def znajdz(zn, sciezka):
    """Element znaczników po ścieżce „a/b/c”: w liście — element o tym id, w słowniku — klucz."""
    o = zn
    for kawalek in sciezka.split("/"):
        if isinstance(o, list):
            pasujace = [x for x in o if isinstance(x, dict) and x.get("id") == kawalek]
            if len(pasujace) != 1:
                raise BladDanych("znacznik %s: w liście %d elementów o id %r" % (sciezka, len(pasujace), kawalek))
            o = pasujace[0]
        elif isinstance(o, dict):
            if kawalek not in o:
                raise BladDanych("znacznik %s: brak klucza %r" % (sciezka, kawalek))
            o = o[kawalek]
        else:
            raise BladDanych("znacznik %s: %r nie jest listą ani słownikiem" % (sciezka, kawalek))
    return o


def _r(v, n=4):
    """Zaokrąglenie liczb (stabilny zapis w Luau)."""
    if isinstance(v, (list, tuple)):
        return [_r(x, n) for x in v]
    x = round(float(v), n)
    return 0.0 if x == 0 else x


def _dodaj(a, b):
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]


def wszystko():
    """→ (konfig, znaczniki, D) — D to dane dla Luau (bez przypadków i skrótu dopisywanych w dane_z_przypadkami)."""
    K = czytaj_json(KONFIG)
    zn = czytaj_json(sciezka_repo(K["znaczniki"]))
    ub = czytaj_json(sciezka_repo(zn["uklad"]))
    pp = K["podpowiedz"]

    start = zn["start"]
    start_punkt = _r(start["swiat"])
    kier = _r(start["kier"])
    D = {
        "wersja": 1,
        "kontener": K["kontener"],
        "prefiks": K["prefiks"],
        "mapa": K["mapa"],
        "zdarzenie_okien": K["zdarzenie_okien"],
        "sygnal_hud": K["sygnal_hud"],
        "podpowiedz": {"zasieg": pp["zasieg"], "zapas": pp["zapas_serwera"], "klawisz": pp["klawisz"], "pad": pp["pad"],
                       "linia_wzroku": pp["linia_wzroku"], "wysokosc_korzenia": pp["wysokosc_korzenia"]},
        "czasy": {k: v for k, v in K["czasy"].items() if k != "opis"},
        "teksty": dict(K["teksty"]),
        "dymek": {k: v for k, v in K["dymek"].items() if k != "opis"},
        "tabliczka": {k: v for k, v in K["tabliczka"].items() if k != "opis"},
        "start": {
            "punkt": start_punkt,
            "korzen": _r(_dodaj(start_punkt, [0, pp["wysokosc_korzenia"], 0])),
            "patrz": _r(_dodaj(start_punkt, [kier[0] * 10, pp["wysokosc_korzenia"], kier[2] * 10])),
            "kier": kier,
        },
    }
    X0, Z0 = zn["kontener"]["X0"], zn["kontener"]["Z0"]
    g = ub["granice"]
    D["bazar"] = {
        "pole_x": _r([X0 + g["pole_gry_x"][0], X0 + g["pole_gry_x"][1]]),
        "pole_z": _r([Z0 + g["pole_gry_z"][0], Z0 + g["pole_gry_z"][1]]),
        "czesci_x": _r([X0 + g["czesci_x"][0], X0 + g["czesci_x"][1]]),
        "czesci_z": _r([Z0 + g["czesci_z"][0], Z0 + g["czesci_z"][1]]),
    }

    kolejnosc, miejsca = [], {}
    for m in K["miejsca"]:
        mid = m["id"]
        if mid in miejsca:
            raise BladDanych("powtórzone id miejsca %r w miejsca.json" % mid)
        w = {
            "id": mid,
            "akcja": m["akcja"],
            "obiekt": m["obiekt"],
            "akcja_tekst": m["akcja_tekst"],
            "postac": m["postac"],
            "dymek": m["dymek"],
            "zasieg": m.get("zasieg", pp["zasieg"]),
        }
        for klucz in ("hud", "gui", "dymek_otwarte", "cel", "tabliczka"):
            if m.get(klucz) is not None:
                w[klucz] = m[klucz]
        if w.get("hud") is not None and w["hud"] not in K["przyciski_hud"]                 and w["hud"] not in K.get("sygnaly_hud_bez_przycisku", {}):
            raise BladDanych("%s: hud %r nie jest przyciskiem HUD %s ani sygnałem bez przycisku %s"
                             % (mid, w["hud"], K["przyciski_hud"], sorted(K.get("sygnaly_hud_bez_przycisku", {}))))
        if m.get("znacznik"):
            z = znajdz(zn, m["znacznik"])
            if "podpowiedz" not in z or "stoisko" not in z:
                raise BladDanych("%s: znacznik %s bez „podpowiedz” albo „stoisko”" % (mid, m["znacznik"]))
            w["znacznik"] = m["znacznik"]
            w["znacznik_id"] = z["id"]
            w["punkt"] = _r(z["podpowiedz"])
            w["stoisko"] = _r(z["stoisko"])
            w["dymek_nad"] = _r(_dodaj(w["punkt"], [0, K["dymek"]["nad_podpowiedzia"], 0]))
            if z.get("model"):
                w["model"] = z["model"]
            if z.get("czesc_podpowiedzi"):
                w["czesc_mapy"] = z["grupa_zaczepu"] + "/" + z["czesc_podpowiedzi"]
        else:
            raise BladDanych("%s: miejsce bez znacznika — od 26.11.2026 każde miejsce stoi w bazarze" % mid)
        kolejnosc.append(mid)
        miejsca[mid] = w
    D["kolejnosc"] = kolejnosc
    D["miejsca"] = miejsca

    tz = znajdz(zn, K["tablica"]["znacznik"])
    kt = K["tablica"]
    D["tablica"] = {
        "srodek": _r(tz["swiat"]), "normalna": _r(tz["normalna"], 6), "rozmiar": _r(tz["rozmiar"]),
        "wiersze": kt["wiersze"], "odsuniecie": kt["odsuniecie"], "grubosc": kt["grubosc"], "px_na_stud": kt["px_na_stud"],
        "tytul": kt["tytul"], "naglowek": kt["naglowek"], "pusto": kt["pusto"], "stopka": kt["stopka"],
        "statystyki": list(kt["statystyki"]),
    }
    kl = K["lochy"]
    D["lochy"] = {"blokada": kl["blokada"], "atrybut_gracza": kl["atrybut_gracza"]}
    if kl.get("wymagany_poziom") is not None:
        D["lochy"]["wymagany_poziom"] = kl["wymagany_poziom"]
    if znajdz(zn, "lochy/blokada")["grupa"] != kl["blokada"]:
        raise BladDanych("lochy.blokada %r ≠ znaczniki lochy/blokada %r" % (kl["blokada"], znajdz(zn, "lochy/blokada")["grupa"]))
    D["las"] = {k: v for k, v in K["las"].items() if k != "opis"}
    D["chmury"] = {k: v for k, v in K["chmury"].items() if k != "opis"}
    return K, zn, D


def skrot(D):
    bez = {k: v for k, v in D.items() if k != "skrot"}
    return hashlib.sha1(json.dumps(bez, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]


def dane_z_przypadkami():
    K, zn, D = wszystko()
    D["przypadki"] = LB.przypadki(D)
    D["skrot"] = skrot(D)
    return K, zn, D


# ------------------------------------------------------------------------------------------------ zapis Luau
SLOWA = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in", "local", "nil", "not",
         "or", "repeat", "return", "then", "true", "until", "while", "continue", "type", "export"}


def luau_napis(s):
    return json.dumps(s, ensure_ascii=False)


def luau_wartosc(v, wc=1):
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "nil"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if v == int(v) and abs(v) < 1e15:
            return "%d" % int(v) if v != 0 else "0"
        return repr(v)
    if isinstance(v, str):
        return luau_napis(v)
    if isinstance(v, list):
        if all(not isinstance(x, (dict, list)) for x in v):
            return "{ " + ", ".join(luau_wartosc(x, wc + 1) for x in v) + " }" if v else "{}"
        return "{\n" + "\n".join("\t" * wc + luau_wartosc(x, wc + 1) + "," for x in v) + "\n" + "\t" * (wc - 1) + "}"
    if isinstance(v, dict):
        if not v:
            return "{}"
        linie = []
        for k, x in v.items():
            if x is None:
                continue
            klucz = k if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", k) and k not in SLOWA else "[%s]" % luau_napis(k)
            linie.append("\t" * wc + "%s = %s," % (klucz, luau_wartosc(x, wc + 1)))
        return "{\n" + "\n".join(linie) + "\n" + "\t" * (wc - 1) + "}"
    raise TypeError(type(v))


def tekst_luau(D):
    return ("--[[\n"
            "\tDaneBazaru — WYGENEROWANE przez swiat/miasteczko_bazar_gra/dane.py z miejsca.json i swiat/miasteczko_bazar/\n"
            "\tznaczniki.json (+ uklad.json bazaru). Nie edytuj ręcznie: zmień źródła i uruchom dane.py.\n"
            "\tSkrót danych: %s\n"
            "]]\n" % D["skrot"]
            + STRAZNIK + "\n\treturn {}\nend\n\nreturn " + luau_wartosc(D) + "\n")


def zapisz(folder=ZRODLA):
    _, _, D = dane_z_przypadkami()
    tekst = tekst_luau(D)
    os.makedirs(folder, exist_ok=True)
    sciezka = os.path.join(folder, PLIK_LUAU)
    stary = None
    if os.path.isfile(sciezka):
        with open(sciezka, encoding="utf-8") as f:
            stary = f.read()
    if stary != tekst:
        with open(sciezka, "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst)
        return True, D
    return False, D


def aktualny():
    """(czy plik w zrodla/ jest aktualny, D)."""
    _, _, D = dane_z_przypadkami()
    sciezka = os.path.join(ZRODLA, PLIK_LUAU)
    if not os.path.isfile(sciezka):
        return False, D
    with open(sciezka, encoding="utf-8") as f:
        return f.read() == tekst_luau(D), D


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Dane pakietu miasteczko-bazar w grze → zrodla/DaneBazaru.luau")
    ap.add_argument("--sprawdz", action="store_true", help="kod 1, gdy zrodla/DaneBazaru.luau jest nieaktualny")
    ap.add_argument("--wyjscie", default=None, help="folder zapisu zamiast zrodla/")
    a = ap.parse_args()
    try:
        if a.sprawdz:
            ok, D = aktualny()
            print("DaneBazaru.luau: %s (skrót %s, miejsc %d, przypadków %d)"
                  % ("aktualny" if ok else "NIEAKTUALNY — uruchom python -B swiat/miasteczko_bazar_gra/dane.py",
                     D["skrot"], len(D["kolejnosc"]), len(D["przypadki"])))
            return 0 if ok else 1
        zmieniony, D = zapisz(a.wyjscie or ZRODLA)
    except BladDanych as e:
        print("BŁĄD danych: %s" % e)
        return 2
    print("DaneBazaru.luau %s (skrót %s)" % ("zapisany" if zmieniony else "bez zmian", D["skrot"]))
    print("  %-17s %-8s %-28s %s" % ("miejsce", "akcja", "podpowiedź E (świat)", "znacznik"))
    for mid in D["kolejnosc"]:
        m = D["miejsca"][mid]
        p = m.get("punkt")
        print("  %-17s %-8s %-28s %s" % (mid, m["akcja"], "(%.1f; %.1f; %.1f)" % tuple(p) if p else "(wybiera zbuduj.py)",
                                        m.get("znacznik") or "—"))
    print("  przypadki wzorcowe logiki: %d" % len(D["przypadki"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
