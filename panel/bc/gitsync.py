# -*- coding: utf-8 -*-
"""Git: stan repozytorium oraz „Pobierz” / „Wyślij” danych panelu.

- Każde polecenie git idzie przez rdzen.uruchom z limitem czasu i ze środowiskiem, w którym git nigdy nie czeka na
  hasło (GIT_TERMINAL_PROMPT=0, GCM_INTERACTIVE=never, ssh w trybie wsadowym) i pisze komunikaty po angielsku
  (LC_ALL=C), żeby dało się je rozpoznać i przetłumaczyć na zrozumiały polski.
- Stan pamiętany 5 s. `git fetch` w tle (osobny wątek) najwyżej raz na 5 minut, wyzwalany leniwie przez
  GET /api/git/stan — żądanie nigdy na niego nie czeka. Tylko wtedy, gdy NIE działa stała synchronizacja (niżej): ona
  robi fetch w każdym obiegu i po każdym lekkim sprawdzeniu, które zobaczy nowy commit (`FETCH_CO_S` jej nie dotyczy).
- „Wyślij” dodaje i commituje WYŁĄCZNIE ścieżki z `git.sciezki_panelu` (domyślnie `panel/dane`) oraz te pliki planu
  sejfu (Pytania otwarte, Zadania, Rejestr decyzji, Dziennik zmian), które naprawdę zmienił panel i w których nie ma
  cudzych niezatwierdzonych zmian (bc/zapis.py: `do_wyslania`; ślad w danych lokalnych). Opis commita: „panel: …”.
- Funkcje przyjmują `repo=` (domyślnie rdzen.REPO), żeby dało się je sprawdzić na repozytorium testowym.
- Stała synchronizacja (decyzja D-070, od 14.11): wątek w tle co `git.auto_co_s` s robi fetch, samo pobieranie
  (przewinięcie albo zwykłe scalenie — NIGDY autostash ani rebase, bo w katalogu roboczym pracują agenci, Blender
  i ludzie) i samo wysyłanie tego, co wysyła przycisk „Wyślij”. Opis zasad: część „Stała synchronizacja” niżej
  i panel/README.md (Git).
"""
import contextlib
import datetime
import os
import re
import sys
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
                "LANGUAGE": "C", "GIT_OPTIONAL_LOCKS": "0", "GIT_MERGE_AUTOEDIT": "no"})
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
    if petla_dziala(repo):                                     # stała synchronizacja sama robi fetch (jedna operacja naraz)
        return False
    if os.environ.get("BC_GIT_BEZ_SIECI") == "1":              # testy: serwer testowy nie łączy się z GitHubem
        return False
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
def pobierz(repo=None, bezpiecznie=None):
    """„Pobierz”. Przy działającej stałej synchronizacji (albo `bezpiecznie=True`) tą samą bezpieczną drogą co samo
    pobieranie: fetch + przewinięcie albo zwykłe scalenie, bez autostash i bez rebase — praca w toku na tym komputerze
    zostaje nietknięta. Bez niej (jak dawniej) `git pull --rebase --autostash`.
    Zwraca {ok, wyjscie, uwaga?}; przy problemie rzuca BladHTTP z czytelnym opisem."""
    repo = _repo(repo)
    if bezpiecznie is None:
        bezpiecznie = petla_dziala(repo)
    if bezpiecznie:
        _pilnuj(repo)
    if not _zapis_blokada.acquire(blocking=False):
        raise BladHTTP(409, "Trwa już inna operacja Git. Poczekaj chwilę.")
    try:
        # przed _upstream: w trakcie cudzego rebase HEAD jest odłączony, a `git rebase --abort` niżej nie może
        # przerwać rebase, którego panel nie zaczął
        cudza = _cudza_operacja(repo)
        if cudza in ("index_lock", "scalanie"):
            raise BladHTTP(409, "Ktoś właśnie zapisuje commit albo scala zmiany w repozytorium (terminal, agent) — "
                                "spróbuj za chwilę.", ok=False)
        if not _upstream(repo):
            raise BladHTTP(409, "Ta gałąź nie jest połączona z GitHubem, więc nie ma skąd pobrać zmian.")
        if bezpiecznie:
            return _pobierz_reczne_bezpiecznie(repo)
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


def sejf_do_wyslania(repo=None):
    """(ścieżki względem repo, opisy, uwagi) plików sejfu zmienionych przez panel — patrz bc/zapis.py."""
    repo = _repo(repo)
    try:
        from . import zapis
        return zapis.do_wyslania(repo, lambda argumenty, r: git(argumenty, r, timeout=15))
    except Exception as e:                                     # bez modułu zapisu „Wyślij” działa jak dawniej
        rdzen.log("git: nie udało się sprawdzić zmian sejfu z panelu: %r" % e)
        return [], [], []


PODGLAD_WIERSZY = 40
PODGLAD_ZNAKOW = 240


def podglad_sejfu(sciezki_rel, repo=None):
    """Co naprawdę pójdzie do publicznego repozytorium z plików sejfu: [{plik, wiersze:["+ …"/"- …"], ucieto}] z
    `git diff HEAD` (bez kontekstu). Pokazuje to okno „Wyślij”, zanim człowiek kliknie."""
    repo = _repo(repo)
    wynik = []
    for rel in sciezki_rel:
        kod, out, _ = git(["diff", "--no-color", "--no-ext-diff", "-U0", "HEAD", "--", rel], repo, timeout=15)
        if kod != 0:
            continue
        wiersze, w_zmianach = [], False
        for l in out.split("\n"):
            if l.startswith("@@"):                             # nagłówek fragmentu; wcześniej są nagłówki pliku
                w_zmianach = True
            elif w_zmianach and l[:1] in ("+", "-"):
                wiersze.append(l[0] + " " + l[1:].rstrip("\r")[:PODGLAD_ZNAKOW])
        wynik.append({"plik": rel, "wiersze": wiersze[:PODGLAD_WIERSZY],
                      "ucieto": max(0, len(wiersze) - PODGLAD_WIERSZY)})
    return wynik


def wyslij(repo=None, opis=None, sciezki=None, z_sejfem=None):
    """Commit wyłącznie ścieżek panelu (+ plików sejfu zmienionych przez panel) + push. Zwraca {ok, commit?, wyjscie}.
    `z_sejfem` domyślnie włączone, gdy nie podano własnych `sciezki`."""
    repo = _repo(repo)
    if z_sejfem is None:
        z_sejfem = sciezki is None
    sciezki = sciezki if sciezki is not None else sciezki_panelu()
    if not _zapis_blokada.acquire(blocking=False):
        raise BladHTTP(409, "Trwa już inna operacja Git. Poczekaj chwilę.")
    try:
        wynik = _wyslij(repo, opis, sciezki, z_sejfem)
        if wynik.get("ok") and (wynik.get("commit") or "Nie ma nic do wysłania" not in str(wynik.get("wyjscie"))):
            _zapisz_wyslanie(repo, _st(repo), wynik.get("commit"), recznie=True)
        return wynik
    finally:
        _uniewaznij(repo)
        _zapis_blokada.release()


def _blokada_sejfu(z_sejfem):
    """Blokada zapisu sejfu z panelu (bc/zapis.py) na czas od sprawdzenia plików do wyczyszczenia śladu po commicie —
    inaczej odpowiedź zapisana w trakcie commita zostałaby niezacommitowana i bez śladu. Bez modułu zapisu: nic."""
    if z_sejfem:
        try:
            from . import zapis
            return zapis.blokada_wysylania()
        except ImportError:
            pass
    return contextlib.nullcontext()


def _wyslij(repo, opis, sciezki, z_sejfem):
    with _blokada_sejfu(z_sejfem):                             # push (długi) już poza blokadą sejfu
        commit, wyjscia, dodatki = _zatwierdz(repo, opis, sciezki, z_sejfem)

    def wynik(d):
        if dodatki.get("uwaga") and d.get("uwaga"):
            d["uwaga"] = d["uwaga"] + " " + dodatki["uwaga"]
        return dict(dodatki, **d)
    return _wypchnij(repo, commit, wyjscia, wynik)


def _zatwierdz(repo, opis, sciezki, z_sejfem):
    """`git add` + `git commit` ścieżek panelu i plików sejfu z panelu. Zwraca (commit albo None, wyjścia, dodatki)."""
    sejf_sciezki, sejf_opisy, sejf_uwagi = sejf_do_wyslania(repo) if z_sejfem else ([], [], [])
    dodatki = {}
    if sejf_sciezki:
        dodatki["pliki_sejfu"] = sejf_sciezki
    uwagi = list(sejf_uwagi)
    if not str(opis or "").strip() and sejf_opisy:
        opis = "; ".join(dict.fromkeys(sejf_opisy))           # bez powtórzeń, w kolejności zmian

    # tylko ścieżki, które istnieją na dysku albo są znane gitowi (inaczej `git add` zgłasza błąd)
    istniejace = []
    for s in sciezki:
        if os.path.exists(os.path.join(repo, *s.split("/"))):
            istniejace.append(s)
        else:
            kod, out, _ = git(["ls-files", "--", s], repo, timeout=15)
            if kod == 0 and out.strip():
                istniejace.append(s)
    istniejace += [s for s in sejf_sciezki if s not in istniejace]
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
            if sejf_sciezki:                                   # zmiany sejfu z panelu są już w commicie
                try:
                    from . import zapis
                    gitfn = lambda argumenty, r: git(argumenty, r, timeout=15)
                    for rel in zapis.po_commicie(repo, gitfn, sejf_sciezki):
                        uwagi.append("%s zmienił się w trakcie wysyłania (Obsidian albo agent) — commit zawiera też "
                                     "tę zmianę spoza panelu; zajrzyj do niego." % rel)
                    zapis.wyslano(repo, sejf_sciezki)
                except Exception as e:
                    rdzen.log("git: nie udało się wyczyścić śladu zmian sejfu: %r" % e)
        elif kod != 0:
            raise BladHTTP(409, "Nie udało się sprawdzić zmian w danych panelu.", ok=False)
    if uwagi:
        dodatki["uwaga"] = " ".join(uwagi)
    return commit, wyjscia, dodatki


