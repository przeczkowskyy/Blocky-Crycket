#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próby gry w Play bez prawdziwego zapisu postępu (D-110, 19.11.2026) — jedno miejsce dla wszystkich prób.

Każde `start_stop_play` wysłane przez tools/studio_mcp.py (StudioMCP.call — korzystają z niego wszystkie proba_play.py,
SesjaPlay ze swiat/test_walki2 i swiat/przejscie_gry/regresja_calosci.py) przechodzi przez `play()`:
  • przed Play (tryb Edit): na kontenerze Workspace/StanGracza znacznik ZapisProbaDo = os.time() + CZAS_S. Serwer stanu
    gracza czyta go tylko przy starcie: przy znaczniku NIE czyta i NIE pisze prawdziwego zapisu człowieka — gracz zaczyna
    świeży (poziom 1, wartości Pawła), jak przed włączeniem zapisu. Znacznik sam wygasa po CZAS_S (gdy próba padnie
    przed Stop, zwykła gra człowieka wraca najpóźniej po kwadransie);
  • po Stop: znacznik zdjęty (razem z ZapisProbaMagazyn i ZapisProbaBledy).
Kontener jest, a znacznika nie da się ustawić → Play NIE startuje (wyjątek). Brak kontenera → bez znacznika (bez
kontenera nie ma zapisu).

Wyjątek od reguły: próba zapisu (swiat/stan_gracza/testy/proba_zapisu.py) przed Play ustawia też ZapisProbaMagazyn = true
(funkcja kod_magazynu) — serwer pracuje wtedy na osobnym magazynie próby (…_Studio_Proba), nigdy na prawdziwym.

Ręcznie (np. gdy agent włącza Play narzędziem MCP sesji, z pominięciem tools/studio_mcp.py):
    python -B tools/zapis_prob.py start [--studio <id>]     # znacznik przed własnym Play
    python -B tools/zapis_prob.py koniec [--studio <id>]    # zdjęcie po Stop
    python -B tools/zapis_prob.py stan [--studio <id>]      # znaczniki i tryb Studio
