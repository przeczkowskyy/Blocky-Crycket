#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Podgląd budynku albo całej mapy z klocków: generuje czesci.json, sprawdza jakość i renderuje kadry w Blenderze.

    # jeden budynek (moduł z funkcją buduj(s, rnd)) — stanie na podłożu, z ludzikiem wzrostu gracza dla skali
    python swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/karczma.py --wyj <folder>

    # gotowy plik części (np. cała mapa)
    python swiat/biblioteka/podglad.py --json swiat/krzywe_miasteczko/czesci.json --wyj <folder> --ujecia <ujecia.json>

Opcje: --szer 1100 (szerokość kadru w pikselach), --swiatlo slonce|studio (studio = płaskie, szare światło domyślnego
miejsca Roblox), --tylko a,d (wybrane kadry auto: a_przod34, b_tyl34, c_bok, d_oczy, e_gora), --probki 32,
--ujecia <plik.json> + --przesun x,y,z (własne ujęcia w układzie mapy i przesunięcie mapy w świecie),
--bez-renderu (tylko JSON i kontrola jakości), --paleta <plik.py z PALETA> (domyślnie paleta.py dwa foldery nad modułem).

Blender działa w tle (bez okna); rendery są ustawiane w kolejce blokadą pliku, więc wielu autorów może wołać to naraz.
Wynik: lista plików JPG w --wyj, ostrzeżenia kontroli jakości, liczba części. Kod wyjścia 0 = wszystko się udało.
"""
import argparse
import glob
import importlib.util
import json
import math
import os
import random
import shutil
import subprocess
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.biblioteka.scena import Scena  # noqa: E402

KLOCKI = os.path.join(REPO, "tools", "blender", "klocki.py")
LIMIT_CZEKANIA_S = 25 * 60
STARA_BLOKADA_S = 12 * 60


def blender_exe():
    env = os.environ.get("BLENDER_EXE")
    if env and os.path.isfile(env):
        return env
    w = shutil.which("blender")
    if w:
        return w
    kandydaci = sorted(glob.glob(r"C:\Program Files\Blender Foundation\Blender *\blender.exe"), reverse=True)
    if kandydaci:
        return kandydaci[0]
    raise SystemExit("Nie znalazłem Blendera. Ustaw zmienną BLENDER_EXE na pełną ścieżkę do blender.exe.")


def _plik_blokady():
    root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    kat = os.path.join(root, "BlockyCrycket")
    os.makedirs(kat, exist_ok=True)
    return os.path.join(kat, "blender.lock")


def zajmij_blender():
    """Jedna instancja Blendera naraz (mało pamięci i jedna karta graficzna). Zwraca ścieżkę blokady."""
    sciezka, start = _plik_blokady(), time.time()
    while True:
        try:
            fd = os.open(sciezka, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, ("%d %d" % (os.getpid(), int(time.time()))).encode("ascii"))
            os.close(fd)
            return sciezka
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(sciezka) > STARA_BLOKADA_S:
                    os.remove(sciezka)                         # porzucona blokada (proces padł)
                    continue
            except OSError:
                pass
            if time.time() - start > LIMIT_CZEKANIA_S:
                raise SystemExit("Blender jest zajęty zbyt długo (blokada %s)." % sciezka)
            time.sleep(1.5)


def zwolnij_blender(sciezka):
    try:
        os.remove(sciezka)
    except OSError:
        pass


def wczytaj_modul(sciezka):
    nazwa = "podglad_" + os.path.splitext(os.path.basename(sciezka))[0]
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def wczytaj_palete(sciezka_modulu, jawna=None):
    kandydaci = [jawna] if jawna else [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(sciezka_modulu))), "paleta.py"),
                                       os.path.join(os.path.dirname(os.path.abspath(sciezka_modulu)), "paleta.py")]
    for k in kandydaci:
        if k and os.path.isfile(k):
            return dict(getattr(wczytaj_modul(k), "PALETA"))
    return {}


def ludzik(s, x, z):
    """Postać odniesienia wzrostu gracza R15 (ok. 5,3 studa) — żeby od razu widać było skalę drzwi, okien i szyldów."""
    with s.uklad(pos=(x, 0, z), grupa="_Ludzik"):
        s.blok("Nogi", (0, 1.0, 0), (1.9, 2.0, 0.95), "2F5FB5")
        s.blok("Tułów", (0, 3.0, 0), (2.0, 2.0, 1.0), "E23B3B")
        s.blok("Ręka L", (-1.5, 3.0, 0), (0.95, 2.0, 0.95), "F2C79B")
        s.blok("Ręka P", (1.5, 3.0, 0), (0.95, 2.0, 0.95), "F2C79B")
        s.blok("Głowa", (0, 4.65, 0), (1.25, 1.25, 1.25), "F2C79B")


def scena_z_modulu(sciezka, paleta, ziarno):
    mod = wczytaj_modul(sciezka)
    if not hasattr(mod, "buduj"):
        raise SystemExit("Moduł %s nie ma funkcji buduj(s, rnd)." % sciezka)
    nazwa = getattr(mod, "NAZWA", os.path.splitext(os.path.basename(sciezka))[0].title().replace("_", ""))
    s = Scena("Workspace/Podglad", paleta=paleta)
    with s.uklad(grupa=nazwa):
        mod.buduj(s, random.Random(ziarno))
    st = s.statystyki()
    if not st["zakres"]:
        raise SystemExit("Moduł %s nie dodał żadnej części." % sciezka)
    mn, mx = st["zakres"]["min"], st["zakres"]["max"]
    szer, gl = mx[0] - mn[0], mx[2] - mn[2]
    with s.grupa("_Podloze"):
        s.walec("Podłoże", ((mn[0] + mx[0]) / 2.0, -0.5, (mn[2] + mx[2]) / 2.0), math.hypot(szer, gl) / 2.0 + 12, 1.0, "79C95A", "Grass", "y")
    ludzik(s, min(mx[0] - 2.0, 5.0), mx[2] + 4.0)
    return s, nazwa


def main():
    ap = argparse.ArgumentParser(description="Podgląd budynku / mapy z klocków (JSON + kontrola + rendery Blendera)")
    ap.add_argument("--modul", help="plik .py budynku z funkcją buduj(s, rnd)")
    ap.add_argument("--json", help="gotowy czesci.json")
    ap.add_argument("--wyj", required=True, help="folder na rendery (bezwzględny albo względem bieżącego)")
    ap.add_argument("--paleta", default=None)
    ap.add_argument("--ziarno", type=int, default=7)
    ap.add_argument("--szer", type=int, default=1100)
    ap.add_argument("--probki", type=int, default=32)
    ap.add_argument("--swiatlo", choices=("slonce", "studio"), default="slonce")
    ap.add_argument("--tylko", default="")
    ap.add_argument("--ujecia", default=None, help="plik JSON z własnymi ujęciami (zamiast kadrów auto)")
    ap.add_argument("--przesun", default="0,0,0", help="przesunięcie mapy w świecie x,y,z — dodawane do ujęć z pliku (są w układzie mapy)")
    ap.add_argument("--zapisz-blend", default=None, help="zapisz też scenę Blendera do tego pliku")
    ap.add_argument("--bez-renderu", action="store_true")
    ap.add_argument("--limit-czesci", type=int, default=None)
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    wyj = os.path.abspath(a.wyj)
    os.makedirs(wyj, exist_ok=True)

    if a.modul:
        s, nazwa = scena_z_modulu(os.path.abspath(a.modul), wczytaj_palete(a.modul, a.paleta), a.ziarno)
        plik_json = os.path.join(wyj, "czesci.json")
        s.zapisz(plik_json)
        st = s.statystyki(pomin_podkreslone=True)
        mn, mx = st["zakres"]["min"], st["zakres"]["max"]
        print("PODGLAD | %s: %d części; wymiary %.1f (X) × %.1f (Y) × %.1f (Z) studów; zakres %s … %s"
              % (nazwa, st["czesci"], mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2], mn, mx))
        for u in s.sprawdz(limit_czesci=a.limit_czesci):
            print("PODGLAD | UWAGA:", u)
    elif a.json:
        plik_json = os.path.abspath(a.json)
        with open(plik_json, encoding="utf-8") as f:
            print("PODGLAD | %s: %d części" % (os.path.basename(plik_json), len(json.load(f)["czesci"])))
    else:
        raise SystemExit("Podaj --modul albo --json.")
    if a.bez_renderu:
        return 0

    polecenie = [blender_exe(), "-b", "--factory-startup", "--python-exit-code", "1", "--python", KLOCKI, "--",
                 "--z-json", plik_json, "--render", wyj, "--szer", str(a.szer), "--probki", str(a.probki), "--swiatlo", a.swiatlo]
    if a.ujecia:
        polecenie += ["--ujecia", os.path.abspath(a.ujecia), "--przesun", a.przesun]
    else:
        polecenie += ["--auto"]
    if a.tylko:
        polecenie += ["--tylko", a.tylko]
    if a.zapisz_blend:
        polecenie += ["--zapisz", os.path.abspath(a.zapisz_blend)]
    blokada = zajmij_blender()
    t0 = time.time()
    try:
        r = subprocess.run(polecenie, capture_output=True, timeout=20 * 60,
                           creationflags=0x08000000 if os.name == "nt" else 0)
    finally:
        zwolnij_blender(blokada)
    wyjscie = (r.stdout + r.stderr).decode("utf-8", "replace")
    for linia in wyjscie.splitlines():
        if linia.startswith("KLOCKI |"):
            print(linia)
    if r.returncode != 0:
        print("PODGLAD | Blender zakończył się błędem (kod %d). Ostatnie linie:" % r.returncode)
        for linia in wyjscie.splitlines()[-25:]:
            print("   ", linia)
        return 1
    print("PODGLAD | gotowe w %.0f s -> %s" % (time.time() - t0, wyj))
    return 0


if __name__ == "__main__":
    sys.exit(main())
