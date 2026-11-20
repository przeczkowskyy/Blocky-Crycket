# -*- coding: utf-8 -*-
"""Wytwórnia pomysłów: lejek gier i pomysłów, karta pomysłu, portfel gier z pulpitem gry, radar trendów, oceny ludzi.

Zasada D-008/D-028: dane leżą w sejfie, panel jest tylko oknem. Wszystko czyta z notatek folderu
`<sejf B&C>/Wytwórnia/` (przez indeks bc/sejf.py) i zapisuje tą samą drogą co reszta panelu (bc/zapis.py:
blokada sejfu, kontrola wersji, zapis atomowy, ślad w Dzienniku zmian „Panel (ludzie)”, ślad dla „Wyślij”):

- `Wytwórnia/Pomysły/<Nazwa>.md` — jedna notatka na grę albo pomysł. Płaski frontmatter: `typ`, `gra` (krótka
  nazwa), `etap` (pomysł | ocena | prototyp | test | publiczna | wstrzymana | porzucona), `zdanie`, `ocena_agenta`,
  `werdykt_agenta` (buduj | popraw | odrzuć), `ocena_karol`, `ocena_pawel`, `d1`, `d7`, `sesja_min`, `ccu`,
  `miejsce` (placeId), opcjonalnie `aliases` (inne nazwy gry — do dopasowania raportów, zadań i decyzji).
  Sekcje `##`: W jednym zdaniu, Pierwsze 10 sekund, Hak ciekawości, Głębia, Inni gracze i pokazanie się, Moment do
  nagrania, Powód powrotu, Karta oceny (tabela `| Kryterium | Agent | Karol | Paweł |`, 10 wierszy, 0–3),
  Krytyka agenta, Najtańszy test, Powiązane.
- `Wytwórnia/Radar trendów.md` — tabela `| Trend | Przykłady | Siła | Kierunek | Źródło |`, `aktualizacja:` we
  frontmatterze.
- `Wytwórnia/Karta oceny pomysłu.md` — opis 10 kryteriów (panel bierze z niej opisy do formularza oceny).
- `Szablony/Pomysł gry.md` — szablon nowej notatki (bez niego panel bierze wbudowany, o tej samej budowie).

Uprawnienia: nowy pomysł dodaje każdy z dostępem (gość z kodem dostępu też, z limitem zapisów gościa — jak zadanie).
Ocenę (kolumna Karol / Paweł w Karcie oceny i suma `ocena_karol` / `ocena_pawel`) i etap zmienia tylko decydent
(klucz lokalny albo klucz zatwierdzania) z imieniem z Ustawień — jak status decyzji; gość dostaje 403
`brak_klucza_zatwierdzania`. Kolumnę oceny wybiera imię z Ustawień (Karol albo Paweł, porównane kanonicznie).

Pulpit gry (reguła do czasu tagów): raporty panelu, których TYTUŁ ZACZYNA SIĘ od nazwy gry, oraz zadania z
`Zadania.md` i decyzje z `Rejestr decyzji.md`, które WSPOMINAJĄ nazwę gry (całe słowo, bez wielkości liter).
Nazwy gry = pole `gra`, nazwa notatki i `aliases` / `aliasy` z frontmattera.
"""
import os
import re
import unicodedata

from . import rdzen, sejf, zapis
from .rdzen import BladHTTP

FOLDER = "Wytwórnia"
PODFOLDER = "Pomysły"
PLIK_RADARU = "Radar trendów.md"
PLIK_KARTY = "Karta oceny pomysłu.md"
SZABLON = ("Szablony", "Pomysł gry.md")

ETAPY = ("pomysł", "ocena", "prototyp", "test", "publiczna", "wstrzymana", "porzucona")
ETAPY_LEJKA = ETAPY[:5]                                        # kolumny lejka; wstrzymane i porzucone osobno
ETAPY_GIER = ("prototyp", "test", "publiczna")                 # portfel gier (pulpit gry)
NAZWY_ETAPOW = {"pomysł": "Pomysł", "ocena": "Ocena", "prototyp": "Prototyp", "test": "Test", "publiczna": "Publiczna",
                "wstrzymana": "Wstrzymana", "porzucona": "Porzucona"}
KRYTERIA = ("Jedno zdanie", "Pierwsze 10 sekund", "Hak ciekawości", "Głębia", "Inni gracze", "Pokazanie się",
            "Moment do nagrania", "Powód powrotu", "Trend", "Koszt dla nas")
MAKS_KRYTERIUM = 3
MAKS_SUMY = MAKS_KRYTERIUM * len(KRYTERIA)                    # 30
WERDYKTY = ("buduj", "popraw", "odrzuć")
METRYKI = ("d1", "d7", "sesja_min", "ccu")
OSOBY_OCEN = {"karol": ("Karol", "ocena_karol"), "pawel": ("Paweł", "ocena_pawel")}
LIMIT_NAZWY = 60
LIMIT_ZDANIA = 300
LIMIT_HAKA = 600
ZAKAZANE_W_NAZWIE = set('\\/:*?"<>|#^[]{}')
ZASTRZEZONE_NAZWY = {"con", "prn", "aux", "nul"} | {"com%d" % i for i in range(1, 10)} | {"lpt%d" % i for i in range(1, 10)}

REGULA_PULPITU = ("Raporty panelu, których tytuł zaczyna się od nazwy gry, oraz zadania i decyzje, które wspominają "
                  "nazwę gry (całe słowo, bez wielkości liter). Nazwy: pole „gra”, nazwa notatki i „aliases”.")

