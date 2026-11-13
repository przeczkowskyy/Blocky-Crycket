# -*- coding: utf-8 -*-
"""Praca na sejfie z panelu: odpowiedzi na pytania otwarte, odhaczanie i dodawanie zadań, statusy decyzji.

Zasada D-008: sejf `B&C/` zostaje jedynym źródłem prawdy. Panel nie ma własnej bazy — zapisuje te same pliki
Markdown (`<sejf>/Produkcja/*.md`), których używa Obsidian i agenci, małymi zmianami jak przy edycji ręcznej:
- każda operacja zmienia WYŁĄCZNIE wskazane miejsce; reszta pliku zostaje bajt w bajt (BOM, końce linii CRLF/LF,
  spacje na końcach linii, a w wierszu statusu decyzji także dopiski i odstępy);
- jedna blokada zapisu na cały sejf — operacje idą po kolei; przycisk „Wyślij” (bc/gitsync.py) bierze tę samą
  blokadę (`blokada_wysylania`), więc zapis z panelu nie wcina się w commit;
- klient przysyła znacznik wersji pliku z GET /api/sejf/plan (`wersje`, skrót SHA-256 treści); gdy plik zmienił się
  od odczytu — 409 z prośbą o odświeżenie (nic nie jest nadpisywane po cichu). Ponowna próba zapisu przy blokadzie
  pliku (OneDrive, Obsidian) też najpierw sprawdza, czy nikt w tym czasie nie zapisał pliku;
- plik ze znacznikami konfliktu gita (`<<<<<<<` … `>>>>>>>`) albo z samotnymi znakami CR panel odrzuca (409) —
  wtedy parser planu i zapis widziałyby plik inaczej;
- dwie sekcje o tym samym numerze (pytanie „## 23.”, decyzja „### D-028”) albo dwie sekcje „Zrobione” = 409 zamiast
  zgadywania, którą zmienić;
- każda operacja dopisuje ślad do Dziennika zmian w sekcji dnia „## RRRR-MM-DD · Panel (ludzie)” z linkiem do notatki;
- zapis atomowy (plik tymczasowy + os.replace) i unieważnienie pamięci planu w bc/sejf.py; pozostawione po
  przerwanym zapisie pliki tymczasowe panelu (`<plik>.md.<pid>.<hex>.tmp`, starsze niż 10 min) są sprzątane.

Pliki biorą się z konfiguracji sejfów (`sejf.pliki_planu()`), nie ze sztywnej ścieżki — testy i próby działają na kopii.

Uprawnienia: odpowiedzi i zadania — każdy z dostępem do panelu (także gość z kodem dostępu przez tunel; goście mają
limit zapisów). Statusy decyzji (decyzja z 13.11.2026: Karol i Paweł mają równe prawa, wystarcza decyzja jednego,
każda zostaje w logach z imieniem i datą) zmienia „decydent”: żądanie z KLUCZEM ZATWIERDZANIA (`z.game_director` —
nazwa pola została po dawnym kluczu Game Directora, patrz serwer.py) albo osoba przy komputerze z panelem
(`z.lokalny`, klucz lokalny). Gość z samym kodem dostępu dostaje 403. Zmiana statusu wymaga prawdziwego imienia
wpisanego w Ustawieniach panelu (nagłówek X-BC-Kto, `z.kto_z_naglowka`); puste albo domyślne „gość” = 400
`brak_imienia`, bo decyzja musi mieć podpis. Dotyczy to także osoby przy komputerze: gdy przeglądarka nie wysyła
imienia, serwer bierze do innych podpisów `git config user.name` (albo nazwę konta systemu), ale takim domyślnym
imieniem decyzji nie podpisze — też 400 `brak_imienia`. W Rejestrze decyzji podpis to
„zdecydował: Imię RRRR-MM-DD” / „oznaczył: Imię RRRR-MM-DD” i „Uzasadnienie — Imię, RRRR-MM-DD: …”.

Imię wpisane w panelu niczego nie daje — służy tylko do podpisu, a o zaufaniu mówi ZNACZNIK, który dopisuje serwer
i którego nie da się wpisać w imieniu (nawiasy są z imienia usuwane):
  - `- Paweł (klucz zatwierdzania, 2026-11-13): …` — żądanie z kluczem zatwierdzania;
  - `- Karol (2026-11-13): …`                      — osoba przy komputerze z panelem (klucz lokalny);
  - `- Paweł (gość panelu, 2026-11-13): …`          — gość z kodem dostępu (telefon, tunel) — imię niczego nie dowodzi.
Wpisy z 13.11.2026 sprzed tej zmiany mają znacznik „Game Director” — znaczy on to samo co „klucz zatwierdzania”.
Imiona zawierające znaczniki („Game Director”, „klucz zatwierdzania”, „gość panelu”, bez względu na wielkość liter)
są odrzucane (400 `imie_zastrzezone`) — także z kluczem, bo podpis ma nieść prawdziwe imię.

Tekst od ludzi: limit długości, bez znaków sterujących, zawsze jedna linia (nowe linie → „ / ”), bez prób
wstrzyknięcia struktury pliku (nagłówek „#”, pole zadania „- [ ]”, „**Odpowiedź:**”, kolejne pole „· [ ]”).

Pliki sejfu zmienione przez panel zapamiętuje `<dane lokalne>/zapis_sejfu.json`, żeby przycisk „Wyślij”
(bc/gitsync.py) commitował je tylko wtedy, gdy naprawdę zmienił je panel (`do_wyslania`, `po_commicie`, `wyslano`).
"""
import contextlib
import datetime
import hashlib
import os
import re
import secrets
import threading
import time
import unicodedata

from . import rdzen, sejf
from .rdzen import BladHTTP

LIMIT_ODPOWIEDZI = 2000
LIMIT_ZADANIA = 300
LIMIT_UZASADNIENIA = 1000
LIMIT_IMIENIA = 40
LIMIT_W_DZIENNIKU = 140
PLIK_STANU = "zapis_sejfu.json"                               # w danych lokalnych (rdzen.RUNTIME), poza repozytorium

# Goście (bez klucza lokalnego i bez klucza zatwierdzania): najwyżej tyle zapisów w oknie czasu — na klienta
# i razem dla wszystkich gości. Osoba przy komputerze i przeglądarka z kluczem zatwierdzania nie mają limitu.
OKNO_LIMITU_S = 600
LIMIT_ZAPISOW_GOSCIA = 30
LIMIT_ZAPISOW_GOSCI = 120

ZNACZNIK_ZATWIERDZANIA = "klucz zatwierdzania"
ZNACZNIK_GOSCIA = "gość panelu"
DOMYSLNE_IMIE = "gość"
KOMUNIKAT_BRAK_IMIENIA = "Wpisz swoje imię w Ustawieniach — decyzja musi mieć podpis (imię i datę)."

PRIORYTETY = {"wysoki": "wysoki", "średni": "średni", "sredni": "średni", "niski": "niski"}
SEKCJE_DODAWANIA = ("teraz", "backlog")
RODZAJE_SEKCJI = ("teraz", "backlog", "zrobione")
NAZWY_SEKCJI = {"teraz": "Teraz", "backlog": "Backlog", "zrobione": "Zrobione"}
# status docelowy -> (emoji, słowo w pliku, słowo do dziennika, podpis)
STATUSY_DOCELOWE = {"zatwierdzona": ("✅", "zatwierdzona", "zatwierdzona", "zdecydował"),
                    "odrzucona": ("❌", "odrzucona", "odrzucona", "zdecydował"),
                    "do_decyzji": ("🕓", "do decyzji", "oznaczona „do decyzji”", "oznaczył")}
