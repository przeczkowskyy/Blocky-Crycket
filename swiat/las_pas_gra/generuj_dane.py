#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dane gry lasu-pasa z planu (i mapy, gdy jest) — dwa moduły Luau dla kontenera Workspace/LasPasGra. Bez Studio.

    python -B swiat/las_pas_gra/generuj_dane.py               # zapisuje oba moduły i drukuje tabelę stref
    python -B swiat/las_pas_gra/generuj_dane.py --sprawdz     # tylko sprawdza, czy pliki są aktualne (kod 1, gdy nie)
    python -B swiat/las_pas_gra/generuj_dane.py --wyjscie DIR # zapisuje do innego folderu (testy determinizmu)
    python -B swiat/las_pas_gra/generuj_dane.py --bez-mapy    # udaje, że swiat/las_pas/ nie istnieje (tylko plan; do testów)

Wyjście:
  zrodla/DanePotworowPasa.luau — strefy potworów w PRZEGRODACH pasa w formacie modułu DanePotworow z swiat/las_potwory
      (PROJEKT.md tam, rozdz. 2.4). W Studio ten plik staje się Workspace/LasPasGra/Moduly/DanePotworow, więc
      istniejące SerwerPotworow i KlientPotworow działają na nim BEZ ZMIAN w logice ruchu (jeden kod potworów).
  zrodla/DanePasa.luau — liczby świata dla skryptów pasa (SerwerPasa, KlientPasa, MglaPasa): przybycie, Kamień
      Powrotu, brama do Bagna, za bramą, mgła, przelot kamery (punkty w świecie), wczytywanie mapy przed przelotem.

Wejścia (tylko odczyt): swiat/biom_las/pas/plan_pasa.json (zawsze), swiat/las_pas/znaczniki.json i czesci.json (gdy są;
warstwa zrodlo_mapy.py), tools/walka/dane_walki.json (gatunki silnika), swiat/test_walki2/aktorzy.py (aktorzy prototypu).
Pliki są deterministyczne: współrzędne 0,01, długości 0,001, UTF-8 bez BOM, LF, bez daty i bez ścieżek lokalnych.

Generator PRZERYWA (kod 2), gdy: plan i mapa się różnią; potwór nie ma gatunku w silniku albo aktora w prototypie;
poziom poza 1–10; strefa nie mieści swoich grup; dom jest bliżej lub dalej od węzła niż zasady.dom_od_wezlow; pole
strefy wychodzi poza jej przegrodę albo kojec; teksty zasad i przelotu nie zawierają liczb, które przepisujemy.

Drugi biom (17.11.2026): ten sam generator robi dane Bagna — swiat/bagno_pas_gra/generuj_dane.py woła wszystko()
i main() z własną konfiguracją (KONFIG niżej opisuje las-pas; pola: mapa, gatunki, poziomy, teksty, mgła, nazwy
dla skryptów Luau w polu „biom”). Dla lasu konfiguracja jest domyślna, więc wynik jest ten sam co wcześniej.

Odczytania planu (najprostsze; opisane też w README):
  • „podbiom” strefy = id przegrody (jak w planie); „pod” = kojec / polanka; pole strefy w świecie jako {x1, x2, z1, z2};
  • zasiegGraczy (promień liczenia graczy do skracania odrodzenia) = pół przekątnej pola strefy + 4 st — stary las miał
    r + 50, ale tu kojce stoją co 64 st i r + 50 liczyłoby graczy z sąsiedniego kojca;
  • Leśny Troll ma odrodzenie stałe 150 s (pole odrodzenieStale = true; serwer potworów traktuje je jak u Strażnika),
    ale dom i blokadę domu 12 jak zwykła strefa; Strażnik jak w starym lesie: strefa „straznik” z jednym punktem;
  • Strażnik stoi na posadzce kręgu (y ze znaczników, gdy są), twarzą do wejścia: yaw = Logika.yaw(−1, 0) = π/2.