SZABLON_WBUDOWANY = """---
status: propozycja
typ: pomysł-gry
gra: {{nazwa}}
etap: pomysł
zdanie: ""
ocena_agenta:
werdykt_agenta:
ocena_karol:
ocena_pawel:
d1:
d7:
sesja_min:
ccu:
miejsce:
tags: [wytwórnia, pomysł]
---
# {{nazwa}}

## W jednym zdaniu

## Pierwsze 10 sekund

## Hak ciekawości

## Głębia

## Inni gracze i pokazanie się

## Moment do nagrania

## Powód powrotu

## Karta oceny
| Kryterium | Agent | Karol | Paweł |
|---|---|---|---|
""" + "".join("| %s |  |  |  |\n" % k for k in KRYTERIA) + """
## Krytyka agenta

## Najtańszy test

## Powiązane
- [[Karta oceny pomysłu]]
"""


# =========================================================================== drobiazgi
def _proste(s):
    """Do porównań: NFC, małe litery, bez polskich znaków i formatowania Markdown, pojedyncze spacje."""
    t = unicodedata.normalize("NFD", str(s or "").casefold().replace("ł", "l"))
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[*_`~]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def etap(wartosc):
    """Etap z frontmattera → jeden z ETAPY (bez wielkości liter i polskich znaków, też „publiczny”, „wstrzymany”).
    Pusty albo nieznany = „pomysł”."""
    p = _proste(wartosc)
    if not p:
        return "pomysł"
    for e in ETAPY:
        pe = _proste(e)
        if p == pe or (len(p) >= 5 and p[:-1] == pe[:-1]):    # publiczna / publiczny, wstrzymana / wstrzymany
            return e
    return "pomysł"


def _liczba(v):
    """Liczba z frontmattera („17”, 17, „17/30”, „12%”, „12,5”) albo None."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return v
    m = re.match(r"^\s*(-?\d+(?:[.,]\d+)?)", str(v))
    if not m:
        return None
    t = m.group(1).replace(",", ".")
    return float(t) if "." in t else int(t)


def _werdykt(v):
    p = _proste(v)
    for w in WERDYKTY:
        if p and p.startswith(_proste(w)[:4]):                 # buduj / popraw(ić) / odrzuć (odrzucić)
            return w
    return None


def _tekst(v):
    if v is None or isinstance(v, (dict, list)):
        return ""
    return str(v).strip()


def _baza():
    """(id sejfu, ścieżka bezwzględna) sejfu B&C albo 503."""
    s = sejf._sejf_planu()
    if not s:
        raise BladHTTP(503, "Panel nie widzi sejfu B&C — sprawdź listę sejfów w konfiguracji.")
    return s[0], s[2]


def _pokaz(sid, baza, sciezka):
    if sejf._w_repo(baza):
        return sejf._nfc(rdzen.wzgledem_repo(sciezka))
    return "sejf:%s/%s" % (sid, sejf._nfc(os.path.relpath(sciezka, baza).replace("\\", "/")))


def folder_pomyslow():
    sid, baza = _baza()
    return os.path.join(baza, FOLDER, PODFOLDER)


# =========================================================================== tabele Markdown
_RX_WIERSZ_TABELI = re.compile(r"^\s*\|.*\|\s*$")
_RX_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")


def komorki(linia):
    """`| a | b \\| c |` → ["a", "b \\| c"] (z odstępami). Tylko wiersz zaczynający i kończący się `|`."""
    s = linia.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return re.split(r"(?<!\\)\|", s)


def _tabele(linie):
    """[(indeks pierwszej linii, [indeksy wierszy danych], nagłówek: [komórki])] tabel w liniach (bez bloków kodu)."""
    wynik, i, n, plot = [], 0, len(linie), None
    while i < n:
        l = linie[i]
        m = sejf._RX_PLOT.match(l)
        if plot:
            if sejf.zamyka_plot(l, plot):
                plot = None
            i += 1
            continue
        if m:
            plot = m.group(1)
            i += 1
            continue
        if _RX_WIERSZ_TABELI.match(l) and i + 1 < n and _RX_SEPARATOR.match(linie[i + 1]):
            naglowek = [c.strip() for c in komorki(l)]
            dane, j = [], i + 2
            while j < n and _RX_WIERSZ_TABELI.match(linie[j]):
                dane.append(j)
                j += 1
            wynik.append((i, dane, naglowek))
            i = j
            continue
        i += 1
    return wynik


def _czysta_komorka(c):
    t = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", c or "")
    t = re.sub(r"\[\[([^\]]+)\]\]", r"\1", t)
    return re.sub(r"[*_`]", "", t).replace("\\|", "|").strip()


def _ocena_komorki(c):
    """Wartość 0–3 z komórki („2”, „**3**”, „2/3”) albo None (puste, „—”, „?”)."""
    m = re.match(r"^\s*(\d+)", _czysta_komorka(c))
    if not m:
        return None
    v = int(m.group(1))
    return v if 0 <= v <= MAKS_KRYTERIUM else None


def _indeks_kryterium(nazwa):
    """Indeks w KRYTERIA dla nazwy z tabeli („Inni gracze”, „**Trend**”, „1. Jedno zdanie”) albo None."""
    p = re.sub(r"^\d+[.)]\s*", "", _proste(_czysta_komorka(nazwa)))
    if not p:
        return None
    for i, k in enumerate(KRYTERIA):
        if p == _proste(k):
            return i
    for i, k in enumerate(KRYTERIA):
        pk = _proste(k)
        if p.startswith(pk) or pk.startswith(p):
            return i
    return None


