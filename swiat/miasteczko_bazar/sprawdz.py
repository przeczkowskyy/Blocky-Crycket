#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola bazaru BEZ Studio: format, granice, nachodzenie, przejścia, osiągalność, czasy biegu, rozmiary części.

    python -B swiat/miasteczko_bazar/sprawdz.py            # pełny raport (kod 1 = błąd)
    python -B swiat/miasteczko_bazar/sprawdz.py --krotko   # tylko błędy, ostrzeżenia i podsumowanie

Sprawdza:
 1. format zgodny z tools/studio_buduj.py (na podstawie jego źródeł: jeden kontener Workspace/<Nazwa>, wiersz 15 albo
    16 pól, kształty 0–4, nazwy materiałów z Enum.Material, kolory RRGGBB, przezroczystość 0–1, cechy 1/2/3, liczby
    skończone) — sam skrypt Studio nie jest uruchamiany (zakaz pracy ze Studio w tym etapie);
 2. liczbę części (cel ok. 8000, twardy limit 12 000) i budżety budynków z modułów;
 3. granice: każda część w skrzynce z uklad.json (X ≤ 1066 — początek pasa Lasu), brak nachodzenia na Krzywe
    Miasteczko, stary las, oba prototypy walki i pas Lasu (skrzynki z swiat/biom_las/pas/plan_pasa.json); Baseplate
    — tylko styk (nic nie wchodzi w płytę głębiej niż 0,05);
 4. chodzenie (siatka.py): każdy punkt E osiągalny ze startu, czasy biegu (sklepy ≤ 5 s, portal ≤ 6 s), wejścia
    ≥ 8 szer. (zalecane ≥ 10) i ≥ 10 wys., wolny pas 8 st przez całą uliczkę, wolne miejsce wokół każdego punktu E,
    podpowiedź E ≤ 10 st od stoiska (domyślny zasięg ProximityPrompt);
 5. sprzedawcy: Model z częścią „Korzeń” na początku i podgrupami Glowa / Tulow / Rece / Nogi;
 6. jakość: części za małe (< 0,2 ostrzeżenie, < 0,05 błąd) i za duże (> 2048), zakazane materiały, migotanie
    (pokrywające się płaszczyzny różnych kolorów, bez części niewidzialnych), duplikaty, Neon i przezroczystość;
 7. znaczniki: start, portal, działka, zagroda z miejscami petów, tablica, Training Center z wejściem, sklepy, lochy,
    Brama Leśna i połączenie z Lasem.
