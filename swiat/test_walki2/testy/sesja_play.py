# -*- coding: utf-8 -*-
"""Wspólna obsługa sesji PLAY w Studio dla testów walki v2 (test_walki_play.py, klatki_walki.py, proba_play.py).

Zasady (jak w testach v1 i etapu 1): okno wybiera cel_studio.py (placeId gry); Play tylko na czas testu — `with
SesjaPlay(...)` ZAWSZE zatrzymuje Play w `finally` (także po błędzie i Ctrl+C) i sprawdza, że Studio wróciło do Edit.
Zmienia wyłącznie stan sesji Play (znika po jej zatrzymaniu).
"""
import io
import json
import os
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
KATALOG = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(KATALOG))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"), TU):
    if _s not in sys.path:
        sys.path.insert(0, _s)
from studio_mcp import StudioMCP, StudioError  # noqa: E402
from cel_studio import wybierz_studio  # noqa: E402
from czuwanie import nie_usypiaj  # noqa: E402

# przed tablicą (świat): tablica w (16, 3.7, 220), napis na północ; stajemy 6 studów na północ od niej
PRZY_TABLICY = ("16, 4.5, 213", "16, 4.5, 220")
DALEKO = ("16, 4.5, 185", "16, 4.5, 190")
SCIEZKA_GUI = "LocalPlayer.PlayerGui."  # format narzędzia user_mouse_input (jak w teście v1)

STAN = r'''
local HS = game:GetService("HttpService")
local CAS = game:GetService("ContextActionService")
local SG = game:GetService("StarterGui")
local gracz = game:GetService("Players").LocalPlayer
local k = workspace:FindFirstChild("TestWalki2")
local t = {}
if k then for n, v in k:GetAttributes() do t[n] = v end end
local kam = workspace.CurrentCamera
t._kamera = kam.CameraType.Name
local hum = gracz.Character and gracz.Character:FindFirstChildOfClass("Humanoid")
t._podmiotToHumanoid = hum ~= nil and kam.CameraSubject == hum
t._hp = hum and hum.Health or -1
local hrp = gracz.Character and gracz.Character:FindFirstChild("HumanoidRootPart")
t._poz = hrp and { hrp.Position.X, hrp.Position.Y, hrp.Position.Z } or { 0, 0, 0 }
t._gui = gracz.PlayerGui:FindFirstChild("TestWalki2Cutscenka") ~= nil
t._panel = gracz.PlayerGui:FindFirstChild("TestWalki2Wybor") ~= nil
t._scena = k and k:FindFirstChild("ScenaLokalna") ~= nil
t._lista = SG:GetCoreGuiEnabled(Enum.CoreGuiType.PlayerList)
t._czat = SG:GetCoreGuiEnabled(Enum.CoreGuiType.Chat)
t._blokada = next(CAS:GetBoundActionInfo("TestWalki2BlokadaSterowania")) ~= nil
t._pominKlawisz = next(CAS:GetBoundActionInfo("TestWalki2Pomin")) ~= nil
local pp = k and k:FindFirstChild("PodpowiedzWalki2", true)
t._podpowiedz = pp and pp.Enabled
t._podpowiedzTekst = pp and pp.ActionText
local sz = k and k:FindFirstChild("Aktorzy") and k.Aktorzy:FindFirstChild("wojownik")
local cz = sz and sz:FindFirstChildWhichIsA("BasePart", true)
t._szablonUkryty = cz and cz.LocalTransparencyModifier
local glowa = gracz.Character and gracz.Character:FindFirstChild("Head")
t._postacUkryta = glowa and glowa.LocalTransparencyModifier
local gui = gracz.PlayerGui:FindFirstChild("TestWalki2Cutscenka")
local jeszcze = gui and gui:FindFirstChild("JeszczeRaz", true)
jeszcze = jeszcze and jeszcze:FindFirstChild("Przycisk")
t._jeszczeZablokowany = jeszcze and jeszcze:GetAttribute("Zablokowany")
t._jeszczeTekst = jeszcze and jeszcze:FindFirstChild("Napis") and jeszcze.Napis.Text
local wynik = gui and gui:FindFirstChild("Wynik", true)
t._wynikWidoczny = wynik and wynik.Visible
if wynik then
	local lup = {}
	for i = 1, 5 do
		local kafel = wynik:FindFirstChild("Kafel" .. i, true)
		lup[i] = kafel and kafel:GetAttribute("Wartosc")
	end
	t._lupPanelu = lup
end
local s = k and k.Sygnaly:FindFirstChild("Sterowanie")
if s then
	local ok, st = pcall(function() return s:Invoke("stan") end)
	if ok then t._odtw = st end
end
t._czasSerwera = workspace:GetServerTimeNow()
return HS:JSONEncode(t)
'''

