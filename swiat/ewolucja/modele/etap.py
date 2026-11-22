# -*- coding: utf-8 -*-
"""Etap (staging): zmienione i nowe pliki danych trafiają do dane_nastepne/ pod tymi samymi nazwami — folderu dane/
to polecenie NIE dotyka (agent gry czyta go przy każdej budowie). Sesja główna przenosi pliki między krokami gry.

    python -B swiat/ewolucja/modele/generuj.py etap      # pliki do dane_nastepne/, film biegu nad kratą, podglądy 05 i 26

Runda 5: chód 7 i bieg 18 studs/s w każdym stadium, krótki koziołek (14 klatek) + koziolek_dlugi, poza „portret”,
indeks w wersji 3 (stadia = osiem stadiów, jajo osobno), predkosc dla owcy i golemów, stożek ognia z klipem,
przypalenie ziemi, łagodny wariant pisklęcia (smok_1_lagodny).
"""
import json
import math
import os
import shutil
import subprocess

from swiat.ewolucja.modele import efekty, stwory, stwory_grozne
from swiat.ewolucja.modele import smok_klipy as sk
from swiat.ewolucja.modele import smok_model as sm

LAGODNY = {"oczy": ("dziecko", 0.84), "dodatki": ("skorupka", "rumieniec", "lagodne_brwi")}


def _predkosc_nog(m, klip, dl_nogi, kat):
    """Prędkość bez poślizgu dla prostych nóg-wahadeł: krok 2·L·sin(kąt) w pół cyklu (jednostki projektu na sekundę)."""
    k = next(x for x in m.klipy if x.nazwa == klip)
    k.predkosc = 4.0 * dl_nogi * math.sin(math.radians(kat)) / (k.dlugosc / 30.0)


