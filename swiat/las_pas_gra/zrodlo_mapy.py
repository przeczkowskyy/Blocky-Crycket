# -*- coding: utf-8 -*-
"""Cienka warstwa „skąd wziąć mapę pasa” dla swiat/las_pas_gra (bez Studio, bez sieci; pliki tylko czyta).

Źródła, w kolejności:
  1. znaczniki mapy z klocków: swiat/las_pas/znaczniki.json (+ rekord „Płyta” z swiat/las_pas/czesci.json) —
     robi je równolegle inny agent; gdy są, z nich bierzemy nazwę kontenera, punkty E, grupy bramy i Płytę;
  2. sam plan: swiat/biom_las/pas/plan_pasa.json — zawsze (strefy potworów, Strażnik, przelot kamery, zasady).

Gdy są oba, sprawdzamy, czy mówią to samo: węzły i domy każdej strefy, miejsce Strażnika, przybycie, brama do Bagna,
położenie pasa w świecie (X0, Z0, bez obrotu). Rozjazd to błąd (Blad) z czytelnym opisem, a nie cicha zmiana — wtedy
trzeba najpierw uzgodnić plan z mapą.

Wynik `wczytaj()` to jedna struktura w układzie ŚWIATA Studio (świat = (X0 + u; y; Z0 + v), bez obrotu, więc
kierunki się nie odwracają). Używa jej generuj_dane.py.
"""
import json
import math
import os

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
PLIK_PLANU = os.path.join(REPO, "swiat", "biom_las", "pas", "plan_pasa.json")
PLIK_ZNACZNIKOW = os.path.join(REPO, "swiat", "las_pas", "znaczniki.json")
PLIK_CZESCI = os.path.join(REPO, "swiat", "las_pas", "czesci.json")

# zadanie z 16.11 (orkiestrator): mapę z klocków buduje inny agent w kontenerze Workspace/LasPas. Plan pisze jeszcze
# „Workspace/PasLas” — gdy nie ma znaczników, bierzemy nazwę z zadania, nie z planu (opisane w README, ryzyka).
KONTENER_DOMYSLNY = "LasPas"
GRUPA_PLYTY = "Teren/Grunt"
NAZWA_PLYTY = "Płyta"
# grupy bramy i zapowiedzi Bagna, gdy nie ma znaczników (takie same jak w swiat/las_pas/znaczniki.json z 16.11)
GRUPA_WROT = "BramaBagna/Wrota"
GRUPA_PALISADY = "BramaBagna/Palisada"
GRUPA_ZAPOWIEDZI = "ZapowiedzBagna"
TOL = 1e-6

# Konfiguracja mapy biomu (17.11.2026: ten sam kod gry dla drugiego biomu — swiat/bagno_pas_gra podaje własną).
# Domyślnie las-pas, więc dla lasu nic się nie zmienia (te same pliki, te same nazwy, ten sam skrót danych).
LAS = {
    "plik_planu": PLIK_PLANU, "plik_znacznikow": PLIK_ZNACZNIKOW, "plik_czesci": PLIK_CZESCI,
    "kontener": KONTENER_DOMYSLNY, "klucz_bramy": "brama_bagna", "nazwa_bramy": "brama do Bagna",
    "grupa_wrot": GRUPA_WROT, "grupa_palisady": GRUPA_PALISADY, "zapowiedz": GRUPA_ZAPOWIEDZI,
    "opis_mapy": "swiat/las_pas", "opis_planu": "plan_pasa.json",
}


class Blad(Exception):
    pass


def _json(sciezka):
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def swiat(u, y, v, X0, Z0):
    """Układ pasa → świat (bez obrotu)."""
    return [X0 + u, y, Z0 + v]


def _blisko(a, b, tol=1e-3):
    return all(abs(x - y) <= tol for x, y in zip(a, b)) and len(a) == len(b)


def _miejsce(plan, mid):
    for m in plan["miejsca"]:
        if m["id"] == mid:
            return m
    raise Blad("plan nie ma miejsca „%s”" % mid)


def _plyta(czesci, kontener):
    """Rekord „Płyta” z czesci.json mapy (pierwsza część, grupa Workspace/<kontener>/Teren/Grunt) albo Blad."""
    if not czesci.get("czesci"):
        raise Blad("czesci.json mapy nie ma listy „czesci”")
    grupy = czesci["grupy"]
    chce = "Workspace/%s/%s" % (kontener, GRUPA_PLYTY)
    for c in czesci["czesci"][:50]:
        grupa = grupy[c[1]] if 0 <= c[1] < len(grupy) else "?"
        if c[14] == NAZWA_PLYTY and grupa == chce:
            return {"pozycja": [c[2], c[3], c[4]], "rozmiar": [c[8], c[9], c[10]], "obrot_y": math.degrees(c[6]),
                    "rekord": c}
    raise Blad("w czesci.json mapy nie ma części „%s” w grupie %s (wśród pierwszych 50)" % (NAZWA_PLYTY, chce))