GOTOWOSC = ('local p = game:GetService("Players").LocalPlayer; local k = workspace:FindFirstChild("TestWalki2"); '
            'return tostring(p and p.Character ~= nil) .. " " .. tostring(k and k:GetAttribute("KlientGotowy"))')

PRZESTAW = ('local p = game:GetService("Players"):GetPlayers()[1] '
            'p.Character:PivotTo(CFrame.lookAt(Vector3.new(%s), Vector3.new(%s))) return "ok"')

UKRYJ_GUI_GRY = r'''
local gracz = game:GetService("Players").LocalPlayer
for _, g in gracz.PlayerGui:GetChildren() do
	if g:IsA("ScreenGui") and g.Name ~= "TestWalki2Cutscenka" and g.Name ~= "TestWalki2Wybor" then g.Enabled = false end
end
return "ok"
'''


def log(*a):
    print("[%s]" % time.strftime("%H:%M:%S"), *a, flush=True)


class SesjaPlay:
    def __init__(self, studio=None, timeout=180):
        self.studio = studio
        self.timeout = timeout
        self.s = None
        self.sid = None

    # --- wejście / wyjście: Play tylko na czas bloku `with`
    def __enter__(self):
        self.mcp = StudioMCP(timeout=self.timeout)
        self.s = self.mcp.__enter__()
        self.sid = wybierz_studio(self.s, self.studio)
        if not self.tryb_edit():
            self.mcp.__exit__(None, None, None)
            sys.exit("Studio nie jest w trybie Edit — nie zaczynam.")
        nie_usypiaj()
        try:
            log("Play:", self.call("start_stop_play", {"is_start": True})["text"][:80])
            for _ in range(140):
                if "Client" in self.call("get_studio_state")["text"]:
                    try:
                        if self.luau(GOTOWOSC).strip() == "true true":
                            break
                    except StudioError:
                        pass
                time.sleep(0.5)
            time.sleep(1.5)
        except BaseException:
            self.zatrzymaj()
            self.mcp.__exit__(None, None, None)
            raise
        return self

    def __exit__(self, typ, wart, tb):
        try:
            self.zatrzymaj()
        finally:
            self.mcp.__exit__(typ, wart, tb)
        return False

    def zatrzymaj(self):
        try:
            log("Stop:", self.call("start_stop_play", {"is_start": False})["text"][:80])
        except Exception as e:  # noqa: BLE001
            log("Stop — błąd:", e)
        for _ in range(60):
            time.sleep(0.5)
            try:
                if self.tryb_edit():
                    break
            except Exception:  # noqa: BLE001
                pass
        self.edit_po = self.tryb_edit()
        log("Studio w trybie Edit:", self.edit_po)

    # --- narzędzia
    def call(self, nazwa, args=None, timeout=None):
        a = dict(args or {})
        a["studio_id"] = self.sid
        return self.s.call(nazwa, a, timeout=timeout)

    def tryb_edit(self):
        return "Current Studio Mode: Edit" in self.call("get_studio_state")["text"]

    def luau(self, kod, dm="Client", timeout=120):
        r = self.call("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=timeout)
        if r["is_error"]:
            raise StudioError(r["text"][:2000])
        return r["text"]

    def stan(self):
        return json.loads(self.luau(STAN))

    def steruj(self, kod_args):
        """Sygnaly/Sterowanie:Invoke(...) u klienta; kod_args = tekst argumentów Luau, np. '"pomin"'."""
        return self.luau('local s = workspace.TestWalki2.Sygnaly.Sterowanie '
                         'return game:GetService("HttpService"):JSONEncode(s:Invoke(%s))' % kod_args)

    def przy_tablicy(self):
        return self.luau(PRZESTAW % PRZY_TABLICY, "Server")

    def daleko(self):
        return self.luau(PRZESTAW % DALEKO, "Server")

    def ziarno(self, ziarno):
        if ziarno:
            return self.luau('workspace.TestWalki2:SetAttribute("ZiarnoTestowe", %d) return "ok"' % ziarno, "Server")
        return self.luau('workspace.TestWalki2:SetAttribute("ZiarnoTestowe", nil) return "ok"', "Server")

    def start(self, klasa, przeciwnik, poziom, opcje="nil"):
        return self.steruj('"start", { klasa = "%s", przeciwnik = "%s", poziom = "%s" }, %s' % (klasa, przeciwnik, poziom, opcje))

    def czekaj(self, stany, limit):
        t0 = time.time()
        s = {}
        while time.time() - t0 < limit:
            s = self.stan()
            if s.get("OstatniStan") in stany:
                return s, time.time() - t0
            time.sleep(0.25)
        return s, time.time() - t0

    def czekaj_wolna(self, limit):
        t0 = time.time()
        zostalo = 0
        while time.time() - t0 < limit:
            s = self.stan()
            zostalo = (s.get("NastepnaWalkaOd") or 0) - s["_czasSerwera"]
            if zostalo <= -0.1:
                break
            time.sleep(0.3)
        return zostalo

    def klik(self, sciezka):
        return self.call("user_mouse_input", {"datamodel_type": "Client", "actions": [
            {"action": "moveTo", "instance_path": SCIEZKA_GUI + sciezka},
            {"action": "mouseButtonClick", "mouse_button": "left"}]})["text"]

    def klawisz(self, kod):
        return self.call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": kod}]})

    def klawisz_w(self, ms=900):
        p1 = self.stan()["_poz"]
        self.call("user_keyboard_input", {"datamodel_type": "Client", "actions": [
            {"action": "keyDown", "key_code": "W"}, {"action": "wait", "wait_time_ms": ms}, {"action": "keyUp", "key_code": "W"}]})
        time.sleep(0.4)
        p2 = self.stan()["_poz"]
        return ((p2[0] - p1[0]) ** 2 + (p2[2] - p1[2]) ** 2) ** 0.5

    def zrzut(self, kamera=None, patrz=None):
        """Zrzut ekranu (PIL Image). W Play narzędzie samo ustawia kamerę — podajemy bieżącą kamerę odtwarzacza."""
        from PIL import Image
        nie_usypiaj()
        args = {"capture_id": "tw2_walka"}
        if kamera is not None:
            args["camera_position"] = list(kamera)
            args["look_at_position"] = list(patrz)
        r = self.call("screen_capture", args, timeout=120)
        if r["is_error"] or not r["images"]:
            raise StudioError("zrzut: %s" % (r["text"] or "brak obrazu")[:300])
        return Image.open(io.BytesIO(r["images"][0])).convert("RGB")

    def zrzut_odtwarzacza(self):
        st = self.stan().get("_odtw") or {}
        if st.get("kamera"):
            return self.zrzut(st["kamera"], st["patrz"]), st
        return self.zrzut(), st

    def konsola(self):
        return self.call("get_console_output")["text"]
