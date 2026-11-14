# -*- coding: utf-8 -*-
"""Agent = Claude Code w trybie bezobsługowym (`claude -p --output-format stream-json`), na subskrypcji osoby przy
tym komputerze (nie klucz API, nie --bare — działa CLAUDE.md, skille i serwery MCP z .mcp.json).

- Wątek rozmowy: RUNTIME/agent/watki/<id>.json {id, tytul, utworzono, ostatnio, utworzyl, zdalnie, session_id,
  wiadomosci:[…]}. Kolejne wiadomości wznawiają tę samą sesję (`--resume <session_id>`).
- Kto zużywa subskrypcję: każdy przebieg idzie na subskrypcji osoby przy komputerze z panelem, także gdy pisze ktoś
  zdalnie (przez tunel). Dlatego wątek pamięta, kto go założył (`utworzyl` — imię z panelu) i czy zdalnie
  (`zdalnie`), a każda wiadomość człowieka — `kto` i `zdalnie`; lista wątków pokazuje to w zakładce Agent.
  Starsze wątki nie mają pola `zdalnie` (null = nie wiadomo).
- Przebieg: proces potomny w katalogu repozytorium; wiadomość idzie przez stdin; wyjście stream-json zamieniamy na
  zdarzenia {n, typ:"tekst"|"narzedzie"|"wiadomosc"|"blad"|"koniec", …} trzymane w pamięci (bufor przebiegu)
  i wysyłane strumieniem SSE (`?od=<n>` = wyślij zdarzenia o numerze >= n, potem nowe).
- Jeden przebieg naraz na wątek (409), najwyżej 2 przebiegi naraz w całym panelu.
- Żądania spoza komputera: 403, dopóki konfiguracja `agent.zdalnie` nie jest true; wtedy tryb `auto` → `praca`.
"""
import collections
import glob
import json
import os
import re
import shutil
import subprocess
import threading
import time

from . import rdzen
from .http import Strumien
from .rdzen import BladHTTP

TRYBY = [
    {"id": "plan", "nazwa": "Plan", "opis": "Tylko czyta i planuje — niczego nie zmienia."},
    {"id": "praca", "nazwa": "Praca", "opis": "Edytuje pliki i używa dozwolonych narzędzi; o resztę nie pyta, tylko odmawia."},
    {"id": "auto", "nazwa": "Auto", "opis": "Sam decyduje o uprawnieniach (tylko przy komputerze z panelem)."},
]
ID_TRYBOW = [t["id"] for t in TRYBY]
DOZWOLONE_NARZEDZIA = ["Read", "Glob", "Grep", "Edit", "Write", "WebSearch", "WebFetch", "mcp__Roblox_Studio",
                       "Bash(python tools/*)", "Bash(python panel/narzedzia/*)", "Bash(git status*)", "Bash(git diff*)",
                       "Bash(git log*)", "Bash(rojo build*)"]
# Zawężone zestawy narzędzi dla poleceń panelu, które czytają treść od ludzi spoza grona decydentów (zapis rozmowy
# z zakładki Sesja, wiersze agendy, odpowiedzi gości). Tryb „dontAsk”: wolno tylko to, co jest na liście; bez serwerów
# MCP, bez sieci, bez dowolnych poleceń. Notatki tylko czytają — ich treść zapisuje panel z odpowiedzi agenta.
ZESTAWY_NARZEDZI = {
    "czytanie": ["Read", "Glob", "Grep"],
    "sejf": ["Read", "Glob", "Grep", "Edit", "Write"],
    "ustalenia": ["Read", "Glob", "Grep", "Edit", "Write", "Bash(python panel/narzedzia/raport.py *)"],
}
ZAKAZANE_W_ZESTAWACH = ["Read(./.env)", "Read(./.env.*)", "Edit(./.env)", "Edit(./.claude/**)", "Edit(./CLAUDE.md)",
                        "Edit(./panel/konfiguracja.json)", "Edit(./B&C/.obsidian/**)", "Edit(./B&C/Źródła/**)"]
MAX_PRZEBIEGOW = 2
MAX_TEKST = 20000
MAX_KONTEKST = 12
MAX_WIADOMOSCI = 600                                           # starsze wiadomości wątku są przycinane
MAX_ZDARZEN = 20000                                            # bufor jednego przebiegu (potem bez przyrostów tekstu)
MAX_NARZEDZI_W_WATKU = 200                                     # wpisów „narzedzie” zapisywanych z jednego przebiegu
RX_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")
RX_MODEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._\-\[\]]{0,79}$")
# zmienne środowiska sesji Claude Code, z której ewentualnie uruchomiono panel — dziecko ma być osobną sesją;
# ANTHROPIC_API_KEY usuwamy, żeby agent zawsze szedł z subskrypcji osoby przy komputerze, a nie z klucza API
ZMIENNE_DO_USUNIECIA = ("ANTHROPIC_API_KEY", "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_SESSION_ID",
                        "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CODE_MESSAGING_SOCKET", "CLAUDE_CODE_MESSAGING_TOKEN",
                        "CLAUDE_PID", "CLAUDE_CODE_SSE_PORT", "CLAUDE_AGENT_SDK_VERSION", "CLAUDE_CODE_EXECPATH",
                        "CLAUDE_CODE_SESSION_ATTENDED", "CLAUDE_CODE_EMIT_STARTUP_TIMING",
                        "CLAUDE_CODE_STARTUP_FAILURE_RESULTS", "CLAUDE_CODE_QUESTION_PREVIEW_FORMAT", "CLAUDE_EFFORT",
                        "CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING", "CLAUDE_CODE_ENABLE_TASKS")

