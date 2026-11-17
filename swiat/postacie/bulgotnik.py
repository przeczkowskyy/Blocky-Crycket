# -*- coding: utf-8 -*-
"""BULGOTNIK — zwykły przeciwnik Bagna (Bulgotne Trzęsawisko): mały błotny szaman, ok. 4,2 studa (gracz ma 5,7).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/bulgotnik.py --wyj <folder> --klip umiejetnosc

Opis z planu Bagna (swiat/bagno_pas/README.md, rozdz. „Potwory”): mały błotny szaman — kopczyk z błota na krótkich
nóżkach, głowa to bańka gazu z oczami, kij z ognikiem. Klasa w przegrodzie: Mag. Bije słabo kijem, „bańka gazu”
rani magią; umiejętność silnika `bariera` = tarcza na siebie.

Sylwetka (z daleka): schodkowy brązowy kopiec (szerszy u dołu) na dwóch krótkich nóżkach, na czubku wielka
jasnozielona bańka z dwojgiem wyłupiastych oczu, w prawej ręce krzywy kij wyższy od kopca ze świecącą zielonożółtą
kulą (Neon) w szponie z trzech gałązek; na grzbiecie kilka bąbli gazu i dwie pałki trzciny.

Paleta: błoto 5B4A34 (dwa odcienie), bańka 9FD89A, ognik C8E05A (Neon), mech A9B48E, trzcina B59A52, drewno kija.

Szkielet (typ „stwor”; L = lewa = +X, P = prawa = −X):
    Root > Cialo > {Glowa > {BankaL, BankaP, BankaG}, RamieL, RamieP > Kij, NogaL > StopaL, NogaP > StopaP}
- `Cialo` niesie cały kopiec; Stopa* trzymane płasko na ziemi (liczone w module);
- bańka-głowa = rdzeń na `Glowa` i trzy płaty na kościach BankaL/BankaP/BankaG: przy „nadymaniu” płaty odsuwają się
  od rdzenia (przesunięcie, bez kanału skali), więc bańka rośnie o ok. 35%;
- `Kij` siedzi w prawej dłoni (OgnikAttachment w środku ognika).

Klipy (30 kl./s; patrzy w +Z):
  idle (pętla 2,4 s: kołysanie, bańka „oddycha”, rozgląda się), ruch (pętla 0,8 s: drepcze na nóżkach, kij jak
  laska), atak (uderzenie kijem z góry, trafienie kl. 13, 0,9 s), umiejetnosc (bariera: kij w górę, bańka się
  nadyma, obrót wokół siebie z ognikiem nad głową, uderzenie kijem w ziemię kl. 40 = krąg, 1,9 s),
  trafienie (szarpnięcie w tył, bańka się trzęsie, 0,6 s), unik (podskok w lewo 1,4 studa i powrót, 0,9 s),
  upadek (chwieje się, pada na plecy, bańka sflaczała, kopiec zapada się w błoto; 2 s, leży w ostatniej klatce),
  wiwat (pętla 2 s: podskoki z kijem w górze, bańka pulsuje).
Klipy są zapisane jako pozy kluczowe zamienione na klucz w KAŻDEJ klatce (wygładzanie „liniowo”).
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Postac, katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor

ID = "bulgotnik"

PALETA = {
    "bloto": "5B4A34", "bloto_ciemne": "45372A", "bloto_jasne": "75603F",
    "banka": "9FD89A", "banka_ciemna": "79BC7A", "ognik": "C8E05A",
    "mech": "A9B48E", "trzcina": "B59A52", "palka": "5E3F26",
    "drewno": "6B4F33", "drewno_ciemne": "4A3522",
    "bialy": "F4F6EE", "tusz": "1C1A14", "muszla": "E6DCC0",
}

CHWILE = {"atak": 13, "umiejetnosc": 40, "trafienie": 4, "unik": 12}

SLABOSCI = [
    "Kości Bulgotnika nie są R15 (własny szkielet: Root + 12 kości) — import do Roblox Studio nie był testowany.",
    "Bańka jest nieprzezroczysta: format rigu nie niesie przezroczystości (w Studio można dać Transparency ok. 0,3 "
    "rdzeniowi i płatom). Oczy siedzą na przedniej ściance bańki, więc widać je i bez przezroczystości.",
    "Nadymanie bańki to rozsunięcie trzech płatów od rdzenia (bez skali) — z bliska widać, że to cztery bryły.",
    "Świecenie ognika: materiał Neon na rigu z klocków; poświaty (PointLight) nie ma.",
    "Kij przechodzi przez prawą dłoń (dłoń go „obejmuje”); w ataku i barierze dolny koniec kija może wejść w ziemię.",
    "Krąg bariery (aura) robi odtwarzacz (styl „na_siebie”) — klip daje obrót z kijem i uderzenie w ziemię.",
]

# ----------------------------------------------------------------------------------------------- szkielet (studs)
CIALO = (0.0, 0.7, 0.0)
GLOWA = (0.0, 2.5, 0.0)
RDZEN = (0.0, 3.35, 0.05)           # środek rdzenia bańki
BANKA_L = (0.45, 3.35, 0.0)
BANKA_G = (0.0, 3.8, 0.0)
BARK = (0.95, 2.0, 0.05)
DLON = (1.22, 1.2, 0.22)
BIODRO = (0.5, 0.6, 0.0)
KOSTKA = (0.5, 0.15, 0.05)
OGNIK = (-1.12, 3.52, 0.12)        # środek świecącej kuli (prawa ręka = −X)

GLOWNA = "Cialo"
PLASKIE = ("StopaL", "StopaP")
POMIN_ZIEMIA = ("Kij",)
OS = {"Kij": (0.13, 3.08, -0.18)}      # oś kija (dolny koniec -> szpon) — pozy z kierunkiem „k”


def _lu(v, zn):
    return (zn * v[0], v[1], v[2])


def _model(p, kosc, obrot=(0, 0, 0), pos=(0, 0, 0)):
    """Układ MODELU (0, 0, 0 = ziemia pod środkiem) na kości: bryły podaje się we współrzędnych modelu."""
    s = p.staw(kosc)
    return p.na(kosc, pos=(pos[0] - s[0], pos[1] - s[1], pos[2] - s[2]), obrot=obrot)


def zbuduj():
    p = Postac(ID, "Bulgotnik", typ="stwor", skala=1.0, faza=0.05, paleta=PALETA)

    p.kosc("Cialo", "Root", staw=CIALO, dl=0.6)
    p.kosc("Glowa", "Cialo", staw=GLOWA, dl=0.5)
    p.kosc("BankaL", "Glowa", staw=BANKA_L, dl=0.3)
    p.kosc("BankaP", "Glowa", staw=_lu(BANKA_L, -1), dl=0.3)
    p.kosc("BankaG", "Glowa", staw=BANKA_G, dl=0.3)
    for s, zn in (("L", 1.0), ("P", -1.0)):
        p.kosc("Ramie" + s, "Cialo", staw=_lu(BARK, zn), dl=0.4)
        p.kosc("Noga" + s, "Cialo", staw=_lu(BIODRO, zn), dl=0.3)
        p.kosc("Stopa" + s, "Noga" + s, staw=_lu(KOSTKA, zn), dl=0.2)
    p.kosc("Kij", "RamieP", staw=_lu(DLON, -1), dl=0.8)

    _nogi(p)
    _kopiec(p)
    _banka(p)
    _rece(p)
    _kij(p)

    p.zaczep("RootAttachment", "Cialo", (-CIALO[0], -CIALO[1], -CIALO[2]))
    p.zaczep("GlowaAttachment", "Glowa", tuple(RDZEN[i] - GLOWA[i] for i in range(3)))
    p.zaczep("OgnikAttachment", "Kij", tuple(OGNIK[i] - _lu(DLON, -1)[i] for i in range(3)))

    _klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return p


# ---------------------------------------------------------------------------------------------------- bryły
def _nogi(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        with _model(p, "Noga" + s):
            p.blok("Noga", _lu((0.5, 0.4, 0.0), zn), (0.42, 0.55, 0.45), "bloto_ciemne", "matowy", faza=0.08)
        with _model(p, "Stopa" + s):
            p.blok("Stopa", _lu((0.52, 0.08, 0.12), zn), (0.55, 0.16, 0.7), "bloto_ciemne", "matowy", faza=0.05)
            for i, (x, ry) in enumerate(((0.38, -15), (0.66, 18))):
                p.blok("Korzonek %d" % i, _lu((x, 0.05, 0.52), zn), (0.12, 0.09, 0.32), "drewno",
                       "matowy", rot=(0, zn * ry, 0), faza=0.02)


def _kopiec(p):
    with _model(p, "Cialo"):
        # schodkowy kopiec z błota, każdy stopień lekko przesunięty (krzywy, ulepiony ręcznie)
        p.blok("Kopiec 1", (0, 0.95, -0.05), (2.3, 0.65, 1.95), "bloto", "matowy", faza=0.12)
        p.blok("Kopiec 2", (0.05, 1.55, -0.08), (2.05, 0.6, 1.75), "bloto", "matowy", faza=0.12)
        p.blok("Kopiec 3", (-0.04, 2.08, -0.1), (1.7, 0.5, 1.45), "bloto", "matowy", faza=0.1)
        p.blok("Kopiec 4", (0.0, 2.42, -0.1), (1.25, 0.3, 1.1), "bloto_jasne", "matowy", faza=0.08)
        # grudy na brzegach stopni
        for i, (pos, sz) in enumerate((((1.05, 1.0, 0.55), (0.5, 0.45, 0.5)), ((-1.1, 1.05, -0.4), (0.45, 0.5, 0.6)),
                                       ((0.85, 1.6, -0.6), (0.45, 0.4, 0.45)), ((-0.9, 1.5, 0.45), (0.4, 0.4, 0.4)),
                                       ((0.6, 2.1, 0.45), (0.38, 0.3, 0.38)))):
            p.blok("Gruda %d" % i, pos, sz, "bloto_ciemne", "matowy", faza=0.08)
        # zacieki błota na przodzie i bokach (wystają 0,03)
        for i, (x, y, h) in enumerate(((-0.55, 1.05, 0.5), (0.2, 0.95, 0.4), (0.7, 1.55, 0.42), (-0.3, 1.6, 0.36))):
            z = 0.93 if y < 1.25 else 0.81
            p.blok("Zaciek %d" % i, (x, y, z), (0.18, h, 0.06), "bloto_jasne", "matowy", faza=0.0)
        for zn in (1, -1):
            p.blok("Zaciek bok", (zn * 1.165, 1.0, 0.1), (0.06, 0.42, 0.22), "bloto_jasne", "matowy", faza=0.0)
        # naszyjnik z muszli ślimaków (jasne kropki na brzuchu — akcent pod bańką)
        for i, (x, y) in enumerate(((-0.6, 1.72), (-0.3, 1.62), (0.0, 1.58), (0.3, 1.62), (0.6, 1.72))):
            p.blok("Muszla %d" % i, (x, y, 0.79), (0.16, 0.16, 0.08), "muszla", "polysk", rot=(0, 0, 45), faza=0.02)
        # mech na stopniach
        for i, (pos, sz) in enumerate((((-0.55, 1.88, 0.2), (0.6, 0.06, 0.5)), ((0.6, 2.36, -0.3), (0.45, 0.06, 0.5)),
                                       ((0.7, 1.29, -0.5), (0.6, 0.06, 0.6)))):
            p.blok("Mech %d" % i, pos, sz, "mech", "matowy", faza=0.0)
        # bąble gazu na grzbiecie (do połowy w błocie)
        for i, (pos, r) in enumerate((((0.4, 2.0, -0.78), 0.42), ((-0.5, 1.62, -0.92), 0.5), ((0.1, 2.45, -0.6), 0.34),
                                      ((-0.25, 1.15, -1.0), 0.38), ((0.75, 1.42, -0.93), 0.34))):
            p.kula("Babel %d" % i, pos, r, "banka", "polysk", segm=8)
        # dwie pałki trzciny wbite w grzbiet (kolce sylwetki)
        for i, (x, rz, rx, h) in enumerate(((-0.45, 14, 22, 1.3), (-0.15, -6, 30, 1.05))):
            with p.uklad(pos=(x, 2.0, -0.55), obrot=(rx * -1, 0, rz)):
                p.blok("Trzcina %d" % i, (0, h / 2, 0), (0.07, h, 0.07), "trzcina", "matowy", faza=0.0)
                p.blok("Palka %d" % i, (0, h - 0.12, 0), (0.15, 0.32, 0.15), "palka", "matowy", faza=0.03)


def _banka(p):
    with _model(p, "Glowa"):
        p.blok("Kolnierz", (0, 2.62, 0.0), (1.35, 0.22, 1.2), "bloto_ciemne", "matowy", faza=0.06)
        p.kula("Banka rdzen", RDZEN, 1.45, "banka", "polysk", segm=12)
        # oczy na przedniej ściance bańki (wyłupiaste, zezujące lekko do środka) i krzywy uśmiech
        for zn in (1, -1):
            x = zn * 0.3
            p.kula("Oko", (x, 3.4, 0.72), 0.4, "bialy", "polysk", segm=8)
            p.blok("Zrenica", (x - zn * 0.04, 3.38, 0.92), (0.15, 0.2, 0.05), "tusz", "polysk", faza=0.0)
            p.blok("Blysk oka", (x - zn * 0.02, 3.46, 0.945), (0.06, 0.06, 0.02), "bialy", faza=0.0)
        p.blok("Usta", (0.04, 3.0, 0.7), (0.34, 0.06, 0.05), "banka_ciemna", "matowy", rot=(0, 0, -8), faza=0.0)
        p.blok("Odblask", (0.36, 3.78, 0.55), (0.28, 0.1, 0.04), "bialy", "polysk", rot=(-33, 35, 0), faza=0.0)
    # płaty bańki (odsuwają się przy nadymaniu)
    for s, zn in (("L", 1.0), ("P", -1.0)):
        with _model(p, "Banka" + s):
            p.kula("Plat " + s, _lu((0.5, 3.35, -0.02), zn), (0.75, 1.15, 1.1), "banka", "polysk", segm=12)
            p.blok("Wir " + s, _lu((0.86, 3.25, 0.0), zn), (0.04, 0.3, 0.42), "banka_ciemna", "matowy", faza=0.0)
    with _model(p, "BankaG"):
        p.kula("Plat G", (0, 3.88, -0.02), (1.05, 0.6, 1.0), "banka", "polysk", segm=12)
        p.kula("Babelek", (-0.32, 4.1, -0.15), 0.22, "banka_ciemna", "polysk", segm=8)


def _rece(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        with _model(p, "Ramie" + s):
            _belka(p, "Ramie", _lu((0.88, 2.08, 0.05), zn), _lu(DLON, zn), 0.3, 0.3, "bloto_ciemne", "matowy")
            p.blok("Dlon", _lu((1.22, 1.17, 0.22), zn), (0.36, 0.32, 0.36), "bloto_ciemne", "matowy", faza=0.06)
            p.blok("Palec", _lu((1.12, 1.02, 0.42), zn), (0.1, 0.24, 0.1), "drewno", "matowy", rot=(30, 0, 0),
                   faza=0.0)


def _kij(p):
    """Krzywy kij z korzenia (prawa ręka): trzy wygięte odcinki, u góry szpon z trzech gałązek trzyma świecącą kulę."""
    with _model(p, "Kij"):
        pkt = ((-1.25, 0.12, 0.3), (-1.2, 1.3, 0.22), (-1.29, 2.4, 0.2), (-1.12, 3.2, 0.12))
        for i in range(3):
            _belka(p, "Kij %d" % i, pkt[i], pkt[i + 1], 0.17, 0.17, "drewno", "matowy", nad=0.04)
        p.blok("Sek", (-1.27, 1.85, 0.21), (0.24, 0.1, 0.24), "drewno_ciemne", "matowy", faza=0.02)
        p.blok("Owijka", (-1.21, 1.42, 0.22), (0.23, 0.14, 0.23), "mech", "matowy", faza=0.02)
        # szpon: trzy gałązki wokół kuli
        for i, (dx, dz) in enumerate(((0.26, 0.0), (-0.16, 0.2), (-0.14, -0.2))):
            a = (OGNIK[0] + dx * 0.3, 3.18, OGNIK[2] + dz * 0.3)
            b = (OGNIK[0] + dx, 3.5, OGNIK[2] + dz)
            c = (OGNIK[0] + dx * 0.6, 3.82, OGNIK[2] + dz * 0.6)
            _belka(p, "Galazka %d" % i, a, b, 0.08, 0.08, "drewno_ciemne", "matowy")
            _belka(p, "Pazur %d" % i, b, c, 0.07, 0.07, "drewno_ciemne", "matowy")
        p.kula("Ognik", OGNIK, 0.44, "ognik", "swiecacy", segm=8)
        p.blok("Plomyk", (OGNIK[0] + 0.04, 3.88, OGNIK[2]), (0.14, 0.24, 0.14), "ognik", "swiecacy", rot=(0, 45, 12),
               faza=0.0)
        p.blok("Plomyk 2", (OGNIK[0] - 0.1, 3.8, OGNIK[2] + 0.05), (0.09, 0.15, 0.09), "ognik", "swiecacy",
               rot=(0, 45, -18), faza=0.0)


# ---------------------------------------------------------------------------------------------------- klipy
def _z(*czesci, **kosci):
    out = {}
    for c in czesci:
        out.update(c)
    out.update(kosci)
    return out


def _nadmij(s):
    """Płaty bańki odsunięte od rdzenia o s (0 = spoczynek, 1 = nadęta)."""
    return {"BankaL": {"p": (0.28 * s, 0.04 * s, 0.0)}, "BankaP": {"p": (-0.28 * s, 0.04 * s, 0.0)},
            "BankaG": {"p": (0.0, 0.3 * s, 0.0)}}


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
    """Spoczynek (2,4 s): kopiec kołysze się na nóżkach, bańka „oddycha” (płaty), łeb rozgląda się, ognik drga."""
    k = p.klip("idle", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        b = math.sin(4 * math.pi * t)
        return _z(_nadmij(0.12 + 0.12 * b),
                  Cialo=(1.5 * b, 0, 2.5 * a), Glowa=(-2 * b, 12 * math.sin(2 * math.pi * t + 0.8), -3 * a),
                  RamieL=(-8 + 4 * a, 0, 8), RamieP=(-12 - 3 * b, 0, -4), Kij={"k": (0.04, 1, 0.02 * b)})
    _petla(k, poza)
    return k


def ruch(p, dl=24):
    """Drepcze (0,8 s na dwa kroki): nóżki na zmianę, kopiec kiwa się na boki, bańka spóźnia się za ruchem, kij
    idzie jak laska wędrowca."""
    k = p.klip("ruch", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        c = math.cos(2 * math.pi * t)
        return _z(_nadmij(0.1 + 0.08 * math.sin(4 * math.pi * t - 1.0)),
                  Cialo=(5, 6 * a, 7 * c), NogaL=(-28 * a, 0, 0), NogaP=(28 * a, 0, 0),
                  Glowa=(-3, -4 * a, -6 * math.cos(2 * math.pi * t - 0.9)),
                  RamieL=(24 * a - 6, 0, 10), RamieP=(-22 - 18 * a, 0, -4), Kij={"k": (0.03, 1, 0.08 + 0.25 * a)},
                  _h=0.06 * abs(math.sin(2 * math.pi * t)))
    _petla(k, poza)
    return k


def atak(p, dl=27):
    """Uderzenie kijem (0,9 s): kij w górę za głowę, łuk z góry przed siebie (trafienie kl. 13), odbicie, powrót."""
    k = p.klip("atak", dl, petla=False)
    spocz = {}
    zamach = _z(_nadmij(0.2), Cialo={"o": (-8, -14, 0), "p": (0, 0, -0.15)}, Glowa=(-10, 0, 0),
                RamieP=(-165, 0, -20), Kij={"k": (0.3, 0.35, -1.0)}, RamieL=(-30, 0, 20))
    cios = _z(_nadmij(0.1), Cialo={"o": (14, 8, 0), "p": (0, 0, 0.35)}, Glowa=(10, 0, 0),
              RamieP=(-70, 0, -18), Kij={"k": (0.32, -0.12, 1.0)}, RamieL=(10, 0, 18))
    dobicie = _z(_nadmij(0.05), Cialo={"o": (16, 8, 0), "p": (0, 0, 0.38)}, Glowa=(12, 0, 0),
                 RamieP=(-52, 0, -18), Kij={"k": (0.3, -0.3, 1.0)}, RamieL=(14, 0, 18))
    powrot = _z(Cialo={"o": (4, 2, 0), "p": (0, 0, 0.1)}, RamieP=(-25, 0, -16), Kij={"k": (0.0, 1, 0.3)})
    _sekwencja(k, (0, 8, 13, 16, 21, 27), (spocz, zamach, cios, dobicie, powrot, spocz),
               wyg={0: "s", 1: "we", 2: "wy"})
    return k


def umiejetnosc(p, dl=56):
    """Bariera (1,9 s): kij w górę, bańka się nadyma, obrót wokół siebie z ognikiem nad głową (kl. 12–34),
    uderzenie kijem w ziemię (kl. 40 = krąg), bańka wraca, kij do boku."""
    k = p.klip("umiejetnosc", dl, petla=False)
    spocz = {}
    gora = _z(_nadmij(0.3), RamieP=(-170, 0, -12), Kij={"k": (-0.1, 1, 0.08)}, RamieL=(-40, 0, 40), Glowa=(-12, 0, 0),
              Cialo=(-6, 0, 0))

    def obrot(kat, s):
        a = math.radians(kat)
        return _z(gora, _nadmij(s), Cialo={"o": (-4, kat, 0), "p": (0, 0, 0)},
                  Kij={"k": (-0.25 * math.cos(a), 1, 0.25 * math.sin(a))}, _h=0.18 * s)
    zamach = _z(_nadmij(1.0), RamieP=(-175, 0, -6), Kij={"k": (0.0, 0.55, -0.85)}, RamieL=(-60, 0, 50),
                Glowa=(-16, 0, 0),
                Cialo=(-10, 0, 0), _h=0.2)
    uderz = _z(_nadmij(1.1), RamieP=(-52, 0, -8), Kij={"k": (0.0, -0.5, 0.86)}, RamieL=(-20, 0, 55), Glowa=(8, 0, 0),
               Cialo={"o": (12, 0, 0), "p": (0, 0, 0.1)})
    trzyma = _z(_nadmij(0.8), RamieP=(-48, 0, -8), Kij={"k": (0.0, -0.45, 0.89)}, RamieL=(-15, 0, 45), Glowa=(4, 0, 0),
                Cialo={"o": (8, 0, 0), "p": (0, 0, 0.08)})
    przed = _z(_nadmij(0.15), RamieP=(-85, 0, -10), Kij={"k": (-0.05, 1, 0.1)}, RamieL=(-20, 0, 30),
               Glowa=(-6, 0, 0))
    _sekwencja(k, (0, 5, 10, 16, 22, 28, 34, 40, 46, 56),
               (spocz, przed, gora, obrot(120, 0.6), obrot(240, 0.9), obrot(360, 1.0), zamach, uderz, trzyma, spocz),
               wyg={0: "we", 1: "wy", 3: "l", 4: "l", 6: "we", 7: "wy"})
    return k


def trafienie(p, dl=18):
    """Szarpnięcie w tył (0,6 s, najdalej kl. 4): bańka trzęsie się płatami, ręce w górę."""
    k = p.klip("trafienie", dl, petla=False)
    spocz = {}
    szarp = _z(_nadmij(0.6), Cialo={"o": (-14, 0, 4), "p": (0, 0, -0.35)}, Glowa=(-16, 0, 6),
               RamieL=(-50, 0, 40), RamieP=(-45, 0, -30), Kij={"k": (-0.05, 1, -0.3)})
    drga = _z(_nadmij(-0.1), Cialo={"o": (4, 0, -2), "p": (0, 0, -0.12)}, Glowa=(6, 0, -3))
    drga2 = _z(_nadmij(0.25), Cialo={"o": (-2, 0, 1), "p": (0, 0, -0.05)})
    _sekwencja(k, (0, 4, 9, 13, 18), (spocz, szarp, drga, drga2, spocz), wyg={0: "wy"})
    return k


def unik(p, dl=27):
    """Podskok w lewo o 1,4 studa (najdalej kl. 12) i drugi z powrotem (0,9 s)."""
    k = p.klip("unik", dl, petla=False)
    spocz = {}
    przys = _z(Cialo={"o": (6, 0, -6), "p": (0, 0, 0)}, NogaL=(0, 0, 10), NogaP=(0, 0, -10))
    lot = _z(_nadmij(0.3), Cialo={"o": (0, 0, 12), "p": (0.8, 0, 0)}, NogaL=(-20, 0, 25), NogaP=(15, 0, -5),
             RamieL=(-30, 0, 60), RamieP=(-40, 0, -35), Kij={"k": (0.0, 1, 0.1)}, Glowa=(0, 0, -10), _h=0.6,
             _wolne=True)
    lad = _z(_nadmij(0.15), Cialo={"o": (6, 0, 6), "p": (1.4, 0, 0)}, Glowa=(0, -14, 4))
    lot2 = _z(lot, Cialo={"o": (0, 0, -10), "p": (0.7, 0, 0)}, Glowa=(0, 0, 8), _h=0.45)
    lad2 = _z(Cialo={"o": (5, 0, -3), "p": (0, 0, 0)})
    _sekwencja(k, (0, 3, 8, 12, 16, 21, 27), (spocz, przys, lot, lad, lot2, lad2, spocz),
               wyg={1: "wy", 2: "we", 4: "we"})
    return k


def upadek(p, dl=60):
    """Upadek (2 s): chwieje się, kij wypada z ręki na bok, kopiec pada na plecy, bańka sflaczała (płaty
    schowane), całość zapada się w błoto (kl. 60 = leży)."""
    k = p.klip("upadek", dl, petla=False)
    spocz = {}
    chwiej = _z(_nadmij(0.5), Cialo={"o": (-8, 0, 10), "p": (0, 0, -0.2)}, Glowa=(-10, 0, 10),
                RamieL=(-40, 0, 50), RamieP=(-30, 0, -40), Kij={"k": (-0.1, 1, 0.2)})
    chwiej2 = _z(_nadmij(0.3), Cialo={"o": (8, 10, -12), "p": (0.1, 0, -0.1)}, Glowa=(12, 0, -14),
                 RamieL=(-10, 0, 30), RamieP=(-20, 0, -60), Kij={"k": (-0.2, 1, 0.3)})
    pada = _z(_nadmij(0.0), Cialo={"o": (-55, 5, 4), "p": (0, 0, -0.6)}, Glowa=(-14, 0, 0),
              RamieL=(-60, 0, 70), RamieP=(-60, 0, -80), Kij={"k": (0.15, 0.3, 1.0)}, NogaL=(-40, 0, 0),
              NogaP=(-30, 0, 0),
              _wolne=True)
    lezy = _z(_nadmij(-0.25), Cialo={"o": (-88, 4, 6), "p": (0, 0, -1.2)}, Glowa=(-18, 0, 6),
              RamieL=(-40, 0, 85), RamieP=(-45, 0, -90), Kij={"k": (0.05, 0.03, 1.0)}, NogaL=(-55, 0, 8),
              NogaP=(-45, 0, -8),
              _wolne=True)
    bloto = _z(lezy, _h=-0.55)
    _sekwencja(k, (0, 9, 18, 30, 38, 60), (spocz, chwiej, chwiej2, pada, lezy, bloto),
               wyg={2: "we", 3: "wy", 4: "l"})
    return k


def wiwat(p, dl=60):
    """Radość (pętla 2 s): dwa podskoki z kijem wysoko nad bańką, bańka pulsuje, ognik macha w kółko."""
    k = p.klip("wiwat", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        hop = abs(math.sin(2 * math.pi * t))
        return _z(_nadmij(0.35 + 0.35 * math.sin(4 * math.pi * t + 1.2)),
                  Cialo=(-4 + 4 * math.cos(4 * math.pi * t), 10 * a, 6 * math.sin(4 * math.pi * t)),
                  Glowa=(-10, -8 * a, 0), RamieP=(-165 + 12 * math.sin(4 * math.pi * t), 15 * a, -10),
                  Kij={"k": (0.25 * math.cos(2 * math.pi * t), 1, 0.25 * a)}, RamieL=(-120 + 20 * a, 0, 30),
                  NogaL=(-15 * hop, 0, 6), NogaP=(-15 * hop, 0, -6), _h=0.55 * hop)
    _petla(k, poza)
    return k


# =============================================================== animacja: pozy kluczowe -> klucz w każdej klatce
# (ten sam zestaw pomocników w modułach potworów Bagna: rechotek, bulgotnik, klodoklap, ropucha_z_chatka,
#  straznik_topieli). Poza = {kość: (rx, ry, rz) | {"o": obrót, "p": przesunięcie, "k": kierunek osi OS[kość] w
#  świecie}}; "_h" = wysokość najniższego punktu ciała nad ziemią (domyślnie 0), "_wolne" = kości PLASKIE nie są
#  trzymane poziomo (lot, przewrót). Brak kości w pozie = spoczynek tej kości (względem rodzica).
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


def _plasko(p, lok):
    """Kości PLASKIE: poziomo w świecie, z odchyleniem (yaw) rodzica."""
    W = {}
    for n, k in p.kosci.items():
        o, pr = lok.get(n, (ZERO, ZERO))
        if n in PLASKIE:
            Rp = W[k["rodzic"]][0]
            f = razy_wektor(Rp, (0.0, 0.0, 1.0))
            yaw = math.degrees(math.atan2(f[0], f[2])) if abs(f[0]) + abs(f[2]) > 1e-6 else 0.0
            o = katy_z_macierzy(mnoz(_T(Rp), macierz_obrotu(0.0, yaw, 0.0)))
            lok[n] = (o, pr)
        _krok(p, W, n, o, pr)
    return W


def _uziem(p, lok, h, plasko=True):
    W = _plasko(p, lok) if plasko else _fk(p, lok)
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
        plasko = not (pozy[i].get("_wolne") or pozy[i + 1].get("_wolne"))
        if ziemia:
            _uziem(p, lok, h0 + (h1 - h0) * e, plasko)
        elif plasko:
            _plasko(p, lok)
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
            _uziem(p, lok, pz.get("_h", 0.0), not pz.get("_wolne"))
        _ciagle_katy(lok, poprz)
        _zapisz(k, f, lok)
        if pierwsza is None:
            pierwsza = dict(lok)
    _zapisz(k, k.dlugosc, pierwsza)
    return k