def _wypchnij(repo, commit, wyjscia, wynik):
    """`git push` po commicie (albo zaległych commitach). `wynik(d)` dokleja pola z etapu commita."""

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
                return wynik({"ok": True, "commit": commit, "wyjscie": "\n".join(wyjscia),
                              "uwaga": "Zapisano lokalnie, ale repozytorium nie ma połączenia z GitHubem."})
            raise BladHTTP(409, "Repozytorium nie jest połączone z GitHubem, więc nie ma dokąd wysłać.", ok=False)
        do_wyslania = 1
        polecenie = ["push", "-u", "origin" if "origin" in zdalne else zdalne[0], "HEAD"]

    if not commit and do_wyslania == 0:
        return wynik({"ok": True, "commit": None,
                      "wyjscie": "Nie ma nic do wysłania — dane panelu są już na GitHubie."})

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
    return wynik({"ok": True, "commit": commit, "wyjscie": wyjscie})


# --------------------------------------------------------------------------- trasy
def _t_stan(z):
    wynik = stan()
    if not wynik.get("blad"):                                  # pliki sejfu zmienione w panelu też idą przyciskiem „Wyślij”
        sejf_sciezki, _, sejf_uwagi = sejf_do_wyslania()
        wynik["zmiany_sejfu"] = sejf_sciezki
        wynik["zmiany_panelu"] = wynik.get("zmiany_panelu", 0) + len(sejf_sciezki)
        if sejf_uwagi:
            wynik["uwagi_sejfu"] = sejf_uwagi
        if sejf_sciezki:
            wynik["podglad_sejfu"] = podglad_sejfu(sejf_sciezki)
    if not wynik.get("blad") and wynik.get("zdalne"):
        if moze_fetch():
            wynik["fetch_trwa"] = True
    st = _fetch.get(_repo(None)) or {}
    if st.get("blad"):
        wynik["blad_fetch"] = st["blad"]
    wynik["auto"] = stan_auto()
    return wynik


def _t_auto(z):
    """Sam stan stałej synchronizacji — bez uruchamiania gita (powłoka pyta co 30 s, czy przyszły cudze zmiany)."""
    return stan_auto()


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
    app.dodaj("GET", "/api/git/auto", _t_auto)
    app.dodaj("POST", "/api/git/pobierz", _t_pobierz)
    app.dodaj("POST", "/api/git/wyslij", _t_wyslij)


def zdrowie():
    s = stan()
    a = stan_auto()
    return {"galaz": s.get("galaz"), "zdalne": (s.get("zdalne") or {}).get("url"), "blad": s.get("blad"),
            "sciezki_panelu": sciezki_panelu(), "auto": {"wlaczona": a["wlaczona"], "stan": a["stan"]}}


# =========================================================================== stała synchronizacja (D-070)
# Pętla w tle (wątek „git-auto”) na komputerze z panelem. Co `git.auto_co_s` s (domyślnie 90) jeden obieg:
#   0. nic nie rób, gdy trwa inna operacja panelu (ta sama blokada co „Pobierz”/„Wyślij”), ktoś właśnie commituje
#      (index.lock) albo trwa cudze scalanie / rebase / cherry-pick;
#   1. `git fetch` (bez czekania na hasło, z limitem czasu);
#   2. SAMO POBIERANIE, bezpieczne dla pracy w toku: najpierw próba na sucho (`git merge-tree`, `git diff`), czy
#      nadchodzące zmiany nie dotykają plików zmienionych lokalnie (także nieśledzonych i ignorowanych, także pliku
#      leżącego tam, gdzie nadchodzi katalog), czy nikt nie ma plików dodanych do commita (`git add` bez commita) i czy
#      nie ma konfliktu. Gdy dotykają albo są dodane — stan „czeka” (nic nie ruszone); konflikt — stan „konflikt”, bez
#      ponawiania, dopóki nie zmieni się lokalny albo zdalny commit. Inaczej katalog roboczy rusza tylko przewinięcie
#      (`merge --ff-only --no-autostash --no-overwrite-ignore`), które git przy kolizji czysto odrzuca. Przy własnych
#      commitach commit scalający „panel: scalenie zmian z GitHuba” powstaje POZA katalogiem roboczym (`merge-tree` →
#      `commit-tree`), a gałąź przechodzi na niego tym samym przewinięciem. Zwykłego `git merge` nie ma (przy odmowie
#      strategia ort sama robi reset --hard i stash apply), nie ma też rebase, reset, stash ani usuwania plików;
#      2b. ZAPIS PRZED POBRANIEM (od 16.11, `git.auto_commit_przed_pobraniem`, domyślnie tak): gdy WSZYSTKIE kolizje
#      to własne, niewysłane zmiany panelu (pliki z `git.sciezki_panelu` albo pliki sejfu zmienione w panelu bez cudzych
#      zmian — dokładnie to, co commituje „Wyślij”), panel zapisuje je commitem TYLKO LOKALNIE i pobiera od razu (krok 2
#      drugi raz, już drogą commita scalającego). Wcześniej to był zastój: pobieranie czekało na commit zmian panelu,
#      a krok 3 nie commituje, dopóki na GitHubie są niepobrane zmiany — każdy agent dopisuje się do Dziennika zmian,
#      każde kliknięcie w panelu też, więc pobieranie stało, aż ktoś kliknął „Wyślij” (16.11: 10 minut). Cudza praca
#      w toku dalej = „czeka”;
#   3. SAMO WYSYŁANIE: dokładnie to, co przycisk „Wyślij” (`_zatwierdz`: ścieżki panelu i pliki sejfu zmienione w
#      panelu bez cudzych zmian), gdy od ostatniej zmiany minęło `git.auto_wyslij_po_s` s (domyślnie 60) albo od
#      pierwszej czekającej 5 min; lokalne commity — gdy najnowszy ma co najmniej tyle samo lat. Commit z kroku 2b idzie
#      tą samą regułą co zmiany, które zapisał (pierwsza zmiana i spokój liczone dalej) — nic nie wychodzi wcześniej
#      tylko dlatego, że trzeba było pobrać. Push (nigdy --force); odrzucony, bo ktoś wysłał wcześniej — krok 2 (bez
#      2b) i push jeszcze raz (jeden raz).
# Między obiegami, co `git.auto_sprawdz_co_s` s (domyślnie 30; 0 = wyłączone), lekkie sprawdzenie bez fetch, bez
# `git status` i bez blokady (`sprawdz_lekko`: `git ls-remote` gałęzi na GitHubie, a gdy pobieranie czeka — HEAD).
# Nowy commit = od razu obieg „samo pobieranie” (kroki 0–2b; bez kroku 3, bez publikacji prac i bez przesuwania
# zwykłego rytmu), więc cudze zmiany są tu średnio po ok. 20 s (najdłużej ok. 40 s), a wysyłanie dalej tylko
# w zwykłych obiegach.
# Błąd sieci: rosnący odstęp (2×, 4×, … `auto_co_s`, najwyżej 15 min); brak logowania: od razu co 15 min.
# Telegram (bc/telegram.py, wyłącznik `git.auto_telegram`): cudze commity po samym pobraniu; konflikt / błąd / brak
# logowania dłużej niż dwa obiegi — jedna wiadomość na incydent i jedna po powrocie do normy.
STANY_AUTO = ("ok", "pobieram", "wysylam", "czeka", "konflikt", "blad", "brak_logowania", "wylaczona")
STANY_PROBLEMU = ("konflikt", "blad", "brak_logowania")
ZMIENNA_WYLACZNIKA = "BC_GIT_AUTO"                             # "0" = wyłączone, "1" = włączone także na danych zastępczych
ZBIERAJ_NAJWYZEJ_S = 300                                       # najdłużej czekająca zmiana panelu idzie po 5 min
SPRAWDZ_CO_S = 30.0                                            # lekkie sprawdzenie GitHuba między obiegami (domyślnie)
ZDALNA_PAMIEC_S = 600                                          # nazwa zdalnego i gałęzi do `ls-remote` — pamiętana 10 min
MAKS_ODSTEP_S = 900                                            # przy błędach najwyżej co 15 min
START_PO_S = 15                                                # pierwszy obieg chwilę po starcie panelu
POMINIEC_DO_UWAGI = 10                                         # tyle obiegów z index.lock = uwaga dla człowieka
OPIS_SCALENIA = "panel: scalenie zmian z GitHuba"
MAKS_PLIKOW_W_STANIE = 10
MAKS_COMMITOW_W_STANIE = 5
_RX_STERUJACE = re.compile("[\x00-\x1f\x7f-\x9f​-‏‪-‮⁠-⁩﻿]")

_auto = {}                                                     # repo -> stan (słownik, pod _auto_blokada)
_auto_blokada = threading.RLock()
_petla = {"watek": None, "stop": None, "repo": None}
_ID_STARTU = "%x" % int(time.time())                          # część id pobrania: nowy proces = nowe id


def _liczba(wartosc, domyslnie, od, do):
    try:
        w = float(wartosc)
    except (TypeError, ValueError):
        return domyslnie
    return max(od, min(do, w))


def ustawienia_auto():
    """{auto, co_s, wyslij_po_s, sprawdz_co_s, commit_przed_pobraniem, telegram} z `git.*` konfiguracji (domyślnie:
    włączone, 90 s, 60 s, 30 s, tak, Telegram tak). Liczby przycięte do rozsądnych granic — wspólna konfiguracja jest
    w repozytorium, więc nie może wymusić fetch co sekundę. `auto_sprawdz_co_s` = 0 (albo false) wyłącza lekkie
    sprawdzanie między obiegami."""
    g = rdzen.konfiguracja().get("git") or {}
    sprawdz = g.get("auto_sprawdz_co_s")
    wylaczone = sprawdz is False or (not isinstance(sprawdz, bool) and _liczba(sprawdz, 1.0, -1e9, 1e9) <= 0)
    return {"auto": g.get("auto", True) is not False,
            "co_s": _liczba(g.get("auto_co_s"), 90.0, 30.0, 3600.0),
            "wyslij_po_s": _liczba(g.get("auto_wyslij_po_s"), 60.0, 10.0, 3600.0),
            "sprawdz_co_s": 0.0 if wylaczone else _liczba(sprawdz, SPRAWDZ_CO_S, 15.0, 600.0),
            "commit_przed_pobraniem": g.get("auto_commit_przed_pobraniem", True) is not False,
            "telegram": g.get("auto_telegram", True) is not False}


