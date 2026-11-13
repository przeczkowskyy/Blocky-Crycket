# -*- coding: utf-8 -*-
"""KOT-MAG „Crycket” — drugi bohater-maskotka: mały kanciasty pomarańczowy kot w za dużej fioletowej szacie,
z kosturem zakończonym fioletowym kryształem i spiczastym kapeluszem (kapelusz i kryształ to w kanonie wciąż
propozycja — dlatego kapelusz jest OSOBNYM akcesorium i można go zdjąć).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/kot_mag.py --wyj <folder> --klip idle

Status: propozycja (kanon wyglądu: B&C/Postacie/Kot-Mag.md, obraz referencyjny assets/processed/KeyArt.png).

Budowa:
- szkielet R15 z przerysowanymi proporcjami (duża głowa, krótkie łapy): ok. 3,15 studa do czubka głowy,
  ok. 3,45 z uszami, bez kapelusza;
- DWIE kości spoza standardu R15: `Tail` (dziecko LowerTorso) i `TailTip` (dziecko Tail) — ogon musi się kołysać, a sztywne bryły
  ruszają się tylko z kością. W Roblox to już nie „czysty” R15 (16./17. część Tail/TailTip) — do NPC i własnej
  postaci w grze wystarczy; klipy kości standardowych działają tak samo;
- dół szaty to jeden ośmiokątny dzwon na LowerTorso do samej ziemi (za duża szata) z trenem leżącym z tyłu;
  nogi chodzą w środku (wymach uda ≤ 15°), spod rąbka wystają łapy;
- akcesoria: `kot_mag_kapelusz` (Hat) i `kot_mag_kostur` (Bron, RightGripAttachment, konwencja broni: uchwyt
  w (0,0,0), drzewce w +Y). Na kocie kostur jest założony z korektą obrot=(−90, 0, 0), żeby przy zwisającej łapie
  stał pionowo (jak na obrazie referencyjnym); w pozie bazowej łapa jest odsunięta na zewnątrz, a nadgarstek
  odchyla kostur od głowy (inaczej kryształ chowa się w szerokiej głowie i rondzie kapelusza);
- klipy bez kanału skali (Roblox przenosi tylko pozycję i obrót kości): „pulsowanie” kryształu w klipie czar to
  potrząśnięcie kosturem; prawdziwe świecenie / błyski w grze dorobić skryptem (PointLight, ParticleEmitter);
- to rig NPC / postaci w grze, NIE ciało awatara na Marketplace (ogon spoza R15, 3,7 studa wzrostu).
"""
from swiat.postacie.biblioteka.postac import Akcesorium, Postac

ID = "kot_mag"

SLABOSCI = [
    "Rig NPC, nie ciało awatara: kości Tail i TailTip spoza R15, wzrost ok. 3,7 studa z kapeluszem.",
    "Kapelusz i kostur są osobnymi przedmiotami (przedmioty/kot_mag_*.fbx); w FBX kota ich nie ma.",
    "Dzwon szaty jest sztywny (idzie za biodrami): w chodzie nogi są schowane, ruch widać po łapach i kołysaniu.",
    "Tren leży na ziemi tylko w spoczynku; przy podskoku w wiwacie unosi się razem z biodrami.",
    "Czar i zianie nie mają efektów cząsteczkowych; kryształ świeci tylko w renderze.",
]

PALETA = {
    "kot": "F28A2E", "kot_jasny": "FFD9A6", "kot_ciemny": "C8601C",
    "szata": "7B45CC", "szata_ciemna": "4F2A93", "szata_jasna": "9F72E6",
    "wstazka": "F7C531", "nos": "F5879F", "krysztal": "9B4DFF", "krysztal_jasny": "C49BFF",
    "drewno": "7A4A26", "drewno_ciemne": "4E2D15",
}


