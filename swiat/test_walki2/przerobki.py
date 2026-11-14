# -*- coding: utf-8 -*-
"""Przeróbki modeli NA POTRZEBY PROTOTYPU WALKI v2 — tylko w pamięci, pliki modeli w swiat/postacie/ zostają bez zmian.

Każda funkcja dostaje gotową postać (Postac z modułu modelu) i dokłada to, czego aktorowi brakuje do walki:
- Rycerz (Wojownik): tarcza na lewym przedramieniu (Wojownik blokuje tylko tarczą) i klipy, których model nie ma:
  blok, unik, trafienie, upadek oraz trzy umiejętności (cięcie, miażdżący cios, kamienna skóra);
- Kot-Mag (Mag): zwykły atak kosturem, lodowy pocisk, bariera, trafienie, unik, upadek (kula ognia = istniejący „czar”);
- Zwiadowca: skupienie (jedyna umiejętność bez klipu w modelu);
- Leśny Slime (ZASTĘPCZY: slime-pet ×1,5, zielony): trafienie, unik, upadek;
- Strażnik Lasu (ZASTĘPCZY: Leśny Troll ×1,2, kamienne barwy, zielony kryształ w piersi).
Klipy zastępcze są szkicami (kilka póz kluczowych), oznaczone w tabeli aktorów polem „zastepcze_klipy”.

Konwencje biblioteki (swiat/postacie/biblioteka/README.md): postać patrzy w +Z, lewa strona +X; rx < 0 unosi rękę
do przodu, rz > 0 odchyla w stronę +X, ry > 0 skręca przód w stronę +X; przes w osiach modelu (mnożone przez skalę).
"""
from swiat.postacie.biblioteka.postac import Akcesorium


def _poza_z(baza, **zmiany):
    w = dict(baza)
    w.update(zmiany)
    return w


def _idle0(p, klip="idle"):
    """Poza z klatki 0 klipu spoczynku modelu: {kość: {"obrot": …, "przes": …}} — klipy zastępcze zaczynają się
    i kończą w niej, więc przejście z i do spoczynku jest płynne (broń zostaje w tym samym chwycie)."""
    k = next(k for k in p.klipy if k.nazwa == klip)
    poza = {}
    for (kosc, kanal) in k.kanaly:
        if kanal != "skala":
            poza.setdefault(kosc, {})[kanal] = tuple(round(v, 3) for v in k.wartosc(kosc, kanal, 0))
    return poza


# --------------------------------------------------------------------------- R15: wspólne klipy zastępcze
def _trafienie_r15(p, baza, dl=18, nazwa="trafienie"):
    """Odrzut po ciosie: tułów i głowa w tył, ręce na zewnątrz, krok w tył — i powrót."""
    k = p.klip(nazwa, dl, petla=False)
    zero = {"LowerTorso": {"obrot": (0, 0, 0), "przes": (0, 0, 0)}, "UpperTorso": (0, 0, 0), "Head": (0, 0, 0)}
    k.poza(0, _poza_z(baza, **zero))
    uderz = _poza_z(baza, LowerTorso={"obrot": (-6, 0, 4), "przes": (0, -0.05, -0.35)}, UpperTorso=(-16, 0, -5),
                    Head=(-20, 0, 8), LeftUpperArm=(-25, 0, 35), LeftLowerArm=(-35, 0, 0),
                    LeftUpperLeg=(-14, 0, 0), RightUpperLeg=(10, 0, 0), LeftLowerLeg=(12, 0, 0))
    k.poza(3, uderz)
    k.poza(7, _poza_z(uderz, UpperTorso=(-12, 0, -3), Head=(-14, 0, 5)))
    k.poza(dl, _poza_z(baza, **zero, LeftUpperLeg=(0, 0, 0), RightUpperLeg=(0, 0, 0), LeftLowerLeg=(0, 0, 0)))
    return k


