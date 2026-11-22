#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Krótki film z Monster Evolution (ok. 35 s, 16:9) — dla ludzi bez Studio. Plik MP4 i plansza klatek POZA repo.

    python -B swiat/ewolucja/testy/demo_wideo.py --studio <id> [--wyj <plik.mp4 poza repo>] [--zostaw-klipy]

Domyślnie zapis do folderu tymczasowego systemu (zmienna środowiska TEMP; tak jak katalog roboczy demo Pet Areny):
<TEMP>/ewolucja_demo/ewolucja_smok.mp4 i ..._plansza.jpg. Wzór: swiat/pet_arena/testy/demo_wideo.py — Play / Stop przez
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


def sceny_walka(p, f):
    """walka1: łańcuch BITE, EMBER SPIT, FIRE BREATH, TAIL SWEEP, WING GLIDE na SKY NEST, ROAR, INFERNO, METEOR DIVE."""
    st = p.serwer('"stan"')
    byt = st["byt"]
    p.serwer('"laska_zeruj"')

    def stadium(forma, x, z):
        p.serwer('"forma_gracza", %d' % forma)
        p.serwer('"zdolnosci_zeruj"')
        p.serwer('"przenies", %d, %f, %f' % (byt, x, z))
        time.sleep(1.0)
        p.serwer('"tarcza_zeruj"')
        p.serwer('"hp", nil, 9999')
        return p.serwer('"stan"')

    def patrz(x, z, czas=0.3):
        p.ustaw("EW_TestSter", "Vector3.new(%f, %f, %f)" % (-x, z, czas))
        time.sleep(czas)

    # łańcuch BITE z odwetem bota tego samego stadium, kończy chrupnięciem
    st = stadium(3, 0, -20)
    r = D["formy"][2]["r"]
    bid = PP.bot_obok(p, st, 3, 2 * r + 1, 0)
    p.serwer('"hp", %d, 75' % bid)
    patrz(1, 0.05)
    f.nagrywaj("gryz")
    for _ in range(7):
        p.przycisk("gryz")
        time.sleep(0.5)
    time.sleep(1.2)
    f.stop()
    # EMBER SPIT na odległość
    st = stadium(2, -10, 10)
    bid = PP.bot_obok(p, st, 2, 0, 16)
    patrz(0, 1)
    f.nagrywaj("ember")
    p.przycisk("ogien")
    time.sleep(1.6)
    f.stop()
    # FIRE BREATH sterowany w dwa boty
    st = stadium(4, 10, -15)
    PP.bot_obok(p, st, 3, -3, 10)
    PP.bot_obok(p, st, 3, 4, 11)
    patrz(0, 1)
    f.nagrywaj("oddech")
    p.przycisk("ogien")
    time.sleep(0.8)
    patrz(0.4, 1, 0.6)
    patrz(-0.4, 1, 0.6)
    time.sleep(0.8)
    f.stop()
    # TAIL SWEEP w otoczeniu
    st = stadium(3, 20, 20)
    for dx, dz in ((6, 0), (-6, 1), (0, -6)):
        PP.bot_obok(p, st, 2, dx, dz)
    f.nagrywaj("ogon")
    time.sleep(0.4)
    p.przycisk("moc")
    time.sleep(1.8)
    f.stop()
    # WING GLIDE nad lawą na SKY NEST
    WY = D["wyspa"]
    stadium(5, WY["x"], WY["z"] - WY["r_zew"] - 8)
    patrz(0, 1)
    f.nagrywaj("szybowanie")
    p.przycisk("moc")
    time.sleep(2.6)
    f.stop()
    # ROAR: mniejsze uciekają, reszta ogłuszona
    st = stadium(6, -20, 40)
    for dx, dz in ((10, 2), (-9, 4), (2, 11)):
        PP.bot_obok(p, st, 4, dx, dz)
    f.nagrywaj("ryk")
    time.sleep(0.3)
    p.przycisk("moc")
    time.sleep(2.2)
    f.stop()
    # INFERNO BREATH: płonąca ziemia
    st = stadium(7, 30, -30)
    PP.bot_obok(p, st, 5, 0, 18)
    patrz(0, 1)
    f.nagrywaj("inferno")
    p.przycisk("ogien")
    time.sleep(1.0)
    patrz(0.5, 1, 0.8)
    time.sleep(1.8)
    f.stop()
    # METEOR DIVE w grupę
    st = stadium(len(D["formy"]), 0, -60)
    A = D["zdolnosci"]["moc"][-1]
    for dx, dz in ((0, 0), (7, 3), (-7, 2)):
        PP.bot_obok(p, st, 6, dx, A["d"] + dz)
    patrz(0, 1)
    f.nagrywaj("meteor")
    p.przycisk("moc")
    time.sleep(2.6)
    f.stop()


