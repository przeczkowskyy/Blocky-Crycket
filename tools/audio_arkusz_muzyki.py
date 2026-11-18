#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arkusz muzyki: skleja kilka pętli w JEDEN plik OGG (cisza między utworami) i zapisuje mapę odcinków.

Po co: Roblox liczy wgrania audio na miesiąc, a plik może mieć do 7 minut i 20 MB. Jeden arkusz = jedno wgranie;
gra odtwarza wybrany utwór jako odcinek pliku (Sound.PlaybackRegionsEnabled + Sound.PlaybackRegion) — tak jak efekty
z tools/audio_arkusz.py. Mapa podaje dla każdego utworu dokładne granice w pliku (poczatek, koniec) oraz odcinek do
grania (graj_od, graj_do) zwężony o margines z obu stron: po przekodowaniu w Roblox czasy mogą się przesunąć o kilka–
kilkadziesiąt ms, a cisza między utworami i margines nie wpuszczą sąsiada.

    python -B tools/audio_arkusz_muzyki.py --nazwa muzyka_arkusz_b <utwór> [<utwór> …]   # buduje arkusz i mapę
    python -B tools/audio_arkusz_muzyki.py --nazwa muzyka_arkusz_b --sprawdz               # kontrola istniejącego

<utwór> = nazwa pętli z assets/audio/muzyka (np. muzyka_13_walka_petla). Źródło: bezstratna pętla
assets/audio/muzyka/oryginaly/<utwór>.flac (zapisuje ją tools/audio_petla.py --bezstratne; folder poza gitem), gdy
jest i ma tę samą długość co <utwór>.ogg; inaczej dekodowany <utwór>.ogg (drugie kodowanie stratne — narzędzie to
wypisuje i zapisuje w mapie). Wynik: assets/audio/arkusz/<nazwa>.ogg (Vorbis q6) i <nazwa>.json.
Niczego nie wgrywa. Wymaga ffmpeg i ffprobe w PATH oraz numpy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
MUZYKA = ROOT / "assets" / "audio" / "muzyka"
ARKUSZ = ROOT / "assets" / "audio" / "arkusz"
FS = 44100
KANALY = 2
CISZA_NA_BRZEGU_S = 0.5     # cisza przed pierwszym i po ostatnim utworze
CISZA_S = 1.5               # cisza między utworami
MARGINES_S = 0.05           # o tyle zwężony odcinek do grania (z każdej strony)
LIMIT_S = 7 * 60            # Roblox: audio do 7 minut
LIMIT_BAJTOW = 20 * 1024 * 1024


def dekoduj(plik: Path) -> np.ndarray:
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(plik), "-f", "s16le", "-acodec", "pcm_s16le",
                        "-ar", str(FS), "-ac", str(KANALY), "-"], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        sys.exit("ffmpeg nie odczytał %s: %s" % (plik.name, r.stderr.decode("utf-8", "replace")[:300]))
    return np.frombuffer(r.stdout, dtype="<i2").reshape(-1, KANALY)


def sha256(plik: Path) -> str:
    return hashlib.sha256(plik.read_bytes()).hexdigest()


def zrodlo_utworu(nazwa: str) -> tuple[np.ndarray, str, Path]:
    """Próbki pętli: z bezstratnego FLAC (gdy jest i zgadza się długością z OGG), inaczej z OGG."""
    ogg = MUZYKA / (nazwa + ".ogg")
    if not ogg.is_file():
        sys.exit("nie ma pliku assets/audio/muzyka/%s.ogg" % nazwa)
    x = dekoduj(ogg)
    flac = MUZYKA / "oryginaly" / (nazwa + ".flac")
    if flac.is_file():
        y = dekoduj(flac)
        if len(y) == len(x):
            return y, "flac", ogg
        print("UWAGA: %s.flac ma inną długość niż .ogg (%d ≠ %d próbek) — biorę .ogg" % (nazwa, len(y), len(x)))
    return x, "ogg", ogg