Nazwy atrybutów i czas są te same co D.zapis.proba w swiat/stan_gracza/dane.py (pilnuje test_zapisu.py).
"""
import os
import sys
import time

KONTENER = "StanGracza"
ATR_DO = "ZapisProbaDo"
ATR_MAGAZYNU = "ZapisProbaMagazyn"
ATR_BLEDOW = "ZapisProbaBledy"
CZAS_S = 900
PONOW_KONIEC = 12  # prób zdjęcia znacznika po Stop (Studio wraca do Edit kilka sekund)

_KONTENER_LUAU = ('local k = workspace:FindFirstChild("%s") '
                  'if not k or k:GetAttribute("Wygenerowane") ~= true then return "BRAK" end ' % KONTENER)

LUAU_START = ('if game:GetService("RunService"):IsRunning() then return "STOP: Studio jest w trybie Play" end '
              + _KONTENER_LUAU +
              'local d = os.time() + %d k:SetAttribute("%s", d) '
              'if k:GetAttribute("%s") ~= d then return "STOP: znacznik próby się nie ustawił" end '
              'return "OK " .. tostring(d)' % (CZAS_S, ATR_DO, ATR_DO))

LUAU_KONIEC = (_KONTENER_LUAU +
               'for _, a in { "%s", "%s", "%s" } do k:SetAttribute(a, nil) end return "OK"' % (ATR_DO, ATR_MAGAZYNU, ATR_BLEDOW))

LUAU_STAN = (_KONTENER_LUAU +
             'local d = k:GetAttribute("%s") '
             'return string.format("znacznik %%s (zostało %%s s), magazyn próby %%s, błędy %%s, ZapisPostepu %%s", '
             'tostring(d), if type(d) == "number" then tostring(d - os.time()) else "-", '
             'tostring(k:GetAttribute("%s")), tostring(k:GetAttribute("%s")), tostring(k:GetAttribute("ZapisPostepu")))'
             % (ATR_DO, ATR_MAGAZYNU, ATR_BLEDOW))


# po starcie Play (serwer): stan zapisu, jaki wybrał serwer stanu gracza — do dziennika próby
LUAU_PO_STARCIE = ('local k = workspace:FindFirstChild("%s") local z = k and k:GetAttribute("ZapisStan") '
                   'return if z == nil then "" else tostring(z) .. " | magazyn " .. tostring(k:GetAttribute("ZapisMagazyn"))'
                   % KONTENER)


def sprawdz_po_starcie(wywolaj, sid, prob=20, czekaj=0.5):
    """Po Play: odczytuje ZapisStan z serwera i wypisuje go (dziennik próby). Nie rzuca."""
    for _ in range(prob):
        try:
            r = wywolaj("execute_luau", dict(sid, code=LUAU_PO_STARCIE, datamodel_type="Server"), 30)
            w = (r.get("text") or "").strip()
            if not r.get("is_error") and w:
                print("[zapis_prob] Play ze znacznikiem próby: ZapisStan = %s" % w, flush=True)
                return w
        except Exception:  # noqa: BLE001 — serwer jeszcze rusza
            pass
        time.sleep(czekaj)
    print("[zapis_prob] Play: nie odczytałem ZapisStan z serwera", flush=True)
    return None


def kod_magazynu(bledy=None):
    """Luau (Edit) dla próby zapisu: ZapisProbaMagazyn = true i atrapa błędów (ile kolejnych wywołań usługi pada)."""
    b = "nil" if bledy is None else str(int(bledy))
    return (_KONTENER_LUAU + 'k:SetAttribute("%s", true) k:SetAttribute("%s", %s) return "OK"'
            % (ATR_MAGAZYNU, ATR_BLEDOW, b))


def _luau(wywolaj, kod, sid, timeout=60):
    """execute_luau w trybie Edit → tekst wyniku albo wyjątek RuntimeError (treść błędu)."""
    r = wywolaj("execute_luau", dict(sid, code=kod, datamodel_type="Edit"), timeout)
    if r.get("is_error"):
        raise RuntimeError((r.get("text") or "")[:400])
    return (r.get("text") or "").strip()


def koniec(wywolaj, sid=None, ponow=PONOW_KONIEC, czekaj=1.0):
    """Zdejmuje znaczniki (po Stop). Nie rzuca: przy kłopocie zwraca opis (znacznik i tak wygaśnie)."""
    sid = sid or {}
    blad = None
    for _ in range(max(1, ponow)):
        try:
            w = _luau(wywolaj, LUAU_KONIEC, sid)
            if w.startswith("OK") or w == "BRAK":
                return w
            blad = w
        except Exception as e:  # noqa: BLE001 — Studio wraca z Play do Edit
            blad = str(e)
        time.sleep(czekaj)
    print("[zapis_prob] UWAGA: nie zdjąłem znacznika próby (%s) — wygaśnie sam po %d s" % (blad, CZAS_S), flush=True)
    return "BŁĄD: %s" % blad


def play(wywolaj, arguments=None, timeout=None, blad=RuntimeError):
    """Opakowanie `start_stop_play`. wywolaj(name, args, timeout) → dict jak StudioMCP.call (bez tego opakowania)."""
    a = dict(arguments or {})
    sid = {"studio_id": a["studio_id"]} if a.get("studio_id") else {}
    if a.get("is_start"):
        try:
            w = _luau(wywolaj, LUAU_START, sid)
        except Exception as e:  # noqa: BLE001
            raise blad("Play nie startuje: nie ustawiłem znacznika próby (zapis postępu człowieka byłby w grze) — %s" % e)
        if not (w.startswith("OK") or w == "BRAK"):
            raise blad("Play nie startuje: znacznik próby — %s" % w)
        r = wywolaj("start_stop_play", a, timeout)
        if r.get("is_error"):
            koniec(wywolaj, sid, ponow=2)
        elif w != "BRAK":
            sprawdz_po_starcie(wywolaj, sid)
        return r
    r = wywolaj("start_stop_play", a, timeout)
    koniec(wywolaj, sid)
    return r


def main(argv):
    if not argv or argv[0] not in ("start", "koniec", "stan"):
        print(__doc__)
        return 2
    tu = os.path.dirname(os.path.abspath(__file__))
    for s in (tu, os.path.join(os.path.dirname(tu), "swiat", "test_walki_roblox")):
        if s not in sys.path:
            sys.path.insert(0, s)
    from studio_mcp import StudioMCP  # noqa: E402
    from cel_studio import wybierz_studio  # noqa: E402
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    with StudioMCP() as s:
        sid = {"studio_id": wybierz_studio(s, studio)}

        def wywolaj(n, a, t=None):
            return s._call(n, a, t)
        if argv[0] == "start":
            print(_luau(wywolaj, LUAU_START, sid))
        elif argv[0] == "koniec":
            print(koniec(wywolaj, sid))
        else:
            print(_luau(wywolaj, LUAU_STAN, sid))
            print(s._call("get_studio_state", sid)["text"].splitlines()[0])
    return 0


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
