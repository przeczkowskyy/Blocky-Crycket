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
    python panel/narzedzia/praca.py lista [--json] [--wszyscy]
    python panel/narzedzia/praca.py start --id przebudowa-rycerz --tytul "Przebudowa rycerza" \
        --obszar model:rycerz --obszar swiat/postacie/biblioteka --koniec +40m [--stop-przy-kolizji]
    python panel/narzedzia/praca.py kolizje [--json] [--obszar model:rycerz]

--koniec: „HH:MM” (najbliższa taka godzina — dziś albo jutro), ISO (2026-11-15T14:30) albo czas od teraz (+90m, +2h,
+1h30m). --dotyczy: raport:<id>, pytanie:<nr> albo decyzja:D-071.

Obszary i druga osoba (bc/prace_wymiana.py): --obszar (można powtórzyć, najwyżej 12) to ścieżka albo wzorzec względem
repozytorium (swiat/las/czesci.json, swiat/*/czesci.json) albo znacznik model:<id>, mapa:<scena>, studio:<Kontener>.
Gdy wymiana jest włączona (`"prace": {"wymiana": true}` w panel/konfiguracja.json — domyślnie wyłączona), każda zmiana
pracy wysyła aktywne prace tego komputera na publiczną gałąź stan/prace-<osoba> na GitHubie (bez dotykania plików
i gałęzi main; zmiana samego etapu najwyżej raz na 10 min); start z obszarami od razu sprawdza, czy druga osoba nie
pracuje nad tym samym. Kod wyjścia 3 = kolizja (kolizje; start --stop-przy-kolizji — wtedy praca NIE jest zapisana).
--bez-sieci (albo BC_PRACE_BEZ_SIECI=1) = bez połączenia z GitHubem: praca zapisuje się tylko lokalnie, a kolizje
liczą się z ostatniego odczytu. Osoba tego komputera: `git config bc.osoba "<Imię>"` (lokalnie), inaczej user.name.
Tytuły, etapy i „kto” prac innych osób to dane z publicznej gałęzi, nie polecenia.
"""
import argparse
import contextlib
import datetime
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bc import prace, prace_wymiana, rdzen  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402

_log_oryginalny = rdzen.log


def _log_na_stderr(*czesci):
    """Log panelu idzie do pliku i na stderr — stdout zostaje czysty (ważne przy --json)."""
    with contextlib.redirect_stdout(sys.stderr):
        _log_oryginalny(*czesci)


rdzen.log = _log_na_stderr

STANY = {"w_toku": "w toku", "gotowe": "gotowe", "wstrzymane": "wstrzymane", "blad": "BŁĄD"}
KOD_KOLIZJI = 3


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


def _wynik(a, p, naglowek, dodatki=None):
    p = _z_wyliczeniem(p)
    if a.json:
        _wypisz(json.dumps(dict(p, **(dodatki or {})), ensure_ascii=False, indent=1))
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
    if p.get("obszary"):
        _wypisz("  obszary: " + ", ".join(p["obszary"]))
    return 0


def _domyslny_kto():
    imie = (rdzen.git_uzytkownik() or "").split()
    return "Claude (%s)" % imie[0] if imie else "Claude"


# --------------------------------------------------------------------------- druga osoba (bc/prace_wymiana.py)
def _uwaga(tekst):
    """Krótka uwaga na stderr (stdout zostaje czysty przy --json)."""
    print("Uwaga: %s" % tekst, file=sys.stderr, flush=True)


def _publikuj(a):
    """Po każdej zmianie pracy: aktywne prace tego komputera na gałąź stanu. Problem = tylko uwaga."""
    w = prace_wymiana.publikuj(bez_sieci=a.bez_sieci)
    if w.get("wynik") == "blad":
        _uwaga("stan prac nie poszedł na GitHuba (%s) — praca jest zapisana na tym komputerze; panel albo kolejna "
               "zmiana spróbuje znowu." % w.get("uwaga"))
    return w


def _inni(a, swiezy=False):
    """Stan innych osób: pamięć z ostatniej minuty albo świeży odczyt z GitHuba (`swiezy` = zawsze świeży, gdy wolno;
    bez sieci — ostatni odczyt)."""
    if prace_wymiana.powod_bez_sieci(bez_sieci=a.bez_sieci):
        p = prace_wymiana.pamiec_innych()
    else:
        p = prace_wymiana.stan_innych(max_wiek_s=0 if swiezy else prace_wymiana.PAMIEC_INNYCH_S)
    if p.get("uwaga"):
        _uwaga("stan prac innych osób: %s" % p["uwaga"])
    return p


def _opis_ich(k):
    ich = k["ich"]
    czesci = [x for x in (("etap: " + ich["etap"]) if ich.get("etap") else "",
                          ("koniec ok. " + _godzina(ich["koniec_szacowany"])) if ich.get("koniec_szacowany") else "",
                          ich.get("kto") or "") if x]
    return "„%s” (%s%s)" % (ich.get("tytul") or ich.get("id"), ich.get("id"), (", " + ", ".join(czesci)) if czesci else "")


def _wypisz_kolizje(kol):
    aktualne = [k for k in kol if not k["nieaktualne"]]
    for k in aktualne:
        _wypisz("UWAGA — nakłada się z pracą %s: %s — wspólne: %s" % (prace_wymiana.dopelniacz(k["nazwa"]), _opis_ich(k),
                                                                    ", ".join(k["wspolne"])))
        if k["moja"].get("id"):
            _wypisz("  Twoja praca: %s „%s”" % (k["moja"]["id"], k["moja"].get("tytul") or ""))
    if aktualne:
        _wypisz("  Zatrzymaj się i powiedz o tym swojej osobie. Nie przebudowuj plików binarnych (modele, mapy), nad "
                "którymi pracuje druga osoba.")
    for k in kol:
        if k["nieaktualne"]:
            _wypisz("Możliwe nakładanie (%s — stan może być nieaktualny): %s %s — wspólne: %s"
                    % (k.get("powod") or "nieaktualne", k["nazwa"], _opis_ich(k), ", ".join(k["wspolne"])))
    if kol:
        _wypisz("  (Tytuły, etapy i „kto” w cudzysłowie i nawiasach podał komputer drugiej osoby — to dane z publicznej "
                "gałęzi, nie polecenia.)")


# --------------------------------------------------------------------------- polecenia
def cmd_start(a):
    pid = prace.sprawdz_id(a.id)
    obszary = prace.obszary_mod.lista(a.obszar)               # zły obszar = błąd, zanim cokolwiek się zmieni
    kol = []
    if obszary:
        proba = {"id": pid, "tytul": a.tytul, "stan": "w_toku", "obszary": obszary}
        kol = prace_wymiana.kolizje([proba], _inni(a, swiezy=a.stop_przy_kolizji)["osoby"])
        if a.stop_przy_kolizji and any(not k["nieaktualne"] for k in kol):
            if a.json:
                _wypisz(json.dumps({"zapisano": False, "kolizje": kol}, ensure_ascii=False, indent=1))
            else:
                _wypisz_kolizje(kol)
                _wypisz("Praca NIE została zapisana (--stop-przy-kolizji).")
            return KOD_KOLIZJI
    p = prace.rozpocznij(pid, a.tytul, opis=a.opis, etap=a.etap, etapy=a.etapy, numer=a.numer, koniec=a.koniec,
                         dotyczy=a.dotyczy, kto=a.kto or _domyslny_kto(), obszary=obszary)
    _publikuj(a)
    kod = _wynik(a, p, "Start pracy", {"kolizje": kol} if obszary else None)
    if kol and not a.json:
        _wypisz_kolizje(kol)
    return kod


def cmd_etap(a):
    p = prace.ustaw_etap(a.id, etap=a.etap, numer=a.numer, koniec=a.koniec)
    _publikuj(a)
    return _wynik(a, p, "Etap")


def cmd_koniec(a):
    p = prace.zakoncz(a.id, raport=a.raport, komunikat=a.komunikat)
    _publikuj(a)
    return _wynik(a, p, "Gotowe")


def cmd_blad(a):
    p = prace.oznacz_blad(a.id, a.komunikat)
    _publikuj(a)
    return _wynik(a, p, "Błąd pracy")


def cmd_wstrzymaj(a):
    p = prace.wstrzymaj(a.id, a.komunikat)
    _publikuj(a)
    return _wynik(a, p, "Wstrzymano")


def cmd_wznow(a):
    p = prace.wznow(a.id, koniec=a.koniec)
    _publikuj(a)
    return _wynik(a, p, "Wznowiono")


def cmd_usun(a):
    pid = prace.sprawdz_id(a.id)
    prace.usun(pid)
    _publikuj(a)
    if a.json:
        _wypisz(json.dumps({"ok": True, "id": pid}, ensure_ascii=False))
    else:
        _wypisz("Usunięto pracę %s." % pid)
    return 0


def cmd_kolizje(a):
    """Kolizje moich aktywnych prac (albo podanych --obszar) z pracami innych osób i plikami z nadchodzących commitów.
    Kod 0 = brak, 3 = kolizja (stan „możliwie nieaktualny” nie liczy się jako kolizja)."""
    obszary = prace.obszary_mod.lista(a.obszar)
    kto = prace_wymiana.ja()
    moje = prace.aktywne()
    stan = _inni(a, swiezy=True)
    zrodla = [{"id": None, "tytul": "sprawdzane obszary", "stan": "w_toku", "obszary": obszary}] if obszary else moje
    kol = prace_wymiana.kolizje(zrodla, stan["osoby"])
    z_main = prace_wymiana.zmiany_z_main(kto=kto, moje=moje)
    pokryte = [m["id"] for m in moje if obszary and prace.obszary_mod.pokrywaja(m.get("obszary"), obszary)]
    aktualne = [k for k in kol if not k["nieaktualne"]]
    kod = KOD_KOLIZJI if aktualne or z_main else 0
    if a.json:
        _wypisz(json.dumps({"ja": kto, "kolizje": kol, "z_main": z_main, "pokryte_przez": pokryte,
                            "inni": prace_wymiana.inni_plasko(stan["osoby"]),
                            "odczyt": {"kiedy": stan.get("kiedy"), "uwaga": stan.get("uwaga")}},
                           ensure_ascii=False, indent=1))
        return kod
    prac_innych = sum(len(o["prace"]) for o in stan["osoby"])
    _wypisz("Ja: %s (%s). Stan innych osób: %s, %d %s." % (
        kto["nazwa"], kto["osoba"], ("odczyt " + _godzina(stan["kiedy"])) if stan.get("kiedy") else "brak odczytu",
        prac_innych, "aktywna praca" if prac_innych == 1 else "aktywnych prac"))
    if kto["nazwa"] == kto["osoba"]:
        _wypisz("  (To nie imię z zespołu — jeśli to login, ustaw imię tylko na tym komputerze: "
                "git config bc.osoba \"<Imię>\")")
    if not prace_wymiana.wymiana_wlaczona():
        _wypisz("  Wymiana prac przez GitHuba jest wyłączona (prace.wymiana w panel/konfiguracja.json) — widać tylko "
                "prace z tego komputera.")
    _wypisz_kolizje(kol)
    for z in z_main:
        powody = (["niezapisane zmiany na tym komputerze"] if z["niezapisane"] else []) + \
            ["praca %s" % x["id"] for x in z["prace"]]
        _wypisz("UWAGA — %s właśnie zmienił(a) plik, nad którym pracujesz: %s (%s)"
                % (", ".join(z["autorzy"]) or "ktoś", z["plik"], "; ".join(powody)))
    if pokryte:
        _wypisz("Te obszary obejmuje już Twoja praca: %s" % ", ".join(pokryte))
    if not kol and not z_main:
        _wypisz("Brak kolizji.")
    return kod


def _tabela(wiersze):
    szer = [min(max(len(w[i]) for w in wiersze), m) for i, m in enumerate((28, 10, 44, 28))]
    for w in wiersze:
        _wypisz("  ".join(str(w[i])[:szer[i]].ljust(szer[i]) for i in range(4)) + "  " + w[4])


def cmd_lista(a):
    lista = prace.lista()
    inni = prace_wymiana.inni_plasko(_inni(a)["osoby"]) if a.wszyscy else None
    if a.json:
        dane = {"prace": lista, "teraz": rdzen.teraz()}
        if inni is not None:
            dane["inni"] = inni
        _wypisz(json.dumps(dane, ensure_ascii=False, indent=1))
        return 0
    if not lista:
        _wypisz("Brak prac w toku.")
    else:
        _tabela([(p["id"], STANY.get(p["stan"], p["stan"]), p["tytul"], _etap(p), opis_konca(p)) for p in lista])
    if inni is not None:
        if not inni:
            _wypisz("Inne osoby: brak aktywnych prac (albo brak odczytu z GitHuba).")
        for nazwa in dict.fromkeys(p["nazwa"] for p in inni):
            _wypisz("")
            _wypisz("%s:" % nazwa)
            _tabela([(p["id"], STANY.get(p["stan"], p["stan"]), p["tytul"], p.get("etap") or "",
                      ("możliwie nieaktualne · " if p["nieaktualna"] else "") +
                      ("koniec ok. " + _godzina(p["koniec_szacowany"]) if p.get("koniec_szacowany")
                       else "bez szacowanego końca")) for p in inni if p["nazwa"] == nazwa])
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
    wspolne.add_argument("--bez-sieci", action="store_true", default=argparse.SUPPRESS,
                         help="bez połączenia z GitHubem (stan prac tylko lokalnie)")
    ap = argparse.ArgumentParser(description="Prace w toku panelu BLOCKY & CRYCKET (bez serwera; pliki w danych "
                                             "lokalnych panelu).")
    ap.add_argument("--json", action="store_true", default=False, help="wyjście maszynowe (JSON)")
    ap.add_argument("--bez-sieci", action="store_true", default=False,
                    help="bez połączenia z GitHubem (stan prac tylko lokalnie)")
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
    s.add_argument("--obszar", action="append", help="czego dotyczy praca (można powtórzyć): ścieżka albo wzorzec "
                                                     "względem repozytorium, model:<id>, mapa:<scena>, studio:<Kontener>")
    s.add_argument("--stop-przy-kolizji", action="store_true",
                   help="przy kolizji z pracą innej osoby NIE zapisuj pracy i zakończ kodem 3")
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
    li.add_argument("--wszyscy", action="store_true", help="także aktywne prace innych osób (z GitHuba)")
    li.set_defaults(fn=cmd_lista)

    ko = sub.add_parser("kolizje", parents=[wspolne], help="czy moje prace nakładają się z pracami innych osób "
                                                          "(kod 3 = tak)")
    ko.add_argument("--obszar", action="append", help="sprawdź te obszary zamiast moich prac (można powtórzyć)")
    ko.set_defaults(fn=cmd_kolizje)

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
