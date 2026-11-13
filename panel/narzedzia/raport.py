#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Raporty z wdrożeń — narzędzie dla agentów i ludzi (działa bez serwera panelu, pisze pliki w panel/dane/).

Przykłady:
    python panel/narzedzia/raport.py dodaj --tytul "Karczma: nowe drzwi" --opis "Co zrobiłem…" \
        --komponent studio:Workspace/DemoLesnaBaza/Karczma:"Karczma" --zrzut zrzut.png
    python panel/narzedzia/raport.py dodaj --rodzaj pytanie --tytul "Kolor dachu?" --pytanie "Czerwony czy zielony?"
    python panel/narzedzia/raport.py lista [--czeka] [--json]
    python panel/narzedzia/raport.py odpowiedzi [--od 2026-11-12T20:00] [--raport r-…] [--json]

`odpowiedzi` wypisuje decyzje i komentarze ludzi (bez wpisów agentów „Claude…”) — tak agent czyta odpowiedź człowieka.
"""
import argparse
import datetime
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import contextlib  # noqa: E402

from bc import rdzen, raporty  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402

_log_oryginalny = rdzen.log


def _log_na_stderr(*czesci):
    """Log panelu idzie do pliku i na stderr — stdout zostaje czysty (ważne przy --json)."""
    with contextlib.redirect_stdout(sys.stderr):
        _log_oryginalny(*czesci)


rdzen.log = _log_na_stderr

STATUSY = {"czeka": "CZEKA NA DECYZJĘ", "zaakceptowane": "zaakceptowane", "do_poprawy": "DO POPRAWY",
           "informacja": "informacja"}
DECYZJE = {"zaakceptowane": "ZAAKCEPTOWANE", "do_poprawy": "DO POPRAWY"}


def _wypisz(tekst=""):
    print(tekst, flush=True)


def _czas(iso):
    try:
        return datetime.datetime.fromisoformat(iso).strftime("%d.%m %H:%M")
    except (TypeError, ValueError):
        return str(iso or "")


def _parsuj_od(tekst):
    """--od w ISO (z godziną albo bez, ze strefą albo bez — bez strefy = czas lokalny)."""
    if not tekst:
        return None
    try:
        d = datetime.datetime.fromisoformat(tekst.strip().replace("Z", "+00:00"))
    except ValueError:
        raise BladHTTP(400, "Nie rozumiem daty --od „%s” (przykład: 2026-11-12T20:00)" % tekst)
    if d.tzinfo is None:
        d = d.astimezone()
    return d.timestamp()


def _ts(iso):
    try:
        d = datetime.datetime.fromisoformat(str(iso))
        if d.tzinfo is None:
            d = d.astimezone()
        return d.timestamp()
    except (TypeError, ValueError):
        return 0.0


def _komponent(spec):
    """typ:cel[:Etykieta] — etykieta po ostatnim dwukropku."""
    typ, sep, reszta = spec.partition(":")
    if not sep or not reszta:
        raise BladHTTP(400, "Komponent „%s” — oczekiwano typ:cel[:Etykieta], np. studio:Workspace/X:\"Karczma\"" % spec)
    if ":" in reszta:
        cel, _, etykieta = reszta.rpartition(":")
    else:
        cel, etykieta = reszta, ""
    k = {"typ": typ.strip(), "cel": cel.strip()}
    if etykieta.strip():
        k["etykieta"] = etykieta.strip().strip('"')
    return k


def _domyslny_kto():
    imie = (rdzen.git_uzytkownik() or "").split()
    return "Claude (%s)" % imie[0] if imie else "Claude"


def _tekst_opisu(a):
    if a.opis == "-":
        return sys.stdin.read()
    if a.opis_plik:
        with open(a.opis_plik, encoding="utf-8-sig") as f:
            return f.read()
    return a.opis or ""


# --------------------------------------------------------------------------- polecenia
def cmd_dodaj(a):
    r = raporty.dodaj_raport(a.tytul, _tekst_opisu(a), a.rodzaj, [_komponent(s) for s in a.komponent or []],
                             a.migawka, a.pytanie, kto=a.kto or _domyslny_kto(), zrzuty=a.zrzut or [])
    if a.json:
        _wypisz(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        _wypisz("Dodano raport %s: %s" % (r["id"], r["tytul"]))
        _wypisz("  status: %s · zrzutów: %d · komponentów: %d" % (STATUSY.get(r["status"], r["status"]),
                                                                 len(r["zrzuty"]), len(r["komponenty"])))
        _wypisz("  plik: %s" % rdzen.wzgledem_repo(os.path.join(rdzen.DANE, "raporty", r["id"] + ".json")))
        _wypisz("  Odpowiedź ludzi sprawdzisz poleceniem: python panel/narzedzia/raport.py odpowiedzi --raport %s"
                % r["id"])
    return 0


def cmd_lista(a):
    lista = raporty.lista_raportow()
    if a.czeka:
        lista = [r for r in lista if r["status"] == "czeka"]
    lista = lista[:a.ile] if a.ile else lista
    if a.json:
        _wypisz(json.dumps({"raporty": lista}, ensure_ascii=False, indent=1))
        return 0
    if not lista:
        _wypisz("Brak raportów.")
        return 0
    for r in lista:
        _wypisz("%s  %-17s %s  (%s, %s)%s" % (r["id"], STATUSY.get(r["status"], r["status"]), r["tytul"], r.get("kto"),
                                              _czas(r.get("czas")),
                                              "  · komentarzy: %d" % r["komentarzy"] if r.get("komentarzy") else ""))
    return 0


def _czy_agent(kto):
    return str(kto or "").strip().lower().startswith("claude")


def zbierz_odpowiedzi(od=None, raport_id=None):
    """Decyzje i komentarze ludzi (najstarsze pierwsze). Zwraca listę wpisów {rodzaj, czas, kto, …}."""
    prog = _parsuj_od(od)
    tytuly = {r["id"]: r["tytul"] for r in raporty.lista_raportow()}
    wpisy = []
    for r in raporty.lista_raportow():
        d = r.get("decyzja")
        if not d or (raport_id and r["id"] != raport_id):
            continue
        if prog is not None and _ts(d.get("czas")) < prog:
            continue
        wpisy.append({"rodzaj": "decyzja", "czas": d.get("czas"), "kto": d.get("kto"), "raport": r["id"],
                      "tytul": r["tytul"], "wartosc": d.get("wartosc"), "komentarz": d.get("komentarz") or ""})
    for k in raporty.komentarze(limit=0):
        if _czy_agent(k.get("kto")):
            continue
        cel = k.get("cel") or {}
        if raport_id and not (cel.get("typ") == "raport" and cel.get("cel") == raport_id):
            continue
        if prog is not None and _ts(k.get("czas")) < prog:
            continue
        w = {"rodzaj": "komentarz", "czas": k.get("czas"), "kto": k.get("kto"), "cel": cel, "tekst": k.get("tekst"),
             "zrodlo": k.get("zrodlo"), "id": k.get("id")}
        if cel.get("typ") == "raport":
            w["raport"] = cel.get("cel")
            w["tytul"] = tytuly.get(cel.get("cel"), "")
        wpisy.append(w)
    wpisy.sort(key=lambda w: _ts(w.get("czas")))
    return wpisy


def cmd_odpowiedzi(a):
    wpisy = zbierz_odpowiedzi(a.od, a.raport)
    if a.json:
        _wypisz(json.dumps({"odpowiedzi": wpisy, "teraz": rdzen.teraz()}, ensure_ascii=False, indent=1))
        return 0
    if not wpisy:
        _wypisz("Brak odpowiedzi ludzi%s." % (" od %s" % a.od if a.od else ""))
        return 0
    for w in wpisy:
        if w["rodzaj"] == "decyzja":
            _wypisz("[%s] %s: %s — raport %s „%s”" % (_czas(w["czas"]), w["kto"], DECYZJE.get(w["wartosc"], w["wartosc"]),
                                                      w["raport"], w["tytul"]))
            if w["komentarz"]:
                _wypisz("    " + w["komentarz"].replace("\n", "\n    "))
        else:
            cel = w["cel"]
            if cel.get("typ") == "raport":
                gdzie = "raport %s „%s”" % (cel.get("cel"), w.get("tytul", ""))
            else:
                gdzie = "%s %s" % (cel.get("typ"), cel.get("etykieta") or cel.get("cel"))
            _wypisz("[%s] %s%s komentuje %s:" % (_czas(w["czas"]), w["kto"], " (głosówka)" if w.get("zrodlo") == "glos"
                                                 else "", gdzie))
            _wypisz("    " + (w["tekst"] or "").replace("\n", "\n    "))
    _wypisz("\n(stan na %s — następnym razem użyj --od %s)" % (_czas(rdzen.teraz()), rdzen.teraz()))
    return 0


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    wspolne = argparse.ArgumentParser(add_help=False)
    wspolne.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="wyjście maszynowe (JSON)")
    ap = argparse.ArgumentParser(description="Raporty z wdrożeń panelu BLOCKY & CRYCKET (bez serwera).")
    ap.add_argument("--json", action="store_true", default=False, help="wyjście maszynowe (JSON)")
    sub = ap.add_subparsers(dest="polecenie")

    d = sub.add_parser("dodaj", parents=[wspolne], help="dodaj raport")
    d.add_argument("--tytul", required=True, help="krótki tytuł (do 140 znaków)")
    d.add_argument("--opis", default="", help="opis w Markdownie (do 8000 znaków); „-” = czytaj ze standardowego wejścia")
    d.add_argument("--opis-plik", help="opis z pliku .md (UTF-8)")
    d.add_argument("--rodzaj", default="wdrozenie", choices=raporty.RODZAJE)
    d.add_argument("--komponent", action="append", help="typ:cel[:Etykieta], typ = studio|notatka|plik|migawka")
    d.add_argument("--migawka", help="id migawki podglądu 3D")
    d.add_argument("--zrzut", action="append", help="obraz do załączenia (PNG/JPG/WEBP/GIF, limit 3 MB)")
    d.add_argument("--pytanie", help="pytanie do ludzi (przy rodzaju „pytanie”)")
    d.add_argument("--kto", help="autor (domyślnie „Claude (<imię z git>)”)")
    d.set_defaults(fn=cmd_dodaj)

    li = sub.add_parser("lista", parents=[wspolne], help="lista raportów")
    li.add_argument("--czeka", action="store_true", help="tylko czekające na decyzję")
    li.add_argument("--ile", type=int, default=0, help="najwyżej tyle (najnowsze)")
    li.set_defaults(fn=cmd_lista)

    o = sub.add_parser("odpowiedzi", parents=[wspolne], help="decyzje i komentarze ludzi")
    o.add_argument("--od", help="tylko nowsze niż ten czas (ISO, np. 2026-11-12T20:00)")
    o.add_argument("--raport", help="tylko dla tego raportu")
    o.set_defaults(fn=cmd_odpowiedzi)

    a = ap.parse_args(argv)
    if not getattr(a, "fn", None):
        ap.print_help()
        return 2
    try:
        return a.fn(a)
    except BladHTTP as e:
        if a.json:
            _wypisz(json.dumps({"blad": e.komunikat}, ensure_ascii=False))
        else:
            print("Błąd: %s" % e.komunikat, file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
