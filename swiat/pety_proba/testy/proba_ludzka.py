# -*- coding: utf-8 -*-
"""Przejście „po ludzku” z petami (Roblox Studio, tryb Play) — nowy gracz, prawdziwe klawisze i kliknięcia:
las → walki do Złota na pierwsze jajko → wskazówka o jajku → leśne jajko w mieście (E, 5 kliknięć) → wyklucie → pet za graczem → walka
z premią → Kamień Powrotu → bazar → zagroda (E opiekunki) → okno → odstaw / wybierz kliknięciem.

    python -B swiat/pety_proba/testy/proba_ludzka.py <folder wyników POZA repo> [--studio <id>] [--limit-walk 40]
    python -B swiat/pety_proba/testy/proba_ludzka.py --sprawdz

Jak próba dymna (swiat/przejscie_gry/proba_dymna.py): postać jest przestawiana obok potworu, Kamienia Powrotu
i jajka (dojście piechotą zajęłoby minuty), walki oglądane w tempie ×4 (przycisk ×4), wszystkie E, kliknięcia
i klawisze są prawdziwym wejściem. Haczyki pakietów tylko do odczytu stanu. Złota NIE ustawia — zarabia je w walkach.
Czas „w prawdziwej grze” = suma czasów walk przy tempie ×1 (czas ekranu walki ×4) + 3 s karty wyniku + dojście
16 st/s do kolejnego potwora (jak swiat/stan_gracza/symulacja_lasu.py). Zrzuty → swiat/pety_proba/klatki/ (L*).
"""
import io
import json
import math
import os
import re
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (PAKIET, os.path.join(REPO, "tools"), os.path.join(REPO, "tools", "walka"),
           os.path.join(REPO, "swiat", "test_walki_roblox")):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import dane_petow as DP  # noqa: E402

KLATKI = os.path.join(PAKIET, "klatki")
H = 'local H = game:GetService("HttpService") '
LP = H + 'local lp = game:GetService("Players").LocalPlayer '
GR = 'local gracz = game:GetService("Players"):GetPlayers()[1] '
J = ('local function J(v) local t = typeof(v) if t == "Vector3" then return { v.X, v.Y, v.Z } '
     'elseif t == "table" then local o = {} if #v > 0 then for i, b in ipairs(v) do o[i] = J(b) end '
     'else for a, b in v do o[tostring(a)] = J(b) end end return o elseif t == "Instance" then return v:GetFullName() '
     'elseif t == "number" and (v ~= v or v == math.huge or v == -math.huge) then return tostring(v) end return v end ')
