# -*- coding: utf-8 -*-
"""Telemetria gry: sesje i ich długość, gracze naraz, wydane Robuxy, błędy skryptów i serwery na żywo.

Skąd dane: moduł w grze (src/server/Telemetria) zapisuje co 5 minut liczby zbiorcze do Data Store — jeden wpis na
godzinę zegarową UTC, klucz "g_RRRRMMDD_GG" — a każdy serwer odnawia co minutę swój wpis w sorted mapie Memory Store.
Panel czyta jedno i drugie przez Roblox Open Cloud (API v2) kluczem TYLKO DO ODCZYTU.

Zasady:
- Klucz Open Cloud bierzemy wyłącznie ze zmiennej środowiskowej BC_OPEN_CLOUD_KEY albo z konfiguracji lokalnej
  (`analityka.klucz_open_cloud` w konfiguracja.lokalna.json — poza repozytorium; wspólna konfiguracja z repo nie może
  go ustawić, zob. rdzen.TYLKO_LOKALNE_SEKCJE). Klucz nigdy nie trafia do odpowiedzi API, do logu ani do lustra
  statycznego; wysyłamy go tylko nagłówkiem x-api-key pod adres Open Cloud i nie idziemy za przekierowaniami.
- Do sieci wychodzimy tylko wtedy, gdy ktoś pyta. Odpowiedź pamiętamy 5 minut (zamknięte godziny dłużej), każde
  żądanie ma limit czasu, a błąd Roblox zamieniamy na zdanie po polsku: czego brakuje i co zrobić.
- Dopóki nie ma klucza albo moduł w grze nie jest włączony, odpowiedź mówi `wlaczona: false` i podaje powód.
  Dane przykładowe (`?probka=1`) dostaje tylko osoba przy komputerze i są wyraźnie oznaczone.
- Dane z gry traktujemy jak obce: każdy kubełek przechodzi przez normalizuj_kubelek() (typy, długości, liczba kluczy).

Format kubełka opisuje nagłówek src/server/Telemetria/Agregator.luau. Uprawnienia klucza, limity i źródła
z dokumentacji Roblox: notatka B&C/Technika/Telemetria gry.md.
"""
import concurrent.futures
import datetime
import http.client
import json
import math
import os
import random
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from . import rdzen
from .rdzen import BladHTTP

ADRES_OPEN_CLOUD = "https://apis.roblox.com"
ZMIENNA_KLUCZA = "BC_OPEN_CLOUD_KEY"
MAGAZYN = "BC_Telemetria_v1"                                   # nazwa Data Store — ta sama co w init.luau
MAPA_SERWEROW = "BC_Telemetria_Serwery"                        # sorted mapa Memory Store — ta sama co w init.luau
WPIS_STANU = "stan"                                            # ślad „moduł w grze był włączony”
INNE = "_inne"                                                 # klucz, pod którym gra sumuje wpisy ponad limit
UPRAWNIENIE_DANYCH = "universe-datastores.objects:read"
UPRAWNIENIE_SERWEROW = "memory-store.sorted-map:read"

GODZIN_DOMYSLNIE = 24
GODZIN_MAX = 168                                               # tydzień
LIMIT_CZASU_S = 8                                              # jedno żądanie do Roblox
LIMIT_CALOSCI_S = 25                                           # wszystkie godziny razem
ROWNOLEGLE = 6
PAMIEC_S = 300                                                 # gotowa odpowiedź: 5 minut
PAMIEC_BLEDU_S = 60                                            # po błędzie pytamy ponownie najwcześniej za minutę
PAMIEC_ZAMKNIETEJ_GODZINY_S = 6 * 3600                         # godzina sprzed ≥ 3 h już się nie zmienia
GODZINA_ZAMKNIETA_PO_S = 3 * 3600
LIMIT_ODPOWIEDZI = 8 * 1024 * 1024
LIMIT_KLUCZY = 300                                             # tyle kluczy słownika z jednego kubełka bierzemy pod uwagę
NA_LISCIE = 20                                                 # produktów / błędów / zdarzeń w odpowiedzi
SERWEROW_NA_LISCIE = 50
STRON_SERWEROW = 5                                             # 5 × 200 serwerów
# Budżet odczytów Data Store jest WSPÓLNY dla gry i Open Cloud (300 + 40 × gracze na minutę dla całej gry), więc panel
# sam pilnuje, żeby nie zabrać go zapisom profili graczy: najwyżej tyle żądań do Roblox na minutę, ze wszystkich tras.
ZAPYTAN_NA_MINUTE = 120
CZAS_MAX = 32503680000                                         # 3000-01-01 UTC: późniejszy czas z gry to śmieć
WZOR_KROKU = re.compile(r"^[0-9]{1,3}$")                       # numer kroku lejka (1–100); isdigit() przepuszcza „²”

POLA_LICZBOWE = ("zaktualizowano", "serwery", "zapisy", "starty", "sesje", "sesje_zakonczone", "sekundy_gry",
                 "ccu_max", "ccu_suma", "ccu_probki", "robuxy", "bledy_n")
NAZWA_ZASOBU = re.compile(r"^[A-Za-z0-9_.\-]{1,50}$")
WZOR_KLUCZA = re.compile(r"^[\x21-\x7e]{8,4096}$")             # klucz to drukowalne znaki ASCII bez spacji