def powod_wylaczenia():
    """None, gdy pętla może wystartować na tym komputerze; inaczej zdanie, dlaczego nie."""
    zm = os.environ.get(ZMIENNA_WYLACZNIKA, "").strip()
    if zm == "0":
        return "Samo pobieranie i wysyłanie jest wyłączone (zmienna środowiskowa BC_GIT_AUTO=0)."
    if zm != "1" and (os.environ.get("BC_PANEL_DANE") or os.environ.get("BC_PANEL_RUNTIME")):
        return "Samo pobieranie i wysyłanie jest wyłączone: panel działa na katalogach zastępczych (np. w testach)."
    if not ustawienia_auto()["auto"]:
        return "Samo pobieranie i wysyłanie jest wyłączone w ustawieniach panelu (git.auto = false)."
    return None


_PRAWDZIWE_REPO = os.path.normcase(os.path.realpath(rdzen.REPO))   # z chwili importu: test nie podmieni go łatką


def _pilnuj(repo):
    """Bezpiecznik testów: w procesie z unittest samo pobieranie i wysyłanie nie ruszy prawdziwego repozytorium."""
    if "unittest" in sys.modules and os.path.normcase(os.path.realpath(repo)) == _PRAWDZIWE_REPO:
        raise RuntimeError("Bezpiecznik testów: stała synchronizacja nie działa na prawdziwym repozytorium w testach "
                           "— podaj repo= z katalogu tymczasowego.")


def petla_dziala(repo=None):
    w = _petla.get("watek")
    return bool(w and w.is_alive() and _petla.get("repo") == _repo(repo))


def _nowy_stan():
    return {"wlaczona": True, "stan": "ok", "opis": "Pierwsze sprawdzenie GitHuba za chwilę.", "krotko": None,
            "co_zrobic": None, "pliki": [], "plikow": 0, "zgodne": None, "ostatni_obieg": None, "nastepna_proba": 0.0,
            "bledy_z_rzedu": 0, "pominiete": 0, "konflikt_klucz": None, "pierwsza_zmiana": None,
            "czeka_na_wyslanie": 0, "pobranie": None, "wyslanie": None, "licznik_pobran": 0, "obiegi_problemu": 0,
            "incydent": None, "do_powiadomienia": None, "wczesny_commit": None, "do_pobrania": 0,
            "do_pobrania_od": None, "do_pobrania_assety": False, "head_po_obiegu": None, "zdalna": None}


def _st(repo):
    with _auto_blokada:
        return _auto.setdefault(_repo(repo), _nowy_stan())


def _bez_sciezek(t):
    """Ścieżki bezwzględne repozytorium i katalogu domowego (z nazwą użytkownika systemu) → krótkie znaczniki.
    Opis błędu gita widzi też gość przez link i grupa na Telegramie."""
    for sciezka, znak in ((rdzen.REPO, "<repo>"), (os.path.expanduser("~"), "~")):
        if not sciezka or len(sciezka) < 4:
            continue
        for wariant in sorted({sciezka, sciezka.replace("\\", "/"), sciezka.replace("/", "\\")}):
            t = re.sub(re.escape(wariant), lambda m, z=znak: z, t, flags=re.IGNORECASE)
    return t


def _czysty(t, n=120):
    t = re.sub(r"\s+", " ", _RX_STERUJACE.sub(" ", str(t or ""))).strip()
    t = re.sub(r"([a-z][a-z0-9+.-]*://)[^/@\s]*@", r"\1", t, flags=re.IGNORECASE)   # bez loginu i tokenu w adresach
    t = _bez_sciezek(t)
    return t if len(t) <= n else t[:n - 1].rstrip() + "…"


def _ustaw(st, stan, opis, krotko=None, co_zrobic=None, pliki=None, zgodne=False):
    with _auto_blokada:
        st.update(stan=stan, opis=_czysty(opis, 400), krotko=krotko, co_zrobic=co_zrobic)
        if pliki is not None:
            st["pliki"] = [_czysty(p, 200) for p in pliki[:MAKS_PLIKOW_W_STANIE]]
            st["plikow"] = len(pliki)
        elif stan not in ("pobieram", "wysylam"):
            st["pliki"], st["plikow"] = [], 0
        if zgodne:
            st["zgodne"] = rdzen.teraz()


def stan_auto(repo=None):
    """Stan stałej synchronizacji dla API (pole `auto` w GET /api/git/stan i GET /api/git/auto). Bez uruchamiania gita."""
    repo = _repo(repo)
    st = _st(repo)
    ustaw = ustawienia_auto()
    with _auto_blokada:
        wynik = {k: st.get(k) for k in ("wlaczona", "stan", "opis", "krotko", "co_zrobic", "pliki", "plikow", "zgodne",
                                        "ostatni_obieg", "czeka_na_wyslanie", "pobranie", "wyslanie", "do_pobrania",
                                        "do_pobrania_od", "do_pobrania_assety")}
        wynik["do_pobrania"] = int(wynik.get("do_pobrania") or 0)
        wynik["do_pobrania_assety"] = bool(wynik["do_pobrania"] and wynik.get("do_pobrania_assety"))
        wynik["pobranie"] = dict(st["pobranie"]) if st.get("pobranie") else None
        wynik["wyslanie"] = dict(st["wyslanie"]) if st.get("wyslanie") else None
        wynik["pliki"] = list(st.get("pliki") or [])
        if st.get("nastepna_proba") and st["nastepna_proba"] > time.time():
            wynik["nastepna_proba"] = datetime.datetime.fromtimestamp(st["nastepna_proba"]).astimezone().isoformat(
                timespec="seconds")
    # pętla nie działa w tym procesie i nie było żadnego obiegu (np. testy, --lan bez GitHuba): „wyłączona” z powodem
    if not petla_dziala(repo) and not wynik.get("ostatni_obieg") and wynik.get("stan") != "wylaczona":
        wynik.update(stan="wylaczona", krotko=None, co_zrobic=None,
                     opis=powod_wylaczenia() or "Samo pobieranie i wysyłanie nie działa w tym procesie panelu.")
    if wynik.get("stan") == "wylaczona":
        wynik["wlaczona"] = False
        wynik.update(do_pobrania=0, do_pobrania_od=None, do_pobrania_assety=False)
    wynik.update(co_s=int(ustaw["co_s"]), wyslij_po_s=int(ustaw["wyslij_po_s"]),
                 sprawdz_co_s=int(ustaw["sprawdz_co_s"]))
    return wynik


def czeka_z_githuba(repo=None):
    """Dla innych modułów (zakładka Assety, co 2 s): czy na GitHubie leżą zmiany, których panel jeszcze nie pobrał —
    {ile, od, assety (czy dotyczą assets/), stan, krotko} albo None. Bez gita i bez czytania konfiguracji."""
    repo = _repo(repo)
    with _auto_blokada:
        st = _auto.get(repo)
        if not st or not st.get("do_pobrania") or st.get("stan") == "wylaczona":
            return None
        return {"ile": int(st["do_pobrania"]), "od": st.get("do_pobrania_od"), "assety": bool(st.get("do_pobrania_assety")),
                "stan": st.get("stan"), "krotko": st.get("krotko")}


# --------------------------------------------------------------------------- pomocnicze polecenia (tylko odczyt)
def _git_dir(repo):
    kod, out, _ = git(["rev-parse", "--absolute-git-dir"], repo, timeout=10)
    return out.strip() if kod == 0 and out.strip() else None


def _cudza_operacja(repo):
    """None, "index_lock" (ktoś właśnie zapisuje indeks / commituje), "scalanie" (cudze scalanie, rebase,
    cherry-pick, revert) albo "brak_repo" (git nie widzi repozytorium) — wtedy panel nic nie robi."""
    gd = _git_dir(repo)
    if not gd:
        return "brak_repo"
    if os.path.exists(os.path.join(gd, "index.lock")):
        return "index_lock"
    for n in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply"):
        if os.path.exists(os.path.join(gd, n)):
            return "scalanie"
    return None


def _rev(repo, ref):
    kod, out, _ = git(["rev-parse", "--verify", "--quiet", ref + "^{commit}"], repo, timeout=10)
    return out.strip() if kod == 0 and out.strip() else None


def _przod_tyl(repo):
    kod, out, _ = git(["rev-list", "--left-right", "--count", "HEAD...@{u}"], repo, timeout=20)
    try:
        a, b = out.split()
        return int(a), int(b)
    except ValueError:
        return 0, 0


def _brudne(repo):
    """Ścieżki zmienione lokalnie (śledzone i nieśledzone, bez ignorowanych) — z `git status`. None = błąd."""
    kod, out, _ = git(["status", "--porcelain=v1", "-z", "-uall", "--no-renames"], repo, timeout=60)
    if kod != 0:
        return None
    return [p for _, p in _parsuj_status(out)[1]]


def _lista_z(out):
    return [p for p in out.split("\0") if p]


def _zmienione_miedzy(repo, a, b):
    kod, out, _ = git(["diff", "--name-only", "-z", "--no-renames", a, b], repo, timeout=60)
    return _lista_z(out) if kod == 0 else None


def _dodane_do_indeksu(repo):
    """Ścieżki dodane do indeksu (`git add`), a jeszcze bez commita — indeks różny od HEAD. None = błąd."""
    kod, out, _ = git(["diff", "--cached", "--name-only", "-z", "--no-renames", "HEAD", "--"], repo, timeout=60)
    return _lista_z(out) if kod == 0 else None


