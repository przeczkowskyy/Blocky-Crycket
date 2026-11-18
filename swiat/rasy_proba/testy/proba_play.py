#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba wystawy ras w trybie PLAY w Studio — punkty R00–R09, wynik w <folder>/wynik_play.json (POZA repozytorium).

    python -B swiat/rasy_proba/testy/proba_play.py <folder wyników poza repo>
    python -B swiat/rasy_proba/testy/proba_play.py <folder> --bez-zrzutow

Wymaga: kontener Workspace/RasyProba (zbuduj.py), Studio w trybie Edit. Play tylko na czas próby (SesjaPlay
z swiat/test_walki2/testy/sesja_play.py zatrzymuje go zawsze i sprawdza powrót do Edit).
  R00 Edit: kontener jest, siedem figur, liczba części każdej = dane, skrypt spoczynku zainstalowany
  R01 Play (serwer): figury, skala i wzrost zgodne z danymi ras, stopy na ziemi
  R02 nic nie koliduje z graczem: żadna część nie ma kolizji, dotyku ani promieni; postać upuszczona na figurę
      przelatuje przez nią i staje na ziemi
  R03 tabliczki: napis = nazwa rasy, nad najwyższym punktem figury
  R04 spoczynek: skrypt uruchomił oddech siedmiu figur; u klienta każda gra klip, a głowa się rusza
  R05 świecenie: oczy demona i półboga oraz aureola to części Neon
  R06 konsola bez błędów i ostrzeżeń pakietu
  R07 czas klatki z kamerą na wystawę i odwróconą (miarodajny tylko, gdy okno Studio jest na wierzchu)
  R08 zrzuty do swiat/rasy_proba/klatki/ (bez listy graczy, bez interfejsu gry, bez nazwy nad postacią)
  R09 po próbie Studio wróciło do trybu Edit
