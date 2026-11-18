#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba cutscenki biomu w trybie PLAY w Studio — punkty C00–C14, wynik w <folder>/wynik_play.json (POZA repozytorium).

    python -B swiat/cutscenka_biomu/testy/proba_play.py <folder wyników poza repo>
    python -B swiat/cutscenka_biomu/testy/proba_play.py <folder> --bez-zrzutow

Wymaga: kontener Workspace/CutscenkaBiomu (zbuduj.py), kontenery gry trzech biomów ze skryptem SerwerPasa z haczykiem,
Studio w trybie Edit. Play tylko na czas próby (SesjaPlay z swiat/test_walki2/testy/sesja_play.py zatrzymuje go
zawsze i sprawdza powrót do Edit). Trwa ok. 3 minut.
  C00 Edit: kontener, cztery skrypty i moduły, zero części; haczyk w SerwerPasa każdego biomu
  C01 Play: serwer i klient gotowe, trzy biomy przejęte, zgodność logiki, stary przelot nie ruszył
  C02 las, pierwsze wejście: cutscenka startuje — kamera skryptowa, pasy, plansza z nazwą biomu, postać zakotwiczona,
      blokada walki, HUD i podpowiedzi E schowane
  C03 w trakcie: próba walki odrzucona, postać stoi w miejscu
  C04 koniec: napis i ryk strażnika (dźwięk, gdy katalog ma plik), czas zgodny z danymi
  C05 po cutscence: kamera Custom, W przesuwa postać, kotwica i blokada zdjęte, HUD, podpowiedzi E i lista graczy
      jak przed cutscenką
  C06 drugie wejście do lasu: cutscenki nie ma (licznik bez zmian), pamięć na graczu (atrybut)
  C07 Bagno: pominięcie klawiszem — kończy się od razu, wszystko wraca, serwer liczy pominięcie
  C08 Dżungla: pełna cutscenka z pomiarem czasu klatki (miarodajny tylko, gdy okno Studio jest na wierzchu)
  C09 zrzuty kluczowych kadrów do swiat/cutscenka_biomu/klatki/ (bez nazwy konta i listy graczy)
  C10 odtworzenie na życzenie i śmierć postaci w trakcie: sprzątanie, kamera Custom po odrodzeniu, nic zablokowane
  C11 cutscenka w czasie przejścia przez chmury: klient odmawia, serwer pyta ponownie, pamięć pusta do startu
  C12 telefon: układ dla 667 × 375 i 844 × 390 z klienta = układ z testu bez Studio; rozmiary na bieżącym ekranie
  C13 konsola bez błędów pakietu
  C14 po próbie Studio wróciło do trybu Edit
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (REPO, os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki2", "testy"),
           os.path.join(REPO, "swiat", "test_walki_roblox")):
    if _s not in sys.path:
        sys.path.append(_s)
if PAKIET in sys.path:
    sys.path.remove(PAKIET)
sys.path.insert(0, PAKIET)                             # własne moduły pakietu zawsze pierwsze
import dane as DN  # noqa: E402
import logika_cutscenki as LP  # noqa: E402
import zbuduj as ZB  # noqa: E402

KLATKI = os.path.join(PAKIET, "klatki")
BEZCZYNNOSC_S = 120
PREFIKS = "[CutscenkaBiomu]"

SERWER_STAN = r'''
local HS = game:GetService("HttpService")
local k = workspace:FindFirstChild("__KONTENER__")
if not k then return HS:JSONEncode({ jest = false }) end
local w = { jest = true, atrybuty = {}, stare = {} }
for n, v in k:GetAttributes() do w.atrybuty[n] = v end
for _, n in { __GRY__ } do
	local g = workspace:FindFirstChild(n)
	w.stare[n] = g and g:GetAttribute("LicznikPrzelotow") or -1
end
local s = k.Sygnaly.SterowanieCutscenki:Invoke("stan")
w.stan = s
for _, g in s.gracze do
	if g.pozycja then g.pozycja = { g.pozycja.X, g.pozycja.Y, g.pozycja.Z } end
end
local gracz = game:GetService("Players"):GetPlayers()[1]
w.gracz = gracz and gracz.Name
w.atrybutyGracza = {}
if gracz then
	for n, v in gracz:GetAttributes() do
		if type(v) == "boolean" or type(v) == "number" or type(v) == "string" then w.atrybutyGracza[n] = v end
	end
end
return HS:JSONEncode(w)
'''