INSTRUKCJA = (
    "Rozmowa idzie przez Panel zespołu gry BLOCKY & CRYCKET (przeglądarka, często telefon) — człowiek nie widzi "
    "terminala ani nie odpowie na pytania o uprawnienia. Odpowiadaj krótko, po polsku, prostym językiem. "
    "Przestrzegaj CLAUDE.md i zasad sejfu B&C. Po wdrożeniu czegokolwiek w Roblox Studio lub w repozytorium "
    "opublikuj raport: python panel/narzedzia/raport.py dodaj --tytul \"…\" --opis \"…\" "
    "[--komponent studio:Workspace/Ścieżka:Etykieta] [--zrzut plik.png] — ludzie zaakceptują go albo odeślą "
    "do poprawy w panelu (ich odpowiedzi: python panel/narzedzia/raport.py odpowiedzi). "
    "Nie commituj i nie pushuj bez wyraźnej prośby."
)

_lock = threading.RLock()                                      # stan przebiegów i zapis wątków
_przebiegi = {}                                                # id wątku -> Przebieg (ostatni, także zakończony)
_licznik_n = {}                                                # id wątku -> ostatni numer zdarzenia
_program = {"t": 0.0, "sciezka": None}
_wersje = {}                                                   # ścieżka -> (czas, wersja)


# --------------------------------------------------------------------------- program `claude`
def _kandydaci():
    cfg = rdzen.konfiguracja().get("agent") or {}
    if cfg.get("sciezka"):
        yield os.path.expandvars(os.path.expanduser(str(cfg["sciezka"])))
    yield shutil.which("claude")
    dom = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    yield os.path.join(dom, ".local", "bin", "claude.exe" if os.name == "nt" else "claude")
    rozszerzenia = glob.glob(os.path.join(dom, ".vscode", "extensions", "anthropic.claude-code-*", "resources",
                                          "native-binary", "claude.exe" if os.name == "nt" else "claude"))

    def wersja(sciezka):
        m = re.search(r"anthropic\.claude-code-(\d+)\.(\d+)\.(\d+)", sciezka)
        return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)
    for s in sorted(rozszerzenia, key=wersja, reverse=True):
        yield s
    if os.environ.get("APPDATA"):
        yield os.path.join(os.environ["APPDATA"], "npm", "claude.cmd")


def znajdz_program():
    """Ścieżka do programu Claude Code albo None (pamięć 60 s)."""
    if time.time() - _program["t"] < 60:
        return _program["sciezka"]
    znaleziony = None
    for s in _kandydaci():
        if s and os.path.isfile(s):
            znaleziony = os.path.abspath(s)
            break
    _program.update(t=time.time(), sciezka=znaleziony)
    return znaleziony


def wersja_programu(sciezka):
    if not sciezka:
        return None
    z = _wersje.get(sciezka)
    if z and time.time() - z[0] < 600:
        return z[1]
    kod, out, _ = rdzen.uruchom([sciezka, "--version"], timeout=20)
    w = out.strip().split()[0] if kod == 0 and out.strip() else None
    _wersje[sciezka] = (time.time(), w)
    return w


def zdrowie():
    s = znajdz_program()
    return {"dostepny": bool(s), "sciezka": s, "wersja": wersja_programu(s), "przebiegi": _ile_trwa()}


# --------------------------------------------------------------------------- wątki (pliki)
def _kat_watkow():
    return os.path.join(rdzen.RUNTIME, "agent", "watki")


def _sciezka_watku(wid):
    if not isinstance(wid, str) or not RX_ID.match(wid):
        raise BladHTTP(400, "Niepoprawny identyfikator wątku")
    return os.path.join(_kat_watkow(), wid + ".json")


def _czytaj_watek(wid):
    w = rdzen.czytaj_json(_sciezka_watku(wid))
    if not isinstance(w, dict):
        raise BladHTTP(404, "Nie ma takiego wątku")
    w.setdefault("wiadomosci", [])
    return w


def _zapisz_watek(w):
    if len(w["wiadomosci"]) > MAX_WIADOMOSCI:
        w["wiadomosci"] = w["wiadomosci"][-MAX_WIADOMOSCI:]
    rdzen.zapisz_json(_sciezka_watku(w["id"]), w)


def _dopisz(wid, wiadomosc=None, **pola):
    """Dopisuje wiadomość (nadaje nr i czas) i/lub zmienia pola wątku. Zwraca dopisaną wiadomość."""
    with _lock:
        w = _czytaj_watek(wid)
        if wiadomosc is not None:
            nr = (w["wiadomosci"][-1]["nr"] + 1) if w["wiadomosci"] else 1
            wiadomosc = dict({"nr": nr, "czas": rdzen.teraz()}, **wiadomosc)
            w["wiadomosci"].append(wiadomosc)
            w["ostatnio"] = wiadomosc["czas"]
        w.update(pola)
        _zapisz_watek(w)
        return wiadomosc


def _wymagaj_watku(wid):
    """404, gdy wątku nie ma (400 przy niepoprawnym identyfikatorze)."""
    if not os.path.isfile(_sciezka_watku(wid)):
        raise BladHTTP(404, "Nie ma takiego wątku")


def _trwa(wid):
    p = _przebiegi.get(wid)
    return bool(p and not p.zakonczony)


def _ile_trwa():
    with _lock:
        return sum(1 for p in _przebiegi.values() if not p.zakonczony)


def _osoby_watku(w):
    """Kto pisał w wątku: [{kto, zdalnie}] bez powtórzeń, w kolejności pierwszej wiadomości (zdalnie = true, gdy
    choć jedna wiadomość tej osoby przyszła zdalnie; null, gdy stary wątek tego nie zapisał)."""
    osoby = collections.OrderedDict()
    for m in w.get("wiadomosci") or []:
        if not isinstance(m, dict) or m.get("rola") != "user":
            continue
        kto = str(m.get("kto") or "").strip() or "ktoś"
        z = m.get("zdalnie")
        if kto not in osoby:
            osoby[kto] = z
        elif z is True or (osoby[kto] is None and z is False):
            osoby[kto] = z
    return [{"kto": k, "zdalnie": v} for k, v in osoby.items()]


