# -*- coding: utf-8 -*-
"""D-107 (walka bez przestojów) — wspólne punkty prób w Play dla lasu, Bagna i Dżungli.

Woła je proba_play.py każdego biomu (ten sam kod potworów, więc te same punkty), podając swoje funkcje pomocnicze;
samodzielnie (krótka próba tylko tych punktów): testy/proba_d107.py.

    D1  liczba potworów: przy 1 graczu każda strefa ma tyle potworów, ile mówi Logika.cel; po „gracze = 20” strefy
        dopełniają się do pełnego zestawu w czasie odrodzenia
    D2  odradzanie w zadanym czasie: zabity zwykły potwór, rzadki i strażnik wracają po czasie z danych (± pętla 1 s)
    D3  koszt przy pełnym zestawie (gracze = 20) w najgęstszej strefie: klatka klienta (śr., p95), widoki potworów
        i ich bryły (budżet klienta), pętla ruchu serwera
    D4  brak czekania po przegranej: walka ze strażnikiem przegrana i OBEJRZANA do końca przy tempie ×4 (bez
        pomijania) — po zamknięciu wyniku gracz nie ma blokady („następna za … s”), strażnik nie jest zajęty,
        a rewanż (E przy nim) rusza od razu
    D5  czas pominiętej walki: E → przycisk POMIŃ → wynik → powrót na pas, mierzony u klienta (bez czasu reakcji
        człowieka); potwierdza założenie rachunku „gracz nigdy nie czeka” (test_bez_przestojow.py)

Kody punktów: <litera biomu>D1 … D5 (PD1, BD1, JD1 …). Liczby oczekiwane czyta z danych generatora (nie na sztywno).
Punkty zostawiają pas w stanie zastanym: TestGraczy = nil, nadmiar potworów usunięty, ziarno i bohater testowy zdjęte.
"""
import importlib.util
import json
import os
import sys
import time


def wczytaj_liczby(repo, pakiet):
    """Liczby D-107 pakietu biomu (las_pas_gra | bagno_pas_gra | dzungla_pas_gra) prosto z jego generatora danych."""
    def modul(nazwa, sciezka):
        spec = importlib.util.spec_from_file_location(nazwa, sciezka)
        m = importlib.util.module_from_spec(spec)
        sys.path.insert(0, os.path.dirname(sciezka))
        sys.modules.pop("przeciwnicy", None)   # Bagno i Dżungla mają moduł o tej samej nazwie
        try:
            spec.loader.exec_module(m)
        finally:
            sys.path.remove(os.path.dirname(sciezka))
        return m
    gen = modul("generuj_dane_proby_d107_" + pakiet, os.path.join(repo, "swiat", pakiet, "generuj_dane.py"))
    lg = modul("logika_potworow_proby_d107", os.path.join(repo, "swiat", "las_potwory", "logika.py"))
    return liczby(gen.wszystko()[1], lg.cel)


def liczby(dp, cel):
    """dp = dane potworów z generatora biomu (generuj_dane.wszystko()[1]); cel = Logika.cel z lustra w Pythonie."""
    strefy = []
    for s in dp["strefy"]:
        strefy.append({"id": s["id"], "straznik": bool(s["straznik"]), "rzadki": bool(s.get("rzadki")),
                       "cel1": 1 if s["straznik"] else cel(s["naraz"], s["max"], 1),
                       "cel20": 1 if s["straznik"] else cel(s["naraz"], s["max"], 20),
                       "odrodzenie": s["odrodzenieS"], "x": s["srodek"][0], "z": s["srodek"][2],
                       "promien": dp["gatunki"][s["gatunek"]]["promien"]})
    return {"strefy": strefy, "razem1": sum(s["cel1"] for s in strefy), "razem20": sum(s["cel20"] for s in strefy)}


def _tabela(slownik):
    return "{ " + ", ".join('["%s"] = %s' % (k, v) for k, v in slownik.items()) + " }"


