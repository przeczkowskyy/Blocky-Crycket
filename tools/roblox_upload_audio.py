#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wgranie plików audio do Roblox przez Open Cloud Assets API (assetType: Audio).

    python -B tools/roblox_upload_audio.py plan                        # co jest do wgrania i ile zostało z limitu
    python -B tools/roblox_upload_audio.py zgoda --kto "Imię" --plik <plik> [--plik <plik> …]   # zapis zgody człowieka
    python -B tools/roblox_upload_audio.py wgraj <plik> --nazwa "<nazwa w Roblox>"
    python -B tools/roblox_upload_audio.py wgraj-studio <plik> --nazwa "<nazwa>" [--poczekalnia]   # przez Studio, bez klucza
    python -B tools/roblox_upload_audio.py stan                        # ponowne sprawdzenie wgranych (moderacja)

BEZPIECZNIK: `wgraj` odmawia, jeśli w assets/audio/zgoda_wgrania.json nie ma wpisu dla DOKŁADNIE tego pliku (sha256).
Wpis powstaje poleceniem `zgoda` dopiero po wyraźnym „tak” Karola albo Pawła na wgranie tych plików — zgoda na
wgrywanie modeli i materiałów nie obejmuje dźwięku. Wgranie jest nieodwracalne (plik trafia na konto i do moderacji),
a Roblox liczy wgrania: 10 na miesiąc bez weryfikacji tożsamości konta, 100 z weryfikacją.

Dwie drogi: `wgraj` używa klucza Open Cloud z .env, `wgraj-studio` idzie przez Roblox Studio na konto osoby w nim
zalogowanej (tak wgrywane są modele; Studio przyjmuje pliki tylko z folderów zatwierdzonych przez człowieka).
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


KTO_LUAU = r'''
local SS = game:GetService("StudioService")
return game:GetService("HttpService"):JSONEncode({
	placeId = game.PlaceId,
	userId = SS:GetUserId(),
	tenSamTworca = game.CreatorType == Enum.CreatorType.User and game.CreatorId == SS:GetUserId(),
	tworcaGry = tostring(game.CreatorType),
})
'''


def bez_liczb(tekst: str) -> str:
    """Odpowiedź usługi do pokazania na ekranie: bez długich liczb (identyfikatory kont i zasobów)."""
    import re
    return re.sub(r"\d{6,}", "<liczba>", str(tekst or ""))[:400]


