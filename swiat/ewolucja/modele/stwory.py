# -*- coding: utf-8 -*-
"""Stwory obok smoka, w tym samym stylu i z tych samych klocków danych: OWCA (ofiara dla maluchów) i KNIGHT GOLEM
(mini-boss strzegący skarbu, pięć stopni przez przemalowanie i dodatki).

    from swiat.ewolucja.modele import stwory
    stwory.owca(); stwory.golem(3)          # Postac z klipami (te same regiony koloru co smok: cialo, luski, zar…)

Owca — stawy: Tulow, Glowa, NogaPL, NogaPP, NogaTL, NogaTP, Ogonek; klipy: spoczynek, chod, ucieczka, zjedzona.
Golem — stawy: Tulow, Klatka, Glowa, RekaL1/2, RekaP1/2, NogaL1/2, NogaP1/2; klipy: spoczynek, chod, zamach,
uderzenie, zachwianie, upadek (wszystkie stopnie mają te same stawy i klipy).
"""
from swiat.ewolucja.modele.smok_klipy import petla, sekwencja
from swiat.ewolucja.modele.smok_model import Smok, _mix

NOGI_OWCY = (("NogaPL", 0.45, 0.6, 0.0), ("NogaPP", -0.45, 0.6, 0.5), ("NogaTL", 0.45, -0.6, 0.5), ("NogaTP", -0.45, -0.6, 0.0))


def owca(skala=1.0):
    """Klockowa owca: ok. 2,3 studa długości przy skali 1 (ofiara dla HATCHLING i WHELP)."""
    pal = {"welna": "FFF8EC", "welna_c": "E4D8C6", "pysk": "4A3A5A", "noga": "372B46", "bialy": "FFFFFF", "rozowy": "FF9AA8"}
    p = Smok("owca", "Owca", typ="stwor", skala=skala, faza=0.12, paleta=pal)
    p.kosc("Tulow", "Root", (0, 1.15, 0), czesc=(1.5, 1.2, 2.0))
    p.kosc("Glowa", "Tulow", (0, 1.45, 0.95), czesc=(0.9, 0.8, 0.8), srodek=(0, 0.1, 0.35))
    for n, x, z, _ in NOGI_OWCY:
        p.kosc(n, "Tulow", (x, 0.72, z), czesc=(0.34, 0.72, 0.34), srodek=(0, -0.36, 0), dl=0.25)
    p.kosc("Ogonek", "Tulow", (0, 1.4, -1.0), czesc=(0.4, 0.4, 0.4), dl=0.2)
    with p.na("Tulow"):
        p.blok("Welna", (0, 0, 0), (1.5, 1.2, 2.0), "welna", "matowy", faza=0.28)
        p.blok("Welna grzbiet", (0, 0.62, -0.1), (1.1, 0.3, 1.4), "welna_c", "matowy", faza=0.12)
        p.blok("Welna piers", (0, 0.1, 0.95), (1.2, 0.9, 0.4), "welna", "matowy", faza=0.16)
    with p.na("Glowa"):
        p.blok("Pysk", (0, 0.1, 0.35), (0.8, 0.75, 0.8), "pysk", faza=0.14)
        p.blok("Czupryna", (0, 0.52, 0.2), (0.86, 0.34, 0.6), "welna", "matowy", faza=0.12)
        p.blok("Nos", (0, -0.08, 0.76), (0.26, 0.12, 0.05), "rozowy", "matowy", faza=0.0)
        for zn in (1, -1):
            p.blok("Oko", (zn * 0.24, 0.2, 0.76), (0.22, 0.26, 0.06), "bialy", "polysk", faza=0.02)
            p.blok("Zrenica", (zn * 0.24, 0.17, 0.79), (0.11, 0.15, 0.04), "noga", "polysk", faza=0.0)
            p.blok("Ucho", (zn * 0.52, 0.3, 0.1), (0.3, 0.16, 0.26), "pysk", rot=(0, 0, -zn * 20), faza=0.05)
    for n, _, _, _ in NOGI_OWCY:
        with p.na(n):
            p.blok("Noga", (0, -0.36, 0), (0.32, 0.72, 0.32), "noga", faza=0.06)
    with p.na("Ogonek"):
        p.blok("Ogonek", (0, 0, -0.12), (0.4, 0.4, 0.4), "welna", "matowy", faza=0.14)
    p.zaczep("SrodekAttachment", "Tulow", (0, 0, 0))

    petla(p, "spoczynek", 60, {"Glowa": (26, 0, 0)}, [                          # skubie trawę
        ("Glowa", "obrot", (7, 5, 0), 2, 0.0), ("Ogonek", "obrot", (0, 26, 0), 4, 0.0), ("Tulow", "przes", (0, 0.02, 0), 1, 0.0)])
    petla(p, "chod", 20, {}, [(n, "obrot", (24, 0, 0), 1, f) for n, _, _, f in NOGI_OWCY] + [
        ("Tulow", "przes", (0, 0.04, 0), 2, 0.2), ("Glowa", "obrot", (4, 0, 0), 2, 0.3), ("Ogonek", "obrot", (0, 14, 0), 2, 0.0)])
    petla(p, "ucieczka", 12, {"Glowa": (-14, 0, 0), "Tulow": {"obrot": (4, 0, 0), "przes": (0, 0.1, 0)}},
          [(n, "obrot", (44, 0, 0), 1, 0.06 * (i % 2) + (0.5 if i >= 2 else 0.0)) for i, (n, _, _, _) in enumerate(NOGI_OWCY)] + [
              ("Tulow", "przes", (0, 0.22, 0), 1, 0.2), ("Tulow", "obrot", (8, 0, 0), 1, 0.45), ("Ogonek", "obrot", (24, 0, 0), 2, 0.0)])
    nogi_w_gore = {n: (-50 if "P" == n[4] else 50, 0, 0) for n, _, _, _ in NOGI_OWCY}
    sekwencja(p, "zjedzona", 20, [
        (0.25, dict({"Tulow": {"przes": (0, 0.55, 0), "obrot": (-10, 0, 20)}, "Glowa": (-20, 0, 0)}, **nogi_w_gore)),
        (0.6, dict({"Tulow": {"przes": (0, 0.1, 0), "obrot": (0, 40, 85)}, "Glowa": (10, 0, 0)}, **nogi_w_gore)),
        (1.0, {"Tulow": {"przes": (0, -0.42, 0), "obrot": (0, 60, 90)}, "Glowa": (24, 0, 0), "NogaPL": (-20, 0, 0),
               "NogaPP": (-30, 0, 0), "NogaTL": (25, 0, 0), "NogaTP": (35, 0, 0), "Ogonek": (0, 0, 0)})], {"zjedzona": 0.6})
    return p


