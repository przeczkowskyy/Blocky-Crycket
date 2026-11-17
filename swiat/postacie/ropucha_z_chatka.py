# -*- coding: utf-8 -*-
"""ROPUCHA Z CHATKĄ — rzadki przeciwnik Bagna (Leże Ropuchy): ogromna stara ropucha z krzywą chatką z desek na
grzbiecie, ok. 11 studów z kominem i 12 szerokości (gracz ma 5,7).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/ropucha_z_chatka.py --wyj <folder> --klip umiejetnosc

Opis z planu Bagna (swiat/bagno_pas/README.md, rozdz. „Potwory”): ogromna stara ropucha z krzywą chatką na
grzbiecie; z komina bucha dym. Klasa: Mag (rzadka). Dym z komina truje i spowalnia (umiejętność silnika
`chmura_zarodnikow`), skok rani fizycznie (`uderzenie_z_gory`).

Sylwetka (z daleka): szeroka, płaska, ciemnooliwkowa ropucha w brodawkach, a na jej grzbiecie wysoka, przekrzywiona
chatka z desek z dwuspadowym dachem porośniętym mchem i krzywym kamiennym kominem; z przodu chatki świeci ciepło
okienko (Neon), z komina wznoszą się kłęby dymu. Łeb szeroki, oczy mniejsze niż u Rechotka, z ciężkimi, opadającymi
powiekami (stara, znudzona), szeroka szara broda pod pyskiem, worek pod gardłem.

Model jest budowany w „jednostkach ropuchy” (ok. 1/2,9 studa) i skalowany przez `skala=2.9` (kości, bryły, zaczepy
i przesunięcia w klipach skalują się razem).

Paleta: ciemna oliwka 5F6E30 w plamy 3E4A22, brodawki 76843C, brzuch C9B97A, oczy D9822A, deski 9C7A4A (trzy odcienie),
dach 5E4B3A z mchem A9B48E, kamień komina, dym B8BEA8, okienko FFB84A (Neon).

Szkielet (typ „stwor”; L = lewa = +X, P = prawa = −X):
    Root > Cialo > {Glowa > Szczeka > Wole, LapaPL > DlonPL, LapaPP > DlonPP,
                    UdoL > GolenL > StopaL, UdoP > GolenP > StopaP, Chata > {Dym0, Dym1, Dym2}}
- `Chata` kołysze się na grzbiecie (z opóźnieniem za ropuchą) i zsuwa się w upadku;
- Dym0…Dym2 = trzy kłęby dymu; w spoczynku schowane w kominie, w klipach wznoszą się z komina (KominAttachment).

Klipy (30 kl./s; patrzy w +Z):
  idle (pętla 2,4 s: oddech, worek pod brodą, kłęby dymu jeden po drugim), ruch (pętla 1,2 s: ciężki sus w miejscu),
  atak (plaśnięcie prawą łapą przed siebie, trafienie kl. 16, 1,0 s), umiejetnosc (chmura: wdech, nadęty worek,
  szarpnięcie całym ciałem i komin wyrzuca wielki kłąb kl. 30, 2,0 s), skok (uderzenie z góry: ciężkie przyczajenie,
  wybicie, plaśnięcie brzuchem kl. 34, chatka podskakuje; 2,0 s), trafienie (0,67 s), unik (ciężki sus w lewo 1,6
  studa i powrót, 1,0 s), upadek (zatacza się, plaśnięcie z rozjechanymi łapami, przechył na bok, chatka zsuwa się
  i przekrzywia, dym gaśnie, zapada się w błoto; 2 s), ryk (pętla 2 s: staje dęba z otwartym pyskiem i nadętym
  workiem, komin bucha).
Klipy są zapisane jako pozy kluczowe zamienione na klucz w KAŻDEJ klatce (wygładzanie „liniowo”).
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Postac, katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor

ID = "ropucha_z_chatka"
SKALA = 2.9

PALETA = {
    "oliwka": "5F6E30", "plama": "3E4A22", "brodawka": "76843C",
    "brzuch": "C9B97A", "brzuch_cien": "A8995E", "broda": "8E9277",
    "oko": "D9822A", "powieka": "4E5B27", "tusz": "1C1912", "bialy": "F2F0E6",
    "paszcza": "6A2C26", "palce": "8C9650",
    "deska": "9C7A4A", "deska_jasna": "B8955E", "deska_ciemna": "6E5233", "belka": "54402A",
    "dach": "5E4B3A", "mech": "A9B48E", "kamien": "7A766C", "kamien_ciemny": "57544D", "sadza": "201D19",
    "okno": "FFB84A", "dym": "B8BEA8", "dym_jasny": "D6DACB", "sznur": "4A3B2A",
}

CHWILE = {"atak": 16, "umiejetnosc": 30, "skok": 34, "trafienie": 4, "unik": 14}

SLABOSCI = [
    "Kości Ropuchy nie są R15 (własny szkielet: Root + 18 kości) — import do Roblox Studio nie był testowany.",
    "Dym to trzy sztywne kłęby (po trzy kule) na własnych kościach: wznoszą się z komina i wracają do niego skokiem "
    "(w spoczynku są schowane w kominie); nie rozpraszają się ani nie bledną — w grze warto dołożyć cząsteczki na "
    "KominAttachment.",
    "Chmurę trucizny do celu robi odtwarzacz (styl „chmura” z punktu Pocisk = KominAttachment); klip daje tylko "
    "wyrzut z komina.",
    "Łuk skoku w klipie `skok` robi odtwarzacz (styl „skok”); klip podnosi ropuchę najwyżej o ok. 1 stud.",
    "Okienko świeci materiałem Neon (bez PointLight). Chatka nie ma wnętrza.",
    "Sus (ruch) jest w miejscu — stopy w podporze ślizgają się po ziemi.",
]

# ----------------------------------------------------------------------------------------------- szkielet (jednostki)
CIALO = (0.0, 0.95, -0.3)
GLOWA = (0.0, 1.3, 0.5)
SZCZEKA = (0.0, 1.25, 0.45)
WOLE = (0.0, 0.95, 0.85)
BARK = (0.95, 0.95, 0.55)
NADGARSTEK = (1.15, 0.2, 0.9)
BIODRO = (0.95, 0.9, -1.1)
KOLANO = (1.45, 0.72, 0.2)
PIETA = (1.55, 0.28, -1.0)
CHATA = (0.0, 1.78, -0.62)          # środek podłogi chatki na grzbiecie
CHATA_OBROT = (-4.0, 7.0, 4.0)      # krzywo: lekko w tył, skręcona i przechylona w lewo
KOMIN = (-0.5, 1.95, -0.32)          # wierzch komina w układzie chatki

GLOWNA = "Cialo"
PLASKIE = ("DlonPL", "DlonPP", "StopaL", "StopaP")
POMIN_ZIEMIA = ("Dym0", "Dym1", "Dym2", "Chata")


def _lu(v, zn):
    return (zn * v[0], v[1], v[2])


def _chata_pkt(lok):
    """Punkt z układu chatki -> układ modelu (spoczynek)."""
    q = razy_wektor(macierz_obrotu(*CHATA_OBROT), lok)
    return tuple(CHATA[i] + q[i] for i in range(3))


def _os_kosci():
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
    p = Postac(ID, "Ropucha z Chatką", typ="stwor", skala=SKALA, faza=0.03, paleta=PALETA)

    p.kosc("Cialo", "Root", staw=CIALO, dl=0.6)
    p.kosc("Glowa", "Cialo", staw=GLOWA, dl=0.5)
    p.kosc("Szczeka", "Glowa", staw=SZCZEKA, dl=0.4)
    p.kosc("Wole", "Szczeka", staw=WOLE, dl=0.25)
    for s, zn in (("L", 1.0), ("P", -1.0)):
        p.kosc("LapaP" + s, "Cialo", staw=_lu(BARK, zn), dl=0.4)
        p.kosc("DlonP" + s, "LapaP" + s, staw=_lu(NADGARSTEK, zn), dl=0.2)
        p.kosc("Udo" + s, "Cialo", staw=_lu(BIODRO, zn), dl=0.5)
        p.kosc("Golen" + s, "Udo" + s, staw=_lu(KOLANO, zn), dl=0.4)
        p.kosc("Stopa" + s, "Golen" + s, staw=_lu(PIETA, zn), dl=0.3)
    p.kosc("Chata", "Cialo", staw=CHATA, dl=0.5)
    for i in range(3):
        p.kosc("Dym%d" % i, "Chata", staw=_chata_pkt(KOMIN), dl=0.2)

    _tulow(p)
    _glowa(p)
    _paszcza(p)
    _lapy(p)
    _chata(p)
    _dym(p)

    p.zaczep("RootAttachment", "Cialo", (-CIALO[0], -CIALO[1], -CIALO[2]))
    p.zaczep("GlowaAttachment", "Glowa", (0.0, 0.25, 0.4))
    p.zaczep("KominAttachment", "Chata", tuple(_chata_pkt(KOMIN)[i] - CHATA[i] for i in range(3)))
    # czubki palców prawej przedniej łapy (plaśnięcie) — Bron
    p.zaczep("LapaAttachment", "DlonPP", (-0.07, -0.15, 0.62))

    _klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return p


# ---------------------------------------------------------------------------------------------------- bryły
def _tulow(p):
    with _model(p, "Cialo"):
        with p.uklad(pos=(0, 1.0, -0.45), obrot=(-7, 0, 0)):
            p.blok("Tulow", (0, 0, 0), (2.55, 1.15, 2.35), "oliwka", faza=0.12)
            p.blok("Grzbiet", (0, 0.65, 0.03), (2.15, 0.3, 2.05), "oliwka", faza=0.08)
            p.blok("Zad", (0, -0.05, -1.27), (2.1, 0.9, 0.3), "oliwka", faza=0.1)
            for zn in (1, -1):
                p.blok("Plama bok", (zn * 1.29, 0.1, -0.7), (0.04, 0.4, 0.7), "plama", "matowy", faza=0.0)
                p.blok("Plama bok przod", (zn * 1.29, 0.25, 0.4), (0.04, 0.3, 0.4), "plama", "matowy", faza=0.0)
                p.blok("Plama tyl", (zn * 0.55, 0.05, -1.435), (0.45, 0.36, 0.04), "plama", "matowy", faza=0.0)
                p.blok("Brzuch bok", (zn * 1.29, -0.42, -0.2), (0.04, 0.24, 1.8), "brzuch", "matowy", faza=0.0)
                # sznury, którymi chatka jest przywiązana do grzbietu
                p.blok("Sznur", (zn * 1.29, 0.2, -0.15), (0.04, 0.95, 0.07), "sznur", "matowy", rot=(0, 0, 0),
                       faza=0.0)
            # brodawki (stara ropucha)
            for i, (x, y, z) in enumerate(((1.05, 0.62, 0.7), (-1.08, 0.6, 0.5), (1.12, 0.5, -0.9), (-1.1, 0.55, -1.0),
                                           (0.75, 0.82, 0.85), (-0.7, 0.82, 0.9), (1.29, -0.1, 0.0),
                                           (-1.29, -0.05, -0.3), (1.29, 0.3, -1.1), (-1.29, 0.35, 0.95),
                                           (0.2, 0.0, -1.43), (-0.35, -0.25, -1.43))):
                if abs(x) > 1.2:
                    sz = (0.1, 0.16, 0.16)
                elif abs(z) > 1.4:
                    sz = (0.16, 0.16, 0.1)
                else:
                    sz = (0.18, 0.12, 0.18)
                p.blok("Brodawka %d" % i, (x, y, z), sz, "brodawka", faza=0.02)
        p.blok("Brzuch", (0, 0.55, 0.05), (2.1, 0.5, 1.65), "brzuch", faza=0.1)
        for zn in (1, -1):
            p.blok("Gruczol", (zn * 0.75, 1.82, 0.32), (0.5, 0.24, 0.72), "plama", faza=0.06)
            p.blok("Gruczol brodawka", (zn * 0.75, 1.96, 0.36), (0.16, 0.06, 0.16), "brodawka", faza=0.0)


def _glowa(p):
    with _model(p, "Glowa"):
        p.blok("Leb", (0, 1.62, 1.07), (2.7, 0.7, 1.45), "oliwka", faza=0.1)
        p.blok("Leb gora", (0, 2.05, 1.0), (2.2, 0.18, 1.15), "oliwka", faza=0.06)
        p.blok("Plama leb", (0.3, 2.15, 1.25), (0.42, 0.03, 0.32), "plama", "matowy", faza=0.0)
        p.blok("Usta", (0, 1.29, 1.815), (2.6, 0.07, 0.05), "tusz", faza=0.0)
        for i, (x, z) in enumerate(((0.55, 1.5), (-0.7, 1.35), (0.95, 0.75), (-0.2, 0.62))):
            p.blok("Brodawka leb %d" % i, (x, 2.16, z), (0.14, 0.06, 0.14), "brodawka", faza=0.0)
        for zn in (1, -1):
            p.blok("Usta bok", (zn * 1.365, 1.29, 1.12), (0.05, 0.07, 1.3), "tusz", faza=0.0)
            p.blok("Kacik", (zn * 1.365, 1.24, 0.42), (0.05, 0.07, 0.34), "tusz", rot=(-22, 0, 0), faza=0.0)
            p.blok("Nozdrze", (zn * 0.34, 1.84, 1.815), (0.13, 0.07, 0.05), "tusz", faza=0.0)
            # oczy mniejsze niż u Rechotka, z ciężkimi opadającymi powiekami
            x = zn * 0.78
            p.walec("Oko kopula", (x, 2.18, 0.95), (0.62, 0.32, 0.62), "oliwka", segm=8)
            p.kula("Oko", (x, 2.38, 1.0), 0.52, "oko", "polysk", segm=8)
            p.blok("Zrenica", (x, 2.33, 1.26), (0.26, 0.07, 0.05), "tusz", "polysk", faza=0.0)
            p.blok("Powieka", (x, 2.53, 1.0), (0.62, 0.26, 0.62), "powieka", faza=0.05)
            p.blok("Powieka brzeg", (x, 2.42, 1.27), (0.5, 0.06, 0.06), "plama", "matowy", rot=(0, 0, -zn * 6),
                   faza=0.0)
        p.blok("Podniebienie", (0, 1.29, 1.1), (2.4, 0.04, 1.25), "paszcza", "matowy", faza=0.0)


def _paszcza(p):
    with _model(p, "Szczeka"):
        p.blok("Zuchwa", (0, 1.08, 1.1), (2.6, 0.36, 1.38), "oliwka", faza=0.08)
        p.blok("Gardlo", (0, 0.88, 1.05), (2.3, 0.1, 1.2), "brzuch", "matowy", faza=0.02)
        p.blok("Wnetrze", (0, 1.25, 1.1), (2.4, 0.04, 1.25), "paszcza", "matowy", faza=0.0)
        # obwisła skóra pod pyskiem (stara ropucha): dwa fałdy
        p.blok("Falda", (0, 0.86, 1.6), (2.1, 0.12, 0.1), "plama", "matowy", faza=0.02)
        p.blok("Falda 2", (0, 0.92, 1.5), (1.4, 0.06, 0.08), "brzuch_cien", "matowy", faza=0.0)
    with _model(p, "Wole"):
        p.blok("Wole", (0, 0.8, 0.95), (1.7, 0.42, 0.95), "brzuch", faza=0.12)
        p.blok("Wole cien", (0, 0.72, 1.43), (1.3, 0.2, 0.04), "brzuch_cien", "matowy", faza=0.0)


def _lapy(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        with _model(p, "LapaP" + s):
            _belka(p, "Ramie", _lu((0.95, 1.05, 0.55), zn), _lu(NADGARSTEK, zn), 0.46, 0.46, "oliwka")
            p.blok("Brodawka ramie", _lu((1.27, 0.6, 0.78), zn), (0.08, 0.12, 0.12), "brodawka", faza=0.0)
        with _model(p, "DlonP" + s):
            p.blok("Dlon", _lu((1.2, 0.07, 1.0), zn), (0.6, 0.14, 0.55), "oliwka", faza=0.04)
            for i, (x, z, ry) in enumerate(((0.98, 1.34, -25), (1.22, 1.4, 0), (1.46, 1.32, 25))):
                p.blok("Palec %d" % i, _lu((x, 0.05, z), zn), (0.14, 0.1, 0.38), "palce", rot=(0, zn * ry, 0),
                       faza=0.02)
        with _model(p, "Udo" + s):
            sr, rot = _belka(p, "Udo", _lu(BIODRO, zn), _lu(KOLANO, zn), 0.95, 0.85, "oliwka", nad=0.25,
                             ksztalt="kula")
            with p.uklad(pos=sr, obrot=rot):
                p.blok("Plama uda", (zn * 0.44, 0.1, 0.0), (0.04, 0.35, 0.4), "plama", "matowy", faza=0.0)
                p.blok("Brodawka uda", (zn * 0.4, -0.35, 0.15), (0.08, 0.14, 0.14), "brodawka", faza=0.0)
        with _model(p, "Golen" + s):
            _belka(p, "Golen", _lu(KOLANO, zn), _lu(PIETA, zn), 0.52, 0.47, "oliwka", nad=0.08)
        with _model(p, "Stopa" + s):
            p.blok("Pieta", _lu((1.55, 0.18, -1.0), zn), (0.42, 0.3, 0.38), "oliwka", faza=0.06)
            p.blok("Stopa", _lu((1.62, 0.06, -0.35), zn), (0.52, 0.12, 1.3), "oliwka", rot=(0, zn * 8, 0), faza=0.03)
            for i, (x, z, ry) in enumerate(((1.48, 0.45, -12), (1.72, 0.52, 5), (1.92, 0.4, 25))):
                p.blok("Palec stopy %d" % i, _lu((x, 0.045, z), zn), (0.13, 0.09, 0.55), "palce",
                       rot=(0, zn * ry, 0), faza=0.02)


def _gable(p, nazwa, z, gora, szer, kolor):
    """Szczyt dachu (trójkąt) z dwóch klinów w płaszczyźnie XY na głębokości z."""
    for zn, ry in ((1, -90), (-1, 90)):
        p.klin(nazwa, (zn * szer / 4.0, gora[0] + (gora[1] - gora[0]) / 2.0, z), (0.05, gora[1] - gora[0], szer / 2.0),
               kolor, "matowy", rot=(0, ry, 0), faza=0.0)


def _chata(p):
    with _model(p, "Chata"), p.uklad(pos=CHATA, obrot=CHATA_OBROT):
        # podłoga z desek i belki pod nią
        p.blok("Podloga", (0, 0.0, 0), (1.75, 0.07, 1.55), "deska_ciemna", "matowy", faza=0.01)
        for i, z in enumerate((-0.55, 0.0, 0.55)):
            p.blok("Belka podlogi %d" % i, (0, -0.06, z), (1.9, 0.08, 0.1), "belka", "matowy", faza=0.0)
        # ściany z desek, narożne słupy, linie desek
        p.blok("Sciany", (0, 0.52, 0), (1.45, 0.95, 1.25), "deska", "matowy", faza=0.02)
        for x in (-0.72, 0.72):
            for z in (-0.62, 0.62):
                p.blok("Slup", (x, 0.52, z), (0.11, 1.02, 0.11), "belka", "matowy", faza=0.0)
        for i, y in enumerate((0.22, 0.46, 0.7)):
            p.blok("Deski przod %d" % i, (0, y, 0.632), (1.44, 0.025, 0.02), "deska_ciemna", "matowy", faza=0.0)
            p.blok("Deski tyl %d" % i, (0, y, -0.632), (1.44, 0.025, 0.02), "deska_ciemna", "matowy", faza=0.0)
            for zn in (1, -1):
                p.blok("Deski bok %d" % i, (zn * 0.732, y, 0), (0.02, 0.025, 1.24), "deska_ciemna", "matowy",
                       faza=0.0)
        p.blok("Deska jasna", (-0.3, 0.33, 0.636), (0.5, 0.2, 0.02), "deska_jasna", "matowy", rot=(0, 0, 4), faza=0.0)
        p.blok("Deska jasna bok", (0.736, 0.6, -0.3), (0.02, 0.2, 0.45), "deska_jasna", "matowy", faza=0.0)
        # okienko z przodu (świeci) i na lewym boku
        for nazwa, pos, rozm, rot in (("Okno przod", (0.32, 0.56, 0.64), (0.46, 0.42, 0.04), (0, 0, 3)),
                                      ("Okno bok", (0.74, 0.5, 0.18), (0.04, 0.36, 0.4), (0, 0, 0))):
            p.blok(nazwa + " rama", pos, rozm, "belka", "matowy", rot=rot, faza=0.0)
            if rozm[2] < rozm[0]:
                szyba = (pos[0], pos[1], pos[2] + 0.02)
                p.blok(nazwa + " szyba", szyba, (rozm[0] - 0.1, rozm[1] - 0.1, 0.03), "okno", "swiecacy", rot=rot,
                       faza=0.0)
                p.blok(nazwa + " krzyz", (szyba[0], szyba[1], szyba[2] + 0.02), (0.04, rozm[1] - 0.1, 0.02), "belka",
                       "matowy", rot=rot, faza=0.0)
                p.blok(nazwa + " krzyz 2", (szyba[0], szyba[1], szyba[2] + 0.02), (rozm[0] - 0.1, 0.04, 0.02),
                       "belka", "matowy", rot=rot, faza=0.0)
            else:
                szyba = (pos[0] + 0.02, pos[1], pos[2])
                p.blok(nazwa + " szyba", szyba, (0.03, rozm[1] - 0.1, rozm[2] - 0.1), "okno", "swiecacy", faza=0.0)
                p.blok(nazwa + " krzyz", (szyba[0] + 0.02, szyba[1], szyba[2]), (0.02, rozm[1] - 0.1, 0.04), "belka",
                       "matowy", faza=0.0)
        p.blok("Parapet", (0.32, 0.33, 0.67), (0.52, 0.04, 0.08), "deska_jasna", "matowy", faza=0.0)
        # drzwi na prawym boku z klamką i daszkiem
        p.blok("Drzwi", (-0.735, 0.36, -0.1), (0.03, 0.66, 0.42), "deska_ciemna", "matowy", faza=0.0)
        p.blok("Klamka", (-0.76, 0.36, 0.04), (0.04, 0.06, 0.06), "kamien", "metal", faza=0.0)
        p.blok("Prog", (-0.8, 0.04, -0.1), (0.16, 0.05, 0.5), "belka", "matowy", faza=0.0)
        # dach dwuspadowy z kalenicą i mchem
        for zn in (1, -1):
            p.blok("Dach", (zn * 0.43, 1.2, 0), (1.02, 0.08, 1.62), "dach", "matowy", rot=(0, 0, -zn * 33), faza=0.01)
            p.blok("Dach okap", (zn * 0.84, 0.94, 0), (0.12, 0.05, 1.64), "belka", "matowy", rot=(0, 0, -zn * 33),
                   faza=0.0)
        _gable(p, "Szczyt przod", 0.6, (0.98, 1.42), 1.45, "deska")
        _gable(p, "Szczyt tyl", -0.6, (0.98, 1.42), 1.45, "deska")
        p.blok("Kalenica", (0, 1.49, 0), (0.12, 0.1, 1.7), "belka", "matowy", faza=0.0)
        for i, (x, z, sx, sz) in enumerate(((0.45, 0.35, 0.5, 0.6), (-0.4, -0.3, 0.45, 0.7), (0.55, -0.5, 0.3, 0.35))):
            zn = 1 if x > 0 else -1
            p.blok("Mech dach %d" % i, (x, 1.205 + 0.05 - abs(x) * 0.62 + 0.24, z), (sx, 0.05, sz), "mech", "matowy",
                   rot=(0, 0, -zn * 33), faza=0.0)
        # krzywy kamienny komin (z tyłu po prawej, wystaje ponad dach)
        for i, (dx, y, w) in enumerate(((0.0, 0.95, 0.54), (-0.02, 1.25, 0.52), (-0.04, 1.53, 0.5),
                                        (-0.07, 1.78, 0.5))):
            kol = "kamien" if i % 2 == 0 else "kamien_ciemny"
            p.blok("Komin %d" % i, (KOMIN[0] + dx + 0.07, y, KOMIN[2]), (w, 0.3, w), kol, "matowy",
                   rot=(0, 12 * i, 0), faza=0.02)
        p.blok("Komin wieniec", (KOMIN[0], 1.93, KOMIN[2]), (0.58, 0.08, 0.58), "kamien_ciemny", "matowy", faza=0.01)
        p.blok("Komin sadza", (KOMIN[0], 1.975, KOMIN[2]), (0.4, 0.02, 0.4), "sadza", "matowy", faza=0.0)
        # latarenka pod okapem
        p.blok("Latarnia sznur", (0.88, 0.85, 0.55), (0.02, 0.18, 0.02), "sznur", "matowy", faza=0.0)
        p.blok("Latarnia", (0.88, 0.7, 0.55), (0.12, 0.14, 0.12), "okno", "swiecacy", faza=0.0)


def _dym(p):
    """Trzy kłęby dymu (po cztery kule), w spoczynku schowane w kominie (wierzch kul 0,05 pod wieńcem)."""
    for i in range(3):
        with p.na("Dym%d" % i):
            for j, (pos, r) in enumerate((((0.0, -0.3, 0.0), 0.42), ((0.08, -0.17, 0.05), 0.28),
                                          ((-0.08, -0.4, -0.06), 0.3), ((0.05, -0.55, -0.04), 0.32))):
                p.kula("Klab %d %d" % (i, j), pos, r, "dym" if j else "dym_jasny", "matowy", segm=8)


# ---------------------------------------------------------------------------------------------------- klipy
def _nogi(przod=None, udo=None, golen=None, stopa=None, przodP=None, udoP=None, golenP=None, stopaP=None):
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
    out = {}
    for c in czesci:
        out.update(c)
    out.update(kosci)
    return out


def _klab(i, wys, dryf=0.0, bok=0.0):
    """Kłąb Dym<i> wysunięty z komina o `wys` (jednostki), zniesiony w tył o `dryf` i w bok o `bok`."""
    return {"Dym%d" % i: {"p": (bok, wys, -dryf)}}


def _dym_cykl(t, faza, wys=1.1):
    """Kłąb wznosi się z komina przez cały cykl (t 0…1), na końcu wraca do komina."""
    u = (t + faza) % 1.0
    return wys * u, 0.35 * u * u


PRZYSIAD = _nogi(przod=(0.3, -0.55, 0.55), udo=(0.55, -0.02, 1.3), golen=(0.12, -0.3, -1.22))
WYPROST = _nogi(przod=(0.15, -0.85, 0.25), udo=(0.3, -0.8, -0.55), golen=(0.1, -0.75, -0.75),
                stopa=(0.0, -0.75, -0.65))
ROZJECHANE = _nogi(przod=(0.95, -0.22, 0.35), udo=(1.1, -0.12, 0.5), golen=(0.65, -0.18, -0.85))


def _klipy(p):
    idle(p)
    ruch(p)
    atak(p)
    umiejetnosc(p)
    skok(p)
    trafienie(p)
    unik(p)
    upadek(p)
    ryk(p)


def idle(p, dl=72):
    """Spoczynek (2,4 s): ciężki oddech, worek pod brodą, chatka kołysze się z opóźnieniem, trzy kłęby dymu
    wznoszą się z komina jeden po drugim."""
    k = p.klip("idle", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        wole = max(0.0, math.sin(2 * math.pi * t)) ** 2
        pz = {"Cialo": (-1.0 * a, 0, 0), "Glowa": (1.2 * a, 6 * math.sin(2 * math.pi * t + 0.6), 0),
              "Szczeka": (1.0 * wole, 0, 0), "Wole": {"p": (0, -0.1 * wole, 0.05 * wole)},
              "Chata": (0.8 * math.sin(2 * math.pi * t - 0.7), 0, 1.0 * math.sin(2 * math.pi * t - 1.2))}
        for i in range(3):
            w, d = _dym_cykl(t, i / 3.0)
            pz.update(_klab(i, w, d, 0.06 * math.sin(2 * math.pi * (t + i / 3.0))))
        return pz
    _petla(k, poza)
    return k


def ruch(p, dl=36):
    """Ciężki sus w miejscu (1,2 s): przyczajenie, wybicie, krótki lot, lądowanie z bujnięciem chatki."""
    k = p.klip("ruch", dl, petla=True)
    spocz = _z(_klab(0, 0.5, 0.15))
    przys = _z(PRZYSIAD, Cialo=(4, 0, 0), Chata=(-2, 0, 0), **_klab(0, 0.6, 0.2))
    wybicie = _z(WYPROST, Cialo=(-14, 0, 0), Glowa=(-5, 0, 0), Chata=(4, 0, 0), _h=0.1, **_klab(0, 0.7, 0.3))
    lot = _z(_nogi(przod=(0.15, -0.6, 0.75), udo=(0.35, -0.45, -0.8), golen=(0.1, -0.2, -1.0), stopa=(0, -0.3, -1)),
             Cialo=(-3, 0, 0), Chata=(3, 0, 0), _h=0.35, _wolne=True, **_klab(0, 0.85, 0.45))
    ladowanie = _z(_nogi(przod=(0.25, -0.6, 0.55), udo=(0.5, -0.3, 1.0), golen=(0.1, -0.4, -1.2)),
                   Cialo=(7, 0, 0), Glowa=(4, 0, 0), Chata=(-5, 0, 2), _h=0.0, **_klab(0, 0.4, 0.3))
    _sekwencja(k, (0, 6, 12, 19, 26, 36), (spocz, przys, wybicie, lot, ladowanie, spocz),
               wyg={1: "we", 2: "wy", 3: "we"})
    return k


def atak(p, dl=30):
    """Plaśnięcie łapą (1,0 s): ropucha unosi się na tylnych łapach, prawa przednia łapa wysoko w górę, plaśnięcie
    przed siebie w ziemię (kl. 16), chatka podskakuje, powrót."""
    k = p.klip("atak", dl, petla=False)
    spocz = {}
    zamach = _z(_nogi(przod=(0.3, -0.6, 0.5), przodP=(0.2, 0.75, 0.55)), Cialo={"o": (-14, -6, 6), "p": (0, 0, -0.08)},
                Glowa=(-8, -8, 0), Chata=(4, 0, -3), Szczeka=(6, 0, 0))
    plask = _z(_nogi(przod=(0.3, -0.7, 0.4), przodP=(-0.4, -0.45, 0.85)), Cialo={"o": (10, 10, -3), "p": (0, 0, 0.3)},
               Glowa=(8, 4, 0), Chata=(-6, 0, 3), Szczeka=(10, 0, 0))
    dobicie = _z(plask, Chata=(3, 0, -2), Glowa=(6, 4, 0))
    _sekwencja(k, (0, 10, 16, 20, 30), (spocz, zamach, plask, dobicie, spocz), wyg={0: "s", 1: "we", 2: "wy"})
    return k


def umiejetnosc(p, dl=60):
    """Chmura (2,0 s): wdech — ropucha unosi przód, worek pod brodą się nadyma (kl. 0–20), szarpnięcie całym ciałem
    w dół i komin wyrzuca trzy kłęby naraz wysoko i szeroko (kl. 30 = wypuszczenie chmury), potem dym opada."""
    k = p.klip("umiejetnosc", dl, petla=False)
    spocz = {}
    wdech = _z(_nogi(przod=(0.15, -0.85, 0.3)), Cialo=(-10, 0, 0), Glowa=(-8, 0, 0), Wole={"p": (0, -0.24, 0.12)},
               Chata=(3, 0, 0), **_z(_klab(0, 0.15), _klab(1, 0.05), _klab(2, 0.0)))
    wdech2 = _z(wdech, Cialo=(-12, 0, 0), Chata=(4, 0, -2))
    szarp = _z(PRZYSIAD, Cialo=(8, 0, 0), Glowa=(6, 0, 0), Szczeka=(14, 0, 0), Wole={"p": (0, -0.05, 0.02)},
               Chata=(-7, 0, 3), **_z(_klab(0, 0.9, 0.1, 0.15), _klab(1, 0.8, -0.1, -0.2), _klab(2, 0.6, 0.15, 0.0)))
    wybuch = _z(PRZYSIAD, Cialo=(6, 0, 0), Glowa=(4, 0, 0), Szczeka=(10, 0, 0), Chata=(4, 0, -3),
                **_z(_klab(0, 1.7, 0.3, 0.55), _klab(1, 1.6, -0.25, -0.6), _klab(2, 1.5, 0.45, -0.05)))
    opada = _z(Cialo=(2, 0, 0), Chata=(-1, 0, 1),
               **_z(_klab(0, 2.0, 0.6, 0.75), _klab(1, 1.9, 0.0, -0.8), _klab(2, 1.85, 0.8, 0.0)))
    _sekwencja(k, (0, 14, 22, 30, 38, 52, 60),
               (spocz, wdech, wdech2, szarp, wybuch, opada, spocz),
               wyg={2: "we", 3: "wy", 5: "s"})
    return k


def skok(p, dl=60):
    """Uderzenie z góry (2,0 s): ciężkie przyczajenie (kl. 0–14), wybicie (14–19), zwinięcie w locie (19–30),
    plaśnięcie brzuchem z rozjechanymi łapami (kl. 34), chatka podskakuje i bucha dym, powrót na łapy."""
    k = p.klip("skok", dl, petla=False)
    spocz = {}
    przys = _z(_nogi(przod=(0.4, -0.45, 0.6), udo=(0.6, 0.05, 1.3), golen=(0.15, -0.25, -1.22)),
               Cialo=(10, 0, 0), Glowa=(4, 0, 0), Chata=(-3, 0, 0))
    wybicie = _z(WYPROST, Cialo=(-24, 0, 0), Glowa=(-8, 0, 0), Chata=(6, 0, 0), _h=0.2, _wolne=True)
    lot = _z(_nogi(przod=(0.15, -0.45, 0.88), udo=(0.4, 0.15, 1.3), golen=(0.1, -0.15, -1.25), stopa=(0, 0.2, 1)),
             Cialo=(-4, 0, 0), Chata=(-4, 0, 2), _h=0.35, _wolne=True, **_klab(0, 0.3))
    opad = _z(_nogi(przod=(0.55, -0.4, 0.7), udo=(0.8, 0.05, 0.9), golen=(0.4, -0.1, -1.1), stopa=(0.3, 0, 1)),
              Cialo=(12, 0, 0), Glowa=(6, 0, 0), Chata=(4, 0, 0), _h=0.18, _wolne=True, **_klab(0, 0.2))
    plask = _z(ROZJECHANE, Cialo=(3, 0, 0), Glowa=(6, 0, 0), Szczeka=(8, 0, 0), Chata=(-8, 0, 4),
               **_z(_klab(0, 0.7, 0.1, 0.2), _klab(1, 0.5, -0.1, -0.2)))
    plask2 = _z(ROZJECHANE, Cialo=(1, 0, 0), Glowa=(2, 0, 0), Chata=(3, 0, -2),
                **_z(_klab(0, 1.3, 0.3, 0.35), _klab(1, 1.1, 0.1, -0.35), _klab(2, 0.6, 0.2, 0.0)))
    wstaje = _z(PRZYSIAD, Cialo=(-3, 0, 0), Glowa=(-5, 0, 0), Chata=(-1, 0, 0),
                **_z(_klab(0, 1.6, 0.5, 0.45), _klab(1, 1.4, 0.3, -0.45), _klab(2, 1.0, 0.4, 0.0)))
    _sekwencja(k, (0, 14, 19, 26, 32, 34, 42, 51, 60),
               (spocz, przys, wybicie, lot, opad, plask, plask2, wstaje, spocz),
               wyg={1: "l", 2: "wy", 4: "we", 5: "wy"})
    return k


def trafienie(p, dl=20):
    """Szarpnięcie w tył (0,67 s, najdalej kl. 4): łeb w górę, pysk uchylony, chatka chwieje się."""
    k = p.klip("trafienie", dl, petla=False)
    spocz = {}
    szarp = _z(_nogi(przod=(0.2, -0.65, 0.65)), Cialo={"o": (-10, 0, 0), "p": (0, 0, -0.12)}, Glowa=(-10, 0, 0),
               Szczeka=(10, 0, 0), Chata=(-6, 0, 2))
    odbicie = _z(Cialo={"o": (4, 0, 0), "p": (0, 0, -0.04)}, Glowa=(3, 0, 0), Chata=(5, 0, -2))
    _sekwencja(k, (0, 4, 11, 20), (spocz, szarp, odbicie, spocz), wyg={0: "wy"})
    return k


def unik(p, dl=30):
    """Ciężki sus w lewo o ok. 1,6 studa (najdalej kl. 14) i powrót (1,0 s)."""
    k = p.klip("unik", dl, petla=False)
    spocz = {}
    przys = _z(PRZYSIAD, Cialo={"o": (0, 0, -6), "p": (0, 0, 0)}, Chata=(0, 0, 3))
    lot = _z(_nogi(przod=(0.5, -0.6, 0.5), udo=(0.5, -0.4, -0.7), golen=(0.2, -0.3, -1.0), stopa=(0, -0.3, -1)),
             Cialo={"o": (-6, 0, 8), "p": (0.3, 0, 0)}, Chata=(0, 0, -5), _h=0.25, _wolne=True)
    lad = _z(PRZYSIAD, Cialo={"o": (5, 0, 3), "p": (0.55, 0, 0)}, Glowa=(0, -10, 0), Chata=(0, 0, 6))
    lot2 = _z(lot, Cialo={"o": (-5, 0, -6), "p": (0.28, 0, 0)}, Chata=(0, 0, 4), _h=0.18)
    lad2 = _z(PRZYSIAD, Cialo={"o": (4, 0, 0), "p": (0, 0, 0)}, Chata=(0, 0, -3))
    _sekwencja(k, (0, 4, 9, 14, 19, 24, 30), (spocz, przys, lot, lad, lot2, lad2, spocz),
               wyg={1: "wy", 2: "we", 4: "we"})
    return k


def upadek(p, dl=60):
    """Upadek (2 s): zatacza się, ostatni wydech dymu, plaśnięcie z rozjechanymi łapami, przechył na prawy bok,
    chatka przekrzywia się i zsuwa, ropucha zapada się w błoto (kl. 60 = leży)."""
    k = p.klip("upadek", dl, petla=False)
    spocz = {}
    chwiej = _z(_nogi(przod=(0.25, -0.7, 0.5)), Cialo={"o": (-10, 0, 6), "p": (0, 0, -0.1)}, Glowa=(-8, 12, 0),
                Szczeka=(10, 0, 0), Chata=(-4, 0, -6), **_klab(0, 0.6, 0.2))
    chwiej2 = _z(PRZYSIAD, Cialo={"o": (5, -8, -6), "p": (0.04, 0, -0.06)}, Glowa=(12, -8, 0), Szczeka=(4, 0, 0),
                 Chata=(3, 0, 8), **_klab(0, 0.9, 0.35))
    plask = _z(ROZJECHANE, Cialo={"o": (5, -5, -4), "p": (0, 0, 0)}, Glowa=(10, 0, 0), Szczeka=(12, 0, 0),
               Chata=(-6, 0, -4), **_klab(0, 1.1, 0.5))
    bok = _z(_nogi(przod=(0.9, 0.1, 0.4), udo=(1.0, 0.25, 0.5), golen=(0.6, 0.1, -0.85),
                   przodP=(0.9, -0.3, 0.3), udoP=(1.0, -0.15, 0.45), golenP=(0.6, -0.2, -0.85)),
             Cialo={"o": (3, -6, -24), "p": (0, 0, 0)}, Glowa=(14, 0, -5), Szczeka=(18, 0, 0),
             Chata={"o": (-8, 10, -14), "p": (-0.18, -0.06, 0.05)}, _wolne=True)
    bloto = _z(bok, _h=-0.12)
    _sekwencja(k, (0, 9, 18, 28, 38, 60), (spocz, chwiej, chwiej2, plask, bok, bloto),
               wyg={2: "we", 3: "wy", 5: "l"})
    return k


def ryk(p, dl=60):
    """Ryk po wygranej (pętla 2 s): staje dęba na przednich łapach, pysk szeroko, worek pod brodą nadęty, chatka
    się trzęsie, komin bucha kłębami; potem ciężko opada."""
    k = p.klip("ryk", dl, petla=True)

    def poza(t):
        s = math.sin(math.pi * t) ** 2                      # 0 → 1 → 0
        drz = math.sin(12 * math.pi * t) * s
        pz = _z(_nogi(przod=(0.15, -0.85 + 0.1 * s, 0.3 - 0.25 * s)),
                {"Cialo": (-16 * s, 0, 2 * drz), "Glowa": (-14 * s, 0, 0), "Szczeka": (34 * s, 0, 0),
                 "Wole": {"p": (0, -0.28 * s, 0.14 * s)}, "Chata": (3 * drz, 0, 4 * drz)})
        for i in range(3):
            w, d = _dym_cykl(t, i / 3.0, wys=1.6)
            pz.update(_klab(i, w, d, 0.1 * math.sin(2 * math.pi * (t + i / 3.0))))
        return pz
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
