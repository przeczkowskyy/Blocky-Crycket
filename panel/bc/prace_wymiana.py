# -*- coding: utf-8 -*-
"""Prace w toku obu osób: wymiana stanu przez gita i wykrywanie prac, które się nakładają.

Po co: Karol i Paweł pracują nad tą samą grą z dwóch komputerów (każdy ze swoimi agentami). Prace w toku
(bc/prace.py) leżą w danych lokalnych komputera, więc bez wymiany widać tylko własne. Ten moduł:

0. WŁĄCZNIK — wymiana przez GitHuba jest DOMYŚLNIE WYŁĄCZONA. Włącza ją właściciel: `"prace": {"wymiana": true}`
   w panel/konfiguracja.json (wspólna, w repozytorium — po `git pull` działa na obu komputerach); konfiguracja
   lokalna tego komputera może ją wyłączyć (`"prace": {"wymiana": false}`), a BC_PRACE_WYMIANA=1/0 wymusza stan
   (testy, awaria). Wyłączona = jak BC_PRACE_BEZ_SIECI=1: prace, obszary i kolizje działają lokalnie, nic nie idzie
   na GitHuba.
1. KTO — osoba tego komputera: slug z imienia tak, jak panel rozpoznaje osoby przy podpisach (bc/sejf.py:
   `kanoniczne` — pierwsze słowo, małe litery, bez polskich znaków; „Karol Balucki” → „karol”) i nazwa do pokazania
   (osoba z zespołu: „Karol”, „Paweł”; inaczej sam slug). Imię: BC_PRACE_OSOBA, inaczej `git config bc.osoba`
   (lokalnie w klonie — gdy `user.name` to login, a nie imię), inaczej `git config user.name`. Nigdy e-mail.
2. PUBLIKACJA — aktywne prace (w_toku i wstrzymane) jako jeden mały plik `prace.json` na WŁASNEJ gałęzi
   `stan/prace-<slug>` na origin. Wyłącznie polecenia „plumbing”: hash-object -w, mktree, commit-tree (rodzic =
   poprzedni czubek tej gałęzi), update-ref prywatnego refa `refs/bc/prace/publikacja` i push tego jednego refa.
   Nigdy katalog roboczy, indeks, HEAD, main ani inne gałęzie; nigdy --force; nigdy okno logowania
   (GIT_TERMINAL_PROMPT=0, GCM_INTERACTIVE=never); każde polecenie gita najwyżej LIMIT_GITA_S s.
   Ta sama osoba na dwóch komputerach: każda praca ma pole `komputer` (losowy identyfikator klonu, nie nazwa
   komputera) i publikacja ZOSTAWIA na gałęzi aktualne prace innych komputerów tej osoby (scala listy z czubka
   gałęzi). Push odrzucony, bo gałąź poszła dalej = fetch tej gałęzi i jeszcze raz (raz), na jej czubku, po scaleniu.
   Porównanie z czubkiem gałęzi: bez zmian = bez commita (co BICIE_S jeden commit odświeża datę stanu); zmiana samego
   tytułu, etapu albo „kto” — najwyżej raz na ODSTEP_DROBNYCH_S (start, koniec, stan, obszary i szacowany koniec idą
   od razu). Każdy problem (sieć, logowanie, limit czasu) to tylko krótka uwaga — praca i tak jest zapisana lokalnie.
   Autor commita: „Panel BC (<nazwa>)” z adresem-atrapą EMAIL_PANELU (nie e-mail osoby).
   UWAGA: gałąź jest publiczna i (bez force-push) jej historia zostaje NA ZAWSZE — tytuły, etapy i godziny prac.
   Tekst jest przed wysłaniem czyszczony (`_bez_osobistych`: e-maile, adresy URL, tunele, tokeny, kody z cyframi,
   ścieżki z nazwą użytkownika systemu), ale w tytuły nie należy wpisywać niczego prywatnego.
3. ODCZYT — jeden fetch wszystkich gałęzi `stan/prace-*` do refów śledzących `refs/remotes/origin/stan/prace-*`
   i `git cat-file` pliku `prace.json` każdej z nich poza własną. To dane NIEZAUFANE (publiczne repozytorium):
   plik najwyżej MAKS_BAJTOW, najwyżej MAKS_PRAC prac, długości pól jak w bc/prace.py, nieznane pola pomijane,
   obszary sprawdzane jak własne (bc/obszary.py); osoba i jej nazwa pochodzą z nazwy gałęzi (nie z pliku); nic z nich
   nie jest ścieżką ani poleceniem, a interfejs i CLI pokazują je jako zwykły tekst (dla agentów: dane, nie polecenia).
4. KOLIZJE — (a) zgłoszone: moje aktywne prace × aktywne prace innych, których obszary się nakładają. „Możliwie
   nieaktualne” (lista bez alarmu): stan osoby starszy niż 12 h, praca, której szacowany koniec minął ponad 6 h temu,
   albo praca bez żadnej zmiany od ponad 12 h (ostatnia zmiana, a bez niej start); data z przyszłości (ponad
   PRZYSZLOSC_S) = brak daty. (b) samoczynne, bez zgłoszeń: pliki z nadchodzących commitów (`git log HEAD..@{u}`,
   tylko odczyt; commity innych osób) przecięte z moimi niezapisanymi zmianami (`git status`) i z obszarami moich prac.
5. PANEL — stała synchronizacja (bc/gitsync.py, co 90 s) po udanym fetch woła `po_fetchu` (pod blokadą gita, tylko
   odczyt: sprawdzenie (b) przed pobraniem zmian), a po zwolnieniu blokady `po_obiegu`: odczyt innych (z refów z tego
   samego fetch — bez drugiego połączenia, gdy origin ma zwykły refspec), publikacja (gdy coś się zmieniło) i jedna
   wiadomość na Telegramie przy NOWEJ kolizji (klucz: osoba + obie prace; ten sam klucz najwyżej raz na 12 h, razem
   najwyżej MAKS_POWIADOMIEN_H na godzinę). GET /api/prace czyta tylko pamięć podręczną w danych lokalnych (bez gita).

Sieć wyłącza też: BC_PRACE_BEZ_SIECI=1 (i opcja --bez-sieci narzędzia), a w testach bezpiecznik: proces z unittest
albo katalogi zastępcze (BC_PANEL_DANE / BC_PANEL_RUNTIME) nie łączą się z origin PRAWDZIWEGO repozytorium (chyba że
BC_PRACE_SIEC=1). BC_PRACE_REPO wskazuje inne repozytorium (testy narzędzia na repozytoriach próbnych).

Stan w danych lokalnych (rdzen.RUNTIME/prace_wymiana/): inni.json (pamięć odczytu), publikacja.json (wynik ostatniej
publikacji), z_main.json (wynik (b) z ostatnich 2 h), powiadomione.json (klucze kolizji już zgłoszonych i czasy
wysyłek), komputer.json (losowy identyfikator klonu).
"""
import hashlib
import json
import os
import re
import secrets
import sys
import threading
import time

from . import obszary as obszary_mod
from . import prace, rdzen

