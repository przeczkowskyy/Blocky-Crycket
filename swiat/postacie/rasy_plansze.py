#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plansze ras: porównanie modelu z rzutem Pawła i plansza skali (opis ras: swiat/postacie/RASY.md).

    # z głównego folderu repozytorium; Blender 5.0 pod wspólną blokadą (jedna instancja naraz), Pillow
    python -B swiat/postacie/rasy_plansze.py elf ork                 # do swiat/postacie/wynik/rasa_<id>/
    python -B swiat/postacie/rasy_plansze.py elf --wyj <folder>      # próba do folderu poza repozytorium

Powstają (przebuduj.py woła to samo przez po_przebudowie() modułu rasy, zaraz po ułożeniu wynik/rasa_<id>/):
  rasa_<id>_porownanie.jpg  u góry rzut (przód, 3/4, bok, tył), pod spodem te same cztery widoki modelu w jednej
                            skali; model stoi w pozie A (ręce 10° od ciała) — tylko w tym renderze
  rasa_<id>_skala.jpg       manekin R15 | człowiek (goły Rycerz) | rasa pomnożona przez skalę z danych rasy
Widoki renderuje rasy_plansze_blender.py (kwadratowe rendery ortogonalne o stałej skali), plansze składa Pillow.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.biblioteka.podglad import blender_exe, zajmij_blender, zwolnij_blender  # noqa: E402
from swiat.postacie import rasy  # noqa: E402
from swiat.postacie.biblioteka.postac import manekin_r15, pakiet, zapisz_json  # noqa: E402

SKRYPT = os.path.join(TU, "rasy_plansze_blender.py")
WYNIK = os.path.join(TU, "wynik")
# widoki jak na rzutach: przód, 3/4 (twarz ku prawej stronie obrazu), bok (profil w prawo), tył
WIDOKI = (("przod", (0.0, 0.0, 1.0), 5.0), ("trzy_czwarte", (-0.75, 0.1, 1.0), 5.0),
          ("bok", (-1.0, 0.0, 0.0), 3.2), ("tyl", (0.0, 0.0, -1.0), 5.0))        # (nazwa, kierunek, szerokość kadru)
POZA_A = {"LeftUpperArm": (0, 0, 10), "RightUpperArm": (0, 0, -10)}              # ręce lekko od ciała, jak na rzutach
WYS_POROWNANIE = (-0.4, 6.7)             # zakres wysokości kadru (studs): stopy … czubek koka orka
WYS_SKALA = (-0.3, 7.3)
SZER_PLANSZY = 2000                      # px; plansza porównawcza
TLO, TEKST, TEKST2 = "#1d1729", "#ffffff", "#d9d0ee"


def log(*a):
    print("RASY |", *a, flush=True)


def _czcionki():
    from PIL import ImageFont
    try:
        return (ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 34),
                ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 22))
    except OSError:
        f = ImageFont.load_default()
        return f, f


def renderuj_widoki(modele, zadania, robocze):
    """Jedno uruchomienie Blendera (pod wspólną blokadą): modele -> PNG widoków w folderze roboczym."""
    os.makedirs(robocze, exist_ok=True)
    plik_pak = os.path.join(robocze, "pakiet_rasy.json")
    zapisz_json(pakiet(modele), plik_pak)
    plik_zad = os.path.join(robocze, "zadania_rasy.json")
    with open(plik_zad, "w", encoding="utf-8") as f:
        json.dump({"pakiet": plik_pak, "wyj": robocze, "probki": 16, "modele": zadania}, f)
    polecenie = [blender_exe(), "-b", "--factory-startup", "--python-exit-code", "1", "--python", SKRYPT, "--",
                 plik_zad]
    blokada = zajmij_blender()
    try:
        r = subprocess.run(polecenie, capture_output=True, timeout=20 * 60,
                           creationflags=0x08000000 if os.name == "nt" else 0)
    finally:
        zwolnij_blender(blokada)
    if r.returncode != 0:
        tekst = (r.stdout + r.stderr).decode("utf-8", "replace")
        print("\n".join(tekst.splitlines()[-30:]))
        raise SystemExit("rasy_plansze: Blender zakończył się błędem (kod %d)" % r.returncode)


