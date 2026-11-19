# -*- coding: utf-8 -*-
"""Zrzuty z gry (tryb Play) do README — tablica wejścia, wybór przy trenerze w bazarze, Siła (trafienie, seria,
pudło), Pancerz w trakcie zamachu, podsumowanie, ekran telefonu 667 × 375 (emulacja: atrybut EmulacjaEkranu), a od
nocy 17/18.11.2026 także cztery nowe mini-gry: dla każdej start z podpowiedzią obrazkową, środek rundy, podsumowanie
i widok telefonu; 25 — okno wyboru z sześcioma grami. Lista graczy i czat schowane (SetCoreGuiEnabled u klienta).

    python -B swiat/trening_proba/testy/zrzuty_gry.py [--wyj <folder>] [--studio <studio_id>] [--nowe]
    python -B swiat/trening_proba/testy/zrzuty_gry.py --telefon     # 26–37: sześć gier na telefonie 667 × 375 i 844 × 390
    python -B swiat/trening_proba/testy/zrzuty_gry.py --walka       # 38–67: wygląd jak w walce — dla każdej z sześciu gier
                                                                    #  odliczanie (dojazd kamery), trafienie z komiksowym
                                                                    #  napisem, akcent serii, zbliżenie z konfetti po rundzie
                                                                    #  bez pudła i to samo zbliżenie na telefonie 667 × 375
    python -B swiat/trening_proba/testy/zrzuty_gry.py --walka --tylko sila,pancerz   # wybrane gry
    python -B swiat/trening_proba/testy/zrzuty_gry.py --walka --klasa Warrior        # klasa bohatera: Warrior | Scout | Mage
    python -B swiat/trening_proba/testy/zrzuty_gry.py --walka --klasa Mage --krotko  # 68–79: druga klasa — dla każdej gry
                                                                    #  runda z trafieniem i zbliżenie po pierwszym punkcie
    python -B swiat/trening_proba/testy/zrzuty_gry.py --arena       # a1–a12: scenerie krain (D-108) — Las, Bagno i Dżungla
                                                                    #  z ukosa, cały pas scenerii, sześć gier w rundzie
                                                                    #  na tle swojej scenerii, zbliżenie Siły, Siła na telefonie
    python -B swiat/trening_proba/testy/zrzuty_gry.py --sprawdz     # bez Studio: kawałki Luau parsują się

Domyślnie zapisuje do swiat/trening_proba/klatki/ (JPG, szerokość 1280 px) i wypisuje pomiar telefonu: najmniejszy
widoczny napis i przycisk w punktach telefonu. --nowe: tylko cztery nowe mini-gry (09–24). Warunki jak w proba_play.py
(Studio w trybie Edit, zbudowane TreningProba, najlepiej MiasteczkoBazar + MiasteczkoBazarGra). W Play zmienia tylko
stan gracza, kamerę i atrybuty własnego kontenera u klienta; na końcu wraca do trybu Edit. Nazwa konta nie trafia do
plików (na zrzutach jej nie ma: własna postać nie ma nad sobą nazwy, a HUD jest na stanowisku schowany).
"""
import io
import json
import os
import re
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
-- napisy komiksowe (osobna warstwa na cały ekran): wysokość liter w punktach telefonu i czy są w prostokącie telefonu
local komiks = {}
local inset = game:GetService("GuiService"):GetGuiInset()
local x0, y0 = ekran.AbsolutePosition.X + inset.X, ekran.AbsolutePosition.Y + inset.Y
local w = p.PlayerGui:FindFirstChild("TreningProbaKomiks")
if w and w.Enabled then
	for _, d in w:GetDescendants() do
		if d:IsA("TextLabel") and d.Name == "Tekst" and d.Text ~= "" then
			local a, r = d.AbsolutePosition, d.AbsoluteSize
			table.insert(komiks, { t = d.Text, pt = d.TextBounds.Y / k.Scale, czcionka = d.FontFace.Family,
				w_ekranie = a.X >= x0 and a.Y >= y0 and a.X + r.X <= x0 + ekran.AbsoluteSize.X and a.Y + r.Y <= y0 + ekran.AbsoluteSize.Y })
		end
	end