"""
import hashlib
import importlib.util
import json
import math
import os
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if TU not in sys.path:
    sys.path.insert(0, TU)
import zrodlo_mapy  # noqa: E402

PAKIET_POTWOROW = os.path.join(REPO, "swiat", "las_potwory")
PLIK_WALKI = os.path.join(REPO, "tools", "walka", "dane_walki.json")
PLIK_AKTOROW = os.path.join(REPO, "swiat", "test_walki2", "aktorzy.py")
CEL_POTWOROW = os.path.join(TU, "zrodla", "DanePotworowPasa.luau")
CEL_PASA = os.path.join(TU, "zrodla", "DanePasa.luau")


def _modul(nazwa, sciezka):
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# serializacja Luau i matematyka ruchu — te same funkcje co generator starego lasu (jeden format danych)
GEN_LASU = _modul("generuj_dane_las_potwory", os.path.join(PAKIET_POTWOROW, "generuj_dane.py"))
Lg = GEN_LASU.logika
k2, k3 = GEN_LASU.k2, GEN_LASU.k3

GATUNKI = {
    "Leśny Slime": "lesny_slime",
    "Muchomornik": "muchomornik",
    "Cierniowy Wilk": "cierniowy_wilk",
    "Leśny Troll": "lesny_troll",
    "Strażnik Gaju": "straznik_lasu",
}
PRZEDPOLE = 6                  # = Stale.PRZEDPOLE (studs od węzła w stronę domu)
ODSTEP_W_GRUPIE_ZAPAS = 5      # odstepWGrupie = max(szer, dl) + 5 (jak w starym lesie)
ZASIEG_ZAPAS = 4               # zasiegGraczy = pół przekątnej pola + 4
STRAZNIK_R_ZAPAS = 0           # promień strefy Strażnika = promień kręgu areny
PUNKTY_STRUMIENIA_U = [200, 450, 700, 874]   # plan, przelot_kamery.streaming (tekst sprawdzany niżej)
WYS_POSTACI = 3.2              # HumanoidRootPart nad gruntem po teleporcie (jak swiat/biom_las/teleport.py)
MIASTECZKO_SRODEK = [0.3, 0, -698.7]   # środek układu Krzywego Miasteczka (swiat/biom_las/teleport.py)

# mgła: te same wartości co MglaLasu w starym lesie (zgoda Karola z 15.11.2026), prostokąt pasa zamiast kwadratu
MGLA_CEL = {"Density": 0.36, "Offset": 0.15, "Haze": 1.4, "Glare": 0, "Color": "D6E4DA", "Decay": "8FAF9A"}
MGLA_POL_Z = 60                # plan rozdz. 7: |Z + 700| ≤ 60 (pas z kulisami)
MGLA_PAS = 120                 # pas łagodnego przejścia na zewnątrz prostokąta
MGLA_TEMPO = 0.8               # wagi na sekundę (jak stary las: pełne przejście ok. 1,25 s)
MGLA_W_PRZELOCIE = 0.5         # w czasie przelotu mgła rzadsza (plan rozdz. 7: „na czas przelotu można ją rozrzedzić”)

# przelot: fazy serwera (logika_pasa.krok_przelotu) i klienta
PRZELOT_STALE = {"uspokojenie": 0.5, "ladowanie": 4.0, "zapas": 6.0, "strumienCo": 1.0, "wyprzedzenie": 2.5,
                 "ponowPoOdmowie": 5.0, "rozjasnienie": 0.35}

BRAMA_TOLERANCJA = 1.5         # HumanoidRootPart dalej niż 1,5 za linią bramy = „za bramą”
BRAMA_GLEBOKOSC = 200          # do tylu studów za bramą serwer pilnuje (dalej to już inny biom)
PRZED_BRAMA_U = 10             # cofnięcie: 10 st przed bramą, twarzą do bramy
ZA_BRAMA_U = 12                # uprawniony ratowany za bramą: 12 st za nią
RATUNEK_Y = -30                # niżej = spadł z mapy


class Blad(Exception):
    pass


# --------------------------------------------------------------------------------------------- wczytanie
def wczytaj(bez_mapy=False, k=None):
    k = k or KONFIG
    try:
        m = zrodlo_mapy.wczytaj(bez_mapy=bez_mapy, konf=k["mapa"])
    except zrodlo_mapy.Blad as e:
        raise Blad(str(e))
    with open(PLIK_WALKI, encoding="utf-8") as f:
        walka = json.load(f)
    aktorzy = ""
    for plik in [PLIK_AKTOROW] + list(k.get("pliki_aktorow") or []):
        with open(plik, encoding="utf-8") as f:
            aktorzy += f.read()
    # drugi biom dokłada własnych przeciwników (dane walki biomu, nie tools/walka/dane_walki.json)
    m["przeciwnicy"] = [p["id"] for p in walka["przeciwnicy"]] + list(k.get("przeciwnicy_dodatkowi") or [])
    m["aktorzy"] = sorted(set(re.findall(r'"klucz":\s*"(\w+)"', aktorzy)))
    return m


def skrot(m):
    tekst = json.dumps([zrodlo_mapy.wejscie_dla_skrotu(m), m["przeciwnicy"], m["aktorzy"]], sort_keys=True,
                       ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha1(tekst.encode("utf-8")).hexdigest()[:12]


def sw(m, u, y, v):
    return [k2(m["X0"] + u), k2(y), k2(m["Z0"] + v)]


# --------------------------------------------------------------------------------------------- potwory
def gatunki(plan, k=None):
    k = k or KONFIG
    rozm = plan["rozmiary"]
    pred = plan["zasady"]["predkosc"]
    wynik = {}
    for nazwa, gid in k["gatunki"].items():
        r = rozm.get(nazwa)
        if not r:
            raise Blad("brak rozmiarów potwora „%s” w plan_pasa.json" % nazwa)
        szer = r.get("szer", r.get("dl"))
        dl = r.get("dl", r.get("szer"))
        wymiar = max(szer, dl)
        stoi = gid == k["straznik_gatunek"]
        if not stoi and nazwa not in pred:
            raise Blad("brak prędkości potwora „%s” w zasady.predkosc" % nazwa)
        wynik[gid] = {"nazwa": nazwa, "predkosc": 0 if stoi else pred[nazwa], "promien": k3(wymiar / 2),
                      "wymiary": [szer, r["wys"], dl], "odstepWGrupie": 0 if stoi else k3(wymiar + ODSTEP_W_GRUPIE_ZAPAS)}
    return wynik


def zasady(plan):
    z = plan["zasady"]
    for pole, wzor in (("walke_zaczyna", "promieniu 8"), ("skracanie", "najmniej 10 s"), ("skracanie", "0,15")):
        if wzor not in z.get(pole, ""):
            raise Blad("zasady.%s nie zawiera „%s” — sprawdź, czy liczba się nie zmieniła" % (pole, wzor))
    return {"odstep": z["odstep_min"], "smycz": z["smycz"], "blokadaDomu": z["blokada_domu"],
            "zasiegE": 8, "minOdrodzenia": 10, "skracanie": 0.15}


def _odcinek_strefy(plan, st):
    """(u_od, u_do) kojca / polanki strefy albo całej przegrody."""
    for q in plan["przegrody"]:
        if q["id"] == st["podbiom"]:
            for p in q.get("pod", []):
                if p["id"] == st.get("pod"):
                    return p["u_od"], p["u_do"], q
            return q["u_od"], q["u_do"], q
    raise Blad("strefa %s: nieznana przegroda „%s”" % (st["id"], st["podbiom"]))


def _poziomy_strefy(k, sid, z_planu):
    """Poziomy strefy: z planu albo z konfiguracji biomu (poziomy_stref) — konfiguracja musi znać każdą strefę."""
    if k.get("poziomy_stref") is None:
        return list(z_planu)
    if sid not in k["poziomy_stref"]:
        raise Blad("strefa %s: brak poziomów w konfiguracji biomu (poziomy_stref)" % sid)
    return list(k["poziomy_stref"][sid])


def strefa(m, st, gat, zas, k=None):
    k = k or KONFIG
    plan = m["plan"]
    sid = st["id"]
    if st["potwor"] not in k["gatunki"]:
        raise Blad("strefa %s: potwór „%s” nie ma odpowiednika w silniku" % (sid, st["potwor"]))
    gid = k["gatunki"][st["potwor"]]
    g = gat[gid]
    p1, p2 = _poziomy_strefy(k, sid, st["poziomy"])
    lo, hi = k["poziomy"]
    if not (lo <= p1 <= p2 <= hi):
        raise Blad("strefa %s: poziomy %s poza %d–%d" % (sid, [p1, p2], lo, hi))
    if st.get("wariant"):
        raise Blad("strefa %s: odmiany (wariant) w pasie nie są obsługiwane" % sid)
    y = float(st["y"])
    u_od, u_do, przeg = _odcinek_strefy(plan, st)
    pu1, pu2, pv1, pv2 = st["pole"]
    if pu1 < u_od or pu2 > u_do:
        raise Blad("strefa %s: pole u %s–%s wychodzi poza swój odcinek u %s–%s" % (sid, pu1, pu2, u_od, u_do))
    pts = [sw(m, u, y, v) for u, v in st["trasa"]]
    dl = [k3(d) for d in GEN_LASU.dlugosci(pts, True)]
    L = dl[-1]
    trasa = {"x": [p[0] for p in pts], "y": [p[1] for p in pts], "z": [p[2] for p in pts], "dl": dl, "L": L,
             "zamknieta": True}
    grupa = st.get("grupa") or {}
    watahy = grupa.get("watahy", 0) or 0
    if watahy > 0:
        grupy, miejsc = watahy, math.ceil(st["max"] / watahy)
    else:
        grupy, miejsc = st["max"], 1
    odstep_w = g["odstepWGrupie"]
    potrzeba = grupy * ((miejsc - 1) * odstep_w + zas["odstep"])
    if potrzeba > L + 1e-9:
        raise Blad("strefa %s: %d grup × %d miejsc potrzebuje %.1f st, a pętla ma %.1f" % (sid, grupy, miejsc, potrzeba, L))
    dom_od, dom_do = plan["zasady"]["dom_od_wezlow"]
    domy = []
    for du, dv in st["dom"]["pts"]:
        odl = [math.hypot(du - w[0], dv - w[1]) for w in st["trasa"]]
        k = min(range(len(odl)), key=lambda i: odl[i])
        if odl[k] < dom_od - 1e-9 or odl[k] > dom_do + 1e-9:
            raise Blad("strefa %s: dom (%s; %s) jest %.1f od najbliższego węzła (ma być %s–%s)" % (sid, du, dv, odl[k], dom_od, dom_do))
        if not (pu1 <= du <= pu2 and pv1 <= dv <= pv2):
            raise Blad("strefa %s: dom (%s; %s) poza polem strefy" % (sid, du, dv))
        wx, wy, wz = sw(m, du, y, dv)
        nx, nz = trasa["x"][k], trasa["z"][k]
        ux, uz = wx - nx, wz - nz
        n = math.hypot(ux, uz)
        domy.append({"x": wx, "y": wy, "z": wz, "wejscie": [k2(nx + ux / n * PRZEDPOLE), k2(nz + uz / n * PRZEDPOLE)],
                     "wezel": k + 1, "s": [dl[k]]})
    su, sv = st["srodek"]
    zasieg = math.hypot(max(abs(pu1 - su), abs(pu2 - su)), max(abs(pv1 - sv), abs(pv2 - sv))) + ZASIEG_ZAPAS
    x1, _, z1 = sw(m, pu1, y, pv1)
    x2, _, z2 = sw(m, pu2, y, pv2)
    return {
        "id": sid, "podbiom": st["podbiom"], "gatunek": gid, "wariant": False,
        "poziomy": [p1, p2], "naraz": st["naraz"], "max": st["max"],
        "srodek": sw(m, su, y, sv), "r": st["r"], "zasiegGraczy": k3(round(zasieg, 1)),
        "grupy": grupy, "miejsc": miejsc, "odstepWGrupie": odstep_w, "watahy": watahy > 0,
        "odrodzenieS": st["odrodzenie_s"], "straznik": False,
        "trasa": trasa, "domy": domy,
        "odrodzenieStale": bool(st.get("odrodzenie_stale")),
        # D-096: strefa scalona z kilku kojców — poziomy rozdane po miejscach (SerwerPotworow: poziomNaMiejsce)
        "poziomyPoMiejscach": bool(st.get("scalone_z")) and p2 > p1,
        "pod": st.get("pod") or "", "pole": {"x1": x1, "x2": x2, "z1": z1, "z2": z2},
    }


def strefa_straznika(m, k=None):
    k = k or KONFIG
    s = m["plan"]["straznik"]
    poz = s["poziom"] if k.get("poziom_straznika") is None else k["poziom_straznika"]
    lo, hi = k["poziomy"]
    if not (lo <= poz <= hi):
        raise Blad("strażnik: poziom %s poza %d–%d" % (poz, lo, hi))
    if not s.get("odrodzenie_stale", True):
        raise Blad("strażnik: plan mówi o odrodzeniu ze skracaniem — serwer potworów zna tylko stałe")
    x, y, z = [k2(c) for c in m["straznik"]["poz"]]
    kierunek = Lg.yaw(-1, 0)   # twarzą w −X świata = w stronę wejścia pasa
    if abs(kierunek - s["yaw_swiat"]) > 0.01:
        raise Blad("strażnik: plan podaje yaw %.4f, a twarzą do wejścia jest %.4f" % (s["yaw_swiat"], kierunek))
    r = s["arena"]["r"] + STRAZNIK_R_ZAPAS
    return {
        "id": "straznik", "podbiom": "arena", "gatunek": k["gatunki"][s["potwor"]], "wariant": False,
        "poziomy": [poz, poz], "naraz": 1, "max": 1,
        "srodek": [x, y, z], "r": r, "zasiegGraczy": 0,
        "grupy": 1, "miejsc": 1, "odstepWGrupie": 0, "watahy": False,
        "odrodzenieS": s["odrodzenie_s"], "straznik": True,
        "trasa": {"x": [x], "y": [y], "z": [z], "dl": [0], "L": 0, "zamknieta": True, "yaw": k3(kierunek)},
        "domy": [{"x": x, "y": y, "z": z, "wejscie": [x, z], "wezel": 1, "s": [0]}],
        "odrodzenieStale": True, "pod": "", "pole": {"x1": k2(x - r), "x2": k2(x + r), "z1": k2(z - r), "z2": k2(z + r)},
    }


def dane_potworow(m, k=None):
    k = k or KONFIG
    plan = m["plan"]
    silnik, aktorzy = set(m["przeciwnicy"]), set(m["aktorzy"])
    for gid in k["gatunki"].values():
        if gid not in silnik:
            raise Blad("gatunek %s nie istnieje w danych walki (%s)" % (gid, k["opis_walki"]))
        if gid not in aktorzy:
            raise Blad("gatunek %s nie ma aktora w swiat/test_walki2/aktorzy.py (szablon modelu dla klienta)" % gid)
    gat = gatunki(plan, k)
    zas = zasady(plan)
    strefy = [strefa(m, st, gat, zas, k) for st in plan["strefy"]]
    strefy.append(strefa_straznika(m, k))
    spokoj_pr = []
    for sp in plan["strefy_spokoju"]:
        x1, _, z1 = sw(m, sp["u"][0], 0, sp["v"][0])
        x2, _, z2 = sw(m, sp["u"][1], 0, sp["v"][1])
        spokoj_pr.append({"id": sp["id"], "x1": x1, "x2": x2, "z1": z1, "z2": z2})
    for g in gat.values():
        del g["odstepWGrupie"]
    if m["plyta"]:
        p = m["plyta"]
        plyta = {"sciezka": zrodlo_mapy.GRUPA_PLYTY + "/" + zrodlo_mapy.NAZWA_PLYTY,
                 "pozycja": [k2(c) for c in p["pozycja"]], "rozmiar": [k2(c) for c in p["rozmiar"]]}
    else:
        plyta = False
    return {
        "wersja": 1,
        "skrot": skrot(m),
        "biom": {"nazwa": m["kontener"], "srodek": [k2(m["X0"]), 0, k2(m["Z0"])], "obrotY": 0, "plyta": plyta},
        "zasady": zas,
        "gatunki": gat,
        "strefy": strefy,
        "spokoj": [],
        "serce": [],
        "pominiete": [],
        "spokojProstokaty": spokoj_pr,
        "zrodloMapy": m["zrodlo"],
    }


# --------------------------------------------------------------------------------------------- dane pasa (świat)
def punkty_strumienia(plan, konf):
    """Punkty wczytywania mapy przed przelotem: z planu (krótka mapa D-096: przelot_kamery.streaming_u), inaczej stałe."""
    return list(plan["przelot_kamery"].get("streaming_u") or konf["punkty_strumienia_u"])


def _sprawdz_teksty(plan, konf=None):
    konf = konf or KONFIG
    k = plan["przelot_kamery"]
    tekst = "u = " + ", ".join(str(u) for u in punkty_strumienia(plan, konf))
    if tekst not in k.get("streaming", ""):
        raise Blad("przelot_kamery.streaming nie zawiera „%s” — punkty wczytywania mapy się zmieniły?" % tekst)
    if "zaciemnienie 0,5 s" not in k.get("potem", ""):
        raise Blad("przelot_kamery.potem nie zawiera „zaciemnienie 0,5 s”")
    if abs(plan["straznik"]["ryk"]["dl_s"] - 2.0) > 1e-9 or plan["straznik"]["ryk"]["klip"] != "ryk":
        raise Blad("straznik.ryk: oczekiwano klipu „ryk” 2,0 s")


def dane_pasa(m, skrot_danych, konf=None):
    konf = konf or KONFIG
    plan = m["plan"]
    _sprawdz_teksty(plan, konf)
    X0, Z0 = m["X0"], m["Z0"]
    pas = m["pas"]
    b = m["brama"]
    xb = k2(b["x"])
    sciana = pas["sciana_v"]
    k = plan["przelot_kamery"]
    punkty = [{"t": p["t"], "poz": sw(m, p["poz"][0], p["poz"][2], p["poz"][1]),
               "patrz": sw(m, p["patrz"][0], p["patrz"][2], p["patrz"][1])} for p in k["punkty"]]
    if abs(punkty[-1]["t"] - k["czas_s"]) > 1e-9:
        raise Blad("przelot: czas_s %s ≠ czas ostatniego punktu %s" % (k["czas_s"], punkty[-1]["t"]))
    przyb = m["przybycie"]
    zu1, zu2 = pas["zakres_u"]
    pp = next(p for p in plan["punkty_przybycia"] if p["id"] == "miasteczko")
    stale = dict(PRZELOT_STALE)
    stale.update({"czas": k["czas_s"], "zatrzymanieOd": k["zatrzymanie_od_s"], "rykOd": k["ryk_od_s"],
                  "rykDl": plan["straznik"]["ryk"]["dl_s"], "klip": plan["straznik"]["ryk"]["klip"],
                  "zaciemnienie": 0.5,
                  "punkty": punkty, "strumien": [sw(m, u, 0, 0) for u in punkty_strumienia(plan, konf)]})
    # prostokąt „gracz jest w biomie” (pierwsze wejście → przelot) i prostokąt ratunku: domyślnie zakres części
    # mapy ± 10 / ± 150 st; biom za bramą poprzedniego (Bagno) zaczyna je od własnej bramy wejściowej
    wu1, wu2 = konf["wejscie_u"] if konf.get("wejscie_u") else (zu1 - 10, zu2 + 10)
    ru1, ru2 = konf["ratunek_u"] if konf.get("ratunek_u") else (zu1 - 150, zu2 + 150)
    napis_t, napis_p = konf["napis_bramy"]
    tab_t, tab_p = konf["tabliczka"]
    wynik = {
        "wersja": 1,
        "skrot": skrot_danych,
        "mapa": {"nazwa": m["kontener"], "zrodlo": m["zrodlo"], "X0": k2(X0), "Z0": k2(Z0),
                 "grupaWrot": b["grupa_wrot"], "grupaPalisady": b["grupa_palisady"], "zapowiedz": b["zapowiedz"]},
        # „gracz jest w lesie” (pierwsze wejście → przelot): cały zakres części mapy + 10 st zapasu
        "wejscie": {"x1": k2(X0 + wu1), "x2": k2(X0 + wu2), "z1": k2(Z0 - MGLA_POL_Z), "z2": k2(Z0 + MGLA_POL_Z)},
        "przybycie": {"punkt": [k2(c) for c in przyb["punkt"]], "patrz": [k2(c) for c in przyb["patrz"]],
                      "wysokosc": WYS_POSTACI},
        "przedBrama": {"punkt": sw(m, b["u"] - PRZED_BRAMA_U, 0, 0), "patrz": sw(m, b["u"], 0, 0)},
        "zaBrama": {"punkt": sw(m, b["u"] + ZA_BRAMA_U, 0, 0), "patrz": sw(m, b["u"] + 40, 0, 0)},
        "powrot": {"punkt": [k2(c) for c in m["kamien_powrotu"]], "zasieg": 10},
        # Kamień Powrotu: nowe miasteczko (bazar, uchwyt swiat/miasteczko_bazar_gra), gdy jest jego kontener;
        # inaczej stare miasteczko (punkt LasTeleport albo z planu) — D-075: miasteczko to pierwszy blok pasa
        "miasteczko": {"punkt": [k2(pp["swiat_xz"][0]), 0, k2(pp["swiat_xz"][1])], "patrz": MIASTECZKO_SRODEK,
                       "teleport": "LasTeleport",
                       "bazar": {"kontener": "MiasteczkoBazarGra", "uchwyt": "PrzeniesDoBazaru", "punkt": "start"}},
        "brama": {"x": xb, "z1": k2(Z0 - MGLA_POL_Z), "z2": k2(Z0 + MGLA_POL_Z), "tolerancja": BRAMA_TOLERANCJA,
                  "glebokosc": BRAMA_GLEBOKOSC, "otwarcie": [k2(Z0 + b["otwarcie_v"][0]), k2(Z0 + b["otwarcie_v"][1])]},
        # niewidzialna zapora przez całą szerokość pasa (u klienta uprawnionego bez kolizji); napis nad wrotami
        "zapora": {"srodek": [xb, 20, k2(Z0)], "rozmiar": [1, 40, k2(2 * sciana + 4)]},
        "napisBramy": {"punkt": [k2(xb - 1.6), 6.5, k2(Z0)], "tekst": napis_t, "podpis": napis_p},
        # za bramą (zapas, gdyby mapa nie miała własnej zapowiedzi Bagna): podłoga tuż pod Płytą i ściana na końcu
        "zabezpieczenie": {"podloga": {"srodek": [k2(xb + 35), -0.55, k2(Z0)], "rozmiar": [70, 1, k2(2 * sciana + 4)]},
                           "sciana": {"srodek": [k2(xb + 70), 20, k2(Z0)], "rozmiar": [2, 40, k2(2 * sciana + 4)]}},
        "tabliczka": {"punkt": sw(m, b["u"] + 18, 0, 0), "tekst": tab_t, "podpis": tab_p},
        "ratunek": {"x1": k2(X0 + ru1), "x2": k2(X0 + ru2), "z1": k2(Z0 - 200), "z2": k2(Z0 + 200),
                    "yMin": RATUNEK_Y},
        "mgla": {"x1": k2(X0 + pas["u_od"]), "x2": k2(X0 + pas["u_do"]), "z1": k2(Z0 - MGLA_POL_Z), "z2": k2(Z0 + MGLA_POL_Z),
                 "pas": MGLA_PAS, "tempo": MGLA_TEMPO, "wPrzelocie": MGLA_W_PRZELOCIE, "cel": konf["mgla_cel"]},
        "przelot": stale,
        "straznik": {"poz": [k2(c) for c in m["straznik"]["poz"]], "gatunek": konf["straznik_gatunek"]},
    }
    # nazwy i teksty biomu dla SerwerPasa / KlientPasa / MglaPasa (skrypty mają te same wartości lasu jako zapas)
    wynik["biom"] = konf["biom"]
    return wynik


# --------------------------------------------------------------------------------------------- zapis Luau
NAGLOWEK_POTWOROW = """--[[
\tDanePotworow (LAS-PAS) — WYGENEROWANE przez swiat/las_pas_gra/generuj_dane.py z swiat/biom_las/pas/plan_pasa.json
\t(i swiat/las_pas/znaczniki.json + czesci.json, gdy są) oraz tools/walka/dane_walki.json. NIE EDYTUJ RĘCZNIE: zmień plan
\talbo mapę i uruchom python -B swiat/las_pas_gra/generuj_dane.py (testy i zbuduj.py --sucho pilnują aktualności).

\tFormat jak swiat/las_potwory/zrodla/DanePotworow.luau (PROJEKT.md tam, rozdz. 2.4) — w Studio ten moduł to
\tWorkspace/LasPasGra/Moduly/DanePotworow, a czytają go te same SerwerPotworow i KlientPotworow co w starym lesie.
\tWspółrzędne są już w układzie ŚWIATA (świat = (1100 + u; y; −700 + v), bez obrotu). Pola dodatkowe pasa:
\todrodzenieStale (Leśny Troll: 150 s bez skracania), pod (kojec / polanka), pole (prostokąt strefy w świecie),
\tspokojProstokaty (strefy spokoju), zrodloMapy ("znaczniki" albo "plan").
]]
if not game:GetService("RunService"):IsStudio() then
\treturn {}
end
"""

NAGLOWEK_PASA = """--[[
\tDanePasa — WYGENEROWANE przez swiat/las_pas_gra/generuj_dane.py z planu pasa (i mapy, gdy jest). NIE EDYTUJ RĘCZNIE.
\tLiczby świata dla skryptów pasa (SerwerPasa, KlientPasa, MglaPasa): przybycie, Kamień Powrotu, brama do Bagna i to,
\tco za nią, mgła (prostokąt pasa), przelot kamery (punkty Catmull-Rom w ŚWIECIE, ryk, wczytywanie mapy) i Strażnik.
\tProstokąty to { x1, x2, z1, z2 } w poziomie świata; punkty to { x, y, z }.
]]
if not game:GetService("RunService"):IsStudio() then
\treturn {}
end
"""


# ------------------------------------------------------------------------------------- konfiguracja biomu (las-pas)
# Nazwy w „biom” czytają skrypty Luau pakietu (SerwerPasa, KlientPasa, MglaPasa); drugi biom podaje własne.
BIOM_LASU = {
    "id": "las", "nazwa": "Las",
    "uchwyt": "PrzeniesDoLasu",                      # Sygnaly/<uchwyt> (BindableFunction dla innych skryptów serwera)
    "pamiecPrzelot": "widzialPrzelotLasu", "pamiecStraznik": "pokonalStraznikaLasu",   # klucze PamiecGracza
    "atrybutPrzelot": "WidzialPrzelotLasu", "atrybutStraznik": "PokonalStraznikaLasu",  # atrybuty gracza (serwer)
    "atrybutPunktu": "PunktPrzybyciaLasu", "atrybutPatrz": "PatrzPrzybyciaLasu",       # atrybuty kontenera
    "straznik": "Strażnika Gaju",
    "komunikatBramy": "Brama do Bagna jest zamknięta — pokonaj Strażnika Gaju.",
    "przekieruj": True,                              # brama w miasteczku (LasTeleport) prowadzi tutaj (tylko las)
    "podpisBramy": "Brama do Bagna otwarta — idź za arenę",
    "banerBramy": "BRAMA DO BAGNA OTWARTA!",
    "podpisBanera": "Idź za arenę — dalej Bagno",
    "podpisBaneraWkrotce": "Idź za arenę — dalej Bagno (wkrótce)",
    # następny biom: gdy w Workspace stoi jego mapa (Wygenerowane), serwer w Play usuwa ZaBrama (zapasowa ściana i
    # tabliczka „wkrótce”), a baner mówi „dalej Bagno” — brama prowadzi wtedy prosto do Bagna
    "nastepny": {"mapa": "BagnoPas", "nazwa": "Bagno"},
}

KONFIG = {
    "id": "las",
    "mapa": zrodlo_mapy.LAS,
    "gatunki": GATUNKI,
    "straznik_gatunek": "straznik_lasu",
    "poziomy": (1, 10),
    "poziomy_stref": None,                           # None = poziomy z planu
    "poziom_straznika": None,
    "punkty_strumienia_u": PUNKTY_STRUMIENIA_U,
    "mgla_cel": MGLA_CEL,
    "wejscie_u": None,
    "ratunek_u": None,
    "napis_bramy": ("ZAMKNIĘTE", "Pokonaj Strażnika Gaju"),
    "tabliczka": ("BAGNO — WKRÓTCE", "tu zaczyna się następny biom"),
    "biom": BIOM_LASU,
    "cel_potworow": CEL_POTWOROW, "cel_pasa": CEL_PASA,
    "naglowek_potworow": NAGLOWEK_POTWOROW, "naglowek_pasa": NAGLOWEK_PASA,
    "polecenie": "python -B swiat/las_pas_gra/generuj_dane.py",
    "opis_walki": "tools/walka/dane_walki.json",
    "dodatkowe_pliki": None,
}


def tekst(naglowek, d):
    return naglowek + "\nreturn " + GEN_LASU.luau(d, 0) + "\n"


def wszystko(bez_mapy=False, k=None):
    k = k or KONFIG
    m = wczytaj(bez_mapy=bez_mapy, k=k)
    dp = dane_potworow(m, k)
    dpa = dane_pasa(m, dp["skrot"], k)
    return m, dp, dpa


def tabela(dp):
    wiersze = ["strefa   gatunek          poz.   naraz/max  L       grupy×miejsca  zasięg  odrodzenie   cel G=1/8/20"]
    sumy = [0, 0, 0]
    for st in dp["strefy"]:
        g = dp["gatunki"][st["gatunek"]]
        cele = [1, 1, 1] if st["straznik"] else [Lg.cel(st["naraz"], st["max"], G) for G in (1, 8, 20)]
        sumy = [a + b for a, b in zip(sumy, cele)]
        odr = ("%d s stałe" if st.get("odrodzenieStale") else "%d s") % st["odrodzenieS"]
        wiersze.append("%-8s %-16s %-6s %-10s %-7.1f %-14s %-7s %-12s %s" % (
            st["id"], g["nazwa"], "%d–%d" % tuple(st["poziomy"]), "%d / %d" % (st["naraz"], st["max"]), st["trasa"]["L"],
            "%d × %d" % (st["grupy"], st["miejsc"]), st["zasiegGraczy"], odr, " / ".join(str(c) for c in cele)))
    wiersze.append("razem ze Strażnikiem: %d / %d / %d potworów przy 1 / 8 / 20 graczach" % tuple(sumy))
    return "\n".join(wiersze)


def main(k=None):
    k = k or KONFIG
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    argv = sys.argv[1:]
    try:
        m, dp, dpa = wszystko(bez_mapy="--bez-mapy" in argv, k=k)
    except (Blad, GEN_LASU.Blad) as e:
        print("BŁĄD generatora danych pasa:", e)
        sys.exit(2)
    pliki = {k["cel_potworow"]: tekst(k["naglowek_potworow"], dp), k["cel_pasa"]: tekst(k["naglowek_pasa"], dpa)}
    pliki.update(k["dodatkowe_pliki"](m, dp, dpa) if k.get("dodatkowe_pliki") else {})
    if "--sprawdz" in argv:
        zle = []
        for cel, nowy in pliki.items():
            try:
                with open(cel, encoding="utf-8", newline="") as f:
                    stary = f.read()
            except OSError:
                stary = None
            if stary != nowy:
                zle.append(os.path.basename(cel))
        if zle:
            print("NIEAKTUALNE: %s — uruchom: %s" % (", ".join(zle), k["polecenie"]))
            sys.exit(1)
        print("%s aktualne (skrót %s, mapa: %s)" % (" i ".join(os.path.basename(c) for c in pliki), dp["skrot"], m["zrodlo"]))
        return
    folder = None
    if "--wyjscie" in argv:
        i = argv.index("--wyjscie")
        if i + 1 >= len(argv):
            print("--wyjscie wymaga folderu")
            sys.exit(2)
        folder = os.path.abspath(argv[i + 1])
        os.makedirs(folder, exist_ok=True)
    for cel, nowy in pliki.items():
        sciezka = os.path.join(folder, os.path.basename(cel)) if folder else cel
        os.makedirs(os.path.dirname(sciezka), exist_ok=True)
        with open(sciezka, "w", encoding="utf-8", newline="\n") as f:
            f.write(nowy)
    for u in m["uwagi"]:
        print("uwaga:", u)
    print(tabela(dp))
    print("mapa: %s (kontener Workspace/%s, Płyta %s)" % (m["zrodlo"], m["kontener"],
                                                       "z czesci.json" if m["plyta"] else "nieznana — bez kontroli"))
    print("zapisano %s (skrót %s)" % ("do folderu z --wyjscie" if folder else
                                       " i ".join(os.path.relpath(c, TU).replace(os.sep, "/") for c in pliki),
                                       dp["skrot"]))


if __name__ == "__main__":
    main()
