#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Jedna walka z próby walki w trybie Play (narzędzie robocze do oglądania; sam wraca do trybu Edit).

    python -B swiat/test_walki2/testy/proba_play.py --wybor wojownik/lesny_troll/5 --ziarno 7
    python -B swiat/test_walki2/testy/proba_play.py --wybor mag/lesny_slime/10 --ziarno 31997 --klatki 0.25 --od 1 --do 9
    python -B swiat/test_walki2/testy/proba_play.py --wybor ... --zywo [--tempo 4]   # odtworzenie w czasie rzeczywistym

--klatki S: czas sceny stoi (opcja reczny), skrypt przesuwa go o S sekund i robi zrzut — arkusz klatek w --wyj.
--zywo: zwykłe odtworzenie do panelu wyniku; wypisuje atrybuty pomiarów i komunikaty konsoli z TestWalki2.
"""
import argparse
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
from sesja_play import SesjaPlay, log, UKRYJ_GUI_GRY  # noqa: E402


def arkusz(kafle, sciezka, kolumny=4, bok=(480, 270)):
    from PIL import Image
    kol = min(kolumny, len(kafle))
    wiersze = (len(kafle) + kol - 1) // kol
    ark = Image.new("RGB", (kol * bok[0], wiersze * bok[1]), (20, 18, 24))
    for i, im in enumerate(kafle):
        ark.paste(im, ((i % kol) * bok[0], (i // kol) * bok[1]))
    ark.save(sciezka, "JPEG", quality=84)
    log("arkusz:", sciezka)


def kafel(im, podpis, bok=(480, 270)):
    from PIL import ImageDraw
    w, h = im.size
    # kadr 16:9 ze środka
    if w / h > 16 / 9:
        nw = int(h * 16 / 9)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w * 9 / 16)
        im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    im = im.resize(bok)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, bok[0], 14), fill=(0, 0, 0))
    d.text((4, 1), podpis, fill=(255, 255, 255))
    return im


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--wybor", default="wojownik/lesny_troll/5")
    ap.add_argument("--ziarno", type=int, default=7)
    ap.add_argument("--klatki", type=float, default=0.0)
    ap.add_argument("--od", type=float, default=0.0)
    ap.add_argument("--do", type=float, default=0.0)
    ap.add_argument("--zywo", action="store_true")
    ap.add_argument("--tempo", type=int, default=1)
    ap.add_argument("--wyj", default=None)
    ap.add_argument("--nazwa", default="proba")
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    klasa, wrog, poziom = a.wybor.split("/")
    wyj = a.wyj or os.path.join(os.environ.get("TEMP", TU), "tw2_proba")
    os.makedirs(wyj, exist_ok=True)
    with SesjaPlay(a.studio) as p:
        p.przy_tablicy()
        p.ziarno(a.ziarno)
        time.sleep(0.5)
        if a.klatki > 0:
            p.luau(UKRYJ_GUI_GRY)
            p.start(klasa, wrog, poziom, "{ reczny = true, tempo = %d }" % a.tempo)
            s, dt = p.czekaj(("odtwarzanie",), 15)
            log("start:", s.get("OstatniStan"), "%.1f s" % dt, s.get("OstatniaOdmowa"))
            st = s.get("_odtw") or {}
            czas = st.get("czas") or 10
            koniec = a.do or czas
            if a.od > 0:
                p.steruj('"przewin", %f' % a.od)
            t = a.od
            kafle = []
            while t <= koniec + 1e-6:
                im, st = p.zrzut_odtwarzacza()
                kafle.append(kafel(im, "t=%.2f zd.%s %s %s %s" % (st.get("tau", 0), st.get("biezace"), st.get("typ") or "",
                                                                  st.get("umiejetnosc") or "", st.get("ujecie"))))
                p.steruj('"przewin", %f' % a.klatki)
                t += a.klatki
                if len(kafle) >= 48:
                    break
            arkusz(kafle, os.path.join(wyj, "%s.jpg" % a.nazwa))
            p.steruj('"przewin", 100')
            time.sleep(1.0)
            im, st = p.zrzut_odtwarzacza()
            kafel(im, "wynik").save(os.path.join(wyj, "%s_wynik.jpg" % a.nazwa), quality=88)
        else:
            p.start(klasa, wrog, poziom, "{ tempo = %d, etykietaCzasu = true }" % a.tempo)
            s, dt = p.czekaj(("odtwarzanie",), 15)
            log("start:", s.get("OstatniStan"), "%.1f s" % dt, s.get("OstatniaOdmowa"))
            s, dt = p.czekaj(("wynik", "blad", "przerwano"), 120)
            log("koniec:", s.get("OstatniStan"), "%.1f s" % dt)
            for k in sorted(s):
                if k.startswith("Ostatni") or k.startswith("Ostatnie") or k.startswith("Serwer"):
                    print("   ", k, "=", s[k])
            time.sleep(1.5)
            im, st = p.zrzut_odtwarzacza()
            kafel(im, "wynik").save(os.path.join(wyj, "%s_wynik.jpg" % a.nazwa), quality=88)
        kons = p.konsola()
        zle = [w for w in kons.splitlines() if "TestWalki2" in w or "rror" in w]
        log("konsola (TestWalki2/Error):", len(zle))
        for w in zle[:15]:
            print("   ", w[:300])


if __name__ == "__main__":
    main()
