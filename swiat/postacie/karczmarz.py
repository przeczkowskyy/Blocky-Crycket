# -*- coding: utf-8 -*-
"""KARCZMARZ — gospodarz gospody (NPC). Gruby, szeroki klockowy ludzik R15: wielki brzuch, krótkie nogi,
pełne brązowe włosy zaczesane na bok, sumiaste wąsy, oczy zamknięte w uśmiechu, biała koszula z podwiniętymi
rękawami, brązowa kamizelka, brązowe spodnie i buty; w prawej dłoni chochla z gulaszem.

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/karczmarz.py --wyj <folder> --klip zaproszenie

Klipy: idle (lewa ręka na biodrze, oddech), zaproszenie (szeroki gest lewą ręką), smiech (głowa w tył, brzuch podskakuje).
Status: propozycja (wygląd wg obrazu referencyjnego gry i notatki B&C/Postacie/Karczmarz.md; nie kanon).
Konwencje: 1 jednostka = 1 stud, Y w górę, postać patrzy w +Z, jej LEWA strona to +X.
"""
from swiat.postacie.biblioteka.postac import Postac, Akcesorium

ID = "karczmarz"

PALETA = {
    "koszula": "F4F0E6",          # biała koszula
    "koszula_cien": "DCD3C2",     # podwinięte mankiety, kołnierz od spodu
    "kamizelka": "7E4A24",        # brązowa kamizelka (cieplejsza niż spodnie)
    "kamizelka_lam": "4E2C14",    # lamówka kamizelki
    "spodnie": "5C3A1E",
    "but": "3A2414",
    "but_jasny": "53351C",
    "podeszwa": "22150B",
    "pas": "33200F",
    "wlosy": "6B3F1F",
    "wlosy_jasne": "86532B",      # pasmo zaczesanych włosów
    "wasy": "5A3318",
    "nos": "EBA582",
    "lysina": "FFE0C2",           # blik na łysinie
    "usta": "3B1A1A",
    "jezyk": "D9534A",
    "zupa": "E0832E",             # gulasz w chochli
    "drewno": "B57E47",
}


def chochla():
    """Chochla na RightGripAttachment: trzonek wzdłuż +Y, czerpak na górze otwarty ku +Z (w pozie trzymania — ku widzowi)."""
    a = Akcesorium("karczmarz_chochla", "Chochla karczmarza", zaczep="RightGripAttachment", typ="Inne",
                   paleta=PALETA, ikona_obrot=(0, 0, -30))
    a.walec("Raczka", (0, 0.0, 0), (0.24, 0.9, 0.24), "drewno", "matowy", segm=8)
    a.walec("Okucie", (0, 0.48, 0), (0.27, 0.1, 0.27), "stal_cien", "metal", segm=8)
    a.walec("Trzonek", (0, 1.0, 0), (0.13, 1.0, 0.13), "stal", "metal", segm=8)
    a.blok("Koniec", (0, -0.5, 0), (0.3, 0.12, 0.3), "brazowy_ciemny", "matowy")
    # szyjka zagięta na zewnątrz (−X = na zewnątrz prawej dłoni), czerpak otwarty ku górze
    a.walec("Szyjka", (-0.2, 1.62, 0), (0.13, 0.55, 0.13), "stal", "metal", rot=(0, 0, 50), segm=8)
    with a.uklad(pos=(-0.62, 1.62, 0)):
        a.walec("Czerpak", (0, 0.08, 0), (0.9, 0.3, 0.9), "stal", "metal", segm=12)
        a.kula("Dno czerpaka", (0, -0.1, 0), (0.9, 0.42, 0.9), "stal_cien", "metal", segm=12)
        a.walec("Gulasz", (0, 0.2, 0), (0.74, 0.08, 0.74), "zupa", "polysk", segm=12)
        a.blok("Kawalek", (0.12, 0.26, 0.1), (0.2, 0.08, 0.16), "brazowy", "matowy", faza=0.0)
        a.blok("Kawalek 2", (-0.14, 0.25, -0.12), (0.15, 0.08, 0.13), "zielony", "matowy", faza=0.0)
    return a