STATUSY_ZMIENIALNE = ("propozycja", "do_decyzji")              # zatwierdzonej decyzji się nie przepisuje
NAZWY_STATUSOW = {"zatwierdzona": "zatwierdzona", "odrzucona": "odrzucona", "zastapiona": "zastąpiona",
                  "propozycja": "propozycja", "do_decyzji": "do decyzji"}

_blokada = threading.Lock()                                    # jedna blokada zapisu na cały sejf
_stan_blokada = threading.Lock()
_limity = {}                                                   # klient -> [czasy zapisów gościa]
_limity_blokada = threading.Lock()
_posprzatane = set()                                           # foldery, w których już szukano starych plików .tmp

_RX_DATA_NAGLOWKA = re.compile(r"^\d{4}-\d{2}-\d{2}\b")
_RX_LISTA = re.compile(r"^\s*[-*+]\s")
_RX_ZNACZNIK_POLA = re.compile(r"\s+·\s+\[([^\[\]])\](?=\s)")
_RX_STERUJACE = re.compile("[\x00-\x08\x0b-\x1f\x7f-\x9f​‎‏‪-‮⁠⁦-⁩﻿]")
_RX_NR_PYTANIA = re.compile(r"^(\d+)[.)]?\s+")
_RX_NR_DECYZJI = re.compile(r"^D-(\d+)\b")
_RX_KONFLIKT_POCZATEK = re.compile(rb"^<<<<<<<(?: |\r?$)", re.MULTILINE)
_RX_KONFLIKT_KONIEC = re.compile(rb"^>>>>>>>(?: |\r?$)", re.MULTILINE)
_RX_PLIK_TYMCZASOWY = re.compile(r"^.+\.md\.\d+\.[0-9a-f]{6}\.tmp$")
# znaczniki serwera (i dawny „Game Director”) nie mogą być imieniem — inaczej imię udawałoby znacznik zaufania
_RX_ZASTRZEZONE_IMIE = re.compile(r"game\s*director|klucz\s*zatwierdzania|go[śs][ćc]\s*panelu", re.IGNORECASE)
# początek wiersza statusu decyzji: [wcięcie][emoji][odstęp][*_][słowo statusu] — reszta wiersza zostaje bajt w bajt
_RX_STATUS_NA_POCZATKU = re.compile(
    r"^(?P<wciecie>\s*)(?P<emoji>[^\w\s·*]+)?(?P<odstep>\s*)(?P<format>[*_]*)"
    r"(?P<slowo>(?:propozycj|do[ _]decyzji|zatwierdzon|odrzucon|zast[aą]pion)\w*)?", re.IGNORECASE)
_RX_STARY_PODPIS = re.compile(r"\s+·\s+(?:zdecydował|zdecydowała|oznaczył|oznaczyła)\b[^·]*?(?=\s+·\s|\s*$)",
                              re.IGNORECASE)


def dzis():
    """Dzisiejsza data (czas lokalny komputera z panelem) jako RRRR-MM-DD. Testy podmieniają tę funkcję."""
    return datetime.date.today().isoformat()


def dostepny():
    """Czy zapis do sejfu z panelu jest włączony (`zapis_sejfu` w konfiguracji; domyślnie tak)."""
    return rdzen.konfiguracja().get("zapis_sejfu", True) is not False


# =========================================================================== dokument: linie z zachowaniem bajtów
class Dokument:
    """Plik Markdown jako lista linii z ich własnymi końcami (\\n, \\r\\n albo brak na końcu pliku).

    Zmiany dotykają tylko wskazanych linii; `bajty()` składa plik z powrotem — reszta bajt w bajt jak w oryginale.
    Nagłówki i bloki kodu rozpoznaje tak samo jak parser planu w bc/sejf.py (`_RX_NAGLOWEK`, `zamyka_plot`).
    """

    def __init__(self, bajty):
        self.bom = bajty.startswith(b"\xef\xbb\xbf")
        try:
            tekst = bajty[3 if self.bom else 0:].decode("utf-8")
        except UnicodeDecodeError:
            raise BladHTTP(409, "Ten plik nie jest zapisany w UTF-8, więc panel go nie zmieni. Popraw kodowanie w edytorze.")
        self.linie = re.findall(r"[^\n]*\n|[^\n]+$", tekst)
        if "".join(self.linie) != tekst:                       # zabezpieczenie: podział musi być bezstratny
            raise BladHTTP(500, "Nie udało się bezpiecznie odczytać pliku (nietypowe końce linii).")
        # samotne CR: parser planu (bc/sejf.py) liczy je jako nową linię, a ten podział — nie
        self.samotne_cr = "\r" in tekst.replace("\r\n", "")
        crlf = tekst.count("\r\n")
        lf = tekst.count("\n") - crlf
        self.nl = "\r\n" if crlf > lf else "\n"

    def __len__(self):
        return len(self.linie)

    def tresc(self, i):
        """Linia bez znaków końca linii."""
        l = self.linie[i]
        if l.endswith("\n"):
            l = l[:-1]
            if l.endswith("\r"):
                l = l[:-1]
        return l

    def _koniec(self, i):
        l = self.linie[i]
        return "\r\n" if l.endswith("\r\n") else "\n" if l.endswith("\n") else ""

    def _nl_obok(self, i):
        """Koniec linii do nowych wierszy: taki jak u sąsiada (pliki mieszane), inaczej przeważający w pliku."""
        for j in (i - 1, i):
            if 0 <= j < len(self.linie) and self._koniec(j):
                return self._koniec(j)
        return self.nl

    def zamien(self, i, tekst):
        self.linie[i] = tekst + self._koniec(i)

    def wstaw(self, i, teksty):
        """Wstawia wiersze PRZED indeksem i (i == len = na końcu pliku)."""
        nl = self._nl_obok(i)
        if i == len(self.linie) and i > 0 and not self._koniec(i - 1):
            self.linie[i - 1] += nl                            # ostatnia linia bez końca: inaczej sklejenie wierszy
        self.linie[i:i] = [t + nl for t in teksty]

    def usun(self, i, ile=1):
        del self.linie[i:i + ile]

    def bajty(self):
        return (b"\xef\xbb\xbf" if self.bom else b"") + "".join(self.linie).encode("utf-8")

    # --- struktura
    def poczatek_tresci(self):
        """Indeks pierwszej linii po frontmatterze (--- … ---)."""
        if self.linie and self.tresc(0).strip() == "---":
            for k in range(1, len(self.linie)):
                if self.tresc(k).strip() in ("---", "..."):
                    return k + 1
        return 0

    def naglowki(self):
        """[(indeks, poziom, tekst)] nagłówków Markdown poza frontmatterem i blokami kodu."""
        wynik, plot = [], None
        for i in range(self.poczatek_tresci(), len(self.linie)):
            linia = self.tresc(i)
            if plot:
                if sejf.zamyka_plot(linia, plot):
                    plot = None
                continue
            m_plot = sejf._RX_PLOT.match(linia)
            if m_plot:
                plot = m_plot.group(1)
                continue
            m = sejf._RX_NAGLOWEK.match(linia)
            if m:
                wynik.append((i, len(m.group(1)), m.group(2).strip()))
        return wynik

    def koniec_sekcji(self, i, poziom, na_linii_poziomej=False):
        """Indeks pierwszej linii za sekcją, która zaczyna się nagłówkiem i (następny nagłówek poziomu <= poziom,
        z na_linii_poziomej=True także linia --- , za którą w rejestrze jest stopka)."""
        koniec = len(self.linie)
        for j, p, _ in self.naglowki():
            if j > i and p <= poziom:
                koniec = j
                break
        if na_linii_poziomej:
            for j in range(i + 1, koniec):
                if sejf._RX_LINIA_POZIOMA.match(self.tresc(j)):
                    return j
        return koniec

    def za_trescia(self, i, koniec):
        """Indeks tuż za ostatnią niepustą linią w (i, koniec) — miejsce na dopisanie na końcu sekcji."""
        k = i + 1
        for j in range(i + 1, koniec):
            if self.tresc(j).strip():
                k = j + 1
        return k


