#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola liczb planu „Las jako wąski pas” (swiat/biom_las/pas/plan_pasa.json). Nie dotyka Studio ani sieci.

    python -B swiat/biom_las/pas/sprawdz_plan.py            # kontrola + tabele (kod 1 = błąd w planie)
    python -B swiat/biom_las/pas/sprawdz_plan.py --krotko   # tylko błędy, ostrzeżenia i podsumowanie
    python -B swiat/biom_las/pas/sprawdz_plan.py KOPIA.json # sprawdza inny plik (np. kopię z próbną zmianą)

Sprawdza: szerokość pasa w sekundach biegu; przegrody i przejścia leżą jedno za drugim bez nakładania i mieszczą się
w pasie; każda strefa potworów ma pole w swojej przegrodzie, pętla i place walki (r 12) mieszczą się w pasie i w
przegrodzie, domy 12–20 od węzłów, pojemność pętli (zasada odstępu 25 z swiat/las_potwory), poziomy rosną wzdłuż pasa,
węzły różnych stref ≥ 25 od siebie, z dala od stref spokoju i punktów orientacyjnych; miejsca (przybycie, jajko, Kamień
Powrotu, brama) są tam, gdzie mają być; trasa kamery nie wychodzi poza pas, nie wchodzi w punkty orientacyjne, trwa
10–14 s i zatrzymuje się na Strażniku na czas ryku; położenie w świecie nie nachodzi na znane obiekty.

