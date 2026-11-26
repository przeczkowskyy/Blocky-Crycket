#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba sklepu zbrojmistrza w trybie PLAY w Studio — lista S00–S11, wynik w testy/wynik_play.json (albo --wynik <plik>
poza repo), zrzuty w klatki/. Pierwszy przebieg w Studio 19.11.2026 (wynik w README).

    python -B swiat/sklep_proba/testy/proba_play.py --sprawdz            # bez Studio: każdy kawałek Luau parsuje się
    python -B tools/studio_okno.py --na-wierzch                          # przed próbą (okno w tle rysuje 15 kl./s)
    python -B swiat/sklep_proba/testy/proba_play.py [--tylko S03,S07] [--bez-zrzutow] [--studio <id>] [--wynik <plik>]

Wymaga w trybie Edit: Workspace/SklepProba (zbuduj.py), KowalProba z Sygnaly/Sklep, StanGracza (WydajZloto,
DanePakietu, Modyfikatory), StrojeProba z przedmiotami stopni, bazar z podpowiedzią E zbrojowni. Play tylko na czas
próby (SesjaPlay z swiat/test_walki2/testy/sesja_play.py zatrzymuje go zawsze). Zrzuty bez listy graczy i czatu,
wynik bez nazw kont. Próba ustawia graczowi poziom i Złoto atrybutami (tylko w Play — po próbie znikają).
  S00 Edit: kontenery, wejście kowala dla sklepu, skrót danych = lokalny
  S01 gotowość: serwer i klient sklepu, zgodność logiki, kowal podłączony, okno podpięte pod E bazaru
  S02 prawdziwe E przy zbrojmistrzu otwiera okno (zrzut); oferta klasy w czterech stopniach; jedno okno — makieta
      sklepu z HUD (ScreenGui „Shop”, też słucha E zbrojowni) schowana. Od 26.11.2026, gdy działa okno sklepu Pawła
      („Shop” z towarem z tego serwera): po E tylko jego okno, z towarem na ladzie; okno próbne się nie otwiera
  S03 kupno prawdziwym kliknięciem: Złoto w dół o cenę, przedmiot w posiadanych, napis potwierdzenia (zrzut); przy
      oknie Pawła — kliknięcie slotu, karta, BUY w jego oknie (ten sam serwer)
  S04 strój na postaci po kupnie: przedmiot w stroju przymierzalni (zrzut postaci)
  S05 reguła zakładania: wyższy stopień, potem niższy — zostaje wyższy; „Załóż” kliknięciem zmienia (zrzut); przy
      oknie Pawła „Załóż” = EQUIP na jego karcie
  S06 walka w kupionym przedmiocie: wpis kowala w Modyfikatory i opis bohatera walki rosną o statystyki przedmiotu
  S07 odmowy: za mało Złota, za niski poziom, posiadany, cudza klasa, nieznany, część zbroi, daleko — nic się nie zmienia
  S08 okno na małym ekranie (emulacja 667 × 375): tekst ≥ 12 pt, okno w ekranie; zrzut. Przy oknie Pawła — „?” (okno
      próbne nie jest już oknem gry, jego okna na telefonie próba nie mierzy)
  S09 zrzuty trzech klas w trzech stopniach (komplet leśny, bagienny, Dżungli na postaci)
  S11 prawdziwa walka w kupionym komplecie (po S09: komplet Dżungli klasy gracza): TELEPORT → chmury → Las, prawdziwe
      E przy slime'ie; bohater walki ma broń i pancerz = wzór poziomu + wpis kowala, model w walce w kupionym stroju
      (zrzut walki); bez LasPasGra — „?”
  S10 konsola bez błędów [SklepProba] i [KowalProba] (na końcu)