Okno Studio idzie na wierzch tylko wtedy, gdy nie jest już na wierzchu, a klawiatura i mysz stoją od co najmniej
120 s (ktoś może pracować). Uwaga: sesja Play sama rusza myszą (czuwanie ekranu), więc próba puszczona zaraz po
innej widzi krótką bezczynność.
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
for _s in (REPO, os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki2", "testy")):
    if _s not in sys.path:
        sys.path.append(_s)
if PAKIET in sys.path:
    sys.path.remove(PAKIET)
sys.path.insert(0, PAKIET)                             # własne moduły pakietu zawsze pierwsze (dane, zbuduj)
import dane as DN  # noqa: E402
import zbuduj as ZB  # noqa: E402

KLATKI = os.path.join(PAKIET, "klatki")
BEZCZYNNOSC_S = 120

UPUSC = r'''
local gracz = game:GetService("Players"):GetPlayers()[1]
local hrp = gracz and gracz.Character and gracz.Character:FindFirstChild("HumanoidRootPart")
local m = workspace.__KONTENER__:FindFirstChild("__FIGURA__")
if not hrp or not m then return "brak" end
local ziemia = m:GetAttribute("Ziemia")
local p = m.HumanoidRootPart.Position
hrp.AssemblyLinearVelocity = Vector3.zero
hrp.CFrame = CFrame.new(p.X, ziemia + 9, p.Z)
task.wait(2.2)
local y = hrp.Position.Y - ziemia
hrp.CFrame = CFrame.new(__POWROT__)
return string.format("%.2f", y)
'''

KLIENT_SPOCZYNEK = r'''
local HS = game:GetService("HttpService")
local kont = workspace:WaitForChild("__KONTENER__", 10)
local w = {}
local glowy = {}
for _, m in kont:GetChildren() do
	if m:IsA("Model") then
		local ac = m:FindFirstChildWhichIsA("AnimationController")
		local an = ac and ac:FindFirstChildWhichIsA("Animator")
		w[m.Name] = { gra = an and #an:GetPlayingAnimationTracks() or 0, ruch = 0 }
		glowy[m.Name] = m:FindFirstChild("Head")
	end
end
local p0 = {}
for n, g in glowy do p0[n] = g.CFrame end
for _ = 1, 8 do
	task.wait(0.15)
	for n, g in glowy do
		local d = (g.Position - p0[n].Position).Magnitude + math.abs(g.CFrame.LookVector:Dot(p0[n].LookVector) - 1) * 10
		w[n].ruch = math.max(w[n].ruch, d)
	end
end
return HS:JSONEncode(w)
'''

KLATKA = r'''
local RS = game:GetService("RunService")
local kam = workspace.CurrentCamera
local typ = kam.CameraType
kam.CameraType = Enum.CameraType.Scriptable
kam.CFrame = CFrame.lookAt(Vector3.new(__Z__), Vector3.new(__NA__))
task.wait(0.5)
local n, suma, maks = 0, 0, 0
local t0 = os.clock()
while os.clock() - t0 < 3 do
	local dt = RS.RenderStepped:Wait()
	n += 1
	suma += dt
	maks = math.max(maks, dt)
end
kam.CameraType = typ
return string.format("%.2f %.2f %d", suma / n * 1000, maks * 1000, n)
'''

# na czas zrzutów: bez listy graczy i reszty interfejsu, bez nazwy nad postacią gracza; stan wraca po zrzutach
SCHOWAJ = r'''
local SG = game:GetService("StarterGui")
local gracz = game:GetService("Players").LocalPlayer
pcall(function() SG:SetCoreGuiEnabled(Enum.CoreGuiType.All, false) end)
local ile = 0
for _, g in gracz.PlayerGui:GetChildren() do
	if g:IsA("ScreenGui") and g.Enabled then
		g.Enabled = false
		g:SetAttribute("RasyProbaSchowane", true)
		ile += 1
	end
end
local hum = gracz.Character and gracz.Character:FindFirstChildOfClass("Humanoid")
if hum then
	hum.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
end
game:GetService("ProximityPromptService").Enabled = false
return tostring(ile)
'''

POKAZ = r'''
local SG = game:GetService("StarterGui")
local gracz = game:GetService("Players").LocalPlayer
for _, g in gracz.PlayerGui:GetChildren() do
	if g:IsA("ScreenGui") and g:GetAttribute("RasyProbaSchowane") then
		g.Enabled = true
		g:SetAttribute("RasyProbaSchowane", nil)
	end
end
pcall(function() SG:SetCoreGuiEnabled(Enum.CoreGuiType.All, true) end)
local hum = gracz.Character and gracz.Character:FindFirstChildOfClass("Humanoid")
if hum then
	hum.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.Viewer
end
game:GetService("ProximityPromptService").Enabled = true
return "ok"
'''


def log(*a):
    print("[%s]" % time.strftime("%H:%M:%S"), *a, flush=True)


def bezczynnosc_s():
    """Sekundy od ostatniego ruchu myszy albo klawisza (Windows GetLastInputInfo); None poza Windows."""
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


def wek(v):
    return ", ".join(repr(float(x)) for x in v)


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Próba wystawy ras (Play)")
    ap.add_argument("folder", help="folder wyników POZA repozytorium")
    ap.add_argument("--bez-zrzutow", action="store_true")
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    folder = os.path.abspath(a.folder)
    if os.path.commonpath([folder, REPO]) == REPO:
        sys.exit("Folder wyników musi leżeć poza repozytorium.")
    os.makedirs(folder, exist_ok=True)
    U = DN.ustawienia()
    F = DN.figury(U)
    P = U["proba"]
    kont = U["kontener"]
    wyniki, dane = [], {}

    def punkt(kod, ok, opis):
        wyniki.append({"punkt": kod, "wynik": "OK" if ok is True else ("?" if ok is None else "BŁĄD"), "opis": opis})
        log("%s %s — %s" % (kod, wyniki[-1]["wynik"], opis))

    # okno na wierzch tylko, gdy przy komputerze nikt nie pracuje (pomiar PRZED startem sesji: sesja rusza myszą)
    bezcz = bezczynnosc_s()
    okno = [sys.executable, "-B", os.path.join(REPO, "tools", "studio_okno.py")]
    stan_okna = subprocess.run(okno, capture_output=True).stdout.decode("utf-8", "replace")
    na_wierzchu = "na wierzchu" in stan_okna                   # już jest na wierzchu — niczego nie przenoszę
    if not na_wierzchu and bezcz is not None and bezcz >= BEZCZYNNOSC_S:
        na_wierzchu = subprocess.run(okno + ["--na-wierzch"], capture_output=True).returncode == 0
    log("bezczynność klawiatury i myszy: %s s; okno Studio na wierzchu: %s"
        % ("?" if bezcz is None else "%.0f" % bezcz, "tak" if na_wierzchu else "nie (nie przenoszę)"))
    dane["bezczynnosc_s"], dane["okno_na_wierzchu"] = bezcz, na_wierzchu

    from sesja_play import SesjaPlay  # noqa: E402  (tylko odczyt: wspólna obsługa Play)
    from studio_mcp import StudioMCP  # noqa: E402
    from cel_studio import wybierz_studio  # noqa: E402

    def sprawdz_stan(stan, kod, gdzie):
        zle = []
        if not stan.get("jest"):
            return punkt(kod, False, "%s: brak kontenera Workspace/%s" % (gdzie, kont))
        for f in F:
            m = next((x for x in stan["figury"] if x["id"] == f["id"]), None)
            if m is None:
                zle.append("%s: brak" % f["id"])
                continue
            if m["czesci"] != DN.liczba_czesci(f) or m["bryl"] != len(f["czesci"]):
                zle.append("%s: części %d/%d" % (f["id"], m["czesci"], DN.liczba_czesci(f)))
            if abs(m["skala"] - f["skala"]) > 1e-6 or abs(m["wzrost"] - f["wzrost"]) > P["tolerancja_wzrostu"]:
                zle.append("%s: skala %.2f, wzrost %.3f (dane %.2f, %.2f)" % (f["id"], m["skala"], m["wzrost"],
                                                                               f["skala"], f["wzrost"]))
            if abs(m["stopy"]) > P["tolerancja_stop"]:
                zle.append("%s: stopy %.3f nad ziemią" % (f["id"], m["stopy"]))
            if not m["korzen_zakotwiczony"]:
                zle.append("%s: korzeń niezakotwiczony" % f["id"])
        if len(stan["figury"]) != len(F):
            zle.append("figur %d zamiast %d" % (len(stan["figury"]), len(F)))
        opis = ("%s: %d figur, %d części; wzrost %s; stopy do %.3f studa od ziemi"
                % (gdzie, len(stan["figury"]), stan["czesci"],
                   ", ".join("%s %.2f" % (m["id"], m["wzrost"]) for m in stan["figury"]),
                   max(abs(m["stopy"]) for m in stan["figury"])))
        punkt(kod, not zle, opis if not zle else opis + " — " + "; ".join(zle))

    # R00: odczyt w trybie Edit
    with StudioMCP(timeout=120) as s:
        sid = wybierz_studio(s, a.studio)
        r = s.call("execute_luau", {"code": ZB.kod_stanu(U), "datamodel_type": "Edit", "studio_id": sid})
        stan_edit = json.loads(r["text"])
    dane["edit"] = stan_edit
    sprawdz_stan(stan_edit, "R00", "Edit")
    if stan_edit.get("jest") and not stan_edit.get("skrypt"):
        punkt("R00s", False, "brak skryptu %s w kontenerze" % U["skrypt_spoczynku"])

    edit_po = None
    with SesjaPlay(a.studio) as sp:
        try:
            time.sleep(2.0)
            stan = json.loads(sp.luau(ZB.kod_stanu(U), "Server"))
            dane["play"] = stan
            sprawdz_stan(stan, "R01", "Play (serwer)")
            figury = stan.get("figury", [])
            # R02: kolizje
            zle = ["%s: kolizja %d, dotyk %d, promienie %d" % (m["id"], m["koliduja"], m["dotyk"], m["promienie"])
                   for m in figury if m["koliduja"] or m["dotyk"] or m["promienie"]]
            powrot = "0, 6.0, 3"                              # z powrotem nad płytę startu
            upusc = {}
            for fid in ("ork", "polbog"):
                kod = ZB.wstaw(UPUSC, KONTENER=kont, FIGURA=fid, POWROT=powrot)
                try:
                    upusc[fid] = float(sp.luau(kod, "Server", timeout=60))
                except Exception as e:  # noqa: BLE001
                    upusc[fid] = None
                    zle.append("%s: upuszczenie postaci: %s" % (fid, str(e)[:80]))
            dane["upuszczenie"] = upusc
            # postać stojąca na ziemi ma korzeń ok. 3 study nad ziemią; na figurze stałaby ponad 5,5 studa wyżej
            for fid, y in upusc.items():
                if y is not None and y > 4.6:
                    zle.append("%s: postać została %.2f studa nad ziemią (stoi na figurze?)" % (fid, y))
            punkt("R02", not zle, "żadna z %d części nie ma kolizji, dotyku ani promieni; postać upuszczona na orka "
                  "i półboga staje na ziemi (korzeń %s studa nad ziemią)"
                  % (stan.get("czesci", 0), ", ".join("%.2f" % y for y in upusc.values() if y is not None))
                  if not zle else "; ".join(zle))
            # R03: tabliczki
            zle = []
            for f in F:
                m = next((x for x in figury if x["id"] == f["id"]), None)
                if not m or m["tabliczka"] != f["nazwa"]:
                    zle.append("%s: napis %r" % (f["id"], m and m["tabliczka"]))
            punkt("R03", not zle, "tabliczki: %s" % ", ".join("„%s”" % m["tabliczka"] for m in figury)
                  if not zle else "; ".join(zle))
            # R04: spoczynek
            kl = json.loads(sp.luau(ZB.wstaw(KLIENT_SPOCZYNEK, KONTENER=kont), "Client", timeout=60))
            dane["spoczynek_klient"] = kl
            zle = []
            if stan.get("spoczynek") != len(F):
                zle.append("serwer uruchomił oddech %s figur zamiast %d" % (stan.get("spoczynek"), len(F)))
            for fid, v in kl.items():
                if v["gra"] < 1 or v["ruch"] < 1e-4:
                    zle.append("%s: klipów %d, ruch głowy %.5f" % (fid, v["gra"], v["ruch"]))
            punkt("R04", not zle, "oddech gra na %s figurach (serwer); u klienta każda figura gra klip, ruch głowy "
                  "%.4f–%.4f studa" % (stan.get("spoczynek"), min(v["ruch"] for v in kl.values()),
                                        max(v["ruch"] for v in kl.values())) if not zle else "; ".join(zle))
            # R05: Neon
            neon = {m["id"]: m["neon"] for m in figury}
            ocz = {f["id"]: f["swiecace"] for f in F}
            punkt("R05", neon == ocz and ocz.get("demon", 0) > 0 and ocz.get("polbog", 0) > 0,
                  "części Neon: demon %s, półbóg %s (dane: %s, %s); pozostałe figury 0"
                  % (neon.get("demon"), neon.get("polbog"), ocz.get("demon"), ocz.get("polbog")))
            # R07: czas klatki
            try:
                na = sp.luau(ZB.wstaw(KLATKA, Z=wek(P["kamera_gracza"]["z"]), NA=wek(P["kamera_gracza"]["na"])),
                             "Client", timeout=60).split()
                kz = P["kamera_gracza"]["z"]
                od = sp.luau(ZB.wstaw(KLATKA, Z=wek(kz), NA=wek([kz[0], kz[1], kz[2] + 30.0])), "Client",
                             timeout=60).split()
                dane["czas_klatki"] = {"na_wystawe_ms": float(na[0]), "najdluzsza_ms": float(na[1]), "klatek": int(na[2]),
                                       "odwrocona_ms": float(od[0])}
                ok = float(na[0]) <= P["dopuszczalny_czas_klatki_ms"]
                punkt("R07", (ok if na_wierzchu else None),
                      "czas klatki z kamerą na wystawę %.1f ms (najdłuższa %.1f, %d klatek w 3 s), odwróconą %.1f ms; "
                      "próg %.0f ms%s" % (float(na[0]), float(na[1]), int(na[2]), float(od[0]),
                                          P["dopuszczalny_czas_klatki_ms"],
                                          "" if na_wierzchu else " — okno Studio nie było na wierzchu, pomiar niemiarodajny"))
            except Exception as e:  # noqa: BLE001
                punkt("R07", None, "pomiar czasu klatki się nie udał: %s" % str(e)[:120])
            # R08: zrzuty
            if a.bez_zrzutow:
                punkt("R08", None, "zrzuty pominięte (--bez-zrzutow)")
            else:
                os.makedirs(KLATKI, exist_ok=True)
                zapisane = []
                try:
                    sp.luau(SCHOWAJ, "Client")
                    time.sleep(0.8)
                    kadry = dict(P["kamery"], widok_gracza=P["kamera_gracza"])
                    for nazwa in ("widok_gracza", "lewa_grupa", "prawa_grupa", "z_boku"):
                        k = kadry[nazwa]
                        im = sp.zrzut(k["z"], k["na"])
                        if im.width > 1600:
                            im = im.resize((1600, round(im.height * 1600 / im.width)))
                        sc = os.path.join(KLATKI, "wystawa_%s.jpg" % nazwa)
                        im.save(sc, quality=88)
                        zapisane.append(os.path.basename(sc))
                finally:
                    sp.luau(POKAZ, "Client")
                punkt("R08", len(zapisane) == 4, "zrzuty: %s" % ", ".join(zapisane))
            # R06: konsola
            kons = sp.konsola()
            linie = [l for l in kons.splitlines() if U["prefiks"].strip() in l or U["skrypt_spoczynku"] in l
                     or kont in l]
            with open(os.path.join(folder, "konsola.txt"), "w", encoding="utf-8") as f:
                f.write(kons)
            punkt("R06", not linie, "konsola bez wpisów pakietu (błędów i ostrzeżeń %s nie ma)" % U["prefiks"].strip()
                  if not linie else "wpisy pakietu w konsoli: " + " | ".join(linie[:4]))
        finally:
            pass
    edit_po = getattr(sp, "edit_po", None)
    punkt("R09", edit_po is True, "Studio po próbie w trybie Edit: %s" % edit_po)
    with open(os.path.join(folder, "wynik_play.json"), "w", encoding="utf-8") as f:
        json.dump({"kiedy": time.strftime("%Y-%m-%d %H:%M"), "wyniki": wyniki, "dane": dane}, f, ensure_ascii=False,
                  indent=1)
    zle = [w for w in wyniki if w["wynik"] == "BŁĄD"]
    log("RAZEM: %d OK, %d ?, %d BŁĄD" % (sum(w["wynik"] == "OK" for w in wyniki),
                                         sum(w["wynik"] == "?" for w in wyniki), len(zle)))
    return 1 if zle else 0


if __name__ == "__main__":
    sys.exit(main())
