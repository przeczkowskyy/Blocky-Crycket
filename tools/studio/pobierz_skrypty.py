#!/usr/bin/env python3
"""Pobiera źródła skryptów z otwartego Studio do porównania z plikami repozytorium (Studio bywa nowsze niż dysk,
gdy ktoś poprawił skrypt wprost w Studio albo wgrał go z drugiego komputera).

    python tools/studio/pobierz_skrypty.py MistrzGier3DClient KotRasySwiatClient        # klient -> build/studio_zrodla/
    python tools/studio/pobierz_skrypty.py --serwer MistrzGier                          # ServerScriptService.Server
    python tools/studio/pobierz_skrypty.py MistrzGier3DClient --zapisz                  # nadpisz plik w src/ wersją ze Studio

Bez --zapisz niczego w src/ nie zmienia: zapisuje kopię i wypisuje, czy różni się od pliku na dysku.
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from studio_mcp import StudioMCP, first_studio_id  # noqa: E402

KAWALEK = 40000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nazwy", nargs="+")
    ap.add_argument("--serwer", action="store_true")
    ap.add_argument("--zapisz", action="store_true")
    a = ap.parse_args()
    rodzic = ('game:GetService("ServerScriptService"):WaitForChild("Server")' if a.serwer else
              'game:GetService("StarterPlayer").StarterPlayerScripts:WaitForChild("Client")')
    wyj = os.path.join(ROOT, "build", "studio_zrodla")
    os.makedirs(wyj, exist_ok=True)
    with StudioMCP() as s:
        sid = first_studio_id(s)
        for n in a.nazwy:
            czesci, i = [], 0
            while True:
                kod = ('local sk = %s:FindFirstChild("%s") if not sk then return "\\0BRAK" end '
                       'return string.sub(sk.Source, %d, %d)' % (rodzic, n, i * KAWALEK + 1, (i + 1) * KAWALEK))
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=120)
                t = r["text"]
                if r["is_error"] or t.startswith("\0BRAK"):
                    czesci = None
                    break
                if not t:
                    break
                czesci.append(t)
                if len(t.encode("utf-8")) < KAWALEK:
                    break
                i += 1
            if czesci is None:
                print("%-28s BRAK w Studio" % n)
                continue
            zrodlo = "".join(czesci).replace("\r\n", "\n")
            plik = os.path.join(ROOT, "src", "server" if a.serwer else "client",
                                n + (".server.luau" if a.serwer else ".client.luau"))
            dysk = open(plik, encoding="utf-8").read().replace("\r\n", "\n") if os.path.exists(plik) else None
            with open(os.path.join(wyj, n + ".luau"), "w", encoding="utf-8", newline="\n") as f:
                f.write(zrodlo)
            stan = "brak pliku na dysku" if dysk is None else ("TAKIE SAME" if dysk.rstrip() == zrodlo.rstrip() else
                                                               "RÓŻNE (Studio %d linii, dysk %d)" % (
                                                                   zrodlo.count("\n"), dysk.count("\n")))
            print("%-28s %s" % (n, stan))
            if a.zapisz and dysk is not None and dysk.rstrip() != zrodlo.rstrip():
                with open(plik, "w", encoding="utf-8", newline="\n") as f:
                    f.write(zrodlo)
                print("   -> zapisano wersję ze Studio do %s" % os.path.relpath(plik, ROOT))


if __name__ == "__main__":
    main()
