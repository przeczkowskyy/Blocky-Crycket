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
    # P48 ekran powitania przy wejściu (seria, nagroda dnia, zadania), zamknięty przed resztą prób
    pw, _ = czekaj(lambda: p.atr().get("EW_K_Powitanie"), 8, 0.3)
    time.sleep(0.6)
    if zrzuty:
        p.zrzut("41_powitanie.jpg")
    zl0 = json.loads(p.atr().get("EW_Zadania") or "[]")
    wynik("P48 powitanie: seria i zadania", pw is not None and pw >= 1 and len(zl0) == D["zadania"]["ile"], seria=pw, zadania=[q["id"] for q in zl0])
    p.przycisk("powitanie_zamknij")
    time.sleep(0.3)
    a = p.atr()
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
    if D.get("swiat"):
        swiat(p, zrzuty)
    # P03 jedzenie: autopilot jak gracz (kulki i mniejsi), bez EVOLVE — czas do pierwszej kulki i pełnego paska
    t0 = time.time()
    p.ustaw("EW_TestAuto", "true")
    pierwsza, _ = czekaj(lambda: p.atr().get("EW_K_Pierwsza"), 20, 0.3)
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
    wynik("P04 ewolucja 1 z odsłoną", kok and ew and a.get("EW_K_Odslon") == 1 and (a.get("EW_ZlotoNaS") or 0) >= 3 and a.get("EW_K_Drabina") == "ZZN????C",
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
    for _ in range(3):
        if ew2:
            break
        czekaj(lambda: not (moje(p.serwer('"stan"')) or {}).get("martwy"), 5, 0.3)
        p.serwer('"hp", nil, 9000')
        p.serwer('"wzrost_pelny"')
        time.sleep(0.4)
        p.przycisk("ewoluuj")
        ew2, _ = czekaj(lambda: p.atr().get("EW_Forma") == 3, 6, 0.3)
    a = p.atr()
    time.sleep(1.7)
    wynik("P05 ewolucja 2 i drabina", ew2 and a.get("EW_K_Drabina") == "ZZZN???C" and (a.get("EW_ZlotoNaS") or 0) >= 7,
          naturalnie_s=pomiary["ewolucja_2_naturalnie_s"], forma=a.get("EW_Forma"), drabina=a.get("EW_K_Drabina"), na_s=a.get("EW_ZlotoNaS"))
    # P06 złoto z legowiska rośnie (w legowisku; zbiera się przez wejście)
    st = p.serwer('"stan"')
    p.serwer('"przenies", %d, 0, -30' % st["byt"])
    p.serwer('"hp", nil, 5000')  # pomiar złota nie może przerwać zjedzenie (odrodzenie w legowisku zbiera złoto)
    time.sleep(0.4)
    z0 = p.serwer('"stan"')["zlotoLeg"]
    time.sleep(3)
    st = p.serwer('"stan"')
    przyrost = st["zlotoLeg"] - z0
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
    wynik("P07 zakup (Szybkość)", kup and st["poziomy"]["szybkosc"] == 2 and 650 - cena - 1 <= st["zloto"] <= 650 - cena + 200,
          poziom=st["poziomy"]["szybkosc"], zloto_po=round(st["zloto"]), panel=p.atr().get("EW_K_Legowisko"))
    # P08 pościg i zjedzenie przez większego bota: forma niżej, legowisko / złoto / ulepszenia zostają
    st = p.serwer('"stan"')
    for _ in range(6):  # gracz mógł zostać zjedzony w P05 — wróć do formy 3 (bez strefy startu i łaski nowicjusza)
        if st["forma"] >= 3:
            break
        p.serwer('"wzrost_pelny"')
        p.przycisk("ewoluuj")
        czekaj(lambda: p.serwer('"stan"')["forma"] > st["forma"], 4, 0.3)
        st = p.serwer('"stan"')
    czekaj(lambda: (lambda x: x["strefy"] == 0 and not x["laska"])(p.serwer('"stan"')), 12, 0.5)
    st = p.serwer('"stan"')
    p.serwer('"przenies", %d, 0, -30' % st["byt"])  # poza legowiskiem (tam nikt nie zje)
    p.serwer('"hp", nil, 5000')  # do chwili próby nikt przypadkiem nie zje gracza
    time.sleep(0.6)
    st = p.serwer('"stan"')
    ja = moje(st)
    forma0, max0, zl0 = st["forma"], st["maxForma"], st["zloto"]
    smierci0 = p.serwer('"miary"').get("smierci", 0)
    p.serwer('"tarcza_zeruj"')
    bot = next(b for b in st["byty"] if b["slot"] == 0 and not b["martwy"] and b["forma"] >= forma0 + 2 and b.get("strefa") == 1)
    p.serwer('"przenies", %d, %f, %f' % (bot["id"], ja["x"] + 11, ja["z"] - 9))
    time.sleep(0.3)
    if zrzuty:
        p.zrzut("05_pogon.jpg")
    cel = next((b.get("cel") for b in p.serwer('"stan"')["byty"] if b["id"] == bot["id"]), 0)
    st = p.serwer('"stan"')
    ja = moje(st)
    p.serwer('"laska_zeruj"')
    p.serwer('"tarcza_zeruj"')
    p.serwer('"bot_stoj", %d, 3' % bot["id"])
    smierci0 = p.serwer('"miary"').get("smierci", 0)
    p.serwer('"hp", nil, 1')  # walka1: zjada się przez życie — jeden punkt, bot gryzie z bliska
    p.serwer('"bot_cel", %d, %d' % (bot["id"], st["byt"]))
    p.serwer('"przenies", %d, %f, %f' % (bot["id"], ja["x"] + D["formy"][bot["forma"] - 1]["r"] + D["formy"][forma0 - 1]["r"] + 0.5, ja["z"]))
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
    # P11 odpowiedź na wejście: bez opóźnienia i przy 2 × 60 ms (start z otwartego miejsca łąki)
    p.serwer('"przenies", %d, 0, -30' % p.serwer('"stan"')["byt"])
    time.sleep(1.0)
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
                                   "gryz_od_razu": (b2.get("EW_K_Gryzy") or 0) > g0, "flagi": b1.get("EW_K_Flagi"), "odslona": b1.get("EW_K_Odslona"),
                                   "ster": b1.get("EW_K_Ster"), "poz": [round(b0.get("EW_K_PozX") or 0), round(b0.get("EW_K_PozZ") or 0)]}
    wynik("P11 odpowiedź na wejście", ruch > 0.5 and pomiary["bez_opoznienia"]["korekty"] == 0 and pomiary["opoznienie_120ms"]["korekty"] == 0
          and pomiary["opoznienie_120ms"]["snapy"] == 0 and pomiary["opoznienie_120ms"]["gryz_od_razu"], **pomiary["bez_opoznienia"],
          **{"lag_" + k: v for k, v in pomiary["opoznienie_120ms"].items()})
    # P12 klatka i liczba widoków
    a = p.atr()
    st = p.serwer('"stan"')
    las_i_boss(p, zrzuty)
    etap3(p, zrzuty)
    pomiar(p)
    walka(p, zrzuty)
    interfejs(p, zrzuty)
    odrodzenie_proby(p, zrzuty)
    retencja_proby(p, zrzuty)
    odczucie_proby(p, zrzuty)
    a = p.atr()
    wynik("P12 klatka", (a.get("EW_K_Klatka") or 99) < 25, klatka_ms=round(a.get("EW_K_Klatka") or 0, 1), praca_skryptu_ms=round(a.get("EW_K_Praca") or 0, 2),
          czesci_smokow=a.get("EW_K_CzesciSmokow"), rigi=a.get("EW_K_Rigi"), widokow=a.get("EW_K_Widokow"),
          krok_serwera_ms=round(st.get("krok_ms") or 0, 2), okno=a.get("okno"), liczniki=st.get("liczniki"))


