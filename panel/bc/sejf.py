# -*- coding: utf-8 -*-
"""Sejf Obsidiana: indeks notatek, graf („sieć neuronowa”), treść notatek, wyszukiwanie i plan produkcji.

Zasada D-008: mózgiem projektu jest sejf `B&C/`. Ten moduł niczego nie zapisuje — tylko czyta notatki.

- Indeks obejmuje wszystkie sejfy z `konfiguracja()["sejfy"]` (ścieżka względem repo albo bezwzględna;
  brak folderu = sejf pomijany bez błędu). Przebudowa tylko wtedy, gdy zmienił się zestaw plików albo ich czasy
  modyfikacji; sprawdzenie najwyżej co 3 s.
- Frontmatter czyta prosty parser YAML własnej roboty, który nigdy nie rzuca wyjątku.
- Plan (roadmapa, zadania, decyzje, pytania, dziennik) parsowany z `<sejf B&C>/Produkcja/*.md`.
"""
import datetime
import os
import re
import threading
import time
import unicodedata
import zlib

from . import rdzen
from .rdzen import BladHTTP

POMIJANE_FOLDERY = {".obsidian", ".trash", "_narzędzia", "__pycache__"}
SPRAWDZANIE_CO_S = 3.0
MAKS_WYNIKOW = 40

# Stała paleta kategorii sejfu gry (zgodna z wyglądem panelu)
PALETA_BC = {
    "Gra": "#f5b82e", "Postacie": "#ff8a5b", "Styl": "#e85d9c", "UI": "#4ea8ff", "Technika": "#3ecf8e",
    "Produkcja": "#b08cff", "Źródła": "#9aa3b8", "Szablony": "#6b7280", "Badania": "#22d3ee", "(korzeń)": "#ffffff",
}
# Chłodna paleta dla innych sejfów i nieznanych folderów (wybór deterministyczny po nazwie)
PALETA_CHLODNA = ["#38bdf8", "#2dd4bf", "#818cf8", "#a3e635", "#f472b6", "#fb923c", "#94a3b8", "#c084fc"]
KORZEN = "(korzeń)"

# Rozszerzenia załączników: link do nich nie jest powiązaniem między notatkami
ZALACZNIKI = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".avif", ".ico", ".pdf", ".mp3", ".mp4",
              ".wav", ".ogg", ".webm", ".m4a", ".mov", ".mkv", ".flac", ".glb", ".gltf", ".fbx", ".obj", ".blend",
              ".zip", ".canvas", ".base", ".excalidraw", ".json", ".csv", ".txt", ".luau", ".lua", ".py", ".rbxl",
              ".rbxm", ".docx", ".xlsx", ".pptx", ".psd", ".fig"}

PLIKI_PLANU = {
    "roadmapa": "Roadmapa.md",
    "zadania": "Zadania.md",
    "decyzje": "Rejestr decyzji.md",
    "pytania": "Pytania otwarte.md",
    "dziennik": "Dziennik zmian.md",
}
FOLDER_PLANU = "Produkcja"


# =========================================================================== drobiazgi
def _nfc(s):
    return unicodedata.normalize("NFC", s or "")


def _klucz(s):
    """Klucz porównywania nazw: NFC, małe litery, ukośniki /."""
    return _nfc(s).replace("\\", "/").strip().lower()


def _iso_z_mtime(mtime):
    try:
        return datetime.datetime.fromtimestamp(mtime).astimezone().isoformat(timespec="seconds")
    except (OverflowError, OSError, ValueError):
        return None


def _czytaj(sciezka):
    try:
        with open(sciezka, "rb") as f:
            surowe = f.read()
    except OSError:
        return None
    tekst = surowe.decode("utf-8-sig", "replace")
    return tekst.replace("\r\n", "\n").replace("\r", "\n")


# =========================================================================== frontmatter (prosty YAML)
_RX_KLUCZ = re.compile(r"^(\"[^\"]*\"|'[^']*'|[^\s:#\-][^:]*?|-[^\s:][^:]*?)\s*:(?:[ \t]+(.*))?$")


def _odcytuj(s):
    """Zdejmuje cudzysłowy z napisu YAML (\"…\" z ucieczkami albo '…' z '')."""
    s = s.strip()
    if len(s) >= 2 and s[0] == '"' and s.endswith('"'):
        wnetrze = s[1:-1]
        return (wnetrze.replace('\\"', '"').replace("\\n", "\n").replace("\\t", "\t").replace("\\\\", "\\"))
    if len(s) >= 2 and s[0] == "'" and s.endswith("'"):
        return s[1:-1].replace("''", "'")
    return s


def _bez_komentarza(s):
    """Usuwa komentarz ` # …` z wartości bez cudzysłowów."""
    m = re.search(r"\s+#", s)
    return s[:m.start()].rstrip() if m else s