def _wytnij(sciezka, szer_studow, px_na_stud, wys_px):
    """Środkowy pas kwadratowego renderu o szerokości szer_studow, przeskalowany do wys_px wysokości."""
    from PIL import Image
    im = Image.open(sciezka).convert("RGB")
    skala = wys_px / im.height
    im = im.resize((round(im.width * skala), wys_px), Image.LANCZOS)
    w = round(szer_studow * px_na_stud)
    x0 = (im.width - w) // 2
    return im.crop((x0, 0, x0 + w, wys_px))


def plansza_porownawcza(rasa, robocze, cel):
    """Rzut (góra) + cztery widoki modelu (dół) -> cel (JPG)."""
    from PIL import Image, ImageDraw
    r = rasy.RASY[rasa]
    rid = rasy.id_rasy(rasa)
    fb, fn = _czcionki()
    W = SZER_PLANSZY
    rzut = Image.open(os.path.join(REPO, r["rzut"])).convert("RGB")
    rzut = rzut.resize((W, round(rzut.height * W / rzut.width)), Image.LANCZOS)
    zakres = WYS_POROWNANIE[1] - WYS_POROWNANIE[0]
    px = W / sum(s for _, _, s in WIDOKI)                         # pikseli na stud w wierszu modelu
    wys = round(zakres * px)
    N1, N2, N3 = 64, 44, 44                                       # paski: tytuł, podpis rzutu, podpis modelu
    im = Image.new("RGB", (W, N1 + N2 + rzut.height + N3 + wys), TLO)
    dr = ImageDraw.Draw(im)
    dr.text((18, 12), "%s — rzut i model 3D (propozycja, pilotaż D-104)" % r["nazwa"], font=fb, fill=TEKST)
    dr.text((18, N1 + 8), "Rzut Pawła: %s — przód, 3/4, bok, tył" % r["rzut"], font=fn, fill=TEKST2)
    im.paste(rzut, (0, N1 + N2))
    y = N1 + N2 + rzut.height
    dr.text((18, y + 8), "Model: klocki ciała „czlowiek” (jak goły Rycerz), strój bazowy; poza A tylko w tym renderze; "
            "skala rasy %s — plansza %s_skala.jpg" % (("%.2f" % r["skala"]).replace(".", ","), rid),
            font=fn, fill=TEKST2)
    x = 0
    for nazwa, _, szer in WIDOKI:
        kadr = _wytnij(os.path.join(robocze, "%s_%s.png" % (rid, nazwa)), szer, px, wys)
        im.paste(kadr, (round(x), y + N3))
        x += szer * px
    im.save(cel, quality=88)
    return cel


