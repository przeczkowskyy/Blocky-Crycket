#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Podglądy bazaru BEZ Blendera i BEZ Studio (Pillow + numpy, rysownik.py).

    python -B swiat/miasteczko_bazar/podglad.py                  # wszystkie kadry → swiat/miasteczko_bazar/podglad/*.jpg
    python -B swiat/miasteczko_bazar/podglad.py --tylko plan,u2  # wybrane kadry
    python -B swiat/miasteczko_bazar/podglad.py --wyj <folder>   # kadry gdzie indziej (robocze)

Kadry: `plan` — plansza z góry z przekrojem na wysokości 12 (widać wnętrza, lady i sprzedawców), podpisami po polsku,
izochronami biegu z miejsca startu (co 1 s) i skalą w studach i sekundach; `u1`–`u5` — ujęcia z ukosa (całość, uliczka
sklepów, wnętrze karczmy, plac z portalem i Bramą Twierdzy, zagroda petów z tablicą). Te same kamery trafiają do
ujecia.json w świecie Studio (format tools/studio_zrzuty.py) — do zrzutów w następnym etapie.
TO NIE JEST WYGLĄD Z ROBLOX: bez faktur, cieni rzucanych, poświaty Neonu i oświetlenia miejsca.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.biblioteka.scena import macierz_obrotu  # noqa: E402
from swiat.miasteczko_bazar import rysownik, siatka  # noqa: E402
from swiat.miasteczko_bazar.rysownik import czcionka, naglowek, ramka_napisu  # noqa: E402

# kadry z ukosa: (kamera [x, y, z] bazaru, cel [x, y, z], kąt widzenia w pionie °, tytuł, opis)
KADRY = {
    "u1_calosc": ((-24.0, 165.0, 172.0), (-16.0, 0.0, -6.0), 46.0, "Bazar z lotu ptaka (od południa)",
                  "od placyku studni (z lewej) po Bramę Leśną i Las (z prawej) · pole gry 163 × 72 st · fronty rzędu północnego"),
    "u2_uliczka": ((-9.0, 11.0, 6.0), (60.0, 7.0, -1.0), 62.0, "Uliczka sklepów od placu ku Lasowi",
                   "z lewej sklep magiczny i zbrojownia, z prawej stragan i Wrota lochów, na końcu Brama Leśna"),
    "u3_wnetrze": ((-34.5, 6.4, -11.0), (-31.5, 4.4, -34.0), 66.0, "Wnętrze karczmy (kamera jak za plecami gracza)",
                   "barman za ladą (E → zadania), mistrz gier przy stole z planszą (E → plansza), tablica zleceń"),
    "u4_portal_dzialka": ((44.0, 64.0, 12.0), (-4.0, 4.0, -4.0), 54.0, "Plac startu: portal do krain i Brama Twierdzy",
                          "z prawej (północ) portal do krain z wirem i tablica z rankingiem, z lewej Brama Twierdzy (działka), w środku start"),
    "u5_zagroda_tablica": ((-36.0, 40.0, 48.0), (-24.0, 2.0, -2.0), 60.0, "Zagroda petów i tablica ogłoszeń",
                           "na dole zagroda (opiekunka, pies, slime, smok), wyżej tablica z rankingiem obok startu i portalu"),
}
ETYKIETY = {   # id znacznika → (numer, krótka nazwa, budynek do położenia etykiety, rząd etykiety: z bazaru)
    "start": (1, "Start", None, None),
    "portal_krain": (2, "Portal do krain", "PortalKrain", -54.0),
    "brama_twierdzy": (3, "Działka (Twierdza)", "BramaTwierdzy", 54.0),
    "tablica": (4, "Tablica (ranking)", "Tablica", -44.0),
    "karczma": (5, "Karczma", "Karczma", -54.0),
    "sklep_magiczny": (6, "Sklep magiczny", "SklepMagiczny", -44.0),
    "zbrojownia": (7, "Zbrojownia", "Zbrojownia", -54.0),
    "training_center": (8, "Training Center", "TrainingCenter", -44.0),
    "zagroda_petow": (9, "Zagroda petów", "ZagrodaPetow", 44.0),
    "brama_lochow": (10, "Wrota lochów", "BramaLochow", 44.0),
    "brama_lesna": (11, "Brama Leśna → Las", "BramaLesna", None),
    "studnia_pomnik": (12, "Studnia", "StudniaPomnik", None),
}


