# -*- coding: utf-8 -*-
"""KOTY RAS WEDŁUG RZUTÓW — sześć kotów w stroju podstawowym zbudowanych według arkuszy obrotowych Pawła z 26.11
(assets/raw/RasyKoty/obroty_podstawowe/: czlowiek, polbog, goblin, mroczny_elf, elf, ork). Status: propozycja, PRÓBA —
nie są w grze.

Wzór: zaakceptowany Kot-Demon (kot_demon.wg_rzutow). Ta sama bryła bazowa (głowa-sześcian 1,7 × 1,5 × 1,5, koszulka
w serek, spodenki), ten sam szkielet i te same klipy Kota-Maga Karola (KM._postac + kopia klipów postaci odniesienia)
— plik kot_mag.py bez zmian. Rasę robią cechy widoczne w sylwetce: włosy, kształt uszu, ogon, znaki, aureola, kły.
Zasada Pawła: jedna para uszu (kocie uszy w kształcie rasy; dodatkowe uszy elfa na rzucie to błąd generatora).

    python -B swiat/postacie/koty_wg_rzutow.py --kontrola        # sprawdzian biblioteki (bez Blendera)
"""
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(TU)))

from swiat.postacie import kot_demon as KD  # noqa: E402

KM = KD.KM
W, H, D = 1.7, 1.5, 1.5                     # głowa jak u demona
KREM = "EFE3C2"

# ------------------------------------------------------------------------------------------------ dane ras
KOTY = {
    "czlowiek": dict(
        nazwa="Kot-Człowiek", futro="F28A2E", prega="D9601C", mordka="FFD9A6", ucho="E88A78", nos="F5879F",
        koszulka=KREM, spodenki="2F6FD6", pregi=("czolo", "czubek", "tyl", "bok"), wasy=2, pregi_rak=True,
        mordka_rozmiar=(1.36, 0.72), rumieniec="F08F8F", uszy="kot", ogon="kot", ogon_koniec="FFD9A6", ogon_pregi=True,
        oczy=dict(okragle=True, obrys=(0.36, 0.44), blyski=((-0.05, 0.1, 0.11, 0.12), (0.06, -0.1, 0.05, 0.06)))),
    "polbog": dict(
        nazwa="Kot-Półbóg", futro="F2C230", prega="D9A21E", mordka="FFE58A", ucho="C98A4A", nos="C9825A",
        koszulka="F4F1EA", spodenki="D4A72C", pregi=("czolo", "czubek", "tyl", "policzek"), wasy=3,
        mordka_rozmiar=(1.1, 0.6), uszy="kot", ogon="kot", ogon_koniec="FFE58A", aureola=True,
        oczy=dict(okragle=True, obrys=(0.46, 0.5), teczowka=(0.38, 0.42, "1CCFEA", "poswiata"),
                  blyski=((-0.07, 0.04, 0.07, 0.2),))),
    "goblin": dict(
        nazwa="Kot-Goblin", futro="8FD32A", prega="5FA82A", mordka="C8E85A", ucho="3F7F1E", nos="7FBF2A",
        koszulka=KREM, spodenki="B35A10", pregi=(), wasy=3, wasy_krzywe=True, mordka_rozmiar=(1.4, 0.66),
        rumieniec="B98A5E", uszy="goblin", ogon="zygzak", wlosy="2F6B1E", laty=True,
        oczy=dict(okragle=True, x=0.44, y=0.14, obrys=(0.52, 0.52), teczowka=(0.42, 0.42, "FFD21A", "swiecacy"),
                  zrenica=(0.05, 0.26, "tusz", 0.0, 0.0), blyski=((-0.1, 0.1, 0.07, 0.08),),
                  skala={1: 0.78, -1: 1.08},
                  brew=dict(w=0.56, h=0.17, kolor="2F6B1E", kat=20, dy=0.33, x=0.42, z=0.06, gr=0.07))),
    "mroczny_elf": dict(
        nazwa="Kot-Mroczny elf", futro="4A4466", prega="2E2A44", mordka="8F84B8", ucho="5A3A6E", nos="2A2638",
        koszulka=KREM, spodenki="3A3566", lapy="2A2638", uszy_kolor="2A2638", pregi=(), wasy=3, wasy_kolor="CFCBE0",
        mordka_rozmiar=(1.0, 0.56), uszy="mroczny", ogon="bicz", wlosy="F1EEF7", wlosy_cien="D5CFE6",
        poduszka="8F84B8",
        oczy=dict(obrys=(0.46, 0.3), teczowka=(0.38, 0.2, "A050FF", "poswiata"),
                  zrenica=(0.05, 0.16, "5A2A9A", 0.02, -0.01), blyski=((-0.08, 0.03, 0.05, 0.05),), powieka=19)),
    "elf": dict(
        nazwa="Kot-Elf", futro="F6D2A6", prega="E0B483", mordka="FFE9CF", ucho="F5A3A8", nos="F5879F",
        koszulka=KREM, spodenki="2F8F4E", pregi=(), wasy=3, mordka_rozmiar=(1.0, 0.56), uszy="wysokie",
        ogon="kita", wlosy="F2C94C", wlosy_cien="D9A92E",
        # Paweł 26.11: oczy elfki łagodniejsze — bez czarnej obwódki, cienka brązowa rzęsa, jasna cienka brew
        oczy=dict(okragle=True, bez_obrysu=True, obrys=(0.38, 0.35), teczowka=(0.38, 0.35, "3FBF5A", "polysk"),
                  zrenica=(0.11, 0.18, "tusz", 0.0, -0.01), blyski=((-0.07, 0.06, 0.07, 0.08),), rzesa=2,
                  rzesa_kolor="7A5230", rzesa_gr=0.03,
                  brew=dict(w=0.3, h=0.035, kolor="D9A92E", kat=-5, dy=0.31, x=0.43, z=0.006, gr=0.02))),
    "ork": dict(
        nazwa="Kot-Ork", futro="6A8A34", prega="46611F", mordka="8FA850", ucho="4E6427", nos="D98A8A",
        koszulka=KREM, spodenki="7A4E2C", pregi=("czolo", "czubek", "policzek"), wasy=2, mordka_rozmiar=(1.2, 0.62),
        uszy="kot", ogon="kot", ogon_pregi=True, kok=True, kly=True, pas=True,
        oczy=dict(y=0.1, obrys=(0.42, 0.28), teczowka=(0.34, 0.2, "ECE7CC", "polysk"),
                  zrenica=(0.12, 0.16, "tusz", 0.03, -0.01),
                  brew=dict(w=0.58, h=0.2, kolor="46611F", kat=17, dy=0.2, x=0.42, z=0.06, gr=0.08))),
}
KOLEJNOSC = ("czlowiek", "polbog", "goblin", "mroczny_elf", "elf", "ork")