_blokada = threading.Lock()
_pamiec = {}                                                   # (uid, magazyn, godzin) -> {"t", "wynik", "dobry"}
_godziny = {}                                                  # (uid, magazyn, początek godziny) -> (kiedy, kubełek | None)
_ostatni = {"t": None, "kod": None}
_otwieracz = None
_zapytania = []                                                # chwile (monotonic) ostatnich żądań do Roblox
_blokada_zapytan = threading.Lock()


class BladOC(Exception):
    """Odczyt z Open Cloud się nie udał. `kod`: klucz_odrzucony | brak_uprawnien | limit | siec | blad_roblox."""

    def __init__(self, kod, komunikat, szczegoly=""):
        super().__init__(komunikat)
        self.kod = kod
        self.komunikat = komunikat
        self.szczegoly = szczegoly


# --------------------------------------------------------------------------- klucz i ustawienia
def klucz_open_cloud():
    """(klucz, skąd) albo (None, None). Tylko zmienna środowiskowa albo konfiguracja lokalna tego komputera."""
    k = (os.environ.get(ZMIENNA_KLUCZA) or "").strip()
    if k:
        return k, "zmienna środowiskowa %s" % ZMIENNA_KLUCZA
    an = rdzen.konfiguracja().get("analityka")
    k = str((an if isinstance(an, dict) else {}).get("klucz_open_cloud") or "").strip()
    return (k, "konfiguracja lokalna") if k else (None, None)


def _bez_klucza(tekst, klucz):
    """Na wszelki wypadek: gdyby klucz znalazł się w jakimś tekście (np. w odpowiedzi serwera), wycinamy go."""
    tekst = str(tekst or "")
    return tekst.replace(klucz, "***") if klucz else tekst


def _adres(an):
    """Adres Open Cloud. Inny niż domyślny tylko z konfiguracji lokalnej i tylko https (albo atrapa na tym komputerze)."""
    a = str(an.get("adres_open_cloud") or "").strip().rstrip("/")
    if not a:
        return ADRES_OPEN_CLOUD
    u = urllib.parse.urlsplit(a)
    if u.hostname and (u.scheme == "https" or (u.scheme == "http" and u.hostname in ("127.0.0.1", "localhost"))):
        return a
    return ADRES_OPEN_CLOUD


def ustawienia():
    """{uid, magazyn, mapa, adres} z konfiguracji; nazwy spoza dozwolonych znaków wracają do domyślnych."""
    cfg = rdzen.konfiguracja()
    gra = cfg.get("gra") if isinstance(cfg.get("gra"), dict) else {}
    an = cfg.get("analityka") if isinstance(cfg.get("analityka"), dict) else {}
    try:
        uid = int(gra.get("universeId"))
    except (TypeError, ValueError):
        uid = None
    magazyn, mapa = str(an.get("magazyn") or MAGAZYN), str(an.get("mapa_serwerow") or MAPA_SERWEROW)
    return {"uid": uid if uid and uid > 0 else None,
            "magazyn": magazyn if NAZWA_ZASOBU.match(magazyn) else MAGAZYN,
            "mapa": mapa if NAZWA_ZASOBU.match(mapa) else MAPA_SERWEROW,
            "adres": _adres(an)}