def buduj(nazwa_arkusza: str, utwory: list[str]) -> int:
    if len(set(utwory)) != len(utwory):
        sys.exit("ten sam utwór podany dwa razy")
    brzeg = np.zeros((int(CISZA_NA_BRZEGU_S * FS), KANALY), dtype="<i2")
    cisza = np.zeros((int(CISZA_S * FS), KANALY), dtype="<i2")
    kawalki, mapa, pozycja = [brzeg], {}, len(brzeg)
    for i, nazwa in enumerate(utwory):
        x, skad, ogg = zrodlo_utworu(nazwa)
        if skad == "ogg":
            print("UWAGA: %s — brak bezstratnej pętli, arkusz powstaje z pliku .ogg (drugie kodowanie stratne)" % nazwa)
        if i:
            kawalki.append(cisza)
            pozycja += len(cisza)
        poczatek, koniec = pozycja, pozycja + len(x)
        kawalki.append(x)
        pozycja = koniec
        mapa[nazwa] = {
            "poczatek": round(poczatek / FS, 4), "koniec": round(koniec / FS, 4),
            "graj_od": round(poczatek / FS + MARGINES_S, 4), "graj_do": round(koniec / FS - MARGINES_S, 4),
            "dlugosc": round(len(x) / FS, 4), "plik": "muzyka/" + ogg.name, "sha256_pliku": sha256(ogg), "zrodlo": skad,
        }
    kawalki.append(brzeg)
    dane = np.concatenate(kawalki)
    ARKUSZ.mkdir(parents=True, exist_ok=True)
    plik = ARKUSZ / (nazwa_arkusza + ".ogg")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(FS), "-ac", str(KANALY), "-i", "-",
                        "-map_metadata", "-1", "-c:a", "libvorbis", "-q:a", "6", str(plik)],
                       input=dane.tobytes(), capture_output=True)
    if r.returncode != 0:
        sys.exit("ffmpeg nie zapisał ogg: %s" % r.stderr.decode("utf-8", "replace")[:300])
    opis = {
        "opis": "Arkusz muzyki: kilka pętli w jednym pliku, odcinki w sekundach. Buduje tools/audio_arkusz_muzyki.py. "
                "poczatek / koniec = dokładne granice utworu w pliku; graj_od / graj_do = odcinek do grania "
                "(zwężony o margines na przesunięcie po przekodowaniu w Roblox).",
        "plik": plik.name,
        "sha256": sha256(plik),
        "dlugosc_s": round(len(dane) / FS, 3),
        "rozmiar_bajtow": plik.stat().st_size,
        "odstep_s": CISZA_S,
        "margines_s": MARGINES_S,
        "kolejnosc": utwory,
        "utwory": mapa,
    }
    (ARKUSZ / (nazwa_arkusza + ".json")).write_text(json.dumps(opis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Arkusz muzyki %s: %d utworów, %.1f s (%d min %02d s), %.2f MB → %s" % (
        nazwa_arkusza, len(mapa), opis["dlugosc_s"], opis["dlugosc_s"] // 60, opis["dlugosc_s"] % 60,
        plik.stat().st_size / 1024 / 1024, plik.relative_to(ROOT).as_posix()))
    return sprawdz(nazwa_arkusza)


