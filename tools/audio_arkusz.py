#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arkusz dźwięków: skleja krótkie efekty w JEDEN plik audio i zapisuje mapę odcinków.

Po co: Roblox liczy wgrania audio na miesiąc (10 bez weryfikacji tożsamości konta, 100 z weryfikacją), a efektów
walki jest 22. Jeden plik = jedno wgranie; gra odtwarza wybrany odcinek (Sound.PlaybackRegionsEnabled +
Sound.PlaybackRegion). Między efektami jest cisza, żeby drobne przesunięcie po przekodowaniu nie wpuściło sąsiada.

    python -B tools/audio_arkusz.py                 # wariant A wszystkich efektów → assets/audio/arkusz/
    python -B tools/audio_arkusz.py --wariant b     # wariant B
    python -B tools/audio_arkusz.py --sprawdz       # tylko kontrola istniejącego arkusza z mapą

Wynik: assets/audio/arkusz/sfx_arkusz_<wariant>.ogg i .json (mapa: nazwa → początek i koniec w sekundach).
Niczego nie wgrywa. Wymaga ffmpeg i ffprobe w PATH.
Arkusz MUZYKI (kilka pętli w jednym pliku, ta sama zasada) buduje osobne narzędzie: tools/audio_arkusz_muzyki.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DZWIEKI = ROOT / "assets" / "audio" / "dzwieki"
ARKUSZ = ROOT / "assets" / "audio" / "arkusz"
CZESTOTLIWOSC = 44100
KANALY = 2
CISZA_S = 0.35          # odstęp między efektami
CISZA_NA_POCZATKU_S = 0.25
LIMIT_S = 7 * 60        # Roblox: audio do 7 minut
LIMIT_BAJTOW = 20 * 1024 * 1024


def pcm(plik: Path) -> bytes:
    """Dekoduje plik do surowych próbek s16le, 44,1 kHz, stereo."""
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(plik), "-f", "s16le", "-acodec", "pcm_s16le",
         "-ar", str(CZESTOTLIWOSC), "-ac", str(KANALY), "-"],
        capture_output=True)
    if r.returncode != 0 or not r.stdout:
        sys.exit("ffmpeg nie odczytał %s: %s" % (plik.name, r.stderr.decode("utf-8", "replace")[:300]))
    return r.stdout


def uderzenie(probki: bytes) -> tuple[float, float]:
    """Zwraca (atak, szczyt) w sekundach od początku efektu: atak = pierwsze okno 10 ms głośniejsze niż ćwierć
    najgłośniejszego, szczyt = najgłośniejsze okno. Gra ustawia szczyt na klatkę trafienia (część efektów ma długi
    narastający wstęp, np. świst przed „łup”)."""
    import array
    a = array.array("h")
    a.frombytes(probki)
    okno = (CZESTOTLIWOSC // 100) * KANALY
    poziomy = [sum(abs(x) for x in a[i:i + okno]) / okno for i in range(0, max(len(a) - okno, 1), okno)]
    if not poziomy or max(poziomy) <= 0:
        return 0.0, 0.0
    najwiecej = max(poziomy)
    szczyt = poziomy.index(najwiecej)
    atak = next(i for i, p in enumerate(poziomy) if p >= 0.25 * najwiecej)
    return round(atak * 0.01, 2), round(szczyt * 0.01, 2)


def pliki_wariantu(wariant: str) -> list[Path]:
    wszystkie = sorted(DZWIEKI.glob("sfx_*.wav"))
    if wariant == "a":
        return [p for p in wszystkie if not p.stem.endswith("_b")]
    return [p for p in wszystkie if p.stem.endswith("_b")]


def nazwa_efektu(plik: Path) -> str:
    return plik.stem[:-2] if plik.stem.endswith("_b") else plik.stem


def buduj(wariant: str) -> int:
    pliki = pliki_wariantu(wariant)
    if not pliki:
        sys.exit("Brak plików sfx_*.wav wariantu %s w %s" % (wariant.upper(), DZWIEKI.relative_to(ROOT)))
    ramka = 2 * KANALY                                   # bajtów na próbkę stereo
    cisza = b"\x00" * (int(CISZA_S * CZESTOTLIWOSC) * ramka)
    dane = bytearray(b"\x00" * (int(CISZA_NA_POCZATKU_S * CZESTOTLIWOSC) * ramka))
    mapa = {}
    for p in pliki:
        probki = pcm(p)
        probki = probki[: len(probki) - len(probki) % ramka]
        poczatek = len(dane) // ramka
        dane += probki
        koniec = len(dane) // ramka
        atak, szczyt = uderzenie(probki)
        mapa[nazwa_efektu(p)] = {
            "poczatek": round(poczatek / CZESTOTLIWOSC, 4),
            "koniec": round(koniec / CZESTOTLIWOSC, 4),
            "atak": atak,
            "szczyt": szczyt,
            "plik": p.name,
        }
        dane += cisza
    ARKUSZ.mkdir(parents=True, exist_ok=True)
    wav = ARKUSZ / ("sfx_arkusz_%s.wav" % wariant)
    ogg = ARKUSZ / ("sfx_arkusz_%s.ogg" % wariant)
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(KANALY)
        w.setsampwidth(2)
        w.setframerate(CZESTOTLIWOSC)
        w.writeframes(bytes(dane))
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-c:a", "libvorbis", "-q:a", "6", str(ogg)],
                       capture_output=True)
    wav.unlink()
    if r.returncode != 0:
        sys.exit("ffmpeg nie zapisał ogg: %s" % r.stderr.decode("utf-8", "replace")[:300])
    dlugosc = len(dane) / ramka / CZESTOTLIWOSC
    opis = {
        "opis": "Arkusz efektów dźwiękowych: jeden plik, odcinki w sekundach. Buduje tools/audio_arkusz.py.",
        "wariant": wariant.upper(),
        "plik": ogg.name,
        "sha256": hashlib.sha256(ogg.read_bytes()).hexdigest(),
        "dlugosc_s": round(dlugosc, 3),
        "odstep_s": CISZA_S,
        "efekty": mapa,
    }
    (ARKUSZ / ("sfx_arkusz_%s.json" % wariant)).write_text(
        json.dumps(opis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Arkusz %s: %d efektów, %.1f s, %.0f kB → %s" % (
        wariant.upper(), len(mapa), dlugosc, ogg.stat().st_size / 1024, ogg.relative_to(ROOT).as_posix()))
    return sprawdz(wariant)