def id_kota(rasa):
    return "kot_%s_wg_rzutow" % rasa


# ------------------------------------------------------------------------------------------------ cegiełki
def _krazek(p, nazwa, pos, dx, dy, kolor, mat="matowy", gr=0.04):
    """Płaski krążek / elipsa na przedniej ścianie głowy (oś do przodu)."""
    p.walec(nazwa, pos, (dx, gr, dy), kolor, mat, rot=(90, 0, 0), faza=0.0, segm=12)


def _oko(p, zn, s, yc, zf, o, futro):
    sk = o.get("skala", {}).get(zn, 1.0)
    x, y = zn * o.get("x", 0.43), yc + o.get("y", 0.12)
    ow, oh = o["obrys"][0] * sk, o["obrys"][1] * sk
    okr = o.get("okragle")
    if o.get("bez_obrysu"):                                  # delikatne oko: sama tęczówka, bez czarnej obwódki
        pass
    elif okr:
        _krazek(p, "Oko obrys " + s, (x, y, zf + 0.012), ow, oh, "tusz", "polysk", 0.05)
    else:
        p.blok("Oko obrys " + s, (x, y, zf + 0.01), (ow, oh, 0.05), "tusz", "polysk", faza=0.04)
    t = o.get("teczowka")
    if t:
        if okr:
            _krazek(p, "Oko " + s, (x, y, zf + 0.03), t[0] * sk, t[1] * sk, t[2], t[3], 0.03)
        else:
            p.blok("Oko " + s, (x, y - 0.01, zf + 0.03), (t[0] * sk, t[1] * sk, 0.03), t[2], t[3], faza=0.0)
    z = o.get("zrenica")
    if z:
        p.blok("Zrenica " + s, (x - zn * z[3] * sk, y + z[4] * sk, zf + 0.047), (z[0] * sk, z[1] * sk, 0.02), z[2],
               "polysk", faza=0.0)
    for i, (dx, dy, bw, bh) in enumerate(o.get("blyski", ())):
        p.blok("Blysk %s%d" % (s, i), (x + dx * sk, y + dy * sk, zf + 0.058), (bw * sk, bh * sk, 0.02), "bialy",
               faza=0.0)
    if o.get("powieka") is not None:                         # skośna powieka jak u demona
        kat = o["powieka"]
        p.blok("Powieka " + s, (x, y + oh / 2 + 0.02, zf + 0.05), (ow + 0.1, 0.2, 0.05), futro, rot=(0, 0, zn * kat),
               faza=0.0)
        p.blok("Powieka kreska " + s, (x, y + oh / 2 - 0.075, zf + 0.055), (ow + 0.08, 0.06, 0.05), "tusz",
               rot=(0, 0, zn * kat), faza=0.0)
    b = o.get("brew")
    if b:
        p.blok("Brew " + s, (zn * b.get("x", 0.45), y + b["dy"] * sk, zf + b.get("z", 0.01)),
               (b["w"] * sk, b["h"], b.get("gr", 0.03)), b["kolor"], "matowy", rot=(0, 0, zn * b["kat"]), faza=0.0)
    if o.get("rzesa"):                                       # górna kreska oka z wywiniętą rzęsą
        rk, rg = o.get("rzesa_kolor", "tusz"), o.get("rzesa_gr", 0.06)
        p.blok("Rzesa " + s, (x + zn * 0.04, y + oh / 2 - 0.02, zf + 0.056), (ow + 0.12, rg, 0.03), rk,
               rot=(0, 0, zn * o["rzesa"]), faza=0.0)
        p.blok("Rzesa koniec " + s, (x + zn * (ow / 2 + 0.1), y + oh / 2 + 0.03, zf + 0.056), (0.12, rg * 0.75, 0.03),
               rk, rot=(0, 0, zn * 35), faza=0.0)


def _glowa(p, k):
    F, PR = k["futro"], k["prega"]
    w0, h0, d0 = p.wymiary("Head")
    yc = -h0 / 2 + H / 2
    gora, zf = yc + H / 2, D / 2
    pr = k.get("pregi", ())
    with p.na("Head", od="srodek"):
        p.blok("Glowa", (0, yc, 0), (W, H, D), F, faza=0.14)
        for i, (x, dl) in enumerate(((0.0, 0.36), (-0.27, 0.27), (0.27, 0.27))):
            if "czolo" in pr:
                p.ostroslup("Prega czolo %d" % i, (x, gora - dl / 2 - 0.04, zf + 0.005), (0.15, dl, 0.03), PR,
                            "matowy", rot=(0, 0, 180 + x * 30), gora=(0.02, 0.03), faza=0.0)
            if "czubek" in pr:
                p.blok("Prega czubek %d" % i, (x, gora + 0.005, 0), (0.15, 0.03, D - 0.34), PR, "matowy", faza=0.0)
            if "tyl" in pr:
                p.ostroslup("Prega tyl %d" % i, (x, gora - dl / 2 - 0.04, -zf - 0.005), (0.15, dl + 0.1, 0.03), PR,
                            "matowy", rot=(0, 0, 180), gora=(0.02, 0.03), faza=0.0)
        mw, mh = k["mordka_rozmiar"]
        _krazek(p, "Mordka", (0, yc - H / 2 + mh / 2 + 0.01, zf + 0.008), mw, mh, k["mordka"])
        for zn, s in ((1, "L"), (-1, "P")):
            if "bok" in pr:
                for i, (y, dl) in enumerate(((0.16, 0.5), (-0.1, 0.62), (-0.36, 0.42))):
                    p.ostroslup("Prega bok %s%d" % (s, i), (zn * (W / 2 + 0.005), yc + y, -zf + 0.1 + dl / 2),
                                (0.03, dl, 0.14), PR, "matowy", rot=(90, 0, 0), gora=(0.03, 0.02), faza=0.0)
            if "policzek" in pr:
                for i, y in enumerate((-0.02, -0.22)):
                    p.ostroslup("Prega policzek %s%d" % (s, i), (zn * (W / 2 - 0.15), yc + y, zf + 0.005),
                                (0.1, 0.26, 0.03), PR, "matowy", rot=(0, 0, zn * 90), gora=(0.02, 0.03), faza=0.0)
            _oko(p, zn, s, yc, zf, k["oczy"], F)
            if k.get("rumieniec"):
                _krazek(p, "Rumieniec " + s, (zn * 0.62, yc - 0.2, zf + 0.014), 0.26, 0.13, k["rumieniec"])
            n = k.get("wasy", 3)
            uklad = ((-0.18, 11), (-0.3, 0), (-0.42, -11)) if n == 3 else ((-0.22, 6), (-0.36, -8))
            for i, (dy, kat) in enumerate(uklad):
                kolor = k.get("wasy_kolor", "tusz")
                if k.get("wasy_krzywe"):                     # goblin: łamane wąsy z dwóch odcinków
                    p.blok("Was %s%da" % (s, i), (zn * 0.86, yc + dy, zf + 0.02), (0.24, 0.02, 0.02), kolor, "matowy",
                           rot=(0, 0, zn * (kat + 22)), faza=0.0)
                    p.blok("Was %s%db" % (s, i), (zn * 1.06, yc + dy + 0.02, zf + 0.02), (0.22, 0.02, 0.02), kolor,
                           "matowy", rot=(0, 0, zn * (kat - 24)), faza=0.0)
                else:
                    p.blok("Was %s%d" % (s, i), (zn * 0.93, yc + dy, zf + 0.02), (0.48, 0.02, 0.02), kolor, "matowy",
                           rot=(0, 0, zn * kat), faza=0.0)
    return yc, gora, zf


