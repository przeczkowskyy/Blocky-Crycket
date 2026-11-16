# -*- coding: utf-8 -*-
"""Rdzeń panelu: ścieżki, konfiguracja, atomowy zapis JSON, identyfikatory, log, uruchamianie poleceń.

Zasady (wzorzec z panelu Saga Studio):
- stan WSPÓLNY (raporty, komentarze, migawki) to pliki w `panel/dane/` — jeden plik na wpis, żeby git nigdy nie miał
  konfliktów scalania; trafiają do repozytorium;
- stan LOKALNY (token, log, wątki agenta, nagrania głosowe, historia analityki) leży poza repo i poza OneDrive:
  Windows `%LOCALAPPDATA%\\BlockyCrycket\\panel`, inne systemy `~/.local/state/blocky-crycket/panel`
  (zmienna BC_PANEL_RUNTIME nadpisuje);
- zapis zawsze atomowy (plik .tmp + os.replace) z ponowieniami, bo OneDrive i antywirus potrafią blokować pliki.
"""
import datetime
import json
import os
import secrets
import subprocess
import sys
import threading
import time

WERSJA = "0.1.0"
APP = "bc-panel"

PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(PANEL)
STATIC = os.path.join(PANEL, "static")
DANE = os.environ.get("BC_PANEL_DANE") or os.path.join(PANEL, "dane")   # BC_PANEL_DANE: katalog zastępczy dla testów
PLIK_KONFIGURACJI = os.path.join(PANEL, "konfiguracja.json")
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def _runtime_dir():
    env = os.environ.get("BC_PANEL_RUNTIME")
    if env:
        return env
    if os.name == "nt":
        root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(root, "BlockyCrycket", "panel")
    root = os.environ.get("XDG_STATE_HOME") or os.path.expanduser("~/.local/state")
    return os.path.join(root, "blocky-crycket", "panel")


RUNTIME = _runtime_dir()
PLIK_KONFIGURACJI_LOKALNEJ = os.path.join(RUNTIME, "konfiguracja.lokalna.json")
PLIK_LOGU = os.path.join(RUNTIME, "panel.log")

_log_lock = threading.Lock()
_cfg_lock = threading.Lock()
_cfg_cache = {"mtime": None, "dane": None}


class BladHTTP(Exception):
    """Rzuć w handlerze, żeby zwrócić błąd JSON: raise BladHTTP(404, "Nie ma takiego raportu")."""

    def __init__(self, status, komunikat, **dodatkowe):
        super().__init__(komunikat)
        self.status = int(status)
        self.komunikat = komunikat
        self.dodatkowe = dodatkowe


# --------------------------------------------------------------------------- czas i identyfikatory
def teraz():
    """Czas lokalny ISO ze strefą, np. 2026-11-12T21:40:05+01:00."""
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def nowe_id(prefiks=""):
    """Identyfikator sortowalny po czasie: [prefiks-]RRRRMMDD-GGMMSS-xxxx."""
    rdzen = time.strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(2)
    return (prefiks + "-" + rdzen) if prefiks else rdzen


# --------------------------------------------------------------------------- pliki
def upewnij_katalog(sciezka):
    os.makedirs(sciezka, exist_ok=True)
    return sciezka


def czytaj_json(sciezka, domyslnie=None):
    try:
        with open(sciezka, encoding="utf-8-sig") as f:
            return json.load(f)
    except (OSError, ValueError):
        return domyslnie


def zapisz_json(sciezka, obj, wciecie=1):
    """Atomowy zapis JSON (UTF-8, bez BOM, \\n). Ponawia przy blokadzie pliku przez OneDrive/antywirusa."""
    upewnij_katalog(os.path.dirname(sciezka))
    tmp = "%s.%d.%s.tmp" % (sciezka, os.getpid(), secrets.token_hex(3))
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=wciecie)
        f.write("\n")
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass
    ostatni = None
    for proba in range(8):
        try:
            os.replace(tmp, sciezka)
            return sciezka
        except OSError as e:                                   # PermissionError: plik chwilowo zablokowany
            ostatni = e
            time.sleep(0.05 * (proba + 1))
    try:
        os.remove(tmp)
    except OSError:
        pass
    raise ostatni


def zapisz_bajty(sciezka, dane):
    upewnij_katalog(os.path.dirname(sciezka))
    tmp = "%s.%d.%s.tmp" % (sciezka, os.getpid(), secrets.token_hex(3))
    with open(tmp, "wb") as f:
        f.write(dane)
    for proba in range(8):
        try:
            os.replace(tmp, sciezka)
            return sciezka
        except OSError:
            time.sleep(0.05 * (proba + 1))
    os.replace(tmp, sciezka)
    return sciezka


def czytaj_tekst(sciezka, domyslnie=None):
    try:
        with open(sciezka, encoding="utf-8-sig") as f:
            return f.read()
    except OSError:
        return domyslnie


