#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator danych pakietu „jajka i pety na próbę” (swiat/pety_proba) — moduły Luau dla serwera i klienta w Studio.

    python -B swiat/pety_proba/dane_petow.py               # zapisuje zrodla/DanePetow.luau i zrodla/rigi/*.luau
    python -B swiat/pety_proba/dane_petow.py --sprawdz     # kod 1, gdy któryś plik w zrodla/ jest nieaktualny

JEDNA PRAWDA (tylko odczyt cudzych plików, nic nie jest przepisane ręcznie):
  • ustawienia.json (ten pakiet) — pety, skille, rzadkości, jajka (każde jajko = wpis: pula, cena, model, stanowisko),
    licznik ceny, teksty, czasy;
  • tools/walka/progresja.py — szanse jajek (ZALOZENIA["szanse_jajka"], te same dla każdego jajka) i cena z kalkulatora
    (ceny_jajek[0] — tylko jajko lasu; kalkulator nie ma jajek dalszych biomów);
  • znaczniki map ze „stanowisko.znaczniki” każdego jajka (swiat/las_pas, swiat/bagno_pas) — miejsce „jajko” i punkt
    E „Punkty/StanowiskoJajka”;
  • swiat/miasteczko_bazar/znaczniki.json — zagroda petów (punkt E, kierunek, sześć miejsc na pety);
  • swiat/postacie/<pet>.py, jajko_lesne.py, jajko_bagienne.py — modele z klocków → rigi (roblox_klocki.rig, próbki
    liniowe co 2. klatkę); z modelu inkubatora: stałe bryły („kosci_stale”: tablica, gniazdo, latarnia) i wysokość jajka.
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
TRYBY_LICZNIKA = ("osobny", "wspolny")
KOLEJNOSC_STATYSTYK = ["Strength", "Dexterity", "Intelligence", "Constitution", "Luck", "Armor"]
MALE_RZADKOSCI = ("pospolity", "zwykly")   # D-101: zwykłe pety tylko mała pasywka
MALA_PREMIA_MAKS = 0.03


def sprawdz_skille(U):
    """Skille petów (D-101): jeden stały skill — żywioł (pasywki silnika) i/lub premie do statystyk i łupu; granice
    Sygnaly/Modyfikatory stanu gracza (procent 0..1, łup 0..0,5, do 6 pasywek); pospolite i zwykłe tylko mała premia."""
    import silnik  # noqa: E402  (tools/walka — tylko odczyt: pasywki, które silnik zna)
    znane = {n for n in list(silnik.PASYWNE) + list(silnik.PASYWKI_BRONI) if n != "wskrzeszenie"}
    if sorted(U["statystyki"]) != sorted(KOLEJNOSC_STATYSTYK):
        raise BladDanych("statystyki w ustawieniach ≠ sześć atrybutów gracza %s" % KOLEJNOSC_STATYSTYK)
    for zid, z in U["zywioly"].items():
        if len(z["pasywki"]) > 6 or any(n not in znane for n in z["pasywki"]):
            raise BladDanych("żywioł %s: pasywki spoza silnika albo więcej niż 6: %s" % (zid, z["pasywki"]))
        if z.get("zaklecie") is not None and z["zaklecie"] not in silnik.ZAKLECIA:
            raise BladDanych("żywioł %s: zaklęcie %r spoza silnika %s" % (zid, z["zaklecie"], sorted(silnik.ZAKLECIA)))
        if not z["pasywki"] and z.get("zaklecie") is None:
            raise BladDanych("żywioł %s nic nie daje" % zid)
    for p in U["pety"]:
        s = p["skill"]
        m = s.get("mod") or {}
        if not isinstance(s.get("nazwa"), str) or set(m) - {"procent", "lup"}:
            raise BladDanych("pet %s: skill bez nazwy albo nieznane pole modyfikatora %s" % (p["id"], sorted(m)))
        if s.get("zywiol") is not None and s["zywiol"] not in U["zywioly"]:
            raise BladDanych("pet %s: nieznany żywioł %s" % (p["id"], s["zywiol"]))
        wartosci = []
        for a, v in (m.get("procent") or {}).items():
            if a not in U["statystyki"] or not 0 < v <= 1:
                raise BladDanych("pet %s: zła premia %s = %s" % (p["id"], a, v))
            wartosci.append(v)
        for k, v in (m.get("lup") or {}).items():
            if k not in ("zloto", "doswiadczenie") or not 0 < v <= 0.5:
                raise BladDanych("pet %s: zła premia łupu %s = %s" % (p["id"], k, v))
            wartosci.append(v)
        if not wartosci and not s.get("zywiol"):
            raise BladDanych("pet %s: skill nic nie daje" % p["id"])
        if p["rzadkosc"] in MALE_RZADKOSCI and (s.get("zywiol") or max(wartosci) > MALA_PREMIA_MAKS + 1e-9):
            raise BladDanych("pet %s (%s): zwykły pet ma tylko małą premię (≤ %d%%, bez żywiołu) — D-101"
                             % (p["id"], p["rzadkosc"], round(100 * MALA_PREMIA_MAKS)))


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


