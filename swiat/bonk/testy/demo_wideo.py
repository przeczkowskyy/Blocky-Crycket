#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Krótki film z gry BONK (etap 3, ok. 40 s, 16:9) — dla ludzi bez Studio. Plik MP4 POZA repo.

    python -B swiat/bonk/testy/demo_wideo.py <plik.mp4 poza repo> [--studio <id>] [--zostaw-klipy]

Jak: Play WYŁĄCZNIE przez tools/studio_mcp.py (znacznik próby zapisu — prawdziwe magazyny nietknięte, rekord próby
kasowany na końcu), AutoStart na czas filmu, stan profilu ustawiany haczykami próby (bez grindu). Każda scena to osobne
nagranie narzędziem MCP `video_capture` (obraz gry z Play, 30 kl./s, z dźwiękiem gry), kamera filmowa z haczyka klienta
"kamera". Klipy przycina i skleja ffmpeg (H.264 1280 × 720, AAC). W kadrze: „Player 1” zamiast nazwy konta, bez listy
graczy i czatu (wyłączone w Play).
Sceny: wejście do lasu → BONK-i z lotem → HOME RUN → zakup pałki (pałka na ramieniu, zamach) → wyklucie peta i pety za
graczem → Strażnik (tupot, pasek, lot w niebo) → otwarta brama i przejście do Bagna.
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


def v3(p):
    return "Vector3.new(%r, %r, %r)" % tuple(float(x) for x in p)


class Film:
    def __init__(self, p, kat):
        self.p, self.kat, self.klipy = p, kat, []

    def kamera(self, **k):
        czesci = []
        for n, v in k.items():
            if isinstance(v, bool):
                czesci.append("%s = %s" % (n, "true" if v else "false"))
            elif isinstance(v, (list, tuple)):
                czesci.append("%s = %s" % (n, v3(v)))
            else:
                czesci.append("%s = %r" % (n, v))
        self.p.klient('"kamera", {%s}' % ", ".join(czesci))

    def nagrywaj(self, nazwa):
        r = self.p.call("video_capture", {"is_start": True, "datamodel_type": "Client"})
        if r["is_error"]:
            raise PP.StudioError("video_capture start: %s" % r["text"][:300])
        self.biezacy = nazwa
        self.t0 = time.time()

    def stop(self, przyciecie=0.25):
        r = self.p.call("video_capture", {"is_start": False, "datamodel_type": "Client"}, timeout=300)
        try:
            w = json.loads(r["text"])
        except ValueError:
            raise PP.StudioError("video_capture stop: %s" % r["text"][:300])
        v = w["artifacts"]["video"]
        cel = os.path.join(self.kat, "%02d_%s.mp4" % (len(self.klipy) + 1, self.biezacy))
        shutil.copyfile(v, cel)
        self.klipy.append((cel, przyciecie))
        log("klip %s: %.1f s (%s)" % (self.biezacy, time.time() - self.t0, w.get("status")))


def wejdz(p):
    autostart_przed = p.luau(PP.ATR_EDIT % "true")
    p.luau(PP.ZP.kod_magazynu(None, K))
    log("Play:", p.call("start_stop_play", {"is_start": True})["text"][:80])
    PP.czekaj(lambda: p.luau(PP.GOTOWOSC, "Client") == "true true true", 90, 0.5)
    for _ in range(22):
        cz = p.luau(PP.KLASA, "Client").split()
        if len(cz) >= 3 and cz[0] == "false" and cz[1] == "Custom" and cz[2] != "nil":
            break
        p.call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": "Return"}]})
        time.sleep(1.6)
    PP.czekaj(lambda: p.klient('"stan"').get("aktywny"), 15, 0.3)
    p.luau(PP.BEZ_LISTY, "Client")
    p.serwer('"od_nowa"')
    p.serwer('"straznicy_profil", {0, 0, 0}')
    return autostart_przed


