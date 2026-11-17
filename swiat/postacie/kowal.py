# -*- coding: utf-8 -*-
"""KOWAL — mistrz kuźni w bazarze (NPC, próba D-102; swiat/kowal_proba). Krępy, szeroki klockowy ludzik R15:
łysa głowa w czerwonej chustce z mosiężnymi goglami na czole, gęste czarne brwi i krótka czarna broda z dwoma
warkoczykami, sadza na policzku, szaroniebieska koszula bez rękawów, ciężki skórzany fartuch z kieszenią i nitami,
grube przedramiona, skórzana rękawica na lewej dłoni (trzyma szczypce), ciemne spodnie i buty z okutymi noskami;
w prawej dłoni młot kowalski. Inny niż zbrojmistrz bazaru (hełm z nosalem, ruda broda, młot na ramieniu).

    python -B swiat/postacie/przebuduj.py kowal --bez-filmow

Klipy: spoczynek (młot przy nodze, oddech, rozgląda się), kucie (zamach nad barkiem i uderzenie w kowadło przed sobą,
pętla 1 s), radosc (młot w górę i kiwnięcie głową — po udanym ulepszeniu).
Status: propozycja (własny projekt, nie kanon). Konwencje: 1 jednostka = 1 stud, Y w górę, postać patrzy w +Z,
jej LEWA strona to +X. Młot i szczypce są bryłami na kościach dłoni (nie akcesoriami), więc rig z klocków w grze
(swiat/kowal_proba) ma je od razu w rękach.
"""
from swiat.postacie.biblioteka.postac import Postac

ID = "kowal"

PALETA = {
    "skora": "E2A57A",            # opalona od paleniska
    "skora_cien": "C08460",
    "chustka": "C8372D",
    "chustka_cien": "962520",
    "broda": "2A1F1B",
    "gogle": "D9A441",
    "gogle_szklo": "7FD3E8",
    "koszula": "5D6B80",
    "koszula_cien": "48536A",
    "fartuch": "6B3E1E",
    "fartuch_cien": "4A2A12",
    "fartuch_pas": "33200F",
    "nit": "C9CED6",
    "spodnie": "3B3944",
    "but": "2B1E16",
    "okucie": "8E98A8",
    "rekawica": "8A5A2C",
    "trzonek": "8B5A2E",
    "glowica": "4A5368",
    "glowica_jasna": "AEB8C6",
    "sadza": "5C504A",
    "usta": "6E2A22",
    "zar": "FF7A1F",
}


