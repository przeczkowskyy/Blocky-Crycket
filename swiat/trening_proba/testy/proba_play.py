# -*- coding: utf-8 -*-
"""Próba Training Center (sześć mini-gier) w Roblox Studio, tryb Play. T01–T14: Siła i Pancerz (przebieg z 17.11.2026,
14 × OK), T15–T22: Kondycja „Bieżnia”, Zręczność „Kłody”, Inteligencja „Runy”, Szczęście „Koniczyny” (nowe, noc
17/18.11.2026 — jeszcze nieuruchomione w Studio).

    python -B swiat/trening_proba/testy/proba_play.py <folder wyjściowy poza repo> [--studio <studio_id>]
           [--bez-zrzutow] [--tylko T01,T05,…] [--nowe]
    python -B swiat/trening_proba/testy/proba_play.py --sprawdz     # bez Studio: każdy kawałek Luau parsuje się

--nowe: tylko gotowość (T01) i punkty nowych gier (T15–T22). Warunki: Studio w trybie Edit, otwarte miejsce gry
(placeId sprawdza cel_studio), zbudowane Workspace/TreningProba (python -B swiat/trening_proba/zbuduj.py); najlepiej też
MiasteczkoBazar + MiasteczkoBazarGra (T03 z prawdziwym E przy trenerze — bez nich T03 sprawdza tylko zdarzenie
OknoMiejsca). Skrypt sam włącza i wyłącza Play, w trybie Play zmienia tylko stan gracza (położenie postaci, kamera
testu, życie postaci w T20) i używa haczyków pakietu; niczego nie zapisuje w miejscu i niczego nie publikuje. Wyniki:
<wyj>/wyniki.json, lista kontrolna na ekranie i w <wyj>/lista.txt, zrzuty <wyj>/<nazwa>.jpg (tylko zrzuty, bez filmów).
Nazwa konta w zapisach zamieniana na <gracz> (repo jest publiczne).

LISTA KONTROLNA (każdy punkt kończy się OK / BŁĄD / ? w liście):
  T01 gotowość: SerwerTreninguGotowy, ZgodnoscLogikiTreningu „OK n/n”, Podpowiedzi = 3, KlientTreninguGotowy,
      6 kafelków wyboru (6 grywalnych), zdarzenie OknoMiejsca podpięte
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
      na obecnym ekranie
  T13 czas klatki: RenderStepped 6 s w rundzie Siły (średnio, p95) — przy zaciemnionym oknie Studio „?”
  T14 konsola: bez błędów z [TreningProba] i bez „error” ze skryptów pakietu
  --- nowe mini-gry (noc 17/18.11.2026) ---
  T15 Kondycja „Bieżnia”: wejście (postać twarzą do kamery na taśmie), podpowiedź obrazkowa na stanowisku, w odliczaniu
      podpowiedź jest, a przycisków nie ma; runda autograj 1,0: trafienia = kroki, pudła 0, jednostki = Σ przyrost ×
      waga, punkty z paska, TreningKondycja += suma, rozbieżności 0, animacja biegu gra (gdy postać ma skrypt Animate);
      prawdziwe klawisze A / D / ← / → w drugiej rundzie dochodzą jako zgłoszenia, postać się nie przesuwa
  T16 Zręczność „Kłody”: runda autograj 1,0 bez pudła, TreningZrecznosc += suma; w trakcie rundy staw biodra
      przesunięty (skok / padnij widać), po rundzie wszystkie stawy jak przed nią; prawdziwa spacja i S dochodzą
  T17 Inteligencja „Runy”: naciśnięcie w czasie pokazu → „pokaz” (bez kary); runda autograj 1,0: pudła 0, zaklęć ≥ 2,
      TreningInteligencja += suma; potem jedna zła runa → sekwencja krótsza o karę (stan serwera)
  T18 Szczęście „Koniczyny”: runda autograj 1,0: złapane = wszystkie koniczyny, pudła ≤ 1, postać przechodziła między
      torami; runda bez ruchu (AFK, 15 s) → 0 jednostek paska
  T19 spam w każdej nowej grze: 60 zgłoszeń naraz → ≥ 48 odrzuconych jako spam, jednostki paska ze spamu ≤ 8 × waga
  T20 reset postaci w czasie rundy Kłód (staw przesunięty): serwer kończy rundę i zdejmuje ze stanowiska, klient:
      ekran „brak”, kamera Custom, dotyk przywrócony, HUD oddany (schowane ekrany 0), nowa postać bez zmian stawów
  T21 czas klatki w rundzie Bieżni i Koniczyn (najwięcej ruchomych części): śr. i p95 (okno Studio na wierzchu)
  T22 konsola po nowych grach: bez błędów pakietu; ZgodnoscLogikiTreningu dalej „OK”
  (ręcznie, poza skryptem: dźwięki na słuch; dwóch graczy (Test → Clients and Servers, 2); pad)

ZRZUTY (w <wyj>): 01_wybor_tymczasowy, 02_stanowisko_sila, 03_runda_sila, 04_runda_pancerz, 05_podsumowanie,
  06_tablica_wejscia, 15_kondycja, 16_zrecznosc, 17_inteligencja, 18_szczescie.
"""
import io
import json
import math
import os
import re
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