def _unik_r15(p, baza, dl=24, nazwa="unik"):
    """Odskok w tył z odchyleniem tułowia (cios mija), lądowanie i powrót na miejsce."""
    k = p.klip(nazwa, dl, petla=False)
    zero = {"LowerTorso": {"obrot": (0, 0, 0), "przes": (0, 0, 0)}, "UpperTorso": (0, 0, 0), "Head": (0, 0, 0),
            "LeftUpperLeg": (0, 0, 0), "RightUpperLeg": (0, 0, 0), "LeftLowerLeg": (0, 0, 0), "RightLowerLeg": (0, 0, 0)}
    k.poza(0, _poza_z(baza, **zero))
    lot = _poza_z(baza, LowerTorso={"obrot": (-14, 18, 0), "przes": (0, 0.45, -1.3)}, UpperTorso=(-14, 10, 0),
                  Head=(6, -20, 0), LeftUpperLeg=(-35, 0, 0), LeftLowerLeg=(45, 0, 0),
                  RightUpperLeg=(-10, 0, 0), RightLowerLeg=(30, 0, 0))
    k.poza(5, lot)
    laduje = _poza_z(baza, LowerTorso={"obrot": (8, 14, 0), "przes": (0, -0.3, -1.5)}, UpperTorso=(8, 8, 0),
                     Head=(-4, -16, 0), LeftUpperLeg=(-30, 0, 0), LeftLowerLeg=(50, 0, 0),
                     RightUpperLeg=(-18, 0, 0), RightLowerLeg=(40, 0, 0))
    k.poza(10, laduje)
    k.poza(14, laduje)
    k.poza(dl, _poza_z(baza, **zero))
    return k


def _upadek_r15(p, baza, dl=40, nazwa="upadek", dlon_broni=(0, 0, 0), reka_broni=(-15, 0, -80), chwiejna=(-50, 0, -50),
                przedramie_broni=(-15, 0, 0)):
    """Upadek na plecy: zachwianie, ugięte kolana, przewrót w tył, odbicie i leżenie (ostatnia klatka = leżenie)."""
    k = p.klip(nazwa, dl, petla=False)
    hy = p.staw("LowerTorso")[1]                                 # wysokość bioder w spoczynku
    gl = p.wymiary("UpperTorso")[2] / 2.0                        # pół grubości tułowia: plecy leżą na ziemi
    k.poza(0, _poza_z(baza, LowerTorso={"obrot": (0, 0, 0), "przes": (0, 0, 0)}, UpperTorso=(0, 0, 0), Head=(0, 0, 0)))
    chwieje = _poza_z(baza, LowerTorso={"obrot": (-12, 0, 6), "przes": (0, -0.15 * hy, -0.3)}, UpperTorso=(-14, 0, -6),
                      Head=(-18, 0, 10), LeftUpperArm=(-40, 0, 50), RightUpperArm=chwiejna, RightLowerArm=przedramie_broni,
                      RightHand=dlon_broni,
                      LeftUpperLeg=(-25, 0, 0), RightUpperLeg=(-15, 0, 0), LeftLowerLeg=(35, 0, 0), RightLowerLeg=(25, 0, 0))
    k.poza(3, _poza_z(baza, RightHand=dlon_broni, RightLowerArm=przedramie_broni))  # najpierw nadgarstek, potem ręka
    k.poza(7, chwieje)
    lezy = _poza_z(baza, LowerTorso={"obrot": (-88, 0, 0), "przes": (0, -(hy - gl - 0.05), -0.4)},
                   UpperTorso=(-2, 0, 0), Head=(14, 0, 0),
                   LeftUpperArm=(-10, 0, 80), LeftLowerArm=(-10, 0, 0), RightUpperArm=reka_broni, RightLowerArm=przedramie_broni,
                   RightHand=dlon_broni,                         # broń leży wzdłuż wyciągniętej ręki, nie sterczy
                   LeftUpperLeg=(8, 0, 6), RightUpperLeg=(14, 0, -6), LeftLowerLeg=(6, 0, 0), RightLowerLeg=(4, 0, 0))
    k.poza(17, lezy)
    k.poza(21, _poza_z(lezy, LowerTorso={"obrot": (-80, 0, 0), "przes": (0, -(hy - gl - 0.25), -0.4)}, Head=(4, 0, 0)))
    k.poza(26, lezy)
    k.poza(dl, lezy)
    return k