def _skalar(s):
    s = s.strip()
    if not s:
        return ""
    if s[0] in "\"'":
        koniec = s.find(s[0], 1)
        while s[0] == '"' and koniec > 0 and s[koniec - 1] == "\\":
            koniec = s.find('"', koniec + 1)
        if koniec > 0:
            return _odcytuj(s[:koniec + 1])
        return s[1:]
    s = _bez_komentarza(s)
    niski = s.lower()
    if niski in ("true", "yes"):
        return True
    if niski in ("false", "no"):
        return False
    if niski in ("null", "~"):
        return None
    if re.match(r"^-?(0|[1-9]\d{0,15})$", s):
        return int(s)
    return s


def _lista_w_nawiasach(s):
    """`[a, "b, c", d]` -> ["a", "b, c", "d"]. Brak zamykającego nawiasu = bierze do końca."""
    wnetrze = s.strip()[1:]
    elementy, biezacy, cudzyslow = [], "", None
    for znak in wnetrze:
        if cudzyslow:
            biezacy += znak
            if znak == cudzyslow:
                cudzyslow = None
        elif znak in "\"'":
            cudzyslow = znak
            biezacy += znak
        elif znak == ",":
            elementy.append(biezacy)
            biezacy = ""
        elif znak == "]":
            break
        else:
            biezacy += znak
    elementy.append(biezacy)
    return [_skalar(e) for e in elementy if e.strip()]


def _wartosc(s):
    s = (s or "").strip()
    if s.startswith("[") and not s.startswith("[["):
        return _lista_w_nawiasach(s)
    return _skalar(s)


def _yaml(linie):
    """Rozumie: `klucz: wartość`, listy `[a, b]`, listy wielowierszowe `- x`, napisy w cudzysłowach, bloki `|`/`>`
    i jeden poziom zagnieżdżonych kluczy. Czego nie rozumie — pomija."""
    wynik = {}
    i, n = 0, len(linie)
    while i < n:
        try:
            linia = linie[i].rstrip()
            i += 1
            if not linia.strip() or linia.lstrip().startswith("#") or linia[:1] in (" ", "\t"):
                continue
            m = _RX_KLUCZ.match(linia)
            if not m:
                continue
            klucz = _odcytuj(m.group(1).strip())
            surowa = (m.group(2) or "").strip()
            if surowa in ("|", ">", "|-", ">-", "|+", ">+"):
                blok = []
                while i < n and (not linie[i].strip() or linie[i][:1] in (" ", "\t")):
                    blok.append(linie[i].strip())
                    i += 1
                wynik[klucz] = ("\n" if surowa.startswith("|") else " ").join(blok).strip()
            elif surowa == "" or surowa.startswith("#"):
                elementy, pod = [], {}
                while i < n:
                    l = linie[i].rstrip()
                    s = l.strip()
                    if not s:
                        i += 1
                        continue
                    if s == "-" or s.startswith("- "):
                        elementy.append(_wartosc(s[1:]))
                        i += 1
                    elif l[:1] in (" ", "\t"):
                        mm = _RX_KLUCZ.match(s)
                        if mm:
                            pod[_odcytuj(mm.group(1).strip())] = _wartosc(mm.group(2))
                        i += 1
                    else:
                        break
                wynik[klucz] = elementy if elementy else (pod if pod else None)
            else:
                wynik[klucz] = _wartosc(surowa)
        except Exception:                                      # dziwny YAML: bierzemy to, co już zrozumiane
            continue
    return wynik


def parsuj_frontmatter(tekst):
    """Zwraca (frontmatter: dict, treść bez frontmattera, surowy tekst frontmattera). Nigdy nie rzuca."""
    try:
        tekst = (tekst or "").lstrip("﻿")
        if not tekst.startswith("---"):
            return {}, tekst, ""
        linie = tekst.split("\n")
        if linie[0].strip() != "---":
            return {}, tekst, ""
        for k in range(1, len(linie)):
            if linie[k].strip() in ("---", "..."):
                return _yaml(linie[1:k]), "\n".join(linie[k + 1:]), "\n".join(linie[1:k])
        return {}, tekst, ""
    except Exception:
        return {}, tekst or "", ""


def _tagi(fm):
    surowe = fm.get("tags", fm.get("tagi", fm.get("tag")))
    if surowe is None:
        return []
    if isinstance(surowe, (list, tuple)):
        lista = surowe
    else:
        lista = re.split(r"[,\s]+", str(surowe))
    wynik = []
    for t in lista:
        if t is None or isinstance(t, (dict, list)):
            continue
        t = str(t).strip().lstrip("#").strip()
        if t and t not in wynik:
            wynik.append(t)
    return wynik


