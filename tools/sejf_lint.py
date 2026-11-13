#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola sejfu Obsidiana przed commitem: linki, nagłówki, sekrety.

    python tools/sejf_lint.py            # sprawdza B&C/
    python tools/sejf_lint.py --sejf B&C --sejf inny/folder

Sprawdza:
- każdy [[wikilink]] wskazuje istniejącą notatkę (po nazwie pliku, bez rozróżniania wielkości liter);
- każda notatka ma nagłówek ze `status:` (kanon / propozycja / do-decyzji) — poza Szablonami i Źródłami;
- w treści nie ma rzeczy, które nie mogą trafić do publicznego repozytorium: adresów e-mail, kluczy i tokenów.
Kod wyjścia 1, gdy są błędy (ostrzeżenia nie blokują).
"""
import argparse
import os
import re
import sys

POMIJANE = {".obsidian", ".trash", "_narzędzia", "__pycache__", ".git"}
STATUSY = {"kanon", "propozycja", "do-decyzji"}
LINK = re.compile(r"!?\[\[([^\]\|#]+)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]")
SEKRETY = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "adres e-mail"),
    (re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}"), "klucz Anthropic"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"), "token GitHub"),
    (re.compile(r"(?i)(api[_-]?key|token|secret|haslo|hasło|password)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{16,}"), "klucz albo hasło"),
    (re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}"), "token JWT"),
]
WYJATKI_EMAIL = ("noreply@anthropic.com",)


def notatki(sejf):
    for katalog, podkatalogi, pliki in os.walk(sejf):
        podkatalogi[:] = [d for d in podkatalogi if d not in POMIJANE]
        for p in pliki:
            if p.lower().endswith(".md"):
                yield os.path.join(katalog, p)


def bez_kodu(tekst):
    tekst = re.sub(r"```.*?```", "", tekst, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", tekst)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser()
    ap.add_argument("--sejf", action="append")
    a = ap.parse_args()
    sejfy = [os.path.join(repo, s) if not os.path.isabs(s) else s for s in (a.sejf or ["B&C"])]
    bledy, ostrzezenia, ile = [], [], 0
    for sejf in sejfy:
        pliki = list(notatki(sejf))
        nazwy = {}
        for p in pliki:
            nazwy.setdefault(os.path.splitext(os.path.basename(p))[0].lower(), []).append(p)
        for nazwa, lista in nazwy.items():
            if len(lista) > 1:
                ostrzezenia.append("dwie notatki o tej samej nazwie „%s”: %s" % (nazwa, ", ".join(os.path.relpath(x, repo) for x in lista)))
        for p in pliki:
            ile += 1
            rel = os.path.relpath(p, repo).replace("\\", "/")
            with open(p, encoding="utf-8-sig") as f:
                tekst = f.read()
            czesci = os.path.relpath(p, sejf).replace("\\", "/").split("/")
            if czesci[0] not in ("Szablony", "Źródła"):
                m = re.match(r"---\n(.*?)\n---", tekst, flags=re.S)
                st = re.search(r"^status:\s*(\S+)", m.group(1), flags=re.M) if m else None
                if not st:
                    ostrzezenia.append("%s: brak `status:` w nagłówku" % rel)
                elif st.group(1) not in STATUSY:
                    ostrzezenia.append("%s: nieznany status „%s”" % (rel, st.group(1)))
            for cel in LINK.findall(bez_kodu(tekst)):
                # w tabelach Obsidian zapisuje alias jako [[Notatka\|Alias]] — ukośnik przed kreską nie należy do nazwy
                cel = cel.strip().rstrip("\\").strip()
                if cel.lower() not in nazwy and not os.path.exists(os.path.join(sejf, cel)):
                    bledy.append("%s: link [[%s]] nie wskazuje żadnej notatki" % (rel, cel))
            for wzor, opis in SEKRETY:
                for m in wzor.finditer(tekst):
                    if m.group(0) in WYJATKI_EMAIL:
                        continue
                    bledy.append("%s: możliwy sekret (%s): %s…" % (rel, opis, m.group(0)[:12]))
    for o in ostrzezenia:
        print("uwaga:", o)
    for b in bledy:
        print("BŁĄD:", b)
    print("Sejf: %d notatek, %d błędów, %d uwag" % (ile, len(bledy), len(ostrzezenia)))
    sys.exit(1 if bledy else 0)


if __name__ == "__main__":
    main()