def _pyszczek(p, k, yc, zf):
    """Nos i kocie usta „w” (rasy z własnym pyskiem dokładają swoje w cechach)."""
    with p.na("Head", od="srodek"):
        p.ostroslup("Nos", (0, yc - 0.15, zf + 0.045), (0.21, 0.13, 0.05), k["nos"], "polysk", rot=(0, 0, 180),
                    gora=(0.03, 0.03), faza=0.0)
        p.blok("Usta pion", (0, yc - 0.26, zf + 0.04), (0.03, 0.1, 0.03), "tusz", faza=0.0)
        for zn in (1, -1):
            p.blok("Usta a", (zn * 0.065, yc - 0.335, zf + 0.04), (0.14, 0.035, 0.03), "tusz", rot=(0, 0, -zn * 28),
                   faza=0.0)
            p.blok("Usta b", (zn * 0.185, yc - 0.335, zf + 0.04), (0.14, 0.035, 0.03), "tusz", rot=(0, 0, zn * 28),
                   faza=0.0)


def _uszy(p, k):
    F = k.get("uszy_kolor", k["futro"])
    rodzaj = k["uszy"]
    for zn, s, kosc in ((1, "L", "LeftEar"), (-1, "P", "RightEar")):
        if rodzaj == "kot":
            with p.na(kosc, obrot=(0, 0, -zn * 24)):
                p.ostroslup("Ucho " + s, (zn * 0.06, 0.42, -0.12), (0.7, 0.76, 0.56), F, gora=(0.08, 0.16),
                            przes_gory=(zn * 0.14, -0.04))
                p.ostroslup("Ucho srodek " + s, (zn * 0.07, 0.38, 0.17), (0.46, 0.54, 0.03), k["ucho"], "matowy",
                            gora=(0.04, 0.02), przes_gory=(zn * 0.1, 0), faza=0.0)
        elif rodzaj == "wysokie":                            # elf: wysokie uszy rysia z kępką na czubku
            with p.na(kosc, obrot=(0, 0, -zn * 22)):
                p.ostroslup("Ucho " + s, (zn * 0.05, 0.62, -0.1), (0.66, 1.16, 0.5), F, gora=(0.06, 0.12),
                            przes_gory=(zn * 0.2, -0.04))
                p.ostroslup("Ucho srodek " + s, (zn * 0.07, 0.56, 0.16), (0.42, 0.86, 0.03), k["ucho"], "matowy",
                            gora=(0.03, 0.02), przes_gory=(zn * 0.15, 0), faza=0.0)
                p.ostroslup("Ucho kepka " + s, (zn * 0.27, 1.3, -0.14), (0.14, 0.3, 0.12), k["wlosy_cien"], "matowy",
                            gora=(0.0, 0.0), przes_gory=(zn * 0.08, 0), faza=0.0)
        elif rodzaj == "mroczny":                            # mroczny elf: długie ostre uszy odchylone na boki
            with p.na(kosc, obrot=(0, 0, -zn * 33)):
                p.ostroslup("Ucho " + s, (zn * 0.04, 0.7, -0.1), (0.66, 1.34, 0.46), F, gora=(0.0, 0.06),
                            przes_gory=(zn * 0.2, -0.08))
                p.ostroslup("Ucho srodek " + s, (zn * 0.06, 0.6, 0.15), (0.42, 0.94, 0.03), k["ucho"], "matowy",
                            gora=(0.0, 0.02), przes_gory=(zn * 0.14, 0), faza=0.0)
        elif rodzaj == "goblin":                             # goblin: ogromne uszy nietoperza na boki
            # Układ ucha: oś Y = długość ucha (od głowy w bok i w górę), +zn·X = dolna krawędź. Ucho składa się
            # z grzbietu (długi klin wzdłuż górnej krawędzi) i trzech płatów błony coraz krótszych ku czubkowi —
            # klinowe przerwy między płatami dają nadgryziony, postrzępiony dolny brzeg jak na rzucie.
            with p.na(kosc, obrot=(0, 0, -zn * 60)):
                for nazwa, sk, z, kolor, mat, gr in (("Ucho", 1.0, -0.06, F, "zwykly", 0.22),
                                                     ("Ucho srodek", 0.74, 0.062, k["ucho"], "matowy", 0.03)):
                    faza = 0.02 if sk == 1.0 else 0.0
                    p.ostroslup("%s grzbiet %s" % (nazwa, s), (-zn * 0.2 * sk, 0.08 + 0.7 * sk, z),
                                (0.46 * sk, 1.4 * sk, gr), kolor, mat, gora=(0.0, gr * 0.3),
                                przes_gory=(-zn * 0.1 * sk, 0), faza=faza)
                    for i, (v, szer, dl) in enumerate(((0.3, 0.58, 0.6), (0.76, 0.42, 0.5), (1.07, 0.28, 0.32))):
                        p.ostroslup("%s plat %s%d" % (nazwa, s, i), (zn * (dl / 2 - 0.06) * sk, 0.08 + v * sk, z),
                                    (szer * sk, dl * sk, gr), kolor, mat, rot=(0, 0, -zn * 90),
                                    gora=(szer * 0.58 * sk, gr * 0.6), przes_gory=(-0.04 * sk, 0), faza=faza)
                if zn == 1:                                  # złote kółko w lewym uchu kota, w końcu środkowego płata
                    p.walec("Kolczyk", (zn * 0.44, 0.76, 0.0), (0.2, 0.06, 0.2), "FFC21A", "metal", rot=(90, 0, 0),
                            faza=0.0, segm=8)