def wczytaj():
    with open(os.path.join(TU, "uklad.json"), encoding="utf-8") as f:
        U = json.load(f)
    with open(os.path.join(TU, "czesci.json"), encoding="utf-8") as f:
        D = json.load(f)
    with open(os.path.join(TU, "znaczniki.json"), encoding="utf-8") as f:
        Z = json.load(f)
    return U, D, Z


def z_lasem(D, U, u_maks=110.0):
    """Do podglądu (NIE do czesci.json): dokleja początek pasa Lasu z swiat/las_pas/czesci.json, jeśli plik jest (praca
    innego etapu, tylko odczyt) — żeby było widać, jak bazar styka się z Lasem. Zwraca (dane, czy_doklejono)."""
    plik = os.path.join(REPO, "swiat", "las_pas", "czesci.json")
    if not os.path.exists(plik):
        return D, False
    with open(plik, encoding="utf-8") as f:
        L = json.load(f)
    x_maks = U["swiat"]["las_od_X"] + u_maks
    og, om = len(D["grupy"]), len(D["materialy"])
    czesci = list(D["czesci"])
    for c in L["czesci"]:
        if c[2] <= x_maks:
            c = list(c)
            c[1] += og
            c[12] += om
            czesci.append(c)
    return {"grupy": D["grupy"] + L["grupy"], "materialy": D["materialy"] + L["materialy"], "czesci": czesci}, True


def l1(v):
    return ("%.1f" % v).replace(".", ",")


def ujecie(model, U, nazwa, W=1600, H=1000):
    kam, cel, fov, tytul, opis = KADRY[nazwa]
    X0, Z0 = U["swiat"]["X0"], U["swiat"]["Z0"]
    k = (X0 + kam[0], kam[1], Z0 + kam[2])
    c = (X0 + cel[0], cel[1], Z0 + cel[2])
    img = rysownik.kadr(model, k, c, fov=fov, W=W, H=H, mgla=900.0)
    d = ImageDraw.Draw(img)
    ramka_napisu(d, (W - 14, H - 26), "podgląd z klocków, nie wygląd z Roblox", czcionka(22), kotwica="rm",
                 tlo=(250, 246, 236))
    return naglowek(img, tytul, opis)


