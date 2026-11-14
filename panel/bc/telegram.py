# -*- coding: utf-8 -*-
"""Bot Telegram: alert o decyzji i potwierdzenie przez drugą osobę (decyzja D-043).

Jedna osoba zatwierdza albo odrzuca decyzję w panelu, druga dostaje na Telegramie wiadomość z trzema przyciskami:
Zgoda, Brak zgody, Przedyskutuj. Odpowiedź idzie przez tę samą funkcję co w panelu (bc/zapis.py:
`potwierdz_decyzje`) — ta sama blokada sejfu, zapis atomowy jednej linii w Rejestrze decyzji i ślad w Dzienniku zmian
z dopiskiem „przez Telegram”. Format pól w wierszu statusu opisuje bc/sejf.py („potwierdzanie decyzji”).

Ustawienia bota: plik `telegram.json` w danych lokalnych panelu (rdzen.RUNTIME, poza repozytorium):
    {"token": "<token od BotFather>", "bot": "nazwa_bota",
     "osoby": {"<liczbowe id użytkownika>": "Karol", …}, "grupy": {"<liczbowe id czatu grupy>": "tytuł", …}}
Plik jest czytany przy starcie i po każdej zmianie (czas modyfikacji). Brak pliku albo tokenu = Telegram wyłączony;
panel działa dalej, a potwierdzanie w samym panelu działa bez bota.

Bezpieczeństwo:
- token nigdy nie trafia do logu, odpowiedzi API ani komunikatu błędu (`_bez_tokenu`; adres z tokenem składa tylko
  `_wywolaj` i nie wychodzi poza tę funkcję);
- adres API to stała API_TELEGRAMA; test podaje adres atrapy jawnym parametrem (`Bot(api=…)`) albo zmienną
  BC_TELEGRAM_API_TESTOWE czytaną WYŁĄCZNIE razem z BC_TELEGRAM_TRYB_TESTOWY=1 — w zwykłej pracy bota nie da się
  przekierować;
- bot przyjmuje tylko kliknięcia i komendy z czatów z listy „grupy” oraz z rozmów prywatnych osób z listy „osoby”;
  resztę pomija. Nieznana osoba w znanej grupie dostaje tylko komunikat, nic nie zmienia w sejfie;
- dane przycisku (callback_data) to `p:D-019:z:<8 hex>` (akcja z zamkniętej listy z / n / r i odcisk stanu decyzji)
  albo `c:<liczba>` (strona listy /czeka) — sprawdzane wzorcem; nic z nich nie trafia do ścieżek ani poleceń;
- wysyłka idzie w tle (kolejka i wątek): błąd sieci nie psuje zapisu decyzji — alert czeka w danych lokalnych
  (`telegram_stan.json`: `zalegle`) i idzie przy następnym udanym połączeniu albo po komendzie /czeka;
- odbiór: jeden wątek z długim odpytywaniem getUpdates; numer ostatniej aktualizacji (`offset`) jest zapamiętany
  w danych lokalnych, więc po restarcie nic nie jest przetwarzane dwa razy. Tylko jeden komputer może mieć plik
  z tokenem (dwa panele na jednym bocie = błąd 409 od Telegrama, opisany w stanie bota).

Komendy (w grupie i prywatnie): /czeka — decyzje, które czekają na potwierdzenie piszącego (po jednej wiadomości
z przyciskami, najwyżej 5 naraz, przycisk „Następne”); /pomoc — krótki opis; /start — czy bot zna tę osobę.
Brak zgody: bot prosi o krótki powód; odpowiedź na tę wiadomość w ciągu 15 minut trafia do wiersza
„Uzasadnienie sprzeciwu — Imię, data: …” (zapis.dopisz_powod_sprzeciwu).
"""
import html
import json
import os
import queue
import re
import threading
import time
import urllib.error
import urllib.request

from . import rdzen, sejf, zapis
from .rdzen import BladHTTP

API_TELEGRAMA = "https://api.telegram.org"
ZMIENNA_TRYBU_TESTOWEGO = "BC_TELEGRAM_TRYB_TESTOWY"
ZMIENNA_ADRESU_TESTOWEGO = "BC_TELEGRAM_API_TESTOWE"
PLIK_USTAWIEN = "telegram.json"
PLIK_STANU = "telegram_stan.json"
CZAS_ODPYTYWANIA_S = 25                                        # długie odpytywanie getUpdates
CZAS_NA_POWOD_S = 15 * 60
NA_RAZ = 5                                                     # /czeka: najwyżej tyle wiadomości naraz
PONOWIENIE_CO_S = 60
LIMIT_UZASADNIENIA_W_ALERCIE = 600

