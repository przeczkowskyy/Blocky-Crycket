#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migawka świata gry z otwartego Roblox Studio — bez uruchomionego panelu (dla agentów i z terminala).

    python panel/narzedzia/migawka.py --tytul "Karczma po poprawkach" [--opis "..."]
        [--korzen Workspace/DemoLesnaBaza] [--bez-zrzutow] [--kto "Claude (Karol)"] [--json]

Zapisuje panel/dane/podglad/<id>/ (meta.json, czesci.json, zrzut_N.jpg) i wypisuje id migawki oraz ścieżkę.
Id można podać raportowi: python panel/narzedzia/raport.py dodaj … --migawka <id>.
Z Studio tylko CZYTA (eksport części + zrzuty ekranu; kamera na chwilę się przestawia i wraca).
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import contextlib  # noqa: E402

from bc import podglad, rdzen  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402

_log_oryginalny = rdzen.log


def _log_na_stderr(*czesci):
    """Log panelu idzie do pliku i na stderr — stdout zostaje czysty (pierwsza linia = id, --json = sam JSON)."""
    with contextlib.redirect_stdout(sys.stderr):
        _log_oryginalny(*czesci)


rdzen.log = _log_na_stderr


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Migawka świata gry z Roblox Studio (podgląd 3D panelu)")
    ap.add_argument("--tytul", required=True, help="krótki tytuł migawki")
    ap.add_argument("--opis", default="", help="co widać / co się zmieniło")
    ap.add_argument("--korzen", default="Workspace", help="np. Workspace/DemoLesnaBaza (domyślnie cały Workspace)")
    ap.add_argument("--bez-zrzutow", action="store_true", help="tylko części, bez zrzutów ekranu")
    ap.add_argument("--kto", default=None, help='autor, np. "Claude (Karol)" (domyślnie git user.name)')
    ap.add_argument("--json", action="store_true", help="wypisz całe meta jako JSON")
    a = ap.parse_args()
    try:
        meta = podglad.zrob_migawke(a.tytul, a.opis, a.kto or rdzen.git_uzytkownik(), zrzuty=not a.bez_zrzutow,
                                    korzen=a.korzen)
    except BladHTTP as e:
        print("BŁĄD: %s" % e.komunikat, file=sys.stderr)
        return 1
    finally:
        try:
            from bc import studio
            studio._zamknij_sesje()                         # zamknij mostek MCP od razu
        except Exception:
            pass
    folder = os.path.normpath(os.path.join(podglad.katalog_podgladu(), meta["id"]))
    if a.json:
        print(json.dumps(dict(meta, folder=folder), ensure_ascii=False, indent=1))
    else:
        print(meta["id"])
        print(folder)
        print("części: %d, grup: %d, zrzutów: %d" % (meta["czesci"], len(meta["grupy"]), len(meta["zrzuty"])))
        for u in meta.get("uwagi") or []:
            print("uwaga: %s" % u)
    return 0


if __name__ == "__main__":
    sys.exit(main())
