#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba „bohatera w świecie” w Roblox Studio (tryb Play) — część B. Nie zmienia miejsca: sama włącza i wyłącza Play
(SesjaPlay z swiat/test_walki2/testy/sesja_play.py zatrzymuje go zawsze), niczego nie zapisuje i nie publikuje.

    python -B swiat/bohater_swiat/testy/proba_play.py --sprawdz                       # bez Studio: parsuje kawałki Luau
    python -B tools/studio_okno.py --na-wierzch                                       # przed próbą (okno w tle rysuje wolno)
    python -B swiat/bohater_swiat/testy/proba_play.py <folder wyników POZA repo>      # zrzuty → swiat/bohater_swiat/klatki/
    python -B swiat/bohater_swiat/testy/proba_play.py <folder> --bez-zrzutow [--tylko B05,B06] [--studio <id>]

Warunki (tryb Edit): Workspace/BohaterSwiat (zbuduj.py), Workspace/TestWalki2 i Workspace/StrojeProba (klipy i strój).
Reszta jest sprawdzana, gdy stoi w miejscu (inaczej punkt dostaje „?”): KowalProba, PetyProba + StanGracza, LasPasGra,
TeleportChmury, TreningProba. Wyniki (wyniki.json, lista.txt, konsola.txt) idą do podanego folderu — mogą zawierać
nazwę konta, dlatego folder nie może leżeć w repozytorium. Zrzuty mają schowaną listę graczy i czat.

LISTA KONTROLNA (OK / BŁĄD / ?):
  B00 w Edit: kontener (Wygenerowane, 0 części, skrót = lokalny, wyłącznik), zależności na miejscu
  B01 przed wyborem klasy: klient i serwer gotowi, bohatera nie ma, awatar widoczny, RuchBohatera "stan" → nil
  B02 wybór klasy (Enter jak gracz) → bohater klasy gracza w jego stroju, bryły = dane, awatar niewidoczny
  B03 bohater poza fizyką (kolizje, dotyk, zapytania, masa), korzeń zakotwiczony; masa, HipHeight, WalkSpeed
      i skok postaci takie same jak przy wyłączonym bohaterze
  B04 stopy na ziemi, bohater pod postacią, przodem jak postać; zrzut zza pleców (kamera gracza)
  B05 ruch po ziemi: prawdziwy klawisz W — z miejsca do biegu i z powrotem do spoczynku, stopy przy ziemi; droga z W
      taka sama z bohaterem i bez; zrzut w ruchu
  B06 skok (spacja): skok → spadanie → lądowanie → spoczynek; zrzut w powietrzu
  B07 wyłącznik BohaterWSwiecie = false → bohater znika od razu, awatar wraca; true → bohater wraca
  B08 trzy klasy: zmiana klasy → bohater przebudowany (klasa, bryły); zrzut każdej
  B09 strój z przymierzalni (goły, mieszany, komplet) → bohater w świecie w tym stroju, stopy na ziemi; zrzut
  B10 kowal: nowy przedmiot z łupu zakłada się sam → bohater w świecie go nosi
  B11 reset postaci: upadek, po odrodzeniu bohater wraca, awatar schowany
  B12 umowa RuchBohatera: stan, pięć klipów, zły klip, powrót, przesunięcie; zrzuty póz
  B13 pet idzie za graczem-bohaterem; zrzut obok peta
  B14 walka w lesie-pasie: w walce bohater świata schowany, aktor walki w tym samym stroju, po walce bohater wraca;
      zrzut w lesie
  B15 teleport przez chmury: po przejściu bohater przy postaci, stopy na ziemi
  B16 runda Training Center: bez błędów, po rundzie bohater w ruchu samoczynnym
  B17 wielu bohaterów (postacie testowe): limit i zasięg, liczba brył, czas klatki; zrzut
  B18 konsola bez wierszy [BohaterSwiat]
  B19 cykl biegu: stopa w podporze stoi w miejscu — w zatrzymanych fazach (z przesunięciem o drogę postaci) i w
      prawdziwym biegu klatka po klatce; arkusz ośmiu kolejnych klatek biegu każdej klasy
  B20 bieg w przeszkodę (ściana próby przed postacią, klawisz W trzymany): stopa w podporze nie jedzie po ziemi,
      bohater przechodzi do spoczynku, choć klawisz jest wciśnięty; zakręt (W + strzałka): tułów się przechyla