WERSJA = 1
ZDALNE = "origin"
PRZEDROSTEK_GALEZI = "stan/prace-"
REFY_SLEDZACE = "refs/remotes/origin/stan/"
REF_PRYWATNY = "refs/bc/prace/publikacja"
REFSPEC_INNYCH = "+refs/heads/stan/prace-*:refs/remotes/origin/stan/prace-*"
PLIK = "prace.json"
EMAIL_PANELU = "panel@blocky-crycket.invalid"

LIMIT_GITA_S = 25
MAKS_BAJTOW = 64 * 1024
MAKS_PRAC = 50
MAKS_OSOB = 20
MAKS_NAZWA = 40
MAKS_DATA = 40
STAN_NIEAKTUALNY_S = 12 * 3600
PRACA_NIEAKTUALNA_S = 6 * 3600
PRACA_BEZ_ZMIAN_S = 12 * 3600
PRZYSZLOSC_S = 10 * 60
BICIE_S = 6 * 3600
ODSTEP_DROBNYCH_S = 10 * 60
PAMIEC_INNYCH_S = 60
Z_MAIN_ZYCIE_S = 2 * 3600
MAKS_Z_MAIN = 20
MAKS_POWIADOMIEN = 3                                           # w jednym obiegu
MAKS_POWIADOMIEN_H = 3                                         # w ciągu godziny
OKNO_POWIADOMIEN_S = 12 * 3600                                 # ten sam klucz kolizji najwyżej raz na tyle
PONOW_TELEGRAM_S = 15 * 60                                     # nieudana wysyłka: następna próba najwcześniej po tylu

ZMIENNA_BEZ_SIECI = "BC_PRACE_BEZ_SIECI"
ZMIENNA_SIEC = "BC_PRACE_SIEC"
ZMIENNA_REPO = "BC_PRACE_REPO"
ZMIENNA_WYMIANA = "BC_PRACE_WYMIANA"
ZMIENNA_OSOBA = "BC_PRACE_OSOBA"

RX_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,31}$")
RX_REF_INNEGO = re.compile(r"^refs/remotes/origin/stan/prace-([a-z0-9][a-z0-9-]{0,31})$")
RX_SHA = re.compile(r"^[0-9a-f]{40}([0-9a-f]{24})?$")
RX_KOMPUTER = re.compile(r"^[0-9a-f]{8}$")
RX_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
RX_GALAZ = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,99}$")
# to, co nie powinno trafić na publiczną gałąź stanu (tytuł, etap, „kto”, obszary): adresy (w tym tunel panelu),
# tokeny, kody i hasła z cyframi, ścieżki z nazwą użytkownika systemu (także względne: Users/<nazwa>/…)
RX_ADRES = re.compile(r"(?:\b[a-z][a-z0-9+.-]*://|\bwww\.)\S+"
                      r"|\b[\w.-]+\.(?:trycloudflare\.com|ngrok(?:-free)?\.(?:app|io|dev)|loca\.lt)\S*", re.I)
RX_TOKEN = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{8,}|github_pat_\w{8,}|sk-[\w-]{8,}|xox[abprs]-[\w-]{8,}"
                      r"|AKIA[0-9A-Z]{12,}|\d{6,12}:[\w-]{20,})")
RX_SEKRET = re.compile(r"\b(kod|code|hasło|haslo|password|token|klucz|secret|sekret|pin)(\s*[:=]\s*|\s+)(?=\S*\d)\S+",
                       re.I)
RX_KATALOG_OSOBY = re.compile(r"(?<![\w.-])(?:Users|Użytkownicy|home)[\\/]+[^\\/\s\"']+", re.I)

DOPELNIACZ = {"Karol": "Karola", "Paweł": "Pawła"}

_PRAWDZIWE_REPO = os.path.normcase(os.path.realpath(rdzen.REPO))
_blokada = threading.Lock()
_ja_pamiec = {}                                                # repo -> (czas, wynik, slugi)
_czeka_po_obiegu = {}                                          # repo -> True (po_fetchu był w tym obiegu)
_czeka_blokada = threading.Lock()


# --------------------------------------------------------------------------- repozytorium, sieć, git
def repo_domyslne():
    """Repozytorium wymiany: BC_PRACE_REPO (testy narzędzia) albo repozytorium panelu."""
    r = os.environ.get(ZMIENNA_REPO, "").strip()
    return os.path.normpath(r) if r else rdzen.REPO


def _repo(repo):
    return os.path.normpath(repo or repo_domyslne())


def _prawdziwe(repo):
    return os.path.normcase(os.path.realpath(repo)) == _PRAWDZIWE_REPO


def wymiana_wlaczona():
    """Czy wymiana przez GitHuba jest włączona: BC_PRACE_WYMIANA=1/0 albo `prace.wymiana` w konfiguracji panelu
    (wspólna z repozytorium + lokalna tego komputera). Domyślnie WYŁĄCZONA — włącza ją właściciel."""
    z = os.environ.get(ZMIENNA_WYMIANA, "").strip()
    if z in ("0", "1"):
        return z == "1"
    try:
        p = rdzen.konfiguracja().get("prace")
    except Exception:                                          # noqa: BLE001 — zła konfiguracja = wyłączona
        return False
    return isinstance(p, dict) and p.get("wymiana") is True


def powod_bez_sieci(repo=None, bez_sieci=False):
    """None, gdy wolno łączyć się z origin; inaczej krótki powód (opcja, zmienna środowiskowa, bezpiecznik testów,
    wyłączona wymiana)."""
    if bez_sieci:
        return "sieć wyłączona opcją --bez-sieci"
    if os.environ.get(ZMIENNA_BEZ_SIECI, "").strip() == "1":
        return "sieć wyłączona (BC_PRACE_BEZ_SIECI=1)"
    if _prawdziwe(_repo(repo)):
        if "unittest" in sys.modules:
            return "bezpiecznik testów: bez połączenia z GitHubem prawdziwego repozytorium"
        if (os.environ.get("BC_PANEL_DANE") or os.environ.get("BC_PANEL_RUNTIME")) and \
                os.environ.get(ZMIENNA_SIEC, "").strip() != "1":
            return "panel na katalogach zastępczych: bez połączenia z GitHubem"
    if not wymiana_wlaczona():
        return "wymiana prac przez GitHuba wyłączona (prace.wymiana w panel/konfiguracja.json)"
    return None


def _srodowisko(dodatkowe=None):
    from . import gitsync
    env = gitsync._srodowisko()                               # bez okien logowania, komunikaty po angielsku
    env["GCM_INTERACTIVE"] = "never"
    env["GIT_TERMINAL_PROMPT"] = "0"
    if dodatkowe:
        env.update(dodatkowe)
    return env


def _git(argumenty, repo, timeout=LIMIT_GITA_S, wejscie=None, env=None):
    """git w repozytorium z limitem czasu (najwyżej LIMIT_GITA_S s). → (kod, stdout, stderr)."""
    return rdzen.uruchom(["git", "-c", "core.quotepath=false", "-c", "color.ui=false",
                          "-c", "http.lowSpeedLimit=1000", "-c", "http.lowSpeedTime=20"] + list(argumenty),
                         cwd=repo, timeout=min(float(timeout), LIMIT_GITA_S), wejscie=wejscie, env=_srodowisko(env))


