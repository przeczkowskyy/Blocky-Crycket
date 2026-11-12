# -*- coding: utf-8 -*-
"""Git: stan repozytorium oraz „Pobierz” / „Wyślij” danych panelu.

- Każde polecenie git idzie przez rdzen.uruchom z limitem czasu i ze środowiskiem, w którym git nigdy nie czeka na
  hasło (GIT_TERMINAL_PROMPT=0, GCM_INTERACTIVE=never, ssh w trybie wsadowym) i pisze komunikaty po angielsku
  (LC_ALL=C), żeby dało się je rozpoznać i przetłumaczyć na zrozumiały polski.
- Stan pamiętany 5 s. `git fetch` w tle (osobny wątek) najwyżej raz na 5 minut, wyzwalany leniwie przez
  GET /api/git/stan — żądanie nigdy na niego nie czeka.
- „Wyślij” dodaje i commituje WYŁĄCZNIE ścieżki z `git.sciezki_panelu` (domyślnie `panel/dane`).
- Funkcje przyjmują `repo=` (domyślnie rdzen.REPO), żeby dało się je sprawdzić na repozytorium testowym.
"""
import datetime
import os
import re
import threading
import time

from . import rdzen
from .rdzen import BladHTTP

PAMIEC_STANU_S = 5.0
FETCH_CO_S = 300.0
MAKS_ZMIENIONYCH = 300

_pamiec_stanu = {}                                             # (repo, ścieżki) -> (czas, wynik)
_pamiec_blokada = threading.Lock()
_fetch = {}                                                    # repo -> {proba, kiedy, trwa, blad}
_fetch_blokada = threading.Lock()
_zapis_blokada = threading.Lock()                              # jedna operacja pobierz/wyślij naraz

OPISY_STANU = {"M": "zmieniony", "A": "dodany", "D": "usunięty", "R": "przeniesiony", "C": "skopiowany",
               "T": "zmieniony", "U": "konflikt", "?": "nowy", "!": "ignorowany"}


# --------------------------------------------------------------------------- uruchamianie gita
def _srodowisko():
    env = dict(os.environ)
    env.update({"GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never", "LC_ALL": "C", "LANG": "C",
                "LANGUAGE": "C", "GIT_OPTIONAL_LOCKS": "0"})
    env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes")
    env.pop("GIT_DIR", None)
    env.pop("GIT_WORK_TREE", None)
    return env


def git(argumenty, repo=None, timeout=30):
    """Uruchamia git w repozytorium. Zwraca (kod, stdout, stderr); kod -1 = brak gita, -2 = przekroczony czas."""
    return rdzen.uruchom(["git", "-c", "core.quotepath=false", "-c", "color.ui=false",
                          "-c", "http.lowSpeedLimit=1000", "-c", "http.lowSpeedTime=60"] + list(argumenty),
                         cwd=repo or rdzen.REPO, timeout=timeout, env=_srodowisko())


def _repo(repo):
    return os.path.normpath(repo or rdzen.REPO)


def sciezki_panelu():
    s = (rdzen.konfiguracja().get("git") or {}).get("sciezki_panelu") or ["panel/dane"]
    return [str(x).replace("\\", "/").strip("/") for x in s if str(x).strip("/ ")]


def _w_sciezkach(plik, sciezki):
    for s in sciezki:
        if plik == s or plik.startswith(s + "/"):
            return True
    return False


def _bez_hasla(url):
    """Usuwa dane logowania z adresu (https://login:token@host/… -> https://host/…)."""
    return re.sub(r"^([a-z][a-z0-9+.-]*://)[^/@]*@", r"\1", url or "", flags=re.IGNORECASE)


# --------------------------------------------------------------------------- stan
def _parsuj_status(tekst):
    """`git status --porcelain=v1 -b -z` -> (nagłówek gałęzi, [(XY, plik)])."""
    wpisy = tekst.split("\0")
    naglowek, pliki = "", []
    i = 0
    while i < len(wpisy):
        w = wpisy[i]
        i += 1
        if not w:
            continue
        if w.startswith("## "):
            naglowek = w[3:]
            continue
        if len(w) < 4:
            continue
        xy, plik = w[:2], w[3:]
        if xy[0] in "RC":                                      # przeniesienie: następny wpis to stara ścieżka
            i += 1
        pliki.append((xy, plik))
    return naglowek, pliki


