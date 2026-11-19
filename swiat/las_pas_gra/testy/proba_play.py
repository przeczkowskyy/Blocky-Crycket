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
  P04 pierwszy przelot: fazy uspokaja → laduje → trwa → brak, kamera skryptowa, czas lotu z krótkiego planu (D-096) ± 1,5 s, ryk Strażnika
      zagrał, postać nie ruszyła się (zakotwiczona), walka w trakcie odrzucona (licznik walk bez zmian), po locie
      kamera Custom, postać i walki odblokowane, WidzialPrzelotLasu = true
  P05 brak drugiego przelotu: miasteczko → brama → las, 6 s — faza „brak”, LicznikPrzelotow bez zmian
  P05t TELEPORT „Las” z głębi lasu (D-096, „Kliknąć Las jeszcze raz?”): przeniesienie na Polanę Przybycia (inkubator,
      Kamień Powrotu), bez odmowy i bez drugiego przelotu; bez Workspace/TeleportChmury „?”
  P06 uchwyt „odtwórz ponownie”: przelot jeszcze raz i znów kończy się czysto
  P07 potwory w swoich przegrodach: 40 s próbkowania pozycji wszystkich potworów — 0 poza polem strefy
  P08 walka z każdym gatunkiem (s1 slime, m1 muchomornik, w1 wilk, t1 troll): podpowiedź E przy potworze, prawdziwe E
      zaczyna walkę, po walce kamera i postać wracają do pasa
  P08r przegrana i rewanż z pominięciem (17.11.2026): wojownik poz. 1 przeciw wilkowi (gatunek poznany w P08) —
      przegrana, przycisk POMIŃ, spacja → wynik „przegrana”, serwer „ok”, gracz wolny od razu, ten sam wilk żyje i
      nie jest zajęty; rewanż = ponowne E przy TYM SAMYM wilku → walka z POMIŃ, spacja → wynik, znów wolni
  P08j jeden komplet: w pasie widać tylko panel bohatera pasa (LasPasGraBohater), panel starego lasu schowany
  P09 odradzanie: zabity slime s1 wraca po czasie z danych gry (D-107: 4 s, do +3 s na pętlę odradzania; było 12–16 s)
  PD1–PD4 (D-107, walka bez przestojów; wspólne z Bagnem i Dżunglą — pomoc_d107.py): liczba potworów przy 1 i 20
      graczach, odradzanie zwykłego / rzadkiego / Strażnika w zadanym czasie, czas klatki przy pełnym zestawie, brak
      czekania po przegranej obejrzanej przy ×4 i rewanż od razu
  P10 brama zamknięta: nieuprawniony za bramą → cofnięty przed bramę w < 1 s, komunikat; wrota z kolizją u klienta
  P11 Strażnik: walka (do 6 prób z różnym ziarnem) aż do wygranej → PokonalStraznikaLasu = true; wrota u klienta
      bez kolizji i niewidoczne, NA SERWERZE nadal z kolizją (otwarcie tylko dla zwycięzcy); przejście za bramę bez
      cofnięcia; tabliczka „Bagno — wkrótce”; spadek w pustkę za bramą → ratunek. Gdy stoi Bagno (Workspace/BagnoPas
      i BagnoPasGra, swiat/bagno_pas_gra): przed wejściem za bramę wyłączony przelot Bagna (jego haczyk
      „zapomnijPrzelot”), a ratunek za bramą robi serwer Bagna (liczniki obu kontenerów)
  P11n (tylko gdy stoi mapa Bagna) brama prowadzi do Bagna: ZaBrama lasu usunięta, NastepnyBiomJest = true
  P11j jeden baner po wygranej ze Strażnikiem: „STRAŻNIK GAJU POKONANY!” z podpisem o otwartej bramie, bez drugiego
      banera „BRAMA DO BAGNA OTWARTA!” (KlientPasa)
  P12 Kamień Powrotu: podpowiedź E przy kamieniu, prawdziwe E → miasteczko
  P13 mgła: waga 1 w pasie, 0 w miasteczku; Atmosphere u klienta zmieniona, NA SERWERZE taka jak w miejscu
  P14 koszt: serwer potworów, serwer pasa, klient potworów (ms) i klatki klienta w trzech miejscach pasa
  P15 stary las działa: widoki potworów starego lasu i jego mgła po przeniesieniu do Boru; w Borze widać tylko
      panel bohatera starego lasu
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


def _geometria():
    """Położenia i czasy z krótkiej mapy lasu (D-096, swiat/biomy/przycinarka.py) — bez liczb pasa na sztywno."""
    import json

    def wczytaj(sciezka):
        with open(os.path.join(REPO, *sciezka.split("/")), encoding="utf-8") as f:
            return json.load(f)
    zl = wczytaj("swiat/las_pas/krotki/znaczniki.json")
    pl = wczytaj("swiat/las_pas/krotki/plan_pasa.json")
    x0 = float(pl["swiat"]["X0"])

    def m(i):
        return next(x for x in zl["miejsca"] if x["id"] == i)["punkt_swiat"]
    k = pl["przelot_kamery"]
    import importlib.util
    spec = importlib.util.spec_from_file_location("logika_potworow_proby_lasu", os.path.join(REPO, "swiat", "las_potwory", "logika.py"))
    lg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lg)
    return {"brama": m("brama_bagna")[0], "przybycie": m("przybycie")[0], "straznik": x0 + pl["straznik"]["miejsce"][0],
            "potworow_1": sum(lg.cel(s["naraz"], s["max"], 1) for s in pl["strefy"]) + 1,
            "strefy": {s["id"]: x0 + s["srodek"][0] for s in pl["strefy"]},
            "przelot": k["czas_s"], "zatrzymanie": k["zatrzymanie_od_s"]}


