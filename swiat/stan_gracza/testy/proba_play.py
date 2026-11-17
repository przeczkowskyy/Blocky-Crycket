# -*- coding: utf-8 -*-
"""Próba „stanu gracza” w Roblox Studio (tryb Play) — część B zlecenia z 17.11.2026, plus pomiar poprawki M6 (E przy
chodzących potworach). Nie zmienia miejsca: sama włącza i wyłącza Play, niczego nie zapisuje i nie publikuje.

    python -B swiat/stan_gracza/testy/proba_play.py <folder wyników POZA repo> [--studio <id>] [--bez-zrzutow] [--bez-m6] [--tylko-m6]
    python -B swiat/stan_gracza/testy/proba_play.py --sprawdz      # bez Studio: parsuje każdy kawałek Luau (luau_mini)

Warunki (tryb Edit): Workspace/StanGracza (swiat/stan_gracza/zbuduj.py), Workspace/LasPasGra i Workspace/LasPas
(z wymienionymi skryptami: swiat/las_pas_gra/zbuduj.py --skrypty), Workspace/TestWalki2; dla punktu S07 także
Workspace/TreningProba. Wyniki (wyniki.json, lista.txt) idą do podanego folderu — mogą zawierać nazwę konta, dlatego
folder nie może leżeć w repozytorium. Zrzuty (bez nazwy konta: lista graczy i czat schowane) → swiat/stan_gracza/klatki/.

LISTA KONTROLNA (OK / BŁĄD / ?):
  S00 w Edit: kontenery na miejscu; script_grep po innych piszących Gold / XP / DataStore / leaderstats (i)
  S01 gotowość: SerwerStanuGotowy, ZgodnoscLogikiStanu „OK n/n”, RozkladyZ z ClassData, KlientStanuGotowy, las-pas gotowy
  S02 wybór klasy prawdziwym Enterem → Class = Warrior, sześć statystyk = 30 pkt rozkładu klasy, XPMax z krzywej
  S03 (a) każda z trzech klas (Warrior z ekranu, Scout i Mage przez ChooseClass jak ekran wyboru): walka ze slime'em
      przegrody s1 → serwer walczy tą klasą na poziomie gracza (SerwerOstatniaWalka), panel „Twój bohater: …”
  S04 (b) łup po walce: w trakcie walki Gold / XP / Level bez zmian, po walce = wynik z OstatniLup i krzywej; HUD (Gold,
      Level) pokazuje to samo co atrybuty
  S05 (d) awans → baner „POZIOM N” (PlayerGui.StanGraczaBaner), zrzut
  S06 (c) przegrana (troll albo wilk ponad poziom gracza) → +20% doświadczenia z OstatniLup, Gold i statystyki bez zmian
  S07 (e) trening Siły (haczyki TreningProba: wejdź, runda, autogra, wyjdź) → Strength rośnie o przyrost z treningu →
      opis bohatera (Sygnaly/SterowanieSerwera "bohater") ma tę Siłę → walka
  S08 (f) TestBohater = true na lesie-pasie → dawny panel T1, walka klasą i poziomem z panelu, bez łupu; potem wyłączony
  S09 M6: 15 podejść prawdziwym E (różne strony, kamera z przodu / z boku / za plecami) z dawną kotwicą
      (TestKotwicaStara = true) i 15 z nową — ile zaczęło walkę; dymek przy odmowie (blokada po walce)
  S10 (g) brak sygnału Sygnaly/Bohater (zmiana nazwy) → dawna walka, bez łupu; nazwa przywrócona
  S11 (g) usunięcie Workspace/StanGracza w czasie gry → dawny panel T1 i dawna walka, bez łupu
  S12 (h) konsola: bez błędów naszych skryptów ([StanGracza], [LasPasGra], [LasPotwory], „Script …StanGracza”);
      znane wiersze „Requester does not have permission for Asset” (dźwięki) pomijane
"""
import io
import json
import math
import os
import re
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (PAKIET, os.path.join(REPO, "tools"), os.path.join(REPO, "tools", "walka"),
           os.path.join(REPO, "swiat", "test_walki_roblox"), os.path.join(REPO, "swiat", "test_walki2", "testy")):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import dane as DANE  # noqa: E402
import logika_stanu as LS  # noqa: E402

KLATKI = os.path.join(PAKIET, "klatki")
_, D = DANE.dane_z_przypadkami()
ID_KLASY = {v: k for k, v in D["klasy_gracza"].items()}  # klasa silnika → Class
REAKCJA_M6 = 1.5  # s od stanięcia przy potworze do E w pomiarze M6 (gracz-człowiek; potwory chodzą)
ZNANE_W_KONSOLI = ("Requester does not have permission for Asset",)

KP = 'local k = workspace:FindFirstChild("LasPasGra") local H = game:GetService("HttpService") '
KS = 'local s = workspace:FindFirstChild("StanGracza") local H = game:GetService("HttpService") '
GR = 'local gracz = game:GetService("Players"):GetPlayers()[1] '
HRP = 'local hrp = game:GetService("Players"):GetPlayers()[1].Character.HumanoidRootPart '
J = ('local H = game:GetService("HttpService") local function J(v) local t = typeof(v) if t == "Vector3" then return { v.X, v.Y, v.Z } '
     'elseif t == "table" then local o = {} if #v > 0 then for i, b in ipairs(v) do o[i] = J(b) end '
     'else for a, b in v do o[tostring(a)] = J(b) end end return o '
     'elseif t == "number" and (v ~= v or v == math.huge or v == -math.huge) then return tostring(v) '
     'elseif t == "Instance" then return v:GetFullName() end return v end ')
ATRYBUTY_GRACZA = ["Class", "Level", "XP", "XPMax", "Gold", "Gems", "Strength", "Constitution", "Intelligence",
                   "Dexterity", "Luck", "Armor", "ShardyEwolucji", "TokenyKrainy_las", "BlokadaWalki"]