def _ignorowane_na_drodze(repo, pliki):
    """Pliki, które scalenie by zapisało, a na dysku leżą jako nieśledzone IGNOROWANE (git nadpisałby je bez pytania),
    oraz katalogi nadrzędne nadchodzących plików, które na dysku są nieśledzonym PLIKIEM albo dowiązaniem (nadchodzi
    `build/x.txt`, a leży ignorowany plik `build` — git skasowałby go bez pytania)."""
    wynik = []
    istniejace = [p for p in pliki if os.path.lexists(os.path.join(repo, *p.split("/")))]
    for i in range(0, len(istniejace), 100):
        kod, out, _ = git(["--literal-pathspecs", "ls-files", "-z", "--others", "--ignored", "--exclude-standard",
                           "--"] + istniejace[i:i + 100], repo, timeout=60)
        if kod == 0:
            wynik += _lista_z(out)
    przedrostki = {}
    for p in pliki:
        cz = p.split("/")
        for j in range(1, len(cz)):
            d = "/".join(cz[:j])
            if d in przedrostki:
                continue
            pelna = os.path.join(repo, *cz[:j])
            przedrostki[d] = os.path.lexists(pelna) and (os.path.islink(pelna) or not os.path.isdir(pelna))
    na_drodze = [d for d, plik in przedrostki.items() if plik]
    if na_drodze:
        kod, out, _ = git(["--literal-pathspecs", "ls-files", "-z", "--"] + na_drodze, repo, timeout=60)
        sledzone = set(_lista_z(out)) if kod == 0 else set()
        # śledzony plik zastąpiony katalogiem to zwykła zmiana z GitHuba (git sprawdzi, czy nie jest zmieniony lokalnie)
        wynik += [d for d in na_drodze if d not in sledzone and d not in wynik]
    return wynik


def _migawka(repo):
    """Stan katalogu roboczego do porównania przed i po próbie: wynik `git status` + rozmiar i czas zmian plików."""
    kod, out, _ = git(["status", "--porcelain=v1", "-z", "-uall", "--no-renames"], repo, timeout=60)
    pliki = {}
    for _, p in _parsuj_status(out)[1]:
        try:
            s = os.stat(os.path.join(repo, *p.split("/")))
            pliki[p] = (s.st_size, s.st_mtime_ns)
        except OSError:
            pliki[p] = None
    return out if kod == 0 else None, pliki


def _pliki_z_odmowy(tekst):
    """Lista plików z komunikatu gita „…would be overwritten by merge:” — pod nim pliki z wcięciem (tabulator albo
    spacje, zależnie od miejsca w gicie), do pierwszego wiersza bez wcięcia."""
    wynik, w_liscie = [], False
    for l in (tekst or "").splitlines():
        if l.rstrip().endswith(":") and ("would be" in l or "untracked working tree files" in l):
            w_liscie = True
            continue
        if w_liscie and l[:1] in ("\t", " ") and l.strip():
            wynik.append(l.strip())
            continue
        w_liscie = False
    return list(dict.fromkeys(wynik))


def _nadchodzace(repo, gora):
    kod, out, _ = git(["log", "--no-merges", "-n", "200", "--format=%h%x1f%an%x1f%s", "HEAD.." + gora], repo, timeout=20)
    wynik = []
    for linia in (out.splitlines() if kod == 0 else []):
        cz = linia.split("\x1f")
        if len(cz) >= 3:
            wynik.append({"hash": cz[0][:12], "autor": _czysty(cz[1], 60) or "ktoś", "temat": _czysty(cz[2], 120)})
    return wynik


def _ja(repo):
    kod, out, _ = git(["config", "user.name"], repo, timeout=10)
    return out.strip() if kod == 0 else ""


def _rodzaj_bledu(tekst):
    t = (tekst or "").lower()
    if "authentication failed" in t or "terminal prompts disabled" in t or "could not read username" in t \
            or "could not read password" in t or "permission denied" in t or "error: 403" in t \
            or "invalid username or password" in t or "returned error: 403" in t:
        return "brak_logowania"
    if "could not resolve host" in t or "unable to access" in t or "failed to connect" in t or "timed out" in t \
            or "przekroczony czas" in t or "connection reset" in t or "network is unreachable" in t:
        return "siec"
    return "inny"


CO_ZROBIC_LOGOWANIE = ("Na komputerze z panelem zaloguj się raz do GitHuba (np. `git push` w terminalu albo GitHub "
                       "Desktop). Panel sam spróbuje znowu za 15 minut.")
CO_ZROBIC_SIEC = "Sprawdź internet. Panel spróbuje sam — coraz rzadziej, najwyżej co 15 minut."


def _porazka(st, rodzaj, teraz, co_s):
    """Rosnący odstęp przed kolejną próbą (bez szybkich ponowień przy błędzie)."""
    with _auto_blokada:
        st["bledy_z_rzedu"] = st.get("bledy_z_rzedu", 0) + 1
        if rodzaj == "brak_logowania":
            odstep = MAKS_ODSTEP_S
        else:
            odstep = min(MAKS_ODSTEP_S, co_s * (2 ** min(st["bledy_z_rzedu"], 10)))
        st["nastepna_proba"] = teraz + odstep


def _blad_sieci(st, tekst, teraz, ustaw, co_robil):
    rodzaj = _rodzaj_bledu(tekst)
    if rodzaj == "brak_logowania":
        _ustaw(st, "brak_logowania", "GitHub nie przyjął logowania (%s)." % co_robil, krotko="brak logowania",
               co_zrobic=CO_ZROBIC_LOGOWANIE)
    elif rodzaj == "siec":
        _ustaw(st, "blad", "Brak połączenia z GitHubem (%s)." % co_robil, krotko="brak połączenia",
               co_zrobic=CO_ZROBIC_SIEC)
    else:
        _ustaw(st, "blad", "Git zgłosił błąd (%s): %s" % (co_robil, _czysty(tekst, 240) or "bez opisu"),
               krotko="błąd gita", co_zrobic="Poproś agenta na komputerze z panelem, żeby sprawdził `git fetch` "
                                             "i `git push`. Panel spróbuje sam — coraz rzadziej, najwyżej co 15 minut.")
    _porazka(st, rodzaj, teraz, ustaw["co_s"])


def _fetch_teraz(repo):
    kod, _, err = git(["fetch", "--quiet", "--prune"], repo, timeout=90)
    with _fetch_blokada:
        f = _fetch.setdefault(repo, {"proba": 0.0, "kiedy": None, "trwa": False, "blad": None})
        f["proba"] = time.time()
        if kod == 0:
            f.update(kiedy=rdzen.teraz(), blad=None)
        else:
            f["blad"] = _tlumacz_blad(err, "Nie udało się sprawdzić zmian na GitHubie")
    return kod, err


# --------------------------------------------------------------------------- S2: samo pobieranie
def _zapisz_pobranie(repo, st, commity):
    ja = _ja(repo).strip().casefold()
    with _auto_blokada:
        st["licznik_pobran"] = st.get("licznik_pobran", 0) + 1
        autorzy = list(dict.fromkeys(c["autor"] for c in commity))
        st["pobranie"] = {"id": "%s-%d" % (_ID_STARTU, st["licznik_pobran"]), "kiedy": rdzen.teraz(),
                          "ile": len(commity), "autorzy": autorzy[:MAKS_COMMITOW_W_STANIE],
                          "commity": [dict(c) for c in commity[:MAKS_COMMITOW_W_STANIE]]}
        obce = [c for c in commity if c["autor"].strip().casefold() != ja]
        st["do_powiadomienia"] = obce or None


def _do_pobrania(st, ile, assety=None):
    """Ile commitów z GitHuba czeka na pobranie (po ostatnim fetch) — dla pola `auto` i zakładki Assety."""
    with _auto_blokada:
        if not ile:
            st.update(do_pobrania=0, do_pobrania_od=None, do_pobrania_assety=False)
            return
        st["do_pobrania"] = int(ile)
        st["do_pobrania_od"] = st.get("do_pobrania_od") or rdzen.teraz()
        if assety is not None:
            st["do_pobrania_assety"] = bool(assety)


def _dotyczy_assetow(pliki):
    return any(p == "assets/manifest.json" or p.startswith("assets/processed/") for p in pliki or [])


