# -*- coding: utf-8 -*-
"""Próba Training Center (mini-gry Siła i Pancerz) w Roblox Studio, tryb Play — do etapu B (jeszcze nieuruchomiona).

    python -B swiat/trening_proba/testy/proba_play.py <folder wyjściowy poza repo> [--studio <studio_id>]
           [--bez-zrzutow] [--tylko T01,T05,…]

Warunki: Studio w trybie Edit, otwarte miejsce gry (placeId sprawdza cel_studio), zbudowane Workspace/TreningProba
(python -B swiat/trening_proba/zbuduj.py); najlepiej też MiasteczkoBazar + MiasteczkoBazarGra (T03 z prawdziwym E przy
trenerze — bez nich T03 sprawdza tylko zdarzenie OknoMiejsca). Skrypt sam włącza i wyłącza Play, w trybie Play
zmienia tylko stan gracza (położenie postaci, kamera testu) i używa haczyków pakietu; niczego nie zapisuje w miejscu
i niczego nie publikuje. Wyniki: <wyj>/wyniki.json, lista kontrolna na ekranie i w <wyj>/lista.txt, zrzuty
<wyj>/<nazwa>.jpg (tylko zrzuty, bez filmów). Nazwa konta w zapisach zamieniana na <gracz> (repo jest publiczne).

LISTA KONTROLNA (każdy punkt kończy się OK / BŁĄD / ? w liście):
  T01 gotowość: SerwerTreninguGotowy, ZgodnoscLogikiTreningu „OK n/n”, Podpowiedzi = 3, KlientTreninguGotowy,
      6 kafelków wyboru (2 grywalne), zdarzenie OknoMiejsca podpięte
  T02 tablica wejścia, prawdziwe E: postać przed TablicaWejscia twarzą do niej → tymczasowy wybór na ekranie
      (zrodlo = "tablica"), dymek bazaru nie jest potrzebny
  T03 E przy trenerze w bazarze: zdarzenie OknoMiejsca("training_center") → wybór (zrodlo = "bazar"); gdy stoi
      MiasteczkoBazarGra — prawdziwe E przy trenerze, wybór otwarty, dymek „Trener: mini-gry w budowie” NIE pokazany
  T04 wejście do Siły prawdziwym kliknięciem GRAJ: postać na podeście (≤ 1,5 st), TreningGra = "sila", kamera
      Scriptable, sterowanie dotykowe wyłączone, punkt powrotu = miejsce przy tablicy
  T05 runda Siły grana bezbłędnie (autograj 1,0): trafienia = liczba zdarzeń, pudła 0, jednostki paska = Σ przyrost(1..n),
      punkty = pasek z malejącym zyskiem (logika_treningu.punkty_za_serie, W = punkty sesji, pula z atrybutu Level),
      atrybut TreningSila = punkty, sygnał PrzyrostStatystyki tyle razy, ile trafień dało punkt; rozbieżności 0
  T06 prawdziwe klawisze w rundzie: strzałki / WASD / spacja docierają do serwera jako zgłoszenia, a postać się nie
      rusza (ruch pochłonięty) — przesunięcie < 0,5 st
  T07 spam: 60 zgłoszeń naraz → serwer odrzuca ≥ 50 jako spam, jednostki paska ze spamu ≤ 8
  T08 werdykty: zaplanowane naciśnięcia — dobre (T), zły kierunek (zly_kierunek), za wcześnie (za_wczesnie),
      brak (przepuszczone), podwójne (drugie pominięte jako dubel — seria nie spada)
  T09 Pancerz przez INNA GRA: bloki na każdy cios i JEDEN blok na zmyłkę → pudła = 1 (zmyłka), reszta trafienia;
      TreningPancerz = suma rundy
  T10 podsumowanie i JESZCZE RAZ: po rundzie panel podsumowania; prawdziwa spacja startuje nową rundę
  T11 wyjście przyciskiem WYJDŹ (prawdziwe kliknięcie): postać ≤ 1,5 st od punktu sprzed wejścia, kamera Custom,
      sterowanie dotykowe przywrócone, klawisz W znów porusza postacią; brama WYJŚCIE (E) w arenie bez punktu powrotu
      → miejsce startu
  T12 telefon: przyciski ≥ 44 px i teksty ≥ 12 pt przy 667 × 375 i 568 × 320 (skala z logiki), najmniejszy przycisk
      na obecnym ekranie; (ręcznie: emulator telefonu w poziomie — czy krzyż nie zasłania skrzynek)
  T13 czas klatki: RenderStepped 6 s w rundzie Siły (średnio, p95) — przy zaciemnionym oknie Studio „?”
  T14 konsola: bez błędów z [TreningProba] i bez „error” ze skryptów pakietu
  (ręcznie, poza skryptem: dźwięki na słuch; dwóch graczy (Test → Clients and Servers, 2) — każdy widzi tylko swoje
   skrzynki; pad — krzyż przycisków ABXY)

ZRZUTY (w <wyj>): 01_wybor_tymczasowy, 02_stanowisko_sila, 03_runda_sila, 04_runda_pancerz, 05_podsumowanie,
  06_tablica_wejscia.
"""
import io
import json
import math
import os
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))

