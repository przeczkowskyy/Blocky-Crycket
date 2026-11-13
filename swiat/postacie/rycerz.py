# -*- coding: utf-8 -*-
"""RYCERZ „Blocky” — jeden z dwóch bohaterów-maskotek (kanon: B&C/Postacie/Rycerz.md, obraz KeyArt.png).

Kanciasty ludzik R15 w stalowej zbroi płytowej (naramienniki, napierśnik z obojczykiem, nałokcice, nakolanniki,
nagolenniki), stalowy hełm z otwartą twarzą (zadziorny uśmiech, grube brwi), niebieski tabard ze złotą lamówką,
brązowy pas ze stalową klamrą i wielki miecz w prawej dłoni (akcesorium na RightGripAttachment).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/rycerz.py --wyj <folder> --klip idle

Klipy: idle (oddech, lekkie kołysanie, miecz w gotowości), chod, atak_miecz (zamach znad głowy), wiwat (miecz w górę).
Proporcje przerysowane: duża głowa w hełmie (ok. 1/3 wzrostu), szeroka klatka, krótkie masywne nogi.
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
from swiat.postacie.biblioteka.postac import Postac, Akcesorium

ID = "rycerz"
# stal zbroi trochę ciemniejsza i chłodniejsza niż w palecie biblioteki (jak na obrazie referencyjnym)
PALETA = {"stal": "A8B4C8", "stal_cien": "75839C", "stal_ciemna": "4D576D", "niebieski": "2C6BE0"}


# --------------------------------------------------------------------------- miecz (akcesorium na prawej dłoni)
def miecz():
    """Wielki miecz: rękojeść w (0, 0, 0), ostrze w +Y, płaz do przodu (+Z)."""
    a = Akcesorium("rycerz_miecz", "Wielki miecz Rycerza", zaczep="RightGripAttachment", typ="Bron", paleta=PALETA,
                   ikona_obrot=(0, 0, -45))
    a.blok("Rekojesc", (0, 0, 0), (0.24, 1.05, 0.24), "brazowy_ciemny", "matowy", faza=0.04)
    for y in (-0.3, 0.0, 0.3):
        a.blok("Owijka", (0, y, 0), (0.28, 0.07, 0.28), "brazowy", "matowy", faza=0.0)
    a.blok("Glowica", (0, -0.66, 0), (0.42, 0.3, 0.42), "zloto", "metal", faza=0.08)
    a.blok("Glowica kamien", (0, -0.66, 0.23), (0.16, 0.14, 0.06), "niebieski_jasny", "swiecacy", faza=0.02)
    # jelec: końce zadarte ku ostrzu; rozpiętość 1,4 (szerszy przechodził przez przedramię w wiwacie i ataku)
    a.blok("Jelec", (0, 0.64, 0), (1.1, 0.24, 0.36), "stal_ciemna", "metal", faza=0.06)
    for zn in (1, -1):
        a.blok("Jelec koniec", (zn * 0.58, 0.74, 0), (0.24, 0.44, 0.4), "zloto", "metal", faza=0.06)
    a.blok("Jelec srodek", (0, 0.66, 0), (0.46, 0.4, 0.44), "zloto", "metal", faza=0.08)
    a.blok("Klejnot", (0, 0.66, 0.235), (0.2, 0.2, 0.06), "niebieski", "swiecacy", faza=0.02)
    a.blok("Klejnot tyl", (0, 0.66, -0.235), (0.2, 0.2, 0.06), "niebieski", "swiecacy", faza=0.02)
    # klinga: szeroka, z ciemniejszym zbroczem po obu stronach płazu
    a.blok("Klinga", (0, 2.21, 0), (0.62, 2.7, 0.16), "stal", "metal", faza=0.04)
    a.blok("Zbrocze", (0, 2.0, 0), (0.14, 2.2, 0.2), "stal_cien", "metal", faza=0.0)
    a.ostroslup("Sztych", (0, 3.86, 0), (0.62, 0.6, 0.16), "stal", "metal", gora=(0.0, 0.16))
    return a


# --------------------------------------------------------------------------- rycerz
def zbuduj():
    p = Postac(ID, "Rycerz Blocky", typ="r15", faza=0.05, paleta=PALETA,
               wymiary={"Head": (1.6, 1.5, 1.45),
                        "UpperTorso": (2.2, 1.5, 1.2), "LowerTorso": (2.2, 0.4, 1.2),
                        "UpperArm": (0.95, 0.95, 0.95), "LowerArm": (0.95, 0.75, 0.95), "Hand": (0.9, 0.35, 0.9),
                        "UpperLeg": (1.05, 0.8, 1.05), "LowerLeg": (1.05, 0.75, 1.05), "Foot": (1.05, 0.35, 1.35)})
    p.cialo({"glowa": "skora", "tulow": "stal", "pas": "brazowy", "ramiona": "stal",
             "LeftUpperArm": "stal_ciemna", "RightUpperArm": "stal_ciemna",
             "dlonie": "stal_ciemna", "nogi": "stal", "stopy": "stal_ciemna"})

    # --- głowa: twarz + hełm z otwartą twarzą
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        z = d / 2                                                   # przednia ściana głowy (skóra)
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * 0.27
            p.blok("Oko " + s, (x, 0.1, z + 0.02), (0.2, 0.3, 0.08), "tusz", "polysk", faza=0.03)
            p.blok("Blysk " + s, (x - 0.04, 0.18, z + 0.07), (0.08, 0.09, 0.04), "bialy", faza=0.0)
            # grube brwi, lekko skośne (7°) — pewna siebie, nie zła mina
            p.blok("Brew " + s, (zn * 0.28, 0.33, z + 0.03), (0.38, 0.13, 0.1), "brazowy_ciemny", "matowy",
                   rot=(0, 0, zn * 7), faza=0.02)
            p.blok("Rumieniec " + s, (zn * 0.5, -0.17, z + 0.01), (0.14, 0.08, 0.04), "rumieniec", "matowy", faza=0.0)
        p.blok("Nos", (0, -0.04, z + 0.05), (0.2, 0.2, 0.12), "skora_cien", "matowy", faza=0.03)
        # szeroki, pewny siebie uśmiech: ciemne usta 0,9 × 0,22 z białym pasem zębów, oba kąciki uniesione
        p.blok("Usta", (0.0, -0.38, z + 0.02), (0.9, 0.22, 0.06), "tusz", faza=0.02)
        p.blok("Zeby", (0.0, -0.33, z + 0.05), (0.78, 0.1, 0.04), "bialy", faza=0.0)
        p.blok("Jezyk", (0.0, -0.45, z + 0.04), (0.36, 0.07, 0.04), "D9534A", "matowy", faza=0.0)
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Kacik " + s, (zn * 0.47, -0.3, z + 0.02), (0.12, 0.2, 0.06), "tusz", faza=0.0,
                   rot=(0, 0, zn * 35))
        p.blok("Podbrodek", (0.0, -0.58, z + 0.02), (0.3, 0.06, 0.04), "skora_cien", "matowy", faza=0.0)

        # hełm: kubeł z zaokrągloną kopułą, szeroki otwór na twarz, obręcz dookoła
        hw, hd, hh = w + 0.32, d + 0.32, h + 0.1
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Helm bok " + s, (zn * (w / 2 + 0.08), -0.0, 0), (0.16, hh, hd), "stal", "metal")
            p.blok("Policzek " + s, (zn * 0.72, -0.07, z + 0.08), (0.24, 0.86, 0.16), "stal", "metal")
            p.blok("Nit " + s, (zn * 0.72, 0.22, z + 0.18), (0.09, 0.09, 0.05), "stal_ciemna", "metal", faza=0.0)
            p.blok("Obrecz bok " + s, (zn * (w / 2 + 0.18), h / 2 - 0.12, 0), (0.06, 0.18, hd + 0.04),
                   "stal_cien", "metal", faza=0.0)
            for zz in (-0.45, 0.0):
                p.blok("Nit bok " + s, (zn * (w / 2 + 0.18), -0.25, zz), (0.05, 0.1, 0.1), "stal_ciemna", "metal",
                       faza=0.0)
        p.blok("Helm tyl", (0, 0, -z - 0.08), (hw, hh, 0.16), "stal", "metal")
        p.blok("Obrecz tyl", (0, h / 2 - 0.12, -z - 0.18), (hw + 0.04, 0.18, 0.06), "stal_cien", "metal", faza=0.0)
        p.blok("Helm tyl listwa", (0, -0.12, -z - 0.18), (0.22, h - 0.5, 0.06), "stal_cien", "metal", faza=0.0)
        p.blok("Helm kopula", (0, h / 2 + 0.1, 0), (hw, 0.3, hd), "stal", "metal", faza=0.12)
        p.blok("Helm czubek", (0, h / 2 + 0.28, 0), (w - 0.2, 0.14, d - 0.2), "stal", "metal", faza=0.06)
        p.blok("Grzebien", (0, h / 2 + 0.34, -0.02), (0.22, 0.14, d + 0.08), "stal_cien", "metal", faza=0.05)
        p.blok("Czolo", (0, h / 2 - 0.1, z + 0.08), (hw, 0.24, 0.16), "stal", "metal")
        p.blok("Czolo obrecz", (0, h / 2 - 0.12, z + 0.18), (hw + 0.04, 0.18, 0.06), "stal_cien", "metal",
               faza=0.0)

    # --- tułów: obojczyk (gorget), tabard ze złotą lamówką
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.blok("Obojczyk", (0, h / 2 - 0.06, 0), (1.5, 0.28, d + 0.12), "stal_cien", "metal")
        p.blok("Tabard", (0, -0.08, z + 0.03), (1.3, h - 0.16, 0.06), "niebieski", "matowy", faza=0.0)
        p.blok("Tabard tyl", (0, -0.08, -z - 0.03), (1.3, h - 0.16, 0.06), "niebieski", "matowy", faza=0.0)
        for zn in (1, -1):
            p.blok("Lamowka", (zn * 0.68, -0.08, z + 0.045), (0.1, h - 0.16, 0.06), "zloto", "metal", faza=0.0)
            p.blok("Lamowka tyl", (zn * 0.68, -0.08, -z - 0.045), (0.1, h - 0.16, 0.06), "zloto", "metal", faza=0.0)
        p.blok("Godlo", (0, 0.05, z + 0.07), (0.34, 0.34, 0.05), "zloto", "metal", rot=(0, 0, 45), faza=0.0)
        p.blok("Godlo srodek", (0, 0.05, z + 0.1), (0.16, 0.16, 0.04), "niebieski_ciemny", "polysk", rot=(0, 0, 45),
               faza=0.0)

    # --- pas z klamrą i poła tabardu (przód i tył)
    with p.na("LowerTorso", od="srodek"):
        w, h, d = p.wymiary("LowerTorso")
        z = d / 2
        p.blok("Klamra", (0, 0, z + 0.04), (0.42, 0.34, 0.08), "stal", "metal", faza=0.03)
        p.blok("Klamra srodek", (0, 0, z + 0.08), (0.2, 0.16, 0.04), "brazowy_ciemny", faza=0.0)
        # poła tabardu: sztywna, lekko odchylona od nóg (przy kroku noga nie przebija materiału)
        for zk, s, kat in ((1, "", -15), (-1, " tyl", 15)):
            with p.uklad(pos=(0, -h / 2 + 0.02, zk * (z + 0.07)), obrot=(kat, 0, 0)):
                p.blok("Pola" + s, (0, -0.32, 0), (1.24, 0.64, 0.08), "niebieski", "matowy", faza=0.0)
                for zn in (1, -1):
                    p.blok("Pola lamowka" + s, (zn * 0.62, -0.32, 0), (0.1, 0.64, 0.12), "zloto", "metal", faza=0.0)
                # dolny szpic (romb do połowy schowany pod połą) i złoty rąbek tuż za nim
                p.blok("Pola szpic" + s, (0, -0.64, -zk * 0.012), (0.62, 0.62, 0.06), "niebieski", "matowy",
                       rot=(0, 0, 45), faza=0.0)
                p.blok("Pola rabek" + s, (0, -0.69, -zk * 0.025), (0.74, 0.74, 0.06), "zloto", "metal",
                       rot=(0, 0, 45), faza=0.0)
                p.blok("Pola rabek poziom" + s, (0, -0.64, -zk * 0.025), (1.34, 0.1, 0.06), "zloto", "metal",
                       faza=0.0)

    # --- ręce: naramienniki, nałokcice, mankiety rękawic
    for strona, zn in (("Left", 1), ("Right", -1)):
        with p.na(strona + "UpperArm", od="srodek"):
            w, h, d = p.wymiary(strona + "UpperArm")
            p.blok("Naramiennik", (zn * 0.1, h / 2 - 0.06, 0), (1.32, 0.36, 1.32), "stal", "metal", faza=0.12)
            p.blok("Naramiennik lama 1", (zn * 0.16, h / 2 - 0.3, 0), (1.22, 0.2, 1.24), "stal_cien", "metal",
                   faza=0.06)
            p.blok("Naramiennik lama 2", (zn * 0.2, h / 2 - 0.48, 0), (1.1, 0.18, 1.14), "stal", "metal", faza=0.05)
            p.blok("Naramiennik nit", (zn * 0.78, h / 2 - 0.06, 0.3), (0.06, 0.1, 0.1), "zloto", "metal", faza=0.0)
            p.blok("Naramiennik nit 2", (zn * 0.78, h / 2 - 0.06, -0.3), (0.06, 0.1, 0.1), "zloto", "metal", faza=0.0)
        with p.na(strona + "LowerArm", od="srodek"):
            w, h, d = p.wymiary(strona + "LowerArm")
            p.blok("Nalokcica", (zn * 0.06, h / 2 - 0.05, -0.08), (0.95, 0.26, 0.9), "stal_cien", "metal", faza=0.06)
        with p.na(strona + "Hand", od="srodek"):
            w, h, d = p.wymiary(strona + "Hand")
            p.blok("Mankiet", (0, h / 2 + 0.02, 0), (1.04, 0.2, 1.04), "stal", "metal", faza=0.05)

    # --- nogi: nakolanniki, nagolenniki, trzewiki
    for strona, zn in (("Left", 1), ("Right", -1)):
        with p.na(strona + "UpperLeg", od="srodek"):
            w, h, d = p.wymiary(strona + "UpperLeg")
            p.blok("Udo plyta", (0, 0.05, d / 2 + 0.03), (0.8, 0.6, 0.06), "stal_cien", "metal", faza=0.02)
        with p.na(strona + "LowerLeg", od="srodek"):
            w, h, d = p.wymiary(strona + "LowerLeg")
            p.blok("Nakolannik", (0, h / 2 - 0.08, d / 2 + 0.06), (0.72, 0.36, 0.2), "stal_cien", "metal", faza=0.07)
            p.blok("Nagolennik", (0, -0.12, d / 2 + 0.03), (0.62, 0.42, 0.06), "stal", "metal", faza=0.02)
        with p.na(strona + "Foot", od="srodek"):
            w, h, d = p.wymiary(strona + "Foot")
            p.blok("Czubek", (0, -0.02, d / 2 + 0.03), (w - 0.1, 0.28, 0.1), "stal_cien", "metal", faza=0.03)
            p.blok("Podeszwa", (0, -h / 2 + 0.04, 0), (w + 0.04, 0.08, d + 0.04), "brazowy_ciemny", "matowy",
                   faza=0.0)

    # miecz: osobny przedmiot (rycerz_miecz.fbx, np. jako Tool); w FBX postaci go nie ma (eksport=False),
    # w renderach i filmach jest w dłoni
    m = miecz()
    p.zaloz(m, eksport=False)

    # --- klipy
    idle(p)
    chod(p)
    atak_miecz(p)
    wiwat(p)
    p.ustaw_poze_renderu("idle", 0)
    return [p, m]


SLABOSCI = [
    "Miecz jest osobnym przedmiotem (przedmioty/rycerz_miecz.fbx) — w FBX postaci go nie ma; w grze trzeba go "
    "dać jako Tool albo akcesorium na RightGripAttachment.",
    "Bryły sztywno przypięte do kości: przy dużych zamachach naramienniki przenikają hełm i tułów.",
    "Tabard i poły są sztywne (nie falują w chodzie); w ataku poła tnie uda.",
    "Klipy to szkice (1–2 s), nie gotowa animacja; atak nie ma efektu cięcia (smugi).",
    "LowerTorso i Root nie są w 0,0,0 (biodra na wysokości 1,9) — dla NPC bez znaczenia, ciało awatara może tego "
    "wymagać (sprawdzić przy pierwszym imporcie).",
]


# --------------------------------------------------------------------------- animacje
TRZYMA = {"RightUpperArm": (-12, 0, -4), "RightLowerArm": (-68, 0, 0)}   # miecz w gotowości (ostrze w górę-przód)


def idle(p):
    k = p.klip("idle", 60, petla=True)
    k.poza(0, TRZYMA)
    k.cykl("UpperTorso", "obrot", (2.0, 0, 0))
    k.cykl("UpperTorso", "obrot", (0, 2.0, 1.0), faza=0.25)
    k.cykl("Head", "obrot", (-1.5, 0, 1.5), faza=0.1)
    k.cykl("LeftUpperArm", "obrot", (0, 0, 2.5), srodek=(0, 0, 5))
    k.cykl("LeftLowerArm", "obrot", (-2.0, 0, 0), srodek=(-8, 0, 0), faza=0.1)
    # przedramię trzyma miecz w gotowości: jawny środek cyklu (−68°), żeby cykl nigdy nie zszedł do pozy wiszącej
    k.kanaly.pop(("RightLowerArm", "obrot"), None)
    k.cykl("RightLowerArm", "obrot", (-3.0, 0, 0), faza=0.15, srodek=TRZYMA["RightLowerArm"])
    k.kanaly.pop(("RightUpperArm", "obrot"), None)
    k.cykl("RightUpperArm", "obrot", (0, 0, -1.5), faza=0.15, srodek=TRZYMA["RightUpperArm"])
    return k


def chod(p, dlugosc=24, krok=32.0, ramiona=38.0):
    import math
    k = p.klip("chod", dlugosc, petla=True)
    k.cykl("LeftUpperLeg", "obrot", (krok, 0, 0), faza=0.0)
    k.cykl("RightUpperLeg", "obrot", (krok, 0, 0), faza=0.5)
    k.cykl("LeftUpperArm", "obrot", (ramiona, 0, 0), faza=0.5, srodek=(0, 0, 4))
    k.cykl("RightUpperArm", "obrot", (8, 0, 0), faza=0.0, srodek=TRZYMA["RightUpperArm"])
    k.cykl("RightLowerArm", "obrot", (-4, 0, 0), faza=0.0, srodek=TRZYMA["RightLowerArm"])
    for strona, faza in (("Left", 0.0), ("Right", 0.5)):
        for i in range(9):
            t = i / 8.0
            sn = math.sin(2 * math.pi * (t + faza))
            k.klucz(dlugosc * t, strona + "LowerLeg", obrot=(max(0.0, -sn) * krok * 1.4, 0, 0))
            k.klucz(dlugosc * t, strona + "Foot", obrot=(-max(0.0, sn) * 10, 0, 0))
    for i in range(9):
        t = i / 8.0
        sn = math.sin(2 * math.pi * (t + 0.5))
        k.klucz(dlugosc * t, "LeftLowerArm", obrot=(-12 - 10 * max(0.0, sn), 0, 0))
    k.cykl("LowerTorso", "przes", (0, 0.07, 0), czestosc=2, faza=0.25, srodek=(0, 0.07, 0))
    k.cykl("LowerTorso", "obrot", (0, 6, 0), faza=0.0)
    k.cykl("UpperTorso", "obrot", (0, -9, 0), faza=0.0, srodek=(4, 0, 0))
    k.cykl("Head", "obrot", (0, 3, 0), faza=0.0, srodek=(-3, 0, 0))
    return k


def atak_miecz(p):
    """Cięcie z góry: wzięcie z boku nad barkiem (ręka odchylona na zewnątrz, z dala od hełmu), łuk w dół
    z nadgarstkiem dociśniętym w uderzeniu (ostrze kładzie się do przodu), 2 klatki zatrzymania, powrót."""
    k = p.klip("atak_miecz", 32, petla=False)
    cz = (0.36, 0.48, 0.62)
    k.zamach("RightUpperArm", spocz=TRZYMA["RightUpperArm"], wziecie=(-150, 0, -40), uderzenie=(-48, 0, 6),
             czasy=cz, dobicie=0.0)
    k.zamach("RightLowerArm", spocz=TRZYMA["RightLowerArm"], wziecie=(-30, 0, 0), uderzenie=(-8, 0, 0), czasy=cz,
             dobicie=0.0)
    k.zamach("RightHand", wziecie=(55, 0, 0), uderzenie=(70, 0, 0), czasy=cz, dobicie=0.0)   # ostrze kładzie się do przodu
    # zatrzymanie po uderzeniu: 2 klatki w pozie uderzenia
    for kosc, w in (("RightUpperArm", (-48, 0, 6)), ("RightLowerArm", (-8, 0, 0)), ("RightHand", (70, 0, 0))):
        k.klucz(32 * cz[1] + 2, kosc, obrot=w)
    k.zamach("UpperTorso", wziecie=(-8, -14, 0), uderzenie=(14, 16, 0), czasy=cz)
    k.zamach("Head", wziecie=(-8, 8, 0), uderzenie=(4, -8, 0), czasy=cz)
    k.zamach("LeftUpperArm", wziecie=(-28, 0, 22), uderzenie=(20, 0, 14), czasy=cz)
    k.zamach("LeftLowerArm", wziecie=(-30, 0, 0), uderzenie=(-10, 0, 0), czasy=cz)
    k.zamach("LeftUpperLeg", wziecie=(-6, 0, 0), uderzenie=(-22, 0, 0), czasy=cz)
    k.zamach("LeftLowerLeg", wziecie=(4, 0, 0), uderzenie=(18, 0, 0), czasy=cz)
    k.zamach("RightUpperLeg", wziecie=(4, 0, 0), uderzenie=(12, 0, 0), czasy=cz)
    k.zamach("LowerTorso", wziecie=(0, -8, 0), uderzenie=(0, 10, 0), czasy=cz)
    return k


def wiwat(p, dlugosc=36):
    """Radość po zwycięstwie: miecz pionowo w górę, lewa pięść pompuje, dwa podskoki na pętlę."""
    k = p.klip("wiwat", dlugosc, petla=True)
    gora = {"RightUpperArm": (-170, 0, -16), "RightLowerArm": (-10, 0, 0), "RightHand": (84, 0, 0),
            "LeftUpperArm": (-160, 0, 22), "LeftLowerArm": (-18, 0, 0),
            "UpperTorso": (-7, 0, 0), "Head": (-12, 0, 0)}
    nizej = {"RightUpperArm": (-148, 0, -24), "RightLowerArm": (-28, 0, 0), "RightHand": (82, 0, 0),
             "LeftUpperArm": (-112, 0, 30), "LeftLowerArm": (-55, 0, 0),
             "UpperTorso": (3, 0, 0), "Head": (0, 0, 0)}
    for f, poza in ((0, nizej), (9, gora), (18, nizej), (27, gora)):
        k.poza(f, poza)
    # podskok: szczyt w klatkach 9 i 27 (razem z rękami w górze), stopy nigdy pod ziemią
    k.cykl("LowerTorso", "przes", (0, 0.16, 0), czestosc=2, faza=-0.25, srodek=(0, 0.16, 0))
    for strona in ("Left", "Right"):
        k.cykl(strona + "UpperLeg", "obrot", (-9, 0, 0), czestosc=2, faza=-0.25, srodek=(-9, 0, 0))
        k.cykl(strona + "LowerLeg", "obrot", (14, 0, 0), czestosc=2, faza=-0.25, srodek=(14, 0, 0))
    return k
