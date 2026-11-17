# -*- coding: utf-8 -*-
"""ZWIJOGON — zwykły przeciwnik Dżungli (Polana Zwijogonów): kameleon z liści na pazurzastych łapach, ze zwiniętym
w spiralę ogonem i oczami na wieżyczkach, ok. 3,4 studa (gracz ma 5,7).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/zwijogon.py --wyj <folder> --klip skupienie

Opis z zarysu biomów (swiat/biomy/PLAN_BIOMOW.md, rozdz. „2. Dżungla”; tam roboczo „Liściołaz”): kameleon z liści na
pazurzastych łapach, zwinięty ogon. Klasa w przegrodzie: Zwiadowca (często unika). Umiejętności silnika: `skupienie`
(kameleon wtapia się w liście, oczy na wieżyczkach krążą i obie zatrzymują się na celu; złotą aurę robi odtwarzacz)
i `rozszarpanie` (staje słupka na tylnych łapach, podparty ogonem, i tnie pazurami na krzyż).

Sylwetka (z daleka): wysoki, wąski z boku tułów (jak liść postawiony na sztorc), na grzbiecie grzebień z liściowych
ząbków, z przodu łeb z wysokim hełmem (czerwona krawędź); po bokach łba dwie wieżyczki z żółtymi oczami (turkusowy
pierścień), za tułowiem ogon zwinięty w ślimak w dół i do przodu; cztery cienkie, rozstawione łapy z jasnymi
pazurami. Boki pokryte zachodzącymi na siebie liśćmi w dwóch zieleniach, wzdłuż boku żółty pas (czytelny na
zielonym tle polany).

Paleta (Dżungla): zieleń 2FA34A i 6CCB4A, ciemna zieleń żyłek, pnie 5C3A22 (pazury u nasady), kwiaty E5392B / F2B030
(hełm, pas, oczy), turkus 2EC4B6 (pierścień oka), jasne pazury.

Szkielet (typ „stwor”; L = lewa = +X, P = prawa = −X):
    Root > Cialo > {Glowa > {Szczeka, OkoL, OkoP},
                    RamieL > PrzedramieL > DlonL, RamieP > PrzedramieP > DlonP,
                    UdoL > GolenL > StopaL, UdoP > GolenP > StopaP,
                    Ogon1 > Ogon2 > Ogon3 > Ogon4}
- `Cialo` niesie całego kameleona (sus, unik, upadek); Dlon*/Stopa* trzymane płasko na ziemi (liczone w module);
- `Oko*` = wieżyczka z okiem: obraca się wokół swojej podstawy na łbie (kameleon patrzy każdym okiem osobno);
- ogon to płaska spirala (w płaszczyźnie YZ) na czterech kościach — obrót kości wokół X zwija i rozwija ślimak.

Klipy (30 kl./s; kameleon patrzy w +Z):
  idle (pętla 2,4 s: kołysanie w przód i w tył jak na gałęzi, oczy krążą osobno, ogon oddycha), ruch (pętla 1,0 s:
  chód na przemian po przekątnej, ogon się kołysze), atak (zamach prawą łapą i cięcie pazurami w dół przed siebie,
  trafienie kl. 12, 0,9 s), umiejetnosc (rozszarpanie: staje słupka podparty ogonem, cięcie lewą i prawą łapą na
  krzyż — trafienie kl. 28, opada na cztery łapy, 1,6 s), skupienie (przywiera do ziemi, oczy krążą, kl. 22 obie
  wieżyczki zatrzymują się na celu — aura, 1,5 s), trafienie (szarpnięcie w tył, 0,6 s), unik (sus w lewo 1,6 studa
  i powrót, 0,9 s), upadek (zatacza się, przewraca na prawy bok, ogon się rozwija; 2 s, leży w ostatniej klatce),
  wiwat (pętla 2 s: podskoki, macha lewą łapą, ogon zwija się i rozwija, oczy wirują).
Klipy są zapisane jako pozy kluczowe zamienione na klucz w KAŻDEJ klatce (wygładzanie „liniowo”), więc próbki
liniowe, Blender i Roblox dają to samo. Najniższy punkt ciała stoi na ziemi (y = 0) poza chwilami lotu.
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Postac, katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor

ID = "zwijogon"

PALETA = {
    "lisc": "2FA34A", "lisc_jasny": "6CCB4A", "lisc_ciemny": "1F7A36", "zylka": "A6E07A",
    "brzuch": "9CDB6E", "pas": "F2B030", "kask": "E5392B", "oko": "F2B030", "turkus": "2EC4B6",
    "tusz": "17121F", "bialy": "FFFFFF", "paszcza": "B8323A", "pazur": "F2E6C8", "pien": "5C3A22",
}

# klatki trafienia / wypuszczenia efektu (aktorzy: chwile_modulu) — ściśle wewnątrz klipów
CHWILE = {"atak": 12, "umiejetnosc": 28, "skupienie": 22, "trafienie": 4, "unik": 12}

SLABOSCI = [
    "Kości Zwijogona nie są R15 (własny szkielet: Root + 21 kości) — import do Roblox Studio nie był testowany.",
    "Zmiany odcienia przy skupieniu nie ma w klipie (rig z klocków nie zmienia kolorów): klip daje przywarcie do ziemi "
    "i oczy zatrzymane na celu, złotą aurę robi odtwarzacz (styl „na_siebie”).",
    "Ogon to cztery sztywne kawałki spirali — przy mocnym zwinięciu na stykach kości widać drobne schodki.",
    "Bryły są sztywno przypięte do kości: w podporze stopy ślizgają się lekko po ziemi, gdy tułów się kołysze.",
    "Liście na bokach to płaskie romby (bez wygięcia).",
]

# ----------------------------------------------------------------------------------------------- szkielet (studs)
CIALO = (0.0, 1.75, 0.0)
GLOWA = (0.0, 2.05, 1.05)
SZCZEKA = (0.0, 1.85, 1.2)
OKO = (0.48, 2.25, 1.72)            # podstawa wieżyczki lewego oka (na boku łba)
BARK = (0.5, 1.45, 0.75)
LOKIEC = (1.15, 1.05, 1.0)
NADGARSTEK = (0.95, 0.2, 1.2)
BIODRO = (0.5, 1.4, -0.82)
KOLANO = (1.15, 1.02, -1.05)
KOSTKA = (0.92, 0.2, -0.86)
OGON_START = (0.0, 1.88, -1.28)     # nasada ogona (koniec tułowia)
SPIRALA = (1.12, -1.95)              # środek spirali ogona (y, z)
R0, R1 = 0.76, 0.17                  # promień spirali na początku i na końcu
KAT_MAX = 540.0                      # półtora obrotu
GRANICE_OGONA = (0.0, 120.0, 260.0, 400.0, KAT_MAX)    # kąty, w których zaczynają się kości Ogon1…Ogon4

GLOWNA = "Cialo"
PLASKIE = ("DlonL", "DlonP", "StopaL", "StopaP")
POMIN_ZIEMIA = ()


def _lu(v, zn):
    """Punkt lewej strony (+X) -> strona zn (1 = lewa, −1 = prawa)."""
    return (zn * v[0], v[1], v[2])


def _roznica(a, b):
    return tuple(b[i] - a[i] for i in range(3))


def _spirala(kat):
    """Punkt osi ogona na spirali: kat w stopniach od góry spirali, rośnie w tył, w dół i do przodu (ślimak w dół)."""
    r = R0 - (R0 - R1) * kat / KAT_MAX
    a = math.radians(kat)
    return (0.0, SPIRALA[0] + r * math.cos(a), SPIRALA[1] - r * math.sin(a))


def _os_kosci():
    o = {}
    for s, zn in (("L", 1.0), ("P", -1.0)):
        o["Ramie" + s] = _roznica(_lu(BARK, zn), _lu(LOKIEC, zn))
        o["Przedramie" + s] = _roznica(_lu(LOKIEC, zn), _lu(NADGARSTEK, zn))
        o["Udo" + s] = _roznica(_lu(BIODRO, zn), _lu(KOLANO, zn))
        o["Golen" + s] = _roznica(_lu(KOLANO, zn), _lu(KOSTKA, zn))
        o["Dlon" + s] = (0.0, 0.0, 1.0)
        o["Stopa" + s] = (0.0, 0.0, 1.0)
    return o


OS = _os_kosci()


def _model(p, kosc, obrot=(0, 0, 0), pos=(0, 0, 0)):
    """Układ MODELU (0, 0, 0 = ziemia pod środkiem) na kości: bryły podaje się we współrzędnych modelu."""
    s = p.staw(kosc)
    return p.na(kosc, pos=(pos[0] - s[0], pos[1] - s[1], pos[2] - s[2]), obrot=obrot)


def zbuduj():
    p = Postac(ID, "Zwijogon", typ="stwor", skala=1.0, faza=0.04, paleta=PALETA)

    p.kosc("Cialo", "Root", staw=CIALO, dl=0.6)
    p.kosc("Glowa", "Cialo", staw=GLOWA, dl=0.5)
    p.kosc("Szczeka", "Glowa", staw=SZCZEKA, dl=0.4)
    for s, zn in (("L", 1.0), ("P", -1.0)):
        p.kosc("Oko" + s, "Glowa", staw=_lu(OKO, zn), dl=0.25)
    for s, zn in (("L", 1.0), ("P", -1.0)):
        p.kosc("Ramie" + s, "Cialo", staw=_lu(BARK, zn), dl=0.35)
        p.kosc("Przedramie" + s, "Ramie" + s, staw=_lu(LOKIEC, zn), dl=0.35)
        p.kosc("Dlon" + s, "Przedramie" + s, staw=_lu(NADGARSTEK, zn), dl=0.2)
        p.kosc("Udo" + s, "Cialo", staw=_lu(BIODRO, zn), dl=0.35)
        p.kosc("Golen" + s, "Udo" + s, staw=_lu(KOLANO, zn), dl=0.35)
        p.kosc("Stopa" + s, "Golen" + s, staw=_lu(KOSTKA, zn), dl=0.2)
    p.kosc("Ogon1", "Cialo", staw=OGON_START, dl=0.3)
    for i in range(1, 4):
        p.kosc("Ogon%d" % (i + 1), "Ogon%d" % i, staw=_spirala(GRANICE_OGONA[i]), dl=0.25)

    _tulow(p)
    _glowa(p)
    _oczy(p)
    _lapy(p)
    _ogon(p)

    p.zaczep("RootAttachment", "Cialo", (-CIALO[0], -CIALO[1], -CIALO[2]))
    # cel trafienia: pierś pod łbem (tabliczkę nad głową gra stawia z wysokości)
    p.zaczep("GlowaAttachment", "Cialo", _roznica(CIALO, (0.0, 1.85, 0.85)))
    # koniuszki pazurów prawej przedniej łapy (Bron) i pysk (Pocisk)
    p.zaczep("PazurAttachment", "DlonP", _roznica(_lu(NADGARSTEK, -1), (-0.9, 0.08, 1.78)))
    p.zaczep("PyskAttachment", "Szczeka", _roznica(SZCZEKA, (0.0, 1.85, 2.55)))

    _klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return p


# ---------------------------------------------------------------------------------------------------- bryły
def _lisc(p, nazwa, pos, dl, szer, kolor, rot=(0, 0, 0), grub=0.06, zylka=True):
    """Liść-romb: płytka obrócona o 45° wokół swojej osi grubości, z jaśniejszą żyłką wzdłuż."""
    with p.uklad(pos=pos, obrot=rot):
        p.blok(nazwa, (0, 0, 0), (grub, szer, dl), kolor, "matowy", faza=0.0)
        p.klin(nazwa + " czubek", (0, 0, dl / 2 + szer * 0.3), (grub, szer, szer * 0.6), kolor, "matowy",
               rot=(0, 0, 0), faza=0.0)
        if zylka:
            p.blok(nazwa + " zylka", (0, 0, 0.02), (grub + 0.02, 0.05, dl * 0.9), "zylka", "matowy", faza=0.0)


def _tulow(p):
    with _model(p, "Cialo"):
        with p.uklad(pos=(0, 1.88, -0.1), obrot=(-4, 0, 0)):
            p.blok("Tulow", (0, 0, 0), (1.2, 1.3, 2.5), "lisc", faza=0.1)
            p.blok("Grzbiet", (0, 0.72, -0.05), (0.8, 0.22, 2.2), "lisc_ciemny", faza=0.05)
            # grzebień z liściowych ząbków wzdłuż grzbietu (sylwetka z boku)
            for i, z in enumerate((0.95, 0.55, 0.15, -0.25, -0.65, -1.05)):
                h = 0.5 - 0.035 * i
                kol = "lisc_jasny" if i % 2 else "lisc"
                p.klin("Zab grzebienia %d" % i, (0, 0.83 + h / 2, z), (0.1, h, 0.42), kol, "matowy",
                       rot=(0, 180, 0), faza=0.0)
            # żółty pas wzdłuż boku i liście-łuski zachodzące na siebie
            for zn in (1, -1):
                p.blok("Pas boku", (zn * 0.61, -0.1, 0.1), (0.04, 0.16, 2.2), "pas", "matowy", faza=0.0)
                for i, (y, z, rx, kol) in enumerate(((0.32, 0.75, -35, "lisc_jasny"), (0.38, 0.05, -35, "lisc"),
                                                     (0.3, -0.7, -35, "lisc_jasny"), (-0.42, 0.45, 35, "lisc"),
                                                     (-0.45, -0.35, 35, "lisc_jasny"))):
                    _lisc(p, "Lisc boku %d" % i, (zn * 0.63, y, z), 0.7, 0.36, kol, rot=(rx, 0, 0))
        p.blok("Brzuch", (0, 1.27, -0.05), (0.95, 0.3, 2.0), "brzuch", faza=0.06)
        # kark (łączy tułów z łbem)
        p.blok("Kark", (0, 2.0, 1.1), (0.95, 0.9, 0.6), "lisc", faza=0.06)


def _glowa(p):
    with _model(p, "Glowa"):
        p.blok("Leb", (0, 2.18, 1.62), (1.0, 0.86, 1.15), "lisc", faza=0.08)
        p.ostroslup("Pysk", (0, 2.04, 2.4), (0.8, 0.6, 0.6), "lisc", rot=(90, 0, 0), gora=(0.48, 0.36), faza=0.0)
        for zn in (1, -1):
            p.blok("Nozdrze", (zn * 0.12, 2.12, 2.705), (0.08, 0.07, 0.03), "tusz", faza=0.0)
        # hełm: wysoki klin pochylony do tyłu z czerwoną krawędzią
        # hełm: klin wznoszący się ku tyłowi (wysoka ściana z tyłu), czerwona krawędź wzdłuż skosu
        p.klin("Helm", (0, 2.95, 1.3), (0.6, 1.0, 1.1), "lisc", rot=(0, 180, 0), faza=0.03)
        p.blok("Krawedz helmu", (0, 2.99, 1.32), (0.2, 0.1, 1.45), "kask", "matowy", rot=(42, 0, 0), faza=0.0)
        for zn in (1, -1):
            p.blok("Pas helmu", (zn * 0.305, 2.7, 1.25), (0.03, 0.12, 0.85), "kask", "matowy", rot=(42, 0, 0),
                   faza=0.0)
        for zn in (1, -1):
            # linia pyska od czubka do kąta („uśmiech” kameleona)
            p.blok("Usta bok", (zn * 0.4, 1.86, 1.95), (0.04, 0.05, 1.0), "tusz", faza=0.0)
            p.blok("Kacik", (zn * 0.505, 1.9, 1.42), (0.04, 0.05, 0.22), "tusz", rot=(-25, 0, 0), faza=0.0)
            p.blok("Pas policzka", (zn * 0.505, 2.0, 1.3), (0.04, 0.12, 0.5), "pas", "matowy", faza=0.0)
        p.blok("Podniebienie", (0, 1.84, 1.95), (0.72, 0.04, 0.95), "paszcza", "matowy", faza=0.0)
    with _model(p, "Szczeka"):
        p.blok("Zuchwa", (0, 1.7, 1.9), (0.82, 0.26, 1.2), "lisc", faza=0.05)
        p.blok("Broda", (0, 1.6, 1.45), (0.7, 0.2, 0.5), "brzuch", faza=0.04)
        p.blok("Wnetrze", (0, 1.83, 1.9), (0.7, 0.04, 1.1), "paszcza", "matowy", faza=0.0)


def _oczy(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        # wieżyczka: oś (lokalne X) skierowana w bok i 45° do przodu; stożkowata (dwa walce leżące wzdłuż osi:
        # rozmiar walca = (średnica, długość, średnica), obrót Rz 90°), kula oka i źrenica
        with _model(p, "Oko" + s), p.uklad(pos=_lu(OKO, zn), obrot=(0, -45 * zn, 0)):
            p.walec("Wiezyczka", (zn * 0.14, 0, 0), (0.64, 0.3, 0.64), "lisc", rot=(0, 0, 90), segm=8)
            p.walec("Wiezyczka 2", (zn * 0.33, 0, 0), (0.52, 0.16, 0.52), "lisc_jasny", rot=(0, 0, 90), segm=8)
            p.walec("Pierscien", (zn * 0.42, 0, 0), (0.48, 0.06, 0.48), "turkus", rot=(0, 0, 90), faza=0.0,
                    segm=8)
            p.kula("Oko", (zn * 0.52, 0, 0), 0.42, "oko", "polysk", segm=8)
            p.blok("Zrenica", (zn * 0.71, 0, 0), (0.06, 0.2, 0.2), "tusz", "polysk", faza=0.0)
            p.blok("Blysk", (zn * 0.72, 0.08, 0.06), (0.04, 0.07, 0.07), "bialy", faza=0.0)


def _lapa(p, s, zn, kosc, nazwa, a, b, gr):
    with _model(p, kosc):
        _belka(p, nazwa, _lu(a, zn), _lu(b, zn), gr, gr, "lisc", nad=gr * 0.3)


def _stopa(p, nazwa, kosc, zn, srodek, przod):
    """Płaska stopa z pazurami: dwa pęczki palców (jak u kameleona) i jasne pazury."""
    with _model(p, kosc):
        p.blok(nazwa, _lu(srodek, zn), (0.42, 0.14, 0.42), "lisc", faza=0.04)
        for i, (dx, ry) in enumerate(((-0.14, -28), (0.0, 0), (0.15, 30))):
            x = srodek[0] + dx
            p.blok("Palec %d" % i, _lu((x + 0.05 * math.sin(math.radians(ry)), 0.06, przod), zn),
                   (0.12, 0.1, 0.3), "lisc_jasny", rot=(0, zn * ry, 0), faza=0.02)
            p.blok("Pazur %d" % i, _lu((x + 0.11 * math.sin(math.radians(ry)), 0.05, przod + 0.2), zn),
                   (0.08, 0.08, 0.16), "pazur", rot=(0, zn * ry, 0), faza=0.0)


def _lapy(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        _lapa(p, s, zn, "Ramie" + s, "Ramie", BARK, LOKIEC, 0.3)
        _lapa(p, s, zn, "Przedramie" + s, "Przedramie", LOKIEC, NADGARSTEK, 0.25)
        _stopa(p, "Dlon", "Dlon" + s, zn, (0.9, 0.07, 1.3), 1.56)
        _lapa(p, s, zn, "Udo" + s, "Udo", BIODRO, KOLANO, 0.33)
        _lapa(p, s, zn, "Golen" + s, "Golen", KOLANO, KOSTKA, 0.26)
        _stopa(p, "Stopa", "Stopa" + s, zn, (0.9, 0.07, -0.74), -0.48)
        # kolano i łokieć: zgrubienie stawu
        with _model(p, "Ramie" + s):
            p.blok("Lokiec", _lu(LOKIEC, zn), (0.32, 0.3, 0.32), "lisc_ciemny", faza=0.05)
        with _model(p, "Udo" + s):
            p.blok("Kolano", _lu(KOLANO, zn), (0.36, 0.34, 0.36), "lisc_ciemny", faza=0.05)


def _ogon(p):
    """Spirala ogona: nasada (prosto w tył) i półtora obrotu ślimaka; grubość maleje, pasy w dwóch zieleniach."""
    kroki = 24
    punkty = [OGON_START] + [_spirala(KAT_MAX * i / kroki) for i in range(kroki + 1)]
    katy = [None] + [KAT_MAX * i / kroki for i in range(kroki + 1)]
    for i in range(len(punkty) - 1):
        a, b = punkty[i], punkty[i + 1]
        kat_sr = 0.0 if katy[i] is None else (katy[i] + katy[i + 1]) / 2.0
        kosc = "Ogon%d" % (1 + sum(1 for g in GRANICE_OGONA[1:4] if kat_sr >= g))
        gr = 0.44 - 0.29 * (kat_sr / KAT_MAX)
        kol = "lisc" if i % 2 == 0 else "lisc_jasny"
        with _model(p, kosc):
            sr, rot = _belka(p, "Ogon %d" % i, a, b, gr, gr * 1.1, kol, nad=0.05)
            if i % 3 == 1 and i < 20:
                # listek na zewnętrznej krawędzi spirali
                with p.uklad(pos=sr, obrot=rot):
                    p.blok("Listek ogona %d" % i, (0, 0, -gr * 0.55), (0.05, 0.2, 0.22), "lisc_ciemny", "matowy",
                           rot=(45, 0, 0), faza=0.0)


# ---------------------------------------------------------------------------------------------------- klipy
def _z(*czesci, **kosci):
    """Złożenie słowników pozy (późniejsze nadpisują wcześniejsze)."""
    out = {}
    for c in czesci:
        out.update(c)
    out.update(kosci)
    return out


def _mix(a, b, s):
    """Kierunek pośredni między a i b (s = 0…1)."""
    a, b = _norm(a), _norm(b)
    return _norm(tuple(a[i] + (b[i] - a[i]) * s for i in range(3)))


def _lapy_poz(ramie=None, przed=None, udo=None, golen=None, ramieP=None, przedP=None, udoP=None, golenP=None):
    """Kierunki łap w świecie: ramie/przed/udo/golen = lewa strona (+X), prawa dostaje ich lustro; *P = kierunek
    prawej łapy podany wprost w świecie (prawa strona to −X). None = spoczynek względem rodzica."""
    out = {}
    for n, v, vp in (("Ramie", ramie, ramieP), ("Przedramie", przed, przedP), ("Udo", udo, udoP),
                     ("Golen", golen, golenP)):
        if v:
            out[n + "L"] = {"k": v}
        if vp:
            out[n + "P"] = {"k": vp}
        elif v:
            out[n + "P"] = {"k": _lu(v, -1)}
    return out


def _ogon_poz(zwin=0.0, bok=0.0):
    """Ogon: zwin > 0 zwija ślimak mocniej (stopnie na kość), < 0 rozwija; bok = wychylenie w bok (stopnie)."""
    return {"Ogon1": (-zwin * 0.6, bok, 0), "Ogon2": (-zwin, bok * 0.5, 0), "Ogon3": (-zwin, 0, 0),
            "Ogon4": (-zwin * 1.2, 0, 0)}


def _oczy_poz(ryL=0.0, ryP=0.0, rxL=0.0, rxP=0.0):
    """Wieżyczki oczu: ry > 0 kieruje oko do przodu (lewe i prawe w lustrze), rx > 0 w dół."""
    return {"OkoL": (rxL, -ryL, 0), "OkoP": (rxP, ryP, 0)}


def _klipy(p):
    idle(p)
    ruch(p)
    atak(p)
    umiejetnosc(p)
    skupienie(p)
    trafienie(p)
    unik(p)
    upadek(p)
    wiwat(p)


def idle(p, dl=72):
    """Spoczynek (2,4 s): kołysanie w przód i w tył jak na gałęzi, oczy krążą każde osobno, ogon oddycha."""
    k = p.klip("idle", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        pz = {"Cialo": {"o": (1.5 * a, 0, 0), "p": (0, 0, 0.08 * a)}, "Glowa": (-1.5 * a, 4 * math.sin(4 * math.pi * t), 0),
              "Szczeka": (2.0 * max(0.0, math.sin(4 * math.pi * t + 1.0)) ** 4, 0, 0)}
        pz.update(_oczy_poz(28 * math.sin(2 * math.pi * t), 22 * math.sin(2 * math.pi * t + 2.1),
                            12 * math.sin(4 * math.pi * t + 0.5), -10 * math.sin(2 * math.pi * t + 1.0)))
        pz.update(_ogon_poz(3 * math.sin(2 * math.pi * t - 0.8), 2 * a))
        return pz
    _petla(k, poza)
    return k


def ruch(p, dl=30):
    """Chód w miejscu (1,0 s): łapy na przemian po przekątnej (LP z tyłu z PP z przodu), tułów kołysze się na boki,
    łeb kiwa, ogon wychyla się w przeciwfazie."""
    k = p.klip("ruch", dl, petla=True)

    def krok(faza, a, b, przod=True):
        """Kierunki dwóch odcinków łapy (świat) w fazie 0…1: w pierwszej połowie łapa w powietrzu idzie do przodu,
        w drugiej stoi i przesuwa się w tył (podpora)."""
        w = max(0.0, math.sin(2 * math.pi * faza))                  # uniesienie
        n = -math.cos(2 * math.pi * faza)                            # wysunięcie (+ do przodu)
        if przod:
            return ((a[0], a[1] + 0.45 * w, a[2] + 0.3 * n + 0.25 * w),
                    (b[0], b[1] + 0.25 * w, b[2] + 0.3 * n + 0.35 * w))
        return ((a[0], a[1] + 0.4 * w, a[2] + 0.3 * n + 0.2 * w),
                (b[0], b[1] + 0.2 * w, b[2] + 0.25 * n + 0.3 * w))

    def poza(t):
        a = math.sin(2 * math.pi * t)
        lp = krok(t, OS["RamieL"], OS["PrzedramieL"])                      # lewa przednia z prawą tylną
        pt = krok(t, OS["UdoP"], OS["GolenP"], przod=False)
        pp = krok(t + 0.5, OS["RamieP"], OS["PrzedramieP"])               # prawa przednia z lewą tylną
        lt = krok(t + 0.5, OS["UdoL"], OS["GolenL"], przod=False)
        pz = _lapy_poz(ramie=lp[0], przed=lp[1], udo=lt[0], golen=lt[1], ramieP=pp[0], przedP=pp[1], udoP=pt[0],
                       golenP=pt[1])
        pz.update({"Cialo": {"o": (0, 6 * a, 4 * a), "p": (0, 0, 0)}, "Glowa": (2 * math.sin(4 * math.pi * t), -5 * a, 0)})
        pz.update(_ogon_poz(2 * math.sin(4 * math.pi * t), -10 * a))
        pz.update(_oczy_poz(10, 10, 6 * math.sin(4 * math.pi * t), 6 * math.sin(4 * math.pi * t)))
        return pz
    _petla(k, poza)
    return k


def atak(p, dl=27):
    """Cięcie pazurami (0,9 s): kameleon cofa się i unosi prawą łapę wysoko (kl. 0–8), wypad i cięcie w dół przed
    siebie (kl. 12 = trafienie), dobicie przy ziemi i powrót."""
    k = p.klip("atak", dl, petla=False)
    spocz = {}
    wolna = ("DlonP",)                                  # prawa dłoń idzie za przedramieniem (pazury w górze)
    zamach = _z(_lapy_poz(ramieP=(-0.75, 0.62, -0.05), przedP=(-0.4, 0.88, 0.2)),
                Cialo={"o": (-10, 10, -8), "p": (0, 0, -0.15)}, Glowa=(-6, -8, 0), _wolne=wolna,
                **_oczy_poz(25, 20))
    tniecie = _z(_lapy_poz(ramieP=(-0.2, -0.1, 1.0), przedP=(-0.1, -0.55, 0.85)),
                 Cialo={"o": (8, -8, 0), "p": (0, 0, 0.35)}, Glowa=(6, 4, 0), Szczeka=(14, 0, 0), _wolne=wolna,
                 **_oczy_poz(30, 30))
    dobicie = _z(_lapy_poz(ramieP=(-0.25, -0.45, 0.85), przedP=(-0.1, -0.85, 0.5)),
                 Cialo={"o": (9, -10, 0), "p": (0, 0, 0.4)}, Glowa=(8, 6, 0), Szczeka=(8, 0, 0), _wolne=wolna,
                 **_oczy_poz(30, 30))
    powrot = _z(Cialo={"o": (2, -2, 0), "p": (0, 0, 0.12)})
    _sekwencja(k, (0, 8, 12, 16, 21, 27), (spocz, zamach, tniecie, dobicie, powrot, spocz),
               wyg={1: "we", 2: "wy"})
    return k


def umiejetnosc(p, dl=48):
    """Rozszarpanie (1,6 s): staje słupka na tylnych łapach podparty ogonem, obie łapy w górze (kl. 0–14), cięcie lewą
    łapą na skos (kl. 20), cięcie prawą na krzyż (kl. 28 = trafienie), opada na cztery łapy i wraca."""
    k = p.klip("umiejetnosc", dl, petla=False)
    spocz = {}
    tyl = dict(udo=(0.45, -0.75, 0.35), golen=(0.1, -0.8, -0.45))
    wolne = ("DlonL", "DlonP")                           # przednie dłonie w powietrzu idą za przedramionami
    slupek = _z(_lapy_poz(ramie=(0.6, 0.72, 0.2), przed=(0.35, 0.85, 0.3), **tyl),
                Cialo={"o": (-42, 0, 0), "p": (0, 0, -0.2)}, Glowa=(26, 0, 0), Szczeka=(18, 0, 0), _wolne=wolne,
                **_z(_ogon_poz(-12), _oczy_poz(40, 40)))
    zamachL = _z(_lapy_poz(ramie=(0.7, 0.7, -0.1), przed=(0.45, 0.85, 0.1), ramieP=(-0.6, 0.65, 0.3),
                           przedP=(-0.3, 0.8, 0.4), **tyl),
                 Cialo={"o": (-44, -10, 0), "p": (0, 0, -0.2)}, Glowa=(26, 8, 0), Szczeka=(20, 0, 0), _wolne=wolne,
                 **_z(_ogon_poz(-12), _oczy_poz(45, 45)))
    tnieL = _z(_lapy_poz(ramie=(-0.2, 0.0, 1.0), przed=(-0.45, -0.35, 0.8), ramieP=(-0.7, 0.7, 0.0),
                         przedP=(-0.4, 0.85, 0.2), **tyl),
               Cialo={"o": (-30, 14, 0), "p": (0, 0, 0.15)}, Glowa=(18, -6, 0), Szczeka=(22, 0, 0), _wolne=wolne,
               **_z(_ogon_poz(-10), _oczy_poz(45, 45)))
    tnieP = _z(_lapy_poz(ramie=(0.4, -0.3, 0.85), przed=(0.2, -0.6, 0.6), ramieP=(0.2, 0.0, 1.0),
                         przedP=(0.45, -0.35, 0.8), **tyl),
               Cialo={"o": (-22, -14, 0), "p": (0, 0, 0.45)}, Glowa=(14, 8, 0), Szczeka=(22, 0, 0), _wolne=wolne,
               **_z(_ogon_poz(-8), _oczy_poz(45, 45)))
    opada = _z(_lapy_poz(ramie=(0.4, -0.55, 0.6), przed=(0.0, -0.85, 0.4)),
               Cialo={"o": (4, -4, 0), "p": (0, 0, 0.35)}, Glowa=(4, 2, 0), Szczeka=(6, 0, 0))
    _sekwencja(k, (0, 10, 16, 20, 25, 28, 36, 48), (spocz, slupek, zamachL, tnieL, zamachL, tnieP, opada, spocz),
               wyg={1: "we", 2: "we", 3: "wy", 4: "we", 5: "wy"})
    return k


def skupienie(p, dl=45):
    """Skupienie (1,5 s): przywiera brzuchem do liści (łapy rozjeżdżają się, łeb nisko, ogon zwinięty ciaśniej),
    oczy krążą każde w swoją stronę (kl. 6–18), a w kl. 22 obie wieżyczki zatrzymują się na celu — aura; chwila
    bez ruchu i powrót."""
    k = p.klip("skupienie", dl, petla=False)
    spocz = {}
    nisko = dict(ramie=(0.75, -0.35, 0.45), przed=(0.2, -0.8, 0.45), udo=(0.8, -0.3, -0.4), golen=(0.15, -0.8, 0.35))
    przyw = _z(_lapy_poz(**nisko), Cialo={"o": (3, 0, 0), "p": (0, -0.35, 0)}, Glowa=(4, 0, 0),
               **_z(_ogon_poz(8), _oczy_poz(-30, 40, 20, -25)))
    kraza = _z(przyw, **_oczy_poz(50, -35, -25, 20))
    kraza2 = _z(przyw, **_oczy_poz(-20, 55, 25, 10))
    cel = _z(_lapy_poz(**nisko), Cialo={"o": (5, 0, 0), "p": (0, -0.38, 0.05)}, Glowa=(6, 0, 0),
             **_z(_ogon_poz(10), _oczy_poz(42, 42, 6, 6)))
    trzyma = _z(cel, Cialo={"o": (5, 0, 0), "p": (0, -0.38, 0.08)})
    _sekwencja(k, (0, 6, 12, 18, 22, 32, 45), (spocz, przyw, kraza, kraza2, cel, trzyma, spocz),
               wyg={3: "wy", 5: "s"})
    return k


def trafienie(p, dl=18):
    """Szarpnięcie w tył (0,6 s, najdalej kl. 4): łeb zadarty, pysk uchylony, oczy rozbiegają się na boki."""
    k = p.klip("trafienie", dl, petla=False)
    spocz = {}
    szarp = _z(_lapy_poz(ramie=(0.4, -0.55, 0.55)), Cialo={"o": (-12, 0, 0), "p": (0, 0, -0.3)}, Glowa=(-14, 0, 0),
               Szczeka=(14, 0, 0), **_z(_ogon_poz(-6), _oczy_poz(-35, -35, -15, -15)))
    odbicie = _z(Cialo={"o": (4, 0, 0), "p": (0, 0, -0.1)}, Glowa=(4, 0, 0), Szczeka=(3, 0, 0),
                 **_oczy_poz(-10, -10))
    _sekwencja(k, (0, 4, 10, 18), (spocz, szarp, odbicie, spocz), wyg={0: "wy"})
    return k


def unik(p, dl=27):
    """Sus w lewo o 1,6 studa (najdalej kl. 12) i drugi sus z powrotem na miejsce (0,9 s)."""
    k = p.klip("unik", dl, petla=False)
    spocz = {}
    przys = _z(_lapy_poz(ramie=(0.6, -0.5, 0.45), udo=(0.7, -0.35, -0.3)), Cialo={"o": (0, 0, -8), "p": (0, -0.15, 0)})
    lot = _z(_lapy_poz(ramie=(0.55, -0.6, 0.5), przed=(0.3, -0.7, 0.6), udo=(0.45, -0.5, -0.6),
                       golen=(0.1, -0.5, -0.85)),
             Cialo={"o": (-6, 0, 12), "p": (0.9, 0, 0)}, _h=0.6, _wolne=True, **_z(_ogon_poz(-8, 12), _oczy_poz(0, 40)))
    lad = _z(_lapy_poz(ramie=(0.6, -0.5, 0.45), udo=(0.7, -0.35, -0.3)), Cialo={"o": (4, -12, 4), "p": (1.6, -0.12, 0)},
             Glowa=(0, -14, 0), **_oczy_poz(-30, 50))
    lot2 = _z(lot, Cialo={"o": (-6, 0, -8), "p": (0.8, 0, 0)}, _h=0.45, **_ogon_poz(-6, -10))
    lad2 = _z(przys, Cialo={"o": (3, 0, 0), "p": (0, -0.1, 0)})
    _sekwencja(k, (0, 3, 8, 12, 16, 21, 27), (spocz, przys, lot, lad, lot2, lad2, spocz),
               wyg={1: "wy", 2: "we", 4: "we"})
    return k


def upadek(p, dl=60):
    """Upadek (2 s): zatacza się w tył, chwieje na boki, przewraca na prawy bok z bezwładnymi łapami, ogon się
    rozwija, oczy opadają (kl. 60 = leży)."""
    k = p.klip("upadek", dl, petla=False)
    spocz = {}
    chwiej = _z(_lapy_poz(ramie=(0.4, -0.6, 0.5)), Cialo={"o": (-12, 0, 6), "p": (0, 0, -0.3)}, Glowa=(-10, 15, 0),
                Szczeka=(10, 0, 0), **_oczy_poz(-20, 30, 10, -10))
    chwiej2 = _z(_lapy_poz(ramie=(0.6, -0.5, 0.4), udo=(0.7, -0.4, -0.3)), Cialo={"o": (6, -10, -8), "p": (0.1, -0.1, -0.2)},
                 Glowa=(14, -10, 0), **_z(_ogon_poz(-6), _oczy_poz(30, -20)))
    pada = _z(_lapy_poz(ramie=(0.8, -0.1, 0.5), przed=(0.6, -0.5, 0.4), udo=(0.85, 0.0, -0.4), golen=(0.5, -0.6, -0.4),
                        ramieP=(-0.7, -0.6, 0.3), przedP=(-0.3, -0.8, 0.3), udoP=(-0.7, -0.5, -0.3)),
              Cialo={"o": (4, -6, 40), "p": (0, 0, 0)}, Glowa=(10, 0, 10), Szczeka=(16, 0, 0),
              _wolne=True, **_z(_ogon_poz(-15, 6), _oczy_poz(-10, -10, 30, 30)))
    lezy = _z(_lapy_poz(ramie=(0.85, 0.45, 0.4), przed=(0.6, 0.3, 0.6), udo=(0.85, 0.4, -0.4), golen=(0.6, 0.2, -0.6),
                        ramieP=(-0.6, -0.75, 0.3), przedP=(-0.2, -0.8, 0.5), udoP=(-0.6, -0.7, -0.4),
                        golenP=(-0.2, -0.8, -0.5)),
              Cialo={"o": (2, -8, 82), "p": (0, 0, 0)}, Glowa=(14, 0, 12), Szczeka=(22, 0, 0),
              _wolne=True, **_z(_ogon_poz(-30, 0), _oczy_poz(-15, -15, 40, 40)))
    _sekwencja(k, (0, 8, 18, 30, 44, 60), (spocz, chwiej, chwiej2, pada, lezy, lezy),
               wyg={2: "we", 3: "wy", 4: "l"})
    return k


def wiwat(p, dl=60):
    """Radość (pętla 2 s): dwa podskoki w miejscu, po każdym macha lewą łapą, ogon zwija się i rozwija, oczy wirują
    w przeciwne strony."""
    k = p.klip("wiwat", dl, petla=True)
    spocz = {}
    przys = _z(_lapy_poz(ramie=(0.6, -0.5, 0.45), udo=(0.7, -0.35, -0.3)), Cialo={"o": (4, 0, 0), "p": (0, -0.12, 0)})
    hop = _z(_lapy_poz(ramie=(0.5, -0.6, 0.55), przed=(0.3, -0.7, 0.6), udo=(0.45, -0.5, -0.6), golen=(0.1, -0.5, -0.85)),
             Cialo=(-14, 0, 0), Glowa=(-8, 0, 0), Szczeka=(10, 0, 0), _h=0.6, _wolne=True,
             **_z(_ogon_poz(-10), _oczy_poz(50, -40)))
    lad = _z(przys, Cialo={"o": (6, 0, 0), "p": (0, -0.12, 0)})
    macha = _z(_lapy_poz(ramie=(0.6, 0.7, 0.35), przed=(0.75, 0.6, 0.1)), Cialo={"o": (-8, 0, -10), "p": (0, 0, 0)},
               Glowa=(-10, 12, 0), Szczeka=(12, 0, 0), **_z(_ogon_poz(10), _oczy_poz(-40, 50, 15, -15)))
    macha2 = _z(_lapy_poz(ramie=(0.6, 0.7, 0.35), przed=(0.35, 0.8, 0.45)), Cialo={"o": (-8, 0, -10), "p": (0, 0, 0)},
                Glowa=(-10, -8, 0), Szczeka=(6, 0, 0), **_z(_ogon_poz(10), _oczy_poz(40, -50, -15, 15)))
    _sekwencja(k, (0, 4, 10, 16, 22, 28, 34, 40, 46, 52, 60),
               (spocz, przys, hop, lad, macha, macha2, przys, hop, lad, macha, spocz),
               wyg={1: "wy", 2: "we", 7: "we"})
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