def plansza_skali(rasa, robocze, cel):
    """Manekin R15 | człowiek (goły Rycerz) | rasa × skala — przód, jedna skala, wspólna linia stóp -> cel (JPG)."""
    from PIL import Image, ImageDraw
    r = rasy.RASY[rasa]
    rid = rasy.id_rasy(rasa)
    fb, fn = _czcionki()
    zakres = WYS_SKALA[1] - WYS_SKALA[0]
    px, szer = 86.0, 5.4
    wys = round(zakres * px)
    wzrost = 5.3                                                  # czubek głowy ciała „czlowiek” (bez włosów)
    kolumny = (("skala_manekin", "Manekin R15 biblioteki", 5.25, None),
               ("skala_czlowiek", "Człowiek (goły Rycerz) × 1,00", wzrost, None),
               (rid + "_w_skali", "%s × %s" % (r["nazwa"], ("%.2f" % r["skala"]).replace(".", ",")),
                wzrost * r["skala"], r["skala"]))
    K = round(szer * px)
    N1, N2 = 64, 78
    im = Image.new("RGB", (K * len(kolumny), N1 + wys + N2), TLO)
    dr = ImageDraw.Draw(im)
    dr.text((18, 12), "%s — skala rasy (dana rasy, niewypieczona w klocki)" % r["nazwa"], font=fb, fill=TEKST)
    ziemia = N1 + round(WYS_SKALA[1] * px)                        # y pikseli linii stóp
    for i, (mid, podpis, h, _) in enumerate(kolumny):
        kadr = _wytnij(os.path.join(robocze, "%s_przod.png" % mid), szer, px, wys)
        im.paste(kadr, (i * K, N1))
    for i, (mid, podpis, h, _) in enumerate(kolumny):
        yh = ziemia - round(h * px)
        dr.line((i * K + 8, yh, (i + 1) * K - 8, yh), fill="#ffffff", width=2)       # czubek głowy (bez włosów)
        t = "%s" % podpis
        dr.text((i * K + (K - dr.textlength(t, font=fn)) // 2, N1 + wys + 8), t, font=fn, fill=TEKST)
        t = "wzrost %s studa (czubek głowy, bez włosów)" % ("%.2f" % h).replace(".", ",")
        dr.text((i * K + (K - dr.textlength(t, font=fn)) // 2, N1 + wys + 40), t, font=fn, fill=TEKST2)
    im.save(cel, quality=88)
    return cel


def plansze(rasa, cel_folder, robocze=None):
    """Rendery i obie plansze rasy do cel_folder. Zwraca nazwy powstałych plików."""
    if rasa not in rasy.RASY:
        raise SystemExit("Nieznana rasa %r (są: %s)" % (rasa, ", ".join(rasy.RASY)))
    from swiat.postacie import rycerz
    rid = rasy.id_rasy(rasa)
    sprzataj = robocze is None
    robocze = robocze or tempfile.mkdtemp(prefix="rasy_plansze_%s_" % rasa)
    m = rasy.model(rasa)
    czlowiek = rycerz.cialo()
    czlowiek.id = "skala_czlowiek"
    modele = [m, rasy.w_skali(m), czlowiek, manekin_r15("skala_manekin", "Manekin skali", klipy=False)]
    zakres_p = WYS_POROWNANIE[1] - WYS_POROWNANIE[0]
    px_p = SZER_PLANSZY / sum(s for _, _, s in WIDOKI)
    przod = [["przod", [0.0, 0.0, 1.0]]]
    skala = {"widoki": przod, "wys": list(WYS_SKALA), "rozmiar": 700, "obrys": True}
    zadania = {rid: {"widoki": [[n, list(k)] for n, k, _ in WIDOKI], "wys": list(WYS_POROWNANIE),
                     "rozmiar": int(round(zakres_p * px_p * 1.5)), "poza": {k: list(v) for k, v in POZA_A.items()},
                     "obrys": True},
               rid + "_w_skali": skala, "skala_czlowiek": skala, "skala_manekin": skala}
    renderuj_widoki(modele, zadania, robocze)
    os.makedirs(cel_folder, exist_ok=True)
    pliki = [rid + "_porownanie.jpg", rid + "_skala.jpg"]
    plansza_porownawcza(rasa, robocze, os.path.join(cel_folder, pliki[0]))
    plansza_skali(rasa, robocze, os.path.join(cel_folder, pliki[1]))
    for p in pliki:
        log("gotowe", os.path.join(cel_folder, p))
    if sprzataj:
        shutil.rmtree(robocze, ignore_errors=True)
    return pliki


def po_przebudowie(rasa, cel):
    """Haczyk przebuduj.py (moduł rasy: po_przebudowie(cel)): plansze do świeżo ułożonego wynik/rasa_<id>/."""
    return plansze(rasa, cel)


def main():
    ap = argparse.ArgumentParser(description="Plansze ras: porównanie z rzutem i plansza skali")
    ap.add_argument("rasy", nargs="+", help="rasy z modułem rasa_<id>.py, np. elf ork")
    ap.add_argument("--wyj", default="", help="folder wyników (domyślnie swiat/postacie/wynik/rasa_<id>/)")
    ap.add_argument("--robocze", default="", help="folder roboczy na rendery widoków (domyślnie tymczasowy)")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    for rasa in a.rasy:
        rasa = rasa[5:] if rasa.startswith("rasa_") else rasa
        plansze(rasa, a.wyj or os.path.join(WYNIK, rasy.id_rasy(rasa)),
                os.path.join(a.robocze, rasa) if a.robocze else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