REJESTRATOR = '''
local k = workspace:FindFirstChild("%s")
local UIS = game:GetService("UserInputService")
local H = game:GetService("HttpService")
local S = workspace.TestWalki2.Sygnaly.Sterowanie
local SK = k.Sygnaly.SterowanieKlienta
k:SetAttribute("PomiarD107", nil)
task.spawn(function()
	local z = {}
	local t0 = os.clock()
	local pol = UIS.InputBegan:Connect(function(w)
		if w.KeyCode == Enum.KeyCode.E and not z.E then z.E = os.clock() - t0 end
		if w.KeyCode == Enum.KeyCode.Space and not z.spacja then z.spacja = os.clock() - t0 end
	end)
	local function czekaj(f, limit)
		local t = os.clock()
		while os.clock() - t < limit do
			local ok, w = pcall(f)
			if ok and w then return true end
			task.wait()
		end
		return false
	end
	if czekaj(function() return SK:Invoke("stan").walka end, 15) then z.walka = os.clock() - t0 end
	if z.walka and czekaj(function() return S:Invoke("stan").pomijanieNaEkranie == true end, 12) then z.przycisk = os.clock() - t0 end
	if z.walka and czekaj(function() return S:Invoke("stan").faza == "wynik" end, 45) then z.wynik = os.clock() - t0 end
	if z.wynik then S:Invoke("zamknij") z.zamknij = os.clock() - t0 end
	if z.walka and czekaj(function() return not SK:Invoke("stan").walka end, 20) then z.koniec = os.clock() - t0 end
	pol:Disconnect()
	k:SetAttribute("PomiarD107", H:JSONEncode(z))
end)
return "ok"
'''