def _parsuj_naglowek(naglowek):
    """`main...origin/main [ahead 1, behind 2]` -> (gałąź, upstream, do_wysłania, do_pobrania)."""
    galaz, upstream, przod, tyl = None, None, 0, 0
    h = naglowek.strip()
    for przedrostek in ("No commits yet on ", "Initial commit on "):
        if h.startswith(przedrostek):
            h = h[len(przedrostek):]
    m = re.match(r"^(.*?)(?:\.\.\.(\S+))?(?: \[(.*)\])?$", h)
    if m:
        galaz = m.group(1) or None
        upstream = m.group(2)
        nawias = m.group(3) or ""
        ma = re.search(r"ahead (\d+)", nawias)
        mb = re.search(r"behind (\d+)", nawias)
        przod = int(ma.group(1)) if ma else 0
        tyl = int(mb.group(1)) if mb else 0
        if "gone" in nawias:
            upstream = None
    if galaz and galaz.startswith("HEAD (no branch)"):
        galaz = None
    return galaz, upstream, przod, tyl


def _ostatni_fetch(repo):
    st = _fetch.get(repo) or {}
    if st.get("kiedy"):
        return st["kiedy"]
    p = os.path.join(repo, ".git", "FETCH_HEAD")
    try:
        t = os.path.getmtime(p)
    except OSError:
        return None
    return datetime.datetime.fromtimestamp(t).astimezone().isoformat(timespec="seconds")


def _zdalne(repo, upstream):
    kod, out, _ = git(["remote", "-v"], repo, timeout=10)
    if kod != 0:
        return None
    adresy = {}
    for linia in out.splitlines():
        cz = linia.split()
        if len(cz) >= 2 and (len(cz) < 3 or cz[2] == "(fetch)"):
            adresy.setdefault(cz[0], cz[1])
    if not adresy:
        return None
    nazwa = upstream.split("/", 1)[0] if upstream and upstream.split("/", 1)[0] in adresy else (
        "origin" if "origin" in adresy else sorted(adresy)[0])
    return {"nazwa": nazwa, "url": _bez_hasla(adresy[nazwa]), "galaz": upstream}


def ostatnie_commity(repo=None, ile=10):
    kod, out, _ = git(["log", "-n", str(int(ile)), "--format=%h%x1f%an%x1f%aI%x1f%s"], repo, timeout=15)
    if kod != 0:
        return []
    wynik = []
    for linia in out.splitlines():
        cz = linia.split("\x1f")
        if len(cz) >= 4:
            wynik.append({"hash": cz[0], "autor": cz[1], "data": cz[2], "temat": cz[3]})
    return wynik