def w_katalogu(baza, wzgledna):
    """Bezpieczne łączenie ścieżek: zwraca ścieżkę bezwzględną wewnątrz `baza` albo None (.., dysk, strumień NTFS)."""
    if wzgledna is None:
        return None
    wzgledna = str(wzgledna).replace("\\", "/")
    if wzgledna.startswith("/") or ":" in wzgledna or "\x00" in wzgledna:
        return None
    czesci = [c for c in wzgledna.split("/") if c not in ("", ".")]
    if any(c == ".." for c in czesci):
        return None
    baza_abs = os.path.realpath(baza)
    pelna = os.path.realpath(os.path.join(baza_abs, *czesci))
    if pelna != baza_abs and not pelna.startswith(baza_abs + os.sep):
        return None
    return pelna


def wzgledem_repo(sciezka):
    """Ścieżka względem repozytorium z ukośnikami / (do pokazywania i do API)."""
    try:
        return os.path.relpath(sciezka, REPO).replace("\\", "/")
    except ValueError:
        return sciezka.replace("\\", "/")


# --------------------------------------------------------------------------- konfiguracja
def _scal(a, b):
    """Głębokie scalenie słowników: wartości z b nadpisują a."""
    out = dict(a)
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _scal(out[k], v)
        else:
            out[k] = v
    return out


DOMYSLNA = {
    "port": 8787,
    "gra": {"nazwa": "BLOCKY & CRYCKET", "universeId": None, "placeId": None},
    "sejfy": [{"id": "B&C", "nazwa": "Sejf gry", "sciezka": "B&C"}],
    "agent": {"tryb_domyslny": "praca", "model": "", "zdalnie": False, "limit_czasu_min": 30},
    "glos": {"model": "large-v3-turbo", "jezyk": "pl"},
    "git": {"sciezki_panelu": ["panel/dane"]},
    "dozwolone_hosty": [],
}


# Ustawienia, od których zależy bezpieczeństwo komputera, wolno ustawić TYLKO w konfiguracji lokalnej. Wspólny plik
# panel/konfiguracja.json leży w repozytorium: może go zmienić druga osoba albo scalona cudza zmiana, więc nie może
# włączać agenta dla połączeń zdalnych, wskazywać programu do uruchomienia, poszerzać listy narzędzi ani dopisywać hostów.
# Tak samo klucz Open Cloud do telemetrii i adres, pod który jest wysyłany (bc/telemetria.py): sekret nie może
# przyjść z publicznego repozytorium ani zostać przekierowany na cudzy serwer.
# Zakładka Sesja (bc/sesje.py): serwer TURN z hasłem i zostawianie nagrań rozmowy na dysku — też tylko lokalnie.
TYLKO_LOKALNE_GLOWNE = ("dozwolone_hosty",)
TYLKO_LOKALNE_SEKCJE = {"agent": ("zdalnie", "sciezka", "dozwolone_narzedzia"), "glos": ("katalog_modeli",),
                        "analityka": ("klucz_open_cloud", "adres_open_cloud"), "sesje": ("turn", "zostaw_dzwiek"),
                        # samo uruchamianie zadań przypisanych do agenta tej osoby (bc/zadania_agenta.py) wydaje JEJ
                        # tokeny — włącza je tylko ona na swoim komputerze, nie wspólny plik z repozytorium
                        "zadania_agenta": ("auto",)}


def _bezpieczna_wspolna(cfg):
    """Wspólna konfiguracja bez kluczy zastrzeżonych dla konfiguracji lokalnej i bez sejfów spoza repozytorium."""
    if not isinstance(cfg, dict):
        return {}
    cfg = dict(cfg)
    for k in TYLKO_LOKALNE_GLOWNE:
        cfg.pop(k, None)
    for sekcja, klucze in TYLKO_LOKALNE_SEKCJE.items():
        if isinstance(cfg.get(sekcja), dict):
            d = dict(cfg[sekcja])
            for k in klucze:
                d.pop(k, None)
            cfg[sekcja] = d
    if "sejfy" in cfg:
        sejfy = []
        for s in cfg.get("sejfy") or []:
            sciezka = str(s.get("sciezka") or "") if isinstance(s, dict) else ""
            if sciezka and not os.path.isabs(sciezka) and w_katalogu(REPO, sciezka):
                sejfy.append(s)                                # sejf wspólny musi leżeć w repozytorium
        cfg["sejfy"] = sejfy
    if isinstance(cfg.get("agent"), dict) and cfg["agent"].get("tryb_domyslny") not in (None, "plan", "praca"):
        cfg["agent"].pop("tryb_domyslny", None)                # tryb „auto” jako domyślny tylko z konfiguracji lokalnej
    if isinstance(cfg.get("git"), dict) and "sciezki_panelu" in cfg["git"]:
        g = dict(cfg["git"])                                   # przycisk „Wyślij” commituje tylko dane panelu
        g["sciezki_panelu"] = [p for p in g.get("sciezki_panelu") or [] if isinstance(p, str)
                               and (p.replace("\\", "/").strip("/") + "/").startswith("panel/dane/") and w_katalogu(REPO, p)]
        if not g["sciezki_panelu"]:
            g.pop("sciezki_panelu")
        cfg["git"] = g
    return cfg


