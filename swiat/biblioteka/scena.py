# -*- coding: utf-8 -*-
"""Biblioteka scen z klocków Roblox (v2) — wspólny kręgosłup generatorów map.

Scena to lista części (blok, kula, walec, klin, klin narożny) zapisywana jako `czesci.json` — jedno źródło dla Blendera
(tools/blender/klocki.py), Roblox Studio (tools/studio_buduj.py) i podglądu 3D w panelu. Format: panel/README.md,
geometria kształtów: panel/luau/KSZTALTY.md. Jednostka = stud, Y w górę, północ = −Z.

Najważniejsze w v2 — UKŁADY LOKALNE. Budynek budujesz wokół własnego (0, 0, 0), a gdzie stanie, jak jest obrócony,
pochylony i jak duży, decyduje `with s.uklad(...)`. Układy można zagnieżdżać (krzywe piętro na pochylonym parterze):

    s = Scena("Workspace/KrzyweMiasteczko", paleta=PALETA)
    with s.uklad(pos=(40, 0, -30), obrot=(0, 125, 0), grupa="Karczma"):      # miejsce i obrót budynku w mieście
        s.blok("Parter", (0, 6, 0), (30, 12, 22), "tynk")
        with s.uklad(pos=(0, 12, 0), obrot=(0, 4, 3)):                       # piętro: skręcone o 4°, przechylone o 3°
            s.blok("Piętro", (0, 5, 1.5), (33, 10, 25), "tynk2")

Konwencje:
- obrót = (rx, ry, rz) w STOPNIACH w konwencji Roblox (CFrame.fromOrientation: Ry · Rx · Rz) — ry skręca wokół pionu,
  rx pochyla w przód/tył, rz przechyla na boki;
- budynek w swoim układzie: środek obrysu na ziemi = (0, 0, 0), FRONT z wejściem po stronie +Z;
- obrót ry = θ kieruje front (+Z) w stronę (sin θ, 0, cos θ) — żeby front patrzył na punkt (0, 0) z pozycji (x, z):
  θ = degrees(atan2(−x, −z)) (funkcja `ku_srodkowi`);
- kolory: klucz palety albo „RRGGBB”; nieznany klucz to błąd (literówka nie przejdzie po cichu);
- materiały = nazwy Enum.Material (SmoothPlastic, Wood, WoodPlanks, Slate, Cobblestone, Brick, Grass, Sand, Fabric,
  Metal, Neon, Glass…).
"""
import contextlib
import json
import math
import re

BLOK, KULA, WALEC, KLIN, NAROZNIK = 0, 1, 2, 3, 4
NAZWY_KSZTALTOW = {BLOK: "blok", KULA: "kula", WALEC: "walec", KLIN: "klin", NAROZNIK: "klin narożny"}
MATERIALY = {"SmoothPlastic", "Plastic", "Wood", "WoodPlanks", "Slate", "Cobblestone", "Brick", "Concrete", "Grass", "Ground",
             "LeafyGrass", "Sand", "Sandstone", "Fabric", "Metal", "DiamondPlate", "CorrodedMetal", "Marble", "Granite",
             "Pebble", "Neon", "Glass", "Ice", "Snow", "Limestone", "Pavement", "Rock", "Basalt", "Mud", "Cardboard",
             "Carpet", "Leather", "Plaster", "Rubber", "RoofShingles", "ClayRoofTiles", "CeramicTiles", "Foil"}
_HEX = re.compile(r"^[0-9A-Fa-f]{6}$")
I3 = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


# --------------------------------------------------------------------------- matematyka obrotów (konwencja Roblox)
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
    """Odwrotność macierz_obrotu: (rx, ry, rz) w stopniach (jak CFrame:ToOrientation)."""
    sx = max(-1.0, min(1.0, -m[1][2]))
    rx = math.asin(sx)
    if abs(sx) > 0.999999:                                     # pion: rz wchłonięty przez ry
        ry = math.atan2(-m[2][0], m[0][0])
        rz = 0.0
    else:
        ry = math.atan2(m[0][2], m[2][2])
        rz = math.atan2(m[1][0], m[1][1])
    return math.degrees(rx), math.degrees(ry), math.degrees(rz)


def ku_srodkowi(x, z, cel=(0.0, 0.0)):
    """Kąt ry, przy którym front budynku (+Z) stojącego w (x, z) patrzy na punkt `cel`."""
    return math.degrees(math.atan2(cel[0] - x, cel[1] - z))


