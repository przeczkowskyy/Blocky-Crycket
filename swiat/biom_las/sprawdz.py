# -*- coding: utf-8 -*-
"""Kontrola układu biomu Las (uklad.json + potwory.json + ujecia.json; czesci.json, jeśli jest).

    python -B swiat/biom_las/sprawdz.py

Sprawdza:
 1. podbiomy dzielą obszar gry bez dziur i nakładek; wszystkie wielokąty (podbiomy, poziomy terenu, jezioro) są proste;
 2. teren: żadnego uskoku w paśmie 6,5–9 (przeszkoda ≤ 6 do przeskoczenia albo ≥ 10 bariera);
 3. lokacje: w swoim podbiomie, bez nakładek, z dojściem; obrys lokacji z murami (labirynt) nie przecina wody;
 4. ścieżki: jedna sieć, struga tylko przy przeprawach, ŻADNEGO URWISKA NA DRODZE (wysokość wzdłuż ścieżki zmienia się
    najwyżej o 0,6 na studzie — zejścia tylko rampami i zboczami), czasy biegu od bramy;
 5. potwory: strefy w podbiomie, poza strefami spokoju, bez nakładek; węzły walki (płasko ±0,5 w r 12, woda, rdzenie
    lokacji); przejścia między węzłami, trasa trolla i patrole bez urwisk; pojemność z obwodu pętli; domy 35–50 od węzłów
    (blokada odradzania 18); strefy różniące się o ≥ 3 poziomy odsunięte ≥ 60 (brzeg–brzeg); przepływ walk na Łące;
 6. kontrast potworów z gruntem ich strefy (ΔL* ≥ 20 albo podkładka);
 7. budżet części (z uklad.json; z czesci.json, jeśli istnieje) i ujęcia z oczu (≥ 2 punkty orientacyjne w kadrze).
Kod wyjścia 1, gdy jest błąd (ostrzeżenia nie blokują).
"""
import heapq
import json
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import geo  # noqa: E402
import wezly as W  # noqa: E402
from geo import BIEG, w_wielokacie, odl_lamana, dlugosc, przeciecie, okrag  # noqa: E402

