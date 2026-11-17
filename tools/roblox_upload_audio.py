#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wgranie plików audio do Roblox przez Open Cloud Assets API (assetType: Audio).

    python -B tools/roblox_upload_audio.py plan                        # co jest do wgrania i ile zostało z limitu
    python -B tools/roblox_upload_audio.py zgoda --kto "Imię" --plik <plik> [--plik <plik> …]   # zapis zgody człowieka
    python -B tools/roblox_upload_audio.py wgraj <plik> --nazwa "<nazwa w Roblox>"
    python -B tools/roblox_upload_audio.py stan                        # ponowne sprawdzenie wgranych (moderacja)

BEZPIECZNIK: `wgraj` odmawia, jeśli w assets/audio/zgoda_wgrania.json nie ma wpisu dla DOKŁADNIE tego pliku (sha256).
Wpis powstaje poleceniem `zgoda` dopiero po wyraźnym „tak” Karola albo Pawła na wgranie tych plików — zgoda na
wgrywanie modeli i materiałów nie obejmuje dźwięku. Wgranie jest nieodwracalne (plik trafia na konto i do moderacji),
a Roblox liczy wgrania: 10 na miesiąc bez weryfikacji tożsamości konta, 100 z weryfikacją.

Formaty: mp3, ogg, wav, flac; do 7 minut i 20 MB. Wynik (identyfikator zasobu, stan moderacji) trafia do
assets/audio/wgrane.json. Klucz i twórca są w .env (ROBLOX_API_KEY, ROBLOX_CREATOR_TYPE, ROBLOX_CREATOR_ID) —
nigdy ich nie wypisujemy ani nie zapisujemy do plików w repozytorium.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roblox_upload as RU  # noqa: E402  (wspólne: klucz, twórca, odczyt operacji)

ROOT = RU.ROOT
AUDIO = ROOT / "assets" / "audio"
ZGODA = AUDIO / "zgoda_wgrania.json"
WGRANE = AUDIO / "wgrane.json"
TYPY = {".mp3": "audio/mpeg", ".ogg": "audio/ogg", ".wav": "audio/wav", ".flac": "audio/flac"}
LIMIT_S = 7 * 60
LIMIT_BAJTOW = 20 * 1024 * 1024
LIMIT_MIESIAC_BEZ_WERYFIKACJI = 10


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def wzgledna(p: Path) -> str:
    return p.resolve().relative_to(ROOT).as_posix()


def wczytaj(p: Path, domyslne):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else domyslne


