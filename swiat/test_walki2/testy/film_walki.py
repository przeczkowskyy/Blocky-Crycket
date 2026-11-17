#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Film MP4 z JEDNEJ całej walki z próby walki (tryb Play; sam wraca do trybu Edit) — do pokazania walki komuś bez Studio.

    python -B swiat/test_walki2/testy/film_walki.py                                   # walka pokazowa z ziarna.json („shard”)
    python -B swiat/test_walki2/testy/film_walki.py --klasa mag --przeciwnik cierniowy_wilk --poziom 5 --ziarno 910854
    python -B swiat/test_walki2/testy/film_walki.py --kl 8 --wyj <plik.mp4>

Jak: walka startuje z opcją `reczny` (czas sceny stoi), skrypt przesuwa czas co 1/kl sekundy czasu „jak w grze”
(„przewin”: z tempem gracza, zwolnieniem przy krytyku i finałem w ×1) i przy każdym kroku robi zrzut z bieżącej kamery
odtwarzacza. Z klatek ffmpeg składa film. Na końcu kilka sekund panelu wyniku. To zapis poklatkowy: efekty, napisy
i kamera liczą się w tym samym czasie co w grze, ale dźwięku w filmie nie ma (dźwięki gra tylko klient w Play). Wymaga: Studio w trybie Edit z kontenerem Workspace/TestWalki2, ffmpeg, Pillow.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
KATALOG = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(KATALOG))
for _s in (TU, os.path.join(REPO, "tools", "walka")):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import silnik as S  # noqa: E402
import wzorcowe as WZ  # noqa: E402
from sesja_play import SesjaPlay, log  # noqa: E402


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    with open(os.path.join(TU, "ziarna.json"), encoding="utf-8") as f:
        pokaz = json.load(f)["shard"]
    ap = argparse.ArgumentParser()
    ap.add_argument("--klasa", default=pokaz["klasa"])
    ap.add_argument("--przeciwnik", default=pokaz["przeciwnik"])
    ap.add_argument("--poziom", type=int, default=pokaz["poziom"])
    ap.add_argument("--ziarno", type=int, default=pokaz["ziarno"])
    ap.add_argument("--kl", type=int, default=10, help="klatek na sekundę czasu sceny")
    ap.add_argument("--wynik-s", type=float, default=3.0, help="ile sekund panelu wyniku na końcu")
    ap.add_argument("--tempo", type=int, default=1, help="tempo gracza (1, 2, 4); finał i tak gra w ×1")
    ap.add_argument("--wyj", default=None)
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()

    walka = S.symuluj(WZ.postac(a.klasa, a.poziom), {"potwor": a.przeciwnik, "poziom": a.poziom}, a.ziarno)
    czas = float(walka["czas"])
    wyj = a.wyj or os.path.join(KATALOG, "klatki", "film_%s_%s_%d.mp4" % (a.klasa, a.przeciwnik, a.poziom))
    log("walka: %s kontra %s, poziom %d, ziarno %d — %s, %d tur, %.1f s" % (
        a.klasa, a.przeciwnik, a.poziom, a.ziarno, walka["wynik"], walka["tury"], czas))
    kat = tempfile.mkdtemp(prefix="film_walki_")
    n = 0
    try:
        with SesjaPlay(a.studio) as s:
            for _ in range(40):                                   # ekran ładowania gry zasłania scenę po starcie
                if s.luau('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("LoadingScreen") '
                          'local b = g and g:FindFirstChild("Background") '
                          'return tostring(g == nil or not g.Enabled or b == nil or not b.Visible or b.BackgroundTransparency >= 0.99)').strip() == "true":
                    break
                time.sleep(0.5)
            time.sleep(1.0)
            s.przy_tablicy()
            s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", true) return "ok"', "Server")
            try:
                s.steruj('"zamknij"')
                time.sleep(1.2)
                s.ziarno(a.ziarno)
                s.start(a.klasa, a.przeciwnik, str(a.poziom), "{ reczny = true, tempo = %d }" % a.tempo)
                st, _ = s.czekaj(("odtwarzanie",), 15)
                if st.get("OstatniStan") != "odtwarzanie":
                    raise SystemExit("walka nie wystartowała: %s %s" % (st.get("OstatniStan"), st.get("OstatniaOdmowa")))
                t0 = time.time()
                # od 15.11: krok = 1/kl sekundy czasu „jak w grze” (przewin): zwolnienia przy krytyku, finał w ×1,
                # napisy i przejścia kamery wyglądają tak, jak przy zwykłym oglądaniu (wcześniej krok czasu sceny)
                kroki = int((czas / a.tempo + 20) * a.kl)
                for k in range(kroki):
                    st = json.loads(s.steruj('"przewin", %f' % (1.0 / a.kl)))
                    time.sleep(0.05)
                    im, _ = s.zrzut_odtwarzacza()
                    im.save(os.path.join(kat, "k_%05d.jpg" % n), "JPEG", quality=90)
                    n += 1
                    if n == 10:
                        log("  10 klatek w %.1f s" % (time.time() - t0))
                    if st.get("faza") != "odtwarzanie":
                        break
                s.steruj('"przewinDo", 1000')
                time.sleep(1.8)
                im, _ = s.zrzut_odtwarzacza()
                for _ in range(max(1, int(a.wynik_s * a.kl))):       # panel wyniku: ta sama klatka przez kilka sekund
                    im.save(os.path.join(kat, "k_%05d.jpg" % n), "JPEG", quality=90)
                    n += 1
                s.steruj('"zamknij"')
            finally:
                try:
                    s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", nil) '
                           'workspace.TestWalki2:SetAttribute("ZiarnoTestowe", nil) return "ok"', "Server")
                except Exception:  # noqa: BLE001
                    pass
        log("klatek: %d — składam film" % n)
        os.makedirs(os.path.dirname(os.path.abspath(wyj)), exist_ok=True)
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(a.kl), "-i", os.path.join(kat, "k_%05d.jpg"),
                            # film do repozytorium i na telefon: szerokość najwyżej 1280, żeby plik miał kilka MB
                            "-vf", "scale='min(1280,iw)':-2", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                            "-crf", "27", "-movflags", "+faststart", wyj], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("ffmpeg: %s" % (r.stderr or "")[:400])
        log("film: %s (%.1f MB, %.1f s)" % (os.path.relpath(wyj, REPO), os.path.getsize(wyj) / 1e6, n / a.kl))
    finally:
        shutil.rmtree(kat, ignore_errors=True)


if __name__ == "__main__":
    main()