# --------------------------------------------------------------------------- Rycerz (Wojownik)


def tarcza_rycerza():
    """Tarcza na zewnętrznej (lewej, +X) stronie przedramienia: lico zwrócone w +X, (0, 0, 0) = zaczep."""
    a = Akcesorium("rycerz_tarcza", "Tarcza Rycerza (dodatek prototypu)", zaczep="TarczaAttachment", typ="Bron")
    a.blok("Plyta", (0.06, 0.1, 0.0), (0.16, 1.5, 1.45), "niebieski", "matowy", faza=0.04)
    a.blok("Plyta dol", (0.06, -0.85, 0.0), (0.16, 0.5, 0.95), "niebieski", "matowy", faza=0.04)
    a.blok("Plyta czubek", (0.06, -1.15, 0.0), (0.16, 0.3, 0.45), "niebieski", "matowy", faza=0.04)
    for zn in (1, -1):
        a.blok("Rant bok", (0.1, 0.12, zn * 0.74), (0.2, 1.5, 0.12), "zloto", "metal", faza=0.03)
    a.blok("Rant gora", (0.1, 0.88, 0.0), (0.2, 0.14, 1.6), "zloto", "metal", faza=0.03)
    a.blok("Pas", (0.16, 0.15, 0.0), (0.08, 0.32, 1.42), "zloto", "metal", faza=0.0)
    a.blok("Pas pion", (0.16, -0.15, 0.0), (0.08, 1.6, 0.32), "zloto", "metal", faza=0.0)
    a.blok("Guz", (0.22, 0.15, 0.0), (0.14, 0.42, 0.42), "stal", "metal", faza=0.06)
    a.blok("Pas mocujacy", (-0.04, 0.0, 0.0), (0.08, 0.5, 1.0), "brazowy_ciemny", "matowy", faza=0.0)
    return a


