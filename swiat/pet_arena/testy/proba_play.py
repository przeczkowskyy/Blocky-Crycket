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
            # ---------------------------------------------------------------- P01
            s1, _ = czekaj(lambda: (lambda w: w if w.get("gotowy") and w.get("gracze") else None)(p.serwer('"stan"')), 20)
            s1 = s1 or {}
            wz = int(float(p.luau(WZORCE_RS, "Client")))
            p.wynik("P01", bool(gotowe) and moj(s1).get("slot") == 1 and "w pamięci" in str(s1.get("zapis")) and wz == len(D["pety"])
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
            p.serwer('"przenies", %d, 0, 0' % moj_id)
            p.serwer('"stoj", %d, 30' % moj_id)
            a_id = p.serwer('"dziki", 1, -12, -6')
            b_id = p.serwer('"dziki", 1, -12, 6')
            time.sleep(1.6)
            for pid in (a_id, b_id):
                p.serwer('"cd", %d, 30' % pid)
            p.serwer('"zycie", %d, %d' % (b_id, int(D["pety"][0]["zycie"] * D["boty"]["zycie_x"] * 0.25)))
            s4b = p.serwer('"stan"')
            pa, pb = pet(s4b, a_id), pet(s4b, b_id)
            # cios mojego peta (Slime) w oba: stawiamy go obok każdego po kolei
            drogi = {}
            for pid, z0 in ((a_id, -6), (b_id, 6)):
                p.serwer('"przenies", %d, -12, %d' % (pid, z0))
                p.serwer('"stoj", %d, 3' % pid)
                p.serwer('"przenies", %d, -12, %d' % (moj_id, z0 - (3 if z0 < 0 else -3)))
                p.serwer('"stoj", %d, 0' % moj_id)
                before = pet(p.serwer('"stan"'), pid)
                time.sleep(1.6)
                after = pet(p.serwer('"stan"'), pid)
                drogi[pid] = round(math.hypot(after["x"] - before["x"], after["z"] - before["z"]), 1) if after and before else 99
                p.serwer('"stoj", %d, 30' % moj_id)
            ost = p.serwer('"stan"').get("ostatnie") or []
            v = {}
            for e in ost:
                if e["t"] == "cios" and e.get("a") == moj_id and e.get("b") in (a_id, b_id) and e["b"] not in v and not e.get("k"):
                    v[e["b"]] = round(e["v"], 1)
            p.wynik("P04", cios >= 3 and v.get(a_id) and v.get(b_id) and v[b_id] > 1.4 * v[a_id],
                    ciosy=cios, odrzut_pelne_zycie=v.get(a_id), odrzut_25proc=v.get(b_id), droga_pelne_zycie=drogi.get(a_id),
                    droga_25proc=drogi.get(b_id),
                    hp=[pa and round(pa["hp"]), pb and round(pb["hp"])])
            # ---------------------------------------------------------------- P05 RING OUT mojego peta
            p.serwer('"usun_dzikie"')
            p.serwer('"przenies", %d, 18, 0' % moj_id)
            zl0 = moj(p.serwer('"stan"')).get("zloto", 0)
            p.serwer('"pchnij", %d, 40, 0' % moj_id)
            wypadl, _ = czekaj(lambda: moj(p.serwer('"stan"')).get("pet") == 0, 3, 0.1)
            time.sleep(1.5)
            if zrzuty:
                p.zrzut("pa_ring_out.jpg")
            k5 = p.klient('"stan"')
            s5 = p.serwer('"stan"')
            dr = moj(s5).get("druzyna", [])
            odpoczywa = dr and dr[0]["odpoczynek_s"] >= D["odpoczynek"] - 5
            time.sleep(2.5)
            k5b = p.klient('"stan"')
            p.wynik("P05", bool(wypadl) and s5["liczniki"].get("ringout", 0) >= 1 and odpoczywa
                    and any(w["odlot"] for w in k5["widoki"]) and not any(w["id"] == moj_id for w in k5b["widoki"])
                    and k5["zdarzenia"].get("ringout", 0) >= 1,
                    odpoczynek_s=dr and dr[0]["odpoczynek_s"], ringout=s5["liczniki"].get("ringout"), zloto_przed=zl0,
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
            c_id = p.serwer('"dziki", 3, 3, 0')
            time.sleep(1.4)
            p.serwer('"przenies", %d, 3.5, 0' % c_id)
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
            for x, oczek in ((0, 5), (8, 2), (18, 1)):
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
            p.serwer('"przenies", %d, 14, 0' % moj_id)
            p.serwer('"stoj", %d, 30' % moj_id)
            d_id = p.serwer('"dziki", 5, 0, 0')
            p.serwer('"cd", %d, 30' % d_id)
            p.serwer('"stoj", %d, 30' % d_id)
            dziki_krol, _ = czekaj(lambda: p.serwer('"stan"').get("krol") == d_id, 8, 0.2)
            time.sleep(1.0)
            zl10 = moj(p.serwer('"stan"')).get("zloto", 0)
            n2 = p.serwer('"stan"').get("nagroda", 0)
            p.serwer('"przenies", %d, 0, 0' % d_id)
            p.serwer('"przenies", %d, -4.6, 0' % moj_id)
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
            for i, (x, zz) in enumerate(((5, 0), (-4, 4), (0, -6))):
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
                    p.serwer('"przenies", %d, 30, 0' % moj(st8)["pet"])      # za krawędzią: RING OUT w następnym kroku
                    if not czekaj(lambda: moj(p.serwer('"stan"')).get("pet") == 0, 3, 0.1)[0]:
                        p.serwer('"zycie", %d, 0' % moj(st8)["pet"])
                        czekaj(lambda: moj(p.serwer('"stan"')).get("pet") == 0, 3, 0.1)
                    time.sleep(3.5)
                p.serwer('"usun_dzikie"')
                for i, (x, zz) in enumerate(((4, 3), (-4, 3), (6, -6), (-14, -8))):
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
                p.serwer('"przenies", %d, 30, 0' % moj(s12)["pet"])      # za krawędzią: RING OUT w następnym kroku
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
            czekaj(lambda: len(p.serwer('"stan"')["pety"]) >= U["rzut"]["limit_areny"], 10, 0.3)
            p.klient('"pomiar_zeruj"')
            p.serwer('"liczniki_zeruj"')
            time.sleep(8)
            k14 = p.klient('"stan"')
            s14 = p.serwer('"stan"')
            if zrzuty:
                p.zrzut("pa_osiem_petow.jpg")
            p.wynik("P14", len(s14["pety"]) >= U["rzut"]["limit_areny"] - 1 and k14["srKlatki"] < (1 / 25 if okno_ok else 1 / 8) and k14["srPetli"] < 0.004 and s14["srKroku_ms"] < 2,
                    petow=len(s14["pety"]), okno_na_wierzchu=okno_ok, srKlatki_ms=round(1000 * k14["srKlatki"], 1),
                    maksKlatki_ms=round(1000 * k14["maksKlatki"], 1), srPetli_ms=round(1000 * k14["srPetli"], 2),
                    serwer_krok_ms=round(s14["srKroku_ms"], 3), czesci=k14["czesciWidokow"])
            # ---------------------------------------------------------------- P13 telefon 667 × 375
            p.serwer('"boty", %d' % D["boty"]["do_ilu"])
            p.serwer('"odpoczynek", 0')
            time.sleep(0.6)
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
                        "podpowiedz": u.get("podpowiedz")}
            for i, kk in enumerate(u.get("karty") or []):
                elementy["karta%d" % (i + 1)] = kk
            w_ekranie = {n: wewnatrz(r, okno) for n, r in elementy.items() if r}
            przyciski = [u["przycisk"]] + list(u.get("karty") or [])
            min_pt = min(min(r[2], r[3]) for r in przyciski)
            lista = [r for r in elementy.values() if r]
            nakladanie = [(i, j) for i in range(len(lista)) for j in range(i + 1, len(lista)) if nachodza(lista[i], lista[j])]
            p.wynik("P13", all(w_ekranie.values()) and min_pt >= 44 and not nakladanie and w_pasie(tel),
                    okno=okno, w_ekranie=w_ekranie, min_przycisk_pt=min_pt, nakladanie=nakladanie, skala=u.get("skala"))
            if zrzuty:
                # obraz 3D w oknie ma proporcje telefonu, a ekran telefonu jest powiększony do okna — to widok telefonu
                img = p.obraz()
                img = img.resize((1334, int(img.height * 1334 / img.width)))
                img.save(os.path.join(KLATKI, "pa_telefon.jpg"), quality=88)
                log("zrzut: klatki/pa_telefon.jpg (ekran telefonu 667 × 375 powiększony do okna)")
            p.klient('"emulacja", nil')
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