def zbuduj():
    p = Postac(ID, "Karczmarz", typ="r15", skala=1.0, faza=0.05, paleta=PALETA,
               wymiary={"Head": (1.8, 1.6, 1.55),
                        "UpperTorso": (3.0, 1.9, 2.0),
                        "LowerTorso": (2.8, 0.5, 1.9),
                        "UpperArm": (0.9, 1.0, 0.9),
                        "LowerArm": (0.85, 0.8, 0.85),
                        "Hand": (0.95, 0.4, 0.95),
                        # lewa dłoń otwarta (gest zaproszenia, ręka na biodrze): płaska, palce wzdłuż kości
                        "LeftHand": (0.3, 0.8, 1.0),
                        "UpperLeg": (1.1, 0.55, 1.1),
                        "LowerLeg": (1.05, 0.5, 1.05),
                        "Foot": (1.15, 0.35, 1.5)},
               rozstaw_rak=2.2)            # +0,25: przedramię nie wchodzi w brzuch
    p.cialo({"glowa": "skora", "tulow": "kamizelka", "pas": "spodnie", "ramiona": "koszula",
             "LeftLowerArm": "skora", "RightLowerArm": "skora", "dlonie": "skora",
             "LeftUpperLeg": "spodnie", "RightUpperLeg": "spodnie",
             "LeftLowerLeg": "but", "RightLowerLeg": "but", "stopy": "but"})

    # --- głowa: zaczesane włosy, oczy-łuki, wąsy, nos, uśmiech
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        z = d / 2
        # pełne, zaczesane na bok brązowe włosy (jak w KeyArcie): czapa na czubku, grzywka-klin na bok, tył do karku,
        # boki i baczki do linii uszu
        p.blok("Wlosy czapa", (0, h / 2 + 0.12, -0.02), (w + 0.1, 0.35, d + 0.06), "wlosy", "matowy", faza=0.08)
        p.blok("Wlosy pasmo", (0.12, h / 2 + 0.3, 0.05), (w - 0.5, 0.1, d - 0.4), "wlosy_jasne", "matowy", faza=0.04)
        p.klin("Grzywka", (0.3, h / 2 - 0.08, z + 0.07), (0.75, 0.3, 0.2), "wlosy", "matowy", rot=(0, 0, -12),
               faza=0.04)
        p.blok("Grzywka nasada", (-0.25, h / 2 - 0.02, z + 0.02), (1.0, 0.16, 0.12), "wlosy", "matowy", faza=0.03)
        p.blok("Wlosy tyl", (0, 0.05, -z - 0.07), (w + 0.12, h - 0.25, 0.18), "wlosy", "matowy", faza=0.05)
        for zn in (1, -1):
            s = "L" if zn > 0 else "P"
            p.blok("Wlosy bok " + s, (zn * (w / 2 + 0.06), 0.3, -0.18), (0.16, 0.7, d - 0.25), "wlosy", "matowy")
            p.blok("Bak " + s, (zn * (w / 2 + 0.04), -0.05, 0.4), (0.12, 0.6, 0.28), "wlosy", "matowy")
            p.blok("Ucho " + s, (zn * (w / 2 + 0.1), 0.04, 0.0), (0.18, 0.38, 0.3), "skora_cien", "matowy")
            # oczy zamknięte w uśmiechu: łuk „^” z dwóch kresek
            xo = zn * 0.38
            p.blok("Oko a " + s, (xo - 0.08, 0.1, z + 0.02), (0.2, 0.075, 0.06), "tusz", faza=0.0, rot=(0, 0, 28))
            p.blok("Oko b " + s, (xo + 0.08, 0.1, z + 0.02), (0.2, 0.075, 0.06), "tusz", faza=0.0, rot=(0, 0, -28))
            p.blok("Brew " + s, (xo, 0.38, z + 0.03), (0.44, 0.12, 0.08), "wlosy", "matowy", rot=(0, 0, zn * 8),
                   faza=0.0)
            p.blok("Policzek " + s, (zn * 0.6, -0.1, z + 0.005), (0.28, 0.16, 0.04), "rumieniec", "matowy", faza=0.0)
            # wąsy: skrzydło + podkręcony koniec
            p.blok("Was " + s, (zn * 0.42, -0.24, z + 0.07), (0.44, 0.19, 0.14), "wasy", "matowy",
                   rot=(0, 0, zn * 18))
            p.blok("Was koniec " + s, (zn * 0.66, -0.07, z + 0.06), (0.15, 0.26, 0.12), "wasy", "matowy",
                   rot=(0, 0, zn * -20))
        p.blok("Was srodek", (0, -0.27, z + 0.08), (0.5, 0.22, 0.16), "wasy", "matowy")
        p.blok("Nos", (0, -0.04, z + 0.15), (0.38, 0.34, 0.3), "nos", "matowy", faza=0.08)
        p.blok("Usta", (0, -0.46, z + 0.015), (0.5, 0.2, 0.06), "usta", faza=0.0)
        p.blok("Zeby", (0, -0.39, z + 0.03), (0.4, 0.06, 0.04), "bialy", faza=0.0)
        p.blok("Jezyk", (0, -0.52, z + 0.03), (0.26, 0.07, 0.04), "jezyk", faza=0.0)
        p.blok("Podbrodek", (0, -h / 2 + 0.02, z - 0.12), (1.2, 0.2, 0.3), "skora", faza=0.06)

    # --- tułów: kamizelka (klocek ciała) + biała koszula z przodu i wielki brzuch
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.blok("Koszula przod", (0, 0.05, z + 0.03), (1.3, h - 0.1, 0.08), "koszula", "matowy")
        # brzuch z dwóch klocków z dużą fazą (klockowy, nie kula): przód 2,3 × 1,5 × 0,55 i wysunięty środek
        # 1,9 × 1,0 × 0,35; pod spodem pas cienia (biała koszula nie szarzeje od cieniowania kuli)
        p.blok("Brzuch", (0, -0.42, z + 0.27), (2.3, 1.5, 0.55), "koszula", "matowy", faza=0.12)
        # środek jako ścięty ostrosłup (podstawa 1,9 × 1,1, czoło 1,4 × 0,7) — miękki „kopiec”, nie szuflada
        p.ostroslup("Brzuch srodek", (0, -0.42, z + 0.7), (1.9, 0.32, 1.1), "koszula", "matowy", rot=(90, 0, 0),
                    gora=(1.4, 0.7))
        p.blok("Brzuch cien", (0, -1.12, z + 0.5), (1.8, 0.1, 0.6), "koszula_cien", "matowy", faza=0.0)
        p.blok("Rabek kamizelki", (0, -h / 2 + 0.06, 0), (w + 0.1, 0.12, d + 0.1), "kamizelka_lam", "matowy",
               faza=0.0)
        for zn in (1, -1):
            s = "L" if zn > 0 else "P"
            p.blok("Pola kamizelki " + s, (zn * 1.28, 0.05, z + 0.24), (0.46, h - 0.2, 0.5), "kamizelka", "matowy")
            p.blok("Lamowka " + s, (zn * 1.04, 0.05, z + 0.26), (0.08, h - 0.18, 0.52), "kamizelka_lam", "matowy",
                   faza=0.0)
            p.klin("Kolnierz " + s, (zn * 0.3, h / 2 + 0.06, z - 0.12), (0.42, 0.22, 0.34), "koszula",
                   rot=(0, 0, zn * -12))
        p.blok("Dekolt", (0, h / 2 - 0.15, z + 0.08), (0.28, 0.28, 0.03), "skora", rot=(0, 0, 45), faza=0.0)
        p.blok("Guzik 0", (0, 0.5, z + 0.09), (0.12, 0.12, 0.04), "koszula_cien", faza=0.0)
        p.blok("Guzik 1", (0, 0.2, z + 0.57), (0.12, 0.12, 0.04), "koszula_cien", faza=0.0)
        p.blok("Szyja", (0, h / 2 + 0.04, -0.05), (1.0, 0.1, 0.9), "skora", faza=0.0)

    # --- pas: dolny brzuch nad paskiem, pas z klamrą
    with p.na("LowerTorso", od="srodek"):
        w, h, d = p.wymiary("LowerTorso")
        z = d / 2
        p.blok("Pasek", (0, -0.02, 0), (w + 0.08, 0.22, d + 0.08), "pas", "matowy")
        p.blok("Pasek przod", (0, -0.02, z + 0.35), (2.2, 0.22, 0.72), "pas", "matowy")
        p.blok("Klamra", (0, -0.02, z + 0.72), (0.36, 0.3, 0.06), "zloto", "metal", faza=0.03)

    # --- ręce: podwinięte rękawy
    for s in ("Left", "Right"):
        with p.na(s + "UpperArm", od="srodek"):
            w, h, d = p.wymiary(s + "UpperArm")
            zw = 1 if s == "Left" else -1                   # strona zewnętrzna; bufka rękawa sięga 0,3 w stronę barku
            p.blok("Mankiet", (0, -h / 2 + 0.14, 0), (w + 0.12, 0.28, d + 0.12), "koszula_cien", "matowy")
            p.blok("Bufka", (-zw * 0.14, h / 2 - 0.25, 0), (w + 0.28, 0.5, d + 0.1), "koszula", "matowy", faza=0.1)
        with p.na(s + "LowerArm", od="srodek"):
            w, h, d = p.wymiary(s + "LowerArm")
            p.blok("Lokiec", (0, h / 2 + 0.12, 0), (w - 0.06, 0.36, d - 0.06), "skora", faza=0.0)
        with p.na(s + "Hand", od="srodek"):
            w, h, d = p.wymiary(s + "Hand")
            if s == "Left":                                  # otwarta dłoń: palce (ciemniejszy pas) i odstający kciuk
                p.blok("Palce", (0, -h / 2 + 0.17, 0), (w + 0.02, 0.32, d + 0.02), "skora", faza=0.04)
                p.blok("Palce szpara", (0, -h / 2 + 0.33, 0), (w + 0.04, 0.03, d - 0.1), "skora_cien", faza=0.0)
                p.blok("Kciuk", (0, h / 2 - 0.22, d / 2 + 0.12), (0.26, 0.3, 0.3), "skora", faza=0.05,
                       rot=(-25, 0, 0))
            else:
                p.blok("Kciuk", (w / 2 - 0.12, 0.0, d / 2 + 0.06), (0.24, 0.3, 0.16), "skora_cien", faza=0.03)
        with p.na(s + "UpperLeg", od="srodek"):
            w, h, d = p.wymiary(s + "UpperLeg")
            p.blok("Nogawka", (0, -h / 2 + 0.06, 0), (w + 0.06, 0.12, d + 0.06), "spodnie", "matowy")
        with p.na(s + "LowerLeg", od="srodek"):
            w, h, d = p.wymiary(s + "LowerLeg")
            p.blok("Cholewa", (0, h / 2 - 0.1, 0), (w + 0.14, 0.2, d + 0.14), "but_jasny", "matowy")
        with p.na(s + "Foot", od="srodek"):
            w, h, d = p.wymiary(s + "Foot")
            p.blok("Podeszwa", (0, -h / 2 + 0.05, 0), (w + 0.06, 0.1, d + 0.06), "podeszwa", "matowy")
            p.blok("Czubek", (0, 0.0, d / 2 - 0.1), (w - 0.1, h - 0.05, 0.3), "but_jasny", "matowy")

    # chochla: osobny przedmiot (przedmioty/karczmarz_chochla.fbx); w FBX postaci jej nie ma, w renderach jest w dłoni
    ch = chochla()
    p.zaloz(ch, eksport=False)

    # --- klipy
    BAZA = {"LeftUpperArm": (6, 0, 32), "LeftLowerArm": (0, 0, -68), "LeftHand": (0, 0, -8),
            "RightUpperArm": (-18, 0, -8), "RightLowerArm": (-70, 0, 0)}

    k = p.klip("idle", 60, petla=True)
    k.poza(0, BAZA)
    k.cykl("UpperTorso", "obrot", (-1.5, 0, 0))
    k.cykl("UpperTorso", "przes", (0, 0.03, 0), faza=0.25)
    k.cykl("Head", "obrot", (2.0, 0, 1.5), faza=0.1)
    k.cykl("RightLowerArm", "obrot", (-3, 0, 0), faza=0.15)

    k = p.klip("zaproszenie", 60, petla=True)
    k.poza(0, BAZA)
    gest = {"LeftUpperArm": (-35, 0, 82), "LeftLowerArm": (-20, 0, 22), "LeftHand": (0, -30, 10),
            "RightUpperArm": (-20, 0, -30), "RightLowerArm": (-55, 0, 0),
            "UpperTorso": (-5, 10, 0), "Head": (-6, 12, 6)}
    k.poza(16, gest)
    k.poza(40, {**gest, "LeftUpperArm": (-32, 0, 78), "Head": (-3, 10, 4)})
    k.poza(60, {**BAZA, "UpperTorso": (0, 0, 0), "Head": (0, 0, 0)})
    k.poza(0, {"UpperTorso": (0, 0, 0), "Head": (0, 0, 0)})

    k = p.klip("smiech", 40, petla=True)
    k.poza(0, {"LeftUpperArm": (-30, 0, 25), "LeftLowerArm": (-55, 0, -45),
               "RightUpperArm": (-35, 0, -14), "RightLowerArm": (-60, 0, 0),
               "UpperTorso": (-7, 0, 0), "Head": (-10, 0, 0)})
    k.cykl("UpperTorso", "przes", (0, 0.1, 0), czestosc=4)
    # bez kanału skali (Roblox go nie przenosi): brzuch „podskakuje” przesunięciem i kiwnięciem tułowia
    k.cykl("UpperTorso", "obrot", (3, 0, 0), czestosc=4, faza=0.25)
    k.cykl("Head", "obrot", (-6, 0, 0), czestosc=4, faza=0.1)
    k.cykl("LeftLowerArm", "obrot", (-6, 0, 0), czestosc=4, faza=0.3)
    k.cykl("Head", "obrot", (0, 0, 4), czestosc=1)
    k.cykl("RightUpperArm", "obrot", (-6, 0, 0), czestosc=4, faza=0.2)

    p.ustaw_poze_renderu("zaproszenie", 30)
    return [p, ch]


SLABOSCI = [
    "Chochla jest osobnym przedmiotem (przedmioty/karczmarz_chochla.fbx); w FBX postaci jej nie ma.",
    "Brzuch, kamizelka i ręce to sztywne bryły na kościach: w geście zaproszenia ramię lekko wchodzi w bufkę "
    "rękawa, a w śmiechu przedramię dotyka brzucha.",
    "Lewa dłoń jest otwarta (płaska) także w pozie ręki na biodrze; prawa to pięść z chochlą.",
    "Klipy to szkice (1–2 s), nie gotowa animacja.",
]
