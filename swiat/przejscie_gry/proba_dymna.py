# -*- coding: utf-8 -*-
"""Próba dymna całej gry (Roblox Studio, tryb Play) — do powtarzania po każdej zmianie, ok. 4–6 minut.

    python -B swiat/przejscie_gry/proba_dymna.py <folder wyjściowy POZA repo> [--studio <studio_id>] [--bez-zrzutow]

Droga gracza: Play → ekran wyboru klasy (Enter) → HUD TELEPORT → chmury (strzałka w prawo + Enter = Las) →
pierwsza walka ze slime'em (prawdziwe E, tempo ×4, ZAMKNIJ) → Kamień Powrotu (E) → bazar → trener (E) → Siła
(kliknięcie GRAJ, spacja = START, cała runda) → WYJDŹ → koniec. Na każdy punkt wynik OK / NIE (albo „?” — tylko
pomiar bez progu). Na końcu Studio wraca do trybu Edit.

Warunki: Studio w trybie Edit, otwarte miejsce gry, zbudowane kontenery TeleportChmury, LasPas + LasPasGra,
TestWalki2, MiasteczkoBazar + MiasteczkoBazarGra, TreningProba (sprawdza D00). Skrypt niczego nie zapisuje w miejscu
i niczego nie publikuje. W trybie Play zmienia tylko położenie WŁASNEJ postaci (przestawienie przy potworze, Kamieniu
Powrotu i trenerze — tak jak próby pakietów; dojście piechotą zajęłoby minuty) i przed każdym E ustawia kamerę za
plecami postaci (podpowiedź E Roblox pokazuje się tylko na ekranie). Wszystkie przyciski i klawisze są
prawdziwym wejściem (user_mouse_input / user_keyboard_input). Haczyki pakietów są używane WYŁĄCZNIE do odczytu
stanu („stan”), nigdy do sterowania grą.

Wyniki: <wyj>/wyniki.json, <wyj>/lista.txt, zrzuty <wyj>/<nazwa>.jpg (bez filmów). Nazwa konta w zapisach zamieniana
na <gracz> (repo jest publiczne) — mimo to folder wyjściowy ma być poza repozytorium.

LISTA KONTROLNA:
  D00 Edit: stoją wszystkie potrzebne kontenery
  D01 start: ekran ładowania znika, ekran wyboru klasy, Enter → atrybut Class, kamera Custom, HUD włączony (≤ 60 s)
  D02 teleport do lasu: klik TELEPORT → chmury (TeleportChmury.Trwa), → + Enter → postać w lesie (x ≥ 1066) ≤ 12 s,
      po przelocie (jeśli był) kamera Custom i postać nie zakotwiczona ≤ 30 s
  D03 walka: prawdziwe E przy slime → walka (SerwerLicznikWalk +1), klik ×4, karta wyniku, klik ZAMKNIJ → kamera Custom
  D04 nagroda: złoto gracza (atrybut Gold) po wygranej większe niż przed — 17.11.2026 NIE (znana dziura w pętli:
      łup z karty walki nie trafia do gracza); wynik informacyjny, nie przerywa próby
  D05 powrót: E przy Kamieniu Powrotu → start bazaru (≤ 4 st od (990; 3; −697)) albo stare miasteczko, gdy bazaru brak
  D06 trener: E przy trenerze w bazarze → okno wyboru mini-gry (TreningProba: wybor = true, zrodlo = bazar)
  D07 runda Siły: klik GRAJ → stanowisko, spacja → runda, po rundzie panel podsumowania (≤ 75 s)
  D08 wyjście: klik WYJDŹ → ekran „brak”, kamera Custom, postać przy trenerze (≤ 3 st od miejsca sprzed wejścia)
  D09 czas klatki: 3 s RenderStepped w lesie i w bazarze (śr. / p95) — „?” gdy okno Studio w tle (> 50 ms)
  D10 konsola: brak śladów błędów (wiersze „Workspace.…:<linia>” / „error” / „błąd”) ze skryptów gry; ślady
      narzędzia Studio (AssistantCommand) pomijane; ostrzeżenia policzone osobno
  D11 wskazówka celu po starcie (pakiet swiat/wskazowki_gry): linijka widoczna, krok „a_teleport”, strzałka przy
      TELEPORT; bez kontenera WskazowkiGry — „?” (pakiet niewdrożony)
  D12 wskazówka w lesie po przelocie: krok „b_potwor” i znacznik nad potworem; bez kontenera — „?”
  D13 dźwięk w walce: grało coś (OstatnieDzwiekiZagrane > 0 na kontenerze lasu); wypisany zestaw (arkusz /
      wbudowany) i czy arkusz się wczytał (OstatniArkuszNiewczytany)
  D04 czeka do 10 s na złoto: ze swiat/stan_gracza łup trafia do gracza po zamknięciu ekranu walki
"""
import io
import json
import math
import os
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"),
           os.path.join(REPO, "swiat", "test_walki2", "testy")):
    sys.path.insert(0, _s)

