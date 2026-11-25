# -*- coding: utf-8 -*-
"""Gry studia: rejestr gier i jeden klasyfikator spraw (25.11.2026, Karol: „Chcę, żeby dashboard był per gra robiony”).

Rejestr — klucz „gry” w panel/konfiguracja.json (stary klucz „gra” zostaje: to identyfikatory Roblox głównej gry):

    "gry": {"domyslna": "bc", "aktywna": "bc",
            "lista": [{"id": "bc", "nazwa": "Blocky & Crycket", "stan": "aktywna", "slowa": ["blocky"]},
                      {"id": "smok", "nazwa": "Gra o smoku", "stan": "wstrzymana", "slowa": ["o smok", "monster evolution"]},
                      {"id": "wspolne", "nazwa": "Wspólne", "wspolne": true, "slowa": ["sesj glown", "panel"]}]}

  - `domyslna` — gra spraw bez znacznika i bez słowa kluczowego; `aktywna` — pulpit, który panel pokazuje na start
    (osoba może wybrać inny — zapamiętuje go jej przeglądarka);
  - `stan` — „aktywna” albo „wstrzymana” (przełącznik pokazuje wstrzymane przygaszone, z liczbą spraw, które tam czekają);
  - `wspolne: true` — sprawy wspólne (proces zespołu, panel, sesje główne): widać je pod każdą grą;
  - `slowa` — początki wyrazów w TYTULE, bez wielkości liter i polskich znaków: „smok” łapie „smoka” i „Smoku”,
    „pet aren” — „Pet Arenę”. Słowo z kilku wyrazów pasuje do kolejnych wyrazów tytułu; wyraz z jednej albo dwóch liter
    („o”, „b”) musi pasować w całości, więc „o smok” łapie „gra o smoku”, ale nie „obok smoka”. „^” na początku słowa =
    tylko na początku tytułu („^panel” łapie „Panel: lustro…”, ale nie „…zaakceptowany w panelu”).
Bez klucza (albo z pustą listą) panel działa jak dawniej: jedna gra, bez przełącznika, sprawy bez pola `gra`.

Klasyfikator — jeden dla pytań, decyzji, zadań i raportów (zakładki, Pulpit, lustro, narzędzia):
  1. jawny znacznik zawsze wygrywa:
       pytanie   — wiersz „Gra: <id>” w treści (przed „**Odpowiedź:**”; dopuszczalne „- **Gra:** smok”);
       decyzja   — wiersz „Gra: <id>” w opisie, POD wierszem statusu (wiersz statusu zostaje pierwszy — starszy panel
                   czyta go bez zmian);
       zadanie   — znacznik Obsidiana „#gra/<id>” w linii, przed „· agent:” i priorytetem
                   (`- [ ] tekst · #gra/smok · agent: Paweł · #wysoki`);
       raport    — pole „gra” w pliku JSON raportu (`narzedzia/raport.py dodaj --gra smok`);
     wartością znacznika jest identyfikator albo nazwa gry z rejestru; nieznana wartość się nie liczy;
  2. inaczej słowa kluczowe w samym tytule — wygrywa pierwsza gra w kolejności rejestru;
  3. inaczej `domyslna`.
Znaczniki nie psują starszego kodu panelu: wiersz „Gra:” jest dla niego zwykłym tekstem opisu, „#gra/x” częścią tekstu
zadania (priorytet i „· agent:” zostają na końcu linii), a pole „gra” w pliku raportu odczyt zostawia bez zmian.
Starych plików w panel/dane/ nikt nie przepisuje: raport bez pola dostaje grę przy odczycie.
"""
import json
import re
import threading
import unicodedata

from . import rdzen
from .rdzen import BladHTTP

STANY = ("aktywna", "wstrzymana")
RX_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,31}$")
MAX_GIER = 40
MAX_SLOW = 80
MAX_NAZWA = 60

# Pytanie i decyzja: wiersz „Gra: smok” (pogrubienie i punkt listy dopuszczalne, jak przy „Rozstrzyga:”).
RX_WIERSZ_GRY = re.compile(r"^\s*(?:[-*+]\s+)?(?:\*\*|__)?\s*Gra\s*(?:\*\*|__)?\s*:\s*(?:\*\*|__)?\s*(.*?)\s*(?:\*\*|__)?\s*$",
                           re.IGNORECASE)