def _tulow_i_konczyny(p, k):
    F, DOL = k["futro"], k.get("lapy", k["futro"])
    with p.na("UpperTorso", od="srodek"):
        w, h, d = p.wymiary("UpperTorso")
        p.blok("Koszulka", (0, 0, 0), (w + 0.12, h + 0.06, d + 0.12), k["koszulka"], "matowy", faza=0.08)
        p.blok("Koszulka rabek", (0, -h / 2 + 0.03, 0), (w + 0.2, 0.14, d + 0.2), k["koszulka"], "matowy", faza=0.05)
        p.ostroslup("Dekolt", (0, h / 2 - 0.1, d / 2 + 0.065), (0.36, 0.26, 0.02), F, "matowy", rot=(0, 0, 180),
                    gora=(0.04, 0.02), faza=0.0)
    with p.na("LowerTorso", od="srodek"):
        w, h, d = p.wymiary("LowerTorso")
        p.blok("Spodenki", (0, 0, 0), (w + 0.08, h + 0.06, d + 0.08), k["spodenki"], "matowy", faza=0.06)
        if k.get("pas"):
            p.blok("Pas", (0, h / 2, 0), (w + 0.16, 0.14, d + 0.16), "5A361C", "matowy", faza=0.03)
            p.blok("Klamra", (0, h / 2, d / 2 + 0.09), (0.24, 0.18, 0.04), "C9CED8", "metal", faza=0.02)
            p.blok("Klamra srodek", (0, h / 2, d / 2 + 0.105), (0.12, 0.08, 0.03), "5A361C", "matowy", faza=0.0)
    for s, zn in (("Left", 1), ("Right", -1)):
        with p.na(s + "UpperLeg"):
            p.blok("Nogawka", (0, -0.13, 0), (0.58, 0.32, 0.6), k["spodenki"], "matowy", faza=0.05)
        with p.na(s + "LowerLeg", od="srodek"):
            p.blok("Lydka", (0, 0, 0), (0.42, 0.3, 0.42), DOL, faza=0.05)
            if k.get("laty"):
                p.blok("Lata lydka", (zn * 0.21, 0.0, 0.05), (0.03, 0.14, 0.18), k["prega"], "matowy", faza=0.0)
        with p.na(s + "Foot", od="srodek"):
            w, h, d = p.wymiary(s + "Foot")
            p.blok("Lapa", (0, 0, 0.04), (w, h, d), DOL, faza=0.06)
            p.blok("Lapa przod", (0, -0.01, d / 2 + 0.12), (w, h - 0.02, 0.3), DOL, faza=0.06)
            for i, x in enumerate((-0.09, 0.09)):
                p.blok("Palec kreska %d" % i, (x, 0.0, d / 2 + 0.262), (0.025, 0.11, 0.03), k["prega"], "matowy",
                       faza=0.0)
        with p.na(s + "UpperArm", od="srodek"):
            w, h, d = p.wymiary(s + "UpperArm")
            p.blok("Futro ramie", (0, 0, 0), (w, h, d), F)
            p.blok("Rekaw", (0, h * 0.12, 0), (w + 0.16, h * 0.78, d + 0.16), k["koszulka"], "matowy", faza=0.05)
        with p.na(s + "LowerArm", od="srodek"):
            w, h, d = p.wymiary(s + "LowerArm")
            p.blok("Futro przedramie", (0, 0, 0), (w, h, d), DOL if k.get("lapy") else F)
            if k.get("pregi_rak"):
                for i, y in enumerate((0.08, -0.06)):
                    p.blok("Prega reka %d" % i, (zn * 0.12, y, 0), (w * 0.5 + 0.03, 0.05, d + 0.03), k["prega"],
                           "matowy", faza=0.0)
            if k.get("laty"):
                p.blok("Lata reka", (zn * (w / 2 + 0.005), 0.02, 0.02), (0.03, 0.16, 0.2), k["prega"], "matowy",
                       faza=0.0)
        with p.na(s + "Hand"):
            p.blok("Lapka", (0, -0.19, 0), (0.42, 0.34, 0.42), DOL, faza=0.08)
            for i, x in enumerate((-0.07, 0.07)):
                p.blok("Palec kreska %d" % i, (x, -0.3, 0.2), (0.025, 0.1, 0.03), k["prega"], "matowy", faza=0.0)
            pod = k.get("poduszka", "F29AAA")
            p.blok("Poduszka", (0, -0.27, -0.205), (0.17, 0.1, 0.02), pod, "matowy", faza=0.0)
            for i, x in enumerate((-0.1, 0.0, 0.1)):
                p.blok("Poduszka palec %d" % i, (x, -0.16, -0.205), (0.06, 0.06, 0.02), pod, "matowy", faza=0.0)


