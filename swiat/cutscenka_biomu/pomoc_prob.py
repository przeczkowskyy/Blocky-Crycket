# -*- coding: utf-8 -*-
"""Pomoc dla prób w grze pakietów biomów (las-pas, Bagno, Dżungla): jeden punkt „przelot” dla dwóch wykonań D-077.

Gdy w grze stoi Workspace/CutscenkaBiomu i przejął biom (atrybut „Przejmuje_<id>”), punkty prób o przelocie
sprawdzają NOWĄ cutscenkę (jej serwer i klient); gdy kontenera nie ma — stary przelot pasa, jak dotąd. Próba woła
te same funkcje w obu przypadkach, a wynik ma kształt, który znała wcześniej (faza, zablokowany, blokadaWalki,
pamiec[...], ostatniPrzelot.ok / ryk / czas, kamera).

`luau` to funkcja próby: luau(kod, "Server" | "Client") → tekst zwrócony przez Studio. Nic tu nie zmienia gry poza
uchwytami testowymi cutscenki („oznacz”, „odtworz”).
"""
import importlib.util
import json
import os

TU = os.path.dirname(os.path.abspath(__file__))
_stan = {}


def _dn():
    if "dn" not in _stan:
        spec = importlib.util.spec_from_file_location("cutscenka_biomu_dane", os.path.join(TU, "dane.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _stan["dn"] = m
    return _stan["dn"]


def biomy():
    """id biomu → { gra, klucz (pamięć starego przelotu), czas, lot } z ustawień i zapisanego modułu danych."""
    if "biomy" not in _stan:
        DN = _dn()
        U = DN.ustawienia()
        with open(DN.PLIK_LUAU, encoding="utf-8") as f:
            T = DN.tabela_luau(f.read())
        wynik = {}
        for wpis, b in zip(U["biomy"], T["biomy"]):
            wynik[b["id"]] = {"gra": wpis["kontener_gry"], "klucz": DN.dane_gry(wpis)["biom"]["pamiecPrzelot"],
                              "czas": b["trasa"]["czas"], "lot": b["trasa"]["lot"]}
        _stan["biomy"] = wynik
        _stan["kontener"] = U["kontener"]
        _stan["przejecie"] = U["zaleznosci"]["haczyk_pasa"]["atrybut_przejecia"]
    return _stan["biomy"]


def _kontener():
    biomy()
    return _stan["kontener"]


def przejety(luau, biom):
    """Czy cutscenkę tego biomu gra nowy pakiet (sprawdzane w grze; wynik „tak” zapamiętany na czas próby)."""
    if _stan.get(("przejety", biom)):
        return True
    biomy()
    try:
        w = luau('local c = workspace:FindFirstChild("%s") return tostring(c ~= nil and c:GetAttribute("%s%s") == true)'
                 % (_kontener(), _stan["przejecie"], biom), "Server").strip() == "true"
    except Exception:  # noqa: BLE001
        w = False
    if w:
        _stan[("przejety", biom)] = True
    return w


def _gracz(luau):
    kod = ('local H = game:GetService("HttpService") local k = workspace.%s '
           'local g = k.Sygnaly.SterowanieCutscenki:Invoke("gracz") if not g then return "{}" end g.pozycja = nil '
           'g.licznik = k:GetAttribute("LicznikCutscenek") return H:JSONEncode(g)' % _kontener())
    return json.loads(luau(kod, "Server"))


def _klient(luau):
    kod = ('local H = game:GetService("HttpService") '
           'return H:JSONEncode(workspace.%s.Sygnaly.SterowanieCutscenkiKlienta:Invoke("stan"))' % _kontener())
    return json.loads(luau(kod, "Client"))


def scal_gracza(luau, biom, gs):
    """Stan gracza ze starego uchwytu pasa z polami nowej cutscenki, gdy to ona gra w tym biomie."""
    if not przejety(luau, biom):
        return gs
    g = _gracz(luau)
    gs = dict(gs or {})
    gs["faza"] = g.get("faza")
    gs["zablokowany"] = bool(g.get("zakotwiczony"))
    gs["blokadaWalki"] = bool(g.get("blokadaWalki"))
    pamiec = dict(gs.get("pamiec") or {})
    pamiec[biomy()[biom]["klucz"]] = bool((g.get("widziane") or {}).get(biom))
    gs["pamiec"] = pamiec
    gs["cutscenka"] = g
    return gs


def scal_klienta(luau, biom, kp):
    """Stan klienta pasa z wynikiem ostatniej nowej cutscenki tego biomu (ostatniPrzelot.ok / ryk / czas, kamera)."""
    if not przejety(luau, biom):
        return kp
    k = _klient(luau)
    kp = dict(kp or {})
    o = k.get("ostatnia") or {}
    kp["ostatniPrzelot"] = ({"ok": o.get("ok"), "ryk": o.get("ryk"), "czas": o.get("czas"), "powod": o.get("powod"),
                             "napisStraznika": o.get("napisStraznika"), "plansza": o.get("plansza")}
                            if o.get("biom") == biom else {})
    kp["kamera"] = k.get("kamera")
    kp["cutscenka"] = k
    return kp


def dopasuj(luau, biom, G):
    """Czasy planu próby (G["przelot"] = lot bez końcowego zaciemnienia, G["zatrzymanie"] = dojście do strażnika)
    przestawione na nową cutscenkę, gdy to ona gra. → czy przestawiono."""
    if not przejety(luau, biom):
        return False
    b = biomy()[biom]
    G["przelot"] = b["czas"] - 0.5
    G["zatrzymanie"] = b["lot"]
    return True


def licznik(luau, biom, stary):
    """Licznik odtworzeń: nowej cutscenki (wspólny dla biomów), gdy to ona gra; inaczej licznik starego przelotu."""
    if not przejety(luau, biom):
        return stary
    return _gracz(luau).get("licznik") or 0


def odtworz(luau, biom):
    """Odtworzenie na życzenie przez uchwyt nowej cutscenki. → False, gdy biom gra stary przelot (próba woła stary uchwyt)."""
    if not przejety(luau, biom):
        return False
    luau('local g = game:GetService("Players"):GetPlayers()[1] '
         'return tostring(workspace.%s.Sygnaly.SterowanieCutscenki:Invoke("odtworz", g.Name, "%s"))' % (_kontener(), biom), "Server")
    return True


def oznacz(luau, lista):
    """Biomy z listy oznaczone jako „widziane” — próba innego biomu przechodzi przez nie bez cutscenki
    (odpowiednik „zapomnijPrzelot” starego przelotu). Bez kontenera cutscenki nic nie robi."""
    kod = ('local k = workspace:FindFirstChild("%s") if not k then return "brak" end '
           'local g = game:GetService("Players"):GetPlayers()[1] for _, b in { %s } do '
           'k.Sygnaly.SterowanieCutscenki:Invoke("oznacz", g.Name, b) end return "ok"'
           % (_kontener(), ", ".join('"%s"' % b for b in lista)))
    try:
        return luau(kod, "Server").strip()
    except Exception:  # noqa: BLE001
        return "blad"


OKNO_ZRZUTU_S = 1.2


def pora_na_zrzut(luau, biom, plan, t_trwa, teraz, okno=OKNO_ZRZUTU_S):
    """Czy zrobić pierwszy zrzut z planu [(chwila lotu w s, nazwa), …]. Liczy się czas lotu u KLIENTA, a zasłona musi
    być odsłonięta. Pozycje planu, których chwila minęła o więcej niż `okno` s, są z planu USUWANE — kadr zrobiony
    za późno pokazywałby co innego, niż mówi nazwa pliku.
    (18.11.2026: próba liczyła czas od chwili, w której sama zauważyła lot, a marsz przez bramę kończy się pod koniec
    lotu — zrzut „z połowy lotu” trafiał w końcowe zaciemnienie i wychodził czarny.) Gdy klienta nie da się
    zapytać: stary sposób, czas od zauważenia lotu."""
    if not plan:
        return False
    try:
        if przejety(luau, biom):
            k = _klient(luau)
            lot = k.get("trwa") or {}
            trwa, t, odslonieta = bool(lot) and bool(lot.get("lot")), lot.get("t", 0), (k.get("zaslona") or 0) >= 0.97
        else:
            kod = ('local H = game:GetService("HttpService") local s = workspace.%s.Sygnaly.SterowaniePasaKlienta:Invoke("stan") '
                   'local p = s.przelot return H:JSONEncode({ lot = p and p.lot or false, t = p and p.t or 0, zaslona = s.zaslona == true })'
                   % biomy()[biom]["gra"])
            s = json.loads(luau(kod, "Client"))
            trwa, t, odslonieta = bool(s.get("lot")), s.get("t", 0), not s.get("zaslona")
    except Exception:  # noqa: BLE001
        return t_trwa is not None and teraz - t_trwa >= plan[0][0]
    if not trwa:
        return False
    while plan and t > plan[0][0] + okno:
        plan.pop(0)
    return bool(plan) and t >= plan[0][0] and odslonieta