def konfiguracja():
    """Konfiguracja = domyślna + panel/konfiguracja.json (wspólna, w repo, bez kluczy zastrzeżonych) +
    konfiguracja.lokalna.json (ten komputer; tylko tu wolno ustawić klucze z TYLKO_LOKALNE_*)."""
    with _cfg_lock:
        try:
            m = (os.path.getmtime(PLIK_KONFIGURACJI) if os.path.exists(PLIK_KONFIGURACJI) else 0,
                 os.path.getmtime(PLIK_KONFIGURACJI_LOKALNEJ) if os.path.exists(PLIK_KONFIGURACJI_LOKALNEJ) else 0)
        except OSError:
            m = None
        if _cfg_cache["dane"] is not None and _cfg_cache["mtime"] == m:
            return _cfg_cache["dane"]
        cfg = _scal(DOMYSLNA, _bezpieczna_wspolna(czytaj_json(PLIK_KONFIGURACJI, {})))
        cfg = _scal(cfg, czytaj_json(PLIK_KONFIGURACJI_LOKALNEJ, {}) or {})
        _cfg_cache.update(mtime=m, dane=cfg)
        return cfg


def zapisz_konfiguracje_lokalna(zmiany):
    """Scala `zmiany` z konfiguracją lokalną tego komputera (poza repo)."""
    with _cfg_lock:
        obecna = czytaj_json(PLIK_KONFIGURACJI_LOKALNEJ, {}) or {}
        zapisz_json(PLIK_KONFIGURACJI_LOKALNEJ, _scal(obecna, zmiany))
        _cfg_cache.update(mtime=None, dane=None)


# --------------------------------------------------------------------------- log
def log(*czesci):
    linia = "%s  %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), " ".join(str(c) for c in czesci))
    with _log_lock:
        try:
            upewnij_katalog(RUNTIME)
            if os.path.exists(PLIK_LOGU) and os.path.getsize(PLIK_LOGU) > 5 * 1024 * 1024:
                os.replace(PLIK_LOGU, PLIK_LOGU + ".1")
            with open(PLIK_LOGU, "a", encoding="utf-8") as f:
                f.write(linia + "\n")
        except OSError:
            pass
        try:
            print(linia, flush=True)
        except Exception:
            pass


# --------------------------------------------------------------------------- polecenia
def uruchom(cmd, cwd=None, timeout=60, wejscie=None, env=None):
    """Uruchamia polecenie bez okna konsoli. Zwraca (kod, stdout, stderr) jako tekst UTF-8; kod -1 = nie wystartowało,
    -2 = przekroczony czas."""
    try:
        p = subprocess.Popen(cmd, cwd=cwd or REPO, env=env, creationflags=CREATE_NO_WINDOW,
                             stdin=subprocess.PIPE if wejscie is not None else subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as e:                                       # także FileNotFoundError: programu nie ma
        return -1, "", str(e)
    try:
        out, err = p.communicate(wejscie, timeout=timeout)
    except subprocess.TimeoutExpired:
        # Samo zabicie procesu nie wystarcza: jego dzieci (np. git-remote-https) trzymają potoki i communicate()
        # czekałoby bez końca. Na Windows kończymy całe drzewo, zanim zniknie rodzic.
        if os.name == "nt":
            try:
                subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True, timeout=15,
                               creationflags=CREATE_NO_WINDOW)
            except (OSError, subprocess.TimeoutExpired):
                pass
        try:
            p.kill()
        except OSError:
            pass
        try:
            out, _ = p.communicate(timeout=5)
        except (subprocess.TimeoutExpired, OSError, ValueError):
            out = b""
        return -2, (out or b"").decode("utf-8", "replace"), "przekroczony czas %s s" % timeout
    return p.returncode, (out or b"").decode("utf-8", "replace"), (err or b"").decode("utf-8", "replace")


_git_user = {"t": 0.0, "v": None}


def git_uzytkownik():
    """Nazwa z `git config user.name` (pamiętana 5 min) — domyślna tożsamość osoby przy tym komputerze."""
    if _git_user["v"] is not None and time.time() - _git_user["t"] < 300:
        return _git_user["v"]
    kod, out, _ = uruchom(["git", "config", "user.name"], timeout=10)
    nazwa = out.strip() if kod == 0 and out.strip() else (os.environ.get("USERNAME") or os.environ.get("USER") or "ktoś")
    _git_user.update(t=time.time(), v=nazwa)
    return nazwa


def python_exe():
    return sys.executable or "python"
