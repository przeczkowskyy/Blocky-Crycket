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


def skala_potworow(U=None):
    return float((U or ustawienia())["potwory"].get("skala", 1))


def straznicy_modele(U=None):
    return {s["model"] for s in (U or ustawienia())["straznicy"]}


def wzorzec(klucz, k=None):
    """Wzorzec potwora do budowy w Studio: bryły w pozie spoczynku (układ rigu: stopy na y = 0, przód = −Z), w skali
    potwory.skala (Strażnicy: straznik.skala). Bryła: [kształt, x, y, z, rx, ry, rz, sx, sy, sz, kolor, materiał,
    połysk, siatka]."""
    if k is None:
        U = ustawienia()
        k = float(U["straznik"]["skala"]) if klucz in straznicy_modele(U) else skala_potworow(U)
    d = model_potwora(klucz)
    bryly = []
    for c in d["czesci"]:
        mat = d["materialy"][int(c[13])]
        bryly.append([int(c[1]), _r(c[3] * k, 4), _r(c[4] * k, 4), _r(c[5] * k, 4), _r(c[6], 5), _r(c[7], 5), _r(c[8], 5),
                      _r(c[9] * k, 4), _r(c[10] * k, 4), _r(c[11] * k, 4), c[12], mat[0], _r(mat[1], 3), c[15] or ""])
    return {"klucz": klucz, "nazwa": d["nazwa"], "bryly": bryly, "wymiary": d["wymiary"]}


def _postacie():
    """Moduły modeli swiat/postacie (tylko odczyt) — import leniwy (repo na ścieżce)."""
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    from swiat.postacie.roblox_postac import postacie_z_modulu
    from swiat.postacie.biblioteka import roblox_klocki as RK
    return postacie_z_modulu, RK


def _bryly_z_rigu(d, k):
    """Rig z klocków (roblox_klocki.rig, układ rigu: ziemia y = 0, przód −Z) → bryły wzorca w pozie spoczynku."""
    bryly = []
    for c in d["czesci"]:
        mat = d["materialy"][int(c[13])]
        bryly.append([int(c[1]), _r(c[3] * k, 4), _r(c[4] * k, 4), _r(c[5] * k, 4), _r(c[6], 5), _r(c[7], 5), _r(c[8], 5),
                      _r(c[9] * k, 4), _r(c[10] * k, 4), _r(c[11] * k, 4), c[12].upper(), mat[0], _r(mat[1], 3), c[15] or ""])
    return bryly


_RIGI = {}


def wzorzec_modelu(modul, model_id, k):
    """Pet albo jajko z swiat/postacie/<modul>.py → wzorzec (bryły w pozie spoczynku, skala k)."""
    klucz = (modul, model_id, k)
    if klucz not in _RIGI:
        postacie_z_modulu, RK = _postacie()
        p = next((x for x in postacie_z_modulu(os.path.join(REPO, "swiat", "postacie", modul + ".py")) if x.id == model_id), None)
        if p is None:
            raise BladDanych("brak modelu %s w swiat/postacie/%s.py" % (model_id, modul))
        d = RK.rig(p, None)
        bryly = _bryly_z_rigu(d, k)
        wys = max(b[2] + b[8] / 2 for b in bryly)
        _RIGI[klucz] = {"klucz": model_id, "nazwa": p.nazwa, "bryly": bryly, "wysokosc": _r(wys)}
    return _RIGI[klucz]


