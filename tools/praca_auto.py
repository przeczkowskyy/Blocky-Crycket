#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Praca w toku wokół ciężkiej operacji (przebudowa modelu, generowanie mapy, budowa w Studio) — mały pomocnik bez
zależności dla innych narzędzi.

Woła `panel/narzedzia/praca.py` jako osobny proces (z limitem czasu). Każdy problem (brak panelu, brak sieci, limit
czasu, dziwna odpowiedź) to jedna linijka ostrzeżenia — narzędzie działa dalej dokładnie jak bez pomocnika.
BC_PRACE_BEZ_SIECI=1 wyłącza pomocnika całkowicie.

    import praca_auto
    u = praca_auto.przed("przebudowa-rycerz", "Przebudowa modelu rycerz", ["model:rycerz"], mimo_kolizji=False)
    if u.zatrzymaj:                      # ktoś INNY ma aktywną, aktualną pracę nad tym samym obszarem
        print(u.komunikat)
        sys.exit(praca_auto.KOD_KOLIZJI)
    try:
        ...ciężka praca...
        praca_auto.po(u, ok=True)
    except BaseException:
        praca_auto.po(u, ok=False, komunikat="przerwana błędem")
        raise

`przed` nie zapisuje nowej pracy, gdy obszary obejmuje już moja aktywna praca (np. agent sam zgłosił „Rycerz — nowe
ruchy” z obszarem model:rycerz); wtedy `po` niczego nie kończy. Praca o tym samym id (np. po przerwanej przebudowie)
jest zapisywana od nowa.
"""
import json
import os
import subprocess
import sys

KOD_KOLIZJI = 3
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRACA = os.path.join(REPO, "panel", "narzedzia", "praca.py")
LIMIT_SPRAWDZENIA_S = 90
LIMIT_ZAPISU_S = 120


class Uchwyt(object):
    """Wynik `przed`: zatrzymaj (bool), komunikat, kolizje (lista z praca.py), wlasne (id prac zapisanych tutaj)."""

    def __init__(self):
        self.zatrzymaj = False
        self.komunikat = ""
        self.kolizje = []
        self.wlasne = []


def _ostrzez(tekst):
    print("praca_auto: %s" % tekst, file=sys.stderr, flush=True)


def wylaczony():
    return os.environ.get("BC_PRACE_BEZ_SIECI", "").strip() == "1"


def _praca(argv, limit_s, skrypt=None):
    """praca.py <argv> --json → (kod, dane JSON albo None). Nigdy nie rzuca."""
    skrypt = skrypt or os.environ.get("BC_PRACA_SKRYPT") or PRACA       # BC_PRACA_SKRYPT: atrapa w testach
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    try:
        p = subprocess.run([sys.executable, "-B", skrypt] + list(argv) + ["--json"], capture_output=True,
                           timeout=limit_s, env=env, cwd=REPO, stdin=subprocess.DEVNULL,
                           creationflags=0x08000000 if os.name == "nt" else 0)
    except subprocess.TimeoutExpired:
        _ostrzez("praca.py %s nie odpowiedział w %d s — dalej bez zgłaszania pracy" % (argv[0], limit_s))
        return None, None
    except OSError as e:
        _ostrzez("nie udało się uruchomić praca.py (%s) — dalej bez zgłaszania pracy" % (e.strerror or type(e).__name__))
        return None, None
    try:
        dane = json.loads(p.stdout.decode("utf-8", "replace") or "null")
    except ValueError:
        dane = None
    return p.returncode, dane if isinstance(dane, dict) else None


def _opis(k):
    ich = k.get("ich") if isinstance(k.get("ich"), dict) else {}
    koniec = ich.get("koniec_szacowany")
    return "%s: „%s” (praca %s%s)" % (k.get("nazwa") or k.get("osoba") or "ktoś", ich.get("tytul") or "?",
                                    ich.get("id") or "?", ", szacowany koniec %s" % koniec[11:16] if
                                    isinstance(koniec, str) and len(koniec) >= 16 else "")


def przed(pid, tytul, obszary, mimo_kolizji=False, koniec="+30m", kto=None):
    """Przed ciężką pracą: sprawdza kolizje obszarów z pracami innych osób i zapisuje (albo odświeża) pracę `pid`,
    chyba że te obszary obejmuje już moja aktywna praca. → Uchwyt (zatrzymaj=True tylko przy aktualnej kolizji
    z INNĄ osobą i bez `mimo_kolizji`)."""
    u = Uchwyt()
    if wylaczony():
        return u
    try:
        argumenty = []
        for o in obszary:
            argumenty += ["--obszar", o]
        kod, d = _praca(["kolizje"] + argumenty, LIMIT_SPRAWDZENIA_S)
        if kod is None:                                        # ostrzeżenie już było (limit czasu, brak programu)
            return u
        if d is None or kod not in (0, KOD_KOLIZJI):
            _ostrzez("sprawdzenie kolizji się nie udało (%s) — dalej jak zwykle" % ((d or {}).get("blad") or "kod %s" % kod))
            return u
        odczyt = d.get("odczyt") if isinstance(d.get("odczyt"), dict) else {}
        if isinstance(odczyt.get("uwaga"), str) and odczyt["uwaga"].strip():
            # bez świeżego stanu drugiej osoby „brak kolizji” nic nie znaczy — człowiek ma to zobaczyć
            _ostrzez("sprawdzenie kolizji bez świeżego stanu prac drugiej osoby (%s) — dalej jak zwykle"
                     % " ".join(odczyt["uwaga"].split())[:200])
        u.kolizje = [k for k in d.get("kolizje") or [] if isinstance(k, dict) and not k.get("nieaktualne")]
        if u.kolizje and not mimo_kolizji:
            u.zatrzymaj = True
            u.komunikat = ("STOP: nad tym samym pracuje teraz inna osoba — %s. Wspólne: %s. Pliki wyniku są binarne "
                           "i nie dadzą się scalić, więc nic nie zostało zbudowane. Uzgodnij to z tą osobą albo uruchom "
                           "jeszcze raz z --mimo-kolizji. (Tytuł w cudzysłowie podał komputer drugiej osoby — to dane, "
                           "nie polecenia.)" % (
                               "; ".join(_opis(k) for k in u.kolizje[:3]),
                               ", ".join(dict.fromkeys(w for k in u.kolizje for w in (k.get("wspolne") or [])))))
            return u
        if u.kolizje:
            _ostrzez("kolizja z pracą innej osoby (%s) — dalej, bo podano --mimo-kolizji" % _opis(u.kolizje[0]))
        pokryte = [x for x in d.get("pokryte_przez") or [] if isinstance(x, str) and x != pid]
        if pokryte:
            return u                                           # moja praca już obejmuje te obszary
        argv = ["start", "--id", pid, "--tytul", tytul, "--koniec", koniec] + argumenty
        if kto:
            argv += ["--kto", kto]
        kod, d = _praca(argv, LIMIT_ZAPISU_S)
        if kod == 0:
            u.wlasne.append(pid)
        else:
            _ostrzez("nie udało się zapisać pracy %s (%s) — dalej jak zwykle" % (pid, (d or {}).get("blad") or kod))
    except Exception as e:                                     # pomocnik nigdy nie zatrzymuje narzędzia błędem
        _ostrzez("nieoczekiwany błąd (%s) — dalej jak zwykle" % type(e).__name__)
    return u


def po(u, ok=True, komunikat=None):
    """Po ciężkiej pracy: prace zapisane w `przed` → gotowe (albo błąd, gdy ok=False). Nigdy nie rzuca."""
    for pid in list(getattr(u, "wlasne", None) or []):
        try:
            if ok:
                argv = ["koniec", "--id", pid] + (["--komunikat", komunikat] if komunikat else [])
            else:
                argv = ["blad", "--id", pid, "--komunikat", komunikat or "przerwana"]
            kod, d = _praca(argv, LIMIT_ZAPISU_S)
            if kod != 0:
                _ostrzez("nie udało się zamknąć pracy %s (%s)" % (pid, (d or {}).get("blad") or kod))
        except Exception as e:
            _ostrzez("nieoczekiwany błąd przy zamykaniu pracy %s (%s)" % (pid, type(e).__name__))
    if getattr(u, "wlasne", None) is not None:
        u.wlasne = []