def sceny(p, f):
    K1, K2 = D["krainy"][0], D["krainy"][1]
    y = K1["start"][1]
    st = K1["start"]
    # ------------------------------------------------------------------ 1. wejście: las, nazwa krainy, pierwsza podpowiedź
    p.serwer('"kraina", 1')
    time.sleep(1.5)
    f.kamera(odl=13, wys=4.5, yaw=200, zaGraczem=True, gladko=2.2, skok=True, fov=62)
    time.sleep(0.6)
    f.nagrywaj("wejscie")
    p.klient('"kraina_napis"')
    f.kamera(odl=14, wys=5, yaw=330, zaGraczem=True, gladko=1.2)
    time.sleep(1.6)
    p.idz(st[0] + 36, y, st[2])                                       # ścieżką przez furtkę polany
    time.sleep(2.2)
    f.stop()
    # ------------------------------------------------------------------ 2. BONK-i z lotem
    slimy = PP.potwory(p, 1, "lesny_slime")
    poz = p.poz() or st
    cel = min(slimy, key=lambda m: (m["x"] - poz[0]) ** 2 + (m["z"] - poz[2]) ** 2)
    f.kamera(odl=17, wys=7, yaw=245, zaGraczem=False, gladko=2.5)
    p.idz(cel["x"], cel["y"], cel["z"])
    f.nagrywaj("bonk")
    p.klient('"trzymaj", true')
    time.sleep(2.0)
    for _ in range(2):
        slimy = PP.potwory(p, 1, "lesny_slime")
        poz = p.poz() or st
        if slimy:
            cel = min(slimy, key=lambda m: (m["x"] - poz[0]) ** 2 + (m["z"] - poz[2]) ** 2)
            p.idz(cel["x"], cel["y"], cel["z"])
        time.sleep(1.7)
    p.klient('"trzymaj", false')
    time.sleep(0.4)
    f.stop()
    # ------------------------------------------------------------------ 3. HOME RUN
    p.serwer('"moc", 1e7')
    sl = PP.potwory(p, 1, "lesny_slime")[0]
    p.przenies(sl["x"] - 5, sl["y"], sl["z"])
    f.kamera(odl=15, wys=6, yaw=235, zaGraczem=False, gladko=6, skok=True)
    time.sleep(1.0)
    f.nagrywaj("home_run")
    time.sleep(0.4)
    p.klient('"bonk"')
    f.kamera(cel=[sl["x"] + 40, sl["y"] + 18, sl["z"]], pozycja=[sl["x"] - 18, sl["y"] + 9, sl["z"] - 14], gladko=1.6)
    time.sleep(2.6)
    f.stop()
    p.serwer('"moc", 40')
    # ------------------------------------------------------------------ 4. zakup pałki: okno, BUY, pałka na ramieniu, zamach
    p.serwer('"palka", 2')
    P3 = U["palki"]["lista"][2]
    p.serwer('"monety", %d' % (P3["cena"] + 650))
    sk = D["sklepy"][0]["miejsce"]
    p.przenies(sk[0], y, sk[2] + 5)
    time.sleep(1.0)
    pz = p.poz()
    f.kamera(cel=[pz[0], pz[1] + 1.2, pz[2]], pozycja=[pz[0] + 3, pz[1] + 3.5, pz[2] + 10], gladko=8, skok=True)
    time.sleep(0.8)
    f.nagrywaj("palka")
    time.sleep(0.6)
    p.klient('"okno", "sklep"')
    time.sleep(1.6)
    p.klient('"akcja", "palka", 3')
    time.sleep(1.7)
    p.klient('"okno", nil')
    f.kamera(odl=8.5, wys=2.6, yaw=35, zaGraczem=False, gladko=3)
    time.sleep(1.4)
    p.klient('"trzymaj", true')
    time.sleep(1.1)
    p.klient('"trzymaj", false')
    time.sleep(0.6)
    f.stop()
    # ------------------------------------------------------------------ 5. jajko: wyklucie i pety za graczem
    J = D["jajka"][0]
    jm = J["miejsce"]
    p.przenies(jm[0], y, jm[2] - 6)
    p.serwer('"monety", %d' % (J["cena"] + 300))
    time.sleep(1.0)
    pz = p.poz()
    f.kamera(cel=[jm[0], pz[1] + 1, jm[2]], pozycja=[jm[0] - 6, pz[1] + 4.5, jm[2] - 14], gladko=8, skok=True)
    time.sleep(0.8)
    f.nagrywaj("jajko")
    time.sleep(0.8)
    p.klient('"akcja", "jajko", 1')
    time.sleep(4.6)
    p.serwer('"pety_profil", {lisciolis = 1, swietlikowka = 1, jelonek_gaju = 1}')
    time.sleep(0.3)
    f.kamera(odl=12, wys=4.5, yaw=245, zaGraczem=False, gladko=2.2)
    p.idz(jm[0] + 34, y, st[2] - 2)
    time.sleep(3.3)
    f.stop()
    # ------------------------------------------------------------------ 6. Strażnik: pasek u góry, tupot, lot w niebo
    S = D["straznicy"][0]
    sm = S["miejsce"]
    p.serwer('"straznik_odrodz", 1')
    g = PP.gracz(p.serwer('"stan"'))
    mn = (g.get("mnoznikPalki") or 1) * (g.get("mnoznikPetow") or 1)
    p.serwer('"moc", %d' % int(62000 / mn))
    p.przenies(sm[0] - 11, y, sm[2] + 2)
    time.sleep(1.2)
    f.kamera(cel=[sm[0] - 4, sm[1] + 6, sm[2]], pozycja=[sm[0] - 24, sm[1] + 10, sm[2] + 17], gladko=8, skok=True)
    time.sleep(0.8)
    f.nagrywaj("straznik")
    time.sleep(0.5)
    p.klient('"trzymaj", true')
    t0 = time.time()
    padl = False
    while time.time() - t0 < 14:
        s1 = (p.serwer('"stan"').get("straznicy") or [{}])[0]
        if not s1.get("zywy"):
            padl = True
            break
        pz = p.poz()                                                  # tupot odepchnął — wracamy pod Strażnika
        if pz and ((pz[0] - sm[0]) ** 2 + (pz[2] - sm[2]) ** 2) ** 0.5 > 11.5:
            p.idz(sm[0] - 10, y, sm[2] + 2)
        time.sleep(0.3)
    p.klient('"trzymaj", false')
    f.kamera(cel=[sm[0] + 20, sm[1] + 45, sm[2] - 5], pozycja=[sm[0] - 30, sm[1] + 10, sm[2] + 22], gladko=1.8)
    time.sleep(2.8)
    f.stop()
    log("Strażnik pokonany:", padl, "po %.1f s" % (time.time() - t0))
    # ------------------------------------------------------------------ 7. brama otwarta, przejście do Bagna
    p.serwer('"moc", %d' % int(K1["brama"]["wymagana"] / mn + 50))
    bx = K1["brama"]["x"]
    p.przenies(bx - 16, y, st[2])
    time.sleep(1.2)
    f.kamera(odl=12, wys=5, yaw=20, zaGraczem=True, gladko=3, skok=True)
    time.sleep(0.8)
    f.nagrywaj("brama")
    time.sleep(0.5)
    p.idz(bx + 30, y, K2["start"][2])
    time.sleep(4.2)
    f.kamera(odl=14, wys=6, yaw=160, zaGraczem=True, gladko=1.5)
    time.sleep(1.6)
    f.stop()