AKCJE = {"z": "zgoda", "n": "sprzeciw", "r": "rozmowa"}
NAPISY_AKCJI = {"zgoda": "zgoda", "sprzeciw": "brak zgody", "rozmowa": "do rozmowy na sesji głównej"}
RX_DANE_PRZYCISKU = re.compile(r"^p:(D-\d{1,4}):([znr]):([0-9a-f]{8})$")
RX_DANE_NASTEPNE = re.compile(r"^c:(\d{1,3})$")
RX_TOKEN = re.compile(r"^\d{3,20}:[A-Za-z0-9_-]{20,100}$")
RX_NAZWA_BOTA = re.compile(r"^[A-Za-z0-9_]{3,64}$")
_RX_UZASADNIENIE = re.compile(r"^\s*Uzasadnienie\s+—\s+([^,:\n]{1,60}),\s*(\d{4}-\d{2}-\d{2})\s*:\s*(.+?)\s*$")


# =========================================================================== ustawienia (telegram.json)
_ust_pamiec = {"stan": None, "dane": None}
_ust_lock = threading.Lock()


def _plik_ustawien():
    return os.path.join(rdzen.RUNTIME, PLIK_USTAWIEN)


def _plik_stanu():
    return os.path.join(rdzen.RUNTIME, PLIK_STANU)


def _czyste_imie(t):
    t = re.sub(r"[\x00-\x1f\x7f*_\[\]#`|<>:()·,]", "", str(t or "")).strip()
    return re.sub(r"\s{2,}", " ", t)[:40].strip()


def _identyfikatory(slownik, ujemne_tylko=False):
    wynik = {}
    if not isinstance(slownik, dict):
        return wynik
    for k, v in slownik.items():
        try:
            n = int(str(k).strip())
        except ValueError:
            continue
        if ujemne_tylko and n >= 0:                            # grupy w Telegramie mają ujemne numery czatów
            continue
        wynik[n] = _czyste_imie(v) if not ujemne_tylko else str(v or "")[:80]
    return wynik


def ustawienia():
    """{wlaczony, token, bot, osoby:{id: imię}, grupy:{id: tytuł}, blad} — z pamięcią po czasie zmiany pliku.
    Brak pliku albo tokenu = wyłączony (osoby i tak służą do rozpoznania zespołu)."""
    p = _plik_ustawien()
    try:
        st = os.stat(p)
        stan = (st.st_mtime_ns, st.st_size)
    except OSError:
        stan = None
    with _ust_lock:
        if _ust_pamiec["dane"] is not None and _ust_pamiec["stan"] == stan:
            return _ust_pamiec["dane"]
        wynik = {"wlaczony": False, "token": None, "bot": "", "osoby": {}, "grupy": {}, "blad": None}
        if stan is not None:
            d = rdzen.czytaj_json(p, None)
            if not isinstance(d, dict):
                wynik["blad"] = "Plik ustawień bota nie jest poprawnym JSON-em."
            else:
                token = str(d.get("token") or "").strip()
                if token and not RX_TOKEN.match(token):
                    wynik["blad"] = "Token bota ma zły format (oczekiwano liczba:ciąg znaków od BotFathera)."
                    token = ""
                bot = str(d.get("bot") or "").strip().lstrip("@")
                wynik.update(token=token or None, wlaczony=bool(token),
                             bot=bot if RX_NAZWA_BOTA.match(bot) else "",
                             osoby={k: v for k, v in _identyfikatory(d.get("osoby")).items() if v},
                             grupy=_identyfikatory(d.get("grupy"), ujemne_tylko=True))
        _ust_pamiec.update(stan=stan, dane=wynik)
        return wynik


def imiona_osob():
    """Imiona osób z ustawień bota (do rozpoznania zespołu w bc/sejf.py)."""
    return [v for v in ustawienia()["osoby"].values() if v]


def adres_api(api=None):
    """Adres API: stała, albo jawny parametr (testy), albo zmienna testowa — tylko w trybie testowym."""
    if api:
        return str(api).rstrip("/")
    if os.environ.get(ZMIENNA_TRYBU_TESTOWEGO) == "1" and os.environ.get(ZMIENNA_ADRESU_TESTOWEGO):
        return os.environ[ZMIENNA_ADRESU_TESTOWEGO].rstrip("/")
    return API_TELEGRAMA


def _bez_tokenu(tekst, token=None):
    t = str(tekst or "")
    if token:
        t = t.replace(token, "***")
    return re.sub(r"\d{3,20}:[A-Za-z0-9_-]{20,100}", "***", t)


class BladTelegrama(Exception):
    """Błąd rozmowy z Telegramem — komunikat bez tokenu i bez szczegółów sieci."""

    def __init__(self, komunikat, kod=None):
        super().__init__(komunikat)
        self.komunikat = komunikat
        self.kod = kod


