#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Podgląd Bagna-pasa BEZ Blendera i bez Studio — rysownik brył lasu-pasa (swiat/las_pas/podglad.py) na częściach Bagna.

    python -B swiat/bagno_pas/podglad.py                       # wszystkie kadry → swiat/bagno_pas/podglad/*.jpg
    python -B swiat/bagno_pas/podglad.py --tylko gora,oczka    # wybrane kadry
    python -B swiat/bagno_pas/podglad.py --wyj <folder>        # gdzie indziej (np. robocze)

Kadry: `gora` (rzut z góry całego Bagna, u w górę, v w prawo), `gora_strefy` (to samo z placami walki, pętlami, osią
kładki i otwarciami), trzy ujęcia z ukosa (`oczka`, `trzesawisko`, `kepy_leze`, `topiel_brama`) i dwa z oczu gracza
(`oczy_przybycie`, `oczy_kepy`). Obrazy mają najwyżej 1280 px szerokości. Te same kamery w świecie Studio →
`ujecia_swiat.json` (dla tools/studio_zrzuty.py po budowie).

Z lasu-pasa: wczytywanie brył, cieniowanie, rzut perspektywiczny i z góry, kontury, podpisy (bez zmian). Bagno ma niebo
i mgłę podglądu w kolorach mgły bagna (atrybuty NIEBO_* rysownika ustawiane tylko w tym procesie). W kadrach przy wejściu
widać też koniec lasu-pasa (części lasu od u 860, bez grupy ZapowiedzBagna, która ma zniknąć przed budową Bagna).
TO NIE JEST WYGLĄD Z ROBLOX: brak faktur, cieni rzucanych, poświaty Neonu i mgły z Lighting — tylko kształty, kolory i układ.
"""
import argparse
import json
import math
import os
import sys
import tempfile
import time

import numpy as np
from PIL import Image, ImageDraw

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.las_pas import podglad as rys  # noqa: E402
from swiat.las_pas.kontekst import PLAC_R  # noqa: E402
from swiat.bagno_pas.kontekst import ODCINKI_SCIEZKI, v_sciezki  # noqa: E402

X0, Z0 = rys.X0, rys.Z0
LAS = os.path.join(REPO, "swiat", "las_pas", "czesci.json")
SZER = 1280
# kadry: (kamera [u, wys, v], cel [u, wys, v], kąt widzenia w pionie °, opis)
KADRY = {
    "oczy_przybycie": ((954.0, 5.6, 0.0), (1030.0, 3.0, 0.0), 60.0, "z oczu gracza w miejscu przybycia (Pomost Przybycia)"),
    "oczka": ((992.0, 34.0, -16.0), (1120.0, 0.0, 6.0), 52.0, "Pomost Przybycia, rów z kładką i Rechotne Oczka"),
    "trzesawisko": ((1196.0, 30.0, 14.0), (1330.0, 0.0, -2.0), 52.0, "Kładka nad Topielą i Bulgotne Trzęsawisko"),
    "kepy_leze": ((1430.0, 36.0, -12.0), (1610.0, 0.0, 4.0), 50.0, "trzcinowa przesieka, Kłapiące Kępy i Wrak Łodzi"),
    "oczy_kepy": ((1442.0, 5.6, 1.0), (1520.0, 3.5, 0.0), 60.0, "z oczu gracza za trzcinową przesieką (Kępy)"),
    "topiel_brama": ((1700.0, 30.0, 16.0), (1830.0, 5.0, -2.0), 54.0, "Leże Ropuchy, Latarnie Topieli, Topiel i brama do Dżungli"),
}


def ustaw_niebo():
    """Mglisto-zielone niebo i mgła podglądu (lokalna mgła Bagna); rysownik lasu czyta te atrybuty przy każdym kadrze."""
    rys.NIEBO_GORA = np.array((0.66, 0.74, 0.72))
    rys.NIEBO_DOL = np.array((0.80, 0.84, 0.78))


def sciany_lasu(u_od=860.0):
    """Ściany końca lasu-pasa (dla kadrów przy wejściu) — bez ZapowiedzBagna (do usunięcia przed budową Bagna)."""
    if not os.path.isfile(LAS):
        return []
    with open(LAS, encoding="utf-8") as f:
        d = json.load(f)
    zost = [c for c in d["czesci"] if "/ZapowiedzBagna" not in d["grupy"][c[1]] and c[2] - X0 > u_od]
    d = dict(d, czesci=zost)
    fd, tmp = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(d, f)
        _, sc = rys.wczytaj(tmp)
    finally:
        os.remove(tmp)
    return [(P, n, k, pid + 10 ** 6, neon, grunt, alfa) for P, n, k, pid, neon, grunt, alfa in sc]


def plansza_gory(img, rzut, plan, u0, u1, strefy=False):
    """Rzut z góry na planszy (szer. ≤ 1280): po lewej przegrody, po prawej przejścia, punkty orientacyjne i strefy."""
    ml, mt, mr, mb = 290, 112, 440, 70
    W, H = img.width + ml + mr, img.height + mt + mb
    out = Image.new("RGB", (W, H), (244, 243, 234))
    out.paste(img, (ml, mt))
    d = ImageDraw.Draw(out, "RGBA")
    f1, f2, f3, f4 = rys.czcionka(26, True), rys.czcionka(16), rys.czcionka(16, True), rys.czcionka(14)
    xr = ml + img.width + 14

    def px(u, v):
        x, y = rzut(u, v)
        return x + ml, y + mt
    d.text((16, 10), "Bagno jako wąski pas — rzut z góry z części" + (" · strefy potworów" if strefy else ""), fill=(40, 34, 30), font=f1)
    d.text((16, 48), "swiat/bagno_pas/czesci.json · u w górę (u góry brama do Dżungli), v w prawo · PROPOZYCJA, nic nie jest "
                     "zbudowane", fill=(110, 84, 60), font=f2)
    d.text((16, 72), "rysunek własny w Pillow z brył części — to NIE jest wygląd z Roblox (bez faktur, cieni i świateł)",
           fill=(150, 60, 40), font=f2)
    for q in plan["przegrody"]:
        _, y1 = px(q["u_od"], -90)
        _, y2 = px(q["u_do"], -90)
        d.line((ml - 10, y1, ml, y1), fill=(60, 50, 40, 255), width=2)
        d.line((ml - 10, y2, ml, y2), fill=(60, 50, 40, 255), width=2)
        d.text((12, (y1 + y2) / 2 - 20), q["nazwa"], fill=(40, 34, 30), font=f3)
        d.text((12, (y1 + y2) / 2), "u %d–%d" % (q["u_od"], q["u_do"]), fill=(110, 84, 60), font=f4)
    _, yb = px(934, -90)
    d.text((12, yb - 18), "brama lasu (u 934)", fill=(110, 84, 60), font=f4)
    et = []
    for t_ in plan["przejscia"]:
        et.append(((t_["u_od"] + t_["u_do"]) / 2.0, t_["nazwa"], "otwarcie %d st" % (t_["otwarcie"][1] - t_["otwarcie"][0]), (40, 90, 170)))
    for z_ in plan["punkty_orientacyjne"]:
        if z_["id"].endswith("_prawa"):
            continue
        et.append((z_["u"], z_["nazwa"].replace(" (lewa)", ""), "wys. %d" % z_["wys"], (90, 70, 40)))
    if strefy:
        for st in plan["strefy"]:
            p = st["poziomy"]
            et.append((st["srodek"][0], "%s · %s (%s)" % (st["id"], st["potwor"], st["klasa"]),
                       "poz. %s · %d/%d naraz" % ("%d" % p[0] if p[0] == p[1] else "%d–%d" % tuple(p), st["naraz"], st["max"]),
                       (170, 40, 40)))
        s_ = plan["straznik"]
        et.append((s_["miejsce"][0], s_["potwor"], "poz. %d" % s_["poziom"], (170, 40, 40)))
    et.sort(key=lambda e: -e[0])
    ostatni = -1e9
    for u, n1, n2, kol in et:
        _, yu = px(u, 0)
        y = max(yu - 18, ostatni + 38)
        ostatni = y
        d.line((ml + img.width, yu, xr - 4, y + 11), fill=kol + (160,), width=1)
        d.text((xr, y), n1, fill=kol, font=f3)
        d.text((xr, y + 18), n2, fill=(110, 84, 60), font=f4)
    if strefy:
        sk = img.width / 180.0
        rr = PLAC_R * sk
        for st in plan["strefy"]:
            tr = st["trasa"] + [st["trasa"][0]]
            d.line([px(u, v) for u, v in tr], fill=(255, 210, 40, 230), width=2)
            for u, v in st["trasa"]:
                x, y = px(u, v)
                d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=(230, 40, 40, 200), width=2)
            for u, v in st["dom"]["pts"]:
                x, y = px(u, v)
                d.rectangle((x - 4, y - 4, x + 4, y + 4), fill=(170, 60, 230, 255))
        x, y = px(*plan["straznik"]["miejsce"])
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=(230, 40, 40, 220), width=3)
        for t_ in plan["przejscia"]:
            a_ = px(t_["u_do"], t_["otwarcie"][0])
            b_ = px(t_["u_od"], t_["otwarcie"][1])
            d.rectangle((a_[0], a_[1], b_[0], b_[1]), outline=(40, 140, 255, 230), width=2)
        for a_, b_ in ODCINKI_SCIEZKI:
            d.line([px(u, v_sciezki(u)) for u in np.arange(a_, b_ + 0.1, 4.0)], fill=(255, 255, 255, 170), width=1)
        for m in plan["miejsca"]:
            x, y = px(m["u"], m["v"])
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 60, 60, 255) if m["id"] == "przybycie" else (60, 200, 255, 255))
        d.text((ml, H - mb + 8), "czerwone koła: place walki r 12 · żółte: pętle · fiolet: domy potworów", fill=(60, 50, 40), font=f4)
        d.text((ml, H - mb + 28), "niebieskie ramki: otwarcia przejść · biała kreska: oś kładki · kropki: miejsca (czerwona = "
                                  "przybycie)", fill=(60, 50, 40), font=f4)
    return out


def zapisz_ujecia(plik):
    wyn = []
    for nazwa, (kam, cel, fov, _) in KADRY.items():
        ogn = round(12.0 / math.tan(math.radians(fov) / 2.0), 1)
        wyn.append([nazwa, [X0 + kam[0], kam[1], Z0 + kam[2]], [X0 + cel[0], cel[1], Z0 + cel[2]], ogn, None])
    with open(plik, "w", encoding="utf-8", newline="\n") as f:
        f.write("[\n" + ",\n".join(" " + json.dumps(u, ensure_ascii=False) for u in wyn) + "\n]\n")


def main():
    ap = argparse.ArgumentParser(description="Podgląd Bagna-pasa w Pillow (bez Blendera)")
    ap.add_argument("--json", default=os.path.join(TU, "czesci.json"))
    ap.add_argument("--wyj", default=os.path.join(TU, "podglad"))
    ap.add_argument("--tylko", default="")
    ap.add_argument("--skala-gory", type=float, default=3.0)
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(a.wyj, exist_ok=True)
    ustaw_niebo()
    t0 = time.time()
    d, sciany = rys.wczytaj(a.json)
    las = sciany_lasu()
    with open(os.path.join(TU, "plan_bagna.json"), encoding="utf-8") as f:
        plan = json.load(f)
    tylko = set(x for x in a.tylko.split(",") if x)
    print("PODGLĄD: %d części Bagna, %d ścian (+ %d ścian końca lasu-pasa) (%.1f s)" % (len(d["czesci"]), len(sciany), len(las),
                                                                                     time.time() - t0))
    if not tylko or tylko & {"gora", "gora_strefy"}:
        u0, u1 = 926.0, 1910.0
        img, rzut = rys.kadr_gora(sciany + [x for x in las if x[0][:, 0].max() - X0 > u0], a.skala_gory, u0=u0, u1=u1)
        for nazwa, strefy in (("gora", False), ("gora_strefy", True)):
            if not tylko or nazwa in tylko:
                plansza_gory(img, rzut, plan, u0, u1, strefy).save(os.path.join(a.wyj, nazwa + ".jpg"), quality=86)
        print("  gora (%.1f s)" % (time.time() - t0))
    H = int(SZER * 0.625)
    for nazwa, (kam, cel, fov, opis) in KADRY.items():
        if tylko and nazwa not in tylko:
            continue
        t1 = time.time()
        sc = sciany + las if kam[0] < 1150 else sciany
        img = rys.kadr_perspektywa(sc, (X0 + kam[0], kam[1], Z0 + kam[2]), (X0 + cel[0], cel[1], Z0 + cel[2]), fov, SZER, H, mgla=330.0)
        rys.podpis(img, opis, "kamera u %g, wys. %g, v %g → u %g · rysunek własny w Pillow, to NIE jest wygląd z Roblox"
                   % (kam[0], kam[1], kam[2], cel[0])).save(os.path.join(a.wyj, nazwa + ".jpg"), quality=86)
        print("  %s (%.1f s)" % (nazwa, time.time() - t1))
    zapisz_ujecia(os.path.join(TU, "ujecia_swiat.json"))
    print("GOTOWE w %.0f s → %s (+ swiat/bagno_pas/ujecia_swiat.json)" % (time.time() - t0, os.path.relpath(a.wyj, REPO).replace(os.sep, "/")))


if __name__ == "__main__":
    main()