"""
import argparse
import json
import math
import os
import re
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.biblioteka.scena import MATERIALY  # noqa: E402
from swiat.miasteczko_bazar import siatka  # noqa: E402
from swiat.miasteczko_bazar.generuj import modul, LIMIT, CEL  # noqa: E402

PLAN_PASA = os.path.join(REPO, "swiat", "biom_las", "pas", "plan_pasa.json")
ZAKAZANE_MATERIALY = {"Metal", "Glass", "Plastic", "Ground", "Grass", "Foil", "Ice"}
HEX = re.compile(r"^[0-9A-F]{6}$")
bledy, uwagi, info = [], [], []


def blad(t):
    bledy.append(t)


def uwaga(t):
    uwagi.append(t)


def l1(x):
    return ("%.1f" % x).replace(".", ",")


def wczytaj(n):
    with open(os.path.join(TU, n), encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------- 1. format
def sprawdz_format(D, U):
    for k in ("grupy", "materialy", "czesci"):
        if k not in D:
            blad("brak klucza %r w czesci.json" % k)
            return
    if D.get("generator") != "biblioteka-v2":
        uwaga("generator ≠ biblioteka-v2 — studio_buduj.py czytałby cechy po nazwach (v1)")
    korzenie = {g.split("/")[1] for g in D["grupy"] if g.startswith("Workspace/") and g.count("/") >= 1}
    obce = [g for g in D["grupy"] if not g.startswith("Workspace/")]
    if len(korzenie) != 1 or obce:
        blad("grupy muszą leżeć w jednym kontenerze Workspace/<Nazwa>/… (jest: %s, obce: %d)" % (sorted(korzenie), len(obce)))
    elif "Workspace/" + korzenie.pop() != U["swiat"]["kontener"]:
        blad("kontener inny niż w uklad.json: %s" % U["swiat"]["kontener"])
    for g in D["grupy"]:
        if any(not cz for cz in g.split("/")):
            blad("pusta część ścieżki grupy: %r" % g)
    for m in D["materialy"]:
        if m not in MATERIALY:
            blad("nieznany materiał %r (nie ma go w Enum.Material wg scena.py)" % m)
        if m in ZAKAZANE_MATERIALY:
            blad("zakazany materiał (PROJEKT miasteczka 2): %s" % m)
    ng, nm = len(D["grupy"]), len(D["materialy"])
    zle = 0
    for i, c in enumerate(D["czesci"]):
        ok = len(c) in (15, 16) and c[0] in (0, 1, 2, 3, 4) and isinstance(c[1], int) and 0 <= c[1] < ng
        ok = ok and all(isinstance(v, (int, float)) and math.isfinite(v) for v in c[2:11])
        ok = ok and isinstance(c[11], str) and bool(HEX.match(c[11])) and isinstance(c[12], int) and 0 <= c[12] < nm
        ok = ok and isinstance(c[13], (int, float)) and 0 <= c[13] <= 1 and isinstance(c[14], str) and 0 < len(c[14]) <= 40
        if len(c) == 16:
            ok = ok and c[15] in (1, 2, 3)
        if not ok:
            zle += 1
            if zle <= 5:
                blad("wiersz %d niezgodny z formatem studio_buduj.py: %s" % (i, json.dumps(c, ensure_ascii=False)[:160]))
    info.append("format: %d części, %d grup, %d materiałów (%s) — zgodny z tools/studio_buduj.py: %s"
                % (len(D["czesci"]), ng, nm, ", ".join(D["materialy"]), "tak" if not zle else "NIE (%d wierszy)" % zle))


# --------------------------------------------------------------------------- 2. liczba części
def sprawdz_liczbe(D, U, Z):
    n = len(D["czesci"])
    if n > LIMIT:
        blad("części %d > twardy limit %d" % (n, LIMIT))
    info.append("części: %d (cel ok. %d, twardy limit %d)" % (n, CEL, LIMIT))
    rap = Z.get("czesci_na_budynek", {})
    for b in U["budynki"]:
        m = modul(b["modul"])
        n_b = rap.get(m.NAZWA)
        bud = getattr(m, "BUDZET", None)
        if n_b is not None and bud is not None and n_b > bud:
            uwaga("%s: %d części > budżet modułu %d" % (m.NAZWA, n_b, bud))


# --------------------------------------------------------------------------- 3. granice i nachodzenie
def obwiednie(D):
    for c in D["czesci"]:
        W = siatka.wierzcholki(c)
        yield c, W.min(axis=0), W.max(axis=0)


def sprawdz_granice(D, U):
    X0, Z0 = U["swiat"]["X0"], U["swiat"]["Z0"]
    g = U["granice"]
    bx0, bx1 = X0 + g["czesci_x"][0], X0 + g["czesci_x"][1]
    bz0, bz1 = Z0 + g["czesci_z"][0], Z0 + g["czesci_z"][1]
    by0, by1 = g["czesci_y"]
    with open(PLAN_PASA, encoding="utf-8") as f:
        P = json.load(f)
    sw = P["swiat"]
    pudla = [("Krzywe Miasteczko (Workspace/KrzyweMiasteczko)", sw["miasteczko"]["zajete"])]
    pudla += [(o["id"], o["xz"]) for o in sw["zajete_inne"] if o["id"] != "baseplate"]
    h = sw["polowa_szerokosci_z_tlem"]
    las = ("pas Lasu z kulisami i tłem (X ≥ %g, |Z − (%g)| ≤ %g)" % (U["swiat"]["las_od_X"], sw["Z0"], h),
           [U["swiat"]["las_od_X"], sw["X0"] + P["kolejne_biomy"][-1]["u_do"], sw["Z0"] - h, sw["Z0"] + h])
    pudla.append(las)
    base = [o["xz"] for o in sw["zajete_inne"] if o["id"] == "baseplate"][0]
    poza, nach, pod_plyta = 0, {}, 0
    mn_all, mx_all = [1e9] * 3, [-1e9] * 3
    glebiej = 0.0
    for c, mn, mx in obwiednie(D):
        for i in range(3):
            mn_all[i], mx_all[i] = min(mn_all[i], mn[i]), max(mx_all[i], mx[i])
        if mn[0] < bx0 - 0.01 or mx[0] > bx1 + 0.01 or mn[2] < bz0 - 0.01 or mx[2] > bz1 + 0.01 or mn[1] < by0 or mx[1] > by1:
            poza += 1
            if poza <= 5:
                blad("część poza przyznanym miejscem: %s (X %s…%s, Z %s…%s, Y %s…%s)" % (
                    c[14], l1(mn[0]), l1(mx[0]), l1(mn[2]), l1(mx[2]), l1(mn[1]), l1(mx[1])))
        for nazwa, (a1, a2, b1, b2) in pudla:
            if mn[0] < a2 - 0.01 and mx[0] > a1 + 0.01 and mn[2] < b2 - 0.01 and mx[2] > b1 + 0.01:
                nach[nazwa] = nach.get(nazwa, 0) + 1
        if mn[0] < base[1] and mx[0] > base[0] and mn[2] < base[3] and mx[2] > base[2] and mn[1] < -0.05:
            pod_plyta += 1
            glebiej = max(glebiej, -mn[1])
    for nazwa, n in nach.items():
        blad("%d części nachodzi na: %s" % (n, nazwa))
    if poza > 5:
        blad("… razem %d części poza przyznanym miejscem" % poza)
    if pod_plyta:
        uwaga("%d części wchodzi w płytę Baseplate głębiej niż 0,05 (najgłębiej %s) — w Roblox niewidoczne, ale to nie "
              "jest czysty styk" % (pod_plyta, l1(glebiej)))
    info.append("zakres części w świecie: X %s…%s, Y %s…%s, Z %s…%s (przyznane X %s…%s, Z %s…%s)" % (
        l1(mn_all[0]), l1(mx_all[0]), l1(mn_all[1]), l1(mx_all[1]), l1(mn_all[2]), l1(mx_all[2]), l1(bx0), l1(bx1),
        l1(bz0), l1(bz1)))
    info.append("nachodzenie: Krzywe Miasteczko, BiomLas, TestWalki2, TestWalki, pas Lasu — %s; Baseplate: bazar stoi na "
                "jej wschodnim końcu (X ≤ 1024), wierzch gruntu 0,1 nad płytą" % ("brak" if not nach else "SĄ"))
    return mn_all, mx_all


# --------------------------------------------------------------------------- 4. chodzenie
def sprawdz_chodzenie(D, U, Z):
    S = siatka.Siatka(D, U)
    st = U["start"]
    S.z_punktu(st["x"], st["z"])
    v = U["bieg_st_s"]
    cele = U["cele_czasu"]
    wiersze = []
    for z in Z["wszystkie"]:
        if "stoisko_bazar" not in z:
            continue
        x, _, zz = z["stoisko_bazar"]
        d = S.droga_do(x, zz)
        t = d / v
        limit = cele["portal_s"] if z["typ"] == "portal" else (cele["sklep_s"] if z["typ"] in (
            "sklep", "training_center", "zagroda") else None)
        stan = "ok"
        if not math.isfinite(d):
            blad("punkt E %s nieosiągalny ze startu (siatka %s st, promień postaci %s)" % (z["id"], l1(S.krok), l1(siatka.PROMIEN)))
            stan = "NIEOSIĄGALNY"
        elif limit is not None and t > limit:
            blad("%s: %s s biegu > cel %s s" % (z["id"], l1(t), l1(limit)))
            stan = "ZA DALEKO"
        wiersze.append((z["id"], z["typ"], d, t, limit, stan))
        # wolne miejsce wokół stoiska (kwadrat 4 × 4 bez przeszkód) i zasięg podpowiedzi
        iz, ix = S.komorka(x, zz)
        r = int(2.0 / S.krok)
        blok = S.surowe[max(0, iz - r):iz + r, max(0, ix - r):ix + r]
        if blok.any():
            uwaga("%s: w kwadracie 4 × 4 wokół punktu E jest przeszkoda" % z["id"])
        if "podpowiedz_bazar" in z:
            px, py, pz = z["podpowiedz_bazar"]
            dd = math.sqrt((px - x) ** 2 + (py - (z["stoisko_bazar"][1] + 2.5)) ** 2 + (pz - zz) ** 2)
            if dd > 10.0:
                blad("%s: podpowiedź E %s st od głowy gracza na stoisku (> 10 — domyślny zasięg ProximityPrompt)" % (z["id"], l1(dd)))
    # wejścia
    for z in Z["wszystkie"]:
        if z["typ"] != "wejscie":
            continue
        if z["szer"] < 8.0 or z["wys"] < 10.0:
            blad("wejście %s: %s × %s (wymagane ≥ 8 × 10)" % (z["budynek"], l1(z["szer"]), l1(z["wys"])))
        elif z["szer"] < 10.0:
            uwaga("wejście %s: %s szer. — przechodzi, ale bez zapasu (zalecane ≥ 10)" % (z["budynek"], l1(z["szer"])))
    # wolny pas przez uliczkę (8 st, bez poszerzania o promień — sam pas ma być pusty)
    ul = U["uliczka"]
    zajete = []
    for xx in [ul["x"][0] + 0.5 * k for k in range(int((ul["x"][1] - ul["x"][0]) / 0.5))]:
        for zz in (-4.0, -2.0, 0.0, 2.0, 4.0):
            iz, ix = S.komorka(xx, zz)
            if S.surowe[iz, ix]:
                zajete.append((round(xx, 1), zz))
    if zajete:
        blad("pas 8 st przez uliczkę ma przeszkody, np. w %s" % zajete[:4])
    info.append("uliczka: wolny pas 8 st od x %s do %s (z −4…4): %s" % (l1(ul["x"][0]), l1(ul["x"][1]), "tak" if not zajete else "NIE"))
    return wiersze, S


# --------------------------------------------------------------------------- 5. sprzedawcy
def sprawdz_sprzedawcow(D, Z):
    grupy = D["grupy"]
    for z in Z["wszystkie"]:
        if not z.get("postac"):
            continue
        g = z.get("model")
        if not g or g not in grupy:
            blad("%s: brak Modelu sprzedawcy %s w czesci.json" % (z["id"], g))
            continue
        brak = [p for p in ("Glowa", "Tulow", "Rece", "Nogi") if g + "/" + p not in grupy]
        if brak:
            blad("%s: sprzedawca %s bez podgrup %s" % (z["id"], g, brak))
        gi = grupy.index(g)
        pierwsza = next((c for c in D["czesci"] if c[1] == gi), None)
        if not pierwsza or pierwsza[14] != "Korzeń":
            blad("%s: pierwsza część Modelu %s to nie „Korzeń” (studio_buduj.py zrobiłby z niej Folder)" % (z["id"], g))
        info.append("sprzedawca %-15s → %s (podgrupy: %s)" % (z["id"], g[len(Z["kontener"]["nazwa"]) + 1:], ", ".join(
            sorted({gg[len(g) + 1:].split("/")[0] for gg in grupy if gg.startswith(g + "/")}))))


# --------------------------------------------------------------------------- 6. jakość
def migotanie(D):
    """Pary nieobróconych bloków różnych kolorów, których ściany leżą w tej samej płaszczyźnie i zwrócone są w tę samą
    stronę (ta sama logika co Scena.sprawdz). Pomija części niewidzialne i spody leżące przy gruncie (y ≤ 0,6) —
    tych nikt nie zobaczy, bo pod nimi jest grunt."""
    pl = {}
    for i, c in enumerate(D["czesci"]):
        ks, g, x, y, z, rx, ry, rz, sx, sy, sz, kolor = c[:12]
        if ks != 0 or c[13] >= 0.98 or abs(rx) > 1e-4 or abs(rz) > 1e-4:
            continue
        q = ry / (math.pi / 2)
        if abs(q - round(q)) > 1e-3:
            continue
        if round(q) % 2:
            sx, sz = sz, sx
        for os_, wsp, pol, a0, a1, b0, b1 in ((0, x, sx / 2, y - sy / 2, y + sy / 2, z - sz / 2, z + sz / 2),
                                              (1, y, sy / 2, x - sx / 2, x + sx / 2, z - sz / 2, z + sz / 2),
                                              (2, z, sz / 2, x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2)):
            for zn in (1, -1):
                w = round(wsp + zn * pol, 2)
                if os_ == 1 and zn < 0 and w <= 0.6:
                    continue
                pl.setdefault((os_, zn, w), []).append((a0, a1, b0, b1, c[14], D["grupy"][g].split("/", 2)[-1], kolor))
    pary = []
    for sc in pl.values():
        if len(sc) < 2 or len(sc) > 400:
            continue
        for i in range(len(sc)):
            for j in range(i + 1, len(sc)):
                a, b = sc[i], sc[j]
                if a[6] != b[6] and min(a[1], b[1]) - max(a[0], b[0]) > 0.15 and min(a[3], b[3]) - max(a[2], b[2]) > 0.15:
                    pary.append("%s (%s) ↔ %s (%s)" % (a[4], a[5], b[4], b[5]))
    return pary


def sprawdz_jakosc(D):
    for c in D["czesci"]:
        if min(c[8], c[9], c[10]) < 0.05:
            blad("część za mała (< 0,05): %s" % c[14])
        if max(c[8], c[9], c[10]) > 2048:
            blad("część za duża (> 2048): %s" % c[14])
    klucze = {}
    for c in D["czesci"]:
        k = tuple(c[:11])
        if k in klucze:
            uwaga("duplikat części: %s" % c[14])
        klucze[k] = 1
    for p in migotanie(D)[:20]:
        uwaga("migotanie (ta sama płaszczyzna, różne kolory): " + p)
    drobne = [c for c in D["czesci"] if max(c[8], c[9], c[10]) < 0.5 and c[13] < 0.98]
    if drobne:
        uwaga("%d drobiazgów mniejszych niż 0,5 w każdym wymiarze, np. %s" % (len(drobne), sorted({c[14] for c in drobne})[:6]))
    mats = D["materialy"]
    neon = sum(1 for c in D["czesci"] if mats[c[12]] == "Neon")
    przezr = sum(1 for c in D["czesci"] if 0 < c[13] < 0.98)
    niew = sum(1 for c in D["czesci"] if c[13] >= 0.98)
    kol = sum(1 for c in D["czesci"] if not (len(c) > 15 and c[15] & 1))
    cienkie = sum(1 for c in D["czesci"] if min(c[8], c[9], c[10]) < 0.2)
    info.append("jakość: Neon %d, półprzezroczyste %d, niewidzialne zaczepy i ściany %d, z kolizją %d (%.0f%%), płaskich "
                "płyt cieńszych niż 0,2 (bruk, fuga, kody, oczka) %d" % (neon, przezr, niew, kol, 100.0 * kol / len(D["czesci"]),
                                                                         cienkie))


# --------------------------------------------------------------------------- 7. znaczniki
def sprawdz_znaczniki(Z):
    wsz = Z["wszystkie"]
    typy = {z["typ"] for z in wsz}
    ids = {z["id"] for z in wsz}
    for t in ("start", "portal", "dzialka", "zagroda", "miejsce_peta", "tablica", "training_center", "sklep", "lochy",
              "las", "polaczenie_las", "wejscie", "blokada"):
        if t not in typy:
            blad("brak znacznika typu %s" % t)
    for i in ("karczma", "mistrz_gier", "zbrojownia", "sklep_magiczny", "training_center", "zagroda_petow", "portal_krain",
              "brama_twierdzy", "tablica_ranking", "brama_lesna", "polaczenie_las", "wejscie_TrainingCenter", "start"):
        if i not in ids:
            blad("brak znacznika %s" % i)
    for z in wsz:
        if z["typ"] == "sklep" and not z.get("sklep"):
            blad("sprzedawca %s bez identyfikatora sklepu" % z["id"])


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Kontrola bazaru")
    ap.add_argument("--krotko", action="store_true")
    a = ap.parse_args()
    U, D, Z = wczytaj("uklad.json"), wczytaj("czesci.json"), wczytaj("znaczniki.json")
    sprawdz_format(D, U)
    sprawdz_liczbe(D, U, Z)
    sprawdz_granice(D, U)
    wiersze, S = sprawdz_chodzenie(D, U, Z)
    sprawdz_sprzedawcow(D, Z)
    sprawdz_jakosc(D)
    sprawdz_znaczniki(Z)
    if not a.krotko:
        print("CZASY BIEGU ZE STARTU (16 st/s, najkrótsza droga z omijaniem przeszkód, postać Ø %s):" % l1(2 * siatka.PROMIEN))
        for i, t, d, s_, lim, stan in sorted(wiersze, key=lambda w: w[3]):
            print("  %-18s %-16s %6s st  %5s s%s  %s" % (i, t, l1(d), l1(s_), ("  (cel ≤ %s s)" % l1(lim)) if lim else "", stan))
        print("CZĘŚCI NA BUDYNEK / GRUPĘ:")
        for k, n in sorted(Z.get("czesci_na_budynek", {}).items(), key=lambda kv: -kv[1]):
            print("  %-22s %5d" % (k, n))
        for t in info:
            print("INFO:", t)
    for t in uwagi:
        print("UWAGA:", t)
    for t in bledy:
        print("BŁĄD:", t)
    print("WYNIK: %d błędów, %d ostrzeżeń" % (len(bledy), len(uwagi)))
    return 1 if bledy else 0


if __name__ == "__main__":
    sys.exit(main())
