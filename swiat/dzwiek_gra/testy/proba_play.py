#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba w trybie PLAY podpięcia dźwięku (pakiet swiat/dzwiek_gra) — bez wgranych plików; sam wraca do trybu Edit.

    python -B swiat/dzwiek_gra/testy/proba_play.py <folder wyjściowy poza repozytorium> [--studio <id>]

Warunki: Studio w trybie Edit, zbudowane Workspace/DzwiekGra (zbuduj.py) i Workspace/TestWalki2 (odtwarzacz z obsługą
arkusza). Skrypt niczego nie zapisuje w miejscu; atrybuty testowe ustawia tylko w sesji Play (u klienta).

LISTA KONTROLNA:
  D1 Sound.PlaybackRegionsEnabled i Sound.PlaybackRegion istnieją i dają się ustawić (u klienta)
  D2 walka na arkuszu z katalogu — próba rozpoznaje stan, który zastała, i wypisuje go (od 17.11.2026 katalog ma
     prawdziwe identyfikatory, a gra może jeszcze nie mieć prawa do zasobu):
       • katalog: id 0 → dźwięki wbudowane (OstatniZestawDzwiekow = „wbudowany”), zagrane > 0, bez odcinków;
       • arkusz wczytany → zestaw „arkusz”, grają odcinki (OstatnieOdcinkiArkusza niepuste), zagrane > 0;
       • arkusz niewczytany → zestaw „arkusz”, OstatniArkuszNiewczytany > 0, odcinków 0, zagrane > 0 (grały
         wbudowane) — nigdy cisza w walce
  D3 walka z „arkuszem” próbnym (wbudowany dźwięk Robloxa action_falling.mp3 jako TestArkuszId, czasy odcinków
     przeskalowane TestArkuszSkala): grają odcinki z katalogu — region każdego odtwarzanego dźwięku = odcinek efektu ×
     skala, pozycja odtwarzania w regionie, a szczyt uderzeń wypada na trafienie (|odchylenie| ≤ 0,1 s przy ×1)
  D4 po zabraniu identyfikatora próbnego następna walka znów na arkuszu z katalogu — te same trzy stany co D2
  D5 muzyka stref: strefa liczona z położenia (bazar / las-pas, gdy stoją ich mapy); w każdej strefie stan wypisany:
     katalog bez identyfikatora → cisza; z identyfikatorem → wybrany utwór strefy, a gra tylko wtedy, gdy plik się
     wczytał (niewczytany: nie gra i nie liczy się jako błąd); z identyfikatorem próbnym gra i w walce cichnie do
     przyciszenia z katalogu; po zabraniu próbnego — wraca do stanu z katalogu (jak wyżej)
  D6 konsola bez błędów [DzwiekGra] i [TestWalki2]
  D7 strefa z utworami zastępczymi (Bagno, strefa wymuszona haczykiem): stan z katalogu (własne utwory, gdy mają
     identyfikator, inaczej zastępcze); własny utwór „bez identyfikatora” (próbny identyfikator 0) → grają zastępcze
     (utwory lasu); własny utwór z identyfikatorem próbnym → gra własny, nie zastępcze, z głośnością strefy; po
     zabraniu próbnego wraca stan z katalogu
  D8 utwór jako odcinek pliku (jak utwory z arkusza muzyki; próbny plik, odcinek 2,0–8,0 s w strefie Dżungla): Sound
     ma PlaybackRegion = odcinek, pozycja odtwarzania zostaje w odcinku, a pod koniec odcinka utwór przechodzi
     w następny (tu: w siebie) — licznik zmian rośnie
  D9 muzyka kontekstu walki (próbne odcinki dla „walka” i „walka_straznik”, strefa bazar z próbnym plikiem):
     zwykła walka z tablicy → kontekst „walka” i utwór walki; okno wyniku → muzyka walki przyciszona; po zamknięciu
     wraca muzyka strefy; walka ze Strażnikiem Gaju → kontekst „walka_straznik” i utwór Strażnika; Strażnik bez
     własnego utworu → utwór zwykłej walki; bez żadnego utworu kontekstu → zostaje muzyka strefy
  D10 muzyka mini-gry: atrybut gracza z katalogu (TreningGra, tu ustawiony próbą po stronie serwera — tak jak robi to
     serwer mini-gier przy wejściu na stanowisko) → kontekst „trening” i utwór treningu; po zdjęciu atrybutu wraca
     muzyka strefy i gra dalej od miejsca, w którym ucichła (licznik wznowień rośnie)
  D11 plik niewczytany (gra bez prawa do zasobu, moderacja): własny utwór strefy z identyfikatorem, którego plik się
     nie wczyta (próbny adres bez pliku) → grają zastępcze, nie cisza; po podstawieniu pliku, który się wczytuje →
     własny utwór; kontekst z niewczytanym plikiem → zostaje muzyka strefy; prawdziwe pliki Bagna i Dżungli —
     co zwraca klient (IsLoaded, TimeLength, ContentProvider:PreloadAsync) i czy strefa gra wtedy własne albo zastępcze