end
return game:GetService("HttpService"):JSONEncode({
	x = x0, y = y0, w = ekran.AbsoluteSize.X,
	h = ekran.AbsoluteSize.Y, k = k.Scale, vp = { workspace.CurrentCamera.ViewportSize.X, workspace.CurrentCamera.ViewportSize.Y },
	napisy = napisy, przyciski = przyciski, komiks = komiks })
'''

# Kawałki Luau: (szablon, przykładowe argumenty dla --sprawdz)
KOD = {
    "pomiar": (POMIAR_TELEFONU, ()),
    "hak": (KP + 'return H:JSONEncode(k.Sygnaly.%s:Invoke("%s"%s))', ("SterowanieKlienta", "stan", ', "x", 1')),
    "przestaw": (HRP + 'if hrp then local p = Vector3.new(%r, %r, %r) local q = Vector3.new(%r, p.Y, %r) '
                 'gracz.Character:PivotTo(CFrame.lookAt(p, q)) hrp.AssemblyLinearVelocity = Vector3.zero end return "ok"',
                 (1.0, 2.0, 3.0, 4.0, 5.0)),
    "kamera_za": ('local cam = workspace.CurrentCamera local p = game:GetService("Players").LocalPlayer '
                  'local h = p.Character and p.Character:FindFirstChild("HumanoidRootPart") if h then '
                  'cam.CameraType = Enum.CameraType.Custom cam.CFrame = CFrame.lookAt(h.Position - h.CFrame.LookVector * %r '
                  '+ Vector3.new(0, %r, 0), h.Position + h.CFrame.LookVector * 4) end return "ok"', (10.0, 4.0)),
    # kamera testu w stałym miejscu (widoki areny) i oddanie kamery graczowi
    # (ustawiana co klatkę po innych skryptach kamery — samo CFrame gra potrafi nadpisać, gdy kamera jest daleko od postaci)
    "kamera_stala": ('local RS = game:GetService("RunService") pcall(function() RS:UnbindFromRenderStep("ProbaKameraAreny") end) '
                     'local cf = CFrame.lookAt(Vector3.new(%r, %r, %r), Vector3.new(%r, %r, %r)) local kat = %r '
                     'RS:BindToRenderStep("ProbaKameraAreny", Enum.RenderPriority.Last.Value + 1, function() '
                     'local cam = workspace.CurrentCamera cam.CameraType = Enum.CameraType.Scriptable cam.CFrame = cf '
                     'cam.FieldOfView = kat end) return "ok"', (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 70.0)),
    "kamera_oddaj": ('pcall(function() game:GetService("RunService"):UnbindFromRenderStep("ProbaKameraAreny") end) '
                     'local cam = workspace.CurrentCamera cam.CameraType = Enum.CameraType.Custom cam.FieldOfView = 70 return "ok"', ()),
    "teraz": ('return workspace:GetServerTimeNow()', ()),
    "gotowy": ('local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)', ()),
    "wybor_klasy": ('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("ClassSelect") '
                    'return game:GetService("HttpService"):JSONEncode({ e = g ~= nil and g.Enabled, '
                    'k = workspace.CurrentCamera.CameraType.Name })', ()),
    "tablica": (KP + 'local e = k.TablicaWejscia.E return H:JSONEncode({ p = { e.Position.X, e.Position.Y, e.Position.Z }, '
                'f = { e.CFrame.LookVector.X, 0, e.CFrame.LookVector.Z } })', ()),
    "emulacja": (KP + 'k:SetAttribute("EmulacjaEkranu", %s) return "ok"', ("Vector2.new(667, 375)",)),
    "runda_serwera": (KP + 'local s = k.Sygnaly.SterowanieSerwera:Invoke("stan") local g = next(s.gracze) '
                      'local r = g and s.gracze[g].runda return H:JSONEncode(r or {})', ()),
    # klasa gracza jak z ekranu wyboru klasy (zdarzenie gry ChooseClass) — bohater klasy z pakietu swiat/bohater_swiat
    "zmien_klase": ('game:GetService("ReplicatedStorage"):WaitForChild("ChooseClass"):FireServer("%s") return "ok"', ("Warrior",)),
    "bohater": ('local k = workspace:FindFirstChild("BohaterSwiat") local s = k and k:FindFirstChild("Sygnaly") '
                'local r = s and s:FindFirstChild("RuchBohatera") local w = nil if r then w = r:Invoke("stan") end '
                'return game:GetService("HttpService"):JSONEncode({ jest = r ~= nil, klasa = w and w.klasa or false, '
                'klip = w and w.klip or false, wymuszony = w and w.wymuszony or false })', ()),
    # na zrzutach bez listy graczy i czatu (nazwa konta) — tylko u klienta, na czas Play
    "bez_nazwy": ('local SG = game:GetService("StarterGui") for _, t in { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Chat } do '
                  'pcall(function() SG:SetCoreGuiEnabled(t, false) end) end return "ok"', ()),
}


def kod(nazwa, *argi):
    return KOD[nazwa][0] % argi if argi else KOD[nazwa][0]


def sprawdz_kod():
    sys.path.insert(0, os.path.join(REPO, "tools", "walka"))
    import luau_mini as LM  # noqa: E402
    bledy = []
    for nazwa, (szablon, przyklad) in KOD.items():
        tekst = szablon % przyklad if przyklad else szablon
        try:
            LM.Parser(tekst, nazwa, LM.Interpreter()).program()
        except LM.BladSkladni as e:
            bledy.append("%s: %s" % (nazwa, e))
        if re.search(r"%[sdrf]", tekst):
            bledy.append("%s: nie wszystkie %%-pola podstawione" % nazwa)
    print("sprawdz: %d kawałków Luau, %s" % (len(KOD), "OK" if not bledy else "BŁĘDY:\n  " + "\n  ".join(bledy)))
    return 0 if not bledy else 1


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def main():
    argv = sys.argv[1:]
    if "--sprawdz" in argv:
        sys.exit(sprawdz_kod())
    wyj = os.path.abspath(argv[argv.index("--wyj") + 1]) if "--wyj" in argv else os.path.join(PAKIET, "klatki")
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    tylko_nowe = "--nowe" in argv
    tylko_telefon = "--telefon" in argv
    tylko_walka = "--walka" in argv
    tylko_arena = "--arena" in argv
    wybrane = argv[argv.index("--tylko") + 1].split(",") if "--tylko" in argv else None
    klasa = argv[argv.index("--klasa") + 1] if "--klasa" in argv else None
    krotko = "--krotko" in argv
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

        def luau(kod_, dm):
            r = call("execute_luau", {"code": kod_, "datamodel_type": dm}, timeout=120)
            if r["is_error"]:
                raise StudioError(r["text"][:800])
            return r["text"].strip()

        def hak(polecenie, *argi, dm="Client"):
            nazwa = "SterowanieSerwera" if dm == "Server" else "SterowanieKlienta"
            a = ", ".join(json.dumps(x, ensure_ascii=False) if not isinstance(x, list) else
                          "{ " + ", ".join("{ nr = %d, w = %s, dt = %r }" % (p["nr"], json.dumps(p["w"]), p["dt"]) for p in x) + " }"
                          for x in argi)
            return json.loads(luau(kod("hak", nazwa, polecenie, (", " + a) if a else ""), dm))

        def klawisz(kod_):
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": kod_}]})

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
            luau(kod("przestaw", p[0], p[1], p[2], patrz[0], patrz[2]), "Server")

        def kamera_za(odl=10, wys=4):
            luau(kod("kamera_za", float(odl), float(wys)), "Client")

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
            return float(luau(kod("teraz"), "Client"))

        def start_rundy():
            hak("start")
            return czekaj_na(lambda: (lambda c: c if c.get("ekran") == "runda" and c.get("runda") else None)(klient()), 10)

        def czekaj_do(t_serwera):
            dt = t_serwera - teraz_serwera()
            if dt > 0:
                time.sleep(dt)

        def wejdz(gra):
            hak("inna")
            hak("graj", gra)
            czekaj_na(lambda: klient().get("gra") == gra and klient().get("ekran") == "stanowisko", 10)
            time.sleep(1.5)

        def pomiar_i_zrzut(nazwa):
            pomiar = json.loads(luau(kod("pomiar"), "Client"))
            zrzut(nazwa, pomiar)
            napisy = sorted(pomiar["napisy"], key=lambda x: x["pt"])
            przyciski = sorted(pomiar["przyciski"], key=lambda x: x["pt"])
            wynik = {"zrzut": nazwa, "skala_k": pomiar["k"], "prostokat": [pomiar["w"], pomiar["h"]],
                     "najmniejsze_napisy": napisy[:3], "najmniejsze_przyciski": przyciski[:3],
                     "napisy_komiksowe": pomiar.get("komiks")}
            print(json.dumps(wynik, ensure_ascii=False, indent=1))

        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        try:
            czekaj_na(lambda: "Client" in call("get_studio_state")["text"] and luau(kod("gotowy"), "Client") == "true", 90, 1)
            time.sleep(2)
            for _ in range(20):
                w = json.loads(luau(kod("wybor_klasy"), "Client"))
                if not w["e"] and w["k"] == "Custom":
                    break
                klawisz("Return")
                time.sleep(1.5)
            luau(kod("bez_nazwy"), "Client")
            if klasa:
                # klasa bohatera (jak wybór na ekranie klas); czekamy, aż pakiet bohatera pokaże właściwy model
                luau(kod("zmien_klase", klasa), "Client")
                oczek = {"Warrior": "wojownik", "Scout": "zwiadowca", "Mage": "mag"}.get(klasa)
                b = czekaj_na(lambda: (lambda x: x if x.get("klasa") == oczek else None)(json.loads(luau(kod("bohater"), "Client"))), 15, 0.5)
                log("klasa %s → bohater: %s" % (klasa, b or json.loads(luau(kod("bohater"), "Client"))))
            else:
                log("bohater:", json.loads(luau(kod("bohater"), "Client")))
            # napisy komiksowe żyją 2 × dłużej, żeby zrzut zdążył je złapać (więcej — nakładałyby się słowa kolejnych trafień)
            hak("dlugie_napisy", 2)
            # przy tablicy wejścia (wejście sprawdza odległość — z miejsca startu bywa za daleko)
            tab0 = json.loads(luau(kod("tablica"), "Server"))
            przestaw([tab0["p"][0] + tab0["f"][0] * 5, tab0["p"][1] + 0.5, tab0["p"][2] + tab0["f"][2] * 5], tab0["p"])
            time.sleep(1.2)

            if tylko_arena:
                # a1–a12: scenerie krain (D-108, 19.11.2026). Widoki kamerą testu w stałych miejscach nad pasem scenerii
                # (gracz stoi na podeście jednej ze scenerii krainy), potem sześć gier w trakcie rundy na tle swojej
                # scenerii, zbliżenie Siły i Siła na telefonie.
                c = D["arena"]["srodek"]
                for nazwa, gra_stoi, oko, cel, kat in (("a1_las", "sila", [-144, 36, 40], [-144, 0, -14], 62.0),
                                                       ("a2_bagno", "zrecznosc", [0, 36, 40], [0, 0, -14], 62.0),
                                                       ("a3_dzungla", "pancerz", [144, 36, 40], [144, 0, -14], 62.0),
                                                       ("a4_pas_scenerii", "kondycja", [0, 150, 172], [0, 0, -14], 62.0)):
                    if wybrane and nazwa.split("_")[0] not in wybrane:
                        continue
                    pr = D["swiat"][gra_stoi]["podest"]
                    przestaw([pr[0], pr[1] + 3.5, pr[2]], D["swiat"][gra_stoi]["patrz"])
                    time.sleep(1.5)
                    luau(kod("kamera_stala", float(c[0] + oko[0]), float(c[1] + oko[1]), float(c[2] + oko[2]),
                             float(c[0] + cel[0]), float(c[1] + cel[1]), float(c[2] + cel[2]), kat), "Client")
                    time.sleep(1.2)
                    zrzut(nazwa)
                luau(kod("kamera_oddaj"), "Client")
                for nr, gra in ((5, "sila"), (6, "kondycja"), (7, "szczescie"), (10, "zrecznosc"), (11, "pancerz"), (12, "inteligencja")):
                    if wybrane and "a%d" % nr not in wybrane:
                        continue
                    wejdz(gra)
                    k0 = start_rundy()
                    if not k0:
                        log("%s: runda nie ruszyła" % gra)
                        continue
                    hak("autograj", 1.0, False)
                    czekaj_do(k0["runda"]["t0"] + 6.0)
                    czekaj_na(lambda: (klient().get("komiks") or {}).get("naEkranie", 0) >= 1, 4, 0.2)
                    zrzut("a%d_arena_%s_runda" % (nr, gra))
                    if gra == "sila" and (not wybrane or "a8" in wybrane):
                        czekaj_na(lambda: ((klient().get("lokalnie") or {}).get("suma") or 0) >= 1, 40, 0.3)
                        time.sleep(0.4)
                        hak("przerwij")
                        czekaj_na(lambda: klient().get("ekran") == "podsumowanie", 8, 0.3)
                        time.sleep(1.6)
                        zrzut("a8_arena_sila_final")
                    else:
                        hak("przerwij")
                    time.sleep(1.2)
                if not wybrane or "a9" in wybrane:
                    wejdz("sila")
                    luau(kod("emulacja", "Vector2.new(667, 375)"), "Client")
                    time.sleep(1.2)
                    k0 = start_rundy()
                    if k0:
                        hak("autograj", 1.0, False)
                        czekaj_do(k0["runda"]["t0"] + 7.0)
                        pomiar_i_zrzut("a9_arena_telefon_sila_667x375")
                        hak("przerwij")
                        time.sleep(1.2)
                    luau(kod("emulacja", "nil"), "Client")
                return
            if tylko_walka:
                # 38–67: wygląd jak w walce. Dla każdej gry jedna pełna runda bez pudła (autogra): odliczanie w połowie
                # dojazdu kamery, trafienie z komiksowym napisem i efektem, akcent serii („SERIA 10!”), zbliżenie
                # z konfetti i kartą podsumowania; potem krótka runda na telefonie 667 × 375 przerwana po pierwszym
                # punkcie statystyki — zbliżenie z kartą na małym ekranie (+ pomiar napisów)
                if krotko:
                    # 68–79: krótki zestaw (druga klasa bohatera): runda z trafieniem i zbliżenie po pierwszym punkcie
                    nr = 68
                    przyrostek = {"Warrior": "wojownik", "Scout": "zwiadowca", "Mage": "mag"}.get(klasa, "klasa")
                    for gra in ("sila", "pancerz", "kondycja", "zrecznosc", "inteligencja", "szczescie"):
                        if wybrane and gra not in wybrane:
                            nr += 2
                            continue
                        wejdz(gra)
                        k0 = start_rundy()
                        if not k0:
                            log("%s: runda nie ruszyła" % gra)
                            nr += 2
                            continue
                        hak("autograj", 1.0, False)
                        czekaj_do(k0["runda"]["t0"] + 6.0)
                        czekaj_na(lambda: (klient().get("komiks") or {}).get("naEkranie", 0) >= 1, 4, 0.2)
                        log("%s: bohater w rundzie %s" % (gra, klient().get("bohater")))
                        zrzut("%02d_%s_%s_runda" % (nr, przyrostek, gra))
                        czekaj_na(lambda: ((klient().get("lokalnie") or {}).get("suma") or 0) >= 1, 40, 0.3)
                        time.sleep(0.4)
                        hak("przerwij")
                        czekaj_na(lambda: klient().get("ekran") == "podsumowanie", 8, 0.3)
                        time.sleep(1.6)
                        zrzut("%02d_%s_%s_final" % (nr + 1, przyrostek, gra))
                        nr += 2
                    return
                nr = 38
                for gra in ("sila", "pancerz", "kondycja", "zrecznosc", "inteligencja", "szczescie"):
                    if wybrane and gra not in wybrane:
                        nr += 5
                        continue
                    wejdz(gra)
                    k0 = start_rundy()
                    if not k0:
                        log("%s: runda nie ruszyła" % gra)
                        nr += 5
                        continue
                    t0 = k0["runda"]["t0"]
                    hak("autograj", 1.0, False)
                    czekaj_do(t0 - D["runda"]["odliczanie_s"] * 0.45)
                    zrzut("%02d_walka_%s_odliczanie" % (nr, gra))
                    if gra == "zrecznosc":
                        # Kłody: postać w skoku nad niską kłodą, a potem w padzie pod wysoką (ruch postaci albo bohatera)
                        plan = hak("plan", dm="Server")
                        e = next((x for x in plan if x.get("t") and x["t"] > 5), plan[0])
                        czekaj_do(t0 + e["t"] + 0.1)
                        zrzut("%02d_walka_%s_trafienie" % (nr + 1, gra))
                        e2 = next((x for x in plan if x.get("wartosc") == "wysoko"), None)
                        if e2:
                            czekaj_do(t0 + e2["t"] + 0.1)
                            zrzut("%02db_walka_%s_padnij" % (nr + 1, gra))
                    else:
                        czekaj_do(t0 + 6.0)
                        czekaj_na(lambda: (klient().get("komiks") or {}).get("naEkranie", 0) >= 1, 4, 0.2)
                        zrzut("%02d_walka_%s_trafienie" % (nr + 1, gra))
                    # akcent serii: duże słowo z gwiazdą żyje dłużej (dlugie_napisy), łapiemy je zaraz po progu serii
                    prog = D["przyrost"]["progi_serii"][1]
                    czekaj_na(lambda: ((klient().get("lokalnie") or {}).get("seria") or 0) >= prog, 30, 0.2)
                    time.sleep(0.25)
                    zrzut("%02d_walka_%s_seria" % (nr + 2, gra))
                    czekaj_na(lambda: klient().get("ekran") == "podsumowanie", D["runda"]["dlugosc_s"] + 12, 0.5)
                    time.sleep(1.5)
                    kf = klient()
                    log("%s: konfetti %s, radość %s, ujęcie %s, efekty %s" % (gra, kf.get("konfetti"), kf.get("radosc"),
                                                                             kf.get("kameraUjecie"), kf.get("efekty")))
                    zrzut("%02d_walka_%s_final" % (nr + 3, gra))
                    # telefon: runda przerwana po pierwszym punkcie statystyki → zbliżenie z kartą (bez „BEZ PUDŁA!”)
                    luau(kod("emulacja", "Vector2.new(667, 375)"), "Client")
                    time.sleep(1.2)
                    k0 = start_rundy()
                    if k0:
                        hak("autograj", 1.0, False)
                        czekaj_na(lambda: ((klient().get("lokalnie") or {}).get("suma") or 0) >= 1, 40, 0.3)
                        time.sleep(0.4)
                        hak("przerwij")
                        czekaj_na(lambda: klient().get("ekran") == "podsumowanie", 8, 0.3)
                        time.sleep(1.6)
                        pomiar_i_zrzut("%02d_walka_%s_final_telefon_667x375" % (nr + 4, gra))
                    luau(kod("emulacja", "nil"), "Client")
                    time.sleep(0.8)
                    nr += 5
                return

            if tylko_telefon:
                # 26–37: każda z sześciu gier w trakcie rundy na ekranie telefonu 667 × 375 i 844 × 390 (emulacja
                # prostokąta ekranu u klienta) + pomiar najmniejszych napisów i przycisków
                nr = 26
                for gra in ("sila", "pancerz", "kondycja", "zrecznosc", "inteligencja", "szczescie"):
                    wejdz(gra)
                    for ew, eh in ((667, 375), (844, 390)):
                        luau(kod("emulacja", "Vector2.new(%d, %d)" % (ew, eh)), "Client")
                        time.sleep(1.2)
                        k0 = start_rundy()
                        if not k0:
                            log("%s: runda nie ruszyła" % gra)
                            continue
                        hak("autograj", 1.0, False)
                        czekaj_do(k0["runda"]["t0"] + 7.0)
                        pomiar_i_zrzut("%02d_telefon_%s_%dx%d" % (nr, gra, ew, eh))
                        nr += 1
                        hak("przerwij")
                        time.sleep(1.2)
                    luau(kod("emulacja", "nil"), "Client")
                return

            # 25 okno wyboru z sześcioma grami (wszystkie grywalne)
            hak("wybor", "test")
            time.sleep(1.0)
            zrzut("25_wybor_szesc_gier")
            hak("zamknij")

            if not tylko_nowe:
                # 01 tablica wejścia (kamera gracza za plecami)
                tab = json.loads(luau(kod("tablica"), "Server"))
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
                wejdz("pancerz")
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
                wejdz("sila")
                luau(kod("emulacja", "Vector2.new(667, 375)"), "Client")
                time.sleep(1.5)
                k0 = start_rundy()
                plan = hak("plan", dm="Server")
                t0 = k0["runda"]["t0"]
                hak("autograj", 1.0, False)
                czekaj_do(t0 + plan[5]["t"] + 0.15)
                pomiar_i_zrzut("08_telefon_667x375")
                hak("przerwij")
                time.sleep(1)
                luau(kod("emulacja", "nil"), "Client")

            # 09–24: cztery nowe mini-gry — start z podpowiedzią, środek rundy, podsumowanie, telefon
            nr = 9
            for gra in ("kondycja", "zrecznosc", "inteligencja", "szczescie"):
                wejdz(gra)
                zrzut("%02d_%s_start" % (nr, gra))
                k0 = start_rundy()
                t0 = k0["runda"]["t0"]
                plan = hak("plan", dm="Server")
                hak("autograj", 1.0, False)
                if gra == "zrecznosc":
                    # postać w skoku albo w padzie, gdy kłoda jest tuż przy niej
                    e = next((x for x in plan if x.get("t") and x["t"] > 10), plan[-1])
                    czekaj_do(t0 + e["t"] + D["gry"]["zrecznosc"]["wyprzedzenie_s"] - 0.05)
                elif gra == "inteligencja":
                    # w czasie trzeciego pokazu run (kamień świeci, napis PATRZ!)
                    czekaj_na(lambda: (json.loads(luau(kod("runda_serwera"), "Server")).get("pokazy") or 0) >= 3, 40, 0.3)
                    r = json.loads(luau(kod("runda_serwera"), "Server"))
                    czekaj_do(t0 + (r.get("pokazOd") or 0) + 0.15)
                else:
                    czekaj_do(t0 + 10.2)
                zrzut("%02d_%s_runda" % (nr + 1, gra))
                czekaj_na(lambda: klient().get("ekran") == "podsumowanie", D["runda"]["dlugosc_s"] + 12, 1.0)
                time.sleep(0.8)
                zrzut("%02d_%s_podsumowanie" % (nr + 2, gra))
                luau(kod("emulacja", "Vector2.new(667, 375)"), "Client")
                time.sleep(1.2)
                k0 = start_rundy()
                hak("autograj", 1.0, False)
                czekaj_do(k0["runda"]["t0"] + 7.0)
                pomiar_i_zrzut("%02d_%s_telefon_667x375" % (nr + 3, gra))
                hak("przerwij")
                time.sleep(1)
                luau(kod("emulacja", "nil"), "Client")
                nr += 4
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
