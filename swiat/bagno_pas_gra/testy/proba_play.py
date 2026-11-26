# -*- coding: utf-8 -*-
"""Próba „Bagna w grze” w Roblox Studio (tryb Play) — część B. Sama włącza i wyłącza Play, niczego nie zapisuje w
miejscu i niczego nie publikuje.

    python -B swiat/bagno_pas_gra/testy/proba_play.py <folder wyników POZA repo> [--studio <id>] [--bez-zrzutow]
    python -B swiat/bagno_pas_gra/testy/proba_play.py --sprawdz     # bez Studio: parsuje każdy kawałek Luau (luau_mini)

Warunki (tryb Edit): Workspace/BagnoPas (mapa, swiat/bagno_pas) i Workspace/BagnoPasGra (swiat/bagno_pas_gra/zbuduj.py),
Workspace/LasPas i LasPasGra (skrypty po zmianach z 17.11), Workspace/TestWalki2 z aktorami Bagna, Workspace/TeleportChmury;
najlepiej też Workspace/StanGracza (punkt B08) i MiasteczkoBazarGra (Kamień Powrotu). Wyniki (wyniki.json, lista.txt)
idą do podanego folderu POZA repozytorium (mogą zawierać nazwę konta); zrzuty (lista graczy i czat schowane) →
swiat/bagno_pas_gra/klatki/. Przed B13 próba wyciąga okno Studio na wierzch (tools/studio_okno.py --na-wierzch) —
w tle Studio rysuje 15 kl./s i pomiar klatki nic nie mówi.

LISTA KONTROLNA (OK / BŁĄD / ?):
  B00 w Edit: mapa i gra Bagna, las-pas, prototyp z 5 aktorami Bagna, teleport; LasPas/ZapowiedzBagna usunięta
  B01 gotowość: serwer Bagna (StanMapy, StanBiomu ok, SzablonyGotowe, potwory przy 1 graczu jak w danych (krótki pas: 8), zgodność logiki
      70/70 i 39/39, Przekierowanie „nie_ten_biom”), las wie o Bagnie (NastepnyBiomJest, bez ZaBrama), klienci gotowi
      (tryb „aktorzy”)
  B02 bez bramy lasu: uchwyt PrzeniesDoBagna → „zamkniete”, teleport przez chmury nie ma Bagna, gracz postawiony w
      głębi Bagna jest cofnięty przed bramę lasu z komunikatem
  B03 droga bramą lasu (brama otwarta haczykiem lasu, przelot lasu wyłączony): bieg za bramę → pierwszy przelot Bagna
      (fazy, czas przelotu krótkiego planu ± 1,5 s, ryk Strażnika Topieli, kamera Custom, WidzialPrzelotBagna), przelot lasu nie ruszył
  B04 droga chmurami: Bagno otwarte w teleporcie (ten sam stan bramy), przeniesienie przez uchwyt PrzeniesDoBagna na
      Pomost, bez drugiego przelotu
  B04b TELEPORT do krainy, w której gracz już jest (D-096): z głębi Bagna wybór „Bagno” → przybycie (inkubator,
      Kamień Powrotu), bez odmowy i bez drugiego przelotu
  B05 potwory w przegrodach: 30 s próbkowania — 0 poza polem strefy
  B06 walka z każdym gatunkiem w trybie testowym (TestBohater, poziom „auto”): r1 Rechotek, b1 Bulgotnik, k1 Kłodokłap,
      t1 Ropucha — E (zapas: haczyk walcz), właściwy gatunek, walka do końca, kamera i postać wracają; mostek pomijania
      prototypu przyjął walki Bagna (SerwerMostekWalk)
  B07 POMIŃ przy znanym gatunku: druga walka z Rechotkiem bez TestBezSesji → przycisk POMIŃ, spacja, serwer „ok”
  B08 zwykły tryb (Workspace/StanGracza): Level = 11 → bohater walczy na 11. poziomie (Rechotki r1 mają 10, więc
      „→11” odróżnia bohatera z danych gracza od reguły „auto”), po walce łup (OstatniLup,
      Gold albo XP) — bez StanGracza „?”
  B09 brama do Dżungli zamknięta: gracz za nią cofnięty z komunikatem, wrota z kolizją
  B10 Strażnik Topieli: przegrana (Wojownik poz. 10) → brama dalej zamknięta; wygrana (Zwiadowca poz. 20, do 4 ziaren)
      → PokonalStraznikaBagna, jeden baner „STRAŻNIK TOPIELI POKONANY!” z podpisem o Dżungli, wrota u zwycięzcy bez
      kolizji (na serwerze z kolizją), przejście za bramę bez cofnięcia, tabliczka „DŻUNGLA — WKRÓTCE”
  B11 Kamień Powrotu: prawdziwe E → miasteczko (bazar albo stare)
  B12 mgła tylko u gracza: w Bagnie waga Bagna 1 i lasu 0 (gęstość ok. 0,42), w lesie odwrotnie; serwer bez zmian
  B13 koszt przy oknie na wierzchu: klatka klienta w Kępach (śr., p95, maks.), widoki potworów i ich bryły
  B14 konsola: bez błędów [BagnoPasGra] / BagnoPasGra
"""
import io
import json
import os
import re
import subprocess
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "tools", "walka"),
           os.path.join(REPO, "swiat", "test_walki_roblox"), os.path.join(REPO, "swiat", "test_walki2", "testy")):
    if _s not in sys.path:
        sys.path.insert(0, _s)

KLATKI = os.path.join(PAKIET, "klatki")
GATUNKI = {"r1": "rechotek", "b1": "bulgotnik", "k1": "klodoklap", "t1": "ropucha_z_chatka"}
AKTORZY = ["rechotek", "bulgotnik", "klodoklap", "ropucha_z_chatka", "straznik_topieli"]
NASZE = ("BagnoPasGra",)


def _geometria():
    """Położenia i czasy z krótkich map gry (D-096, swiat/biomy/przycinarka.py) — bez liczb pasa wpisanych na sztywno."""
    import importlib.util

    def wczytaj(sciezka):
        with open(os.path.join(REPO, *sciezka.split("/")), encoding="utf-8") as f:
            return json.load(f)
    zl, zb = wczytaj("swiat/las_pas/krotki/znaczniki.json"), wczytaj("swiat/bagno_pas/krotki/znaczniki.json")
    x0 = float(wczytaj("swiat/bagno_pas/krotki/plan_bagna.json")["swiat"]["X0"])

    def m(z, i):
        return next(x for x in z["miejsca"] if x["id"] == i)["punkt_swiat"]
    spec = importlib.util.spec_from_file_location("logika_potworow_proby", os.path.join(REPO, "swiat", "las_potwory", "logika.py"))
    lg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lg)
    k = zb["przelot_kamery"]
    return {"brama_lasu": m(zl, "brama_bagna")[0], "przybycie": m(zb, "przybycie")[0], "brama": m(zb, "brama_dzungli")[0],
            "las_srodek": (m(zl, "przybycie")[0] + m(zl, "brama_bagna")[0]) / 2.0,
            "strefy": {s["id"]: x0 + s["srodek"][0] for s in zb["strefy"]},
            "potworow_1": sum(lg.cel(s["naraz"], s["max"], 1) for s in zb["strefy"]) + 1,
            "przelot": k["czas_s"], "zatrzymanie": k["zatrzymanie_od_s"]}