Punkty D7–D11 biegną przed D6 (konsola na końcu). Wynik: <wyj>/wyniki.json i lista na ekranie (nazwa konta
w konsoli zastąpiona znacznikiem <gracz>).
"""
import json
import os
import re
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TU)))
sys.path.insert(0, os.path.join(REPO, "swiat", "test_walki2", "testy"))
from sesja_play import SesjaPlay, log  # noqa: E402
sys.path.insert(0, os.path.dirname(TU))
import zbuduj as ZB  # noqa: E402  (katalog muzyki do oczekiwań D7–D10: te same dane co w Studio)

with open(os.path.join(os.path.dirname(TU), "ustawienia.json"), encoding="utf-8") as _f:
    # przyciszenie muzyki w walce bierzemy z ustawień pakietu (17.11.2026: 0,6 zamiast 0,25) — próg nie jest wpisany na sztywno
    PRZYCISZENIE_WALKI = float(json.load(_f)["muzyka"]["przyciszenie_walki"])

PROBNY = "rbxasset://sounds/action_falling.mp3"  # wbudowany w klienta (ok. 10 s szumu wiatru) — nie upload
NIEWCZYTYWALNY = "rbxasset://sounds/proba_dzwiek_gra_nie_ma_takiego_pliku.mp3"  # adres bez pliku: dźwięk się nie wczyta
WALKA = ("wojownik", "cierniowy_wilk", 5, 1)       # krytyk Wojownika, ciosy i bloki; ok. 20 s przy ×1
LISTA = []
WYNIKI = {}


def punkt(kod, ok, opis):
    LISTA.append((kod, "OK" if ok else "BŁĄD", opis))
    log("%s %s — %s" % (kod, LISTA[-1][1], opis))


def id_arkusza(kat_src):
    """Identyfikator arkusza w zbudowanym katalogu (zrodla/KatalogDzwiekow.luau): 0 = jeszcze nie wgrany."""
    m = re.search(r"arkusz = \{\s*id = (\d+)", kat_src)
    return int(m.group(1)) if m else 0


def id_stref(kat_src):
    """strefa muzyki → lista identyfikatorów utworów z katalogu (0 = utwór niewgrany)."""
    wynik = {}
    czesc = kat_src.split("strefy = {", 1)[1] if "strefy = {" in kat_src else ""
    for m in re.finditer(r"\n\t\t\t(\w+) = \{(.*?)\n\t\t\t\},", czesc, re.S):
        wynik[m.group(1)] = [int(x) for x in re.findall(r"\bid = (\d+)", m.group(2))]
    return wynik


def ocen_arkusz(w, ident):
    """D2 / D4: walka na arkuszu z katalogu → (ok, stan). Nigdy cisza: zawsze zagrane > 0."""
    zagrane = w.get("zagrane") or 0
    if not ident:
        return (w["zestaw"] == "wbudowany" and zagrane > 0 and not w["odcinki"] and not w["probki"],
                "katalog bez identyfikatora arkusza → dźwięki wbudowane")
    if w["odcinki"]:
        return (w["zestaw"] == "arkusz" and zagrane > 0, "arkusz wczytany → grają odcinki arkusza")
    return (w["zestaw"] == "arkusz" and (w.get("niewczytane") or 0) > 0 and zagrane > 0 and not w["probki"],
            "arkusz niewczytany (gra nie ma jeszcze prawa do zasobu?) → grały dźwięki wbudowane")


def ocen_strefe(st, strefa, idy):
    """D5: stan muzyki w strefie wg katalogu → (ok, opis stanu)."""
    if st.get("strefa") != strefa:
        return False, "strefa %s zamiast %s" % (st.get("strefa"), strefa)
    if not any(idy):
        return not st.get("gra"), "bez identyfikatora → cisza"
    if st.get("wczytany"):
        return bool(st.get("utwor")) and bool(st.get("gra")), "utwór %s wczytany → gra" % st.get("utwor")
    return bool(st.get("utwor")), "utwór %s niewczytany → nie gra (bez prawa do zasobu?)" % st.get("utwor")


def main():
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    os.makedirs(wyj, exist_ok=True)
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    kat_src = open(os.path.join(REPO, "swiat", "dzwiek_gra", "zrodla", "KatalogDzwiekow.luau"), encoding="utf-8").read()
    mapa = json.load(open(os.path.join(REPO, "assets", "audio", "arkusz", "sfx_arkusz_a.json"), encoding="utf-8"))
    skala = round(9.5 / mapa["dlugosc_s"], 4)

    with SesjaPlay(studio) as s:
        H = 'local H = game:GetService("HttpService") local D = workspace:FindFirstChild("DzwiekGra") '

        def js(kod, dm="Client"):
            return json.loads(s.luau(H + kod, dm))

        s.przy_tablicy()
        s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", true) return "ok"', "Server")
        # D1
        d1 = js('local x = Instance.new("Sound") local ok, b = pcall(function() x.PlaybackRegionsEnabled = true '
                'x.PlaybackRegion = NumberRange.new(1.5, 2.5) return x.PlaybackRegion end) local r = ok and { b.Min, b.Max } '
                'x:Destroy() return H:JSONEncode({ ok = ok, region = r, blad = (not ok) and tostring(b) or nil })')
        WYNIKI["D1"] = d1
        punkt("D1", d1.get("ok") and d1.get("region") == [1.5, 2.5], "PlaybackRegion: %s" % d1)

        def walka(etykieta, przeciwnik=None, tempo=1):
            klasa, wrog, poz, z = WALKA
            wrog = przeciwnik or wrog
            s.steruj('"zamknij"')
            time.sleep(0.8)
            s.ziarno(z)
            s.steruj('"start", { klasa = "%s", przeciwnik = "%s", poziom = "%d" }, { tempo = %d }' % (klasa, wrog, poz, tempo))
            s.czekaj(("odtwarzanie",), 15)
            probki, przyciszenia = [], []
            t0 = time.time()
            while time.time() - t0 < 90:
                r = js('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("TestWalki2Cutscenka") '
                       'local o = {} if g then for _, x in g:GetChildren() do if x:IsA("Sound") and string.sub(x.Name, 1, 6) == "Arkusz" '
                       'and x.IsPlaying then table.insert(o, { x.Name, x.PlaybackRegion.Min, x.PlaybackRegion.Max, x.TimePosition, '
                       'x.PlaybackRegionsEnabled, x.SoundId }) end end end '
                       'local m = D and D.Sygnaly.SterowanieMuzyki:Invoke("stan") '
                       'return H:JSONEncode({ graja = o, stan = workspace.TestWalki2:GetAttribute("OstatniStan"), '
                       'muzyka = m and { gra = m.gra, przyciszenie = m.przyciszenie, walka = m.walka, kontekst = m.kontekst, '
                       'utwor = m.utwor, region = m.region, pozycja = m.pozycja, pk = m.przyciszenieKontekstu, '
                       'wk = m.walkaKontekst, faza = m.walkaFaza, wczytany = m.wczytany } })')
                probki.extend(r["graja"])
                if r.get("muzyka"):
                    przyciszenia.append(r["muzyka"])
                if r.get("stan") == "wynik":
                    break
                time.sleep(0.12)
            st = s.stan()
            w = {"zestaw": st.get("OstatniZestawDzwiekow"), "zagrane": st.get("OstatnieDzwiekiZagrane"),
                 "niewczytane": st.get("OstatniArkuszNiewczytany"),
                 "odcinki": json.loads(st.get("OstatnieOdcinkiArkusza") or "[]"), "regiony": st.get("OstatnieRegionyArkusza"),
                 "probki": probki[:80], "muzyka": przyciszenia[-40:], "muzyka_wszystko": przyciszenia[:400],
                 "czas": st.get("OstatniCzasTrwania")}
            WYNIKI[etykieta] = w
            return w

        # D2 — arkusz z katalogu (id 0 / wczytany / niewczytany)
        ident = id_arkusza(kat_src)
        w2 = walka("D2")
        ok2, stan2 = ocen_arkusz(w2, ident)
        WYNIKI["D2_stan"] = stan2
        punkt("D2", ok2, "%s: zestaw %s, zagrane %s, odcinków arkusza %d, niewczytany %s" % (
            stan2, w2["zestaw"], w2["zagrane"], len(w2["odcinki"]), w2.get("niewczytane")))
        # D3 — arkusz próbny
        s.luau('local D = workspace.DzwiekGra D:SetAttribute("TestArkuszId", "%s") D:SetAttribute("TestArkuszSkala", %s) return "ok"'
               % (PROBNY, skala))
        w3 = walka("D3")
        efekty = mapa["efekty"]
        zle = []
        for o in w3["odcinki"]:
            e = efekty.get(o["e"])
            if not e:
                zle.append("nieznany efekt %s" % o["e"])
                continue
            if abs(o["p1"] - e["koniec"] * skala) > 0.002 or abs(o["p0"] - (e["poczatek"] + o["od"]) * skala) > 0.002:
                zle.append("%s: region %s–%s ≠ katalog × skala" % (o["e"], o["p0"], o["p1"]))
        for p in w3["probki"]:
            nazwa, a, b, pos, wl, sid = p
            if sid != PROBNY or not wl or not (a - 0.05 <= pos <= b + 0.05):
                zle.append("%s: pozycja %.3f poza regionem %.3f–%.3f (%s, %s)" % (nazwa, pos, a, b, wl, sid))
        uderzenia = [o for o in w3["odcinki"] if o.get("dSzczyt") is not None]
        zle_szczyt = [o for o in uderzenia if abs(o["dSzczyt"]) > 0.1]
        WYNIKI["D3_podsumowanie"] = {"odcinkow": len(w3["odcinki"]), "uderzen": len(uderzenia), "probek": len(w3["probki"]),
                                     "zle": zle[:10], "zle_szczyt": zle_szczyt[:10],
                                     "efekty": sorted({o["e"] for o in w3["odcinki"]})}
        punkt("D3", w3["zestaw"] == "arkusz" and w3["regiony"] is True and len(w3["odcinki"]) > 3 and len(w3["probki"]) > 0
              and not zle and uderzenia and not zle_szczyt,
              "odcinków %d (efekty %s), uderzeń ze szczytem %d (odchylenia %s), próbek odtwarzania %d, błędów %d %s"
              % (len(w3["odcinki"]), WYNIKI["D3_podsumowanie"]["efekty"], len(uderzenia),
                 [o["dSzczyt"] for o in uderzenia][:12], len(w3["probki"]), len(zle), (zle + zle_szczyt)[:3]))
        # D4 — bez identyfikatora
        s.luau('local D = workspace.DzwiekGra D:SetAttribute("TestArkuszId", nil) D:SetAttribute("TestArkuszSkala", nil) return "ok"')
        w4 = walka("D4")
        ok4, stan4 = ocen_arkusz(w4, ident)
        WYNIKI["D4_stan"] = stan4
        punkt("D4", ok4, "po zabraniu próbnego — %s: zestaw %s, zagrane %s, odcinków %d, niewczytany %s" % (
            stan4, w4["zestaw"], w4["zagrane"], len(w4["odcinki"]), w4.get("niewczytane")))
        # D5 — muzyka stref
        strefy_kat = id_stref(kat_src)
        STAN_MUZYKI = ('local s = D.Sygnaly.SterowanieMuzyki:Invoke("stan") local wcz = false '
                       'for _, x in D:GetDescendants() do if x:IsA("Sound") and s.id and x.SoundId == s.id and x.IsLoaded '
                       'and x.TimeLength > 0 then wcz = true end end s.wczytany = wcz return H:JSONEncode(s)')
        m = {}
        m["tablica"] = js('return H:JSONEncode(D.Sygnaly.SterowanieMuzyki:Invoke("stan"))')
        strefy = js('local o = {} for _, n in { "MiasteczkoBazar", "LasPas" } do o[n] = workspace:FindFirstChild(n) ~= nil end '
                    'return H:JSONEncode(o)')
        m["mapy"] = strefy
        polozenia = {"bazar": (990, 3.5, -697), "las": (1300, 3.5, -700)}
        for nazwa, (x, y, zz) in polozenia.items():
            s.luau('local p = game:GetService("Players"):GetPlayers()[1] p.Character:PivotTo(CFrame.new(%f, %f, %f)) return "ok"'
                   % (x, y, zz), "Server")
            time.sleep(4.0)  # przejście utworu + czas na wczytanie pliku
            m[nazwa] = js(STAN_MUZYKI)
        s.przy_tablicy()
        s.steruj('"zamknij"')         # okno wyniku poprzedniej walki to jeszcze walka (muzyka przyciszona)
        time.sleep(1.0)
        js('D.Sygnaly.SterowanieMuzyki:Invoke("probny", "bazar", "%s") D.Sygnaly.SterowanieMuzyki:Invoke("wymus", "bazar") '
           'return H:JSONEncode({})' % PROBNY)
        time.sleep(4.0)
        m["probny"] = js('return H:JSONEncode(D.Sygnaly.SterowanieMuzyki:Invoke("stan"))')
        w5 = walka("D5_walka")
        pr = [x["przyciszenie"] for x in w5["muzyka"] if x.get("walka")]
        m["przyciszenie_w_walce"] = min(pr) if pr else None
        s.steruj('"zamknij"')
        js('D.Sygnaly.SterowanieMuzyki:Invoke("probny", "bazar", nil) D.Sygnaly.SterowanieMuzyki:Invoke("wymus", nil) return H:JSONEncode({})')
        time.sleep(4.0)
        m["po"] = js(STAN_MUZYKI)
        WYNIKI["D5"] = m
        oczek_strefy = [n for n, k in (("bazar", "MiasteczkoBazar"), ("las", "LasPas")) if strefy.get(k)]
        oceny = {n: ocen_strefe(m[n], n, strefy_kat.get(n, [])) for n in oczek_strefy}
        # po zabraniu próbnego: wymuszenie zdjęte, gracz przy tablicy (poza strefami) → cisza; gdyby strefa została
        # bazarem, oceniamy ją jak wyżej (stan z katalogu)
        if m["po"].get("strefa") in strefy_kat:
            ok_po, stan_po = ocen_strefe(m["po"], m["po"]["strefa"], strefy_kat[m["po"]["strefa"]])
        else:
            ok_po, stan_po = not m["po"].get("gra"), "poza strefami → cisza"
        WYNIKI["D5_stany"] = {n: o[1] for n, o in oceny.items()}
        WYNIKI["D5_stany"]["po"] = stan_po
        ok5 = (not m["tablica"].get("gra") and all(o[0] for o in oceny.values())
               and m["probny"].get("gra") and (m["probny"].get("glosnosc") or 0) > 0.2
               and m["przyciszenie_w_walce"] is not None and m["przyciszenie_w_walce"] <= PRZYCISZENIE_WALKI + 0.05
               and m["przyciszenie_w_walce"] < 0.95 and ok_po
               and (m["po"].get("bledy") or 0) == 0)
        punkt("D5", ok5, "tablica %s; strefy %s; próbny %s; przyciszenie w walce %s; po zabraniu: %s %s" % (
            {k: m["tablica"].get(k) for k in ("strefa", "gra")},
            {n: o[1] for n, o in oceny.items()}, {k: m["probny"].get(k) for k in ("utwor", "gra", "glosnosc")},
            m["przyciszenie_w_walce"], stan_po, {k: m["po"].get(k) for k in ("strefa", "gra", "bledy")}))
        # ---------------------------------------------------------------- D7–D10: zastępcze, odcinki, konteksty
        MUZ = "D.Sygnaly.SterowanieMuzyki"
        KAT = ZB.katalog(ZB.wczytaj_json(ZB.USTAWIENIA), ZB.wczytaj_json(ZB.IDENTYFIKATORY))["muzyka"]

        def muz(argumenty):
            """SterowanieMuzyki:Invoke(…) u klienta; argumenty = tekst argumentów Luau."""
            return js('local w = %s:Invoke(%s) return H:JSONEncode({ ok = true, w = w })' % (MUZ, argumenty)).get("w")

        def stan_muzyki():
            return js('return H:JSONEncode(%s:Invoke("stan"))' % MUZ)

        def czekaj_na(warunek, limit, co=0.25):
            """Odpytuje stan muzyki, aż warunek(stan) będzie prawdą albo minie limit; zwraca ostatni stan."""
            t0 = time.time()
            st = stan_muzyki()
            while not warunek(st) and time.time() - t0 < limit:
                time.sleep(co)
                st = stan_muzyki()
            return st

        def proba(kod, opis, funkcja):
            try:
                ok, tekst = funkcja()
            except Exception as e:  # noqa: BLE001 — punkt nie może zatrzymać pozostałych ani D6
                ok, tekst = False, "wyjątek: %s" % str(e)[:300]
            punkt(kod, ok, "%s — %s" % (opis, tekst))

        def nazwy(utwory):
            return [u["nazwa"] for u in utwory if u["id"]]

        def stan_plikow(idy):
            """Co klient mówi o plikach audio: dźwięk „Wczytanie” skryptu muzyki (IsLoaded, TimeLength) i wynik
            ContentProvider:PreloadAsync na osobnym, niepodpiętym dźwięku (tylko odczyt, nic nie zostaje w miejscu)."""
            if not idy:
                return {}
            lista = js('local CP = game:GetService("ContentProvider") local o = {} '
                       'for _, id in { %s } do local adres = "rbxassetid://" .. id local w = { id = id } '
                       'local s, wlasny = nil, false '
                       'for _, x in D.MuzykaLokalna:GetChildren() do if x:IsA("Sound") and x.Name == "Wczytanie" '
                       'and x.SoundId == adres then s = x w.wczytanie = { IsLoaded = x.IsLoaded, TimeLength = x.TimeLength } end end '
                       'if not s then s = Instance.new("Sound") s.SoundId = adres wlasny = true end '
                       'local ok, blad = pcall(function() CP:PreloadAsync({ s }, function(_, status) w.status = status.Name end) end) '
                       'if not ok then w.blad = tostring(blad) end '
                       'w.poPreload = { IsLoaded = s.IsLoaded, TimeLength = s.TimeLength, osobnyDzwiek = wlasny } '
                       'if wlasny then s:Destroy() end table.insert(o, w) end '
                       'return H:JSONEncode(o)' % ", ".join('"%d"' % i for i in idy))
            return {int(w["id"]): w for w in lista}

        def wczytane(utwory, pliki):
            """Nazwy utworów z identyfikatorem, których plik skrypt muzyki ma wczytany."""
            return [u["nazwa"] for u in utwory if u["id"] and (pliki.get(u["id"], {}).get("wczytanie") or {}).get("IsLoaded")
                    and (pliki[u["id"]]["wczytanie"].get("TimeLength") or 0) > 0]

        def opis_plikow(utwory, pliki):
            return "; ".join("%s: skrypt muzyki IsLoaded=%s TimeLength=%s, PreloadAsync=%s" % (
                u["nazwa"], (pliki.get(u["id"], {}).get("wczytanie") or {}).get("IsLoaded"),
                (pliki.get(u["id"], {}).get("wczytanie") or {}).get("TimeLength"),
                pliki.get(u["id"], {}).get("status") or pliki.get(u["id"], {}).get("blad")) for u in utwory if u["id"]) or "brak identyfikatorów"

        def ocen_strefe_z_zastepczymi(st, strefa, pliki):
            """Strefa z utworami zastępczymi: własne wczytane → własne; inaczej zastępcze (nigdy cisza z braku pliku)."""
            sk = KAT["strefy"][strefa]
            gotowe, zast = wczytane(sk["utwory"], pliki), nazwy(sk["zastepcze"]["utwory"])
            if st.get("strefa") != strefa:
                return False
            if gotowe:
                return st.get("utwor") in gotowe and not st.get("zastepcze")
            if zast:
                return st.get("utwor") in zast and st.get("zastepcze") is True
            return True

        def d7():
            sb = KAT["strefy"]["bagno"]
            wlasne, zast = nazwy(sb["utwory"]), nazwy(sb["zastepcze"]["utwory"])
            pliki = stan_plikow([u["id"] for u in sb["utwory"] if u["id"]])

            def wg_katalogu(st):
                return ocen_strefe_z_zastepczymi(st, "bagno", pliki)

            muz('"probny", "bagno", nil')
            muz('"wymus", "bagno"')
            time.sleep(4.0)
            a = stan_muzyki()
            # własny utwór „bez identyfikatora” (próbny identyfikator 0) → grają zastępcze, także gdy katalog ma już własne
            muz('"probny", "bagno", 0')
            time.sleep(3.0)
            z = stan_muzyki()
            muz('"probny", "bagno", "%s"' % PROBNY)
            time.sleep(4.0)
            b = stan_muzyki()
            muz('"probny", "bagno", nil')
            time.sleep(2.0)
            c = stan_muzyki()
            WYNIKI["D7"] = {"wlasne_w_katalogu": wlasne, "zastepcze_w_katalogu": zast, "pliki_wlasne": pliki, "katalog": a,
                            "bez_wlasnych": z, "probny": b, "po": c}
            ok_z = (z.get("utwor") in zast and z.get("zastepcze") is True) if zast else not z.get("gra")
            ok_b = (b.get("utwor") == sb["utwory"][0]["nazwa"] and not b.get("zastepcze") and b.get("gra")
                    and b.get("id") == PROBNY and abs((b.get("glosnosc") or 0) - sb["glosnosc"]) < 0.08)
            return (wg_katalogu(a) and ok_z and ok_b and wg_katalogu(c) and (c.get("bledy") or 0) == 0,
                    "katalog: własne %s, zastępcze %s → gra %s (zastępcze: %s); własny bez identyfikatora → %s (zastępcze: %s); "
                    "z próbnym: %s, głośność %s; po zabraniu: %s (zastępcze: %s)"
                    % (wlasne, zast, a.get("utwor"), a.get("zastepcze"), z.get("utwor"), z.get("zastepcze"), b.get("utwor"),
                       b.get("glosnosc"), c.get("utwor"), c.get("zastepcze")))

        def d8():
            pierwszy = KAT["strefy"]["dzungla"]["utwory"][0]["nazwa"]
            muz('"probny", "bagno", nil')
            muz('"probny", "dzungla", "%s", { poczatek = 2.0, koniec = 8.0 }' % PROBNY)
            muz('"wymus", "dzungla"')
            probki, t0 = [], time.time()
            while time.time() - t0 < 10.0:
                st = stan_muzyki()
                st["_t"] = round(time.time() - t0, 2)
                probki.append(st)
                time.sleep(0.2)
            muz('"probny", "dzungla", nil')
            swoje = [x for x in probki if x.get("utwor") == pierwszy and x.get("gra") and x.get("wczytany")]
            poza = [x for x in swoje if x.get("region") != [2, 8] or not (1.7 <= (x.get("pozycja") or 0) <= 8.3)]
            pozniej = [x for x in probki if x["_t"] >= 1.5]
            zmiany = (pozniej[-1].get("zmiany", 0) - pozniej[0].get("zmiany", 0)) if pozniej else 0
            najdalej = max([x.get("pozycja") or 0 for x in swoje] or [0])
            WYNIKI["D8"] = {"probek": len(probki), "swoje": len(swoje), "poza": poza[:5], "zmiany": zmiany, "najdalej": najdalej,
                            "korekty": probki[-1].get("korekty"), "probki": [
                                {k: x.get(k) for k in ("_t", "utwor", "pozycja", "region", "zmiany", "glosnosc", "korekty")}
                                for x in probki[:60]]}
            return (len(swoje) >= 5 and not poza and zmiany >= 1 and najdalej > 3.5 and (probki[-1].get("bledy") or 0) == 0,
                    "próbek z utworem %s: %d, poza odcinkiem 2–8 s: %d, najdalsza pozycja %.2f s, zmian utworu po 1,5 s: %d, "
                    "korekt pozycji: %s" % (pierwszy, len(swoje), len(poza), najdalej, zmiany, probki[-1].get("korekty")))

        def d9():
            bazar = KAT["strefy"]["bazar"]["utwory"][0]["nazwa"]
            u_walka = KAT["konteksty"]["walka"]["utwory"][0]["nazwa"]
            u_straznik = KAT["konteksty"]["walka_straznik"]["utwory"][0]["nazwa"]
            muz('"probny", "bazar", "%s"' % PROBNY)
            muz('"wymus", "bazar"')
            muz('"probny", "walka", "%s", { poczatek = 2.0, koniec = 8.0 }' % PROBNY)
            muz('"probny", "walka_straznik", "%s", { poczatek = 1.0, koniec = 9.0 }' % PROBNY)
            time.sleep(3.5)
            przed = stan_muzyki()

            def w_walce(w, kontekst, utwor, region):
                """Próbki z czasu odtwarzania walki: (ile z oczekiwanym kontekstem i utworem, ile z innym kontekstem)."""
                odtw = [x for x in w["muzyka_wszystko"] if x.get("faza") == "odtwarzanie"]
                dobre = [x for x in odtw if x.get("kontekst") == kontekst and x.get("utwor") == utwor
                         and x.get("region") == region and x.get("wk") == kontekst]
                inne = [x for x in odtw if x.get("kontekst") not in (None, kontekst)]
                return len(odtw), len(dobre), len(inne), min([x.get("pk", 1) for x in dobre] or [0])

            wa = walka("D9_walka")
            a = w_walce(wa, "walka", u_walka, [2, 8])
            wynik = czekaj_na(lambda st: st.get("walkaFaza") == "wynik" and (st.get("przyciszenieKontekstu") or 1) <= PRZYCISZENIE_WALKI + 0.05, 4.0)
            s.steruj('"zamknij"')
            po = czekaj_na(lambda st: st.get("kontekst") is None and st.get("utwor") == bazar and not st.get("walka"), 5.0)
            wb = walka("D9_straznik", przeciwnik="straznik_lasu", tempo=4)
            b = w_walce(wb, "walka_straznik", u_straznik, [1, 9])
            s.steruj('"zamknij"')
            time.sleep(1.0)
            # Strażnik bez własnego utworu → utwór zwykłej walki; bez żadnego utworu kontekstu → muzyka strefy
            muz('"probny", "walka_straznik", nil')
            muz('"wymus_kontekst", "walka_straznik"')
            c = czekaj_na(lambda st: st.get("kontekst") == "walka" and st.get("utwor") == u_walka, 5.0)
            muz('"probny", "walka", nil')
            bez_id = not any(u["id"] for k in ("walka", "walka_straznik") for u in KAT["konteksty"][k]["utwory"])
            d = czekaj_na(lambda st: st.get("kontekst") is None and st.get("utwor") == bazar, 5.0)
            muz('"wymus_kontekst", nil')
            WYNIKI["D9"] = {"przed": przed, "walka": a, "wynik": wynik, "po": po, "straznik": b, "straznik_bez_utworu": c,
                            "bez_utworow": d, "katalog_bez_id_kontekstow": bez_id}
            ok = (przed.get("utwor") == bazar and przed.get("gra") and przed.get("kontekst") is None
                  and a[1] >= 3 and a[2] == 0 and a[3] > 0.95
                  and wynik.get("walkaFaza") == "wynik" and (wynik.get("przyciszenieKontekstu") or 1) <= PRZYCISZENIE_WALKI + 0.05
                  and po.get("kontekst") is None and po.get("utwor") == bazar
                  and b[1] >= 3 and b[2] == 0
                  and c.get("kontekst") == "walka" and c.get("utwor") == u_walka
                  and (not bez_id or (d.get("kontekst") is None and d.get("utwor") == bazar))
                  and (d.get("bledy") or 0) == 0)
            return ok, ("zwykła walka: próbek odtwarzania %d, z kontekstem „walka” i utworem %s: %d, z innym kontekstem: %d; "
                        "okno wyniku: przyciszenie muzyki walki %s; po zamknięciu: kontekst %s, utwór %s; Strażnik: próbek %d, "
                        "z kontekstem „walka_straznik” i utworem %s: %d, z innym: %d; Strażnik bez utworu → kontekst %s, utwór %s; "
                        "bez utworów kontekstu → kontekst %s, utwór %s"
                        % (a[0], u_walka, a[1], a[2], wynik.get("przyciszenieKontekstu"), po.get("kontekst"), po.get("utwor"),
                           b[0], u_straznik, b[1], b[2], c.get("kontekst"), c.get("utwor"), d.get("kontekst"), d.get("utwor")))

        def d10():
            bazar = KAT["strefy"]["bazar"]["utwory"][0]["nazwa"]
            u_trening = KAT["konteksty"]["trening"]["utwory"][0]["nazwa"]
            atrybut = KAT["konteksty"]["trening"]["atrybutGracza"]
            ustaw = 'game:GetService("Players"):GetPlayers()[1]:SetAttribute("%s", %%s) return "ok"' % atrybut
            muz('"probny", "trening", "%s"' % PROBNY)
            muz('"probny", "bazar", "%s"' % PROBNY)
            muz('"wymus", "bazar"')            # utwór strefy od początku — znana pozycja
            time.sleep(2.0)
            a = stan_muzyki()
            s.luau(ustaw % '"proba_muzyki"', "Server")
            try:
                b = czekaj_na(lambda st: st.get("kontekst") == "trening" and st.get("utwor") == u_trening and st.get("gra"), 4.0)
                time.sleep(3.5)                 # strefa zdąży ucichnąć i zostać wstrzymana
            finally:
                s.luau(ustaw % "nil", "Server")
            c = czekaj_na(lambda st: st.get("kontekst") is None and st.get("utwor") == bazar, 4.0)
            muz('"probny", "trening", nil')
            muz('"probny", "bazar", nil')
            muz('"wymus", nil')
            time.sleep(1.0)
            k = stan_muzyki()
            WYNIKI["D10"] = {"przed": a, "w_mini_grze": b, "po": c, "koniec": k}
            wznowien = (c.get("wznowienia") or 0) - (a.get("wznowienia") or 0)
            ok = (a.get("utwor") == bazar and a.get("gra") and b.get("kontekst") == "trening" and b.get("utwor") == u_trening
                  and b.get("gra") and c.get("kontekst") is None and c.get("utwor") == bazar and wznowien == 1
                  and (c.get("pozycja") or 0) > (a.get("pozycja") or 0) + 0.5 and (k.get("bledy") or 0) == 0)
            return ok, ("przed: utwór %s na pozycji %s s; z atrybutem %s: kontekst %s, utwór %s; po zdjęciu: kontekst %s, utwór %s "
                        "na pozycji %s s, wznowień %d" % (a.get("utwor"), a.get("pozycja"), atrybut, b.get("kontekst"), b.get("utwor"),
                                                          c.get("kontekst"), c.get("utwor"), c.get("pozycja"), wznowien))

        def d11():
            sb = KAT["strefy"]["bagno"]
            pierwszy, zast = sb["utwory"][0]["nazwa"], nazwy(sb["zastepcze"]["utwory"])
            bazar = KAT["strefy"]["bazar"]["utwory"][0]["nazwa"]
            # a) własny utwór ma identyfikator, ale plik się nie wczyta → zastępcze (nie cisza)
            muz('"probny", "bagno", "%s"' % NIEWCZYTYWALNY)
            muz('"wymus", "bagno"')
            time.sleep(4.0)
            a = stan_muzyki()
            ok_a = (a.get("utwor") in zast and a.get("zastepcze") is True) if zast else True
            # b) plik zaczyna się wczytywać → strefa przechodzi na własny utwór
            muz('"probny", "bagno", "%s"' % PROBNY)
            b = czekaj_na(lambda st: st.get("utwor") == pierwszy and not st.get("zastepcze") and st.get("gra"), 6.0)
            ok_b = b.get("utwor") == pierwszy and not b.get("zastepcze") and bool(b.get("gra"))
            # c) kontekst z identyfikatorem, którego plik się nie wczyta → zostaje muzyka strefy
            muz('"probny", "bagno", nil')
            muz('"probny", "bazar", "%s"' % PROBNY)
            muz('"wymus", "bazar"')
            muz('"probny", "walka", "%s"' % NIEWCZYTYWALNY)
            time.sleep(3.0)
            muz('"wymus_kontekst", "walka"')
            time.sleep(3.0)
            c = stan_muzyki()
            ok_c = c.get("kontekst") is None and c.get("utwor") == bazar and bool(c.get("gra"))
            muz('"wymus_kontekst", nil')
            muz('"probny", "walka", nil')
            muz('"probny", "bazar", nil')
            # d) prawdziwe pliki Bagna i Dżungli: co zwraca Studio i co gra strefa (stojąc w niej, gdy stoi jej mapa)
            krainy, ok_d, opisy = {}, True, []
            for strefa in ("bagno", "dzungla"):
                sk = KAT["strefy"][strefa]
                pl = stan_plikow([u["id"] for u in sk["utwory"] if u["id"]])
                pl_z = stan_plikow([u["id"] for u in sk["zastepcze"]["utwory"] if u["id"]])
                r = sk["prostokaty"][0] if sk["prostokaty"] else None
                stoi = bool(sk.get("kontener")) and js('return H:JSONEncode({ jest = workspace:FindFirstChild("%s") ~= nil })'
                                                       % sk.get("kontener")).get("jest")
                # stajemy w strefie, gdy stoi jej mapa; serwer krainy może cofnąć postać (np. zamknięta brama do Bagna) —
                # wtedy strefę wymuszamy haczykiem (wybór utworów jest ten sam, nie zależy od sposobu wejścia do strefy)
                jak = "strefa wymuszona, mapa nie stoi"
                na_miejscu = False
                if stoi and r:
                    muz('"wymus", nil')
                    s.luau('local p = game:GetService("Players"):GetPlayers()[1] p.Character:PivotTo(CFrame.new(%f, 14, %f)) return "ok"'
                           % ((r[0] + r[1]) / 2, (r[2] + r[3]) / 2), "Server")
                    time.sleep(2.5)
                    poz = js('local c = game:GetService("Players").LocalPlayer.Character local h = c and c:FindFirstChild("HumanoidRootPart") '
                             'return H:JSONEncode(h and { h.Position.X, h.Position.Y, h.Position.Z } or {})')
                    na_miejscu = len(poz) == 3 and r[0] <= poz[0] <= r[1] and r[2] <= poz[2] <= r[3]
                    jak = "postać w strefie" if na_miejscu else "strefa wymuszona — po przeniesieniu postać nie została w strefie (X %s, Z %s)" % (
                        round(poz[0]) if len(poz) == 3 else None, round(poz[2]) if len(poz) == 3 else None)
                if not na_miejscu:
                    muz('"wymus", "%s"' % strefa)
                time.sleep(4.5)
                st = stan_muzyki()
                ok_s = ocen_strefe_z_zastepczymi(st, strefa, pl)
                ok_d = ok_d and ok_s
                krainy[strefa] = {"pliki_wlasne": pl, "pliki_zastepcze": pl_z, "na_miejscu": na_miejscu, "jak": jak, "stan": st, "ok": ok_s}
                opisy.append("%s (%s): własne — %s; gra %s (zastępcze: %s, wczytany: %s, gra: %s)" % (
                    strefa, jak, opis_plikow(sk["utwory"], pl), st.get("utwor"), st.get("zastepcze"), st.get("wczytany"), st.get("gra")))
            muz('"wymus", nil')
            s.przy_tablicy()
            time.sleep(1.0)
            k = stan_muzyki()
            # co konsola Studio mówi o własnych plikach Bagna i Dżungli (wiersze z ich identyfikatorami)
            idy = [str(u["id"]) for n in ("bagno", "dzungla") for u in KAT["strefy"][n]["utwory"] if u["id"]]
            kons = s.call("get_console_output", {}, timeout=60)["text"]
            gracz_ = s.luau('return game:GetService("Players"):GetPlayers()[1].Name', "Server").strip()
            wiersze = []
            for x in kons.splitlines():
                x = x.strip()[:300].replace(gracz_, "<gracz>")
                if any(i in x for i in idy) and x not in wiersze:
                    wiersze.append(x)
            opisy.append("konsola o tych plikach: %s" % (wiersze[:4] or "brak wierszy"))
            WYNIKI["D11"] = {"niewczytany_wlasny": a, "po_wczytaniu": b, "niewczytany_kontekst": c, "krainy": krainy, "koniec": k,
                             "konsola_o_plikach": wiersze[:20]}
            return (ok_a and ok_b and ok_c and ok_d and (k.get("bledy") or 0) == 0,
                    "własny z niewczytanym plikiem → %s (zastępcze: %s); po podstawieniu pliku, który się wczytuje → %s (zastępcze: %s); "
                    "kontekst z niewczytanym plikiem → kontekst %s, gra %s; %s"
                    % (a.get("utwor"), a.get("zastepcze"), b.get("utwor"), b.get("zastepcze"), c.get("kontekst"), c.get("utwor"),
                       " | ".join(opisy)))

        proba("D7", "utwory zastępcze i własne (Bagno)", d7)
        proba("D8", "utwór jako odcinek pliku (PlaybackRegion)", d8)
        proba("D9", "muzyka walki i walki ze Strażnikiem", d9)
        proba("D10", "muzyka mini-gry i wznowienie muzyki strefy", d10)
        proba("D11", "plik niewczytany: zastępcze zamiast ciszy, pliki Bagna i Dżungli", d11)
        try:   # sprzątanie haczyków także po wyjątku w którymś punkcie
            for cel in ("bagno", "dzungla", "bazar", "walka", "walka_straznik", "trening"):
                muz('"probny", "%s", nil' % cel)
            muz('"wymus", nil')
            muz('"wymus_kontekst", nil')
            s.steruj('"zamknij"')
        except Exception as e:  # noqa: BLE001
            log("sprzątanie haczyków muzyki: %s" % str(e)[:200])
        s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", nil) return "ok"', "Server")
        # D6 — konsola
        kons = s.call("get_console_output", {}, timeout=60)["text"]
        imie = s.luau('return game:GetService("Players"):GetPlayers()[1].Name', "Server").strip()
        linie = [x.strip()[:240].replace(imie, "<gracz>") for x in kons.splitlines() if "DzwiekGra" in x or "TestWalki2" in x]
        bledy = [x for x in linie if "rror" in x or "błąd" in x.lower() or "warn" in x.lower()]
        WYNIKI["D6"] = linie[-40:]
        punkt("D6", not bledy, "%d wierszy [DzwiekGra]/[TestWalki2], podejrzanych %d %s" % (len(linie), len(bledy), bledy[:3]))
    WYNIKI["lista"] = LISTA
    WYNIKI["katalog_skrot"] = kat_src.split('skrot = "', 1)[1][:12] if 'skrot = "' in kat_src else None
    with open(os.path.join(wyj, "wyniki.json"), "w", encoding="utf-8") as f:
        json.dump(WYNIKI, f, ensure_ascii=False, indent=1)
    print("\nLISTA KONTROLNA:")
    for x in LISTA:
        print("  %s %-4s %s" % x)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