# Kawałki Luau: (szablon %-owy, przykładowe argumenty dla --sprawdz). Te z "js" dostają przedrostek KP + J.
KOD = {
    "atrybuty": ('local o = {} if not k then return H:JSONEncode({ brak = true }) end '
                 'for _, n in { %s } do o[n] = J(k:GetAttribute(n)) end return H:JSONEncode(o)', ('"a", "b"',)),
    "hak": ('return H:JSONEncode(J(k.Sygnaly.%s:Invoke("%s"%s)))', ("SterowanieKlienta", "stan", ', 1, "x", { 1 }')),
    "poz": (HRP + 'return H:JSONEncode(J(if hrp then hrp.Position else nil))', ()),
    "przestaw": (HRP + 'if hrp then local p = Vector3.new(%r, %r, %r) local q = Vector3.new(%r, p.Y, %r) '
                 'gracz.Character:PivotTo(CFrame.lookAt(p, q)) hrp.AssemblyLinearVelocity = Vector3.zero end return "ok"',
                 (1.0, 2.0, 3.0, 4.0, 5.0)),
    "kamera_za": ('local cam = workspace.CurrentCamera local p = game:GetService("Players").LocalPlayer '
                  'local h = p.Character and p.Character:FindFirstChild("HumanoidRootPart") if h then '
                  'cam.CameraType = Enum.CameraType.Custom cam.CFrame = CFrame.lookAt(h.Position - h.CFrame.LookVector * 10 '
                  '+ Vector3.new(0, 4, 0), h.Position + h.CFrame.LookVector * 4) end return "ok"', ()),
    "edit": ('return H:JSONEncode({ kontener = k ~= nil, wygenerowane = k and k:GetAttribute("Wygenerowane"), '
             'bazar = workspace:FindFirstChild("%s") ~= nil, punkt = k and J(k:GetAttribute("PunktTablicy")) })',
             ("MiasteczkoBazarGra",)),
    "gotowy_klient": ('local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)', ()),
    "imie": ('return game:GetService("Players").LocalPlayer.Name', ()),
    "wybor_klasy": ('local p = game:GetService("Players").LocalPlayer local g = p.PlayerGui:FindFirstChild("ClassSelect") '
                    'local c = workspace.CurrentCamera return H:JSONEncode({ ekran = g ~= nil and g.Enabled, '
                    'kamera = c.CameraType.Name, podpowiedzi = game:GetService("ProximityPromptService").Enabled })', ()),
    "sluchacz": (KP + 'local n = 0 k.Sygnaly.PrzyrostStatystyki.Event:Connect(function(g, p) n += 1 '
                 'k:SetAttribute("ProbaSygnaly", n) k:SetAttribute("ProbaOstatniSygnal", H:JSONEncode(p)) end) return "ok"', ()),
    "tablica": ('local e = k:FindFirstChild("TablicaWejscia") e = e and e:FindFirstChild("E") '
                'return H:JSONEncode(if e then { p = J(e.Position), przod = J(e.CFrame.LookVector) } else {})', ()),
    "stan_bazaru": ('local b = workspace:FindFirstChild("%s") local s = b and b.Sygnaly.SterowanieKlienta:Invoke("stan") '
                    'return H:JSONEncode(J(s))', ("MiasteczkoBazarGra",)),
    "poziom": (GR + 'return H:JSONEncode({ l = gracz:GetAttribute("Level") })', ()),
    "klatka": ('local k = workspace.TreningProba task.spawn(function() local RS = game:GetService("RunService") '
               'task.wait(%r) local t = {} local t0 = os.clock() while os.clock() - t0 < %r do table.insert(t, RS.RenderStepped:Wait()) end '
               'table.sort(t) local s = 0 for _, x in t do s += x end k:SetAttribute("%sSr", s / #t * 1000) '
               'k:SetAttribute("%sP95", t[math.max(1, math.floor(#t * 0.95))] * 1000) end) return "ok"',
               (4.0, 6.0, "ProbaKlatka", "ProbaKlatka")),
    "brama": ('local e = k.Arena.Lobby.Wyjscie.E return H:JSONEncode({ p = J(e.Position) })', ()),
    # T20: reset postaci (serwer) — życie 0, Roblox odradza postać jak po zwykłej śmierci
    "reset": (GR + 'local h = gracz.Character and gracz.Character:FindFirstChildOfClass("Humanoid") '
              'if h then h.Health = 0 end return tostring(h ~= nil)', ()),
    # próbka stanu klienta co 0,1 s przez N s (stawy przesunięte, bieg, tor, pozycja) → atrybuty kontenera u klienta
    "probki": ('local k = workspace.TreningProba task.spawn(function() local maks, bieg, x0, x1 = 0, false, nil, nil '
               'for _ = 1, %d do local s = k.Sygnaly.SterowanieKlienta:Invoke("stan") maks = math.max(maks, s.stawyZmienione or 0) '
               'bieg = bieg or s.bieg if s.pozycja then x0 = math.min(x0 or s.pozycja[1], s.pozycja[1]) '
               'x1 = math.max(x1 or s.pozycja[1], s.pozycja[1]) end task.wait(0.1) end '
               'k:SetAttribute("ProbaStawy", maks) k:SetAttribute("ProbaBieg", bieg) '
               'k:SetAttribute("ProbaRozpietoscX", if x0 then x1 - x0 else -1) end) return "ok"', (50,)),
}