# =========================================================================== tekst od ludzi i podpis
def _jedna_linia(tekst):
    t = unicodedata.normalize("NFC", tekst)
    t = re.sub(r"[ \t]*[\r\n  \x85]\s*", " / ", t.strip())
    t = t.replace("\t", " ")
    t = _RX_STERUJACE.sub("", t)
    t = re.sub(r"[  ]{2,}", " ", t).strip()
    while t.startswith("/ ") or t == "/":
        t = t[2:].strip()
    while t.endswith(" /"):
        t = t[:-2].strip()
    return t


def czysty_tekst(tekst, limit, nazwa, wymagany=True):
    """Tekst od człowieka gotowy do wpisania w jeden wiersz pliku. Błędy jako 400 z czytelnym komunikatem."""
    if tekst is None:
        tekst = ""
    if not isinstance(tekst, str):
        raise BladHTTP(400, "Pole „%s” musi być tekstem" % nazwa)
    t = _jedna_linia(tekst)
    if not t:
        if wymagany:
            raise BladHTTP(400, "Pole „%s” jest puste" % nazwa)
        return ""
    if len(t) > limit:
        raise BladHTTP(400, "Pole „%s” jest za długie: %d znaków (najwyżej %d)" % (nazwa, len(t), limit))
    if re.match(r"#{1,6}(\s|$)", t):
        raise BladHTTP(400, "Pole „%s” nie może zaczynać się nagłówkiem Markdown („#”)" % nazwa)
    if re.match(r"([-*+]\s*)?\[[^\[\]]?\]", t):
        raise BladHTTP(400, "Pole „%s” nie może zaczynać się polem zadania („- [ ]”)" % nazwa)
    if re.search(r"\*\*\s*odpowied[źz]", t, re.IGNORECASE):
        raise BladHTTP(400, "Pole „%s” nie może zawierać „**Odpowiedź:**”" % nazwa)
    if re.search(r"·\s*\[[^\[\]]\](\s|$)", t):
        raise BladHTTP(400, "Pole „%s” nie może zawierać kolejnego pola zadania („· [ ]”)" % nazwa)
    return t


def imie(z):
    """Imię z panelu (X-BC-Kto) oczyszczone ze znaków formatowania i z nawiasów, przecinków i „·” — te należą do
    znacznika dopisywanego przez serwer (patrz `podpis`) i do pól wiersza statusu. Nie daje żadnych uprawnień."""
    t = _jedna_linia(str(getattr(z, "kto", "") or "")).replace(" / ", " ")
    t = re.sub(r"\s{2,}", " ", re.sub(r"[*_\[\]#`|<>:()·,]", "", t)).strip()[:LIMIT_IMIENIA].strip()
    return t or DOMYSLNE_IMIE


def bez_imienia(kto):
    """Czy imię jest puste albo domyślne („gość”) — takim imieniem nie da się podpisać decyzji."""
    return not (kto or "").strip() or (kto or "").strip().casefold() in (DOMYSLNE_IMIE, "gosc")


def decydent(z):
    """Czy żądanie może zmieniać statusy decyzji: klucz zatwierdzania albo osoba przy komputerze (klucz lokalny)."""
    return bool(getattr(z, "game_director", False) or getattr(z, "lokalny", False))


def podpis(z):
    """(imię, znacznik) do podpisu zmiany. Znacznik dopisuje serwer na podstawie kluczy, nie imienia:
    „klucz zatwierdzania” (klucz zatwierdzania), None (osoba przy komputerze z kluczem lokalnym), „gość panelu”
    (reszta). Imię ze znacznikiem w środku jest odrzucane (400) dla każdego — także z kluczem."""
    kto = imie(z)
    if _RX_ZASTRZEZONE_IMIE.search(kto):
        raise BladHTTP(400, "Imię „%s” jest zastrzeżone — tak brzmią znaczniki, które dopisuje panel. Wpisz swoje "
                            "imię w Ustawieniach." % kto, kod="imie_zastrzezone")
    if getattr(z, "game_director", False):
        return kto, ZNACZNIK_ZATWIERDZANIA
    return kto, (None if getattr(z, "lokalny", False) else ZNACZNIK_GOSCIA)


def _kto_w_dzienniku(kto, znacznik):
    return "%s (%s)" % (kto, znacznik) if znacznik and znacznik != kto else kto


def skrot(tekst, n=LIMIT_W_DZIENNIKU):
    """Skraca tekst do dziennika na granicy słowa, bez urwanego wikilinku."""
    if len(tekst) <= n:
        return tekst
    t = tekst[:n - 1].rsplit(" ", 1)[0].rstrip(" ,;:·")
    if t.count("[[") > t.count("]]"):
        t = t[:t.rfind("[[")].rstrip()
    return t + "…"


def _klient(z):
    """Kto pisze (do limitu gości): za tunelem na pętli zwrotnej prawdziwy adres podaje pośrednik."""
    ip = str(getattr(z, "ip", "") or "")
    naglowki = getattr(z, "naglowki", None) or {}
    if ip in ("127.0.0.1", "::1", "::ffff:127.0.0.1"):
        posrednik = (naglowki.get("Cf-Connecting-Ip") or naglowki.get("X-Forwarded-For") or "").split(",")[0].strip()
        if posrednik:
            return posrednik[:64]
    return ip or "?"


