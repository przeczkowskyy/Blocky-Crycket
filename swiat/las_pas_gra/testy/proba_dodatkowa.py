# -*- coding: utf-8 -*-
"""Dodatkowa próba „lasu-pasa w grze” w Roblox Studio (tryb Play) — to, czego nie obejmuje lista P01–P16.

    python -B swiat/las_pas_gra/testy/proba_dodatkowa.py <folder zrzutów> [--tylko drogi,chod,sciany,walki,koszt,zrzuty]
                                                        [--studio <studio_id>]

Warunki jak w proba_play.py: Studio w trybie Edit, zbudowane Workspace/LasPas i Workspace/LasPasGra, do dróg także
Workspace/LasTeleport (brama w miasteczku) i Workspace/TeleportChmury (przejście przez chmury). Skrypt sam włącza
i wyłącza Play (tylko swoje), niczego nie zapisuje w miejscu i niczego nie publikuje. Wyniki: JSON w
swiat/las_pas_gra/wyniki/proba_dodatkowa_<czas>.json — zapisywany po każdym kroku (przerwana próba nie przepada);
zrzuty (bez filmów) w <folder zrzutów>.

CZĘŚCI (kolejność wykonania):
  drogi   świeży gracz: brama w miasteczku prawdziwym E → przelot (oś czasu klienta: kamera, czarna zasłona,
          klatki), Kamień Powrotu prawdziwym E → miasteczko, brama jeszcze raz → bez przelotu; potem
          „odtwórz ponownie” w miasteczku (gracz znów świeży) i przejście przez chmury → przelot, drugie przejście
          przez chmury → bez przelotu; po każdym przelocie kamera Custom i ruch klawiszem W
  chod    bieg postaci (Humanoid:MoveTo u klienta) od Polany Przybycia do bramy po osi pasa: czas (plan: krótki pas D-096, 25 s),
          zatrzymania, wysokości (mostek), cofnięcia
  sciany  niewidzialne ściany: marsz w bok w 7 miejscach pasa i w tył za Polanę; skoki; spadek w pustkę → ratunek
  koszt   (wykonywany przed walkami, żeby Strażnik był żywy) czas klatki klienta i koszt serwera przy 1 graczu
          i przy pełnym zestawie potworów (TestGraczy = 20), w trzech miejscach; liczba brył i części u klienta
  walki   każdy gatunek (slime, muchomornik, wilk, troll) prawdziwym E: przeniesienie na arenę, wynik, powrót
          w to samo miejsce, odrodzenie; Strażnik: przegrana (brama dalej zamknięta), wygrana (brama otwarta
          tylko u zwycięzcy), przejście przez bramę do tabliczki, baner
  zrzuty  ujęcia potworów w przegrodach (kamera skryptowa na chwilę, tylko u klienta), Kamień Powrotu
"""
import io
import json
import os
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"),
           os.path.join(REPO, "swiat", "test_walki2", "testy")):
    sys.path.insert(0, _s)

KP = 'local k = workspace:FindFirstChild("LasPasGra") local H = game:GetService("HttpService") '
J = ('local function J(v) local t = typeof(v) if t == "Vector3" then return { v.X, v.Y, v.Z } '
     'elseif t == "table" then local o = {} if #v > 0 then for i, b in ipairs(v) do o[i] = J(b) end '
     'else for a, b in v do o[tostring(a)] = J(b) end end return o '
     'elseif t == "number" and (v ~= v or v == math.huge or v == -math.huge) then return tostring(v) '
     'elseif t == "Instance" then return v:GetFullName() end return v end ')
HRP_S = 'local g = game:GetService("Players"):GetPlayers()[1] local hrp = g.Character.HumanoidRootPart '
HRP_K = 'local g = game:GetService("Players").LocalPlayer local hrp = g.Character.HumanoidRootPart local hum = g.Character.Humanoid '
ARENA = (-76, 64, 190, 314)  # TestWalki2: x1, x2, z1, z2
# D-096: położenia z projektu (długi pas) → krótka mapa gry, tym samym przekształceniem co mapa
# (swiat/biomy/przycinarka.py); liczby niżej to dawne położenia projektu w X(…)
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from swiat.biomy.przycinarka import PLIK_WYMIAROW, Przeksztalcenie, _json  # noqa: E402
P_D096 = Przeksztalcenie(_json(PLIK_WYMIAROW))


def X(x):
    return round(P_D096.x(x), 2)


PAS = (1056, X(2076), -760, -640)

# oś czasu klienta (próbki co 0,1 s + statystyka klatek): kamera, czarna zasłona przelotu, przelot, chmury, postać
OS_KLIENTA = r'''
local k = workspace.LasPasGra
local H = game:GetService("HttpService")
local RS = game:GetService("RunService")
local p = game:GetService("Players").LocalPlayer
local CZAS = __CZAS__
k:SetAttribute("TestOs", nil)
task.spawn(function()
	local o, dts = {}, {}
	local t0 = os.clock()
	local nast = 0
	while os.clock() - t0 < CZAS do
		local dt = RS.RenderStepped:Wait()
		local t = os.clock() - t0
		local wPrzelocie = k:GetAttribute("KlientPrzelot") == true
		if wPrzelocie then
			table.insert(dts, dt)
		end
		if t >= nast then
			nast = t + 0.1
			local e = p.PlayerGui:FindFirstChild("LasPasGraEkran")
			local z = e and e:FindFirstChild("Zaslona")
			local c = workspace.CurrentCamera
			local hrp = p.Character and p.Character:FindFirstChild("HumanoidRootPart")
			local tc = workspace:FindFirstChild("TeleportChmury")
			local czern = 1
			if z and e.Enabled and z.Visible then
				czern = math.floor(z.BackgroundTransparency * 100 + 0.5) / 100
			end
			table.insert(o, { math.floor(t * 100 + 0.5) / 100, c.CameraType.Name, czern, wPrzelocie,
				tc ~= nil and tc:GetAttribute("Trwa") == true, hrp and math.floor(hrp.Position.X + 0.5) or 0,
				hrp and math.floor(hrp.Position.Z + 0.5) or 0, math.floor(c.CFrame.Position.X + 0.5), math.floor(c.CFrame.Position.Y + 0.5) })
		end
	end
	table.sort(dts)
	local s = 0
	for _, d in dts do
		s += d
	end
	local zryw = 0
	for _, d in dts do
		if d > 0.1 then
			zryw += 1
		end
	end
	k:SetAttribute("TestOs", H:JSONEncode({ probki = o, klatkiPrzelotu = #dts,
		srMs = if #dts > 0 then s / #dts * 1000 else 0,
		p95Ms = if #dts > 0 then dts[math.max(1, math.floor(#dts * 0.95))] * 1000 else 0,
		maksMs = if #dts > 0 then dts[#dts] * 1000 else 0, ponad100ms = zryw }))
end)
return "ok"
'''