def _pobierz_bezpiecznie(repo, st, reczne=False, sciezki=None, ustaw=None, teraz=None, wczesny=True):
    """Krok S2. Zwraca (wynik, szczegóły): "aktualne", "pobrano", "czeka", "konflikt", "blad". Ustawia stan.
    Niczego nie nadpisuje: każda kolizja z lokalną pracą = „czeka” bez dotykania plików. Wyjątek (krok 2b): kolizje,
    które są WYŁĄCZNIE własnymi zmianami panelu, idą najpierw do lokalnego commita (`_zapisz_przed_pobraniem`), a
    pobieranie rusza od razu drogą commita scalającego. `wczesny=False` — bez kroku 2b (ponowienie po odrzuconym
    wysłaniu: wtedy push idzie zaraz potem, a zmiany panelu mają czekać na swój spokój)."""
    przod, tyl = _przod_tyl(repo)
    if tyl == 0:
        with _auto_blokada:
            st["konflikt_klucz"] = None
        _do_pobrania(st, 0)
        return "aktualne", {"przod": przod}
    kod, out, _ = git(["diff", "--name-only", "-z", "--no-renames", "HEAD...@{u}", "--"], repo, timeout=60)
    _do_pobrania(st, tyl, _dotyczy_assetow(_lista_z(out)) if kod == 0 else None)
    head, gora = _rev(repo, "HEAD"), _rev(repo, "@{u}")
    if not head or not gora:
        _ustaw(st, "blad", "Nie udało się odczytać commitów (HEAD albo gałęzi na GitHubie).", krotko="błąd gita",
               co_zrobic="Poproś agenta, żeby sprawdził repozytorium na komputerze z panelem.")
        return "blad", {}
    klucz = head + ".." + gora
    if not reczne and st.get("konflikt_klucz") == klucz:          # ten sam konflikt — nie próbujemy w kółko
        return "konflikt", {"powtorka": True}
    commity = _nadchodzace(repo, gora)
    ile = len(commity) or tyl
    nazwy = _odmiana_zmian(ile)                                 # „1 zmianę”, „2 zmiany”, „5 zmian”
    drzewo = None
    if przod == 0:
        zmienione = _zmienione_miedzy(repo, head, gora)
    else:
        kod, out, err = git(["merge-tree", "--write-tree", "--name-only", "--no-messages", head, gora], repo,
                            timeout=120)
        linie = [l for l in out.splitlines() if l.strip()]
        if kod == 1 and linie:
            konfl = list(dict.fromkeys(linie[1:]))
            with _auto_blokada:
                st["konflikt_klucz"] = klucz
            _ustaw(st, "konflikt", "Zmiany z GitHuba (%d) i commity z tego komputera zmieniają te same miejsca w "
                                   "plikach. Panel niczego nie zmienił." % ile,
                   krotko="potrzebny człowiek", pliki=konfl,
                   co_zrobic="Poproś agenta na komputerze z panelem: „scal zmiany z GitHuba i rozwiąż konflikt” "
                             "(albo w terminalu `git pull` i ręczne scalenie). Panel spróbuje sam dopiero, gdy "
                             "zmieni się commit tutaj albo na GitHubie.")
            return "konflikt", {"pliki": konfl}
        if kod != 0 or not linie:
            _ustaw(st, "blad", "Nie udało się sprawdzić scalenia na sucho: %s" % (_czysty(err, 200) or kod),
                   krotko="błąd gita", co_zrobic="Poproś agenta, żeby pobrał zmiany ręcznie (git pull bez rebase).")
            return "blad", {}
        drzewo = linie[0].strip()
        if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", drzewo):
            _ustaw(st, "blad", "Próba scalenia na sucho dała nieoczekiwany wynik.", krotko="błąd gita",
                   co_zrobic="Poproś agenta, żeby pobrał zmiany ręcznie (git pull bez rebase).")
            return "blad", {}
        zmienione = _zmienione_miedzy(repo, head, drzewo)
    brudne = _brudne(repo)
    if zmienione is None or brudne is None:
        _ustaw(st, "blad", "Nie udało się porównać zmian z GitHuba z plikami na dysku.", krotko="błąd gita",
               co_zrobic="Panel spróbuje w następnym obiegu.")
        return "blad", {}
    lokalne = {os.path.normcase(p): p for p in brudne}
    kolizje = [p for p in zmienione if os.path.normcase(p) in lokalne]
    kolizje += [p for p in _ignorowane_na_drodze(repo, [p for p in zmienione if p not in kolizje]) if p not in kolizje]
    if kolizje:
        ustaw = dict(ustawienia_auto(), **(ustaw or {}))
        if wczesny and ustaw.get("commit_przed_pobraniem", True):
            try:
                # Blokada zapisu sejfu od sprawdzenia plików do końca pobierania: kliknięcie w panelu w tym czasie
                # poczeka (najwyżej 15 s), zamiast zmienić plik między lokalnym commitem a przewinięciem.
                with _blokada_sejfu(True):
                    if _zapisz_przed_pobraniem(repo, st, kolizje, lokalne,
                                               sciezki if sciezki is not None else sciezki_panelu(),
                                               time.time() if teraz is None else teraz):
                        return _pobierz_bezpiecznie(repo, st, reczne=reczne, sciezki=sciezki, ustaw=ustaw,
                                                    teraz=teraz, wczesny=False)
            except BladHTTP as e:                              # zapis z panelu trwa dłużej — następny obieg
                rdzen.log("git-auto: zapis przed pobraniem odłożony: %s" % e.komunikat)
        _ustaw_czeka_na_pliki(st, kolizje, ile)
        return "czeka", {"pliki": kolizje}
    dodane = _dodane_do_indeksu(repo)                         # ktoś jest w trakcie commita (git add, commit jeszcze nie)
    if dodane is None:
        _ustaw(st, "blad", "Nie udało się sprawdzić plików dodanych do commita (git diff --cached).",
               krotko="błąd gita", co_zrobic="Panel spróbuje w następnym obiegu.")
        return "blad", {}
    if dodane:
        _ustaw_czeka_na_dodane(st, dodane, ile)
        return "czeka", {"pliki": dodane}

    # Katalog roboczy rusza WYŁĄCZNIE `git merge --ff-only` (przewinięcie): git sprawdza pliki i odmawia czysto, bez
    # stash i bez reset. Zwykłego `git merge` nie ma — przy odmowie strategia ort sama robi reset --hard i stash apply,
    # co przy programach piszących równolegle gubi pracę w toku. Commit scalający powstaje więc poza katalogiem roboczym
    # (`merge-tree` → `commit-tree`), a gałąź przechodzi na niego przewinięciem.
    cel = gora
    if przod:
        kod, out, err = git(["commit-tree", drzewo, "-p", head, "-p", gora, "-m", OPIS_SCALENIA], repo, timeout=60)
        cel = out.strip()
        if kod != 0 or not cel:
            _ustaw(st, "blad", "Nie udało się przygotować commita scalającego: %s" % (_czysty(err, 200) or kod),
                   krotko="błąd gita", co_zrobic="Poproś agenta, żeby pobrał zmiany ręcznie (git pull bez rebase).")
            return "blad", {}
    if _rev(repo, "HEAD") != head:                             # w tym czasie powstał commit — następnym razem
        _ustaw(st, "czeka", "W trakcie pobierania na tym komputerze powstał nowy commit — panel spróbuje w następnym "
                            "obiegu.", krotko="nowy commit w trakcie", co_zrobic="Nic — panel ruszy sam.")
        return "czeka", {}
    przed = _migawka(repo)
    _ustaw(st, "pobieram", ("Scalam %s z GitHuba z commitami z tego komputera." if przod else
                            "Pobieram %s z GitHuba (przewinięcie).") % nazwy, krotko=None)
    kod, out, err = git(["merge", "--ff-only", "--no-autostash", "--no-overwrite-ignore", "--quiet", cel], repo,
                        timeout=180)
    tekst = out + "\n" + err
    if kod == 0:
        with _auto_blokada:
            st["konflikt_klucz"] = None
        _do_pobrania(st, 0)
        _sprawdz_po_scaleniu(repo, przed, zmienione)
        _zapisz_pobranie(repo, st, commity or [{"hash": gora[:12], "autor": "ktoś", "temat": "(scalenie)"}])
        rdzen.log("git-auto: pobrano %s (%s)" % (nazwy, "scalenie" if przod else "przewinięcie"))
        return "pobrano", {"ile": ile, "scalenie": bool(przod)}
    po = _migawka(repo)
    if przed[0] is None or po[0] != przed[0] or po[1] != przed[1]:
        rdzen.log("git-auto: UWAGA — po odmowie przewinięcia katalog roboczy różni się od stanu sprzed próby "
                  "(git przewinięcia nie zaczął, więc pisał w tym czasie inny program)")
    if "would be overwritten" in tekst or "untracked working tree files" in tekst or "would be removed" in tekst:
        pliki = _pliki_z_odmowy(tekst)
        if not pliki:
            rdzen.log("git-auto: odmowa pobrania, git podał: %s" % _czysty(tekst, 800))
        _ustaw_czeka_na_pliki(st, pliki or ["(lista plików w logu panelu)"], ile)
        return "czeka", {}
    if _rev(repo, "HEAD") != head or "not possible to fast-forward" in tekst.lower():
        _ustaw(st, "czeka", "W trakcie pobierania na tym komputerze powstał nowy commit — panel spróbuje w następnym "
                            "obiegu.", krotko="nowy commit w trakcie", co_zrobic="Nic — panel ruszy sam.")
        return "czeka", {}
    _ustaw(st, "blad", "Nie udało się pobrać zmian z GitHuba: %s" % (_czysty(tekst, 240) or kod), krotko="błąd gita",
           co_zrobic="Poproś agenta, żeby sprawdził repozytorium. Panel spróbuje sam — coraz rzadziej.")
    return "blad", {}


def _ustaw_czeka_na_pliki(st, pliki, ile):
    n = len(pliki)
    _ustaw(st, "czeka", "Na GitHubie są nowe zmiany (%d), ale dotyczą plików, które ktoś zmienia na tym komputerze "
                        "(zmiany jeszcze niezapisane commitem). Panel ich nie rusza." % ile,
           krotko="lokalne zmiany w %d %s" % (n, "pliku" if n == 1 else "plikach"), pliki=pliki,
           co_zrobic="Zapisz te pliki commitem (albo poproś agenta, który je zmienia) — panel scali resztę sam "
                     "w kolejnym obiegu.")


def _ustaw_czeka_na_dodane(st, pliki, ile):
    n = len(pliki)
    _ustaw(st, "czeka", "Na GitHubie są nowe zmiany (%d), ale na tym komputerze są pliki dodane do commita (git add), "
                        "a commit jeszcze nie powstał. Panel czeka, żeby nie przeszkadzać." % ile,
           krotko="pliki dodane do commita (git add) — dokończ commit", pliki=pliki,
           co_zrobic="Dokończ commit (albo poproś agenta, który dodał %s) — panel pobierze zmiany sam w kolejnym "
                     "obiegu." % ("ten plik" if n == 1 else "te pliki"))