def polozenie_jajka(j):
    """Stanowisko jajka w układzie świata Studio — miejsce „jajko” i punkt E z mapy biomu (tylko odczyt)."""
    S = j["stanowisko"]
    z = _znaczniki(S["znaczniki"])
    m = next((x for x in z["miejsca"] if x["id"] == S["miejsce"]), None)
    e = next((x for x in z["punkty_e"] if x["grupa"] == S["grupa_e"]), None)
    if not m or not e:
        raise BladDanych("jajko %s: brak miejsca %r albo punktu E %r w %s" % (j["id"], S["miejsce"], S["grupa_e"],
                                                                         S["znaczniki"]))
    return {"gniazdo": [_r(v) for v in m["punkt_swiat"]], "obrot": S["obrot"], "e": [_r(v) for v in e["punkt_swiat"]]}


def polozenia(U):
    """Zagroda (bazar) w układzie świata Studio — z mapy, tylko odczyt (stanowiska jajek: polozenie_jajka)."""
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
        "zagroda_e": [_r(v) for v in e0],
        "zagroda_kier": [_r(v, 4) for v in kz],
        "zagroda_tablica": [_r(v) for v in tablica],
        "miejsca_petow": [[_r(v) for v in x["swiat"]] for x in zg["miejsca_petow"]],
        "zagroda_podpowiedz": [_r(v) for v in pz["podpowiedz"]],
    }


def szanse_i_cena(U):
    """Szanse jajek z kalkulatora (tools/walka/progresja.py) na pety z puli w kolejności rzadkości; każdy pet w puli
    dokładnie jednego jajka; cena kalkulatora sprawdzana tam, gdzie jajko ją ma (dziś tylko las)."""
    szanse = list(progresja.ZALOZENIA["szanse_jajka"])
    kalk = progresja.ZALOZENIA["ceny_jajek"][0]
    if abs(sum(szanse) - 1.0) > 1e-9:
        raise BladDanych("szanse jajka nie sumują się do 1: %s" % szanse)
    rz = [r["id"] for r in U["rzadkosci"]]
    pety = {p["id"]: p for p in U["pety"]}
    gdzie = {}
    jajka = []
    for j in U["jajka"]:
        if not re.match(r"^[A-Za-z0-9_]{1,24}$", j["id"]):
            raise BladDanych("jajko %s: id spoza liter, cyfr i „_”" % j["id"])
        if len(j["pula"]) != len(szanse):
            raise BladDanych("jajko %s: %d petów w puli, a kalkulator ma %d szans" % (j["id"], len(j["pula"]), len(szanse)))
        for i, pid in enumerate(j["pula"]):
            if pid not in pety:
                raise BladDanych("jajko %s: nieznany pet %s" % (j["id"], pid))
            if pid in gdzie:
                raise BladDanych("pet %s w dwóch jajkach (%s, %s)" % (pid, gdzie[pid], j["id"]))
            if pety[pid]["rzadkosc"] != rz[i]:
                raise BladDanych("jajko %s: %d. pet puli (%s) powinien być %s" % (j["id"], i + 1, pid, rz[i]))
            gdzie[pid] = j["id"]
        c = j["cena"]
        if c.get("kalkulator") is not None and c["kalkulator"] != kalk:
            raise BladDanych("jajko %s: cena kalkulatora %s ≠ progresja.py %s" % (j["id"], c["kalkulator"], kalk))
        # tryb ceny: "stala" (domyślny — decyzja Karola 17.11), "rosnaca" i "kalkulator" jako przełącznik
        potrzebne = {"stala": ("stala",), "rosnaca": ("start", "krok", "maks"), "kalkulator": ("kalkulator",)}
        if c["tryb"] not in potrzebne or any(c.get(k) is None for k in potrzebne[c["tryb"]]):
            raise BladDanych("jajko %s: tryb ceny %r bez wartości" % (j["id"], c["tryb"]))
        if any(not isinstance(c.get(k), int) or c[k] < 1 for k in ("stala", "start", "krok", "maks")):
            raise BladDanych("jajko %s: ceny (stala, start, krok, maks) muszą być liczbami całkowitymi ≥ 1" % j["id"])
        cena = {k: v for k, v in c.items() if k in ("tryb", "stala", "start", "krok", "maks", "kalkulator")
                and v is not None}
        jajka.append({"id": j["id"], "nazwa": j["nazwa"], "kraina": j["kraina"], "tytul": j["tytul"], "pula": j["pula"],
                      "cena": cena, "folder": j["folder"], "punkt_e": j["punkt_e"], "atrybuty": j["atrybuty"],
                      "kolor_swiatla": j["kolor_swiatla"], "opis_miejsca": j["opis_miejsca"],
                      "skala_jajka": j["stanowisko"]["skala_jajka"], "jajko_na_mchu": j["stanowisko"]["jajko_na_mchu"],
                      "rig": j["model"]["rig"], "polozenie": polozenie_jajka(j),
                      "szanse": [{"pet": p, "szansa": s} for p, s in zip(j["pula"], szanse)]})
    bez = sorted(set(pety) - set(gdzie))
    if bez:
        raise BladDanych("pety bez jajka: %s" % ", ".join(bez))
    for nazwa in ("folder", "punkt_e"):
        if len({j[nazwa] for j in jajka}) != len(jajka):
            raise BladDanych("jajka muszą mieć różne „%s”" % nazwa)
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