def _kolumny(naglowek):
    """{"agent": i, "karol": i, "pawel": i} — indeksy kolumn tabeli karty oceny (po początku nagłówka)."""
    wynik = {}
    for i, h in enumerate(naglowek):
        p = _proste(_czysta_komorka(h))
        for klucz in ("agent", "karol", "pawel"):
            if p.startswith(klucz) and klucz not in wynik:
                wynik[klucz] = i
    return wynik


def karta_z_linii(linie):
    """Karta oceny z linii sekcji: [{kryterium, agent, karol, pawel}] w kolejności KRYTERIA (brak = None)."""
    karta = [{"kryterium": k, "agent": None, "karol": None, "pawel": None} for k in KRYTERIA]
    tabele = [t for t in _tabele(linie) if "agent" in _kolumny(t[2]) or len(_kolumny(t[2])) >= 2]
    if not tabele:
        return karta, False
    _, dane, naglowek = tabele[0]
    kol = _kolumny(naglowek)
    bez_nazwy = 0
    for j in dane:
        c = komorki(linie[j])
        i = _indeks_kryterium(c[0] if c else "")
        if i is None:                                          # wiersz bez znanej nazwy: kolejny wolny
            while bez_nazwy < len(KRYTERIA) and any(karta[bez_nazwy][o] is not None for o in kol):
                bez_nazwy += 1
            if bez_nazwy >= len(KRYTERIA):
                continue
            i = bez_nazwy
        for o, k in kol.items():
            if k < len(c):
                karta[i][o] = _ocena_komorki(c[k])
    return karta, True


def suma(karta, kolumna):
    wartosci = [w[kolumna] for w in karta if w.get(kolumna) is not None]
    return sum(wartosci) if wartosci else None


# =========================================================================== odczyt notatek
def _sekcja(tresc, poczatek_nazwy):
    """Linie sekcji `## <nazwa…>` (porównanie bez wielkości liter i polskich znaków) albo None."""
    p = _proste(poczatek_nazwy)
    for naglowek, linie in sejf._sekcje(tresc, 2):
        if _proste(naglowek).startswith(p):
            return linie
    return None


def _pierwszy_akapit(linie, n=400):
    tekst = []
    for l in linie or []:
        s = l.strip()
        if not s:
            if tekst:
                break
            continue
        if s.startswith(">") or s.startswith("%%") or s.startswith("<!--") or s.startswith("|"):
            continue
        tekst.append(re.sub(r"^[-*+]\s+", "", s))
    t = " ".join(tekst)
    return t if len(t) <= n else t[:n - 1].rstrip() + "…"


def _notatki_pomyslow():
    """Notatki z <sejf B&C>/Wytwórnia/Pomysły/ z indeksu sejfu (pamięć podręczna bc/sejf.py)."""
    sid, _ = _baza()
    folder = sejf._klucz("%s/%s" % (FOLDER, PODFOLDER))
    return [n for n in sejf.indeks()["notatki"] if n["sejf"] == sid and sejf._klucz(n["folder"]) == folder]


def _notatka_wytworni(nazwa_pliku):
    sid, _ = _baza()
    cel = sejf._klucz("%s/%s" % (FOLDER, nazwa_pliku))
    return next((n for n in sejf.indeks()["notatki"] if n["sejf"] == sid and sejf._klucz(n["wzgl"]) == cel), None)


def _aliasy(fm):
    surowe = fm.get("aliases", fm.get("aliasy", fm.get("alias")))
    if surowe is None:
        return []
    lista = surowe if isinstance(surowe, list) else [surowe]
    return [str(a).strip() for a in lista if a is not None and not isinstance(a, (dict, list)) and str(a).strip()]


def karta_pomyslu(n):
    """Karta lejka z notatki indeksu: nazwa, zdanie, etap, oceny (sumy 0–30), werdykt, metryki."""
    fm = n["fm"] or {}
    tresc = n["tresc"]
    karta, ma_tabele = karta_z_linii(_sekcja(tresc, "Karta oceny") or [])
    oceny = {}
    for kolumna, pole in (("agent", "ocena_agenta"), ("karol", "ocena_karol"), ("pawel", "ocena_pawel")):
        v = _liczba(fm.get(pole))
        oceny[kolumna] = v if v is not None else suma(karta, kolumna)
    zdanie = _tekst(fm.get("zdanie")) or _pierwszy_akapit(_sekcja(tresc, "W jednym zdaniu"), 300)
    metryki = {}
    for m in METRYKI:
        v = fm.get(m)
        metryki[m] = None if v is None or v == "" or isinstance(v, (dict, list, bool)) else v
    miejsce = _tekst(fm.get("miejsce"))
    return {
        "id": n["tytul"], "nazwa": _tekst(fm.get("gra")) or n["tytul"], "tytul": n["tytul"], "sciezka": n["sciezka"],
        "etap": etap(fm.get("etap")), "etap_surowy": _tekst(fm.get("etap")), "zdanie": zdanie,
        "ocena_agenta": oceny["agent"], "ocena_karol": oceny["karol"], "ocena_pawel": oceny["pawel"],
        "werdykt_agenta": _werdykt(fm.get("werdykt_agenta")), "werdykt_surowy": _tekst(fm.get("werdykt_agenta")),
        "metryki": metryki, "miejsce": miejsce if re.match(r"^\d{1,20}$", miejsce) else None,
        "status": n["status"], "typ": _tekst(fm.get("typ")), "aliasy": _aliasy(fm), "zmieniono": n["zmieniono"],
        "ma_karte": ma_tabele,
    }