def plan(U, D, Z, czasy, S):
    """Plansza z góry: przekrój na wysokości 12, izochrony biegu, numery i podpisy, legenda z czasami, skala."""
    X0, Z0 = U["swiat"]["X0"], U["swiat"]["Z0"]
    gx0, gx1 = U["granice"]["czesci_x"]
    zv0, zv1 = -62.0, 62.0
    W = 1600
    skala = W / (gx1 - gx0)

    def ukryj(c, grupa):
        R = macierz_obrotu(math.degrees(c[5]), math.degrees(c[6]), math.degrees(c[7]))
        hy = (abs(R[1][0]) * c[8] + abs(R[1][1]) * c[9] + abs(R[1][2]) * c[10]) / 2.0
        return c[3] - hy > 12.0 or c[14] in ("Strop", "Belka stropu") or "Girlanda" in c[14] or "Chmura" in c[14]
    model = rysownik.Model(D, pomin=ukryj)
    img, px = rysownik.kadr_gora(model, X0 + gx0, X0 + gx1, Z0 + zv0, Z0 + zv1, skala, tlo=(0.42, 0.62, 0.30))

    def p(x, z):
        return px(X0 + x, Z0 + z)
    d = ImageDraw.Draw(img, "RGBA")
    # izochrony co 1 s (komórki siatki, gdzie zmienia się pełna sekunda)
    T = S.odl / U["bieg_st_s"]
    sek = np.where(np.isfinite(T), np.floor(T), -1)
    gr = np.zeros(sek.shape, dtype=bool)
    gr[:, 1:] |= (sek[:, 1:] != sek[:, :-1]) & (sek[:, 1:] >= 0) & (sek[:, :-1] >= 0)
    gr[1:, :] |= (sek[1:, :] != sek[:-1, :]) & (sek[1:, :] >= 0) & (sek[:-1, :] >= 0)
    for iz, ix in zip(*np.nonzero(gr)):
        x, z = S.punkt(iz, ix)
        a, b = p(x, z)
        d.ellipse((a - 2.2, b - 2.2, a + 2.2, b + 2.2), fill=(255, 255, 255, 235))
    f_s = czcionka(22, True)
    st = U["start"]
    for t in range(1, 6):                                     # podpisy izochron na osi uliczki (na wschód i zachód)
        for kier in (1, -1):
            for xx in np.arange(st["x"], st["x"] + kier * 140, kier * 0.5):
                iz, ix = S.komorka(xx, 7.0)
                if 0 <= ix < S.nx and np.isfinite(T[iz, ix]) and T[iz, ix] >= t:
                    ramka_napisu(d, p(xx, 7.0), "%d s" % t, f_s, tlo=(255, 255, 255), pad=3)
                    break
    # numery i podpisy
    po_id = {z["id"]: z for z in Z["wszystkie"]}
    srodki = {b["id"]: (b["x"], b["z"]) for b in U["budynki"]}
    f_num, f_nap = czcionka(26, True), czcionka(25, True)
    zajete = []
    for zid, (nr, nazwa, bud, rzad) in ETYKIETY.items():
        z = po_id.get(zid)
        if z is None:
            continue
        x, _, zz = z.get("stoisko_bazar", z["bazar"])
        t = czasy.get(zid)
        if rzad is not None:
            bx, bz = srodki.get(zid, (x, zz))
            tekst = "%d %s · %s s" % (nr, nazwa, l1(t)) if t is not None else "%d %s" % (nr, nazwa)
            a, b = p(bx, rzad)
            d.line((p(bx, bz + (8 if rzad < 0 else -8)), (a, b)), fill=(30, 26, 22, 255), width=3)
            box = ramka_napisu(d, (a, b), tekst, f_nap)
            zajete.append(box)
        a, b = p(x, zz)
        d.ellipse((a - 17, b - 17, a + 17, b + 17), fill=(255, 214, 64, 255), outline=(30, 26, 22, 255), width=3)
        d.text((a, b), str(nr), fill=(30, 26, 22), font=f_num, anchor="mm")
    # numery dla brama_lesna i studnia (bez podpisu na mapie — w legendzie)
    for zid, (nr, nazwa) in (("mistrz_gier", (5, "")),):
        z = po_id.get(zid)
        if z:
            a, b = p(z["stoisko_bazar"][0], z["stoisko_bazar"][2])
            d.ellipse((a - 13, b - 13, a + 13, b + 13), fill=(255, 214, 64, 255), outline=(30, 26, 22, 255), width=3)
            d.text((a, b), "5b", fill=(30, 26, 22), font=czcionka(18, True), anchor="mm")
    # pas Lasu za wschodnim brzegiem i strzałka północy
    a, b = p(gx1, zv0)
    ramka_napisu(d, (W - 12, 30), "Las (pas) →", f_nap, kotwica="rm", tlo=(214, 240, 200))
    ramka_napisu(d, (16, 30), "↑ północ (−Z)", czcionka(23, True), kotwica="lm")
    mapa = img
    # legenda pod mapą
    H_leg = 330
    out = Image.new("RGB", (W, mapa.height + H_leg), (250, 246, 236))
    out.paste(mapa, (0, 0))
    d = ImageDraw.Draw(out)
    y0 = mapa.height + 14
    # skala: 0–64 st = 0–4 s
    xs0 = 24
    d.text((xs0, y0), "Skala:", fill=(40, 34, 30), font=czcionka(24, True))
    xs = xs0 + 96
    for i in range(5):
        a = xs + i * 16 * skala
        d.rectangle((a, y0 + 6, a + 16 * skala, y0 + 22), fill=(30, 26, 22) if i % 2 == 0 else (255, 255, 255),
                    outline=(30, 26, 22), width=2) if i < 4 else None
        d.text((a, y0 + 26), "%d st" % (16 * i), fill=(40, 34, 30), font=czcionka(22), anchor="ma")
        d.text((a, y0 + 52), "%d s" % i, fill=(120, 80, 50), font=czcionka(22, True), anchor="ma")
    d.text((xs + 4 * 16 * skala + 40, y0 + 2), "bieg 16 st/s · białe kropki = izochrony co 1 s od startu (1)",
           fill=(40, 34, 30), font=czcionka(22))
    d.text((xs + 4 * 16 * skala + 40, y0 + 34), "czasy = najkrótsza droga do punktu E, z omijaniem przeszkód",
           fill=(40, 34, 30), font=czcionka(22))
    # lista punktów z czasami
    wiersze = [
        "1 Start (punkt pojawienia się)",
        "2 Portal do krain · %s s" % l1(czasy.get("portal_krain", 0)),
        "3 Brama Twierdzy → działka · %s s" % l1(czasy.get("brama_twierdzy", 0)),
        "4 Tablica z rankingiem · %s s" % l1(czasy.get("tablica", 0)),
        "5 Karczma: barman %s s, 5b mistrz gier %s s" % (l1(czasy.get("karczma", 0)), l1(czasy.get("mistrz_gier", 0))),
        "6 Sklep magiczny (mag) · %s s" % l1(czasy.get("sklep_magiczny", 0)),
        "7 Zbrojownia (zbrojmistrz) · %s s" % l1(czasy.get("zbrojownia", 0)),
        "8 Training Center (trener) · %s s" % l1(czasy.get("training_center", 0)),
        "9 Zagroda petów (opiekunka) · %s s" % l1(czasy.get("zagroda_petow", 0)),
        "10 Wrota lochów z kłódką · %s s" % l1(czasy.get("brama_lochow", 0)),
        "11 Brama Leśna → pas Lasu · %s s" % l1(czasy.get("brama_lesna", 0)),
        "12 Studnia-pomnik (ozdoba) · %s s" % l1(czasy.get("studnia_pomnik", 0)),
    ]
    f = czcionka(24)
    for i, w in enumerate(wiersze):
        kol, rz = i // 4, i % 4
        d.text((24 + kol * 530, y0 + 92 + rz * 36), w, fill=(40, 34, 30), font=f)
    d.text((24, y0 + 92 + 4 * 36 + 6), "Kolorowe kreski od startu = ścieżki-kody do wejść (kolor dachu celu). Rzut z góry "
           "przecięty na wysokości 12 st (widać wnętrza, lady i sprzedawców).", fill=(120, 80, 50), font=czcionka(22))
    d.text((24, y0 + 92 + 4 * 36 + 36), "Podgląd z klocków (Pillow) — nie wygląd z Roblox: bez faktur, cieni i świecenia "
           "Neonu.", fill=(120, 80, 50), font=czcionka(22))
    return naglowek(out, "Krzywe Miasteczko jako ciasny bazar — plan",
                    "pole gry 72 st (4,5 s biegu) · wschodni brzeg = początek pasa Lasu (X 1066) · Workspace/MiasteczkoBazar")


