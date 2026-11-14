# -*- coding: utf-8 -*-
"""CIERNIOWY WILK — zwykły, szybki przeciwnik lasu (ok. 3 study w kłębie; pies-pet ma 2,2, gracz 5,7).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/cierniowy_wilk.py --wyj <folder> --klip atak

Opis z danych walki (tools/walka/dane_walki.json, id „cierniowy_wilk”): chudy, kanciasty wilk o futrze z ciemnej
sierści przetykanej kolcami jeżyny, z bursztynowymi świecącymi oczami i ogonem jak zarośla. Umiejętność:
rozszarpanie — skok z dwoma szybkimi kłapnięciami paszczy.

Sylwetka (rozpoznawalna po samym kształcie): długie, cienkie łapy; głęboka klatka piersiowa i wcięta talia; głowa
nisko, na wysokości kłębu, wysunięta do przodu; długi pysk z kłami na zewnątrz; wysokie, spiczaste uszy; zjeżona
grzywa na karku; grzbiet najeżony jasnymi kolcami jeżyny; ogon trzymany poziomo, zakończony gęstwiną pędów.
Twarz: ciężkie brwi w „V”, świecące bursztynowe oczy z pionową źrenicą (jedyny mocny akcent koloru). Głowa jest
przerysowana (cała powiększona 1,2× wokół stawu szyi — SKALA_GLOWY), tak jak duże głowy innych postaci gry.

Paleta (7 rodzin): futro łupkowo-granatowe w trzech odcieniach, pędy jeżyny (dwie zielenie), kolce (jasne drewno),
kość (kły, pazury), tusz (nos, źrenice, wargi), wnętrze paszczy z językiem; AKCENT: świecący bursztyn oczu.

Szkielet (własny, typ „stwor” — wzór: pies.py). L = lewa = +X, P = prawa = −X:
    Root > Zad > {Klatka > {Glowa > {Szczeka, UchoL, UchoP, Powieki},
                            LapaPrzodL/P_Gora > _Dol > _Stopa},
                  LapaTylL/P_Gora > _Dol > _Stopa, Ogon > OgonKoniec}
- `Zad` (biodra i talia) jest korzeniem ciała: jego przesunięcie i obrót niosą całego wilka (skok, unik, upadek);
- `Klatka` (pierś i barki) zgina grzbiet względem zadu (galop, przysiad);
- `Stopa` w każdej łapie trzyma łapę płasko na ziemi (liczone w module, jak stopy Leśnego Trolla);
- `Powieki` chowają się w czaszce; mrugnięcie w idle, zamknięte oczy po upadku.

Klipy (30 kl./s; wilk patrzy w +Z i w tę stronę atakuje):
  idle (pętla 2,4 s), ruch (galop, pętla 0,53 s), atak (ugryzienie z wypadu, 0,9 s, trafienie w kl. 13),
  umiejetnosc (rozszarpanie: przysiad, skok, dwa kłapnięcia w locie w kl. 17 i 23, lądowanie z szarpaniem
  głową, odskok na miejsce, 1,8 s), trafienie (szarpnięcie w tył, 0,6 s), unik (odskok w lewo i powrót, 0,93 s),
  upadek (chwieje się, przednie łapy się uginają, przewraca się na prawy bok i leży z zamkniętymi oczami, 1,9 s),
  ryk (wycie po wygranej: łeb do góry, otwarta paszcza; pętla 2 s).
Klipy są zapisane jako pozy kluczowe (_sekwencja) zamienione na klucz w każdej klatce: łapy, które w pozie „stoją”
(("z", dz, h)), są dociągane do ziemi odwrotną kinematyką (dwa ogniwa w płaszczyźnie łapy), a ciało nigdy nie
schodzi pod ziemię. Zmiany rób w pozach kluczowych w tym pliku, nie w Blenderze.
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Postac, katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor

ID = "cierniowy_wilk"

PALETA = {
    "futro": "4A5068", "futro_ciemne": "2A2E40", "futro_jasne": "8A92AA",
    "pnacze": "5C8A3A", "pnacze_ciemne": "3A5C2A",
    "kolec": "E8D4A2",
    "kosc": "F4EEDC",
    "tusz": "16141E",
    "gardlo": "7A1F33", "jezyk": "C94A66",
    "bursztyn": "F26A0C",          # z emisją w renderze wychodzi jasny bursztyn (FFB21F wychodził cytrynowo-żółty)
}

# ----------------------------------------------------------------------------------------------- szkielet (studs)
ZAD = (0.0, 2.42, -0.4)            # staw zadu = środek ciała (obrót całego wilka)
KLATKA = (0.0, 2.48, 0.05)         # staw klatki = talia (zgięcie grzbietu)
GLOWA = (0.0, 2.8, 1.45)           # staw szyi
SKALA_GLOWY = 1.2                  # cała głowa (z żuchwą, uszami i powiekami) powiększona wokół stawu szyi


def _gl(pt):
    """Punkt głowy podany w wymiarach „naturalnych” -> po powiększeniu głowy wokół stawu szyi."""
    return tuple(GLOWA[i] + SKALA_GLOWY * (pt[i] - GLOWA[i]) for i in range(3))


SZCZEKA = _gl((0.0, 2.8, 2.3))     # zawias żuchwy
UCHO_L = _gl((0.3, 3.5, 1.98))
POWIEKI = _gl((0.0, 3.33, 2.6))
OGON = (0.0, 2.72, -1.72)
OGON_KAT = -100.0                  # ogon trzymany prawie poziomo (oś ogona = +Y obrócone o rx)
OGON_DL = 0.5
X_LAP = 0.4
# łapa przednia: bark, łokieć, nadgarstek (staw stopy); tylna: biodro, kolano, staw skokowy niżej (staw stopy)
PRZOD = {"bark": (2.25, 1.0), "lokiec": (1.2, 1.0), "stopa": (0.42, 1.02)}            # (y, z)
TYL = {"biodro": (2.35, -1.3), "kolano": (1.4, -1.0), "stopa": (0.3, -1.42)}
NOGI = {"PL": ("LapaPrzodL", "Klatka", 1.0), "PP": ("LapaPrzodP", "Klatka", -1.0),
        "TL": ("LapaTylL", "Zad", 1.0), "TP": ("LapaTylP", "Zad", -1.0)}


def _ogon_koniec():
    a = math.radians(OGON_KAT)
    return (0.0, OGON[1] + math.cos(a) * OGON_DL, OGON[2] + math.sin(a) * OGON_DL)


def _model(p, kosc, obrot=(0, 0, 0), pos=(0, 0, 0)):
    """Układ MODELU (0, 0, 0 = ziemia pod środkiem) na kości: bryły podaje się we współrzędnych modelu."""
    s = p.staw(kosc)
    return p.na(kosc, pos=(pos[0] - s[0], pos[1] - s[1], pos[2] - s[2]), obrot=obrot)


class _ModelGlowy:
    """Jak _model, ale bryły podane w wymiarach „naturalnych” głowy są powiększane (SKALA_GLOWY) wokół szyi."""

    def __init__(self, p, kosc):
        self.p, self.kosc, self.stos = p, kosc, []

    def __enter__(self):
        p = self.p
        for cm in (_model(p, self.kosc), p.uklad(pos=GLOWA, skala=SKALA_GLOWY),
                   p.uklad(pos=(-GLOWA[0], -GLOWA[1], -GLOWA[2]))):
            cm.__enter__()
            self.stos.append(cm)
        return p

    def __exit__(self, *a):
        while self.stos:
            self.stos.pop().__exit__(*a)
        return False


def zbuduj():
    p = Postac(ID, "Cierniowy Wilk", typ="stwor", skala=1.0, faza=0.05, paleta=PALETA)

    # ------------------------------------------------------------------ szkielet
    p.kosc("Zad", "Root", staw=ZAD, dl=0.6)
    p.kosc("Klatka", "Zad", staw=KLATKA, dl=0.6)
    p.kosc("Glowa", "Klatka", staw=GLOWA, czesc=(1.05, 0.85, 0.95), srodek=(0, 0.35, 0.7))
    p.kosc("Szczeka", "Glowa", staw=SZCZEKA, dl=0.3)
    p.kosc("UchoL", "Glowa", staw=UCHO_L, dl=0.3)
    p.kosc("UchoP", "Glowa", staw=(-UCHO_L[0], UCHO_L[1], UCHO_L[2]), dl=0.3)
    p.kosc("Powieki", "Glowa", staw=POWIEKI, dl=0.2)
    for s, zn in (("L", 1.0), ("P", -1.0)):
        x = zn * X_LAP
        g, d, st = "LapaPrzod%s_Gora" % s, "LapaPrzod%s_Dol" % s, "LapaPrzod%s_Stopa" % s
        p.kosc(g, "Klatka", staw=(x,) + PRZOD["bark"], dl=0.6)
        p.kosc(d, g, staw=(x,) + PRZOD["lokiec"], dl=0.5)
        p.kosc(st, d, staw=(x,) + PRZOD["stopa"], dl=0.25)
        g, d, st = "LapaTyl%s_Gora" % s, "LapaTyl%s_Dol" % s, "LapaTyl%s_Stopa" % s
        p.kosc(g, "Zad", staw=(x,) + TYL["biodro"], dl=0.6)
        p.kosc(d, g, staw=(x,) + TYL["kolano"], dl=0.5)
        p.kosc(st, d, staw=(x,) + TYL["stopa"], dl=0.25)
    p.kosc("Ogon", "Zad", staw=OGON, dl=0.5)
    p.kosc("OgonKoniec", "Ogon", staw=_ogon_koniec(), dl=0.5)

    _tulow(p)
    _glowa(p)
    _lapy(p)
    _ogon(p)

    # punkty zaczepienia dla gry: korzeń, tabliczka nad głową, pysk (efekt ugryzienia / krwawienia)
    p.zaczep("RootAttachment", "Zad", (-ZAD[0], -ZAD[1], -ZAD[2]))
    p.zaczep("GlowaAttachment", "Glowa", (0, 1.4, 0.85))
    p.zaczep("PyskAttachment", "Glowa", (0, 0.0, 2.3))

    _klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return p


SLABOSCI = [
    "Kości wilka nie są R15 (własny szkielet: Root + 21 kości, jak u petów) — klipy importuje się na własny rig; "
    "import do Roblox Studio nie był testowany.",
    "Bryły są sztywno przypięte do kości (jedna siatka na kość): górne części łap i nasady uszu siedzą w tułowiu "
    "i czaszce (celowo), a przy mocnym zgięciu grzbietu pierś i talia lekko się przenikają.",
    "Galop jest w miejscu (łapa w podporze sunie po ziemi); faza lotu jest krótka i niska, a przednia łapa przy "
    "pełnym wykroku jest prawie wyprostowana (dłuższego kroku ten szkielet nie da). "
    "W ataku, umiejętności i trafieniu stojące łapy przesuwają się po ziemi przy powrocie na miejsce.",
    "Rozszarpanie przesuwa wilka o 2,4 studa do przodu i odskokiem wraca na miejsce — w grze trzeba zgrać to "
    "z odległością od celu (albo przesuwać model skryptem i skrócić odskok).",
    "Świecenie oczu jest tylko w teksturze-palecie (emisja) — w grze trzeba je dać materiałem Neon albo "
    "PointLight; krwawienia, śladów pazurów i kurzu nie ma (dorobić efektem na PyskAttachment).",
    "Kolce jeżyny i pędy (także gęstwina ogona) są sztywnymi bryłami — nie kołyszą się w biegu; ogon rusza się "
    "tylko dwiema kośćmi.",
    "Powieki przy mrugnięciu na 1–2 klatki wysuwają się z czaszki przez twarz (szybko, z daleka nie widać).",
    "Kolizje sprawdzane w przybliżeniu (punkty skrzynek brył w każdej klatce, wartości kluczy liniowo): dolne "
    "części łap, łapy i koniec ogona nie wchodzą w głowę ani tułów; czaszka, kufa i żuchwa nie wchodzą w tułów. "
    "Kolce i pędy na tułowiu nie były sprawdzane. Po przeglądzie (dłuższy wypad w ataku, szerszy galop, "
    "opadające łapy w leżeniu) przenikanie sprawdzono tylko na renderach z dwóch stron, nie liczbowo.",
    "Obrys renderu (odwrócona otoczka) przy ostrym bocznym spojrzeniu nadal rysuje cienką pionową kreskę przy "
    "dalszym oku — to efekt podglądu, w grze obrysu nie ma.",
    "Klipy to szkice (0,5–1,9 s), nie gotowa animacja; mimika tylko z żuchwy, uszu i powiek.",
]


# ---------------------------------------------------------------------------------------------------- pomocnicze
def _kolec(p, nazwa, pos, dl, rot, gr=0.16, kolor="kolec"):
    """Kolec jeżyny: czworoboczny szpic (podstawa w pos, szpic w kierunku +Y obróconym o rot)."""
    with p.uklad(pos=pos, obrot=rot):
        p.ostroslup(nazwa, (0, dl / 2, 0), (gr, dl, gr), kolor, "polysk", gora=(0.0, 0.0))


def _kepka(p, nazwa, pos, dl, rot, gr=(0.26, 0.14), kolor="futro_ciemne"):
    """Kępka zjeżonej sierści: płaski szpic."""
    with p.uklad(pos=pos, obrot=rot):
        p.ostroslup(nazwa, (0, dl / 2, 0), (gr[0], dl, gr[1]), kolor, "matowy", gora=(0.0, 0.0))


def _pnacze(p, nazwa, z, y0, y1, szer, rz=0.0, kolce=()):
    """Pęd jeżyny owinięty wokół klocka tułowia (wierzch + dwa boki, ukośnie), z kolcami na zewnątrz.
    y0..y1 = dół i góra klocka, szer = jego szerokość, z = środek opaski."""
    h = y1 - y0
    with p.uklad(pos=(0, 0, z), obrot=(0, 0, 0)):
        p.blok(nazwa + " wierzch", (0, y1 + 0.03, 0), (szer + 0.04, 0.07, 0.1), "pnacze", "matowy", faza=0.02,
               rot=(0, 20, 0))
        for zn in (1, -1):
            # na boku pęd idzie zygzakiem: w dół i do tyłu, potem w dół i do przodu (jak pnącze, nie pasek)
            p.blok(nazwa + " bok gora", (zn * (szer / 2 + 0.025), y1 - h * 0.25, zn * 0.13), (0.07, h * 0.55, 0.1),
                   "pnacze", "matowy", faza=0.02, rot=(zn * 28, 0, 0))
            p.blok(nazwa + " bok dol", (zn * (szer / 2 + 0.025), y0 + h * 0.3, zn * 0.12), (0.07, h * 0.5, 0.1),
                   "pnacze", "matowy", faza=0.02, rot=(-zn * 24, 0, 0))
            with p.uklad(pos=(zn * (szer / 2 + 0.05), y0 + h * 0.52, zn * 0.26), obrot=(0, 0, -zn * 70)):
                p.ostroslup(nazwa + " lisc", (0, 0.12, 0), (0.2, 0.24, 0.04), "pnacze_ciemne", "matowy",
                            gora=(0.0, 0.0))
        for i, (x, y, rot, dl) in enumerate(kolce):
            _kolec(p, nazwa + " kolec %d" % i, (x, y, 0), dl, rot, gr=0.1)


# ---------------------------------------------------------------------------------------------------- bryły
def _tulow(p):
    # --- klatka piersiowa (głęboka), barki, grzywa
    with _model(p, "Klatka"):
        p.blok("Klatka", (0, 2.45, 0.85), (1.15, 1.1, 1.5), "futro", faza=0.08)
        p.klin("Mostek", (0, 1.78, 1.0), (0.86, 0.32, 1.1), "futro", faza=0.05, rot=(0, 0, 180))
        p.blok("Piers", (0, 2.2, 1.62), (0.84, 0.8, 0.06), "futro_jasne", "matowy", faza=0.02)
        # kryza jasnej sierści na piersi (szpice w dół)
        for i, (x, dl) in enumerate(((-0.26, 0.42), (0.0, 0.5), (0.26, 0.42))):
            _kepka(p, "Kryza %d" % i, (x, 1.86, 1.6), dl, (180, 0, -x * 30), gr=(0.3, 0.12), kolor="futro_jasne")
        # łopatki (kłąb) i ciemne siodło
        for zn in (1, -1):
            p.blok("Lopatka", (zn * 0.3, 3.0, 1.05), (0.34, 0.16, 0.6), "futro", faza=0.05, rot=(0, 0, -zn * 12))
            # warstwy sierści na boku klatki (ciemne szpice do tyłu)
            for i, (y, z, dl) in enumerate(((2.55, 0.55, 0.42), (2.2, 0.75, 0.36))):
                _kepka(p, "Bok kepka %d" % i, (zn * 0.56, y, z), dl, (-90, -zn * 25, 0), gr=(0.05, 0.3))
        p.blok("Siodlo", (0, 3.02, 0.55), (0.78, 0.06, 0.9), "futro_ciemne", "matowy", faza=0.02)
        # grzbiet: kolce jeżyny (jasne) na przemian z kępkami ciemnej sierści
        _kolec(p, "Kolec grzbiet 1", (0, 3.02, 0.95), 0.42, (-38, 0, 0), gr=0.2)
        _kepka(p, "Kepka grzbiet 1", (0, 3.02, 0.7), 0.32, (-50, 0, 0))
        _kolec(p, "Kolec grzbiet 2", (0, 3.02, 0.4), 0.5, (-34, 0, 6), gr=0.22)
        _kolec(p, "Kolec bok L", (0.5, 2.95, 0.75), 0.3, (-30, 0, -50), gr=0.13)
        _kolec(p, "Kolec bok P", (-0.5, 2.95, 0.5), 0.3, (-30, 0, 50), gr=0.13)
        # pęd jeżyny wzdłuż grzbietu (z niego wyrastają kolce) i drugi wokół klatki
        p.blok("Ped grzbiet", (0.12, 3.075, 0.75), (0.07, 0.07, 1.0), "pnacze", "matowy", faza=0.02, rot=(0, 8, 0))
        _pnacze(p, "Pnacze klatka", 1.32, 1.95, 3.0, 1.15,
                kolce=((0.62, 2.55, (0, 0, -80), 0.22), (-0.62, 2.3, (0, 0, 80), 0.22), (0.2, 3.05, (-20, 0, -20),
                                                                                           0.2)))

    # --- talia (wcięta) i zad
    with _model(p, "Zad"):
        p.blok("Talia", (0, 2.5, -0.38), (0.86, 0.7, 1.0), "futro", faza=0.07)
        p.blok("Zad", (0, 2.45, -1.32), (1.05, 0.9, 0.85), "futro", faza=0.08)
        p.blok("Talia spod", (0, 2.13, -0.4), (0.6, 0.04, 0.8), "futro_jasne", "matowy", faza=0.0)
        p.blok("Siodlo talia", (0, 2.875, -0.4), (0.62, 0.06, 0.9), "futro_ciemne", "matowy", faza=0.02)
        p.blok("Siodlo zad", (0, 2.925, -1.3), (0.7, 0.06, 0.7), "futro_ciemne", "matowy", faza=0.02)
        for zn in (1, -1):
            _kepka(p, "Talia kepka", (zn * 0.42, 2.3, -0.05), 0.36, (-95, -zn * 20, 0), gr=(0.05, 0.28))
        p.blok("Ped grzbiet talia", (-0.1, 2.93, -0.45), (0.07, 0.07, 0.9), "pnacze", "matowy", faza=0.02,
               rot=(0, -10, 0))
        p.blok("Ped grzbiet zad", (-0.05, 2.985, -1.25), (0.07, 0.07, 0.6), "pnacze", "matowy", faza=0.02,
               rot=(0, 12, 0))
        _kepka(p, "Kepka zad 1", (0, 2.86, -0.05), 0.3, (-55, 0, 0))
        _kolec(p, "Kolec zad 1", (0, 2.86, -0.35), 0.45, (-36, 0, -6), gr=0.2)
        _kepka(p, "Kepka zad 2", (0, 2.88, -0.75), 0.3, (-55, 0, 0))
        _kolec(p, "Kolec zad 2", (0, 2.9, -1.1), 0.48, (-40, 0, 5), gr=0.22)
        _kolec(p, "Kolec zad 3", (0, 2.92, -1.5), 0.36, (-55, 0, 0), gr=0.18)
        _kolec(p, "Kolec biodro L", (0.53, 2.7, -1.15), 0.28, (-25, 0, -60), gr=0.13)
        _kolec(p, "Kolec biodro P", (-0.53, 2.75, -1.45), 0.28, (-25, 0, 60), gr=0.13)
        _pnacze(p, "Pnacze zad", -1.0, 2.0, 2.9, 1.05,
                kolce=((0.57, 2.35, (0, 0, -85), 0.2), (-0.57, 2.55, (0, 0, 85), 0.2)))


def _glowa(p):
    with _model(p, "Glowa"):
        # szyja pochylona do przodu (wychodzi z piersi) + obroża z pędu jeżyny
        p.blok("Szyja", (0, 2.82, 1.62), (0.8, 0.82, 0.9), "futro", faza=0.07, rot=(28, 0, 0))
        with p.uklad(pos=(0, 2.86, 1.7), obrot=(28, 0, 0)):
            p.blok("Obroza pnacze", (0, 0, 0), (0.88, 0.12, 0.98), "pnacze", "matowy", faza=0.03)
            for i, (x, z, rot) in enumerate(((0.44, 0.1, (0, 0, -90)), (-0.44, -0.15, (0, 0, 90)),
                                              (0.2, 0.49, (90, 0, -20)), (-0.25, 0.49, (90, 0, 25)))):
                _kolec(p, "Obroza kolec %d" % i, (x, 0, z), 0.2, rot, gr=0.09)
    with _ModelGlowy(p, "Glowa"):
        # czaszka, czoło, kości policzkowe
        p.blok("Czaszka", (0, 3.15, 2.15), (1.05, 0.85, 0.95), "futro", faza=0.08)
        p.blok("Czolo", (0, 3.585, 2.05), (0.62, 0.04, 0.7), "futro_ciemne", "matowy", faza=0.0)
        # kufa (długi pysk) z garbem nosa i jaśniejszym spodem
        p.blok("Kufa", (0, 2.98, 2.95), (0.62, 0.42, 0.8), "futro", faza=0.06)
        p.klin("Grzbiet nosa", (0, 3.24, 2.8), (0.56, 0.18, 0.5), "futro", faza=0.03, rot=(0, 180, 0))
        p.blok("Kufa bok jasny L", (0.315, 2.92, 2.98), (0.04, 0.22, 0.66), "futro_jasne", "matowy", faza=0.0)
        p.blok("Kufa bok jasny P", (-0.315, 2.92, 2.98), (0.04, 0.22, 0.66), "futro_jasne", "matowy", faza=0.0)
        p.blok("Nos", (0, 3.12, 3.37), (0.32, 0.2, 0.16), "tusz", "polysk", faza=0.05)
        p.blok("Nos blysk", (0.07, 3.19, 3.455), (0.08, 0.04, 0.02), "bialy", faza=0.0)
        p.blok("Warga", (0, 2.785, 2.98), (0.64, 0.05, 0.77), "tusz", "matowy", faza=0.0)
        p.blok("Podniebienie", (0, 2.76, 2.9), (0.5, 0.04, 0.66), "gardlo", "matowy", faza=0.0)
        # górne kły na zewnątrz żuchwy + siekacze
        for zn in (1, -1):
            with p.uklad(pos=(zn * 0.26, 2.79, 3.22), obrot=(180, 0, 0)):
                p.ostroslup("Kiel gorny", (0, 0.12, 0), (0.1, 0.24, 0.1), "kosc", "polysk", gora=(0.0, 0.0),
                            przes_gory=(0.0, -0.02))
        for i, x in enumerate((-0.1, 0.1)):
            p.blok("Siekacz %d" % i, (x, 2.74, 3.3), (0.07, 0.07, 0.05), "kosc", "polysk", faza=0.0)
        # oczy: ciemny oczodół, bursztyn (świeci), pionowa źrenica, błysk; ciężkie brwi w „V”
        zf = 2.625
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * 0.27
            with p.uklad(pos=(x, 3.33, zf), obrot=(0, 0, zn * 14)):
                # warstwy płytkie (każda wystaje 0,02 nad poprzednią), żeby obrys renderu nie rysował przy bocznym
                # spojrzeniu grubych pionowych kresek; źrenica krótsza niż oko — nie dzieli go na dwa „okienka”
                p.blok("Oczodol " + s, (0, 0, 0.005), (0.44, 0.28, 0.03), "tusz", "matowy", faza=0.0)
                p.blok("Oko " + s, (0, -0.01, 0.025), (0.36, 0.2, 0.03), "bursztyn", "swiecacy", faza=0.0)
                p.blok("Zrenica " + s, (0, -0.01, 0.05), (0.08, 0.14, 0.02), "tusz", "polysk", faza=0.0)
            p.blok("Brew " + s, (zn * 0.28, 3.49, zf + 0.05), (0.44, 0.13, 0.16), "futro_ciemne", "matowy",
                   faza=0.03, rot=(0, 0, zn * 22))
            # sierść policzków: dwa szpice w bok i do tyłu
            for i, (y, z, dl) in enumerate(((3.0, 1.95, 0.42), (2.82, 1.8, 0.34))):
                _kepka(p, "Policzek %s %d" % (s, i), (zn * 0.5, y, z), dl, (-20, 0, -zn * 105), gr=(0.24, 0.12),
                       kolor="futro")
        # zjeżona grzywa na karku (ciemne szpice w górę i do tyłu)
        for i, (x, y, z, dl, rz) in enumerate(((0.0, 3.5, 1.72, 0.5, 0), (0.24, 3.38, 1.62, 0.42, -20),
                                                (-0.24, 3.38, 1.62, 0.42, 20), (0.0, 3.25, 1.4, 0.42, 0))):
            _kepka(p, "Grzywa %d" % i, (x, y, z), dl, (-62, 0, rz), gr=(0.3, 0.14))

    # żuchwa: zawias pod czaszką, dolne kły (schowane w kufie, widoczne przy otwartej paszczy), język
    with _ModelGlowy(p, "Szczeka"):
        p.blok("Zuchwa", (0, 2.66, 2.85), (0.44, 0.2, 0.85), "futro", faza=0.05)
        p.blok("Broda", (0, 2.6, 3.27), (0.32, 0.1, 0.1), "futro_jasne", "matowy", faza=0.02)
        p.blok("Dziaslo", (0, 2.775, 2.85), (0.36, 0.04, 0.72), "gardlo", "matowy", faza=0.0)
        p.blok("Jezyk", (0, 2.8, 2.8), (0.26, 0.04, 0.5), "jezyk", "polysk", faza=0.0)
        for zn in (1, -1):
            _kolec(p, "Kiel dolny", (zn * 0.15, 2.76, 3.15), 0.17, (0, 0, 0), gr=0.08, kolor="kosc")

    # uszy: wysokie, spiczaste, lekko na zewnątrz
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Ucho" + s, obrot=(-8, 0, -zn * 14)), p.uklad(skala=SKALA_GLOWY):
            p.ostroslup("Ucho", (0, 0.3, 0), (0.36, 0.62, 0.22), "futro", "zwykly", gora=(0.0, 0.0))
            p.ostroslup("Ucho srodek", (0, 0.24, 0.08), (0.2, 0.4, 0.08), "futro_jasne", "matowy", gora=(0.0, 0.0))
            p.ostroslup("Ucho czubek", (0, 0.55, 0.0), (0.12, 0.14, 0.08), "futro_ciemne", "matowy", gora=(0.0, 0.0))

    # powieki: w spoczynku schowane w czaszce nad oczami; przes (0, 0, 0.29) zasłania oczy
    with p.na("Powieki"), p.uklad(skala=SKALA_GLOWY):
        for zn in (1, -1):
            p.blok("Powieka", (zn * 0.27, 0.0, -0.15), (0.44, 0.3, 0.04), "futro_ciemne", "matowy", faza=0.0,
                   rot=(0, 0, zn * 14))


def _lapy(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        x = zn * X_LAP
        # --- przednia: ramię (górą w piersi), przedramię, śródręcze i łapa z pazurami
        with _model(p, "LapaPrzod%s_Gora" % s):
            p.blok("Ramie", (x, 1.78, 1.0), (0.42, 1.2, 0.56), "futro", faza=0.06)
            _kepka(p, "Lokiec kepka", (x, 1.35, 0.75), 0.3, (-120, 0, 0), gr=(0.26, 0.05))
        with _model(p, "LapaPrzod%s_Dol" % s):
            p.blok("Przedramie", (x, 0.82, 1.0), (0.34, 0.84, 0.38), "futro", faza=0.05)
            p.blok("Przedramie przod", (x, 0.82, 1.2), (0.22, 0.6, 0.04), "futro_jasne", "matowy", faza=0.0)
        with _model(p, "LapaPrzod%s_Stopa" % s):
            p.blok("Srodreze", (x, 0.3, 1.04), (0.31, 0.32, 0.34), "futro", faza=0.04)
            _lapa(p, x, 1.12)
        # --- tylna: szerokie udo (do przodu), goleń do tyłu, pięta, śródstopie pionowo, łapa
        with _model(p, "LapaTyl%s_Gora" % s):
            with p.uklad(pos=(x, 1.9, -1.18), obrot=(-18, 0, 0)):
                p.blok("Udo", (0, 0, 0), (0.42, 1.2, 0.72), "futro", faza=0.07)
                _kepka(p, "Udo kepka", (zn * 0.2, 0.3, -0.3), 0.34, (-100, -zn * 15, 0), gr=(0.05, 0.26))
        with _model(p, "LapaTyl%s_Dol" % s):
            with p.uklad(pos=(x, 1.08, -1.24), obrot=(31, 0, 0)):
                p.blok("Golen", (0, 0, 0), (0.34, 0.95, 0.38), "futro", faza=0.05)
            p.blok("Pieta", (x, 0.72, -1.55), (0.26, 0.2, 0.18), "futro_ciemne", "matowy", faza=0.04)
            p.blok("Srodstopie", (x, 0.52, -1.44), (0.3, 0.5, 0.32), "futro", faza=0.04)
        with _model(p, "LapaTyl%s_Stopa" % s):
            p.blok("Srodstopie dol", (x, 0.24, -1.43), (0.29, 0.14, 0.3), "futro", faza=0.03)
            _lapa(p, x, -1.33)


def _lapa(p, x, z):
    """Łapa: klocek z jaśniejszym spodem i trzema pazurami z przodu (spód na y = 0)."""
    p.blok("Lapa", (x, 0.1, z), (0.46, 0.2, 0.56), "futro_ciemne", faza=0.04)
    p.blok("Lapa wierzch", (x, 0.215, z + 0.04), (0.34, 0.04, 0.4), "futro", "matowy", faza=0.0)
    for i, dx in enumerate((-0.12, 0.0, 0.12)):
        with p.uklad(pos=(x + dx * 1.15, 0.06, z + 0.27), obrot=(80, 0, 0)):
            p.ostroslup("Pazur %d" % i, (0, 0.07, 0), (0.07, 0.14, 0.08), "kosc", "polysk", gora=(0.0, 0.0))


def _ogon(p):
    """Ogon: futrzana nasada i gęstwina pędów jeżyny z kolcami i liśćmi na końcu (jak zarośla)."""
    # układ ogona: +Y wzdłuż ogona ku końcowi, +Z = w górę (grzbiet ogona), +X = lewa strona wilka
    with p.na("Ogon", obrot=(OGON_KAT, 0, 0)):
        p.blok("Ogon nasada", (0, 0.28, 0), (0.5, 0.62, 0.56), "futro", faza=0.06)
        for i, y in enumerate((0.18, 0.45)):
            _kepka(p, "Ogon kepka %d" % i, (0, y, 0.24), 0.3, (45, 0, 0), gr=(0.22, 0.1))
        _kolec(p, "Ogon kolec", (0.24, 0.3, 0), 0.22, (0, 0, -80), gr=0.1)
    with p.na("OgonKoniec", obrot=(OGON_KAT, 0, 0)):
        # kita: futrzany rdzeń zwężający się ku końcowi, w środku ciemna gęstwina
        p.ostroslup("Ogon kita", (0, 0.55, 0), (0.8, 1.1, 0.84), "futro", "zwykly", gora=(0.24, 0.26))
        p.blok("Ogon gestwina", (0, 0.5, 0), (0.62, 0.8, 0.62), "pnacze_ciemne", "matowy", faza=0.08,
               rot=(0, 45, 0))
        # pędy jeżyny wyrastają wzdłuż całej kity i rozchodzą się do tyłu na wszystkie strony (jak zarośla);
        # (wysokość nasady, odchylenie od osi, kierunek odchylenia wokół osi: 90 = w górę, długość, kolor)
        for i, (y0, th, fi, dl, kol) in enumerate((
                (0.12, 52, 90, 0.5, "pnacze"), (0.18, 50, 210, 0.45, "pnacze_ciemne"),
                (0.24, 55, 330, 0.48, "pnacze"), (0.4, 40, 30, 0.6, "pnacze_ciemne"),
                (0.45, 40, 150, 0.6, "pnacze"), (0.5, 44, 270, 0.5, "pnacze"),
                (0.66, 30, 100, 0.62, "pnacze_ciemne"), (0.7, 30, 220, 0.6, "pnacze"),
                (0.72, 32, 340, 0.58, "pnacze_ciemne"), (0.86, 12, 60, 0.6, "pnacze"),
                (0.86, 14, 200, 0.56, "pnacze_ciemne"))):
            fr = math.radians(fi)
            with p.uklad(pos=(0.18 * math.cos(fr), y0, 0.18 * math.sin(fr)),
                         obrot=(th * math.sin(fr), 0, -th * math.cos(fr))):
                dl *= 1.2
                p.ostroslup("Ped %d" % i, (0, dl / 2, 0), (0.12, dl, 0.12), kol, "matowy", gora=(0.03, 0.03))
                _kolec(p, "Ped kolec %d" % i, (0.05, dl * 0.5, 0), 0.13, (0, 0, -75), gr=0.07)
                if i % 3 == 0:
                    with p.uklad(pos=(0, dl * 0.7, 0.04), obrot=(55, 0, 0)):
                        p.ostroslup("Ped lisc %d" % i, (0, 0.11, 0), (0.18, 0.22, 0.04), "pnacze_ciemne", "matowy",
                                    gora=(0.0, 0.0))
        for i, (y, fi) in enumerate(((0.3, 60), (0.55, 120), (0.75, 80))):
            fr = math.radians(fi)
            _kepka(p, "Kita kepka %d" % i, (0, y, 0), 0.45, (40 * math.sin(fr), 0, -40 * math.cos(fr)),
                   gr=(0.22, 0.1))


# ---------------------------------------------------------------------------------------------------- kinematyka
I3 = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def _T(m):
    return tuple(tuple(m[j][i] for j in range(3)) for i in range(3))


def _fk(p, poza):
    """{kość: {"obrot", "przes"}} -> {kość: (obrót w świecie, staw w świecie)}."""
    W = {}
    for n, k in p.kosci.items():
        v = poza.get(n, {})
        Rl = macierz_obrotu(*v.get("obrot", (0, 0, 0)))
        pr = v.get("przes", (0, 0, 0))
        if k["rodzic"] is None:
            W[n] = (Rl, tuple(k["staw"][i] + pr[i] for i in range(3)))
        else:
            Rp, tp = W[k["rodzic"]]
            st = p.kosci[k["rodzic"]]["staw"]
            d = razy_wektor(Rp, tuple(k["staw"][i] - st[i] + pr[i] for i in range(3)))
            W[n] = (mnoz(Rp, Rl), tuple(tp[i] + d[i] for i in range(3)))
    return W


def _punkty(c):
    """Narożniki i środki ścian skrzynki bryły (w układzie stawu kości)."""
    Rc = macierz_obrotu(*c["r"])
    h = [v / 2 for v in c["s"]]
    pk = []
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            for e in (-1, 0, 1):
                n = math.sqrt(a * a + b * b + e * e) if (c["k"] == "kula" and (a or b or e)) else 1.0
                lok = razy_wektor(Rc, (a * h[0] / n, b * h[1] / n, e * h[2] / n))
                pk.append(tuple(c["p"][i] + lok[i] for i in range(3)))
    return pk


def _najnizej(p, W, kosci=None):
    mn = 1e9
    for c in p.czesci:
        if kosci is not None and c["kosc"] not in kosci:
            continue
        R, t = W[c["kosc"]]
        for q in _punkty(c):
            mn = min(mn, razy_wektor(R, q)[1] + t[1])
    return mn


def _ik(p, W, noga, cel):
    """Dwa ogniwa w płaszczyźnie łapy: (rx Gora, rx Dol) tak, by staw stopy trafił w punkt cel (świat)."""
    baza, rodzic, _ = NOGI[noga]
    g, d, s = baza + "_Gora", baza + "_Dol", baza + "_Stopa"
    Rp, tp = W[rodzic]
    st = p.kosci[rodzic]["staw"]
    hip, kol, sto = p.staw(g), p.staw(d), p.staw(s)
    q = razy_wektor(_T(Rp), tuple(cel[i] - tp[i] for i in range(3)))
    q = tuple(q[i] - (hip[i] - st[i]) for i in range(3))
    y1, z1 = kol[1] - hip[1], kol[2] - hip[2]
    y2, z2 = sto[1] - kol[1], sto[2] - kol[2]
    A, B = y1 * y2 + z1 * z2, z1 * y2 - y1 * z2
    C = (q[1] ** 2 + q[2] ** 2 - (y1 * y1 + z1 * z1) - (y2 * y2 + z2 * z2)) / 2.0
    R = math.hypot(A, B)
    fi = math.atan2(B, A)
    c = max(-1.0, min(1.0, C / R))
    kand = [fi + math.acos(c), fi - math.acos(c)]
    kand = [math.atan2(math.sin(b), math.cos(b)) for b in kand]
    b = min(kand, key=abs)
    wy = y1 + y2 * math.cos(b) - z2 * math.sin(b)
    wz = z1 + y2 * math.sin(b) + z2 * math.cos(b)
    a = math.atan2(q[2], q[1]) - math.atan2(wz, wy)
    a = math.atan2(math.sin(a), math.cos(a))
    return math.degrees(a), math.degrees(b)


def _plaska_stopa(p, W, noga, rx_g, rx_d, rz_g=0.0):
    """Obrót kości Stopa, przy którym łapa leży płasko (obrót w świecie = brak)."""
    _, rodzic, _ = NOGI[noga]
    Rp = W[rodzic][0]
    R = mnoz(mnoz(Rp, macierz_obrotu(rx_g, 0, rz_g)), macierz_obrotu(rx_d, 0, 0))
    return katy_z_macierzy(_T(R))


def _trojka(v):
    if isinstance(v, (int, float)):
        return (float(v), 0.0, 0.0)
    return tuple(float(x) for x in v)


def _rozwiaz(p, pz):
    """Poza kluczowa -> {kość: {"obrot", "przes"}} z łapami rozwiązanymi (IK albo kąty) i ciałem nad ziemią.
    Poza: {kość: (rx, ry, rz) | {"obrot", "przes"}}, "nogi": {"PL"|"PP"|"TL"|"TP": ("z", dz, h) — łapa stoi
    (dz = przesunięcie po ziemi względem spoczynku, h = uniesienie) | ("k", gora, dol[, stopa]) — kąty},
    "lez": True — całe ciało opuszczone do ziemi po najniższym punkcie (leżenie)."""
    wyn = {}
    for n, v in pz.items():
        if n in ("nogi", "lez"):
            continue
        wyn[n] = {"obrot": _trojka(v)} if not isinstance(v, dict) else {
            "obrot": _trojka(v.get("obrot", (0, 0, 0))), "przes": tuple(v.get("przes", (0, 0, 0)))}
    wyn.setdefault("Zad", {}).setdefault("obrot", (0.0, 0.0, 0.0))
    wyn["Zad"].setdefault("przes", (0.0, 0.0, 0.0))
    nogi = pz.get("nogi", {})
    W = _fk(p, wyn)
    for noga, (baza, rodzic, zn) in NOGI.items():
        sp = nogi.get(noga, ("z", 0.0, 0.0))
        if sp[0] == "z":
            st = p.staw(baza + "_Stopa")
            a, b = _ik(p, W, noga, (st[0], st[1] + sp[2], st[2] + sp[1]))
            wyn[baza + "_Gora"] = {"obrot": (a, 0.0, 0.0)}
            wyn[baza + "_Dol"] = {"obrot": (b, 0.0, 0.0)}
            wyn[baza + "_Stopa"] = {"obrot": _plaska_stopa(p, W, noga, a, b)}
        else:
            wyn[baza + "_Gora"] = {"obrot": _trojka(sp[1])}
            wyn[baza + "_Dol"] = {"obrot": _trojka(sp[2])}
            wyn[baza + "_Stopa"] = {"obrot": _trojka(sp[3]) if len(sp) > 3 else (0.0, 0.0, 0.0)}
    if pz.get("lez"):
        dno = _najnizej(p, _fk(p, wyn))
        x, y, z = wyn["Zad"]["przes"]
        wyn["Zad"]["przes"] = (x, y - dno, z)
    wyn["_nogi"] = {n: nogi.get(n, ("z", 0.0, 0.0)) for n in NOGI}
    return wyn


def _ciaglosc(ob, poprz):
    """Ten sam obrót zapisany kątami najbliższymi poprzedniemu (bez skoku −170° → +170°)."""
    if poprz is None:
        return tuple(ob)

    def blisko(a, b):
        return a + 360.0 * round((b - a) / 360.0)
    return tuple(round(blisko(ob[i], poprz[i]), 3) for i in range(3))


def _sekwencja(k, czasy, pozy, wyg=None):
    """Klucz w KAŻDEJ klatce między pozami kluczowymi (łagodne wejście i wyjście; wyg={i: "liniowo"} — odcinek od
    pozy i jednostajnie). Łapy stojące w obu pozach odcinka są w każdej klatce dociągane do ziemi (IK), stopy
    płasko; w każdej klatce nic nie schodzi pod ziemię (ciało podnoszone po najniższym punkcie)."""
    p = k.postac
    roz = [_rozwiaz(p, pz) for pz in pozy]
    kosci = [n for n in p.kosci if n != "Root"]
    poprz = {}
    for f in range(int(czasy[0]), int(czasy[-1]) + 1):
        i = max(j for j in range(len(czasy) - 1) if czasy[j] <= f) if f < czasy[-1] else len(czasy) - 2
        t = (f - czasy[i]) / float(czasy[i + 1] - czasy[i])
        e = t if (wyg or {}).get(i) == "liniowo" else t * t * (3 - 2 * t)
        A, B = roz[i], roz[i + 1]
        pz = {}
        for n in kosci:
            a, b = A.get(n, {}), B.get(n, {})
            oa, ob = a.get("obrot", (0, 0, 0)), b.get("obrot", (0, 0, 0))
            ob = _ciaglosc(ob, oa)
            pa, pb = a.get("przes", (0, 0, 0)), b.get("przes", (0, 0, 0))
            pz[n] = {"obrot": tuple(oa[j] + (ob[j] - oa[j]) * e for j in range(3)),
                     "przes": tuple(pa[j] + (pb[j] - pa[j]) * e for j in range(3))}
        W = _fk(p, pz)
        for noga, (baza, rodzic, zn) in NOGI.items():
            sa, sb = A["_nogi"][noga], B["_nogi"][noga]
            if sa[0] == "z" and sb[0] == "z":
                dz = sa[1] + (sb[1] - sa[1]) * e
                h = sa[2] + (sb[2] - sa[2]) * e
                st = p.staw(baza + "_Stopa")
                ag, bd = _ik(p, W, noga, (st[0], st[1] + h, st[2] + dz))
                pz[baza + "_Gora"]["obrot"] = (ag, 0.0, 0.0)
                pz[baza + "_Dol"]["obrot"] = (bd, 0.0, 0.0)
                pz[baza + "_Stopa"]["obrot"] = _plaska_stopa(p, W, noga, ag, bd)
        dno = _najnizej(p, _fk(p, pz))
        if dno < 0.0:
            x, y, z = pz["Zad"]["przes"]
            pz["Zad"]["przes"] = (x, y - dno, z)
        for n in kosci:
            o = _ciaglosc(pz[n]["obrot"], poprz.get(n))
            poprz[n] = o
            k.klucz(f, n, obrot=tuple(round(v, 2) for v in o), wyg="liniowo")
        k.klucz(f, "Zad", przes=tuple(round(v, 3) for v in pz["Zad"]["przes"]), wyg="liniowo")
        k.klucz(f, "Powieki", przes=tuple(round(v, 3) for v in pz["Powieki"]["przes"]), wyg="liniowo")


# ---------------------------------------------------------------------------------------------------- animacje
OTWARTE, ZAMKNIETE = (0.0, 0.0, 0.0), (0.0, 0.0, 0.29 * SKALA_GLOWY)        # przesunięcie kości Powieki
BAZA = {"Glowa": (6, 0, 0), "Szczeka": (4, 0, 0), "UchoL": (0, 0, 0), "UchoP": (0, 0, 0)}


def _z(baza, **zm):
    d = dict(baza)
    d.update(zm)
    return d


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
    """Czujne czekanie (2,4 s): oddech (ciało lekko opada, łapy stoją), łeb nisko rozgląda się w lewo i w prawo,
    warczenie (żuchwa drga), uszy strzygą, ogon-zarośla kołysze się; jedno mrugnięcie."""
    k = p.klip("idle", dl, petla=True)
    a = _z(BAZA)
    b = _z(BAZA, Zad={"przes": (0, -0.05, 0)}, Klatka=(1.5, 0, 0), Glowa=(9, 14, 0), Szczeka=(9, 0, 0),
           UchoL=(0, 0, 8), Ogon=(0, 0, 9), OgonKoniec=(0, 0, 12))
    c = _z(BAZA, Glowa=(5, 2, 0), Szczeka=(3, 0, 0), Ogon=(0, 0, -4), OgonKoniec=(0, 0, -6))
    d = _z(c, Powieki={"przes": ZAMKNIETE})
    e = _z(BAZA, Zad={"przes": (0, -0.05, 0)}, Klatka=(1.5, 0, 0), Glowa=(9, -14, 0), Szczeka=(9, 0, 0),
           UchoP=(0, 0, -8), Ogon=(0, 0, -9), OgonKoniec=(0, 0, -12))
    _sekwencja(k, (0, 18, 34, 37, 40, 54, dl), (a, b, c, d, c, e, a))
    return k


# galop: początek podparcia każdej łapy (ułamek cyklu) — tylne, potem przednie, potem lot w fazie zebranej
GALOP_FAZY = {"TL": 0.0, "TP": 0.08, "PL": 0.38, "PP": 0.46}
GALOP_PODPORA = 0.4              # jaką część cyklu łapa stoi na ziemi
GALOP_KROK = {"P": 0.8, "T": 0.8}         # łapa sunie po ziemi od +krok do −krok względem spoczynku
GALOP_UNIES = {"P": 0.55, "T": 0.5}       # (przednia łapa przy 0,8 jest prawie wyprostowana — więcej nie sięgnie)
GALOP_LOT = 0.22                          # uniesienie ciała w fazie zebranej (lot)


def ruch(p, dl=16):
    """Galop (0,53 s, w miejscu): łapa w podporze sunie po ziemi od przodu do tyłu (dociągana do ziemi odwrotną
    kinematyką), w przenoszeniu wraca łukiem w powietrzu z podwiniętą łapą. Kolejność: tylna lewa, tylna prawa,
    przednia lewa, przednia prawa, krótki lot w fazie zebranej. Ciało biegnie nisko (−0,2), grzbiet się wygina,
    łeb nisko i stabilnie, uszy położone, paszcza uchylona, ogon-zarośla płynie za wilkiem."""
    k = p.klip("ruch", dl, petla=True)
    for f in range(dl + 1):
        t = f / float(dl)

        def sn(ph):
            return math.sin(2 * math.pi * (t + ph))
        zebr = math.cos(2 * math.pi * (t - 0.93))             # +1 w fazie zebranej (lot), −1 w wyciągniętej
        lot = GALOP_LOT * max(0.0, zebr) ** 2
        kl, zd = 9 * zebr, 3 * sn(0.2)
        pz = {"Zad": {"obrot": (zd, 0, 0), "przes": (0, -0.2 + lot, 0)}, "Klatka": {"obrot": (kl, 0, 0)},
              "Glowa": {"obrot": (8 - 0.8 * (kl + zd), 0, 0)}, "Szczeka": {"obrot": (14 + 5 * sn(0.1), 0, 0)},
              "UchoL": {"obrot": (-32, 0, 6)}, "UchoP": {"obrot": (-32, 0, -6)},
              "Ogon": {"obrot": (12 + 6 * sn(0.3), 0, 4 * sn(0.0))},
              "OgonKoniec": {"obrot": (6 + 10 * sn(0.15), 0, 7 * sn(0.2))}, "Powieki": {"obrot": (0, 0, 0)}}
        W = _fk(p, pz)
        for noga, (baza, rodzic, zn) in NOGI.items():
            rodz = noga[0]
            u = (t - GALOP_FAZY[noga]) % 1.0
            A, H = GALOP_KROK[rodz], GALOP_UNIES[rodz]
            if u < GALOP_PODPORA:
                s = u / GALOP_PODPORA
                dz, h, mach = A * (1 - 2 * s), 0.0, 0.0
            else:
                s = (u - GALOP_PODPORA) / (1 - GALOP_PODPORA)
                dz, h = -A * math.cos(math.pi * s), H * math.sin(math.pi * s)
                mach = math.sin(math.pi * s)
            st = p.staw(baza + "_Stopa")
            ag, bd = _ik(p, W, noga, (st[0], st[1] + h, st[2] + dz))
            stopa = _plaska_stopa(p, W, noga, ag, bd)
            stopa = (stopa[0] + mach * (60 if rodz == "P" else -35), stopa[1], stopa[2])
            pz[baza + "_Gora"] = {"obrot": (ag, 0, 0)}
            pz[baza + "_Dol"] = {"obrot": (bd, 0, 0)}
            pz[baza + "_Stopa"] = {"obrot": stopa}
        dno = _najnizej(p, _fk(p, pz))
        if dno < 0:
            pz["Zad"]["przes"] = (0, pz["Zad"]["przes"][1] - dno, 0)
        for n, v in pz.items():
            k.klucz(f, n, obrot=tuple(round(x, 2) for x in v["obrot"]), wyg="gladko")
        k.klucz(f, "Zad", przes=tuple(round(x, 3) for x in pz["Zad"]["przes"]), wyg="gladko")
    return k


def atak(p, dl=27):
    """Zwykły cios — ugryzienie z wypadu (0,9 s): przysiad z cofnięciem i łbem nisko (kl. 7), paszcza szeroko
    (kl. 10), wypad do przodu z przednimi łapami w powietrzu i KŁAPNIĘCIE w kl. 13, szarpnięcie łbem, powrót."""
    k = p.klip("atak", dl, petla=False)
    zamach = _z(BAZA, Zad={"przes": (0, -0.3, -0.35), "obrot": (4, 0, 0)}, Klatka=(3, 0, 0), Glowa=(16, 0, 0),
                Szczeka=(20, 0, 0), UchoL=(-35, 0, 10), UchoP=(-35, 0, -10), Ogon=(-12, 0, 0))
    otwarcie = _z(BAZA, Zad={"przes": (0, -0.12, 0.45), "obrot": (-3, 0, 0)}, Klatka=(-2, 0, 0), Glowa=(4, 0, 0),
                  Szczeka=(56, 0, 0), UchoL=(-35, 0, 10), UchoP=(-35, 0, -10), Ogon=(4, 0, 0),
                  nogi={"PL": ("z", 0.2, 0.15), "PP": ("z", 0.1, 0.1)})
    traf = _z(BAZA, Zad={"przes": (0, 0.08, 1.35), "obrot": (-8, 0, 0)}, Klatka=(-5, 0, 0), Glowa=(12, 0, 0),
              Szczeka=(-2, 0, 0), UchoL=(-30, 0, 8), UchoP=(-30, 0, -8), Ogon=(10, 0, 4), OgonKoniec=(8, 0, 0),
              nogi={"PL": ("k", -64, -36, 60), "PP": ("k", -52, -42, 60), "TL": ("z", 0.9, 0.0),
                    "TP": ("z", 0.85, 0.0)})
    szarp = _z(BAZA, Zad={"przes": (0, -0.05, 1.15), "obrot": (-1, 0, 0)}, Klatka=(1, 0, 0), Glowa=(12, 14, 6),
               Szczeka=(-2, 0, 0), UchoL=(-25, 0, 8), UchoP=(-25, 0, -8), Ogon=(4, 0, -6),
               nogi={"PL": ("z", 1.2, 0.0), "PP": ("z", 1.1, 0.0), "TL": ("z", 0.75, 0.0), "TP": ("z", 0.7, 0.0)})
    szarp2 = _z(szarp, Glowa=(10, -10, -4), Ogon=(4, 0, 6))
    odskok = _z(BAZA, Zad={"przes": (0, 0.05, 0.35)}, Glowa=(8, 0, 0), Szczeka=(6, 0, 0),
                nogi={"PL": ("z", 0.4, 0.2), "PP": ("z", 0.35, 0.15), "TL": ("z", 0.2, 0.1), "TP": ("z", 0.2, 0.1)})
    _sekwencja(k, (0, 7, 10, 13, 17, 20, 23, dl), (BAZA, zamach, otwarcie, traf, szarp, szarp2, odskok, BAZA),
               wyg={2: "liniowo"})
    return k


def umiejetnosc(p, dl=54):
    """Rozszarpanie (1,8 s): głęboki przysiad (kl. 8), wybicie z otwartą paszczą (kl. 12), w locie DWA szybkie
    kłapnięcia (kl. 17 i 23) z szarpnięciem łba, lądowanie przed sobą i szarpanie łbem na boki (kl. 27–38),
    odskok tyłem na miejsce (kl. 42–48)."""
    k = p.klip("umiejetnosc", dl, petla=False)
    uszy = {"UchoL": (-40, 0, 12), "UchoP": (-40, 0, -12)}
    przysiad = _z(BAZA, Zad={"przes": (0, -0.55, -0.3), "obrot": (4, 0, 0)}, Klatka=(4, 0, 0), Glowa=(16, 0, 0),
                  Szczeka=(16, 0, 0), Ogon=(-20, 0, 0), **uszy)
    wybicie = _z(BAZA, Zad={"przes": (0, 0.25, 0.6), "obrot": (-18, 0, 0)}, Klatka=(-6, 0, 0), Glowa=(8, 0, 0),
                 Szczeka=(42, 0, 0), Ogon=(10, 0, 0), **uszy)
    wybicie["nogi"] = {"PL": ("k", -62, 55, 30), "PP": ("k", -55, 60, 30), "TL": ("z", 0.35, 0.0),
                       "TP": ("z", 0.3, 0.0)}
    lot = {"PL": ("k", -78, 22, 20), "PP": ("k", -70, 28, 20), "TL": ("k", 48, 5, 30), "TP": ("k", 42, 8, 30)}
    klap1 = _z(BAZA, Zad={"przes": (0, 1.3, 1.6), "obrot": (-6, 0, 0)}, Klatka=(-4, 0, 0), Glowa=(12, 10, 0),
               Szczeka=(-2, 0, 0), Ogon=(16, 0, 6), OgonKoniec=(10, 0, 0), nogi=lot, **uszy)
    otw2 = _z(BAZA, Zad={"przes": (0, 1.25, 2.0), "obrot": (0, 0, 0)}, Klatka=(-2, 0, 0), Glowa=(2, -8, 0),
              Szczeka=(46, 0, 0), Ogon=(12, 0, -6), OgonKoniec=(6, 0, 0), nogi=lot, **uszy)
    klap2 = _z(BAZA, Zad={"przes": (0, 0.8, 2.3), "obrot": (7, 0, 0)}, Klatka=(2, 0, 0), Glowa=(14, 12, 4),
               Szczeka=(-2, 0, 0), Ogon=(8, 0, 6),
               nogi={"PL": ("k", -40, 12, 10), "PP": ("k", -36, 16, 10), "TL": ("k", 20, 20, 0),
                     "TP": ("k", 16, 22, 0)}, **uszy)
    stoi = {"PL": ("z", 2.55, 0.0), "PP": ("z", 2.5, 0.0), "TL": ("z", 2.25, 0.0), "TP": ("z", 2.2, 0.0)}
    ladowanie = _z(BAZA, Zad={"przes": (0, -0.35, 2.4), "obrot": (5, 0, 0)}, Klatka=(6, 0, 0), Glowa=(20, -16, -6),
                   Szczeka=(-2, 0, 0), Ogon=(-6, 0, 0), nogi=stoi, **uszy)
    szarp1 = _z(ladowanie, Zad={"przes": (0, -0.25, 2.4), "obrot": (3, 2, 0)}, Glowa=(16, 18, 8), Ogon=(-4, 0, 8))
    szarp2 = _z(ladowanie, Zad={"przes": (0, -0.25, 2.4), "obrot": (3, -2, 0)}, Glowa=(14, -14, -6),
                Ogon=(-4, 0, -8))
    puszcza = _z(BAZA, Zad={"przes": (0, -0.2, 2.4), "obrot": (2, 0, 0)}, Glowa=(10, 4, 0), Szczeka=(14, 0, 0),
                 nogi=stoi)
    odskok = _z(BAZA, Zad={"przes": (0, 0.4, 1.2), "obrot": (-4, 0, 0)}, Glowa=(8, 0, 0), Szczeka=(8, 0, 0),
                nogi={"PL": ("k", 10, 40, 0), "PP": ("k", 6, 44, 0), "TL": ("k", -24, 30, 0),
                      "TP": ("k", -20, 32, 0)})
    ladow2 = _z(BAZA, Zad={"przes": (0, -0.15, 0.0), "obrot": (2, 0, 0)}, Glowa=(8, 0, 0))
    _sekwencja(k, (0, 8, 12, 17, 20, 23, 27, 31, 35, 38, 43, 48, dl),
               (BAZA, przysiad, wybicie, klap1, otw2, klap2, ladowanie, szarp1, szarp2, puszcza, odskok, ladow2,
                BAZA), wyg={2: "liniowo", 4: "liniowo"})
    return k


def trafienie(p, dl=18):
    """Reakcja na cios (0,6 s): szarpnięcie w tył (kl. 3) — łeb w górę i w bok, paszcza otwarta w skowycie, uszy
    położone, przednie łapy podrywają się; cofnięcie i powrót."""
    k = p.klip("trafienie", dl, petla=False)
    szarp = _z(BAZA, Zad={"przes": (0, 0.05, -0.45), "obrot": (-6, 0, 3)}, Klatka=(-8, 0, 0), Glowa=(-24, -12, 8),
               Szczeka=(30, 0, 0), UchoL=(-40, 0, 14), UchoP=(-40, 0, -14), Ogon=(-25, 0, 10),
               OgonKoniec=(-10, 0, 0),
               nogi={"PL": ("z", -0.25, 0.25), "PP": ("z", -0.2, 0.2), "TL": ("z", -0.3, 0.0), "TP": ("z", -0.3, 0.0)})
    wraca = _z(BAZA, Zad={"przes": (0, -0.08, -0.3), "obrot": (-1, 0, 1)}, Glowa=(-4, -4, 0), Szczeka=(10, 0, 0),
               UchoL=(-15, 0, 4), UchoP=(-15, 0, -4), Ogon=(-10, 0, 0),
               nogi={"PL": ("z", -0.3, 0.0), "PP": ("z", -0.3, 0.0), "TL": ("z", -0.3, 0.0), "TP": ("z", -0.3, 0.0)})
    _sekwencja(k, (0, 3, 8, dl), (BAZA, szarp, wraca, BAZA), wyg={0: "liniowo"})
    return k


def unik(p, dl=28):
    """Unik (0,93 s): przysiad z przechyłem, skok w lewo (+X) z podkurczonymi łapami, lądowanie bokiem do linii
    ciosu z łbem zwróconym na przeciwnika, chwila, skok z powrotem na miejsce."""
    k = p.klip("unik", dl, petla=False)
    podkurcz = {"PL": ("k", -30, 60, 10), "PP": ("k", -26, 64, 10), "TL": ("k", -30, 40, 0), "TP": ("k", -26, 44, 0)}
    przysiad = _z(BAZA, Zad={"przes": (0.15, -0.35, 0), "obrot": (2, 0, -6)}, Glowa=(8, 14, 0), Szczeka=(14, 0, 0),
                  UchoL=(-20, 0, 6), UchoP=(-20, 0, -6))
    w_locie = _z(BAZA, Zad={"przes": (1.0, 0.6, -0.1), "obrot": (0, 12, -10)}, Glowa=(4, -10, 0),
                 Szczeka=(10, 0, 0), Ogon=(6, 0, -20), OgonKoniec=(0, 0, -15), UchoL=(-25, 0, 6),
                 UchoP=(-25, 0, -6), nogi=podkurcz)
    ladowanie = _z(BAZA, Zad={"przes": (1.8, -0.25, -0.1), "obrot": (3, 16, 5)}, Glowa=(10, -18, 0),
                   Szczeka=(18, 0, 0), Ogon=(0, 0, -12), UchoL=(-20, 0, 6), UchoP=(-20, 0, -6))
    stoi = _z(ladowanie, Zad={"przes": (1.8, -0.08, -0.1), "obrot": (1, 14, 2)}, Glowa=(8, -16, 0),
              Szczeka=(8, 0, 0))
    powrot = _z(BAZA, Zad={"przes": (0.8, 0.4, -0.05), "obrot": (0, 5, 8)}, Glowa=(6, -6, 0), nogi=podkurcz)
    ladow2 = _z(BAZA, Zad={"przes": (0.0, -0.18, 0), "obrot": (2, 0, 3)}, Glowa=(8, 0, 0))
    _sekwencja(k, (0, 4, 8, 12, 16, 20, 24, dl), (BAZA, przysiad, w_locie, ladowanie, stoi, powrot, ladow2, BAZA))
    return k


def upadek(p, dl=56):
    """Pokonanie (1,9 s): chwieje się z opuszczonym łbem, przednie łapy się uginają (pada na pierś), zad osiada,
    przewraca się na prawy bok i leży z bezwładnie opadłymi łapami i zamkniętymi oczami (ostatnia klatka do
    utrzymania)."""
    k = p.klip("upadek", dl, petla=False)
    chwiej = _z(BAZA, Zad={"przes": (0, -0.05, -0.15), "obrot": (-3, 6, -4)}, Glowa=(-12, -10, -8),
                Szczeka=(22, 0, 0), UchoL=(-30, 0, 20), UchoP=(-30, 0, -20), Ogon=(-25, 0, 0),
                nogi={"PL": ("z", -0.1, 0.0)})
    piers = _z(BAZA, Zad={"przes": (0, -0.55, -0.1), "obrot": (12, 0, -4)}, Klatka=(10, 0, 0), Glowa=(24, -6, 0),
               Szczeka=(14, 0, 0), UchoL=(-30, 0, 30), UchoP=(-30, 0, -30), Ogon=(-30, 0, 0),
               nogi={"PL": ("k", 40, -95, 55), "PP": ("k", 38, -90, 52)})
    osiada = _z(piers, Zad={"przes": (0, -1.2, -0.1), "obrot": (6, 0, 30)}, Klatka=(8, 0, 0), Glowa=(16, 0, -10),
                nogi={"PL": ("k", 40, -95, 55), "PP": ("k", 38, -90, 52), "TL": ("k", -25, 30, -10),
                      "TP": ("k", -25, 30, -10)}, lez=True)
    # łapy bezwładnie podkurczone (nie sztywne jak u przewróconej zabawki): górne mocniej, dolne prawie proste
    # górne (lewe) łapy opadają ku ziemi (rz < 0 = w stronę prawego boku, który leży na ziemi), zamiast sterczeć
    bok = {"PL": ("k", (-32, 0, -24), 52, 12), "PP": ("k", (-14, 0, -6), 30, 6), "TL": ("k", (-18, 0, -22), 28, 0),
           "TP": ("k", (2, 0, -6), 16, 0)}
    lezy = _z(BAZA, Zad={"przes": (0, 0, -0.1), "obrot": (0, 0, 88)}, Klatka=(0, 0, 2), Glowa=(4, 0, 6),
              Szczeka=(18, 0, 0), UchoL=(-30, 0, 10), UchoP=(-30, 0, -10), Ogon=(0, 0, 10), OgonKoniec=(0, 0, 8),
              nogi=bok, lez=True)
    odbicie = _z(lezy, Zad={"przes": (0, 0, -0.1), "obrot": (0, 0, 80)}, Glowa=(-2, 0, 0), lez=True)
    koniec = _z(lezy, Powieki={"przes": ZAMKNIETE}, Szczeka=(14, 0, 0))
    _sekwencja(k, (0, 6, 14, 24, 32, 36, 42, 48, dl), (BAZA, chwiej, piers, osiada, lezy, odbicie, lezy, koniec, koniec))
    return k


def ryk(p, dl=60):
    """Wycie po wygranej (pętla 2 s): łeb zadarty do nieba, paszcza otwarta, uszy lekko położone, ogon uniesiony;
    dwa „pociągnięcia” wycia na pętlę (łeb i żuchwa pulsują)."""
    k = p.klip("ryk", dl, petla=True)
    h = _z(BAZA, Zad={"przes": (0, -0.06, -0.05), "obrot": (-4, 0, 0)}, Klatka=(-3, 0, 0), Glowa=(-46, 0, 0),
           Szczeka=(26, 0, 0), UchoL=(-12, 0, 6), UchoP=(-12, 0, -6), Ogon=(22, 0, 0), OgonKoniec=(14, 0, 0))
    g1 = _z(h, Glowa=(-54, 5, 0), Szczeka=(38, 0, 0), Ogon=(26, 0, 6), OgonKoniec=(18, 0, 6),
            Zad={"przes": (0, -0.03, -0.05), "obrot": (-5, 0, 0)})
    g2 = _z(h, Glowa=(-54, -5, 0), Szczeka=(38, 0, 0), Ogon=(26, 0, -6), OgonKoniec=(18, 0, -6),
            Zad={"przes": (0, -0.03, -0.05), "obrot": (-5, 0, 0)})
    _sekwencja(k, (0, 15, 30, 45, dl), (h, g1, h, g2, h))
    return k