# --------------------------------------------------------------------------- akcesoria
def kapelusz():
    """Spiczasty fioletowy kapelusz z żółtą wstążką; (0,0,0) = HatAttachment (środek góry głowy)."""
    a = Akcesorium("kot_mag_kapelusz", "Kapelusz Kota-Maga", zaczep="HatAttachment", typ="Hat",
                   paleta=PALETA, ikona_obrot=(0, 20, 0))
    a.walec("Rondo", (0, 0.06, 0), (2.25, 0.12, 2.05), "szata", "matowy", segm=8)
    a.walec("Rondo spod", (0, 0.0, 0), (2.05, 0.03, 1.85), "szata_ciemna", "matowy", segm=8, faza=0.0)
    a.ostroslup("Glowa kapelusza", (0, 0.58, 0), (1.25, 0.95, 1.15), "szata", "matowy", gora=(0.78, 0.72))
    a.blok("Wstazka", (0, 0.26, 0), (1.31, 0.24, 1.21), "wstazka", "matowy", faza=0.03)
    a.blok("Klamra", (0, 0.26, 0.6), (0.34, 0.3, 0.08), "zloto", "metal", faza=0.03)
    a.blok("Klamra srodek", (0, 0.26, 0.64), (0.14, 0.12, 0.04), "szata_ciemna", faza=0.0)
    # górna część przełamana do tyłu — krzywy, komiksowy szpic
    with a.uklad(pos=(0, 1.04, -0.02), obrot=(-22, 0, 6)):
        a.ostroslup("Szpic", (0, 0.42, 0), (0.8, 0.84, 0.75), "szata", "matowy", gora=(0.0, 0.0),
                    przes_gory=(0.0, -0.12))
    a.blok("Gwiazdka", (0.38, 0.62, 0.44), (0.16, 0.16, 0.06), "wstazka", "swiecacy", rot=(10, 0, 45), faza=0.0)
    return a


def kostur():
    """Drewniany kostur z fioletowym kryształem; uchwyt w (0,0,0), drzewce w +Y (konwencja broni)."""
    a = Akcesorium("kot_mag_kostur", "Kostur Kota-Maga", zaczep="RightGripAttachment", typ="Bron",
                   paleta=PALETA, ikona_obrot=(0, 0, -35))
    a.walec("Drzewce", (0, 0.42, 0), (0.17, 2.55, 0.17), "drewno", "matowy", segm=8)
    a.blok("Okucie", (0, -0.83, 0), (0.22, 0.12, 0.22), "zloto", "metal", faza=0.03)
    a.blok("Owijka", (0, 0.0, 0), (0.23, 0.42, 0.23), "szata_ciemna", "matowy", faza=0.04)
    for i, y in enumerate((0.5, 0.85, 1.2)):
        a.blok("Spirala %d" % i, (0, y, 0), (0.24, 0.06, 0.24), "szata_jasna", "matowy", rot=(0, 30 * i, 18),
               faza=0.0)
    a.blok("Pierscien", (0, 1.62, 0), (0.3, 0.1, 0.3), "zloto", "metal", faza=0.03)
    a.blok("Oprawa", (0, 1.73, 0), (0.36, 0.12, 0.36), "zloto", "metal", rot=(0, 45, 0), faza=0.03)
    for i in range(4):
        with a.uklad(pos=(0, 1.78, 0), obrot=(0, 45 + 90 * i, 0)):
            a.blok("Pazur %d" % i, (0, 0.17, 0.17), (0.07, 0.34, 0.07), "zloto", "metal", rot=(28, 0, 0), faza=0.0)
    # kryształ: dwa ostrosłupy (dolny odwrócony), obrócone o 45° — romb
    with a.uklad(pos=(0, 2.02, 0), obrot=(0, 45, 0)):
        a.ostroslup("Krysztal gora", (0, 0.27, 0), (0.42, 0.54, 0.42), "krysztal", "polysk", gora=(0, 0))
        a.ostroslup("Krysztal dol", (0, -0.12, 0), (0.42, 0.24, 0.42), "krysztal", "polysk", rot=(180, 0, 0),
                    gora=(0, 0))
        a.blok("Blysk", (0.0, 0.14, 0.215), (0.1, 0.2, 0.03), "krysztal_jasny", "swiecacy", faza=0.0)   # kryształ: fiolet z połyskiem, świeci tylko blask
    for zn in (1, -1):
        a.blok("Odlamek", (zn * 0.36, 2.2 + zn * 0.06, 0), (0.1, 0.16, 0.1), "krysztal", "swiecacy",
               rot=(0, 45, zn * 20), faza=0.0)
    return a