def rycerz(p):
    p.zaczep("TarczaAttachment", "LeftLowerArm", (0.6, -0.42, 0.0))
    p.zaloz(tarcza_rycerza(), eksport=False)
    baza = _idle0(p)                                             # miecz w gotowości jak w idle
    _trafienie_r15(p, baza)
    _unik_r15(p, baza)
    _upadek_r15(p, baza, dlon_broni=(90, 0, 0))                 # nadgarstek 90°: klinga wzdłuż ręki

    # blok: lewy bark do przeciwnika, tarcza przed sobą, przysiad; uderzenie w tarczę spycha o krok
    k = p.klip("blok", 26, petla=False)
    zero = {"LowerTorso": {"obrot": (0, 0, 0), "przes": (0, 0, 0)}, "UpperTorso": (0, 0, 0), "Head": (0, 0, 0),
            "LeftUpperLeg": (0, 0, 0), "RightUpperLeg": (0, 0, 0), "LeftLowerLeg": (0, 0, 0), "RightLowerLeg": (0, 0, 0)}
    k.poza(0, _poza_z(baza, **zero))
    garda = {"LowerTorso": {"obrot": (0, -38, 0), "przes": (0, -0.22, 0)}, "UpperTorso": (8, -6, 0), "Head": (-4, 40, 0),
             "LeftUpperArm": (-62, 0, 30), "LeftLowerArm": (-64, 0, 0), "LeftHand": (0, 0, 0),
             "RightUpperArm": (-30, 0, -30), "RightLowerArm": (-70, 0, 0),
             "LeftUpperLeg": (-26, 0, 6), "LeftLowerLeg": (30, 0, 0), "RightUpperLeg": (14, 0, -6), "RightLowerLeg": (22, 0, 0)}
    k.poza(5, garda)
    k.poza(8, _poza_z(garda, LowerTorso={"obrot": (-4, -38, 0), "przes": (0, -0.28, -0.45)}, UpperTorso=(0, -6, 0)))
    k.poza(17, _poza_z(garda, LowerTorso={"obrot": (0, -38, 0), "przes": (0, -0.22, -0.4)}))
    k.poza(26, _poza_z(baza, **zero))

    # potężne cięcie: zamach (skręt w lewo, miecz na wyciągniętej w bok ręce, klinga wzdłuż ręki), obrót o pełne koło
    # w prawo — klinga zatacza poziomy krąg na wysokości barku — i powrót do gardy
    k = p.klip("ciecie", 42, petla=False)
    ramie = {"RightUpperArm": (0, 0, -88), "RightLowerArm": (0, 0, 0), "RightHand": (90, 0, 0),
             "LeftUpperArm": (-30, 0, 45), "LeftLowerArm": (-50, 0, 0)}
    k.poza(0, _poza_z(baza, LowerTorso={"obrot": (0, 0, 0), "przes": (0, 0, 0)}, UpperTorso=(0, 0, 0)))
    k.poza(10, _poza_z(baza, LowerTorso={"obrot": (0, 50, 0), "przes": (0, -0.3, 0)}, UpperTorso=(4, 25, 0), **ramie))
    k.poza(16, _poza_z(baza, LowerTorso={"obrot": (0, -60, 0), "przes": (0, -0.3, 0.2)}, UpperTorso=(4, -10, 0), **ramie),
           wyg="liniowo")
    k.poza(22, _poza_z(baza, LowerTorso={"obrot": (0, -200, 0), "przes": (0, -0.25, 0.3)}, UpperTorso=(4, -15, 0), **ramie),
           wyg="liniowo")
    k.poza(28, _poza_z(baza, LowerTorso={"obrot": (0, -330, 0), "przes": (0, -0.3, 0.3)}, UpperTorso=(8, -10, 0), **ramie))
    k.poza(42, _poza_z(baza, LowerTorso={"obrot": (0, -360, 0), "przes": (0, 0, 0)}, UpperTorso=(0, 0, 0)))

    # miażdżący cios: przysiad, wyskok z mieczem nad głową, uderzenie w ziemię przed sobą, powrót
    k = p.klip("miazdzacy_cios", 46, petla=False)
    nogi0 = {"LeftUpperLeg": (0, 0, 0), "RightUpperLeg": (0, 0, 0), "LeftLowerLeg": (0, 0, 0), "RightLowerLeg": (0, 0, 0)}
    k.poza(0, _poza_z(baza, LowerTorso={"obrot": (0, 0, 0), "przes": (0, 0, 0)}, UpperTorso=(0, 0, 0), **nogi0))
    przysiad = _poza_z(baza, LowerTorso={"obrot": (10, 0, 0), "przes": (0, -0.55, 0)}, UpperTorso=(14, 0, 0),
                       RightUpperArm=(-150, 0, -30), RightLowerArm=(-40, 0, 0), RightHand=(40, 0, 0),
                       LeftUpperArm=(-150, 0, 30), LeftLowerArm=(-40, 0, 0),
                       LeftUpperLeg=(-50, 0, 0), RightUpperLeg=(-50, 0, 0), LeftLowerLeg=(80, 0, 0), RightLowerLeg=(80, 0, 0))
    k.poza(9, przysiad)
    k.poza(17, _poza_z(przysiad, LowerTorso={"obrot": (-12, 0, 0), "przes": (0, 1.4, 0.8)}, UpperTorso=(-14, 0, 0),
                       RightUpperArm=(-175, 0, -15), RightLowerArm=(-25, 0, 0), RightHand=(30, 0, 0),
                       LeftUpperArm=(-175, 0, 15), LeftLowerArm=(-25, 0, 0),
                       LeftUpperLeg=(-30, 0, 0), RightUpperLeg=(-10, 0, 0), LeftLowerLeg=(50, 0, 0), RightLowerLeg=(30, 0, 0)))
    uderz = _poza_z(przysiad, LowerTorso={"obrot": (22, 0, 0), "przes": (0, -0.5, 1.3)}, UpperTorso=(24, 0, 0),
                    RightUpperArm=(-55, 0, 5), RightLowerArm=(-5, 0, 0), RightHand=(75, 0, 0),
                    LeftUpperArm=(-55, 0, 20), LeftLowerArm=(-10, 0, 0), Head=(-10, 0, 0))
    k.poza(22, uderz, wyg="liniowo")
    k.poza(30, uderz)
    k.poza(46, _poza_z(baza, LowerTorso={"obrot": (0, 0, 0), "przes": (0, 0, 0)}, UpperTorso=(0, 0, 0), Head=(0, 0, 0),
                       **nogi0))

    # kamienna skóra: szeroki rozkrok, napięte ręce, drżenie z wysiłku, powrót
    k = p.klip("kamienna_skora", 44, petla=False)
    k.poza(0, _poza_z(baza, LowerTorso={"obrot": (0, 0, 0), "przes": (0, 0, 0)}, UpperTorso=(0, 0, 0), Head=(0, 0, 0), **nogi0))
    napiecie = _poza_z(baza, LowerTorso={"obrot": (0, 0, 0), "przes": (0, -0.35, 0)}, UpperTorso=(10, 0, 0), Head=(10, 0, 0),
                       LeftUpperArm=(-20, 0, 55), LeftLowerArm=(-95, 0, 0),   # miecz zostaje w chwycie z idle
                       LeftUpperLeg=(-12, 0, 20), RightUpperLeg=(-12, 0, -20), LeftLowerLeg=(24, 0, 0), RightLowerLeg=(24, 0, 0))
    k.poza(10, napiecie)
    for f, d in ((14, 3), (18, -3), (22, 3), (26, -3), (30, 3)):
        k.poza(f, _poza_z(napiecie, UpperTorso=(10 + d, 0, d * 0.5), Head=(10 - d, 0, 0)))
    k.poza(34, napiecie)
    k.poza(44, _poza_z(baza, LowerTorso={"obrot": (0, 0, 0), "przes": (0, 0, 0)}, UpperTorso=(0, 0, 0), Head=(0, 0, 0),
                       **nogi0))


