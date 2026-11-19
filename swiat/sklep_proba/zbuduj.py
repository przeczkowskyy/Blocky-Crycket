#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buduje kontener Workspace/SklepProba (sklep zbrojmistrza na próbę, D-106) w Roblox Studio.

    python -B swiat/sklep_proba/zbuduj.py --sucho     # bez Studio: dane aktualne, kontrola Luau, plan
    python -B swiat/sklep_proba/zbuduj.py             # buduje cały kontener (Studio w trybie Edit)
    python -B swiat/sklep_proba/zbuduj.py --skrypty   # tylko moduły i skrypty do istniejącego kontenera
    python -B swiat/sklep_proba/zbuduj.py --usun      # usuwa Workspace/SklepProba

Kontener (Folder, atrybuty Wygenerowane, Zrodlo, Zbudowano, Skrot):
  Moduly/DaneSklepu, LogikaSklepu, OknoSklepu      ModuleScript
  SerwerSklepu (Script, RunContext = Server), KlientSklepu (Script, RunContext = Client)
  Zdalne/Sklep (RemoteFunction)
  Sygnaly/SterowanieSerwera, Sygnaly/SterowanieKlienta   BindableFunction — haczyki testowe
Części świata sklep nie ma: stoisko, zbrojmistrz i podpowiedź E należą do bazaru (swiat/miasteczko_bazar_gra).

