#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba kowala w trybie PLAY w Studio (część B) — lista K00–K13, wynik w testy/wynik_play.json, zrzuty w klatki/.

    python -B swiat/kowal_proba/testy/proba_play.py --sprawdz            # bez Studio: każdy kawałek Luau parsuje się
    python -B tools/studio_okno.py --na-wierzch                          # przed próbą (okno w tle rysuje 15 kl./s)
    python -B swiat/kowal_proba/testy/proba_play.py [--tylko K05,K08] [--bez-zrzutow] [--studio <id>]

Wymaga w trybie Edit: Workspace/KowalProba (zbuduj.py), StanGracza z sygnałami Modyfikatory, DanePakietu i WydajZloto
(przebudowa stanu gracza 18.11), najlepiej StrojeProba i LasPasGra. Play tylko na czas próby (SesjaPlay z
swiat/test_walki2/testy/sesja_play.py zatrzymuje go zawsze). Zrzuty bez listy graczy i czatu (nazwa konta nie trafia
do plików), wynik bez nazw kont.
  K00 Edit: kontenery i skrót danych = lokalny
  K01 gotowość: serwer i klient kowala, zgodność logiki, podpowiedź E, stan gracza podłączony, kowal animowany
  K02 start: podstawowy zestaw klasy, strój w przymierzalni, wpis „kowal” w Modyfikatory, bohater = wzór poziomu
  K03 kuźnia z kilku stron (zrzuty: przód, ¾ z lewej i prawej, od drzwi zbrojowni, kowal przy kowadle)
  K04 prawdziwe E przy kowalu otwiera okno (zrzut); lista przedmiotów klasy. Od 26.11.2026, gdy stoi okno kowala Pawła
      (OknoKowala): po E tylko jego okno (okno próbne się nie otwiera), widok serwera z przedmiotami klasy, zamknięcie X
  K05 łup: haczyk (nowy przedmiot → założony, napis) i prawdziwa droga przez przyrost tokenów krainy (ochrona ≤ 10)
  K06 walka z nowymi liczbami: wpis kowala = oczekiwany; wejście do lasu jak gracz (TELEPORT → chmury → Las, jak
      swiat/przejscie_gry/proba_dymna.py), prawdziwe E przy slime'ie: bohater walki ma broń i pancerz z przedmiotami,
      model bohatera w walce nosi przedmiot z łupu (atrybut Stroj); zrzut walki i karty wyniku
  K07 wskazówka celu „kowal” (krok g, znacznik nad E kowala) i rozbiórka zapasu prawdziwym kliknięciem (materiały +N; zrzut)
  K08 ulepszenie prawdziwym kliknięciem: Złoto i materiały w dół, poziom w górę, klip radości kowala (zrzut)
  K09 odmowy serwera: za mało Złota, za mało materiałów, daleko od kowala, zły przedmiot — nic się nie zmienia
  K10 reset postaci: przedmioty, poziomy i wpis Modyfikatory zostają; okno działa
  K11 przymierzalnia: tylko posiadane przedmioty, bez „Dawny wygląd” (serwer odmawia)
  K12 okno na małym ekranie (emulacja 667 × 375): tekst ≥ 12 pt, okno nad dolną krawędzią; zrzut. Gdy okno próbne
      zastąpiło okno Pawła — „?” (okno próbne nie jest już oknem gry; jego okna na telefonie próba nie mierzy)
  K13 konsola bez błędów [KowalProba]