def stan(repo=None, sciezki=None, wymus=False):
    """Stan repozytorium (pamięć 5 s). Nie rzuca — przy problemie zwraca pole `blad`."""
    repo = _repo(repo)
    sciezki = sciezki if sciezki is not None else sciezki_panelu()
    klucz = (repo, tuple(sciezki))
    with _pamiec_blokada:
        zap = _pamiec_stanu.get(klucz)
        if zap and not wymus and time.time() - zap[0] < PAMIEC_STANU_S:
            return dict(zap[1], ostatni_fetch=_ostatni_fetch(repo), fetch_trwa=bool((_fetch.get(repo) or {}).get("trwa")))
    wynik = {"galaz": None, "czyste": True, "zmienione": [], "zmiany_panelu": 0, "do_wyslania": 0, "do_pobrania": 0,
             "ostatni_fetch": _ostatni_fetch(repo), "ostatnie_commity": [], "zdalne": None}
    kod, out, err = git(["status", "--porcelain=v1", "-b", "-z", "-uall"], repo, timeout=30)
    if kod != 0:
        if kod == -1:
            wynik["blad"] = "Nie znaleziono programu Git. Zainstaluj Git for Windows."
        elif kod == -2:
            wynik["blad"] = "Git nie odpowiedział na czas (sprawdzanie stanu)."
        else:
            wynik["blad"] = "To nie jest repozytorium Git albo Git zgłosił błąd: %s" % (err.strip()[:200] or kod)
        return wynik
    naglowek, pliki = _parsuj_status(out)
    galaz, upstream, przod, tyl = _parsuj_naglowek(naglowek)
    zmienione = []
    for xy, plik in pliki:
        if xy == "??":
            kod_stanu = "?"
        elif "U" in xy or xy in ("AA", "DD"):
            kod_stanu = "U"
        else:
            kod_stanu = xy[0] if xy[0] != " " else xy[1]
        zmienione.append({"plik": plik, "stan": OPISY_STANU.get(kod_stanu, "zmieniony"), "kod": xy})
    wynik.update(galaz=galaz, czyste=not zmienione, zmienione=zmienione[:MAKS_ZMIENIONYCH],
                 zmiany_panelu=sum(1 for z in zmienione if _w_sciezkach(z["plik"], sciezki)),
                 do_wyslania=przod, do_pobrania=tyl, ostatnie_commity=ostatnie_commity(repo),
                 zdalne=_zdalne(repo, upstream))
    if len(zmienione) > MAKS_ZMIENIONYCH:
        wynik["zmienione_wszystkich"] = len(zmienione)
    with _pamiec_blokada:
        _pamiec_stanu[klucz] = (time.time(), wynik)
    return dict(wynik, fetch_trwa=bool((_fetch.get(repo) or {}).get("trwa")))


def _uniewaznij(repo):
    with _pamiec_blokada:
        for k in [k for k in _pamiec_stanu if k[0] == repo]:
            _pamiec_stanu.pop(k, None)


# --------------------------------------------------------------------------- fetch w tle
def _fetch_watek(repo):
    st = _fetch[repo]
    try:
        kod, _, err = git(["fetch", "--quiet", "--prune"], repo, timeout=90)
        if kod == 0:
            st["kiedy"] = rdzen.teraz()
            st["blad"] = None
        else:
            st["blad"] = _tlumacz_blad(err, "Nie udało się sprawdzić zmian na GitHubie")
    except Exception as e:                                     # wątek w tle nie może wywrócić serwera
        st["blad"] = str(e)
    finally:
        st["trwa"] = False
        _uniewaznij(repo)


def moze_fetch(repo=None, wymus=False):
    """Startuje `git fetch` w tle, jeśli od ostatniej próby minęło ≥ 5 min. Nigdy nie czeka. Zwraca True, gdy ruszył."""
    repo = _repo(repo)
    with _fetch_blokada:
        st = _fetch.setdefault(repo, {"proba": 0.0, "kiedy": None, "trwa": False, "blad": None})
        if st["trwa"] or (not wymus and time.time() - st["proba"] < FETCH_CO_S):
            return False
        st["proba"] = time.time()
        st["trwa"] = True
    threading.Thread(target=_fetch_watek, args=(repo,), name="git-fetch", daemon=True).start()
    return True


# --------------------------------------------------------------------------- komunikaty
def _tlumacz_blad(tekst, domyslnie):
    t = (tekst or "").lower()
    if "could not resolve host" in t or "unable to access" in t or "failed to connect" in t or "timed out" in t:
        return "Brak połączenia z GitHubem. Sprawdź internet i spróbuj ponownie."
    if "authentication failed" in t or "terminal prompts disabled" in t or "could not read username" in t \
            or "permission denied" in t or "error: 403" in t:
        return ("GitHub nie przyjął logowania. Zaloguj się raz w Git (np. `git push` w terminalu albo GitHub Desktop) "
                "i spróbuj ponownie.")
    if "przekroczony czas" in t:
        return "Git nie odpowiedział na czas. Spróbuj ponownie za chwilę."
    return domyslnie


def _odrzucony_push(tekst):
    t = (tekst or "").lower()
    return ("rejected" in t and ("fetch first" in t or "non-fast-forward" in t or "behind" in t)) or \
        "updates were rejected" in t


