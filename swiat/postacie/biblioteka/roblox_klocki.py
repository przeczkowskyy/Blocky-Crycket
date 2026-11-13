# -*- coding: utf-8 -*-
"""Postać z biblioteki -> rig z KLOCKÓW Roblox (Part, WedgePart, CornerWedgePart + Motor6D) — bez wgrywania czegokolwiek.

Te same dane, z których `blender_postac.py` robi siatki i szkielet, zamieniamy na opis dla Roblox Studio:
- każda kość = niewidzialna część o wymiarach „klocka” kości, połączona z rodzicem przez Motor6D w stawie,
- każda bryła = zwykła część Roblox przyspawana (WeldConstraint) do części swojej kości,
- punkty zaczepienia = obiekty Attachment w częściach kości (orientacje jak w standardzie Roblox),
- klipy = pozy kości próbkowane co klatkę (w Studio powstaje z nich KeyframeSequence).

UKŁADY. Biblioteka: postać patrzy w +Z, lewa strona +X. Roblox: postać patrzy w −Z (LookVector), lewa strona −X.
Rig w Roblox = dane obrócone o 180° wokół pionu:  położenie (x, y, z) -> (−x, y, −z);  obrót BRYŁY (rx, ry, rz) ->
(rx, ry + 180, rz);  obrót POZY i ZACZEPU (rx, ry, rz) -> (−rx, ry, −rz)  (sprzężenie obrotem o 180°).
Układ jest prawoskrętny po obu stronach, więc nic się nie odbija lustrzanie.

Czego klocki NIE oddają: fazowania krawędzi (bryły są ostre), skórowania na dwóch kościach (`skoruj`, np. slime),
kanału skali w klipach. Stożek jest schodkowy (walce), walec i kula o niekołowym przekroju idą przez SpecialMesh.
"""
import math

from .postac import I3, macierz_obrotu, katy_z_macierzy, mnoz, razy_wektor

# kody kształtów części w Studio
BLOK, KULA, WALEC, KLIN, NAROZNIK = 0, 1, 2, 3, 4
# materiał biblioteki -> (materiał Roblox, Reflectance)
MATERIALY_ROBLOX = {
    "zwykly": ("SmoothPlastic", 0.0),
    "matowy": ("SmoothPlastic", 0.0),
    "polysk": ("SmoothPlastic", 0.14),
    "metal": ("Metal", 0.0),
    "swiecacy": ("Neon", 0.0),
    "poswiata": ("Glass", 0.0),
}
Y180 = ((-1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, -1.0))
EPS = 1e-4
# nazwy stawów Motor6D w standardowym R15 (część-dziecko -> nazwa stawu)
STAWY_R15 = {
    "LowerTorso": "Root", "UpperTorso": "Waist", "Head": "Neck",
    "LeftUpperArm": "LeftShoulder", "LeftLowerArm": "LeftElbow", "LeftHand": "LeftWrist",
    "RightUpperArm": "RightShoulder", "RightLowerArm": "RightElbow", "RightHand": "RightWrist",
    "LeftUpperLeg": "LeftHip", "LeftLowerLeg": "LeftKnee", "LeftFoot": "LeftAnkle",
    "RightUpperLeg": "RightHip", "RightLowerLeg": "RightKnee", "RightFoot": "RightAnkle",
}


def _ry(stopnie):
    return macierz_obrotu(0.0, stopnie, 0.0)


def _rz(stopnie):
    return macierz_obrotu(0.0, 0.0, stopnie)


def _rx(stopnie):
    return macierz_obrotu(stopnie, 0.0, 0.0)