def sprawdz(wariant: str) -> int:
    ogg = ARKUSZ / ("sfx_arkusz_%s.ogg" % wariant)
    js = ARKUSZ / ("sfx_arkusz_%s.json" % wariant)
    if not ogg.exists() or not js.exists():
        print("BŁĄD: brak arkusza albo mapy wariantu %s" % wariant.upper())
        return 1
    opis = json.loads(js.read_text(encoding="utf-8"))
    bledy = []
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ogg)],
                       capture_output=True, text=True)
    try:
        dl = float(r.stdout.strip())
    except ValueError:
        dl = -1.0
        bledy.append("ffprobe nie podał długości")
    if dl > LIMIT_S:
        bledy.append("arkusz dłuższy niż 7 minut (%.1f s)" % dl)
    if ogg.stat().st_size > LIMIT_BAJTOW:
        bledy.append("arkusz większy niż 20 MB")
    if abs(dl - opis["dlugosc_s"]) > 0.05:
        bledy.append("długość pliku %.3f s różni się od mapy %.3f s" % (dl, opis["dlugosc_s"]))
    if hashlib.sha256(ogg.read_bytes()).hexdigest() != opis.get("sha256"):
        bledy.append("plik zmienił się od zapisania mapy (sha256)")
    poprzedni_koniec = 0.0
    for nazwa, e in sorted(opis["efekty"].items(), key=lambda kv: kv[1]["poczatek"]):
        if e["poczatek"] - poprzedni_koniec < 0.2:
            bledy.append("%s: za mały odstęp od poprzedniego efektu" % nazwa)
        if e["koniec"] <= e["poczatek"]:
            bledy.append("%s: pusty odcinek" % nazwa)
        if e["koniec"] > dl + 0.01:
            bledy.append("%s: odcinek wychodzi poza plik" % nazwa)
        poprzedni_koniec = e["koniec"]
    print("Kontrola arkusza %s: %d efektów, %.1f s, błędów: %d" % (
        wariant.upper(), len(opis["efekty"]), dl, len(bledy)))
    for b in bledy:
        print("  BŁĄD:", b)
    return 1 if bledy else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--wariant", choices=["a", "b"], default="a")
    ap.add_argument("--sprawdz", action="store_true")
    a = ap.parse_args()
    return sprawdz(a.wariant) if a.sprawdz else buduj(a.wariant)


if __name__ == "__main__":
    raise SystemExit(main())
