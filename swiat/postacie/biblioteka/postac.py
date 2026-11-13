# -*- coding: utf-8 -*-
"""Postacie, stwory i ekwipunek z brył — opis jako DANE (czysty Python, bez bpy).

Z tego opisu `blender_postac.py` buduje w Blenderze siatki, szkielet i animacje, a `podglad_postaci.py` robi podgląd,
ikony, film i eksport FBX/GLB. Ściąga i fakty Roblox: README.md obok.

    from swiat.postacie.biblioteka.postac import Postac, Akcesorium, manekin_r15

    p = Postac("ludzik", "Ludzik", typ="r15", wymiary={"Head": (1.4, 1.3, 1.3)})
    p.cialo({"glowa": "skora", "tulow": "zielony"})               # 15 klocków ciała
    with p.na("Head", od="srodek"):                                # układ lokalny: środek klocka głowy
        p.blok("Oko L", (0.3, 0.1, 0.68), (0.2, 0.3, 0.1), "tusz", "polysk")
    k = p.klip("machanie", 36)                                     # 36 klatek, 30 kl./s, pętla
    k.poza(0, {"RightUpperArm": (0, 0, -160)})
    k.cykl("RightLowerArm", "obrot", (0, 0, 25), czestosc=2)

KONWENCJE (te same co swiat/biblioteka/scena.py):
- jednostka = stud (1 jednostka Blendera = 1 stud); Y w górę; postać PATRZY W +Z; jej LEWA strona to +X;
- obrót = (rx, ry, rz) w STOPNIACH, kolejność Roblox (CFrame.fromOrientation): R = Ry · Rx · Rz;
- kości w spoczynku mają osie równoległe do osi modelu (X lewo, Y góra, Z przód), więc obrót kości w klipie to
  obrót wokół tych osi zaczepiony w stawie: rx < 0 unosi zwisającą kończynę DO PRZODU, rz > 0 odchyla ją w stronę +X
  (lewa ręka na zewnątrz), ry > 0 skręca przód w stronę +X; dla głowy rx > 0 = skłon w przód;
- części (bryły) są przypięte sztywnie do kości (jedna siatka na kość) i opisane w układzie lokalnym kości: (0, 0, 0)
  to staw (punkt obrotu), osie jak wyżej; `with p.na(kosc, od="srodek")` przenosi początek na środek klocka kości;
- kolory: klucz palety KOLORY (albo własnej) albo „RRGGBB”; materiały: zwykly, matowy, polysk, metal, swiecacy;
- nazwy id, kości, klipów i punktów zaczepienia: ASCII (litery, cyfry, podkreślnik).
"""
import contextlib
import json
import math
import re

WERSJA = 1
_HEX = re.compile(r"^[0-9A-Fa-f]{6}$")
_ASCII = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
I3 = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))

# --------------------------------------------------------------------------- materiały i paleta
# Jeden materiał na siatkę (wymóg Roblox) — różnice między materiałami siedzą w mapach palety (kolor, metaliczność,
# szorstkość, emisja), które blender_postac.py generuje z tych liczb.
MATERIALY = {
    "zwykly": {"szorstkosc": 0.42, "metal": 0.0, "emisja": 0.0},    # plastik z połyskiem (domyślny)
    "matowy": {"szorstkosc": 0.85, "metal": 0.0, "emisja": 0.0},    # tkanina, skóra, drewno
    "polysk": {"szorstkosc": 0.15, "metal": 0.0, "emisja": 0.0},    # oczy, lakier, szkło
    "metal": {"szorstkosc": 0.28, "metal": 0.7, "emisja": 0.0},     # stal, złoto
    "swiecacy": {"szorstkosc": 0.35, "metal": 0.0, "emisja": 1.0},  # kryształy, slime, magia
    "poswiata": {"szorstkosc": 0.2, "metal": 0.0, "emisja": 0.6},   # lekka poświata (skorupka slime'a)
}

# Wspólna paleta stylu (żywe, nasycone kolory z obrazu referencyjnego). Własne kolory: „RRGGBB” albo paleta=... w modelu.
KOLORY = {
    "tusz": "1B1625", "bialy": "F4F1EA", "oko": "1B1625",
    "skora": "F5C9A0", "skora_cien": "D9A27A", "rumieniec": "F08F8F",
    "stal": "B9C3D0", "stal_cien": "7F8A9A", "stal_ciemna": "566070",
    "zloto": "F2C230", "zloto_ciemne": "C38E1C",
    "niebieski": "2F6FDB", "niebieski_ciemny": "1F4A9E", "niebieski_jasny": "6FA2F2",
    "fiolet": "7E3FC9", "fiolet_ciemny": "55289A", "fiolet_jasny": "B57CFF",
    "pomarancz": "F08C2A", "pomarancz_jasny": "FFC27A", "pomarancz_ciemny": "C4621A",
    "brazowy": "8B5A2B", "brazowy_ciemny": "5E3A1A", "brazowy_jasny": "B57E47",
    "czerwony": "D7382C", "czerwony_ciemny": "9E2219",
    "zielony": "4FB443", "zielony_ciemny": "2F7A2C",
    "turkus": "3FE7E2", "turkus_ciemny": "1BB4C6",
    "szary": "A3A8B3", "szary_ciemny": "6B7180",
}

# --------------------------------------------------------------------------- Roblox R15
R15_KOSCI = ("LowerTorso", "UpperTorso", "Head",
             "LeftUpperArm", "LeftLowerArm", "LeftHand", "RightUpperArm", "RightLowerArm", "RightHand",
             "LeftUpperLeg", "LeftLowerLeg", "LeftFoot", "RightUpperLeg", "RightLowerLeg", "RightFoot")
# Wymiary klocków klockowego R15 (studs; szer X × wys Y × głęb Z). Razem ok. 5,25 studa wzrostu, nogi 2,0, tułów 2,0.
R15_WYMIARY = {
    "Head": (1.25, 1.25, 1.25), "UpperTorso": (2.0, 1.6, 1.0), "LowerTorso": (2.0, 0.4, 1.0),
    "UpperArm": (1.0, 0.95, 1.0), "LowerArm": (1.0, 0.75, 1.0), "Hand": (1.0, 0.3, 1.0),
    "UpperLeg": (1.0, 0.85, 1.0), "LowerLeg": (1.0, 0.8, 1.0), "Foot": (1.0, 0.35, 1.0),
}
# Grupy kolorów dla Postac.cialo().
GRUPY_CIALA = {
    "glowa": ("Head",), "tulow": ("UpperTorso",), "pas": ("LowerTorso",),
    "ramiona": ("LeftUpperArm", "RightUpperArm", "LeftLowerArm", "RightLowerArm"),
    "dlonie": ("LeftHand", "RightHand"),
    "nogi": ("LeftUpperLeg", "RightUpperLeg", "LeftLowerLeg", "RightLowerLeg"),
    "stopy": ("LeftFoot", "RightFoot"),
}

