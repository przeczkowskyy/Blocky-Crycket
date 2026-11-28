# -*- coding: utf-8 -*-
"""KOT-DEMON — rasa Demon jako wariant Kota-Maga (Paweł 23.11, referencja assets/raw/RasyKoty/kot_demon.png,
zatwierdzona przez Pawła; notatka B&C/Postacie/Rasy jako koty — referencje.md). Status: propozycja.

Zasada: TEN SAM model co Kot-Mag (swiat/postacie/kot_mag.py — wymiary, kości, klipy, kapelusz, szata, kostur), zmienia
się tylko wygląd. Plik Karola nie jest zmieniany: wczytujemy WŁASNĄ kopię modułu kot_mag (importlib), podmieniamy w niej
paletę i dokładamy cechy demona na tych samych kościach:
  - futro karmazynowe z ciemniejszymi pręgami, jaśniejsza różowa mordka;
  - żółto-bursztynowe oczy (nakładka na czarne oko, czarna obwódka zostaje) i zadziorne brwi;
  - mały biały kieł; dwa czarne zakrzywione rogi na głowie (przebijają rondo kapelusza);
  - na końcu ogona grot w kształcie łopatki (ogon diabełka);
  - szata i kapelusz czarne z karmazynowym obszyciem, klejnoty i kryształ kostura pomarańczowe jak żar.
Klipy: te same co Kota-Maga (kopiowane z jego postaci odniesienia — dodatki nie zmieniają ruchu).

Dwie wersje (Paweł 23.11):
  zbuduj()      → [kot_demon]               pełny strój jak na referencji (kapelusz, szata, szarfa, kostur);
  podstawowy()  → kot_demon_podstawowy      strój bazowy: koszulka i spodenki, bez przedmiotów;
  czlowiek_podstawowy() → kot_czlowiek_podstawowy  rasa Człowiek = rudy Kot-Mag w stroju bazowym (Paweł 23.11).

    python -B swiat/postacie/kot_demon.py --kontrola       # sprawdzian biblioteki (bez Blendera)
"""
import importlib.util
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(TU)))

ID = "kot_demon"
NAZWA = "Kot-Demon"


def _kot_mag():
    """Świeża, prywatna kopia modułu kot_mag (zmiana palety nie dotyka prawdziwego Kota-Maga)."""
    spec = importlib.util.spec_from_file_location("kot_mag_dla_demona", os.path.join(TU, "kot_mag.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.PALETA.update({
        "kot": "C8243A", "kot_jasny": "EBA0A6", "kot_ciemny": "8A1426",
        "szata": "2E2A33", "szata_ciemna": "1B191F", "szata_jasna": "47414F",
        "wstazka": "C8243A", "krysztal": "FF7A1A", "krysztal_jasny": "FFC060",
        "drewno": "3E2418", "drewno_ciemne": "231208",
        # nowe kolory demona
        "oko_demona": "FFC21A", "rog": "26232B", "kiel": "FFFFFF",
        "koszulka": "F1E6CC", "spodenki": "26232B",
        # wersja według rzutów Pawła z 26.11 (wg_rzutow)
        "d_futro": "C2283E", "d_prega": "961A2E", "d_mordka": "E97C90", "d_ucho": "F29AAA", "d_nos": "D75A73",
        "d_zrenica": "7A2E10", "d_rog": "2A2830", "d_rog_jasny": "45414D", "d_koszulka": "EFE3C2",
        "d_spodenki": "1F1D22",
    })
    return m


# ------------------------------------------------------------------------------------------- baza bliżej referencji
def ulepsz_baze(p):
    """Bryła kota bliżej referencji z Higgsfield (Paweł 25.11: „popraw bazowe modele, nie tylko dodatki”) — na
    kopii modelu, plik Karola kot_mag.py bez zmian: uszy większe i mocniej odchylone na boki (na referencjach wystają
    daleko poza rondo kapelusza i są jedną z najbardziej widocznych cech kota). Kości i klipy te same."""
    stare = {"Ucho L", "Ucho P", "Ucho srodek L", "Ucho srodek P"}
    p.czesci[:] = [c for c in p.czesci if c["n"] not in stare]
    for zn, s, kosc in ((1, "L", "LeftEar"), (-1, "P", "RightEar")):
        with p.na(kosc, obrot=(0, 0, -zn * 36)):
            p.ostroslup("Ucho " + s, (zn * 0.05, 0.47, 0), (0.82, 1.0, 0.36), "kot", gora=(0.0, 0.12),
                        przes_gory=(zn * 0.08, 0))
            p.ostroslup("Ucho srodek " + s, (zn * 0.05, 0.4, 0.19), (0.5, 0.72, 0.04), "nos", "matowy",
                        gora=(0.0, 0.03), przes_gory=(zn * 0.05, 0), faza=0.0)
    return p


