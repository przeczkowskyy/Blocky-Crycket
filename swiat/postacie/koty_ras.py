# -*- coding: utf-8 -*-
"""KOTY RAS — elf, mroczny elf, ork, goblin i półbóg jako warianty Kota-Maga (Paweł 24.11: „na bazie referencji
pozostałe modele kotków”; referencje assets/raw/RasyKoty/koty_rasy_plansza.jpg, notatka
B&C/Postacie/Rasy jako koty — referencje.md). Status: propozycja.

Zasada jak w kot_demon.py: TEN SAM model co Kot-Mag (swiat/postacie/kot_mag.py — wymiary, kości, klipy, kapelusz,
szata, kostur), zmienia się tylko wygląd. Pliku Karola nie zmieniamy: każda rasa wczytuje WŁASNĄ kopię modułu
kot_mag (importlib), podmienia paletę i dokłada cechy rasy na tych samych kościach.
Uwaga Pawła (obowiązkowa): elfy, mroczny elf i goblin mają TYLKO dwa kocie uszy — o rasie mówi kolor, włosy, oczy
i nos, nie dodatkowe uszy.

  ELF          kremowe futro, długie złote włosy, zielone oczy; szata i kapelusz zielone ze złotem, zielony kryształ;
  MROCZNY ELF  lawendowe futro, długie białe włosy, fioletowe oczy; szata granatowo-fioletowa ze srebrem;
  ORK          oliwkowe futro z ciemnymi pręgami, kły, czarny kok, groźne brwi; szata brązowa, kryształ jak kość;
  GOBLIN       limonkowe futro, zakrzywiony nos jak na referencji, groźne brwi, uśmiech z ząbkami; szata pomarańczowa, zielony kryształ;
  PÓŁBÓG       złote futro, świecące turkusowe oczy, złota aureola; szata biała ze złotem, kryształ jak gwiazda.

Dwie wersje każdej rasy (jak u demona): zbuduj_<rasa>() — pełny strój Kota-Maga w barwach rasy;
podstawowy_<rasa>() — koszulka i spodenki (kot_demon._stroj_podstawowy), bez przedmiotów. W wyborze rasy stoją
wersje podstawowe (tools/studio/koty_ras_studio.py).

    python -B swiat/postacie/koty_ras.py --kontrola       # sprawdzian biblioteki (bez Blendera)
"""
import importlib.util
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(TU)))

from swiat.postacie import kot_demon as KD  # noqa: E402  (strój podstawowy)