H = 'local H = game:GetService("HttpService") '
J = ('local function J(v) local t = typeof(v) if t == "Vector3" then return { v.X, v.Y, v.Z } '
     'elseif t == "CFrame" then return { v.X, v.Y, v.Z } '
     'elseif t == "table" then local o = {} if #v > 0 then for i, b in ipairs(v) do o[i] = J(b) end '
     'else for a, b in v do o[tostring(a)] = J(b) end end return o '
     'elseif t == "number" and (v ~= v or v == math.huge or v == -math.huge) then return tostring(v) '
     'elseif t == "Instance" then return v.Name elseif t == "EnumItem" then return v.Name end return v end ')
GR = 'local gracz = game:GetService("Players"):GetPlayers()[1] '
LP = 'local lp = game:GetService("Players").LocalPlayer '
KONTENERY = ["TeleportChmury", "LasPas", "LasPasGra", "TestWalki2", "MiasteczkoBazar", "MiasteczkoBazarGra",
             "TreningProba"]
START_BAZARU = (990.0, 3.0, -697.0)
KAMIEN = ((1106.5, 6.5, -712.3), (1106.5, -717.0))        # stoisko i punkt, na który patrzy postać (krótki pas D-096)
TRENER = ((942.0, 6.5, -724.0), (942.0, -729.0))
WYNIKI = {}
LISTA = []


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def odl_xz(a, b):
    return math.hypot(a[0] - b[0], a[2] - b[2])


