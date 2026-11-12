# -*- coding: utf-8 -*-
"""Analityka gry: publiczne liczby z Roblox (gracze online, wizyty, ulubione, głosy), historia graczy z tego
komputera i stan konsoli Studio.

Do sieci wychodzi WYŁĄCZNIE numer universeId z konfiguracji (publiczne API games.roblox.com, bez logowania).
Odświeżamy najwyżej co 60 s i tylko wtedy, gdy ktoś pyta. Historia (próbka najwyżej co 5 min) leży lokalnie:
rdzen.RUNTIME/analityka/historia.jsonl — każdy komputer ma własną.
"""
import datetime
import json
import os
import threading
import time
import http.client
import urllib.error
import urllib.request

from . import rdzen

API_GRY = "https://games.roblox.com/v1/games?universeIds=%d"
API_GLOSOW = "https://games.roblox.com/v1/games/votes?universeIds=%d"
LIMIT_CZASU_S = 6
PAMIEC_S = 60
CO_ILE_PROBKA_S = 300
HISTORIA_H = 24
TRZYMAJ_DNI = 7
LINII_KONSOLI = 60

_blokada = threading.Lock()
_blokada_historii = threading.Lock()
_pamiec = {"t": 0.0, "uid": None, "gra": None}


def plik_historii():
    return os.path.join(rdzen.RUNTIME, "analityka", "historia.jsonl")


# --------------------------------------------------------------------------- Roblox
def _pobierz_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "bc-panel/%s" % rdzen.WERSJA,
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=LIMIT_CZASU_S) as r:
        return json.loads(r.read().decode("utf-8"))


def _uid_z_konfiguracji():
    gra = rdzen.konfiguracja().get("gra") or {}
    try:
        uid = int(gra.get("universeId"))
    except (TypeError, ValueError):
        uid = None
    try:
        place = int(gra.get("placeId")) if gra.get("placeId") else None
    except (TypeError, ValueError):
        place = None
    return uid if uid and uid > 0 else None, place, gra.get("nazwa")


def _pusta_gra(uid, place, nazwa):
    return {"universeId": uid, "placeId": place, "nazwa": nazwa, "gracze": 0, "wizyty": 0, "ulubione": 0,
            "zaktualizowano": None, "publiczna": False}


def interpretuj(uid, place, nazwa, dane_gry, dane_glosow=None):
    """Odpowiedzi API → pole `gra`. Gra prywatna/nieopublikowana: Roblox zwraca wpis z id 0 i „[TITLE UNAVAILABLE]”
    (albo pustą listę) — wtedy publiczna False i opis zamiast błędu."""
    wynik = _pusta_gra(uid, place, nazwa)
    wynik["zaktualizowano"] = rdzen.teraz()
    lista = (dane_gry or {}).get("data") or []
    wpis = next((d for d in lista if isinstance(d, dict) and str(d.get("id")) == str(uid)), None)
    if not wpis or "UNAVAILABLE" in str(wpis.get("name") or ""):
        wynik["opis"] = ("Gra jest prywatna albo jeszcze nieopublikowana — Roblox nie pokazuje jej liczb. "
                         "Dane pojawią się po publikacji.")
        return wynik
    wynik.update(publiczna=True, nazwa=wpis.get("name") or nazwa,
                 placeId=wpis.get("rootPlaceId") or place,
                 gracze=int(wpis.get("playing") or 0), wizyty=int(wpis.get("visits") or 0),
                 ulubione=int(wpis.get("favoritedCount") or 0))
    if wpis.get("maxPlayers"):
        wynik["max_graczy"] = int(wpis["maxPlayers"])
    for g in (dane_glosow or {}).get("data") or []:
        if isinstance(g, dict) and str(g.get("id")) == str(uid):
            wynik["glosy"] = {"za": int(g.get("upVotes") or 0), "przeciw": int(g.get("downVotes") or 0)}
    return wynik


def dane_gry():
    """Pole `gra` (pamięć 60 s). Nigdy nie rzuca."""
    uid, place, nazwa = _uid_z_konfiguracji()
    if not uid:
        g = _pusta_gra(None, place, nazwa)
        g["opis"] = "Brak universeId gry w panel/konfiguracja.json — uzupełnij, żeby widzieć liczby."
        return g
    with _blokada:
        if _pamiec["gra"] is not None and _pamiec["uid"] == uid and time.time() - _pamiec["t"] < PAMIEC_S:
            return _pamiec["gra"]
        try:
            dg = _pobierz_json(API_GRY % uid)
            gra = interpretuj(uid, place, nazwa, dg)
            if gra["publiczna"]:
                try:
                    gra = interpretuj(uid, place, nazwa, dg, _pobierz_json(API_GLOSOW % uid))
                except Exception:
                    pass                                   # głosy są dodatkiem
        except (urllib.error.URLError, OSError, ValueError, http.client.HTTPException) as e:
            poprzednia = _pamiec["gra"] if _pamiec["uid"] == uid else None
            gra = dict(poprzednia) if poprzednia else _pusta_gra(uid, place, nazwa)
            powod = getattr(e, "reason", None) or e
            gra["blad"] = "Nie udało się pobrać danych z Roblox (%s). Pokazuję ostatnie znane." % str(powod)[:120] \
                if poprzednia else "Nie udało się pobrać danych z Roblox (%s)." % str(powod)[:120]
            _pamiec.update(t=time.time() - PAMIEC_S + 15, uid=uid, gra=gra)   # ponów najwcześniej za 15 s
            return gra
        _pamiec.update(t=time.time(), uid=uid, gra=gra)
    if gra.get("publiczna"):
        dopisz_probke(gra["gracze"])
    return gra


