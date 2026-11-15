# -*- coding: utf-8 -*-
"""Prace w toku: co właśnie powstaje, na jakim jest etapie i o której mniej więcej się skończy.

Jedna praca = jeden mały plik JSON w DANYCH LOKALNYCH panelu (rdzen.RUNTIME/prace/<id>.json) — nie w repozytorium:
stan prac zmienia się co chwilę i nie może robić commitów. Pliki pisze narzędzie `narzedzia/praca.py` (agenci, bez
serwera); serwer tylko czyta (GET /api/prace) i sprząta zakończone prace starsze niż 48 h.

Odporność: odczyt bierze z pliku tylko pola z listy niżej, z właściwymi typami (dziwna wartość = brak pola, nieznane
pola nie idą do API), a jedna zła praca jest pomijana z wpisem w logu — reszta listy zostaje. Odczyt w chwili, gdy inny
proces podmienia plik, jest ponawiany. Zmiana pracy (odczyt–zmiana–zapis) idzie pod krótką blokadą <id>.lock.

Pola pliku:
    id                 bezpieczny slug (małe litery, cyfry, „-” i „_”, do 64 znaków), np. „biom-las”
    tytul              krótki tytuł (do 120 znaków)
    opis?              jedno zdanie (do 300 znaków)
    etap?              krótki tekst bieżącego etapu, np. „Kontrola”
    etapy?, numer?     lista nazw etapów i numer bieżącego (od 1)
    start              ISO — kiedy praca ruszyła
    koniec_szacowany?  ISO — szacowany koniec
    stan               w_toku | gotowe | wstrzymane | blad
    komunikat?         np. powód błędu albo wstrzymania
    dotyczy?           {typ: raport | pytanie | decyzja, id} — pozycja w panelu, której praca dotyczy
    raport?            id raportu z wynikiem
    kto?               kto pracuje (np. „Claude (Karol)”)
    aktualizacja       ISO — ostatnia zmiana
    zakonczono?        ISO — kiedy praca przeszła w „gotowe” albo „blad”

Funkcje publiczne (dla CLI i testów; `teraz` = datetime ze strefą, domyślnie teraz):
    parsuj_koniec(tekst, teraz=None) -> ISO        HH:MM (najbliższa taka godzina), ISO albo +90m / +2h / +1h30m
    rozpocznij(id, tytul, ...) -> praca            nowa praca (ten sam id = praca od nowa)
    ustaw_etap(id, etap=None, numer=None, koniec=None) -> praca
    zakoncz(id, raport=None, komunikat=None), oznacz_blad(id, komunikat), wstrzymaj(id, komunikat=None),
    wznow(id, koniec=None), usun(id)
    lista(teraz=None) -> [praca z polami wyliczanymi]   (kolejność jak w GET /api/prace)
    sprzataj(teraz=None) -> liczba usuniętych plików

Pola wyliczane (w liście i w API): zostalo_min albo po_czasie_min, przeterminowana, postep (0–1 albo null).
Błędy walidacji to rdzen.BladHTTP(400, "…") z komunikatem po polsku (CLI pokazuje sam komunikat).
"""
import contextlib
import datetime
import functools
import json
import math
import os
import re
import threading
import time

from . import rdzen
from .rdzen import BladHTTP

STANY = ("w_toku", "gotowe", "wstrzymane", "blad")
ZAKONCZONE = ("gotowe", "blad")
TYPY_DOTYCZY = ("raport", "pytanie", "decyzja")
WIDOCZNE_PO_KONCU_S = 48 * 3600

RX_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
RX_RAPORT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")     # jak w bc/raporty.py
RX_DECYZJA = re.compile(r"^D-?(\d{1,4})$", re.I)
RX_GODZINA = re.compile(r"^(\d{1,2})[:.](\d{2})$")
RX_ZA = re.compile(r"^\+\s*(?:(\d+)\s*h)?\s*(?:(\d+)\s*(?:m|min)?)?$", re.I)
# ścieżki z nazwą użytkownika systemu (C:\Users\…, /home/…) nie trafiają do panelu — repozytorium i panel są publiczne
RX_SCIEZKA = re.compile(r"(?:[A-Za-z]:[\\/]+(?:Users|Użytkownicy|Documents and Settings)[\\/]+[^\\/\s\"']+"
                        r"|/(?:home|Users)/[^/\s\"']+)", re.I)