Liczy: czas biegu od przybycia do bramy i między przegrodami, liczbę potworów przy 1 / 8 / 20 graczach (ten sam wzór co
swiat/las_potwory/logika.py → cel), przepustowość farmienia (walki na minutę bez czekania na odrodzenie), budżet czasu
ok. 30 min z udziałem chodzenia i to samo dla kolejnych biomów.
"""
import json
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
PLIK = os.path.join(TU, "plan_pasa.json")

GATUNEK = {"zagroda": "Leśny Slime", "lasek": "Muchomornik", "zarosla": "Cierniowy Wilk", "leze": "Leśny Troll",
           "arena": "Strażnik Gaju"}
PLAC_WALKI_R = 12          # zasada „plaski_grunt” z swiat/biom_las/potwory.json
WYCHODZENIE_ZAPAS_S = 1.0  # potwór z domu: droga do węzła + chwila na wejście na pętlę
ZAJETOSC_ZAPAS_S = 1.0     # Stale.ZAPAS_ZAJETOSCI w swiat/las_potwory
MAKS_PREDKOSC_KAMERY = 120

bledy = []
uwagi = []


def blad(t):
    bledy.append(t)


def uwaga(t):
    uwagi.append(t)


def l1(x):
    """Liczba po polsku z jednym miejscem po przecinku."""
    return ("%.1f" % x).replace(".", ",")


def cel(naraz, maks, gracze):
    """Kopia swiat/las_potwory/logika.py → cel (rozdz. 3.5 PROJEKT.md)."""
    g = max(1, gracze)
    pol = math.ceil(naraz / 2)
    if g <= 8:
        c = pol + (naraz - pol) * (g - 1) / 7
    else:
        c = naraz + (maks - naraz) * min(1, (g - 8) / 12)
    return math.floor(c + 0.5)


def czas_odrodzenia(baza, gracze, stale=False):
    if stale:
        return baza
    return max(10, baza / (1 + 0.15 * (max(1, gracze) - 1)))


def odl(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def obwod(pts):
    n = len(pts)
    return sum(odl(pts[i], pts[(i + 1) % n]) for i in range(n))


def zgodnosc_z_logika():
    """Gdy jest swiat/las_potwory/logika.py, porównaj kopię wzoru `cel` (bez zapisu bajtkodu)."""
    sys.dont_write_bytecode = True
    sciezka = os.path.join(os.path.dirname(os.path.dirname(TU)), "las_potwory")
    if not os.path.isfile(os.path.join(sciezka, "logika.py")):
        return None
    sys.path.insert(0, sciezka)
    try:
        import logika  # noqa: E402
    except Exception:  # noqa: BLE001
        return None
    finally:
        sys.path.pop(0)
    for naraz, mx in ((4, 5), (4, 6), (3, 4), (1, 1), (6, 9)):
        for g in (0, 1, 4, 8, 14, 20, 50):
            if logika.cel(naraz, mx, g) != cel(naraz, mx, g):
                return False
    return True


# ===================================================================================================== kontrole
def sprawdz_pas(p):
    pas, bieg = p["pas"], p["bieg"]["walkspeed"]
    W = pas["szerokosc"]
    s = W / bieg
    if not 4 <= s <= 5:
        blad("szerokość pasa %d st = %s s biegu — ma być 4–5 s" % (W, l1(s)))
    if abs(pas["szerokosc_s"] - s) > 1e-9:
        blad("pas.szerokosc_s = %s, a z liczb wychodzi %s" % (pas["szerokosc_s"], s))
    return W / 2


def sprawdz_odcinki(p, pol):
    pas = p["pas"]
    odc = [("przegroda", q["id"], q["u_od"], q["u_do"]) for q in p["przegrody"]]
    odc += [("przejście", q["id"], q["u_od"], q["u_do"]) for q in p["przejscia"]]
    odc.sort(key=lambda o: o[2])
    if odc[0][2] != 0:
        blad("pierwszy odcinek zaczyna się w u = %s, a las zaczyna się w 0" % odc[0][2])
    if odc[-1][3] != pas["u_do"]:
        blad("ostatni odcinek kończy się w u = %s, a pas w %s" % (odc[-1][3], pas["u_do"]))
    for a, b in zip(odc, odc[1:]):
        if a[3] > b[2]:
            blad("%s %s (do %s) nachodzi na %s %s (od %s)" % (a[0], a[1], a[3], b[0], b[1], b[2]))
        elif a[3] < b[2]:
            blad("dziura w pasie między %s a %s: u %s–%s" % (a[1], b[1], a[3], b[2]))
        if a[0] == b[0]:
            blad("dwa odcinki tego samego rodzaju obok siebie: %s, %s (między przegrodami ma być przejście)" % (a[1], b[1]))
    for o in odc:
        if o[3] <= o[2]:
            blad("%s %s ma długość ≤ 0" % (o[0], o[1]))
        if o[2] < pas["u_od"] or o[3] > pas["u_do"]:
            blad("%s %s wychodzi poza pas" % (o[0], o[1]))
    przeg = {q["id"]: q for q in p["przegrody"]}
    kolej = [q["id"] for q in sorted(p["przegrody"], key=lambda q: q["u_od"])]
    for t in p["przejscia"]:
        a, b = t["miedzy"]
        if a not in przeg or b not in przeg:
            blad("przejście %s łączy nieznane przegrody %s" % (t["id"], t["miedzy"]))
            continue
        if kolej.index(b) != kolej.index(a) + 1:
            blad("przejście %s nie leży między sąsiednimi przegrodami %s → %s" % (t["id"], a, b))
        if przeg[a]["u_do"] != t["u_od"] or przeg[b]["u_od"] != t["u_do"]:
            blad("przejście %s (u %s–%s) nie wypełnia luki między %s a %s" % (t["id"], t["u_od"], t["u_do"], a, b))
        o1, o2 = t["otwarcie"]
        if o1 < -pol or o2 > pol:
            blad("przejście %s: otwarcie %s poza pasem" % (t["id"], t["otwarcie"]))
        if o2 - o1 < 16:
            blad("przejście %s: otwarcie %s st < 16 (gracze w obie strony, troll 12,7)" % (t["id"], o2 - o1))
        if t.get("blokuje"):
            blad("przejście %s blokuje — między przegrodami nic nie ma blokować farmienia" % t["id"])
        if t["wys_w_otwarciu"] > 2:
            blad("przejście %s: w otwarciu coś ma %s wys. — ma być widać następny etap (≤ 2)" % (t["id"], t["wys_w_otwarciu"]))
    for q in p["przegrody"]:
        pod = sorted(q.get("pod", []), key=lambda x: x["u_od"])
        if not pod:
            continue
        if pod[0]["u_od"] != q["u_od"] or pod[-1]["u_do"] != q["u_do"]:
            blad("przegroda %s: kojce/polanki nie wypełniają jej od brzegu do brzegu" % q["id"])
        for a, b in zip(pod, pod[1:]):
            if a["u_do"] != b["u_od"]:
                blad("przegroda %s: %s i %s nie stykają się" % (q["id"], a["id"], b["id"]))
    return przeg


def grupy_i_miejsca(st, rozmiary):
    r = rozmiary[st["potwor"]]
    wymiar = max(r.get("szer", r.get("dl")), r.get("dl", r.get("szer")))
    odstep_w = round(wymiar + 5, 3)
    gr = st.get("grupa") or {}
    watahy = gr.get("watahy", 0) or 0
    if watahy > 0:
        return watahy, math.ceil(st["max"] / watahy), odstep_w
    return st["max"], 1, odstep_w


def sprawdz_strefy(p, przeg, pol):
    z = p["zasady"]
    dom_od, dom_do = z["dom_od_wezlow"]
    spokoj = p["strefy_spokoju"]
    znaki = p["punkty_orientacyjne"]
    PLAC_WALKI_R = z.get("plac_walki_r", globals()["PLAC_WALKI_R"])   # krótki pas (D-096) ma własny promień w planie
    poddzialy = {x["id"]: (q["id"], x) for q in p["przegrody"] for x in q.get("pod", [])}
    wszystkie = []
    for st in p["strefy"]:
        sid = st["id"]
        if st["podbiom"] not in przeg:
            blad("strefa %s: nieznana przegroda %s" % (sid, st["podbiom"]))
            continue
        q = przeg[st["podbiom"]]
        u_od, u_do = q["u_od"], q["u_do"]
        if st.get("pod"):
            if st["pod"] not in poddzialy or poddzialy[st["pod"]][0] != q["id"]:
                blad("strefa %s: kojec/polanka %s nie należy do przegrody %s" % (sid, st["pod"], q["id"]))
            else:
                u_od, u_do = poddzialy[st["pod"]][1]["u_od"], poddzialy[st["pod"]][1]["u_do"]
        pu1, pu2, pv1, pv2 = st["pole"]
        if pu1 < u_od or pu2 > u_do:
            blad("strefa %s: pole u %s–%s wychodzi poza swoje miejsce u %s–%s" % (sid, pu1, pu2, u_od, u_do))
        if pv1 < -pol or pv2 > pol:
            blad("strefa %s: pole v %s–%s wychodzi poza pas ±%s" % (sid, pv1, pv2, pol))
        tr = st["trasa"]
        if len(tr) != st["liczba_wezlow"]:
            blad("strefa %s: liczba_wezlow %s ≠ %d punktów trasy" % (sid, st["liczba_wezlow"], len(tr)))
        for w in tr:
            if not (pu1 <= w[0] <= pu2 and pv1 <= w[1] <= pv2):
                blad("strefa %s: węzeł %s poza polem" % (sid, w))
            if abs(w[1]) + PLAC_WALKI_R > pol + 1e-9:
                blad("strefa %s: plac walki węzła %s wychodzi poza pas" % (sid, w))
            if w[0] - PLAC_WALKI_R < q["u_od"] - 1e-9 or w[0] + PLAC_WALKI_R > q["u_do"] + 1e-9:
                blad("strefa %s: plac walki węzła %s wchodzi w przejście" % (sid, w))
            if odl(w, st["srodek"]) > st["r"] + z["smycz"] + 1e-9:
                blad("strefa %s: węzeł %s dalej niż r + smycz od środka" % (sid, w))
            for sp in spokoj:
                if sp["u"][0] - PLAC_WALKI_R < w[0] < sp["u"][1] + PLAC_WALKI_R and sp["v"][0] <= w[1] <= sp["v"][1]:
                    blad("strefa %s: węzeł %s w strefie spokoju %s" % (sid, w, sp["id"]))
            for zn in znaki:
                if odl(w, (zn["u"], zn["v"])) < PLAC_WALKI_R + zn["r"] - 1e-9:
                    blad("strefa %s: plac walki węzła %s wchodzi w %s" % (sid, w, zn["nazwa"]))
        for d in st["dom"]["pts"]:
            if not (pu1 <= d[0] <= pu2 and pv1 <= d[1] <= pv2) or abs(d[1]) > pol:
                blad("strefa %s: dom %s poza polem albo pasem" % (sid, d))
            dmin = min(odl(d, w) for w in tr)
            if not dom_od - 1e-9 <= dmin <= dom_do + 1e-9:
                blad("strefa %s: dom %s jest %s od najbliższego węzła (ma być %d–%d)" % (sid, d, l1(dmin), dom_od, dom_do))
            for zn in znaki:
                if odl(d, (zn["u"], zn["v"])) < zn["r"] + 2:
                    blad("strefa %s: dom %s wchodzi w %s" % (sid, d, zn["nazwa"]))
        L = obwod(tr)
        if abs(L - st["obwod"]) > 0.3:
            blad("strefa %s: obwod %s, a z węzłów wychodzi %s" % (sid, st["obwod"], l1(L)))
        if st["pojemnosc"] != int(L // z["odstep_min"]):
            blad("strefa %s: pojemnosc %s ≠ floor(obwód / 25) = %d" % (sid, st["pojemnosc"], int(L // z["odstep_min"])))
        grupy, miejsc, odstep_w = grupy_i_miejsca(st, p["rozmiary"])
        potrzeba = grupy * ((miejsc - 1) * odstep_w + z["odstep_min"])
        if potrzeba > L + 1e-9:
            blad("strefa %s: %d grup × %d miejsc potrzebuje %s st pętli, a jest %s" % (sid, grupy, miejsc, l1(potrzeba), l1(L)))
        p1, p2 = st["poziomy"]
        if not 1 <= p1 <= p2 <= 10:
            blad("strefa %s: poziomy %s poza 1–10" % (sid, st["poziomy"]))
        if st["naraz"] > st["max"]:
            blad("strefa %s: naraz > max" % sid)
        if st["potwor"] != GATUNEK.get(q["id"]):
            uwaga("strefa %s: %s w przegrodzie %s (plan zakłada %s)" % (sid, st["potwor"], q["id"], GATUNEK.get(q["id"])))
        wszystkie.append((sid, st, L, grupy, miejsc, odstep_w, potrzeba))
    # odstęp między węzłami różnych stref
    for i, a in enumerate(p["strefy"]):
        for b in p["strefy"][i + 1:]:
            dm = min(odl(x, y) for x in a["trasa"] for y in b["trasa"])
            if dm < z["odstep_min"]:
                blad("węzły stref %s i %s są %s od siebie (< %d)" % (a["id"], b["id"], l1(dm), z["odstep_min"]))
    # poziomy rosną wzdłuż pasa
    po_u = sorted(p["strefy"], key=lambda s: s["srodek"][0])
    for a, b in zip(po_u, po_u[1:]):
        if b["poziomy"][0] < a["poziomy"][0] or b["poziomy"][1] < a["poziomy"][1]:
            blad("poziomy maleją wzdłuż pasa: %s %s → %s %s" % (a["id"], a["poziomy"], b["id"], b["poziomy"]))
    return wszystkie


def sprawdz_straznika(p, przeg, pol):
    s = p["straznik"]
    q = przeg.get("arena")
    if not q:
        blad("brak przegrody „arena”")
        return
    u, v = s["miejsce"]
    if not q["u_od"] <= u <= q["u_do"]:
        blad("Strażnik (u %s) poza areną" % u)
    a = s["arena"]
    if abs(a["srodek"][1]) + a["r"] > pol or a["srodek"][0] - a["r"] < q["u_od"] or a["srodek"][0] + a["r"] > q["u_do"]:
        blad("krąg areny r %s nie mieści się w przegrodzie i w pasie" % a["r"])
    if odl(s["miejsce"], a["srodek"]) > a["r"]:
        blad("Strażnik stoi poza kręgiem areny")
    najw = max(st["poziomy"][1] for st in p["strefy"])
    if s["poziom"] <= najw:
        blad("Strażnik (poziom %s) nie jest ponad najwyższą strefą (%s)" % (s["poziom"], najw))
    # patrzy w stronę wejścia: LookVector = (−sin yaw; −cos yaw) w (X; Z) → ma wyjść (−1; 0)
    lx, lz = -math.sin(s["yaw_swiat"]), -math.cos(s["yaw_swiat"])
    if lx > -0.99:
        blad("Strażnik nie patrzy w stronę wejścia (yaw %s → kierunek (%s; %s))" % (s["yaw_swiat"], l1(lx), l1(lz)))


def sprawdz_miejsca(p, przeg, pol):
    pas = p["pas"]
    m = {x["id"]: x for x in p["miejsca"]}
    for x in p["miejsca"]:
        if abs(x["v"]) > pol or not pas["u_od"] <= x["u"] <= pas["u_do"]:
            blad("miejsce %s poza pasem" % x["id"])
    for wym in ("przybycie", "jajko", "kamien_powrotu", "brama_bagna"):
        if wym not in m:
            blad("brak miejsca %s" % wym)
    if "przybycie" in m:
        pr = m["przybycie"]
        w = przeg["wejscie"]
        if not w["u_od"] <= pr["u"] <= w["u_do"]:
            blad("przybycie poza Polaną Przybycia")
        for k, mx in (("jajko", 30), ("kamien_powrotu", 30)):
            if k in m and odl((pr["u"], pr["v"]), (m[k]["u"], m[k]["v"])) > mx:
                blad("%s dalej niż %d od przybycia" % (k, mx))
    if "brama_bagna" in m:
        b = m["brama_bagna"]
        ost = max(p["przegrody"], key=lambda q: q["u_do"])
        if not ost["u_do"] - 12 <= b["u"] <= ost["u_do"]:
            blad("brama do Bagna nie stoi na końcu ostatniej przegrody")
    for st in p["strefy"]:
        for w in st["trasa"]:
            for k in ("przybycie", "jajko", "kamien_powrotu"):
                if k in m and odl(w, (m[k]["u"], m[k]["v"])) < 25:
                    blad("węzeł %s strefy %s za blisko miejsca %s" % (w, st["id"], k))
    return m


def czasy_biegu(p, m):
    bieg = p["bieg"]["walkspeed"]
    u0 = m["przybycie"]["u"]
    u1 = m["brama_bagna"]["u"]
    wiersze = []
    for q in sorted(p["przegrody"], key=lambda q: q["u_od"]):
        wej = max(q["u_od"], u0)
        wiersze.append((q["nazwa"], q["u_od"], q["u_do"], q["u_do"] - q["u_od"], (wej - u0) / bieg,
                        (q["u_do"] - q["u_od"]) / bieg))
    srodki = sorted([st["srodek"][0] for st in p["strefy"]] + [p["straznik"]["miejsce"][0]])
    miedzy = [(b - a) / bieg for a, b in zip(srodki, srodki[1:])]
    return (u1 - u0) / bieg, wiersze, miedzy


def krzywa_kamery(pts, krok=0.05):
    """Próbki (t, u, v, y) krzywej Catmull-Rom przez punkty przelotu, co `krok` sekund.

    Odcinek o tych samych końcach (zatrzymanie) to postój, nie łuk. Sąsiad za postojem albo za końcem listy = sam koniec
    odcinka, więc kamera dojeżdża do punktu zatrzymania bez przestrzelenia. Tę samą krzywą rysuje rysuj_plan.py i ma
    odtworzyć skrypt przelotu w Studio."""
    P = [x["poz"] for x in pts]
    wynik = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        dt = b["t"] - a["t"]
        if dt <= 0:
            continue
        p1, p2 = P[i], P[i + 1]
        p0 = P[i - 1] if i > 0 and P[i - 1] != p1 else p1
        p3 = P[i + 2] if i + 2 < len(P) and P[i + 2] != p2 else p2
        n = max(2, int(round(dt / krok)))
        for k in range(n + (1 if i == len(pts) - 2 else 0)):
            f = k / n
            if p1 == p2:
                q = list(p1)
            else:
                q = [0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * f + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * f * f
                            + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * f ** 3) for j in range(3)]
            wynik.append((a["t"] + dt * f, q[0], q[1], q[2]))
    return wynik


def sprawdz_kamere(p, pol):
    k = p["przelot_kamery"]
    pas = p["pas"]
    pts = k["punkty"]
    znaki = p["punkty_orientacyjne"]
    for x in pts:
        if not pas["u_od"] <= x["patrz"][0] <= pas["u_do"] or abs(x["patrz"][1]) > pol:
            blad("przelot t = %s: cel spojrzenia %s poza pasem" % (x["t"], x["patrz"]))
    for a, b in zip(pts, pts[1:]):
        if b["t"] - a["t"] <= 0:
            blad("przelot: czasy nie rosną (%s → %s)" % (a["t"], b["t"]))
    probki = krzywa_kamery(pts)
    vmax = 0
    zgloszone = set()
    for (t0, u0, v0, y0), (t1, u, v, y) in zip(probki, probki[1:]):
        if t1 > t0:
            vmax = max(vmax, math.dist((u0, v0, y0), (u, v, y)) / (t1 - t0))
    for t, u, v, y in probki:
        if abs(v) > pol or not pas["u_od"] <= u <= pas["u_do"]:
            if "pas" not in zgloszone:
                blad("przelot t ≈ %s: kamera (%s; %s) poza pasem" % (l1(t), l1(u), l1(v)))
                zgloszone.add("pas")
        if not 3 <= y <= 80 and "wys" not in zgloszone:
            blad("przelot t ≈ %s: wysokość kamery %s poza 3–80" % (l1(t), l1(y)))
            zgloszone.add("wys")
        for zn in znaki:
            if zn["id"] in zgloszone:
                continue
            if odl((u, v), (zn["u"], zn["v"])) < zn["r"] + 4 and y < zn["wys"] + 4:
                blad("przelot t ≈ %s: kamera wchodzi w %s" % (l1(t), zn["nazwa"]))
                zgloszone.add(zn["id"])
            kor = zn.get("korona")
            if kor and odl((u, v), (zn["u"], zn["v"])) < kor["r"] + 4 and kor["od"] - 4 < y < zn["wys"] + 4:
                blad("przelot t ≈ %s: kamera wchodzi w kapelusz/koronę %s" % (l1(t), zn["nazwa"]))
                zgloszone.add(zn["id"])
    if vmax > MAKS_PREDKOSC_KAMERY:
        blad("przelot: kamera leci %s st/s (> %d)" % (l1(vmax), MAKS_PREDKOSC_KAMERY))
    T = pts[-1]["t"]
    if abs(T - k["czas_s"]) > 1e-9:
        blad("przelot: czas_s %s ≠ czas ostatniego punktu %s" % (k["czas_s"], T))
    # D-096 (17.11.2026): krótki pas (plan z polem „wymiary”, swiat/biomy/przycinarka.py) ma lot krótszy w proporcji
    # toru — wtedy 5–14 s; projekt długiego pasa dalej 10–14 s
    dolna = 5 if p.get("wymiary") else 10
    if not dolna <= T <= 14:
        blad("przelot trwa %s s — ma %d–14 s" % (l1(T), dolna))
    s = p["straznik"]
    stop = [x for x in pts if x["t"] >= k["zatrzymanie_od_s"] - 1e-9]
    if len(stop) < 2 or any(x["poz"] != stop[0]["poz"] for x in stop):
        blad("przelot: brak zatrzymania kamery od %s s" % k["zatrzymanie_od_s"])
    if k["ryk_od_s"] < k["zatrzymanie_od_s"] or k["ryk_od_s"] + s["ryk"]["dl_s"] > T + 1e-9:
        blad("przelot: ryk (%s s od %s) nie mieści się w zatrzymaniu" % (s["ryk"]["dl_s"], k["ryk_od_s"]))
    kon = pts[-1]
    wys = p["rozmiary"]["Strażnik Gaju"]["wys"]
    if odl(kon["patrz"][:2], s["miejsce"]) > 3 or not 0.5 * wys <= kon["patrz"][2] <= wys:
        blad("przelot kończy się, nie patrząc na Strażnika (cel %s)" % kon["patrz"])
    # każda przegroda widziana: kamera przelatuje nad nią albo na nią patrzy
    for q in p["przegrody"]:
        nad = any(q["u_od"] <= x["poz"][0] <= q["u_do"] or q["u_od"] <= x["patrz"][0] <= q["u_do"] for x in pts)
        przez = any(min(a["poz"][0], b["poz"][0]) <= q["u_od"] and max(a["poz"][0], b["poz"][0]) >= q["u_do"]
                    for a, b in zip(pts, pts[1:]))
        if not (nad or przez):
            blad("przelot nie pokazuje przegrody %s" % q["id"])
    return T, vmax


def sprawdz_swiat(p):
    sw = p["swiat"]
    pas = p["pas"]
    X0, Z0, h = sw["X0"], sw["Z0"], sw["polowa_szerokosci_z_tlem"]
    kon = max([pas["u_do"]] + [b["u_do"] for b in p["kolejne_biomy"]])
    x1, x2, z1, z2 = X0 + pas["u_od"] - 10, X0 + kon, Z0 - h, Z0 + h
    zajete = [("Krzywe Miasteczko", sw["miasteczko"]["zajete"])] + [(o["id"], o["xz"]) for o in sw["zajete_inne"]]
    for nazwa, (a1, a2, b1, b2) in zajete:
        if x1 < a2 and a1 < x2 and z1 < b2 and b1 < z2:
            blad("pas (x %s…%s, z %s…%s) nachodzi na %s" % (x1, x2, z1, z2, nazwa))
    u = pas["u_do"]
    for b in p["kolejne_biomy"]:
        if b["u_od"] != u:
            blad("biom %s nie zaczyna się tam, gdzie kończy się poprzedni (u %s ≠ %s)" % (b["id"], b["u_od"], u))
        if b["swiat_x"] != [X0 + b["u_od"], X0 + b["u_do"]]:
            blad("biom %s: swiat_x nie zgadza się z u" % b["id"])
        u = b["u_do"]
    return (x1, x2, z1, z2), kon


# ===================================================================================================== liczby
def tabela_potworow(p):
    wiersze = []
    sumy = [0, 0, 0]
    for st in p["strefy"]:
        c = [cel(st["naraz"], st["max"], g) for g in (1, 8, 20)]
        sumy = [a + b for a, b in zip(sumy, c)]
        wiersze.append((st["id"], st["potwor"], st["poziomy"], c, st["odrodzenie_s"], st.get("odrodzenie_stale", False)))
    return wiersze, [s + 1 for s in sumy]  # + Strażnik


def czas_wychodzenia(st, p):
    v = p["zasady"]["predkosc"][st["potwor"]]
    d = min(min(odl(d_, w) for w in st["trasa"]) for d_ in st["dom"]["pts"])
    return d / v + WYCHODZENIE_ZAPAS_S


def przepustowosc(p, st, G, P, t_w, tryb):
    """Ile walk na minutę daje strefa (podaż) i ile chce P graczy (popyt).

    tryb: "x1" — gracz ogląda walkę; "pomija" — gracz pomija pokaz (D-078), potwór zajęty do końca walki jak w
    prototypie; "pomija+zwalnia" — pominięcie zwalnia też potwora (propozycja)."""
    z = p["czas"]["zalozenia"]
    N = cel(st["naraz"], st["max"], G)
    t_odr = czas_odrodzenia(st["odrodzenie_s"], P, st.get("odrodzenie_stale", False))
    t_pokaz = t_w if tryb == "x1" else z["pominieta_walka_s"]
    zajety = (t_w if tryb != "pomija+zwalnia" else z["pominieta_walka_s"]) + ZAJETOSC_ZAPAS_S
    cykl_potwora = zajety + t_odr + czas_wychodzenia(st, p)
    cykl_gracza = t_pokaz + z["narzut_walki_s"] + z["dojscie_s"]
    podaz = N * 60 / cykl_potwora
    popyt = P * 60 / cykl_gracza
    return podaz, popyt


def ilu_graczy(p, strefy, G, t_w, tryb="x1"):
    """Największe P (graczy w każdej strefie przegrody), przy którym podaż przegrody ≥ jej popyt."""
    best = 0
    for P in range(1, 41):
        podaz = popyt = 0
        for st in strefy:
            a, b = przepustowosc(p, st, G, P, t_w, tryb)
            podaz += a
            popyt += b
        if podaz >= popyt - 1e-9:
            best = P
    return best


def budzet_czasu(p, t_prosto):
    c = p["czas"]
    z = c["zalozenia"]
    walki = c["walki_plan"]
    narzut = z["narzut_walki_s"] + z["dojscie_s"]
    staly = t_prosto + z["przelot_s"] + z["jajko_s"] + z["trening_i_decyzje_s"]
    x1 = staly
    pom = staly
    n = 0
    for prz, ile in walki.items():
        t_w = z["walka_s"][GATUNEK[prz]]
        n += ile
        x1 += ile * (t_w + narzut)
        pom += (t_w + narzut) + max(0, ile - 1) * (z["pominieta_walka_s"] + narzut)
    chodzenie = t_prosto + n * z["dojscie_s"]
    return {"walk": n, "x1_s": x1, "pom_s": pom, "chodzenie_s": chodzenie}


def skala_biomow(p, t_prosto):
    c = p["czas"]
    z = c["zalozenia"]
    cykl = sum(z["walka_s"][GATUNEK[k]] * v for k, v in c["walki_plan"].items()) / sum(c["walki_plan"].values())
    cykl += z["narzut_walki_s"] + z["dojscie_s"]
    wynik = []
    for bid, minuty in c["rozklad_rosnacy_min"].items():
        trening = z["trening_i_decyzje_s"] * minuty / c["cel_min"]
        walki = (minuty * 60 - t_prosto - z["przelot_s"] - z["jajko_s"] - trening) / cykl
        chodz = t_prosto + walki * z["dojscie_s"]
        wynik.append((bid, minuty, walki, chodz / (minuty * 60)))
    return cykl, wynik


def farmienie(p):
    """Wiersze tabeli farmienia dla przegród ze strefami + błędy/ostrzeżenia „gracz czeka na odrodzenie”."""
    z = p["czas"]["zalozenia"]
    wiersze = []
    for q in p["przegrody"]:
        sts = [st for st in p["strefy"] if st["podbiom"] == q["id"]]
        if not sts:
            continue
        pod = [sum(przepustowosc(p, st, 8, 1, t_w, "x1")[0] for st in sts) for t_w in (15, 30)]
        if all(st.get("odrodzenie_stale") for st in sts):
            wiersze.append((q["nazwa"], pod, None, None, None, None))
            continue
        g8 = [ilu_graczy(p, sts, 8, t) * len(sts) for t in (15, 30)]
        g20 = [ilu_graczy(p, sts, 20, t) * len(sts) for t in (15, 30)]
        t_w = z["walka_s"][GATUNEK[q["id"]]]
        # jeden gracz ogląda walki ×1 w kojcu swojego poziomu — tu nie może czekać (błąd)
        for st in sts:
            for t in (15, 30):
                a, b_ = przepustowosc(p, st, 1, 1, t, "x1")
                if a < b_:
                    blad("%s, strefa %s: jeden gracz (×1, walka %d s) czeka na odrodzenie — %s z %s walk/min"
                         % (q["nazwa"], st["id"], t, l1(a), l1(b_)))
        # jeden gracz pomija walki (D-078) i chodzi po kojcach przegrody — ostrzeżenie, gdy czeka
        r1 = [przepustowosc(p, st, 1, 1, t_w, "pomija") for st in sts]
        r2 = [przepustowosc(p, st, 1, 1, t_w, "pomija+zwalnia") for st in sts]
        f1 = sum(a for a, _ in r1) / r1[0][1]
        f2 = sum(a for a, _ in r2) / r2[0][1]
        if f1 < 1:
            uwaga("%s: jeden gracz pomijający walki czeka na odrodzenie (%s× potrzeb)" % (q["nazwa"], l1(f1)))
        if g8[1] < 2 * len(sts):
            uwaga("%s: przy 8 graczach na serwerze mniej niż 2 graczy na kojec bez czekania" % q["nazwa"])
        wiersze.append((q["nazwa"], pod, g8, g20, f1, f2))
    return wiersze


# ===================================================================================================== główna
def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    global PLIK
    krotko = "--krotko" in sys.argv[1:]
    inne = [a for a in sys.argv[1:] if not a.startswith("--")]
    if inne:
        PLIK = os.path.abspath(inne[0])   # np. kopia planu do próby zmian
    with open(PLIK, encoding="utf-8") as f:
        p = json.load(f)

    pol = sprawdz_pas(p)
    przeg = sprawdz_odcinki(p, pol)
    strefy = sprawdz_strefy(p, przeg, pol)
    sprawdz_straznika(p, przeg, pol)
    m = sprawdz_miejsca(p, przeg, pol)
    T, vmax = sprawdz_kamere(p, pol)
    pudlo, koniec_u = sprawdz_swiat(p)
    zg = zgodnosc_z_logika()
    if zg is False:
        blad("kopia wzoru `cel` różni się od swiat/las_potwory/logika.py")
    t_prosto, czasy, miedzy = czasy_biegu(p, m)
    pot, sumy = tabela_potworow(p)
    b = budzet_czasu(p, t_prosto)
    farm = farmienie(p)
    z = p["czas"]["zalozenia"]
    lo, hi = p["czas"]["pasmo_min"]
    if not lo <= b["x1_s"] / 60 <= hi:
        uwaga("budżet ×1 = %s min — poza pasmem %d–%d min" % (l1(b["x1_s"] / 60), lo, hi))
    udzial = b["chodzenie_s"] / b["x1_s"]
    if udzial > 0.15:
        uwaga("chodzenie to %s%% czasu (×1) — więcej niż 15%%" % l1(100 * udzial))

    pas = p["pas"]
    try:
        nazwa_pliku = os.path.relpath(PLIK, os.path.dirname(os.path.dirname(os.path.dirname(TU)))).replace(os.sep, "/")
    except ValueError:
        nazwa_pliku = os.path.basename(PLIK)
    print("PLAN PASA LASU — kontrola (%s)" % nazwa_pliku)
    print("pas: %d × %d st (gra %d szer. = %s s biegu przy %d st/s; z kulisami %d szer.), las u %d…%d"
          % (pas["szerokosc"], pas["u_do"] - pas["u_od"], pas["szerokosc"], l1(pas["szerokosc_s"]),
             p["bieg"]["walkspeed"], pas["szerokosc"] + 2 * pas["kulisy"], pas["u_od"], pas["u_do"]))
    print("świat: X %s…%s (z rezerwą na 7 kolejnych biomów do X %s), Z %s…%s; kontener %s"
          % (pudlo[0], p["swiat"]["X0"] + pas["u_do"], p["swiat"]["X0"] + koniec_u, pudlo[2], pudlo[3],
             p["swiat"]["kontener"]))
    print("bieg od przybycia do bramy Bagna: %s s (%d st)" % (l1(t_prosto), round(t_prosto * p["bieg"]["walkspeed"])))
    if not krotko:
        print()
        print("%-24s %-11s %-7s %-14s %-10s" % ("przegroda", "u", "dł.", "od przybycia", "bieg przez nią"))
        for nazwa, u1, u2, dl, od, przez in czasy:
            print("%-24s %-11s %-7s %-14s %-10s" % (nazwa, "%d–%d" % (u1, u2), dl, l1(od) + " s", l1(przez) + " s"))
        print("między środkami sąsiednich stref: %s s (najwięcej %s s)" % (
            " / ".join(l1(x) for x in miedzy), l1(max(miedzy))))
        print()
        print("%-5s %-15s %-8s %-15s %-12s %s" % ("strefa", "potwór", "poziomy", "naraz G1/8/20", "odrodzenie",
                                                  "pętla / potrzeba"))
        for (sid, potw, poz, c, odr, stale), s_ in zip(pot, strefy):
            _, st, L, grupy, miejsc, ow, potrzeba = s_
            print("%-5s %-15s %-8s %-15s %-12s %s / %s st (%d × %d)" % (
                sid, potw, "%d–%d" % tuple(poz) if poz[0] != poz[1] else str(poz[0]), "%d / %d / %d" % tuple(c),
                ("%d s stałe" if stale else "%d s") % odr, l1(L), l1(potrzeba), grupy, miejsc))
        print("%-5s %-15s %-8s %-15s %-12s" % ("G", "Strażnik Gaju", str(p["straznik"]["poziom"]), "1 / 1 / 1",
                                               "%d s stałe" % p["straznik"]["odrodzenie_s"]))
        print("razem ze Strażnikiem: %d / %d / %d potworów przy 1 / 8 / 20 graczach" % tuple(sumy))
        print()
        print("FARMIENIE — walki na minutę (podaż) w przegrodzie; walka 15 s / 30 s przy ×1, narzut %d s + dojście %d s"
              % (z["narzut_walki_s"], z["dojscie_s"]))
        print("%-20s %-22s %-22s %-25s %s" % ("przegroda", "podaż G8 (walka 15/30)", "graczy bez czekania G8",
                                              "graczy bez czekania G20", "1 gracz pomija (prototyp / zwalnia)"))
        for nazwa, pod, g8, g20, f1, f2 in farm:
            if g8 is None:
                print("%-20s %-22s %-22s %-25s %s" % (nazwa, "%s / %s" % (l1(pod[0]), l1(pod[1])),
                                                      "— (rzadki)", "— (rzadki)", "— (nie do farmienia)"))
                continue
            print("%-20s %-22s %-22s %-25s %s" % (
                nazwa, "%s / %s" % (l1(pod[0]), l1(pod[1])), "%d / %d" % tuple(g8), "%d / %d" % tuple(g20),
                "%s× / %s× potrzeb" % (l1(f1), l1(f2))))
        print("(„graczy bez czekania” = ilu graczy naraz farmi w przegrodzie, rozłożonych po jej kojcach, i nie czeka "
              "na odrodzenie; „×potrzeb” ≥ 1 = jeden gracz pomijający walki nie czeka, gdy przechodzi między kojcami)")
        tr = p["strefy"][[s["id"] for s in p["strefy"]].index("t1")] if any(s["id"] == "t1" for s in p["strefy"]) else None
        if tr:
            pt, _ = przepustowosc(p, tr, 8, 1, z["walka_s"]["Leśny Troll"], "x1")
            print("Leśny Troll: %s walki/min na serwer (co ok. %d s) — rzadki z założenia" % (l1(pt), round(60 / pt)))
        print()
    print("BUDŻET CZASU LASU (cel %d min, pasmo %d–%d): ×1 %s min, z pomijaniem znanych walk (D-078) %s min; %d walk"
          % (p["czas"]["cel_min"], lo, hi, l1(b["x1_s"] / 60), l1(b["pom_s"] / 60), b["walk"]))
    print("chodzenie: %s s (bieg prosto %s s + dojście do potwora %d × %d s) = %s%% czasu ×1, %s%% z pomijaniem"
          % (l1(b["chodzenie_s"]), l1(t_prosto), b["walk"], z["dojscie_s"], l1(100 * b["chodzenie_s"] / b["x1_s"]),
             l1(100 * b["chodzenie_s"] / b["pom_s"])))
    if not krotko:
        cykl, sk = skala_biomow(p, t_prosto)
        print("kolejne biomy przy tym samym pasie (%d st, bieg prosto %s s) i średniej walce z narzutem %s s:"
              % (pas["u_do"] - pas["u_od"], l1(t_prosto), l1(cykl)))
        print("  " + " · ".join("%s %d min ≈ %d walk, chodzenie %s%%" % (bid, mi, round(w), l1(100 * u_))
                                for bid, mi, w, u_ in sk))
    print("przelot kamery: %s s, najszybciej %s st/s, zatrzymanie na Strażniku od %s s, ryk %s–%s s"
          % (l1(T), l1(vmax), l1(p["przelot_kamery"]["zatrzymanie_od_s"]), l1(p["przelot_kamery"]["ryk_od_s"]),
             l1(p["przelot_kamery"]["ryk_od_s"] + p["straznik"]["ryk"]["dl_s"])))
    bc = p["budzet_czesci"]
    razem = sum(v if isinstance(v, int) else sum(v.values()) for k, v in bc.items() if k != "porownanie")
    print("budżet części (szacunek): ok. %d (stary las v2: 22 419)" % razem)
    if zg is None:
        print("wzór `cel`: nie porównano z swiat/las_potwory/logika.py (brak pliku)")
    else:
        print("wzór `cel`: zgodny z swiat/las_potwory/logika.py")
    print()
    for t in uwagi:
        print("OSTRZEŻENIE:", t)
    for t in bledy:
        print("BŁĄD:", t)
    print("WYNIK: %d błędów, %d ostrzeżeń" % (len(bledy), len(uwagi)))
    sys.exit(1 if bledy else 0)


if __name__ == "__main__":
    main()
