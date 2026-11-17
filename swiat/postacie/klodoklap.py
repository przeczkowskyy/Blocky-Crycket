# -*- coding: utf-8 -*-
"""KŁODOKŁAP — zwykły przeciwnik Bagna (Kłapiące Kępy): żywa omszała kłoda na czterech łapach-korzeniach,
ok. 3,2 studa wysokości z grzybkiem, 8,6 studa długości (gracz ma 5,7).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/klodoklap.py --wyj <folder> --klip umiejetnosc

Opis z planu Bagna (swiat/bagno_pas/README.md, rozdz. „Potwory”): żywa omszała kłoda na łapach-korzeniach, przód
rozcięty w paszczę z kołkami-zębami, grzybek na grzbiecie. Klasa w przegrodzie: Wojownik. Gruby Pancerz, mocno gryzie,
czasem ogłusza, nie unika; umiejętność silnika `miazdzacy_cios` = szarpnięcie do przodu i zatrzaśnięcie paszczy.

Sylwetka (z daleka): długi, niski, ośmiokątny (schodkowy) pień nisko nad ziemią na czterech krzywych korzeniach;
przód rozcięty poziomo na dwie szczęki z jasnego drewna, z kołkami i czterema kłami na zewnątrz (widać je i przy
zamkniętej paszczy), wzdłuż szwu paszczy jasna „warga”; na łbie dwa sęki-oczy z bursztynowym blaskiem (Neon);
na grzbiecie pas mchu, zwisające kosmyki i pomarańczowy grzyb; tył ścięty — jasny przekrój ze słojami.

Paleta: kora 6B4F33 (dwa odcienie), jasne drewno paszczy i przekrojów E3C99A, mech A9B48E, grzyb C8642E,
oczy E0A030 (Neon), próchno w paszczy.

Szkielet (typ „stwor”; L = lewa = +X, P = prawa = −X):
    Root > Cialo > {Glowa (górna szczęka), Szczeka (dolna szczęka), Grzyb, Ogon (ścięty koniec),
                    LapaPrzodL > StopaPrzodL, LapaPrzodP > StopaPrzodP, LapaTylL > StopaTylL, LapaTylP > StopaTylP}
- `Cialo` niesie całą kłodę (wypad, przewrót); Stopa* (dolny korzeń z palcami) trzymane pionowo i płasko;
- obie szczęki mają zawias w tym samym miejscu (z = 1,4): paszcza otwiera się na oba boki jak u krokodyla.

Klipy (30 kl./s; patrzy w +Z):
  idle (pętla 2,4 s: oddech paszczą, grzyb i ogon się kiwają), ruch (pętla 1,07 s: chód krzyżowy na korzeniach),
  atak (kłapnięcie z wypadu, trafienie kl. 14, 0,9 s), umiejetnosc (miażdżący cios: przód w górę, paszcza szeroko,
  szarpnięcie 1,3 studa do przodu i zatrzaśnięcie kl. 26, szarpanie na boki, powrót; 1,9 s), trafienie (0,6 s),
  unik (ciężki krok w lewo 1,0 studa i powrót, 0,9 s), upadek (korzenie się uginają, kłoda przewraca się na grzbiet
  korzeniami do góry, paszcza otwarta, zapada się w błoto; 2 s, leży w ostatniej klatce),
  wiwat (pętla 2 s: kłapanie i tupanie przednimi korzeniami, ogon macha).
Klipy są zapisane jako pozy kluczowe zamienione na klucz w KAŻDEJ klatce (wygładzanie „liniowo”).
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Postac, katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor

ID = "klodoklap"

PALETA = {
    "kora": "6B4F33", "kora_ciemna": "4F3A26", "kora_jasna": "86663F",
    "drewno": "E3C99A", "drewno_cien": "C2A472", "sloj": "A88654", "prochno": "4A3424",
    "mech": "A9B48E", "mech_ciemny": "7F8C62",
    "grzyb": "C8642E", "grzyb_kropka": "F0E2C0", "trzon": "E8DCC0",
    "oko": "E0A030", "tusz": "21160E", "zab": "F6EDD6",
}

CHWILE = {"atak": 14, "umiejetnosc": 26, "trafienie": 4, "unik": 12}

SLABOSCI = [
    "Kości Kłodokłapa nie są R15 (własny szkielet: Root + 13 kości) — import do Roblox Studio nie był testowany.",
    "Pień jest schodkowym ośmiokątem z klocków (bez walców) — z bliska widać stopnie.",
    "Kołki-zęby wewnątrz paszczy przy zamkniętej paszczy chowają się w drugiej szczęce; na zewnątrz zostają "
    "cztery kły.",
    "Chód jest w miejscu — dolne korzenie stoją pionowo i ślizgają się po ziemi w podporze.",
    "Miażdżący cios przesuwa kłodę o 1,3 studa do przodu i z powrotem (ruch w klipie).",
    "W upadku grzyb na grzbiecie wchodzi w ziemię (kłoda leży na grzbiecie) — z założenia „wbity w błoto”.",
    "Świecenie oczu: materiał Neon na rigu z klocków.",
]

# ----------------------------------------------------------------------------------------------- szkielet (studs)
Y_OS = 1.75                         # oś pnia
CIALO = (0.0, Y_OS, -0.6)
ZAWIAS = (0.0, Y_OS, 1.4)
GRZYB = (0.35, 2.72, -1.6)
OGON = (0.0, Y_OS, -3.55)
Z_PRZOD, Z_TYL = 0.9, -2.6          # z barków i bioder
BARK = (0.8, 1.15)                  # (x, y) stawu łapy
KOLANO = (1.42, 0.72, 0.18)         # względem barku: (x, y, dz)
STOPA_X = 1.58

GLOWNA = "Cialo"
PLASKIE = ("StopaPrzodL", "StopaPrzodP", "StopaTylL", "StopaTylP")
POMIN_ZIEMIA = ("Grzyb",)
OS = {}


def _lu(v, zn):
    return (zn * v[0], v[1], v[2])


def _model(p, kosc, obrot=(0, 0, 0), pos=(0, 0, 0)):
    """Układ MODELU (0, 0, 0 = ziemia pod środkiem) na kości: bryły podaje się we współrzędnych modelu."""
    s = p.staw(kosc)
    return p.na(kosc, pos=(pos[0] - s[0], pos[1] - s[1], pos[2] - s[2]), obrot=obrot)


LAPY = (("PrzodL", 1.0, Z_PRZOD), ("PrzodP", -1.0, Z_PRZOD), ("TylL", 1.0, Z_TYL), ("TylP", -1.0, Z_TYL))


def zbuduj():
    p = Postac(ID, "Kłodokłap", typ="stwor", skala=1.0, faza=0.05, paleta=PALETA)

    p.kosc("Cialo", "Root", staw=CIALO, dl=0.8)
    p.kosc("Glowa", "Cialo", staw=ZAWIAS, dl=0.6)
    p.kosc("Szczeka", "Cialo", staw=(0.0, Y_OS - 0.05, ZAWIAS[2]), dl=0.6)
    p.kosc("Grzyb", "Cialo", staw=GRZYB, dl=0.3)
    p.kosc("Ogon", "Cialo", staw=OGON, dl=0.5)
    for s, zn, z in LAPY:
        p.kosc("Lapa" + s, "Cialo", staw=(zn * BARK[0], BARK[1], z), dl=0.5)
        p.kosc("Stopa" + s, "Lapa" + s, staw=(zn * KOLANO[0], KOLANO[1], z + KOLANO[2]), dl=0.4)

    _pien(p)
    _paszcza(p)
    _grzyb(p)
    _lapy(p)

    p.zaczep("RootAttachment", "Cialo", (-CIALO[0], -CIALO[1], -CIALO[2]))
    # cel trafienia: łeb za zawiasem (środek przedniej części pnia)
    p.zaczep("GlowaAttachment", "Glowa", (0.0, 0.25, 0.9))
    # czubek paszczy między kłami (Bron i Pocisk)
    p.zaczep("PyskAttachment", "Glowa", (0.0, 0.0, 2.85))

    _klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return p


# ---------------------------------------------------------------------------------------------------- bryły
def _przekroj(p, nazwa, z0, z1, y0=None, y1=None, kolor="kora", szer=1.9, wys=1.9):
    """Schodkowy ośmiokąt pnia od z0 do z1 (rdzeń + górna i dolna płyta); y0/y1 przycinają do połowy (szczęki)."""
    zc, dz = (z0 + z1) / 2.0, z1 - z0
    h3 = wys * 0.315
    gora, dol = Y_OS + wys / 2.0, Y_OS - wys / 2.0
    czesci = [("rdzen", szer, dol + h3 * 0.5 + 0.0, gora - h3 * 0.5), ("gora", szer * 0.68, gora - h3 * 0.5, gora),
              ("dol", szer * 0.68, dol, dol + h3 * 0.5)]
    for n, w, a, b in czesci:
        a2, b2 = a, b
        if y0 is not None:
            a2 = max(a2, y0)
        if y1 is not None:
            b2 = min(b2, y1)
        if b2 - a2 > 0.02:
            p.blok("%s %s" % (nazwa, n), (0, (a2 + b2) / 2.0, zc), (w, b2 - a2, dz), kolor, "matowy", faza=0.06)


def _przekroj_slojow(p, nazwa, z, zn, y0, y1):
    """Jasny przekrój ze słojami na ściętym końcu (zn = +1 przód, −1 tył), od y0 do y1."""
    for i, (w, kol) in enumerate(((1.7, "drewno_cien"), (1.15, "sloj"), (0.95, "drewno_cien"), (0.4, "sloj"))):
        a, b = max(y0, Y_OS - w / 2), min(y1, Y_OS + w / 2)
        if b - a > 0.02:
            p.blok("%s %d" % (nazwa, i), (0, (a + b) / 2.0, z + zn * (0.02 + 0.012 * i)), (w, b - a, 0.04), kol,
                   "matowy", faza=0.0)


def _pien(p):
    with _model(p, "Cialo"):
        _przekroj(p, "Pien", -3.6, 1.45)
        # prążki kory wzdłuż pnia
        for i, (x, y, z, dl) in enumerate(((0.96, 1.5, -1.2, 3.6), (0.96, 2.05, 0.1, 2.4), (-0.96, 1.6, -0.8, 3.8),
                                           (-0.96, 2.1, -2.0, 2.2), (0.5, 2.67, -2.4, 2.0), (-0.45, 2.67, 0.3, 1.8),
                                           (0.4, 0.83, -1.0, 3.0))):
            sx = 0.08 if abs(x) > 0.9 else 0.14
            sy = 0.14 if abs(x) > 0.9 else 0.08
            p.blok("Kora %d" % i, (x + (0.02 if x > 0 else -0.02) * (abs(x) > 0.9), y, z), (sx, sy, dl),
                   "kora_ciemna", "matowy", faza=0.0)
        # pas mchu na grzbiecie i kosmyki zwisające po bokach
        p.blok("Mech grzbiet", (0.0, 2.72, -1.2), (1.05, 0.1, 3.4), "mech", "matowy", faza=0.03)
        p.blok("Mech grzbiet 2", (-0.25, 2.72, 0.75), (0.7, 0.08, 1.2), "mech_ciemny", "matowy", faza=0.02)
        for i, (zn, z, h) in enumerate(((1, -0.3, 0.55), (1, -2.2, 0.75), (-1, -1.3, 0.65), (-1, 0.6, 0.45),
                                        (1, -3.2, 0.4))):
            p.blok("Kosmyk %d" % i, (zn * 0.72, 2.45 - h / 2 + 0.2, z), (0.18, h, 0.22), "mech", "matowy",
                   rot=(0, 0, zn * 18), faza=0.02)
        # sęki-kikuty gałęzi
        for i, (zn, z, ry) in enumerate(((1, -1.7, 20), (-1, -0.2, -25))):
            with p.uklad(pos=(zn * 0.95, 2.2, z), obrot=(0, 0, -zn * 55)):
                p.blok("Kikut %d" % i, (0, 0.25, 0), (0.34, 0.5, 0.34), "kora", "matowy", faza=0.04)
                p.blok("Kikut przekroj %d" % i, (0, 0.51, 0), (0.26, 0.03, 0.26), "drewno", "matowy", faza=0.0)
    with _model(p, "Ogon"):
        _przekroj(p, "Ogon", -4.25, -3.5, kolor="kora")
        _przekroj_slojow(p, "Sloje tyl", -4.25, -1, 0.85, 2.65)
        for i, (x, rz, rx) in enumerate(((0.45, 20, -30), (-0.35, -15, -40))):
            with p.uklad(pos=(x, 0.95, -4.0), obrot=(rx, 0, rz)):
                p.blok("Korzonek ogona %d" % i, (0, -0.3, 0), (0.14, 0.6, 0.14), "kora_ciemna", "matowy", faza=0.0)


def _paszcza(p):
    z0, z1 = 1.3, 4.1
    with _model(p, "Glowa"):
        _przekroj(p, "Szczeka gorna", z0, z1, y0=Y_OS)
        # lekko ścięty nos (klin na wierzchu przodu)
        p.klin("Nos", (0, 2.62, 3.85), (1.25, 0.18, 0.5), "kora", "matowy", rot=(0, 180, 0))
        _przekroj_slojow(p, "Sloje gora", z1, 1, Y_OS, 2.65)
        p.blok("Podniebienie", (0, Y_OS + 0.02, 2.75), (1.6, 0.04, 2.6), "drewno", "matowy", faza=0.0)
        p.blok("Prochno gora", (0, Y_OS + 0.045, 2.6), (0.7, 0.03, 1.8), "prochno", "matowy", faza=0.0)
        for zn in (1, -1):
            p.blok("Warga gora", (zn * 0.965, Y_OS + 0.06, 2.7), (0.04, 0.12, 2.8), "drewno", "matowy", faza=0.0)
            for i, z in enumerate((1.8, 2.35, 2.9, 3.45)):
                p.blok("Kolek gora %d" % i, (zn * 0.72, Y_OS - 0.12, z), (0.16, 0.3, 0.16), "zab", rot=(0, 45, 0),
                       faza=0.02)
            # kieł na zewnątrz (widać go przy zamkniętej paszczy)
            p.blok("Kiel gora", (zn * 0.42, Y_OS - 0.14, 4.2), (0.22, 0.46, 0.2), "zab", rot=(0, 45, 0), faza=0.03)
            # sęk-oko z bursztynowym blaskiem
            p.blok("Oko sek", (zn * 0.58, 2.78, 1.95), (0.48, 0.34, 0.48), "kora_jasna", "matowy", faza=0.06)
            p.blok("Oko dziupla", (zn * 0.58, 2.8, 2.205), (0.32, 0.22, 0.04), "tusz", "matowy", faza=0.0)
            p.blok("Oko", (zn * 0.55, 2.8, 2.23), (0.15, 0.13, 0.03), "oko", "swiecacy", faza=0.0)
            p.blok("Brew", (zn * 0.58, 3.0, 2.05), (0.5, 0.1, 0.3), "mech_ciemny", "matowy", rot=(0, 0, -zn * 12),
                   faza=0.0)
        p.blok("Mech leb", (0.0, 2.72, 3.0), (0.8, 0.08, 1.4), "mech", "matowy", faza=0.02)
        # ciemny szew paszczy na przodzie i po bokach (widać rozcięcie przy zamkniętej paszczy)
        p.blok("Szew przod", (0, Y_OS - 0.02, z1 + 0.075), (1.75, 0.08, 0.03), "tusz", "matowy", faza=0.0)
    with _model(p, "Szczeka"):
        _przekroj(p, "Szczeka dolna", z0, z1 - 0.05, y1=Y_OS - 0.05)
        _przekroj_slojow(p, "Sloje dol", z1 - 0.05, 1, 0.85, Y_OS - 0.05)
        p.blok("Jezor", (0, Y_OS - 0.07, 2.7), (1.6, 0.04, 2.5), "drewno", "matowy", faza=0.0)
        p.blok("Prochno dol", (0, Y_OS - 0.045, 2.5), (0.8, 0.03, 1.7), "prochno", "matowy", faza=0.0)
        for zn in (1, -1):
            p.blok("Warga dol", (zn * 0.965, Y_OS - 0.12, 2.7), (0.04, 0.1, 2.75), "drewno", "matowy", faza=0.0)
            for i, z in enumerate((2.05, 2.6, 3.15, 3.7)):
                p.blok("Kolek dol %d" % i, (zn * 0.72, Y_OS + 0.05, z), (0.15, 0.26, 0.15), "zab", rot=(0, 45, 0),
                       faza=0.02)
            p.blok("Kiel dol", (zn * 0.7, Y_OS + 0.04, 4.16), (0.2, 0.4, 0.18), "zab", rot=(0, 45, 0),
                   faza=0.03)


def _grzyb(p):
    with _model(p, "Grzyb"):
        p.walec("Trzon", (0.35, 2.92, -1.6), (0.24, 0.42, 0.24), "trzon", "matowy", segm=8)
        p.kula("Kapelusz", (0.35, 3.08, -1.6), (0.82, 0.32, 0.82), "grzyb", "zwykly", segm=12)
        for i, (dx, dz) in enumerate(((0.15, 0.12), (-0.18, -0.05), (0.02, -0.22))):
            p.blok("Kropka %d" % i, (0.35 + dx, 3.225, -1.6 + dz), (0.1, 0.03, 0.1), "grzyb_kropka", "matowy",
                   faza=0.0)
        p.walec("Trzon maly", (0.0, 2.85, -2.05), (0.14, 0.26, 0.14), "trzon", "matowy", segm=8)
        p.kula("Kapelusz maly", (0.0, 2.97, -2.05), (0.42, 0.18, 0.42), "grzyb", "zwykly", segm=8)


def _lapy(p):
    for s, zn, z in LAPY:
        bark = (zn * BARK[0], BARK[1] + 0.1, z)
        kol = (zn * KOLANO[0], KOLANO[1], z + KOLANO[2])
        with _model(p, "Lapa" + s):
            _belka(p, "Korzen gorny", bark, kol, 0.56, 0.52, "kora", "matowy", nad=0.1)
            p.blok("Kolano", kol, (0.6, 0.5, 0.58), "kora_ciemna", "matowy", rot=(0, 30, 0), faza=0.06)
        with _model(p, "Stopa" + s):
            dol = (zn * STOPA_X, 0.14, z + 0.3)
            _belka(p, "Korzen dolny", kol, dol, 0.46, 0.42, "kora", "matowy", nad=0.05)
            for i, (ry, dl) in enumerate(((-35, 0.6), (5, 0.7), (45, 0.55))):
                kat = math.radians(ry * zn)
                kon = (dol[0] + zn * 0.12 + math.sin(kat) * dl, 0.05, dol[2] + math.cos(kat) * dl)
                _belka(p, "Palec %d" % i, (dol[0], 0.12, dol[2]), kon, 0.16, 0.12, "kora_ciemna", "matowy")


# ---------------------------------------------------------------------------------------------------- klipy
def _z(*czesci, **kosci):
    out = {}
    for c in czesci:
        out.update(c)
    out.update(kosci)
    return out


def _paszcza_poz(gora, dol):
    """Otwarcie paszczy: górna szczęka w górę o `gora` stopni, dolna w dół o `dol`."""
    return {"Glowa": (-gora, 0, 0), "Szczeka": (dol, 0, 0)}


def _lapy_poz(przodL=(0, 0, 0), przodP=(0, 0, 0), tylL=(0, 0, 0), tylP=(0, 0, 0)):
    return {"LapaPrzodL": przodL, "LapaPrzodP": przodP, "LapaTylL": tylL, "LapaTylP": tylP}


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
    """Spoczynek (2,4 s): paszcza uchyla się w rytm oddechu, pień lekko się wznosi, grzyb i ogon kiwają się."""
    k = p.klip("idle", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        odd = 0.5 - 0.5 * math.cos(2 * math.pi * t)
        return _z(_paszcza_poz(5 + 5 * odd, 3 + 3 * odd),
                  Cialo=(-1.2 * odd, 2 * math.sin(2 * math.pi * t + 0.5), 0),
                  Grzyb=(4 * math.sin(4 * math.pi * t), 0, 5 * a), Ogon=(0, 6 * a, 0))
    _petla(k, poza)
    return k


def ruch(p, dl=32):
    """Chód krzyżowy na korzeniach (1,07 s na pełny cykl): przednia lewa z tylną prawą, kłoda kiwa się na boki,
    łeb prowadzi, ogon zamiata."""
    k = p.klip("ruch", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        c = math.cos(2 * math.pi * t)
        lift_a = max(0.0, c) * 22
        lift_b = max(0.0, -c) * 22
        return _z(_paszcza_poz(3 + 2 * math.sin(4 * math.pi * t), 2),
                  _lapy_poz(przodL=(-24 * a, 0, lift_a), tylP=(-24 * a, 0, -lift_a),
                            przodP=(24 * a, 0, -lift_b), tylL=(24 * a, 0, lift_b)),
                  Cialo=(0, 4 * a, 3 * c), Glowa=(-3, 3 * math.sin(2 * math.pi * t - 0.6), 0),
                  Ogon=(0, -9 * a, 0), Grzyb=(0, 0, -6 * c))
    _petla(k, poza)
    return k


def atak(p, dl=27):
    """Kłapnięcie (0,9 s): paszcza szeroko, wypad 0,6 studa i zatrzaśnięcie (kl. 14), powrót."""
    k = p.klip("atak", dl, petla=False)
    spocz = {}
    otwarta = _z(_paszcza_poz(28, 18), _lapy_poz(przodL=(12, 0, 0), przodP=(12, 0, 0)),
                 Cialo={"o": (-6, 0, 0), "p": (0, 0, -0.2)}, Ogon=(0, 0, 0))
    wypad = _z(_paszcza_poz(32, 20), _lapy_poz(przodL=(-25, 0, 0), przodP=(-25, 0, 0), tylL=(-10, 0, 0),
                                               tylP=(-10, 0, 0)),
               Cialo={"o": (3, 0, 0), "p": (0, 0, 0.45)})
    zatrzask = _z(_paszcza_poz(-3, -2), _lapy_poz(przodL=(-28, 0, 0), przodP=(-28, 0, 0), tylL=(-12, 0, 0),
                                                  tylP=(-12, 0, 0)),
                  Cialo={"o": (5, 0, 0), "p": (0, 0, 0.6)}, Grzyb=(-12, 0, 0))
    po = _z(_paszcza_poz(2, 1), Cialo={"o": (1, 0, 0), "p": (0, 0, 0.3)}, Grzyb=(8, 0, 0))
    _sekwencja(k, (0, 8, 12, 14, 20, 27), (spocz, otwarta, wypad, zatrzask, po, spocz),
               wyg={1: "we", 2: "we", 3: "wy"})
    return k


def umiejetnosc(p, dl=57):
    """Miażdżący cios (1,9 s): przód kłody w górę, paszcza bardzo szeroko (kl. 0–16), szarpnięcie 1,3 studa do
    przodu i zatrzaśnięcie z uderzeniem łbem w dół (kl. 26), szarpanie na boki, cofnięcie."""
    k = p.klip("umiejetnosc", dl, petla=False)
    spocz = {}
    wznies = _z(_paszcza_poz(40, 26), _lapy_poz(przodL=(-30, 0, 8), przodP=(-30, 0, -8), tylL=(20, 0, 0),
                                                tylP=(20, 0, 0)),
                Cialo={"o": (-16, 0, 0), "p": (0, 0, -0.35)}, Ogon=(10, 0, 0), Grzyb=(10, 0, 0))
    wznies2 = _z(wznies, _paszcza_poz(46, 30), Cialo={"o": (-18, 0, 0), "p": (0, 0, -0.4)})
    skok = _z(_paszcza_poz(44, 28), _lapy_poz(przodL=(-40, 0, 6), przodP=(-40, 0, -6), tylL=(-25, 0, 0),
                                              tylP=(-25, 0, 0)),
              Cialo={"o": (-4, 0, 0), "p": (0, 0, 0.9)}, Ogon=(-6, 0, 0), _h=0.2)
    trzask = _z(_paszcza_poz(-6, -3), _lapy_poz(przodL=(-20, 0, 10), przodP=(-20, 0, -10), tylL=(-30, 0, 0),
                                                tylP=(-30, 0, 0)),
                Cialo={"o": (10, 0, 0), "p": (0, 0, 1.3)}, Grzyb=(-20, 0, 0), Ogon=(-12, 0, 0))
    szarp1 = _z(trzask, Cialo={"o": (8, 14, 10), "p": (0, 0, 1.25)}, Grzyb=(0, 0, -18), Ogon=(0, -14, 0))
    szarp2 = _z(trzask, Cialo={"o": (8, -14, -10), "p": (0, 0, 1.25)}, Grzyb=(0, 0, 18), Ogon=(0, 14, 0))
    puszcza = _z(_paszcza_poz(14, 8), Cialo={"o": (0, 0, 0), "p": (0, 0, 0.6)})
    _sekwencja(k, (0, 10, 16, 22, 26, 31, 36, 41, 48, 57),
               (spocz, wznies, wznies2, skok, trzask, szarp1, szarp2, trzask, puszcza, spocz),
               wyg={2: "we", 3: "we", 4: "wy"})
    return k


def trafienie(p, dl=18):
    """Szarpnięcie w tył (0,6 s, najdalej kl. 4): przód w górę, paszcza uchylona, grzyb się chwieje."""
    k = p.klip("trafienie", dl, petla=False)
    spocz = {}
    szarp = _z(_paszcza_poz(14, 10), _lapy_poz(przodL=(18, 0, 0), przodP=(18, 0, 0)),
               Cialo={"o": (-8, 0, 3), "p": (0, 0, -0.4)}, Grzyb=(-16, 0, 6), Ogon=(-6, 0, 0))
    odb = _z(_paszcza_poz(2, 1), Cialo={"o": (2, 0, -1), "p": (0, 0, -0.15)}, Grzyb=(10, 0, -4))
    _sekwencja(k, (0, 4, 10, 18), (spocz, szarp, odb, spocz), wyg={0: "wy"})
    return k


def unik(p, dl=27):
    """Ciężki krok w lewo o 1,0 studa (najdalej kl. 12) i powrót (0,9 s)."""
    k = p.klip("unik", dl, petla=False)
    spocz = {}
    przys = _z(_lapy_poz(przodL=(0, 0, 10), przodP=(0, 0, -14), tylL=(0, 0, 10), tylP=(0, 0, -14)),
               Cialo={"o": (0, 0, -6), "p": (0, 0, 0)})
    lot = _z(_lapy_poz(przodL=(0, 0, 25), przodP=(0, 0, 12), tylL=(0, 0, 25), tylP=(0, 0, 12)),
             Cialo={"o": (0, -8, 8), "p": (0.55, 0, 0)}, Ogon=(0, 12, 0), _h=0.25)
    lad = _z(_paszcza_poz(6, 4), Cialo={"o": (0, -6, 3), "p": (1.0, 0, 0)}, Ogon=(0, -8, 0), Grzyb=(0, 0, 14))
    lot2 = _z(_lapy_poz(przodL=(0, 0, -10), przodP=(0, 0, -25), tylL=(0, 0, -10), tylP=(0, 0, -25)),
              Cialo={"o": (0, 4, -6), "p": (0.5, 0, 0)}, _h=0.18)
    _sekwencja(k, (0, 4, 8, 12, 17, 22, 27), (spocz, przys, lot, lad, lot2, spocz, spocz),
               wyg={1: "wy", 2: "we"})
    return k


def upadek(p, dl=60):
    """Upadek (2 s): korzenie się uginają, kłoda przechyla się na prawy bok, przewraca na grzbiet korzeniami do góry,
    paszcza opada otwarta, kłoda zapada się w błoto (kl. 60 = leży)."""
    k = p.klip("upadek", dl, petla=False)
    spocz = {}
    chwiej = _z(_paszcza_poz(10, 8), _lapy_poz(przodL=(10, 0, 20), przodP=(10, 0, -5), tylL=(0, 0, 20)),
                Cialo={"o": (-4, 6, -10), "p": (0, 0, -0.2)}, Grzyb=(0, 0, 14))
    ugina = _z(_paszcza_poz(16, 12), _lapy_poz(przodL=(0, 0, 50), przodP=(0, 0, -45), tylL=(0, 0, 50),
                                               tylP=(0, 0, -45)),
               Cialo={"o": (2, -4, -28), "p": (0, 0, -0.2)}, Grzyb=(0, 0, 20), _wolne=True)
    bok = _z(_paszcza_poz(18, 14), _lapy_poz(przodL=(-20, 0, 30), przodP=(20, 0, -10), tylL=(15, 0, 30),
                                             tylP=(-15, 0, -10)),
             Cialo={"o": (0, -6, -95), "p": (0, 0, -0.2)}, Grzyb=(0, 0, 25), _wolne=True)
    grzbiet = _z(_paszcza_poz(20, 22), _lapy_poz(przodL=(-25, 0, -15), przodP=(25, 0, 15), tylL=(20, 0, -15),
                                                 tylP=(-20, 0, 15)),
                 Cialo={"o": (0, -8, -165), "p": (0, 0, -0.2)}, Ogon=(0, 10, 0), _wolne=True)
    drga = _z(grzbiet, _lapy_poz(przodL=(-10, 0, -25), przodP=(15, 0, 25), tylL=(30, 0, -10), tylP=(-30, 0, 5)))
    bloto = _z(grzbiet, _paszcza_poz(24, 26), _h=-0.4)
    _sekwencja(k, (0, 10, 20, 30, 38, 46, 60), (spocz, chwiej, ugina, bok, grzbiet, drga, bloto),
               wyg={2: "we", 3: "wy", 6: "l"})
    return k


def wiwat(p, dl=60):
    """Radość (pętla 2 s): kłapie paszczą trzy razy, tupie przednimi korzeniami, ogon macha, grzyb podskakuje."""
    k = p.klip("wiwat", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        klap = max(0.0, math.sin(6 * math.pi * t))
        tup = math.sin(4 * math.pi * t)
        return _z(_paszcza_poz(30 * klap, 18 * klap),
                  _lapy_poz(przodL=(-30 * max(0.0, tup), 0, 10 * max(0.0, tup)),
                            przodP=(-30 * max(0.0, -tup), 0, -10 * max(0.0, -tup))),
                  Cialo=(-6 * klap, 5 * a, 3 * tup), Ogon=(0, 18 * a, 0), Grzyb=(-8 * klap, 0, 10 * a))
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