Zasady (wspólne miejsce Team Create) i szablony kodu są te same co u kowala (swiat/kowal_proba/zbuduj.py — tylko
odczyt): okno wybiera swiat/test_walki_roblox/cel_studio.py, KAŻDY wysyłany kod sprawdza game.PlaceId i tryb Edit,
ruszany jest tylko własny kontener (obiekt o tej nazwie bez atrybutu Wygenerowane → STOP), punkty historii przed i po,
nic nie jest zapisywane ani publikowane. --sucho nie importuje studio_mcp ani cel_studio.
"""
import argparse
import importlib.util
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))


def _modul(nazwa, sciezka):
    if nazwa in sys.modules:
        return sys.modules[nazwa]
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nazwa] = m
    spec.loader.exec_module(m)
    return m


if TU not in sys.path:
    sys.path.insert(0, TU)
DANE = _modul("dane_sklepu", os.path.join(TU, "dane.py"))
SLS = _modul("sprawdz_luau_sklepu", os.path.join(TU, "sprawdz_luau_sklepu.py"))
ZBK = _modul("zbuduj_kowala_dla_sklepu", os.path.join(REPO, "swiat", "kowal_proba", "zbuduj.py"))  # szablony, tylko odczyt

SL = SLS.SL
MIEJSCE = ZBK.MIEJSCE
NAGLOWEK_MIEJSCA = ZBK.NAGLOWEK_MIEJSCA
STRAZNIK = ZBK.STRAZNIK
LIMIT_ZRODLA = ZBK.LIMIT_ZRODLA
ZRODLO = "swiat/sklep_proba"
ZRODLA = os.path.join(TU, "zrodla")
KONTENER = "SklepProba"

SKRYPTY = [
    ("DaneSklepu.luau", "ModuleScript", "Moduly/DaneSklepu", None),
    ("LogikaSklepu.luau", "ModuleScript", "Moduly/LogikaSklepu", None),
    ("OknoSklepu.luau", "ModuleScript", "Moduly/OknoSklepu", None),
    ("SerwerSklepu.server.luau", "Script", "SerwerSklepu", "Server"),
    ("KlientSklepu.client.luau", "Script", "KlientSklepu", "Client"),
]
FOLDERY = ["Moduly", "Zdalne", "Sygnaly"]
INNE = [
    ("RemoteFunction", "Zdalne/Sklep"),
    ("BindableFunction", "Sygnaly/SterowanieSerwera"),
    ("BindableFunction", "Sygnaly/SterowanieKlienta"),
]


def zrodla_pakietu():
    wynik, braki = [], []
    for plik, klasa, sciezka, kontekst in SKRYPTY:
        pelna = os.path.join(ZRODLA, plik)
        if not os.path.isfile(pelna):
            braki.append(plik)
            continue
        wynik.append((sciezka, klasa, kontekst, ZBK.wczytaj(pelna), plik))
    if braki:
        print("BŁĄD: brak plików w zrodla/: " + ", ".join(braki))
        sys.exit(2)
    return wynik


def sprawdz_offline(zrodla):
    zle, D, _tekst = DANE.aktualny()
    print("dane.py --sprawdz: %s (skrót %s, przypadków %d)" % ("aktualne" if not zle else "NIEAKTUALNE: " + ", ".join(zle),
                                                              D["skrot"], sum(len(v) for v in D["przypadki"].values())))
    if zle:
        sys.exit("BŁĄD: pliki nieaktualne — uruchom python -B swiat/sklep_proba/dane.py")
    if D["kontener"] != KONTENER:
        sys.exit("BŁĄD: D.kontener (%s) ≠ %s" % (D["kontener"], KONTENER))
    bledy, parser = SLS.sprawdz_pliki(SLS.pliki_pakietu(), wypisz=print)
    print("sprawdz_luau_sklepu.py: %d plików, %s%s" % (len(zrodla), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
                                                      " (z parserem luau_mini)" if parser else " (bez parsera)"))
    if bledy:
        for b in bledy:
            print("  " + b)
        sys.exit("BŁĄD: kontrola Luau")
    for sciezka, klasa, kontekst, tekst, plik in zrodla:
        if not SL.pierwsza_instrukcja(tekst).startswith(STRAZNIK):
            sys.exit("BŁĄD: %s (%s) nie zaczyna się od strażnika Studio" % (sciezka, plik))
        if len(tekst) > LIMIT_ZRODLA:
            sys.exit("BŁĄD: %s ma %d znaków (limit Source 200 000)" % (sciezka, len(tekst)))
    return D


def _napis(s):
    return DANE._napis(s)


def kod_start(usun=False, czas="", skrot=""):
    return (ZBK.START.replace("__KONTENER__", KONTENER).replace("__USUN__", "true" if usun else "false")
            .replace("__ZRODLO__", ZRODLO).replace("__CZAS__", czas).replace("__SKROT__", skrot)
            .replace("__FOLDERY__", ", ".join(_napis(x) for x in FOLDERY))
            .replace("__TRWALE__", "{ }")
            .replace("__INNE__", ", ".join("{%s, %s}" % (_napis(k), _napis(p)) for k, p in INNE)))


def kod_skryptu(sciezka, klasa, kontekst, tekst):
    kod = (ZBK.SKRYPT.replace("__KONTENER__", KONTENER).replace("__SCIEZKA__", sciezka).replace("__KLASA__", klasa)
           .replace("__RUNCONTEXT__", "s.RunContext = Enum.RunContext.%s" % kontekst if kontekst else ""))
    return kod.replace("__ZRODLO__", ZBK.dlugi_napis(tekst))


def kod_konca(punkt_historii="zbudowano"):
    return (ZBK.KONIEC.replace("__KONTENER__", KONTENER).replace("__OCZEKIWANE__", str(len(SKRYPTY)))
            .replace("__PUNKT_HISTORII__", punkt_historii))


def wszystkie_kody():
    """Kod wysyłany do Studio (bez skryptów) — do --sucho i do testu parsowania."""
    return {"start": kod_start(czas="x", skrot="x"), "usun": kod_start(True), "koniec": kod_konca()}


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje kontener Workspace/SklepProba w Roblox Studio")
    ap.add_argument("--sucho", action="store_true", help="bez Studio: sprawdź dane i źródła, pokaż plan")
    ap.add_argument("--skrypty", action="store_true", help="tylko moduły i skrypty do istniejącego kontenera")
    ap.add_argument("--usun", action="store_true", help="usuń Workspace/SklepProba")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()

    if a.usun:
        zrodla, D = [], None
    else:
        zrodla = zrodla_pakietu()
        D = sprawdz_offline(zrodla)
        print("Kontener: Workspace/%s · Skrot danych: %s · placeId %d · modułów i skryptów: %d"
              % (KONTENER, D["skrot"], MIEJSCE, len(zrodla)))
        print("  %-28s → %s" % ("Folder", ", ".join(FOLDERY)))
        for klasa, sciezka in INNE:
            print("  %-28s → %s" % (sciezka, klasa))
        for sciezka, klasa, kontekst, tekst, plik in zrodla:
            print("  %-28s → %s%s, zrodla/%s (%d znaków)" % (sciezka, klasa, " [RunContext=%s]" % kontekst if kontekst else "",
                                                           plik, len(tekst)))
        m = D["miejsce"]
        print("  miejsce bazaru %s: stoisko %s, zasięg %s (serwer +%s), okno zamyka się po %s st"
              % (m["id"], m["punkt"], m["zasieg"], m["zapasSerwera"], m["zasiegOkna"]))
        print("  wejście kowala: Workspace/%s/Sygnaly/%s (bez niego okno pisze „%s”)"
              % (D["kowal"]["kontener"], D["kowal"]["sygnal"], D["teksty"]["nieczynny"]))
        kody = wszystkie_kody()
        print("  kod wysyłany do Studio: %s" % ", ".join("%s %d zn." % (k, len(v)) for k, v in kody.items()))
    if a.sucho:
        print("sucho: OK (Studio nieużywane)")
        return

    # --- dopiero tutaj Studio (--sucho niczego z tego nie importuje)
    for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
        if _s not in sys.path:
            sys.path.insert(0, _s)
    from cel_studio import MIEJSCE as MIEJSCE_GRY, wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    if MIEJSCE_GRY != MIEJSCE:
        sys.exit("BŁĄD: placeId w cel_studio.py (%s) ≠ %s — przerywam" % (MIEJSCE_GRY, MIEJSCE))
    try:
        with StudioMCP() as s:
            s.studios(wait=15)
            sid = wybierz_studio(s, a.studio)
            stan = s.call("get_studio_state", {"studio_id": sid})["text"]
            if "Current Studio Mode: Edit" not in stan:
                sys.exit("Studio nie jest w trybie Edit — zatrzymaj Play i spróbuj ponownie.\n" + stan)

            def wykonaj(kod):
                kod = NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", str(MIEJSCE)) + kod
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
                if r["is_error"]:
                    raise StudioError(r["text"][:3000])
                w = r["text"].strip()
                if w.startswith("STOP"):
                    print(w)
                    sys.exit(2)
                return w

            def wyslij_skrypty():
                for sciezka, klasa, kontekst, tekst, plik in zrodla:
                    print("  skrypt:", wykonaj(kod_skryptu(sciezka, klasa, kontekst, tekst)))

            t0 = time.time()
            if a.skrypty:
                wykonaj('local f = workspace:FindFirstChild("%s") if not f or f:GetAttribute("Wygenerowane") ~= true '
                        'then return "STOP: brak kontenera — zbuduj całość" end '
                        'game:GetService("ChangeHistoryService"):SetWaypoint("%s: przed wymianą skryptów") '
                        'f:SetAttribute("Skrot", "%s") return "OK"' % (KONTENER, KONTENER, D["skrot"]))
                wyslij_skrypty()
                print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca("skrypty wymienione")), time.time() - t0))
                return
            wynik = wykonaj(kod_start(a.usun, time.strftime("%Y-%m-%dT%H:%M:%S"), "" if a.usun else D["skrot"]))
            print("start:", wynik)
            if a.usun or wynik != "OK":
                return
            wyslij_skrypty()
            print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca()), time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
