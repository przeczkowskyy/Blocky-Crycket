# -*- coding: utf-8 -*-
"""Próba tabliczek potworów i portretów w walce (27.11.2026, polecenie Karola) — trzy biomy w jednym Play.

    python -B swiat/las_pas_gra/testy/proba_tabliczek.py <folder wyjściowy> [--studio <studio_id>] [--bez-zrzutow]

Warunki: Studio w trybie Edit, miejsce gry, zbudowane LasPasGra, BagnoPasGra, DzunglaPasGra (zbuduj.py --skrypty
każdego pakietu) i TestWalki2 z modułem IkonyPotworow (swiat/test_walki2/zbuduj.py --skrypty). Skrypt sam włącza i
wyłącza Play (tylko swoje), niczego nie zapisuje w miejscu i niczego nie publikuje. Wyniki: <wyj>/wyniki.json,
<wyj>/lista.txt, zrzuty <wyj>/<nazwa>.jpg oraz wycinki „jak na telefonie” (<nazwa>_667x375.jpg: tabliczka ma stały
rozmiar w punktach ekranu, więc wycinek 667 × 375 px wokół potwora pokazuje, ile miejsca zajmie na takim telefonie).

LISTA KONTROLNA (OK / BŁĄD / ?):
  T00 w Edit: trzy kontenery biomów i TestWalki2 z Moduly/IkonyPotworow (15 obrazów)
  T<biom>z / T<biom>r / T<biom>b (las, bagno, dzungla) tabliczka zwykłego potwora, rzadkiego (strefa t1) i Strażnika:
      nazwa = atrybut Nazwa, widoczna z bliska; „LV N” = atrybut Poziom; ranga zwykly / rare + „RARE” / boss + „BOSS”;
      kolor LV czerwony dokładnie wtedy, gdy poziom ≥ poziom bohatera z panelu + 3 (bohater: najniższy poziom z listy)
  T<biom>d nazwa zwykłego potwora chowa się dalej niż Stale.TABLICZKA_NAZWA_DO (kamera odsunięta), LV zostaje
  T<biom>p portret przeciwnika w walce (zwykły potwór biomu) to obraz (atrybut Portret = "obraz", ImageLabel wczytany),
      nie piksele
  T09 konsola: bez błędów skryptów pakietów potworów i walki
"""
import io
import json
import os
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TU)))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"),
           os.path.join(REPO, "swiat", "test_walki2", "testy")):
    sys.path.insert(0, _s)
import importlib.util as _ilu  # noqa: E402
_sp = _ilu.spec_from_file_location("cutscenka_pomoc_prob", os.path.join(REPO, "swiat", "cutscenka_biomu", "pomoc_prob.py"))
PP = _ilu.module_from_spec(_sp)
_sp.loader.exec_module(PP)

H = 'local H = game:GetService("HttpService") '
J = ('local function J(v) local t = typeof(v) if t == "Vector3" then return { v.X, v.Y, v.Z } '
     'elseif t == "Color3" then return v:ToHex() '
     'elseif t == "table" then local o = {} if #v > 0 then for i, b in ipairs(v) do o[i] = J(b) end '
     'else for a, b in v do o[tostring(a)] = J(b) end end return o '
     'elseif t == "Instance" then return v:GetFullName() end return v end ')
