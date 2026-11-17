# -*- coding: utf-8 -*-
"""Próba „lasu-pasa w grze” w Roblox Studio (tryb Play). Pierwsze przebiegi 17.11.2026 (wyniki w ../wyniki/,
opis w README pakietu); poprawki po nich: ekran wyboru klasy zamykany Enterem przed P03, P08 z TestBezSesji
i ponownym E (potwory chodzą). Uzupełnienie: testy/proba_dodatkowa.py (drogi do lasu, bieg, ściany, wszystkie
gatunki, koszt przy pełnym zestawie).

    python -B swiat/las_pas_gra/testy/proba_play.py <folder wyjściowy> [--studio <studio_id>] [--bez-zrzutow]

Warunki: Studio w trybie Edit, otwarte miejsce gry (placeId sprawdza cel_studio), zbudowane Workspace/LasPas
(swiat/las_pas) i Workspace/LasPasGra (python -B swiat/las_pas_gra/zbuduj.py); najlepiej też TestWalki2, LasTeleport,
LasPotwory i LasMgla (stary las ma dalej działać). Skrypt sam włącza i wyłącza Play (tylko swoje), niczego nie
zapisuje w miejscu i niczego nie publikuje. Wyniki: <wyj>/wyniki.json, lista kontrolna na ekranie i w
<wyj>/lista.txt, zrzuty <wyj>/<nazwa>.jpg (bez filmów). Przy wygaszonym ekranie Studio nie rysuje — skrypt budzi go
przed każdym zrzutem (swiat/test_walki2/testy/czuwanie.py).

LISTA KONTROLNA (każdy punkt kończy się OK / BŁĄD / ? w liście):
  P01 serwery gotowe: SerwerGotowy (potwory pasa), SerwerPasaGotowy, StanMapy ok, StanBiomu ok, SzablonyGotowe,
      Potworow = 20 przy 1 graczu, ZgodnoscLogiki „OK 70/70”, ZgodnoscLogikiPasa „OK 39/39”, Przekierowanie „tak”;
      stary las: LasPotwory SerwerGotowy, Potworow 36
  P02 klienci gotowi: KlientGotowy i KlientTryb „aktorzy” (potwory pasa), KlientPasaGotowy
  P03 przybycie: z miasteczka przez dzisiejszą bramę (LasTeleport.Steruj „las”, przekierowana) → Polana Przybycia
  P04 pierwszy przelot: fazy uspokaja → laduje → trwa → brak, kamera skryptowa, czas lotu 13,4 ± 1 s, ryk Strażnika
      zagrał, postać nie ruszyła się (zakotwiczona), walka w trakcie odrzucona (licznik walk bez zmian), po locie
      kamera Custom, postać i walki odblokowane, WidzialPrzelotLasu = true
  P05 brak drugiego przelotu: miasteczko → brama → las, 6 s — faza „brak”, LicznikPrzelotow bez zmian
  P06 uchwyt „odtwórz ponownie”: przelot jeszcze raz i znów kończy się czysto
  P07 potwory w swoich przegrodach: 40 s próbkowania pozycji wszystkich potworów — 0 poza polem strefy
  P08 walka z każdym gatunkiem (s1 slime, m1 muchomornik, w1 wilk, t1 troll): podpowiedź E przy potworze, prawdziwe E
      zaczyna walkę, po walce kamera i postać wracają do pasa
  P09 odradzanie: zabity slime s2 wraca w 12–16 s
  P10 brama zamknięta: nieuprawniony za bramą → cofnięty przed bramę w < 1 s, komunikat; wrota z kolizją u klienta
  P11 Strażnik: walka (do 6 prób z różnym ziarnem) aż do wygranej → PokonalStraznikaLasu = true; wrota u klienta
      bez kolizji i niewidoczne, NA SERWERZE nadal z kolizją (otwarcie tylko dla zwycięzcy); przejście za bramę bez
      cofnięcia; tabliczka „Bagno — wkrótce”; spadek w pustkę za bramą → ratunek
  P12 Kamień Powrotu: podpowiedź E przy kamieniu, prawdziwe E → miasteczko
  P13 mgła: waga 1 w pasie, 0 w miasteczku; Atmosphere u klienta zmieniona, NA SERWERZE taka jak w miejscu
  P14 koszt: serwer potworów, serwer pasa, klient potworów (ms) i klatki klienta w trzech miejscach pasa
  P15 stary las działa: widoki potworów starego lasu i jego mgła po przeniesieniu do Boru
  P16 konsola: bez błędów [LasPasGra]
  (ręcznie, poza skryptem: telefon w emulatorze Studio — przelot, przycisk E, Kamień Powrotu, panel bohatera;
   dwóch graczy (Test → Clients and Servers, 2) — brama otwarta tylko dla zwycięzcy, drugi cofany)

ZRZUTY (w <wyj>): 01_przybycie, 02_przelot_polana, 03_przelot_zagroda, 04_przelot_lasek, 05_przelot_zarosla,
  06_przelot_leze, 07_przelot_straznik, 08_przelot_ryk, 09_po_przelocie, 10_podpowiedz_slime, 11_walka_slime,
  12_po_walce_w_pasie, 13_brama_zamknieta, 14_komunikat_brama, 15_brama_otwarta, 16_za_brama_tabliczka,
  17_kamien_powrotu, 18_mgla_pas, 19_miasteczko_bez_mgly, 20_stary_las.
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

KP = 'local k = workspace:FindFirstChild("LasPasGra") local H = game:GetService("HttpService") '
# zamiana Vector3 / Color3 / nieskończoności na liczby, żeby JSONEncode nie zawiódł
J = ('local function J(v) local t = typeof(v) if t == "Vector3" then return { v.X, v.Y, v.Z } '
     'elseif t == "table" then local o = {} if #v > 0 then for i, b in ipairs(v) do o[i] = J(b) end '
     'else for a, b in v do o[tostring(a)] = J(b) end end return o '
     'elseif t == "number" and (v ~= v or v == math.huge or v == -math.huge) then return tostring(v) '
     'elseif t == "Instance" then return v:GetFullName() end return v end ')
HRP = 'local hrp = game:GetService("Players"):GetPlayers()[1].Character.HumanoidRootPart '
WYNIKI = {}
LISTA = []


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


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
    try:
        from PIL import Image  # noqa: E402
    except ImportError:
        Image = None

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
            return json.loads(luau(KP + J + kod, dm))

        def stan_studio():
            return call("get_studio_state")["text"]

        def zrzut(nazwa):
            if bez_zrzutow:
                return
            nie_usypiaj()
            r = call("screen_capture", {"capture_id": "laspas_" + nazwa}, timeout=150)
            if r["is_error"] or not r.get("images"):
                log("zrzut %s: BŁĄD %s" % (nazwa, r["text"][:120]))
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
            log("zrzut", nazwa)

        def atrybuty(sciezka, nazwy, dm="Server"):
            return js('local o = {} local f = workspace:FindFirstChild("%s") if not f then return H:JSONEncode({ brak = true }) end '
                      'for _, n in { %s } do o[n] = J(f:GetAttribute(n)) end return H:JSONEncode(o)'
                      % (sciezka, ", ".join('"%s"' % n for n in nazwy)), dm)

        def pasa(polecenie, *argi, dm="Server"):
            hak = "SterowaniePasa" if dm == "Server" else "SterowaniePasaKlienta"
            a = ", ".join("nil" if x is None else json.dumps(x) for x in argi)
            return js('return H:JSONEncode(J(k.Sygnaly.%s:Invoke("%s"%s)))' % (hak, polecenie, (", " + a) if a else ""), dm)

        def gracz_serwer():
            return pasa("gracz")

        def klient_pasa():
            return pasa("stan", dm="Client")

        def klient_potworow():
            return js('return H:JSONEncode(J(k.Sygnaly.SterowanieKlienta:Invoke("stan")))', "Client")

        def odtw(polecenie):
            return js('return H:JSONEncode(J(workspace.TestWalki2.Sygnaly.Sterowanie:Invoke(%s)))' % polecenie, "Client")

        def przestaw(x, y, z, patrz_x=None):
            luau(HRP + 'local p = Vector3.new(%f, %f, %f) hrp.Parent:PivotTo(CFrame.lookAt(p, p + Vector3.new(%s, 0, 0))) '
                       'hrp.AssemblyLinearVelocity = Vector3.zero return "ok"' % (x, y, z, "1" if patrz_x is None else patrz_x),
                 "Server")

        def poz():
            return js(HRP + 'return H:JSONEncode(J(hrp.Position))', "Server")

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

        def czekaj_na_przelot_koniec(limit=30):
            fazy, t_trwa, zrzuty = [], None, []
            plan = [(1.0, "02_przelot_polana"), (3.0, "03_przelot_zagroda"), (5.0, "04_przelot_lasek"),
                    (7.0, "05_przelot_zarosla"), (8.8, "06_przelot_leze"), (10.4, "07_przelot_straznik"),
                    (11.6, "08_przelot_ryk")]
            t0 = time.time()
            while time.time() - t0 < limit:
                g = gracz_serwer()
                if not fazy or fazy[-1][0] != g["faza"]:
                    fazy.append((g["faza"], round(time.time() - t0, 1), g.get("zablokowany"), g.get("blokadaWalki")))
                if g["faza"] == "trwa" and t_trwa is None:
                    t_trwa = time.time()
                if t_trwa is not None and plan and time.time() - t_trwa >= plan[0][0]:
                    zrzut(plan.pop(0)[1])
                    continue
                if g["faza"] == "brak" and len(fazy) > 1:
                    return fazy, (time.time() - t_trwa) if t_trwa else None
                time.sleep(0.3)
            return fazy, None

        nie_usypiaj()
        if "Current Studio Mode: Edit" not in stan_studio():
            sys.exit("Studio nie jest w trybie Edit — ta próba sama włącza Play")
        edit = json.loads(luau('local H = game:GetService("HttpService") local a = game:GetService("Lighting"):FindFirstChildOfClass("Atmosphere") '
                               'local k, m = workspace:FindFirstChild("LasPasGra"), workspace:FindFirstChild("LasPas") '
                               'return H:JSONEncode({ kontener = k ~= nil and k:GetAttribute("Wygenerowane") == true, '
                               'mapa = m ~= nil, gestosc = a and a.Density or -1, stary = workspace:FindFirstChild("LasPotwory") ~= nil })', "Edit"))
        zapisz("edit", edit)
        if not edit["kontener"] or not edit["mapa"]:
            sys.exit("Brak Workspace/LasPasGra albo Workspace/LasPas w trybie Edit: %s" % edit)

        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        try:
            czekaj_na(lambda: "Client" in stan_studio() and luau(
                'local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)', "Client") == "true",
                90, 1.0)
            # ---------------------------------------------------------------- P01–P02 gotowość
            time.sleep(3)
            gotowe = czekaj_na(lambda: (lambda a: a if a.get("SerwerGotowy") and a.get("SerwerPasaGotowy") else None)(
                atrybuty("LasPasGra", ["SerwerGotowy", "SerwerPasaGotowy", "StanMapy", "StanBiomu", "SzablonyGotowe",
                                       "Potworow", "ZgodnoscLogiki", "ZgodnoscLogikiPasa", "Przekierowanie",
                                       "PunktPrzybyciaLasu", "LicznikPrzelotow"])), 60, 1.0) or {}
            stary = atrybuty("LasPotwory", ["SerwerGotowy", "Potworow"])
            zapisz("P01", {"pas": gotowe, "stary": stary})
            punkt("P01", bool(gotowe) and gotowe.get("StanMapy") == "ok" and gotowe.get("StanBiomu") == "ok"
                  and gotowe.get("SzablonyGotowe") is True and gotowe.get("Potworow") == 20
                  and gotowe.get("ZgodnoscLogiki") == "OK 70/70" and gotowe.get("ZgodnoscLogikiPasa") == "OK 39/39"
                  and gotowe.get("Przekierowanie") == "tak" and (stary.get("brak") or stary.get("Potworow") == 36),
                  "serwery: %s | stary las: %s" % (gotowe, stary))
            kl = czekaj_na(lambda: (lambda a: a if a.get("KlientGotowy") and a.get("KlientPasaGotowy") else None)(
                atrybuty("LasPasGra", ["KlientGotowy", "KlientTryb", "KlientPasaGotowy"], "Client")), 60, 1.0) or {}
            zapisz("P02", kl)
            punkt("P02", kl.get("KlientTryb") == "aktorzy" and kl.get("KlientPasaGotowy") is True, "klienci: %s" % kl)
            # ekran wyboru klasy (src/client/ClassSelectClient) trzyma kamerę skryptową w sali klas i wyłącza
            # podpowiedzi E — Enter wybiera klasę jak gracz; bez tego przelot, mgła i E w pasie nie mają sensu
            wybor = {}
            for _ in range(20):
                wybor = js('local p = game:GetService("Players").LocalPlayer local g = p.PlayerGui:FindFirstChild("ClassSelect") '
                           'local c = workspace.CurrentCamera return H:JSONEncode({ ekran = g ~= nil and g.Enabled, kamera = c.CameraType.Name, '
                           'podpowiedzi = game:GetService("ProximityPromptService").Enabled })', "Client")
                if not wybor["ekran"] and wybor["kamera"] == "Custom" and wybor["podpowiedzi"]:
                    break
                nacisnij("Return")
                time.sleep(1.5)
            zapisz("wybor_klasy", wybor)
            log("wybór klasy:", wybor)

            # ---------------------------------------------------------------- P03–P04 przybycie i pierwszy przelot
            luau(HRP + 'local t = workspace:FindFirstChild("LasTeleport") local p = t and t:GetAttribute("PunktMiasteczka") '
                       'if p then hrp.Parent:PivotTo(CFrame.new(p)) end return "ok"', "Server")
            time.sleep(3)
            licznik_walk = atrybuty("LasPasGra", ["SerwerLicznikWalk"]).get("SerwerLicznikWalk") or 0
            wynik_bramy = luau('local t = workspace:FindFirstChild("LasTeleport") local s = t and t:FindFirstChild("Steruj") '
                               'return tostring(s and s:Invoke("las"))', "Server")
            time.sleep(0.4)
            p_przyb = poz()
            cel = gotowe.get("PunktPrzybyciaLasu") or [1114, 3.2, -700]
            d = ((p_przyb[0] - cel[0]) ** 2 + (p_przyb[2] - cel[2]) ** 2) ** 0.5
            zapisz("P03", {"steruj": wynik_bramy, "pozycja": p_przyb, "cel": cel, "odleglosc": d})
            punkt("P03", wynik_bramy == "true" and d < 3, "brama miasteczka → (%.1f; %.1f; %.1f), %.1f st od przybycia" % (
                p_przyb[0], p_przyb[1], p_przyb[2], d))
            zrzut("01_przybycie")
            # próba walki w czasie przelotu (serwer ma odmówić: postać zablokowana)
            czekaj_na(lambda: gracz_serwer()["faza"] in ("laduje", "trwa"), 8, 0.3)
            proba = luau(KP + 'local naj, d = nil, 1e9 local hrp = game:GetService("Players").LocalPlayer.Character.HumanoidRootPart '
                         'for _, c in k.Stan:GetChildren() do local p = c:GetAttribute("Pozycja") if p and (p - hrp.Position).Magnitude < d then '
                         'naj, d = c.Name, (p - hrp.Position).Magnitude end end '
                         'return tostring(naj and k.Sygnaly.SterowanieKlienta:Invoke("walcz", naj))', "Client")
            fazy, czas_lotu = czekaj_na_przelot_koniec()
            time.sleep(1.5)
            zrzut("09_po_przelocie")
            g = gracz_serwer()
            kp = klient_pasa()
            p_po = poz()
            licznik_po = atrybuty("LasPasGra", ["SerwerLicznikWalk", "LicznikPrzelotow"])
            ruch = ((p_po[0] - p_przyb[0]) ** 2 + (p_po[2] - p_przyb[2]) ** 2) ** 0.5
            ost = kp.get("ostatniPrzelot") or {}
            zapisz("P04", {"fazy": fazy, "czas_lotu": czas_lotu, "gracz": g, "klient": kp, "proba_walki": proba,
                           "liczniki": licznik_po, "ruch_postaci": ruch})
            nazwy_faz = [f[0] for f in fazy]
            punkt("P04", "trwa" in nazwy_faz and nazwy_faz[-1] == "brak" and czas_lotu is not None and abs(czas_lotu - 13.9) < 1.5
                  and ost.get("ok") is True and ost.get("ryk") is True and kp.get("kamera") == "Custom"
                  and not g["zablokowany"] and not g["blokadaWalki"] and g["pamiec"]["widzialPrzelotLasu"]
                  and (licznik_po.get("SerwerLicznikWalk") or 0) == licznik_walk and ruch < 1.0,
                  "fazy %s, lot %.1f s, ryk %s, kamera %s, ruch postaci %.2f st, walka w trakcie: %s → licznik walk %s→%s"
                  % (nazwy_faz, czas_lotu or -1, ost.get("ryk"), kp.get("kamera"), ruch, proba, licznik_walk,
                     licznik_po.get("SerwerLicznikWalk")))

            # ---------------------------------------------------------------- P05 brak drugiego przelotu
            przed = licznik_po.get("LicznikPrzelotow")
            pasa("przenies", None, "miasteczko")
            time.sleep(3)
            zrzut("19_miasteczko_bez_mgly")
            waga_miasto = atrybuty("LasPasGra", ["WagaMglyPasa"], "Client").get("WagaMglyPasa")
            luau('return tostring(workspace.LasTeleport.Steruj:Invoke("las"))', "Server")
            fazy2 = []
            for _ in range(12):
                fazy2.append(gracz_serwer()["faza"])
                time.sleep(0.5)
            po = atrybuty("LasPasGra", ["LicznikPrzelotow"]).get("LicznikPrzelotow")
            zapisz("P05", {"fazy": fazy2, "licznik": [przed, po]})
            punkt("P05", set(fazy2) == {"brak"} and po == przed, "po ponownym wejściu fazy %s, przeloty %s→%s" % (set(fazy2), przed, po))

            # ---------------------------------------------------------------- P13 mgła (gracz stoi w pasie)
            time.sleep(2)
            mg = js('local a = game:GetService("Lighting"):FindFirstChildOfClass("Atmosphere") '
                    'return H:JSONEncode({ waga = k:GetAttribute("WagaMglyPasa"), gestosc = a and a.Density or -1 })', "Client")
            mg_s = js('local a = game:GetService("Lighting"):FindFirstChildOfClass("Atmosphere") '
                      'return H:JSONEncode({ gestosc = a and a.Density or -1 })', "Server")
            zrzut("18_mgla_pas")
            zapisz("P13", {"pas": mg, "serwer": mg_s, "miasteczko": waga_miasto, "edit": edit["gestosc"]})
            punkt("P13", mg.get("waga") == 1 and abs(mg.get("gestosc", 0) - 0.36) < 0.01 and waga_miasto == 0
                  and abs(mg_s["gestosc"] - edit["gestosc"]) < 1e-6,
                  "waga w pasie %s (gęstość %.3f), w miasteczku %s; serwer %.3f = Edit %.3f"
                  % (mg.get("waga"), mg.get("gestosc", -1), waga_miasto, mg_s["gestosc"], edit["gestosc"]))

            # ---------------------------------------------------------------- P06 odtwórz ponownie
            pasa("odtworzPrzelot")
            fazy3, czas3 = czekaj_na_przelot_koniec()
            time.sleep(1)
            g3 = gracz_serwer()
            po3 = atrybuty("LasPasGra", ["LicznikPrzelotow"]).get("LicznikPrzelotow")
            zapisz("P06", {"fazy": fazy3, "czas": czas3, "gracz": g3, "licznik": po3})
            punkt("P06", "trwa" in [f[0] for f in fazy3] and po3 == (po or 0) + 1 and not g3["zablokowany"],
                  "ponowny przelot: fazy %s, %s s, licznik %s" % ([f[0] for f in fazy3], czas3 and round(czas3, 1), po3))

            # ---------------------------------------------------------------- P07 potwory w swoich przegrodach
            p07 = js('local D = require(k.Moduly.DanePotworow) local pola = {} for _, st in D.strefy do pola[st.id] = st.pole end '
                     'local probki, poza, przyk = 0, 0, {} for i = 1, 20 do for _, c in k.Stan:GetChildren() do '
                     'local p, sid = c:GetAttribute("Pozycja"), c:GetAttribute("Strefa") local r = pola[sid] if p and r then '
                     'probki += 1 if p.X < r.x1 - 0.5 or p.X > r.x2 + 0.5 or p.Z < r.z1 - 0.5 or p.Z > r.z2 + 0.5 then poza += 1 '
                     'if #przyk < 5 then table.insert(przyk, c.Name) end end end end task.wait(2) end '
                     'return H:JSONEncode({ probki = probki, poza = poza, przyklady = przyk, potworow = #k.Stan:GetChildren() })', "Server")
            zapisz("P07", p07)
            punkt("P07", p07["probki"] > 300 and p07["poza"] == 0, "%d próbek pozycji w 40 s, poza polem strefy: %d %s"
                  % (p07["probki"], p07["poza"], p07["przyklady"]))

            # ---------------------------------------------------------------- P08 walka z każdym gatunkiem
            luau(KP + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("bohater", "zwiadowca", "auto"))', "Client")
            # test przewija walki — bez TestBezSesji serwer (słusznie) nie przyjmie następnej walki przed upływem
            # prawdziwego czasu poprzedniej (odtwarzacz: OstatniaOdmowa = walka_trwa_lokalnie); sprawdzone 17.11.2026
            luau(KP + 'k:SetAttribute("TestBezSesji", true) return "ok"', "Server")
            wyniki_walk = {}
            for nr, sid_strefy in enumerate(("s1", "m1", "w1", "t1")):
                try:
                    cel = js('for _, c in k.Stan:GetChildren() do if c:GetAttribute("Strefa") == "%s" and c:GetAttribute("Stan") ~= "zajety" then '
                             'return H:JSONEncode({ id = c.Name, p = J(c:GetAttribute("Pozycja")) }) end end return H:JSONEncode({})' % sid_strefy, "Server")
                    if not cel:
                        wyniki_walk[sid_strefy] = "brak potwora"
                        continue
                    przed_walka = atrybuty("LasPasGra", ["SerwerLicznikWalk"]).get("SerwerLicznikWalk") or 0
                    widzial_e, odmowy = False, []
                    for proba_e in range(2):  # potwory chodzą: E przy oddalającym się potworze serwer może odrzucić
                        for _ in range(6):
                            p = js('local c = k.Stan:FindFirstChild("%s") return H:JSONEncode(J(c and c:GetAttribute("Pozycja") or Vector3.zero))' % cel["id"], "Server")
                            przestaw(p[0] - 4, p[1] + 3.2, p[2], 1)
                            time.sleep(0.6)
                            kpot = klient_potworow()
                            if kpot.get("podpowiedz") and kpot.get("najblizszy") == cel["id"]:
                                widzial_e = True
                                if nr == 0 and proba_e == 0:
                                    zrzut("10_podpowiedz_slime")
                                luau(KP + 'k:SetAttribute("OstatniaOdmowa", nil) return "ok"', "Client")
                                nacisnij("E")
                                break
                        if czekaj_na(lambda: klient_potworow().get("walka"), 6, 0.5):
                            break
                        odmowy.append(luau(KP + 'return tostring(k:GetAttribute("OstatniaOdmowa"))', "Client"))
                    jak = "E" if not odmowy else "E (za %d. razem; odmowy %s)" % (len(odmowy) + 1, odmowy)
                    if not czekaj_na(lambda: klient_potworow().get("walka"), 1, 0.5):
                        luau(KP + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("walcz", "%s"))' % cel["id"], "Client")
                        jak = "haczyk walcz (E nie zadziałało)"
                    trwa = czekaj_na(lambda: klient_potworow().get("walka"), 10, 0.5)
                    if trwa and nr == 0:
                        time.sleep(4)
                        zrzut("11_walka_slime")
                    if trwa:
                        odtw('"przewinDo", 1000')
                        time.sleep(2.5)
                        odtw('"zamknij"')
                    czekaj_na(lambda: not klient_potworow().get("walka"), 30, 1.0)
                    time.sleep(1.5)
                    pp = poz()
                    kam = js('local c = workspace.CurrentCamera return H:JSONEncode({ typ = c.CameraType.Name })', "Client")
                    po_walce = atrybuty("LasPasGra", ["SerwerLicznikWalk", "SerwerOstatniaWalka"])
                    if nr == 0:
                        zrzut("12_po_walce_w_pasie")
                    w_pasie = 1056 <= pp[0] <= 2076 and -760 <= pp[2] <= -640
                    wyniki_walk[sid_strefy] = {"id": cel["id"], "E": widzial_e, "jak": jak, "walka": bool(trwa), "kamera": kam["typ"],
                                               "w_pasie": w_pasie, "walk": [przed_walka, po_walce.get("SerwerLicznikWalk")],
                                               "ostatnia": po_walce.get("SerwerOstatniaWalka")}
                    time.sleep(1.5)
                except Exception as e:  # noqa: BLE001
                    wyniki_walk[sid_strefy] = "wyjątek: %s" % str(e)[:200]
            luau(KP + 'k:SetAttribute("TestBezSesji", nil) return "ok"', "Server")
            zapisz("P08", wyniki_walk)
            dobre = [k for k, v in wyniki_walk.items() if isinstance(v, dict) and v["E"] and v["walka"] and v["kamera"] == "Custom"
                     and v["jak"].startswith("E")
                     and v["w_pasie"] and (v["walk"][1] or 0) > v["walk"][0]]
            punkt("P08", len(dobre) == 4, "walki z E i powrotem do pasa: %s; szczegóły %s" % (dobre, wyniki_walk))

            # ---------------------------------------------------------------- P09 odradzanie
            p09 = js('local S = k.Sygnaly.SterowanieSerwera local function ile() local n = 0 for _, c in k.Stan:GetChildren() do '
                     'if c:GetAttribute("Strefa") == "s2" then n += 1 end end return n end local przed = ile() local id = nil '
                     'for _, c in k.Stan:GetChildren() do if c:GetAttribute("Strefa") == "s2" then id = c.Name break end end '
                     'S:Invoke("zabij", id) local t0 = os.clock() local po = ile() while ile() < przed and os.clock() - t0 < 25 do task.wait(0.25) end '
                     'return H:JSONEncode({ przed = przed, zaraz = po, wrocil = ile() >= przed, czas = os.clock() - t0 })', "Server")
            zapisz("P09", p09)
            punkt("P09", p09["wrocil"] and 11 <= p09["czas"] <= 17, "slime s2: %d → %d, wrócił po %.1f s" % (p09["przed"], p09["zaraz"], p09["czas"]))

            # ---------------------------------------------------------------- P10 brama zamknięta
            pasa("zamknijBrame")
            time.sleep(0.5)
            cofniecia = atrybuty("LasPasGra", ["LicznikCofniec"]).get("LicznikCofniec") or 0
            pasa("przenies", None, "przed_brama")
            time.sleep(1.5)
            zrzut("13_brama_zamknieta")
            pasa("przenies", None, "za_brama")
            time.sleep(1.0)
            p10 = poz()
            kom = js('local e = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("LasPasGraEkran") '
                     'local l = e and e:FindFirstChild("Komunikat") return H:JSONEncode({ widoczny = l and l.Visible, tekst = l and l.Text })', "Client")
            zrzut("14_komunikat_brama")
            wrota_k = js('local m = workspace:FindFirstChild("LasPas") local w = m and m:FindFirstChild("BramaBagna") w = w and w:FindFirstChild("Wrota") '
                         'local n, kol = 0, 0 if w then for _, d in w:GetDescendants() do if d:IsA("BasePart") then n += 1 if d.CanCollide then kol += 1 end end end end '
                         'return H:JSONEncode({ czesci = n, kolizja = kol })', "Client")
            po_cof = atrybuty("LasPasGra", ["LicznikCofniec"]).get("LicznikCofniec") or 0
            zapisz("P10", {"pozycja": p10, "komunikat": kom, "wrota_klient": wrota_k, "cofniecia": [cofniecia, po_cof]})
            punkt("P10", p10[0] < 2034 and po_cof > cofniecia and kom.get("widoczny") and wrota_k["kolizja"] > 0,
                  "nieuprawniony za bramą → X %.1f (brama 2034), cofnięć %s→%s, komunikat „%s”, wrota u klienta z kolizją: %s"
                  % (p10[0], cofniecia, po_cof, kom.get("tekst"), wrota_k))

            # ---------------------------------------------------------------- P11 Strażnik i brama dla zwycięzcy
            luau(KP + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("bohater", "zwiadowca", "10"))', "Client")
            luau(KP + 'k:SetAttribute("TestBezSesji", true) return "ok"', "Server")
            proby, wygrana = [], False
            for ziarno in (11, 23, 37, 41, 59, 73):
                if wygrana:
                    break
                luau(KP + 'k:SetAttribute("ZiarnoTestowe", %d) return "ok"' % ziarno, "Server")
                sid_str = czekaj_na(lambda: luau(KP + 'for _, c in k.Stan:GetChildren() do if c:GetAttribute("Straznik") == true '
                                                 'and c:GetAttribute("Stan") ~= "zajety" then return c.Name end end return ""', "Server"), 130, 2.0)
                if not sid_str:
                    proby.append((ziarno, "brak Strażnika"))
                    continue
                przestaw(1974 - 9, 3.5, -700, 1)
                time.sleep(1.5)
                luau(KP + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("walcz", "%s"))' % sid_str, "Client")
                if czekaj_na(lambda: klient_potworow().get("walka"), 10, 0.5):
                    odtw('"przewinDo", 1000')
                    time.sleep(2.5)
                    odtw('"zamknij"')
                czekaj_na(lambda: not klient_potworow().get("walka"), 30, 1.0)
                wynik = atrybuty("LasPasGra", ["SerwerOstatniaWalka"]).get("SerwerOstatniaWalka")
                wygrana = gracz_serwer()["pamiec"]["pokonalStraznikaLasu"]
                proby.append((ziarno, wynik))
            luau(KP + 'k:SetAttribute("TestBezSesji", nil) k:SetAttribute("ZiarnoTestowe", nil) return "ok"', "Server")
            jak_otwarta = "wygrana"
            if not wygrana:
                pasa("otworzBrame")
                jak_otwarta = "haczyk otworzBrame (brak wygranej w %d próbach)" % len(proby)
            time.sleep(2)
            wrota_k2 = js('local m = workspace:FindFirstChild("LasPas") local w = m and m:FindFirstChild("BramaBagna") w = w and w:FindFirstChild("Wrota") '
                          'local n, kol, prz = 0, 0, 0 if w then for _, d in w:GetDescendants() do if d:IsA("BasePart") then n += 1 '
                          'if d.CanCollide then kol += 1 end if d.LocalTransparencyModifier > 0.99 then prz += 1 end end end end '
                          'local z = k.Brama.Zapora return H:JSONEncode({ czesci = n, kolizja = kol, niewidoczne = prz, zapora = z.CanCollide })', "Client")
            wrota_s = js('local w = workspace.LasPas.BramaBagna.Wrota local kol = 0 for _, d in w:GetDescendants() do '
                         'if d:IsA("BasePart") and d.CanCollide then kol += 1 end end return H:JSONEncode({ kolizja = kol, zapora = k.Brama.Zapora.CanCollide })', "Server")
            pasa("przenies", None, "przed_brama")
            time.sleep(1.5)
            zrzut("15_brama_otwarta")
            cof = atrybuty("LasPasGra", ["LicznikCofniec"]).get("LicznikCofniec") or 0
            call("character_navigation", {"datamodel_type": "Client", "x": 2048, "y": 3, "z": -700})
            time.sleep(6)
            p11 = poz()
            cof2 = atrybuty("LasPasGra", ["LicznikCofniec"]).get("LicznikCofniec") or 0
            zrzut("16_za_brama_tabliczka")
            ratunki = atrybuty("LasPasGra", ["LicznikRatunkow"]).get("LicznikRatunkow") or 0
            przestaw(2090, -60, -700)
            time.sleep(2)
            p11b = poz()
            ratunki2 = atrybuty("LasPasGra", ["LicznikRatunkow"]).get("LicznikRatunkow") or 0
            zapisz("P11", {"proby": proby, "jak": jak_otwarta, "wrota_klient": wrota_k2, "wrota_serwer": wrota_s,
                           "za_brama": p11, "cofniecia": [cof, cof2], "ratunek": {"pozycja": p11b, "licznik": [ratunki, ratunki2]}})
            punkt("P11", wygrana and wrota_k2["kolizja"] == 0 and wrota_k2["zapora"] is False and wrota_s["kolizja"] > 0
                  and wrota_s["zapora"] is True and p11[0] > 2036 and cof2 == cof and ratunki2 > ratunki and p11b[1] > -5,
                  "%s; wrota klient %s / serwer %s; za bramą X %.1f (cofnięć %s→%s); ratunek → (%.0f; %.1f; %.0f)"
                  % (jak_otwarta, wrota_k2, wrota_s, p11[0], cof, cof2, p11b[0], p11b[1], p11b[2]))

            # ---------------------------------------------------------------- P12 Kamień Powrotu
            kam = js('local p = k.Punkty.KamienPowrotu return H:JSONEncode(J(p.Position))', "Server")
            przestaw(kam[0] + 4, kam[1] + 1, kam[2] + 3, -1)
            time.sleep(1.5)
            pp = js('local p = k.Punkty.KamienPowrotu.PodpowiedzPowrotu return H:JSONEncode({ wlaczona = p.Enabled })', "Client")
            zrzut("17_kamien_powrotu")
            # D-075: z pakietem nowego miasteczka (Workspace/MiasteczkoBazarGra) Kamień prowadzi na start bazaru
            bazar12 = luau('return tostring(workspace:FindFirstChild("MiasteczkoBazarGra") ~= nil)', "Server") == "true"

            def w_miasteczku(p):
                if bazar12:
                    return 882 <= p[0] <= 1066 and -790 <= p[2] <= -610
                return abs(p[0]) < 400 and -900 < p[2] < -600
            nacisnij("E")
            time.sleep(4)
            p12 = poz()
            jak12 = "E"
            if not w_miasteczku(p12):
                pasa("przenies", None, "miasteczko")
                jak12 = "haczyk (E nie przeniosło)"
                time.sleep(2)
                p12 = poz()
            zapisz("P12", {"podpowiedz": pp, "jak": jak12, "pozycja": p12, "cel": "bazar" if bazar12 else "stare"})
            punkt("P12", pp.get("wlaczona") and jak12 == "E" and w_miasteczku(p12), "podpowiedź %s, %s → %s (%.0f; %.0f; %.0f)"
                  % (pp, jak12, "nowe miasteczko" if bazar12 else "stare miasteczko", p12[0], p12[1], p12[2]))

            # ---------------------------------------------------------------- P14 koszt
            koszt = {}
            for nazwa, (x, z) in (("przybycie", (1114, -700)), ("zarosla_w1", (1625, -700)), ("straznik", (1955, -700))):
                przestaw(x, 3.5, z, 1)
                time.sleep(4)
                luau(KP + 'k.Sygnaly.SterowanieSerwera:Invoke("koszt", true) k.Sygnaly.SterowaniePasa:Invoke("koszt", true) return "ok"', "Server")
                luau(KP + 'k.Sygnaly.SterowanieKlienta:Invoke("koszt", true) return "ok"', "Client")
                klatki = js('local RS = game:GetService("RunService") local t = {} local c = RS.RenderStepped:Connect(function(dt) table.insert(t, dt) end) '
                            'task.wait(8) c:Disconnect() table.sort(t) local s = 0 for _, d in t do s += d end '
                            'return H:JSONEncode({ n = #t, sr_ms = s / math.max(1, #t) * 1000, p95_ms = (t[math.max(1, math.floor(#t * 0.95))] or 0) * 1000 })', "Client")
                koszt[nazwa] = {
                    "serwer_potworow": js('return H:JSONEncode(J(k.Sygnaly.SterowanieSerwera:Invoke("koszt")))', "Server"),
                    "serwer_pasa": pasa("koszt"),
                    "klient_potworow": js('return H:JSONEncode(J(k.Sygnaly.SterowanieKlienta:Invoke("koszt")))', "Client"),
                    "klatki": klatki,
                }
            zapisz("P14", koszt)
            punkt("P14", None, "koszt zapisany w wyniki.json (P14) — ocenia człowiek; klatka śr. %s ms"
                  % {k2: round(v["klatki"]["sr_ms"], 1) for k2, v in koszt.items()})

            # ---------------------------------------------------------------- P15 stary las
            if edit["stary"]:
                przestaw(-200, 6, -2400)
                time.sleep(12)
                st = js('local s = workspace.LasPotwory.Sygnaly.SterowanieKlienta:Invoke("stan") local m = workspace:FindFirstChild("LasMgla") '
                        'return H:JSONEncode({ tryb = s.tryb, widoki = s.widoki, mgla = m and m:GetAttribute("WagaMgly") })', "Client")
                zrzut("20_stary_las")
                zapisz("P15", st)
                punkt("P15", st.get("widoki", 0) > 0 and st.get("tryb") == "aktorzy", "stary las: %s" % st)
            else:
                punkt("P15", None, "nie ma Workspace/LasPotwory — pominięte")

            # ---------------------------------------------------------------- P16 konsola
            kons = call("get_console_output", {}, timeout=60)["text"]
            imie = luau('return game:GetService("Players"):GetPlayers()[1].Name', "Server")
            # repo jest publiczne: nazwa konta gracza z konsoli zastąpiona znacznikiem
            linie = [x.strip()[:240].replace(imie, "<gracz>") for x in kons.splitlines() if "LasPasGra" in x or "rror" in x]
            bledy = [x for x in linie if "rror" in x or "błąd" in x.lower()]
            zapisz("P16", linie[-60:])
            punkt("P16", not bledy, "%d wierszy [LasPasGra]/error, w tym błędów: %d %s" % (len(linie), len(bledy), bledy[:3]))
        finally:
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
            for _ in range(60):
                time.sleep(0.5)
                if "Current Studio Mode: Edit" in stan_studio():
                    break
            print("\nLISTA KONTROLNA:")
            for x in LISTA:
                print("  %s %-4s %s" % x)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
