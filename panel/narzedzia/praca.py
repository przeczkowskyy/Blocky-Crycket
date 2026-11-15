#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prace w toku — narzędzie dla agentów (działa bez serwera panelu, pisze małe pliki w danych lokalnych panelu).

Panel pokazuje je na Pulpicie (karta „Prace w toku”) z szacowaną godziną końca, a przy raporcie, pytaniu albo decyzji,
której praca dotyczy — mały znaczek „w pracy — koniec ok. 12:40”.

Przykłady:
    python panel/narzedzia/praca.py start --id biom-las --tytul "Biom Las — mapa z klocków" \
        --etapy "Plan,Budowa,Kontrola,Raport" --koniec +90m
    python panel/narzedzia/praca.py etap --id biom-las --etap Kontrola --koniec 12:40
    python panel/narzedzia/praca.py koniec --id biom-las --raport r-20261115-121500-ab12
    python panel/narzedzia/praca.py blad --id biom-las --komunikat "Studio się zamknęło"
    python panel/narzedzia/praca.py wstrzymaj --id biom-las [--komunikat "czeka na decyzję"]
    python panel/narzedzia/praca.py wznow --id biom-las [--koniec +30m]
    python panel/narzedzia/praca.py usun --id biom-las
    python panel/narzedzia/praca.py lista [--json]

