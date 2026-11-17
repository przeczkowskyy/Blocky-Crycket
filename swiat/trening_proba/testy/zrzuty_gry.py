# -*- coding: utf-8 -*-
"""Zrzuty z gry (tryb Play) do README — tablica wejścia, wybór przy trenerze w bazarze, Siła (trafienie, seria,
pudło), Pancerz w trakcie zamachu, podsumowanie i ekran telefonu 667 × 375 (emulacja: atrybut EmulacjaEkranu).

    python -B swiat/trening_proba/testy/zrzuty_gry.py [--wyj <folder>] [--studio <studio_id>]

Domyślnie zapisuje do swiat/trening_proba/klatki/ (8 plików JPG, szerokość 1280 px) i wypisuje pomiar telefonu:
najmniejszy widoczny napis i przycisk w punktach telefonu. Warunki jak w proba_play.py (Studio w trybie Edit,
zbudowane TreningProba, najlepiej MiasteczkoBazar + MiasteczkoBazarGra). W Play zmienia tylko stan gracza, kamerę
i atrybuty własnego kontenera u klienta; na końcu wraca do trybu Edit. Nazwa konta nie trafia do plików (na
zrzutach jej nie ma: własna postać nie ma nad sobą nazwy, a HUD jej nie pokazuje).
"""
import io
import json
import os
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
KP = 'local k = workspace:FindFirstChild("TreningProba") local H = game:GetService("HttpService") '
GR = 'local gracz = game:GetService("Players"):GetPlayers()[1] '
HRP = GR + 'local hrp = gracz.Character and gracz.Character:FindFirstChild("HumanoidRootPart") '

