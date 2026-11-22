#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Krótki film z Monster Evolution (ok. 35 s, 16:9) — dla ludzi bez Studio. Plik MP4 i plansza klatek POZA repo.

    python -B swiat/ewolucja/testy/demo_wideo.py --studio <id> [--wyj <plik.mp4 poza repo>] [--zostaw-klipy]

Domyślnie zapis do folderu tymczasowego systemu (zmienna środowiska TEMP; tak jak katalog roboczy demo Pet Areny):
<TEMP>/ewolucja_demo/ewolucja_etap3.mp4 i ..._plansza.jpg. Wzór: swiat/pet_arena/testy/demo_wideo.py — Play / Stop przez
tools/studio_mcp.py (podproces), stan ustawiany haczykami próby (bez grindu), każda scena to osobne nagranie narzędziem
MCP `video_capture` (obraz gry z Play z dźwiękiem), klipy przycina i skleja ffmpeg (H.264 1280 × 720, AAC).
Sceny (etap 3): start w legowisku → jedzenie → odsłona z wariantem → zebranie złota w legowisku → poziom trofeum → boss stopnia 2 → Olbrzym.
W kadrze gracz próby, bez listy graczy i czatu. Okna Studio nie wysuwa (bez sterowania pulpitem).
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

D = PP.D
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
    st = p.serwer('"stan"')
    byt = st["byt"]
    lx, lz = D["legowiska"][0]
    # start w legowisku i jedzenie
    p.ustaw("EW_TestAuto", "true")
    f.nagrywaj("start")
    time.sleep(4.5)
    f.stop()
    time.sleep(2)
    f.nagrywaj("jedzenie")
    time.sleep(5)
    f.stop()
    # odsłona z wariantem (los serwera wymuszony haczykiem próby)
    p.ustaw("EW_TestAuto", "false")
    p.serwer('"wymus_wariant", "krysztal"')
    p.serwer('"wzrost_pelny"')
    f.nagrywaj("wariant")
    p.przycisk("ewoluuj")
    time.sleep(4.8)
    f.stop()
    # legowisko w świecie: kupka złota, wejście i zebranie
    p.serwer('"zloto_leg", 1500')
    p.serwer('"przenies", %d, %f, %f' % (byt, lx * 0.78, lz * 0.78))
    time.sleep(1.2)
    f.nagrywaj("legowisko")
    p.ustaw("EW_TestSter", "Vector3.new(%f, %f, 2.2)" % (-lx / 126.0, lz / 126.0))
    time.sleep(3.5)
    f.stop()
    # panel legowiska: poziom trofeum
    p.serwer('"do_legowiska"')
    p.serwer('"zloto", 3000')
    p.przycisk("legowisko")
    time.sleep(0.5)
    f.nagrywaj("panel")
    time.sleep(1.0)
    p.przycisk("trofeum:2")
    time.sleep(1.2)
    p.przycisk("trofeum:1")
    time.sleep(1.2)
    p.przycisk("zamknij")
    f.stop()
    # boss stopnia 2 w lesie
    for _ in range(4):
        st = p.serwer('"stan"')
        if st["forma"] >= 5:
            break
        p.serwer('"wzrost_pelny"')
        p.przycisk("ewoluuj")
        PP.czekaj(lambda: p.serwer('"stan"')["forma"] > st["forma"], 5, 0.3)
    time.sleep(1.5)
    p.serwer('"boss_stopien", 2')
    st = p.serwer('"stan"')
    B = p.serwer('"boss"')
    r = D["formy"][st["forma"] - 1]["r"] + D["formy"][D["boss"]["forma"] - 1]["r"] + 1.5
    p.serwer('"przenies", %d, %f, %f' % (byt, B["x"] + 26, B["z"] - 14))
    time.sleep(1.0)
    f.nagrywaj("boss")
    time.sleep(1.2)
    p.serwer('"boss_hp", 30')
    p.serwer('"boss_stoj", 6')
    B = p.serwer('"boss"')
    p.serwer('"tarcza_zeruj"')
    p.serwer('"przenies", %d, %f, %f' % (byt, B["x"] + r, B["z"]))
    for _ in range(5):
        time.sleep(0.75)
        p.przycisk("gryz")
        if p.serwer('"boss"')["martwy"]:
            break
    p.serwer('"boss_hp", 2')
    time.sleep(0.6)
    p.przycisk("gryz")
    time.sleep(2.4)
    f.stop()
    # Olbrzym z koroną
    p.serwer('"forma_gracza", %d' % len(D["formy"]))
    p.serwer('"przenies", %d, 20, -40' % byt)
    time.sleep(1.5)
    f.nagrywaj("olbrzym")
    p.ustaw("EW_TestSter", "Vector3.new(0.6, 0.4, 3)")
    time.sleep(3.5)
    f.stop()