# Kawałki Luau (szablony %s / %d / %f) — --sprawdz parsuje każdy po podstawieniu zer (tools/walka/luau_mini.py).
KOD = {
    "edit": ('local H = game:GetService("HttpService") local function jest(n) local o = workspace:FindFirstChild(n) '
             'return o ~= nil and o:GetAttribute("Wygenerowane") == true end '
             'return H:JSONEncode({ stan = jest("StanGracza"), pas = jest("LasPasGra"), mapa = workspace:FindFirstChild("LasPas") ~= nil, '
             'proto = workspace:FindFirstChild("TestWalki2") ~= nil, trening = jest("TreningProba"), '
             'statystyki = workspace:FindFirstChild("StanGracza") and workspace.StanGracza:GetAttribute("StatystykiKlasy") })'),
    "gracz_atr": GR + 'local o = {} for _, n in { %s } do o[n] = J(gracz:GetAttribute(n)) end return H:JSONEncode(o)',
    "kont_atr": 'local o = {} local f = workspace:FindFirstChild("%s") if not f then return H:JSONEncode({ brak = true }) end '
                'for _, n in { %s } do o[n] = J(f:GetAttribute(n)) end return H:JSONEncode(o)',
    "stan_haczyk": KS + 'if not s then return H:JSONEncode({ brak = true }) end '
                        'return H:JSONEncode(J(s.Sygnaly.SterowanieSerwera:Invoke("%s", game:GetService("Players"):GetPlayers()[1])))',
    "klient_potworow": KP + 'return H:JSONEncode(J(k.Sygnaly.SterowanieKlienta:Invoke("stan")))',
    "odtw": 'local H = game:GetService("HttpService") return H:JSONEncode(J(workspace.TestWalki2.Sygnaly.Sterowanie:Invoke(%s)))',
    "przestaw": HRP + 'local p = Vector3.new(%f, %f, %f) hrp.Parent:PivotTo(CFrame.lookAt(p, Vector3.new(%f, p.Y, %f))) '
                      'hrp.AssemblyLinearVelocity = Vector3.zero return "ok"',
    "pozycja_potwora": KP + 'local c = k.Stan:FindFirstChild("%s") return H:JSONEncode(J(c and c:GetAttribute("Pozycja") or false))',
    "potwor_w_strefie": KP + 'local najlepszy for _, c in k.Stan:GetChildren() do if c:GetAttribute("Strefa") == "%s" '
                             'and c:GetAttribute("Stan") ~= "zajety" then najlepszy = c break end end '
                             'if not najlepszy then return H:JSONEncode({}) end '
                             'return H:JSONEncode({ id = najlepszy.Name, p = J(najlepszy:GetAttribute("Pozycja")), '
                             'poziom = najlepszy:GetAttribute("Poziom") })',
    "kamera": ('local cam = workspace.CurrentCamera local p = game:GetService("Players").LocalPlayer '
               'local h = p.Character and p.Character:FindFirstChild("HumanoidRootPart") if not h then return "brak" end '
               'local f, r = h.CFrame.LookVector, h.CFrame.RightVector local tryb = "%s" local oko, cel '
               'local g = Vector3.new(0, 1.5, 0) '
               'if tryb == "za" then oko, cel = h.Position - f * 10 + Vector3.new(0, 4, 0), h.Position + f * 6 '
               'elseif tryb == "przod" then oko, cel = h.Position + f * 2 + g, h.Position + g '
               'else oko, cel = h.Position + r * 6 - f * 2 + g, h.Position - f * 4 end '
               'cam.CameraType = Enum.CameraType.Scriptable cam.CFrame = CFrame.lookAt(oko, cel) return "ok"'),
    "kamera_zwykla": 'workspace.CurrentCamera.CameraType = Enum.CameraType.Custom return "ok"',
    "podpowiedz": KP + ('local w = k:FindFirstChild("Widoki") local kot = w and w:FindFirstChild("KotwicaE") '
                        'local pp = kot and kot:FindFirstChildOfClass("ProximityPrompt") local cam = workspace.CurrentCamera '
                        'local naEkranie = false if kot then local v, widac = cam:WorldToViewportPoint(kot.Position) '
                        'naEkranie = widac and v.Z > 0 end '
                        'local st = k.Sygnaly.SterowanieKlienta:Invoke("stan") '
                        'return H:JSONEncode({ wlaczona = pp ~= nil and pp.Enabled, najblizszy = st.najblizszy, '
                        'naEkranie = naEkranie, kotwica = J(kot and kot.Position or false), tekst = pp and pp.ActionText or "" })'),
    "zero_odmowy": KP + 'k:SetAttribute("OstatniaOdmowa", nil) k:SetAttribute("KlientOstatniKomunikat", nil) return "ok"',
    "komunikat": KP + ('local pg = game:GetService("Players").LocalPlayer.PlayerGui local g = pg:FindFirstChild("LasPotworyKomunikat") '
                       'return H:JSONEncode({ dymek = g ~= nil and g:GetAttribute("Tekst") or false, '
                       'ostatni = k:GetAttribute("KlientOstatniKomunikat") or false, odmowa = k:GetAttribute("OstatniaOdmowa") or false, '
                       'ogolny = pg:FindFirstChild("TestWalki2Komunikat") ~= nil })'),
    "kotwica_stara": KP + 'k:SetAttribute("TestKotwicaStara", %s) return "ok"',
    "hud": ('local H = game:GetService("HttpService") local pg = game:GetService("Players").LocalPlayer.PlayerGui '
            'local hud = pg:FindFirstChild("HUD") local p = hud and hud:FindFirstChild("PlayerPanel") '
            'local b = pg:FindFirstChild("StanGraczaBaner") local function t(n) local l = p and p:FindFirstChild(n) return l and l.Text or false end '
            'local tytul = b and b:FindFirstChild("Tytul", true) '
            'return H:JSONEncode({ wlaczony = hud ~= nil and hud.Enabled, gold = t("Gold"), level = t("Level"), gems = t("Gems"), '
            'baner = b ~= nil, banerTekst = tytul and tytul.Text or false })'),
    "panel": ('local H = game:GetService("HttpService") local pg = game:GetService("Players").LocalPlayer.PlayerGui '
              'local g = pg:FindFirstChild("LasPasGraBohater") local b = g and g:FindFirstChild("Przycisk") '
              'local o = g and g:FindFirstChild("Okno") return H:JSONEncode({ tekst = b and b.Text or false, '
              'widac = b ~= nil and b.Visible, okno = o ~= nil and o.Visible })'),
    "bez_nazwy": ('local SG = game:GetService("StarterGui") for _, t in { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Chat } do '
                  'pcall(function() SG:SetCoreGuiEnabled(t, false) end) end return "ok"'),
    "wybor_klasy": ('local H = game:GetService("HttpService") local p = game:GetService("Players").LocalPlayer '
                    'local g = p.PlayerGui:FindFirstChild("ClassSelect") local c = workspace.CurrentCamera '
                    'return H:JSONEncode({ ekran = g ~= nil and g.Enabled, kamera = c.CameraType.Name, '
                    'podpowiedzi = game:GetService("ProximityPromptService").Enabled, klasa = p:GetAttribute("Class") or false })'),
    "zmien_klase": 'game:GetService("ReplicatedStorage"):WaitForChild("ChooseClass"):FireServer("%s") return "ok"',
    "pas": KP + 'return H:JSONEncode(J(k.Sygnaly.SterowaniePasa:Invoke("%s", nil, %s)))',
    "test_atr": 'local k = workspace:FindFirstChild("%s") if k then k:SetAttribute("%s", %s) end return "ok"',
    "trening_wejdz": ('local H = game:GetService("HttpService") local t = workspace:FindFirstChild("TreningProba") '
                      'if not t then return H:JSONEncode({ brak = true }) end '
                      'local w = t.Sygnaly.SterowanieSerwera:Invoke("wejdz", "sila", game:GetService("Players"):GetPlayers()[1]) '
                      'local R = require(t.Moduly.DaneTreningu).runda '
                      'return H:JSONEncode({ wynik = J(w), dlugosc = R.dlugosc_s, odliczanie = R.odliczanie_s })'),
    "trening_klient": ('local H = game:GetService("HttpService") local t = workspace.TreningProba '
                       'return H:JSONEncode(J(t.Sygnaly.SterowanieKlienta:Invoke("%s", %s)))'),
    "trening_wyjdz": ('local t = workspace:FindFirstChild("TreningProba") if t then '
                      't.Sygnaly.SterowanieSerwera:Invoke("wyjdz", game:GetService("Players"):GetPlayers()[1]) end return "ok"'),
    "przemianuj": KS + 'local f = s and s.Sygnaly:FindFirstChild("%s") if f then f.Name = "%s" end return tostring(f ~= nil)',
    "usun_stan": KS + 'if s then s:Destroy() end return tostring(s ~= nil)',
    "imie": 'return game:GetService("Players"):GetPlayers()[1].Name',
    "walcz": KP + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("walcz", "%s"))',
    "bohater_t1": KP + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("bohater", "%s", "%s"))',
    "trening_sila": GR + 'return H:JSONEncode({ s = gracz:GetAttribute("TreningSila") or 0 })',
    "gotowy_klient": 'local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)',
    # baner trwa 2,6 s — liczymy go słuchaczem u klienta (lokalne atrybuty kontenera), zrzut jest tylko dodatkiem
    "sledz_baner": ('local pg = game:GetService("Players").LocalPlayer.PlayerGui local s = workspace.StanGracza '
                    'pg.ChildAdded:Connect(function(c) if c.Name == "StanGraczaBaner" then task.wait(0.05) '
                    'local t = c:FindFirstChild("Tytul", true) s:SetAttribute("ProbaBanery", (s:GetAttribute("ProbaBanery") or 0) + 1) '
                    's:SetAttribute("ProbaBanerTekst", t and t.Text or "?") end end) return "ok"'),
}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def sprawdz_kod():
    """Bez Studio: każdy szablon z KOD (po podstawieniu zer) i każdy przedrostek parsuje się w luau_mini."""
    import luau_mini as LM
    bledy = []
    for nazwa, szablon in KOD.items():
        kod = re.sub(r"%[sdf]", "0", szablon)
        if "J(" in kod and "local function J" not in kod:
            kod = J + kod
        try:
            LM.Parser(kod, nazwa, LM.Interpreter()).program()
        except LM.BladSkladni as e:
            bledy.append("%s: %s" % (nazwa, e))
    print("sprawdz: %d kawałków Luau, %s" % (len(KOD), "OK" if not bledy else "BŁĘDY:\n  " + "\n  ".join(bledy)))
    return 0 if not bledy else 1