# --------------------------------------------------------------------------- rozkład brył na prymitywy Roblox
def _ostroslup(sx, sy, sz, tx, tz, dx, dz):
    """Ostrosłup / klocek ścięty (podstawa sx × sz na dole, góra tx × tz przesunięta o dx, dz) jako klocek środkowy +
    do 4 klinów + do 4 klinów narożnych. Rozkład jest dokładny, gdy góra mieści się w obrysie podstawy.
    Zwraca listę (kształt, (ox, oy, oz), macierz 3×3, (rozmiar części))."""
    hx, hz = sx / 2.0, sz / 2.0
    x0, x1 = dx - tx / 2.0, dx + tx / 2.0                       # zakres góry
    z0, z1 = dz - tz / 2.0, dz + tz / 2.0
    wyn = []
    if tx > EPS and tz > EPS:
        wyn.append((BLOK, (dx, 0.0, dz), I3, (tx, sy, tz)))
    # kliny boczne: pionowa ściana klina (+Z lokalnie) przylega do klocka środkowego
    if tz > EPS and hx - x1 > EPS:                               # strona +X
        g = hx - x1
        wyn.append((KLIN, ((x1 + hx) / 2.0, 0.0, dz), _ry(-90.0), (tz, sy, g)))
    if tz > EPS and x0 + hx > EPS:                               # strona −X
        g = x0 + hx
        wyn.append((KLIN, ((x0 - hx) / 2.0, 0.0, dz), _ry(90.0), (tz, sy, g)))
    if tx > EPS and hz - z1 > EPS:                               # strona +Z
        g = hz - z1
        wyn.append((KLIN, (dx, 0.0, (z1 + hz) / 2.0), _ry(180.0), (tx, sy, g)))
    if tx > EPS and z0 + hz > EPS:                               # strona −Z
        g = z0 + hz
        wyn.append((KLIN, (dx, 0.0, (z0 - hz) / 2.0), I3, (tx, sy, g)))
    # narożniki: wierzchołek klina narożnego (+X, +Y, −Z lokalnie) nad wewnętrznym rogiem
    ex_p, ex_m, ez_p, ez_m = hx - x1, x0 + hx, hz - z1, z0 + hz
    if ex_p > EPS and ez_p > EPS:                                # róg (+X, +Z): obrót 90°, rozmiary zamienione
        wyn.append((NAROZNIK, ((x1 + hx) / 2.0, 0.0, (z1 + hz) / 2.0), _ry(90.0), (ez_p, sy, ex_p)))
    if ex_m > EPS and ez_p > EPS:                                # róg (−X, +Z): bez obrotu
        wyn.append((NAROZNIK, ((x0 - hx) / 2.0, 0.0, (z1 + hz) / 2.0), I3, (ex_m, sy, ez_p)))
    if ex_p > EPS and ez_m > EPS:                                # róg (+X, −Z): obrót 180°
        wyn.append((NAROZNIK, ((x1 + hx) / 2.0, 0.0, (z0 - hz) / 2.0), _ry(180.0), (ex_p, sy, ez_m)))
    if ex_m > EPS and ez_m > EPS:                                # róg (−X, −Z): obrót −90°, rozmiary zamienione
        wyn.append((NAROZNIK, ((x0 - hx) / 2.0, 0.0, (z0 - hz) / 2.0), _ry(-90.0), (ez_m, sy, ex_m)))
    return wyn