SERWER_WEJDZ = r'''
local gracz = game:GetService("Players"):GetPlayers()[1]
local gra = workspace:FindFirstChild("__GRA__")
if not gracz or not gra then return "brak" end
for _, w in { __OTWORZ__ } do
	local p = workspace:FindFirstChild(w)
	if p then p.Sygnaly.SterowaniePasa:Invoke("otworzBrame", gracz.Name) end
end
local r = gra.Sygnaly:FindFirstChild("__UCHWYT__"):Invoke(gracz, { punkt = "przybycie", przelotPo = 0 })
return game:GetService("HttpService"):JSONEncode({ ok = r.ok, powod = r.powod })
'''

SERWER_MIASTECZKO = r'''
local gracz = game:GetService("Players"):GetPlayers()[1]
local r = workspace.__GRA__.Sygnaly.SterowaniePasa:Invoke("przenies", gracz.Name, "miasteczko")
return tostring(r and r.ok)
'''

SERWER_POLECENIE = r'''
local gracz = game:GetService("Players"):GetPlayers()[1]
return tostring(workspace.__KONTENER__.Sygnaly.SterowanieCutscenki:Invoke("__POLECENIE__", gracz.Name, __ARG__))
'''

SERWER_ZABIJ = r'''
local gracz = game:GetService("Players"):GetPlayers()[1]
local hum = gracz.Character and gracz.Character:FindFirstChildOfClass("Humanoid")
if hum then hum.Health = 0 end
return tostring(hum ~= nil)
'''

KLIENT_STAN = r'''
local HS = game:GetService("HttpService")
local SG = game:GetService("StarterGui")
local gracz = game:GetService("Players").LocalPlayer
local k = workspace:FindFirstChild("__KONTENER__")
local w = { stan = k.Sygnaly.SterowanieCutscenkiKlienta:Invoke("stan"), ekran = k.Sygnaly.SterowanieCutscenkiKlienta:Invoke("ekran"),
	gui = {}, gotowy = k:GetAttribute("KlientGotowy") == true, trwa = k:GetAttribute("KlientTrwa") == true }
for _, g in gracz.PlayerGui:GetChildren() do
	if g:IsA("ScreenGui") and g.Enabled then table.insert(w.gui, g.Name) end
end
table.sort(w.gui)
local ok, lista = pcall(function() return SG:GetCoreGuiEnabled(Enum.CoreGuiType.PlayerList) end)
w.listaGraczy = ok and lista
local kam = workspace.CurrentCamera
w.kamera = { kam.CFrame.Position.X, kam.CFrame.Position.Y, kam.CFrame.Position.Z }
local cel = kam.CFrame.Position + kam.CFrame.LookVector * 30
w.patrz = { cel.X, cel.Y, cel.Z }
local hrp = gracz.Character and gracz.Character:FindFirstChild("HumanoidRootPart")
w.pozycja = hrp and { hrp.Position.X, hrp.Position.Y, hrp.Position.Z }
w.zakotwiczona = hrp and hrp.Anchored
local proto = workspace:FindFirstChild("TestWalki2")
local o = proto and proto:FindFirstChild("Moduly") and proto.Moduly:FindFirstChild("OdtwarzaczWalki2")
w.walka = o ~= nil and require(o).czyTrwa() == true
return HS:JSONEncode(w)
'''

KLIENT_WALCZ = r'''
local gra = workspace:FindFirstChild("__GRA__")
local stan = gra and gra:FindFirstChild("Stan")
local pierwszy = stan and stan:GetChildren()[1]
if not pierwszy or gra:GetAttribute("KlientGotowy") ~= true then return "brak" end
return tostring(gra.Sygnaly.SterowanieKlienta:Invoke("walcz", pierwszy.Name))
'''

KLIENT_UKLAD = r'''
local k = workspace.__KONTENER__.Sygnaly.SterowanieCutscenkiKlienta
return game:GetService("HttpService"):JSONEncode(k:Invoke("uklad", __W__, __H__))
'''

