# -*- coding: utf-8 -*-
"""Krótka próba w Play tylko dla punktów D-107 (walka bez przestojów) jednego biomu — bez reszty listy kontrolnej.

    python -B swiat/las_pas_gra/testy/proba_d107.py <folder wyjściowy poza repo> [las|bagno|dzungla] [--studio <id>] [--bez-zrzutow]

Pełne próby biomów (testy/proba_play.py lasu, Bagna i Dżungli) wołają te same punkty na końcu swojej listy; ta próba
służy do szybkiego sprawdzenia samych liczb D-107 (ok. 5 min): D1 liczba potworów przy 1 i 20 graczach, D2 odradzanie
w zadanym czasie, D3 koszt przy pełnym zestawie w najgęstszej strefie, D4 przegrana ze strażnikiem przy ×4 bez blokady
i rewanż od razu, D5 czas pominiętej walki. Punkty: swiat/las_pas_gra/testy/pomoc_d107.py.

Warunki: Studio w trybie Edit, zbudowane kontenery gry i mapy biomu oraz Workspace/TestWalki2. Skrypt sam włącza
i wyłącza Play (tylko swoje), niczego nie zapisuje w miejscu i niczego nie publikuje. Wyniki: <wyj>/wyniki.json,
<wyj>/lista.txt, zrzuty <wyj>/d107_*.jpg (strefa z pełnym zestawem, chwila po przegranej z dostępnym rewanżem).
Do Bagna i Dżungli gracz wchodzi z bramami otwartymi haczykiem testowym poprzednich biomów.
"""
import io
import json
import os
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TU)))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"),
           os.path.join(REPO, "swiat", "test_walki2", "testy"), TU):
    sys.path.insert(0, _s)
import pomoc_d107 as D107  # noqa: E402