# Limity z dokumentacji Roblox (create.roblox.com, sprawdzone 13.11.2026) — źródła w README.md.
LIMITY = {
    "trojkaty_siatka": 20000,                  # zwykły MeshPart
    "trojkaty_akcesorium": 4000,               # sztywne akcesorium
    "trojkaty_cialo": {"Head": 4000, "Torso": 1750, "LeftArm": 1248, "RightArm": 1248, "LeftLeg": 1248, "RightLeg": 1248},
    "trojkaty_cialo_razem": 10742,
    "grupy_ciala": {"Head": ["Head"], "Torso": ["UpperTorso", "LowerTorso"],
                    "LeftArm": ["LeftUpperArm", "LeftLowerArm", "LeftHand"],
                    "RightArm": ["RightUpperArm", "RightLowerArm", "RightHand"],
                    "LeftLeg": ["LeftUpperLeg", "LeftLowerLeg", "LeftFoot"],
                    "RightLeg": ["RightUpperLeg", "RightLowerLeg", "RightFoot"]},
    # (min szer, wys, głęb), (max szer, wys, głęb) w studach
    "wymiary_ciala": {"Head": [[0.05, 0.5, 0.05], [4.0, 2.0, 4.0]], "Torso": [[0.05, 0.65, 0.05], [4.0, 4.0, 4.0]],
                      "Arm": [[0.05, 0.5, 0.05], [4.0, 4.5, 4.0]], "Leg": [[0.05, 0.5, 0.05], [4.0, 4.5, 4.0]],
                      "Razem": [[1.0, 4.0, 0.5], [8.0, 10.0, 4.0]]},
    "wplywy_kosci": 4,
    "tekstura_bezpieczna": 1024,
    "emote_max_s": 10.0,
}
# Pudełka rozmiaru akcesoriów skali Classic (studs), liczone od punktu zaczepienia: [min x, min y, min z], [max ...].
# Przód = +Z (konwencja tej biblioteki). Asymetryczne pudełka (Hair, Back, Waist) wg tabeli Roblox.
TYPY_AKCESORIOW = {
    "Hat": {"zaczepy": ["HatAttachment"], "pudlo": [[-1.5, -2.0, -1.5], [1.5, 2.0, 1.5]]},
    "Hair": {"zaczepy": ["HairAttachment"], "pudlo": [[-1.5, -3.0, -2.0], [1.5, 2.0, 1.5]]},
    "Face": {"zaczepy": ["FaceFrontAttachment", "FaceCenterAttachment"], "pudlo": [[-1.5, -1.0, -1.0], [1.5, 1.0, 1.0]]},
    "Neck": {"zaczepy": ["NeckAttachment"], "pudlo": [[-1.5, -1.5, -1.0], [1.5, 1.5, 1.0]]},
    "Shoulder": {"zaczepy": ["LeftShoulderAttachment", "RightShoulderAttachment", "LeftCollarAttachment",
                             "RightCollarAttachment"], "pudlo": [[-1.5, -1.5, -1.5], [1.5, 1.5, 1.5]]},
    "Front": {"zaczepy": ["BodyFrontAttachment"], "pudlo": [[-1.5, -1.5, -1.5], [1.5, 1.5, 1.5]]},
    "Back": {"zaczepy": ["BodyBackAttachment"], "pudlo": [[-5.0, -3.5, -3.0], [5.0, 3.5, 1.5]]},
    "Waist": {"zaczepy": ["WaistCenterAttachment", "WaistFrontAttachment", "WaistBackAttachment"],
              "pudlo": [[-2.0, -2.0, -3.5], [2.0, 1.5, 3.5]]},
    "Bron": {"zaczepy": ["RightGripAttachment", "LeftGripAttachment"], "pudlo": None},   # Tool/gear: bez pudełka
    "Inne": {"zaczepy": [], "pudlo": None},
}

KSZTALTY = ("blok", "klin", "naroznik", "walec", "stozek", "kula", "ostroslup")
KANALY = ("obrot", "przes", "skala")
WYGLADZANIA = ("gladko", "liniowo", "stale")