def zrob(g):
    cel = os.path.join(g.TU, "dane_nastepne")
    os.makedirs(cel, exist_ok=True)
    rob = g.wyjscie("dane_robocze")
    smoki = g.modele_pelne(jajo=False)
    owca = stwory.owca()
    _predkosc_nog(owca, "chod", 0.72, 24)
    _predkosc_nog(owca, "ucieczka", 0.72, 44)
    golemy = [stwory.golem(t) for t in range(1, 6)] + [stwory_grozne.golem_grozny(t) for t in range(1, 6)]
    for m in golemy:
        _predkosc_nog(m, "chod", 3.6, 22)
    ogien, przyp = efekty.ogien_stozek(), efekty.przypalenie()
    lagodny = sm.zbuduj_stadium(1, id="smok_1_lagodny", nadpisz=LAGODNY)
    z_klipami = smoki + [owca] + golemy + [ogien]
    for m in z_klipami + [przyp, lagodny]:
        for x in m.sprawdz()[0]:
            raise SystemExit("BŁĄD danych: " + x)
    pj, wj = os.path.join(rob, "_pakiet_etap.json"), os.path.join(rob, "_probki_etap.json")
    g.zapisz_json(g.pakiet(z_klipami), pj)
    g.blender(os.path.join(g.BIB, "blender_probki.py"), [pj, wj], "próbki klipów (etap: %d modeli)" % len(z_klipami))
    with open(wj, encoding="utf-8") as f:
        probki = json.load(f)
    pliki = []

    def zapisz(dane, nazwa):
        g._zapisz(dane, os.path.join(cel, nazwa))
        pliki.append(nazwa)

    predkosci = {}
    for m in z_klipami:
        r = g.rig_modelu(m)
        k = g.klipy_modelu(m, r, probki[m.id])
        zapisz(k, m.id + "_klipy.json")
        predkosci[m.id] = {n: c["predkosc"] for n, c in k["klipy"].items() if "predkosc" in c}
        if m is ogien:
            zapisz(r, m.id + "_rig.json")
            czesci_ognia = r["liczba_czesci"]
    rp = g.rig_modelu(przyp)
    zapisz(rp, "rekwizyt_przypalenie_rig.json")
    rl = g.rig_modelu(lagodny)
    zapisz(rl, "smok_1_lagodny_rig.json")
    with open(os.path.join(g.DANE, "indeks.json"), encoding="utf-8") as f:
        indeks = json.load(f)
    stare = indeks["stadia"]
    indeks["jajo"] = next(s for s in stare if s["id"] == "smok_jajo")
    indeks["stadia"] = [dict(s, klipy=len(m.klipy), klatki=sum(x.dlugosc for x in m.klipy), predkosc=predkosci[m.id])
                        for s, m in zip([s for s in stare if s["id"] != "smok_jajo"], smoki)]
    indeks.update({"format": "smok-ewolucji-indeks/3", "wersja": 3, "klipy_dodatkowe": list(sk.KLIPY_DODATKOWE),
                   "efekty": [{"id": "ogien_stozek", "czesci": czesci_ognia, "dlugosc": efekty.DLUGOSC_STOZKA,
                               "stawy": ["Podstawa", "Rdzen", "Pierscien1", "Pierscien2", "Pierscien3"], "klipy": ["migotanie"],
                               "pliki": ["ogien_stozek_rig.json", "ogien_stozek_klipy.json"]},
                              {"id": "przypalenie", "czesci": rp["liczba_czesci"], "promien": efekty.PROMIEN_PRZYPALENIA,
                               "plik": "rekwizyt_przypalenie_rig.json"}],
                   "warianty_modeli": [{"id": "smok_1_lagodny", "zamiast": "smok_1", "plik": "smok_1_lagodny_rig.json",
                                        "czesci": rl["liczba_czesci"], "opis": "łagodniejsze brwi i mniejsze oczy; te same stawy i klipy"}],
                   "predkosc_stworow": {i: v for i, v in predkosci.items() if not i.startswith("smok_") and v}})
    zapisz(indeks, "indeks.json")
    for m in smoki:
        print("ETAP | %-7s chód %.2f  bieg %.2f studs/s  (przysiad chód %.2f, bieg %.2f)" % (
            m.id, predkosci[m.id]["chod"], predkosci[m.id]["bieg"],
            next(x for x in m.klipy if x.nazwa == "chod").przysiad, next(x for x in m.klipy if x.nazwa == "bieg").przysiad))
    print("ETAP | %d plików w dane_nastepne: %s" % (len(pliki), " ".join(sorted(pliki))))

    # ---- film biegu nad ruchomą kratą przy 16 studs/s (stadia 1, 3, 8), pasek klatek i porównanie pisklęcia
    fr, filmy = g.wyjscie("bieg_robocze"), g.wyjscie("filmy")
    wyb = (1, 3, 8)
    zad = [{"typ": "bieg", "model": "smok_%d" % n, "klip": "bieg", "v_gry": 16.0, "v_klipu": predkosci["smok_%d" % n]["bieg"],
            "klatek": 45, "rozmiar": 480, "kierunek": [-1.0, 0.22, 0.3], "kratka": smoki[n - 1].dane_stadium["r"] * 0.8,
            "nazwa": "bieg16"} for n in wyb]
    zad += [{"typ": "widoki", "model": i, "widoki": {"przod": [0.34, 0.2, 1.0], "gra": list(g.GRA)}, "rozmiar": 450,
             "przyrostek": "_por"} for i in ("smok_1", "smok_1_lagodny")]
    g.widoki([smoki[n - 1] for n in wyb] + [lagodny], zad, fr, "film biegu nad kratą i porównanie pisklęcia")
    ffmpeg = shutil.which("ffmpeg")
    for n in wyb:
        if ffmpeg:
            subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-framerate", "30", "-i", os.path.join(fr, "smok_%d_bieg16_%%03d.jpg" % n),
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", os.path.join(filmy, "smok_%d_bieg_16_studs_krata.mp4" % n)],
                           capture_output=True)
    g.siatka_obrazow([[os.path.join(fr, "smok_%d_bieg16_%03d.jpg" % (n, i)) for i in range(0, 16, 2)] for n in wyb],
                     os.path.join(g.PODGLAD, "26_bieg_16_studs.jpg"), kom=200,
                     etykiety_wierszy=["bieg przy 16 studs/s — " + smoki[n - 1].dane_stadium["nazwa"] for n in wyb],
                     tytul="Bieg nad kratą jadącą z prędkością gry (co druga klatka filmu): stopa w podporze stoi na kracie")
    g.siatka_obrazow([[os.path.join(fr, "smok_1_przod_por.jpg"), os.path.join(fr, "smok_1_lagodny_przod_por.jpg")],
                      [os.path.join(fr, "smok_1_gra_por.jpg"), os.path.join(fr, "smok_1_lagodny_gra_por.jpg")]],
                     os.path.join(g.PODGLAD, "05_stadium_1.jpg"), kom=450, etykiety_kolumn=["teraz (smok_1)", "łagodny (smok_1_lagodny)"],
                     tytul="HATCHLING — do wyboru: obecny i łagodny wariant")
    return pliki