def _ogon(p, k):
    """Ogon na kościach Tail i TailTip Kota-Maga (układy jak w kot_mag._golas)."""
    F, PR, rodzaj = k["futro"], k["prega"], k["ogon"]
    gr = {"kot": 0.26, "kita": 0.3, "bicz": 0.13, "zygzak": 0.16}[rodzaj]
    with p.na("LowerTorso", od="srodek"):
        sr = p.staw("LowerTorso")[1] + p.srodek("LowerTorso")[1]
        p.blok("Ogon u nasady", (0.1, 0.5 - sr, -0.5), (gr, 0.62, gr), F, faza=0.04)
    with p.na("Tail", obrot=(0, -50, 0)):
        p.blok("Ogon nasada", (0, -0.06, -0.47), (gr, gr, 1.02), F, faza=0.04)
        if k.get("ogon_pregi"):
            p.blok("Ogon pasek", (0, -0.06, -0.62), (gr + 0.04, gr + 0.04, 0.08), PR, "matowy", faza=0.02)
    with p.na("TailTip", obrot=(0, -50, -18)):
        if rodzaj == "kot":
            p.blok("Ogon srodek", (0, 0.4, 0), (gr, 1.04, gr), F, faza=0.06)
            p.blok("Ogon koncowka", (0, 0.98, 0), (gr + 0.02, 0.3, gr + 0.02), k.get("ogon_koniec", F), faza=0.08)
            if k.get("ogon_pregi"):
                for i, y in enumerate((0.15, 0.42, 0.69)):
                    p.blok("Ogon pasek %d" % i, (0, y, 0), (gr + 0.04, 0.08, gr + 0.04), PR, "matowy", faza=0.02)
        elif rodzaj == "kita":                               # elf: puszysta kita z zielonym czubkiem-liściem
            p.kula("Kita", (0, 0.52, 0), (0.7, 1.3, 0.66), F)
            p.ostroslup("Kita czubek", (0, 1.16, 0), (0.52, 0.56, 0.5), "4CC35A", gora=(0.06, 0.06), faza=0.03)
            p.ostroslup("Kita zabek", (0.2, 0.92, 0), (0.2, 0.3, 0.3), "4CC35A", rot=(0, 0, 155), gora=(0.0, 0.05),
                        faza=0.0)
            p.ostroslup("Kita zabek 2", (-0.2, 0.92, 0), (0.2, 0.3, 0.3), "4CC35A", rot=(0, 0, -155), gora=(0.0, 0.05),
                        faza=0.0)
        elif rodzaj == "bicz":                               # mroczny elf: cienki ogon z fioletowym płomykiem
            p.blok("Ogon srodek", (0, 0.24, 0), (gr, 0.7, gr), F, faza=0.04)
            p.ostroslup("Plomyk", (0, 0.92, 0), (0.4, 0.72, 0.22), "A66BFF", "poswiata", gora=(0.0, 0.04),
                        przes_gory=(0.08, 0), faza=0.0)
            p.ostroslup("Plomyk srodek", (0, 0.82, 0.0), (0.22, 0.44, 0.26), "F1EEF7", "swiecacy", gora=(0.0, 0.04),
                        faza=0.0)
            for i, zn in enumerate((1, -1)):
                p.ostroslup("Plomyk jezyk %d" % i, (zn * 0.2, 0.84, 0), (0.18, 0.4, 0.16), "A66BFF", "poswiata",
                            rot=(0, 0, -zn * 24), gora=(0.0, 0.03), faza=0.0)
        else:                                                # goblin: złamany ogon z kępką
            p.blok("Ogon a", (0.08, 0.1, 0), (gr, 0.5, gr), F, rot=(0, 0, -28), faza=0.04)
            p.blok("Ogon b", (0.08, 0.5, 0), (gr, 0.52, gr), F, rot=(0, 0, 34), faza=0.04)
            p.blok("Ogon c", (0.04, 0.86, 0), (gr, 0.4, gr), F, rot=(0, 0, -22), faza=0.04)
            for i, (x, kat) in enumerate(((0.12, 0), (0.3, -32), (-0.06, 30))):
                p.ostroslup("Ogon kepka %d" % i, (x, 1.2, 0), (0.24, 0.42, 0.2), k["wlosy"], "matowy",
                            rot=(0, 0, kat), gora=(0.0, 0.04), faza=0.0)


# ------------------------------------------------------------------------------------------------ cechy ras
def _cechy_czlowiek(p, k, yc, gora, zf):
    _pyszczek(p, k, yc, zf)


def _cechy_polbog(p, k, yc, gora, zf):
    _pyszczek(p, k, yc, zf)
    with p.na("Head", od="srodek"):                          # aureola: pierścień nad głową, wyżej niż czubki uszu
        r, n = 0.66, 14
        for i in range(n):
            a = 2 * math.pi * i / n
            p.blok("Aureola %d" % i, (r * math.cos(a), gora + 1.02 - 0.32 * r * math.sin(a), r * math.sin(a)), (0.33, 0.08, 0.1), "FFD54A",
                   "swiecacy", rot=(0, -math.degrees(a) + 90, 0), faza=0.0)


def _cechy_goblin(p, k, yc, gora, zf):
    F, CIEMNY, WL = k["futro"], k["prega"], k["wlosy"]
    with p.na("Head", od="srodek"):
        # haczykowaty nos z brodawką
        p.blok("Nos nasada", (0, yc + 0.06, zf + 0.07), (0.2, 0.34, 0.14), k["nos"], "matowy", rot=(-25, 0, 0),
               faza=0.03)
        p.blok("Nos garb", (0, yc - 0.13, zf + 0.19), (0.3, 0.28, 0.24), k["nos"], "matowy", rot=(-40, 0, 0), faza=0.05)
        p.ostroslup("Nos czubek", (0, yc - 0.33, zf + 0.26), (0.28, 0.3, 0.22), k["nos"], "matowy", rot=(160, 0, 0),
                    gora=(0.1, 0.08), faza=0.03)
        p.kula("Brodawka", (0.09, yc - 0.1, zf + 0.33), (0.08, 0.08, 0.08), CIEMNY)
        # szeroki krzywy uśmiech pełen zębów, jeden złoty
        y = yc - 0.53
        p.blok("Zeby", (0, y, zf + 0.03), (0.98, 0.17, 0.03), "FFF8E8", "polysk", rot=(0, 0, 5), faza=0.0)
        p.blok("Usmiech gora", (0, y + 0.095, zf + 0.04), (1.06, 0.045, 0.04), "tusz", rot=(0, 0, 5), faza=0.0)
        p.blok("Usmiech dol", (0, y - 0.095, zf + 0.04), (0.9, 0.045, 0.04), "tusz", rot=(0, 0, 5), faza=0.0)
        for i, x in enumerate((-0.33, -0.17, 0.0, 0.16)):
            p.ostroslup("Zab przerwa %d" % i, (x, y + 0.03 + x * 0.09, zf + 0.047), (0.1, 0.11, 0.02), "tusz",
                        rot=(0, 0, 180 if i % 2 else 0), gora=(0.0, 0.02), faza=0.0)
        p.blok("Zab zloty", (0.33, y + 0.03, zf + 0.05), (0.12, 0.15, 0.03), "FFC21A", "metal", rot=(0, 0, 5),
               faza=0.0)
        for zn in (1, -1):
            p.blok("Kacik", (zn * 0.56, y + 0.12 + zn * 0.05, zf + 0.04), (0.14, 0.045, 0.04), "tusz",
                   rot=(0, 0, zn * 42), faza=0.0)
        # blizna przez mniejsze (lewe) oko
        p.blok("Blizna", (0.47, yc + 0.2, zf + 0.085), (0.04, 0.56, 0.02), "8A4A2A", "matowy", rot=(0, 0, -12),
               faza=0.0)
        # irokez: grzebień kolców od czoła przez czubek po kark
        p.blok("Irokez pas", (0, gora + 0.03, -0.02), (0.34, 0.1, D - 0.1), WL, "matowy", faza=0.03)
        for i, (z, wys, kat) in enumerate(((0.58, 0.5, 24), (0.3, 0.66, 8), (0.0, 0.7, -6), (-0.3, 0.6, -20),
                                           (-0.58, 0.46, -36))):
            p.ostroslup("Irokez %d" % i, (0, gora + wys / 2 + 0.02, z), (0.32, wys, 0.36), WL, "matowy",
                        rot=(kat, 0, 0), gora=(0.0, 0.05), faza=0.0)
        p.ostroslup("Irokez czolo", (0, gora - 0.12, zf + 0.012), (0.34, 0.3, 0.04), WL, "matowy", rot=(0, 0, 180),
                    gora=(0.0, 0.03), faza=0.0)
        p.ostroslup("Irokez tyl", (0, yc + 0.02, -zf - 0.03), (0.42, H - 0.1, 0.08), WL, "matowy", rot=(0, 0, 180),
                    gora=(0.06, 0.05), faza=0.0)
        # łaty i plamki
        for i, (x, y, r) in enumerate(((-0.56, 0.56, 0.24), (0.58, 0.5, 0.16), (-0.7, -0.46, 0.14))):
            _krazek(p, "Lata przod %d" % i, (x, yc + y, zf + 0.006), r, r, CIEMNY)
        for zn, s in ((1, "L"), (-1, "P")):
            for i, (y, z, r) in enumerate(((0.3, -0.3, 0.4), (-0.35, -0.1, 0.5), (0.1, 0.35, 0.18))):
                p.walec("Lata bok %s%d" % (s, i), (zn * (W / 2 + 0.006), yc + y, z), (r, 0.03, r * 1.2), CIEMNY,
                        "matowy", rot=(0, 0, 90), faza=0.0, segm=10)
        for i, (x, y, r) in enumerate(((-0.45, 0.2, 0.36), (0.5, -0.35, 0.3), (0.42, 0.45, 0.16))):
            _krazek(p, "Lata tyl %d" % i, (x, yc + y, -zf - 0.006), r, r * 0.85, CIEMNY)