MAX_TYTUL = 120
MAX_OPIS = 300
MAX_ETAP = 80
MAX_ETAPY = 12
MAX_KOMUNIKAT = 300
MAX_KTO = 40

_zapis_lock = threading.Lock()
_sprzatanie = {"t": 0.0}


# --------------------------------------------------------------------------- ścieżki i czas
def katalog():
    """Katalog plików prac (w danych lokalnych panelu, poza repozytorium)."""
    return os.path.join(rdzen.RUNTIME, "prace")


def _sciezka(pid):
    return os.path.join(katalog(), pid + ".json")


def _teraz(teraz=None):
    t = teraz or datetime.datetime.now().astimezone()
    return t if t.tzinfo else t.astimezone()


def _iso(d):
    return d.astimezone().isoformat(timespec="seconds")


ROK_MIN, ROK_MAX = 2000, 2200                                  # daty spoza tego zakresu to zepsute dane


def _czas(iso):
    """ISO → datetime ze strefą (bez strefy = czas lokalny) albo None — także dla dat, których system nie umie
    przeliczyć (np. rok 1 albo 9999: na Windows astimezone() rzuca wtedy OSError)."""
    if not iso or not isinstance(iso, str):
        return None
    try:
        d = datetime.datetime.fromisoformat(iso.strip().replace("Z", "+00:00"))
        if not ROK_MIN <= d.year <= ROK_MAX:
            return None
        d = d if d.tzinfo else d.astimezone()
        d.astimezone()
        d.timestamp()
        return d
    except (ValueError, OverflowError, OSError, TypeError):
        return None


ZAKRES_KONCA = (datetime.timedelta(days=1), datetime.timedelta(days=14))    # od wczoraj do dwóch tygodni naprzód


def _najblizsza_godzina(t, g, mi):
    """Najbliższa godzina g:mi czasu lokalnego po chwili t (dziś albo jutro). Godzina jest składana na dacie lokalnej
    i dopiero potem dostaje strefę — tak „20:00” zostaje 20:00 także przez zmianę czasu (letni/zimowy)."""
    dzien = t.astimezone().date()
    for dni in (0, 1, 2):
        k = datetime.datetime.combine(dzien + datetime.timedelta(days=dni), datetime.time(g, mi)).astimezone()
        if k > t:
            return k
    return k


def parsuj_koniec(tekst, teraz=None):
    """Szacowany koniec z tekstu: „HH:MM” (najbliższa taka godzina — dziś albo jutro), ISO („2026-11-15T14:30”)
    albo czas od teraz („+90m”, „+2h”, „+1h30m”, „+45”). Zwraca ISO ze strefą; zły tekst = BladHTTP 400."""
    if tekst is None:
        return None
    s = str(tekst).strip()
    if not s:
        raise BladHTTP(400, "Pusty szacowany koniec (przykłady: 12:40, +90m, 2026-11-15T14:30)")
    t = _teraz(teraz).replace(microsecond=0)
    m = RX_GODZINA.match(s)
    if m:
        g, mi = int(m.group(1)), int(m.group(2))
        if g > 23 or mi > 59:
            raise BladHTTP(400, "Nie ma takiej godziny: „%s” (przykład: 12:40)" % s)
        return _iso(_najblizsza_godzina(t, g, mi))             # ta godzina już była (albo trwa) — jutro
    if s.startswith("+"):
        m = RX_ZA.match(s)
        if not m or not (m.group(1) or m.group(2)):
            raise BladHTTP(400, "Nie rozumiem czasu „%s” (przykłady: +90m, +2h, +1h30m)" % s)
        minuty = int(m.group(1) or 0) * 60 + int(m.group(2) or 0)
        if minuty <= 0 or minuty > 14 * 24 * 60:
            raise BladHTTP(400, "Czas „%s” musi być dłuższy niż zero i krótszy niż dwa tygodnie" % s)
        return _iso(t + datetime.timedelta(minutes=minuty))
    try:
        datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        poprawny_zapis = True
    except ValueError:
        poprawny_zapis = False
    d = _czas(s)
    za_daleko = "Szacowany koniec „%s” jest poza zakresem — podaj czas od wczoraj do dwóch tygodni naprzód " \
                "(przykłady: 12:40, +90m, 2026-11-15T14:30)" % s[:40]
    if d is None:
        if poprawny_zapis:
            raise BladHTTP(400, za_daleko)
        raise BladHTTP(400, "Nie rozumiem szacowanego końca „%s” (przykłady: 12:40, +90m, 2026-11-15T14:30)" % s[:40])
    if not t - ZAKRES_KONCA[0] <= d <= t + ZAKRES_KONCA[1]:
        raise BladHTTP(400, za_daleko)
    return _iso(d.replace(microsecond=0))