def _zapisz_przed_pobraniem(repo, st, kolizje, lokalne, sciezki, teraz):
    """Krok 2b (pod blokadą gita i blokadą zapisu sejfu). Gdy KAŻDA kolizja to własna, niewysłana zmiana panelu —
    plik z `sciezki` zmieniony lokalnie albo plik sejfu, który zmienił panel i w którym nie ma cudzych zmian (te same
    warunki co przycisk „Wyślij”, bc/zapis.py: `do_wyslania`) — zapisuje je commitem tylko lokalnie (`_zatwierdz`, bez
    push). Cudza praca w toku, plik ignorowany na drodze albo pliki dodane do commita przez kogoś innego = nic (False).
    Zwraca True, gdy powstał commit. Wysłanie: krok S3, tą samą regułą spokoju co zapisane zmiany (`wczesny_commit`)."""
    sejf_sciezki, _, _ = sejf_do_wyslania(repo)
    sejf = {os.path.normcase(s) for s in sejf_sciezki}
    panelu, sejfu = [], []
    for p in kolizje:
        k = os.path.normcase(p)
        if k in sejf:
            sejfu.append(p)
        elif k in lokalne and _w_sciezkach(p, sciezki):
            panelu.append(p)
        else:
            return False                                       # cudza praca w toku — czekamy jak dotąd
    dodane = _dodane_do_indeksu(repo)
    if dodane is None or dodane:                               # ktoś jest w trakcie commita — nie wchodzimy mu w drogę
        return False
    with _auto_blokada:
        pierwsza = st.get("pierwsza_zmiana") or (st.get("wczesny_commit") or {}).get("pierwsza") or teraz
    try:
        commit, _, dodatki = _zatwierdz(repo, None if sejfu else _opis_danych(panelu), panelu, bool(sejfu))
    except BladHTTP as e:
        rdzen.log("git-auto: nie udało się zapisać zmian panelu przed pobraniem: %s" % e.komunikat)
        return False
    if dodatki.get("uwaga"):
        rdzen.log("git-auto: %s" % dodatki["uwaga"])
    if not commit:
        return False
    with _auto_blokada:
        st["wczesny_commit"] = {"kiedy": teraz, "pierwsza": min(pierwsza, teraz), "commit": commit}
    rdzen.log("git-auto: zmiany panelu w %d %s, które zmieniono też na GitHubie (%s), zapisane commitem %s tylko "
              "lokalnie — pobieram od razu, wysłanie po zwykłym spokoju" % (
                  len(kolizje), "pliku" if len(kolizje) == 1 else "plikach", ", ".join(kolizje[:3]), commit))
    return True


def _sprawdz_po_scaleniu(repo, przed, zmienione):
    """Pliki zmienione lokalnie przed scaleniem (a nie przez scalenie) muszą zostać co do rozmiaru i czasu zmiany."""
    _, po = _migawka(repo)
    ruszone = {os.path.normcase(p) for p in zmienione}
    inne = [p for p, s in przed[1].items() if os.path.normcase(p) not in ruszone and po.get(p) != s]
    if inne:
        rdzen.log("git-auto: po scaleniu zmieniły się też pliki spoza scalenia (inny program?): %s" % ", ".join(inne[:5]))


def _pobierz_reczne_bezpiecznie(repo):
    """Przycisk „Pobierz” przy stałej synchronizacji (woła `pobierz` pod blokadą, po sprawdzeniu cudzej operacji
    i gałęzi śledzącej): fetch + krok S2."""
    _pilnuj(repo)
    st = _st(repo)
    kod, err = _fetch_teraz(repo)
    if kod != 0:
        raise BladHTTP(502 if kod == -2 else 409, _tlumacz_blad(err, "Nie udało się sprawdzić zmian na GitHubie."),
                       wyjscie=_czysty(err, 300), ok=False)
    wynik, sz = _pobierz_bezpiecznie(repo, st, reczne=True)
    if wynik == "aktualne":
        _ustaw(st, "ok", "Wszystko zgodne z GitHubem." if not sz.get("przod") else
               "Zmiany z GitHuba są pobrane; commity z tego komputera czekają na wysłanie.",
               zgodne=not sz.get("przod"))
        return {"ok": True, "wyjscie": "Już aktualne."}
    if wynik == "pobrano":
        with _auto_blokada:
            st["do_powiadomienia"] = None                      # ręczne pobranie: bez wiadomości na Telegramie
        _ustaw(st, "ok", "Pobrano zmiany z GitHuba.", zgodne=not sz.get("scalenie"))
        return {"ok": True, "wyjscie": "Pobrano %s." % _odmiana_zmian(sz["ile"]) +
                (" Powstał commit scalający (na tym komputerze były też własne commity)." if sz.get("scalenie") else "")}
    raise BladHTTP(409, "Nie pobrano: %s %s" % (st.get("opis") or "", st.get("co_zrobic") or ""), ok=False,
                   wyjscie=", ".join(st.get("pliki") or []), stan=wynik)


# --------------------------------------------------------------------------- S3: samo wysyłanie
def _czekajace(repo, sciezki, brudne):
    """Zmiany panelu czekające na wysłanie: (lista ścieżek, czas ostatniej zmiany albo None)."""
    panelowe = [p for p in brudne if _w_sciezkach(p, sciezki)]
    sejf_sciezki, _, _ = sejf_do_wyslania(repo)
    wszystkie = list(dict.fromkeys(panelowe + list(sejf_sciezki)))
    ostatnia = None
    for p in wszystkie:
        pelna = os.path.join(repo, *p.split("/"))
        for kandydat in (pelna, os.path.dirname(pelna)):       # usunięty plik: czas zmiany folderu
            try:
                t = os.path.getmtime(kandydat)
                ostatnia = t if ostatnia is None else max(ostatnia, t)
                break
            except OSError:
                continue
    return wszystkie, ostatnia, bool(sejf_sciezki)


def _opis_danych(sciezki_zmian):
    rodzaje = []
    for p in sciezki_zmian:
        cz = p.split("/")
        if len(cz) >= 3 and cz[0] == "panel" and cz[1] == "dane":
            rodzaje.append(cz[2] if len(cz) > 3 else "pliki")
    rodzaje = list(dict.fromkeys(rodzaje))
    return ("dane panelu: " + ", ".join(rodzaje[:6])) if rodzaje else None


def _lokalne_gotowe(repo, teraz, po_s):
    """Lokalne commity (niewysłane) idą, gdy najnowszy zwykły commit ma co najmniej `po_s` s (same scalenia — od razu)."""
    kod, out, _ = git(["log", "-1", "--no-merges", "--format=%ct", "@{u}..HEAD"], repo, timeout=15)
    if kod != 0:
        return False
    if not out.strip():
        return True
    try:
        return teraz - int(out.strip()) >= po_s
    except ValueError:
        return True


def _zapisz_wyslanie(repo, st, commit, recznie=False, ile=None):
    kod, out, _ = git(["log", "-1", "--format=%h%x1f%s"], repo, timeout=10)
    cz = out.strip().split("\x1f") if kod == 0 else []
    with _auto_blokada:
        st["wyslanie"] = {"kiedy": rdzen.teraz(), "commit": (commit or (cz[0] if cz else None)),
                          "temat": _czysty(cz[1], 120) if len(cz) > 1 else None, "ile": ile, "recznie": bool(recznie)}


def _wyslij_bezpiecznie(repo, sciezki, ustaw, teraz, st):
    """Krok S3. Zwraca "nic", "czeka_na_spokoj", "wyslano", "czeka", "konflikt", "blad"."""
    brudne = _brudne(repo)
    if brudne is None:
        _ustaw(st, "blad", "Nie udało się sprawdzić plików (git status).", krotko="błąd gita",
               co_zrobic="Panel spróbuje w następnym obiegu.")
        return "blad"
    czekajace, ostatnia, z_sejfu = _czekajace(repo, sciezki, brudne)
    przod, tyl = _przod_tyl(repo)
    with _auto_blokada:
        if przod == 0:
            st["wczesny_commit"] = None                        # commit z kroku 2b już jest na GitHubie
        wczesny = st.get("wczesny_commit")
        if czekajace:
            # pierwsza czekająca zmiana liczy się od zmian zapisanych już w kroku 2b — limit 5 min się nie przesuwa
            st["pierwsza_zmiana"] = st.get("pierwsza_zmiana") or (wczesny or {}).get("pierwsza") or teraz
        else:
            st["pierwsza_zmiana"] = None
        st["czeka_na_wyslanie"] = len(czekajace)
        pierwsza = st["pierwsza_zmiana"]
    gotowe_zmiany = False
    if czekajace:
        spokoj = teraz - min(teraz, ostatnia if ostatnia is not None else pierwsza)
        gotowe_zmiany = spokoj >= ustaw["wyslij_po_s"] or teraz - pierwsza >= ZBIERAJ_NAJWYZEJ_S
    gotowe_commity = przod > 0 and (_lokalne_gotowe(repo, teraz, ustaw["wyslij_po_s"]) or bool(
        wczesny and teraz - wczesny["pierwsza"] >= ZBIERAJ_NAJWYZEJ_S))
    if wczesny and czekajace and not gotowe_zmiany:
        # Commit z kroku 2b to zmiany panelu zapisane wcześniej tylko po to, żeby pobrać — idzie razem z resztą
        # zmian panelu, gdy te będą gotowe (spokój albo 5 min od pierwszej), nie wcześniej.
        gotowe_commity = False
    if tyl or (not gotowe_zmiany and not gotowe_commity):
        if czekajace or przod:
            n = len(czekajace)
            _ustaw(st, "ok", ("%d %s z panelu pójdzie na GitHuba za chwilę." % (n, "zmiana" if n == 1 else "zmiany")
                              if n else "Commity z tego komputera pójdą na GitHuba za chwilę."),
                   krotko="zmiany pójdą za chwilę")
            return "czeka_na_spokoj"
        _ustaw(st, "ok", "Wszystko zgodne z GitHubem.", zgodne=True)
        return "nic"

    commit = None
    if gotowe_zmiany:
        _ustaw(st, "wysylam", "Zapisuję zmiany z panelu (commit).")
        try:
            with _blokada_sejfu(True):
                commit, _, dodatki = _zatwierdz(repo, None if z_sejfu else _opis_danych(czekajace), sciezki, True)
            if dodatki.get("uwaga"):
                rdzen.log("git-auto: %s" % dodatki["uwaga"])
        except BladHTTP as e:
            if "Trwa zapis do sejfu" in e.komunikat:          # zapis z panelu w toku — następny obieg
                _ustaw(st, "ok", "Zapis z panelu w toku — wyślę w następnym obiegu.", krotko="zmiany pójdą za chwilę")
                return "czeka_na_spokoj"
            _ustaw(st, "blad", "Nie udało się zapisać zmian z panelu: %s" % e.komunikat, krotko="błąd commita",
                   co_zrobic="Poproś agenta na komputerze z panelem, żeby sprawdził commit danych panelu.")
            _porazka(st, "inny", teraz, ustaw["co_s"])
            return "blad"
        with _auto_blokada:
            st["pierwsza_zmiana"] = None
            st["czeka_na_wyslanie"] = 0
    return _wypchnij_auto(repo, ustaw, teraz, st, commit, ponow=True)