# =========================================================================== wikilinki
_RX_LINK_LUB_KOD = re.compile(r"(`+)(?:.+?)\1|(!?)\[\[([^\[\]\n]+?)\]\]")
_RX_PLOT = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def bez_blokow_kodu(tekst):
    """Zastępuje linie bloków kodu (``` / ~~~) pustymi liniami (numeracja linii zostaje)."""
    wyjscie, plot = [], None
    for linia in tekst.split("\n"):
        m = _RX_PLOT.match(linia)
        if plot:
            if m and m.group(1)[0] == plot[0] and len(m.group(1)) >= len(plot) and not linia.strip()[len(m.group(1)):].strip():
                plot = None
            wyjscie.append("")
            continue
        if m:
            plot = m.group(1)
            wyjscie.append("")
            continue
        wyjscie.append(linia)
    return "\n".join(wyjscie)


def wyciagnij_linki(tekst):
    """Lista (cel, osadzenie) z tekstu bez bloków kodu; linki w `kodzie` są pomijane.
    Cel bez aliasu i nagłówka; puste cele (link do nagłówka tej samej notatki) pominięte."""
    wynik = []
    for m in _RX_LINK_LUB_KOD.finditer(bez_blokow_kodu(tekst)):
        if m.group(1):                                         # fragment `kodu`
            continue
        cel = m.group(3).split("|", 1)[0].rstrip("\\")
        cel = cel.split("#", 1)[0].strip()
        if cel:
            wynik.append((cel, m.group(2) == "!"))
    return wynik


# =========================================================================== indeks notatek
_blokada = threading.Lock()
_pamiec = {"sprawdzono": 0.0, "podpis": None, "indeks": None}


def _sejfy():
    """[(id, nazwa, ścieżka bezwzględna)] istniejących sejfów z konfiguracji."""
    wynik, widziane = [], set()
    for s in rdzen.konfiguracja().get("sejfy") or []:
        if not isinstance(s, dict):
            continue
        sid = str(s.get("id") or "").strip()
        sc = str(s.get("sciezka") or "").strip()
        if not sid or not sc or sid in widziane:
            continue
        pelna = sc if os.path.isabs(sc) else os.path.join(rdzen.REPO, sc)
        pelna = os.path.normpath(pelna)
        if os.path.isdir(pelna):
            widziane.add(sid)
            wynik.append((sid, str(s.get("nazwa") or sid), pelna))
    return wynik


def _w_repo(sciezka):
    try:
        repo = os.path.normcase(os.path.realpath(rdzen.REPO))
        p = os.path.normcase(os.path.realpath(sciezka))
        return os.path.commonpath([repo, p]) == repo
    except ValueError:                                         # inny dysk
        return False


def _skanuj(sejfy):
    """Lista (id sejfu, ścieżka, mtime_ns, rozmiar) wszystkich notatek .md."""
    pliki = []
    for sid, _, baza in sejfy:
        for korzen, katalogi, nazwy in os.walk(baza):
            katalogi[:] = sorted(d for d in katalogi if d not in POMIJANE_FOLDERY and not d.startswith("."))
            for nazwa in sorted(nazwy):
                if not nazwa.lower().endswith(".md"):
                    continue
                p = os.path.join(korzen, nazwa)
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                pliki.append((sid, p, st.st_mtime_ns, st.st_size))
    return pliki


def _kolor(sid, kategoria):
    if sid == "B&C" and _nfc(kategoria) in PALETA_BC:
        return PALETA_BC[_nfc(kategoria)]
    return PALETA_CHLODNA[zlib.crc32(_nfc(kategoria).encode("utf-8")) % len(PALETA_CHLODNA)]