# --------------------------------------------------------------------------- walidacja
def sprawdz_id(pid):
    """Bezpieczny identyfikator pracy (slug). Wielkie litery są zamieniane na małe."""
    if not isinstance(pid, str):
        raise BladHTTP(400, "Brak identyfikatora pracy (--id)")
    p = pid.strip().lower()
    if not RX_ID.match(p):
        raise BladHTTP(400, "Niepoprawny identyfikator pracy „%s” — tylko małe litery, cyfry, „-” i „_” "
                            "(do 64 znaków), np. biom-las" % pid[:80])
    return p


def _bez_sciezek(tekst):
    return RX_SCIEZKA.sub("…", tekst) if tekst else tekst


def _tekst(v, nazwa, maks, wymagane=False):
    if v is None:
        if wymagane:
            raise BladHTTP(400, "Brak pola „%s”" % nazwa)
        return None
    if not isinstance(v, str):
        raise BladHTTP(400, "Pole „%s” musi być tekstem" % nazwa)
    v = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", v.replace("\r\n", "\n").replace("\n", " ")).strip()
    if wymagane and not v:
        raise BladHTTP(400, "Pole „%s” nie może być puste" % nazwa)
    if len(v) > maks:
        raise BladHTTP(400, "Pole „%s” jest za długie (%d znaków, najwyżej %d)" % (nazwa, len(v), maks))
    return _bez_sciezek(v) or None


def _etapy(lista):
    if lista is None:
        return None
    if isinstance(lista, str):
        lista = [x for x in lista.split(",")]
    if not isinstance(lista, list):
        raise BladHTTP(400, "Etapy muszą być listą nazw (np. \"Plan,Budowa,Kontrola\")")
    out = [_tekst(x, "etap", MAX_ETAP) for x in lista]
    out = [x for x in out if x]
    if len(out) > MAX_ETAPY:
        raise BladHTTP(400, "Za dużo etapów (%d, najwyżej %d)" % (len(out), MAX_ETAPY))
    return out or None


def parsuj_dotyczy(spec):
    """„raport:<id>”, „pytanie:<nr>”, „decyzja:D-019” (albo słownik {typ, id}) → {typ, id}."""
    if spec is None:
        return None
    if isinstance(spec, dict):
        typ, ident = spec.get("typ"), spec.get("id")
    else:
        typ, sep, ident = str(spec).strip().partition(":")
        if not sep:
            raise BladHTTP(400, "„%s” — oczekiwano typ:id, np. raport:r-20261115-101500-ab12, pytanie:19 albo "
                                "decyzja:D-071" % str(spec)[:80])
    typ = str(typ or "").strip().lower()
    ident = str(ident if ident is not None else "").strip()
    if typ not in TYPY_DOTYCZY:
        raise BladHTTP(400, "Typ w „dotyczy” musi być jednym z: %s" % ", ".join(TYPY_DOTYCZY))
    if typ == "raport":
        if not RX_RAPORT.match(ident):
            raise BladHTTP(400, "Niepoprawny identyfikator raportu w „dotyczy”: „%s”" % ident[:80])
    elif typ == "pytanie":
        if not re.match(r"^\d{1,4}$", ident):
            raise BladHTTP(400, "Pytanie w „dotyczy” to numer, np. pytanie:19")
        ident = str(int(ident))
    else:
        m = RX_DECYZJA.match(ident)
        if not m:
            raise BladHTTP(400, "Decyzja w „dotyczy” to numer, np. decyzja:D-071")
        ident = "D-%03d" % int(m.group(1))
    return {"typ": typ, "id": ident}