KOD = {
    "klient": LP + ('local hrp = lp.Character and lp.Character:FindFirstChild("HumanoidRootPart") '
                    'local cs = lp.PlayerGui:FindFirstChild("ClassSelect") local hud = lp.PlayerGui:FindFirstChild("HUD") '
                    'return H:JSONEncode({ poz = hrp and J(hrp.Position), kotwica = hrp and hrp.Anchored, '
                    'kamera = workspace.CurrentCamera.CameraType.Name, klasa = lp:GetAttribute("Class"), '
                    'wybor = cs ~= nil and cs.Enabled, hud = hud ~= nil and hud.Enabled, zloto = lp:GetAttribute("Gold"), '
                    'poziom = lp:GetAttribute("Level"), cena = lp:GetAttribute("PetyCenaJajka"), '
                    'pety = lp:GetAttribute("PetyLiczba"), aktywny = lp:GetAttribute("PetAktywny") })'),
    "las": ('local k = workspace:FindFirstChild("LasPasGra") if not k then return "{}" end '
            'local s = k.Sygnaly.SterowanieKlienta:Invoke("stan") return H:JSONEncode({ walka = s.walka, '
            'licznik = k:GetAttribute("SerwerLicznikWalk"), przelot = (function() local p = '
            '(k.Sygnaly.SterowaniePasaKlienta:Invoke("stan") or {}).przelot return p ~= nil and p ~= false end)() })'),
    "potwor": LP + ('local k = workspace.LasPasGra local hrp = lp.Character.HumanoidRootPart local poz = lp:GetAttribute("Level") or 1 '
                    'local best, bd for _, c in k.Stan:GetChildren() do local q = c:GetAttribute("Pozycja") '
                    'local pz = c:GetAttribute("Poziom") or 1 if q and c:GetAttribute("Straznik") ~= true and c:GetAttribute("Stan") ~= "zajety" '
                    'and pz <= poz + 1 then local d = (q - hrp.Position).Magnitude if not bd or d < bd then best, bd = c, d end end end '
                    'return H:JSONEncode(if best then { id = best.Name, p = J(best:GetAttribute("Pozycja")), d = bd, '
                    'g = best:GetAttribute("Gatunek"), poziom = best:GetAttribute("Poziom") } else {})'),
    # 26.11.2026: leśne jajko ze scenką Pawła (w mieście przy zagrodzie) — miejsce i przód modelu
    "jajko": ('local k = workspace:FindFirstChild("JajkoKorowePodglad") local m = k and k:FindFirstChild("Jajko korowe") '
              'if not m then return H:JSONEncode({ brak = true }) end local cf = m:GetPivot() '
              'return H:JSONEncode({ p = { cf.Position.X, cf.Position.Y, cf.Position.Z }, '
              'przod = { cf.LookVector.X, cf.LookVector.Z } })'),
    "przestaw": GR + ('local c = gracz.Character if c then local p = Vector3.new(%f, %f, %f) '
                      'c:PivotTo(CFrame.lookAt(p, Vector3.new(%f, p.Y, %f))) c.HumanoidRootPart.AssemblyLinearVelocity = '
                      'Vector3.zero end return "ok"'),
    "kamera_za": LP + ('local cam = workspace.CurrentCamera local h = lp.Character and lp.Character:FindFirstChild('
                       '"HumanoidRootPart") if h then task.delay(0.05, function() cam.CFrame = CFrame.lookAt(h.Position - '
                       'h.CFrame.LookVector * 10 + Vector3.new(0, 4, 0), h.Position + h.CFrame.LookVector * 4) end) end '
                       'return "ok"'),
    "wskazowka": ('local k = workspace:FindFirstChild("WskazowkiGry") if not k then return H:JSONEncode({ brak = true }) end '
                  'local s = k.Sygnaly.SterowanieKlienta:Invoke("stan") return H:JSONEncode({ krok = s.krok, tekst = s.tekst, '
                  'znacznik = s.znacznik, jajko = s.jajko, pety = s.pety })'),
    "pety": 'return H:JSONEncode(J(workspace.PetyProba.Sygnaly.SterowanieKlienta:Invoke("stan")))',
    "lup": 'local s = workspace.StanGracza return H:JSONEncode({ lup = s:GetAttribute("OstatniLup") or "", n = s:GetAttribute("LicznikLupow") or 0 })',
    "widoczny": LP + ('local o = lp.PlayerGui for _, n in string.split("%s", ".") do o = o and o:FindFirstChild(n) end '
                      'if not o then return "false" end local a = o while a and a:IsA("GuiObject") do '
                      'if not a.Visible then return "false" end a = a.Parent end '
                      'return tostring(a and (not a:IsA("ScreenGui") or a.Enabled))'),
    "chmury": 'local k = workspace:FindFirstChild("TeleportChmury") return tostring(k and k:GetAttribute("Trwa"))',
    "faza": ('local k = workspace:FindFirstChild("TeleportChmury") local s = k and k.Sygnaly.SterowanieKlienta:Invoke("stan") '
             'return tostring(s and s.biezacy and s.biezacy.faza)'),
    "bez_nazwy": ('local SG = game:GetService("StarterGui") for _, t in { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Chat } do '
                  'pcall(function() SG:SetCoreGuiEnabled(t, false) end) end return "ok"'),
    "kamien": ('local k = workspace.LasPasGra local p = k.Punkty:FindFirstChild("KamienPowrotu") '
               'return H:JSONEncode(J(p and (p:IsA("BasePart") and p.Position or p:GetPivot().Position) or false))'),
}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def sprawdz_kod():
    import luau_mini as LM
    bledy = []
    for nazwa, szablon in KOD.items():
        kod = re.sub(r"%[sdf]", "0", szablon)
        if "local function J" not in kod:
            kod = H + J + kod
        try:
            LM.Parser(kod, nazwa, LM.Interpreter()).program()
        except LM.BladSkladni as e:
            bledy.append("%s: %s" % (nazwa, e))
    print("sprawdz: %d kawałków Luau, %s" % (len(KOD), "OK" if not bledy else "BŁĘDY:\n  " + "\n  ".join(bledy)))
    return 0 if not bledy else 1