def obszycie_peleryny(p):
    """Jasna lamówka pod peleryną na ramionach (referencje: szeroka peleryna z obszyciem) — tylko pełny strój."""
    w, h, d = p.wymiary("UpperTorso")
    with p.na("UpperTorso", od="srodek"):
        p.blok("Peleryna obszycie", (0, h / 2 - 0.135, 0), (w + 0.32, 0.05, d + 0.28), "wstazka", "matowy", faza=0.0)
    return p


def szersze_rondo(m):
    """Kapelusz w kopii modułu kot_mag: szersze rondo (referencje: rondo wyraźnie szersze od głowy), bez bocznej
    gwiazdki (klejnot z przodu dokłada rasa). Podmienia m.kapelusz — m.przedmioty() bierze już nową wersję."""
    stary = m.kapelusz

    def kapelusz():
        a = stary()
        a.czesci[:] = [c for c in a.czesci if c["n"] not in ("Rondo", "Rondo spod", "Gwiazdka")]
        a.walec("Rondo", (0, 0.06, 0), (2.7, 0.12, 2.45), "szata", "matowy", segm=8)
        a.walec("Rondo spod", (0, 0.0, 0), (2.5, 0.03, 2.25), "szata_ciemna", "matowy", segm=8, faza=0.0)
        return a

    m.kapelusz = kapelusz
    return m


KM = szersze_rondo(_kot_mag())
PALETA = KM.PALETA


def _cechy_demona(p):
    """Rogi, oczy, brwi, kieł i grot ogona — na kościach Kota-Maga (układ jak w kot_mag._golas)."""
    w, h, d = p.wymiary("Head")
    with p.na("Head", od="srodek"):
        z = d / 2
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * 0.38
            # żółta tęczówka na czarnym oku (czarny brzeg zostaje), błyski Kota-Maga leżą przed nią
            p.blok("Oko demona " + s, (x, 0.11, z + 0.045), (0.27, 0.4, 0.02), "oko_demona", "swiecacy", faza=0.0)
            p.blok("Zrenica " + s, (x, 0.06, z + 0.064), (0.1, 0.18, 0.02), "tusz", "polysk", faza=0.0)
            # zadziorna brew: opada ku środkowi
            p.blok("Brew " + s, (zn * 0.36, 0.43, z + 0.03), (0.36, 0.08, 0.05), "kot_ciemny", "matowy",
                   rot=(0, 0, zn * 16), faza=0.0)
        p.blok("Kiel", (0.1, -0.43, z + 0.075), (0.06, 0.1, 0.03), "kiel", "polysk", faza=0.0)
    # rogi: podstawa przy górnej krawędzi głowy (między uszami) + szpic odchylony na zewnątrz i w górę
    for zn, s in ((1, "L"), (-1, "P")):
        with p.na("Head", pos=(zn * 0.42, h / 2, 0.05), obrot=(0, 0, -zn * 22), od="srodek"):
            p.blok("Rog nasada " + s, (0, 0.13, 0), (0.26, 0.3, 0.26), "rog", faza=0.03)
            p.ostroslup("Rog " + s, (0, 0.5, 0), (0.22, 0.46, 0.22), "rog", gora=(0.0, 0.0),
                        przes_gory=(zn * 0.1, 0.0), faza=0.02)
    # grot ogona: płaski „szpic łopatki” za ostatnim zawijasem (układ kości TailTip z kot_mag)
    with p.na("TailTip", obrot=(0, -50, -10)):
        p.ostroslup("Grot ogona", (0, 1.12, 0.72), (0.5, 0.42, 0.1), "kot", rot=(90, 0, 0), gora=(0.0, 0.0), faza=0.02)
        p.blok("Grot ogona nasada", (0, 1.12, 0.52), (0.18, 0.16, 0.16), "kot", faza=0.02)
    return p


