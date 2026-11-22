#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba układu ekranu Monster Evolution na telefonie: Device Simulator Studio (najmniejszy telefon z listy, poziomo)
ustawiony w Edit przed Play; w grze klient mierzy prostokąty HUD (nakładanie, wyjście poza ekran, przyciski < 44 pt).
Play / Stop przez `python -B tools/studio_mcp.py call start_stop_play`. Na końcu symulacja urządzenia wyłączona.

    python -B swiat/ewolucja/testy/proba_telefon.py --studio <id> [--urzadzenie "Samsung Galaxy A06"]
"""
import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import proba_play as PP  # noqa: E402

URZADZENIE = r'''
local svc = game:GetService("StudioDeviceSimulatorService")
local chce = "__NAZWA__"
local best, bestPole, nazwa = nil, math.huge, nil
for _, id in svc:GetDeviceListAsync() do
	local info = svc:GetDeviceInfoAsync(id)
	if info.Name == chce then
		best, nazwa = id, info.Name
		break
	end
	if info.DeviceForm == Enum.DeviceForm.Phone and info.Width * info.Height < bestPole then
		best, bestPole, nazwa = id, info.Width * info.Height, info.Name
	end
end
if not best then
	return "STOP: brak telefonu na liście"
end
svc:SetDeviceAsync(best)
task.wait(0.3)
pcall(function()
	svc:SetOrientationAsync(Enum.ScreenOrientation.LandscapeLeft)
end)
task.wait(0.4)
local v = workspace.CurrentCamera.ViewportSize
return string.format("%s|%dx%d", nazwa, v.X, v.Y)
'''
KONIEC = ('local svc = game:GetService("StudioDeviceSimulatorService") local ok = pcall(function() svc:StopSimulationAsync() end) '
          'task.wait(0.3) return tostring(ok) .. "|" .. tostring(workspace.CurrentCamera.ViewportSize)')


def uklad(p):
    p.ustaw("EW_TestUklad", "true")
    time.sleep(0.4)
    return json.loads(p.atr().get("EW_K_Uklad") or "{}")


def main():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio", required=True)
    ap.add_argument("--urzadzenie", default="Samsung Galaxy A06")
    a = ap.parse_args()
    with PP.StudioMCP(timeout=180) as s:
        p = PP.P(s, a.studio)
        if "Current Studio Mode: Edit" not in p.call("get_studio_state")["text"]:
            PP.log("PRZERWANO — Studio nie jest w trybie Edit")
            return 1
        urz = p.luau(URZADZENIE.replace("__NAZWA__", a.urzadzenie), "Edit")
        PP.log("urządzenie:", urz)
        if urz.startswith("STOP"):
            return 1
        try:
            PP.log("Play:", PP.play(a.studio, True)[-40:])
            PP.czekaj(lambda: p.atr().get("klient") and p.atr().get("EW_Byt"), 30, 0.5)
            p.luau(PP.BEZ_LISTY, "Client")
            p.ustaw("EW_TestAuto", "true")
            time.sleep(6)
            p.zrzut("06_telefon.jpg")
            u1 = uklad(p)
            p.ustaw("EW_TestAuto", "false")
            PP.wynik("T1 HUD w grze", u1 and not u1["nakladanie"] and not u1["poza"] and not u1["male"] and not u1.get("rogi_paska"),
                     okno=u1.get("okno"), skala=u1.get("skala"), inset=u1.get("inset"), nakladanie=u1.get("nakladanie"), poza=u1.get("poza"),
                     male=u1.get("male"), rogi_paska=u1.get("rogi_paska"), prostokaty=u1.get("prostokaty"))
            p.serwer('"wzrost_pelny"')
            time.sleep(0.6)
            u2 = uklad(p)
            PP.wynik("T2 pełny pasek: EVOLVE + podpowiedź", u2 and "Ewolucja" in u2["prostokaty"] and not u2["nakladanie"] and not u2["poza"],
                     nakladanie=u2.get("nakladanie"), poza=u2.get("poza"), ewolucja=u2.get("prostokaty", {}).get("Ewolucja"))
            p.przycisk("ewoluuj")
            time.sleep(PP.D["ewolucja"]["kokon_s"] + 0.4)
            u3 = uklad(p)
            PP.wynik("T3 tabliczka odsłony mieści się", u3 and "Tabliczka" in u3["prostokaty"] and "Tabliczka" not in u3["poza"],
                     tabliczka=u3.get("prostokaty", {}).get("Tabliczka"), poza=u3.get("poza"))
            time.sleep(1.5)
            p.przycisk("legowisko")
            time.sleep(0.5)
            u4 = uklad(p)
            PP.wynik("T4 panel legowiska mieści się", u4 and "Panel" in u4["prostokaty"] and "Panel" not in u4["poza"] and not u4["male"],
                     panel=u4.get("prostokaty", {}).get("Panel"), okno=u4.get("okno"), male=u4.get("male"))
            p.przycisk("zakladka_u")
            time.sleep(0.4)
            u5 = uklad(p)
            PP.wynik("T4b zakładka ulepszeń mieści się", u5 and "Panel" in u5["prostokaty"] and "Panel" not in u5["poza"] and not u5["male"],
                     male=u5.get("male"))
            p.przycisk("zamknij")
            # T7 (walka1): cztery przyciski (BITE, DASH, FIRE, POWER) i ciemne sylwetki zamkniętych / następnych wersji
            pr1 = u1.get("prostokaty", {}) if u1 else {}
            zd1 = json.loads(p.atr().get("EW_K_Zd") or "{}")
            p.serwer('"forma_gracza", 4')
            time.sleep(2.6)
            u7 = uklad(p)
            pr7 = u7.get("prostokaty", {}) if u7 else {}
            zd7 = json.loads(p.atr().get("EW_K_Zd") or "{}")
            cztery = all(n in pr1 for n in ("Gryz", "Zryw", "Ogien", "Moc")) and all(n in pr7 for n in ("Gryz", "Zryw", "Ogien", "Moc"))
            PP.wynik("T7 cztery przyciski + sylwetki", cztery and u7 and not u7["nakladanie"] and not u7["poza"] and not u7["male"]
                     and "OgienNast" in pr7 and "MocNast" in pr7 and zd7.get("ogien", {}).get("nazwa") == "oddech"
                     and (zd1.get("moc", {}).get("zamkniete") or zd1.get("ogien", {}).get("zamkniete")),
                     przed=zd1, po=zd7, nakladanie=u7 and u7.get("nakladanie"), poza=u7 and u7.get("poza"),
                     prostokaty={k: v for k, v in pr7.items() if k in ("Gryz", "Zryw", "Ogien", "Moc", "OgienNast", "MocNast", "Zycie")})
            p.zrzut("17_telefon_walka.jpg")
            a1 = p.atr()
            PP.wynik("T5 klatka na telefonie", (a1.get("EW_K_Klatka") or 99) < 25, klatka_ms=round(a1.get("EW_K_Klatka") or 0, 1),
                     praca_skryptu_ms=round(a1.get("EW_K_Praca") or 0, 2), widokow=a1.get("EW_K_Widokow"), czesci_smokow=a1.get("EW_K_CzesciSmokow"),
                     rigi=a1.get("EW_K_Rigi"))
        finally:
            zle, _ = PP.bledy_konsoli(p)
            PP.wynik("T6 konsola bez błędów", not zle, bledy=zle[:10])
            PP.log("Stop:", PP.play(a.studio, False)[-40:])
            PP.czekaj(lambda: "Current Studio Mode: Edit" in p.call("get_studio_state")["text"], 40, 0.5)
            PP.log("symulacja urządzenia wyłączona:", p.luau(KONIEC, "Edit"))
    ok = sum(1 for v in PP.wyniki.values() if v)
    PP.log("WYNIK: %d/%d OK" % (ok, len(PP.wyniki)))
    return 0 if ok == len(PP.wyniki) else 1


if __name__ == "__main__":
    sys.exit(main())
