#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Krótki film z gry Pet Arena (etap 2, ok. 40 s, 16:9) — dla ludzi bez Studio. Plik MP4 i plansza klatek POZA repo.

    python -B swiat/pet_arena/testy/demo_wideo.py <plik.mp4 poza repo> [--studio <id>] [--zostaw-klipy]

Jak (wzór: swiat/bonk/testy/demo_wideo.py): Play WYŁĄCZNIE przez tools/studio_mcp.py (znacznik próby — w kadrze
„Player 1”, magazyn nieczytany), stan ustawiany haczykami próby (bez grindu), każda scena to osobne nagranie narzędziem
MCP `video_capture` (obraz gry z Play, z dźwiękiem gry), klipy przycina i skleja ffmpeg (H.264 1280 × 720, AAC).
Sceny: wejście i pierwszy rzut z ręki → bitka o środek → umiejętność w dobrym momencie (GROUND SLAM) → RING OUT z
lotem → król i nagroda za głowę → wyklucie jajka → BOSS (lądowanie, walka, deszcz złota).
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
if TU not in sys.path:
    sys.path.insert(0, TU)
import proba_play as PP  # noqa: E402

D, U, K = PP.D, PP.U, PP.K
log = PP.log


class Film:
    def __init__(self, p, kat):
        self.p, self.kat, self.klipy = p, kat, []

    def nagrywaj(self, nazwa):
        r = self.p.call("video_capture", {"is_start": True, "datamodel_type": "Client"})
        if r["is_error"]:
            raise PP.StudioError("video_capture start: %s" % r["text"][:300])
        self.biezacy, self.t0 = nazwa, time.time()

    def stop(self, przyciecie=0.25):
        r = self.p.call("video_capture", {"is_start": False, "datamodel_type": "Client"}, timeout=300)
        try:
            w = json.loads(r["text"])
        except ValueError:
            raise PP.StudioError("video_capture stop: %s" % r["text"][:300])
        cel = os.path.join(self.kat, "%02d_%s.mp4" % (len(self.klipy) + 1, self.biezacy))
        shutil.copyfile(w["artifacts"]["video"], cel)
        self.klipy.append((cel, przyciecie))
        log("klip %s: %.1f s" % (self.biezacy, time.time() - self.t0))


def sceny(p, f):
    S = lambda a: p.serwer(a)  # noqa: E731
    Kl = lambda a: p.klient(a)  # noqa: E731
    S('"bez_wydarzen", true')
    S('"boty", 0')
    S('"usun_dzikie"')
    S('"profil_nowy"')
    S('"zloto", 0')
    time.sleep(1.0)
    # ------------------------------------------------------------------ 1. wejście i pierwszy rzut z ręki
    S('"boty", 3, 0.5')
    time.sleep(2.5)
    f.nagrywaj("rzut")
    time.sleep(1.2)
    Kl('"rzut", 2, 0')
    time.sleep(3.8)
    f.stop()
    # ------------------------------------------------------------------ 2. bitka o środek
    S('"boty", 5, 0.5')
    time.sleep(1.5)
    f.nagrywaj("bitka")
    time.sleep(6.0)
    f.stop()
    # ------------------------------------------------------------------ 3. umiejętność w dobrym momencie: Troll w tłumie
    S('"druzyna", {"lesny_troll", "zoledziak"}, 2')
    mid = PP.rzuc_moim(p, 1, 0, 0)
    S('"usun_dzikie"')
    for i, (x, z) in enumerate(((5, 2), (-5, 2), (2, -6))):
        q = S('"dziki", %d, %d, %d' % (i + 1, x, z))
        S('"zycie", %d, 30' % q)
    time.sleep(1.6)
    f.nagrywaj("umiejetnosc")
    time.sleep(0.8)
    S('"pasek", %d, 1' % mid)
    time.sleep(0.4)
    Kl('"umiejetnosc"')
    time.sleep(3.6)
    f.stop()
    # ------------------------------------------------------------------ 4. RING OUT z lotem
    S('"usun_dzikie"')
    q = S('"dziki", 6, 16, 4')
    time.sleep(1.4)
    S('"zycie", %d, 15' % q)
    S('"przenies", %d, -6, 0' % mid)
    S('"przenies", %d, 18, 4' % q)
    f.nagrywaj("ring_out")
    time.sleep(0.5)
    S('"pchnij", %d, 45, 10' % q)
    time.sleep(3.6)
    f.stop()
    # ------------------------------------------------------------------ 5. król i nagroda za głowę
    S('"przenies", %d, 0, 0' % mid)
    S('"stoj", %d, 7' % mid)
    time.sleep(1.0)
    f.nagrywaj("krol")
    time.sleep(4.5)
    f.stop()
    # ------------------------------------------------------------------ 6. wyklucie jajka
    S('"zloto", 2500')
    time.sleep(0.4)
    Kl('"okno", "jajka"')
    time.sleep(0.6)
    f.nagrywaj("jajko")
    time.sleep(1.0)
    Kl('"jajko", 2')
    time.sleep(4.6)
    f.stop()
    # ------------------------------------------------------------------ 7. BOSS: lądowanie, walka, deszcz złota
    Kl('"okno", nil')
    S('"usun_dzikie"')
    S('"boty", 3, 0.5')
    mid = PP.rzuc_moim(p, 1, -6, 4)
    time.sleep(1.0)
    S('"bez_wydarzen", false')
    S('"wydarzenie", "boss", 0')
    f.nagrywaj("boss")
    boss_id, _ = PP.czekaj(lambda: next((x["id"] for x in S('"stan"')["pety"] if x.get("boss")), None), 4, 0.2)
    S('"bez_wydarzen", true')
    time.sleep(1.6)
    S('"przenies", %d, -5.5, 2' % mid)
    time.sleep(1.6)
    S('"pasek", %d, 1' % mid)
    Kl('"umiejetnosc"')
    time.sleep(1.2)
    if boss_id:
        S('"zycie", %d, 1' % boss_id)
    time.sleep(3.6)
    f.stop()


