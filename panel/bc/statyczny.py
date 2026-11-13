# -*- coding: utf-8 -*-
"""Lustro tylko-do-odczytu: strona statyczna z tym, co panel pokazuje z repozytorium (plan, raporty, podgląd 3D, sieć,
assety).

Po co: żeby zobaczyć stan projektu z telefonu, gdy żaden komputer z panelem nie jest włączony (np. przez GitHub Pages).
Jak: eksporter woła te same trasy GET co przeglądarka i zapisuje odpowiedzi jako pliki `dane/<klucz>.json`;
`static/tryb.js` dostaje `window.BC_STATYCZNY = true`, a `wspolne/api.js` czyta pliki zamiast API.

    python panel/serwer.py --eksport <folder>          # albo: cd panel && python -m bc.statyczny --do <folder>

W lustrze NIE ma: agenta, głosówek, wysyłania komentarzy, zapisu do sejfu (odpowiedzi, zadania, decyzje) ani danych
lokalnych (rozmowy z agentem, nagrania, kod dostępu, klucz Game Directora).
Jest tylko to, co i tak leży w repozytorium, plus publiczne liczby gry pobrane w chwili eksportu.
"""
import json
import os
import shutil
import sys
import urllib.parse

from . import rdzen
from .http import Odp, Strumien, Zadanie

_APP = None
POMIJANE_STATIC = ("_",)                                      # pliki robocze zaczynające się od podkreślenia


def klucz(tekst):
    """Klucz pliku danych: FNV-1a 32-bit (8 hex) + djb2 32-bit (8 hex) po bajtach UTF-8 — tak samo liczy wspolne/api.js."""
    f, d = 0x811C9DC5, 5381
    for b in str(tekst).encode("utf-8"):
        f = ((f ^ b) * 0x01000193) & 0xFFFFFFFF
        d = (d * 33 + b) & 0xFFFFFFFF
    return "%08x%08x" % (f, d)


def enc(s):
    """Odpowiednik encodeURIComponent z JavaScriptu."""
    return urllib.parse.quote(str(s), safe="-_.!~*'()")


def zarejestruj(app):
    global _APP
    _APP = app


def zdrowie():
    return {"eksport": "python panel/serwer.py --eksport <folder>"}


def _tylko_repo(siec):
    """Usuwa z grafu notatki sejfów spoza repozytorium (ścieżka „sejf:<id>/…”) — lustro pokazuje tylko to, co jest w repo.
    Prywatny sejf podłączony lokalnie (konfiguracja.lokalna.json) nigdy nie trafia do lustra."""
    wezly = siec.get("wezly") or []
    zachowaj = [i for i, w in enumerate(wezly) if not str(w.get("sciezka", "")).startswith("sejf:")]
    if len(zachowaj) == len(wezly):
        return siec
    mapa = {stary: nowy for nowy, stary in enumerate(zachowaj)}
    krawedzie = [[mapa[k[0]], mapa[k[1]]] for k in siec.get("krawedzie") or [] if k[0] in mapa and k[1] in mapa]
    stopnie = {}
    for a, b in krawedzie:
        stopnie[a] = stopnie.get(a, 0) + 1
        stopnie[b] = stopnie.get(b, 0) + 1
    nowe = []
    for stary in zachowaj:
        w = dict(wezly[stary])
        w["id"] = mapa[stary]
        w["stopien"] = stopnie.get(mapa[stary], 0)
        nowe.append(w)
    sejfy = {w.get("sejf") for w in nowe}
    liczniki = {}
    for w in nowe:
        liczniki[(w.get("sejf"), w.get("kategoria"))] = liczniki.get((w.get("sejf"), w.get("kategoria")), 0) + 1
    kategorie = []
    for k in siec.get("kategorie") or []:
        if k.get("sejf") in sejfy:
            k = dict(k)
            k["liczba"] = liczniki.get((k.get("sejf"), k.get("id")), k.get("liczba"))
            kategorie.append(k)
    out = dict(siec)
    out.update(wezly=nowe, krawedzie=krawedzie, kategorie=kategorie,
               nierozwiazane=[n for n in siec.get("nierozwiazane") or [] if not str(n.get("z", "")).startswith("sejf:")],
               statystyki={"notatki": len(nowe), "powiazania": len(krawedzie), "sejfy": len(sejfy)})
    return out