G = _geometria()

# 18.11.2026 (swiat/cutscenka_biomu): gdy Workspace/CutscenkaBiomu przejął biom, punkty o przelocie sprawdzają nową
# cutscenkę; bez tego kontenera — stary przelot pasa. Wspólna pomoc: swiat/cutscenka_biomu/pomoc_prob.py
import importlib.util as _ilu  # noqa: E402
_sp = _ilu.spec_from_file_location("cutscenka_pomoc_prob", os.path.join(REPO, "swiat", "cutscenka_biomu", "pomoc_prob.py"))
PP = _ilu.module_from_spec(_sp)
_sp.loader.exec_module(PP)

# D-107 (19.11.2026, walka bez przestojów): liczby potworów i czasy odradzania z DANYCH GRY (generator), nie z planu
# mapy; wspólne punkty prób D1–D4 trzech biomów: swiat/las_pas_gra/testy/pomoc_d107.py
_spd = _ilu.spec_from_file_location("pomoc_d107", os.path.join(REPO, "swiat", "las_pas_gra", "testy", "pomoc_d107.py"))
D107 = _ilu.module_from_spec(_spd)
_spd.loader.exec_module(D107)
G["d107"] = D107.wczytaj_liczby(REPO, "bagno_pas_gra")
G["potworow_1"] = G["d107"]["razem1"]


def tp(t):
    """Chwila zrzutu z projektu (lot 10,5 s, postój od 10,5) → ta sama chwila krótkiego przelotu."""
    return t * G["zatrzymanie"] / 10.5 if t <= 10.5 else G["zatrzymanie"] + (t - 10.5)

KB = 'local k = workspace:FindFirstChild("BagnoPasGra") local H = game:GetService("HttpService") '
GR = 'local gracz = game:GetService("Players"):GetPlayers()[1] '
HRP = 'local hrp = game:GetService("Players"):GetPlayers()[1].Character.HumanoidRootPart '
J = ('local H = game:GetService("HttpService") local function J(v) local t = typeof(v) if t == "Vector3" then return { v.X, v.Y, v.Z } '
     'elseif t == "table" then local o = {} if #v > 0 then for i, b in ipairs(v) do o[i] = J(b) end '
     'else for a, b in v do o[tostring(a)] = J(b) end end return o '
     'elseif t == "number" and (v ~= v or v == math.huge or v == -math.huge) then return tostring(v) '
     'elseif t == "Instance" then return v:GetFullName() end return v end ')

