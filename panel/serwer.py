#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BLOCKY & CRYCKET — Panel zespołu. Serwer lokalny w czystym Pythonie (bez zależności).

Uruchomienie:
    python panel/serwer.py                 # http://127.0.0.1:8787 (tylko ten komputer)
    python panel/serwer.py --lan           # także telefon / drugi komputer w tej samej sieci (wymaga kodu dostępu)
    python panel/serwer.py --sprawdz       # sprawdza środowisko i kończy (dla instalacji)
    python panel/serwer.py --port 8790 --bez-przegladarki

Bezpieczeństwo (wzorzec z panelu Saga Studio):
- domyślnie nasłuch tylko na 127.0.0.1; `--lan` otwiera 0.0.0.0, ale każde żądanie spoza tego komputera wymaga
  kodu dostępu (ciasteczko po wejściu przez link z kodem);
- nagłówek Host musi być znany (ochrona przed DNS-rebinding); każdy POST wymaga nagłówka `X-BC: 1`, a Origin —
  jeśli jest — musi być własny (ochrona przed CSRF);
- prawa osoby przy komputerze („lokalny”) daje dopiero KLUCZ LOKALNY: ciasteczko ustawiane przez adres z kluczem,
  który panel otwiera w przeglądarce przy starcie (jak Jupyter). Samo połączenie z pętli zwrotnej nie wystarcza, bo
  przekierowanie portu (ssh -R, ngrok tcp, netsh portproxy) też przychodzi z 127.0.0.1. Żądanie bez klucza —
  także z tego komputera — potrzebuje zwykłego kodu dostępu i ma prawa osoby zdalnej;
- zmianę kanonu z panelu (status decyzji) daje wyłącznie KLUCZ GAME DIRECTORA: osobny sekret w danych lokalnych
  (`klucz_gd.txt`, tworzy go `--klucz-gd`), przyniesiony adresem `/?gd=<klucz>` (zamieniany na ciasteczko bc_gd
  i usuwany z adresu) albo nagłówkiem X-BC-GD. Działa też przez tunel, ale zawsze OBOK zwykłego dostępu (kod dostępu
  albo klucz lokalny) — nie zastępuje go. Nieudane próby liczą się do tego samego limitu co kod dostępu.