# --------------------------------------------------------------------------- historia
def _czytaj_historie():
    try:
        with open(plik_historii(), encoding="utf-8") as f:
            linie = f.read().splitlines()
    except OSError:
        return []
    wynik = []
    for l in linie:
        try:
            d = json.loads(l)
            wynik.append({"t": str(d["t"]), "gracze": int(d["gracze"])})
        except (ValueError, KeyError, TypeError):
            continue
    return wynik


def _czas(iso):
    try:
        return datetime.datetime.fromisoformat(iso).timestamp()
    except (TypeError, ValueError):
        return 0.0


def dopisz_probke(gracze, teraz=None):
    """Dopisuje próbkę, jeśli od ostatniej minęło ≥ 5 min. Zwraca True, gdy dopisano."""
    teraz = teraz or time.time()
    with _blokada_historii:
        hist = _czytaj_historie()
        if hist and teraz - _czas(hist[-1]["t"]) < CO_ILE_PROBKA_S:
            return False
        t = datetime.datetime.fromtimestamp(teraz).astimezone().isoformat(timespec="seconds")
        sciezka = plik_historii()
        try:
            rdzen.upewnij_katalog(os.path.dirname(sciezka))
            if len(hist) > (TRZYMAJ_DNI * 24 * 12 + 500):   # przycinanie do 7 dni (rzadko)
                granica = teraz - TRZYMAJ_DNI * 86400
                hist = [h for h in hist if _czas(h["t"]) >= granica] + [{"t": t, "gracze": int(gracze)}]
                tekst = "".join(json.dumps(h, ensure_ascii=False) + "\n" for h in hist)
                rdzen.zapisz_bajty(sciezka, tekst.encode("utf-8"))
            else:
                with open(sciezka, "a", encoding="utf-8", newline="\n") as f:
                    f.write(json.dumps({"t": t, "gracze": int(gracze)}, ensure_ascii=False) + "\n")
        except OSError as e:
            rdzen.log("Analityka: nie mogę zapisać historii (%s)" % e)
            return False
        return True


def historia(godzin=HISTORIA_H):
    granica = time.time() - godzin * 3600
    with _blokada_historii:
        return [h for h in _czytaj_historie() if _czas(h["t"]) >= granica]


# --------------------------------------------------------------------------- Studio
def stan_studio():
    """Sekcja `studio`: połączenie, tryb, liczba błędów/ostrzeżeń i ostatnie 60 linii konsoli. Nie rzuca."""
    try:
        from . import studio
        st = studio.stan()
        if not st.get("polaczone"):
            return {"polaczone": False, "bledy": 0, "ostrzezenia": 0, "konsola": [],
                    "blad": st.get("blad") or "Roblox Studio nie jest połączone."}
        k = studio.konsola()
        wynik = {"polaczone": True, "tryb": (st.get("studio") or {}).get("tryb"),
                 "bledy": k.get("bledy", 0), "ostrzezenia": k.get("ostrzezenia", 0),
                 "konsola": (k.get("linie") or [])[-LINII_KONSOLI:]}
        if k.get("blad"):
            wynik["blad"] = k["blad"]
        return wynik
    except Exception as e:
        return {"polaczone": False, "bledy": 0, "ostrzezenia": 0, "konsola": [],
                "blad": "Nie mogę odczytać stanu Studio (%s)" % e}


TELEMETRIA = {"podlaczona": False,
              "opis": "Telemetria z gry nie jest jeszcze podłączona. Potrzebny jest skrypt w grze, który zapisuje "
                      "zdarzenia (np. wejścia, ukończone zadania) do magazynu danych, i odczyt przez Open Cloud."}
ROBUXY = {"dostepne": False,
          "opis": "Sprzedaży w Robuxach nie da się odczytać z publicznego API. Wymaga klucza Open Cloud właściciela "
                  "gry z uprawnieniami do statystyk — do podłączenia, gdy gra zacznie zarabiać."}


# --------------------------------------------------------------------------- trasy
def _analityka(z):
    wynik_studio = {}
    w = threading.Thread(target=lambda: wynik_studio.update(stan_studio()), daemon=True)
    w.start()                                              # Studio i Roblox odpytujemy równolegle
    gra = dane_gry()
    w.join(timeout=20)
    if not wynik_studio:
        wynik_studio = {"polaczone": False, "bledy": 0, "ostrzezenia": 0, "konsola": [],
                        "blad": "Studio nie odpowiedziało na czas."}
    return {"gra": gra, "historia": historia(), "studio": wynik_studio,
            "telemetria": dict(TELEMETRIA), "robuxy": dict(ROBUXY)}


def zarejestruj(app):
    app.dodaj("GET", "/api/analityka", _analityka)


def zdrowie():
    uid, _, _ = _uid_z_konfiguracji()
    g = _pamiec["gra"]
    return {"universeId": uid, "ostatnie_pobranie": g.get("zaktualizowano") if g else None,
            "publiczna": g.get("publiczna") if g else None, "probki_24h": len(historia())}
