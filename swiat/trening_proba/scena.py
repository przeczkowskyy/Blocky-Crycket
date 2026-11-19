# -*- coding: utf-8 -*-
"""Mini-gry Training Center w sceneriach krain (D-108): elementy gier z prostych części (klocki, jak reszta świata; bez
Toolboxa i bez zasobów generowanych) + scenerie z pliku scenerie.json (generuje je scenerie.py).

    python -B swiat/trening_proba/scena.py        # wypisuje liczbę części, obrys i stanowiska

czesci(D) → lista części w układzie świata (środek areny z ustawienia.json + układ lokalny):
    {"n": nazwa, "r": rodzic w kontenerze ("Arena/Sila/Miotacz"), "k": "B" klocek | "C" walec | "K" kula | "W" klin |
     "N" klin narożny, "p": [x, y, z] środek, "s": [x, y, z] rozmiar Roblox, "o": [rx, ry, rz] stopnie (walec: oś już
     w obrocie), "c": kolor hex, "m": materiał, "t": przezroczystość, "kol": CanCollide, "bc": true = bez cienia,
     "napis": {...} SurfaceGui (opcjonalnie)}
czesci_gry(D) → to samo bez scenerii (same elementy gier: podłoże, stanowiska, figury trenerów).

Układ: sześć scenerii w jednym pasie (zachód → wschód: Łąka pod dębem i Polana drwali w Lesie, Grobla i Pomost nad
topielą na Bagnie, Krąg strażnika i Świątynia run w Dżungli), komórka 72 st na grę, podest w środku komórki, kamery
patrzą na północny zachód (−z, −x). Poziom podestów y = 0; na Bagnie pod pomostami jest woda (arena.woda_y).
Nazwy części, które klient animuje lokalnie (ramię miotacza, pięść golema, oczy, strefy, deski grobli, cele stóp, bęben
i pałka trenera, ramię z kłodą, znaki run, kula maga, tory Koniczyn), pochodzą z dane.NAZWY — wygląd wolno zmieniać,
nazw, miejsc i rozmiarów pól gry nie. Figury trenerów stoją w punktach stanowiska.<gra>.trener_npc (do podmiany na
postacie NPC). Części scenerii (grupa „Arena/Dekoracje/<Gra>/…”, bez kolizji) pilnuje dekoracje.kontrola.
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
if not sys.path or sys.path[0] != TU:
    sys.path.insert(0, TU)
import dane as DANE  # noqa: E402
import dekoracje as DEK  # noqa: E402

TUSZ, KREM = "17121F", "FFF6E0"
DREWNO, DREWNO_C = "6B4A2F", "7A5C44"
SKORA = "E8B98A"
# kolor znaku runy w spoczynku (jaśniejszy w czasie świecenia — klient); kształty różne, żeby nie liczyć tylko na kolor
ZNAKI_RUN = {"gora": "2A6FB0", "lewo": "A8382A", "prawo": "2A8A40", "dol": "B88A20"}
PLIK_SCENERII = os.path.join(TU, "scenerie.json")
# podłoże komórki w barwie krainy (Las i Dżungla: grunt na poziomie podestów; Bagno: woda pod pomostami)
GRUNT = {"las": "4E9A3A", "bagno": "4E6E5E", "dzungla": "2E7D3A"}
ZAPAS_SKRAJU = 6.0  # o tyle podłoże skrajnych komórek wychodzi poza pas (miejsce na dalekie sylwety)
# barwy kamienia Dżungli (golem strażnik, ściana run) i drewna Bagna (grobla, pomosty)
KAMIEN_DZ, KAMIEN_DZ_C, KAMIEN_DZ_J = "8E9A82", "667260", "B5BDA3"
DESKA, DESKA_C, PAL = "9C7A4A", "6E5434", "6B5A44"
GOLEM = {"8C8C99": "8E9A82", "9A9AA8": "A3AE94", "A8A8B6": "B5BDA3", "7C7C88": "7F8B74", "6E6E7A": "6F7B66"}


class _Scena:
    def __init__(self, srodek):
        self.c = srodek
        self.lista = []

    def _sw(self, p):
        return [round(self.c[i] + p[i], 4) for i in range(3)]

    def klocek(self, r, n, p, s, c, m="SmoothPlastic", t=0.0, kol=True, o=None, napis=None, swiat=False):
        d = {"n": n, "r": r, "k": "B", "p": p if swiat else self._sw(p), "s": [round(x, 4) for x in s], "c": c, "m": m}
        if t:
            d["t"] = t
        if not kol:
            d["kol"] = False
        if o:
            d["o"] = o
        if napis:
            d["napis"] = napis
        self.lista.append(d)
        return d

    def walec(self, r, n, p, dl, sr, c, os_="y", m="SmoothPlastic", t=0.0, kol=True, swiat=False):
        o = {"x": None, "y": [0, 0, 90], "z": [0, 90, 0]}[os_]
        d = self.klocek(r, n, p, [dl, sr, sr], c, m, t, kol, o, swiat=swiat)
        d["k"] = "C"
        return d

    def kula(self, r, n, p, sr, c, m="SmoothPlastic", t=0.0, kol=True):
        d = self.klocek(r, n, p, [sr, sr, sr], c, m, t, kol)
        d["k"] = "K"
        return d


def _obroc(v, kat):
    """Przesunięcie (x, y, z) obrócone o kat stopni wokół osi Y (jak CFrame.Angles(0, kat, 0) w Roblox)."""
    a = math.radians(kat)
    return [round(v[0] * math.cos(a) + v[2] * math.sin(a), 4), v[1], round(-v[0] * math.sin(a) + v[2] * math.cos(a), 4)]


def _postac(S, r, baza, kat, ubranie, spodnie, dodatki=(), kol=True):
    """Postać z klocków (jak miotacz Siły) twarzą do +z, obrócona o kat stopni wokół Y; dodatki: (nazwa, przesunięcie,
    rozmiar, kolor[, materiał]) w tym samym układzie postaci."""
    czesci = [("NogaL", [-0.6, 1.3, 0], [1, 2.6, 1], spodnie), ("NogaP", [0.6, 1.3, 0], [1, 2.6, 1], spodnie),
              ("Tulow", [0, 4.1, 0], [3, 3, 1.6], ubranie), ("Glowa", [0, 6.6, 0], [2, 2, 2], SKORA),
              ("OkoL", [-0.45, 6.75, 1.02], [0.3, 0.4, 0.05], TUSZ), ("OkoP", [0.45, 6.75, 1.02], [0.3, 0.4, 0.05], TUSZ),
              ("Usmiech", [0, 6.15, 1.02], [0.9, 0.15, 0.05], TUSZ), ("RamieL", [-2, 4.3, 0], [1, 2.8, 1], ubranie),
              ("RamieP", [2, 4.3, 0], [1, 2.8, 1], ubranie)]
    for d in dodatki:
        czesci.append(d)
    for c in czesci:
        n, v, s, kolor = c[0], c[1], c[2], c[3]
        m = c[4] if len(c) > 4 else "SmoothPlastic"
        S.klocek(r, n, _plus(baza, _obroc(v, kat)), s, kolor, m=m, kol=kol and n in ("NogaL", "NogaP", "Tulow"),
                 o=[0, kat, 0] if kat else None)


def _napis(tekst, strona="Back", px=40, kolor=TUSZ):
    return {"tekst": tekst, "strona": strona, "px": px, "kolor": kolor}


def _plus(a, b):
    return [a[i] + b[i] for i in range(3)]


def komorki(K):
    """Komórki pasa scenerii w układzie areny: [(gra, kraina, x0, x1, z0, z1)] od zachodu."""
    A, SC = K["arena"], K["scenerie"]
    pol = A["komorka"] / 2.0
    wynik = []
    for g in SC["kolejnosc"]:
        pd = K["stanowiska"][g]["podest"]
        wynik.append((g, SC[g]["kraina"], pd[0] - pol, pd[0] + pol, pd[2] + A["polnoc"], pd[2] + A["poludnie"]))
    return wynik


def czesci_gry(D):
    """Elementy gier bez scenerii: podłoże komórek, niewidzialne ściany pasa, sześć stanowisk z figurami trenerów."""
    K = DANE._czytaj_json(DANE.USTAWIENIA)
    A = K["arena"]
    S = _Scena(A["srodek"])
    kolory = {s["id"]: s["kolor"] for s in D["statystyki"]}
    st_k = {s["id"]: s for s in D["statystyki"]}
    woda = A["woda_y"]
    KM = komorki(K)

    # --- podłoże: jedna płyta na komórkę (kolizja — na niej stoi postać i w nią trafia promień serwera przy wejściu);
    #     Bagno: tafla wody poniżej pomostów. Cztery niewidzialne ściany wokół całego pasa.
    for i, (g, kraina, x0, x1, z0, z1) in enumerate(KM):
        if i == 0:
            x0 -= ZAPAS_SKRAJU
        if i == len(KM) - 1:
            x1 += ZAPAS_SKRAJU
        gora = woda if kraina == "bagno" else 0.0
        S.klocek("Arena/Podloga", "Plyta_" + g, [(x0 + x1) / 2, gora - 1, (z0 + z1) / 2], [x1 - x0, 2, z1 - z0], GRUNT[kraina])
    x0, x1, z0, z1 = KM[0][2] - ZAPAS_SKRAJU, KM[-1][3] + ZAPAS_SKRAJU, KM[0][4], KM[0][5]
    for n, p, s in [("ScianaN", [(x0 + x1) / 2, 6, z0 - 0.5], [x1 - x0 + 2, 16, 1]), ("ScianaS", [(x0 + x1) / 2, 6, z1 + 0.5], [x1 - x0 + 2, 16, 1]),
                    ("ScianaW", [x0 - 0.5, 6, (z0 + z1) / 2], [1, 16, z1 - z0]), ("ScianaE", [x1 + 0.5, 6, (z0 + z1) / 2], [1, 16, z1 - z0])]:
        S.klocek("Arena/Mury", n, p, s, KREM, t=1.0)

    def szyld(r, srodek, wys, gid, szer=10, dol=0.0, slupek=DREWNO, m="Wood"):
        """Szyld z nazwą gry na dwóch słupkach (dol < 0: słupki wchodzą w wodę)."""
        for i, dx in enumerate((-szer / 2 - 0.2, szer / 2 + 0.2)):
            S.klocek(r, "Slupek%d" % (i + 1), _plus(srodek, [dx, (wys + dol) / 2, 0]), [0.5, wys - dol, 0.5], slupek, m=m)
        S.klocek(r, "Deska", _plus(srodek, [0, wys, 0]), [szer, 2, 0.4], KREM,
                 napis=_napis("%s — %s" % (st_k[gid]["nazwa"].upper(), st_k[gid]["gra"].upper())))

    def trener(gid):
        T = K["stanowiska"][gid]["trener_npc"]
        return _plus(K["stanowiska"][gid]["podest"], T["miejsce"]), T["obrot_y"], T["figura"]

    def podest(r, pd, gid, sloj, m, sr=6.0):
        """Miejsce gracza: krążek w barwie statystyki z wkładką w barwie scenerii (płaski, bez wpływu na grę)."""
        S.walec(r, "Podest", _plus(pd, [0, 0.1, 0]), 0.2, sr, kolory[gid])
        S.walec(r, "PodestSloj", _plus(pd, [0, 0.115, 0]), 0.21, sr - 1.0, sloj, m=m, kol=False)

    # --- Siła „Rozbijanie” — Polana drwali (Las): pień-podest, strefy ciosu, miotacz przy skrzyniach z dyniami, szyld
    st = K["stanowiska"]["sila"]
    pd = st["podest"]
    podest("Arena/Sila", pd, "sila", "D9A066", "Wood")
    for k, v in st["strefy"].items():
        S.walec("Arena/Sila/Strefy", k, _plus(pd, v), 0.15, 1.8, KREM, os_="z", m="Neon", t=0.7, kol=False)
    m, kat, r = trener("sila")
    S.walec(r, "Mata", _plus(m, [0, 0.1, 0]), 0.2, 5, "B98A5A", m="Wood")
    DEK.figura(S, r, m, kat, "F28C28", "4A4E69", buty=DREWNO, rekaw=SKORA, cale_ramie_p=True, dodatki=[
        ("Fartuch", [0, 3.6, 0.86], [2.4, 2.2, 0.12], DREWNO), ("Opaska", [0, 7.3, 0], [2.7, 0.45, 2.5], "3DBE5A"),
        ("Wezel", [0.9, 7.2, -1.4], [0.7, 0.5, 0.4], "3DBE5A", "SmoothPlastic", 25),
        ("Wasy", [0, 6.12, 1.3], [1.5, 0.28, 0.12], "6B3A1F"), ("Karwasz", [-2.05, 3.5, 0], [1.15, 0.7, 1.15], DREWNO)])
    for i, (p, s, c) in enumerate([([3.8, 0.8, -0.6], 1.6, "B07A45"), ([5.5, 0.8, -0.2], 1.6, "A8703E")]):
        S.klocek("Arena/Sila/Skrzynie", "Skrzynia%d" % (i + 1), _plus(m, p), [s, s, s], c, m="WoodPlanks")
    for i, (p, sr) in enumerate([([3.8, 2.3, -0.6], 1.45), ([5.5, 2.25, -0.2], 1.3), ([4.8, 0.6, 1.3], 1.2)]):
        S.kula("Arena/Sila/Skrzynie", "Dynia%d" % (i + 1), _plus(m, p), sr, "F08A24")
        S.klocek("Arena/Sila/Skrzynie", "Ogonek%d" % (i + 1), _plus(m, [p[0], p[1] + sr / 2 + 0.1, p[2]]), [0.3, 0.4, 0.3], "3F8F35", kol=False)
    for i, dx in enumerate((-5.2, 5.2)):
        S.klocek("Arena/Sila/Szyld", "Slupek%d" % (i + 1), _plus(m, [dx, 5.2, -1.5]), [0.5, 10.4, 0.5], DREWNO, m="Wood")
    S.klocek("Arena/Sila/Szyld", "Deska", _plus(m, [0, 10.5, -1.5]), [10, 2, 0.4], KREM,
             napis=_napis("%s — %s" % (st_k["sila"]["nazwa"].upper(), st_k["sila"]["gra"].upper())))

    # --- Pancerz „Blok” — Krąg strażnika (Dżungla): kamienny podest, omszały golem z pięścią w rękawicy, szyld
    st = K["stanowiska"]["pancerz"]
    pd = st["podest"]
    podest("Arena/Pancerz", pd, "pancerz", KAMIEN_DZ_J, "Slate")
    g = _plus(pd, st["golem"])
    r = "Arena/Pancerz/Golem"
    n0 = len(S.lista)
    S.walec(r, "Mata", _plus(g, [0, 0.1, 0]), 0.2, 7, KAMIEN_DZ_C, m="Slate")
    for n, p, s, c, extra in [("NogaL", [-1.4, 1.5, 0], [2, 3, 2], "8C8C99", {}), ("NogaP", [1.4, 1.5, 0], [2, 3, 2], "8C8C99", {}),
                              ("Tulow", [0, 5, 0], [5, 4, 3], "9A9AA8", {}), ("Pas", [0, 3.2, 0], [5.2, 0.6, 3.2], "3E7D2E", {}),
                              ("Glowa", [0, 8.2, 0.2], [3, 2.4, 2.6], "A8A8B6", {}),
                              ("OkoL", [-0.7, 8.4, 1.53], [0.6, 0.4, 0.06], "3DA5FF", {"m": "Neon", "kol": False}),
                              ("OkoP", [0.7, 8.4, 1.53], [0.6, 0.4, 0.06], "3DA5FF", {"m": "Neon", "kol": False}),
                              ("RamieL", [-3.3, 5.2, 0], [1.6, 3.6, 1.6], "8C8C99", {}),
                              ("PiescL", [-3.3, 3, 0.3], [2, 2, 2], "9A9AA8", {}),
                              ("RamieP", [3.3, 6, 0], [1.6, 2.4, 1.6], "8C8C99", {})]:
        S.klocek(r, n, _plus(g, p), s, c, m=extra.get("m", "Slate"), kol=extra.get("kol", True))
    S.klocek(r, "Piesc", _plus(g, st["piesc_spoczynek"]), [2.4, 2.4, 2.4], "E5533D", kol=False)
    DEK.golem_dodatki(S, r, g)
    for c in S.lista[n0:]:  # kamień w barwach ruin Dżungli (pięść, oczy, mech i złota klamra — bez zmian)
        c["c"] = GOLEM.get(c["c"], c["c"])
    for i, dx in enumerate((-5.2, 5.2)):
        S.klocek("Arena/Pancerz/Szyld", "Slupek%d" % (i + 1), _plus(g, [dx, 6.2, -2.5]), [0.7, 12.4, 0.7], KAMIEN_DZ, m="Slate")
    S.klocek("Arena/Pancerz/Szyld", "Deska", _plus(g, [0, 12.5, -2.5]), [10, 2, 0.4], KREM,
             napis=_napis("%s — %s" % (st_k["pancerz"]["nazwa"].upper(), st_k["pancerz"]["gra"].upper())))
    tn, kat, _ = trener("pancerz")  # punkt trenera bez figury: płaska kamienna płyta (miejsce dla postaci NPC)
    S.walec("Arena/Pancerz", "MiejsceTrenera", _plus(tn, [0, 0.08, 0]), 0.16, 3.6, KAMIEN_DZ_J, m="Slate", kol=False)

    # --- Kondycja „Bieżnia” — Grobla przez Bagno: biegacz twarzą do kamery na grobli z bali; deski (dawne pasy taśmy)
    #     przesuwa klient, ślady stóp jadą od przodu do linii przed palcami; poręcze z żerdzi, z boku pomost trenera z bębnem
    st = K["stanowiska"]["kondycja"]
    pd = st["podest"]
    r = "Arena/Kondycja"
    ts, tr = _plus(pd, st["tasma_srodek"]), st["tasma_rozmiar"]
    S.klocek(r + "/Tasma", "Plyta", ts, tr, "3E2F24", m="WoodPlanks")
    z0, z1 = ts[2] - tr[2] / 2, ts[2] + tr[2] / 2
    gora_t = ts[1] + tr[1] / 2
    for i in range(st["pasy"]):
        z = z0 + (i + 0.5) * tr[2] / st["pasy"]
        S.klocek(r + "/Tasma", "Pas%d" % (i + 1), [ts[0], gora_t + 0.02, z], [tr[0] - 0.3, 0.05, 0.35], "5E4936", kol=False)
    for n, dx in (("BokL", -tr[0] / 2 - 0.3), ("BokP", tr[0] / 2 + 0.3)):
        S.klocek(r + "/Rama", n, [ts[0] + dx, 0.5, ts[2]], [0.6, 1.0, tr[2] + 0.4], DESKA_C, m="Wood")
        S.klocek(r + "/Rama", n.replace("Bok", "Lina"), [ts[0] + dx, 1.04, ts[2]], [0.3, 0.1, tr[2] + 0.4], kolory["kondycja"], kol=False)
    for n, z in (("WalekP", z1 + 0.2), ("WalekT", z0 - 0.2)):
        S.walec(r + "/Rama", n, [ts[0], 0.5, z], tr[0], 1.0, "8C5A3C", os_="x", m="Wood")
    for i, (dx, z) in enumerate([(sx * (tr[0] / 2 + 0.3), zz) for zz in (z0 + 1.5, ts[2], z1 - 1.5) for sx in (-1, 1)]):
        S.walec(r + "/Pale", "Pal%d" % (i + 1), [ts[0] + dx, (woda - 1 + 0.2) / 2, z], 1.2 - woda, 0.9, PAL, m="Wood", kol=False)
    li = _plus(pd, st["linia"])
    S.klocek(r, "Linia", [li[0], gora_t + 0.03, li[2]], [tr[0] - 0.4, 0.05, 0.25], KREM, m="Neon", kol=False)
    for k, v in st["stopy"].items():
        p = _plus(pd, v)
        S.klocek(r + "/Prowadnice", k, [p[0], gora_t + 0.025, (z1 - 0.4 + p[2]) / 2], [0.12, 0.05, z1 - 0.4 - p[2]],
                 KREM, t=0.55, kol=False)
        S.walec(r + "/Cele", k, [p[0], gora_t + 0.04, p[2]], 0.06, 1.4, KREM, os_="y", m="Neon", t=0.55, kol=False)
    for n, dx in (("SlupekL", -tr[0] / 2 - 0.3), ("SlupekP", tr[0] / 2 + 0.3)):
        S.klocek(r + "/Porecze", n, _plus(pd, [dx, 2.1, 1.6]), [0.4, 3.0, 0.4], DESKA_C, m="Wood")
        S.klocek(r + "/Porecze", n.replace("Slupek", "Drazek"), _plus(pd, [dx, 3.5, -0.2]), [0.35, 0.35, 3.6], "B59A52", m="Wood")
    szyld(r + "/Szyld", [ts[0], 0, z0 - 1.0], 4.6, "kondycja", 10, dol=woda - 1, slupek=PAL)
    tn, kat, rt = trener("kondycja")
    bb = _plus(pd, st["beben"])
    px0 = ts[0] + tr[0] / 2 + 0.6  # pomost trenera przylega do grobli od wschodu
    S.klocek(r + "/Pomost", "Deski", [px0 + 3.5, -0.25, (tn[2] + bb[2]) / 2], [7.0, 0.5, 7.6], DESKA, m="WoodPlanks")
    for i, (dx, dz) in enumerate(((0.6, -3.2), (6.4, -3.2), (0.6, 3.2), (6.4, 3.2))):
        S.walec(r + "/Pomost", "Pal%d" % (i + 1), [px0 + dx, (woda - 1 + 0.4) / 2, (tn[2] + bb[2]) / 2 + dz],
                1.4 - woda, 0.8, PAL, m="Wood", kol=False)
    DEK.figura(S, rt, tn, kat, "2E8B57", "264653", buty=KREM, rekaw=SKORA, pas="F2B630", cale_ramie_p=True,
               dodatki=[("Opaska", [0, 7.3, 0], [2.7, 0.45, 2.5], "F2B630"), ("Czub", [0, 7.95, 0], [2.3, 0.5, 2.2], TUSZ),
                        ("Sznurek", [0.2, 5.0, 0.84], [0.1, 1.0, 0.08], TUSZ, "SmoothPlastic", 20),
                        ("Gwizdek", [0.4, 4.5, 0.9], [0.45, 0.35, 0.3], "D8DEE9"),
                        ("PasKoszulki", [0, 4.6, 0.82], [3.02, 0.5, 0.06], KREM),
                        ("Spodenki", [0, 2.2, 0], [2.5, 0.7, 1.3], "264653")])
    S.walec(rt, "BebenKorpus", _plus(bb, [0, 2.0, 0]), 1.3, 2.0, "E5533D")
    S.walec(rt, "Beben", _plus(bb, [0, 2.7, 0]), 0.08, 2.05, KREM, kol=False)
    for i, (dx, dz) in enumerate(((-0.7, -0.4), (0.7, -0.4), (0, 0.8))):
        S.klocek(rt, "NogaBebna%d" % (i + 1), _plus(bb, [dx, 0.7, dz]), [0.2, 1.4, 0.2], DREWNO)

    # --- Zręczność „Kłody” — Pomost nad topielą (Bagno): okrągły pomost na palach, pal cumowniczy, ramię z kłodą
    #     (obraca klient), drwal na bocznym pomoście
    st = K["stanowiska"]["zrecznosc"]
    pd = st["podest"]
    r = "Arena/Zrecznosc"
    sl = _plus(pd, st["slup"])
    sr_placu = 2 * st["ramie"] + 3
    S.walec(r, "Plac", [sl[0], (woda - 0.3 + 0.16) / 2, sl[2]], 0.16 - (woda - 0.3), sr_placu, DESKA, m="WoodPlanks")
    S.walec(r, "Obrecz", [sl[0], -0.35, sl[2]], 0.5, sr_placu + 1.0, DESKA_C, m="Wood", kol=False)
    S.walec(r, "Podest", _plus(pd, [0, 0.18, 0]), 0.2, 4.6, kolory["zrecznosc"])
    S.walec(r + "/Slup", "Pal", [sl[0], 3.6, sl[2]], 7.2, 1.2, PAL, m="Wood")
    S.kula(r + "/Slup", "Czapa", [sl[0], 7.3, sl[2]], 1.6, "C8E05A", m="Neon")
    h = st["wysokosci"]["nisko"]
    sr = st["kloda_srednica"]
    dl = st["ramie"] - 0.6
    S.walec(r + "/Ramie", "Piasta", [sl[0], h, sl[2]], 0.9, 1.9, "9AA0A8", m="Metal", kol=False)
    S.walec(r + "/Ramie", "Kloda", [sl[0] - 0.6 - dl / 2, h, sl[2]], dl, sr, "7A5A3C", os_="x", m="Wood", kol=False)
    for i, rr in enumerate((3.0, 6.0, st["ramie"] - 0.5)):
        S.walec(r + "/Ramie", "Pas%d" % (i + 1), [sl[0] - rr, h, sl[2]], 0.28, sr + 0.1, "F2B630", os_="x", kol=False)
    S.walec(r + "/Ramie", "Koniec", [sl[0] - st["ramie"] - 0.03, h, sl[2]], 0.06, sr - 0.3, "C48A52", os_="x", kol=False)
    szyld(r + "/Szyld", [sl[0], 0, sl[2] - st["ramie"] - 2.2], 7.6, "zrecznosc", dol=woda - 1, slupek=PAL)
    tn, kat, rt = trener("zrecznosc")
    S.walec(r + "/Pomost", "Deski", [tn[0], (woda - 0.3 + 0.1) / 2, tn[2]], 0.1 - (woda - 0.3), 6.4, DESKA, m="WoodPlanks")
    DEK.figura(S, rt, tn, kat, "C0392B", "264653", buty=DREWNO, dodatki=[
        ("Broda", [0, 5.75, 1.15], [2.2, 1.1, 0.4], "6B3A1F"), ("Czapka", [0, 7.95, 0], [2.7, 0.5, 2.5], "C0392B"),
        ("Pompon", [0, 8.45, 0], [0.7, 0.5, 0.7], KREM), ("Daszek", [0, 7.75, 1.5], [2.2, 0.2, 0.7], "8E2A20"),
        ("Krata1", [0, 4.8, 0.82], [3.02, 0.2, 0.05], TUSZ), ("Krata2", [0, 3.6, 0.82], [3.02, 0.2, 0.05], TUSZ),
        ("Krata3", [-0.7, 4.05, 0.82], [0.2, 2.7, 0.05], TUSZ), ("Krata4", [0.7, 4.05, 0.82], [0.2, 2.7, 0.05], TUSZ),
        ("Szelka1", [-1.2, 4.2, 0.86], [0.35, 2.6, 0.06], "264653"), ("Szelka2", [1.2, 4.2, 0.86], [0.35, 2.6, 0.06], "264653"),
        ("Stylisko", [2.3, 2.4, 0.9], [0.25, 3.6, 0.25], DREWNO), ("Ostrze", [2.3, 4.2, 1.25], [0.15, 0.9, 0.9], "D8DEE9", "Metal")])

    # --- Inteligencja „Runy” — Świątynia run (Dżungla): ściana świątyni, cztery kamienne tablice w krzyżu ze znakami
    #     (kolor + kształt), mag
    st = K["stanowiska"]["inteligencja"]
    pd = st["podest"]
    r = "Arena/Inteligencja"
    podest(r, pd, "inteligencja", KAMIEN_DZ_J, "Slate")
    sc, sr_ = _plus(pd, st["sciana"]), st["sciana_rozmiar"]
    S.klocek(r + "/Luk", "Sciana", sc, sr_, KAMIEN_DZ_C, m="Slate")
    for n, dx in (("KolumnaL", -sr_[0] / 2 - 0.5), ("KolumnaP", sr_[0] / 2 + 0.5)):
        S.klocek(r + "/Luk", n, [sc[0] + dx, sr_[1] / 2 + 0.3, sc[2]], [1.0, sr_[1] + 0.6, 1.2], KAMIEN_DZ, m="Slate")
    S.klocek(r + "/Luk", "Belka", [sc[0], sr_[1] + 0.9, sc[2]], [sr_[0] + 2.2, 0.8, 1.3], KAMIEN_DZ, m="Slate")
    S.klocek(r + "/Luk", "Deska", [sc[0], sr_[1] + 2.2, sc[2] + 0.2], [10, 1.8, 0.4], KREM,
             napis=_napis("%s — %s" % (st_k["inteligencja"]["nazwa"].upper(), st_k["inteligencja"]["gra"].upper())))
    ks = st["kamien_rozmiar"]
    for k, v in st["kamienie"].items():
        p = _plus(pd, v)
        rk = r + "/Runy/" + k
        S.klocek(rk, "Kamien", p, ks, KAMIEN_DZ_J, m="Slate")
        zf = p[2] + ks[2] / 2 + 0.03
        c = ZNAKI_RUN[k]
        if k == "gora":  # pierścień
            S.walec(rk, "Znak1", [p[0], p[1], zf], 0.06, 1.8, c, os_="z", kol=False)
            S.walec(rk, "Srodek", [p[0], p[1], zf + 0.02], 0.06, 1.05, KAMIEN_DZ_J, os_="z", kol=False)
        elif k == "lewo":  # kwadrat
            for i, (dx, dy, sx, sy) in enumerate(((0, 0.7, 1.7, 0.32), (0, -0.7, 1.7, 0.32), (-0.7, 0, 0.32, 1.7),
                                                  (0.7, 0, 0.32, 1.7))):
                S.klocek(rk, "Znak%d" % (i + 1), [p[0] + dx, p[1] + dy, zf], [sx, sy, 0.06], c, kol=False)
        elif k == "prawo":  # romb
            S.klocek(rk, "Znak1", [p[0], p[1], zf], [1.35, 1.35, 0.06], c, kol=False, o=[0, 0, 45])
            S.klocek(rk, "Srodek", [p[0], p[1], zf + 0.02], [0.72, 0.72, 0.06], KAMIEN_DZ_J, kol=False, o=[0, 0, 45])
        else:  # krzyż
            S.klocek(rk, "Znak1", [p[0], p[1], zf], [1.8, 0.42, 0.06], c, kol=False)
            S.klocek(rk, "Znak2", [p[0], p[1], zf], [0.42, 1.8, 0.06], c, kol=False)
    mg, kat_maga, rt = trener("inteligencja")
    DEK.figura(S, rt, mg, kat_maga, "6C3FB5", "4B2C82", buty="4B2C82", pas="F2B630", dodatki=[
        ("Szata", [0, 1.6, 0], [3.3, 2.2, 1.9], "6C3FB5"), ("Rabek", [0, 0.6, 0], [3.5, 0.3, 2.1], "F2B630"),
        ("Broda", [0, 5.5, 1.2], [1.8, 1.6, 0.4], "F2F2F2"), ("BrodaKoniec", [0, 4.5, 1.2], [1.0, 0.7, 0.35], "F2F2F2"),
        ("Kapelusz1", [0, 7.95, 0], [3.6, 0.4, 3.4], "4B2C82"), ("Kapelusz2", [0, 8.6, 0], [2.2, 0.9, 2.1], "4B2C82"),
        ("Kapelusz3", [0, 9.4, -0.2], [1.4, 0.8, 1.3], "4B2C82"), ("Kapelusz4", [0, 10.1, -0.5], [0.8, 0.7, 0.8], "4B2C82"),
        ("Wstazka", [0, 8.25, 0], [2.3, 0.3, 2.2], "F2B630"), ("Gwiazda", [0, 8.9, 1.08], [0.6, 0.6, 0.08], "F2B630", "Neon", 45),
        ("Laska", [2.4, 3.6, 0.6], [0.3, 7.2, 0.3], DREWNO)])
    S.kula(rt, "Kula", _plus(mg, _plus(_obroc([2.4, 0, 0.6], kat_maga), [0, 7.6, 0])), 0.9, "C9A7FF", m="Neon", kol=False)

    # --- Szczęście „Koniczyny” — Łąka pod dębem (Las): jasna łąka, trzy tory, stary dąb z koroną nad torami, ogrodnik
    st = K["stanowiska"]["szczescie"]
    pd = st["podest"]
    r = "Arena/Szczescie"
    S.klocek(r, "Trawa", _plus(pd, [0, 0.05, -3.5]), [15, 0.1, 13], "8FC04A", kol=False)
    kosz = st["koszyk"]
    for k, v in st["tory"].items():
        S.klocek(r + "/Tory", k, _plus(pd, [v[0], 0.13, kosz[2]]), [2.6, 0.05, 2.6], KREM, t=0.45, kol=False)
    # dąb z tyłu, korona i gałąź nad torami: koniczyny wypadają spod korony nad koszem trzymanym nad głową
    dz = _plus(pd, st["drzewo"])
    wys = st["spad_y"] + 1.6
    S.klocek(r + "/Drzewo", "Pien", _plus(dz, [0, wys / 2, 0]), [2.8, wys, 2.8], "7A5232", m="Wood")
    S.klocek(r + "/Drzewo", "Galaz", [dz[0], wys - 0.4, pd[2] + kosz[2] - 2.4], [13.5, 0.8, 0.8], "7A5232", m="Wood")
    S.klocek(r + "/Drzewo", "Konar", [dz[0], wys - 0.4, (dz[2] + pd[2] + kosz[2] - 2.4) / 2],
             [0.9, 0.9, pd[2] + kosz[2] - 2.4 - dz[2]], "7A5232", m="Wood")
    zp = pd[2] + kosz[2] - dz[2]
    # korona z płatów (jak dęby krain): ciemny spód nad torami, jaśniejsze wierzchy — każdy płat mieści się w dawnej kuli
    for i, (dx, dy, dzz, srn, kolor) in enumerate(((-5.2, 3.2, zp - 3.2, 6.0, "3F8F35"), (0, 3.6, zp - 3.0, 6.6, "3F8F35"),
                                                  (5.2, 3.2, zp - 3.2, 6.0, "3F8F35"), (-2.6, 5.0, zp - 6.0, 6.0, "58A83C"),
                                                  (2.6, 5.0, zp - 6.0, 6.0, "58A83C"), (0, 4.0, 0, 6.4, "72BF3A"))):
        S.klocek(r + "/Drzewo", "Korona%d" % (i + 1), _plus(dz, [dx, wys + dy - 1.2, dzz]), [srn, srn * 0.62, srn * 0.92], kolor)
    for i, dx in enumerate((-4.2, 1.0, 4.6)):
        S.kula(r + "/Drzewo", "Owoc%d" % (i + 1), _plus(dz, [dx, wys + 0.2, zp - 1.0]), 0.7, "F2B630", kol=False)
    for i, (kat_k, dl_k) in enumerate(((35, 3.4), (150, 3.0), (255, 3.2))):  # korzenie dębu (niskie, za torami)
        a = math.radians(kat_k)
        S.klocek(r + "/Drzewo", "Korzen%d" % (i + 1), _plus(dz, [math.cos(a) * (1.2 + dl_k / 2), 0.35, -math.sin(a) * (1.2 + dl_k / 2)]),
                 [dl_k, 0.7, 0.9], "7A5232", m="Wood", o=[0, kat_k, 0], kol=False)
    szyld(r + "/Szyld", _plus(pd, [-9.6, 0, -6.5]), 5.0, "szczescie", 6.2)
    og, kat, rt = trener("szczescie")
    DEK.figura(S, rt, og, kat, "2EC4B6", "6B4A2F", buty="3F8F35", dodatki=[
        ("Fartuch", [0, 3.6, 0.86], [2.4, 2.2, 0.12], "3DBE5A"), ("Kieszen", [0, 3.3, 0.94], [1.2, 0.8, 0.08], "2E9B4A"),
        ("Koniczynka", [0, 4.3, 0.95], [0.5, 0.5, 0.06], KREM, "SmoothPlastic", 45),
        ("Wasy", [0, 6.12, 1.3], [1.4, 0.26, 0.12], "8B5A2E"), ("Denko", [0, 8.25, 0], [1.9, 0.9, 1.8], "E8C872"),
        ("Wstazka", [0, 7.98, 0], [2.0, 0.25, 1.9], "E5392B"), ("Konewka", [2.3, 2.3, 0.9], [1.0, 1.0, 0.8], "9AA0A8", "Metal"),
        ("Dziobek", [2.3, 2.6, 1.6], [0.25, 0.25, 0.9], "9AA0A8", "Metal")])
    S.walec(rt, "Kapelusz", _plus(og, [0, 7.85, 0]), 0.2, 3.8, "E8C872", kol=False)
    return S.lista


_PAMIEC = {}


def czesci_scenerii(D):
    """Części scenerii z scenerie.json (układ areny → świat); brak pliku = pusta lista (pierwsze generowanie)."""
    if not os.path.isfile(PLIK_SCENERII):
        return []
    znak = os.path.getmtime(PLIK_SCENERII)
    if _PAMIEC.get("znak") != znak:
        with open(PLIK_SCENERII, encoding="utf-8") as f:
            _PAMIEC["dane"] = json.load(f)
        _PAMIEC["znak"] = znak
    c0 = D["arena"]["srodek"]
    wynik = []
    for c in _PAMIEC["dane"]["czesci"]:
        d = dict(c)
        d["p"] = [round(c0[i] + c["p"][i], 4) for i in range(3)]
        d["kol"] = False
        wynik.append(d)
    return wynik


def czesci(D):
    """Wszystkie części areny: elementy gier + scenerie krain."""
    return czesci_gry(D) + czesci_scenerii(D)


def pole_gry(D, gra):
    """Punkty świata, które gracz musi widzieć w czasie rundy (pole gry): [x, y, z, opis]. Rzutuje je test telefonu
    (testy/test_treningu.py, 5e) — żaden nie może wpaść pod panel rundy ani przycisk na żadnym z badanych ekranów."""
    W = D["swiat"][gra]
    P = []
    if gra == "sila":
        for k, z in W["strefy"].items():
            for dx, dy in ((-0.9, 0), (0.9, 0), (0, -0.9), (0, 0.9)):
                P.append([z[0] + dx, z[1] + dy, z[2], "strefa " + k])
    elif gra == "pancerz":
        for k in ("piesc_spoczynek", "piesc_zamach", "piesc_cel", "tarcza", "tarcza_blok"):
            P.append(W[k] + [k])
        a, b = W["piesc_zamach"], W["piesc_cel"]
        for i in range(1, 5):
            P.append([a[j] + (b[j] - a[j]) * i / 5 for j in range(3)] + ["cios"])
        g = W["golem"]
        for dx, dy in ((-2.5, 3.2), (2.5, 3.2), (-1.5, 9.4), (1.5, 9.4), (0, 8.4)):
            P.append([g[0] + dx, g[1] + dy, g[2], "golem"])
        pd = W["podest"]
        for y in (0.2, 2.7, 5.4):  # postać z tarczą (kamera z boku: gracz nie może wypaść z kadru)
            P.append([pd[0], pd[1] + y, pd[2], "gracz"])
    elif gra == "kondycja":
        pd = W["podest"]
        gora_t = W["tasma_srodek"][1] + W["tasma_rozmiar"][1] / 2
        for y in (0.2, 2.7, 5.4):  # biegacz na taśmie
            P.append([pd[0], gora_t + y, pd[2], "gracz"])
        for k, p in W["stopy"].items():
            for i in range(9):
                z = p[2] + W["slad_predkosc"] * W["slady_s"] * i / 8
                for dx in (-0.45, 0.45):
                    P.append([p[0] + dx, p[1], z, "slad %s" % k])
    elif gra == "zrecznosc":
        sl, pd = W["slup"], W["podest"]
        for nazwa, h in W["wysokosci"].items():
            for kat in range(90, 181, 10):  # nadlatująca kłoda: ćwierć obrotu przed przejściem (strona podejścia)
                a = math.radians(90 - W["obrot"] * (kat - 90))
                for rr in (4.0, 7.0, W["ramie"]):
                    P.append([sl[0] + math.cos(a) * rr, pd[1] + h, sl[2] + math.sin(a) * rr, "kloda %s" % nazwa])
        for y in (0.2, 2.7, 5.4):
            P.append([pd[0], pd[1] + y, pd[2], "gracz"])
        P.append([pd[0], pd[1] + 5.4 + 2.7, pd[2], "gracz w skoku"])  # głowa w szczycie skoku (niska kamera z bliska)
    elif gra == "inteligencja":
        ks = W["kamien_rozmiar"]
        for k, p in W["kamienie"].items():
            for dx, dy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                P.append([p[0] + dx * ks[0] / 2, p[1] + dy * ks[1] / 2, p[2] + ks[2] / 2, "kamien " + k])
    elif gra == "szczescie":
        pd = W["podest"]
        kosz = [W["koszyk"][i] - pd[i] for i in range(3)]
        for k, p in W["tory"].items():
            y0, y1 = pd[1] + W["spad_y"] + 0.7, p[1] + kosz[1] - 0.6
            for i in range(7):
                y = y0 + (y1 - y0) * i / 6
                for dx in (-0.8, 0.8):
                    P.append([p[0] + dx, y, p[2] + kosz[2], "tor " + k])
            for y in (0.2, 5.4):
                P.append([p[0], p[1] + y, p[2], "postac na torze " + k])
    return P


def obrys(D):
    """(min, max) części areny w świecie (pudła osiowe obróconych części — rozmiar_osiowy)."""
    mn, mx = [1e9] * 3, [-1e9] * 3
    for c in czesci(D):
        s = rozmiar_osiowy(c)
        for i in range(3):
            mn[i] = min(mn[i], c["p"][i] - s[i] / 2)
            mx[i] = max(mx[i], c["p"][i] + s[i] / 2)
    return mn, mx


def macierz(o):
    """Macierz obrotu CFrame.Angles(rx, ry, rz) (stopnie) = Rx · Ry · Rz, jak w Roblox."""
    rx, ry, rz = [math.radians(a) for a in (o or [0, 0, 0])]
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    Rx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    Ry = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    Rz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]

    def mn(A, B):
        return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return mn(mn(Rx, Ry), Rz)


def rozmiar_osiowy(c):
    """Rozmiar pudła osiowego części po obrocie (walec: oś wzdłuż lokalnego X, jak w Roblox)."""
    s = c["s"]
    if not c.get("o"):
        return s
    R = macierz(c["o"])
    return [round(sum(abs(R[i][j]) * s[j] for j in range(3)), 6) for i in range(3)]


if __name__ == "__main__":
    for strumien in (sys.stdout,):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    _, D = DANE.wczytaj()
    cz = czesci(D)
    mn, mx = obrys(D)
    print("części: %d, obrys %s – %s" % (len(cz), [round(x, 1) for x in mn], [round(x, 1) for x in mx]))