def wzorzec_palki(id_, k):
    """Broń z swiat/postacie/bronie.py → bryły w układzie RightGripAttachment (konwencja Roblox, przód −Z), skala k."""
    klucz = ("bronie", id_, k)
    if klucz not in _RIGI:
        _postacie_z, RK = _postacie()
        from swiat.postacie import bronie
        from swiat.postacie.biblioteka.postac import macierz_obrotu, mnoz, razy_wektor
        a = next((x for x in bronie.akcesoria() if x.id == id_), None)
        if a is None:
            raise BladDanych("brak broni %s w swiat/postacie/bronie.py" % id_)
        bryly = []
        for c in a.czesci_w():
            R0 = macierz_obrotu(*c["r"])
            mat = RK.MATERIALY_ROBLOX.get(c["m"], RK.MATERIALY_ROBLOX["zwykly"])
            for ks, o, R, roz, siatka in RK.rozloz(c, []):
                if min(roz) < 0.001:
                    continue
                pp = RK._poz(tuple(c["p"][i] + razy_wektor(R0, o)[i] for i in range(3)))
                katy = RK._katy_bryly(mnoz(R0, R))
                bryly.append([int(ks), _r(pp[0] * k, 4), _r(pp[1] * k, 4), _r(pp[2] * k, 4), _r(katy[0], 5), _r(katy[1], 5),
                              _r(katy[2], 5), _r(roz[0] * k, 4), _r(roz[1] * k, 4), _r(roz[2] * k, 4), str(c["c"]).upper(),
                              mat[0], _r(mat[1], 3), siatka or ""])
        _RIGI[klucz] = {"klucz": id_, "nazwa": a.nazwa, "bryly": bryly}
    return _RIGI[klucz]


def nazwa_wzorca_peta(pid):
    return "Pet_" + pid


def nazwa_wzorca_jajka(nr):
    return "Jajko_%d" % nr


def nazwa_wzorca_palki(nr):
    return "Palka_%d" % nr


def wzorce_etapu2(U):
    """{nazwa wzorca: dane wzorca} — pety, jajka, pałki (potwory i Strażnicy: wzorzec(klucz))."""
    w = {}
    P = U["pety"]
    for nr, J in enumerate(U["jajka"], 1):
        for p in J["pety"]:
            w[nazwa_wzorca_peta(p["id"])] = wzorzec_modelu(p["id"], p["id"], P["skala"])
        w[nazwa_wzorca_jajka(nr)] = wzorzec_modelu(J["model"], J["model"], P["skala_jajka"])
    for nr, pal in enumerate(U["palki"]["lista"], 1):
        w[nazwa_wzorca_palki(nr)] = wzorzec_palki(pal["id"], U["palki"]["skala"])
    return w


def _miejsce_mapy(K, id_):
    zn = czytaj_json(sciezka_repo(K["mapa"] + "/znaczniki.json"))
    m = next((x for x in zn["miejsca"] if x["id"] == id_), None)
    if m is None:
        raise BladDanych("%s: brak miejsca %r w znaczniki.json" % (K["id"], id_))
    return m["punkt"]