def kryteria():
    """[{nazwa, opis}] — opisy z notatki „Karta oceny pomysłu” (nagłówek, wiersz tabeli albo punkt listy z nazwą)."""
    n = _notatka_wytworni(PLIK_KARTY)
    opisy, skale = {}, {}
    if n:
        linie = n["tresc"].split("\n")
        for _, dane, naglowek in _tabele(linie):               # | # | Kryterium | Pytanie | 0 | 3 | albo | Kryterium | Opis |
            h = [_proste(_czysta_komorka(x)) for x in naglowek]
            k_nazwa = next((i for i, x in enumerate(h) if x.startswith("kryter")), 0)
            k_opis = next((i for i, x in enumerate(h) if x.startswith("pytanie") or x.startswith("opis")), k_nazwa + 1)
            k_0 = next((i for i, x in enumerate(h) if x == "0"), None)
            k_3 = next((i for i, x in enumerate(h) if x == str(MAKS_KRYTERIUM)), None)
            for j in dane:
                c = komorki(linie[j])
                i = _indeks_kryterium(c[k_nazwa]) if k_nazwa < len(c) else None
                if i is None or i in opisy:
                    continue
                if k_opis < len(c) and _czysta_komorka(c[k_opis]):
                    opisy[i] = _czysta_komorka(c[k_opis])
                if k_0 is not None and k_3 is not None and max(k_0, k_3) < len(c):
                    skale[i] = {"0": _czysta_komorka(c[k_0]), str(MAKS_KRYTERIUM): _czysta_komorka(c[k_3])}
        for naglowek, cialo in sejf._sekcje(n["tresc"], 2) + sejf._sekcje(n["tresc"], 3):
            i = _indeks_kryterium(naglowek)
            if i is not None and i not in opisy:
                opisy[i] = _pierwszy_akapit(cialo, 300)
        for l in linie:                                        # - **Nazwa** — opis / 1. **Nazwa**: opis
            m = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+\*\*(.+?)\*\*\s*[:—–-]?\s*(.*)$", l)
            if m:
                i = _indeks_kryterium(m.group(1))
                if i is not None and i not in opisy and m.group(2).strip():
                    opisy[i] = m.group(2).strip()[:300]
    return [{"nazwa": k, "opis": opisy.get(i, ""), "skala": skale.get(i)} for i, k in enumerate(KRYTERIA)]


def radar():
    """{jest, sciezka, aktualizacja, kolumny, pozycje:[{trend, przyklady, sila, kierunek, zrodlo}]}."""
    n = _notatka_wytworni(PLIK_RADARU)
    if not n:
        return {"jest": False, "sciezka": None, "aktualizacja": None, "kolumny": [], "pozycje": []}
    linie = n["tresc"].split("\n")
    klucze = {"trend": "trend", "przyklad": "przyklady", "sila": "sila", "kierunek": "kierunek", "zrodl": "zrodlo"}
    pozycje, kolumny = [], []
    for _, dane, naglowek in _tabele(linie):
        mapa = {}
        for i, h in enumerate(naglowek):
            p = _proste(_czysta_komorka(h))
            for poczatek, klucz in klucze.items():
                if p.startswith(poczatek) and klucz not in mapa.values():
                    mapa[i] = klucz
        if "trend" not in mapa.values():
            continue
        kolumny = [_czysta_komorka(h) for h in naglowek]
        for j in dane:
            c = komorki(linie[j])
            poz = {k: "" for k in klucze.values()}
            for i, klucz in mapa.items():
                if i < len(c):
                    poz[klucz] = c[i].strip()                  # Markdown zostaje (linki), interfejs renderuje
            if any(poz.values()):
                pozycje.append(poz)
        break
    fm = n["fm"] or {}
    return {"jest": True, "sciezka": n["sciezka"], "aktualizacja": _tekst(fm.get("aktualizacja")) or None,
            "kolumny": kolumny, "pozycje": pozycje, "zmieniono": n["zmieniono"]}


def lista():
    """GET /api/wytwornia: pomysły, lejek, portfel gier, radar, kryteria."""
    try:
        sid, baza = _baza()
    except BladHTTP:
        return {"jest": False, "pomysly": [], "lejek": {e: [] for e in ETAPY}, "gry": [], "etapy": list(ETAPY),
                "radar": {"jest": False, "pozycje": []}, "kryteria": [{"nazwa": k, "opis": ""} for k in KRYTERIA]}
    pomysly = []
    for n in _notatki_pomyslow():
        try:
            pomysly.append(karta_pomyslu(n))
        except Exception as e:                                 # jedna dziwna notatka nie psuje Wytwórni
            rdzen.log("wytwórnia: nie udało się odczytać %s: %r" % (n["sciezka"], e))
    pomysly.sort(key=lambda p: (-(p["ocena_agenta"] or -1), p["nazwa"].lower()))
    lejek = {e: [p["id"] for p in pomysly if p["etap"] == e] for e in ETAPY}
    folder = os.path.join(baza, FOLDER)
    szablon = os.path.join(baza, *SZABLON)
    return {
        "jest": os.path.isdir(folder), "pomysly": pomysly, "lejek": lejek, "etapy": list(ETAPY),
        "etapy_lejka": list(ETAPY_LEJKA), "etapy_gier": list(ETAPY_GIER), "nazwy_etapow": NAZWY_ETAPOW,
        "gry": [p["id"] for p in pomysly if p["etap"] in ETAPY_GIER], "radar": radar(), "kryteria": kryteria(),
        "maks_sumy": MAKS_SUMY, "werdykty": list(WERDYKTY),
        "pliki": {"folder": _pokaz(sid, baza, folder), "pomysly": _pokaz(sid, baza, os.path.join(folder, PODFOLDER)),
                  "szablon": _pokaz(sid, baza, szablon), "szablon_jest": os.path.isfile(szablon)},
        "funkcje": {"dodaj": True, "ocena": True, "etap": True, "pulpit_gry": True},
    }