STOPNIE_GOLEMA = {   # stopień = paleta regionów + dodatki
    1: {"cialo": "8A8496", "zar": "FF7A2A", "kolce": "D8D2C0", "blona": "6A4A3A", "dodatki": ()},
    2: {"cialo": "B0764A", "zar": "FFC21F", "kolce": "F2E2B0", "blona": "7A2E2E", "dodatki": ("kolce",)},
    3: {"cialo": "5E6E8E", "zar": "4FD0FF", "kolce": "E6F4FF", "blona": "2F4A8A", "dodatki": ("kolce", "tarcza")},
    4: {"cialo": "3A3048", "zar": "C04DFF", "kolce": "B9A6FF", "blona": "5A1E7A", "dodatki": ("kolce", "tarcza", "korona")},
    5: {"cialo": "E0B23A", "zar": "FFF6B0", "kolce": "7FF8FF", "blona": "B8202E", "dodatki": ("kolce", "tarcza", "korona", "peleryna")},
}


def golem(stopien=1, skala=1.6):
    """KNIGHT GOLEM: kamienny rycerz z łuskami-dachówkami, żarem w szczelinach i kryształowym mieczem.
    Wysokość ok. 9 jednostek × skala (stopień 1: ok. 14 studów); wyższy stopień jest o 8% większy na stopień."""
    T = STOPNIE_GOLEMA[stopien]
    pal = {k: T[k] for k in ("cialo", "zar", "kolce", "blona")}
    pal.update({"cialo_c": _mix(T["cialo"], "140A1E", 0.45), "cialo_j": _mix(T["cialo"], "FFFFFF", 0.2),
                "zar_c": _mix(T["zar"], "140A1E", 0.3), "zar_j": _mix(T["zar"], "FFFFFF", 0.6),
                "kolce_c": _mix(T["kolce"], "140A1E", 0.3), "blona_c": _mix(T["blona"], "140A1E", 0.3)})
    dod = T["dodatki"]
    p = Smok("golem_%d" % stopien, "Knight Golem %d" % stopien, typ="stwor", skala=skala * (1 + 0.08 * (stopien - 1)),
             faza=0.1, paleta=pal)
    p.kosc("Tulow", "Root", (0, 3.6, 0), czesc=(2.6, 1.2, 1.6))
    p.kosc("Klatka", "Tulow", (0, 4.3, 0), czesc=(3.6, 2.7, 2.0), srodek=(0, 1.35, 0))
    p.kosc("Glowa", "Klatka", (0, 7.05, 0.1), czesc=(1.5, 1.4, 1.5), srodek=(0, 0.7, 0))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Reka%s1" % s, "Klatka", (zn * 2.4, 6.4, 0), czesc=(1.2, 2.0, 1.2), srodek=(0, -1.0, 0))
        p.kosc("Reka%s2" % s, "Reka%s1" % s, (zn * 2.4, 4.4, 0), czesc=(1.3, 2.2, 1.3), srodek=(0, -1.1, 0))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Noga%s1" % s, "Tulow", (zn * 0.8, 3.6, 0), czesc=(1.2, 1.8, 1.3), srodek=(0, -0.9, 0))
        p.kosc("Noga%s2" % s, "Noga%s1" % s, (zn * 0.8, 1.8, 0), czesc=(1.3, 1.8, 1.5), srodek=(0, -0.9, 0.1))
    with p.na("Tulow"):
        p.blok("Biodra", (0, 0, 0), (2.6, 1.3, 1.6), "cialo", faza=0.14)
        p.blok("Pas zaru", (0, 0.62, 0), (2.3, 0.14, 1.7), "zar_c", "swiecacy", faza=0.0)
    with p.na("Klatka"):
        p.blok("Klatka", (0, 1.45, 0), (3.6, 2.5, 2.0), "cialo", faza=0.18)
        p.blok("Serce", (0, 1.5, 1.02), (1.0, 1.0, 0.1), "zar_j", "swiecacy", rot=(0, 0, 45), faza=0.0)
        p.blok("Zar piersi", (0, 1.5, 0.98), (2.6, 0.2, 0.1), "zar_c", "swiecacy", faza=0.0)
        p.blok("Zar plecow", (0, 1.4, -1.0), (0.5, 2.0, 0.1), "zar_c", "swiecacy", faza=0.0)
        for i, y in enumerate((2.3, 1.5, 0.7)):                 # łuski-dachówki na plecach
            p.blok("Luska plecow", (0, y, -1.06), (3.2 - 0.3 * i, 0.66, 0.2), "cialo_c", "matowy", rot=(-10, 0, 0), faza=0.05)
        for zn in (1, -1):
            p.blok("Naramiennik", (zn * 2.3, 2.5, 0), (1.9, 0.5, 2.2), "cialo_c", "matowy", rot=(0, 0, -zn * 14), faza=0.08)
            if "kolce" in dod:
                p.klin("Kolec barku", (zn * 2.6, 3.2, -0.1), (0.36, 1.1, 0.9), "kolce", "polysk", rot=(0, 180, -zn * 14), faza=0.02)
            if "peleryna" in dod:
                p.blok("Peleryna", (zn * 0.9, 0.4, -1.3), (1.7, 3.6, 0.12), "blona", "matowy", rot=(-8, 0, zn * 4), faza=0.0)
        p.zaczep("SerceAttachment", "Klatka", (0, 1.5, 1.2))
    with p.na("Glowa"):
        p.blok("Helm", (0, 0.7, 0), (1.5, 1.4, 1.5), "cialo", faza=0.14)
        p.blok("Wizjer", (0, 0.72, 0.76), (1.1, 0.22, 0.06), "zar_j", "swiecacy", faza=0.0)
        p.blok("Daszek", (0, 1.44, 0.05), (1.7, 0.24, 1.7), "cialo_c", "matowy", rot=(8, 0, 0), faza=0.06)
        p.klin("Grzebien", (0, 1.95, -0.1), (0.3, 0.9, 1.3), "kolce", "polysk", rot=(0, 180, 0), faza=0.02)
        if "korona" in dod:
            for zn in (1, -1):
                p.klin("Rog", (zn * 0.85, 1.7, -0.1), (0.3, 1.5, 0.5), "kolce", "swiecacy" if stopien == 5 else "polysk",
                       rot=(-20, 180, -zn * 30), faza=0.02)
        p.zaczep("GlowaAttachment", "Glowa", (0, 2.6, 0))
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Reka%s1" % s):
            p.blok("Ramie", (0, -1.0, 0), (1.15, 2.2, 1.15), "cialo", faza=0.12)
        with p.na("Reka%s2" % s):
            p.blok("Rekawica", (0, -1.0, 0), (1.4, 2.0, 1.4), "cialo_c", "matowy", faza=0.12)
            p.blok("Zar rekawicy", (0, 0.02, 0), (1.2, 0.14, 1.2), "zar_c", "swiecacy", faza=0.0)
            p.blok("Piesc", (0, -2.2, 0), (1.2, 0.7, 1.2), "cialo", faza=0.12)
            if s == "P":                                        # miecz w prawej dłoni: ostrze do przodu, gdy ręka zwisa
                p.blok("Rekojesc", (0, -2.2, 0.5), (0.34, 0.34, 1.8), "cialo_c", "matowy", faza=0.04)
                p.blok("Jelec", (0, -2.2, 1.2), (1.8, 0.4, 0.34), "kolce_c", "polysk", faza=0.04)
                p.klin("Ostrze", (0, -2.2, 3.6), (0.3, 1.1, 4.6), "kolce", "polysk", rot=(0, 180, 90), faza=0.0)
                p.blok("Zar ostrza", (0, -2.2, 3.2), (0.34, 0.2, 3.6), "zar_j", "swiecacy", faza=0.0)
                p.zaczep("MieczAttachment", "RekaP2", (0, -2.2, 5.8))
            elif "tarcza" in dod:
                p.blok("Tarcza", (0.8, -1.2, 0.2), (0.24, 3.2, 2.6), "blona", "matowy", faza=0.06)
                p.blok("Okucie tarczy", (0.84, -1.2, 0.2), (0.24, 3.5, 0.5), "cialo_c", "matowy", faza=0.04)
                p.blok("Znak tarczy", (0.96, -1.0, 0.2), (0.08, 0.9, 0.9), "zar_j", "swiecacy", rot=(45, 0, 0), faza=0.0)
        with p.na("Noga%s1" % s):
            p.blok("Udo", (0, -0.9, 0), (1.2, 2.0, 1.3), "cialo", faza=0.12)
        with p.na("Noga%s2" % s):
            p.blok("Goleń", (0, -0.8, 0), (1.35, 1.7, 1.45), "cialo_c", "matowy", faza=0.12)
            p.blok("Stopa", (0, -1.55, 0.3), (1.5, 0.5, 2.2), "cialo", faza=0.1)

    petla(p, "spoczynek", 80, {}, [
        ("Klatka", "przes", (0, 0.05, 0), 1, 0.0), ("Klatka", "obrot", (1.5, 0, 0), 1, 0.25), ("Glowa", "obrot", (0, 7, 0), 1, 0.1),
        ("RekaL1", "obrot", (2, 0, 2), 1, 0.2), ("RekaP1", "obrot", (2, 0, -2), 1, 0.2), ("RekaP2", "obrot", (3, 0, 0), 1, 0.4)])
    petla(p, "chod", 40, {"NogaL2": (12, 0, 0), "NogaP2": (12, 0, 0), "RekaP2": (-20, 0, 0)}, [
        ("NogaL1", "obrot", (22, 0, 0), 1, 0.0), ("NogaP1", "obrot", (22, 0, 0), 1, 0.5),
        ("NogaL2", "obrot", (12, 0, 0), 1, 0.3), ("NogaP2", "obrot", (12, 0, 0), 1, 0.8),
        ("Tulow", "przes", (0, 0.09, 0), 2, 0.1), ("Tulow", "obrot", (0, 0, 2.5), 1, 0.0), ("Klatka", "obrot", (0, 6, 0), 1, 0.5),
        ("RekaL1", "obrot", (14, 0, 0), 1, 0.5), ("RekaP1", "obrot", (8, 0, 0), 1, 0.0), ("Glowa", "obrot", (0, -4, 0), 1, 0.5)])
    sekwencja(p, "zamach", 36, [
        (0.38, {"Klatka": (-4, -34, 0), "RekaP1": (-150, 0, -24), "RekaP2": (-34, 0, 0), "RekaL1": (-20, 0, 24),
                "Glowa": (0, 20, 0), "Tulow": {"przes": (0, -0.1, -0.2), "obrot": (0, -8, 0)}}, "liniowo"),
        (0.5, {"Klatka": (14, 30, 0), "RekaP1": (-42, 0, 26), "RekaP2": (-8, 0, 0), "RekaL1": (20, 0, 16), "Glowa": (4, -16, 0),
               "Tulow": {"przes": (0, -0.3, 0.5), "obrot": (4, 8, 0)}, "NogaL1": (-22, 0, 0), "NogaL2": (26, 0, 0)}),
        (0.66, {"Klatka": (16, 36, 0), "RekaP1": (-30, 0, 30), "RekaP2": (-4, 0, 0), "Tulow": {"przes": (0, -0.3, 0.45), "obrot": (4, 8, 0)},
                "NogaL1": (-20, 0, 0), "NogaL2": (24, 0, 0)})], {"uderzenie": 0.5})
    rece_gora = {"RekaL1": (-172, 0, 12), "RekaP1": (-172, 0, -12), "RekaL2": (-14, 0, 0), "RekaP2": (-14, 0, 0)}
    sekwencja(p, "uderzenie", 44, [
        (0.36, dict({"Klatka": (-16, 0, 0), "Glowa": (-12, 0, 0), "Tulow": {"przes": (0, 0.15, -0.2), "obrot": (-4, 0, 0)}}, **rece_gora),
         "liniowo"),
        (0.52, {"Klatka": (40, 0, 0), "Glowa": (-20, 0, 0), "Tulow": {"przes": (0, -0.7, 0.4), "obrot": (10, 0, 0)},
                "RekaL1": (-66, 0, 10), "RekaP1": (-66, 0, -10), "RekaL2": (-20, 0, 0), "RekaP2": (-20, 0, 0),
                "NogaL1": (-34, 0, 0), "NogaP1": (-34, 0, 0), "NogaL2": (52, 0, 0), "NogaP2": (52, 0, 0)}),
        (0.72, {"Klatka": (36, 0, 0), "Glowa": (-16, 0, 0), "Tulow": {"przes": (0, -0.64, 0.4), "obrot": (9, 0, 0)},
                "RekaL1": (-62, 0, 10), "RekaP1": (-62, 0, -10), "NogaL1": (-32, 0, 0), "NogaP1": (-32, 0, 0),
                "NogaL2": (50, 0, 0), "NogaP2": (50, 0, 0)})], {"uderzenie": 0.52})
    sekwencja(p, "zachwianie", 30, [
        (0.3, {"Tulow": {"przes": (0, -0.1, -0.6), "obrot": (-6, 10, 0)}, "Klatka": (-18, 12, 4), "Glowa": (-12, -10, 0),
               "RekaL1": (10, 0, 44), "RekaP1": (20, 0, -40), "NogaL1": (24, 0, 0), "NogaL2": (10, 0, 0), "NogaP1": (-10, 0, 0)}),
        (0.62, {"Tulow": {"przes": (0, -0.05, -0.3), "obrot": (3, -4, 0)}, "Klatka": (8, -6, -2), "RekaL1": (0, 0, 16),
                "RekaP1": (6, 0, -14), "NogaL1": (10, 0, 0)})])
    sekwencja(p, "upadek", 50, [
        (0.34, {"Tulow": {"przes": (0, -1.5, 0.2), "obrot": (6, 0, 0)}, "Klatka": (22, 0, 0), "Glowa": (16, 0, 0),
                "NogaL1": (-52, 0, 0), "NogaP1": (-52, 0, 0), "NogaL2": (104, 0, 0), "NogaP2": (104, 0, 0),
                "RekaL1": (-10, 0, 14), "RekaP1": (-10, 0, -14)}),
        (0.5, {"Tulow": {"przes": (0, -1.6, 0.3), "obrot": (14, 0, 0)}, "Klatka": (30, 0, 0), "Glowa": (24, 0, 0),
               "NogaL1": (-56, 0, 0), "NogaP1": (-56, 0, 0), "NogaL2": (108, 0, 0), "NogaP2": (108, 0, 0)}, "liniowo"),
        (0.72, {"Tulow": {"przes": (0, -2.5, 1.8), "obrot": (82, 0, 0)}, "Klatka": (6, 0, 0), "Glowa": (-10, 0, 0),
                "NogaL1": (-20, 0, 0), "NogaP1": (-20, 0, 0), "NogaL2": (30, 0, 0), "NogaP2": (30, 0, 0),
                "RekaL1": (-60, 0, 30), "RekaP1": (-60, 0, -30)}),
        (1.0, {"Tulow": {"przes": (0, -2.6, 1.9), "obrot": (86, 0, 0)}, "Klatka": (4, 0, 0), "Glowa": (-6, 14, 0),
               "NogaL1": (-8, 0, 0), "NogaP1": (-8, 0, 0), "NogaL2": (12, 0, 0), "NogaP2": (12, 0, 0),
               "RekaL1": (-70, 0, 34), "RekaP1": (-70, 0, -34), "RekaL2": (0, 0, 0), "RekaP2": (0, 0, 0)})], {"upadek": 0.72})
    return p