# --------------------------------------------------------------------------- Kot-Mag (Mag)
# Kostur jest założony na chwyt obrócony o −90° w X: przy wyprostowanej ręce i nadgarstku 0 drzewce idzie WZDŁUŻ
# ręki do tyłu (w głowę przy uniesionej ręce). Nadgarstek 180° kieruje kryształ wzdłuż ręki do przodu, 130° przy
# zgiętym łokciu stawia kostur pionowo nad łapą (pozy dobrane liczbowo testem przenikania — testy/test_aktorow.py).
def kot_mag(p):
    BAZA_KOT = _idle0(p)
    _trafienie_r15(p, BAZA_KOT)
    _unik_r15(p, BAZA_KOT)
    _upadek_r15(p, BAZA_KOT, dlon_broni=(90, 0, 0), reka_broni=(-30, 0, -60), chwiejna=(-20, 0, -60),
                przedramie_broni=(-30, 0, 0))
    zero = {"LowerTorso": {"obrot": (0, 0, 0), "przes": (0, 0, 0)}, "UpperTorso": (0, 0, 0), "Head": (0, 0, 0)}

    # zwykły atak: pchnięcie kosturem — kryształ celuje w przeciwnika
    k = p.klip("atak", 30, petla=False)
    k.poza(0, _poza_z(BAZA_KOT, **zero), wyg="liniowo")              # liniowo: krzywa gładka przerzucała kostur przez głowę
    k.poza(8, _poza_z(BAZA_KOT, LowerTorso={"obrot": (0, 20, 0), "przes": (0, -0.04, -0.1)}, UpperTorso=(-8, 15, 0),
                      RightUpperArm=(-50, 0, -20), RightLowerArm=(-60, 0, 0), RightHand=(130, 0, 0), Tail=(30, 0, 0)))
    pchniecie = _poza_z(BAZA_KOT, LowerTorso={"obrot": (6, -15, 0), "przes": (0, -0.03, 0.25)}, UpperTorso=(10, -15, 0),
                        RightUpperArm=(-90, 0, -10), RightLowerArm=(0, 0, 0), RightHand=(180, 0, 0),
                        LeftUpperArm=(10, 0, 30), Head=(-6, 10, 0), Tail=(-10, 0, 0))
    k.poza(13, pchniecie, wyg="liniowo")
    k.poza(18, pchniecie)
    k.poza(24, _poza_z(BAZA_KOT, RightUpperArm=(-50, 0, -20), RightLowerArm=(-60, 0, 0), RightHand=(130, 0, 0)),
           wyg="liniowo")  # kostur wraca pionowo, nie przez głowę
    k.poza(30, _poza_z(BAZA_KOT, **zero))

    # lodowy pocisk: obie łapy wypychają kostur przed siebie, mocny wykrok
    k = p.klip("lodowy_pocisk", 40, petla=False)
    k.poza(0, _poza_z(BAZA_KOT, **zero), wyg="liniowo")
    k.poza(12, _poza_z(BAZA_KOT, LowerTorso={"obrot": (-6, 0, 0), "przes": (0, -0.05, -0.15)}, UpperTorso=(-12, 0, 0),
                       RightUpperArm=(-50, 0, -20), RightLowerArm=(-60, 0, 0), RightHand=(130, 0, 0),
                       LeftUpperArm=(-60, 0, 40), LeftLowerArm=(-70, 0, 0), Head=(-10, 0, 0), Tail=(40, 0, 0)))
    wypych = _poza_z(BAZA_KOT, LowerTorso={"obrot": (8, 0, 0), "przes": (0, -0.06, 0.35)}, UpperTorso=(14, 0, 0),
                     RightUpperArm=(-90, 0, -10), RightLowerArm=(0, 0, 0), RightHand=(180, 0, 0),
                     LeftUpperArm=(-88, 0, 12), LeftLowerArm=(-2, 0, 0), Head=(-12, 0, 0), Tail=(-15, 0, 0))
    k.poza(18, wypych, wyg="liniowo")
    k.poza(28, wypych)
    k.poza(40, _poza_z(BAZA_KOT, **zero))

    # kula ognia: kostur wysoko w górę (kula rośnie nad kryształem), potrząśnięcia, pchnięcie w przeciwnika, powrót.
    # Zastępuje klip modelu „czar”, w którym kostur przechodzi przez głowę kota (test przenikania).
    k = p.klip("kula_ognia", 54, petla=False)
    w_gorze = _poza_z(BAZA_KOT, LowerTorso={"obrot": (-4, 0, 0), "przes": (0, 0.05, -0.1)}, UpperTorso=(-10, 0, 0),
                      RightUpperArm=(-120, 0, -30), RightLowerArm=(-20, 0, 0), RightHand=(130, 0, 0),
                      LeftUpperArm=(-40, 0, 60), LeftLowerArm=(-30, 0, 0), Head=(-12, 0, 0), Tail=(35, 0, 0))
    k.poza(0, _poza_z(BAZA_KOT, **zero), wyg="liniowo")
    k.poza(4, _poza_z(BAZA_KOT, **zero, RightHand=(130, 0, 0)), wyg="liniowo")
    k.poza(12, w_gorze)
    for f, d in ((16, 6), (20, -6), (24, 6), (28, -6)):
        k.poza(f, _poza_z(w_gorze, RightHand=(130 + d, 0, 0)))
    k.poza(32, w_gorze, wyg="liniowo")
    rzut = _poza_z(BAZA_KOT, LowerTorso={"obrot": (8, 0, 0), "przes": (0, -0.05, 0.3)}, UpperTorso=(12, 0, 0),
                   RightUpperArm=(-90, 0, -10), RightLowerArm=(0, 0, 0), RightHand=(180, 0, 0),
                   LeftUpperArm=(10, 0, 40), Head=(-8, 0, 0), Tail=(-15, 0, 0))
    k.poza(37, rzut)
    k.poza(42, rzut)
    k.poza(48, _poza_z(BAZA_KOT, RightUpperArm=(-50, 0, -20), RightLowerArm=(-60, 0, 0), RightHand=(130, 0, 0)), wyg="liniowo")
    k.poza(54, _poza_z(BAZA_KOT, **zero))

    # radość: podskoki z kosturem pionowo nad łapą (zastępuje „wiwat” modelu — tam kostur wchodzi w głowę)
    k = p.klip("radosc", 30, petla=True)
    dol = _poza_z(BAZA_KOT, LowerTorso={"obrot": (0, 0, 0), "przes": (0, -0.08, 0)},
                  LeftUpperLeg=(-16, 0, 0), RightUpperLeg=(-16, 0, 0), LeftLowerLeg=(32, 0, 0), RightLowerLeg=(32, 0, 0),
                  UpperTorso=(8, 0, 0), Head=(5, 0, 0), LeftUpperArm=(-10, 0, 20), LeftLowerArm=(-20, 0, 0),
                  RightUpperArm=(-50, 0, -20), RightLowerArm=(-60, 0, 0), RightHand=(130, 0, 0), Tail=(5, 0, 0))
    gora = _poza_z(dol, LowerTorso={"obrot": (0, 0, 0), "przes": (0, 0.7, 0)},
                   LeftUpperLeg=(-12, 0, 6), RightUpperLeg=(-12, 0, -6), LeftLowerLeg=(30, 0, 0), RightLowerLeg=(30, 0, 0),
                   UpperTorso=(-8, 0, 0), Head=(-12, 0, 0), LeftUpperArm=(-15, 0, 150), LeftLowerArm=(0, 0, 0),
                   RightUpperArm=(-110, 0, -30), RightLowerArm=(-20, 0, 0), RightHand=(130, 0, 0), Tail=(40, 0, 0))
    k.poza(0, dol)
    k.poza(10, gora)
    k.poza(15, gora)
    k.poza(30, dol)

    # bariera: kostur pionowo przed sobą, lewa łapa wyciągnięta dłonią do przodu, przysiad
    k = p.klip("bariera", 40, petla=False)
    k.poza(0, _poza_z(BAZA_KOT, **zero))
    oslona = _poza_z(BAZA_KOT, LowerTorso={"obrot": (0, 0, 0), "przes": (0, -0.08, 0)}, UpperTorso=(4, 0, 0),
                     RightUpperArm=(-50, 0, -20), RightLowerArm=(-60, 0, 0), RightHand=(130, 0, 0),
                     LeftUpperArm=(-85, 0, 25), LeftLowerArm=(-20, 0, 0), Head=(-8, 0, 0), Tail=(35, 0, 0))
    k.poza(10, oslona)
    k.poza(30, _poza_z(oslona, Head=(-4, 0, 0)))
    k.poza(40, _poza_z(BAZA_KOT, **zero))