def zbuduj():
    p = Postac(ID, "Kowal", typ="r15", skala=1.0, faza=0.05, paleta=PALETA,
               wymiary={"Head": (1.6, 1.45, 1.45),
                        "UpperTorso": (2.8, 1.8, 1.5),
                        "LowerTorso": (2.5, 0.5, 1.4),
                        "UpperArm": (1.05, 1.0, 1.05),
                        "LowerArm": (1.1, 0.85, 1.1),
                        "Hand": (1.0, 0.42, 1.0),
                        "UpperLeg": (1.1, 0.65, 1.1),
                        "LowerLeg": (1.1, 0.6, 1.1),
                        "Foot": (1.2, 0.4, 1.5)},
               rozstaw_rak=2.05)
    p.cialo({"glowa": "skora", "tulow": "koszula", "pas": "spodnie", "ramiona": "koszula",
             "LeftLowerArm": "skora", "RightLowerArm": "skora", "LeftHand": "rekawica", "RightHand": "skora",
             "LeftUpperLeg": "spodnie", "RightUpperLeg": "spodnie",
             "LeftLowerLeg": "but", "RightLowerLeg": "but", "stopy": "but"})

    # --- głowa: chustka z węzłem, gogle na czole, brwi, broda z warkoczykami, sadza
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        z = d / 2
        p.blok("Chustka czapa", (0, h / 2 + 0.1, -0.03), (w + 0.12, 0.32, d + 0.08), "chustka", "matowy", faza=0.08)
        p.blok("Chustka czolo", (0, h / 2 - 0.12, 0.0), (w + 0.1, 0.24, d + 0.1), "chustka", "matowy")
        p.blok("Chustka wezel", (0, h / 2 - 0.15, -z - 0.14), (0.42, 0.34, 0.24), "chustka_cien", "matowy", faza=0.06)
        p.klin("Chustka koniec L", (0.2, h / 2 - 0.55, -z - 0.16), (0.24, 0.5, 0.1), "chustka_cien", "matowy",
               rot=(0, 0, -14))
        p.klin("Chustka koniec P", (-0.18, h / 2 - 0.6, -z - 0.15), (0.24, 0.6, 0.1), "chustka", "matowy",
               rot=(0, 0, 18))
        p.blok("Gogle pasek", (0, h / 2 - 0.08, 0.0), (w + 0.16, 0.12, d + 0.14), "fartuch_pas", "matowy", faza=0.0)
        for zn in (1, -1):
            s = "L" if zn > 0 else "P"
            p.walec("Gogle oprawka " + s, (zn * 0.32, h / 2 - 0.02, z + 0.1), (0.46, 0.14, 0.46), "gogle", "metal",
                    rot=(90, 0, 0), segm=10)
            p.walec("Gogle szklo " + s, (zn * 0.32, h / 2 - 0.02, z + 0.18), (0.32, 0.04, 0.32), "gogle_szklo",
                    "polysk", rot=(90, 0, 0), segm=10)
            p.blok("Ucho " + s, (zn * (w / 2 + 0.08), 0.0, 0.0), (0.16, 0.36, 0.3), "skora_cien", "matowy")
            xo = zn * 0.36
            p.blok("Oko " + s, (xo, 0.06, z + 0.02), (0.17, 0.2, 0.06), "tusz", faza=0.0)
            p.blok("Oko blik " + s, (xo + 0.04, 0.11, z + 0.05), (0.06, 0.06, 0.02), "bialy", faza=0.0)
            p.blok("Brew " + s, (xo, 0.3, z + 0.04), (0.5, 0.16, 0.1), "broda", "matowy", rot=(0, 0, zn * -10),
                   faza=0.0)
            p.blok("Policzek " + s, (zn * 0.58, -0.12, z + 0.005), (0.26, 0.14, 0.04), "rumieniec", "matowy", faza=0.0)
            # broda: boki od uszu do podbródka, warkoczyki na końcu
            p.blok("Broda bok " + s, (zn * (w / 2 - 0.12), -0.3, z - 0.18), (0.26, 0.62, 0.5), "broda", "matowy",
                   faza=0.05)
            p.blok("Warkocz " + s, (zn * 0.22, -h / 2 - 0.32, z + 0.02), (0.16, 0.4, 0.16), "broda", "matowy",
                   rot=(0, 0, zn * 6))
            p.blok("Warkocz obraczka " + s, (zn * 0.22, -h / 2 - 0.36, z + 0.02), (0.2, 0.08, 0.2), "gogle", "metal",
                   faza=0.0)
        p.blok("Nos", (0, -0.08, z + 0.16), (0.36, 0.36, 0.3), "skora_cien", "matowy", faza=0.08)
        p.blok("Was", (0, -0.36, z + 0.08), (0.9, 0.16, 0.14), "broda", "matowy")
        p.blok("Broda", (0, -h / 2 + 0.02, z - 0.02), (w - 0.2, 0.42, 0.28), "broda", "matowy", faza=0.06)
        p.blok("Broda dol", (0, -h / 2 - 0.12, z - 0.12), (0.8, 0.26, 0.36), "broda", "matowy", faza=0.05)
        p.blok("Usta", (0, -0.5, z + 0.02), (0.36, 0.08, 0.05), "usta", faza=0.0)
        p.blok("Sadza", (0.46, -0.02, z + 0.012), (0.24, 0.12, 0.03), "sadza", "matowy", rot=(0, 0, 20), faza=0.0)

    # --- tułów: koszula bez rękawów, fartuch na szelkach z kieszenią i nitami
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.blok("Fartuch przod", (0, -0.12, z + 0.05), (1.9, h - 0.15, 0.1), "fartuch", "matowy")
        p.blok("Kieszen", (0, -0.42, z + 0.12), (0.8, 0.5, 0.06), "fartuch_cien", "matowy", faza=0.0)
        p.blok("Mlotek w kieszeni", (0.22, -0.1, z + 0.14), (0.1, 0.5, 0.08), "trzonek", "matowy", faza=0.0)
        for zn in (1, -1):
            s = "L" if zn > 0 else "P"
            p.blok("Szelka " + s, (zn * 0.62, 0.35, z + 0.06), (0.22, h - 0.65, 0.08), "fartuch_pas", "matowy",
                   faza=0.0)
            p.blok("Szelka tyl " + s, (zn * 0.62, 0.05, -z - 0.04), (0.22, h - 0.1, 0.08), "fartuch_pas", "matowy",
                   faza=0.0)
            p.blok("Szelka bark " + s, (zn * 0.62, h / 2 + 0.03, 0), (0.22, 0.08, d + 0.08), "fartuch_pas", "matowy",
                   faza=0.0)
            p.blok("Nit " + s, (zn * 0.62, 0.66, z + 0.11), (0.12, 0.12, 0.04), "nit", "metal", faza=0.0)
            p.blok("Pacha " + s, (zn * (w / 2 - 0.14), 0.3, 0), (0.3, 0.9, d - 0.1), "koszula_cien", "matowy",
                   faza=0.0)
        p.blok("Dekolt", (0, h / 2 - 0.12, z + 0.02), (0.6, 0.24, 0.04), "skora", faza=0.0)
        p.blok("Szyja", (0, h / 2 + 0.04, -0.05), (1.1, 0.1, 1.0), "skora", faza=0.0)

    # --- pas: rzemień, fartuch do kolan (przód) i klamra
    with p.na("LowerTorso", od="srodek"):
        w, h, d = p.wymiary("LowerTorso")
        z = d / 2
        p.blok("Pas", (0, 0.05, 0), (w + 0.08, 0.24, d + 0.08), "fartuch_pas", "matowy")
        p.blok("Klamra", (0, 0.05, z + 0.06), (0.34, 0.28, 0.06), "gogle", "metal", faza=0.03)
        p.blok("Fartuch dol", (0, -0.55, z + 0.1), (1.9, 1.3, 0.1), "fartuch", "matowy")
        p.blok("Fartuch rabek", (0, -1.18, z + 0.11), (1.92, 0.1, 0.11), "fartuch_cien", "matowy", faza=0.0)

    # --- ręce: gołe, grube przedramiona; skórzana opaska na prawym nadgarstku; rękawica z mankietem na lewej
    for s in ("Left", "Right"):
        with p.na(s + "UpperArm", od="srodek"):
            w, h, d = p.wymiary(s + "UpperArm")
            p.blok("Bark", (0, h / 2 - 0.2, 0), (w + 0.1, 0.4, d + 0.08), "koszula", "matowy", faza=0.08)
            p.blok("Biceps", (0, -0.15, 0), (w - 0.04, h - 0.4, d - 0.04), "skora", faza=0.05)
        with p.na(s + "LowerArm", od="srodek"):
            w, h, d = p.wymiary(s + "LowerArm")
            if s == "Right":
                p.blok("Opaska", (0, -h / 2 + 0.12, 0), (w + 0.08, 0.2, d + 0.08), "fartuch_pas", "matowy")
            else:
                p.blok("Mankiet rekawicy", (0, -h / 2 + 0.15, 0), (w + 0.12, 0.3, d + 0.12), "rekawica", "matowy")
        with p.na(s + "UpperLeg", od="srodek"):
            w, h, d = p.wymiary(s + "UpperLeg")
            p.blok("Lata", (0.0, -0.05, d / 2 + 0.01), (0.4, 0.3, 0.03), "koszula_cien", "matowy", faza=0.0)
        with p.na(s + "LowerLeg", od="srodek"):
            w, h, d = p.wymiary(s + "LowerLeg")
            p.blok("Cholewa", (0, h / 2 - 0.08, 0), (w + 0.12, 0.18, d + 0.12), "fartuch_pas", "matowy")
        with p.na(s + "Foot", od="srodek"):
            w, h, d = p.wymiary(s + "Foot")
            p.blok("Podeszwa", (0, -h / 2 + 0.05, 0), (w + 0.06, 0.1, d + 0.06), "tusz", "matowy")
            p.blok("Okucie", (0, 0.0, d / 2 - 0.12), (w - 0.06, h - 0.06, 0.3), "okucie", "metal")

    # --- młot w prawej dłoni: trzonek przedłuża rękę (−Y dłoni), obuch wzdłuż Z; twarz obucha po stronie −Z dłoni
    #     (przy ręce wyciągniętej do przodu i zgiętym nadgarstku patrzy w dół, na kowadło)
    with p.na("RightHand", od="srodek"):
        w, h, d = p.wymiary("RightHand")
        p.blok("Piesc", (0, 0, 0.0), (w + 0.04, h + 0.06, d + 0.04), "skora", faza=0.06)
        p.blok("Trzonek", (0, -0.62, 0), (0.2, 1.0, 0.2), "trzonek", "matowy")
        p.blok("Obuch", (0, -1.2, 0), (0.5, 0.5, 1.0), "glowica", "metal", faza=0.04)
        p.blok("Obuch twarz", (0, -1.2, -0.52), (0.54, 0.54, 0.08), "glowica_jasna", "metal", faza=0.0)
        p.blok("Obuch klin", (0, -1.2, 0.54), (0.4, 0.4, 0.1), "glowica_jasna", "metal", faza=0.0)
        p.blok("Obuch opaska", (0, -1.2, 0), (0.54, 0.54, 0.14), "fartuch_pas", "matowy", faza=0.0)

    # --- szczypce w lewej (rękawica): dwa ramiona wzdłuż −Y z rozżarzonym końcem
    with p.na("LeftHand", od="srodek"):
        for zn in (1, -1):
            p.blok("Szczypce ramie " + ("a" if zn > 0 else "b"), (zn * 0.07, -0.75, 0.05), (0.08, 1.2, 0.1), "glowica",
                   "metal", rot=(0, 0, zn * 3), faza=0.0)
        p.blok("Szczypce szczeki", (0, -1.4, 0.05), (0.26, 0.16, 0.16), "glowica", "metal", faza=0.0)
        p.blok("Zar w szczypcach", (0, -1.55, 0.05), (0.18, 0.2, 0.42), "zar", "swiecacy", faza=0.0)

    # --- klipy (stopnie, osie modelu): rx < 0 unosi zwisającą rękę do przodu, a tułów odchyla do tyłu (rx > 0 =
    #     skłon w przód); rz > 0 odchyla kończynę w stronę +X (prawą rękę — do środka). Uderzenie dobrane
    #     kinematyką rigu z klocków (swiat/kowal_proba/testy/test_kowala.py): twarz obucha ok. 1,45 st w prawo,
    #     2,4 st przed postacią, 2,8 st nad stopami — tam stoi blat kowadła kuźni; szczypce trzymają sztabę po lewej.
    BAZA = {"RightUpperArm": (-8, 0, -6), "RightLowerArm": (-6, 0, 0),
            "LeftUpperArm": (-28, 0, 8), "LeftLowerArm": (-42, 0, 0), "LeftHand": (0, 0, 0)}

    k = p.klip("spoczynek", 60, petla=True)
    k.poza(0, BAZA)
    k.cykl("UpperTorso", "obrot", (1.5, 0, 0))
    k.cykl("UpperTorso", "przes", (0, 0.03, 0), faza=0.25)
    k.cykl("Head", "obrot", (1.5, 9, 0), faza=0.1)
    k.cykl("RightUpperArm", "obrot", (-2, 0, 0), faza=0.2)

    k = p.klip("kucie", 30, petla=True)
    lewa = {"LeftUpperArm": (-75, 0, -30), "LeftLowerArm": (-65, 0, 0), "LeftHand": (80, 0, 0)}
    lewa_nisko = {"LeftUpperArm": (-55, 0, -25), "LeftLowerArm": (-55, 0, 0), "LeftHand": (75, 0, 0)}  # zamach: twarz odsłonięta
    gora = {**lewa_nisko, "RightUpperArm": (-160, 0, 5), "RightLowerArm": (-35, 0, 0), "RightHand": (10, 0, 0),
            "UpperTorso": {"obrot": (-6, -8, 0), "przes": (0, 0, 0)}, "Head": (-4, 0, 0),
            "LowerTorso": {"przes": (0, 0, 0)}}
    k.poza(0, gora)
    k.poza(9, {**gora, "RightUpperArm": (-172, 0, 5), "UpperTorso": {"obrot": (-9, -10, 0), "przes": (0, 0, 0)}},
           wyg="liniowo")
    uderzenie = {**lewa, "RightUpperArm": (-80, 0, 15), "RightLowerArm": (-65, 0, 0), "RightHand": (80, 0, 0),
                 "UpperTorso": {"obrot": (10, 4, 0), "przes": (0, -0.05, 0)}, "Head": (8, 0, 0),
                 "LowerTorso": {"przes": (0, -0.02, 0)}}
    k.poza(14, uderzenie)
    k.poza(17, {**uderzenie, "RightUpperArm": (-95, 0, 14), "RightHand": (60, 0, 0), "Head": (4, 0, 0)})
    k.poza(30, gora)

    k = p.klip("radosc", 40, petla=False)
    k.poza(0, BAZA)
    wiwat = {"RightUpperArm": (-172, 0, -24), "RightLowerArm": (-12, 0, 0),
             "LeftUpperArm": (-30, 0, 40), "LeftLowerArm": (-60, 0, 0), "Head": (-10, 0, 0),
             "UpperTorso": (-6, 0, 0)}
    k.poza(10, wiwat)
    k.poza(18, {**wiwat, "Head": (8, 0, 0), "RightUpperArm": (-165, 0, -20)})
    k.poza(26, {**wiwat, "Head": (-8, 0, 0)})
    k.poza(40, {**BAZA, "Head": (0, 0, 0), "UpperTorso": (0, 0, 0)})

    p.ustaw_poze_renderu("kucie", 9)
    return [p]


SLABOSCI = [
    "Młot i szczypce to bryły na kościach dłoni (nie osobne akcesoria) — w FBX postaci są częścią dłoni.",
    "Uderzenie młotem jest ustawione na kowadło kuźni z swiat/kowal_proba (twarz obucha ok. 2,4 studa przed postacią "
    "i 1,45 w prawo, blat ok. 2,8 nad stopami); przy innym kowadle młot może trafiać nad nim albo w nie wchodzić.",
    "Broda, fartuch i ręce to sztywne bryły na kościach: przy pełnym zamachu bark lekko wchodzi w chustkę.",
    "Klipy to szkice (1–1,3 s), nie gotowa animacja.",
]