# --------------------------------------------------------------------------- postać
def zbuduj():
    p = Postac(ID, "Kot-Mag Crycket", typ="r15", skala=1.0, faza=0.05, paleta=PALETA, rozstaw_nog=0.3,
               wymiary={"Head": (1.65, 1.3, 1.4),
                        "UpperTorso": (1.3, 0.85, 0.95), "LowerTorso": (1.3, 0.25, 0.95),
                        "UpperArm": (0.42, 0.42, 0.42), "LowerArm": (0.42, 0.36, 0.42), "Hand": (0.4, 0.22, 0.4),
                        "UpperLeg": (0.5, 0.3, 0.5), "LowerLeg": (0.45, 0.27, 0.45), "Foot": (0.5, 0.18, 0.62)})

    # ---------------- głowa (układ: środek klocka głowy)
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        z = d / 2
        p.blok("Glowa", (0, 0, 0), (w, h, d), "kot")
        # policzki-kępki: schodki po bokach — kocia sylwetka głowy
        for zn in (1, -1):
            p.blok("Kepka", (zn * (w / 2 + 0.07), -0.3, 0.0), (0.16, 0.42, 0.95), "kot")
            p.blok("Kepka mala", (zn * (w / 2 + 0.17), -0.38, 0.05), (0.1, 0.22, 0.6), "kot", faza=0.02)
        # uszy (trójkątne, odchylone na zewnątrz)
        # uszy wyżej (+0,15) i odchylone na zewnątrz — przebijają rondo kapelusza z obu stron
        for zn, s in ((1, "L"), (-1, "P")):
            with p.uklad(pos=(zn * 0.6, h / 2 + 0.09, -0.05), obrot=(0, 0, -zn * 28)):
                p.ostroslup("Ucho " + s, (0, 0.36, 0), (0.56, 0.72, 0.32), "kot", gora=(0.0, 0.12),
                            przes_gory=(zn * 0.05, 0))
                p.ostroslup("Ucho srodek " + s, (0, 0.3, 0.17), (0.32, 0.5, 0.04), "nos", "matowy",
                            gora=(0.0, 0.03), przes_gory=(zn * 0.03, 0), faza=0.0)
        # paski na czole i z tyłu
        for i, x in enumerate((-0.22, 0.0, 0.22)):
            p.blok("Pasek czolo %d" % i, (x, h / 2 - 0.13 - (0.03 if x == 0 else 0), z + 0.015),
                   (0.1, 0.24 + (0.06 if x == 0 else 0), 0.05), "kot_ciemny", "matowy", faza=0.0)
        for i, y in enumerate((0.25, -0.05)):
            p.blok("Pasek tyl %d" % i, (0, y, -z - 0.015), (1.1 - 0.25 * i, 0.12, 0.05), "kot_ciemny", "matowy",
                   faza=0.0)
        # oczy: duże, czarne, z dwoma błyskami
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * 0.38
            p.blok("Oko " + s, (x, 0.12, z + 0.02), (0.32, 0.46, 0.06), "tusz", "polysk", faza=0.03)
            p.blok("Blysk " + s, (x - 0.05, 0.23, z + 0.055), (0.11, 0.13, 0.03), "bialy", faza=0.0)
            p.blok("Blysk maly " + s, (x + 0.07, 0.0, z + 0.055), (0.05, 0.06, 0.03), "bialy", faza=0.0)
            p.blok("Rumieniec " + s, (zn * 0.62, -0.17, z + 0.012), (0.22, 0.1, 0.03), "rumieniec", "matowy",
                   faza=0.0)
            # wąsy: dwa z każdej strony, wystają poza obrys głowy
            for i, (dy, kat) in enumerate(((-0.2, 8), (-0.32, -6))):
                p.blok("Was %s%d" % (s, i), (zn * 0.78, dy, z + 0.03), (0.6, 0.04, 0.04), "tusz", "matowy",
                       rot=(0, 0, zn * kat), faza=0.0)
        # pyszczek: jasna mordka, różowy nos, uśmiech „w”
        p.blok("Mordka", (0, -0.36, z + 0.025), (0.8, 0.44, 0.08), "kot_jasny", "matowy", faza=0.03)
        p.blok("Broda", (0, -0.58, z - 0.12), (0.52, 0.12, 0.3), "kot_jasny", "matowy", faza=0.02)
        p.blok("Nos", (0, -0.2, z + 0.09), (0.24, 0.13, 0.07), "nos", "polysk", faza=0.03)
        p.blok("Nos dol", (0, -0.27, z + 0.085), (0.1, 0.05, 0.06), "nos", "polysk", faza=0.0)
        # kocie usta „ω”: same kreski tuszu (bez czarnego wypełnienia) — dwie małe litery v obok siebie
        for zn in (1, -1):
            p.blok("Usta a", (zn * 0.06, -0.37, z + 0.075), (0.12, 0.035, 0.04), "tusz", rot=(0, 0, -zn * 30),
                   faza=0.0)
            p.blok("Usta b", (zn * 0.165, -0.37, z + 0.075), (0.12, 0.035, 0.04), "tusz", rot=(0, 0, zn * 30),
                   faza=0.0)

    # ---------------- tułów: szata, kołnierz w szpic, zapinka z klejnotem, kaptur na plecach
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2 + 0.05
        p.blok("Szata gora", (0, 0, 0), (w + 0.1, h + 0.02, d + 0.1), "szata", "matowy")
        p.blok("Piers", (0, h / 2 - 0.2, z + 0.012), (0.36, 0.36, 0.04), "kot_jasny", "matowy", faza=0.0)
        for zn in (1, -1):
            p.blok("Kolnierz", (zn * 0.17, h / 2 - 0.2, z + 0.03), (0.15, 0.52, 0.06), "szata_ciemna", "matowy",
                   rot=(0, 0, zn * 28), faza=0.02)
        p.blok("Listwa", (0, -0.12, z + 0.02), (0.16, 0.6, 0.05), "szata_ciemna", "matowy", faza=0.0)
        p.blok("Zapinka", (0, 0.04, z + 0.05), (0.26, 0.26, 0.06), "zloto", "metal", rot=(0, 0, 45), faza=0.03)
        p.blok("Klejnot", (0, 0.04, z + 0.09), (0.13, 0.13, 0.04), "krysztal", "swiecacy", rot=(0, 0, 45), faza=0.0)
        p.blok("Ramiona", (0, h / 2 - 0.03, 0), (w + 0.26, 0.16, d + 0.22), "szata_ciemna", "matowy")
        p.blok("Kaptur", (0, h / 2 - 0.12, -d / 2 - 0.12), (1.0, 0.5, 0.26), "szata_ciemna", "matowy")
        p.klin("Kaptur szpic", (0, h / 2 - 0.5, -d / 2 - 0.14), (0.5, 0.3, 0.2), "szata_ciemna", "matowy",
               rot=(180, 180, 0))

    # ---------------- pas + rdzeń dzwonu szaty (sztywno na LowerTorso)
    with p.na("LowerTorso"):                                   # (0,0,0) = staw bioder (y = 0,75 w modelu)
        p.blok("Pas", (0, 0.13, 0), (1.44, 0.2, 1.1), "szata_ciemna", "matowy")
        p.blok("Pas klamra", (0, 0.13, 0.57), (0.26, 0.22, 0.06), "wstazka", "metal", faza=0.02)
        # za duża szata: jeden ośmiokątny dzwon od pasa (y ≈ 1,0) do ziemi (y ≈ 0,1), szerszy u dołu o 0,25 z każdej
        # strony; nogi chodzą w środku, spod rąbka wystają tylko łapy. Z tyłu tren leżący na ziemi.
        p.stozek("Szata dzwon", (0, -0.2, -0.04), (2.1, 0.9, 1.75), "szata", "matowy", gora=0.72, segm=8)
        p.stozek("Szata rabek", (0, -0.61, -0.04), (2.16, 0.1, 1.8), "szata_ciemna", "matowy", gora=0.97, segm=8,
                 faza=0.0)
        p.stozek("Szata lamowka", (0, -0.53, -0.04), (2.07, 0.05, 1.73), "wstazka", "matowy", gora=0.99, segm=8,
                 faza=0.0)
        p.blok("Szata pola", (0, -0.2, 0.62), (0.16, 0.8, 0.06), "szata_ciemna", "matowy", rot=(-14, 0, 0), faza=0.0)
        # tren: klin 1,6 × 0,15 × 0,7 leży na ziemi za piętami (wysoka ściana przy szacie, skos ku tyłowi)
        p.klin("Tren", (0, -0.665, -1.12), (1.6, 0.15, 0.7), "szata", "matowy", faza=0.03)

    # ---------------- nogi: w środku dzwonu; łapki z jasnymi palcami wystają spod rąbka
    for s, zn in (("Left", 1), ("Right", -1)):
        with p.na(s + "UpperLeg"):                             # staw biodra (x = ±0,3, y = 0,75)
            p.blok("Udo", (0, -0.15, 0), (0.42, 0.3, 0.42), "kot", faza=0.03)
        with p.na(s + "LowerLeg", od="srodek"):
            p.blok("Lydka", (0, 0, 0), (0.4, 0.3, 0.4), "kot", faza=0.03)
        with p.na(s + "Foot", od="srodek"):
            w, h, d = p.wymiary(s + "Foot")
            p.blok("Lapa", (0, 0, 0), (w, h, d), "kot")
            # łapa wysunięta do przodu — wystaje spod rąbka szaty
            p.blok("Lapa przod", (0, -0.01, d / 2 + 0.2), (w, h - 0.02, 0.42), "kot", faza=0.04)
            p.blok("Palce", (0, -0.01, d / 2 + 0.33), (w + 0.04, h - 0.02, 0.2), "kot_jasny", "matowy", faza=0.03)
            for i, x in enumerate((-0.12, 0.12)):
                p.blok("Szpara %d" % i, (x, 0.02, d / 2 + 0.442), (0.03, 0.1, 0.04), "kot_ciemny", faza=0.0)

    # ---------------- ręce: za długie rękawy z szerokim mankietem, łapka ledwo wystaje
    for s, zn in (("Left", 1), ("Right", -1)):
        with p.na(s + "UpperArm", od="srodek"):
            p.blok("Rekaw", (0, 0, 0), (0.5, 0.48, 0.5), "szata", "matowy")
        with p.na(s + "LowerArm"):                             # staw łokcia
            p.ostroslup("Mankiet", (0, -0.24, 0), (0.76, 0.48, 0.76), "szata", "matowy", rot=(180, 0, 0),
                        gora=(0.5, 0.5))
            p.blok("Obszycie rekawa", (0, -0.43, 0), (0.79, 0.1, 0.79), "szata_ciemna", "matowy", faza=0.03)
            p.blok("Wnetrze rekawa", (0, -0.485, 0), (0.62, 0.02, 0.62), "tusz", "matowy", faza=0.0)
        with p.na(s + "Hand"):                                 # staw nadgarstka
            p.blok("Lapka", (0, -0.19, 0), (0.38, 0.32, 0.38), "kot", faza=0.05)
            p.blok("Lapka palce", (0, -0.31, 0.13), (0.3, 0.08, 0.14), "kot_jasny", "matowy", faza=0.02)

    # ---------------- ogon: dwie dodatkowe kości (kołysanie)
    # nasada idzie spod szaty do tyłu i w lewo (+X), końcówka wznosi się obok szaty — widać ją też z przodu
    p.kosc("Tail", "LowerTorso", staw=(0.1, 0.3, -0.5), czesc=(0.28, 0.28, 0.86), srodek=(0.33, -0.06, -0.28))
    p.kosc("TailTip", "Tail", staw=(0.75, 0.24, -1.05), czesc=(0.28, 1.15, 0.28), srodek=(0, 0.52, 0))
    with p.na("Tail", obrot=(0, -50, 0)):
        p.blok("Ogon nasada", (0, -0.06, -0.47), (0.28, 0.28, 1.0), "kot", faza=0.04)     # zachodzi na końcówkę
        p.blok("Ogon pasek", (0, -0.06, -0.62), (0.32, 0.32, 0.08), "kot_ciemny", "matowy", faza=0.02)
    with p.na("TailTip", obrot=(0, -50, -10)):
        p.blok("Ogon srodek", (0, 0.45, 0), (0.28, 1.24, 0.28), "kot", faza=0.04)
        p.blok("Ogon zawijas", (0, 1.12, 0.12), (0.28, 0.26, 0.52), "kot", faza=0.04)
        p.blok("Ogon koncowka", (0, 1.05, 0.4), (0.28, 0.22, 0.14), "kot_jasny", "matowy", faza=0.03)
        for k, y in enumerate((0.2, 0.5, 0.8)):
            p.blok("Ogon pasek %d" % k, (0, y, 0), (0.32, 0.08, 0.32), "kot_ciemny", "matowy", faza=0.02)

    # ---------------- akcesoria
    # kapelusz i kostur: osobne przedmioty (przedmioty/kot_mag_*.fbx); w FBX kota ich nie ma, w renderach są
    kap, kos = kapelusz(), kostur()
    p.zaloz(kap, pos=(0, 0.02, 0), eksport=False)
    p.zaloz(kos, zaczep="RightGripAttachment", pos=(-0.08, 0, 0), obrot=(-90, 0, 0), eksport=False)

    klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return [p, kap, kos]