def zbuduj():
    """[Kot-Demon w pełnym stroju jak na referencji] — strój kanoniczny Kota-Maga w barwach demona."""
    prz = KM.przedmioty()
    p = KM.ubierz(KM.cialo(), KM.wybierz(KM.KANON, prz), id=ID, nazwa=NAZWA, korekty=KM.KOREKTY_CHWYTU)
    return [_cechy_demona(obszycie_peleryny(ulepsz_baze(p)))]


def _stroj_podstawowy(p):
    """Koszulka z dekoltem i krótkimi rękawami oraz spodenki na gołym kocie (kolory „koszulka”, „spodenki”)."""
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        p.blok("Koszulka", (0, 0, 0), (w + 0.1, h + 0.04, d + 0.1), "koszulka", "matowy")
        p.ostroslup("Dekolt", (0, h / 2 - 0.12, d / 2 + 0.055), (0.3, 0.26, 0.02), "kot", "matowy",
                    rot=(0, 0, 180), gora=(0.0, 0.0), faza=0.0)
    for strona in ("Left", "Right"):
        kosc = strona + "UpperArm"
        with p.na(kosc, od="srodek"):
            w, h, d = p.wymiary(kosc)
            p.blok("Rekaw " + strona, (0, h * 0.18, 0), (w + 0.08, h * 0.66, d + 0.08), "koszulka", "matowy")
    with p.na("LowerTorso", od="srodek"):
        w, h, d = p.wymiary("LowerTorso")
        p.blok("Spodenki", (0, 0, 0), (w + 0.1, h + 0.04, d + 0.1), "spodenki", "matowy")
    for strona in ("Left", "Right"):
        kosc = strona + "UpperLeg"
        with p.na(kosc, od="srodek"):
            w, h, d = p.wymiary(kosc)
            p.blok("Nogawka " + strona, (0, h * 0.2, 0), (w + 0.08, h * 0.6, d + 0.08), "spodenki", "matowy")
    return p


def podstawowy():
    """Kot-Demon w stroju bazowym: koszulka i spodenki, bez kapelusza, szaty i kostura."""
    p = KM.cialo()
    p.id, p.nazwa = ID + "_podstawowy", NAZWA + " (strój podstawowy)"
    return _cechy_demona(_stroj_podstawowy(ulepsz_baze(p)))


