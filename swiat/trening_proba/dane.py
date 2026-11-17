#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator zrodla/DaneTreningu.luau — dane mini-gier Training Center (próba) dla serwera i klienta w Studio.

    python -B swiat/trening_proba/dane.py               # zapisuje zrodla/DaneTreningu.luau
    python -B swiat/trening_proba/dane.py --sprawdz     # kod 1, gdy plik w zrodla/ jest nieaktualny
    python -B swiat/trening_proba/dane.py --wyjscie DIR # zapis do innego folderu (test powtarzalności)

Źródła (tylko odczyt): ustawienia.json (jedyne źródło liczb pakietu), swiat/miasteczko_bazar/znaczniki.json (punkt
trenera w bazarze — zapas, gdy w Studio nie ma kontenera bazaru), swiat/miasteczko_bazar_gra/miejsca.json (id miejsca
i nazwa zdarzenia OknoMiejsca). Położenia w świecie liczy się tu (środek areny + układ lokalny stanowisk), więc w kodzie
Luau nie ma żadnej liczby położenia. Przypadki wzorcowe liczy lustro logika_treningu.py.
"""
import copy
import hashlib
import json
import os
import random
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if not sys.path or sys.path[0] != TU:
    sys.path.insert(0, TU)
import logika_treningu as LT  # noqa: E402

USTAWIENIA = os.path.join(TU, "ustawienia.json")
ZNACZNIKI = os.path.join(REPO, "swiat", "miasteczko_bazar", "znaczniki.json")
MIEJSCA_BAZARU = os.path.join(REPO, "swiat", "miasteczko_bazar_gra", "miejsca.json")
PLIK_LUAU = "DaneTreningu.luau"
ZRODLA = os.path.join(TU, "zrodla")

# 11 plików dźwięku wbudowanych w klienta Roblox (content/sounds; lista z swiat/test_walki2/zrodla/Ustawienia.luau)
DZWIEKI_WBUDOWANE = {"action_falling.ogg", "action_footsteps_plastic.mp3", "action_get_up.mp3", "action_jump.mp3",
                     "action_jump_land.mp3", "action_swim.mp3", "impact_explosion_03.mp3", "impact_water.mp3",
                     "oof.ogg", "ouch.ogg", "volume_slider.ogg"}
KLAWISZE = {"Up", "Down", "Left", "Right", "W", "A", "S", "D", "F", "Q", "E", "Space", "Return", "Thumbstick1",
            "DPadUp", "DPadDown", "DPadLeft", "DPadRight", "ButtonA", "ButtonB", "ButtonX", "ButtonY", "ButtonR1",
            "ButtonR2", "ButtonL1", "ButtonSelect"}

# nazwy instancji areny, które klient animuje lokalnie (scena.py buduje je pod tymi nazwami)
NAZWY = {
    "arena": "Arena",
    "miotacz_ramie": "Arena/Sila/Miotacz/RamieP",
    "strefy": "Arena/Sila/Strefy",
    "golem_piesc": "Arena/Pancerz/Golem/Piesc",
    "golem_oczy": ["Arena/Pancerz/Golem/OkoL", "Arena/Pancerz/Golem/OkoP"],
    "tablica_wyboru": "Arena/Lobby/TablicaWyboru/E",
    "wyjscie": "Arena/Lobby/Wyjscie/E",
    "tablica_wejscia": "TablicaWejscia/E",
}


class BladDanych(Exception):
    pass


def _czytaj_json(sciezka):
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def _dodaj(a, b):
    return [round(a[i] + b[i], 4) for i in range(3)]


def _sprawdz(K):
    """Reguły ustawień → BladDanych z opisem."""
    st = K["statystyki"]
    ids = [s["id"] for s in st]
    if len(ids) != 6 or len(set(ids)) != 6:
        raise BladDanych("statystyk ma być sześć, bez powtórzeń: %s" % ids)
    for s in st:
        if s["stan"] not in ("grywalna", "w_projekcie"):
            raise BladDanych("zły stan %s: %s" % (s["id"], s["stan"]))
        if (s["stan"] == "grywalna") != (s["id"] in K["gry"]):
            raise BladDanych("%s: stan „grywalna” wymaga wpisu w gry (i odwrotnie)" % s["id"])
        if s["stan"] == "grywalna" and s["id"] not in K["stanowiska"]:
            raise BladDanych("%s: brak stanowiska" % s["id"])
        if not re.fullmatch(r"[0-9A-F]{6}", s["kolor"]):
            raise BladDanych("%s: kolor %s" % (s["id"], s["kolor"]))
    for gid, G in K["gry"].items():
        poz = G["poziomy"]
        if not poz or poz[0]["od_s"] != 0:
            raise BladDanych("%s: pierwszy poziom musi zaczynać się od 0 s" % gid)
        for a, b in zip(poz, poz[1:]):
            if b["od_s"] <= a["od_s"]:
                raise BladDanych("%s: poziomy nie rosną" % gid)
        for p in poz:
            if not (0 < p["okno_s"] < 1):
                raise BladDanych("%s: okno %s" % (gid, p["okno_s"]))
            # rozdzielność: najkrótszy odstęp dłuższy niż dwa okna + 0,05 s — zgłoszenie zawsze wskazuje jedno zdarzenie
            if p["odstep_s"] * (1 - G["rozrzut"]) <= 2 * p["okno_s"] + 0.05:
                raise BladDanych("%s: odstęp %s za krótki przy oknie %s" % (gid, p["odstep_s"], p["okno_s"]))
            if G["typ"] == "kierunki" and not (1 <= p["kierunki"] <= len(G["kierunki"])):
                raise BladDanych("%s: kierunki %s" % (gid, p["kierunki"]))
            if G["typ"] == "blok" and not (0 <= p["zmylki"] <= 0.5):
                raise BladDanych("%s: zmyłki %s" % (gid, p["zmylki"]))
        if G["typ"] == "kierunki" and sorted(G["akcje"]) != sorted(G["kierunki"]):
            raise BladDanych("%s: akcje ≠ kierunki" % gid)
        if G["typ"] == "blok" and G["akcje"] != ["blok"]:
            raise BladDanych("%s: akcja bloku" % gid)
        if G["typ"] not in ("kierunki", "blok"):
            raise BladDanych("%s: typ %s" % (gid, G["typ"]))
        if not (0 <= G["rozrzut"] < 0.5):
            raise BladDanych("%s: rozrzut" % gid)
    P = K["przyrost"]
    if len(P["za_trafienie"]) != len(P["progi_serii"]) + 1:
        raise BladDanych("przyrost: za_trafienie ma mieć o jeden wpis więcej niż progi_serii")
    if P["progi_serii"] != sorted(set(P["progi_serii"])) or P["za_trafienie"] != sorted(P["za_trafienie"]):
        raise BladDanych("przyrost: progi i przyrosty mają rosnąć")
    if any((not isinstance(x, int)) or x < 1 for x in P["za_trafienie"]):
        raise BladDanych("przyrost: jednostki za trafienie — liczby całkowite ≥ 1")
    if not P["mnoznik_centrum"] >= 1 or not P["prog_paska"] > 0 or not P["polowa_udzialu"] > 0:
        raise BladDanych("przyrost: mnoznik_centrum ≥ 1, prog_paska > 0, polowa_udzialu > 0")
    if not P["pula_baza"] > 0 or P["pula_na_poziom"] < 0 or not isinstance(P["malejacy_zysk"], bool):
        raise BladDanych("przyrost: pula_baza > 0, pula_na_poziom ≥ 0, malejacy_zysk true/false")
    O = K["ochrona"]
    for k in ("pojemnosc", "uzupelnianie_na_s", "max_opoznienie_s", "przypisanie_s", "odstep_wejsc_s",
              "odstep_startu_s", "zasieg_wejscia", "wiadomosci_pojemnosc", "wiadomosci_na_s", "tik_s"):
        if not O[k] > 0:
            raise BladDanych("ochrona.%s ma być > 0" % k)
    if O["pojemnosc"] < 1:
        raise BladDanych("ochrona.pojemnosc < 1")
    U = K["ui"]
    if U["przycisk_maly_px"] * U["skala_min"] < U["wymog_przycisk_px"]:
        raise BladDanych("ui: najmniejszy przycisk przy skali minimalnej < %d px" % U["wymog_przycisk_px"])
    if min(U["tekst_px"].values()) * U["skala_min"] < U["wymog_tekst_pt"]:
        raise BladDanych("ui: najmniejszy tekst przy skali minimalnej < %d pt" % U["wymog_tekst_pt"])
    for n, d in K["dzwieki"].items():
        if isinstance(d, dict) and d["plik"] not in DZWIEKI_WBUDOWANE:
            raise BladDanych("dźwięk %s: %s nie jest wbudowany w klienta Roblox" % (n, d["plik"]))
    for n, s in K["sterowanie"].items():
        klawisze = s if isinstance(s, list) else s["klawisze"] + s["pad"]
        for k in klawisze:
            if k not in KLAWISZE:
                raise BladDanych("sterowanie %s: nieznany klawisz %s" % (n, k))


def _swiat(K):
    """Położenia w świecie: środek areny + układ lokalny (Y w górę, gracz na stanowisku patrzy na −Z)."""
    c = K["arena"]["srodek"]
    S = {"przybycie": _dodaj(c, K["arena"]["przybycie"]), "patrz_przybycie": _dodaj(c, K["arena"]["patrz_przybycie"])}
    for gid, st in K["stanowiska"].items():
        p = _dodaj(c, st["podest"])
        w = {"podest": p, "patrz": _dodaj(p, [0, 0, -10]),
             "oko": _dodaj(p, st["kamera"]["oko"]), "cel": _dodaj(p, st["kamera"]["cel"])}
        if gid == "sila":
            w["miotacz"] = _dodaj(p, st["miotacz"])
            w["reka"] = _dodaj(w["miotacz"], st["reka"])
            w["strefy"] = {k: _dodaj(p, v) for k, v in st["strefy"].items()}
            w["luki"] = st["luki"]
            w["miecz"] = _dodaj(p, st["miecz"])
        else:
            g = _dodaj(p, st["golem"])
            w["golem"] = g
            for k in ("piesc_spoczynek", "piesc_zamach"):
                w[k] = _dodaj(g, st[k])
            for k in ("piesc_cel", "tarcza", "tarcza_blok"):
                w[k] = _dodaj(p, st[k])
        S[gid] = w
    return S


def _trener():
    """Punkt podpowiedzi E trenera w bazarze (znaczniki.json) i nazwa zdarzenia okien z pakietu bazaru."""
    z = _czytaj_json(ZNACZNIKI)["training_center"]
    m = _czytaj_json(MIEJSCA_BAZARU)
    ids = [x.get("id") for x in m["miejsca"]]
    return z, m, ids


def wczytaj():
    K = _czytaj_json(USTAWIENIA)
    _sprawdz(K)
    z, m, ids = _trener()
    if K["id_miejsca_bazaru"] not in ids:
        raise BladDanych("w miejsca.json bazaru nie ma miejsca %s" % K["id_miejsca_bazaru"])
    if [s["id"] for s in K["statystyki"]] != z["statystyki"]:
        raise BladDanych("kolejność statystyk ≠ znaczniki.json bazaru (%s)" % z["statystyki"])
    D = {
        "wersja": 1,
        "kontener": K["kontener"],
        "prefiks": K["prefiks"],
        "zdarzenie_okien": K["zdarzenie_okien"],
        "id_miejsca_bazaru": K["id_miejsca_bazaru"],
        "bazar": {"kontener": K["bazar"]["kontener"], "podpowiedz": K["bazar"]["podpowiedz"],
                  "punkt_zapasowy": z["podpowiedz"]},
        "arena": K["arena"],
        "statystyki": K["statystyki"],
        "runda": K["runda"],
        "przyrost": K["przyrost"],
        "ochrona": K["ochrona"],
        "gry": K["gry"],
        "swiat": _swiat(K),
        "podpowiedz": K["podpowiedz"],
        "ui": K["ui"],
        "sterowanie": K["sterowanie"],
        "dzwieki": K["dzwieki"],
        "teksty": K["teksty"],
        "nazwy": NAZWY,
        "tablica_wejscia": K["tablica_wejscia"],
    }
    return K, D


# ------------------------------------------------------------------------------------------------ przypadki wzorcowe
def _sekwencja(D, gra, z, t0, rnd, ile=16):
    """Kroki próby: trafienia, pudła, spam, złe wartości, czasy spoza zakresu, przeterminowanie i koniec rundy."""
    O = D["ochrona"]
    G = D["gry"][gra]
    pl = LT.plan(D, gra, z)
    kroki = []
    teraz = t0
    for e in pl[:ile]:
        cel = t0 + e["t"]
        rodzaj = rnd.choice(["traf", "traf", "traf", "brzeg", "zle", "wczesnie", "pozno", "pomin", "spam", "zla",
                             "przyszlosc", "stary", "podwojne"])
        if rodzaj == "pomin":
            teraz = max(teraz, cel + e["okno"] + O["max_opoznienie_s"] + 0.05)
            kroki.append({"typ": "p", "teraz": round(teraz, 3)})
            continue
        if rodzaj == "traf":
            tk = cel + round(rnd.uniform(-0.8, 0.8) * e["okno"], 3)
        elif rodzaj == "brzeg":
            tk = cel + e["okno"]
        elif rodzaj == "wczesnie":
            tk = cel - e["okno"] - 0.1
        elif rodzaj == "pozno":
            tk = cel + e["okno"] + 0.08
        else:
            tk = cel + round(rnd.uniform(-0.5, 0.5) * e["okno"], 3)
        przybycie = round(max(teraz, tk + rnd.uniform(0.02, 0.2)), 3)
        teraz = przybycie
        if G["typ"] == "kierunki":
            dobra = e["wartosc"]
            zla = [k for k in G["akcje"] if k != dobra][rnd.randrange(len(G["akcje"]) - 1)]
        else:
            dobra, zla = "blok", "blok"
        w = zla if rodzaj == "zle" else dobra
        if rodzaj == "zla":
            kroki.append({"typ": "z", "w": "miecz", "tk": round(tk, 3), "teraz": teraz})
        elif rodzaj == "przyszlosc":
            kroki.append({"typ": "z", "w": w, "tk": round(teraz + 5, 3), "teraz": teraz})
        elif rodzaj == "stary":
            kroki.append({"typ": "z", "w": w, "tk": round(teraz - 3, 3), "teraz": teraz})
        elif rodzaj == "spam":
            for _ in range(7):
                kroki.append({"typ": "z", "w": w, "tk": round(tk, 3), "teraz": teraz})
        elif rodzaj == "podwojne":
            kroki.append({"typ": "z", "w": w, "tk": round(tk, 3), "teraz": teraz})
            kroki.append({"typ": "z", "w": w, "tk": round(tk + 0.05, 3), "teraz": round(teraz + 0.05, 3)})
            teraz = round(teraz + 0.05, 3)
        else:
            kroki.append({"typ": "z", "w": w, "tk": round(tk, 3), "teraz": teraz})
        if rnd.random() < 0.3:
            kroki.append({"typ": "p", "teraz": teraz})
    kroki.append({"typ": "p", "teraz": round(t0 + D["runda"]["dlugosc_s"] + 1, 3)})
    kroki.append({"typ": "z", "w": G["akcje"][0], "tk": round(t0 + D["runda"]["dlugosc_s"] + 1, 3),
                  "teraz": round(t0 + D["runda"]["dlugosc_s"] + 1, 3)})
    return kroki


def przypadki(D):
    rnd = random.Random(17112026)
    P = {"plany": [], "sekwencje": [], "przyrosty": [], "wejscia": [], "skale": []}
    for gra in sorted(D["gry"]):
        for z in (1, 7, 12345, 99999, 2147483000, 31337):
            pl = LT.plan(D, gra, z)
            P["plany"].append({"gra": gra, "ziarno": z, "n": len(pl), "suma_t": round(sum(e["t"] for e in pl), 6),
                               "pierwsze": [[e["t"], e["wartosc"]] for e in pl[:6]]})
        for _ in range(6):
            z = rnd.randrange(1, 2 ** 31 - 2)
            t0 = round(rnd.uniform(10, 5000), 3)
            kroki = _sekwencja(D, gra, z, t0, rnd)
            s0 = {"pasek": round(rnd.uniform(0, 30), 3), "W": rnd.randrange(0, 40), "pula": LT.pula(D, rnd.randrange(1, 66))}
            kod, R = LT.wykonaj_kroki(D, gra, z, t0, kroki, s0)
            P["sekwencje"].append({"gra": gra, "ziarno": z, "t0": t0, "kroki": kroki, "s0": s0, "wynik": {
                "kod": kod, "trafienia": R["trafienia"], "pudla": R["pudla"], "puste": R["puste"], "spam": R["spam"],
                "najdluzsza": R["najdluzsza"], "suma": R["suma"], "koniec": R["koniec"], "jednostki": R["jednostki"],
                "W": R["W"], "pasek": round(R["pasek"], 9)}})
    for seria in range(0, 26):
        P["przyrosty"].append([seria, LT.przyrost(D, seria)])
    O = D["ochrona"]
    zas = O["zasieg_wejscia"]
    for gra, ost, runda, teraz, odl, wa in [
        ("sila", LT.NIGDY, False, 100.0, 5.0, False), ("pancerz", LT.NIGDY, False, 100.0, zas, False),
        ("sila", LT.NIGDY, False, 100.0, zas + 0.01, False), ("sila", LT.NIGDY, False, 100.0, None, False),
        ("sila", LT.NIGDY, False, 100.0, None, True), ("sila", 99.0, False, 100.0, 1.0, False),
        ("sila", 100.0 - O["odstep_wejsc_s"], False, 100.0, 1.0, False), ("kondycja", LT.NIGDY, False, 100.0, 1.0, False),
        ("szczescie", LT.NIGDY, False, 100.0, 1.0, True), ("nic", LT.NIGDY, False, 100.0, 1.0, False),
        ("pancerz", LT.NIGDY, True, 100.0, 1.0, True), ("pancerz", LT.NIGDY, True, 100.0, 1.0, False)]:
        S = LT.nowy_gracz()
        S["ostatnieWejscie"] = ost
        if runda:
            S["runda"] = {"koniec": False}
        w = LT.wejscie(D, gra, S, teraz, odl, wa)
        c = {"gra": gra, "ostatnie": ost, "runda": runda, "teraz": teraz, "wArenie": wa, "ok": w["ok"], "powod": w["powod"]}
        if odl is not None:
            c["odl"] = odl
        P["wejscia"].append(c)
    for w, h in [(667, 375), (568, 320), (812, 375), (1280, 720), (1920, 1080), (2560, 1440), (480, 270), (1024, 768)]:
        P["skale"].append([w, h, LT.skala_ui(D, w, h)])
    return P


def dane_z_przypadkami():
    K, D = wczytaj()
    D = copy.deepcopy(D)
    D["przypadki"] = przypadki(D)
    D["skrot"] = hashlib.sha1(json.dumps(D, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]
    return K, D


# ------------------------------------------------------------------------------------------------ zapis Luau
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SLOWA = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in", "local", "nil",
          "not", "or", "repeat", "return", "then", "true", "until", "while", "continue"}


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
    if isinstance(k, int):
        return "[%d]" % k
    return k if (_IDENT.match(k) and k not in _SLOWA) else "[%s]" % _napis(k)


def _luau(v, wciecie=1):
    if v is None:
        return "nil"
    if isinstance(v, (bool, int, float)):
        return _liczba(v)
    if isinstance(v, str):
        return _napis(v)
    tab = "\t" * wciecie
    if isinstance(v, list):
        czesci = [_luau(x, wciecie + 1) for x in v]
        jedna = "{ " + ", ".join(czesci) + " }" if czesci else "{}"
        if len(jedna) <= 110 and "\n" not in jedna:
            return jedna
        return "{\n" + "".join(tab + c + ",\n" for c in czesci) + "\t" * (wciecie - 1) + "}"
    if isinstance(v, dict):
        czesci = ["%s = %s" % (_klucz(k), _luau(x, wciecie + 1)) for k, x in v.items() if x is not None]
        jedna = "{ " + ", ".join(czesci) + " }" if czesci else "{}"
        if len(jedna) <= 110 and "\n" not in jedna:
            return jedna
        return "{\n" + "".join(tab + c + ",\n" for c in czesci) + "\t" * (wciecie - 1) + "}"
    raise TypeError(repr(v))


def luau_tekst(D):
    naglowek = ("--[[\n\tDaneTreningu — WYGENEROWANE przez swiat/trening_proba/dane.py z ustawienia.json (oraz punktu\n"
                "\ttrenera ze swiat/miasteczko_bazar/znaczniki.json). Nie edytuj ręcznie: zmień ustawienia i uruchom dane.py.\n"
                "\tSkrót danych: %s\n]]\n" % D["skrot"])
    return (naglowek + 'if not game:GetService("RunService"):IsStudio() then\n\treturn {}\nend\n\nreturn '
            + _luau(D) + "\n")


def zapisz(folder):
    _, D = dane_z_przypadkami()
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, PLIK_LUAU), "w", encoding="utf-8", newline="\n") as f:
        f.write(luau_tekst(D))
    return D


def aktualny():
    _, D = dane_z_przypadkami()
    sciezka = os.path.join(ZRODLA, PLIK_LUAU)
    if not os.path.isfile(sciezka):
        return False, D
    with open(sciezka, encoding="utf-8") as f:
        return f.read() == luau_tekst(D), D


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    try:
        if "--sprawdz" in argv:
            ok, D = aktualny()
            print("DaneTreningu.luau: %s (skrót %s, przypadków: plany %d, sekwencje %d)"
                  % ("aktualny" if ok else "NIEAKTUALNY", D["skrot"], len(D["przypadki"]["plany"]),
                     len(D["przypadki"]["sekwencje"])))
            return 0 if ok else 1
        folder = argv[argv.index("--wyjscie") + 1] if "--wyjscie" in argv else ZRODLA
        D = zapisz(folder)
        print("zapisano %s (skrót %s)" % (os.path.join(os.path.relpath(folder, REPO) if folder == ZRODLA else folder,
                                                       PLIK_LUAU), D["skrot"]))
        return 0
    except BladDanych as e:
        print("BŁĄD DANYCH: %s" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