# --------------------------------------------------------------------------- klipy
# poza bazowa: prawa łapa trzyma kostur lekko z przodu i na zewnątrz (kostur nie wchodzi w szatę)
BAZA = {"RightUpperArm": (-14, 0, -36), "RightLowerArm": (-8, 0, 0), "RightHand": (22, 0, 44),
        "LeftUpperArm": (4, 0, 9), "LeftLowerArm": (-10, 0, 0),
        "Tail": (20, 0, 0), "TailTip": (15, 0, 0)}           # ogon uniesiony od ziemi, końcówka zawinięta ku plecom


def klipy(p):
    # --- idle: oddech, przechył głowy, ogon kołysze się na boki (końcówka z opóźnieniem)
    k = p.klip("idle", 60, petla=True)
    k.poza(0, BAZA)
    k.cykl("Tail", "obrot", (0, 12, 3))
    k.cykl("TailTip", "obrot", (0, 12, 8), faza=0.3)
    k.cykl("UpperTorso", "obrot", (2.5, 0, 0), faza=0.25)
    k.cykl("Head", "obrot", (2, 0, 5), faza=0.1)
    k.cykl("LeftUpperArm", "obrot", (0, 0, 3), faza=0.25)
    k.cykl("RightUpperArm", "obrot", (-2, 0, 0), faza=0.25)

    # --- chod: drobne, szybkie kroki; płaty szaty na udach falują; ogon i głowa w rytmie
    k = p.klip("chod", 20, petla=True)
    k.poza(0, BAZA)
    k.cykl("LeftUpperLeg", "obrot", (14, 0, 0))                # ≤ 15°: nogi zostają w dzwonie szaty
    k.cykl("RightUpperLeg", "obrot", (14, 0, 0), faza=0.5)
    k.cykl("LeftLowerLeg", "obrot", (12, 0, 0), faza=0.25, srodek=(12, 0, 0))
    k.cykl("RightLowerLeg", "obrot", (12, 0, 0), faza=0.75, srodek=(12, 0, 0))
    k.cykl("LeftFoot", "obrot", (-10, 0, 0), faza=0.1)
    k.cykl("RightFoot", "obrot", (-10, 0, 0), faza=0.6)
    k.cykl("LowerTorso", "przes", (0, 0.06, 0), faza=0.0, czestosc=2, srodek=(0, 0.03, 0))
    k.cykl("LowerTorso", "obrot", (0, 7, 3))
    k.cykl("UpperTorso", "obrot", (0, -9, -2))
    k.cykl("UpperTorso", "obrot", (4, 0, 0), czestosc=2, faza=0.1, srodek=(5, 0, 0))   # lekki skłon w marszu
    k.cykl("LeftUpperArm", "obrot", (-24, 0, 0))
    k.cykl("RightUpperArm", "obrot", (-7, 0, 0), faza=0.5)
    k.cykl("Head", "obrot", (3, 0, 0), czestosc=2, faza=0.35)
    k.cykl("Head", "obrot", (0, 4, 3), faza=0.5)
    k.cykl("Tail", "obrot", (0, 16, 4), faza=0.2)
    k.cykl("TailTip", "obrot", (0, 22, 10), faza=0.05)

    # --- czar: przygarbienie, kostur w górę nad głowę, kryształ pulsuje trzy razy, powrót
    k = p.klip("czar", 54, petla=False)
    baza = dict(BAZA)
    k.poza(0, dict(baza, **{"Head": (0, 0, 0), "UpperTorso": (0, 0, 0), "Tail": (0, 0, 0),
                            "LowerTorso": {"obrot": (0, 0, 0), "przes": (0, 0, 0)}}))
    k.poza(9, {"RightUpperArm": (6, 0, -22), "RightLowerArm": (-30, 0, 0), "RightHand": (30, 0, 0),
               "LeftUpperArm": (-30, 0, 20), "LeftLowerArm": (-40, 0, 0),
               "UpperTorso": (10, -12, 0), "Head": (8, 0, 0), "Tail": (-10, 0, 0),
               "LowerTorso": {"obrot": (0, 0, 0), "przes": (0, -0.06, 0)}})
    # łapa w górę i na zewnątrz; nadgarstek obrócony tak, by kostur sterczał w górę i lekko do przodu
    uniesienie = {"RightUpperArm": (-150, 0, -62), "RightLowerArm": (-12, 0, 0), "RightHand": (180, 0, -32),
                  "LeftUpperArm": (-30, 0, 125), "LeftLowerArm": (-25, 0, 0),
                  "UpperTorso": (-8, 10, 0), "Head": (-14, 0, 0), "Tail": (32, 0, 0), "TailTip": (20, 0, 0),
                  "LowerTorso": {"obrot": (0, 0, 0), "przes": (0, 0.1, 0)}}
    k.poza(17, uniesienie)
    k.poza(40, uniesienie)
    # pulsowanie kryształu bez kanału skali (Roblox go nie przenosi): krótkie potrząśnięcia kosturem
    for f, rx in ((21, 192), (25, 180), (29, 192), (33, 180), (37, 194)):
        k.klucz(f, "RightHand", obrot=(rx, 0, -32))
    k.poza(54, dict(baza, **{"Head": (0, 0, 0), "UpperTorso": (0, 0, 0), "Tail": (0, 0, 0), "TailTip": (0, 0, 0),
                             "LowerTorso": {"obrot": (0, 0, 0), "przes": (0, 0, 0)}}))
    k.klucz(0, "TailTip", obrot=(0, 0, 0))

    # --- wiwat: przysiad, podskok z łapkami w górze, lądowanie (pętla skoków)
    k = p.klip("wiwat", 30, petla=True)
    przysiad = {"LowerTorso": {"przes": (0, -0.08, 0)},
                "LeftUpperLeg": (-16, 0, 0), "RightUpperLeg": (-16, 0, 0),
                "LeftLowerLeg": (32, 0, 0), "RightLowerLeg": (32, 0, 0),
                "LeftFoot": (-16, 0, 0), "RightFoot": (-16, 0, 0),
                "UpperTorso": (8, 0, 0), "Head": (5, 0, 0),
                "LeftUpperArm": (-10, 0, 20), "LeftLowerArm": (-20, 0, 0),
                "RightUpperArm": (-10, 0, -20), "RightLowerArm": (-20, 0, 0), "RightHand": (30, 0, 0),
                "Tail": (5, 0, 0), "TailTip": (0, 0, 0)}
    lot = {"LowerTorso": {"przes": (0, 0.8, 0)},
           "LeftUpperLeg": (-12, 0, 6), "RightUpperLeg": (-12, 0, -6),
           "LeftLowerLeg": (34, 0, 0), "RightLowerLeg": (34, 0, 0),
           "LeftFoot": (16, 0, 0), "RightFoot": (16, 0, 0),
           "UpperTorso": (-8, 0, 0), "Head": (-12, 0, 0),
           "LeftUpperArm": (-15, 0, 160), "LeftLowerArm": (0, 0, 0),
           "RightUpperArm": (-120, 0, -55), "RightLowerArm": (-10, 0, 0), "RightHand": (115, 0, -20),
           "Tail": (40, 0, 0), "TailTip": (25, 0, 0)}
    k.poza(0, przysiad)
    k.poza(10, lot)
    k.poza(14, lot)
    k.poza(22, {"LowerTorso": {"przes": (0, 0.0, 0)}, "LeftUpperLeg": (-6, 0, 0), "RightUpperLeg": (-6, 0, 0),
                "LeftLowerLeg": (10, 0, 0), "RightLowerLeg": (10, 0, 0), "LeftFoot": (-4, 0, 0),
                "RightFoot": (-4, 0, 0)})
    k.cykl("TailTip", "obrot", (0, 30, 0), czestosc=2)
    k.cykl("Head", "obrot", (0, 0, 6), czestosc=1, faza=0.25)