def cmd_wgraj_studio(a: argparse.Namespace) -> int:
    """Wgranie przez Roblox Studio (narzędzie MCP open_cloud_invoke) — bez klucza w .env, na konto osoby zalogowanej
    w Studio; tak samo wgrywane są modele (swiat/postacie/roblox_import.py). Studio przyjmuje pliki tylko z folderów
    zatwierdzonych przez człowieka (Assistant → Settings → MCP Permissions → approved upload directories). Opcja
    --poczekalnia kopiuje plik na czas wgrania do zatwierdzonego folderu wyników postaci i usuwa kopię po wgraniu —
    używać jej tylko dla plików, na których wgranie człowiek wyraźnie się zgodził (wpis `zgoda`)."""
    import shutil
    p = Path(a.plik)
    blad = problem_pliku(p) or problem_zgody(p)
    if blad:
        print(json.dumps({"blad": "NIE WGRANO", "powod": blad}, ensure_ascii=False, indent=2))
        return 3
    rel, suma = wzgledna(p), sha256(p)
    rejestr = wczytaj(WGRANE, {
        "opis": "Pliki audio wgrane do Roblox (tools/roblox_upload_audio.py). Identyfikatory zasobów nie są tajne.",
        "wgrane": []})
    for w in rejestr["wgrane"]:
        if w.get("plik") == rel and w.get("sha256") == suma:
            if w.get("assetId"):
                print(json.dumps({"juz_wgrany": w}, ensure_ascii=False, indent=2))
                return 0
            if w.get("etap") in ("wysylanie", "nieznane", "operacja") and not a.mimo_nieznanego:
                print(json.dumps({"blad": "NIE WGRANO", "powod": "poprzednia próba wgrania tego pliku skończyła się "
                                  "w stanie „%s” — nie wiadomo, czy zasób powstał. Sprawdź Creator Dashboard albo "
                                  "polecenie `stan`; świadome ponowienie: --mimo-nieznanego" % w.get("etap")},
                                 ensure_ascii=False, indent=2))
                return 3
    ile = wgrane_w_tym_miesiacu()
    if ile >= LIMIT_MIESIAC_BEZ_WERYFIKACJI and not a.mimo_limitu:
        print(json.dumps({"blad": "NIE WGRANO", "powod": "w tym miesiącu wgrano już %d plików (limit bez weryfikacji "
                          "tożsamości: 10); jeśli konto jest zweryfikowane, dodaj --mimo-limitu" % ile},
                         ensure_ascii=False, indent=2))
        return 3

    sys.path.insert(0, str(ROOT / "swiat" / "postacie"))
    import roblox_import as RI  # noqa: E402  (rozbiór odpowiedzi Open Cloud, ten sam co przy modelach)
    from studio_mcp import StudioMCP, StudioError, first_studio_id  # noqa: E402

    def zapisz_wpis(**pola):
        wpis = {"plik": rel, "sha256": suma, "nazwa": a.nazwa[:50], "droga": "studio",
                "kiedy": dt.datetime.now().strftime("%Y-%m-%d %H:%M")}
        wpis.update(pola)
        rejestr["wgrane"] = [w for w in rejestr["wgrane"] if w.get("plik") != rel] + [wpis]
        zapisz(WGRANE, rejestr)
        return wpis

    zrodlo, kopia = p.resolve(), None
    if a.poczekalnia:
        folder = ROOT / "swiat" / "postacie" / "wynik" / "_audio"
        folder.mkdir(parents=True, exist_ok=True)
        kopia = folder / p.name
        shutil.copyfile(zrodlo, kopia)
        zrodlo = kopia
    try:
        with StudioMCP() as s:
            sid = first_studio_id(s)
            if not sid:
                sys.exit("Roblox Studio nie jest podłączone.")
            r = None
            for model_danych in ("Edit", "Server"):       # w trybie Play model Edit jest niedostępny
                r = s.call("execute_luau", {"code": KTO_LUAU, "datamodel_type": model_danych, "studio_id": sid},
                           timeout=120)
                if not r["is_error"]:
                    break
            if r["is_error"]:
                sys.exit("Studio nie odpowiedziało na pytanie o konto: %s" % bez_liczb(r["text"]))
            kto = json.loads(r["text"])
            if kto["placeId"] != RI.PLACE_ID:
                sys.exit("To nie jest miejsce gry — nic nie wysłano.")
            print("konto: zasób trafi na konto osoby zalogowanej w Studio; właściciel gry to ta sama osoba: %s (%s)"
                  % ("tak" if kto["tenSamTworca"] else "NIE", kto["tworcaGry"].replace("Enum.CreatorType.", "")))

            def chmura(metoda, endpoint, body=None, files=None, scopes=("asset:read",)):
                arg = {"method": metoda, "endpoint": endpoint, "scopes": list(scopes), "studio_id": sid}
                if body is not None:
                    arg["body"] = json.dumps(body)
                if files:
                    arg["files"] = files
                wynik = s.call("open_cloud_invoke", arg, timeout=300)
                tekst = wynik["text"] or ""
                kod, dane = RI.rozbierz_odpowiedz(tekst)
                return kod, dane, tekst, bool(wynik["is_error"])

            zapisz_wpis(etap="wysylanie")                      # BEZ tego zapisu nie wysyłamy
            kod, dane, tekst, blad_post, wyjatek = 0, None, "", False, None
            try:
                kod, dane, tekst, blad_post = chmura("POST", "/assets/v1/assets", {"request": {
                    "assetType": "Audio", "displayName": a.nazwa[:50], "description": a.opis or "Dźwięk do gry.",
                    "creationContext": {"creator": {"userId": str(kto["userId"])}}}},
                    files=[{"name": "fileContent", "path": str(zrodlo)}], scopes=("asset:read", "asset:write"))
            except StudioError as e:
                wyjatek = e
            etap, op, opis = RI.ocen_wyslanie(kod, dane, tekst, wyjatek, blad_post)
            if etap == "nie_wyslano":
                rejestr["wgrane"] = [w for w in rejestr["wgrane"] if w.get("plik") != rel]
                zapisz(WGRANE, rejestr)
                print(json.dumps({"blad": "NIE WGRANO", "powod": "Studio odrzuciło plik: folder nie jest zatwierdzony do "
                                  "wgrywania (approved upload directories). Nic nie wysłano."}, ensure_ascii=False, indent=2))
                return 4
            if etap == "odrzucone_zadanie":
                zapisz_wpis(etap=etap, kod_http=kod)
                print(json.dumps({"blad": "ODRZUCONE", "kod_http": kod, "odpowiedz": bez_liczb(tekst)},
                                 ensure_ascii=False, indent=2))
                return 1
            if etap != "operacja":
                zapisz_wpis(etap="nieznane", kod_http=kod)
                print(json.dumps({"blad": "STAN NIEZNANY", "opis": opis, "odpowiedz": bez_liczb(tekst or wyjatek)},
                                 ensure_ascii=False, indent=2))
                return 2
            wpis = zapisz_wpis(etap="operacja", operacja=op)
            koniec = time.time() + a.limit_czasu
            stan = {"gotowe": False, "asset": "", "moderacja": "", "blad": None}
            while time.time() < koniec:
                kod, dane, tekst, _ = chmura("GET", "/assets/v1/operations/%s" % op)
                stan = RI.wynik_operacji(dane)
                if stan["gotowe"] or stan["blad"]:
                    break
                time.sleep(4)
            wpis = zapisz_wpis(etap="gotowe" if stan["asset"] else ("blad" if stan["blad"] else "operacja"),
                               operacja=op, gotowe=bool(stan["gotowe"]), assetId=stan["asset"] or None,
                               moderacja=stan["moderacja"] or None,
                               blad=bez_liczb(json.dumps(stan["blad"], ensure_ascii=False)) if stan["blad"] else None)
            print(json.dumps(wpis, ensure_ascii=False, indent=2))
            return 0 if wpis.get("assetId") else 1
    finally:
        if kopia is not None:
            try:
                kopia.unlink()
                kopia.parent.rmdir()
            except OSError:
                pass


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
    ws = sub.add_parser("wgraj-studio", help="wgranie przez Roblox Studio (bez klucza w .env)")
    ws.add_argument("plik")
    ws.add_argument("--nazwa", required=True)
    ws.add_argument("--opis", default="")
    ws.add_argument("--limit-czasu", type=int, default=240)
    ws.add_argument("--poczekalnia", action="store_true",
                    help="skopiuj plik na czas wgrania do zatwierdzonego folderu wyników postaci")
    ws.add_argument("--mimo-limitu", action="store_true", help="konto ma weryfikację tożsamości (limit 100 na miesiąc)")
    ws.add_argument("--mimo-nieznanego", action="store_true",
                    help="ponów mimo poprzedniej próby o nieznanym wyniku (może powstać drugi zasób)")
    ws.set_defaults(fn=cmd_wgraj_studio)
    sub.add_parser("stan").set_defaults(fn=cmd_stan)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