def _kto_zalozyl(w):
    return {"utworzyl": w.get("utworzyl") or None, "zdalnie": w.get("zdalnie") if isinstance(w.get("zdalnie"), bool) else None}


def _widok_watku(w):
    out = {"id": w["id"], "tytul": w.get("tytul") or "Rozmowa", "utworzono": w.get("utworzono"),
           "ostatnio": w.get("ostatnio"), "trwa": _trwa(w["id"]), "wiadomosci": w.get("wiadomosci") or [],
           "osoby": _osoby_watku(w)}
    out.update(_kto_zalozyl(w))
    return out


# --------------------------------------------------------------------------- przebieg
class Przebieg:
    def __init__(self, wid):
        self.wid = wid
        self.zdarzenia = []
        self.zakonczony = False
        self.przerwany = False
        self.limit_czasu = False
        self.proc = None
        self.koniec_t = 0.0
        self.cond = threading.Condition(_lock)

    def zdarzenie(self, typ, **pola):
        with self.cond:
            if typ == "tekst" and len(self.zdarzenia) >= MAX_ZDARZEN:
                return None
            n = _licznik_n.get(self.wid, 0) + 1
            _licznik_n[self.wid] = n
            e = dict({"n": n, "typ": typ}, **pola)
            self.zdarzenia.append(e)
            if typ == "koniec":
                self.zakonczony = True
                self.koniec_t = time.time()
            self.cond.notify_all()
            return e


def _skroc(tekst, ile=80):
    tekst = " ".join(str(tekst or "").split())
    return tekst if len(tekst) <= ile else tekst[:ile - 1] + "…"


def _sciezka_czytelna(s):
    s = str(s or "")
    try:
        if os.path.isabs(s):
            wzgl = os.path.relpath(s, rdzen.REPO)
            if not wzgl.startswith(".."):
                return wzgl.replace("\\", "/")
    except ValueError:
        pass
    return s.replace("\\", "/")


def opis_narzedzia(nazwa, wejscie):
    """(czytelna nazwa, krótki opis argumentów) dla zdarzenia „narzedzie”."""
    wejscie = wejscie if isinstance(wejscie, dict) else {}
    czytelna = nazwa or "narzędzie"
    if czytelna.startswith("mcp__"):
        czesci = czytelna.split("__")
        serwer = czesci[1].replace("_", " ") if len(czesci) > 1 else "MCP"
        czytelna = "%s · %s" % (serwer, "__".join(czesci[2:]).replace("_", " ") or "?")
    for klucz in ("file_path", "notebook_path", "path"):
        if wejscie.get(klucz) and klucz != "path":
            return czytelna, _skroc(_sciezka_czytelna(wejscie[klucz]), 120)
    if wejscie.get("command"):
        return czytelna, _skroc(wejscie["command"], 80)
    if wejscie.get("pattern"):
        gdzie = (" w " + _sciezka_czytelna(wejscie["path"])) if wejscie.get("path") else ""
        return czytelna, _skroc(str(wejscie["pattern"]) + gdzie, 100)
    if wejscie.get("path"):
        return czytelna, _skroc(_sciezka_czytelna(wejscie["path"]), 120)
    for klucz in ("url", "query", "description", "skill", "prompt", "code", "name"):
        if wejscie.get(klucz):
            return czytelna, _skroc(wejscie[klucz], 80)
    for v in wejscie.values():                                 # pierwszy krótki tekst z argumentów
        if isinstance(v, str) and v.strip():
            return czytelna, _skroc(v, 80)
    return czytelna, ""