def zbuduj_indeks(sejfy, pliki=None):
    """Czyta notatki i liczy graf. `sejfy` = [(id, nazwa, ścieżka)]. Funkcja czysta (bez pamięci podręcznej)."""
    if pliki is None:
        pliki = _skanuj(sejfy)
    bazy = {sid: baza for sid, _, baza in sejfy}
    kolejnosc_sejfow = {sid: k for k, (sid, _, _) in enumerate(sejfy)}
    w_repo = {sid: _w_repo(baza) for sid, _, baza in sejfy}

    notatki = []
    for sid, p, mtime_ns, _ in pliki:
        tekst = _czytaj(p)
        if tekst is None:
            continue
        wzgl = _nfc(os.path.relpath(p, bazy[sid]).replace("\\", "/"))
        folder = wzgl.rsplit("/", 1)[0] if "/" in wzgl else ""
        nazwa = wzgl.rsplit("/", 1)[-1][:-3]
        fm, tresc, fm_surowy = parsuj_frontmatter(tekst)
        status = fm.get("status")
        notatki.append({
            "sejf": sid, "abs": p, "wzgl": wzgl,
            "sciezka": _nfc(rdzen.wzgledem_repo(p)) if w_repo[sid] else "sejf:%s/%s" % (sid, wzgl),
            "tytul": nazwa, "folder": folder, "kategoria": folder.split("/")[0] if folder else KORZEN,
            "fm": fm, "tresc": tresc, "status": "" if status is None else str(status), "tagi": _tagi(fm),
            "slowa": len(re.findall(r"\w+", tresc)), "zmieniono": _iso_z_mtime(mtime_ns / 1e9),
            "linki_surowe": wyciagnij_linki(fm_surowy + "\n" + tresc),
        })
    notatki.sort(key=lambda n: (kolejnosc_sejfow.get(n["sejf"], 99), n["wzgl"].lower()))

    # słowniki do rozwiązywania wikilinków: po nazwie pliku i po ścieżce w sejfie (bez .md)
    po_nazwie, po_sciezce = {}, {}
    for i, n in enumerate(notatki):
        po_nazwie.setdefault(_klucz(n["tytul"]), []).append(i)
        po_sciezce.setdefault(_klucz(n["wzgl"][:-3]), []).append(i)

    def rozwiaz(cel, sid):
        k = _klucz(cel)
        if k.endswith(".md"):
            k = k[:-3]
        k = k.strip("/")
        kandydaci = po_sciezce.get(k) if "/" in k else None
        if not kandydaci:
            kandydaci = po_nazwie.get(k.rsplit("/", 1)[-1])
        if not kandydaci:
            return None
        return min(kandydaci, key=lambda j: (notatki[j]["sejf"] != sid, notatki[j]["wzgl"].count("/"),
                                             notatki[j]["wzgl"].lower()))

    krawedzie, nierozwiazane = set(), []
    wy = [[] for _ in notatki]
    we = [[] for _ in notatki]
    widziane_nierozw = set()
    for i, n in enumerate(notatki):
        for cel, osadzenie in n["linki_surowe"]:
            rozszerzenie = os.path.splitext(cel)[1].lower()
            if rozszerzenie in ZALACZNIKI:                     # obraz, PDF itp. — nie notatka
                continue
            j = rozwiaz(cel, n["sejf"])
            if j is None:
                if osadzenie:                                  # osadzenie czegoś, co nie jest notatką .md
                    continue
                if (i, _klucz(cel)) not in widziane_nierozw:
                    widziane_nierozw.add((i, _klucz(cel)))
                    nierozwiazane.append({"z": n["sciezka"], "link": cel})
                continue
            if j == i:
                continue
            if j not in wy[i]:
                wy[i].append(j)
            if i not in we[j]:
                we[j].append(i)
            krawedzie.add((min(i, j), max(i, j)))

    sasiedzi = [set() for _ in notatki]
    for a, b in krawedzie:
        sasiedzi[a].add(b)
        sasiedzi[b].add(a)

    kategorie = {}
    for n in notatki:
        k = (n["sejf"], n["kategoria"])
        kategorie[k] = kategorie.get(k, 0) + 1

    def porzadek_kategorii(k):
        sid, nazwa = k
        lista = list(PALETA_BC)
        return (kolejnosc_sejfow.get(sid, 99), nazwa != KORZEN,
                lista.index(nazwa) if sid == "B&C" and nazwa in lista else 50, nazwa.lower())

    return {
        "notatki": notatki,
        "po_sciezce_api": {n["sciezka"]: i for i, n in enumerate(notatki)},
        "krawedzie": sorted(krawedzie),
        "stopnie": [len(s) for s in sasiedzi],
        "wy": wy, "we": we,
        "nierozwiazane": nierozwiazane,
        "kategorie": [{"id": "%s/%s" % k, "nazwa": k[1], "sejf": k[0], "kolor": _kolor(k[0], k[1]), "liczba": c}
                      for k, c in sorted(kategorie.items(), key=lambda kv: porzadek_kategorii(kv[0]))],
        "sejfy": [{"id": sid, "nazwa": nazwa, "w_repo": w_repo[sid],
                   "prefiks": (_nfc(rdzen.wzgledem_repo(baza)) + "/") if w_repo[sid] else "sejf:%s/" % sid}
                  for sid, nazwa, baza in sejfy],
        "bazy": bazy,
    }


def indeks():
    """Indeks z pamięci podręcznej; przebudowa tylko po zmianie plików (sprawdzanie najwyżej co 3 s)."""
    with _blokada:
        teraz = time.time()
        if _pamiec["indeks"] is not None and teraz - _pamiec["sprawdzono"] < SPRAWDZANIE_CO_S:
            return _pamiec["indeks"]
        sejfy = _sejfy()
        pliki = _skanuj(sejfy)
        podpis = (tuple(sejfy), tuple(pliki))
        if _pamiec["indeks"] is None or podpis != _pamiec["podpis"]:
            _pamiec["indeks"] = zbuduj_indeks(sejfy, pliki)
            _pamiec["podpis"] = podpis
        _pamiec["sprawdzono"] = time.time()
        return _pamiec["indeks"]