KP = 'local k = workspace:FindFirstChild("TreningProba") local H = game:GetService("HttpService") '
J = ('local function J(v) local t = typeof(v) if t == "Vector3" then return { v.X, v.Y, v.Z } '
     'elseif t == "CFrame" then return { v.X, v.Y, v.Z } '
     'elseif t == "table" then local o = {} if #v > 0 then for i, b in ipairs(v) do o[i] = J(b) end '
     'else for a, b in v do o[tostring(a)] = J(b) end end return o '
     'elseif t == "number" and (v ~= v or v == math.huge or v == -math.huge) then return tostring(v) '
     'elseif t == "Instance" then return v:GetFullName() elseif t == "EnumItem" then return v.Name end return v end ')
GR = 'local gracz = game:GetService("Players"):GetPlayers()[1] '
HRP = GR + 'local hrp = gracz.Character and gracz.Character:FindFirstChild("HumanoidRootPart") '
WYNIKI = {}
LISTA = []


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def odl_xz(a, b):
    return math.hypot(a[0] - b[0], a[2] - b[2])


def main():
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    if os.path.commonpath([wyj, REPO]) == REPO:
        sys.exit("Folder wyjściowy ma być poza repozytorium (zrzuty nie trafiają do git): %s" % wyj)
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    bez_zrzutow = "--bez-zrzutow" in argv
    tylko = set(argv[argv.index("--tylko") + 1].split(",")) if "--tylko" in argv else None
    os.makedirs(wyj, exist_ok=True)

    sys.path.insert(0, PAKIET)
    import dane as DANE  # noqa: E402
    import logika_treningu as LT  # noqa: E402
    _, D = DANE.dane_z_przypadkami()

    for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"),
               os.path.join(REPO, "swiat", "test_walki2", "testy")):
        sys.path.insert(0, _s)
    from cel_studio import wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    try:
        from czuwanie import nie_usypiaj  # noqa: E402
    except ImportError:
        def nie_usypiaj():
            return False
    try:
        from PIL import Image  # noqa: E402
    except ImportError:
        Image = None

    nazwa_gracza = [None]

    def anonim(v):
        tekst = json.dumps(v, ensure_ascii=False)
        if nazwa_gracza[0]:
            tekst = tekst.replace(nazwa_gracza[0], "<gracz>")
        return json.loads(tekst)

    def zapisz(klucz, wartosc):
        WYNIKI[klucz] = anonim(wartosc)
        with open(os.path.join(wyj, "wyniki.json"), "w", encoding="utf-8") as f:
            json.dump(WYNIKI, f, ensure_ascii=False, indent=1)

    def punkt(kod, ok, opis):
        opis = anonim(opis) if isinstance(opis, str) else opis
        LISTA.append((kod, "OK" if ok is True else ("BŁĄD" if ok is False else "?"), opis))
        log("%s %s — %s" % (kod, LISTA[-1][1], opis))
        with open(os.path.join(wyj, "lista.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join("%s %-4s %s" % x for x in LISTA) + "\n")

    def chce(kod):
        return tylko is None or kod in tylko

    with StudioMCP(timeout=180) as s:
        sid = wybierz_studio(s, studio)

        def call(n, a=None, timeout=None):
            d = dict(a or {})
            d["studio_id"] = sid
            return s.call(n, d, timeout=timeout)

        def luau(kod, dm, proby=3):
            for i in range(proby):
                try:
                    r = call("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=120)
                    if r["is_error"]:
                        raise StudioError(r["text"][:800])
                    return r["text"].strip()
                except Exception as e:  # noqa: BLE001 — Studio czasem chwilę nie odpowiada
                    if i == proby - 1:
                        raise
                    log("luau: ponawiam po błędzie:", str(e)[:200])
                    time.sleep(8)

        def js(kod, dm):
            return json.loads(luau(KP + J + kod, dm))

        def stan_studio():
            return call("get_studio_state")["text"]

        def zrzut(nazwa):
            if bez_zrzutow:
                return
            nie_usypiaj()
            r = call("screen_capture", {"capture_id": "trening_" + nazwa}, timeout=150)
            if r["is_error"] or not r.get("images"):
                log("zrzut %s: BŁĄD %s" % (nazwa, r["text"][:120]))
                return
            dane = r["images"][0]
            if Image is not None:
                im = Image.open(io.BytesIO(dane)).convert("RGB")
                if im.width > 1280:
                    im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
                im.save(os.path.join(wyj, nazwa + ".jpg"), "JPEG", quality=85)
            else:
                with open(os.path.join(wyj, nazwa + ".png"), "wb") as f:
                    f.write(dane)
            log("zrzut", nazwa)

        def atrybuty(nazwy, dm="Server"):
            w = js('local o = {} if not k then return H:JSONEncode({ brak = true }) end '
                   'for _, n in { %s } do o[n] = J(k:GetAttribute(n)) end return H:JSONEncode(o)'
                   % ", ".join('"%s"' % n for n in nazwy), dm)
            return w if isinstance(w, dict) else {}

        def hak(polecenie, *argi, dm="Server"):
            nazwa = "SterowanieSerwera" if dm == "Server" else "SterowanieKlienta"
            a = ", ".join("nil" if x is None else lua(x) for x in argi)
            return js('return H:JSONEncode(J(k.Sygnaly.%s:Invoke("%s"%s)))' % (nazwa, polecenie, (", " + a) if a else ""), dm)

        def lua(x):
            if isinstance(x, bool):
                return "true" if x else "false"
            if isinstance(x, (int, float)):
                return repr(x)
            if isinstance(x, str):
                return '"' + x.replace("\\", "\\\\").replace('"', '\\"') + '"'
            if isinstance(x, list):
                return "{ " + ", ".join(lua(v) for v in x) + " }"
            if isinstance(x, dict):
                return "{ " + ", ".join("%s = %s" % (k2, lua(v)) for k2, v in x.items()) + " }"
            return "nil"

        def klient():
            return hak("stan", dm="Client")

        def serwer_gracza():
            st = hak("stan")
            g = (st.get("gracze") or {}) if isinstance(st, dict) else {}
            return next(iter(g.values()), {}) if g else {}

        def czekaj_na(warunek, limit, co=0.5):
            t0 = time.time()
            while time.time() - t0 < limit:
                w = warunek()
                if w:
                    return w
                time.sleep(co)
            return None

        def poz():
            return js(HRP + 'return H:JSONEncode(J(if hrp then hrp.Position else nil))', "Server")

        def przestaw(p, patrz):
            luau(HRP + 'if hrp then local p = Vector3.new(%r, %r, %r) local q = Vector3.new(%r, p.Y, %r) '
                 'gracz.Character:PivotTo(CFrame.lookAt(p, q)) hrp.AssemblyLinearVelocity = Vector3.zero end return "ok"'
                 % (p[0], p[1], p[2], patrz[0], patrz[2]), "Server")

        def kamera_za():
            luau('local cam = workspace.CurrentCamera local p = game:GetService("Players").LocalPlayer '
                 'local h = p.Character and p.Character:FindFirstChild("HumanoidRootPart") if h then '
                 'cam.CameraType = Enum.CameraType.Custom cam.CFrame = CFrame.lookAt(h.Position - h.CFrame.LookVector * 10 '
                 '+ Vector3.new(0, 4, 0), h.Position + h.CFrame.LookVector * 4) end return "ok"', "Client")

        def klawisz(kod):
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": kod}]})

        def klik(sciezka_gui):
            call("user_mouse_input", {"datamodel_type": "Client", "actions": [
                # panele siedzą w ramce „Ekran” (korzeń emulacji ekranu telefonu) — bez niej kliknięcie nie trafiało
                # i próba przechodziła na haczyk (przejście gry 17.11.2026)
                {"action": "moveTo", "instance_path": "LocalPlayer.PlayerGui.TreningProba.Ekran." + sciezka_gui},
                {"action": "mouseButtonClick", "mouse_button": "left"}]})

        def czekaj_na_koniec_rundy(limit=None):
            limit = limit or D["runda"]["dlugosc_s"] + D["runda"]["odliczanie_s"] + 8
            return czekaj_na(lambda: klient().get("ekran") == "podsumowanie" and klient(), limit, 1.0)

        def start_rundy():
            hak("start", dm="Client")
            k0 = czekaj_na(lambda: (lambda c: c if c.get("ekran") == "runda" and c.get("runda") else None)(klient()), 10, 0.3)
            return k0

        # ---------------------------------------------------------------- Edit: kontener stoi?
        edit = js('return H:JSONEncode({ kontener = k ~= nil, wygenerowane = k and k:GetAttribute("Wygenerowane"), '
                  'bazar = workspace:FindFirstChild("%s") ~= nil, punkt = k and J(k:GetAttribute("PunktTablicy")) })'
                  % D["bazar"]["kontener"], "Edit")
        zapisz("edit", edit)
        if not edit.get("kontener"):
            sys.exit("Brak Workspace/TreningProba w trybie Edit — najpierw python -B swiat/trening_proba/zbuduj.py")

        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        try:
            czekaj_na(lambda: "Client" in stan_studio() and luau(
                'local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)', "Client") == "true", 90, 1)
            nazwa_gracza[0] = luau('return game:GetService("Players").LocalPlayer.Name', "Client")
            time.sleep(2)
            # ekran wyboru klasy (src/client/ClassSelectClient) trzyma kamerę skryptową i wyłącza podpowiedzi E —
            # Enter wybiera klasę jak gracz (tak samo robią próby lasu-pasa)
            wybor_klasy = {}
            for _ in range(20):
                wybor_klasy = js('local p = game:GetService("Players").LocalPlayer local g = p.PlayerGui:FindFirstChild("ClassSelect") '
                                 'local c = workspace.CurrentCamera return H:JSONEncode({ ekran = g ~= nil and g.Enabled, '
                                 'kamera = c.CameraType.Name, podpowiedzi = game:GetService("ProximityPromptService").Enabled })', "Client")
                if not wybor_klasy["ekran"] and wybor_klasy["kamera"] == "Custom" and wybor_klasy["podpowiedzi"]:
                    break
                klawisz("Return")
                time.sleep(1.5)
            zapisz("wybor_klasy", wybor_klasy)
            log("wybór klasy:", wybor_klasy)
            # słuchacz sygnału PrzyrostStatystyki (tylko na czas próby, w pamięci serwera)
            luau(KP + 'local n = 0 k.Sygnaly.PrzyrostStatystyki.Event:Connect(function(g, p) n += 1 '
                 'k:SetAttribute("ProbaSygnaly", n) k:SetAttribute("ProbaOstatniSygnal", H:JSONEncode(p)) end) return "ok"', "Server")

            # ---------------------------------------------------------------- T01 gotowość
            at = atrybuty(["SerwerTreninguGotowy", "ZgodnoscLogikiTreningu", "Podpowiedzi"])
            kl = klient()
            klg = atrybuty(["KlientTreninguGotowy"], "Client")
            zapisz("T01", {"serwer": at, "klient": kl, "klient_atr": klg})
            ok = (at.get("SerwerTreninguGotowy") is True and str(at.get("ZgodnoscLogikiTreningu", "")).startswith("OK")
                  and at.get("Podpowiedzi") == 3 and klg.get("KlientTreninguGotowy") is True
                  and kl.get("kafelki") == 6 and kl.get("grywalne") == 2 and (kl.get("zdarzeniaOkien") or 0) >= 1)
            punkt("T01", ok, "%s, podpowiedzi %s, kafelki %s/%s, zdarzeń OknoMiejsca %s" % (
                at.get("ZgodnoscLogikiTreningu"), at.get("Podpowiedzi"), kl.get("grywalne"), kl.get("kafelki"), kl.get("zdarzeniaOkien")))

            # ---------------------------------------------------------------- T02 tablica wejścia (prawdziwe E)
            tab = js('local e = k:FindFirstChild("TablicaWejscia") e = e and e:FindFirstChild("E") '
                     'return H:JSONEncode(if e then { p = J(e.Position), przod = J(e.CFrame.LookVector) } else {})', "Server")
            P0 = None
            if tab.get("p"):
                p, f = tab["p"], tab["przod"]
                stoisko = [p[0] + f[0] * 4, p[1] + 0.5, p[2] + f[2] * 4]
                przestaw(stoisko, p)
                time.sleep(1.2)
                kamera_za()
                time.sleep(0.5)
                P0 = poz()
                zrzut("06_tablica_wejscia")
                klawisz("E")
                kl = czekaj_na(lambda: (lambda c: c if c.get("wybor") else None)(klient()), 4, 0.3) or klient()
                zapisz("T02", {"tablica": tab, "klient": kl})
                punkt("T02", kl.get("wybor") is True and kl.get("zrodlo") == "tablica",
                      "wybór %s, źródło %s, tablica w (%.1f; %.1f; %.1f)" % (kl.get("wybor"), kl.get("zrodlo"), p[0], p[1], p[2]))
                zrzut("01_wybor_tymczasowy")
            else:
                punkt("T02", False, "brak TablicaWejscia/E")

            # ---------------------------------------------------------------- T03 E przy trenerze (OknoMiejsca)
            if chce("T03"):
                hak("zamknij", dm="Client")
                hak("okno", dm="Client")
                kl = klient()
                wynik3 = {"zdarzenie": {"wybor": kl.get("wybor"), "zrodlo": kl.get("zrodlo")}}
                ok3 = kl.get("wybor") is True and kl.get("zrodlo") == "bazar"
                if edit.get("bazar"):
                    hak("zamknij", dm="Client")
                    zn = DANE._czytaj_json(DANE.ZNACZNIKI)["training_center"]
                    przestaw([zn["stoisko"][0], zn["stoisko"][1] + 3.2, zn["stoisko"][2]], zn["podpowiedz"])
                    time.sleep(1.5)
                    kamera_za()
                    time.sleep(0.4)
                    klawisz("E")
                    time.sleep(1.2)
                    kl = klient()
                    bz = js('local b = workspace:FindFirstChild("%s") local s = b and b.Sygnaly.SterowanieKlienta:Invoke("stan") '
                            'return H:JSONEncode(J(s))' % D["bazar"]["kontener"], "Client")
                    hist = bz.get("historia") if isinstance(bz, dict) else None
                    ost = hist[-1] if isinstance(hist, list) and hist else {}
                    wynik3["bazar"] = {"wybor": kl.get("wybor"), "zrodlo": kl.get("zrodlo"), "historia_bazaru": ost}
                    ok3 = ok3 and kl.get("wybor") is True and kl.get("zrodlo") == "bazar" and not ost.get("dymek")
                zapisz("T03", wynik3)
                punkt("T03", ok3, json.dumps(wynik3, ensure_ascii=False)[:220])
                if P0 is not None and tab.get("p"):
                    przestaw([P0[0], P0[1], P0[2]], tab["p"])
                    time.sleep(1.0)
                    P0 = poz()

            # ---------------------------------------------------------------- T04 wejście do Siły (kliknięcie GRAJ)
            hak("wybor", "test", dm="Client")
            time.sleep(0.5)
            klik("Wybor.Kafelek_sila.Graj")
            sg = czekaj_na(lambda: (lambda g: g if g.get("gra") == "sila" else None)(serwer_gracza()), 10, 0.5) or {}
            if not sg:
                log("klik GRAJ nie zadziałał — wejście haczykiem")
                hak("graj", "sila", dm="Client")
                sg = czekaj_na(lambda: (lambda g: g if g.get("gra") == "sila" else None)(serwer_gracza()), 10, 0.5) or {}
            time.sleep(1.0)
            kl = klient()
            p = poz() or [0, 0, 0]
            podest = D["swiat"]["sila"]["podest"]
            powrot = sg.get("powrot")
            ok4 = (sg.get("gra") == "sila" and odl_xz(p, podest) <= 1.5 and kl.get("kamera") == "Scriptable"
                   and kl.get("dotyk") is False and kl.get("ekran") == "stanowisko"
                   and (P0 is None or (powrot and odl_xz(powrot, P0) <= 1.5)))
            zapisz("T04", {"serwer": sg, "klient": kl, "pozycja": p, "P0": P0})
            punkt("T04", ok4, "gra %s, od podestu %.2f st, kamera %s, dotyk %s, powrót %s" % (
                sg.get("gra"), odl_xz(p, podest), kl.get("kamera"), kl.get("dotyk"),
                "%.2f st od P0" % odl_xz(powrot, P0) if (powrot and P0) else powrot))
            zrzut("02_stanowisko_sila")

            # ---------------------------------------------------------------- T05 runda Siły bezbłędnie + T13 klatka
            sesja0 = (serwer_gracza().get("sesja") or {}).get("TreningSila") or 0
            syg0 = atrybuty(["ProbaSygnaly"]).get("ProbaSygnaly") or 0
            poziom = js(GR + 'return H:JSONEncode({ l = gracz:GetAttribute("Level") })', "Server").get("l")
            k0 = start_rundy()
            if k0:
                n = hak("autograj", 1.0, False, dm="Client")
                luau('local k = workspace.TreningProba task.spawn(function() local RS = game:GetService("RunService") '
                     'task.wait(%r) local t = {} local t0 = os.clock() while os.clock() - t0 < 6 do table.insert(t, RS.RenderStepped:Wait()) end '
                     'table.sort(t) local s = 0 for _, x in t do s += x end k:SetAttribute("ProbaKlatkaSr", s / #t * 1000) '
                     'k:SetAttribute("ProbaKlatkaP95", t[math.max(1, math.floor(#t * 0.95))] * 1000) end) return "ok"'
                     % (D["runda"]["odliczanie_s"] + 4), "Client")
                time.sleep(D["runda"]["odliczanie_s"] + 7)
                zrzut("03_runda_sila")
                kk = czekaj_na_koniec_rundy() or klient()
                time.sleep(1.0)
                sg = serwer_gracza()
                ost = sg.get("ostatnia") or {}
                nz = ost.get("n") or 0
                # pierwsza runda Siły w tej sesji Play: pasek od zera, W = punkty sesji, pula z atrybutu Level
                oczek, _, _, z_punktem = LT.punkty_za_serie(D, nz, {"pasek": 0, "W": sesja0, "pula": LT.pula(D, poziom)})
                jedn = sum(LT.przyrost(D, i) for i in range(1, nz + 1))
                sesja1 = (sg.get("sesja") or {}).get("TreningSila") or 0
                syg1 = atrybuty(["ProbaSygnaly"]).get("ProbaSygnaly") or 0
                ok5 = (ost.get("trafienia") == nz and ost.get("pudla") == 0 and ost.get("suma") == oczek
                       and ost.get("jednostki") == jedn and sesja1 - sesja0 == oczek and syg1 - syg0 == z_punktem
                       and kk.get("rozbieznosci") == 0)
                zapisz("T05", {"zaplanowane": n, "ostatnia": ost, "oczekiwana_suma": oczek, "poziom": poziom,
                               "oczekiwane_jednostki": jedn, "oczekiwane_sygnaly": z_punktem, "sesja": [sesja0, sesja1],
                               "sygnaly": [syg0, syg1], "rozbieznosci": kk.get("rozbieznosci"),
                               "sygnal": atrybuty(["ProbaOstatniSygnal"]).get("ProbaOstatniSygnal")})
                punkt("T05", ok5, "trafienia %s/%s, pudła %s, jednostki %s (oczek. %s), punkty %s (oczek. %s), TreningSila +%s, "
                      "sygnałów %s (oczek. %s), rozbieżności %s" % (
                          ost.get("trafienia"), nz, ost.get("pudla"), ost.get("jednostki"), jedn, ost.get("suma"), oczek,
                          sesja1 - sesja0, syg1 - syg0, z_punktem, kk.get("rozbieznosci")))
                kl13 = atrybuty(["ProbaKlatkaSr", "ProbaKlatkaP95"], "Client")
                sr, p95 = kl13.get("ProbaKlatkaSr"), kl13.get("ProbaKlatkaP95")
                zapisz("T13", kl13)
                punkt("T13", None if (sr is None or sr > 50) else (p95 or 0) < 33.4,
                      "klatka śr. %s ms, p95 %s ms%s" % (sr and round(sr, 1), p95 and round(p95, 1),
                                                        " (≈ limit Studia pod zaciemnieniem)" if sr and sr > 50 else ""))
            else:
                punkt("T05", False, "runda nie wystartowała")

            # ---------------------------------------------------------------- T06 prawdziwe klawisze, ruch pochłonięty
            k0 = start_rundy()
            if k0:
                time.sleep(D["runda"]["odliczanie_s"] + 1.5)
                p_przed = poz()
                r_przed = (serwer_gracza().get("runda") or {})
                for kod in ("Up", "Left", "W", "D", "Space", "Down"):
                    klawisz(kod)
                    time.sleep(0.5)
                time.sleep(1.0)
                r_po = (serwer_gracza().get("runda") or {})
                p_po = poz()
                zgl = lambda r: (r.get("trafienia") or 0) + (r.get("pudla") or 0) + (r.get("puste") or 0)  # noqa: E731
                przes = odl_xz(p_przed, p_po) if (p_przed and p_po) else 99
                zapisz("T06", {"przed": r_przed, "po": r_po, "przesuniecie": przes})
                punkt("T06", zgl(r_po) - zgl(r_przed) >= 3 and przes < 0.5,
                      "zgłoszeń z klawiszy: %d (werdykty), przesunięcie postaci %.2f st" % (zgl(r_po) - zgl(r_przed), przes))
                hak("przerwij", dm="Client")
                time.sleep(1.5)

            # ---------------------------------------------------------------- T07 spam
            time.sleep(1.2)
            k0 = start_rundy()
            if k0:
                time.sleep(D["runda"]["odliczanie_s"] + 2)
                r_przed = serwer_gracza().get("runda") or {}
                hak("spam", 60, "gora", dm="Client")
                time.sleep(1.5)
                r_po = serwer_gracza().get("runda") or {}
                spam = (r_po.get("spam") or 0) - (r_przed.get("spam") or 0)
                zysk = (r_po.get("jednostki") or 0) - (r_przed.get("jednostki") or 0)
                zapisz("T07", {"przed": r_przed, "po": r_po})
                punkt("T07", spam >= 50 and zysk <= 8, "odrzucone jako spam: %d z 60, jednostki paska ze spamu %d" % (spam, zysk))
                hak("przerwij", dm="Client")
                time.sleep(1.5)

            # ---------------------------------------------------------------- T08 werdykty
            time.sleep(1.2)
            k0 = start_rundy()
            if k0:
                plan = hak("plan") or []
                e = {x["nr"]: x for x in plan} if isinstance(plan, list) else {}
                if len(e) >= 8:
                    zly = [a for a in D["gry"]["sila"]["akcje"] if a != e[2]["wartosc"]][0]
                    zap = [{"nr": 1, "w": e[1]["wartosc"], "dt": 0}, {"nr": 2, "w": zly, "dt": 0},
                           {"nr": 3, "w": e[3]["wartosc"], "dt": -(e[3]["okno"] + 0.15)},
                           {"nr": 5, "w": e[5]["wartosc"], "dt": 0}, {"nr": 6, "w": e[6]["wartosc"], "dt": 0},
                           {"nr": 6, "w": e[6]["wartosc"], "dt": 0.08}, {"nr": 7, "w": e[7]["wartosc"], "dt": 0}]
                    hak("zaplanuj", zap, dm="Client")
                    time.sleep(D["runda"]["odliczanie_s"] + e[8]["t"] + 1.5)  # runda ruszyła tuż przed planem
                    kl = klient()
                    wyn = {w.get("nr"): w.get("powod") for w in (kl.get("wyniki") or []) if isinstance(w, dict) and w.get("nr")}
                    oczek = {1: "trafienie", 2: "zly_kierunek", 3: "za_wczesnie", 4: "przepuszczone", 5: "trafienie",
                             6: "trafienie", 7: "trafienie"}
                    seria7 = [w.get("seria") for w in (kl.get("wyniki") or []) if isinstance(w, dict) and w.get("nr") == 7]
                    zapisz("T08", {"wyniki": kl.get("wyniki"), "oczekiwane": oczek})
                    ok8 = all(wyn.get(nr) == p for nr, p in oczek.items()) and seria7 == [3]
                    punkt("T08", ok8, "werdykty %s, seria po 7: %s (oczek. 3 — dubel przy 6 nie zeruje)" % (
                        {nr: wyn.get(nr) for nr in oczek}, seria7))
                else:
                    punkt("T08", False, "brak planu rundy z haczyka")
                hak("przerwij", dm="Client")
                time.sleep(1.5)

            # ---------------------------------------------------------------- T09 Pancerz przez INNA GRA (+ T10)
            sesja0 = (serwer_gracza().get("sesja") or {}).get("TreningPancerz") or 0
            hak("inna", dm="Client")
            time.sleep(0.4)
            hak("graj", "pancerz", dm="Client")
            sg = czekaj_na(lambda: (lambda g: g if g.get("gra") == "pancerz" else None)(serwer_gracza()), 10, 0.5) or {}
            time.sleep(1.5)
            k0 = start_rundy() if sg else None
            if k0:
                plan = hak("plan") or []
                ciosy = [x for x in plan if x["wartosc"] == "cios"]
                zm = [x for x in plan if x["wartosc"] == "zmylka"]
                zap = [{"nr": x["nr"], "w": "blok", "dt": 0} for x in ciosy] + ([{"nr": zm[0]["nr"], "w": "blok", "dt": 0}] if zm else [])
                hak("zaplanuj", zap, dm="Client")
                time.sleep(D["runda"]["odliczanie_s"] + 12)
                zrzut("04_runda_pancerz")
                kk = czekaj_na_koniec_rundy() or klient()
                time.sleep(1.0)
                sg = serwer_gracza()
                ost = sg.get("ostatnia") or {}
                sesja1 = (sg.get("sesja") or {}).get("TreningPancerz") or 0
                ok9 = (ost.get("pudla") == (1 if zm else 0) and ost.get("trafienia") == len(plan) - (1 if zm else 0)
                       and sesja1 - sesja0 == ost.get("suma"))
                zapisz("T09", {"ostatnia": ost, "zmylek": len(zm), "sesja": [sesja0, sesja1]})
                punkt("T09", ok9, "trafienia %s/%s, pudła %s (zablokowana zmyłka: %s), TreningPancerz +%s = suma %s" % (
                    ost.get("trafienia"), len(plan), ost.get("pudla"), "tak" if zm else "brak zmyłek w planie",
                    sesja1 - sesja0, ost.get("suma")))
                zrzut("05_podsumowanie")
                # T10: podsumowanie → prawdziwa spacja = JESZCZE RAZ
                ok10a = kk.get("ekran") == "podsumowanie"
                time.sleep(1.2)
                klawisz("Space")
                k10 = czekaj_na(lambda: (lambda c: c if c.get("ekran") == "runda" else None)(klient()), 6, 0.3)
                zapisz("T10", {"podsumowanie": kk.get("podsumowanie"), "po_spacji": k10 and k10.get("ekran")})
                punkt("T10", ok10a and bool(k10), "panel podsumowania: %s, spacja → %s" % (ok10a, k10 and k10.get("ekran")))
                hak("przerwij", dm="Client")
                time.sleep(1.5)
            else:
                punkt("T09", False, "nie weszło na stanowisko Pancerza / brak rundy")

            # ---------------------------------------------------------------- T11 wyjście (kliknięcie WYJDŹ, brama w arenie)
            klik("Podsumowanie.Wyjdz")
            ok_wyj = czekaj_na(lambda: not serwer_gracza().get("gra"), 8, 0.5)
            if not ok_wyj:
                log("klik WYJDŹ nie zadziałał — wyjście haczykiem")
                hak("wyjdz", dm="Client")
                czekaj_na(lambda: not serwer_gracza().get("gra"), 8, 0.5)
            time.sleep(1.5)
            p = poz() or [0, 0, 0]
            kl = klient()
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": [
                {"action": "keyDown", "key_code": "W"}, {"action": "wait", "wait_time_ms": 600}, {"action": "keyUp", "key_code": "W"}]})
            time.sleep(0.5)
            p2 = poz() or p
            od_p0 = odl_xz(p, P0) if P0 else None
            # brama WYJŚCIE (E) w arenie bez punktu powrotu → miejsce startu
            br = js('local e = k.Arena.Lobby.Wyjscie.E return H:JSONEncode({ p = J(e.Position) })', "Server")
            przestaw([br["p"][0], br["p"][1] + 0.5, br["p"][2] - 4], br["p"])
            time.sleep(1.2)
            kamera_za()
            time.sleep(0.4)
            klawisz("E")
            time.sleep(1.5)
            p3 = poz() or [0, 0, 0]
            w_arenie = LT.w_arenie(D, p3[0], p3[1], p3[2])
            zapisz("T11", {"po_wyjsciu": p, "P0": P0, "klient": kl, "po_W": p2, "po_bramie": p3})
            punkt("T11", (od_p0 is None or od_p0 <= 1.5) and kl.get("kamera") == "Custom" and kl.get("ekran") == "brak"
                  and odl_xz(p, p2) > 1.0 and not w_arenie,
                  "od P0 %s st, kamera %s, dotyk %s, W przesuwa o %.1f st, brama → %s" % (
                      od_p0 and round(od_p0, 2), kl.get("kamera"), kl.get("dotyk"), odl_xz(p, p2),
                      "poza areną" if not w_arenie else "NADAL W ARENIE"))

            # ---------------------------------------------------------------- T12 telefon (rozmiary)
            u = (klient().get("ui") or {})
            ok12 = all((u.get(x) or 0) >= 44 for x in ("przycisk667", "przycisk568")) and all(
                (u.get(x) or 0) >= 12 for x in ("tekst667", "tekst568"))
            zapisz("T12", u)
            punkt("T12", ok12, "przy 667×375: przycisk %s px, tekst %s pt; przy 568×320: %s px, %s pt; ekran %s (skala %s)" % (
                u.get("przycisk667"), u.get("tekst667"), u.get("przycisk568"), u.get("tekst568"), u.get("ekranPx"), u.get("skala")))

            # ---------------------------------------------------------------- T14 konsola
            kons = call("get_console_output", {}, timeout=60)["text"]
            linie = [x.strip()[:240] for x in kons.splitlines() if "TreningProba" in x or "Treningu" in x or "rror" in x]
            bledy = [x for x in linie if ("rror" in x or "błąd" in x.lower()) and ("TreningProba" in x or "Treningu" in x)]
            zapisz("T14", linie[-60:])
            punkt("T14", not bledy, "%d wierszy [TreningProba]/error, błędów pakietu: %d %s" % (len(linie), len(bledy), bledy[:3]))
        finally:
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
            for _ in range(60):
                time.sleep(0.5)
                if "Current Studio Mode: Edit" in stan_studio():
                    break
    print("\n".join("%s %-4s %s" % x for x in LISTA))


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    main()
