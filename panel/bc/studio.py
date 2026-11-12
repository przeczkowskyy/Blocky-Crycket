# -*- coding: utf-8 -*-
"""Sesja MCP z Roblox Studio — jedna, współdzielona przez cały panel.

Mostek MCP Studio (`%LOCALAPPDATA%\\Roblox\\mcp.bat`) rozmawia przez stdio; klient jest w `tools/studio_mcp.py`.
Ten moduł trzyma JEDNĄ sesję (blokada), łączy się leniwie przy pierwszym pytaniu, po błędzie zamyka sesję i przy
następnym pytaniu łączy się od nowa, a gdy Studio odpowie „studio_id is not connected” (miejsce otwarte ponownie),
odświeża identyfikator okna i ponawia raz.

API dla innych modułów (nazwy są kontraktem):
    stan(odswiez=False) -> dict      jak GET /api/studio/stan (pamięć 10 s, nigdy nie rzuca, najwyżej ~8 s)
    luau(kod, dm="Edit", timeout=60) -> str      wynik execute_luau; BladHTTP(503) gdy Studio niedostępne
    zrzut(pozycja=None, cel=None) -> bytes       obraz z widoku Studio (screen_capture; PNG albo JPG — patrz magia)
    konsola() -> dict                jak GET /api/studio/konsola (pamięć 5 s)
    zdrowie() -> dict                {mostek, polaczone, blad?}

Panel z Studio wyłącznie CZYTA: kod Luau wysyłany przez panel niczego nie tworzy ani nie zmienia.
"""
import json
import os
import re
import sys
import threading
import time

from . import rdzen
from .rdzen import BladHTTP

LIMIT_STANU_S = 8.0                     # stan() nie może wisieć dłużej
PAMIEC_STANU_S = 10.0
PAMIEC_KONSOLI_S = 5.0
MAKS_LINII_KONSOLI = 400

_blokada = threading.RLock()            # jedna rozmowa z mostkiem naraz
_sesja = {"mcp": None, "studio_id": None, "studio": None, "start": 0.0, "nr_zrzutu": 0}
_pamiec_stanu = {"t": 0.0, "v": None}
_pamiec_konsoli = {"t": 0.0, "v": None}
_klasa = {"mod": None}


# --------------------------------------------------------------------------- mostek i klient
def _klient():
    """Moduł tools/studio_mcp.py (import leniwy — nic ciężkiego przy starcie panelu)."""
    if _klasa["mod"] is None:
        sciezka = os.path.join(rdzen.REPO, "tools")
        if sciezka not in sys.path:
            sys.path.insert(0, sciezka)
        import studio_mcp  # noqa: E402
        _klasa["mod"] = studio_mcp
    return _klasa["mod"]


def mostek_istnieje():
    if os.environ.get("STUDIO_MCP_CMD"):
        return True
    if os.name == "nt":
        return os.path.isfile(os.path.join(os.environ.get("LOCALAPPDATA", ""), "Roblox", "mcp.bat"))
    return os.path.isfile(os.path.expanduser("~/Library/Application Support/Roblox/mcp.sh"))


def _zamknij_sesje():
    mcp = _sesja["mcp"]
    _sesja.update(mcp=None, studio_id=None, studio=None)
    if mcp is not None:
        def _zamknij():
            try:
                mcp.close()                                # close() potrafi czekać do 3 s na koniec procesu
            except Exception:
                pass
        threading.Thread(target=_zamknij, daemon=True).start()


def _polacz(limit_s):
    """Zwraca żywą sesję (startuje mostek, jeśli trzeba). Rzuca StudioError."""
    mcp = _sesja["mcp"]
    if mcp is not None and mcp.alive():
        return mcp
    _zamknij_sesje()
    mod = _klient()
    mcp = mod.StudioMCP(timeout=max(2.0, limit_s))
    _sesja.update(mcp=mcp, start=time.time())
    try:
        mcp.start()
    except Exception:
        _zamknij_sesje()                                   # zamyka w tle — nie przedłużamy czekania
        raise
    return mcp


def _lista_okien(mcp, limit_s):
    """Lista okien Studio. Świeży mostek potrzebuje chwili, żeby je zobaczyć — wtedy ponawiamy do limitu."""
    koniec = time.time() + limit_s
    while True:
        r = mcp.call("list_roblox_studios", {}, timeout=max(1.0, koniec - time.time()))
        try:
            d = json.loads(r["text"] or "[]")
        except ValueError:
            d = []
        lst = d if isinstance(d, list) else (d.get("studios") or d.get("instances") or [])
        lst = [s for s in lst if isinstance(s, dict)]
        swiezy = time.time() - _sesja["start"] < 15
        if lst or not swiezy or time.time() + 0.5 >= koniec:
            return lst
        time.sleep(0.5)