def swiat(p, zrzuty):
    """swiat1: legowisko z rekwizytami i wyjście na łąkę, owca zjedzona, boty nie wchodzą w przeszkody, sztandar w kolorze."""
    st = p.serwer('"stan"')
    byt, slot = st["byt"], st.get("slot") or 1
    lx, lz = D["legowiska"][slot - 1]
    if zrzuty:
        p.zrzut("24_legowisko_blisko.jpg")
    kol = D["swiat"]["kolory_legowisk"][(slot - 1) % len(D["swiat"]["kolory_legowisk"])]
    szt = p.luau('local m = workspace.%s.Scena.Swiat.legowisko:FindFirstChild("sztandar_%d") if not m then return "brak" end '
                 'for _, d in m:GetDescendants() do if d:IsA("BasePart") and d:GetAttribute("Region") == 0 then return d.Color:ToHex() end end '
                 'return "bez regionu"' % (K, slot), "Client")
    rek = p.luau('local s = workspace.%s.Scena.Swiat local n = 0 for _, d in s:GetDescendants() do if d:IsA("BasePart") then n += 1 end end '
                 'return n' % K, "Server")
    # wyjście: pisklę idzie z miejsca wyklucia prosto na środek łąki przez wejście legowiska (5 s)
    p.serwer('"laska_zeruj"')
    p.serwer('"boty_cisza", 8')  # próba drogi wyjścia, nie bezpieczeństwa (to P02): boty bez ciosów na 8 s
    p.ustaw("EW_TestSter", "Vector3.new(%f, %f, 5)" % (lx / 126.0, -lz / 126.0))
    time.sleep(5.3)
    st2 = p.serwer('"stan"')
    ja = moje(st2)
    od = math.hypot(ja["x"] - lx, ja["z"] - lz)
    if zrzuty:
        p.zrzut("23_laka.jpg")
    wynik("P31 legowisko z rekwizytami i wyjście na łąkę", szt.lower() == kol.lower() and int(rek) > 2000 and od > 30 and not st2["martwy"],
          sztandar=szt, kolor_wlasciciela=kol, czesci_swiata=int(rek), od_srodka_legowiska=round(od, 1))
    # P32 owca: podejście i zjedzenie dotykiem (wzrost jak duża kulka)
    k0 = p.atr().get("EW_K_Owce") or 0
    w0 = st2["wzrost"]
    zj = False
    for _ in range(4):
        ow = [o for o in p.serwer('"stan"').get("owce", []) if not o["martwa"]]
        if not ow:
            time.sleep(1.0)
            continue
        o = min(ow, key=lambda q: math.hypot(q["x"], q["z"]))
        p.serwer('"przenies", %d, %f, %f' % (byt, o["x"] + 0.4, o["z"]))
        zj, _ = czekaj(lambda: (p.atr().get("EW_K_Owce") or 0) > k0, 2.0, 0.2)
        if zj:
            break
    st3 = p.serwer('"stan"')
    time.sleep(1.2)
    a = p.atr()
    wynik("P32 owca zjedzona", zj and (a.get("EW_K_Owce") or 0) >= 1 and st3["wzrost"] > w0, owiec=len(st2.get("owce", [])),
          zjedzone_serwer=st3["liczniki"].get("owca"), zjedzone_klient=a.get("EW_K_Owce"), wzrost=[round(w0), round(st3["wzrost"])])
    # P33 boty omijają przeszkody (głazy, pnie, kręgi legowisk, znaki): 4 próbki co 1 s, żaden bot w środku przeszkody
    blok = [q for q in D["przeszkody"] if q["typ"] != "staw"]
    w_srodku, probek = [], 0
    for _ in range(4):
        st4 = p.serwer('"stan"')
        for b in st4["byty"]:
            if b["slot"] == 0 and not b["martwy"] and b.get("strefa") is not None:
                r = D["formy"][b["forma"] - 1]["r"]
                probek += 1
                for q in blok:
                    if math.hypot(b["x"] - q["x"], b["z"] - q["z"]) < q["r"] + r * 0.7 - 1.0:
                        w_srodku.append((b["id"], q.get("rid"), round(math.hypot(b["x"] - q["x"], b["z"] - q["z"]), 1)))
        time.sleep(1.0)
    wynik("P33 boty nie przechodzą przez przeszkody", probek > 50 and not w_srodku, probek=probek, w_przeszkodzie=w_srodku[:6], przeszkod=len(blok))
    if zrzuty:
        p.serwer('"przenies", %d, -44, 30' % byt)
        time.sleep(1.2)
        p.zrzut("26_czaszka.jpg")
    p.serwer('"przenies", %d, %f, %f' % (byt, lx * 0.97, lz * 0.97))
    time.sleep(0.5)


def las_i_boss(p, zrzuty):
    # P14 DEEP WOODS: brama otwiera się przy formie 4, gracz w lesie, boss z paskiem życia
    st = p.serwer('"stan"')
    for _ in range(6):
        if st["forma"] >= 4:
            break
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
    r = D["formy"][st["forma"] - 1]["r"] + D["formy"][D["boss"]["forma"] - 1]["r"] - 0.5
    p.serwer('"boss_hp", 120')
    p.serwer('"boss_stoj", 4')
    p.serwer('"tarcza_zeruj"')
    p.serwer('"hp", nil, 9000')  # boty lasu nie przerwą próby
    rana = None
    for _ in range(5):
        B = p.serwer('"boss"')
        p.serwer('"boss_stoj", 4')
        p.serwer('"przenies", %d, %f, %f' % (st["byt"], B["x"] + r, B["z"]))
        p.ustaw("EW_TestSter", "Vector3.new(1, 0, 0.35)")
        time.sleep(0.6)
        p.przycisk("odnowa_zeruj")
        p.przycisk("gryz")
        rana, _ = czekaj(lambda: p.serwer('"boss"')["hp"] < 120, 1.5, 0.2)
        if rana:
            break
    time.sleep(0.4)
    if zrzuty:
        p.zrzut("08_boss.jpg")
    pok = None
    for _ in range(6):
        p.serwer('"boss_hp", 3')
        p.serwer('"boss_stoj", 3')
        B = p.serwer('"boss"')
        p.serwer('"przenies", %d, %f, %f' % (st["byt"], B["x"] + r, B["z"]))
        p.ustaw("EW_TestSter", "Vector3.new(1, 0, 0.35)")
        time.sleep(0.9)
        p.przycisk("odnowa_zeruj")
        p.przycisk("gryz")
        pok, _ = czekaj(lambda: p.serwer('"boss"')["martwy"], 1.5, 0.2)
        if pok:
            break
    st2 = p.serwer('"stan"')
    m = p.serwer('"miary"')
    wynik("P15 mini-boss", rana and pok and st2["zloto"] - zl0 >= D["boss"]["skrzynia"] and m.get("boss_pokonany"), rana=bool(rana), pokonany=bool(pok),
          zloto=[round(zl0), round(st2["zloto"])], miara_boss_s=m.get("boss_pokonany"), miara_las_s=m.get("las"))


def etap3(p, zrzuty):
    st = p.serwer('"stan"')
    byt = st["byt"]
    lx, lz = D["legowiska"][(st.get("slot") or 1) - 1] if st.get("slot") else D["legowiska"][0]
    # P16 legowisko w świecie: trofea na cokołach, kupka złota, zbieranie przez wejście, strefa bezpieczna
    p.serwer('"zloto_leg", 800')
    zl0 = p.serwer('"stan"')["zloto"]
    p.serwer('"przenies", %d, %f, %f' % (byt, lx * 0.8, lz * 0.8))
    time.sleep(1.5)
    if zrzuty:
        p.zrzut("09_legowisko_swiat.jpg")
    a0 = p.atr()
    p.serwer('"do_legowiska"')
    zeb, _ = czekaj(lambda: p.serwer('"stan"')["zloto"] >= zl0 + 790, 4, 0.3)
    st = p.serwer('"stan"')
    bot = next(b for b in st["byty"] if b["slot"] == 0 and not b["martwy"] and b["forma"] > st["forma"] and b.get("strefa") == 1)
    p.serwer('"tarcza_zeruj"')
    p.serwer('"przenies", %d, %f, %f' % (bot["id"], lx + 2, lz))
    time.sleep(1.5)
    st2 = p.serwer('"stan"')
    botb = next(b for b in st2["byty"] if b["id"] == bot["id"])
    wynik("P16 legowisko w świecie", zeb and not st2["martwy"] and math.hypot(botb["x"] - lx, botb["z"] - lz) > D["legowisko"]["r"] - 0.5
          and (a0.get("EW_K_Legowisk") or 0) >= 1, zebrano=bool(zeb), zjedzony_w_legowisku=st2["martwy"],
          bot_od_srodka=round(math.hypot(botb["x"] - lx, botb["z"] - lz), 1), legowisk_u_klienta=a0.get("EW_K_Legowisk"))
    # P17 poziom trofeum (w legowisku, za zebrane złoto)
    p.serwer('"zloto", 5000')
    p.przycisk("trofeum:1")
    lv, _ = czekaj(lambda: (p.atr().get("EW_Trofea") or "").startswith("2,"), 4, 0.3)
    st = p.serwer('"stan"')
    wynik("P17 poziom trofeum", lv and st["zloto"] <= 5000 - D["legowisko"]["ceny_x"][0] * D["formy"][0]["trofeum"] + 30,
          trofea=p.atr().get("EW_Trofea"), zloto=round(st["zloto"]))
    # P18 wariant przy ewolucji (wymuszony los serwera, kokon w kolorze, odsłona)
    p.serwer('"przenies", %d, 0, -30' % byt)
    p.serwer('"wymus_wariant", "zloty"')
    p.serwer('"wzrost_pelny"')
    p.przycisk("ewoluuj")
    wa, _ = czekaj(lambda: p.atr().get("EW_K_Wariant") == "zloty", 5, 0.15)
    if zrzuty:
        time.sleep(0.25)
        p.zrzut("10_wariant.jpg")
    a = p.atr()
    wynik("P18 wariant", wa and "zloty" in (a.get("EW_Warianty") or ""), warianty=a.get("EW_Warianty"), forma=a.get("EW_Forma"),
          na_s=a.get("EW_ZlotoNaS"))
    # P19 boss stopień 3: pasek z gwiazdkami, pokonany → trofeum bossa
    for _ in range(4):
        st = p.serwer('"stan"')
        if st["forma"] >= 6:
            break
        p.serwer('"wzrost_pelny"')
        p.przycisk("ewoluuj")
        czekaj(lambda: p.serwer('"stan"')["forma"] > st["forma"], 5, 0.3)
    time.sleep(1.5)
    p.serwer('"boss_stopien", 3')
    B = p.serwer('"boss"')
    p.serwer('"boss_stoj", 6')
    st = p.serwer('"stan"')
    r = D["formy"][st["forma"] - 1]["r"] + D["formy"][D["boss"]["forma"] - 1]["r"] - 0.5
    p.serwer('"tarcza_zeruj"')
    p.serwer('"przenies", %d, %f, %f' % (byt, B["x"] + r, B["z"]))
    time.sleep(0.8)
    p.przycisk("gryz")
    time.sleep(0.6)
    if zrzuty:
        p.zrzut("11_boss_stopien.jpg")
    pok = None
    for _ in range(6):
        p.serwer('"boss_hp", 3')
        p.serwer('"boss_stoj", 3')
        B = p.serwer('"boss"')
        p.serwer('"przenies", %d, %f, %f' % (byt, B["x"] + r, B["z"]))
        time.sleep(0.9)
        p.przycisk("gryz")
        pok, _ = czekaj(lambda: p.serwer('"boss"')["martwy"], 1.5, 0.2)
        if pok:
            break
    time.sleep(0.8)
    a = p.atr()
    m = p.serwer('"miary"')
    wynik("P19 boss stopień 3", pok and (a.get("EW_BossTrofea") or 0) >= 3 and m.get("boss_stopien_3"), boss_trofea=a.get("EW_BossTrofea"),
          miara=m.get("boss_stopien_3"))
    # P20 Olbrzym: korona (z jednym graczem bez bossa serwera), zrzut
    p.serwer('"forma_gracza", %d' % len(D["formy"]))
    p.serwer('"przenies", %d, 20, -40' % byt)
    p.serwer('"hp", nil, 9000')
    time.sleep(2.0)
    if zrzuty:
        p.zrzut("12_olbrzym.jpg")
    a = p.atr()
    st = p.serwer('"stan"')
    wynik("P20 Olbrzym", st["forma"] == len(D["formy"]) and a.get("EW_K_Korona") is True, forma=st["forma"], atr_forma=a.get("EW_Forma"),
          korona=a.get("EW_K_Korona"), martwy=st["martwy"], kokon=st.get("kokon"), olbrzym=st.get("olbrzymId") == st["byt"])
    # P21 wyjście i powrót po godzinie: stan z zapisu (magazyn w pamięci), złoto legowiska za nieobecność
    w = p.serwer('"wyjdz_wroc", 3600')
    time.sleep(1.0)
    a = p.atr()
    prz, po = (w or {}).get("przed", {}), (w or {}).get("po", {})
    oczek = prz.get("zlotoLeg", 0) + prz.get("stawka", 0) * 3600
    wynik("P21 wyjście i powrót", w and w.get("zapisano") and w.get("magazyn") == "pamiec" and po.get("forma") == 1 and po.get("zloto") == prz.get("zloto")
          and po.get("maxForma") == prz.get("maxForma") and po.get("poziomy") == prz.get("poziomy") and abs(po.get("zlotoLeg", 0) - oczek) < 2
          and (a.get("EW_K_Powrot") or 0) > 0, magazyn=w and w.get("magazyn"), przed=prz, po=po, powrot_u_klienta=a.get("EW_K_Powrot"))