def inkubator_jajka(U, j):
    """Z modelu inkubatora jajka (tylko odczyt): stałe bryły kości z „kosci_stale” (tablica, gniazdo, latarnia) w układzie
    stanowiska (środek gniazda na ziemi, przód −Z) i wysokość spodu jajka (staw kości „Jajko”)."""
    M = j["model"]
    d = rig_modelu(_postac_z_modulu(M["modul"], M["inkubator"]), 1.0)
    nr = {k[0]: i + 1 for i, k in enumerate(d["kosci"])}
    brak = [k for k in M["kosci_stale"] + ["Jajko"] if k not in nr]
    if brak:
        raise BladDanych("inkubator %s: brak kości %s" % (M["inkubator"], ", ".join(brak)))
    stale = {nr[k] for k in M["kosci_stale"]}
    # paski szans z modelu są tylko w podglądzie Blendera — w grze rysuje je SurfaceGui (z liczbami i nazwami)
    czesci = [c for c in d["czesci"] if c[0] in stale and not c[2].startswith(("Pasek szansy", "Znak peta"))]
    papier = U["modele"]["papier"]
    if U["modele"]["tablica_kosc"] in M["kosci_stale"] and not any(c[2] == papier for c in czesci):
        raise BladDanych("tablica inkubatora %s bez bryły %r (na nią idzie SurfaceGui)" % (M["inkubator"], papier))
    y = next(k[3] for k in d["kosci"] if k[0] == "Jajko")
    # wiersz: nazwa kości, kształt, nazwa bryły, poz xyz, obrót xyz (rad), rozmiar xyz, kolor, materiał, siatka
    return {"czesci": [[d["kosci"][c[0] - 1][0]] + c[1:] for c in czesci], "materialy": d["materialy"]}, _r(y)


def rigi(U):
    w = {}
    for p in U["pety"]:
        w[p["id"]] = rig_modelu(_postac_z_modulu(p["id"], p["id"]), p.get("skala", 1.0))
    for j in U["jajka"]:
        M = j["model"]
        w[M["jajko"]] = rig_modelu(_postac_z_modulu(M["modul"], M["jajko"]), 1.0)
    return w


def nazwa_rigu(model_id, U=None):
    """Moduł rigu: Rig_<id> (pet) albo nazwa z „model.rig” jajka."""
    for j in (U or ustawienia())["jajka"]:
        if j["model"]["jajko"] == model_id:
            return j["model"]["rig"]
    return "Rig_" + model_id


