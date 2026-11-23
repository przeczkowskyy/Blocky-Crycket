#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba Pet Arena w trybie PLAY w Studio (D-118, etap 1) — punkty P00–P16, wynik w <folder>/wynik_play.json (POZA repo).

    python -B swiat/pet_arena/testy/proba_play.py <folder wyników poza repo> [--studio <id>] [--bez-zrzutow] [--bez-okna]

Play włącza się WYŁĄCZNIE przez tools/studio_mcp.py (tools/zapis_prob.py stawia znacznik próby na Workspace/PetArenaGra:
serwer pokazuje „Player 1” zamiast nazwy konta). Lista graczy i czat schowane na czas zrzutów. Studio zawsze wraca do Edit.
  P00 Edit: kontener zgodny z repo (źródła, skrót, scena, wzorce, start, światło)
  P01 Play: serwer i klient gotowe, profil w pamięci, slot gracza, wzorce w ReplicatedStorage
  P02 wejście i kamera: kamera stała, cała arena w kadrze (okno i telefon 667 × 375), awatar na obrzeżu, podpowiedź
  P03 pierwszy rzut ≤ 10 s od wejścia (ta sama droga co stuknięcie: punkt ekranu → arena) i lądowanie peta
  P04 walka i odrzut: ciosy padają, pet słabszy (mniej życia) leci dalej po takim samym pchnięciu
  P05 RING OUT: pet gracza za krawędzią → fosa, gejzer, lot w niebo i powrót do właściciela; odpoczynek
  P06 KO: dziki pet z życiem 0 → KO, premia za wybicie dla gracza
  P07 złoto w trzech strefach (×5 / ×2 / ×1 × stopień) i „+G/s” na ekranie
  P08 umiejętności: pasek pełny → przycisk ABILITY → zdarzenie i efekt (Slime, Troll, Toad)
  P09 dzikie pety: dopełniają arenę, używają umiejętności
  P10 nagroda za głowę: król środka z koroną i rosnącą nagrodą; wybicie króla → nagroda dla gracza
  P11 odpoczynek i drugi pet: odliczanie na karcie, rzut wybiera gotowego peta; po odpoczynku pet znów gotowy
  P12 limit areny (8) i limit tempa żądań
  P13 telefon 667 × 375: wszystko w ekranie, przyciski ≥ 44 pt, bez nakładania; zrzut
  P14 czas klatki przy 8 petach
  P15 konsola bez błędów pakietu
  P16 po próbie Studio w trybie Edit
