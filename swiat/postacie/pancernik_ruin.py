# -*- coding: utf-8 -*-
"""PANCERNIK RUIN — rzadki potwór Dżungli (leże w ruinach): pancernik obrośnięty płytami starego kamienia z rytami
i mchem, ze świecącymi turkusowymi szczelinami, ok. 7 studów długości z ogonem i ok. 3,9 studa wysokości (gracz ma
5,7).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/pancernik_ruin.py --wyj <folder> --klip umiejetnosc

Opis (propozycja do zarysu biomów, swiat/biomy/PLAN_BIOMOW.md, rozdz. „2. Dżungla” — w tabeli zarysu leża jeszcze
nie ma): pancernik obrośnięty płytami starego kamienia z rytami i mchem, świecące turkusowe szczeliny. Rzadki potwór
leża w ruinach, klasa Wojownik. Zwykły cios = szarża z kamiennym hełmem; umiejętność silnika `kamienna_skora` =
zwija się w kulę: płyty pancerza zamykają się, a w szwach między nimi rozbłyskują turkusowe pasy (tarcza na siebie).

Sylwetka (z daleka): niska, długa kopuła z siedmiu pasów kamiennych płyt (sklepienie jak w ruinie), z przodu
wąski ryj w kamiennym hełmie, z tyłu ogon z kamiennych pierścieni; cztery krótkie łapy z ciemnymi pazurami do
kopania. Na grzbiecie mech, paproć i czerwony kwiatek; na bokach ryty (kwadratowe spirale) i turkusowe pęknięcia
(Neon), na czole świecący znak.

Paleta (Dżungla + kamień ruin): kamień 8E8A7E w trzech odcieniach, ryty ciemne, mech 6CCB4A / 2FA34A, skóra B07A44,
pazury pnie 5C3A22, kwiat E5392B / F2B030, świecące szczeliny i znak turkus 2EC4B6.

Szkielet (typ „stwor”; L = lewa = +X, P = prawa = −X):
    Root > Cialo > {Przod > {Glowa > Szczeka, LapaPL > DlonPL, LapaPP > DlonPP},
                    Tyl > {Ogon1 > Ogon2, LapaTL > StopaTL, LapaTP > StopaTP}}
- pancerz w trzech częściach: środek na `Cialo`, przód na `Przod` (z łbem i przednimi łapami), tył na `Tyl`
  (z ogonem i tylnymi łapami) — przy zwijaniu przód i tył obracają się w dół wokół szwów i chowają łapy pod kulę;
- turkusowe pasy w szwach (Neon) leżą pod zakładkami płyt: w spoczynku prawie ich nie widać, w kuli świecą na
  grzbiecie;
- Dlon*/Stopa* trzymane płasko na ziemi (liczone w module).

Klipy (30 kl./s; patrzy w +Z):
  idle (pętla 2,4 s: oddech, węszy ryjem, ogon się kołysze), ruch (pętla 1,0 s: kłus po przekątnej), atak (szarża:
  cofa się z łbem w dół i uderza kamiennym hełmem — trafienie kl. 13, 0,9 s), umiejetnosc (kamienna skóra: zwija się
  w kulę, kl. 22 płyty zamknięte i świecą szwy, kołysze się i rozwija; 1,8 s), trafienie (0,6 s), unik (sus w lewo
  1,5 studa i powrót, 0,9 s), upadek (przewraca się na grzbiet łapami do góry; 2 s, leży w ostatniej klatce), ryk
  (dokładnie 60 klatek = 2,0 s, pętla: staje na tylnych łapach, unosi ryj i otwiera paszczę).
Klipy są zapisane jako pozy kluczowe zamienione na klucz w KAŻDEJ klatce (wygładzanie „liniowo”).
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Postac, katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor

ID = "pancernik_ruin"

PALETA = {
    "kamien": "8E8A7E", "kamien_jasny": "A8A496", "kamien_ciemny": "6A665C", "ryt": "45423B",
    "mech": "6CCB4A", "mech_ciemny": "2FA34A", "skora": "B07A44", "skora_ciemna": "8A5A32",
    "pazur": "5C3A22", "swiatlo": "2EC4B6", "kwiat": "E5392B", "kwiat_srodek": "F2B030",
    "tusz": "17121F", "bialy": "FFFFFF", "paszcza": "6E1E24",
}

CHWILE = {"atak": 13, "umiejetnosc": 22, "trafienie": 4, "unik": 12}

SLABOSCI = [
    "Kości Pancernika nie są R15 (własny szkielet: Root + 15 kości) — import do Roblox Studio nie był testowany.",
    "Kula przy kamiennej skórze to trzy sztywne części pancerza obrócone wokół szwów — z boku widać, że to „klamra”, "
    "a nie idealna kula; łapy chowają się pod nią.",
    "Świecenie szwów i znaku: materiał Neon na rigu z klocków; poświaty (PointLight) nie ma. Szwy świecą cały czas — "
    "w spoczynku przykrywają je zakładki płyt.",
    "Łapy są jednoczęściowe (bez kolan): krok to wymach łapy; stopy w podporze ślizgają się lekko po ziemi.",
    "Aurę kamiennej skóry (kamienie wokół) robi odtwarzacz (styl „na_siebie”).",
]

# ----------------------------------------------------------------------------------------------- szkielet (studs)
CIALO = (0.0, 1.9, 0.0)
PRZOD = (0.0, 1.9, 0.72)            # szew przód–środek (oś zwijania)
TYL = (0.0, 1.9, -0.72)             # szew środek–tył
GLOWA = (0.0, 1.85, 2.05)
SZCZEKA = (0.0, 1.62, 2.55)
OGON1 = (0.0, 1.55, -2.05)
OGON2 = (0.0, 1.0, -2.9)
BARK = (0.92, 1.3, 1.25)             # lewa przednia łapa
DLON = (1.0, 0.22, 1.4)
BIODRO = (0.92, 1.3, -1.2)           # lewa tylna łapa
STOPA = (1.0, 0.22, -1.1)
CY_LUKU = 1.72                       # wysokość środka łuku sklepienia pancerza
KATY_PLYT = (-6, 24, 57, 90, 123, 156, 186)

GLOWNA = "Cialo"
PLASKIE = ("DlonPL", "DlonPP", "StopaTL", "StopaTP")
POMIN_ZIEMIA = ()


def _lu(v, zn):
    return (zn * v[0], v[1], v[2])


def _roznica(a, b):
    return tuple(b[i] - a[i] for i in range(3))


def _os_kosci():
    o = {}
    for s, zn in (("L", 1.0), ("P", -1.0)):
        o["LapaP" + s] = _roznica(_lu(BARK, zn), _lu(DLON, zn))
        o["LapaT" + s] = _roznica(_lu(BIODRO, zn), _lu(STOPA, zn))
        o["DlonP" + s] = (0.0, 0.0, 1.0)
        o["StopaT" + s] = (0.0, 0.0, 1.0)
    o["Ogon1"] = _roznica(OGON1, OGON2)
    return o


OS = _os_kosci()


def _model(p, kosc, obrot=(0, 0, 0), pos=(0, 0, 0)):
    """Układ MODELU (0, 0, 0 = ziemia pod środkiem) na kości: bryły podaje się we współrzędnych modelu."""
    s = p.staw(kosc)
    return p.na(kosc, pos=(pos[0] - s[0], pos[1] - s[1], pos[2] - s[2]), obrot=obrot)


def zbuduj():
    p = Postac(ID, "Pancernik Ruin", typ="stwor", skala=1.0, faza=0.06, paleta=PALETA)

    p.kosc("Cialo", "Root", staw=CIALO, dl=0.8)
    p.kosc("Przod", "Cialo", staw=PRZOD, dl=0.6)
    p.kosc("Tyl", "Cialo", staw=TYL, dl=0.6)
    p.kosc("Glowa", "Przod", staw=GLOWA, dl=0.5)
    p.kosc("Szczeka", "Glowa", staw=SZCZEKA, dl=0.4)
    p.kosc("Ogon1", "Tyl", staw=OGON1, dl=0.6)
    p.kosc("Ogon2", "Ogon1", staw=OGON2, dl=0.5)
    for s, zn in (("L", 1.0), ("P", -1.0)):
        p.kosc("LapaP" + s, "Przod", staw=_lu(BARK, zn), dl=0.4)
        p.kosc("DlonP" + s, "LapaP" + s, staw=_lu(DLON, zn), dl=0.2)
        p.kosc("LapaT" + s, "Tyl", staw=_lu(BIODRO, zn), dl=0.4)
        p.kosc("StopaT" + s, "LapaT" + s, staw=_lu(STOPA, zn), dl=0.2)

    _pancerz(p)
    _ozdoby(p)
    _glowa(p)
    _ogon(p)
    _lapy(p)

    p.zaczep("RootAttachment", "Cialo", (-CIALO[0], -CIALO[1], -CIALO[2]))
    # cel trafienia: środek boku pancerza od przodu (pierś pod kołnierzem)
    p.zaczep("GlowaAttachment", "Przod", _roznica(PRZOD, (0.0, 2.1, 1.6)))
    # czoło kamiennego hełmu (Bron przy szarży) i ryj (Pocisk)
    p.zaczep("HelmAttachment", "Glowa", _roznica(GLOWA, (0.0, 2.2, 3.05)))
    p.zaczep("PyskAttachment", "Szczeka", _roznica(SZCZEKA, (0.0, 1.55, 3.85)))

    _klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return p


# ---------------------------------------------------------------------------------------------------- bryły
def _plyta_luku(p, nazwa, kat, R, z, dl, kolor="kamien", szer=1.12, grub=0.34, cy=CY_LUKU):
    """Płyta sklepienia pancerza: kąt na łuku (90 = grzbiet, 0 = lewy bok), promień R, środek pasa w z."""
    a = math.radians(kat)
    pos = (R * math.cos(a), cy + R * math.sin(a), z)
    p.blok(nazwa, pos, (szer, grub, dl), kolor, "matowy", rot=(0, 0, kat - 90), faza=0.05)
    return pos


def _pas(p, nazwa, R, z, dl=0.78, kolory=("kamien", "kamien_jasny")):
    for i, kat in enumerate(KATY_PLYT):
        _plyta_luku(p, "%s %d" % (nazwa, i), kat, R, z, dl, kolory[i % 2])
    # krawędź pasa (ciemniejszy wał na grzbiecie, czytelny podział na pasy)
    for i, kat in enumerate((40, 90, 140)):
        _plyta_luku(p, "%s wal %d" % (nazwa, i), kat, R + 0.17, z - dl / 2 + 0.07, 0.12, "kamien_ciemny", szer=1.0,
                    grub=0.06)


def _szew(p, nazwa, R, z):
    """Świecący pas w szwie (pod zakładką płyt): kilka krótkich odcinków na łuku, trochę pod powierzchnią."""
    for i, kat in enumerate((30, 62, 90, 118, 150)):
        a = math.radians(kat)
        p.blok("%s %d" % (nazwa, i), (R * math.cos(a), CY_LUKU + R * math.sin(a), z), (0.62, 0.12, 0.16),
               "swiatlo", "swiecacy", rot=(0, 0, kat - 90), faza=0.0)


def _pancerz(p):
    """Skóra pod pancerzem i trzy części sklepienia z płyt (środek, przód z kołnierzem, tył z tarczą zadu)."""
    with _model(p, "Cialo"):
        p.blok("Brzuch", (0, 1.45, 0.0), (2.2, 1.0, 1.7), "skora", "matowy", faza=0.15)
        _pas(p, "Pancerz srodek A", 1.62, 0.36)
        _pas(p, "Pancerz srodek B", 1.62, -0.36, kolory=("kamien_jasny", "kamien"))
        _szew(p, "Szew przod", 1.42, 0.7)
        _szew(p, "Szew tyl", 1.42, -0.7)
    with _model(p, "Przod"):
        p.blok("Piers", (0, 1.4, 1.35), (2.0, 0.9, 1.2), "skora", "matowy", faza=0.12)
        _pas(p, "Pancerz przod A", 1.56, 1.08)
        _pas(p, "Pancerz przod B", 1.46, 1.74, kolory=("kamien_jasny", "kamien"))
        # kołnierz: płyta czołowa nad karkiem
        p.blok("Kolnierz", (0, 2.75, 2.12), (2.3, 1.0, 0.3), "kamien_ciemny", "matowy", faza=0.06)
        p.blok("Kolnierz gora", (0, 3.15, 2.0), (1.8, 0.3, 0.45), "kamien", "matowy", faza=0.05)
    with _model(p, "Tyl"):
        p.blok("Zad", (0, 1.4, -1.35), (2.0, 0.9, 1.2), "skora", "matowy", faza=0.12)
        _pas(p, "Pancerz tyl A", 1.56, -1.08)
        _pas(p, "Pancerz tyl B", 1.44, -1.74, kolory=("kamien_jasny", "kamien"))
        p.blok("Tarcza zadu", (0, 2.3, -2.12), (2.1, 1.3, 0.3), "kamien_ciemny", "matowy", faza=0.06)


def _ozdoby(p):
    """Ryty (kwadratowe spirale), turkusowe pęknięcia, mech, paproć i kwiatek na grzbiecie."""
    with _model(p, "Cialo"):
        for zn in (1, -1):
            for j, z in enumerate((0.36, -0.36)):
                # kwadratowa spirala z trzech kresek na płycie bocznej (kąt 24 / 156)
                kat = 24 if zn > 0 else 156
                a = math.radians(kat)
                c = (1.81 * math.cos(a), CY_LUKU + 1.81 * math.sin(a), z)
                with p.uklad(pos=c, obrot=(0, 0, kat - 90)):
                    p.blok("Ryt %d a" % j, (0, 0, 0.18), (0.5, 0.04, 0.06), "ryt", "matowy", faza=0.0)
                    p.blok("Ryt %d b" % j, (0.22, 0, 0.0), (0.06, 0.04, 0.42), "ryt", "matowy", faza=0.0)
                    p.blok("Ryt %d c" % j, (0.0, 0, -0.18), (0.5, 0.04, 0.06), "ryt", "matowy", faza=0.0)
                    p.blok("Ryt %d d" % j, (-0.1, 0, 0.0), (0.06, 0.04, 0.2), "ryt", "matowy", faza=0.0)
        # turkusowe pęknięcie zygzakiem przez grzbiet
        for i, (x, z, ry) in enumerate(((0.45, 0.42, 35), (0.2, 0.2, -30), (-0.05, 0.0, 35), (-0.3, -0.22, -30))):
            p.blok("Peknieci %d" % i, (x, 3.53, z), (0.06, 0.04, 0.34), "swiatlo", "swiecacy", rot=(0, ry, 0),
                   faza=0.0)
        # mech i paproć
        p.blok("Mech grzbiet", (-0.4, 3.53, -0.3), (0.9, 0.05, 0.75), "mech", "matowy", faza=0.0)
        p.blok("Mech bok", (-1.25, 3.0, 0.2), (0.6, 0.05, 0.6), "mech_ciemny", "matowy", rot=(0, 0, 33), faza=0.0)
        for i, (rz, rx, h) in enumerate(((-25, -15, 1.0), (15, 10, 0.85), (40, -30, 0.7), (-50, 20, 0.6))):
            with p.uklad(pos=(-0.45, 3.5, -0.35), obrot=(rx, 0, rz)):
                p.blok("Paproc %d" % i, (0, h / 2, 0), (0.08, h, 0.3), "mech_ciemny", "matowy", faza=0.0)
                p.blok("Paproc listki %d" % i, (0, h * 0.6, 0), (0.24, h * 0.5, 0.06), "mech", "matowy", faza=0.0)
    with _model(p, "Przod"):
        p.blok("Mech przod", (0.35, 3.38, 1.2), (0.7, 0.05, 0.55), "mech", "matowy", faza=0.0)
        for i, (x, z, ry) in enumerate(((-1.12, 1.05, 20), (-1.18, 1.3, -25))):
            p.blok("Peknieci boku %d" % i, (x, 2.9, z), (0.05, 0.28, 0.06), "swiatlo", "swiecacy",
                   rot=(0, 0, 33 + ry), faza=0.0)
    with _model(p, "Tyl"):
        p.blok("Mech tyl", (0.3, 3.35, -1.1), (0.8, 0.05, 0.6), "mech_ciemny", "matowy", faza=0.0)
        # kwiatek w mchu
        for i in range(5):
            a = math.radians(90 + i * 72)
            p.blok("Kwiatek %d" % i, (0.3 + 0.1 * math.cos(a), 3.42, -1.1 + 0.1 * math.sin(a)), (0.13, 0.06, 0.13),
                   "kwiat", "matowy", rot=(0, 45 + i * 72, 0), faza=0.0)
        p.blok("Kwiatek srodek", (0.3, 3.45, -1.1), (0.08, 0.05, 0.08), "kwiat_srodek", "matowy", faza=0.0)
        for zn in (1, -1):
            kat = 24 if zn > 0 else 156
            a = math.radians(kat)
            c = (1.73 * math.cos(a), CY_LUKU + 1.73 * math.sin(a), -1.08)
            with p.uklad(pos=c, obrot=(0, 0, kat - 90)):
                p.blok("Ryt tyl", (0, 0, 0), (0.42, 0.04, 0.42), "ryt", "matowy", rot=(0, 45, 0), faza=0.0)
                p.blok("Ryt tyl srodek", (0, 0.01, 0), (0.16, 0.04, 0.16), "swiatlo", "swiecacy", rot=(0, 45, 0),
                       faza=0.0)


def _glowa(p):
    with _model(p, "Glowa"):
        p.blok("Szyja", (0, 1.75, 1.95), (1.1, 0.9, 0.6), "skora", "matowy", faza=0.1)
        p.blok("Leb", (0, 1.9, 2.5), (1.15, 0.95, 1.05), "skora", "matowy", faza=0.12)
        # długi ryj zwężony ku przodowi (ostrosłup położony do przodu), mały nos na końcu
        p.ostroslup("Ryj", (0, 1.74, 3.45), (0.7, 0.95, 0.5), "skora", "matowy", rot=(90, 0, 0), gora=(0.3, 0.24),
                    faza=0.0)
        p.blok("Nos", (0, 1.76, 3.95), (0.26, 0.2, 0.08), "skora_ciemna", "matowy", faza=0.02)
        for zn in (1, -1):
            p.blok("Nozdrze", (zn * 0.06, 1.77, 3.995), (0.05, 0.06, 0.02), "tusz", faza=0.0)
            # oczy na przedniej ścianie łba, obok nasady ryja (widać je od przodu)
            p.blok("Oko", (zn * 0.43, 1.98, 3.04), (0.17, 0.17, 0.06), "tusz", "polysk", faza=0.0)
            p.blok("Blysk oka", (zn * 0.4, 2.02, 3.075), (0.06, 0.06, 0.02), "bialy", faza=0.0)
            # duże uszy sterczące spod hełmu w bok i do tyłu
            p.blok("Ucho", (zn * 0.62, 2.55, 2.2), (0.18, 0.62, 0.36), "skora_ciemna", "matowy",
                   rot=(-25, 0, -zn * 35), faza=0.04)
            p.blok("Ucho srodek", (zn * 0.66, 2.58, 2.25), (0.06, 0.42, 0.22), "skora", "matowy",
                   rot=(-25, 0, -zn * 35), faza=0.0)
        # kamienny hełm z mchem i świecącym znakiem na czole
        with p.uklad(pos=(0, 2.45, 2.62), obrot=(8, 0, 0)):
            p.blok("Helm", (0, 0, 0), (1.25, 0.3, 1.25), "kamien", "matowy", faza=0.06)
            p.blok("Helm czolo", (0, -0.04, 0.62), (1.05, 0.42, 0.22), "kamien_jasny", "matowy", faza=0.05)
            p.blok("Znak", (0, -0.03, 0.74), (0.3, 0.06, 0.03), "swiatlo", "swiecacy", faza=0.0)
            p.blok("Znak 2", (0, -0.03, 0.74), (0.06, 0.3, 0.03), "swiatlo", "swiecacy", faza=0.0)
            p.blok("Mech helmu", (0.2, 0.17, -0.2), (0.6, 0.05, 0.5), "mech", "matowy", faza=0.0)
    with _model(p, "Szczeka"):
        p.blok("Zuchwa", (0, 1.45, 3.25), (0.56, 0.2, 1.2), "skora_ciemna", "matowy", faza=0.05)
        p.blok("Wnetrze", (0, 1.56, 3.25), (0.46, 0.04, 1.1), "paszcza", "matowy", faza=0.0)


def _ogon(p):
    with _model(p, "Ogon1"):
        _belka(p, "Ogon nasada", (0, 1.62, -1.95), OGON2, 0.62, 0.62, "skora", "matowy")
        for i, (t, r) in enumerate(((0.15, 0.56), (0.5, 0.5), (0.85, 0.45))):
            c = tuple(OGON1[j] + (OGON2[j] - OGON1[j]) * t for j in range(3))
            _belka(p, "Pierscien %d" % i, (c[0], c[1] + 0.12, c[2] + 0.14), (c[0], c[1] - 0.12, c[2] - 0.14),
                   2 * r, 2 * r, "kamien" if i % 2 else "kamien_jasny", "matowy", faza=0.04)
    with _model(p, "Ogon2"):
        koniec = (0.0, 0.42, -3.55)
        _belka(p, "Ogon koniec", OGON2, koniec, 0.36, 0.36, "skora", "matowy", nad=0.05)
        for i, (t, r) in enumerate(((0.2, 0.4), (0.6, 0.32))):
            c = tuple(OGON2[j] + (koniec[j] - OGON2[j]) * t for j in range(3))
            _belka(p, "Pierscien konca %d" % i, (c[0], c[1] + 0.1, c[2] + 0.1), (c[0], c[1] - 0.1, c[2] - 0.1),
                   2 * r, 2 * r, "kamien_jasny" if i % 2 else "kamien", "matowy", faza=0.03)


def _lapy(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        for kosc, dlon, a, b in (("LapaP", "DlonP", BARK, DLON), ("LapaT", "StopaT", BIODRO, STOPA)):
            with _model(p, kosc + s):
                _belka(p, "Lapa", _lu((a[0] - 0.05, a[1] + 0.25, a[2]), zn), _lu(b, zn), 0.62, 0.66, "skora", "matowy",
                       nad=0.05)
                p.blok("Luska lapy", _lu((a[0] + 0.25, a[1] - 0.45, a[2] + 0.05), zn), (0.08, 0.4, 0.5), "kamien_ciemny",
                       "matowy", faza=0.0)
            with _model(p, dlon + s):
                p.blok("Stopa", _lu((b[0], 0.12, b[2] + 0.12), zn), (0.66, 0.24, 0.74), "skora_ciemna", "matowy",
                       faza=0.05)
                for i, dx in enumerate((-0.2, 0.0, 0.2)):
                    p.blok("Pazur %d" % i, _lu((b[0] + dx, 0.07, b[2] + 0.58), zn), (0.13, 0.12, 0.4), "pazur", "matowy",
                           rot=(12, 0, 0), faza=0.02)


# ---------------------------------------------------------------------------------------------------- klipy
def _z(*czesci, **kosci):
    out = {}
    for c in czesci:
        out.update(c)
    out.update(kosci)
    return out


def _lapy_poz(przod=None, tyl=None, przodP=None, tylP=None):
    """Kierunki łap w świecie: przod/tyl = lewa strona (+X), prawa = lustro; *P = prawa łapa wprost w świecie."""
    out = {}
    for n, v, vp in (("LapaP", przod, przodP), ("LapaT", tyl, tylP)):
        if v:
            out[n + "L"] = {"k": v}
        if vp:
            out[n + "P"] = {"k": vp}
        elif v:
            out[n + "P"] = {"k": _lu(v, -1)}
    return out


WOLNE = ("DlonPL", "DlonPP", "StopaTL", "StopaTP")


def _klipy(p):
    idle(p)
    ruch(p)
    atak(p)
    umiejetnosc(p)
    trafienie(p)
    unik(p)
    upadek(p)
    ryk(p)


def idle(p, dl=72):
    """Spoczynek (2,4 s): pancerz unosi się z oddechem, ryj węszy w dół i na boki, ogon kołysze się."""
    k = p.klip("idle", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        w = max(0.0, math.sin(6 * math.pi * t)) ** 2 * (1.0 if t < 0.5 else 0.0)
        return {"Cialo": (-0.8 * a, 0, 0.6 * math.cos(2 * math.pi * t)), "Przod": (0.8 * a, 0, 0),
                "Glowa": (6 * w + 3 * a, 10 * math.sin(2 * math.pi * t + 0.8), 0), "Szczeka": (3 * w, 0, 0),
                "Ogon1": (2 * a, 8 * math.sin(2 * math.pi * t - 0.6), 0), "Ogon2": (0, 10 * math.sin(2 * math.pi * t - 1.4), 0)}
    _petla(k, poza)
    return k


def ruch(p, dl=30):
    """Kłus w miejscu (1,0 s): łapy po przekątnej (lewa przednia z prawą tylną), pancerz kołysze się, ogon w bok."""
    k = p.klip("ruch", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        b = math.sin(2 * math.pi * t + math.pi)
        pz = {"LapaPL": (-24 * a, 0, 0), "LapaTP": (-24 * a, 0, 0), "LapaPP": (-24 * b, 0, 0), "LapaTL": (-24 * b, 0, 0),
              "Cialo": (2 * math.sin(4 * math.pi * t), 4 * a, 3 * a), "Glowa": (-3 * math.sin(4 * math.pi * t), -4 * a, 0),
              "Ogon1": (0, -10 * a, 0), "Ogon2": (0, -8 * a, 0),
              "_h": 0.06 * abs(math.sin(2 * math.pi * t)), "_wolne": WOLNE}
        return pz
    _petla(k, poza)
    return k


def atak(p, dl=27):
    """Szarża (0,9 s): cofa się na tylnych łapach, łeb nisko (kl. 0–8), wypad i uderzenie kamiennym hełmem przed
    siebie (kl. 13 = trafienie), odbicie i powrót."""
    k = p.klip("atak", dl, petla=False)
    spocz = {}
    zamach = _z(_lapy_poz(przod=(0.1, -0.85, -0.2), tyl=(0.1, -0.9, 0.35)),
                Cialo={"o": (7, 0, 0), "p": (0, 0, -0.5)}, Przod=(5, 0, 0), Glowa=(24, 0, 0), Ogon1=(-12, 0, 0),
                _wolne=WOLNE)
    wypad = _z(_lapy_poz(przod=(0.1, -0.7, 0.75), tyl=(0.1, -0.75, -0.6)),
               Cialo={"o": (-2, 0, 0), "p": (0, 0, 0.55)}, Przod=(2, 0, 0), Glowa=(12, 0, 0), Ogon1=(8, 0, 0), _h=0.15,
               _wolne=WOLNE)
    traf = _z(_lapy_poz(przod=(0.1, -0.75, 0.6), tyl=(0.1, -0.8, -0.5)),
              Cialo={"o": (5, 0, 0), "p": (0, 0, 0.85)}, Przod=(6, 0, 0), Glowa=(26, 0, 0), Szczeka=(6, 0, 0),
              Ogon1=(10, 0, 0), _wolne=WOLNE)
    odbicie = _z(Cialo={"o": (-3, 0, 0), "p": (0, 0, 0.35)}, Glowa=(-8, 0, 0), Ogon1=(-4, 0, 0))
    _sekwencja(k, (0, 8, 11, 13, 18, 27), (spocz, zamach, wypad, traf, odbicie, spocz),
               wyg={1: "we", 2: "wy", 3: "s"})
    return k


def umiejetnosc(p, dl=54):
    """Kamienna skóra (1,8 s): przysiada, łeb chowa się pod kołnierz, przód i tył pancerza obracają się w dół wokół
    szwów (kl. 0–18), kl. 22 kula zamknięta — szwy świecą na grzbiecie (aura), kula kołysze się, rozwija się
    (kl. 38–54)."""
    k = p.klip("umiejetnosc", dl, petla=False)
    spocz = {}
    przysiad = _z(_lapy_poz(przod=(0.3, -0.75, 0.3), tyl=(0.3, -0.8, -0.2)), Cialo=(0, 0, 0), Glowa=(30, 0, 0),
                  Ogon1=(-25, 0, 0), _wolne=WOLNE)
    kula = _z(_lapy_poz(przod=(0.25, -0.2, -0.95), tyl=(0.25, -0.2, 0.95)),
              Cialo=(0, 0, 0), Przod=(78, 0, 0), Tyl=(-78, 0, 0), Glowa=(70, 0, 0), Szczeka=(0, 0, 0),
              Ogon1=(-70, 0, 0), Ogon2=(-40, 0, 0), _wolne=True)
    kula2 = _z(kula, Cialo=(-6, 0, 4))
    kula3 = _z(kula, Cialo=(6, 0, -4))
    _sekwencja(k, (0, 8, 18, 22, 28, 34, 40, 54), (spocz, przysiad, kula, kula, kula2, kula3, kula, spocz),
               wyg={1: "we", 2: "wy", 4: "s", 5: "s", 6: "we"})
    return k


def trafienie(p, dl=18):
    """Szarpnięcie w tył (0,6 s, najdalej kl. 4): ryj w górę, pancerz przechyla się, ogon podskakuje."""
    k = p.klip("trafienie", dl, petla=False)
    spocz = {}
    szarp = _z(Cialo={"o": (-8, 0, 4), "p": (0, 0, -0.35)}, Przod=(-6, 0, 0), Glowa=(-18, 0, 0), Szczeka=(10, 0, 0),
               Ogon1=(14, 0, 0), _wolne=WOLNE)
    odbicie = _z(Cialo={"o": (3, 0, -1), "p": (0, 0, -0.12)}, Glowa=(5, 0, 0), Ogon1=(-4, 0, 0))
    _sekwencja(k, (0, 4, 10, 18), (spocz, szarp, odbicie, spocz), wyg={0: "wy"})
    return k


def unik(p, dl=27):
    """Sus w lewo o 1,5 studa (najdalej kl. 12) i powrót (0,9 s): pancerz przechyla się, łapy podkulone w locie."""
    k = p.klip("unik", dl, petla=False)
    spocz = {}
    przys = _z(Cialo={"o": (0, 0, -6), "p": (0, 0, 0)}, _wolne=WOLNE)
    lot = _z(_lapy_poz(przod=(0.4, -0.6, 0.4), tyl=(0.4, -0.6, -0.4)), Cialo={"o": (0, 0, 14), "p": (0.8, 0, 0)},
             Ogon1=(0, 14, 0), _h=0.5, _wolne=True)
    lad = _z(Cialo={"o": (0, -10, 4), "p": (1.5, 0, 0)}, Glowa=(0, -14, 0), _wolne=WOLNE)
    lot2 = _z(lot, Cialo={"o": (0, 0, -10), "p": (0.75, 0, 0)}, Ogon1=(0, -12, 0), _h=0.35)
    _sekwencja(k, (0, 3, 8, 12, 16, 21, 27), (spocz, przys, lot, lad, lot2, przys, spocz),
               wyg={1: "wy", 2: "we", 4: "we"})
    return k


def upadek(p, dl=60):
    """Upadek (2 s): zatacza się, przechyla na prawy bok i przewraca na grzbiet — leży kopułą w dół, łapy w górze,
    ryj przekrzywiony (kl. 60 = leży)."""
    k = p.klip("upadek", dl, petla=False)
    spocz = {}
    chwiej = _z(Cialo={"o": (-6, 8, 8), "p": (0, 0, -0.2)}, Glowa=(-10, 14, 0), Szczeka=(10, 0, 0), _wolne=WOLNE)
    chwiej2 = _z(Cialo={"o": (4, -6, -10), "p": (0, 0, -0.1)}, Glowa=(12, -12, 0), _wolne=WOLNE)
    bok = _z(_lapy_poz(przod=(0.9, 0.0, 0.4), tyl=(0.9, 0.0, -0.4)),
             Cialo={"o": (0, -6, 95), "p": (0, 0, 0)}, Glowa=(10, 0, 20), Szczeka=(14, 0, 0), Ogon1=(0, 20, 0),
             _wolne=True)
    grzbiet = _z(_lapy_poz(przod=(0.5, 0.3, 0.6), tyl=(0.5, 0.3, -0.6), przodP=(-0.6, 0.6, 0.4),
                           tylP=(-0.6, 0.6, -0.4)),
                 Cialo={"o": (0, -8, 172), "p": (0, 0, 0)}, Glowa=(-20, 20, 0), Szczeka=(22, 0, 0),
                 Ogon1=(20, 10, 0), Ogon2=(10, 0, 0), _wolne=True)
    _sekwencja(k, (0, 10, 20, 34, 48, 60), (spocz, chwiej, chwiej2, bok, grzbiet, grzbiet),
               wyg={2: "we", 3: "s", 4: "l"})
    return k


def ryk(p, dl=60):
    """Ryk (dokładnie 60 klatek = 2,0 s, pętla): staje na tylnych łapach podparty ogonem, przednie łapy w górze,
    ryj uniesiony, paszcza otwarta, drży; wraca na cztery łapy."""
    k = p.klip("ryk", dl, petla=True)

    def poza(t):
        s = min(1.0, max(0.0, (t - 0.08) / 0.25)) * min(1.0, max(0.0, (0.95 - t) / 0.22))
        s = s * s * (3 - 2 * s)
        drz = math.sin(16 * math.pi * t) * s
        pz = _lapy_poz(przod=_mix(OS["LapaPL"], (0.5, 0.2, 0.85), s), tyl=_mix(OS["LapaTL"], (0.25, -0.9, 0.35), s))
        pz.update({"Cialo": {"o": (-40 * s + 1.5 * drz, 0, 1.0 * drz), "p": (0, 0, -0.5 * s)}, "Przod": (-6 * s, 0, 0),
                   "Glowa": (-24 * s + 2 * drz, 0, 0), "Szczeka": (30 * s, 0, 0),
                   "Ogon1": (40 * s, 0, 0), "Ogon2": (20 * s, 0, 0), "_wolne": ("DlonPL", "DlonPP")})
        return pz
    _petla(k, poza)
    return k


def _mix(a, b, s):
    a, b = _norm(a), _norm(b)
    return _norm(tuple(a[i] + (b[i] - a[i]) * s for i in range(3)))


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
