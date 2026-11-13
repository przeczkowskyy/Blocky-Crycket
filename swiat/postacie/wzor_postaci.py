# -*- coding: utf-8 -*-
"""WZÓR POSTACI — prosty klockowy ludzik R15 z jednym klipem. Kopiuj ten plik jako punkt startu.

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/wzor_postaci.py --wyj <folder> --klip machanie

Konwencje (pełna ściąga: biblioteka/README.md):
- 1 jednostka = 1 stud, Y w górę, postać patrzy w +Z, jej LEWA strona to +X (prawa ręka jest po stronie −X);
- najpierw szkielet (typ="r15" + ewentualne `wymiary`), potem bryły w blokach `with p.na("Kosc", od="srodek")`
  — wtedy (0, 0, 0) to środek klocka kości, a przednia ściana głowy leży na z = głębokość / 2;
- elementy twarzy wystają 0,02–0,05 przed ścianę (nigdy w tej samej płaszczyźnie — migotanie);
- obroty w stopniach (rx, ry, rz); dla ręki zwisającej: rx < 0 = do przodu, rz < 0 = prawa ręka na zewnątrz.
"""
from swiat.postacie.biblioteka.postac import Postac

ID = "wzor_ludzik"


def zbuduj():
    p = Postac(ID, "Wzorcowy ludzik", typ="r15",
               wymiary={"Head": (1.4, 1.35, 1.3),            # głowa trochę większa — przerysowanie
                        "Foot": (1.0, 0.35, 1.2)})           # buty wystają do przodu
    p.cialo({"glowa": "skora", "tulow": "zielony", "pas": "brazowy", "ramiona": "zielony",
             "LeftLowerArm": "skora", "RightLowerArm": "skora", "dlonie": "skora",
             "nogi": "niebieski_ciemny", "stopy": "brazowy_ciemny"})

    # --- twarz i włosy (układ: środek klocka głowy)
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        z = d / 2                                             # przednia ściana głowy
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * 0.3
            p.blok("Oko " + s, (x, 0.08, z + 0.01), (0.22, 0.36, 0.1), "tusz", "polysk", faza=0.03)
            p.blok("Blysk " + s, (x - 0.04, 0.17, z + 0.07), (0.08, 0.1, 0.04), "bialy", faza=0.0)
            p.blok("Brew " + s, (x, 0.37, z + 0.02), (0.3, 0.08, 0.08), "brazowy_ciemny", "matowy",
                   rot=(0, 0, -zn * 8), faza=0.0)                  # wewnętrzne końce wyżej = pogodna mina
            p.blok("Rumieniec " + s, (zn * 0.47, -0.2, z + 0.005), (0.18, 0.1, 0.04), "rumieniec", "matowy", faza=0.0)
            p.blok("Kacik " + s, (zn * 0.22, -0.29, z + 0.02), (0.08, 0.11, 0.08), "tusz", faza=0.0)
        p.blok("Nos", (0, -0.08, z + 0.05), (0.16, 0.18, 0.12), "skora_cien", "matowy", faza=0.03)
        p.blok("Usta", (0, -0.34, z + 0.02), (0.4, 0.08, 0.08), "tusz", faza=0.0)
        p.blok("Wlosy", (0, h / 2 + 0.12, -0.04), (w + 0.1, 0.34, d + 0.06), "brazowy", "matowy")
        p.blok("Grzywka", (0, h / 2 - 0.08, z + 0.02), (w + 0.1, 0.22, 0.2), "brazowy", "matowy", rot=(0, 0, -3))
        p.blok("Wlosy tyl", (0, 0.2, -z - 0.04), (w + 0.06, 0.9, 0.14), "brazowy", "matowy")
        for zn in (1, -1):
            p.blok("Bak", (zn * (w / 2 + 0.04), 0.18, -0.12), (0.12, 0.62, d - 0.2), "brazowy", "matowy")

    # --- ubranie: lamówka tuniki, pas z klamrą, wywinięcia butów
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        p.blok("Lamowka", (0, -h / 2 + 0.09, 0), (w + 0.08, 0.18, d + 0.08), "zielony_ciemny")
        p.blok("Dekolt", (0, h / 2 - 0.12, d / 2 + 0.01), (0.5, 0.26, 0.06), "skora", faza=0.02)
    with p.na("LowerTorso", od="srodek"):
        w, h, d = p.wymiary("LowerTorso")
        p.blok("Klamra", (0, 0, d / 2 + 0.03), (0.36, 0.3, 0.08), "zloto", "metal", faza=0.03)
    for s in ("Left", "Right"):
        with p.na(s + "Foot", od="srodek"):
            w, h, d = p.wymiary(s + "Foot")
            p.blok("Cholewka", (0, h / 2 + 0.06, -0.08), (w + 0.08, 0.14, 1.06), "brazowy")

    # --- klip: machanie prawą ręką (36 klatek = 1,2 s, pętla)
    k = p.klip("machanie", 36, petla=True)
    k.poza(0, {"RightUpperArm": (-10, 0, -150),              # ręka w górze, na zewnątrz (prawa = −rz)
               "LeftUpperArm": (0, 0, 4)})
    k.cykl("RightLowerArm", "obrot", (0, 0, 24), czestosc=2)  # przedramię macha dwa razy na pętlę
    k.cykl("Head", "obrot", (0, 0, 5))                        # głowa przechyla się w rytm
    k.cykl("UpperTorso", "obrot", (0, 4, 2), faza=0.25)
    k.cykl("LeftLowerArm", "obrot", (-6, 0, 0), srodek=(-8, 0, 0))
    p.ustaw_poze_renderu("machanie", 9)                       # rendery: ręka w górze, nie poza spoczynkowa
    return p
