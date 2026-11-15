# -*- coding: utf-8 -*-
"""Kontrola Play z listy PROJEKT.md rozdz. 9.2 (punkty, których pierwsza próba nie sprawdziła) i klatki do filmu.

Uzycie: python -B swiat/las_potwory/testy/kontrola_play.py <folder wyjsciowy>

Jedna sesja Play: las i podpowiedź E, walka ze slime'em aż do ZAMKNIJ i odrodzenie, Strażnik Gaju (haczyk „zabij”)
z odliczaniem 120 s, w tym czasie skalowanie haczykiem „gracze” (8, 20, 1), koszt w Ostępach, walka z wilkiem
i z Muchomornikiem, pomiar panelu bohatera pod telefon. Wyniki idą do <wyj>/wyniki.json, klatki do <wyj>/film/,
a krótki wpis po każdym kroku do swiat/las_potwory/klatki/kontrola_postep.txt. Skrypt sam zatrzymuje Play, które
sam zaczął; gdy Studio jest w Play kogoś innego, czeka na tryb Edit (do 60 minut).
"""
import io
import json
import os
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TU)))
WYJ = sys.argv[1]
FILM = os.path.join(WYJ, "film")
POSTEP = os.path.join(os.path.dirname(TU), "klatki", "kontrola_postep.txt")
sys.path.insert(0, os.path.join(REPO, "tools"))
sys.path.insert(0, os.path.join(REPO, "swiat", "test_walki2", "testy"))
from studio_mcp import StudioMCP, StudioError, first_studio_id  # noqa: E402
from czuwanie import nie_usypiaj  # noqa: E402
from PIL import Image  # noqa: E402