KLIENT_CHMURY = r'''
local ch = workspace:FindFirstChild("__CHMURY__")
if not ch then return "brak" end
ch:SetAttribute("__ATRYBUT__", __WARTOSC__)
return "ok"
'''

KLIENT_NAZWA = r'''
local hum = game:GetService("Players").LocalPlayer.Character and game:GetService("Players").LocalPlayer.Character:FindFirstChildOfClass("Humanoid")
if hum then hum.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.__TRYB__ end
return "ok"
'''

KLIENT_PORUSZ = r'''
local gracz = game:GetService("Players").LocalPlayer
local hrp = gracz.Character and gracz.Character:FindFirstChild("HumanoidRootPart")
return hrp and string.format("%.3f %.3f %.3f", hrp.Position.X, hrp.Position.Y, hrp.Position.Z) or "brak"
'''


def log(*a):
    print("[%s]" % time.strftime("%H:%M:%S"), *a, flush=True)


def wstaw(szablon, **w):
    for k, v in w.items():
        szablon = szablon.replace("__%s__" % k, str(v))
    return szablon


def bezczynnosc_s():
    if os.name != "nt":
        return None
    import ctypes

    class LII(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
    lii = LII()
    lii.cbSize = ctypes.sizeof(LII)
    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
        return None
    return ((ctypes.windll.kernel32.GetTickCount() - lii.dwTime) & 0xFFFFFFFF) / 1000.0


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Próba cutscenki biomu (Play)")
    ap.add_argument("folder", help="folder wyników POZA repozytorium")
    ap.add_argument("--bez-zrzutow", action="store_true")
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    folder = os.path.abspath(a.folder)
    if os.path.commonpath([folder, REPO]) == REPO:
        sys.exit("Folder wyników musi leżeć poza repozytorium.")
    os.makedirs(folder, exist_ok=True)
    U = DN.ustawienia()
    D = DN.wszystko(U)
    PR = U["progi"]
    kont = U["kontener"]
    biomy = {b["id"]: b for b in D["biomy"]}
    uchwyty = {DN.dane_gry(w)["biom"]["id"]: DN.dane_gry(w)["biom"]["uchwyt"] for w in U["biomy"]}
    gry = [b["kontenerGry"] for b in D["biomy"]]
    wyniki, dane = [], {}

    def punkt(kod, ok, opis):
        wyniki.append({"punkt": kod, "wynik": "OK" if ok is True else ("?" if ok is None else "BŁĄD"), "opis": opis})
        log("%s %s — %s" % (kod, wyniki[-1]["wynik"], opis))

    bezcz = bezczynnosc_s()
    okno = [sys.executable, "-B", os.path.join(REPO, "tools", "studio_okno.py")]
    stan_okna = subprocess.run(okno, capture_output=True).stdout.decode("utf-8", "replace")
    na_wierzchu = "na wierzchu" in stan_okna
    if not na_wierzchu and bezcz is not None and bezcz >= BEZCZYNNOSC_S:
        na_wierzchu = subprocess.run(okno + ["--na-wierzch"], capture_output=True).returncode == 0
    log("bezczynność: %s s; okno Studio na wierzchu: %s" % ("?" if bezcz is None else "%.0f" % bezcz, na_wierzchu))
    dane["okno_na_wierzchu"] = na_wierzchu

    from sesja_play import SesjaPlay  # noqa: E402
    from studio_mcp import StudioMCP  # noqa: E402
    from cel_studio import wybierz_studio  # noqa: E402

    # C00: odczyt w trybie Edit
    with StudioMCP(timeout=120) as s:
        sid = wybierz_studio(s, a.studio)
        r = s.call("execute_luau", {"code": ZB.kod_stanu(kont), "datamodel_type": "Edit", "studio_id": sid})
        edit = json.loads(r["text"])
        r = s.call("execute_luau", {"code": ZB.kod_konca(D, "próba: odczyt"), "datamodel_type": "Edit", "studio_id": sid})
        haczyki = r["text"]
    dane["edit"], dane["haczyki"] = edit, haczyki
    punkt("C00", bool(edit.get("jest")) and edit.get("czesci") == 0 and len(edit.get("dzieci", [])) >= 7
          and "BRAK" not in haczyki and edit.get("atrybuty", {}).get("Skrot") == D["skrot"],
          "Edit: kontener %s, skrót %s (dane %s), części %s; %s" % ("jest" if edit.get("jest") else "BRAK",
                                                                   edit.get("atrybuty", {}).get("Skrot"), D["skrot"],
                                                                   edit.get("czesci"), haczyki[:300]))
    if not edit.get("jest"):
        return 1

    with SesjaPlay(a.studio) as sp:
        def serwer():
            return json.loads(sp.luau(wstaw(SERWER_STAN, KONTENER=kont, GRY=", ".join('"%s"' % g for g in gry)), "Server"))

        def klient():
            return json.loads(sp.luau(wstaw(KLIENT_STAN, KONTENER=kont), "Client"))

        def gracz_serwera(st):
            return st["stan"]["gracze"][st["gracz"]]

        def wejdz(biom):
            otworz = [b["kontenerGry"] for b in D["biomy"][:[x["id"] for x in D["biomy"]].index(biom)]]
            return sp.luau(wstaw(SERWER_WEJDZ, GRA=biomy[biom]["kontenerGry"], UCHWYT=uchwyty[biom],
                                 OTWORZ=", ".join('"%s"' % g for g in otworz)), "Server", timeout=60)

        def czekaj(warunek, limit, co=0.25):
            t0 = time.time()
            while time.time() - t0 < limit:
                k = klient()
                if warunek(k):
                    return k, time.time() - t0
                time.sleep(co)
            return klient(), None

        def zrzut(nazwa, zapisane):
            if a.bez_zrzutow:
                return
            k = klient()
            im = sp.zrzut(k["kamera"], k["patrz"])
            if im.width > 1600:
                im = im.resize((1600, round(im.height * 1600 / im.width)))
            os.makedirs(KLATKI, exist_ok=True)
            im.save(os.path.join(KLATKI, nazwa + ".jpg"), quality=88)
            zapisane.append(nazwa + ".jpg")

        try:
            time.sleep(2.0)
            sp.luau(wstaw(KLIENT_NAZWA, TRYB="None"), "Client")
            # C01
            st, kl = serwer(), klient()
            dane["start"] = {"serwer": st, "klient": kl}
            stany = st["stan"]["biomy"]
            przed_gui, przed_lista = kl["gui"], kl["listaGraczy"]
            punkt("C01", st["stan"]["gotowy"] and kl["gotowy"] and all(v == "przejety" for v in stany.values())
                  and str(st["atrybuty"].get("ZgodnoscLogiki", "")).startswith("OK") and kl["kamera"] is not None,
                  "serwer gotowy: %s, klient gotowy: %s, biomy: %s, zgodność logiki: %s, zapis postępu aktywny: %s"
                  % (st["stan"]["gotowy"], kl["gotowy"], stany, st["atrybuty"].get("ZgodnoscLogiki"), st["stan"]["zapisAktywny"]))
            stare0 = st["stare"]
            poz0 = None

            # C02: las, pierwsze wejście
            log("wejście do lasu:", wejdz("las"))
            kl, po = czekaj(lambda k: k["stan"]["trwa"] and k["stan"]["trwa"]["lot"], 12)
            st = serwer()
            g = gracz_serwera(st)
            dane["las_start"] = {"klient": kl, "serwer": g, "po_s": po}
            poz0 = kl["pozycja"]
            ok = (po is not None and kl["stan"]["kamera"] == "Scriptable" and kl["stan"]["pasy"] and g["faza"] == "trwa"
                  and g["zakotwiczony"] and g["blokadaWalki"] and not kl["stan"]["podpowiedzi"]
                  and kl["ekran"]["nazwa"]["napis"] == biomy["las"]["nazwa"].upper()
                  and not [n for n in kl["gui"] if not n.startswith(kont)])
            punkt("C02", ok, "las: start po %s s od wejścia, kamera %s, pasy %s, plansza „%s”, faza serwera %s, kotwica %s, "
                  "blokada walki %s, podpowiedzi E %s, widoczne ekrany: %s"
                  % ("?" if po is None else "%.1f" % po, kl["stan"]["kamera"], kl["stan"]["pasy"], kl["ekran"]["nazwa"]["napis"],
                     g["faza"], g["zakotwiczony"], g["blokadaWalki"], kl["stan"]["podpowiedzi"], kl["gui"]))
            zapisane = []
            time.sleep(max(0.0, 0.9 - (kl["stan"]["trwa"]["t"] if kl["stan"]["trwa"] else 0)))
            zrzut("01_las_plansza", zapisane)

            # C03: próba walki i postać w miejscu
            walcz = sp.luau(wstaw(KLIENT_WALCZ, GRA=biomy["las"]["kontenerGry"]), "Client")
            time.sleep(1.5)
            kl = klient()
            ruch = max(abs(kl["pozycja"][i] - poz0[i]) for i in range(3)) if kl["pozycja"] and poz0 else 9
            punkt("C03", not kl["walka"] and ruch < 0.05 and kl["zakotwiczona"],
                  "próba walki w trakcie: odpowiedź klienta potworów %s, walka trwa: %s; postać przesunęła się o %.3f st"
                  % (walcz, kl["walka"], ruch))
            zrzut("02_las_przegroda", zapisane)

            # C04: koniec ze strażnikiem
            czekaj(lambda k: k["stan"]["trwa"] and k["stan"]["trwa"]["t"] >= biomy["las"]["trasa"]["lot"] + 1.0, 14)
            zrzut("03_las_straznik", zapisane)
            kl, _ = czekaj(lambda k: not k["stan"]["trwa"] and k["stan"]["ostatnia"], 14)
            o = kl["stan"]["ostatnia"] or {}
            dane["las_koniec"] = kl
            czas = biomy["las"]["trasa"]["czas"]
            ok = (o.get("ok") is True and not o.get("pominieta") and abs(o.get("czas", 0) - czas) < 1.5
                  and o.get("napisStraznika") == biomy["las"]["straznik"]["nazwa"].upper() and o.get("ryk") is True)
            punkt("C04", ok, "koniec: ok %s, czas %.1f s (dane %.1f), napis „%s”, klip ryku %s, dźwięk ryku %s, podpisów przegród %s"
                  % (o.get("ok"), o.get("czas", 0), czas, o.get("napisStraznika"), o.get("ryk"), o.get("dzwiek"), o.get("podpisy")))

            # C05: powrót
            time.sleep(1.2)
            p1 = [float(x) for x in sp.luau(KLIENT_PORUSZ, "Client").split()]
            sp.call("user_keyboard_input", {"datamodel_type": "Client", "actions": [
                {"action": "keyDown", "key_code": "W"}, {"action": "wait", "wait_time_ms": 900}, {"action": "keyUp", "key_code": "W"}]})
            time.sleep(0.4)
            p2 = [float(x) for x in sp.luau(KLIENT_PORUSZ, "Client").split()]
            droga = ((p2[0] - p1[0]) ** 2 + (p2[2] - p1[2]) ** 2) ** 0.5
            kl, st = klient(), serwer()
            g = gracz_serwera(st)
            ok = (kl["stan"]["kamera"] == "Custom" and droga > 4 and not g["zakotwiczony"] and not g["kotwicaCzesci"]
                  and not g["blokadaWalki"] and kl["gui"] == przed_gui and kl["stan"]["podpowiedzi"]
                  and kl["listaGraczy"] == przed_lista and g["faza"] == "brak" and not kl["trwa"])
            punkt("C05", ok, "po cutscence: kamera %s, W przesuwa o %.1f st, kotwica %s, blokada walki %s, ekrany jak przed: %s, "
                  "podpowiedzi E %s, lista graczy jak przed: %s" % (kl["stan"]["kamera"], droga, g["zakotwiczony"],
                                                                    g["blokadaWalki"], kl["gui"] == przed_gui,
                                                                    kl["stan"]["podpowiedzi"], kl["listaGraczy"] == przed_lista))

            # C06: drugie wejście
            licznik = st["atrybuty"].get("LicznikCutscenek")
            sp.luau(wstaw(SERWER_MIASTECZKO, GRA=biomy["las"]["kontenerGry"]), "Server", timeout=60)
            time.sleep(2.5)
            log("drugie wejście do lasu:", wejdz("las"))
            time.sleep(5.0)
            st, kl = serwer(), klient()
            g = gracz_serwera(st)
            punkt("C06", st["atrybuty"].get("LicznikCutscenek") == licznik and g["faza"] == "brak" and not kl["stan"]["trwa"]
                  and g["widziane"]["las"] and st["atrybutyGracza"].get(biomy["las"]["atrybut"]) is True
                  and kl["stan"]["kamera"] == "Custom",
                  "drugie wejście: licznik %s → %s, faza %s, kamera %s, pamięć las %s, atrybut gracza %s = %s"
                  % (licznik, st["atrybuty"].get("LicznikCutscenek"), g["faza"], kl["stan"]["kamera"], g["widziane"]["las"],
                     biomy["las"]["atrybut"], st["atrybutyGracza"].get(biomy["las"]["atrybut"])))

            # C07: Bagno i pominięcie klawiszem
            pom0 = st["atrybuty"].get("LicznikPominiec")
            log("wejście do Bagna:", wejdz("bagno"))
            kl, po = czekaj(lambda k: k["stan"]["trwa"] and k["stan"]["trwa"]["lot"]
                            and k["stan"]["trwa"]["t"] >= U["oprawa"]["pomijanie"]["od_s"] + 0.6, 14)
            przycisk = kl["ekran"]["pomin"]
            zrzut("04_bagno_przycisk_pomin", zapisane)
            sp.klawisz("Space")
            kl, po2 = czekaj(lambda k: not k["stan"]["trwa"] and k["stan"]["ostatnia"] and k["stan"]["ostatnia"]["biom"] == "bagno", 6)
            time.sleep(1.0)
            kl, st = klient(), serwer()
            g = gracz_serwera(st)
            o = kl["stan"]["ostatnia"] or {}
            ok = (o.get("pominieta") is True and o.get("czas", 99) < 6 and kl["stan"]["kamera"] == "Custom"
                  and st["atrybuty"].get("LicznikPominiec") == (pom0 or 0) + 1 and not g["zakotwiczony"]
                  and not g["blokadaWalki"] and kl["gui"] == przed_gui and przycisk["widoczny"]
                  and przycisk["w"] >= PR["przycisk_min_px"] and przycisk["h"] >= PR["przycisk_min_px"]
                  and g["widziane"]["bagno"])
            punkt("C07", ok, "Bagno: przycisk widoczny %s (%.0f × %.0f px, napis %s), po Spacji koniec w %s s, pominięta %s, "
                  "czas %.1f s, kamera %s, licznik pominięć %s → %s, ekrany jak przed: %s"
                  % (przycisk["widoczny"], przycisk["w"], przycisk["h"], przycisk["napis"],
                     "?" if po2 is None else "%.1f" % po2, o.get("pominieta"), o.get("czas", 0), kl["stan"]["kamera"], pom0,
                     st["atrybuty"].get("LicznikPominiec"), kl["gui"] == przed_gui))

            # C08: Dżungla — pełna cutscenka z pomiarem klatek; C09: zrzuty
            log("wejście do Dżungli:", wejdz("dzungla"))
            tr = biomy["dzungla"]["trasa"]
            kl, po = czekaj(lambda k: k["stan"]["trwa"] and k["stan"]["trwa"]["lot"], 14)
            for nazwa, t in (("05_dzungla_plansza", 1.0), ("06_dzungla_przegroda", tr["przystanki"][1]["t"]),
                             ("07_dzungla_leze", tr["przystanki"][-1]["t"]), ("08_dzungla_straznik", tr["lot"] + 1.0)):
                czekaj(lambda k: not k["stan"]["trwa"] or k["stan"]["trwa"]["t"] >= t, 14, co=0.1)
                zrzut(nazwa, zapisane)
            kl, _ = czekaj(lambda k: not k["stan"]["trwa"] and k["stan"]["ostatnia"] and k["stan"]["ostatnia"]["biom"] == "dzungla", 16)
            o = kl["stan"]["ostatnia"] or {}
            kla = o.get("klatki") or {}
            dane["dzungla_koniec"] = kl
            # zrzuty wstrzymują klatki, więc pomiar bez zrzutów jest uczciwszy — przy zrzutach wynik tylko informacyjny
            miarodajny = na_wierzchu and a.bez_zrzutow
            ok = o.get("ok") is True and o.get("napisStraznika") == biomy["dzungla"]["straznik"]["nazwa"].upper()
            punkt("C08", (ok and kla.get("sr", 99) <= PR["klatka_ms"]) if miarodajny else (None if ok else False),
                  "Dżungla: ok %s, czas %.1f s, napis „%s”, ryk %s; klatki: %s, średnio %.1f ms, 95%% %.1f ms, najdłuższa %.1f ms; "
                  "próg %.0f ms%s" % (o.get("ok"), o.get("czas", 0), o.get("napisStraznika"), o.get("ryk"), kla.get("n"),
                                      kla.get("sr", 0), kla.get("p95", 0), kla.get("maks", 0), PR["klatka_ms"],
                                      "" if miarodajny else " — pomiar niemiarodajny (okno nie na wierzchu albo zrzuty w trakcie)"))
            punkt("C09", None if a.bez_zrzutow else len(zapisane) >= 7,
                  "zrzuty pominięte (--bez-zrzutow)" if a.bez_zrzutow else "zrzuty: %s" % ", ".join(zapisane))

            # C10: odtworzenie na życzenie i śmierć postaci w trakcie
            time.sleep(1.5)
            odt = sp.luau(wstaw(SERWER_POLECENIE, KONTENER=kont, POLECENIE="odtworz", ARG='"las"'), "Server")
            kl, po = czekaj(lambda k: k["stan"]["trwa"] and k["stan"]["trwa"]["lot"] and k["stan"]["trwa"]["t"] >= 2.0, 14)
            sp.luau(SERWER_ZABIJ, "Server")
            kl, po2 = czekaj(lambda k: not k["stan"]["trwa"] and k["stan"]["kamera"] == "Custom" and k["pozycja"], 20)
            time.sleep(1.0)
            kl, st = klient(), serwer()
            g = gracz_serwera(st)
            o = kl["stan"]["ostatnia"] or {}
            ok = (odt.strip() == "true" and po is not None and o.get("ok") is False and kl["stan"]["kamera"] == "Custom"
                  and g["faza"] == "brak" and not g["kotwicaCzesci"] and not g["blokadaWalki"] and kl["gui"] == przed_gui
                  and kl["stan"]["podpowiedzi"])
            punkt("C10", ok, "odtworzenie na życzenie: %s (start po %s s); śmierć w trakcie: powód „%s”, kamera %s, faza %s, "
                  "kotwica %s, blokada %s, ekrany jak przed: %s" % (odt.strip(), "?" if po is None else "%.1f" % po, o.get("powod"),
                                                                   kl["stan"]["kamera"], g["faza"], g["kotwicaCzesci"],
                                                                   g["blokadaWalki"], kl["gui"] == przed_gui))

            # C11: cutscenka trafia na przejście przez chmury (lokalny atrybut „trwa” jak w KlientTeleportu)
            Z = U["zaleznosci"]["chmury"]
            sp.luau(wstaw(SERWER_POLECENIE, KONTENER=kont, POLECENIE="zapomnij", ARG='"bagno"'), "Server")
            sp.luau(wstaw(SERWER_MIASTECZKO, GRA=biomy["las"]["kontenerGry"]), "Server", timeout=60)
            time.sleep(2.5)
            chm = sp.luau(wstaw(KLIENT_CHMURY, CHMURY=Z["kontener"], ATRYBUT=Z["atrybut"], WARTOSC="true"), "Client")
            odm0 = serwer()["atrybuty"].get("LicznikOdmow") or 0
            log("wejście do Bagna w czasie chmur:", wejdz("bagno"))
            time.sleep(4.0)
            st, kl = serwer(), klient()
            g = gracz_serwera(st)
            w_chmurach = (not kl["stan"]["trwa"], (st["atrybuty"].get("LicznikOdmow") or 0) - odm0, g["widziane"]["bagno"],
                          kl["stan"]["kamera"], g["zakotwiczony"])
            sp.luau(wstaw(KLIENT_CHMURY, CHMURY=Z["kontener"], ATRYBUT=Z["atrybut"], WARTOSC="false"), "Client")
            kl, po = czekaj(lambda k: k["stan"]["trwa"] and k["stan"]["trwa"]["lot"], 10)
            time.sleep(1.5)
            sp.klawisz("Space")
            czekaj(lambda k: not k["stan"]["trwa"], 6)
            ok = (chm.strip() == "ok" and w_chmurach[0] and w_chmurach[1] >= 2 and not w_chmurach[2] and not w_chmurach[4]
                  and po is not None)
            punkt("C11", ok if chm.strip() == "ok" else None,
                  "w czasie chmur: cutscenka nie gra %s, odmów %s, pamięć Bagna %s, kamera %s, kotwica %s; po chmurach start po %s s"
                  % (w_chmurach[0], w_chmurach[1], w_chmurach[2], w_chmurach[3], w_chmurach[4], "?" if po is None else "%.1f" % po)
                  if chm.strip() == "ok" else "brak kontenera chmur — punkt pominięty")

            # C12: telefon
            k = DN.uklad_stale(U)
            zle = []
            for w, h in U["telefon"]:
                lu = json.loads(sp.luau(wstaw(KLIENT_UKLAD, KONTENER=kont, W=w, H=h), "Client"))
                py = LP.uklad(w, h, 0, 0, 0, 0, k)
                for nazwa in ("pomin", "nazwa", "nadtytul", "podpis", "straznik"):
                    for pole in ("x", "y", "w", "h", "tekst"):
                        if abs(lu[nazwa][pole] - py[nazwa][pole]) > 0.01:
                            zle.append("%dx%d %s.%s: klient %s, test %s" % (w, h, nazwa, pole, lu[nazwa][pole], py[nazwa][pole]))
                if py["pomin"]["w"] < PR["przycisk_min_px"] or py["pomin"]["h"] < PR["przycisk_min_px"]:
                    zle.append("%dx%d: przycisk za mały" % (w, h))
            e = dane["las_start"]["klient"]["ekran"]
            if e["nazwa"]["tekst"] < PR["napis_min_px"] or e["nadtytul"]["tekst"] < PR["napis_min_px"]:
                zle.append("napisy planszy poniżej %d px na bieżącym ekranie" % PR["napis_min_px"])
            punkt("C12", not zle, "układ 667 × 375 i 844 × 390 u klienta = układ z testu; bieżący ekran %s × %s: nazwa %s px, "
                  "nadtytuł %s px, przycisk %.0f × %.0f px" % (e["szer"], e["wys"], e["nazwa"]["tekst"], e["nadtytul"]["tekst"],
                                                              przycisk["w"], przycisk["h"]) if not zle else "; ".join(zle[:6]))

            # C01 c.d.: stary przelot nie ruszył ani razu
            st = serwer()
            punkt("C01p", st["stare"] == stare0, "liczniki starego przelotu pasa: %s → %s" % (stare0, st["stare"]))

            # C13: konsola
            kons = sp.konsola()
            with open(os.path.join(folder, "konsola.txt"), "w", encoding="utf-8") as f:
                f.write(kons)
            linie = [l for l in kons.splitlines() if (PREFIKS in l or kont in l)
                     and "serwer gotowy" not in l and "klient gotowy" not in l
                     and "postać usunięta" not in l and "postać zginęła" not in l]
            kl = klient()
            punkt("C13", not linie and kl["stan"]["bledy"] == 0, "konsola bez błędów i ostrzeżeń pakietu (poza zapowiedzianym "
                  "przerwaniem przy śmierci postaci); błędów klienta: %s" % kl["stan"]["bledy"]
                  if not linie else "wpisy pakietu w konsoli: " + " | ".join(linie[:5]))
        finally:
            try:
                sp.luau(wstaw(KLIENT_NAZWA, TRYB="Viewer"), "Client")
            except Exception:  # noqa: BLE001
                pass
    edit_po = getattr(sp, "edit_po", None)
    punkt("C14", edit_po is True, "Studio po próbie w trybie Edit: %s" % edit_po)
    with open(os.path.join(folder, "wynik_play.json"), "w", encoding="utf-8") as f:
        json.dump({"kiedy": time.strftime("%Y-%m-%d %H:%M"), "wyniki": wyniki, "dane": dane}, f, ensure_ascii=False, indent=1,
                  default=str)
    zle = [w for w in wyniki if w["wynik"] == "BŁĄD"]
    log("RAZEM: %d OK, %d ?, %d BŁĄD" % (sum(w["wynik"] == "OK" for w in wyniki),
                                         sum(w["wynik"] == "?" for w in wyniki), len(zle)))
    return 1 if zle else 0


if __name__ == "__main__":
    sys.exit(main())
