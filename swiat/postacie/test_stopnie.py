#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy stopni ekwipunku i katalogu sklepu (D-106) — czysty Python, bez Blendera i Studio, ok. 1 min.

    python -B swiat/postacie/test_stopnie.py            # kod 1, gdy którykolwiek test nie przechodzi
    python -B swiat/postacie/test_stopnie.py --md       # dodatkowo tabela pomiaru przenikania (Markdown)

1. Bohaterowie bez zmian: dzisiejsze 20 przedmiotów (id jak w przedmioty.json), kanon i zbuduj() — odcisk pakietu
   dla Blendera taki sam przed zbudowaniem stopni i po nim (stopnie niczego w modułach bohaterów nie zmieniają).
2. Nowe przedmioty: 20 na stopień (8 + 8 + 4), te same sloty, kości, powłoki i ukrywanie co odpowiednik startowy,
   każdy zakłada się sam na gołe ciało swojej klasy, komplet zakłada się w całości, obce ciało i druga powłoka
   na tej samej kości dają błąd; sylwetka hełmu, napierśnika i broni różni się od startowej i między stopniami.
3. Przenikanie kompletów w spoczynku (poza wyjściowa szkieletu, bryły jako prostopadłościany):
   a) przedmioty w dłoni i na głowie kota nie wchodzą w głowę, tułów, biodra i nogi głębiej niż 0,06 studa
      (albo nie głębiej niż w komplecie startowym);
   b) bryły zbroi nie wchodzą w bryły INNYCH kości głębiej niż w komplecie startowym + 0,10 studa.
4. Katalog: sklep_przedmioty.json aktualny; każdy slot klasy obsadzony w każdym stopniu; cena, wymagany poziom
   i suma statystyk bazowych rosną ze stopniem; części zbroi (nogawice, spodnie) nie są sprzedawane osobno;
   statystyki tylko z listy kowala.