--koniec: „HH:MM” (najbliższa taka godzina — dziś albo jutro), ISO (2026-11-15T14:30) albo czas od teraz (+90m, +2h,
+1h30m). --dotyczy: raport:<id>, pytanie:<nr> albo decyzja:D-071.
"""
import argparse
import contextlib
import datetime
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bc import prace, rdzen  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402

_log_oryginalny = rdzen.log


def _log_na_stderr(*czesci):
    """Log panelu idzie do pliku i na stderr — stdout zostaje czysty (ważne przy --json)."""
    with contextlib.redirect_stdout(sys.stderr):
        _log_oryginalny(*czesci)


rdzen.log = _log_na_stderr

STANY = {"w_toku": "w toku", "gotowe": "gotowe", "wstrzymane": "wstrzymane", "blad": "BŁĄD"}


def _wypisz(tekst=""):
    print(tekst, flush=True)


def ile_czasu(minuty):
    """35 → „35 min”, 80 → „1 h 20 min”, 120 → „2 h”, 1600 → „1 d 2 h”."""
    m = max(0, int(minuty))
    if m < 60:
        return "%d min" % m
    if m < 24 * 60:
        h, r = divmod(m, 60)
        return "%d h" % h + (" %d min" % r if r else "")
    d, r = divmod(m, 24 * 60)
    return "%d d" % d + (" %d h" % (r // 60) if r // 60 else "")


def _godzina(iso):
    try:
        d = datetime.datetime.fromisoformat(str(iso)).astimezone()
    except (TypeError, ValueError, OverflowError, OSError):
        return "?"
    dzis = datetime.datetime.now().astimezone().date()
    if d.date() == dzis:
        return d.strftime("%H:%M")
    if d.date() == dzis + datetime.timedelta(days=1):
        return "jutro " + d.strftime("%H:%M")
    return d.strftime("%d.%m %H:%M")


def opis_konca(p):
    """„koniec ok. 12:40 (za 35 min)”, „po czasie o 10 min (miał być 12:40)”, „gotowe 11:52”, „bez szacowanego końca”."""
    stan = p.get("stan")
    if stan == "gotowe":
        return "gotowe " + _godzina(p.get("zakonczono") or p.get("aktualizacja"))
    if stan == "blad":
        return "błąd " + _godzina(p.get("zakonczono") or p.get("aktualizacja"))
    if not p.get("koniec_szacowany"):
        return "bez szacowanego końca"
    k = _godzina(p["koniec_szacowany"])
    if p.get("po_czasie_min") is not None:
        return "po czasie o %s (miał być %s)" % (ile_czasu(p["po_czasie_min"]), k)
    return "koniec ok. %s (za %s)" % (k, ile_czasu(p.get("zostalo_min") or 0))


def _etap(p):
    etap = p.get("etap") or ""
    if p.get("etapy") and p.get("numer"):
        etap = "%s (%d z %d)" % (etap or p["etapy"][p["numer"] - 1], p["numer"], len(p["etapy"]))
    return etap


def _z_wyliczeniem(p):
    """Praca po zapisie z polami wyliczanymi (jak w liście)."""
    for x in prace.lista():
        if x["id"] == p["id"]:
            return x
    return p


def _wynik(a, p, naglowek):
    p = _z_wyliczeniem(p)
    if a.json:
        _wypisz(json.dumps(p, ensure_ascii=False, indent=1))
        return 0
    _wypisz("%s: %s — %s" % (naglowek, p["id"], p["tytul"]))
    czesci = [STANY.get(p["stan"], p["stan"])]
    if _etap(p):
        czesci.append("etap: " + _etap(p))
    czesci.append(opis_konca(p))
    _wypisz("  " + " · ".join(czesci))
    if p.get("komunikat"):
        _wypisz("  komunikat: " + p["komunikat"])
    if p.get("dotyczy"):
        _wypisz("  dotyczy: %s %s" % (p["dotyczy"]["typ"], p["dotyczy"]["id"]))
    if p.get("raport"):
        _wypisz("  raport z wynikiem: " + p["raport"])
    return 0


def _domyslny_kto():
    imie = (rdzen.git_uzytkownik() or "").split()
    return "Claude (%s)" % imie[0] if imie else "Claude"


# --------------------------------------------------------------------------- polecenia
def cmd_start(a):
    p = prace.rozpocznij(a.id, a.tytul, opis=a.opis, etap=a.etap, etapy=a.etapy, numer=a.numer, koniec=a.koniec,
                         dotyczy=a.dotyczy, kto=a.kto or _domyslny_kto())
    return _wynik(a, p, "Start pracy")


def cmd_etap(a):
    return _wynik(a, prace.ustaw_etap(a.id, etap=a.etap, numer=a.numer, koniec=a.koniec), "Etap")


def cmd_koniec(a):
    return _wynik(a, prace.zakoncz(a.id, raport=a.raport, komunikat=a.komunikat), "Gotowe")


def cmd_blad(a):
    return _wynik(a, prace.oznacz_blad(a.id, a.komunikat), "Błąd pracy")


def cmd_wstrzymaj(a):
    return _wynik(a, prace.wstrzymaj(a.id, a.komunikat), "Wstrzymano")


def cmd_wznow(a):
    return _wynik(a, prace.wznow(a.id, koniec=a.koniec), "Wznowiono")


def cmd_usun(a):
    pid = prace.sprawdz_id(a.id)
    prace.usun(pid)
    if a.json:
        _wypisz(json.dumps({"ok": True, "id": pid}, ensure_ascii=False))
    else:
        _wypisz("Usunięto pracę %s." % pid)
    return 0


def cmd_lista(a):
    lista = prace.lista()
    if a.json:
        _wypisz(json.dumps({"prace": lista, "teraz": rdzen.teraz()}, ensure_ascii=False, indent=1))
        return 0
    if not lista:
        _wypisz("Brak prac w toku.")
        return 0
    wiersze = [(p["id"], STANY.get(p["stan"], p["stan"]), p["tytul"], _etap(p), opis_konca(p)) for p in lista]
    szer = [min(max(len(w[i]) for w in wiersze), m) for i, m in enumerate((28, 10, 44, 28))]
    for w in wiersze:
        _wypisz("  ".join(str(w[i])[:szer[i]].ljust(szer[i]) for i in range(4)) + "  " + w[4])
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
    ap = argparse.ArgumentParser(description="Prace w toku panelu BLOCKY & CRYCKET (bez serwera; pliki w danych "
                                             "lokalnych panelu).")
    ap.add_argument("--json", action="store_true", default=False, help="wyjście maszynowe (JSON)")
    sub = ap.add_subparsers(dest="polecenie")
    koniec_pomoc = "szacowany koniec: HH:MM (najbliższa taka godzina), ISO albo +90m / +2h / +1h30m"

    s = sub.add_parser("start", parents=[wspolne], help="nowa praca")
    s.add_argument("--id", required=True, help="krótki identyfikator, np. biom-las (małe litery, cyfry, - i _)")
    s.add_argument("--tytul", required=True, help="krótki tytuł (do 120 znaków)")
    s.add_argument("--opis", help="jedno zdanie (do 300 znaków)")
    s.add_argument("--etap", help="bieżący etap, np. Plan")
    s.add_argument("--etapy", help="lista etapów po przecinku, np. \"Plan,Budowa,Kontrola\"")
    s.add_argument("--numer", type=int, help="numer bieżącego etapu (od 1)")
    s.add_argument("--koniec", help=koniec_pomoc)
    s.add_argument("--dotyczy", help="raport:<id>, pytanie:<nr> albo decyzja:D-071")
    s.add_argument("--kto", help="kto pracuje (domyślnie „Claude (<imię z git>)”)")
    s.set_defaults(fn=cmd_start)

    e = sub.add_parser("etap", parents=[wspolne], help="zmiana etapu albo szacowanego końca")
    e.add_argument("--id", required=True)
    e.add_argument("--etap", help="nowy etap")
    e.add_argument("--numer", type=int, help="numer etapu (od 1)")
    e.add_argument("--koniec", help=koniec_pomoc)
    e.set_defaults(fn=cmd_etap)

    k = sub.add_parser("koniec", parents=[wspolne], help="praca gotowa")
    k.add_argument("--id", required=True)
    k.add_argument("--raport", help="id raportu z wynikiem (z narzedzia/raport.py dodaj)")
    k.add_argument("--komunikat", help="krótka uwaga")
    k.set_defaults(fn=cmd_koniec)

    b = sub.add_parser("blad", parents=[wspolne], help="praca przerwana błędem")
    b.add_argument("--id", required=True)
    b.add_argument("--komunikat", required=True, help="co się stało (krótko)")
    b.set_defaults(fn=cmd_blad)

    w = sub.add_parser("wstrzymaj", parents=[wspolne], help="praca wstrzymana")
    w.add_argument("--id", required=True)
    w.add_argument("--komunikat", help="dlaczego (np. czeka na decyzję)")
    w.set_defaults(fn=cmd_wstrzymaj)

    z = sub.add_parser("wznow", parents=[wspolne], help="praca wznowiona")
    z.add_argument("--id", required=True)
    z.add_argument("--koniec", help=koniec_pomoc)
    z.set_defaults(fn=cmd_wznow)

    u = sub.add_parser("usun", parents=[wspolne], help="usuń pracę z listy")
    u.add_argument("--id", required=True)
    u.set_defaults(fn=cmd_usun)

    li = sub.add_parser("lista", parents=[wspolne], help="prace w toku i zakończone w ostatnich 48 h")
    li.set_defaults(fn=cmd_lista)

    a = ap.parse_args(argv)
    if not getattr(a, "fn", None):
        ap.print_help()
        return 2
    try:
        return a.fn(a)
    except (BladHTTP, OSError) as e:
        # OSError (np. dysk pełny, plik zablokowany): sam opis błędu systemu, bez ścieżki z nazwą użytkownika
        komunikat = e.komunikat if isinstance(e, BladHTTP) else \
            "nie udało się zapisać ani odczytać pliku pracy (%s)" % (e.strerror or type(e).__name__)
        if a.json:
            _wypisz(json.dumps({"blad": komunikat}, ensure_ascii=False))
        else:
            print("Błąd: %s" % komunikat, file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
