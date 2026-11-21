#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba zabawek w trybie PLAY w Studio (wybrane punkty). Play wyłącznie przez tools/studio_mcp.py.

    python -B swiat/zabawki/testy/proba_play.py --studio <id> [--bez-zrzutow] [--tylko 1|2]

Wejście jak z palca: atrybuty lokalnego gracza (ZT_TestSter, ZT_TestDash, ZT_TestRzut, ZT_TestCel); haczyki serwera:
Sygnaly/SterowanieSerwera. Lista graczy schowana na czas zrzutów (bez nazwy konta).
"""
import argparse
import io
import json
import math
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
sys.path.insert(0, PAKIET)
sys.path.append(os.path.join(REPO, "tools"))
import dane as DN  # noqa: E402
from studio_mcp import StudioMCP, StudioError  # noqa: E402

D = DN.dane()
Z, W = D["zjadacz"], D["wabik"]
K = D["kontener"]
KLATKI = os.path.join(PAKIET, "klatki")
SERWER = 'local HS = game:GetService("HttpService") return HS:JSONEncode(workspace.%s.Sygnaly.SterowanieSerwera:Invoke(%%s))' % K
ATR = ('local HS = game:GetService("HttpService") local p = game:GetService("Players").LocalPlayer local a = p:GetAttributes() '
       'local g = p.PlayerGui:FindFirstChild("Zabawki") a.menu = g and g.Ekran.Menu.Visible a.kamera = tostring(workspace.CurrentCamera.CameraType) '
       'local v = workspace.CurrentCamera.ViewportSize a.okno = { v.X, v.Y } '
       'local pa = workspace:FindFirstChild("PetArenaGra") a.pa_serwer = pa and pa:GetAttribute("SerwerGotowy") a.pa_slot = p:GetAttribute("PA_Slot") '
       'for k, x in a do if typeof(x) == "Vector2" or typeof(x) == "Vector3" then a[k] = tostring(x) end end return HS:JSONEncode(a)')
BEZ_LISTY = ('local SG = game:GetService("StarterGui") pcall(function() SG:SetCoreGuiEnabled(Enum.CoreGuiType.PlayerList, false) '
             'SG:SetCoreGuiEnabled(Enum.CoreGuiType.Chat, false) end) return "ok"')
wyniki = {}


def log(*a):
    print("[%s]" % time.strftime("%H:%M:%S"), *a, flush=True)


class P:
    def __init__(self, s, sid):
        self.s, self.sid = s, sid

    def call(self, n, args=None, timeout=None):
        x = dict(args or {})
        x["studio_id"] = self.sid
        return self.s.call(n, x, timeout=timeout)

    def luau(self, kod, dm, timeout=120):
        r = self.call("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=timeout)
        if r["is_error"]:
            raise StudioError(r["text"][:1200])
        return r["text"].strip()

    def serwer(self, a):
        return json.loads(self.luau(SERWER % a, "Server"))

    def atr(self):
        return json.loads(self.luau(ATR, "Client"))

    def ustaw(self, nazwa, wartosc):
        self.luau('game:GetService("Players").LocalPlayer:SetAttribute("%s", %s) return "ok"' % (nazwa, wartosc), "Client")

    def akcja(self, *a):
        self.luau('workspace.%s.Sygnaly.Akcja:FireServer(%s) return "ok"' % (K, ", ".join(a)), "Client")

    def zrzut(self, nazwa):
        from PIL import Image
        r = self.call("screen_capture", {"capture_id": "zabawki"}, timeout=120)
        if r["is_error"] or not r["images"]:
            log("zrzut nieudany:", (r["text"] or "")[:200])
            return
        img = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
        if img.width > 1920:
            img = img.resize((1920, int(img.height * 1920 / img.width)))
        os.makedirs(KLATKI, exist_ok=True)
        img.save(os.path.join(KLATKI, nazwa), quality=86)
        log("zrzut: swiat/zabawki/klatki/" + nazwa)


def wynik(punkt, ok, **sz):
    wyniki[punkt] = bool(ok)
    log("%s %s %s" % (punkt, "OK  " if ok else "BŁĄD", json.dumps(sz, ensure_ascii=False)[:600]))


def czekaj(war, limit, krok=0.25):
    t0 = time.time()
    while time.time() - t0 < limit:
        try:
            w = war()
            if w:
                return w, time.time() - t0
        except StudioError:
            pass
        time.sleep(krok)
    return None, time.time() - t0


def moj_byt(st):
    return next((b for b in st["byty"] if b["id"] == st.get("byt")), None)


def zabawka1(p, zrzuty):
    t0 = time.time()
    p.akcja('"wybor"', "1")
    czekaj(lambda: p.atr().get("ZT_Tryb") == "z1", 5)
    a = p.atr()
    st = p.serwer('"stan"')
    wynik("Z10 wejście", a.get("ZT_Tryb") == "z1" and a.get("menu") is False and "Scriptable" in a.get("kamera", "") and moj_byt(st),
          tryb=a.get("ZT_Tryb"), kamera=a.get("kamera"), byt=bool(moj_byt(st)))
    # pierwsze sekundy: kieruj do najbliższej kulki (jak gracz, który widzi świecące kulki)
    b = moj_byt(st)
    zywe = [Z["kulkiPoz"][i - 1] for i in st.get("kulkiZywe", [])]
    best = min(zywe, key=lambda k: math.hypot(k[0] - b["x"], k[1] - b["z"]))
    odl0 = math.hypot(best[0] - b["x"], best[1] - b["z"])
    dx, dz = best[0] - b["x"], best[1] - b["z"]
    d = max(0.1, math.hypot(dx, dz))
    # ekran: prawo = −x świata, góra = +z
    p.ustaw("ZT_TestSter", "Vector3.new(%f, %f, 4)" % (-dx / d, dz / d))
    pierwsza, _ = czekaj(lambda: p.atr().get("ZT_Pierwsza"), 8, 0.2)
    wynik("Z11 pierwsze zjedzenie", pierwsza is not None and pierwsza <= 5, s_od_wyboru=pierwsza, najblizsza_kulka=round(odl0, 1),
          od_kliku=round(time.time() - t0, 1))
    if zrzuty:
        time.sleep(0.5)
        p.zrzut("zj_gra.jpg")
    # ewolucja: masa tuż pod progiem, kulka → EVOLVED!
    p.serwer('"masa", %f' % (Z["formy"][1]["od"] - 0.05))
    st = p.serwer('"stan"')
    b = moj_byt(st)
    zywe = [Z["kulkiPoz"][i - 1] for i in st.get("kulkiZywe", [])]
    best = min(zywe, key=lambda k: math.hypot(k[0] - b["x"], k[1] - b["z"]) if math.hypot(k[0] - b["x"], k[1] - b["z"]) > 3 else 999)
    dx, dz = best[0] - b["x"], best[1] - b["z"]
    d = max(0.1, math.hypot(dx, dz))
    p.ustaw("ZT_TestSter", "Vector3.new(%f, %f, 4)" % (-dx / d, dz / d))
    ew, _ = czekaj(lambda: (p.atr().get("ZT_Ewolucji") or 0) >= 1, 7, 0.2)
    if zrzuty:
        p.zrzut("zj_ewolucja.jpg")
    wynik("Z12 ewolucja", bool(ew), forma=(moj_byt(p.serwer('"stan"')) or {}).get("forma"))
    # zjedzenie mniejszego bota
    p.serwer('"masa", 30')
    time.sleep(0.4)
    st = p.serwer('"stan"')
    b = moj_byt(st)
    bot = next(x for x in st["byty"] if x["slot"] == 0 and not x["martwy"] and not x["tarcza"])
    p.serwer('"bot_masa", %d, 4' % bot["id"])
    p.serwer('"bot_stoj", %d, 3' % bot["id"])
    p.serwer('"przenies", %d, %f, %f' % (bot["id"], b["x"] + 2, b["z"]))
    zj, _ = czekaj(lambda: (moj_byt(p.serwer('"stan"')) or {}).get("zjadl", 0) > b.get("zjadl", 0), 4, 0.2)
    wynik("Z13 zjadasz mniejszego", bool(zj), masa=(moj_byt(p.serwer('"stan"')) or {}).get("m"))
    # DASH
    p.serwer('"liczniki_zeruj"')
    p.ustaw("ZT_TestDash", "true")
    da, _ = czekaj(lambda: (p.serwer('"stan"').get("liczniki") or {}).get("dash", 0) >= 1 if isinstance(p.serwer('"stan"').get("liczniki"), dict) else False, 3)
    lk = p.serwer('"stan"').get("liczniki")
    wynik("Z14 DASH", bool(da), liczniki=lk if isinstance(lk, dict) else {})
    # zjedzony przez większego: pyk, po 2 s wracasz forma niżej z tarczą
    st = p.serwer('"stan"')
    b = moj_byt(st)
    forma0 = b["forma"]
    p.serwer('"tarcza_zeruj"')
    duzy = next(x for x in st["byty"] if x["slot"] == 0 and not x["martwy"] and x["id"] != bot["id"] and not x["tarcza"])
    p.serwer('"bot_masa", %d, 45' % duzy["id"])
    p.serwer('"bot_stoj", %d, 3' % duzy["id"])
    p.serwer('"przenies", %d, %f, %f' % (duzy["id"], b["x"] + 1, b["z"]))
    zjedzony, _ = czekaj(lambda: (p.atr().get("ZT_Zjedzen") or 0) >= 1, 5, 0.2)
    time.sleep(2.6)
    b2 = moj_byt(p.serwer('"stan"')) or {}
    wynik("Z15 zjedzony i powrót", bool(zjedzony) and not b2.get("martwy") and b2.get("tarcza") and b2.get("forma", 9) <= forma0,
          forma_przed=forma0, forma_po=b2.get("forma"), tarcza=b2.get("tarcza"))
    # czas klatki i kamera oddala się z rozmiarem
    a1 = p.atr()
    p.serwer('"masa", 30')
    time.sleep(2.0)
    a2 = p.atr()
    if zrzuty:
        p.zrzut("zj_duzy.jpg")
    wynik("Z16 klatka i kamera", (a2.get("ZT_Klatka") or 99) < 25 and (a2.get("ZT_KameraY") or 0) > (a1.get("ZT_KameraY") or 0) + 4,
          klatka_ms=round(a2.get("ZT_Klatka") or 0, 1), kamera_y=[round(a1.get("ZT_KameraY") or 0), round(a2.get("ZT_KameraY") or 0)],
          okno=a2.get("okno"), widokow=a2.get("ZT_Widokow"))
    # opóźnienie 2 × 60 ms: własny potwór rusza od razu
    p.luau('local n = settings().Network n.InboundNetworkMinDelayMs = 60 n.OutboundNetworkMinDelayMs = 60 return "ok"', "Server")
    try:
        time.sleep(0.8)
        a0 = p.atr()
        p.ustaw("ZT_TestSter", "Vector3.new(1, 0, 1.5)")
        time.sleep(0.15)
        a1 = p.atr()
        ruch = math.hypot((a1.get("ZT_MojX") or 0) - (a0.get("ZT_MojX") or 0), (a1.get("ZT_MojZ") or 0) - (a0.get("ZT_MojZ") or 0))
        time.sleep(1.5)
    finally:
        p.luau('local n = settings().Network n.InboundNetworkMinDelayMs = 0 n.OutboundNetworkMinDelayMs = 0 return "ok"', "Server")
    wynik("Z17 opóźnienie 120 ms", ruch > 0.5, ruch_po_015s=round(ruch, 2))


def zabawka2(p, zrzuty):
    t0 = time.time()
    p.akcja('"wybor"', "2")
    czekaj(lambda: p.atr().get("ZT_Tryb") == "z2", 5)
    a = p.atr()
    wynik("W20 wejście", a.get("ZT_Tryb") == "z2" and "Scriptable" in a.get("kamera", ""), tryb=a.get("ZT_Tryb"))
    time.sleep(1.0)
    if zrzuty:
        p.ustaw("ZT_TestCel", "Vector2.new(0.12, 0.45)")
        time.sleep(1.0)
        p.zrzut("wb_celowanie.jpg")
        p.ustaw("ZT_TestCel", "false")
    # pierwsze rzuty: celuj w najbliższy potwór (jak gracz) — z poprawką na ruch
    t_pierwszy = None
    for proba in range(6):
        st = p.serwer('"stan"')
        slot = st["slot"]
        zp = W["zagrodyPoz"][slot - 1]
        x0, z0 = zp[0], zp[1] + W["zagroda_gl"] / 2
        laka = [m for m in st["potwory"] if m["stan"] == "laka" and m["strefa"] == 1]
        m = min(laka, key=lambda q: math.hypot(q["x"] - x0, q["z"] - z0))
        dx, dz = m["x"] - x0, m["z"] - z0
        kat = math.atan2(dx, dz)
        zasieg = st["zasieg"]
        moc = (math.hypot(dx, dz) - W["zasieg_min"]) / (zasieg - W["zasieg_min"])
        p.ustaw("ZT_TestRzut", "Vector2.new(%f, %f)" % (kat, max(0.02, min(1, moc))))
        if t_pierwszy is None:
            t_pierwszy = time.time() - t0
        ok, _ = czekaj(lambda: (p.atr().get("ZT_Zwabien") or 0) >= 1, 2.5, 0.2)
        if ok:
            break
    a = p.atr()
    if zrzuty:
        time.sleep(0.2)
        p.zrzut("wb_zwabiony.jpg")
    wynik("W21 pierwszy rzut i zwabienie", (a.get("ZT_Zwabien") or 0) >= 1 and (a.get("ZT_Pierwsza") or 99) <= 15,
          pierwszy_rzut_s=round(t_pierwszy or 0, 1), pierwsze_zwabienie_s=round(a.get("ZT_Pierwsza") or 0, 1), prob=proba + 1)
    # pudło płoszy
    p.serwer('"liczniki_zeruj"')
    time.sleep(0.6)
    p.ustaw("ZT_TestRzut", "Vector2.new(-0.6, 0.02)")
    pu, _ = czekaj(lambda: (p.serwer('"stan"').get("liczniki") or {}).get("pudlo", 0) >= 1 if isinstance(p.serwer('"stan"').get("liczniki"), dict) else False, 4)
    wynik("W22 pudło", bool(pu))
    # odmiana GIANT (wymuszona) i scena
    p.serwer('"wymus_odmiane", "giant"')
    st = p.serwer('"stan"')
    m = next(q for q in st["potwory"] if q["stan"] == "laka" and q["strefa"] == 1)
    x, z_ = W["zagrodyPoz"][st["slot"] - 1][0], 40
    p.serwer('"potwor_tu", %d, %f, %f' % (m["id"], x, z_))
    zasieg = st["zasieg"]
    moc = (z_ - (W["zagrodyPoz"][st["slot"] - 1][1] + W["zagroda_gl"] / 2) - W["zasieg_min"]) / (zasieg - W["zasieg_min"])
    time.sleep(0.6)
    n0 = p.atr().get("ZT_Zwabien") or 0
    p.ustaw("ZT_TestRzut", "Vector2.new(0, %f)" % moc)
    gi, _ = czekaj(lambda: (p.atr().get("ZT_Zwabien") or 0) > n0, 4, 0.2)
    if zrzuty:
        time.sleep(0.3)
        p.zrzut("wb_giant.jpg")
    a = p.atr()
    wynik("W23 odmiana GIANT", bool(gi) and any(q.get("odm") == "giant" for q in p.serwer('"stan"')["potwory"]) and "GIANT" in (a.get("ZW_Najlepszy") or ""), najlepszy=a.get("ZW_Najlepszy"), ile=a.get("ZW_Ile"))
    # rzadki biegacz
    p.serwer('"liczniki_zeruj"')
    p.serwer('"rzadki_teraz"')
    rz, _ = czekaj(lambda: (p.serwer('"stan"').get("liczniki") or {}).get("rzadki", 0) >= 1 if isinstance(p.serwer('"stan"').get("liczniki"), dict) else False, 3)
    # zasięg rośnie ze zwabieniami
    p.serwer('"zwabione", 12')
    time.sleep(0.4)
    zs = p.atr().get("ZW_Zasieg")
    wynik("W24 rzadki i zasięg", bool(rz) and (zs or 0) >= W["strefy"][2]["od"], rzadki=bool(rz), zasieg_po_12=zs)
    time.sleep(1.5)
    a = p.atr()
    wynik("W25 klatka", (a.get("ZT_Klatka") or 99) < 25, klatka_ms=round(a.get("ZT_Klatka") or 0, 1), widokow=a.get("ZT_Widokow"))


def main():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio", required=True)
    ap.add_argument("--bez-zrzutow", action="store_true")
    ap.add_argument("--tylko", default=None)
    a = ap.parse_args()
    zrzuty = not a.bez_zrzutow
    with StudioMCP(timeout=240) as s:
        p = P(s, a.studio)
        if "Current Studio Mode: Edit" not in p.call("get_studio_state")["text"]:
            sys.exit("Studio nie jest w Edit")
        ed = json.loads(p.luau('local HS = game:GetService("HttpService") local k = workspace:FindFirstChild("%s") '
                               'local pa = workspace:FindFirstChild("PetArenaGra") return HS:JSONEncode({ jest = k ~= nil, '
                               'wzorce = k and #k.Wzorce:GetChildren() or 0, pa = pa and pa:GetAttribute("PetArenaWlaczony") })' % K, "Edit"))
        wynik("Z00 budowa", ed["jest"] and ed["wzorce"] == 12 and ed["pa"] is False, **ed)
        try:
            log("Play:", p.call("start_stop_play", {"is_start": True})["text"][:60])
            czekaj(lambda: p.luau('return tostring(workspace.%s:GetAttribute("KlientGotowy"))' % K, "Client") == "true", 60, 0.5)
            p.luau(BEZ_LISTY, "Client")
            time.sleep(1.5)
            a0 = p.atr()
            if zrzuty:
                p.zrzut("menu.jpg")
            wynik("Z01 menu, Pet Arena wyłączona", a0.get("menu") is True and a0.get("ZT_Tryb") == "menu" and not a0.get("pa_serwer")
                  and a0.get("pa_slot") is None, menu=a0.get("menu"), pa_serwer=a0.get("pa_serwer"), pa_slot=a0.get("pa_slot"), okno=a0.get("okno"))
            if a.tylko in (None, "1"):
                zabawka1(p, zrzuty)
                p.akcja('"menu"')
                time.sleep(0.8)
                wynik("Z30 MENU wraca", p.atr().get("menu") is True)
            if a.tylko in (None, "2"):
                zabawka2(p, zrzuty)
            kons = p.call("get_console_output")["text"]
            bledy = [l for l in kons.splitlines() if ("Zabawk" in l) and ("error" in l.lower() or "attempt" in l.lower() or "stack" in l.lower())]
            wynik("Z31 konsola", not bledy, bledy=bledy[:6])
        finally:
            log("Stop:", p.call("start_stop_play", {"is_start": False})["text"][:60])
            czekaj(lambda: "Current Studio Mode: Edit" in p.call("get_studio_state")["text"], 40, 0.5)
    ok = sum(wyniki.values())
    log("WYNIK: %d/%d OK%s" % (ok, len(wyniki), "" if ok == len(wyniki) else " — błędy: " + ", ".join(k for k, v in wyniki.items() if not v)))


if __name__ == "__main__":
    main()