def ostatni_lup(tekst):
    """OstatniLup = „<gracz>:<zrodlo>:<wynik>:<N>z:<N>xp” → (wynik, złoto, xp) albo None."""
    m = re.search(r":(\w+):(\w+):(\d+)z:(\d+)xp$", tekst or "")
    return (m.group(2), int(m.group(3)), int(m.group(4))) if m else None


def main():
    argv = sys.argv[1:]
    if "--sprawdz" in argv:
        return sprawdz_kod()
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    try:
        w_repo = os.path.commonpath([os.path.normcase(wyj), os.path.normcase(REPO)]) == os.path.normcase(REPO)
    except ValueError:  # inny dysk
        w_repo = False
    if w_repo:
        sys.exit("Folder wyników leży w repozytorium (wyniki mogą zawierać nazwę konta) — podaj folder poza repo")
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    bez_zrzutow = "--bez-zrzutow" in argv
    bez_m6 = "--bez-m6" in argv
    tylko_m6 = "--tylko-m6" in argv  # tylko S00–S02, S09 i S12 (powtórka pomiaru M6)
    os.makedirs(wyj, exist_ok=True)
    os.makedirs(KLATKI, exist_ok=True)
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

    WYNIKI, LISTA = {}, []

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
                    time.sleep(8)

        def js(kod, dm):
            w = json.loads(luau(J + kod, dm))
            return {} if w == [] else w  # JSONEncode pustej tabeli daje „[]”

        def stan_studio():
            return call("get_studio_state")["text"]

        def zrzut(nazwa):
            if bez_zrzutow:
                return
            nie_usypiaj()
            r = call("screen_capture", {"capture_id": "stan_" + nazwa}, timeout=150)
            if r["is_error"] or not r.get("images"):
                log("zrzut %s: BŁĄD %s" % (nazwa, r["text"][:120]))
                return
            dane = r["images"][0]
            if Image is not None:
                im = Image.open(io.BytesIO(dane)).convert("RGB")
                if im.width > 1280:
                    im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
                im.save(os.path.join(KLATKI, nazwa + ".jpg"), "JPEG", quality=85)
            else:
                with open(os.path.join(KLATKI, nazwa + ".png"), "wb") as f:
                    f.write(dane)
            log("zrzut", nazwa)

        def lua_lista(nazwy):
            return ", ".join('"%s"' % n for n in nazwy)

        def gracz_atr():
            return js(KOD["gracz_atr"] % lua_lista(ATRYBUTY_GRACZA), "Server")

        def kont_atr(nazwa, atrybuty, dm="Server"):
            return js(KOD["kont_atr"] % (nazwa, lua_lista(atrybuty)), dm)

        def stan_hak(polecenie):
            return js(KOD["stan_haczyk"] % polecenie, "Server")

        def klient_potworow():
            return js(KOD["klient_potworow"], "Client")

        def odtw(polecenie):
            return js(KOD["odtw"] % polecenie, "Client")

        def przestaw(p, patrz):
            luau(KOD["przestaw"] % (p[0], p[1], p[2], patrz[0], patrz[2]), "Server")

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

        def staty(a):
            return {st: a.get(at) for st, at in D["atrybuty_statystyk"].items()}

        def ostatnia_walka():
            return kont_atr("LasPasGra", ["SerwerOstatniaWalka", "SerwerLicznikWalk"])

        def stan_licz():
            return kont_atr("StanGracza", ["LicznikLupow", "LicznikPokazan", "LicznikAwansow", "OstatniLup", "OstatniBohater"])

        def dokoncz_walke(lap_baner=False):
            """Przewija trwającą walkę do końca i zamyka panel wyniku (jak gracz: POMIŃ niedostępne przy nowym gatunku).
            lap_baner: zaraz po zamknięciu czeka na baner awansu (2,6 s) i robi zrzut."""
            czekaj_na(lambda: odtw('"stan"').get("faza") == "odtwarzanie", 10, 0.4)
            odtw('"przewinDo", 1000')
            time.sleep(2.5)
            odtw('"zamknij"')
            if lap_baner and czekaj_na(lambda: js(KOD["hud"], "Client").get("baner"), 3, 0.2):
                zrzut("03_baner_awansu")
            czekaj_na(lambda: not klient_potworow().get("walka"), 30, 1.0)
            time.sleep(1.0)
            luau(KOD["kamera_zwykla"], "Client")

        def podejdz_i_e(cel_id, kamera="za", kat=180.0, odl=4.0, zrzut_przed=None, reakcja=None):
            """Staje obok potwora (kąt w stopniach wokół niego), twarzą do niego, ustawia kamerę i wciska prawdziwe E,
            gdy podpowiedź wskazuje tego potwora. → słownik: czy była podpowiedź, czy kotwica w kadrze, czy walka ruszyła."""
            info = {"id": cel_id, "kamera": kamera, "kat": kat, "reakcja": reakcja}
            for _ in range(1 if reakcja else 6):
                p = js(KOD["pozycja_potwora"] % cel_id, "Server")
                if not p:
                    info["blad"] = "potwor_zniknal"
                    return info
                r = math.radians(kat)
                stan = [p[0] + math.cos(r) * odl, p[1] + 3.2, p[2] + math.sin(r) * odl]
                przestaw(stan, p)
                luau(KOD["kamera"] % kamera, "Client")
                time.sleep(reakcja or 0.5)
                pp = js(KOD["podpowiedz"], "Client")
                info["podpowiedz"] = pp
                # z „reakcją”: gracz wciska E po tylu sekundach, czy podpowiedź jeszcze jest, czy nie (jak człowiek)
                if reakcja or (pp.get("wlaczona") and pp.get("najblizszy") == cel_id):
                    luau(KOD["zero_odmowy"], "Client")
                    if zrzut_przed:
                        zrzut(zrzut_przed)
                    nacisnij("E")
                    info["e"] = True
                    break
            info["walka"] = bool(czekaj_na(lambda: klient_potworow().get("walka"), 4, 0.4))
            if not info["walka"]:
                time.sleep(0.6)
                info["komunikat"] = js(KOD["komunikat"], "Client")
                luau(KOD["kamera_zwykla"], "Client")
            return info

        def walka_w_strefie(strefa, kamera="za", proby=3, zrzut_walki=None, lap_baner=False):
            """Walka z pierwszym wolnym potworem strefy (prawdziwe E; zapas: haczyk "walcz" z adnotacją)."""
            for _ in range(proby):
                cel = js(KOD["potwor_w_strefie"] % strefa, "Server")
                if not cel.get("id"):
                    time.sleep(3)
                    continue
                przed = {"gracz": gracz_atr(), "walka": ostatnia_walka(), "stan": stan_licz()}
                e = podejdz_i_e(cel["id"], kamera)
                jak = "E"
                if not e.get("walka"):
                    luau(KOD["walcz"] % cel["id"], "Client")
                    jak = "haczyk walcz (E nie zadziałało)"
                    e["walka"] = bool(czekaj_na(lambda: klient_potworow().get("walka"), 6, 0.4))
                if not e["walka"]:
                    continue
                time.sleep(3)
                w_trakcie = {"gracz": gracz_atr(), "hud": js(KOD["hud"], "Client")}
                if zrzut_walki:
                    zrzut(zrzut_walki)
                dokoncz_walke(lap_baner)
                time.sleep(2.0)
                po = {"gracz": gracz_atr(), "walka": ostatnia_walka(), "stan": stan_licz(), "hud": js(KOD["hud"], "Client")}
                return {"cel": cel, "jak": jak, "e": e, "przed": przed, "w_trakcie": w_trakcie, "po": po}
            return None

        # ================================================================ S00 Edit + script_grep
        nie_usypiaj()
        if "Current Studio Mode: Edit" not in stan_studio():
            sys.exit("Studio nie jest w trybie Edit — ta próba sama włącza Play")
        edit = json.loads(luau(KOD["edit"], "Edit"))
        zapisz("S00_edit", edit)
        grep = {}
        # zapytanie to wzorzec Luau — „(” trzeba ucieczką %(
        for q in ('SetAttribute%("Gold"', 'SetAttribute%("XP"', '"Gold"', '"XP"', "DataStore", "leaderstats"):
            r = call("script_grep", {"query": q}, timeout=120)
            grep[q] = r["text"][:4000]
        zapisz("S00_script_grep", grep)
        if not (edit["stan"] and edit["pas"] and edit["mapa"] and edit["proto"]):
            punkt("S00", False, "brak kontenerów w Edit: %s" % edit)
            sys.exit(2)
        punkt("S00", None, "kontenery: %s; script_grep — do przejrzenia w wyniki.json (S00_script_grep)" % edit)

        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        imie = None
        try:
            czekaj_na(lambda: "Client" in stan_studio() and luau(KOD["gotowy_klient"], "Client") == "true", 90, 1.0)
            imie = luau(KOD["imie"], "Server")
            luau(KOD["bez_nazwy"], "Client")
            time.sleep(3)

            # ================================================================ S01 gotowość
            st_atr = czekaj_na(lambda: (lambda a: a if a.get("SerwerStanuGotowy") else None)(
                kont_atr("StanGracza", ["SerwerStanuGotowy", "ZgodnoscLogikiStanu", "RozkladyZ", "TreningPodlaczony", "StatystykiKlasy"])),
                40, 1.0) or {}
            kl_atr = czekaj_na(lambda: (lambda a: a if a.get("KlientStanuGotowy") else None)(
                kont_atr("StanGracza", ["KlientStanuGotowy"], "Client")), 30, 1.0) or {}
            pas_atr = czekaj_na(lambda: (lambda a: a if a.get("SerwerGotowy") and a.get("SerwerPasaGotowy") else None)(
                kont_atr("LasPasGra", ["SerwerGotowy", "SerwerPasaGotowy"])), 60, 1.0) or {}
            n_przyp = sum(len(v) for v in D["przypadki"].values())
            zapisz("S01", {"stan": st_atr, "klient": kl_atr, "pas": pas_atr})
            punkt("S01", st_atr.get("ZgodnoscLogikiStanu") == "OK %d/%d" % (n_przyp, n_przyp)
                  and str(st_atr.get("RozkladyZ", "")).startswith("ClassData (3 klas)") and kl_atr.get("KlientStanuGotowy") is True
                  and bool(pas_atr), "stan %s | klient %s | las-pas %s" % (st_atr, kl_atr, pas_atr))

            # ================================================================ S02 wybór klasy Enterem
            wybor = {}
            for _ in range(20):
                wybor = js(KOD["wybor_klasy"], "Client")
                if not wybor["ekran"] and wybor["kamera"] == "Custom" and wybor["podpowiedzi"]:
                    break
                nacisnij("Return")
                time.sleep(1.5)
            time.sleep(1.5)
            a = gracz_atr()
            klasa = LS.klasa_silnika(D, a.get("Class"))[0]
            oczek = LS.rozdziel(D, D["rozklady"][klasa], LS.pula(D, LS.poziom_z(D, a.get("Level"))))
            zapisz("S02", {"wybor": wybor, "gracz": a, "oczekiwane": oczek})
            punkt("S02", a.get("Class") == "Warrior" and staty(a) == oczek and a.get("XPMax") == LS.xp_do_nastepnego(D, a.get("Level") or 1),
                  "Class %s, statystyki %s (oczek. %s), XPMax %s" % (a.get("Class"), staty(a), oczek, a.get("XPMax")))

            # do lasu-pasa bez przelotu kamery (przelot sprawdza próba pakietu las_pas_gra); walki przewijane
            js(KOD["pas"] % ("zapomnijPrzelot", "nil"), "Server")
            js(KOD["pas"] % ("przenies", '"las"'), "Server")
            luau(KOD["test_atr"] % ("LasPasGra", "TestBezSesji", "true"), "Server")
            time.sleep(4)
            czekaj_na(lambda: klient_potworow().get("widoki", 0) > 0, 20, 1.0)

            if not tylko_m6:
                # ================================================================ S03 + S04 + S05 trzy klasy, łup, awans
                walki = {}
                luau(KOD["sledz_baner"], "Client")
                for nr, id_klasy in enumerate(("Warrior", "Scout", "Mage")):
                    if nr > 0:
                        luau(KOD["zmien_klase"] % id_klasy, "Client")
                        time.sleep(1.5)
                    a0 = gracz_atr()
                    panel = js(KOD["panel"], "Client")
                    if nr == 0:
                        zrzut("01_panel_twoj_bohater")
                    banery = kont_atr("StanGracza", ["ProbaBanery"], "Client").get("ProbaBanery") or 0
                    # baner awansu pojawia się, gdy po walce HUD znów widać (KlientStanu) — zrzut przy pierwszym
                    w = walka_w_strefie("s1", zrzut_walki="02_walka_z_danych_gracza" if nr == 0 else None,
                                        lap_baner=banery == 0)
                    if not w:
                        walki[id_klasy] = {"blad": "walka nie ruszyła", "panel": panel}
                        continue
                    if nr == 0:
                        zrzut("04_hud_po_walce")
                    w["panel"] = panel
                    w["klasa_przed"] = a0.get("Class")
                    walki[id_klasy] = w
                zapisz("S03_S04", walki)
                dobre_a, dobre_b, opisy = [], [], {}
                for id_klasy, w in walki.items():
                    if "blad" in w:
                        opisy[id_klasy] = w["blad"]
                        continue
                    klasa = D["klasy_gracza"][id_klasy]
                    L0 = LS.poziom_z(D, w["przed"]["gracz"].get("Level"))
                    ow = str(w["po"]["walka"].get("SerwerOstatniaWalka") or "")
                    m = re.search(r"/(\w+)/(\w+)→(\d+)/(\w+)$", ow)
                    ok_a = bool(m) and m.group(1) == klasa and int(m.group(3)) == L0 and "Twój bohater" in str(w["panel"].get("tekst"))
                    lup = ostatni_lup(w["po"]["stan"].get("OstatniLup"))
                    gp, gw, gpo = w["przed"]["gracz"], w["w_trakcie"]["gracz"], w["po"]["gracz"]
                    ok_b = False
                    if lup:
                        L1, xp1, _ = LS.awans(D, L0, gp.get("XP") or 0, lup[2])
                        bez_zmian = all(gw.get(x) == gp.get(x) for x in ("Gold", "XP", "Level"))
                        po_ok = (gpo.get("Gold") == (gp.get("Gold") or 0) + lup[1] and gpo.get("Level") == L1 and gpo.get("XP") == xp1
                                 and gpo.get("XPMax") == LS.xp_do_nastepnego(D, L1))
                        hud = w["po"]["hud"]
                        hud_ok = (str(hud.get("gold")).replace(" ", "") == str(gpo.get("Gold")) and str(hud.get("level")) == str(gpo.get("Level")))
                        ok_b = bez_zmian and po_ok and hud_ok
                    opisy[id_klasy] = {"walka": ow, "panel": w["panel"].get("tekst"), "lup": lup, "przed": {x: gp.get(x) for x in ("Level", "XP", "Gold")},
                                       "w_trakcie": {x: gw.get(x) for x in ("Level", "XP", "Gold")},
                                       "po": {x: gpo.get(x) for x in ("Level", "XP", "Gold", "XPMax")}, "hud": w["po"]["hud"], "jak": w["jak"]}
                    if ok_a:
                        dobre_a.append(id_klasy)
                    if ok_b:
                        dobre_b.append(id_klasy)
                punkt("S03", len(dobre_a) == 3, "klasa i poziom gracza w walce: %s; %s" % (dobre_a, opisy))
                punkt("S04", len(dobre_b) == 3, "łup dopiero po walce, HUD = atrybuty: %s" % dobre_b)
                ban = kont_atr("StanGracza", ["ProbaBanery", "ProbaBanerTekst"], "Client")
                awanse = kont_atr("StanGracza", ["LicznikAwansow"]).get("LicznikAwansow") or 0
                zapisz("S05", {"banery": ban, "awansow": awanse})
                punkt("S05", (ban.get("ProbaBanery") or 0) >= 1 and str(ban.get("ProbaBanerTekst", "")).startswith("POZIOM") and awanse >= 1,
                      "awansów %s, banerów %s, ostatni %r (zrzut klatki/03_baner_awansu.jpg)" % (
                          awanse, ban.get("ProbaBanery"), ban.get("ProbaBanerTekst")))

                # ================================================================ S06 przegrana
                prz = None
                for strefa in ("t1", "w3", "w2"):
                    prz = walka_w_strefie(strefa, zrzut_walki="05_przegrana")
                    if prz:
                        prz["strefa"] = strefa
                        break
                if prz:
                    lup = ostatni_lup(prz["po"]["stan"].get("OstatniLup"))
                    gp, gpo = prz["przed"]["gracz"], prz["po"]["gracz"]
                    L0 = LS.poziom_z(D, gp.get("Level"))
                    ok6 = False
                    if lup and lup[0] == "przegrana":
                        L1, xp1, _ = LS.awans(D, L0, gp.get("XP") or 0, lup[2])
                        ok6 = (lup[1] == 0 and gpo.get("Gold") == gp.get("Gold") and gpo.get("Level") == L1 and gpo.get("XP") == xp1
                               and (L1 != L0 or staty(gpo) == staty(gp)))
                    zapisz("S06", {"strefa": prz["strefa"], "lup": lup, "przed": gp, "po": gpo, "walka": prz["po"]["walka"]})
                    punkt("S06", ok6 if (lup and lup[0] == "przegrana") else None,
                          "strefa %s, łup %s, Gold %s→%s, XP %s→%s, poziom %s→%s" % (prz["strefa"], lup, gp.get("Gold"), gpo.get("Gold"),
                                                                                 gp.get("XP"), gpo.get("XP"), gp.get("Level"), gpo.get("Level")))
                else:
                    punkt("S06", False, "walka z trollem / wilkiem nie ruszyła")

                # ================================================================ S07 trening Siły
                if edit.get("trening"):
                    a0 = gracz_atr()
                    t0 = kont_atr("StanGracza", ["LicznikTreningu"]).get("LicznikTreningu") or 0
                    tw = js(KOD["trening_wejdz"], "Server")
                    time.sleep(2.0)
                    js(KOD["trening_klient"] % ("start", "nil"), "Client")
                    time.sleep(0.8)
                    js(KOD["trening_klient"] % ("autograj", "1.0, false"), "Client")
                    time.sleep((tw.get("odliczanie") or 3) + 3)
                    zrzut("06_trening_sily")
                    time.sleep((tw.get("dlugosc") or 20) + 4)
                    luau(KOD["trening_wyjdz"], "Server")
                    time.sleep(2.5)
                    a1 = gracz_atr()
                    t1 = kont_atr("StanGracza", ["LicznikTreningu"]).get("LicznikTreningu") or 0
                    przyrost_sesji = js(KOD["trening_sila"], "Server").get("s")
                    opis = stan_hak("bohater")
                    w7 = walka_w_strefie("s2")
                    zapisz("S07", {"wejscie": tw, "przed": a0, "po": a1, "sygnaly": [t0, t1], "TreningSila": przyrost_sesji,
                                   "opis": opis, "walka": w7 and w7["po"]["walka"], "stan": w7 and w7["po"]["stan"]})
                    dS = (a1.get("Strength") or 0) - (a0.get("Strength") or 0)
                    ok7 = (dS > 0 and t1 > t0 and isinstance(opis, dict) and (opis.get("statystyki") or {}).get("sila") == a1.get("Strength")
                           and bool(w7))
                    punkt("S07", ok7, "Strength %s→%s (+%s, sygnałów %s), opis bohatera: siła %s, walka po treningu: %s" % (
                        a0.get("Strength"), a1.get("Strength"), dS, t1 - t0, (opis or {}).get("statystyki", {}).get("sila") if isinstance(opis, dict) else opis,
                        w7 and w7["po"]["walka"].get("SerwerOstatniaWalka")))
                else:
                    punkt("S07", None, "brak Workspace/TreningProba — pominięte")

                # ================================================================ S08 tryb testowy TestBohater
                luau(KOD["test_atr"] % ("LasPasGra", "TestBohater", "true"), "Server")
                time.sleep(1.5)
                panel8 = js(KOD["panel"], "Client")
                zrzut("07_panel_tryb_testowy")
                luau(KOD["bohater_t1"] % ("mag", "10"), "Client")
                w8 = walka_w_strefie("s2")
                luau(KOD["test_atr"] % ("LasPasGra", "TestBohater", "nil"), "Server")
                time.sleep(1.5)
                panel8po = js(KOD["panel"], "Client")
                ok8 = False
                if w8:
                    ow = str(w8["po"]["walka"].get("SerwerOstatniaWalka") or "")
                    bez_lupu = w8["po"]["stan"].get("LicznikLupow") == w8["przed"]["stan"].get("LicznikLupow")
                    ok8 = ("/mag/10→10/" in ow and bez_lupu and str(panel8.get("tekst", "")).find("Bohater:") >= 0
                           and "Twój" not in str(panel8.get("tekst")) and "Twój bohater" in str(panel8po.get("tekst")))
                zapisz("S08", {"panel": panel8, "panel_po": panel8po, "walka": w8 and w8["po"]["walka"], "stan": w8 and [w8["przed"]["stan"], w8["po"]["stan"]]})
                punkt("S08", ok8, "panel w trybie testowym %r → po wyłączeniu %r; walka %s" % (
                    panel8.get("tekst"), panel8po.get("tekst"), w8 and w8["po"]["walka"].get("SerwerOstatniaWalka")))

            # ================================================================ S09 M6 — prawdziwe E przed i po poprawce
            if not bez_m6:
                m6 = {}
                for seria, stara in (("przed", "true"), ("po", "nil")):
                    luau(KOD["kotwica_stara"] % stara, "Client")
                    proby = []
                    for i in range(15):
                        kamera = ("przod", "bok", "za")[i % 3]
                        kat = (i * 67) % 360
                        cel = None
                        for strefa in ("s1", "s2", "s3", "m1"):
                            cel = js(KOD["potwor_w_strefie"] % strefa, "Server")
                            if cel.get("id"):
                                break
                        if not cel or not cel.get("id"):
                            proby.append({"blad": "brak wolnego potwora"})
                            continue
                        pierwszy = seria == "po" and kamera == "przod" and not m6.get("zrzut")
                        if pierwszy:
                            m6["zrzut"] = True
                        info = podejdz_i_e(cel["id"], kamera, kat, 4.5, "08_m6_kamera_z_przodu" if pierwszy else None,
                                           reakcja=REAKCJA_M6)
                        if info.get("walka"):
                            dokoncz_walke()
                        proby.append(info)
                    m6[seria] = proby
                luau(KOD["kotwica_stara"] % "nil", "Client")
                # dymek przy odmowie: blokada po walce bez TestBezSesji (walka przewinięta, serwer liczy pełny czas)
                luau(KOD["test_atr"] % ("LasPasGra", "TestBezSesji", "nil"), "Server")
                odm = {}

                def wolny():
                    for strefa in ("s1", "s2", "s3", "m1"):
                        c = js(KOD["potwor_w_strefie"] % strefa, "Server")
                        if c.get("id"):
                            return c
                    return {}
                cel = wolny()
                if cel.get("id"):
                    i1 = podejdz_i_e(cel["id"], "za")
                    if i1.get("walka"):
                        dokoncz_walke()
                        cel2 = wolny()
                        if cel2.get("id"):
                            i2 = podejdz_i_e(cel2["id"], "za")
                            odm = {"pierwsza": i1.get("walka"), "druga": i2.get("walka"), "komunikat": i2.get("komunikat")}
                            zrzut("09_dymek_odmowy")
                            if i2.get("walka"):
                                dokoncz_walke()
                luau(KOD["test_atr"] % ("LasPasGra", "TestBezSesji", "true"), "Server")
                m6["dymek"] = odm
                zapisz("S09", m6)

                def zlicz(proby):
                    e = [p for p in proby if p.get("e")]
                    return {"e": len(e), "walka": sum(1 for p in e if p.get("walka")), "bez_podpowiedzi": len(proby) - len(e),
                            "podpowiedz_przy_E": sum(1 for p in e if (p.get("podpowiedz") or {}).get("wlaczona")),
                            "dymek_przy_porazce": sum(1 for p in e if not p.get("walka") and ((p.get("komunikat") or {}).get("ostatni"))),
                            "kamera_przod": "%d/%d" % (sum(1 for p in e if p["kamera"] == "przod" and p.get("walka")),
                                                       sum(1 for p in e if p["kamera"] == "przod"))}
                zp, zpo = zlicz(m6["przed"]), zlicz(m6["po"])
                kom = (odm.get("komunikat") or {}) if odm else {}
                # z reakcją 1,5 s część potworów odchodzi naprawdę (poza bramkę serwera) — wtedy ma być dymek, nie cisza
                punkt("S09", zpo["e"] > 0 and zpo["walka"] >= zp["walka"] and zpo["walka"] >= 0.8 * zpo["e"]
                      and bool(kom.get("ostatni")),
                      "E (po %.1f s od stanięcia przy potworze) zaczęło walkę: przed %d/%d (podpowiedź przy E %d, kamera z przodu %s), "
                      "po %d/%d (podpowiedź przy E %d, kamera z przodu %s, dymek przy nieudanych %d); dymek przy blokadzie: %r" % (
                          REAKCJA_M6, zp["walka"], zp["e"], zp["podpowiedz_przy_E"], zp["kamera_przod"], zpo["walka"], zpo["e"],
                          zpo["podpowiedz_przy_E"], zpo["kamera_przod"], zpo["dymek_przy_porazce"], kom.get("ostatni")))

            if not tylko_m6:
                # ================================================================ S10 brak sygnału Bohater
                js(KOD["przemianuj"] % ("Bohater", "BohaterWylaczony"), "Server")
                w10 = walka_w_strefie("s2")
                js(KOD["przemianuj"] % ("BohaterWylaczony", "Bohater"), "Server")
                ok10 = False
                if w10:
                    ow = str(w10["po"]["walka"].get("SerwerOstatniaWalka") or "")
                    ok10 = ("/auto→" in ow and w10["po"]["stan"].get("LicznikLupow") == w10["przed"]["stan"].get("LicznikLupow")
                            and w10["po"]["gracz"].get("Gold") == w10["przed"]["gracz"].get("Gold"))
                zapisz("S10", {"walka": w10 and w10["po"]["walka"], "stan": w10 and [w10["przed"]["stan"], w10["po"]["stan"]]})
                punkt("S10", ok10, "bez sygnału Bohater: %s (dawna reguła „auto”, bez łupu)" % (w10 and w10["po"]["walka"].get("SerwerOstatniaWalka")))

                # ================================================================ S11 usunięcie kontenera StanGracza
                js(KOD["usun_stan"], "Server")
                time.sleep(2.5)
                panel11 = js(KOD["panel"], "Client")
                w11 = walka_w_strefie("s1", zrzut_walki=None)
                zrzut("10_bez_stanu_gracza")
                ok11 = False
                if w11:
                    ow = str(w11["po"]["walka"].get("SerwerOstatniaWalka") or "")
                    ok11 = ("/auto→" in ow and "Bohater:" in str(panel11.get("tekst")) and "Twój" not in str(panel11.get("tekst"))
                            and w11["po"]["gracz"].get("Gold") == w11["przed"]["gracz"].get("Gold"))
                zapisz("S11", {"panel": panel11, "walka": w11 and w11["po"]["walka"]})
                punkt("S11", ok11, "bez kontenera: panel %r, walka %s" % (panel11.get("tekst"), w11 and w11["po"]["walka"].get("SerwerOstatniaWalka")))

            # ================================================================ S12 konsola
            kons = call("get_console_output", {}, timeout=60)["text"]
            nasze = ("StanGracza", "LasPasGra", "LasPotwory")
            linie = [x.strip()[:240] for x in kons.splitlines()
                     if any(n in x for n in nasze) or "rror" in x]
            linie = [x for x in linie if not any(z in x for z in ZNANE_W_KONSOLI)]
            bledy = [x for x in linie if ("rror" in x or "błąd" in x.lower() or "Stack" in x) and any(n in x for n in nasze)]
            zapisz("S12", linie[-80:])
            punkt("S12", not bledy, "%d wierszy naszych / z błędem, błędów naszych skryptów: %d %s" % (len(linie), len(bledy), bledy[:3]))
        finally:
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
            for _ in range(60):
                time.sleep(0.5)
                if "Current Studio Mode: Edit" in stan_studio():
                    break
            if imie:
                WYNIKI["_konto"] = imie  # tylko w folderze wyników poza repo
                zapisz("_koniec", time.strftime("%Y-%m-%d %H:%M:%S"))
            print("\nLISTA KONTROLNA:")
            for x in LISTA:
                print("  %s %-4s %s" % x)
            print("\nwyniki: %s | zrzuty: %s" % (wyj, os.path.relpath(KLATKI, REPO)))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
