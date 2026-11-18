#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola offline Dżungli-pasa (plan, czesci.json, znaczniki.json). Nie dotyka Studio ani sieci.

    python -B swiat/dzungla_pas/sprawdz.py                  # kontrola (kod 1 = błąd)
    python -B swiat/dzungla_pas/sprawdz.py --bez-sucho      # bez próby `tools/studio_buduj.py --sucho`

Sprawdza (wzór: swiat/bagno_pas/sprawdz.py):
 0. układ = Bagno + 940 co do studa: pas, przegrody i pody, przejścia (otwarcia, woda), miejsca, punkty orientacyjne,
    strefy (środki, pętle, domy, pola), Strażnik i arena, strefy spokoju, przelot kamery; zostawiane przez przycinarkę
    odcinki (Bagno + 940) zawierają przybycie, pierwszy kojec każdej przegrody z przejściem przed nim, leże, arenę i bramę;
 1. plan: pętle (pojemność, plac walki r 12 w polu gry), domy 12–20 od węzłów, węzły ≥ 25 od przybycia, jajka i Kamienia,
    przelot kamery (ta sama krzywa co w lesie: w pasie, 3–80 nad gruntem, ≤ 120 st/s, 10–14 s, nie przez punkty
    orientacyjne, kończy na Strażniku, ryk w zatrzymaniu, pokazuje każdą przegrodę), D-069 (w trzech przegrodach każda
    klasa gracza ma swojego przeciwnika), jeden gracz ×1 nie czeka na odrodzenie, wymiary potworów z danych aktorów;
 2. format tools/studio_buduj.py (las_pas.sprawdz.sprawdz_format z kontenerem Dżungli) i jego tryb `--sucho`;
 3. liczby i sufity, granice (u 1876…2846, |v| ≤ 90), skrzynki miasteczka i prototypów, brak nachodzenia na Bagno-pas
    (poza grupą ZapowiedzDzungli, którą trzeba usunąć przed budową);
 4. zasady na częściach (ZasadyDzungli: place walki, Dróżka, otwarcia, pętle, przelot kamery);
 5. grunt bez dziur (płyta Dżungli + płyta Bagna do u 1906), woda bez kolizji, niewidzialne ściany, wrota do Pustyni,
    punkty E, wymagane grupy, domy stref;
 6. znaczniki zgodne z planem, faktury: każda część ma rolę.