def _porownaj(plan, zn, X0, Z0, k=None):
    """Plan i znaczniki mają mówić to samo. Zwraca listę opisów rozjazdu (pusta = zgodne)."""
    roznice = []
    konf = k or LAS
    k = zn["kontener"]
    if abs(k["X0"] - X0) > TOL or abs(k["Z0"] - Z0) > TOL or abs(k.get("obrot_y", 0)) > TOL:
        roznice.append("położenie pasa: znaczniki (%s; %s; obrót %s), plan (%s; %s; 0)" % (k["X0"], k["Z0"], k.get("obrot_y"), X0, Z0))
    zs = {s["id"]: s for s in zn.get("strefy", [])}
    for st in plan["strefy"]:
        z = zs.get(st["id"])
        if z is None:
            roznice.append("strefa %s: brak w znacznikach" % st["id"])
            continue
        wez = [(w[0], w[2]) for w in z["wezly"]]
        if len(wez) != len(st["trasa"]) or any(not _blisko(a, b) for a, b in zip(wez, st["trasa"])):
            roznice.append("strefa %s: węzły w znacznikach różnią się od trasy w planie" % st["id"])
        domy = [(d[0], d[2]) for d in z["domy"]]
        if len(domy) != len(st["dom"]["pts"]) or any(not _blisko(a, b) for a, b in zip(domy, st["dom"]["pts"])):
            roznice.append("strefa %s: domy w znacznikach różnią się od planu" % st["id"])
        for pole in ("potwor", "poziomy", "naraz", "max", "odrodzenie_s"):
            if z.get(pole) != st.get(pole):
                roznice.append("strefa %s: pole %s — znaczniki %r, plan %r" % (st["id"], pole, z.get(pole), st.get(pole)))
    for sid in zs:
        if sid not in {s["id"] for s in plan["strefy"]}:
            roznice.append("strefa %s jest w znacznikach, a nie ma jej w planie" % sid)
    s_plan, s_zn = plan["straznik"], zn.get("straznik", {})
    if list(s_zn.get("miejsce", [])) != list(s_plan["miejsce"]) or s_zn.get("poziom") != s_plan["poziom"]:
        roznice.append("Strażnik: znaczniki %s poz. %s, plan %s poz. %s" % (s_zn.get("miejsce"), s_zn.get("poziom"),
                                                                         s_plan["miejsce"], s_plan["poziom"]))
    pr = _miejsce(plan, "przybycie")
    p_zn = zn.get("przybycie", {}).get("punkt")
    if not p_zn or abs(p_zn[0] - pr["u"]) > TOL or abs(p_zn[2] - pr["v"]) > TOL:
        roznice.append("przybycie: znaczniki %s, plan (%s; %s)" % (p_zn, pr["u"], pr["v"]))
    br = _miejsce(plan, konf["klucz_bramy"])
    b_zn = zn.get(konf["klucz_bramy"], {})
    if abs(b_zn.get("u", -1e9) - br["u"]) > TOL or list(b_zn.get("otwarcie_v", [])) != list(br["otwarcie"]):
        roznice.append("%s: znaczniki u %s otwarcie %s, plan u %s otwarcie %s" % (
            konf["nazwa_bramy"], b_zn.get("u"), b_zn.get("otwarcie_v"), br["u"], br["otwarcie"]))
    return roznice


