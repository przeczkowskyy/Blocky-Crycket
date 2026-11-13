#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Podgląd postaci / stwora / ekwipunku: moduł .py -> JSON -> Blender w tle (pod wspólną blokadą) -> rendery i raport.

    # z głównego folderu repozytorium; --wyj najlepiej poza repozytorium (rendery próbne)
    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/<id>.py --wyj <folder>
           [--klip <nazwa>] [--ikony] [--eksport] [--bez-obrysu] [--bez-renderu] [--tylko id1,id2] [--szer 900]

Moduł ma funkcję zbuduj(), która zwraca Postac, Akcesorium albo listę takich obiektów. Same akcesoria (bez postaci)
podglad zakłada na szarego manekina R15 (model „przymiarka”) — widać, jak siedzą i czy idą za animacją.

Zawsze: <id>_raport.json + raport w konsoli (trójkąty, wymiary w studach, kości, klipy, ostrzeżenia względem limitów
Roblox), <id>_plansza.jpg (bohater 3/4 z obrysem | przód z manekinem skali / bok | tył) i <id>_bohater.jpg; dla
akcesoriów też <id>_ikona.png.
  --klip X     film <id>_X.mp4 (H.264, yuv420p) + arkusz 8 klatek <id>_X_klatki.jpg (z renderu) + arkusz klatek
               odczytanych z gotowego MP4 <id>_X_z_filmu.jpg (sprawdzenie, że film się odtwarza)
  --ikony      ikony 512 px (przezroczyste PNG z obrysem) także dla postaci
  --eksport    <id>.fbx, <id>__<klip>.fbx (jeden klip na plik), <id>.glb (wszystkie klipy), <id>.blend, a potem
               KONTROLA: każdy plik wczytany z powrotem do pustego Blendera i porównany (siatki, kości, klatki,
               trójkąty, wzrost)
  --bez-obrysu kadr bohaterski i film bez komiksowego obrysu (ikony zawsze z obrysem)
  --bez-renderu tylko JSON, kontrola danych i raport
