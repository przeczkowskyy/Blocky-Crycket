# -*- coding: utf-8 -*-
"""Mikro-framework HTTP panelu (sama biblioteka standardowa).

Moduł funkcjonalny (np. bc/raporty.py) definiuje funkcję `zarejestruj(app)` i dodaje w niej trasy:

    from .http import Odp, Strumien
    from .rdzen import BladHTTP

    def zarejestruj(app):
        app.dodaj("GET", "/api/raporty", lista)
        app.dodaj("POST", "/api/raporty/<id>/decyzja", decyzja)

    def lista(z):                      # z = Zadanie
        return {"raporty": [...]}      # dict / list -> JSON 200

    def decyzja(z):
        rid = z.params["id"]
        dane = z.json or {}            # ciało JSON (dict) albo None
        if "wartosc" not in dane:
            raise BladHTTP(400, "Brak pola wartosc")
        return 201, {"ok": True}       # (status, obiekt) -> JSON z tym statusem

Zwracane wartości handlera:
    dict / list            -> JSON 200
    (status, dict)         -> JSON ze statusem
    Odp.plik(sciezka)      -> plik z dysku (obsługuje Range dla audio/wideo)
    Odp.bajty(b, mime)     -> surowe bajty
    Odp.tekst(s)           -> text/plain
    Strumien(generator)    -> Server-Sent Events: generator zwraca słowniki (każdy = jedno zdarzenie `data: <json>`);
                              None = komentarz podtrzymujący połączenie — zwracaj go co <= 10 s, gdy nic się nie dzieje
    None                   -> 204

Pola Zadania: metoda, sciezka, query (dict), params (z wzorca trasy), naglowki, cialo (bytes), json, lokalny (bool —
żądanie z tego komputera), kto (nazwa osoby z nagłówka X-BC-Kto albo `git config user.name`), ip, game_director
(bool — żądanie niesie klucz Game Directora; tylko to, a nie imię, pozwala zmieniać kanon, np. statusy decyzji).
"""
import json
import mimetypes
import os
import re
import urllib.parse

from . import rdzen

MIME = {
    ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".mjs": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8", ".svg": "image/svg+xml",
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif",
    ".ico": "image/x-icon", ".woff2": "font/woff2", ".glb": "model/gltf-binary", ".md": "text/markdown; charset=utf-8",
    ".txt": "text/plain; charset=utf-8", ".map": "application/json", ".webm": "audio/webm", ".ogg": "audio/ogg",
    ".m4a": "audio/mp4", ".mp3": "audio/mpeg", ".wav": "audio/wav", ".mp4": "video/mp4",
}


def mime_pliku(sciezka):
    ext = os.path.splitext(sciezka)[1].lower()
    return MIME.get(ext) or mimetypes.guess_type(sciezka)[0] or "application/octet-stream"


class Zadanie:
    __slots__ = ("metoda", "sciezka", "query", "params", "naglowki", "cialo", "_json", "_json_ok", "lokalny", "kto",
                 "ip", "host", "game_director")

    def __init__(self, metoda, sciezka, query, naglowki, cialo, lokalny, kto, ip, host):
        self.metoda = metoda
        self.sciezka = sciezka
        self.query = query
        self.params = {}
        self.naglowki = naglowki
        self.cialo = cialo
        self._json = None
        self._json_ok = False
        self.lokalny = lokalny
        self.kto = kto
        self.ip = ip
        self.host = host
        self.game_director = False                             # ustawia serwer po sprawdzeniu klucza Game Directora

    @property
    def json(self):
        """Ciało jako JSON (zwykle dict) albo None, gdy puste lub niepoprawne."""
        if not self._json_ok:
            self._json_ok = True
            if self.cialo:
                try:
                    self._json = json.loads(self.cialo.decode("utf-8-sig"))
                except (ValueError, UnicodeDecodeError):
                    self._json = None
        return self._json

    def q(self, nazwa, domyslnie=None):
        return self.query.get(nazwa, domyslnie)

    def q_int(self, nazwa, domyslnie=0, minimum=None, maksimum=None):
        try:
            v = int(self.query.get(nazwa, domyslnie))
        except (TypeError, ValueError):
            v = domyslnie
        if minimum is not None:
            v = max(minimum, v)
        if maksimum is not None:
            v = min(maksimum, v)
        return v


class Odp:
    """Odpowiedź inna niż JSON."""

    def __init__(self, status=200, cialo=b"", mime="application/octet-stream", naglowki=None, plik=None):
        self.status = status
        self.cialo = cialo
        self.mime = mime
        self.naglowki = naglowki or {}
        self.plik_sciezka = plik

    @staticmethod
    def plik(sciezka, mime=None, pamiec_s=0):
        if not sciezka or not os.path.isfile(sciezka):
            raise rdzen.BladHTTP(404, "Nie ma takiego pliku")
        h = {"Cache-Control": ("max-age=%d" % pamiec_s) if pamiec_s else "no-cache"}
        return Odp(200, b"", mime or mime_pliku(sciezka), h, plik=sciezka)

    @staticmethod
    def bajty(dane, mime, status=200):
        return Odp(status, dane, mime)

    @staticmethod
    def tekst(tekst, status=200, mime="text/plain; charset=utf-8"):
        return Odp(status, tekst.encode("utf-8"), mime)

    @staticmethod
    def przekieruj(dokad, ciasteczko=None):
        """`ciasteczko` = jeden napis Set-Cookie albo lista (każde idzie osobnym nagłówkiem)."""
        h = {"Location": dokad}
        if ciasteczko:
            h["Set-Cookie"] = ciasteczko
        return Odp(302, b"", "text/plain", h)


class Strumien:
    """Server-Sent Events. `generator` zwraca dict (zdarzenie) albo None (podtrzymanie)."""

    def __init__(self, generator):
        self.generator = generator


class Aplikacja:
    def __init__(self):
        self._trasy = []                                       # (metoda, regex, fn, wzorzec)
        self.moduly = {}                                       # nazwa -> {"ok": bool, "blad": str|None}
        self.zdrowie = {}                                      # nazwa -> fn() -> dict (opcjonalne)

    @staticmethod
    def _regex(wzorzec):
        out = "^"
        for kawalek in re.split(r"(<[^>]+>)", wzorzec):
            if kawalek.startswith("<") and kawalek.endswith(">"):
                nazwa = kawalek[1:-1]
                if nazwa.endswith(":reszta"):                  # <sciezka:reszta> łapie także ukośniki
                    out += "(?P<%s>.+)" % nazwa[:-7]
                else:
                    out += "(?P<%s>[^/]+)" % nazwa
            else:
                out += re.escape(kawalek)
        return re.compile(out + "$")

    def dodaj(self, metoda, wzorzec, fn):
        """Rejestruje trasę. Wzorzec: "/api/raporty/<id>" albo "/api/pliki/<sciezka:reszta>"."""
        self._trasy.append((metoda.upper(), self._regex(wzorzec), fn, wzorzec))

    def znajdz(self, metoda, sciezka):
        inne_metody = False
        for m, rx, fn, _ in self._trasy:
            mt = rx.match(sciezka)
            if not mt:
                continue
            if m == metoda or (metoda == "HEAD" and m == "GET"):
                return fn, {k: urllib.parse.unquote(v) for k, v in mt.groupdict().items()}
            inne_metody = True
        return (None, "metoda") if inne_metody else (None, None)

    def lista_tras(self):
        return [{"metoda": m, "wzorzec": w} for m, _, _, w in self._trasy]