def sklej(klipy, wyj, kat):
    gotowe = []
    for i, (k, od) in enumerate(klipy):
        c = os.path.join(kat, "c%02d.mp4" % i)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.2f" % od, "-i", k, "-map", "0:v:0", "-map", "0:a?",
                        "-vf", r"crop=trunc(min(iw\,ih*16/9)/2)*2:trunc(min(ih\,iw*9/16)/2)*2,scale=1280:720,fps=30,format=yuv420p",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-c:a", "aac", "-b:a", "96k", "-ar", "48000", "-ac", "2",
                        c], check=True)
        gotowe.append(c)
    lista = os.path.join(kat, "lista.txt")
    with open(lista, "w", encoding="utf-8") as f:
        for c in gotowe:
            f.write("file '%s'\n" % c.replace("\\", "/"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", "-movflags", "+faststart", wyj],
                   check=True)


def plansza(wyj):
    cel = os.path.splitext(wyj)[0] + "_plansza.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wyj, "-vf", "fps=1/3,scale=640:-1,tile=4x3", "-frames:v", "1", "-q:v", "4", cel], check=True)
    return cel


def main():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio", required=True)
    ap.add_argument("--wyj", default=os.path.join(tempfile.gettempdir(), "ewolucja_demo", "ewolucja_etap3.mp4"))
    ap.add_argument("--zostaw-klipy", action="store_true")
    a = ap.parse_args()
    wyj = os.path.abspath(a.wyj)
    if wyj.startswith(os.path.abspath(PP.REPO)):
        sys.exit("film zapisuj POZA repozytorium")
    os.makedirs(os.path.dirname(wyj), exist_ok=True)
    kat = tempfile.mkdtemp(prefix="ewolucja_demo_", dir=os.path.dirname(wyj))
    with PP.StudioMCP(timeout=300) as s:
        p = PP.P(s, a.studio)
        if "Current Studio Mode: Edit" not in p.call("get_studio_state")["text"]:
            sys.exit("Studio nie jest w trybie Edit — nie zaczynam")
        f = Film(p, kat)
        try:
            log("Play:", PP.play(a.studio, True)[-40:])
            PP.czekaj(lambda: p.atr().get("klient") and p.atr().get("EW_Byt"), 30, 0.5)
            p.luau(PP.BEZ_LISTY, "Client")
            time.sleep(1.0)
            sceny(p, f)
        finally:
            log("Stop:", PP.play(a.studio, False)[-40:])
            PP.czekaj(lambda: "Current Studio Mode: Edit" in p.call("get_studio_state")["text"], 40, 0.5)
    sklej(f.klipy, wyj, kat)
    pl = plansza(wyj)
    if not a.zostaw_klipy:
        shutil.rmtree(kat, ignore_errors=True)
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", wyj], capture_output=True, text=True)
    log("film:", wyj, r.stdout.replace("\n", " "), "plansza:", pl)


if __name__ == "__main__":
    main()