def _wypchnij_auto(repo, ustaw, teraz, st, commit, ponow):
    przod, _ = _przod_tyl(repo)
    if przod == 0:
        _ustaw(st, "ok", "Wszystko zgodne z GitHubem.", zgodne=True)
        return "nic"
    _ustaw(st, "wysylam", "Wysyłam %d %s na GitHuba." % (przod, "commit" if przod == 1 else "commity"))
    kod, out, err = git(["push"], repo, timeout=180)
    tekst = out + "\n" + err
    if kod == 0:
        with _auto_blokada:
            st["wczesny_commit"] = None
        _zapisz_wyslanie(repo, st, commit, ile=przod)
        _ustaw(st, "ok", "Wysłano na GitHuba.", zgodne=True)
        rdzen.log("git-auto: wysłano %d commit(ów)" % przod)
        return "wyslano"
    if _odrzucony_push(tekst) and ponow:                       # ktoś wysłał wcześniej: pobierz i jeszcze raz (raz)
        kod_f, err_f = _fetch_teraz(repo)
        if kod_f != 0:
            _blad_sieci(st, err_f, teraz, ustaw, "pobieranie po odrzuconym wysłaniu")
            return "blad"
        wynik, _ = _pobierz_bezpiecznie(repo, st, ustaw=ustaw, teraz=teraz, wczesny=False)
        if wynik not in ("aktualne", "pobrano"):
            return wynik
        return _wypchnij_auto(repo, ustaw, teraz, st, commit, ponow=False)
    if _odrzucony_push(tekst):
        _ustaw(st, "blad", "GitHub drugi raz odrzucił wysłanie (ktoś znowu wysłał zmiany w tym samym czasie).",
               krotko="odrzucone wysłanie", co_zrobic="Panel spróbuje sam w następnym obiegu.")
        _porazka(st, "inny", teraz, ustaw["co_s"])
        return "blad"
    _blad_sieci(st, tekst, teraz, ustaw, "wysyłanie")
    return "blad"


# --------------------------------------------------------------------------- jeden obieg i pętla
def obieg(repo=None, sciezki=None, ustaw=None, teraz=None, tylko_pobieranie=False):
    """Jeden obieg stałej synchronizacji (S1–S3). Nie rzuca — błąd trafia do stanu. Zwraca `stan_auto(repo)`.
    `tylko_pobieranie=True` (po lekkim sprawdzeniu między obiegami): kroki 0–2b bez wysyłania (S3) i bez publikacji
    prac — wysyłanie zostaje w zwykłym rytmie. Testy podają repo= z katalogu tymczasowego (bezpiecznik `_pilnuj`),
    `ustaw` i `teraz`."""
    repo = _repo(repo)
    _pilnuj(repo)
    ustaw = dict(ustawienia_auto(), **(ustaw or {}))
    sciezki = sciezki if sciezki is not None else sciezki_panelu()
    teraz = time.time() if teraz is None else float(teraz)
    st = _st(repo)
    with _auto_blokada:
        st["wlaczona"] = True
    if not ustaw["auto"]:
        _ustaw(st, "wylaczona", "Samo pobieranie i wysyłanie jest wyłączone w ustawieniach panelu (git.auto = false).")
        with _auto_blokada:
            st["ostatni_obieg"] = rdzen.teraz()
        return stan_auto(repo)
    if teraz < (st.get("nastepna_proba") or 0):                # odstęp po błędzie
        return stan_auto(repo)
    if not _zapis_blokada.acquire(blocking=False):             # trwa „Pobierz” albo „Wyślij” z panelu
        return stan_auto(repo)
    proba = False
    poprzedni = st.get("stan")
    przed = (st.get("stan"), st.get("krotko"), st.get("opis"))
    try:
        proba = _obieg(repo, sciezki, ustaw, teraz, st, tylko_pobieranie)
    except Exception as e:                                     # pętla nigdy nie pada
        rdzen.log("git-auto: nieoczekiwany błąd obiegu: %r" % e)
        _ustaw(st, "blad", "Nieoczekiwany błąd synchronizacji: %s" % _czysty(str(e) or e.__class__.__name__, 200),
               krotko="błąd panelu", co_zrobic="Poproś agenta, żeby zajrzał do logu panelu (panel.log).")
        _porazka(st, "inny", teraz, ustaw["co_s"])
        proba = True
    finally:
        _uniewaznij(repo)
        _zapis_blokada.release()
    if st.get("stan") in ("pobieram", "wysylam"):              # nie powinno zostać — na wszelki wypadek
        _ustaw(st, poprzedni if poprzedni not in ("pobieram", "wysylam", None) else "ok", "Obieg zakończony.")
    _zapisz_zmiane_stanu(st, przed)
    if not tylko_pobieranie:                                   # publikacja prac tylko w zwykłym rytmie
        _prace_po_obiegu(repo, ustaw)
    if proba:
        _po_obiegu(repo, st, ustaw)
    return stan_auto(repo)


def _zapisz_zmiane_stanu(st, przed):
    """Przejście do „czeka” / problemu (albo między nimi) — jeden wpis w logu. Dotąd log milczał, gdy pobieranie stało
    (16.11: 10 minut bez śladu)."""
    with _auto_blokada:
        po = (st.get("stan"), st.get("krotko"), st.get("opis"))
        pliki = list(st.get("pliki") or [])[:3]
    if po[0] in ("czeka",) + STANY_PROBLEMU and po != przed:
        rdzen.log("git-auto: stan „%s”%s — %s%s" % (po[0], (" (%s)" % po[1]) if po[1] else "", _czysty(po[2], 200),
                                                    (" Pliki: " + ", ".join(pliki)) if pliki else ""))
    elif przed[0] in ("czeka",) + STANY_PROBLEMU and po[0] not in ("czeka",) + STANY_PROBLEMU:
        rdzen.log("git-auto: stan „%s” — %s" % (po[0], _czysty(po[2], 200)))


def _obieg(repo, sciezki, ustaw, teraz, st, tylko_pobieranie=False):
    """Zwraca True, gdy obieg naprawdę próbował (do liczenia obiegów incydentu), False — gdy pominięty."""
    with _auto_blokada:
        st["ostatni_obieg"] = rdzen.teraz()
    cudza = _cudza_operacja(repo)                              # przed _upstream: w trakcie rebase HEAD jest odłączony
    if cudza == "index_lock":
        with _auto_blokada:
            st["pominiete"] = st.get("pominiete", 0) + 1
            dlugo = st["pominiete"] >= POMINIEC_DO_UWAGI
        if dlugo:
            _ustaw(st, "czeka", "Od dłuższego czasu leży plik .git/index.lock (ktoś commituje albo git przerwał "
                                "pracę) — panel czeka.", krotko="blokada gita",
                   co_zrobic="Jeśli żaden program nie używa teraz gita, poproś agenta o usunięcie .git/index.lock.")
        return False
    with _auto_blokada:
        st["pominiete"] = 0
    if cudza == "brak_repo":
        _ustaw(st, "wylaczona", "Git nie widzi tu repozytorium — nie ma skąd pobierać ani dokąd wysyłać.")
        return False
    if cudza:
        _ustaw(st, "czeka", "W repozytorium trwa scalanie albo rebase (terminal, agent) — panel czeka, aż się skończy.",
               krotko="trwa scalanie w repozytorium",
               co_zrobic="Dokończ albo przerwij scalanie w terminalu (albo poproś agenta). Panel ruszy sam.")
        return True
    if not _upstream(repo):
        _ustaw(st, "wylaczona", "Ta gałąź nie jest połączona z GitHubem (brak gałęzi śledzącej) — nie ma skąd pobierać "
                                "ani dokąd wysyłać.")
        return False
    kod, err = _fetch_teraz(repo)
    if kod != 0:
        _blad_sieci(st, err, teraz, ustaw, "sprawdzanie GitHuba")
        return True
    with _auto_blokada:
        st["bledy_z_rzedu"] = 0
        st["nastepna_proba"] = 0.0
    _prace_innych(repo, ustaw)
    wynik, sz = _pobierz_bezpiecznie(repo, st, sciezki=sciezki, ustaw=ustaw, teraz=teraz)
    head = _rev(repo, "HEAD")
    with _auto_blokada:
        st["head_po_obiegu"] = head                             # lekkie sprawdzenie: czy ktoś potem zrobił commit
    if wynik in ("czeka", "konflikt", "blad"):
        return True
    if tylko_pobieranie:                                       # wysyłanie zostaje w zwykłym rytmie obiegów
        if wynik == "pobrano":
            p = st.get("pobranie") or {}
            _ustaw(st, "ok", "Pobrano z GitHuba %s." % _odmiana_zmian(p.get("ile") or 0),
                   zgodne=not sz.get("scalenie") and not st.get("czeka_na_wyslanie"))
        elif st.get("stan") in ("czeka", "konflikt"):          # ktoś pobrał albo scalił sam — stan sprzed obiegu nieaktualny
            _ustaw(st, "ok", "Zmiany z GitHuba są pobrane.")
        return True
    _wyslij_bezpiecznie(repo, sciezki, ustaw, teraz, st)
    if wynik == "pobrano" and st.get("stan") == "ok" and st.get("opis") == "Wszystko zgodne z GitHubem.":
        p = st.get("pobranie") or {}
        _ustaw(st, "ok", "Pobrano z GitHuba %s." % _odmiana_zmian(p.get("ile") or 0), zgodne=True)
    return True