def _sprawdz_id(ident):
    t = sejf._nfc(str(ident or "")).strip()
    if not t or len(t) > 120 or "/" in t or "\\" in t or "\x00" in t or t in (".", "..") or t.startswith("."):
        raise BladHTTP(400, "Niepoprawny identyfikator pomysłu")
    return t


def _znajdz(ident):
    """Notatka pomysłu o nazwie pliku `ident` (najpierw dokładnie, potem bez wielkości liter) albo 404."""
    ident = _sprawdz_id(ident)
    notatki = _notatki_pomyslow()
    n = next((x for x in notatki if x["tytul"] == ident), None)
    if n is None:
        n = next((x for x in notatki if x["tytul"].casefold() == ident.casefold()), None)
    if n is None:
        raise BladHTTP(404, "Nie ma pomysłu „%s” w Wytwórni (może został przeniesiony albo usunięty)." % ident)
    return n


def szczegol(ident):
    """Karta pomysłu z całą notatką: sekcje, karta oceny (10 kryteriów × Agent/Karol/Paweł), krytyka, wersja pliku."""
    n = _znajdz(ident)
    p = karta_pomyslu(n)
    try:
        with open(n["abs"], "rb") as f:
            wersja = sejf.wersja_bajtow(f.read())
    except OSError:
        wersja = None
    karta, _ = karta_z_linii(_sekcja(n["tresc"], "Karta oceny") or [])
    sekcje = [{"tytul": t, "tresc_md": "\n".join(l).strip()} for t, l in sejf._sekcje(n["tresc"], 2)]
    krytyka = _sekcja(n["tresc"], "Krytyka agenta")
    p.update({"frontmatter": n["fm"], "tresc_md": n["tresc"], "sekcje": sekcje, "karta": karta,
              "krytyka_md": "\n".join(krytyka).strip() if krytyka else "", "wersja": wersja,
              "sumy": {k: suma(karta, k) for k in ("agent", "karol", "pawel")}, "maks_sumy": MAKS_SUMY})
    return p


# =========================================================================== pulpit gry
def nazwy_gry(p):
    nazwy = []
    for n in [p.get("nazwa"), p.get("tytul")] + list(p.get("aliasy") or []):
        n = re.sub(r"\s+", " ", str(n or "")).strip()
        if len(n) >= 2 and n.casefold() not in [x.casefold() for x in nazwy]:
            nazwy.append(n)
    return nazwy


def _zaczyna_sie(tytul, nazwy):
    t = re.sub(r"^[^\w]+", "", str(tytul or "")).strip()         # bez emoji i znaków na początku
    for n in nazwy:
        if t.casefold().startswith(n.casefold()) and (len(t) == len(n) or not t[len(n)].isalnum()):
            return True
    return False


def _wzorzec(nazwy):
    return re.compile(r"(?<!\w)(?:%s)(?!\w)" % "|".join(re.escape(n) for n in sorted(nazwy, key=len, reverse=True)),
                      re.IGNORECASE)


def pulpit_gry(ident):
    p = szczegol(ident)
    nazwy = nazwy_gry(p)
    rx = _wzorzec(nazwy) if nazwy else None
    raporty_gry = []
    try:
        from . import raporty
        for r in raporty.lista_raportow():
            if _zaczyna_sie(r.get("tytul"), nazwy):
                raporty_gry.append({k: r.get(k) for k in ("id", "tytul", "kto", "czas", "status", "rodzaj", "zrzuty")})
    except Exception as e:                                     # bez modułu raportów pulpit działa dalej
        rdzen.log("wytwórnia: raporty dla pulpitu gry: %r" % e)
    plan = sejf.plan()
    zadania, decyzje = [], []
    if rx:
        for s in (plan.get("zadania") or {}).get("sekcje") or []:
            for poz in s.get("pozycje") or []:
                if rx.search(poz.get("tekst_md") or ""):
                    zadania.append(dict(poz, sekcja=s.get("nazwa")))
        for d in plan.get("decyzje") or []:
            if rx.search((d.get("tytul") or "") + "\n" + (d.get("opis_md") or "")):
                decyzje.append({k: d.get(k) for k in ("id", "tytul", "tytul_md", "status", "emoji", "kategoria",
                                                       "zdecydowal", "czeka_na")})
    return {"pomysl": p, "nazwy": nazwy, "regula": REGULA_PULPITU, "raporty": raporty_gry[:40],
            "zadania": zadania[:60], "decyzje": decyzje[:60],
            "pliki": {"zadania": (plan.get("pliki") or {}).get("zadania"), "decyzje": (plan.get("pliki") or {}).get("decyzje")}}


# =========================================================================== zapis: frontmatter i sekcje
def _yaml_napis(s):
    """Wartość do płaskiego frontmattera: bez cudzysłowów, gdy bezpieczna, inaczej w "…" z ucieczkami."""
    s = str(s)
    if s and re.match(r"^[^\W\d_][\w .,()\-–—!?ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]*$", s) and not s.endswith(" ") \
            and _proste(s) not in ("true", "false", "yes", "no", "null"):
        return s
    return '"%s"' % s.replace("\\", "\\\\").replace('"', '\\"')


def _zakres_fm(dok):
    """(indeks linii „---” otwierającej, indeks zamykającej) albo None."""
    if len(dok) and dok.tresc(0).strip() == "---":
        for k in range(1, len(dok)):
            if dok.tresc(k).strip() in ("---", "..."):
                return 0, k
    return None


