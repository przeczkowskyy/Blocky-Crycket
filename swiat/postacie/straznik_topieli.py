# -*- coding: utf-8 -*-
"""STRAŻNIK TOPIELI — strażnik Bagna (Topiel Strażnika): olbrzym z błota i korzeni wynurzony z wody, ok. 16 studów
z łódką-kapeluszem i ok. 10 szerokości (gracz ma 5,7).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/straznik_topieli.py --wyj <folder> --klip ryk

Opis z planu Bagna (swiat/bagno_pas/README.md, rozdz. „Potwory”): olbrzym z błota i korzeni wynurzony z wody,
przewrócona łódka jak kapelusz, w piersi zielona latarnia, broda z mchu. Strażnik biomu (pół na pół: fizyczne
i magiczne). Umiejętność silnika `ogluszajace_uderzenie` = oburęczne uderzenie w taflę (fala).

Sylwetka (z daleka): przygarbiony kolos o szerokich, błotnych barkach i bardzo długich rękach z korzeni (pięści-sęki
wiszą nisko, tuż nad kolanami), krótkie, grube nogi w spódnicy z wodorostów; na głowie szeroka, przewrócona do góry
dnem płaskodenna łódka z wypłowiałym turkusowym pasem i wiosłem sterczącym w tył — z przodu wygląda jak wielki
kapelusz. W piersi, w klatce z korzeni, świeci zielona latarnia (Neon); zielone są też szparki oczu i poświata
w gardle przy ryku. Broda z mchu do połowy piersi, na barkach mech, trzcina i liść grzybienia z fioletowym kwiatem.
Nogi i dłonie do wysokości ok. 2 studów ciemniejsze — mokre od wody.

Paleta: błoto 5B4A34 (trzy odcienie, ciemne mokre 3A3226), korzenie 4A3824, mech A9B48E, wodorosty, drewno łódki
8A6E4A z pasem 4E7A74, latarnia i oczy C8E05A (Neon), mosiądz latarni, kwiat 8C5A9E.

Szkielet (typ „stwor”; L = lewa = +X, P = prawa = −X):
    Root > Biodra > {Tulow > {Glowa > {Lodz, Broda}, Latarnia, RamieL > PrzedramieL > DlonL,
                              RamieP > PrzedramieP > DlonP},
                     NogaL > StopaL, NogaP > StopaP}
- `Biodra` niesie całego olbrzyma; Stopa* trzymane płasko na ziemi (liczone w module);
- `Broda` to żuchwa z brodą z mchu (otwiera paszczę przy ryku, w paszczy zielona poświata);
- `Lodz` (kapelusz) kołysze się z opóźnieniem i spada z głowy w upadku; `Latarnia` buja się w klatce.

Klipy (30 kl./s; patrzy w +Z):
  idle (pętla 2,4 s: ciężki oddech, latarnia się buja, łódka i broda kołyszą się), ruch (pętla 2,0 s: brnie przez
  wodę, ciężkie kroki), atak (cios pięścią z korzeni z prawego barku w dół przed siebie, trafienie kl. 18, 1,2 s),
  umiejetnosc (ogłuszające uderzenie: obie pięści nad głowę i uderzenie w taflę przed sobą kl. 38, 2,2 s),
  trafienie (0,67 s), unik (ciężki krok w lewo 1,5 studa i powrót, 1,0 s), upadek (zatacza się, łódka spada z głowy,
  pada na plecy i zapada się w topiel; 2,2 s, leży w ostatniej klatce), ryk (dokładnie 60 klatek = 2,0 s, pętla:
  staje wyprostowany z rozłożonymi rękami, paszcza otwarta, drży — gra go przelot kamery).
Klipy są zapisane jako pozy kluczowe zamienione na klucz w KAŻDEJ klatce (wygładzanie „liniowo”).
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Postac, katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor

ID = "straznik_topieli"

PALETA = {
    "bloto": "5B4A34", "bloto_jasne": "75603F", "bloto_ciemne": "45372A", "mokre": "3A3226",
    "korzen": "4A3824", "korzen_jasny": "6B5236",
    "mech": "A9B48E", "mech_ciemny": "7F8C62", "wodorost": "3E5A3E", "wodorost_jasny": "5E7A4A",
    "lodz": "8A6E4A", "lodz_ciemna": "5E4A32", "lodz_jasna": "A8885C", "farba": "4E7A74",
    "latarnia": "C8E05A", "mosiadz": "6A5A3A", "tusz": "16130E", "gardlo": "1E2A20",
    "trzcina": "B59A52", "palka": "5E3F26", "lisc": "5C8A3A", "kwiat": "8C5A9E", "kwiat_srodek": "E8D27A",
}

CHWILE = {"atak": 18, "umiejetnosc": 38, "trafienie": 4, "unik": 14}

SLABOSCI = [
    "Kości Strażnika nie są R15 (własny szkielet: Root + 16 kości) — import do Roblox Studio nie był testowany.",
    "Nogi są jednoczęściowe (bez kolan): krok to wymach całej nogi i kołysanie bioder; w podporze stopy ślizgają się.",
    "Fali na wodzie przy ogłuszającym uderzeniu nie ma w klipie — robi ją odtwarzacz (fala, wstrząs kamery).",
    "Świecenie latarni, oczu i gardła: materiał Neon na rigu z klocków; PointLight trzeba dodać w Studio.",
    "Bryły są sztywno przypięte do kości: przy mocnym zgięciu tułowia barki i broda lekko wchodzą w siebie.",
    "W upadku łódka zsuwa się z głowy i ląduje obok (liczone w przybliżeniu, bez fizyki); olbrzym zapada się "
    "do połowy pod poziom ziemi (topiel) — w grze ziemia/woda musi to zasłonić.",
]

# ----------------------------------------------------------------------------------------------- szkielet (studs)
BIODRA = (0.0, 4.6, 0.0)
TULOW = (0.0, 5.8, 0.0)
GLOWA = (0.0, 11.3, 1.1)
LODZ = (0.0, 13.55, 1.45)
BRODA = (0.0, 11.75, 2.35)          # zawias żuchwy z brodą
LATARNIA = (0.0, 9.75, 2.05)        # zaczep latarni w klatce (buja się)
BARK = (3.6, 10.2, 0.3)
LOKIEC = (4.2, 7.0, 0.9)
NADGARSTEK = (4.3, 4.0, 1.3)
BIODRO = (1.5, 4.5, 0.0)
KOSTKA = (1.7, 1.0, 0.2)
PIESC = (4.35, 3.05, 1.55)          # środek pięści-sęka
SWIATLO = (0.0, 8.85, 2.3)          # środek świecącego rdzenia latarni (spoczynek)

GLOWNA = "Biodra"
PLASKIE = ("StopaL", "StopaP")
POMIN_ZIEMIA = ("Lodz", "Broda", "DlonL", "DlonP", "PrzedramieL", "PrzedramieP")


def _lu(v, zn):
    return (zn * v[0], v[1], v[2])


def _roznica(a, b):
    return tuple(b[i] - a[i] for i in range(3))


def _os_kosci():
    o = {}
    for s, zn in (("L", 1.0), ("P", -1.0)):
        o["Ramie" + s] = _roznica(_lu(BARK, zn), _lu(LOKIEC, zn))
        o["Przedramie" + s] = _roznica(_lu(LOKIEC, zn), _lu(NADGARSTEK, zn))
        o["Noga" + s] = _roznica(_lu(BIODRO, zn), _lu(KOSTKA, zn))
    return o


OS = _os_kosci()


def _model(p, kosc, obrot=(0, 0, 0), pos=(0, 0, 0)):
    """Układ MODELU (0, 0, 0 = ziemia pod środkiem) na kości: bryły podaje się we współrzędnych modelu."""
    s = p.staw(kosc)
    return p.na(kosc, pos=(pos[0] - s[0], pos[1] - s[1], pos[2] - s[2]), obrot=obrot)


def zbuduj():
    p = Postac(ID, "Strażnik Topieli", typ="stwor", skala=1.0, faza=0.08, paleta=PALETA)

    p.kosc("Biodra", "Root", staw=BIODRA, dl=1.0)
    p.kosc("Tulow", "Biodra", staw=TULOW, dl=1.5)
    p.kosc("Glowa", "Tulow", staw=GLOWA, dl=1.0)
    p.kosc("Lodz", "Glowa", staw=LODZ, dl=0.8)
    p.kosc("Broda", "Glowa", staw=BRODA, dl=0.6)
    p.kosc("Latarnia", "Tulow", staw=LATARNIA, dl=0.5)
    for s, zn in (("L", 1.0), ("P", -1.0)):
        p.kosc("Ramie" + s, "Tulow", staw=_lu(BARK, zn), dl=1.2)
        p.kosc("Przedramie" + s, "Ramie" + s, staw=_lu(LOKIEC, zn), dl=1.2)
        p.kosc("Dlon" + s, "Przedramie" + s, staw=_lu(NADGARSTEK, zn), dl=0.8)
        p.kosc("Noga" + s, "Biodra", staw=_lu(BIODRO, zn), dl=1.2)
        p.kosc("Stopa" + s, "Noga" + s, staw=_lu(KOSTKA, zn), dl=0.6)

    _nogi(p)
    _biodra(p)
    _tulow(p)
    _latarnia(p)
    _glowa(p)
    _lodz(p)
    _rece(p)

    p.zaczep("RootAttachment", "Biodra", (-BIODRA[0], -BIODRA[1], -BIODRA[2]))
    # cel trafienia: środek piersi przy latarni
    p.zaczep("GlowaAttachment", "Tulow", _roznica(TULOW, (0.0, 8.9, 1.6)))
    p.zaczep("LatarniaAttachment", "Latarnia", _roznica(LATARNIA, SWIATLO))
    p.zaczep("PiescAttachment", "DlonP", _roznica(_lu(NADGARSTEK, -1), _lu(PIESC, -1)))
    p.zaczep("PiescLAttachment", "DlonL", _roznica(NADGARSTEK, PIESC))

    _klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return p


# ---------------------------------------------------------------------------------------------------- bryły
def _korzen(p, nazwa, a, b, gr, kolor="korzen"):
    _belka(p, nazwa, a, b, gr, gr, kolor, "matowy", nad=gr * 0.3)


def _nogi(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        with _model(p, "Noga" + s):
            _belka(p, "Noga", _lu((1.5, 4.9, 0.0), zn), _lu((1.7, 2.2, 0.15), zn), 1.9, 1.9, "bloto", "matowy")
            _belka(p, "Noga mokra", _lu((1.7, 2.4, 0.15), zn), _lu(KOSTKA, zn), 2.02, 2.02, "mokre", "matowy",
                   nad=0.1)
            _korzen(p, "Korzen nogi", _lu((1.0, 4.2, 0.95), zn), _lu((1.9, 2.0, 1.1), zn), 0.32)
            _korzen(p, "Korzen nogi 2", _lu((2.45, 4.0, 0.2), zn), _lu((2.55, 2.3, -0.2), zn), 0.28)
        with _model(p, "Stopa" + s):
            p.blok("Stopa", _lu((1.75, 0.38, 0.55), zn), (2.1, 0.76, 2.7), "mokre", "matowy", faza=0.15)
            for i, (ry, dl) in enumerate(((-30, 1.3), (5, 1.5), (40, 1.2))):
                kat = math.radians(ry * zn)
                a = (zn * 1.75, 0.3, 1.4)
                b = (a[0] + math.sin(kat) * dl, 0.16, a[2] + math.cos(kat) * dl)
                _korzen(p, "Palec %d" % i, a, b, 0.4, "korzen")


def _biodra(p):
    with _model(p, "Biodra"):
        p.blok("Miednica", (0, 5.0, 0.1), (4.6, 2.0, 3.1), "bloto", "matowy", faza=0.2)
        p.blok("Pas korzeni", (0, 5.85, 0.25), (5.0, 0.45, 3.4), "korzen", "matowy", faza=0.1)
        # spódnica z wodorostów (wynurzony z wody)
        n = 14
        for i in range(n):
            a = 2 * math.pi * (i + 0.3) / n
            x, z = 2.45 * math.sin(a), 0.2 + 1.65 * math.cos(a)
            dl = 1.5 + 0.5 * ((i * 7) % 5) / 4.0
            kol = "wodorost" if i % 2 else "wodorost_jasny"
            p.blok("Wodorost %d" % i, (x, 5.5 - dl / 2, z), (0.5, dl, 0.16), kol, "matowy",
                   rot=(0, math.degrees(a) + 90, 6 * (1 if i % 2 else -1)), faza=0.0)


def _tulow(p):
    with _model(p, "Tulow"):
        p.blok("Brzuch", (0, 7.1, 0.35), (5.2, 2.7, 3.6), "bloto", "matowy", faza=0.25)
        with p.uklad(pos=(0, 9.5, 0.45), obrot=(12, 0, 0)):
            p.blok("Piers", (0, 0, 0), (6.3, 2.9, 3.4), "bloto", "matowy", faza=0.25)
            p.blok("Garb", (0, 1.25, -0.9), (4.6, 1.3, 2.4), "bloto_jasne", "matowy", faza=0.2)
            # klatka z korzeni wokół latarni (żebra) i wnęka
            p.blok("Wneka", (0, -0.45, 1.66), (2.1, 2.2, 0.12), "tusz", "matowy", faza=0.0)
            for i, (x0, y0, x1, y1) in enumerate(((-1.5, 0.9, -0.9, -1.7), (1.5, 0.9, 0.9, -1.7), (-1.3, 1.0, 1.3, 1.0),
                                                  (-1.2, -1.75, 1.2, -1.75))):
                _korzen(p, "Zebro %d" % i, (x0, y0, 1.72), (x1, y1, 1.72), 0.36)
            for i, (x, y, rz) in enumerate(((-2.4, -0.2, 20), (2.4, -0.3, -18), (-2.1, 0.8, -35), (2.2, 0.7, 40))):
                p.blok("Korzen piersi %d" % i, (x, y, 1.72), (0.3, 1.6, 0.3), "korzen", "matowy", rot=(0, 0, rz),
                       faza=0.04)
        # żebra korzeni na brzuchu
        for i, (y, w) in enumerate(((6.4, 4.4), (7.3, 4.8))):
            p.blok("Korzen brzucha %d" % i, (0, y, 2.18), (w, 0.3, 0.3), "korzen", "matowy",
                   rot=(0, 0, 4 if i else -5), faza=0.04)
        # barki: wielkie bryły błota z mchem, trzciną i liściem grzybienia
        for zn in (1, -1):
            p.blok("Bark", (zn * 3.05, 10.55, 0.35), (2.7, 2.2, 2.9), "bloto", "matowy", rot=(0, 0, -zn * 10),
                   faza=0.25)
            p.blok("Mech bark", (zn * 3.0, 11.7, 0.3), (1.9, 0.18, 2.1), "mech", "matowy", rot=(0, 0, -zn * 10),
                   faza=0.04)
            p.blok("Mech bark zwis", (zn * 4.3, 11.0, 0.6), (0.2, 1.0, 1.0), "mech_ciemny", "matowy", faza=0.03)
        for i, (x, z, rx, rz, h) in enumerate(((2.6, -0.3, -12, -16, 2.4), (3.0, 0.2, -4, -26, 2.0),
                                               (3.4, -0.5, -20, -8, 1.7))):
            with p.uklad(pos=(x, 11.6, z), obrot=(rx, 0, rz)):
                p.blok("Trzcina %d" % i, (0, h / 2, 0), (0.12, h, 0.12), "trzcina", "matowy", faza=0.0)
                p.blok("Palka %d" % i, (0, h - 0.25, 0), (0.24, 0.55, 0.24), "palka", "matowy", faza=0.04)
        p.walec("Lisc grzybienia", (-3.05, 11.85, 0.45), (1.7, 0.08, 1.7), "lisc", "matowy", rot=(4, 0, 9), segm=12)
        p.blok("Kwiat", (-2.8, 12.05, 0.65), (0.42, 0.3, 0.42), "kwiat", "matowy", rot=(0, 45, 9), faza=0.08)
        p.blok("Kwiat srodek", (-2.79, 12.22, 0.65), (0.16, 0.06, 0.16), "kwiat_srodek", "matowy", faza=0.0)
        # mech na plecach i grudy
        for i, (pos, sz) in enumerate((((0.9, 11.0, -1.7), (2.2, 1.2, 0.2)), ((-1.2, 9.6, -1.55), (1.6, 1.4, 0.2)),
                                       ((0.3, 8.0, -1.45), (2.4, 0.9, 0.2)))):
            p.blok("Mech plecy %d" % i, pos, sz, "mech", "matowy", rot=(-12 if pos[1] > 9 else 0, 0, 0), faza=0.04)
        for i, (pos, sz) in enumerate((((2.2, 7.6, 1.6), (1.1, 1.0, 1.0)), ((-2.3, 6.7, 1.5), (1.0, 0.9, 1.0)),
                                       ((-1.6, 8.0, -1.6), (1.2, 1.0, 0.8)))):
            p.blok("Gruda %d" % i, pos, sz, "bloto_ciemne", "matowy", faza=0.15)


def _latarnia(p):
    with _model(p, "Latarnia"):
        x, y, z = SWIATLO
        p.blok("Uchwyt", (x, 9.95, z - 0.25), (0.12, 0.4, 0.12), "mosiadz", "metal", faza=0.0)
        p.blok("Daszek", (x, 9.62, z), (1.45, 0.24, 1.0), "mosiadz", "metal", faza=0.06)
        p.blok("Swiatlo", (x, y, z), (1.15, 1.3, 0.7), "latarnia", "swiecacy", faza=0.0)
        p.blok("Podstawa", (x, 8.08, z), (1.45, 0.24, 1.0), "mosiadz", "metal", faza=0.06)
        for i, dx in enumerate((-0.42, 0.0, 0.42)):
            p.blok("Pret %d" % i, (x + dx, y, z + 0.4), (0.1, 1.32, 0.1), "mosiadz", "metal", faza=0.0)
        for zn in (1, -1):
            p.blok("Slupek", (x + zn * 0.66, y, z), (0.12, 1.4, 0.82), "mosiadz", "metal", faza=0.0)


def _glowa(p):
    with _model(p, "Glowa"):
        p.blok("Leb", (0, 12.45, 1.55), (3.0, 2.4, 2.6), "bloto", "matowy", faza=0.25)
        p.blok("Potylica", (0, 12.8, 0.45), (2.6, 1.6, 1.2), "bloto_jasne", "matowy", faza=0.2)
        p.blok("Luk brwiowy", (0, 13.12, 2.86), (3.2, 0.42, 0.62), "korzen", "matowy", rot=(-8, 0, 0), faza=0.08)
        for zn in (1, -1):
            p.blok("Oczodol", (zn * 0.72, 12.72, 2.86), (0.85, 0.55, 0.06), "tusz", "matowy", faza=0.0)
            p.blok("Oko", (zn * 0.72, 12.7, 2.89), (0.55, 0.26, 0.06), "latarnia", "swiecacy",
                   rot=(0, 0, zn * 8), faza=0.0)
            _korzen(p, "Korzen policzka", (zn * 1.35, 13.0, 2.4), (zn * 1.5, 11.6, 2.5), 0.26)
        p.blok("Nos", (0.05, 12.25, 3.0), (0.62, 0.75, 0.5), "bloto_ciemne", "matowy", rot=(0, 0, 6), faza=0.12)
        p.blok("Paszcza", (0, 11.62, 2.4), (2.0, 0.5, 0.7), "gardlo", "matowy", faza=0.0)
        p.blok("Gardlo swiatlo", (0, 11.6, 2.12), (1.2, 0.26, 0.08), "latarnia", "swiecacy", faza=0.0)
    with _model(p, "Broda"):
        p.blok("Zuchwa", (0, 11.35, 2.1), (2.7, 0.75, 1.6), "bloto", "matowy", faza=0.15)
        p.blok("Broda", (0, 11.05, 2.85), (2.4, 1.0, 0.55), "mech", "matowy", faza=0.08)
        for i, (x, dl, kol) in enumerate(((-1.0, 1.0, "mech_ciemny"), (-0.55, 1.45, "mech"), (-0.1, 1.7, "mech"),
                                          (0.35, 1.5, "mech_ciemny"), (0.8, 1.2, "mech"), (1.1, 0.8, "mech_ciemny"))):
            p.blok("Kosmyk %d" % i, (x, 10.7 - dl / 2, 2.98 + 0.05 * (i % 2)), (0.38, dl, 0.3), kol, "matowy",
                   rot=(4, 0, (i - 2.5) * 3), faza=0.04)


def _lodz(p):
    """Przewrócona płaskodenna łódka w poprzek głowy (z przodu wygląda jak szeroki kapelusz), krzywo."""
    with _model(p, "Lodz"), p.uklad(pos=LODZ, obrot=(-4, -6, 7)):
        H, B = 1.35, 1.3                                   # wysokość burty, pół szerokości
        # burty: trapez (dłuższe przy krawędzi, krótsze przy dnie) = klocek + kliny na końcach
        for zn in (1, -1):
            with p.uklad(pos=(0, H / 2, zn * B), obrot=(-zn * 10, 0, 0)):
                p.blok("Burta", (0, 0, 0), (4.6, H, 0.16), "lodz", "matowy", faza=0.02)
                for xn in (1, -1):
                    p.klin("Burta dziob", (xn * 2.7, 0, 0), (0.16, H, 0.8), "lodz", "matowy", rot=(0, -xn * 90, 0),
                           faza=0.0)
                p.blok("Deska burty", (0, -0.2, zn * 0.09), (4.7, 0.06, 0.03), "lodz_ciemna", "matowy", faza=0.0)
                p.blok("Pas farby", (0, -H / 2 + 0.17, zn * 0.1), (5.4, 0.26, 0.04), "farba", "matowy", faza=0.0)
        # dno (na wierzchu) i dwie skośne pawęże na końcach
        p.blok("Dno", (0, H + 0.04, 0), (4.6, 0.16, 2.75), "lodz_jasna", "matowy", faza=0.02)
        for i, x in enumerate((-1.5, 0.0, 1.5)):
            p.blok("Deska dna %d" % i, (x, H + 0.13, 0), (0.06, 0.03, 2.7), "lodz_ciemna", "matowy", faza=0.0)
        p.blok("Ploza", (0, H + 0.2, 0), (4.4, 0.16, 0.3), "lodz_ciemna", "matowy", faza=0.0)
        for xn in (1, -1):
            p.blok("Pawez", (xn * 2.7, H / 2, 0), (0.16, 1.6, 2.75), "lodz_ciemna", "matowy",
                   rot=(0, 0, xn * 31), faza=0.02)
            p.blok("Dulka", (xn * 0.9, -0.1, 1.42), (0.12, 0.3, 0.12), "mosiadz", "metal", faza=0.0)
        p.blok("Dziura", (1.2, H + 0.13, -0.6), (0.6, 0.03, 0.45), "tusz", "matowy", faza=0.0)
        p.blok("Mech dna", (-0.8, H + 0.14, 0.4), (1.6, 0.05, 1.1), "mech", "matowy", faza=0.0)
        p.blok("Mech dna 2", (1.6, H + 0.14, 0.7), (0.8, 0.05, 0.7), "mech_ciemny", "matowy", faza=0.0)
        # wiosło sterczące w tył spod łódki
        with p.uklad(pos=(-1.4, 0.2, -1.0), obrot=(-62, 18, 0)):
            p.blok("Wioslo", (0, 1.6, 0), (0.18, 3.6, 0.18), "lodz_jasna", "matowy", faza=0.0)
            p.blok("Pioro wiosla", (0, 3.7, 0), (0.6, 1.1, 0.08), "lodz", "matowy", faza=0.02)
        p.blok("Sznur", (2.0, -0.45, 1.4), (0.06, 0.9, 0.06), "korzen", "matowy", faza=0.0)


def _rece(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        with _model(p, "Ramie" + s):
            _belka(p, "Ramie", _lu((3.55, 10.6, 0.3), zn), _lu(LOKIEC, zn), 1.35, 1.3, "bloto", "matowy", nad=0.2)
            _korzen(p, "Korzen ramienia", _lu((3.0, 10.4, 1.0), zn), _lu((4.6, 7.3, 1.35), zn), 0.38)
            _korzen(p, "Korzen ramienia 2", _lu((4.3, 10.0, -0.4), zn), _lu((4.75, 7.2, 0.4), zn), 0.32)
            p.blok("Lokiec", _lu(LOKIEC, zn), (1.55, 1.3, 1.45), "bloto_ciemne", "matowy", rot=(0, 20, 0), faza=0.15)
        with _model(p, "Przedramie" + s):
            _belka(p, "Przedramie", _lu(LOKIEC, zn), _lu((4.3, 4.3, 1.25), zn), 1.5, 1.45, "korzen_jasny", "matowy",
                   nad=0.1)
            _korzen(p, "Korzen przedramienia", _lu((3.6, 6.8, 1.4), zn), _lu((3.75, 4.4, 1.85), zn), 0.4)
            _korzen(p, "Korzen przedramienia 2", _lu((4.95, 6.6, 0.6), zn), _lu((4.95, 4.2, 0.9), zn), 0.34)
            p.blok("Mech przedramienia", _lu((4.4, 6.3, 0.35), zn), (0.9, 1.1, 0.2), "mech", "matowy",
                   rot=(10, 0, 0), faza=0.03)
        with _model(p, "Dlon" + s):
            p.blok("Piesc", _lu(PIESC, zn), (1.7, 1.85, 1.75), "mokre", "matowy", faza=0.25)
            for i, x in enumerate((3.8, 4.2, 4.6, 4.95)):
                p.blok("Kostka %d" % i, _lu((x, 2.55, 2.4), zn), (0.42, 0.55, 0.5), "korzen", "matowy",
                       rot=(20, 0, 0), faza=0.08)
            p.blok("Kciuk", _lu((3.55, 3.15, 2.1), zn), (0.45, 0.8, 0.5), "korzen", "matowy", rot=(0, 0, zn * 20),
                   faza=0.08)
            _korzen(p, "Wlos korzenia", _lu((4.7, 2.3, 1.0), zn), _lu((4.95, 1.75, 0.85), zn), 0.12)
            _korzen(p, "Wlos korzenia 2", _lu((4.0, 2.2, 0.9), zn), _lu((3.85, 1.8, 0.7), zn), 0.1)


# ---------------------------------------------------------------------------------------------------- klipy
def _z(*czesci, **kosci):
    out = {}
    for c in czesci:
        out.update(c)
    out.update(kosci)
    return out


def _rece_poz(ramieL=None, przedL=None, ramieP=None, przedP=None):
    """Kierunki ramion i przedramion w świecie (None = spoczynek względem rodzica)."""
    out = {}
    for n, v in (("RamieL", ramieL), ("PrzedramieL", przedL), ("RamieP", ramieP), ("PrzedramieP", przedP)):
        if v is not None:
            out[n] = {"k": v}
    return out


def _mix(a, b, s):
    """Kierunek pośredni między a i b (s = 0…1)."""
    a, b = _norm(a), _norm(b)
    return _norm(tuple(a[i] + (b[i] - a[i]) * s for i in range(3)))


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
    """Spoczynek (2,4 s): ciężki oddech barkami, latarnia buja się w klatce, łódka i broda kołyszą się z opóźnieniem,
    ręce wiszą i lekko się kołyszą, łeb powoli rozgląda się."""
    k = p.klip("idle", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        c = math.cos(2 * math.pi * t)
        return {"Tulow": (-1.5 * a, 0, 0.8 * c), "Glowa": (1.2 * a, 7 * math.sin(2 * math.pi * t + 0.4), 0),
                "Lodz": (1.5 * math.sin(2 * math.pi * t - 0.9), 0, 2.0 * math.sin(2 * math.pi * t - 1.4)),
                "Broda": (1.5 * math.sin(2 * math.pi * t - 0.7), 0, 2.5 * math.sin(2 * math.pi * t - 1.0)),
                "Latarnia": (4 * math.sin(2 * math.pi * t - 0.5), 0, 3 * math.sin(4 * math.pi * t)),
                "RamieL": (2.5 * a, 0, 1.5 * c), "RamieP": (-2.5 * a, 0, -1.5 * c),
                "PrzedramieL": (-3 - 2 * a, 0, 0), "PrzedramieP": (-3 + 2 * a, 0, 0)}
    _petla(k, poza)
    return k


def ruch(p, dl=60):
    """Brnie przez wodę (2,0 s na dwa kroki): ciężki wymach nóg, biodra kołyszą się na boki, tułów pochylony,
    ręce wahadłem w przeciwfazie, łódka i latarnia bujają się z opóźnieniem."""
    k = p.klip("ruch", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        c = math.cos(2 * math.pi * t)
        return {"Biodra": (0, 7 * a, 5 * c), "NogaL": (-24 * a, 0, -4 * c), "NogaP": (24 * a, 0, -4 * c),
                "Tulow": (8 + 2 * math.sin(4 * math.pi * t), -9 * a, -5 * c), "Glowa": (-6, 4 * a, 3 * c),
                "RamieL": (18 * a, 0, 3), "RamieP": (-18 * a, 0, -3),
                "PrzedramieL": (-10 + 8 * a, 0, 0), "PrzedramieP": (-10 - 8 * a, 0, 0),
                "Lodz": (3 * math.sin(4 * math.pi * t - 1.2), 0, 4 * math.sin(2 * math.pi * t - 1.0)),
                "Broda": (3 * math.sin(4 * math.pi * t - 1.0), 0, 3 * c),
                "Latarnia": (5 * math.sin(4 * math.pi * t - 0.8), 0, 4 * c),
                "_h": 0.0}
    _petla(k, poza)
    return k


def atak(p, dl=36):
    """Cios pięścią z korzeni (1,2 s): prawa ręka w górę za bark, skręt tułowia, uderzenie z góry w dół przed siebie
    (trafienie kl. 18), dobicie i powrót."""
    k = p.klip("atak", dl, petla=False)
    spocz = {}
    zamach = _z(_rece_poz(ramieP=(-0.55, 0.85, -0.35), przedP=(-0.15, 0.95, 0.2), ramieL=(0.5, -0.8, 0.5),
                          przedL=(0.1, -0.9, 0.6)),
                Biodra={"o": (0, -10, 0), "p": (0, 0, -0.3)}, Tulow=(-8, -24, 6), Glowa=(-6, 12, 0),
                Lodz=(4, 0, -4), Latarnia=(-6, 0, 4))
    cios = _z(_rece_poz(ramieP=(0.35, -0.5, 0.8), przedP=(0.2, -0.85, 0.5), ramieL=(0.55, -0.85, -0.2)),
              Biodra={"o": (8, 4, 0), "p": (0, 0, 0.7)}, Tulow=(34, 12, -4), Glowa=(-8, -6, 0), Lodz=(-6, 0, 3),
              Latarnia=(10, 0, -4), NogaL=(-14, 0, 0), NogaP=(8, 0, 0))
    dobicie = _z(_rece_poz(ramieP=(0.42, -0.6, 0.6), przedP=(0.25, -0.9, 0.3), ramieL=(0.55, -0.85, -0.25)),
                 Biodra={"o": (9, 5, 0), "p": (0, 0, 0.75)}, Tulow=(36, 15, -4), Glowa=(-6, -8, 0), Lodz=(-8, 0, 4),
                 Latarnia=(12, 0, -5), NogaL=(-14, 0, 0), NogaP=(8, 0, 0))
    powrot = _z(Biodra={"o": (0, -2, 0), "p": (0, 0, 0.25)}, Tulow=(6, -4, 0), Lodz=(3, 0, -2), Latarnia=(-4, 0, 2))
    _sekwencja(k, (0, 12, 18, 22, 29, 36), (spocz, zamach, cios, dobicie, powrot, spocz),
               wyg={0: "s", 1: "we", 2: "wy"})
    return k


def umiejetnosc(p, dl=66):
    """Ogłuszające uderzenie (2,2 s): obie pięści splecione wysoko nad łodzią, olbrzym prostuje się i odchyla
    (kl. 0–26), potężne uderzenie obiema pięściami w taflę przed sobą (kl. 38 = trafienie, fala), chwila w dole,
    powrót."""
    k = p.klip("umiejetnosc", dl, petla=False)
    spocz = {}
    gora = _z(_rece_poz(ramieL=(-0.3, 1.0, 0.1), przedL=(-0.35, 1.0, -0.05), ramieP=(0.3, 1.0, 0.1),
                        przedP=(0.35, 1.0, -0.05)),
              Biodra={"o": (-4, 0, 0), "p": (0, 0, -0.3)}, Tulow=(-12, 0, 0), Glowa=(-14, 0, 0), Lodz=(6, 0, 0),
              Latarnia=(-8, 0, 0), Broda=(6, 0, 0))
    gora2 = _z(gora, Tulow=(-15, 0, 0), Glowa=(-16, 0, 0), Lodz=(8, 0, 2))
    w_dol = _z(_rece_poz(ramieL=(-0.3, -0.2, 1.0), przedL=(-0.25, -0.6, 0.8), ramieP=(0.3, -0.2, 1.0),
                         przedP=(0.25, -0.6, 0.8)),
               Biodra={"o": (8, 0, 0), "p": (0, 0, 0.4)}, Tulow=(28, 0, 0), Glowa=(-6, 0, 0), Lodz=(-4, 0, 0),
               Latarnia=(6, 0, 0), NogaL=(-12, 0, 6), NogaP=(-12, 0, -6))
    uderz = _z(_rece_poz(ramieL=(-0.35, -1.0, 0.25), przedL=(-0.2, -0.95, 0.32), ramieP=(0.35, -1.0, 0.25),
                         przedP=(0.2, -0.95, 0.32)),
               Biodra={"o": (15, 0, 0), "p": (0, 0, 0.6)}, Tulow=(45, 0, 0), Glowa=(-14, 0, 0), Lodz=(-10, 0, 3),
               Latarnia=(16, 0, 0), Broda=(10, 0, 0), NogaL=(-22, 0, 8), NogaP=(-22, 0, -8))
    trzyma = _z(uderz, Lodz=(4, 0, -3), Latarnia=(-6, 0, 3), Broda=(4, 0, 0))
    _sekwencja(k, (0, 14, 26, 34, 38, 48, 66), (spocz, gora, gora2, w_dol, uderz, trzyma, spocz),
               wyg={2: "we", 3: "we", 4: "wy"})
    return k


def trafienie(p, dl=20):
    """Szarpnięcie w tył (0,67 s, najdalej kl. 4): tułów odchylony, łeb w górę, łódka przekrzywia się, latarnia
    się buja."""
    k = p.klip("trafienie", dl, petla=False)
    spocz = {}
    szarp = _z(Biodra={"o": (-4, 0, 0), "p": (0, 0, -0.5)}, Tulow=(-12, 4, 3), Glowa=(-12, 0, 4), Lodz=(10, 0, -6),
               Latarnia=(-14, 0, 6), Broda=(8, 0, 0), RamieL=(8, 0, 6), RamieP=(10, 0, -8))
    odb = _z(Biodra={"o": (2, 0, 0), "p": (0, 0, -0.2)}, Tulow=(4, -2, -1), Glowa=(4, 0, -1), Lodz=(-6, 0, 4),
             Latarnia=(8, 0, -4))
    _sekwencja(k, (0, 4, 12, 20), (spocz, szarp, odb, spocz), wyg={0: "wy"})
    return k


def unik(p, dl=30):
    """Ciężki krok w lewo o 1,5 studa (najdalej kl. 14) i powrót (1,0 s)."""
    k = p.klip("unik", dl, petla=False)
    spocz = {}
    przenies = _z(Biodra={"o": (0, 0, -5), "p": (0.2, 0, 0)}, Tulow=(0, 0, -4), NogaL=(0, 0, 14),
                  Lodz=(0, 0, 4), Latarnia=(0, 0, 6))
    krok = _z(Biodra={"o": (0, -6, 6), "p": (1.0, 0, 0)}, Tulow=(0, 0, 6), NogaL=(0, 0, 8), NogaP=(0, 0, 10),
              RamieP=(0, 0, -12), Lodz=(0, 0, -6), Latarnia=(0, 0, -8), _h=0.15)
    stoi = _z(Biodra={"o": (0, -8, 3), "p": (1.5, 0, 0)}, Tulow=(2, 6, 2), Glowa=(0, -10, 0), Lodz=(0, 0, 3),
              Latarnia=(0, 0, 4))
    wraca = _z(Biodra={"o": (0, -3, -4), "p": (0.7, 0, 0)}, NogaP=(0, 0, -10), Tulow=(0, 0, -3), _h=0.1)
    _sekwencja(k, (0, 5, 10, 14, 21, 30), (spocz, przenies, krok, stoi, wraca, spocz), wyg={1: "we", 2: "wy"})
    return k


def upadek(p, dl=66):
    """Upadek (2,2 s): zatacza się, łeb opada, łódka zsuwa się z głowy na bok, olbrzym pada na plecy z rozrzuconymi
    rękami i zapada się w topiel (kl. 66 = leży, latarnia świeci nad wodą)."""
    k = p.klip("upadek", dl, petla=False)
    spocz = {}
    chwiej = _z(Biodra={"o": (-4, 6, 6), "p": (0, 0, -0.4)}, Tulow=(-10, 6, 8), Glowa=(-10, 10, 6),
                Lodz={"o": (6, 0, -10), "p": (0.2, 0, 0)}, Latarnia=(-10, 0, 8), RamieL=(6, 0, 18), RamieP=(10, 0, -8))
    chwiej2 = _z(Biodra={"o": (6, -8, -6), "p": (0, 0, -0.2)}, Tulow=(14, -6, -8), Glowa=(16, -6, -8),
                 Lodz={"o": (12, 0, 16), "p": (-0.6, -0.2, 0.3)}, Latarnia=(12, 0, -6), RamieL=(-6, 0, 10),
                 RamieP=(-8, 0, -14), NogaL=(-10, 0, 0))
    pada = _z(Biodra={"o": (-40, 4, 4), "p": (0, 0, -1.8)}, Tulow=(-12, 0, 0), Glowa=(-16, 0, 0),
              Lodz={"o": (30, 0, 40), "p": (-2.4, -1.5, 1.4)}, Latarnia=(-20, 0, 0), RamieL=(-10, 0, 45),
              RamieP=(-10, 0, -45), NogaL=(-30, 0, 4), NogaP=(-24, 0, -4), _wolne=True)
    lezy = _z(Biodra={"o": (-82, 4, 4), "p": (0, 0, -3.6)}, Tulow=(-6, 0, 0), Glowa=(-14, 10, 0), Broda=(14, 0, 0),
              Lodz={"o": (68, 0, 64), "p": (-3.4, -4.6, 1.2)}, Latarnia=(4, 0, 0), RamieL=(-30, 0, 70),
              RamieP=(-25, 0, -70), PrzedramieL=(-20, 0, 10), PrzedramieP=(-20, 0, -10),
              NogaL=(-40, 0, 8), NogaP=(-34, 0, -8), _wolne=True)
    topiel = _z(lezy, _h=-1.4)
    _sekwencja(k, (0, 10, 20, 32, 42, 66), (spocz, chwiej, chwiej2, pada, lezy, topiel),
               wyg={2: "we", 3: "wy", 4: "l"})
    return k


def ryk(p, dl=60):
    """Ryk (dokładnie 60 klatek = 2,0 s, pętla — gra go przelot kamery): olbrzym prostuje się, rozkłada długie ręce,
    odchyla łeb, otwiera paszczę z zieloną poświatą i drży; łódka podskakuje na głowie, latarnia się buja."""
    k = p.klip("ryk", dl, petla=True)

    def poza(t):
        s = min(1.0, max(0.0, (t - 0.08) / 0.22)) * min(1.0, max(0.0, (0.95 - t) / 0.2))
        s = s * s * (3 - 2 * s)
        drz = math.sin(14 * math.pi * t) * s
        rl, pl = _mix(OS["RamieL"], (0.85, 0.3, 0.35), s), _mix(OS["PrzedramieL"], (0.6, 0.75, 0.3), s)
        pz = _rece_poz(ramieL=rl, przedL=pl, ramieP=_lu(rl, -1), przedP=_lu(pl, -1))
        pz.update({"Biodra": {"o": (-3 * s, 0, 0), "p": (0, 0, -0.25 * s)},
                   "Tulow": (-14 * s + 1.2 * drz, 0, 0.8 * drz),
                   "Glowa": (-20 * s, 0, 1.5 * drz), "Broda": (22 * s, 0, 0),
                   "Lodz": (3 * drz + 4 * s, 0, 2 * drz), "Latarnia": (6 * math.sin(4 * math.pi * t) * s, 0, 3 * drz)})
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