BIOMY = {
    "las": {"pakiet": "las_pas_gra", "kontener": "LasPasGra", "litera": "P", "bramy": []},
    "bagno": {"pakiet": "bagno_pas_gra", "kontener": "BagnoPasGra", "litera": "B", "bramy": ["LasPasGra"]},
    "dzungla": {"pakiet": "dzungla_pas_gra", "kontener": "DzunglaPasGra", "litera": "J", "bramy": ["LasPasGra", "BagnoPasGra"]},
}
HRP = 'local hrp = game:GetService("Players"):GetPlayers()[1].Character.HumanoidRootPart '
LISTA, WYNIKI = [], {}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def main():
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    biom = argv[1] if len(argv) > 1 and argv[1] in BIOMY else "las"
    B = BIOMY[biom]
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    bez_zrzutow = "--bez-zrzutow" in argv
    os.makedirs(wyj, exist_ok=True)
    L = D107.wczytaj_liczby(REPO, B["pakiet"])
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
    K = 'local k = workspace:FindFirstChild("%s") local H = game:GetService("HttpService") ' % B["kontener"]

    def zapisz(klucz, wartosc):
        WYNIKI[klucz] = wartosc
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
                except Exception as e:  # noqa: BLE001 — Studio czasem nie odpowiada chwilę
                    if i == proby - 1:
                        raise
                    log("luau: ponawiam po błędzie:", str(e)[:200])
                    time.sleep(10)

        def js(kod, dm):
            return json.loads(luau(K + kod, dm))

        def stan_studio():
            return call("get_studio_state")["text"]

        def zrzut(nazwa):
            if bez_zrzutow:
                return
            nie_usypiaj()
            r = call("screen_capture", {"capture_id": "d107_" + nazwa}, timeout=150)
            if r["is_error"] or not r.get("images"):
                log("zrzut %s: BŁĄD %s" % (nazwa, r["text"][:120]))
                return
            dane = r["images"][0]
            if Image is not None:
                im = Image.open(io.BytesIO(dane)).convert("RGB")
                if im.width > 1280:
                    im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
                im.save(os.path.join(wyj, "%s_%s.jpg" % (nazwa, biom)), "JPEG", quality=85)
            else:
                with open(os.path.join(wyj, "%s_%s.png" % (nazwa, biom)), "wb") as f:
                    f.write(dane)
            log("zrzut", nazwa)

        def klient_potworow():
            return js('local w = k.Sygnaly.SterowanieKlienta:Invoke("stan") local o = {} for n, v in w do '
                      'if type(v) == "string" or type(v) == "number" or type(v) == "boolean" then o[n] = v end end '
                      'return H:JSONEncode(o)', "Client")

        def odtw(polecenie):
            return json.loads(luau('local H = game:GetService("HttpService") local w = workspace.TestWalki2.Sygnaly.Sterowanie:Invoke(%s) '
                                   'if type(w) ~= "table" then w = { wynik = tostring(w) } end local o = {} '
                                   'for n, v in w do if type(v) == "string" or type(v) == "number" or type(v) == "boolean" then o[n] = v end end '
                                   'return H:JSONEncode(o)' % polecenie, "Client"))

        def przestaw(x, y, z, _kier=None):
            luau(HRP + 'local p = Vector3.new(%f, %f, %f) hrp.Parent:PivotTo(CFrame.lookAt(p, p + Vector3.new(1, 0, 0))) '
                       'hrp.AssemblyLinearVelocity = Vector3.zero return "ok"' % (x, y, z), "Server")

        def nacisnij(klawisz):
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": klawisz}]})

        def czekaj_na(warunek, limit, co=0.5):
            t0 = time.time()
            while time.time() - t0 < limit:
                w = warunek()
                if w:
                    return w
                time.sleep(co)
            return None

        nie_usypiaj()
        if "Current Studio Mode: Edit" not in stan_studio():
            sys.exit("Studio nie jest w trybie Edit — ta próba sama włącza Play")
        edit = json.loads(luau(K + 'return H:JSONEncode({ kontener = k ~= nil and k:GetAttribute("Wygenerowane") == true, '
                                   'skrot = k and k:GetAttribute("Skrot") })', "Edit"))
        zapisz("edit", edit)
        if not edit["kontener"]:
            sys.exit("Brak Workspace/%s w trybie Edit" % B["kontener"])
        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        try:
            czekaj_na(lambda: "Client" in stan_studio() and luau(
                'local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)', "Client") == "true",
                90, 1.0)
            luau(K + 'k:SetAttribute("TestBohater", true) return "ok"', "Server")
            gotowe = czekaj_na(lambda: js('return H:JSONEncode({ s = k:GetAttribute("SerwerGotowy") == true, '
                                          'p = k:GetAttribute("Potworow"), biom = k:GetAttribute("StanBiomu") })', "Server").get("s"), 60, 1.0)
            czekaj_na(lambda: js('return H:JSONEncode({ kl = k:GetAttribute("KlientGotowy") == true })', "Client").get("kl"), 60, 1.0)
            # ekran wyboru klasy trzyma kamerę skryptową i wyłącza podpowiedzi E — Enter wybiera klasę jak gracz
            for _ in range(20):
                wybor = js('local p = game:GetService("Players").LocalPlayer local g = p.PlayerGui:FindFirstChild("ClassSelect") '
                           'local c = workspace.CurrentCamera return H:JSONEncode({ ekran = g ~= nil and g.Enabled, kamera = c.CameraType.Name, '
                           'podpowiedzi = game:GetService("ProximityPromptService").Enabled })', "Client")
                if not wybor["ekran"] and wybor["kamera"] == "Custom" and wybor["podpowiedzi"]:
                    break
                nacisnij("Return")
                time.sleep(1.5)
            # bramy poprzednich biomów otwarte haczykiem testowym (Bagno i Dżungla odsyłają gracza bez Strażnika)
            for kb in B["bramy"]:
                luau('local k = workspace:FindFirstChild("%s") if k then pcall(function() k.Sygnaly.SterowaniePasa:Invoke("otworzBrame") end) end '
                     'return "ok"' % kb, "Server")
            # wejście do biomu: pierwsza strefa; pierwszy przelot / cutscenka blokuje walki — czekamy na jego koniec
            s0 = L["strefy"][0]
            przestaw(s0["x"] - 25, 3.5, s0["z"])
            time.sleep(6)
            wolny = 0
            for _ in range(80):
                st = json.loads(luau('local H = game:GetService("HttpService") local p = game:GetService("Players"):GetPlayers()[1] '
                                     'return H:JSONEncode({ blokada = p:GetAttribute("BlokadaWalki") == true })', "Server"))
                kam = luau('return workspace.CurrentCamera.CameraType.Name', "Client")
                wolny = wolny + 1 if (not st["blokada"] and kam == "Custom") else 0
                if wolny >= 3:
                    break
                time.sleep(1.0)
            zapisz("wejscie", {"gotowe": bool(gotowe), "wolny": wolny >= 3})
            log("wejście do biomu: gotowe=%s, wolny=%s" % (bool(gotowe), wolny >= 3))
            przestaw(s0["x"], 3.5, s0["z"])
            time.sleep(1.0)

            D107.punkty(B["litera"], B["kontener"], L, luau, punkt, zapisz, przestaw, nacisnij, czekaj_na, klient_potworow, odtw,
                        zrzut=zrzut)

            kons = call("get_console_output", {}, timeout=60)["text"]
            linie = [x.strip()[:240] for x in kons.splitlines() if B["kontener"] in x]
            bledy = [x for x in linie if "rror" in x or "błąd" in x.lower() or "Stack" in x]
            zapisz("konsola", {"wierszy": len(linie), "bledy": bledy[:10]})
            punkt(B["litera"] + "D9", not bledy, "konsola: %d wierszy %s, błędów: %d %s" % (len(linie), B["kontener"], len(bledy), bledy[:2]))
        finally:
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
            for _ in range(60):
                time.sleep(0.5)
                if "Current Studio Mode: Edit" in stan_studio():
                    break
            print("\nLISTA KONTROLNA D-107 (%s):" % biom)
            for x in LISTA:
                print("  %s %-4s %s" % x)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
