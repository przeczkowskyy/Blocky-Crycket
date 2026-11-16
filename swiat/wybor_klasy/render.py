#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render sceny wyboru klasy w Blenderze: sala z czesci.json + bohaterowie (GLB) na podeście.
    python -B swiat/wybor_klasy/render.py --bohaterowie <folder z eksportem> --wyj <folder> [--przod rycerz] [--szer 1600]

<folder z eksportem>: wynik `python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/<id>.py
--wyj <folder>/<id> --eksport --bez-renderu` dla rycerz, zwiadowca, kot_mag (pliki GLB są poza repozytorium).
Wynik: <wyj>/wybor_klasy_<przod>.jpg (+ wybor_klasy.blend przy --zapisz). Blender pod wspólną blokadą (jak podglad.py).
"""
import argparse
import os
import subprocess
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
sys.path.insert(0, REPO)
from swiat.biblioteka.podglad import blender_exe, zajmij_blender, zwolnij_blender  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bohaterowie", required=True)
    ap.add_argument("--wyj", required=True)
    ap.add_argument("--przod", default="rycerz")
    ap.add_argument("--szer", default="1600")
    ap.add_argument("--probki", default="64")
    ap.add_argument("--zapisz", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.wyj, exist_ok=True)
    wyj = os.path.abspath(a.wyj)
    sala = os.path.join(wyj, "sala.blend")
    exe = blender_exe()
    blokada = zajmij_blender()
    try:
        subprocess.run([exe, "-b", "--factory-startup", "--python-exit-code", "1", "--python",
                        os.path.join(REPO, "tools", "blender", "klocki.py"), "--",
                        "--z-json", os.path.join(TU, "czesci.json"), "--zapisz", sala], check=True,
                       stdout=subprocess.DEVNULL)
        cmd = [exe, "-b", sala, "--python-exit-code", "1", "--python", os.path.join(TU, "blender_scena.py"), "--",
               "--bohaterowie", os.path.abspath(a.bohaterowie), "--wyj", os.path.join(wyj, f"wybor_klasy_{a.przod}.jpg"),
               "--przod", a.przod, "--szer", a.szer, "--probki", a.probki]
        if a.zapisz:
            cmd += ["--zapisz", os.path.join(wyj, "wybor_klasy.blend")]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        print("\n".join(l for l in (r.stdout + r.stderr).splitlines() if "SCENA" in l or "Error" in l or "Traceback" in l)[-2000:])
        sys.exit(r.returncode)
    finally:
        zwolnij_blender(blokada)


if __name__ == "__main__":
    main()
