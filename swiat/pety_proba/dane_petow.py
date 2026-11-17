#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator danych pakietu „jajka i pety na próbę” (swiat/pety_proba) — moduły Luau dla serwera i klienta w Studio.

    python -B swiat/pety_proba/dane_petow.py               # zapisuje zrodla/DanePetow.luau i zrodla/rigi/*.luau
    python -B swiat/pety_proba/dane_petow.py --sprawdz     # kod 1, gdy któryś plik w zrodla/ jest nieaktualny

JEDNA PRAWDA (tylko odczyt cudzych plików, nic nie jest przepisane ręcznie):
  • ustawienia.json (ten pakiet) — pety, skille, rzadkości, cena jajka, teksty, czasy;
  • tools/walka/progresja.py — szanse jajka (ZALOZENIA["szanse_jajka"]) i cena z kalkulatora (ceny_jajek[0]);
  • swiat/las_pas/znaczniki.json — stanowisko jajka (miejsce „jajko”, punkt E „Punkty/StanowiskoJajka”);
  • swiat/miasteczko_bazar/znaczniki.json — zagroda petów (punkt E, kierunek, sześć miejsc na pety);
  • swiat/postacie/<pet>.py i jajko_lesne.py — modele z klocków → rigi (roblox_klocki.rig, próbki liniowe co 2. klatkę).