def _prace_innych(repo, ustaw):
    """Prace w toku obu osób (bc/prace_wymiana.py) po udanym fetch i PRZED pobraniem zmian, pod blokadą gita: tylko
    odczyt — pliki z nadchodzących commitów a moja praca (nic podczas cudzego scalania — ten krok jest po sprawdzeniu
    `_cudza_operacja`). Żaden błąd nie zatrzymuje synchronizacji."""
    try:
        from . import prace_wymiana
        prace_wymiana.po_fetchu(repo, ustaw)
    except Exception as e:                                     # noqa: BLE001
        rdzen.log("git-auto: prace innych osób: %r" % e)


def _prace_po_obiegu(repo, ustaw):
    """Druga część (po zwolnieniu blokady gita, żeby push stanu i Telegram nie wstrzymywały przycisków Pobierz/Wyślij):
    odczyt stanu innych z gałęzi stan/prace-*, publikacja własnego, gdy się zmienił, i wiadomość o nowej kolizji.
    Działa tylko, gdy w tym obiegu był `_prace_innych`."""
    try:
        from . import prace_wymiana
        prace_wymiana.po_obiegu(repo, ustaw)
    except Exception as e:                                     # noqa: BLE001
        rdzen.log("git-auto: prace innych osób (po obiegu): %r" % e)


def _odmiana_zmian(n):
    return "%d %s" % (n, "zmianę" if n == 1 else ("zmiany" if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14
                                                  else "zmian"))


def tekst_pobrania(commity):
    """Wiadomość o cudzych commitach (zwykły tekst — autorzy i tematy to treść od ludzi)."""
    autorzy = list(dict.fromkeys(c["autor"] for c in commity))
    tematy = ["„%s”" % _czysty(c["temat"], 90) for c in commity[:3]]
    reszta = len(commity) - len(tematy)
    return "Panel pobrał z GitHuba %s (%s): %s%s." % (_odmiana_zmian(len(commity)), ", ".join(autorzy[:3]),
                                                      "; ".join(tematy), (" i %d więcej" % reszta) if reszta > 0 else "")


def _tekst_incydentu(st):
    nazwy = {"konflikt": "Synchronizacja z GitHubem stoi — konflikt, potrzebny człowiek.",
             "brak_logowania": "Synchronizacja z GitHubem stoi — GitHub nie przyjmuje logowania.",
             "blad": "Synchronizacja z GitHubem nie działa."}
    linie = [nazwy.get(st.get("stan"), "Synchronizacja z GitHubem nie działa."), _czysty(st.get("opis"), 300)]
    if st.get("pliki"):
        linie.append("Pliki: " + ", ".join(st["pliki"][:5]))
    if st.get("co_zrobic"):
        linie.append("Co zrobić: " + _czysty(st["co_zrobic"], 300))
    return "\n".join(l for l in linie if l)


def _telegram(tekst):
    try:
        from . import telegram
        return telegram.wyslij_do_zespolu(tekst)
    except Exception as e:                                     # brak modułu albo błąd bota: synchronizacja działa dalej
        rdzen.log("git-auto: wiadomość na Telegram nie poszła (%s)" % e.__class__.__name__)
        return 0


def _po_obiegu(repo, st, ustaw):
    """Licznik obiegów incydentu i wiadomości na Telegram (poza blokadą gita)."""
    wiadomosci = []
    with _auto_blokada:
        obce = st.get("do_powiadomienia")
        st["do_powiadomienia"] = None
        if obce:
            wiadomosci.append(tekst_pobrania(obce))
        if st.get("stan") in STANY_PROBLEMU:
            st["obiegi_problemu"] = st.get("obiegi_problemu", 0) + 1
            if st["obiegi_problemu"] > 2 and not st.get("incydent"):
                st["incydent"] = st["stan"]
                wiadomosci.append(_tekst_incydentu(st))
        else:
            st["obiegi_problemu"] = 0
            if st.get("incydent") and st.get("stan") == "ok":
                st["incydent"] = None
                wiadomosci.append("Synchronizacja z GitHubem znów działa.")
    if ustaw.get("telegram"):
        for w in wiadomosci:
            _telegram(w)


def _zdalna_galaz(repo, st):
    """(nazwa zdalnego, gałąź na zdalnym) gałęzi śledzącej, np. ("origin", "refs/heads/main") — do `git ls-remote`.
    Pamiętane `ZDALNA_PAMIEC_S` s (zmiana gałęzi też unieważnia). None, gdy gałąź nie śledzi niczego."""
    kod, out, _ = git(["rev-parse", "--symbolic-full-name", "HEAD"], repo, timeout=10)
    ref = out.strip() if kod == 0 else ""
    if not ref.startswith("refs/heads/"):
        return None
    with _auto_blokada:
        z = st.get("zdalna")
    if z and z["ref"] == ref and time.time() - z["kiedy"] < ZDALNA_PAMIEC_S:
        return z["zdalne"], z["galaz"]
    kod, out, _ = git(["for-each-ref", "--format=%(upstream:remotename)%09%(upstream:remoteref)", ref], repo,
                      timeout=10)
    cz = out.strip().split("\t") if kod == 0 else []
    if len(cz) != 2 or not cz[0] or cz[0].startswith("-") or not cz[1].startswith("refs/"):
        return None
    with _auto_blokada:
        st["zdalna"] = {"ref": ref, "zdalne": cz[0], "galaz": cz[1], "kiedy": time.time()}
    return cz[0], cz[1]


def sprawdz_lekko(repo=None, teraz=None):
    """Lekkie sprawdzenie między obiegami (pętla, co `git.auto_sprawdz_co_s` s): bez fetch, bez `git status`, bez
    blokady i bez zapisu w .git. True, gdy warto od razu zrobić samo pobieranie — gałąź na GitHubie wskazuje inny
    commit niż ostatnio pobrany (`git ls-remote`), albo pobieranie czeka (kolizja, `git add`, konflikt), a od obiegu
    na tym komputerze powstał commit (HEAD). Błąd sieci = False: opisze go zwykły obieg (z rosnącym odstępem)."""
    repo = _repo(repo)
    _pilnuj(repo)
    st = _st(repo)
    teraz = time.time() if teraz is None else float(teraz)
    with _auto_blokada:
        if teraz < (st.get("nastepna_proba") or 0) or st.get("stan") == "wylaczona" or not st.get("ostatni_obieg"):
            return False
        czeka = st.get("stan") in ("czeka", "konflikt") and bool(st.get("do_pobrania"))
        head_po = st.get("head_po_obiegu")
    if _cudza_operacja(repo):
        return False
    if czeka:
        head = _rev(repo, "HEAD")
        if head and head_po and head != head_po:
            return True
    zd = _zdalna_galaz(repo, st)
    if not zd:
        return False
    kod, out, _ = git(["ls-remote", zd[0], zd[1]], repo, timeout=30)
    if kod != 0:
        return False
    zdalny = next((l.split("\t")[0].strip() for l in out.splitlines()
                   if "\t" in l and l.split("\t", 1)[1].strip() == zd[1]), None)
    return bool(zdalny) and zdalny != _rev(repo, "@{u}")


def _petla_watek(repo, stop):
    if stop.wait(START_PO_S):
        return
    while not stop.is_set():
        try:
            obieg(repo)
        except Exception as e:                                 # obieg sam łapie błędy; to tylko ostatnia siatka
            rdzen.log("git-auto: błąd pętli: %r" % e)
        try:
            u = ustawienia_auto()
            co_s, sprawdz_s = u["co_s"], u["sprawdz_co_s"]
        except Exception:
            co_s, sprawdz_s = 90.0, 0.0
        # do następnego zwykłego obiegu: lekkie sprawdzenie co `sprawdz_s` s; nowy commit = samo pobieranie od razu
        # (zwykły rytm — i wysyłanie — się nie przesuwa)
        nastepny = time.monotonic() + co_s
        while not stop.is_set():
            zostalo = nastepny - time.monotonic()
            if zostalo <= 0:
                break
            if stop.wait(min(zostalo, sprawdz_s) if sprawdz_s > 0 else zostalo):
                return
            if sprawdz_s <= 0 or nastepny - time.monotonic() < 5:   # zwykły obieg za chwilę i tak
                continue
            try:
                if sprawdz_lekko(repo):
                    obieg(repo, tylko_pobieranie=True)
            except Exception as e:
                rdzen.log("git-auto: błąd lekkiego sprawdzenia: %r" % e)


def uruchom_w_tle():
    """Woła serwer.py, gdy panel naprawdę obsługuje żądania. Pętla startuje tylko, gdy nic jej nie wyłącza
    (`powod_wylaczenia`) i gałąź ma gałąź śledzącą na GitHubie."""
    repo = _repo(None)
    st = _st(repo)
    powod = powod_wylaczenia()
    # w trakcie cudzego rebase HEAD jest odłączony (brak @{u}) — pętla i tak rusza, a obieg poczeka na koniec rebase
    if not powod and not _upstream(repo) and _cudza_operacja(repo) != "scalanie":
        powod ="Ta gałąź nie jest połączona z GitHubem (brak gałęzi śledzącej) — samo pobieranie i wysyłanie nie rusza."
    if powod:
        _ustaw(st, "wylaczona", powod)
        with _auto_blokada:
            st["wlaczona"] = False
        rdzen.log("git-auto: " + powod)
        return
    if petla_dziala(repo):
        return
    _pilnuj(repo)
    stop = threading.Event()
    w = threading.Thread(target=_petla_watek, args=(repo, stop), name="git-auto", daemon=True)
    _petla.update(watek=w, stop=stop, repo=repo)
    w.start()
    u = ustawienia_auto()
    rdzen.log("git-auto: stała synchronizacja włączona (co %d s, wysyłanie po %d s spokoju, %s)" % (
        u["co_s"], u["wyslij_po_s"], ("lekkie sprawdzenie GitHuba co %d s" % u["sprawdz_co_s"]) if u["sprawdz_co_s"]
        else "bez lekkiego sprawdzania"))


def zatrzymaj_w_tle(czekaj_s=20.0):
    """Zamykanie panelu: koniec pętli; czeka na trwające polecenie gita najwyżej `czekaj_s` s."""
    stop, w = _petla.get("stop"), _petla.get("watek")
    if stop:
        stop.set()
    if w and w.is_alive() and w is not threading.current_thread():
        w.join(czekaj_s)
