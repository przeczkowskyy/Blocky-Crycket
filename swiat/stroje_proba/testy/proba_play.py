#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba ubierania postaci (D-071) w trybie PLAY w Studio — lista S00–S10, wynik w testy/wynik_play.json.

    python -B tools/studio_okno.py --na-wierzch                        # przed próbą (bez okna w tle Studio rysuje 15 kl./s)
    python -B swiat/stroje_proba/testy/proba_play.py                   # zrzuty do swiat/stroje_proba/klatki/
    python -B swiat/stroje_proba/testy/proba_play.py --bez-zrzutow
    python -B swiat/stroje_proba/testy/proba_play.py --tylko S05,S06 --studio <studio_id>

Wymaga: kontener Workspace/StrojeProba (zbuduj.py) i TestWalki2 z haczykiem stroju (zbuduj.py --walka); Studio w trybie
Edit. Play tylko na czas próby (SesjaPlay z swiat/test_walki2/testy/sesja_play.py zatrzymuje go zawsze).
  S00 Edit: kontener i skrót danych = lokalne, Aktorzy w TestWalki2 z haczykiem
  S01 gotowość serwera i klienta, podpowiedź E włączona
  S02 prawdziwe E przy stojaku otwiera okno; X zamyka (kamera wraca)
  S03 prawdziwe kliknięcie „>” w wierszu hełmu → serwer zmienia atrybut (następna opcja slotu), podgląd w nowym stroju
  S04 serwer odrzuca: przedmiot innej klasy, część zbroi, zła klasa, zły slot; za szybko; atrybut bez zmian
  S05 każda klasa: goła, komplet, mieszany i komplety trzech stopni sklepu (leśny, bagienny, Dżungli; 19.11.2026) —
      podgląd ma dokładnie te bryły co dane (liczba, atrybut Stroj), cały podgląd nad oknem; zrzuty
  S06 każdy klip każdej klasy w sześciu strojach klatka po klatce: nic nie odpada (odejście od kości < 0,02),
      nic głębiej pod ziemią niż komplet (0,05; komplety stopni — granice GRANICA_STOPNI jak w test_strojow.py),
      w ostatniej klatce upadku kapelusz i kostur kota na ziemi; zawis ciała
  S07 próba walki (tablica): bohater gracza w walce w stroju z przymierzalni; zrzuty w trzech chwilach
  S08 „Dawny wygląd”: walka z dawnym szablonem (bez atrybutu Stroj na modelu)
  S09 walka w lesie-pasie (jeśli LasPasGra jest w miejscu): bohater w stroju
  S10 konsola bez błędów [StrojeProba]
  S11 okno na małym ekranie (emulacja 667 × 375): tekst ≥ 12 pt; zrzut

Dwa tryby (18.11.2026), próba wybiera sama na starcie Play:
  • bez kowala (brak Workspace/KowalProba albo gracz bez atrybutu KowalDostepne) — wszystko jak dotąd;
  • z kowalem (swiat/kowal_proba: przymierzalnia zakłada tylko posiadane przedmioty i nie ma „Dawnego wyglądu”) —
    przed przebieraniem próba nadaje graczowi wszystkie nieposiadane całe przedmioty haczykiem kowala
    (KowalProba/Sygnaly/SterowanieSerwera, polecenie „daj” — ten sam haczyk co próba kowala K05; reguł gry nie zmienia).
    S03 zaczyna od stroju odniesienia zamiast „dawnego”, a S08 sprawdza, że „Dawnego wyglądu” nie ma: serwer odmawia
    powodem „dawny_niedostepny”, atrybut stroju bez zmian, w oknie nie ma przycisku „Dawny wygląd”.
