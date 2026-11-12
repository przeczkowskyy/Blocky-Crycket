# -*- coding: utf-8 -*-
"""Głosówki: przyjęcie nagrania i lokalna transkrypcja (faster-whisper, opcjonalnie).

- POST /api/glos przyjmuje surowe audio (format rozpoznany po pierwszych bajtach: webm, ogg, m4a/mp4, wav, mp3),
  zapisuje RUNTIME/nagrania/<id>/nagranie.<ext> + stan.json i budzi robotnika.
- Robotnik to osobny proces `python -m bc.glos --robotnik` (katalog roboczy panel/, niski priorytet, bez okna,
  jeden naraz dzięki plikowi pid). Bierze po kolei wszystkie nagrania „czeka”, model ładuje raz.
- Karta graficzna (float16) tylko wtedy, gdy są biblioteki CUDA z pip (nvidia/cublas/bin, nvidia/cudnn/bin),
  nvidia-smi pokazuje >= 2500 MB wolnej pamięci i nie ma blokady Sagi (%LOCALAPPDATA%/SagaPipeline/gpu.lock).
  W każdym innym razie i po każdym błędzie karty: procesor int8.
- Serwer nigdy nie importuje faster_whisper (ciężki) — sprawdza tylko, czy pakiet jest (importlib.util.find_spec).
"""
import importlib.util
import json
import os
import re
import site
import subprocess
import sys
import threading
import time

from . import rdzen
from .rdzen import BladHTTP

MIN_BAJTY = 1024
MAX_BAJTY = 80 * 1024 * 1024
MIN_WOLNA_VRAM_MB = 2500
MAX_PROB = 3
BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
SLOWNIK_GRY = "Roblox, karczma, questy, dungeon, tycoon, pety, gildia, Robuxy, Blender, Figma, Obsidian"
PODPOWIEDZ_WHISPER = "Transkrypcja wymaga pakietu faster-whisper. Zainstaluj go na komputerze z panelem: pip install faster-whisper"
RX_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")

# sztampowe „napisy” wymyślane przez Whispera na ciszy — usuwane zawsze
HALUCYNACJE = [re.compile(w, re.I) for w in (
    r"dzi[eę]kuj[eę]\s+za\s+(uwag[eę]|ogl[aą]danie|obejrzenie|wys[lł]uchanie)",
    r"dzi[eę]ki\s+za\s+(ogl[aą]danie|obejrzenie|uwag[eę])",
    r"napisy\s+(stworzone|wykonane|przygotowane|zrobione|robione)\s+przez",
    r"(napisy|t[lł]umaczenie)\s*[:\-]?\s*\w*\s*(amara|ninja)",
    r"amara\.org",
    r"subskrybuj",
    r"zapraszam[y]?\s+(na|do)\s+(kolejn|nast[eę]pn)",
    r"do\s+zobaczenia\s+w\s+(kolejnym|nast[eę]pnym)\s+(odcinku|filmie)",
)]
# krótkie słowa, które same w sobie (jako cały tekst) są najpewniej halucynacją na ciszy
SAMA_HALUCYNACJA = re.compile(r"^\W*(dzi[eę]kuj[eę]( bardzo)?|dzi[eę]ki|okej|ok|cze[sś][cć]|hej)\W*$", re.I)

_whisper_cache = {"t": 0.0, "v": None}
_urzadzenie_cache = {"t": 0.0, "v": None}
_start_lock = threading.Lock()
_ostatni_start = {"t": 0.0}


# --------------------------------------------------------------------------- ścieżki i stan nagrań
def _kat_nagran():
    return os.path.join(rdzen.RUNTIME, "nagrania")


def _plik_pid():
    return os.path.join(_kat_nagran(), "robotnik.pid")


def _kat(nid):
    if not isinstance(nid, str) or not RX_ID.match(nid):
        raise BladHTTP(400, "Niepoprawny identyfikator nagrania")
    return os.path.join(_kat_nagran(), nid)


def _czytaj_stan(nid):
    return rdzen.czytaj_json(os.path.join(_kat(nid), "stan.json"))


def _zapisz_stan(nid, stan):
    rdzen.zapisz_json(os.path.join(_kat(nid), "stan.json"), stan)


def _zmien_stan(nid, **pola):
    st = _czytaj_stan(nid) or {"id": nid}
    st.update(pola)
    for k in [k for k, v in pola.items() if v is None]:
        st.pop(k, None)
    _zapisz_stan(nid, st)
    return st