"""
import hashlib
import json
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.postacie import sklep_katalog, stopnie  # noqa: E402
from swiat.postacie.biblioteka.postac import macierz_obrotu, pakiet, razy_wektor  # noqa: E402
from swiat.postacie.ekwipunek import ubierz  # noqa: E402

PROG_BRONI = 0.06            # EKWIPUNEK.md pkt 2: próg dla broni i dłoni w głowie i tułowiu
ZAPAS_ZBROI = 0.10           # o ile komplet stopnia może być gorszy od startowego (bryły liczone jak pudełka)
WYNIKI = []


def test(nazwa, ok, szczegoly=""):
    WYNIKI.append(bool(ok))
    print("%s  %s%s" % ("OK  " if ok else "BŁĄD", nazwa, (" — " + szczegoly) if szczegoly else ""))


def odcisk(mod):
    tekst = json.dumps(pakiet(mod.zbuduj()), ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(tekst.encode("utf-8")).hexdigest()[:12]


# --------------------------------------------------------------------------- pomiar przenikania w spoczynku
def _T(m):
    return [[m[j][i] for j in range(3)] for i in range(3)]


def _pudelka(p):
    """[(grupa, kość, środek, R, R^T, połowy)] wszystkich brył postaci w układzie modelu (poza wyjściowa)."""
    j = p.json()
    wynik = []
    for grupa, lista in [("Cialo", j["czesci"])] + [(a["id"], a["czesci"]) for a in j["akcesoria"]]:
        for c in lista:
            R = macierz_obrotu(*c["r"])
            wynik.append((grupa, c["kosc"], tuple(c["p"]), R, _T(R), tuple(v / 2.0 for v in c["s"]), c["n"]))
    return wynik


def _punkty(b):
    """Siatka punktów bryły (co ok. 0,2 studa, z brzegami), w układzie modelu."""
    _, _, sr, R, _, pol, _ = b
    osie = []
    for h in pol:
        n = max(2, min(14, int(math.ceil(2 * h / 0.2)) + 1))
        osie.append([-h + 2 * h * i / (n - 1) for i in range(n)])
    return [tuple(sr[i] + v[i] for i in range(3))
            for x in osie[0] for y in osie[1] for z in osie[2]
            for v in (razy_wektor(R, (x, y, z)),)]


def _glebokosc(pt, b):
    _, _, sr, _, RT, pol, _ = b
    lok = razy_wektor(RT, (pt[0] - sr[0], pt[1] - sr[1], pt[2] - sr[2]))
    return min(pol[i] - abs(lok[i]) for i in range(3))


def _najglebiej(zrodla, cele):
    """Największa głębokość punktu którejkolwiek bryły ze `zrodla` w którejkolwiek bryle z `cele` (0 = brak)."""
    naj = (0.0, "", "")
    for a in zrodla:
        ra = math.sqrt(sum(v * v for v in a[5]))
        bliskie = [b for b in cele
                   if math.dist(a[2], b[2]) < ra + math.sqrt(sum(v * v for v in b[5]))]
        if not bliskie:
            continue
        for pt in _punkty(a):
            for b in bliskie:
                g = _glebokosc(pt, b)
                if g > naj[0]:
                    naj = (g, "%s/%s" % (a[1], a[6]), "%s/%s" % (b[1], b[6]))
    return naj


RAMIE = {"RightHand": ("RightHand", "RightLowerArm", "RightUpperArm"),
         "LeftHand": ("LeftHand", "LeftLowerArm", "LeftUpperArm"),
         "StaffPivot": ("RightHand", "RightLowerArm", "RightUpperArm", "StaffPivot"),
         "HatPivot": ("Head", "LeftEar", "RightEar", "HatPivot")}


def przenikanie(p):
    """(a: przedmioty na zaczepach w ciele poza własną ręką / głową, b: bryły kości w bryłach innych kości)."""
    pud = _pudelka(p)
    cialo = [b for b in pud if b[0] == "Cialo"]
    a = (0.0, "", "")
    for grupa in sorted({b[0] for b in pud if b[0] != "Cialo"}):
        swoje = [b for b in pud if b[0] == grupa]
        if swoje[0][1] not in RAMIE:
            continue                                              # włosy i inne akcesoria ciała
        wynik = _najglebiej(swoje, [b for b in cialo if b[1] not in RAMIE[swoje[0][1]]])
        if wynik[0] > a[0]:
            a = wynik
    b_ = (0.0, "", "")
    for kosc in sorted({b[1] for b in cialo}):
        wynik = _najglebiej([b for b in cialo if b[1] == kosc], [b for b in cialo if b[1] != kosc])
        if wynik[0] > b_[0]:
            b_ = wynik
    return a, b_


def obrys(akc_czesci):
    """Skrzynka brył (szer, wys, głęb) — do porównania sylwetek."""
    mn, mx = [1e9] * 3, [-1e9] * 3
    for c in akc_czesci:
        R = macierz_obrotu(*c["r"])
        for sx in (-1, 1):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    v = razy_wektor(R, (sx * c["s"][0] / 2, sy * c["s"][1] / 2, sz * c["s"][2] / 2))
                    for i in range(3):
                        mn[i] = min(mn[i], c["p"][i] + v[i])
                        mx[i] = max(mx[i], c["p"][i] + v[i])
    return tuple(round(mx[i] - mn[i], 2) for i in range(3))


# --------------------------------------------------------------------------- testy
def main(argv):
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    katalog_bohaterow = json.load(open(os.path.join(TU, "przedmioty.json"), encoding="utf-8"))
    wiersze_md = []

    # 1. bohaterowie bez zmian
    przed = {k: odcisk(m) for k, m in stopnie.MODULY.items()}
    po_id = {k: stopnie.wszystkie(k) for k in stopnie.MODULY}
    po = {k: odcisk(m) for k, m in stopnie.MODULY.items()}
    test("1a odcisk zbuduj() bohaterów bez zmian po zbudowaniu stopni", przed == po, str(po))
    dzis = [x.id for m in stopnie.MODULY.values() for x in m.przedmioty()]
    w_katalogu = {p["id"] for p in katalog_bohaterow["przedmioty"]}
    test("1b dzisiejsze przedmioty bohaterów: 20, wszystkie w przedmioty.json", len(dzis) == 20
         and set(dzis) <= w_katalogu, "%d przedmiotów" % len(dzis))
    test("1c komplet startowy = dzisiejszy kanon (Wojownik z tarczą)",
         all(set(stopnie.komplet(k, "start")) <= {x.id for x in m.przedmioty()} and
             tuple(m.KANON) == tuple(stopnie.komplet(k, "start"))[:len(m.KANON)]
             for k, m in stopnie.MODULY.items()))

    # 2. nowe przedmioty
    liczby = {k: [len(stopnie.komplet(k, st)) for st in stopnie.STOPNIE] for k in stopnie.MODULY}
    test("2a po 8 / 8 / 4 przedmiotów na stopień", liczby == {"wojownik": [8, 8, 8], "zwiadowca": [8, 8, 8],
                                                              "mag": [4, 4, 4]}, str(liczby))
    zle, sylwetki = [], []
    for klasa, mod in stopnie.MODULY.items():
        korekty = getattr(mod, "KOREKTY_CHWYTU", None)
        golas = mod.cialo()
        start = stopnie.komplet(klasa, "start")
        for st in stopnie.STOPNIE:
            for i_start, i in zip(start, stopnie.komplet(klasa, st)):
                b, n = po_id[klasa][i_start], po_id[klasa][i]
                ob, on = b.opis(korekty), n.opis(korekty)
                if stopnie.rzecz(i)[2] != stopnie.rzecz(i_start)[2]:
                    zle.append("%s ≠ %s" % (i, i_start))
                for pole in ("slot", "kategoria", "cialo", "klasy", "ukrywa"):
                    if ob[pole] != on[pole]:
                        zle.append("%s: %s" % (i, pole))
                if [(c["kosc"], c["zakrywa"], c["zaczep"]) for c in ob["czesci"]] != \
                        [(c["kosc"], c["zakrywa"], c["zaczep"]) for c in on["czesci"]]:
                    zle.append("%s: segmenty" % i)
                if bool(b.czesc_od) != bool(n.czesc_od) or (n.czesc_od and n.czesc_od not in po_id[klasa]):
                    zle.append("%s: czesc_od" % i)
                try:
                    u = ubierz(golas, [n], korekty=korekty)
                    bledy, _ = u.sprawdz()
                    if bledy:
                        zle.append("%s: %s" % (i, bledy[0]))
                except Exception as e:                            # noqa: BLE001
                    zle.append("%s: %s" % (i, e))
        for r in ("helm", "zbroja", "miecz", "kaptur", "kurtka", "sztylet", "kapelusz", "szata", "kostur"):
            ids = [i for st in stopnie.WSZYSTKIE_STOPNIE for i in stopnie.komplet(klasa, st)
                   if stopnie.rzecz(i)[2] == r]
            if ids:
                ob = [obrys(po_id[klasa][i].ikona().czesci) for i in ids]
                sylwetki.append((r, ob))
                if len(set(ob)) != len(ob):
                    zle.append("%s: ta sama skrzynka sylwetki w dwóch stopniach %s" % (r, ob))
    test("2b sloty, kości, powłoki i ukrywanie jak w odpowiedniku startowym; każdy przedmiot zakłada się sam",
         not zle, "; ".join(zle[:6]))
    test("2c sylwetka hełmu, napierśnika i broni inna w każdym stopniu (skrzynka brył)", len(sylwetki) == 9
         and all(len(set(o)) == 4 for _, o in sylwetki),
         "; ".join("%s %s" % (r, "→".join("×".join(str(v) for v in o) for o in ob)) for r, ob in sylwetki[:3]))
    bledy = 0
    for a, b in (("wojownik", "mag"), ("mag", "zwiadowca")):
        try:
            ubierz(stopnie.MODULY[b].cialo(), [po_id[a][stopnie.komplet(a, "las")[1]]])
        except ValueError:
            bledy += 1
    try:
        ubierz(stopnie.MODULY["wojownik"].cialo(), [po_id["wojownik"]["rycerz_zbroja"],
                                                    po_id["wojownik"]["rycerz_bagno_zbroja"]])
    except ValueError:
        bledy += 1
    test("2d obce ciało i dwie powłoki na jednej kości dają błąd", bledy == 3, "%d z 3" % bledy)

    # 3. przenikanie kompletów w spoczynku
    wszystko_ok = True
    for klasa in stopnie.MODULY:
        baza = None
        for st in stopnie.WSZYSTKIE_STOPNIE:
            p = stopnie.postac(klasa, st, po_id[klasa])
            a, b = przenikanie(p)
            if st == "start":
                baza = (a[0], b[0])
            ok_a = a[0] <= max(PROG_BRONI, baza[0] + 0.005)
            ok_b = b[0] <= baza[1] + ZAPAS_ZBROI
            wszystko_ok = wszystko_ok and ok_a and ok_b
            wiersze_md.append("| %s | %s | %.2f | %s | %.2f | %s | %s |" % (
                klasa, st, a[0], ("%s w %s" % a[1:]) if a[0] else "—", b[0], ("%s w %s" % b[1:]) if b[0] else "—",
                "tak" if ok_a and ok_b else "NIE"))
            print("      %-10s %-8s w dłoni/na głowie %.2f%s · zbroja między kośćmi %.2f%s%s" % (
                klasa, st, a[0], (" (%s w %s)" % a[1:]) if a[0] > PROG_BRONI else "", b[0],
                (" (%s w %s)" % b[1:]) if b[0] > baza[1] + 1e-9 else "", "" if ok_a and ok_b else "  <-- ZA GŁĘBOKO"))
    test("3 przenikanie kompletów w spoczynku nie gorsze niż progi", wszystko_ok)

    # 4. katalog
    try:
        swiezy = sklep_katalog.tekst(sklep_katalog.zbierz())
        zapisany = open(sklep_katalog.WYNIK, encoding="utf-8").read()
        test("4a sklep_przedmioty.json aktualny", swiezy == zapisany)
    except Exception as e:                                        # noqa: BLE001
        test("4a sklep_przedmioty.json aktualny", False, str(e))
    K = sklep_katalog.wczytaj()
    znane = {s[0] for s in K["statystyki"]}
    zle = []
    for klasa, opis in K["klasy"].items():
        sloty_startu = None
        poprz = {}
        for st in stopnie.WSZYSTKIE_STOPNIE:
            wpisy = [p for p in K["przedmioty"] if p["klasa"] == klasa and p["stopien"] == st]
            if [p["id"] for p in wpisy] != opis["komplety"][st]:
                zle.append("%s %s: komplet" % (klasa, st))
            sprzed = {p["slot"]: p for p in wpisy if p["sprzedawany"]}
            if len(sprzed) != sum(1 for p in wpisy if p["sprzedawany"]):
                zle.append("%s %s: dwa przedmioty w jednym slocie" % (klasa, st))
            sloty_startu = sloty_startu or set(sprzed)
            if set(sprzed) != sloty_startu:
                zle.append("%s %s: sloty %s" % (klasa, st, sorted(set(sprzed) ^ sloty_startu)))
            for p in wpisy:
                if not p["sprzedawany"]:
                    if "cena" in p or not p["czesc_od"]:
                        zle.append("%s: część z ceną" % p["id"])
                    continue
                if set(p["baza"]) - znane or set(p["krok"]) - znane:
                    zle.append("%s: nieznana statystyka" % p["id"])
                moc = sum(v * (100 if k == "tarcza" else 1) for k, v in p["baza"].items())
                if p["slot"] in poprz:
                    c0, l0, m0 = poprz[p["slot"]]
                    if not (p["cena"] > c0 and p["poziom"] > l0 and moc > m0):
                        zle.append("%s: cena %s→%s, poziom %s→%s, statystyki %s→%s" % (
                            p["id"], c0, p["cena"], l0, p["poziom"], m0, moc))
                poprz[p["slot"]] = (p["cena"], p["poziom"], moc)
    test("4b każdy slot obsadzony w każdym stopniu; cena, poziom i statystyki rosną ze stopniem", not zle,
         "; ".join(zle[:6]))
    ceny = {(k, s["id"]): sum(p["cena"] for p in K["przedmioty"] if p["klasa"] == k and p["stopien"] == s["id"]
                              and p["sprzedawany"]) for k in K["klasy"] for s in K["stopnie"]}
    test("4c komplet stopnia kosztuje tyle samo w każdej klasie",
         all(len({ceny[(k, s["id"])] for k in K["klasy"]}) == 1 for s in K["stopnie"]),
         ", ".join("%s %d" % (s["id"], ceny[("wojownik", s["id"])]) for s in K["stopnie"]))

    if "--md" in argv:
        print("\n| Klasa | Komplet | W dłoni / na głowie → ciało | Gdzie | Zbroja między kośćmi | Gdzie | W progu |")
        print("|---|---|---:|---|---:|---|---|")
        print("\n".join(wiersze_md))
    print("\n%d z %d testów OK" % (sum(WYNIKI), len(WYNIKI)))
    return 0 if all(WYNIKI) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