G = _geometria()

# 18.11.2026 (swiat/cutscenka_biomu): gdy Workspace/CutscenkaBiomu przejął biom, punkty o przelocie sprawdzają nową
# cutscenkę; bez tego kontenera — stary przelot pasa. Wspólna pomoc: swiat/cutscenka_biomu/pomoc_prob.py
import importlib.util as _ilu  # noqa: E402
_sp = _ilu.spec_from_file_location("cutscenka_pomoc_prob", os.path.join(REPO, "swiat", "cutscenka_biomu", "pomoc_prob.py"))
PP = _ilu.module_from_spec(_sp)
_sp.loader.exec_module(PP)

# D-107 (19.11.2026, walka bez przestojów): liczby potworów i czasy odradzania z DANYCH GRY (generator), nie z planu
# mapy; wspólne punkty prób D1–D4 trzech biomów: swiat/las_pas_gra/testy/pomoc_d107.py
_spd = _ilu.spec_from_file_location("pomoc_d107", os.path.join(REPO, "swiat", "las_pas_gra", "testy", "pomoc_d107.py"))
D107 = _ilu.module_from_spec(_spd)
_spd.loader.exec_module(D107)
G["d107"] = D107.wczytaj_liczby(REPO, "las_pas_gra")
G["potworow_1"] = G["d107"]["razem1"]