# paleta: futro, strój pełny (szata/kapelusz/wstążka/kryształ) i strój podstawowy (koszulka/spodenki) + cechy
RASY = {
    "elf": {"nazwa": "Kot-Elf", "paleta": {
        "kot": "F3E3C8", "kot_jasny": "FFF6E6", "kot_ciemny": "D9C29E",
        "szata": "2F8F4E", "szata_ciemna": "1F6136", "szata_jasna": "4DB06B",
        "wstazka": "E8B93A", "krysztal": "4CE38A", "krysztal_jasny": "A8FFC6",
        "wlosy": "F2C94C", "wlosy_cien": "D9A92E", "oko_rasy": "3FBF5A",
        "koszulka": "F1E6CC", "spodenki": "2F8F4E"}},
    "mroczny_elf": {"nazwa": "Kot-Mroczny elf", "paleta": {
        "kot": "9C8FC4", "kot_jasny": "C9C0E6", "kot_ciemny": "7A6CA6",
        "szata": "2B2547", "szata_ciemna": "1A1630", "szata_jasna": "433A6B",
        "wstazka": "C9CED8", "krysztal": "B98CFF", "krysztal_jasny": "E2D2FF",
        "wlosy": "F1EEF7", "wlosy_cien": "CFCBE0", "oko_rasy": "B36BFF",
        "koszulka": "F1E6CC", "spodenki": "433A6B"}},
    "ork": {"nazwa": "Kot-Ork", "paleta": {
        "kot": "6F8A3A", "kot_jasny": "9DB36A", "kot_ciemny": "4E6427",
        "szata": "7A4E2C", "szata_ciemna": "5A361C", "szata_jasna": "9A6A40",
        "wstazka": "3A2A1C", "krysztal": "E8E0CC", "krysztal_jasny": "FFF8E8",
        "wlosy": "1E1A17", "wlosy_cien": "0F0D0B", "kiel": "FFF8E8",
        "koszulka": "F1E6CC", "spodenki": "7A4E2C"}},
    "goblin": {"nazwa": "Kot-Goblin", "paleta": {
        "kot": "92CF3A", "kot_jasny": "C6EB8A", "kot_ciemny": "86C232", "nos": "5E9A22",
        "szata": "E07A1F", "szata_ciemna": "B35A10", "szata_jasna": "F59A45",
        "wstazka": "6B4325", "krysztal": "6CFF6C", "krysztal_jasny": "C8FFC8",
        "koszulka": "F1E6CC", "spodenki": "B35A10"}},
    "polbog": {"nazwa": "Kot-Półbóg", "paleta": {
        "kot": "F2C230", "kot_jasny": "FFE58A", "kot_ciemny": "D49A1A",
        "szata": "F4F1EA", "szata_ciemna": "D9D3C4", "szata_jasna": "FFFFFF",
        "wstazka": "E8B93A", "krysztal": "FFF3A0", "krysztal_jasny": "FFFBE0",
        "oko_rasy": "5FF2FF", "aureola": "FFD54A",
        "koszulka": "F4F1EA", "spodenki": "E8B93A"}},
}