def _fetch(repo, refspecs, prune=False):
    """`git fetch` podanych refspeców z origin: bez tagów i bez zapisu FETCH_HEAD (nie zmienia go nawet w trakcie
    scalania). Starszy git bez --no-write-fetch-head = jeszcze raz bez tej opcji; „cannot lock ref” (ten sam ref
    pobiera właśnie stała synchronizacja) = jeszcze raz po sekundzie. → (kod, stdout, stderr)."""
    arg = ["fetch", "--quiet", "--no-tags", "--no-write-fetch-head"] + (["--prune"] if prune else []) + \
        [ZDALNE] + list(refspecs)
    kod, out, err = _git(arg, repo)
    if kod != 0 and "no-write-fetch-head" in (err or ""):
        arg.remove("--no-write-fetch-head")
        kod, out, err = _git(arg, repo)
    if kod != 0 and "cannot lock ref" in (err or ""):
        time.sleep(1)
        kod, out, err = _git(arg, repo)
    return kod, out, err


def _krotko(tekst, domyslnie):
    from . import gitsync
    t = gitsync._tlumacz_blad(tekst, "")
    if t:
        return t
    opis = gitsync._czysty(tekst, 160)
    return "%s: %s" % (domyslnie, opis) if opis else domyslnie


def _rev(repo, ref):
    kod, out, _ = _git(["rev-parse", "--verify", "--quiet", ref + "^{commit}"], repo, timeout=10)
    s = out.strip()
    return s if kod == 0 and RX_SHA.match(s) else None


def _ref_galezi(slug):
    return "refs/heads/" + PRZEDROSTEK_GALEZI + slug


def _ref_sledzacy(slug):
    return REFY_SLEDZACE + "prace-" + slug


def _klucz_repo(repo):
    return hashlib.sha1(os.path.normcase(os.path.realpath(repo)).encode("utf-8")).hexdigest()[:12]


# --------------------------------------------------------------------------- kto
def _bez_osobistych(t):
    """Tekst, który idzie na publiczną gałąź (albo z niej przyszedł): bez adresów e-mail i URL (także tunelu panelu),
    tokenów, kodów i haseł z cyframi oraz ścieżek z nazwą użytkownika systemu."""
    if not t:
        return t
    t = RX_EMAIL.sub("…", t)
    t = RX_ADRES.sub("…", t)
    t = RX_TOKEN.sub("…", t)
    t = RX_SEKRET.sub(lambda m: m.group(1) + m.group(2) + "…", t)
    return RX_KATALOG_OSOBY.sub("…", prace._bez_sciezek(t))


def _nazwa(t):
    if not isinstance(t, str):
        return None
    t = prace.RX_NIEWIDOCZNE.sub("", re.sub(r"[\x00-\x1f\x7f]", " ", t)).strip()
    if "@" in t:
        return None
    t = _bez_osobistych(t)[:MAKS_NAZWA].strip()
    return t or None


def _slug(imie):
    from . import sejf
    s = re.sub(r"[^a-z0-9]+", "-", sejf.kanoniczne(imie)).strip("-")[:32].strip("-")
    return s if RX_SLUG.match(s) else "osoba"


def osoba_z_imienia(imie):
    """{osoba (slug do nazwy gałęzi), nazwa (do pokazania)} z imienia („Karol Balucki” → karol, Karol)."""
    from . import sejf
    imie = str(imie or "").strip()
    if "@" in imie:                                            # imię z adresem e-mail — e-mail nie idzie dalej
        imie = " ".join(w for w in imie.split() if "@" not in w)
    slug = _slug(imie)
    nazwa = sejf.osoba_zespolu(imie, sejf.ZESPOL) or _nazwa(imie.split()[0] if imie.split() else "") or slug
    return {"osoba": slug, "nazwa": nazwa}


def nazwa_osoby(slug, podana=None):
    """Nazwa do pokazania dla sluga z nazwy gałęzi: osoba z zespołu (Karol, Paweł), inaczej sam slug. Nazwa z cudzego
    pliku (`podana`) jest pomijana — gałąź stan/prace-x nie może podpisać się jako „Paweł”."""
    from . import sejf
    for o in sejf.ZESPOL:
        if osoba_z_imienia(o)["osoba"] == slug:
            return o
    return slug


def dopelniacz(nazwa):
    """„z pracą Pawła”, „z pracą Karola”, a dla innych „z pracą osoby <nazwa>”."""
    return DOPELNIACZ.get(nazwa) or "osoby %s" % nazwa


def _ja_z_gita(repo):
    zap = _ja_pamiec.get(repo)
    if zap and time.time() - zap[0] < 300:
        return zap
    imie = os.environ.get(ZMIENNA_OSOBA, "").strip()
    if not imie:
        kod, out, _ = _git(["config", "--get", "bc.osoba"], repo, timeout=10)
        imie = out.strip() if kod == 0 else ""
    kod, out, _ = _git(["config", "user.name"], repo, timeout=10)
    z_gita = out.strip() if kod == 0 else ""
    wynik = osoba_z_imienia(imie or z_gita)
    zap = (time.time(), wynik, {wynik["osoba"], osoba_z_imienia(z_gita)["osoba"]})
    _ja_pamiec[repo] = zap
    return zap


def ja(repo=None):
    """Osoba tego komputera ({osoba, nazwa}): BC_PRACE_OSOBA, `git config bc.osoba` albo `git config user.name`
    repozytorium (pamięć 5 min)."""
    return dict(_ja_z_gita(_repo(repo))[1])


def _moje_slugi(repo):
    """Slugi, pod którymi występuje osoba tego komputera (z bc.osoba i z user.name) — własne commity w (b)."""
    return set(_ja_z_gita(_repo(repo))[2])


def _komputer(repo):
    """Losowy identyfikator tego klonu (8 znaków szesnastkowych; nie nazwa komputera ani osoby), trzymany w danych
    lokalnych. Rozróżnia prace tej samej osoby z dwóch komputerów na jednej gałęzi."""
    klucz = _klucz_repo(repo)
    d = _czytaj("komputer")
    k = d.get(klucz)
    if isinstance(k, str) and RX_KOMPUTER.match(k):
        return k
    k = secrets.token_hex(4)
    d = {x: v for x, v in d.items() if isinstance(v, str) and RX_KOMPUTER.match(v)}
    d[klucz] = k
    _zapisz("komputer", d)
    return k


# --------------------------------------------------------------------------- dane wymiany (własne i cudze)
def _data(v):
    return v if isinstance(v, str) and len(v) <= MAKS_DATA and prace._czas(v) else None


def _tekst(v, maks):
    """Pole tekstowe do wymiany: najpierw filtr publiczny na całym tekście, dopiero potem ucięcie do `maks` (ucięty
    w połowie token albo adres nie przeszedłby przez filtr)."""
    t = prace._tekst_z_pliku(v, 2000)
    t = _bez_osobistych(t)[:maks].strip() if t else None
    return t or None


def _obszary(v):
    """Obszary do wymiany: poprawne (bc/obszary.py) i bez niczego, co filtr publiczny by zmienił."""
    return [o for o in obszary_mod.lista_bez_bledow(v) if _bez_osobistych(o) == o]


