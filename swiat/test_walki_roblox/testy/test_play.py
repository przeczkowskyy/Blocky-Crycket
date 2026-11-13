#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test cutscenki w trybie Play (Roblox Studio przez tools/studio_mcp.py). Na końcu ZAWSZE wraca do trybu Edit.

    python -B swiat/test_walki_roblox/testy/test_play.py [--studio <studio_id>] [--zrzuty <folder>] [--pomiary 3]

Wymaga zbudowanego kontenera (zbuduj.py) i Studio w trybie Edit. W jednej sesji Play sprawdza:
  1. wejście przez ProximityPrompt: nawigacja postaci do tablicy przy arenie + klawisz E → cutscenka startuje;
  2. przycisk „POMIŃ” kliknięty myszą → od razu panel wyniku, a „JESZCZE RAZ” jest zablokowane z odliczaniem
     (serwer nie uznał jeszcze walki za skończoną); kliknięcie w trakcie blokady nic nie robi;
  3. „JESZCZE RAZ” po odliczaniu → nowa walka; „ZAMKNIJ” → kamera, GUI, lista graczy, czat, podpowiedź i sterowanie wracają;
  4. reset postaci (Health = 0 po stronie serwera) w trakcie walki → wszystko lokalne posprzątane, po odrodzeniu sterowanie działa;
  5. bezpieczeństwo: liczby od klienta ignorowane; druga prośba w 1 s → „za_szybko”; prośba w trakcie walki → „walka_trwa”;
     prośba z daleka od tablicy → „za_daleko”;
  6. pomiary: N pełnych odtworzeń w normalnym tempie (czas trwania, czas klatki, koszt skryptu, liczba instancji);
  8. obcy w kadrze: manekin R15, część dodana w trakcie walki i część z tagiem (CanQuery = false) na arenie oraz własna
     postać są lokalnie schowane w trakcie walki i widoczne po niej;
  9. symulacja publikacji: kopia SerwerWalki z IsStudio() = false usuwa swój kontener (u serwera i u klienta);
  7. konsola: żadnych ostrzeżeń ani błędów z „[TestWalki]”.