"""
import argparse
import ctypes
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
for _s in (REPO, os.path.join(REPO, "tools")):
    if _s not in sys.path:
        sys.path.append(_s)
if PAKIET in sys.path:
    sys.path.remove(PAKIET)
sys.path.insert(0, PAKIET)
import dane as DN  # noqa: E402
import zbuduj as ZB  # noqa: E402
from studio_mcp import StudioMCP, StudioError  # noqa: E402

KLATKI = os.path.join(PAKIET, "klatki")
U, D, PLIKI = DN.wszystkie_pliki()
K = U["kontener"]
SERWER = 'local HS = game:GetService("HttpService") return HS:JSONEncode(workspace.%s.Sygnaly.SterowanieSerwera:Invoke(%%s))' % K
KLIENT = 'local HS = game:GetService("HttpService") return HS:JSONEncode(workspace.%s.Sygnaly.SterowanieKlienta:Invoke(%%s))' % K
GOTOWOSC = ('local p = game:GetService("Players").LocalPlayer local k = workspace:FindFirstChild("%s") '
            'return tostring(p and p.Character ~= nil) .. " " .. tostring(k and k:GetAttribute("KlientGotowy")) .. " " '
            '.. tostring(p and p:GetAttribute("PA_Slot"))' % K)
BEZ_LISTY = ('local SG = game:GetService("StarterGui") pcall(function() SG:SetCoreGuiEnabled(Enum.CoreGuiType.PlayerList, false) '
             'SG:SetCoreGuiEnabled(Enum.CoreGuiType.Chat, false) end) return "ok"')
AWATAR = ('local HS = game:GetService("HttpService") local c = game:GetService("Players").LocalPlayer.Character '
          'local r = c and c:FindFirstChild("HumanoidRootPart") local v, na = Vector3.zero, false '
          'if r then local p, n = workspace.CurrentCamera:WorldToViewportPoint(r.Position) v = p na = n end '
          'local s = workspace.CurrentCamera.ViewportSize '
          'return HS:JSONEncode({ poz = if r then { r.Position.X, r.Position.Y, r.Position.Z } else nil, '
          'ekran = { v.X / s.X, v.Y / s.Y }, naEkranie = na })')
ATRYB = ('local HS = game:GetService("HttpService") local p = game:GetService("Players").LocalPlayer '
         'return HS:JSONEncode(p:GetAttributes())')
SPAM = ('local e = workspace.%s.Sygnaly.Akcja for i = 1, 30 do e:FireServer("wybierz", 1) end return "ok"' % K)
WZORCE_RS = 'return #game:GetService("ReplicatedStorage"):WaitForChild("%s", 5):GetChildren()' % U["folder_wzorcow_rs"]


def log(*a):
    print("[%s]" % time.strftime("%H:%M:%S"), *a, flush=True)


def bezczynnosc_s():
    """Sekundy od ostatniego ruchu myszy / klawiatury (Windows GetLastInputInfo)."""
    try:
        class LII(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
        li = LII()
        li.cbSize = ctypes.sizeof(LII)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(li))
        return (ctypes.windll.kernel32.GetTickCount() - li.dwTime) / 1000.0
    except Exception:  # noqa: BLE001
        return 0.0


def zaciemnienie_dziala():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*ekran_zaciemnienie*' -and "
                            "$_.CommandLine -notlike '*--stop*' } | Measure-Object | Select-Object -ExpandProperty Count"],
                           capture_output=True, text=True, timeout=30)
        return int((r.stdout or "0").strip() or 0) > 0
    except Exception:  # noqa: BLE001
        return False


class Proba:
    def __init__(self, studio):
        self.studio = studio
        self.wyniki = {}

    def __enter__(self):
        self.m = StudioMCP(timeout=240)
        self.s = self.m.__enter__()
        self.sid = ZB.wybierz_okno(self.s, self.studio)
        return self

    def __exit__(self, *a):
        self.m.__exit__(*a)
        return False

    def call(self, n, args=None, timeout=None):
        x = dict(args or {})
        x["studio_id"] = self.sid
        return self.s.call(n, x, timeout=timeout)

    def luau(self, kod, dm="Edit", timeout=120):
        r = self.call("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=timeout)
        if r["is_error"]:
            raise StudioError(r["text"][:1500])
        return r["text"].strip()

    def tryb_edit(self):
        return "Current Studio Mode: Edit" in self.call("get_studio_state")["text"]

    def serwer(self, argi):
        return json.loads(self.luau(SERWER % argi, "Server"))

    def klient(self, argi):
        return json.loads(self.luau(KLIENT % argi, "Client"))

    def wynik(self, punkt, ok, **szczegoly):
        self.wyniki[punkt] = dict(ok=bool(ok), **szczegoly)
        log("%s %s %s" % (punkt, "OK  " if ok else "BŁĄD", json.dumps(szczegoly, ensure_ascii=False)[:500]))

    def obraz(self):
        from PIL import Image
        r = self.call("screen_capture", {"capture_id": "petarena"}, timeout=120)
        if r["is_error"] or not r["images"]:
            raise StudioError("zrzut: %s" % (r["text"] or "brak obrazu")[:300])
        return Image.open(io.BytesIO(r["images"][0])).convert("RGB")

    def zrzut(self, nazwa, szer=1920):
        img = self.obraz()
        if img.width > szer:
            img = img.resize((szer, int(img.height * szer / img.width)))
        sciezka = os.path.join(KLATKI, nazwa)
        img.save(sciezka, quality=86)
        log("zrzut:", os.path.relpath(sciezka, REPO))
        return img


def czekaj(warunek, limit, krok=0.3):
    t0 = time.time()
    while time.time() - t0 < limit:
        try:
            w = warunek()
            if w:
                return w, time.time() - t0
        except StudioError:
            pass
        time.sleep(krok)
    return None, time.time() - t0


def moj(st):
    return st["gracze"][0] if st.get("gracze") else {}


def pet(st, pid):
    return next((p for p in st.get("pety", []) if p["id"] == pid), None)


def wewnatrz(r, o, zapas=2):
    return bool(r and o and r[0] >= o[0] - zapas and r[1] >= o[1] - zapas and r[0] + r[2] <= o[0] + o[2] + zapas
                and r[1] + r[3] <= o[1] + o[3] + zapas)


def nachodza(r, q):
    return bool(r and q and r[0] < q[0] + q[2] and q[0] < r[0] + r[2] and r[1] < q[1] + q[3] and q[1] < r[1] + r[3])


def tablica(p, nr):
    kod = ('local HS = game:GetService("HttpService") local t = workspace.%s:FindFirstChild("Tablice") '
           'local m = t and t:FindFirstChild("Tablica%d") local w = {} if m then for _, l in m:GetDescendants() do '
           'if l:IsA("TextLabel") and string.sub(l.Name, 1, 4) == "Rzad" and l.Text ~= "" then table.insert(w, l.Text) end end end '
           'return HS:JSONEncode(w)' % (K, nr))
    return json.loads(p.luau(kod, "Server"))


def mojpet(p):
    st = p.serwer('"stan"')
    return st, pet(st, moj(st).get("pet"))


def rzuc_moim(p, nr=None, x=0, zz=2):
    """Mój pet na arenę (odpoczynek 0, wybrany nr); zwraca id."""
    st = p.serwer('"stan"')
    if moj(st).get("pet"):
        p.serwer('"przenies", %d, 60, 0' % moj(st)["pet"])
        czekaj(lambda: not moj(p.serwer('"stan"')).get("pet"), 3, 0.2)
        time.sleep(1.6)                                      # kamera lotu wraca do całości (rzut celuje w punkt ekranu)
    p.serwer('"odpoczynki_zeruj"')
    time.sleep(0.3)
    if nr:
        p.klient('"wybierz", %d' % nr)
        time.sleep(0.3)
    p.klient('"rzut", %r, %r' % (float(x), float(zz)))
    w, _ = czekaj(lambda: (lambda s: (pet(s, moj(s).get("pet")) or {}).get("faza") == "walka")(p.serwer('"stan"')), 5, 0.2)
    return moj(p.serwer('"stan"')).get("pet")


def etap2(p, zrzuty):
    """P17–P27: jajka, gwiazdki, drużyna i Księga, boss, złoty pet, tarcza, trener, zapis, pad, tablet, tablice."""
    p.serwer('"boty", 0')
    p.serwer('"usun_dzikie"')
    p.serwer('"profil_nowy"')
    p.serwer('"zloto", 0')
    time.sleep(0.5)
    # ---------------------------------------------------------------- P17 jajka: okno, darmowe pierwsze, zakup, za mało złota
    p.klient('"okno", "jajka"')
    time.sleep(0.6)
    k = p.klient('"stan"')
    o = k["okna"]
    przyc = o.get("przyciski") or []
    s0 = moj(p.serwer('"stan"'))
    p.klient('"jajko", 1')
    czekaj(lambda: moj(p.serwer('"stan"')).get("jajek", 0) > s0.get("jajek", 0), 4, 0.2)
    if zrzuty:
        time.sleep(1.85)
        p.zrzut("pa_wyklucie.jpg")
    k1 = p.klient('"stan"')
    s1 = moj(p.serwer('"stan"'))
    time.sleep(3.0)
    p.serwer('"zloto", %d' % (D["jajka"][0]["cena"] + 40))
    time.sleep(0.3)
    p.klient('"jajko", 1')
    czekaj(lambda: len(moj(p.serwer('"stan"')).get("wylegarnia") or []) > 0, 4, 0.2)    # v3: kupione → wylęgarnia
    s2 = moj(p.serwer('"stan"'))
    time.sleep(2.8)
    odm = s2.get("odrzucone", 0)
    p.klient('"jajko", 3')                                   # za mało złota
    time.sleep(0.6)
    s3 = moj(p.serwer('"stan"'))
    k3 = p.klient('"stan"')
    p.wynik("P17", o.get("okno") == "jajka" and len(przyc) >= 4 and min(min(b[2], b[3]) for b in przyc) >= 44
            and s1.get("jajek") == 1 and s1.get("zloto") == 0 and len(s1.get("pety", {})) + sum(s1.get("pety", {}).values()) >= 5
            and (k1.get("okna", {}).get("wyklucie") or {}).get("t") is not None
            and s2.get("zloto") == 40 and len(s2.get("wylegarnia") or []) == 1 and s3.get("odrzucone", 0) > odm and s3.get("jajek") == 1,
            przyciski=len(przyc), min_pt=round(min((min(b[2], b[3]) for b in przyc), default=0), 1), darmowe_zloto=s1.get("zloto"),
            kolekcja=s1.get("pety"), wyklucie=(k1.get("okna") or {}).get("wyklucie"), po_zakupie=s2.get("zloto"), wylegarnia=s2.get("wylegarnia"),
            baner_za_malo=k3["ui"].get("baner"))
    # ---------------------------------------------------------------- P18 gwiazdki: kopie → mocniejszy pet, gwiazdki przy pecie
    p.serwer('"druzyna", {"lesny_slime", "zoledziak"}, 3')
    mid = rzuc_moim(p, 1)
    st, mp = mojpet(p)
    time.sleep(0.6)
    kw = [w for w in p.klient('"stan"')["widoki"] if w["id"] == mid]
    p.wynik("P18", mp is not None and mp.get("gwiazdki") == 3 and mp.get("mnSila", 1) > 1.1 and kw and "★★★" in (kw[0].get("napis") or ""),
            gwiazdki=mp and mp.get("gwiazdki"), mnSila=mp and round(mp.get("mnSila", 0), 3), napis=kw and kw[0].get("napis"),
            hpMax=mp and round(mp.get("hpMax")))
    # ---------------------------------------------------------------- P19 drużyna (okno PETS) i Księga
    p.serwer('"druzyna", {"lesny_slime", "zoledziak", "ognik"}, 1')
    p.serwer('"druzyna", {"lesny_slime", "zoledziak"}, 1')
    p.klient('"okno", "pety"')
    time.sleep(0.8)
    if zrzuty:
        p.zrzut("pa_okno_pety.jpg")
    p.klient('"druzyna_ui", "ognik", 1')                    # miejsce 1 ← Wisp
    time.sleep(0.8)
    dr = [w["id"] for w in moj(p.serwer('"stan"')).get("druzyna", [])]
    p.klient('"okno", "ksiega"')
    time.sleep(0.8)
    ks = p.klient('"stan"')["okna"]
    if zrzuty:
        p.zrzut("pa_ksiega.jpg")
    p.klient('"okno", nil')
    p.wynik("P19", dr and dr[0] == "ognik" and "zoledziak" in dr and ks.get("okno") == "ksiega",
            druzyna=dr, ksiega=ks.get("okno"))
    # ---------------------------------------------------------------- P22 tarcza słabszego
    p.serwer('"druzyna", {"lesny_slime"}, 1')
    mid = rzuc_moim(p, 1)
    p.serwer('"przenies", %d, -12, 0' % mid)
    p.serwer('"stoj", %d, 8' % mid)
    w_id = p.serwer('"dziki", 10, 12, 0')                    # Forest Troll (stopień 4)
    time.sleep(1.6)
    st = p.serwer('"stan"')
    time.sleep(0.4)
    kw = [w for w in p.klient('"stan"')["widoki"] if w["id"] == mid]
    p.wynik("P22", (pet(st, mid) or {}).get("chroniony") is True and kw and kw[0].get("tarcza") is True,
            chroniony=(pet(st, mid) or {}).get("chroniony"), napis=kw and kw[0].get("napis"))
    p.serwer('"usun_dzikie"')
    # ---------------------------------------------------------------- P20 boss: zapowiedź, walka razem, nagroda
    p.serwer('"bez_wydarzen", false')
    p.serwer('"wydarzenie", "boss", 12')
    time.sleep(1.0)
    zap = p.klient('"stan"')["ui"].get("nastepneTekst")
    p.serwer('"wydarzenie", "boss", 0')
    boss_id, _ = czekaj(lambda: next((x["id"] for x in p.serwer('"stan"')["pety"] if x.get("boss")), None), 5, 0.2)
    p.serwer('"bez_wydarzen", true')
    time.sleep(1.2)
    if zrzuty:
        p.zrzut("pa_boss.jpg")                                # boss wchodzi bramą
    time.sleep(1.6)
    mid = rzuc_moim(p, 1, -14, 0)
    p.serwer('"stoj", %d, 0' % mid)
    p.serwer('"przenies", %d, -10.5, 0' % mid)
    kb = p.klient('"stan"')
    zl0 = moj(p.serwer('"stan"')).get("zloto", 0)
    udzial, _ = czekaj(lambda: (p.serwer('"stan"').get("bossUdzial") or {}) != {}, 8, 0.3)
    if boss_id:
        p.serwer('"zycie", %d, 1' % boss_id)
    pokonany, _ = czekaj(lambda: not any(x.get("boss") for x in p.serwer('"stan"')["pety"]), 6, 0.2)
    time.sleep(0.6)
    if zrzuty:
        p.zrzut("pa_boss_nagroda.jpg")
    s20 = p.serwer('"stan"')
    przyrost = moj(s20).get("zloto", 0) - zl0
    p.wynik("P20", bool(zap) and zap.startswith("NEXT: BOSS") and bool(boss_id) and kb["ui"].get("boss") and bool(pokonany)
            and przyrost >= D["boss"]["minimum"],
            zapowiedz=zap, pasek=kb["ui"].get("boss"), udzial=bool(udzial), zloto_przyrost=przyrost,
            ostatnie=[e for e in s20.get("ostatnie", []) if e.get("boss")][-1:])
    # ---------------------------------------------------------------- P21 złoty pet: ucieka, każdy cios = złoto
    p.serwer('"wydarzenie", "zloty", 0')
    p.serwer('"bez_wydarzen", false')
    zid, _ = czekaj(lambda: next((x["id"] for x in p.serwer('"stan"')["pety"] if x.get("zloty") and x.get("boss")), None), 5, 0.2)
    p.serwer('"bez_wydarzen", true')
    zl0 = moj(p.serwer('"stan"')).get("zloto", 0)
    c0 = p.serwer('"stan"')["liczniki"].get("zloto_cios", 0)
    time.sleep(3.0)
    if zid:
        p.serwer('"druzyna", {"lesny_troll", "lesny_slime"}, 1')
        mid = rzuc_moim(p, 1, -16, 0)
        p.serwer('"przenies", %d, -15, 0' % mid)
        p.serwer('"stoj", %d, 0' % mid)
    time.sleep(3.0)
    if zrzuty:
        p.zrzut("pa_zloty.jpg")
    s21 = p.serwer('"stan"')
    c1 = s21["liczniki"].get("zloto_cios", 0)
    p.wynik("P21", bool(zid) and c1 > c0 and moj(s21).get("zloto", 0) > zl0 and (pet(s21, zid) or {}).get("boss") is not False,
            ciosy_zlota=c1 - c0, zloto_przyrost=moj(s21).get("zloto", 0) - zl0)
    if zid:
        p.serwer('"przenies", %d, 60, 0' % zid)
    # ---------------------------------------------------------------- P23 trener: poziom, mata, napis nad głową
    s0 = moj(p.serwer('"stan"'))
    p.klient('"widok", true')
    p.klient('"trening"')
    time.sleep(2.5)
    s1 = moj(p.serwer('"stan"'))
    av = json.loads(p.luau(AWATAR, "Client"))
    mata = D["sloty"][0]["mata"]
    na_macie = av.get("poz") and math.hypot(av["poz"][0] - mata[0], av["poz"][2] - mata[2]) < 3
    if zrzuty:
        p.zrzut("pa_trening.jpg")
    p.serwer('"xp", %d' % (2 * D["trener"]["baza"]))
    time.sleep(0.6)
    k23 = p.klient('"stan"')
    s2 = moj(p.serwer('"stan"'))
    p.klient('"trening"')
    p.klient('"widok", false')
    time.sleep(0.6)
    p.wynik("P23", s1.get("trening") is True and s1.get("xp", 0) > s0.get("xp", 0) and na_macie and s2.get("poziom", 1) >= 2
            and k23["ui"].get("poziom") == "LV %d" % s2.get("poziom") and k23.get("napisyGraczy", 0) >= 1,
            xp=[s0.get("xp"), s1.get("xp"), s2.get("xp")], poziom=s2.get("poziom"), na_macie=na_macie, ui=k23["ui"].get("poziom"))
    # ---------------------------------------------------------------- P24 zapis: w próbie gracz w pamięci, bez błędów
    st = p.serwer('"stan"')
    zap = p.serwer('"zapisz"')
    p.wynik("P24", "wyłączony" in str(st.get("zapis")) or "pamięci" in str(st.get("zapis")),
            zapis=st.get("zapis"), zapisano=zap, wczytany=moj(st).get("wczytany"), zapisywalny=moj(st).get("zapisywalny"))
    # ---------------------------------------------------------------- P25 pad: znaczki, okna bez myszy
    def slownik(x):
        return x if isinstance(x, dict) else {}
    r1 = slownik(p.klient('"pad", "ButtonY"'))
    time.sleep(0.4)
    k25 = p.klient('"stan"')
    r2 = slownik(p.klient('"pad", "ButtonB"'))
    r3 = slownik(p.klient('"pad", "DPadUp"'))
    time.sleep(0.3)
    r4 = slownik(p.klient('"pad", "ButtonB"'))
    p.wynik("P25", r1.get("okno") == "pety" and bool(r1.get("zaznaczony")) and k25["ui"].get("pad") is True and r2.get("okno") is None
            and r3.get("okno") == "jajka" and r4.get("okno") is None,
            y=r1, b=r2, gora=r3)
    # ---------------------------------------------------------------- P27 tablice wyników
    mid = rzuc_moim(p, 1, 0, 0)
    p.serwer('"przenies", %d, 0, 0' % mid)
    p.serwer('"stoj", %d, 4' % mid)
    time.sleep(3.2)
    t1, t3 = tablica(p, 1), tablica(p, 3)
    p.wynik("P27", any("Player 1" in x for x in t1 + t3), top_gold=t1, wybicia=t3)
    # ---------------------------------------------------------------- P26 tablet 1024 × 768 (okna i przyciski)
    p.klient('"emulacja", Vector2.new(1024, 768)')
    time.sleep(0.8)
    p.klient('"okno", "jajka"')
    time.sleep(0.6)
    k26 = p.klient('"stan"')
    u, o = k26["ui"], k26["okna"]
    okno = u["okno"]
    rects = [u["gora"], u["przycisk"]] + list(u["przyciskiGorne"]) + list(u.get("karty") or []) + [o.get("ramka")]
    p.wynik("P26", all(wewnatrz(r, okno) for r in rects if r) and min(min(b[2], b[3]) for b in o.get("przyciski", [[0, 0, 99, 99]])) >= 44,
            okno=okno, ramka=o.get("ramka"))
    p.klient('"okno", nil')
    p.klient('"emulacja", nil')
    etap_v2(p, zrzuty)
    etap_v3(p, zrzuty)
    p.serwer('"boty", %d' % D["boty"]["do_ilu"])


def wybij_dzikiego(p, nr, x=10.0):
    """Dziki z bramy; po lądowaniu wyrzucony poza arenę z zaliczeniem dla slotu 1 (jak cios kończący peta gracza)."""
    d = p.serwer('"dziki", %d, %s, 0' % (nr, x))
    czekaj(lambda: (pet(p.serwer('"stan"'), d) or {}).get("faza") == "walka", 5, 0.2)
    p.serwer('"stoj", %d, 6' % d)
    p.serwer('"przenies", %d, %s, 0' % (d, x))
    p.serwer('"wyrzuc", %d, 80, 1' % d)
    return d


def etap_v3(p, zrzuty):
    """P34–P40 (v3 Throw & Catch): panel NEXT i zegar, pewne pierwsze złapanie, ucieczka i litość, odmiana GIANT,
    ALPHA, wylęgarnia w czasie, dzienny prezent."""
    p.serwer('"usun_dzikie"')
    p.serwer('"boty", 0')
    # ---------------------------------------------------------------- P34 panel NEXT od wejścia, zegar wydarzeń sam odpala
    k = p.klient('"stan"')
    n1, n2 = k["ui"].get("nastepneTekst") or "", k["ui"].get("nastepneTekst2") or ""
    p.serwer('"bez_wydarzen", false')
    p.serwer('"liczniki_zeruj"')
    z = p.serwer('"zegar_tempo", 120')                        # 5 min zegara = 2,5 s
    def odpalil():
        lk = p.serwer('"stan"').get("liczniki")
        return isinstance(lk, dict) and (lk.get("boss", 0) + lk.get("alfa", 0)) > 0
    odpalone, _ = czekaj(odpalil, 12, 0.5)
    p.serwer('"zegar_tempo", 1')
    p.serwer('"bez_wydarzen", true')
    p.serwer('"usun_dzikie"')
    time.sleep(0.5)
    p.wynik("P34", n1.startswith("NEXT:") and "NEW MONSTER" in n2 and bool(odpalone),
            panel=[n1, n2], przyspieszony=z, zegar_odpalil=bool(odpalone))
    # ---------------------------------------------------------------- P35 rzuć → wybij → złap (pierwsze pewne), scena CAUGHT!
    p.serwer('"profil_nowy"')
    p.serwer('"druzyna", {"lesny_slime", "zoledziak"}, 1')
    time.sleep(0.4)
    mid = rzuc_moim(p, 1, -14, 0)
    p.serwer('"stoj", %d, 30' % mid)
    k0 = p.klient('"stan"')
    pod = k0["ui"].get("podpowiedzTekst")
    wybij_dzikiego(p, 6)
    zl, _ = czekaj(lambda: (moj(p.serwer('"stan"')).get("zlapane") or 0) > 0, 6, 0.2)
    time.sleep(0.9)
    k35 = p.klient('"stan"')
    if zrzuty:
        p.zrzut("pa_zlapanie.jpg")
    s35 = p.serwer('"stan"')
    ev = [e for e in s35.get("ostatnie", []) if e["t"] == "zlapanie"]
    p.wynik("P35", bool(zl) and ev and ev[-1].get("pewne") is True and "lisciolis" in (moj(s35).get("pety") or {})
            and (k35.get("okna", {}).get("wyklucie") or {}).get("napis", "").startswith("CAUGHT") and pod == D["ui"]["podpowiedz_lap"],
            podpowiedz=pod, zlapanie=ev[-1:] if ev else None, scena=(k35.get("okna") or {}).get("wyklucie"))
    time.sleep(2.5)
    # ---------------------------------------------------------------- P36 ucieczka: ESCAPED!, złoto, litość rośnie
    zl0 = moj(p.serwer('"stan"')).get("zloto", 0)
    p.serwer('"wymus_lap", false')
    wybij_dzikiego(p, 1)
    uc, _ = czekaj(lambda: any(e["t"] == "ucieczka" for e in p.serwer('"stan"').get("ostatnie", [])), 6, 0.2)
    s36 = moj(p.serwer('"stan"'))
    lit = s36.get("litosc") or []
    p.wynik("P36", bool(uc) and (lit[0] if lit else 0) >= 1 and s36.get("zloto", 0) > zl0,
            ucieczka=bool(uc), litosc=lit, zloto_przyrost=s36.get("zloto", 0) - zl0)
    # ---------------------------------------------------------------- P37 odmiana GIANT: ogłoszenie, większy pet nad areną
    p.serwer('"wymus_lap", true')
    p.serwer('"wymus_odmiane", "giant"')
    wybij_dzikiego(p, 10)
    gi, _ = czekaj(lambda: "lesny_troll" in (moj(p.serwer('"stan"')).get("odmiany") or {}), 6, 0.2)
    s37 = p.serwer('"stan"')
    ogl = [e for e in s37.get("ostatnie", []) if e["t"] == "ogloszenie"]
    time.sleep(3.2)
    p.serwer('"druzyna", {"lesny_troll", "lesny_slime"}, 1')
    p.serwer('"odpoczynki_zeruj"')
    mid = rzuc_moim(p, 1, -12, 6)
    p.serwer('"stoj", %d, 8' % mid)
    time.sleep(1.0)
    s37b = p.serwer('"stan"')
    kw = next((w for w in p.klient('"stan"')["widoki"] if w["id"] == mid), {})
    if zrzuty:
        p.klient('"widok", "pet"')
        time.sleep(1.0)
        p.zrzut("pa_odmiana.jpg")
        p.klient('"widok", false')
    troll = D["pety"][9]
    p.wynik("P37", bool(gi) and bool(ogl) and abs(((pet(s37b, mid) or {}).get("wys") or 0) - troll["wysokosc"] * 1.6) < 0.2
            and abs((kw.get("skala") or 0) - 1.6) < 0.01 and "GIANT" in (kw.get("napis") or ""),
            odmiany=moj(s37).get("odmiany"), ogloszenie=bool(ogl), wys=(pet(s37b, mid) or {}).get("wys"), skala=kw.get("skala"),
            napis=kw.get("napis"))
    # ---------------------------------------------------------------- P38 ALPHA: zapowiedź, większy, ostatni cios łapie
    p.serwer('"przenies", %d, 60, 0' % mid)
    p.serwer('"wydarzenie", "alfa", 0')
    aid, _ = czekaj(lambda: next((x["id"] for x in p.serwer('"stan"')["pety"] if x.get("dziki") and (x.get("wys") or 0) > 0
                                  and x["id"] != mid and x.get("faza") == "walka"), None), 6, 0.2)
    k38 = p.klient('"stan"')
    if zrzuty:
        time.sleep(0.3)
        p.zrzut("pa_alfa.jpg")
    s38 = p.serwer('"stan"')
    a = pet(s38, aid) or {}
    kwa = next((w for w in k38["widoki"] if w["id"] == aid), {})
    Pa = D["pety"][(a.get("nr") or 1) - 1]
    oczek = Pa["wysokosc"] * D["dzikie"]["rozmiar"][Pa["stopien"] - 1] * D["alfa"]["rozmiar"]
    p.serwer('"wymus_lap", true')
    if aid:
        p.serwer('"stoj", %d, 6' % aid)
        p.serwer('"przenies", %d, 10, 0' % aid)
        p.serwer('"wyrzuc", %d, 90, 1' % aid)
    al, _ = czekaj(lambda: any(e["t"] == "zlapanie" and e.get("alfa") for e in p.serwer('"stan"').get("ostatnie", [])), 6, 0.2)
    p.wynik("P38", bool(aid) and Pa["stopien"] >= D["alfa"]["rzadkosc_min"] and abs((a.get("wys") or 0) - oczek) < 0.2
            and kwa.get("odm") == D["ui"]["alfa"] and bool(al),
            alfa=Pa["nazwa"], wys=a.get("wys"), oczekiwana=round(oczek, 2), napis=kwa.get("odm"), zlapany=bool(al),
            baner=k38["ui"].get("baner"))
    time.sleep(3.0)
    # ---------------------------------------------------------------- P39 wylęgarnia w czasie: kup, czas mija (atrapa), HATCH; SPEED UP
    p.serwer('"zloto", 12000')
    time.sleep(0.4)
    p.klient('"jajko", 2')
    czekaj(lambda: len(moj(p.serwer('"stan"')).get("wylegarnia") or []) > 0, 4, 0.2)
    p.klient('"okno", "jajka"')
    time.sleep(0.6)
    ko = p.klient('"stan"')["okna"]
    p.serwer('"czas_plus", %d' % D["wylegarnia"]["czas_s"][1])
    time.sleep(1.2)
    kg = p.klient('"stan"')
    if zrzuty:
        p.zrzut("pa_wylegarnia.jpg")
    w0 = moj(p.serwer('"stan"')).get("jajek", 0)
    p.klient('"wylegarnia", 1')
    hat, _ = czekaj(lambda: moj(p.serwer('"stan"')).get("jajek", 0) > w0, 4, 0.2)
    time.sleep(6.2)
    p.klient('"okno", nil')
    zl1 = moj(p.serwer('"stan"')).get("zloto", 0)
    time.sleep(2.7)
    p.klient('"jajko", 2')
    czekaj(lambda: len(moj(p.serwer('"stan"')).get("wylegarnia") or []) > 0, 4, 0.2)
    p.klient('"wylegarnia", 1, true')
    sp, _ = czekaj(lambda: moj(p.serwer('"stan"')).get("jajek", 0) > w0 + 1, 4, 0.2)
    zl2 = moj(p.serwer('"stan"')).get("zloto", 0)
    koszt = zl1 - zl2 - D["jajka"][1]["cena"]
    p.wynik("P39", ko.get("okno") == "jajka" and kg["ui"].get("baner") == D["ui"]["jajko_gotowe"] and bool(hat) and bool(sp)
            and 0 < koszt <= D["wylegarnia"]["czas_s"][1] * D["wylegarnia"]["zl_na_s"][1] + 20,
            gotowe_baner=kg["ui"].get("baner"), wyklute=bool(hat), przyspieszone=bool(sp), koszt_przyspieszenia=koszt)
    time.sleep(6.2)
    # ---------------------------------------------------------------- P40 dzienny prezent: odbiór, „Tomorrow”, seria następnego dnia
    p.klient('"okno", "prezent"')
    time.sleep(0.6)
    if zrzuty:
        p.zrzut("pa_prezent.jpg")
    kp = p.klient('"stan"')
    zp0 = moj(p.serwer('"stan"')).get("zloto", 0)
    p.klient('"prezent"')
    time.sleep(1.0)
    kp2 = p.klient('"stan"')
    s40 = moj(p.serwer('"stan"'))
    p.serwer('"czas_plus", 86400')
    time.sleep(0.6)
    p.klient('"prezent"')
    time.sleep(1.0)
    s40b = moj(p.serwer('"stan"'))
    N = D["prezent"]["nagrody"]
    p.wynik("P40", kp["okna"].get("okno") == "prezent" and s40.get("zloto", 0) - zp0 >= N[0]["zloto"]
            and "Tomorrow" in (kp2["ui"].get("ogloszenie") or "") and (s40b.get("prezent") or {}).get("seria") == 2,
            okno=kp["okna"].get("okno"), zloto=s40.get("zloto", 0) - zp0, jutro=kp2["ui"].get("ogloszenie"), seria=(s40b.get("prezent") or {}).get("seria"))
    p.klient('"okno", nil')
    p.serwer('"usun_dzikie"')


def etap_v2(p, zrzuty):
    """P28–P31 (v2): wielkość petów według wagi, zderzenia i lot, kamera, wzgórze i monety."""
    # ---------------------------------------------------------------- P28 wielkość według wagi (lekki 1 : średni 1,6 : ciężki 2,4)
    p.serwer('"usun_dzikie"')
    p.serwer('"boty", 0')
    st = p.serwer('"stan"')
    if moj(st).get("pet"):
        p.serwer('"przenies", %d, 60, 0' % moj(st)["pet"])
        time.sleep(0.5)
    ids = [p.serwer('"dziki", %d, %d, -15' % (nr, x)) for nr, x in ((1, -22), (3, 0), (10, 22))]
    for i in ids:
        p.serwer('"stoj", %d, 8' % i)
        p.serwer('"cd", %d, 30' % i)
    time.sleep(2.0)
    p.klient('"widok", true')
    time.sleep(1.2)
    k = p.klient('"stan"')
    pt = {w["id"]: w["pt"] for w in k["widoki"]}
    s = p.serwer('"stan"')
    wys = {x["id"]: x.get("wys") for x in s["pety"]}
    r1 = (wys.get(ids[1]) or 0) / max(1e-6, wys.get(ids[0]) or 1)
    r2 = (wys.get(ids[2]) or 0) / max(1e-6, wys.get(ids[0]) or 1)
    rz = D["dzikie"]["rozmiar"]
    f1 = rz[D["pety"][2]["stopien"] - 1] / rz[D["pety"][0]["stopien"] - 1]
    f2 = rz[D["pety"][9]["stopien"] - 1] / rz[D["pety"][0]["stopien"] - 1]
    p.wynik("P28", abs(r1 - 1.6 * f1) < 0.1 and abs(r2 - 2.4 * f2) < 0.12 and pt.get(ids[2], 0) > 1.8 * pt.get(ids[0], 99) and D["rzut"]["limit_areny"] == 6,
            wysokosci=[wys.get(i) for i in ids], pt=[round(pt.get(i, 0)) for i in ids], limit_areny=D["rzut"]["limit_areny"])
    # ---------------------------------------------------------------- P29 zderzenia (przekazanie pędu) i lot w powietrzu
    p.serwer('"liczniki_zeruj"')
    lekki, sredni, ciezki = ids
    p.serwer('"przenies", %d, -10, 0' % ciezki)
    p.serwer('"przenies", %d, -1.5, 0' % lekki)
    p.serwer('"stoj", %d, 0' % ciezki)
    p.serwer('"pchnij", %d, 40, 0' % ciezki)                 # ciężki rozpędzony wpada w lekkiego
    time.sleep(0.6)
    s29 = p.serwer('"stan"')
    lx = (pet(s29, lekki) or {}).get("x", -99)
    p.serwer('"przenies", %d, -20, 0' % sredni)
    p.serwer('"wyrzuc", %d, 30' % sredni)
    ys, _ = czekaj(lambda: ((pet(p.serwer('"stan"'), sredni) or {}).get("y") or 0) > 0.5, 2, 0.03)
    time.sleep(2.0)
    s29b = p.serwer('"stan"')
    l29 = s29["liczniki"] if isinstance(s29.get("liczniki"), dict) else {}
    l29b = s29b["liczniki"] if isinstance(s29b.get("liczniki"), dict) else {}
    p.wynik("P29", l29.get("zderzenie", 0) >= 1 and lx > 4 and bool(ys) and l29b.get("upadek", 0) >= 1,
            zderzen=l29.get("zderzenie"), lekki_x=round(lx, 1), lot=bool(ys), upadkow=l29b.get("upadek"))
    # ---------------------------------------------------------------- P30 kamera: całość bez peta, za petem, przycisk VIEW
    p.klient('"widok", false')
    p.serwer('"usun_dzikie"')
    st = p.serwer('"stan"')
    if moj(st).get("pet"):
        p.serwer('"przenies", %d, 60, 0' % moj(st)["pet"])
        time.sleep(0.4)
    time.sleep(0.8)
    k0 = p.klient('"stan"')
    mid = rzuc_moim(p, 1, 8, 8)
    p.serwer('"stoj", %d, 4' % mid)
    time.sleep(1.5)
    k1a = p.klient('"stan"')                                 # autopilot → cała arena
    p.klient('"ster", Vector2.new(0, 0.3), 2.0')
    time.sleep(1.4)
    k1 = p.klient('"stan"')                                  # sterowanie → za petem
    if zrzuty:
        p.zrzut("pa_kamera_pet.jpg")
    p.klient('"ster", nil')
    p.klient('"widok", true')
    time.sleep(0.8)
    k2 = p.klient('"stan"')
    p.klient('"widok", false')
    p.wynik("P30", k0.get("trybKamery") == "calosc" and k1a.get("trybKamery") == "calosc" and k1.get("trybKamery") == "pet"
            and 80 <= (k1.get("mojPt") or 0) <= 140 and k2.get("trybKamery") == "calosc",
            bez_peta=k0.get("trybKamery"), autopilot=k1a.get("trybKamery"), sterowanie=k1.get("trybKamery"), pet_pt=round(k1.get("mojPt") or 0), przycisk_view=k2.get("trybKamery"))
    # ---------------------------------------------------------------- P31 wzgórze króla: monety lecą do peta, korona rośnie z nagrodą
    p.serwer('"przenies", %d, 0, 0' % mid)
    p.serwer('"stoj", %d, 12' % mid)
    m0 = p.klient('"stan"').get("monetLeci", 0)
    time.sleep(6.0)
    k31 = p.klient('"stan"')
    if zrzuty:
        p.zrzut("pa_wzgorze.jpg")
    s31 = p.serwer('"stan"')
    p.wynik("P31", k31.get("monetLeci", 0) - m0 >= 5 and s31.get("krol") == mid and (k31.get("koronaSkala") or 1) > 1.1
            and k31.get("kibicow", 0) == 8 and k31.get("plomieni", 0) >= 12,
            monet=k31.get("monetLeci", 0) - m0, korona_skala=round(k31.get("koronaSkala") or 1, 2), nagroda=round(s31.get("nagroda", 0)),
            kibicow_sektorow=k31.get("kibicow"), plomieni=k31.get("plomieni"))
    p.serwer('"stoj", %d, 0' % mid)
    # ---------------------------------------------------------------- P32 sterowanie petem: drążek → ruch, cios sam, autopilot
    p.serwer('"usun_dzikie"')
    p.serwer('"przenies", %d, -20, 0' % mid)
    time.sleep(0.4)
    s0 = pet(p.serwer('"stan"'), mid) or {}
    p.klient('"ster", Vector2.new(1, 0), 1.2')                 # w prawo na ekranie
    time.sleep(0.25)
    k1 = p.klient('"stan"')
    w1 = next((w for w in k1["widoki"] if w["id"] == mid), {})
    time.sleep(0.9)
    s1 = pet(p.serwer('"stan"'), mid) or {}
    przes = math.hypot(s1.get("x", 0) - s0.get("x", 0), s1.get("z", 0) - s0.get("z", 0))
    reczny = s1.get("reczny")
    time.sleep(D["sterowanie"]["autopilot_s"] + 1.0)
    s2 = pet(p.serwer('"stan"'), mid) or {}
    k2 = p.klient('"stan"')
    p.klient('"okno", nil')
    p.wynik("P32", przes > 6 and reczny is True and s2.get("reczny") is False and k1.get("reczne") is True and k2.get("reczne") is False
            and k1.get("sterowanieAwatara") is False,
            przesuniecie=round(przes, 1), reczny=reczny, autopilot_po=s2.get("reczny"), awatar_zablokowany=not k1.get("sterowanieAwatara"),
            napis=next((w.get("napis") for w in k2["widoki"] if w["id"] == mid), None))
    # ---------------------------------------------------------------- P33 opóźnienie sieci 120 ms (2 × 60): przewidywanie u klienta
    stare = p.luau('local n = settings().Network return string.format("%d,%d,%d,%d", n.InboundNetworkMinDelayMs, n.OutboundNetworkMinDelayMs, '
                   'n.InboundNetworkJitterMs, n.OutboundNetworkJitterMs)', "Server")
    try:
        p.luau('local n = settings().Network n.InboundNetworkMinDelayMs = 60 n.OutboundNetworkMinDelayMs = 60 return "ok"', "Server")
        time.sleep(0.8)
        p.serwer('"przenies", %d, -20, 0' % mid)
        time.sleep(0.6)
        k0 = next((w for w in p.klient('"stan"')["widoki"] if w["id"] == mid), {})
        p.klient('"ster", Vector2.new(0, 1), 1.0')
        time.sleep(0.15)
        k1 = next((w for w in p.klient('"stan"')["widoki"] if w["id"] == mid), {})
        sv = pet(p.serwer('"stan"'), mid) or {}
        klient_ruszyl = math.hypot(k1.get("x", 0) - k0.get("x", 0), k1.get("z", 0) - k0.get("z", 0))
        serwer_ruszyl = math.hypot(sv.get("x", 0) + 20, sv.get("z", 0))
        time.sleep(1.2)
    finally:
        a = stare.split(",")
        p.luau('local n = settings().Network n.InboundNetworkMinDelayMs = %s n.OutboundNetworkMinDelayMs = %s n.InboundNetworkJitterMs = %s '
               'n.OutboundNetworkJitterMs = %s return "ok"' % tuple(a), "Server")
    p.wynik("P33", klient_ruszyl > 0.5, klient_po_015s=round(klient_ruszyl, 2), serwer_po_015s=round(serwer_ruszyl, 2),
            siec_przywrocona=stare)


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--studio", default=None)
    ap.add_argument("--bez-zrzutow", action="store_true")
    ap.add_argument("--bez-okna", action="store_true")
    a = ap.parse_args()
    wyj = os.path.abspath(a.folder)
    if wyj.startswith(os.path.abspath(REPO)):
        sys.exit("folder wyników musi być POZA repozytorium")
    os.makedirs(wyj, exist_ok=True)
    os.makedirs(KLATKI, exist_ok=True)
    zrzuty = not a.bez_zrzutow
    Z = ZB.zrodla(PLIKI)
    scena = DN.scena(U)
    R = U["scena"]["arena_r"]
    with Proba(a.studio) as p:
        if not p.tryb_edit():
            sys.exit("Studio nie jest w trybie Edit — nie zaczynam")
        # ---------------------------------------------------------------- P00
        st = json.loads(p.luau(ZB.wstaw(ZB.STAN, KONTENER=K)))
        zle = [n for _, n, kl, _, t in Z if st.get("zrodla", {}).get(n, {}).get("bajtow") != len(t.encode("utf-8"))]
        p.wynik("P00", st.get("jest") and not zle and st["atrybuty"].get("Skrot") == D["skrot"] and st["czesciSceny"] == len(scena)
                and st["wzorce"] == ZB.oczekiwane_wzorce(U) and st.get("start"),
                niezgodne=zle, scena=st.get("czesciSceny"), wzorce=len(st.get("wzorce", {})), zegar=st.get("zegar"))
        if not st.get("jest"):
            sys.exit("brak kontenera — najpierw python -B swiat/pet_arena/zbuduj.py")
        idle = bezczynnosc_s()
        ciemno = zaciemnienie_dziala()
        okno_ok = (idle >= 600 or ciemno) and not a.bez_okna
        log("bezczynność %.0f s, zaciemnienie %s → okno Studio na wierzch: %s" % (idle, ciemno, okno_ok))
        if okno_ok:
            subprocess.run([sys.executable, "-B", os.path.join(REPO, "tools", "studio_okno.py"), "--na-wierzch"], capture_output=True)
        t_play = time.time()
        try:
            log("Play:", p.call("start_stop_play", {"is_start": True})["text"][:80])
            gotowe, dt = czekaj(lambda: p.luau(GOTOWOSC, "Client").startswith("true true"), 60, 0.3)
            t_wejscia = time.time()
            log("klient gotowy po %.1f s od Play" % (t_wejscia - t_play))
            p.luau(BEZ_LISTY, "Client")
            p.serwer('"bez_wydarzen", true')                 # boss i złoty pet osobno (P20, P21)
            # ---------------------------------------------------------------- P01
            s1, _ = czekaj(lambda: (lambda w: w if w.get("gotowy") and w.get("gracze") else None)(p.serwer('"stan"')), 20)
            s1 = s1 or {}
            wz = int(float(p.luau(WZORCE_RS, "Client")))
            p.wynik("P01", bool(gotowe) and moj(s1).get("slot") == 1 and ("w pamięci" in str(s1.get("zapis")) or "wyłączony" in str(s1.get("zapis"))) and wz == len(D["pety"]) + len(D["jajka"]) + len(D["boss"]["modele"])
                    and moj(s1).get("nazwa") == "Player 1",
                    slot=moj(s1).get("slot"), nazwa=moj(s1).get("nazwa"), zapis=s1.get("zapis"), wzorce_rs=wz,
                    druzyna=[w["id"] for w in moj(s1).get("druzyna", [])])
            # ---------------------------------------------------------------- P02
            k2 = p.klient('"stan"')
            tel = p.klient('"kadr", 667, 375')
            av = json.loads(p.luau(AWATAR, "Client"))
            pas = U["kamera"]["pas_ekranu"]
            kadr = k2.get("kadr") or {}

            def w_pasie(kd):
                return bool(kd) and pas[0] <= kd["y"][0] and kd["y"][1] <= pas[1] and 0.02 <= kd["x"][0] and kd["x"][1] <= 0.98
            s_slot = D["sloty"][0]["poz"]
            na_slocie = av.get("poz") and math.hypot(av["poz"][0] - s_slot[0], av["poz"][2] - s_slot[2]) < 3
            p.wynik("P02", k2["kamera"]["typ"] == "Scriptable" and w_pasie(kadr) and w_pasie(tel) and na_slocie and av.get("naEkranie")
                    and (k2["ui"].get("podpowiedzTekst") or "").startswith(("Tap", "Click")),
                    kadr_okna=kadr, kadr_telefonu=tel, awatar=av, podpowiedz=k2["ui"].get("podpowiedzTekst"),
                    dzwieki="%s/%s" % (k2.get("dzwiekiZaladowane"), k2.get("dzwiekiRazem")))
            if zrzuty:
                time.sleep(1.0)
                p.zrzut("pa_wejscie.jpg")
            # ---------------------------------------------------------------- P03 pierwszy rzut
            r3 = p.klient('"rzut", 4, -3')
            if zrzuty:
                time.sleep(0.3)
                p.zrzut("pa_rzut.jpg")
            ladowal, _ = czekaj(lambda: (lambda st: (pet(st, moj(st).get("pet")) or {}).get("faza") == "walka")(p.serwer('"stan"')), 6, 0.2)
            t3 = time.time() - t_wejscia
            s3 = p.serwer('"stan"')
            moj_id = moj(s3).get("pet")
            k3 = p.klient('"stan"')
            p.wynik("P03", r3.get("wyslano") and bool(ladowal) and t3 <= 10 and not k3["ui"].get("podpowiedzTekst", "").startswith("Tap"),
                    od_wejscia_s=round(t3, 1), rzut=r3, pet=pet(s3, moj_id), podpowiedz=k3["ui"].get("podpowiedzTekst"))
            # ---------------------------------------------------------------- P04 walka i odrzut
            time.sleep(4)
            s4 = p.serwer('"stan"')
            cios = s4["liczniki"].get("cios", 0)
            # dwa dzikie pety tego samego gatunku: pełne i niskie życie, to samo pchnięcie → kto dalej
            p.serwer('"boty", 0')
            p.serwer('"usun_dzikie"')
            moj_id = rzuc_moim(p, 1, 0, 0)
            p.serwer('"przenies", %d, 0, 0' % moj_id)
            p.serwer('"stoj", %d, 30' % moj_id)
            a_id = p.serwer('"dziki", 1, -24, -12')
            b_id = p.serwer('"dziki", 1, -24, 12')
            time.sleep(1.6)
            for pid in (a_id, b_id):
                p.serwer('"cd", %d, 30' % pid)
            p.serwer('"zycie", %d, %d' % (b_id, int(D["pety"][0]["zycie"] * D["boty"]["zycie_x"] * 0.25)))
            s4b = p.serwer('"stan"')
            pa, pb = pet(s4b, a_id), pet(s4b, b_id)
            # cios mojego peta (Slime) w oba: stawiamy go obok każdego po kolei
            drogi = {}
            v = {}

            def zwykly_cios(pid):
                # pierwszy cios mojego peta w pid bez krytyka (krytyk ma inną siłę — wtedy próbujemy jeszcze raz)
                for e in p.serwer('"stan"').get("ostatnie") or []:
                    if e["t"] == "cios" and e.get("a") == moj_id and e.get("b") == pid and not e.get("k"):
                        return round(e["v"], 1)
                return None
            for pid, z0 in ((a_id, -12), (b_id, 12)):
                for _proba in range(3):
                    p.serwer('"przenies", %d, -24, %d' % (pid, z0))
                    p.serwer('"stoj", %d, 3' % pid)
                    p.serwer('"przenies", %d, -24, %d' % (moj_id, z0 - (4.5 if z0 < 0 else -4.5)))
                    p.serwer('"stoj", %d, 0' % moj_id)
                    before = pet(p.serwer('"stan"'), pid)
                    time.sleep(1.6)
                    after = pet(p.serwer('"stan"'), pid)
                    drogi[pid] = round(math.hypot(after["x"] - before["x"], after["z"] - before["z"]), 1) if after and before else 99
                    p.serwer('"stoj", %d, 30' % moj_id)
                    v[pid] = zwykly_cios(pid)
                    if v[pid] or not after:
                        break
                    pelne = D["pety"][0]["zycie"] * D["boty"]["zycie_x"]
                    p.serwer('"zycie", %d, %d' % (pid, int(pelne * (0.25 if pid == b_id else 1))))
            p.wynik("P04", cios >= 3 and v.get(a_id) and v.get(b_id) and v[b_id] > 1.4 * v[a_id],
                    ciosy=cios, odrzut_pelne_zycie=v.get(a_id), odrzut_25proc=v.get(b_id), droga_pelne_zycie=drogi.get(a_id),
                    droga_25proc=drogi.get(b_id),
                    hp=[pa and round(pa["hp"]), pb and round(pb["hp"])])
            # ---------------------------------------------------------------- P05 RING OUT mojego peta
            p.serwer('"usun_dzikie"')
            moj_id = rzuc_moim(p, 1, 30, 0)
            p.serwer('"odpoczynek", %d' % D["odpoczynek"])
            p.serwer('"przenies", %d, 40, 0' % moj_id)
            zl0 = moj(p.serwer('"stan"')).get("zloto", 0)
            p.serwer('"wyrzuc", %d, 70' % moj_id)
            wypadl, _ = czekaj(lambda: moj(p.serwer('"stan"')).get("pet") == 0, 3, 0.1)
            time.sleep(0.6)
            k5lot = p.klient('"stan"')
            if zrzuty:
                p.zrzut("pa_wybicie_lot.jpg")
            time.sleep(0.6)
            k5 = p.klient('"stan"')
            s5 = p.serwer('"stan"')
            dr = moj(s5).get("druzyna", [])
            odpoczywa = dr and dr[0]["odpoczynek_s"] >= D["odpoczynek"] - 5
            time.sleep(2.5)
            k5b = p.klient('"stan"')
            p.wynik("P05", bool(wypadl) and s5["liczniki"].get("ringout", 0) >= 1 and odpoczywa
                    and any(w["odlot"] for w in k5["widoki"]) and not any(w["id"] == moj_id for w in k5b["widoki"])
                    and k5["zdarzenia"].get("ringout", 0) >= 1 and k5lot.get("trybKamery") == "lot",
                    odpoczynek_s=dr and dr[0]["odpoczynek_s"], ringout=s5["liczniki"].get("ringout"), zloto_przed=zl0,
                    kamera_w_locie=k5lot.get("trybKamery"),
                    karta=(k5b["ui"].get("karty") or [None])[0])
            # ---------------------------------------------------------------- P11a drugi pet: rzut wybiera gotowego (Acornling)
            r11 = p.klient('"rzut", -3, 3')
            drugi, _ = czekaj(lambda: moj(p.serwer('"stan"')).get("naArenie") == 2, 4, 0.2)
            s11 = p.serwer('"stan"')
            moj_id = moj(s11).get("pet")
            k11 = p.klient('"stan"')
            # ---------------------------------------------------------------- P06 KO dzikiego peta z premią
            time.sleep(1.2)
            p.serwer('"stoj", %d, 0' % moj_id)
            p.serwer('"przenies", %d, 0, 0' % moj_id)
            c_id = p.serwer('"dziki", 3, 6, 0')
            time.sleep(1.8)
            p.serwer('"przenies", %d, 5.8, 0' % c_id)
            p.serwer('"cd", %d, 30' % c_id)
            zl6 = moj(p.serwer('"stan"')).get("zloto", 0)
            ko0 = p.serwer('"stan"')["liczniki"].get("ko", 0)
            p.serwer('"zycie", %d, 1' % c_id)
            ko, _ = czekaj(lambda: p.serwer('"stan"')["liczniki"].get("ko", 0) > ko0, 4, 0.1)
            if zrzuty:
                time.sleep(0.5)
                p.zrzut("pa_ko.jpg")
            s6 = p.serwer('"stan"')
            p.wynik("P06", bool(ko) and moj(s6).get("zloto", 0) - zl6 >= D["pety"][2]["stopien"] * U["zloto"]["premia_dzikiego"]
                    and moj(s6).get("wybicia", 0) >= 1,
                    zloto_przyrost=moj(s6).get("zloto", 0) - zl6, wybicia=moj(s6).get("wybicia"))
            # ---------------------------------------------------------------- P07 złoto w trzech strefach
            p.serwer('"usun_dzikie"')
            strefy = []
            stopien = D["pety"][1]["stopien"]
            for x, oczek in ((0, 5), (7.5, 2), (14, 1)):
                p.serwer('"przenies", %d, %r, 0' % (moj_id, float(x)))
                p.serwer('"stoj", %d, 5' % moj_id)
                time.sleep(2.3)
                s7 = p.serwer('"stan"')
                strefy.append({"x": x, "gs": moj(s7).get("gs"), "oczekiwane": oczek * stopien * U["zloto"]["baza"],
                               "ekran": p.klient('"stan"')["ui"].get("gs")})
            p.wynik("P07", all(s["gs"] == s["oczekiwane"] for s in strefy) and all("G/s" in (s["ekran"] or "") for s in strefy),
                    strefy=strefy)
            # ---------------------------------------------------------------- P10 nagroda za głowę (mój pet królem, potem wybicie dzikiego króla)
            p.serwer('"przenies", %d, 0, 0' % moj_id)
            p.serwer('"stoj", %d, 6' % moj_id)
            krol, _ = czekaj(lambda: p.serwer('"stan"').get("krol") == moj_id, 5, 0.2)
            time.sleep(1.5)
            k10 = p.klient('"stan"')
            if zrzuty:
                p.zrzut("pa_krol.jpg")
            n1 = p.serwer('"stan"').get("nagroda", 0)
            # dziki król: mój pet wychodzi ze środka, dziki zajmuje środek, potem mój go wybija
            p.serwer('"przenies", %d, 35, 0' % moj_id)
            p.serwer('"stoj", %d, 30' % moj_id)
            d_id = p.serwer('"dziki", 5, 0, 0')
            p.serwer('"cd", %d, 30' % d_id)
            p.serwer('"stoj", %d, 30' % d_id)
            dziki_krol, _ = czekaj(lambda: p.serwer('"stan"').get("krol") == d_id, 8, 0.2)
            time.sleep(1.0)
            zl10 = moj(p.serwer('"stan"')).get("zloto", 0)
            n2 = p.serwer('"stan"').get("nagroda", 0)
            p.serwer('"przenies", %d, 0, 0' % d_id)
            p.serwer('"przenies", %d, -7.6, 0' % moj_id)
            p.serwer('"stoj", %d, 0' % moj_id)
            p.serwer('"zycie", %d, 1' % d_id)
            wybity, _ = czekaj(lambda: p.serwer('"stan"').get("krol") != d_id, 5, 0.1)
            s10 = p.serwer('"stan"')
            ko10 = [e for e in s10.get("ostatnie") or [] if e["t"] in ("ko", "ringout") and e.get("id") == d_id]
            p.wynik("P10", bool(krol) and k10.get("korona") and n1 >= U["nagroda"]["start"] and bool(dziki_krol) and bool(wybity)
                    and moj(s10).get("zloto", 0) - zl10 >= math.floor(n2),
                    moj_krol=bool(krol), korona=k10.get("korona"), nagroda_moja=round(n1, 1), dziki_krol=bool(dziki_krol),
                    nagroda_dzikiego=round(n2, 1), zloto_przyrost=moj(s10).get("zloto", 0) - zl10, wybicie=ko10)
            # ---------------------------------------------------------------- P08 umiejętności (Slime z drużyny, potem Troll i Toad)
            p.serwer('"usun_dzikie"')
            for i, (x, zz) in enumerate(((8, 0), (-7, 6), (0, -10))):
                q = p.serwer('"dziki", %d, %d, %d' % (i + 1, x, zz))
                p.serwer('"cd", %d, 30' % q)
            time.sleep(1.5)
            umiej = []
            if not moj(p.serwer('"stan"')).get("pet"):
                p.serwer('"odpoczynek", 0')
                time.sleep(0.3)
                p.klient('"rzut", 0, 2')
                time.sleep(1.5)
            moj_id = moj(p.serwer('"stan"')).get("pet")
            for _ in range(1):
                p.serwer('"pasek", %d, 1' % moj_id)
                p.serwer('"stoj", %d, 0' % moj_id)
                time.sleep(0.3)
                u0 = p.klient('"stan"')["zdarzenia"].get("umiejetnosc", 0)
                ui8 = p.klient('"stan"')["ui"]
                p.klient('"umiejetnosc"')
                ok8, _ = czekaj(lambda: p.klient('"stan"')["zdarzenia"].get("umiejetnosc", 0) > u0, 3, 0.1)
                umiej.append({"pet": (pet(p.serwer('"stan"'), moj_id) or {}).get("nazwa"), "przycisk_gotowy": ui8.get("gotowa"), "nazwa": ui8.get("przyciskNazwa"),
                              "zdarzenie": bool(ok8)})
            # Troll i Toad: drużyna z haczyka, rzut, pasek, umiejętność
            p.serwer('"odpoczynek", 3')
            p.serwer('"druzyna", {"lesny_troll", "ropucha_z_chatka"}')
            for nr, pid, plik in ((1, "lesny_troll", "pa_umiejetnosc_troll.jpg"), (2, "ropucha_z_chatka", "pa_umiejetnosc_toad.jpg")):
                st8 = p.serwer('"stan"')
                if moj(st8).get("pet"):
                    p.serwer('"przenies", %d, 60, 0' % moj(st8)["pet"])      # za krawędzią: RING OUT w następnym kroku
                    if not czekaj(lambda: moj(p.serwer('"stan"')).get("pet") == 0, 3, 0.1)[0]:
                        p.serwer('"zycie", %d, 0' % moj(st8)["pet"])
                        czekaj(lambda: moj(p.serwer('"stan"')).get("pet") == 0, 3, 0.1)
                    time.sleep(3.5)
                p.serwer('"usun_dzikie"')
                for i, (x, zz) in enumerate(((9, 5), (-9, 5), (10, -9), (-20, -12))):
                    q = p.serwer('"dziki", %d, %d, %d' % (i + 1, x, zz))
                    p.serwer('"cd", %d, 30' % q)
                p.klient('"wybierz", %d' % nr)
                time.sleep(0.4)
                p.klient('"rzut", 0, 1')
                czekaj(lambda: (pet(p.serwer('"stan"'), moj(p.serwer('"stan"')).get("pet")) or {}).get("faza") == "walka", 4, 0.2)
                time.sleep(0.4)
                mid = moj(p.serwer('"stan"')).get("pet")
                p.serwer('"pasek", %d, 1' % mid)
                time.sleep(0.25)
                u0 = p.klient('"stan"')["zdarzenia"].get("umiejetnosc", 0)
                p.klient('"umiejetnosc"')
                if zrzuty:
                    time.sleep(0.35 if pid == "lesny_troll" else 1.75)
                    p.zrzut(plik)
                ok8, _ = czekaj(lambda: p.klient('"stan"')["zdarzenia"].get("umiejetnosc", 0) > u0, 3, 0.1)
                umiej.append({"pet": pid, "zdarzenie": bool(ok8), "na_arenie": (pet(p.serwer('"stan"'), mid) or {}).get("pet")})
            p.wynik("P08", all(u["zdarzenie"] for u in umiej) and umiej[0]["przycisk_gotowy"] and umiej[0]["nazwa"]
                    and all(u.get("na_arenie") in (None, u["pet"]) for u in umiej[1:]),
                    umiejetnosci=umiej)
            # ---------------------------------------------------------------- P11 odpoczynek: odliczanie i powrót
            p.serwer('"odpoczynek", %d' % D["odpoczynek"])
            s11b = p.serwer('"stan"')
            karty11 = k11["ui"].get("kartyTekst") or []
            p.wynik("P11", bool(drugi) and r11.get("wyslano") and odpoczywa and karty11 and karty11[0].startswith("RESTING")
                    and karty11[1] == "IN ARENA",
                    drugi_pet=moj(s11).get("naArenie"), karty=karty11, druzyna_po_probie=moj(s11b).get("druzyna"))
            # ---------------------------------------------------------------- P09 dzikie pety
            p.serwer('"usun_dzikie"')
            p.serwer('"liczniki_zeruj"')
            p.serwer('"boty", %d' % D["boty"]["do_ilu"])
            pelno, t9 = czekaj(lambda: p.serwer('"stan"')["dzikich"] >= D["boty"]["do_ilu"] - 1, 20, 0.5)
            time.sleep(12)
            s9 = p.serwer('"stan"')
            p.wynik("P09", bool(pelno) and s9["liczniki"].get("umiejetnosc", 0) >= 1 and s9["liczniki"].get("cios", 0) > 5,
                    dzikich=s9["dzikich"], w_s=round(t9, 1), umiejetnosci=s9["liczniki"].get("umiejetnosc"),
                    ciosy=s9["liczniki"].get("cios"), wybicia=s9["liczniki"].get("ringout", 0) + s9["liczniki"].get("ko", 0))
            if zrzuty:
                p.zrzut("pa_arena.jpg")
            # ---------------------------------------------------------------- P12 limit areny i tempo
            s12 = p.serwer('"stan"')
            if moj(s12).get("pet"):
                p.serwer('"przenies", %d, 60, 0' % moj(s12)["pet"])      # za krawędzią: RING OUT w następnym kroku
                if not czekaj(lambda: not moj(p.serwer('"stan"')).get("pet"), 3, 0.2)[0]:
                    p.serwer('"zycie", %d, 0' % moj(s12)["pet"])
                    czekaj(lambda: not moj(p.serwer('"stan"')).get("pet"), 3, 0.2)
            p.serwer('"odpoczynek", 0')
            time.sleep(0.3)
            p.serwer('"boty", %d, 0.3' % U["rzut"]["limit_areny"])
            pelna, _ = czekaj(lambda: len(p.serwer('"stan"')["pety"]) >= U["rzut"]["limit_areny"], 15, 0.2)
            p.serwer('"pauza", true')                       # arena stoi pełna — żadne miejsce się nie zwolni
            s12 = p.serwer('"stan"')
            odm0 = moj(s12).get("odrzucone", 0)
            moj12 = moj(s12).get("pet")
            p.klient('"rzut", 2, 2')                       # droga gracza (klient wysyła, serwer odmawia: pełna)
            p.luau('workspace.%s.Sygnaly.Akcja:FireServer("rzut", 1, 2, 2) return "ok"' % K, "Client")   # wprost do serwera
            time.sleep(0.6)
            k12 = p.klient('"stan"')
            odm1 = moj(p.serwer('"stan"')).get("odrzucone", 0)
            p.serwer('"pauza", false')
            p.luau(SPAM, "Client")
            time.sleep(0.8)
            odm2 = moj(p.serwer('"stan"')).get("odrzucone", 0)
            p.wynik("P12", bool(pelna) and odm1 > odm0 and odm2 - odm1 >= 20 and k12["ui"].get("baner") == U["ui"]["pelna"],
                    petow=len(s12["pety"]), moj_pet=moj12, odmowa_pelna=odm1 - odm0, baner=k12["ui"].get("baner"), odrzucone_ze_spamu=odm2 - odm1)
            # ---------------------------------------------------------------- P14 czas klatki przy 8 petach
            p.serwer('"odpoczynek", %d' % D["odpoczynek"])
            p.klient('"emulacja", Vector2.new(667, 375)')
            p.klient('"widok", true')
            czekaj(lambda: len(p.serwer('"stan"')["pety"]) >= U["rzut"]["limit_areny"], 10, 0.3)
            time.sleep(1.0)
            p.klient('"pomiar_zeruj"')
            p.serwer('"liczniki_zeruj"')
            time.sleep(8)
            k14 = p.klient('"stan"')
            s14 = p.serwer('"stan"')
            if zrzuty:
                p.zrzut("pa_szesc_petow.jpg")
            p.klient('"widok", false')
            p.klient('"emulacja", nil')
            p.wynik("P14", len(s14["pety"]) >= U["rzut"]["limit_areny"] - 2 and k14["srKlatki"] < (1 / 25 if okno_ok else 1 / 8) and k14["srPetli"] < 0.004 and s14["srKroku_ms"] < 2,
                    petow=len(s14["pety"]), okno_na_wierzchu=okno_ok, srKlatki_ms=round(1000 * k14["srKlatki"], 1),
                    maksKlatki_ms=round(1000 * k14["maksKlatki"], 1), srPetli_ms=round(1000 * k14["srPetli"], 2),
                    serwer_krok_ms=round(s14["srKroku_ms"], 3), czesci=k14["czesciWidokow"])
            # ---------------------------------------------------------------- P17–P27: etap 2
            etap2(p, zrzuty)
            # ---------------------------------------------------------------- P13 telefon 667 × 375 (w środku bitki)
            p.serwer('"odpoczynki_zeruj"')
            p.serwer('"boty", 4, 0.4')
            czekaj(lambda: len(p.serwer('"stan"')["pety"]) >= 4, 10, 0.3)
            p.klient('"emulacja", Vector2.new(667, 375)')
            time.sleep(0.8)
            if not moj(p.serwer('"stan"')).get("pet"):
                p.klient('"rzut", 2, -2')
                time.sleep(1.5)
            p.serwer('"pasek", %d, 1' % (moj(p.serwer('"stan"')).get("pet") or 0))
            time.sleep(0.6)
            k13 = p.klient('"stan"')
            u = k13["ui"]
            okno = u["okno"]
            elementy = {"gora": u["gora"], "przycisk": u["przycisk"], "pet": u["pet"] if u.get("petWidoczny") else None,
                        "podpowiedz": u.get("podpowiedz"), "eggs": u["przyciskiGorne"][0], "pets": u["przyciskiGorne"][1],
                        "train": u["przyciskiGorne"][2], "view": u["przyciskiGorne"][3], "nastepne": u.get("nastepne"), "prezent": u.get("prezent")}
            for i, kk in enumerate(u.get("karty") or []):
                elementy["karta%d" % (i + 1)] = kk
            w_ekranie = {n: wewnatrz(r, okno) for n, r in elementy.items() if r}
            przyciski = [u["przycisk"]] + list(u.get("karty") or []) + list(u["przyciskiGorne"])
            wielkosci = sorted(round(w["pt"]) for w in k13["widoki"] if not w["lot"] and not w["odlot"] and not w.get("boss"))
            min_pt = min(min(r[2], r[3]) for r in przyciski)
            lista = [r for r in elementy.values() if r]
            nakladanie = [(i, j) for i in range(len(lista)) for j in range(i + 1, len(lista)) if nachodza(lista[i], lista[j])]
            moj13 = k13.get("mojPt") or 0
            # domyślna ścieżka bez drążka: drążka nie ma, dopóki palec nie dotknie lewej strony (tu: sterowanie z próby)
            drazek_ukryty = u.get("drazek") is None
            p.klient('"ster", Vector2.new(0.6, 0.4), 1.6')
            time.sleep(1.2)
            k13b = p.klient('"stan"')
            u13b = k13b["ui"]
            drazek_przy_ruchu = bool(u13b.get("drazek")) and wewnatrz(u13b["drazek"], okno)
            moj13 = k13b.get("mojPt") or 0
            p.klient('"ster", nil')
            p.wynik("P13", all(w_ekranie.values()) and min_pt >= 44 and not nakladanie and w_pasie(tel) and 80 <= moj13 <= 140
                    and k13.get("trybKamery") == "calosc" and k13b.get("trybKamery") == "pet" and k13.get("duzychSlow", 0) <= 2
                    and drazek_ukryty and drazek_przy_ruchu,
                    okno=okno, w_ekranie=w_ekranie, min_przycisk_pt=round(min_pt, 1), nakladanie=nakladanie, skala=u.get("skala"),
                    pety_pt=wielkosci, moj_pet_pt=round(moj13), kamera=k13.get("trybKamery"), duze_slowa=k13.get("duzychSlow"),
                    podpowiedz=u.get("podpowiedzTekst"), drazek_domyslnie=not drazek_ukryty, drazek_przy_ruchu=drazek_przy_ruchu)
            if zrzuty:
                # obraz 3D w oknie ma proporcje telefonu, a ekran telefonu jest powiększony do okna — to widok telefonu
                img = p.obraz()
                img = img.resize((1334, int(img.height * 1334 / img.width)))
                img.save(os.path.join(KLATKI, "pa_telefon.jpg"), quality=88)
                log("zrzut: klatki/pa_telefon.jpg (ekran telefonu 667 × 375 powiększony do okna)")
            p.klient('"emulacja", nil')
            p.serwer('"boty", %d' % D["boty"]["do_ilu"])
            # ---------------------------------------------------------------- P15 konsola
            kons = p.call("get_console_output")["text"]
            linie = [x for x in kons.splitlines() if "PetArena" in x]
            bledy = [x for x in linie if any(s in x.lower() for s in ("error", "błąd", "stack", "attempt", "zdarzenie "))]
            with open(os.path.join(wyj, "konsola.txt"), "w", encoding="utf-8") as f:
                f.write(kons)
            p.wynik("P15", not bledy, bledy=bledy[:8], wpisow=len(linie))
        finally:
            log("Stop:", p.call("start_stop_play", {"is_start": False})["text"][:80])
            edit, _ = czekaj(p.tryb_edit, 40, 0.5)
            p.wynik("P16", bool(edit), edit=bool(edit))
        with open(os.path.join(wyj, "wynik_play.json"), "w", encoding="utf-8") as f:
            json.dump(p.wyniki, f, ensure_ascii=False, indent=1)
        zle = [k for k, v in p.wyniki.items() if not v["ok"]]
        log("WYNIK: %d/%d OK%s" % (len(p.wyniki) - len(zle), len(p.wyniki), (" — błędy: " + ", ".join(zle)) if zle else ""))
        return 1 if zle else 0


if __name__ == "__main__":
    sys.exit(main())