"""
import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (REPO, os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki2"),
           os.path.join(REPO, "swiat", "test_walki2", "testy"), PAKIET):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import dane as DN  # noqa: E402
import logika_strojow as L  # noqa: E402

KLATKI = os.path.join(PAKIET, "klatki")
WYNIK = os.path.join(TU, "wynik_play.json")
KS = 'local k = workspace:FindFirstChild("StrojeProba") local H = game:GetService("HttpService") '
# stroje „mieszane” do prób (część przedmiotów: widać gołe ciało obok przedmiotów)
MIESZANE = {"wojownik": ["rycerz_helm", "rycerz_buty", "rycerz_miecz", "rycerz_tarcza"],
            "zwiadowca": ["zwiadowca_kaptur", "zwiadowca_rekawice", "zwiadowca_luk"],
            "mag": ["kot_mag_kapelusz", "kot_mag_kostur"]}
PRZECIWNIK = {"wojownik": "cierniowy_wilk", "zwiadowca": "lesny_slime", "mag": "muchomornik"}
# komplety stopni ze sklepu zbrojmistrza (D-106, dane: D["klasy"][k]["stopnie"]) — w S05 i S06 obok dzisiejszych strojów
STOPNIE = ("las", "bagno", "dzungla")
# o ile komplet stopnia może zejść w klipie głębiej pod ziemię niż komplet startowy (stud) — te same granice co
# GRANICA_STOPNI w testy/test_strojow.py (stan z 19.11.2026 z zapasem; długie łuki i ozdoby, poprawki w stopnie.py);
# dzisiejsze stroje: 0,05
GRANICA_STOPNI = {"wojownik": {"las": 0.09, "bagno": 0.19, "dzungla": 0.03},
                  "zwiadowca": {"las": 0.17, "bagno": 0.23, "dzungla": 0.55},
                  "mag": {"las": 0.04, "bagno": 0.02, "dzungla": 0.02}}
# tryb z kowalem (swiat/kowal_proba): odczyt i nadanie przedmiotów jego haczykiem testowym (tylko w Play)
KW = ('local kw = workspace:FindFirstChild("KowalProba") local H = game:GetService("HttpService") '
      'local g = game:GetService("Players"):GetPlayers()[1] ')
KOD_TRYB = KW + ('return H:JSONEncode({ jest = kw ~= nil, kowal = kw ~= nil and g ~= nil and '
                 'type(g:GetAttribute("KowalDostepne")) == "string", dostepne = g and g:GetAttribute("KowalDostepne") })')
KOD_DAJ = KW + 'return H:JSONEncode(kw.Sygnaly.SterowanieSerwera:Invoke("daj", g, "%s"))'
KOD_PRZYCISK_DAWNY = ('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("StrojeProbaOkno") '
                      'local z = g and g:FindFirstChild("Zestawy", true) return tostring(z ~= nil and z:FindFirstChild("Dawny") ~= nil)')


def log(*a):
    print("[%s]" % time.strftime("%H:%M:%S"), *a, flush=True)


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Próba przymierzalni i stroju w walce (Play)")
    ap.add_argument("--studio", default=None)
    ap.add_argument("--bez-zrzutow", action="store_true")
    ap.add_argument("--tylko", default="")
    a = ap.parse_args()
    tylko = {x.strip() for x in a.tylko.split(",") if x.strip()}
    D, _ = DN.zbierz()
    from sesja_play import SesjaPlay  # noqa: E402  (tylko odczyt: wspólna obsługa Play próby walki)
    from studio_mcp import StudioError  # noqa: E402

    wyniki, dane = [], {}

    def punkt(kod, ok, opis):
        wyniki.append({"punkt": kod, "wynik": "OK" if ok is True else ("?" if ok is None else "BŁĄD"), "opis": opis})
        log("%s %s — %s" % (kod, "OK" if ok is True else ("?" if ok is None else "BŁĄD"), opis))

    def chce(kod):
        return not tylko or kod in tylko

    def napis(klasa, ids):
        ok, st = L.normalizuj(D, klasa, list(ids))
        return L.na_napis(st) if ok else None

    def bryly(klasa, ids):
        ok, plan = L.plan(D, klasa, list(ids))
        return len(DN.zloz(D, klasa, plan))

    with SesjaPlay(a.studio) as sp:
        def js(kod, dm="Client"):
            return json.loads(sp.luau(kod, dm))

        def hak(argi):
            return js(KS + 'return H:JSONEncode(k.Sygnaly.SterowanieKlienta:Invoke(%s))' % argi)

        def ustaw(klasa, ids):
            arg = "nil" if ids is None else json.dumps(",".join(ids))
            return js(KS + 'local g = game:GetService("Players"):GetPlayers()[1] return H:JSONEncode('
                      'k.Sygnaly.SterowanieSerwera:Invoke("ustaw", g, "%s", %s))' % (klasa, arg), "Server")

        def atrybut(klasa):
            return js(KS + 'local g = game:GetService("Players"):GetPlayers()[1] return H:JSONEncode({ v = '
                      'g:GetAttribute("%s%s") })' % (D["atrybut"], klasa), "Server").get("v")

        def zrzut(nazwa, st=None):
            if a.bez_zrzutow:
                return
            try:
                obraz = sp.zrzut(st["kamera"], st["patrz"]) if st and st.get("kamera") else sp.zrzut()
                os.makedirs(KLATKI, exist_ok=True)
                obraz.thumbnail((1280, 1280))
                obraz.save(os.path.join(KLATKI, nazwa + ".jpg"), quality=86)
            except StudioError as e:
                log("zrzut %s: %s" % (nazwa, e))

        def czekaj(warunek, limit, co=0.3):
            t0 = time.time()
            while time.time() - t0 < limit:
                try:
                    if warunek():
                        return True
                except (StudioError, ValueError, KeyError):
                    pass
                time.sleep(co)
            return False

        def przy_stojaku():
            return sp.luau(KS + 'local p, kier = k:GetAttribute("PunktStojaka"), k:GetAttribute("KierunekStojaka") '
                           'local g = game:GetService("Players"):GetPlayers()[1] local s = p + kier * 5 + Vector3.new(0, 3, 0) '
                           'g.Character:PivotTo(CFrame.lookAt(s, Vector3.new(p.X, s.Y, p.Z))) return "ok"', "Server")

        # ------------------------------------------------------------------ tryb: bez kowala / z kowalem
        tk = js(KOD_TRYB, "Server")
        if tk.get("jest"):     # kontener kowala jest — dane gracza dochodzą z jego serwera chwilę po wejściu
            czekaj(lambda: js(KOD_TRYB, "Server").get("kowal"), 15)
            tk = js(KOD_TRYB, "Server")
        kowal = bool(tk.get("kowal"))
        nadane = []
        if kowal:
            posiadane = set((tk.get("dostepne") or "").split(","))
            for pid in sorted(i for i, P in D["przedmioty"].items() if not P.get("czescOd")):
                if pid not in posiadane:
                    if js(KOD_DAJ % pid, "Server").get("ok"):
                        nadane.append(pid)
            time.sleep(0.5)
            tk = js(KOD_TRYB, "Server")
        dane["tryb"] = {"kowal": kowal, "nadane": nadane, "dostepne": tk.get("dostepne")}
        log("tryb: %s" % ("z kowalem — nadano %d przedmiotów haczykiem kowala" % len(nadane) if kowal else "bez kowala"))

        # ------------------------------------------------------------------ S00–S01
        if chce("S01"):
            ok = czekaj(lambda: js(KS + 'return H:JSONEncode({ g = k:GetAttribute("KlientGotowy") })').get("g"), 20)
            s = js(KS + 'return H:JSONEncode({ s = k:GetAttribute("SerwerGotowy"), p = k:GetAttribute("PodpowiedziWlaczone"), '
                   'skrot = k:GetAttribute("SkrotSerwera"), haczyk = string.find(workspace.TestWalki2.Moduly.Aktorzy.Source, '
                   '"zeStrojem", 1, true) ~= nil })', "Server")
            punkt("S01", ok and s.get("s") and s.get("p") == 1 and s.get("skrot") == D["skrot"] and s.get("haczyk"),
                  "klient %s, serwer %s, podpowiedzi %s, skrót %s (lokalnie %s), haczyk w Aktorzy %s; tryb %s"
                  % (ok, s.get("s"), s.get("p"), s.get("skrot"), D["skrot"], s.get("haczyk"),
                     "z kowalem (nadano %d)" % len(nadane) if kowal else "bez kowala"))

        # ------------------------------------------------------------------ S02 prawdziwe E, X
        if chce("S02"):
            przy_stojaku()
            time.sleep(1.0)
            sp.luau(KS + 'local p = k:GetAttribute("PunktStojaka") local c = workspace.CurrentCamera '
                    'local g = game:GetService("Players").LocalPlayer.Character.HumanoidRootPart.Position '
                    'c.CFrame = CFrame.lookAt(g + (g - p).Unit * 6 + Vector3.new(0, 4, 0), p + Vector3.new(0, 3, 0)) return "ok"')
            time.sleep(0.6)
            sp.klawisz("E")
            otwarte = czekaj(lambda: hak('"stan"').get("okno"), 4)
            zrzut("01_okno_wojownik", hak('"kadr"'))
            kam = sp.luau('return workspace.CurrentCamera.CameraType.Name')
            sp.klik("StrojeProbaOkno.Ekran.Okno.Naglowek.Zamknij")
            zamkniete = czekaj(lambda: not hak('"stan"').get("okno"), 4)
            kam2 = sp.luau('return workspace.CurrentCamera.CameraType.Name')
            punkt("S02", otwarte and zamkniete and kam.strip() == "Scriptable" and kam2.strip() == "Custom",
                  "E → okno %s (kamera %s), X → zamknięte %s (kamera %s)" % (otwarte, kam.strip(), zamkniete, kam2.strip()))

        # ------------------------------------------------------------------ S03 prawdziwe kliknięcie w oknie
        if chce("S03"):
            ustaw("wojownik", D["klasy"]["wojownik"]["odniesienie"] if kowal else None)
            hak('"otworz"')
            hak('"klasa", "wojownik"')
            time.sleep(0.8)
            sp.klik("StrojeProbaOkno.Ekran.Okno.Slot_Helmet.Nastepny")
            # „>” idzie do następnej opcji slotu (nic + hełmy z oferty; z kowalem tylko posiadane — po nadaniu także
            # hełmy stopni sklepu, więc po hełmie startowym jest leśny, a nie „bez hełmu”)
            odn = D["klasy"]["wojownik"]["odniesienie"]
            helmy = next((z["przedmioty"] for z in L.oferta(D, "wojownik") if z["slot"] == "Helmet"), [])
            if kowal:
                helmy = [i for i in helmy if i in set((tk.get("dostepne") or "").split(","))]
            opcje = [None] + list(helmy)
            teraz = next((i for i in odn if i in helmy), None)
            nastepny = opcje[(opcje.index(teraz) + 1) % len(opcje)]
            ok, oczek = (L.zdejmij(D, "wojownik", odn, "Helmet") if nastepny is None
                         else L.zaloz(D, "wojownik", odn, nastepny))
            cel = L.na_napis(oczek)
            zgodne = czekaj(lambda: atrybut("wojownik") == cel and hak('"stan"').get("strojModelu") == cel, 5)
            st = hak('"stan"')
            punkt("S03", zgodne, "„>” przy hełmie: atrybut %r, podgląd %r (oczekiwane %r)" % (atrybut("wojownik"),
                                                                                         st.get("strojModelu"), cel))
            zrzut("02_okno_bez_helmu", hak('"kadr"'))

        # ------------------------------------------------------------------ S04 odmowy serwera
        if chce("S04"):
            przed = atrybut("wojownik")
            odp = []
            for argi in ('"zaloz", "wojownik", "kot_mag_kapelusz"', '"zaloz", "wojownik", "rycerz_nogawice"',
                         '"zaloz", "lucznik", "rycerz_helm"', '"zdejmij", "wojownik", "Plecy"', '"zaloz", "wojownik", "nie_ma"'):
                odp.append(hak('"zmien", ' + argi).get("powod"))
                time.sleep(0.25)
            spam = js(KS + 'local z = k.Zdalne.ZmienStroj local n = 0 for i = 1, 8 do local w = z:InvokeServer("stan", "wojownik") '
                      'if not w.ok and w.powod == "za_szybko" then n += 1 end end return H:JSONEncode({ n = n })')
            po = atrybut("wojownik")
            oczek = ["przedmiot_innej_klasy", "czesc_zbroi", "zla_klasa", "zly_slot", "nieznany_przedmiot"]
            punkt("S04", odp == oczek and spam.get("n", 0) >= 1 and przed == po,
                  "odmowy %s, za szybko %s z 8, atrybut bez zmian %s" % (odp, spam.get("n"), przed == po))

        # ------------------------------------------------------------------ S05 stroje w podglądzie
        if chce("S05") or chce("S06"):
            hak('"otworz"')
        def stopien(klasa, sid):
            return next((list(z["przedmioty"]) for z in D["klasy"][klasa].get("stopnie") or [] if z["id"] == sid), None)

        stroje = {k: [("golas", []), ("komplet", D["klasy"][k]["odniesienie"]), ("mieszany", MIESZANE[k])]
                  + [(sid, stopien(k, sid)) for sid in STOPNIE if stopien(k, sid)] for k in D["klasy"]}
        if chce("S05"):
            zle = []
            for klasa in D["klasy"]:
                hak('"klasa", "%s"' % klasa)
                for nazwa, ids in stroje[klasa]:
                    time.sleep(0.3)
                    ustaw(klasa, ids)
                    cel = napis(klasa, ids)
                    ok = czekaj(lambda: hak('"stan"').get("strojModelu") == cel, 5)
                    st = hak('"stan"')
                    if not ok or st.get("bryly") != bryly(klasa, ids):
                        zle.append((klasa, nazwa, st.get("strojModelu"), st.get("bryly"), bryly(klasa, ids)))
                    dane.setdefault("S05", {})["%s_%s" % (klasa, nazwa)] = {"bryly": st.get("bryly"), "oczekiwane": bryly(klasa, ids),
                                                                         "zRuchem": st.get("zRuchem")}
                    time.sleep(0.5)
                    kd = hak('"kadr"')
                    dane["S05"]["%s_%s" % (klasa, nazwa)]["kadr"] = {k: (round(v, 3) if isinstance(v, float) else v)
                                                                   for k, v in kd.items() if k not in ("kamera", "patrz")}
                    # podgląd cały nad oknem, w środkowym pasie ekranu (między kolumnami HUD)
                    if not (kd.get("y0", -1) >= 0 and kd.get("y1", 9) <= kd.get("oknoGora", 0) + 0.01
                            and kd.get("x0", -1) >= 0.22 and kd.get("x1", 9) <= 0.78):
                        zle.append((klasa, nazwa, "kadr", {k: round(v, 3) for k, v in kd.items() if isinstance(v, float)}))
                    zrzut("03_%s_%s" % (klasa, nazwa), kd)
            punkt("S05", not zle, "%d strojów w podglądzie = dane (bryły, atrybut Stroj, cały podgląd nad oknem; z kompletami "
                  "stopni)%s" % (sum(len(v) for v in stroje.values()), "; ZŁE: %s" % zle if zle else ""))

        # ------------------------------------------------------------------ S06 klipy klatka po klatce
        if chce("S06"):
            zle, tab = [], {}
            for klasa in D["klasy"]:
                hak('"klasa", "%s"' % klasa)
                ref = {}
                for nazwa, ids in [stroje[klasa][1]] + [x for i, x in enumerate(stroje[klasa]) if i != 1]:   # komplet najpierw
                    time.sleep(0.3)
                    ustaw(klasa, ids)
                    czekaj(lambda: hak('"stan"').get("strojModelu") == napis(klasa, ids), 5)
                    for akcja in hak('"stan"').get("ruchy", []):
                        w = hak('"przebieg", "%s"' % akcja)
                        if not w.get("ok"):
                            zle.append((klasa, nazwa, akcja, w.get("powod")))
                            continue
                        if nazwa == "komplet":
                            ref[akcja] = w["najnizej"]
                        tab["%s/%s/%s" % (klasa, nazwa, akcja)] = {"klatki": w["klatki"], "najnizej": round(w["najnizej"], 3),
                                                                  "odejscie": round(w["odchylenie"], 4),
                                                                  "koniec_cialo": round(w["koniec"]["cialo"], 3),
                                                                  "koniec_grupy": {g: round(v, 3) for g, v in (w["koniec"]["grupy"] or {}).items()}}
                        if w["odchylenie"] > 0.02:
                            zle.append((klasa, nazwa, akcja, "odejście %.3f" % w["odchylenie"]))
                        granica = GRANICA_STOPNI[klasa].get(nazwa, 0.05) + (0.01 if nazwa in STOPNIE else 0.0)
                        if akcja in ref and w["najnizej"] < ref[akcja] - granica:
                            zle.append((klasa, nazwa, akcja, "pod ziemią %.3f (komplet %.3f)" % (w["najnizej"], ref[akcja])))
                        if akcja == "upadek":
                            for g in ("kot_mag_kapelusz", "kot_mag_kostur"):
                                y = (w["koniec"]["grupy"] or {}).get(g)
                                if y is not None and not (-0.08 <= y <= 0.08):
                                    zle.append((klasa, nazwa, g, "po upadku %.3f nad ziemią" % y))
            dane["S06"] = tab
            zawisy = {k: v["koniec_cialo"] for k, v in tab.items() if k.endswith("/upadek")}
            punkt("S06", not zle, "%d klipów × strojów klatka po klatce; zawis ciała po upadku: %s%s"
                  % (len(tab), zawisy, "; ZŁE: %s" % zle[:6] if zle else ""))
            hak('"zamknij"')

        # ------------------------------------------------------------------ S11 mały ekran (telefon 667 × 375)
        if chce("S11"):
            hak('"zamknij"')
            sp.luau(KS + 'k:SetAttribute("EmulacjaEkranu", Vector2.new(667, 375)) return "ok"')
            hak('"otworz"')
            hak('"klasa", "wojownik"')
            time.sleep(0.8)
            kd = hak('"kadr"')
            zrzut("05_telefon_667x375_okno", kd)
            hak('"zamknij"')
            sp.luau(KS + 'k:SetAttribute("EmulacjaEkranu", nil) return "ok"')
            dane["S11"] = {k: v for k, v in kd.items() if k not in ("kamera", "patrz")}
            punkt("S11", (kd.get("tekst") or 0) >= 12 and kd.get("y1", 9) <= kd.get("oknoGora", 0) + 0.01,
                  "okno na 667 × 375: tekst %s pt (najmniej 12), góra okna %.2f, podgląd %.2f–%.2f wysokości ekranu"
                  % (kd.get("tekst"), kd.get("oknoGora", -1), kd.get("y0", -1), kd.get("y1", -1)))

        # ------------------------------------------------------------------ S07 / S08 próba walki
        def walka(klasa, nazwa_zrzutu):
            sp.przy_tablicy()
            time.sleep(0.8)
            sp.start(klasa, PRZECIWNIK[klasa], "5")
            czekaj(lambda: (sp.stan().get("_odtw") or {}).get("faza") == "odtwarzanie", 20)
            time.sleep(1.5)
            m = js('local s = workspace.TestWalki2:FindFirstChild("ScenaLokalna") local m = s and s:FindFirstChild("%s_lokalny") '
                   'local n = 0 if m then for _, d in m:GetDescendants() do if d:IsA("BasePart") and d.Transparency < 1 and '
                   'd.Name ~= "HumanoidRootPart" and d:GetAttribute("Obrys") == nil and d:GetAttribute("Punkt") == nil then n += 1 '
                   'end end end return game:GetService("HttpService"):JSONEncode({ jest = m ~= nil, stroj = m and '
                   'm:GetAttribute("Stroj"), bryly = n })' % klasa)
            if nazwa_zrzutu:
                obraz, st = None, sp.stan().get("_odtw") or {}
                zrzut(nazwa_zrzutu + "_1_start", st)
                koniec = st.get("czasKonca") or 30
                sp.steruj('"przewinDo", %.2f' % (koniec * 0.5))
                time.sleep(1.2)
                zrzut(nazwa_zrzutu + "_2_srodek", sp.stan().get("_odtw"))
                sp.steruj('"przewinDo", %.2f' % max(0, koniec - 2.5))
                time.sleep(1.5)
                zrzut(nazwa_zrzutu + "_3_final", sp.stan().get("_odtw"))
            sp.steruj('"pomin", true')
            czekaj(lambda: (sp.stan().get("_odtw") or {}).get("faza") in ("wynik", "brak"), 15)
            sp.steruj('"zamknij"')
            time.sleep(1.0)
            sp.czekaj_wolna(40)
            return m

        if chce("S07"):
            zle = []
            for klasa in D["klasy"]:
                ustaw(klasa, MIESZANE[klasa])
                m = walka(klasa, "04_walka_%s" % klasa)
                cel = napis(klasa, MIESZANE[klasa])
                dane.setdefault("S07", {})[klasa] = m
                if not (m.get("jest") and m.get("stroj") == cel and m.get("bryly") == bryly(klasa, MIESZANE[klasa])):
                    zle.append((klasa, m, cel))
            punkt("S07", not zle, "bohater w walce w stroju z przymierzalni (3 klasy)%s" % ("; ZŁE: %s" % zle if zle else ""))

        if chce("S08") and kowal:
            time.sleep(0.4)
            przed = atrybut("wojownik")
            r = hak('"zmien", "dawny", "wojownik"')
            po = atrybut("wojownik")
            hak('"otworz"')
            hak('"klasa", "wojownik"')
            time.sleep(0.8)
            przycisk = sp.luau(KOD_PRZYCISK_DAWNY).strip()
            hak('"zamknij"')
            dane["S08"] = {"odpowiedz": r, "przycisk_dawny": przycisk}
            punkt("S08", r.get("powod") == "dawny_niedostepny" and przed == po and przycisk == "false",
                  "z kowalem „Dawnego wyglądu” nie ma: serwer %s (powód %r), atrybut bez zmian %s, przycisk w oknie %s"
                  % ("odmawia" if not r.get("ok") else "PRZYJĄŁ", r.get("powod"), przed == po, przycisk))
        elif chce("S08"):
            ustaw("wojownik", None)
            m = walka("wojownik", None)
            dane["S08"] = m
            punkt("S08", m.get("jest") and m.get("stroj") is None and m.get("bryly") == 127,
                  "dawny wygląd: model walki bez atrybutu Stroj, %s brył (szablon 127)" % m.get("bryly"))

        # ------------------------------------------------------------------ S09 las-pas (jeśli jest)
        if chce("S09"):
            jest = sp.luau('return tostring(workspace:FindFirstChild("LasPasGra") ~= nil)').strip() == "true"
            punkt("S09", None, "las-pas %s — walka w lesie gra tym samym Aktorzy.nowy (kod); próba w lesie do zrobienia "
                  "ręcznie albo jego testy/proba_play.py po ustawieniu stroju" % ("jest" if jest else "nie ma w miejscu"))

        # ------------------------------------------------------------------ S10 konsola
        if chce("S10"):
            k = sp.konsola()
            bledy = [l for l in k.splitlines() if "[StrojeProba]" in l or "StrojeProba" in l and "error" in l.lower()]
            punkt("S10", not bledy, "konsola: %d linii z [StrojeProba]%s" % (len(bledy), (": " + bledy[0][:200]) if bledy else ""))

    if tylko and os.path.isfile(WYNIK):
        # przebieg częściowy: dopisz do poprzedniego wyniku (te same punkty — nowsze)
        with open(WYNIK, encoding="utf-8") as f:
            stary = json.load(f)
        nowe = {w["punkt"] for w in wyniki}
        wyniki = [w for w in stary.get("wyniki", []) if w["punkt"] not in nowe] + wyniki
        wyniki.sort(key=lambda w: w["punkt"])
        dane = dict(stary.get("dane", {}), **dane)
    with open(WYNIK, "w", encoding="utf-8") as f:
        json.dump({"czas": time.strftime("%Y-%m-%d %H:%M"), "skrot": D["skrot"], "wyniki": wyniki, "dane": dane}, f,
                  ensure_ascii=False, indent=1)
    zle = [w for w in wyniki if w["wynik"] == "BŁĄD"]
    log("WYNIK: %d × OK, %d × ?, %d × BŁĄD (%s)" % (sum(w["wynik"] == "OK" for w in wyniki),
                                                    sum(w["wynik"] == "?" for w in wyniki), len(zle),
                                                    os.path.relpath(WYNIK, REPO)))
    return 1 if zle else 0


if __name__ == "__main__":
    sys.exit(main())