def _wybierz_okno(lst):
    """Okno z placeId gry z konfiguracji, a jeśli go nie ma — pierwsze."""
    place = (rdzen.konfiguracja().get("gra") or {}).get("placeId")
    for s in lst:
        if place and str(s.get("placeId")) == str(place):
            return s
    return lst[0] if lst else None


def _odswiez_okno(mcp, limit_s):
    okno = _wybierz_okno(_lista_okien(mcp, limit_s))
    if okno is None:
        _sesja.update(studio_id=None, studio=None)
        return None
    _sesja.update(studio_id=okno.get("id") or okno.get("studio_id") or okno.get("studioId"), studio=okno)
    return okno


def _niepolaczone(tekst):
    return "not connected" in (tekst or "") or "studio_id" in (tekst or "") and "list_roblox_studios" in (tekst or "")


def _czysty_blad_luau(tekst):
    """Usuwa z błędu Luau wewnętrzne ścieżki Asystenta Studio (zostaje „AssistantCommand:3: …”)."""
    t = (tekst or "").strip()
    i = t.rfind("AssistantCommand:")
    return t[i:] if i >= 0 else t[:500]


def _wywolaj(nazwa, argumenty, timeout, limit_polaczenia=8.0):
    """Wywołuje narzędzie MCP na wybranym oknie Studio. Wymaga trzymanej blokady. Rzuca BladHTTP(503)."""
    mod = _klient()
    for proba in range(2):
        try:
            mcp = _polacz(limit_polaczenia)
            if not _sesja["studio_id"]:
                if _odswiez_okno(mcp, min(limit_polaczenia, 6.0)) is None:
                    raise BladHTTP(503, "Roblox Studio nie jest otwarte (albo nie ma włączonego serwera MCP).")
            arg = dict(argumenty or {})
            arg["studio_id"] = _sesja["studio_id"]
            r = mcp.call(nazwa, arg, timeout=timeout)
        except mod.StudioError as e:
            _zamknij_sesje()
            if proba == 0 and "Brak odpowiedzi" not in str(e):
                continue                                   # mostek padł między pytaniami — jedno ponowienie
            raise BladHTTP(503, "Brak połączenia z Roblox Studio: %s" % e)
        if r["is_error"] and _niepolaczone(r["text"]):
            _sesja.update(studio_id=None, studio=None)     # okno zamknięte lub miejsce otwarte ponownie
            if proba == 0:
                continue
            raise BladHTTP(503, "Roblox Studio nie ma otwartego miejsca (okno zamknięte?).")
        return r
    raise BladHTTP(503, "Brak połączenia z Roblox Studio.")


def _zablokuj(limit_s):
    if not _blokada.acquire(timeout=max(0.1, limit_s)):
        raise BladHTTP(503, "Studio jest teraz zajęte innym zadaniem panelu (np. migawką). Spróbuj za chwilę.")