# Zadanie: znacznik Obsidiana „#gra/smok” (w Obsidianie to zagnieżdżony tag — da się po nim szukać).
RX_ZNACZNIK_ZADANIA = re.compile(r"(?:^|(?<=\s))#gra/([A-Za-z0-9][A-Za-z0-9_-]{0,31})(?=$|[\s·,.;)])", re.IGNORECASE)
_RX_ZNACZNIK_Z_ODSTEPEM = re.compile(r"\s*(?:·\s*)?(?:^|(?<=\s))#gra/[A-Za-z0-9][A-Za-z0-9_-]{0,31}(?=$|[\s·,.;)])",
                                     re.IGNORECASE)
_RX_PLOT = re.compile(r"^ {0,3}(`{3,}|~{3,})")

_blokada = threading.Lock()
_pamiec = {"klucz": None, "rejestr": None}


# --------------------------------------------------------------------------- normalizacja
def wyrazy(tekst):
    """Wyrazy do porównań: małe litery, bez polskich znaków, tylko litery i cyfry („Pet-Arenę!” → ["pet", "arene"])."""
    t = unicodedata.normalize("NFD", str(tekst or "").casefold().replace("ł", "l"))
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.findall(r"[0-9a-z]+", t)


def _pasuje_slowo(slowo, tytul_wyrazy, od_poczatku=False):
    """Czy słowo kluczowe (lista wyrazów) pasuje do kolejnych wyrazów tytułu (każdy wyraz jako początek wyrazu);
    `od_poczatku` — tylko pierwsze wyrazy tytułu."""
    n = len(slowo)
    if not n:
        return False
    for i in range(min(1, len(tytul_wyrazy) - n + 1) if od_poczatku else len(tytul_wyrazy) - n + 1):
        if all((tytul_wyrazy[i + j] == w) if len(w) <= 2 else tytul_wyrazy[i + j].startswith(w)
               for j, w in enumerate(slowo)):
            return True
    return False


# --------------------------------------------------------------------------- rejestr
def _zbuduj(surowy):
    """Rejestr z surowego klucza „gry” albo None (brak, zły format, pusta lista)."""
    if not isinstance(surowy, dict) or not isinstance(surowy.get("lista"), list):
        return None
    lista, widziane = [], set()
    for g in surowy["lista"][:MAX_GIER]:
        if not isinstance(g, dict):
            continue
        gid = str(g.get("id") or "").strip().lower()
        if not RX_ID.match(gid) or gid in widziane:
            rdzen.log("gry: pomijam grę o złym albo powtórzonym identyfikatorze: %r" % g.get("id"))
            continue
        widziane.add(gid)
        nazwa = re.sub(r"[\x00-\x1f\x7f]", "", str(g.get("nazwa") or gid)).strip()[:MAX_NAZWA] or gid
        stan = g.get("stan") if g.get("stan") in STANY else "aktywna"
        wspolne = bool(g.get("wspolne")) if "wspolne" in g else gid == "wspolne"
        slowa = []
        for s in (g.get("slowa") or [])[:MAX_SLOW] if isinstance(g.get("slowa"), list) else []:
            w = wyrazy(s) if isinstance(s, str) else []
            kotwica = isinstance(s, str) and s.strip().startswith("^")
            if w and (w, kotwica) not in [(x[1], x[2]) for x in slowa]:
                slowa.append((s.strip(), w, kotwica))
        lista.append({"id": gid, "nazwa": nazwa, "stan": stan, "wspolne": wspolne, "slowa": slowa,
                      "_nazwa_w": wyrazy(nazwa), "_id_w": wyrazy(gid)})
    gry = [g for g in lista if not g["wspolne"]]
    if not gry:
        return None                                            # sama gra „wspólne” to nie rejestr gier
    ids = {g["id"] for g in gry}
    domyslna = str(surowy.get("domyslna") or "").strip().lower()
    if domyslna not in ids:
        domyslna = gry[0]["id"]
    aktywna = str(surowy.get("aktywna") or "").strip().lower()
    if aktywna not in ids:
        aktywna = domyslna
    return {"lista": lista, "domyslna": domyslna, "aktywna": aktywna,
            "podpis": json.dumps(surowy, sort_keys=True, ensure_ascii=False)}