def _modul(rasa):
    """Świeża, prywatna kopia kot_mag z paletą rasy (prawdziwy Kot-Mag bez zmian)."""
    spec = importlib.util.spec_from_file_location("kot_mag_dla_" + rasa, os.path.join(TU, "kot_mag.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.PALETA.update(RASY[rasa]["paleta"])
    return m


# ------------------------------------------------------------------------------------------- cechy ras
def _oczy(p, kolor, mat="polysk"):
    """Kolorowa tęczówka na czarnym oku Kota-Maga (czarny brzeg zostaje), jak u demona."""
    w, h, d = p.wymiary("Head")
    with p.na("Head", od="srodek"):
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Oko rasy " + s, (zn * 0.38, 0.1, d / 2 + 0.045), (0.22, 0.32, 0.02), kolor, mat, faza=0.0)


def _wlosy_dlugie(p):
    """Długie włosy elfów: czapka na czubku (uszy ją przebijają), grzywka nad oczami, pasma po bokach i z tyłu
    do ramion. Boki głowy zakryte włosami — bez dodatkowych uszu."""
    w, h, d = p.wymiary("Head")
    z = d / 2
    with p.na("Head", od="srodek"):
        p.blok("Wlosy czubek", (0, h / 2 + 0.05, -0.04), (w + 0.12, 0.12, d + 0.04), "wlosy", "matowy", faza=0.04)
        for zn, s in ((1, "L"), (-1, "P")):
            # grzywka zaczesana na boki (środek czoła odsłonięty, oczy wolne)
            p.blok("Grzywka " + s, (zn * 0.42, h / 2 - 0.12, z + 0.04), (0.78, 0.22, 0.08), "wlosy", "matowy",
                   rot=(0, 0, zn * 14), faza=0.02)
            # pasma z przodu po bokach twarzy, aż na ramiona (jak na ikonie rasy)
            p.blok("Pasmo przod " + s, (zn * (w / 2 - 0.06), -0.25, z - 0.02), (0.28, h + 0.2, 0.16), "wlosy",
                   "matowy", faza=0.03)
            p.blok("Pasmo cien " + s, (zn * (w / 2 - 0.12), -0.5, z + 0.07), (0.12, 0.6, 0.04), "wlosy_cien",
                   "matowy", faza=0.0)
            p.blok("Wlosy bok " + s, (zn * (w / 2 + 0.06), -0.25, -0.1), (0.14, h + 0.4, d - 0.15), "wlosy",
                   "matowy", faza=0.03)
        p.blok("Wlosy tyl", (0, -0.3, -z - 0.07), (w + 0.14, h + 0.6, 0.14), "wlosy", "matowy", faza=0.03)


def _cechy_elf(p):
    _wlosy_dlugie(p)
    _oczy(p, "oko_rasy")
    return p


def _cechy_mroczny_elf(p):
    _wlosy_dlugie(p)
    _oczy(p, "oko_rasy")
    w, h, d = p.wymiary("Head")
    with p.na("Head", od="srodek"):
        for zn, s in ((1, "L"), (-1, "P")):  # spokojne, lekko uniesione brwi
            p.blok("Brew " + s, (zn * 0.36, 0.4, d / 2 + 0.03), (0.3, 0.06, 0.05), "kot_ciemny", "matowy",
                   rot=(0, 0, -zn * 8), faza=0.0)
    return p


def _cechy_ork(p):
    w, h, d = p.wymiary("Head")
    z = d / 2
    with p.na("Head", od="srodek"):
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Brew " + s, (zn * 0.36, 0.42, z + 0.03), (0.4, 0.1, 0.05), "kot_ciemny", "matowy",
                   rot=(0, 0, zn * 18), faza=0.0)
            p.ostroslup("Kiel " + s, (zn * 0.3, -0.36, z + 0.06), (0.12, 0.2, 0.08), "kiel", "polysk",
                        gora=(0.0, 0.0), faza=0.0)
            p.blok("Prega " + s, (zn * (w / 2 - 0.25), h / 2 - 0.25, z + 0.01), (0.1, 0.32, 0.02), "kot_ciemny",
                   "matowy", faza=0.0)
        p.blok("Prega srodek", (0, h / 2 - 0.12, z + 0.01), (0.1, 0.22, 0.02), "kot_ciemny", "matowy", faza=0.0)
        # czarny kok na czubku, przewiązany rzemieniem
        p.blok("Kok nasada", (0, h / 2 + 0.06, -0.1), (0.5, 0.12, 0.5), "wlosy", "matowy", faza=0.03)
        p.blok("Rzemien", (0, h / 2 + 0.16, -0.1), (0.3, 0.08, 0.3), "kot_ciemny", "matowy", faza=0.0)
        p.kula("Kok", (0, h / 2 + 0.38, -0.12), (0.42, 0.42, 0.42), "wlosy", "matowy")
    return p


def _cechy_goblin(p):
    """Goblin według referencji assets/raw/RasyKoty (Paweł 24.11: „popraw cały model, żeby pasował do referencji”):
    limonkowe futro bez pręg (kot_ciemny prawie jak futro), zielone wnętrza uszu (kolor „nos” — różowy nosek i tak
    zasłania nos goblina), grube ciemnozielone groźne brwi opadające ku środkowi, zakrzywiony nos w kolorze futra
    (nasada między oczami, garb do przodu, czubek zgięty w dół i w bok), szeroki chytry uśmiech z ząbkami i kiełkiem
    przesunięty w bok, brązowe rumieńce. Tylko dwa kocie uszy (zasada Pawła)."""
    w, h, d = p.wymiary("Head")
    z = d / 2
    with p.na("Head", od="srodek"):
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Brew " + s, (zn * 0.37, 0.42, z + 0.04), (0.44, 0.14, 0.07), "3F7F1E", "matowy",
                   rot=(0, 0, zn * 18), faza=0.015)
            p.blok("Rumieniec " + s, (zn * 0.57, -0.19, z + 0.045), (0.34, 0.12, 0.02), "B98A5E", "matowy", faza=0.0)
        # nos: nasada między oczami -> garb -> czubek w dół i lekko w prawo figury (w lewo dla patrzącego)
        p.blok("Nos nasada", (0, 0.1, z + 0.07), (0.18, 0.32, 0.12), "kot", "matowy", rot=(-25, 0, 0), faza=0.03)
        p.blok("Nos garb", (-0.02, -0.09, z + 0.18), (0.25, 0.26, 0.2), "kot", "matowy", rot=(-40, 0, 6), faza=0.04)
        p.ostroslup("Nos czubek", (-0.06, -0.27, z + 0.25), (0.23, 0.32, 0.2), "kot", "matowy", rot=(160, 0, 15),
                    gora=(0.0, 0.0), faza=0.02)
        p.blok("Nos cien", (0.1, -0.08, z + 0.17), (0.03, 0.3, 0.12), "6FA82A", "matowy", rot=(-35, 0, 6), faza=0.0)
        # chytry uśmiech od nosa w lewo figury (w prawo dla patrzącego), z ząbkami i kiełkiem — na wierzchu
        # pyszczka Kota-Maga (przód pyszczka ok. z + 0,07); kocie usta „w” zakryte łatą w kolorze pyszczka
        p.blok("Zaslona ust", (0, -0.37, z + 0.085), (0.44, 0.07, 0.02), "kot_jasny", "matowy", faza=0.0)
        p.blok("Usmiech", (0.12, -0.43, z + 0.095), (0.52, 0.05, 0.03), "tusz", "matowy", rot=(0, 0, 9), faza=0.0)
        p.blok("Zeby", (0.12, -0.47, z + 0.09), (0.44, 0.07, 0.025), "FFF8E8", "polysk", rot=(0, 0, 9), faza=0.0)
        p.ostroslup("Kielek", (0.3, -0.52, z + 0.09), (0.07, 0.09, 0.03), "FFF8E8", "polysk", rot=(0, 0, 180),
                    gora=(0.0, 0.0), faza=0.0)
        p.blok("Kacik", (0.39, -0.37, z + 0.095), (0.09, 0.05, 0.03), "tusz", "matowy", rot=(0, 0, 40), faza=0.0)
    return p


