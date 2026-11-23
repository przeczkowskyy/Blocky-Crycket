#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Krótki film z gry Pet Arena (v3 Throw & Catch Monsters, ok. 40 s, 16:9) — dla ludzi bez Studio. Plik MP4 i plansza klatek POZA repo.

    python -B swiat/pet_arena/testy/demo_wideo.py <plik.mp4 poza repo> [--studio <id>] [--zostaw-klipy]

Jak (wzór: swiat/bonk/testy/demo_wideo.py): Play WYŁĄCZNIE przez tools/studio_mcp.py (znacznik próby — w kadrze
„Player 1”, magazyn nieczytany), stan ustawiany haczykami próby (bez grindu), każda scena to osobne nagranie narzędziem
MCP `video_capture` (obraz gry z Play, z dźwiękiem gry), klipy przycina i skleja ffmpeg (H.264 1280 × 720, AAC).
Sceny (v3 Throw & Catch): dzikie wchodzą bramą i rzut → wybicie dzikiego i „CAUGHT!” → odmiana GIANT z ogłoszeniem →
olbrzymi troll na tronie → panel NEXT i ALPHA → jajko w wylęgarni i wyklucie.
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
    """v3 (Throw & Catch Monsters): rzut, wybicie dzikiego i „CAUGHT!” (pierwsze złapanie pewne), odmiana GIANT z ogłoszeniem,
    olbrzymi troll na tronie, panel NEXT i ALPHA z zegara, jajko w wylęgarni i wyklucie."""
    S = lambda a: p.serwer(a)  # noqa: E731
    Kl = lambda a: p.klient(a)  # noqa: E731

    def wyladowal(pid, limit=5):
        PP.czekaj(lambda: (PP.pet(S('"stan"'), pid) or {}).get("faza") == "walka", limit, 0.2)

    def wybij(pid, x, z=0):
        S('"stoj", %d, 6' % pid)
        S('"przenies", %d, %s, %s' % (pid, x, z))
        S('"wyrzuc", %d, 80, 1' % pid)

    S('"bez_wydarzen", true')
    S('"boty", 0')
    S('"usun_dzikie"')
    S('"profil_nowy"')
    S('"zloto", 0')
    S('"druzyna", {"lesny_slime", "zoledziak"}, 1')
    time.sleep(0.6)
    # ------------------------------------------------------------------ 1. cała arena: dzikie wchodzą bramą, rzut z ręki
    f.nagrywaj("arena")
    dzikie = [S('"dziki", %d, %d, %d' % (nr, x, z)) for nr, x, z in ((3, 12, 8), (6, -14, 6), (9, 2, -8))]
    time.sleep(2.0)
    Kl('"rzut", -10, -2')
    time.sleep(2.6)
    f.stop()
    mid = PP.moj(S('"stan"')).get("pet")
    if mid:
        S('"stoj", %d, 20' % mid)
    # ------------------------------------------------------------------ 2. wybicie dzikiego → „CAUGHT!” (pierwsze złapanie pewne)
    f.nagrywaj("zlapanie")
    time.sleep(0.4)
    wybij(dzikie[0], 12, 8)
    time.sleep(4.4)
    f.stop()
    # ------------------------------------------------------------------ 3. odmiana GIANT: ogłoszenie na serwerze
    S('"wymus_lap", true')
    S('"wymus_odmiane", "giant"')
    tr = S('"dziki", 10, 14, -4')
    wyladowal(tr)
    f.nagrywaj("giant")
    time.sleep(0.5)
    wybij(tr, 14, -4)
    time.sleep(4.0)
    f.stop()
    # ------------------------------------------------------------------ 4. olbrzymi troll (GIANT) na tronie, monety, korona
    S('"usun_dzikie"')
    S('"druzyna", {"lesny_troll", "lesny_slime"}, 1')
    mid = PP.rzuc_moim(p, 1, 0, 0)
    if mid:
        S('"przenies", %d, 0, 0' % mid)
        S('"stoj", %d, 10' % mid)
    for nr, x, z in ((1, -12, 6), (4, 12, -6)):
        S('"dziki", %d, %d, %d' % (nr, x, z))
    Kl('"widok", "pet"')
    time.sleep(1.6)
    f.nagrywaj("tron")
    time.sleep(3.6)
    f.stop()
    Kl('"widok", false')
    # ------------------------------------------------------------------ 5. panel NEXT odlicza, ALPHA wchodzi bramą
    S('"wydarzenie", "alfa", 3')
    f.nagrywaj("alfa")
    time.sleep(6.0)
    f.stop()
    # ------------------------------------------------------------------ 6. jajko do wylęgarni, czas mija (atrapa zegara), HATCH!
    S('"zloto", 3000')
    Kl('"okno", "jajka"')
    time.sleep(0.5)
    f.nagrywaj("wylegarnia")
    time.sleep(0.4)
    Kl('"jajko", 2')
    time.sleep(1.8)
    S('"czas_plus", %d' % D["wylegarnia"]["czas_s"][1])
    time.sleep(1.6)
    Kl('"wylegarnia", 1')
    time.sleep(5.4)
    f.stop()
    Kl('"okno", nil')


def sklej(klipy, wyj, kat):
    gotowe = []
    for i, (k, od) in enumerate(klipy):
        c = os.path.join(kat, "c%02d.mp4" % i)
        # klip z video_capture bywa z dwoma strumieniami obrazu — bierzemy pierwszy (inaczej wychodzi sam dźwięk)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.2f" % od, "-i", k, "-map", "0:v:0", "-map", "0:a?",
                        # kadr 16:9 ze środka niezależnie od proporcji okna Studio (szersze albo wyższe)
                        "-vf", r"crop=trunc(min(iw\,ih*16/9)/2)*2:trunc(min(ih\,iw*9/16)/2)*2,scale=1280:720,fps=30,format=yuv420p",
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
    # okno Studio na wierzch tylko, gdy nikt nie siedzi przy komputerze (bezczynność ≥ 600 s) albo działa zaciemnienie
    idle, ciemno = PP.bezczynnosc_s(), PP.zaciemnienie_dziala()
    log("bezczynność %.0f s, zaciemnienie %s" % (idle, ciemno))
    if idle >= 600 or ciemno:
        subprocess.run([sys.executable, "-B", os.path.join(PP.REPO, "tools", "studio_okno.py"), "--na-wierzch"], capture_output=True)
    else:
        log("ktoś pracuje przy komputerze — nie wysuwam okna Studio (film może mieć gorszy obraz)")
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