def _srodowisko():
    env = dict(os.environ)
    for k in ZMIENNE_DO_USUNIECIA:
        env.pop(k, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


def _program_argv(program):
    """Program jako początek listy argumentów. Skrót npm (`claude.cmd`) zamieniamy na `node cli.js`, bo pliki .cmd
    źle znoszą znaki specjalne w argumentach (cudzysłowy w instrukcji, „&” w ścieżce projektu)."""
    if program.lower().endswith((".cmd", ".bat")):
        cli = os.path.join(os.path.dirname(program), "node_modules", "@anthropic-ai", "claude-code", "cli.js")
        node = shutil.which("node")
        if node and os.path.isfile(cli):
            return [node, cli]
    return [program]


def _katalogi_sesji(katalogi):
    """Dodatkowe katalogi do odczytu przez agenta (`--add-dir`) — wyłącznie istniejące katalogi sesji rozmów w danych
    lokalnych panelu (zapis rozmowy z zakładki Sesja). Wszystko inne jest pomijane."""
    baza = os.path.realpath(os.path.join(rdzen.RUNTIME, "sesje"))
    out = []
    for k in katalogi or []:
        if not isinstance(k, str):
            continue
        p = os.path.realpath(k)
        if p.startswith(baza + os.sep) and os.path.isdir(p) and p not in out:
            out.append(p)
    return out


def zbuduj_polecenie(program, tryb, model=None, session_id=None, katalogi=None, zestaw=None):
    """Wiersz poleceń `claude -p`. `zestaw` (klucz ZESTAWY_NARZEDZI) zastępuje uprawnienia trybu zawężoną listą
    narzędzi — tylko dla poleceń panelu (bc/sesje.py), nigdy z wyboru człowieka."""
    cfg = rdzen.konfiguracja().get("agent") or {}
    cmd = _program_argv(program) + ["-p", "--output-format", "stream-json", "--verbose", "--include-partial-messages"]
    if zestaw is not None:
        narzedzia = ZESTAWY_NARZEDZI[zestaw]
        wbudowane = []
        for n in narzedzia:
            nazwa = n.split("(")[0]
            if nazwa not in wbudowane:
                wbudowane.append(nazwa)
        cmd += ["--permission-mode", "dontAsk", "--permission-prompts", "none", "--strict-mcp-config",
                "--tools", ",".join(wbudowane), "--allowedTools"] + narzedzia + \
               ["--disallowedTools"] + ZAKAZANE_W_ZESTAWACH
    elif tryb == "plan":
        cmd += ["--permission-mode", "plan", "--permission-prompts", "none"]
    elif tryb == "auto":
        cmd += ["--permission-mode", "auto", "--permission-prompts", "none"]
    else:
        narzedzia = cfg.get("dozwolone_narzedzia")
        if not isinstance(narzedzia, list) or not narzedzia:
            narzedzia = DOZWOLONE_NARZEDZIA
        cmd += ["--permission-mode", "acceptEdits", "--permission-prompts", "none",
                "--allowedTools"] + [str(n) for n in narzedzia]
    if zestaw is None and os.path.isfile(os.path.join(rdzen.REPO, ".mcp.json")):
        cmd += ["--mcp-config", ".mcp.json"]                   # względnie: katalog roboczy procesu to repozytorium
    dodatkowe = _katalogi_sesji(katalogi)
    if dodatkowe:                                              # zapis rozmowy z zakładki Sesja (dane lokalne)
        cmd += ["--add-dir"] + dodatkowe
    cmd += ["--append-system-prompt", INSTRUKCJA]
    if session_id:
        cmd += ["--resume", session_id]
    if model:
        cmd += ["--model", model]
    return cmd


def tresc_dla_agenta(kto, tekst, kontekst=None):
    linie = ["[Panel zespołu · pisze: %s]" % kto]
    if kontekst:
        linie.append("Kontekst: " + "; ".join(
            "%s:%s%s" % (k["typ"], k["cel"], (" („%s”)" % k["etykieta"]) if k.get("etykieta") else "") for k in kontekst))
    return "\n".join(linie) + "\n\n" + tekst


def _zabij(proc):
    """Kończy nasz proces potomny razem z jego dziećmi (serwery MCP, polecenia) — i nic poza nim."""
    if proc is None or proc.poll() is not None:
        return
    if os.name == "nt":
        rdzen.uruchom(["taskkill", "/PID", str(proc.pid), "/T", "/F"], timeout=15)
    try:
        if proc.poll() is None:
            proc.kill()
    except OSError:
        pass


def _blad_czytelny(kod, stderr_linie, wynik_tekst, przerwany_limitem, limit_min):
    if przerwany_limitem:
        glowny = "Agent pracował dłużej niż limit (%d min) i został zatrzymany." % limit_min
    else:
        caly = (wynik_tekst or "") + "\n" + "\n".join(stderr_linie)
        niski = caly.lower()
        if "no conversation found" in niski:
            glowny = "Nie udało się wznowić poprzedniej rozmowy (sesja wygasła). Następna wiadomość zacznie ją od nowa."
        elif "login" in niski or "api key" in niski or "authentication" in niski or "unauthorized" in niski:
            glowny = "Claude Code na tym komputerze nie jest zalogowany. Uruchom w terminalu „claude” i wpisz /login."
        elif "rate limit" in niski or "usage limit" in niski or "limit reached" in niski:
            glowny = "Wyczerpany limit subskrypcji Claude. Spróbuj później."
        else:
            glowny = "Agent zakończył się błędem (kod %s)." % kod
    ogon = [l for l in stderr_linie if l.strip()][-8:]
    if wynik_tekst and not przerwany_limitem:
        ogon = [_skroc(wynik_tekst, 400)] + ogon
    return glowny + (("\n\n" + "\n".join(ogon)) if ogon else "")


def _uruchom_przebieg(p, cmd, wejscie, limit_min):
    """Wątek roboczy: proces → zdarzenia → zapis wątku."""
    wid = p.wid
    start = time.time()
    stderr_linie = collections.deque(maxlen=40)
    segmenty = []                                              # tekst z przyrostów (po blokach)
    teksty_wiadomosci = []                                     # tekst z pełnych wiadomości asystenta (zapas)
    widziane_narzedzia = set()
    zapisane_narzedzia = 0
    wynik = None
    blok_tekstowy = False
    try:
        proc = subprocess.Popen(cmd, cwd=rdzen.REPO, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, env=_srodowisko(), creationflags=rdzen.CREATE_NO_WINDOW)
    except OSError as e:
        tekst = "Nie mogę uruchomić Claude Code (%s). Sprawdź instalację albo ustaw ścieżkę agent.sciezka." % e
        _dopisz(wid, {"rola": "system", "tekst": tekst})
        p.zdarzenie("blad", tekst=tekst)
        p.zdarzenie("koniec", czas_s=round(time.time() - start, 1))
        return
    with _lock:
        p.proc = proc
        if p.przerwany:                                        # „stop” przyszedł, zanim proces wystartował
            _zabij(proc)

    def czytaj_stderr():
        for linia in iter(proc.stderr.readline, b""):
            stderr_linie.append(linia.decode("utf-8", "replace").rstrip())
    t_err = threading.Thread(target=czytaj_stderr, daemon=True)
    t_err.start()

    def limit():
        if proc.poll() is None:
            p.limit_czasu = True
            rdzen.log("agent: wątek %s przekroczył limit %d min — zatrzymuję" % (wid, limit_min))
            _zabij(proc)
    zegar = threading.Timer(max(60, limit_min * 60), limit)
    zegar.daemon = True
    zegar.start()
    try:
        try:
            proc.stdin.write(wejscie.encode("utf-8"))
            proc.stdin.close()
        except OSError:
            pass
        for surowa in iter(proc.stdout.readline, b""):
            linia = surowa.decode("utf-8", "replace").strip()
            if not linia.startswith("{"):
                continue
            try:
                d = json.loads(linia)
            except ValueError:
                continue
            typ = d.get("type")
            if d.get("session_id") and typ in ("system", "result"):
                with _lock:
                    w = rdzen.czytaj_json(_sciezka_watku(wid)) or {}
                    if w.get("session_id") != d["session_id"]:
                        _dopisz(wid, session_id=d["session_id"])
            if d.get("parent_tool_use_id"):                    # wnętrze pod-agenta — nie pokazujemy
                continue
            if typ == "stream_event":
                ev = d.get("event") or {}
                if ev.get("type") == "content_block_start" and (ev.get("content_block") or {}).get("type") == "text":
                    blok_tekstowy = True
                    if segmenty and segmenty[-1]:
                        segmenty.append("")
                        p.zdarzenie("tekst", delta="\n\n")
                    elif not segmenty:
                        segmenty.append("")
                elif ev.get("type") == "content_block_delta":
                    delta = ev.get("delta") or {}
                    if delta.get("type") == "text_delta" and delta.get("text"):
                        if not segmenty:
                            segmenty.append("")
                        segmenty[-1] += delta["text"]
                        p.zdarzenie("tekst", delta=delta["text"])
            elif typ == "assistant":
                for blok in ((d.get("message") or {}).get("content") or []):
                    if not isinstance(blok, dict):
                        continue
                    if blok.get("type") == "text" and blok.get("text"):
                        teksty_wiadomosci.append(blok["text"])
                    elif blok.get("type") == "tool_use":
                        klucz = blok.get("id") or id(blok)
                        if klucz in widziane_narzedzia:
                            continue
                        widziane_narzedzia.add(klucz)
                        nazwa, opis = opis_narzedzia(blok.get("name"), blok.get("input"))
                        p.zdarzenie("narzedzie", nazwa=nazwa, opis=opis)
                        if zapisane_narzedzia < MAX_NARZEDZI_W_WATKU:
                            zapisane_narzedzia += 1
                            _dopisz(wid, {"rola": "narzedzie", "tekst": (nazwa + (": " + opis if opis else ""))})
            elif typ == "result":
                wynik = d
        proc.wait()
    finally:
        zegar.cancel()
    t_err.join(timeout=5)

    czas_s = round(time.time() - start, 1)
    tekst = "".join(s if i == 0 else "\n\n" + s for i, s in enumerate(x for x in segmenty if x)).strip()
    if not tekst and not blok_tekstowy:
        tekst = "\n\n".join(teksty_wiadomosci).strip()
    if not tekst and wynik and isinstance(wynik.get("result"), str) and not wynik.get("is_error"):
        tekst = wynik["result"].strip()
    if tekst:
        msg = _dopisz(wid, {"rola": "assistant", "tekst": tekst})
        p.zdarzenie("wiadomosc", wiadomosc=msg)
    koniec = {"czas_s": czas_s}
    if wynik and isinstance(wynik.get("total_cost_usd"), (int, float)):
        koniec["koszt_usd"] = round(float(wynik["total_cost_usd"]), 4)
    if wynik and isinstance(wynik.get("duration_ms"), (int, float)):
        koniec["czas_s"] = round(wynik["duration_ms"] / 1000.0, 1)

    blad_wyniku = bool(wynik and (wynik.get("is_error") or (wynik.get("subtype") not in (None, "success"))))
    if p.przerwany:
        _dopisz(wid, {"rola": "system", "tekst": "Przerwano."})
        koniec["przerwano"] = True
    elif p.limit_czasu or proc.returncode != 0 or blad_wyniku or wynik is None:
        wynik_tekst = ""
        if wynik:
            wynik_tekst = wynik.get("result") if isinstance(wynik.get("result"), str) else str(wynik.get("subtype") or "")
            for e in wynik.get("errors") or []:
                wynik_tekst += "\n" + str(e)
        if wynik is None and proc.returncode == 0 and not p.limit_czasu:
            wynik_tekst = "Program nie zwrócił wyniku."
        opis = _blad_czytelny(proc.returncode, list(stderr_linie), wynik_tekst, p.limit_czasu, limit_min)
        if "no conversation found" in (wynik_tekst + "\n".join(stderr_linie)).lower():
            _dopisz(wid, session_id=None)                      # następna wiadomość zacznie nową sesję
        _dopisz(wid, {"rola": "system", "tekst": opis})
        p.zdarzenie("blad", tekst=opis)
        rdzen.log("agent: wątek %s — błąd (kod %s): %s" % (wid, proc.returncode, opis.splitlines()[0]))
    p.zdarzenie("koniec", **koniec)


# --------------------------------------------------------------------------- dostęp
def _wymagaj_dostepu(z):
    if z.lokalny:
        return
    if not (rdzen.konfiguracja().get("agent") or {}).get("zdalnie"):
        raise BladHTTP(403, "Agent z telefonu jest wyłączony. Włącz go na komputerze z panelem: Ustawienia → Telefon → "
                            "„Agent z telefonu”.", kod="agent_zdalnie_wylaczony")


def _chroniony(fn):
    def opakowanie(z):
        _wymagaj_dostepu(z)
        return fn(z)
    opakowanie.__name__ = fn.__name__
    return opakowanie


# --------------------------------------------------------------------------- trasy
def _stan(z):
    cfg = rdzen.konfiguracja().get("agent") or {}
    s = znajdz_program()
    tryb = cfg.get("tryb_domyslny") if cfg.get("tryb_domyslny") in ID_TRYBOW else "praca"
    tryby = TRYBY if z.lokalny else [t for t in TRYBY if t["id"] != "auto"]
    if not z.lokalny and tryb == "auto":
        tryb = "praca"
    out = {"dostepny": bool(s), "zdalnie": bool(cfg.get("zdalnie")), "tryby": tryby, "tryb_domyslny": tryb,
           "model": cfg.get("model") or "", "przebiegi": _ile_trwa(), "max_przebiegow": MAX_PRZEBIEGOW}
    if s:
        out["wersja"] = wersja_programu(s)
        if z.lokalny:
            out["sciezka"] = s
    else:
        out["powod"] = ("Nie znaleziono Claude Code na tym komputerze. Zainstaluj go (claude.ai/code) i zaloguj się "
                        "albo wpisz ścieżkę do programu w konfiguracji lokalnej (agent.sciezka).")
    if not z.lokalny and not cfg.get("zdalnie"):
        out["dostepny"] = False
        out["powod"] = "Agent z telefonu jest wyłączony (włącz na komputerze: Ustawienia → Telefon)."
    return out


@_chroniony
def _lista(z):
    out = []
    try:
        nazwy = [n for n in os.listdir(_kat_watkow()) if n.endswith(".json")]
    except OSError:
        nazwy = []
    for n in nazwy:
        w = rdzen.czytaj_json(os.path.join(_kat_watkow(), n))
        if not isinstance(w, dict) or not w.get("id"):
            continue
        wpis = {"id": w["id"], "tytul": w.get("tytul") or "Rozmowa", "utworzono": w.get("utworzono"),
                "ostatnio": w.get("ostatnio") or w.get("utworzono"), "wiadomosci": len(w.get("wiadomosci") or []),
                "trwa": _trwa(w["id"]), "osoby": _osoby_watku(w)}
        wpis.update(_kto_zalozyl(w))
        out.append(wpis)
    out.sort(key=lambda w: (w["ostatnio"] or "", w["id"]), reverse=True)
    return {"watki": out}


@_chroniony
def _nowy(z):
    dane = z.json if z.json is not None else {}
    if not isinstance(dane, dict):
        raise BladHTTP(400, "Oczekiwano obiektu JSON {tytul?}")
    if set(dane) - {"tytul"}:
        raise BladHTTP(400, "Nieznane pola: %s" % ", ".join(sorted(set(dane) - {"tytul"})))
    tytul = dane.get("tytul")
    if tytul is not None and not isinstance(tytul, str):
        raise BladHTTP(400, "Tytuł musi być tekstem")
    tytul = " ".join((tytul or "").split())[:120]
    with _lock:
        for _ in range(50):
            wid = rdzen.nowe_id("w")
            if not os.path.exists(_sciezka_watku(wid)):
                break
        teraz = rdzen.teraz()
        w = {"id": wid, "tytul": tytul or "Nowa rozmowa", "tytul_auto": not tytul, "utworzono": teraz,
             "ostatnio": teraz, "utworzyl": z.kto, "zdalnie": not z.lokalny, "session_id": None, "wiadomosci": []}
        _zapisz_watek(w)
    return 201, _widok_watku(w)


@_chroniony
def _watek(z):
    with _lock:
        return _widok_watku(_czytaj_watek(z.params["id"]))


def _sprawdz_kontekst(lista):
    if lista is None:
        return []
    if not isinstance(lista, list):
        raise BladHTTP(400, "Pole „kontekst” musi być listą")
    if len(lista) > MAX_KONTEKST:
        raise BladHTTP(400, "Za dużo odwołań w kontekście (najwyżej %d)" % MAX_KONTEKST)
    out = []
    for k in lista:
        if not isinstance(k, dict) or set(k) - {"typ", "cel", "etykieta"}:
            raise BladHTTP(400, "Każde odwołanie w kontekście to obiekt {typ, cel, etykieta}")
        typ, cel, ety = k.get("typ"), k.get("cel"), k.get("etykieta")
        if not isinstance(typ, str) or not isinstance(cel, str) or not typ.strip() or not cel.strip():
            raise BladHTTP(400, "Odwołanie w kontekście musi mieć typ i cel")
        if ety is not None and not isinstance(ety, str):
            raise BladHTTP(400, "Etykieta odwołania musi być tekstem")
        wpis = {"typ": _skroc(typ, 20), "cel": _skroc(cel, 300)}
        if ety and ety.strip():
            wpis["etykieta"] = _skroc(ety, 120)
        out.append(wpis)
    return out


@_chroniony
def _wiadomosc(z):
    wid = z.params["id"]
    dane = z.json
    if not isinstance(dane, dict):
        raise BladHTTP(400, "Oczekiwano obiektu JSON {tekst, tryb?, model?, kontekst?}")
    nieznane = set(dane) - {"tekst", "tryb", "model", "kontekst"}
    if nieznane:
        raise BladHTTP(400, "Nieznane pola: %s" % ", ".join(sorted(nieznane)))
    tekst = dane.get("tekst")
    if not isinstance(tekst, str) or not tekst.strip():
        raise BladHTTP(400, "Napisz wiadomość do agenta")
    tekst = tekst.replace("\r\n", "\n").strip()
    if len(tekst) > MAX_TEKST:
        raise BladHTTP(400, "Wiadomość jest za długa (najwyżej %d znaków)" % MAX_TEKST)
    cfg = rdzen.konfiguracja().get("agent") or {}
    tryb = dane.get("tryb") or cfg.get("tryb_domyslny") or "praca"
    if tryb not in ID_TRYBOW:
        raise BladHTTP(400, "Nieznany tryb: %s (dostępne: %s)" % (tryb, ", ".join(ID_TRYBOW)))
    if not z.lokalny and tryb == "auto":
        tryb = "praca"
    model = dane.get("model") or cfg.get("model") or None
    if model is not None and (not isinstance(model, str) or not RX_MODEL.match(model)):
        raise BladHTTP(400, "Niepoprawna nazwa modelu")
    kontekst = _sprawdz_kontekst(dane.get("kontekst"))
    program = znajdz_program()
    if not program:
        raise BladHTTP(503, "Nie znaleziono Claude Code na tym komputerze — agent jest niedostępny.")
    limit_min = int(cfg.get("limit_czasu_min") or 30)

    with _lock:
        w = _czytaj_watek(wid)
        if _trwa(wid):
            raise BladHTTP(409, "Agent jeszcze odpowiada w tym wątku. Poczekaj albo go zatrzymaj.")
        if _ile_trwa() >= MAX_PRZEBIEGOW:
            raise BladHTTP(409, "Agent pracuje już w %d wątkach naraz. Poczekaj, aż któryś skończy." % MAX_PRZEBIEGOW)
        wiad = {"rola": "user", "tekst": tekst, "kto": z.kto, "zdalnie": not z.lokalny, "tryb": tryb}
        if kontekst:
            wiad["kontekst"] = kontekst
        pola = {}
        if w.get("tytul_auto") and not any(m.get("rola") == "user" for m in w.get("wiadomosci") or []):
            pola = {"tytul": _skroc(tekst.splitlines()[0], 60), "tytul_auto": False}   # tytuł z pierwszej wiadomości
        msg = _dopisz(wid, wiad, **pola)
        for stary in [k for k, v in _przebiegi.items() if v.zakonczony and time.time() - v.koniec_t > 3600]:
            del _przebiegi[stary]                              # bufory starych przebiegów nie rosną bez końca
        p = Przebieg(wid)
        _przebiegi[wid] = p
        od = _licznik_n.get(wid, 0) + 1
    cmd = zbuduj_polecenie(program, tryb, model, w.get("session_id"), w.get("katalogi"))
    rdzen.log("agent: wątek %s, tryb %s%s, pisze %s%s" % (wid, tryb, (", model " + model) if model else "", z.kto,
                                                        ", wznowienie" if w.get("session_id") else ""))
    threading.Thread(target=_bezpiecznie, args=(p, cmd, tresc_dla_agenta(z.kto, tekst, kontekst), limit_min),
                     daemon=True, name="agent-" + wid).start()
    return 202, {"ok": True, "nr": msg["nr"], "od": od, "tryb": tryb}


def _bezpiecznie(p, cmd, wejscie, limit_min):
    try:
        _uruchom_przebieg(p, cmd, wejscie, limit_min)
    except Exception as e:                                     # nie zostawiaj wątku w stanie „trwa”
        import traceback
        rdzen.log("agent: awaria przebiegu %s\n%s" % (p.wid, traceback.format_exc()))
        try:
            _zabij(p.proc)                                     # nie zostawiaj procesu bez czytelnika stdout i bez limitu
        except Exception:
            pass
        if not p.zakonczony:
            p.zdarzenie("blad", tekst="Wewnętrzny błąd panelu przy obsłudze agenta: %s" % e)
            p.zdarzenie("koniec")


@_chroniony
def _strumien(z):
    wid = z.params["id"]
    _wymagaj_watku(wid)
    od = z.q_int("od", 0, minimum=0)

    def generator():
        with _lock:
            p = _przebiegi.get(wid)
        # „koniec” ma zawsze n >= od: klient pomija zdarzenia o numerze, który już widział, a koniec musi dotrzeć
        # (np. po restarcie serwera w trakcie pracy liczniki zaczynają się od zera)
        if p is None:                                          # nic nie trwa i nic nie było od startu serwera
            yield {"n": max(_licznik_n.get(wid, 0), od), "typ": "koniec", "bezczynny": True}
            return
        i = 0
        while True:
            with p.cond:
                nowe = p.zdarzenia[i:]
                if not nowe and not p.zakonczony:
                    p.cond.wait(8)
                    nowe = p.zdarzenia[i:]
                i += len(nowe)
                zakonczony = p.zakonczony
            for e in nowe:
                if e["typ"] == "koniec":
                    yield e if e["n"] >= od else dict(e, n=od)  # koniec wysyłany zawsze — klient wie, że ma zamknąć
                    return
                if e["n"] >= od:
                    yield e
            if not nowe:
                if zakonczony:
                    yield {"n": max(_licznik_n.get(wid, 0), od), "typ": "koniec", "bezczynny": True}
                    return
                yield None                                     # podtrzymanie połączenia
    return Strumien(generator())


@_chroniony
def _stop(z):
    wid = z.params["id"]
    _wymagaj_watku(wid)
    with _lock:
        p = _przebiegi.get(wid)
        if not p or p.zakonczony:
            return {"ok": True, "trwal": False}
        p.przerwany = True
        proc = p.proc
    rdzen.log("agent: %s zatrzymuje wątek %s" % (z.kto, wid))
    _zabij(proc)
    return {"ok": True, "trwal": True}


# --------------------------------------------------------------------------- dla innych modułów (bc/sesje.py)
def mozna_uruchomic(z):
    """Czy to żądanie może uruchomić agenta: osoba przy komputerze z panelem albo (gdy włączony jest „Agent
    z telefonu”) żądanie zdalne. Uprawnienia dodatkowe (np. tylko decydent) sprawdza wołający."""
    return bool(z.lokalny or (rdzen.konfiguracja().get("agent") or {}).get("zdalnie"))


def uruchom_polecenie(tekst, kto, tytul=None, watek=None, tryb="praca", katalogi=None, zestaw=None, zdalnie=None):
    """Przebieg agenta z gotowym poleceniem od panelu (np. notatki z rozmowy, propozycje tematów).

    `watek` = istniejący wątek (wtedy rozmowa jest wznawiana) albo None (nowy wątek z `tytul`). `katalogi` = katalogi
    sesji rozmów, które agent może czytać (`--add-dir`, zapamiętane w wątku). `zestaw` = zawężona lista narzędzi
    (ZESTAWY_NARZEDZI) zamiast uprawnień trybu. `zdalnie` = czy polecenie zlecił ktoś zdalnie (None = nie wiadomo;
    zapisuje się przy wątku i wiadomości). Uprawnienia osoby sprawdza wołający.
    Zwraca {watek, nr, od, tryb}. Błędy: 503 brak programu, 409 wątek pracuje albo limit przebiegów naraz."""
    if tryb not in ("plan", "praca"):
        raise BladHTTP(400, "Nieznany tryb agenta")
    if zestaw is not None and zestaw not in ZESTAWY_NARZEDZI:
        raise BladHTTP(400, "Nieznany zestaw narzędzi agenta")
    tekst = str(tekst or "").replace("\r\n", "\n").strip()
    if not tekst or len(tekst) > MAX_TEKST:
        raise BladHTTP(400, "Polecenie dla agenta jest puste albo za długie")
    cfg = rdzen.konfiguracja().get("agent") or {}
    program = znajdz_program()
    if not program:
        raise BladHTTP(503, "Nie znaleziono Claude Code na tym komputerze — agent jest niedostępny.")
    limit_min = int(cfg.get("limit_czasu_min") or 30)
    model = cfg.get("model") or None
    if model is not None and (not isinstance(model, str) or not RX_MODEL.match(model)):
        model = None
    katalogi = _katalogi_sesji(katalogi)
    with _lock:
        if _ile_trwa() >= MAX_PRZEBIEGOW:                     # przed założeniem wątku: bez pustych wątków-sierot
            raise BladHTTP(409, "Agent pracuje już w %d wątkach naraz. Spróbuj za chwilę." % MAX_PRZEBIEGOW)
        if watek is None:
            for _ in range(50):
                wid = rdzen.nowe_id("w")
                if not os.path.exists(_sciezka_watku(wid)):
                    break
            teraz = rdzen.teraz()
            _zapisz_watek({"id": wid, "tytul": _skroc(tytul or "Polecenie z panelu", 120), "tytul_auto": False,
                           "utworzono": teraz, "ostatnio": teraz, "utworzyl": kto, "zdalnie": zdalnie,
                           "session_id": None, "wiadomosci": [], "katalogi": katalogi})
        else:
            wid = watek
        w = _czytaj_watek(wid)
        if _trwa(wid):
            raise BladHTTP(409, "Agent jeszcze pracuje nad poprzednim poleceniem w tym wątku.")
        if _ile_trwa() >= MAX_PRZEBIEGOW:
            raise BladHTTP(409, "Agent pracuje już w %d wątkach naraz. Spróbuj za chwilę." % MAX_PRZEBIEGOW)
        pola = {"katalogi": katalogi} if katalogi and katalogi != w.get("katalogi") else {}
        wiad = {"rola": "user", "tekst": tekst, "kto": kto, "tryb": tryb}
        if zdalnie is not None:
            wiad["zdalnie"] = bool(zdalnie)
        msg = _dopisz(wid, wiad, **pola)
        p = Przebieg(wid)
        _przebiegi[wid] = p
        od = _licznik_n.get(wid, 0) + 1
    cmd = zbuduj_polecenie(program, tryb, model, w.get("session_id"), katalogi or w.get("katalogi"), zestaw=zestaw)
    rdzen.log("agent: polecenie panelu w wątku %s (tryb %s%s, %s)" % (wid, tryb, (", narzędzia: " + zestaw)
                                                                       if zestaw else "", kto))
    threading.Thread(target=_bezpiecznie, args=(p, cmd, tresc_dla_agenta(kto, tekst), limit_min),
                     daemon=True, name="agent-" + wid).start()
    return {"watek": wid, "nr": msg["nr"], "od": od, "tryb": tryb}


def stan_watku(wid):
    """{trwa, ostatnia_odpowiedz, blad} wątku — do sprawdzania, czy polecenie panelu się skończyło. None, gdy wątku nie
    ma. `blad` = ostatnia wiadomość systemowa po ostatniej odpowiedzi (np. limit subskrypcji)."""
    try:
        with _lock:
            w = _czytaj_watek(wid)
            trwa = _trwa(wid)
    except BladHTTP:
        return None
    odp, blad = None, None
    for m in reversed(w.get("wiadomosci") or []):
        if m.get("rola") == "assistant" and odp is None:
            odp = m.get("tekst")
            break
        if m.get("rola") == "system" and blad is None:
            blad = m.get("tekst")
        if m.get("rola") == "user":
            break
    return {"trwa": trwa, "ostatnia_odpowiedz": odp, "blad": blad}


def zarejestruj(app):
    app.dodaj("GET", "/api/agent/stan", _stan)
    app.dodaj("GET", "/api/agent/watki", _lista)
    app.dodaj("POST", "/api/agent/watki", _nowy)
    app.dodaj("GET", "/api/agent/watki/<id>", _watek)
    app.dodaj("POST", "/api/agent/watki/<id>/wiadomosc", _wiadomosc)
    app.dodaj("GET", "/api/agent/watki/<id>/strumien", _strumien)
    app.dodaj("POST", "/api/agent/watki/<id>/stop", _stop)


def _sprzatanie():
    """Przy zamykaniu panelu kończy trwające przebiegi razem z ich drzewem procesów (inaczej osierocony agent
    pracowałby dalej w repozytorium bez limitu czasu)."""
    if not _lock.acquire(timeout=3):
        return
    try:
        procesy = [p.proc for p in _przebiegi.values() if not p.zakonczony and p.proc is not None]
    finally:
        _lock.release()
    for proc in procesy:
        try:
            _zabij(proc)
        except Exception:
            pass


import atexit  # noqa: E402

atexit.register(_sprzatanie)