def punkty(litera, kontener, L, luau, punkt, zapisz, przestaw, nacisnij, czekaj_na, klient_potworow, odtw, zrzut=None):
    """litera: "P" | "B" | "J"; kontener: nazwa kontenera potworów; L = liczby(); reszta — pomoc proby biomu.
    zrzut (opcjonalnie): funkcja zrzut(nazwa) — dwa zrzuty: pełna strefa i chwila po przegranej z rewanżem."""
    K = ('local k = workspace:FindFirstChild("%s") local H = game:GetService("HttpService") '
         'local S = k.Sygnaly.SterowanieSerwera '
         'local function licz() local t = {} for _, c in k.Stan:GetChildren() do local s = c:GetAttribute("Strefa") '
         't[s] = (t[s] or 0) + 1 end return t end '
         'local function rowne(cel) local t = licz() for s, n in cel do if (t[s] or 0) ~= n then return false end end return true end '
         'local function przytnij(cel) for _, c in k.Stan:GetChildren() do local s = c:GetAttribute("Strefa") '
         'local t = licz() if cel[s] and (t[s] or 0) > cel[s] and c:GetAttribute("Stan") ~= "zajety" then S:Invoke("zabij", c.Name) end end end '
         % kontener)
    KA = 'local k = workspace:FindFirstChild("%s") ' % kontener

    def js(kod, dm="Server"):
        return json.loads(luau(K + kod, dm))

    def fotka(nazwa):
        if zrzut is not None:
            try:
                zrzut(nazwa)
            except Exception:  # noqa: BLE001
                pass

    cel1 = {s["id"]: s["cel1"] for s in L["strefy"]}
    cel20 = {s["id"]: s["cel20"] for s in L["strefy"]}
    zwykle = [s for s in L["strefy"] if not s["straznik"] and not s["rzadki"]]
    rzadkie = [s for s in L["strefy"] if s["rzadki"]]
    straznik = next(s for s in L["strefy"] if s["straznik"])

    def pozycja(id_potwora):
        return js('local c = k.Stan:FindFirstChild("%s") local v = c and c:GetAttribute("Pozycja") '
                  'return H:JSONEncode(v and { v.X, v.Y, v.Z } or {})' % id_potwora)

    def podejdz_i_walcz(id_potwora, promien, przed_e=None):
        """Staje przy potworze, czeka na podpowiedź E i naciska E. → {walka, start_po_s, odmowy}"""
        w = {"odmowy": []}
        t0 = time.time()
        for _ in range(8):
            p = pozycja(id_potwora)
            if not p:
                w["brak_potwora"] = True
                break
            przestaw(p[0] - (promien + 3.5), p[1] + 3.2, p[2])
            time.sleep(0.6)
            kp = klient_potworow()
            if kp.get("podpowiedz") and kp.get("najblizszy") == id_potwora:
                luau(KA + 'k:SetAttribute("OstatniaOdmowa", nil) return "ok"', "Client")
                if przed_e:
                    przed_e()
                nacisnij("E")
                if czekaj_na(lambda: klient_potworow().get("walka"), 6, 0.3):
                    break
                w["odmowy"].append(luau(KA + 'return tostring(k:GetAttribute("OstatniaOdmowa"))', "Client"))
        w["walka"] = bool(klient_potworow().get("walka"))
        w["start_po_s"] = round(time.time() - t0, 1)
        return w

    def patrz_w_strone(kierunek_x):
        """Kamera za plecami postaci, wzdłuż pasa (tylko do zrzutów; kamera Custom zachowuje kierunek)."""
        try:
            luau('local p = game:GetService("Players").LocalPlayer local h = p.Character and p.Character:FindFirstChild("HumanoidRootPart") '
                 'local c = workspace.CurrentCamera if h and c.CameraType == Enum.CameraType.Custom then '
                 'c.CFrame = CFrame.lookAt(h.Position + Vector3.new(%d, 7, 0), h.Position + Vector3.new(%d, 1, 0)) end return "ok"'
                 % (-14 * kierunek_x, 20 * kierunek_x), "Client")
        except Exception:  # noqa: BLE001
            pass

    def bohater(klasa, poziom):
        return luau(KA + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("bohater", "%s", "%s"))' % (klasa, poziom), "Client")

    # ------------------------------------------------------------------------------------------ D1 liczba potworów
    d1 = {}
    try:
        d1["jeden"] = js('S:Invoke("gracze", nil) local cel = %s przytnij(cel) local t0 = os.clock() '
                         'while not rowne(cel) and os.clock() - t0 < 45 do task.wait(0.5) end '
                         'return H:JSONEncode({ stan = licz(), ok = rowne(cel), czas = os.clock() - t0, '
                         'potworow = k:GetAttribute("Potworow") })' % _tabela(cel1))
        d1["dwudziestu"] = js('S:Invoke("gracze", 20) local cel = %s local t0 = os.clock() '
                              'while not rowne(cel) and os.clock() - t0 < 25 do task.wait(0.25) end '
                              'return H:JSONEncode({ stan = licz(), ok = rowne(cel), czas = os.clock() - t0, '
                              'potworow = k:GetAttribute("Potworow") })' % _tabela(cel20))
    except Exception as e:  # noqa: BLE001
        d1["wyjatek"] = str(e)[:300]
    zapisz(litera + "D1", d1)
    j, d = d1.get("jeden") or {}, d1.get("dwudziestu") or {}
    najdluzsze = max(s["odrodzenie"] for s in zwykle)
    punkt(litera + "D1", bool(j.get("ok")) and j.get("potworow") == L["razem1"] and bool(d.get("ok"))
          and d.get("potworow") == L["razem20"] and d.get("czas", 99) <= najdluzsze + 3,
          "1 gracz: %s (razem %s, ma być %d); 20 graczy: %s (razem %s, ma być %d) po %.1f s" % (
              j.get("stan"), j.get("potworow"), L["razem1"], d.get("stan"), d.get("potworow"), L["razem20"], d.get("czas", -1)))

    # ------------------------------------------------------------------------------------------ D3 koszt
    # (przed D2: pełny zestaw jeszcze stoi)
    d3 = {}
    try:
        gesta = zwykle[-1]
        if zrzut is not None:
            # zrzut „widok gracza”: gracz na dróżce przed strefą, kamera za plecami patrzy w głąb strefy
            przestaw(gesta["x"] - 30, 3.5, gesta["z"])
            time.sleep(6)
            patrz_w_strone(1)
            time.sleep(1.5)
            fotka("d107_strefa_pelna")
        przestaw(gesta["x"], 3.5, gesta["z"])
        time.sleep(8)       # budowa widoków (jeden klon co 0,1 s) i wejście nowych potworów na pętlę
        luau(K + 'S:Invoke("koszt", true) return "ok"', "Server")
        luau(K + 'k.Sygnaly.SterowanieKlienta:Invoke("koszt", true) return "ok"', "Client")
        d3["klatki"] = js('local RS = game:GetService("RunService") local t = {} '
                          'local c = RS.RenderStepped:Connect(function(dt) table.insert(t, dt) end) task.wait(8) c:Disconnect() '
                          'table.sort(t) local s = 0 for _, x in t do s += x end '
                          'return H:JSONEncode({ n = #t, sr_ms = s / math.max(1, #t) * 1000, '
                          'p95_ms = (t[math.max(1, math.floor(#t * 0.95))] or 0) * 1000, maks_ms = (t[#t] or 0) * 1000 })', "Client")
        d3["serwer"] = js('local w = S:Invoke("koszt") local r = w.ruchu or {} local t = licz() '
                          'return H:JSONEncode({ ruch_sr_ms = r.sr or -1, ruch_maks_ms = r.maks or -1, potworow = k:GetAttribute("Potworow"), '
                          'w_strefie = t["%s"] or 0 })' % gesta["id"])
        kp = klient_potworow()
        d3["klient"] = {x: kp.get(x) for x in ("tryb", "widoki", "animowane", "czesciWidokow")}
        d3["klient_koszt"] = luau(K + 'local w = k.Sygnaly.SterowanieKlienta:Invoke("koszt") '
                                      'local ok, tekst = pcall(function() return H:JSONEncode(w) end) '
                                      'return if ok then tekst else "?"', "Client")[:600]
        d3["strefa"] = gesta["id"]
    except Exception as e:  # noqa: BLE001
        d3["wyjatek"] = str(e)[:300]
    zapisz(litera + "D3", d3)
    kl, se, kli = d3.get("klatki") or {}, d3.get("serwer") or {}, d3.get("klient") or {}
    w_budzecie = kli.get("widoki") is not None and se.get("potworow") is not None
    if not kl or not se:
        ok3 = False
    elif kl["sr_ms"] > 25:
        ok3 = None      # okno Studio w tle rysuje 15 kl./s — klatkę ocenia człowiek
    else:
        # każdy potwór najgęstszej strefy ma widok (najbliższe mają pierwszeństwo w budżecie brył klienta)
        ok3 = (kl["p95_ms"] <= 34 and 0 <= se["ruch_sr_ms"] <= 1.0 and w_budzecie
               and kli["widoki"] >= se["w_strefie"] and (kli.get("czesciWidokow") or 0) <= 4000)
    punkt(litera + "D3", ok3, "pełny zestaw (%s potworów, w strefie %s: %s): klatka śr. %.1f ms, p95 %.1f ms, maks. %.1f ms; "
          "widoków %s, brył widoków %s; pętla ruchu serwera śr. %.2f ms, maks. %.2f ms%s" % (
              se.get("potworow"), d3.get("strefa"), se.get("w_strefie"), kl.get("sr_ms", -1), kl.get("p95_ms", -1),
              kl.get("maks_ms", -1), kli.get("widoki"), kli.get("czesciWidokow"), se.get("ruch_sr_ms", -1),
              se.get("ruch_maks_ms", -1), "" if w_budzecie else " (brak danych klienta)"))
    try:
        js('S:Invoke("gracze", nil) local cel = %s przytnij(cel) task.wait(0.5) przytnij(cel) '
           'return H:JSONEncode({ stan = licz() })' % _tabela(cel1))
    except Exception:  # noqa: BLE001
        pass

    # ------------------------------------------------------------------------------------------ D2 odradzanie
    d2 = {}
    cele = [("zwykly", zwykle[0])] + [("rzadki", s) for s in rzadkie[:1]] + [("straznik", straznik)]
    try:
        # wszystkie strefy pełne (strażnik i rzadki mogły być pokonane we wcześniejszych punktach)
        js('local cel = %s local t0 = os.clock() while not rowne(cel) and os.clock() - t0 < 45 do task.wait(0.5) end '
           'return H:JSONEncode({ ok = rowne(cel) })' % _tabela(cel1))
        strefy_lua = "{ " + ", ".join('"%s"' % s["id"] for _, s in cele) + " }"
        d2["pomiar"] = js('local strefy = %s local przed = licz() local t0 = os.clock() local wrocil = {} '
                          'for _, s in strefy do for _, c in k.Stan:GetChildren() do '
                          'if c:GetAttribute("Strefa") == s and c:GetAttribute("Stan") ~= "zajety" then S:Invoke("zabij", c.Name) break end end end '
                          'local zaraz = licz() '
                          'while os.clock() - t0 < 50 do local t = licz() local wszystkie = true '
                          'for _, s in strefy do if wrocil[s] == nil then if (t[s] or 0) >= (przed[s] or 0) then wrocil[s] = os.clock() - t0 '
                          'else wszystkie = false end end end if wszystkie then break end task.wait(0.2) end '
                          'return H:JSONEncode({ przed = przed, zaraz = zaraz, wrocil = wrocil })' % strefy_lua)
    except Exception as e:  # noqa: BLE001
        d2["wyjatek"] = str(e)[:300]
    zapisz(litera + "D2", d2)
    wrocil = (d2.get("pomiar") or {}).get("wrocil") or {}
    opisy, dobre = [], True
    for nazwa, s in cele:
        t = wrocil.get(s["id"])
        # pętla odradzania chodzi co 1 s: wpis do kolejki najpóźniej 1 s po zniknięciu, powrót najpóźniej 1 s po czasie
        w_czasie = t is not None and s["odrodzenie"] - 0.5 <= t <= s["odrodzenie"] + 2.6
        dobre = dobre and w_czasie
        opisy.append("%s %s: %s s (ma być %d–%.1f)" % (nazwa, s["id"], "brak" if t is None else "%.1f" % t,
                                                        s["odrodzenie"], s["odrodzenie"] + 2.6))
    punkt(litera + "D2", dobre, "odradzanie: " + "; ".join(opisy))

    stary_test = luau(KA + 'return tostring(k:GetAttribute("TestBohater"))', "Server")
    poziomy = luau(KA + 'return tostring(k:GetAttribute("Stale_POZIOMY_BOHATERA") or "auto,1,5,10")', "Server")
    najnizszy = str(min([int(x) for x in poziomy.replace(" ", "").split(",") if x.isdigit()] or [1]))

    # ------------------------------------------------------------------------------------------ D5 czas pominięcia
    d5 = {"proby": []}
    try:
        luau(KA + 'k:SetAttribute("TestBohater", true) k:SetAttribute("ZiarnoTestowe", nil) return "ok"', "Server")
        time.sleep(0.5)
        bohater("zwiadowca", "auto")
        s0 = zwykle[0]
        for _ in range(3):
            # blokada po poprzedniej walce (najkrótszy pokaz) mogła jeszcze nie minąć, gdy walkę przewinięto
            czekaj_na(lambda: float(luau(KA + 'return tostring((k:GetAttribute("NastepnaWalkaOd") or 0) - workspace:GetServerTimeNow())',
                                         "Client")) <= 0, 15, 0.5)
            cel_p = js('for _, c in k.Stan:GetChildren() do if c:GetAttribute("Strefa") == "%s" and c:GetAttribute("Stan") ~= "zajety" then '
                       'return H:JSONEncode({ id = c.Name }) end end return H:JSONEncode({})' % s0["id"])
            if not cel_p.get("id"):
                time.sleep(2)
                continue
            w = podejdz_i_walcz(cel_p["id"], s0["promien"], przed_e=lambda: luau(REJESTRATOR % kontener, "Client"))
            if not w["walka"]:
                d5["proby"].append({"walka": False, "odmowy": w["odmowy"]})
                continue
            if czekaj_na(lambda: odtw('"stan"').get("pomijanieNaEkranie"), 6, 0.2):
                nacisnij("Space")
            else:
                odtw('"tempo", 4')      # pierwsze spotkanie z gatunkiem: bez pomijania — obejrzeć przy ×4
            pomiar = czekaj_na(lambda: (lambda t: t if t and t != "nil" else None)(
                luau(KA + 'return tostring(k:GetAttribute("PomiarD107"))', "Client")), 70, 0.5)
            odtw('"tempo", 1')
            z = json.loads(pomiar) if pomiar else {}
            d5["proby"].append(z)
            if z.get("przycisk") is not None and z.get("spacja") is not None and z.get("koniec") is not None:
                d5["pomiar"] = z
                break
    except Exception as e:  # noqa: BLE001
        d5["wyjatek"] = str(e)[:300]
    zapisz(litera + "D5", d5)
    z = d5.get("pomiar") or {}
    if z and z.get("E") is not None and z.get("wynik") is not None and z.get("zamknij") is not None:
        do_przycisku = z["przycisk"] - z["E"]
        do_wyniku = z["wynik"] - z["spacja"]
        do_pasa = z["koniec"] - z["zamknij"]
        cykl = do_przycisku + do_wyniku + do_pasa
        d5["cykl_s"] = round(cykl, 2)
        zapisz(litera + "D5", d5)
        punkt(litera + "D5", cykl <= 6.0, "pominięta walka (bez reakcji człowieka): E → przycisk POMIŃ %.2f s, spacja → wynik %.2f s, "
              "zamknięcie → pas %.2f s; razem %.2f s" % (do_przycisku, do_wyniku, do_pasa, cykl))
    else:
        punkt(litera + "D5", False, "nie udało się zmierzyć pominiętej walki: %s" % str(d5)[:300])

    # ------------------------------------------------------------------------------------------ D4 po przegranej
    d4 = {"proby": []}
    try:
        bohater("wojownik", najnizszy)
        js('local cel = %s local t0 = os.clock() while not rowne(cel) and os.clock() - t0 < 45 do task.wait(0.5) end '
           'return H:JSONEncode({ ok = rowne(cel) })' % _tabela({straznik["id"]: 1}))
        id_s = js('for _, c in k.Stan:GetChildren() do if c:GetAttribute("Strefa") == "%s" then return H:JSONEncode({ id = c.Name }) end end '
                  'return H:JSONEncode({})' % straznik["id"]).get("id")
        d4["straznik"] = id_s
        for ziarno in (1, 2, 3):
            if not id_s:
                break
            luau(KA + 'k:SetAttribute("ZiarnoTestowe", %d) return "ok"' % ziarno, "Server")
            czekaj_na(lambda: float(luau(KA + 'return tostring((k:GetAttribute("NastepnaWalkaOd") or 0) - workspace:GetServerTimeNow())',
                                         "Client")) <= 0, 20, 0.5)
            w1 = podejdz_i_walcz(id_s, straznik["promien"])
            w1["ziarno"] = ziarno
            d4["proby"].append(w1)
            if not w1["walka"]:
                continue
            odtw('"tempo", 4')
            t_walki = time.time()
            czekaj_na(lambda: odtw('"stan"').get("faza") in ("wynik", "brak", "koniec"), 120, 0.4)
            w1["pokaz_s"] = round(time.time() - t_walki, 1)
            w1["wynik"] = luau(KA + 'return tostring(k:GetAttribute("OstatniWynik"))', "Client")
            w1["serwer"] = luau(KA + 'return tostring(k:GetAttribute("SerwerOstatniaWalka"))', "Server")
            odtw('"zamknij"')
            czekaj_na(lambda: not klient_potworow().get("walka"), 20, 0.2)
            po = js('local c = k.Stan:FindFirstChild("%s") local p = S:Invoke("potwor", "%s") '
                    'return H:JSONEncode({ jest = c ~= nil, stan = c and c:GetAttribute("Stan") or "", teraz = workspace:GetServerTimeNow(), '
                    'zajetyDo = p and p.zajetyDo or 0 })' % (id_s, id_s))
            wolna = luau(KA + 'return tostring(k:GetAttribute("NastepnaWalkaOd") or 0)', "Client")
            w1["po_zamknieciu"] = po
            w1["blokada_gracza_s"] = round(float(wolna) - po["teraz"], 2)
            if w1["wynik"] != "przegrana":
                # bohater wygrał — strażnik znika; następne ziarno po jego powrocie
                js('local cel = %s local t0 = os.clock() task.wait(2) while not rowne(cel) and os.clock() - t0 < 45 do task.wait(0.5) end '
                   'return H:JSONEncode({ ok = rowne(cel) })' % _tabela({straznik["id"]: 1}))
                id_s = js('for _, c in k.Stan:GetChildren() do if c:GetAttribute("Strefa") == "%s" then return H:JSONEncode({ id = c.Name }) end end '
                          'return H:JSONEncode({})' % straznik["id"]).get("id")
                continue
            d4["pierwsza"] = w1
            if zrzut is not None:
                # zrzut: gracz z powrotem na pasie przy strażniku, który nie jest zajęty (rewanż dostępny)
                p_s = pozycja(id_s)
                if p_s:
                    przestaw(p_s[0] - (straznik["promien"] + 7), p_s[1] + 3.2, p_s[2])
                    time.sleep(1.5)
                    patrz_w_strone(1)
                    time.sleep(1.0)
                    fotka("d107_po_przegranej_rewanz")
            w2 = podejdz_i_walcz(id_s, straznik["promien"])
            d4["rewanz"] = w2
            if w2["walka"]:
                odtw('"tempo", 4')
                czekaj_na(lambda: odtw('"stan"').get("faza") in ("wynik", "brak", "koniec"), 120, 0.4)
            odtw('"tempo", 1')
            odtw('"zamknij"')
            czekaj_na(lambda: not klient_potworow().get("walka"), 20, 0.3)
            break
    except Exception as e:  # noqa: BLE001
        d4["wyjatek"] = str(e)[:300]
    try:
        odtw('"tempo", 1')
        luau(KA + 'k:SetAttribute("ZiarnoTestowe", nil) k:SetAttribute("TestBohater", %s) return "ok"'
             % ("true" if stary_test == "true" else "nil"), "Server")
        bohater("zwiadowca", "auto")
    except Exception:  # noqa: BLE001
        pass
    zapisz(litera + "D4", d4)
    w1, w2 = d4.get("pierwsza") or {}, d4.get("rewanz") or {}
    if "wyjatek" in d4 or not d4["proby"] or not any(p.get("walka") for p in d4["proby"]):
        ok4 = False
    elif not w1:
        ok4 = None      # bohater wygrał we wszystkich próbach — przegranej nie było, punkt do powtórzenia
    else:
        ok4 = (w1.get("blokada_gracza_s", 99) <= 0 and (w1.get("po_zamknieciu") or {}).get("jest") is True
               and (w1.get("po_zamknieciu") or {}).get("stan") != "zajety" and w2.get("walka") is True
               and not w2.get("odmowy") and w2.get("start_po_s", 99) <= 6)
    punkt(litera + "D4", ok4, "przegrana ze strażnikiem obejrzana przy ×4 (pokaz %s s): po zamknięciu blokada gracza %s s, "
          "strażnik „%s”, rewanż ruszył po %s s (odmowy: %s); próby: %s" % (
              w1.get("pokaz_s"), w1.get("blokada_gracza_s"), (w1.get("po_zamknieciu") or {}).get("stan"),
              w2.get("start_po_s"), w2.get("odmowy"), [(p.get("ziarno"), p.get("wynik")) for p in d4["proby"]]))
    return {"D1": d1, "D2": d2, "D3": d3, "D4": d4, "D5": d5}
