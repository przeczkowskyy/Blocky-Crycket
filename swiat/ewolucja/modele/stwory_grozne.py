# -*- coding: utf-8 -*-
"""KNIGHT GOLEM, wersja groźna — NOWE id golem_grozny_<stopień> (pliki golem_<stopień>_* z wersji 1 zostają bez zmian).

Te same stawy, zaczepy i klipy co stwory.golem(); inna bryła: przygarbiony, szerokie naramienniki ponad głową, mały hełm
z rogami i dwojgiem skośnych świecących oczu, piec w piersi za kratą, wielki zębaty miecz z żarem w zbroczu, pancerz
z łusek na plecach. Stopień = paleta (STOPNIE_GOLEMA) + rosnące dodatki (kolce, tarcza od 3, kolce pleców od 4, peleryna 5).
"""
from swiat.ewolucja.modele.smok_model import Smok, _mix
from swiat.ewolucja.modele.stwory import STOPNIE_GOLEMA, golem


def golem_grozny(stopien=1, skala=1.7):
    T = STOPNIE_GOLEMA[stopien]
    pal = {k: T[k] for k in ("cialo", "zar", "kolce", "blona")}
    pal.update({"cialo_c": _mix(T["cialo"], "140A1E", 0.5), "cialo_j": _mix(T["cialo"], "FFFFFF", 0.2),
                "zar_c": _mix(T["zar"], "140A1E", 0.3), "zar_j": _mix(T["zar"], "FFFFFF", 0.6),
                "kolce_c": _mix(T["kolce"], "140A1E", 0.3), "blona_c": _mix(T["blona"], "140A1E", 0.3), "mrok": "1A1424"})
    wzor = golem(stopien, skala)
    p = Smok("golem_grozny_%d" % stopien, "Knight Golem %d (groźny)" % stopien, typ="stwor", skala=wzor.skala, faza=0.12,
             paleta=pal)
    for n, k in wzor.kosci.items():                              # ten sam szkielet co w wersji 1
        if n != "Root":
            p.kosc(n, k["rodzic"], k["staw"], czesc=k["czesc"], srodek=k["srodek"])
    r = 0.25 * (stopien - 1)                                     # dodatki rosną ze stopniem
    with p.na("Tulow"):
        p.blok("Biodra", (0, 0, 0), (3.0, 1.3, 1.9), "cialo_c", "matowy", faza=0.16)
        p.blok("Pas zaru", (0, 0.66, 0), (2.7, 0.16, 2.0), "zar_c", "swiecacy", faza=0.0)
        p.blok("Fartuch", (0, -0.9, 0.9), (1.5, 1.6, 0.3), "blona", "matowy", rot=(-8, 0, 0), faza=0.04)
    with p.na("Klatka", obrot=(14, 0, 0)):                       # przygarbienie: klatka pochylona do przodu
        p.blok("Klatka", (0, 1.5, 0.1), (4.8, 2.9, 2.7), "cialo", faza=0.24)
        p.blok("Piec", (0, 1.4, 1.42), (2.0, 1.5, 0.14), "zar_j", "swiecacy", faza=0.0)
        for x in (-0.6, 0.0, 0.6):
            p.blok("Krata pieca", (x, 1.4, 1.5), (0.22, 1.7, 0.16), "mrok", "matowy", faza=0.04)
        p.blok("Zar plecow", (0, 1.5, -1.3), (1.0, 2.6, 0.2), "zar_c", "swiecacy", faza=0.0)
        for i, y in enumerate((2.6, 1.6, 0.6)):
            p.blok("Luska plecow", (0, y, -1.42), (4.4 - 0.5 * i, 0.9, 0.3), "cialo_c", "matowy", rot=(-14, 0, 0), faza=0.06)
        p.blok("Kolnierz", (0, 3.3, -0.9), (2.6, 1.4, 0.5), "cialo_c", "matowy", rot=(-12, 0, 0), faza=0.08)
        for zn in (1, -1):
            p.blok("Naramiennik", (zn * 3.0, 3.1, 0.1), (2.8, 1.3, 3.2), "cialo_c", "matowy", rot=(0, 0, -zn * 16), faza=0.14)
            p.blok("Zar barku", (zn * 2.5, 2.42, 0.1), (1.6, 0.16, 2.6), "zar_c", "swiecacy", rot=(0, 0, -zn * 16), faza=0.0)
            p.klin("Kolec barku", (zn * 3.5, 4.4 + r * 0.5, -0.2), (0.5, 1.8 + r, 1.3), "kolce", "polysk",
                   rot=(0, 180, -zn * 22), faza=0.02)
            if stopien >= 2:
                p.klin("Kolec barku 2", (zn * 2.5, 4.1 + r * 0.4, 0.9), (0.4, 1.2 + r * 0.6, 0.9), "kolce", "polysk",
                       rot=(10, 180, -zn * 8), faza=0.02)
            if stopien >= 4:
                p.klin("Kolec plecow", (zn * 1.2, 3.4, -1.9), (0.4, 1.6 + r, 1.2), "kolce",
                       "swiecacy" if stopien == 5 else "polysk", rot=(-40, 0, -zn * 10), faza=0.02)
            if stopien == 5:
                p.blok("Peleryna", (zn * 1.1, 0.2, -1.8), (2.0, 4.6, 0.14), "blona", "matowy", rot=(-10, 0, zn * 5), faza=0.0)
        p.zaczep("SerceAttachment", "Klatka", (0, 1.4, 1.7))
    with p.na("Glowa", pos=(0, -0.35, 0.5), obrot=(10, 0, 0)):   # mały hełm wsunięty między naramienniki
        p.blok("Helm", (0, 0.6, 0), (1.5, 1.3, 1.6), "cialo_c", "matowy", faza=0.14)
        p.blok("Przylbica", (0, 0.5, 0.84), (1.3, 0.8, 0.1), "mrok", "matowy", faza=0.02)
        for zn in (1, -1):                                       # wizjer: dwoje skośnych świecących oczu
            p.blok("Wizjer", (zn * 0.34, 0.64, 0.9), (0.6, 0.2, 0.08), "zar_j", "swiecacy", rot=(0, 0, zn * 20), faza=0.0)
            p.klin("Rog", (zn * 0.9, 1.5 + r * 0.3, 0.1), (0.36, 1.4 + r, 0.7), "kolce",
                   "swiecacy" if stopien >= 4 else "polysk", rot=(24, 180, -zn * 34), faza=0.02)
        p.klin("Grzebien", (0, 1.6, -0.2), (0.3, 0.9 + r * 0.5, 1.5), "kolce_c", "polysk", rot=(0, 180, 0), faza=0.02)
        p.zaczep("GlowaAttachment", "Glowa", (0, 2.6, 0))
    for s_, zn in (("L", 1), ("P", -1)):
        with p.na("Reka%s1" % s_, pos=(zn * 0.5, 0, 0.2)):
            p.blok("Ramie", (0, -1.0, 0), (1.3, 2.3, 1.4), "cialo", faza=0.14)
        with p.na("Reka%s2" % s_, pos=(zn * 0.5, 0, 0.2)):
            p.blok("Rekawica", (0, -1.0, 0), (1.8, 2.2, 1.8), "cialo_c", "matowy", faza=0.16)
            p.blok("Zar rekawicy", (0, 0.04, 0), (1.5, 0.16, 1.5), "zar_c", "swiecacy", faza=0.0)
            p.blok("Piesc", (0, -2.3, 0), (1.5, 0.8, 1.5), "cialo", faza=0.14)
            if s_ == "P":                                        # wielki zębaty miecz z żarem w zbroczu
                p.blok("Rekojesc", (0, -2.3, 0.6), (0.4, 0.4, 2.4), "mrok", "matowy", faza=0.04)
                p.blok("Jelec", (0, -2.3, 1.6), (2.6, 0.5, 0.5), "kolce_c", "polysk", faza=0.06)
                p.blok("Glownia", (0, -2.3, 4.6), (0.36, 1.5, 5.6), "kolce", "polysk", faza=0.04)
                p.klin("Sztych", (0, -2.3, 8.3), (0.36, 1.5, 1.9), "kolce", "polysk", rot=(0, 180, 90), faza=0.0)
                p.blok("Zar ostrza", (0, -2.3, 4.4), (0.42, 0.3, 5.0), "zar_j", "swiecacy", faza=0.0)
                for z in (3.2, 5.0, 6.8):
                    p.klin("Zab miecza", (0, -1.3, z), (0.36, 0.7, 0.9), "kolce", "polysk", rot=(0, 180, 0), faza=0.0)
                p.zaczep("MieczAttachment", "RekaP2", (0, -2.3, 9.2))
            elif stopien >= 3:                                   # tarcza z kolcem
                p.blok("Tarcza", (1.0, -1.2, 0.3), (0.3, 4.0, 3.2), "blona", "matowy", faza=0.08)
                p.blok("Okucie tarczy", (1.06, -1.2, 0.3), (0.3, 4.3, 0.6), "cialo_c", "matowy", faza=0.04)
                p.klin("Kolec tarczy", (1.5, -1.0, 0.3), (0.7, 1.0, 0.7), "kolce", "polysk", rot=(0, 90, 90), faza=0.0)
                p.blok("Znak tarczy", (1.2, -2.4, 0.3), (0.08, 0.9, 0.9), "zar_j", "swiecacy", rot=(45, 0, 0), faza=0.0)
            else:                                                # szpony
                for z in (-0.4, 0.1, 0.6):
                    p.klin("Szpon", (0.3, -3.0, z), (0.3, 1.1, 0.5), "kolce", "polysk", rot=(180, 90, 0), faza=0.0)
        with p.na("Noga%s1" % s_):
            p.blok("Udo", (0, -0.9, 0), (1.4, 2.0, 1.5), "cialo", faza=0.14)
        with p.na("Noga%s2" % s_):
            p.blok("Nakolannik", (0, 0.1, 0.5), (1.6, 1.0, 1.0), "cialo_c", "matowy", rot=(-14, 0, 0), faza=0.1)
            p.blok("Golen", (0, -0.8, 0), (1.5, 1.7, 1.6), "cialo_c", "matowy", faza=0.14)
            p.blok("Stopa", (0, -1.55, 0.4), (1.7, 0.5, 2.6), "cialo", faza=0.12)
            p.blok("Pazury stopy", (0, -1.62, 1.8), (1.5, 0.36, 0.3), "kolce", "polysk", faza=0.04)
    for k in wzor.klipy:                                         # klipy 1:1 z wersji 1 (te same nazwy stawów)
        nk = p.klip(k.nazwa, k.dlugosc, petla=k.petla)
        nk.kanaly = {klucz: {f: list(v) for f, v in kl.items()} for klucz, kl in k.kanaly.items()}
        nk.zdarzenia = dict(getattr(k, "zdarzenia", {}))
    return p
