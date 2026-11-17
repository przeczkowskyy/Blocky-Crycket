#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba w trybie PLAY odtwarzacza pod dziennik v3 i pomijania walk (D-078) — DLA NASTĘPNEGO ETAPU (sam wraca do Edit).

    python -B swiat/test_walki2/testy/test_v3_play.py                  # wszystko → testy/wynik_v3.json + klatki/v3_*.jpg
    python -B swiat/test_walki2/testy/test_v3_play.py --tylko pomijanie,mana
    python -B swiat/test_walki2/testy/test_v3_play.py --bez-zrzutow --bez-mostka --studio <id>

Przygotowane bez Studio 17.11.2026 i NIEURUCHOMIONE (praca offline). Przed uruchomieniem: kontener przebudowany
(`python -B swiat/test_walki2/zbuduj.py`), Studio w trybie Edit, ziarna z `testy/ziarna.json` („v3”, liczy
`test_odtwarzacza.py --ziarna`). Wymaga serwera MCP Studio (jak inne *_play.py).

LISTA KONTROLNA (części, --tylko):
  pomijanie  D-078 — PIERWSZA część (pamięć serwera jest pusta tylko na starcie sesji Play):
             P1  pierwsza walka z Leśnym Slime'em: brak przycisku POMIŃ, w jego miejscu „PIERWSZE SPOTKANIE…”,
                 zgoda serwera = false (atrybut OstatniPowodPominiecia = pierwsza_walka);
             P2  spacja nic nie pomija (OstatnieOdrzuconePominiecia ≥ 1, walka trwa); haczyk "pomin" bez wymuszenia też nie;
             P3  próba oszukania z klienta: Zdalne/PominiecieWalki2:InvokeServer("pomin", "TestWalki2") → ok = false,
                 powod = pierwsza_walka; złe argumenty → zly_wybor; licznik SerwerPominieciaOdrzucone rośnie;
             P4  wymuszony pokaz bez zgody (haczyk "pomin", true): panel wyniku, ale serwer odmawia — JESZCZE RAZ
                 zablokowane z odliczaniem (sesja serwera trwa);
             P5  po końcu pierwszej walki gatunek poznany (atrybut gracza PoznaneGatunki); druga walka: przycisk POMIŃ
                 widoczny, klik → wynik od razu, serwer „ok”, JESZCZE RAZ od razu dostępne (gracz wolny);
             P6  trzecia walka (JESZCZE RAZ): spacja pomija, serwer „ok”;
             P7  inny gatunek (Cierniowy Wilk) — znów bez przycisku;
             P8  mostek lasu-pasa (gdy jest Workspace/LasPasGra z Sygnaly/WynikWalki; --bez-mostka pomija): sztuczny
                 sygnał WynikWalki (gatunek lesny_slime, straznik = false — SerwerPasa go ignoruje) → "czy" LasPasGra = ok
                 (pamięć wspólna z tablicą), "pomin" → ok i powod = sesja_zrodla (las bez Sygnaly/ZwolnijPoPominieciu);
                 dla nieznanego gatunku → pierwsza_walka; stary las LasPotwory → brak_walki.
  mana       pasek many na ekranie = dziennik zdarzenie po zdarzeniu (po każdym zdarzeniu obu stron; przy użyciu
             umiejętności spadek o koszt od początku zdarzenia), gotowość i próg = plan z dziennika; walki: wzorcowa
             i pod manę (pierwsza akcja = umiejętność), atrybut OstatniaNiezgodnoscMany = 0.
  statusy    każdy status z wyglądem i licznikiem: trucizna ×N (znaczek i napis), podpalenie dłuższe (Ognista różdżka:
             licznik tur z dziennika), krwawienie, spowolnienie (lód, BEZ „TRACI TURĘ!”), ogłuszenie (gwiazdki przy
             trollu i Miażdżącym ciosie, pnącza przy Uścisku korzeni, „TRACI TURĘ!” w turze celu), zdarcie pancerza,
             wzmocnienie (Skupienie), tarcza −N% na 3 tury (Kamienna skóra, Bariera; bez „zapasu”, „TARCZA −n”).
  blok       blok każdej klasy i każdego potwora: napis „BLOK −75%” (z czesc_przez_blok) i liczba tego, co przeszło;
             Wojownik — iskry przy tarczy, bez łuku parady; pozostali — łuk parady (części „Parada”); zablokowana
             umiejętność bez efektu.
  wskrzeszenie  gracza, przeciwnika (lustro) i obu: światło (części „Swiatlo”), napis „WSKRZESZENIE!”, pasek życia
             z 0 do życia z dziennika, pióro legendy szare po użyciu, walka trwa dalej; OstatnieWskrzeszenia = „g/w”.
  pasywki    zapowiedź na starcie (zestaw „pasywki”, każda klasa, poziom 10): karteczki PasywkaGracza z nazwami
             i premiami z danych, OstatniePasywki = sloty + broń; pióro legendy przy zestawie „wskrzeszenie”.
  telefon    emulacja 844 × 390 i 667 × 375: panel wyboru (z rzędem ZESTAW i LUSTREM) i walka z maną, znaczkami,
             karteczką pasywki i informacją o pomijaniu — każdy napis ≥ 12 pkt (pomiar jak testy/telefon.py).
  koszt      koszt klienta w pełnych walkach ×1 (wskrzeszenie obu, pasywki, długa walka): średni / p95 / maks. czas
             skryptu na klatkę, p95 klatki, liczba instancji; progi orientacyjne: skrypt śr. < 2 ms, p95 < 4 ms.
  konsola    bez ostrzeżeń i błędów z [TestWalki2] (w tym „Dziennik: …” z normalizacji — w v3 ich nie ma).