KADRY_LOKACJI = {"l02", "l07", "l08", "l09", "l11", "l12", "l14", "l16", "l17"}
KOLOR_POTWORA = {"Leśny Slime": "7EDB57", "Bursztynowy Slime": "zloto", "Muchomornik": "czerwien",
                 "Cierniowy Wilk": "kamien_lochu"}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    U, P, UJ = geo.wczytaj("uklad.json"), geo.wczytaj("potwory.json"), geo.wczytaj("ujecia.json")
    T = geo.Teren(U)
    bledy, ostrz = [], []
    pod = {b["id"]: b for b in U["podbiomy"]}
    x0, z0, x1, z1 = U["obrys"]["gra"]

    # ------------------------------------------------------------------ 1. podbiomy i wielokąty
    krok = 2.0
    pola = {k: 0 for k in pod}
    dziury = nakl = 0
    z = z0 + krok / 2
    while z < z1:
        x = x0 + krok / 2
        while x < x1:
            ile = [k for k, b in pod.items() if w_wielokacie((x, z), b["wielokat"])]
            if not ile:
                dziury += 1
            elif len(ile) > 1:
                nakl += 1
            else:
                pola[ile[0]] += 1
            x += krok
        z += krok
    cale = (x1 - x0) * (z1 - z0)
    print("PODBIOMY (pole w tys. st², udział w obszarze gry):")
    for k, n in pola.items():
        print("  %-18s %6.1f  %4.1f%%" % (pod[k]["nazwa"], n * krok * krok / 1000, 100 * n * krok * krok / cale))
    if dziury or nakl:
        bledy.append("podbiomy: %d pól bez podbiomu, %d pól w dwóch naraz" % (dziury, nakl))
    wiel = [("podbiom " + b["id"], b["wielokat"]) for b in U["podbiomy"]]
    wiel += [("poziom " + e["id"], e["wielokat"]) for e in T.poziomy]
    wiel += [("woda " + w["id"], w["wielokat"]) for w in U["woda"] if "wielokat" in w]
    for nazwa, w in wiel:
        zle = geo.samoprzeciecia(w)
        if zle:
            bledy.append("%s: wielokąt przecina sam siebie (krawędzie %s)" % (nazwa, zle[:4]))
    print("WIELOKĄTY: %d sprawdzonych, samoprzecięcia: %s" % (len(wiel), "są" if any("przecina sam" in b for b in bledy) else "brak"))

    # ------------------------------------------------------------------ 2. teren: pasmo 6,5–9
    xs, _, H = T.siatka(2.0)
    import numpy as np
    X, Z = np.meshgrid(xs, xs)
    rampa = np.zeros(H.shape, dtype=bool)
    for e in T.rampy:
        (ax, az, _), (bx, bz, _) = e["od"], e["do"]
        d = geo.odl_lamana_np(X, Z, [(ax, az), (bx, bz)])
        rampa |= d < e["szer"] / 2.0 + 3
    gra = (np.abs(X) <= 432) & (np.abs(Z) <= 432)
    zle_pasmo = 0
    for dH, m in ((np.abs(np.diff(H, axis=0)), gra[1:, :] & ~rampa[1:, :] & ~rampa[:-1, :]),
                  (np.abs(np.diff(H, axis=1)), gra[:, 1:] & ~rampa[:, 1:] & ~rampa[:, :-1])):
        zle_pasmo += int(((dH > 6.5) & (dH < 9.5) & m).sum())
    uskoki = sorted({round(float(v), 1) for v in np.unique(np.abs(np.diff(H, axis=0))) if v > 0.6})
    print("TEREN: poziomy %s; uskoki między sąsiednimi polami 2 st: %s" % (
        sorted({e["y"] for e in T.poziomy}), ", ".join("%g" % v for v in uskoki if v > 3) or "—"))
    if zle_pasmo:
        bledy.append("teren: %d par pól z uskokiem 6,5–9 (ani do przeskoczenia, ani bariera)" % zle_pasmo)

    # ------------------------------------------------------------------ 3. lokacje
    lok = {l["id"]: l for l in U["lokacje"]}
    for l in U["lokacje"]:
        w = pod[l["podbiom"]]["wielokat"]
        if not w_wielokacie((l["x"], l["z"]), w):
            bledy.append("lokacja %s: środek poza podbiomem %s" % (l["id"], l["podbiom"]))
        h = T.H(l["x"], l["z"])
        if abs(h - l["y"]) > 1.0 and not l.get("wewnatrz") and l["id"] not in ("jezioro_za_tama",):
            ostrz.append("lokacja %s: y %.1f w uklad.json, a grunt w środku %.1f" % (l["id"], l["y"], h))
    ll = U["lokacje"]
    for i in range(len(ll)):
        for j in range(i + 1, len(ll)):
            a, b = ll[i], ll[j]
            if a.get("wewnatrz") == b["id"] or b.get("wewnatrz") == a["id"]:
                continue
            d = math.hypot(a["x"] - b["x"], a["z"] - b["z"])
            if d < a["r"] + b["r"]:
                bledy.append("lokacje %s i %s zachodzą na siebie (%.0f < %d)" % (a["id"], b["id"], d, a["r"] + b["r"]))
    lab = lok["jezynowy_labirynt"]
    if geo.woda_odl(U, lab["x"], lab["z"]) < lab["r"] + 3:
        bledy.append("Jeżynowy Labirynt: obrys z murami (r %d) przecina wodę" % lab["r"])
    else:
        print("LABIRYNT: brzeg wody %.0f st od obrysu z murami" % (geo.woda_odl(U, lab["x"], lab["z"]) - lab["r"]))

    # ------------------------------------------------------------------ 4. ścieżki
    kraw = {}

    def wezel(p):
        return (round(p[0], 1), round(p[1], 1))

    for s in U["sciezki"]:
        for i in range(len(s["pts"]) - 1):
            a, b = wezel(s["pts"][i]), wezel(s["pts"][i + 1])
            d = math.dist(a, b)
            kraw.setdefault(a, []).append((b, d))
            kraw.setdefault(b, []).append((a, d))
    start = wezel(U["wejscie"]["punkt"])
    dist = {start: 0.0}
    q = [(0.0, start)]
    while q:
        d, u = heapq.heappop(q)
        if d > dist[u]:
            continue
        for v, w in kraw.get(u, []):
            if d + w < dist.get(v, 1e18):
                dist[v] = d + w
                heapq.heappush(q, (d + w, v))
    if len(dist) != len(kraw):
        bledy.append("ścieżki: %d z %d węzłów nieosiągalnych z wejścia: %s" % (
            len(kraw) - len(dist), len(kraw), [k for k in kraw if k not in dist][:5]))
    print("ŚCIEŻKI: %d węzłów, razem %.0f st; urwiska na drodze:" % (len(kraw), sum(dlugosc(s["pts"]) for s in U["sciezki"])))
    for s in U["sciezki"]:
        us = geo.uskoki(T, s["pts"])
        if us:
            bledy.append("ścieżka %s: urwisko na drodze w %s" % (s["id"], ["(%.0f;%.0f) %+.1f" % u for u in us[:3]]))
    print("  %s" % ("brak" if not any("urwisko na drodze" in b for b in bledy) else "SĄ (niżej)"))
    struga = next(w for w in U["woda"] if w["id"] == "kreta_struga")["pts"]
    for s in U["sciezki"]:
        if s["rodzaj"] == "sekretna":
            continue
        for i in range(len(s["pts"]) - 1):
            for j in range(len(struga) - 1):
                p = przeciecie(s["pts"][i], s["pts"][i + 1], struga[j], struga[j + 1])
                if p:
                    blisko = min(math.hypot(p[0] - pr["x"], p[1] - pr["z"]) for pr in U["przeprawy"])
                    if blisko > 15:
                        bledy.append("ścieżka %s przecina strugę w (%.0f;%.0f) %.0f od przeprawy" % (s["id"], p[0], p[1], blisko))
    print("DOJŚCIA od bramy (bieg %d st/s, po ścieżkach):" % BIEG)
    czasy = {}
    for l in U["lokacje"]:
        if l.get("wewnatrz"):
            continue
        best = None
        for k, d in dist.items():
            r = math.hypot(k[0] - l["x"], k[1] - l["z"])
            if r > l["r"] + 25:
                continue
            c = d + max(0.0, r - l["r"])
            if best is None or c < best:
                best = c
        od_sc = min(odl_lamana((l["x"], l["z"]), s["pts"]) for s in U["sciezki"])
        if od_sc > l["r"] + 15:
            bledy.append("lokacja %s: najbliższa ścieżka %.0f od środka (obrys %d)" % (l["id"], od_sc, l["r"]))
        if best is None:
            bledy.append("lokacja %s: brak węzła ścieżki przy obrysie" % l["id"])
            continue
        czasy[l["id"]] = best / BIEG
        print("  %2d %-30s %5.0f st  %4.1f s" % (l["nr"], l["nazwa"], best, best / BIEG))

    # ------------------------------------------------------------------ 5. potwory
    maska = W.Maska(U, P)
    spokoj = [s for s in U["strefy_spokoju"] if "srodek" in s]
    serce = pod["serce"]["wielokat"]
    zs = P["strefy"]
    suma = suma_max = 0
    print("STREFY POTWORÓW:")
    for st in zs:
        c, r = st["srodek"], st["r"]
        w = pod[st["podbiom"]]["wielokat"]
        if sum(1 for p in okrag(c, r) if not w_wielokacie(p, w)) > 3:
            ostrz.append("strefa %s: brzeg wychodzi poza podbiom" % st["id"])
        for s in spokoj:
            if math.dist(c, s["srodek"]) < r + s["r"]:
                bledy.append("strefa %s nachodzi na strefę spokoju %s" % (st["id"], s["id"]))
        if any(w_wielokacie(p, serce) for p in okrag(c, r + P["zasady"]["smycz"])):
            bledy.append("strefa %s (ze smyczą) wchodzi do Serca Boru" % st["id"])
        woda_min = 10.0 if st["id"] == "z01" else W.WODA_MIN
        for x, zz in st["trasa"]:
            pw = maska.powod(x, zz, float(st["y"]), st, woda_min)
            if pw:
                bledy.append("strefa %s: węzeł (%.0f;%.0f) nie nadaje się na walkę: %s" % (st["id"], x, zz, pw))
        tr = st["trasa"]
        for i in range(len(tr)):
            if st["id"] in W.RECZNE and i == len(tr) - 1:
                break
            us = geo.uskoki(T, [tr[i], tr[(i + 1) % len(tr)]])
            if us and st["id"] not in W.RECZNE:
                bledy.append("strefa %s: przejście %s → %s przez urwisko" % (st["id"], tr[i], tr[(i + 1) % len(tr)]))
        ob = W.obwod([(x, zz) for x, zz in tr])
        poj = max(1, int(ob // P["zasady"]["odstep_min"])) if len(tr) > 2 else len(tr)
        if W.jednostki(st) > poj:
            bledy.append("strefa %s: %d potworów/watah przy pojemności %d (obwód %.0f / 25)" % (st["id"], W.jednostki(st), poj, ob))
        domy = st["dom"]["pts"]
        if len(domy) < 2:
            ostrz.append("strefa %s: tylko %d dom(y)" % (st["id"], len(domy)))
        for d in domy:
            m = min(math.dist(d, t) for t in tr)
            if m < 35 - 0.5 or m > 50 + 0.5:
                bledy.append("strefa %s: dom %s %.0f od najbliższego węzła (ma być 35–50)" % (st["id"], d, m))
        od_sc = min(odl_lamana(c, s["pts"]) for s in U["sciezki"] if s["rodzaj"] != "sekretna") - r
        if od_sc > 15:
            ostrz.append("strefa %s: brzeg %.0f od najbliższej ścieżki" % (st["id"], od_sc))
        suma += st["naraz"]
        suma_max += st["max"]
        print("  %s %-12s %-15s poz %2d–%-2d naraz %d (max %d)  y %4.1f  węzłów %d  obwód %3.0f → pojemność %d  domów %d" % (
            st["id"], st["podbiom"], st["potwor"], st["poziomy"][0], st["poziomy"][1], st["naraz"], st["max"], st["y"],
            len(tr), ob, poj, len(domy)))
    for i in range(len(zs)):
        for j in range(i + 1, len(zs)):
            a, b = zs[i], zs[j]
            d = math.dist(a["srodek"], b["srodek"]) - a["r"] - b["r"]
            if d < 0:
                bledy.append("strefy %s i %s zachodzą na siebie" % (a["id"], b["id"]))
            roznica = max(abs(a["poziomy"][0] - b["poziomy"][1]), abs(b["poziomy"][0] - a["poziomy"][1]))
            if min(a["poziomy"][1], b["poziomy"][1]) + 3 <= max(a["poziomy"][0], b["poziomy"][0]) and d < 60:
                bledy.append("strefy %s (%s) i %s (%s) różnią się o %d poziomy, a brzegi dzieli tylko %.0f st" % (
                    a["id"], a["poziomy"], b["id"], b["poziomy"], roznica, d))
    pat = P.get("patrole", [])
    for p in pat:
        if geo.uskoki(T, p["trasa"]):
            bledy.append("patrol %s: trasa przez urwisko" % p["id"])
        for x, zz in p["trasa"]:
            for s in spokoj:
                if math.dist((x, zz), s["srodek"]) < s["r"]:
                    bledy.append("patrol %s: węzeł w strefie spokoju %s" % (p["id"], s["id"]))
    print("  RAZEM: %d zwykłych naraz (max %d) w %d strefach + %d patrole (%d potworów) + troll + strażnik" % (
        suma, suma_max, len(zs), len(pat), sum(sum(v for v in p["grupa"].values()) for p in pat)))
    tr = P["troll"]["trasa"]
    if geo.uskoki(T, tr):
        bledy.append("trasa trolla przez urwisko: %s" % geo.uskoki(T, tr)[:3])
    for p in tr:
        for s in spokoj:
            if math.dist(p, s["srodek"]) < s["r"]:
                bledy.append("trasa trolla: węzeł %s w strefie spokoju %s" % (p, s["id"]))
    print("TROLL: trasa %.0f st (%.0f s w jedną stronę przy %d st/s), bez urwisk: %s" % (
        dlugosc(tr), dlugosc(tr) / P["zasady"]["predkosc"]["Leśny Troll"], P["zasady"]["predkosc"]["Leśny Troll"],
        "tak" if not geo.uskoki(T, tr) else "NIE"))
    # pokrycie ścieżek
    sciezki_gry = [s for s in U["sciezki"] if s["rodzaj"] in ("glowna", "boczna", "labirynt")]
    probki = b40 = b60 = 0
    for s in sciezki_gry:
        for x, zz, _, _ in geo.punkty_co(s["pts"], 10):
            if w_wielokacie((x, zz), serce) or any(math.dist((x, zz), sp["srodek"]) < sp["r"] for sp in spokoj):
                continue
            probki += 1
            d = min(max(0.0, math.dist((x, zz), q["srodek"]) - q["r"]) for q in zs)
            d = min([d] + [odl_lamana((x, zz), p["trasa"]) for p in pat])
            b40 += d <= 40
            b60 += d <= 60
    print("POKRYCIE: %d próbek ścieżek poza strefami spokoju; potwory (strefa albo patrol) ≤ 40 st: %.0f%%, ≤ 60 st: %.0f%%" % (
        probki, 100 * b40 / probki, 100 * b60 / probki))
    # przepływ na Łące (start gry: wszyscy na 1. poziomie)
    laka = [s for s in zs if s["podbiom"] == "laka"]
    for gracze in (8, 20):
        sloty = sum(min(s["max"], max(s["naraz"] // 2, round(s["naraz"] * gracze / 8.0))) for s in laka)
        odr = max(10.0, 15.0 / (1 + 0.15 * (gracze / len(laka) - 1)))
        podaz = sloty * 60.0 / (odr + 12.0)                 # 12 s: dojście z domu do węzła i chwila na wybór
        popyt = gracze * 60.0 / (14.0 + 10.0)               # walka ok. 14 s + 10 s na podejście do następnego
        print("PRZEPŁYW ŁĄKI przy %2d graczach: %2d slime'ów naraz, odradzanie %.0f s → do %.0f walk/min; gracze chcą ok. %.0f/min"
              " → %.1f walk/min na gracza" % (gracze, sloty, odr, podaz, popyt, min(podaz, popyt) / gracze))
        if podaz < popyt * 0.8:
            ostrz.append("Łąka przy %d graczach: potworów za mało (%.0f < %.0f walk/min)" % (gracze, podaz, popyt))

    # ------------------------------------------------------------------ 6. kontrast potworów z gruntem
    import paleta as PAL
    grunt = {"laka": ("runo", "podkładka strefy: wydeptana ciemniejsza trawa"), "kapeluszowo": ("mech", "polanka mchu"),
             "ostepy": ("runo", "runo boru"), "wawoz": ("kamien_cokol", "ciemne błoto Wyschniętej Kałuży"),
             "korona": ("runo_ciemne", "taras")}
    print("KONTRAST potworów z gruntem strefy (ΔL*, wymagane ≥ 20):")
    for st in zs:
        nazwa = "Bursztynowy Slime" if st.get("wariant") else st["potwor"]
        g, opis = grunt[st["podbiom"]]
        g, opis = {"z13": ("bruk_ciemny", "półka wąwozu"), "z06": ("runo", "podkładka: runo w mchu"),
                   "z11": ("ziemia", "dno rynny"), "z14": ("mech", "polanka mchu na tarasie"),
                   "z15": ("trawa", "taras górny")}.get(st["id"], (g, opis))
        dl = abs(PAL.lstar(KOLOR_POTWORA[nazwa]) - PAL.lstar(g))
        znak = "OK" if dl >= 20 else "!!"
        print("  %s %s %-18s na %-13s (%s): ΔL* %4.1f" % (znak, st["id"], nazwa, g, opis, dl))
        if dl < 20:
            ostrz.append("strefa %s: %s słabo widać na %s (ΔL* %.0f)" % (st["id"], nazwa, g, dl))

    # ------------------------------------------------------------------ 7. budżet i ujęcia
    b = U["budzet"]
    plan = sum(v for k, v in b.items() if k not in ("limit", "wspolne", "opis")) + sum(b.get("wspolne", {}).values())
    print("BUDŻET (plan): %d części przy limicie %d" % (plan, b["limit"]))
    cz = os.path.join(TU, "czesci.json")
    if os.path.exists(cz):
        with open(cz, encoding="utf-8") as f:
            n = len(json.load(f)["czesci"])
        print("BUDŻET (czesci.json): %d części" % n)
        if n > b["limit"]:
            bledy.append("czesci.json: %d części > limit %d" % (n, b["limit"]))
    orient = [l for l in U["lokacje"] if l["orientacyjny"]]
    print("UJĘCIA z oczu (punkty orientacyjne w poziomym kącie kadru 16:9; zasłaniania nie liczymy):")
    for nazwa, cam, cel, ogn, orto in UJ:
        if orto or cam[1] > 100:
            continue
        kier = math.atan2(cel[0] - cam[0], cel[2] - cam[2])
        widac = []
        for l in orient:
            d = math.hypot(l["x"] - cam[0], l["z"] - cam[2])
            if d < 5:
                continue
            a = math.atan2(l["x"] - cam[0], l["z"] - cam[2]) - kier
            a = (a + math.pi) % (2 * math.pi) - math.pi
            if abs(math.degrees(a)) <= 51:
                widac.append("%s (%.0f st)" % (l["nazwa"], d))
        lokacji = nazwa.split("_")[0] in KADRY_LOKACJI
        if len(widac) < 2 and not lokacji:
            ostrz.append("ujęcie %s: tylko %d punkt(y) orientacyjne w kadrze" % (nazwa, len(widac)))
        print("  %s%-22s %s" % ("OK " if len(widac) >= 2 else ("-- " if lokacji else "!! "), nazwa, "; ".join(widac) or "—"))

    print()
    for o in ostrz:
        print("OSTRZEŻENIE:", o)
    for e in bledy:
        print("BŁĄD:", e)
    print("Wynik: %d błędów, %d ostrzeżeń" % (len(bledy), len(ostrz)))
    return 1 if bledy else 0


if __name__ == "__main__":
    sys.exit(main())