def oczysc_prace(d):
    """Jedna praca do wymiany (własna przed wysłaniem albo cudza po odczycie): tylko pola z listy, z właściwymi typami
    i długościami; praca nieaktywna albo z dziwnym id = None. Nigdy nie rzuca."""
    if not isinstance(d, dict):
        return None
    pid = d.get("id")
    if not isinstance(pid, str) or not prace.RX_ID.match(pid):
        return None
    stan = d.get("stan")
    if stan not in prace.AKTYWNE:
        return None
    komp = d.get("komputer")
    w = {"id": pid, "tytul": _tekst(d.get("tytul"), prace.MAX_TYTUL) or pid, "stan": stan,
         "etap": _tekst(d.get("etap"), prace.MAX_ETAP), "start": _data(d.get("start")),
         "koniec_szacowany": _data(d.get("koniec_szacowany")), "aktualizacja": _data(d.get("aktualizacja")),
         "obszary": _obszary(d.get("obszary")), "kto": _tekst(d.get("kto"), prace.MAX_KTO),
         "komputer": komp if isinstance(komp, str) and RX_KOMPUTER.match(komp) else None}
    return {k: v for k, v in w.items() if v is not None}


def _dodaj(wynik, klucze, w):
    k = (w.get("komputer") or "", w["id"])
    if k not in klucze and len(wynik) < MAKS_PRAC:
        klucze.add(k)
        wynik.append(w)


def ladunek(prace_lista, kto, teraz=None, komputer=None, inne=None):
    """Plik prace.json tego komputera: {wersja, osoba, nazwa, aktualizacja, prace:[…]} — tylko prace aktywne.
    `komputer` = identyfikator tego klonu (każda własna praca dostaje go w polu `komputer`); `inne` = prace tej samej
    osoby z jej innych komputerów (z czubka gałęzi), które zostają na gałęzi."""
    wynik, klucze = [], set()
    for p in prace_lista or []:
        w = oczysc_prace(p)
        if w:
            w.pop("komputer", None)
            if komputer:
                w["komputer"] = komputer
            _dodaj(wynik, klucze, w)
    for p in inne or []:
        w = oczysc_prace(p)
        if w and w.get("komputer") and w["komputer"] != komputer:
            _dodaj(wynik, klucze, w)
    wynik.sort(key=lambda w: (w["id"], w.get("komputer") or ""))
    return {"wersja": WERSJA, "osoba": kto["osoba"], "nazwa": _nazwa(kto.get("nazwa")) or kto["osoba"],
            "aktualizacja": prace._iso(prace._teraz(teraz)), "prace": wynik}


def _osoba_z_danych(d, slug):
    """Stan osoby z danych (cudzy plik po sprawdzeniu wersji albo pamięć podręczna) — oczyszczony. Nigdy nie rzuca."""
    if not isinstance(d, dict) or not isinstance(slug, str) or not RX_SLUG.match(slug):
        return None
    lista = d.get("prace")
    if not isinstance(lista, list):
        return None
    wynik, klucze = [], set()
    for x in lista[:MAKS_PRAC]:
        w = oczysc_prace(x)
        if w:
            _dodaj(wynik, klucze, w)
    return {"osoba": slug, "nazwa": nazwa_osoby(slug), "aktualizacja": _data(d.get("aktualizacja")),
            "prace": wynik, "ucieto": len(lista) > MAKS_PRAC}


def czytaj_obcy(tekst, slug):
    """Treść prace.json z cudzej gałęzi (tekst albo bajty) → (stan osoby albo None, uwaga albo None)."""
    if isinstance(tekst, str):
        tekst = tekst.encode("utf-8", "replace")
    if not isinstance(tekst, (bytes, bytearray)):
        return None, "zły typ danych"
    if len(tekst) > MAKS_BAJTOW:
        return None, "plik prac za duży (%d B, najwyżej %d B)" % (len(tekst), MAKS_BAJTOW)
    try:
        d = json.loads(tekst.decode("utf-8-sig"))
    except (ValueError, RecursionError, UnicodeDecodeError):
        return None, "plik prac nie jest poprawnym JSON"
    if not isinstance(d, dict):
        return None, "plik prac nie jest obiektem JSON"
    w = d.get("wersja")
    if not isinstance(w, int) or isinstance(w, bool) or w != WERSJA:
        return None, "nieznana wersja pliku prac"
    o = _osoba_z_danych(d, slug)
    if o is None:
        return None, "plik prac bez listy prac"
    return o, None


def _plik_z_refa(repo, ref):
    """Bajty prace.json z commita `ref` — najpierw rozmiar (`cat-file -s`), dopiero potem treść. → (bajty, uwaga)."""
    kod, out_s, _ = _git(["cat-file", "-s", ref + ":" + PLIK], repo, timeout=10)
    try:
        rozmiar = int(out_s.strip()) if kod == 0 else -1
    except ValueError:
        rozmiar = -1
    if rozmiar < 0:
        return None, "brak pliku prac na gałęzi stanu"
    if rozmiar > MAKS_BAJTOW:
        return None, "plik prac za duży (%d B) — pominięty" % rozmiar
    kod, tresc, _ = _git(["cat-file", "blob", ref + ":" + PLIK], repo, timeout=10)
    if kod != 0:
        return None, "nie udało się odczytać pliku prac"
    return tresc, None


# --------------------------------------------------------------------------- pliki stanu (dane lokalne)
def _katalog():
    return os.path.join(rdzen.RUNTIME, "prace_wymiana")


def _czytaj(nazwa):
    d = rdzen.czytaj_json(os.path.join(_katalog(), nazwa + ".json"), {})
    return d if isinstance(d, dict) else {}


def _zapisz(nazwa, dane):
    try:
        rdzen.zapisz_json(os.path.join(_katalog(), nazwa + ".json"), dane)
    except OSError as e:
        rdzen.log("prace-wymiana: nie udało się zapisać stanu %s (%s)" % (nazwa, e.strerror or type(e).__name__))


