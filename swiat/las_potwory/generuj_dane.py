#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generuje moduł Luau swiat/las_potwory/zrodla/DanePotworow.luau z plików lasu (PROJEKT.md rozdz. 2).

    python -B swiat/las_potwory/generuj_dane.py                 # zapisuje zrodla/DanePotworow.luau i drukuje tabelę stref
    python -B swiat/las_potwory/generuj_dane.py --sprawdz       # tylko sprawdza, czy plik jest aktualny (kod 1, gdy nie)
    python -B swiat/las_potwory/generuj_dane.py --wyjscie PLIK  # zapisuje do innego pliku (testy determinizmu)

Wejścia (tylko odczyt): swiat/biom_las/potwory.json, znaczniki.json, uklad.json, czesci.json (rekord „Płyta”),
tools/walka/dane_walki.json (lista przeciwników silnika). Wyjście ma współrzędne ŚWIATA Studio (przeliczenie robi
logika.swiat_z_lasu: świat = (−x, y, −2000 − z)), więc serwer i klient niczego nie przeliczają.

Plik jest deterministyczny: kolejność stref jak w potwory.json (Strażnik na końcu), współrzędne zaokrąglone do 0,01,
długości do 0,001, UTF-8 bez BOM, końce linii LF, bez daty i bez ścieżek. `skrot` = 12 pierwszych znaków SHA-1
kanonicznego JSON czterech struktur: potwory.json, znaczniki.json, uklad.json oraz czwartej, złożonej z tego, co
bierzemy z dwóch dużych plików ({"plyta": rekord Płyty z czesci.json, "przeciwnicy": lista id z dane_walki.json}) —
dzięki temu skrót nie zmienia się, gdy w lesie przybędzie krzak, a zmienia się, gdy zmieni się cokolwiek, co czytamy.

Generator PRZERYWA (kod 2, czytelny komunikat), gdy: potwór nie ma odpowiednika w silniku; węzły albo domy z
znaczniki.json różnią się od potwory.json; poziom poza 1–10; strefa nie mieści swoich grup
(grupy × ((miejsc − 1) × odstepWGrupie + 25) > L); dom jest bliżej niż 35 albo dalej niż 50 od najbliższego węzła;
Płyta w czesci.json nie jest tam, gdzie mówi kontener; teksty zasad nie zawierają liczb, które przepisujemy.

Odczytania (najprostsze; opisane też w UWAGI_S.md):
  • `wezel` domu to numer punktu TRASY (1…n), w którym leży najbliższy węzeł walki; węzły walki to `wezly` z
    znaczniki.json (w z09 trzy place, a nie punkty korytarza);
  • w trasie „tam i z powrotem” (z09) lista `s` domu ma jedną wartość, gdy węzeł leży na końcu trasy (d = 0 albo
    d = Lp — wtedy d i L − d to ten sam punkt pętli parametru);
  • wymiary gatunku = { szer, wys, dł }, a brakujący wymiar poziomy bierzemy z drugiego (wilk ma tylko „dl”).