HRP = 'local hrp = game:GetService("Players"):GetPlayers()[1].Character.HumanoidRootPart '
# biom → (kontener, najniższy poziom bohatera z listy panelu, nazwa w zrzutach)
BIOMY = [("las", "LasPasGra", "1"), ("bagno", "BagnoPasGra", "10"), ("dzungla", "DzunglaPasGra", "17")]
CZERWONY = "e8364f"
NAZWA_DO = 55
WYNIKI, LISTA = {}, []


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# tabliczka widoku u klienta (Workspace/<kontener>/Widoki/<id>/Tabliczka) i atrybuty potwora z Stan
TABLICZKA = H + J + '''
local k = workspace:FindFirstChild("%s")
local cfg = k and k.Stan:FindFirstChild("%s")
local m = k and k:FindFirstChild("Widoki") and k.Widoki:FindFirstChild("%s")
local bb = m and m:FindFirstChild("Tabliczka")
if not bb then return H:JSONEncode({ brak = true, cfg = cfg ~= nil }) end
local r = bb:FindFirstChild("Rzad")
local lv = r and r:FindFirstChild("Poziom")
local chip = r and r:FindFirstChild("Ranga")
local napis = chip and chip:FindFirstChild("Napis")
local cam = workspace.CurrentCamera
return H:JSONEncode(J({ nazwa = bb.Nazwa.Text, nazwaWidac = bb.Nazwa.Visible, lv = lv and lv.Text, kolor = lv and lv.BackgroundColor3,
	ranga = bb:GetAttribute("Ranga"), chip = napis and napis.Text, chipWidac = chip ~= nil and chip.Visible, max = bb.MaxDistance,
	cfgNazwa = cfg and cfg:GetAttribute("Nazwa"), cfgPoziom = cfg and cfg:GetAttribute("Poziom"),
	odl = math.floor((cam.CFrame.Position - bb.Adornee.WorldPosition).Magnitude),
	ekran = (function() local p, w = cam:WorldToViewportPoint(bb.Adornee.WorldPosition) return { p.X, p.Y, w } end)(),
	okno = { cam.ViewportSize.X, cam.ViewportSize.Y } }))
'''

PORTRET = H + '''
local pg = game:GetService("Players").LocalPlayer.PlayerGui
for _, d in pg:GetDescendants() do
	if d.Name == "TabliczkaWroga" then
		local p = d:FindFirstChild("Portret")
		local img = p and p:FindFirstChild("Obraz")
		local pix = p and p:FindFirstChild("Ikona")
		return H:JSONEncode({ portret = p and p:GetAttribute("Portret"), obraz = img and img.Image, wczytany = img and img.IsLoaded,
			piksele = pix and pix.Visible, nazwa = d:FindFirstChild("Nazwa") and d.Nazwa.Text })
	end
end
return H:JSONEncode({ brak = true })
'''