# --------------------------------------------------------------------------- Zwiadowca
def zwiadowca(p):
    # skupienie: przyklęk, łuk pionowo przed twarzą, głowa pochylona — chwila skupienia i powrót
    baza = _idle0(p)
    zero = {"LowerTorso": {"obrot": (0, 0, 0), "przes": (0, 0, 0)}, "UpperTorso": (0, 0, 0), "Head": (0, 0, 0),
            "LeftUpperLeg": (0, 0, 0), "LeftLowerLeg": (0, 0, 0), "RightUpperLeg": (0, 0, 0), "RightLowerLeg": (0, 0, 0)}
    start = dict(zero, **baza)
    k = p.klip("skupienie", 44, petla=False)
    k.poza(0, start)
    skup = {"LowerTorso": {"obrot": (0, 0, 0), "przes": (0, -0.45, 0)}, "UpperTorso": (12, 0, 0), "Head": (22, 0, 0),
            "LeftUpperArm": (-70, 0, -25), "LeftLowerArm": (-70, 0, 0), "LeftHand": (0, 0, 0),
            "RightUpperArm": (-40, 0, 30), "RightLowerArm": (-60, 0, 0),
            "LeftUpperLeg": (-60, 0, 0), "LeftLowerLeg": (70, 0, 0), "RightUpperLeg": (10, 0, 0), "RightLowerLeg": (70, 0, 0)}
    k.poza(10, skup)
    k.poza(32, _poza_z(skup, Head=(16, 0, 0), UpperTorso=(8, 0, 0)))
    k.poza(44, start)