def rozpoznaj_format(poczatek):
    """Rozszerzenie pliku audio z pierwszych bajtów albo None."""
    if poczatek[:4] == b"\x1a\x45\xdf\xa3":
        return "webm"
    if poczatek[:4] == b"OggS":
        return "ogg"
    if poczatek[4:8] == b"ftyp":
        return "m4a"
    if poczatek[:4] == b"RIFF" and poczatek[8:12] == b"WAVE":
        return "wav"
    if poczatek[:3] == b"ID3" or (len(poczatek) > 1 and poczatek[0] == 0xFF and (poczatek[1] & 0xE0) == 0xE0):
        return "mp3"
    return None


# --------------------------------------------------------------------------- środowisko transkrypcji
def whisper_dostepny():
    if time.time() - _whisper_cache["t"] > 60:
        try:
            v = importlib.util.find_spec("faster_whisper") is not None
        except (ImportError, ValueError):
            v = False
        _whisper_cache.update(t=time.time(), v=v)
    return _whisper_cache["v"]


def _cfg():
    return rdzen.konfiguracja().get("glos") or {}


def nazwa_modelu():
    return str(_cfg().get("model") or "large-v3-turbo")


def katalog_modeli():
    """glos.katalog_modeli z konfiguracji → istniejący katalog modeli Sagi → RUNTIME/whisper_models."""
    k = _cfg().get("katalog_modeli")
    if k:
        return os.path.expandvars(os.path.expanduser(str(k)))
    saga = os.path.join(os.environ.get("LOCALAPPDATA") or "", "SagaPipeline", "whisper_models")
    if os.environ.get("LOCALAPPDATA") and os.path.isdir(saga):
        return saga
    return os.path.join(rdzen.RUNTIME, "whisper_models")


def model_lokalny():
    """Czy model jest już na dysku (żeby nigdy nie pobierać go drugi raz)."""
    nazwa = nazwa_modelu()
    if os.path.isdir(nazwa):
        return True
    kat = katalog_modeli()
    try:
        wpisy = os.listdir(kat)
    except OSError:
        return False
    klucz = nazwa.lower().replace("/", "--")
    for w in wpisy:
        if w.lower().startswith("models--") and w.lower().endswith(klucz):
            snap = os.path.join(kat, w, "snapshots")
            try:
                if any(os.path.isfile(os.path.join(snap, s, "model.bin")) for s in os.listdir(snap)):
                    return True
            except OSError:
                pass
    return False


def _katalogi_cuda():
    """Katalogi bin bibliotek CUDA z pip (nvidia-cublas-cu12, nvidia-cudnn-cu12) albo None."""
    kandydaci = []
    try:
        kandydaci += site.getsitepackages()
    except AttributeError:
        pass
    try:
        kandydaci.append(site.getusersitepackages())
    except AttributeError:
        pass
    kandydaci += [p for p in sys.path if p.lower().endswith("site-packages")]
    for sp in kandydaci:
        cublas = os.path.join(sp, "nvidia", "cublas", "bin")
        cudnn = os.path.join(sp, "nvidia", "cudnn", "bin")
        if os.path.isdir(cublas) and os.path.isdir(cudnn):
            return [cublas, cudnn]
    return None