# --------------------------------------------------------------------------- scena
class Scena:
    def __init__(self, korzen="Workspace/Scena", paleta=None):
        self.korzen = korzen.rstrip("/")
        self.paleta = dict(paleta or {})
        self.grupy, self.materialy, self.czesci = [], [], []
        self._stos = [(I3, (0.0, 0.0, 0.0), 1.0)]              # (obrót 3×3, przesunięcie, skala)
        self._grupy = ["Inne"]
        self._cechy = [(True, True)]                           # (kolizja, cień) dla dodawanych części
        self.obrysy = []                                       # grupy, którym Studio ma dodać obrys sylwetki (Highlight)

    # --- układy lokalne i grupy
    @contextlib.contextmanager
    def uklad(self, pos=(0.0, 0.0, 0.0), obrot=(0.0, 0.0, 0.0), skala=1.0, grupa=None):
        """Układ lokalny: wszystko dodane w środku jest najpierw skalowane, potem obracane, potem przesuwane."""
        R, t, s = self._stos[-1]
        nt = tuple(t[i] + s * v for i, v in enumerate(razy_wektor(R, pos)))
        self._stos.append((mnoz(R, macierz_obrotu(*obrot)), nt, s * float(skala)))
        if grupa is not None:
            self._grupy.append(grupa)
        try:
            yield self
        finally:
            self._stos.pop()
            if grupa is not None:
                self._grupy.pop()

    @contextlib.contextmanager
    def grupa(self, nazwa):
        """Grupa = Model w Studio i kolekcja w Blenderze. Można podać ścieżkę „Karczma/Szyld”."""
        self._grupy.append(nazwa)
        try:
            yield self
        finally:
            self._grupy.pop()

    @contextlib.contextmanager
    def cechy(self, kolizja=None, cien=None):
        """Części dodane w środku: kolizja=False → gracz przez nie przechodzi (liście, dym, woda, światła, chorągwie);
        cien=False → nie rzucają cienia (płaskie łaty na ziemi, poświaty). None = bez zmiany."""
        k, c = self._cechy[-1]
        self._cechy.append((k if kolizja is None else bool(kolizja), c if cien is None else bool(cien)))
        try:
            yield self
        finally:
            self._cechy.pop()

    def obrys_sylwetki(self, grupa=None):
        """Poproś o komiksowy obrys całej grupy w Studio (jeden Highlight na Model; limit silnika: 31 naraz)."""
        g = self.korzen + "/" + (grupa or self._grupy[-1])
        if g not in self.obrysy:
            self.obrysy.append(g)

    # --- dodawanie części
    def _kolor(self, kolor):
        k = self.paleta.get(kolor, kolor)
        k = str(k).lstrip("#")
        if not _HEX.match(k):
            raise ValueError("Nieznany kolor %r — użyj klucza palety albo RRGGBB" % (kolor,))
        return k.upper()

    def _idx(self, lista, wartosc):
        try:
            return lista.index(wartosc)
        except ValueError:
            lista.append(wartosc)
            return len(lista) - 1

    def dodaj(self, ksztalt, nazwa, pos, size, kolor, mat="SmoothPlastic", rot=(0.0, 0.0, 0.0), alfa=0.0):
        if mat not in MATERIALY:
            raise ValueError("Nieznany materiał %r" % (mat,))
        R, t, s = self._stos[-1]
        p = razy_wektor(R, pos)
        rx, ry, rz = katy_z_macierzy(mnoz(R, macierz_obrotu(*rot)))
        g = self._idx(self.grupy, self.korzen + "/" + self._grupy[-1])
        m = self._idx(self.materialy, mat)
        wiersz = [ksztalt, g, round(t[0] + s * p[0], 3), round(t[1] + s * p[1], 3), round(t[2] + s * p[2], 3),
                  round(math.radians(rx), 4), round(math.radians(ry), 4), round(math.radians(rz), 4),
                  round(abs(size[0]) * s, 3), round(abs(size[1]) * s, 3), round(abs(size[2]) * s, 3),
                  self._kolor(kolor), m, round(float(alfa), 2), str(nazwa)[:40]]
        kolizja, cien = self._cechy[-1]
        if not (kolizja and cien):                             # 16. pole (opcjonalne): 1 = bez kolizji, 2 = bez cienia
            wiersz.append((0 if kolizja else 1) | (0 if cien else 2))
        self.czesci.append(wiersz)

    # --- prymitywy (współrzędne w bieżącym układzie lokalnym; pos = ŚRODEK części)
    def blok(self, nazwa, pos, size, kolor, mat="SmoothPlastic", rot=(0, 0, 0), alfa=0.0):
        self.dodaj(BLOK, nazwa, pos, size, kolor, mat, rot, alfa)

    def kula(self, nazwa, pos, srednica, kolor, mat="SmoothPlastic", alfa=0.0):
        self.dodaj(KULA, nazwa, pos, (srednica, srednica, srednica), kolor, mat, (0, 0, 0), alfa)

    def klin(self, nazwa, pos, size, kolor, mat="SmoothPlastic", rot=(0, 0, 0), alfa=0.0):
        """Klin: wysoka pionowa ściana po stronie +Z, skos opada ku −Z (size = szer X, wys Y, głęb Z)."""
        self.dodaj(KLIN, nazwa, pos, size, kolor, mat, rot, alfa)

    def naroznik(self, nazwa, pos, size, kolor, mat="SmoothPlastic", rot=(0, 0, 0), alfa=0.0):
        """Klin narożny: wierzchołek w rogu (+X, +Y, −Z)."""
        self.dodaj(NAROZNIK, nazwa, pos, size, kolor, mat, rot, alfa)

    def walec(self, nazwa, pos, r, dl, kolor, mat="SmoothPlastic", os="y", rot=(0, 0, 0), alfa=0.0):
        """Walec o promieniu r i długości dl; pos = środek. os: „y” stojący, „x” albo „z” leżący; rot = dodatkowy obrót."""
        wlasny = {"x": (0, 0, 0), "y": (0, 0, 90), "z": (0, 90, 0)}[os]
        with self.uklad(pos=pos, obrot=rot):
            self.dodaj(WALEC, nazwa, (0, 0, 0), (dl, 2 * r, 2 * r), kolor, mat, wlasny, alfa)

    def slup(self, nazwa, x, y0, z, r, h, kolor, mat="SmoothPlastic", przechyl=(0, 0), alfa=0.0):
        """Stojący walec od podstawy: (x, y0, z) = środek podstawy; przechyl = (stopnie w przód/tył, stopnie na boki)."""
        with self.uklad(pos=(x, y0, z), obrot=(przechyl[0], 0, przechyl[1])):
            self.walec(nazwa, (0, h / 2.0, 0), r, h, kolor, mat, "y", alfa=alfa)

    def belka(self, nazwa, p1, p2, grub, kolor, mat="Wood", szer=None):
        """Belka (blok) między dwoma punktami; grub = wysokość przekroju, szer = szerokość (domyślnie = grub)."""
        dx, dy, dz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
        dl = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dl < 1e-6:
            return
        rx = math.degrees(math.asin(max(-1.0, min(1.0, -dy / dl))))
        ry = math.degrees(math.atan2(dx, dz))
        self.blok(nazwa, ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0, (p1[2] + p2[2]) / 2.0), (szer or grub, grub, dl),
                  kolor, mat, (rx, ry, 0))

    def ostroslup(self, nazwa, srodek_podstawy, a, b, h, kolor, mat="SmoothPlastic"):
        """Ostrosłup o podstawie prostokątnej 2a (X) × 2b (Z) i wysokości h — cztery kliny narożne, wierzchołek nad środkiem."""
        cx, y0, cz = srodek_podstawy
        y = y0 + h / 2.0
        self.naroznik(nazwa, (cx - a / 2.0, y, cz + b / 2.0), (a, h, b), kolor, mat, (0, 0, 0))
        self.naroznik(nazwa, (cx + a / 2.0, y, cz + b / 2.0), (b, h, a), kolor, mat, (0, 90, 0))
        self.naroznik(nazwa, (cx + a / 2.0, y, cz - b / 2.0), (a, h, b), kolor, mat, (0, 180, 0))
        self.naroznik(nazwa, (cx - a / 2.0, y, cz - b / 2.0), (b, h, a), kolor, mat, (0, 270, 0))

    def dach_dwuspadowy(self, nazwa, srodek_okapu, dl, pol, wznios, grub, kolor, mat="Slate", okap=1.2, kalenica=None,
                        obrys=None):
        """Dach z dwóch płyt, kalenica wzdłuż X. srodek_okapu = (x, y na wysokości okapu, z); pol = połowa głębokości
        budynku; okap = wysunięcie płyt poza ściany; kalenica = kolor belki na szczycie (None = bez); obrys = kolor
        ciemnej podkładki pod każdą połacią (komiksowy rant widoczny od dołu i z boków; None = bez)."""
        cx, y, cz = srodek_okapu
        kat = math.degrees(math.atan2(wznios, pol))
        dlugosc = math.hypot(pol, wznios) + okap
        for znak in (1, -1):
            srodek = (cx, y + wznios / 2.0 + grub * 0.35, cz + znak * (pol / 2.0 + okap * 0.32))
            self.blok(nazwa, srodek, (dl, grub, dlugosc), kolor, mat, (znak * kat, 0, 0))
            if obrys:
                with self.uklad(pos=srodek, obrot=(znak * kat, 0, 0)):
                    self.blok(nazwa + " obrys", (0, -grub * 0.55, 0), (dl + 0.7, grub * 0.5, dlugosc + 0.7), obrys, "SmoothPlastic")
        if kalenica:
            self.blok(nazwa + " kalenica", (cx, y + wznios + grub * 0.55, cz), (dl + 0.6, grub * 0.9, grub * 1.6), kalenica, mat)

    def szczyt(self, nazwa, srodek_podstawy, pol, wznios, grub, kolor, mat="SmoothPlastic"):
        """Trójkątna ściana szczytowa pod dach dwuspadowy z kalenicą wzdłuż X: stoi w płaszczyźnie YZ (grubość wzdłuż X).
        srodek_podstawy = (x, y dołu trójkąta, z środka); pol = połowa szerokości podstawy."""
        x, y0, cz = srodek_podstawy
        self.klin(nazwa, (x, y0 + wznios / 2.0, cz - pol / 2.0), (grub, wznios, pol), kolor, mat)
        self.klin(nazwa, (x, y0 + wznios / 2.0, cz + pol / 2.0), (grub, wznios, pol), kolor, mat, (0, 180, 0))

    def ramka(self, nazwa, pos, szer, wys, kolor="tusz", grub=0.35, gleb=0.3, mat="SmoothPlastic"):
        """Prostokątna rama z 4 beleczek w płaszczyźnie XY (wokół okna, drzwi, szyldu); pos = środek otworu."""
        x, y, z = pos
        self.blok(nazwa, (x, y + wys / 2.0 + grub / 2.0, z), (szer + 2 * grub, grub, gleb), kolor, mat)
        self.blok(nazwa, (x, y - wys / 2.0 - grub / 2.0, z), (szer + 2 * grub, grub, gleb), kolor, mat)
        self.blok(nazwa, (x - szer / 2.0 - grub / 2.0, y, z), (grub, wys, gleb), kolor, mat)
        self.blok(nazwa, (x + szer / 2.0 + grub / 2.0, y, z), (grub, wys, gleb), kolor, mat)

    def podkladka(self, nazwa, pos, size, kolor="tusz", zapas=0.35, cofnij=0.12, os="z", mat="SmoothPlastic", rot=(0, 0, 0)):
        """Komiksowy obrys płaskiego elementu: ciemny blok większy o `zapas` z każdej strony, cofnięty o `cofnij` wzdłuż
        osi `os` (kierunek „w głąb”, od patrzącego). pos i size = element, który ma dostać obrys."""
        sx, sy, sz = size
        with self.uklad(pos=pos, obrot=rot):
            if os == "z":
                self.blok(nazwa, (0, 0, -cofnij), (sx + 2 * zapas, sy + 2 * zapas, sz), kolor, mat)
            elif os == "x":
                self.blok(nazwa, (-cofnij, 0, 0), (sx, sy + 2 * zapas, sz + 2 * zapas), kolor, mat)
            else:
                self.blok(nazwa, (0, -cofnij, 0), (sx + 2 * zapas, sy, sz + 2 * zapas), kolor, mat)

    # --- wynik
    def json(self):
        d = {"wersja": 1, "generator": "biblioteka-v2", "grupy": self.grupy, "materialy": self.materialy, "czesci": self.czesci}
        if self.obrysy:
            d["obrysy"] = self.obrysy
        return d

    def zapisz(self, sciezka):
        with open(sciezka, "w", encoding="utf-8", newline="\n") as f:
            json.dump(self.json(), f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

    def statystyki(self, pomin_podkreslone=False):
        """{"czesci": n, "grupy": {nazwa: n}, "zakres": {"min": [x,y,z], "max": [x,y,z]}} — zakres to dokładna skrzynka
        obejmująca wszystkie części z uwzględnieniem ich obrotu. pomin_podkreslone = bez grup o nazwie zaczynającej się
        od „_” (podłoże, ludzik odniesienia)."""
        grupy = {}
        mn, mx = [1e9] * 3, [-1e9] * 3
        n = 0
        for c in self.czesci:
            nazwa = self.grupy[c[1]]
            if pomin_podkreslone and nazwa.split("/")[-1].startswith("_"):
                continue
            n += 1
            grupy[nazwa] = grupy.get(nazwa, 0) + 1
            R = macierz_obrotu(math.degrees(c[5]), math.degrees(c[6]), math.degrees(c[7]))
            for i in range(3):
                pol = (abs(R[i][0]) * c[8] + abs(R[i][1]) * c[9] + abs(R[i][2]) * c[10]) / 2.0
                mn[i] = min(mn[i], c[2 + i] - pol)
                mx[i] = max(mx[i], c[2 + i] + pol)
        return {"czesci": n, "grupy": grupy,
                "zakres": {"min": [round(v, 2) for v in mn], "max": [round(v, 2) for v in mx]} if n else None}

    def sprawdz(self, min_y=-6.0, limit_czesci=None):
        """Kontrola jakości — lista ostrzeżeń (pusta = dobrze): części za małe / za duże, pod ziemią, duplikaty,
        podejrzenie migotania (dwie nieobrócone ściany w tej samej płaszczyźnie nachodzące na siebie), budżet."""
        uwagi, widziane, plaszczyzny = [], {}, {}
        for i, c in enumerate(self.czesci):
            ks, g, x, y, z, rx, ry, rz, sx, sy, sz, kolor, m, alfa, nazwa = c[:15]
            opis = "%s „%s” w %s" % (NAZWY_KSZTALTOW.get(ks, ks), nazwa, self.grupy[g].split("/", 2)[-1])
            if min(sx, sy, sz) < 0.05:
                uwagi.append("za mała (< 0,05 studa): " + opis)
            if max(sx, sy, sz) > 2048:
                uwagi.append("za duża (> 2048 studów): " + opis)
            if y + max(sx, sy, sz) / 2.0 < min_y:
                uwagi.append("cała pod ziemią (y = %.1f): %s" % (y, opis))
            klucz = (ks, x, y, z, rx, ry, rz, sx, sy, sz)
            if klucz in widziane:
                uwagi.append("duplikat części: " + opis)
            widziane[klucz] = i
            if ks == BLOK and abs(rx) < 1e-4 and abs(rz) < 1e-4 and abs((ry / (math.pi / 2)) - round(ry / (math.pi / 2))) < 1e-3:
                if round(ry / (math.pi / 2)) % 2:
                    sx, sz = sz, sx
                for os_, wsp, pol, a0, a1, b0, b1 in (
                        (0, x, sx / 2, y - sy / 2, y + sy / 2, z - sz / 2, z + sz / 2),
                        (1, y, sy / 2, x - sx / 2, x + sx / 2, z - sz / 2, z + sz / 2),
                        (2, z, sz / 2, x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2)):
                    for znak in (1, -1):
                        plaszczyzny.setdefault((os_, znak, round(wsp + znak * pol, 2)), []).append((a0, a1, b0, b1, opis, kolor))
        migotanie = 0
        for sciany in plaszczyzny.values():
            if len(sciany) < 2 or len(sciany) > 400:
                continue
            for i in range(len(sciany)):
                a = sciany[i]
                for j in range(i + 1, len(sciany)):
                    b = sciany[j]
                    if a[5] == b[5]:                           # ten sam kolor w tej samej płaszczyźnie — niewidoczne
                        continue
                    wa = min(a[1], b[1]) - max(a[0], b[0])
                    wb = min(a[3], b[3]) - max(a[2], b[2])
                    if wa > 0.15 and wb > 0.15:
                        migotanie += 1
                        if migotanie <= 25:
                            uwagi.append("migotanie (ta sama płaszczyzna, różne kolory): %s ↔ %s" % (a[4], b[4]))
        if migotanie > 25:
            uwagi.append("… i jeszcze %d par podejrzanych o migotanie" % (migotanie - 25))
        if limit_czesci and len(self.czesci) > limit_czesci:
            uwagi.append("budżet przekroczony: %d części (limit %d)" % (len(self.czesci), limit_czesci))
        return uwagi