def main():
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    if os.path.commonpath([wyj, REPO]) == REPO:
        sys.exit("Folder wyjściowy ma być poza repozytorium (zrzuty i nazwa konta nie trafiają do git): %s" % wyj)
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    bez_zrzutow = "--bez-zrzutow" in argv
    os.makedirs(wyj, exist_ok=True)

    from cel_studio import wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    try:
        from czuwanie import nie_usypiaj  # noqa: E402
    except ImportError:
        def nie_usypiaj():
            return False
    try:
        from PIL import Image  # noqa: E402
    except ImportError:
        Image = None

    nazwa_gracza = [None]

    def anonim(v):
        tekst = json.dumps(v, ensure_ascii=False)
        if nazwa_gracza[0]:
            tekst = tekst.replace(nazwa_gracza[0], "<gracz>")
        return json.loads(tekst)

    def zapisz(klucz, wartosc):
        WYNIKI[klucz] = anonim(wartosc)
        with open(os.path.join(wyj, "wyniki.json"), "w", encoding="utf-8") as f:
            json.dump(WYNIKI, f, ensure_ascii=False, indent=1)

    def punkt(kod, ok, opis):
        opis = anonim(opis) if isinstance(opis, str) else opis
        LISTA.append((kod, "OK" if ok is True else ("NIE" if ok is False else "?"), opis))
        log("%s %s — %s" % (kod, LISTA[-1][1], opis))
        with open(os.path.join(wyj, "lista.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join("%s %-3s %s" % x for x in LISTA) + "\n")

    with StudioMCP(timeout=180) as s:
        sid = wybierz_studio(s, studio)

        def call(n, a=None, timeout=None):
            d = dict(a or {})
            d["studio_id"] = sid
            return s.call(n, d, timeout=timeout)

        def luau(kod, dm, proby=3):
            for i in range(proby):
                try:
                    r = call("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=120)
                    if r["is_error"]:
                        raise StudioError(r["text"][:800])
                    return r["text"].strip()
                except Exception as e:  # noqa: BLE001 — Studio czasem chwilę nie odpowiada
                    if i == proby - 1:
                        raise
                    log("luau: ponawiam po błędzie:", str(e)[:200])
                    time.sleep(5)

        def js(kod, dm):
            w = luau(H + J + kod, dm)
            try:
                return json.loads(w)
            except ValueError:
                return {}

        def stan_studio():
            return call("get_studio_state")["text"]

        def zrzut(nazwa):
            if bez_zrzutow:
                return
            nie_usypiaj()
            r = call("screen_capture", {"capture_id": "dymna_" + nazwa}, timeout=150)
            if r["is_error"] or not r.get("images"):
                log("zrzut %s: błąd %s" % (nazwa, r["text"][:120]))
                return
            dane = r["images"][0]
            if Image is not None:
                im = Image.open(io.BytesIO(dane)).convert("RGB")
                if im.width > 1280:
                    im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
                im.save(os.path.join(wyj, nazwa + ".jpg"), "JPEG", quality=85)
            else:
                with open(os.path.join(wyj, nazwa + ".png"), "wb") as f:
                    f.write(dane)

        def klawisz(kod, przytrzymaj_ms=None):
            if przytrzymaj_ms:
                akcje = [{"action": "keyDown", "key_code": kod}, {"action": "wait", "wait_time_ms": przytrzymaj_ms},
                         {"action": "keyUp", "key_code": kod}]
            else:
                akcje = [{"action": "keyPress", "key_code": kod}]
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": akcje})

        def klik(sciezka):
            r = call("user_mouse_input", {"datamodel_type": "Client", "actions": [
                {"action": "moveTo", "instance_path": "LocalPlayer.PlayerGui." + sciezka},
                {"action": "mouseButtonClick", "mouse_button": "left"}]})
            return not r["is_error"]

        def czekaj_na(warunek, limit, co=0.5):
            t0 = time.time()
            while time.time() - t0 < limit:
                w = warunek()
                if w:
                    return w
                time.sleep(co)
            return None

        def klient():
            return js(LP + 'local hrp = lp.Character and lp.Character:FindFirstChild("HumanoidRootPart") '
                      'local cs = lp.PlayerGui:FindFirstChild("ClassSelect") local hud = lp.PlayerGui:FindFirstChild("HUD") '
                      'return H:JSONEncode({ poz = hrp and J(hrp.Position), kotwica = hrp and hrp.Anchored, '
                      'kamera = workspace.CurrentCamera.CameraType.Name, klasa = lp:GetAttribute("Class"), '
                      'wybor = cs ~= nil and cs.Enabled, hud = hud ~= nil and hud.Enabled, zloto = lp:GetAttribute("Gold"), '
                      'xp = lp:GetAttribute("XP") })', "Client")

        def przestaw(p, patrz):
            luau(GR + 'local c = gracz.Character if c then local p = Vector3.new(%r, %r, %r) '
                 'c:PivotTo(CFrame.lookAt(p, Vector3.new(%r, p.Y, %r))) c.HumanoidRootPart.AssemblyLinearVelocity = '
                 'Vector3.zero end return "ok"' % (p[0], p[1], p[2], patrz[0], patrz[1]), "Server")

        def stan_lasu():   # odczyt: klient potworów pasa
            return js('local k = workspace:FindFirstChild("LasPasGra") if not k then return "{}" end '
                      'local s = k.Sygnaly.SterowanieKlienta:Invoke("stan") return H:JSONEncode({ walka = s.walka, '
                      'podpowiedz = s.podpowiedz, najblizszy = s.najblizszy, licznik = k:GetAttribute("SerwerLicznikWalk"), '
                      'przelot = (function() local p = (k.Sygnaly.SterowaniePasaKlienta:Invoke("stan") or {}).przelot '
                      'return p ~= nil and p ~= false end)() })', "Client")

        def kamera_za():
            # tylko kamera testu: po przestawieniu postaci kamera Custom zostaje zwrócona tam, gdzie patrzyła wcześniej,
            # a podpowiedź E Roblox pokazuje się wyłącznie na ekranie — bez tego E „nic nie robi” (fałszywe NIE)
            luau(LP + 'local cam = workspace.CurrentCamera local h = lp.Character and lp.Character:FindFirstChild('
                 '"HumanoidRootPart") if h then task.delay(0.05, function() cam.CFrame = CFrame.lookAt(h.Position - '
                 'h.CFrame.LookVector * 10 + Vector3.new(0, 4, 0), h.Position + h.CFrame.LookVector * 4) end) end '
                 'return "ok"', "Client")
            time.sleep(0.5)

        def stan_treningu():   # odczyt: klient Training Center
            return js('local k = workspace:FindFirstChild("TreningProba") if not k then return "{}" end '
                      'local s = k.Sygnaly.SterowanieKlienta:Invoke("stan") return H:JSONEncode({ ekran = s.ekran, '
                      'wybor = s.wybor, zrodlo = s.zrodlo, kamera = s.kamera })', "Client")

        def stan_wskazowek():   # odczyt: klient wskazówek (None = brak kontenera WskazowkiGry)
            w = js('local k = workspace:FindFirstChild("WskazowkiGry") if not k then return H:JSONEncode({ brak = true }) end '
                   'local s = k.Sygnaly.SterowanieKlienta:Invoke("stan") return H:JSONEncode({ krok = s.krok, tekst = s.tekst, '
                   'widoczne = s.widoczne, strzalka = s.strzalka, znacznik = s.znacznik, miejsce = s.miejsce, '
                   'ukryte = s.ukryte })', "Client")
            return None if w.get("brak") else w

        def widoczny(sciezka):
            return luau(LP + 'local o = lp.PlayerGui for _, n in string.split("%s", ".") do o = o and o:FindFirstChild(n) end '
                        'if not o then return "false" end local a = o while a and a:IsA("GuiObject") do '
                        'if not a.Visible then return "false" end a = a.Parent end '
                        'return tostring(a and (not a:IsA("ScreenGui") or a.Enabled))' % sciezka, "Client") == "true"

        def klatka(miejsce):
            w = js('local RS = game:GetService("RunService") local t = {} local t0 = os.clock() '
                   'while os.clock() - t0 < 3 do table.insert(t, RS.RenderStepped:Wait()) end table.sort(t) '
                   'local s = 0 for _, x in t do s += x end '
                   'return H:JSONEncode({ sr = s / #t * 1000, p95 = t[math.max(1, math.floor(#t * 0.95))] * 1000 })', "Client")
            w["miejsce"] = miejsce
            return w

        # ------------------------------------------------------------------ D00 Edit
        edit = js('local o = {} for _, n in { %s } do o[n] = workspace:FindFirstChild(n) ~= nil end return H:JSONEncode(o)'
                  % ", ".join('"%s"' % n for n in KONTENERY), "Edit")
        zapisz("D00", edit)
        brak = [n for n in KONTENERY if not edit.get(n)]
        punkt("D00", not brak, "brak kontenerów: %s" % (", ".join(brak) if brak else "—"))
        if "Current Studio Mode: Edit" not in stan_studio():
            sys.exit("Studio nie jest w trybie Edit — zatrzymaj Play i uruchom próbę jeszcze raz.")

        t_start = time.time()
        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        try:
            # -------------------------------------------------------------- D01 start
            czekaj_na(lambda: "Client" in stan_studio() and luau(
                LP + 'return tostring(lp ~= nil and lp.Character ~= nil)', "Client") == "true", 90, 1)
            nazwa_gracza[0] = luau(LP + 'return lp.Name', "Client")
            ekran_wyboru = czekaj_na(lambda: klient().get("wybor"), 30, 1)
            zrzut("01_wybor_klasy")
            kl = {}
            for _ in range(10):
                klawisz("Return")
                time.sleep(1.5)
                kl = klient()
                if kl.get("klasa") and not kl.get("wybor") and kl.get("kamera") == "Custom":
                    break
            t1 = time.time() - t_start
            zapisz("D01", {"ekran_wyboru": bool(ekran_wyboru), "klient": kl, "sekundy": t1})
            punkt("D01", bool(ekran_wyboru) and bool(kl.get("klasa")) and kl.get("kamera") == "Custom" and kl.get("hud")
                  and t1 <= 60, "klasa %s, kamera %s, HUD %s, %.0f s od Play" % (kl.get("klasa"), kl.get("kamera"),
                                                                                  kl.get("hud"), t1))
            zrzut("02_start")

            # -------------------------------------------------------------- D11 wskazówka po starcie
            w11 = czekaj_na(lambda: (lambda w: w if (w is None or w.get("widoczne")) else None)(stan_wskazowek()), 6, 0.5)
            w11 = stan_wskazowek() if w11 is None else w11
            zapisz("D11", w11)
            if w11 is None:
                punkt("D11", None, "brak Workspace/WskazowkiGry — pakiet niewdrożony")
            else:
                punkt("D11", bool(w11.get("widoczne")) and w11.get("krok") == "a_teleport" and bool(w11.get("strzalka")),
                      "krok %s „%s”, strzałka przy TELEPORT %s" % (w11.get("krok"), w11.get("tekst"), w11.get("strzalka")))

            # -------------------------------------------------------------- D02 teleport do lasu
            klik("HUD.LeftColumn.TeleportSlot.Teleport")
            chmury = czekaj_na(lambda: luau('local k = workspace:FindFirstChild("TeleportChmury") '
                                            'return tostring(k and k:GetAttribute("Trwa"))', "Client") == "true", 8, 0.5)
            # klawisze działają dopiero w fazie „wybor” (makieta gotowa) — wcześniej strzałka przepada
            # i Enter wybiera Miasteczko (start bazaru); odczyt fazy haczykiem „stan” (tylko odczyt)
            faza = czekaj_na(lambda: luau('local k = workspace:FindFirstChild("TeleportChmury") local s = k and '
                                          'k.Sygnaly.SterowanieKlienta:Invoke("stan") return tostring(s and s.biezacy '
                                          'and s.biezacy.faza)', "Client") == "wybor", 10, 0.3)
            zrzut("03_chmury")
            klawisz("Right")
            time.sleep(0.8)
            klawisz("Return")
            w_lesie = czekaj_na(lambda: (lambda k: k if (k.get("poz") or [0])[0] >= 1066 else None)(klient()), 12, 0.5)
            zapisz("D02_faza_wyboru", bool(faza))
            # przelot przy pierwszym wejściu rusza ok. 1–4 s po końcu chmur; w czasie przelotu walki są odrzucane
            przelot_byl = czekaj_na(lambda: stan_lasu().get("przelot"), 8, 0.4) if w_lesie else None
            po_przelocie = czekaj_na(lambda: (lambda k, l: k if (k.get("kamera") == "Custom" and not k.get("kotwica")
                                                                  and not l.get("przelot")) else None)(klient(), stan_lasu()),
                                     30, 1.0)
            zapisz("D02_przelot", bool(przelot_byl))
            zapisz("D02", {"chmury": bool(chmury), "w_lesie": w_lesie, "po_przelocie": po_przelocie})
            punkt("D02", bool(chmury) and bool(w_lesie) and bool(po_przelocie),
                  "chmury %s, w lesie %s, po przelocie kamera %s" % (bool(chmury), (w_lesie or {}).get("poz"),
                                                                     (po_przelocie or {}).get("kamera")))
            zrzut("04_las")
            kl9 = [klatka("las (przybycie)")]
            w12 = stan_wskazowek()
            zapisz("D12", w12)
            if w12 is None:
                punkt("D12", None, "brak Workspace/WskazowkiGry — pakiet niewdrożony")
            else:
                punkt("D12", bool(w12.get("widoczne")) and w12.get("krok") == "b_potwor" and bool(w12.get("znacznik")),
                      "miejsce %s, krok %s „%s”, znacznik %s" % (w12.get("miejsce"), w12.get("krok"), w12.get("tekst"),
                                                               w12.get("znacznik")))

            # -------------------------------------------------------------- D03 walka + D04 nagroda
            zloto0 = klient().get("zloto") or 0
            licz0 = stan_lasu().get("licznik") or 0
            walka = None
            proby = []
            for _ in range(8):
                p = js('local k = workspace.LasPasGra local hrp = game:GetService("Players").LocalPlayer.Character'
                       '.HumanoidRootPart local best, bd for _, c in k.Stan:GetChildren() do local q = c:GetAttribute('
                       '"Pozycja") if q and c:GetAttribute("Gatunek") == "lesny_slime" then local d = (q - hrp.Position)'
                       '.Magnitude if not bd or d < bd then best, bd = c, d end end end return H:JSONEncode(if best then '
                       '{ id = best.Name, p = J(best:GetAttribute("Pozycja")) } else {})', "Client")
                if not p.get("p"):
                    proby.append("brak slime'a")
                    break
                q = p["p"]
                przestaw((q[0] - 4, q[1] + 3.2, q[2]), (q[0], q[2]))
                kamera_za()
                klawisz("E")
                if czekaj_na(lambda: stan_lasu().get("walka"), 5, 0.4):
                    walka = p["id"]
                    break
                proby.append(p["id"])
            licz1 = stan_lasu().get("licznik") or 0
            karta = False
            if walka:
                time.sleep(1.5)
                klik("TestWalki2Cutscenka.Kadr.Tempo.Tempo4.Przycisk")
                zrzut("05_walka")
                karta = czekaj_na(lambda: widoczny("TestWalki2Cutscenka.Kadr.Wynik.Karta.Zamknij.Przycisk"), 60, 1.0)
                zrzut("06_karta_wyniku")
                klik("TestWalki2Cutscenka.Kadr.Wynik.Karta.Zamknij.Przycisk")
            po_walce = czekaj_na(lambda: (lambda k: k if k.get("kamera") == "Custom" else None)(klient()), 10, 0.5) or {}
            zapisz("D03", {"walka_z": walka, "nieudane_E": proby, "licznik": [licz0, licz1], "karta": bool(karta),
                           "po_walce": po_walce})
            punkt("D03", bool(walka) and licz1 == licz0 + 1 and bool(karta) and po_walce.get("kamera") == "Custom",
                  "walka z %s (E: %d nieudanych), licznik walk %s → %s, karta wyniku %s, potem kamera %s" % (
                      walka, len(proby), licz0, licz1, bool(karta), po_walce.get("kamera")))
            dz = js('local k = workspace:FindFirstChild("LasPasGra") return H:JSONEncode({ zagrane = k and '
                    'k:GetAttribute("OstatnieDzwiekiZagrane"), zestaw = k and k:GetAttribute("OstatniZestawDzwiekow"), '
                    'niewczytany = k and k:GetAttribute("OstatniArkuszNiewczytany") })', "Client")
            zapisz("D13", dz)
            stan_dz = ("arkusz niewczytany — grały wbudowane" if dz.get("zestaw") == "arkusz" and (dz.get("niewczytany") or 0) > 0
                       else "arkusz" if dz.get("zestaw") == "arkusz" else "dźwięki wbudowane")
            punkt("D13", (dz.get("zagrane") or 0) > 0 if walka else None,
                  "zagrane %s, zestaw %s (%s)" % (dz.get("zagrane"), dz.get("zestaw"), stan_dz))
            # ze stanem gracza łup dochodzi po zamknięciu ekranu walki (albo najpóźniej czas walki + 6 s)
            po_lupie = czekaj_na(lambda: (lambda k: k if (k.get("zloto") or 0) > zloto0 else None)(klient()), 10, 0.5)
            zloto1 = (po_lupie or klient()).get("zloto") or 0
            zapisz("D04", {"zloto": [zloto0, zloto1], "xp": (po_lupie or po_walce).get("xp")})
            punkt("D04", zloto1 > zloto0, "złoto gracza %s → %s (karta walki pokazuje łup; NIE = łup nie trafia do gracza)"
                  % (zloto0, zloto1))

            # -------------------------------------------------------------- D05 Kamień Powrotu
            przestaw(KAMIEN[0], KAMIEN[1])
            time.sleep(0.8)
            kamera_za()
            klawisz("E")
            dom = czekaj_na(lambda: (lambda k: k if (k.get("poz") or [9999])[0] < 1066 else None)(klient()), 6, 0.5) or {}
            pz = dom.get("poz") or [0, 0, 0]
            zapisz("D05", dom)
            punkt("D05", bool(dom) and (odl_xz(pz, START_BAZARU) <= 4 or pz[0] < 500),
                  "po E przy Kamieniu: (%.0f; %.0f; %.0f), od startu bazaru %.1f st" % (pz[0], pz[1], pz[2],
                                                                                         odl_xz(pz, START_BAZARU)))
            kl9.append(klatka("bazar (start)"))
            zrzut("07_bazar")

            # -------------------------------------------------------------- D06 trener
            przestaw(TRENER[0], TRENER[1])
            time.sleep(1.5)
            p_trener = klient().get("poz") or list(TRENER[0])
            tr, proby6 = {}, 0
            for proby6 in range(1, 4):   # bazar ma krótką blokadę po przeniesieniu („Chwila…”) — do 3 naciśnięć
                kamera_za()
                klawisz("E")
                tr = czekaj_na(lambda: (lambda t: t if t.get("wybor") else None)(stan_treningu()), 3, 0.4) or stan_treningu()
                if tr.get("wybor"):
                    break
                time.sleep(1.5)
            hist = js('local b = workspace:FindFirstChild("MiasteczkoBazarGra") local s = b and '
                      'b.Sygnaly.SterowanieKlienta:Invoke("stan") local h = s and s.historia return H:JSONEncode('
                      'J(h and h[#h] or {}))', "Client")
            tr["proby_E"], tr["historia_bazaru"] = proby6, hist
            zapisz("D06", tr)
            punkt("D06", tr.get("wybor") is True and tr.get("zrodlo") == "bazar",
                  "okno wyboru %s, źródło %s, naciśnięć E %s, ostatnie E w bazarze %s" % (
                      tr.get("wybor"), tr.get("zrodlo"), proby6, json.dumps(hist, ensure_ascii=False)[:120]))
            zrzut("08_wybor_minigry")

            # -------------------------------------------------------------- D07 runda Siły
            klik("TreningProba.Ekran.Wybor.Kafelek_sila.Graj")
            stan0 = czekaj_na(lambda: (lambda t: t if t.get("ekran") == "stanowisko" else None)(stan_treningu()), 10, 0.5)
            time.sleep(1.0)
            klawisz("Space")
            runda = czekaj_na(lambda: (lambda t: t if t.get("ekran") == "runda" else None)(stan_treningu()), 8, 0.4)
            time.sleep(6)
            zrzut("09_runda_sila")
            for kod in ("Up", "Left", "Right", "Down"):      # kilka prawdziwych naciśnięć w trakcie rundy
                klawisz(kod)
                time.sleep(0.4)
            podsum = czekaj_na(lambda: (lambda t: t if t.get("ekran") == "podsumowanie" else None)(stan_treningu()), 75, 1.0)
            zapisz("D07", {"stanowisko": bool(stan0), "runda": bool(runda), "podsumowanie": bool(podsum)})
            punkt("D07", bool(stan0) and bool(runda) and bool(podsum),
                  "stanowisko %s, runda %s, podsumowanie %s" % (bool(stan0), bool(runda), bool(podsum)))
            zrzut("10_podsumowanie")

            # -------------------------------------------------------------- D08 wyjście
            klik("TreningProba.Ekran.Podsumowanie.Wyjdz")
            wyj8 = czekaj_na(lambda: (lambda t: t if t.get("ekran") == "brak" else None)(stan_treningu()), 8, 0.5) or {}
            time.sleep(1.0)
            k8 = klient()
            od = odl_xz(k8.get("poz") or [0, 0, 0], p_trener)
            zapisz("D08", {"trening": wyj8, "klient": k8, "od_trenera": od})
            punkt("D08", wyj8.get("ekran") == "brak" and k8.get("kamera") == "Custom" and od <= 3,
                  "ekran %s, kamera %s, %.1f st od miejsca sprzed wejścia" % (wyj8.get("ekran"), k8.get("kamera"), od))

            # -------------------------------------------------------------- D09 klatka
            zapisz("D09", kl9)
            srednie = [x.get("sr") or 0 for x in kl9]
            punkt("D09", None if any(x > 50 for x in srednie) else all((x.get("p95") or 99) < 33.4 for x in kl9),
                  "; ".join("%s: śr. %.1f ms, p95 %.1f ms" % (x["miejsce"], x.get("sr") or 0, x.get("p95") or 0)
                            for x in kl9))

            # -------------------------------------------------------------- D10 konsola
            kons = call("get_console_output", {}, timeout=60)["text"]
            linie = [x.strip() for x in kons.splitlines() if x.strip()]
            slady, ostrz, poprzedni = [], [], ""
            for x in linie:
                if "AssistantCommand" in x or "Stack Begin" in x or "Stack End" in x:
                    poprzedni = x
                    continue
                if (x.startswith("Workspace.") and ":" in x) or "rror" in x or "błąd" in x.lower():
                    slady.append(x[:200])
                elif "przerwane" in x or "nie udało" in x.lower() or "uwaga" in x.lower():
                    ostrz.append(x[:200])
                poprzedni = x
            zapisz("D10", {"slady_bledow": slady[-30:], "ostrzezenia": ostrz[-30:], "wierszy": len(linie)})
            punkt("D10", not slady, "%d wierszy, śladów błędów %d %s, ostrzeżeń %d" % (len(linie), len(slady), slady[:2],
                                                                                     len(ostrz)))
        finally:
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
            for _ in range(60):
                time.sleep(0.5)
                if "Current Studio Mode: Edit" in stan_studio():
                    break
    print("\n".join("%s %-3s %s" % x for x in LISTA))
    print("Czas próby: %.0f s" % (time.time() - t_start))


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    main()