def etap2(U, krainy):
    """Dane etapu 2: pałki, rzadkości, jajka i pety, Strażnicy, pokazanie się, prezent, akcje."""
    nr_krainy = {K["id"]: i + 1 for i, K in enumerate(U["krainy"])}
    W = wzorce_etapu2(U)
    palki = []
    for nr, p in enumerate(U["palki"]["lista"], 1):
        palki.append({"nr": nr, "id": p["id"], "nazwa": p["nazwa"], "cena": p["cena"], "mnoznik": p["mnoznik"],
                      "wzorzec": nazwa_wzorca_palki(nr), "czesci": len(W[nazwa_wzorca_palki(nr)]["bryly"])})
    ceny = [p["cena"] for p in palki]
    if ceny != sorted(ceny) or [p["mnoznik"] for p in palki] != sorted(p["mnoznik"] for p in palki):
        raise BladDanych("pałki: ceny i mnożniki muszą rosnąć")
    sklepy = []
    for s in U["palki"]["sklepy"]:
        sklepy.append({"kraina": nr_krainy[s["kraina"]], "miejsce": swiat(U, s["u"], 0, s["v"])})
    rz = U["rzadkosci"]
    if abs(sum(r["szansa"] for r in rz) - 1) > 1e-9:
        raise BladDanych("szanse rzadkości nie sumują się do 1")
    jajka, pety, kolejnosc = [], {}, []
    for nr, J in enumerate(U["jajka"], 1):
        if nr_krainy.get(J["kraina"]) != nr:
            raise BladDanych("jajka w kolejności krain (%s)" % J["kraina"])
        if len(J["pety"]) != len(rz) or len(J["premie"]) != len(rz):
            raise BladDanych("jajko %s: po jednym pecie i premii na rzadkość" % J["nazwa"])
        K = U["krainy"][nr - 1]
        m = _miejsce_mapy(K, "jajko")
        wj = W[nazwa_wzorca_jajka(nr)]
        jajka.append({"nr": nr, "nazwa": J["nazwa"], "cena": J["cena"], "wzorzec": nazwa_wzorca_jajka(nr),
                      "pety": [p["id"] for p in J["pety"]], "miejsce": swiat(U, m[0], m[1], m[2]),
                      "wysokosc": wj["wysokosc"], "czesci": len(wj["bryly"])})
        for r, p in enumerate(J["pety"], 1):
            if p["id"] in pety:
                raise BladDanych("pet %s w dwóch jajkach" % p["id"])
            wp = W[nazwa_wzorca_peta(p["id"])]
            pety[p["id"]] = {"nazwa": p["nazwa"], "rzadkosc": r, "kraina": nr, "premia": J["premie"][r - 1],
                             "wzorzec": nazwa_wzorca_peta(p["id"]), "wysokosc": wp["wysokosc"], "czesci": len(wp["bryly"])}
            kolejnosc.append(p["id"])
    straznicy = []
    for S in U["straznicy"]:
        nr = nr_krainy[S["kraina"]]
        st = krainy[nr - 1]["straznik"]
        straznicy.append({"kraina": nr, "gatunek": S["model"], "nazwa": S["nazwa"], "hp": S["hp"], "moc": S["moc"],
                          "monety": S["monety"], "miejsce": st["miejsce"], "arena": st["arena"], "r": st["r"]})
    if [s["kraina"] for s in straznicy] != list(range(1, len(krainy) + 1)):
        raise BladDanych("po jednym Strażniku na krainę, w kolejności krain")
    T = U["pokazanie"]["tablice"]
    K1 = U["krainy"][0]
    tablice = []
    for i, tytul in enumerate(U["ui"]["tablice"]):
        u = T["u"] - (i - 1) * T["odstep"]          # patrząc od polany (+Z): pierwsza z lewej
        tablice.append({"nr": i + 1, "tytul": tytul, "miejsce": swiat(U, u, 0, T["v"]),
                        "patrz": swiat(U, u, 0, 0), "szer": T["szer"], "wys": T["wys"]})
    bez_opisu = lambda d: {k: v for k, v in d.items() if k != "opis"}  # noqa: E731
    return {
        "palki": palki, "sklepy": sklepy, "sklep": {"zasieg": U["palki"]["zasieg"]},
        "rzadkosci": [{"nazwa": r["nazwa"], "kolor": r["kolor"], "szansa": r["szansa"]} for r in rz],
        "jajka": jajka, "pety": pety, "petyKolejnosc": kolejnosc, "petyUst": bez_opisu(U["pety"]),
        "straznicy": straznicy, "straznik": bez_opisu(U["straznik"]),
        "pokazanie": {"tablice": tablice, "wierszy": T["wierszy"], "co_s": U["pokazanie"]["co_s"],
                      "korona": U["pokazanie"]["korona"], "nad_glowa": U["pokazanie"]["nad_glowa"]},
        "prezent": bez_opisu(U["prezent"]), "akcje": bez_opisu(U["akcje"]),
    }


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
        k = skala_potworow(U)
        gatunki[g] = {"nazwa": G["nazwa"], "hp": G["hp"], "moc": G["moc"], "monety": G["monety"],
                      "promien": _r(k * max(1.2, min(w["promien"], max(w["szerokosc"], w["glebokosc"]) / 2))),
                      "wysokosc": _r(k * w["wysokosc"]), "czesci": len(m["czesci"])}
    E2 = etap2(U, krainy)
    ks = float(U["straznik"]["skala"])
    for S in E2["straznicy"]:
        g = S["gatunek"]
        m = model_potwora(g)
        w = m["wymiary"]
        gatunki[g] = {"nazwa": S["nazwa"], "hp": S["hp"], "moc": S["moc"], "monety": S["monety"], "straznik": True,
                      "promien": _r(ks * max(1.2, min(w["promien"], max(w["szerokosc"], w["glebokosc"]) / 2))),
                      "wysokosc": _r(ks * w["wysokosc"]), "czesci": len(m["czesci"])}
    pow_ = U["powrot"]
    D = {
        "wersja": 2,
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
    D.update(E2)
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
