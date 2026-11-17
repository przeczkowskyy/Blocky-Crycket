# -*- coding: utf-8 -*-
"""KOKOSOWY SIŁACZ — zwykły przeciwnik Dżungli (Gaj Kokosów): krępa małpa-siłacz z dwoma kokosami w pięściach,
ok. 7,0 studa (gracz ma 5,7).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/kokosowy_silacz.py --wyj <folder> --klip umiejetnosc

Opis z zarysu biomów (swiat/biomy/PLAN_BIOMOW.md, rozdz. „2. Dżungla”): krępa małpa-siłacz z dwoma kokosami
w pięściach. Klasa w przegrodzie: Wojownik. Zwykły cios = sierp prawym kokosem; umiejętność silnika `ciecie` = oba
kokosy wysoko nad głowę i uderzenie nimi z góry przed siebie.

Sylwetka (z daleka): trapez — ogromne barki i beczkowata pierś, łeb nisko między barkami, bardzo długie ręce
z grubymi przedramionami (karwasze z liści) i kokosami w pięściach, które wiszą tuż nad ziemią; krótkie, pałąkowate
nogi. Na brzuchu pas z liany ze złotą klamrą-kwiatem (pas mistrza), na czole opaska z liści i czerwony kwiat za uchem.

Paleta (Dżungla): futro pnie 5C3A22 (dwa odcienie), pierś, twarz i uszy jasny brąz B07A44 / D9A066, kokosy brązowe
z jaśniejszymi włóknami i trzema „oczkami”, liście 2FA34A / 6CCB4A (opaska, karwasze, pas), kwiaty E5392B / F2B030
(kwiat za uchem, klamra pasa), turkus 2EC4B6 (kamyk w klamrze).

Szkielet (typ „stwor”; L = lewa = +X, P = prawa = −X):
    Root > Biodra > {Tulow > {Glowa > Szczeka, RamieL > PrzedramieL > DlonL > KokosL,
                              RamieP > PrzedramieP > DlonP > KokosP},
                     UdoL > GolenL > StopaL, UdoP > GolenP > StopaP}
- `Biodra` niesie całą małpę; Stopa* trzymane płasko na ziemi (liczone w module);
- `Kokos*` = kokos w pięści na własnej kości (KokosLAttachment / KokosPAttachment w środku kokosa).

Klipy (30 kl./s; patrzy w +Z):
  idle (pętla 2,4 s: ciężki oddech, barki się unoszą, kokosy kołyszą się, rozgląda się), ruch (pętla 1,0 s: ciężki
  chód na pałąkowatych nogach, kołysanie barków, ręce wahadłem), atak (sierp prawym kokosem: zamach za bark i skręt,
  uderzenie przed siebie w dół — trafienie kl. 15, 1,0 s), umiejetnosc (cięcie: oba kokosy wysoko nad głowę, wspięcie
  na palce, uderzenie oboma kokosami z góry przed sobą kl. 26, przysiad, 1,6 s), trafienie (0,67 s), unik (ciężki
  krok w lewo 1,5 studa i powrót, 1,0 s), upadek (zatacza się, siada i pada na plecy z rozrzuconymi rękami; 2 s, leży
  w ostatniej klatce), wiwat (pętla 2 s: dwa razy stuka kokosami nad głową, potem poza siłacza — oba bicepsy).
Klipy są zapisane jako pozy kluczowe zamienione na klucz w KAŻDEJ klatce (wygładzanie „liniowo”).
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Postac, katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor

ID = "kokosowy_silacz"

PALETA = {
    "futro": "5C3A22", "futro_ciemne": "432817", "futro_jasne": "70482A",
    "skora": "B07A44", "twarz": "D9A066", "dlon": "3B2618",
    "kokos": "A06A36", "kokos_wlokno": "D2A46A", "kokos_oko": "2A1A10",
    "lisc": "2FA34A", "lisc_jasny": "6CCB4A", "liana": "1F7A36",
    "kwiat": "E5392B", "zloto": "F2B030", "turkus": "2EC4B6",
    "tusz": "17121F", "bialy": "FFFFFF", "zab": "F4EEDC",
}

CHWILE = {"atak": 15, "umiejetnosc": 26, "trafienie": 4, "unik": 14}

SLABOSCI = [
    "Kości Kokosowego Siłacza nie są R15 (własny szkielet: Root + 18 kości) — import do Roblox Studio nie był testowany.",
    "Kokos jest kulą (w Roblox: Ball przez SpecialMesh) na własnej kości w pięści; palce to klocki na przedniej "
    "ścianie kokosa (pięść go „obejmuje” z góry).",
    "Bryły są sztywno przypięte do kości: przy mocnym uniesieniu rąk barki i ramiona lekko wchodzą w siebie.",
    "Nogi są krótkie i grube — w chodzie stopy w podporze ślizgają się lekko po ziemi.",
    "Fali przy uderzeniu kokosami nie ma w klipie — wstrząs i smugę robi odtwarzacz (styl „wrecz”).",
]

# ----------------------------------------------------------------------------------------------- szkielet (studs)
BIODRA = (0.0, 2.35, 0.0)
TULOW = (0.0, 2.9, 0.0)
GLOWA = (0.0, 5.55, 0.55)
SZCZEKA = (0.0, 5.62, 1.12)
BARK = (1.75, 5.25, 0.1)
LOKIEC = (2.25, 3.75, 0.35)
NADGARSTEK = (2.35, 2.32, 0.55)
KOKOS = (2.38, 1.55, 0.82)          # środek lewego kokosa
R_KOKOSA = 0.63
BIODRO = (0.68, 2.25, 0.0)
KOLANO = (0.88, 1.25, 0.32)
KOSTKA = (0.85, 0.32, 0.05)

GLOWNA = "Biodra"
PLASKIE = ("StopaL", "StopaP")
POMIN_ZIEMIA = ()


def _lu(v, zn):
    return (zn * v[0], v[1], v[2])


def _roznica(a, b):
    return tuple(b[i] - a[i] for i in range(3))


def _os_kosci():
    o = {}
    for s, zn in (("L", 1.0), ("P", -1.0)):
        o["Ramie" + s] = _roznica(_lu(BARK, zn), _lu(LOKIEC, zn))
        o["Przedramie" + s] = _roznica(_lu(LOKIEC, zn), _lu(NADGARSTEK, zn))
        o["Udo" + s] = _roznica(_lu(BIODRO, zn), _lu(KOLANO, zn))
        o["Golen" + s] = _roznica(_lu(KOLANO, zn), _lu(KOSTKA, zn))
    return o


OS = _os_kosci()


def _model(p, kosc, obrot=(0, 0, 0), pos=(0, 0, 0)):
    """Układ MODELU (0, 0, 0 = ziemia pod środkiem) na kości: bryły podaje się we współrzędnych modelu."""
    s = p.staw(kosc)
    return p.na(kosc, pos=(pos[0] - s[0], pos[1] - s[1], pos[2] - s[2]), obrot=obrot)


def zbuduj():
    p = Postac(ID, "Kokosowy Siłacz", typ="stwor", skala=1.0, faza=0.08, paleta=PALETA)

    p.kosc("Biodra", "Root", staw=BIODRA, dl=0.8)
    p.kosc("Tulow", "Biodra", staw=TULOW, dl=1.2)
    p.kosc("Glowa", "Tulow", staw=GLOWA, dl=0.7)
    p.kosc("Szczeka", "Glowa", staw=SZCZEKA, dl=0.4)
    for s, zn in (("L", 1.0), ("P", -1.0)):
        p.kosc("Ramie" + s, "Tulow", staw=_lu(BARK, zn), dl=0.9)
        p.kosc("Przedramie" + s, "Ramie" + s, staw=_lu(LOKIEC, zn), dl=0.9)
        p.kosc("Dlon" + s, "Przedramie" + s, staw=_lu(NADGARSTEK, zn), dl=0.4)
        p.kosc("Kokos" + s, "Dlon" + s, staw=_lu(KOKOS, zn), dl=0.4)
        p.kosc("Udo" + s, "Biodra", staw=_lu(BIODRO, zn), dl=0.6)
        p.kosc("Golen" + s, "Udo" + s, staw=_lu(KOLANO, zn), dl=0.6)
        p.kosc("Stopa" + s, "Golen" + s, staw=_lu(KOSTKA, zn), dl=0.3)

    _nogi(p)
    _biodra(p)
    _tulow(p)
    _glowa(p)
    _rece(p)
    _kokosy(p)

    p.zaczep("RootAttachment", "Biodra", (-BIODRA[0], -BIODRA[1], -BIODRA[2]))
    # cel trafienia: środek piersi
    p.zaczep("GlowaAttachment", "Tulow", _roznica(TULOW, (0.0, 4.45, 1.15)))
    # środki kokosów (Bron i Pocisk na prawym)
    p.zaczep("KokosPAttachment", "KokosP", (0.0, 0.0, 0.0))
    p.zaczep("KokosLAttachment", "KokosL", (0.0, 0.0, 0.0))

    _klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return p


# ---------------------------------------------------------------------------------------------------- bryły
def _nogi(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        with _model(p, "Udo" + s):
            _belka(p, "Udo", _lu((0.66, 2.45, 0.0), zn), _lu(KOLANO, zn), 1.0, 1.0, "futro", "matowy", nad=0.1)
        with _model(p, "Golen" + s):
            _belka(p, "Golen", _lu(KOLANO, zn), _lu(KOSTKA, zn), 0.82, 0.82, "futro", "matowy", nad=0.12)
            p.blok("Kepka", _lu((1.25, 0.95, 0.15), zn), (0.12, 0.35, 0.4), "futro_ciemne", "matowy", faza=0.0)
        with _model(p, "Stopa" + s):
            p.blok("Stopa", _lu((0.88, 0.17, 0.38), zn), (0.86, 0.34, 1.3), "dlon", "matowy", faza=0.08)
            for i, (x, dl) in enumerate(((0.62, 0.42), (0.86, 0.38), (1.08, 0.34))):
                p.blok("Palec stopy %d" % i, _lu((x, 0.1, 1.12), zn), (0.2, 0.2, dl), "dlon", "matowy", faza=0.04)
            # kciuk stopy (od środka)
            p.blok("Kciuk stopy", _lu((0.42, 0.12, 0.65), zn), (0.24, 0.22, 0.38), "dlon", "matowy",
                   rot=(0, zn * 35, 0), faza=0.04)


def _biodra(p):
    with _model(p, "Biodra"):
        p.blok("Miednica", (0, 2.55, -0.05), (2.15, 1.0, 1.6), "futro", "matowy", faza=0.15)
        # pas mistrza z liany ze złotą klamrą-kwiatem
        p.blok("Pas", (0, 2.98, 0.0), (2.3, 0.36, 1.78), "liana", "matowy", faza=0.06)
        p.walec("Klamra", (0, 2.98, 0.92), (0.82, 0.12, 0.82), "zloto", "metal", rot=(90, 0, 0), faza=0.02,
                segm=12)
        for i in range(5):
            a = math.radians(90 + i * 72)
            p.blok("Platek klamry %d" % i, (0.22 * math.cos(a), 2.98 + 0.22 * math.sin(a), 0.99), (0.2, 0.2, 0.05),
                   "kwiat", "matowy", rot=(0, 0, 45 + i * 72), faza=0.0)
        p.blok("Kamyk", (0, 2.98, 1.02), (0.16, 0.16, 0.05), "turkus", "polysk", rot=(0, 0, 45), faza=0.0)
        for zn in (1, -1):
            p.blok("Lisc pasa", (zn * 0.75, 2.7, 0.88), (0.36, 0.5, 0.06), "lisc", "matowy", rot=(0, 0, zn * 20),
                   faza=0.0)


def _tulow(p):
    with _model(p, "Tulow"):
        with p.uklad(pos=(0, 4.25, 0.1), obrot=(8, 0, 0)):
            p.blok("Tors", (0, 0, 0), (2.9, 2.6, 2.0), "futro", "matowy", faza=0.25)
            p.blok("Kark", (0, 1.25, -0.45), (2.3, 0.9, 1.3), "futro_ciemne", "matowy", faza=0.2)
            for zn in (1, -1):
                p.blok("Piers", (zn * 0.62, 0.5, 1.02), (1.15, 0.95, 0.14), "skora", "matowy", faza=0.06)
            p.blok("Brzuch", (0, -0.62, 1.02), (1.5, 1.15, 0.12), "skora", "matowy", faza=0.06)
            p.blok("Linia brzucha", (0, -0.62, 1.09), (0.05, 1.0, 0.03), "futro_jasne", "matowy", faza=0.0)
            for y in (-0.35, -0.85):
                p.blok("Kratka brzucha", (0, y, 1.09), (1.2, 0.05, 0.03), "futro_jasne", "matowy", faza=0.0)
        for zn in (1, -1):
            p.blok("Bark", (zn * 1.72, 5.2, 0.1), (1.4, 1.3, 1.5), "futro", "matowy", rot=(0, 0, -zn * 8), faza=0.2)
            p.blok("Kepka barku", (zn * 2.18, 5.65, -0.2), (0.4, 0.3, 0.6), "futro_ciemne", "matowy",
                   rot=(0, 0, -zn * 25), faza=0.04)


def _glowa(p):
    with _model(p, "Glowa"):
        p.blok("Leb", (0, 6.1, 0.8), (1.55, 1.35, 1.35), "futro", "matowy", faza=0.15)
        p.blok("Czub", (0, 6.82, 0.62), (0.62, 0.22, 0.62), "futro_ciemne", "matowy", rot=(0, 45, 0), faza=0.06)
        p.blok("Twarz", (0, 5.98, 1.48), (1.2, 0.95, 0.1), "twarz", "matowy", faza=0.04)
        p.blok("Brew", (0, 6.35, 1.52), (1.4, 0.26, 0.24), "futro_ciemne", "matowy", faza=0.06)
        p.blok("Pysk", (0, 5.75, 1.62), (0.95, 0.5, 0.42), "twarz", "matowy", faza=0.08)
        for zn in (1, -1):
            p.blok("Oko", (zn * 0.3, 6.12, 1.535), (0.26, 0.2, 0.03), "bialy", "polysk", faza=0.0)
            p.blok("Zrenica", (zn * 0.27, 6.11, 1.55), (0.12, 0.15, 0.02), "tusz", "polysk", faza=0.0)
            p.blok("Nozdrze", (zn * 0.14, 5.88, 1.84), (0.12, 0.08, 0.03), "tusz", faza=0.0)
            p.blok("Ucho", (zn * 0.86, 6.08, 0.78), (0.24, 0.5, 0.42), "twarz", "matowy", faza=0.06)
            p.blok("Ucho srodek", (zn * 0.99, 6.08, 0.78), (0.03, 0.3, 0.24), "skora", "matowy", faza=0.0)
        # opaska z liści i czerwony kwiat za prawym uchem
        p.blok("Opaska", (0, 6.5, 0.8), (1.62, 0.18, 1.42), "lisc", "matowy", faza=0.03)
        for i, (x, rz, kol) in enumerate(((0.3, -20, "lisc"), (0.0, 0, "lisc_jasny"), (-0.3, 20, "lisc"))):
            with p.uklad(pos=(x, 6.6, 0.15), obrot=(-35, 0, rz)):
                p.blok("Lisc opaski %d" % i, (0, 0.3, 0), (0.28, 0.6, 0.06), kol, "matowy", faza=0.0)
        with p.uklad(pos=(-0.8, 6.55, 1.05), obrot=(0, -40, 0)):
            for i in range(5):
                a = math.radians(90 + i * 72)
                p.blok("Kwiat %d" % i, (0.13 * math.cos(a), 0.13 * math.sin(a), 0), (0.2, 0.2, 0.08), "kwiat",
                       "matowy", rot=(0, 0, 45 + i * 72), faza=0.0)
            p.blok("Kwiat srodek", (0, 0, 0.05), (0.12, 0.12, 0.06), "zloto", "matowy", faza=0.0)
    with _model(p, "Szczeka"):
        p.blok("Zuchwa", (0, 5.38, 1.42), (0.95, 0.36, 0.62), "twarz", "matowy", faza=0.06)
        p.blok("Usta", (0, 5.55, 1.74), (0.7, 0.05, 0.04), "tusz", faza=0.0)
        for zn in (1, -1):
            p.blok("Kiel", (zn * 0.24, 5.62, 1.72), (0.09, 0.14, 0.06), "zab", faza=0.0)


def _rece(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        with _model(p, "Ramie" + s):
            _belka(p, "Ramie", _lu((1.8, 5.45, 0.1), zn), _lu(LOKIEC, zn), 1.05, 1.05, "futro", "matowy", nad=0.1)
            p.blok("Lokiec", _lu(LOKIEC, zn), (0.95, 0.85, 0.95), "futro_ciemne", "matowy", faza=0.15)
        with _model(p, "Przedramie" + s):
            _belka(p, "Przedramie", _lu(LOKIEC, zn), _lu((2.35, 2.55, 0.55), zn), 1.15, 1.1, "futro", "matowy",
                   nad=0.05)
            _belka(p, "Karwasz", _lu((2.33, 3.05, 0.5), zn), _lu((2.35, 2.5, 0.55), zn), 1.24, 1.2, "lisc", "matowy")
            _belka(p, "Karwasz brzeg", _lu((2.33, 3.12, 0.5), zn), _lu((2.33, 3.02, 0.5), zn), 1.3, 1.26, "lisc_jasny",
                   "matowy")
        with _model(p, "Dlon" + s):
            p.blok("Piesc", _lu((2.37, 2.08, 0.62), zn), (0.95, 0.72, 0.95), "dlon", "matowy", faza=0.12)
            # palce obejmują kokos od przodu, kciuk od środka
            for i, x in enumerate((2.08, 2.28, 2.48, 2.68)):
                p.blok("Palec %d" % i, _lu((x, 1.72, 1.32), zn), (0.2, 0.42, 0.22), "dlon", "matowy",
                       rot=(18, 0, 0), faza=0.04)
            p.blok("Kciuk", _lu((1.86, 1.75, 0.95), zn), (0.22, 0.4, 0.26), "dlon", "matowy", rot=(0, 0, zn * 15),
                   faza=0.04)


def _kokosy(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        with _model(p, "Kokos" + s):
            c = _lu(KOKOS, zn)
            p.kula("Kokos", c, 2 * R_KOKOSA, "kokos", "matowy", segm=10)
            # włókna (jaśniejsze paski) i trzy oczka od dołu z przodu
            for i, ry in enumerate((-50, 10, 70)):
                with p.uklad(pos=c, obrot=(0, ry, 0)):
                    p.blok("Wlokno %d" % i, (0, 0, R_KOKOSA - 0.04), (0.08, 0.9, 0.06), "kokos_wlokno", "matowy",
                           faza=0.0)
            with p.uklad(pos=c, obrot=(35, 0, 0)):
                for i, (dx, dy) in enumerate(((-0.13, -0.08), (0.13, -0.08), (0.0, 0.12))):
                    p.blok("Oczko %d" % i, (dx, dy, R_KOKOSA - 0.02), (0.11, 0.11, 0.05), "kokos_oko", "matowy",
                           faza=0.0)


# ---------------------------------------------------------------------------------------------------- klipy
def _z(*czesci, **kosci):
    out = {}
    for c in czesci:
        out.update(c)
    out.update(kosci)
    return out


def _mix(a, b, s):
    a, b = _norm(a), _norm(b)
    return _norm(tuple(a[i] + (b[i] - a[i]) * s for i in range(3)))


def _rece_poz(ramieL=None, przedL=None, ramieP=None, przedP=None):
    """Kierunki ramion i przedramion w świecie (prawa strona to −X; None = spoczynek względem rodzica)."""
    out = {}
    for n, v in (("RamieL", ramieL), ("PrzedramieL", przedL), ("RamieP", ramieP), ("PrzedramieP", przedP)):
        if v is not None:
            out[n] = {"k": v}
    return out


def _obie(ramie, przed):
    """Obie ręce w lustrze: kierunki podane dla lewej (+X)."""
    return _rece_poz(ramie, przed, _lu(ramie, -1), _lu(przed, -1))


def _klipy(p):
    idle(p)
    ruch(p)
    atak(p)
    umiejetnosc(p)
    trafienie(p)
    unik(p)
    upadek(p)
    wiwat(p)


def idle(p, dl=72):
    """Spoczynek (2,4 s): ciężki oddech barkami, kokosy kołyszą się jak wahadła, łeb rozgląda się."""
    k = p.klip("idle", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        c = math.cos(2 * math.pi * t)
        return {"Tulow": (-2.5 * a, 0, 0.8 * c), "Glowa": (2.0 * a, 12 * math.sin(2 * math.pi * t + 0.4), 0),
                "Szczeka": (2 * max(0.0, a) ** 2, 0, 0),
                "RamieL": (4 * a, 0, 1.5 * c), "RamieP": (-4 * a, 0, -1.5 * c),
                "PrzedramieL": (-4 - 3 * a, 0, 0), "PrzedramieP": (-4 + 3 * a, 0, 0),
                "KokosL": (6 * a, 0, 0), "KokosP": (-6 * a, 0, 0)}
    _petla(k, poza)
    return k


def ruch(p, dl=30):
    """Ciężki chód w miejscu (1,0 s): pałąkowate nogi na przemian, biodra i barki kołyszą się na boki, ręce
    z kokosami wahadłem w przeciwfazie."""
    k = p.klip("ruch", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        c = math.cos(2 * math.pi * t)
        uniesL, uniesP = max(0.0, c), max(0.0, -c)
        return {"Biodra": (0, 8 * a, 5 * a), "UdoL": (-26 * a - 18 * uniesL, 0, -3), "UdoP": (26 * a - 18 * uniesP, 0, 3),
                "GolenL": (28 * uniesL, 0, 0), "GolenP": (28 * uniesP, 0, 0),
                "Tulow": (8 + 2 * math.sin(4 * math.pi * t), -10 * a, -6 * a), "Glowa": (-6, 6 * a, 4 * a),
                "RamieL": (22 * a, 0, 3), "RamieP": (-22 * a, 0, -3),
                "PrzedramieL": (-12 + 8 * a, 0, 0), "PrzedramieP": (-12 - 8 * a, 0, 0),
                "_h": 0.0}
    _petla(k, poza)
    return k


def atak(p, dl=30):
    """Sierp prawym kokosem (1,0 s): zamach za prawy bark ze skrętem tułowia (kl. 0–10), uderzenie przed siebie
    w dół (kl. 15 = trafienie), dobicie i powrót."""
    k = p.klip("atak", dl, petla=False)
    spocz = {}
    zamach = _z(_rece_poz(ramieP=(-0.8, 0.5, -0.35), przedP=(-0.35, 0.85, 0.35), ramieL=(0.45, -0.8, 0.45),
                          przedL=(0.15, -0.8, 0.6)),
                Biodra={"o": (0, -10, 0), "p": (0, 0, -0.2)}, Tulow=(-6, -26, 4), Glowa=(-4, 16, 0))
    cios = _z(_rece_poz(ramieP=(-0.2, -0.2, 1.0), przedP=(0.05, -0.7, 0.7), ramieL=(0.55, -0.75, -0.35),
                        przedL=(0.2, -0.9, -0.2)),
              Biodra={"o": (6, 8, 0), "p": (0, 0, 0.55)}, Tulow=(22, 18, -4), Glowa=(-16, -10, 0), Szczeka=(10, 0, 0),
              UdoL=(-16, 0, 0), UdoP=(10, 0, 0))
    dobicie = _z(_rece_poz(ramieP=(-0.15, -0.4, 0.9), przedP=(0.1, -0.85, 0.5), ramieL=(0.55, -0.75, -0.4),
                           przedL=(0.2, -0.9, -0.25)),
                 Biodra={"o": (7, 10, 0), "p": (0, 0, 0.6)}, Tulow=(26, 20, -4), Glowa=(-18, -12, 0), Szczeka=(6, 0, 0),
                 UdoL=(-16, 0, 0), UdoP=(10, 0, 0))
    powrot = _z(Biodra={"o": (0, 2, 0), "p": (0, 0, 0.2)}, Tulow=(6, 4, 0))
    _sekwencja(k, (0, 10, 15, 19, 25, 30), (spocz, zamach, cios, dobicie, powrot, spocz),
               wyg={0: "s", 1: "we", 2: "wy"})
    return k


def umiejetnosc(p, dl=48):
    """Cięcie (1,6 s): oba kokosy wysoko nad głowę, wspięcie i odchylenie w tył (kl. 0–16), zamach w przód (kl. 22)
    i uderzenie oboma kokosami z góry przed sobą (kl. 26 = trafienie), przysiad na ugiętych nogach, powrót."""
    k = p.klip("umiejetnosc", dl, petla=False)
    spocz = {}
    gora = _z(_obie((0.22, 1.0, -0.06), (-0.12, 0.95, 0.1)),
              Biodra={"o": (-4, 0, 0), "p": (0, 0, -0.25)}, Tulow=(-14, 0, 0), Glowa=(-12, 0, 0), Szczeka=(12, 0, 0))
    gora2 = _z(gora, Tulow=(-17, 0, 0), Glowa=(-14, 0, 0), _h=0.12)
    zamach = _z(_obie((0.2, 0.62, 0.78), (0.0, 0.42, 0.92)),
                Biodra={"o": (2, 0, 0), "p": (0, 0, 0.2)}, Tulow=(12, 0, 0), Glowa=(-14, 0, 0), Szczeka=(16, 0, 0))
    uderz = _z(_obie((0.2, -0.3, 1.0), (0.0, -0.78, 0.62)),
               Biodra={"o": (10, 0, 0), "p": (0, 0, 0.6)}, Tulow=(30, 0, 0), Glowa=(-24, 0, 0), Szczeka=(18, 0, 0),
               UdoL=(-30, 0, 4), UdoP=(-30, 0, -4), GolenL=(34, 0, 0), GolenP=(34, 0, 0))
    trzyma = _z(uderz, Glowa=(-20, 0, 0), Szczeka=(8, 0, 0))
    _sekwencja(k, (0, 12, 16, 22, 26, 36, 48), (spocz, gora, gora2, zamach, uderz, trzyma, spocz),
               wyg={0: "s", 2: "we", 3: "wy"})
    return k


def trafienie(p, dl=20):
    """Szarpnięcie w tył (0,67 s, najdalej kl. 4): tułów odchylony, łeb w górę, ręce z kokosami na boki."""
    k = p.klip("trafienie", dl, petla=False)
    spocz = {}
    szarp = _z(Biodra={"o": (-4, 0, 0), "p": (0, 0, -0.45)}, Tulow=(-12, 4, 3), Glowa=(-14, 0, 4), Szczeka=(12, 0, 0),
               RamieL=(8, 0, 14), RamieP=(10, 0, -14))
    odb = _z(Biodra={"o": (2, 0, 0), "p": (0, 0, -0.15)}, Tulow=(4, -2, -1), Glowa=(4, 0, -1))
    _sekwencja(k, (0, 4, 12, 20), (spocz, szarp, odb, spocz), wyg={0: "wy"})
    return k


def unik(p, dl=30):
    """Ciężki krok w lewo o 1,5 studa (najdalej kl. 14) i powrót (1,0 s)."""
    k = p.klip("unik", dl, petla=False)
    spocz = {}
    przenies = _z(Biodra={"o": (0, 0, -5), "p": (0.2, 0, 0)}, Tulow=(0, 0, -4), UdoL=(0, 0, 14))
    krok = _z(Biodra={"o": (0, -6, 6), "p": (1.0, 0, 0)}, Tulow=(0, 0, 6), UdoL=(0, 0, 8), UdoP=(0, 0, 10),
              RamieP=(0, 0, -10), _h=0.15)
    stoi = _z(Biodra={"o": (0, -8, 3), "p": (1.5, 0, 0)}, Tulow=(2, 6, 2), Glowa=(0, -12, 0))
    wraca = _z(Biodra={"o": (0, -3, -4), "p": (0.7, 0, 0)}, UdoP=(0, 0, -10), Tulow=(0, 0, -3), _h=0.1)
    _sekwencja(k, (0, 5, 10, 14, 21, 30), (spocz, przenies, krok, stoi, wraca, spocz), wyg={1: "we", 2: "wy"})
    return k


def upadek(p, dl=60):
    """Upadek (2 s): zatacza się, ciężko siada, pada na plecy z rozrzuconymi rękami, kokosy leżą obok dłoni
    (kl. 60 = leży)."""
    k = p.klip("upadek", dl, petla=False)
    spocz = {}
    chwiej = _z(Biodra={"o": (-4, 6, 6), "p": (0, 0, -0.3)}, Tulow=(-10, 6, 8), Glowa=(-10, 10, 6),
                RamieL=(6, 0, 16), RamieP=(10, 0, -8))
    chwiej2 = _z(Biodra={"o": (6, -8, -6), "p": (0, 0, -0.2)}, Tulow=(12, -6, -8), Glowa=(16, -6, -8),
                 RamieL=(-6, 0, 10), RamieP=(-8, 0, -14))
    siada = _z(_obie((0.75, -0.6, 0.2), (0.55, -0.8, 0.3)),
               Biodra={"o": (-20, 0, 0), "p": (0, 0, -0.6)}, Tulow=(10, 0, 0), Glowa=(10, 0, 0), Szczeka=(14, 0, 0),
               UdoL=(-70, 0, 12), UdoP=(-70, 0, -12), GolenL=(40, 0, 0), GolenP=(40, 0, 0), _wolne=True)
    lezy = _z(_obie((1.0, -0.15, 0.15), (0.9, -0.3, 0.35)),
              Biodra={"o": (-84, 0, 0), "p": (0, 0, -1.6)}, Tulow=(-4, 0, 0), Glowa=(-16, 12, 0), Szczeka=(18, 0, 0),
              UdoL=(-40, 0, 14), UdoP=(-34, 0, -14), GolenL=(30, 0, 0), GolenP=(26, 0, 0), _wolne=True)
    _sekwencja(k, (0, 10, 20, 32, 46, 60), (spocz, chwiej, chwiej2, siada, lezy, lezy),
               wyg={2: "we", 3: "wy", 4: "l"})
    return k


def wiwat(p, dl=60):
    """Radość (pętla 2 s): dwa razy stuka kokosami wysoko nad głową (kl. 10 i 22), potem poza siłacza — oba bicepsy
    napięte, kokosy przy barkach (kl. 36–50)."""
    k = p.klip("wiwat", dl, petla=True)
    spocz = {}
    rozloz = _z(_obie((0.55, 0.85, 0.15), (0.2, 0.95, 0.25)),
                Tulow=(-8, 0, 0), Glowa=(-14, 0, 0), Szczeka=(14, 0, 0))
    stuk = _z(_obie((0.42, 0.9, 0.22), (-0.84, 0.52, 0.25)),
              Tulow=(-10, 0, 0), Glowa=(-18, 0, 0), Szczeka=(20, 0, 0), _h=0.1)
    biceps = _z(_obie((1.0, 0.12, 0.08), (-0.1, 1.0, 0.2)),
                Biodra={"o": (0, 0, 0), "p": (0, -0.1, 0)}, Tulow=(-4, 0, 0), Glowa=(-6, 0, 0), Szczeka=(8, 0, 0),
                UdoL=(0, 0, 8), UdoP=(0, 0, -8))
    biceps2 = _z(biceps, Tulow=(-4, 10, 0), Glowa=(-6, -12, 0))
    _sekwencja(k, (0, 6, 10, 16, 22, 28, 36, 43, 50, 60),
               (spocz, rozloz, stuk, rozloz, stuk, rozloz, biceps, biceps2, biceps, spocz),
               wyg={1: "we", 3: "we", 8: "s"})
    return k


# =============================================================== animacja: pozy kluczowe -> klucz w każdej klatce
# (ten sam zestaw pomocników co w modułach potworów Bagna — rechotek, bulgotnik, klodoklap, ropucha_z_chatka,
#  straznik_topieli — i Dżungli: zwijogon, gebokwiat, kokosowy_silacz, pancernik_ruin, waz_stu_lian). Poza = {kość: (rx, ry, rz) | {"o": obrót, "p": przesunięcie, "k": kierunek osi OS[kość] w
#  świecie}}; "_h" = wysokość najniższego punktu ciała nad ziemią (domyślnie 0), "_wolne" = kości PLASKIE nie są
#  trzymane poziomo (lot, przewrót); w Dżungli "_wolne" może też być krotką nazw kości — wtedy tylko one idą za
#  rodzicem (np. łapa uniesiona do ciosu), a reszta zostaje płasko. Brak kości w pozie = spoczynek tej kości.
I3 = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
ZERO = (0.0, 0.0, 0.0)


def _T(R):
    return tuple(tuple(R[j][i] for j in range(3)) for i in range(3))


def _norm(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return tuple(x / n for x in v)


def _obrot_miedzy(a, b):
    """Macierz najkrótszego obrotu, który przenosi kierunek a na kierunek b."""
    a, b = _norm(a), _norm(b)
    o = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    s, c = math.sqrt(sum(x * x for x in o)), sum(a[i] * b[i] for i in range(3))
    if s < 1e-9:
        return I3
    x, y, z = (v / s for v in o)
    t = 1.0 - c
    return ((t * x * x + c, t * x * y - s * z, t * x * z + s * y),
            (t * x * y + s * z, t * y * y + c, t * y * z - s * x),
            (t * x * z - s * y, t * y * z + s * x, t * z * z + c))


def _belka(p, nazwa, a, b, szer, gleb, kolor, mat="zwykly", nad=0.0, faza=None, ksztalt="blok"):
    """Klocek (albo elipsoida: ksztalt="kula", walec: "walec") od punktu a do punktu b (bieżący układ; oś Y bryły
    wzdłuż a→b, nad = wydłużenie z obu końców). Zwraca (środek, obrót) — układ do dokładania brył wzdłuż belki."""
    d = tuple(b[i] - a[i] for i in range(3))
    L = math.sqrt(sum(x * x for x in d))
    sr = tuple((a[i] + b[i]) / 2.0 for i in range(3))
    rot = katy_z_macierzy(_obrot_miedzy((0.0, 1.0, 0.0), d))
    if ksztalt == "kula":
        p.kula(nazwa, sr, (szer, L + 2 * nad, gleb), kolor, mat, rot=rot)
    elif ksztalt == "walec":
        p.walec(nazwa, sr, (szer, L + 2 * nad, gleb), kolor, mat, rot=rot, faza=faza)
    else:
        p.blok(nazwa, sr, (szer, L + 2 * nad, gleb), kolor, mat, rot=rot, faza=faza)
    return sr, rot


def _krok(p, W, n, o, pr):
    k = p.kosci[n]
    Rl = macierz_obrotu(*o)
    if k["rodzic"] is None:
        W[n] = (Rl, tuple(k["staw"][i] + pr[i] for i in range(3)))
    else:
        Rp, tp = W[k["rodzic"]]
        st = p.kosci[k["rodzic"]]["staw"]
        d = razy_wektor(Rp, tuple(k["staw"][i] - st[i] + pr[i] for i in range(3)))
        W[n] = (mnoz(Rp, Rl), tuple(tp[i] + d[i] for i in range(3)))


def _fk(p, lok):
    W = {}
    for n in p.kosci:
        o, pr = lok.get(n, (ZERO, ZERO))
        _krok(p, W, n, o, pr)
    return W


def _naroza(p):
    """Narożniki brył względem stawu ich kości (do dociągania do ziemi), liczone raz."""
    if getattr(p, "_bagno_naroza", None) is None:
        out = {}
        for c in p.czesci:
            R = macierz_obrotu(*c["r"])
            h = [v / 2.0 for v in c["s"]]
            for sx in (-1, 1):
                for sy in (-1, 1):
                    for sz in (-1, 1):
                        q = razy_wektor(R, (sx * h[0], sy * h[1], sz * h[2]))
                        out.setdefault(c["kosc"], []).append(tuple(c["p"][i] + q[i] for i in range(3)))
        p._bagno_naroza = out
    return p._bagno_naroza


def _najnizej(p, W, pomin=()):
    mn = 1e9
    for kosc, pkt in _naroza(p).items():
        if kosc in pomin:
            continue
        R, t = W[kosc]
        for q in pkt:
            y = R[1][0] * q[0] + R[1][1] * q[1] + R[1][2] * q[2] + t[1]
            if y < mn:
                mn = y
    return mn


def _rozwiaz(p, poza):
    """Poza kluczowa -> {kość: (obrót lokalny, przesunięcie)}; kierunki "k" zamienione na obroty lokalne."""
    lok, W = {}, {}
    for n, k in p.kosci.items():
        v = poza.get(n)
        o, pr, kier = ZERO, ZERO, None
        if isinstance(v, dict):
            o, pr, kier = tuple(v.get("o", ZERO)), tuple(v.get("p", ZERO)), v.get("k")
        elif v is not None:
            o = tuple(v)
        if kier is not None:
            Rp = W[k["rodzic"]][0] if k["rodzic"] else I3
            o = katy_z_macierzy(mnoz(_T(Rp), _obrot_miedzy(OS[n], kier)))
        lok[n] = (tuple(o), tuple(pr))
        _krok(p, W, n, lok[n][0], lok[n][1])
    return lok


def _plasko(p, lok, wolne=()):
    """Kości PLASKIE (bez `wolne`): poziomo w świecie, z odchyleniem (yaw) rodzica."""
    W = {}
    for n, k in p.kosci.items():
        o, pr = lok.get(n, (ZERO, ZERO))
        if n in PLASKIE and n not in wolne:
            Rp = W[k["rodzic"]][0]
            f = razy_wektor(Rp, (0.0, 0.0, 1.0))
            yaw = math.degrees(math.atan2(f[0], f[2])) if abs(f[0]) + abs(f[2]) > 1e-6 else 0.0
            o = katy_z_macierzy(mnoz(_T(Rp), macierz_obrotu(0.0, yaw, 0.0)))
            lok[n] = (o, pr)
        _krok(p, W, n, o, pr)
    return W


def _wolne(*pozy):
    """(płasko?, wolne kości) z pól "_wolne" póz: True = żadna kość PLASKIE nie jest trzymana poziomo."""
    wolne = set()
    for pz in pozy:
        w = pz.get("_wolne")
        if w is True:
            return False, ()
        if w:
            wolne.update(w)
    return True, tuple(wolne)


def _uziem(p, lok, h, plasko=True, wolne=()):
    W = _plasko(p, lok, wolne) if plasko else _fk(p, lok)
    dno = _najnizej(p, W, POMIN_ZIEMIA)
    o, pr = lok[GLOWNA]
    lok[GLOWNA] = (o, (pr[0], pr[1] + h - dno, pr[2]))


def _ciaglosc(ob, poprz):
    """Ten sam obrót zapisany kątami najbliższymi poprzedniemu kluczowi (bez skoku przez ±180°)."""
    if poprz is None:
        return tuple(ob)

    def blisko(a, b):
        return a + 360.0 * round((b - a) / 360.0)
    najl = None
    for c in (tuple(ob), (180.0 - ob[0], ob[1] + 180.0, ob[2] + 180.0)):
        c = tuple(blisko(c[i], poprz[i]) for i in range(3))
        d = sum(abs(c[i] - poprz[i]) for i in range(3))
        if najl is None or d < najl[0] - 1e-6:
            najl = (d, c)
    return najl[1]


def _cr(a, b, c, d, t):
    return 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)


def _kw(R):
    """Macierz obrotu -> kwaternion (w, x, y, z)."""
    tr = R[0][0] + R[1][1] + R[2][2]
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        q = (0.25 * s, (R[2][1] - R[1][2]) / s, (R[0][2] - R[2][0]) / s, (R[1][0] - R[0][1]) / s)
    elif R[0][0] > R[1][1] and R[0][0] > R[2][2]:
        s = math.sqrt(1.0 + R[0][0] - R[1][1] - R[2][2]) * 2
        q = ((R[2][1] - R[1][2]) / s, 0.25 * s, (R[0][1] + R[1][0]) / s, (R[0][2] + R[2][0]) / s)
    elif R[1][1] > R[2][2]:
        s = math.sqrt(1.0 + R[1][1] - R[0][0] - R[2][2]) * 2
        q = ((R[0][2] - R[2][0]) / s, (R[0][1] + R[1][0]) / s, 0.25 * s, (R[1][2] + R[2][1]) / s)
    else:
        s = math.sqrt(1.0 + R[2][2] - R[0][0] - R[1][1]) * 2
        q = ((R[1][0] - R[0][1]) / s, (R[0][2] + R[2][0]) / s, (R[1][2] + R[2][1]) / s, 0.25 * s)
    return _norm(q)


def _z_kw(q):
    w, x, y, z = _norm(q)
    return ((1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)),
            (2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)),
            (2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)))


def _bliski(q, wzor):
    return q if sum(q[i] * wzor[i] for i in range(4)) >= 0 else tuple(-v for v in q)


def _slerp(a, b, t):
    b = _bliski(b, a)
    c = max(-1.0, min(1.0, sum(a[i] * b[i] for i in range(4))))
    kat = math.acos(c)
    if kat < 1e-5:
        return _norm(tuple(a[i] + (b[i] - a[i]) * t for i in range(4)))
    sa, sb = math.sin((1 - t) * kat) / math.sin(kat), math.sin(t * kat) / math.sin(kat)
    return tuple(sa * a[i] + sb * b[i] for i in range(4))


def _wygladz(t, tryb):
    if tryb == "l":
        return t
    if tryb == "we":
        return t * t
    if tryb == "wy":
        return 1.0 - (1.0 - t) * (1.0 - t)
    return t * t * (3.0 - 2.0 * t)


def _zapisz(k, f, lok):
    for n, (o, pr) in lok.items():
        if n == "Root":
            continue
        k.klucz(f, n, obrot=tuple(round(x, 3) for x in o), przes=tuple(round(x, 4) for x in pr), wyg="liniowo")


def _ciagle_katy(lok, poprz):
    """Kąty każdej kości zapisane najbliżej poprzedniej klatki (Euler bez skoków)."""
    for n, (o, pr) in lok.items():
        o = _ciaglosc(o, poprz.get(n))
        poprz[n] = o
        lok[n] = (o, pr)


def _sekwencja(k, czasy, pozy, wyg=None, domyslnie="s", ziemia=True, po=None):
    """Klucz w KAŻDEJ klatce między pozami kluczowymi (obroty kości przez kwaterniony, więc duże obroty łap nie
    kręcą się po kątach). wyg = {numer odcinka: "s" | "l" | "we" | "wy" | "cr"}: s = łagodnie, l = jednostajnie,
    we = przyspiesza (w uderzenie), wy = hamuje (po wybiciu), cr = płynnie przez pozy. ziemia = najniższy punkt
    brył (bez POMIN_ZIEMIA) na wysokości "_h" pozy. po(f, lok) — dopiski w klatce. Klip zapętlony: ostatnia klatka
    = pierwsza."""
    p = k.postac
    n_poz = len(pozy)
    kosci = [n for n in p.kosci if n != "Root"]
    tab = []
    for pz in pozy:
        lok = _rozwiaz(p, pz)
        tab.append({n: (_kw(macierz_obrotu(*lok[n][0])), lok[n][1]) for n in kosci})
    for i in range(1, n_poz):
        for n in kosci:
            tab[i][n] = (_bliski(tab[i][n][0], tab[i - 1][n][0]), tab[i][n][1])

    def sasiad(i):
        if k.petla:
            if i < 0:
                return i + n_poz - 1
            if i > n_poz - 1:
                return i - n_poz + 1
            return i
        return max(0, min(n_poz - 1, i))

    poprz, pierwsza = {}, None
    for f in range(int(czasy[0]), int(czasy[-1]) + 1):
        if k.petla and f == k.dlugosc and pierwsza is not None:
            _zapisz(k, f, pierwsza)
            continue
        i = max(j for j in range(n_poz - 1) if czasy[j] <= f) if f < czasy[-1] else n_poz - 2
        t = (f - czasy[i]) / float(czasy[i + 1] - czasy[i])
        tryb = (wyg or {}).get(i, domyslnie)
        e = _wygladz(t, tryb)
        lok = {}
        for n in kosci:
            if tryb == "cr":
                ia, id_ = sasiad(i - 1), sasiad(i + 2)
                qb = tab[i][n][0]
                qa, qc, qd = (_bliski(tab[ia][n][0], qb), _bliski(tab[i + 1][n][0], qb),
                              _bliski(tab[id_][n][0], qb))
                q = _norm(tuple(_cr(qa[j], qb[j], qc[j], qd[j], t) for j in range(4)))
                pa, pb, pc, pd = (tab[ia][n][1], tab[i][n][1], tab[i + 1][n][1], tab[id_][n][1])
                pr = tuple(_cr(pa[j], pb[j], pc[j], pd[j], t) for j in range(3))
            else:
                q = _slerp(tab[i][n][0], tab[i + 1][n][0], e)
                a, b = tab[i][n][1], tab[i + 1][n][1]
                pr = tuple(a[j] + (b[j] - a[j]) * e for j in range(3))
            lok[n] = (katy_z_macierzy(_z_kw(q)), pr)
        h0, h1 = pozy[i].get("_h", 0.0), pozy[i + 1].get("_h", 0.0)
        plasko, wolne = _wolne(pozy[i], pozy[i + 1])
        if ziemia:
            _uziem(p, lok, h0 + (h1 - h0) * e, plasko, wolne)
        elif plasko:
            _plasko(p, lok, wolne)
        if po:
            po(f, lok)
        _ciagle_katy(lok, poprz)
        if pierwsza is None:
            pierwsza = dict(lok)
        _zapisz(k, f, lok)
    return k


def _petla(k, poza, ziemia=True):
    """Klip zapętlony z funkcji poza(t), t = 0…1 (okresowa); ostatnia klatka = pierwsza (bez szwu)."""
    p = k.postac
    pierwsza, poprz = None, {}
    for f in range(k.dlugosc):
        pz = poza(f / float(k.dlugosc))
        lok = _rozwiaz(p, pz)
        if ziemia:
            plasko, wolne = _wolne(pz)
            _uziem(p, lok, pz.get("_h", 0.0), plasko, wolne)
        _ciagle_katy(lok, poprz)
        _zapisz(k, f, lok)
        if pierwsza is None:
            pierwsza = dict(lok)
    _zapisz(k, k.dlugosc, pierwsza)
    return k