def rozloz(c, uwagi=None):
    """Bryła biblioteki (słownik z Postac.json()) -> lista prymitywów Roblox w układzie LOKALNYM bryły:
    (kształt, przesunięcie, macierz obrotu, rozmiar części, siatka), siatka = "" albo nazwa SpecialMesh
    ("Sphere", "Cylinder") dla przekrojów niekołowych."""
    k = c["k"]
    sx, sy, sz = c["s"]
    uwagi = uwagi if uwagi is not None else []
    if k == "blok":
        return [(BLOK, (0.0, 0.0, 0.0), I3, (sx, sy, sz), "")]
    if k == "klin":
        return [(KLIN, (0.0, 0.0, 0.0), I3, (sx, sy, sz), "")]
    if k == "naroznik":
        return [(NAROZNIK, (0.0, 0.0, 0.0), I3, (sx, sy, sz), "")]
    if k == "kula":
        if max(sx, sy, sz) - min(sx, sy, sz) <= 0.06 * max(sx, sy, sz):
            d = (sx + sy + sz) / 3.0
            return [(KULA, (0.0, 0.0, 0.0), I3, (d, d, d), "")]
        return [(BLOK, (0.0, 0.0, 0.0), I3, (sx, sy, sz), "Sphere")]
    if k in ("walec", "stozek"):
        g = float(c.get("gora", 1.0))
        kolowy = abs(sx - sz) <= 0.06 * max(sx, sz)
        # walec Roblox leży wzdłuż lokalnej osi X: obrót Rz(90°) stawia go pionowo; rozmiar = (wysokość, średnica, średnica)
        if k == "walec" or g >= 0.85:
            m = (1.0 + g) / 2.0 if k == "stozek" else 1.0
            if kolowy:
                d = (sx + sz) / 2.0 * m
                return [(WALEC, (0.0, 0.0, 0.0), _rz(90.0), (sy, d, d), "")]
            return [(BLOK, (0.0, 0.0, 0.0), _rz(90.0), (sy, sx * m, sz * m), "Cylinder")]
        n = max(2, min(4, int(round(sy / 0.22))))                 # stożek schodkowy: 2–4 plastry
        wyn = []
        for j in range(n):
            u = (j + 0.5) / n                                     # 0 = dół, 1 = góra
            m = max(0.12, 1.0 - (1.0 - g) * u)
            oy = -sy / 2.0 + sy * u
            if kolowy:
                d = (sx + sz) / 2.0 * m
                wyn.append((WALEC, (0.0, oy, 0.0), _rz(90.0), (sy / n, d, d), ""))
            else:
                wyn.append((BLOK, (0.0, oy, 0.0), _rz(90.0), (sy / n, sx * m, sz * m), "Cylinder"))
        return wyn
    if k == "ostroslup":
        tx, tz = (float(v) for v in c.get("gora", [0.0, 0.0]))
        dx, dz = (float(v) for v in c.get("pg", [0.0, 0.0]))
        hx, hz = sx / 2.0, sz / 2.0
        w_obrysie = (dx - tx / 2.0 >= -hx - EPS and dx + tx / 2.0 <= hx + EPS
                     and dz - tz / 2.0 >= -hz - EPS and dz + tz / 2.0 <= hz + EPS)
        if w_obrysie:
            return [(ks, o, R, s, "") for ks, o, R, s in _ostroslup(sx, sy, sz, tx, tz, dx, dz)]
        odwrotny = (-hx >= dx - tx / 2.0 - EPS and hx <= dx + tx / 2.0 + EPS
                    and -hz >= dz - tz / 2.0 - EPS and hz <= dz + tz / 2.0 + EPS)
        if odwrotny:                                              # góra większa od podstawy: ten sam rozkład do góry nogami
            Rx = _rx(180.0)                                       # (x, y, z) -> (x, −y, −z)
            wyn = []
            for ks, o, R, s in _ostroslup(tx, sy, tz, sx, sz, -dx, dz):
                o2 = razy_wektor(Rx, o)
                wyn.append((ks, (o2[0] + dx, o2[1], o2[2] + dz), mnoz(Rx, R), s, ""))
            return wyn
        uwagi.append("%s: ostrosłup z górą wystającą poza podstawę — uproszczony do klocka" % c["n"])
        return [(BLOK, (dx / 2.0, 0.0, dz / 2.0), I3, ((sx + tx) / 2.0, sy, (sz + tz) / 2.0), "")]
    raise ValueError("nieznany kształt %r" % k)


# --------------------------------------------------------------------------- przejście do układu rigu Roblox
def _poz(p):
    return (-p[0], p[1], -p[2])


def _katy_bryly(R):
    """Macierz obrotu bryły w układzie danych -> kąty (radiany) dla CFrame.fromOrientation w układzie rigu."""
    return tuple(math.radians(v) for v in katy_z_macierzy(mnoz(Y180, R)))


def _katy_pozy(r):
    """Obrót pozy / zaczepu (stopnie, dane) -> radiany w układzie rigu (sprzężenie obrotem o 180° wokół Y)."""
    return (math.radians(-r[0]), math.radians(r[1]), math.radians(-r[2]))


def _z(v, n=4):
    return [round(float(x), n) for x in v]