"""
import argparse
import json
import math
import os
import subprocess
import sys

import numpy as np

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.biom_las import faktury  # noqa: E402
from swiat.biom_las.pas.sprawdz_plan import MAKS_PREDKOSC_KAMERY, krzywa_kamery, przepustowosc  # noqa: E402
from swiat.dzungla_pas import plan as plan_dzungli  # noqa: E402
from swiat.dzungla_pas.generuj import CEL, FAKTURY_DODATKOWE, LIMIT, NADPISZ_ROLE, ODCINKI_RAPORTU, PRZEZROCZYSTE_MAX, \
    odcinek_raportu  # noqa: E402
from swiat.dzungla_pas.kontekst import D, KONTENER, U_MAX, U_MIN, U_PLYTY, U_SCIANY, U_STYKU, Dzungla, ZasadyDzungli  # noqa: E402
from swiat.dzungla_pas.teren import WODA_NAZWY  # noqa: E402
from swiat.las_pas import sprawdz as sprawdz_lasu  # noqa: E402
from swiat.las_pas.zasady import aabb  # noqa: E402

BAGNO_CZESCI = os.path.join(REPO, "swiat", "bagno_pas", "czesci.json")
BAGNO_PLAN = os.path.join(REPO, "swiat", "bagno_pas", "plan_bagna.json")
DANE_AKTOROW = os.path.join(REPO, "swiat", "test_walki2", "dane")
V_GRANICA = 90.0
# odcinki, które przycinarka (D-096) zostawi z projektu Bagna, przesunięte o +940 (swiat/biomy/wymiary_pasa.json → bagno)
ZOSTAW_BAGNA = [[934, 984], [1004, 1080], [1208, 1292], [1420, 1500], [1628, 1762], [1788, 1856], [1862, 1906]]
WYMAGANE_GRUPY = [
    "Wejscie/TarasPrzybycia", "Punkty/KamienPowrotu", "Punkty/StanowiskoJajka", "Punkty/ChatkaNaDrzewie", "Punkty/WielkiKielich",
    "Punkty/KaskadaGaju", "Punkty/ZapadlaKaplica", "Punkty/PosagiStraznikow", "Punkty/SwiatyniaStuLian", "Przejscia/Strumienie",
    "Przejscia/Mostki", "Przejscia/Kaskady", "Przejscia/BambusowaPrzesieka", "Przejscia/KamienneSchody",
    "Przejscia/BramaPosagow", "Kwietnik/Przegrodki", "Kwietnik/Grzadki", "Arena/Posadzka", "Arena/Krag",
    "BramaPustyni/Palisada", "BramaPustyni/Wrota", "ZapowiedzPustyni", "Kulisy/Niewidzialne", "Sciezka", "Teren/Grunt",
    "Teren/Woda", "Teren/Polanki", "Teren/Posadzka", "Teren/Swiatlo", "Mgla",
]
KLASY_GRACZA = {"Wojownik", "Zwiadowca", "Mag"}

bledy, uwagi = [], []


def blad(t):
    bledy.append(t)


def uwaga(t):
    uwagi.append(t)


def l1(x):
    return ("%.1f" % x).replace(".", ",")


def bez_kolizji(c):
    return len(c) > 15 and c[15] & 1


# =========================================================================== 0. układ = Bagno + 940
def sprawdz_uklad(P):
    """Plan Dżungli = plan Bagna przesunięty o D wzdłuż pasa (wszystkie położenia u; v, rozmiary i liczby bez zmian)."""
    if not os.path.isfile(BAGNO_PLAN):
        uwaga("brak swiat/bagno_pas/plan_bagna.json — nie porównano układu z Bagnem")
        return 0
    with open(BAGNO_PLAN, encoding="utf-8") as f:
        B = json.load(f)
    n = 0

    def rowne(co, a, b):
        nonlocal n
        n += 1
        if abs(float(a) - float(b)) > 1e-6:
            blad("układ ≠ Bagno + %d: %s (Dżungla %s, Bagno + %d = %s)" % (D, co, a, D, b))

    if P["pas"]["u_od"] != B["miejsca"][4]["u"] or B["miejsca"][4]["id"] != "brama_dzungli":
        blad("układ: pas Dżungli nie zaczyna się na bramie do Dżungli Bagna")
    rowne("pas.u_do", P["pas"]["u_do"], B["pas"]["u_do"] + D)
    rowne("pas.szerokosc", P["pas"]["szerokosc"], B["pas"]["szerokosc"])
    for a, b in ((P["przegrody"], B["przegrody"]), (P["przejscia"], B["przejscia"])):
        if len(a) != len(b):
            blad("układ: %d przegród/przejść, w Bagnie %d" % (len(a), len(b)))
            continue
        for x, y in zip(a, b):
            for k in ("u_od", "u_do"):
                rowne("%s.%s" % (x["id"], k), x[k], y[k] + D)
            for i, (p, q) in enumerate(zip(x.get("pod", []), y.get("pod", []))):
                rowne("%s.pod[%d]" % (x["id"], i), p["u_od"], q["u_od"] + D)
                rowne("%s.pod[%d]" % (x["id"], i), p["u_do"], q["u_do"] + D)
            if len(x.get("pod", [])) != len(y.get("pod", [])) or len(x.get("strefy", [])) != len(y.get("strefy", [])):
                blad("układ: %s ma inną liczbę kojców/stref niż %s w Bagnie" % (x["id"], y["id"]))
            for k in ("otwarcie", "woda", "kladka"):
                if k in y:
                    for p, q in zip(x.get(k, []), y[k]):
                        rowne("%s.%s" % (x["id"], k), p, q + (D if k == "woda" else 0))
            for k in ("wys_w_otwarciu", "wys_reszty"):
                if k in y:
                    rowne("%s.%s" % (x["id"], k), x[k], y[k])
    mb, md = {m["id"]: m for m in B["miejsca"]}, {m["id"]: m for m in P["miejsca"]}
    for a, b in (("przybycie", "przybycie"), ("jajko", "jajko"), ("kamien_powrotu", "kamien_powrotu"), ("brama_bagna", "brama_lasu"),
                 ("brama_pustyni", "brama_dzungli"), ("odrodzenie", "odrodzenie")):
        if a == "przybycie":
            pp = {p["id"]: p for p in B["punkty_przybycia"]}["dzungla"]
            rowne("przybycie.u (punkt „dzungla” Bagna)", md[a]["u"], pp["u"])
            continue
        rowne("%s.u" % a, md[a]["u"], mb[b]["u"] + D)
        rowne("%s.v" % a, md[a]["v"], mb[b]["v"])
    rowne("brama_bagna.u (= brama do Dżungli Bagna)", md["brama_bagna"]["u"], mb["brama_dzungli"]["u"])
    for x, y in zip(P["punkty_orientacyjne"], B["punkty_orientacyjne"]):
        rowne("%s.u" % x["id"], x["u"], y["u"] + D)
        rowne("%s.v" % x["id"], x["v"], y["v"])
    if len(P["strefy"]) != len(B["strefy"]):
        blad("układ: %d stref, w Bagnie %d" % (len(P["strefy"]), len(B["strefy"])))
    for x, y in zip(P["strefy"], B["strefy"]):
        rowne("%s.srodek" % x["id"], x["srodek"][0], y["srodek"][0] + D)
        for (a, b), (c, d) in zip(x["trasa"], y["trasa"]):
            rowne("%s.trasa" % x["id"], a, c + D)
            rowne("%s.trasa" % x["id"], b, d)
        for (a, b), (c, d) in zip(x["dom"]["pts"], y["dom"]["pts"]):
            rowne("%s.dom" % x["id"], a, c + D)
            rowne("%s.dom" % x["id"], b, d)
        for i in (0, 1):
            rowne("%s.pole" % x["id"], x["pole"][i], y["pole"][i] + D)
        for k in ("naraz", "max", "odrodzenie_s", "r"):
            rowne("%s.%s" % (x["id"], k), x[k], y[k])
    sd, sb = P["straznik"], B["straznik"]
    rowne("straznik.miejsce", sd["miejsce"][0], sb["miejsce"][0] + D)
    rowne("straznik.arena", sd["arena"]["srodek"][0], sb["arena"]["srodek"][0] + D)
    rowne("straznik.arena.r", sd["arena"]["r"], sb["arena"]["r"])
    for x, y in zip(P["strefy_spokoju"], B["strefy_spokoju"]):
        rowne("%s.u" % x["id"], x["u"][0], y["u"][0] + D)
        rowne("%s.u" % x["id"], x["u"][1], y["u"][1] + D)
    kd, kb = P["przelot_kamery"], B["przelot_kamery"]
    for k in ("czas_s", "ryk_od_s", "zatrzymanie_od_s"):
        rowne("przelot.%s" % k, kd[k], kb[k])
    for x, y in zip(kd["punkty"], kb["punkty"]):
        rowne("przelot t %s" % x["t"], x["t"], y["t"])
        for k in ("poz", "patrz"):
            rowne("przelot t %s %s" % (x["t"], k), x[k][0], y[k][0] + D)
            rowne("przelot t %s %s" % (x["t"], k), x[k][1], y[k][1])
            rowne("przelot t %s %s" % (x["t"], k), x[k][2], y[k][2])
    # odcinki przycinarki (Bagno + 940) zawierają to, co zostaje w krótkiej grze
    zost = [(a + D, b + D) for a, b in ZOSTAW_BAGNA]

    def w(u):
        return any(a <= u <= b for a, b in zost)
    for co, u in (("przybycie", md["przybycie"]["u"]), ("brama do Pustyni", md["brama_pustyni"]["u"]),
                  ("Strażnik", sd["miejsce"][0]), ("środek leża", [s for s in P["strefy"] if s["id"] == "t1"][0]["srodek"][0])):
        if not w(u):
            blad("przycinarka: %s (u %g) poza zostawianymi odcinkami" % (co, u))
    for q in P["przegrody"]:
        if len(q.get("pod", [])) == 3:
            p0 = q["pod"][0]
            t = [x for x in P["przejscia"] if x["u_do"] == q["u_od"]]
            od = t[0]["u_od"] if t else p0["u_od"]
            if not any(a <= od and p0["u_do"] <= b for a, b in zost):
                blad("przycinarka: pierwszy kojec %s z przejściem przed nim (u %g–%g) nie mieści się w jednym odcinku" % (
                    p0["id"], od, p0["u_do"]))
    return n


# =========================================================================== 1. plan
def sprawdz_plan(P):
    pol = P["pas"]["szerokosc"] / 2.0
    m = {x["id"]: x for x in P["miejsca"]}
    zas = P["zasady"]
    for st in P["strefy"]:
        tr = st["trasa"]
        ob = plan_dzungli.obwod(tr + [tr[0]])
        if st["max"] > ob // zas["odstep_min"]:
            blad("strefa %s: max %d > pojemność pętli %d (obwód %s / %d)" % (st["id"], st["max"], ob // 25, l1(ob), zas["odstep_min"]))
        for u, v in tr:
            if abs(v) + zas["plac_walki_r"] > pol + 0.01:
                blad("strefa %s: plac walki węzła (%s; %s) wychodzi poza pole gry" % (st["id"], u, v))
            for k in ("przybycie", "jajko", "kamien_powrotu"):
                if math.hypot(u - m[k]["u"], v - m[k]["v"]) < 25:
                    blad("strefa %s: węzeł (%s; %s) bliżej niż 25 od %s" % (st["id"], u, v, k))
        q = {x["id"]: x for x in P["przegrody"]}[st["podbiom"]]
        if not all(q["u_od"] <= u <= q["u_do"] for u, _ in tr):
            blad("strefa %s: pętla wychodzi poza przegrodę %s" % (st["id"], q["id"]))
        d0, d1 = zas["dom_od_wezlow"]
        for du, dv in st["dom"]["pts"]:
            d = min(math.hypot(du - u, dv - v) for u, v in tr)
            if not d0 - 0.01 <= d <= d1 + 0.01:
                blad("strefa %s: dom (%s; %s) %s od najbliższego węzła (ma być %d–%d)" % (st["id"], du, dv, l1(d), d0, d1))
    # D-069: każda klasa gracza ma w Dżungli przeciwnika swojej klasy, a żadna przegroda nie wymaga jednej klasy
    glowne = [q for q in P["przegrody"] if len([s for s in P["strefy"] if s["podbiom"] == q["id"]]) == 3]
    klasy = {[s for s in P["strefy"] if s["podbiom"] == q["id"]][0]["klasa"] for q in glowne}
    if len(glowne) != 3 or klasy != KLASY_GRACZA:
        blad("D-069: trzy przegrody mają mieć po jednym potworze każdej klasy (Wojownik, Zwiadowca, Mag) — są %s" % sorted(klasy))
    for q in glowne:
        if len({s["potwor"] for s in P["strefy"] if s["podbiom"] == q["id"]}) != 1:
            blad("D-069: przegroda %s ma mieć jeden gatunek w trzech kojcach" % q["id"])
    # poziomy rosną przez przegrody (17 → 23)
    poz = [s["poziomy"] for s in P["strefy"]] + [[P["straznik"]["poziom"]] * 2]
    if any(a[0] > b[0] or a[1] > b[1] for a, b in zip(poz, poz[1:])) or poz[0][0] != 17 or poz[-1][1] != 23:
        blad("poziomy: mają rosnąć od 17 (z1) do 23 (Strażnik) — są %s" % poz)
    # wymiary potworów z danych aktorów (swiat/test_walki2/dane/<model>.json)
    for nazwa, r in P["rozmiary"].items():
        mod = P["potwory_opis"][nazwa]["model"]
        plik = os.path.join(DANE_AKTOROW, mod + ".json")
        if not os.path.isfile(plik):
            uwaga("rozmiary: brak danych aktora swiat/test_walki2/dane/%s.json — nie porównano wymiarów %s" % (mod, nazwa))
            continue
        with open(plik, encoding="utf-8") as f:
            wm = json.load(f)["wymiary"]
        if abs(r["wys"] - wm["wysokosc"]) > 0.35:
            blad("rozmiary: %s wys. %s, dane aktora %s" % (nazwa, r["wys"], wm["wysokosc"]))
        if "dl" in r and abs(r["dl"] - wm["glebokosc"]) > 0.4:
            blad("rozmiary: %s dł. %s, dane aktora %s" % (nazwa, r["dl"], wm["glebokosc"]))
        if "szer" in r and abs(r["szer"] - wm["szerokosc"]) > 0.35:
            blad("rozmiary: %s szer. %s, dane aktora %s" % (nazwa, r["szer"], wm["szerokosc"]))
    # farmienie: jeden gracz oglądający walki ×1 nie czeka w kojcu swojego poziomu (wzór z sprawdz_plan lasu)
    for st in P["strefy"]:
        if st.get("odrodzenie_stale"):
            continue
        for t in (15, 30):
            a, b = przepustowosc(P, st, 1, 1, t, "x1")
            if a < b:
                blad("strefa %s: jeden gracz (×1, walka %d s) czeka na odrodzenie" % (st["id"], t))
    # przelot kamery
    k = P["przelot_kamery"]
    pts = k["punkty"]
    probki = krzywa_kamery(pts)
    zgl = set()
    vmax = 0.0
    for (t0, u0, v0, y0), (t1, u1, v1, y1) in zip(probki, probki[1:]):
        if t1 > t0:
            vmax = max(vmax, math.dist((u0, v0, y0), (u1, v1, y1)) / (t1 - t0))
    for t, u, v, y in probki:
        if (abs(v) > pol or not P["pas"]["u_od"] <= u <= P["pas"]["u_do"]) and "pas" not in zgl:
            blad("przelot t ≈ %s: kamera poza pasem" % l1(t))
            zgl.add("pas")
        if not 3 <= y <= 80 and "wys" not in zgl:
            blad("przelot t ≈ %s: wysokość %s poza 3–80" % (l1(t), l1(y)))
            zgl.add("wys")
        for zn in P["punkty_orientacyjne"]:
            if zn["id"] not in zgl and math.hypot(u - zn["u"], v - zn["v"]) < zn["r"] + 4 and y < zn["wys"] + 4:
                blad("przelot t ≈ %s: kamera wchodzi w %s" % (l1(t), zn["nazwa"]))
                zgl.add(zn["id"])
    if vmax > MAKS_PREDKOSC_KAMERY:
        blad("przelot: kamera leci %s st/s (> %d)" % (l1(vmax), MAKS_PREDKOSC_KAMERY))
    T = pts[-1]["t"]
    if abs(T - k["czas_s"]) > 1e-9 or not 10 <= T <= 14:
        blad("przelot: czas %s s (ma być czas_s i 10–14 s)" % l1(T))
    stop = [x for x in pts if x["t"] >= k["zatrzymanie_od_s"] - 1e-9]
    if len(stop) < 2 or any(x["poz"] != stop[0]["poz"] for x in stop):
        blad("przelot: brak zatrzymania od %s s" % k["zatrzymanie_od_s"])
    s_ = P["straznik"]
    wys = P["rozmiary"][s_["potwor"]]["wys"]
    if math.hypot(pts[-1]["patrz"][0] - s_["miejsce"][0], pts[-1]["patrz"][1] - s_["miejsce"][1]) > 3 or \
            not 0.5 * wys <= pts[-1]["patrz"][2] <= wys:
        blad("przelot kończy się, nie patrząc na Strażnika")
    if k["ryk_od_s"] < k["zatrzymanie_od_s"] or k["ryk_od_s"] + s_["ryk"]["dl_s"] > T + 1e-9 or abs(s_["ryk"]["dl_s"] - 2.0) > 1e-9:
        blad("przelot: ryk 2,0 s nie mieści się w zatrzymaniu")
    for q in P["przegrody"]:
        nad = any(q["u_od"] <= x["poz"][0] <= q["u_do"] or q["u_od"] <= x["patrz"][0] <= q["u_do"] for x in pts)
        przez = any(min(a["poz"][0], b["poz"][0]) <= q["u_od"] and max(a["poz"][0], b["poz"][0]) >= q["u_do"]
                    for a, b in zip(pts, pts[1:]))
        if not (nad or przez):
            blad("przelot nie pokazuje przegrody %s" % q["id"])
    a = s_["arena"]
    if math.hypot(s_["miejsce"][0] - a["srodek"][0], s_["miejsce"][1] - a["srodek"][1]) + 12 > a["r"] + 1:
        blad("plac walki Strażnika wychodzi poza posadzkę areny")
    return T, vmax, len(probki)


def studio_sucho(plik):
    try:
        r = subprocess.run([sys.executable, "-B", os.path.join(REPO, "tools", "studio_buduj.py"), plik, "--sucho"],
                           capture_output=True, timeout=120, cwd=REPO, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    except Exception as e:  # noqa: BLE001
        uwaga("studio_buduj.py --sucho nie ruszył: %s" % e)
        return None
    out = (r.stdout + r.stderr).decode("utf-8", "replace").strip()
    if r.returncode != 0 or ("Kontener: " + KONTENER) not in out:
        blad("studio_buduj.py --sucho: kod %d, wyjście: %s" % (r.returncode, out[-300:]))
    return out


def main():
    ap = argparse.ArgumentParser(description="Kontrola offline Dżungli-pasa")
    ap.add_argument("plik", nargs="?", default=os.path.join(TU, "czesci.json"))
    ap.add_argument("--znaczniki", default=os.path.join(TU, "znaczniki.json"))
    ap.add_argument("--bez-sucho", action="store_true")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    P = plan_dzungli.zbuduj()
    with open(os.path.join(TU, "plan_dzungli.json"), encoding="utf-8") as f:
        if json.load(f) != json.loads(json.dumps(P)):
            blad("plan_dzungli.json nie zgadza się z plan.py — uruchom generuj.py")
    with open(a.plik, encoding="utf-8") as f:
        d = json.load(f)
    K = Dzungla(plan=P)
    Z = ZasadyDzungli(K)
    X0, Z0 = K.X0, K.Z0
    grupy, mats, cz = d["grupy"], d["materialy"], d["czesci"]
    print("DŻUNGLA-PAS — kontrola (%s)" % os.path.relpath(a.plik, REPO).replace(os.sep, "/"))

    # 0–1. układ i plan
    n_uklad = sprawdz_uklad(P)
    T, vmax, n_probek = sprawdz_plan(P)

    # 2. format (funkcja lasu-pasa z kontenerem Dżungli; błędy zbiera jej moduł)
    sprawdz_lasu.KONTENER = KONTENER
    sprawdz_lasu.bledy.clear()
    sprawdz_lasu.sprawdz_format(d)
    bledy.extend(sprawdz_lasu.bledy)
    sucho = None if a.bez_sucho else studio_sucho(a.plik)
    if any(t.startswith(("format", "część")) for t in bledy):
        for t in bledy:
            print("BŁĄD:", t)
        print("WYNIK: %d błędów (format) — dalsza kontrola przerwana" % len(bledy))
        return 1

    # 3. liczby, sufity, granice
    n = len(cz)
    if n > LIMIT:
        blad("części %d > twardy limit %d" % (n, LIMIT))
    elif n > CEL * 1.1:
        uwaga("części %d — więcej niż cel ok. %d" % (n, CEL))
    neon = sum(1 for c in cz if mats[c[12]] == "Neon")
    kule = sum(1 for c in cz if c[0] == 1)
    walce = sum(1 for c in cz if c[0] == 2)
    przezr = sum(1 for c in cz if 0 < c[13] < 0.98)
    niewid = sum(1 for c in cz if c[13] >= 0.98)
    for nazwa, ile, mx in (("Neon", neon, 300), ("kule", kule, 300), ("walce", walce, 3000),
                           ("półprzezroczyste", przezr, PRZEZROCZYSTE_MAX)):
        if ile > mx:
            blad("%s: %d > %d" % (nazwa, ile, mx))
    pudla = [("Krzywe Miasteczko", P["swiat"]["miasteczko"]["zajete"])] + [(o["id"], o["xz"]) for o in P["swiat"]["zajete_inne"]]
    poza = 0
    bb = [aabb(c) for c in cz]
    mn_all = np.min([b[0] for b in bb], axis=0)
    mx_all = np.max([b[1] for b in bb], axis=0)
    for c, (mn, mx) in zip(cz, bb):
        u1, u2, v1, v2 = mn[0] - X0, mx[0] - X0, mn[2] - Z0, mx[2] - Z0
        if u1 < U_MIN - 0.05 or u2 > U_MAX + 0.05 or v1 < -V_GRANICA or v2 > V_GRANICA or mn[1] < -4.0 or mx[1] > 120:
            poza += 1
            if poza <= 8:
                blad("poza pasem: „%s” (%s) u %s…%s, v %s…%s" % (c[14], grupy[c[1]][len(KONTENER) + 1:], l1(u1), l1(u2), l1(v1), l1(v2)))
        for nazwa, (a1, a2, b1, b2) in pudla:
            if mn[0] < a2 and a1 < mx[0] and mn[2] < b2 and b1 < mx[2]:
                blad("„%s” nachodzi na %s" % (c[14], nazwa))
    # Bagno-pas: żadna wyższa niż grunt część Dżungli nie wchodzi w wyższą niż grunt część Bagna (poza ZapowiedzDzungli)
    nachodzi = 0
    plyta_bagna = None
    if os.path.isfile(BAGNO_CZESCI):
        with open(BAGNO_CZESCI, encoding="utf-8") as f:
            B = json.load(f)
        bag = []
        for c in B["czesci"]:
            g = B["grupy"][c[1]]
            if "/ZapowiedzDzungli" in g:
                continue
            mn, mx = aabb(c)
            if c[14] == "Płyta" and g.endswith("/Teren/Grunt"):
                plyta_bagna = (mn, mx)
            if mx[0] < X0 + U_MIN - 1 or mx[1] <= 0.45 or c[13] >= 0.98:
                continue
            bag.append((mn, mx, c[14], g.split("/", 2)[-1]))
        for c, (mn, mx) in zip(cz, bb):
            if mn[0] > X0 + U_STYKU or mx[1] <= 0.45 or c[13] >= 0.98:
                continue
            for bmn, bmx, bn, bg in bag:
                if np.all(mn < bmx - 0.05) and np.all(bmn < mx - 0.05):
                    nachodzi += 1
                    if nachodzi <= 6:
                        blad("„%s” (%s) nachodzi na część Bagna-pasa „%s” (%s)" % (c[14], grupy[c[1]][len(KONTENER) + 1:], bn, bg))
                    break
        if nachodzi > 6:
            blad("… razem %d części nachodzi na Bagno-pas" % nachodzi)
    else:
        uwaga("brak swiat/bagno_pas/czesci.json — nie sprawdzono styku z Bagnem-pasem")

    # 4. zasady na częściach
    licz = {}
    for c in cz:
        for t in Z.naruszenia(c, grupy[c[1]], tylko=("plac", "sciezka", "otwarcie", "petla", "kamera")):
            klucz = t.split(" (")[0] if not t.startswith("plac") else "plac walki"
            licz[klucz] = licz.get(klucz, 0) + 1
            if licz[klucz] <= 6:
                blad("%s: „%s” w %s" % (t, c[14], grupy[c[1]][len(KONTENER) + 1:]))
    for k_, v_ in licz.items():
        if v_ > 6:
            blad("… %s: razem %d części" % (k_, v_))

    # 5. grunt, woda, ściany, brama, punkty E, obecność
    def gr(c):
        return grupy[c[1]][len(KONTENER) + 1:]
    plyty = [(c, b) for c, b in zip(cz, bb) if c[14] == "Płyta" and not bez_kolizji(c)]
    if not plyty:
        blad("brak płyty gruntu z kolizją")
    else:
        mn, mx = plyty[0][1]
        if not (mn[0] - X0 <= U_PLYTY[0] + 0.01 and mx[0] - X0 >= 1904 + D and mn[2] - Z0 <= -40 and mx[2] - Z0 >= 40
                and abs(mx[1]) < 0.01):
            blad("płyta Dżungli nie przykrywa u %g…%g, |v| ≤ 40 albo jej wierzch nie leży na y = 0" % (U_PLYTY[0], 1904 + D))
        if gr(plyty[0][0]) != "Teren/Grunt" or cz.index(plyty[0][0]) != 0:
            blad("Płyta ma być pierwszą częścią, w grupie Teren/Grunt (czyta ją swiat/las_pas_gra/zrodlo_mapy.py)")
    podlogi = [b for c, b in zip(cz, bb) if not bez_kolizji(c) and c[13] < 0.98 and -0.05 <= b[1][1] <= 0.6]
    if plyta_bagna is not None:
        podlogi.append(plyta_bagna)
    GU, GV = np.meshgrid(np.arange(938.0 + D, 1904.0 + D, 2.0) + X0, np.arange(-37.0, 37.1, 2.0) + Z0, indexing="ij")
    pokryte = np.zeros(GU.shape, dtype=bool)
    for mn, mx in podlogi:
        pokryte |= (GU >= mn[0]) & (GU <= mx[0]) & (GV >= mn[2]) & (GV <= mx[2])
    if (~pokryte).sum():
        blad("dziury w gruncie: %d punktów pola gry bez podłogi z kolizją" % int((~pokryte).sum()))
    nierowny = [c for c, b in zip(cz, bb) if not bez_kolizji(c) and "/Teren/" in grupy[c[1]] and abs(b[1][1]) > 0.01]
    if nierowny:
        blad("teren nie jest płaski: %d części gruntu z kolizją ma wierzch ≠ 0" % len(nierowny))
    woda_kol = [c for c in cz if c[14] in WODA_NAZWY and not bez_kolizji(c)]
    if woda_kol:
        blad("woda z kolizją: %d części (%s)" % (len(woda_kol), ", ".join(sorted({c[14] for c in woda_kol}))))
    sciany = [(c, b) for c, b in zip(cz, bb) if c[14] == "Niewidzialna ściana"]
    for zn in (-1, 1):
        if not any(not bez_kolizji(c) and c[13] >= 0.98 and abs(c[4] - Z0 - zn * 38.0) < 1.01 and b[0][0] - X0 <= 964.5 + D
                   and b[1][0] - X0 >= 1903.5 + D and b[1][1] >= 20 for c, b in sciany):
            blad("brak niewidzialnej ściany na v = %d (od u %g do %g)" % (zn * 38, 964 + D, 1904 + D))
    if not any(abs(c[2] - X0 - U_SCIANY) < 1.01 and c[10] >= 76 for c, _ in sciany):
        blad("brak niewidzialnej ściany na końcu zapowiedzi Pustyni (u %g)" % U_SCIANY)
    obecne = {gr(c) for c in cz}
    for g in WYMAGANE_GRUPY:
        if not any(o == g or o.startswith(g + "/") for o in obecne):
            blad("brak grupy %s" % g)
    for st in P["strefy"]:
        if not any(o.startswith("Domy/%s/" % st["id"]) for o in obecne):
            blad("brak domu potworów strefy %s" % st["id"])
    wrota = [(c, b) for c, b in zip(cz, bb) if gr(c).startswith("BramaPustyni/Wrota") and not bez_kolizji(c)]
    if not wrota:
        blad("brama do Pustyni: brak wrót z kolizją")
    else:
        o1, o2 = K.miejsca["brama_pustyni"]["otwarcie"]
        v, wys = o1, 99.0
        for a_, b_, h in sorted((b[0][2] - Z0, b[1][2] - Z0, b[1][1]) for _, b in wrota):
            if a_ <= v + 0.3:
                v = max(v, b_)
                wys = min(wys, h)
        if v < o2 - 0.3 or wys < 7.0:
            blad("wrota do Pustyni nie zamykają otwarcia v %s…%s na wys. ≥ 7" % (o1, o2))
    # mur bramy domyka pas od wrót do niewidzialnych ścian (|v| 8 … 38) na wys. ≥ 7, z kolizją
    ub = K.miejsca["brama_pustyni"]["u"]
    mur = sorted((b[0][2] - Z0, b[1][2] - Z0) for c, b in zip(cz, bb) if gr(c).startswith("BramaPustyni/") and not bez_kolizji(c)
                 and b[0][0] - X0 <= ub + 0.5 and b[1][0] - X0 >= ub - 0.5 and b[1][1] >= 7.0 and b[0][1] <= 0.5)
    for zn in (-1, 1):
        v = 0.0
        for a_, b_ in (mur if zn > 0 else [(-b2, -a2) for a2, b2 in reversed(mur)]):
            if a_ <= v + 0.3:
                v = max(v, b_)
        if v < 38.0:
            blad("brama do Pustyni: mur z kolizją nie domyka pasu po stronie v %s0 (domknięte do |v| %s)" % ("+" if zn > 0 else "−", l1(v)))
    for g in ("Punkty/KamienPowrotu/_Interakcja", "Punkty/StanowiskoJajka/_Interakcja"):
        if g not in obecne:
            blad("brak punktu E %s" % g)

    # 6. znaczniki i faktury
    try:
        with open(a.znaczniki, encoding="utf-8") as f:
            zn = json.load(f)
        if zn.get("kontener", {}).get("nazwa") != KONTENER:
            blad("znaczniki: kontener ≠ %s" % KONTENER)
        for klucz in ("grupy_stale_wczytane", "grupy_niski_detal"):
            gg = (zn.get(klucz) or {}).get("grupy")
            if not gg:
                blad("znaczniki: brak %s.grupy" % klucz)
                continue
            for g in gg:
                if not any(o == g or o.startswith(g + "/") for o in obecne):
                    blad("znaczniki: grupa %s z %s nie istnieje w częściach" % (g, klucz))
        ps = {st["id"]: st for st in P["strefy"]}
        for st in zn.get("strefy", []):
            p_ = ps.get(st["id"])
            if not p_ or len(st["wezly"]) != len(p_["trasa"]) or any(abs(w[0] - q[0]) > 1e-6 or abs(w[2] - q[1]) > 1e-6
                                                                     for w, q in zip(st["wezly"], p_["trasa"])):
                blad("znaczniki: węzły strefy %s różnią się od planu" % st["id"])
            for w, ws in zip(st["wezly"], st["wezly_swiat"]):
                if abs(ws[0] - (X0 + w[0])) > 0.01 or abs(ws[2] - (Z0 + w[2])) > 0.01:
                    blad("znaczniki: zły przelicznik na świat w strefie %s" % st["id"])
                    break
        if len(zn.get("strefy", [])) != len(P["strefy"]):
            blad("znaczniki: %d stref, w planie %d" % (len(zn.get("strefy", [])), len(P["strefy"])))
        for klucz in ("start", "inkubator", "straznik", "brama_pustyni", "przelot_kamery", "punkty_e", "punkty_przybycia", "mgla"):
            if not zn.get(klucz):
                blad("znaczniki: brak „%s”" % klucz)
        if len(zn.get("punkty_e", [])) < 2:
            blad("znaczniki: za mało punktów E")
        if zn.get("brama_pustyni", {}).get("grupa_wrot") != KONTENER + "/BramaPustyni/Wrota":
            blad("znaczniki: brak ścieżki grupy wrót")
        if {"Punkty/KamienPowrotu", "Punkty/StanowiskoJajka"} - {p["grupa"] for p in zn.get("punkty_e", [])}:
            blad("znaczniki: punkty E Kamienia Powrotu i stanowiska jajka")
    except (OSError, ValueError, KeyError) as e:
        blad("znaczniki.json: %s" % e)
    znane = set(faktury.NAZWY) | {z_[0] for z_ in faktury.ZALEZNE} | set(FAKTURY_DODATKOWE) | set(NADPISZ_ROLE)
    bez_roli = sorted({c[14] for c in cz if c[14] not in znane and mats[c[12]] != "Neon"})
    if bez_roli:
        blad("faktury: części bez roli: %s" % ", ".join(bez_roli))

    # wynik
    od = {}
    for c in cz:
        o = odcinek_raportu(c[2] - X0)
        od[o] = od.get(o, 0) + 1
    bez_k = sum(1 for c in cz if bez_kolizji(c))
    t_bieg = plan_dzungli.czasy_biegu(P)[0]
    print("części: %d (cel ok. %d, limit %d) · grup: %d · materiały: %s" % (n, CEL, LIMIT, len(grupy), ", ".join(mats)))
    print("zakres w świecie: X %s…%s, Y %s…%s, Z %s…%s (u %s…%s, v %s…%s)" % (
        l1(mn_all[0]), l1(mx_all[0]), l1(mn_all[1]), l1(mx_all[1]), l1(mn_all[2]), l1(mx_all[2]),
        l1(mn_all[0] - X0), l1(mx_all[0] - X0), l1(mn_all[2] - Z0), l1(mx_all[2] - Z0)))
    print("Neon %d, kule %d, walce %d, półprzezroczyste %d, niewidzialne %d, z kolizją %d%%" % (
        neon, kule, walce, przezr, niewid, round(100.0 * (n - bez_k) / n)))
    print("części na odcinek pasa:")
    for _, _, nazwa in ODCINKI_RAPORTU:
        print("  %-34s %5d" % (nazwa, od.get(nazwa, 0)))
    print("plan: bieg od przybycia do bramy %s s, przelot %s s (najszybciej %s st/s, %d próbek); układ = Bagno + %d (%d porównań)"
          % (l1(t_bieg), l1(T), l1(vmax), n_probek, D, n_uklad))
    if sucho:
        print("studio_buduj.py --sucho: " + sucho.splitlines()[-1])
    print("sprawdzone: układ = Bagno + 940 i odcinki przycinarki, plan (pętle, domy, D-069, poziomy, wymiary z danych aktorów, "
          "farmienie, przelot), format, rozmiary, limity, granice, styk z Bagnem-pasem, place walki r 12 (%d węzłów), Dróżka, "
          "%d otwarć przejść, pętle, przelot kamery na częściach, grunt bez dziur, woda bez kolizji, niewidzialne ściany, "
          "wrota i mur bramy, punkty E, grupy, znaczniki, faktury" % (len(Z.wezly), len(Z.otwarcia)))
    print()
    for t in uwagi:
        print("OSTRZEŻENIE:", t)
    for t in bledy:
        print("BŁĄD:", t)
    print("WYNIK: %d błędów, %d ostrzeżeń" % (len(bledy), len(uwagi)))
    return 1 if bledy else 0


if __name__ == "__main__":
    sys.exit(main())