def sklej(klipy, wyj, kat):
    """Przycina początek każdego klipu, skaluje do 1280 × 720 (16:9, kadr przycięty), skleja; AAC 128 kb/s."""
    gotowe = []
    for i, (k, od) in enumerate(klipy):
        c = os.path.join(kat, "c%02d.mp4" % i)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.2f" % od, "-i", k,
                        "-vf", "crop=iw:trunc(iw*9/16/2)*2,scale=1280:720,fps=30,format=yuv420p",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "25", "-c:a", "aac", "-b:a", "96k", "-ar", "48000", "-ac", "2",
                        c], check=True)
        gotowe.append(c)
    lista = os.path.join(kat, "lista.txt")
    with open(lista, "w", encoding="utf-8") as f:
        for c in gotowe:
            f.write("file '%s'\n" % c.replace("\\", "/"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy",
                    "-movflags", "+faststart", wyj], check=True)


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
    kat = tempfile.mkdtemp(prefix="bonk_demo_", dir=os.path.dirname(wyj))
    PP.na_wierzch()
    with PP.Proba(a.studio) as p:
        if not p.tryb_edit():
            sys.exit("Studio nie jest w trybie Edit — nie zaczynam")
        f = Film(p, kat)
        stary = wejdz(p)
        try:
            sceny(p, f)
            try:
                p.klient('"kamera", nil')
                p.serwer('"skasuj"')
            except PP.StudioError:
                pass
        finally:
            log("Stop:", p.call("start_stop_play", {"is_start": False})["text"][:80])
            PP.czekaj(p.tryb_edit, 40, 0.5)
            p.luau(PP.ATR_EDIT % ("true" if stary == "true" else "false"))
    sklej(f.klipy, wyj, kat)
    if not a.zostaw_klipy:
        shutil.rmtree(kat, ignore_errors=True)
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", wyj],
                       capture_output=True, text=True)
    log("film:", wyj, r.stdout.replace("\n", " "))


if __name__ == "__main__":
    main()
