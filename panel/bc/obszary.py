# -*- coding: utf-8 -*-
"""Obszary pracy: czego dotyczy praca w toku i czy dwie prace się nakładają (czysta logika, bez plików i gita).

Obszar to jeden z wpisów (najwyżej MAKS_OBSZAROW na pracę, każdy do MAKS_DLUGOSC znaków):
    ścieżka albo wzorzec względem repozytorium, z ukośnikami „/”, np. „swiat/las/czesci.json”, „panel/bc”,
    „swiat/*/czesci.json”, „src/**” — bez ścieżek bezwzględnych, liter dysku, „..”, „@” i znaków sterujących,
    a pierwszy człon to konkretny katalog albo plik (nie „*”, „**”, „*.py” — taki obszar nakładałby się ze wszystkim)
    (ukośnik wsteczny „\\” jest zamieniany na „/”, „./” na początku i „/” na końcu są pomijane);
    model:<id>         moduł postaci: swiat/postacie/<id>.py i swiat/postacie/wynik/<id>/**  (id małymi literami)
    mapa:<scena>       mapa z klocków: swiat/<scena>/**                                     (scena małymi literami)
    studio:<Kontener>  kontener w Workspace wspólnego miejsca w Team Create; porównywany tylko z tym samym
                       znacznikiem, bez względu na wielkość liter.

Dwa obszary nakładają się, gdy to ten sam znacznik albo ich ścieżki się przecinają: są równe, jedna jest katalogiem
nadrzędnym drugiej, albo wzorzec pasuje do ścieżki drugiego obszaru lub do jej katalogu nadrzędnego. Porównanie jest
ostrożne: bez rozróżniania wielkości liter (Windows), a dwa wzorce w tym samym miejscu ścieżki albo „**” liczą się
jako nakładanie. Lepiej raz za dużo ostrzec niż pozwolić dwóm osobom nadpisać sobie pliki binarne.

Funkcje:
    normalizuj(wpis) -> postać kanoniczna         (zły wpis = rdzen.BladHTTP 400 z komunikatem po polsku)
    lista(wpisy) -> [postacie kanoniczne]         (bez powtórzeń; za dużo wpisów = BladHTTP 400)
    sciezki(obszar) -> [wzorce ścieżek]           (studio: pusta lista)
    nakladaja_sie(a, b) -> bool
    wspolne(lista_a, lista_b) -> [opis]           opisy par, które się nakładają („model:rycerz” albo „a ~ b”)
    pokrywa(a, b) -> bool                         czy obszar a obejmuje CAŁY obszar b
    pokrywaja(lista_a, lista_b) -> bool           czy każdy obszar z b jest objęty którymś z a
    dotyczy_pliku(lista, plik) -> [obszar]        obszary, w które wpada plik (ścieżka z gita)
"""
import fnmatch
import re

from .rdzen import BladHTTP

MAKS_OBSZAROW = 12
MAKS_DLUGOSC = 120
ZNACZNIKI = ("model", "mapa", "studio")

RX_ID_MODELU = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
RX_KONTENER = re.compile(r"^[^\x00-\x1f\x7f/\\:*?\[\]\"<>|@]{1,100}$")
# znaki sterujące (także C1), znaki kierunku tekstu i zerowej szerokości — jak gitsync._RX_STERUJACE
RX_STERUJACE = re.compile("[\x00-\x1f\x7f-\x9f​-‏‪-‮⁠-⁩﻿]")
ZNAKI_WZORCA = set("*?[")


def _blad(wpis, powod):
    return BladHTTP(400, "Niepoprawny obszar „%s” — %s (przykłady: model:rycerz, mapa:las_potwory, "
                         "studio:DemoLesnaBaza, swiat/las/czesci.json)" % (str(wpis)[:80], powod))