def tp(t):
    """Chwila zrzutu z projektu (lot 10,5 s, postój od 10,5) → ta sama chwila krótkiego przelotu."""
    return t * G["zatrzymanie"] / 10.5 if t <= 10.5 else G["zatrzymanie"] + (t - 10.5)
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
            return PP.scal_gracza(luau, "las", pasa("gracz"))

        def klient_pasa():
            return PP.scal_klienta(luau, "las", pasa("stan", dm="Client"))

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
            plan = [(tp(1.0), "02_przelot_polana"), (tp(3.0), "03_przelot_zagroda"), (tp(5.0), "04_przelot_lasek"),
                    (tp(7.0), "05_przelot_zarosla"), (tp(8.8), "06_przelot_leze"), (tp(10.4), "07_przelot_straznik"),
                    (tp(11.6), "08_przelot_ryk")]
            t0 = time.time()
            while time.time() - t0 < limit:
                g = gracz_serwer()
                if not fazy or fazy[-1][0] != g["faza"]:
                    fazy.append((g["faza"], round(time.time() - t0, 1), g.get("zablokowany"), g.get("blokadaWalki")))
                if g["faza"] == "trwa" and t_trwa is None:
                    t_trwa = time.time()
                if plan and PP.pora_na_zrzut(luau, "las", plan, t_trwa, time.time()):
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
            # stan gracza (swiat/stan_gracza, 17.11.2026): próba używa reguły testowej T1 (klasa i poziom z panelu) w obu lasach
            luau('for _, n in { "LasPasGra", "LasPotwory" } do local k = workspace:FindFirstChild(n) '
                 'if k then k:SetAttribute("TestBohater", true) end end return "ok"', "Server")
            time.sleep(3)
            gotowe = czekaj_na(lambda: (lambda a: a if a.get("SerwerGotowy") and a.get("SerwerPasaGotowy") else None)(
                atrybuty("LasPasGra", ["SerwerGotowy", "SerwerPasaGotowy", "StanMapy", "StanBiomu", "SzablonyGotowe",
                                       "Potworow", "ZgodnoscLogiki", "ZgodnoscLogikiPasa", "Przekierowanie",
                                       "PunktPrzybyciaLasu", "LicznikPrzelotow"])), 60, 1.0) or {}
            stary = atrybuty("LasPotwory", ["SerwerGotowy", "Potworow"])
            zapisz("P01", {"pas": gotowe, "stary": stary})
            punkt("P01", bool(gotowe) and gotowe.get("StanMapy") == "ok" and gotowe.get("StanBiomu") == "ok"
                  and gotowe.get("SzablonyGotowe") is True and gotowe.get("Potworow") == G["potworow_1"]
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
            nowa = PP.dopasuj(luau, "las", G)     # nowa cutscenka (CutscenkaBiomu) albo stary przelot pasa
            log("przelot lasu gra: %s" % ("nowa cutscenka (CutscenkaBiomu)" if nowa else "stary przelot pasa"))
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
            licznik_po["LicznikPrzelotow"] = PP.licznik(luau, "las", licznik_po.get("LicznikPrzelotow"))
            ruch = ((p_po[0] - p_przyb[0]) ** 2 + (p_po[2] - p_przyb[2]) ** 2) ** 0.5
            ost = kp.get("ostatniPrzelot") or {}
            zapisz("P04", {"fazy": fazy, "czas_lotu": czas_lotu, "gracz": g, "klient": kp, "proba_walki": proba,
                           "liczniki": licznik_po, "ruch_postaci": ruch})
            nazwy_faz = [f[0] for f in fazy]
            punkt("P04", "trwa" in nazwy_faz and nazwy_faz[-1] == "brak" and czas_lotu is not None and abs(czas_lotu - (G["przelot"] + 0.5)) < 1.5
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
            po = PP.licznik(luau, "las", atrybuty("LasPasGra", ["LicznikPrzelotow"]).get("LicznikPrzelotow"))
            zapisz("P05", {"fazy": fazy2, "licznik": [przed, po]})
            punkt("P05", set(fazy2) == {"brak"} and po == przed, "po ponownym wejściu fazy %s, przeloty %s→%s" % (set(fazy2), przed, po))

            # ---------------------------------------------------------------- P05t TELEPORT „Las”, gdy gracz jest w lesie
            # D-096 (Karol: „Kliknąć Las jeszcze raz?”): wybór krainy, w której gracz już jest, stawia go przy przybyciu
            # (inkubator, Kamień Powrotu) — bez odmowy i bez drugiego przelotu (przelot tylko, gdy go nie widział)
            time.sleep(3.5)                                  # odstęp przeniesień teleportu (3 s) i pasa (2 s)
            przestaw(G["strefy"]["w1"], 3.5, -700, 1)
            time.sleep(1.5)
            z05t = poz()
            przed_t = PP.licznik(luau, "las", atrybuty("LasPasGra", ["LicznikPrzelotow"]).get("LicznikPrzelotow"))
            w05t = js('local g = game:GetService("Players"):GetPlayers()[1] local t = workspace:FindFirstChild("TeleportChmury") '
                      'if not t then return H:JSONEncode({ brak = true }) end '
                      'return H:JSONEncode(J(t.Sygnaly.SterowanieSerwera:Invoke("przenies", "las", g)))', "Server")
            time.sleep(6.0)
            p05t = poz()
            fazy_t = gracz_serwer()["faza"]
            po_t = PP.licznik(luau, "las", atrybuty("LasPasGra", ["LicznikPrzelotow"]).get("LicznikPrzelotow"))
            zapisz("P05t", {"z": z05t, "przenies": w05t, "pozycja": p05t, "faza": fazy_t, "przeloty": [przed_t, po_t]})
            punkt("P05t", None if w05t.get("brak") else (
                      w05t.get("ok") is True and abs(p05t[0] - G["przybycie"]) < 4 and abs(p05t[2] + 700) < 4
                      and fazy_t == "brak" and po_t == przed_t),
                  "z X %.0f wybór Lasu → %s (%.1f; %.1f), faza %s, przeloty %s→%s" % (
                      z05t[0], w05t.get("zrodlo") or w05t.get("powod") or w05t, p05t[0], p05t[2], fazy_t, przed_t, po_t))

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
            if not PP.odtworz(luau, "las"):
                pasa("odtworzPrzelot")
            fazy3, czas3 = czekaj_na_przelot_koniec()
            time.sleep(1)
            g3 = gracz_serwer()
            po3 = PP.licznik(luau, "las", atrybuty("LasPasGra", ["LicznikPrzelotow"]).get("LicznikPrzelotow"))
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
            punkt("P07", p07["probki"] >= 15 * max(1, p07.get("potworow", 0)) and p07["poza"] == 0, "%d próbek pozycji w 40 s, poza polem strefy: %d %s"
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
                    v3 = None
                    if trwa:
                        time.sleep(4 if nr == 0 else 2)
                        if nr == 0:
                            zrzut("11_walka_slime")
                        # dziennik v3 na ekranie (17.11.2026): mana na paskach, pierwsza walka z gatunkiem bez pomijania
                        so = odtw('"stan"')
                        v3 = {"mana": [so.get("manaGracz"), so.get("manaWrog")], "pomijanie": so.get("pomijanie"),
                              "powod": so.get("powodPominiecia"), "przycisk": so.get("pomijanieNaEkranie")}
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
                    w_pasie = 1056 <= pp[0] <= G["brama"] + 42 and -760 <= pp[2] <= -640
                    wyniki_walk[sid_strefy] = {"id": cel["id"], "E": widzial_e, "jak": jak, "walka": bool(trwa), "kamera": kam["typ"],
                                               "w_pasie": w_pasie, "walk": [przed_walka, po_walce.get("SerwerLicznikWalk")],
                                               "ostatnia": po_walce.get("SerwerOstatniaWalka"), "v3": v3,
                                               "kontrola": atrybuty("LasPasGra", ["OstatniaNiezgodnoscMany", "OstatniaNiezgodnoscPaskow",
                                                                                  "OstatnieBledyObslugi"], "Client")}
                    time.sleep(1.5)
                except Exception as e:  # noqa: BLE001
                    wyniki_walk[sid_strefy] = "wyjątek: %s" % str(e)[:200]
            luau(KP + 'k:SetAttribute("TestBezSesji", nil) return "ok"', "Server")
            zapisz("P08", wyniki_walk)
            dobre = [k for k, v in wyniki_walk.items() if isinstance(v, dict) and v["E"] and v["walka"] and v["kamera"] == "Custom"
                     and v["jak"].startswith("E")
                     and v["w_pasie"] and (v["walk"][1] or 0) > v["walk"][0]]
            punkt("P08", len(dobre) == 4, "walki z E i powrotem do pasa: %s; szczegóły %s" % (dobre, wyniki_walk))
            # P08v3 — każda walka pasa odtworzona z dziennika v3: mana na paskach (liczby), pierwsza walka z każdym
            # gatunkiem bez pomijania (pamięć serwera prototypu pusta na starcie Play), kontrola pasków i many = 0
            v3_ok = [k for k, v in wyniki_walk.items() if isinstance(v, dict) and v.get("v3")
                     and all(isinstance(x, (int, float)) for x in v["v3"]["mana"])
                     and v["v3"]["pomijanie"] is False and v["v3"]["powod"] == "pierwsza_walka" and not v["v3"]["przycisk"]
                     and (v["kontrola"].get("OstatniaNiezgodnoscMany") or 0) == 0
                     and (v["kontrola"].get("OstatniaNiezgodnoscPaskow") or 0) == 0
                     and (v["kontrola"].get("OstatnieBledyObslugi") or 0) == 0]
            punkt("P08v3", len(v3_ok) == 4, "dziennik v3 i pierwsze spotkanie bez pomijania: %s" % v3_ok)

            # ---------------------------------------------------------------- P08p pominięcie przy drugim spotkaniu (D-078)
            # bez TestBezSesji: po pominięciu gracz i potwór mają być wolni od razu (Sygnaly/ZwolnijPoPominieciu, opcja A)
            p08p = {}
            try:
                cel = js('for _, c in k.Stan:GetChildren() do local s = c:GetAttribute("Strefa") if (s == "s1" or s == "s2") '
                         'and c:GetAttribute("Stan") ~= "zajety" then return H:JSONEncode({ id = c.Name }) end end return H:JSONEncode({})', "Server")
                p08p["cel"] = cel.get("id")
                if cel.get("id"):
                    for _ in range(6):
                        p = js('local c = k.Stan:FindFirstChild("%s") return H:JSONEncode(J(c and c:GetAttribute("Pozycja") or Vector3.zero))' % cel["id"], "Server")
                        przestaw(p[0] - 4, p[1] + 3.2, p[2], 1)
                        time.sleep(0.6)
                        kpot = klient_potworow()
                        if kpot.get("podpowiedz") and kpot.get("najblizszy") == cel["id"]:
                            nacisnij("E")
                            break
                    if not czekaj_na(lambda: klient_potworow().get("walka"), 6, 0.5):
                        luau(KP + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("walcz", "%s"))' % cel["id"], "Client")
                    p08p["walka"] = bool(czekaj_na(lambda: klient_potworow().get("walka"), 10, 0.5))
                    zgoda = czekaj_na(lambda: odtw('"stan"').get("pomijanie"), 8, 0.5)
                    so = odtw('"stan"')
                    p08p["przed"] = {"pomijanie": so.get("pomijanie"), "przycisk": so.get("pomijanieNaEkranie"),
                                     "powod": so.get("powodPominiecia"), "faza": so.get("faza")}
                    zrzut("11b_druga_walka_pomin")
                    nacisnij("Space")
                    czekaj_na(lambda: odtw('"stan"').get("faza") in ("wynik", "brak", "koniec"), 8, 0.4)
                    time.sleep(1.2)
                    kl = atrybuty("LasPasGra", ["OstatniaOdpowiedzPominiecia", "OstatnioPominieto", "NastepnaWalkaOd"], "Client")
                    teraz_s = float(luau('return tostring(workspace:GetServerTimeNow())', "Server"))
                    potwor = js('local c = k.Stan:FindFirstChild("%s") return H:JSONEncode({ jest = c ~= nil, stan = c and c:GetAttribute("Stan") or "" })'
                                % cel["id"], "Server")
                    p08p["po"] = {"odpowiedz": kl.get("OstatniaOdpowiedzPominiecia"), "pominieto": kl.get("OstatnioPominieto"),
                                  "wolna_za_s": round((kl.get("NastepnaWalkaOd") or 0) - teraz_s, 2), "potwor": potwor,
                                  "zgoda": bool(zgoda)}
                    odtw('"zamknij"')
                    czekaj_na(lambda: not klient_potworow().get("walka"), 20, 0.5)
                    time.sleep(1.0)
                    # od razu następna walka (muchomornik m1) — serwer lasu ma ją przyjąć (gracz wolny)
                    przed_walka = atrybuty("LasPasGra", ["SerwerLicznikWalk"]).get("SerwerLicznikWalk") or 0
                    cel2 = js('for _, c in k.Stan:GetChildren() do if c:GetAttribute("Strefa") == "m1" and c:GetAttribute("Stan") ~= "zajety" then '
                              'return H:JSONEncode({ id = c.Name }) end end return H:JSONEncode({})', "Server")
                    if cel2.get("id"):
                        p = js('local c = k.Stan:FindFirstChild("%s") return H:JSONEncode(J(c and c:GetAttribute("Pozycja") or Vector3.zero))' % cel2["id"], "Server")
                        przestaw(p[0] - 4, p[1] + 3.2, p[2], 1)
                        time.sleep(0.8)
                        luau(KP + 'k:SetAttribute("OstatniaOdmowa", nil) return tostring(k.Sygnaly.SterowanieKlienta:Invoke("walcz", "%s"))'
                             % cel2["id"], "Client")
                        p08p["nastepna"] = bool(czekaj_na(lambda: klient_potworow().get("walka"), 8, 0.5))
                        p08p["odmowa"] = luau(KP + 'return tostring(k:GetAttribute("OstatniaOdmowa"))', "Client")
                        p08p["walk"] = [przed_walka, atrybuty("LasPasGra", ["SerwerLicznikWalk"]).get("SerwerLicznikWalk")]
                        time.sleep(1.0)
                        odtw('"pomin", true')
                        time.sleep(1.0)
                        odtw('"zamknij"')
                        czekaj_na(lambda: not klient_potworow().get("walka"), 20, 0.5)
            except Exception as e:  # noqa: BLE001
                p08p["wyjatek"] = str(e)[:300]
            zapisz("P08p", p08p)
            po = p08p.get("po") or {}
            pot = po.get("potwor") or {}
            punkt("P08p", bool(p08p.get("walka")) and po.get("zgoda") is True and (p08p.get("przed") or {}).get("przycisk") is True
                  and po.get("odpowiedz") == "ok" and po.get("pominieto") is True and po.get("wolna_za_s", 99) <= 0.5
                  and (not pot.get("jest") or pot.get("stan") != "zajety") and p08p.get("nastepna") is True,
                  "druga walka ze slime'em: przycisk POMIŃ, spacja → wynik, serwer ok, gracz i potwór wolni od razu, "
                  "następna walka przyjęta: %s" % p08p)

            # ---------------------------------------------------------------- P08r przegrana i rewanż z pominięciem
            # 17.11.2026 (zadanie „Walka v3, dalej”): po pominięciu PRZEGRANEJ gracz ma być wolny od razu, wilk zostaje
            # (wygrywa) i nie jest zajęty, a rewanż to ponowne E przy tym samym wilku — też z pominięciem
            p08r = {}

            def walka_z_pominieciem(id_potwora, etykieta):
                w = {"id": id_potwora}
                for _ in range(8):  # wilki chodzą: E przy oddalającym się potworze bywa odrzucone
                    p = js('local c = k.Stan:FindFirstChild("%s") return H:JSONEncode(J(c and c:GetAttribute("Pozycja") or Vector3.zero))'
                           % id_potwora, "Server")
                    if p == [0, 0, 0]:
                        w["brak_potwora"] = True  # potwór zniknął (wygrana) — nie przenosimy gracza na środek świata
                        break
                    przestaw(p[0] - 5, p[1] + 3.2, p[2], 1)
                    time.sleep(0.6)
                    kpot = klient_potworow()
                    if kpot.get("podpowiedz") and kpot.get("najblizszy") == id_potwora:
                        w["E"] = True
                        luau(KP + 'k:SetAttribute("OstatniaOdmowa", nil) return "ok"', "Client")
                        nacisnij("E")
                        if czekaj_na(lambda: klient_potworow().get("walka"), 6, 0.4):
                            break
                        w.setdefault("odmowy", []).append(luau(KP + 'return tostring(k:GetAttribute("OstatniaOdmowa"))', "Client"))
                    else:
                        w.setdefault("bez_podpowiedzi", []).append(kpot.get("najblizszy"))
                w["walka"] = bool(czekaj_na(lambda: klient_potworow().get("walka"), 2, 0.4))
                if not w["walka"]:
                    return w
                w["zgoda"] = bool(czekaj_na(lambda: odtw('"stan"').get("pomijanie"), 8, 0.4))
                so = odtw('"stan"')
                w["przycisk"] = so.get("pomijanieNaEkranie")
                w["serwer"] = atrybuty("LasPasGra", ["SerwerOstatniaWalka"]).get("SerwerOstatniaWalka")
                zrzut("11c_%s" % etykieta)
                nacisnij("Space")
                czekaj_na(lambda: odtw('"stan"').get("faza") in ("wynik", "brak", "koniec"), 8, 0.4)
                time.sleep(1.0)
                kl = atrybuty("LasPasGra", ["OstatniaOdpowiedzPominiecia", "OstatnioPominieto", "NastepnaWalkaOd", "OstatniWynik"], "Client")
                teraz_s = float(luau('return tostring(workspace:GetServerTimeNow())', "Server"))
                w["odpowiedz"] = kl.get("OstatniaOdpowiedzPominiecia")
                w["pominieto"] = kl.get("OstatnioPominieto")
                w["wynik"] = kl.get("OstatniWynik")
                w["wolna_za_s"] = round((kl.get("NastepnaWalkaOd") or 0) - teraz_s, 2)
                odtw('"zamknij"')
                czekaj_na(lambda: not klient_potworow().get("walka"), 20, 0.5)
                time.sleep(0.8)
                w["potwor"] = js('local c = k.Stan:FindFirstChild("%s") return H:JSONEncode({ jest = c ~= nil, stan = c and c:GetAttribute("Stan") or "" })'
                                 % id_potwora, "Server")
                w["kamera"] = js('local c = workspace.CurrentCamera return H:JSONEncode({ typ = c.CameraType.Name })', "Client")["typ"]
                return w

            try:
                luau(KP + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("bohater", "wojownik", "1"))', "Client")
                # ziarno 1: Wojownik poz. 1 przegrywa z wilkiem poz. 6 (port silnika: 192 ze 199 ziaren to przegrana,
                # ale bez stałego ziarna raz na ~30 prób wygrywał i wilk znikał — rewanżu nie było)
                luau(KP + 'k:SetAttribute("ZiarnoTestowe", 1) return "ok"', "Server")
                wilk = js('for _, c in k.Stan:GetChildren() do local s = c:GetAttribute("Strefa") if (s == "w2" or s == "w3" or s == "w1") '
                          'and c:GetAttribute("Stan") ~= "zajety" then return H:JSONEncode({ id = c.Name, strefa = s }) end end '
                          'return H:JSONEncode({})', "Server")
                p08r["wilk"] = wilk
                if wilk.get("id"):
                    p08r["pierwsza"] = walka_z_pominieciem(wilk["id"], "przegrana")
                    p08r["rewanz"] = walka_z_pominieciem(wilk["id"], "rewanz")
            except Exception as e:  # noqa: BLE001
                p08r["wyjatek"] = str(e)[:300]
            luau(KP + 'k:SetAttribute("ZiarnoTestowe", nil) return "ok"', "Server")
            luau(KP + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("bohater", "zwiadowca", "auto"))', "Client")
            zapisz("P08r", p08r)

            def dobra_przegrana(w):
                return bool(isinstance(w, dict) and w.get("walka") and w.get("zgoda") and w.get("przycisk") is True
                            and w.get("odpowiedz") == "ok" and w.get("pominieto") is True and w.get("wynik") == "przegrana"
                            and w.get("wolna_za_s", 99) <= 0.5 and (w.get("potwor") or {}).get("jest")
                            and (w.get("potwor") or {}).get("stan") != "zajety" and w.get("kamera") == "Custom")
            punkt("P08r", dobra_przegrana(p08r.get("pierwsza")) and dobra_przegrana(p08r.get("rewanz"))
                  and (p08r.get("rewanz") or {}).get("E") is True,
                  "przegrana z pominięciem i rewanż E przy tym samym wilku: %s" % p08r)

            # ---------------------------------------------------------------- P08j jeden panel bohatera w pasie
            panele = js('local g = game:GetService("Players").LocalPlayer.PlayerGui local function w(n) local s = g:FindFirstChild(n) '
                        'local b = s and s:FindFirstChild("Przycisk") return b ~= nil and s.Enabled and b.Visible end '
                        'return H:JSONEncode({ pas = w("LasPasGraBohater"), stary = w("LasPotworyBohater"), '
                        'starySa = g:FindFirstChild("LasPotworyBohater") ~= nil })', "Client")
            zapisz("P08j", panele)
            punkt("P08j", panele.get("pas") is True and not panele.get("stary"),
                  "w pasie panel bohatera pasa widoczny, starego lasu schowany: %s" % panele)

            # ---------------------------------------------------------------- P09 odradzanie
            p09 = js('local S = k.Sygnaly.SterowanieSerwera local function ile() local n = 0 for _, c in k.Stan:GetChildren() do '
                     'if c:GetAttribute("Strefa") == "s1" then n += 1 end end return n end local przed = ile() local id = nil '
                     'for _, c in k.Stan:GetChildren() do if c:GetAttribute("Strefa") == "s1" then id = c.Name break end end '
                     'S:Invoke("zabij", id) local t0 = os.clock() local po = ile() while ile() < przed and os.clock() - t0 < 25 do task.wait(0.25) end '
                     'return H:JSONEncode({ przed = przed, zaraz = po, wrocil = ile() >= przed, czas = os.clock() - t0 })', "Server")
            zapisz("P09", p09)
            # D-107: czas odrodzenia z danych gry (4 s stałe; pętla odradzania co 1 s → do +3 s zapasu); było 11–17 s
            t09 = next(s["odrodzenie"] for s in G["d107"]["strefy"] if s["id"] == "s1")
            punkt("P09", p09["wrocil"] and t09 - 0.5 <= p09["czas"] <= t09 + 3, "slime s1: %d → %d, wrócił po %.1f s (ma być %d–%d s)" % (
                p09["przed"], p09["zaraz"], p09["czas"], t09, t09 + 3))

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
            punkt("P10", p10[0] < G["brama"] and po_cof > cofniecia and kom.get("widoczny") and wrota_k["kolizja"] > 0,
                  "nieuprawniony za bramą → X %.1f (brama %.0f), cofnięć %s→%s, komunikat „%s”, wrota u klienta z kolizją: %s"
                  % (p10[0], G["brama"], cofniecia, po_cof, kom.get("tekst"), wrota_k))

            # ---------------------------------------------------------------- P11 Strażnik i brama dla zwycięzcy
            luau(KP + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("bohater", "zwiadowca", "10"))', "Client")
            luau(KP + 'k:SetAttribute("TestBezSesji", true) return "ok"', "Server")
            proby, wygrana, banery = [], False, {}
            for ziarno in (11, 23, 37, 41, 59, 73):
                if wygrana:
                    break
                luau(KP + 'k:SetAttribute("ZiarnoTestowe", %d) return "ok"' % ziarno, "Server")
                sid_str = czekaj_na(lambda: luau(KP + 'for _, c in k.Stan:GetChildren() do if c:GetAttribute("Straznik") == true '
                                                 'and c:GetAttribute("Stan") ~= "zajety" then return c.Name end end return ""', "Server"), 130, 2.0)
                if not sid_str:
                    proby.append((ziarno, "brak Strażnika"))
                    continue
                przestaw(G["straznik"] - 9, 3.5, -700, 1)
                time.sleep(1.5)
                luau(KP + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("walcz", "%s"))' % sid_str, "Client")
                if czekaj_na(lambda: klient_potworow().get("walka"), 10, 0.5):
                    # przewijać można dopiero odtwarzanie (w czasie prośby do serwera przewinięcie nic nie robi, a „zamknij”
                    # kończyło walkę przed wynikiem — klient nie widział wygranej, P11j)
                    czekaj_na(lambda: odtw('"stan"').get("faza") == "odtwarzanie", 10, 0.3)
                    odtw('"przewinDo", 1000')
                    time.sleep(2.5)
                    odtw('"zamknij"')
                    # P11j: banery od razu po zamknięciu walki — przez 10 s co 0,25 s (baner klienta potworów żyje 5 s,
                    # zapasowy baner KlientPasa pokazałby się po 8 s bez walki)
                    banery = js('local g = game:GetService("Players").LocalPlayer.PlayerGui local wid, maks, podpisy = {}, 0, {} '
                                'local t0 = os.clock() while os.clock() - t0 < 10 do local n = 0 '
                                'local b1 = g:FindFirstChild("LasPasGraBaner") if b1 then n += 1 wid.potworow = true '
                                'local p = b1:FindFirstChild("Podpis", true) if p then podpisy[p.Text] = true end end '
                                'local e = g:FindFirstChild("LasPasGraEkran") if e and e:FindFirstChild("Baner") then n += 1 wid.pasa = true end '
                                'maks = math.max(maks, n) task.wait(0.25) end '
                                'local l = {} for k2 in podpisy do table.insert(l, k2) end '
                                'return H:JSONEncode({ potworow = wid.potworow == true, pasa = wid.pasa == true, maksNaraz = maks, podpisy = l, '
                                'zuzyty = k:GetAttribute("BanerStraznikaZPodpisem") })', "Client")
                czekaj_na(lambda: not klient_potworow().get("walka"), 30, 1.0)
                wynik = atrybuty("LasPasGra", ["SerwerOstatniaWalka"]).get("SerwerOstatniaWalka")
                wygrana = gracz_serwer()["pamiec"]["pokonalStraznikaLasu"]
                proby.append((ziarno, wynik))
            luau(KP + 'k:SetAttribute("TestBezSesji", nil) k:SetAttribute("ZiarnoTestowe", nil) return "ok"', "Server")
            # P11j — jeden baner po wygranej (pomiar z ostatniej, wygranej próby — w pętli wyżej)
            zapisz("P11j", banery)
            punkt("P11j", None if not wygrana else (banery.get("potworow") is True and banery.get("pasa") is False
                  and banery.get("maksNaraz") == 1 and any("Brama do Bagna" in x for x in banery.get("podpisy") or [])),
                  "po wygranej ze Strażnikiem jeden baner z podpisem o bramie: %s" % banery)
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
            # Bagno za bramą (swiat/bagno_pas_gra): bez przelotu Bagna w tej próbie (sprawdza go próba Bagna)
            PP.oznacz(luau, ["bagno"])            # to samo dla nowej cutscenki Bagna
            bagno = js('local b = workspace:FindFirstChild("BagnoPasGra") local m = workspace:FindFirstChild("BagnoPas") '
                       'if b and b:FindFirstChild("Sygnaly") then b.Sygnaly.SterowaniePasa:Invoke("zapomnijPrzelot") end '
                       'return H:JSONEncode({ gra = b ~= nil, mapa = m ~= nil and m:GetAttribute("Wygenerowane") == true, '
                       'nastepny = k:GetAttribute("NastepnyBiomJest") == true, zaBrama = k:FindFirstChild("ZaBrama") ~= nil })', "Server")
            zapisz("P11n", bagno)
            if bagno.get("mapa"):
                punkt("P11n", bagno.get("nastepny") is True and bagno.get("zaBrama") is False,
                      "stoi mapa Bagna: NastepnyBiomJest %s, ZaBrama lasu %s" % (bagno.get("nastepny"),
                                                                               "jest" if bagno.get("zaBrama") else "usunięta"))
            pasa("przenies", None, "przed_brama")
            time.sleep(1.5)
            zrzut("15_brama_otwarta")
            cof = atrybuty("LasPasGra", ["LicznikCofniec"]).get("LicznikCofniec") or 0
            call("character_navigation", {"datamodel_type": "Client", "x": G["brama"] + 14, "y": 3, "z": -700})
            time.sleep(6)
            p11 = poz()
            cof2 = atrybuty("LasPasGra", ["LicznikCofniec"]).get("LicznikCofniec") or 0
            zrzut("16_za_brama_tabliczka")
            def licz_ratunki():
                # za bramą lasu przy stojącym Bagnie ratuje serwer Bagna (jedno pilnowanie) — sumujemy oba kontenery
                n = atrybuty("LasPasGra", ["LicznikRatunkow"]).get("LicznikRatunkow") or 0
                if bagno.get("gra"):
                    n += atrybuty("BagnoPasGra", ["LicznikRatunkow"]).get("LicznikRatunkow") or 0
                return n
            ratunki = licz_ratunki()
            przestaw(G["brama"] + 56, -60, -700)
            time.sleep(2)
            p11b = poz()
            ratunki2 = licz_ratunki()
            zapisz("P11", {"proby": proby, "jak": jak_otwarta, "wrota_klient": wrota_k2, "wrota_serwer": wrota_s,
                           "za_brama": p11, "cofniecia": [cof, cof2], "ratunek": {"pozycja": p11b, "licznik": [ratunki, ratunki2]}})
            punkt("P11", wygrana and wrota_k2["kolizja"] == 0 and wrota_k2["zapora"] is False and wrota_s["kolizja"] > 0
                  and wrota_s["zapora"] is True and p11[0] > G["brama"] + 2 and cof2 == cof and ratunki2 > ratunki and p11b[1] > -5,
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
            jak12 = "E"
            for proba12 in range(3):
                # przy kamieniu bywa slime z podpowiedzią „Walcz” na tym samym klawiszu — wtedy inne miejsce przy kamieniu
                if proba12:
                    przestaw(kam[0] + (4, -4, 3)[proba12], kam[1] + 1, kam[2] + (3, 3, -4)[proba12], -1)
                    time.sleep(1.5)
                    jak12 = "E (za %d. razem)" % (proba12 + 1)
                nacisnij("E")
                time.sleep(4)
                p12 = poz()
                if w_miasteczku(p12):
                    break
                if klient_potworow().get("walka"):
                    odtw('"zamknij"')
                    czekaj_na(lambda: not klient_potworow().get("walka"), 20, 0.5)
            if not w_miasteczku(p12):
                pasa("przenies", None, "miasteczko")
                jak12 = "haczyk (E nie przeniosło)"
                time.sleep(2)
                p12 = poz()
            zapisz("P12", {"podpowiedz": pp, "jak": jak12, "pozycja": p12, "cel": "bazar" if bazar12 else "stare"})
            punkt("P12", pp.get("wlaczona") and jak12.startswith("E") and w_miasteczku(p12), "podpowiedź %s, %s → %s (%.0f; %.0f; %.0f)"
                  % (pp, jak12, "nowe miasteczko" if bazar12 else "stare miasteczko", p12[0], p12[1], p12[2]))

            # ---------------------------------------------------------------- P14 koszt
            koszt = {}
            for nazwa, (x, z) in (("przybycie", (G["przybycie"], -700)), ("zarosla_w1", (G["strefy"]["w1"], -700)),
                                  ("straznik", (G["straznik"] - 19, -700))):
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
                # narzędzie zrzutu ekranu w Play zostawia kamerę skryptową (17.11.2026: P15 — kamera „Scriptable” gdzie
                # indziej, więc stary las nie budował widoków i mgła 0; to nie gra) — kamera postaci jak u gracza
                kamera_przed = js('return H:JSONEncode({ t = workspace.CurrentCamera.CameraType.Name })', "Client").get("t")
                luau('local p = game:GetService("Players").LocalPlayer task.delay(0.1, function() local c = workspace.CurrentCamera '
                     'c.CameraType = Enum.CameraType.Custom local h = p.Character and p.Character:FindFirstChildOfClass("Humanoid") '
                     'if h then c.CameraSubject = h end end) return "ok"', "Client")
                time.sleep(4)
                czekaj_na(lambda: js('local s = workspace.LasPotwory.Sygnaly.SterowanieKlienta:Invoke("stan") '
                                     'return H:JSONEncode({ w = s.widoki })', "Client").get("w", 0) > 0, 25, 1.0)
                st = js('local s = workspace.LasPotwory.Sygnaly.SterowanieKlienta:Invoke("stan") local m = workspace:FindFirstChild("LasMgla") '
                        'local g = game:GetService("Players").LocalPlayer.PlayerGui local function w(n) local s2 = g:FindFirstChild(n) '
                        'local b = s2 and s2:FindFirstChild("Przycisk") return b ~= nil and s2.Enabled and b.Visible end '
                        'return H:JSONEncode({ tryb = s.tryb, widoki = s.widoki, mgla = m and m:GetAttribute("WagaMgly"), '
                        'panelStary = w("LasPotworyBohater"), panelPasa = w("LasPasGraBohater") })', "Client")
                zrzut("20_stary_las")
                # diagnoza (17.11.2026): stary las nie buduje widoków, gdy odtwarzacz prototypu ma otwartą sesję walki
                st["odtwarzacz"] = odtw('"stan"').get("faza")
                st["kamera"] = js('return H:JSONEncode({ t = workspace.CurrentCamera.CameraType.Name })', "Client").get("t")
                st["kamera_przed"] = kamera_przed
                zapisz("P15", st)
                punkt("P15", st.get("widoki", 0) > 0 and st.get("tryb") == "aktorzy" and st.get("panelStary") is True
                      and not st.get("panelPasa"), "stary las: %s" % st)
            else:
                punkt("P15", None, "nie ma Workspace/LasPotwory — pominięte")

            # D-107 (walka bez przestojów): PD1 liczba potworów (1 i 20 graczy), PD2 odradzanie w zadanym czasie,
            # PD3 czas klatki przy pełnym zestawie, PD4 brak czekania po przegranej obejrzanej przy ×4 i rewanż od razu
            D107.punkty("P", "LasPasGra", G["d107"], luau, punkt, zapisz, przestaw, nacisnij, czekaj_na, klient_potworow, odtw)

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