def ustaw_pole(dok, klucz, wartosc):
    """`klucz: wartość` we frontmatterze (cała linia podmieniona; brak klucza = nowa linia przed zamknięciem;
    brak frontmattera = nowy na górze). `wartosc` = gotowy tekst YAML (albo "" — puste pole)."""
    linia = ("%s: %s" % (klucz, wartosc)).rstrip()
    zakres = _zakres_fm(dok)
    if zakres is None:
        dok.wstaw(0, ["---", linia, "---"])
        return
    rx = re.compile(r"^%s\s*:" % re.escape(klucz))
    for i in range(zakres[0] + 1, zakres[1]):
        if rx.match(dok.tresc(i)):
            dok.zamien(i, linia)
            return
    dok.wstaw(zakres[1], [linia])


def _zastepcza(linia):
    s = linia.strip()
    return (not s or s in ("-", "…", "...", "- …", "- ...", "TODO", "todo") or s.startswith(">") or s.startswith("%%")
            or s.startswith("<!--") or bool(re.match(r"^([_*]).*\1$", s)) or bool(re.match(r"^\(.*\)$", s))
            or "{{" in s)


def _wpisz_do_sekcji(linie, nazwa, tekst):
    """W liniach notatki (lista napisów): tekst pod nagłówkiem `## <nazwa>`; treść zastępcza sekcji (puste linie,
    podpowiedzi „> …”, „_…_”, komentarze) jest zastępowana, prawdziwa treść zostaje pod nowym tekstem."""
    pn = _proste(nazwa)
    for i, l in enumerate(linie):
        m = sejf._RX_NAGLOWEK.match(l)
        if m and len(m.group(1)) == 2 and _proste(m.group(2)).startswith(pn):
            j = i + 1
            while j < len(linie):
                mm = sejf._RX_NAGLOWEK.match(linie[j])
                if mm and len(mm.group(1)) <= 2:
                    break
                j += 1
            cialo = linie[i + 1:j]
            if all(_zastepcza(x) for x in cialo):
                linie[i + 1:j] = [tekst, ""]
            else:
                linie[i + 1:i + 1] = [tekst, ""]
            return linie
    # brak sekcji: na końcu notatki
    while linie and not linie[-1].strip():
        linie.pop()
    return linie + ["", "## " + nazwa, tekst, ""]


def _szablon():
    _, baza = _baza()
    p = os.path.join(baza, *SZABLON)
    try:
        with open(p, "rb") as f:
            tekst = f.read().decode("utf-8-sig")
        return tekst.replace("\r\n", "\n").replace("\r", "\n"), True
    except (OSError, UnicodeDecodeError):
        return SZABLON_WBUDOWANY, False


def sprawdz_nazwe(nazwa):
    t = zapis.czysty_tekst(nazwa, LIMIT_NAZWY, "nazwa")
    if any(c in ZAKAZANE_W_NAZWIE for c in t):
        raise BladHTTP(400, "Nazwa pomysłu nie może zawierać znaków: \\ / : * ? \" < > | # ^ [ ] { }")
    if t.startswith(".") or t.endswith(".") or t.split(".")[0].strip().lower() in ZASTRZEZONE_NAZWY:
        raise BladHTTP(400, "Ta nazwa nie nadaje się na nazwę notatki — wybierz inną.")
    return t


def tresc_nowego(nazwa, zdanie, hak, dzis):
    """Notatka nowego pomysłu z szablonu: podstawione {{nazwa}}/{{title}}/{{date}}, frontmatter (`gra`, `etap: pomysł`,
    `zdanie`, `status: propozycja`, oceny i metryki puste) i treść sekcji „W jednym zdaniu” / „Hak ciekawości”."""
    tekst, _ = _szablon()
    for wzor, wartosc in (("{{title}}", nazwa), ("{{tytul}}", nazwa), ("{{nazwa}}", nazwa), ("{{gra}}", nazwa),
                          ("{{date:YYYY-MM-DD}}", dzis), ("{{date}}", dzis), ("{{data}}", dzis),
                          ("{{zdanie}}", zdanie)):
        tekst = tekst.replace(wzor, wartosc)
    dok = zapis.Dokument(tekst.encode("utf-8"))
    ustaw_pole(dok, "status", "propozycja")
    zakres = _zakres_fm(dok)
    fm_tekst = "\n".join(dok.tresc(i) for i in range(zakres[0] + 1, zakres[1])) if zakres else ""
    if not re.search(r"^typ\s*:", fm_tekst, re.MULTILINE):
        ustaw_pole(dok, "typ", "pomysł-gry")
    ustaw_pole(dok, "gra", _yaml_napis(nazwa))
    ustaw_pole(dok, "etap", "pomysł")
    ustaw_pole(dok, "zdanie", _yaml_napis(zdanie))
    for pole in ("ocena_agenta", "werdykt_agenta", "ocena_karol", "ocena_pawel") + METRYKI + ("miejsce",):
        if re.search(r"^%s\s*:" % pole, fm_tekst, re.MULTILINE):
            ustaw_pole(dok, pole, "")                          # przykład z szablonu nie jest oceną nowego pomysłu
    linie = dok.bajty().decode("utf-8").split("\n")
    linie = _wpisz_do_sekcji(linie, "W jednym zdaniu", zdanie)
    if hak:
        linie = _wpisz_do_sekcji(linie, "Hak ciekawości", hak)
    wynik = "\n".join(linie)
    if not wynik.endswith("\n"):
        wynik += "\n"
    return wynik.encode("utf-8")