# =========================================================================== graf, notatka, wyszukiwanie
def siec():
    ix = indeks()
    wezly = []
    for i, n in enumerate(ix["notatki"]):
        wezly.append({"id": i, "tytul": n["tytul"], "sejf": n["sejf"], "folder": n["folder"],
                      "kategoria": n["kategoria"], "status": n["status"], "tagi": n["tagi"], "slowa": n["slowa"],
                      "zmieniono": n["zmieniono"], "stopien": ix["stopnie"][i], "sciezka": n["sciezka"]})
    return {
        "wezly": wezly,
        "krawedzie": [[a, b] for a, b in ix["krawedzie"]],
        "kategorie": ix["kategorie"],
        "nierozwiazane": ix["nierozwiazane"],
        "statystyki": {"notatki": len(wezly), "powiazania": len(ix["krawedzie"]), "sejfy": len(ix["sejfy"])},
    }


def _odrzuc_obca(sciezka, ix):
    """403 dla ścieżek spoza sejfów, 404 dla nieistniejących notatek w sejfie."""
    czesci = sciezka.split("/")
    obca = (not sciezka or sciezka.startswith("/") or ".." in czesci or "\x00" in sciezka
            or re.match(r"^[A-Za-z]:", sciezka) is not None
            or not any(sciezka.startswith(s["prefiks"]) for s in ix["sejfy"]))
    if obca:
        raise BladHTTP(403, "Ta ścieżka nie należy do żadnego sejfu")
    raise BladHTTP(404, "Nie ma takiej notatki (może została przeniesiona albo usunięta)")


def notatka(sciezka):
    ix = indeks()
    sciezka = _nfc(str(sciezka or "").replace("\\", "/").strip())
    i = ix["po_sciezce_api"].get(sciezka)
    if i is None:
        _odrzuc_obca(sciezka, ix)
    n = ix["notatki"][i]
    lista = lambda idx: [{"tytul": ix["notatki"][j]["tytul"], "sciezka": ix["notatki"][j]["sciezka"]} for j in idx]
    return {"sciezka": n["sciezka"], "tytul": n["tytul"], "sejf": n["sejf"], "frontmatter": n["fm"],
            "tresc_md": n["tresc"], "linki_wy": lista(ix["wy"][i]), "linki_we": lista(ix["we"][i]),
            "zmieniono": n["zmieniono"]}