def _wlosy_boki_tyl(p, k, yc, gora, zf, dl_tyl):
    """Wspólne dla elfów (Paweł 26.11: włosy nie jak hełm, bryła głowy nie może z nich wystawać, grzywka ma łączyć
    się z resztą). Czapa obejmuje cały czubek głowy razem z narożnikami i styka się z grzywką; na niej zaokrąglona
    kopuła. Bok: pasmo od skroni schodzące skosem do tyłu (łączy grzywkę z włosami za uchem), pełna płyta na tylnej
    połowie boku i kosmyk pod nią. Tył: płyta zakrywa całą tylną ścianę głowy, na niej zaokrąglona bryła i długie
    zwężające się pasmo. Policzki i czoło zostają odsłonięte."""
    WL = k["wlosy"]
    p.blok("Wlosy czapa", (0, gora, -0.01), (W + 0.14, 0.26, D + 0.12), WL, "matowy", faza=0.1)
    p.kula("Wlosy kopula", (0, gora + 0.1, -0.03), (W + 0.02, 0.54, D), WL, "matowy", segm=10)
    for zn, s in ((1, "L"), (-1, "P")):
        x = zn * (W / 2 + 0.04)
        p.ostroslup("Wlosy skron " + s, (x, gora - 0.5, 0.4), (0.12, 1.0, 0.74), WL, "matowy", rot=(0, 0, 180),
                    gora=(0.08, 0.1), przes_gory=(0, -0.3), faza=0.02)
        p.blok("Wlosy bok " + s, (x, yc - 0.03, -0.34), (0.12, H + 0.1, D * 0.56), WL, "matowy", faza=0.03)
        p.ostroslup("Wlosy bok kosmyk " + s, (x, yc - H / 2 - 0.3, -0.36), (0.12, 0.5, D * 0.5), WL, "matowy",
                    rot=(0, 0, 180), gora=(0.06, 0.1), faza=0.02)
    # tył (Paweł 26.11: bez „bulwy” i bez lewitującej dolnej części): płyta zakrywa tylną ścianę głowy, a na niej
    # pięć pasm biegnie jednym ciągiem od czubka głowy aż do końców włosów — środkowe najdłuższe i najgrubsze,
    # każde zwęża się ku dołowi, więc dół włosów jest postrzępiony, a nie ucięty
    p.blok("Wlosy tyl plyta", (0, yc - 0.03, -zf - 0.04), (W + 0.12, H + 0.1, 0.14), WL, "matowy", faza=0.04)
    CI = k.get("wlosy_cien", WL)
    for i, (x, dl, gr) in enumerate(((-0.68, 0.82, 0.16), (-0.34, 0.94, 0.22), (0.0, 1.0, 0.26), (0.34, 0.94, 0.22),
                                     (0.68, 0.82, 0.16))):
        dl = dl * (dl_tyl + 0.1)
        p.ostroslup("Wlosy tyl pasmo %d" % i, (x, gora + 0.02 - dl / 2, -zf - 0.05 - gr / 2), (0.44, dl, gr),
                    CI if i % 2 else WL, "matowy", rot=(0, 0, 180), gora=(0.13, 0.07), faza=0.02)


def _cechy_elf(p, k, yc, gora, zf):
    _pyszczek(p, k, yc, zf)
    WL, CI = k["wlosy"], k["wlosy_cien"]
    with p.na("Head", od="srodek"):
        _wlosy_boki_tyl(p, k, yc, gora, zf, 2.6)
        for zn, s in ((1, "L"), (-1, "P")):
            # włosy zaczesane od przedziałka na boki, kosmyk przy skroni i warkocz na ramieniu
            # linia włosów w odwrócone „V”: trójkąt od przedziałka na środku czoła do skroni (czoło odsłonięte)
            p.ostroslup("Grzywka " + s, (zn * 0.44, gora - 0.25, zf + 0.005), (0.52, 0.9, 0.11), WL, "matowy",
                        rot=(0, 0, zn * 90), gora=(0.04, 0.09), przes_gory=(zn * 0.24, 0), faza=0.0)
            p.ostroslup("Kosmyk " + s, (zn * (W / 2 - 0.03), gora - 1.0, zf - 0.03), (0.2, 1.0, 0.18), WL, "matowy",
                        rot=(0, 0, 180), gora=(0.07, 0.07), faza=0.03)
            for i in range(5):
                p.blok("Warkocz %s%d" % (s, i), (zn * 0.74, yc - 0.86 - i * 0.17, zf - 0.08),
                       (0.2 - 0.01 * i, 0.19, 0.2 - 0.01 * i), CI if i % 2 else WL, "matowy", rot=(0, 45, 0),
                       faza=0.03)
            p.blok("Warkocz wiazanie " + s, (zn * 0.74, yc - 1.72, zf - 0.08), (0.18, 0.06, 0.18), "2F8F4E", "matowy",
                   faza=0.0)
            p.ostroslup("Warkocz koniec " + s, (zn * 0.74, yc - 1.86, zf - 0.08), (0.18, 0.22, 0.18), WL, "matowy",
                        rot=(0, 0, 180), gora=(0.03, 0.03), faza=0.0)
            # złoty ornament na policzku
            _krazek(p, "Ornament " + s, (zn * 0.66, yc - 0.12, zf + 0.006), 0.16, 0.16, "E8B93A")
            _krazek(p, "Ornament srodek " + s, (zn * 0.66, yc - 0.12, zf + 0.012), 0.08, 0.08, k["futro"])
        # świecący liść na czole
        p.ostroslup("Lisc gora", (0, yc + 0.5, zf + 0.012), (0.17, 0.17, 0.03), "3FD06A", "poswiata", gora=(0.0, 0.03),
                    faza=0.0)
        p.ostroslup("Lisc dol", (0, yc + 0.37, zf + 0.012), (0.17, 0.1, 0.03), "3FD06A", "poswiata", rot=(0, 0, 180),
                    gora=(0.0, 0.03), faza=0.0)