def policz_czasy(U, D, Z):
    S = siatka.Siatka(D, U)
    S.z_punktu(U["start"]["x"], U["start"]["z"])
    czasy = {}
    for z in Z["wszystkie"]:
        if "stoisko_bazar" in z:
            x, _, zz = z["stoisko_bazar"]
            czasy[z["id"]] = S.droga_do(x, zz) / U["bieg_st_s"]
    return S, czasy


def zapisz_ujecia(U, plik):
    X0, Z0 = U["swiat"]["X0"], U["swiat"]["Z0"]
    wyn = []
    for nazwa, (kam, cel, fov, _, _) in KADRY.items():
        f = 10.125 / math.tan(math.radians(fov) / 2.0)          # ogniskowa (mm, matryca 36 × 20,25) dla kąta pionowego
        wyn.append([nazwa, [round(X0 + kam[0], 2), kam[1], round(Z0 + kam[2], 2)],
                    [round(X0 + cel[0], 2), cel[1], round(Z0 + cel[2], 2)], round(f, 2), None])
    wyn.append(["plan_gora", [X0 - 20.0, 400.0, Z0 + 0.01], [X0 - 20.0, 0.0, Z0], 35.0, 190.0])
    with open(plik, "w", encoding="utf-8", newline="\n") as f:
        f.write("[\n" + ",\n".join(" " + json.dumps(u, ensure_ascii=False) for u in wyn) + "\n]\n")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Podglądy bazaru (Pillow)")
    ap.add_argument("--wyj", default=os.path.join(TU, "podglad"))
    ap.add_argument("--tylko", default="")
    a = ap.parse_args()
    os.makedirs(a.wyj, exist_ok=True)
    tylko = [t for t in a.tylko.split(",") if t]
    U, D, Z = wczytaj()
    S, czasy = policz_czasy(U, D, Z)
    if not tylko or any(t in "plan" for t in tylko):
        plan(U, D, Z, czasy, S).save(os.path.join(a.wyj, "plan_gora.jpg"), quality=88)
        print("plan_gora.jpg")
    model = None
    DL, z_lasu = z_lasem(D, U)
    for nazwa in KADRY:
        if tylko and not any(t in nazwa for t in tylko):
            continue
        if model is None:
            model = rysownik.Model(DL)
        img = ujecie(model, U, nazwa)
        if z_lasu and nazwa in ("u1_calosc", "u2_uliczka"):
            d = ImageDraw.Draw(img)
            ramka_napisu(d, (14, img.height - 26), "za Bramą Leśną: początek pasa Lasu z swiat/las_pas (inny etap, praca w toku)",
                         czcionka(22), kotwica="lm", tlo=(214, 240, 200))
        img.save(os.path.join(a.wyj, nazwa + ".jpg"), quality=88)
        print(nazwa + ".jpg")
    zapisz_ujecia(U, os.path.join(TU, "ujecia.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