os.makedirs(FILM, exist_ok=True)
K = 'local k = workspace:FindFirstChild("LasPotwory") local H = game:GetService("HttpService") '
HRP = 'local hrp = game:GetService("Players"):GetPlayers()[1].Character.HumanoidRootPart '
WYNIKI = {}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def postep(tekst):
    with open(POSTEP, "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (time.strftime("%H:%M"), tekst))
    log("POSTEP:", tekst)


def zapisz(klucz, wartosc):
    WYNIKI[klucz] = wartosc
    with open(os.path.join(WYJ, "wyniki.json"), "w", encoding="utf-8") as f:
        json.dump(WYNIKI, f, ensure_ascii=False, indent=1)


def main():
    with StudioMCP(timeout=180) as s:
        s.studios(wait=15)
        sid = first_studio_id(s)
        licznik = [0]

        def call(n, a=None, timeout=None):
            d = dict(a or {})
            d["studio_id"] = sid
            return s.call(n, d, timeout=timeout)

        def luau(kod, dm, proby=3):
            for i in range(proby):
                try:
                    r = call("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=120)
                    if r["is_error"]:
                        raise StudioError(r["text"][:600])
                    return r["text"].strip()
                except Exception as e:  # noqa: BLE001 — Studio czasem nie odpowiada 2–3 minuty
                    if i == proby - 1:
                        raise
                    log("luau: ponawiam po bledzie:", str(e)[:200])
                    time.sleep(30)

        def js(kod, dm):
            return json.loads(luau(kod, dm))

        def stan_studio():
            return call("get_studio_state")["text"]

        def zrzut(nazwa=None, kamera=None, patrz=None, film=True):
            """Zrzut ekranu; do filmu (kolejny numer) i/lub pod nazwą do raportu."""
            nie_usypiaj()
            args = {"capture_id": "lask_%d" % licznik[0]}
            if kamera is not None:
                args["camera_position"] = list(kamera)
                args["look_at_position"] = list(patrz)
            r = call("screen_capture", args, timeout=150)
            if r["is_error"] or not r["images"]:
                log("zrzut: BLAD", r["text"][:120])
                return None
            im = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
            if im.width > 1280:
                im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
            if film:
                im.save(os.path.join(FILM, "k_%04d.jpg" % licznik[0]), "JPEG", quality=88)
                licznik[0] += 1
            if nazwa:
                im.save(os.path.join(WYJ, nazwa + ".jpg"), "JPEG", quality=85)
            return im

        def seria(ile, odstep, **kw):
            """Zrzuty w stałym odstępie (ile klatek co `odstep` sekund)."""
            for _ in range(ile):
                t = time.time()
                zrzut(**kw)
                time.sleep(max(0.0, odstep - (time.time() - t)))

        def przestaw(x, y, z):
            luau(HRP + 'hrp.Parent:PivotTo(CFrame.new(%f, %f, %f)) return "ok"' % (x, y, z), "Server")

        def klient():
            return js(K + 'return H:JSONEncode(k.Sygnaly.SterowanieKlienta:Invoke("stan"))', "Client")

        def odtw(polecenie):
            return js('local s = workspace.TestWalki2.Sygnaly.Sterowanie '
                      'return game:GetService("HttpService"):JSONEncode(s:Invoke(%s))' % polecenie, "Client")

        def strefy():
            return js(K + 'local o = {} for id, s in k.Sygnaly.SterowanieSerwera:Invoke("strefy") do '
                      'o[id] = { s.cel, s.istnieje, #s.kolejka, if s.minLuka == math.huge then -1 '
                      'else math.floor(s.minLuka * 10) / 10 } end '
                      'return H:JSONEncode({ s = o, P = k:GetAttribute("Potworow"), G = k:GetAttribute("Graczy") })',
                      "Server")

        def najblizszy(przedrostek):
            """Najbliższy postaci wolny potwór, którego id zaczyna się od przedrostka (widok serwera)."""
            return js(K + HRP + 'local naj, d = nil, 1e9 for _, c in k.Stan:GetChildren() do '
                      'if c.Name:sub(1, %d) == "%s" then local o = k.Sygnaly.SterowanieSerwera:Invoke("potwor", c.Name) '
                      'if o and o.stan ~= "zajety" and o.stan ~= "wychodzi" then local dd = (o.pozycja - hrp.Position).Magnitude '
                      'if dd < d then naj, d = o, dd end end end end '
                      'if not naj then return "null" end '
                      'return H:JSONEncode({ id = naj.id, stan = naj.stan, poziom = naj.poziom, x = naj.pozycja.X, '
                      'y = naj.pozycja.Y, z = naj.pozycja.Z, d = math.floor(d) })' % (len(przedrostek), przedrostek),
                      "Server")

        def walcz(przedrostek, klasa, poziom, proby=5):
            luau(K + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("bohater", "%s", "%s"))' % (klasa, poziom), "Client")
            for i in range(proby):
                m = najblizszy(przedrostek)
                if not m:
                    time.sleep(2)
                    continue
                przestaw(m["x"] + 1.5, m["y"] + 3.2, m["z"] + 1.5)
                ok = luau(K + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("walcz", "%s"))' % m["id"], "Client")
                time.sleep(2.5)
                if klient().get("walka"):
                    log("walka z %s (poz. %s) w probie %d, walcz=%s" % (m["id"], m["poziom"], i, ok))
                    return m
            return None

        def zamknij_okno():
            """ZAMKNIJ w oknie wyniku kliknięciem myszy (jak test prototypu); haczyk „zamknij” tylko awaryjnie."""
            sc = luau('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("TestWalki2Cutscenka") '
                      'local b = g and g:FindFirstChild("Zamknij", true) local p = b and b:FindFirstChild("Przycisk") '
                      'return p and p:GetFullName() or "brak"', "Client")
            jak = "brak przycisku"
            if sc != "brak" and ".PlayerGui." in sc:
                sciezka = "LocalPlayer.PlayerGui." + sc.split(".PlayerGui.", 1)[1]
                call("user_mouse_input", {"datamodel_type": "Client", "actions": [
                    {"action": "moveTo", "instance_path": sciezka}, {"action": "mouseButtonClick", "mouse_button": "left"}]})
                jak = "klik"
                time.sleep(2.5)
            if klient().get("walka"):
                odtw('"zamknij"')
                jak += " + haczyk zamknij"
                time.sleep(2.5)
            return jak

        def po_walce():
            """Kamera, sterowanie i miejsce postaci po zamknięciu okna."""
            st = js(HRP + 'local c = workspace.CurrentCamera local h = hrp.Parent:FindFirstChildOfClass("Humanoid") '
                    'return game:GetService("HttpService"):JSONEncode({ typ = c.CameraType.Name, '
                    'podmiot = c.CameraSubject == h, x = hrp.Position.X, y = hrp.Position.Y, z = hrp.Position.Z, '
                    'odKamery = math.floor((c.CFrame.Position - hrp.Position).Magnitude) })',
                    "Client")
            p1 = st
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": [
                {"action": "keyDown", "key_code": "W"}, {"action": "wait", "wait_time_ms": 900},
                {"action": "keyUp", "key_code": "W"}]})
            time.sleep(0.4)
            p2 = js(HRP + 'return game:GetService("HttpService"):JSONEncode({ x = hrp.Position.X, z = hrp.Position.Z })',
                    "Client")
            st["krokW"] = round(((p2["x"] - p1["x"]) ** 2 + (p2["z"] - p1["z"]) ** 2) ** 0.5, 1)
            return st

        def widoki_strefy(przedrostek):
            """Widoki klienta w strefie: spód modelu, grunt pod nim (promień w BiomLas) i liczba części."""
            return js(K + 'local rp = RaycastParams.new() rp.FilterType = Enum.RaycastFilterType.Include '
                      'rp.FilterDescendantsInstances = { workspace.BiomLas } local o = {} '
                      'for _, m in k.Widoki:GetChildren() do if m:IsA("Model") and m.Name:sub(1, %d) == "%s" then '
                      'local cf, sz = m:GetBoundingBox() local dol = cf.Position.Y - sz.Y / 2 '
                      'local r = workspace:Raycast(Vector3.new(cf.Position.X, dol + 4, cf.Position.Z), Vector3.new(0, -40, 0), rp) '
                      'o[m.Name] = { math.floor(dol * 100) / 100, if r then math.floor(r.Position.Y * 100) / 100 else "brak", '
                      '#m:GetDescendants() } end end return H:JSONEncode(o)' % (len(przedrostek), przedrostek), "Client")

        def walka_do_konca(film_klatek=0, nazwa_wyniku=None):
            """Przewija walkę: z klatkami do filmu (1 s czasu walki na klatkę) albo od razu na koniec."""
            st = odtw('"stan"')
            log("odtwarzacz:", {k2: st.get(k2) for k2 in ("faza", "czas", "t") if k2 in st})
            for _ in range(film_klatek):
                st = odtw('"przewin", 1.0')
                time.sleep(0.1)
                if st.get("kamera"):
                    zrzut(kamera=st["kamera"], patrz=st["patrz"])
                else:
                    zrzut()
                if st.get("faza") != "odtwarzanie":
                    break
            st = odtw('"przewinDo", 1000')
            time.sleep(2.0)
            im = zrzut(nazwa=nazwa_wyniku, kamera=st.get("kamera"), patrz=st.get("patrz")) if st.get("kamera") \
                else zrzut(nazwa=nazwa_wyniku)
            if im is not None and film_klatek:
                for _ in range(3):  # okno wyniku zostaje w filmie dłużej
                    im.save(os.path.join(FILM, "k_%04d.jpg" % licznik[0]), "JPEG", quality=88)
                    licznik[0] += 1
            return st

        # ------------------------------------------------------------------ start
        nie_usypiaj()
        t_czek = time.time()
        while "Current Studio Mode: Edit" not in stan_studio():
            if time.time() - t_czek > 3600:
                sys.exit("Studio nie wróciło do trybu Edit w 60 minut")
            time.sleep(10)
        zapisz("czekanie_na_edit_s", round(time.time() - t_czek))
        log("Play:", call("start_stop_play", {"is_start": True})["text"][:40])
        try:
            for _ in range(160):
                if "Client" in stan_studio():
                    try:
                        if luau('local p = game:GetService("Players").LocalPlayer '
                                'return tostring(p ~= nil and p.Character ~= nil)', "Client", proby=1) == "true":
                            break
                    except Exception:  # noqa: BLE001
                        pass
                time.sleep(0.5)
            time.sleep(4)
            p1 = js(K + 'return H:JSONEncode({ k:GetAttribute("SerwerGotowy"), k:GetAttribute("StanBiomu"), '
                    'k:GetAttribute("Potworow"), k:GetAttribute("Graczy"), k:GetAttribute("ZgodnoscLogiki"), #k.Stan:GetChildren() })',
                    "Server")
            zapisz("P1", p1)
            log("P1:", p1)
            # dziennik zdarzeń Stan po stronie serwera (czas serwera): dokładny czas odrodzenia niezależnie od tego,
            # ile trwają zrzuty; atrybut istnieje tylko w tej sesji Play i znika po jej zatrzymaniu
            luau(K + 'k:SetAttribute("TestDziennik", "") '
                 'k.Stan.ChildRemoved:Connect(function(c) k:SetAttribute("TestDziennik", k:GetAttribute("TestDziennik") .. '
                 'string.format("-%s@%.2f;", c.Name, workspace:GetServerTimeNow())) end) '
                 'k.Stan.ChildAdded:Connect(function(c) k:SetAttribute("TestDziennik", k:GetAttribute("TestDziennik") .. '
                 'string.format("+%s@%.2f;", c.Name, workspace:GetServerTimeNow())) end) return "ok"', "Server")

            # ------------------------------------------------ las z01: slime'y idą, podpowiedź E
            przestaw(-215, 8, -2300)
            time.sleep(12)
            zapisz("z01_klient", {k2: v for k2, v in klient().items() if k2 != "bohater"})
            seria(10, 1.5)
            for _ in range(3):
                m = najblizszy("z01-")
                przestaw(m["x"] + 3, m["y"] + 3.2, m["z"] + 3)
                time.sleep(0.6)
                k1 = klient()
                if k1.get("podpowiedz"):
                    zrzut(nazwa="kontrola_1_podpowiedz")
                    zapisz("podpowiedz", {"id": m["id"], "najblizszy": k1.get("najblizszy")})
                    break
            postep("las z01: %s widokow, %s animowanych, podpowiedz E %s" % (
                WYNIKI["z01_klient"].get("widoki"), WYNIKI["z01_klient"].get("animowane"), "jest" if "podpowiedz" in WYNIKI else "nie zlapana"))

            # ------------------------------------------------ 1. walka ze slime'em, ZAMKNIJ, odrodzenie
            m = walcz("z01-", "wojownik", "10")
            if not m:
                zapisz("krok1", "walka nie ruszyla")
                postep("krok 1: walka ze slime'em nie ruszyla")
            else:
                serwer = js(K + 'local o = k.Sygnaly.SterowanieSerwera:Invoke("potwor", "%s") return H:JSONEncode({ '
                            'stan = o.stan, wynik = o.wynik, zajetyDo = o.zajetyDo, teraz = workspace:GetServerTimeNow() })' % m["id"],
                            "Server")
                time.sleep(3)
                walka_do_konca(film_klatek=16, nazwa_wyniku="kontrola_2_wynik")
                jak = zamknij_okno()
                time.sleep(1)
                pw = po_walce()
                widok = luau(K + 'return tostring(k.Widoki:FindFirstChild("%s") ~= nil)' % m["id"], "Client")
                seria(5, 1.5)
                # odrodzenie: kiedy Configuration znika i kiedy pojawia się nowy slime w z01
                stare = set(js(K + 'local o = {} for _, c in k.Stan:GetChildren() do if c.Name:sub(1, 4) == "z01-" then '
                               'table.insert(o, c.Name) end end return H:JSONEncode(o)', "Server"))
                t_usun, t_nowy, nowy = None, None, None
                t0 = time.time()
                while time.time() - t0 < 90:
                    teraz = set(js(K + 'local o = {} for _, c in k.Stan:GetChildren() do if c.Name:sub(1, 4) == "z01-" then '
                                   'table.insert(o, c.Name) end end return H:JSONEncode(o)', "Server"))
                    if t_usun is None and m["id"] not in teraz:
                        t_usun = time.time()
                    nowe = teraz - stare
                    if nowe:
                        nowy = sorted(nowe)[0]
                        t_nowy = time.time()
                        break
                    time.sleep(0.5)
                droga = None
                if nowy:
                    a = js(K + 'local o = k.Sygnaly.SterowanieSerwera:Invoke("potwor", "%s") return H:JSONEncode({ '
                           's = o.stan, x = o.pozycja.X, z = o.pozycja.Z })' % nowy, "Server")
                    # kamera na nowego slime'a przy domu (w Play narzędzie przyjmuje własną kamerę)
                    for i in range(6):
                        b = js(K + 'local o = k.Sygnaly.SterowanieSerwera:Invoke("potwor", "%s") return H:JSONEncode({ '
                               's = o.stan, x = o.pozycja.X, y = o.pozycja.Y, z = o.pozycja.Z })' % nowy, "Server")
                        zrzut(kamera=[b["x"] + 14, b["y"] + 9, b["z"] + 14], patrz=[b["x"], b["y"] + 1, b["z"]],
                              nazwa="kontrola_3_nowy_slime" if i == 2 else None)
                        time.sleep(0.8)
                    time.sleep(4)
                    b = js(K + 'local o = k.Sygnaly.SterowanieSerwera:Invoke("potwor", "%s") return H:JSONEncode({ '
                           's = o.stan, x = o.pozycja.X, z = o.pozycja.Z })' % nowy, "Server")
                    droga = {"start": a, "po": b}
                wynik1 = {"potwor": m, "serwer_przy_starcie": serwer, "zamkniecie": jak, "po_walce": pw,
                          "widok_po_zamknieciu": widok,
                          "usuniety_po_s_od_zamkniecia": round(t_usun - t0, 1) if t_usun else None,
                          # uwaga: liczone od pierwszego odczytu po zrzutach, więc zaniżone; dokładny czas daje „dziennik”
                          "nowy": nowy, "odrodzenie_s_przyblizone": round(t_nowy - t_usun, 1) if (t_nowy and t_usun) else None,
                          "nowy_ruch": droga}
                zapisz("krok1", wynik1)
                postep("krok 1: walka %s %s, okno: %s, kamera %s, krok W %s st, nowy %s (przyblizenie %s s, dokladnie w dzienniku)" % (
                    m["id"], serwer.get("wynik"), jak, pw.get("typ"), pw.get("krokW"), nowy, wynik1["odrodzenie_s_przyblizone"]))

            # ------------------------------------------------ 2. Strażnik Gaju i 3. skalowanie w czasie czekania
            przestaw(5, 36, -1634)
            time.sleep(8)
            sid_s = luau(K + 'for _, c in k.Stan:GetChildren() do if c:GetAttribute("Gatunek") == "straznik_lasu" then '
                         'return c.Name end end return ""', "Server")
            t_zab = None
            if sid_s:
                luau(K + 'return tostring(k.Sygnaly.SterowanieSerwera:Invoke("zabij", "%s"))' % sid_s, "Server")
                t_zab = time.time()
                wraca = js(K + 'return H:JSONEncode({ w = k:GetAttribute("StraznikWraca") or 0, t = workspace:GetServerTimeNow() })',
                           "Server")
            else:
                wraca = None
            skal = {"start": strefy()}
            luau(K + 'return tostring(k.Sygnaly.SterowanieSerwera:Invoke("gracze", 8))', "Server")
            time.sleep(40)
            skal["8"] = strefy()
            luau(K + 'return tostring(k.Sygnaly.SterowanieSerwera:Invoke("gracze", 20))', "Server")
            time.sleep(45)
            skal["20"] = strefy()
            t_wrot = None
            while t_zab and time.time() - t_zab < 200:
                if luau(K + 'for _, c in k.Stan:GetChildren() do if c:GetAttribute("Gatunek") == "straznik_lasu" then '
                        'return c.Name end end return ""', "Server"):
                    t_wrot = time.time()
                    break
                time.sleep(1)
            time.sleep(4)
            ks = klient()
            straz_widok = luau(K + 'local n = 0 for _, m in k.Widoki:GetChildren() do if m:IsA("Model") then '
                               'local c = k.Stan:FindFirstChild(m.Name) if c and c:GetAttribute("Gatunek") == "straznik_lasu" '
                               'then n += 1 end end end return tostring(n)', "Client")
            zrzut(nazwa="kontrola_4_straznik_wrocil", film=False)
            zapisz("krok2", {"id": sid_s, "wraca": wraca, "powrot_s": round(t_wrot - t_zab, 1) if t_wrot else None,
                             "klient": {"podpowiedz": ks.get("podpowiedz"), "najblizszy": ks.get("najblizszy")},
                             "widok": straz_widok})
            postep("krok 2: Straznik %s wrocil po %s s (postac obok), podpowiedz %s, widok %s" % (
                sid_s, WYNIKI["krok2"]["powrot_s"], ks.get("podpowiedz"), straz_widok))
            luau(K + 'return tostring(k.Sygnaly.SterowanieSerwera:Invoke("gracze", 1))', "Server")
            time.sleep(10)
            skal["1_po_20"] = strefy()
            zapisz("krok3", skal)
            postep("krok 3: Potworow start %s, 8 graczy %s, 20 graczy %s, z powrotem 1 %s" % (
                skal["start"]["P"], skal["8"]["P"], skal["20"]["P"], skal["1_po_20"]["P"]))

            # ------------------------------------------------ 6. koszt i 4. wilki w Ostępach (przy 87 potworach)
            przestaw(325, 8, -1895)
            time.sleep(14)
            luau(K + 'k.Sygnaly.SterowanieKlienta:Invoke("koszt", true) return "ok"', "Client")
            luau(K + 'k.Sygnaly.SterowanieSerwera:Invoke("koszt", true) return "ok"', "Server")
            time.sleep(20)
            kk = js(K + 'return H:JSONEncode(k.Sygnaly.SterowanieKlienta:Invoke("koszt"))', "Client")
            ksrv = js(K + 'return H:JSONEncode(k.Sygnaly.SterowanieSerwera:Invoke("koszt"))', "Server")
            kst = klient()
            wilki = widoki_strefy("z08-")
            wilki.update(widoki_strefy("z07-"))
            m2 = najblizszy("z08-")
            if m2:  # kamera z boku: kamera postaci w Ostępach bywa w krzakach
                zrzut(nazwa="kontrola_5_wilki", film=False, kamera=[m2["x"] + 16, m2["y"] + 9, m2["z"] + 16],
                      patrz=[m2["x"], m2["y"] + 2, m2["z"]])
            zapisz("krok6", {"klient": kk, "serwer": ksrv, "stan": {k2: kst.get(k2) for k2 in
                                                                  ("widoki", "animowane", "czesciWidokow", "ukryte", "bledy")}})
            zapisz("krok4_wilki_widoki", wilki)
            postep("krok 6: koszt w Ostepach zapisany (widoki %s, czesci %s)" % (kst.get("widoki"), kst.get("czesciWidokow")))
            m = walcz("z08-", "wojownik", "10")
            wynik4 = {"wilk": m["id"] if m else None}
            if m:
                time.sleep(3)
                walka_do_konca(nazwa_wyniku=None)
                wynik4["wilk_zamkniecie"] = zamknij_okno()
            # Muchomornik z04
            m04 = najblizszy("z04-")
            if m04:
                przestaw(m04["x"] + 10, m04["y"] + 4, m04["z"] + 10)
                time.sleep(12)
                wynik4["muchomorniki_widoki"] = widoki_strefy("z04-")
                wynik4["klient_z04"] = {k2: klient().get(k2) for k2 in ("widoki", "animowane", "bledy")}
                zrzut(nazwa="kontrola_6_muchomornik", film=False)
                m = walcz("z04-", "wojownik", "10")
                wynik4["muchomornik"] = m["id"] if m else None
                if m:
                    time.sleep(3)
                    walka_do_konca()
                    wynik4["muchomornik_zamkniecie"] = zamknij_okno()
            zapisz("krok4", wynik4)
            postep("krok 4: wilk %s, muchomornik %s, widokow wilkow %d, muchomornikow %d" % (
                wynik4.get("wilk"), wynik4.get("muchomornik"), len(wilki), len(wynik4.get("muchomorniki_widoki") or {})))

            # ------------------------------------------------ 5. telefon: panel bohatera i napisy w punktach
            m = najblizszy("z01-")
            przestaw(-215, 8, -2300)
            time.sleep(8)
            sc = luau('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("LasPotworyBohater") '
                      'return g and "ok" or "brak"', "Client")
            if sc == "ok":
                call("user_mouse_input", {"datamodel_type": "Client", "actions": [
                    {"action": "moveTo", "instance_path": "LocalPlayer.PlayerGui.LasPotworyBohater.Przycisk"},
                    {"action": "mouseButtonClick", "mouse_button": "left"}]})
                time.sleep(1.5)
            tel = js('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("LasPotworyBohater") '
                     'local o = { vp = { workspace.CurrentCamera.ViewportSize.X, workspace.CurrentCamera.ViewportSize.Y }, napisy = {} } '
                     'if g then local okno = g:FindFirstChild("Okno") o.okno = okno and { okno.Visible, okno.AbsoluteSize.X, okno.AbsoluteSize.Y } '
                     'for _, t in g:GetDescendants() do if (t:IsA("TextLabel") or t:IsA("TextButton")) and t.Text ~= "" then '
                     'table.insert(o.napisy, { t.Name, math.floor(t.TextBounds.Y * 10) / 10, t.AbsoluteSize.X, t.AbsoluteSize.Y }) end end end '
                     'return game:GetService("HttpService"):JSONEncode(o)', "Client")
            zrzut(nazwa="kontrola_7_panel_bohatera", film=False)
            zapisz("krok5", tel)
            postep("krok 5: panel bohatera %s, najmniejszy napis %s pkt" % (
                tel.get("okno"), min([n[1] for n in tel.get("napisy") or [[0, 0]]])))
            try:
                call("user_mouse_input", {"datamodel_type": "Client", "actions": [
                    {"action": "moveTo", "instance_path": "LocalPlayer.PlayerGui.LasPotworyBohater.Okno.Gotowe"},
                    {"action": "mouseButtonClick", "mouse_button": "left"}]})
            except Exception:  # noqa: BLE001
                pass

            luau(K + 'return tostring(k.Sygnaly.SterowanieSerwera:Invoke("gracze", nil))', "Server")
            zapisz("dziennik", luau(K + 'return k:GetAttribute("TestDziennik")', "Server"))
            kons = call("get_console_output", {}, timeout=60)["text"]
            linie = [x.strip()[:220] for x in kons.splitlines()
                     if "LasPotwory" in x or "rror" in x or "TestWalki2" in x]
            zapisz("konsola", linie[-30:])
        finally:
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:40])
            for _ in range(60):
                time.sleep(0.5)
                if "Current Studio Mode: Edit" in stan_studio():
                    break
            zapisz("edit_na_koncu", "Current Studio Mode: Edit" in stan_studio())
            postep("sesja Play zakonczona, Studio w Edit: %s" % WYNIKI.get("edit_na_koncu"))


main()