def rejestr():
    """Rejestr gier z konfiguracji (z pamięcią do zmiany konfiguracji) albo None, gdy go nie ma."""
    surowy = rdzen.konfiguracja().get("gry")
    try:
        klucz = json.dumps(surowy, sort_keys=True, ensure_ascii=False)
    except (TypeError, ValueError):
        return None
    with _blokada:
        if _pamiec["klucz"] != klucz:
            _pamiec.update(klucz=klucz, rejestr=_zbuduj(surowy))
        return _pamiec["rejestr"]


def podpis():
    """Znacznik rejestru do kluczy pamięci podręcznej (plan, lista raportów): zmiana rejestru = nowa klasyfikacja."""
    r = rejestr()
    return r["podpis"] if r else ""


def publiczny(rej=None):
    """Rejestr dla interfejsu: {lista:[{id, nazwa, stan, wspolne}], domyslna, aktywna} albo None (bez rejestru)."""
    r = rej if rej is not None else rejestr()
    if not r:
        return None
    return {"lista": [{"id": g["id"], "nazwa": g["nazwa"], "stan": g["stan"], "wspolne": g["wspolne"]} for g in r["lista"]],
            "domyslna": r["domyslna"], "aktywna": r["aktywna"]}


def gra(gid, rej=None):
    """Gra z rejestru po identyfikatorze albo None."""
    r = rej if rej is not None else rejestr()
    if not r:
        return None
    return next((g for g in r["lista"] if g["id"] == gid), None)


def rozpoznaj(wartosc, rej=None):
    """Identyfikator gry z wartości znacznika („smok”, „Gra o smoku”, „[[Gra o smoku]]”, „pet-arena (stara)”) albo None."""
    r = rej if rej is not None else rejestr()
    if not r or not isinstance(wartosc, str):
        return None
    w = wyrazy(wartosc)
    if not w:
        return None
    for g in r["lista"]:
        if w == g["_id_w"] or w == g["_nazwa_w"]:
            return g["id"]
    for k in range(len(w) - 1, 0, -1):                         # „smok — gra o smoku”, „pet-arena (stara)”
        for g in r["lista"]:
            if w[:k] == g["_id_w"]:
                return g["id"]
    return None


# --------------------------------------------------------------------------- znaczniki
def znacznik_tresci(tresc_md):
    """Wartość pierwszego wiersza „Gra: …” w treści (poza blokami kodu) albo None."""
    plot = None
    for linia in str(tresc_md or "").split("\n"):
        m = _RX_PLOT.match(linia)
        if plot:
            if m and m.group(1)[0] == plot[0] and len(m.group(1)) >= len(plot) and not linia.strip()[len(m.group(1)):].strip():
                plot = None
            continue
        if m:
            plot = m.group(1)
            continue
        mg = RX_WIERSZ_GRY.match(linia)
        if mg and mg.group(1).strip():
            return mg.group(1).strip()
    return None


def jest_wierszem_gry(linia):
    """Czy linia to wiersz znacznika „Gra: …” (interfejs go nie pokazuje jako tekstu)."""
    m = RX_WIERSZ_GRY.match(linia or "")
    return bool(m and m.group(1).strip())


def znacznik_zadania(tekst):
    """Wartość znacznika „#gra/<id>” w linii zadania albo None."""
    m = RX_ZNACZNIK_ZADANIA.search(str(tekst or ""))
    return m.group(1) if m else None


def bez_znacznika_zadania(tekst):
    """Tekst zadania bez znacznika „#gra/<id>” (razem z kropką rozdzielającą przed nim)."""
    t = str(tekst or "")
    if "#" not in t:
        return t
    return re.sub(r"\s{2,}", " ", _RX_ZNACZNIK_Z_ODSTEPEM.sub("", t)).strip()


