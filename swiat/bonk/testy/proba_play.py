#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba BONK w trybie PLAY w Studio — punkty B00–B16, wynik w <folder>/wynik_play.json (POZA repo: zawiera nazwę konta).

    python -B swiat/bonk/testy/proba_play.py <folder wyników poza repo> [--bez-zrzutow] [--studio <id>]

Play włącza się WYŁĄCZNIE przez tools/studio_mcp.py (StudioMCP.call → tools/zapis_prob.py stawia znacznik próby na
Workspace/StanGracza i Workspace/BonkGra: prawdziwy zapis ludzi nietknięty). Na czas próby: AutoStart = true i
ZapisProbaMagazyn = true na BonkGra (zapis idzie do magazynu próby BONK_Gracz_v1_Studio_Proba, rekord próby
kasowany na końcu); po Stop AutoStart wraca do poprzedniej wartości. Studio zawsze wraca do Edit.
  B00 Edit: kontener zgodny z repo (źródła, skrót, mapa, wzorce, bramy, portale)
  B01 Play: serwer gotowy, potwory w trzech krainach, zapis = magazyn próby (nie prawdziwy klucz)
  B02 wejście przez AutoStart: gracz w lesie, ekran BONK, cudze ekrany schowane, bez bohatera klasy (awatar widać)
  B03 pierwszy BONK ≤ 30 s od wejścia (dojście do slime'a i trzymany BONK)
  B04 lot i monety: zdarzenie lotu u klienta, monety i Moc rosną
  B05 odradzanie: zagroda znów pełna w ≤ 5 s
  B06 trafienie bez zabicia: życie spada, potwór żyje
  B07 limit tempa: 30 BONK naraz od klienta → serwer przyjmuje najwyżej kilka
  B08 HOME RUN przy dużej Mocy (haczyk próby) + zrzuty lotu
  B09 brama: bez Mocy serwer cofa za bramę; z Mocą wrota otwarte, przejście do Bagna, nazwa krainy
  B10 trzy krainy (Moc podniesiona haczykiem próby): każda z potworami, zrzut każdej
  B11 czas klatki przy pełnej krainie
  B12 zapis: zapis do magazynu próby, odczyt, ponowne wczytanie
  B13 wyjście portalem: cudze ekrany wracają, gracz przy bramie BONK; ponowne wejście bramą BONK
  B14 ekran telefonu 667 × 375 (emulacja) — zrzut
  B15 konsola bez błędów pakietu
  B16 po próbie Studio w trybie Edit, AutoStart przywrócony
"""
import argparse
import io
import json
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (REPO, os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"),
           os.path.join(REPO, "swiat", "test_walki2", "testy")):
    if _s not in sys.path:
        sys.path.append(_s)
if PAKIET in sys.path:
    sys.path.remove(PAKIET)
sys.path.insert(0, PAKIET)
import dane as DN  # noqa: E402
import zbuduj as ZB  # noqa: E402
import zapis_prob as ZP  # noqa: E402
from studio_mcp import StudioMCP, StudioError  # noqa: E402
from cel_studio import wybierz_studio  # noqa: E402

KLATKI = os.path.join(PAKIET, "klatki")
U, D, PLIKI = DN.wszystkie_pliki()
K = U["kontener"]

SERWER = 'local HS = game:GetService("HttpService") return HS:JSONEncode(workspace.%s.Sygnaly.SterowanieSerwera:Invoke(%%s))' % K
KLIENT = 'local HS = game:GetService("HttpService") return HS:JSONEncode(workspace.%s.Sygnaly.SterowanieKlienta:Invoke(%%s))' % K
GOTOWOSC = ('local p = game:GetService("Players").LocalPlayer local k = workspace:FindFirstChild("%s") '
            'return tostring(p and p.Character ~= nil) .. " " .. tostring(k and k:GetAttribute("KlientGotowy")) .. " " '
            '.. tostring(p and p:GetAttribute("BonkAktywny"))' % K)
PRZENIES = ('local g = game:GetService("Players"):GetPlayers()[1] local c = g and g.Character if not c then return "brak" end '
            'c:PivotTo(CFrame.new(%s)) c.HumanoidRootPart.AssemblyLinearVelocity = Vector3.zero return "ok"')
IDZ = ('local g = game:GetService("Players"):GetPlayers()[1] local h = g and g.Character and g.Character:FindFirstChildOfClass("Humanoid") '
       'if not h then return "brak" end h:MoveTo(Vector3.new(%s)) return "ok"')
POZ = ('local HS = game:GetService("HttpService") local g = game:GetService("Players"):GetPlayers()[1] '
       'local r = g and g.Character and g.Character:FindFirstChild("HumanoidRootPart") '
       'return HS:JSONEncode(if r then { r.Position.X, r.Position.Y, r.Position.Z } else {})')
SPAM = ('local e = workspace.%s.Sygnaly.Bonk for i = 1, 30 do e:FireServer() end return "ok"' % K)
BEZ_LISTY = ('local SG = game:GetService("StarterGui") pcall(function() SG:SetCoreGuiEnabled(Enum.CoreGuiType.PlayerList, false) '
             'SG:SetCoreGuiEnabled(Enum.CoreGuiType.Chat, false) end) return "ok"')
AWATAR = ('local HS = game:GetService("HttpService") local c = game:GetService("Players").LocalPlayer.Character '
          'local w, n = 0, 0 if c then for _, d in c:GetDescendants() do if d:IsA("BasePart") and d.Name ~= "HumanoidRootPart" then '
          'n += 1 if d.Transparency < 1 and d.LocalTransparencyModifier < 1 then w += 1 end end end end '
          'local b = workspace:FindFirstChild("BohaterSwiat") local bl = b and workspace:FindFirstChild("BohaterowieLokalni", true) '
          'local ile = 0 if bl then ile = #bl:GetChildren() end '
          'return HS:JSONEncode({ czesci = n, widoczne = w, bohater = b ~= nil, bohaterow = ile, '
          'bez = game:GetService("Players").LocalPlayer:GetAttribute("BezBohatera") })')
ATR_EDIT = ('local k = workspace:FindFirstChild("%s") if not k or k:GetAttribute("Wygenerowane") ~= true then return "BRAK" end '
            'local stary = k:GetAttribute("%s") k:SetAttribute("%s", %%s) return tostring(stary)' % (K, U["autostart"], U["autostart"]))
KLASA = ('local p = game:GetService("Players").LocalPlayer local g = p.PlayerGui:FindFirstChild("ClassSelect") '
         'return tostring(g ~= nil and g.Enabled) .. " " .. workspace.CurrentCamera.CameraType.Name .. " " '
         '.. tostring(p:GetAttribute("Class")) .. " " .. tostring(p:GetAttribute("Race"))')


def log(*a):
    print("[%s]" % time.strftime("%H:%M:%S"), *a, flush=True)


class Proba:
    def __init__(self, studio=None):
        self.studio = studio
        self.wyniki = {}

    def __enter__(self):
        self.m = StudioMCP(timeout=240)
        self.s = self.m.__enter__()
        self.sid = wybierz_studio(self.s, self.studio)
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

    def poz(self):
        return json.loads(self.luau(POZ, "Server"))

    def przenies(self, x, y, z):
        return self.luau(PRZENIES % ("%r, %r, %r" % (x, y + 3.5, z)), "Server")

    def idz(self, x, y, z):
        return self.luau(IDZ % ("%r, %r, %r" % (x, y, z)), "Server")

    def wynik(self, punkt, ok, **szczegoly):
        self.wyniki[punkt] = dict(ok=bool(ok), **szczegoly)
        log("%s %s %s" % (punkt, "OK  " if ok else "BŁĄD", json.dumps(szczegoly, ensure_ascii=False)[:400]))

    def zrzut(self, sciezka, kamera, patrz):
        from PIL import Image
        r = self.call("screen_capture", {"capture_id": "bonk", "camera_position": list(kamera), "look_at_position": list(patrz)},
                      timeout=120)
        if r["is_error"] or not r["images"]:
            raise StudioError("zrzut: %s" % (r["text"] or "brak obrazu")[:300])
        img = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
        img.save(sciezka, quality=88)
        log("zrzut:", os.path.relpath(sciezka, REPO))
        return img

    def zrzut_bez_kamery(self, sciezka):
        from PIL import Image
        r = self.call("screen_capture", {"capture_id": "bonk"}, timeout=120)
        if r["is_error"] or not r["images"]:
            raise StudioError("zrzut: %s" % (r["text"] or "brak obrazu")[:300])
        img = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
        return img


def na_wierzch():
    """Okno Studio na wierzch (w tle Studio rysuje ok. 15 klatek/s) — tylko gdy nikt nie pracuje przy komputerze."""
    r = subprocess.run([sys.executable, "-B", os.path.join(REPO, "tools", "studio_okno.py"), "--na-wierzch"], capture_output=True)
    log("okno Studio na wierzch: kod %d" % r.returncode)


def czekaj(warunek, limit, krok=0.4):
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


def gracz(st):
    return st["gracze"][0] if st.get("gracze") else {}


def potwory(p, kraina, gatunek=None):
    return [m for m in p.serwer('"potwory", %d' % kraina) if m["zywy"] and (gatunek is None or m["gatunek"] == gatunek)]


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--bez-zrzutow", action="store_true")
    ap.add_argument("--studio", default=None)
    ap.add_argument("--bez-okna", action="store_true", help="nie wysuwaj okna Studio na wierzch")
    a = ap.parse_args()
    wyj = os.path.abspath(a.folder)
    if wyj.startswith(os.path.abspath(REPO)):
        sys.exit("folder wyników musi być POZA repozytorium (wyniki mają nazwę konta)")
    os.makedirs(wyj, exist_ok=True)
    os.makedirs(KLATKI, exist_ok=True)
    try:
        from czuwanie import nie_usypiaj
    except Exception:  # noqa: BLE001
        def nie_usypiaj():
            return False
    nie_usypiaj()
    Z = ZB.zrodla(PLIKI)
    K1, K2, K3 = D["krainy"]
    with Proba(a.studio) as p:
        if not p.tryb_edit():
            sys.exit("Studio nie jest w trybie Edit — nie zaczynam")
        # ---------------------------------------------------------------- B00
        st = json.loads(p.luau(ZB.wstaw(ZB.STAN, KONTENER=K)))
        zle = [n for _, n, kl, _, t in Z if st.get("zrodla", {}).get(n, {}).get("bajtow") != len(t.encode("utf-8"))]
        oczek_mapy = sum(len(c) for *_, c in ZB.dane_mapy(U))
        p.wynik("B00", st.get("jest") and not zle and st["atrybuty"].get("Skrot") == D["skrot"] and st["czesciMapy"] == oczek_mapy
                and len(st["wzorce"]) == len(D["gatunki"]) and st["bramy"] == 3 and st["portal"] and st["powrot"],
                niezgodne=zle, mapa=st.get("czesciMapy"), wzorce=len(st.get("wzorce", {})), portal=st.get("portal"))
        if not st.get("jest"):
            sys.exit("brak kontenera — najpierw python -B swiat/bonk/zbuduj.py")
        if not a.bez_okna:
            na_wierzch()
        autostart_przed = p.luau(ATR_EDIT % "true")
        p.luau(ZP.kod_magazynu(None, K))
        t_play = time.time()
        try:
            log("Play:", p.call("start_stop_play", {"is_start": True})["text"][:80])
            gotowe, dt = czekaj(lambda: p.luau(GOTOWOSC, "Client") == "true true true", 90, 0.5)
            log("klient gotowy, serwer wpuścił do BONK po %.1f s" % (time.time() - t_play))
            # ekran wyboru klasy obecnej gry (gracz bez zapisu, AutoStart w obecnym miejscu): BONK czeka, aż się skończy;
            # wybór jak człowiek — Enter (klasa, potem rasa), aż ekran zniknie i kamera wróci do postaci
            stan_klasy = ""
            for _ in range(22):
                stan_klasy = p.luau(KLASA, "Client")
                cz = stan_klasy.split()
                if len(cz) >= 3 and cz[0] == "false" and cz[1] == "Custom" and cz[2] != "nil":
                    break
                p.call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": "Return"}]})
                time.sleep(1.6)
            log("wybór klasy:", stan_klasy)
            aktywny, dt = czekaj(lambda: p.klient('"stan"').get("aktywny"), 15, 0.3)
            t_wejscia = time.time()
            log("ekran BONK po wyborze klasy po %.1f s" % dt)
            p.luau(BEZ_LISTY, "Client")
            p.serwer('"od_nowa"')                           # rekord magazynu próby z poprzedniej próby — od zera
            # ---------------------------------------------------------------- B01
            s0, _ = czekaj(lambda: (lambda w: w if w.get("gotowy") else None)(p.serwer('"stan"')), 30)
            s0 = s0 or {}
            p.wynik("B01", s0.get("potworow") == sum(z["ile"] for k in D["krainy"] for z in k["zagrody"])
                    and all(n > 0 for n in s0.get("krainy", [])) and s0.get("zapis") == "włączony (magazyn próby)"
                    and str(s0.get("magazyn", "")).endswith("_Studio_Proba"),
                    potworow=s0.get("potworow"), krainy=s0.get("krainy"), zapis=s0.get("zapis"), magazyn=s0.get("magazyn"))
            # ---------------------------------------------------------------- B02
            k0 = p.klient('"stan"')
            av = json.loads(p.luau(AWATAR, "Client"))
            poz = k0.get("poz") or [0, 0, 0]
            p.wynik("B02", bool(gotowe) and bool(aktywny) and k0.get("ui") and K1["xOd"] < poz[0] < K1["brama"]["x"]
                    and k0.get("kamera") == "Custom"
                    and not [n for n in k0.get("wlaczoneCudze", []) if n not in ("BonkEkran",)] and av["widoczne"] > 0
                    and av["bez"] is True and av["bohaterow"] == 0,
                    poz=poz, schowane=k0.get("schowane"), wlaczoneCudze=k0.get("wlaczoneCudze"), awatar=av,
                    kamera=k0.get("kamera"), klasa=p.luau(KLASA, "Client"), podpowiedz=(k0.get("ui") or {}).get("podpowiedz"),
                    inneDzwieki=k0.get("inneDzwieki"), muzyka=k0.get("muzyka"))
            # ---------------------------------------------------------------- B03: dojście do slime'a i trzymany BONK
            slimy = potwory(p, 1, "lesny_slime")
            cel = min(slimy, key=lambda m: (m["x"] - poz[0]) ** 2 + (m["z"] - poz[2]) ** 2)
            p.idz(cel["x"], cel["y"], cel["z"])
            p.klient('"trzymaj", true')
            pierwszy, t_b = czekaj(lambda: gracz(p.serwer('"stan"')).get("bonki", 0) >= 1, 30, 0.3)
            od_wejscia = time.time() - t_wejscia
            p.wynik("B03", bool(pierwszy) and od_wejscia <= 30, od_wejscia_s=round(od_wejscia, 1), od_dojscia_s=round(t_b, 1))
            # ---------------------------------------------------------------- B04
            time.sleep(2.5)
            p.klient('"trzymaj", false')
            g1 = gracz(p.serwer('"stan"'))
            k1 = p.klient('"stan"')
            p.wynik("B04", g1.get("bonki", 0) >= 1 and g1.get("monety", 0) > 0 and (g1.get("moc") or 0) > 1
                    and k1.get("dzwiekow", 0) > 0 and (k1.get("ui") or {}).get("moc") not in (None, "1"),
                    bonki=g1.get("bonki"), monety=g1.get("monety"), moc=g1.get("moc"), ui=(k1.get("ui") or {}).get("moc"),
                    dzwiekow=k1.get("dzwiekow"), podpowiedz=k1.get("podpowiedz"))
            # ---------------------------------------------------------------- B05
            pelna, t_o = czekaj(lambda: len(potwory(p, 1, "lesny_slime")) == 5, 6, 0.3)
            p.wynik("B05", bool(pelna), czas_s=round(t_o, 1))
            # ---------------------------------------------------------------- B06: wilk (życie 90) przy Mocy 10
            p.serwer('"moc", 10')
            wilki = potwory(p, 1, "cierniowy_wilk")
            w = wilki[0]
            p.przenies(w["x"] - 4, w["y"], w["z"])
            time.sleep(0.6)
            p.klient('"bonk"')
            time.sleep(0.5)
            po = [m for m in p.serwer('"potwory", 1') if m["id"] == w["id"]][0]
            p.wynik("B06", po["zywy"] and po["hp"] < po["hpMax"], hp=po["hp"], hpMax=po["hpMax"])
            # ---------------------------------------------------------------- B07
            przed = gracz(p.serwer('"stan"'))
            p.luau(SPAM, "Client")
            time.sleep(0.8)
            po_spam = gracz(p.serwer('"stan"'))
            przyjete = po_spam["trafienia"] - przed["trafienia"]
            odrzucone = po_spam["odrzucone"] - przed["odrzucone"]
            p.wynik("B07", przyjete <= 4 and odrzucone >= 25, przyjete=przyjete, odrzucone=odrzucone)
            # ---------------------------------------------------------------- B09a: bez Mocy serwer cofa za bramę
            bx = K1["brama"]["x"]
            p.przenies(bx + 12, K2["start"][1], K2["start"][2])
            time.sleep(1.5)
            po_cofnieciu = p.poz()
            cofniety = bool(po_cofnieciu) and po_cofnieciu[0] < bx
            # ---------------------------------------------------------------- B08: HOME RUN i zrzuty lotu
            p.serwer('"moc", 1e7')
            sl = potwory(p, 1, "lesny_slime")[0]
            p.przenies(sl["x"] - 5, sl["y"], sl["z"])
            time.sleep(0.8)
            hr0 = gracz(p.serwer('"stan"')).get("homeRuny", 0)
            p.klient('"bonk"')
            if not a.bez_zrzutow:
                time.sleep(0.25)
                p.zrzut(os.path.join(KLATKI, "bonk_home_run.jpg"), (sl["x"] - 16, sl["y"] + 9, sl["z"] - 18),
                        (sl["x"] + 20, sl["y"] + 14, sl["z"]))
            time.sleep(0.5)
            hr1 = gracz(p.serwer('"stan"'))
            p.wynik("B08", hr1.get("homeRuny", 0) > hr0 and hr1.get("najdalej", 0) >= U["lot"]["home_run"],
                    homeRuny=hr1.get("homeRuny"), najdalej=hr1.get("najdalej"))
            p.serwer('"moc", 40')
            if not a.bez_zrzutow:
                tr = potwory(p, 1, "lesny_troll")
                if tr:
                    t = tr[0]
                    p.serwer('"moc", 300')
                    p.przenies(t["x"] - 7, t["y"], t["z"] + 3)
                    time.sleep(0.8)
                    p.klient('"bonk"')
                    time.sleep(0.3)
                    p.zrzut(os.path.join(KLATKI, "bonk_lot.jpg"), (t["x"] - 26, t["y"] + 12, t["z"] + 34),
                            (t["x"] + 14, t["y"] + 10, t["z"]))
            # ---------------------------------------------------------------- B09: brama lasu
            p.serwer('"moc", %d' % K1["brama"]["wymagana"])
            time.sleep(0.5)
            p.przenies(bx - 10, K1["start"][1], K1["start"][2])
            time.sleep(0.6)
            p.idz(bx + 20, K2["start"][1], K2["start"][2])
            przeszedl, t_p = czekaj(lambda: (p.poz() or [0])[0] > bx + 12, 10, 0.4)
            k9 = p.klient('"stan"')
            p.wynik("B09", cofniety and bool(przeszedl) and k9.get("kraina") == 2 and k9.get("odblokowane", 0) >= 2,
                    cofniety=cofniety, przeszedl=bool(przeszedl), kraina=k9.get("kraina"), napis=(k9.get("ui") or {}).get("kraina"),
                    muzyka=k9.get("muzyka"), inneDzwieki=k9.get("inneDzwieki"))
            # ---------------------------------------------------------------- B10: trzy krainy
            p.serwer('"moc", %d' % K2["brama"]["wymagana"])
            krainy_ok = []
            for nr, Kx, plik in ((1, K1, "bonk_las.jpg"), (2, K2, "bonk_bagno.jpg"), (3, K3, "bonk_dzungla.jpg")):
                p.serwer('"kraina", %d' % nr)
                time.sleep(2.0)
                z1 = Kx["zagrody"][0]
                p.przenies(z1["srodek"][0] - 24, z1["srodek"][1], z1["srodek"][2])
                time.sleep(2.0)
                kx = p.klient('"stan"')
                krainy_ok.append({"kraina": nr, "widokow": kx.get("widokow"), "czesci": kx.get("czesciWidokow"),
                                  "naKrainie": kx.get("kraina")})
                if not a.bez_zrzutow:
                    c = z1["srodek"]
                    p.zrzut(os.path.join(KLATKI, plik), (c[0] - 34, c[1] + 14, c[2] - 20), (c[0] + 6, c[1] + 2, c[2]))
            p.wynik("B10", all(k["widokow"] and k["widokow"] > 0 and k["naKrainie"] == k["kraina"] for k in krainy_ok),
                    krainy=krainy_ok)
            # ---------------------------------------------------------------- B11: czas klatki (pełny las)
            na_wierzch()
            p.serwer('"kraina", 1')
            time.sleep(1.5)
            z3 = K1["zagrody"][2]
            p.przenies(z3["srodek"][0] - 20, z3["srodek"][1], z3["srodek"][2])
            time.sleep(2.0)
            p.klient('"pomiar_zeruj"')
            time.sleep(8)
            k11 = p.klient('"stan"')
            p.wynik("B11", k11.get("srKlatki", 1) < 1 / 25 and k11.get("srPetli", 1) < 0.004,
                    srKlatki_ms=round(1000 * k11.get("srKlatki", 0), 1), maksKlatki_ms=round(1000 * k11.get("maksKlatki", 0), 1),
                    srPetli_ms=round(1000 * k11.get("srPetli", 0), 2), maksPetli_ms=round(1000 * k11.get("maksPetli", 0), 2),
                    widokow=k11.get("widokow"), czesci=k11.get("czesciWidokow"))
            # ---------------------------------------------------------------- B12: zapis do magazynu próby
            ok_z = p.serwer('"zapisz"')
            odczyt = p.serwer('"odczyt"')
            rek = odczyt.get("rekord") or {}
            g12 = gracz(p.serwer('"stan"'))
            ponownie = p.serwer('"wczytaj_ponownie"')
            p.wynik("B12", ok_z is True and isinstance(rek, dict) and rek.get("moc") == g12.get("mocBaza")
                    and ponownie.get("moc") == g12.get("mocBaza") and ponownie.get("zapisywalny") is True,
                    zapisano=ok_z, rekord_moc=rek.get("moc") if isinstance(rek, dict) else rek, moc=g12.get("mocBaza"),
                    wersja=rek.get("v") if isinstance(rek, dict) else None)
            # ---------------------------------------------------------------- B13: wyjście i ponowne wejście portalem
            st13 = json.loads(p.luau(ZB.wstaw(ZB.STAN, KONTENER=K), "Server"))
            pw = st13["atrybuty"].get("PowrotPoz")
            pp = st13["atrybuty"].get("PortalPoz")
            p.serwer('"kraina", 1')
            time.sleep(3.2)                                    # przerwa po przejściu (portal.przerwa_s)
            p.przenies(pw[0], pw[1], pw[2] + 1)
            wyszedl, _ = czekaj(lambda: p.luau(GOTOWOSC, "Client").endswith("false"), 6, 0.3)
            time.sleep(1.0)
            k13 = p.klient('"stan"')
            poz13 = p.poz()
            przy_bramie = poz13 and pp and ((poz13[0] - pp[0]) ** 2 + (poz13[2] - pp[2]) ** 2) ** 0.5 < 14
            time.sleep(3.2)
            p.przenies(pp[0], pp[1], pp[2])
            wszedl, _ = czekaj(lambda: p.luau(GOTOWOSC, "Client").endswith("true"), 6, 0.3)
            p.wynik("B13", bool(wyszedl) and not k13.get("aktywny") and not k13.get("ui") and bool(k13.get("wlaczoneCudze"))
                    and przy_bramie and bool(wszedl),
                    przywrocone=k13.get("wlaczoneCudze"), przy_bramie=przy_bramie, wszedl_znow=bool(wszedl))
            # ---------------------------------------------------------------- B14: telefon 667 × 375
            if not a.bez_zrzutow:
                time.sleep(2.0)
                p.klient('"emulacja", Vector2.new(667, 375)')
                time.sleep(1.0)
                z1 = K1["zagrody"][0]
                p.przenies(z1["srodek"][0] - 14, z1["srodek"][1], z1["srodek"][2] - 4)
                time.sleep(1.5)
                k14 = p.klient('"stan"')
                okno = (k14.get("ui") or {}).get("okno")
                pz = p.poz()
                img = p.zrzut(os.path.join(wyj, "telefon_caly.jpg"), (pz[0] - 20, pz[1] + 10, pz[2] - 6),
                              (pz[0] + 14, pz[1] + 1, pz[2]))
                if okno:
                    # okno w punktach ekranu; zrzut może mieć inną skalę niż okno gry — liczymy z proporcji
                    vp = json.loads(p.luau('local v = workspace.CurrentCamera.ViewportSize local i = game:GetService("GuiService"):'
                                           'GetGuiInset() return game:GetService("HttpService"):JSONEncode({ v.X, v.Y, i.Y })', "Client"))
                    sx, sy = img.width / vp[0], img.height / vp[1]
                    y0 = okno[1] + vp[2]                       # AbsolutePosition liczy się pod paskiem Robloxa (wcięcie)
                    wyc = img.crop((int(okno[0] * sx), int(y0 * sy), int((okno[0] + okno[2]) * sx), int((y0 + okno[3]) * sy)))
                    wyc.save(os.path.join(KLATKI, "bonk_telefon.jpg"), quality=90)
                p.wynik("B14", bool(okno) and (k14.get("ui") or {}).get("dotyk") is True,
                        okno=okno, przycisk=(k14.get("ui") or {}).get("przyciskPoz"), gora=(k14.get("ui") or {}).get("goraPoz"))
                p.klient('"emulacja", nil')
            # ---------------------------------------------------------------- B15: konsola
            kons = p.call("get_console_output")["text"]
            linie = [x for x in kons.splitlines() if ("BonkGra" in x or "[BONK]" in x or "Bonk" in x)]
            bledy = [x for x in linie if ("error" in x.lower() or "błąd" in x.lower() or "stack" in x.lower()
                                          or "attempt" in x.lower()) and "zapis" not in x.lower()]
            with open(os.path.join(wyj, "konsola.txt"), "w", encoding="utf-8") as f:
                f.write(kons)
            p.wynik("B15", not bledy, bledy=bledy[:8], wpisow_pakietu=len(linie))
            try:
                p.serwer('"skasuj"')
            except StudioError:
                pass
        finally:
            log("Stop:", p.call("start_stop_play", {"is_start": False})["text"][:80])
            edit, _ = czekaj(p.tryb_edit, 40, 0.5)
            stary = "true" if autostart_przed == "true" else "false"
            try:
                p.luau(ATR_EDIT % stary)
            except StudioError as e:
                log("AutoStart nie przywrócony:", e)
            p.wynik("B16", bool(edit), edit=bool(edit), autostart=stary)
        with open(os.path.join(wyj, "wynik_play.json"), "w", encoding="utf-8") as f:
            json.dump(p.wyniki, f, ensure_ascii=False, indent=1)
        zle = [k for k, v in p.wyniki.items() if not v["ok"]]
        log("WYNIK: %d/%d OK%s" % (len(p.wyniki) - len(zle), len(p.wyniki), (" — błędy: " + ", ".join(zle)) if zle else ""))
        return 1 if zle else 0


if __name__ == "__main__":
    sys.exit(main())