def _kto(kto):
    kto = _bez_sciezek(re.sub(r"[\x00-\x1f\x7f]", "", str(kto or "")).strip())[:MAX_KTO].strip()
    return kto or None


def _numer(numer, etapy):
    if numer is None:
        return None
    try:
        n = int(numer)
    except (TypeError, ValueError):
        raise BladHTTP(400, "Numer etapu musi być liczbą (od 1)")
    if n < 1:
        raise BladHTTP(400, "Numer etapu zaczyna się od 1")
    if etapy and n > len(etapy):
        raise BladHTTP(400, "Numer etapu %d, a etapów jest %d" % (n, len(etapy)))
    return n


# --------------------------------------------------------------------------- odczyt i zapis
POLA_CZASU = ("start", "koniec_szacowany", "aktualizacja", "zakonczono")


def _tekst_z_pliku(v, maks):
    """Pole tekstowe odczytane z pliku: tekst bez ścieżek i znaków sterujących albo None (inny typ = brak pola)."""
    if not isinstance(v, str):
        return None
    v = _bez_sciezek(re.sub(r"[\x00-\x1f\x7f]", " ", v).strip())[:maks].strip()
    return v or None


def _oczysc(dane):
    """Praca z pliku → tylko pola z listy (P1), z właściwymi typami. Pola nieznane (np. ręcznie dopisane „token” albo
    „sciezka”) nie idą dalej — ani do API, ani do kolejnego zapisu. Dziwna wartość pola = brak tego pola."""
    p = {"id": dane["id"], "tytul": _tekst_z_pliku(dane.get("tytul"), MAX_TYTUL) or dane["id"], "stan": dane["stan"]}
    for k, maks in (("opis", MAX_OPIS), ("etap", MAX_ETAP), ("komunikat", MAX_KOMUNIKAT)):
        p[k] = _tekst_z_pliku(dane.get(k), maks)
    p["kto"] = _kto(dane["kto"]) if isinstance(dane.get("kto"), str) else None
    etapy = dane.get("etapy")
    etapy = [x for x in (_tekst_z_pliku(e, MAX_ETAP) for e in etapy) if x][:MAX_ETAPY] if isinstance(etapy, list) else []
    p["etapy"] = etapy or None
    numer = dane.get("numer")
    p["numer"] = numer if isinstance(numer, int) and not isinstance(numer, bool) and 1 <= numer <= len(etapy) else None
    if etapy and p["numer"] is None:
        p["numer"] = 1
    for k in POLA_CZASU:
        p[k] = dane[k] if _czas(dane.get(k)) else None
    try:
        p["dotyczy"] = parsuj_dotyczy(dane["dotyczy"]) if isinstance(dane.get("dotyczy"), dict) else None
    except BladHTTP:
        p["dotyczy"] = None
    raport = dane.get("raport")
    p["raport"] = raport if isinstance(raport, str) and RX_RAPORT.match(raport) else None
    return {k: v for k, v in p.items() if v is not None}


def _czytaj_surowe(sciezka, proby=4):
    """JSON z pliku. Ponawia, gdy plik istnieje, ale chwilowo nie da się go przeczytać (inny proces właśnie go
    podmienia — na Windows os.replace daje wtedy PermissionError). → (dane albo None, czy_plik_istnieje)."""
    for proba in range(proby):
        try:
            with open(sciezka, encoding="utf-8-sig") as f:
                return json.load(f), True
        except FileNotFoundError:
            if proba == proby - 1 or not os.path.exists(sciezka):
                return None, False
        except (OSError, ValueError):
            if proba == proby - 1:
                return None, os.path.exists(sciezka)
        time.sleep(0.03 * (proba + 1))
    return None, os.path.exists(sciezka)


def _czytaj_plik(sciezka, nazwa):
    """Praca z pliku (oczyszczona) albo None (trwale zepsuty plik pomijany z wpisem w logu)."""
    dane, jest = _czytaj_surowe(sciezka)
    if not isinstance(dane, dict) or dane.get("id") != nazwa[:-5] or dane.get("stan") not in STANY:
        if jest:
            rdzen.log("prace: pomijam zepsuty plik pracy %s" % nazwa)
        return None
    return _oczysc(dane)