"""
import argparse
import importlib.util
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
KOWAL = os.path.join(REPO, "swiat", "kowal_proba")


def _modul(nazwa, sciezka):
    if nazwa in sys.modules:
        return sys.modules[nazwa]
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nazwa] = m
    spec.loader.exec_module(m)
    return m


for _s in (REPO, os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki2", "testy"), PAKIET):
    if _s not in sys.path:
        sys.path.insert(0, _s)
DN = _modul("dane_sklepu", os.path.join(PAKIET, "dane.py"))

KLATKI = os.path.join(PAKIET, "klatki")
WYNIK = os.path.join(TU, "wynik_play.json")
OKNO = "SklepProbaOkno.Ekran.Okno."
H = 'local H = game:GetService("HttpService") '
KS = H + 'local k = workspace:FindFirstChild("SklepProba") '
GR = 'local g = game:GetService("Players"):GetPlayers()[1] '
J = ('local function J(v) local t = typeof(v) if t == "Vector3" then return { v.X, v.Y, v.Z } '
     'elseif t == "table" then local o = {} for a, b in v do o[a] = J(b) end return o end return v end ')

# Kawałki Luau (szablony %s / %d / %f) — --sprawdz parsuje każdy po podstawieniu (tools/walka/luau_mini.py).
KOD = {
    "edit": H + ('local function jest(n) return workspace:FindFirstChild(n) ~= nil end '
                 'local k = workspace:FindFirstChild("SklepProba") local kw = workspace:FindFirstChild("KowalProba") '
                 'local sy = kw and kw:FindFirstChild("Sygnaly") '
                 'return H:JSONEncode({ sklep = k ~= nil and k:GetAttribute("Wygenerowane") == true, '
                 'skrot = k and k:GetAttribute("Skrot") or false, kowal = kw ~= nil, '
                 'wejscie = sy ~= nil and sy:FindFirstChild("Sklep") ~= nil, stan = jest("StanGracza"), '
                 'stroje = jest("StrojeProba"), bazar = jest("MiasteczkoBazar"), las = jest("LasPasGra") })'),
    "atr_serwera": KS + ('local w = {} for _, n in { "SerwerSklepuGotowy", "ZgodnoscLogikiSklepu", "KowalPodlaczony", '
                         '"SkrotSerwera", "LicznikKupna", "LicznikZalozen", "LicznikOdmow" } do w[n] = k:GetAttribute(n) end '
                         'return H:JSONEncode(w)'),
    "atr_klienta": KS + ('return H:JSONEncode({ gotowy = k:GetAttribute("KlientSklepuGotowy"), '
                         'podE = k:GetAttribute("PodpietePodE"), okno = k:GetAttribute("OknoOtwarte"), '
                         'zastapione = k:GetAttribute("OknoZastapione"), pawel = k:GetAttribute("ChowajOknoShop") == false })'),
    # okno sklepu Pawła (ScreenGui „Shop”, src/client/ShopClient — towar i kupno z tego serwera, od 23.11.2026), odczyt
    "okno_pawla": H + ('local pg = game:GetService("Players").LocalPlayer.PlayerGui local g = pg:FindFirstChild("Shop") '
                       'local p = g and g:FindFirstChild("Panel") local c = p and p:FindFirstChild("Card") local ceny = {} '
                       'for i = 1, 6 do local sl = p and p:FindFirstChild("ShopSlot" .. i) local t = sl and sl:FindFirstChild("Price") '
                       'local o = sl and sl:FindFirstChild("Owned") ceny[i] = (t and t.Text or "") .. "|" .. (o and o.Text or "") end '
                       'local pl = p and p:FindFirstChild("Plate") local b = c and c:FindFirstChild("BuyButton") '
                       'local n = c and c:FindFirstChild("ItemName") '
                       'return H:JSONEncode({ jest = g ~= nil and g:IsA("ScreenGui"), wlaczone = g ~= nil and g:IsA("ScreenGui") and g.Enabled, '
                       'karta = c ~= nil and c.Visible, nazwa = n and n.Text or "", przycisk = b and b.Visible and b.Text or "", '
                       'tabliczka = pl and pl.Text or "", sloty = ceny })'),
    "gracz": H + GR + ('local klasa = ({ Warrior = "wojownik", Scout = "zwiadowca", Mage = "mag" })[g:GetAttribute("Class") or ""] '
                       'or "wojownik" return H:JSONEncode({ klasa = klasa, dostepne = g:GetAttribute("KowalDostepne"), '
                       'zloto = g:GetAttribute("Gold"), poziom = g:GetAttribute("Level"), stac = g:GetAttribute("SklepStacNa"), '
                       'stroj = g:GetAttribute("StrojProba_" .. klasa) })'),
    "mody": H + GR + J + ('local s = workspace.StanGracza.Sygnaly return H:JSONEncode({ mod = J(s.Modyfikatory:Invoke("czytaj", g)), '
                          'bohater = J(s.Bohater:Invoke(g)) })'),
    "ustaw_atr": GR + 'g:SetAttribute("%s", %s) return "ok"',
    "bez_nazwy": ('local SG = game:GetService("StarterGui") for _, t in { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Chat } do '
                  'pcall(function() SG:SetCoreGuiEnabled(t, false) end) end return "ok"'),
    "postaw": GR + ('local p = Vector3.new(%f, %f, %f) local cel = Vector3.new(%f, p.Y, %f) '
                    'g.Character:PivotTo(CFrame.lookAt(p, cel)) g.Character.HumanoidRootPart.AssemblyLinearVelocity = Vector3.zero '
                    'return "ok"'),
    "kamera_za": ('local lp = game:GetService("Players").LocalPlayer local cam = workspace.CurrentCamera '
                  'local h = lp.Character and lp.Character:FindFirstChild("HumanoidRootPart") if h then '
                  'cam.CameraType = Enum.CameraType.Custom task.delay(0.05, function() cam.CFrame = CFrame.lookAt('
                  'h.Position - h.CFrame.LookVector * 10 + Vector3.new(0, 4, 0), h.Position + h.CFrame.LookVector * 4) end) '
                  'end return "ok"'),
    "kamera_przod": ('local lp = game:GetService("Players").LocalPlayer local cam = workspace.CurrentCamera '
                     'local h = lp.Character and lp.Character:FindFirstChild("HumanoidRootPart") if h then '
                     'cam.CameraType = Enum.CameraType.Scriptable cam.CFrame = CFrame.lookAt('
                     'h.Position + h.CFrame.LookVector * 5.5 + h.CFrame.RightVector * 1.2 + Vector3.new(0, 0.9, 0), h.Position + Vector3.new(0, 0.1, 0)) '
                     'end return "ok"'),
    "kamera_zwykla": 'workspace.CurrentCamera.CameraType = Enum.CameraType.Custom return "ok"',
    # zdjęcie postaci: przy stoisku zbrojmistrza kamera z przodu wpada w ladę — postać na placu startowym bazaru
    # (atrybut PunktStartuBazaru kontenera bazaru), twarzą na −X, kamera z przodu patrzy w głąb bazaru (+X) — za plecami
    # postaci zostaje tablica „RANKING SERWERA” z nazwami graczy, której nie kadrujemy
    "na_plac": H + GR + ('local b = workspace:FindFirstChild("MiasteczkoBazarGra") local p = b and b:GetAttribute("PunktStartuBazaru") '
                         'if typeof(p) ~= "Vector3" then return H:JSONEncode({ ok = false }) end p = p + Vector3.new(%f, 3, %f) '
                         'g.Character:PivotTo(CFrame.lookAt(p, p - Vector3.new(1, 0, 0))) '
                         'g.Character.HumanoidRootPart.AssemblyLinearVelocity = Vector3.zero return H:JSONEncode({ ok = true })'),
    "klient": KS + J + 'return H:JSONEncode(J(k.Sygnaly.SterowanieKlienta:Invoke("%s", %s)))',
    "zdalnie": KS + J + 'return H:JSONEncode(J(k.Zdalne.Sklep:InvokeServer("%s", %s)))',
    "emulacja": KS + 'k:SetAttribute("EmulacjaEkranu", %s) return "ok"',
    "okno_geometria": H + ('local pg = game:GetService("Players").LocalPlayer.PlayerGui local g = pg:FindFirstChild("SklepProbaOkno") '
                           'local o = g and g:FindFirstChild("Okno", true) if not o then return H:JSONEncode({}) end '
                           # względem ramki ekranu (Ekran = emulowany telefon): AbsolutePosition w ScreenGui z IgnoreGuiInset
                           # jest przesunięte o pasek u góry, więc liczymy różnicę dwóch pozycji z tym samym przesunięciem
                           'local ek = g:FindFirstChild("Ekran") or o.Parent local p0, e = ek.AbsolutePosition, ek.AbsoluteSize '
                           'local najm = 999 for _, d in o:GetDescendants() do '
                           'if (d:IsA("TextLabel") or d:IsA("TextButton")) and d.Text ~= "" then najm = math.min(najm, d.TextSize) end end '
                           'return H:JSONEncode({ dol = (o.AbsolutePosition.Y - p0.Y + o.AbsoluteSize.Y) / e.Y, '
                           'gora = (o.AbsolutePosition.Y - p0.Y) / e.Y, lewo = (o.AbsolutePosition.X - p0.X) / e.X, '
                           'prawo = (o.AbsolutePosition.X - p0.X + o.AbsoluteSize.X) / e.X, tekst = najm, ekran = { e.X, e.Y }, '
                           'ekranWGui = { (p0.X - g.AbsolutePosition.X) / g.AbsoluteSize.X, (p0.Y - g.AbsolutePosition.Y) / g.AbsoluteSize.Y, '
                           '(p0.X - g.AbsolutePosition.X + e.X) / g.AbsoluteSize.X, (p0.Y - g.AbsolutePosition.Y + e.Y) / g.AbsoluteSize.Y } })'),
    "stan_kowala": H + GR + J + ('local k = workspace.KowalProba return H:JSONEncode(J(k.Sygnaly.SterowanieSerwera:Invoke("stan", g)))'),
    # ile okien stoi po E przy zbrojowni (okno sklepu z HUD „Shop” ma się schować, póki stoi SklepProba)
    "okna_ekranu": H + ('local pg = game:GetService("Players").LocalPlayer.PlayerGui local s = pg:FindFirstChild("Shop") '
                        'local o = pg:FindFirstChild("SklepProbaOkno") local k = workspace:FindFirstChild("SklepProba") '
                        'return H:JSONEncode({ shop = s ~= nil and s:IsA("ScreenGui") and s.Enabled, sklep = o ~= nil and o.Enabled, '
                        'schowano = k and k:GetAttribute("SchowanoOknoShop") or 0 })'),
    # wejście do lasu i walka jak gracz — te same kawałki co swiat/kowal_proba/testy/proba_play.py (K06); cudze kontenery
    # (TeleportChmury, LasPasGra) tylko czytane, walkę rusza prawdziwe E przy slime'ie
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
    "stroj_w_walce": H + ('local w = {} for _, k in workspace:GetChildren() do local s = k:FindFirstChild("ScenaLokalna") '
                          'if s then for _, m in s:GetDescendants() do if m:IsA("Model") and '
                          'm:GetAttribute("Stroj") ~= nil then table.insert(w, { model = m.Name, stroj = m:GetAttribute("Stroj"), '
                          'kontener = k.Name }) end end end end return H:JSONEncode(w)'),
    "widoczny": ('local o = game:GetService("Players").LocalPlayer.PlayerGui for _, n in string.split("%s", ".") do '
                 'o = o and o:FindFirstChild(n) end if not o then return "false" end local a = o while a and a:IsA("GuiObject") '
                 'do if not a.Visible then return "false" end a = a.Parent end '
                 'return tostring(a and (not a:IsA("ScreenGui") or a.Enabled))'),
}
DOMYSLNE = {"ustaw_atr": ("Gold", "0"), "postaw": (0.0, 0.0, 0.0, 1.0, 1.0), "klient": ("stan", "nil"),
            "zdalnie": ("oferta", "nil"), "emulacja": ("nil",), "widoczny": ("HUD.X",), "na_plac": (0.0, 0.0)}


def sprawdz_kod():
    SLS = _modul("sprawdz_luau_sklepu", os.path.join(PAKIET, "sprawdz_luau_sklepu.py"))
    LM = SLS.luau_mini()
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


def katalog():
    with open(os.path.join(REPO, "swiat", "postacie", "sklep_przedmioty.json"), encoding="utf-8") as f:
        return json.load(f)


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    if "--sprawdz" in argv:
        return sprawdz_kod()
    ap = argparse.ArgumentParser(description="Próba sklepu zbrojmistrza w trybie Play")
    ap.add_argument("--studio", default=None)
    ap.add_argument("--bez-zrzutow", action="store_true")
    ap.add_argument("--tylko", default="")
    ap.add_argument("--wynik", default=None, help="plik wyniku (najlepiej poza repo)")
    a = ap.parse_args(argv)
    global WYNIK
    if a.wynik:
        WYNIK = os.path.abspath(a.wynik)
    tylko = {x.strip() for x in a.tylko.split(",") if x.strip()}
    D = DN.dane_z_przypadkami()
    K = katalog()
    P = {p["id"]: p for p in K["przedmioty"]}
    from sesja_play import SesjaPlay  # noqa: E402  (tylko odczyt: wspólna obsługa Play próby walki)
    from studio_mcp import StudioError, StudioMCP  # noqa: E402
    from cel_studio import wybierz_studio  # noqa: E402

    wyniki, dane = [], {}

    def punkt(kod, ok, opis):
        wyniki.append({"punkt": kod, "wynik": "OK" if ok is True else ("?" if ok is None else "BŁĄD"), "opis": opis})
        log("%s %s — %s" % (kod, "OK" if ok is True else ("?" if ok is None else "BŁĄD"), opis))

    def chce(kod):
        return not tylko or kod in tylko

    def przedmioty(klasa, stopien, slot=None):
        return [p["id"] for p in K["przedmioty"] if p["klasa"] == klasa and p["stopien"] == stopien and p["sprzedawany"]
                and (slot is None or p["slot"] == slot)]

    with StudioMCP() as s:
        sid = wybierz_studio(s, a.studio)
        r = s.call("execute_luau", {"code": KOD["edit"], "datamodel_type": "Edit", "studio_id": sid})
        edit = json.loads(r["text"])
    ok0 = edit.get("sklep") and edit.get("skrot") == D["skrot"] and edit.get("wejscie") and edit.get("stan")
    punkt("S00", bool(ok0), "kontenery %s; skrót %s (lokalnie %s)" % (edit, edit.get("skrot"), D["skrot"]))
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

        def zrzut(nazwa):
            if a.bez_zrzutow:
                return
            try:
                obraz = sp.zrzut()
                os.makedirs(KLATKI, exist_ok=True)
                obraz.thumbnail((1280, 1280))
                obraz.save(os.path.join(KLATKI, nazwa + ".jpg"), quality=86)
            except StudioError as e:
                log("zrzut %s: %s" % (nazwa, e))

        def gracz():
            return js(KOD["gracz"], "Server")

        def mody():
            return js(KOD["mody"], "Server")

        def atr(nazwa, wartosc):
            sp.luau(KOD["ustaw_atr"] % (nazwa, wartosc), "Server")
            time.sleep(0.4)

        def klient(polecenie, arg="nil"):
            return js(KOD["klient"] % (polecenie, arg))

        def zdalnie(akcja, pid=None):
            time.sleep(D["limit"] + 0.15)
            return js(KOD["zdalnie"] % (akcja, json.dumps(pid) if pid else "nil"))

        def przy_zbrojmistrzu(odl=2.0):
            p = D["miejsce"]["punkt"]
            sp.luau(KOD["postaw"] % (p[0], p[1] + 3.0, p[2] + odl, p[0], p[2] - 6.0), "Server")
            time.sleep(0.8)

        def kamera_za():
            sp.luau(KOD["kamera_za"])
            time.sleep(0.5)

        def zdjecie(nazwa):
            """Postać na placu startowym bazaru, kamera z przodu, zrzut; kamera wraca do zwykłej."""
            js(KOD["na_plac"] % (12.0, 0.0), "Server")
            time.sleep(1.0)
            sp.luau(KOD["kamera_przod"])
            time.sleep(0.8)
            zrzut(nazwa)
            sp.luau(KOD["kamera_zwykla"])

        def otworz_okno():
            klient("zamknij")
            klient("otworz")
            return czekaj(lambda: (lambda w: w if w.get("wiersze", 0) > 0 else None)(klient("stan")), 6) or {}

        def okno_pawla():
            return js(KOD["okno_pawla"])

        def jest_okno_pawla():
            """Okno sklepu Pawła działa (ScreenGui „Shop” + jego ShopClient ustawił ChowajOknoShop = false) — wtedy E
            zbrojowni otwiera tylko jego okno, a okno próbne zostaje dla haczyka (26.11.2026)."""
            return bool(okno_pawla().get("jest")) and bool(js(KOD["atr_klienta"]).get("pawel"))

        def zamknij_okno_pawla():
            """Jego X, jak gracz (otwarte okno i jego tło łapią kliknięcia: TELEPORT, przyciski okna próbnego)."""
            if okno_pawla().get("wlaczone"):
                sp.klik("Shop.Panel.CloseButton")
                return bool(czekaj(lambda: not okno_pawla().get("wlaczone"), 3, 0.3))
            return None

        def otworz_okno_pawla():
            """Świeże okno Pawła prawdziwym E (otwarcie pyta serwer o ofertę) — po zamknięciu poprzedniego."""
            zamknij_okno_pawla()
            klient("zamknij")
            przy_zbrojmistrzu()
            kamera_za()
            sp.klawisz("E")
            return czekaj(lambda: (lambda o: o if o.get("wlaczone") and any(x != "|" for x in o.get("sloty") or []) else None)(
                okno_pawla()), 6)

        def klik_w_oknie_pawla(pid):
            """Przedmiot na ladzie w oknie Pawła: sloty 1–6, potem następna szóstka (RerollButton); karta → BuyButton
            (BUY albo EQUIP — o akcji decyduje jego okno po stanie z oferty). → slot, strona, napis przycisku."""
            nazwa = {w.get("id"): w.get("nazwa") for w in zdalnie("oferta").get("widok", {}).get("oferta", [])}.get(pid)
            if not nazwa or not otworz_okno_pawla():
                return None
            for strona in range(6):
                for i in range(1, 7):
                    sp.klik("Shop.Panel.ShopSlot%d" % i)
                    time.sleep(0.35)
                    o = okno_pawla()
                    if o.get("karta") and o.get("nazwa") == nazwa:
                        napis = o.get("przycisk")
                        sp.klik("Shop.Panel.Card.BuyButton")
                        return {"slot": i, "strona": strona, "przycisk": napis, "nazwa": nazwa}
                sp.klik("Shop.Panel.RerollButton")
                time.sleep(0.35)
            return {"brak": nazwa}

        sp.luau(KOD["bez_nazwy"])
        time.sleep(1.0)
        # ------------------------------------------------------------------ S01
        if chce("S01"):
            cl = czekaj(lambda: (lambda w: w if w.get("gotowy") else None)(js(KOD["atr_klienta"])), 30)
            sv = js(KOD["atr_serwera"], "Server")
            ok = (bool(cl) and cl.get("podE") and sv.get("SerwerSklepuGotowy") and sv.get("KowalPodlaczony")
                  and str(sv.get("ZgodnoscLogikiSklepu")).startswith("OK") and sv.get("SkrotSerwera") == D["skrot"])
            punkt("S01", bool(ok), "klient %s; serwer %s" % (cl, sv))
        atr("Level", "30")
        atr("Gold", "20000")
        g0 = gracz()
        k = g0["klasa"]
        # ------------------------------------------------------------------ S02 prawdziwe E
        if chce("S02") and jest_okno_pawla():
            # 26.11.2026: okno sklepu Pawła (44f6579, 23.11) zastąpiło okno próbne — prawdziwe E otwiera jego okno
            # i tylko ono; towar na jego ladzie pochodzi z oferty tego serwera (Zdalne/Sklep "oferta")
            ok = otworz_okno_pawla()
            time.sleep(1.0)
            ekr = js(KOD["okna_ekranu"])
            kl = js(KOD["atr_klienta"])
            op = okno_pawla()
            zrzut("s02_okno_sklepu")
            of = zdalnie("oferta").get("widok", {}).get("oferta", [])
            na_ladzie = sum(1 for x in op.get("sloty") or [] if x != "|")
            punkt("S02", bool(ok) and len(of) == len([p for p in K["przedmioty"] if p["klasa"] == k and p["sprzedawany"]])
                  and ekr.get("shop") is True and ekr.get("sklep") is False and kl.get("zastapione") == "Shop" and na_ladzie > 0,
                  "okno Pawła po E: %s (towar w %d z 6 slotów, tabliczka „%s”), okno próbne: %s (OknoZastapione %s), "
                  "pozycji w ofercie serwera %d; okna na ekranie %s" % (bool(ok), na_ladzie, op.get("tabliczka"), ekr.get("sklep"),
                                                                     kl.get("zastapione"), len(of), ekr))
            dane["S02"] = {"okna": ekr, "okno_pawla": op}
        elif chce("S02"):
            # czcionka okna (FredokaOne) nie ma polskich liter — Roblox dociąga zastępczą przy pierwszym pokazaniu tekstu
            # i przez kilka sekund „ś”, „ę”, „ż” są puste; rozgrzewka haczykiem, żeby zrzut po E był czytelny
            przy_zbrojmistrzu()
            otworz_okno()
            time.sleep(4.0)
            klient("zamknij")
            przy_zbrojmistrzu()
            kamera_za()
            sp.klawisz("E")
            ok = czekaj(lambda: js(KOD["atr_klienta"]).get("okno"), 6)
            st = czekaj(lambda: (lambda w: w if w.get("wiersze", 0) > 0 else None)(klient("stan")), 6) or {}
            time.sleep(1.0)
            ekr = js(KOD["okna_ekranu"])
            zrzut("s02_okno_sklepu")
            of = zdalnie("oferta").get("widok", {}).get("oferta", [])
            punkt("S02", bool(ok) and len(of) == len([p for p in K["przedmioty"] if p["klasa"] == k and p["sprzedawany"]])
                  and ekr.get("sklep") is True and ekr.get("shop") is False,
                  "okno po E: %s, zakładka %s, wierszy %s, pozycji w ofercie %d; okna na ekranie %s"
                  % (ok, st.get("zakladka"), st.get("wiersze"), len(of), ekr))
            dane["S02"] = {"okna": ekr}
        # ------------------------------------------------------------------ S03 kupno kliknięciem
        pas = przedmioty(k, "las", "Belt")[0]
        if chce("S03") and jest_okno_pawla():
            # kupno prawdziwym kliknięciem w oknie Pawła: slot z przedmiotem → karta → BUY (jego okno woła ten serwer)
            przed = gracz()
            klik = klik_w_oknie_pawla(pas)
            po = czekaj(lambda: (lambda g: g if pas in (g.get("dostepne") or "").split(",") else None)(gracz()), 6) or gracz()
            time.sleep(0.6)
            op = okno_pawla()
            zrzut("s03_po_kupnie")
            ok = (bool(klik) and not (klik or {}).get("brak") and (klik or {}).get("przycisk") == "BUY"
                  and pas in (po.get("dostepne") or "").split(",") and (przed.get("zloto") or 0) - (po.get("zloto") or 0) == P[pas]["cena"])
            punkt("S03", bool(ok), "kupno w oknie Pawła %s; %s za %d Złota: Złoto %s → %s; tabliczka jego okna „%s”"
                  % (klik, pas, P[pas]["cena"], przed.get("zloto"), po.get("zloto"), op.get("tabliczka")))
            dane["S03"] = {"przed": przed, "po": po, "klik": klik}
        elif chce("S03"):
            przy_zbrojmistrzu()
            otworz_okno()
            klient("zakladka", '"las"')
            time.sleep(0.5)
            przed = gracz()
            klik = sp.klik(OKNO + "Lista.Wiersz_" + pas + ".Przycisk")
            po = czekaj(lambda: (lambda g: g if pas in (g.get("dostepne") or "").split(",") else None)(gracz()), 6) or gracz()
            st = klient("stan")
            zrzut("s03_po_kupnie")
            ok = (pas in (po.get("dostepne") or "").split(",") and (przed.get("zloto") or 0) - (po.get("zloto") or 0) == P[pas]["cena"])
            punkt("S03", bool(ok), "klik %s; %s za %d Złota: Złoto %s → %s; napis „%s”"
                  % (klik, pas, P[pas]["cena"], przed.get("zloto"), po.get("zloto"), st.get("komunikat")))
            dane["S03"] = {"przed": przed, "po": po}
        # ------------------------------------------------------------------ S04 strój na postaci
        if chce("S04"):
            g1 = gracz()
            klient("zamknij")
            zamknij_okno_pawla()
            zdjecie("s04_postac_po_kupnie")
            punkt("S04", pas in (g1.get("stroj") or "").split(","), "strój: %s" % g1.get("stroj"))
        # ------------------------------------------------------------------ S05 reguła zakładania
        helm_b, helm_l = przedmioty(k, "bagno", "Helmet")[0], przedmioty(k, "las", "Helmet")[0]
        if chce("S05"):
            przy_zbrojmistrzu()
            r1 = zdalnie("kup", helm_b)
            r2 = zdalnie("kup", helm_l)
            g2 = gracz()
            if jest_okno_pawla():
                # „Załóż” = EQUIP na karcie w oknie Pawła (dla posiadanego przedmiotu jego okno wysyła "zaloz")
                dane["S05_klik"] = klik_w_oknie_pawla(helm_l)
            else:
                otworz_okno()
                klient("zakladka", '"las"')
                time.sleep(0.5)
                sp.klik(OKNO + "Lista.Wiersz_" + helm_l + ".Przycisk")
            g3 = czekaj(lambda: (lambda g: g if helm_l in (g.get("stroj") or "").split(",") else None)(gracz()), 6) or gracz()
            zrzut("s05_zaloz_recznie")
            ok = (r1.get("zalozony") is True and r2.get("ok") is True and r2.get("zalozony") is False
                  and helm_b in (g2.get("stroj") or "").split(",") and helm_l in (g3.get("stroj") or "").split(",")
                  and helm_b not in (g3.get("stroj") or "").split(","))
            punkt("S05", bool(ok), "wyższy %s założony: %s; niższy %s założony sam: %s; po „Załóż”: %s"
                  % (helm_b, r1.get("zalozony"), helm_l, r2.get("zalozony"), g3.get("stroj")))
        # ------------------------------------------------------------------ S06 walka w kupionym przedmiocie
        if chce("S06"):
            przy_zbrojmistrzu()
            bron = przedmioty(k, "las", "Weapon")[0]
            m0 = mody()
            r = zdalnie("kup", bron)
            m1 = mody()
            dod = P[bron]["baza"].get("bron", 0)
            b0, b1 = m0["bohater"]["bron"]["obrazenia"], m1["bohater"]["bron"]["obrazenia"]
            ok = (r.get("ok") is True and r.get("zalozony") is True and "kowal" in m1["mod"].get("zrodla", [])
                  and abs((m1["mod"].get("bron", 0) - m0["mod"].get("bron", 0)) - dod) < 1e-6 and b1 > b0)
            punkt("S06", bool(ok), "%s (broń +%s): wpis kowala %s → %s, obrażenia bohatera %s → %s"
                  % (bron, dod, m0["mod"].get("bron"), m1["mod"].get("bron"), b0, b1))
            dane["S06"] = {"przed": m0, "po": m1}
        # ------------------------------------------------------------------ S07 odmowy
        if chce("S07"):
            przy_zbrojmistrzu()
            cel = przedmioty(k, "dzungla", "Belt")[0]
            przed = js(KOD["stan_kowala"], "Server").get("dane")
            w = {}
            atr("Gold", str(P[cel]["cena"] - 150))
            w["za_malo_zlota"] = zdalnie("kup", cel)
            atr("Gold", "20000")
            atr("Level", str(P[cel]["poziom"] - 1))
            w["za_niski_poziom"] = zdalnie("kup", cel)
            atr("Level", "30")
            w["masz"] = zdalnie("kup", pas)
            inna = next(p["id"] for p in K["przedmioty"] if p["klasa"] != k and p["sprzedawany"] and p["stopien"] == "las")
            w["inna_klasa"] = zdalnie("kup", inna)
            w["nieznany_przedmiot"] = zdalnie("kup", "nie_ma")
            czesc = next((p["id"] for p in K["przedmioty"] if p["klasa"] == k and not p["sprzedawany"]), None)
            if czesc:
                w["czesc_zbroi"] = zdalnie("kup", czesc)
            przy_zbrojmistrzu(60.0)
            w["daleko"] = zdalnie("kup", cel)
            przy_zbrojmistrzu()
            po = js(KOD["stan_kowala"], "Server").get("dane")
            zle = [n for n, r in w.items() if r.get("ok") is not False or r.get("powod") != n]
            punkt("S07", not zle and przed == po and gracz().get("zloto") == 20000,
                  "odmowy: %s; teksty: %s; dane bez zmian: %s" % ({n: r.get("powod") for n, r in w.items()},
                                                                  [r.get("tekst") for r in w.values()], przed == po))
        # ------------------------------------------------------------------ S08 mały ekran
        if chce("S08"):
            zamknij_okno_pawla()
            przy_zbrojmistrzu()
            klient("zamknij")
            sp.luau(KOD["emulacja"] % "Vector2.new(667, 375)")
            st = otworz_okno()
            time.sleep(0.8)
            geo = js(KOD["okno_geometria"])
            zrzut("s08_okno_maly_ekran")
            sp.luau(KOD["emulacja"] % "nil")
            klient("zamknij")
            ok8 = ((st.get("rozmiarTekstu") or 0) >= 12 and (geo.get("tekst") or 0) >= 12 and geo.get("dol", 2) <= 1.0
                   and geo.get("gora", -1) >= 0)
            opis8 = "tekst %s pt (najmniejszy w oknie %s), okno %s" % (st.get("rozmiarTekstu"), geo.get("tekst"), geo)
            if jest_okno_pawla():
                # okno próbne nie pokazuje się już graczowi — jego wynik nie mówi nic o grze; okna Pawła na telefonie
                # ta próba nie mierzy
                punkt("S08", None if ok8 else False, "okno zastąpione przez okno Pawła — okno próbne na małym ekranie: " + opis8)
            else:
                punkt("S08", ok8, opis8)
        # ------------------------------------------------------------------ S09 trzy klasy w trzech stopniach
        if chce("S09"):
            zrobione = []
            for klasa_gry, klasa in (("Warrior", "wojownik"), ("Scout", "zwiadowca"), ("Mage", "mag")):
                atr("Class", json.dumps(klasa_gry))
                atr("Gold", "100000")
                time.sleep(1.0)
                for stopien in ("las", "bagno", "dzungla"):
                    przy_zbrojmistrzu()
                    kupione = [zdalnie("kup", pid) for pid in przedmioty(klasa, stopien)]
                    stroj = (gracz().get("stroj") or "").split(",")
                    for pid in przedmioty(klasa, stopien):
                        if pid not in stroj:     # kupiony wcześniej (np. hełm z S05) — gracz zakłada go przyciskiem „Załóż”
                            zdalnie("zaloz", pid)
                    g = gracz()
                    stroj = (g.get("stroj") or "").split(",")
                    caly = all(pid in stroj for pid in przedmioty(klasa, stopien))
                    zdjecie("s09_%s_%s" % (klasa, stopien))
                    zrobione.append((klasa, stopien, caly, sum(1 for r in kupione if r.get("ok") is True)))
            atr("Class", json.dumps({"wojownik": "Warrior", "zwiadowca": "Scout", "mag": "Mage"}[k]))
            punkt("S09", all(x[2] for x in zrobione), "komplety na postaci (klasa, stopień, cały, kupionych): %s" % zrobione)
        # ------------------------------------------------------------------ S11 walka w kupionym komplecie
        def do_lasu():
            """TELEPORT → chmury → strzałka w prawo + Enter = Las, potem koniec przelotu (jak kowal K06 i proba_dymna D02)."""
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
            for _ in range(6):
                c = js(KOD["slime"])
                if not c.get("p"):
                    return {"blad": "brak wolnego slime'a"}
                q = c["p"]
                sp.luau(KOD["postaw"] % (q[0] - 4, q[1] + 3.2, q[2], q[0], q[2]), "Server")
                kamera_za()
                sp.klawisz("E")
                if czekaj(lambda: js(KOD["postac"]).get("walka"), 5, 0.4):
                    break
            else:
                return {"blad": "E nie ruszyło walki"}
            m = mody()
            time.sleep(1.5)
            stroje = czekaj(lambda: js(KOD["stroj_w_walce"]) or None, 6, 0.5) or []
            time.sleep(1.0)
            zrzut("s11_walka_w_komplecie")
            sp.klik("TestWalki2Cutscenka.Kadr.Tempo.Tempo4.Przycisk")
            sciezka_karty = "TestWalki2Cutscenka.Kadr.Wynik.Karta.Zamknij.Przycisk"
            karta = czekaj(lambda: sp.luau(KOD["widoczny"] % sciezka_karty).strip() == "true", 60, 1.0)
            sp.klik(sciezka_karty)
            czekaj(lambda: js(KOD["postac"]).get("kamera") == "Custom", 10, 0.5)
            return {"bohater": m["bohater"], "mod": m["mod"], "stroje": stroje, "karta": bool(karta)}

        if chce("S11"):
            g = gracz()
            kl = g["klasa"]
            stroj = (g.get("stroj") or "").split(",")
            komplet = przedmioty(kl, "dzungla")
            if not all(pid in stroj for pid in komplet):        # bez S09 w tym przebiegu: kupno kompletu Dżungli teraz
                atr("Gold", "100000")
                przy_zbrojmistrzu()
                for pid in komplet:
                    zdalnie("kup", pid)
                g = gracz()
                stroj = (g.get("stroj") or "").split(",")
            L = g.get("poziom") or 1
            m0 = mody()
            wynik = {"komplet": komplet, "w_stroju": all(pid in stroj for pid in komplet), "mod": m0["mod"]}
            if edit.get("las"):
                wynik["las"] = do_lasu()
                if not wynik["las"].get("blad"):
                    wynik["walka"] = walka_ze_slimem()
            dane["S11"] = wynik
            wk = wynik.get("walka") or {}
            b, md = wk.get("bohater") or {}, wk.get("mod") or {}
            bron_ok = abs((b.get("bron") or {}).get("obrazenia", -1) - (8 + 4 * L + (md.get("bron") or 0))) < 1e-6
            panc_ok = abs((b.get("pancerz_przedmiotow") or -1) - (3 + 1.5 * L + (md.get("pancerz") or 0))) < 1e-6
            w_walce = any(all(pid in (x.get("stroj") or "").split(",") for pid in komplet) for x in wk.get("stroje") or [])
            ok = (wynik["w_stroju"] and (md.get("bron") or 0) > 0 and (md.get("pancerz") or 0) > 0 and bron_ok and panc_ok
                  and w_walce and wk.get("karta"))
            punkt("S11", bool(ok) if edit.get("las") else None,
                  "komplet Dżungli %s na postaci %s; wpis kowala %s; las %s; w walce broń %s / pancerz %s (wzór L%d + wpis: "
                  "%s / %s), model w walce w komplecie %s, karta wyniku %s"
                  % (kl, wynik["w_stroju"], md or m0["mod"], wynik.get("las"), (b.get("bron") or {}).get("obrazenia"),
                     b.get("pancerz_przedmiotow"), L, 8 + 4 * L + (md.get("bron") or 0), 3 + 1.5 * L + (md.get("pancerz") or 0),
                     w_walce, wk.get("karta")))
        # ------------------------------------------------------------------ S10 konsola (na końcu)
        if chce("S10"):
            kons = sp.konsola()
            zle = [w for w in kons.splitlines() if "[SklepProba]" in w or "SklepProba." in w or "[KowalProba]" in w]
            punkt("S10", not zle, "wiersze konsoli o sklepie i kowalu: %d%s" % (len(zle), (" — " + " | ".join(zle[:5])) if zle else ""))
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