# --------------------------------------------------------------------------- matematyka (jak swiat/biblioteka/scena.py)
def mnoz(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def razy_wektor(m, v):
    return tuple(m[i][0] * v[0] + m[i][1] * v[1] + m[i][2] * v[2] for i in range(3))


def macierz_obrotu(rx, ry, rz):
    """Macierz 3×3 dla obrotu (rx, ry, rz) w stopniach: R = Ry · Rx · Rz (jak CFrame.fromOrientation)."""
    x, y, z = math.radians(rx), math.radians(ry), math.radians(rz)
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    return ((cy * cz + sy * sx * sz, -cy * sz + sy * sx * cz, sy * cx),
            (cx * sz, cx * cz, -sx),
            (-sy * cz + cy * sx * sz, sy * sz + cy * sx * cz, cy * cx))


def katy_z_macierzy(m):
    """Odwrotność macierz_obrotu: (rx, ry, rz) w stopniach."""
    sx = max(-1.0, min(1.0, -m[1][2]))
    rx = math.asin(sx)
    if abs(sx) > 0.999999:
        ry, rz = math.atan2(-m[2][0], m[0][0]), 0.0
    else:
        ry, rz = math.atan2(m[0][2], m[2][2]), math.atan2(m[1][0], m[1][1])
    return math.degrees(rx), math.degrees(ry), math.degrees(rz)


def _trzy(v, co="wartość"):
    if isinstance(v, (int, float)):
        return (float(v),) * 3
    v = tuple(float(x) for x in v)
    if len(v) != 3:
        raise ValueError("%s musi mieć 3 liczby, jest %r" % (co, v))
    return v


def _dodaj(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _razy(v, s):
    return (v[0] * s, v[1] * s, v[2] * s)


def _zaokr(v, n=4):
    return [round(float(x), n) for x in v]


def _sprawdz_id(nazwa, co="id"):
    if not isinstance(nazwa, str) or not _ASCII.match(nazwa):
        raise ValueError("Nazwa %s %r: tylko litery ASCII, cyfry i „_”, zaczyna się literą" % (co, nazwa))
    return nazwa


def kolor_hex(kolor, paleta=None):
    k = (paleta or {}).get(kolor, KOLORY.get(kolor, kolor))
    k = str(k).lstrip("#")
    if not _HEX.match(k):
        raise ValueError("Nieznany kolor %r — użyj klucza palety (KOLORY) albo „RRGGBB”" % (kolor,))
    return k.upper()


def nazwa_att(zaczep):
    """HatAttachment -> Hat_Att (nazwa siatki-znacznika, którą importer Roblox zamienia na Attachment)."""
    return (zaczep[:-len("Attachment")] if zaczep.endswith("Attachment") else zaczep) + "_Att"


def pudelko(czesci):
    """Skrzynka obejmująca części (z obrotami) — przybliżenie bez fazowania: ((min x,y,z), (max x,y,z)) albo None."""
    mn, mx = [1e9] * 3, [-1e9] * 3
    for c in czesci:
        R = macierz_obrotu(*c["r"])
        for i in range(3):
            pol = (abs(R[i][0]) * c["s"][0] + abs(R[i][1]) * c["s"][1] + abs(R[i][2]) * c["s"][2]) / 2.0
            mn[i] = min(mn[i], c["p"][i] - pol)
            mx[i] = max(mx[i], c["p"][i] + pol)
    return (tuple(mn), tuple(mx)) if czesci else None


# --------------------------------------------------------------------------- bryły (wspólne dla postaci i akcesoriów)
class _Bryly:
    def __init__(self, faza=0.05, paleta=None):
        self.faza = float(faza)               # domyślne fazowanie krawędzi (studs); 0 = ostre krawędzie
        self.paleta = dict(paleta or {})
        self.czesci = []
        self._stos = [(I3, (0.0, 0.0, 0.0), 1.0)]
        self._kosc = [None]

    @contextlib.contextmanager
    def uklad(self, pos=(0.0, 0.0, 0.0), obrot=(0.0, 0.0, 0.0), skala=1.0):
        """Układ lokalny (zagnieżdżalny): to, co w środku, jest skalowane, obracane i przesuwane jak w scena.py."""
        R, t, s = self._stos[-1]
        nt = _dodaj(t, _razy(razy_wektor(R, _trzy(pos, "pos")), s))
        self._stos.append((mnoz(R, macierz_obrotu(*_trzy(obrot, "obrot"))), nt, s * float(skala)))
        try:
            yield self
        finally:
            self._stos.pop()

    def _wymagana_kosc(self):
        return None

    def _dodaj(self, ksztalt, nazwa, pos, size, kolor, mat, rot, faza, **dodatki):
        if mat not in MATERIALY:
            raise ValueError("Nieznany materiał %r (są: %s)" % (mat, ", ".join(MATERIALY)))
        kosc = self._wymagana_kosc()
        R, t, s = self._stos[-1]
        size = _trzy(size, "size")
        if min(size) <= 0:
            raise ValueError("Część %r: rozmiar musi być dodatni, jest %r" % (nazwa, size))
        p = _dodaj(t, _razy(razy_wektor(R, _trzy(pos, "pos")), s))
        r = katy_z_macierzy(mnoz(R, macierz_obrotu(*_trzy(rot, "rot"))))
        c = {"k": ksztalt, "n": str(nazwa)[:40], "kosc": kosc, "p": p, "r": r, "s": _razy(size, s),
             "c": kolor_hex(kolor, self.paleta), "m": mat, "f": (self.faza if faza is None else float(faza)) * s}
        for klucz, wartosc in dodatki.items():
            c[klucz] = wartosc(s) if callable(wartosc) else wartosc
        self.czesci.append(c)
        return c

    # --- prymitywy: pos = ŚRODEK skrzynki części w bieżącym układzie, size = (szer X, wys Y, głęb Z)
    def blok(self, nazwa, pos, size, kolor, mat="zwykly", rot=(0, 0, 0), faza=None):
        """Prostopadłościan."""
        return self._dodaj("blok", nazwa, pos, size, kolor, mat, rot, faza)

    def klin(self, nazwa, pos, size, kolor, mat="zwykly", rot=(0, 0, 0), faza=None):
        """Klin jak WedgePart: wysoka pionowa ściana po stronie +Z, skos opada ku −Z."""
        return self._dodaj("klin", nazwa, pos, size, kolor, mat, rot, faza)

    def naroznik(self, nazwa, pos, size, kolor, mat="zwykly", rot=(0, 0, 0), faza=None):
        """Klin narożny jak CornerWedgePart: wierzchołek w rogu (+X, +Y, −Z)."""
        return self._dodaj("naroznik", nazwa, pos, size, kolor, mat, rot, faza)

    def walec(self, nazwa, pos, size, kolor, mat="zwykly", rot=(0, 0, 0), faza=None, segm=8):
        """Walec STOJĄCY (oś wzdłuż Y): size = (średnica X, wysokość Y, średnica Z). segm = liczba ścian bocznych
        (wielokrotność 4 trzyma dokładny rozmiar; 8 = klockowy, 12–16 = okrąglejszy). Leżący: rot=(0, 0, 90)."""
        return self._dodaj("walec", nazwa, pos, size, kolor, mat, rot, faza, seg=int(segm), gora=1.0)

    def stozek(self, nazwa, pos, size, kolor, mat="zwykly", rot=(0, 0, 0), gora=0.0, segm=8, faza=None):
        """Stożek (ścięty) stojący na podstawie: gora = promień góry jako ułamek podstawy (0 = szpic, 1 = walec)."""
        return self._dodaj("stozek", nazwa, pos, size, kolor, mat, rot, faza, seg=int(segm), gora=float(gora))

    def kula(self, nazwa, pos, size, kolor, mat="zwykly", rot=(0, 0, 0), segm=8):
        """Kula / elipsoida low-poly: size = średnica albo (sx, sy, sz); segm = podział (8 = klockowo)."""
        return self._dodaj("kula", nazwa, pos, size, kolor, mat, rot, 0.0, seg=int(segm))

    def ostroslup(self, nazwa, pos, size, kolor, mat="zwykly", rot=(0, 0, 0), gora=(0.0, 0.0), przes_gory=(0.0, 0.0),
                  faza=None):
        """Ostrosłup / klocek ścięty o prostokątnych przekrojach: podstawa size X × Z na dole skrzynki, góra = prostokąt
        gora=(szer X, głęb Z) w studach (0, 0 = szpic; (0, z) albo (x, 0) = grzbiet), przesunięty o przes_gory=(dx, dz)
        — krzywy szpic kapelusza, klinga, ucho."""
        g, pg = (float(gora[0]), float(gora[1])), (float(przes_gory[0]), float(przes_gory[1]))
        return self._dodaj("ostroslup", nazwa, pos, size, kolor, mat, rot, faza,
                           gora=lambda s: [g[0] * s, g[1] * s], pg=lambda s: [pg[0] * s, pg[1] * s])

    @staticmethod
    def _czesc_w(c, R0, t0, s0=1.0):
        """Kopia części przeniesiona układem (R0, t0) ze skalą s0 (bez zmiany kości)."""
        d = dict(c)
        d["p"] = _dodaj(t0, razy_wektor(R0, _razy(c["p"], s0)))
        d["r"] = katy_z_macierzy(mnoz(R0, macierz_obrotu(*c["r"])))
        d["s"] = _razy(c["s"], s0)
        d["f"] = c["f"] * s0
        if "gora" in c and isinstance(c["gora"], list):
            d["gora"] = [c["gora"][0] * s0, c["gora"][1] * s0]
        if "pg" in c:
            d["pg"] = [c["pg"][0] * s0, c["pg"][1] * s0]
        return d

    @staticmethod
    def _czesc_json(c):
        d = {"k": c["k"], "n": c["n"], "kosc": c["kosc"], "p": _zaokr(c["p"]), "r": _zaokr(c["r"], 3),
             "s": _zaokr(c["s"]), "c": c["c"], "m": c["m"], "f": round(c["f"], 4)}
        for klucz in ("seg", "gora", "pg"):
            if klucz in c:
                d[klucz] = _zaokr(c[klucz]) if isinstance(c[klucz], list) else c[klucz]
        return d


# --------------------------------------------------------------------------- akcesorium (sztywny model na zaczepie)
class Akcesorium(_Bryly):
    """Sztywne akcesorium (hełm, kapelusz, peleryna, miecz, kostur…) — JEDNA siatka, modelowana w układzie punktu
    zaczepienia: (0, 0, 0) = punkt zaczepienia, osie jak w ramce zaczepu (dla HatAttachment: Y góra, Z przód).
    Broń (zaczep RightGripAttachment/LeftGripAttachment): rękojeść w (0, 0, 0), ostrze w +Y, płaz do przodu (+Z) —
    gdy ręka zwisa, ostrze celuje do przodu; gdy przedramię uniesione do przodu (rx = −90), ostrze sterczy w górę."""

    rodzaj = "akcesorium"

    def __init__(self, id, nazwa, zaczep="HatAttachment", typ=None, skala=1.0, faza=0.05, paleta=None,
                 ikona_obrot=(0, 0, 0), chwyt=None, przymierz=True):
        """chwyt="drzewce" — broń długa (kostur, włócznia): w chodzie przymiarki stoi pionowo (przedramię −80°).
        przymierz=False — przedmiot tylko do ikony i eksportu, nie zakładany na przymiarkę (np. sygnet)."""
        super().__init__(faza, paleta)
        self.chwyt, self.przymierz = chwyt, bool(przymierz)
        self.id, self.nazwa, self.zaczep = _sprawdz_id(id), str(nazwa), _sprawdz_id(zaczep, "zaczepu")
        if typ is None:
            typ = next((t for t, o in TYPY_AKCESORIOW.items() if zaczep in o["zaczepy"]), "Inne")
        if typ not in TYPY_AKCESORIOW:
            raise ValueError("Nieznany typ akcesorium %r (są: %s)" % (typ, ", ".join(TYPY_AKCESORIOW)))
        self.typ, self.skala, self.ikona_obrot = typ, float(skala), _trzy(ikona_obrot, "ikona_obrot")

    def czesci_w(self, R0=I3, t0=(0.0, 0.0, 0.0)):
        """Części przeniesione z układu zaczepu do układu (R0, t0), z własną skalą akcesorium."""
        return [self._czesc_w(c, R0, t0, self.skala) for c in self.czesci]

    def json(self):
        return {"wersja": WERSJA, "rodzaj": "akcesorium", "id": self.id, "nazwa": self.nazwa, "zaczep": self.zaczep,
                "typ": self.typ, "pudlo": TYPY_AKCESORIOW[self.typ]["pudlo"], "ikona_obrot": list(self.ikona_obrot),
                "czesci": [self._czesc_json(c) for c in self.czesci_w()], "materialy": MATERIALY, "limity": LIMITY}

    def sprawdz(self):
        bledy, uwagi = [], []
        if not self.czesci:
            bledy.append("%s: akcesorium bez części" % self.id)
        for c in self.czesci_w():
            if min(c["s"]) < 0.02:
                uwagi.append("%s: część „%s” cieńsza niż 0,02 studa" % (self.id, c["n"]))
        box = TYPY_AKCESORIOW[self.typ]["pudlo"]
        pud = pudelko(self.czesci_w())
        if box and pud:
            for i, os_ in enumerate("XYZ"):
                if pud[0][i] < box[0][i] - 1e-6 or pud[1][i] > box[1][i] + 1e-6:
                    uwagi.append("%s: wystaje poza pudełko typu %s w osi %s (%.2f…%.2f, dozwolone %.2f…%.2f)"
                                 % (self.id, self.typ, os_, pud[0][i], pud[1][i], box[0][i], box[1][i]))
        return bledy, uwagi


# --------------------------------------------------------------------------- postać / stwór
class Postac(_Bryly):
    """Postać R15 (typ="r15": 15 części, kości i zaczepy Roblox) albo stwór (typ="stwor": własne kości).

    wymiary   — tylko r15: zmiany klocków, np. {"Head": (1.6, 1.5, 1.5), "UpperTorso": (2.8, 1.6, 1.8)}; klucze
                ogólne ("UpperArm") albo z bokiem ("RightHand"); stawy liczą się same z wysokości klocków
    rozstaw_nog, rozstaw_rak — x środka nogi / ręki (domyślnie z szerokości tułowia)
    bark      — o ile staw barku leży poniżej górnej krawędzi tułowia (domyślnie 0,25)
    skala     — mnożnik całej postaci (kości, części, zaczepy, przesunięcia w klipach); założone akcesoria zachowują
                własny rozmiar (Akcesorium.skala), zmienia się tylko miejsce zaczepu
    """

    rodzaj = "postac"

    def __init__(self, id, nazwa, typ="r15", skala=1.0, wymiary=None, rozstaw_nog=None, rozstaw_rak=None, bark=None,
                 faza=0.05, paleta=None):
        super().__init__(faza, paleta)
        if typ not in ("r15", "stwor"):
            raise ValueError("typ musi być „r15” albo „stwor”")
        self.id, self.nazwa, self.typ, self.skala = _sprawdz_id(id), str(nazwa), typ, float(skala)
        self.kosci, self.zaczepy, self.zalozone, self.klipy = {}, {}, [], []
        self.poza_renderu = None
        self.skora = {}                                          # kość -> (druga kość, y0, y1): siatka skórowana
        if typ == "r15":
            self._zbuduj_r15(dict(wymiary or {}), rozstaw_nog, rozstaw_rak, bark)
        else:
            if wymiary:
                raise ValueError("wymiary= działa tylko dla r15; stwór dostaje kości przez p.kosc(...)")
            self.kosc("Root", None, (0, 0, 0), dl=0.5)

    # --- szkielet
    def kosc(self, nazwa, rodzic, staw, dl=None, czesc=None, srodek=None):
        """Dodaj albo przestaw kość. staw = (x, y, z) stawu w układzie modelu (spoczynek); rodzic = nazwa kości
        (dla stworów zwykle "Root" albo kość tułowia); czesc = (szer, wys, głęb) „klocka” kości (dla klocek(), srodek(),
        zaczepów); srodek = środek klocka względem stawu (domyślnie (0, 0, 0)); dl = długość kości w Blenderze."""
        _sprawdz_id(nazwa, "kości")
        if rodzic is not None and rodzic not in self.kosci:
            raise ValueError("Kość %s: nieznany rodzic %r (najpierw dodaj rodzica)" % (nazwa, rodzic))
        if czesc is not None:
            czesc = _trzy(czesc, "czesc")
        if dl is None:
            dl = max(0.25, 0.5 * czesc[1]) if czesc else 0.4
        self.kosci[nazwa] = {"rodzic": rodzic, "staw": _trzy(staw, "staw"), "dl": float(dl), "czesc": czesc,
                             "srodek": _trzy(srodek or (0.0, 0.0, 0.0), "srodek")}
        return nazwa

    def wymiary(self, kosc):
        """(szer, wys, głęb) klocka kości."""
        cz = self.kosci[kosc]["czesc"]
        if cz is None:
            raise ValueError("Kość %s nie ma klocka (czesc=None)" % kosc)
        return cz

    def srodek(self, kosc):
        """Środek klocka kości względem jej stawu."""
        return self.kosci[kosc]["srodek"]

    def staw(self, kosc):
        """Położenie stawu w układzie modelu (przed skalą postaci)."""
        return self.kosci[kosc]["staw"]

    def _zbuduj_r15(self, wym, rozstaw_nog, rozstaw_rak, bark):
        for k in wym:
            ogolny = k.replace("Left", "").replace("Right", "")
            if ogolny not in R15_WYMIARY:
                raise ValueError("wymiary: nieznana część %r (są: %s)" % (k, ", ".join(R15_WYMIARY)))

        def w(strona, czesc):
            return _trzy(wym.get(strona + czesc, wym.get(czesc, R15_WYMIARY[czesc])), czesc)

        LT, UT, H = w("", "LowerTorso"), w("", "UpperTorso"), w("", "Head")
        biodro = max(w(s, "UpperLeg")[1] + w(s, "LowerLeg")[1] + w(s, "Foot")[1] for s in ("Left", "Right"))
        pas, szyja = biodro + LT[1], biodro + LT[1] + UT[1]
        self.kosc("Root", None, (0, 0, 0), dl=0.5)
        self.kosc("HumanoidRootNode", "Root", (0, biodro, 0), dl=0.35)
        self.kosc("LowerTorso", "HumanoidRootNode", (0, biodro, 0), czesc=LT, srodek=(0, LT[1] / 2, 0))
        self.kosc("UpperTorso", "LowerTorso", (0, pas, 0), czesc=UT, srodek=(0, UT[1] / 2, 0))
        self.kosc("Head", "UpperTorso", (0, szyja, 0), czesc=H, srodek=(0, H[1] / 2, 0))
        for strona, zn in (("Left", 1.0), ("Right", -1.0)):
            UA, LA, HD = w(strona, "UpperArm"), w(strona, "LowerArm"), w(strona, "Hand")
            UL, LL, F = w(strona, "UpperLeg"), w(strona, "LowerLeg"), w(strona, "Foot")
            xr = zn * (rozstaw_rak if rozstaw_rak is not None else UT[0] / 2 + UA[0] / 2)
            xn = zn * (rozstaw_nog if rozstaw_nog is not None else LT[0] / 4)
            b = bark if bark is not None else min(0.25, UA[1] / 3)
            yb, yl = szyja - b, szyja - UA[1]
            yn = yl - LA[1]
            self.kosc(strona + "UpperArm", "UpperTorso", (xr, yb, 0), czesc=UA, srodek=(0, b - UA[1] / 2, 0))
            self.kosc(strona + "LowerArm", strona + "UpperArm", (xr, yl, 0), czesc=LA, srodek=(0, -LA[1] / 2, 0))
            self.kosc(strona + "Hand", strona + "LowerArm", (xr, yn, 0), czesc=HD, srodek=(0, -HD[1] / 2, 0))
            y_kol, y_kost = biodro - UL[1], F[1] + (biodro - UL[1] - LL[1] - F[1])
            self.kosc(strona + "UpperLeg", "LowerTorso", (xn, biodro, 0), czesc=UL, srodek=(0, -UL[1] / 2, 0))
            self.kosc(strona + "LowerLeg", strona + "UpperLeg", (xn, y_kol, 0), czesc=LL, srodek=(0, -LL[1] / 2, 0))
            self.kosc(strona + "Foot", strona + "LowerLeg", (xn, y_kost, 0), czesc=F,
                      srodek=(0, -F[1] / 2, (F[2] - LL[2]) / 2))
        self._zaczepy_r15()

    def _zaczepy_r15(self):
        """Standardowe punkty zaczepienia R15 (nazwy jak w Roblox Studio), liczone z klocków."""
        def na(kosc, dx=0.0, dy=0.0, dz=0.0, rot=(0, 0, 0), nazwa=None):
            c, (w, h, d) = self.srodek(kosc), self.wymiary(kosc)
            self.zaczepy[nazwa] = {"kosc": kosc, "p": (c[0] + dx * w / 2, c[1] + dy * h / 2, c[2] + dz * d / 2),
                                   "r": _trzy(rot)}
        na("Head", nazwa="FaceCenterAttachment")
        na("Head", dz=1, nazwa="FaceFrontAttachment")
        na("Head", dy=1, nazwa="HatAttachment")
        na("Head", dy=1, nazwa="HairAttachment")
        na("UpperTorso", dy=1, nazwa="NeckAttachment")
        na("UpperTorso", dz=1, nazwa="BodyFrontAttachment")
        na("UpperTorso", dz=-1, nazwa="BodyBackAttachment")
        na("UpperTorso", dx=1, dy=1, nazwa="LeftCollarAttachment")
        na("UpperTorso", dx=-1, dy=1, nazwa="RightCollarAttachment")
        na("LowerTorso", nazwa="WaistCenterAttachment")
        na("LowerTorso", dz=1, nazwa="WaistFrontAttachment")
        na("LowerTorso", dz=-1, nazwa="WaistBackAttachment")
        for s in ("Left", "Right"):
            na(s + "UpperArm", dy=1, nazwa=s + "ShoulderAttachment")
            na(s + "Hand", rot=(90, 0, 0), nazwa=s + "GripAttachment")
            na(s + "Foot", dy=-1, nazwa=s + "FootAttachment")

    def skoruj(self, kosc, gora, y0, y1):
        """Siatka <kosc>_Geo dostaje wagi na DWÓCH kościach zależnie od wysokości wierzchołka (układ modelu, y):
        poniżej y0 waga 1 do `kosc`, powyżej y1 waga 1 do `gora`, pomiędzy liniowo. Przesunięcie kości `gora`
        w klipie zgniata/rozciąga bryłę bez kanału skali (np. slime: y0 = 0, y1 = wysokość → równe zgniecenie)."""
        for k in (kosc, gora):
            if k not in self.kosci:
                raise ValueError("skoruj: nieznana kość %r" % k)
        self.skora[kosc] = (gora, float(y0), float(y1))

    def zaczep(self, nazwa, kosc, pos, rot=(0, 0, 0)):
        """Dodaj albo przestaw punkt zaczepienia: pos względem stawu kości, rot w stopniach."""
        _sprawdz_id(nazwa, "zaczepu")
        if kosc not in self.kosci:
            raise ValueError("Zaczep %s: nieznana kość %r" % (nazwa, kosc))
        self.zaczepy[nazwa] = {"kosc": kosc, "p": _trzy(pos, "pos"), "r": _trzy(rot, "rot")}

    # --- bryły na kościach
    def _wymagana_kosc(self):
        kosc = self._kosc[-1]
        if kosc is None:
            raise ValueError("Postać %s: bryłę dodaj w bloku `with p.na(\"Kosc\"):`" % self.id)
        return kosc

    @contextlib.contextmanager
    def na(self, kosc, pos=(0.0, 0.0, 0.0), obrot=(0.0, 0.0, 0.0), od="staw"):
        """Układ lokalny kości: bryły dodane w środku poruszają się z tą kością. od="staw" — (0, 0, 0) w stawie;
        od="srodek" — (0, 0, 0) w środku klocka kości. pos/obrot przesuwają i obracają ten układ."""
        if kosc not in self.kosci:
            raise ValueError("Nieznana kość %r (są: %s)" % (kosc, ", ".join(self.kosci)))
        if od not in ("staw", "srodek"):
            raise ValueError("od = „staw” albo „srodek”")
        baza = self.srodek(kosc) if od == "srodek" else (0.0, 0.0, 0.0)
        self._kosc.append(kosc)
        self._stos.append((I3, (0.0, 0.0, 0.0), 1.0))
        try:
            with self.uklad(pos=_dodaj(baza, _trzy(pos, "pos")), obrot=obrot):
                yield self
        finally:
            self._stos.pop()
            self._kosc.pop()

    def klocek(self, kosc, kolor, mat="zwykly", faza=None, powieksz=(0, 0, 0), przesun=(0, 0, 0), nazwa=None):
        """Klocek o wymiarach części kości (+ powieksz) w jej środku (+ przesun)."""
        w = self.wymiary(kosc)
        with self.na(kosc, pos=przesun, od="srodek"):
            return self.blok(nazwa or kosc, (0, 0, 0), _dodaj(w, _trzy(powieksz, "powieksz")), kolor, mat, faza=faza)

    def cialo(self, kolory=None, mat="zwykly", faza=None):
        """Klocki wszystkich kości, które mają wymiary. kolory: {kość albo grupa (glowa, tulow, pas, ramiona, dlonie,
        nogi, stopy) albo "reszta": kolor}; brak = szary manekin."""
        kolory = dict(kolory or {})
        for kosc, k in self.kosci.items():
            if k["czesc"] is None:
                continue
            kol = kolory.get(kosc)
            if kol is None:
                kol = next((kolory[g] for g, kosci in GRUPY_CIALA.items() if kosc in kosci and g in kolory), None)
            self.klocek(kosc, kol or kolory.get("reszta", "szary"), mat, faza)

    def zaloz(self, akcesorium, zaczep=None, pos=(0, 0, 0), obrot=(0, 0, 0), eksport=True):
        """Załóż akcesorium na punkt zaczepienia (domyślnie jego własny). pos/obrot = dodatkowa korekta w ramce zaczepu.
        eksport=False — tylko do podglądu (nie trafia do FBX/GLB postaci, np. przy ciele awatara na Marketplace)."""
        z = zaczep or akcesorium.zaczep
        if z not in self.zaczepy:
            raise ValueError("Postać %s nie ma zaczepu %r (są: %s)" % (self.id, z, ", ".join(sorted(self.zaczepy))))
        self.zalozone.append((akcesorium, z, _trzy(pos, "pos"), _trzy(obrot, "obrot"), bool(eksport)))

    # --- animacje
    def klip(self, nazwa, dlugosc, fps=30, petla=True, probki=8):
        """Nowy klip animacji: dlugosc w klatkach (klatki 0…dlugosc), fps, petla = klip zapętlony."""
        if any(k.nazwa == nazwa for k in self.klipy):
            raise ValueError("Klip %r już istnieje" % nazwa)
        k = Klip(self, nazwa, dlugosc, fps, petla, probki)
        self.klipy.append(k)
        return k

    def ustaw_poze_renderu(self, klip, klatka=0):
        """Rendery prezentacyjne i ikona pokażą postać w tej klatce klipu (zamiast pozy spoczynkowej)."""
        self.poza_renderu = (klip, float(klatka))

    # --- wynik
    def _ramka_zaczepu(self, nazwa):
        z = self.zaczepy[nazwa]
        t = _razy(_dodaj(self.kosci[z["kosc"]]["staw"], z["p"]), self.skala)
        return z["kosc"], macierz_obrotu(*z["r"]), t

    def json(self):
        s = self.skala
        kosci = [{"n": n, "rodzic": k["rodzic"], "staw": _zaokr(_razy(k["staw"], s)), "dl": round(k["dl"] * s, 4)}
                 for n, k in self.kosci.items()]
        czesci = []
        for c in self.czesci:
            st = self.kosci[c["kosc"]]["staw"]
            czesci.append(self._czesc_json(self._czesc_w(dict(c, p=_dodaj(st, c["p"])), I3, (0.0, 0.0, 0.0), s)))
        zaczepy = []
        for n in self.zaczepy:
            kosc, R, t = self._ramka_zaczepu(n)
            zaczepy.append({"n": n, "kosc": kosc, "p": _zaokr(t), "r": _zaokr(self.zaczepy[n]["r"], 3)})
        akcesoria = []
        for akc, z, pos, obrot, eksport in self.zalozone:
            kosc, R, t = self._ramka_zaczepu(z)
            R0 = mnoz(R, macierz_obrotu(*obrot))
            t0 = _dodaj(t, razy_wektor(R, pos))
            cz = []
            for c in akc.czesci_w(R0, t0):
                c["kosc"] = kosc
                cz.append(self._czesc_json(c))
            akcesoria.append({"id": akc.id, "nazwa": akc.nazwa, "zaczep": z, "kosc": kosc, "eksport": eksport,
                              "czesci": cz})
        return {"wersja": WERSJA, "rodzaj": "postac", "id": self.id, "nazwa": self.nazwa, "typ": self.typ,
                "skala": s, "kosci": kosci, "czesci": czesci, "zaczepy": zaczepy, "akcesoria": akcesoria,
                "klipy": [k.json(s) for k in self.klipy],
                "skora": {k: [g, round(y0 * s, 4), round(y1 * s, 4)] for k, (g, y0, y1) in self.skora.items()},
                "poza_renderu": list(self.poza_renderu) if self.poza_renderu else None,
                "materialy": MATERIALY, "limity": LIMITY}

    def sprawdz(self):
        """(bledy, uwagi) — błędy zatrzymują podgląd, uwagi tylko się wypisują."""
        bledy, uwagi = [], []
        if self.typ == "r15":
            brak = [k for k in R15_KOSCI if k not in self.kosci]
            if brak:
                bledy.append("%s: brak kości R15: %s" % (self.id, ", ".join(brak)))
            dodatkowe = [k for k in self.kosci if k not in R15_KOSCI and k not in ("Root", "HumanoidRootNode")]
            if dodatkowe:
                uwagi.append("%s: kości spoza standardu R15 (%s) — w Roblox to już nie zwykły R15"
                             % (self.id, ", ".join(dodatkowe)))
        for c in self.czesci:
            if c["kosc"] in ("Root", "HumanoidRootNode"):
                bledy.append("%s: część „%s” na kości %s (Roblox: korzeń bez wpływów) — przypnij ją do innej kości"
                             % (self.id, c["n"], c["kosc"]))
            if min(c["s"]) < 0.02:
                uwagi.append("%s: część „%s” cieńsza niż 0,02 studa" % (self.id, c["n"]))
        kosci_z_czesciami = {c["kosc"] for c in self.czesci}
        if self.typ == "r15":
            puste = [k for k in R15_KOSCI if k in self.kosci and k not in kosci_z_czesciami]
            if puste:
                uwagi.append("%s: kości R15 bez żadnej bryły: %s" % (self.id, ", ".join(puste)))
        d = self.json()
        pud = pudelko([dict(c, r=tuple(c["r"])) for c in d["czesci"]])
        if pud:
            if pud[0][1] > 0.05:
                uwagi.append("%s: najniższy punkt na y = %.2f — postać nie stoi na ziemi (y = 0)" % (self.id, pud[0][1]))
            if pud[0][1] < -0.3:
                uwagi.append("%s: część schodzi pod ziemię (y = %.2f)" % (self.id, pud[0][1]))
        for akc, z, *_ in self.zalozone:
            for b in akc.sprawdz()[0]:
                bledy.append(b)
        for k in self.klipy:
            uwagi.extend(k.sprawdz())
        if self.poza_renderu and not any(k.nazwa == self.poza_renderu[0] for k in self.klipy):
            bledy.append("%s: poza renderu wskazuje nieznany klip %r" % (self.id, self.poza_renderu[0]))
        return bledy, uwagi


# --------------------------------------------------------------------------- klipy animacji
class Klip:
    """Klip = klatki kluczowe kanałów kości: obrot (stopnie), przes (studs, w osiach modelu), skala (mnożniki).
    Wygładzanie klucza dotyczy odcinka OD tego klucza do następnego: "gladko" (Bezier, auto), "liniowo", "stale".
    Klip zapętlony: brakujący klucz w ostatniej klatce dostaje wartość z klatki 0 (i odwrotnie)."""

    def __init__(self, postac, nazwa, dlugosc, fps=30, petla=True, probki=8):
        self.postac, self.nazwa = postac, _sprawdz_id(nazwa, "klipu")
        self.dlugosc, self.fps, self.petla, self.probki = int(dlugosc), int(fps), bool(petla), int(probki)
        if self.dlugosc < 1:
            raise ValueError("Klip %s: dlugosc >= 1 klatka" % nazwa)
        self.kanaly = {}                                         # (kosc, kanal) -> {klatka: [x, y, z, wyg]}

    def _ustaw(self, klatka, kosc, kanal, wartosc, wyg):
        if kosc not in self.postac.kosci:
            raise ValueError("Klip %s: nieznana kość %r" % (self.nazwa, kosc))
        if kanal not in KANALY or wyg not in WYGLADZANIA:
            raise ValueError("Klip %s: kanał %r / wygładzanie %r" % (self.nazwa, kanal, wyg))
        f = round(float(klatka), 3)
        if f < -1e-6 or f > self.dlugosc + 1e-6:
            raise ValueError("Klip %s: klatka %s poza 0…%d" % (self.nazwa, klatka, self.dlugosc))
        v = _trzy(wartosc, kanal)
        self.kanaly.setdefault((kosc, kanal), {})[f] = [v[0], v[1], v[2], wyg]

    def klucz(self, klatka, kosc, obrot=None, przes=None, skala=None, wyg="gladko"):
        """Klucz jednej kości: obrot=(rx, ry, rz), przes=(dx, dy, dz), skala=(sx, sy, sz) albo liczba."""
        for kanal, w in (("obrot", obrot), ("przes", przes), ("skala", skala)):
            if w is not None:
                self._ustaw(klatka, kosc, kanal, w, wyg)
        return self

    def poza(self, klatka, kosci, wyg="gladko"):
        """Poza = klucze wielu kości w jednej klatce: {kość: (rx, ry, rz)} albo {kość: {"obrot":…, "przes":…}}."""
        for kosc, w in kosci.items():
            if isinstance(w, dict):
                self.klucz(klatka, kosc, wyg=wyg, **w)
            else:
                self.klucz(klatka, kosc, obrot=w, wyg=wyg)
        return self

    def wartosc(self, kosc, kanal, klatka):
        """Wartość kanału w klatce (liniowo między kluczami; dla pętli z zawinięciem) albo None."""
        kl = self.kanaly.get((kosc, kanal))
        if not kl:
            return None
        ks = sorted(kl)
        f = float(klatka)
        if f in kl:
            return tuple(kl[f][:3])
        if self.petla and len(ks) > 0:
            ks2 = [k - self.dlugosc for k in ks] + ks + [k + self.dlugosc for k in ks]
            war = [kl[k][:3] for k in ks] * 3
        else:
            ks2, war = ks, [kl[k][:3] for k in ks]
        if f <= ks2[0]:
            return tuple(war[0])
        if f >= ks2[-1]:
            return tuple(war[-1])
        for i in range(len(ks2) - 1):
            if ks2[i] <= f <= ks2[i + 1]:
                t = (f - ks2[i]) / (ks2[i + 1] - ks2[i])
                return tuple(war[i][j] + (war[i + 1][j] - war[i][j]) * t for j in range(3))
        return tuple(war[-1])

    def cykl(self, kosc, kanal, amplituda, faza=0.0, czestosc=1, srodek=None, probki=None):
        """Drganie sinusoidalne przez cały klip: wartość = srodek + amplituda · sin(2π(czestosc · t + faza)),
        t = klatka / dlugosc. Kolejne cykle tej samej kości i kanału SUMUJĄ się (np. kołysanie + podskok).
        faza 0,5 = przeciwnie (lewa noga vs prawa). czestosc całkowita trzyma pętlę bez szwu."""
        if kanal not in KANALY:
            raise ValueError("kanał: obrot, przes albo skala")
        amp = _trzy(amplituda, "amplituda")
        neutralny = (1.0, 1.0, 1.0) if kanal == "skala" else (0.0, 0.0, 0.0)
        n = int(probki or max(self.probki, 4 * int(czestosc)))
        istnial = (kosc, kanal) in self.kanaly
        sr = _trzy(srodek, "srodek") if srodek is not None else neutralny
        nowe = []
        for i in range(n + 1):
            f = self.dlugosc * i / n
            sn = math.sin(2 * math.pi * (czestosc * i / n + faza))
            baza = self.wartosc(kosc, kanal, f) if istnial else sr
            if istnial and srodek is not None:
                baza = tuple(baza[j] + sr[j] - neutralny[j] for j in range(3))
            nowe.append((f, tuple(baza[j] + amp[j] * sn for j in range(3))))
        for f, v in nowe:
            self._ustaw(f, kosc, kanal, v, "gladko")
        return self

    def zamach(self, kosc, wziecie, uderzenie, spocz=(0, 0, 0), czasy=(0.35, 0.5, 0.62), dobicie=0.12, start=0,
               koniec=None):
        """Zamach (atak) jednej kości, obroty w stopniach: spocz → wziecie (powoli, przygotowanie) → uderzenie
        (szybko, liniowo) → dobicie (przelot za uderzenie o ułamek `dobicie`) → spocz. czasy = ułamki odcinka
        start…koniec dla wzięcia, uderzenia i dobicia. Kilka kości z tymi samymi czasami = skoordynowany zamach."""
        k0 = float(start)
        k3 = float(self.dlugosc if koniec is None else koniec)
        L = k3 - k0
        sp, wz, ud = _trzy(spocz), _trzy(wziecie), _trzy(uderzenie)
        do = tuple(ud[i] + dobicie * (ud[i] - wz[i]) for i in range(3))
        self._ustaw(k0, kosc, "obrot", sp, "gladko")
        self._ustaw(k0 + czasy[0] * L, kosc, "obrot", wz, "liniowo")
        self._ustaw(k0 + czasy[1] * L, kosc, "obrot", ud, "gladko")
        self._ustaw(k0 + czasy[2] * L, kosc, "obrot", do, "gladko")
        self._ustaw(k3, kosc, "obrot", sp, "gladko")
        return self

    def _domkniete(self, kl):
        kl = {f: list(v) for f, v in kl.items()}
        koniec = float(self.dlugosc)
        if self.petla:
            if 0.0 in kl and koniec not in kl:
                kl[koniec] = list(kl[0.0])
            elif koniec in kl and 0.0 not in kl:
                kl[0.0] = list(kl[koniec])
        return kl

    def json(self, skala=1.0):
        kanaly = []
        for (kosc, kanal), kl in sorted(self.kanaly.items()):
            wiersze = []
            for f, (x, y, z, w) in sorted(self._domkniete(kl).items()):
                if kanal == "przes":
                    x, y, z = x * skala, y * skala, z * skala
                wiersze.append([f, round(x, 4), round(y, 4), round(z, 4), w])
            kanaly.append({"kosc": kosc, "typ": kanal, "klucze": wiersze})
        return {"n": self.nazwa, "dlugosc": self.dlugosc, "fps": self.fps, "petla": self.petla, "kanaly": kanaly}

    def sprawdz(self):
        uwagi = []
        if not self.kanaly:
            uwagi.append("klip %s: pusty" % self.nazwa)
        skala = sorted({kosc for (kosc, kanal) in self.kanaly if kanal == "skala"})
        if skala:
            uwagi.append("klip %s: kanał skali (%s) — animacja Roblox najpewniej przenosi tylko pozycję i obrót kości"
                         % (self.nazwa, ", ".join(skala)))
        if self.dlugosc / float(self.fps) > LIMITY["emote_max_s"]:
            uwagi.append("klip %s: %.1f s — emote w Roblox musi mieć < 10 s" % (self.nazwa, self.dlugosc / float(self.fps)))
        if self.petla:
            for (kosc, kanal), kl in self.kanaly.items():
                kl2 = self._domkniete(kl)
                a, b = kl2.get(0.0), kl2.get(float(self.dlugosc))
                if a is None or b is None:
                    uwagi.append("klip %s: %s.%s bez klucza w klatce 0 ani %d — pętla może skakać"
                                 % (self.nazwa, kosc, kanal, self.dlugosc))
                elif max(abs(a[i] - b[i]) for i in range(3)) > 1e-3:
                    uwagi.append("klip %s: %s.%s — klatka 0 ≠ klatka %d, pętla skoczy"
                                 % (self.nazwa, kosc, kanal, self.dlugosc))
        return uwagi


# --------------------------------------------------------------------------- gotowe klipy R15 (do użycia albo podpatrzenia)
def klip_spoczynek_r15(p, nazwa="spoczynek", dlugosc=60, sila=1.0):
    """Oddech: lekkie kołysanie tułowia i głowy, ręce odchylają się minimalnie."""
    k = p.klip(nazwa, dlugosc, petla=True)
    k.cykl("UpperTorso", "obrot", (1.6 * sila, 0, 0))
    k.cykl("Head", "obrot", (-1.2 * sila, 0, 1.0 * sila), faza=0.1)
    k.cykl("LeftUpperArm", "obrot", (0, 0, 2.5 * sila), srodek=(0, 0, 3))
    k.cykl("RightUpperArm", "obrot", (0, 0, -2.5 * sila), srodek=(0, 0, -3))
    k.cykl("LeftLowerArm", "obrot", (-2.0 * sila, 0, 0), srodek=(-6, 0, 0), faza=0.1)
    k.cykl("RightLowerArm", "obrot", (-2.0 * sila, 0, 0), srodek=(-6, 0, 0), faza=0.1)
    return k


def klip_chod_r15(p, nazwa="chod", dlugosc=24, krok=30.0, ramiona=24.0, podskok=0.1):
    """Chód w miejscu: nogi i ręce na przemian, kolana uginają się przy przenoszeniu nogi, tułów podskakuje dwa razy
    na cykl i skręca się z biodrami."""
    k = p.klip(nazwa, dlugosc, petla=True, probki=8)
    k.cykl("LeftUpperLeg", "obrot", (krok, 0, 0), faza=0.0)
    k.cykl("RightUpperLeg", "obrot", (krok, 0, 0), faza=0.5)
    k.cykl("LeftUpperArm", "obrot", (ramiona, 0, 0), faza=0.5, srodek=(0, 0, 3))
    k.cykl("RightUpperArm", "obrot", (ramiona, 0, 0), faza=0.0, srodek=(0, 0, -3))
    for strona, faza in (("Left", 0.0), ("Right", 0.5)):
        for i in range(9):                                   # kolano: tylko zgięcie w tył, gdy noga idzie do przodu
            t = i / 8.0
            sn = math.sin(2 * math.pi * (t + faza))
            k.klucz(dlugosc * t, strona + "LowerLeg", obrot=(max(0.0, -sn) * krok * 1.3, 0, 0))
            k.klucz(dlugosc * t, strona + "LowerArm", obrot=(-10 - 8 * max(0.0, sn), 0, 0))
    k.cykl("LowerTorso", "przes", (0, podskok / 2, 0), czestosc=2, faza=0.25, srodek=(0, podskok / 2, 0))
    k.cykl("UpperTorso", "obrot", (0, 5, 0), faza=0.0)
    k.cykl("Head", "obrot", (0, -4, 0), faza=0.0)
    return k


def klip_atak_r15(p, nazwa="atak", dlugosc=30, reka="Right"):
    """Zamach bronią z góry: ręka nad głowę, cięcie w dół, tułów skręca się za ciosem."""
    k = p.klip(nazwa, dlugosc, petla=False)
    zn = -1.0 if reka == "Right" else 1.0
    k.zamach(reka + "UpperArm", wziecie=(-165, 0, zn * 10), uderzenie=(-50, 0, -zn * 5))
    k.zamach(reka + "LowerArm", wziecie=(-40, 0, 0), uderzenie=(-15, 0, 0))
    k.zamach("UpperTorso", wziecie=(-4, zn * 18, 0), uderzenie=(8, -zn * 22, 0))
    k.zamach("Head", wziecie=(-6, -zn * 8, 0), uderzenie=(6, zn * 10, 0))
    druga = "Left" if reka == "Right" else "Right"
    k.zamach(druga + "UpperArm", wziecie=(-20, 0, -zn * 20), uderzenie=(25, 0, -zn * 10))
    return k


def klip_trzymanie_r15(p, nazwa="trzymanie", reka="Right"):
    """Poza z bronią w górze: przedramię do przodu, ostrze broni z zaczepu Grip sterczy pionowo."""
    k = p.klip(nazwa, 2, petla=True)
    poza = {reka + "UpperArm": (-8, 0, 0), reka + "LowerArm": (-80, 0, 0)}
    k.poza(0, poza)
    k.poza(2, poza)
    return k


def chod_z_bronia(k, drzewce=False, reka="Right"):
    """Przeróbka klipu chodu, gdy w dłoni jest broń: przedramię na stałe uniesione (jak animacja „toolnone” w Roblox),
    zamiast zwisać — wtedy ostrze nie celuje w kamerę i nie wchodzi w udo. Broń długa (drzewce): przedramię −80°,
    drzewce stoi pionowo, ramię prawie nie macha (cykl ±6°); broń krótka: przedramię −35°, ramię macha słabiej."""
    for kosc in (reka + "LowerArm", reka + "UpperArm"):
        k.kanaly.pop((kosc, "obrot"), None)
    zn = -1.0 if reka == "Right" else 1.0
    if drzewce:
        k.cykl(reka + "LowerArm", "obrot", (6, 0, 0), faza=0.0, srodek=(-80, 0, 0))
        k.cykl(reka + "UpperArm", "obrot", (6, 0, 0), faza=0.0, srodek=(-8, 0, zn * 4))
    else:
        k.cykl(reka + "LowerArm", "obrot", (6, 0, 0), faza=0.0, srodek=(-35, 0, 0))
        k.cykl(reka + "UpperArm", "obrot", (14, 0, 0), faza=0.0, srodek=(-4, 0, zn * 6))
    return k


def przymiarka(id, akcesoria, nazwa="Przymiarka na manekinie R15"):
    """Szary manekin R15 z założonymi akcesoriami (bez tych z przymierz=False). Z bronią: poza renderu „trzymanie”
    i chód z uniesionym przedramieniem (chod_z_bronia)."""
    p = manekin_r15(id, nazwa)
    for a in akcesoria:
        if a.przymierz:
            p.zaloz(a)
    bronie = [a for a in akcesoria if a.typ == "Bron" and a.przymierz]
    if bronie:
        p.ustaw_poze_renderu("trzymanie", 0)
    prawa = [a for a in bronie if a.zaczep == "RightGripAttachment"]
    if prawa:
        chod_z_bronia(next(k for k in p.klipy if k.nazwa == "chod"), drzewce=any(a.chwyt == "drzewce" for a in prawa))
    return p


def manekin_r15(id="manekin", nazwa="Manekin R15", klipy=True):
    """Szary klockowy ludzik R15 (ok. 5,25 studa) do przymierzania ekwipunku i jako miara skali.
    Klipy: spoczynek, chod, atak (zamach prawą ręką), trzymanie (broń w górze)."""
    p = Postac(id, nazwa, typ="r15")
    p.cialo({"glowa": "B4B9C3", "reszta": "szary"})
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        for zn, nz in ((1, "Oko L"), (-1, "Oko P")):
            p.blok(nz, (zn * 0.27, 0.08, d / 2 + 0.03), (0.17, 0.27, 0.08), "szary_ciemny", faza=0.02)
    if klipy:
        klip_spoczynek_r15(p)
        klip_chod_r15(p)
        klip_atak_r15(p)
        klip_trzymanie_r15(p)
    return p


# --------------------------------------------------------------------------- pakiet dla Blendera
def pakiet(modele, zadania=None):
    """Słownik {"wersja", "modele": [...]} z listy Postac/Akcesorium (zadania: {id: {...}} dla blender_postac.py)."""
    wynik = []
    for m in modele:
        d = m.json()
        if zadania and m.id in zadania:
            d["zadania"] = zadania[m.id]
        wynik.append(d)
    return {"wersja": WERSJA, "generator": "swiat/postacie/biblioteka/postac.py", "modele": wynik}


def zapisz_json(dane, sciezka):
    with open(sciezka, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dane, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