def bot_obok(p, st, forma, dx, dz, strefa=1):
    """Najbliższy żywy bot łąki: forma ustawiona, postawiony obok gracza (dx, dz od środka gracza), stoi."""
    ja = moje(st)
    boty = sorted((b for b in st["byty"] if b["slot"] == 0 and not b["martwy"] and b.get("strefa") == strefa),
                  key=lambda b: math.hypot(b["x"] - ja["x"], b["z"] - ja["z"]))
    b = boty[0]
    p.serwer('"bot_forma", %d, %d' % (b["id"], forma))
    p.serwer('"bot_stoj", %d, 8' % b["id"])
    p.serwer('"przenies", %d, %f, %f' % (b["id"], ja["x"] + dx, ja["z"] + dz))
    p.serwer('"hp", %d, 999' % b["id"])
    return b["id"]


def walka(p, zrzuty):
    """walka1: przyciski i sylwetki, łańcuch BITE, FIRE, POWER (szybowanie na SKY NEST, meteor), boty ze zdolnościami."""
    st = p.serwer('"stan"')
    byt = st["byt"]
    time.sleep(1.2)
    a = p.atr()
    zd = json.loads(a.get("EW_K_Zd") or "{}")
    o, m = zd.get("ogien", {}), zd.get("moc", {})
    wynik("P23 FIRE i POWER zamknięte na stadium 1", st["forma"] == 1 and o.get("zamkniete") and m.get("zamkniete") and o.get("od", "").startswith("at ")
          and m.get("od", "").startswith("at "), ogien=o, moc=m)
    # P24 łańcuch BITE: trzy ciosy, rany u celu, trzeci odrzuca (bot o tym samym stadium)
    p.serwer('"forma_gracza", 3')
    p.serwer('"przenies", %d, 0, -20' % byt)
    p.serwer('"laska_zeruj"')
    time.sleep(1.0)
    p.serwer('"tarcza_zeruj"')
    p.serwer('"hp", nil, 5000')  # próba: gracz nie ginie od odwetu i botów wokół
    st = p.serwer('"stan"')
    r3 = D["formy"][2]["r"]
    bid = bot_obok(p, st, 3, -(2 * r3 + 1.0), 0)
    p.serwer('"hp", %d, 5000' % bid)  # manekin: nie zginie od innych stworków w ruchliwym świecie
    p.serwer('"bot_cisza", %d, 6' % bid)  # manekin: bez odwetu (przewrót przerwałby łańcuch)
    p.ustaw("EW_TestSter", "Vector3.new(1, 0, 0.15)")
    time.sleep(0.4)
    a0 = p.atr()
    for _ in range(3):
        p.przycisk("gryz")
        time.sleep(0.62)
    time.sleep(0.15)
    if zrzuty:
        p.zrzut("14_walka_gryzienie.jpg")
    a1 = p.atr()
    wi = p.serwer('"walka_info", %d' % bid)
    ja = p.serwer('"walka_info"')
    rany = (a1.get("EW_K_RanyZad") or 0) - (a0.get("EW_K_RanyZad") or 0)
    # klipy zdolności stadium 3: EMBER SPIT (splun) i TAIL SWEEP (ogon_zamach)
    p.przycisk("ogien")
    time.sleep(0.9)
    p.przycisk("moc")
    time.sleep(0.9)
    wynik("P24 łańcuch BITE", rany >= 3 and ja and ja.get("lancuch") == 3 and wi and wi["hp"] < 5000, rany_zadane=rany, lancuch=ja and ja.get("lancuch"),
          hp_celu=wi and round(wi["hp"]), efekty=a1.get("EW_K_Efekty"))
    # P25 FIRE: stadium 4, FIRE BREATH w bota przed pyskiem (kanał, rany co tik)
    p.serwer('"forma_gracza", 4')
    p.serwer('"przenies", %d, 10, -15' % byt)
    time.sleep(0.8)
    p.serwer('"tarcza_zeruj"')
    p.serwer('"zdolnosci_zeruj"')
    p.serwer('"hp", nil, 5000')
    st = p.serwer('"stan"')
    r4 = D["formy"][3]["r"]
    bid = bot_obok(p, st, 3, 0, r4 + D["formy"][2]["r"] + 5)
    p.serwer('"hp", %d, 5000' % bid)
    p.serwer('"bot_cisza", %d, 6' % bid)
    p.ustaw("EW_TestSter", "Vector3.new(0, 1, 0.25)")
    time.sleep(0.35)
    a0 = p.atr()
    l0 = p.serwer('"stan"')["liczniki"]
    p.przycisk("ogien")
    time.sleep(1.0)
    if zrzuty:
        p.zrzut("15_ogien.jpg")
    time.sleep(1.4)
    a1 = p.atr()
    l1 = p.serwer('"stan"')["liczniki"]
    wi = p.serwer('"walka_info", %d' % bid)
    zd = json.loads(a1.get("EW_K_Zd") or "{}")
    wynik("P25 FIRE BREATH", (a1.get("EW_K_Zamachy") or 0) > (a0.get("EW_K_Zamachy") or 0) and (l1.get("oddech") or 0) > (l0.get("oddech") or 0)
          and wi and wi["hp"] < 5000 and zd.get("ogien", {}).get("nazwa") == "oddech" and zd.get("ogien", {}).get("pigulka"),
          zamachy=a1.get("EW_K_Zamachy"), oddechy=l1.get("oddech"), hp_celu=wi and round(wi["hp"]), przycisk=zd.get("ogien"))
    # P26 POWER: stadium 5, WING GLIDE nad fosą lawy na SKY NEST
    WY = D["wyspa"]
    p.serwer('"forma_gracza", 5')
    p.serwer('"zdolnosci_zeruj"')
    p.serwer('"przenies", %d, %f, %f' % (byt, WY["x"], WY["z"] - WY["r_zew"] - 7))
    time.sleep(0.8)
    p.serwer('"hp", nil, 5000')
    p.ustaw("EW_TestSter", "Vector3.new(0, 1, 0.3)")
    time.sleep(0.25)
    t_lot = time.time()
    p.przycisk("moc")
    if zrzuty:
        time.sleep(0.45)
        p.zrzut("18_szybowanie.jpg")
    wysp, _ = czekaj(lambda: p.serwer('"walka_info"').get("naWyspie"), 4, 0.25)
    time.sleep(0.6)
    if zrzuty:
        p.zrzut("25_wyspa_lawy.jpg")
    st = p.serwer('"stan"')
    wynik("P26 WING GLIDE na SKY NEST", wysp and not st["martwy"], na_wyspie=bool(wysp), x=round(st["x"], 1), z=round(st["z"], 1))
    # P27 POWER: stadium 8, METEOR DIVE w grupę botów (wybuch przy lądowaniu)
    p.serwer('"forma_gracza", %d' % len(D["formy"]))
    p.serwer('"zdolnosci_zeruj"')
    p.serwer('"przenies", %d, 30, -10' % byt)
    time.sleep(1.0)
    p.serwer('"tarcza_zeruj"')
    p.serwer('"hp", nil, 9000')
    time.sleep(max(0.0, 6.6 - (time.time() - t_lot)))  # odnowa POWER u klienta (po szybowaniu)
    st = p.serwer('"stan"')
    A = D["zdolnosci"]["moc"][-1]
    ids = []
    ja = moje(st)
    boty = sorted((b for b in st["byty"] if b["slot"] == 0 and not b["martwy"] and b.get("strefa") == 1),
                  key=lambda b: math.hypot(b["x"] - ja["x"], b["z"] - ja["z"]))[:3]
    for b, (dx, dz) in zip(boty, ((0, 0), (6, 3), (-6, 2))):
        p.serwer('"bot_stoj", %d, 8' % b["id"])
        p.serwer('"przenies", %d, %f, %f' % (b["id"], ja["x"] + dx, ja["z"] + A["d"] + dz))
        p.serwer('"hp", %d, 999' % b["id"])
        ids.append(b["id"])
    p.ustaw("EW_TestSter", "Vector3.new(0, 1, 0.25)")
    time.sleep(0.3)
    l0 = p.serwer('"stan"')["liczniki"]
    t_met = time.time()
    p.przycisk("moc")
    time.sleep(2.0)
    l1 = p.serwer('"stan"')["liczniki"]
    ranni = sum(1 for i in ids if (p.serwer('"walka_info", %d' % i) or {}).get("hp", 999) < 999)
    wynik("P27 METEOR DIVE", (l1.get("meteor") or 0) > (l0.get("meteor") or 0) and (l1.get("ladowanie") or 0) > (l0.get("ladowanie") or 0) and ranni >= 1,
          meteory=l1.get("meteor"), ladowania=l1.get("ladowanie"), ranni=ranni)
    # P27b POWER: stadium 6, ROAR w trzy boty (zrzut 16_moc)
    p.serwer('"forma_gracza", 6')
    p.serwer('"zdolnosci_zeruj"')
    p.serwer('"przenies", %d, -30, 30' % byt)
    time.sleep(1.0)
    p.serwer('"tarcza_zeruj"')
    p.serwer('"hp", nil, 9000')
    st = p.serwer('"stan"')
    r6 = D["formy"][5]["r"]
    ids2 = [bot_obok(p, st, f, dx, dz) for f, dx, dz in ((4, r6 + 6, 2), (5, -(r6 + 6), 3), (4, 2, r6 + 7))]
    time.sleep(max(0.0, 8.8 - (time.time() - t_met)))  # odnowa POWER u klienta (po meteorze)
    l0 = p.serwer('"stan"')["liczniki"]
    p.przycisk("moc")
    time.sleep(0.62)
    if zrzuty:
        p.zrzut("16_moc.jpg")
    time.sleep(0.5)
    l1 = p.serwer('"stan"')["liczniki"]
    ogl = sum(1 for i in ids2 if (p.serwer('"walka_info", %d' % i) or {}).get("hp", 999) < 999)
    wynik("P27b ROAR", (l1.get("ryk") or 0) > (l0.get("ryk") or 0) and ogl >= 2, ryki=l1.get("ryk"), ranni=ogl)
    # P29 klipy: każdy podpięty stan zagrał swój klip (własny smok albo inne stworki w tej sesji), trofea w pozie cokołu
    a = p.atr()
    own = json.loads(a.get("EW_K_Klipy") or "{}")
    inni = json.loads(a.get("EW_K_KlipyInni") or "{}")
    wymagane = ["wyklucie", "spoczynek", "bieg", "gryz1", "gryz2", "gryz3", "ogien_start", "ogien_petla", "ogien_koniec", "splun", "ogon_zamach",
                "ryk", "szybowanie_start", "szybowanie_petla", "szybowanie_ladowanie", "nurkowanie_skok", "nurkowanie_ladowanie", "trafienie",
                "koziolek", "pozarcie", "radosc"]
    brak = [k for k in wymagane if not own.get(k) and not inni.get(k)]
    wynik("P29 klipy stanów", D.get("zestaw") != "blender" or (not brak and (a.get("EW_K_Cokol") or 0) > 0 and inni.get("upadek")),
          brak=brak, wlasne=own, inne_upadek_golema=inni.get("upadek"), cokol=a.get("EW_K_Cokol"))
    wynik("P30 koszt rigów", D.get("zestaw") != "blender" or ("pełne" in (a.get("EW_K_Rigi") or "") and (a.get("EW_K_CzesciSmokow") or 0) > 0),
          rigi=a.get("EW_K_Rigi"), czesci_smokow=a.get("EW_K_CzesciSmokow"), klatka_ms=round(a.get("EW_K_Klatka") or 0, 1))
    # P28 boty walczą tymi samymi zasadami: zamachy botów (wszystkie zamachy minus moje) i rany w świecie
    a = p.atr()
    l = p.serwer('"stan"')["liczniki"]
    bot_zamachy = (l.get("zamach") or 0) - (a.get("EW_K_Zamachy") or 0)
    wynik("P28 boty: BITE i zdolności", bot_zamachy >= 1 and (l.get("rana") or 0) > (a.get("EW_K_RanyZad") or 0), zamachy_botow=bot_zamachy,
          rany_w_swiecie=l.get("rana"), pociski=l.get("pocisk"), ogony=l.get("ogon"), oddechy=l.get("oddech"), zjedzenia=l.get("zjedz"))