# ------------------------------------------------------------------------------------------------ dane
def stawki_zagrody(U, jajko_peta):
    """Zagroda petów (25.11.2026, propozycja — LICZBY ROBOCZE): Rybki na sekundę każdego peta stojącego w zagrodzie =
    stawka rzadkości (zagroda.stawki_s) × mnożnik jajka biomu (zagroda.mnozniki_jajek; las 1, Bagno 2,5, Dżungla 4,5 —
    jak ceny jajek 300 / 750 / 1350); pole `rybki_s` w pecie w ustawieniach nadpisuje wzór. Sprawdza też poziomy zagrody
    (miejsca rosną, pierwszy poziom za darmo, ceny całkowite)."""
    Z = U["zagroda"]
    poz = Z["poziomy"]
    if not poz or poz[0]["cena"] != 0:
        raise BladDanych("zagroda.poziomy: pierwszy poziom musi być za darmo")
    for a, b in zip(poz, poz[1:]):
        if not (isinstance(b["miejsc"], int) and b["miejsc"] > a["miejsc"] and isinstance(b["cena"], int) and b["cena"] > 0):
            raise BladDanych("zagroda.poziomy: miejsca muszą rosnąć, ceny być całkowite > 0 (%s → %s)" % (a, b))
    if not 1 <= Z["tik_s"] <= Z["tik_maks_s"] <= 60:
        raise BladDanych("zagroda: 1 <= tik_s <= tik_maks_s <= 60")
    w = {}
    for p in U["pety"]:
        if "rybki_s" in p:
            v = p["rybki_s"]
        else:
            if p["rzadkosc"] not in Z["stawki_s"] or jajko_peta[p["id"]] not in Z["mnozniki_jajek"]:
                raise BladDanych("pet %s: brak stawki rzadkości albo mnożnika jajka w zagroda" % p["id"])
            v = Z["stawki_s"][p["rzadkosc"]] * Z["mnozniki_jajek"][jajko_peta[p["id"]]]
        v = round(float(v), 4)
        if not 0 <= v <= 10:
            raise BladDanych("pet %s: Rybki na sekundę %s poza 0..10" % (p["id"], v))
        w[p["id"]] = v
    return w


def podstawa():
    U = ustawienia()
    rz = {r["id"]: r for r in U["rzadkosci"]}
    for p in U["pety"]:
        if p["rzadkosc"] not in rz:
            raise BladDanych("pet %s: nieznana rzadkość %s" % (p["id"], p["rzadkosc"]))
        if not re.match(r"^[A-Za-z0-9_]{1,24}$", p["id"]):
            raise BladDanych("pet %s: id spoza liter, cyfr i „_”" % p["id"])
    sprawdz_skille(U)
    LC = U["licznik_ceny"]
    if LC["tryb"] not in TRYBY_LICZNIKA:
        raise BladDanych("licznik_ceny.tryb %r spoza %s" % (LC["tryb"], TRYBY_LICZNIKA))
    jajka = szanse_i_cena(U)
    for j, ju in zip(jajka, U["jajka"]):
        j["stale"], j["y_jajka"] = inkubator_jajka(U, ju)
    jajko_peta = {pid: j["id"] for j in jajka for pid in j["pula"]}
    stawki = stawki_zagrody(U, jajko_peta)
    D = {
        "wersja": 2,
        "kontener": U["kontener"],
        "prefiks": U["prefiks"],
        "rzadkosci": U["rzadkosci"],
        "pety": [dict(p, jajko=jajko_peta[p["id"]], rybki_s=stawki[p["id"]]) for p in U["pety"]],
        "jajka": jajka,
        "licznik_ceny": {"tryb": LC["tryb"]},
        "zywioly": {k: {kk: z[kk] for kk in ("nazwa", "opis", "pasywki", "zaklecie") if kk in z}
                    for k, z in U["zywioly"].items()},
        "statystyki": U["statystyki"],
        "kolejnosc_statystyk": KOLEJNOSC_STATYSTYK,
        "modele": U["modele"],
        "rigi": {p["id"]: nazwa_rigu(p["id"], U) for p in U["pety"]},
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
        w["rigi/%s.luau" % nazwa_rigu(mid, U)] = luau_rigu(R)
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