def _sprawdz_limit(z):
    """Limit zapisów gościa (429). Osoba przy komputerze i przeglądarka z kluczem zatwierdzania bez limitu."""
    if getattr(z, "lokalny", False) or getattr(z, "game_director", False):
        return
    teraz = time.time()
    klient = _klient(z)
    with _limity_blokada:
        for k in list(_limity):
            _limity[k] = [t for t in _limity[k] if teraz - t < OKNO_LIMITU_S]
            if not _limity[k]:
                del _limity[k]
        moje = _limity.get(klient, [])
        if len(moje) >= LIMIT_ZAPISOW_GOSCIA or sum(len(v) for v in _limity.values()) >= LIMIT_ZAPISOW_GOSCI:
            raise BladHTTP(429, "Za dużo zapisów do sejfu z tego połączenia. Spróbuj za kilka minut "
                                "(limit dla gości: %d na %d min)." % (LIMIT_ZAPISOW_GOSCIA, OKNO_LIMITU_S // 60),
                           kod="limit_zapisow")
        _limity[klient] = moje + [teraz]


# =========================================================================== pliki i stan lokalny
# Notatki sejfu spoza planu, które panel też zmienia (agenda sesji głównych — bc/sesje.py). Klucz -> nazwa pliku
# w <sejf B&C>/Produkcja/. Plan (sejf.PLIKI_PLANU) zostaje bez zmian.
PLIKI_DODATKOWE = {"sesje": "Sesje główne.md"}


def _plik(klucz):
    if klucz in PLIKI_DODATKOWE:
        wynik = sejf.plik_produkcji(PLIKI_DODATKOWE[klucz])
        if wynik:
            return wynik
        raise BladHTTP(503, "Panel nie widzi sejfu B&C — sprawdź listę sejfów w konfiguracji.")
    pliki = sejf.pliki_planu()
    if klucz not in pliki:
        raise BladHTTP(503, "Panel nie widzi sejfu B&C — sprawdź listę sejfów w konfiguracji.")
    return pliki[klucz]


def plik(klucz):
    """(ścieżka bezwzględna, ścieżka do pokazania) pliku sejfu, który zmienia panel (także „sesje”)."""
    return _plik(klucz)


def _notatka(klucz):
    """Nazwa notatki do wikilinku w Dzienniku zmian, np. „Pytania otwarte”."""
    return (PLIKI_DODATKOWE.get(klucz) or sejf.PLIKI_PLANU[klucz])[:-3]


def wykonaj(klucz, wersja, zmiana, kto, znacznik=None):
    """Publiczna droga zapisu dla innych modułów (bc/sesje.py): to samo co odpowiedzi i zadania — blokada sejfu,
    kontrola wersji, zapis atomowy, ślad w Dzienniku zmian i dla „Wyślij”. `zmiana(dok)` zwraca opis do dziennika."""
    return _wykonaj(klucz, wersja, zmiana, kto, znacznik)


def sprawdz_limit(z):
    """Limit zapisów gościa (429) — ten sam licznik co odpowiedzi i zadania."""
    _sprawdz_limit(z)


def _czytaj_bajty(sciezka, pokaz):
    try:
        with open(sciezka, "rb") as f:
            return f.read()
    except FileNotFoundError:
        raise BladHTTP(404, "W sejfie nie ma pliku %s" % pokaz)
    except OSError as e:
        raise BladHTTP(503, "Nie udało się odczytać %s (%s). Spróbuj za chwilę." % (pokaz, e.__class__.__name__))


def _sprawdz_tresc(dane, dok, pokaz):
    """Plik, którego panel nie zmieni bezpiecznie: znaczniki konfliktu gita albo samotne znaki CR."""
    nazwa = pokaz.rsplit("/", 1)[-1]
    if _RX_KONFLIKT_POCZATEK.search(dane) and _RX_KONFLIKT_KONIEC.search(dane):
        raise BladHTTP(409, "W pliku %s są znaczniki konfliktu gita (<<<<<<< … >>>>>>>). Najpierw rozwiąż konflikt "
                            "(np. z pomocą agenta), potem zapisuj z panelu." % nazwa, kod="konflikt_gita")
    if dok.samotne_cr:
        raise BladHTTP(409, "Plik %s ma nietypowe końce linii (samotne CR) — otwórz go i zapisz w Obsidianie, "
                            "potem spróbuj jeszcze raz." % nazwa, kod="konce_linii")


def _zapisz(sciezka, dane, przed=None):
    """Zapis atomowy: plik tymczasowy obok + os.replace (z ponowieniami — OneDrive i antywirus blokują pliki).

    `przed` = treść, od której liczono zmianę. Przed każdą próbą plik jest czytany ponownie: blokada pliku często
    znaczy, że ktoś (Obsidian, agent) właśnie go zapisuje — wtedy 409 zamiast nadpisania jego zmiany."""
    tmp = "%s.%d.%s.tmp" % (sciezka, os.getpid(), secrets.token_hex(3))
    with open(tmp, "wb") as f:
        f.write(dane)
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass
    ostatni = None
    try:
        for proba in range(10):
            if przed is not None:
                try:
                    with open(sciezka, "rb") as f:
                        teraz = f.read()
                except FileNotFoundError:
                    teraz = b""
                except OSError:                                # chwilowo nie da się odczytać: spróbuj za chwilę
                    teraz = None
                if teraz is not None and teraz != przed:
                    raise BladHTTP(409, "Ktoś zapisał plik %s w tej samej chwili — odśwież plan i spróbuj jeszcze "
                                        "raz." % os.path.basename(sciezka), kod="konflikt_wersji",
                                   wersja=sejf.wersja_bajtow(teraz))
            try:
                os.replace(tmp, sciezka)
                return
            except OSError as e:
                ostatni = e
                time.sleep(0.05 * (proba + 1))
    except BaseException:
        _usun_cicho(tmp)
        raise
    _usun_cicho(tmp)
    raise BladHTTP(503, "Plik jest chwilowo zablokowany (OneDrive albo inny program) — spróbuj za chwilę. (%s)"
                   % ostatni.__class__.__name__)


def _usun_cicho(sciezka):
    try:
        os.remove(sciezka)
    except OSError:
        pass


def _sprzataj_tymczasowe(folder):
    """Usuwa pozostawione po przerwanym zapisie pliki tymczasowe panelu (`*.md.<pid>.<hex>.tmp`, starsze niż
    10 min), żeby nie trafiły do repozytorium. Raz na folder w czasie działania panelu."""
    if folder in _posprzatane:
        return
    _posprzatane.add(folder)
    try:
        nazwy = os.listdir(folder)
    except OSError:
        return
    for nazwa in nazwy:
        if not _RX_PLIK_TYMCZASOWY.match(nazwa):
            continue
        p = os.path.join(folder, nazwa)
        try:
            if time.time() - os.path.getmtime(p) > 600:
                os.remove(p)
                rdzen.log("zapis: usunięto stary plik tymczasowy %s" % nazwa)
        except OSError:
            pass


def _skrot_normalny(dane):
    """Skrót treści bez różnic końców linii (git zapisuje LF, kopia robocza może mieć CRLF)."""
    return hashlib.sha256(dane.replace(b"\r\n", b"\n")).hexdigest()


def _plik_stanu():
    return os.path.join(rdzen.RUNTIME, PLIK_STANU)


def _klucz_stanu(sciezka):
    return os.path.normcase(os.path.realpath(sciezka))


def _zapamietaj(sciezka, przed, po, opis):
    """Zapisuje w danych lokalnych, że panel zmienił ten plik (dla przycisku „Wyślij”)."""
    with _stan_blokada:
        stan = rdzen.czytaj_json(_plik_stanu(), {}) or {}
        pliki = stan.setdefault("pliki", {})
        k = _klucz_stanu(sciezka)
        wpis = pliki.get(k)
        if wpis is None:
            wpis = {"sciezka": os.path.realpath(sciezka), "baza": _skrot_normalny(przed), "opisy": [], "obce": False}
        elif wpis.get("ostatni") != sejf.wersja_bajtow(przed):
            wpis["obce"] = True                                # ktoś zmienił plik poza panelem między zapisami panelu
        wpis["ostatni"] = sejf.wersja_bajtow(po)
        wpis["ostatni_lf"] = _skrot_normalny(po)               # do sprawdzenia, co naprawdę trafiło do commita
        wpis["kiedy"] = rdzen.teraz()
        wpis["opisy"] = (list(wpis.get("opisy") or []) + [opis])[-30:]
        pliki[k] = wpis
        rdzen.zapisz_json(_plik_stanu(), stan)


def _rel_w_repo(repo, sciezka):
    try:
        rel = os.path.relpath(os.path.realpath(sciezka), os.path.realpath(repo))
    except ValueError:                                         # inny dysk
        return None
    rel = rel.replace("\\", "/")
    if rel.startswith("../") or rel == ".." or os.path.isabs(rel):
        return None
    return rel


@contextlib.contextmanager
def blokada_wysylania(czekaj_s=15):
    """Blokada zapisu sejfu na czas przycisku „Wyślij” (od sprawdzenia plików do wyczyszczenia śladu po commicie):
    zapis z panelu w tym czasie poczeka, zamiast trafić między commit a `wyslano()`."""
    if not _blokada.acquire(timeout=czekaj_s):
        raise BladHTTP(409, "Trwa zapis do sejfu z panelu — kliknij Wyślij jeszcze raz za chwilę.")
    try:
        yield
    finally:
        _blokada.release()


def do_wyslania(repo, git):
    """Pliki sejfu zmienione przez panel, które można bezpiecznie wysłać przyciskiem „Wyślij”.

    Plik idzie do commita tylko wtedy, gdy: leży w repozytorium, jest jednym z plików, które zmienia panel (pytania,
    zadania, decyzje, dziennik i agenda sesji głównych „Sesje główne.md”), jego treść jest dokładnie tą, którą zapisał panel, a wersja w HEAD
    jest tą, od której panel zaczynał — czyli w pliku nie ma cudzych, niezatwierdzonych zmian.
    Zwraca (ścieżki względem repo, opisy zmian, uwagi dla człowieka). `git(argumenty, repo)` = gitsync.git.
    """
    with _stan_blokada:
        stan = rdzen.czytaj_json(_plik_stanu(), {}) or {}
    dozwolone = {}
    try:
        for klucz in ("pytania", "zadania", "decyzje", "dziennik", "sesje"):
            p, _ = _plik(klucz)
            dozwolone[_klucz_stanu(p)] = p
    except (KeyError, BladHTTP):
        return [], [], []
    sciezki, opisy, uwagi, do_usuniecia = [], [], [], []
    for k, wpis in sorted((stan.get("pliki") or {}).items()):
        if k not in dozwolone:
            continue
        rel = _rel_w_repo(repo, dozwolone[k])
        if not rel:
            continue
        try:
            with open(dozwolone[k], "rb") as f:
                teraz = f.read()
        except OSError:
            do_usuniecia.append(k)
            continue
        kod, out, _ = git(["show", "HEAD:" + rel], repo)
        w_head = _skrot_normalny(out.encode("utf-8")) if kod == 0 else None
        if w_head == _skrot_normalny(teraz):                   # nic do wysłania (np. ktoś już to zacommitował)
            do_usuniecia.append(k)
            continue
        if not wpis.get("obce") and sejf.wersja_bajtow(teraz) == wpis.get("ostatni") and w_head == wpis.get("baza"):
            sciezki.append(rel)
            opisy.extend(wpis.get("opisy") or [])
        else:
            uwagi.append("%s ma też zmiany spoza panelu — wyślij go zwykłym commitem (np. przez agenta)." % rel)
    if do_usuniecia:
        _zapomnij(do_usuniecia)
    return sciezki, opisy, uwagi


def po_commicie(repo, git, sciezki_rel):
    """Po commicie: ścieżki, których treść w HEAD NIE jest ostatnim zapisem panelu — ktoś (Obsidian, agent) zmienił
    plik między sprawdzeniem a commitem, więc commit „panel: …” zawiera też jego zmianę. Do uwagi dla człowieka."""
    with _stan_blokada:
        stan = rdzen.czytaj_json(_plik_stanu(), {}) or {}
    pliki = stan.get("pliki") or {}
    inne = []
    for rel in sciezki_rel:
        wpis = pliki.get(_klucz_stanu(os.path.join(repo, *rel.split("/")))) or {}
        if not wpis.get("ostatni_lf"):
            continue
        kod, out, _ = git(["show", "HEAD:" + rel], repo)
        if kod == 0 and _skrot_normalny(out.encode("utf-8")) != wpis["ostatni_lf"]:
            inne.append(rel)
    return inne


def wyslano(repo, sciezki_rel):
    """Po udanym commicie: zapomina pliki, które poszły do repozytorium (woła się pod `blokada_wysylania`)."""
    cele = {_klucz_stanu(os.path.join(repo, *r.split("/"))) for r in sciezki_rel}
    _zapomnij(cele)


def _zapomnij(klucze):
    klucze = set(klucze)
    with _stan_blokada:
        stan = rdzen.czytaj_json(_plik_stanu(), {}) or {}
        pliki = stan.get("pliki") or {}
        if not any(k in pliki for k in klucze):
            return
        for k in klucze:
            pliki.pop(k, None)
        stan["pliki"] = pliki
        rdzen.zapisz_json(_plik_stanu(), stan)


# =========================================================================== wspólny przebieg zapisu
def _sprawdz_wersje(bajty, wersja, pokaz):
    if not isinstance(wersja, str) or not wersja.strip():
        raise BladHTTP(400, "Brak pola „wersja” (znacznik z GET /api/sejf/plan) — odśwież plan i spróbuj jeszcze raz.")
    aktualna = sejf.wersja_bajtow(bajty)
    if wersja.strip() != aktualna:
        raise BladHTTP(409, "Ktoś zmienił plik %s, odkąd go wczytałeś — odśwież plan i spróbuj jeszcze raz."
                       % pokaz.rsplit("/", 1)[-1], kod="konflikt_wersji", wersja=aktualna)


def _wykonaj(klucz, wersja, zmiana, kto, znacznik=None):
    """Blokada → odczyt → kontrola wersji i treści → zmiana w pamięci → zapis atomowy → stan lokalny → dziennik → plan.

    `zmiana(dok)` zmienia Dokument i zwraca opis do dziennika (bez imienia), np. „odpowiedź na pytanie 16”.
    """
    if not _blokada.acquire(timeout=15):
        raise BladHTTP(409, "Trwa inny zapis do sejfu. Spróbuj za chwilę.")
    uwaga = None
    try:
        p, pokaz = _plik(klucz)
        _sprzataj_tymczasowe(os.path.dirname(p))
        przed = _czytaj_bajty(p, pokaz)
        _sprawdz_wersje(przed, wersja, pokaz)
        dok = Dokument(przed)
        _sprawdz_tresc(przed, dok, pokaz)
        opis = zmiana(dok)
        po = dok.bajty()
        if po == przed:
            raise BladHTTP(409, "Nic się nie zmieniło.")
        _zapisz(p, po, przed)
        try:
            _zapamietaj(p, przed, po, opis)
        except OSError as e:                                   # brak śladu dla „Wyślij” nie cofa zmiany w sejfie
            rdzen.log("zapis: nie udało się zapamiętać zmiany %s: %r" % (pokaz, e))
        kto_dz = _kto_w_dzienniku(kto, znacznik)
        try:
            _dopisz_do_dziennika(kto_dz, opis, _notatka(klucz))
        except (BladHTTP, OSError) as e:
            uwaga = "Zapisano, ale nie udało się dopisać śladu do Dziennika zmian: %s" % getattr(e, "komunikat", e)
            rdzen.log("zapis: dziennik: %s" % uwaga)
        rdzen.log("Sejf: %s — %s (%s)" % (pokaz, opis, kto_dz))
        nowa = sejf.wersja_bajtow(po)
    finally:
        sejf.uniewaznij()
        _blokada.release()
    wynik = {"ok": True, "opis": opis, "plik": pokaz, "wersja": nowa, "plan": sejf.plan()}
    if uwaga:
        wynik["uwaga"] = uwaga
    return wynik


def _dopisz_do_dziennika(kto, opis, notatka):
    """Wiersz „- <Imię>: <opis> ([[<notatka>]])” w sekcji dnia „## RRRR-MM-DD · Panel (ludzie)” (nowa sekcja na
    górze wpisów)."""
    p, pokaz = _plik("dziennik")
    przed = _czytaj_bajty(p, pokaz)
    dok = Dokument(przed)
    _sprawdz_tresc(przed, dok, pokaz)
    tytul = "%s · Panel (ludzie)" % dzis()
    wiersz = "- %s: %s ([[%s]])" % (kto, opis, notatka)
    naglowki = dok.naglowki()
    for i, poziom, tekst in naglowki:
        if poziom == 2 and tekst == tytul:
            dok.wstaw(dok.za_trescia(i, dok.koniec_sekcji(i, 2)), [wiersz])
            break
    else:
        pierwszy = next((i for i, poziom, tekst in naglowki if poziom == 2 and _RX_DATA_NAGLOWKA.match(tekst)), None)
        if pierwszy is not None:
            dok.wstaw(pierwszy, ["## " + tytul, wiersz, ""])
        else:
            koniec = len(dok)
            pusta = koniec == 0 or not dok.tresc(koniec - 1).strip()
            dok.wstaw(koniec, ([] if pusta else [""]) + ["## " + tytul, wiersz])
    _zapisz(p, dok.bajty(), przed)
    try:
        _zapamietaj(p, przed, dok.bajty(), opis)
    except OSError as e:
        rdzen.log("zapis: nie udało się zapamiętać zmiany dziennika: %r" % e)


def _jedna(trafienia, komunikat_brak, komunikat_wiele):
    """Dokładnie jedno trafienie — inaczej 404 (brak) albo 409 (powtórzony numer: nie zgadujemy, które zmienić)."""
    if not trafienia:
        raise BladHTTP(404, komunikat_brak)
    if len(trafienia) > 1:
        raise BladHTTP(409, komunikat_wiele, kod="powtorzony_numer")
    return trafienia[0]


# =========================================================================== 1. odpowiedź na pytanie otwarte
def _za_odpowiedziami(dok, j, koniec):
    """Miejsce na kolejny wiersz odpowiedzi: pod dotychczasowymi odpowiedziami (do pierwszej pustej linii albo `---`),
    z blokami kodu w całości (pusta linia w bloku kodu nie kończy odpowiedzi)."""
    plot = None
    while j < koniec:
        t = dok.tresc(j)
        if plot:
            if sejf.zamyka_plot(t, plot):
                plot = None
        else:
            m = sejf._RX_PLOT.match(t)
            if m:
                plot = m.group(1)
            elif not t.strip() or sejf._RX_LINIA_POZIOMA.match(t):
                break
        j += 1
    if plot:
        raise BladHTTP(409, "Odpowiedź ma niezamknięty blok kodu (```) — popraw ją w Obsidianie.")
    return j


def odpowiedz(nr, tekst, wersja, kto, znacznik=None):
    tekst = czysty_tekst(tekst, LIMIT_ODPOWIEDZI, "tekst")
    wiersz = "- %s (%s%s): %s" % (kto, (znacznik + ", ") if znacznik else "", dzis(), tekst)

    def zmiana(dok):
        trafienia = []
        for i, poziom, naglowek in dok.naglowki():
            m = _RX_NR_PYTANIA.match(naglowek)
            if poziom == 2 and m and int(m.group(1)) == nr:
                trafienia.append(i)
        i = _jedna(trafienia, "Nie ma pytania nr %d w Pytaniach otwartych" % nr,
                   "W Pytaniach otwartych są %d pytania nr %d — popraw numerację w Obsidianie, potem odpowiedz."
                   % (len(trafienia), nr))
        # sekcja jak w parserze planu: do następnego nagłówka ## (linia --- w treści pytania jej nie kończy)
        koniec = dok.koniec_sekcji(i, 2)
        if any(dok.tresc(j) == wiersz for j in range(i + 1, koniec)):
            raise BladHTTP(409, "Ta odpowiedź jest już zapisana pod pytaniem %d." % nr, kod="juz_zapisane")
        linia_odp = next((j for j in range(i + 1, koniec) if sejf._RX_ODPOWIEDZ.match(dok.tresc(j))), None)
        if linia_odp is None:                                 # pytanie bez wiersza „**Odpowiedź:**” — dopisz go
            granica = koniec
            if koniec == len(dok):                             # ostatnie pytanie: linia --- przed stopką pliku
                granica = next((j for j in range(i + 1, koniec) if sejf._RX_LINIA_POZIOMA.match(dok.tresc(j))), koniec)
            dok.wstaw(dok.za_trescia(i, granica), ["**Odpowiedź:**", wiersz])
            return "odpowiedź na pytanie %d" % nr
        dok.wstaw(_za_odpowiedziami(dok, linia_odp + 1, koniec), [wiersz])
        return "odpowiedź na pytanie %d" % nr

    return _wykonaj("pytania", wersja, zmiana, kto, znacznik)


# =========================================================================== 2. zadania
def _sekcje_h2(dok):
    """[(indeks nagłówka, koniec sekcji, nazwa małymi literami bez emoji)] sekcji ## pliku zadań."""
    wynik = []
    for i, poziom, tekst in dok.naglowki():
        if poziom == 2:
            nazwa = re.sub(r"[^\w\s()—–-]", "", tekst).strip().lower()
            wynik.append((i, dok.koniec_sekcji(i, 2), nazwa))
    return wynik


def _rodzaj_sekcji(nazwa):
    """Rodzaj sekcji po PIERWSZYM słowie nazwy (bez emoji): „Zrobione (archiwum backlogu)” to „zrobione”."""
    slowa = re.findall(r"\w+", nazwa)
    return slowa[0] if slowa and slowa[0] in RODZAJE_SEKCJI else "inna"


def _sekcja_rodzaju(sekcje, rodzaj):
    """(start, koniec) jedynej sekcji danego rodzaju, None gdy jej nie ma, 409 gdy jest ich kilka."""
    pasujace = [(s, k) for s, k, n in sekcje if _rodzaj_sekcji(n) == rodzaj]
    if len(pasujace) > 1:
        raise BladHTTP(409, "W pliku zadań są %d sekcje „%s” — połącz je w Obsidianie, potem spróbuj jeszcze raz."
                       % (len(pasujace), NAZWY_SEKCJI[rodzaj]), kod="powtorzona_sekcja")
    return pasujace[0] if pasujace else None


def _znaczniki_pol(linia):
    """Pozycje znaków stanu pól wyboru w linii `- [ ] A · [ ] B` (indeksy znaku między nawiasami)."""
    m = sejf._RX_POLE.match(linia)
    if not m:
        return []
    pozycje = [m.start(1)]
    for mm in _RX_ZNACZNIK_POLA.finditer(linia, m.end(1)):
        pozycje.append(mm.start(1))
    return pozycje


def _bez_priorytetu(t):
    mp = sejf._RX_PRIORYTET.search(t)
    return t[:mp.start()].rstrip(" ·").strip() if mp else t.strip()


def odhacz(id_zadania, tekst, wersja, kto, znacznik=None):
    if id_zadania is not None and (not isinstance(id_zadania, str) or not re.match(r"^z[0-9a-f]{10}$", id_zadania)):
        raise BladHTTP(400, "Niepoprawny identyfikator zadania (pole „id”)")
    if tekst is not None and not isinstance(tekst, str):
        raise BladHTTP(400, "Pole „tekst” musi być tekstem")
    szukany = unicodedata.normalize("NFC", tekst).strip() if tekst else None
    if not id_zadania and not szukany:
        raise BladHTTP(400, "Podaj „id” zadania (z planu) albo jego dokładny „tekst”")

    def pasuje(pole):
        if id_zadania:
            return sejf.id_zadania(pole) == id_zadania
        return szukany in (unicodedata.normalize("NFC", pole).strip(), _bez_priorytetu(unicodedata.normalize("NFC", pole)))

    def zmiana(dok):
        sekcje = _sekcje_h2(dok)
        juz_zrobione = False
        for start, koniec, nazwa in sekcje:
            rodzaj = _rodzaj_sekcji(nazwa)
            for i in range(start + 1, koniec):
                linia = dok.tresc(i)
                pola = sejf._pola_wyboru(linia)
                for k, (zrobione, pole) in enumerate(pola):
                    if not pasuje(pole):
                        continue
                    if zrobione:
                        juz_zrobione = True
                        continue
                    znaczniki = _znaczniki_pol(linia)
                    if len(znaczniki) != len(pola):
                        raise BladHTTP(409, "Nie rozumiem budowy tej linii zadań — odhacz ją w Obsidianie.")
                    tekst_zadania = _bez_priorytetu(pole)
                    # lista wielopolowa (assety), podzadanie, inna sekcja albo otwarta pozycja w „Zrobione”: [x] w miejscu
                    w_miejscu = len(pola) > 1 or rodzaj not in ("teraz", "backlog") or linia[:1] in (" ", "\t")
                    if w_miejscu:
                        dok.zamien(i, linia[:znaczniki[k]] + "x" + linia[znaczniki[k] + 1:])
                        return "odhaczone zadanie: %s" % skrot(tekst_zadania)
                    return _przenies_do_zrobionych(dok, sekcje, i, tekst_zadania)
        if juz_zrobione:
            raise BladHTTP(409, "To zadanie jest już odhaczone.")
        raise BladHTTP(404, "Nie ma takiego otwartego zadania — może ktoś je już zmienił. Odśwież plan.")

    return _wykonaj("zadania", wersja, zmiana, kto, znacznik)


def _przenies_do_zrobionych(dok, sekcje, i, tekst_zadania):
    """Zadanie z „Teraz”/„Backlog” znika i trafia na górę „Zrobione” jako `- [x] RRRR-MM-DD: tekst`."""
    ile = 1                                                    # wcięte linie pod zadaniem idą razem z nim
    while i + ile < len(dok) and dok.tresc(i + ile)[:1] in (" ", "\t") and dok.tresc(i + ile).strip() \
            and not sejf._RX_NAGLOWEK.match(dok.tresc(i + ile)):
        ile += 1
    dalsze = [dok.tresc(j) for j in range(i + 1, i + ile)]
    otwarte = [pole for l in dalsze for zrobione, pole in sejf._pola_wyboru(l) if not zrobione]
    if otwarte:                                                # w „Zrobione” liczyłyby się dalej jako otwarte
        raise BladHTTP(409, "To zadanie ma otwarte podzadania (np. „%s”) — najpierw odhacz je, potem całe zadanie."
                       % skrot(otwarte[0], 60), kod="otwarte_podzadania")
    nowe = ["- [x] %s: %s" % (dzis(), tekst_zadania)] + dalsze
    zrobione = _sekcja_rodzaju(sekcje, "zrobione")
    if zrobione is None:                                       # brak sekcji „Zrobione”: dopisz ją na końcu pliku
        dok.usun(i, ile)
        koniec = len(dok)
        pusta = koniec == 0 or not dok.tresc(koniec - 1).strip()
        dok.wstaw(koniec, ([] if pusta else [""]) + ["## ✅ Zrobione"] + nowe)
    else:
        s, k = zrobione
        cel = next((j for j in range(s + 1, k) if _RX_LISTA.match(dok.tresc(j))), None)
        if cel is None:
            cel = dok.za_trescia(s, k)
        if cel > i:                                            # najpierw wstaw dalej w pliku, potem usuń wcześniej
            dok.wstaw(cel, nowe)
            dok.usun(i, ile)
        else:
            dok.usun(i, ile)
            dok.wstaw(cel, nowe)
    return "odhaczone zadanie: %s" % skrot(tekst_zadania)


def dodaj_zadanie(tekst, sekcja, priorytet, wersja, kto, znacznik=None):
    tekst = czysty_tekst(tekst, LIMIT_ZADANIA, "tekst")
    if sejf._RX_PRIORYTET.search(tekst):
        raise BladHTTP(400, "Priorytet wybierz w polu „priorytet”, nie w treści zadania")
    if sekcja not in SEKCJE_DODAWANIA:
        raise BladHTTP(400, "Pole „sekcja” musi mieć wartość „teraz” albo „backlog”")
    if priorytet not in PRIORYTETY:
        raise BladHTTP(400, "Pole „priorytet” musi mieć wartość „wysoki”, „średni” albo „niski”")
    wiersz = "- [ ] %s · #%s" % (tekst, PRIORYTETY[priorytet])

    def zmiana(dok):
        sekcje = _sekcje_h2(dok)
        for start, koniec, nazwa in sekcje:                    # bez dubli: identyczne otwarte zadanie już jest
            for i in range(start + 1, koniec):
                for zrobione, pole in sejf._pola_wyboru(dok.tresc(i)):
                    if not zrobione and _bez_priorytetu(pole) == tekst:
                        raise BladHTTP(409, "Takie zadanie już jest na liście.", kod="juz_zapisane")
        cel = _sekcja_rodzaju(sekcje, sekcja)
        if cel is None:
            raise BladHTTP(404, "W pliku zadań nie ma sekcji „%s”" % NAZWY_SEKCJI[sekcja])
        dok.wstaw(dok.za_trescia(cel[0], cel[1]), [wiersz])
        return "dodane zadanie: %s (%s)" % (skrot(tekst), NAZWY_SEKCJI[sekcja])

    return _wykonaj("zadania", wersja, zmiana, kto, znacznik)


# =========================================================================== 3. status decyzji (Karol albo Paweł)
def _wiersz_statusu(linia, emoji, slowo, podpis_txt):
    """Nowy wiersz statusu: podmienia TYLKO emoji i słowo statusu w pierwszym polu, usuwa poprzedni podpis panelu
    („zdecydował: …” / „oznaczył: …” — także dawny „zdecydował: Game Director (Paweł) 2026-11-13”) i dopisuje nowy
    na końcu. Reszta wiersza (dopiski, pola, odstępy) bez zmian."""
    m = _RX_STATUS_NA_POCZATKU.match(linia)
    if not m or not (m.group("emoji") or m.group("slowo")):
        raise BladHTTP(409, "Nie rozumiem wiersza statusu tej decyzji — zmień go w Obsidianie.")
    if m.group("slowo"):
        reszta = linia[m.end("slowo"):]
        nowy = m.group("wciecie") + emoji + " " + m.group("format") + slowo + reszta
    else:                                                      # samo emoji („💡 · styl”): słowo dochodzi za nim
        nowy = m.group("wciecie") + emoji + " " + slowo + linia[m.end("emoji"):]
    nowy = _RX_STARY_PODPIS.sub("", nowy)
    tresc = nowy.rstrip()
    ogon = nowy[len(tresc):]                                   # spacje na końcu wiersza zostają
    if tresc.endswith("·"):
        tresc = tresc[:-1].rstrip()
    return tresc + " · " + podpis_txt + ogon


def zmien_status_decyzji(id_decyzji, status, uzasadnienie, wersja, kto, znacznik=None):
    """Zmiana statusu decyzji — wołać tylko dla decydenta (klucz zatwierdzania albo klucz lokalny, patrz `_t_status`).

    W Rejestrze decyzji podpis to samo imię i data („zdecydował: Paweł 2026-11-13”); znacznik zaufania
    („klucz zatwierdzania” albo None dla osoby przy komputerze) trafia tylko do Dziennika zmian."""
    m = re.match(r"^D-(\d{1,4})$", str(id_decyzji or ""), re.IGNORECASE)
    if not m:
        raise BladHTTP(400, "Niepoprawny identyfikator decyzji (oczekiwano np. D-019)")
    numer = int(m.group(1))
    if status not in STATUSY_DOCELOWE:
        raise BladHTTP(400, "Pole „status” musi mieć wartość „zatwierdzona”, „odrzucona” albo „do_decyzji”")
    if bez_imienia(kto):
        raise BladHTTP(400, KOMUNIKAT_BRAK_IMIENIA, kod="brak_imienia")
    uzasadnienie = czysty_tekst(uzasadnienie, LIMIT_UZASADNIENIA, "uzasadnienie", wymagany=False)
    emoji, slowo, w_dzienniku, czasownik = STATUSY_DOCELOWE[status]
    data = dzis()

    def zmiana(dok):
        trafienia = []
        for i, poziom, naglowek in dok.naglowki():
            mm = _RX_NR_DECYZJI.match(naglowek)
            if poziom == 3 and mm and int(mm.group(1)) == numer:
                trafienia.append((i, "D-%s" % mm.group(1)))
        i, ident = _jedna(trafienia, "Nie ma decyzji D-%03d w Rejestrze decyzji" % numer,
                          "W Rejestrze decyzji są %d decyzje D-%03d — popraw numerację w Obsidianie, potem zatwierdzaj."
                          % (len(trafienia), numer))
        koniec = dok.koniec_sekcji(i, 3, na_linii_poziomej=True)
        j = next((k for k in range(i + 1, koniec) if dok.tresc(k).strip()), None)
        st = sejf._linia_statusu(dok.tresc(j)) if j is not None else None
        obecny = st[0] if st else "propozycja"
        if obecny not in STATUSY_ZMIENIALNE:
            raise BladHTTP(409, "%s ma już status „%s” — takiej decyzji się nie przepisuje. Dodaj nową decyzję, "
                                "która ją zastąpi." % (ident, NAZWY_STATUSOW.get(obecny, obecny)), kod="status_zamkniety")
        if obecny == status:
            raise BladHTTP(409, "%s ma już status „%s”." % (ident, NAZWY_STATUSOW[status]))
        podpis_txt = "%s: %s %s" % (czasownik, kto, data)
        if st:
            dok.zamien(j, _wiersz_statusu(dok.tresc(j), emoji, slowo, podpis_txt))
        else:                                                  # decyzja bez wiersza statusu: dopisz go pod nagłówkiem
            dok.wstaw(i + 1, ["%s %s · %s" % (emoji, slowo, podpis_txt)])
            koniec += 1
        if uzasadnienie:
            dok.wstaw(dok.za_trescia(i, koniec), ["Uzasadnienie — %s, %s: %s" % (kto, data, uzasadnienie)])
        return "decyzja %s %s" % (ident, w_dzienniku)

    return _wykonaj("decyzje", wersja, zmiana, kto, znacznik)


# =========================================================================== trasy
def _dane(z, dozwolone):
    if not dostepny():
        raise BladHTTP(403, "Zapis do sejfu z panelu jest wyłączony (ustawienie „zapis_sejfu” w konfiguracji).")
    d = z.json
    if not isinstance(d, dict):
        raise BladHTTP(400, "Oczekiwano obiektu JSON")
    nieznane = set(d) - set(dozwolone)
    if nieznane:
        raise BladHTTP(400, "Nieznane pola: %s" % ", ".join(sorted(nieznane)))
    _sprawdz_limit(z)
    return d


def _t_odpowiedz(z):
    d = _dane(z, ("tekst", "wersja"))
    try:
        nr = int(z.params["nr"])
    except (TypeError, ValueError):
        raise BladHTTP(400, "Numer pytania musi być liczbą")
    if not 1 <= nr <= 9999 or not re.match(r"^\d{1,4}$", z.params["nr"]):
        raise BladHTTP(400, "Niepoprawny numer pytania")
    kto, znacznik = podpis(z)
    return odpowiedz(nr, d.get("tekst"), d.get("wersja"), kto, znacznik)


def _t_odhacz(z):
    d = _dane(z, ("id", "tekst", "wersja"))
    kto, znacznik = podpis(z)
    return odhacz(d.get("id"), d.get("tekst"), d.get("wersja"), kto, znacznik)


def _t_dodaj(z):
    d = _dane(z, ("tekst", "sekcja", "priorytet", "wersja"))
    kto, znacznik = podpis(z)
    return dodaj_zadanie(d.get("tekst"), d.get("sekcja"), d.get("priorytet"), d.get("wersja"), kto, znacznik)


def _t_status(z):
    if not decydent(z):
        if not dostepny():
            raise BladHTTP(403, "Zapis do sejfu z panelu jest wyłączony (ustawienie „zapis_sejfu” w konfiguracji).")
        raise BladHTTP(403, "Status decyzji zmienia Karol albo Paweł: przy komputerze z panelem albo w przeglądarce "
                            "z kluczem zatwierdzania. Link z kluczem wypisuje na komputerze z panelem polecenie: "
                            "python panel/serwer.py --klucz-zatwierdzania. Możesz zostawić komentarz pod decyzją.",
                       kod="brak_klucza_zatwierdzania")
    d = _dane(z, ("status", "uzasadnienie", "wersja"))
    if not getattr(z, "kto_z_naglowka", False):
        # Imię nie przyszło z Ustawień (X-BC-Kto), tylko serwer wziął domyślne z `git config user.name` albo z nazwy
        # konta systemu. Takie imię nie podpisuje decyzji: trafiłoby do publicznego Rejestru bez wiedzy człowieka.
        raise BladHTTP(400, KOMUNIKAT_BRAK_IMIENIA, kod="brak_imienia")
    kto, znacznik = podpis(z)
    return zmien_status_decyzji(z.params["id"], d.get("status"), d.get("uzasadnienie"), d.get("wersja"), kto, znacznik)


def zarejestruj(app):
    app.dodaj("POST", "/api/sejf/pytania/<nr>/odpowiedz", _t_odpowiedz)
    app.dodaj("POST", "/api/sejf/zadania/odhacz", _t_odhacz)
    app.dodaj("POST", "/api/sejf/zadania/dodaj", _t_dodaj)
    app.dodaj("POST", "/api/sejf/decyzje/<id>/status", _t_status)


def zdrowie():
    pliki = sejf.pliki_planu()
    stan = rdzen.czytaj_json(_plik_stanu(), {}) or {}
    return {"ok": True, "zapis": dostepny(),
            "pliki": {pokaz: os.path.isfile(p) for k, (p, pokaz) in pliki.items() if k != "roadmapa"},
            "zmienione_przez_panel": len(stan.get("pliki") or {})}