def _sciezka(wpis):
    s = wpis.replace("\\", "/")
    if s.startswith("/") or s.startswith("~"):
        raise _blad(wpis, "ścieżka musi być względna wobec repozytorium (bez „/” i „~” na początku)")
    if ":" in s:
        raise _blad(wpis, "bez liter dysku i dwukropków (znaczniki to tylko model:, mapa: i studio:)")
    czesci = [c for c in s.split("/") if c not in ("", ".")]
    if not czesci:
        raise _blad(wpis, "pusta ścieżka")
    if any(c == ".." for c in czesci):
        raise _blad(wpis, "bez „..”")
    if any(c.strip() != c or not c for c in czesci):
        raise _blad(wpis, "bez spacji na początku i końcu części ścieżki")
    if "@" in s:
        raise _blad(wpis, "bez „@” (obszar idzie na publiczny GitHub — żadnych adresów e-mail)")
    if _wzorzec(czesci[0]) or czesci[0] == "**":
        raise _blad(wpis, "za szeroki — zacznij od konkretnego katalogu albo pliku (np. swiat/las/**), nie od wzorca")
    return "/".join(czesci)


def normalizuj(wpis):
    """Wpis obszaru → postać kanoniczna („model:rycerz”, „studio:DemoLesnaBaza”, „swiat/las/czesci.json”)."""
    if not isinstance(wpis, str):
        raise BladHTTP(400, "Obszar musi być tekstem")
    w = wpis.strip()
    if not w:
        raise _blad(wpis, "pusty wpis")
    if len(w) > MAKS_DLUGOSC:
        raise _blad(wpis, "za długi (najwyżej %d znaków)" % MAKS_DLUGOSC)
    if RX_STERUJACE.search(w):
        raise _blad(wpis, "znaki sterujące")
    m = re.match(r"^([A-Za-z]+):(.*)$", w)
    if m and m.group(1).lower() in ZNACZNIKI:
        rodzaj, wartosc = m.group(1).lower(), m.group(2).strip()
        if rodzaj == "studio":
            if not RX_KONTENER.match(wartosc) or wartosc.strip() != wartosc:
                raise _blad(wpis, "nazwa kontenera w Workspace (bez ukośników i znaków specjalnych)")
            return "studio:" + wartosc
        wartosc = wartosc.lower()
        if not RX_ID_MODELU.match(wartosc):
            raise _blad(wpis, "po „%s:” nazwa z małych liter, cyfr, „_” i „-”" % rodzaj)
        return rodzaj + ":" + wartosc
    if m and len(m.group(1)) > 1:
        raise _blad(wpis, "nieznany rodzaj obszaru „%s:”" % m.group(1)[:20])
    return _sciezka(w)


def lista(wpisy):
    """Lista wpisów → lista postaci kanonicznych bez powtórzeń (kolejność zachowana). None = pusta lista."""
    if wpisy is None:
        return []
    if isinstance(wpisy, str):
        wpisy = [wpisy]
    if not isinstance(wpisy, (list, tuple)):
        raise BladHTTP(400, "Obszary muszą być listą")
    wynik = []
    for w in wpisy:
        n = normalizuj(w)
        if n not in wynik:
            wynik.append(n)
    if len(wynik) > MAKS_OBSZAROW:
        raise BladHTTP(400, "Za dużo obszarów (%d, najwyżej %d)" % (len(wynik), MAKS_OBSZAROW))
    return wynik


def lista_bez_bledow(wpisy):
    """Jak `lista`, ale dla danych z pliku albo od innych: złe wpisy są pomijane, nadmiar ucinany. Nigdy nie rzuca."""
    if not isinstance(wpisy, list):
        return []
    wynik = []
    for w in wpisy[:MAKS_OBSZAROW * 4]:
        try:
            n = normalizuj(w)
        except BladHTTP:
            continue
        if n not in wynik:
            wynik.append(n)
        if len(wynik) >= MAKS_OBSZAROW:
            break
    return wynik


def _rodzaj(obszar):
    for z in ZNACZNIKI:
        if obszar.startswith(z + ":"):
            return z, obszar[len(z) + 1:]
    return None, obszar


def sciezki(obszar):
    """Wzorce ścieżek obszaru (postać kanoniczna). studio:… = brak ścieżek (porównanie tylko po znaczniku)."""
    rodzaj, wartosc = _rodzaj(obszar)
    if rodzaj == "model":
        return ["swiat/postacie/%s.py" % wartosc, "swiat/postacie/wynik/%s/**" % wartosc]
    if rodzaj == "mapa":
        return ["swiat/%s/**" % wartosc]
    if rodzaj == "studio":
        return []
    return [obszar]