def wczytaj(plik_planu=None, plik_znacznikow=None, plik_czesci=None, bez_mapy=False, konf=None):
    """Znormalizowana mapa pasa w układzie świata. bez_mapy=True — udajemy, że mapy z klocków nie ma (testy).
    konf — konfiguracja biomu (domyślnie LAS, czyli las-pas)."""
    konf = konf or LAS
    plan = _json(plik_planu or konf["plik_planu"])
    sw = plan["swiat"]
    X0, Z0 = float(sw["X0"]), float(sw["Z0"])
    if abs(sw.get("obrot_y", 0)) > TOL:
        raise Blad("plan: obsługujemy tylko pas bez obrotu (obrot_y = 0), jest %s" % sw.get("obrot_y"))
    plik_znacznikow = plik_znacznikow or konf["plik_znacznikow"]
    plik_czesci = plik_czesci or konf["plik_czesci"]
    zn = None if bez_mapy or not os.path.isfile(plik_znacznikow) else _json(plik_znacznikow)
    czesci = None if bez_mapy or not os.path.isfile(plik_czesci) else _json(plik_czesci)
    uwagi = []

    if zn is not None:
        roznice = _porownaj(plan, zn, X0, Z0, konf)
        if roznice:
            raise Blad("%s i %s/znaczniki.json się różnią:\n  " % (konf["opis_planu"], konf["opis_mapy"])
                       + "\n  ".join(roznice))
        kontener = zn["kontener"]["nazwa"].split("/")[-1]
        zrodlo = "znaczniki"
    else:
        kontener = konf["kontener"]
        zrodlo = "plan"
        uwagi.append("brak %s/znaczniki.json — kontener mapy „%s” (z zadania), punkty z planu"
                     % (konf["opis_mapy"], kontener))
    if plan["swiat"].get("kontener", "").split("/")[-1] != kontener:
        uwagi.append("%s podaje kontener „%s”, mapa ma „%s” — bierzemy nazwę mapy"
                     % (konf["opis_planu"], plan["swiat"].get("kontener"), kontener))

    plyta = None
    if czesci is not None:
        plyta = _plyta(czesci, kontener)
        if abs(plyta["obrot_y"]) > 1:
            raise Blad("Płyta mapy jest obrócona o %.1f° (pas ma być bez obrotu)" % plyta["obrot_y"])
    else:
        uwagi.append("brak %s/czesci.json — serwer potworów sprawdzi tylko, czy mapa jest (bez Płyty)"
                     % konf["opis_mapy"])

    pas = plan["pas"]
    pr = _miejsce(plan, "przybycie")
    przybycie = {"punkt": swiat(pr["u"], pr["y"], pr["v"], X0, Z0), "patrz": swiat(pr["patrz"][0], pr["y"], pr["patrz"][1], X0, Z0)}
    kp = _miejsce(plan, "kamien_powrotu")
    kamien = swiat(kp["u"], kp["y"], kp["v"], X0, Z0)
    if zn is not None:
        for p in zn.get("punkty_e", []):
            if p.get("grupa") == "Punkty/KamienPowrotu":
                kamien = list(p["punkt_swiat"])
    br = _miejsce(plan, konf["klucz_bramy"])
    b_zn = (zn or {}).get(konf["klucz_bramy"], {})
    brama = {
        "u": br["u"], "x": X0 + br["u"], "otwarcie_v": list(br["otwarcie"]),
        "grupa_wrot": b_zn.get("grupa_wrot", "Workspace/%s/%s" % (kontener, konf["grupa_wrot"])).split("/", 2)[-1],
        "grupa_palisady": b_zn.get("grupa_palisady",
                                   "Workspace/%s/%s" % (kontener, konf["grupa_palisady"])).split("/", 2)[-1],
        "zapowiedz": konf["zapowiedz"],
    }
    for klucz in ("grupa_wrot", "grupa_palisady"):
        if brama[klucz].startswith(kontener + "/"):
            brama[klucz] = brama[klucz][len(kontener) + 1:]
    s = plan["straznik"]
    y_str = float(s["y"])
    if zn is not None and zn.get("straznik", {}).get("miejsce_swiat"):
        y_str = float(zn["straznik"]["miejsce_swiat"][1])
    straznik = {"poz": swiat(s["miejsce"][0], y_str, s["miejsce"][1], X0, Z0), "yaw": float(s["yaw_swiat"]),
                "arena": swiat(s["arena"]["srodek"][0], y_str, s["arena"]["srodek"][1], X0, Z0), "arena_r": s["arena"]["r"]}
    zakres_u = list((zn or {}).get("pas", {}).get("zakres_czesci_u", [pas["u_od"] - 10, pas["u_do"] + 26]))
    return {
        "konf": konf,
        "zrodlo": zrodlo, "uwagi": uwagi, "plan": plan, "znaczniki": zn, "kontener": kontener, "X0": X0, "Z0": Z0,
        "pas": {"u_od": pas["u_od"], "u_do": pas["u_do"], "szerokosc": pas["szerokosc"], "kulisy": pas["kulisy"],
                "sciana_v": (zn or {}).get("pas", {}).get("niewidzialna_sciana_v", pas["szerokosc"] / 2 + 2),
                "zakres_u": zakres_u},
        "przybycie": przybycie, "kamien_powrotu": kamien, "brama": brama, "straznik": straznik, "plyta": plyta,
    }


def wejscie_dla_skrotu(m):
    """To, co czytamy z mapy (bez statystyk i opisów, które drugi agent zmienia przy każdej budowie) — do skrótu danych."""
    zn = m["znaczniki"]
    klucz = m.get("konf", LAS)["klucz_bramy"]
    male = None
    if zn is not None:
        male = {"kontener": zn["kontener"], "strefy": [{"id": s["id"], "wezly": s["wezly"], "domy": s["domy"]}
                                                       for s in zn.get("strefy", [])],
                "straznik": zn.get("straznik"), "przybycie": zn.get("przybycie"), klucz: zn.get(klucz),
                "punkty_e": zn.get("punkty_e"), "pas": zn.get("pas")}
    return {"plan": m["plan"], "mapa": male, "plyta": m["plyta"]["rekord"] if m["plyta"] else None,
            "kontener": m["kontener"]}