"""
import argparse
import json
import math
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (REPO, os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki2", "testy"), PAKIET):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import dane as DN  # noqa: E402
import logika_kowala as LK  # noqa: E402

KLATKI = os.path.join(PAKIET, "klatki")
WYNIK = os.path.join(TU, "wynik_play.json")
H = 'local H = game:GetService("HttpService") '
KK = H + 'local k = workspace:FindFirstChild("KowalProba") '
GR = 'local g = game:GetService("Players"):GetPlayers()[1] '
J = ('local function J(v) local t = typeof(v) if t == "Vector3" then return { v.X, v.Y, v.Z } '
     'elseif t == "table" then local o = {} for a, b in v do o[a] = J(b) end return o end return v end ')

# Kawałki Luau (szablony %s / %d / %f) — --sprawdz parsuje każdy po podstawieniu (tools/walka/luau_mini.py).
KOD = {
    "edit": H + ('local function jest(n) return workspace:FindFirstChild(n) ~= nil end '
                 'local s = workspace:FindFirstChild("StanGracza") local sy = s and s:FindFirstChild("Sygnaly") '
                 'local k = workspace:FindFirstChild("KowalProba") '
                 'return H:JSONEncode({ kowal = k ~= nil and k:GetAttribute("Wygenerowane") == true, '
                 'skrot = k and k:GetAttribute("Skrot") or false, stan = s ~= nil, '
                 'mod = sy ~= nil and sy:FindFirstChild("Modyfikatory") ~= nil, '
                 'dane = sy ~= nil and sy:FindFirstChild("DanePakietu") ~= nil, '
                 'wydaj = sy ~= nil and sy:FindFirstChild("WydajZloto") ~= nil, stroje = jest("StrojeProba"), '
                 'las = jest("LasPasGra"), bazar = jest("MiasteczkoBazar"), '
                 'czesci = k and #k.Kuznia:GetDescendants() or 0 })'),
    "atr_kowala": KK + ('local w = {} for _, n in { "SerwerKowalaGotowy", "ZgodnoscLogikiKowala", "PodpowiedziWlaczone", '
                        '"StanGraczaPodlaczony", "SkrotSerwera", "LicznikLupow", "LicznikUlepszen", "LicznikRozbiorek", '
                        '"LicznikOdmow" } do w[n] = k:GetAttribute(n) end return H:JSONEncode(w)'),
    "atr_klienta": KK + ('return H:JSONEncode({ gotowy = k:GetAttribute("KlientKowalaGotowy"), '
                         'animowany = k:GetAttribute("KowalAnimowany"), okno = k:GetAttribute("OknoOtwarte"), '
                         'napis = k:GetAttribute("OstatniNapis"), zastapione = k:GetAttribute("OknoZastapione") })'),
    # okno kowala Pawła (ScreenGui „OknoKowala”, src/client/OknoKowalaClient, od 24.11.2026) — tylko odczyt
    "okno_pawla": ('local H = game:GetService("HttpService") local pg = game:GetService("Players").LocalPlayer.PlayerGui '
                   'local g = pg:FindFirstChild("OknoKowala") local o = pg:FindFirstChild("KowalProbaOkno") '
                   'return H:JSONEncode({ jest = g ~= nil and g:IsA("ScreenGui"), wlaczone = g ~= nil and g:IsA("ScreenGui") and g.Enabled, '
                   'proba = o ~= nil and o:IsA("ScreenGui") and o.Enabled })'),
    "gracz": KK + GR + ('local klasa = ({ Warrior = "wojownik", Scout = "zwiadowca", Mage = "mag" })[g:GetAttribute("Class") or ""] '
                        'or "wojownik" return H:JSONEncode({ klasa = klasa, dostepne = g:GetAttribute("KowalDostepne"), '
                        'materialy = g:GetAttribute("KowalMaterialy"), zloto = g:GetAttribute("Gold"), '
                        'poziom = g:GetAttribute("Level"), stroj = g:GetAttribute("StrojProba_" .. klasa) })'),
    "stan_kowala": KK + GR + J + 'return H:JSONEncode(J(k.Sygnaly.SterowanieSerwera:Invoke("stan", g)))',
    "hak_serwera": KK + GR + J + 'return H:JSONEncode(J(k.Sygnaly.SterowanieSerwera:Invoke("%s", g, %s, %s)))',
    "mody": H + GR + J + ('local s = workspace.StanGracza.Sygnaly return H:JSONEncode({ mod = J(s.Modyfikatory:Invoke("czytaj", g)), '
                          'bohater = J(s.Bohater:Invoke(g)) })'),
    "ustaw_atr": GR + 'g:SetAttribute("%s", %s) return "ok"',
    "tokeny": H + GR + 'return H:JSONEncode({ t = g:GetAttribute("%s") or 0 })',
    "bez_nazwy": ('local SG = game:GetService("StarterGui") for _, t in { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Chat } do '
                  'pcall(function() SG:SetCoreGuiEnabled(t, false) end) end return "ok"'),
    "przy_kowalu": GR + ('local p = Vector3.new(%f, %f, %f) local cel = Vector3.new(%f, p.Y, %f) '
                         'g.Character:PivotTo(CFrame.lookAt(p, cel)) g.Character.HumanoidRootPart.AssemblyLinearVelocity = Vector3.zero '
                         'return "ok"'),
    "kamera": ('local c = workspace.CurrentCamera c.CameraType = Enum.CameraType.Scriptable '
               'c.CFrame = CFrame.lookAt(Vector3.new(%f, %f, %f), Vector3.new(%f, %f, %f)) return "ok"'),
    "kamera_zwykla": 'workspace.CurrentCamera.CameraType = Enum.CameraType.Custom return "ok"',
    "klient": KK + J + 'return H:JSONEncode(J(k.Sygnaly.SterowanieKlienta:Invoke("%s", %s)))',
    "zdalnie": KK + J + 'return H:JSONEncode(J(k.Zdalne.Kuznia:InvokeServer("%s", %s)))',
    "emulacja": KK + 'k:SetAttribute("EmulacjaEkranu", %s) return "ok"',
    "okno_geometria": H + ('local pg = game:GetService("Players").LocalPlayer.PlayerGui local g = pg:FindFirstChild("KowalProbaOkno") '
                           'local o = g and g:FindFirstChild("Okno", true) if not o then return H:JSONEncode({}) end '
                           'local e = g.AbsoluteSize return H:JSONEncode({ dol = (o.AbsolutePosition.Y + o.AbsoluteSize.Y) / e.Y, '
                           'gora = o.AbsolutePosition.Y / e.Y, lewo = o.AbsolutePosition.X / e.X, '
                           'prawo = (o.AbsolutePosition.X + o.AbsoluteSize.X) / e.X })'),
    "stroje": H + J + 'return H:JSONEncode(J(workspace.StrojeProba.Zdalne.ZmienStroj:InvokeServer("%s", "%s", %s)))',
    "reset": GR + 'g:LoadCharacter() return "ok"',
    "postac_gotowa": 'local p = game:GetService("Players").LocalPlayer return tostring(p.Character ~= nil and '
                     'p.Character:FindFirstChild("HumanoidRootPart") ~= nil)',
    # las-pas (tylko odczyt cudzego kontenera; walka przez jego haczyk testowy, jak swiat/stan_gracza/testy/proba_play.py)
    "potwor_w_strefie": H + J + ('local k = workspace.LasPasGra local w for _, c in k.Stan:GetChildren() do '
                                 'if c:GetAttribute("Strefa") == "%s" and c:GetAttribute("Stan") ~= "zajety" then w = c break end end '
                                 'if not w then return H:JSONEncode({}) end return H:JSONEncode({ id = w.Name, '
                                 'p = J(w:GetAttribute("Pozycja")) })'),
    "walcz": 'return tostring(workspace.LasPasGra.Sygnaly.SterowanieKlienta:Invoke("walcz", "%s"))',
    "klient_lasu": H + J + 'return H:JSONEncode(J(workspace.LasPasGra.Sygnaly.SterowanieKlienta:Invoke("stan")))',
    "odtw": H + J + 'return H:JSONEncode(J(workspace.TestWalki2.Sygnaly.Sterowanie:Invoke(%s)))',
    # wejście do lasu jak gracz (te same kroki co swiat/przejscie_gry/proba_dymna.py; cudze kontenery tylko czytane)
    "chmury_trwa": ('local k = workspace:FindFirstChild("TeleportChmury") return tostring(k and k:GetAttribute("Trwa"))'),
    "chmury_faza": ('local k = workspace:FindFirstChild("TeleportChmury") local s = k and '
                    'k.Sygnaly.SterowanieKlienta:Invoke("stan") return tostring(s and s.biezacy and s.biezacy.faza)'),
    "postac": H + J + ('local lp = game:GetService("Players").LocalPlayer local hrp = lp.Character and '
                       'lp.Character:FindFirstChild("HumanoidRootPart") local k = workspace:FindFirstChild("LasPasGra") '
                       'local p = k and (k.Sygnaly.SterowaniePasaKlienta:Invoke("stan") or {}).przelot '
                       'return H:JSONEncode({ poz = hrp and J(hrp.Position), kotwica = hrp and hrp.Anchored, '
                       'kamera = workspace.CurrentCamera.CameraType.Name, przelot = p ~= nil and p ~= false, '
                       'walka = k and k.Sygnaly.SterowanieKlienta:Invoke("stan").walka })'),
    "slime": H + J + ('local k = workspace.LasPasGra local hrp = game:GetService("Players").LocalPlayer.Character'
                      '.HumanoidRootPart local best, bd for _, c in k.Stan:GetChildren() do local q = c:GetAttribute('
                      '"Pozycja") if q and c:GetAttribute("Gatunek") == "lesny_slime" and c:GetAttribute("Stan") ~= "zajety" '
                      'then local d = (q - hrp.Position).Magnitude if not bd or d < bd then best, bd = c, d end end end '
                      'return H:JSONEncode(if best then { id = best.Name, p = J(best:GetAttribute("Pozycja")) } else {})'),
    "kamera_za": ('local lp = game:GetService("Players").LocalPlayer local cam = workspace.CurrentCamera '
                  'local h = lp.Character and lp.Character:FindFirstChild("HumanoidRootPart") if h then '
                  'cam.CameraType = Enum.CameraType.Custom task.delay(0.05, function() cam.CFrame = CFrame.lookAt('
                  'h.Position - h.CFrame.LookVector * 10 + Vector3.new(0, 4, 0), h.Position + h.CFrame.LookVector * 4) end) '
                  'end return "ok"'),
    # scena walki jest lokalna i leży w kontenerze, który zgłosił walkę (w lesie: Workspace/LasPasGra, przy tablicy
    # prototypu: Workspace/TestWalki2) — szukamy folderu ScenaLokalna w każdym kontenerze Workspace
    "stroj_w_walce": H + ('local w = {} for _, k in workspace:GetChildren() do local s = k:FindFirstChild("ScenaLokalna") '
                          'if s then for _, m in s:GetDescendants() do if m:IsA("Model") and '
                          'm:GetAttribute("Stroj") ~= nil then table.insert(w, { model = m.Name, stroj = m:GetAttribute("Stroj"), '
                          'kontener = k.Name }) end end end end return H:JSONEncode(w)'),
    "widoczny": ('local o = game:GetService("Players").LocalPlayer.PlayerGui for _, n in string.split("%s", ".") do '
                 'o = o and o:FindFirstChild(n) end if not o then return "false" end local a = o while a and a:IsA("GuiObject") '
                 'do if not a.Visible then return "false" end a = a.Parent end '
                 'return tostring(a and (not a:IsA("ScreenGui") or a.Enabled))'),
    "wskazowka": H + ('local k = workspace:FindFirstChild("WskazowkiGry") if not k then return H:JSONEncode({ brak = true }) end '
                      'local s = k.Sygnaly.SterowanieKlienta:Invoke("stan") return H:JSONEncode({ krok = s.krok, tekst = s.tekst, '
                      'widoczne = s.widoczne, znacznik = s.znacznik, kowal = s.kowal, zapas = s.kowal_zapas, '
                      'ulepszen = s.kowal_ulepszen })'),
    "licz_stanu": H + ('local s = workspace.StanGracza return H:JSONEncode({ bohaterow = s:GetAttribute("LicznikBohaterow"), '
                       'lupow = s:GetAttribute("LicznikLupow") })'),
}
DOMYSLNE = {"hak_serwera": ("lup", '"zwykly"', "0"), "ustaw_atr": ("Gold", "0"), "tokeny": ("TokenyKrainy_las",),
            "przy_kowalu": (0.0, 0.0, 0.0, 1.0, 1.0), "kamera": (0.0, 5.0, 0.0, 1.0, 1.0, 1.0), "klient": ("stan", "nil"),
            "zdalnie": ("widok", "nil"), "emulacja": ("nil",), "stroje": ("zaloz", "wojownik", "nil"),
            "potwor_w_strefie": ("s1",), "walcz": ("x",), "odtw": ('"stan"',), "widoczny": ("HUD.X",)}


def sprawdz_kod():
    import sprawdz_luau_kowala as SLK
    LM = SLK.luau_mini()
    if LM is None:
        print("brak luau_mini — nic do sprawdzenia")
        return 0
    bledy = 0
    for nazwa, szablon in KOD.items():
        kod = szablon % DOMYSLNE[nazwa] if nazwa in DOMYSLNE else szablon
        try:
            LM.Parser(kod, nazwa, LM.Interpreter()).program()
        except LM.BladSkladni as e:
            print("BŁĄD składni %s: %s" % (nazwa, e))
            bledy += 1
    print("proba_play --sprawdz: %d kawałków Luau, %s" % (len(KOD), "OK" if not bledy else "BŁĘDY: %d" % bledy))
    return 1 if bledy else 0


def log(*a):
    print("[%s]" % time.strftime("%H:%M:%S"), *a, flush=True)


def _swiat(D, lok):
    """Punkt w układzie kuźni (przód +Z) → świat."""
    kz = D["kuznia"]
    a = math.radians(kz["ry"])
    s = kz["srodek"]
    return [s[0] + math.cos(a) * lok[0] + math.sin(a) * lok[2], s[1] + lok[1], s[2] - math.sin(a) * lok[0] + math.cos(a) * lok[2]]


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    if "--sprawdz" in argv:
        return sprawdz_kod()
    ap = argparse.ArgumentParser(description="Próba kowala w trybie Play")
    ap.add_argument("--studio", default=None)
    ap.add_argument("--bez-zrzutow", action="store_true")
    ap.add_argument("--tylko", default="")
    a = ap.parse_args(argv)
    tylko = {x.strip() for x in a.tylko.split(",") if x.strip()}
    D = DN.dane_z_przypadkami()[0]
    from sesja_play import SesjaPlay  # noqa: E402  (tylko odczyt: wspólna obsługa Play próby walki)
    from studio_mcp import StudioError, StudioMCP  # noqa: E402
    from cel_studio import wybierz_studio  # noqa: E402

    wyniki, dane = [], {}

    def punkt(kod, ok, opis):
        wyniki.append({"punkt": kod, "wynik": "OK" if ok is True else ("?" if ok is None else "BŁĄD"), "opis": opis})
        log("%s %s — %s" % (kod, "OK" if ok is True else ("?" if ok is None else "BŁĄD"), opis))

    def chce(kod):
        return not tylko or kod in tylko

    # K00 w Edit (przed Play)
    with StudioMCP() as s:
        sid = wybierz_studio(s, a.studio)
        r = s.call("execute_luau", {"code": KOD["edit"], "datamodel_type": "Edit", "studio_id": sid})
        edit = json.loads(r["text"])
    ok0 = edit.get("kowal") and edit.get("skrot") == D["skrot"] and edit.get("mod") and edit.get("dane") and edit.get("wydaj")
    punkt("K00", bool(ok0), "kontenery %s; skrót %s (lokalnie %s)" % (edit, edit.get("skrot"), D["skrot"]))
    if not ok0:
        zapisz(wyniki, dane)
        return 2

    with SesjaPlay(a.studio) as sp:
        def js(kod, dm="Client"):
            return json.loads(sp.luau(kod, dm))

        def czekaj(warunek, limit, co=0.4):
            t0 = time.time()
            while time.time() - t0 < limit:
                try:
                    w = warunek()
                    if w:
                        return w
                except (StudioError, ValueError, KeyError, TypeError):
                    pass
                time.sleep(co)
            return None

        def zrzut(nazwa, kamera=None, patrz=None):
            if a.bez_zrzutow:
                return
            try:
                obraz = sp.zrzut(kamera, patrz) if kamera else sp.zrzut()
                os.makedirs(KLATKI, exist_ok=True)
                obraz.thumbnail((1280, 1280))
                obraz.save(os.path.join(KLATKI, nazwa + ".jpg"), quality=86)
            except StudioError as e:
                log("zrzut %s: %s" % (nazwa, e))

        def gracz():
            return js(KOD["gracz"], "Server")

        def mody():
            return js(KOD["mody"], "Server")

        def hak(polecenie, x="nil", y="nil"):
            return js(KOD["hak_serwera"] % (polecenie, x, y), "Server")

        def klient(polecenie, arg="nil"):
            return js(KOD["klient"] % (polecenie, arg))

        def przy_kowalu(odl=1.5):
            e, kw = D["kuznia"]["e"], D["kuznia"]["kowal"]
            sp.luau(KOD["przy_kowalu"] % (e[0], e[1] + 1.8, e[2] - odl, kw[0], kw[2]), "Server")
            time.sleep(0.6)

        def klik(nazwa):
            return sp.klik("KowalProbaOkno.Ekran.Okno." + nazwa)

        def kamera_za():
            # kamera postaci za plecami (po zrzutach z ustawioną kamerą i po przestawieniu postaci)
            sp.luau(KOD["kamera_za"])
            time.sleep(0.5)

        def okno_pawla():
            return js(KOD["okno_pawla"])

        def zamknij_okno_pawla():
            """Okno kowala Pawła zamykamy jego X (jak gracz): otwarte zostaje po E i jego tło łapie kliknięcia —
            26.11.2026 kliknięcie TELEPORT w K06 trafiało w tło jego okna i chmury się nie otwierały."""
            if okno_pawla().get("wlaczone"):
                sp.klik("OknoKowala.Panel.CloseButton")
                return bool(czekaj(lambda: not okno_pawla().get("wlaczone"), 3, 0.3))
            return None

        def do_lasu():
            """TELEPORT → chmury → strzałka w prawo + Enter = Las, potem koniec przelotu (jak proba_dymna D02)."""
            zamknij_okno_pawla()
            sp.luau(KOD["kamera_zwykla"])
            sp.klik("HUD.LeftColumn.TeleportSlot.Teleport")
            if not czekaj(lambda: sp.luau(KOD["chmury_trwa"]).strip() == "true", 8, 0.5):
                return {"blad": "chmury się nie otworzyły"}
            czekaj(lambda: sp.luau(KOD["chmury_faza"]).strip() == "wybor", 10, 0.3)
            sp.klawisz("Right")
            time.sleep(0.8)
            sp.klawisz("Return")
            w_lesie = czekaj(lambda: (lambda p: p if (p.get("poz") or [0])[0] >= 1066 else None)(js(KOD["postac"])), 12, 0.5)
            if not w_lesie:
                return {"blad": "postać nie doszła do lasu"}
            czekaj(lambda: js(KOD["postac"]).get("przelot"), 8, 0.4)
            gotowe = czekaj(lambda: (lambda p: p if p.get("kamera") == "Custom" and not p.get("kotwica")
                                     and not p.get("przelot") else None)(js(KOD["postac"])), 30, 1.0)
            return {"poz": w_lesie.get("poz"), "po_przelocie": bool(gotowe)}

        def walka_ze_slimem():
            """Prawdziwe E przy najbliższym slime'ie (do 6 prób) → opis bohatera i strój modelu w walce, zrzuty."""
            for _ in range(6):
                c = js(KOD["slime"])
                if not c.get("p"):
                    return {"blad": "brak wolnego slime'a"}
                q = c["p"]
                sp.luau(KOD["przy_kowalu"] % (q[0] - 4, q[1] + 3.2, q[2], q[0], q[2]), "Server")
                kamera_za()
                sp.klawisz("E")
                if czekaj(lambda: js(KOD["postac"]).get("walka"), 5, 0.4):
                    break
            else:
                return {"blad": "E nie ruszyło walki"}
            m = mody()   # opis bohatera z serwera stanu = ten, którym liczono tę walkę (wpis kowala już ustawiony)
            time.sleep(1.5)
            stroje = czekaj(lambda: js(KOD["stroj_w_walce"]) or None, 6, 0.5) or []
            zrzut("k06_walka_w_przedmiotach")
            sp.klik("TestWalki2Cutscenka.Kadr.Tempo.Tempo4.Przycisk")
            sciezka_karty = "TestWalki2Cutscenka.Kadr.Wynik.Karta.Zamknij.Przycisk"
            karta = czekaj(lambda: sp.luau(KOD["widoczny"] % sciezka_karty).strip() == "true", 60, 1.0)
            zrzut("k06_karta_wyniku")
            sp.klik(sciezka_karty)
            czekaj(lambda: js(KOD["postac"]).get("kamera") == "Custom", 10, 0.5)
            return {"bohater": m["bohater"], "mod": m["mod"], "stroje": stroje, "karta": bool(karta)}

        sp.luau(KOD["bez_nazwy"])
        time.sleep(1.0)
        # ------------------------------------------------------------------ K01
        if chce("K01"):
            cl = czekaj(lambda: (lambda w: w if w.get("gotowy") and w.get("animowany") else None)(js(KOD["atr_klienta"])), 30)
            sv = js(KOD["atr_kowala"], "Server")
            n = sum(len(v) for v in D["przypadki"].values())
            ok = (bool(cl) and sv.get("SerwerKowalaGotowy") and str(sv.get("ZgodnoscLogikiKowala")).startswith("OK")
                  and sv.get("PodpowiedziWlaczone") == 1 and sv.get("StanGraczaPodlaczony") and sv.get("SkrotSerwera") == D["skrot"])
            punkt("K01", bool(ok), "klient %s; serwer %s (przypadków w danych %d)" % (cl, sv, n))
        # ------------------------------------------------------------------ K02
        g0 = gracz()
        if chce("K02"):
            m = mody()
            k = g0["klasa"]
            podst = [p for p in D["kolejnosc"] if p in D["klasy"][k]["podstawowe"]]
            L = g0.get("poziom") or 1
            b = m["bohater"]
            ok = (g0.get("dostepne") == ",".join(podst) and g0.get("stroj") is not None and "kowal" in m["mod"].get("zrodla", [])
                  and abs(b["bron"]["obrazenia"] - (8 + 4 * L)) < 1e-6)
            punkt("K02", bool(ok), "klasa %s, dostępne %s, strój %s, źródła %s, broń %s / pancerz %s (wzór L%d: %d / %.1f)"
                  % (k, g0.get("dostepne"), g0.get("stroj"), m["mod"].get("zrodla"), b["bron"]["obrazenia"],
                     b.get("pancerz_przedmiotow"), L, 8 + 4 * L, 3 + 1.5 * L))
            dane["K02"] = {"gracz": g0, "mody": m}
        # ------------------------------------------------------------------ K03 kuźnia z kilku stron
        if chce("K03"):
            cel = _swiat(D, (0.0, 3.0, 0.0))
            ujecia = [("k03_kuznia_przod", (0.0, 7.0, 17.0)), ("k03_kuznia_lewo", (-13.0, 8.0, 12.0)),
                      ("k03_kuznia_prawo", (13.0, 8.0, 12.0)), ("k03_kuznia_z_gory", (0.5, 22.0, 13.0))]
            for nazwa, lok in ujecia:
                zrzut(nazwa, _swiat(D, lok), cel)
            uk = DN._json(os.path.join(DN.BAZAR, "uklad.json"))["swiat"]
            zrzut("k03_kuznia_od_zbrojowni", [uk["X0"] + 50.5, 6.5, uk["Z0"] - 12.0], cel)
            kw = D["kuznia"]["kowal"]
            zrzut("k03_kowal_przy_kowadle", _swiat(D, (-1.5, 4.6, 6.0)), [kw[0], kw[1] + 2.6, kw[2]])
            sp.luau(KOD["kamera_zwykla"])
            punkt("K03", None if a.bez_zrzutow else True, "zrzuty kuźni z %d stron i kowala przy kowadle → klatki/" % (len(ujecia) + 1))
        # ------------------------------------------------------------------ K04 prawdziwe E
        if chce("K04"):
            przy_kowalu()
            kamera_za()
            n_klasy = len(D["klasy"][g0["klasa"]]["przedmioty"])
            if okno_pawla().get("jest"):
                # 26.11.2026: okno kowala Pawła (24.11, ab56560; zakładki 641e578) zastąpiło okno próbne — E otwiera jego
                # okno i tylko ono; jego treść to widok z naszego serwera (Zdalne/Kuznia "widok"), więc liczbę
                # przedmiotów klasy sprawdzamy w widoku serwera. Okno zamykamy jego X (inaczej łapie kliknięcia dalej).
                sp.klawisz("E")
                ok = czekaj(lambda: okno_pawla().get("wlaczone"), 6)
                time.sleep(0.8)
                op = okno_pawla()
                kl = js(KOD["atr_klienta"])
                w = js(KOD["zdalnie"] % ("widok", "nil"))
                n_widok = len(((w.get("widok") or {}).get("wiersze")) or [])
                zrzut("k04_okno_kowala")
                zamkniete = zamknij_okno_pawla()
                punkt("K04", bool(ok) and not op.get("proba") and not kl.get("okno") and kl.get("zastapione") == "OknoKowala"
                      and n_widok == n_klasy and zamkniete is True,
                      "okno Pawła po E %s, okno próbne %s (OknoZastapione %s), wierszy w widoku serwera %s (klasa ma %d), "
                      "zamknięte jego X: %s" % (ok, op.get("proba") or kl.get("okno"), kl.get("zastapione"), n_widok, n_klasy, zamkniete))
            else:
                sp.klawisz("E")
                ok = czekaj(lambda: js(KOD["atr_klienta"]).get("okno"), 6)
                st = czekaj(lambda: (lambda w: w if w.get("wiersze", 0) > 0 else None)(klient("stan")), 6) or {}
                zrzut("k04_okno_kowala")
                punkt("K04", bool(ok) and st.get("wiersze", 0) == n_klasy,
                      "okno %s, wierszy %s (klasa ma %d przedmiotów)" % (ok, st.get("wiersze"), n_klasy))
        # ------------------------------------------------------------------ K05 łup
        k = g0["klasa"]
        lista = D["klasy"][k]["przedmioty"]
        nowy = next(p for p in lista if not D["przedmioty"][p]["podstawowy"])
        if chce("K05"):
            i = lista.index(nowy)
            w = hak("lup", '"zwykly"', "%.4f" % ((i + 0.5) / len(lista)))
            g1 = gracz()
            napis = czekaj(lambda: js(KOD["atr_klienta"]).get("napis"), 5)
            kamera_za()
            zrzut("k05_lup_nowy_przedmiot")
            ok1 = w.get("ok") and nowy in (g1.get("dostepne") or "").split(",") and nowy in (g1.get("stroj") or "").split(",")
            sv0 = js(KOD["atr_kowala"], "Server").get("LicznikLupow") or 0
            tok = "TokenyKrainy_las"
            ile = 0
            for ile in range(1, D["lup"]["ochrona"] + 2):
                t = js(KOD["tokeny"] % tok, "Server")["t"]
                sp.luau(KOD["ustaw_atr"] % (tok, str(t + 1)), "Server")
                time.sleep(0.4)
                if (js(KOD["atr_kowala"], "Server").get("LicznikLupow") or 0) > sv0:
                    break
            ok2 = (js(KOD["atr_kowala"], "Server").get("LicznikLupow") or 0) > sv0
            punkt("K05", bool(ok1 and ok2 and napis), "haczyk: %s, napis „%s”; prawdziwa droga: przedmiot po %d wygranych"
                  " (przyrost tokenów)" % (w, napis, ile))
        # ------------------------------------------------------------------ K06 walka z nowymi liczbami
        if chce("K06"):
            st = js(KOD["stan_kowala"], "Server")
            m = mody()
            oczek = LK.mod(D, k, LK.czyste(D, st["dane"]), st["zalozone"])
            wpis_ok = all(abs((m["mod"].get(p) or 0) - oczek.get(p, 0)) < 1e-6 for p in ("bron", "pancerz"))
            z_lupu = [p for p in st["zalozone"] if not D["przedmioty"][p]["podstawowy"]]
            wynik = {"wpis": wpis_ok, "z_lupu": z_lupu}
            L = gracz().get("poziom") or 1          # poziom przed walką (opis bohatera brany na jej starcie)
            if edit.get("las"):
                wynik["las"] = do_lasu()
                if not wynik["las"].get("blad"):
                    wynik["walka"] = walka_ze_slimem()
            dane["K06"] = wynik
            wk = wynik.get("walka") or {}
            b = wk.get("bohater") or {}
            bron_ok = abs((b.get("bron") or {}).get("obrazenia", -1) - (8 + 4 * L + oczek.get("bron", 0))) < 1e-6
            panc_ok = abs((b.get("pancerz_przedmiotow") or -1) - (3 + 1.5 * L + oczek.get("pancerz", 0))) < 1e-6
            w_stroju = any(all(p in (x.get("stroj") or "").split(",") for p in z_lupu) for x in wk.get("stroje") or [])
            ok = wpis_ok and bool(z_lupu) and bron_ok and panc_ok and w_stroju and wk.get("karta")
            punkt("K06", bool(ok) if edit.get("las") else (None if wpis_ok else False),
                  "wpis kowala %s (oczekiwany %s); przedmioty z łupu na sobie %s; las %s; w walce broń %s / pancerz %s "
                  "(wzór L%d + przedmioty: %s / %s), modele w stroju %s, karta wyniku %s"
                  % (m["mod"], oczek, z_lupu, wynik.get("las"), (b.get("bron") or {}).get("obrazenia"),
                     b.get("pancerz_przedmiotow"), L, 8 + 4 * L + oczek.get("bron", 0), 3 + 1.5 * L + oczek.get("pancerz", 0),
                     wk.get("stroje"), wk.get("karta")))
        # ------------------------------------------------------------------ K07 rozbiórka prawdziwym kliknięciem
        if chce("K07"):
            podst = D["klasy"][k]["podstawowe"][0]
            hak("lup", '"zwykly"', "%.4f" % ((lista.index(podst) + 0.5) / len(lista)))
            przy_kowalu()
            # wskazówka celu „kowal” (swiat/wskazowki_gry, krok g): po wygranej (K06), z zapasem, przed 1. ulepszeniem
            kamera_za()
            wsk = czekaj(lambda: (lambda w: w if w.get("krok") or w.get("brak") else None)(js(KOD["wskazowka"])), 4) or {}
            dane["K07_wskazowka"] = wsk
            if not wsk.get("brak"):
                zrzut("k07a_wskazowka_kowal")
            klient("zamknij")
            klient("otworz")
            time.sleep(1.0)
            m0 = gracz().get("materialy") or 0
            klik("Lista.Przedmiot_" + podst)
            time.sleep(0.5)
            klik("Szczegoly.Rozbierz")
            ok = czekaj(lambda: (gracz().get("materialy") or 0) == m0 + D["rozbiorka"]["materialy"], 5)
            zrzut("k07_rozbiorka")
            wsk_ok = wsk.get("brak") or (wsk.get("krok") == "g_kowal_zapas" and wsk.get("znacznik"))
            punkt("K07", bool(ok) and bool(wsk_ok), "materiały %s → %s (zapas %s); wskazówka %s „%s”, znacznik %s"
                  % (m0, gracz().get("materialy"), podst, wsk.get("krok") or ("brak pakietu" if wsk.get("brak") else None),
                     wsk.get("tekst"), wsk.get("znacznik")))
        # ------------------------------------------------------------------ K08 ulepszenie prawdziwym kliknięciem
        if chce("K08"):
            pid = D["klasy"][k]["podstawowe"][0]
            st = js(KOD["stan_kowala"], "Server")
            poz = st["dane"]["przedmioty"][pid]["poziom"]
            kosz = LK.koszt(D, pid, poz)
            hak("materialy", str(kosz["materialy"] + 2))
            sp.luau(KOD["ustaw_atr"] % ("Gold", str(kosz["zloto"] + 50)), "Server")
            przy_kowalu()
            klient("zamknij")
            klient("otworz")
            time.sleep(1.0)
            klik("Lista.Przedmiot_" + pid)
            time.sleep(0.6)
            zrzut("k08a_przed_ulepszeniem")
            klik("Szczegoly.Ulepsz")
            ok = czekaj(lambda: js(KOD["stan_kowala"], "Server")["dane"]["przedmioty"][pid]["poziom"] == poz + 1, 6)
            klip = czekaj(lambda: klient("stan").get("klip") == D["kowal"]["klipRadosci"], 3, 0.2)
            time.sleep(0.4)
            zrzut("k08b_po_ulepszeniu")
            g8 = gracz()
            punkt("K08", bool(ok) and g8.get("zloto") == 50 and g8.get("materialy") == 2,
                  "%s +%d → +%s; Złoto %s (oczekiwane 50), materiały %s (oczekiwane 2), klip radości %s"
                  % (pid, poz, poz + 1 if ok else "?", g8.get("zloto"), g8.get("materialy"), bool(klip)))
        # ------------------------------------------------------------------ K09 odmowy serwera
        if chce("K09"):
            pid = D["klasy"][k]["podstawowe"][0]
            przy_kowalu()
            sp.luau(KOD["ustaw_atr"] % ("Gold", "0"), "Server")
            hak("materialy", "20")
            time.sleep(0.4)
            r1 = js(KOD["zdalnie"] % ("ulepsz", json.dumps(pid)))
            time.sleep(0.4)
            hak("materialy", "0")
            sp.luau(KOD["ustaw_atr"] % ("Gold", "5000"), "Server")
            time.sleep(0.4)
            r2 = js(KOD["zdalnie"] % ("ulepsz", json.dumps(pid)))
            time.sleep(0.4)
            r3 = js(KOD["zdalnie"] % ("rozbierz", '"kot_mag_kostur"' if k != "mag" else '"rycerz_miecz"'))
            sp.luau(KOD["przy_kowalu"] % (D["kuznia"]["e"][0] + 40, 5, D["kuznia"]["e"][2], 0, 0), "Server")
            time.sleep(0.6)
            r4 = js(KOD["zdalnie"] % ("ulepsz", json.dumps(pid)))
            g9 = gracz()
            ok = (r1.get("powod") == "za_malo_zlota" and r2.get("powod") == "za_malo_materialow"
                  and r3.get("powod") == "nieznany_przedmiot" and r4.get("powod") == "daleko" and g9.get("zloto") == 5000)
            punkt("K09", bool(ok), "za mało Złota: %s; za mało materiałów: %s; obcy przedmiot: %s; daleko: %s; Złoto %s"
                  % (r1.get("tekst"), r2.get("tekst"), r3.get("powod"), r4.get("powod"), g9.get("zloto")))
        # ------------------------------------------------------------------ K10 reset postaci
        if chce("K10"):
            przed = js(KOD["stan_kowala"], "Server")
            sp.luau(KOD["reset"], "Server")
            czekaj(lambda: sp.luau(KOD["postac_gotowa"]).strip() == "true", 20, 0.5)
            time.sleep(1.5)
            po = js(KOD["stan_kowala"], "Server")
            m = mody()
            przy_kowalu()
            klient("zamknij")
            klient("otworz")
            okno = czekaj(lambda: klient("stan").get("wiersze", 0) > 0, 6)
            ok = przed.get("dane") == po.get("dane") and "kowal" in m["mod"].get("zrodla", []) and bool(okno)
            punkt("K10", bool(ok), "przedmioty i materiały bez zmian: %s; wpis kowala: %s; okno: %s"
                  % (przed.get("dane") == po.get("dane"), "kowal" in m["mod"].get("zrodla", []), bool(okno)))
        # ------------------------------------------------------------------ K11 przymierzalnia
        if chce("K11") and edit.get("stroje"):
            nieposiadany = next((p for p in lista if p not in (gracz().get("dostepne") or "").split(",")), None)
            r1 = js(KOD["stroje"] % ("zaloz", k, json.dumps(nieposiadany))) if nieposiadany else {"powod": "wszystko_posiadane"}
            time.sleep(0.3)
            r2 = js(KOD["stroje"] % ("dawny", k, "nil"))
            punkt("K11", r1.get("powod") in ("nie_masz", "wszystko_posiadane") and r2.get("powod") == "dawny_niedostepny",
                  "nieposiadany %s: %s; dawny wygląd: %s" % (nieposiadany, r1.get("powod"), r2.get("powod")))
        # ------------------------------------------------------------------ K12 mały ekran
        if chce("K12"):
            przy_kowalu()
            klient("zamknij")
            sp.luau(KOD["emulacja"] % "Vector2.new(667, 375)")
            klient("otworz")
            time.sleep(1.2)
            st = klient("stan")
            geo = js(KOD["okno_geometria"])
            zrzut("k12_okno_maly_ekran")
            sp.luau(KOD["emulacja"] % "nil")
            klient("zamknij")
            ok12 = (st.get("rozmiarTekstu") or 0) >= 12 and geo.get("dol", 2) <= 1.0
            if okno_pawla().get("jest"):
                # okno próbne nie pokazuje się już graczowi (zastąpione oknem Pawła) — wynik nie mówi nic o grze
                punkt("K12", None if ok12 else False, "okno zastąpione przez okno Pawła — okno próbne na małym ekranie: "
                      "tekst %s pt, okno %s; okna Pawła na telefonie ta próba nie mierzy" % (st.get("rozmiarTekstu"), geo))
            else:
                punkt("K12", ok12, "tekst %s pt, okno %s" % (st.get("rozmiarTekstu"), geo))
        # ------------------------------------------------------------------ K13 konsola
        if chce("K13"):
            kons = sp.konsola()
            zle = [w for w in kons.splitlines() if "[KowalProba]" in w or "KowalProba." in w]
            punkt("K13", not zle, "wiersze konsoli o kowalu: %d%s" % (len(zle), (" — " + " | ".join(zle[:5])) if zle else ""))
    zapisz(wyniki, dane)
    zle = [w for w in wyniki if w["wynik"] == "BŁĄD"]
    log("koniec: %d OK, %d ?, %d BŁĄD" % (sum(w["wynik"] == "OK" for w in wyniki), sum(w["wynik"] == "?" for w in wyniki),
                                          len(zle)))
    return 1 if zle else 0


def zapisz(wyniki, dane):
    with open(WYNIK, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"czas": time.strftime("%Y-%m-%d %H:%M"), "punkty": wyniki, "dane": dane}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