def zapisz(p: Path, dane) -> None:
    p.write_text(json.dumps(dane, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def dlugosc_s(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return -1.0


def problem_pliku(p: Path) -> str | None:
    if not p.exists():
        return "brak pliku"
    if p.suffix.lower() not in TYPY:
        return "nieobsługiwany format (mp3, ogg, wav, flac)"
    if p.stat().st_size > LIMIT_BAJTOW:
        return "plik większy niż 20 MB"
    d = dlugosc_s(p)
    if d <= 0:
        return "nie da się odczytać długości (ffprobe)"
    if d > LIMIT_S:
        return "dłuższy niż 7 minut"
    return None


def problem_zgody(p: Path) -> str | None:
    wpisy = wczytaj(ZGODA, {"zgody": []})["zgody"]
    rel, suma = wzgledna(p), sha256(p)
    for z in wpisy:
        if z.get("plik") == rel:
            if z.get("sha256") != suma:
                return "plik zmienił się od zapisania zgody (sha256) — potrzebna nowa zgoda"
            return None
    return "brak zgody człowieka na wgranie tego pliku (polecenie `zgoda` po wyraźnym „tak”)"


def wgrane_w_tym_miesiacu() -> int:
    teraz = dt.date.today().strftime("%Y-%m")
    return sum(1 for w in wczytaj(WGRANE, {"wgrane": []})["wgrane"] if str(w.get("kiedy", "")).startswith(teraz))


def cmd_plan(_: argparse.Namespace) -> int:
    zg = wczytaj(ZGODA, {"zgody": []})["zgody"]
    wg = {w["plik"]: w for w in wczytaj(WGRANE, {"wgrane": []})["wgrane"]}
    print("Wgrane w tym miesiącu (według rejestru): %d; limit bez weryfikacji tożsamości: %d, z weryfikacją: 100"
          % (wgrane_w_tym_miesiacu(), LIMIT_MIESIAC_BEZ_WERYFIKACJI))
    if not zg:
        print("Brak zapisanych zgód — nic nie zostanie wgrane.")
    for z in zg:
        stan = "wgrany: %s (%s)" % (wg[z["plik"]].get("assetId"), wg[z["plik"]].get("moderacja")) \
            if z["plik"] in wg else "czeka na wgranie"
        print("  %-55s zgoda: %s %s · %s" % (z["plik"], z.get("kto"), z.get("kiedy"), stan))
    return 0


def cmd_zgoda(a: argparse.Namespace) -> int:
    dane = wczytaj(ZGODA, {
        "opis": "Zgody ludzi na wgranie plików audio do Roblox. Wpis dotyczy dokładnie jednego pliku (sha256). "
                "Dodaje je tools/roblox_upload_audio.py zgoda — tylko po wyraźnym „tak” Karola albo Pawła.",
        "zgody": []})
    kiedy = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    for nazwa in a.plik:
        p = Path(nazwa)
        blad = problem_pliku(p)
        if blad:
            sys.exit("%s: %s" % (nazwa, blad))
        rel = wzgledna(p)
        dane["zgody"] = [z for z in dane["zgody"] if z.get("plik") != rel]
        dane["zgody"].append({"plik": rel, "sha256": sha256(p), "kto": a.kto, "kiedy": kiedy,
                              "dlugosc_s": round(dlugosc_s(p), 2)})
        print("Zgoda zapisana: %s (%s, %s)" % (rel, a.kto, kiedy))
    zapisz(ZGODA, dane)
    return 0


def cmd_wgraj(a: argparse.Namespace) -> int:
    p = Path(a.plik)
    blad = problem_pliku(p) or problem_zgody(p)
    if blad:
        print(json.dumps({"blad": "NIE WGRANO", "powod": blad}, ensure_ascii=False, indent=2))
        return 3
    rel = wzgledna(p)
    rejestr = wczytaj(WGRANE, {
        "opis": "Pliki audio wgrane do Roblox (tools/roblox_upload_audio.py). Identyfikatory zasobów nie są tajne.",
        "wgrane": []})
    for w in rejestr["wgrane"]:
        if w.get("plik") == rel and w.get("sha256") == sha256(p) and w.get("assetId"):
            print(json.dumps({"juz_wgrany": w}, ensure_ascii=False, indent=2))
            return 0
    ile = wgrane_w_tym_miesiacu()
    if ile >= LIMIT_MIESIAC_BEZ_WERYFIKACJI and not a.mimo_limitu:
        print(json.dumps({"blad": "NIE WGRANO", "powod": "w tym miesiącu wgrano już %d plików — limit konta bez "
                          "weryfikacji tożsamości to 10; jeśli konto jest zweryfikowane, dodaj --mimo-limitu" % ile},
                         ensure_ascii=False, indent=2))
        return 3
    zadanie = {
        "assetType": "Audio",
        "displayName": a.nazwa[:50],
        "description": a.opis or "Blocky&Crycket: dźwięk do gry",
        "creationContext": {"creator": RU.creator()},
    }
    with p.open("rb") as fh:
        r = RU.requests.post(f"{RU.API}/assets", headers=RU.headers(),
                             data={"request": json.dumps(zadanie)},
                             files={"fileContent": (p.name, fh, TYPY[p.suffix.lower()])}, timeout=300)
    if r.status_code not in (200, 202):
        print(json.dumps({"blad": r.status_code, "tresc": r.text[:800]}, ensure_ascii=False, indent=2))
        return 1
    op = r.json()
    op_id = (op.get("path") or "").split("/")[-1] or op.get("operationId")
    wynik = op
    koniec = time.time() + a.limit_czasu
    while not wynik.get("done") and time.time() < koniec:
        time.sleep(3)
        wynik = RU.get_operation(op_id)
    odp = wynik.get("response") or {}
    wpis = {
        "plik": rel,
        "sha256": sha256(p),
        "nazwa": a.nazwa[:50],
        "kiedy": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "operacja": op_id,
        "gotowe": bool(wynik.get("done")),
        "assetId": odp.get("assetId"),
        "moderacja": (odp.get("moderationResult") or {}).get("moderationState"),
    }
    rejestr["wgrane"] = [w for w in rejestr["wgrane"] if w.get("plik") != rel] + [wpis]
    zapisz(WGRANE, rejestr)
    print(json.dumps(wpis, ensure_ascii=False, indent=2))
    return 0 if wpis["assetId"] else 1


def cmd_stan(_: argparse.Namespace) -> int:
    rejestr = wczytaj(WGRANE, {"wgrane": []})
    zmiana = False
    for w in rejestr["wgrane"]:
        if w.get("operacja") and not (w.get("gotowe") and w.get("assetId")):
            wynik = RU.get_operation(w["operacja"])
            odp = wynik.get("response") or {}
            w["gotowe"] = bool(wynik.get("done"))
            w["assetId"] = odp.get("assetId") or w.get("assetId")
            w["moderacja"] = (odp.get("moderationResult") or {}).get("moderationState") or w.get("moderacja")
            zmiana = True
        print("  %-55s %s · %s" % (w["plik"], w.get("assetId"), w.get("moderacja")))
    if zmiana:
        zapisz(WGRANE, rejestr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan").set_defaults(fn=cmd_plan)
    z = sub.add_parser("zgoda")
    z.add_argument("--kto", required=True, help="imię osoby, która wyraźnie się zgodziła")
    z.add_argument("--plik", action="append", required=True)
    z.set_defaults(fn=cmd_zgoda)
    w = sub.add_parser("wgraj")
    w.add_argument("plik")
    w.add_argument("--nazwa", required=True)
    w.add_argument("--opis", default="")
    w.add_argument("--limit-czasu", type=int, default=180)
    w.add_argument("--mimo-limitu", action="store_true", help="konto ma weryfikację tożsamości (limit 100 na miesiąc)")
    w.set_defaults(fn=cmd_wgraj)
    sub.add_parser("stan").set_defaults(fn=cmd_stan)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