# --------------------------------------------------------------------------- czas
def klucz_godziny(t):
    """Klucz wpisu w Data Store dla godziny zawierającej chwilę `t` (sekundy Unix): "g_RRRRMMDD_GG" w UTC."""
    return time.strftime("g_%Y%m%d_%H", time.gmtime(int(t) // 3600 * 3600))


def poczatki_godzin(godzin, teraz=None):
    """Początki `godzin` kolejnych godzin zegarowych kończących się bieżącą (sekundy Unix, rosnąco)."""
    ostatnia = int(teraz if teraz is not None else time.time()) // 3600 * 3600
    return [ostatnia - 3600 * i for i in range(godzin - 1, -1, -1)]


def _iso(t):
    return datetime.datetime.fromtimestamp(int(t)).astimezone().isoformat(timespec="seconds")


def _iso_z_gry(t):
    """Czas zapisany przez grę → ISO albo None. Dane z gry są obce: liczba spoza zakresu kalendarza (np. 1e20 —
    na Windows już rok > 3000) nie może wywrócić całej odpowiedzi."""
    t = _liczba(t)
    if not t or t > CZAS_MAX:
        return None
    try:
        return _iso(t)
    except (OverflowError, OSError, ValueError):
        return None


# --------------------------------------------------------------------------- Open Cloud
class _BezPrzekierowan(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None                                            # klucz nie może pójść pod inny adres


def _otworz(zadanie, limit_czasu):
    """Jedyny punkt wyjścia do sieci (testy podmieniają tę funkcję atrapą)."""
    global _otwieracz
    if _otwieracz is None:
        _otwieracz = urllib.request.build_opener(_BezPrzekierowan)
    return _otwieracz.open(zadanie, timeout=limit_czasu)


def _blad_http(e, klucz, zasob):
    szczegoly = ""
    try:
        d = json.loads(e.read(4000).decode("utf-8", "replace"))
        if isinstance(d, dict):
            szczegoly = str(d.get("message") or d.get("code") or "")
    except Exception:
        szczegoly = ""
    szczegoly = _bez_klucza(re.sub(r"\s+", " ", szczegoly), klucz)[:200]
    if e.code == 401:
        return BladOC("klucz_odrzucony", "Roblox odrzucił klucz Open Cloud (401): klucz jest błędny, wyłączony albo wygasł "
                      "— nieużywany klucz wygasa sam po 60 dniach. Utwórz nowy w Creator Dashboard i wpisz go lokalnie.",
                      szczegoly)
    if e.code == 403:
        return BladOC("brak_uprawnien", "Klucz Open Cloud nie ma uprawnień do %s. Dodaj tę operację dla tej gry w "
                      "ustawieniach klucza (Creator Dashboard → API Keys) i sprawdź listę dozwolonych adresów IP." % zasob,
                      szczegoly)
    if e.code == 429:
        return BladOC("limit", "Roblox ograniczył liczbę zapytań (429). Panel spróbuje ponownie za kilka minut.", szczegoly)
    if 300 <= e.code < 400:
        return BladOC("blad_roblox", "Roblox chciał przekierować zapytanie pod inny adres — przerwano, żeby nie wysyłać "
                      "tam klucza.", szczegoly)
    return BladOC("blad_roblox", "Roblox Open Cloud zwrócił błąd %d. Spróbuj ponownie za chwilę." % e.code, szczegoly)


def _wolno_zapytac():
    """Ogranicznik panelu: True i zapisanie żądania, gdy w ostatniej minucie było mniej niż ZAPYTAN_NA_MINUTE."""
    teraz = time.monotonic()
    with _blokada_zapytan:
        while _zapytania and teraz - _zapytania[0] >= 60:
            _zapytania.pop(0)
        if len(_zapytania) >= ZAPYTAN_NA_MINUTE:
            return False
        _zapytania.append(teraz)
        return True


def _zapytaj(url, klucz, zasob):
    """GET do Open Cloud → obiekt JSON albo None, gdy wpisu nie ma (404). Pozostałe błędy: BladOC po polsku."""
    if not _wolno_zapytac():
        raise BladOC("limit", "Panel wstrzymał odczyt telemetrii: w ostatniej minucie wysłał już %d zapytań do Roblox, "
                     "a ten budżet dzieli z zapisami graczy w grze. Spróbuj ponownie za minutę." % ZAPYTAN_NA_MINUTE)
    zadanie = urllib.request.Request(url, headers={"x-api-key": klucz, "Accept": "application/json",
                                                   "User-Agent": "bc-panel/%s" % rdzen.WERSJA})
    try:
        with _otworz(zadanie, LIMIT_CZASU_S) as odp:
            tresc = odp.read(LIMIT_ODPOWIEDZI + 1)
    except urllib.error.HTTPError as e:
        try:
            if e.code == 404:
                return None
            raise _blad_http(e, klucz, zasob)
        finally:
            e.close()
    except (urllib.error.URLError, OSError, http.client.HTTPException) as e:
        powod = _bez_klucza(str(getattr(e, "reason", None) or e), klucz)[:120]
        raise BladOC("siec", "Nie udało się połączyć z Roblox Open Cloud (%s)." % powod)
    if len(tresc) > LIMIT_ODPOWIEDZI:
        raise BladOC("blad_roblox", "Odpowiedź Roblox Open Cloud jest za duża, żeby ją bezpiecznie przeczytać.")
    try:
        return json.loads(tresc.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise BladOC("blad_roblox", "Roblox Open Cloud zwrócił odpowiedź, której nie da się odczytać.")


def _q(tekst):
    return urllib.parse.quote(str(tekst), safe="")


def _czytaj_wpis(ust, klucz, nazwa):
    """Wartość wpisu Data Store albo None, gdy wpisu nie ma."""
    url = "%s/cloud/v2/universes/%d/data-stores/%s/entries/%s" % (ust["adres"], ust["uid"], _q(ust["magazyn"]), _q(nazwa))
    obj = _zapytaj(url, klucz, "odczytu Data Store „%s” (operacja %s)" % (ust["magazyn"], UPRAWNIENIE_DANYCH))
    if obj is None:
        return None
    wartosc = obj.get("value") if isinstance(obj, dict) else None
    if isinstance(wartosc, str):                               # wartość zapisana jako tekst JSON
        try:
            wartosc = json.loads(wartosc)
        except ValueError:
            wartosc = None
    return wartosc if isinstance(wartosc, dict) else {}


def _czytaj_godziny(ust, klucz, poczatki, teraz):
    """Kubełki dla podanych godzin, równolegle → ({początek: kubełek}, ile godzin nie udało się pobrać)."""
    wynik, do_pobrania, nieudane, ostatni_blad = {}, [], 0, None
    for t in poczatki:
        zap = _godziny.get((ust["uid"], ust["magazyn"], t))
        if zap and teraz - zap[0] < PAMIEC_ZAMKNIETEJ_GODZINY_S and t + GODZINA_ZAMKNIETA_PO_S <= teraz:
            if zap[1] is not None:
                wynik[t] = zap[1]
        else:
            do_pobrania.append(t)
    if not do_pobrania:
        return wynik, 0
    if len(_godziny) > 4000:
        _godziny.clear()
    pula = concurrent.futures.ThreadPoolExecutor(max_workers=ROWNOLEGLE, thread_name_prefix="bc-telemetria")
    try:
        zadania = {pula.submit(_czytaj_wpis, ust, klucz, klucz_godziny(t)): t for t in do_pobrania}
        try:
            for z in concurrent.futures.as_completed(zadania, timeout=LIMIT_CALOSCI_S):
                t = zadania[z]
                try:
                    surowy = z.result()
                except BladOC as e:
                    if e.kod in ("klucz_odrzucony", "brak_uprawnien", "limit"):
                        raise                                  # kolejne godziny skończyłyby tak samo
                    nieudane, ostatni_blad = nieudane + 1, e
                    continue
                kubelek = normalizuj_kubelek(surowy, t) if surowy is not None else None
                if kubelek is not None:
                    wynik[t] = kubelek
                if t + GODZINA_ZAMKNIETA_PO_S <= teraz:
                    _godziny[(ust["uid"], ust["magazyn"], t)] = (teraz, kubelek)
        except concurrent.futures.TimeoutError:
            nieudane += sum(1 for z in zadania if not z.done())
            ostatni_blad = ostatni_blad or BladOC("siec", "Roblox Open Cloud odpowiada zbyt wolno (przekroczony czas).")
    finally:
        pula.shutdown(wait=False, cancel_futures=True)
    if nieudane and nieudane == len(do_pobrania):
        raise ostatni_blad                                     # nie przyszło nic: to awaria, a nie brak danych
    return wynik, nieudane


def _czytaj_serwery(ust, klucz, koniec=None):
    """Serwery na żywo z sorted mapy Memory Store → (lista, czy jest ich więcej, niż przeczytano).

    `koniec` (time.monotonic): po tej chwili nie prosimy o kolejną stronę — lista zostaje niepełna."""
    serwery, token = [], None
    for strona in range(STRON_SERWEROW):
        if strona and koniec is not None and time.monotonic() > koniec:
            break                                              # token zostaje: odpowiedź powie, że lista jest niepełna
        zapytanie = {"maxPageSize": "200", "orderBy": "desc"}
        if token:
            zapytanie["pageToken"] = token
        url = "%s/cloud/v2/universes/%d/memory-store/sorted-maps/%s/items?%s" % (
            ust["adres"], ust["uid"], _q(ust["mapa"]), urllib.parse.urlencode(zapytanie))
        obj = _zapytaj(url, klucz, "odczytu Memory Store (operacja %s)" % UPRAWNIENIE_SERWEROW)
        if not isinstance(obj, dict):
            break                                              # 404: mapy jeszcze nie ma — żaden serwer nie wystartował
        for wpis in obj.get("items") or []:
            s = normalizuj_serwer(wpis)
            if s:
                serwery.append(s)
        token = obj.get("nextPageToken")
        if not token:
            break
    return serwery, bool(token)


# --------------------------------------------------------------------------- normalizacja danych z gry
def _liczba(v, calkowita=True):
    """Liczba nieujemna; wszystko inne (tekst, NaN, nieskończoność, wartość ujemna) → 0."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return 0
    if v != v or v in (float("inf"), float("-inf")) or v < 0:
        return 0
    return int(v) if calkowita else float(v)


def _tekst(v, limit):
    if not isinstance(v, str):
        return ""
    return re.sub(r"[\x00-\x1f\x7f]+", " ", v).strip()[:limit]


def _slownik(v):
    """Słownik z gry; pusta tabela Luau przychodzi jako [] — też jest pustym słownikiem."""
    return v if isinstance(v, dict) else {}


def _wpisy(v):
    return [(str(k), w) for k, w in list(_slownik(v).items())[:LIMIT_KLUCZY]]


def normalizuj_kubelek(surowy, t=None):
    """Kubełek godzinowy z Data Store → słownik o znanych polach i typach. Nie rzuca dla żadnych danych."""
    s = _slownik(surowy)
    k = {pole: _liczba(s.get(pole)) for pole in POLA_LICZBOWE}
    k["t"] = int(t) if t is not None else _liczba(s.get("t"))
    minuty = s.get("ccu_minuty")
    k["ccu_minuty"] = [_liczba(x) for x in minuty[:60]] if isinstance(minuty, list) else []
    k["zakupy"] = {_tekst(i, 60): {"n": _liczba(w.get("n")), "robuxy": _liczba(w.get("robuxy")),
                                   "nazwa": _tekst(w.get("nazwa"), 80)}
                   for i, w in _wpisy(s.get("zakupy")) if isinstance(w, dict) and _tekst(i, 60)}
    k["bledy"] = {_tekst(i, 60): {"n": _liczba(w.get("n")), "komunikat": _tekst(w.get("komunikat"), 240)}
                  for i, w in _wpisy(s.get("bledy")) if isinstance(w, dict) and _tekst(i, 60)}
    k["lejek"] = {_tekst(i, 12): {"n": _liczba(w.get("n")), "nazwa": _tekst(w.get("nazwa"), 80)}
                  for i, w in _wpisy(s.get("lejek")) if isinstance(w, dict) and _tekst(i, 12)}
    for pole in ("zdarzenia", "dlugosci", "zamkniecia"):
        k[pole] = {_tekst(i, 60): _liczba(w, calkowita=False) for i, w in _wpisy(s.get(pole)) if _tekst(i, 60)}
    return k


def normalizuj_serwer(wpis):
    """Element sorted mapy Memory Store → {id, gracze, od, pamiec_mb?, fps?, bledy?} albo None."""
    if not isinstance(wpis, dict):
        return None
    v = wpis.get("value")
    if isinstance(v, str):
        try:
            v = json.loads(v)
        except ValueError:
            v = None
    if not isinstance(v, dict):
        return None
    ident = _tekst(str(wpis.get("id") or ""), 64)
    s = {"id": ident[:8] or "?", "gracze": _liczba(v.get("gracze")), "od": _iso_z_gry(v.get("od"))}
    if _liczba(v.get("pamiec_mb")):
        s["pamiec_mb"] = _liczba(v.get("pamiec_mb"))
    if _liczba(v.get("fps"), calkowita=False):
        s["fps"] = round(min(_liczba(v.get("fps"), calkowita=False), 1000.0), 1)
    if "bledy" in v:
        s["bledy"] = _liczba(v.get("bledy"))
    return s


# --------------------------------------------------------------------------- składanie odpowiedzi
def _dolicz(cel, klucz, wpis, pola_liczbowe, pole_tekstowe):
    obecny = cel.setdefault(klucz, dict({p: 0 for p in pola_liczbowe}, **{pole_tekstowe: ""}))
    for p in pola_liczbowe:
        obecny[p] += wpis[p]
    if wpis[pole_tekstowe]:
        obecny[pole_tekstowe] = wpis[pole_tekstowe]            # najnowsza niepusta nazwa


def zloz(kubelki, poczatki, serwery=None):
    """Kubełki godzinowe ({początek godziny: kubełek po normalizuj_kubelek}) → pola odpowiedzi API.

    `poczatki` wyznacza oś czasu: godzina bez kubełka to zera. `serwery` = lista po normalizuj_serwer albo None,
    gdy listy serwerów nie da się odczytać."""
    suma = {"sesje": 0, "sredni_czas_sesji_s": None, "ccu_max": 0, "robuxy": 0, "zakupy": 0, "bledy": 0}
    godziny, zakupy, bledy, lejek, zdarzenia, dlugosci, zamkniecia = [], {}, {}, {}, {}, {}, {}
    zakonczone = sekundy = starty = serwerogodziny = 0
    for t in poczatki:
        k = kubelki.get(t)
        if not k:
            godziny.append({"t": _iso(t), "sesje": 0, "ccu_max": 0, "robuxy": 0, "bledy": 0})
            continue
        # gracze naraz w całej grze = największa minuta (suma serwerów); ccu_max to szczyt jednego serwera
        ccu = max([k["ccu_max"]] + k["ccu_minuty"])
        ile_bledow = max(k["bledy_n"], sum(w["n"] for w in k["bledy"].values()))
        godziny.append({"t": _iso(t), "sesje": k["sesje"], "ccu_max": ccu, "robuxy": k["robuxy"], "bledy": ile_bledow})
        suma["sesje"] += k["sesje"]
        suma["robuxy"] += k["robuxy"]
        suma["bledy"] += ile_bledow
        suma["ccu_max"] = max(suma["ccu_max"], ccu)
        zakonczone += k["sesje_zakonczone"]
        sekundy += k["sekundy_gry"]
        starty += k["starty"]
        serwerogodziny += k["serwery"]
        for i, w in k["zakupy"].items():
            _dolicz(zakupy, i, w, ("n", "robuxy"), "nazwa")
        for i, w in k["bledy"].items():
            _dolicz(bledy, i, w, ("n",), "komunikat")
        for i, w in k["lejek"].items():
            _dolicz(lejek, i, w, ("n",), "nazwa")
        for cel, pole in ((zdarzenia, "zdarzenia"), (dlugosci, "dlugosci"), (zamkniecia, "zamkniecia")):
            for i, w in k[pole].items():
                cel[i] = cel.get(i, 0) + w
    if zakonczone:
        suma["sredni_czas_sesji_s"] = int(round(sekundy / zakonczone))
    suma["zakupy"] = sum(w["n"] for w in zakupy.values())
    suma["sesje_zakonczone"] = zakonczone
    suma["sesje_ponizej_minuty"] = int(dlugosci.get("do_1", 0))
    suma["serwerogodziny"] = serwerogodziny
    suma["serwery_start"] = starty
    suma["serwery_koniec"] = int(sum(zamkniecia.values()))
    suma["brak_pamieci"] = int(zamkniecia.get("OutOfMemory", 0))
    # serwery, które wystartowały i nie zapisały zamknięcia, a nie ma ich na liście żywych: możliwe awarie
    suma["niedomkniete"] = (max(0, starty - suma["serwery_koniec"] - len(serwery)) if serwery is not None else None)
    suma["serwery_teraz"] = len(serwery) if serwery is not None else None
    suma["gracze_teraz"] = sum(s["gracze"] for s in serwery) if serwery is not None else None

    def ostatnie_inne(x):
        return x == INNE

    lista_zakupow = [{"id": i, "nazwa": w["nazwa"] or ("Pozostałe produkty" if i == INNE else "Produkt %s" % i),
                      "n": w["n"], "robuxy": w["robuxy"]} for i, w in zakupy.items()]
    lista_zakupow.sort(key=lambda x: (ostatnie_inne(x["id"]), -x["robuxy"], -x["n"], x["id"]))
    lista_bledow = [{"sygnatura": i, "n": w["n"],
                     "komunikat": w["komunikat"] or ("Pozostałe błędy (bez treści)" if i == INNE else "(bez treści)")}
                    for i, w in bledy.items()]
    lista_bledow.sort(key=lambda x: (ostatnie_inne(x["sygnatura"]), -x["n"], x["sygnatura"]))
    lista_lejka = [{"krok": int(i), "nazwa": w["nazwa"], "n": w["n"]} for i, w in lejek.items() if WZOR_KROKU.match(i)]
    lista_lejka.sort(key=lambda x: x["krok"])
    lista_zdarzen = [{"nazwa": i, "n": int(w) if float(w).is_integer() else round(w, 2)} for i, w in zdarzenia.items()]
    lista_zdarzen.sort(key=lambda x: (ostatnie_inne(x["nazwa"]), -x["n"], x["nazwa"]))
    lista_serwerow = sorted(serwery or [], key=lambda s: (-s["gracze"], s["id"]))
    return {"suma": suma, "godziny": godziny, "zakupy": lista_zakupow[:NA_LISCIE], "bledy": lista_bledow[:NA_LISCIE],
            "serwery": lista_serwerow[:SERWEROW_NA_LISCIE], "lejek": lista_lejka, "zdarzenia": lista_zdarzen[:NA_LISCIE],
            "dlugosci_sesji": {i: int(w) for i, w in dlugosci.items()}}


def _okres(poczatki, teraz):
    return {"od": _iso(poczatki[0]), "do": _iso(teraz), "godzin": len(poczatki)}


# --------------------------------------------------------------------------- dane przykładowe
PRODUKTY_PRZYKLADOWE = (("1000001", "Worek złota", 49), ("1000002", "Jajo peta", 99),
                        ("1000003", "Skrzynia klejnotów", 199), ("1000004", "Przepustka sezonu", 399))
BLEDY_PRZYKLADOWE = (("3f2a9c1e", "ServerScriptService.Server.Walka:42: attempt to index nil with 'Zdrowie'"),
                     ("a81d07b2", "ServerScriptService.Server.Karczma:118: zadanie <n> nie istnieje"),
                     ("5c44e9f0", "ServerScriptService.Server.Pety:77: invalid argument #1 to 'insert' (table expected, got nil)"),
                     ("0be7d313", "ServerScriptService.Server.Sklep:203: attempt to compare number < nil"))


def kubelki_przykladowe(poczatki, teraz):
    """Kubełki w formacie zapisywanym przez grę (surowe), wymyślone, ale powtarzalne dla danej godziny."""
    wynik = {}
    for t in poczatki:
        los = random.Random(int(t) // 3600)
        godzina = datetime.datetime.fromtimestamp(t).hour
        dzien = math.sin(max(0.0, min(1.0, (godzina - 7) / 16.0)) * math.pi) ** 1.4      # szczyt po południu
        czesc = max(0.05, min(1.0, (teraz - t) / 3600.0))                                # bieżąca godzina jest niepełna
        gracze = int(round(3 + 44 * dzien * (0.8 + 0.4 * los.random())))
        serwery = max(1, -(-gracze // 12))
        sesje = int(round(gracze * (1.6 + 0.8 * los.random()) * czesc))
        zakonczone = int(sesje * 0.9)
        zakupy = {}
        for id_, nazwa, cena in PRODUKTY_PRZYKLADOWE:
            n = int(sesje * los.random() * 0.07 * (120.0 / (cena + 60)))
            if n:
                zakupy[id_] = {"n": n, "robuxy": n * cena, "nazwa": nazwa}
        bledy = {}
        for i, (sygnatura, komunikat) in enumerate(BLEDY_PRZYKLADOWE):
            n = int(max(0.0, los.random() - 0.5 - 0.1 * i) * 5 * czesc * (0.3 + gracze / 25.0))
            if n:
                bledy[sygnatura] = {"n": n, "komunikat": komunikat}
        minuty = [max(0, int(round(gracze * (0.85 + 0.3 * los.random())))) for _ in range(60)]
        minuty = minuty[:max(1, int(60 * czesc))] + [0] * (60 - max(1, int(60 * czesc)))
        # serwery: ile wystartowało, tyle się zamknęło (licznik „możliwych awarii” zostaje przy zera); raz na dobę
        # (14:00 UTC) jedno zamknięcie z braku pamięci — żeby było widać, jak wygląda awaria
        starty = 1 if los.random() < 0.35 else 0
        zamkniecia = {"ServerEmpty": starty} if starty else {}
        if int(t) // 3600 % 24 == 14:
            starty, zamkniecia = starty + 1, dict(zamkniecia, OutOfMemory=1)
        wynik[t] = {
            "wersja": 1, "t": t, "zaktualizowano": min(teraz, t + 3599), "serwery": serwery, "zapisy": 12 * serwery,
            "starty": starty, "sesje": sesje, "sesje_zakonczone": zakonczone,
            "sekundy_gry": int(zakonczone * (420 + 600 * los.random())),
            "dlugosci": {"do_1": int(zakonczone * 0.14), "do_5": int(zakonczone * 0.27), "do_15": int(zakonczone * 0.31),
                         "do_30": int(zakonczone * 0.18), "do_60": int(zakonczone * 0.08), "ponad_60": int(zakonczone * 0.02)},
            "ccu_max": min(12, gracze), "ccu_suma": sum(minuty), "ccu_probki": 60 * serwery, "ccu_minuty": minuty,
            "robuxy": sum(z["robuxy"] for z in zakupy.values()), "zakupy": zakupy,
            "bledy_n": sum(b["n"] for b in bledy.values()), "bledy": bledy,
            "zdarzenia": {"quest_ukonczony": int(sesje * 2.4), "pet_wykluty": int(sesje * 0.3)},
            "lejek": {"1": {"n": sesje, "nazwa": "Wejście do gry"}, "2": {"n": int(sesje * 0.82), "nazwa": "Wybór bohatera"},
                      "3": {"n": int(sesje * 0.64), "nazwa": "Pierwsza walka"}},
            "zamkniecia": zamkniecia,
        }
    return wynik


def serwery_przykladowe(teraz, gracze=23):
    """Wpisy sorted mapy „na żywo” (surowe, jak z Open Cloud): `gracze` rozłożeni na serwery po najwyżej 12 osób,
    żeby „gracze teraz” zgadzało się z wykresem godzinowym danych przykładowych."""
    surowe = [("7c1e5a90-3b1f-4c0e-9a51-0d6f2b8e1a11", 5 * 3600 + 720, 1412, 59.8, 3),
              ("e04b77d2-91aa-4f6d-8c3e-5a2d90c4b7f3", 2 * 3600 + 95, 1188, 60.0, 0),
              ("19fd3c6b-0a44-4e8a-b7d1-c2e8f5a6d0b9", 1260, 1034, 60.0, 1),
              ("5a0e2c71-6d84-4b19-a3f2-8e7c1d9b4a60", 640, 980, 60.0, 0)]
    gracze = max(1, int(gracze))
    ile = max(1, min(len(surowe), -(-gracze // 12)))
    podzial = [gracze // ile + (1 if i < gracze % ile else 0) for i in range(ile)]
    return [{"id": i, "expireTime": None,
             "value": {"gracze": g, "od": int(teraz) - wiek, "t": int(teraz) - 20, "pamiec_mb": mb, "fps": fps, "bledy": b}}
            for (i, wiek, mb, fps, b), g in zip(surowe, podzial)]


def probka(godzin, teraz=None):
    """Odpowiedź z danymi przykładowymi — przechodzi przez tę samą normalizację i składanie co dane z gry."""
    teraz = int(teraz if teraz is not None else time.time())
    poczatki = poczatki_godzin(godzin, teraz)
    kubelki = {t: normalizuj_kubelek(k, t) for t, k in kubelki_przykladowe(poczatki, teraz).items()}
    minuty = [n for n in kubelki[poczatki[-1]]["ccu_minuty"] if n]       # gracze w ostatniej minucie bieżącej godziny
    serwery = [s for s in (normalizuj_serwer(w) for w in serwery_przykladowe(teraz, minuty[-1] if minuty else 1)) if s]
    wynik = {"wlaczona": False, "zrodlo": "probka", "kod": "probka", "przykladowe": True,
             "powod": "To są dane przykładowe: pokazują, jak będzie wyglądać telemetria po włączeniu. Nie pochodzą z gry.",
             "okres": _okres(poczatki, teraz), "zaktualizowano": rdzen.teraz()}
    wynik.update(zloz(kubelki, poczatki, serwery))
    return wynik


# --------------------------------------------------------------------------- stan telemetrii
def _wylaczona(kod, powod, klucz=False, modul=None, chwilowe=False):
    """Odpowiedź „telemetria nie działa”: powód po polsku i stan trzech kroków włączenia."""
    wynik = {"wlaczona": False, "zrodlo": None, "kod": kod, "powod": powod,
             "kroki": {"modul": modul, "klucz": bool(klucz)}}
    if chwilowe:
        wynik["chwilowe"] = True                               # awaria sieci / limit, a nie brak konfiguracji
    return wynik


def _odczytaj(ust, klucz, godzin, teraz):
    """Pełny odczyt z Open Cloud: ślad modułu, kubełki godzinowe, serwery na żywo. Rzuca BladOC."""
    start = time.monotonic()
    stan = _czytaj_wpis(ust, klucz, WPIS_STANU)
    if stan is None:
        return _wylaczona("modul_wylaczony", "Klucz działa, ale gra nie zapisała jeszcze żadnych danych: moduł telemetrii "
                          "nie jest włączony w grze albo od włączenia nie wystartował żaden serwer (poza Studio).",
                          klucz=True, modul=False)
    poczatki = poczatki_godzin(godzin, teraz)
    kubelki, nieudane = _czytaj_godziny(ust, klucz, poczatki, teraz)
    uwagi, serwery = [], None
    if nieudane:
        uwagi.append("Nie udało się pobrać %d z %d godzin — liczby mogą być zaniżone." % (nieudane, len(poczatki)))
    try:
        if time.monotonic() - start > LIMIT_CALOSCI_S:         # nie każemy czekać dłużej, niż czeka przeglądarka
            raise BladOC("siec", "Roblox Open Cloud odpowiada zbyt wolno.")
        serwery, wiecej = _czytaj_serwery(ust, klucz, koniec=start + LIMIT_CALOSCI_S)
        if wiecej:
            uwagi.append("Lista serwerów na żywo jest niepełna (panel czyta najwyżej %d serwerów i nie czeka na Roblox "
                         "dłużej niż %d s) — liczba graczy teraz może być zaniżona." % (STRON_SERWEROW * 200, LIMIT_CALOSCI_S))
    except BladOC as e:
        if e.kod == "brak_uprawnien":
            uwagi.append("Lista serwerów na żywo jest niedostępna: klucz nie ma uprawnienia %s." % UPRAWNIENIE_SERWEROW)
        else:
            uwagi.append("Lista serwerów na żywo jest chwilowo niedostępna. " + e.komunikat)
    wynik = {"wlaczona": True, "zrodlo": "open_cloud", "okres": _okres(poczatki, teraz), "zaktualizowano": rdzen.teraz(),
             "modul": {"wersja": _liczba(stan.get("wersja")), "starty": _liczba(stan.get("starty")),
                       "pierwszy_start": _iso_z_gry(stan.get("pierwszy_start")),
                       "ostatni_start": _iso_z_gry(stan.get("ostatni_start"))}}
    wynik.update(zloz(kubelki, poczatki, serwery))
    if uwagi:
        wynik["uwagi"] = uwagi
    return wynik


def stan_telemetrii(godzin=GODZIN_DOMYSLNIE, odswiez=False, teraz=None):
    """Odpowiedź trasy /api/telemetria (bez danych przykładowych). Nigdy nie rzuca i nigdy nie zwraca klucza.

    Pole `szczegoly` (dosłowny komunikat Roblox przy błędzie) jest tylko dla osoby przy komputerze — trasa usuwa je
    z odpowiedzi dla połączeń zdalnych."""
    teraz = int(teraz if teraz is not None else time.time())
    ust = ustawienia()
    klucz, _skad = klucz_open_cloud()
    if not ust["uid"]:
        return _wylaczona("brak_universe", "Brak universeId gry w panel/konfiguracja.json — bez niego panel nie wie, "
                          "której gry dotyczy telemetria.", klucz=bool(klucz))
    if not klucz:
        return _wylaczona("brak_klucza", "Brak klucza Open Cloud na tym komputerze. Telemetria czeka na włączenie: moduł "
                          "w grze, klucz tylko do odczytu i wpisanie go lokalnie.")
    if not WZOR_KLUCZA.match(klucz):
        return _wylaczona("klucz_odrzucony", "Wpisany klucz Open Cloud jest za krótki albo ma niedozwolone znaki (spacje, "
                          "polskie litery). Skopiuj go jeszcze raz z Creator Dashboard.", klucz=True)
    gdzie = (ust["uid"], ust["magazyn"], godzin)
    with _blokada:
        zap = _pamiec.get(gdzie)
        if zap:
            wiek = time.time() - zap["t"]
            swieze = wiek < (PAMIEC_S if zap["dobry"] else PAMIEC_BLEDU_S)
            if swieze and not (odswiez and wiek >= 30):
                return dict(zap["wynik"])
        try:
            wynik = _odczytaj(ust, klucz, godzin, teraz)
            dobry = bool(wynik.get("wlaczona"))
        except BladOC as e:
            rdzen.log("Telemetria: odczyt z Open Cloud nieudany (%s): %s" % (e.kod, _bez_klucza(e.komunikat, klucz)))
            _ostatni.update(t=rdzen.teraz(), kod=e.kod)
            chwilowe = e.kod in ("siec", "limit", "blad_roblox")
            if chwilowe and zap and zap["dobry"]:              # pokaż ostatnie dobre dane z adnotacją
                wynik = dict(zap["wynik"], nieaktualne=True,
                             blad=e.komunikat + " Pokazuję dane z poprzedniego odczytu.")
                _pamiec[gdzie] = {"t": time.time() - PAMIEC_S + PAMIEC_BLEDU_S, "wynik": wynik, "dobry": True}
                return dict(wynik)
            wynik = _wylaczona(e.kod, e.komunikat, klucz=True, chwilowe=chwilowe)
            if e.szczegoly:
                wynik["szczegoly"] = e.szczegoly
            _pamiec[gdzie] = {"t": time.time(), "wynik": wynik, "dobry": False}
            return dict(wynik)
        except Exception as e:                                 # błąd w naszym kodzie nie może wywrócić widoku
            rdzen.log("Telemetria: nieoczekiwany błąd odczytu: %s" % _bez_klucza(repr(e), klucz)[:300])
            _ostatni.update(t=rdzen.teraz(), kod="blad_panelu")
            return _wylaczona("blad_panelu", "Panel nie poradził sobie z odczytem telemetrii (szczegóły w logu panelu).",
                              klucz=True, chwilowe=True)
        _ostatni.update(t=rdzen.teraz(), kod="ok" if dobry else wynik.get("kod"))
        _pamiec[gdzie] = {"t": time.time(), "wynik": wynik, "dobry": dobry}
        if len(_pamiec) > 40:
            for stary in sorted(_pamiec, key=lambda g: _pamiec[g]["t"])[:20]:
                _pamiec.pop(stary, None)
        return dict(wynik)


# --------------------------------------------------------------------------- trasy
def _telemetria(z):
    godzin = z.q_int("godzin", GODZIN_DOMYSLNIE, 1, GODZIN_MAX)
    if str(z.q("probka") or "") in ("1", "true", "tak"):
        if not z.lokalny:
            raise BladHTTP(403, "Dane przykładowe pokazuje tylko panel otwarty na komputerze, na którym działa.")
        return probka(godzin)
    wynik = stan_telemetrii(godzin, odswiez=z.lokalny and z.q("odswiez") == "1")
    if not z.lokalny:
        wynik.pop("szczegoly", None)                           # dosłowna odpowiedź Roblox: tylko dla osoby przy komputerze
    elif not wynik.get("wlaczona"):
        wynik["plik_konfiguracji"] = rdzen.PLIK_KONFIGURACJI_LOKALNEJ   # gdzie wpisać klucz (ścieżka tego komputera)
    return wynik


def zarejestruj(app):
    app.dodaj("GET", "/api/telemetria", _telemetria)


def zdrowie():
    klucz, skad = klucz_open_cloud()
    ust = ustawienia()
    return {"klucz_open_cloud": bool(klucz), "skad_klucz": skad, "universeId": ust["uid"], "magazyn": ust["magazyn"],
            "ostatni_odczyt": _ostatni["t"], "ostatni_wynik": _ostatni["kod"]}