def sprawdz(nazwa_arkusza: str) -> int:
    plik, js = ARKUSZ / (nazwa_arkusza + ".ogg"), ARKUSZ / (nazwa_arkusza + ".json")
    if not plik.exists() or not js.exists():
        print("BŁĄD: brak arkusza albo mapy %s" % nazwa_arkusza)
        return 1
    opis = json.loads(js.read_text(encoding="utf-8"))
    bledy, uwagi = [], []
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(plik)],
                       capture_output=True, text=True)
    try:
        dl = float(r.stdout.strip())
    except ValueError:
        dl = -1.0
        bledy.append("ffprobe nie podał długości")
    if dl >= LIMIT_S:
        bledy.append("arkusz ma %.1f s — Roblox przyjmuje audio do 7 minut" % dl)
    if plik.stat().st_size >= LIMIT_BAJTOW:
        bledy.append("arkusz ma %.1f MB — Roblox przyjmuje audio do 20 MB" % (plik.stat().st_size / 1024 / 1024))
    if abs(dl - opis["dlugosc_s"]) > 0.05:
        bledy.append("długość pliku %.3f s różni się od mapy %.3f s" % (dl, opis["dlugosc_s"]))
    if sha256(plik) != opis.get("sha256"):
        bledy.append("plik zmienił się od zapisania mapy (sha256)")
    dane = dekoduj(plik).astype(np.float64) / 32768.0
    poprzedni = 0.0
    for nazwa in opis["kolejnosc"]:
        u = opis["utwory"][nazwa]
        if u["poczatek"] - poprzedni < 0.4:
            bledy.append("%s: za mały odstęp od poprzedniego utworu" % nazwa)
        if not (u["poczatek"] < u["graj_od"] < u["graj_do"] < u["koniec"] <= dl + 0.01):
            bledy.append("%s: zła kolejność granic albo odcinek poza plikiem" % nazwa)
        # cisza przed utworem i tuż po nim (bez 20 ms przy granicach: kodek rozmywa brzegi)
        for a, b, gdzie in ((poprzedni, u["poczatek"], "przed"), (u["koniec"], u["koniec"] + CISZA_NA_BRZEGU_S, "po")):
            kawalek = dane[int((a + 0.02) * FS):int((b - 0.02) * FS)]
            if len(kawalek) and float(np.max(np.abs(kawalek))) > 10 ** (-60 / 20):
                bledy.append("%s: w ciszy %s utworem jest dźwięk (szczyt %.1f dBFS)" % (
                    nazwa, gdzie, 20 * np.log10(float(np.max(np.abs(kawalek))))))
        # odcinek = ten sam dźwięk co plik pętli (korelacja pierwszych i ostatnich 2 s, bez przesunięcia)
        ogg = MUZYKA / (nazwa + ".ogg")
        if not ogg.is_file():
            uwagi.append("%s: nie ma pliku pętli do porównania" % nazwa)
        elif sha256(ogg) != u.get("sha256_pliku"):
            bledy.append("%s: plik pętli zmienił się od zbudowania arkusza — zbuduj arkusz od nowa" % nazwa)
        else:
            x = dekoduj(ogg).astype(np.float64) / 32768.0
            p = int(round(u["poczatek"] * FS))
            for a, b, gdzie in ((0, 2 * FS, "początek"), (len(x) - 2 * FS, len(x), "koniec")):
                s, t = x[a:b].mean(axis=1), dane[p + a:p + b].mean(axis=1)
                if len(s) != len(t):
                    bledy.append("%s: odcinek krótszy niż pętla" % nazwa)
                    continue
                kor = float(s @ t / (np.linalg.norm(s) * np.linalg.norm(t) + 1e-12))
                if kor < 0.98:
                    bledy.append("%s: %s odcinka nie zgadza się z plikiem pętli (korelacja %.3f)" % (nazwa, gdzie, kor))
        poprzedni = u["koniec"]
    print("Kontrola arkusza muzyki %s: %d utworów, %.1f s z 420 s, %.2f MB z 20 MB, błędów: %d" % (
        nazwa_arkusza, len(opis["utwory"]), dl, plik.stat().st_size / 1024 / 1024, len(bledy)))
    for b in bledy:
        print("  BŁĄD:", b)
    for u in uwagi:
        print("  uwaga:", u)
    return 1 if bledy else 0


def main() -> int:
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("utwory", nargs="*", help="nazwy pętli z assets/audio/muzyka, w kolejności w arkuszu")
    ap.add_argument("--nazwa", required=True, help="nazwa arkusza (plik assets/audio/arkusz/<nazwa>.ogg)")
    ap.add_argument("--sprawdz", action="store_true", help="tylko kontrola istniejącego arkusza z mapą")
    a = ap.parse_args()
    if a.sprawdz:
        return sprawdz(a.nazwa)
    if not a.utwory:
        ap.error("podaj utwory albo --sprawdz")
    return buduj(a.nazwa, a.utwory)


if __name__ == "__main__":
    raise SystemExit(main())