# --------------------------------------------------------------------------- API modułu
def luau(kod, dm="Edit", timeout=60):
    """Wykonuje kod Luau w Studio i zwraca tekst wyniku (pierwsza wartość `return`, ucięta przez Studio do ~100 kB).
    BladHTTP(503) gdy Studio niedostępne, BladHTTP(502) gdy kod zgłosił błąd."""
    _zablokuj(timeout)
    try:
        r = _wywolaj("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=timeout)
    finally:
        _blokada.release()
    if r["is_error"]:
        raise BladHTTP(502, "Kod Luau w Studio zgłosił błąd: %s" % _czysty_blad_luau(r["text"]))
    return r["text"]


def zrzut(pozycja=None, cel=None, timeout=60):
    """Zrzut widoku Studio. `pozycja`/`cel` = [x,y,z] — kamera jest na chwilę przestawiana i wraca na miejsce.
    Zwraca bajty obrazu (Studio zwykle oddaje JPG; rozpoznaj po nagłówku)."""
    _zablokuj(timeout)
    try:
        _sesja["nr_zrzutu"] += 1
        arg = {"capture_id": "ScreenCapture_%d" % _sesja["nr_zrzutu"]}
        if pozycja is not None and cel is not None:
            arg["camera_position"] = [float(v) for v in pozycja]
            arg["look_at_position"] = [float(v) for v in cel]
        r = _wywolaj("screen_capture", arg, timeout=timeout)
    finally:
        _blokada.release()
    if r["is_error"] or not r["images"]:
        raise BladHTTP(502, "Studio nie zwróciło zrzutu ekranu: %s" % (r["text"] or "brak obrazu")[:300])
    return r["images"][0]


_KOD_STANU = r'''
local HS = game:GetService("HttpService")
local osoby = {}
for _, p in game:GetService("Players"):GetPlayers() do
    table.insert(osoby, {nazwa = p.Name, id = p.UserId})
end
return HS:JSONEncode({osoby = osoby, nazwa = game.Name, placeId = game.PlaceId, universeId = game.GameId})
'''


def stan(odswiez=False):
    """{mostek, polaczone, studio?:{id, placeId, universeId, tryb, nazwa}, osoby:[{nazwa,id}], blad?}. Nie rzuca."""
    teraz = time.time()
    p = _pamiec_stanu["v"]
    if p is not None and not odswiez and teraz - _pamiec_stanu["t"] < PAMIEC_STANU_S:
        return p
    if not mostek_istnieje():
        wynik = {"mostek": False, "polaczone": False, "osoby": [],
                 "blad": "Brak mostka MCP Roblox Studio. W Studio: Assistant → … → Manage MCP Servers → "
                         "Enable Studio as MCP server."}
        _pamiec_stanu.update(t=teraz, v=wynik)
        return wynik
    start = time.time()
    if not _blokada.acquire(timeout=LIMIT_STANU_S - 1.0):
        # ktoś długo rozmawia ze Studio (np. migawka) — oddaj ostatni znany stan zamiast czekać
        if p is not None:
            return dict(p, zajete=True)
        return {"mostek": True, "polaczone": False, "osoby": [], "zajete": True,
                "blad": "Studio jest teraz zajęte innym zadaniem panelu (np. migawką). Spróbuj za chwilę."}
    try:
        zostalo = lambda: max(0.5, LIMIT_STANU_S - (time.time() - start))  # noqa: E731
        try:
            mcp = _polacz(max(2.0, zostalo() - 2.5))       # zostaw czas na listę okien i osoby
            okno = _odswiez_okno(mcp, min(4.0, zostalo()))
        except Exception as e:
            _zamknij_sesje()
            wynik = {"mostek": True, "polaczone": False, "osoby": [],
                     "blad": "Nie mogę połączyć się z Roblox Studio — czy jest uruchomione? (%s)" % _krotko(e)}
            _pamiec_stanu.update(t=time.time(), v=wynik)
            return wynik
        if okno is None:
            wynik = {"mostek": True, "polaczone": False, "osoby": [],
                     "blad": "Roblox Studio nie jest otwarte (albo nie ma włączonego serwera MCP)."}
            _pamiec_stanu.update(t=time.time(), v=wynik)
            return wynik
        studio = {"id": _sesja["studio_id"], "placeId": okno.get("placeId"), "universeId": okno.get("universeId"),
                  "tryb": okno.get("mode") or "Edit", "nazwa": okno.get("name") or okno.get("file") or None}
        wynik = {"mostek": True, "polaczone": True, "studio": studio, "osoby": []}
        try:
            r = mcp.call("execute_luau", {"code": _KOD_STANU, "datamodel_type": "Edit",
                                          "studio_id": _sesja["studio_id"]}, timeout=zostalo())
            if not r["is_error"]:
                d = json.loads(r["text"])
                wynik["osoby"] = [{"nazwa": o.get("nazwa"), "id": o.get("id")} for o in d.get("osoby") or []]
                if not studio["nazwa"]:
                    studio["nazwa"] = d.get("nazwa")
                studio["placeId"] = studio["placeId"] or d.get("placeId") or None
                studio["universeId"] = studio["universeId"] or d.get("universeId") or None
            elif _niepolaczone(r["text"]):
                _sesja.update(studio_id=None, studio=None)
        except Exception as e:                             # osoby to dodatek — stan i tak jest znany
            if isinstance(e, _klient().StudioError):
                _zamknij_sesje()
            wynik["blad"] = "Nie udało się odczytać osób w Studio (%s)" % _krotko(e)
        _pamiec_stanu.update(t=time.time(), v=wynik)
        return wynik
    finally:
        _blokada.release()


def _krotko(e):
    t = str(e) or e.__class__.__name__
    return t if len(t) < 200 else t[:200] + "…"


# --------------------------------------------------------------------------- konsola
_RX_LINIA_SKRYPTU = re.compile(r"^[\w .\-\[\]\"']+:\d+: ")        # „Workspace.Skrypt:12: attempt to …”
_RX_BLAD = re.compile(r"(?i)(\berror\b|\bbłąd\b|\bexception\b|attempt to |lacking capability|is not a valid member"
                      r"|failed to load|stack overflow)")
_RX_OSTRZ = re.compile(r"(?i)(\bwarning\b|\bostrzeżenie\b|\bdeprecated\b|infinite yield possible|\bwarn:)")


def parsuj_konsole(tekst, maks=MAKS_LINII_KONSOLI):
    """Tekst z get_console_output → {linie:[{poziom, tekst}], bledy, ostrzezenia}.

    Studio nie podaje poziomów w tekście, więc rozpoznajemy je: blok „Stack Begin … Stack End” oznacza, że linia
    przed nim była błędem (ślad stosu doklejamy do niej); do tego typowe sformułowania błędów i ostrzeżeń."""
    linie = []
    w_stosie = False
    for surowa in (tekst or "").replace("\r\n", "\n").split("\n"):
        t = surowa.rstrip()
        if not t.strip():
            continue
        if t.strip() == "Stack Begin":
            w_stosie = True
            if linie and linie[-1]["poziom"] != "blad":
                linie[-1]["poziom"] = "blad"
            continue
        if t.strip() == "Stack End":
            w_stosie = False
            continue
        if w_stosie:
            if linie:
                linie[-1]["tekst"] += "\n  " + t.strip()
            continue
        if _RX_BLAD.search(t) or _RX_LINIA_SKRYPTU.match(t):
            poziom = "blad"
        elif _RX_OSTRZ.search(t):
            poziom = "ostrzezenie"
        else:
            poziom = "info"
        linie.append({"poziom": poziom, "tekst": t[:2000]})
    linie = linie[-maks:]
    return {"linie": linie,
            "bledy": sum(1 for l in linie if l["poziom"] == "blad"),
            "ostrzezenia": sum(1 for l in linie if l["poziom"] == "ostrzezenie")}


def konsola():
    """{linie:[{poziom, tekst}], bledy, ostrzezenia, polaczone, blad?} — pamięć 5 s. Nie rzuca."""
    teraz = time.time()
    p = _pamiec_konsoli["v"]
    if p is not None and teraz - _pamiec_konsoli["t"] < PAMIEC_KONSOLI_S:
        return p
    st = stan()
    if not st.get("polaczone"):
        wynik = {"linie": [], "bledy": 0, "ostrzezenia": 0, "polaczone": False,
                 "blad": st.get("blad") or "Roblox Studio nie jest połączone."}
        _pamiec_konsoli.update(t=time.time(), v=wynik)
        return wynik
    try:
        _zablokuj(LIMIT_STANU_S - 1.0)
        try:
            r = _wywolaj("get_console_output", {}, timeout=LIMIT_STANU_S)
        finally:
            _blokada.release()
        if r["is_error"]:
            raise BladHTTP(502, (r["text"] or "")[:300])
        wynik = parsuj_konsole(r["text"])
        wynik["polaczone"] = True
    except BladHTTP as e:
        if p is not None:
            return dict(p, blad=e.komunikat)
        wynik = {"linie": [], "bledy": 0, "ostrzezenia": 0, "polaczone": False, "blad": e.komunikat}
    _pamiec_konsoli.update(t=time.time(), v=wynik)
    return wynik


# --------------------------------------------------------------------------- trasy
def _trasa_stan(z):
    return stan(odswiez=z.q("odswiez") in ("1", "true", "tak"))


def _trasa_konsola(z):
    return konsola()


def zarejestruj(app):
    app.dodaj("GET", "/api/studio/stan", _trasa_stan)
    app.dodaj("GET", "/api/studio/konsola", _trasa_konsola)


def zdrowie():
    st = stan()
    wynik = {"mostek": st.get("mostek"), "polaczone": st.get("polaczone")}
    if st.get("blad"):
        wynik["blad"] = st["blad"]
    return wynik


def _sprzatanie():
    try:
        _zamknij_sesje()
    except Exception:
        pass


import atexit  # noqa: E402

atexit.register(_sprzatanie)