def _czesci(lista, indeks_kosci, grupa, materialy, uwagi, skad):
    wyn = []
    for c in lista:
        if indeks_kosci[c["kosc"]] == 0:
            # kość bez części w Roblox (korzeń = HumanoidRootPart, HumanoidRootNode): budowniczy nie miałby do czego
            # przyspawać bryły i zniknęłaby bez śladu — lepiej zatrzymać się od razu
            raise ValueError("%s: bryła „%s” na kości %s, która w Roblox nie ma własnej części (korzeń / "
                             "HumanoidRootNode) — przypnij ją do innej kości" % (skad, c["n"], c["kosc"]))
        R0 = macierz_obrotu(*c["r"])
        mat = c["m"] if c["m"] in MATERIALY_ROBLOX else "zwykly"
        if mat not in materialy:
            materialy.append(mat)
        for nr, (ks, o, R, s, siatka) in enumerate(rozloz(c, uwagi)):
            if min(s) < 0.001:
                continue
            p = _poz(tuple(c["p"][i] + razy_wektor(R0, o)[i] for i in range(3)))
            katy = _katy_bryly(mnoz(R0, R))
            nazwa = c["n"] if nr == 0 else "%s %d" % (c["n"], nr + 1)
            # Roblox nie robi części cieńszych niż 0,001 studa; bardzo cienkie zostawiamy, jak są
            wyn.append([indeks_kosci[c["kosc"]], ks, nazwa] + _z(p) + _z(katy, 5) + _z(s) +
                       [c["c"], materialy.index(mat), grupa, siatka])
    return wyn


def rig(p, klipy=None):
    """Postac -> słownik dla budowniczego w Studio (wszystko w układzie rigu Roblox, początek = ziemia pod postacią).

    klipy: {nazwa klipu: {kość: {"obrot": [[rx, ry, rz], …], "przes": [[x, y, z], …]}}} — próbki co klatkę w układzie
    DANYCH (stopnie, studs), np. z blender_probki.py; None = bez animacji.

    Nic nie znika po cichu: bryła (także akcesorium) na kości bez własnej części Roblox (korzeń „Root”, w R15 też
    HumanoidRootNode) to ValueError; zaczepy i kanały klipów na takich kościach są pomijane z wpisem w "uwagi".
    """
    d = p.json()
    s = p.skala
    uwagi = []
    nazwy = [n for n in p.kosci]
    korzen = nazwy[0]                                             # „Root” — w Roblox to HumanoidRootPart
    # R15: HumanoidRootNode nie ma brył ani kluczy — pomijamy go, LowerTorso wisi bezpośrednio na HumanoidRootPart
    pomijane = set()
    if p.typ == "r15" and "HumanoidRootNode" in p.kosci:
        pomijane.add("HumanoidRootNode")
    indeks, kosci = {korzen: 0}, []
    for n in nazwy[1:]:
        if n in pomijane:
            continue
        k = p.kosci[n]
        rodzic = k["rodzic"]
        while rodzic in pomijane:
            rodzic = p.kosci[rodzic]["rodzic"]
        staw = tuple(v * s for v in k["staw"])
        if k["czesc"] is not None:
            srodek = tuple((k["staw"][i] + k["srodek"][i]) * s for i in range(3))
            rozmiar = tuple(v * s for v in k["czesc"])
        else:
            srodek, rozmiar = staw, (0.2, 0.2, 0.2)
        indeks[n] = len(kosci) + 1
        kosci.append([n, indeks[rodzic]] + _z(_poz(staw)) + _z(_poz(srodek)) + _z(rozmiar) +
                     [STAWY_R15.get(n, n) if p.typ == "r15" else n])
    for n in pomijane:
        indeks[n] = 0
    # HumanoidRootPart: w stawie pierwszej kości (biodra / tułów stwora)
    hrp = tuple(kosci[0][2:5]) if kosci else (0.0, 1.0, 0.0)      # już w układzie rigu
    materialy, grupy = [], ["Cialo"]
    czesci = _czesci(d["czesci"], indeks, 0, materialy, uwagi, "Postać %s" % p.id)
    for a in d["akcesoria"]:
        grupy.append(a["id"])
        czesci += _czesci(a["czesci"], indeks, len(grupy) - 1, materialy, uwagi,
                          "Postać %s, akcesorium %s (zaczep %s)" % (p.id, a["id"], a["zaczep"]))
    zaczepy = []
    for z in d["zaczepy"]:
        ki = indeks[z["kosc"]]
        if ki == 0:
            uwagi.append("zaczep %s na kości %s pominięty — ta kość nie ma w Roblox własnej części" % (z["n"], z["kosc"]))
            continue
        srodek = kosci[ki - 1][5:8]
        pz = _poz(z["p"])
        zaczepy.append([z["n"], ki] + _z([pz[i] - srodek[i] for i in range(3)]) + _z(_katy_pozy(z["r"]), 5))
    if d["skora"]:
        uwagi.append("skórowanie na dwóch kościach (%s) — w klockach bryła idzie sztywno za jedną kością"
                     % ", ".join(sorted(d["skora"])))
    wynik = {"id": p.id, "nazwa": p.nazwa, "typ": p.typ, "hrp": _z(hrp), "kosci": kosci, "czesci": czesci,
             "grupy": grupy, "materialy": [list(MATERIALY_ROBLOX[m]) for m in materialy], "zaczepy": zaczepy,
             "klipy": [], "uwagi": uwagi}
    for kl in d["klipy"]:
        pr = (klipy or {}).get(kl["n"])
        if pr is None:
            continue
        if any(kan["typ"] == "skala" for kan in kl["kanaly"]):
            uwagi.append("klip %s: kanał skali pominięty (Motor6D nie skaluje)" % kl["n"])
        bez_czesci = sorted({kan["kosc"] for kan in kl["kanaly"]
                             if kan["typ"] != "skala" and indeks.get(kan["kosc"], 0) == 0})
        if bez_czesci:
            uwagi.append("klip %s: kanały kości %s pominięte — te kości nie mają w Roblox własnej części "
                         "(HumanoidRootPart jest zakotwiczony)" % (kl["n"], ", ".join(bez_czesci)))
        animowane = [n for n in nazwy if n in pr and indeks.get(n, 0) > 0]
        klatki = []
        for f in range(kl["dlugosc"] + 1):
            wiersz = []
            for n in animowane:
                o = pr[n].get("obrot")
                t = pr[n].get("przes")
                o = o[f] if o else (0.0, 0.0, 0.0)
                t = t[f] if t else (0.0, 0.0, 0.0)
                wiersz += _z(_poz(t), 4) + _z(_katy_pozy(o), 4)
            klatki.append(wiersz)
        wynik["klipy"].append({"n": kl["n"], "fps": kl["fps"], "petla": bool(kl["petla"]), "dl": kl["dlugosc"],
                               "kosci": [indeks[n] for n in animowane], "klatki": klatki})
    return wynik


