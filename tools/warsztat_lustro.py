#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lustro wybranych notatek z prywatnego sejfu narzędziowego („Warsztat”) w sejfie gry — tylko do odczytu.

Po co: druga osoba (i jej Claude) widzi wiedzę narzędziową potrzebną przy grze (Blender, zasoby 3D, Roblox Studio,
Higgsfield…) w tym samym grafie co notatki gry, bez dostępu do prywatnego sejfu. Repozytorium jest publiczne, więc
lustro bierze TYLKO notatki z listy i nigdy te oznaczone `prywatne: true`.

    python tools/warsztat_lustro.py --zrodlo "C:/…/Obsidian Vault/Warsztat"            # notatki z listy poniżej
    python tools/warsztat_lustro.py --zrodlo "…" --wszystko                             # wszystkie nieprywatne
    python tools/warsztat_lustro.py --zrodlo "…" --cel <inny folder> --sucho            # tylko pokaż, co by zrobił

Co robi z każdą notatką: pomija prywatne; zmienia nazwę, gdy koliduje z notatką gry („Warsztat — …”); przepisuje
wikilinki (do notatek spoza lustra zostaje sam tekst); usuwa osadzenia plików; zamienia ścieżki z nazwą użytkownika
na %USERPROFILE%; dopisuje ramkę „lustro — nie edytuj tutaj”. Na końcu sprawdza, czy w lustrze nie ma sekretów.
Folder docelowy jest za każdym razem budowany od nowa (to lustro, nie miejsce do pisania).
"""
import argparse
import os
import re
import shutil
import sys

DOMYSLNA_LISTA = [
    "00 START", "Mapa możliwości", "Dołącz do projektu",
    "Blender", "BlenderKit", "Cycles i render", "ffmpeg i wideo", "Higgsfield", "Higgsfield — wzorzec skryptu", "Obsidian",
    "Roblox Studio", "Skrypty przenośne", "Claude Code — skille, pamięć, pomocnicy",
    "Z Blendera do Robloxa", "Pozyskanie zasobu — szukaj, pobierz, dołącz", "Scenografia z gotowych modeli", "Tekstury i materiały",
    "Styl własny — presety i przewodnik stylu", "Generowanie grafik i dźwięku", "Scena 3D od zera do renderu",
    "Sesje, pomocnicy i oszczędzanie tokenów", "Pułapki narzędzi na Windows", "Roblox — gra",
    "Konwencje notatek", "Szablon — przewodnik stylu", "Start nowego projektu",
    "Darmowe źródła zasobów 3D", "Linki — dokumentacja", "Repozytoria GitHub i MCP",
]
POMIJANE_KATALOGI = {".obsidian", ".trash", "_narzędzia", "__pycache__", "_archiwum"}
LINK = re.compile(r"(!?)\[\[([^\]\|#]+)(#[^\]\|]*)?(\|[^\]]*)?\]\]")
SEKRETY = [re.compile(p) for p in (
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", r"sk-ant-[A-Za-z0-9_-]{10,}", r"gh[pousr]_[A-Za-z0-9]{20,}",
    r"(?i)(api[_-]?key|token|secret|hasło|haslo|password)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{16,}")]
RAMKA = ("> [!note] Lustro notatki z Warsztatu narzędziowego Karola — tylko do odczytu\n"
         "> Ta notatka opisuje narzędzia, nie grę, i ma własne statusy (sprawdzone / częściowo / hipoteza). Nie edytuj jej tutaj: "
         "zmiany powstają w oryginale i wracają poleceniem `python tools/warsztat_lustro.py`.\n\n")


def notatki(sejf):
    for katalog, podkatalogi, pliki in os.walk(sejf):
        podkatalogi[:] = [d for d in podkatalogi if d not in POMIJANE_KATALOGI]
        for p in pliki:
            if p.lower().endswith(".md"):
                yield os.path.join(katalog, p)


def naglowek(tekst):
    m = re.match(r"---\n(.*?)\n---\n?", tekst, flags=re.S)
    return (m.group(1), tekst[m.end():]) if m else ("", tekst)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser(description="Lustro notatek Warsztatu w sejfie gry")
    ap.add_argument("--zrodlo", required=True, help="folder Warsztatu w prywatnym sejfie Obsidiana")
    ap.add_argument("--cel", default=os.path.join(repo, "B&C", "Warsztat"))
    ap.add_argument("--sejf-gry", default=os.path.join(repo, "B&C"))
    ap.add_argument("--wszystko", action="store_true", help="wszystkie nieprywatne notatki zamiast listy domyślnej")
    ap.add_argument("--sucho", action="store_true")
    a = ap.parse_args()
    cel = os.path.abspath(a.cel)

    zrodla = {}
    for p in notatki(a.zrodlo):
        with open(p, encoding="utf-8-sig") as f:
            tekst = f.read()
        fm, _ = naglowek(tekst)
        if re.search(r"^prywatne:\s*true\s*$", fm, flags=re.M | re.I):
            continue
        zrodla[os.path.splitext(os.path.basename(p))[0]] = (p, tekst)
    wybrane = sorted(zrodla) if a.wszystko else [n for n in DOMYSLNA_LISTA if n in zrodla]
    brak = [] if a.wszystko else [n for n in DOMYSLNA_LISTA if n not in zrodla]

    zajete = set()
    for p in notatki(a.sejf_gry):
        if os.path.abspath(p).startswith(cel + os.sep):
            continue
        zajete.add(os.path.splitext(os.path.basename(p))[0].lower())
    nowe_nazwy = {}
    for n in wybrane:
        nowa = n
        if n.lower() in zajete or n.lower() == "00 start":
            nowa = "Warsztat — " + (n[3:] if n.lower().startswith("00 ") else n[0].lower() + n[1:])
        nowe_nazwy[n] = nowa
    mapa_malych = {n.lower(): n for n in wybrane}

    def przepisz(m):
        osadzenie, nazwa, kotwica, alias = m.group(1), m.group(2).strip(), m.group(3) or "", m.group(4)
        klucz = mapa_malych.get(nazwa.lower())
        if osadzenie and not klucz:
            return ""                                          # osadzony plik (np. mapa SVG) nie jest częścią lustra
        if klucz:
            nowa = nowe_nazwy[klucz]
            if not alias and nowa != klucz:
                alias = "|" + nazwa
            return "%s[[%s%s%s]]" % (osadzenie, nowa, kotwica, alias or "")
        return alias[1:] if alias else nazwa                   # notatka spoza lustra: zostaje sam tekst

    print("Lustro: %d notatek -> %s%s" % (len(wybrane), cel, " (na sucho)" if a.sucho else ""))
    if brak:
        print("  brak w źródle (pominięte): " + ", ".join(brak))
    podejrzane = []
    wyniki = []
    for n in wybrane:
        sciezka, tekst = zrodla[n]
        fm, tresc = naglowek(tekst)
        tresc = LINK.sub(przepisz, tresc)
        tresc = re.sub(r"[A-Za-z]:\\Users\\[^\\\s`\"']+", r"%USERPROFILE%", tresc)
        tresc = re.sub(r"[A-Za-z]:/Users/[^/\s`\"']+", r"%USERPROFILE%", tresc)
        uzytkownik = os.environ.get("USERNAME") or os.environ.get("USER") or ""
        if len(uzytkownik) >= 4:                               # nazwa konta systemowego nie trafia do publicznego repo
            tresc = re.sub(re.escape(uzytkownik), "<użytkownik>", tresc, flags=re.I)
        fm = re.sub(r"^zrodla:.*?(?=^\S|\Z)", "", fm, flags=re.S | re.M).rstrip("\n")      # ścieżki źródeł to szczegół prywatny
        if nowe_nazwy[n] != n:
            tresc = re.sub(r"^# .*$", "# " + nowe_nazwy[n], tresc, count=1, flags=re.M)
            fm = re.sub(r"^tytul:.*$", "tytul: " + nowe_nazwy[n], fm, flags=re.M)
        wynik = "---\n%s\nlustro: true\n---\n\n%s%s" % (fm, RAMKA, tresc.lstrip("\n"))
        for wzor in SEKRETY:
            for m in wzor.finditer(wynik):
                podejrzane.append("%s: %s…" % (n, m.group(0)[:14]))
        podfolder = os.path.basename(os.path.dirname(sciezka))
        podfolder = "" if os.path.abspath(os.path.dirname(sciezka)) == os.path.abspath(a.zrodlo) else podfolder
        wyniki.append((os.path.join(cel, podfolder, nowe_nazwy[n] + ".md"), wynik))
        if nowe_nazwy[n] != n:
            print("  zmiana nazwy: %s -> %s" % (n, nowe_nazwy[n]))
    if podejrzane:
        print("STOP — możliwe sekrety w notatkach, nic nie zapisano:")
        for p in podejrzane:
            print("  " + p)
        sys.exit(1)
    if a.sucho:
        return
    if os.path.isdir(cel):
        shutil.rmtree(cel)
    for sciezka, wynik in wyniki:
        os.makedirs(os.path.dirname(sciezka), exist_ok=True)
        with open(sciezka, "w", encoding="utf-8", newline="\n") as f:
            f.write(wynik)
    print("Zapisano %d notatek. Sprawdź: python tools/sejf_lint.py" % len(wyniki))


if __name__ == "__main__":
    main()