def _rebase_trwa(repo):
    kod, out, _ = git(["rev-parse", "--git-path", "rebase-merge", "--git-path", "rebase-apply"], repo, timeout=10)
    if kod != 0:
        return False
    for linia in out.splitlines():
        p = linia.strip()
        if p and os.path.isdir(p if os.path.isabs(p) else os.path.join(repo, p)):
            return True
    return False


def _upstream(repo):
    kod, out, _ = git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], repo, timeout=10)
    return out.strip() if kod == 0 and out.strip() else None


# --------------------------------------------------------------------------- pobierz / wyślij
def pobierz(repo=None):
    """`git pull --rebase --autostash`. Zwraca {ok, wyjscie}; przy problemie rzuca BladHTTP z czytelnym opisem."""
    repo = _repo(repo)
    if not _zapis_blokada.acquire(blocking=False):
        raise BladHTTP(409, "Trwa już inna operacja Git. Poczekaj chwilę.")
    try:
        if not _upstream(repo):
            raise BladHTTP(409, "Ta gałąź nie jest połączona z GitHubem, więc nie ma skąd pobrać zmian.")
        kod, out, err = git(["pull", "--rebase", "--autostash"], repo, timeout=180)
        wyjscie = (out + ("\n" if out and err else "") + err).strip()
        if kod == 0:
            wynik = {"ok": True, "wyjscie": wyjscie or "Już aktualne."}
            if "autostash" in wyjscie.lower() and "conflict" in wyjscie.lower():
                wynik["uwaga"] = ("Pobrano zmiany, ale Twoje niezapisane zmiany kolidują z nimi. Zostały odłożone "
                                  "w `git stash` — poproś agenta o pomoc w ich przywróceniu.")
            with _fetch_blokada:                               # pull to też świeży fetch
                _fetch.setdefault(repo, {"proba": 0.0, "kiedy": None, "trwa": False, "blad": None})
                _fetch[repo].update(kiedy=rdzen.teraz(), proba=time.time(), blad=None)
            return wynik
        if _rebase_trwa(repo):
            git(["rebase", "--abort"], repo, timeout=60)
            raise BladHTTP(409, "Twoje i cudze zmiany dotyczą tych samych miejsc w plikach. Niczego nie zmieniono — "
                                "trzeba to scalić ręcznie (poproś agenta o pomoc).", wyjscie=wyjscie, ok=False)
        raise BladHTTP(502 if kod == -2 else 409, _tlumacz_blad(wyjscie, "Nie udało się pobrać zmian."),
                       wyjscie=wyjscie, ok=False)
    finally:
        _uniewaznij(repo)
        _zapis_blokada.release()


def _opis_commita(opis):
    opis = re.sub(r"\s+", " ", str(opis or "")).strip()[:200]
    return "panel: " + (opis or "dane panelu")