Nazwa pliku inna niż „dane.py”, bo pakiet czyta też swiat/stan_gracza (tam jest dane.py).
"""
import hashlib
import json
import math
import os
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
WALKA = os.path.join(REPO, "tools", "walka")
for _s in (REPO, TU, WALKA):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import logika_petow as LP  # noqa: E402
import progresja  # noqa: E402

ZRODLA = os.path.join(TU, "zrodla")
RIGI = os.path.join(ZRODLA, "rigi")
PLIK_DANYCH = "DanePetow.luau"
POSTACIE = os.path.join(REPO, "swiat", "postacie")
NAZWY_RIGOW = {"jajko_lesne": "RigJajka"}       # moduły rigów: Rig_<id> (pet) albo nazwa z tej mapy


class BladDanych(Exception):
    pass


def ustawienia():
    with open(os.path.join(TU, "ustawienia.json"), encoding="utf-8") as f:
        return json.load(f)


def _znaczniki(sciezka):
    with open(os.path.join(REPO, *sciezka.split("/")), encoding="utf-8") as f:
        return json.load(f)


def _r(v, n=3):
    return round(float(v), n)


def polozenia(U):
    """Stanowisko jajka (las-pas) i zagroda (bazar) w układzie świata Studio — z map, tylko odczyt."""
    I = U["inkubator"]
    z = _znaczniki(I["znaczniki"])
    m = next((x for x in z["miejsca"] if x["id"] == I["miejsce"]), None)
    e = next((x for x in z["punkty_e"] if x["grupa"] == I["grupa_e"]), None)
    if not m or not e:
        raise BladDanych("brak miejsca %r albo punktu E %r w %s" % (I["miejsce"], I["grupa_e"], I["znaczniki"]))
    gniazdo = [_r(v) for v in m["punkt_swiat"]]
    pe = [_r(v) for v in e["punkt_swiat"]]
    zg = _znaczniki(U["zagroda"]["znaczniki"])["zagroda"]
    pz = zg["punkt_e"]
    kier = pz["kier"]
    n = math.hypot(kier[0], kier[2])
    kz = (kier[0] / n, 0.0, kier[2] / n)                    # przód zagrody (patrzy opiekunka)
    kx = (kz[2], 0.0, -kz[0])                               # „lewo” zagrody w tym samym układzie
    a, b = U["zagroda"]["tablica_od_e"]
    e0 = pz["swiat"]
    tablica = [e0[0] + a * kx[0] + b * kz[0], e0[1], e0[2] + a * kx[2] + b * kz[2]]
    return {
        "gniazdo": gniazdo,
        "obrot_stanowiska": I["obrot_stanowiska"],
        "e_inkubatora": pe,
        "zagroda_e": [_r(v) for v in e0],
        "zagroda_kier": [_r(v, 4) for v in kz],
        "zagroda_tablica": [_r(v) for v in tablica],
        "miejsca_petow": [[_r(v) for v in x["swiat"]] for x in zg["miejsca_petow"]],
        "zagroda_podpowiedz": [_r(v) for v in pz["podpowiedz"]],
    }


def szanse_i_cena(U):
    """Szanse jajka z kalkulatora (tools/walka/progresja.py) na pety z puli w kolejności rzadkości."""
    szanse = list(progresja.ZALOZENIA["szanse_jajka"])
    kalk = progresja.ZALOZENIA["ceny_jajek"][0]
    jajka = []
    for j in U["jajka"]:
        if len(j["pula"]) != len(szanse):
            raise BladDanych("jajko %s: %d petów w puli, a kalkulator ma %d szans" % (j["id"], len(j["pula"]), len(szanse)))
        if j["cena"]["kalkulator"] != kalk:
            raise BladDanych("jajko %s: cena kalkulatora %s ≠ progresja.py %s" % (j["id"], j["cena"]["kalkulator"], kalk))
        jajka.append(dict(j, szanse=[{"pet": p, "szansa": s} for p, s in zip(j["pula"], szanse)]))
    if abs(sum(szanse) - 1.0) > 1e-9:
        raise BladDanych("szanse jajka nie sumują się do 1: %s" % szanse)
    return jajka


# ------------------------------------------------------------------------------------------------ rigi z modeli
def _postac(model_id):
    from swiat.postacie.roblox_postac import postacie_z_modulu
    plik = os.path.join(POSTACIE, model_id + ".py")
    for nazwa in (model_id,):
        for p in postacie_z_modulu(plik):
            if p.id == nazwa:
                return p
    raise BladDanych("brak modelu %s w %s" % (model_id, plik))


def _postac_z_modulu(plik, model_id):
    from swiat.postacie.roblox_postac import postacie_z_modulu
    for p in postacie_z_modulu(os.path.join(POSTACIE, plik + ".py")):
        if p.id == model_id:
            return p
    raise BladDanych("brak modelu %s w %s.py" % (model_id, plik))


def rig_modelu(p, skala=1.0):
    """Postac → zwięzły rig dla Studio: kości, bryły, materiały, zaczep głowy, klipy co 2. klatkę (15 kl./s)."""
    from swiat.postacie.biblioteka.roblox_klocki import probki_liniowe, rig
    bledy, _uwagi = p.sprawdz()
    if bledy:
        raise BladDanych("%s: %s" % (p.id, "; ".join(bledy)))
    p.skala = float(skala)
    d = rig(p, probki_liniowe(p))
    kosci = [[k[0], k[1]] + [_r(v) for v in k[2:11]] for k in d["kosci"]]
    czesci = [[c[0], c[1], c[2]] + [_r(v) for v in c[3:6]] + [_r(v, 4) for v in c[6:9]] + [_r(v) for v in c[9:12]]
              + [c[12].upper(), c[13], c[15]] for c in d["czesci"]]
    klipy = {}
    for kl in d["klipy"]:
        krok = 2 if kl["dl"] % 2 == 0 else 1
        klatki = [[_r(v) for v in kl["klatki"][f]] for f in range(0, kl["dl"] + 1, krok)]
        klipy[kl["n"]] = {"fps": kl["fps"] / krok, "petla": kl["petla"], "kosci": kl["kosci"], "klatki": klatki}
    glowa = next(([z[1]] + [_r(v) for v in z[2:5]] for z in d["zaczepy"] if z[0] == "GlowaAttachment"), None)
    wys = max(c[4] + c[10] / 2 for c in d["czesci"])
    return {"id": p.id, "nazwa": p.nazwa, "skala": skala, "hrp": [_r(v) for v in d["hrp"]], "kosci": kosci,
            "czesci": czesci, "materialy": d["materialy"], "glowa": glowa, "klipy": klipy, "wysokosc": _r(wys),
            "uwagi": d["uwagi"]}


def tablica_inkubatora(U):
    """Bryły tablicy z modelu inkubatora (kość „Tablica”) w układzie stanowiska (środek gniazda na ziemi, przód −Z)."""
    M = U["modele"]
    d = rig_modelu(_postac_z_modulu(M["jajko"], M["inkubator"]), 1.0)
    i_tab = next(i + 1 for i, k in enumerate(d["kosci"]) if k[0] == M["tablica_kosc"])
    # paski szans z modelu są tylko w podglądzie Blendera — w grze rysuje je SurfaceGui (z liczbami i nazwami)
    czesci = [c for c in d["czesci"] if c[0] == i_tab and not c[2].startswith(("Pasek szansy", "Znak peta"))]
    if not any(c[2] == M["papier"] for c in czesci):
        raise BladDanych("tablica inkubatora bez bryły %r (na nią idzie SurfaceGui)" % M["papier"])
    return {"czesci": [c[1:] for c in czesci], "materialy": d["materialy"]}


def rigi(U):
    w = {}
    for p in U["pety"]:
        w[p["id"]] = rig_modelu(_postac_z_modulu(p["id"], p["id"]), p.get("skala", 1.0))
    M = U["modele"]
    w[M["jajko"]] = rig_modelu(_postac_z_modulu(M["jajko"], M["jajko"]), 1.0)
    return w


def nazwa_rigu(model_id):
    return NAZWY_RIGOW.get(model_id, "Rig_" + model_id)


# ------------------------------------------------------------------------------------------------ dane
def podstawa():
    U = ustawienia()
    rz = {r["id"]: r for r in U["rzadkosci"]}
    for p in U["pety"]:
        if p["rzadkosc"] not in rz:
            raise BladDanych("pet %s: nieznana rzadkość %s" % (p["id"], p["rzadkosc"]))
        if not re.match(r"^[A-Za-z0-9_]{1,24}$", p["id"]):
            raise BladDanych("pet %s: id spoza liter, cyfr i „_”" % p["id"])
    D = {
        "wersja": 1,
        "kontener": U["kontener"],
        "prefiks": U["prefiks"],
        "rzadkosci": U["rzadkosci"],
        "pety": U["pety"],
        "jajka": szanse_i_cena(U),
        "modele": U["modele"],
        "rigi": {p["id"]: nazwa_rigu(p["id"]) for p in U["pety"]},
        "rig_jajka": nazwa_rigu(U["modele"]["jajko"]),
        "inkubator": U["inkubator"],
        "zagroda": U["zagroda"],
        "wyklucie": U["wyklucie"],
        "pet_przy_graczu": U["pet_przy_graczu"],
        "limity": U["limity"],
        "teksty": U["teksty"],
        "ukrycie": U["ukrycie"],
        "stan_gracza": U["stan_gracza"],
        "atrybuty_gracza": U["atrybuty_gracza"],
        "polozenia": polozenia(U),
    }
    D["tablica_inkubatora"] = tablica_inkubatora(U)
    return D


def dane_z_przypadkami():
    D = podstawa()
    D["przypadki"] = LP.przypadki(D)
    bez = {k: v for k, v in D.items() if k != "skrot"}
    D["skrot"] = hashlib.sha1(json.dumps(bez, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]
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
    naglowek = ("--[[\n\tDanePetow — WYGENEROWANE przez swiat/pety_proba/dane_petow.py z ustawienia.json, tools/walka/progresja.py,\n"
                "\tznaczników map (las_pas, miasteczko_bazar) i modeli swiat/postacie. NIE EDYTUJ RĘCZNIE: zmień źródło i uruchom\n"
                "\tpython -B swiat/pety_proba/dane_petow.py (testy i zbuduj.py --sucho pilnują aktualności). Status: propozycja.\n]]\n")
    return naglowek + STRAZNIK + _luau(D) + "\n"


def luau_rigu(R):
    naglowek = ("--[[\n\t%s — rig z klocków modelu swiat/postacie (%s, skala %s), WYGENEROWANY przez swiat/pety_proba/dane_petow.py.\n"
                "\tUkład rigu Roblox (przód −Z, początek = ziemia pod postacią). kosci: {nazwa, rodzic, staw xyz, środek xyz,\n"
                "\trozmiar xyz}; czesci: {kość, kształt, nazwa, poz xyz, obrót xyz (rad), rozmiar xyz, kolor, materiał, siatka};\n"
                "\tklipy: klatki co 1/fps s, w wierszu po 6 liczb na kość z listy kosci (przes xyz, obrót xyz). NIE EDYTUJ RĘCZNIE.\n]]\n"
                % (nazwa_rigu(R["id"]), R["id"], _liczba(R["skala"])))
    bez_uwag = {k: v for k, v in R.items() if k != "uwagi"}
    return naglowek + STRAZNIK + _luau(bez_uwag) + "\n"


def wszystkie_pliki():
    """{ścieżka względem zrodla/: tekst} — DanePetow.luau i rigi."""
    D = dane_z_przypadkami()
    U = ustawienia()
    w = {PLIK_DANYCH: luau_danych(D)}
    for mid, R in rigi(U).items():
        w["rigi/%s.luau" % nazwa_rigu(mid)] = luau_rigu(R)
    return D, w


def zapisz():
    D, pliki = wszystkie_pliki()
    os.makedirs(RIGI, exist_ok=True)
    for wzgl, tekst in pliki.items():
        with open(os.path.join(ZRODLA, *wzgl.split("/")), "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst)
    return D, pliki


def aktualny():
    D, pliki = wszystkie_pliki()
    nieaktualne = []
    for wzgl, tekst in pliki.items():
        sciezka = os.path.join(ZRODLA, *wzgl.split("/"))
        if not os.path.isfile(sciezka):
            nieaktualne.append(wzgl)
            continue
        with open(sciezka, encoding="utf-8") as f:
            if f.read() != tekst:
                nieaktualne.append(wzgl)
    return nieaktualne, D, pliki


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    try:
        if "--sprawdz" in argv:
            zle, D, pliki = aktualny()
            print("DanePetow + %d rigów: %s (skrót %s, przypadków: %d)" % (
                len(pliki) - 1, "aktualne" if not zle else "NIEAKTUALNE: " + ", ".join(zle), D["skrot"],
                sum(len(v) for v in D["przypadki"].values())))
            return 0 if not zle else 1
        D, pliki = zapisz()
        for wzgl, tekst in sorted(pliki.items()):
            print("zapisano swiat/pety_proba/zrodla/%s (%d znaków)" % (wzgl, len(tekst)))
        print("skrót %s" % D["skrot"])
        return 0
    except BladDanych as e:
        print("BŁĄD DANYCH: %s" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