def sceny_blender(p, f):
    """Smoki z Blendera (smok-blender1): wyklucie → jedzenie → ewolucja → walka z ogniem → szybowanie na SKY NEST → legowisko → stadium 8."""
    st = p.serwer('"stan"')
    byt = st["byt"]
    p.serwer('"przenies", %d, %f, %f' % (byt, D["legowiska"][(st.get("slot") or 1) - 1][0] * 0.97, D["legowiska"][(st.get("slot") or 1) - 1][1] * 0.97))
    time.sleep(0.5)
    p.przycisk("jajko")
    time.sleep(0.15)
    f.nagrywaj("wyklucie")
    time.sleep(4.4)
    f.stop(0.1)
    p.ustaw("EW_TestAuto", "true")
    f.nagrywaj("jedzenie")
    time.sleep(7.0)
    f.stop()
    p.ustaw("EW_TestAuto", "false")
    p.serwer('"wzrost_pelny"')
    f.nagrywaj("ewolucja")
    p.przycisk("ewoluuj")
    time.sleep(5.4)
    f.stop()
    p.serwer('"laska_zeruj"')
    p.serwer('"forma_gracza", 4')
    p.serwer('"zdolnosci_zeruj"')
    p.serwer('"przenies", %d, 10, -15' % byt)
    time.sleep(1.0)
    p.serwer('"tarcza_zeruj"')
    p.serwer('"hp", nil, 5000')
    st = p.serwer('"stan"')
    r4 = D["formy"][3]["r"]
    for dx in (-3, 4):
        b = PP.bot_obok(p, st, 3, dx, r4 + D["formy"][2]["r"] + 2)
        p.serwer('"bot_cisza", %d, 8' % b)
    p.ustaw("EW_TestSter", "Vector3.new(0, 1, 0.3)")
    f.nagrywaj("walka")
    time.sleep(0.3)
    for _ in range(3):
        p.przycisk("gryz")
        time.sleep(0.55)
    p.przycisk("ogien")
    time.sleep(0.9)
    p.ustaw("EW_TestSter", "Vector3.new(0.5, 1, 0.8)")
    time.sleep(2.6)
    p.ustaw("EW_TestSter", "Vector3.new(-0.6, 0.4, 1.5)")
    time.sleep(1.6)
    f.stop()
    WY = D["wyspa"]
    p.serwer('"forma_gracza", 5')
    p.serwer('"zdolnosci_zeruj"')
    p.serwer('"przenies", %d, %f, %f' % (byt, WY["x"], WY["z"] - WY["r_zew"] - 8))
    time.sleep(1.0)
    p.ustaw("EW_TestSter", "Vector3.new(0, 1, 0.3)")
    time.sleep(0.3)
    f.nagrywaj("szybowanie")
    p.przycisk("moc")
    time.sleep(3.4)
    f.stop()
    lx, lz = D["legowiska"][(st.get("slot") or 1) - 1]
    p.serwer('"przenies", %d, %f, %f' % (byt, lx * 0.82, lz * 0.82))
    p.serwer('"zloto_leg", 2500')
    time.sleep(1.2)
    f.nagrywaj("legowisko")
    p.ustaw("EW_TestSter", "Vector3.new(%f, %f, 1.2)" % (-lx / 126.0, lz / 126.0))
    time.sleep(4.8)
    f.stop()
    p.serwer('"forma_gracza", %d' % len(D["formy"]))
    p.serwer('"zdolnosci_zeruj"')
    p.serwer('"przenies", %d, 30, -10' % byt)
    time.sleep(1.2)
    p.serwer('"tarcza_zeruj"')
    p.serwer('"hp", nil, 9000')
    st = p.serwer('"stan"')
    A = D["zdolnosci"]["moc"][-1]
    for dx, dz in ((0, 0), (7, 3), (-7, 2)):
        PP.bot_obok(p, st, 6, dx, A["d"] + dz)
    p.ustaw("EW_TestSter", "Vector3.new(0, 1, 0.3)")
    f.nagrywaj("stadium8")
    time.sleep(0.5)
    p.przycisk("moc")
    time.sleep(3.0)
    p.ustaw("EW_TestSter", "Vector3.new(0.7, 0.7, 2)")
    time.sleep(2.0)
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
    ap.add_argument("--wyj", default=os.path.join(tempfile.gettempdir(), "ewolucja_demo", "ewolucja_smok.mp4"))
    ap.add_argument("--zostaw-klipy", action="store_true")
    ap.add_argument("--walka", action="store_true", help="sceny walki (walka1) zamiast przeglądu gry")
    ap.add_argument("--blender", action="store_true", help="smoki z Blendera: wyklucie → … → stadium 8 (smok-blender1)")
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
            (sceny_blender if a.blender else sceny_walka if a.walka else sceny)(p, f)
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
