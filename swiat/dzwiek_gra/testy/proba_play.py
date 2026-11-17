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
Wynik: <wyj>/wyniki.json i lista na ekranie (nazwa konta w konsoli zastąpiona znacznikiem <gracz>).
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

PROBNY = "rbxasset://sounds/action_falling.mp3"  # wbudowany w klienta (ok. 10 s szumu wiatru) — nie upload
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

        def walka(etykieta):
            klasa, wrog, poz, z = WALKA
            s.steruj('"zamknij"')
            time.sleep(0.8)
            s.ziarno(z)
            s.steruj('"start", { klasa = "%s", przeciwnik = "%s", poziom = "%d" }, { tempo = 1 }' % (klasa, wrog, poz))
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
                       'muzyka = m and { gra = m.gra, przyciszenie = m.przyciszenie, walka = m.walka } })')
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
                 "probki": probki[:80], "muzyka": przyciszenia[-40:], "czas": st.get("OstatniCzasTrwania")}
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
               and m["przyciszenie_w_walce"] is not None and m["przyciszenie_w_walce"] < 0.35 and ok_po
               and (m["po"].get("bledy") or 0) == 0)
        punkt("D5", ok5, "tablica %s; strefy %s; próbny %s; przyciszenie w walce %s; po zabraniu: %s %s" % (
            {k: m["tablica"].get(k) for k in ("strefa", "gra")},
            {n: o[1] for n, o in oceny.items()}, {k: m["probny"].get(k) for k in ("utwor", "gra", "glosnosc")},
            m["przyciszenie_w_walce"], stan_po, {k: m["po"].get(k) for k in ("strefa", "gra", "bledy")}))
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