# =========================================================================== stan lokalny (offset, alerty, zaległe)
_stan_lock = threading.Lock()


def _zmien_stan(fn):
    """Odczyt → zmiana → zapis stanu bota pod blokadą. `fn(stan)` zmienia słownik w miejscu i może coś zwrócić."""
    with _stan_lock:
        stan = rdzen.czytaj_json(_plik_stanu(), {}) or {}
        if not isinstance(stan, dict):
            stan = {}
        wynik = fn(stan)
        try:
            rdzen.zapisz_json(_plik_stanu(), stan)
        except OSError as e:
            rdzen.log("telegram: nie udało się zapisać stanu bota (%s)" % e.__class__.__name__)
        return wynik


def _czytaj_stan():
    with _stan_lock:
        stan = rdzen.czytaj_json(_plik_stanu(), {}) or {}
        return stan if isinstance(stan, dict) else {}


# =========================================================================== decyzje z planu
def _decyzje():
    return [d for d in (sejf.plan().get("decyzje") or []) if isinstance(d, dict)]


def _decyzja(ident):
    n = int(ident[2:])
    return next((d for d in _decyzje() if re.match(r"^D-\d+$", d.get("id") or "") and int(d["id"][2:]) == n), None)


def _odcisk(d):
    pola = {"zdecydowal": d.get("zdecydowal")}
    return sejf.odcisk_decyzji(d["id"], d.get("status"), pola)


def czekajace_na(kto):
    """Decyzje, które czekają na potwierdzenie tej osoby (kolejność z Rejestru)."""
    k = sejf.kanoniczne(kto)
    return [d for d in _decyzje() if d.get("czeka_na") and sejf.kanoniczne(d["czeka_na"]) == k] if k else []


def _ostatnie_uzasadnienie(d):
    """Ostatnie „Uzasadnienie — Imię, data: …” osoby, która zdecydowała (do alertu), skrócone."""
    kto = sejf.kanoniczne((d.get("zdecydowal") or {}).get("kto"))
    ostatnie = None
    for linia in (d.get("opis_md") or "").split("\n"):
        m = _RX_UZASADNIENIE.match(linia)
        if m and sejf.kanoniczne(m.group(1)) == kto:
            ostatnie = m.group(3)
    if ostatnie and len(ostatnie) > LIMIT_UZASADNIENIA_W_ALERCIE:
        ostatnie = ostatnie[:LIMIT_UZASADNIENIA_W_ALERCIE - 1].rsplit(" ", 1)[0] + "…"
    return ostatnie


def _zwykly(t):
    t = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", str(t or ""))
    t = re.sub(r"\[\[([^\]]+)\]\]", r"\1", t)
    return re.sub(r"\s+", " ", re.sub(r"[`*_]", "", t)).strip()


def tresc_pytania(d, ustaw, html_tak=True):
    """Treść wiadomości z pytaniem do drugiej osoby (HTML Telegrama, wszystko z sejfu jest escapowane)."""
    e = html.escape if html_tak else (lambda s: s)
    zd = d.get("zdecydowal") or {}
    czyn = "zatwierdził" if d.get("status") == "zatwierdzona" else "odrzucił"
    linie = ["%s %s decyzję %s" % (e(zd.get("kto") or "?"), czyn, e(d["id"])),
             "„%s”" % e(_zwykly(d.get("tytul")) or d["id"])]
    uz = _ostatnie_uzasadnienie(d)
    if uz:
        linie.append("Uzasadnienie: " + e(_zwykly(uz)))
    kto = d.get("czeka_na") or ""
    uid = next((i for i, v in ustaw["osoby"].items() if sejf.kanoniczne(v) == sejf.kanoniczne(kto)), None)
    wolany = ('<a href="tg://user?id=%d">%s</a>' % (uid, e(kto))) if (uid and html_tak) else e(kto)
    linie.append("")
    linie.append("%s, zgadzasz się?" % wolany)
    linie.append("Z jednym podpisem to robocze ustalenie — obowiązuje po Twojej zgodzie.")
    return "\n".join(linie)


def przyciski(d):
    odc = _odcisk(d)
    dane = lambda a: "p:%s:%s:%s" % (d["id"], a, odc)            # noqa: E731
    return {"inline_keyboard": [[{"text": "✅ Zgoda", "callback_data": dane("z")},
                                 {"text": "❌ Brak zgody", "callback_data": dane("n")}],
                                [{"text": "💬 Przedyskutuj", "callback_data": dane("r")}]]}