Kod wyjścia 0 = wszystko się udało.
"""
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TU)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.biblioteka.podglad import blender_exe, zajmij_blender, zwolnij_blender  # noqa: E402
from swiat.postacie.biblioteka.postac import (Akcesorium, Postac, manekin_r15, pakiet, przymiarka,  # noqa: E402
                                              zapisz_json)

SKRYPT = os.path.join(TU, "blender_postac.py")


def wczytaj_modul(sciezka):
    nazwa = "postac_" + os.path.splitext(os.path.basename(sciezka))[0]
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def uruchom_blendera(argumenty, opis):
    polecenie = [blender_exe(), "-b", "--factory-startup", "--python-exit-code", "1", "--python", SKRYPT, "--"] + argumenty
    t0 = time.time()
    r = subprocess.run(polecenie, capture_output=True, timeout=20 * 60,
                       creationflags=0x08000000 if os.name == "nt" else 0)
    wyjscie = (r.stdout + r.stderr).decode("utf-8", "replace")
    for linia in wyjscie.splitlines():
        if linia.startswith("POSTAC |"):
            print(linia)
    if r.returncode != 0:
        print("PODGLAD | %s: Blender zakończył się błędem (kod %d). Ostatnie linie:" % (opis, r.returncode))
        for linia in wyjscie.splitlines()[-30:]:
            print("   ", linia)
    else:
        print("PODGLAD | %s: %.0f s" % (opis, time.time() - t0))
    return r.returncode


def arkusz_z_filmu(ffmpeg, mp4, cel, kolumny=4, wiersze=2):
    """Odczytaj gotowy MP4 (dekodowanie ffmpeg) i ułóż równo rozłożone klatki w arkusz — dowód, że film się odtwarza."""
    ffprobe = os.path.join(os.path.dirname(ffmpeg), "ffprobe" + (".exe" if os.name == "nt" else ""))
    if not os.path.isfile(ffprobe):
        ffprobe = shutil.which("ffprobe")
    info = ""
    n = 0
    if ffprobe:
        r = subprocess.run([ffprobe, "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
                            "stream=codec_name,pix_fmt,width,height,nb_read_frames,r_frame_rate", "-of", "json", mp4],
                           capture_output=True)
        try:
            s = json.loads(r.stdout.decode("utf-8", "replace"))["streams"][0]
            n = int(s.get("nb_read_frames", 0))
            info = "%s %s %sx%s, %d klatek, %s kl./s" % (s.get("codec_name"), s.get("pix_fmt"), s.get("width"),
                                                         s.get("height"), n, s.get("r_frame_rate"))
        except (ValueError, KeyError, IndexError):
            info = "ffprobe nie odczytał strumienia"
    krok = max(1, n // (kolumny * wiersze)) if n else 4
    r = subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", mp4, "-vf",
                        "select='not(mod(n\\,%d))',scale=240:240,tile=%dx%d" % (krok, kolumny, wiersze),
                        "-frames:v", "1", "-fps_mode", "vfr", cel], capture_output=True)
    ok = r.returncode == 0 and os.path.isfile(cel)
    print("PODGLAD | film %s: %s; arkusz z dekodowanego filmu (co %d. klatka): %s"
          % (os.path.basename(mp4), info or "?", krok, cel if ok else "NIE UDAŁO SIĘ: " + r.stderr.decode("utf-8", "replace")[-300:]))
    return ok


def main():
    ap = argparse.ArgumentParser(description="Podgląd postaci / ekwipunku w Blenderze (rendery, raport, eksport)")
    ap.add_argument("--modul", required=True, help="plik .py z funkcją zbuduj()")
    ap.add_argument("--wyj", required=True, help="folder wyników (najlepiej poza repozytorium)")
    ap.add_argument("--klip", default=None, help="nazwa klipu: film MP4 + arkusz klatek")
    ap.add_argument("--ikony", action="store_true")
    ap.add_argument("--eksport", action="store_true")
    ap.add_argument("--bez-obrysu", action="store_true")
    ap.add_argument("--bez-renderu", action="store_true")
    ap.add_argument("--tylko", default="", help="tylko te id modeli (po przecinku)")
    ap.add_argument("--szer", type=int, default=900)
    ap.add_argument("--probki", type=int, default=16)
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    wyj = os.path.abspath(a.wyj)
    os.makedirs(wyj, exist_ok=True)
    t_start = time.time() - 1

    mod = wczytaj_modul(os.path.abspath(a.modul))
    if not hasattr(mod, "zbuduj"):
        raise SystemExit("Moduł %s nie ma funkcji zbuduj()." % a.modul)
    wynik = mod.zbuduj()
    obiekty = list(wynik) if isinstance(wynik, (list, tuple)) else [wynik]
    for o in obiekty:
        if not isinstance(o, (Postac, Akcesorium)):
            raise SystemExit("zbuduj() zwróciło %r — oczekuję Postac / Akcesorium (albo listy)." % (o,))
    postacie = [o for o in obiekty if isinstance(o, Postac)]
    akcesoria = [o for o in obiekty if isinstance(o, Akcesorium)]
    if akcesoria and not postacie:                             # sam ekwipunek: przymiarka na manekinie
        # id przymiarki = <moduł>_przymiarka (np. zestaw_mag_przymiarka) — ta sama nazwa pliku, folderu tekstur i .blend
        postacie = [przymiarka(os.path.splitext(os.path.basename(a.modul))[0] + "_przymiarka", akcesoria)]
    modele = postacie + akcesoria
    if a.tylko:
        chce = set(a.tylko.split(","))
        modele = [m for m in modele if m.id in chce]
    ids = [m.id for m in modele]
    if len(set(ids)) != len(ids):
        raise SystemExit("Powtórzone id modeli: %s" % ids)

    bledy = 0
    for m in modele:
        b, u = m.sprawdz()
        for x in b:
            print("PODGLAD | BŁĄD:", x)
        for x in u:
            print("PODGLAD | UWAGA:", x)
        bledy += len(b)
    if bledy:
        print("PODGLAD | %d błędów w danych — popraw moduł." % bledy)
        return 1

    zadania = {}
    for m in modele:
        z = {"render": not a.bez_renderu, "ikona": (not a.bez_renderu) and (isinstance(m, Akcesorium) or a.ikony),
             "fbx": a.eksport, "glb": a.eksport, "blend": a.eksport}
        if isinstance(m, Postac) and a.klip and not a.bez_renderu:
            if any(k.nazwa == a.klip for k in m.klipy):
                z["film"] = z["klatki"] = a.klip
            else:
                print("PODGLAD | UWAGA: %s nie ma klipu %r (ma: %s)" % (m.id, a.klip, ", ".join(k.nazwa for k in m.klipy) or "brak"))
        zadania[m.id] = z
    pak = pakiet(modele, zadania)
    man = manekin_r15("manekin_skali", "Manekin skali", klipy=False).json()["czesci"]
    for d in pak["modele"]:
        if d["rodzaj"] == "postac" and d["id"] not in ("przymiarka", "manekin"):
            d["manekin_skali"] = man
    plik = os.path.join(wyj, "pakiet_%s.json" % os.path.splitext(os.path.basename(a.modul))[0])
    zapisz_json(pak, plik)
    for d in pak["modele"]:
        if d["rodzaj"] == "postac":
            print("PODGLAD | %s „%s” (%s): %d kości, %d brył, %d akcesoriów, klipy: %s"
                  % (d["id"], d["nazwa"], d["typ"], len(d["kosci"]), len(d["czesci"]), len(d["akcesoria"]),
                     ", ".join(k["n"] for k in d["klipy"]) or "brak"))
        else:
            print("PODGLAD | %s „%s” (akcesorium %s na %s): %d brył" % (d["id"], d["nazwa"], d["typ"], d["zaczep"],
                                                                     len(d["czesci"])))
    ffmpeg = shutil.which("ffmpeg")
    argumenty = ["--json", plik, "--wyj", wyj, "--szer", str(a.szer), "--probki", str(a.probki)]
    if a.bez_obrysu:
        argumenty.append("--bez-obrysu")
    if ffmpeg:
        argumenty += ["--ffmpeg", ffmpeg]
    blokada = zajmij_blender()
    try:
        kod = uruchom_blendera(argumenty, "budowa i rendery")
        if kod == 0 and a.eksport:
            kod = uruchom_blendera(["--kontrola", os.path.join(wyj, "eksport_oczekiwane.json")], "kontrola eksportów")
    finally:
        zwolnij_blender(blokada)
    if kod == 0 and a.klip and ffmpeg and not a.bez_renderu:
        for m in modele:
            mp4 = os.path.join(wyj, "%s_%s.mp4" % (m.id, a.klip))
            if os.path.isfile(mp4):
                arkusz_z_filmu(ffmpeg, mp4, os.path.join(wyj, "%s_%s_z_filmu.jpg" % (m.id, a.klip)))
    nowe = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(wyj) for f in fs
                  if os.path.getmtime(os.path.join(dp, f)) >= t_start)
    print("PODGLAD | pliki (%d):" % len(nowe))
    for p in nowe:
        print("    %s  (%d kB)" % (p, max(1, os.path.getsize(p) // 1024)))
    return kod


if __name__ == "__main__":
    sys.exit(main())
