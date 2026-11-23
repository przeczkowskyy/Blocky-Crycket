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
    })
    return m


KM = _kot_mag()
PALETA = KM.PALETA


def _cechy_demona(p):
    """Rogi, oczy, brwi, kieł i grot ogona — na kościach Kota-Maga (układ jak w kot_mag._golas)."""
    w, h, d = p.wymiary("Head")
    with p.na("Head", od="srodek"):
        z = d / 2
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * 0.38
            # żółta tęczówka na czarnym oku (czarny brzeg zostaje), błyski Kota-Maga leżą przed nią
            p.blok("Oko demona " + s, (x, 0.1, z + 0.045), (0.22, 0.32, 0.02), "oko_demona", "polysk", faza=0.0)
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
    return [_cechy_demona(p)]


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
    return _cechy_demona(_stroj_podstawowy(p))


def czlowiek_podstawowy():
    """Rasa Człowiek jako kot (Paweł 23.11): nasz rudy Kot-Mag bez zmian wyglądu, w stroju podstawowym jak ludzik rasy
    Człowiek z planszy D-104 — kremowa koszulka i niebieskie spodenki. Osobna kopia kot_mag z dopisanymi kolorami."""
    spec = importlib.util.spec_from_file_location("kot_mag_dla_czlowieka", os.path.join(TU, "kot_mag.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.PALETA.update({"koszulka": "F1E6CC", "spodenki": "2F6FD6"})
    p = m.cialo()
    p.id, p.nazwa = "kot_czlowiek_podstawowy", "Kot-Człowiek (strój podstawowy)"
    return _stroj_podstawowy(p)


if __name__ == "__main__":
    if "--kontrola" in sys.argv:
        for p in zbuduj() + [podstawowy(), czlowiek_podstawowy()]:
            b, u = p.sprawdz()
            print(p.id, "błędy:", len(b), "uwagi:", len(u))
            for x in b[:10]:
                print("  B", x)
            for x in u[:5]:
                print("  U", x)