"""
import hashlib
import json
import math
import os
import re
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
sys.path.insert(0, TU)
import logika  # noqa: E402

LAS = os.path.join(REPO, "swiat", "biom_las")
PLIK_POTWOROW = os.path.join(LAS, "potwory.json")
PLIK_ZNACZNIKOW = os.path.join(LAS, "znaczniki.json")
PLIK_UKLADU = os.path.join(LAS, "uklad.json")
PLIK_CZESCI = os.path.join(LAS, "czesci.json")
PLIK_WALKI = os.path.join(REPO, "tools", "walka", "dane_walki.json")
CEL = os.path.join(TU, "zrodla", "DanePotworow.luau")

# nazwa w potwory.json → id przeciwnika w silniku walki v2 (= klucz aktora prototypu)
GATUNKI = {
    "Leśny Slime": "lesny_slime",
    "Muchomornik": "muchomornik",
    "Cierniowy Wilk": "cierniowy_wilk",
    "Strażnik Gaju": "straznik_lasu",
}
# kolory odmian (swiat/krzywe_miasteczko/paleta.py)
KOLORY_PALETY = {"zloto": "F2B030"}
ODMIANY = {"Bursztynowy Slime": "bursztynowy"}

STRAZNIK_NA_POLUDNIE = 12      # studs od osi filara (miejsce z potwory.json) na posadzkę Kręgu (+z lasu = południe)
STRAZNIK_ODRODZENIE_S = 120    # wartość testowa (rozdz. 2.3)
STRAZNIK_R = 30                # promień Kręgu = strefa spokoju „krag”
PRZEDPOLE = 6                  # studs od węzła w stronę domu (= Stale.PRZEDPOLE)
ZASIEG_GRACZY_PONAD_R = 50     # zasiegGraczy = r + 50 (rozdz. 3.5)
DOM_OD = 35
DOM_DO = 50
ODSTEP_W_GRUPIE_ZAPAS = 5      # odstepWGrupie = max(szer, dl) + 5
PLYTA_GRUPA = "Workspace/BiomLas/Teren/Grunt"
PLYTA_NAZWA = "Płyta"

IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class Blad(Exception):
    pass


# --------------------------------------------------------------------------------------------- wczytanie
def _json(sciezka):
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def wczytaj():
    potwory = _json(PLIK_POTWOROW)
    znaczniki = _json(PLIK_ZNACZNIKOW)
    uklad = _json(PLIK_UKLADU)
    czesci = _json(PLIK_CZESCI)
    walka = _json(PLIK_WALKI)
    if not czesci.get("czesci"):
        raise Blad("czesci.json nie ma listy „czesci”")
    plyta = czesci["czesci"][0]
    grupa = czesci["grupy"][plyta[1]] if 0 <= plyta[1] < len(czesci["grupy"]) else "?"
    if plyta[14] != PLYTA_NAZWA or grupa != PLYTA_GRUPA:
        raise Blad("pierwsza część czesci.json to „%s” w %s, a miała być „%s” w %s" % (plyta[14], grupa, PLYTA_NAZWA, PLYTA_GRUPA))
    przeciwnicy = [p["id"] for p in walka["przeciwnicy"]]
    return {"potwory": potwory, "znaczniki": znaczniki, "uklad": uklad,
            "male": {"plyta": plyta, "przeciwnicy": przeciwnicy}}


def skrot(wej):
    tekst = json.dumps([wej["potwory"], wej["znaczniki"], wej["uklad"], wej["male"]],
                       sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha1(tekst.encode("utf-8")).hexdigest()[:12]


# --------------------------------------------------------------------------------------------- liczby
def k2(v):
    """Współrzędna: 0,01 (bez ujemnego zera)."""
    v = round(v, 2)
    return 0.0 if v == 0 else v


def k3(v):
    """Długość: 0,001."""
    v = round(v, 3)
    return 0.0 if v == 0 else v


def swiat(x, y, z):
    wx, wy, wz = logika.swiat_z_lasu(x, y, z)
    return k2(wx), k2(wy), k2(wz)


# --------------------------------------------------------------------------------------------- budowa danych
def gatunki(potwory):
    rozm = potwory["rozmiary"]
    pred = potwory["zasady"]["predkosc"]
    wynik = {}
    for nazwa, gid in GATUNKI.items():
        r = rozm.get(nazwa)
        if not r:
            raise Blad("brak rozmiarów potwora „%s” w potwory.json" % nazwa)
        szer = r.get("szer", r.get("dl"))
        dl = r.get("dl", r.get("szer"))
        wys = r["wys"]
        wymiar = max(szer, dl)
        wynik[gid] = {
            "nazwa": nazwa,
            "predkosc": pred.get(nazwa, 0) if gid != "straznik_lasu" else 0,
            "promien": k3(wymiar / 2),
            "wymiary": [szer, wys, dl],
            "odstepWGrupie": k3(wymiar + ODSTEP_W_GRUPIE_ZAPAS) if gid != "straznik_lasu" else 0,
        }
    return wynik


def zasady(potwory):
    z = potwory["zasady"]
    # liczby z opisów słownych — przepisujemy je, ale sprawdzamy, że tekst wciąż je zawiera
    for pole, wzor in (("walke_zaczyna", "promieniu 8"), ("skracanie", "najmniej 10 s"), ("skracanie", "0,15")):
        if wzor not in z.get(pole, ""):
            raise Blad("zasady.%s nie zawiera „%s” — sprawdź, czy liczba się nie zmieniła" % (pole, wzor))
    return {"odstep": z["odstep_min"], "smycz": z["smycz"], "blokadaDomu": z["blokada_domu"],
            "zasiegE": 8, "minOdrodzenia": 10, "skracanie": 0.15}


def wariant(st):
    w = st.get("wariant")
    if not w:
        return False
    nazwa = w.split(" (")[0].strip()
    if nazwa not in ODMIANY:
        raise Blad("strefa %s: nieznana odmiana „%s”" % (st["id"], w))
    m = re.search(r"kolor (\w+)", w)
    if not m or m.group(1) not in KOLORY_PALETY:
        raise Blad("strefa %s: odmiana „%s” bez znanego koloru palety" % (st["id"], w))
    return {"id": ODMIANY[nazwa], "nazwa": nazwa, "kolor": KOLORY_PALETY[m.group(1)]}


def dlugosci(pts, zamknieta):
    dl = [0.0]
    n = len(pts)
    ile = n if zamknieta else n - 1
    for i in range(ile):
        a, b = pts[i], pts[(i + 1) % n]
        dl.append(dl[-1] + math.hypot(b[0] - a[0], b[2] - a[2]))
    return dl


def strefa(st, zn, korytarz, gat, zas):
    sid = st["id"]
    if st["potwor"] not in GATUNKI:
        raise Blad("strefa %s: potwór „%s” nie ma odpowiednika w silniku" % (sid, st["potwor"]))
    gid = GATUNKI[st["potwor"]]
    g = gat[gid]
    p1, p2 = st["poziomy"]
    if not (1 <= p1 <= p2 <= 10):
        raise Blad("strefa %s: poziomy %s poza 1–10" % (sid, st["poziomy"]))
    y = float(st["y"])
    # węzły i domy: znaczniki.json (z wysokością) muszą być takie same jak potwory.json
    if len(zn["wezly"]) != len(st["trasa"]) or any(
            abs(a[0] - b[0]) > 1e-6 or abs(a[2] - b[1]) > 1e-6 or abs(a[1] - y) > 1e-6
            for a, b in zip(zn["wezly"], st["trasa"])):
        raise Blad("strefa %s: węzły w znaczniki.json różnią się od trasy w potwory.json" % sid)
    if len(zn["domy"]) != len(st["dom"]["pts"]) or any(
            abs(a[0] - b[0]) > 1e-6 or abs(a[2] - b[1]) > 1e-6 for a, b in zip(zn["domy"], st["dom"]["pts"])):
        raise Blad("strefa %s: domy w znaczniki.json różnią się od potwory.json" % sid)
    wezly_las = [(w[0], w[1], w[2]) for w in zn["wezly"]]

    # trasa w układzie lasu: pętla po węzłach albo (z09) węzeł 1 → korytarz labiryntu → węzeł 3, tam i z powrotem
    if sid == "z09":
        if len(wezly_las) != 3:
            raise Blad("z09: oczekiwano 3 węzłów (plac wejścia, polanka, plac wyjścia)")
        kor = [(p[0], y, p[1]) for p in korytarz]
        srodek = wezly_las[1]
        if not any(abs(p[0] - srodek[0]) < 1e-6 and abs(p[2] - srodek[2]) < 1e-6 for p in kor):
            raise Blad("z09: węzeł 2 (polanka) nie leży na ścieżce korytarz_labiryntu")
        pts_las = [wezly_las[0]] + kor + [wezly_las[2]]
        zamknieta = False
    else:
        pts_las = wezly_las
        zamknieta = True
    pts = [swiat(*p) for p in pts_las]
    dl = [k3(d) for d in dlugosci(pts, zamknieta)]
    L = dl[-1] if zamknieta else k3(2 * dl[-1])
    trasa = {"x": [p[0] for p in pts], "y": [p[1] for p in pts], "z": [p[2] for p in pts],
             "dl": dl, "L": L, "zamknieta": zamknieta}
    # numer punktu trasy dla każdego węzła walki
    numer = []
    for w in wezly_las:
        for i, p in enumerate(pts_las):
            if abs(p[0] - w[0]) < 1e-9 and abs(p[2] - w[2]) < 1e-9:
                numer.append(i + 1)
                break

    # grupy
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

    # domy → najbliższy węzeł, przedpole, parametry węzła na pętli
    domy = []
    for d in zn["domy"]:
        dx_las, dy_las, dz_las = d
        odl = [math.hypot(dx_las - w[0], dz_las - w[2]) for w in wezly_las]
        k = min(range(len(odl)), key=lambda i: odl[i])
        if odl[k] < DOM_OD or odl[k] > DOM_DO:
            raise Blad("strefa %s: dom (%.1f; %.1f) jest %.1f od najbliższego węzła (ma być %d–%d)" % (
                sid, dx_las, dz_las, odl[k], DOM_OD, DOM_DO))
        wx, wy, wz = swiat(dx_las, dy_las, dz_las)
        nr = numer[k]
        nx, nz = trasa["x"][nr - 1], trasa["z"][nr - 1]
        ux, uz = wx - nx, wz - nz
        u = math.hypot(ux, uz)
        wej = [k2(nx + ux / u * PRZEDPOLE), k2(nz + uz / u * PRZEDPOLE)]
        dw = dl[nr - 1]
        if zamknieta:
            s = [dw]
        else:
            s = [dw] if (dw <= 1e-9 or abs(dw - dl[-1]) <= 1e-9) else [dw, k3(L - dw)]
        domy.append({"x": wx, "y": wy, "z": wz, "wejscie": wej, "wezel": nr, "s": s})

    sx, sy, sz = swiat(st["srodek"][0], y, st["srodek"][1])
    return {
        "id": sid, "podbiom": st["podbiom"], "gatunek": gid, "wariant": wariant(st),
        "poziomy": [p1, p2], "naraz": st["naraz"], "max": st["max"],
        "srodek": [sx, sy, sz], "r": st["r"], "zasiegGraczy": st["r"] + ZASIEG_GRACZY_PONAD_R,
        "grupy": grupy, "miejsc": miejsc, "odstepWGrupie": odstep_w, "watahy": watahy > 0,
        "odrodzenieS": st["odrodzenie_s"], "straznik": False,
        "trasa": trasa, "domy": domy,
    }


def strefa_straznika(potwory, znaczniki):
    p = potwory["straznik"]
    z = znaczniki["straznik"]
    if p["miejsce"] != z["miejsce"] or p["y"] != z["y"] or p["poziom"] != z["poziom"]:
        raise Blad("strażnik: potwory.json i znaczniki.json się różnią")
    poz = p["poziom"]
    if not (1 <= poz <= 10):
        raise Blad("strażnik: poziom %s poza 1–10" % poz)
    x, y, z_ = swiat(p["miejsce"][0], p["y"], p["miejsce"][1] + STRAZNIK_NA_POLUDNIE)
    # twarzą na południe lasu (+z lasu) = −Z świata → yaw 0
    kierunek = logika.yaw(0 - 0, -1)
    return {
        "id": "straznik", "podbiom": "korona", "gatunek": GATUNKI[p["potwor"]], "wariant": False,
        "poziomy": [poz, poz], "naraz": 1, "max": 1,
        "srodek": [x, y, z_], "r": STRAZNIK_R, "zasiegGraczy": 0,
        "grupy": 1, "miejsc": 1, "odstepWGrupie": 0, "watahy": False,
        "odrodzenieS": STRAZNIK_ODRODZENIE_S, "straznik": True,
        "trasa": {"x": [x], "y": [y], "z": [z_], "dl": [0], "L": 0, "zamknieta": True, "yaw": k3(kierunek)},
        "domy": [{"x": x, "y": y, "z": z_, "wejscie": [x, z_], "wezel": 1, "s": [0]}],
    }


def biom(znaczniki, plyta):
    k = znaczniki["kontener"]
    if abs(k["obrot_y"] - 180) > 1e-9 or list(k["srodek_swiata"]) != [0.0, 0.0, -2000.0]:
        raise Blad("kontener BiomLas: obsługujemy tylko środek (0; 0; −2000) i obrót 180° (jest %s, %s)" % (
            k["srodek_swiata"], k["obrot_y"]))
    nazwa = k["nazwa"].split("/")[-1]
    poz = [k2(plyta[2]), k2(plyta[3]), k2(plyta[4])]
    rozm = [k2(plyta[8]), k2(plyta[9]), k2(plyta[10])]
    if abs(poz[0] - k["srodek_swiata"][0]) > 0.5 or abs(poz[2] - k["srodek_swiata"][2]) > 0.5:
        raise Blad("Płyta w czesci.json (%s) nie leży w środku kontenera %s" % (poz, k["srodek_swiata"]))
    if abs(abs(math.degrees(plyta[6])) - 180) > 1:
        raise Blad("Płyta w czesci.json ma obrót Y %.1f°, a kontener 180°" % math.degrees(plyta[6]))
    return {"nazwa": nazwa, "srodek": [0, 0, -2000], "obrotY": 180,
            "plyta": {"sciezka": "Teren/Grunt/" + PLYTA_NAZWA, "pozycja": poz, "rozmiar": rozm}}


def dane(wej):
    potwory, znaczniki, uklad = wej["potwory"], wej["znaczniki"], wej["uklad"]
    silnik = set(wej["male"]["przeciwnicy"])
    for gid in GATUNKI.values():
        if gid not in silnik:
            raise Blad("gatunek %s nie istnieje w tools/walka/dane_walki.json" % gid)
    gat = gatunki(potwory)
    zas = zasady(potwory)
    zn = {s["id"]: s for s in znaczniki["strefy"]}
    korytarz = None
    for sc in uklad["sciezki"]:
        if sc["id"] == "korytarz_labiryntu":
            korytarz = sc["pts"]
    if korytarz is None:
        raise Blad("uklad.json nie ma ścieżki korytarz_labiryntu (trasa z09)")
    strefy = []
    for st in potwory["strefy"]:
        if st["id"] not in zn:
            raise Blad("strefa %s nie ma znaczników w znaczniki.json" % st["id"])
        strefy.append(strefa(st, zn[st["id"]], korytarz, gat, zas))
    strefy.append(strefa_straznika(potwory, znaczniki))
    spokoj = []
    for s in znaczniki["strefy_spokoju"]:
        if "srodek" in s:
            x, _, z = swiat(s["srodek"][0], 0, s["srodek"][1])
            spokoj.append({"id": s["id"], "x": x, "z": z, "r": s["r"]})
    serce = None
    for p in uklad["podbiomy"]:
        if p["id"] == "serce":
            serce = [[swiat(a, 0, b)[0], swiat(a, 0, b)[2]] for a, b in p["wielokat"]]
    if not serce:
        raise Blad("uklad.json nie ma wielokąta Serca Boru")
    pominiete = [p["id"] for p in potwory.get("patrole", [])] + (["troll"] if potwory.get("troll") else [])
    for g in gat.values():
        del g["odstepWGrupie"]   # w module odstęp jest w strefie (rozdz. 2.4)
    return {
        "wersja": 1,
        "skrot": skrot(wej),
        "biom": biom(znaczniki, wej["male"]["plyta"]),
        "zasady": zas,
        "gatunki": gat,
        "strefy": strefy,
        "spokoj": spokoj,
        "serce": serce,
        "pominiete": pominiete,
    }


# --------------------------------------------------------------------------------------------- zapis Luau
NAGLOWEK = """--[[
\tDanePotworow — WYGENEROWANE przez swiat/las_potwory/generuj_dane.py z swiat/biom_las/potwory.json, znaczniki.json,
\tuklad.json i czesci.json (Płyta) oraz tools/walka/dane_walki.json. NIE EDYTUJ RĘCZNIE: zmień pliki lasu i uruchom
\tpython -B swiat/las_potwory/generuj_dane.py (testy i zbuduj.py --sucho sprawdzają, czy ten plik jest aktualny).

\tWspółrzędne są już w układzie ŚWIATA Studio (świat = (−x, y, −2000 − z) z układu lasu). Format: PROJEKT.md rozdz. 2.4.
\tCzytają go SerwerPotworow (wszystko) i KlientPotworow (tylko `gatunki`).
]]
if not game:GetService("RunService"):IsStudio() then
\treturn {}
end
"""


def liczba(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if not math.isfinite(v):
        raise Blad("liczba nieskończona w danych")
    if v == 0:
        return "0"
    if v == math.floor(v) and abs(v) < 2 ** 53:
        return str(int(v))
    return repr(v)


def napis(s):
    wynik = ['"']
    for ch in s:
        if ch == "\\":
            wynik.append("\\\\")
        elif ch == '"':
            wynik.append('\\"')
        elif ch == "\n":
            wynik.append("\\n")
        elif ord(ch) < 32:
            wynik.append("\\%03d" % ord(ch))
        else:
            wynik.append(ch)
    wynik.append('"')
    return "".join(wynik)


def jedna_linia(v):
    if isinstance(v, dict):
        if not v:
            return "{}"
        return "{ " + ", ".join("%s = %s" % (klucz(k), jedna_linia(x)) for k, x in v.items()) + " }"
    if isinstance(v, (list, tuple)):
        if not v:
            return "{}"
        return "{ " + ", ".join(jedna_linia(x) for x in v) + " }"
    if isinstance(v, str):
        return napis(v)
    if v is None:
        raise Blad("null w danych — Luau nie ma odpowiednika w tabeli")
    return liczba(v)


def klucz(k):
    if IDENT.match(k):
        return k
    return "[%s]" % napis(k)


def luau(v, wciecie):
    """Tabela w kolejności pól ze słownika (stała); krótkie tabele w jednej linii."""
    pad = "\t" * wciecie
    krotko = jedna_linia(v)
    if len(krotko) + len(pad) * 4 <= 116 or not isinstance(v, (dict, list, tuple)):
        return krotko
    czesci = []
    if isinstance(v, dict):
        for k, x in v.items():
            czesci.append("%s\t%s = %s," % (pad, klucz(k), luau(x, wciecie + 1)))
    else:
        for x in v:
            czesci.append("%s\t%s," % (pad, luau(x, wciecie + 1)))
    return "{\n" + "\n".join(czesci) + "\n" + pad + "}"


def tekst(d):
    return NAGLOWEK + "\nreturn " + luau(d, 0) + "\n"


# --------------------------------------------------------------------------------------------- tabela stref
def tabela(d):
    wiersze = ["strefa   gatunek          poz.   naraz/max  L       trasa      grupy×miejsca  zapas   okrążenie  "
               "cel G=1/4/8/20   odrodzenie 1/4/8"]
    sumy = [0, 0, 0, 0]
    zas = d["zasady"]
    for st in d["strefy"]:
        g = d["gatunki"][st["gatunek"]]
        L = st["trasa"]["L"]
        zapas = L - st["grupy"] * ((st["miejsc"] - 1) * st["odstepWGrupie"] + zas["odstep"]) if L > 0 else 0
        ok = "%.1f s" % (L / g["predkosc"]) if g["predkosc"] > 0 and L > 0 else "—"
        cele = [logika.cel(st["naraz"], st["max"], G) for G in (1, 4, 8, 20)]
        for i in range(4):
            sumy[i] += cele[i]
        if st["straznik"]:
            odr = "%d s (stałe)" % st["odrodzenieS"]
        else:
            odr = " / ".join("%.1f" % logika.czas_odrodzenia(st["odrodzenieS"], n) for n in (1, 4, 8))
        rodzaj = "stoi" if L == 0 else ("pętla" if st["trasa"]["zamknieta"] else "tam-z-powr.")
        wiersze.append("%-8s %-16s %-6s %-10s %-7.1f %-10s %-14s %-7.1f %-10s %-16s %s" % (
            st["id"], (st["wariant"] or {}).get("nazwa", g["nazwa"]) if st["wariant"] else g["nazwa"],
            "%d–%d" % tuple(st["poziomy"]), "%d / %d" % (st["naraz"], st["max"]), L, rodzaj,
            "%d × %d" % (st["grupy"], st["miejsc"]), zapas, ok, " / ".join(str(c) for c in cele), odr))
    wiersze.append("razem (bez Strażnika): cel G=1/4/8/20 = %s; ze Strażnikiem +1" % " / ".join(
        str(s - 1) for s in sumy))
    return "\n".join(wiersze)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    argv = sys.argv[1:]
    try:
        d = dane(wczytaj())
    except Blad as e:
        print("BŁĄD generatora danych potworów:", e)
        sys.exit(2)
    nowy = tekst(d)
    if "--sprawdz" in argv:
        try:
            with open(CEL, encoding="utf-8", newline="") as f:
                stary = f.read()
        except OSError:
            stary = None
        if stary != nowy:
            print("DanePotworow.luau jest NIEAKTUALNY — uruchom: python -B swiat/las_potwory/generuj_dane.py")
            sys.exit(1)
        print("DanePotworow.luau aktualny (skrót %s)" % d["skrot"])
        return
    cel = CEL
    if "--wyjscie" in argv:
        i = argv.index("--wyjscie")
        if i + 1 >= len(argv):
            print("--wyjscie wymaga ścieżki pliku")
            sys.exit(2)
        cel = os.path.abspath(argv[i + 1])
    os.makedirs(os.path.dirname(cel), exist_ok=True)
    with open(cel, "w", encoding="utf-8", newline="\n") as f:
        f.write(nowy)
    print(tabela(d))
    if cel == CEL:
        print("zapisano", os.path.relpath(CEL, REPO).replace(os.sep, "/"), "(skrót %s)" % d["skrot"])
    else:
        print("zapisano do pliku podanego w --wyjscie (skrót %s)" % d["skrot"])


if __name__ == "__main__":
    main()