def wolna_droga(dl=60.0, zapas=4.0, inne=()):
    """Prosty odcinek na łące bez przeszkód (do pomiaru poślizgu): start i kierunek +X. inne: dodatkowe koła (x, z, r)."""
    WY = D["wyspa"]
    for z0 in (-95, -80, 70, 60, -60, 20, 0, -20, 40):
        for x0 in (-110, -90, -70, -50, 0, 20):
            if math.hypot(x0, z0) > D["pole"]["r"] - 20 or math.hypot(x0 + dl, z0) > D["pole"]["r"] - 20:
                continue
            dobre = True
            for t in range(0, int(dl) + 1, 2):
                x = x0 + t
                if math.hypot(x - WY["x"], z0 - WY["z"]) < WY["r_zew"] + 8:
                    dobre = False
                    break
                for o in list(D["przeszkody"]) + [{"x": a, "z": b, "r": c} for a, b, c in inne]:
                    if math.hypot(x - o["x"], z0 - o["z"]) < o["r"] + zapas + 3:
                        dobre = False
                        break
                if not dobre:
                    break
            if dobre:
                return x0, z0
    return -60, 0


def hud(p):
    return json.loads(p.atr().get("EW_K_HUD") or "{}")


def interfejs(p, zrzuty):
    """interfejs1 (dane 3): HUD z makiety, drabina, odnowa, zamknięte pigułki, panel legowiska, odsłona, poślizg stóp, ogień z rigu."""
    st = p.serwer('"stan"')
    byt = st["byt"]
    NF = len(D["formy"])
    # boty bez ciosów na czas prób interfejsu (pasek życia, odnowy, poślizg — bez walki w tle)
    p.serwer('"boty_cisza", 150')
    # P34 HUD: nazwa, STAGE, pasek wzrostu, życie, złoto i skarb — zmieniają się z danymi serwera
    p.serwer('"forma_gracza", 3')
    p.serwer('"przenies", %d, %f, %f' % ((byt,) + wolna_droga()))
    time.sleep(1.2)
    p.serwer('"tarcza_zeruj"')
    pt = p.atr().get("EW_Potrzeba") or 100
    wi = p.serwer('"walka_info"')
    p.serwer('"zloto", 12450')
    p.serwer('"zloto_leg", 1240')
    p.serwer('"wzrost", %d' % (pt // 2))
    p.serwer('"hp", nil, %f' % (wi["hpMaks"] * 0.5))
    time.sleep(0.8)
    h = hud(p)
    wynik("P34 HUD: góra ekranu z danych", h.get("nazwa") == D["formy"][2]["nazwa"] and h.get("etap") == "STAGE 3 / %d" % NF and h.get("zloto") == "12 450"
          and 1240 <= int((h.get("skarb") or "0").replace(" ", "")) < 1240 + 400 and abs((h.get("pasek") or 0) - 0.5) < 0.12 and 0.3 < (h.get("zycie") or 0) < 0.75, hud=h)
    if zrzuty:
        p.zrzut("28_hud.jpg")
    # P35 drabina: zdobyte portrety, następne sylwetka, dalej „?”; portrety w pozie „portret”
    a = p.atr()
    mf = a.get("EW_MaxForma") or 3
    ocz = ("Z" * mf + ("N" if mf < NF else "") + "?" * max(0, NF - mf - 1))
    ocz = ocz[:-1] + "C" if ocz.endswith("?") else ocz
    wynik("P35 drabina z portretami", a.get("EW_K_Drabina") == ocz and (a.get("EW_K_Portrety") or 0) >= 4, drabina=a.get("EW_K_Drabina"),
          oczekiwana=ocz, portrety=a.get("EW_K_Portrety"))
    # P36 odnowa: wycinek DASH i BITE po naciśnięciu, potem zero i błysk żaru; FIRE po strzale
    p.serwer('"hp", nil, 5000')
    p.serwer('"zdolnosci_zeruj"')
    p.przycisk("odnowa_zeruj")
    time.sleep(0.3)
    b0 = hud(p).get("blyski") or 0
    p.ustaw("EW_TestSter", "Vector3.new(0, 1, 0.6)")
    p.przycisk("zryw")
    time.sleep(0.25)
    h1 = hud(p)
    p.przycisk("ogien")
    zd1, _ = czekaj(lambda: (lambda z: z if (z.get("ogien", {}).get("odnowa") or 0) > 0.2 else None)(json.loads(p.atr().get("EW_K_Zd") or "{}")), 2.0, 0.15)
    zd1 = zd1 or {}
    time.sleep(D["ruch"]["zryw_odnowa_s"] + 0.3)
    h2 = hud(p)
    wynik("P36 odnowa: wycinek i błysk", (h1.get("zryw") or 0) > 0.3 and h2.get("zryw", 1) == 0 and (h2.get("blyski") or 0) > b0
          and (zd1.get("ogien", {}).get("odnowa") or 0) > 0.2, zryw_po=h1.get("zryw"), zryw_potem=h2.get("zryw"), blyski=h2.get("blyski"),
          ogien=zd1.get("ogien"))
    # P37 zamknięta linia na stadium 1: kłódka i pigułka „<ZDOLNOŚĆ> at <STADIUM>”
    p.serwer('"forma_gracza", 1')
    time.sleep(0.8)
    zd = json.loads(p.atr().get("EW_K_Zd") or "{}")
    o, m = zd.get("ogien", {}), zd.get("moc", {})
    wynik("P37 zamknięte: kłódka i pigułka", o.get("zamkniete") and o.get("pigulka") and o.get("ikona") == "rysunek" and m.get("zamkniete") and m.get("pigulka"),
          ogien=o, moc=m)
    p.serwer('"forma_gracza", 3')
    time.sleep(0.6)
    # P38 panel legowiska: karty trofeów (3 zdobyte), ceny ulepszeń, zakładki, złoto
    p.przycisk("legowisko")
    time.sleep(1.0)
    a = p.atr()
    pn = json.loads(a.get("EW_K_Panel") or "{}")
    if zrzuty:
        p.zrzut("29_panel.jpg")
    p.przycisk("zakladka_u")
    time.sleep(0.5)
    pu = json.loads(p.atr().get("EW_K_Panel") or "{}")
    if zrzuty:
        p.zrzut("29b_panel_ulepszenia.jpg")
    p.przycisk("zakladka_t")
    time.sleep(0.2)
    p.przycisk("zamknij")
    time.sleep(1.3)
    tro = (pn.get("trofea") or "").split(",")
    mf = a.get("EW_MaxForma") or 3
    wynik("P38 panel legowiska", a.get("EW_K_Legowisko") and [t[:1] for t in tro] == ["Z"] * mf + ["?"] * (NF - mf)
          and abs(int((pn.get("zloto") or "0").replace(" ", "")) - (a.get("EW_Zloto") or 0)) <= 50
          and len(pn.get("ceny") or {}) == 3 and pu.get("zakladka") == "U" and not p.atr().get("EW_K_Legowisko"), panel=pn, zakladka=pu.get("zakladka"))
    # P39 odsłona: kokon → nazwa i nowa moc → sylwetka następnego → CONTINUE (zamyka)
    p.serwer('"wzrost_pelny"')
    time.sleep(0.5)
    p.przycisk("ewoluuj")
    kok, _ = czekaj(lambda: json.loads(p.atr().get("EW_K_Odsl") or "{}").get("faza") == "kokon", 4, 0.2)
    pok, _ = czekaj(lambda: json.loads(p.atr().get("EW_K_Odsl") or "{}").get("faza") == "pokaz", 6, 0.2)
    time.sleep(1.5)
    od = json.loads(p.atr().get("EW_K_Odsl") or "{}")
    if zrzuty:
        p.zrzut("30_odslona.jpg")
    p.przycisk("dalej")
    time.sleep(0.5)
    od2 = json.loads(p.atr().get("EW_K_Odsl") or "{}")
    a = p.atr()
    wynik("P39 odsłona z makiety", kok and pok and od.get("nazwa") == D["formy"][3]["nazwa"] and od.get("plytka") and od.get("nast") and od.get("dalej")
          and "FIRE BREATH" in (od.get("moc") or "") and od2.get("faza") == "" and a.get("EW_Forma") == 4, odslona=od, po=od2.get("faza"),
          forma=a.get("EW_Forma"))
    # P40 poślizg stóp na stadiach 1–4 (bieg przy prędkości gry; stadium 2 także chód): kość stopy w podporze
    x0, z0 = wolna_droga()
    pomiary["poslizg"] = {}
    # kolejność 2, 3, 4, 1: pomiar stadium 2 tuż po stadium 1 bywał zawyżony (niewyjaśnione, patrz README)
    for f in (2, 3, 4, 1):
        for tryb, sila in (("bieg", 1.0), ("chod", 0.3)) if f == 2 else (("bieg", 1.0),):
            # boty stoją (bez potrąceń „odbicie” na torze), tor omija stojące boty
            p.serwer('"boty_stoj_wszystkie", 7')
            stb = p.serwer('"stan"')
            x0, z0 = wolna_droga(inne=[(b["x"], b["z"], D["formy"][b["forma"] - 1]["r"] + 6) for b in stb["byty"] if b["slot"] == 0 and not b["martwy"]])
            p.serwer('"forma_gracza", %d' % f)
            p.serwer('"przenies", %d, %f, %f' % (byt, x0, z0))
            p.serwer('"hp", nil, 5000')
            time.sleep(0.9)
            p.serwer('"tarcza_zeruj"')
            p.ustaw("EW_TestSter", "Vector3.new(%f, 0, 3.2)" % -sila)
            time.sleep(1.0)
            p.ustaw("EW_TestPoslizg", "1.6")
            time.sleep(2.0)
            m = json.loads(p.atr().get("EW_K_Poslizg") or "{}")
            p.ustaw("EW_TestPoslizg", "nil")
            if m.get("przesuw_maks", 0) >= 0.1:
                # zły odczyt: drugi pomiar z surowym śladem stopy (do analizy fazy)
                p.ustaw("EW_TestSter", "Vector3.new(%f, 0, 3.2)" % -sila)
                p.ustaw("EW_TestPoslizg", "-1.6")
                time.sleep(2.0)
                a2 = p.atr()
                log("SUROWE %d_%s %s %s" % (f, tryb, a2.get("EW_K_Poslizg"), a2.get("EW_K_PoslizgSurowe")))
            pomiary["poslizg"]["%d_%s" % (f, tryb)] = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in m.items()}
            p.luau('game:GetService("Players").LocalPlayer:SetAttribute("EW_K_Poslizg", nil) return "ok"', "Client")
    P = pomiary["poslizg"]
    # mediana prędkości stopy w podporze (pasmo 0,03 studa); próg dla biegu stadiów 2–4 (gra odtwarza dane). Stadium 1 (sus)
    # i chód mają w danych podporę krótszą niż próbka co 2 klatki — mierzone i zgłaszane, nie liczone (patrz README)
    # runda 6: przesuw stopy w oknach podporu z danych (chód i bieg co klatkę), cel < 0,1 studa na stadiach 1–4
    ok = all(P[k].get("podporow", 0) >= 4 and 0 <= P[k].get("przesuw_maks", 9) < 0.1 for k in P)
    wynik("P40 stopy w podporze (stadia 1–4, < 0,1 studa)", ok, **{k: {x: P[k].get(x) for x in ("podporow", "przesuw_mediana", "przesuw_maks", "tempo", "v")} for k in P})
    # P41 ogień z rigu: FIRE BREATH (stadium 4) i INFERNO z przypaloną ziemią (stadium 7)
    p.serwer('"forma_gracza", 4')
    p.serwer('"zdolnosci_zeruj"')
    p.przycisk("odnowa_zeruj")
    p.serwer('"przenies", %d, %f, %f' % (byt, x0 + 10, z0))
    time.sleep(1.0)
    p.serwer('"tarcza_zeruj"')
    p.serwer('"hp", nil, 5000')
    a0 = p.atr()
    p.ustaw("EW_TestSter", "Vector3.new(-1, 0, 0.3)")
    time.sleep(0.35)
    p.przycisk("ogien")
    time.sleep(0.9)
    if zrzuty:
        p.zrzut("31_ogien_rig.jpg")
    time.sleep(1.5)
    p.serwer('"forma_gracza", 7')
    p.serwer('"zdolnosci_zeruj"')
    p.przycisk("odnowa_zeruj")
    time.sleep(1.0)
    p.serwer('"tarcza_zeruj"')
    p.ustaw("EW_TestSter", "Vector3.new(-1, 0, 0.3)")
    time.sleep(0.35)
    p.przycisk("ogien")
    time.sleep(1.5)
    if zrzuty:
        p.zrzut("32_inferno_przypalenie.jpg")
    time.sleep(0.9)
    a1 = p.atr()
    wynik("P41 ogień z rigu i przypalona ziemia", (a1.get("EW_K_Ogien") or 0) >= (a0.get("EW_K_Ogien") or 0) + 2 and (a1.get("EW_K_Przypalenia") or 0) > (a0.get("EW_K_Przypalenia") or 0),
          ogien=a1.get("EW_K_Ogien"), przypalenia=a1.get("EW_K_Przypalenia"))
    p.serwer('"forma_gracza", 1')
    time.sleep(0.5)


def odrodzenie_proby(p, zrzuty):
    """odrodzenie1: REBIRTH z ceremonią i linią FROST, DRAGON RAIN, GOLEM RAMPAGE z jednym graczem, jajo dnia, legowisko
    z dwiema liniami, wyjście i powrót z zachowaniem odrodzeń."""
    st = p.serwer('"stan"')
    byt = st["byt"]
    NF = len(D["formy"])
    O = D["odrodzenie"]
    x0, z0 = wolna_droga()
    p.serwer('"boty_cisza", 150')
    # P42 REBIRTH na ANCIENT: ceremonia (jajo nowej linii) → pisklę FROST, mnożnik
    p.serwer('"przenies", %d, %f, %f' % (byt, x0 + 20, z0))
    p.serwer('"forma_gracza", %d' % NF)
    p.serwer('"hp", nil, 99999')
    time.sleep(1.4)
    p.serwer('"tarcza_zeruj"')
    a0 = p.atr()
    p.przycisk("ewoluuj")
    cer, _ = czekaj(lambda: p.atr().get("EW_K_Odr") == "ceremonia", 4, 0.15)
    time.sleep(1.5)
    if zrzuty:
        p.zrzut("35_odrodzenie.jpg")
    wyk, _ = czekaj(lambda: p.atr().get("EW_K_Odr") == "wyklute", 7, 0.2)
    time.sleep(1.2)
    a = p.atr()
    n = (a0.get("EW_Odrodzenia") or 0) + 1
    linia = (a0.get("EW_Linia") or 1) % len(O["linie"]) + 1
    wynik("P42 REBIRTH z ceremonią", cer and wyk and a.get("EW_Forma") == 1 and a.get("EW_Odrodzenia") == n and a.get("EW_Linia") == linia
          and a.get("EW_K_LiniaModelu") == linia and abs((a.get("EW_Mnoznik") or 0) - min(O["maks_x"], O["x"] ** n)) < 0.01
          and a.get("EW_MaxForma") == 1 and a.get("EW_K_Jajko") in ("pekniete", "wyklute", "start"),
          odrodzenia=a.get("EW_Odrodzenia"), linia=a.get("EW_Linia"), model=a.get("EW_K_LiniaModelu"), mnoznik=a.get("EW_Mnoznik"),
          jajko=a.get("EW_K_Jajko"), zloto=[a0.get("EW_Zloto"), a.get("EW_Zloto")])
    p.serwer('"forma_gracza", 4')
    p.serwer('"przenies", %d, %f, %f' % (byt, x0 + 20, z0))
    time.sleep(1.6)
    if zrzuty:
        p.zrzut("36_frost.jpg")
    # P43 DRAGON RAIN wymuszony: złote kule na łące, pigułka z odliczaniem, złoto i wzrost z kul
    p.serwer('"forma_gracza", 2')
    p.serwer('"przenies", %d, %f, %f' % (byt, x0, z0))
    p.serwer('"wymus_deszcz"')
    dsz, _ = czekaj(lambda: p.serwer('"wyd"').get("deszcz"), 3, 0.2)
    time.sleep(1.2)
    w = p.serwer('"wyd"')
    a1 = p.atr()
    zl0 = p.serwer('"stan"')["zloto"]
    p.ustaw("EW_TestAuto", "true")
    time.sleep(1.5)
    if zrzuty:
        p.zrzut("37_deszcz.jpg")
    time.sleep(3.5)
    p.ustaw("EW_TestAuto", "false")
    zl1 = p.serwer('"stan"')["zloto"]
    wynik("P43 DRAGON RAIN", dsz and w.get("zloteKule", 0) > 20 and (a1.get("EW_K_ZloteKule") or 0) > 20 and (a1.get("EW_K_Wyd") or "").startswith("DRAGON RAIN!")
          and zl1 - zl0 >= D["wydarzenia"]["deszcz"]["zloto"], zlote_kule=w.get("zloteKule"), klient=a1.get("EW_K_ZloteKule"), pigulka=a1.get("EW_K_Wyd"),
          zloto=[round(zl0), round(zl1)])
    # P44 GOLEM RAMPAGE z jednym graczem: golem najwyższego stopnia na łące, trafienie → dzielona skrzynia, koniec
    p.serwer('"forma_gracza", 6')
    p.serwer('"wymus_rampage"')
    ramp, _ = czekaj(lambda: p.serwer('"wyd"').get("rampage"), 3, 0.2)
    naLace, _ = czekaj(lambda: (lambda q: q.get("rampage") and not q.get("bossLas"))(p.serwer('"wyd"')), 6, 0.3)
    w = p.serwer('"wyd"')
    a2 = p.atr()
    r = D["formy"][5]["r"] + D["formy"][D["boss"]["forma"] - 1]["r"] - 0.5
    p.serwer('"hp", nil, 99999')
    p.serwer('"tarcza_zeruj"')
    zl0 = p.serwer('"stan"')["zloto"]
    skrz = None
    for i in range(6):
        p.serwer('"boss_stoj", 3')
        p.serwer('"boss_hp", 4')
        B = p.serwer('"boss"')
        p.serwer('"przenies", %d, %f, %f' % (byt, B["x"] + r, B["z"]))
        p.ustaw("EW_TestSter", "Vector3.new(1, 0, 0.35)")
        time.sleep(0.8)
        if i == 0 and zrzuty:
            p.zrzut("38_rampage.jpg")
        p.przycisk("odnowa_zeruj")
        p.przycisk("gryz")
        skrz, _ = czekaj(lambda: p.atr().get("EW_K_Wyd") and not p.serwer('"wyd"').get("rampage"), 2.0, 0.25)
        if skrz:
            break
    zl1 = p.serwer('"stan"')["zloto"]
    wynik("P44 GOLEM RAMPAGE (jeden gracz)", ramp and naLace and skrz and zl1 - zl0 >= D["boss"]["stopnie_skrzynia"][(w.get("stopien") or 1) - 1]
          and (a2.get("EW_K_Wyd") or "").startswith("GOLEM RAMPAGE!"), na_lace=bool(naLace), stopien=w.get("stopien"), boss=[w.get("bossX"), w.get("bossZ")],
          pigulka=a2.get("EW_K_Wyd"), zloto=[round(zl0), round(zl1)])
    # P45 jajo dnia w legowisku: raz na dzień UTC, wariant trofeum obecnego stadium; następny dzień znów
    p.serwer('"forma_gracza", 2')
    p.serwer('"do_legowiska"')
    jest, _ = czekaj(lambda: p.atr().get("EW_JajoDnia") is True, 4, 0.3)
    time.sleep(1.0)
    if zrzuty:
        p.zrzut("40_jajo_dnia.jpg")
    p.przycisk("jajo_dnia")
    wyn, _ = czekaj(lambda: p.atr().get("EW_K_JajoWynik"), 4, 0.2)
    time.sleep(0.6)
    a3 = p.atr()
    jw = json.loads(a3.get("EW_K_JajoWynik") or "{}")
    war = (a3.get("EW_Warianty") or "").split(",")
    p.serwer('"dzien_przesun", 1')
    znow, _ = czekaj(lambda: p.atr().get("EW_JajoDnia") is True, 3, 0.3)
    wynik("P45 jajo dnia", jest and jw.get("ok") and jw.get("f") == 2 and (war[1] if len(war) > 1 else "") != "" and a3.get("EW_JajoDnia") is False and znow,
          wynik=jw, warianty=war, nastepny_dzien=bool(znow))
    # P47 legowisko z dwiema liniami: karty linii EMBER (8 trofeów) i obecnej
    p.przycisk("legowisko")
    time.sleep(0.6)
    p.przycisk("linia:1")
    time.sleep(0.8)
    pn1 = json.loads(p.atr().get("EW_K_Panel") or "{}")
    if zrzuty:
        p.zrzut("39_legowisko_linie.jpg")
    p.przycisk("linia:%d" % linia)
    time.sleep(0.6)
    pn2 = json.loads(p.atr().get("EW_K_Panel") or "{}")
    p.przycisk("zamknij")
    wynik("P47 legowisko z dwiema liniami", pn1.get("linia") == 1 and [t[:1] for t in (pn1.get("trofea") or "").split(",")] == ["Z"] * NF
          and pn2.get("linia") == linia and (pn2.get("trofea") or "").startswith("Z,Z"), ember=pn1.get("trofea"), obecna=pn2.get("trofea"))
    # P46 wyjście i powrót: odrodzenia, linia i postęp linii zostają
    przed = p.serwer('"odr_stan"')
    ww = p.serwer('"wyjdz_wroc", 600')
    time.sleep(1.0)
    po = p.serwer('"odr_stan"')
    wynik("P46 wyjście i powrót z odrodzeniem", ww and ww.get("zapisano") and po["odrodzenia"] == przed["odrodzenia"] and po["linia"] == przed["linia"]
          and po["linie"].get("1") == NF and po["maxForma"] == przed["maxForma"] and abs(po["mnoznik"] - przed["mnoznik"]) < 1e-6,
          przed={k: przed[k] for k in ("odrodzenia", "linia", "maxForma", "linie")}, po={k: po[k] for k in ("odrodzenia", "linia", "maxForma", "linie")})


def retencja_proby(p, zrzuty):
    """retencja1: zadania dnia (postęp, nagroda), seria 7 dni (dalej, reset, dzień 7), wyjście i powrót, ranking
    (leaderstats, tablica z „Player N”), kolory linii botów i trofeów."""
    st = p.serwer('"stan"')
    byt = st["byt"]
    p.serwer('"boty_cisza", 120')
    # P49 zadania dnia: kulki do 3 (autopilot), nagroda złoto + wzrost, pigułka w HUD
    p.serwer('"forma_gracza", 2')
    p.serwer('"przenies", %d, %f, %f' % ((byt,) + wolna_droga()))
    p.serwer('"zadania_ustaw", {"kulki", "owce", "walki"}, nil, 3')
    time.sleep(0.8)
    a0 = p.atr()
    zl0 = p.serwer('"stan"')["zloto"]
    p.ustaw("EW_TestAuto", "true")
    got, _ = czekaj(lambda: (p.atr().get("EW_K_ZadaniaGotowe") or 0) > (a0.get("EW_K_ZadaniaGotowe") or 0), 20, 0.4)
    p.ustaw("EW_TestAuto", "false")
    time.sleep(0.5)
    a1 = p.atr()
    zl1 = p.serwer('"stan"')["zloto"]
    zad = json.loads(a1.get("EW_Zadania") or "[]")
    Q = next(q for q in D["zadania"]["pula"] if q["id"] == "kulki")
    wynik("P49 zadania dnia", got and any(q["id"] == "kulki" and q["g"] for q in zad) and zl1 - zl0 >= Q["zloto"] and "/" in (a1.get("EW_K_Zadania") or ""),
          zadania=zad, pigulka=a1.get("EW_K_Zadania"), zloto=[round(zl0), round(zl1)])
    if zrzuty:
        p.zrzut("44_zadania.jpg")
    # P50 seria: wczoraj dzień 2 → dziś 3 (przyspieszenie), przerwa → 1, dzień 6 → 7 (wariant); wyjście i powrót zachowuje serię i zadania
    p.serwer('"seria_ustaw", 1, 2')
    r3 = p.serwer('"logowanie"')
    time.sleep(0.5)
    b3 = p.atr().get("EW_Boost") or 0
    p.przycisk("powitanie_zamknij")
    p.serwer('"seria_ustaw", 3, 5')
    r1 = p.serwer('"logowanie"')
    p.serwer('"seria_ustaw", 1, 6')
    r7 = p.serwer('"logowanie"')
    time.sleep(0.6)
    if zrzuty:
        p.zrzut("45_seria_dzien7.jpg")
    p.przycisk("powitanie_zamknij")
    przed = p.atr()
    ww = p.serwer('"wyjdz_wroc", 300')
    time.sleep(1.2)
    po = p.atr()
    p.przycisk("powitanie_zamknij")
    wynik("P50 seria 7 dni i zapis", r3 and r3["dni"] == 3 and b3 > 0 and r1["dni"] == 1 and r7["dni"] == 7 and (r7.get("nagroda") or {}).get("jajo")
          and ww and ww.get("zapisano") and po.get("EW_Seria") == przed.get("EW_Seria")
          and [(q["id"], q["p"], q["g"]) for q in json.loads(po.get("EW_Zadania") or "[]")] == [(q["id"], q["p"], q["g"]) for q in json.loads(przed.get("EW_Zadania") or "[]")],
          dni=[r3 and r3["dni"], r1 and r1["dni"], r7 and r7["dni"]], boost=b3, seria=[przed.get("EW_Seria"), po.get("EW_Seria")])
    # P51 ranking: leaderstats Stage i Rebirths, tablica w świecie z „Player N” (nigdy nazwa konta)
    byt = p.serwer('"stan"')["byt"]  # po wyjściu i powrocie gracz ma nowy byt
    rk = p.serwer('"ranking_odswiez"')
    time.sleep(1.0)
    ls = json.loads(p.luau('local HS = game:GetService("HttpService") local pl = game:GetService("Players").LocalPlayer local l = pl:FindFirstChild("leaderstats") '
                           'local t = pl:GetAttribute("EW_K_Ranking") or "" return HS:JSONEncode({ stage = l and l:FindFirstChild("Stage") and l.Stage.Value, '
                           'rebirths = l and l:FindFirstChild("Rebirths") and l.Rebirths.Value, bez_nazwy = string.find(t, pl.Name, 1, true) == nil '
                           'and string.find(t, pl.DisplayName, 1, true) == nil, gracz_n = string.find(t, "Player ", 1, true) ~= nil })', "Client"))
    st = p.serwer('"stan"')
    RK = D["ranking"]
    p.serwer('"przenies", %d, %f, %f' % (byt, RK["x"] + 2, RK["z"] - 7))
    time.sleep(1.4)
    if zrzuty:
        p.zrzut("42_ranking.jpg")
    wynik("P51 ranking i leaderstats", ls.get("stage") == st["forma"] and ls.get("rebirths") is not None and ls.get("bez_nazwy") and ls.get("gracz_n") and rk,
          leaderstats={k: ls.get(k) for k in ("stage", "rebirths")}, bez_nazwy=ls.get("bez_nazwy"), wpisy=len(rk or []))
    # P52 kolory linii: boty w różnych liniach, trofea legowiska w linii właściciela
    p.serwer('"do_legowiska"')
    time.sleep(2.0)
    a = p.atr()
    if zrzuty:
        p.zrzut("43_linie_trofea.jpg")
    wynik("P52 kolory linii (boty, trofea)", (a.get("EW_K_LinieBotow") or 0) >= 3 and a.get("EW_K_TrofeaLinia") == a.get("EW_Linia"),
          linie_botow=a.get("EW_K_LinieBotow"), trofea=a.get("EW_K_TrofeaLinia"), linia=a.get("EW_Linia"))


def czucie(p):
    return json.loads(p.atr().get("EW_K_Czucie") or "{}")


def odczucie_proby(p, zrzuty):
    """odczucie1: wrażenia walki (zatrzymanie 50–90 ms, wstrząs, liczby, łuski, wybuch przy zjedzeniu, pop kul, spowolnienie
    przy ewolucji, haki dźwięków), krótki ekran powitania, sklep z atrapą MarketplaceService (flaga wyłączona)."""
    st = p.serwer('"stan"')
    byt = st["byt"]
    p.serwer('"boty_cisza", 150')
    # P53 walka z bliska: trzy BITE w manekina, potem zjedzenie (wybuch), kule (pop), ewolucja (spowolnienie)
    p.serwer('"forma_gracza", 3')
    x0, z0 = wolna_droga()
    p.serwer('"przenies", %d, %f, %f' % (byt, x0, z0))
    p.serwer('"hp", nil, 9000')
    time.sleep(1.0)
    p.serwer('"tarcza_zeruj"')
    st = p.serwer('"stan"')
    r3 = D["formy"][2]["r"]
    bid = bot_obok(p, st, 3, -(2 * r3 + 1.0), 0)
    p.serwer('"hp", %d, 5000' % bid)
    p.serwer('"bot_cisza", %d, 8' % bid)
    p.ustaw("EW_TestSter", "Vector3.new(1, 0, 0.15)")
    p.ustaw("EW_TestZoom", "0.45")
    time.sleep(0.5)
    c0 = czucie(p)
    h0 = json.loads(p.atr().get("EW_K_DzwiekiHaki") or "{}")
    h0 = h0 if isinstance(h0, dict) else {}
    for i in range(3):
        p.przycisk("odnowa_zeruj")
        p.przycisk("gryz")
        time.sleep(0.62)
        if i == 1 and zrzuty:
            p.zrzut("47_trafienie.jpg")
    time.sleep(1.1)
    c1 = czucie(p)
    p.serwer('"hp", %d, 3' % bid)
    p.serwer('"przenies", %d, %f, %f' % (bid, x0 - (2 * r3 + 1.0), z0))
    p.ustaw("EW_TestSter", "Vector3.new(1, 0, 0.15)")
    zjad, _ = czekaj(lambda: (p.przycisk("odnowa_zeruj"), p.przycisk("gryz"), czucie(p).get("smierci", 0) > c1.get("smierci", 0))[2], 6, 0.6)
    p.ustaw("EW_TestZoom", "nil")
    p.ustaw("EW_TestAuto", "true")
    time.sleep(3.0)
    p.ustaw("EW_TestAuto", "false")
    p.serwer('"wzrost_pelny"')
    time.sleep(0.4)
    p.przycisk("ewoluuj")
    czekaj(lambda: czucie(p).get("slowmo", 0) > c1.get("slowmo", 0), 6, 0.3)
    time.sleep(1.2)
    c2 = czucie(p)
    h2 = json.loads(p.atr().get("EW_K_DzwiekiHaki") or "{}")
    h2 = h2 if isinstance(h2, dict) else {}
    p.przycisk("dalej")
    wynik("P53 wrażenia walki i wzrostu", c1["stopy"] - c0.get("stopy", 0) >= 3 and 50 <= c1["stopMs"] <= 90 and c1["wstrzasy"] > c0.get("wstrzasy", 0)
          and c1["liczby"] > c0.get("liczby", 0) and c1["luski"] > c0.get("luski", 0) and zjad and c2["pop"] > c1["pop"] and c2["slowmo"] > c1["slowmo"]
          and h2.get("gryz", 0) - h0.get("gryz", 0) >= 3 and h2.get("trafienie", 0) > h0.get("trafienie", 0) and h2.get("ewolucja", 0) > h0.get("ewolucja", 0),
          czucie={k: c2.get(k) for k in ("stopy", "stopMs", "wstrzasy", "wstrzasMaks", "liczby", "luski", "smierci", "pop", "slowmo")},
          haki_dzwiekow=h2, zjedzenie=bool(zjad))
    # P56 połowa paska: baner „HALFWAY to …” z zapowiedzią następnego stadium (mały cel między ewolucjami), raz na stadium
    time.sleep(2.5)  # baner „NEW POWER” po ewolucji z P53 mija
    st = p.serwer('"stan"')
    pt = st.get("potrzeba") or 1
    c3 = czucie(p)
    p.serwer('"wzrost", %f' % (pt * 0.2))
    time.sleep(0.8)
    p.serwer('"wzrost", %f' % (pt * 0.6))
    pol, _ = czekaj(lambda: czucie(p).get("polowy", 0) > c3.get("polowy", 0), 4, 0.25)
    time.sleep(0.3)
    ban = p.atr().get("EW_K_Polowa") or ""
    if zrzuty:
        p.zrzut("48_polowa.jpg")
    p.serwer('"wzrost", %f' % (pt * 0.3))
    time.sleep(0.8)
    p.serwer('"wzrost", %f' % (pt * 0.7))
    time.sleep(1.2)
    c4 = czucie(p)
    nast = D["formy"][min(len(D["formy"]), (st.get("forma") or 1) + 1) - 1]["nazwa"]
    wynik("P56 baner połowy paska", pol and "HALFWAY" in ban and nast in ban and c4.get("polowy", 0) == c3.get("polowy", 0) + 1,
          baner=ban, forma=st.get("forma"), raz_na_stadium=c4.get("polowy", 0) - c3.get("polowy", 0))
    # P54 ekran powitania: znika po dotknięciu (to samo co pierwsze dotknięcie) i sam po ok. 6 s; zadania zostają w pigułce
    p.serwer('"logowanie"')
    wid, _ = czekaj(lambda: p.atr().get("EW_K_PowitanieWidoczne") is True, 3, 0.2)
    p.przycisk("dotyk")
    znik, _ = czekaj(lambda: p.atr().get("EW_K_PowitanieWidoczne") is False, 2, 0.15)
    p.serwer('"logowanie"')
    czekaj(lambda: p.atr().get("EW_K_PowitanieWidoczne") is True, 3, 0.2)
    t0 = time.time()
    sam, t6 = czekaj(lambda: p.atr().get("EW_K_PowitanieWidoczne") is False, 9, 0.25)
    a = p.atr()
    wynik("P54 krótkie powitanie", wid and znik and sam and 5.0 <= t6 <= 7.5 and bool(a.get("EW_K_Zadania")),
          po_dotyku=bool(znik), sam_po_s=round(t6, 1), pigulka=a.get("EW_K_Zadania"))
    # P55 sklep (flaga wyłączona, atrapa MarketplaceService): przycisk ukryty, przepustki, paragony idempotentne, błąd zapisu
    a = p.atr()
    ukryty = a.get("EW_Sklep") is False and a.get("EW_K_Sklep") is False
    pr1 = p.serwer('"sklep_atrapa", {wzrost2x = true}')
    time.sleep(0.4)
    pa = p.atr().get("EW_Przepustki")
    p.serwer('"sklep_atrapa", {vip = true}')
    time.sleep(0.4)
    vip = p.atr().get("EW_VIP")
    p.serwer('"produkt_id", "zloto_1", 7001')
    zl = lambda: p.serwer('"stan"')["zloto"]
    z0 = zl()
    d1 = p.serwer('"zakup_symuluj", 7001, "proba-1"')
    z1 = zl()
    d2 = p.serwer('"zakup_symuluj", 7001, "proba-1"')
    z2 = zl()
    p.serwer('"zapis_awaria", true')
    d3 = p.serwer('"zakup_symuluj", 7001, "proba-2"')
    z3 = zl()
    p.serwer('"zapis_awaria", false')
    d4 = p.serwer('"zakup_symuluj", 7001, "proba-2"')
    z4 = zl()
    d5 = p.serwer('"zakup_symuluj", 9999, "proba-3"')
    ww = p.serwer('"wyjdz_wroc", 60')
    time.sleep(1.0)
    p.przycisk("powitanie_zamknij")
    z5 = zl()
    d6 = p.serwer('"zakup_symuluj", 7001, "proba-1"')
    z6 = zl()
    p.serwer('"produkt_id", "zloto_1", 0')
    p.serwer('"sklep_atrapa", {}')
    wynik("P55 sklep (atrapa, flaga wyłączona)", ukryty and pa == "wzrost2x" and vip is True and d1 == "PurchaseGranted" and z1 - z0 == 1000
          and d2 == "PurchaseGranted" and z2 == z1 and d3 == "NotProcessedYet" and z3 == z2 and d4 == "PurchaseGranted" and z4 - z3 == 1000
          and d5 == "NotProcessedYet" and ww and d6 == "PurchaseGranted" and z6 - z5 < 1000,  # po powrocie: bez drugiej nagrody (złoto skarbu może dojść)
          ukryty=ukryty, przepustki=pa, vip=vip, decyzje=[d1, d2, d3, d4, d5, d6], zloto=[z0, z1, z2, z3, z4, z5, z6])


def pomiar(p):
    # P22 pomiar prób: podsumowanie sesji trafia tylko do magazynu w pamięci (nigdy do prawdziwego), bez danych osoby
    klucz = p.serwer('"zapisz_probe"')
    w = p.serwer('"proby"')
    rek = list((w or {}).get("rekordy", {}).values())
    tryb = p.luau('return workspace.%s:GetAttribute("ZapisTryb")' % K, "Server")
    sys.path.insert(0, TU)
    import odczyt_prob as OP
    Z = OP.zestawienie(rek)
    zakazane = {"UserId", "userId", "name", "nazwa", "Name", "DisplayName"}
    wynik("P22 pomiar prób (magazyn w pamięci)", w and w.get("tryb") == "pamiec" and tryb == "pamiec" and klucz and rek
          and all(not (zakazane & set(r)) for r in rek) and Z["sesje"] == len(rek) and rek[0].get("maks", 0) >= 1,
          tryb=w and w.get("tryb"), zapis_tryb=tryb, klucz_format=(klucz or "")[:11], rekordow=len(rek), tabela=Z,
          pola=sorted(rek[0]) if rek else None)


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
    ap.add_argument("--tylko-interfejs", action="store_true", help="start i próby interfejsu (P01, P34–P41)")
    ap.add_argument("--tylko-odrodzenie", action="store_true", help="start i próby odrodzenia (P42–P47)")
    ap.add_argument("--tylko-retencja", action="store_true", help="start, powitanie i próby retencji (P48–P52)")
    ap.add_argument("--tylko-odczucie", action="store_true", help="start i próby odczucia walki, powitania i sklepu (P53–P55)")
    a = ap.parse_args()
    with StudioMCP(timeout=180) as s:
        p = P(s, a.studio)
        if "Current Studio Mode: Edit" not in p.call("get_studio_state")["text"]:
            log("PRZERWANO — Studio nie jest w trybie Edit")
            return 1
        log("Play:", play(a.studio, True)[-80:])
        try:
            # rozkład wydarzeń z zegara UTC wyłączony na czas prób (deszcz i rampage tylko wymuszone) — wyniki nie zależą od godziny
            czekaj(lambda: p.serwer('"wydarzenia_zegar", false'), 30, 0.5)
            if a.tylko_odczucie:
                czekaj(lambda: p.atr().get("klient") and p.atr().get("EW_Byt"), 30, 0.5)
                p.luau(BEZ_LISTY, "Client")
                czekaj(lambda: p.atr().get("EW_K_Powitanie"), 8, 0.3)
                p.przycisk("powitanie_zamknij")
                odczucie_proby(p, not a.bez_zrzutow)
            elif a.tylko_retencja:
                czekaj(lambda: p.atr().get("klient") and p.atr().get("EW_Byt"), 30, 0.5)
                p.luau(BEZ_LISTY, "Client")
                pw, _ = czekaj(lambda: p.atr().get("EW_K_Powitanie"), 8, 0.3)
                time.sleep(0.6)
                if not a.bez_zrzutow:
                    p.zrzut("41_powitanie.jpg")
                wynik("P48 powitanie: seria i zadania", pw is not None and pw >= 1, seria=pw)
                p.przycisk("powitanie_zamknij")
                odrodzenie_proby(p, not a.bez_zrzutow)
                retencja_proby(p, not a.bez_zrzutow)
            elif a.tylko_odrodzenie:
                czekaj(lambda: p.atr().get("klient") and p.atr().get("EW_Byt"), 30, 0.5)
                p.luau(BEZ_LISTY, "Client")
                time.sleep(1.5)
                odrodzenie_proby(p, not a.bez_zrzutow)
            elif a.tylko_interfejs:
                gotowe, _ = czekaj(lambda: p.atr().get("klient") and p.atr().get("EW_Byt"), 30, 0.5)
                p.luau(BEZ_LISTY, "Client")
                time.sleep(1.5)
                interfejs(p, not a.bez_zrzutow)
            else:
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
