# -*- coding: utf-8 -*-
"""RECHOTEK — zwykły przeciwnik Bagna (Rechotne Oczka): przysadzista ropucha z klocków, ok. 2,9 studa z oczami,
3,7 studa długości (gracz ma 5,7).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/rechotek.py --wyj <folder> --klip atak

Opis z planu Bagna (swiat/bagno_pas/README.md, rozdz. „Potwory”): przysadzista ropucha z klocków, płaski szeroki
łeb, oczy-kulki na czubku, szerokie usta, tylne łapy do susów. Klasa w przegrodzie: Zwiadowca. Często unika,
„lepki język” spowalnia; umiejętność silnika `uderzenie_z_gory` = sus w górę i plaśnięcie całym ciałem na celu.

Sylwetka (z daleka): niski, szeroki klin — grzbiet opada ku tyłowi, z przodu płaski łeb szerszy od tułowia, na
czubku dwie wielkie pomarańczowe kule oczu; po bokach grube „szynki” złożonych tylnych łap; żółty brzuch i żółta
broda z przodu, żółty pasek wzdłuż grzbietu (czytelny z kamery z góry na oliwkowej kępie), ciemne plamy.
Twarz: szeroka czarna linia ust od boku do boku z kącikami w górę, poziome źrenice, nozdrza.

Paleta: oliwka 7E8C3E w ciemne plamy 4F5E2A, brzuch E8D27A, oczy F2932E, wnętrze pyska i język (róż), jasne palce.

Szkielet (typ „stwor”; L = lewa = +X, P = prawa = −X):
    Root > Cialo > {Glowa > Szczeka > {Wole, Jezyk},
                    LapaPL > DlonPL, LapaPP > DlonPP,
                    UdoL > GolenL > StopaL, UdoP > GolenP > StopaP}
- `Cialo` niesie całą ropuchę (sus, unik, upadek); Dlon*/Stopa* trzymane płasko na ziemi (liczone w module);
- `Jezyk` w spoczynku leży schowany w żuchwie i tułowiu; w ataku wystrzela 2,3 studa przed pysk;
- `Wole` (żółty worek pod brodą) nadyma się przy oddechu i rechotaniu (przesunięciem, bez kanału skali).

Klipy (30 kl./s; ropucha patrzy w +Z):
  idle (pętla 2,4 s: oddech, worek pod brodą pulsuje, rozgląda się), ruch (pętla 0,8 s: jeden sus w miejscu),
  atak (lepki język, 0,9 s, trafienie kl. 12), umiejetnosc (uderzenie z góry: przyczajenie, wybicie, zwinięcie
  w locie, plaśnięcie brzuchem kl. 30; łuk skoku nad celem robi odtwarzacz, 1,8 s), trafienie (szarpnięcie w tył,
  0,6 s), unik (sus w lewo 1,6 studa i powrót, 0,9 s), upadek (zatacza się, plaśnięcie z rozjechanymi łapami,
  przechył na bok, język na wierzchu, zapada się w błoto; 2 s, leży w ostatniej klatce),
  wiwat (pętla 2 s: dwa podskoki i rechot z nadętym workiem).
Klipy są zapisane jako pozy kluczowe zamienione na klucz w KAŻDEJ klatce (wygładzanie „liniowo”), więc próbki
liniowe, Blender i Roblox dają to samo. Najniższy punkt ciała stoi na ziemi (y = 0) poza chwilami lotu.
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Postac, katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor

ID = "rechotek"

PALETA = {
    "oliwka": "7E8C3E", "plama": "4F5E2A", "brodawka": "687534",
    "brzuch": "E8D27A", "brzuch_cien": "CDB760",
    "oko": "F2932E", "tusz": "1E1A14", "bialy": "FFFFFF",
    "paszcza": "7A2E2A", "jezyk": "D9667A", "palce": "A9B45E",
}

# klatki trafienia / wypuszczenia efektu (aktorzy: chwile_modulu) — ściśle wewnątrz klipów
CHWILE = {"atak": 12, "umiejetnosc": 30, "trafienie": 4, "unik": 12}

SLABOSCI = [
    "Kości Rechotka nie są R15 (własny szkielet: Root + 15 kości) — import do Roblox Studio nie był testowany.",
    "Bryły są sztywno przypięte do kości: górne końce łap siedzą w tułowiu, a przy mocnym ugięciu łapy przednie "
    "lekko wchodzą w brzuch.",
    "Sus (ruch) jest w miejscu — stopy w podporze ślizgają się po ziemi, gdy łapy się uginają.",
    "Język jest prostą belką na jednej kości (bez wygięcia); w spoczynku schowany w żuchwie i tułowiu.",
    "Łuk skoku w umiejętności robi odtwarzacz (styl „skok”); klip podnosi ropuchę najwyżej o 0,5 studa.",
    "Oczy nie mrugają (bez powiek); w upadku źrenice zostają otwarte.",
]

# ----------------------------------------------------------------------------------------------- szkielet (studs)
CIALO = (0.0, 0.95, -0.3)
GLOWA = (0.0, 1.3, 0.5)
SZCZEKA = (0.0, 1.27, 0.45)
WOLE = (0.0, 0.95, 0.85)
JEZYK = (0.0, 1.18, 0.55)
BARK = (0.95, 0.95, 0.55)
NADGARSTEK = (1.15, 0.2, 0.9)
BIODRO = (0.95, 0.9, -1.1)
KOLANO = (1.45, 0.72, 0.2)
PIETA = (1.55, 0.28, -1.0)
WYSUW_JEZYKA = 2.3

GLOWNA = "Cialo"
PLASKIE = ("DlonPL", "DlonPP", "StopaL", "StopaP")
POMIN_ZIEMIA = ("Jezyk",)


def _lu(v, zn):
    """Punkt lewej strony (+X) -> strona zn (1 = lewa, −1 = prawa)."""
    return (zn * v[0], v[1], v[2])


def _os_kosci():
    """Oś spoczynkowa kości (kierunek od stawu do następnego stawu) — do póz z kierunkiem „k”."""
    o = {}
    for s, zn in (("L", 1.0), ("P", -1.0)):
        o["LapaP" + s] = tuple(_lu(NADGARSTEK, zn)[i] - _lu(BARK, zn)[i] for i in range(3))
        o["Udo" + s] = tuple(_lu(KOLANO, zn)[i] - _lu(BIODRO, zn)[i] for i in range(3))
        o["Golen" + s] = tuple(_lu(PIETA, zn)[i] - _lu(KOLANO, zn)[i] for i in range(3))
        o["Stopa" + s] = (0.0, 0.0, 1.0)
        o["DlonP" + s] = (0.0, 0.0, 1.0)
    return o


OS = _os_kosci()


def _model(p, kosc, obrot=(0, 0, 0), pos=(0, 0, 0)):
    """Układ MODELU (0, 0, 0 = ziemia pod środkiem) na kości: bryły podaje się we współrzędnych modelu."""
    s = p.staw(kosc)
    return p.na(kosc, pos=(pos[0] - s[0], pos[1] - s[1], pos[2] - s[2]), obrot=obrot)


def zbuduj():
    p = Postac(ID, "Rechotek", typ="stwor", skala=1.0, faza=0.05, paleta=PALETA)

    p.kosc("Cialo", "Root", staw=CIALO, dl=0.6)
    p.kosc("Glowa", "Cialo", staw=GLOWA, dl=0.5)
    p.kosc("Szczeka", "Glowa", staw=SZCZEKA, dl=0.4)
    p.kosc("Wole", "Szczeka", staw=WOLE, dl=0.25)
    p.kosc("Jezyk", "Szczeka", staw=JEZYK, dl=0.4)
    for s, zn in (("L", 1.0), ("P", -1.0)):
        p.kosc("LapaP" + s, "Cialo", staw=_lu(BARK, zn), dl=0.4)
        p.kosc("DlonP" + s, "LapaP" + s, staw=_lu(NADGARSTEK, zn), dl=0.2)
        p.kosc("Udo" + s, "Cialo", staw=_lu(BIODRO, zn), dl=0.5)
        p.kosc("Golen" + s, "Udo" + s, staw=_lu(KOLANO, zn), dl=0.4)
        p.kosc("Stopa" + s, "Golen" + s, staw=_lu(PIETA, zn), dl=0.3)

    _tulow(p)
    _glowa(p)
    _paszcza(p)
    _lapy(p)

    p.zaczep("RootAttachment", "Cialo", (-CIALO[0], -CIALO[1], -CIALO[2]))
    # cel trafienia: środek łba i tułowia (tabliczkę nad głową gra stawia z wysokości)
    p.zaczep("GlowaAttachment", "Glowa", (0.0, 0.25, 0.35))
    # koniuszek języka: w spoczynku tuż za wargą, w ataku 2,3 studa przed pyskiem (Bron i Pocisk)
    p.zaczep("PyskAttachment", "Jezyk", (0.0, 0.0, 1.2))

    _klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return p


# ---------------------------------------------------------------------------------------------------- bryły
def _tulow(p):
    with _model(p, "Cialo"):
        with p.uklad(pos=(0, 1.0, -0.45), obrot=(-9, 0, 0)):
            p.blok("Tulow", (0, 0, 0), (2.4, 1.15, 2.3), "oliwka", faza=0.12)
            p.blok("Grzbiet", (0, 0.65, 0.03), (2.0, 0.3, 2.0), "oliwka", faza=0.08)
            p.blok("Zad", (0, -0.05, -1.25), (2.0, 0.9, 0.3), "oliwka", faza=0.1)
            # żółty pasek wzdłuż grzbietu (czytelny z góry) i plamy
            p.blok("Pasek grzbietu", (0, 0.815, 0.0), (0.22, 0.04, 2.0), "brzuch", "matowy", faza=0.0)
            for i, (x, z, sx, sz) in enumerate(((0.55, 0.55, 0.42, 0.4), (-0.6, 0.3, 0.5, 0.48),
                                                 (0.6, -0.45, 0.5, 0.55), (-0.5, -0.6, 0.4, 0.42))):
                p.blok("Plama grzbiet %d" % i, (x, 0.815, z), (sx, 0.04, sz), "plama", "matowy", faza=0.0)
            for zn in (1, -1):
                p.blok("Plama bok", (zn * 1.215, 0.1, -0.7), (0.04, 0.38, 0.62), "plama", "matowy", faza=0.0)
                p.blok("Plama bok przod", (zn * 1.215, 0.22, 0.35), (0.04, 0.28, 0.34), "plama", "matowy",
                       faza=0.0)
                p.blok("Plama tyl", (zn * 0.5, 0.0, -1.415), (0.4, 0.34, 0.04), "plama", "matowy", faza=0.0)
                # żółty spód boków
                p.blok("Brzuch bok", (zn * 1.215, -0.42, -0.2), (0.04, 0.26, 1.7), "brzuch", "matowy", faza=0.0)
            for i, (x, z) in enumerate(((0.95, -0.1), (-0.95, -0.25), (0.25, -0.95), (-0.3, 0.75))):
                p.blok("Brodawka %d" % i, (x, 0.6 if abs(x) > 0.9 else 0.83, z), (0.16, 0.1, 0.16), "brodawka",
                       faza=0.02)
        p.blok("Brzuch", (0, 0.55, 0.05), (2.0, 0.5, 1.6), "brzuch", faza=0.1)
        # gruczoły za oczami (ciemne wały na karku)
        for zn in (1, -1):
            p.blok("Gruczol", (zn * 0.72, 1.83, 0.3), (0.45, 0.22, 0.7), "plama", faza=0.06)


def _glowa(p):
    with _model(p, "Glowa"):
        p.blok("Leb", (0, 1.64, 1.07), (2.6, 0.72, 1.45), "oliwka", faza=0.1)
        p.blok("Leb gora", (0, 2.08, 1.0), (2.1, 0.2, 1.15), "oliwka", faza=0.06)
        p.blok("Plama leb 0", (0.0, 2.195, 1.2), (0.36, 0.03, 0.3), "plama", "matowy", faza=0.0)
        p.blok("Plama leb 1", (0.42, 2.195, 0.62), (0.26, 0.03, 0.22), "plama", "matowy", faza=0.0)
        # szeroka linia ust od boku do boku, kąciki w górę
        p.blok("Usta", (0, 1.3, 1.815), (2.5, 0.07, 0.05), "tusz", faza=0.0)
        for zn in (1, -1):
            p.blok("Usta bok", (zn * 1.315, 1.3, 1.12), (0.05, 0.07, 1.3), "tusz", faza=0.0)
            p.blok("Kacik", (zn * 1.315, 1.37, 0.4), (0.05, 0.07, 0.34), "tusz", rot=(25, 0, 0), faza=0.0)
            p.blok("Nozdrze", (zn * 0.32, 1.86, 1.815), (0.12, 0.07, 0.05), "tusz", faza=0.0)
            # oczy-kulki na czubku: olbrzymie pomarańczowe gałki na oliwkowych „kopułach”
            x = zn * 0.72
            p.walec("Oko kopula", (x, 2.25, 0.95), (0.78, 0.4, 0.78), "oliwka", segm=8)
            p.walec("Oko obwodka", (x, 2.42, 0.97), (0.8, 0.08, 0.8), "plama", "matowy", segm=8)
            p.kula("Oko", (x, 2.52, 1.0), 0.7, "oko", "polysk", segm=8)
            p.blok("Zrenica", (x, 2.53, 1.365), (0.34, 0.09, 0.06), "tusz", "polysk", faza=0.0)
            p.blok("Blysk", (x - zn * 0.1, 2.66, 1.335), (0.1, 0.1, 0.04), "bialy", faza=0.0)
        # podniebienie (widać je przy otwartym pysku)
        p.blok("Podniebienie", (0, 1.29, 1.1), (2.3, 0.04, 1.25), "paszcza", "matowy", faza=0.0)


def _paszcza(p):
    with _model(p, "Szczeka"):
        p.blok("Zuchwa", (0, 1.1, 1.1), (2.5, 0.36, 1.38), "oliwka", faza=0.08)
        p.blok("Broda", (0, 1.04, 1.805), (2.3, 0.22, 0.05), "brzuch", "matowy", faza=0.0)
        p.blok("Gardlo", (0, 0.9, 1.05), (2.2, 0.1, 1.2), "brzuch", "matowy", faza=0.02)
        p.blok("Wnetrze", (0, 1.27, 1.1), (2.3, 0.04, 1.25), "paszcza", "matowy", faza=0.0)
    with _model(p, "Wole"):
        p.blok("Wole", (0, 0.82, 0.95), (1.6, 0.4, 0.9), "brzuch", faza=0.12)
        p.blok("Wole cien", (0, 0.74, 1.405), (1.2, 0.2, 0.04), "brzuch_cien", "matowy", faza=0.0)
    with _model(p, "Jezyk"):
        p.blok("Jezyk", (0, 1.2, 0.3), (0.3, 0.1, 2.6), "jezyk", "polysk", faza=0.02)
        p.blok("Jezyk koniec", (0, 1.18, 1.55), (0.5, 0.2, 0.36), "jezyk", "polysk", faza=0.05)


def _lapy(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        with _model(p, "LapaP" + s):
            _belka(p, "Ramie", _lu((0.95, 1.05, 0.55), zn), _lu(NADGARSTEK, zn), 0.42, 0.42, "oliwka")
        with _model(p, "DlonP" + s):
            p.blok("Dlon", _lu((1.2, 0.07, 1.0), zn), (0.55, 0.14, 0.5), "oliwka", faza=0.04)
            for i, (x, z, ry) in enumerate(((1.0, 1.32, -25), (1.22, 1.38, 0), (1.44, 1.3, 25))):
                p.blok("Palec %d" % i, _lu((x, 0.05, z), zn), (0.13, 0.1, 0.36), "palce", rot=(0, zn * ry, 0),
                       faza=0.02)
        with _model(p, "Udo" + s):
            sr, rot = _belka(p, "Udo", _lu(BIODRO, zn), _lu(KOLANO, zn), 0.9, 0.8, "oliwka", nad=0.25,
                             ksztalt="kula")
            with p.uklad(pos=sr, obrot=rot):
                p.blok("Pregi uda", (zn * 0.42, 0.12, 0.0), (0.04, 0.3, 0.4), "plama", "matowy", faza=0.0)
                p.blok("Pregi uda 2", (zn * 0.36, -0.5, 0.0), (0.04, 0.22, 0.3), "plama", "matowy", faza=0.0)
        with _model(p, "Golen" + s):
            sr, rot = _belka(p, "Golen", _lu(KOLANO, zn), _lu(PIETA, zn), 0.5, 0.45, "oliwka", nad=0.08)
            with p.uklad(pos=sr, obrot=rot):
                p.blok("Pregi goleni", (zn * 0.26, 0.0, 0.0), (0.04, 0.3, 0.34), "plama", "matowy", faza=0.0)
        with _model(p, "Stopa" + s):
            p.blok("Pieta", _lu((1.55, 0.18, -1.0), zn), (0.4, 0.3, 0.36), "oliwka", faza=0.06)
            p.blok("Stopa", _lu((1.62, 0.06, -0.35), zn), (0.5, 0.12, 1.3), "oliwka", rot=(0, zn * 8, 0), faza=0.03)
            for i, (x, z, ry) in enumerate(((1.48, 0.45, -12), (1.72, 0.52, 5), (1.92, 0.4, 25))):
                p.blok("Palec stopy %d" % i, _lu((x, 0.045, z), zn), (0.12, 0.09, 0.55), "palce",
                       rot=(0, zn * ry, 0), faza=0.02)


# ---------------------------------------------------------------------------------------------------- klipy
def _nogi(przod=None, udo=None, golen=None, stopa=None, przodP=None, udoP=None, golenP=None, stopaP=None):
    """Kierunki łap (świat) lewej strony; prawa = lustro (albo osobno *P)."""
    out = {}
    for s, zn, (a, b, c, d) in (("L", 1.0, (przod, udo, golen, stopa)),
                                ("P", -1.0, (przodP or przod, udoP or udo, golenP or golen, stopaP or stopa))):
        if a:
            out["LapaP" + s] = {"k": _lu(a, zn)}
        if b:
            out["Udo" + s] = {"k": _lu(b, zn)}
        if c:
            out["Golen" + s] = {"k": _lu(c, zn)}
        if d:
            out["Stopa" + s] = {"k": _lu(d, zn)}
    return out


def _z(*czesci, **kosci):
    """Złożenie słowników pozy (późniejsze nadpisują wcześniejsze)."""
    out = {}
    for c in czesci:
        out.update(c)
    out.update(kosci)
    return out


PRZYSIAD = _nogi(przod=(0.3, -0.55, 0.55), udo=(0.55, -0.02, 1.3), golen=(0.12, -0.3, -1.22))
WYPROST = _nogi(przod=(0.15, -0.85, 0.25), udo=(0.3, -0.8, -0.55), golen=(0.1, -0.75, -0.75),
                stopa=(0.0, -0.75, -0.65))
ZWINIETE = _nogi(przod=(0.15, -0.45, 0.88), udo=(0.4, 0.15, 1.3), golen=(0.1, -0.15, -1.25), stopa=(0, 0.2, 1))
ROZJECHANE = _nogi(przod=(0.95, -0.22, 0.35), udo=(1.1, -0.12, 0.5), golen=(0.65, -0.18, -0.85))


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
    """Oddech (2,4 s): tułów lekko się kiwa, worek pod brodą pulsuje dwa razy, łeb rozgląda się w bok i wraca."""
    k = p.klip("idle", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        wole = max(0.0, math.sin(4 * math.pi * t)) ** 2
        return {"Cialo": (-1.2 * a, 0, 0), "Glowa": (1.0 * a, 9 * math.sin(2 * math.pi * t + 0.6), 0),
                "Szczeka": (1.5 * wole, 0, 0), "Wole": {"p": (0, -0.08 * wole, 0.04 * wole)}}
    _petla(k, poza)
    return k


def ruch(p, dl=24):
    """Sus w miejscu (0,8 s): przyczajenie, wybicie tylnymi łapami, lot ze stopami z tyłu, lądowanie na przednich."""
    k = p.klip("ruch", dl, petla=True)
    spocz = {}
    przys = _z(PRZYSIAD, Cialo=(4, 0, 0))
    wybicie = _z(WYPROST, Cialo=(-16, 0, 0), Glowa=(-6, 0, 0), _h=0.15)
    lot = _z(_nogi(przod=(0.15, -0.6, 0.75), udo=(0.35, -0.45, -0.8), golen=(0.1, -0.2, -1.0), stopa=(0, -0.3, -1)),
             Cialo=(-4, 0, 0), _h=0.85, _wolne=True)
    ladowanie = _z(_nogi(przod=(0.25, -0.6, 0.55), udo=(0.5, -0.3, 1.0), golen=(0.1, -0.4, -1.2)),
                   Cialo=(8, 0, 0), Glowa=(4, 0, 0), _h=0.0)
    _sekwencja(k, (0, 4, 8, 13, 18, 24), (spocz, przys, wybicie, lot, ladowanie, spocz),
               wyg={1: "we", 2: "wy", 3: "we"})
    return k


def atak(p, dl=27):
    """Lepki język (0,9 s): zadarty łeb, wypad, pysk się otwiera i język wystrzela 2,3 studa przed pysk (kl. 12),
    zwija się i ropucha wraca."""
    k = p.klip("atak", dl, petla=False)
    spocz = {}
    zamach = _z(PRZYSIAD, Cialo={"o": (-6, 0, 0), "p": (0, 0, -0.15)}, Glowa=(-10, 0, 0))
    wypad = _z(_nogi(przod=(0.15, -0.8, 0.0)), Cialo={"o": (-2, 0, 0), "p": (0, 0, 0.3)}, Glowa=(-20, 0, 0),
               Szczeka=(12, 0, 0), Jezyk={"p": (0, 0, 0.9)})
    traf = _z(_nogi(przod=(0.15, -0.85, -0.1)), Cialo={"o": (-4, 0, 0), "p": (0, 0, 0.4)}, Glowa=(-24, 0, 0),
              Szczeka=(12, 0, 0), Jezyk={"p": (0, 0, WYSUW_JEZYKA)})
    zwijanie = _z(Cialo={"o": (-1, 0, 0), "p": (0, 0, 0.25)}, Glowa=(-14, 0, 0), Szczeka=(14, 0, 0),
                  Jezyk={"p": (0, 0, 0.7)})
    zamkniety = _z(Cialo={"o": (0, 0, 0), "p": (0, 0, 0.08)}, Szczeka=(4, 0, 0))
    _sekwencja(k, (0, 7, 10, 12, 16, 20, 27), (spocz, zamach, wypad, traf, zwijanie, zamkniety, spocz),
               wyg={1: "we", 2: "l", 3: "wy"})
    return k


def umiejetnosc(p, dl=54):
    """Uderzenie z góry (1,8 s): głębokie przyczajenie (kl. 0–12), wybicie (12–16), zwinięcie w locie (16–27),
    plaśnięcie całym brzuchem z rozjechanymi łapami (kl. 30 = trafienie), chwila płasko, powrót na łapy."""
    k = p.klip("umiejetnosc", dl, petla=False)
    spocz = {}
    przys = _z(_nogi(przod=(0.4, -0.45, 0.6), udo=(0.6, 0.05, 1.3), golen=(0.15, -0.25, -1.22)),
               Cialo=(10, 0, 0), Glowa=(4, 0, 0))
    przys2 = _z(przys, Cialo=(12, 0, 0), Glowa=(-4, 0, 0))
    wybicie = _z(WYPROST, Cialo=(-28, 0, 0), Glowa=(-8, 0, 0), _h=0.35, _wolne=True)
    zwiniete = _z(ZWINIETE, Cialo=(-6, 0, 0), Glowa=(-4, 0, 0), _h=0.5, _wolne=True)
    opad = _z(_nogi(przod=(0.55, -0.4, 0.7), udo=(0.8, 0.05, 0.9), golen=(0.4, -0.1, -1.1), stopa=(0.3, 0, 1)),
              Cialo=(14, 0, 0), Glowa=(6, 0, 0), Szczeka=(8, 0, 0), _h=0.25, _wolne=True)
    plask = _z(ROZJECHANE, Cialo=(4, 0, 0), Glowa=(8, 0, 0), Szczeka=(6, 0, 0))
    plask2 = _z(ROZJECHANE, Cialo=(1, 0, 0), Glowa=(2, 0, 0))
    wstaje = _z(PRZYSIAD, Cialo=(-4, 0, 0), Glowa=(-6, 0, 0))
    _sekwencja(k, (0, 8, 12, 16, 23, 28, 30, 38, 46, 54),
               (spocz, przys, przys2, wybicie, zwiniete, opad, plask, plask2, wstaje, spocz),
               wyg={2: "l", 3: "wy", 5: "we", 6: "wy"})
    return k


def trafienie(p, dl=18):
    """Szarpnięcie w tył (0,6 s, najdalej kl. 4): łeb zadarty, pysk uchylony, przednie łapy do przodu."""
    k = p.klip("trafienie", dl, petla=False)
    spocz = {}
    szarp = _z(_nogi(przod=(0.2, -0.65, 0.65)), Cialo={"o": (-14, 0, 0), "p": (0, 0, -0.35)}, Glowa=(-12, 0, 0),
               Szczeka=(12, 0, 0))
    odbicie = _z(Cialo={"o": (5, 0, 0), "p": (0, 0, -0.12)}, Glowa=(4, 0, 0), Szczeka=(2, 0, 0))
    _sekwencja(k, (0, 4, 10, 18), (spocz, szarp, odbicie, spocz), wyg={0: "wy"})
    return k


def unik(p, dl=27):
    """Sus w lewo o 1,6 studa (najdalej kl. 12) i drugi sus z powrotem na miejsce (0,9 s)."""
    k = p.klip("unik", dl, petla=False)
    spocz = {}
    przys = _z(PRZYSIAD, Cialo={"o": (0, 0, -8), "p": (0, 0, 0)})
    lot = _z(_nogi(przod=(0.5, -0.6, 0.5), udo=(0.5, -0.4, -0.7), golen=(0.2, -0.3, -1.0), stopa=(0, -0.3, -1)),
             Cialo={"o": (-8, 0, 10), "p": (0.9, 0, 0)}, _h=0.7, _wolne=True)
    lad = _z(PRZYSIAD, Cialo={"o": (6, 0, 4), "p": (1.6, 0, 0)}, Glowa=(0, -12, 0))
    lot2 = _z(_nogi(przod=(0.3, -0.6, 0.6), udo=(0.4, -0.4, -0.7), golen=(0.2, -0.3, -1.0), stopa=(0, -0.3, -1)),
              Cialo={"o": (-6, 0, -8), "p": (0.8, 0, 0)}, _h=0.5, _wolne=True)
    lad2 = _z(PRZYSIAD, Cialo={"o": (5, 0, 0), "p": (0, 0, 0)})
    _sekwencja(k, (0, 3, 8, 12, 16, 21, 27), (spocz, przys, lot, lad, lot2, lad2, spocz),
               wyg={1: "wy", 2: "we", 4: "we"})
    return k


def upadek(p, dl=60):
    """Upadek (2 s): zatacza się w tył, ostatni podryg, plaśnięcie brzuchem z rozjechanymi łapami, przechył na
    prawy bok, język wypada z pyska, ropucha zapada się w błoto (kl. 60 = leży)."""
    k = p.klip("upadek", dl, petla=False)
    spocz = {}
    chwiej = _z(_nogi(przod=(0.25, -0.7, 0.5)), Cialo={"o": (-12, 0, 6), "p": (0, 0, -0.3)}, Glowa=(-10, 15, 0),
                Szczeka=(10, 0, 0))
    chwiej2 = _z(PRZYSIAD, Cialo={"o": (6, -10, -8), "p": (0.1, 0, -0.2)}, Glowa=(14, -10, 0), Szczeka=(4, 0, 0))
    podryg = _z(WYPROST, Cialo={"o": (-10, -6, 4), "p": (0.05, 0, -0.1)}, Glowa=(-6, 0, 0), _h=0.25, _wolne=True)
    plask = _z(ROZJECHANE, Cialo={"o": (6, -6, -4), "p": (0, 0, 0)}, Glowa=(12, 0, 0), Szczeka=(14, 0, 0),
               Jezyk={"p": (0, 0, 0.6)})
    bok = _z(_nogi(przod=(0.9, 0.1, 0.4), udo=(1.0, 0.25, 0.5), golen=(0.6, 0.1, -0.85),
                   przodP=(0.9, -0.3, 0.3), udoP=(1.0, -0.15, 0.45), golenP=(0.6, -0.2, -0.85)),
             Cialo={"o": (4, -8, -28), "p": (0, 0, 0)}, Glowa=(16, 0, -6), Szczeka=(20, 0, 0),
             Jezyk={"p": (0, 0, 1.1)}, _wolne=True)
    bloto = _z(bok, _h=-0.3)
    _sekwencja(k, (0, 8, 16, 21, 26, 36, 60), (spocz, chwiej, chwiej2, podryg, plask, bok, bloto),
               wyg={3: "we", 4: "wy", 5: "s", 6: "l"})
    return k


def wiwat(p, dl=60):
    """Radość (pętla 2 s): dwa podskoki w miejscu i po każdym rechot — worek pod brodą nadęty, pysk uchylony."""
    k = p.klip("wiwat", dl, petla=True)
    spocz = {}
    przys = _z(PRZYSIAD, Cialo=(4, 0, 0))
    hop = _z(_nogi(przod=(0.3, -0.6, 0.6), udo=(0.35, -0.5, -0.7), golen=(0.1, -0.3, -1.0), stopa=(0, -0.3, -1)),
             Cialo=(-14, 0, 0), Glowa=(-8, 0, 0), Szczeka=(10, 0, 0), _h=0.9, _wolne=True)
    lad = _z(PRZYSIAD, Cialo=(6, 0, 0))
    rechot = _z(Cialo=(-6, 0, 0), Glowa=(-12, 0, 0), Szczeka=(12, 0, 0), Wole={"p": (0, -0.22, 0.12)})
    hop2 = _z(hop, Cialo=(-14, 0, -6), Glowa=(-8, 10, 0))
    rechot2 = _z(rechot, Glowa=(-12, -10, 0))
    _sekwencja(k, (0, 4, 10, 16, 22, 30, 34, 40, 46, 52, 60),
               (spocz, przys, hop, lad, rechot, spocz, przys, hop2, lad, rechot2, spocz),
               wyg={1: "wy", 2: "we", 6: "wy", 7: "we"})
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
