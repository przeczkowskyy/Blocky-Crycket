# -*- coding: utf-8 -*-
"""D-107 (walka bez przestojów) — wspólne punkty prób w Play dla lasu, Bagna i Dżungli.

Woła je proba_play.py każdego biomu (ten sam kod potworów, więc te same punkty), podając swoje funkcje pomocnicze:

    D1  liczba potworów: przy 1 graczu każda strefa ma tyle potworów, ile mówi Logika.cel (4 na zwykłą strefę, razem 14);
        po „gracze = 20” strefy dopełniają się do 8 (razem 26) w czasie odrodzenia
    D2  odradzanie w zadanym czasie: zabity zwykły potwór wraca po 4 s, rzadki po 20 s, strażnik po 30 s (± pętla 1 s)
    D3  czas klatki przy pełnym zestawie (gracze = 20) w najgęstszej strefie: klatka klienta (śr., p95), pętla ruchu
        serwera, koszt klienta potworów — porównanie z pomiarem sprzed D-107 robi człowiek (README)
    D4  brak czekania po przegranej: walka przegrana i OBEJRZANA do końca przy tempie ×4 (bez pomijania) — po
        zamknięciu wyniku gracz nie ma blokady („następna za … s”), potwór nie jest zajęty, a rewanż (E przy tym samym
        potworze) rusza od razu

Kody punktów: <litera biomu>D1 … D4 (PD1, BD1, JD1 …). Liczby oczekiwane czyta z danych generatora (nie na sztywno).
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
                       "odrodzenie": s["odrodzenieS"], "x": s["srodek"][0], "z": s["srodek"][2]})
    return {"strefy": strefy, "razem1": sum(s["cel1"] for s in strefy), "razem20": sum(s["cel20"] for s in strefy)}


def _tabela(slownik):
    return "{ " + ", ".join('["%s"] = %s' % (k, v) for k, v in slownik.items()) + " }"


def punkty(litera, kontener, L, luau, punkt, zapisz, przestaw, nacisnij, czekaj_na, klient_potworow, odtw):
    """litera: "P" | "B" | "J"; kontener: nazwa kontenera potworów; L = liczby(); reszta — pomoc proby biomu."""
    K = ('local k = workspace:FindFirstChild("%s") local H = game:GetService("HttpService") '
         'local S = k.Sygnaly.SterowanieSerwera '
         'local function licz() local t = {} for _, c in k.Stan:GetChildren() do local s = c:GetAttribute("Strefa") '
         't[s] = (t[s] or 0) + 1 end return t end '
         'local function rowne(cel) local t = licz() for s, n in cel do if (t[s] or 0) ~= n then return false end end return true end '
         'local function przytnij(cel) for _, c in k.Stan:GetChildren() do local s = c:GetAttribute("Strefa") '
         'local t = licz() if cel[s] and (t[s] or 0) > cel[s] and c:GetAttribute("Stan") ~= "zajety" then S:Invoke("zabij", c.Name) end end end '
         % kontener)

    def js(kod, dm="Server"):
        return json.loads(luau(K + kod, dm))

    cel1 = {s["id"]: s["cel1"] for s in L["strefy"]}
    cel20 = {s["id"]: s["cel20"] for s in L["strefy"]}
    zwykle = [s for s in L["strefy"] if not s["straznik"] and not s["rzadki"]]
    rzadkie = [s for s in L["strefy"] if s["rzadki"]]
    straznik = next(s for s in L["strefy"] if s["straznik"])

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

    # ------------------------------------------------------------------------------------------ D3 czas klatki
    # (przed D2: pełny zestaw jeszcze stoi)
    d3 = {}
    try:
        gesta = zwykle[-1]
        przestaw(gesta["x"], 3.5, gesta["z"])
        time.sleep(5)
        luau(K + 'S:Invoke("koszt", true) return "ok"', "Server")
        luau(K + 'k.Sygnaly.SterowanieKlienta:Invoke("koszt", true) return "ok"', "Client")
        d3["klatki"] = js('local RS = game:GetService("RunService") local t = {} '
                          'local c = RS.RenderStepped:Connect(function(dt) table.insert(t, dt) end) task.wait(8) c:Disconnect() '
                          'table.sort(t) local s = 0 for _, x in t do s += x end '
                          'return H:JSONEncode({ n = #t, sr_ms = s / math.max(1, #t) * 1000, '
                          'p95_ms = (t[math.max(1, math.floor(#t * 0.95))] or 0) * 1000, maks_ms = (t[#t] or 0) * 1000, '
                          'widoki = k:GetAttribute("KlientWidoki") })', "Client")
        d3["serwer"] = js('local w = S:Invoke("koszt") local r = w.ruchu or {} '
                          'return H:JSONEncode({ ruch_sr_ms = r.sr or -1, ruch_maks_ms = r.maks or -1, potworow = k:GetAttribute("Potworow") })')
        d3["klient_potworow"] = luau(K + 'local w = k.Sygnaly.SterowanieKlienta:Invoke("koszt") '
                                         'local ok, tekst = pcall(function() return H:JSONEncode(w) end) '
                                         'return if ok then tekst else "?"', "Client")[:600]
        d3["strefa"] = gesta["id"]
    except Exception as e:  # noqa: BLE001
        d3["wyjatek"] = str(e)[:300]
    zapisz(litera + "D3", d3)
    kl, se = d3.get("klatki") or {}, d3.get("serwer") or {}
    if not kl or not se:
        ok3 = False
    elif kl["sr_ms"] > 25:
        ok3 = None      # okno Studio w tle rysuje 15 kl./s — klatkę ocenia człowiek
    else:
        ok3 = kl["p95_ms"] <= 34 and 0 <= se["ruch_sr_ms"] <= 1.0
    punkt(litera + "D3", ok3, "pełny zestaw (%s potworów) w strefie %s: klatka śr. %.1f ms, p95 %.1f ms, maks. %.1f ms; "
          "pętla ruchu serwera śr. %.2f ms, maks. %.2f ms" % (se.get("potworow"), d3.get("strefa"), kl.get("sr_ms", -1),
                                                             kl.get("p95_ms", -1), kl.get("maks_ms", -1),
                                                             se.get("ruch_sr_ms", -1), se.get("ruch_maks_ms", -1)))
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

    # ------------------------------------------------------------------------------------------ D4 po przegranej
    d4 = {}
    KA = 'local k = workspace:FindFirstChild("%s") ' % kontener
    stary_test = luau(KA + 'return tostring(k:GetAttribute("TestBohater"))', "Server")
    try:
        luau(KA + 'k:SetAttribute("TestBohater", true) k:SetAttribute("ZiarnoTestowe", 1) return "ok"', "Server")
        time.sleep(0.5)
        luau(KA + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("bohater", "wojownik", "1"))', "Client")
        mocna = zwykle[-1]["id"]      # najwyższe poziomy zwykłych potworów biomu — wojownik poz. 1 przegrywa
        potwor = js('local id, poz = nil, -1 for _, c in k.Stan:GetChildren() do '
                    'if c:GetAttribute("Strefa") == "%s" and c:GetAttribute("Stan") ~= "zajety" and (c:GetAttribute("Poziom") or 0) > poz then '
                    'id, poz = c.Name, c:GetAttribute("Poziom") end end return H:JSONEncode({ id = id, poziom = poz })' % mocna)
        d4["potwor"] = potwor

        def podejdz_i_walcz(etykieta):
            w = {"odmowy": []}
            t0 = time.time()
            for _ in range(8):
                p = js('local c = k.Stan:FindFirstChild("%s") local v = c and c:GetAttribute("Pozycja") '
                       'return H:JSONEncode(v and { v.X, v.Y, v.Z } or {})' % potwor["id"])
                if not p:
                    w["brak_potwora"] = True
                    break
                przestaw(p[0] - 5, p[1] + 3.2, p[2])
                time.sleep(0.6)
                kp = klient_potworow()
                if kp.get("podpowiedz") and kp.get("najblizszy") == potwor["id"]:
                    luau(KA + 'k:SetAttribute("OstatniaOdmowa", nil) return "ok"', "Client")
                    nacisnij("E")
                    if czekaj_na(lambda: klient_potworow().get("walka"), 6, 0.3):
                        break
                    w["odmowy"].append(luau(KA + 'return tostring(k:GetAttribute("OstatniaOdmowa"))', "Client"))
            w["walka"] = bool(klient_potworow().get("walka"))
            w["start_po_s"] = round(time.time() - t0, 1)
            d4[etykieta] = w
            return w

        if potwor.get("id"):
            w1 = podejdz_i_walcz("pierwsza")
            if w1["walka"]:
                odtw('"tempo", 4')
                t_walki = time.time()
                czekaj_na(lambda: odtw('"stan"').get("faza") in ("wynik", "brak", "koniec"), 90, 0.5)
                w1["pokaz_s"] = round(time.time() - t_walki, 1)
                w1["wynik"] = luau(KA + 'return tostring(k:GetAttribute("OstatniWynik"))', "Client")
                w1["serwer"] = luau(KA + 'return tostring(k:GetAttribute("SerwerOstatniaWalka"))', "Server")
                odtw('"zamknij"')
                czekaj_na(lambda: not klient_potworow().get("walka"), 20, 0.3)
                po = js('local c = k.Stan:FindFirstChild("%s") local p = S:Invoke("potwor", "%s") '
                        'return H:JSONEncode({ jest = c ~= nil, stan = c and c:GetAttribute("Stan") or "", teraz = workspace:GetServerTimeNow(), '
                        'zajetyDo = p and p.zajetyDo or 0 })' % (potwor["id"], potwor["id"]))
                wolna = luau(KA + 'return tostring(k:GetAttribute("NastepnaWalkaOd") or 0)', "Client")
                w1["po_zamknieciu"] = po
                w1["blokada_gracza_s"] = round(float(wolna) - po["teraz"], 2)
                w1["zajetosc_potwora_s"] = round((po.get("zajetyDo") or 0) - po["teraz"], 2) if po.get("zajetyDo") else 0
                w2 = podejdz_i_walcz("rewanz")
                if w2["walka"]:
                    odtw('"tempo", 4')
                    czekaj_na(lambda: odtw('"stan"').get("faza") in ("wynik", "brak", "koniec"), 90, 0.5)
                odtw('"tempo", 1')
                odtw('"zamknij"')
                czekaj_na(lambda: not klient_potworow().get("walka"), 20, 0.3)
    except Exception as e:  # noqa: BLE001
        d4["wyjatek"] = str(e)[:300]
    try:
        luau(KA + 'k:SetAttribute("ZiarnoTestowe", nil) k:SetAttribute("TestBohater", %s) return "ok"'
             % ("true" if stary_test == "true" else "nil"), "Server")
        luau(KA + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("bohater", "zwiadowca", "auto"))', "Client")
    except Exception:  # noqa: BLE001
        pass
    zapisz(litera + "D4", d4)
    w1, w2 = d4.get("pierwsza") or {}, d4.get("rewanz") or {}
    if not w1.get("walka") or "wyjatek" in d4:
        ok4 = False
    elif w1.get("wynik") != "przegrana":
        ok4 = None      # wojownik poz. 1 wygrał — przegranej nie było, punkt do powtórzenia
    else:
        ok4 = (w1.get("blokada_gracza_s", 99) <= 0 and (w1.get("po_zamknieciu") or {}).get("jest") is True
               and (w1.get("po_zamknieciu") or {}).get("stan") != "zajety" and w2.get("walka") is True
               and not w2.get("odmowy") and w2.get("start_po_s", 99) <= 6)
    punkt(litera + "D4", ok4, "przegrana obejrzana przy ×4 (pokaz %s s): po zamknięciu blokada gracza %s s, potwór „%s”, "
          "rewanż ruszył po %s s (odmowy: %s)" % (w1.get("pokaz_s"), w1.get("blokada_gracza_s"),
                                                 (w1.get("po_zamknieciu") or {}).get("stan"), w2.get("start_po_s"), w2.get("odmowy")))
    return {"D1": d1, "D2": d2, "D3": d3, "D4": d4}