# dziennik stanu potworów na serwerze (pojawienia i zniknięcia, do czasów odrodzenia)
DZIENNIK_STANU = r'''
local k = workspace.LasPasGra
local H = game:GetService("HttpService")
local log = {}
local t0 = os.clock()
k:SetAttribute("TestDziennikT0", t0)
local function zapisz()
	k:SetAttribute("TestDziennik", H:JSONEncode(log))
end
k.Stan.ChildAdded:Connect(function(c)
	task.wait()
	table.insert(log, { math.floor((os.clock() - t0) * 10) / 10, "+", c.Name, tostring(c:GetAttribute("Strefa")) })
	zapisz()
end)
k.Stan.ChildRemoved:Connect(function(c)
	table.insert(log, { math.floor((os.clock() - t0) * 10) / 10, "-", c.Name, tostring(c:GetAttribute("Strefa")) })
	zapisz()
end)
zapisz()
return "ok"
'''

WYNIKI = {}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def main():
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    tylko = (argv[argv.index("--tylko") + 1].split(",") if "--tylko" in argv
             else ["drogi", "chod", "sciany", "walki", "koszt", "zrzuty"])
    os.makedirs(wyj, exist_ok=True)
    os.makedirs(os.path.join(PAKIET, "wyniki"), exist_ok=True)
    plik_wynikow = os.path.join(PAKIET, "wyniki", "proba_dodatkowa_%s.json" % time.strftime("%Y%m%d_%H%M"))
    from cel_studio import wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    from czuwanie import nie_usypiaj  # noqa: E402
    from PIL import Image  # noqa: E402

    def zapisz(klucz, wartosc):
        WYNIKI[klucz] = wartosc
        with open(plik_wynikow, "w", encoding="utf-8") as f:
            json.dump(WYNIKI, f, ensure_ascii=False, indent=1)
        log("%s: %s" % (klucz, json.dumps(wartosc, ensure_ascii=False)[:1500]))

    with StudioMCP(timeout=240) as s:
        s.studios(wait=15)
        sid = wybierz_studio(s, studio)

        def call(n, a=None, timeout=None):
            d = dict(a or {})
            d["studio_id"] = sid
            return s.call(n, d, timeout=timeout)

        def luau(kod, dm, proby=3, timeout=200):
            for i in range(proby):
                try:
                    r = call("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=timeout)
                    if r["is_error"]:
                        raise StudioError(r["text"][:1500])
                    return r["text"].strip()
                except Exception as e:  # noqa: BLE001
                    if i == proby - 1:
                        raise
                    log("luau: ponawiam po błędzie:", str(e)[:300])
                    time.sleep(5)

        def js(kod, dm):
            return json.loads(luau(KP + J + kod, dm))

        def stan_studio():
            return call("get_studio_state")["text"]

        def zrzut(nazwa):
            nie_usypiaj()
            r = call("screen_capture", {"capture_id": "lpgd_" + nazwa}, timeout=150)
            if r["is_error"] or not r.get("images"):
                log("zrzut %s: BŁĄD %s" % (nazwa, r["text"][:120]))
                return None
            im = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
            if im.width > 1280:
                im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
            sciezka = os.path.join(wyj, nazwa + ".jpg")
            im.save(sciezka, "JPEG", quality=86)
            log("zrzut", nazwa)
            return os.path.basename(sciezka)  # w wynikach (repo publiczne) sama nazwa pliku, bez ścieżki lokalnej

        def pasa(polecenie, *argi):
            a = ", ".join("nil" if x is None else json.dumps(x) for x in argi)
            return js('return H:JSONEncode(J(k.Sygnaly.SterowaniePasa:Invoke("%s"%s)))' % (polecenie, (", " + a) if a else ""), "Server")

        def gracz():
            return pasa("gracz")

        def potwory_k(polecenie, *argi):
            a = ", ".join(json.dumps(x) for x in argi)
            return js('return H:JSONEncode(J(k.Sygnaly.SterowanieKlienta:Invoke("%s"%s)))' % (polecenie, (", " + a) if a else ""), "Client")

        def chmury(polecenie, *argi):
            a = ", ".join(json.dumps(x) for x in argi)
            return js('local t = workspace:WaitForChild("TeleportChmury", 10) '
                      'return H:JSONEncode(J(t.Sygnaly.SterowanieKlienta:Invoke("%s"%s)))' % (polecenie, (", " + a) if a else ""), "Client")

        def przestaw(x, y, z, kier=(1, 0)):
            luau(HRP_S + 'local p = Vector3.new(%f, %f, %f) g.Character:PivotTo(CFrame.lookAt(p, p + Vector3.new(%f, 0, %f))) '
                         'hrp.AssemblyLinearVelocity = Vector3.zero return "ok"' % (x, y, z, kier[0], kier[1]), "Server")

        def poz():
            return js(HRP_S + 'return H:JSONEncode(J(hrp.Position))', "Server")

        def nacisnij(klawisz, przytrzymaj=None):
            if przytrzymaj:
                akcje = [{"action": "keyDown", "key_code": klawisz}, {"action": "wait", "wait_time_ms": int(przytrzymaj * 1000)},
                         {"action": "keyUp", "key_code": klawisz}]
            else:
                akcje = [{"action": "keyPress", "key_code": klawisz}]
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": akcje}, timeout=60)

        def czekaj_na(warunek, limit, co=0.5):
            t0 = time.time()
            while time.time() - t0 < limit:
                w = warunek()
                if w:
                    return w
                time.sleep(co)
            return None

        def kamera():
            return js('local c = workspace.CurrentCamera local p = game:GetService("Players").LocalPlayer '
                      'local h = p.Character and p.Character:FindFirstChildOfClass("Humanoid") '
                      'return H:JSONEncode({ typ = c.CameraType.Name, podmiot = h ~= nil and c.CameraSubject == h, '
                      'podpowiedzi = game:GetService("ProximityPromptService").Enabled })', "Client")

        def kamera_na(oko, cel):
            """Kamera skryptowa w danym miejscu (tylko u klienta, na zrzut). Narzędzie execute_luau cofa zmianę typu
            kamery zrobioną w czasie wywołania, więc ustawiamy ją chwilę po nim (task.delay)."""
            luau('task.delay(0.1, function() local c = workspace.CurrentCamera c.CameraType = Enum.CameraType.Scriptable '
                 'c.CFrame = CFrame.lookAt(Vector3.new(%g, %g, %g), Vector3.new(%g, %g, %g)) end) return "ok"' % (*oko, *cel), "Client")

        def kamera_wroc():
            luau('task.delay(0.1, function() local c = workspace.CurrentCamera '
                 'local h = game:GetService("Players").LocalPlayer.Character:FindFirstChildOfClass("Humanoid") '
                 'c.CameraType = Enum.CameraType.Custom if h then c.CameraSubject = h end end) return "ok"', "Client")

        def ruch_w():
            """Klawisz W przez 1 s: ile postać przeszła (sterowanie oddane?)."""
            p0 = poz()
            nacisnij("W", 1.0)
            time.sleep(0.3)
            p1 = poz()
            return round(((p1[0] - p0[0]) ** 2 + (p1[2] - p0[2]) ** 2) ** 0.5, 1)

        def os_start(czas):
            luau(OS_KLIENTA.replace("__CZAS__", "%g" % czas), "Client")

        def os_wynik(limit):
            w = czekaj_na(lambda: luau('return tostring(workspace.LasPasGra:GetAttribute("TestOs") or "")', "Client") or None, limit, 1.0)
            return json.loads(w) if w else None

        def streszczenie_osi(o):
            """Czarny ekran: najdłuższy ciąg próbek z zasłoną ≥ 50 % krycia; przelot: od pierwszej do ostatniej próbki."""
            if not o:
                return None
            pr = o["probki"]
            najdl, biez, od = 0.0, 0.0, None
            for t, _kam, czern, *_ in pr:
                if czern <= 0.5:
                    od = t if od is None else od
                    biez = t - od + 0.1
                    najdl = max(najdl, biez)
                else:
                    od = None
            w_przel = [p[0] for p in pr if p[3]]
            chm = [p[0] for p in pr if p[4]]
            kamery = []
            for p in pr:
                if not kamery or kamery[-1][1] != p[1]:
                    kamery.append((p[0], p[1]))
            return {"czarnyNajdluzej_s": round(najdl, 2), "przelot_od_do": [w_przel[0], w_przel[-1]] if w_przel else None,
                    "chmury_od_do": [chm[0], chm[-1]] if chm else None, "kamera": kamery,
                    "klatki": {k2: round(o[k2], 1) if isinstance(o[k2], float) else o[k2]
                               for k2 in ("klatkiPrzelotu", "srMs", "p95Ms", "maksMs", "ponad100ms")}}

        def czekaj_na_przelot(limit=40):
            """Fazy serwera do końca przelotu (albo limit)."""
            fazy, t0 = [], time.time()
            while time.time() - t0 < limit:
                f = gracz()["faza"]
                if not fazy or fazy[-1][0] != f:
                    fazy.append((f, round(time.time() - t0, 1)))
                if f == "brak" and len(fazy) > 1:
                    break
                time.sleep(0.3)
            return fazy

        def wybierz_klase():
            for _ in range(20):
                w = js('local p = game:GetService("Players").LocalPlayer local g = p.PlayerGui:FindFirstChild("ClassSelect") '
                       'local c = workspace.CurrentCamera return H:JSONEncode({ ekran = g ~= nil and g.Enabled, kamera = c.CameraType.Name, '
                       'podpowiedzi = game:GetService("ProximityPromptService").Enabled })', "Client")
                if not w["ekran"] and w["kamera"] == "Custom" and w["podpowiedzi"]:
                    return w
                nacisnij("Return")
                time.sleep(1.5)
            return w

        def w_miasteczku(p):
            return abs(p[0]) < 600 and -1100 < p[2] < -300

        def w_pasie(p):
            return PAS[0] <= p[0] <= PAS[1] and PAS[2] <= p[2] <= PAS[3]

        nie_usypiaj()
        if "Current Studio Mode: Edit" not in stan_studio():
            sys.exit("Studio nie jest w trybie Edit — ta próba sama włącza Play")
        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        try:
            czekaj_na(lambda: "Client" in stan_studio() and luau(
                'local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)', "Client") == "true",
                90, 1.0)
            gotowe = czekaj_na(lambda: luau(KP + 'return tostring(k:GetAttribute("SerwerGotowy") == true and k:GetAttribute("SerwerPasaGotowy") == true)',
                                            "Server") == "true", 60, 1.0)
            czekaj_na(lambda: luau(KP + 'return tostring(k:GetAttribute("KlientGotowy") == true and k:GetAttribute("KlientPasaGotowy") == true)',
                                   "Client") == "true", 60, 1.0)
            # stan gracza (swiat/stan_gracza, 17.11.2026): próba używa reguły testowej T1 (klasa i poziom z panelu) w obu lasach
            luau('for _, n in { "LasPasGra", "LasPotwory" } do local k = workspace:FindFirstChild(n) '
                 'if k then k:SetAttribute("TestBohater", true) end end return "ok"', "Server")
            time.sleep(2)
            zapisz("start", {"serwery": bool(gotowe), "wybor_klasy": wybierz_klase()})
            luau(DZIENNIK_STANU, "Server")

            # ================================================================ DROGI DO LASU I PRZELOT
            if "drogi" in tylko:
                drogi = {}
                # a) brama w miasteczku: podpowiedź E Bramy Miejskiej (LasTeleport, atrybut Cel = "las")
                bramy = js('local t = workspace:FindFirstChild("LasTeleport") local o = {} if t then for _, d in t:GetDescendants() do '
                           'if d:IsA("ProximityPrompt") then local c = d.Parent local p = c:IsA("BasePart") and c.Position '
                           'or (c:IsA("Attachment") and c.WorldPosition) or nil table.insert(o, { nazwa = c:GetFullName(), cel = d:GetAttribute("Cel"), '
                           'p = J(p), zasieg = d.MaxActivationDistance, wlaczona = d.Enabled }) end end end return H:JSONEncode(o)', "Server")
                drogi["podpowiedzi_LasTeleport"] = bramy
                brama = None
                for b in bramy:
                    if b["cel"] == "las" and b["p"] and abs(b["p"][0]) < 600 and "Port" not in b["nazwa"]:
                        brama = b
                if not brama:
                    brama = next((b for b in bramy if b["cel"] == "las" and b["p"]), None)
                pasa("przenies", None, "miasteczko")
                time.sleep(2.5)

                def wejdz_brama(etykieta, os_s):
                    """Staje przy bramie miasteczka, E; zwraca (pozycja po, oś czasu, fazy)."""
                    bp = brama["p"]
                    pm = js('local t = workspace.LasTeleport return H:JSONEncode(J(t:GetAttribute("PunktMiasteczka")))', "Server")
                    # 4 st od podpowiedzi, od strony miasteczka
                    dx, dz = pm[0] - bp[0], pm[2] - bp[2]
                    d = max(0.1, (dx * dx + dz * dz) ** 0.5)
                    przestaw(bp[0] + dx / d * 4, pm[1], bp[2] + dz / d * 4, (-dx / d, -dz / d))
                    time.sleep(1.5)
                    widac = js('local n = 0 for _, d in workspace.LasTeleport:GetDescendants() do if d:IsA("ProximityPrompt") and d.Enabled '
                               'and d:GetAttribute("Cel") == "las" then n += 1 end end return H:JSONEncode({ n = n, '
                               'pps = game:GetService("ProximityPromptService").Enabled })', "Client")
                    if os_s:
                        os_start(os_s)
                    nacisnij("E")
                    t0 = time.time()
                    p_po = czekaj_na(lambda: (lambda p: p if w_pasie(p) else None)(poz()), 8, 0.3)
                    return p_po, round(time.time() - t0, 1), widac

                # pierwsze wejście bramą: przelot
                p_po, t_e, widac = wejdz_brama("brama1", 30)
                zrzut("d01_przybycie_brama")
                fazy = czekaj_na_przelot(40)
                os1 = streszczenie_osi(os_wynik(35))
                time.sleep(1.0)
                kp = js('return H:JSONEncode(J(k.Sygnaly.SterowaniePasaKlienta:Invoke("stan")))', "Client")
                kam = kamera()
                ruch = ruch_w()
                drogi["brama_1"] = {"E_widoczne": widac, "pozycja": p_po, "czas_E_s": t_e, "fazy": fazy, "os": os1,
                                    "ostatniPrzelot": kp.get("ostatniPrzelot"), "kamera": kam, "ruch_W_st": ruch,
                                    "ok": bool(p_po) and any(f[0] == "trwa" for f in fazy) and kam["typ"] == "Custom" and ruch > 5}
                zapisz("drogi", drogi)

                # Kamień Powrotu prawdziwym E → miasteczko
                kpow = js('local p = k.Punkty.KamienPowrotu return H:JSONEncode({ p = J(p.Position), e = p.PodpowiedzPowrotu.Enabled })', "Server")
                przestaw(kpow["p"][0] + 3, 3.5, kpow["p"][2] + 3, (-1, -1))
                time.sleep(1.5)
                zrzut("d02_kamien_powrotu")
                nacisnij("E")
                p_m = czekaj_na(lambda: (lambda p: p if w_miasteczku(p) else None)(poz()), 8, 0.3)
                drogi["kamien_powrotu"] = {"podpowiedz": kpow, "pozycja": p_m, "ok": bool(p_m)}
                zapisz("drogi", drogi)
                time.sleep(2.5)

                # drugie wejście bramą: bez przelotu
                przed = luau(KP + 'return tostring(k:GetAttribute("LicznikPrzelotow"))', "Server")
                p_po2, t_e2, _ = wejdz_brama("brama2", None)
                f2 = []
                for _ in range(16):
                    f2.append(gracz()["faza"])
                    time.sleep(0.4)
                po = luau(KP + 'return tostring(k:GetAttribute("LicznikPrzelotow"))', "Server")
                drogi["brama_2"] = {"pozycja": p_po2, "fazy": sorted(set(f2)), "licznik": [przed, po],
                                    "ok": bool(p_po2) and set(f2) == {"brak"} and przed == po}
                zapisz("drogi", drogi)

                # świeży gracz jeszcze raz (odtwórz ponownie w miasteczku = tylko kasuje flagę) → przez chmury
                pasa("przenies", None, "miasteczko")
                time.sleep(2.5)
                pasa("odtworzPrzelot")
                time.sleep(0.5)
                g0 = gracz()

                def przez_chmury(os_s):
                    st = chmury("stan")
                    if st.get("trwa"):
                        czekaj_na(lambda: not chmury("stan").get("trwa"), 15, 0.5)
                    o = chmury("otworz")
                    if not o.get("ok"):
                        return {"otworz": o}
                    w = czekaj_na(lambda: (chmury("stan").get("biezacy") or {}).get("faza") == "wybor", 15, 0.3)
                    if os_s:
                        os_start(os_s)
                    wyb = chmury("wybierz", "las")
                    t0 = time.time()
                    p = czekaj_na(lambda: (lambda q: q if w_pasie(q) else None)(poz()), 10, 0.3)
                    return {"otworz": o, "wybor": bool(w), "wybierz": wyb, "pozycja": p, "czas_do_lasu_s": round(time.time() - t0, 1)}

                ch1 = przez_chmury(35)
                fazy_c = czekaj_na_przelot(40)
                time.sleep(0.5)
                ch_stan = chmury("stan")
                os2 = streszczenie_osi(os_wynik(40))
                time.sleep(1.0)
                kp2 = js('return H:JSONEncode(J(k.Sygnaly.SterowaniePasaKlienta:Invoke("stan")))', "Client")
                kam2 = kamera()
                ruch2 = ruch_w()
                drogi["chmury_1"] = {"gracz_przed": {"widzial": g0["pamiec"].get("widzialPrzelotLasu"), "faza": g0["faza"]}, **ch1,
                                     "fazy": fazy_c, "os": os2, "ostatniPrzelot": kp2.get("ostatniPrzelot"),
                                     "chmury_ostatnie": (ch_stan.get("ostatnie") or {}).get("wynik"), "kamera": kam2,
                                     "ruch_W_st": ruch2,
                                     "ok": bool(ch1.get("pozycja")) and any(f[0] == "trwa" for f in fazy_c) and kam2["typ"] == "Custom" and ruch2 > 5}
                zapisz("drogi", drogi)

                # drugie przejście przez chmury (miasteczko → las): bez przelotu
                pasa("przenies", None, "miasteczko")
                time.sleep(3.5)
                przed = luau(KP + 'return tostring(k:GetAttribute("LicznikPrzelotow"))', "Server")
                ch2 = przez_chmury(None)
                f3 = []
                for _ in range(16):
                    f3.append(gracz()["faza"])
                    time.sleep(0.4)
                po = luau(KP + 'return tostring(k:GetAttribute("LicznikPrzelotow"))', "Server")
                time.sleep(1)
                kam3 = kamera()
                drogi["chmury_2"] = {**ch2, "fazy": sorted(set(f3)), "licznik": [przed, po], "kamera": kam3,
                                     "ok": bool(ch2.get("pozycja")) and set(f3) == {"brak"} and przed == po and kam3["typ"] == "Custom"}
                zapisz("drogi", drogi)

            # od tego miejsca przelot nie może się wtrącić: flaga „widział” na tak bez przelotu (zapomnij + wstrzymaj)
            g = gracz()
            if not g["pamiec"].get("widzialPrzelotLasu"):
                pasa("zapomnijPrzelot")  # wolnyOd = ∞: nie wystartuje sam

            # ================================================================ BIEG OD POLANY DO BRAMY
            if "chod" in tylko:
                pasa("zamknijBrame")
                pasa("przenies", None, "las")
                time.sleep(2.5)
                cof0 = luau(KP + 'return tostring(k:GetAttribute("LicznikCofniec") or 0)', "Server")
                kod = (HRP_K + ('local XA, XB, F1, F2, F3, F4 = %.2f, %.2f, %.2f, %.2f, %.2f, %.2f '
                                % (X(1130), X(1980), X(1986), X(2002), X(2012), X(2024))) + r'''
-- po osi pasa (z = −700); kryształowy filar Strażnika (mapa: Punkty/FilarKrysztal, 7 × 7 st w (1994; −700))
-- stoi na osi — gracz obchodzi go bokiem jak dróżka (sprawdzone 17.11: na wprost postać na nim utyka)
local cele = {}
for x = XA, XB, 12 do table.insert(cele, { x, -700 }) end
for _, c in { { F1, -689 }, { F2, -689 }, { F3, -700 }, { F4, -700 } } do table.insert(cele, c) end
local t0 = os.clock()
local stoj, yMin, yMaks, zMaks = {}, math.huge, -math.huge, 0
local ostatni, tRuchu = hrp.Position, os.clock()
local i = 1
local probki = {}
local nast = 0
while i <= #cele and os.clock() - t0 < 120 do
	local cel = Vector3.new(cele[i][1], hrp.Position.Y, cele[i][2])
	hum:MoveTo(cel)
	local p = hrp.Position
	yMin, yMaks = math.min(yMin, p.Y), math.max(yMaks, p.Y)
	zMaks = math.max(zMaks, math.abs(p.Z + 700))
	if (p - ostatni).Magnitude > 1 then
		ostatni, tRuchu = p, os.clock()
	elseif os.clock() - tRuchu > 1.5 then
		table.insert(stoj, { math.floor(p.X), math.floor(p.Y * 10) / 10, math.floor(p.Z) })
		hum.Jump = true
		tRuchu = os.clock()
	end
	if os.clock() - t0 >= nast then
		nast += 2
		table.insert(probki, { math.floor((os.clock() - t0) * 10) / 10, math.floor(p.X), math.floor(p.Y * 10) / 10 })
	end
	if (Vector3.new(p.X, 0, p.Z) - Vector3.new(cele[i][1], 0, cele[i][2])).Magnitude < 5 or p.X > cele[i][1] + 1 then
		i += 1
	end
	task.wait(0.05)
end
hum:MoveTo(hrp.Position)
local p = hrp.Position
return game:GetService("HttpService"):JSONEncode({ czas = os.clock() - t0, koniec = { p.X, p.Y, p.Z }, doszedl = i > #cele,
	zatrzymania = stoj, yMin = yMin, yMaks = yMaks, zMaks = zMaks, probki = probki })
''')
                bieg = json.loads(luau(kod, "Client", proby=1, timeout=240))
                cof1 = luau(KP + 'return tostring(k:GetAttribute("LicznikCofniec") or 0)', "Server")
                bieg["cofniecia"] = [cof0, cof1]
                bieg["dystans_st"] = round(bieg["koniec"][0] - X(1114), 1)
                bieg["plan_s"] = round((X(2034) - X(1114)) / 16.0, 1)
                bieg["ok"] = bieg["doszedl"] and not bieg["zatrzymania"] and cof0 == cof1
                zapisz("chod", bieg)

            # ================================================================ NIEWIDZIALNE ŚCIANY I RATUNEK
            if "sciany" in tylko:
                sciany = {"boki": [], "tyl": None, "ratunek": None}
                for x in [X(a) for a in (1110, 1210, 1330, 1480, 1630, 1850, 1975)]:
                    przestaw(x, 3.5, -700)
                    time.sleep(0.8)
                    kod = (HRP_K + r'''
local o = {}
for _, kier in { 1, -1 } do
	local t0 = os.clock()
	local skrajny = 0
	while os.clock() - t0 < 6 do
		hum:MoveTo(Vector3.new(__X__, hrp.Position.Y, -700 + kier * 90))
		if os.clock() - t0 > 2 then hum.Jump = true end
		skrajny = math.max(skrajny, math.abs(hrp.Position.Z + 700))
		task.wait(0.1)
	end
	table.insert(o, { kier = kier, maksV = skrajny, z = hrp.Position.Z, y = hrp.Position.Y })
	hum:MoveTo(Vector3.new(__X__, hrp.Position.Y, -700))
	local t1 = os.clock()
	while os.clock() - t1 < 4 and math.abs(hrp.Position.Z + 700) > 3 do task.wait(0.1) end
end
return game:GetService("HttpService"):JSONEncode(o)
''').replace("__X__", "%g" % x)
                    w = json.loads(luau(kod, "Client", proby=1, timeout=120))
                    sciany["boki"].append({"x": x, "wyniki": w, "maksV": max(r["maksV"] for r in w)})
                    zapisz("sciany", sciany)
                # w tył za Polanę (ściana zamykająca u = −24 → x 1076)
                przestaw(1114, 3.5, -700, (-1, 0))
                time.sleep(0.8)
                tyl = json.loads(luau(HRP_K + r'''
local t0 = os.clock()
local xMin = hrp.Position.X
while os.clock() - t0 < 8 do
	hum:MoveTo(Vector3.new(980, hrp.Position.Y, -700 + math.sin(os.clock() * 2) * 20))
	if os.clock() - t0 > 3 then hum.Jump = true end
	xMin = math.min(xMin, hrp.Position.X)
	task.wait(0.1)
end
return game:GetService("HttpService"):JSONEncode({ xMin = xMin, koniec = { hrp.Position.X, hrp.Position.Y, hrp.Position.Z } })
''', "Client", proby=1, timeout=60))
                sciany["tyl"] = tyl
                # spadek w pustkę w środku pasa → ratunek (serwer stawia z powrotem)
                r0 = luau(KP + 'return tostring(k:GetAttribute("LicznikRatunkow") or 0)', "Server")
                przestaw(X(1500), -60, -700)
                time.sleep(2.0)
                pr = poz()
                r1 = luau(KP + 'return tostring(k:GetAttribute("LicznikRatunkow") or 0)', "Server")
                sciany["ratunek"] = {"po": pr, "licznik": [r0, r1], "ok": pr[1] > -5 and w_pasie(pr)}
                sciany["ok"] = (all(b["maksV"] <= P_D096.g(38.0) + 0.5 for b in sciany["boki"]) and tyl["xMin"] >= 1074
                                and sciany["ratunek"]["ok"])
                zapisz("sciany", sciany)

            # ================================================================ KOSZT (przed walkami: Strażnik żywy)
            if "koszt" in tylko:
                koszt = {}
                for zestaw in (1, 20):
                    js('return H:JSONEncode(J(k.Sygnaly.SterowanieSerwera:Invoke("gracze", %s)))' % ("nil" if zestaw == 1 else zestaw), "Server")
                    time.sleep(6)
                    for nazwa, (x, z) in (("przybycie", (X(1130), -700)), ("wilki", (X(1650), -700)), ("straznik", (X(1945), -700))):
                        przestaw(x, 3.5, z, (1, 0))
                        time.sleep(5)
                        luau(KP + 'k.Sygnaly.SterowanieSerwera:Invoke("koszt", true) k.Sygnaly.SterowaniePasa:Invoke("koszt", true) return "ok"', "Server")
                        luau(KP + 'k.Sygnaly.SterowanieKlienta:Invoke("koszt", true) return "ok"', "Client")
                        kl = js('local RS = game:GetService("RunService") local t = {} local c = RS.RenderStepped:Connect(function(dt) table.insert(t, dt) end) '
                                'task.wait(8) c:Disconnect() table.sort(t) local s = 0 for _, d in t do s += d end '
                                'local n, cz = 0, 0 for _, d in workspace:GetDescendants() do if d:IsA("BasePart") then n += 1 end end '
                                'local w = k:FindFirstChild("Widoki") if w then for _, d in w:GetDescendants() do if d:IsA("BasePart") then cz += 1 end end end '
                                'return H:JSONEncode({ n = #t, sr_ms = s / math.max(1, #t) * 1000, p95_ms = (t[math.max(1, math.floor(#t * 0.95))] or 0) * 1000, '
                                'maks_ms = (t[#t] or 0) * 1000, czesciKlienta = n, czesciWidokow = cz })', "Client")
                        sw = js('local S = game:GetService("Stats") local hb = 0 pcall(function() hb = S.HeartbeatTimeMs end) '
                                'return H:JSONEncode({ potwory = J(k.Sygnaly.SterowanieSerwera:Invoke("koszt")), pas = J(k.Sygnaly.SterowaniePasa:Invoke("koszt")), '
                                'heartbeatMs = hb, fizykaFps = workspace:GetRealPhysicsFPS(), potworow = #k.Stan:GetChildren() })', "Server")
                        kk = js('return H:JSONEncode(J(k.Sygnaly.SterowanieKlienta:Invoke("koszt")))', "Client")
                        st = potwory_k("stan")
                        koszt["%s_%d" % (nazwa, zestaw)] = {"klatki": kl, "serwer": sw, "klient_potworow": kk,
                                                            "widoki": st.get("widoki"), "animowane": st.get("animowane"),
                                                            "czesciWidokow": st.get("czesciWidokow")}
                        zapisz("koszt", koszt)
                js('return H:JSONEncode(J(k.Sygnaly.SterowanieSerwera:Invoke("gracze", nil)))', "Server")

            # ================================================================ WALKI Z KAŻDYM GATUNKIEM I STRAŻNIK
            if "walki" in tylko:
                walki = {}
                luau(KP + 'k:SetAttribute("TestBezSesji", true) return "ok"', "Server")
                potwory_k("bohater", "zwiadowca", "auto")

                def walka_E(strefa, nazwa_zrzutu=None, bohater=None):
                    if bohater:
                        potwory_k("bohater", *bohater)
                    cel = czekaj_na(lambda: js('for _, c in k.Stan:GetChildren() do if c:GetAttribute("Strefa") == "%s" and c:GetAttribute("Stan") ~= "zajety" '
                                               'then return H:JSONEncode({ id = c.Name, p = J(c:GetAttribute("Pozycja")), poziom = c:GetAttribute("Poziom") }) end end '
                                               'return H:JSONEncode({})' % strefa, "Server") or None, 150, 2.0)
                    if not cel:
                        return {"blad": "brak wolnego potwora w strefie %s" % strefa}
                    licznik0 = int(luau(KP + 'return tostring(k:GetAttribute("SerwerLicznikWalk") or 0)', "Server"))
                    widzial_e, start, trwa, odmowy, proby_e = False, None, None, [], 0
                    for _proba in range(3):  # potwory chodzą: E przy oddalającym się potworze serwer może odrzucić
                        for _ in range(8):
                            p = js('local c = k.Stan:FindFirstChild("%s") return H:JSONEncode(J(c and c:GetAttribute("Pozycja") or Vector3.zero))' % cel["id"], "Server")
                            przestaw(p[0] - 5, p[1] + 3.2, p[2], (1, 0))
                            time.sleep(0.7)
                            st = potwory_k("stan")
                            if st.get("podpowiedz") and st.get("najblizszy") == cel["id"]:
                                widzial_e = True
                                start = poz()
                                proby_e += 1
                                luau(KP + 'k:SetAttribute("OstatniaOdmowa", nil) return "ok"', "Client")
                                nacisnij("E")
                                break
                        trwa = czekaj_na(lambda: potwory_k("stan").get("walka"), 6, 0.4)
                        if trwa:
                            break
                        odmowy.append(luau(KP + 'return tostring(k:GetAttribute("OstatniaOdmowa"))', "Client"))
                    na_arenie, postac_w_walce = None, None
                    odmowa = odmowy or None
                    if trwa:
                        time.sleep(3.5)
                        # walka to scena na arenie prototypu (TestWalki2): kamera jedzie na arenę, postać zostaje w pasie
                        kp = js('return H:JSONEncode(J(workspace.CurrentCamera.CFrame.Position))', "Client")
                        na_arenie = ARENA[0] - 40 <= kp[0] <= ARENA[1] + 40 and ARENA[2] - 40 <= kp[2] <= ARENA[3] + 40
                        postac_w_walce = poz()
                        if nazwa_zrzutu:
                            zrzut(nazwa_zrzutu)
                        js('return H:JSONEncode(J(workspace.TestWalki2.Sygnaly.Sterowanie:Invoke("przewinDo", 1000)))', "Client")
                        time.sleep(2.5)
                        js('return H:JSONEncode(J(workspace.TestWalki2.Sygnaly.Sterowanie:Invoke("zamknij")))', "Client")
                    czekaj_na(lambda: not potwory_k("stan").get("walka"), 30, 1.0)
                    time.sleep(1.5)
                    pk = poz()
                    licznik1 = int(luau(KP + 'return tostring(k:GetAttribute("SerwerLicznikWalk") or 0)', "Server"))
                    ost = luau(KP + 'return tostring(k:GetAttribute("SerwerOstatniaWalka"))', "Server")
                    kam = kamera()
                    powrot = (((pk[0] - start[0]) ** 2 + (pk[2] - start[2]) ** 2) ** 0.5) if start else None
                    return {"id": cel["id"], "poziom": cel.get("poziom"), "E": widzial_e, "walka": bool(trwa), "kamera_na_arenie": na_arenie,
                            "postac_w_czasie_walki": postac_w_walce, "odmowa": odmowa,
                            "proby_E": proby_e, "przyjeta": licznik1 > licznik0, "wynik": ost, "kamera": kam["typ"], "powrot_odl_st": powrot and round(powrot, 2),
                            "w_pasie": w_pasie(pk),
                            "ok": widzial_e and bool(trwa) and bool(na_arenie) and licznik1 > licznik0 and kam["typ"] == "Custom"
                            and powrot is not None and powrot < 3}

                for strefa, zr in (("s1", "w_slime_arena"), ("m1", None), ("w1", "w_wilk_arena"), ("t1", None)):
                    try:
                        walki[strefa] = walka_E(strefa, zr)
                    except Exception as e:  # noqa: BLE001
                        walki[strefa] = {"blad": str(e)[:300]}
                    zapisz("walki", walki)
                    time.sleep(1.0)

                # Strażnik: przegrana (bohater poz. 1) — brama zostaje zamknięta
                pasa("zamknijBrame")
                proby_przeg = []
                for ziarno in (5, 6, 7):
                    luau(KP + 'k:SetAttribute("ZiarnoTestowe", %d) return "ok"' % ziarno, "Server")
                    w = walka_E("straznik", None, ("wojownik", "1"))
                    proby_przeg.append(w)
                    if "przegrana" in str(w.get("wynik")):
                        break
                g = gracz()
                przestaw(X(2024), 3.5, -700, (1, 0))
                time.sleep(1.0)
                przestaw(X(2046), 3.5, -700, (1, 0))
                time.sleep(1.2)
                p_po_przeg = poz()
                walki["straznik_przegrana"] = {"proby": proby_przeg, "pokonal": g["pamiec"].get("pokonalStraznikaLasu"),
                                               "za_brama_po_przegranej": p_po_przeg,
                                               "ok": not g["pamiec"].get("pokonalStraznikaLasu") and p_po_przeg[0] < X(2034)}
                zapisz("walki", walki)

                # Strażnik: wygrana (bohater poz. 10, różne ziarna) — zrzut walki na arenie
                proby_wyg, wygrana = [], False
                for i, ziarno in enumerate((11, 23, 37, 41, 59, 73, 89, 97)):
                    luau(KP + 'k:SetAttribute("ZiarnoTestowe", %d) return "ok"' % ziarno, "Server")
                    w = walka_E("straznik", "w_straznik_arena" if i == 0 else None, ("zwiadowca", "10"))
                    proby_wyg.append(w)
                    wygrana = gracz()["pamiec"].get("pokonalStraznikaLasu")
                    if wygrana:
                        break
                time.sleep(2.0)
                baner = js('local e = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("LasPasGraEkran") '
                           'local b = e and e:FindFirstChild("Baner") return H:JSONEncode({ jest = b ~= nil, '
                           'tekst = b and b:FindFirstChild("Tytul") and b.Tytul.Text })', "Client")
                if not baner["jest"]:
                    time.sleep(2.0)
                    baner = js('local e = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("LasPasGraEkran") '
                               'local b = e and e:FindFirstChild("Baner") return H:JSONEncode({ jest = b ~= nil, '
                               'tekst = b and b:FindFirstChild("Tytul") and b.Tytul.Text })', "Client")
                # przejście przez otwartą bramę piechotą i tabliczka
                przestaw(X(2016), 3.5, -700, (1, 0))
                time.sleep(1.5)
                cof0 = luau(KP + 'return tostring(k:GetAttribute("LicznikCofniec") or 0)', "Server")
                przejscie = json.loads(luau(HRP_K + ('local XG, XH = %.2f, %.2f ' % (X(2046), X(2047))) + r'''
local t0 = os.clock()
while os.clock() - t0 < 6 and hrp.Position.X < XG do
	hum:MoveTo(Vector3.new(XH, hrp.Position.Y, -700))
	task.wait(0.1)
end
hum:MoveTo(hrp.Position)
return game:GetService("HttpService"):JSONEncode({ x = hrp.Position.X, y = hrp.Position.Y, czas = os.clock() - t0 })
''', "Client", proby=1, timeout=60))
                time.sleep(1.5)
                cof1 = luau(KP + 'return tostring(k:GetAttribute("LicznikCofniec") or 0)', "Server")
                p_za = poz()
                # ujęcie: brama za plecami? nie — gracz stoi za bramą, kamera patrzy na tabliczkę
                kamera_na((X(2022), 9, -713), (X(2052), 5.5, -700))
                time.sleep(1.5)
                zrzut("w_brama_otwarta_tabliczka")
                kamera_wroc()
                wrota = js('local m = workspace.LasPas.BramaBagna.Wrota local kol, prz, n = 0, 0, 0 for _, d in m:GetDescendants() do '
                           'if d:IsA("BasePart") then n += 1 if d.CanCollide then kol += 1 end if d.LocalTransparencyModifier > 0.99 then prz += 1 end end end '
                           'return H:JSONEncode({ czesci = n, kolizja = kol, niewidoczne = prz })', "Client")
                # za bramą (tylko zwycięzca): marsz w bok, gdzie nie ma ścian kulis — zatrzyma go coś albo spadnie
                # z Płyty i ratunek postawi go z powrotem za bramą
                r0 = luau(KP + 'return tostring(k:GetAttribute("LicznikRatunkow") or 0)', "Server")
                bok = json.loads(luau(HRP_K + ('local XB2 = %.2f ' % X(2060)) + r'''
local t0 = os.clock()
local yMin, zMin = hrp.Position.Y, hrp.Position.Z
while os.clock() - t0 < 9 do
	hum:MoveTo(Vector3.new(XB2, hrp.Position.Y, -830))
	yMin, zMin = math.min(yMin, hrp.Position.Y), math.min(zMin, hrp.Position.Z)
	task.wait(0.1)
end
return game:GetService("HttpService"):JSONEncode({ yMin = yMin, zMin = zMin, koniec = { hrp.Position.X, hrp.Position.Y, hrp.Position.Z } })
''', "Client", proby=1, timeout=60))
                time.sleep(2.0)
                bok["po"] = poz()
                bok["ratunki"] = [r0, luau(KP + 'return tostring(k:GetAttribute("LicznikRatunkow") or 0)', "Server")]
                bok["ok"] = bok["po"][1] > -5 and PAS[2] - 100 <= bok["po"][2] <= PAS[3] + 100
                walki["za_brama_w_bok"] = bok
                walki["straznik_wygrana"] = {"proby": proby_wyg, "wygrana": wygrana, "baner": baner, "przejscie": przejscie,
                                             "za_brama": p_za, "cofniecia": [cof0, cof1], "wrota_klient": wrota,
                                             "ok": bool(wygrana) and p_za[0] > X(2036) and cof0 == cof1}
                zapisz("walki", walki)
                luau(KP + 'k:SetAttribute("TestBezSesji", nil) k:SetAttribute("ZiarnoTestowe", nil) return "ok"', "Server")
                pasa("przenies", None, "las")

            # ================================================================ ZRZUTY POTWORÓW W PRZEGRODACH
            if "zrzuty" in tylko:
                zr = {}
                # potwory: kamera skryptowa ok. 16 st od potwora najbliższego środka przegrody, w pasie (|v| ≤ 28,
                # żeby nie wejść w korony kulis); postać obok, bo widoki buduje klient potworów wokół postaci
                for nazwa, strefa in (("z_slime_kojec", "s1"), ("z_muchomorniki", "m1"), ("z_wilki", "w1"),
                                      ("z_troll", "t1"), ("z_straznik", "straznik")):
                    cel = czekaj_na(lambda: js('local D = require(k.Moduly.DanePotworow) local pole for _, st in D.strefy do '
                                               'if st.id == "%s" then pole = st.pole end end local sx, sz = (pole.x1 + pole.x2) / 2, (pole.z1 + pole.z2) / 2 '
                                               'local naj, d = nil, math.huge for _, c in k.Stan:GetChildren() do local q = c:GetAttribute("Pozycja") '
                                               'if c:GetAttribute("Strefa") == "%s" and q and (q - Vector3.new(sx, q.Y, sz)).Magnitude < d then '
                                               'naj, d = q, (q - Vector3.new(sx, q.Y, sz)).Magnitude end end '
                                               'return H:JSONEncode(naj and J(naj) or {})' % (strefa, strefa), "Server") or None, 130, 2.0)
                    if not cel:
                        zr[nazwa] = "brak potwora w %s" % strefa
                        continue
                    mx, my, mz = cel
                    wys = 9 if strefa in ("t1", "straznik") else 6.5
                    oz = max(-728, min(-672, mz - 10))
                    przestaw(mx - 12, 3.5, max(-725, min(-675, mz + 9)), (1, 0))
                    time.sleep(3.0)
                    kamera_na((mx - 15, my + wys, oz), (mx + 2, my + (4 if strefa in ("t1", "straznik") else 1.5), mz))
                    time.sleep(2.0)
                    zr[nazwa] = zrzut(nazwa)
                    kamera_wroc()
                # otwarta brama (haczyk otworzBrame, gdy test walk nie wygrał) i tabliczka „Bagno — wkrótce”
                if not gracz()["pamiec"].get("pokonalStraznikaLasu"):
                    pasa("otworzBrame")
                przestaw(X(2046), 3.5, -689, (1, 0))
                time.sleep(2.5)
                kamera_na((X(2010), 7.5, -700), (X(2052), 6, -700))
                time.sleep(2.0)
                zr["z_brama_otwarta"] = zrzut("z_brama_otwarta")
                kamera_na((X(2041), 7, -703.5), (X(2052), 6.2, -700))
                time.sleep(1.5)
                zr["z_tabliczka"] = zrzut("z_tabliczka")
                kamera_wroc()
                # Kamień Powrotu: zwykła kamera za postacią, podpowiedź E na ekranie
                kpow = js('return H:JSONEncode(J(k.Punkty.KamienPowrotu.Position))', "Server")
                przestaw(kpow[0] + 6, 3.5, kpow[2] + 1, (-1, 0))
                time.sleep(2.5)
                pp = js('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("ProximityPrompts") '
                        'local n = 0 if g then for _, d in g:GetDescendants() do if d:IsA("GuiObject") and d.Visible then n += 1 end end end '
                        'return H:JSONEncode({ ekran = g ~= nil, widoczne = n, wlaczona = k.Punkty.KamienPowrotu.PodpowiedzPowrotu.Enabled })', "Client")
                zr["podpowiedz_kamienia"] = pp
                zr["z_kamien_powrotu"] = zrzut("z_kamien_powrotu")
                zapisz("zrzuty", zr)

            # dziennik pojawień i zniknięć potworów → czasy odrodzenia
            dz = luau(KP + 'return k:GetAttribute("TestDziennik") or "[]"', "Server")
            zdarzenia = json.loads(dz)
            odrodzenia = []
            for i, (t, znak, nazwa, strefa) in enumerate(zdarzenia):
                if znak != "-":
                    continue
                nast = next((e for e in zdarzenia[i + 1:] if e[1] == "+" and e[3] == strefa), None)
                odrodzenia.append({"strefa": strefa, "potwor": nazwa, "zniknal_s": t,
                                   "odrodzenie_s": round(nast[0] - t, 1) if nast else None})
            zapisz("odrodzenia", odrodzenia)
            kons = call("get_console_output", {}, timeout=60)["text"]
            imie = luau('return game:GetService("Players"):GetPlayers()[1].Name', "Server")
            # repo jest publiczne: nazwa konta gracza z konsoli zastąpiona znacznikiem
            linie = [x.strip()[:300].replace(imie, "<gracz>") for x in kons.splitlines()
                     if "LasPasGra" in x or "rror" in x or "TeleportChmury" in x]
            zapisz("konsola", linie[-80:])
        finally:
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
            for _ in range(60):
                time.sleep(0.5)
                if "Current Studio Mode: Edit" in stan_studio():
                    break
            log("tryb po próbie:", stan_studio().splitlines()[0])
            log("wyniki:", plik_wynikow)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