def _wywolaj(app, sciezka_z_zapytaniem):
    """Woła trasę GET tak, jak zrobiłaby to przeglądarka gościa. Zwraca (obiekt JSON | None, Odp | None)."""
    url = urllib.parse.urlsplit(sciezka_z_zapytaniem)
    sciezka = urllib.parse.unquote(url.path)
    query = {k: v[-1] for k, v in urllib.parse.parse_qs(url.query, keep_blank_values=True).items()}
    fn, params = app.znajdz("GET", sciezka)
    if fn is None:
        return None, None
    z = Zadanie("GET", sciezka, query, {}, b"", False, "gość", "0.0.0.0", "lustro")
    z.params = params
    wynik = fn(z)
    if isinstance(wynik, Strumien):
        return None, None
    if isinstance(wynik, Odp):
        return None, wynik
    if isinstance(wynik, tuple) and len(wynik) == 2 and isinstance(wynik[0], int):
        return (wynik[1] if wynik[0] < 400 else None), None
    return wynik, None


def eksportuj(app, folder, czas=None):
    czas = czas or rdzen.teraz()
    folder = os.path.abspath(folder)
    if os.path.realpath(folder) == os.path.realpath(rdzen.REPO) or os.path.realpath(folder).startswith(os.path.realpath(rdzen.PANEL)):
        raise ValueError("Folder lustra nie może być repozytorium ani leżeć w panel/")
    os.makedirs(folder, exist_ok=True)
    # 1) pliki strony
    for katalog, podkatalogi, pliki in os.walk(rdzen.STATIC):
        podkatalogi[:] = [d for d in podkatalogi if not d.startswith(POMIJANE_STATIC)]
        rel = os.path.relpath(katalog, rdzen.STATIC)
        cel = os.path.join(folder, rel) if rel != "." else folder
        os.makedirs(cel, exist_ok=True)
        for p in pliki:
            if not p.startswith(POMIJANE_STATIC):
                shutil.copyfile(os.path.join(katalog, p), os.path.join(cel, p))
    with open(os.path.join(folder, "tryb.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write("// Lustro tylko do odczytu wygenerowane przez panel/bc/statyczny.py\n"
                "window.BC_STATYCZNY = true;\nwindow.BC_STATYCZNY_CZAS = %s;\n" % json.dumps(czas))
    with open(os.path.join(folder, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")
    dane = os.path.join(folder, "dane")
    os.makedirs(dane, exist_ok=True)
    stat = {"json": 0, "pliki": 0, "bledy": []}

    def zapisz(sciezka, obj):
        with open(os.path.join(dane, klucz(sciezka) + ".json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
        stat["json"] += 1

    def trasa(sciezka, zastap=None):
        try:
            obj, odp = (zastap, None) if zastap is not None else _wywolaj(app, sciezka)
        except Exception as e:                                 # jedna zepsuta trasa nie psuje całego lustra
            stat["bledy"].append("%s: %s" % (sciezka, e))
            return None
        if obj is not None:
            zapisz(sciezka, obj)
        elif odp is not None and odp.status < 400 and (odp.plik_sciezka or odp.cialo):
            # trasa oddaje gotowy plik JSON (np. czesci.json migawki) — kopiujemy go bez ponownego parsowania
            cel = os.path.join(dane, klucz(sciezka) + ".json")
            try:
                if odp.plik_sciezka:
                    shutil.copyfile(odp.plik_sciezka, cel)
                else:
                    with open(cel, "wb") as f:
                        f.write(odp.cialo)
            except OSError as e:
                stat["bledy"].append("%s: %s" % (sciezka, e))
                return None
            stat["json"] += 1
        return obj

    def plik(sciezka):
        """Plik binarny pod tą samą ścieżką względną co w API (wspolne/api.js: plik())."""
        try:
            _, odp = _wywolaj(app, sciezka)
        except Exception as e:
            stat["bledy"].append("%s: %s" % (sciezka, e))
            return
        if odp is None or not (odp.plik_sciezka or odp.cialo):
            return
        cel = os.path.join(folder, *[urllib.parse.unquote(c) for c in sciezka.lstrip("/").split("/")])
        if not os.path.realpath(cel).startswith(os.path.realpath(folder) + os.sep):
            stat["bledy"].append("%s: ścieżka poza folderem lustra" % sciezka)   # nazwa pliku z danych wspólnych
            return
        try:
            os.makedirs(os.path.dirname(cel), exist_ok=True)
            if odp.plik_sciezka:
                shutil.copyfile(odp.plik_sciezka, cel)
            else:
                with open(cel, "wb") as f:
                    f.write(odp.cialo)
        except OSError as e:
            stat["bledy"].append("%s: %s" % (sciezka, e))
            return
        stat["pliki"] += 1

    # 2) rdzeń i stany „niedostępne w lustrze”
    trasa("/api/ja", {"kto": "gość", "lokalny": False, "gospodarz": "", "tryb_statyczny": True, "wersja": rdzen.WERSJA,
                      "czas_lustra": czas, "game_director": False, "zapis_sejfu": False})   # lustro niczego nie zapisuje
    cfg = rdzen.konfiguracja()
    w_repo = [s for s in cfg.get("sejfy") or [] if isinstance(s, dict) and not os.path.isabs(str(s.get("sciezka") or ""))]
    trasa("/api/konfiguracja", {"port": None, "gra": cfg.get("gra"),
                                "sejfy": [{"id": s.get("id"), "nazwa": s.get("nazwa")} for s in w_repo],
                                "agent": {"zdalnie": False}, "glos": cfg.get("glos")})
    niedostepne = "Lustro tylko do odczytu — ta funkcja działa w panelu uruchomionym na komputerze."
    trasa("/api/agent/stan", {"dostepny": False, "zdalnie": False, "tryby": [], "tryb_domyslny": "plan", "model": "", "powod": niedostepne})
    trasa("/api/agent/watki", {"watki": []})
    trasa("/api/glos/stan", {"whisper": False, "model": "", "powod": niedostepne})
    trasa("/api/studio/stan", {"mostek": False, "polaczone": False, "osoby": [], "blad": niedostepne})
    trasa("/api/studio/konsola", {"linie": [], "bledy": 0, "ostrzezenia": 0})
    trasa("/api/zdrowie", {"rdzen": {}, "moduly": {}, "szczegoly": {}, "lustro": True})
    trasa("/api/dostep", {"lan": False, "token": "", "adresy": [], "podpowiedz": niedostepne})
    # telemetria gry: do lustra nie trafia nic z gry (odczyt wymaga klucza Open Cloud na komputerze z panelem)
    for sciezka in ("/api/telemetria", "/api/telemetria?godzin=24"):
        trasa(sciezka, {"wlaczona": False, "powod": "niedostępne w podglądzie"})

    # 3) sejf
    trasa("/api/sejf/plan")
    try:
        siec = _tylko_repo(_wywolaj(app, "/api/sejf/siec")[0] or {})
    except Exception as e:
        stat["bledy"].append("/api/sejf/siec: %s" % e)
        siec = {}
    if siec:
        zapisz("/api/sejf/siec", siec)
    for w in siec.get("wezly") or []:
        if not w.get("sciezka"):
            continue
        sc = "/api/sejf/notatka?sciezka=" + enc(w["sciezka"])
        try:
            nt = _wywolaj(app, sc)[0]
        except Exception as e:
            stat["bledy"].append("%s: %s" % (sc, e))
            continue
        if nt:
            for pole in ("linki_wy", "linki_we"):              # powiązania z prywatnymi sejfami nie trafiają do lustra
                nt[pole] = [l for l in nt.get(pole) or [] if not str((l or {}).get("sciezka", "")).startswith("sejf:")]
            zapisz(sc, nt)

    # 4) podgląd 3D
    podglad = trasa("/api/podglad") or {}
    cele = set()
    for m in podglad.get("migawki") or []:
        mid = m.get("id")
        if not mid:
            continue
        trasa("/api/podglad/%s/czesci" % enc(mid))
        for nazwa in list(m.get("zrzuty") or []) + ([m["model"]] if m.get("model") else []):
            plik("/api/podglad/%s/plik/%s" % (enc(mid), enc(nazwa)))
        cele.add(("migawka", mid))
        for g in m.get("grupy") or []:
            if isinstance(g, dict) and g.get("sciezka"):
                cele.add(("studio", g["sciezka"]))

    # 4b) assety: rejestr grafik i gotowe obrazy pod tymi samymi ścieżkami co w API (nic z assets/raw/)
    assety = trasa("/api/assety") or {}
    obrazy = set()
    for a in assety.get("assety") or []:
        obrazy.update(str(a[pole]).split("?")[0] for pole in ("obraz", "miniatura") if a.get(pole))
        if a.get("cel_komentarzy"):
            cele.add(("plik", a["cel_komentarzy"]))
    for adres in sorted(obrazy):
        plik(adres)
    if assety.get("assety"):
        trasa("/api/komentarze?typ=plik")                      # liczniki komentarzy na kartach assetów

    # 5) raporty i komentarze
    raporty = trasa("/api/raporty") or {}
    for r in raporty.get("raporty") or []:
        rid = r.get("id")
        if not rid:
            continue
        trasa("/api/raporty/%s" % enc(rid))
        for nazwa in r.get("zrzuty") or []:
            plik("/api/raporty/%s/plik/%s" % (enc(rid), enc(nazwa)))
        cele.add(("raport", rid))
        for k in r.get("komponenty") or []:
            if isinstance(k, dict) and k.get("typ") and k.get("cel"):
                cele.add((k["typ"], k["cel"]))
    wszystkie = trasa("/api/komentarze") or {}
    for k in wszystkie.get("komentarze") or []:
        c = k.get("cel") or {}
        if c.get("typ") and c.get("cel"):
            cele.add((c["typ"], c["cel"]))
    for typ, cel in sorted(cele):
        if typ in ("raport", "studio", "notatka", "migawka", "plik"):  # tylko cele, do których da się pisać komentarze
            trasa("/api/komentarze?typ=%s&cel=%s" % (enc(typ), enc(cel)))

    # 6) reszta: obecność i git (same commity — bez listy lokalnych plików), analityka (publiczne liczby z chwili eksportu)
    try:
        ob = _wywolaj(app, "/api/obecnosc")[0] or {}
        zapisz("/api/obecnosc", {"panel": [], "studio": {"dostepne": False, "osoby": []}, "git": ob.get("git") or []})
    except Exception as e:
        stat["bledy"].append("/api/obecnosc: %s" % e)
    try:
        g = _wywolaj(app, "/api/git/stan")[0] or {}
        zapisz("/api/git/stan", {"galaz": g.get("galaz"), "czyste": True, "zmienione": [], "zmiany_panelu": 0, "do_wyslania": 0,
                                 "do_pobrania": 0, "ostatni_fetch": None, "ostatnie_commity": g.get("ostatnie_commity") or [],
                                 "zdalne": g.get("zdalne")})
    except Exception as e:
        stat["bledy"].append("/api/git/stan: %s" % e)
    try:
        an = _wywolaj(app, "/api/analityka")[0] or {}
        an["studio"] = {"polaczone": False, "bledy": 0, "ostrzezenia": 0, "konsola": []}
        zapisz("/api/analityka", an)
    except Exception as e:
        stat["bledy"].append("/api/analityka: %s" % e)
    return stat


def main():
    import argparse
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Eksport lustra tylko-do-odczytu panelu")
    ap.add_argument("--do", required=True, help="folder wyjściowy (poza repozytorium albo ignorowany przez git)")
    a = ap.parse_args()
    sys.path.insert(0, rdzen.PANEL)
    import serwer                                              # ładuje moduły i trasy
    serwer.zaladuj_moduly()
    stat = eksportuj(serwer.APP, a.do)
    print("Lustro: %d plików danych, %d plików binarnych -> %s" % (stat["json"], stat["pliki"], os.path.abspath(a.do)))
    for b in stat["bledy"]:
        print("  uwaga:", b)


if __name__ == "__main__":
    main()
