# -*- coding: utf-8 -*-
"""Obecność: kto jest teraz na panelu, kto siedzi w Roblox Studio (Team Create) i kto ostatnio coś wysłał do gita.

- Pulsy przeglądarek trzymamy tylko w pamięci (klucz: identyfikator klienta, do 64 znaków; puls żyje 45 s).
- Sekcja `studio` pyta moduł bc/studio.py (`studio.stan()`); jego brak, brak funkcji albo wyjątek = Studio niedostępne.
  Wywołanie idzie w osobnym wątku i czekamy na nie najwyżej 2,5 s — zawieszone Studio nie zablokuje panelu.
- Sekcja `git`: ostatni commit każdego autora z `git log` (pamięć 60 s).
"""
import datetime
import threading
import time

from . import gitsync
from .rdzen import BladHTTP

ZYCIE_PULSU_S = 45.0
MAKS_KLIENTOW = 200
PAMIEC_GITA_S = 60.0
CZEKANIE_NA_STUDIO_S = 2.5
NIEDOSTEPNE = {"dostepne": False, "osoby": []}

_pulsy = {}                                                    # klient -> {kto, widok, od, ostatnio(ts), lokalny}
_pulsy_blokada = threading.Lock()
_studio = {"wynik": None, "watek": None}
_studio_blokada = threading.Lock()
_git = {"t": 0.0, "wynik": None}
_git_blokada = threading.Lock()


def _iso(ts):
    return datetime.datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")


# --------------------------------------------------------------------------- panel
def _sprzataj(teraz):
    for k in [k for k, p in _pulsy.items() if teraz - p["ostatnio"] > ZYCIE_PULSU_S]:
        _pulsy.pop(k, None)


def zapisz_puls(klient, kto, widok, lokalny):
    teraz = time.time()
    with _pulsy_blokada:
        _sprzataj(teraz)
        stary = _pulsy.get(klient)
        if stary is None and len(_pulsy) >= MAKS_KLIENTOW:     # ochrona pamięci: wypada najstarszy puls
            najstarszy = min(_pulsy, key=lambda k: _pulsy[k]["ostatnio"])
            _pulsy.pop(najstarszy, None)
        _pulsy[klient] = {"kto": kto, "widok": widok, "od": stary["od"] if stary else teraz, "ostatnio": teraz,
                          "lokalny": bool(lokalny)}


def panel():
    teraz = time.time()
    with _pulsy_blokada:
        _sprzataj(teraz)
        lista = sorted(_pulsy.values(), key=lambda p: -p["ostatnio"])
        return [{"kto": p["kto"], "widok": p["widok"], "od": _iso(p["od"]), "ostatnio": _iso(p["ostatnio"]),
                 "lokalny": p["lokalny"]} for p in lista]


# --------------------------------------------------------------------------- studio
def _przeloz_studio(d):
    """Słownik jak GET /api/studio/stan -> {dostepne, osoby:[{nazwa, id}], tryb?}."""
    if not isinstance(d, dict):
        return dict(NIEDOSTEPNE)
    osoby = []
    for o in d.get("osoby") or []:
        if isinstance(o, dict):
            osoby.append({"nazwa": str(o.get("nazwa") or o.get("name") or "?"), "id": o.get("id")})
        elif isinstance(o, str):
            osoby.append({"nazwa": o, "id": None})
    wynik = {"dostepne": bool(d.get("polaczone")), "osoby": osoby}
    info = d.get("studio")
    if isinstance(info, dict) and info.get("tryb"):
        wynik["tryb"] = info.get("tryb")
    return wynik


def _odswiez_studio():
    try:
        from . import studio                                   # moduł pisze inny agent — może go jeszcze nie być
        fn = getattr(studio, "stan", None)
        wynik = _przeloz_studio(fn()) if callable(fn) else dict(NIEDOSTEPNE)
    except Exception:
        wynik = dict(NIEDOSTEPNE)
    _studio["wynik"] = wynik


def studio_stan():
    with _studio_blokada:
        w = _studio["watek"]
        if w is not None and w.is_alive():                     # poprzednie pytanie jeszcze trwa: nie czekamy
            return _studio["wynik"] or dict(NIEDOSTEPNE)
        w = threading.Thread(target=_odswiez_studio, name="obecnosc-studio", daemon=True)
        _studio["watek"] = w
        w.start()
    w.join(CZEKANIE_NA_STUDIO_S)
    return _studio["wynik"] or dict(NIEDOSTEPNE)


# --------------------------------------------------------------------------- git
def git_autorzy(repo=None):
    """Ostatni commit każdego autora: [{autor, ostatnio, temat}] (najświeższy pierwszy, pamięć 60 s)."""
    with _git_blokada:
        if _git["wynik"] is not None and time.time() - _git["t"] < PAMIEC_GITA_S:
            return _git["wynik"]
    kod, out, _ = gitsync.git(["log", "-n", "500", "--format=%an%x1f%aI%x1f%s"], repo, timeout=15)
    wynik, widziani = [], set()
    if kod == 0:
        for linia in out.splitlines():
            cz = linia.split("\x1f")
            if len(cz) < 3 or cz[0] in widziani:
                continue
            widziani.add(cz[0])
            wynik.append({"autor": cz[0], "ostatnio": cz[1], "temat": cz[2]})
        wynik.sort(key=lambda w: w["ostatnio"], reverse=True)
    with _git_blokada:
        _git.update(t=time.time(), wynik=wynik)
    return wynik


# --------------------------------------------------------------------------- trasy
def obecnosc():
    return {"panel": panel(), "studio": studio_stan(), "git": git_autorzy()}


def _t_puls(z):
    dane = z.json if isinstance(z.json, dict) else {}
    klient = str(dane.get("klient") or "").strip()[:64]
    if not klient:
        raise BladHTTP(400, "Brak pola klient (identyfikator karty przeglądarki)")
    widok = str(dane.get("widok") or "").strip()[:40]
    zapisz_puls(klient, z.kto, widok, z.lokalny)
    return obecnosc()


def _t_obecnosc(z):
    return obecnosc()


def zarejestruj(app):
    app.dodaj("POST", "/api/obecnosc/puls", _t_puls)
    app.dodaj("GET", "/api/obecnosc", _t_obecnosc)


def zdrowie():
    try:
        from . import studio  # noqa: F401
        studio_ok = callable(getattr(studio, "stan", None))
    except Exception:
        studio_ok = False
    return {"na_panelu": len(panel()), "modul_studio": studio_ok}