def _cechy_mroczny_elf(p, k, yc, gora, zf):
    _pyszczek(p, k, yc, zf)
    WL, CI, RUNA = k["wlosy"], k["wlosy_cien"], "B56BFF"
    with p.na("Head", od="srodek"):
        _wlosy_boki_tyl(p, k, yc, gora, zf, 1.9)
        for zn, s in ((1, "L"), (-1, "P")):
            # grzywka opadająca na boki czoła (środek odsłonięty — widać półksiężyc) i długie pasma przy twarzy
            # postrzępiona grzywka z trzech szpiczastych kosmyków (coraz dłuższych ku skroni, końce na zewnątrz)
            for i, (x, dl, szer, kat) in enumerate(((0.28, 0.5, 0.34, 12), (0.56, 0.66, 0.34, 18), (0.82, 1.0, 0.3, 4))):
                p.ostroslup("Grzywka %s%d" % (s, i), (zn * x, gora + 0.1 - dl / 2, zf + 0.02 + 0.012 * i),
                            (szer, dl, 0.1), CI if i == 1 else WL, "matowy", rot=(0, 0, 180 + zn * kat),
                            gora=(0.03, 0.04), faza=0.0)
            # długie szpiczaste pasmo przy twarzy, do piersi
            p.ostroslup("Pasmo " + s, (zn * (W / 2 + 0.06), gora - 0.95, zf - 0.14), (0.26, 1.3, 0.24), WL, "matowy",
                        rot=(0, 0, 180 + zn * 9), gora=(0.05, 0.05), faza=0.03)
            # dwie świecące kreski pazura pod okiem
            for i, (dx, dl) in enumerate(((0.0, 0.3), (0.13, 0.22))):
                p.blok("Pazur %s%d" % (s, i), (zn * (0.5 + dx), yc - 0.2 - dx * 0.3, zf + 0.012), (0.05, dl, 0.02),
                       RUNA, "poswiata", rot=(0, 0, -zn * 26), faza=0.0)
            p.ostroslup("Kiel " + s, (zn * 0.15, yc - 0.42, zf + 0.05), (0.07, 0.11, 0.03), "FFFFFF", "polysk",
                        rot=(0, 0, 180), gora=(0.0, 0.03), faza=0.0)
        # półksiężyc na czole: krążek z wycięciem w kolorze futra
        _krazek(p, "Ksiezyc", (0, yc + 0.47, zf + 0.008), 0.3, 0.3, RUNA, "poswiata", 0.03)
        _krazek(p, "Ksiezyc wyciecie", (0.07, yc + 0.49, zf + 0.014), 0.22, 0.22, k["futro"], "matowy", 0.03)
        # wysoki kucyk: węzeł na czubku, łuk do tyłu i długi ogon włosów do pasa
        p.kula("Kucyk wezel", (0, gora + 0.3, -0.3), (0.56, 0.5, 0.56), WL)
        p.blok("Kucyk luk", (0, gora + 0.2, -zf - 0.1), (0.46, 0.4, 0.5), WL, "matowy", faza=0.08)
        p.ostroslup("Kucyk", (0, gora - 0.95, -zf - 0.32), (0.62, 2.3, 0.34), WL, "matowy", rot=(0, 0, 180),
                    gora=(0.14, 0.1), faza=0.04)
        p.blok("Kucyk cien", (0.1, gora - 0.8, -zf - 0.5), (0.06, 1.5, 0.02), CI, "matowy", faza=0.0)
    for s, zn in (("Left", 1), ("Right", -1)):               # runy na przedramionach, od zewnątrz
        with p.na(s + "LowerArm", od="srodek"):
            w, h, d = p.wymiary(s + "LowerArm")
            for i, (y, z, dl) in enumerate(((0.1, 0.0, 0.14), (-0.02, 0.05, 0.1), (-0.12, -0.03, 0.14))):
                p.blok("Runa %d" % i, (zn * (w / 2 + 0.006), y, z), (0.02, 0.07, dl), RUNA, "poswiata", faza=0.0)


def _cechy_ork(p, k, yc, gora, zf):
    with p.na("Head", od="srodek"):
        p.ostroslup("Nos", (0, yc - 0.15, zf + 0.045), (0.24, 0.14, 0.05), k["nos"], "polysk", rot=(0, 0, 180),
                    gora=(0.05, 0.03), faza=0.0)
        # ponura kreska ust z opadającymi kącikami i dwa kły z dolnej szczęki
        p.blok("Usta", (0, yc - 0.4, zf + 0.04), (0.34, 0.04, 0.03), "tusz", faza=0.0)
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Kacik " + s, (zn * 0.21, yc - 0.43, zf + 0.04), (0.12, 0.04, 0.03), "tusz", rot=(0, 0, -zn * 35),
                   faza=0.0)
            p.ostroslup("Kiel " + s, (zn * 0.33, yc - 0.44, zf + 0.07), (0.13, 0.26, 0.1), "FFF8E8", "polysk",
                        gora=(0.0, 0.0), faza=0.0)
            p.blok("Blizna " + s, (zn * 0.66, yc + (0.42 if zn == 1 else -0.3), zf + 0.006), (0.16, 0.03, 0.02),
                   "8FA850", "matowy", rot=(0, 0, zn * 30), faza=0.0)
        # czarny kok przewiązany sznurkiem
        p.blok("Kok nasada", (0, gora + 0.05, -0.1), (0.46, 0.12, 0.46), "1E1A17", "matowy", faza=0.03)
        p.blok("Sznurek", (0, gora + 0.14, -0.1), (0.34, 0.08, 0.34), "8A5A2C", "matowy", faza=0.0)
        p.kula("Kok", (0, gora + 0.4, -0.12), (0.52, 0.5, 0.52), "1E1A17")