def akcesoria_noszone(p):
    """Akcesoria założone na postać (p.zalozone) jako dane do obiektów Accessory w Roblox: każda bryła w układzie
    PUNKTU ZACZEPIENIA w konwencji Roblox (przód −Z), z poprawką położenia i obrotu z p.zaloz(...).
    Zwraca (lista {"id", "nazwa", "zaczep", "czesci": [[kształt, px, py, pz, rx, ry, rz, sx, sy, sz, kolor, materiał,
    siatka], …]}, lista materiałów [[materiał Roblox, Reflectance], …], uwagi)."""
    materialy, uwagi, wynik = [], [], []
    for akc, zaczep, pos, obrot, _eksport in p.zalozone:
        czesci = []
        for c in akc.czesci_w(macierz_obrotu(*obrot), pos):
            R0 = macierz_obrotu(*c["r"])
            mat = c["m"] if c["m"] in MATERIALY_ROBLOX else "zwykly"
            if mat not in materialy:
                materialy.append(mat)
            for ks, o, R, rozmiar, siatka in rozloz(c, uwagi):
                if min(rozmiar) < 0.001:
                    continue
                pp = _poz(tuple(c["p"][i] + razy_wektor(R0, o)[i] for i in range(3)))
                czesci.append([ks] + _z(pp) + _z(_katy_bryly(mnoz(R0, R)), 5) + _z(rozmiar) +
                              [c["c"], materialy.index(mat), siatka])
        wynik.append({"id": akc.id, "nazwa": akc.nazwa, "zaczep": zaczep, "czesci": czesci})
    return wynik, [list(MATERIALY_ROBLOX[m]) for m in materialy], uwagi


def probki_liniowe(p):
    """Zapas bez Blendera: próbki klipów liczone liniowo między kluczami (Klip.wartosc) — kanciaste, ale bez zależności."""
    wynik = {}
    for kl in p.klipy:
        kosci = {}
        for (kosc, kanal) in kl.kanaly:
            if kanal == "skala":
                continue
            m = p.skala if kanal == "przes" else 1.0
            kosci.setdefault(kosc, {})[kanal] = [[v * m for v in kl.wartosc(kosc, kanal, f)]
                                                 for f in range(kl.dlugosc + 1)]
        wynik[kl.nazwa] = kosci
    return wynik