"""
import json
import math
import os
import re
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
if not sys.path or sys.path[0] != PAKIET:
    sys.path.insert(0, PAKIET)
import dane as DN  # noqa: E402
import logika_bohatera as L  # noqa: E402

for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "tools", "walka"),
           os.path.join(REPO, "swiat", "test_walki_roblox"), os.path.join(REPO, "swiat", "test_walki2", "testy")):
    if _s not in sys.path:
        sys.path.append(_s)

KLATKI = os.path.join(PAKIET, "klatki")
PUNKTY = ["B%02d" % i for i in range(21)]
# stroje „mieszane” do prób (część przedmiotów: widać gołe ciało obok przedmiotów) — te same co w próbie przymierzalni
MIESZANE = {"wojownik": ["rycerz_helm", "rycerz_buty", "rycerz_miecz", "rycerz_tarcza"],
            "zwiadowca": ["zwiadowca_kaptur", "zwiadowca_rekawice", "zwiadowca_luk"],
            "mag": ["kot_mag_kapelusz", "kot_mag_kostur"]}

J = ('local H = game:GetService("HttpService") local function J(v) local t = typeof(v) if t == "Vector3" then return { v.X, v.Y, v.Z } '
     'elseif t == "table" then local o = {} if #v > 0 then for i, b in ipairs(v) do o[i] = J(b) end '
     'else for a, b in v do o[tostring(a)] = J(b) end end return o '
     'elseif t == "number" and (v ~= v or v == math.huge or v == -math.huge) then return tostring(v) '
     'elseif t == "Instance" then return v.ClassName end return v end ')
GR = 'local gracz = game:GetService("Players"):GetPlayers()[1] '
LP = ('local lp = game:GetService("Players").LocalPlayer local postac = lp.Character '
      'local hum = postac and postac:FindFirstChildOfClass("Humanoid") local hrp = postac and postac:FindFirstChild("HumanoidRootPart") ')
KB = 'local k = workspace:FindFirstChild("BohaterSwiat") '

# Kawałki Luau (szablony %s / %d / %f) — --sprawdz parsuje każdy po podstawieniu zer (tools/walka/luau_mini.py).
KOD = {
    "edit": ('local function jest(n) local o = workspace:FindFirstChild(n) return o ~= nil and o:GetAttribute("Wygenerowane") == true end '
             + KB + 'local czesci, skrypty = 0, 0 if k then for _, d in k:GetDescendants() do if d:IsA("BasePart") then czesci += 1 end '
             'if d:IsA("LuaSourceContainer") then skrypty += 1 end end end '
             'return H:JSONEncode({ bohater = jest("BohaterSwiat"), walka = jest("TestWalki2"), stroje = jest("StrojeProba"), '
             'kowal = jest("KowalProba"), pety = jest("PetyProba"), stan = jest("StanGracza"), pas = jest("LasPasGra"), '
             'chmury = jest("TeleportChmury"), trening = jest("TreningProba"), czesci = czesci, skrypty = skrypty, '
             'skrot = k and k:GetAttribute("Skrot") or false, wlacznik = k and k:GetAttribute("BohaterWSwiecie"), '
             'sygnal = k ~= nil and k:FindFirstChild("Sygnaly") ~= nil and k.Sygnaly:FindFirstChild("RuchBohatera") ~= nil })'),
    "gotowosc": KB + ('return H:JSONEncode({ klient = k and k:GetAttribute("KlientGotowy") or false, '
                      'serwer = k and k:GetAttribute("SerwerGotowy") or false, skrotK = k and k:GetAttribute("SkrotKlienta") or false, '
                      'skrotS = k and k:GetAttribute("SkrotSerwera") or false })'),
    "klient": 'return H:JSONEncode(J(workspace.BohaterSwiat.Sygnaly.SterowanieKlienta:Invoke(%s)))',
    "serwer": 'return H:JSONEncode(J(workspace.BohaterSwiat.Sygnaly.SterowanieSerwera:Invoke(%s)))',
    "ruch": 'return H:JSONEncode(J({ w = workspace.BohaterSwiat.Sygnaly.RuchBohatera:Invoke(%s) }))',
    "bez_nazwy": ('local SG = game:GetService("StarterGui") for _, t in { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Chat } do '
                  'pcall(function() SG:SetCoreGuiEnabled(t, false) end) end return "ok"'),
    "awatar": LP + ('local w, u = 0, 0 if postac then for _, d in postac:GetDescendants() do if d:IsA("BasePart") or d:IsA("Decal") then '
                    'if d.Transparency >= 1 then u += 1 else w += 1 end end end end '
                    'local glowa = postac and postac:FindFirstChild("Head") '
                    'return H:JSONEncode({ widoczne = w, ukryte = u, ltmGlowy = glowa and glowa.LocalTransparencyModifier or 0 })'),
    "postac": LP + ('if not (hum and hrp) then return H:JSONEncode({ brak = true }) end '
                    'return H:JSONEncode(J({ masa = hrp.AssemblyMass, hip = hum.HipHeight, predkosc = hum.WalkSpeed, '
                    'skokMoc = hum.JumpPower, skokWys = hum.JumpHeight, zdrowie = hum.Health, stan = hum:GetState().Name, '
                    'poz = hrp.Position, przod = hrp.CFrame.LookVector, prawo = hrp.CFrame.RightVector, '
                    'kamera = workspace.CurrentCamera.CameraType.Name, zakotwiczona = hrp.Anchored }))'),
    "klasa": GR + 'return H:JSONEncode({ klasa = gracz:GetAttribute("Class") or false })',
    "atrybut": GR + 'return H:JSONEncode(J({ v = gracz:GetAttribute("%s") }))',
    "zmien_klase": 'game:GetService("ReplicatedStorage"):WaitForChild("ChooseClass"):FireServer("%s") return "ok"',
    "przestaw": GR + ('local hrp = gracz.Character.HumanoidRootPart local p = Vector3.new(%f, %f, %f) '
                      'gracz.Character:PivotTo(CFrame.lookAt(p, Vector3.new(%f, p.Y, %f))) hrp.AssemblyLinearVelocity = Vector3.zero return "ok"'),
    # kamera gracza za plecami postaci (klawisz W idzie tam, gdzie patrzy kamera)
    "kamera_za": LP + ('local c = workspace.CurrentCamera if hrp and c.CameraType == Enum.CameraType.Custom then '
                       'c.CFrame = CFrame.lookAt(hrp.Position - hrp.CFrame.LookVector * %f + Vector3.new(0, %f, 0), hrp.Position) end return "ok"'),
    "wlacz": 'return tostring(workspace.BohaterSwiat.Sygnaly.SterowanieSerwera:Invoke("wlacz", %s))',
    # kierunek od postaci, w którym przez %f st nie ma przeszkód, a ziemia jest najrówniejsza (24 kierunki co 15°)
    "wolny_kierunek": LP + ('local par = RaycastParams.new() par.FilterType = Enum.RaycastFilterType.Exclude '
                            'local wyklucz = { postac } for _, n in { "BohaterSwiat", "PetyProba" } do '
                            'local o = workspace:FindFirstChild(n) if o then table.insert(wyklucz, o) end end '
                            'par.FilterDescendantsInstances = wyklucz par.RespectCanCollide = true '
                            'local p0 = hrp.Position local d0 = workspace:Raycast(p0, Vector3.new(0, -8, 0), par) '
                            'if not d0 then return H:JSONEncode({}) end local y0 = d0.Position.Y '
                            'local najlepszy, najdalej, najrowniej = nil, 0, 99 '
                            'for i = 0, 23 do local a = i * math.pi / 12 local dir = Vector3.new(math.sin(a), 0, math.cos(a)) '
                            'local dal = %f for _, h in { 0.6, 2.5, 4.5 } do local skad = Vector3.new(p0.X, y0 + h, p0.Z) '
                            'local r = workspace:Raycast(skad, dir * dal, par) '
                            'if r then dal = math.min(dal, (r.Position - skad).Magnitude) end end '
                            'local nierownosc, s = 0, 1 while s <= dal do '
                            'local g = workspace:Raycast(Vector3.new(p0.X, y0 + 3, p0.Z) + dir * s, Vector3.new(0, -9, 0), par) '
                            'if not g then dal = s - 1 break end nierownosc = math.max(nierownosc, math.abs(g.Position.Y - y0)) s += 1 end '
                            'if dal > najdalej + 0.5 or (dal > najdalej - 0.5 and nierownosc < najrowniej) then '
                            'najlepszy, najdalej, najrowniej = dir, dal, nierownosc end end '
                            'return H:JSONEncode(J({ kierunek = najlepszy, dal = najdalej, nierownosc = najrowniej }))'),
    "stroj_ustaw": GR + 'return H:JSONEncode(J(workspace.StrojeProba.Sygnaly.SterowanieSerwera:Invoke("ustaw", gracz, "%s", %s)))',
    "kowal_stan": GR + ('local kw = workspace:FindFirstChild("KowalProba") return H:JSONEncode({ jest = kw ~= nil, '
                        'dostepne = gracz:GetAttribute("KowalDostepne") or false })'),
    "kowal_daj": GR + 'return H:JSONEncode(J(workspace.KowalProba.Sygnaly.SterowanieSerwera:Invoke("daj", gracz, "%s")))',
    "kowal_lup": GR + 'return H:JSONEncode(J(workspace.KowalProba.Sygnaly.SterowanieSerwera:Invoke("lup", gracz, "%s", %f)))',
    "reset": GR + 'local h = gracz.Character and gracz.Character:FindFirstChildOfClass("Humanoid") if h then h.Health = 0 end return "ok"',
    # ślad: stan lokalnego bohatera (i odległość peta, gdy jest) co 0,04 s przez %f s → atrybut kontenera ProbaSlad (u klienta)
    "slad": KB + ('local s = k.Sygnaly.SterowanieKlienta local pk = workspace:FindFirstChild("PetyProba") '
                  'k:SetAttribute("ProbaSlad", nil) task.spawn(function() '
                  'local t0, lista = os.clock(), {} while os.clock() - t0 < %f do local st = s:Invoke("stan") local l = st.lokalny '
                  'local ps = pk and pk.Sygnaly.SterowanieKlienta:Invoke("stan") '
                  'table.insert(lista, { t = os.clock() - t0, tryb = l and l.tryb or false, tempo = l and l.tempo or 0, '
                  'v = l and l.predkosc or 0, stopy = l and l.stopyNadZiemia or false, y = l and l.hrp[2] or 0, '
                  'od = l and l.odPostaci or 0, ltm = l and l.ltm or 0, wb = l and l.wagaBiegu or 0, '
                  'pet = ps and ps.odleglosc or false }) task.wait(0.04) end '
                  'k:SetAttribute("ProbaSlad", H:JSONEncode(J(lista))) end) return "ok"'),
    # zakręt: największy i najmniejszy przechył tułowia lokalnego bohatera przez %f s → atrybut ProbaSkret (u klienta)
    "skret_slad": KB + ('local s = k.Sygnaly.SterowanieKlienta k:SetAttribute("ProbaSkret", nil) task.spawn(function() '
                        'local t0, mn, mx, tryby = os.clock(), 0, 0, {} while os.clock() - t0 < %f do '
                        'local l = s:Invoke("stan").lokalny if l then mn = math.min(mn, l.skret) mx = math.max(mx, l.skret) '
                        'tryby[l.tryb] = true end task.wait(0.03) end '
                        'k:SetAttribute("ProbaSkret", H:JSONEncode(J({ mn = mn, mx = mx, tryby = tryby }))) end) return "ok"'),
    "skret_czytaj": KB + 'return k:GetAttribute("ProbaSkret") or "null"',
    "slad_czytaj": KB + 'return k:GetAttribute("ProbaSlad") or "null"',
    # skok do zrzutu: po spacji postać zostaje na chwilę zawieszona w powietrzu (tylko postać próby, tylko w tej sesji Play)
    "zawies": LP + ('task.spawn(function() local t0 = os.clock() while os.clock() - t0 < 1.5 and hrp.AssemblyLinearVelocity.Y < 5 do '
                    'task.wait() end task.wait(%f) hrp.Anchored = true task.wait(%f) hrp.Anchored = false end) return "ok"'),
    "fps": ('local RS = game:GetService("RunService") local n, t0 = 0, os.clock() while os.clock() - t0 < %f do '
            'RS.RenderStepped:Wait() n += 1 end return tostring(n / (os.clock() - t0))'),
    "manekiny": LP + ('local s = workspace.BohaterSwiat.Sygnaly.SterowanieKlienta postac.Archivable = true '
                      'local f = workspace:FindFirstChild("BohaterSwiatProba") or Instance.new("Folder") f.Name = "BohaterSwiatProba" '
                      'f.Parent = workspace local klasy = { "wojownik", "zwiadowca", "mag" } local n, nr = 0, 0 '
                      'for _, odl in { %s } do nr += 1 local m = postac:Clone() m.Name = "Manekin" '
                      'for _, d in m:GetDescendants() do if d:IsA("LuaSourceContainer") then d:Destroy() end end '
                      'local h = m:FindFirstChildOfClass("Humanoid") if h then h.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None end '
                      'local kat = nr * 0.9 m:PivotTo(postac:GetPivot() * CFrame.new(math.cos(kat) * odl, 0.5, math.sin(kat) * odl)) '
                      'local r = m:FindFirstChild("HumanoidRootPart") if r and odl > 100 then r.Anchored = true end m.Parent = f '
                      'if s:Invoke("manekin", m, klasy[nr - 3 * math.floor((nr - 1) / 3)]) then n += 1 end end return tostring(n)'),
    # ściana próby (tylko u klienta, tylko w tej sesji Play): środek %f %f %f, przodem do punktu %f %f %f
    "sciana": ('local f = workspace:FindFirstChild("BohaterSwiatProba") or Instance.new("Folder") f.Name = "BohaterSwiatProba" '
               'f.Parent = workspace local s = Instance.new("Part") s.Name = "Sciana" s.Anchored = true s.Size = Vector3.new(16, 10, 1) '
               's.Transparency = 0.6 s.CFrame = CFrame.lookAt(Vector3.new(%f, %f, %f), Vector3.new(%f, %f, %f)) s.Parent = f return "ok"'),
    "manekiny_usun": ('workspace.BohaterSwiat.Sygnaly.SterowanieKlienta:Invoke("manekin_usun") '
                      'local f = workspace:FindFirstChild("BohaterSwiatProba") if f then f:Destroy() end return "ok"'),
    # pety (swiat/pety_proba): Złoto próby, kupno haczykiem, kamera próby nie chowa petów
    "pet_kup": GR + ('gracz:SetAttribute("Gold", 5000) '
                     'return H:JSONEncode(J({ w = workspace.PetyProba.Sygnaly.SterowanieSerwera:Invoke("kup", gracz, nil, 0.5) }))'),
    "pet_klient": 'return H:JSONEncode(J(workspace.PetyProba.Sygnaly.SterowanieKlienta:Invoke("stan")))',
    "pet_kamera": 'workspace.PetyProba:SetAttribute("TestKameraProby", %s) return "ok"',
    # las-pas (swiat/las_pas_gra): wolny potwór w strefie, walka jak po E, odtwarzacz walki
    "potwor": ('local k = workspace:FindFirstChild("LasPasGra") local najlepszy for _, c in k.Stan:GetChildren() do '
               'if c:GetAttribute("Strefa") == "%s" and c:GetAttribute("Stan") ~= "zajety" then najlepszy = c break end end '
               'if not najlepszy then return H:JSONEncode({}) end '
               'return H:JSONEncode({ id = najlepszy.Name, p = J(najlepszy:GetAttribute("Pozycja")) })'),
    "potwor_gdzie": ('local c = workspace.LasPasGra.Stan:FindFirstChild("%s") '
                     'return H:JSONEncode({ p = c and J(c:GetAttribute("Pozycja")) or false, stan = c and c:GetAttribute("Stan") or false })'),
    "test_bohater": 'local k = workspace:FindFirstChild("%s") if k then k:SetAttribute("TestBohater", %s) end return "ok"',
    # czy trwa przelot kamery lasu-pasa albo inna blokada postaci (kamera nie gracza, postać zakotwiczona, blokada walk)
    "przelot": LP + ('return tostring((hrp ~= nil and hrp.Anchored) or workspace.CurrentCamera.CameraType ~= Enum.CameraType.Custom '
                     'or lp:GetAttribute("BlokadaWalki") == true)'),
    "walcz": 'return tostring(workspace.LasPasGra.Sygnaly.SterowanieKlienta:Invoke("walcz", "%s"))',
    "potwory_klient": ('local k = workspace.LasPasGra local st = k.Sygnaly.SterowanieKlienta:Invoke("stan") '
                       'return H:JSONEncode(J({ walka = st.walka, odmowa = k:GetAttribute("OstatniaOdmowa") or false }))'),
    "odtw": 'return H:JSONEncode(J(workspace.TestWalki2.Sygnaly.Sterowanie:Invoke(%s)))',
    "aktor_walki": ('local m = nil for _, k in workspace:GetChildren() do local s = k:FindFirstChild("ScenaLokalna") '
                    'if s then m = s:FindFirstChild("%s_lokalny") or m end end local n = 0 if m then for _, d in m:GetDescendants() do '
                    'if d:IsA("BasePart") and d.Transparency < 1 and d.Name ~= "HumanoidRootPart" and d:GetAttribute("Obrys") == nil '
                    'and d:GetAttribute("Punkt") == nil then n += 1 end end end '
                    'return H:JSONEncode({ jest = m ~= nil, stroj = m and m:GetAttribute("Stroj") or false, bryly = n })'),
    # teleport przez chmury (swiat/teleport_chmury)
    "chmury_serwer": GR + 'return H:JSONEncode(J(workspace.TeleportChmury.Sygnaly.SterowanieSerwera:Invoke("odblokuj", "%s", gracz)))',
    "chmury_klient": 'return H:JSONEncode(J(workspace.TeleportChmury.Sygnaly.SterowanieKlienta:Invoke(%s)))',
    # Training Center (swiat/trening_proba)
    "trening_punkt": 'local t = workspace:FindFirstChild("TreningProba") return H:JSONEncode(J({ p = t and t:GetAttribute("PunktTablicy") }))',
    "trening_start": 'return tostring(workspace.TreningProba.Sygnaly.WybierzGre:Invoke("%s"))',
    "trening_stan": GR + ('local t = workspace:FindFirstChild("TreningProba") return H:JSONEncode(J({ gra = gracz:GetAttribute("TreningGra") or false, '
                          'rund = t and t:GetAttribute("LicznikRund") or 0, odmowa = t and t:GetAttribute("OstatniaOdmowa") ~= nil }))'),
}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def sprawdz_kod():
    """Bez Studio: każdy szablon z KOD (po podstawieniu zer) parsuje się w luau_mini."""
    import luau_mini as LM
    bledy = []
    for nazwa, szablon in KOD.items():
        kod = re.sub(r"%[sdf]", "0", szablon)
        try:
            LM.Parser(J + kod, nazwa, LM.Interpreter()).program()
        except LM.BladSkladni as e:
            bledy.append("%s: %s" % (nazwa, e))
    with open(os.path.abspath(__file__), encoding="utf-8") as f:
        tekst = f.read()
    brak = [p for p in PUNKTY if ('punkt("%s"' % p) not in tekst]
    if brak:
        bledy.append("punkty bez wyniku w kodzie próby: %s" % ", ".join(brak))
    print("sprawdz: %d kawałków Luau, %d punktów listy, %s" % (len(KOD), len(PUNKTY),
                                                               "OK" if not bledy else "BŁĘDY:\n  " + "\n  ".join(bledy)))
    return 0 if not bledy else 1


def slownik(v):
    """Pusta tabela Luau wraca z JSON jako [] — tam, gdzie spodziewamy się słownika, robimy z niej {}."""
    return v if isinstance(v, dict) else {}


def dryf_stop(klatki, min_waga=0.999):
    """Nagranie klienta ({ t, tryb, waga biegu, faza, podpór, v, lewa xyz, prawa xyz, hrp xyz } na klatkę) → największe
    przesunięcie stopy w podporze po ziemi (studs) w jednym podporze, liczba podporów i klatek w podporze."""
    najwiecej, podpory, klatek = 0.0, 0, 0
    for przes, kol in ((0.0, 6), (0.5, 9)):
        start = None
        # stawy dostają pozę z poprzedniej klatki (silnik stosuje Motor6D.Transform po kroku fizyki), więc miejsce stopy
        # w klatce i odpowiada fazie z klatki i − 1
        for poprzednia, k in zip(klatki, klatki[1:]):
            fz = (poprzednia[3] + przes) % 1.0
            # tylko klatki sąsiednie w czasie: lista bywa przesiana (np. sama pełna prędkość) i ma wtedy dziury
            if (k[1] == "bieg" and poprzednia[1] == "bieg" and k[2] >= min_waga and fz < poprzednia[4]
                    and 0 <= k[0] - poprzednia[0] < 0.07):
                p = (k[kol], k[kol + 2])
                if start is None:
                    start = p
                    podpory += 1
                klatek += 1
                najwiecej = max(najwiecej, math.hypot(p[0] - start[0], p[1] - start[1]))
            else:
                start = None
    return najwiecej, podpory, klatek


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
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
    tylko = set()
    if "--tylko" in argv:
        tylko = {x.strip() for x in argv[argv.index("--tylko") + 1].split(",") if x.strip()}
    os.makedirs(wyj, exist_ok=True)
    os.makedirs(KLATKI, exist_ok=True)

    D = DN.zbierz()
    DS = DN.dane_strojow()
    Ds, _ = DS.zbierz()
    import logika_strojow as LS
    from cel_studio import wybierz_studio  # noqa: E402
    from sesja_play import SesjaPlay  # noqa: E402  (tylko odczyt: wspólna obsługa Play próby walki)
    from studio_mcp import StudioMCP, StudioError  # noqa: E402

    class Sesja(SesjaPlay):
        def zamknij_wybor_klasy(self):      # klasę wybiera próba: B01 sprawdza stan SPRZED wyboru
            return True

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

    def chce(kod):
        return not tylko or kod in tylko

    def bryly(klasa, napis):
        """Liczba brył bohatera klasy w stroju z atrybutu (None = strój odniesienia) — z danych przymierzalni."""
        ids = LS.z_napisu(napis)
        if ids is None:
            ids = Ds["klasy"][klasa]["odniesienie"]
        ok, plan = LS.plan(Ds, klasa, list(ids))
        if not ok:
            ok, plan = LS.plan(Ds, klasa, Ds["klasy"][klasa]["odniesienie"])
        return len(DS.zloz(Ds, klasa, plan)), LS.na_napis(plan["przedmioty"])

    # ------------------------------------------------------------------ B00 w Edit (przed Play)
    with StudioMCP(timeout=60) as s0:
        sid0 = wybierz_studio(s0, studio)
        r = s0.call("execute_luau", {"code": 'local H = game:GetService("HttpService") ' + KOD["edit"], "datamodel_type": "Edit",
                                     "studio_id": sid0}, timeout=60)
        if r["is_error"]:
            sys.exit("B00: %s" % r["text"][:500])
        e = json.loads(r["text"])
    zapisz("B00", e)
    ok00 = bool(e.get("bohater") and e.get("walka") and e.get("stroje") and e.get("sygnal") and e.get("czesci") == 0
                and e.get("skrot") == D["skrot"] and e.get("skrypty") == 4)
    punkt("B00", ok00, "kontener %s, skrót %s (lokalny %s), skryptów %s, części %s, wyłącznik %s, RuchBohatera %s; TestWalki2 %s, "
          "StrojeProba %s; dodatki: kowal %s, pety %s, stan gracza %s, las-pas %s, chmury %s, trening %s"
          % (e.get("bohater"), e.get("skrot"), D["skrot"], e.get("skrypty"), e.get("czesci"), e.get("wlacznik"), e.get("sygnal"),
             e.get("walka"), e.get("stroje"), e.get("kowal"), e.get("pety"), e.get("stan"), e.get("pas"), e.get("chmury"),
             e.get("trening")))
    if not ok00:
        log("bez kontenera i zależności próba w Play nie ma sensu — koniec")
        return 1

    with Sesja(studio) as sp:
        def js(kod, dm="Client"):
            return json.loads(sp.luau(J + kod, dm))

        def klient(argi='"stan"'):
            return slownik(js(KOD["klient"] % argi))

        def lokalny():
            return slownik(klient().get("lokalny"))

        def ruch(argi):
            return slownik(js(KOD["ruch"] % argi)).get("w")

        def postac():
            return slownik(js(KOD["postac"]))

        def awatar():
            return slownik(js(KOD["awatar"]))

        def atrybut(nazwa):
            return slownik(js(KOD["atrybut"] % nazwa, "Server")).get("v")

        def czekaj(warunek, limit, co=0.3):
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

        def obraz(oko=None, cel=None):
            return sp.zrzut(oko, cel) if oko else sp.zrzut()

        def zrzut(nazwa, oko=None, cel=None):
            if bez_zrzutow:
                return
            try:
                o = obraz(oko, cel)
                o.thumbnail((1280, 1280))
                o.save(os.path.join(KLATKI, nazwa + ".jpg"), quality=86)
                log("zrzut", nazwa)
            except Exception as ex:  # noqa: BLE001 — zrzut nie może przerwać próby
                log("zrzut %s: %s" % (nazwa, str(ex)[:200]))

        def ujecie(dal=9.0, bok=5.0, wys=2.5):
            """Kamera zrzutu z przodu i z boku postaci (narzędzie zrzutu; kamera gracza zostaje zwykła)."""
            p = postac()
            if p.get("brak"):
                return None, None
            poz, przod, prawo = p["poz"], p["przod"], p["prawo"]
            oko = (poz[0] + przod[0] * dal + prawo[0] * bok, poz[1] + wys, poz[2] + przod[2] * dal + prawo[2] * bok)
            return oko, (poz[0], poz[1] - 0.3, poz[2])

        def zrzut_postaci(nazwa, **k):
            oko, cel = ujecie(**k)
            if oko:
                zrzut(nazwa, oko, cel)

        def slad(sekundy, akcja):
            """Ślad stanu lokalnego bohatera w czasie akcji (lista próbek)."""
            sp.luau(J + KOD["slad"] % sekundy)
            akcja()
            w = czekaj(lambda: json.loads(sp.luau(J + KOD["slad_czytaj"])), sekundy + 8, 0.5)
            return w if isinstance(w, list) else []

        def klawisz_w(ms):
            """Prawdziwy klawisz W przez ms milisekund (postać idzie tam, gdzie patrzy kamera)."""
            sp.call("user_keyboard_input", {"datamodel_type": "Client", "actions": [
                {"action": "keyDown", "key_code": "W"}, {"action": "wait", "wait_time_ms": int(ms)},
                {"action": "keyUp", "key_code": "W"}]})

        START = {}

        def na_start(dal=12.0, wys=5.0):
            """Postać wraca na miejsce startu próby, przodem jak na starcie, kamera gracza za plecami."""
            if not START:
                return
            p, f = START["poz"], START["przod"]
            sp.luau(KOD["przestaw"] % (p[0], p[1] + 0.3, p[2], p[0] + f[0] * 10, p[2] + f[2] * 10), "Server")
            time.sleep(0.7)
            sp.luau(KOD["kamera_za"] % (dal, wys))
            time.sleep(0.4)

        def wlacz(tak):
            sp.luau(KOD["wlacz"] % ("true" if tak else "false"), "Server")

        def klasa_gracza():
            return L.klasa(D, slownik(js(KOD["klasa"], "Server")).get("klasa") or None)

        def bohater_gotowy(klasa=None, stroj=None, limit=12):
            def w():
                l = lokalny()
                if not l.get("aktywny") or (klasa and l.get("klasa") != klasa):
                    return None
                if stroj is not None and l.get("stroj") != stroj:
                    return None
                return l
            return czekaj(w, limit) or {}

        def kowal_daj_wszystko(klasa):
            """Tryb z kowalem: przymierzalnia zakłada tylko posiadane przedmioty — próba daje graczowi brakujące całe
            przedmioty klasy haczykiem kowala (jak próba przymierzalni). Zwraca listę danych."""
            ks = slownik(js(KOD["kowal_stan"], "Server"))
            if not ks.get("jest") or not isinstance(ks.get("dostepne"), str):
                return None
            mam = set(ks["dostepne"].split(","))
            dane = []
            for i in Ds["klasy"][klasa]["przedmioty"]:
                if i not in mam and not Ds["przedmioty"][i].get("czescOd"):
                    if slownik(js(KOD["kowal_daj"] % i, "Server")).get("ok"):
                        dane.append(i)
            time.sleep(0.5)
            return dane

        def krok(kod, fn):
            if not chce(kod):
                return
            try:
                fn()
            except Exception as ex:  # noqa: BLE001 — jeden punkt nie przerywa reszty
                punkt(kod, False, "wyjątek próby: %s" % str(ex)[:300])

        sp.luau(KOD["bez_nazwy"])
        stan0 = {}

        # ------------------------------------------------------------------ B01 przed wyborem klasy
        def b01():
            g = czekaj(lambda: (lambda x: x if x.get("klient") and x.get("serwer") else None)(slownik(js(KOD["gotowosc"]))), 25) or {}
            st, a, r = klient(), awatar(), ruch('"stan"')
            zapisz("B01", {"gotowosc": g, "stan": st, "awatar": a, "ruch": r})
            punkt("B01", bool(g.get("klient") and g.get("serwer") and g.get("skrotK") == D["skrot"] and g.get("skrotS") == D["skrot"]
                              and not st.get("lokalny") and st.get("bohaterow") == 0 and a.get("widoczne", 0) > 5 and r is None),
                  "klient %s, serwer %s, skróty %s / %s; przed wyborem klasy: bohaterów %s, widoczne części awatara %s, "
                  "RuchBohatera „stan” → %r" % (g.get("klient"), g.get("serwer"), g.get("skrotK"), g.get("skrotS"),
                                                st.get("bohaterow"), a.get("widoczne"), r))
        krok("B01", b01)

        # ------------------------------------------------------------------ B02 wybór klasy → bohater
        SesjaPlay.zamknij_wybor_klasy(sp)
        klasa = czekaj(klasa_gracza, 15)
        log("klasa gracza:", klasa)
        time.sleep(1.0)
        p_start = postac()
        if not p_start.get("brak"):
            START.update(poz=p_start["poz"], przod=p_start["przod"])
            # próby ruchu biegną tam, gdzie od startu jest najdłuższa wolna i najrówniejsza droga (plac ma stopnie i ławki)
            wk = slownik(js(KOD["wolny_kierunek"] % 34.0))
            if isinstance(wk.get("kierunek"), list):
                START.update(przod=wk["kierunek"], wolne=wk.get("dal"), nierownosc=wk.get("nierownosc"))
            log("start próby: wolna droga %s st, nierówność ziemi %s st" % (START.get("wolne"), START.get("nierownosc")))

        def b02():
            l = bohater_gotowy(klasa, limit=20)
            napis = atrybut(D["atrybut_stroju"] + (klasa or "x"))
            n, stroj = bryly(klasa, napis) if klasa else (0, None)
            a, st = awatar(), klient()
            stan0.update(l)
            zapisz("B02", {"lokalny": l, "awatar": a, "atrybut_stroju": napis, "oczekiwane_bryly": n, "zaleznosci": st.get("zaleznosci"),
                           "powod": st.get("powod")})
            punkt("B02", bool(klasa and l.get("klasa") == klasa and l.get("bryly") == n and l.get("strojBryly") == n
                              and l.get("stroj") == stroj and a.get("widoczne") == 0),
                  "klasa %s → bohater %s, strój %r (atrybut gracza %r), bryły %s (dane %s), instancji %s, budowa %.0f ms; "
                  "awatar: widoczne %s, schowane %s%s"
                  % (klasa, l.get("klasa"), l.get("stroj"), napis, l.get("bryly"), n, l.get("instancji"), l.get("budowa_ms") or 0,
                     a.get("widoczne"), a.get("ukryte"), "" if l else "; zależności %s (%s)" % (st.get("zaleznosci"), st.get("powod"))))
        krok("B02", b02)

        # ------------------------------------------------------------------ B03 fizyka postaci bez zmian
        def b03():
            l = bohater_gotowy(klasa)
            z = postac()
            wlacz(False)
            czekaj(lambda: not lokalny().get("aktywny"), 5)
            bez = postac()
            wlacz(True)
            bohater_gotowy(klasa)
            pola = ("masa", "hip", "predkosc", "skokMoc", "skokWys")
            rozne = [p for p in pola if abs((z.get(p) or 0) - (bez.get(p) or 0)) > 1e-3]
            f = slownik(l.get("fizyka"))
            zapisz("B03", {"z_bohaterem": z, "bez": bez, "fizyka": f})
            punkt("B03", f.get("zle") == 0 and f.get("zakotwiczony") is True and not rozne and not z.get("zakotwiczona"),
                  "części bohatera w fizyce %s, korzeń zakotwiczony %s; postać z bohaterem / bez: masa %.3f / %.3f, HipHeight "
                  "%.2f / %.2f, WalkSpeed %s / %s, skok %.1f / %.1f%s"
                  % (f.get("zle"), f.get("zakotwiczony"), z.get("masa") or -1, bez.get("masa") or -1, z.get("hip") or -1,
                     bez.get("hip") or -1, z.get("predkosc"), bez.get("predkosc"), z.get("skokWys") or -1, bez.get("skokWys") or -1,
                     "; RÓŻNE: %s" % rozne if rozne else ""))
        krok("B03", b03)

        # ------------------------------------------------------------------ B04 stopy na ziemi
        def b04():
            na_start()
            time.sleep(0.6)
            l = bohater_gotowy(klasa)
            stopy = l.get("stopyNadZiemia")
            zapisz("B04", l)
            zrzut("02_zza_plecow_kamera_gracza")
            punkt("B04", isinstance(stopy, (int, float)) and abs(stopy) <= 0.12 and (l.get("odPostaci") or 9) <= 0.35
                  and (l.get("zgodnoscPrzodu") or 0) >= 0.999 and l.get("tryb") == "idle",
                  "stopy %.3f st nad ziemią (spód rigu %.3f), bohater %.3f st od punktu pod postacią, zgodność przodu %.4f, tryb %s"
                  % (stopy if isinstance(stopy, (int, float)) else 99, l.get("spod") or 0, l.get("odPostaci") or 9,
                     l.get("zgodnoscPrzodu") or 0, l.get("tryb")))
        krok("B04", b04)

        # ------------------------------------------------------------------ B05 ruch po ziemi (prawdziwy klawisz W)
        def b05():
            na_start()
            probki = slad(3.6, lambda: (time.sleep(0.5), klawisz_w(1300), time.sleep(1.4)))
            tryby = [x.get("tryb") for x in probki]
            w_ruchu = [x for x in probki if x.get("tryb") in ("chod", "bieg")]
            stopy = [x["stopy"] for x in w_ruchu if isinstance(x.get("stopy"), (int, float))]
            tempa = [x["tempo"] for x in probki if x.get("tryb") == "chod" and x.get("tempo")]
            predkosci = [x.get("v", 0) for x in w_ruchu]
            koniec = lokalny()
            R = D["ruch"]
            # zrzut biegu w bazarze: klatka cyklu biegu zatrzymana haczykiem (zrzutu w trakcie klawisza zrobić się nie da)
            na_start()
            ruch('"klip", "bieg"')
            js(KOD["klient"] % '"faza_biegu", 0.1')
            time.sleep(0.5)
            zrzut_postaci("01_bazar_bieg", dal=6.0, bok=8.0, wys=1.2)
            js(KOD["klient"] % '"faza_biegu", nil')
            ruch('"klip", nil')
            time.sleep(0.4)
            # droga z W: z bohaterem i bez, z tego samego miejsca
            d_z = sp.klawisz_w(1000)
            na_start()
            wlacz(False)
            czekaj(lambda: not lokalny().get("aktywny"), 5)
            d_bez = sp.klawisz_w(1000)
            wlacz(True)
            bohater_gotowy(klasa)
            na_start()
            zapisz("B05", {"wolna_droga": START.get("wolne"), "nierownosc": START.get("nierownosc"), "tryby": tryby, "tempa": tempa[:40], "stopy": stopy[:80], "predkosci": predkosci[:80], "koniec": koniec,
                           "droga_z": d_z, "droga_bez": d_bez})
            kolejnosc = [t for i, t in enumerate(tryby) if t and (i == 0 or t != tryby[i - 1])]
            punkt("B05", len(w_ruchu) >= 10 and "bieg" in tryby and all(R["tempo_min"] - 1e-6 <= t <= R["tempo_max"] + 1e-6 for t in tempa)
                  and bool(stopy) and min(stopy) >= -0.2 and max(stopy) <= 1.2 and tryby[0] == "idle" and koniec.get("tryb") == "idle"
                  and d_bez > 5 and abs(d_z - d_bez) <= max(1.5, 0.12 * d_bez),
                  "klawisz W 1,3 s: %s; %d próbek w ruchu, prędkość do %.1f st/s, stopy %.2f…%.2f st nad ziemią; po zatrzymaniu %s; "
                  "droga z klawisza W przez 1 s: z bohaterem %.1f st, bez %.1f st"
                  % (" → ".join(kolejnosc), len(w_ruchu), max(predkosci or [0]), min(stopy or [0]), max(stopy or [0]),
                     koniec.get("tryb"), d_z, d_bez))
        krok("B05", b05)

        # ------------------------------------------------------------------ B06 skok
        def b06():
            na_start()
            probki = slad(3.5, lambda: (time.sleep(0.4), sp.klawisz("Space"), time.sleep(2.6)))
            tryby = [x.get("tryb") for x in probki]
            ys = [x.get("y", 0) for x in probki]
            # zrzut: drugi skok z zawieszeniem postaci w powietrzu (stan lotu trwa, poza spadania)
            sp.luau(J + KOD["zawies"] % (0.12, 2.2))
            sp.klawisz("Space")
            time.sleep(0.9)
            w_locie = lokalny()
            zrzut_postaci("04_skok_w_powietrzu", dal=8.0, bok=4.0, wys=1.5)
            time.sleep(2.2)
            koniec = czekaj(lambda: (lambda l: l if l.get("tryb") == "idle" else None)(lokalny()), 6) or {}
            zapisz("B06", {"tryby": tryby, "wzniesienie": (max(ys) - ys[0]) if ys else 0, "w_locie": w_locie, "koniec": koniec})
            punkt("B06", "skok" in tryby and "spadanie" in tryby and "ladowanie" in tryby and bool(ys) and max(ys) - ys[0] >= 1.0
                  and tryby[-1] in ("idle", "chod") and koniec.get("tryb") == "idle" and w_locie.get("tryb") in ("skok", "spadanie"),
                  "kolejność trybów: %s; wzniesienie w próbkach %.1f st; zawieszony w powietrzu: %s; na końcu %s"
                  % (" → ".join(t for i, t in enumerate(tryby) if t and (i == 0 or t != tryby[i - 1])),
                     (max(ys) - ys[0]) if ys else 0, w_locie.get("tryb"), koniec.get("tryb")))
        krok("B06", b06)

        # ------------------------------------------------------------------ B07 wyłącznik
        def b07():
            na_start()
            t0 = time.time()
            wlacz(False)
            zniknal = czekaj(lambda: not lokalny().get("aktywny"), 5, 0.1)
            t_off = time.time() - t0
            a_off, r_off = awatar(), ruch('"stan"')
            zrzut_postaci("07_wylacznik_awatar")
            t0 = time.time()
            wlacz(True)
            l = bohater_gotowy(klasa)
            t_on = time.time() - t0
            a_on = awatar()
            zapisz("B07", {"t_off": t_off, "t_on": t_on, "awatar_off": a_off, "awatar_on": a_on, "ruch_off": r_off})
            punkt("B07", bool(zniknal) and a_off.get("widoczne", 0) > 5 and r_off is None and bool(l.get("aktywny"))
                  and a_on.get("widoczne") == 0,
                  "false → bohater zniknął po %.1f s (razem z czasem zapytań próby), widoczne części awatara %s, RuchBohatera „stan” → "
                  "%r; true → bohater po %.1f s, widoczne części awatara %s"
                  % (t_off, a_off.get("widoczne"), r_off, t_on, a_on.get("widoczne")))
        krok("B07", b07)

        # ------------------------------------------------------------------ B10 kowal (przed przebieraniem w B09)
        def b10():
            ks = slownik(js(KOD["kowal_stan"], "Server"))
            if not ks.get("jest") or not isinstance(ks.get("dostepne"), str):
                punkt("B10", None, "kowala na próbę nie ma w miejscu albo gracz nie ma jego danych — pominięte")
                return
            mam = set(ks["dostepne"].split(","))
            przed = atrybut(D["atrybut_stroju"] + klasa)
            # łup z walki (haczyk kowala, pewny łup): losujemy, aż wypadnie przedmiot, którego gracz nie miał
            nowy, proby = None, []
            for ranga in ("zwykly", "elita", "boss"):
                for los in (0.03, 0.2, 0.37, 0.54, 0.71, 0.88, 0.97):
                    odp = slownik(js(KOD["kowal_lup"] % (ranga, los), "Server"))
                    lup = slownik(odp.get("lup"))
                    proby.append((ranga, los, lup.get("id"), lup.get("nowy")))
                    if lup.get("nowy") and lup.get("id") not in mam:
                        nowy = lup["id"]
                        break
                if nowy:
                    break
            if not nowy:
                zapisz("B10", {"proby": proby, "mam": sorted(mam)})
                punkt("B10", None, "w %d losowaniach łupu nie wypadł nowy przedmiot (gracz ma: %s) — pominięte" % (len(proby), sorted(mam)))
                return
            po = czekaj(lambda: (lambda v: v if isinstance(v, str) and nowy in v.split(",") else None)(
                atrybut(D["atrybut_stroju"] + klasa)), 8)
            n, stroj = bryly(klasa, po) if po else (0, None)
            l = bohater_gotowy(klasa, stroj) if po else {}
            zrzut_postaci("08_kowal_nowy_przedmiot", dal=8.0, bok=3.5, wys=1.8)
            zapisz("B10", {"nowy": nowy, "proby": proby, "przed": przed, "po": po, "lokalny": l})
            punkt("B10", bool(po) and l.get("stroj") == stroj and l.get("bryly") == n,
                  "łup kowala: nowy przedmiot %s (po %d losowaniach) → strój gracza %r → %r; bohater w świecie: strój %r, bryły %s "
                  "(dane %s)" % (nowy, len(proby), przed, po, l.get("stroj"), l.get("bryly"), n))
        krok("B10", b10)

        # ------------------------------------------------------------------ B08 trzy klasy
        def b08():
            na_start()
            wyniki, zle = {}, []
            for gra, klucz in list(D["klasy_gracza"].items()) + [(D["klasy"][klasa]["klasaGry"], klasa)]:
                sp.luau(KOD["zmien_klase"] % gra)
                time.sleep(0.7)
                l = bohater_gotowy(klucz)
                n, stroj = bryly(klucz, atrybut(D["atrybut_stroju"] + klucz))
                a = awatar()
                wyniki[klucz] = {"klasa": l.get("klasa"), "bryly": l.get("bryly"), "oczekiwane": n, "stroj": l.get("stroj"),
                                 "stopy": l.get("stopyNadZiemia"), "instancji": l.get("instancji"), "budowa_ms": l.get("budowa_ms"),
                                 "awatar_widoczne": a.get("widoczne")}
                if not (l.get("klasa") == klucz and l.get("bryly") == n and l.get("stroj") == stroj and a.get("widoczne") == 0):
                    zle.append(klucz)
                time.sleep(0.6)
                zrzut_postaci("06_klasa_%s" % klucz, dal=8.0, bok=3.5, wys=1.8)
            zapisz("B08", wyniki)
            punkt("B08", not zle, "zmiana klasy przebudowuje bohatera: %s%s"
                  % (", ".join("%s %s brył (dane %s), %s instancji, budowa %.0f ms" % (k, v["bryly"], v["oczekiwane"], v["instancji"],
                                                                                     v["budowa_ms"] or 0) for k, v in wyniki.items()),
                     "; ZŁE: %s" % zle if zle else ""))
        krok("B08", b08)

        # ------------------------------------------------------------------ B09 strój z przymierzalni
        def b09():
            na_start()
            dane = kowal_daj_wszystko(klasa)
            wyniki, zle = {}, []
            for nazwa, ids in (("golas", []), ("mieszany", MIESZANE[klasa]), ("komplet", Ds["klasy"][klasa]["odniesienie"])):
                odp = slownik(js(KOD["stroj_ustaw"] % (klasa, json.dumps(",".join(ids))), "Server"))
                n, stroj = bryly(klasa, ",".join(ids))
                l = bohater_gotowy(klasa, stroj, limit=8)
                time.sleep(0.8)
                l = bohater_gotowy(klasa, stroj, limit=4)
                a = awatar()
                stopy = l.get("stopyNadZiemia")
                wyniki[nazwa] = {"odpowiedz": odp, "stroj": l.get("stroj"), "bryly": l.get("bryly"), "oczekiwane": n, "stopy": stopy,
                                 "spod": l.get("spod"), "awatar_widoczne": a.get("widoczne"),
                                 "atrybut": atrybut(D["atrybut_stroju"] + klasa)}
                if not (l.get("stroj") == stroj and l.get("bryly") == n and a.get("widoczne") == 0
                        and isinstance(stopy, (int, float)) and abs(stopy) <= 0.12):
                    zle.append(nazwa)
                zrzut_postaci("08_stroj_%s" % nazwa, dal=8.0, bok=3.5, wys=1.8)
            zapisz("B09", {"dane_przez_kowala": dane, "stroje": wyniki})
            punkt("B09", not zle, "strój z przymierzalni na bohaterze w świecie (%s%s): %s%s"
                  % (klasa, "" if dane is None else "; tryb z kowalem, próba dała %d przedmiotów" % len(dane),
                     ", ".join("%s %s brył (dane %s), stopy %.3f" % (k, v["bryly"], v["oczekiwane"],
                                                                 v["stopy"] if isinstance(v["stopy"], (int, float)) else 99)
                               for k, v in wyniki.items()), "; ZŁE: %s" % zle if zle else ""))
        krok("B09", b09)

        # ------------------------------------------------------------------ B11 reset postaci
        def b11():
            na_start()
            sp.luau(KOD["reset"], "Server")
            pada = czekaj(lambda: (lambda l: l if l.get("tryb") == "upadek" else None)(lokalny()), 3, 0.1) or {}
            time.sleep(1.0)
            zrzut_postaci("09_upadek")
            l = czekaj(lambda: (lambda x: x if x.get("aktywny") and x.get("tryb") in ("idle", "chod", "spadanie", "ladowanie")
                                else None)(lokalny()), 20, 0.5) or {}
            time.sleep(1.5)
            sp.luau(KOD["bez_nazwy"])
            a, st = awatar(), klient()
            zrzut_postaci("09_po_odrodzeniu")
            zapisz("B11", {"pada": pada, "po": l, "awatar": a, "ruch": st.get("ruch")})
            punkt("B11", pada.get("tryb") == "upadek" and bool(l.get("aktywny")) and l.get("klasa") == klasa and a.get("widoczne") == 0,
                  "po Health = 0 tryb %s (klip %s); po odrodzeniu bohater %s w trybie %s, widoczne części awatara %s"
                  % (pada.get("tryb"), pada.get("klip"), l.get("klasa"), l.get("tryb"), a.get("widoczne")))
            p = postac()
            if not p.get("brak") and math.dist(p["poz"], START.get("poz", p["poz"])) > 60:
                START.update(poz=p["poz"], przod=p["przod"])     # odrodzenie w innym miejscu: nowe miejsce startu próby
        krok("B11", b11)

        # ------------------------------------------------------------------ B12 umowa RuchBohatera
        def b12():
            na_start()
            K = D["klasy"][klasa]
            zle, zapis = [], {}
            s0 = ruch('"stan"')
            zapis["stan"] = s0
            if not (isinstance(s0, dict) and s0.get("aktywny") is True and s0.get("klasa") == klasa and s0.get("klip") == "idle"):
                zle.append("stan %r" % (s0,))
            p_przed = postac()["poz"]
            for klip in D["kontrakt"]["klipy"]:
                w = ruch('"klip", "%s"' % klip)
                time.sleep(0.7)
                s, l = ruch('"stan"'), lokalny()
                wagi = slownik(l.get("wagi"))
                zapis[klip] = {"wynik": w, "stan": s, "baza": l.get("baza"), "klip": l.get("klip"), "tempo": l.get("tempo"),
                               "wagi": wagi, "stopy": l.get("stopyNadZiemia"), "wagaBiegu": l.get("wagaBiegu")}
                dobrze = w is True and isinstance(s, dict) and s.get("klip") == klip
                if klip == "bieg":
                    dobrze = dobrze and l.get("baza") == "spoczynek" and (l.get("wagaBiegu") or 0) > 0.99
                elif klip == "radosc":
                    dobrze = dobrze and l.get("baza") == "radosc" and l.get("klip") == K["klipy"]["radosc"]
                else:
                    dobrze = dobrze and l.get("baza") == "spoczynek" and (wagi.get(klip) or 0) > 0.99
                    zrzut_postaci("10_umowa_%s" % klip, dal=8.0, bok=3.5, wys=1.8)
                if klip == "padnij":
                    st = l.get("stopyNadZiemia")
                    dobrze = dobrze and isinstance(st, (int, float)) and abs(st) <= 0.15
                if not dobrze:
                    zle.append(klip)
            p_po = postac()["poz"]
            zly = ruch('"klip", "taniec"')
            pusty = ruch('"klip", nil')
            time.sleep(0.6)
            s1 = ruch('"stan"')
            prz = ruch('"przesun", Vector3.new(0, 2, 0)')
            time.sleep(0.3)
            l_prz = lokalny()
            prz_zle = ruch('"przesun", "w gore"')
            prz0 = ruch('"przesun", nil')
            time.sleep(0.3)
            l0 = lokalny()
            nieznane = ruch('"salto"')
            zapis.update({"zly_klip": zly, "klip_nil": pusty, "stan_po": s1, "przesun": prz, "przesun_zly": prz_zle, "przesun_nil": prz0,
                          "od_postaci_z_przesunieciem": l_prz.get("odPostaci"), "od_postaci_po": l0.get("odPostaci"),
                          "nieznane": nieznane, "droga_postaci": math.dist(p_przed, p_po)})
            if zly is not False or pusty is not True or not (isinstance(s1, dict) and s1.get("klip") == "idle"):
                zle.append("zły klip %r / nil %r / stan po %r" % (zly, pusty, s1))
            if prz is not True or prz0 is not True or prz_zle is not False or abs((l_prz.get("odPostaci") or 0) - 2.0) > 0.35 \
                    or (l0.get("odPostaci") or 9) > 0.35:
                zle.append("przesunięcie %r / %r / zły typ %r: %.2f → %.2f" % (prz, prz0, prz_zle, l_prz.get("odPostaci") or -1,
                                                                             l0.get("odPostaci") or -1))
            if math.dist(p_przed, p_po) > 0.5:
                zle.append("postać ruszyła się o %.2f st" % math.dist(p_przed, p_po))
            zapisz("B12", zapis)
            punkt("B12", not zle, "stan %r; klipy %s → true i stan.klip = nazwa; „taniec” → %r; nil → %r (klip %s); przesun (0, 2, 0) → "
                  "bohater %.2f st nad punktem pod postacią, nil → %.2f; nieznane polecenie → %r; postać stoi (%.2f st)%s"
                  % (s0, ", ".join(D["kontrakt"]["klipy"]), zly, pusty, s1.get("klip") if isinstance(s1, dict) else s1,
                     l_prz.get("odPostaci") or -1, l0.get("odPostaci") or -1, nieznane, math.dist(p_przed, p_po),
                     "; ZŁE: %s" % zle if zle else ""))
        krok("B12", b12)

        # ------------------------------------------------------------------ B19 cykl biegu
        def b19():
            from PIL import Image
            v = D["ruch"]["bieg_predkosc"]
            wyniki, zle = {}, []
            for gra, klucz in list(D["klasy_gracza"].items()) + [(D["klasy"][klasa]["klasaGry"], klasa)]:
                Bg = D["klasy"][klucz]["bieg"]
                f, pod = L.kadencja(Bg, v)
                sp.luau(KOD["zmien_klase"] % gra)
                time.sleep(0.7)
                bohater_gotowy(klucz)
                if klucz in wyniki:
                    break                                   # ostatni obrót pętli tylko przywraca klasę gracza
                na_start()
                p = postac()
                poz, przod, prawo = p["poz"], p["przod"], p["prawo"]
                ruch('"klip", "bieg"')
                time.sleep(0.5)
                # (a) zatrzymane fazy podporu lewej nogi: bohater przesunięty o drogę postaci → lewa stopa w tym samym miejscu
                miejsca = []
                for j in range(6):
                    faza = pod * j / 5.0 * 0.999
                    js(KOD["klient"] % ('"faza_biegu", %.6f' % faza))
                    ruch('"przesun", Vector3.new(0, 0, %.5f)' % (-v * faza / f))
                    time.sleep(0.25)
                    js(KOD["klient"] % '"nagraj", 0.15')
                    time.sleep(0.3)
                    kl = slownik(js(KOD["klient"] % '"nagranie"')).get("klatki") or []
                    if kl:
                        miejsca.append((kl[-1][6], kl[-1][7], kl[-1][8]))
                dryf_a = max((math.hypot(m[0] - miejsca[0][0], m[2] - miejsca[0][2]) for m in miejsca), default=99.0)
                wys_a = (max(m[1] for m in miejsca) - min(m[1] for m in miejsca)) if miejsca else 99.0
                # arkusz: osiem kolejnych klatek cyklu, kamera z boku nieruchoma w świecie
                droga = v / f
                if not bez_zrzutow:
                    srodek = (poz[0] + przod[0] * droga / 2, poz[1] - 0.3, poz[2] + przod[2] * droga / 2)
                    bok = 9.5 * max(1.0, droga / 6.0)          # dłuższy cykl = kamera dalej (cała droga w kadrze)
                    oko = (srodek[0] + prawo[0] * bok, poz[1] + 0.1, srodek[2] + prawo[2] * bok)
                    kafle = []
                    for i in range(8):
                        faza = i / 8.0
                        js(KOD["klient"] % ('"faza_biegu", %.6f' % faza))
                        ruch('"przesun", Vector3.new(0, 0, %.5f)' % (-v * faza / f))
                        time.sleep(0.3)
                        try:
                            o = obraz(oko, srodek)
                            w, h = o.size
                            kafle.append(o.crop((int(w * 0.27), int(h * 0.22), int(w * 0.73), int(h * 0.78))))
                        except Exception as ex:  # noqa: BLE001
                            log("arkusz %s klatka %d: %s" % (klucz, i, str(ex)[:160]))
                    if len(kafle) == 8:
                        kw, kh = kafle[0].size
                        arkusz = Image.new("RGB", (kw * 4, kh * 2))
                        for i, kafel in enumerate(kafle):
                            arkusz.paste(kafel, ((i % 4) * kw, (i // 4) * kh))
                        arkusz.thumbnail((2400, 2400))
                        arkusz.save(os.path.join(KLATKI, "20_bieg_%s_pasek.jpg" % klucz), quality=85)
                        log("zrzut 20_bieg_%s_pasek" % klucz)
                    # kadry dodatkowe (klatka cyklu zatrzymana haczykiem, bieg w miejscu): szata kota w ruchu i Rycerz
                    # w zakręcie — przechył tułowia ustawiony haczykiem próby; prawdziwy zakręt mierzy B20
                    ruch('"przesun", nil')
                    for kto, plik, faza, skret, dal, bok in (("mag", "21_kot_szata_w_biegu", 0.30, None, 5.0, 4.5),
                                                             ("wojownik", "22_zakret_wojownik", 0.55, -1, 8.0, 1.5)):
                        if klucz != kto:
                            continue
                        js(KOD["klient"] % ('"faza_biegu", %.2f' % faza))
                        if skret is not None:
                            js(KOD["klient"] % ('"skret", %d' % skret))
                        time.sleep(0.5)
                        try:
                            oko, cel = ujecie(dal=dal, bok=bok, wys=1.0)
                            o = obraz(oko, cel)
                            w, h = o.size
                            o = o.crop((int(w * 0.25), int(h * 0.18), int(w * 0.75), int(h * 0.92)))
                            o.save(os.path.join(KLATKI, plik + ".jpg"), quality=86)
                            log("zrzut", plik)
                        except Exception as ex:  # noqa: BLE001
                            log("zrzut %s: %s" % (plik, str(ex)[:160]))
                        js(KOD["klient"] % '"skret", nil')
                js(KOD["klient"] % '"faza_biegu", nil')
                ruch('"przesun", nil')
                ruch('"klip", nil')
                # (b) prawdziwy bieg: nagranie klatka po klatce w czasie klawisza W
                na_start()
                js(KOD["klient"] % '"nagraj", 2.6')
                time.sleep(0.2)
                klawisz_w(1500)
                time.sleep(1.2)
                kl = slownik(js(KOD["klient"] % '"nagranie"')).get("klatki") or []
                rowne = [k for k in kl if k[1] == "bieg" and k[2] >= 0.999 and k[5] >= 0.95 * v]     # pełna prędkość
                dryf_b, podpory, klatek = dryf_stop(rowne)
                wyniki[klucz] = {"kadencja": f, "podpor": pod, "droga_na_cykl": droga, "dryf_fazy_zatrzymane": dryf_a,
                                 "wysokosc_stopy_w_podporze": wys_a, "miejsca": miejsca, "klatek_nagrania": len(kl),
                                 "klatek_biegu": len(rowne), "dryf_w_biegu": dryf_b, "podporow": podpory, "klatek_w_podporze": klatek}
                if not (len(miejsca) == 6 and dryf_a <= 0.06 and wys_a <= 0.05 and podpory >= 3 and dryf_b <= 0.5):
                    zle.append(klucz)
            na_start()
            zapisz("B19", wyniki)
            punkt("B19", not zle, "stopa w podporze przy %g st/s — %s%s"
                  % (v, "; ".join("%s: kadencja %.2f cyklu/s, podpór %.0f%% cyklu, w zatrzymanych fazach przesunięcie %.3f st "
                                  "(w pionie %.3f), w prawdziwym biegu najwyżej %.2f st na podpór (%d podporów, %d klatek)"
                                  % (k, w["kadencja"], 100 * w["podpor"], w["dryf_fazy_zatrzymane"], w["wysokosc_stopy_w_podporze"],
                                     w["dryf_w_biegu"], w["podporow"], w["klatek_w_podporze"]) for k, w in wyniki.items()),
                     "; ZŁE: %s" % zle if zle else ""))
        krok("B19", b19)

        # ------------------------------------------------------------------ B17 wielu bohaterów
        def b17():
            na_start()
            W = D["widocznosc"]
            sp.luau(J + KOD["klient"] % '"pomiar", "zeruj"')
            time.sleep(3.0)
            jeden = slownik(js(KOD["klient"] % '"pomiar", "zeruj"'))
            fps1 = float(sp.luau(KOD["fps"] % 2.0))
            wlacz(False)
            czekaj(lambda: not lokalny().get("aktywny"), 5)
            fps0 = float(sp.luau(KOD["fps"] % 2.0))
            wlacz(True)
            bohater_gotowy(klasa)
            blisko = [8 + 5 * i for i in range(8)]                                   # 8–43 st: animacja co klatkę
            srednio = [W["promien_pelnej_animacji"] + 25 + 15 * i for i in range(3)]  # dalej: animacja co kilka klatek
            daleko = [W["promien"] * W["histereza"] + 40, W["promien"] * W["histereza"] + 80]   # poza zasięgiem
            n = int(sp.luau(J + KOD["manekiny"] % ", ".join("%g" % x for x in blisko + srednio + daleko)).strip() or 0)
            czekaj(lambda: klient().get("bohaterow", 0) >= 1 + len(blisko) + len(srednio), 15)
            time.sleep(1.0)
            sp.luau(J + KOD["klient"] % '"pomiar", "zeruj"')
            time.sleep(4.0)
            wielu = slownik(js(KOD["klient"] % '"pomiar", "zeruj"'))
            fps12 = float(sp.luau(KOD["fps"] % 2.0))
            st = klient()
            inni = st.get("inni") or []
            okresy = sorted({x.get("okres") for x in inni})
            # koszt cyklu biegu: wszyscy bohaterowie biegną w miejscu — poły stroju włączone, potem wyłączone
            bieg_ms = {}
            js(KOD["klient"] % '"manekiny_bieg", true')
            ruch('"klip", "bieg"')
            for nazwa, arg in (("z_polami", "true"), ("bez_pol", "false"), ("z_polami_2", "true")):
                js(KOD["klient"] % ('"poly", %s' % arg))
                time.sleep(0.6)
                sp.luau(J + KOD["klient"] % '"pomiar", "zeruj"')
                time.sleep(3.0)
                bieg_ms[nazwa] = slownik(js(KOD["klient"] % '"pomiar", "zeruj"'))
            bieg_ms["fps"] = float(sp.luau(KOD["fps"] % 2.0))
            js(KOD["klient"] % '"manekiny_bieg", false')
            ruch('"klip", nil')
            oko, cel = ujecie(dal=30.0, bok=14.0, wys=12.0)
            if oko:
                zrzut("11_wielu_bohaterow", oko, cel)
            sp.luau(KOD["manekiny_usun"])
            po = czekaj(lambda: (lambda x: x if x.get("bohaterow") == 1 else None)(klient()), 8) or {}
            sp.luau(J + KOD["klient"] % '"pomiar", "zeruj"')
            ruch('"klip", "bieg"')
            for nazwa, arg in (("jeden_z_polami", "true"), ("jeden_bez_pol", "false")):
                js(KOD["klient"] % ('"poly", %s' % arg))
                time.sleep(0.6)
                sp.luau(J + KOD["klient"] % '"pomiar", "zeruj"')
                time.sleep(2.5)
                bieg_ms[nazwa] = slownik(js(KOD["klient"] % '"pomiar", "zeruj"'))
            js(KOD["klient"] % '"poly", true')
            ruch('"klip", nil')
            zapisz("B17", {"bieg": bieg_ms, "jeden": jeden, "fps_bez": fps0, "fps_1": fps1, "wielu": wielu, "fps_wielu": fps12, "postaci_testowych": n,
                           "bohaterow": st.get("bohaterow"), "bryl": st.get("bryl"), "inni": inni, "po": po.get("bohaterow")})
            ile = 1 + len(blisko) + len(srednio)
            dobrze = (n == len(blisko) + len(srednio) + len(daleko) and st.get("bohaterow") == ile and ile <= W["maks_bohaterow"]
                      and okresy == [1, W["okres_daleko"]] and po.get("bohaterow") == 1 and (wielu.get("bledy") or 0) == 0)
            wolno = (wielu.get("srednia_ms") or 99) > 6.0
            punkt("B17", (None if wolno else True) if dobrze else False,
                  "bez bohatera %.0f kl./s; 1 bohater: pętla %.2f ms średnio (najwięcej %.2f), %.0f kl./s; %s bohaterów (%s brył; %d "
                  "postaci testowych, 2 poza zasięgiem bez bohatera): pętla %.2f ms średnio (najwięcej %.2f), %.0f kl./s; okresy "
                  "animacji %s; po sprzątaniu bohaterów %s%s; BIEG w miejscu: wszyscy z połami %.2f ms (najwięcej %.2f), bez pół "
                  "%.2f ms, znów z połami %.2f ms, %.0f kl./s; jeden bohater w biegu: z połami %.3f ms, bez %.3f ms"
                  % (fps0, jeden.get("srednia_ms") or -1, jeden.get("maks_ms") or -1, fps1, st.get("bohaterow"), st.get("bryl"), n,
                     wielu.get("srednia_ms") or -1, wielu.get("maks_ms") or -1, fps12, okresy, po.get("bohaterow"),
                     " — UWAGA: pętla wolniejsza niż 6 ms" if wolno and dobrze else "",
                     bieg_ms["z_polami"].get("srednia_ms") or -1, bieg_ms["z_polami"].get("maks_ms") or -1,
                     bieg_ms["bez_pol"].get("srednia_ms") or -1, bieg_ms["z_polami_2"].get("srednia_ms") or -1, bieg_ms["fps"],
                     bieg_ms["jeden_z_polami"].get("srednia_ms") or -1, bieg_ms["jeden_bez_pol"].get("srednia_ms") or -1))
        krok("B17", b17)

        # ------------------------------------------------------------------ B20 bieg w przeszkodę
        def b20():
            v = D["ruch"]["bieg_predkosc"]
            na_start()
            p = postac()
            poz, przod = p["poz"], p["przod"]
            dal = 12.0
            sp.luau(KOD["sciana"] % (poz[0] + przod[0] * dal, poz[1] + 2.0, poz[2] + przod[2] * dal, poz[0], poz[1] + 2.0, poz[2]))
            time.sleep(0.3)
            js(KOD["klient"] % '"nagraj", 4.0')
            time.sleep(0.2)
            klawisz_w(2200)                                  # ok. 0,5 s biegu do ściany, potem klawisz dalej wciśnięty
            koniec_w = lokalny()
            time.sleep(1.0)
            kl = slownik(js(KOD["klient"] % '"nagranie"')).get("klatki") or []
            sp.luau(KOD["manekiny_usun"])
            na_start()
            # chwila uderzenia: postać przestaje iść naprzód (HumanoidRootPart stoi przez 6 kolejnych klatek)
            droga = [math.hypot(b[12] - a[12], b[14] - a[14]) for a, b in zip(kl, kl[1:])]
            ruszyl = next((i for i, x in enumerate(droga) if x > 0.15), None)
            stanal = None
            if ruszyl is not None:
                stanal = next((i for i in range(ruszyl + 5, len(droga) - 6) if sum(droga[i:i + 6]) < 0.05), None)
            przebyl = math.hypot(kl[-1][12] - kl[0][12], kl[-1][14] - kl[0][14]) if kl else 0.0
            dryf, podpory, klatek = dryf_stop(kl)            # cały bieg, razem z podporem, w którym postać trafiła w ścianę
            t_idle, slizg_idle = None, 0.0
            if stanal is not None:
                idle = [i for i in range(stanal, len(kl)) if kl[i][1] == "idle" and kl[i][2] <= 0.001]
                if idle:
                    t_idle = kl[idle[0]][0] - kl[stanal][0]
                    # po przejściu klipów (0,35 s) do puszczenia klawisza stopy mają stać
                    stoi = [i for i in idle if 0.35 <= kl[i][0] - kl[idle[0]][0] <= 0.9]
                    for i in stoi:
                        a = kl[stoi[0]]
                        slizg_idle = max(slizg_idle, math.hypot(kl[i][6] - a[6], kl[i][8] - a[8]),
                                         math.hypot(kl[i][9] - a[9], kl[i][11] - a[11]))
            # zakręt: W i strzałka w prawo (kamera się obraca, postać skręca) — tułów przechyla się do środka zakrętu
            sp.luau(J + KOD["skret_slad"] % 2.4)
            sp.call("user_keyboard_input", {"datamodel_type": "Client", "actions": [
                {"action": "keyDown", "key_code": "W"}, {"action": "keyDown", "key_code": "Right"},
                {"action": "wait", "wait_time_ms": 1600}, {"action": "keyUp", "key_code": "Right"}, {"action": "keyUp", "key_code": "W"}]})
            zakret = czekaj(lambda: json.loads(sp.luau(J + KOD["skret_czytaj"])), 8, 0.4) or {}
            na_start()
            tryby = [k[1] for k in kl]
            kolejnosc = [t for i, t in enumerate(tryby) if i == 0 or t != tryby[i - 1]]
            zmian_po = len([1 for i in range((stanal or 0) + 1, len(tryby)) if tryby[i] != tryby[i - 1]])
            zapisz("B20", {"klatek": len(kl), "ruszyl": ruszyl, "stanal": stanal, "przebyl": przebyl, "dryf": dryf, "podpory": podpory,
                           "klatek_w_podporze": klatek, "t_idle": t_idle, "slizg_idle": slizg_idle, "zmian_trybu_po_zatrzymaniu": zmian_po, "zakret": zakret, "kolejnosc": kolejnosc[:20],
                           "koniec_w": koniec_w.get("tryb"),
                           "slad": [[round(x, 3) if isinstance(x, float) else x for x in k] for k in kl]})
            punkt("B20", stanal is not None and 5.0 <= przebyl <= dal and podpory >= 2 and dryf <= 0.12
                  and t_idle is not None and t_idle <= 0.7 and slizg_idle <= 0.05 and zmian_po <= 3 and koniec_w.get("tryb") == "idle" and (zakret.get("mn") or 0) < -0.25 and (zakret.get("mx") or 0) < 0.25,
                  "bieg %g st/s w ścianę po %.1f st, klawisz W wciśnięty 2,2 s: %s; stopa w podporze najwyżej %.3f st (%d podporów, "
                  "%d klatek, razem z podporem uderzenia); spoczynek %s po zatrzymaniu postaci, w spoczynku stopy przesunięte "
                  "najwyżej %.3f st, zmian trybu po zatrzymaniu %d; pod koniec klawisza tryb %s; zakręt w prawo (W + strzałka): przechył tułowia od %.2f "
                  "do %.2f (−1 = pełny w prawo)"
                  % (v, przebyl, " → ".join(kolejnosc[:12]), dryf, podpory, klatek,
                     ("%.2f s" % t_idle) if t_idle is not None else "nie nastąpił", slizg_idle, zmian_po, koniec_w.get("tryb"),
                     zakret.get("mn") or 0, zakret.get("mx") or 0))
        krok("B20", b20)

        # ------------------------------------------------------------------ B13 pet za bohaterem
        def b13():
            if not e.get("pety") or not e.get("stan"):
                punkt("B13", None, "PetyProba albo StanGracza nie ma w miejscu — pominięte")
                return
            na_start()
            if not atrybut("PetAktywny"):
                js(KOD["pet_kup"], "Server")
            pet = czekaj(lambda: atrybut("PetAktywny"), 12)
            sp.luau(KOD["pet_kamera"] % "true")
            czekaj(lambda: (lambda x: x if x.get("mojPet") and not x.get("wylegaSie") else None)(slownik(js(KOD["pet_klient"]))),
                   25, 0.6)
            na_start()
            probki = slad(4.2, lambda: (time.sleep(0.5), klawisz_w(1300), time.sleep(2.0)))
            odl = [x["pet"] for x in probki if isinstance(x.get("pet"), (int, float))]
            tryby = [x.get("tryb") for x in probki]
            kon = slownik(js(KOD["pet_klient"]))
            l = lokalny()
            zrzut_postaci("05_obok_peta", dal=10.0, bok=5.0, wys=3.0)
            sp.luau(KOD["pet_kamera"] % "nil")
            zapisz("B13", {"pet": pet, "klient_petow": kon, "odleglosci": odl, "tryby_bohatera": tryby, "lokalny": l})
            punkt("B13", bool(pet) and kon.get("mojPet") == pet and bool(odl) and max(odl) <= 14 and "bieg" in tryby
                  and isinstance(kon.get("odleglosc"), (int, float)) and kon["odleglosc"] <= 7 and bool(l.get("aktywny")),
                  "pet %s idzie za graczem-bohaterem: odległość w biegu do %.1f st, po zatrzymaniu %.1f st; bohater: %s"
                  % (pet, max(odl or [0]), kon.get("odleglosc") or -1, sorted({t for t in tryby if t})))
        krok("B13", b13)

        # ------------------------------------------------------------------ B14 walka w lesie-pasie
        def b14():
            if not e.get("pas"):
                punkt("B14", None, "LasPasGra nie ma w miejscu — pominięte")
                return
            sp.luau(KOD["test_bohater"] % ("LasPasGra", "false"), "Server")
            pot = slownik(js(KOD["potwor"] % "s1", "Server"))
            if not pot.get("id"):
                punkt("B14", None, "brak wolnego potwora w strefie s1 — pominięte")
                return
            p = pot["p"]
            sp.luau(KOD["przestaw"] % (p[0] - 22.0, p[1] + 3.2, p[2], p[0], p[2]), "Server")
            time.sleep(2.5)
            stan0["w_lesie"] = True
            sp.luau(KOD["bez_nazwy"])
            # pierwsze wejście do lasu-pasa: kamera leci nad pasem, postać stoi zablokowana (bez walk i bez ruchu)
            przelot = czekaj(lambda: sp.luau(KOD["przelot"]).strip() == "false", 60, 1.0)
            time.sleep(1.0)
            sp.luau(KOD["kamera_za"] % (12.0, 5.0))
            time.sleep(0.5)
            przed = bohater_gotowy(klasa)
            # bieg w lesie (prawdziwy W) i zrzut z boku w biegu: drugi W w tle nie jest możliwy, więc zrzut tuż po biegu
            probki = slad(2.6, lambda: (time.sleep(0.3), klawisz_w(900), time.sleep(1.0)))
            w_lesie = [x.get("tryb") for x in probki]
            ruch('"klip", "bieg"')
            time.sleep(0.5)
            zrzut_postaci("03_las_bieg", dal=7.0, bok=7.0, wys=1.5)
            ruch('"klip", nil')
            # walka: świeże miejsce potwora (potwory chodzą), postać tuż obok, walka jak po E
            gdzie = slownik(js(KOD["potwor_gdzie"] % pot["id"], "Server"))
            if isinstance(gdzie.get("p"), list):
                p = gdzie["p"]
            sp.luau(KOD["przestaw"] % (p[0] - 4.0, p[1] + 3.2, p[2], p[0], p[2]), "Server")
            time.sleep(1.0)
            odp = sp.luau(KOD["walcz"] % pot["id"]).strip()
            faza = czekaj(lambda: slownik(js(KOD["odtw"] % '"stan"')).get("faza") == "odtwarzanie", 15, 0.4)
            time.sleep(1.2)
            w_walce, aw = lokalny(), awatar()
            aktor = slownik(js(KOD["aktor_walki"] % klasa))
            pk = slownik(js(KOD["potwory_klient"]))
            zrzut("12_walka_w_lesie")
            if faza:
                js(KOD["odtw"] % '"przewinDo", 1000')
                time.sleep(2.5)
                js(KOD["odtw"] % '"zamknij"')
                czekaj(lambda: not slownik(js(KOD["potwory_klient"])).get("walka"), 30, 1.0)
                time.sleep(2.0)
            po = czekaj(lambda: (lambda l: l if l.get("aktywny") and (l.get("ltm") or 0) < 0.01 else None)(lokalny()), 10) or {}
            a_po = awatar()
            zrzut_postaci("12_po_walce")
            zapisz("B14", {"przelot_skonczony": bool(przelot), "przed": przed, "tryby_w_lesie": w_lesie, "walcz": odp, "klient_potworow": pk, "faza": faza,
                           "w_walce": w_walce, "awatar_w_walce": aw, "aktor": aktor, "po": po, "awatar_po": a_po})
            ten_sam = aktor.get("jest") and aktor.get("bryly") == przed.get("bryly") and (
                aktor.get("stroj") in (False, None) or aktor.get("stroj") == przed.get("stroj"))
            punkt("B14", bool(faza) and (w_walce.get("ltm") or 0) >= 0.99 and bool(ten_sam) and bool(po.get("aktywny"))
                  and a_po.get("widoczne") == 0 and a_po.get("ltmGlowy") == 0 and "bieg" in w_lesie,
                  "bieg w lesie: %s; walka: start %s%s; w walce bohater świata schowany (przezroczystość %.2f), aktor walki %s brył / "
                  "strój %r (bohater świata %s / %r); po walce bohater wraca (tryb %s, przezroczystość %.2f), awatar dalej "
                  "niewidoczny (%s)"
                  % (sorted({t for t in w_lesie if t}), odp, "" if faza else " — NIE RUSZYŁA (odmowa %r)" % pk.get("odmowa"),
                     w_walce.get("ltm") or 0, aktor.get("bryly"), aktor.get("stroj"), przed.get("bryly"), przed.get("stroj"),
                     po.get("tryb"), po.get("ltm") or 0, a_po.get("widoczne")))
        krok("B14", b14)

        # ------------------------------------------------------------------ B15 teleport przez chmury
        def b15():
            if not e.get("chmury"):
                punkt("B15", None, "TeleportChmury nie ma w miejscu — pominięte")
                return
            p0 = postac()["poz"]
            # z lasu (po B14) wracamy do miasteczka; gdy walki w lesie nie było — z miasteczka do lasu
            kraina = "miasteczko" if stan0.get("w_lesie") else "las"
            js(KOD["chmury_serwer"] % kraina, "Server")
            otw = slownik(js(KOD["chmury_klient"] % '"otworz"'))
            wyb = czekaj(lambda: (lambda x: x if x.get("ok") else None)(
                slownik(js(KOD["chmury_klient"] % ('"wybierz", "%s"' % kraina)))), 20, 0.7) or {}
            w_trakcie = lokalny()
            czekaj(lambda: not slownik(js(KOD["chmury_klient"] % '"stan"')).get("trwa"), 60, 1.0)
            time.sleep(2.0)
            sp.luau(KOD["bez_nazwy"])
            p1 = postac()
            l = bohater_gotowy(klasa)
            stopy = l.get("stopyNadZiemia")
            zrzut_postaci("13_po_teleporcie")
            zapisz("B15", {"kraina": kraina, "otworz": otw, "wybierz": wyb, "w_trakcie": w_trakcie, "przed": p0, "po": p1, "lokalny": l})
            droga = math.dist(p0, p1["poz"]) if not p1.get("brak") else 0
            punkt("B15", bool(wyb.get("ok")) and droga > 50 and bool(l.get("aktywny")) and (l.get("odPostaci") or 9) <= 0.35
                  and isinstance(stopy, (int, float)) and abs(stopy) <= 0.15 and p1.get("kamera") == "Custom",
                  "przejście do krainy „%s”: wybór %s, postać przeniesiona o %.0f st, bohater przy postaci (%.2f st), stopy %.3f st nad "
                  "ziemią, kamera %s" % (kraina, wyb.get("ok"), droga, l.get("odPostaci") or 9,
                                         stopy if isinstance(stopy, (int, float)) else 99, p1.get("kamera")))
        krok("B15", b15)

        # ------------------------------------------------------------------ B16 runda Training Center
        def b16():
            if not e.get("trening"):
                punkt("B16", None, "TreningProba nie ma w miejscu — pominięte")
                return
            pt = slownik(js(KOD["trening_punkt"], "Server")).get("p")
            if not isinstance(pt, list):
                punkt("B16", None, "TreningProba nie ma atrybutu PunktTablicy — pominięte")
                return
            # postać staje przy tablicy (serwer wpuszcza do rundy tylko z bliska)
            sp.luau(KOD["przestaw"] % (pt[0] + 5.0, pt[1] + 3.2, pt[2] + 2.0, pt[0], pt[2]), "Server")
            time.sleep(1.5)
            przed = slownik(js(KOD["trening_stan"], "Server"))
            odp = sp.luau(KOD["trening_start"] % "sila").strip()
            gra = czekaj(lambda: slownik(js(KOD["trening_stan"], "Server")).get("gra"), 15, 0.5)
            if not gra:
                punkt("B16", None, "runda nie ruszyła (odpowiedź %r, serwer odmówił: %s) — pominięte"
                      % (odp, slownik(js(KOD["trening_stan"], "Server")).get("odmowa")))
                return
            proby = []
            t1 = time.time()
            while time.time() - t1 < 8.0:
                proby.append({"ruch": ruch('"stan"'), "tryb": lokalny().get("tryb")})
                time.sleep(0.8)
            zrzut_postaci("14_trening", dal=10.0, bok=4.0, wys=3.0)
            # rundy nikt tu nie gra (klawisze mini-gry naciska próba dymna całej gry) — czekamy krótko, czy skończy się sama
            koniec = czekaj(lambda: not slownik(js(KOD["trening_stan"], "Server")).get("gra"), 25, 1.5)
            time.sleep(2.0)
            l, st, a = lokalny(), klient(), awatar()
            konsola = [x for x in sp.konsola().splitlines() if "[BohaterSwiat]" in x]
            zapisz("B16", {"przed": przed, "odpowiedz": odp, "gra": gra, "proby": proby, "koniec": bool(koniec), "lokalny": l,
                           "ruch": st.get("ruch"), "awatar": a, "wierszy_konsoli": len(konsola)})
            klipy = sorted({(x["ruch"] or {}).get("klip") or "?" for x in proby if isinstance(x["ruch"], dict)})
            ruch_po = slownik(st.get("ruch"))
            dobrze = (not konsola and bool(l.get("aktywny")) and not ruch_po.get("klip") and not ruch_po.get("przesun")
                      and a.get("widoczne") == 0)
            punkt("B16", (dobrze if koniec else None), "runda „%s” (odpowiedź %r): w rundzie klipy bohatera %s; %s; po rundzie bohater "
                  "%s w trybie %s, wymuszony klip %r, przesunięcie %r; wierszy [BohaterSwiat] w konsoli %d"
                  % (gra, odp, klipy, "runda skończona" if koniec else "runda trwa dalej (nikt w nią nie gra; całą rundę przechodzi próba dymna gry)", l.get("klasa"), l.get("tryb"),
                     ruch_po.get("klip"), ruch_po.get("przesun"), len(konsola)))
        krok("B16", b16)

        # ------------------------------------------------------------------ B18 konsola
        def b18():
            k = sp.konsola()
            with open(os.path.join(wyj, "konsola.txt"), "w", encoding="utf-8") as f:
                f.write(k)
            nasze = [x for x in k.splitlines() if "[BohaterSwiat]" in x or ("BohaterSwiat" in x and "error" in x.lower())]
            st = klient()
            bledy = slownik(st.get("klatka")).get("bledy")
            zapisz("B18", {"wiersze": nasze[:20], "bledy_petli": bledy})
            punkt("B18", not nasze and bledy == 0, "konsola: %d wierszy [BohaterSwiat]%s; błędów w pętli klienta: %s"
                  % (len(nasze), (": " + nasze[0][:200]) if nasze else "", bledy))
        krok("B18", b18)

    zle = [x for x in LISTA if x[1] == "BŁĄD"]
    log("WYNIK: %d × OK, %d × ?, %d × BŁĄD (lista: lista.txt w folderze wyników); Studio w trybie Edit: %s"
        % (sum(x[1] == "OK" for x in LISTA), sum(x[1] == "?" for x in LISTA), len(zle), getattr(sp, "edit_po", "?")))
    return 1 if zle else 0


if __name__ == "__main__":
    sys.exit(main())