POMIAR_TELEFONU = r'''
local p = game:GetService("Players").LocalPlayer
local g = p.PlayerGui:FindFirstChild("TreningProba")
local ekran = g and g:FindFirstChild("Ekran")
local k = ekran and ekran:FindFirstChildOfClass("UIScale")
local function widoczny(o)
	while o and o ~= g do
		if o:IsA("GuiObject") and not o.Visible then return false end
		o = o.Parent
	end
	return o == g
end
local napisy, przyciski = {}, {}
for _, d in ekran:GetDescendants() do
	if (d:IsA("TextLabel") or d:IsA("TextButton")) and widoczny(d) and d.Text ~= "" then
		table.insert(napisy, { t = d.Text, pt = d.TextBounds.Y / k.Scale, rozmiar = d.TextSize })
	end
	if d:IsA("TextButton") and widoczny(d) then
		table.insert(przyciski, { n = d.Name, pt = math.min(d.AbsoluteSize.X, d.AbsoluteSize.Y) / k.Scale })
	end
end
local inset = game:GetService("GuiService"):GetGuiInset()
return game:GetService("HttpService"):JSONEncode({
	x = ekran.AbsolutePosition.X + inset.X, y = ekran.AbsolutePosition.Y + inset.Y, w = ekran.AbsoluteSize.X,
	h = ekran.AbsoluteSize.Y, k = k.Scale, vp = { workspace.CurrentCamera.ViewportSize.X, workspace.CurrentCamera.ViewportSize.Y },
	napisy = napisy, przyciski = przyciski })
'''


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def main():
    argv = sys.argv[1:]
    wyj = os.path.abspath(argv[argv.index("--wyj") + 1]) if "--wyj" in argv else os.path.join(PAKIET, "klatki")
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    os.makedirs(wyj, exist_ok=True)
    sys.path.insert(0, PAKIET)
    import dane as DANE  # noqa: E402
    _, D = DANE.dane_z_przypadkami()
    for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
        sys.path.insert(0, _s)
    from cel_studio import wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    from PIL import Image  # noqa: E402

    with StudioMCP(timeout=180) as s:
        sid = wybierz_studio(s, studio)

        def call(n, a=None, timeout=None):
            d = dict(a or {})
            d["studio_id"] = sid
            return s.call(n, d, timeout=timeout)

        def luau(kod, dm):
            r = call("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=120)
            if r["is_error"]:
                raise StudioError(r["text"][:800])
            return r["text"].strip()

        def js(kod, dm):
            return json.loads(luau(KP + kod, dm))

        def hak(polecenie, *argi, dm="Client"):
            nazwa = "SterowanieSerwera" if dm == "Server" else "SterowanieKlienta"
            a = ", ".join(json.dumps(x, ensure_ascii=False) if not isinstance(x, list) else
                          "{ " + ", ".join("{ nr = %d, w = %s, dt = %r }" % (p["nr"], json.dumps(p["w"]), p["dt"]) for p in x) + " }"
                          for x in argi)
            return js('return H:JSONEncode(k.Sygnaly.%s:Invoke("%s"%s))' % (nazwa, polecenie, (", " + a) if a else ""), dm)

        def klawisz(kod):
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": kod}]})

        def zrzut(nazwa, wytnij=None):
            r = call("screen_capture", {"capture_id": "trening_" + nazwa}, timeout=150)
            if r["is_error"] or not r.get("images"):
                log("zrzut %s: BŁĄD %s" % (nazwa, r["text"][:120]))
                return None
            im = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
            if wytnij:
                kx = im.width / wytnij["vp"][0]
                ky = im.height / wytnij["vp"][1]
                im = im.crop((int(wytnij["x"] * kx), int(wytnij["y"] * ky), int((wytnij["x"] + wytnij["w"]) * kx),
                              int((wytnij["y"] + wytnij["h"]) * ky)))
            if im.width != 1280:
                im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
            im.save(os.path.join(wyj, nazwa + ".jpg"), "JPEG", quality=85)
            log("zrzut", nazwa, im.size)
            return im.size

        def przestaw(p, patrz):
            luau(HRP + 'if hrp then local p = Vector3.new(%r, %r, %r) local q = Vector3.new(%r, p.Y, %r) '
                 'gracz.Character:PivotTo(CFrame.lookAt(p, q)) hrp.AssemblyLinearVelocity = Vector3.zero end return "ok"'
                 % (p[0], p[1], p[2], patrz[0], patrz[2]), "Server")

        def kamera_za(odl=10, wys=4):
            luau('local cam = workspace.CurrentCamera local p = game:GetService("Players").LocalPlayer '
                 'local h = p.Character and p.Character:FindFirstChild("HumanoidRootPart") if h then '
                 'cam.CameraType = Enum.CameraType.Custom cam.CFrame = CFrame.lookAt(h.Position - h.CFrame.LookVector * %r '
                 '+ Vector3.new(0, %r, 0), h.Position + h.CFrame.LookVector * 4) end return "ok"' % (odl, wys), "Client")

        def klient():
            return hak("stan")

        def czekaj_na(warunek, limit, co=0.4):
            t0 = time.time()
            while time.time() - t0 < limit:
                w = warunek()
                if w:
                    return w
                time.sleep(co)
            return None

        def teraz_serwera():
            return float(luau("return workspace:GetServerTimeNow()", "Client"))

        def start_rundy():
            hak("start")
            return czekaj_na(lambda: (lambda c: c if c.get("ekran") == "runda" and c.get("runda") else None)(klient()), 10)

        def czekaj_do(t_serwera):
            dt = t_serwera - teraz_serwera()
            if dt > 0:
                time.sleep(dt)

        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        try:
            czekaj_na(lambda: "Client" in call("get_studio_state")["text"] and luau(
                'local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)', "Client") == "true", 90, 1)
            time.sleep(2)
            for _ in range(20):
                w = json.loads(luau('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("ClassSelect") '
                                    'return game:GetService("HttpService"):JSONEncode({ e = g ~= nil and g.Enabled, '
                                    'k = workspace.CurrentCamera.CameraType.Name })', "Client"))
                if not w["e"] and w["k"] == "Custom":
                    break
                klawisz("Return")
                time.sleep(1.5)
            hak("dlugie_napisy", 5)

            # 01 tablica wejścia (kamera gracza za plecami)
            tab = js('local e = k.TablicaWejscia.E return H:JSONEncode({ p = { e.Position.X, e.Position.Y, e.Position.Z }, '
                     'f = { e.CFrame.LookVector.X, 0, e.CFrame.LookVector.Z } })', "Server")
            p, f = tab["p"], tab["f"]
            P0 = [p[0] + f[0] * 5, p[1] + 0.5, p[2] + f[2] * 5]
            przestaw(P0, p)
            time.sleep(1.5)
            kamera_za(12, 7)
            time.sleep(0.8)
            zrzut("01_tablica_wejscia")

            # 02 wybór przy trenerze w bazarze (prawdziwe E)
            zn = DANE._czytaj_json(DANE.ZNACZNIKI)["training_center"]
            przestaw([zn["stoisko"][0], zn["stoisko"][1] + 3.2, zn["stoisko"][2]], zn["podpowiedz"])
            time.sleep(2)
            kamera_za(6, 2)
            time.sleep(0.6)
            klawisz("E")
            czekaj_na(lambda: klient().get("wybor"), 5)
            time.sleep(0.6)
            zrzut("02_wybor_przy_trenerze")

            # 03–05 Siła: trafienie, seria 10, zła strona
            hak("graj", "sila")
            czekaj_na(lambda: klient().get("ekran") == "stanowisko", 10)
            time.sleep(1.5)
            k0 = start_rundy()
            plan = hak("plan", dm="Server")
            t0 = k0["runda"]["t0"]
            zly = [a for a in D["gry"]["sila"]["akcje"] if a != plan[11]["wartosc"]][0]
            zap = [{"nr": i, "w": plan[i - 1]["wartosc"], "dt": 0.0} for i in range(1, 12)] + [{"nr": 12, "w": zly, "dt": 0.0}]
            hak("zaplanuj", zap)
            czekaj_do(t0 + plan[2]["t"] + 0.15)
            zrzut("03_sila_trafienie")
            czekaj_do(t0 + plan[9]["t"] + 0.15)
            zrzut("04_sila_seria")
            czekaj_do(t0 + plan[11]["t"] + 0.15)
            zrzut("05_sila_pudlo")
            hak("przerwij")
            time.sleep(1.5)

            # 06 Pancerz w trakcie zamachu (pierścień), 07 podsumowanie
            hak("inna")
            hak("graj", "pancerz")
            czekaj_na(lambda: klient().get("gra") == "pancerz" and klient().get("ekran") == "stanowisko", 10)
            time.sleep(1.5)
            k0 = start_rundy()
            plan = hak("plan", dm="Server")
            t0 = k0["runda"]["t0"]
            hak("zaplanuj", [{"nr": e["nr"], "w": "blok", "dt": 0.0} for e in plan if e["wartosc"] == "cios"])
            cel = next((e for e in plan if e["wartosc"] == "zmylka"), plan[12])
            czekaj_do(t0 + cel["t"] - 0.35)
            zrzut("06_pancerz_zamach")
            czekaj_do(t0 + plan[-1]["t"] + 2.5)
            czekaj_na(lambda: klient().get("ekran") == "podsumowanie", 10)
            time.sleep(0.8)
            zrzut("07_podsumowanie")

            # 08 telefon 667 × 375: emulacja w kliencie, runda Siły, wycięty prostokąt telefonu + pomiar
            hak("inna")
            hak("graj", "sila")
            czekaj_na(lambda: klient().get("gra") == "sila" and klient().get("ekran") == "stanowisko", 10)
            luau(KP + 'k:SetAttribute("EmulacjaEkranu", Vector2.new(667, 375)) return "ok"', "Client")
            time.sleep(1.5)
            k0 = start_rundy()
            plan = hak("plan", dm="Server")
            t0 = k0["runda"]["t0"]
            hak("autograj", 1.0, False)
            czekaj_do(t0 + plan[5]["t"] + 0.15)
            pomiar = json.loads(luau(POMIAR_TELEFONU, "Client"))
            zrzut("08_telefon_667x375", pomiar)
            napisy = sorted(pomiar["napisy"], key=lambda x: x["pt"])
            przyciski = sorted(pomiar["przyciski"], key=lambda x: x["pt"])
            wynik = {"skala_k": pomiar["k"], "prostokat": [pomiar["w"], pomiar["h"]],
                     "najmniejsze_napisy": napisy[:5], "najmniejsze_przyciski": przyciski[:5]}
            print(json.dumps(wynik, ensure_ascii=False, indent=1))
            hak("przerwij")
            time.sleep(1)
            luau(KP + 'k:SetAttribute("EmulacjaEkranu", nil) return "ok"', "Client")
        finally:
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
            for _ in range(60):
                time.sleep(0.5)
                if "Current Studio Mode: Edit" in call("get_studio_state")["text"]:
                    break


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    main()