CECHY = {"czlowiek": _cechy_czlowiek, "polbog": _cechy_polbog, "goblin": _cechy_goblin,
         "mroczny_elf": _cechy_mroczny_elf, "elf": _cechy_elf, "ork": _cechy_ork}


def zbuduj_kota(rasa):
    """Kot rasy w stroju podstawowym według rzutu — szkielet i klipy Kota-Maga, bryły według arkusza."""
    k = KOTY[rasa]
    p = KM._postac(id_kota(rasa), k["nazwa"] + " (według rzutów 26.11)")
    p.typ_ciala = KM.CIALO_TYP
    yc, gora, zf = _glowa(p, k)
    _uszy(p, k)
    _tulow_i_konczyny(p, k)
    _ogon(p, k)
    CECHY[rasa](p, k, yc, gora, zf)
    for c in p.czesci:
        c["golas"] = True
    return klipy_ruchu(KM.kopiuj_klipy(KM.postac_odniesienia(), p))


def klipy_ruchu(p):
    """Trzy klipy ruchu po świecie, których Kot-Mag nie ma (Paweł 26.11: kot rasy ma biegać po świecie; u Karola
    bieg bohatera liczy kod pakietu „Bohater w świecie”, nie klip). Własne klipy tych modeli — kot_mag.py bez zmian.
    Poza bazowa Kota-Maga zostaje (prawa łapa niesie broń przed sobą), więc broń klasy stoi w łapce jak kostur.
      bieg      pętla 0,4 s: długi krok, wysokie kolana, tułów pochylony, lewa łapa pracuje, ogon i uszy w rytmie
      skok      pętla: nogi podkurczone, lewa łapa w górze, ogon wyprostowany do góry (lot w górę)
      spadanie  pętla: nogi w rozkroku do lądowania, łapy rozłożone, ogon i uszy trzepoczą"""
    B = KM.BAZA
    k = p.klip("bieg", 12, petla=True)
    k.poza(0, B)
    k.cykl("LeftUpperLeg", "obrot", (38, 0, 0))
    k.cykl("RightUpperLeg", "obrot", (38, 0, 0), faza=0.5)
    k.cykl("LeftLowerLeg", "obrot", (28, 0, 0), faza=0.25, srodek=(32, 0, 0))
    k.cykl("RightLowerLeg", "obrot", (28, 0, 0), faza=0.75, srodek=(32, 0, 0))
    k.cykl("LeftFoot", "obrot", (-18, 0, 0), faza=0.1)
    k.cykl("RightFoot", "obrot", (-18, 0, 0), faza=0.6)
    k.cykl("LowerTorso", "przes", (0, 0.09, 0), czestosc=2, srodek=(0, 0.05, 0))
    k.cykl("LowerTorso", "obrot", (0, 9, 4))
    k.cykl("UpperTorso", "obrot", (0, -12, -3))
    k.cykl("UpperTorso", "obrot", (3, 0, 0), czestosc=2, faza=0.1, srodek=(13, 0, 0))
    k.cykl("LeftUpperArm", "obrot", (-44, 0, 0), srodek=(-6, 0, 0))
    k.cykl("LeftLowerArm", "obrot", (-14, 0, 0), faza=0.1, srodek=(-34, 0, 0))
    k.cykl("RightUpperArm", "obrot", (-9, 0, 0), faza=0.5)
    k.cykl("Head", "obrot", (3, 0, 0), czestosc=2, faza=0.35, srodek=(-9, 0, 0))
    k.cykl("Head", "obrot", (0, 5, 3), faza=0.5)
    k.cykl("Tail", "obrot", (0, 20, 6), faza=0.2, srodek=(-14, 0, 0))
    k.cykl("TailTip", "obrot", (0, 28, 12), faza=0.05, srodek=(-10, 0, 0))
    for ucho, f in (("LeftEar", 0.0), ("RightEar", 0.08)):
        k.cykl(ucho, "obrot", (7, 0, 0), czestosc=2, faza=f, srodek=(-10, 0, 0))

    k = p.klip("skok", 16, petla=True)
    k.poza(0, dict(B, LeftUpperLeg=(48, 0, 0), RightUpperLeg=(22, 0, 0), LeftLowerLeg=(62, 0, 0),
                   RightLowerLeg=(38, 0, 0), LeftFoot=(-20, 0, 0), RightFoot=(-12, 0, 0), UpperTorso=(-6, 0, 0),
                   Head=(-8, 0, 0), LeftUpperArm=(-150, 0, 14), LeftLowerArm=(-12, 0, 0), Tail=(52, 0, 0),
                   TailTip=(24, 0, 0), LeftEar=(12, 0, 0), RightEar=(12, 0, 0)))
    k.cykl("TailTip", "obrot", (0, 8, 4))
    k.cykl("LeftUpperArm", "obrot", (4, 0, 3), faza=0.2)

    k = p.klip("spadanie", 12, petla=True)
    k.poza(0, dict(B, LeftUpperLeg=(18, 0, 14), RightUpperLeg=(18, 0, -14), LeftLowerLeg=(20, 0, 0),
                   RightLowerLeg=(20, 0, 0), LeftFoot=(14, 0, 0), RightFoot=(14, 0, 0), UpperTorso=(8, 0, 0),
                   Head=(-12, 0, 0), LeftUpperArm=(-70, 0, 62), LeftLowerArm=(-20, 0, 0), Tail=(-18, 0, 0),
                   TailTip=(-12, 0, 0), LeftEar=(-16, 0, 0), RightEar=(-16, 0, 0)))
    k.cykl("LeftUpperArm", "obrot", (10, 0, 8), czestosc=2)
    k.cykl("Tail", "obrot", (6, 14, 0), czestosc=2)
    k.cykl("TailTip", "obrot", (8, 20, 0), czestosc=2, faza=0.2)
    k.cykl("LeftEar", "obrot", (6, 0, 0), czestosc=2)
    k.cykl("RightEar", "obrot", (6, 0, 0), czestosc=2, faza=0.3)
    return p


def zbuduj():
    return [zbuduj_kota(r) for r in KOLEJNOSC]


if __name__ == "__main__":
    if "--kontrola" in sys.argv:
        for p in zbuduj():
            b, u = p.sprawdz()
            print(p.id, "części:", len(p.czesci), "klipy:", len(p.klipy), "błędy:", len(b), "uwagi:", len(u))
            for x in b[:6]:
                print("  B", x)