def kod(nazwa, *argi):
    return KOD[nazwa][0] % argi if argi else KOD[nazwa][0]


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def odl_xz(a, b):
    return math.hypot(a[0] - b[0], a[2] - b[2])


def sprawdz_kod():
    """Bez Studio: każdy kawałek z KOD (z przykładowymi argumentami, z przedrostkiem jak przy wysyłce) parsuje się."""
    sys.path.insert(0, os.path.join(REPO, "tools", "walka"))
    import luau_mini as LM  # noqa: E402
    bledy = []
    for nazwa, (szablon, przyklad) in KOD.items():
        tekst = szablon % przyklad if przyklad else szablon
        for kod_ in (tekst, KP + J + tekst):
            try:
                LM.Parser(kod_, nazwa, LM.Interpreter()).program()
            except LM.BladSkladni as e:
                bledy.append("%s: %s" % (nazwa, e))
                break
        if re.search(r"%[sdrf]", tekst):
            bledy.append("%s: nie wszystkie %%-pola podstawione" % nazwa)
    print("sprawdz: %d kawałków Luau, %s" % (len(KOD), "OK" if not bledy else "BŁĘDY:\n  " + "\n  ".join(bledy)))
    return 0 if not bledy else 1


def main():
    argv = sys.argv[1:]
    if "--sprawdz" in argv:
        sys.exit(sprawdz_kod())
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    try:
        w_repo = os.path.commonpath([os.path.normcase(wyj), os.path.normcase(REPO)]) == os.path.normcase(REPO)
    except ValueError:  # inny dysk
        w_repo = False
    if w_repo:
        sys.exit("Folder wyjściowy ma być poza repozytorium (zrzuty i nazwa konta nie trafiają do git): %s" % wyj)
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    bez_zrzutow = "--bez-zrzutow" in argv
    tylko = set(argv[argv.index("--tylko") + 1].split(",")) if "--tylko" in argv else None
    if "--nowe" in argv:
        tylko = {"T01"} | {"T%02d" % i for i in range(15, 23)}
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

    def punkt(kod_, ok, opis):
        opis = anonim(opis) if isinstance(opis, str) else opis
        LISTA.append((kod_, "OK" if ok is True else ("BŁĄD" if ok is False else "?"), opis))
        log("%s %s — %s" % (kod_, LISTA[-1][1], opis))
        with open(os.path.join(wyj, "lista.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join("%s %-4s %s" % x for x in LISTA) + "\n")

    def chce(kod_):
        return tylko is None or kod_ in tylko

    with StudioMCP(timeout=180) as s:
        sid = wybierz_studio(s, studio)

        def call(n, a=None, timeout=None):
            d = dict(a or {})
            d["studio_id"] = sid
            return s.call(n, d, timeout=timeout)

        def luau(kod_, dm, proby=3):
            for i in range(proby):
                try:
                    r = call("execute_luau", {"code": kod_, "datamodel_type": dm}, timeout=120)
                    if r["is_error"]:
                        raise StudioError(r["text"][:800])
                    return r["text"].strip()
                except Exception as e:  # noqa: BLE001 — Studio czasem chwilę nie odpowiada
                    if i == proby - 1:
                        raise
                    log("luau: ponawiam po błędzie:", str(e)[:200])
                    time.sleep(8)

        def js(kod_, dm):
            return json.loads(luau(KP + J + kod_, dm))

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
            dane_ = r["images"][0]
            if Image is not None:
                im = Image.open(io.BytesIO(dane_)).convert("RGB")
                if im.width > 1280:
                    im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
                im.save(os.path.join(wyj, nazwa + ".jpg"), "JPEG", quality=85)
            else:
                with open(os.path.join(wyj, nazwa + ".png"), "wb") as f:
                    f.write(dane_)
            log("zrzut", nazwa)

        def atrybuty(nazwy, dm="Server"):
            w = js(kod("atrybuty", ", ".join('"%s"' % n for n in nazwy)), dm)
            return w if isinstance(w, dict) else {}

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

        def hak(polecenie, *argi, dm="Server"):
            nazwa = "SterowanieSerwera" if dm == "Server" else "SterowanieKlienta"
            a = ", ".join("nil" if x is None else lua(x) for x in argi)
            return js(kod("hak", nazwa, polecenie, (", " + a) if a else ""), dm)

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
            return js(kod("poz"), "Server")

        def przestaw(p, patrz):
            luau(kod("przestaw", p[0], p[1], p[2], patrz[0], patrz[2]), "Server")

        def kamera_za():
            luau(kod("kamera_za"), "Client")

        def klawisz(kod_):
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": kod_}]})

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

        def wejdz_do(gra):
            hak("inna", dm="Client")
            time.sleep(0.4)
            hak("graj", gra, dm="Client")
            sg = czekaj_na(lambda: (lambda g: g if g.get("gra") == gra else None)(serwer_gracza()), 10, 0.5) or {}
            time.sleep(1.5)
            return sg

        def sesja(atrybut):
            return (serwer_gracza().get("sesja") or {}).get(atrybut) or 0

        def runda_autogra(gra, celnosc=1.0, zrzut_nazwa=None, probki=None):
            """Wejście (gdy trzeba), runda z autogrą, zrzut w połowie → (ostatnia, oczekiwane, sesja0, sesja1, kk, plan)."""
            st = L_statystyka(gra)
            sesja0 = sesja(st["atrybut_sesji"])
            poziom = js(kod("poziom"), "Server").get("l")
            k0 = start_rundy()
            if not k0:
                return None
            plan = hak("plan") or []
            if probki:
                luau(kod("probki", probki), "Client")
            hak("autograj", celnosc, False, dm="Client")
            time.sleep(D["runda"]["odliczanie_s"] + 14)
            if zrzut_nazwa:
                zrzut(zrzut_nazwa)
            kk = czekaj_na_koniec_rundy() or klient()
            time.sleep(1.0)
            sg = serwer_gracza()
            ost = sg.get("ostatnia") or {}
            sesja1 = (sg.get("sesja") or {}).get(st["atrybut_sesji"]) or 0
            return {"ost": ost, "sesja0": sesja0, "sesja1": sesja1, "kk": kk, "plan": plan, "poziom": poziom, "k0": k0}

        def L_statystyka(gra):
            return LT.statystyka(D, gra)

        def oczekiwane(gra, n, wynik, mnozniki=None):
            G = D["gry"][gra]
            S0 = {"pasek": 0, "W": wynik["sesja0"], "pula": LT.pula(D, wynik["poziom"])}
            pkt, _, _, z_pkt = LT.punkty_za_serie(D, n, S0, G, mnozniki)
            jedn = 0.0
            for i in range(1, n + 1):
                jedn += LT.przyrost(D, i, G) * (mnozniki[i - 1] if mnozniki else 1)
            return pkt, jedn, z_pkt

        # ---------------------------------------------------------------- Edit: kontener stoi?
        edit = js(kod("edit", D["bazar"]["kontener"]), "Edit")
        zapisz("edit", edit)
        if not edit.get("kontener"):
            sys.exit("Brak Workspace/TreningProba w trybie Edit — najpierw python -B swiat/trening_proba/zbuduj.py")

        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        try:
            czekaj_na(lambda: "Client" in stan_studio() and luau(kod("gotowy_klient"), "Client") == "true", 90, 1)
            nazwa_gracza[0] = luau(kod("imie"), "Client")
            time.sleep(2)
            # ekran wyboru klasy (src/client/ClassSelectClient) trzyma kamerę skryptową i wyłącza podpowiedzi E —
            # Enter wybiera klasę jak gracz (tak samo robią próby lasu-pasa)
            wybor_klasy = {}
            for _ in range(20):
                wybor_klasy = js(kod("wybor_klasy"), "Client")
                if not wybor_klasy["ekran"] and wybor_klasy["kamera"] == "Custom" and wybor_klasy["podpowiedzi"]:
                    break
                klawisz("Return")
                time.sleep(1.5)
            zapisz("wybor_klasy", wybor_klasy)
            log("wybór klasy:", wybor_klasy)
            # słuchacz sygnału PrzyrostStatystyki (tylko na czas próby, w pamięci serwera)
            luau(kod("sluchacz"), "Server")

            # ---------------------------------------------------------------- T01 gotowość
            at = atrybuty(["SerwerTreninguGotowy", "ZgodnoscLogikiTreningu", "Podpowiedzi"])
            kl = klient()
            klg = atrybuty(["KlientTreninguGotowy"], "Client")
            zapisz("T01", {"serwer": at, "klient": kl, "klient_atr": klg})
            ok = (at.get("SerwerTreninguGotowy") is True and str(at.get("ZgodnoscLogikiTreningu", "")).startswith("OK")
                  and at.get("Podpowiedzi") == 3 and klg.get("KlientTreninguGotowy") is True
                  and kl.get("kafelki") == 6 and kl.get("grywalne") == 6 and (kl.get("zdarzeniaOkien") or 0) >= 1)
            punkt("T01", ok, "%s, podpowiedzi %s, kafelki %s/%s, zdarzeń OknoMiejsca %s, arkusz dźwięku %s" % (
                at.get("ZgodnoscLogikiTreningu"), at.get("Podpowiedzi"), kl.get("grywalne"), kl.get("kafelki"),
                kl.get("zdarzeniaOkien"), kl.get("arkusz")))

            P0 = None
            tab = {}
            if chce("T02") or chce("T11"):
                # ---------------------------------------------------------------- T02 tablica wejścia (prawdziwe E)
                tab = js(kod("tablica"), "Server")
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
                    bz = js(kod("stan_bazaru", D["bazar"]["kontener"]), "Client")
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
            if chce("T04") or chce("T05"):
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
            if chce("T05"):
                sesja0 = sesja("TreningSila")
                syg0 = atrybuty(["ProbaSygnaly"]).get("ProbaSygnaly") or 0
                poziom = js(kod("poziom"), "Server").get("l")
                k0 = start_rundy()
                if k0:
                    hak("autograj", 1.0, False, dm="Client")
                    luau(kod("klatka", D["runda"]["odliczanie_s"] + 4, 6.0, "ProbaKlatka", "ProbaKlatka"), "Client")
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
                    zapisz("T05", {"ostatnia": ost, "oczekiwana_suma": oczek, "poziom": poziom,
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
            if chce("T06"):
                k0 = start_rundy()
                if k0:
                    time.sleep(D["runda"]["odliczanie_s"] + 1.5)
                    p_przed = poz()
                    r_przed = (serwer_gracza().get("runda") or {})
                    for kod_ in ("Up", "Left", "W", "D", "Space", "Down"):
                        klawisz(kod_)
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
            if chce("T07"):
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
            if chce("T08"):
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
            if chce("T09") or chce("T10"):
                sesja0 = sesja("TreningPancerz")
                sg = wejdz_do("pancerz")
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

            # ================================================================ nowe mini-gry (T15–T22)
            # ---------------------------------------------------------------- T15 Kondycja „Bieżnia”
            if chce("T15"):
                sg = wejdz_do("kondycja")
                kl = klient()
                W = D["swiat"]["kondycja"]
                p = poz() or [0, 0, 0]
                stanowisko_ok = (sg.get("gra") == "kondycja" and odl_xz(p, W["podest"]) <= 1.5 and kl.get("ui", {}).get("obrazek")
                                 and (kl.get("ui", {}).get("obrazekElementy") or 0) > 5)
                zrzut("15_kondycja_start")
                w = runda_autogra("kondycja", zrzut_nazwa="15_kondycja", probki=40)
                if w:
                    ost, n = w["ost"], len(w["plan"])
                    pkt, jedn, _ = oczekiwane("kondycja", n, w)
                    od = atrybuty(["ProbaBieg"], "Client")
                    k0 = w["k0"]
                    ok = (stanowisko_ok and ost.get("trafienia") == n and ost.get("pudla") == 0 and ost.get("suma") == pkt
                          and abs((ost.get("jednostki") or 0) - jedn) < 1e-6 and w["sesja1"] - w["sesja0"] == pkt
                          and w["kk"].get("rozbieznosci") == 0 and k0.get("ui", {}).get("obrazek") is True)
                    # druga runda: prawdziwe klawisze (A, D, ←, →), postać się nie przesuwa
                    k1 = start_rundy()
                    zgl_k = 0
                    przes = 99
                    if k1:
                        time.sleep(D["runda"]["odliczanie_s"] + 1.2)
                        p_przed, r_przed = poz(), serwer_gracza().get("runda") or {}
                        for kl_ in ("A", "D", "Left", "Right"):
                            klawisz(kl_)
                            time.sleep(0.4)
                        time.sleep(0.8)
                        p_po, r_po = poz(), serwer_gracza().get("runda") or {}
                        zgl = lambda r: (r.get("trafienia") or 0) + (r.get("pudla") or 0) + (r.get("puste") or 0)  # noqa: E731
                        zgl_k = zgl(r_po) - zgl(r_przed)
                        przes = odl_xz(p_przed, p_po) if (p_przed and p_po) else 99
                        hak("przerwij", dm="Client")
                        time.sleep(1.5)
                    zapisz("T15", {"wynik": w, "oczek": [pkt, jedn], "bieg": od.get("ProbaBieg"), "klawisze": zgl_k, "przes": przes})
                    punkt("T15", ok and zgl_k >= 3 and przes < 0.5,
                          "trafienia %s/%s, pudła %s, punkty %s (oczek. %s), jednostki %.1f (oczek. %.1f), TreningKondycja +%s, "
                          "rozbieżności %s, bieg %s, klawisze → %d zgłoszeń, przesunięcie %.2f st, podpowiedź %s" % (
                              ost.get("trafienia"), n, ost.get("pudla"), ost.get("suma"), pkt, ost.get("jednostki") or 0, jedn,
                              w["sesja1"] - w["sesja0"], w["kk"].get("rozbieznosci"), od.get("ProbaBieg"), zgl_k, przes,
                              stanowisko_ok))
                else:
                    punkt("T15", False, "runda Bieżni nie wystartowała")

            # ---------------------------------------------------------------- T16 Zręczność „Kłody”
            if chce("T16"):
                wejdz_do("zrecznosc")
                zrzut("16_zrecznosc_start")
                w = runda_autogra("zrecznosc", zrzut_nazwa="16_zrecznosc", probki=60)
                if w:
                    ost, n = w["ost"], len(w["plan"])
                    pkt, jedn, _ = oczekiwane("zrecznosc", n, w)
                    st = atrybuty(["ProbaStawy"], "Client")
                    po = klient()
                    ok = (ost.get("trafienia") == n and ost.get("pudla") == 0 and ost.get("suma") == pkt
                          and w["sesja1"] - w["sesja0"] == pkt and (st.get("ProbaStawy") or 0) >= 1
                          and po.get("stawyZmienione") == 0)
                    k1 = start_rundy()
                    zgl_k = 0
                    if k1:
                        time.sleep(D["runda"]["odliczanie_s"] + 1.2)
                        r_przed = serwer_gracza().get("runda") or {}
                        for kl_ in ("Space", "S", "Space"):
                            klawisz(kl_)
                            time.sleep(0.5)
                        time.sleep(0.8)
                        r_po = serwer_gracza().get("runda") or {}
                        zgl = lambda r: (r.get("trafienia") or 0) + (r.get("pudla") or 0) + (r.get("puste") or 0)  # noqa: E731
                        zgl_k = zgl(r_po) - zgl(r_przed)
                        hak("przerwij", dm="Client")
                        time.sleep(1.5)
                    zapisz("T16", {"wynik": w, "oczek": [pkt, jedn], "stawy": st, "po": po.get("stawyZmienione"), "klawisze": zgl_k})
                    punkt("T16", ok and zgl_k >= 2, "trafienia %s/%s, pudła %s, punkty %s (oczek. %s), TreningZrecznosc +%s, "
                          "staw biodra przesunięty w rundzie: %s, po rundzie zmienione stawy: %s, klawisze → %d" % (
                              ost.get("trafienia"), n, ost.get("pudla"), ost.get("suma"), pkt, w["sesja1"] - w["sesja0"],
                              st.get("ProbaStawy"), po.get("stawyZmienione"), zgl_k))
                else:
                    punkt("T16", False, "runda Kłód nie wystartowała")

            # ---------------------------------------------------------------- T17 Inteligencja „Runy”
            if chce("T17"):
                wejdz_do("inteligencja")
                zrzut("17_inteligencja_start")
                # naciśnięcie w czasie pierwszego pokazu → „pokaz” (pominięte, bez kary)
                k0 = start_rundy()
                pokaz = None
                if k0:
                    G = D["gry"]["inteligencja"]
                    time.sleep(D["runda"]["odliczanie_s"] + G.get("pierwsze_s", D["runda"]["pierwsze_s"]) + 0.3)
                    pokaz = hak("nacisnij", "gora", dm="Client")
                    hak("przerwij", dm="Client")
                    time.sleep(1.5)
                w = runda_autogra("inteligencja", zrzut_nazwa="17_inteligencja")
                if w:
                    ost = w["ost"]
                    n = ost.get("trafienia") or 0
                    pkt, jedn, _ = oczekiwane("inteligencja", n, w)
                    ok = (pokaz == "pokaz" and ost.get("pudla") == 0 and n >= 10 and (ost.get("zaklecia") or 0) >= 2
                          and ost.get("suma") == pkt and w["sesja1"] - w["sesja0"] == pkt)
                    # zła runa → sekwencja krótsza o karę
                    k1 = start_rundy()
                    kara = None
                    if k1:
                        G = D["gry"]["inteligencja"]
                        r0 = serwer_gracza().get("runda") or {}
                        time.sleep(D["runda"]["odliczanie_s"] + (r0.get("pokazDo") or 4) + 0.4)  # w fazie wpisywania
                        plan = hak("plan") or []
                        r1 = serwer_gracza().get("runda") or {}
                        dobra = plan[(r1.get("offset") or 0) + (r1.get("poz") or 0)]["wartosc"] if plan else "gora"
                        zla = [x for x in G["runy"] if x != dobra][0]
                        hak("nacisnij", zla, dm="Client")
                        time.sleep(0.6)
                        r2 = serwer_gracza().get("runda") or {}
                        kara = (r1.get("dl"), r2.get("dl"), r2.get("pudla"))
                        hak("przerwij", dm="Client")
                        time.sleep(1.5)
                    ok = ok and kara is not None and kara[1] == max(G["min_dlugosc"], (kara[0] or 0) - G["kara"]) and kara[2] == 1
                    zapisz("T17", {"wynik": w, "oczek": [pkt, jedn], "pokaz": pokaz, "kara": kara})
                    punkt("T17", ok, "naciśnięcie w pokazie → %s; trafienia %s, pudła %s, zaklęć %s, najdłuższe %s, punkty %s "
                          "(oczek. %s), TreningInteligencja +%s; zła runa: długość %s → %s, pudła %s" % (
                              pokaz, n, ost.get("pudla"), ost.get("zaklecia"), ost.get("najdluzszaSekwencja"), ost.get("suma"),
                              pkt, w["sesja1"] - w["sesja0"], kara and kara[0], kara and kara[1], kara and kara[2]))
                else:
                    punkt("T17", False, "runda Run nie wystartowała")

            # ---------------------------------------------------------------- T18 Szczęście „Koniczyny”
            if chce("T18"):
                wejdz_do("szczescie")
                zrzut("18_szczescie_start")
                w = runda_autogra("szczescie", zrzut_nazwa="18_szczescie", probki=60)
                if w:
                    ost = w["ost"]
                    G = D["gry"]["szczescie"]
                    koniczyny = [e for e in w["plan"] if e["wartosc"] != "kamien"]
                    rozp = atrybuty(["ProbaRozpietoscX"], "Client").get("ProbaRozpietoscX")
                    ok = ((ost.get("zlapane") or 0) >= len(koniczyny) - 1 and (ost.get("pudla") or 0) <= 1
                          and (rozp or 0) >= 3.5 and w["sesja1"] - w["sesja0"] == ost.get("suma"))
                    # runda bez ruchu (15 s): koniczyny spadają poza koszyk → 0 jednostek
                    k1 = start_rundy()
                    afk = None
                    if k1:
                        time.sleep(D["runda"]["odliczanie_s"] + 15)
                        afk = serwer_gracza().get("runda") or {}
                        hak("przerwij", dm="Client")
                        time.sleep(1.5)
                    ok = ok and afk is not None and (afk.get("jednostki") or 0) == 0 and (afk.get("trafienia") or 0) == 0
                    zapisz("T18", {"wynik": w, "rozpietosc": rozp, "afk": afk})
                    punkt("T18", ok, "złapane %s/%s, pudła %s (kamienie %s), postać przeszła %.1f st w poprzek, TreningSzczescie +%s; "
                          "bez ruchu: jednostki %s, trafienia %s, pudła %s" % (
                              ost.get("zlapane"), len(koniczyny), ost.get("pudla"), ost.get("kamienie"), rozp or -1,
                              w["sesja1"] - w["sesja0"], afk and afk.get("jednostki"), afk and afk.get("trafienia"),
                              afk and afk.get("pudla")))
                else:
                    punkt("T18", False, "runda Koniczyn nie wystartowała")

            # ---------------------------------------------------------------- T19 spam w nowych grach
            if chce("T19"):
                opisy, ok19 = [], True
                for gra, wartosc in (("kondycja", "lewa"), ("zrecznosc", "skok"), ("inteligencja", "gora"), ("szczescie", "lewy")):
                    wejdz_do(gra)
                    k0 = start_rundy()
                    if not k0:
                        ok19 = False
                        opisy.append("%s: brak rundy" % gra)
                        continue
                    time.sleep(D["runda"]["odliczanie_s"] + 4.5)
                    r_przed = serwer_gracza().get("runda") or {}
                    hak("spam", 60, wartosc, dm="Client")
                    time.sleep(1.5)
                    r_po = serwer_gracza().get("runda") or {}
                    spam = (r_po.get("spam") or 0) - (r_przed.get("spam") or 0)
                    zysk = (r_po.get("jednostki") or 0) - (r_przed.get("jednostki") or 0)
                    ok19 = ok19 and spam >= 48 and zysk <= 8 * D["gry"][gra].get("waga", 1)
                    opisy.append("%s: spam %d/60, jednostki %.1f" % (gra, spam, zysk))
                    hak("przerwij", dm="Client")
                    time.sleep(1.5)
                zapisz("T19", opisy)
                punkt("T19", ok19, "; ".join(opisy))

            # ---------------------------------------------------------------- T20 reset postaci w czasie rundy Kłód
            if chce("T20"):
                wejdz_do("zrecznosc")
                k0 = start_rundy()
                ok20, opis20 = False, "brak rundy"
                if k0:
                    time.sleep(D["runda"]["odliczanie_s"] + 2)
                    hak("nacisnij", "padnij", dm="Client")
                    time.sleep(0.15)
                    przed = klient()
                    luau(kod("reset"), "Server")
                    czekaj_na(lambda: not serwer_gracza().get("gra"), 12, 0.5)
                    czekaj_na(lambda: luau(kod("gotowy_klient"), "Client") == "true", 20, 1)
                    time.sleep(2.5)
                    po = klient()
                    sg = serwer_gracza()
                    ok20 = (not sg.get("gra") and po.get("ekran") == "brak" and po.get("kamera") == "Custom"
                            and po.get("schowaneEkrany") == 0 and po.get("stawyZmienione") == 0
                            and (sg.get("ostatnia") or {}).get("przerwana") is True)
                    opis20 = ("przed resetem: stawy zmienione %s, ekran %s; po: serwer gra %s, klient ekran %s, kamera %s, dotyk %s, "
                              "schowane ekrany %s, stawy zmienione %s, runda przerwana %s" % (
                                  przed.get("stawyZmienione"), przed.get("ekran"), sg.get("gra"), po.get("ekran"), po.get("kamera"),
                                  po.get("dotyk"), po.get("schowaneEkrany"), po.get("stawyZmienione"),
                                  (sg.get("ostatnia") or {}).get("przerwana")))
                    zapisz("T20", {"przed": przed, "po": po, "serwer": sg})
                punkt("T20", ok20, opis20)
                if wybor_klasy.get("ekran") is not None:
                    for _ in range(6):  # po odrodzeniu ekran wyboru klasy może wrócić
                        wk = js(kod("wybor_klasy"), "Client")
                        if not wk["ekran"] and wk["kamera"] == "Custom":
                            break
                        klawisz("Return")
                        time.sleep(1.5)

            # ---------------------------------------------------------------- T21 czas klatki: Bieżnia i Koniczyny
            if chce("T21"):
                wyniki21, ok21 = {}, True
                for gra in ("kondycja", "szczescie"):
                    wejdz_do(gra)
                    k0 = start_rundy()
                    if not k0:
                        ok21 = None
                        continue
                    hak("autograj", 1.0, False, dm="Client")
                    luau(kod("klatka", D["runda"]["odliczanie_s"] + 3, 6.0, "ProbaKlatka" + gra, "ProbaKlatka" + gra), "Client")
                    time.sleep(D["runda"]["odliczanie_s"] + 10)
                    a = atrybuty(["ProbaKlatka%sSr" % gra, "ProbaKlatka%sP95" % gra], "Client")
                    sr, p95 = a.get("ProbaKlatka%sSr" % gra), a.get("ProbaKlatka%sP95" % gra)
                    wyniki21[gra] = [sr and round(sr, 1), p95 and round(p95, 1)]
                    if sr is None or sr > 50:
                        ok21 = None if ok21 is not False else False
                    elif (p95 or 99) >= 33.4:
                        ok21 = False
                    hak("przerwij", dm="Client")
                    time.sleep(1.5)
                zapisz("T21", wyniki21)
                punkt("T21", ok21, "klatka śr. / p95 [ms]: %s" % wyniki21)

            # ---------------------------------------------------------------- T11 wyjście (kliknięcie WYJDŹ, brama w arenie)
            if chce("T11"):
                if serwer_gracza().get("gra") is None:
                    wejdz_do("sila")
                # punkt powrotu zapamiętany przy OSTATNIM wejściu (po resecie z T20 to miejsce odrodzenia, nie P0)
                powrot = serwer_gracza().get("powrot")
                if powrot:
                    P0 = powrot
                # po przerwanej rundzie ekran podsumowania, po wejściu — panel startu; w obu jest WYJDŹ
                klik("Podsumowanie.Wyjdz" if klient().get("ekran") == "podsumowanie" else "Start.Wyjdz")
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
                br = js(kod("brama"), "Server")
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
            if chce("T12"):
                u = (klient().get("ui") or {})
                ok12 = all((u.get(x) or 0) >= 44 for x in ("przycisk667", "przycisk568")) and all(
                    (u.get(x) or 0) >= 12 for x in ("tekst667", "tekst568"))
                zapisz("T12", u)
                punkt("T12", ok12, "przy 667×375: przycisk %s px, tekst %s pt; przy 568×320: %s px, %s pt; ekran %s (skala %s)" % (
                    u.get("przycisk667"), u.get("tekst667"), u.get("przycisk568"), u.get("tekst568"), u.get("ekranPx"), u.get("skala")))

            # ---------------------------------------------------------------- T14 / T22 konsola
            kons = call("get_console_output", {}, timeout=60)["text"]
            linie = [x.strip()[:240] for x in kons.splitlines() if "TreningProba" in x or "Treningu" in x or "rror" in x]
            bledy = [x for x in linie if ("rror" in x or "błąd" in x.lower()) and ("TreningProba" in x or "Treningu" in x)]
            zapisz("T14", linie[-60:])
            if chce("T14"):
                punkt("T14", not bledy, "%d wierszy [TreningProba]/error, błędów pakietu: %d %s" % (len(linie), len(bledy), bledy[:3]))
            if chce("T22"):
                zg = atrybuty(["ZgodnoscLogikiTreningu"]).get("ZgodnoscLogikiTreningu")
                punkt("T22", not bledy and str(zg).startswith("OK"), "błędów pakietu: %d %s, zgodność logiki %s" % (
                    len(bledy), bledy[:3], zg))
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