@contextlib.contextmanager
def _blokada(pid, czekaj_s=5.0):
    """Krótka blokada pracy na czas odczyt–zmiana–zapis (plik <id>.lock, os.open O_EXCL): dwa procesy zmieniające
    tę samą pracę naraz nie gubią swoich zmian. Blokada starsza niż 30 s (proces padł) jest zdejmowana."""
    sciezka = os.path.join(rdzen.upewnij_katalog(katalog()), pid + ".lock")
    koniec = time.time() + czekaj_s
    while True:
        try:
            fd = os.open(sciezka, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(sciezka) > 30:
                    os.remove(sciezka)
                    continue
            except OSError:
                pass
            if time.time() > koniec:
                raise BladHTTP(409, "Praca „%s” jest właśnie zmieniana — spróbuj za chwilę" % pid)
            time.sleep(0.02)
        except PermissionError:                                # plik blokady właśnie usuwany przez inny proces
            if time.time() > koniec:
                raise BladHTTP(409, "Praca „%s” jest właśnie zmieniana — spróbuj za chwilę" % pid)
            time.sleep(0.02)
    try:
        yield
    finally:
        try:
            os.remove(sciezka)
        except OSError:
            pass


def czytaj(pid):
    pid = sprawdz_id(pid)
    return _czytaj_plik(_sciezka(pid), pid + ".json")


def _wymagaj(pid):
    p = czytaj(pid)
    if not p:
        raise BladHTTP(404, "Nie ma pracy „%s” (lista: python panel/narzedzia/praca.py lista)" % pid)
    return p


def _zapisz(p, teraz=None):
    p["aktualizacja"] = _iso(_teraz(teraz))
    p = {k: v for k, v in p.items() if v is not None and v != [] and v != ""}
    with _zapis_lock:
        rdzen.zapisz_json(_sciezka(p["id"]), p)
    return p


def _pod_blokada(fn):
    """Zmiana pracy pod blokadą jej pliku (patrz _blokada); pierwszy argument to id pracy."""
    @functools.wraps(fn)
    def opakowana(pid, *args, **kwargs):
        pid = sprawdz_id(pid)
        with _blokada(pid):
            return fn(pid, *args, **kwargs)
    return opakowana


@_pod_blokada
def rozpocznij(pid, tytul, opis=None, etap=None, etapy=None, numer=None, koniec=None, dotyczy=None, kto=None,
               teraz=None):
    """Nowa praca (ten sam id = zaczyna się od nowa). `koniec` = tekst jak w parsuj_koniec albo None."""
    pid = sprawdz_id(pid)
    t = _teraz(teraz)
    etapy = _etapy(etapy)
    numer = _numer(numer, etapy)
    etap = _tekst(etap, "etap", MAX_ETAP)
    if etapy and numer is None:
        numer = etapy.index(etap) + 1 if etap in etapy else 1
    if not etap and etapy:
        etap = etapy[numer - 1]
    p = {"id": pid, "tytul": _tekst(tytul, "tytuł", MAX_TYTUL, wymagane=True),
         "opis": _tekst(opis, "opis", MAX_OPIS), "etap": etap, "etapy": etapy, "numer": numer,
         "start": _iso(t), "koniec_szacowany": parsuj_koniec(koniec, t) if koniec else None, "stan": "w_toku",
         "dotyczy": parsuj_dotyczy(dotyczy), "kto": _kto(kto)}
    p = _zapisz(p, t)
    rdzen.log("prace: start %s (%s)" % (pid, p["tytul"][:60]))
    return p


@_pod_blokada
def ustaw_etap(pid, etap=None, numer=None, koniec=None, teraz=None):
    p = _wymagaj(pid)
    t = _teraz(teraz)
    etapy = p.get("etapy") or None
    if numer is not None:
        p["numer"] = _numer(numer, etapy)
    etap = _tekst(etap, "etap", MAX_ETAP)
    if etap:
        p["etap"] = etap
        if etapy and numer is None and etap in etapy:          # nazwa z listy etapów = jej numer
            p["numer"] = etapy.index(etap) + 1
    elif numer is not None and etapy:
        p["etap"] = etapy[p["numer"] - 1]
    if etap is None and numer is None and koniec is None:
        raise BladHTTP(400, "Podaj nowy etap (--etap), numer (--numer) albo szacowany koniec (--koniec)")
    if koniec:
        p["koniec_szacowany"] = parsuj_koniec(koniec, t)
    if p["stan"] != "w_toku":                                  # nowy etap = praca znowu idzie
        p["stan"] = "w_toku"
        p.pop("zakonczono", None)
        p.pop("komunikat", None)
    return _zapisz(p, t)


@_pod_blokada
def zakoncz(pid, raport=None, komunikat=None, teraz=None):
    p = _wymagaj(pid)
    t = _teraz(teraz)
    if raport is not None:
        raport = str(raport).strip()
        if not RX_RAPORT.match(raport):
            raise BladHTTP(400, "Niepoprawny identyfikator raportu „%s”" % raport[:80])
        p["raport"] = raport
    p["komunikat"] = _tekst(komunikat, "komunikat", MAX_KOMUNIKAT)
    p["stan"] = "gotowe"
    p["zakonczono"] = _iso(t)
    if p.get("etapy"):
        p["numer"] = len(p["etapy"])
    p = _zapisz(p, t)
    rdzen.log("prace: koniec %s" % p["id"])
    return p


@_pod_blokada
def oznacz_blad(pid, komunikat, teraz=None):
    p = _wymagaj(pid)
    t = _teraz(teraz)
    p["komunikat"] = _tekst(komunikat, "komunikat", MAX_KOMUNIKAT, wymagane=True)
    p["stan"] = "blad"
    p["zakonczono"] = _iso(t)
    return _zapisz(p, t)


@_pod_blokada
def wstrzymaj(pid, komunikat=None, teraz=None):
    p = _wymagaj(pid)
    p["komunikat"] = _tekst(komunikat, "komunikat", MAX_KOMUNIKAT)
    p["stan"] = "wstrzymane"
    p.pop("zakonczono", None)
    return _zapisz(p, teraz)


@_pod_blokada
def wznow(pid, koniec=None, teraz=None):
    p = _wymagaj(pid)
    t = _teraz(teraz)
    p["stan"] = "w_toku"
    p.pop("zakonczono", None)
    p.pop("komunikat", None)
    if koniec:
        p["koniec_szacowany"] = parsuj_koniec(koniec, t)
    return _zapisz(p, t)


@_pod_blokada
def usun(pid):
    for proba in range(6):
        try:
            os.remove(_sciezka(pid))
            return True
        except FileNotFoundError:
            raise BladHTTP(404, "Nie ma pracy „%s”" % pid)
        except PermissionError:                                # serwer właśnie czyta plik
            if proba == 5:
                raise
            time.sleep(0.05 * (proba + 1))
    return True


# --------------------------------------------------------------------------- lista i pola wyliczane
def _zakonczona_dawno(p, t):
    if p.get("stan") not in ZAKONCZONE:
        return False
    k = _czas(p.get("zakonczono")) or _czas(p.get("aktualizacja"))
    return k is None or (t - k).total_seconds() > WIDOCZNE_PO_KONCU_S


POLA = ("id", "tytul", "opis", "etap", "etapy", "numer", "start", "koniec_szacowany", "stan", "komunikat", "dotyczy",
        "raport", "kto", "aktualizacja", "zakonczono")


def _wylicz(p, t):
    """Praca dla listy i API — tylko pola z listy POLA (oczyszczone przy odczycie, patrz _oczysc) plus pola wyliczane:
    zostalo_min / po_czasie_min, przeterminowana, postep (0–1 albo None)."""
    out = {k: p[k] for k in POLA if p.get(k) is not None}
    start = _czas(p.get("start"))
    koniec = _czas(p.get("koniec_szacowany"))
    stan = p.get("stan")
    out["zostalo_min"] = None
    out["po_czasie_min"] = None
    out["przeterminowana"] = False
    if koniec and stan in ("w_toku", "wstrzymane"):
        sek = (koniec - t).total_seconds()
        if sek >= 0:
            out["zostalo_min"] = int(math.ceil(sek / 60.0))
        else:
            out["po_czasie_min"] = int(-sek // 60)
            out["przeterminowana"] = stan == "w_toku"
    postep = None
    if stan == "gotowe":
        postep = 1.0
    elif koniec and start and koniec > start:
        postep = (t - start).total_seconds() / (koniec - start).total_seconds()
        postep = max(0.0, min(0.99, postep))                   # w toku nigdy pełne 100 %
    elif p.get("etapy") and p.get("numer"):
        postep = max(0.0, min(0.99, (int(p["numer"]) - 1) / float(len(p["etapy"]))))
    out["postep"] = round(postep, 3) if postep is not None else None
    return out


def _klucz_sortowania(p):
    stan = p.get("stan")
    if stan == "w_toku":
        k = _czas(p.get("koniec_szacowany"))
        s = _czas(p.get("start"))
        return (0, 0 if k else 1, k.timestamp() if k else 0.0, s.timestamp() if s else 0.0, p["id"])
    if stan in ("wstrzymane", "blad"):
        a = _czas(p.get("aktualizacja"))
        return (1, 0, -(a.timestamp() if a else 0.0), 0.0, p["id"])
    z = _czas(p.get("zakonczono")) or _czas(p.get("aktualizacja"))
    return (2, 0, -(z.timestamp() if z else 0.0), 0.0, p["id"])


def _wszystkie():
    out = []
    try:
        with os.scandir(katalog()) as it:
            for e in it:
                if not e.name.endswith(".json") or ".tmp" in e.name or not e.is_file():
                    continue
                if not RX_ID.match(e.name[:-5]):
                    continue
                p = _czytaj_plik(e.path, e.name)
                if p:
                    out.append(p)
    except OSError:
        pass
    return out


def lista(teraz=None):
    """Prace do pokazania: w toku (wg szacowanego końca), potem wstrzymane i z błędem, potem zakończone z 48 h."""
    t = _teraz(teraz)
    if time.time() - _sprzatanie["t"] > 600:                   # sprzątanie najwyżej co 10 min
        _sprzatanie["t"] = time.time()
        sprzataj(t)
    gotowe = []
    for p in _wszystkie():                                     # jedna dziwna praca nie wywraca całej listy
        try:
            if not _zakonczona_dawno(p, t):
                gotowe.append((_klucz_sortowania(p), _wylicz(p, t)))
        except Exception as e:                                 # noqa: BLE001
            rdzen.log("prace: pomijam pracę %s (%s)" % (p.get("id"), type(e).__name__))
    gotowe.sort(key=lambda x: x[0])
    return [w for _, w in gotowe]


def sprzataj(teraz=None):
    """Usuwa pliki prac zakończonych dawniej niż 48 h (i stare pliki tymczasowe). → liczba usuniętych."""
    t = _teraz(teraz)
    ile = 0
    for p in _wszystkie():
        if _zakonczona_dawno(p, t):
            try:
                os.remove(_sciezka(p["id"]))
                ile += 1
            except OSError:
                pass
    try:
        with os.scandir(katalog()) as it:
            for e in it:
                if e.name.endswith((".tmp", ".lock")) and time.time() - e.stat().st_mtime > 3600:
                    try:
                        os.remove(e.path)
                    except OSError:
                        pass
    except OSError:
        pass
    return ile


# --------------------------------------------------------------------------- trasy HTTP
def _get_prace(z):
    t = _teraz()
    prace = lista(t)
    w_toku = [p for p in prace if p.get("stan") == "w_toku"]
    konce = [(_czas(p.get("koniec_szacowany")), p["koniec_szacowany"]) for p in w_toku if p.get("koniec_szacowany")]
    konce = [(d.timestamp(), k) for d, k in konce if d]
    return {"prace": prace, "teraz": _iso(t), "w_toku": len(w_toku),
            "najblizszy_koniec": min(konce)[1] if konce else None}


def zarejestruj(app):
    app.dodaj("GET", "/api/prace", _get_prace)


def zdrowie():
    prace = lista()
    return {"ok": True, "prace": len(prace), "w_toku": sum(1 for p in prace if p.get("stan") == "w_toku"),
            "po_czasie": sum(1 for p in prace if p.get("przeterminowana"))}
