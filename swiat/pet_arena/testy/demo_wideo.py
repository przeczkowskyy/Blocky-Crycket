#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Krótki film z gry Pet Arena (v2, ok. 40 s, 16:9) — dla ludzi bez Studio. Plik MP4 i plansza klatek POZA repo.

    python -B swiat/pet_arena/testy/demo_wideo.py <plik.mp4 poza repo> [--studio <id>] [--zostaw-klipy]

Jak (wzór: swiat/bonk/testy/demo_wideo.py): Play WYŁĄCZNIE przez tools/studio_mcp.py (znacznik próby — w kadrze
„Player 1”, magazyn nieczytany), stan ustawiany haczykami próby (bez grindu), każda scena to osobne nagranie narzędziem
MCP `video_capture` (obraz gry z Play, z dźwiękiem gry), klipy przycina i skleja ffmpeg (H.264 1280 × 720, AAC).
Sceny (v2): cała arena z petami różnej wielkości i rzut z ręki → sterowanie petem → zepchnięcie króla z tronu
umiejętnością → wielkie wybicie ponad trybuny → wzgórze ze złotem → wyklucie → złoty boss wchodzący bramą.
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
    """v2: duża arena z petami różnej wielkości, rzut z ręki, sterowanie petem, zepchnięcie króla z tronu, wielkie
    wybicie ponad trybuny, wzgórze ze złotem, wyklucie, złoty boss wchodzący bramą."""
    S = lambda a: p.serwer(a)  # noqa: E731
    Kl = lambda a: p.klient(a)  # noqa: E731
    S('"bez_wydarzen", true')
    S('"boty", 0')
    S('"usun_dzikie"')
    S('"profil_nowy"')
    S('"zloto", 0')
    S('"druzyna", {"lesny_troll", "lesny_slime"}, 2')
    for nr, x, z in ((1, -14, 8), (3, 12, 10), (12, 0, 0), (9, -10, -12)):
        S('"dziki", %d, %d, %d' % (nr, x, z))
    time.sleep(2.5)
    # ------------------------------------------------------------------ 1. cała arena: pety różnej wielkości, rzut z ręki
    Kl('"widok", true')
    time.sleep(0.8)
    f.nagrywaj("arena")
    time.sleep(2.2)
    Kl('"rzut", 14, -6')
    time.sleep(2.0)
    Kl('"widok", false')
    time.sleep(1.4)
    f.stop()
    mid = PP.moj(S('"stan"')).get("pet")
    # ------------------------------------------------------------------ 2. sterowanie: pet biegnie tam, gdzie każe gracz — na tron
    f.nagrywaj("sterowanie")
    Kl('"ster", Vector2.new(-0.7, 0.7), 1.6')
    time.sleep(1.7)
    Kl('"ster", Vector2.new(0, 1), 1.6')
    time.sleep(1.8)
    f.stop()
    # ------------------------------------------------------------------ 3. zepchnięcie króla z tronu: umiejętność w dobrym momencie
    st = S('"stan"')
    krol = st.get("krol")
    if mid:
        S('"przenies", %d, 9, 4' % mid)
        S('"pasek", %d, 1' % mid)
    f.nagrywaj("tron")
    Kl('"ster", Vector2.new(0, 1), 1.0')
    time.sleep(0.9)
    Kl('"umiejetnosc"')
    time.sleep(3.0)
    f.stop()
    # ------------------------------------------------------------------ 4. wielkie wybicie ponad trybuny (kamera za lecącym)
    st = S('"stan"')
    ofiara = next((x["id"] for x in st["pety"] if x.get("dziki") and not x.get("boss")), None)
    if ofiara:
        S('"przenies", %d, 28, 6' % ofiara)
        f.nagrywaj("wybicie")
        time.sleep(0.4)
        S('"wyrzuc", %d, 75, 1' % ofiara)
        time.sleep(3.0)
        f.stop()
    # ------------------------------------------------------------------ 5. wzgórze króla: mój pet na tronie, monety lecą, korona rośnie
    S('"usun_dzikie"')
    if mid:
        S('"przenies", %d, 0, 0' % mid)
        S('"stoj", %d, 8' % mid)
    time.sleep(1.5)
    f.nagrywaj("wzgorze")
    time.sleep(4.2)
    f.stop()
    # ------------------------------------------------------------------ 6. wyklucie jajka
    S('"zloto", 2500')
    time.sleep(0.4)
    Kl('"okno", "jajka"')
    time.sleep(0.5)
    f.nagrywaj("jajko")
    time.sleep(0.6)
    Kl('"jajko", 2')
    time.sleep(5.6)
    f.stop()
    # ------------------------------------------------------------------ 7. złoty boss wchodzi bramą, bicie, deszcz złota
    Kl('"okno", nil')
    S('"boty", 3, 0.5')
    if mid:
        S('"stoj", %d, 0' % mid)
    time.sleep(1.5)
    Kl('"widok", true')
    S('"bez_wydarzen", false')
    S('"wydarzenie", "zloty", 0')
    f.nagrywaj("zloty_boss")
    boss_id, _ = PP.czekaj(lambda: next((x["id"] for x in S('"stan"')["pety"] if x.get("boss")), None), 4, 0.2)
    S('"bez_wydarzen", true')
    time.sleep(3.0)
    if mid:
        S('"przenies", %d, -10.5, 2' % mid)
    Kl('"widok", false')
    time.sleep(2.2)
    if boss_id:
        S('"zycie", %d, 1' % boss_id)
    time.sleep(2.8)
    f.stop()

def sklej(klipy, wyj, kat):
    gotowe = []
    for i, (k, od) in enumerate(klipy):
        c = os.path.join(kat, "c%02d.mp4" % i)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.2f" % od, "-i", k,
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