ZRZUTY (bez filmów; klatki/v3_<nazwa>.jpg, --bez-zrzutow pomija): pomijanie_pierwsza (bez przycisku),
pomijanie_druga (z przyciskiem), mana_gotowa (pasek świeci), mana_uzycie (błysk i spadek), trucizna_stosy,
ogluszenie_gwiazdki, ogluszenie_pnacza, traci_ture, spowolnienie_lod, tarcza_procent, blok_<klasa/potwór> (8),
wskrzeszenie_gracza, wskrzeszenie_przeciwnika, wskrzeszenie_obu, pasywki_<klasa> (3), telefon_v3_<rozmiar>_{panel,walka}.
"""
import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
KATALOG = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(KATALOG))
for _s in (TU, KATALOG, os.path.join(REPO, "tools", "walka")):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import silnik as S  # noqa: E402
import zestawy as ZE  # noqa: E402
from sesja_play import SesjaPlay, log  # noqa: E402

WYNIKI = []
POMIARY = []
GUI = "TestWalki2Cutscenka."
ZRZUTY = True


def wynik(nazwa, ok, opis=""):
    WYNIKI.append({"test": nazwa, "ok": bool(ok), "opis": opis})
    log("%s %s %s" % ("OK  " if ok else "BŁĄD", nazwa, opis))


def ziarna():
    with open(os.path.join(TU, "ziarna.json"), encoding="utf-8") as f:
        return json.load(f)["v3"]


def dziennik(o):
    return S.symuluj(ZE.postac(o["zestaw"], o["klasa"], o["poziom"]),
                     ZE.przeciwnik(o["zestaw"], o["klasa"], o["przeciwnik"], o["poziom"]), o["ziarno"])


def start(s, o, opcje="{ reczny = true }", czekaj=15):
    s.steruj('"zamknij"')
    time.sleep(0.8)
    s.ziarno(o["ziarno"])
    s.steruj('"start", { klasa = "%s", przeciwnik = "%s", poziom = "%d", zestaw = "%s" }, %s'
             % (o["klasa"], o["przeciwnik"], o["poziom"], o["zestaw"], opcje))
    st, _ = s.czekaj(("odtwarzanie",), czekaj)
    return st.get("OstatniStan") == "odtwarzanie"


def przewin(s, tau):
    return json.loads(s.steruj('"przewinDo", %f' % max(0.0, tau)))


def napisy(s):
    d = json.loads(s.steruj('"napisy"'))
    return [n["tekst"] for n in (d.get("napisy") or []) + (d.get("czekajace") or [])]


def czesci_sceny(s, nazwy):
    """Ile części o tych nazwach jest teraz w ScenaLokalna (ozdoby efektów, parada, światło wskrzeszenia)."""
    kod = ('local k = workspace.TestWalki2:FindFirstChild("ScenaLokalna") local t = {} for _, n in { %s } do t[n] = 0 end '
           'if k then for _, d in k:GetDescendants() do if t[d.Name] ~= nil and d:IsA("BasePart") then t[d.Name] += 1 end end end '
           'return game:GetService("HttpService"):JSONEncode(t)' % ", ".join('"%s"' % n for n in nazwy))
    return json.loads(s.luau(kod))


def gui_widoczny(s, sciezka):
    kod = ('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("TestWalki2Cutscenka") '
           'local o = g and g:FindFirstChild("%s", true) if not o then return "brak" end '
           'local p = o while p and p ~= g do if p:IsA("GuiObject") and not p.Visible then return "ukryty" end p = p.Parent end '
           'return "widoczny"' % sciezka)
    return s.luau(kod).strip()


def zrzut(s, nazwa):
    if not ZRZUTY:
        return
    try:
        im, _ = s.zrzut_odtwarzacza()
        os.makedirs(os.path.join(KATALOG, "klatki"), exist_ok=True)
        im.save(os.path.join(KATALOG, "klatki", "v3_%s.jpg" % nazwa), quality=88)
    except Exception as e:  # noqa: BLE001
        log("  zrzut %s się nie udał: %s" % (nazwa, e))


def zdalna_pominiecia(s, *argi):
    a = ", ".join(json.dumps(x) if isinstance(x, str) else str(x) for x in argi)
    return json.loads(s.luau('local r = workspace.TestWalki2.Zdalne.PominiecieWalki2:InvokeServer(%s) '
                             'return game:GetService("HttpService"):JSONEncode(r)' % a))


# --------------------------------------------------------------------------- części
def test_pomijanie(s, Z, mostek):
    s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", nil) return "ok"', "Server")
    s.przy_tablicy()
    o = dict(Z["pomijanie"])                       # Leśny Slime, wzorcowa, krótka walka
    if not start(s, o, "{ tempo = 1 }"):
        wynik("P0. walka ze Slime'em wystartowała", False)
        return
    time.sleep(1.0)
    st = s.stan()
    od = st.get("_odtw") or {}
    wynik("P1. pierwsza walka z gatunkiem: bez przycisku POMIŃ, zgoda serwera = false",
          od.get("pomijanie") is False and od.get("pomijanieNaEkranie") is False and st.get("OstatniPowodPominiecia") == "pierwsza_walka"
          and gui_widoczny(s, "PominInfo") == "widoczny", "(%s, %s)" % (od.get("powodPominiecia"), gui_widoczny(s, "PominInfo")))
    zrzut(s, "pomijanie_pierwsza")
    s.klawisz("Space")
    time.sleep(0.4)
    s.steruj('"pomin"')
    time.sleep(0.3)
    st = s.stan()
    wynik("P2. spacja i haczyk bez wymuszenia nic nie pomijają", st.get("OstatniStan") == "odtwarzanie"
          and (st.get("OstatnieOdrzuconePominiecia") or 0) >= 2, "(%s)" % st.get("OstatnieOdrzuconePominiecia"))
    przed = s.luau('return tostring(workspace.TestWalki2:GetAttribute("SerwerPominieciaOdrzucone") or 0)', "Server").strip()
    r1 = zdalna_pominiecia(s, "pomin", "TestWalki2")
    time.sleep(0.25)                                 # serwer: najwyżej jedno wywołanie na 0,2 s
    r2 = zdalna_pominiecia(s, "pomin", "CudzyKontener")
    time.sleep(0.25)
    r3 = zdalna_pominiecia(s, 123)
    po = s.luau('return tostring(workspace.TestWalki2:GetAttribute("SerwerPominieciaOdrzucone") or 0)', "Server").strip()
    wynik("P3. pominięcie z klienta bez zgody odrzucone przez serwer",
          r1 == {"ok": False, "powod": "pierwsza_walka"} and r2.get("powod") == "zly_wybor" and r3.get("powod") == "zly_wybor"
          and int(po) >= int(przed) + 3, "(%s | %s | %s | odrzucone %s → %s)" % (r1, r2, r3, przed, po))
    time.sleep(0.3)   # limit serwera 1 wywołanie na 0,2 s — bez przerwy P4 dostawał „za_szybko” po P3 (Studio 17.11.2026)
    s.steruj('"pomin", true')
    s.czekaj(("wynik",), 6)
    time.sleep(1.0)
    st = s.stan()
    wynik("P4. wymuszony pokaz bez zgody: serwer odmawia, JESZCZE RAZ zablokowane",
          st.get("OstatniStan") == "wynik" and st.get("OstatniaOdpowiedzPominiecia") == "pierwsza_walka"
          and st.get("_jeszczeZablokowany") is True, "(%s, %s)" % (st.get("OstatniaOdpowiedzPominiecia"), st.get("_jeszczeTekst")))
    s.czekaj_wolna(60)
    time.sleep(0.5)
    s.steruj('"zamknij"')
    time.sleep(1.2)
    if not start(s, o, "{ tempo = 1 }"):
        wynik("P5. druga walka wystartowała", False)
        return
    time.sleep(1.0)
    # atrybut PoznaneGatunki odświeża serwer przy przyjęciu walki (i przy pominięciu)
    poznane = s.luau('return tostring(game:GetService("Players"):GetPlayers()[1]:GetAttribute("PoznaneGatunki"))', "Server").strip()
    st = s.stan()
    od = st.get("_odtw") or {}
    zrzut(s, "pomijanie_druga")
    s.klik(GUI + "Kadr.Pomin.Przycisk")
    s.czekaj(("wynik",), 6)
    time.sleep(0.8)
    st2 = s.stan()
    wolna = (st2.get("NastepnaWalkaOd") or 0) - st2["_czasSerwera"]
    wynik("P5. gatunek poznany; druga walka: przycisk, klik → wynik, serwer ok, gracz wolny od razu",
          "lesny_slime" in poznane and od.get("pomijanie") is True and od.get("pomijanieNaEkranie") is True
          and st2.get("OstatniStan") == "wynik" and st2.get("OstatniaOdpowiedzPominiecia") == "ok" and wolna <= 0.2
          and st2.get("_jeszczeZablokowany") is False,
          "(poznane %s, odpowiedź %s, wolna za %.1f s)" % (poznane, st2.get("OstatniaOdpowiedzPominiecia"), wolna))
    s.klik(GUI + "Kadr.Wynik.Karta.JeszczeRaz.Przycisk")
    s.czekaj(("odtwarzanie",), 10)
    time.sleep(1.2)
    s.klawisz("Space")
    s.czekaj(("wynik",), 6)
    time.sleep(0.6)
    st3 = s.stan()
    wynik("P6. trzecia walka: spacja pomija (serwer ok)", st3.get("OstatniStan") == "wynik" and st3.get("OstatnioPominieto") is True
          and st3.get("OstatniaOdpowiedzPominiecia") == "ok", "(%s)" % st3.get("OstatniaOdpowiedzPominiecia"))
    s.steruj('"zamknij"')
    time.sleep(1.2)
    o2 = dict(o, przeciwnik="cierniowy_wilk")
    start(s, o2, "{ tempo = 4 }")
    time.sleep(0.8)
    od = (s.stan().get("_odtw") or {})
    wynik("P7. inny gatunek — znów bez przycisku", od.get("pomijanie") is False and od.get("pomijanieNaEkranie") is False)
    s.steruj('"zamknij"')
    if not mostek:
        return
    jest = s.luau('local k = workspace:FindFirstChild("LasPasGra") return tostring(k ~= nil and k:FindFirstChild("Sygnaly") ~= nil '
                  'and k.Sygnaly:FindFirstChild("WynikWalki") ~= nil)', "Server").strip()
    if jest != "true":
        log("  P8 pominięte: brak Workspace/LasPasGra/Sygnaly/WynikWalki")
        return
    kod = ('local g = game:GetService("Players"):GetPlayers()[1] local t = workspace:GetServerTimeNow() '
           'workspace.LasPasGra.Sygnaly.WynikWalki:Fire(g, { id = "test-1", strefa = "test", gatunek = "%s", straznik = false, '
           'wynik = "przegrana", poziom = 1, koniec = t + 30 }) task.wait(0.3) return "ok"')
    s.luau(kod % "lesny_slime", "Server")
    c1 = zdalna_pominiecia(s, "czy", "LasPasGra")
    time.sleep(0.25)
    p1 = zdalna_pominiecia(s, "pomin", "LasPasGra")
    time.sleep(0.25)
    s.luau(kod % "lesny_troll", "Server")
    c2 = zdalna_pominiecia(s, "czy", "LasPasGra")
    time.sleep(0.25)
    c3 = zdalna_pominiecia(s, "czy", "LasPotwory")
    # 17.11.2026 (noc): oba lasy mają Sygnaly/ZwolnijPoPominieciu (wybór 1 → opcja A) — „pomin” = ok z nastepnaOd;
    # bez uchwytu (stary kontener) dalej sesja_zrodla
    zwolni = s.luau('local k = workspace.LasPasGra return tostring(k.Sygnaly:FindFirstChild("ZwolnijPoPominieciu") ~= nil)',
                    "Server").strip() == "true"
    p1_ok = (p1.get("ok") is True and p1.get("powod") == "ok" and isinstance(p1.get("nastepnaOd"), (int, float))) if zwolni \
        else p1 == {"ok": True, "powod": "sesja_zrodla"}
    wynik("P8. mostek lasu-pasa: pamięć wspólna, pominięcie %s, nowy gatunek bez zgody, stary las bez walki = brak_walki"
          % ("zwalnia od razu" if zwolni else "= sesja_zrodla"),
          c1.get("ok") is True and p1_ok and c2 == {"ok": False, "powod": "pierwsza_walka"}
          and c3 == {"ok": False, "powod": "brak_walki"}, "(%s | %s | %s | %s)" % (c1, p1, c2, c3))
    # stary las z mostkiem (wybór 2 przyjęty na noc): sztuczny sygnał w LasPotwory → "czy" = ok dla poznanego gatunku
    jest2 = s.luau('local k = workspace:FindFirstChild("LasPotwory") return tostring(k ~= nil and k:FindFirstChild("Sygnaly") ~= nil '
                   'and k.Sygnaly:FindFirstChild("WynikWalki") ~= nil)', "Server").strip()
    if jest2 == "true":
        time.sleep(0.25)
        s.luau(kod.replace("workspace.LasPasGra", "workspace.LasPotwory") % "lesny_slime", "Server")
        c4 = zdalna_pominiecia(s, "czy", "LasPotwory")
        time.sleep(0.25)
        p4 = zdalna_pominiecia(s, "pomin", "LasPotwory")
        wynik("P8b. mostek starego lasu: poznany gatunek → zgoda, pominięcie przyjęte",
              c4.get("ok") is True and p4.get("ok") is True, "(%s | %s)" % (c4, p4))
    else:
        log("  P8b pominięte: brak Workspace/LasPotwory/Sygnaly/WynikWalki")


def test_mana(s, Z):
    for nazwa in ("mana_pierwsza_akcja", "pasywki"):
        o = Z[nazwa] if nazwa != "pasywki" else Z["pasywki"]["mag"]
        w = dziennik(o)
        if not start(s, o):
            wynik("mana %s" % nazwa, False, "walka nie wystartowała")
            continue
        d = w["dziennik"]
        zle, uzycia, gotowa_zrzut = [], 0, False
        for i, z in enumerate(d):
            # na początku zdarzenia: paski = poprzednie zdarzenie (u używającego: już po koszcie)
            st = przewin(s, z["t"] + 0.02)
            poprz = d[i - 1] if i > 0 else {"mana_gracz": w["strony"]["gracz"]["mana"], "mana_wrog": w["strony"]["wrog"]["mana"]}
            uzycie = z["umiejetnosc"] != "" and z["typ"] in ("umiejetnosc", "unik", "blok")
            for strona, pole in (("gracz", "manaGracz"), ("wrog", "manaWrog")):
                oczek = z["mana_" + strona] if (uzycie and z["kto"] == strona) else poprz["mana_" + strona]
                if st.get(pole) != oczek:
                    zle.append("zd. %d start %s: %s ≠ %s" % (i + 1, strona, st.get(pole), oczek))
            if uzycie:
                uzycia += 1
                if uzycia == 1:
                    zrzut(s, "mana_uzycie")
            st = przewin(s, z["t"] + z["trwa"] - 0.02)
            for strona, pole in (("gracz", "manaGracz"), ("wrog", "manaWrog")):
                if st.get(pole) != z["mana_" + strona]:
                    zle.append("zd. %d koniec %s: %s ≠ %s" % (i + 1, strona, st.get(pole), z["mana_" + strona]))
            if (st.get("manaGotowa") or {}).get("gracz") and not gotowa_zrzut:
                zrzut(s, "mana_gotowa")      # pierwsza chwila, gdy pasek gracza świeci (mana ≥ próg)
                gotowa_zrzut = True
        s.steruj('"pomin", true')
        st = s.stan()
        wynik("mana %s (%s): %d zdarzeń, %d użyć — paski = dziennik" % (nazwa, ZE.NAZWY[o["zestaw"]], len(d), uzycia),
              not zle and (st.get("OstatniaNiezgodnoscMany") or 0) == 0, "; ".join(zle[:5]))


def test_statusy(s, Z):
    # (pokaz, efekt, części ozdoby, oczekiwany napis przy nałożeniu (początek), znaczek na ikonie?)
    przypadki = [
        ("trucizna_stosy", "trucizna", ["OzdobaNosnik"], "TRUCIZNA", "stosy"),
        ("podpalenie_dluzsze", "podpalenie", ["OzdobaNosnik"], "PODPALENIE", None),
        ("krwawienie", "krwawienie", ["OzdobaNosnik"], "KRWAWIENIE", None),
        ("spowolnienie", "spowolnienie", ["Krysztal", "LodStopy"], "SPOWOLNIENIE", None),
        ("ogluszenie_gwiazdki", "ogluszenie", ["Gwiazdka"], "OGŁUSZENIE", None),
        ("ogluszenie_miazdzacy", "ogluszenie", ["Gwiazdka"], "OGŁUSZENIE", None),
        ("ogluszenie_pnacza", "ogluszenie", ["Pnacze", "Lisc"], "OGŁUSZENIE", None),
        ("zdarcie", "zdarcie_pancerza", ["Pekniecie"], "ZDARTY PANCERZ", None),
        ("skupienie", "skupienie", ["BlaskKrag"], "SKUPIENIE", None),
        ("tarcza_kamienna", "kamienna_skora", ["Kamien", "KamiennaPowloka"], "KAMIENNA SKÓRA −", "procent"),
        ("tarcza_bariera", "bariera", ["Banka"], "BARIERA −", "procent"),
    ]
    for pokaz, efekt, czesci, napis, znaczek in przypadki:
        o = Z[pokaz]
        w = dziennik(o)
        d = w["dziennik"]
        idx = next((i for i, z in enumerate(d) if z["typ"] == "efekt_nalozony" and z["efekt"] == efekt), None)
        if idx is None or not start(s, o):
            wynik("status %s (%s)" % (efekt, pokaz), False, "brak nałożenia w dzienniku albo walka nie wystartowała")
            continue
        z = d[idx]
        przewin(s, z["t"] + 0.15)
        teksty = napisy(s)
        st = przewin(s, z["t"] + z["trwa"] - 0.02)
        ikony = [e for e in (st.get("efekty") or {}).get(z["cel"], []) if e["id"] == efekt]
        cz = czesci_sceny(s, czesci)
        ok = bool(ikony) and ikony[0]["tury"] == max(1, z["tury"]) and any(t.startswith(napis) for t in teksty) and sum(cz.values()) > 0
        if znaczek == "stosy" and z["stosy"] > 1:
            ok = ok and ikony[0].get("znaczek") == "×%d" % z["stosy"]
        if znaczek == "procent":
            ok = ok and ikony[0].get("znaczek") == "−%d%%" % z["wartosc"]
        zrzut(s, pokaz)
        opis = "ikona %s, napisy %s, części %s" % (ikony[:1], teksty, cz)
        # stosy: zrzut przy nałożeniu z największą liczbą stosów (trucizna ×3) — ikona ze znaczkiem „×N”
        if znaczek == "stosy":
            imax = max((i for i, x in enumerate(d) if x["typ"] == "efekt_nalozony" and x["efekt"] == efekt),
                       key=lambda i: d[i]["stosy"])
            zm = d[imax]
            st3 = przewin(s, zm["t"] + zm["trwa"] - 0.02)
            ik3 = [e for e in (st3.get("efekty") or {}).get(zm["cel"], []) if e["id"] == efekt]
            ok = ok and bool(ik3) and (zm["stosy"] < 2 or ik3[0].get("znaczek") == "×%d" % zm["stosy"])
            zrzut(s, "%s%d" % (pokaz, zm["stosy"]))
            opis += ", najwięcej stosów: zd. %d ×%d → ikona %s" % (imax + 1, zm["stosy"], ik3[:1])
        # ogłuszenie: „TRACI TURĘ!” w turze celu; spowolnienie: nigdy
        traci = next((i for i in range(idx, len(d)) if d[i]["typ"] == "utrata_tury" and d[i]["kto"] == z["cel"]), None)
        if efekt == "ogluszenie" and traci is not None:
            przewin(s, d[traci]["t"] + 0.3)
            t2 = napisy(s)
            ok = ok and "TRACI TURĘ!" in t2
            zrzut(s, "traci_ture")
            opis += ", utrata tury: %s" % t2
        if efekt == "spowolnienie":
            ok = ok and not any(x["typ"] == "utrata_tury" for x in d)
        wynik("status %s (%s)" % (efekt, opis_o(o)), ok, opis)
        s.steruj('"pomin", true')


def opis_o(o):
    return "%s/%s/%d/%s ziarno %d" % (o["klasa"], o["przeciwnik"], o["poziom"], o["zestaw"], o["ziarno"])


def test_blok(s, Z):
    for kto, o in Z["blok"].items():
        if not o:
            wynik("blok %s" % kto, False, "brak walki z blokiem w ziarnach")
            continue
        w = dziennik(o)
        d = w["dziennik"]
        cel = "gracz" if kto in ("wojownik", "zwiadowca", "mag") else "wrog"
        idx = next(i for i, z in enumerate(d) if z["typ"] == "blok" and z["cel"] == cel)
        z = d[idx]
        if not start(s, o):
            wynik("blok %s" % kto, False, "walka nie wystartowała")
            continue
        st = przewin(s, z["t"] + 0.01)
        hit = st.get("trafienie") or (z["t"] + z["trwa"] * 0.5)
        przewin(s, hit + 0.04)
        teksty = napisy(s)
        cz = czesci_sceny(s, ["Parada", "ParadaBlysk"])
        procent = round((1 - w["czesc_przez_blok"]) * 100)
        tarcza = kto == "wojownik"
        ok = ("BLOK −%d%%" % procent) in teksty and ("−%d" % z["obrazenia"]) in teksty and ((cz["Parada"] == 0) == tarcza)
        zrzut(s, "blok_%s" % kto)
        wynik("blok %s (%s, zd. %d)" % (kto, opis_o(o), idx + 1), ok, "napisy %s, parada %s" % (teksty, cz))
        s.steruj('"pomin", true')
    o = Z.get("blok_umiejetnosci")
    if o:
        w = dziennik(o)
        d = w["dziennik"]
        idx = next(i for i, z in enumerate(d) if z["typ"] == "blok" and z["umiejetnosc"])
        bez_efektu = idx + 1 >= len(d) or d[idx + 1]["typ"] != "efekt_nalozony" or d[idx + 1]["kto"] != d[idx]["kto"]
        wynik("blok umiejętności bez efektu w dzienniku (%s)" % opis_o(o), bez_efektu)


def test_wskrzeszenie(s, Z):
    for pokaz in ("wskrzeszenie_gracza", "wskrzeszenie_przeciwnika", "wskrzeszenie_obu"):
        o = Z[pokaz]
        w = dziennik(o)
        d = w["dziennik"]
        if not start(s, o):
            wynik(pokaz, False, "walka nie wystartowała")
            continue
        zle = []
        pierwsze = True
        for i, z in enumerate(d):
            if z["typ"] != "wskrzeszenie":
                continue
            przewin(s, z["t"] + 0.01)
            st = s.stan().get("_odtw") or {}
            pole = "paskiGracz" if z["kto"] == "gracz" else "paskiWrog"
            if st.get(pole) != 0:
                zle.append("zd. %d: pasek przed wstaniem %s ≠ 0" % (i + 1, st.get(pole)))
            przewin(s, z["t"] + z["trwa"] * 0.5)
            cz = czesci_sceny(s, ["Swiatlo", "SwiatloKrag"])
            teksty = napisy(s)
            if pierwsze:
                zrzut(s, pokaz)
                pierwsze = False
            st = przewin(s, z["t"] + z["trwa"] - 0.02)
            if st.get(pole) != z["wartosc"] or cz["Swiatlo"] == 0 or "WSKRZESZENIE!" not in teksty:
                zle.append("zd. %d: pasek %s (oczek. %d), światło %s, napisy %s" % (i + 1, st.get(pole), z["wartosc"], cz, teksty))
            leg = s.luau('local g = game:GetService("Players").LocalPlayer.PlayerGui.TestWalki2Cutscenka '
                         'local t = g:FindFirstChild("%s", true) local l = t and t:FindFirstChild("Legenda", true) '
                         'return tostring(l and l.Visible) .. " " .. tostring(l and l:GetAttribute("Zuzyta"))'
                         % ("TabliczkaGracza" if z["kto"] == "gracz" else "TabliczkaWroga")).strip()
            if leg != "true true":
                zle.append("zd. %d: pióro legendy %s" % (i + 1, leg))
        s.steruj('"pomin", true')
        st = s.stan()
        g = sum(1 for z in d if z["typ"] == "wskrzeszenie" and z["kto"] == "gracz")
        wr = sum(1 for z in d if z["typ"] == "wskrzeszenie" and z["kto"] == "wrog")
        wynik("%s (%s)" % (pokaz, opis_o(o)), not zle and st.get("OstatnieWskrzeszenia") == "%d/%d" % (g, wr)
              and st.get("OstatniePaskiKoniec") == "%d/%d" % (d[-1]["hp_gracz"], d[-1]["hp_wrog"]), "; ".join(zle[:4]))


def test_pasywki(s, Z):
    for klasa, o in Z["pasywki"].items():
        if not start(s, o):
            wynik("pasywki %s" % klasa, False, "walka nie wystartowała")
            continue
        widziane = []
        for k in range(14):                  # co 0,3 s sceny od 0,8 s: karteczki po kolei (ok. 1,25 s każda)
            tau = 0.8 + 0.3 * k
            przewin(s, tau)
            n = s.luau('local g = game:GetService("Players").LocalPlayer.PlayerGui.TestWalki2Cutscenka '
                       'local p = g:FindFirstChild("PasywkaGracza", true) return p and p.Visible and tostring(p:GetAttribute("Pasywka")) or ""').strip()
            if n and (not widziane or widziane[-1] != n):
                widziane.append(n)
            if k == 1:
                zrzut(s, "pasywki_%s" % klasa)
        oczek = [S.PASYWNE[p]["nazwa"] for p in ZE.PASYWKI_ZESTAWU[klasa]] + [S.PASYWKI_BRONI[ZE.BRON_ZESTAWU[klasa]]["nazwa"]]
        s.steruj('"pomin", true')
        st = s.stan()
        sloty = ["gracz:%s" % p for p in ZE.PASYWKI_ZESTAWU[klasa]] + ["gracz:%s" % ZE.BRON_ZESTAWU[klasa]]
        wynik("pasywki %s: zapowiedź %s" % (klasa, oczek), widziane == oczek and all(x in (st.get("OstatniePasywki") or "") for x in sloty),
              "(widziane %s, atrybut %s)" % (widziane, st.get("OstatniePasywki")))


def test_telefon(s, Z):
    import telefon as TEL
    for rozm in ((844, 390), (667, 375)):
        s.steruj('"zamknij"')        # panel nie otwiera się, gdy sesja walki trwa (także w oknie wyniku)
        time.sleep(1.0)
        s.luau('workspace.TestWalki2:SetAttribute("EmulacjaEkranu", Vector2.new(%d, %d)) return "ok"' % rozm)
        time.sleep(0.6)
        s.steruj('"wybor"')
        for _ in range(10):
            time.sleep(0.5)
            if s.luau('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("TestWalki2Wybor") '
                      'return tostring(g ~= nil and g.Enabled)').strip() == "true":
                break
        time.sleep(0.6)
        p = TEL.zmierz(s, "TestWalki2Wybor")
        r = TEL.podsumuj("panel %dx%d" % rozm, p)
        if ZRZUTY:
            try:
                TEL.wytnij(s.zrzut(), p).save(os.path.join(KATALOG, "klatki", "v3_telefon_%dx%d_panel.jpg" % rozm), quality=88)
            except Exception as e:  # noqa: BLE001
                log("  zrzut panelu: %s" % e)
        wynik("telefon %dx%d: panel wyboru (zestaw, lustro) ≥ %g pkt" % (rozm[0], rozm[1], TEL.PROG), not r["ponizej_progu"],
              str([(x["t"], x["pkt"]) for x in r["ponizej_progu"][:6]]))
        o = Z["pasywki"]["mag"]
        start(s, o)
        przewin(s, 1.0)                       # karteczka pasywki, mana, informacja o pomijaniu
        w = dziennik(o)
        t_ef = next((z["t"] for z in w["dziennik"] if z["typ"] == "efekt_nalozony"), 3.0)
        p = TEL.zmierz(s, "TestWalki2Cutscenka")
        r1 = TEL.podsumuj("walka %dx%d (start)" % rozm, p)
        przewin(s, t_ef + 0.5)                # ikony efektów ze znaczkami
        p2 = TEL.zmierz(s, "TestWalki2Cutscenka")
        r2 = TEL.podsumuj("walka %dx%d (efekty)" % rozm, p2)
        if ZRZUTY:
            try:
                TEL.wytnij(s.zrzut_odtwarzacza()[0], p2).save(os.path.join(KATALOG, "klatki", "v3_telefon_%dx%d_walka.jpg" % rozm), quality=88)
            except Exception as e:  # noqa: BLE001
                log("  zrzut walki: %s" % e)
        drobne = r1["ponizej_progu"] + r2["ponizej_progu"]
        wynik("telefon %dx%d: walka v3 (mana, znaczki, pasywki, pomijanie) ≥ %g pkt" % (rozm[0], rozm[1], TEL.PROG), not drobne,
              str([(x["n"][-40:], x["t"], x["pkt"]) for x in drobne[:6]]))
        s.steruj('"pomin", true')
        s.steruj('"zamknij"')
    s.luau('workspace.TestWalki2:SetAttribute("EmulacjaEkranu", nil) return "ok"')


def test_koszt(s, Z):
    for pokaz in ("wskrzeszenie_obu", "pasywki", "trucizna_stosy"):
        o = Z[pokaz] if pokaz != "pasywki" else Z["pasywki"]["zwiadowca"]
        w = dziennik(o)
        if not start(s, o, "{ tempo = 1 }"):
            wynik("koszt %s" % pokaz, False, "walka nie wystartowała")
            continue
        st, dt = s.czekaj(("wynik",), w["czas"] * 1.6 + 25)
        m = {k: st.get(k) for k in ("OstatniKosztSkryptuSredni", "OstatniKosztSkryptuP95", "OstatniKosztSkryptuMaks",
                                    "OstatniP95Klatki", "OstatniaLiczbaInstancji", "OstatniCzasTrwania",
                                    "OstatniaNiezgodnoscPaskow", "OstatniaNiezgodnoscMany", "OstatnieBledyObslugi",
                                    "OstatnieBrakiChoreografii")}
        POMIARY.append(dict(m, walka=opis_o(o), czas_dziennika=w["czas"]))
        ok = (st.get("OstatniStan") == "wynik" and (m["OstatniKosztSkryptuSredni"] or 99) < 2.0 and (m["OstatniKosztSkryptuP95"] or 99) < 4.0
              and m["OstatniaNiezgodnoscPaskow"] == 0 and m["OstatniaNiezgodnoscMany"] == 0 and m["OstatnieBledyObslugi"] == 0
              and m["OstatnieBrakiChoreografii"] == 0)
        wynik("koszt klienta %s (%.1f s dziennika)" % (opis_o(o), w["czas"]), ok, json.dumps(m, ensure_ascii=False))
        s.steruj('"zamknij"')
        time.sleep(1.0)


def test_konsola(s):
    kons = s.konsola()
    zle = [w for w in kons.splitlines() if "[TestWalki2]" in w]
    wynik("konsola bez ostrzeżeń i błędów [TestWalki2]", not zle, "\n".join(zle[:8]))


def main():
    global ZRZUTY
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Próba Play odtwarzacza v3 i pomijania walk")
    ap.add_argument("--tylko", default="", help="pomijanie,mana,statusy,blok,wskrzeszenie,pasywki,telefon,koszt,konsola")
    ap.add_argument("--studio", default=None)
    ap.add_argument("--bez-zrzutow", action="store_true")
    ap.add_argument("--bez-mostka", action="store_true", help="bez sztucznego sygnału WynikWalki w LasPasGra (P8)")
    a = ap.parse_args()
    ZRZUTY = not a.bez_zrzutow
    czesci = [c for c in a.tylko.split(",") if c] or ["pomijanie", "mana", "statusy", "blok", "wskrzeszenie", "pasywki",
                                                         "telefon", "koszt", "konsola"]
    Z = ziarna()
    with SesjaPlay(studio=a.studio, timeout=240) as s:
        s.przy_tablicy()
        time.sleep(0.5)
        if "pomijanie" in czesci:
            test_pomijanie(s, Z, not a.bez_mostka)     # pierwsza: pamięć pomijania jest pusta tylko na starcie Play
            # P7 zostawia sesję serwera (pierwsza walka z wilkiem, bez pominięcia) — bez czekania pierwsza walka
            # części „mana” dostawała odmowę (Studio 17.11.2026: „walka nie wystartowała”)
            s.steruj('"zamknij"')
            s.czekaj_wolna(60)
        s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", true) return "ok"', "Server")
        for nazwa, f in (("mana", test_mana), ("statusy", test_statusy), ("blok", test_blok), ("wskrzeszenie", test_wskrzeszenie),
                         ("pasywki", test_pasywki), ("telefon", test_telefon), ("koszt", test_koszt)):
            if nazwa in czesci:
                try:
                    f(s, Z)
                except Exception as e:  # noqa: BLE001
                    wynik("część %s przerwana błędem" % nazwa, False, repr(e)[:300])
        if "konsola" in czesci:
            test_konsola(s)
        s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", nil) workspace.TestWalki2:SetAttribute("ZiarnoTestowe", nil) return "ok"', "Server")
    wynik("Studio wróciło do trybu Edit", getattr(s, "edit_po", False))
    with open(os.path.join(TU, "wynik_v3.json"), "w", encoding="utf-8") as f:
        json.dump({"wyniki": WYNIKI, "pomiary": POMIARY, "data": time.strftime("%Y-%m-%d %H:%M")}, f, ensure_ascii=False, indent=1)
    zle = [w["test"] for w in WYNIKI if not w["ok"]]
    log("WYNIK: %d/%d zaliczonych%s" % (len(WYNIKI) - len(zle), len(WYNIKI), "" if not zle else " — nie: " + "; ".join(zle)))
    sys.exit(1 if zle else 0)


if __name__ == "__main__":
    main()