def wyslij(repo=None, opis=None, sciezki=None):
    """Commit wyłącznie ścieżek panelu + push. Zwraca {ok, commit?, wyjscie}."""
    repo = _repo(repo)
    sciezki = sciezki if sciezki is not None else sciezki_panelu()
    if not _zapis_blokada.acquire(blocking=False):
        raise BladHTTP(409, "Trwa już inna operacja Git. Poczekaj chwilę.")
    try:
        # tylko ścieżki, które istnieją na dysku albo są znane gitowi (inaczej `git add` zgłasza błąd)
        istniejace = []
        for s in sciezki:
            if os.path.exists(os.path.join(repo, *s.split("/"))):
                istniejace.append(s)
            else:
                kod, out, _ = git(["ls-files", "--", s], repo, timeout=15)
                if kod == 0 and out.strip():
                    istniejace.append(s)
        wyjscia, commit = [], None
        if istniejace:
            kod, out, err = git(["add", "-A", "--"] + istniejace, repo, timeout=60)
            if kod != 0:
                raise BladHTTP(409, "Nie udało się przygotować plików do wysłania.", wyjscie=(out + err).strip(),
                               ok=False)
            kod, _, _ = git(["diff", "--cached", "--quiet", "--"] + istniejace, repo, timeout=30)
            if kod == 1:
                kod, out, err = git(["commit", "-m", _opis_commita(opis), "--"] + istniejace, repo, timeout=60)
                wyjscia.append((out + err).strip())
                if kod != 0:
                    t = (out + err).lower()
                    if "please tell me who you are" in t or "user.email" in t or "user.name" in t:
                        komunikat = ("Git nie zna Twojego imienia i e-maila. Ustaw je raz: "
                                     "git config --global user.name \"Imię\" oraz user.email.")
                    else:
                        komunikat = "Nie udało się zapisać zmian (commit)."
                    raise BladHTTP(409, komunikat, wyjscie="\n".join(wyjscia), ok=False)
                kod, out, _ = git(["rev-parse", "--short", "HEAD"], repo, timeout=10)
                commit = out.strip() if kod == 0 else None
            elif kod != 0:
                raise BladHTTP(409, "Nie udało się sprawdzić zmian w danych panelu.", ok=False)

        upstream = _upstream(repo)
        if upstream:
            kod, out, _ = git(["rev-list", "--count", "@{u}..HEAD"], repo, timeout=15)
            do_wyslania = int(out.strip() or 0) if kod == 0 else 1
            polecenie = ["push"]
        else:
            kod, out, _ = git(["remote"], repo, timeout=10)
            zdalne = out.split()
            if not zdalne:
                if commit:
                    return {"ok": True, "commit": commit, "wyjscie": "\n".join(wyjscia),
                            "uwaga": "Zapisano lokalnie, ale repozytorium nie ma połączenia z GitHubem."}
                raise BladHTTP(409, "Repozytorium nie jest połączone z GitHubem, więc nie ma dokąd wysłać.", ok=False)
            do_wyslania = 1
            polecenie = ["push", "-u", "origin" if "origin" in zdalne else zdalne[0], "HEAD"]

        if not commit and do_wyslania == 0:
            return {"ok": True, "commit": None,
                    "wyjscie": "Nie ma nic do wysłania — dane panelu są już na GitHubie."}

        kod, out, err = git(polecenie, repo, timeout=180)
        wyjscia.append((out + err).strip())
        wyjscie = "\n".join(w for w in wyjscia if w)
        if kod != 0:
            zapisano = (" Twoje zmiany są zapisane na tym komputerze (commit %s) i pójdą przy następnym wysłaniu."
                        % commit) if commit else ""
            if _odrzucony_push(err + out):
                raise BladHTTP(409, "Ktoś wysłał zmiany przed Tobą. Najpierw kliknij Pobierz, a potem Wyślij jeszcze raz."
                               + zapisano, wyjscie=wyjscie, ok=False, commit=commit)
            raise BladHTTP(502 if kod == -2 else 409, _tlumacz_blad(wyjscie, "Nie udało się wysłać zmian.") + zapisano,
                           wyjscie=wyjscie, ok=False, commit=commit)
        return {"ok": True, "commit": commit, "wyjscie": wyjscie}
    finally:
        _uniewaznij(repo)
        _zapis_blokada.release()


# --------------------------------------------------------------------------- trasy
def _t_stan(z):
    wynik = stan()
    if not wynik.get("blad") and wynik.get("zdalne"):
        if moze_fetch():
            wynik["fetch_trwa"] = True
    st = _fetch.get(_repo(None)) or {}
    if st.get("blad"):
        wynik["blad_fetch"] = st["blad"]
    return wynik


def _tylko_lokalnie(z):
    if not z.lokalny:
        raise BladHTTP(403, "Pobieranie i wysyłanie działa tylko na komputerze, na którym działa panel.")


def _t_pobierz(z):
    _tylko_lokalnie(z)
    return pobierz()


def _t_wyslij(z):
    _tylko_lokalnie(z)
    dane = z.json if isinstance(z.json, dict) else {}
    return wyslij(opis=dane.get("opis"))


def zarejestruj(app):
    app.dodaj("GET", "/api/git/stan", _t_stan)
    app.dodaj("POST", "/api/git/pobierz", _t_pobierz)
    app.dodaj("POST", "/api/git/wyslij", _t_wyslij)


def zdrowie():
    s = stan()
    return {"galaz": s.get("galaz"), "zdalne": (s.get("zdalne") or {}).get("url"), "blad": s.get("blad"),
            "sciezki_panelu": sciezki_panelu()}