def _cechy_polbog(p):
    _oczy(p, "oko_rasy", "swiecacy")
    w, h, d = p.wymiary("Head")
    with p.na("Head", od="srodek"):
        # aureola: pierścień z 12 klocków nad głową (między uszami i nad nimi)
        r, n = 0.55, 12
        for i in range(n):
            a = 2 * math.pi * i / n
            p.blok("Aureola %d" % i, (r * math.cos(a), h / 2 + 0.75, r * math.sin(a)), (0.3, 0.07, 0.1), "aureola",
                   "swiecacy", rot=(0, -math.degrees(a) + 90, 0), faza=0.0)
    return p


CECHY = {"elf": _cechy_elf, "mroczny_elf": _cechy_mroczny_elf, "ork": _cechy_ork, "goblin": _cechy_goblin,
         "polbog": _cechy_polbog}


def zbuduj_rase(rasa):
    """[Kot rasy w pełnym stroju Kota-Maga w barwach rasy]."""
    m = _modul(rasa)
    prz = m.przedmioty()
    p = m.ubierz(m.cialo(), m.wybierz(m.KANON, prz), id="kot_" + rasa, nazwa=RASY[rasa]["nazwa"],
                 korekty=m.KOREKTY_CHWYTU)
    return CECHY[rasa](p)


def podstawowy(rasa):
    """Kot rasy w stroju bazowym: koszulka i spodenki, bez kapelusza, szaty i kostura."""
    m = _modul(rasa)
    p = m.cialo()
    p.id, p.nazwa = "kot_%s_podstawowy" % rasa, RASY[rasa]["nazwa"] + " (strój podstawowy)"
    return CECHY[rasa](KD._stroj_podstawowy(p))


def zbuduj():
    return [zbuduj_rase(r) for r in RASY] + [podstawowy(r) for r in RASY]


if __name__ == "__main__":
    if "--kontrola" in sys.argv:
        for p in zbuduj():
            b, u = p.sprawdz()
            print(p.id, "błędy:", len(b), "uwagi:", len(u))
            for x in b[:10]:
                print("  B", x)