def _fragment(tresc, poz, dlugosc, szer=160):
    if poz < 0:
        kawalek = tresc[:szer]
        przed, po = "", "…" if len(tresc) > szer else ""
    else:
        start = max(0, poz - (szer - dlugosc) // 2)
        koniec = min(len(tresc), start + szer)
        start = max(0, min(start, koniec - szer))
        kawalek = tresc[start:koniec]
        przed, po = ("…" if start > 0 else ""), ("…" if koniec < len(tresc) else "")
    return przed + re.sub(r"\s+", " ", kawalek).strip() + po


def szukaj(q):
    q = re.sub(r"\s+", " ", _nfc(q or "")).strip().lower()
    if not q:
        return {"wyniki": []}
    ix = indeks()
    w_tytule, w_tresci = [], []
    for n in ix["notatki"]:
        tytul_ok = q in n["tytul"].lower()
        poz = n["tresc"].lower().find(q)
        if not tytul_ok and poz < 0:
            continue
        wpis = {"sciezka": n["sciezka"], "tytul": n["tytul"], "sejf": n["sejf"],
                "fragment": _fragment(n["tresc"], poz, len(q))}
        (w_tytule if tytul_ok else w_tresci).append(wpis)
    return {"wyniki": (w_tytule + w_tresci)[:MAKS_WYNIKOW]}


# =========================================================================== plan produkcji
_RX_NAGLOWEK = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_RX_POLE = re.compile(r"^\s*[-*+]\s+\[([^\[\]])\]\s?(.*)$")
_RX_PODZIAL_POL = re.compile(r"\s+·\s+(?=\[[^\[\]]\]\s)")
_RX_PRIORYTET = re.compile(r"(?:\s*·\s*|\s+|^)#(wysoki|średni|sredni|niski)\s*$", re.IGNORECASE)
_RX_DATA_ZADANIA = re.compile(r"^(\d{4}-\d{2}-\d{2})\s*[:—–-]\s*(.*)$")
_RX_LINIA_POZIOMA = re.compile(r"^\s{0,3}([-*_])(\s*\1){2,}\s*$")


def _sekcje(tekst, poziom=2):
    """Dzieli tekst na sekcje po nagłówkach danego poziomu (pomija bloki kodu). Zwraca [(nagłówek, [linie])]."""
    wynik, biezaca, plot = [], None, None
    for linia in tekst.split("\n"):
        m_plot = _RX_PLOT.match(linia)
        if plot:
            if m_plot and m_plot.group(1)[0] == plot[0]:
                plot = None
            if biezaca is not None:
                biezaca[1].append(linia)
            continue
        if m_plot:
            plot = m_plot.group(1)
        m = _RX_NAGLOWEK.match(linia)
        if m and len(m.group(1)) <= poziom and not plot:
            if len(m.group(1)) == poziom:
                biezaca = (m.group(2).strip(), [])
                wynik.append(biezaca)
            else:
                biezaca = None                                  # nagłówek wyższego rzędu kończy sekcję
            continue
        if biezaca is not None:
            biezaca[1].append(linia)
    return wynik


def _pola_wyboru(linia):
    """`- [ ] A · [x] B` -> [(False, "A"), (True, "B")]. Linia bez pola wyboru -> []."""
    m = _RX_POLE.match(linia)
    if not m:
        return []
    wynik = []
    for kawalek in _RX_PODZIAL_POL.split("[%s] %s" % (m.group(1), m.group(2))):
        mm = re.match(r"^\[([^\[\]])\]\s?(.*)$", kawalek)
        if mm:
            wynik.append((mm.group(1) in "xX", mm.group(2).strip()))
    return wynik


def _status_w_nawiasie(naglowek):
    """`Faza 1 — Frontend (kanon, w trakcie)` -> ("Faza 1 — Frontend", "kanon, w trakcie")."""
    m = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", naglowek)
    if m and m.group(1).strip():
        return m.group(1).strip(), m.group(2).strip()
    return naglowek.strip(), ""


def parsuj_roadmape(tekst):
    _, tresc, _ = parsuj_frontmatter(tekst)
    fazy, propozycje = [], []
    for naglowek, linie in _sekcje(tresc, 2):
        aktywna = any(z in naglowek for z in ("▶", "►", "⏵"))
        czysty = re.sub(r"[▶►⏵]️?", "", naglowek).strip()
        pozycje, numerowane, opis = [], [], []
        for linia in linie:
            pola = _pola_wyboru(linia)
            if pola:
                pozycje.extend({"tekst_md": t, "zrobione": z} for z, t in pola)
                continue
            mn = re.match(r"^\s*(\d+)[.)]\s+(.*)$", linia)
            if mn:
                numerowane.append([int(mn.group(1)), mn.group(2).strip()])
                continue
            if numerowane and linia[:1] in (" ", "\t") and linia.strip():
                numerowane[-1][1] += " " + linia.strip()       # kontynuacja punktu listy
                continue
            if linia.strip() and not _RX_LINIA_POZIOMA.match(linia):
                opis.append(linia.strip())
        jest_faza = re.search(r"\bFaza\s+\d", czysty, re.IGNORECASE) is not None
        if jest_faza or (pozycje and not numerowane):
            nazwa, status = _status_w_nawiasie(czysty)
            zrobione = sum(1 for p in pozycje if p["zrobione"])
            fazy.append({"nazwa": nazwa, "opis": " ".join(opis), "status_tekst": status, "aktywna": aktywna,
                         "pozycje": pozycje,
                         "postep": int(round(100.0 * zrobione / len(pozycje))) if pozycje else 0})
        elif numerowane:
            for nr, tekst_punktu in numerowane:
                m = re.match(r"^\*\*(.+?)\*\*\s*:?\s*(.*)$", tekst_punktu)
                if m:
                    nazwa, opis_md = m.group(1).strip().rstrip(":").strip(), m.group(2).strip()
                elif ":" in tekst_punktu:
                    nazwa, opis_md = [s.strip() for s in tekst_punktu.split(":", 1)]
                else:
                    nazwa, opis_md = tekst_punktu, ""
                propozycje.append({"nr": nr, "nazwa": nazwa, "opis_md": opis_md})
    if fazy and not any(f["aktywna"] for f in fazy):           # brak ▶: aktywna = pierwsza „w trakcie”
        for f in fazy:
            if "w trakcie" in f["status_tekst"].lower():
                f["aktywna"] = True
                break
    return {"fazy": fazy, "propozycje": propozycje}


def parsuj_zadania(tekst):
    _, tresc, _ = parsuj_frontmatter(tekst)
    sekcje, otwarte, zrobione = [], 0, 0
    for naglowek, linie in _sekcje(tresc, 2):
        pozycje = []
        for linia in linie:
            for zrob, t in _pola_wyboru(linia):
                poz = {"tekst_md": t, "zrobione": zrob}
                mp = _RX_PRIORYTET.search(t)
                if mp:
                    p = mp.group(1).lower()
                    poz["priorytet"] = "średni" if p == "sredni" else p
                    t = t[:mp.start()].rstrip(" ·")
                md = _RX_DATA_ZADANIA.match(t)
                if md:
                    poz["data"] = md.group(1)
                    t = md.group(2).strip()
                poz["tekst_md"] = t
                pozycje.append(poz)
                if zrob:
                    zrobione += 1
                else:
                    otwarte += 1
        sekcje.append({"nazwa": naglowek, "pozycje": pozycje})
    return {"sekcje": sekcje, "otwarte": otwarte, "zrobione": zrobione}


_STATUSY_SLOWA = [("zatwierdzon", "zatwierdzona"), ("do decyzji", "do_decyzji"), ("do_decyzji", "do_decyzji"),
                  ("propozycj", "propozycja"), ("odrzucon", "odrzucona"), ("zastąpion", "zastapiona"),
                  ("zastapion", "zastapiona")]
_STATUSY_EMOJI = {"✅": "zatwierdzona", "✔": "zatwierdzona", "🕓": "do_decyzji", "🕒": "do_decyzji",
                  "⏳": "do_decyzji", "💡": "propozycja", "❌": "odrzucona", "♻": "zastapiona"}


def _linia_statusu(linia):
    """`✅ zatwierdzona · styl · źródło: …` -> (status, emoji, kategoria, meta) albo None."""
    czesci = [c.strip() for c in re.split(r"\s+·\s+|\s*·\s*$", linia.strip()) if c.strip()]
    if not czesci:
        return None
    m = re.match(r"^([^\w\s]+)\s*(.*)$", czesci[0])
    emoji, slowo = (m.group(1).strip(), m.group(2)) if m else ("", czesci[0])
    slowo = slowo.lower().strip("*_ ")
    status = None
    for wzor, wartosc in _STATUSY_SLOWA:
        if slowo.startswith(wzor):
            status = wartosc
            break
    if status is None:
        for znak, wartosc in _STATUSY_EMOJI.items():
            if emoji.startswith(znak):
                status = wartosc
                break
    if status is None:
        return None
    return status, emoji, (czesci[1] if len(czesci) > 1 else ""), czesci[2:]


def parsuj_decyzje(tekst):
    _, tresc, _ = parsuj_frontmatter(tekst)
    decyzje = []
    for naglowek, linie in _sekcje(tresc, 3):
        m = re.match(r"^(D-\d+)\s*[:.—–-]?\s*(.*)$", naglowek)
        if not m:
            continue
        # treść kończy linia pozioma (---) — dalej jest stopka rejestru
        tresc_linie = []
        for linia in linie:
            if _RX_LINIA_POZIOMA.match(linia):
                break
            tresc_linie.append(linia)
        while tresc_linie and not tresc_linie[0].strip():
            tresc_linie.pop(0)
        status, emoji, kategoria, meta = "propozycja", "", "", []
        if tresc_linie:
            st = _linia_statusu(tresc_linie[0])
            if st:
                status, emoji, kategoria, meta = st
                tresc_linie.pop(0)
        tytul_md = m.group(2).strip()
        decyzje.append({"id": m.group(1), "tytul": tytul_md.replace("`", ""), "tytul_md": tytul_md, "status": status,
                        "emoji": emoji, "kategoria": kategoria, "meta": meta,
                        "opis_md": "\n".join(tresc_linie).strip()})
    return decyzje


_RX_ODPOWIEDZ = re.compile(r"^\s*\*\*\s*Odpowied[źz]\s*:?\s*\*\*\s*:?\s*(.*)$", re.IGNORECASE)


def parsuj_pytania(tekst):
    _, tresc, _ = parsuj_frontmatter(tekst)
    pytania = []
    for naglowek, linie in _sekcje(tresc, 2):
        m = re.match(r"^(\d+)[.)]?\s+(.*)$", naglowek)
        if not m:
            continue
        pytanie, odpowiedz, w_odpowiedzi = [], [], False
        for linia in linie:
            mo = _RX_ODPOWIEDZ.match(linia) if not w_odpowiedzi else None
            if mo:
                w_odpowiedzi = True
                if mo.group(1).strip():
                    odpowiedz.append(mo.group(1))
                continue
            if _RX_LINIA_POZIOMA.match(linia):
                continue
            (odpowiedz if w_odpowiedzi else pytanie).append(linia)
        odp = "\n".join(odpowiedz).strip()
        pytania.append({"nr": int(m.group(1)), "tytul": m.group(2).strip(), "tresc_md": "\n".join(pytanie).strip(),
                        "odpowiedz_md": odp, "otwarte": not odp})
    return pytania


def parsuj_dziennik(tekst, limit=30):
    _, tresc, _ = parsuj_frontmatter(tekst)
    wpisy = []
    for naglowek, linie in _sekcje(tresc, 2):
        m = re.match(r"^(\d{4}-\d{2}-\d{2})\s*(?:[·|—–-]\s*)?(.*)$", naglowek)
        if not m:
            continue
        reszta = m.group(2).strip()
        mk = re.match(r"^(.*?)\s*\((.*)\)\s*$", reszta)
        kto, temat = (mk.group(1).strip(), mk.group(2).strip()) if mk and mk.group(1).strip() else (reszta, "")
        punkty = []
        for linia in linie:
            if not linia.strip() or _RX_LINIA_POZIOMA.match(linia):
                continue
            mp = re.match(r"^[-*+]\s+(.*)$", linia)
            if mp:
                punkty.append(mp.group(1).strip())
            elif linia[:1] in (" ", "\t") and punkty:
                punkty[-1] += "\n" + linia.rstrip()            # kontynuacja / podpunkt
            else:
                punkty.append(linia.strip())
        wpisy.append({"data": m.group(1), "kto": kto, "temat": temat, "punkty_md": punkty})
    wpisy = sorted(wpisy, key=lambda w: w["data"], reverse=True)  # stabilne: kolejność z pliku w obrębie dnia
    return wpisy[:limit]


PUSTY_PLAN = {
    "roadmapa": lambda: {"fazy": [], "propozycje": []},
    "zadania": lambda: {"sekcje": [], "otwarte": 0, "zrobione": 0},
    "decyzje": lambda: [],
    "pytania": lambda: [],
    "dziennik": lambda: [],
}
PARSERY = {"roadmapa": parsuj_roadmape, "zadania": parsuj_zadania, "decyzje": parsuj_decyzje,
           "pytania": parsuj_pytania, "dziennik": parsuj_dziennik}
_plan_pamiec = {"podpis": None, "plan": None}
_plan_blokada = threading.Lock()


def _sejf_planu():
    sejfy = _sejfy()
    for s in sejfy:
        if s[0] == "B&C":
            return s
    return sejfy[0] if sejfy else None


def pliki_planu():
    """{klucz: (ścieżka bezwzględna, ścieżka do pokazania)} — także dla plików, których nie ma."""
    s = _sejf_planu()
    if not s:
        return {}
    sid, _, baza = s
    wynik = {}
    for klucz, nazwa in PLIKI_PLANU.items():
        p = os.path.join(baza, FOLDER_PLANU, nazwa)
        pokaz = _nfc(rdzen.wzgledem_repo(p)) if _w_repo(baza) else "sejf:%s/%s/%s" % (sid, FOLDER_PLANU, nazwa)
        wynik[klucz] = (p, pokaz)
    return wynik


def plan():
    pliki = pliki_planu()
    stany = {}
    for klucz, (p, _) in pliki.items():
        try:
            stany[klucz] = os.stat(p).st_mtime_ns
        except OSError:
            stany[klucz] = None
    podpis = tuple(sorted((k, pliki[k][0], v) for k, v in stany.items()))
    with _plan_blokada:
        if _plan_pamiec["plan"] is not None and _plan_pamiec["podpis"] == podpis:
            return _plan_pamiec["plan"]
        wynik, zrodla = {}, {}
        for klucz in PARSERY:
            wynik[klucz] = PUSTY_PLAN[klucz]()
            if klucz not in pliki or stany.get(klucz) is None:
                continue
            p, pokaz = pliki[klucz]
            tekst = _czytaj(p)
            if tekst is None:
                continue
            zrodla[pokaz] = _iso_z_mtime(stany[klucz] / 1e9)
            try:
                wynik[klucz] = PARSERY[klucz](tekst)
            except Exception as e:                             # plan nigdy nie zwraca błędu
                rdzen.log("sejf: nie udało się odczytać %s: %r" % (pokaz, e))
        wynik["zrodla"] = zrodla
        _plan_pamiec.update(podpis=podpis, plan=wynik)
        return wynik


# =========================================================================== trasy
def _t_plan(z):
    return plan()


def _t_siec(z):
    return siec()


def _t_notatka(z):
    sciezka = z.q("sciezka")
    if not sciezka:
        raise BladHTTP(400, "Podaj ścieżkę notatki (parametr sciezka)")
    return notatka(sciezka)


def _t_szukaj(z):
    return szukaj(z.q("q", ""))


def zarejestruj(app):
    app.dodaj("GET", "/api/sejf/plan", _t_plan)
    app.dodaj("GET", "/api/sejf/siec", _t_siec)
    app.dodaj("GET", "/api/sejf/notatka", _t_notatka)
    app.dodaj("GET", "/api/sejf/szukaj", _t_szukaj)


def zdrowie():
    ix = indeks()
    liczby = {}
    for n in ix["notatki"]:
        liczby[n["sejf"]] = liczby.get(n["sejf"], 0) + 1
    skonfigurowane = [str(s.get("id")) for s in rdzen.konfiguracja().get("sejfy") or [] if isinstance(s, dict)]
    return {
        "sejfy": [{"id": s["id"], "nazwa": s["nazwa"], "notatki": liczby.get(s["id"], 0)} for s in ix["sejfy"]],
        "brakujace_sejfy": [sid for sid in skonfigurowane if sid not in {s["id"] for s in ix["sejfy"]}],
        "pliki_planu": {pokaz: os.path.isfile(p) for p, pokaz in pliki_planu().values()},
        "nierozwiazane_linki": len(ix["nierozwiazane"]),
    }