def _wolna_vram_mb():
    kod, out, _ = rdzen.uruchom(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"], timeout=10)
    if kod != 0:
        return None
    wartosci = [int(x) for x in re.findall(r"\d+", out)]
    return max(wartosci) if wartosci else None


def wybierz_urzadzenie():
    """(urzadzenie, typ_obliczen, powod, katalogi_dll) — karta graficzna tylko przy spełnieniu wszystkich warunków."""
    dll = _katalogi_cuda()
    if not dll:
        return "cpu", "int8", "brak bibliotek CUDA (nvidia-cublas-cu12, nvidia-cudnn-cu12)", None
    blokada = os.path.join(os.environ.get("LOCALAPPDATA") or "", "SagaPipeline", "gpu.lock")
    if os.environ.get("LOCALAPPDATA") and os.path.exists(blokada):
        return "cpu", "int8", "karta zajęta przez Sagę (gpu.lock)", None
    wolna = _wolna_vram_mb()
    if wolna is None:
        return "cpu", "int8", "nvidia-smi nie odpowiada", None
    if wolna < MIN_WOLNA_VRAM_MB:
        return "cpu", "int8", "za mało wolnej pamięci karty (%d MB)" % wolna, None
    return "cuda", "float16", "karta graficzna (%d MB wolne)" % wolna, dll


def _urzadzenie_podglad():
    if time.time() - _urzadzenie_cache["t"] > 30:
        urz, typ, powod, _ = wybierz_urzadzenie()
        _urzadzenie_cache.update(t=time.time(), v=(urz, typ, powod))
    return _urzadzenie_cache["v"]


# --------------------------------------------------------------------------- robotnik: pid i start
def _proces_zyje(pid):
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        k32 = ctypes.windll.kernel32
        h = k32.OpenProcess(0x1000, False, pid)                # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return ctypes.GetLastError() == 5                  # brak dostępu = proces istnieje
        kod = ctypes.c_ulong()
        try:
            ok = k32.GetExitCodeProcess(h, ctypes.byref(kod))
        finally:
            k32.CloseHandle(h)
        return bool(ok) and kod.value == 259                   # STILL_ACTIVE
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def robotnik_zyje():
    p = _plik_pid()
    d = rdzen.czytaj_json(p)
    if not isinstance(d, dict):
        return False
    try:
        swiezy = time.time() - os.path.getmtime(p) < 20 * 60  # robotnik „puka” w plik co kilkanaście sekund
    except OSError:
        return False
    return swiezy and _proces_zyje(d.get("pid"))


def uruchom_robotnika():
    """Startuje robotnika, jeśli nie działa. Zwraca True, gdy wystartował nowy proces."""
    with _start_lock:
        if robotnik_zyje() or time.time() - _ostatni_start["t"] < 3:
            return False
        _ostatni_start["t"] = time.time()
        rdzen.upewnij_katalog(_kat_nagran())
        env = dict(os.environ, BC_PANEL_RUNTIME=rdzen.RUNTIME, BC_PANEL_DANE=rdzen.DANE, PYTHONDONTWRITEBYTECODE="1",
                   PYTHONIOENCODING="utf-8")
        flagi = (rdzen.CREATE_NO_WINDOW | BELOW_NORMAL_PRIORITY_CLASS) if os.name == "nt" else 0
        try:
            with open(os.path.join(_kat_nagran(), "robotnik.log"), "ab") as log:
                subprocess.Popen([rdzen.python_exe(), "-B", "-m", "bc.glos", "--robotnik"], cwd=rdzen.PANEL,
                                 stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, env=env,
                                 creationflags=flagi, close_fds=True,
                                 **({} if os.name == "nt" else {"start_new_session": True}))
        except OSError as e:
            rdzen.log("glos: nie mogę uruchomić robotnika: %s" % e)
            return False
        return True


# --------------------------------------------------------------------------- trasy
def _stan_glosu(z):
    out = {"whisper": whisper_dostepny(), "model": nazwa_modelu()}
    if not out["whisper"]:
        out["powod"] = PODPOWIEDZ_WHISPER
        return out
    urz, typ, powod = _urzadzenie_podglad()
    out["urzadzenie"] = "karta graficzna" if urz == "cuda" else "procesor"
    out["urzadzenie_powod"] = powod
    out["model_lokalny"] = model_lokalny()
    if not out["model_lokalny"]:
        out["powod"] = "Model %s zostanie pobrany przy pierwszej głosówce (ok. 1,6 GB)." % nazwa_modelu()
    out["robotnik"] = robotnik_zyje()
    return out


def _przyjmij(z):
    typ = (z.naglowki.get("Content-Type") or "").split(";")[0].strip().lower()
    if not (typ.startswith(("audio/", "video/")) or typ == "application/octet-stream"):
        raise BladHTTP(415, "Wyślij nagranie jako surowe audio (Content-Type: audio/…)")
    dane = z.cialo or b""
    if len(dane) < MIN_BAJTY:
        raise BladHTTP(400, "Nagranie jest puste albo za krótkie")
    if len(dane) > MAX_BAJTY:
        raise BladHTTP(413, "Nagranie jest za duże (najwyżej 80 MB)")
    ext = rozpoznaj_format(dane[:16])
    if not ext:
        raise BladHTTP(415, "Nie rozpoznaję formatu nagrania (obsługiwane: webm, ogg, m4a/mp4, wav, mp3)")
    for _ in range(50):
        nid = rdzen.nowe_id("g")
        if not os.path.exists(os.path.join(_kat_nagran(), nid)):
            break
    rdzen.zapisz_bajty(os.path.join(_kat(nid), "nagranie." + ext), dane)
    stan = {"id": nid, "stan": "czeka", "czas": rdzen.teraz(), "kto": z.kto, "rozmiar": len(dane), "format": ext,
            "proby": 0}
    if not whisper_dostepny():
        stan.update(stan="brak_whispera", podpowiedz=PODPOWIEDZ_WHISPER)
    _zapisz_stan(nid, stan)
    if stan["stan"] == "czeka":
        uruchom_robotnika()
    rdzen.log("glos: nowe nagranie %s (%s, %d kB) od %s" % (nid, ext, len(dane) // 1024, z.kto))
    return 201, {"id": nid, "stan": stan["stan"]}


def _odczytaj(z):
    nid = z.params["id"]
    st = _czytaj_stan(nid)
    if not isinstance(st, dict):
        raise BladHTTP(404, "Nie ma takiego nagrania")
    if st.get("stan") == "brak_whispera" and whisper_dostepny():   # pakiet doinstalowany — spisz zaległe
        st = _zmien_stan(nid, stan="czeka", podpowiedz=None)
    if st.get("stan") in ("czeka", "transkrybuje") and not robotnik_zyje():
        uruchom_robotnika()                                    # samonaprawa: robotnik padł albo panel wstał od nowa
    out = {"id": nid, "stan": st.get("stan")}
    for k in ("tekst", "dlugosc_s", "blad", "podpowiedz", "urzadzenie", "pusty"):
        if st.get(k) is not None:
            out[k] = st[k]
    return out


def zarejestruj(app):
    app.dodaj("GET", "/api/glos/stan", _stan_glosu)
    app.dodaj("POST", "/api/glos", _przyjmij)
    app.dodaj("GET", "/api/glos/<id>", _odczytaj)


def zdrowie():
    out = {"whisper": whisper_dostepny(), "model": nazwa_modelu(), "katalog_modeli": katalog_modeli()}
    if out["whisper"]:
        out["model_lokalny"] = model_lokalny()
        out["urzadzenie"] = _urzadzenie_podglad()[0]
        out["robotnik"] = robotnik_zyje()
    return out


# =========================================================================== robotnik (osobny proces)
def oczysc_tekst(segmenty):
    """Skleja segmenty, wyrzuca sztampowe halucynacje na ciszy. Zwraca tekst ('' = brak mowy)."""
    czyste = []
    for s in segmenty:
        s = " ".join(str(s or "").split())
        if not s:
            continue
        if len(s) <= 120 and any(w.search(s) for w in HALUCYNACJE):
            continue
        czyste.append(s)
    tekst = " ".join(czyste).strip()
    if SAMA_HALUCYNACJA.match(tekst):
        return ""
    return tekst


def _zajmij_pid():
    p = _plik_pid()
    rdzen.upewnij_katalog(_kat_nagran())
    for _ in range(2):
        try:
            fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if robotnik_zyje():
                return False
            try:
                os.remove(p)                                   # po martwym robotniku
            except OSError:
                return False
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"pid": os.getpid(), "start": rdzen.teraz()}, f)
        return True
    return False


def _zwolnij_pid():
    p = _plik_pid()
    d = rdzen.czytaj_json(p)
    if isinstance(d, dict) and d.get("pid") == os.getpid():
        try:
            os.remove(p)
        except OSError:
            pass


def _puknij():
    try:
        os.utime(_plik_pid(), None)
    except OSError:
        pass


def _do_zrobienia():
    try:
        nazwy = sorted(os.listdir(_kat_nagran()))
    except OSError:
        return []
    out = []
    for n in nazwy:
        if not RX_ID.match(n):
            continue
        st = rdzen.czytaj_json(os.path.join(_kat_nagran(), n, "stan.json"))
        if isinstance(st, dict) and st.get("stan") in ("czeka", "transkrybuje"):   # „transkrybuje” = po padniętym
            out.append(n)
    return out


class _Transkryptor:
    """Trzyma załadowany model między nagraniami; po błędzie karty przechodzi na procesor do końca pracy."""

    def __init__(self):
        self.model = None
        self.urzadzenie = None
        self.tylko_cpu = False

    def _zaladuj(self, urzadzenie, typ):
        from faster_whisper import WhisperModel
        nazwa = nazwa_modelu()
        kw = {"device": urzadzenie, "compute_type": typ, "download_root": katalog_modeli()}
        if urzadzenie == "cpu":
            kw["cpu_threads"] = max(2, (os.cpu_count() or 4) // 2)
        lokalny = model_lokalny()
        if not lokalny:
            rdzen.log("glos: pobieram model %s do %s (jednorazowo)" % (nazwa, katalog_modeli()))
        return WhisperModel(nazwa, local_files_only=lokalny, **kw)

    def _model(self):
        if self.model is not None:
            return self.model
        if self.tylko_cpu:
            urz, typ, powod, dll = "cpu", "int8", "po błędzie karty", None
        else:
            urz, typ, powod, dll = wybierz_urzadzenie()
        if dll:
            for d in dll:
                try:
                    os.add_dll_directory(d)
                except (AttributeError, OSError):
                    pass
                if d not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
        rdzen.log("glos: ładuję model %s na: %s (%s)" % (nazwa_modelu(), urz, powod))
        self.urzadzenie = urz                                  # przed ładowaniem — błąd ładowania na karcie też ma
        self.model = self._zaladuj(urz, typ)                   # przełączyć na procesor
        return self.model

    def _jedno(self, sciezka, puls):
        cfg = _cfg()
        segmenty, info = self._model().transcribe(
            sciezka, language=str(cfg.get("jezyk") or "pl"), beam_size=5, vad_filter=True,
            vad_parameters={"threshold": 0.4, "min_silence_duration_ms": 300, "speech_pad_ms": 60,
                            "min_speech_duration_ms": 200},
            condition_on_previous_text=False, hotwords=SLOWNIK_GRY)
        teksty = []
        for s in segmenty:                                     # generator — tu naprawdę liczy
            teksty.append(s.text)
            puls()
        return teksty, float(getattr(info, "duration", 0.0) or 0.0)

    def transkrybuj(self, sciezka, puls):
        try:
            return self._jedno(sciezka, puls) + (self.urzadzenie,)
        except Exception as e:
            if self.urzadzenie != "cuda":
                raise
            rdzen.log("glos: błąd karty graficznej (%s) — przechodzę na procesor" % e)
            self.model = None
            self.tylko_cpu = True
            import gc
            gc.collect()
            return self._jedno(sciezka, puls) + (self.urzadzenie,)


def _przetworz(nid, tr):
    st = _czytaj_stan(nid)
    if not isinstance(st, dict) or st.get("stan") not in ("czeka", "transkrybuje"):
        return
    proby = int(st.get("proby") or 0) + 1
    if proby > MAX_PROB:
        _zmien_stan(nid, stan="blad", blad="Nie udało się spisać nagrania (%d próby)." % MAX_PROB)
        return
    if not whisper_dostepny():
        _zmien_stan(nid, stan="brak_whispera", podpowiedz=PODPOWIEDZ_WHISPER)
        return
    nagranie = next((os.path.join(_kat(nid), n) for n in os.listdir(_kat(nid)) if n.startswith("nagranie.")), None)
    if not nagranie:
        _zmien_stan(nid, stan="blad", blad="Brak pliku nagrania.")
        return
    if proby > 1:
        tr.tylko_cpu = True                                    # poprzednia próba mogła paść na karcie graficznej
    _zmien_stan(nid, stan="transkrybuje", proby=proby, start_transkrypcji=rdzen.teraz())
    t0 = time.time()
    ostatni = {"t": time.time()}

    def puls():
        if time.time() - ostatni["t"] > 15:
            ostatni["t"] = time.time()
            _puknij()
    try:
        segmenty, dlugosc, urz = tr.transkrybuj(nagranie, puls)
    except Exception as e:
        rdzen.log("glos: błąd transkrypcji %s: %r" % (nid, e))
        _zmien_stan(nid, stan="blad", blad="Nie udało się spisać nagrania: %s" % (str(e)[:300] or e.__class__.__name__))
        return
    tekst = oczysc_tekst(segmenty)
    _zmien_stan(nid, stan="gotowe", tekst=tekst, pusty=(not tekst) or None, dlugosc_s=round(dlugosc, 1),
                urzadzenie="karta graficzna" if urz == "cuda" else "procesor",
                czas_transkrypcji_s=round(time.time() - t0, 1), blad=None)
    rdzen.log("glos: %s spisane w %.1f s (%s, %.1f s nagrania)" % (nid, time.time() - t0, urz, dlugosc))


def robotnik():
    """Pętla robotnika: spisuje wszystkie czekające nagrania i kończy pracę."""
    tr = _Transkryptor()
    while True:
        if not _zajmij_pid():
            print("Inny robotnik już pracuje — kończę.", flush=True)
            return 0
        stop = threading.Event()

        def _serce():                                          # puls także przy ładowaniu i pobieraniu modelu
            while not stop.wait(15):
                _puknij()
        threading.Thread(target=_serce, daemon=True).start()
        try:
            while True:
                lista = _do_zrobienia()
                if not lista:
                    break
                for nid in lista:
                    _puknij()
                    _przetworz(nid, tr)
        finally:
            stop.set()
            _zwolnij_pid()
        if not _do_zrobienia():                                # nagranie mogło dojść tuż przed zwolnieniem
            return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if "--robotnik" in sys.argv:
        sys.exit(robotnik())
    print("Użycie: python -m bc.glos --robotnik  (z katalogu panel/)")