def main():
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
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
    from PIL import Image  # noqa: E402

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
                except Exception as e:  # noqa: BLE001
                    if i == proby - 1:
                        raise
                    log("luau: ponawiam po błędzie:", str(e)[:200])
                    time.sleep(8)

        def js(kod, dm):
            return json.loads(luau(kod, dm))

        def stan_studio():
            return call("get_studio_state")["text"]

        def zrzut(nazwa, srodek=None):
            """Zrzut okna; srodek = (x, y) w pikselach okna Studio → dodatkowo wycinek 667 × 375 wokół tego punktu."""
            if bez_zrzutow:
                return None
            nie_usypiaj()
            r = call("screen_capture", {"capture_id": "tabliczki_" + nazwa}, timeout=150)
            if r["is_error"] or not r.get("images"):
                log("zrzut %s: BŁĄD %s" % (nazwa, r["text"][:120]))
                return None
            im = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
            if srodek:
                okno = srodek[2]
                sk = im.width / float(okno[0]) if okno and okno[0] else 1.0
                cx, cy = srodek[0] * sk, srodek[1] * sk
                w, h = 667 * sk, 375 * sk
                x0 = max(0, min(im.width - w, cx - w / 2))
                y0 = max(0, min(im.height - h, cy - h * 0.45))
                im.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((667, 375), Image.LANCZOS).save(
                    os.path.join(wyj, nazwa + "_667x375.jpg"), "JPEG", quality=88)
            if im.width > 1280:
                im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
            sciezka = os.path.join(wyj, nazwa + ".jpg")
            im.save(sciezka, "JPEG", quality=85)
            log("zrzut", nazwa)
            return sciezka

        def czekaj_na(warunek, limit, co=0.5):
            t0 = time.time()
            while time.time() - t0 < limit:
                w = warunek()
                if w:
                    return w
                time.sleep(co)
            return None

        def hak_klienta(kont, *argi):
            a = ", ".join("nil" if x is None else json.dumps(x) for x in argi)
            return js(H + J + 'return H:JSONEncode(J(workspace.%s.Sygnaly.SterowanieKlienta:Invoke(%s)))' % (kont, a), "Client")

        def odtw(polecenie):
            return js(H + J + 'return H:JSONEncode(J(workspace.TestWalki2.Sygnaly.Sterowanie:Invoke(%s)))' % polecenie, "Client")

        def przestaw(x, y, z, patrz):
            luau(HRP + 'local p = Vector3.new(%f, %f, %f) local c = Vector3.new(%f, p.Y, %f) '
                       'hrp.Parent:PivotTo(CFrame.lookAt(p, c)) hrp.AssemblyLinearVelocity = Vector3.zero return "ok"'
                 % (x, y, z, patrz[0], patrz[2]), "Server")

        def patrz_na(cel, wys=3.0):
            """Kamera gracza (zostaje Custom) za postacią, patrzy na punkt wys studs nad celem — moduł kamery bierze
            kierunek (z pochyleniem) z bieżącej CFrame, odległość od postaci zostaje jego."""
            luau('local c = workspace.CurrentCamera local h = game:GetService("Players").LocalPlayer.Character.HumanoidRootPart '
                 'local cel = Vector3.new(%f, %f, %f) local d = cel - h.Position d = Vector3.new(d.X, 0, d.Z).Unit '
                 'c.CFrame = CFrame.lookAt(h.Position - d * 12 + Vector3.new(0, 6, 0), cel + Vector3.new(0, %f, 0)) return "ok"'
                 % (cel[0], cel[1], cel[2], wys), "Client")

        def wysokosc_tabliczki(kont, id_):
            """Wysokość punktu tabliczki nad pozycją potwora (studs) — duże potwory kadrujemy z dalszej odległości."""
            try:
                return float(luau('local k = workspace.%s local m = k.Widoki:FindFirstChild("%s") local c = k.Stan:FindFirstChild("%s") '
                                  'local bb = m and m:FindFirstChild("Tabliczka") if not (bb and c) then return "6" end '
                                  'return tostring(bb.Adornee.WorldPosition.Y - c:GetAttribute("Pozycja").Y)' % (kont, id_, id_), "Client"))
            except Exception:  # noqa: BLE001
                return 6.0

        nie_usypiaj()
        if "Current Studio Mode: Edit" not in stan_studio():
            sys.exit("Studio nie jest w trybie Edit — ta próba sama włącza Play")
        edit = js(H + 'local o = {} for _, n in { "LasPasGra", "BagnoPasGra", "DzunglaPasGra", "TestWalki2" } do '
                  'local k = workspace:FindFirstChild(n) o[n] = k ~= nil and k:GetAttribute("Wygenerowane") == true end '
                  'local m = workspace:FindFirstChild("TestWalki2") and workspace.TestWalki2.Moduly:FindFirstChild("IkonyPotworow") '
                  'local n = 0 if m then for _ in m.Source:gmatch("rbxassetid://%d+") do n += 1 end end '
                  'o.ikony = n return H:JSONEncode(o)', "Edit")
        zapisz("T00", edit)
        punkt("T00", all(edit.get(n) for n in ("LasPasGra", "BagnoPasGra", "DzunglaPasGra", "TestWalki2")) and edit.get("ikony") == 15,
              "kontenery i moduł ikon: %s" % edit)

        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        try:
            czekaj_na(lambda: "Client" in stan_studio() and luau(
                'local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)', "Client") == "true",
                90, 1.0)
            luau('local SG = game:GetService("StarterGui") for _, t in { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Chat } do '
                 'pcall(function() SG:SetCoreGuiEnabled(t, false) end) end return "ok"', "Client")
            for _b, kont, _p in BIOMY:
                luau('local k = workspace:FindFirstChild("%s") if k then k:SetAttribute("TestBohater", true) '
                     'k:SetAttribute("TestBezSesji", true) end return "ok"' % kont, "Server")
            time.sleep(3)
            for kont in ("LasPasGra", "BagnoPasGra"):
                luau('return tostring(workspace.%s.Sygnaly.SterowaniePasa:Invoke("otworzBrame"))' % kont, "Server")
            PP.oznacz(luau, ["las", "bagno", "dzungla"])
            time.sleep(6)  # baner „Brama do Bagna otwarta!” po otworzeniu bramy znika po Stale.BANER_S
            czekaj_na(lambda: all(js(H + 'local k = workspace:FindFirstChild("%s") return H:JSONEncode({ g = k and k:GetAttribute("KlientGotowy") == true })'
                                     % kont, "Client").get("g") for _b, kont, _p in BIOMY), 60, 1.0)
            for _ in range(20):
                wybor = js(H + 'local p = game:GetService("Players").LocalPlayer local g = p.PlayerGui:FindFirstChild("ClassSelect") '
                           'return H:JSONEncode({ ekran = g ~= nil and g.Enabled, kamera = workspace.CurrentCamera.CameraType.Name })', "Client")
                if not wybor["ekran"] and wybor["kamera"] == "Custom":
                    break
                call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": "Return"}]})
                time.sleep(1.5)
            zrzuty = {}

            for biom, kont, niski in BIOMY:
                # potwory: zwykły (pierwsza strefa bez rangi), rzadki (strefa t1), Strażnik (atrybut Straznik)
                wybrane = js(H + J + '''
local k = workspace.%s local o = {}
for _, c in k.Stan:GetChildren() do
	local st, zaj = c:GetAttribute("Strefa"), c:GetAttribute("Stan") == "zajety"
	local wpis = { id = c.Name, p = c:GetAttribute("Pozycja"), strefa = st }
	if c:GetAttribute("Straznik") == true then o.b = o.b or wpis
	elseif st == "t1" then o.r = o.r or wpis
	elseif not zaj and (o.z == nil or tostring(st) < tostring(o.z.strefa)) then o.z = wpis end
end
return H:JSONEncode(J(o))''' % kont, "Server")
                zapisz("wybrane_" + biom, wybrane)
                ok_bohater = hak_klienta(kont, "bohater", "wojownik", niski)
                for kod, rodzaj, oczek_ranga, oczek_chip in (("z", "zwykly", "zwykly", None), ("r", "rzadki", "rare", "RARE"),
                                                              ("b", "straznik", "boss", "BOSS")):
                    w = wybrane.get(kod)
                    nazwa_pkt = "T%s%s" % (biom, kod)
                    if not w:
                        punkt(nazwa_pkt, False, "brak potwora (%s) w Stan" % rodzaj)
                        continue
                    p = w["p"]
                    przestaw(p[0] - 9, p[1] + 3.5, p[2] + 3, p)
                    hak_klienta(kont, "wymus", w["id"])
                    czekaj_na(lambda: not js(TABLICZKA % (kont, w["id"], w["id"]), "Client").get("brak"), 12, 0.6)
                    hw = wysokosc_tabliczki(kont, w["id"])
                    if hw > 7:  # duży potwór (troll, Strażnik): dalej, żeby tabliczka nad głową weszła w kadr
                        przestaw(p[0] - (6 + 1.3 * hw), p[1] + 3.5, p[2] + 3, p)
                    time.sleep(0.5)
                    patrz_na(p, hw * 0.6)
                    t = czekaj_na(lambda: (lambda d: d if not d.get("brak") else None)(js(TABLICZKA % (kont, w["id"], w["id"]), "Client")), 12, 0.6)
                    time.sleep(1.2)
                    t = js(TABLICZKA % (kont, w["id"], w["id"]), "Client") if t else {"brak": True}
                    czerwone_ma_byc = isinstance(t.get("cfgPoziom"), (int, float)) and t["cfgPoziom"] >= int(niski) + 3
                    zapisz(nazwa_pkt, {"potwor": w, "tabliczka": t, "bohater": [ok_bohater, niski], "czerwone_ma_byc": czerwone_ma_byc})
                    ok = (not t.get("brak") and t.get("nazwa") == t.get("cfgNazwa") and t.get("nazwaWidac") is True
                          and t.get("lv") == "LV %s" % t.get("cfgPoziom") and t.get("ranga") == oczek_ranga
                          and (t.get("chip") == oczek_chip) and ((str(t.get("kolor")).lower() == CZERWONY) == czerwone_ma_byc))
                    punkt(nazwa_pkt, ok, "%s %s: „%s” %s, ranga %s / %s, LV kolor %s (czerwone ma być: %s), zasięg %s, kamera %s st"
                          % (rodzaj, w["id"], t.get("nazwa"), t.get("lv"), t.get("ranga"), t.get("chip"), t.get("kolor"),
                             czerwone_ma_byc, t.get("max"), t.get("odl")))
                    e = t.get("ekran") or [0, 0, False]
                    zrzuty[nazwa_pkt] = zrzut("%s_tabliczka_%s" % (biom, rodzaj),
                                              (e[0], e[1], t.get("okno")) if isinstance(e, list) and len(e) == 3 and e[2] else None)
                    if kod == "z":
                        # T<biom>d: z daleka (kamera ok. 75 studs) nazwa zwykłego potwora schowana, LV zostaje
                        przestaw(p[0] - 62, p[1] + 3.5, p[2] + 3, p)
                        time.sleep(0.5)
                        patrz_na(p)
                        time.sleep(1.5)
                        td = js(TABLICZKA % (kont, w["id"], w["id"]), "Client")
                        zapisz(nazwa_pkt + "_daleko", td)
                        punkt("T%sd" % biom, not td.get("brak") and td.get("odl", 0) > NAZWA_DO and td.get("nazwaWidac") is False
                              and str(td.get("lv", "")).startswith("LV "),
                              "z %s st: nazwa widoczna %s, %s" % (td.get("odl"), td.get("nazwaWidac"), td.get("lv")))
                        zrzut("%s_tabliczki_z_daleka" % biom)
                hak_klienta(kont, "wymus", None)

                # T<biom>p: portret przeciwnika w walce (zwykły potwór)
                w = wybrane.get("z")
                hak_klienta(kont, "bohater", "zwiadowca", "auto")
                wynik_p = {"brak": True}
                if w:
                    p = js(H + J + 'local c = workspace.%s.Stan:FindFirstChild("%s") return H:JSONEncode(J(c and c:GetAttribute("Pozycja") or Vector3.zero))'
                           % (kont, w["id"]), "Server")
                    przestaw(p[0] - 4, p[1] + 3.2, p[2], p)
                    time.sleep(0.6)
                    zaczal = hak_klienta(kont, "walcz", w["id"])
                    trwa = czekaj_na(lambda: hak_klienta(kont, "stan").get("walka"), 12, 0.5)
                    if trwa:
                        wynik_p = czekaj_na(lambda: (lambda d: d if d.get("portret") == "obraz" else None)(js(PORTRET, "Client")), 10, 0.5) \
                            or js(PORTRET, "Client")
                        time.sleep(2.5)
                        zrzuty["T%sp" % biom] = zrzut("%s_walka_portret" % biom)
                        odtw('"przewinDo", 1000')
                        time.sleep(2.5)
                        odtw('"zamknij"')
                        czekaj_na(lambda: not hak_klienta(kont, "stan").get("walka"), 30, 1.0)
                        time.sleep(1.5)
                    wynik_p["zaczal"], wynik_p["trwa"] = zaczal, bool(trwa)
                zapisz("T%sp" % biom, wynik_p)
                punkt("T%sp" % biom, wynik_p.get("portret") == "obraz" and wynik_p.get("wczytany") is True and wynik_p.get("piksele") is False
                      and str(wynik_p.get("obraz", "")).startswith("rbxassetid://"),
                      "portret %s: %s, obraz %s, wczytany %s, piksele widać %s" % (
                          wynik_p.get("nazwa"), wynik_p.get("portret"), wynik_p.get("obraz"), wynik_p.get("wczytany"), wynik_p.get("piksele")))

            # T09 konsola
            kons = call("get_console_output", {}, timeout=60)["text"] or ""
            zle = [x for x in kons.splitlines() if ("[LasPasGra]" in x or "[BagnoPasGra]" in x or "[DzunglaPasGra]" in x
                                                    or "TestWalki2" in x or "InterfejsWalki2" in x or "KlientPotworow" in x)
                   and ("błąd" in x.lower() or "error" in x.lower() or "attempt to" in x)]
            zapisz("T09", zle[:30])
            punkt("T09", not zle, "błędy w konsoli: %d %s" % (len(zle), zle[:3]))
            zapisz("zrzuty", zrzuty)
        finally:
            for _b, kont, _p in BIOMY:
                try:
                    luau('local k = workspace:FindFirstChild("%s") if k then k:SetAttribute("TestBezSesji", nil) end return "ok"' % kont, "Server")
                except Exception:  # noqa: BLE001
                    pass
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
    print("\n".join("%s %-4s %s" % x for x in LISTA))
    zle = [x for x in LISTA if x[1] != "OK"]
    print("OK %d, BŁĄD %d, ? %d" % (sum(1 for x in LISTA if x[1] == "OK"), sum(1 for x in LISTA if x[1] == "BŁĄD"),
                                    sum(1 for x in LISTA if x[1] == "?")))
    sys.exit(1 if zle else 0)


if __name__ == "__main__":
    main()