"""
import argparse
import hmac
import http.server
import importlib
import json
import os
import re
import secrets
import shutil
import socket
import sys
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bc import rdzen  # noqa: E402
from bc.http import Aplikacja, Odp, Strumien, Zadanie, mime_pliku  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402

MODULY = ["sejf", "zapis", "gitsync", "obecnosc", "studio", "podglad", "analityka", "telemetria", "assety", "raporty",
          "agent", "glos", "statyczny"]
ROZSZERZENIA_STATIC = {".html", ".js", ".mjs", ".css", ".json", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico",
                       ".woff2", ".glb", ".md", ".txt", ".map"}
LIMIT_JSON = 4 * 1024 * 1024
LIMIT_BINARNY = 100 * 1024 * 1024
NAGLOWKI_POSREDNIKA = ("X-Forwarded-For", "Forwarded", "Cf-Connecting-Ip", "Cf-Ray", "X-Real-Ip", "X-Forwarded-Host")
CSP = ("default-src 'self'; img-src 'self' data: blob:; media-src 'self' blob:; style-src 'self' 'unsafe-inline'; "
       "script-src 'self'; connect-src 'self'; worker-src 'self' blob:; frame-ancestors 'none'; base-uri 'none'")

STAN = {"start": None, "port": None, "lan": False, "token": None, "klucz_lokalny": None, "hosty": set(), "adresy_lan": []}
APP = Aplikacja()
_proby = {}                                                    # ip -> [czasy nieudanych prób kodu]
_proby_lock = threading.Lock()


# --------------------------------------------------------------------------- kod dostępu i hosty
def _token():
    sciezka = os.path.join(rdzen.RUNTIME, "token.txt")
    t = (rdzen.czytaj_tekst(sciezka) or "").strip()
    if len(t) < 20:
        t = secrets.token_urlsafe(24)
        rdzen.upewnij_katalog(rdzen.RUNTIME)
        with open(sciezka, "w", encoding="utf-8") as f:
            f.write(t + "\n")
    return t


def _klucz_lokalny():
    """Sekret dający prawa osoby przy komputerze. Leży w danych lokalnych; przeglądarka dostaje go ciasteczkiem."""
    sciezka = os.path.join(rdzen.RUNTIME, "klucz_lokalny.txt")
    t = (rdzen.czytaj_tekst(sciezka) or "").strip()
    if len(t) < 20:
        t = secrets.token_urlsafe(24)
        rdzen.upewnij_katalog(rdzen.RUNTIME)
        with open(sciezka, "w", encoding="utf-8") as f:
            f.write(t + "\n")
    return t


_gd_pamiec = {"stan": None, "klucz": None}


def _plik_klucza_gd():
    return os.path.join(rdzen.RUNTIME, "klucz_gd.txt")


def _klucz_gd():
    """Klucz Game Directora albo None, gdy go nie utworzono (wtedy nikt nie zmienia kanonu z panelu).
    Czytany przy każdym żądaniu (z pamięcią po czasie zmiany pliku) — nowy klucz działa bez restartu panelu."""
    sciezka = _plik_klucza_gd()
    try:
        st = os.stat(sciezka)
        stan = (st.st_mtime_ns, st.st_size)
    except OSError:
        return None
    if _gd_pamiec["stan"] != stan:
        t = (rdzen.czytaj_tekst(sciezka) or "").strip()
        _gd_pamiec.update(stan=stan, klucz=t if len(t) >= 20 else None)
    return _gd_pamiec["klucz"]


def utworz_klucz_gd(nowy=False):
    """Zwraca klucz Game Directora; tworzy go, gdy go nie ma (albo zawsze, z nowy=True — stary przestaje działać)."""
    sciezka = _plik_klucza_gd()
    t = "" if nowy else (rdzen.czytaj_tekst(sciezka) or "").strip()
    if len(t) < 20:
        t = secrets.token_urlsafe(24)
        rdzen.upewnij_katalog(rdzen.RUNTIME)
        with open(sciezka, "w", encoding="utf-8") as f:
            f.write(t + "\n")
    return t


def wypisz_link_gd(nowy=False):
    """Polecenie --klucz-gd: wypisuje link Game Directora (klucz w danych lokalnych tego komputera)."""
    klucz = utworz_klucz_gd(nowy)
    port = int(rdzen.konfiguracja().get("port") or 8787)
    print("Klucz Game Directora %s. Tylko z nim panel pozwala zatwierdzać i odrzucać decyzje (zmiana kanonu)."
          % ("utworzony na nowo (stary już nie działa)" if nowy else "gotowy"))
    print("\n  Na tym komputerze (przeglądarka, w której działa już panel):\n    http://127.0.0.1:%d/?gd=%s" % (port, klucz))
    print("\n  Przez tunel albo telefon: do adresu z kodem dostępu dopisz  &gd=%s" % klucz)
    print("    np. https://<adres-tunelu>/?k=<kod dostępu>&gd=%s" % klucz)
    print("\nPrzeglądarka zapamięta klucz (ciasteczko) i usunie go z adresu. Link działa jak hasło — przekaż go tylko\n"
          "Game Directorowi, nie wklejaj w publicznych miejscach (repozytorium jest publiczne).\n"
          "Unieważnienie i nowy klucz: python panel/serwer.py --nowy-klucz-gd")
    return 0


def _adresy_lan():
    adresy = set()
    try:
        for a in socket.gethostbyname_ex(socket.gethostname())[2]:
            adresy.add(a)
    except OSError:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))                       # nic nie wysyła — tylko wybiera interfejs
        adresy.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    return sorted(a for a in adresy if not a.startswith("127."))


def _host_dozwolony(host):
    """host = wartość nagłówka Host małymi literami."""
    if not host:
        return False
    if host.startswith("["):
        nazwa, _, port = host.partition("]")
        nazwa += "]"
        port = port.lstrip(":")
    else:
        nazwa, _, port = host.partition(":")
    if nazwa in ("127.0.0.1", "localhost", "[::1]"):
        return port in ("", str(STAN["port"]))
    if nazwa in STAN["hosty"]:
        return True
    for wzor in rdzen.konfiguracja().get("dozwolone_hosty") or []:
        wzor = str(wzor).lower().strip()
        if wzor and (nazwa == wzor or (wzor.startswith(".") and nazwa.endswith(wzor))):
            return True
    return False


def adres_powrotu(surowa_sciezka):
    """Dokąd przekierować po zamianie klucza z adresu na ciasteczko: ta sama ścieżka panelu, ale tylko gdy na pewno
    jest lokalna. `/\\obca.strona` albo `//obca.strona` przeglądarka potraktowałaby jak inny serwer (otwarte
    przekierowanie) — wtedy zawsze „/”. Ścieżka zostaje w postaci z żądania (z kodowaniem %XX)."""
    p = surowa_sciezka or "/"
    odkodowana = urllib.parse.unquote(p)
    if (not p.startswith("/") or re.search(r"[\x00-\x20\x7f\\]", p)
            or re.match(r"^/[/\\]", odkodowana) or re.search(r"[\x00-\x1f\x7f\\]", odkodowana)):
        return "/"
    return p


def _za_duzo_prob(ip):
    teraz = time.time()
    with _proby_lock:
        lista = [t for t in _proby.get(ip, []) if teraz - t < 300]
        _proby[ip] = lista
        return len(lista) >= 10


def _zapisz_probe(ip):
    with _proby_lock:
        _proby.setdefault(ip, []).append(time.time())


STRONA_KODU = """<!doctype html><html lang="pl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Panel B&amp;C — kod dostępu</title>
<body style="font-family:system-ui,Segoe UI,sans-serif;background:#12141c;color:#e8eaf2;display:grid;place-items:center;min-height:100vh;margin:0">
<form method="get" action="/" style="background:#1b1f2b;border:2px solid #2a3042;border-radius:16px;padding:24px;max-width:340px;width:86%">
<h1 style="font-size:20px;margin:0 0 8px">BLOCKY &amp; CRYCKET — panel</h1>
<p style="color:#9aa3b8;margin:0 0 16px">Podaj kod dostępu z komputera, na którym działa panel (Ustawienia → Telefon).</p>
<p style="color:#9aa3b8;margin:0 0 16px;font-size:13px">Siedzisz przy tym komputerze? Uruchom <b>panel\\start.bat</b> — otworzy panel z kluczem lokalnym.</p>
<input name="k" autocomplete="off" autofocus placeholder="kod dostępu" style="width:100%;box-sizing:border-box;padding:12px;border-radius:10px;border:2px solid #2a3042;background:#12141c;color:#fff;font-size:16px">
<button style="margin-top:12px;width:100%;padding:12px;border:0;border-radius:10px;background:#f5b82e;color:#1b1400;font-weight:800;font-size:16px">Wejdź</button>
</form></body></html>"""


# --------------------------------------------------------------------------- obsługa żądań
class Obsluga(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "BCPanel/" + rdzen.WERSJA
    sys_version = ""
    timeout = 60                                               # limit pojedynczego odczytu/zapisu gniazda: zrywa zawieszone wysyłki

    def log_message(self, fmt, *args):                         # cisza w konsoli; błędy idą do rdzen.log
        return

    def do_GET(self):
        self._obsluz()

    def do_HEAD(self):
        self._obsluz()

    def do_POST(self):
        self._obsluz()

    def do_OPTIONS(self):
        self._prosta(405, {"blad": "Metoda niedozwolona"})

    do_PUT = do_DELETE = do_PATCH = do_OPTIONS

    # --- wysyłanie
    def _naglowki_wspolne(self, api):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        if api:
            self.send_header("Cache-Control", "no-store")

    def _prosta(self, status, obj, extra=None):
        cialo = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cialo)))
        self._naglowki_wspolne(True)
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(cialo)

    def _odp(self, odp, api):
        if odp.plik_sciezka:
            return self._plik(odp, api)
        self.send_response(odp.status)
        self.send_header("Content-Type", odp.mime)
        self.send_header("Content-Length", str(len(odp.cialo)))
        self._naglowki_wspolne(api)
        if odp.mime.startswith("text/html"):
            self.send_header("Content-Security-Policy", CSP)
        for k, v in odp.naglowki.items():
            for wartosc in (v if isinstance(v, (list, tuple)) else [v]):    # np. kilka Set-Cookie naraz
                self.send_header(k, wartosc)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(odp.cialo)

    def _plik(self, odp, api):
        f = open(odp.plik_sciezka, "rb")                       # błąd otwarcia leci PRZED nagłówkami -> czyste 500
        try:
            return self._plik_wyslij(odp, f, os.fstat(f.fileno()).st_size)
        finally:
            f.close()

    def _plik_wyslij(self, odp, f, rozmiar):
        start, koniec, status = 0, rozmiar - 1, 200
        rng = self.headers.get("Range")
        if rng:
            m = re.match(r"bytes=(\d*)-(\d*)$", rng.strip())
            if m and (m.group(1) or m.group(2)):
                if m.group(1):
                    start = int(m.group(1))
                    koniec = min(int(m.group(2)), rozmiar - 1) if m.group(2) else rozmiar - 1
                else:
                    start = max(0, rozmiar - int(m.group(2)))
                if start > koniec or start >= rozmiar:
                    self.send_response(416)
                    self.send_header("Content-Range", "bytes */%d" % rozmiar)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                status = 206
        dlugosc = koniec - start + 1
        self.send_response(status)
        self.send_header("Content-Type", odp.mime)
        self.send_header("Content-Length", str(dlugosc))
        self.send_header("Accept-Ranges", "bytes")
        if status == 206:
            self.send_header("Content-Range", "bytes %d-%d/%d" % (start, koniec, rozmiar))
        self._naglowki_wspolne(False)
        if odp.mime.startswith("text/html"):
            self.send_header("Content-Security-Policy", CSP)
        for k, v in odp.naglowki.items():
            self.send_header(k, v)
        self.end_headers()
        if self.command == "HEAD":
            return
        zostalo = dlugosc
        try:
            f.seek(start)
            while zostalo > 0:
                kawalek = f.read(min(256 * 1024, zostalo))
                if not kawalek:
                    break
                self.wfile.write(kawalek)
                zostalo -= len(kawalek)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            raise
        except OSError:
            rdzen.log("BŁĄD odczytu pliku %s\n%s" % (self.path, traceback.format_exc()))
            zostalo = max(zostalo, 1)
        if zostalo > 0:
            self.close_connection = True                       # niepełna treść: zamknij połączenie zamiast dopisywać drugą odpowiedź

    def _strumien(self, strumien):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Connection", "close")
        self.send_header("X-Accel-Buffering", "no")
        self._naglowki_wspolne(True)
        self.end_headers()
        self.close_connection = True
        gen = strumien.generator
        try:
            for zdarzenie in gen:
                if zdarzenie is None:
                    self.wfile.write(b": .\n\n")
                else:
                    self.wfile.write(b"data: " + json.dumps(zdarzenie, ensure_ascii=False).encode("utf-8") + b"\n\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            pass
        finally:
            try:
                gen.close()
            except Exception:
                pass

    # --- główna ścieżka
    def _obsluz(self):
        try:
            self._obsluz_wewn()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass
        except socket.timeout:                                 # klient przestał wysyłać albo odbierać: zamknij bez odpowiedzi
            self.close_connection = True
        except Exception:
            rdzen.log("BŁĄD obsługi %s %s\n%s" % (self.command, self.path, traceback.format_exc()))
            try:
                self._prosta(500, {"blad": "Błąd serwera panelu (szczegóły w logu)"})
            except Exception:
                pass

    def _obsluz_wewn(self):
        url = urllib.parse.urlsplit(self.path)
        sciezka = urllib.parse.unquote(url.path) or "/"
        query = {k: v[-1] for k, v in urllib.parse.parse_qs(url.query, keep_blank_values=True).items()}
        api = sciezka.startswith("/api/")
        host = (self.headers.get("Host") or "").strip().lower()
        ip = self.client_address[0]

        if not _host_dozwolony(host):
            return self._prosta(403, {"blad": "Nieznany adres panelu (nagłówek Host)"})

        nazwa_hosta = host[:host.rfind("]") + 1] if host.startswith("[") else host.partition(":")[0]
        z_petli = ip in ("127.0.0.1", "::1", "::ffff:127.0.0.1")
        petla = (z_petli and nazwa_hosta in ("127.0.0.1", "localhost", "[::1]")
                 and not any(self.headers.get(h) for h in NAGLOWKI_POSREDNIKA))
        ciastka = {}
        for kawalek in (self.headers.get("Cookie") or "").split(";"):
            k, _, v = kawalek.strip().partition("=")
            if k:
                ciastka[k] = v
        klient = (self.headers.get("Cf-Connecting-Ip") or ip).strip()[:64] if z_petli else ip   # za tunelem: prawdziwy klient

        # --- klucz lokalny: prawa osoby przy komputerze (samo połączenie z pętli zwrotnej nie wystarcza)
        klucz_l = STAN["klucz_lokalny"]
        podany_l = query.get("l") or self.headers.get("X-BC-Lokalny") or ciastka.get("bc_l") or ""
        lokalny = bool(petla and klucz_l and podany_l and hmac.compare_digest(podany_l.encode(), klucz_l.encode()))
        do_ustawienia = []                                     # ciasteczka z kluczami z adresu (potem przekierowanie)
        if petla and query.get("l"):
            if not lokalny:
                if _za_duzo_prob(klient):
                    return self._prosta(429, {"blad": "Za dużo nieudanych prób. Spróbuj za kilka minut."})
                _zapisz_probe(klient)
            elif not api and self.command == "GET":            # zapamiętaj klucz w przeglądarce i usuń go z adresu
                do_ustawienia.append("bc_l=%s; Path=/; Max-Age=31536000; HttpOnly; SameSite=Strict" % klucz_l)

        # --- kod dostępu dla wszystkich bez klucza lokalnego (telefon, sieć, tunel, przekierowanie portu)
        ustaw_ciasteczko = None
        if not lokalny:
            token = STAN["token"]
            ciastko = ciastka.get("bc_t") or ""
            ciastko_ok = bool(ciastko) and hmac.compare_digest(ciastko.encode(), token.encode())
            podany = query.get("k") or self.headers.get("X-BC-Token") or ""
            if podany and not ciastko_ok and _za_duzo_prob(klient):
                return self._prosta(429, {"blad": "Za dużo nieudanych prób. Spróbuj za kilka minut."})
            if podany and hmac.compare_digest(podany.encode(), token.encode()):
                ustaw_ciasteczko = "bc_t=%s; Path=/; Max-Age=2592000; HttpOnly; SameSite=Lax" % token
            elif not ciastko_ok:
                if podany:
                    _zapisz_probe(klient)
                if api:
                    return self._prosta(401, {"blad": "Wymagany kod dostępu", "kod": "brak_dostepu"})
                return self._odp(Odp(401, STRONA_KODU.encode("utf-8"), "text/html; charset=utf-8"), False)
            if ustaw_ciasteczko and not api and self.command == "GET":
                do_ustawienia.append(ustaw_ciasteczko)

        # --- klucz Game Directora: uprawnienie do zmiany kanonu, zawsze OBOK dostępu do panelu (nie zamiast niego)
        klucz_gd = _klucz_gd()
        podany_gd = query.get("gd") or self.headers.get("X-BC-GD") or ""
        game_director = False
        if podany_gd:
            if _za_duzo_prob(klient):
                return self._prosta(429, {"blad": "Za dużo nieudanych prób. Spróbuj za kilka minut."})
            if klucz_gd and hmac.compare_digest(podany_gd.encode(), klucz_gd.encode()):
                game_director = True
                if query.get("gd") and not api and self.command == "GET":
                    do_ustawienia.append("bc_gd=%s; Path=/; Max-Age=31536000; HttpOnly; SameSite=Lax" % klucz_gd)
            else:
                _zapisz_probe(klient)
                rdzen.log("Nieudana próba klucza Game Directora (%s)" % klient)
        else:
            ciastko_gd = ciastka.get("bc_gd") or ""
            game_director = bool(klucz_gd and ciastko_gd and hmac.compare_digest(ciastko_gd.encode(), klucz_gd.encode()))
        if do_ustawienia and not api and self.command == "GET":   # klucze z adresu -> ciasteczka, adres bez kluczy
            return self._odp(Odp.przekieruj(adres_powrotu(url.path), do_ustawienia), False)

        # --- ochrona POST
        cialo = b""
        if self.command == "POST":
            if self.headers.get("X-BC") != "1":
                return self._prosta(403, {"blad": "Brak nagłówka X-BC"})
            origin = (self.headers.get("Origin") or "").lower()
            if origin and urllib.parse.urlsplit(origin).netloc != host:
                return self._prosta(403, {"blad": "Obce pochodzenie żądania (Origin)"})
            try:
                dl = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                dl = 0
            typ = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            binarny = typ.startswith(("audio/", "image/", "video/")) or typ == "application/octet-stream"
            if dl > (LIMIT_BINARNY if binarny else LIMIT_JSON):
                return self._prosta(413, {"blad": "Za duże żądanie"})
            if not binarny and typ not in ("application/json", ""):
                return self._prosta(415, {"blad": "Oczekiwano application/json"})
            cialo = self.rfile.read(dl) if dl else b""
        elif self.command not in ("GET", "HEAD"):
            return self._prosta(405, {"blad": "Metoda niedozwolona"})

        if not api:
            return self._static(sciezka)

        kto_raw = self.headers.get("X-BC-Kto") or ""
        try:
            kto = urllib.parse.unquote(kto_raw)
        except Exception:
            kto = ""
        kto = re.sub(r"[\x00-\x1f\x7f]", "", kto).strip()[:40]
        if not kto:
            kto = rdzen.git_uzytkownik() if lokalny else "gość"

        fn, params = APP.znajdz(self.command, sciezka)
        if fn is None:
            if params == "metoda":
                return self._prosta(405, {"blad": "Metoda niedozwolona"})
            return self._prosta(404, {"blad": "Nie ma takiej trasy: %s" % sciezka})
        z = Zadanie(self.command, sciezka, query, self.headers, cialo, lokalny, kto, ip, host)
        z.params = params
        z.game_director = game_director
        extra = {"Set-Cookie": ustaw_ciasteczko} if ustaw_ciasteczko else None
        try:
            wynik = fn(z)
        except BladHTTP as e:
            obj = {"blad": e.komunikat}
            obj.update(e.dodatkowe)
            return self._prosta(e.status, obj, extra)
        except Exception as e:
            rdzen.log("BŁĄD trasy %s %s: %r\n%s" % (self.command, sciezka, e, traceback.format_exc()))
            return self._prosta(500, {"blad": "Błąd modułu: %s" % (str(e) or e.__class__.__name__)}, extra)

        if isinstance(wynik, Strumien):
            return self._strumien(wynik)
        if isinstance(wynik, Odp):
            if extra:
                wynik.naglowki.update(extra)
            return self._odp(wynik, True)
        if wynik is None:
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self._naglowki_wspolne(True)
            self.end_headers()
            return
        if isinstance(wynik, tuple) and len(wynik) == 2 and isinstance(wynik[0], int):
            return self._prosta(wynik[0], wynik[1], extra)
        return self._prosta(200, wynik, extra)

    def _static(self, sciezka):
        rel = "index.html" if sciezka in ("/", "") else sciezka.lstrip("/")
        pelna = rdzen.w_katalogu(rdzen.STATIC, rel)
        if not pelna or not os.path.isfile(pelna) or os.path.splitext(pelna)[1].lower() not in ROZSZERZENIA_STATIC:
            return self._prosta(404, {"blad": "Nie ma takiego pliku"})
        return self._plik(Odp(200, b"", mime_pliku(pelna), {"Cache-Control": "no-cache"}, plik=pelna), False)


class Serwer(http.server.ThreadingHTTPServer):
    allow_reuse_address = False                                # Windows: nie pozwól drugiemu procesowi zająć portu
    daemon_threads = True
    request_queue_size = 64


# --------------------------------------------------------------------------- trasy rdzenia
def _ping(z):
    return {"ok": True, "app": rdzen.APP, "wersja": rdzen.WERSJA, "start": STAN["start"], "pid": os.getpid(),
            "port": STAN["port"], "lan": STAN["lan"]}


def _ja(z):
    zapis = bool((APP.moduly.get("zapis") or {}).get("ok")) and rdzen.konfiguracja().get("zapis_sejfu", True) is not False
    return {"kto": z.kto, "lokalny": z.lokalny, "gospodarz": rdzen.git_uzytkownik(), "tryb_statyczny": False,
            "wersja": rdzen.WERSJA, "game_director": bool(z.game_director), "zapis_sejfu": zapis}


def _konfiguracja(z):
    cfg = rdzen.konfiguracja()
    return {"port": STAN["port"], "gra": cfg.get("gra"), "sejfy": [{"id": s.get("id"), "nazwa": s.get("nazwa")}
                                                                   for s in cfg.get("sejfy") or []],
            "agent": {k: v for k, v in (cfg.get("agent") or {}).items() if k in ("tryb_domyslny", "model", "zdalnie")},
            "glos": {k: v for k, v in (cfg.get("glos") or {}).items() if z.lokalny or k != "katalog_modeli"}}


def _konfiguracja_lokalna(z):
    """Przełączniki tego komputera, które wolno zmienić z panelu. Tylko dla osoby przy tym komputerze."""
    if not z.lokalny:
        raise BladHTTP(403, "To ustawienie zmienia się tylko na komputerze, na którym działa panel")
    d = z.json if isinstance(z.json, dict) else {}
    if not isinstance(d.get("agent_zdalnie"), bool):
        raise BladHTTP(400, "Oczekiwano {\"agent_zdalnie\": true albo false}")
    rdzen.zapisz_konfiguracje_lokalna({"agent": {"zdalnie": d["agent_zdalnie"]}})
    rdzen.log("Ustawienia: agent z telefonu %s (%s)" % ("włączony" if d["agent_zdalnie"] else "wyłączony", z.kto))
    return {"agent": {"zdalnie": d["agent_zdalnie"]}}


def _dostep(z):
    """Adresy do wejścia z telefonu (z kodem). Tylko dla osoby przy tym komputerze."""
    if not z.lokalny:
        raise BladHTTP(403, "Tę informację widać tylko na komputerze, na którym działa panel")
    return {"lan": STAN["lan"], "token": STAN["token"],
            "link_lokalny": "http://127.0.0.1:%d/?l=%s" % (STAN["port"], STAN["klucz_lokalny"]),
            "adresy": ["http://%s:%d/?k=%s" % (a, STAN["port"], STAN["token"]) for a in STAN["adresy_lan"]] if STAN["lan"] else [],
            "podpowiedz": None if STAN["lan"] else "Uruchom panel z opcją --lan (albo start_lan.bat), żeby wejść z telefonu w tej samej sieci Wi-Fi."}


def zdrowie_rdzenia():
    kod, out, _ = rdzen.uruchom(["git", "--version"], timeout=10)
    kod2, out2, _ = rdzen.uruchom(["git", "rev-parse", "--show-toplevel"], timeout=10)
    try:
        wolne = shutil.disk_usage(rdzen.REPO).free
    except OSError:
        wolne = None
    return {"python": sys.version.split()[0], "python_ok": sys.version_info >= (3, 9),
            "git": out.strip() if kod == 0 else None,
            "repo_git": kod2 == 0 and os.path.normcase(os.path.realpath(out2.strip())) == os.path.normcase(os.path.realpath(rdzen.REPO)),
            "repo": rdzen.REPO, "runtime": rdzen.RUNTIME, "wolne_miejsce_gb": round(wolne / 1e9, 1) if wolne else None}


def _zdrowie(z):
    wynik = {"rdzen": zdrowie_rdzenia(), "moduly": APP.moduly, "szczegoly": {}}
    for nazwa, fn in APP.zdrowie.items():
        try:
            wynik["szczegoly"][nazwa] = fn()
        except Exception as e:
            wynik["szczegoly"][nazwa] = {"blad": str(e)}
    if not z.lokalny:                                          # bez lokalnych ścieżek dla telefonu i tunelu
        wynik["rdzen"].pop("repo", None)
        wynik["rdzen"].pop("runtime", None)
        wynik["szczegoly"] = {n: ({k: v for k, v in d.items() if k in ("ok", "blad", "powod", "dostepny", "polaczone", "whisper")}
                                  if isinstance(d, dict) else d) for n, d in wynik["szczegoly"].items()}
    return wynik


def zaladuj_moduly():
    APP.dodaj("GET", "/api/ping", _ping)
    APP.dodaj("GET", "/api/ja", _ja)
    APP.dodaj("GET", "/api/konfiguracja", _konfiguracja)
    APP.dodaj("POST", "/api/konfiguracja/lokalna", _konfiguracja_lokalna)
    APP.dodaj("GET", "/api/dostep", _dostep)
    APP.dodaj("GET", "/api/zdrowie", _zdrowie)
    for nazwa in MODULY:
        try:
            mod = importlib.import_module("bc." + nazwa)
            mod.zarejestruj(APP)
            if hasattr(mod, "zdrowie"):
                APP.zdrowie[nazwa] = mod.zdrowie
            APP.moduly[nazwa] = {"ok": True, "blad": None}
        except ModuleNotFoundError as e:
            if e.name == "bc." + nazwa:
                APP.moduly[nazwa] = {"ok": False, "blad": "moduł jeszcze nie istnieje"}
            else:
                APP.moduly[nazwa] = {"ok": False, "blad": "brak zależności: %s" % e.name}
                rdzen.log("Moduł %s: %s" % (nazwa, e))
        except Exception as e:
            APP.moduly[nazwa] = {"ok": False, "blad": "%s: %s" % (e.__class__.__name__, e)}
            rdzen.log("Moduł %s nie wstał:\n%s" % (nazwa, traceback.format_exc()))


# --------------------------------------------------------------------------- start
def _juz_dziala(port):
    req = urllib.request.Request("http://127.0.0.1:%d/api/ping" % port, headers={"X-BC-Lokalny": _klucz_lokalny()})
    try:
        with urllib.request.urlopen(req, timeout=1.5) as r:
            d = json.loads(r.read().decode("utf-8"))
            return d.get("app") == rdzen.APP
    except urllib.error.HTTPError as e:                        # odpowiada, ale nie zna naszego klucza: to też panel
        return e.code == 401 and "BCPanel" in (e.headers.get("Server") or "")
    except Exception:
        return False


def sprawdz():
    """Samokontrola środowiska dla instalacji: wypisuje raport, kod 0 = można startować."""
    zaladuj_moduly()
    r = zdrowie_rdzenia()
    ok = True
    print("BLOCKY & CRYCKET — panel zespołu %s — kontrola środowiska" % rdzen.WERSJA)
    print("  Python %s %s" % (r["python"], "OK" if r["python_ok"] else "ZA STARY (potrzebny 3.9+)"))
    ok &= r["python_ok"]
    print("  Git: %s" % (r["git"] or "BRAK (zainstaluj Git for Windows)"))
    ok &= bool(r["git"])
    print("  Repozytorium: %s %s" % (r["repo"], "OK" if r["repo_git"] else "(uwaga: to nie jest korzeń repozytorium git)"))
    print("  Dane lokalne: %s" % r["runtime"])
    for nazwa, st in APP.moduly.items():
        print("  moduł %-10s %s" % (nazwa, "OK" if st["ok"] else "BŁĄD: " + str(st["blad"])))
        ok &= st["ok"]
    for nazwa, fn in APP.zdrowie.items():
        try:
            d = fn()
        except Exception as e:
            d = {"blad": str(e)}
        print("  [%s] %s" % (nazwa, json.dumps(d, ensure_ascii=False)))
    print("WYNIK: %s" % ("gotowe do uruchomienia" if ok else "są problemy do naprawienia (patrz wyżej)"))
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="BLOCKY & CRYCKET — panel zespołu")
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--lan", action="store_true", help="udostępnij w sieci lokalnej (telefon); wymaga kodu dostępu")
    ap.add_argument("--sprawdz", action="store_true", help="sprawdź środowisko i zakończ")
    ap.add_argument("--bez-przegladarki", action="store_true")
    ap.add_argument("--eksport", metavar="FOLDER", help="zapisz lustro tylko-do-odczytu (strona statyczna) i zakończ")
    ap.add_argument("--klucz-gd", action="store_true",
                    help="wypisz link Game Directora (zatwierdzanie decyzji w panelu) i zakończ")
    ap.add_argument("--nowy-klucz-gd", action="store_true",
                    help="utwórz nowy klucz Game Directora (stary przestaje działać), wypisz link i zakończ")
    a = ap.parse_args()
    if a.sprawdz:
        sys.exit(sprawdz())
    if a.klucz_gd or a.nowy_klucz_gd:
        sys.exit(wypisz_link_gd(nowy=a.nowy_klucz_gd))
    if a.eksport:
        zaladuj_moduly()
        from bc import statyczny
        stat = statyczny.eksportuj(APP, a.eksport)
        print("Lustro: %d plików danych, %d plików binarnych -> %s" % (stat["json"], stat["pliki"], os.path.abspath(a.eksport)))
        for b in stat["bledy"]:
            print("  uwaga:", b)
        return

    port = a.port or int(rdzen.konfiguracja().get("port") or 8787)
    rdzen.upewnij_katalog(rdzen.RUNTIME)
    url = "http://127.0.0.1:%d/?l=%s" % (port, _klucz_lokalny())   # adres z kluczem lokalnym: tylko dla tego komputera
    if _juz_dziala(port):
        print("Panel już działa: http://127.0.0.1:%d/" % port)
        if not a.bez_przegladarki:
            import webbrowser
            webbrowser.open(url)
        return
    rdzen.upewnij_katalog(rdzen.RUNTIME)
    rdzen.upewnij_katalog(rdzen.DANE)
    STAN.update(start=rdzen.teraz(), port=port, lan=bool(a.lan), token=_token(), klucz_lokalny=_klucz_lokalny())
    STAN["adresy_lan"] = _adresy_lan() if a.lan else []
    STAN["hosty"] = set(STAN["adresy_lan"]) | ({socket.gethostname().lower()} if a.lan else set())
    zaladuj_moduly()
    try:
        srv = Serwer(("0.0.0.0" if a.lan else "127.0.0.1", port), Obsluga)
    except OSError as e:
        print("Nie mogę zająć portu %d (%s). Zamknij program, który go używa, albo podaj inny: --port 8790" % (port, e))
        sys.exit(2)
    rdzen.log("Panel %s wystartował: http://127.0.0.1:%d/ (lan=%s, pid=%d)" % (rdzen.WERSJA, port, a.lan, os.getpid()))
    for nazwa, st in APP.moduly.items():
        if not st["ok"]:
            rdzen.log("  moduł %s wyłączony: %s" % (nazwa, st["blad"]))
    print("\n  Panel zespołu (ten komputer, adres z kluczem lokalnym — nie udostępniaj):\n    %s" % url)
    if a.lan:
        for adr in STAN["adresy_lan"]:
            print("  Telefon (ta sama sieć Wi-Fi):  http://%s:%d/?k=%s" % (adr, port, STAN["token"]))
    print("  Zatrzymanie: Ctrl+C\n")
    if not a.bez_przegladarki:
        try:
            import webbrowser
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        except Exception:
            pass
    try:
        srv.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        print("\nZatrzymuję panel…")
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