def _segmenty(wzorzec):
    return [s.casefold() for s in wzorzec.split("/") if s]


def _wzorzec(seg):
    return any(z in seg for z in ZNAKI_WZORCA)


def _segmenty_pasuja(a, b):
    """Dwa segmenty ścieżki: równe; dosłowny pasuje do wzorca; dwa wzorce — ostrożnie: tak."""
    wa, wb = _wzorzec(a), _wzorzec(b)
    if not wa and not wb:
        return a == b
    if wa and wb:
        return True
    return fnmatch.fnmatchcase(b, a) if wa else fnmatch.fnmatchcase(a, b)


def _sciezki_przecinaja(a, b):
    """Wzorce a i b (ścieżki) się przecinają. Gdy jeden kończy się wcześniej, to jego katalog obejmuje drugi."""
    sa, sb = _segmenty(a), _segmenty(b)
    for x, y in zip(sa, sb):
        if x == "**" or y == "**":
            return True
        if not _segmenty_pasuja(x, y):
            return False
    return True


def nakladaja_sie(a, b):
    """Czy dwa obszary (postacie kanoniczne) się nakładają."""
    ra, wa = _rodzaj(a)
    rb, wb = _rodzaj(b)
    if ra == "studio" or rb == "studio":
        return ra == rb and wa.casefold() == wb.casefold()
    if ra and ra == rb and wa == wb:
        return True
    return any(_sciezki_przecinaja(x, y) for x in sciezki(a) for y in sciezki(b))


def wspolne(lista_a, lista_b):
    """Opisy par obszarów, które się nakładają: sam obszar, gdy oba są takie same, inaczej „a ~ b”."""
    wynik = []
    for a in lista_a or []:
        for b in lista_b or []:
            if nakladaja_sie(a, b):
                opis = a if a.casefold() == b.casefold() else "%s ~ %s" % (a, b)
                if opis not in wynik:
                    wynik.append(opis)
    return wynik


def _baza(wzorzec):
    """(segmenty bez końcowego „**”, czy_cały_katalog). „swiat/las/**” → (["swiat","las"], True)."""
    s = _segmenty(wzorzec)
    katalog = False
    while s and s[-1] == "**":
        s.pop()
        katalog = True
    return s, katalog


def _pokrywa_sciezke(a, b):
    """Wzorzec a obejmuje cały wzorzec b: a jest równe b albo jest katalogiem nadrzędnym b (wzorce w a — tylko równość)."""
    sa, _ = _baza(a)
    sb, _ = _baza(b)
    if any(_wzorzec(x) or x == "**" for x in sa):
        return _segmenty(a) == _segmenty(b)
    return len(sa) <= len(sb) and sb[:len(sa)] == sa


def pokrywa(a, b):
    """Czy obszar a obejmuje cały obszar b (np. „swiat/postacie” obejmuje „model:rycerz”, „model:rycerz” — siebie)."""
    ra, wa = _rodzaj(a)
    rb, wb = _rodzaj(b)
    if ra == "studio" or rb == "studio":
        return ra == rb and wa.casefold() == wb.casefold()
    if ra and ra == rb and wa == wb:
        return True
    sa, sb = sciezki(a), sciezki(b)
    return bool(sb) and all(any(_pokrywa_sciezke(x, y) for x in sa) for y in sb)


def pokrywaja(lista_a, lista_b):
    """Czy każdy obszar z lista_b jest objęty którymś obszarem z lista_a (pusta lista_b = nie)."""
    return bool(lista_b) and all(any(pokrywa(a, b) for a in lista_a or []) for b in lista_b)


def dotyczy_pliku(lista_obszarow, plik):
    """Obszary z listy, w które wpada plik (ścieżka względem repozytorium z gita)."""
    p = str(plik or "").replace("\\", "/").strip("/")
    if not p:
        return []
    return [o for o in lista_obszarow or [] if any(_sciezki_przecinaja(x, p) for x in sciezki(o))]