# --------------------------------------------------------------------------- Leśny Slime (zastępczy: slime-pet)
def lesny_slime(p):
    p.skala = 1.5
    # trafienie: galareta odskakuje w tył i przechyla się
    k = p.klip("trafienie", 16, petla=False)
    k.klucz(0, "Cialo", przes=(0, 0, 0), obrot=(0, 0, 0))
    k.klucz(3, "Cialo", przes=(0, 0.25, -0.55), obrot=(-16, 0, 6))
    k.klucz(8, "Cialo", przes=(0, 0, -0.45), obrot=(4, 0, -2))
    k.klucz(16, "Cialo", przes=(0, 0, 0), obrot=(0, 0, 0))
    # unik: podskok w bok i powrót
    k = p.klip("unik", 22, petla=False)
    k.klucz(0, "Cialo", przes=(0, 0, 0), obrot=(0, 0, 0))
    k.klucz(6, "Cialo", przes=(1.1, 0.9, -0.4), obrot=(0, 0, 16))
    k.klucz(11, "Cialo", przes=(1.4, 0, -0.5), obrot=(0, 0, 0))
    k.klucz(14, "Cialo", przes=(1.4, 0, -0.5), obrot=(0, 0, 0))
    k.klucz(22, "Cialo", przes=(0, 0, 0), obrot=(0, 0, 0))
    # upadek: przewraca się na plecy (oczy do góry) i zostaje
    k = p.klip("upadek", 30, petla=False)
    k.klucz(0, "Cialo", przes=(0, 0, 0), obrot=(0, 0, 0))
    k.klucz(6, "Cialo", przes=(0, 0.35, -0.2), obrot=(-25, 0, 8))
    k.klucz(14, "Cialo", przes=(0, 1.175, -0.1), obrot=(-90, 0, 0))
    k.klucz(18, "Cialo", przes=(0, 1.4, -0.1), obrot=(-84, 0, 0))
    k.klucz(22, "Cialo", przes=(0, 1.175, -0.1), obrot=(-90, 0, 0))
    k.klucz(30, "Cialo", przes=(0, 1.175, -0.1), obrot=(-90, 0, 0))


# --------------------------------------------------------------------------- Strażnik Lasu (zastępczy: troll)
def straznik_lasu(p):
    p.skala = 1.2
    a = Akcesorium("straznik_krysztal", "Kryształ Strażnika (dodatek prototypu)", zaczep="PiersAttachment", typ="Bron")
    a.blok("Krysztal", (0, 0, 0.15), (1.0, 1.0, 0.5), "52F07A", "swiecacy", rot=(0, 0, 45), faza=0.05)
    a.blok("Oprawa", (0, 0, -0.05), (1.45, 1.45, 0.4), "5D636B", "matowy", rot=(0, 0, 45), faza=0.05)
    # przód tułowia trolla na wysokości piersi: ok. 3,1 studa przed stawem Tulow (zmierzone z danych rigu)
    p.zaczep("PiersAttachment", "Tulow", (0, 2.2, 3.05))
    p.zaloz(a, eksport=False)


PRZEROBKI = {"rycerz": rycerz, "kot_mag": kot_mag, "zwiadowca": zwiadowca, "lesny_slime": lesny_slime,
             "straznik_lasu": straznik_lasu}