# --------------------------------------------------------------------------- klasyfikator
def klasyfikuj(tytul, znacznik=None, rej=None):
    """(id gry, skąd, szczegół): skąd = „znacznik” | „slowo” | „domyslna”; szczegół = wartość znacznika albo słowo
    kluczowe (przy „domyslna” — nieznany znacznik albo None). Bez rejestru: (None, None, None)."""
    r = rej if rej is not None else rejestr()
    if not r:
        return None, None, None
    nieznany = None
    if znacznik is not None and str(znacznik).strip():
        gid = rozpoznaj(str(znacznik), r)
        if gid:
            return gid, "znacznik", str(znacznik).strip()
        nieznany = str(znacznik).strip()
    w = wyrazy(tytul)
    for g in r["lista"]:
        for surowe, slowo, kotwica in g["slowa"]:
            if _pasuje_slowo(slowo, w, kotwica):
                return g["id"], "slowo", surowe
    return r["domyslna"], "domyslna", ("nieznany znacznik „%s”" % nieznany if nieznany else None)


def gra_zadania(tekst_pola, rej=None):
    """Gra pozycji zadań z surowego tekstu pola (znacznik albo słowa w tekście bez znacznika)."""
    t = str(tekst_pola or "")
    return klasyfikuj(bez_znacznika_zadania(t), znacznik_zadania(t), rej)[0]


def gra_raportu(r, rej=None):
    """(id, skąd, szczegół) dla raportu (słownika z pliku): pole „gra”, potem tytuł."""
    znacznik = r.get("gra") if isinstance(r, dict) and isinstance(r.get("gra"), str) else None
    return klasyfikuj((r or {}).get("tytul") if isinstance(r, dict) else "", znacznik, rej)


def _oznacz(obiekt, wynik):
    gid, skad, _ = wynik
    obiekt["gra"] = gid
    obiekt["gra_skad"] = skad


def oznacz_plan(plan, rej=None):
    """Dopisuje `gra` i `gra_skad` do pytań, decyzji i pozycji zadań planu (w miejscu). Bez rejestru niczego nie
    dopisuje — tylko zdejmuje roboczy znacznik zadań z parsera."""
    r = rej if rej is not None else rejestr()
    zadania = (plan.get("zadania") or {}).get("sekcje") or []
    for s in zadania:
        for p in s.get("pozycje") or []:
            znacznik = p.pop("gra_znacznik", None)
            if r:
                _oznacz(p, klasyfikuj(p.get("tekst_md") or "", znacznik, r))
    if not r:
        return plan
    for p in plan.get("pytania") or []:
        _oznacz(p, klasyfikuj(p.get("tytul") or "", znacznik_tresci(p.get("tresc_md")), r))
    for d in plan.get("decyzje") or []:
        _oznacz(d, klasyfikuj(d.get("tytul") or "", znacznik_tresci(d.get("opis_md")), r))
    return plan


def oznacz_raport(out, rej=None):
    """Dopisuje `gra` i `gra_skad` do raportu (słownika do API). Bez rejestru raport zostaje bez zmian."""
    r = rej if rej is not None else rejestr()
    if r:
        _oznacz(out, gra_raportu(out, r))
    return out


# --------------------------------------------------------------------------- zapis (nowe sprawy z panelu i narzędzi)
def sprawdz_gre(wartosc, pole="gra"):
    """Identyfikator gry z rejestru dla wartości od człowieka albo narzędzia (400, gdy nieznany albo bez rejestru);
    None dla pustej wartości."""
    if wartosc is None or (isinstance(wartosc, str) and not wartosc.strip()):
        return None
    if not isinstance(wartosc, str):
        raise BladHTTP(400, "Pole „%s” musi być identyfikatorem gry" % pole)
    r = rejestr()
    if not r:
        raise BladHTTP(400, "Panel nie ma rejestru gier (klucz „gry” w panel/konfiguracja.json) — pole „%s” nie działa."
                       % pole, kod="brak_rejestru_gier")
    gid = wartosc.strip().lower()
    if not gra(gid, r):
        raise BladHTTP(400, "Nieznana gra „%s”. Gry w rejestrze: %s" % (wartosc.strip()[:40],
                                                                       ", ".join(g["id"] for g in r["lista"])),
                       kod="nieznana_gra")
    return gid


def znacznik_nowego_zadania(tekst, gid, rej=None):
    """Znacznik „ · #gra/<id>” dla nowego zadania w grze `gid` albo "" — gdy sam tekst i tak trafi do tej gry
    (gra domyślna bez słów innej gry albo słowo kluczowe tej gry), znacznik jest zbędny."""
    r = rej if rej is not None else rejestr()
    if not r or not gid:
        return ""
    return "" if klasyfikuj(tekst, None, r)[0] == gid else " · #gra/%s" % gid
