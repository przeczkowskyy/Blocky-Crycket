#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba Monster Evolution w trybie PLAY w Studio. Play / Stop wyłącznie przez `python -B tools/studio_mcp.py call
start_stop_play` (podproces; ta sama ścieżka co ręcznie, ze znacznikiem prób tools/zapis_prob.py).

    python -B swiat/ewolucja/testy/proba_play.py --studio <id> [--bez-zrzutow]

Wejście jak z palca: atrybuty lokalnego gracza (EW_TestSter, EW_TestPrzycisk, EW_TestAuto — autopilot klienta, który
gra jak człowiek widzący pole). Haczyki serwera: Sygnaly/SterowanieSerwera (tylko do ustawienia sytuacji: pełny pasek,
złoto, bot obok). Przed zrzutami lista graczy i czat schowane (bez nazwy konta).
"""
import argparse
import io
import json
import math
import os
import subprocess
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
K = D["kontener"]
KLATKI = os.path.join(PAKIET, "klatki")
SERWER = 'local HS = game:GetService("HttpService") return HS:JSONEncode(workspace.%s.Sygnaly.SterowanieSerwera:Invoke(%%s))' % K
ATR = ('local HS = game:GetService("HttpService") local p = game:GetService("Players").LocalPlayer local a = p:GetAttributes() '
       'a.kamera = tostring(workspace.CurrentCamera.CameraType) a.klient = workspace.%s:GetAttribute("KlientGotowy") '
       'local v = workspace.CurrentCamera.ViewportSize a.okno = { v.X, v.Y } '
       'for k, x in a do if typeof(x) == "Vector2" or typeof(x) == "Vector3" then a[k] = tostring(x) end end return HS:JSONEncode(a)') % K
BEZ_LISTY = ('local SG = game:GetService("StarterGui") pcall(function() SG:SetCoreGuiEnabled(Enum.CoreGuiType.PlayerList, false) '
             'SG:SetCoreGuiEnabled(Enum.CoreGuiType.Chat, false) end) return "ok"')
wyniki = {}
pomiary = {}


def log(*a):
    print("[%s]" % time.strftime("%H:%M:%S"), *a, flush=True)


def play(sid, start):
    """Play / Stop przez narzędzie wiersza poleceń (jedyna dozwolona ścieżka)."""
    r = subprocess.run([sys.executable, "-B", os.path.join(REPO, "tools", "studio_mcp.py"), "call", "start_stop_play", "--args",
                        json.dumps({"is_start": start, "studio_id": sid})], capture_output=True, text=True, encoding="utf-8", timeout=180)
    return (r.stdout + r.stderr).strip()


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

    def przycisk(self, co):
        self.ustaw("EW_TestPrzycisk", '"%s"' % co)

    def zrzut(self, nazwa):
        from PIL import Image
        r = self.call("screen_capture", {"capture_id": "ewolucja"}, timeout=120)
        if r["is_error"] or not r["images"]:
            log("zrzut nieudany:", (r["text"] or "")[:200])
            return
        img = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
        if img.width > 1600:
            img = img.resize((1600, int(img.height * 1600 / img.width)))
        os.makedirs(KLATKI, exist_ok=True)
        img.save(os.path.join(KLATKI, nazwa), quality=85)
        log("zrzut: swiat/ewolucja/klatki/" + nazwa)


def wynik(punkt, ok, **sz):
    wyniki[punkt] = bool(ok)
    log("%s %s %s" % (punkt, "OK  " if ok else "BŁĄD", json.dumps(sz, ensure_ascii=False)[:700]))


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


def moje(st):
    return next((b for b in st["byty"] if b["id"] == st.get("byt")), None)


def przebieg(p, zrzuty):
    # P01 start
    gotowe, t = czekaj(lambda: p.atr().get("klient") and p.atr().get("EW_Byt"), 30, 0.5)
    p.luau(BEZ_LISTY, "Client")
    time.sleep(1.0)
    a = p.atr()
    st = p.serwer('"stan"')
    wynik("P01 start", gotowe and a.get("EW_Forma") == 1 and "Scriptable" in a.get("kamera", "") and a.get("EW_K_Drabina") == "ZN?????C",
          forma=a.get("EW_Forma"), tarcza=st["tarcza"], drabina=a.get("EW_K_Drabina"), kamera=a.get("kamera"), gotowe_s=round(t, 1))
    if zrzuty:
        p.zrzut("01_start.jpg")
    # P02 bezpieczny start: przez 3 s żaden bot nie goni gracza (łaska nowicjusza, strefa startu), większy nie siedzi na graczu
    najbl, goni = 999, 0
    for _ in range(6):
        st = p.serwer('"stan"')
        ja = moje(st)
        najbl = min([najbl] + [math.hypot(b["x"] - ja["x"], b["z"] - ja["z"]) for b in st["byty"] if b["slot"] == 0 and b["forma"] > 1 and not b["martwy"]])
        goni += sum(1 for b in st["byty"] if b["slot"] == 0 and b.get("cel") == st["byt"])
        time.sleep(0.5)
    wynik("P02 bezpieczny start", goni == 0 and najbl > 10, najblizszy_wiekszy_st=round(najbl, 1), gonitw=goni, laska=st.get("laska"))
    # P03 jedzenie: autopilot jak gracz (kulki i mniejsi), bez EVOLVE — czas do pierwszej kulki i pełnego paska
    t0 = time.time()
    p.ustaw("EW_TestAuto", "true")
    pierwsza, _ = czekaj(lambda: p.atr().get("EW_K_Pierwsza"), 10, 0.3)
    if zrzuty:
        time.sleep(3)
        p.zrzut("02_jedzenie.jpg")
    pelny, tp = czekaj(lambda: (lambda x: (x.get("EW_Wzrost") or 0) >= (x.get("EW_Potrzeba") or 99))(p.atr()), 70, 0.5)
    pomiary["pelny_pasek_1_s"] = round(time.time() - t0, 1)
    wynik("P03 jedzenie do pełnego paska", pierwsza and pelny, pierwsza_kulka_s=round(pierwsza or -1, 1), pelny_pasek_s=pomiary["pelny_pasek_1_s"])
    # P04 EVOLVE z odsłoną (przycisk jak palec)
    p.ustaw("EW_TestAuto", "false")
    a0 = p.atr()
    p.przycisk("ewoluuj")
    kok, _ = czekaj(lambda: (moje(p.serwer('"stan"')) or {}).get("kokon"), 3, 0.15)
    if zrzuty:
        time.sleep(D["ewolucja"]["kokon_s"] + 0.25)
        p.zrzut("03_odslona.jpg")
    ew, _ = czekaj(lambda: p.atr().get("EW_Forma") == 2, 6, 0.3)
    a = p.atr()
    wynik("P04 ewolucja 1 z odsłoną", kok and ew and a.get("EW_K_Odslon") == 1 and a.get("EW_ZlotoNaS") == 3 and a.get("EW_K_Drabina") == "ZZN????C",
          kokon=bool(kok), forma=a.get("EW_Forma"), odslon=a.get("EW_K_Odslon"), na_s=a.get("EW_ZlotoNaS"), drabina=a.get("EW_K_Drabina"),
          przed=a0.get("EW_Forma"))
    # P05 druga ewolucja: autopilot z EVOLVE (naturalnie), najwyżej 75 s; potem haczyk pełnego paska
    t0 = time.time()
    p.ustaw("EW_TestAutoEvo", "true")
    p.ustaw("EW_TestAuto", "true")
    ew2, t2 = czekaj(lambda: p.atr().get("EW_Forma") == 3, 75, 0.5)
    pomiary["ewolucja_2_naturalnie_s"] = round(time.time() - t0, 1) if ew2 else None
    p.ustaw("EW_TestAuto", "false")
    p.ustaw("EW_TestAutoEvo", "false")
    if not ew2:
        p.serwer('"wzrost_pelny"')
        p.przycisk("ewoluuj")
        ew2, _ = czekaj(lambda: p.atr().get("EW_Forma") == 3, 6, 0.3)
    a = p.atr()
    time.sleep(1.7)
    wynik("P05 ewolucja 2 i drabina", ew2 and a.get("EW_K_Drabina") == "ZZZN???C" and a.get("EW_ZlotoNaS") == 7,
          naturalnie_s=pomiary["ewolucja_2_naturalnie_s"], forma=a.get("EW_Forma"), drabina=a.get("EW_K_Drabina"), na_s=a.get("EW_ZlotoNaS"))
    # P06 złoto z legowiska rośnie
    z0 = p.serwer('"stan"')["zloto"]
    time.sleep(3)
    st = p.serwer('"stan"')
    przyrost = st["zloto"] - z0
    wynik("P06 złoto legowiska", abs(przyrost - st["stawka"] * 3) < st["stawka"] * 1.2, przyrost_3s=round(przyrost, 1), stawka=st["stawka"])
    # P07 zakup ulepszenia w panelu legowiska
    p.serwer('"zloto", %d' % 650)
    time.sleep(0.4)
    p.przycisk("legowisko")
    time.sleep(0.6)
    if zrzuty:
        p.zrzut("04_legowisko.jpg")
    p.przycisk("kup:szybkosc")
    kup, _ = czekaj(lambda: p.atr().get("EW_Poz_szybkosc") == 2, 4, 0.3)
    st = p.serwer('"stan"')
    p.przycisk("zamknij")
    cena = D["ulepszenia"][1]["ceny"][0]
    wynik("P07 zakup (Szybkość)", kup and st["poziomy"]["szybkosc"] == 2 and 650 - cena - 1 <= st["zloto"] <= 650 - cena + 25,
          poziom=st["poziomy"]["szybkosc"], zloto_po=round(st["zloto"]), panel=p.atr().get("EW_K_Legowisko"))
    # P08 pościg i zjedzenie przez większego bota: forma niżej, legowisko / złoto / ulepszenia zostają
    st = p.serwer('"stan"')
    while st["forma"] < 3:  # gracz mógł zostać zjedzony w P05 — wróć do formy 3 (bez strefy startu i łaski nowicjusza)
        p.serwer('"wzrost_pelny"')
        p.przycisk("ewoluuj")
        czekaj(lambda: p.serwer('"stan"')["forma"] > st["forma"], 4, 0.3)
        st = p.serwer('"stan"')
    czekaj(lambda: (lambda x: x["strefy"] == 0 and not x["laska"])(p.serwer('"stan"')), 12, 0.5)
    st = p.serwer('"stan"')
    ja = moje(st)
    forma0, max0, zl0 = st["forma"], st["maxForma"], st["zloto"]
    smierci0 = p.serwer('"miary"').get("smierci", 0)
    p.serwer('"tarcza_zeruj"')
    bot = next(b for b in st["byty"] if b["slot"] == 0 and not b["martwy"] and b["forma"] >= forma0 + 2)
    p.serwer('"przenies", %d, %f, %f' % (bot["id"], ja["x"] + 11, ja["z"] - 9))
    time.sleep(0.3)
    if zrzuty:
        p.zrzut("05_pogon.jpg")
    cel = next((b.get("cel") for b in p.serwer('"stan"')["byty"] if b["id"] == bot["id"]), 0)
    st = p.serwer('"stan"')
    ja = moje(st)
    p.serwer('"przenies", %d, %f, %f' % (bot["id"], ja["x"] + 3, ja["z"]))
    zj, _ = czekaj(lambda: p.serwer('"miary"').get("smierci", 0) > smierci0, 5, 0.15)
    t_smierci = time.time()
    wrocil, _ = czekaj(lambda: not p.serwer('"stan"')["martwy"], 5, 0.2)
    st = p.serwer('"stan"')
    wynik("P08 zjedzony i powrót", zj and wrocil and st["forma"] == forma0 - 1 and st["tarcza"] and st["maxForma"] == max0 and st["zloto"] >= zl0
          and st["poziomy"]["szybkosc"] == 2, bot_gonil=cel == st["byt"], forma=[forma0, st["forma"]], tarcza=st["tarcza"], legowisko=st["maxForma"],
          zloto=[round(zl0), round(st["zloto"])], powrot_s=round(time.time() - t_smierci, 1))
    # P09 boty żyją i nie stoją przy miejscu odrodzenia (6 s)
    ja = moje(st)
    x0, z0, f = ja["x"], ja["z"], st["forma"]
    blisko_s, maks_blisko, min_zywych = 0.0, 0.0, 99
    t0 = time.time()
    while time.time() - t0 < 6:
        st = p.serwer('"stan"')
        boty = [b for b in st["byty"] if b["slot"] == 0]
        min_zywych = min(min_zywych, sum(1 for b in boty if not b["martwy"]))
        jest = any(math.hypot(b["x"] - x0, b["z"] - z0) < 20 and b["forma"] > f and not b["martwy"] for b in boty)
        blisko_s = blisko_s + 0.5 if jest else 0.0
        maks_blisko = max(maks_blisko, blisko_s)
        time.sleep(0.5)
    wynik("P09 boty żyją, bez czatowania przy starcie", min_zywych >= 20 and maks_blisko < 2, najmniej_zywych=min_zywych, botow=len(boty),
          wiekszy_przy_starcie_s=maks_blisko)
    # P10 miary w pamięci
    m = p.serwer('"miary"')
    wynik("P10 miary", m and m.get("smierci", 0) >= 1 and "2" in m.get("formy", {}) and "3" in m.get("formy", {}) and m.get("ulepszenia")
          and m.get("sesja_s", 0) > 30, miary=m)
    # P11 odpowiedź na wejście: bez opóźnienia i przy 2 × 60 ms
    p.ustaw("EW_TestPoz", "true")
    time.sleep(1.2)  # liczniki klienta publikowane co 1 s
    a0 = p.atr()
    p.ustaw("EW_TestSter", "Vector3.new(1, 0.3, 4)")
    time.sleep(4.2)
    a1 = p.atr()
    pomiary["bez_opoznienia"] = {"korekty": (a1.get("EW_K_Korekty") or 0) - (a0.get("EW_K_Korekty") or 0),
                                 "snapy": (a1.get("EW_K_Snapy") or 0) - (a0.get("EW_K_Snapy") or 0)}
    p.luau('local n = settings().Network n.InboundNetworkMinDelayMs = 60 n.OutboundNetworkMinDelayMs = 60 return "ok"', "Server")
    try:
        time.sleep(0.8)
        b0 = p.atr()
        p.ustaw("EW_TestSter", "Vector3.new(-1, -0.4, 4)")
        time.sleep(0.15)
        b1 = p.atr()
        ruch = math.hypot((b1.get("EW_K_PozX") or 0) - (b0.get("EW_K_PozX") or 0), (b1.get("EW_K_PozZ") or 0) - (b0.get("EW_K_PozZ") or 0))
        g0 = b1.get("EW_K_Gryzy") or 0
        p.przycisk("gryz")
        time.sleep(0.05)
        b2 = p.atr()
        time.sleep(4)
        b3 = p.atr()
    finally:
        p.luau('local n = settings().Network n.InboundNetworkMinDelayMs = 0 n.OutboundNetworkMinDelayMs = 0 return "ok"', "Server")
        p.ustaw("EW_TestPoz", "false")
    pomiary["opoznienie_120ms"] = {"ruch_po_015s_st": round(ruch, 2), "korekty": (b3.get("EW_K_Korekty") or 0) - (b0.get("EW_K_Korekty") or 0),
                                   "snapy": (b3.get("EW_K_Snapy") or 0) - (b0.get("EW_K_Snapy") or 0), "blad_maks_st": round(b3.get("EW_K_BladMaks") or 0, 2),
                                   "gryz_od_razu": (b2.get("EW_K_Gryzy") or 0) > g0}
    wynik("P11 odpowiedź na wejście", ruch > 0.5 and pomiary["bez_opoznienia"]["korekty"] == 0 and pomiary["opoznienie_120ms"]["korekty"] == 0
          and pomiary["opoznienie_120ms"]["snapy"] == 0 and pomiary["opoznienie_120ms"]["gryz_od_razu"], **pomiary["bez_opoznienia"],
          **{"lag_" + k: v for k, v in pomiary["opoznienie_120ms"].items()})
    # P12 klatka i liczba widoków
    a = p.atr()
    st = p.serwer('"stan"')
    las_i_boss(p, zrzuty)
    a = p.atr()
    wynik("P12 klatka", (a.get("EW_K_Klatka") or 99) < 25, klatka_ms=round(a.get("EW_K_Klatka") or 0, 1), widokow=a.get("EW_K_Widokow"),
          krok_serwera_ms=round(st.get("krok_ms") or 0, 2), okno=a.get("okno"), liczniki=st.get("liczniki"))


def las_i_boss(p, zrzuty):
    # P14 DEEP WOODS: brama otwiera się przy formie 4, gracz w lesie, boss z paskiem życia
    st = p.serwer('"stan"')
    while st["forma"] < 4:
        p.serwer('"wzrost_pelny"')
        p.przycisk("ewoluuj")
        czekaj(lambda: p.serwer('"stan"')["forma"] > st["forma"], 5, 0.3)
        st = p.serwer('"stan"')
    time.sleep(2.0)
    a = p.atr()
    B = p.serwer('"boss"')
    p.serwer('"boss_stoj", 3')
    p.serwer('"przenies", %d, %f, %f' % (st["byt"], B["x"] + 24, B["z"] - 10))
    time.sleep(1.2)
    st = p.serwer('"stan"')
    LS = D["las"]
    w_lesie = math.hypot(st["x"] - LS["x"], st["z"] - LS["z"]) < LS["r"]
    if zrzuty:
        p.zrzut("07_las.jpg")
    wynik("P14 DEEP WOODS", a.get("EW_K_Las") is True and st["maxForma"] >= 4 and w_lesie and B and not B["martwy"],
          las=a.get("EW_K_Las"), forma=st["forma"], w_lesie=w_lesie, boss_hp=B and B["hp"])
    # P15 mini-boss: BITE rani, pasek życia, pokonany → skrzynia i ogłoszenie
    B = p.serwer('"boss"')
    zl0 = p.serwer('"stan"')["zloto"]
    r = D["formy"][st["forma"] - 1]["r"] + D["formy"][D["boss"]["forma"] - 1]["r"] + 1.5
    p.serwer('"boss_hp", 120')
    p.serwer('"boss_stoj", 4')
    p.serwer('"tarcza_zeruj"')
    p.serwer('"przenies", %d, %f, %f' % (st["byt"], B["x"] + r, B["z"]))
    time.sleep(0.5)
    p.przycisk("gryz")
    rana, _ = czekaj(lambda: p.serwer('"boss"')["hp"] < 120, 3, 0.2)
    time.sleep(0.4)
    if zrzuty:
        p.zrzut("08_boss.jpg")
    pok = None
    for _ in range(4):
        p.serwer('"boss_hp", 3')
        p.serwer('"boss_stoj", 3')
        B = p.serwer('"boss"')
        p.serwer('"przenies", %d, %f, %f' % (st["byt"], B["x"] + r, B["z"]))
        time.sleep(0.9)
        p.przycisk("gryz")
        pok, _ = czekaj(lambda: p.serwer('"boss"')["martwy"], 1.5, 0.2)
        if pok:
            break
    st2 = p.serwer('"stan"')
    m = p.serwer('"miary"')
    wynik("P15 mini-boss", rana and pok and st2["zloto"] - zl0 >= D["boss"]["skrzynia"] and m.get("boss_pokonany"), rana=bool(rana), pokonany=bool(pok),
          zloto=[round(zl0), round(st2["zloto"])], miara_boss_s=m.get("boss_pokonany"), miara_las_s=m.get("las"))


def bledy_konsoli(p):
    r = p.call("get_console_output", {}, timeout=60)
    t = r["text"] or ""
    zle = [l for l in t.splitlines() if ("error" in l.lower() or "Stack" in l or "attempt to" in l) and "zapis_prob" not in l]
    return zle, t


def main():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio", required=True)
    ap.add_argument("--bez-zrzutow", action="store_true")
    a = ap.parse_args()
    with StudioMCP(timeout=180) as s:
        p = P(s, a.studio)
        if "Current Studio Mode: Edit" not in p.call("get_studio_state")["text"]:
            log("PRZERWANO — Studio nie jest w trybie Edit")
            return 1
        log("Play:", play(a.studio, True)[-80:])
        try:
            przebieg(p, not a.bez_zrzutow)
        except Exception as e:  # noqa: BLE001
            log("PRZERWANO próbę:", repr(e)[:800])
            wyniki["wyjątek"] = False
        finally:
            zle, _ = bledy_konsoli(p)
            wynik("P13 konsola bez błędów", not zle, bledy=zle[:12])
            log("Stop:", play(a.studio, False)[-80:])
            czekaj(lambda: "Current Studio Mode: Edit" in p.call("get_studio_state")["text"], 40, 0.5)
    ok = sum(1 for v in wyniki.values() if v)
    log("WYNIK: %d/%d OK; pomiary: %s" % (ok, len(wyniki), json.dumps(pomiary, ensure_ascii=False)))
    return 0 if ok == len(wyniki) else 1


if __name__ == "__main__":
    sys.exit(main())