Zmienia wyłącznie stan sesji Play (znika po jej zatrzymaniu). Kod wyjścia 0 = wszystko zaliczone.
"""
import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TU)))
sys.path.insert(0, os.path.join(REPO, "tools"))
from studio_mcp import StudioMCP, StudioError  # noqa: E402
sys.path.insert(0, os.path.dirname(TU))
from cel_studio import wybierz_studio  # noqa: E402

TABLICA = (163.7, -9.5)  # x, z tablicy z podpowiedzią (zachodni skraj areny)
PRZED_TABLICA = {"x": 158.0, "y": 3.0, "z": -9.5}
SCIEZKA_GUI = "LocalPlayer.PlayerGui.TestWalkiCutscenka.Kadr."

STAN = r'''
local HttpService = game:GetService("HttpService")
local CAS = game:GetService("ContextActionService")
local SG = game:GetService("StarterGui")
local gracz = game:GetService("Players").LocalPlayer
local k = workspace:FindFirstChild("TestWalki")
local t = {}
if k then for n, v in k:GetAttributes() do t[n] = v end end
local kam = workspace.CurrentCamera
t._kamera = kam.CameraType.Name
local hum = gracz.Character and gracz.Character:FindFirstChildOfClass("Humanoid")
t._podmiotToHumanoid = hum ~= nil and kam.CameraSubject == hum
t._hp = hum and hum.Health or -1
local hrp = gracz.Character and gracz.Character:FindFirstChild("HumanoidRootPart")
t._poz = hrp and { hrp.Position.X, hrp.Position.Y, hrp.Position.Z } or { 0, 0, 0 }
t._guiCutscenki = gracz.PlayerGui:FindFirstChild("TestWalkiCutscenka") ~= nil
t._hud = gracz.PlayerGui:FindFirstChild("HUD") == nil or gracz.PlayerGui.HUD.Enabled
t._scena = k and k:FindFirstChild("ScenaLokalna") ~= nil
t._lista = SG:GetCoreGuiEnabled(Enum.CoreGuiType.PlayerList)
t._czat = SG:GetCoreGuiEnabled(Enum.CoreGuiType.Chat)
t._blokada = next(CAS:GetBoundActionInfo("TestWalkiBlokadaSterowania")) ~= nil
t._pominKlawisz = next(CAS:GetBoundActionInfo("TestWalkiPomin")) ~= nil
local pp = k and k:FindFirstChild("PodpowiedzWalki", true)
t._podpowiedz = pp and pp.Enabled
local r = k and k:FindFirstChild("Aktorzy") and k.Aktorzy:FindFirstChild("Rycerz")
t._szablonUkryty = r and r:FindFirstChild("UpperTorso") and r.UpperTorso.LocalTransparencyModifier
local glowa = gracz.Character and gracz.Character:FindFirstChild("Head")
t._postacUkryta = glowa and glowa.LocalTransparencyModifier
local intruz = k and k:FindFirstChild("TestowyIntruz")
local function ltm(o) return o and o:IsA("BasePart") and o.LocalTransparencyModifier or -1 end
t._intruzManekin = intruz and ltm(intruz:FindFirstChild("Manekin") and intruz.Manekin:FindFirstChild("UpperTorso"))
t._intruzPozniej = intruz and ltm(intruz:FindFirstChild("Pozniej"))
t._intruzTag = intruz and ltm(intruz:FindFirstChild("ZTagiem"))
local karta = gracz.PlayerGui:FindFirstChild("TestWalkiCutscenka") and gracz.PlayerGui.TestWalkiCutscenka:FindFirstChild("Wynik", true)
local jeszcze = karta and karta:FindFirstChild("JeszczeRaz", true)
jeszcze = jeszcze and jeszcze:FindFirstChild("Przycisk")
t._jeszczeZablokowany = jeszcze and jeszcze:GetAttribute("Zablokowany")
t._jeszczeTekst = jeszcze and jeszcze:FindFirstChild("Napis") and jeszcze.Napis.Text
t._czasSerwera = workspace:GetServerTimeNow()
return HttpService:JSONEncode(t)
'''

GOTOWOSC = ('local p = game:GetService("Players").LocalPlayer; local k = workspace:FindFirstChild("TestWalki"); '
            'return tostring(p and p.Character ~= nil) .. " " .. tostring(k and k:GetAttribute("KlientGotowy"))')

BEZPIECZENSTWO = r'''
local HttpService = game:GetService("HttpService")
local k = workspace.TestWalki
local rf = k.Zdalne.RozpocznijWalke
task.wait(1.1)
k:SetAttribute("ZiarnoTestowe", 5) -- zmiana po stronie klienta: nie replikuje się, serwer jej nie widzi
local a = rf:InvokeServer(999999, { hp = 1e9, atak = 1e9, zloto = 1e9 }, "wygrana")
local b = rf:InvokeServer()
task.wait(1.1)
local c = rf:InvokeServer()
return HttpService:JSONEncode({
	a_ok = a.ok, a_powod = a.powod, a_ziarno = a.walka and a.walka.ziarno, a_hpGracza = a.walka and a.walka.strony.gracz.hp,
	a_zloto = a.walka and a.walka.lup.zloto, a_zostalo = a.nastepnaOd and (a.nastepnaOd - workspace:GetServerTimeNow()),
	b_ok = b.ok, b_powod = b.powod, c_ok = c.ok, c_powod = c.powod, c_ponowZa = c.ponowZa,
})
'''

ZA_DALEKA = r'''
local HttpService = game:GetService("HttpService")
task.wait(1.1)
local d = workspace.TestWalki.Zdalne.RozpocznijWalke:InvokeServer()
return HttpService:JSONEncode({ d_ok = d.ok, d_powod = d.powod, d_odleglosc = d.odleglosc })
'''

# serwer: postać gracza w dane miejsce (tylko stan sesji Play)
PRZESTAW = ('local p = game:GetService("Players"):GetPlayers()[1] '
            'p.Character:PivotTo(CFrame.lookAt(Vector3.new(%s), Vector3.new(%s))) return "ok"')
PRZY_TABLICY = PRZESTAW % ("158, 4.5, -9.5", "170, 4.5, -9.5")
DALEKO = PRZESTAW % ("128, 4.5, -9.5", "140, 4.5, -9.5")

# serwer: obcy na arenie (wszystko w kontenerze, w trybie Play — znika po zatrzymaniu)
INTRUZ = r'''
local CS = game:GetService("CollectionService")
local k = workspace.TestWalki
local stary = k:FindFirstChild("TestowyIntruz")
if stary then stary:Destroy() end
local f = Instance.new("Folder")
f.Name = "TestowyIntruz"
local m = game:GetService("Players"):CreateHumanoidModelFromDescription(Instance.new("HumanoidDescription"), Enum.HumanoidRigType.R15)
m.Name = "Manekin"
m.HumanoidRootPart.Anchored = true
m:PivotTo(CFrame.lookAt(Vector3.new(191.5, 4.2, -0.5), Vector3.new(160, 4.2, -0.5)))
m.Parent = f
local t = Instance.new("Part")
t.Name = "ZTagiem"
t.Size = Vector3.new(2, 2, 2)
t.Color = Color3.fromRGB(255, 0, 255)
t.Material = Enum.Material.Neon
t.Anchored = true
t.CanCollide = false
t.CanQuery = false -- zapytanie przestrzenne tego nie widzi; chowa go tag
t.CFrame = CFrame.new(186, 6, 2.5)
CS:AddTag(t, "TestWalkiUkryj")
t.Parent = f
f.Parent = k
return "ok"
'''
INTRUZ_POZNIEJ = r'''
local p = Instance.new("Part")
p.Name = "Pozniej"
p.Size = Vector3.new(3, 3, 3)
p.Color = Color3.fromRGB(0, 255, 0)
p.Material = Enum.Material.Neon
p.Anchored = true
p.CanCollide = false
p.CFrame = CFrame.new(188, 5, -6)
p.Parent = workspace.TestWalki.TestowyIntruz
return "ok"
'''

# serwer: kopia SerwerWalki z IsStudio() = false w osobnym folderze kontenera → powinna usunąć swój folder
PUBLIKACJA_1 = r'''
local f = Instance.new("Folder")
f.Name = "ProbaPublikacji"
local slup = Instance.new("Part")
slup.Name = "Slup"
slup.Anchored = true
slup.CanCollide = false
slup.Size = Vector3.new(1, 10, 1)
slup.CFrame = CFrame.new(156, 5, -16)
slup.Parent = f
f.Parent = workspace.TestWalki
return "ok"
'''
PUBLIKACJA_2 = r'''
local f = workspace.TestWalki.ProbaPublikacji
local s = Instance.new("Script")
s.Name = "SerwerWalki"
s.RunContext = Enum.RunContext.Server
s.Source = __ZRODLO__
s.Parent = f
local t0 = os.clock()
while f.Parent and os.clock() - t0 < 5 do task.wait(0.05) end
return if f.Parent then "NADAL JEST" else "USUNIETY"
'''

WYNIKI = []


def log(*a):
    print("[%s]" % time.strftime("%H:%M:%S"), *a, flush=True)


def sprawdz(nazwa, warunek, szczegoly=""):
    WYNIKI.append((nazwa, bool(warunek)))
    log("%-58s %s %s" % (nazwa, "OK" if warunek else "BŁĄD", szczegoly))


class Sesja:
    def __init__(self, s, sid, zrzuty):
        self.s, self.sid, self.zrzuty = s, sid, zrzuty

    def call(self, nazwa, args=None, timeout=None):
        a = dict(args or {})
        a["studio_id"] = self.sid
        return self.s.call(nazwa, a, timeout=timeout)

    def luau(self, kod, dm="Client"):
        r = self.call("execute_luau", {"code": kod, "datamodel_type": dm})
        if r["is_error"]:
            raise StudioError(r["text"][:2000])
        return r["text"]

    def stan(self):
        return json.loads(self.luau(STAN))

    def czekaj(self, stany, limit):
        t0 = time.time()
        s = {}
        while time.time() - t0 < limit:
            s = self.stan()
            if s.get("OstatniStan") in stany:
                return s, time.time() - t0
            time.sleep(0.2)
        return s, time.time() - t0

    def czekaj_wolna(self, limit):
        """Czeka, aż serwer przyjmie następną walkę (wg czasu z ostatniej odpowiedzi). Zwraca, ile s zostało (≤ 0 = wolne)."""
        t0 = time.time()
        zostalo = 0
        while time.time() - t0 < limit:
            s = self.stan()
            zostalo = (s.get("NastepnaWalkaOd") or 0) - s["_czasSerwera"]
            if zostalo <= -0.1:
                break
            time.sleep(0.3)
        return zostalo

    def tryb_edit(self):
        return "Current Studio Mode: Edit" in self.call("get_studio_state")["text"]

    def klik(self, sciezka):
        return self.call("user_mouse_input", {"datamodel_type": "Client", "actions": [
            {"action": "moveTo", "instance_path": SCIEZKA_GUI + sciezka},
            {"action": "mouseButtonClick", "mouse_button": "left"}]})["text"]

    def klawisz_w(self, ms=900):
        p1 = self.stan()["_poz"]
        self.call("user_keyboard_input", {"datamodel_type": "Client", "actions": [
            {"action": "keyDown", "key_code": "W"}, {"action": "wait", "wait_time_ms": ms}, {"action": "keyUp", "key_code": "W"}]})
        time.sleep(0.4)
        p2 = self.stan()["_poz"]
        return ((p2[0] - p1[0]) ** 2 + (p2[2] - p1[2]) ** 2) ** 0.5

    def zrzut(self, nazwa):
        if not self.zrzuty:
            return
        r = self.call("screen_capture", {"capture_id": "ScreenCapture_1"}, timeout=60)
        if r["images"]:
            with open(os.path.join(self.zrzuty, nazwa), "wb") as f:
                f.write(r["images"][0])


def stan_po_walce(nazwa, s):
    sprawdz(nazwa + ": kamera Custom i na postaci", s["_kamera"] == "Custom" and s["_podmiotToHumanoid"])
    sprawdz(nazwa + ": GUI cutscenki i scena lokalna usunięte", not s["_guiCutscenki"] and not s["_scena"])
    sprawdz(nazwa + ": HUD, lista graczy i czat z powrotem", s["_hud"] and s["_lista"] and s["_czat"])
    sprawdz(nazwa + ": blokady klawiszy zdjęte, podpowiedź włączona", not s["_blokada"] and not s["_pominKlawisz"] and s["_podpowiedz"])
    sprawdz(nazwa + ": szablony aktorów znów widoczne", s["_szablonUkryty"] == 0)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Test cutscenki walki w trybie Play")
    ap.add_argument("--studio", default=None, help="studio_id (wymagane, gdy otwartych jest kilka okien Studio)")
    ap.add_argument("--zrzuty", default=None, help="folder na zrzuty ekranu (domyślnie bez zrzutów)")
    ap.add_argument("--pomiary", type=int, default=3, help="ile pełnych odtworzeń zmierzyć")
    ap.add_argument("--ziarno", type=int, default=770)
    a = ap.parse_args()
    if a.zrzuty:
        os.makedirs(a.zrzuty, exist_ok=True)

    with StudioMCP(timeout=180) as s:
        sid = wybierz_studio(s, a.studio)
        t = Sesja(s, sid, a.zrzuty)
        if not t.tryb_edit():
            sys.exit("Studio nie jest w trybie Edit — nie zaczynam.")
        try:
            log("Play:", t.call("start_stop_play", {"is_start": True})["text"][:80])
            for _ in range(100):
                if "Client" in t.call("get_studio_state")["text"]:
                    try:
                        if t.luau(GOTOWOSC).strip() == "true true":
                            break
                    except StudioError:
                        pass  # klient jeszcze się ładuje
                time.sleep(0.5)
            time.sleep(2.0)
            t.luau('workspace.TestWalki:SetAttribute("ZiarnoTestowe", %d) return "ok"' % a.ziarno, "Server")

            # 1. ProximityPrompt
            t.call("character_navigation", {"datamodel_type": "Client", "instance_path": "game.Workspace.TestWalki.Arena.Tablica.Deska",
                                            "speed_multiplier": 3.0}, timeout=120)
            for _ in range(4):  # nawigacja na długim dystansie bywa zawodna — dojdź przed tablicę
                p = t.stan()["_poz"]
                if (p[0] - TABLICA[0]) ** 2 + (p[2] - TABLICA[1]) ** 2 < 64:
                    break
                t.call("character_navigation", dict(PRZED_TABLICA, datamodel_type="Client", speed_multiplier=3.0), timeout=120)
                time.sleep(0.8)
            t.zrzut("01_przy_tablicy.png")
            t.call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": "E"}]})
            s1, dt = t.czekaj(("odtwarzanie",), 10)
            sprawdz("1. ProximityPrompt + E uruchamia cutscenkę", s1.get("OstatniStan") == "odtwarzanie", "(%.2f s)" % dt)
            time.sleep(1.6)
            t.zrzut("02_cutscenka.png")

            # 2. POMIŃ (+ blokada „JESZCZE RAZ”, bo serwer nie uznał jeszcze walki za skończoną)
            t.klik("Pomin.Przycisk")
            s2, dt = t.czekaj(("wynik",), 6)
            sprawdz("2. POMIŃ → panel wyniku", s2.get("OstatniStan") == "wynik" and s2.get("OstatnioPominieto") is True,
                    "(%.2f s, cutscenka trwała %s s)" % (dt, s2.get("OstatniCzasTrwania")))
            time.sleep(1.0)
            t.zrzut("03_po_pomin.png")
            s2 = t.stan()
            sprawdz("2b. po POMIŃ „JESZCZE RAZ” zablokowane z odliczaniem", s2.get("_jeszczeZablokowany") is True
                    and str(s2.get("_jeszczeTekst", "")).startswith("ZA "), "(%s)" % s2.get("_jeszczeTekst"))
            t.klik("Wynik.Karta.JeszczeRaz.Przycisk")
            time.sleep(0.6)
            sprawdz("2c. klik w trakcie blokady nic nie robi", t.stan().get("OstatniStan") == "wynik")

            # 3. JESZCZE RAZ, ZAMKNIJ, sterowanie
            zostalo = t.czekaj_wolna(15)
            time.sleep(0.3)
            s3 = t.stan()
            sprawdz("3-. blokada zdjęta po czasie walki", zostalo <= 0 and s3.get("_jeszczeZablokowany") is False,
                    "(%s)" % s3.get("_jeszczeTekst"))
            t.klik("Wynik.Karta.JeszczeRaz.Przycisk")
            s3, _ = t.czekaj(("odtwarzanie",), 8)
            sprawdz("3a. JESZCZE RAZ → nowa walka", s3.get("OstatniStan") == "odtwarzanie")
            s3, dt = t.czekaj(("wynik",), 15)
            sprawdz("3b. druga walka dobiega do wyniku", s3.get("OstatniStan") == "wynik", "(%.1f s)" % dt)
            time.sleep(1.0)
            sprawdz("3b'. po pełnej walce „JESZCZE RAZ” od razu dostępne", t.stan().get("_jeszczeZablokowany") is False)
            t.klik("Wynik.Karta.Zamknij.Przycisk")
            t.czekaj(("zamknieto",), 5)
            time.sleep(0.8)
            stan_po_walce("3c. po ZAMKNIJ", t.stan())
            droga = t.klawisz_w()
            sprawdz("3d. po ZAMKNIJ postać chodzi (W przez 0,9 s)", droga > 5, "(%.1f studa)" % droga)

            # 4. reset w trakcie
            t.luau(PRZY_TABLICY, "Server")
            time.sleep(0.5)
            t.czekaj_wolna(15)
            t.luau('workspace.TestWalki.Sygnaly.StartTestu:Fire() return "ok"')
            t.czekaj(("odtwarzanie",), 10)
            time.sleep(2.5)
            t.luau('local p = game:GetService("Players"):GetPlayers()[1] p.Character:FindFirstChildOfClass("Humanoid").Health = 0 return "ok"', "Server")
            s4, _ = t.czekaj(("przerwano",), 5)
            time.sleep(0.5)
            s4 = t.stan()
            sprawdz("4a. reset przerywa cutscenkę", s4.get("OstatniStan") == "przerwano")
            stan_po_walce("4b. zaraz po resecie", s4)
            for _ in range(40):
                time.sleep(0.5)
                s4 = t.stan()
                if s4["_hp"] > 0 and s4["_podmiotToHumanoid"]:
                    break
            time.sleep(1.5)
            s4 = t.stan()
            stan_po_walce("4c. po odrodzeniu", s4)
            sprawdz("4c'. po odrodzeniu własna postać widoczna", s4.get("_postacUkryta") == 0, "(%s)" % s4.get("_postacUkryta"))
            droga = t.klawisz_w()
            sprawdz("4d. po odrodzeniu postać chodzi", droga > 5, "(%.1f studa)" % droga)

            # 5. bezpieczeństwo
            t.luau(PRZY_TABLICY, "Server")
            t.czekaj_wolna(15)
            b = json.loads(t.luau(BEZPIECZENSTWO))
            sprawdz("5a. liczby od klienta zignorowane (hp 480, ziarno z serwera)",
                    b.get("a_ok") and b.get("a_hpGracza") == 480 and b.get("a_ziarno") == a.ziarno and (b.get("a_zloto") or 0) < 1000, str(b))
            sprawdz("5b. druga prośba w 1 s odrzucona („za_szybko”)", b.get("b_ok") is False and b.get("b_powod") == "za_szybko")
            sprawdz("5c. prośba w trakcie walki odrzucona („walka_trwa”)", b.get("c_ok") is False and b.get("c_powod") == "walka_trwa",
                    "(ponów za %.1f s)" % (b.get("c_ponowZa") or -1))
            t.luau(DALEKO, "Server")
            d = json.loads(t.luau(ZA_DALEKA))
            sprawdz("5d. prośba z daleka od tablicy odrzucona („za_daleko”)", d.get("d_ok") is False and d.get("d_powod") == "za_daleko", str(d))
            t.luau(PRZY_TABLICY, "Server")
            time.sleep(max(0.0, (b.get("a_zostalo") or 0)) + 0.5)  # walka „a” nie szła przez odtwarzacz: czekamy jej czas

            # 6. pomiary
            for nr in range(1, a.pomiary + 1):
                t.czekaj_wolna(15)
                t.luau('workspace.TestWalki.Sygnaly.StartTestu:Fire() return "ok"')
                s6, dt = t.czekaj(("wynik",), 20)
                pola = ("OstatniCzasTrwania", "OstatniaSredniaKlatki", "OstatniP95Klatki", "OstatniaMaksKlatki", "OstatniKosztSkryptuSredni",
                        "OstatniKosztSkryptuP95", "OstatniKosztSkryptuMaks", "OstatniaLiczbaInstancji", "OstatniCzasPrzygotowania",
                        "OstatniCzasSerwera", "OstatniaLiczbaSchowanych")
                log("pomiar %d: %s" % (nr, ", ".join("%s=%s" % (p.replace("Ostatnia", "").replace("Ostatni", ""), s6.get(p)) for p in pola)))
                sprawdz("6. pomiar %d: 8–10 s" % nr, 8.0 <= (s6.get("OstatniCzasTrwania") or 0) <= 10.2)
                time.sleep(0.8)
                t.luau('task.delay(0.5, function() workspace.TestWalki.Sygnaly.ZamknijTest:Fire() end) return "ok"')
                time.sleep(3.0)

            # 8. obcy w kadrze
            t.luau(INTRUZ, "Server")
            time.sleep(1.0)
            s8 = t.stan()
            klucze = ("_intruzManekin", "_intruzTag", "_intruzPozniej", "_postacUkryta")
            sprawdz("8-. przed walką manekin i część z tagiem widoczne", s8.get("_intruzManekin") == 0 and s8.get("_intruzTag") == 0,
                    str({k: s8.get(k) for k in klucze}))
            t.czekaj_wolna(15)
            t.luau('workspace.TestWalki.Sygnaly.StartTestu:Fire({ tempo = 0.5 }) return "ok"')
            t.czekaj(("odtwarzanie",), 10)
            time.sleep(0.6)
            t.luau(INTRUZ_POZNIEJ, "Server")
            time.sleep(1.0)
            s8 = t.stan()
            t.zrzut("08_obcy_schowani.png")
            sprawdz("8a. w trakcie: manekin, część z tagiem i część dodana później schowane",
                    s8.get("_intruzManekin") == 1 and s8.get("_intruzTag") == 1 and s8.get("_intruzPozniej") == 1,
                    str({k: s8.get(k) for k in klucze}))
            sprawdz("8b. w trakcie: własna postać schowana", s8.get("_postacUkryta") == 1)
            t.luau('workspace.TestWalki.Sygnaly.PominTest:Fire() return "ok"')
            s8, _ = t.czekaj(("wynik",), 6)
            sprawdz("8c. liczba schowanych ≥ 4 (gracz, manekin, tag, część)", (s8.get("OstatniaLiczbaSchowanych") or 0) >= 4,
                    "(%s)" % s8.get("OstatniaLiczbaSchowanych"))
            t.luau('workspace.TestWalki.Sygnaly.ZamknijTest:Fire() return "ok"')
            t.czekaj(("zamknieto",), 5)
            time.sleep(0.8)
            s8 = t.stan()
            t.zrzut("08_obcy_po_walce.png")
            sprawdz("8d. po walce wszystko znów widoczne",
                    s8.get("_intruzManekin") == 0 and s8.get("_intruzTag") == 0 and s8.get("_intruzPozniej") == 0 and s8.get("_postacUkryta") == 0,
                    str({k: s8.get(k) for k in klucze}))
            t.luau('workspace.TestWalki.TestowyIntruz:Destroy() return "ok"', "Server")

            # 9. symulacja publikacji
            with open(os.path.join(os.path.dirname(TU), "zrodla", "SerwerWalki.server.luau"), encoding="utf-8-sig") as f:
                zrodlo = f.read().replace("\r\n", "\n")
            kopia = zrodlo.replace('game:GetService("RunService"):IsStudio()', "false", 1)
            poziom = 3
            while ("]" + "=" * poziom + "]") in kopia:
                poziom += 1
            literal = "[" + "=" * poziom + "[\n" + kopia + "]" + "=" * poziom + "]"
            t.luau(PUBLIKACJA_1, "Server")
            time.sleep(1.0)
            klient_przed = t.luau('return tostring(workspace.TestWalki:FindFirstChild("ProbaPublikacji") ~= nil)').strip()
            w9 = t.luau(PUBLIKACJA_2.replace("__ZRODLO__", literal), "Server").strip()
            time.sleep(0.8)
            klient = t.luau('return tostring(workspace.TestWalki:FindFirstChild("ProbaPublikacji") ~= nil)').strip()
            sprawdz("9. poza Studio serwer usuwa swój kontener (serwer i klient)", klient_przed == "true" and w9 == "USUNIETY" and klient == "false",
                    "(klient przed: %s, serwer: %s, klient po: %s)" % (klient_przed, w9, klient))

            # 7. konsola
            kons = t.call("get_console_output")["text"]
            zle = [w for w in kons.splitlines() if "TestWalki" in w]
            sprawdz("7. konsola bez komunikatów [TestWalki]", not zle, "\n".join(zle[:5]))
        finally:
            log("Stop:", t.call("start_stop_play", {"is_start": False})["text"][:80])
            for _ in range(40):
                time.sleep(0.5)
                if t.tryb_edit():
                    break
            sprawdz("Studio wróciło do trybu Edit", t.tryb_edit())

    zle = [n for n, ok in WYNIKI if not ok]
    log("WYNIK: %d/%d zaliczonych%s" % (len(WYNIKI) - len(zle), len(WYNIKI), "" if not zle else " — nie: " + "; ".join(zle)))
    sys.exit(1 if zle else 0)


if __name__ == "__main__":
    main()