def dodaj_pomysl(nazwa, zdanie, hak, kto, znacznik=None):
    nazwa = sprawdz_nazwe(nazwa)
    zdanie = zapis.czysty_tekst(zdanie, LIMIT_ZDANIA, "zdanie")
    hak = zapis.czysty_tekst(hak, LIMIT_HAKA, "hak", wymagany=False)
    sid, baza = _baza()
    folder = os.path.join(baza, FOLDER, PODFOLDER)
    sciezka = os.path.join(folder, nazwa + ".md")
    try:
        istniejace = os.listdir(folder)
    except OSError:
        istniejace = []
    if any(sejf._nfc(x).casefold() == sejf._nfc(nazwa + ".md").casefold() for x in istniejace):
        raise BladHTTP(409, "Pomysł „%s” już jest w Wytwórni — otwórz go albo wybierz inną nazwę." % nazwa,
                       kod="juz_istnieje")
    bajty = tresc_nowego(nazwa, zdanie, hak, zapis.dzis())
    wynik = zapis.utworz_plik(sciezka, _pokaz(sid, baza, sciezka), nazwa, bajty, "nowy pomysł w Wytwórni: %s" % nazwa,
                              kto, znacznik)
    wynik["id"] = nazwa
    wynik["pomysl"] = szczegol(nazwa)
    return wynik


def _osoba_oceny(kto):
    para = OSOBY_OCEN.get(sejf.kanoniczne(kto))
    if not para:
        raise BladHTTP(403, "Kartę oceny wypełnia Karol albo Paweł — wpisz swoje imię w Ustawieniach panelu.",
                       kod="spoza_zespolu")
    return para


def _wiersz_z_komorka(linia, k, wartosc, ile):
    """Wiersz tabeli z podmienioną komórką `k` (reszta komórek bez zmian; brakujące dopisane jako puste)."""
    m = re.match(r"^(\s*)(.*?)(\s*)$", linia)
    wciecie, srodek, koniec = m.group(1), m.group(2), m.group(3)
    c = komorki(srodek)
    while len(c) < ile:
        c.append("  ")
    c[k] = "  " if wartosc is None else " %s " % wartosc
    return wciecie + "|" + "|".join(c) + "|" + koniec


def _zapisz_karte(dok, kolumna_klucz, kolumna_nazwa, oceny):
    """Kolumna osoby w tabeli sekcji „Karta oceny” (sekcja i tabela dochodzą, gdy ich nie ma)."""
    naglowki = [(i, p, t) for i, p, t in dok.naglowki() if p == 2]
    sekcja = next(((i, dok.koniec_sekcji(i, 2)) for i, p, t in naglowki if _proste(t).startswith("karta oceny")), None)
    nowa_tabela = ["| Kryterium | Agent | Karol | Paweł |", "|---|---|---|---|"] + \
                  ["| %s |  |  |  |" % k for k in KRYTERIA]
    if sekcja is None:
        przed = next((i for i, p, t in naglowki if _proste(t).startswith("krytyka agenta")), len(dok))
        dok.wstaw(przed, ["## Karta oceny"] + nowa_tabela + [""])
        sekcja = (przed, przed + len(nowa_tabela) + 2)
    start, koniec = sekcja
    linie = [dok.tresc(j) for j in range(start + 1, koniec)]
    tabele = [t for t in _tabele(linie) if len(_kolumny(t[2])) >= 1]
    if not tabele:
        dok.wstaw(start + 1, nowa_tabela + [""])
        linie = [dok.tresc(j) for j in range(start + 1, start + 1 + len(nowa_tabela) + 1)]
        tabele = [t for t in _tabele(linie) if len(_kolumny(t[2])) >= 1]
    t0, dane, naglowek = tabele[0]
    kol = _kolumny(naglowek)
    if kolumna_klucz not in kol:
        raise BladHTTP(409, "Tabela w sekcji „Karta oceny” nie ma kolumny „%s” — dopisz ją w Obsidianie (nagłówek "
                            "| Kryterium | Agent | Karol | Paweł |), potem oceń jeszcze raz." % kolumna_nazwa,
                       kod="brak_kolumny")
    k = kol[kolumna_klucz]
    ile = len(naglowek)
    wiersze = {}                                               # indeks kryterium -> indeks linii w dokumencie
    bez_nazwy = [j for j in dane if _indeks_kryterium((komorki(linie[j]) or [""])[0]) is None]
    for j in dane:
        i = _indeks_kryterium((komorki(linie[j]) or [""])[0])
        if i is not None and i not in wiersze:
            wiersze[i] = start + 1 + j
    for i in range(len(KRYTERIA)):                             # wiersze bez nazwy: po kolei dla brakujących
        if i not in wiersze and bez_nazwy:
            wiersze[i] = start + 1 + bez_nazwy.pop(0)
    brakujace = []
    for i, wartosc in enumerate(oceny):
        if i in wiersze:
            j = wiersze[i]
            dok.zamien(j, _wiersz_z_komorka(dok.tresc(j), k, wartosc, ile))
        else:
            c = ["  "] * ile
            c[0] = " %s " % KRYTERIA[i]
            if wartosc is not None:
                c[k] = " %s " % wartosc
            brakujace.append("|" + "|".join(c) + "|")
    if brakujace:
        ostatni = start + 1 + (dane[-1] if dane else t0 + 1)
        dok.wstaw(ostatni + 1, brakujace)