# Kawałki Luau (szablony %s / %d / %f) — --sprawdz parsuje każdy po podstawieniu zer (tools/walka/luau_mini.py)
KOD = {
    "edit": ('local H = game:GetService("HttpService") local function jest(n) local o = workspace:FindFirstChild(n) '
             'return o ~= nil and o:GetAttribute("Wygenerowane") == true end '
             'local a = workspace:FindFirstChild("TestWalki2") a = a and a:FindFirstChild("Aktorzy") local akt = {} '
             'for _, n in { %s } do akt[n] = a ~= nil and a:FindFirstChild(n) ~= nil end '
             'local las = workspace:FindFirstChild("LasPas") local atm = game:GetService("Lighting"):FindFirstChildOfClass("Atmosphere") '
             'return H:JSONEncode({ mapa = jest("BagnoPas"), gra = jest("BagnoPasGra"), las = jest("LasPas"), pas = jest("LasPasGra"), '
             'teleport = jest("TeleportChmury"), stan = jest("StanGracza"), bazar = jest("MiasteczkoBazarGra"), aktorzy = akt, '
             'zapowiedz = las ~= nil and las:FindFirstChild("ZapowiedzBagna") ~= nil, gestosc = atm and atm.Density or -1 })'),
    "kont_atr": 'local o = {} local f = workspace:FindFirstChild("%s") if not f then return H:JSONEncode({ brak = true }) end '
                'for _, n in { %s } do o[n] = J(f:GetAttribute(n)) end return H:JSONEncode(o)',
    "gracz_atr": GR + 'local o = {} for _, n in { %s } do o[n] = J(gracz:GetAttribute(n)) end return H:JSONEncode(o)',
    "ustaw_atr": 'local k = workspace:FindFirstChild("%s") if k then k:SetAttribute("%s", %s) end return "ok"',
    "gracz_ustaw": GR + 'gracz:SetAttribute("%s", %s) return "ok"',
    "hak": 'local k = workspace:FindFirstChild("%s") return H:JSONEncode(J(k.Sygnaly.%s:Invoke("%s"%s)))',
    "uchwyt_bagna": KB + GR + 'return H:JSONEncode(J(k.Sygnaly.PrzeniesDoBagna:Invoke(gracz, { punkt = "przybycie" })))',
    "teleport": GR + 'local t = workspace:FindFirstChild("TeleportChmury") if not t then return H:JSONEncode({ brak = true }) end '
                     'return H:JSONEncode(J(t.Sygnaly.SterowanieSerwera:Invoke("%s", %s)))',
    "las_poza": ('local k = workspace:FindFirstChild("LasPasGra") '
                 'return H:JSONEncode({ nastepny = k ~= nil and k:GetAttribute("NastepnyBiomJest") == true, '
                 'zaBrama = k ~= nil and k:FindFirstChild("ZaBrama") ~= nil })'),
    "poz": HRP + 'return H:JSONEncode(J(hrp.Position))',
    "przestaw": HRP + 'local p = Vector3.new(%f, %f, %f) hrp.Parent:PivotTo(CFrame.lookAt(p, p + Vector3.new(%f, 0, 0))) '
                      'hrp.AssemblyLinearVelocity = Vector3.zero return "ok"',
    "komunikat": KB + ('local pg = game:GetService("Players").LocalPlayer.PlayerGui local e = pg:FindFirstChild("BagnoPasGraEkran") '
                       'local l = e and e:FindFirstChild("Komunikat") return H:JSONEncode({ widoczny = l ~= nil and l.Visible, '
                       'tekst = l and l.Text or "" })'),
    "wrota": ('local m = workspace:FindFirstChild("BagnoPas") local w = m and m:FindFirstChild("BramaDzungli") '
              'w = w and w:FindFirstChild("Wrota") local k = workspace:FindFirstChild("BagnoPasGra") '
              'local n, kol, prz = 0, 0, 0 if w then for _, d in w:GetDescendants() do if d:IsA("BasePart") then n += 1 '
              'if d.CanCollide then kol += 1 end if d.LocalTransparencyModifier > 0.99 then prz += 1 end end end end '
              'local z = k and k:FindFirstChild("Brama") z = z and z:FindFirstChild("Zapora") '
              'return H:JSONEncode({ czesci = n, kolizja = kol, niewidoczne = prz, zapora = z ~= nil and z.CanCollide })'),
    "w_polach": KB + ('local D = require(k.Moduly.DanePotworow) local pola = {} for _, s in D.strefy do pola[s.id] = s.pole end '
                      'local n, poza, przyklad = 0, 0, nil for _, c in k.Stan:GetChildren() do local p = c:GetAttribute("Pozycja") '
                      'local s = pola[c:GetAttribute("Strefa")] if p and s then n += 1 if p.X < s.x1 - 0.5 or p.X > s.x2 + 0.5 '
                      'or p.Z < s.z1 - 0.5 or p.Z > s.z2 + 0.5 then poza += 1 przyklad = c.Name end end end '
                      'return H:JSONEncode({ n = n, poza = poza, przyklad = przyklad or false })'),
    "potwor_w_strefie": KB + ('local naj for _, c in k.Stan:GetChildren() do if c:GetAttribute("Strefa") == "%s" '
                              'and c:GetAttribute("Stan") ~= "zajety" then naj = c break end end '
                              'if not naj then return H:JSONEncode({}) end '
                              'return H:JSONEncode({ id = naj.Name, p = J(naj:GetAttribute("Pozycja")), '
                              'poziom = naj:GetAttribute("Poziom"), gatunek = naj:GetAttribute("Gatunek") })'),
    "pozycja_potwora": KB + 'local c = k.Stan:FindFirstChild("%s") return H:JSONEncode(J(c and c:GetAttribute("Pozycja") or false))',
    "klient_potworow": KB + 'return H:JSONEncode(J(k.Sygnaly.SterowanieKlienta:Invoke("stan")))',
    "walcz": KB + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("walcz", "%s"))',
    "bohater_t1": KB + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("bohater", "%s", "%s"))',
    "odtw": 'return H:JSONEncode(J(workspace.TestWalki2.Sygnaly.Sterowanie:Invoke(%s)))',
    "kamera_zwykla": ('local c = workspace.CurrentCamera local p = game:GetService("Players").LocalPlayer '
                      'local h = p.Character and p.Character:FindFirstChildOfClass("Humanoid") c.CameraType = Enum.CameraType.Custom '
                      'if h then c.CameraSubject = h end return "ok"'),
    "kamera_za": ('local cam = workspace.CurrentCamera local p = game:GetService("Players").LocalPlayer '
                  'local h = p.Character and p.Character:FindFirstChild("HumanoidRootPart") if not h then return "brak" end '
                  'local f = h.CFrame.LookVector cam.CameraType = Enum.CameraType.Scriptable '
                  'cam.CFrame = CFrame.lookAt(h.Position - f * 10 + Vector3.new(0, 4, 0), h.Position + f * 6) return "ok"'),
    "podpowiedz": KB + ('local st = k.Sygnaly.SterowanieKlienta:Invoke("stan") return H:JSONEncode({ podpowiedz = st.podpowiedz, '
                        'najblizszy = st.najblizszy, walka = st.walka })'),
    "wybor_klasy": ('local H = game:GetService("HttpService") local p = game:GetService("Players").LocalPlayer '
                    'local g = p.PlayerGui:FindFirstChild("ClassSelect") local c = workspace.CurrentCamera '
                    'return H:JSONEncode({ ekran = g ~= nil and g.Enabled, kamera = c.CameraType.Name, '
                    'podpowiedzi = game:GetService("ProximityPromptService").Enabled })'),
    "bez_nazwy": ('local SG = game:GetService("StarterGui") for _, t in { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Chat } do '
                  'pcall(function() SG:SetCoreGuiEnabled(t, false) end) end return "ok"'),
    "gotowy_klient": 'local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)',
    "imie": 'return game:GetService("Players"):GetPlayers()[1].Name',
    # banery po walce ze Strażnikiem: lokalny słuchacz liczy napisy z „POKONANY!” i „OTWARTA!” (oba kontenery GUI)
    "sledz_banery": (KB + 'local pg = game:GetService("Players").LocalPlayer.PlayerGui k:SetAttribute("ProbaBanery", "") '
                     'pg.DescendantAdded:Connect(function(d) if d:IsA("TextLabel") then task.wait(0.1) '
                     'local t = d.Text if string.find(t, "POKONANY!", 1, true) or string.find(t, "OTWARTA!", 1, true) then '
                     'local p = d.Parent and d.Parent:FindFirstChild("Podpis") '
                     'k:SetAttribute("ProbaBanery", (k:GetAttribute("ProbaBanery") or "") .. t .. " / " .. (p and p.Text or "") .. "|") '
                     'end end end) return "ok"'),
    "atmosfera": ('local H = game:GetService("HttpService") local a = game:GetService("Lighting"):FindFirstChildOfClass("Atmosphere") '
                  'local function w(n) local k = workspace:FindFirstChild(n) return k and k:GetAttribute("WagaMglyPasa") or false end '
                  'return H:JSONEncode({ gestosc = a and a.Density or -1, bagno = w("BagnoPasGra"), las = w("LasPasGra") })'),
    "klatka": ('local H = game:GetService("HttpService") local RS = game:GetService("RunService") local t = {} '
               'local c = RS.RenderStepped:Connect(function(dt) table.insert(t, dt) end) task.wait(%f) c:Disconnect() '
               'table.sort(t) local s = 0 for _, x in t do s += x end '
               'return H:JSONEncode({ n = #t, sr = #t > 0 and s / #t * 1000 or 0, p95 = #t > 0 and t[math.max(1, math.floor(#t * 0.95))] * 1000 or 0, '
               'maks = #t > 0 and t[#t] * 1000 or 0 })'),
    "kamien": KB + 'local p = k.Punkty:FindFirstChild("KamienPowrotu") return H:JSONEncode(J(p and p.Position or false))',
    "mostek": 'local t = workspace:FindFirstChild("TestWalki2") return tostring(t and t:GetAttribute("SerwerMostekWalk") or 0)',
}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def sprawdz_kod():
    """Bez Studio: każdy szablon z KOD (po podstawieniu zer) parsuje się w luau_mini."""
    import luau_mini as LM
    bledy = []
    for nazwa, szablon in KOD.items():
        # %s → nazwa (bywa też częścią ścieżki: Sygnaly.%s), %d / %f → liczba; „"%s"%s” = polecenie + dodatkowe argumenty
        kod = re.sub(r"%[df]", "0", re.sub(r"%s", "x0", szablon.replace('"%s"%s', '"x0", x0')))
        if "J(" in kod and "local function J" not in kod:
            kod = J + kod
        if "H:" in kod and "local H" not in kod:
            kod = 'local H = game:GetService("HttpService") ' + kod
        try:
            LM.Parser(kod, nazwa, LM.Interpreter()).program()
        except LM.BladSkladni as e:
            bledy.append("%s: %s" % (nazwa, e))
    print("sprawdz: %d kawałków Luau, %s" % (len(KOD), "OK" if not bledy else "BŁĘDY:\n  " + "\n  ".join(bledy)))
    return 0 if not bledy else 1