# --------------------------------------------------------------------------- publikacja
def _skrot(dane):
    """Skrót listy prac (bez daty stanu i nazwy) — czy jest co wysyłać."""
    lista = sorted(dane.get("prace") or [], key=lambda w: (w["id"], w.get("komputer") or ""))
    return hashlib.sha256(json.dumps(lista, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _skrot_kolizji(dane):
    """Skrót tylko tego, od czego zależą kolizje i ich aktualność (bez tytułu, etapu, „kto” i daty zmiany)."""
    lista = sorted([w.get("komputer") or "", w["id"], w["stan"], w.get("obszary") or [], w.get("koniec_szacowany")]
                   for w in dane.get("prace") or [])
    return hashlib.sha256(json.dumps(lista, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]


def _bajty(dane):
    return (json.dumps(dane, ensure_ascii=False, indent=1) + "\n").encode("utf-8")


def _stan_galezi(repo, sha, slug):
    """Stan z czubka własnej gałęzi (mógł go zapisać drugi komputer tej osoby — sprawdzany jak cudzy) albo None."""
    if not sha:
        return None
    tresc, _ = _plik_z_refa(repo, sha)
    if tresc is None:
        return None
    o, _ = czytaj_obcy(tresc, slug)
    return o


def _zostaja(tam, komputer, t):
    """Prace z czubka gałęzi z INNYCH komputerów tej osoby, które nadal są aktualne (zostają po publikacji)."""
    if not tam:
        return []
    return [p for p in tam["prace"] if p.get("komputer") and p["komputer"] != komputer and not nieaktualna_praca(p, t)]


def _zbuduj_commit(repo, bajty, rodzic, kto, ile):
    kod, out, err = _git(["hash-object", "-w", "--stdin"], repo, wejscie=bajty)
    blob = out.strip()
    if kod != 0 or not RX_SHA.match(blob):
        return None, _krotko(err, "nie udało się zapisać pliku prac w gicie")
    kod, out, err = _git(["mktree"], repo, wejscie=("100644 blob %s\t%s\n" % (blob, PLIK)).encode("utf-8"))
    drzewo = out.strip()
    if kod != 0 or not RX_SHA.match(drzewo):
        return None, _krotko(err, "nie udało się zbudować drzewa")
    podpis = "Panel BC (%s)" % kto["nazwa"]
    env = {"GIT_AUTHOR_NAME": podpis, "GIT_AUTHOR_EMAIL": EMAIL_PANELU, "GIT_COMMITTER_NAME": podpis,
           "GIT_COMMITTER_EMAIL": EMAIL_PANELU}
    arg = ["commit-tree", drzewo] + (["-p", rodzic] if rodzic else []) + \
        ["-m", "prace w toku: %s (%d)" % (kto["nazwa"], ile)]
    kod, out, err = _git(arg, repo, env=env)
    commit = out.strip()
    if kod != 0 or not RX_SHA.match(commit):
        return None, _krotko(err, "nie udało się zbudować commita")
    kod, _, err = _git(["update-ref", "-m", "prace w toku: publikacja", REF_PRYWATNY, commit], repo, timeout=10)
    if kod != 0:
        return None, _krotko(err, "nie udało się zapisać prywatnego refa")
    return commit, None


def _push(repo, commit, slug):
    # bez --force i bez „+”; haki pre-push repozytorium działają jak przy każdym pushu (świadomie — README)
    kod, out, err = _git(["push", "--porcelain", "--no-progress", ZDALNE, "%s:%s" % (commit, _ref_galezi(slug))], repo)
    return kod, out + "\n" + err


def publikuj(repo=None, prace_lista=None, kto=None, teraz=None, wymus=False, bez_sieci=False):
    """Wysyła aktywne prace tego komputera na gałąź stan/prace-<slug>. Nigdy nie rzuca.
    → {wynik: "wyslano" | "bez_zmian" | "odlozone" | "nic" | "wylaczone" | "blad", uwaga?, commit?}
    „nic” = brak aktywnych prac i nic wcześniej nie wysłano (gałąź nie powstaje bez potrzeby); „odlozone” = zmienił
    się tylko tytuł, etap albo „kto”, a ostatnia publikacja była przed chwilą (pójdzie przy kolejnej zmianie albo
    w obiegu panelu)."""
    repo = _repo(repo)
    try:
        powod = powod_bez_sieci(repo, bez_sieci)
        if powod:
            return {"wynik": "wylaczone", "uwaga": powod}
        with _blokada:
            return _publikuj(repo, prace_lista, kto, teraz, wymus)
    except Exception as e:                                     # publikacja nigdy nie psuje zapisu pracy
        rdzen.log("prace-wymiana: błąd publikacji: %r" % e)
        return {"wynik": "blad", "uwaga": "nieoczekiwany błąd publikacji (%s)" % type(e).__name__}


def _publikuj(repo, prace_lista, kto, teraz, wymus):
    kto = kto or ja(repo)
    slug = kto["osoba"]
    t = prace._teraz(teraz)
    if prace_lista is None:
        prace_lista = prace.aktywne(teraz)
    komputer = _komputer(repo)
    sledzacy, prywatny = _rev(repo, _ref_sledzacy(slug)), _rev(repo, REF_PRYWATNY)
    tam = _stan_galezi(repo, sledzacy, slug)                   # to, co (według ostatniego fetch) jest na GitHubie
    dane = ladunek(prace_lista, kto, t, komputer, _zostaja(tam, komputer, t))
    if not dane["prace"] and not sledzacy and not prywatny:
        return {"wynik": "nic"}
    if not wymus and tam is not None:
        wiek = _sekundy_od_przeszlej(tam.get("aktualizacja"), t)
        if _skrot(dane) == _skrot(tam) and (not dane["prace"] or (wiek is not None and wiek < BICIE_S)):
            return {"wynik": "bez_zmian"}
        if dane["prace"] and _skrot_kolizji(dane) == _skrot_kolizji(tam) and wiek is not None and \
                wiek < ODSTEP_DROBNYCH_S:
            return {"wynik": "odlozone", "uwaga": "zmiana samego tytułu albo etapu — na GitHuba najwyżej raz na "
                                                  "%d min" % (ODSTEP_DROBNYCH_S // 60)}
    commit, blad = _zbuduj_commit(repo, _bajty(dane), sledzacy or prywatny, kto, len(dane["prace"]))
    kod, tekst = (1, "") if blad else _push(repo, commit, slug)
    from . import gitsync
    if not blad and kod != 0 and gitsync._odrzucony_push(tekst):
        # gałąź na GitHubie poszła dalej (ta sama osoba na drugim komputerze): pobrać ją, scalić listy, jeszcze raz
        kod_f, _, err_f = _fetch(repo, ["+%s:%s" % (_ref_galezi(slug), _ref_sledzacy(slug))])
        if kod_f == 0:
            sledzacy = _rev(repo, _ref_sledzacy(slug))
            tam = _stan_galezi(repo, sledzacy, slug)
            dane = ladunek(prace_lista, kto, t, komputer, _zostaja(tam, komputer, t))
            commit, blad = _zbuduj_commit(repo, _bajty(dane), sledzacy, kto, len(dane["prace"]))
            kod, tekst = (1, "") if blad else _push(repo, commit, slug)
        else:
            blad = _krotko(err_f, "nie udało się pobrać gałęzi stanu po odrzuconym wysłaniu")
    stany = _czytaj("publikacja")
    klucz = _klucz_repo(repo) + ":" + slug
    if not blad and kod == 0:
        if _rev(repo, _ref_sledzacy(slug)) != commit:
            _git(["update-ref", _ref_sledzacy(slug), commit], repo, timeout=10)
        stany[klucz] = {"ts": time.time(), "kiedy": rdzen.teraz(), "ok": True, "prac": len(dane["prace"])}
        _zapisz("publikacja", stany)
        return {"wynik": "wyslano", "commit": commit[:12]}
    if not blad:
        blad = ("GitHub odrzucił wysłanie stanu prac" if gitsync._odrzucony_push(tekst)
                else _krotko(tekst, "nie udało się wysłać stanu prac"))
    stany[klucz] = {"ts": time.time(), "kiedy": rdzen.teraz(), "ok": False, "blad": blad[:200]}
    _zapisz("publikacja", stany)
    return {"wynik": "blad", "uwaga": blad}


# --------------------------------------------------------------------------- odczyt innych
def _galaz_sledzaca(repo):
    """Gałąź main na origin, którą śledzi bieżąca gałąź („main”), albo None."""
    kod, out, _ = _git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], repo, timeout=10)
    u = out.strip()
    if kod != 0 or not u.startswith(ZDALNE + "/"):
        return None
    b = u[len(ZDALNE) + 1:]
    return b if RX_GALAZ.match(b) and ".." not in b else None


def zwykly_refspec(repo):
    """Czy `git fetch` origin pobiera wszystkie gałęzie (zwykły refspec) — wtedy fetch synchronizacji przynosi też
    gałęzie stan/prace-* i drugi fetch nie jest potrzebny."""
    kod, out, _ = _git(["config", "--get-all", "remote.%s.fetch" % ZDALNE], repo, timeout=10)
    return kod == 0 and "+refs/heads/*:refs/remotes/origin/*" in [l.strip() for l in out.splitlines()]


def czytaj_refy(repo, kto):
    """Stany innych osób z refów śledzących (bez sieci). → (lista osób, uwagi)."""
    kod, out, err = _git(["for-each-ref", "--format=%(refname)", REFY_SLEDZACE], repo, timeout=10)
    if kod != 0:
        return [], [_krotko(err, "nie udało się odczytać gałęzi stanu")]
    osoby, uwagi = [], []
    for ref in out.splitlines()[:MAKS_OSOB * 3]:
        m = RX_REF_INNEGO.match(ref.strip())
        if not m or m.group(1) == kto["osoba"]:
            continue
        slug = m.group(1)
        tresc, uwaga = _plik_z_refa(repo, ref.strip())
        if tresc is None:
            uwagi.append("%s: %s" % (slug, uwaga))
            continue
        o, uwaga = czytaj_obcy(tresc, slug)
        if uwaga:
            uwagi.append("%s: %s" % (slug, uwaga))
        if o:
            osoby.append(o)
        if len(osoby) >= MAKS_OSOB:
            break
    return osoby, uwagi


def odswiez_innych(repo=None, kto=None, fetch=True, bez_sieci=False):
    """(fetch gałęzi stan/prace-* i main) + odczyt + zapis pamięci podręcznej. Nigdy nie rzuca. → pamięć (jak
    `pamiec_innych`). Uwaga w wyniku = stan innych może być nieaktualny (nie udało się go pobrać)."""
    repo = _repo(repo)
    uwagi = []
    try:
        kto = kto or ja(repo)
        if fetch:
            powod = powod_bez_sieci(repo, bez_sieci)
            if powod:
                uwagi.append(powod)
            else:
                refspecs = [REFSPEC_INNYCH]
                b = _galaz_sledzaca(repo)
                if b:
                    refspecs.append("+refs/heads/%s:refs/remotes/%s/%s" % (b, ZDALNE, b))
                kod, _, err = _fetch(repo, refspecs, prune=True)
                if kod != 0 and len(refspecs) > 1:
                    # np. gałąź śledzona skasowana na GitHubie — jej brak nie może zepsuć odczytu stanu prac
                    rdzen.log("prace-wymiana: nie udało się pobrać gałęzi %s razem ze stanem prac" % b)
                    kod, _, err = _fetch(repo, [REFSPEC_INNYCH], prune=True)
                if kod != 0:
                    uwagi.append(_krotko(err, "nie udało się pobrać stanu prac z GitHuba"))
        osoby, u = czytaj_refy(repo, kto)
        uwagi += u
    except Exception as e:                                     # noqa: BLE001 — odczyt innych nigdy nie psuje pracy
        rdzen.log("prace-wymiana: błąd odczytu innych: %r" % e)
        osoby, kto = [], kto or {"osoba": "osoba", "nazwa": "ktoś"}
        uwagi.append("nieoczekiwany błąd odczytu (%s)" % type(e).__name__)
    pamiec = {"wersja": WERSJA, "repo": _klucz_repo(repo), "ts": time.time(), "kiedy": rdzen.teraz(),
              "ja": kto, "osoby": osoby, "uwaga": "; ".join(uwagi)[:400] or None}
    _zapisz("inni", pamiec)
    return pamiec_innych(repo, pamiec)


def pamiec_innych(repo=None, dane=None):
    """Ostatni odczyt innych z danych lokalnych (bez gita), oczyszczony jeszcze raz. Brak = pusta lista."""
    repo = _repo(repo)
    d = dane if dane is not None else _czytaj("inni")
    if not isinstance(d, dict) or d.get("repo") != _klucz_repo(repo):
        return {"ts": 0.0, "kiedy": None, "osoby": [], "uwaga": None}
    osoby = []
    for o in (d.get("osoby") if isinstance(d.get("osoby"), list) else [])[:MAKS_OSOB]:
        if isinstance(o, dict):
            w = _osoba_z_danych(o, o.get("osoba"))
            if w:
                osoby.append(w)
    ts = d.get("ts") if isinstance(d.get("ts"), (int, float)) and not isinstance(d.get("ts"), bool) else 0.0
    uwaga = d.get("uwaga") if isinstance(d.get("uwaga"), str) else None
    return {"ts": ts, "kiedy": _data(d.get("kiedy")), "osoby": osoby, "uwaga": uwaga[:400] if uwaga else None}


def stan_innych(repo=None, kto=None, max_wiek_s=PAMIEC_INNYCH_S, bez_sieci=False):
    """Stan innych: pamięć, gdy świeższa niż `max_wiek_s` (0 = zawsze świeży odczyt), inaczej świeży odczyt (fetch,
    gdy wolno)."""
    p = pamiec_innych(repo)
    if max_wiek_s > 0 and p["ts"] and time.time() - p["ts"] < max_wiek_s:
        return p
    return odswiez_innych(repo, kto, fetch=True, bez_sieci=bez_sieci)


# --------------------------------------------------------------------------- kolizje
def _sekundy_od(iso, t):
    d = prace._czas(iso)
    return (t - d).total_seconds() if d else None


def _sekundy_od_przeszlej(iso, t):
    """Sekundy od daty, która już minęła (do PRZYSZLOSC_S naprzód = teraz); data z dalszej przyszłości (zły zegar,
    dziwne dane) albo brak = None."""
    s = _sekundy_od(iso, t)
    if s is None or s < -PRZYSZLOSC_S:
        return None
    return max(s, 0.0)


def nieaktualny_stan(osoba, teraz=None):
    """Stan osoby nieaktualny: brak czasu aktualizacji (albo czas z przyszłości) albo starszy niż 12 h."""
    s = _sekundy_od_przeszlej(osoba.get("aktualizacja"), prace._teraz(teraz))
    return s is None or s > STAN_NIEAKTUALNY_S


def _bez_zmian_od(p, t):
    s = _sekundy_od_przeszlej(p.get("aktualizacja"), t)
    return s if s is not None else _sekundy_od_przeszlej(p.get("start"), t)


def nieaktualna_praca(p, teraz=None):
    """Praca nieaktualna: szacowany koniec minął ponad 6 h temu albo praca nie zmieniła się od ponad 12 h (ostatnia
    zmiana, a bez niej start) — np. zapomniana praca bez --koniec."""
    t = prace._teraz(teraz)
    s = _sekundy_od(p.get("koniec_szacowany"), t)
    if s is not None and s > PRACA_NIEAKTUALNA_S:
        return True
    z = _bez_zmian_od(p, t)
    return z is not None and z > PRACA_BEZ_ZMIAN_S


def _powod_nieaktualnosci(osoba, p, t):
    s = _sekundy_od_przeszlej(osoba.get("aktualizacja"), t)
    if s is None or s > STAN_NIEAKTUALNY_S:
        return "stan osoby %s %s" % (osoba["nazwa"], "bez daty" if s is None else "sprzed %d h" % int(s // 3600))
    s = _sekundy_od(p.get("koniec_szacowany"), t)
    if s is not None and s > PRACA_NIEAKTUALNA_S:
        return "szacowany koniec minął %d h temu" % int(s // 3600)
    return "praca bez zmian od %d h" % int((_bez_zmian_od(p, t) or 0) // 3600)


def kolizje(moje, osoby, teraz=None):
    """Zgłoszone kolizje: moje aktywne prace × aktywne prace innych, których obszary się nakładają.
    → [{osoba, nazwa, moja:{id, tytul}, ich:{id, tytul, etap, stan, koniec_szacowany, kto}, wspolne:[…],
        nieaktualne, powod?}] — najpierw aktualne."""
    t = prace._teraz(teraz)
    wynik = []
    for m in moje or []:
        mo = m.get("obszary") or []
        if not mo or m.get("stan", "w_toku") not in prace.AKTYWNE:
            continue
        for o in osoby or []:
            for p in o.get("prace") or []:
                wsp = obszary_mod.wspolne(mo, p.get("obszary") or [])
                if not wsp:
                    continue
                nieakt = nieaktualny_stan(o, t) or nieaktualna_praca(p, t)
                k = {"osoba": o["osoba"], "nazwa": o["nazwa"], "moja": {"id": m.get("id"), "tytul": m.get("tytul")},
                     "ich": {x: p.get(x) for x in ("id", "tytul", "etap", "stan", "koniec_szacowany", "kto")
                             if p.get(x) is not None},
                     "wspolne": wsp[:6], "nieaktualne": nieakt}
                if nieakt:
                    k["powod"] = _powod_nieaktualnosci(o, p, t)
                wynik.append(k)
    wynik.sort(key=lambda k: k["nieaktualne"])
    return wynik


def zmiany_z_main(repo=None, kto=None, moje=None):
    """Kolizje samoczynne (tylko odczyt): pliki z nadchodzących commitów INNYCH osób (`HEAD..@{u}`) przecięte z moimi
    niezapisanymi zmianami i z obszarami moich aktywnych prac. → [{plik, autorzy:[…], niezapisane, prace:[{id,tytul}]}]"""
    repo = _repo(repo)
    kto = kto or ja(repo)
    moje_slugi = _moje_slugi(repo) | {kto["osoba"]}
    moje = [m for m in (moje or []) if m.get("stan", "w_toku") in prace.AKTYWNE]
    gora = "@{u}" if _galaz_sledzaca(repo) else "%s/main" % ZDALNE
    if not _rev(repo, gora):
        return []
    kod, out, _ = _git(["log", "--no-merges", "-n", "200", "--format=%x1e%an", "--name-only", "HEAD.." + gora], repo)
    if kod != 0:
        return []
    pliki = {}
    for wpis in out.split("\x1e")[1:]:
        linie = wpis.split("\n")
        autor = linie[0].strip()
        if osoba_z_imienia(autor)["osoba"] in moje_slugi:
            continue                                           # własne commity (np. z drugiego komputera)
        for p in linie[1:]:
            p = p.strip()
            if p:
                pliki.setdefault(p, [])
                n = osoba_z_imienia(autor)["nazwa"]
                if n not in pliki[p]:
                    pliki[p].append(n)
    if not pliki:
        return []
    from . import gitsync
    kod, out, _ = _git(["status", "--porcelain=v1", "-z", "-uall", "--no-renames"], repo)
    lokalne = {os.path.normcase(p) for _, p in gitsync._parsuj_status(out)[1]} if kod == 0 else set()
    wynik = []
    for plik, autorzy in pliki.items():
        niezapisane = os.path.normcase(plik) in lokalne
        dotyczy = [{"id": m.get("id"), "tytul": m.get("tytul")} for m in moje
                   if obszary_mod.dotyczy_pliku(m.get("obszary"), plik)]
        if niezapisane or dotyczy:
            wynik.append({"plik": gitsync._czysty(plik, 200), "autorzy": autorzy[:3], "niezapisane": niezapisane,
                          "prace": dotyczy[:3]})
        if len(wynik) >= MAKS_Z_MAIN:
            break
    return wynik


def _zapisz_z_main(repo, nowe):
    """Wynik (b) pamiętany 2 h (po pobraniu zmian `HEAD..@{u}` jest już pusty, a człowiek powinien to zobaczyć)."""
    d = _czytaj("z_main")
    stare = d.get("wpisy") if d.get("repo") == _klucz_repo(repo) and isinstance(d.get("wpisy"), list) else []
    teraz = time.time()
    po_pliku = {w["plik"]: w for w in stare if isinstance(w, dict) and isinstance(w.get("plik"), str)
                and isinstance(w.get("ts"), (int, float)) and teraz - w["ts"] < Z_MAIN_ZYCIE_S}
    for w in nowe:
        po_pliku[w["plik"]] = dict(w, ts=teraz, kiedy=rdzen.teraz())
    wpisy = sorted(po_pliku.values(), key=lambda w: -w["ts"])[:MAKS_Z_MAIN]
    _zapisz("z_main", {"repo": _klucz_repo(repo), "wpisy": wpisy})


def z_main_z_pamieci(repo=None, moje=None):
    """Wpisy (b) z ostatnich 2 h, które dalej mają znaczenie (niezapisane zmiany albo praca dalej aktywna)."""
    repo = _repo(repo)
    d = _czytaj("z_main")
    if d.get("repo") != _klucz_repo(repo) or not isinstance(d.get("wpisy"), list):
        return []
    aktywne = {m.get("id") for m in moje or [] if m.get("stan") in prace.AKTYWNE}
    teraz, wynik = time.time(), []
    for w in d["wpisy"][:MAKS_Z_MAIN]:
        if not isinstance(w, dict) or not isinstance(w.get("plik"), str) or not isinstance(w.get("ts"), (int, float)):
            continue
        if teraz - w["ts"] >= Z_MAIN_ZYCIE_S:
            continue
        prace_w = [x for x in (w.get("prace") or []) if isinstance(x, dict) and x.get("id") in aktywne]
        if not w.get("niezapisane") and not prace_w:
            continue
        wynik.append({"plik": w["plik"][:200], "autorzy": [a for a in (w.get("autorzy") or []) if isinstance(a, str)][:3],
                      "niezapisane": bool(w.get("niezapisane")), "prace": prace_w[:3], "kiedy": _data(w.get("kiedy"))})
    return wynik


# --------------------------------------------------------------------------- Telegram
def klucz_kolizji(k):
    return "%s|%s|%s" % (k["osoba"], k["moja"].get("id"), k["ich"].get("id"))


def tekst_kolizji(k, kto):
    """Wiadomość na Telegram (zwykły tekst — tytuły to treść od ludzi i agentów)."""
    from . import gitsync
    return ("Prace się nakładają: %s — „%s” i %s — „%s” (wspólne: %s). Niech jedna osoba poczeka albo się umówcie — "
            "pliki binarne (modele, mapy) nie dadzą się scalić." % (
                kto["nazwa"], gitsync._czysty(k["moja"].get("tytul"), 80), k["nazwa"],
                gitsync._czysty(k["ich"].get("tytul"), 80), gitsync._czysty(", ".join(k["wspolne"][:3]), 120)))


def powiadom(lista_kolizji, kto, wysylaj=True, teraz_s=None):
    """Jedna wiadomość na NOWĄ aktualną kolizję (klucz: osoba + obie prace), tą samą drogą co synchronizacja
    (gitsync._telegram; brak bota = nic). Ten sam klucz najwyżej raz na OKNO_POWIADOMIEN_S (także gdy kolizja na
    chwilę zniknęła), razem najwyżej MAKS_POWIADOMIEN w obiegu i MAKS_POWIADOMIEN_H na godzinę; nieudana wysyłka
    i nadmiar czekają na kolejny obieg. `wysylaj=False` (git.auto_telegram = false): kolizje zapamiętane bez
    wysyłania. → liczba wysłanych."""
    t = time.time() if teraz_s is None else float(teraz_s)
    aktualne = {klucz_kolizji(k): k for k in lista_kolizji if not k.get("nieaktualne")}
    stan = _czytaj("powiadomione")
    znane = {}
    if isinstance(stan.get("klucze"), dict):
        for kl, v in stan["klucze"].items():
            if isinstance(kl, str) and isinstance(v, dict) and isinstance(v.get("widziano"), (int, float)) and \
                    t - v["widziano"] < OKNO_POWIADOMIEN_S:
                znane[kl] = {x: v.get(x) for x in ("widziano", "wyslano", "proba", "pominieto")}
    wyslania = [x for x in stan.get("wyslania") or [] if isinstance(x, (int, float)) and 0 <= t - x < 3600]
    nowe = []
    for kl, k in aktualne.items():
        z = znane.get(kl)
        if z is None:
            nowe.append((kl, k))
            znane[kl] = {"widziano": t}
            continue
        z["widziano"] = t
        if not z.get("wyslano") and not z.get("pominieto") and \
                (not isinstance(z.get("proba"), (int, float)) or t - z["proba"] >= PONOW_TELEGRAM_S):
            nowe.append((kl, k))                               # wcześniej nie poszła (błąd bota, limit) — jeszcze raz
    wyslane = 0
    if wysylaj:
        from . import gitsync
        for kl, k in nowe:
            if wyslane >= MAKS_POWIADOMIEN or len(wyslania) >= MAKS_POWIADOMIEN_H:
                break
            if gitsync._telegram(tekst_kolizji(k, kto)):
                znane[kl].update(wyslano=t)
                wyslania.append(t)
                wyslane += 1
            else:
                znane[kl].update(proba=t)                      # brak bota albo błąd: następna próba za 15 min
                break
    else:
        for kl, _ in nowe:
            znane[kl].update(pominieto=True)                   # Telegram wyłączony: znana, bez wysyłki
    najnowsze = sorted(znane.items(), key=lambda kv: -kv[1]["widziano"])[:200]
    _zapisz("powiadomione", {"klucze": dict(najnowsze), "wyslania": wyslania[-20:]})
    return wyslane


# --------------------------------------------------------------------------- zaczep stałej synchronizacji i API
def po_fetchu(repo=None, ustaw=None):
    """Woła stała synchronizacja (gitsync._obieg) po udanym `git fetch`, POD blokadą gita i przed pobraniem zmian
    (wtedy `HEAD..@{u}` pokazuje nadchodzące pliki). Tylko odczyt i pliki w danych lokalnych; sieć i Telegram są
    w `po_obiegu` (po zwolnieniu blokady). Nigdy nie rzuca."""
    repo = _repo(repo)
    try:
        _zapisz_z_main(repo, zmiany_z_main(repo, ja(repo), prace.aktywne()))
    except Exception as e:                                     # noqa: BLE001 — synchronizacja działa dalej
        rdzen.log("prace-wymiana: błąd po fetch: %r" % e)
    with _czeka_blokada:
        _czeka_po_obiegu[repo] = True


def po_obiegu(repo=None, ustaw=None):
    """Woła stała synchronizacja (gitsync.obieg) PO zwolnieniu blokady gita, gdy w tym obiegu był `po_fetchu`:
    odczyt innych (z refów z fetch synchronizacji, a przy nietypowym refspecu — własny fetch), publikacja własnego
    stanu, gdy się zmienił, i wiadomość o nowej kolizji. Nic w trakcie cudzego scalania albo rebase. Nigdy nie rzuca."""
    repo = _repo(repo)
    with _czeka_blokada:
        if not _czeka_po_obiegu.pop(repo, False):
            return
    try:
        from . import gitsync
        if gitsync._cudza_operacja(repo) in ("scalanie", "brak_repo"):
            return
        kto = ja(repo)
        moje = prace.aktywne()
        pamiec = odswiez_innych(repo, kto, fetch=not zwykly_refspec(repo))
        publikuj(repo, moje, kto)
        telegram = (ustaw or {}).get("telegram", True) is not False
        powiadom(kolizje(moje, pamiec["osoby"]), kto, wysylaj=telegram)
    except Exception as e:                                     # noqa: BLE001 — synchronizacja działa dalej
        rdzen.log("prace-wymiana: błąd po obiegu: %r" % e)


def inni_plasko(osoby, teraz=None):
    """Prace innych jako płaska lista dla API: praca + osoba, nazwa, nieaktualna, stan_osoby (czas aktualizacji)."""
    t = prace._teraz(teraz)
    wynik = []
    for o in osoby:
        nieakt_osoby = nieaktualny_stan(o, t)
        for p in o["prace"]:
            wynik.append(dict(p, osoba=o["osoba"], nazwa=o["nazwa"], stan_osoby=o.get("aktualizacja"),
                              nieaktualna=nieakt_osoby or nieaktualna_praca(p, t)))
    return wynik


def dla_api(moje, teraz=None, repo=None):
    """Pola GET /api/prace: inni, kolizje, z_main, wymiana — z pamięci w danych lokalnych, bez gita (poza
    `git config`, pamiętanym 5 min)."""
    repo = _repo(repo)
    p = pamiec_innych(repo)
    kto = ja(repo)
    st = _czytaj("publikacja").get(_klucz_repo(repo) + ":" + kto["osoba"])
    publikacja = {"kiedy": _data(st.get("kiedy")), "ok": bool(st.get("ok"))} if isinstance(st, dict) else None
    return {"inni": inni_plasko(p["osoby"], teraz), "kolizje": kolizje(moje, p["osoby"], teraz),
            "z_main": z_main_z_pamieci(repo, moje),
            "wymiana": {"osoba": kto["osoba"], "nazwa": kto["nazwa"], "odczyt": p["kiedy"], "uwaga": p["uwaga"],
                        "publikacja": publikacja, "wlaczona": wymiana_wlaczona()}}