def ocen(ident, oceny, wersja, kto, znacznik=None):
    """Karta oceny osoby: 10 wartości 0–3 (albo None = puste) → kolumna Karol/Paweł i suma w `ocena_karol`/`ocena_pawel`."""
    if not isinstance(oceny, list) or len(oceny) != len(KRYTERIA):
        raise BladHTTP(400, "Pole „oceny” to lista %d wartości 0–%d (albo null)." % (len(KRYTERIA), MAKS_KRYTERIUM))
    czyste = []
    for v in oceny:
        if v is None or v == "":
            czyste.append(None)
        elif isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= MAKS_KRYTERIUM:
            czyste.append(v)
        else:
            raise BladHTTP(400, "Każda ocena to liczba całkowita 0–%d albo null." % MAKS_KRYTERIUM)
    nazwa_kolumny, pole = _osoba_oceny(kto)
    klucz_kolumny = sejf.kanoniczne(nazwa_kolumny)
    n = _znajdz(ident)
    sid, baza = _baza()
    s = sum(v for v in czyste if v is not None) if any(v is not None for v in czyste) else None
    nazwa = karta_pomyslu(n)["nazwa"]

    def zmiana(dok):
        _zapisz_karte(dok, klucz_kolumny, nazwa_kolumny, czyste)
        ustaw_pole(dok, pole, "" if s is None else str(s))
        ile = sum(1 for v in czyste if v is not None)
        return "ocena pomysłu %s (%s): %s/%d%s" % (nazwa, nazwa_kolumny, "—" if s is None else s, MAKS_SUMY,
                                                   "" if ile == len(KRYTERIA) else ", %d z %d kryteriów" % (ile, len(KRYTERIA)))

    wynik = zapis.wykonaj_plik(n["abs"], _pokaz(sid, baza, n["abs"]), n["tytul"], wersja, zmiana, kto, znacznik)
    wynik["pomysl"] = szczegol(n["tytul"])
    return wynik


def zmien_etap(ident, nowy, wersja, kto, znacznik=None):
    if not isinstance(nowy, str) or etap(nowy) != nowy and _proste(nowy) != _proste(etap(nowy)):
        raise BladHTTP(400, "Etap to jedno z: %s." % ", ".join(ETAPY))
    nowy = etap(nowy)
    n = _znajdz(ident)
    sid, baza = _baza()
    p = karta_pomyslu(n)
    if p["etap"] == nowy and p["etap_surowy"]:
        raise BladHTTP(409, "Pomysł „%s” już jest na etapie „%s”." % (p["nazwa"], nowy), kod="ten_sam_etap")

    def zmiana(dok):
        ustaw_pole(dok, "etap", nowy)
        return "etap pomysłu %s: %s → %s" % (p["nazwa"], p["etap_surowy"] or "—", nowy)

    wynik = zapis.wykonaj_plik(n["abs"], _pokaz(sid, baza, n["abs"]), n["tytul"], wersja, zmiana, kto, znacznik)
    wynik["pomysl"] = szczegol(n["tytul"])
    return wynik


# =========================================================================== trasy
BRAK_PRAWA = ("Ocenę i etap pomysłu zmienia Karol albo Paweł: przy komputerze z panelem albo w przeglądarce z kluczem "
              "zatwierdzania. Pomysł i komentarz może dodać każdy.")


def _decydent(z):
    if not zapis.decydent(z):
        if not zapis.dostepny():
            raise BladHTTP(403, "Zapis do sejfu z panelu jest wyłączony (ustawienie „zapis_sejfu” w konfiguracji).")
        raise BladHTTP(403, BRAK_PRAWA, kod="brak_klucza_zatwierdzania")


def _t_lista(z):
    return lista()


def _t_pomysl(z):
    return szczegol(z.params["id"])


def _t_gra(z):
    return pulpit_gry(z.params["id"])


def _t_radar(z):
    return radar()


def _t_dodaj(z):
    d = zapis._dane(z, ("nazwa", "zdanie", "hak"))
    kto, znacznik = zapis.podpis(z)
    return 201, dodaj_pomysl(d.get("nazwa"), d.get("zdanie"), d.get("hak"), kto, znacznik)


def _t_ocena(z):
    _decydent(z)
    d = zapis._dane(z, ("oceny", "wersja"))
    if not getattr(z, "kto_z_naglowka", False):
        raise BladHTTP(400, "Wpisz swoje imię w Ustawieniach — ocena trafia do kolumny osoby.", kod="brak_imienia")
    kto, znacznik = zapis.podpis(z)
    return ocen(z.params["id"], d.get("oceny"), d.get("wersja"), kto, znacznik)


def _t_etap(z):
    _decydent(z)
    d = zapis._dane(z, ("etap", "wersja"))
    if not getattr(z, "kto_z_naglowka", False):
        raise BladHTTP(400, zapis.KOMUNIKAT_BRAK_IMIENIA.replace("decyzja", "zmiana etapu"), kod="brak_imienia")
    kto, znacznik = zapis.podpis(z)
    return zmien_etap(z.params["id"], d.get("etap"), d.get("wersja"), kto, znacznik)


def zarejestruj(app):
    app.dodaj("GET", "/api/wytwornia", _t_lista)
    app.dodaj("GET", "/api/wytwornia/radar", _t_radar)
    app.dodaj("POST", "/api/wytwornia/pomysly", _t_dodaj)
    app.dodaj("GET", "/api/wytwornia/pomysly/<id>", _t_pomysl)
    app.dodaj("POST", "/api/wytwornia/pomysly/<id>/ocena", _t_ocena)
    app.dodaj("POST", "/api/wytwornia/pomysly/<id>/etap", _t_etap)
    app.dodaj("GET", "/api/wytwornia/gry/<id>", _t_gra)


def zdrowie():
    try:
        sid, baza = _baza()
    except BladHTTP:
        return {"ok": False, "sejf": False}
    return {"ok": True, "folder": os.path.isdir(os.path.join(baza, FOLDER)), "pomysly": len(_notatki_pomyslow()),
            "szablon": os.path.isfile(os.path.join(baza, *SZABLON))}