def ostatni_lup(tekst):
    """OstatniLup stanu gracza = „<gracz>:<zrodlo>:<wynik>:<N>z:<N>xp” → (wynik, złoto, xp) albo None."""
    m = re.search(r":(\w+):(\w+):(\d+)z:(\d+)xp$", tekst or "")
    return (m.group(2), int(m.group(3)), int(m.group(4))) if m else None


def main():
    argv = sys.argv[1:]
    if "--sprawdz" in argv:
        return sprawdz_kod()
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    try:
        w_repo = os.path.commonpath([os.path.normcase(wyj), os.path.normcase(REPO)]) == os.path.normcase(REPO)
    except ValueError:
        w_repo = False
    if w_repo:
        sys.exit("Folder wyników leży w repozytorium (wyniki mogą zawierać nazwę konta) — podaj folder poza repo")
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    bez_zrzutow = "--bez-zrzutow" in argv
    os.makedirs(wyj, exist_ok=True)
    os.makedirs(KLATKI, exist_ok=True)
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

    WYNIKI, LISTA = {}, []

    def zapisz(klucz, wartosc):
        WYNIKI[klucz] = wartosc
        with open(os.path.join(wyj, "wyniki.json"), "w", encoding="utf-8") as f:
            json.dump(WYNIKI, f, ensure_ascii=False, indent=1)

    def punkt(kod, ok, opis):
        LISTA.append((kod, "OK" if ok is True else ("BŁĄD" if ok is False else "?"), opis))
        log("%s %s — %s" % (kod, LISTA[-1][1], opis))
        with open(os.path.join(wyj, "lista.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join("%s %-4s %s" % x for x in LISTA) + "\n")

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
            if "local H" not in kod:
                kod = 'local H = game:GetService("HttpService") ' + kod
            w = json.loads(luau(J + kod, dm))
            return {} if w == [] else w

        def stan_studio():
            return call("get_studio_state")["text"]

        def zrzut(nazwa):
            if bez_zrzutow:
                return
            nie_usypiaj()
            r = call("screen_capture", {"capture_id": "bagno_" + nazwa}, timeout=150)
            if r["is_error"] or not r.get("images"):
                log("zrzut %s: BŁĄD %s" % (nazwa, r["text"][:120]))
                return
            dane = r["images"][0]
            if Image is not None:
                im = Image.open(io.BytesIO(dane)).convert("RGB")
                if im.width > 1280:
                    im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
                im.save(os.path.join(KLATKI, nazwa + ".jpg"), "JPEG", quality=85)
            log("zrzut", nazwa)

        def lista(nazwy):
            return ", ".join('"%s"' % n for n in nazwy)

        def kont(nazwa, atrybuty, dm="Server"):
            return js(KOD["kont_atr"] % (nazwa, lista(atrybuty)), dm)

        def gracz(atrybuty):
            return js(KOD["gracz_atr"] % lista(atrybuty), "Server")

        def ustaw(kontener, atrybut, wartosc, dm="Server"):
            luau(KOD["ustaw_atr"] % (kontener, atrybut, wartosc), dm)

        def hak(kontener, sygnal, polecenie, *argi, dm="Server"):
            a = "".join(", " + ("nil" if x is None else json.dumps(x)) for x in argi)
            return js(KOD["hak"] % (kontener, sygnal, polecenie, a), dm)

        def bagno(polecenie, *argi):
            return hak("BagnoPasGra", "SterowaniePasa", polecenie, *argi)

        def las(polecenie, *argi):
            return hak("LasPasGra", "SterowaniePasa", polecenie, *argi)

        def teleport(polecenie, arg="nil"):
            return js(KOD["teleport"] % (polecenie, arg), "Server")

        def poz():
            return js(KOD["poz"], "Server")

        def przestaw(x, y, z, kier=1.0):
            luau(KOD["przestaw"] % (x, y, z, kier), "Server")

        def nacisnij(klawisz):
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": klawisz}]})

        def czekaj_na(warunek, limit, co=0.5):
            t0 = time.time()
            while time.time() - t0 < limit:
                w = warunek()
                if w:
                    return w
                time.sleep(co)
            return None

        def klient_potworow():
            return js(KOD["klient_potworow"], "Client")

        def odtw(polecenie):
            return js(KOD["odtw"] % polecenie, "Client")

        def walka_trwa():
            return klient_potworow().get("walka")

        def dokoncz_walke():
            czekaj_na(lambda: odtw('"stan"').get("faza") == "odtwarzanie", 10, 0.4)
            odtw('"przewinDo", 1000')
            time.sleep(2.5)
            odtw('"zamknij"')
            czekaj_na(lambda: not walka_trwa(), 30, 1.0)
            time.sleep(1.0)
            luau(KOD["kamera_zwykla"], "Client")

        def ostatnia_walka():
            return kont("BagnoPasGra", ["SerwerOstatniaWalka", "SerwerLicznikWalk"])

        def zacznij_walke(strefa):
            """Staje przy pierwszym wolnym potworze strefy, wciska prawdziwe E (zapas: haczyk „walcz”). → opis albo None.
            Strażnik po przegranej jest zajęty do końca walki (ok. 30–40 s) — czekamy na niego dłużej."""
            for _ in range(25 if strefa == "straznik" else 3):
                cel = js(KOD["potwor_w_strefie"] % strefa, "Server")
                if not cel.get("id"):
                    time.sleep(3)
                    continue
                jak = None
                for _ in range(6):
                    p = js(KOD["pozycja_potwora"] % cel["id"], "Server")
                    if not p:
                        break
                    przestaw(p[0] - 5, p[1] + 3.2, p[2], 1.0)
                    luau(KOD["kamera_za"], "Client")
                    time.sleep(0.6)
                    pp = js(KOD["podpowiedz"], "Client")
                    if pp.get("podpowiedz") and pp.get("najblizszy") == cel["id"]:
                        nacisnij("E")
                        jak = "E"
                        break
                if not czekaj_na(walka_trwa, 5, 0.4):
                    luau(KOD["walcz"] % cel["id"], "Client")
                    jak = "haczyk walcz (E nie zadziałało)"
                if czekaj_na(walka_trwa, 8, 0.4):
                    cel["jak"] = jak
                    return cel
                luau(KOD["kamera_zwykla"], "Client")
            return None

        def walka(strefa, zrzut_nazwa=None):
            przed = ostatnia_walka()
            cel = zacznij_walke(strefa)
            if not cel:
                return {"blad": "walka nie ruszyła", "strefa": strefa}
            time.sleep(2.5)
            stan_odtw = odtw('"stan"')
            if zrzut_nazwa:
                zrzut(zrzut_nazwa)
            dokoncz_walke()
            time.sleep(1.5)
            p = poz()
            kp = klient_potworow()
            kpa = hak("BagnoPasGra", "SterowaniePasaKlienta", "stan", dm="Client")
            po = kont("BagnoPasGra", ["SerwerOstatniaWalka", "SerwerLicznikWalk", "SerwerOstatnieZiarno"])
            return {"cel": cel, "przed": przed, "po": po, "odtw": {x: stan_odtw.get(x) for x in
                    ("faza", "pomijanie", "pomijanieNaEkranie", "powodPominiecia")}, "pozycja": p,
                    "kamera": kpa.get("kamera"), "walka_po": kp.get("walka")}

        # ================================================================ B00 Edit
        nie_usypiaj()
        if "Current Studio Mode: Edit" not in stan_studio():
            sys.exit("Studio nie jest w trybie Edit — ta próba sama włącza Play")
        edit = json.loads(luau(KOD["edit"] % lista(AKTORZY), "Edit"))
        zapisz("B00", edit)
        ok00 = (edit["mapa"] and edit["gra"] and edit["las"] and edit["pas"] and edit["teleport"]
                and all(edit["aktorzy"].values()) and not edit["zapowiedz"])
        punkt("B00", ok00, "w Edit: %s" % edit)
        if not (edit["mapa"] and edit["gra"]):
            sys.exit(2)
        stan_gracza = edit["stan"]

        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        imie = None
        try:
            czekaj_na(lambda: "Client" in stan_studio() and luau(KOD["gotowy_klient"], "Client") == "true", 90, 1.0)
            imie = luau(KOD["imie"], "Server")
            luau(KOD["bez_nazwy"], "Client")
            # tryb testowy bohatera (panel T1) w obu biomach, walki przewijane bez blokady sesji
            for n in ("BagnoPasGra", "LasPasGra"):
                ustaw(n, "TestBohater", "true")
            ustaw("BagnoPasGra", "TestBezSesji", "true")
            time.sleep(3)

            # ================================================================ B01 gotowość
            g = czekaj_na(lambda: (lambda a: a if a.get("SerwerGotowy") and a.get("SerwerPasaGotowy") else None)(
                kont("BagnoPasGra", ["SerwerGotowy", "SerwerPasaGotowy", "StanMapy", "StanBiomu", "SzablonyGotowe",
                                     "Potworow", "ZgodnoscLogiki", "ZgodnoscLogikiPasa", "Przekierowanie",
                                     "PunktPrzybyciaBagna", "LicznikPrzelotow"])), 60, 1.0) or {}
            lasp = js(KOD["las_poza"], "Server")
            kl = czekaj_na(lambda: (lambda a: a if a.get("KlientGotowy") and a.get("KlientPasaGotowy") else None)(
                kont("BagnoPasGra", ["KlientGotowy", "KlientTryb", "KlientPasaGotowy"], "Client")), 60, 1.0) or {}
            zapisz("B01", {"bagno": g, "las": lasp, "klient": kl})
            punkt("B01", g.get("StanMapy") == "ok" and g.get("StanBiomu") == "ok" and g.get("SzablonyGotowe") is True
                  and g.get("Potworow") == G["potworow_1"] and g.get("ZgodnoscLogiki") == "OK 70/70" and g.get("ZgodnoscLogikiPasa") == "OK 39/39"
                  and g.get("Przekierowanie") == "nie_ten_biom" and lasp.get("nastepny") is True and lasp.get("zaBrama") is False
                  and kl.get("KlientTryb") == "aktorzy" and kl.get("KlientPasaGotowy") is True,
                  "Bagno %s | las %s | klient %s" % (g, lasp, kl))
            wybor = {}
            for _ in range(20):
                wybor = js(KOD["wybor_klasy"], "Client")
                if not wybor["ekran"] and wybor["kamera"] == "Custom" and wybor["podpowiedzi"]:
                    break
                nacisnij("Return")
                time.sleep(1.5)
            zapisz("wybor_klasy", wybor)

            # ================================================================ B02 bez bramy lasu
            las("zamknijBrame")
            las("zapomnijPrzelot")          # przelot lasu nie przeszkadza (sprawdza go próba lasu)
            PP.oznacz(luau, ["las"])     # to samo dla nowej cutscenki wcześniejszych biomów
            nowa = PP.dopasuj(luau, "bagno", G)      # nowa cutscenka (CutscenkaBiomu) albo stary przelot pasa
            log("przelot biomu gra: %s" % ("nowa cutscenka (CutscenkaBiomu)" if nowa else "stary przelot pasa"))
            time.sleep(0.5)
            u = js(KOD["uchwyt_bagna"], "Server")
            t = teleport("stan", "gracz")
            las("przenies", None, "przed_brama")    # uchwyt lasu prosi o wczytanie okolicy (streaming)
            time.sleep(2.0)
            cof0 = kont("BagnoPasGra", ["LicznikCofniec"]).get("LicznikCofniec") or 0
            przestaw(G["strefy"]["t1"], 3.2, -700)       # dalej niż brama lasu + jej głębokość pilnowania (od X)
            time.sleep(2.0)
            p02 = poz()
            kom02 = js(KOD["komunikat"], "Client")
            cof1 = kont("BagnoPasGra", ["LicznikCofniec"]).get("LicznikCofniec") or 0
            zapisz("B02", {"uchwyt": u, "teleport": t, "pozycja": p02, "komunikat": kom02, "cofniecia": [cof0, cof1]})
            punkt("B02", u.get("ok") is False and u.get("powod") == "zamkniete" and "bagno" not in (t.get("odblokowane") or [])
                  and p02[0] < G["brama_lasu"] and cof1 > cof0 and "Strażnika Gaju" in str(kom02.get("tekst")),
                  "uchwyt %s, teleport %s, cofnięty do X %.1f (cofnięć %s→%s), komunikat %r" % (
                      u, t.get("odblokowane"), p02[0], cof0, cof1, kom02.get("tekst")))

            # ================================================================ B03 brama lasu → pierwszy przelot Bagna
            las("otworzBrame")
            las("przenies", None, "przed_brama")
            time.sleep(2.0)
            przel_las = kont("LasPasGra", ["LicznikPrzelotow"]).get("LicznikPrzelotow") or 0
            call("character_navigation", {"datamodel_type": "Client", "x": G["przybycie"] + 6, "y": 3, "z": -700})
            fazy, t_trwa, plan = [], None, [(tp(1.0), "01_przelot_oczka"), (tp(4.0), "02_przelot_trzesawisko"),
                                            (tp(7.0), "03_przelot_kepy"), (tp(10.4), "04_przelot_straznik"),
                                            (tp(11.6), "05_przelot_ryk")]
            t0 = time.time()
            while time.time() - t0 < 45:
                gs = PP.scal_gracza(luau, "bagno", bagno("gracz"))
                if not fazy or fazy[-1][0] != gs.get("faza"):
                    fazy.append((gs.get("faza"), round(time.time() - t0, 1)))
                if gs.get("faza") == "trwa" and t_trwa is None:
                    t_trwa = time.time()
                if plan and PP.pora_na_zrzut(luau, "bagno", plan, t_trwa, time.time()):
                    zrzut(plan.pop(0)[1])
                    continue
                if gs.get("faza") == "brak" and len(fazy) > 1:
                    break
                time.sleep(0.3)
            czas_lotu = (time.time() - t_trwa) if t_trwa else None
            time.sleep(1.5)
            zrzut("06_po_przelocie_pomost")
            gs = PP.scal_gracza(luau, "bagno", bagno("gracz"))
            kp = PP.scal_klienta(luau, "bagno", hak("BagnoPasGra", "SterowaniePasaKlienta", "stan", dm="Client"))
            ost = kp.get("ostatniPrzelot") or {}
            przel_las2 = kont("LasPasGra", ["LicznikPrzelotow"]).get("LicznikPrzelotow") or 0
            zapisz("B03", {"fazy": fazy, "czas": czas_lotu, "gracz": gs, "klient": kp, "przeloty_lasu": [przel_las, przel_las2]})
            nazwy = [f[0] for f in fazy]
            # character_navigation czeka do końca marszu, więc obserwacja faz zaczyna się w trakcie lotu — czas lotu
            # bierzemy z pomiaru klienta (ostatniPrzelot.czas: start lotu → koniec zaciemnienia)
            czas_lotu = ost.get("czas") or czas_lotu
            punkt("B03", "trwa" in nazwy and nazwy[-1] == "brak" and czas_lotu is not None and abs(czas_lotu - (G["przelot"] + 0.5)) < 1.5
                  and ost.get("ok") is True and ost.get("ryk") is True and kp.get("kamera") == "Custom"
                  and (gs.get("pamiec") or {}).get("widzialPrzelotBagna") is True and przel_las2 == przel_las,
                  "fazy %s, lot %.1f s, ryk %s, kamera %s, przeloty lasu %s→%s" % (
                      nazwy, czas_lotu or -1, ost.get("ryk"), kp.get("kamera"), przel_las, przel_las2))

            # ================================================================ B04 chmury → Bagno, bez drugiego przelotu
            t = teleport("stan", "gracz")
            przel0 = PP.licznik(luau, "bagno", kont("BagnoPasGra", ["LicznikPrzelotow"]).get("LicznikPrzelotow") or 0)
            # start bazaru (26.11.2026: starego miasteczka z Workspace/LasTeleport już nie ma)
            luau(HRP + 'local b = workspace:FindFirstChild("MiasteczkoBazarGra") local p = b and b:GetAttribute("PunktStartuBazaru") '
                       'if p then hrp.Parent:PivotTo(CFrame.new(p)) end return "ok"', "Server")
            time.sleep(2.5)
            w04 = teleport("przenies", '"bagno", gracz')
            time.sleep(6.0)
            p04 = poz()
            gs = PP.scal_gracza(luau, "bagno", bagno("gracz"))
            przel1 = PP.licznik(luau, "bagno", kont("BagnoPasGra", ["LicznikPrzelotow"]).get("LicznikPrzelotow") or 0)
            zapisz("B04", {"teleport": t, "przenies": w04, "pozycja": p04, "faza": gs.get("faza"), "przeloty": [przel0, przel1]})
            punkt("B04", "bagno" in (t.get("odblokowane") or []) and w04.get("ok") is True
                  and "PrzeniesDoBagna" in str(w04.get("zrodlo")) and abs(p04[0] - G["przybycie"]) < 4 and abs(p04[2] + 700) < 4
                  and gs.get("faza") == "brak" and przel1 == przel0,
                  "teleport otwarte %s, przeniesienie %s → (%.1f; %.1f), faza %s, przeloty %s→%s" % (
                      t.get("odblokowane"), w04.get("zrodlo"), p04[0], p04[2], gs.get("faza"), przel0, przel1))

            # ================================================================ B04b TELEPORT do krainy, w której gracz jest
            # D-096 (Karol: „Kliknąć Las jeszcze raz?”): z głębi Bagna wybór „Bagno” stawia przy przybyciu (inkubator,
            # Kamień Powrotu) — bez odmowy i bez drugiego przelotu (przelot tylko, gdy gracz go nie widział)
            przestaw(G["strefy"]["k1"], 3.2, -700)
            time.sleep(3.5)                                  # odstęp przeniesień teleportu (3 s) i pasa (2 s)
            z04b = poz()
            przel0 = PP.licznik(luau, "bagno", kont("BagnoPasGra", ["LicznikPrzelotow"]).get("LicznikPrzelotow") or 0)
            w04b = teleport("przenies", '"bagno", gracz')
            time.sleep(6.0)
            p04b = poz()
            gs = PP.scal_gracza(luau, "bagno", bagno("gracz"))
            przel1 = PP.licznik(luau, "bagno", kont("BagnoPasGra", ["LicznikPrzelotow"]).get("LicznikPrzelotow") or 0)
            zapisz("B04b", {"z": z04b, "przenies": w04b, "pozycja": p04b, "faza": gs.get("faza"), "przeloty": [przel0, przel1]})
            punkt("B04b", w04b.get("ok") is True and abs(p04b[0] - G["przybycie"]) < 4 and abs(p04b[2] + 700) < 4
                  and gs.get("faza") == "brak" and przel1 == przel0,
                  "z X %.0f wybór Bagna → %s (%.1f; %.1f), faza %s, przeloty %s→%s" % (
                      z04b[0], w04b.get("zrodlo") or w04b.get("powod"), p04b[0], p04b[2], gs.get("faza"), przel0, przel1))

            # ================================================================ B05 potwory w przegrodach
            probki, poza, przyklad = 0, 0, None
            for _ in range(30):
                w = js(KOD["w_polach"], "Server")
                probki += w.get("n", 0)
                poza += w.get("poza", 0)
                przyklad = przyklad or w.get("przyklad")
                time.sleep(1.0)
            zapisz("B05", {"probki": probki, "poza": poza, "przyklad": przyklad})
            punkt("B05", probki >= 25 * G["potworow_1"] and poza == 0, "%d próbek pozycji, poza polem strefy: %d (%s)" % (probki, poza, przyklad))

            # ================================================================ B06 walka z każdym gatunkiem (tryb testowy)
            luau(KOD["bohater_t1"] % ("wojownik", "auto"), "Client")
            most0 = int(float(luau(KOD["mostek"], "Server")))
            walki = {}
            for strefa, gat in GATUNKI.items():
                walki[strefa] = walka(strefa, "07_walka_" + gat)
            most1 = int(float(luau(KOD["mostek"], "Server")))
            zapisz("B06", {"walki": walki, "mostek": [most0, most1]})
            dobre = []
            for strefa, gat in GATUNKI.items():
                w = walki[strefa]
                if "blad" in w:
                    continue
                ow = str(w["po"].get("SerwerOstatniaWalka") or "")
                if (w["cel"].get("gatunek") == gat and ow.startswith(w["cel"]["id"] + "/") and "/auto→" in ow
                        and w["pozycja"][0] > G["brama_lasu"] and w["kamera"] == "Custom" and not w["walka_po"]):
                    dobre.append(gat)
            punkt("B06", len(dobre) == 4 and most1 - most0 >= 4, "walki z gatunkami %s; mostek pomijania %s→%s" % (
                dobre, most0, most1))

            # ================================================================ B07 POMIŃ przy znanym gatunku (Rechotek)
            ustaw("BagnoPasGra", "TestBezSesji", "nil")
            time.sleep(1.0)
            p07 = {}
            cel = zacznij_walke("r1")                # krótki pas: jedna strefa Rechotków (r1)
            if cel:
                zgoda = czekaj_na(lambda: odtw('"stan"').get("pomijanie"), 8, 0.5)
                so = odtw('"stan"')
                p07["przed"] = {"pomijanie": so.get("pomijanie"), "przycisk": so.get("pomijanieNaEkranie"),
                                "powod": so.get("powodPominiecia"), "zgoda": bool(zgoda)}
                zrzut("08_druga_walka_pomin")
                nacisnij("Space")
                czekaj_na(lambda: odtw('"stan"').get("faza") in ("wynik", "brak", "koniec"), 8, 0.4)
                time.sleep(1.2)
                p07["po"] = kont("BagnoPasGra", ["OstatniaOdpowiedzPominiecia", "OstatnioPominieto"], "Client")
                odtw('"zamknij"')
                czekaj_na(lambda: not walka_trwa(), 20, 0.5)
                luau(KOD["kamera_zwykla"], "Client")
            ustaw("BagnoPasGra", "TestBezSesji", "true")
            zapisz("B07", p07)
            punkt("B07", bool(cel) and (p07.get("przed") or {}).get("przycisk") is True
                  and (p07.get("po") or {}).get("OstatniaOdpowiedzPominiecia") == "ok",
                  "druga walka z Rechotkiem: %s" % p07)

            # ================================================================ B08 zwykły tryb: poziom i łup z danych gracza
            if stan_gracza:
                ustaw("BagnoPasGra", "TestBohater", "nil")
                luau(KOD["gracz_ustaw"] % ("Level", "11"), "Server")
                time.sleep(1.5)
                a0 = gracz(["Class", "Level", "XP", "Gold", "TokenyKrainy_bagno"])
                l0 = kont("StanGracza", ["LicznikLupow", "OstatniLup", "OstatniBohater"])
                w08 = walka("r1", "09_walka_z_danych_gracza")
                a1 = gracz(["Class", "Level", "XP", "Gold", "TokenyKrainy_bagno"])
                l1 = kont("StanGracza", ["LicznikLupow", "OstatniLup", "OstatniBohater"])
                ow = str((w08.get("po") or {}).get("SerwerOstatniaWalka") or "")
                m = re.search(r"/(\w+)/(\w+)→(\d+)/(\w+)$", ow)
                lup = ostatni_lup(l1.get("OstatniLup"))
                zapisz("B08", {"przed": a0, "po": a1, "lupy": [l0, l1], "walka": ow})
                ok08 = bool(m) and int(m.group(3)) == 11 and (l1.get("LicznikLupow") or 0) > (l0.get("LicznikLupow") or 0) and bool(lup)
                if ok08 and lup[0] == "wygrana":
                    ok08 = (a1.get("Gold") or 0) == (a0.get("Gold") or 0) + lup[1]
                punkt("B08", ok08, "walka %s, łup %s, Gold %s→%s, XP %s→%s, Level %s→%s, żetony Bagna %s→%s" % (
                    ow, lup, a0.get("Gold"), a1.get("Gold"), a0.get("XP"), a1.get("XP"), a0.get("Level"), a1.get("Level"),
                    a0.get("TokenyKrainy_bagno"), a1.get("TokenyKrainy_bagno")))
                ustaw("BagnoPasGra", "TestBohater", "true")
            else:
                punkt("B08", None, "brak Workspace/StanGracza — pominięte")

            # ================================================================ B09 brama do Dżungli zamknięta
            cof0 = kont("BagnoPasGra", ["LicznikCofniec"]).get("LicznikCofniec") or 0
            przestaw(G["brama"] + 16, 3.2, -700)
            time.sleep(2.0)
            p09 = poz()
            kom09 = js(KOD["komunikat"], "Client")
            wr09 = js(KOD["wrota"], "Client")
            cof1 = kont("BagnoPasGra", ["LicznikCofniec"]).get("LicznikCofniec") or 0
            zapisz("B09", {"pozycja": p09, "komunikat": kom09, "wrota": wr09, "cofniecia": [cof0, cof1]})
            punkt("B09", p09[0] < G["brama"] and cof1 > cof0 and "Dżungli" in str(kom09.get("tekst")) and wr09.get("kolizja", 0) > 0,
                  "cofnięty do X %.1f (brama %.0f), cofnięć %s→%s, komunikat %r, wrota %s" % (
                      p09[0], G["brama"], cof0, cof1, kom09.get("tekst"), wr09))

            # ================================================================ B10 Strażnik Topieli: przegrana i wygrana
            luau(KOD["sledz_banery"], "Client")
            luau(KOD["bohater_t1"] % ("wojownik", "10"), "Client")
            w_prz = walka("straznik", "10_straznik_przegrana")
            otw_po_prz = gracz(["PokonalStraznikaBagna"]).get("PokonalStraznikaBagna")
            luau(KOD["bohater_t1"] % ("zwiadowca", "20"), "Client")
            proby, wygrana = [], False
            for ziarno in (11, 23, 37, 41):
                ustaw("BagnoPasGra", "ZiarnoTestowe", str(ziarno))
                w = walka("straznik", "11_straznik_walka" if not proby else None)
                proby.append((ziarno, (w.get("po") or {}).get("SerwerOstatniaWalka")))
                wygrana = gracz(["PokonalStraznikaBagna"]).get("PokonalStraznikaBagna") is True
                if wygrana:
                    break
            ustaw("BagnoPasGra", "ZiarnoTestowe", "nil")
            time.sleep(2.0)
            banery = kont("BagnoPasGra", ["ProbaBanery"], "Client").get("ProbaBanery") or ""
            wr_k = js(KOD["wrota"], "Client")
            wr_s = js(KOD["wrota"], "Server")
            cof0 = kont("BagnoPasGra", ["LicznikCofniec"]).get("LicznikCofniec") or 0
            bagno("przenies", None, "przed_brama")
            time.sleep(1.5)
            zrzut("12_brama_dzungli_otwarta")
            call("character_navigation", {"datamodel_type": "Client", "x": G["brama"] + 14, "y": 3, "z": -700})
            time.sleep(6)
            p10 = poz()
            cof1 = kont("BagnoPasGra", ["LicznikCofniec"]).get("LicznikCofniec") or 0
            zrzut("13_za_brama_dzungla_wkrotce")
            lista_banerow = [b for b in banery.split("|") if b]
            zapisz("B10", {"przegrana": w_prz, "otwarta_po_przegranej": otw_po_prz, "proby": proby, "banery": lista_banerow,
                           "wrota_klient": wr_k, "wrota_serwer": wr_s, "za_brama": p10, "cofniecia": [cof0, cof1]})
            punkt("B10", otw_po_prz is not True and wygrana and wr_k.get("kolizja") == 0 and wr_k.get("zapora") is False
                  and wr_s.get("kolizja", 0) > 0 and wr_s.get("zapora") is True and p10[0] > G["brama"] + 2 and cof1 == cof0
                  and len(lista_banerow) == 1 and "STRAŻNIK TOPIELI POKONANY!" in lista_banerow[0]
                  and "Dżungli" in lista_banerow[0],
                  "przegrana: brama %s; próby %s; banery %s; wrota klient %s / serwer %s; za bramą X %.1f (cofnięć %s→%s)" % (
                      "zamknięta" if otw_po_prz is not True else "OTWARTA", proby, lista_banerow, wr_k, wr_s, p10[0], cof0, cof1))

            # ================================================================ B11 Kamień Powrotu
            kam = js(KOD["kamien"], "Server")
            p11 = None
            if kam:
                for _ in range(3):
                    przestaw(kam[0] + 4, kam[1] + 1, kam[2] + 3, -1.0)
                    time.sleep(1.0)
                    nacisnij("E")
                    p11 = czekaj_na(lambda: (lambda p: p if p[0] < 1100 else None)(poz()), 5, 0.5)
                    if p11:
                        break
            zapisz("B11", {"kamien": kam, "pozycja": p11})
            punkt("B11", p11 is not None, "Kamień Powrotu %s → %s" % (kam, p11))

            # ================================================================ B12 mgła
            bagno("przenies", None, "las")
            time.sleep(2.0)
            przestaw(G["strefy"]["b1"], 3.2, -700)
            time.sleep(4.0)
            m_bagno = js(KOD["atmosfera"], "Client")
            zrzut("14_mgla_bagna")
            las("przenies", None, "las")
            time.sleep(2.0)
            przestaw(G["las_srodek"], 3.2, -700)
            time.sleep(4.0)
            m_las = js(KOD["atmosfera"], "Client")
            m_serwer = js(KOD["atmosfera"], "Server")
            zapisz("B12", {"bagno": m_bagno, "las": m_las, "serwer": m_serwer, "edit": edit["gestosc"]})
            punkt("B12", m_bagno.get("bagno") == 1 and m_bagno.get("las") == 0 and abs(m_bagno.get("gestosc", 0) - 0.42) < 0.02
                  and m_las.get("las") == 1 and m_las.get("bagno") == 0 and abs(m_serwer.get("gestosc", -9) - edit["gestosc"]) < 1e-6,
                  "w Bagnie %s, w lesie %s, serwer %s (Edit %s)" % (m_bagno, m_las, m_serwer.get("gestosc"), edit["gestosc"]))

            # ================================================================ B13 koszt przy oknie na wierzchu
            okno = os.path.join(REPO, "tools", "studio_okno.py")
            if os.path.isfile(okno):
                subprocess.run([sys.executable, "-B", okno, "--na-wierzch"], cwd=REPO, capture_output=True, timeout=60)
            bagno("przenies", None, "las")
            time.sleep(2.0)
            przestaw(G["strefy"]["k1"], 3.2, -700)
            time.sleep(8.0)
            kl13 = json.loads(luau(KOD["klatka"] % 4.0, "Client"))
            kp13 = klient_potworow()
            zapisz("B13", {"klatka": kl13, "klient_potworow": {x: kp13.get(x) for x in ("widoki", "animowane", "czesciWidokow", "tryb")}})
            punkt("B13", None, "Kępy: klatka śr. %.1f ms, p95 %.1f, maks. %.1f (%d klatek); widoki %s, bryły widoków %s" % (
                kl13.get("sr", 0), kl13.get("p95", 0), kl13.get("maks", 0), kl13.get("n", 0), kp13.get("widoki"),
                kp13.get("czesciWidokow")))

            # D-107 (walka bez przestojów): BD1 liczba potworów (1 i 20 graczy), BD2 odradzanie w zadanym czasie,
            # BD3 czas klatki przy pełnym zestawie, BD4 przegrana ze strażnikiem przy ×4 bez blokady i rewanż od razu, D5 czas pominiętej walki
            D107.punkty("B", "BagnoPasGra", G["d107"], luau, punkt, zapisz, przestaw, nacisnij, czekaj_na, klient_potworow, odtw)

            # ================================================================ B14 konsola
            kons = call("get_console_output", {}, timeout=60)["text"]
            linie = [x.strip()[:240] for x in kons.splitlines() if any(n in x for n in NASZE)]
            bledy = [x for x in linie if "rror" in x or "błąd" in x.lower() or "Stack" in x]
            zapisz("B14", linie[-80:])
            punkt("B14", not bledy, "%d wierszy Bagna, błędów: %d %s" % (len(linie), len(bledy), bledy[:3]))
        finally:
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
            for _ in range(60):
                time.sleep(0.5)
                if "Current Studio Mode: Edit" in stan_studio():
                    break
            if imie:
                WYNIKI["_konto"] = imie  # tylko w folderze wyników poza repo
                zapisz("_koniec", time.strftime("%Y-%m-%d %H:%M:%S"))
            print("\nLISTA KONTROLNA:")
            for x in LISTA:
                print("  %s %-4s %s" % x)
            print("\nwyniki: %s | zrzuty: %s" % (wyj, os.path.relpath(KLATKI, REPO)))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