def main():
    argv = sys.argv[1:]
    if "--sprawdz" in argv:
        return sprawdz_kod()
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    try:
        w_repo = os.path.commonpath([os.path.normcase(wyj), os.path.normcase(REPO)]) == os.path.normcase(REPO)
    except ValueError:
        w_repo = False
    if w_repo:
        sys.exit("Folder wyników leży w repozytorium — podaj folder poza repo")
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    limit = int(argv[argv.index("--limit-walk") + 1]) if "--limit-walk" in argv else 40
    os.makedirs(wyj, exist_ok=True)
    os.makedirs(KLATKI, exist_ok=True)
    D = DP.dane_z_przypadkami()
    G = D["polozenia"]
    from cel_studio import wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    from PIL import Image  # noqa: E402
    WYNIKI, LISTA = {}, []

    def zapisz(k, v):
        WYNIKI[k] = v
        with open(os.path.join(wyj, "wyniki.json"), "w", encoding="utf-8") as f:
            json.dump(WYNIKI, f, ensure_ascii=False, indent=1)

    def punkt(kod, ok, opis):
        LISTA.append((kod, "OK" if ok is True else ("BŁĄD" if ok is False else "?"), opis))
        log("%s %s — %s" % (kod, LISTA[-1][1], opis))
        with open(os.path.join(wyj, "lista.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join("%s %-4s %s" % x for x in LISTA) + "\n")

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
                except Exception as e:  # noqa: BLE001
                    if i == proby - 1:
                        raise
                    log("luau: ponawiam:", str(e)[:150])
                    time.sleep(5)

        def js(kod, dm="Client"):
            w = json.loads(luau(H + J + kod, dm))
            return {} if w == [] else w

        def zrzut(nazwa):
            r = call("screen_capture", {"capture_id": "lud_" + nazwa}, timeout=150)
            if r["is_error"] or not r.get("images"):
                return
            im = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
            if im.width > 1280:
                im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
            im.save(os.path.join(KLATKI, nazwa + ".jpg"), "JPEG", quality=85)
            log("zrzut", nazwa)

        def klawisz(kod, ms=None):
            akcje = ([{"action": "keyDown", "key_code": kod}, {"action": "wait", "wait_time_ms": ms},
                      {"action": "keyUp", "key_code": kod}] if ms else [{"action": "keyPress", "key_code": kod}])
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": akcje})

        def klik(sciezka):
            r = call("user_mouse_input", {"datamodel_type": "Client", "actions": [
                {"action": "moveTo", "instance_path": "LocalPlayer.PlayerGui." + sciezka},
                {"action": "mouseButtonClick", "mouse_button": "left"}]})
            return not r["is_error"]

        def czekaj_na(w, limit_s, co=0.5):
            t0 = time.time()
            while time.time() - t0 < limit_s:
                x = w()
                if x:
                    return x
                time.sleep(co)
            return None

        def klient():
            return js(KOD["klient"])

        def przestaw(p, patrz):
            luau(KOD["przestaw"] % (p[0], p[1], p[2], patrz[0], patrz[2]), "Server")

        def widoczny(sc):
            return luau(KOD["widoczny"] % sc, "Client") == "true"

        czas_gry = 0.0
        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        try:
            czekaj_na(lambda: "Client" in call("get_studio_state")["text"] and luau(
                'local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)',
                "Client") == "true", 90, 1)
            luau(KOD["bez_nazwy"], "Client")
            czekaj_na(lambda: klient().get("wybor"), 30, 1)
            for _ in range(10):
                klawisz("Return")
                time.sleep(1.5)
                k = klient()
                if k.get("klasa") and not k.get("wybor") and k.get("kamera") == "Custom":
                    break
            punkt("L01", bool(klient().get("klasa")), "klasa %s, Złoto %s, cena jajka %s" % (k.get("klasa"), k.get("zloto"),
                                                                                         k.get("cena")))
            # ---------------------------------------------------------------- do lasu przez TELEPORT i chmury
            klik("HUD.LeftColumn.TeleportSlot.Teleport")
            czekaj_na(lambda: luau(KOD["chmury"], "Client") == "true", 8, 0.5)
            czekaj_na(lambda: luau(KOD["faza"], "Client") == "wybor", 10, 0.3)
            klawisz("Right")
            time.sleep(0.8)
            klawisz("Return")
            w_lesie = czekaj_na(lambda: (lambda k: k if (k.get("poz") or [0])[0] >= 1066 else None)(klient()), 15, 0.5)
            czekaj_na(lambda: js(KOD["las"]).get("przelot"), 8, 0.4)
            czekaj_na(lambda: (lambda k, l: k if k.get("kamera") == "Custom" and not k.get("kotwica") and not l.get("przelot")
                               else None)(klient(), js(KOD["las"])), 40, 1.0)
            punkt("L02", bool(w_lesie), "w lesie: %s" % (w_lesie or {}).get("poz"))
            czas_gry += 13.4 + 6.0  # przelot przy pierwszym wejściu + dojście do pierwszych slime'ów
            # ---------------------------------------------------------------- walki do Złota na jajko
            walki, wygrane = 0, 0
            k = klient()
            pozycja = k.get("poz")
            while (k.get("zloto") or 0) < (k.get("cena") or 300) and walki < limit:
                p = js(KOD["potwor"])
                if not p.get("p"):
                    time.sleep(2)
                    continue
                q = p["p"]
                if pozycja:
                    czas_gry += min(p.get("d") or 0, 80) / 16.0
                przestaw((q[0] - 4, q[1] + 3.2, q[2]), q)
                luau(KOD["kamera_za"], "Client")
                time.sleep(0.6)
                licz0 = js(KOD["las"]).get("licznik") or 0
                klawisz("E")
                if not czekaj_na(lambda: js(KOD["las"]).get("walka"), 5, 0.3):
                    continue
                t0 = time.time()
                time.sleep(1.2)
                klik("TestWalki2Cutscenka.Kadr.Tempo.Tempo4.Przycisk")
                if walki == 0:
                    zrzut("L03_pierwsza_walka")
                czekaj_na(lambda: widoczny("TestWalki2Cutscenka.Kadr.Wynik.Karta.Zamknij.Przycisk"), 90, 0.8)
                ekran = time.time() - t0
                klik("TestWalki2Cutscenka.Kadr.Wynik.Karta.Zamknij.Przycisk")
                czekaj_na(lambda: klient().get("kamera") == "Custom", 10, 0.5)
                walki += 1
                czas_gry += 1.2 + (ekran - 1.2) * 4 + 3.0
                lup = js(KOD["lup"], "Server")
                wygrane += 1 if ":wygrana:" in lup.get("lup", "") else 0
                time.sleep(1.0)
                k = klient()
                pozycja = k.get("poz")
                log("walka %d: %s, Złoto %s / %s, poziom %s, gra ok. %.1f min" % (walki, lup.get("lup", "").split(":", 1)[-1],
                                                                                 k.get("zloto"), k.get("cena"), k.get("poziom"),
                                                                                 czas_gry / 60))
            zapisz("L03", {"walki": walki, "wygrane": wygrane, "czas_gry_min": round(czas_gry / 60, 1), "klient": k})
            punkt("L03", (k.get("zloto") or 0) >= (k.get("cena") or 300),
                  "Złoto na jajko po %d walkach (%d wygranych), ok. %.1f min gry (poziom %s, Złoto %s)" % (
                      walki, wygrane, czas_gry / 60, k.get("poziom"), k.get("zloto")))
            # ---------------------------------------------------------------- wskazówka o jajku
            w = czekaj_na(lambda: (lambda x: x if x.get("krok") == "f_jajko" else None)(js(KOD["wskazowka"])), 6, 0.5) \
                or js(KOD["wskazowka"])
            zrzut("L04_wskazowka_jajko")
            punkt("L04", w.get("krok") == "f_jajko" and bool(w.get("znacznik")), "krok %s „%s”, znacznik %s" % (
                w.get("krok"), w.get("tekst"), w.get("znacznik")))
            # ---------------------------------------------------------------- jajko (scenka Pawła), E, 5 kliknięć
            # 26.11.2026: starych inkubatorów nie ma — leśne jajko stoi w mieście przy zagrodzie (wskazówka prowadzi przez
            # Kamień Powrotu); postać przestawiona 5 st przed jajo jak przy potworach (dojście zajęłoby minuty)
            mj = js(KOD["jajko"], "Server")
            if mj.get("brak"):
                sys.exit("Brak leśnego jajka ze scenką (Workspace/JajkoKorowePodglad/Jajko korowe)")
            gn, pz = mj["p"], mj["przod"]
            n = math.hypot(pz[0], pz[1]) or 1.0
            stoi = (gn[0] + pz[0] / n * 5.0, gn[1] + 3.0, gn[2] + pz[1] / n * 5.0)
            przestaw(stoi, gn)
            luau(KOD["kamera_za"], "Client")
            time.sleep(1.0)
            zrzut("L05_przy_jajku")
            przed = klient()
            klawisz("E")
            time.sleep(1.2)
            for _ in range(5):
                klawisz("Space")
                time.sleep(0.8)
            zrzut("L06_wyklucie")
            time.sleep(6.0)
            po = klient()
            punkt("L05", (po.get("pety") or 0) == 1 and (po.get("zloto") or 0) == (przed.get("zloto") or 0) - (przed.get("cena") or 0),
                  "Złoto %s → %s, pet %s, następna cena %s" % (przed.get("zloto"), po.get("zloto"), po.get("aktywny"),
                                                               po.get("cena")))
            # ---------------------------------------------------------------- pet za graczem (zwykła kamera)
            p0 = klient().get("poz")
            call("character_navigation", {"datamodel_type": "Client", "x": p0[0] + 30, "y": p0[1], "z": p0[2] - 18}, timeout=60)
            time.sleep(1.0)
            st = js(KOD["pety"])
            zrzut("L07_pet_za_graczem")
            punkt("L06", st.get("mojPet") == po.get("aktywny") and (st.get("odleglosc") or 99) < 12,
                  "za graczem %s, odległość %s" % (st.get("mojPet"), st.get("odleglosc")))
            # ---------------------------------------------------------------- walka z premią peta
            premia = None
            for _ in range(6):
                p = js(KOD["potwor"])
                if not p.get("p"):
                    time.sleep(2)
                    continue
                q = p["p"]
                przestaw((q[0] - 4, q[1] + 3.2, q[2]), q)
                luau(KOD["kamera_za"], "Client")
                time.sleep(0.6)
                klawisz("E")
                if not czekaj_na(lambda: js(KOD["las"]).get("walka"), 5, 0.3):
                    continue
                time.sleep(1.2)
                w_walce = js(KOD["pety"])
                klik("TestWalki2Cutscenka.Kadr.Tempo.Tempo4.Przycisk")
                czekaj_na(lambda: widoczny("TestWalki2Cutscenka.Kadr.Wynik.Karta.Zamknij.Przycisk"), 90, 0.8)
                klik("TestWalki2Cutscenka.Kadr.Wynik.Karta.Zamknij.Przycisk")
                premia = czekaj_na(lambda: (lambda x: x if "od peta" in str(x.get("komunikat")) else None)(js(KOD["pety"])),
                                   10, 0.3)
                if premia:
                    zrzut("L08_premia_przy_lupie")
                po_walce = js(KOD["pety"])
                zapisz("L07", {"w_walce": w_walce, "premia": premia, "po_walce": po_walce,
                               "lup": js(KOD["lup"], "Server")})
                punkt("L07", w_walce.get("towarzysze") == 0 and bool(po_walce.get("mojPet")),
                      "w walce petów %s, po walce za graczem %s, napis premii %r" % (
                          w_walce.get("towarzysze"), po_walce.get("mojPet"), (premia or {}).get("komunikat")))
                break
            # ---------------------------------------------------------------- powrót, bazar, zagroda
            kam = js(KOD["kamien"])
            if kam:
                przestaw((kam[0] + 0.5, kam[1] + 3, kam[2] + 5.5), kam)
                luau(KOD["kamera_za"], "Client")
                time.sleep(0.8)
                klawisz("E")
                czekaj_na(lambda: (klient().get("poz") or [9999])[0] < 1066, 8, 0.5)
            ez, kier = G["zagroda_e"], G["zagroda_kier"]
            k = klient()
            call("character_navigation", {"datamodel_type": "Client", "x": ez[0] + kier[0] * 1.2, "y": ez[1] + 3,
                                          "z": ez[2] + kier[2] * 1.2}, timeout=90)
            time.sleep(1.5)
            przestaw((ez[0] + kier[0] * 1.2, ez[1] + 3, ez[2] + kier[2] * 1.2), (ez[0] - kier[0] * 5, 0, ez[2] - kier[2] * 5))
            luau(KOD["kamera_za"], "Client")
            time.sleep(1.0)
            zrzut("L09_zagroda")
            klawisz("E", 300)
            okno = czekaj_na(lambda: widoczny("PetyProbaOkno.Ramka"), 5, 0.4)
            time.sleep(0.6)
            zrzut("L10_okno_zagrody")
            klik("PetyProbaOkno.Ramka.Odstaw")
            time.sleep(1.2)
            odst = klient().get("aktywny")
            pet = po.get("aktywny")
            klik("PetyProbaOkno.Ramka.Lista.Wiersz_%s.Wybierz" % pet)
            time.sleep(1.2)
            wyb = klient().get("aktywny")
            zrzut("L11_okno_po_wyborze")
            klik("PetyProbaOkno.Ramka.Zamknij")
            punkt("L08", bool(okno) and odst is None and wyb == pet,
                  "okno po E opiekunki %s, po „Odstaw” aktywny %s, po „Wybierz” %s" % (bool(okno), odst, wyb))
            out = call("get_console_output")["text"]
            zle = [l for l in out.splitlines() if "PetyProba" in l and ("rror" in l or "Script '" in l)]
            zapisz("L09", zle[:30])
            punkt("L09", not zle, "błędów PetyProba w konsoli: %d" % len(zle))
        finally:
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
    return 1 if any(x[1] == "BŁĄD" for x in LISTA) else 0


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    sys.exit(main() or 0)