# =========================================================================== bot
class Bot:
    """Wysyłka (kolejka w tle) i odbiór (długie odpytywanie). `api` = adres atrapy w testach; `synchronicznie=True`
    (testy) wykonuje zadania od razu, bez wątku wysyłki."""

    def __init__(self, api=None, synchronicznie=False):
        self.api = api
        self.synchronicznie = synchronicznie
        self._kolejka = queue.Queue()
        self._powody = {}                                      # (czat, osoba) -> {"id", "do", "wiadomosci"}
        self._stop = threading.Event()
        self._watki = []
        self.ostatni_blad = None
        self.ostatni_kontakt = None
        self.odbior_dziala = False
        self._ostatnie_ponowienie = 0.0
        self._offset = None                                    # ostatni offset getUpdates (pamięć; plik = zapas)

    # ------------------------------------------------------------------ rozmowa z API
    def _wywolaj(self, metoda, pola, czas=15, ustaw=None):
        ustaw = ustaw or ustawienia()
        token = ustaw.get("token")
        if not token:
            raise BladTelegrama("Telegram jest wyłączony (brak tokenu w ustawieniach bota).")
        adres = "%s/bot%s/%s" % (adres_api(self.api), token, metoda)
        req = urllib.request.Request(adres, data=json.dumps(pola, ensure_ascii=False).encode("utf-8"), method="POST",
                                     headers={"Content-Type": "application/json; charset=utf-8"})
        odp = None
        try:
            with urllib.request.urlopen(req, timeout=czas) as r:
                odp = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            kod = e.code
            try:
                odp = json.loads(e.read().decode("utf-8"))
            except Exception:
                odp = None
            opis = _bez_tokenu((odp or {}).get("description") or "", token)[:120]
            raise BladTelegrama("Telegram odrzucił „%s” (kod %d%s)." % (metoda, kod, (": " + opis) if opis else ""),
                                kod=kod) from None
        except (urllib.error.URLError, OSError, ValueError):
            raise BladTelegrama("Brak połączenia z Telegramem.") from None
        if not isinstance(odp, dict) or not odp.get("ok"):
            opis = _bez_tokenu((odp or {}).get("description") or "", token)[:120] if isinstance(odp, dict) else ""
            raise BladTelegrama("Telegram nie przyjął „%s”%s." % (metoda, (": " + opis) if opis else ""))
        self.ostatni_kontakt = rdzen.teraz()
        return odp.get("result")

    def _blad(self, e):
        self.ostatni_blad = {"tekst": getattr(e, "komunikat", None) or "Błąd bota Telegram.", "kiedy": rdzen.teraz()}
        rdzen.log("telegram: %s" % self.ostatni_blad["tekst"])

    def _wyslij(self, czat, tekst, klawiatura=None, html_tak=True, odpowiedz_na=None, wymus_odpowiedz=False):
        pola = {"chat_id": czat, "text": tekst[:4000], "disable_web_page_preview": True}
        if html_tak:
            pola["parse_mode"] = "HTML"
        if klawiatura:
            pola["reply_markup"] = klawiatura
        elif wymus_odpowiedz:
            pola["reply_markup"] = {"force_reply": True, "selective": True}
        if odpowiedz_na:
            pola["reply_to_message_id"] = odpowiedz_na
            pola["allow_sending_without_reply"] = True
        return self._wywolaj("sendMessage", pola)

    def _odpowiedz_klik(self, klik, tekst, alert=False):
        try:
            self._wywolaj("answerCallbackQuery", {"callback_query_id": str(klik.get("id") or ""), "text": tekst[:190],
                                                  "show_alert": bool(alert)})
        except BladTelegrama as e:
            self._blad(e)

    def _zmien_wiadomosc(self, czat, wiadomosc, tekst):
        """Nowa treść wiadomości bez przycisków (zwykły tekst). Wiadomość niezmieniona albo usunięta — bez błędu."""
        try:
            self._wywolaj("editMessageText", {"chat_id": czat, "message_id": wiadomosc, "text": tekst[:4000],
                                              "disable_web_page_preview": True})
        except BladTelegrama as e:
            if e.kod != 400:                                   # 400: treść ta sama albo wiadomości już nie ma
                self._blad(e)

    # ------------------------------------------------------------------ zdarzenia z zapisu (panel i Telegram)
    def zdarzenie(self, z):
        """Słuchacz bc/zapis.py — tylko wrzuca zadanie do kolejki (nigdy nie blokuje zapisu)."""
        if not isinstance(z, dict) or not re.match(r"^D-\d{1,4}$", str(z.get("id") or "")):
            return
        if self.synchronicznie:
            self._zadanie(z)
        else:
            self._kolejka.put(z)

    def _zadanie(self, z):
        ustaw = ustawienia()
        if not ustaw["wlaczony"]:
            return
        try:
            if z.get("typ") == "status":
                self._zamknij_alerty(z["id"], "Decyzja zmieniła się w panelu — to pytanie jest już nieaktualne.",
                                     tylko_nieaktualne=True)
                if z.get("status") in ("zatwierdzona", "odrzucona"):
                    self.wyslij_alert(z["id"], ustaw)
            elif z.get("typ") == "potwierdzenie":
                wynik = "%s: %s (%s)" % (z.get("kto") or "?", NAPISY_AKCJI.get(z.get("odpowiedz"), "?"),
                                         "przez Telegram" if z.get("skad") == "telegram" else "w panelu")
                self._zamknij_alerty(z["id"], "Odpowiedź zapisana — " + wynik + ".")
        except BladTelegrama as e:
            self._blad(e)
        except Exception as e:                                 # nic z bota nie może zatrzymać kolejki
            rdzen.log("telegram: błąd zadania (%s)" % e.__class__.__name__)

    def wyslij_alert(self, ident, ustaw=None):
        """Wiadomość z pytaniem do grupy (albo prywatnie do osoby, gdy grup nie ma). Błąd sieci = alert czeka
        w `zalegle` i idzie przy następnej okazji. → liczba wysłanych wiadomości."""
        ustaw = ustaw or ustawienia()
        d = _decyzja(ident)
        if not d or not d.get("czeka_na"):
            self._zapomnij_zalegly(ident)
            return 0
        cele = list(ustaw["grupy"])
        if not cele:
            cele = [i for i, v in ustaw["osoby"].items() if sejf.kanoniczne(v) == sejf.kanoniczne(d["czeka_na"])]
        if not cele:
            return 0
        wyslane = 0
        try:
            for czat in cele:
                w = self._wyslij_pytanie(czat, d, ustaw)
                self._zapamietaj_alert(d["id"], czat, (w or {}).get("message_id"), _odcisk(d),
                                       tresc_pytania(d, ustaw, html_tak=False))
                wyslane += 1
        except BladTelegrama as e:
            # ponawiamy tylko to, co może się udać później (sieć, błąd serwera, limit); zły numer czatu (4xx) — nie
            if not wyslane and (e.kod is None or e.kod >= 500 or e.kod == 429):
                _zmien_stan(lambda s: s.__setitem__("zalegle", sorted(set(s.get("zalegle") or []) | {d["id"]})))
            else:
                self._zapomnij_zalegly(d["id"])
            raise
        self._zapomnij_zalegly(d["id"])
        return wyslane

    def _wyslij_pytanie(self, czat, d, ustaw):
        """Pytanie z przyciskami (HTML z wzmianką osoby); gdy Telegram odrzuci HTML (400) — raz zwykłym tekstem."""
        try:
            return self._wyslij(czat, tresc_pytania(d, ustaw), przyciski(d))
        except BladTelegrama as e:
            if e.kod != 400:
                raise
            return self._wyslij(czat, tresc_pytania(d, ustaw, html_tak=False), przyciski(d), html_tak=False)

    def _zapamietaj_alert(self, ident, czat, wiadomosc, odcisk, tekst):
        """Wiadomość z przyciskami o tej decyzji — po odpowiedzi (z panelu albo Telegrama) dostanie wynik."""
        if not isinstance(wiadomosc, int):
            return

        def fn(s):
            al = s.setdefault("alerty", {})
            lista = [a for a in al.get(ident) or [] if not (a.get("czat") == czat and a.get("wiadomosc") == wiadomosc)]
            al[ident] = (lista + [{"czat": czat, "wiadomosc": wiadomosc, "odcisk": odcisk,
                                   "tekst": str(tekst or ident)[:1500]}])[-20:]
        _zmien_stan(fn)

    def _zapomnij_zalegly(self, ident):
        if ident in (_czytaj_stan().get("zalegle") or []):
            _zmien_stan(lambda s: s.__setitem__("zalegle", [x for x in s.get("zalegle") or [] if x != ident]))

    def _zamknij_alerty(self, ident, dopisek, tylko_nieaktualne=False):
        """Zdejmuje przyciski z zapamiętanych wiadomości o tej decyzji i dopisuje wynik."""
        d = _decyzja(ident) if tylko_nieaktualne else None
        aktualny = _odcisk(d) if (d and d.get("czeka_na")) else None

        def fn(s):
            al = s.setdefault("alerty", {})
            lista = al.get(ident) or []
            zostaja = [a for a in lista if tylko_nieaktualne and a.get("odcisk") == aktualny]
            al[ident] = zostaja
            if not zostaja:
                al.pop(ident, None)
            return [a for a in lista if a not in zostaja]
        for a in _zmien_stan(fn):
            self._zmien_wiadomosc(a["czat"], a["wiadomosc"], "%s\n\n%s" % (a.get("tekst") or ident, dopisek))

    def ponow_zalegle(self, ustaw=None):
        """Alerty, których nie udało się wysłać (błąd sieci) — jeszcze raz, jeśli decyzja dalej czeka."""
        self._ostatnie_ponowienie = time.time()
        for ident in list(_czytaj_stan().get("zalegle") or []):
            if re.match(r"^D-\d{1,4}$", str(ident)):
                self.wyslij_alert(ident, ustaw)

    # ------------------------------------------------------------------ odbiór
    def _czat_dozwolony(self, czat, uid, ustaw):
        cid = czat.get("id")
        if cid in ustaw["grupy"]:
            return True
        return czat.get("type") == "private" and cid == uid and uid in ustaw["osoby"]

    def odbierz_raz(self, czas=CZAS_ODPYTYWANIA_S, ustaw=None):
        """Jedno odpytanie getUpdates: każda aktualizacja przetworzona, a `offset` zapisany od razu po niej."""
        ustaw = ustaw or ustawienia()
        # offset trzymamy też w pamięci: gdy zapis pliku stanu się nie uda (pełny dysk, plik zablokowany), plik
        # podałby stary numer i Telegram od razu zwracałby te same aktualizacje — bot odpowiadałby w kółko.
        # Plik jest tylko zapasem na restart panelu.
        z_pliku = _czytaj_stan().get("offset")
        znane = [o for o in (self._offset, z_pliku) if isinstance(o, int) and not isinstance(o, bool)]
        offset = max(znane) if znane else None
        pola = {"timeout": czas, "allowed_updates": ["message", "callback_query"]}
        if isinstance(offset, int):
            pola["offset"] = offset
        wynik = self._wywolaj("getUpdates", pola, czas=czas + 10, ustaw=ustaw)
        n = 0
        for u in wynik if isinstance(wynik, list) else []:
            uid = u.get("update_id") if isinstance(u, dict) else None
            if not isinstance(uid, int):
                continue
            if isinstance(offset, int) and uid < offset:       # już przetworzona (np. atrapa podała ją drugi raz)
                continue
            try:
                self.przetworz(u, ustaw)
            except BladTelegrama as e:
                self._blad(e)
            except Exception as e:
                rdzen.log("telegram: błąd przetwarzania aktualizacji (%s)" % e.__class__.__name__)
            offset = uid + 1
            self._offset = offset
            _zmien_stan(lambda s, o=offset: s.__setitem__("offset", o))
            n += 1
        return n

    def przetworz(self, u, ustaw=None):
        ustaw = ustaw or ustawienia()
        if isinstance(u.get("callback_query"), dict):
            return self._klik(u["callback_query"], ustaw)
        if isinstance(u.get("message"), dict):
            return self._wiadomosc(u["message"], ustaw)

    def _klik(self, klik, ustaw):
        od = klik.get("from") or {}
        uid = od.get("id")
        msg = klik.get("message") or {}
        czat = msg.get("chat") or {}
        if not self._czat_dozwolony(czat, uid, ustaw):
            return                                             # czat spoza listy: nic
        kto = ustaw["osoby"].get(uid)
        if not kto:
            return self._odpowiedz_klik(klik, "Nie znam Cię. Osoba przy komputerze z panelem musi dopisać Cię "
                                              "w ustawieniach bota.", alert=True)
        dane = str(klik.get("data") or "")
        m = RX_DANE_NASTEPNE.match(dane)
        if m:
            self._odpowiedz_klik(klik, "Kolejne decyzje")
            if isinstance(msg.get("message_id"), int):         # przycisk „Następne” znika (lista idzie niżej)
                self._zmien_wiadomosc(czat["id"], msg["message_id"], (msg.get("text") or "Czeka jeszcze")[:3900] + " ⬇")
            return self.wyslij_czekajace(czat["id"], kto, int(m.group(1)), ustaw)
        m = RX_DANE_PRZYCISKU.match(dane)
        if not m:
            return self._odpowiedz_klik(klik, "Nie znam tego przycisku.")
        ident, akcja, odc = m.group(1), AKCJE[m.group(2)], m.group(3)
        if isinstance(msg.get("message_id"), int):            # ta wiadomość też dostanie wynik (bez przycisków)
            self._zapamietaj_alert(ident, czat["id"], msg["message_id"], odc, msg.get("text"))
        try:
            wynik = zapis.potwierdz_decyzje(ident, akcja, None, None, kto, zapis.ZNACZNIK_TELEGRAMA, skad="telegram",
                                            odcisk=odc) or {}
        except BladHTTP as e:
            kod = e.dodatkowe.get("kod")
            self._odpowiedz_klik(klik, e.komunikat, alert=kod in ("wlasna_decyzja", "spoza_zespolu"))
            if kod in ("nic_nie_czeka", "decyzja_zmieniona"):   # przyciski znikają z nieaktualnych pytań
                self._zamknij_alerty(ident, "Już nieaktualne: " + e.komunikat, tylko_nieaktualne=True)
            return
        if akcja == "zgoda":
            self._odpowiedz_klik(klik, "Zapisano: zgoda. %s ma dwa podpisy." % ident)
        elif akcja == "rozmowa":
            if wynik.get("agenda") is True:
                self._odpowiedz_klik(klik, "Zapisano: do rozmowy. %s jest na agendzie sesji głównej." % ident)
            else:                                              # Rejestr zapisany, agenda nie — powiedz to wprost
                self._odpowiedz_klik(klik, "Zapisano: do rozmowy, ale tematu nie dopisałem do agendy. Dodaj go "
                                           "w panelu (Na sesję główną).", alert=True)
        else:
            self._odpowiedz_klik(klik, "Zapisano: brak zgody. %s wraca „do decyzji”." % ident)
            prosba = self._wyslij(czat["id"], "%s, napisz krótko, dlaczego nie zgadzasz się z %s — odpowiedz na tę "
                                  "wiadomość w ciągu 15 minut. Możesz też nic nie pisać." % (kto, ident),
                                  html_tak=False, odpowiedz_na=msg.get("message_id"), wymus_odpowiedz=True)
            wiadomosci = {x for x in ((prosba or {}).get("message_id"), msg.get("message_id")) if isinstance(x, int)}
            self._powody[(czat["id"], uid)] = {"id": ident, "do": time.time() + CZAS_NA_POWOD_S, "wiadomosci": wiadomosci}

    def _wiadomosc(self, msg, ustaw):
        od = msg.get("from") or {}
        uid = od.get("id")
        czat = msg.get("chat") or {}
        if od.get("is_bot") or not self._czat_dozwolony(czat, uid, ustaw):
            return
        tekst = str(msg.get("text") or "").strip()
        kto = ustaw["osoby"].get(uid)
        if tekst.startswith("/"):
            polecenie, _, _ = tekst.partition(" ")
            polecenie, _, adresat = polecenie.partition("@")
            if adresat and ustaw["bot"] and adresat.lower() != ustaw["bot"].lower():
                return                                         # komenda do innego bota w tej grupie
            return self._komenda(polecenie.lower(), czat, uid, kto, ustaw)
        klucz = (czat.get("id"), uid)
        czeka = self._powody.get(klucz)
        if not kto or not czeka or not tekst:
            return
        if time.time() > czeka["do"]:
            self._powody.pop(klucz, None)
            return
        odp_na = (msg.get("reply_to_message") or {}).get("message_id")
        if odp_na not in czeka["wiadomosci"] and czat.get("type") != "private":
            return                                             # w grupie tylko odpowiedź na prośbę bota
        self._powody.pop(klucz, None)
        try:
            zapis.dopisz_powod_sprzeciwu(czeka["id"], tekst, kto, zapis.ZNACZNIK_TELEGRAMA, skad="telegram")
            self._wyslij(czat["id"], "Zapisałem powód przy %s." % czeka["id"], html_tak=False,
                         odpowiedz_na=msg.get("message_id"))
        except BladHTTP as e:
            self._wyslij(czat["id"], "Nie zapisałem powodu: %s" % e.komunikat, html_tak=False,
                         odpowiedz_na=msg.get("message_id"))

    def _komenda(self, polecenie, czat, uid, kto, ustaw):
        cid = czat.get("id")
        if polecenie == "/start":
            if kto:
                return self._wyslij(cid, "Cześć, %s! Znam Cię. Gdy druga osoba podejmie decyzję w panelu, dostaniesz "
                                    "tu pytanie z przyciskami. Wpisz /czeka, żeby zobaczyć, co czeka na Ciebie." % kto,
                                    html_tak=False)
            return self._wyslij(cid, "Nie znam Cię jeszcze. Osoba przy komputerze z panelem musi dopisać Cię "
                                "w ustawieniach bota (Twój numer w Telegramie: %s)." % uid, html_tak=False)
        if polecenie in ("/pomoc", "/help"):
            return self._wyslij(cid, "Jestem botem zespołu B&C. Gdy ktoś zatwierdzi albo odrzuci decyzję w panelu, "
                                "pytam drugą osobę: Zgoda, Brak zgody albo Przedyskutuj. Decyzja z jednym podpisem "
                                "to robocze ustalenie, z dwoma — obowiązuje.\n/czeka — co czeka na Twoje "
                                "potwierdzenie\n/start — czy Cię znam", html_tak=False)
        if polecenie == "/czeka":
            if not kto:
                return self._wyslij(cid, "Nie znam Cię — poproś o dopisanie w ustawieniach bota.", html_tak=False)
            try:
                self.ponow_zalegle(ustaw)
            except BladTelegrama as e:
                self._blad(e)
            return self.wyslij_czekajace(cid, kto, 0, ustaw)

    def wyslij_czekajace(self, czat, kto, od, ustaw=None):
        """Decyzje czekające na potwierdzenie tej osoby: po jednej wiadomości z przyciskami, najwyżej NA_RAZ,
        a gdy jest więcej — wiadomość z przyciskiem „Następne”."""
        ustaw = ustaw or ustawienia()
        lista = czekajace_na(kto)
        if not lista:
            return self._wyslij(czat, "Nic nie czeka na Twoje potwierdzenie. ✅", html_tak=False)
        if od >= len(lista):
            od = 0
        if od == 0:
            self._wyslij(czat, "%s, na Twoje potwierdzenie czeka: %d." % (kto, len(lista)), html_tak=False)
        for d in lista[od:od + NA_RAZ]:
            w = self._wyslij_pytanie(czat, d, ustaw)
            self._zapamietaj_alert(d["id"], czat, (w or {}).get("message_id"), _odcisk(d),
                                   tresc_pytania(d, ustaw, html_tak=False))
        reszta = len(lista) - (od + NA_RAZ)
        if reszta > 0:
            self._wyslij(czat, "Czeka jeszcze: %d." % reszta, {"inline_keyboard": [[
                {"text": "Następne ▶", "callback_data": "c:%d" % (od + NA_RAZ)}]]}, html_tak=False)

    # ------------------------------------------------------------------ wątki
    def _petla_odbioru(self):
        przerwa = 0
        while not self._stop.is_set():
            ustaw = ustawienia()
            if not ustaw["wlaczony"]:
                self.odbior_dziala = False
                self._stop.wait(5)
                continue
            try:
                self.odbior_dziala = True
                self.odbierz_raz(ustaw=ustaw)
                przerwa = 0
                if (_czytaj_stan().get("zalegle") and time.time() - self._ostatnie_ponowienie > PONOWIENIE_CO_S):
                    self.ponow_zalegle(ustaw)
            except BladTelegrama as e:
                self._blad(e)
                if e.kod == 409:
                    self.ostatni_blad["tekst"] = ("Inny program odbiera wiadomości tego bota (np. panel na drugim "
                                                  "komputerze z tym samym tokenem).")
                przerwa = min(60, max(5, przerwa * 2))
                self._stop.wait(przerwa)
            except Exception as e:
                rdzen.log("telegram: błąd odbioru (%s)" % e.__class__.__name__)
                self._stop.wait(10)

    def _petla_wysylki(self):
        while not self._stop.is_set():
            try:
                z = self._kolejka.get(timeout=1.0)
            except queue.Empty:
                continue
            self._zadanie(z)

    def uruchom(self):
        """Wątki odbioru i wysyłki (raz na proces). Bez ustawień bota wątek odbioru tylko co 5 s sprawdza plik."""
        if self._watki:
            return
        for nazwa, cel in (("telegram-odbior", self._petla_odbioru), ("telegram-wysylka", self._petla_wysylki)):
            w = threading.Thread(target=cel, name=nazwa, daemon=True)
            w.start()
            self._watki.append(w)

    def zatrzymaj(self):
        self._stop.set()

    def stan(self):
        """Stan dla osoby przy komputerze: bez tokenu i bez identyfikatorów."""
        u = ustawienia()
        st = _czytaj_stan()
        return {"wlaczony": u["wlaczony"], "bot": u["bot"], "osoby": len(u["osoby"]), "grupy": len(u["grupy"]),
                "blad_ustawien": u["blad"], "odbior": bool(self._watki) and self.odbior_dziala,
                "ostatni_kontakt": self.ostatni_kontakt,
                "ostatni_blad": dict(self.ostatni_blad) if self.ostatni_blad else None,
                "zalegle": len(st.get("zalegle") or [])}


BOT = Bot()


# =========================================================================== trasy i start
def _t_stan(z):
    if not z.lokalny:
        raise BladHTTP(403, "Stan bota Telegram widać tylko na komputerze, na którym działa panel")
    return BOT.stan()


def zarejestruj(app):
    app.dodaj("GET", "/api/telegram/stan", _t_stan)
    zapis.dodaj_sluchacza(BOT.zdarzenie)


def uruchom_w_tle():
    """Woła serwer.py dopiero, gdy panel naprawdę obsługuje żądania (nie przy --sprawdz ani --eksport)."""
    BOT.uruchom()


def zdrowie():
    u = ustawienia()
    return {"ok": True, "wlaczony": u["wlaczony"], "odbior": BOT.odbior_dziala}