def czlowiek_podstawowy():
    """Rasa Człowiek jako kot (Paweł 23.11): nasz rudy Kot-Mag bez zmian wyglądu, w stroju podstawowym jak ludzik rasy
    Człowiek z planszy D-104 — kremowa koszulka i niebieskie spodenki. Osobna kopia kot_mag z dopisanymi kolorami."""
    spec = importlib.util.spec_from_file_location("kot_mag_dla_czlowieka", os.path.join(TU, "kot_mag.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.PALETA.update({"koszulka": "F1E6CC", "spodenki": "2F6FD6"})
    p = m.cialo()
    p.id, p.nazwa = "kot_czlowiek_podstawowy", "Kot-Człowiek (strój podstawowy)"
    return _stroj_podstawowy(ulepsz_baze(p))


# ------------------------------------------------------------------------------------- wersja według rzutów (26.11)
def wg_rzutow():
    """Kot-Demon w stroju podstawowym zbudowany od nowa według czterech rzutów Pawła z 26.11
    (assets/raw/RasyKoty/kot_demon_obroty/: przód, lewy bok, tył, prawy bok). PRÓBA — nie jest w grze.

    Szkielet i klipy Kota-Maga bez zmian (KM._postac + kopia klipów postaci odniesienia), nowe są wszystkie bryły:
    głowa-sześcian większa od tułowia, uszy na górnych rogach głowy z różowym środkiem, dwa czarne wygięte rogi
    między uszami, pręgi na czole, bokach i z tyłu głowy, żółte zmrużone oczy pod skośną powieką, szeroka różowa
    mordka, nos, uśmieszek z jednym kłem, po trzy wąsy, kremowa koszulka z dekoltem w serek i krótkimi rękawami,
    czarne spodenki, gołe łapy z poduszkami, cienki ogon z grotem."""
    p = KM._postac(ID + "_wg_rzutow", NAZWA + " (według rzutów 26.11)")
    p.typ_ciala = KM.CIALO_TYP
    F, PR = "d_futro", "d_prega"

    # ---------------- głowa: sześcian 1,7 × 1,5 × 1,5 (klocek kości 1,65 × 1,3 × 1,4 — spód na tej samej wysokości)
    w0, h0, d0 = p.wymiary("Head")
    W, H, D = 1.7, 1.5, 1.5
    yc = -h0 / 2 + H / 2                       # środek nowej głowy względem środka klocka kości
    gora, zf = yc + H / 2, D / 2
    with p.na("Head", od="srodek"):
        p.blok("Glowa", (0, yc, 0), (W, H, D), F, faza=0.14)
        # pręgi: trzy na czole (szpic w dół), ich ciąg na czubku i z tyłu głowy
        for i, (x, dl) in enumerate(((0.0, 0.36), (-0.27, 0.27), (0.27, 0.27))):
            p.ostroslup("Prega czolo %d" % i, (x, gora - dl / 2 - 0.04, zf + 0.005), (0.15, dl, 0.03), PR, "matowy",
                        rot=(0, 0, 180 + x * 30), gora=(0.02, 0.03), faza=0.0)
            p.blok("Prega czubek %d" % i, (x, gora + 0.005, 0), (0.15, 0.03, D - 0.34), PR, "matowy", faza=0.0)
            p.ostroslup("Prega tyl %d" % i, (x, gora - dl / 2 - 0.04, -zf - 0.005), (0.15, dl + 0.1, 0.03), PR,
                        "matowy", rot=(0, 0, 180), gora=(0.02, 0.03), faza=0.0)
        for zn, s in ((1, "L"), (-1, "P")):
            # pręgi na boku głowy: od tyłu ku pyskowi, szpic do przodu
            for i, (y, dl) in enumerate(((0.16, 0.62), (-0.1, 0.74), (-0.36, 0.5))):
                p.ostroslup("Prega bok %s%d" % (s, i), (zn * (W / 2 + 0.005), yc + y, -zf + 0.1 + dl / 2),
                            (0.03, dl, 0.14), PR, "matowy", rot=(90, 0, 0), gora=(0.03, 0.02), faza=0.0)
            # dwie krótkie pręgi na policzku widoczne z przodu, szpic ku środkowi
            for i, y in enumerate((-0.02, -0.22)):
                p.ostroslup("Prega policzek %s%d" % (s, i), (zn * (W / 2 - 0.15), yc + y, zf + 0.005),
                            (0.1, 0.26, 0.03), PR, "matowy", rot=(0, 0, zn * 90), gora=(0.02, 0.03), faza=0.0)
            # oko: czarna obwódka, żółta świecąca tęczówka, ciemna źrenica przy nosie, błysk
            x, y = zn * 0.43, yc + 0.12
            p.blok("Oko obrys " + s, (x, y, zf + 0.01), (0.46, 0.36, 0.05), "tusz", "polysk", faza=0.04)
            p.blok("Oko " + s, (x, y - 0.01, zf + 0.03), (0.38, 0.27, 0.03), "oko_demona", "swiecacy", faza=0.0)
            p.blok("Zrenica " + s, (x - zn * 0.06, y - 0.03, zf + 0.045), (0.12, 0.2, 0.02), "d_zrenica", "polysk",
                   faza=0.0)
            p.blok("Blysk " + s, (x - zn * 0.02, y + 0.03, zf + 0.056), (0.05, 0.06, 0.02), "bialy", faza=0.0)
            # skośna powieka: futro zakrywa górę oka, pod nim gruba kreska tuszu — zły, zmrużony wzrok
            p.blok("Powieka " + s, (x, y + 0.2, zf + 0.05), (0.56, 0.2, 0.05), F, rot=(0, 0, zn * 17), faza=0.0)
            p.blok("Powieka kreska " + s, (x, y + 0.105, zf + 0.055), (0.54, 0.06, 0.05), "tusz", rot=(0, 0, zn * 17),
                   faza=0.0)
            p.blok("Brew " + s, (zn * 0.5, y + 0.4, zf + 0.008), (0.17, 0.07, 0.03), PR, "matowy", rot=(0, 0, zn * 22),
                   faza=0.0)
            # trzy wąsy: wachlarz wystający poza obrys głowy
            for i, (dy, kat) in enumerate(((-0.18, 11), (-0.3, 0), (-0.42, -11))):
                p.blok("Was %s%d" % (s, i), (zn * 0.93, yc + dy, zf + 0.02), (0.48, 0.02, 0.02), "tusz", "matowy",
                       rot=(0, 0, zn * kat), faza=0.0)
        # mordka: szeroka różowa plama od nosa do brody (spłaszczony krążek), nos, uśmieszek i kieł po lewej kota
        p.walec("Mordka", (0, yc - 0.44, zf + 0.008), (1.16, 0.04, 0.6), "d_mordka", "matowy", rot=(90, 0, 0),
                faza=0.0, segm=12)
        p.ostroslup("Nos", (0, yc - 0.15, zf + 0.045), (0.21, 0.13, 0.05), "d_nos", "polysk", rot=(0, 0, 180),
                    gora=(0.03, 0.03), faza=0.0)
        p.blok("Usta pion", (0, yc - 0.26, zf + 0.04), (0.03, 0.1, 0.03), "tusz", faza=0.0)
        for zn in (1, -1):
            p.blok("Usta a", (zn * 0.065, yc - 0.335, zf + 0.04), (0.14, 0.035, 0.03), "tusz", rot=(0, 0, -zn * 28),
                   faza=0.0)
            p.blok("Usta b", (zn * 0.185, yc - 0.335, zf + 0.04), (0.14, 0.035, 0.03), "tusz", rot=(0, 0, zn * 28),
                   faza=0.0)
        p.blok("Usmieszek", (0.31, yc - 0.27, zf + 0.04), (0.13, 0.035, 0.03), "tusz", rot=(0, 0, 40), faza=0.0)
        p.ostroslup("Kiel", (0.15, yc - 0.42, zf + 0.05), (0.08, 0.12, 0.03), "kiel", "polysk", rot=(0, 0, 180),
                    gora=(0.0, 0.03), faza=0.0)

    # uszy: na górnych rogach głowy, odchylone na boki, różowy środek od przodu
    for zn, s, kosc in ((1, "L", "LeftEar"), (-1, "P", "RightEar")):
        with p.na(kosc, obrot=(0, 0, -zn * 24)):
            p.ostroslup("Ucho " + s, (zn * 0.06, 0.42, -0.12), (0.7, 0.76, 0.56), F, gora=(0.08, 0.16),
                        przes_gory=(zn * 0.14, -0.04))
            p.ostroslup("Ucho srodek " + s, (zn * 0.07, 0.38, 0.17), (0.46, 0.54, 0.03), "d_ucho", "matowy",
                        gora=(0.04, 0.02), przes_gory=(zn * 0.1, 0), faza=0.0)

    # rogi: między uszami, trzy człony — nasada odchylona na zewnątrz, czubek zagięty do środka (półksiężyc)
    for zn, s in ((1, "L"), (-1, "P")):
        x, y = zn * 0.4, gora - 0.05
        katy, dlugosci, szer = (34, 8, -20, -48), (0.24, 0.22, 0.22, 0.26), (0.36, 0.3, 0.23, 0.16, 0.0)
        for i in range(4):                                   # każdy człon zaczyna się tam, gdzie kończy poprzedni
            kat, dl = katy[i], dlugosci[i]
            with p.na("Head", pos=(x, y, 0.24 - 0.04 * i), obrot=(0, 0, -zn * kat), od="srodek"):
                p.ostroslup("Rog %s%d" % (s, i), (0, dl / 2 - 0.02, 0), (szer[i], dl + 0.06, szer[i]), "d_rog",
                            gora=(szer[i + 1], szer[i + 1]), faza=0.02 if i < 3 else 0.0)
                if i < 2:
                    p.blok("Rog pierscien %s%d" % (s, i), (0, dl * 0.55, 0), (szer[i] - 0.02, 0.03, szer[i] - 0.02),
                           "d_rog_jasny", "matowy", faza=0.0)
            x += zn * math.sin(math.radians(kat)) * dl
            y += math.cos(math.radians(kat)) * dl

    # ---------------- tułów: kremowa koszulka z dekoltem w serek, rąbek szerszy od tułowia
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        p.blok("Koszulka", (0, 0, 0), (w + 0.12, h + 0.06, d + 0.12), "d_koszulka", "matowy", faza=0.08)
        p.blok("Koszulka rabek", (0, -h / 2 + 0.03, 0), (w + 0.2, 0.14, d + 0.2), "d_koszulka", "matowy", faza=0.05)
        p.ostroslup("Dekolt", (0, h / 2 - 0.1, d / 2 + 0.065), (0.36, 0.26, 0.02), F, "matowy", rot=(0, 0, 180),
                    gora=(0.04, 0.02), faza=0.0)
    with p.na("LowerTorso", od="srodek"):
        w, h, d = p.wymiary("LowerTorso")
        sr = p.staw("LowerTorso")[1] + p.srodek("LowerTorso")[1]
        p.blok("Spodenki", (0, 0, 0), (w + 0.08, h + 0.06, d + 0.08), "d_spodenki", "matowy", faza=0.06)
        # cienki ogon wychodzi z tyłu spodenek i schodzi do stawu ogona
        p.blok("Ogon u nasady", (0.1, 0.5 - sr, -0.5), (0.15, 0.62, 0.15), F, faza=0.04)

    # ---------------- nogi: nogawki spodenek, gołe łydki, łapy z dwiema kreskami palców
    for s, zn in (("Left", 1), ("Right", -1)):
        with p.na(s + "UpperLeg"):
            p.blok("Nogawka", (0, -0.13, 0), (0.58, 0.32, 0.6), "d_spodenki", "matowy", faza=0.05)
        with p.na(s + "LowerLeg", od="srodek"):
            p.blok("Lydka", (0, 0, 0), (0.42, 0.3, 0.42), F, faza=0.05)
        with p.na(s + "Foot", od="srodek"):
            w, h, d = p.wymiary(s + "Foot")
            p.blok("Lapa", (0, 0, 0.04), (w, h, d), F, faza=0.06)
            p.blok("Lapa przod", (0, -0.01, d / 2 + 0.12), (w, h - 0.02, 0.3), F, faza=0.06)
            for i, x in enumerate((-0.09, 0.09)):
                p.blok("Palec kreska %d" % i, (x, 0.0, d / 2 + 0.262), (0.025, 0.11, 0.03), PR, "matowy", faza=0.0)

    # ---------------- ręce: krótki rękaw, gołe futro, łapka z kreskami palców i różowymi poduszkami od spodu dłoni
    for s, zn in (("Left", 1), ("Right", -1)):
        with p.na(s + "UpperArm", od="srodek"):
            w, h, d = p.wymiary(s + "UpperArm")
            p.blok("Futro ramie", (0, 0, 0), (w, h, d), F)
            p.blok("Rekaw", (0, h * 0.12, 0), (w + 0.16, h * 0.78, d + 0.16), "d_koszulka", "matowy", faza=0.05)
        with p.na(s + "LowerArm", od="srodek"):
            w, h, d = p.wymiary(s + "LowerArm")
            p.blok("Futro przedramie", (0, 0, 0), (w, h, d), F)
        with p.na(s + "Hand"):
            p.blok("Lapka", (0, -0.19, 0), (0.42, 0.34, 0.42), F, faza=0.08)
            for i, x in enumerate((-0.07, 0.07)):
                p.blok("Palec kreska %d" % i, (x, -0.3, 0.2), (0.025, 0.1, 0.03), PR, "matowy", faza=0.0)
            p.blok("Poduszka", (0, -0.27, -0.205), (0.17, 0.1, 0.02), "d_ucho", "matowy", faza=0.0)
            for i, x in enumerate((-0.1, 0.0, 0.1)):
                p.blok("Poduszka palec %d" % i, (x, -0.16, -0.205), (0.06, 0.06, 0.02), "d_ucho", "matowy", faza=0.0)

    # ---------------- ogon diabełka: cienki, na tych samych kościach co ogon Kota-Maga, na końcu grot
    with p.na("Tail", obrot=(0, -50, 0)):
        p.blok("Ogon nasada", (0, -0.06, -0.47), (0.15, 0.15, 1.02), F, faza=0.04)
    with p.na("TailTip", obrot=(0, -50, -26)):
        p.blok("Ogon srodek", (0, 0.24, 0), (0.15, 0.7, 0.15), F, faza=0.04)
        p.ostroslup("Grot ogona", (0, 0.76, 0), (0.44, 0.4, 0.11), F, gora=(0.03, 0.05), faza=0.02)

    for c in p.czesci:
        c["golas"] = True
    return KM.kopiuj_klipy(KM.postac_odniesienia(), p)


if __name__ == "__main__":
    if "--kontrola" in sys.argv:
        for p in zbuduj() + [podstawowy(), czlowiek_podstawowy(), wg_rzutow()]:
            b, u = p.sprawdz()
            print(p.id, "błędy:", len(b), "uwagi:", len(u))
            for x in b[:10]:
                print("  B", x)
            for x in u[:5]:
                print("  U", x)