def sklej(klipy, wyj, kat):
    gotowe = []
    for i, (k, od) in enumerate(klipy):
        c = os.path.join(kat, "c%02d.mp4" % i)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.2f" % od, "-i", k,
                        "-vf", "crop=iw:trunc(iw*9/16/2)*2,scale=1280:720,fps=30,format=yuv420p",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-c:a", "aac", "-b:a", "96k", "-ar", "48000", "-ac", "2",
                        c], check=True)
        gotowe.append(c)
    lista = os.path.join(kat, "lista.txt")
    with open(lista, "w", encoding="utf-8") as f:
        for c in gotowe:
            f.write("file '%s'\n" % c.replace("\\", "/"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy",
                    "-movflags", "+faststart", wyj], check=True)


def plansza(wyj):
    """Plansza klatek (co ok. 3,4 s, 4 × 3) obok filmu."""
    cel = os.path.splitext(wyj)[0] + "_plansza.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wyj, "-vf", "fps=1/3.4,scale=640:-1,tile=4x3", "-frames:v", "1", "-q:v", "4", cel],
                   check=True)
    return cel


def main():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("wyj")
    ap.add_argument("--studio", default=None)
    ap.add_argument("--zostaw-klipy", action="store_true")
    a = ap.parse_args()
    wyj = os.path.abspath(a.wyj)
    if wyj.startswith(os.path.abspath(PP.REPO)):
        sys.exit("film zapisuj POZA repozytorium")
    os.makedirs(os.path.dirname(wyj), exist_ok=True)
    kat = tempfile.mkdtemp(prefix="petarena_demo_", dir=os.path.dirname(wyj))
    subprocess.run([sys.executable, "-B", os.path.join(PP.REPO, "tools", "studio_okno.py"), "--na-wierzch"], capture_output=True)
    with PP.Proba(a.studio) as p:
        if not p.tryb_edit():
            sys.exit("Studio nie jest w trybie Edit — nie zaczynam")
        f = Film(p, kat)
        try:
            log("Play:", p.call("start_stop_play", {"is_start": True})["text"][:80])
            PP.czekaj(lambda: p.luau(PP.GOTOWOSC, "Client").startswith("true true"), 60, 0.3)
            p.luau(PP.BEZ_LISTY, "Client")
            time.sleep(1.0)
            sceny(p, f)
        finally:
            log("Stop:", p.call("start_stop_play", {"is_start": False})["text"][:80])
            PP.czekaj(p.tryb_edit, 40, 0.5)
    sklej(f.klipy, wyj, kat)
    pl = plansza(wyj)
    if not a.zostaw_klipy:
        shutil.rmtree(kat, ignore_errors=True)
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", wyj], capture_output=True, text=True)
    log("film:", wyj, r.stdout.replace("\n", " "), "plansza:", pl)


if __name__ == "__main__":
    main()
