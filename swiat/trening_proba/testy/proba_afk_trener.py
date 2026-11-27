# -*- coding: utf-8 -*-
"""Próba wejścia do sali treningu AFK przez trenera (tryb Play, 26.11.2026, zlecenie Karola) i sklepu trenera
(27.11.2026, polecenie Pawła: ulepszenia stanowisk i wzmacniacze ×2). Nie zmienia miejsca: sama włącza i wyłącza Play,
niczego nie zapisuje i nie publikuje (bez magazynu próby stan gracza nie zapisuje profilu). Ok. 10–12 minut.

    python -B swiat/trening_proba/testy/proba_afk_trener.py <folder wyników POZA repo> [--studio <id>] [--bez-zrzutow]

Warunki: Studio w trybie Edit; wdrożone trzy skrypty Pawła (swiat/trening_proba/wdroz_trening_afk.py), mapa
MiasteczkoBazar po przebudowie (studnia i ławki przesunięte), MiasteczkoBazarGra z danymi „Train” i TreningProba
z wybor_od_trenera = false. Wejście gracza jest prawdziwe (user_keyboard_input / user_mouse_input); kod Luau tylko
czyta stan, przestawia własną postać (jak inne próby — dojście piechotą trwałoby długo), w B20 udaje zajęte stanowisko
atrybutem (drugiego gracza w Play nie ma) i w B21–B23 wysyła prośbę wprost zdalnym zdarzeniem, jak zrobiłby oszust.
Wyniki: <wyj>/wyniki.json, <wyj>/lista.txt, zrzuty <wyj>/<nazwa>.jpg. Nazwa konta w zapisach → <gracz>; lista graczy
i czat schowane przed zrzutami.

LISTA (OK / BŁĄD / ?):
  B00 Edit: Source trzech skryptów w Studio = pliki repo (po wdrożeniu)
  B01 Play: Workspace/TreningAFK — 6 stanowisk, atrybut Zajete = false, ZERO części „Tabliczka*” i SurfaceGui
  B02 prawdziwe E przy trenerze → okno TreningAFKMenu otwarte (6 kafelków), wybór mini-gry zamknięty, bez dymka bazaru
  B03 kafelki: wartość = atrybut statystyki gracza, żaden nie jest zajęty
  B1x każde z sześciu: E przy trenerze → prawdziwy klik kafelka → okno zamknięte, TreningAFK = id, postać zakotwiczona
      ≤ 1,5 st od maty TEGO stanowiska, stanowisko Zajete; potem prawdziwy klik STOP → koniec, bez kotwicy, wolne
  B20 zajęte stanowisko (atrybut Zajete = true na serwerze): kafelek szary z BUSY, klik nic nie zaczyna; po zdjęciu
      atrybutu klik działa
  B21 prośba z daleka (25 st od trenera, wprost zdalnym zdarzeniem): odmowa „daleko”, trening nie startuje
  B22 limit: zła prośba i zaraz poprawna (< 0,5 s) → poprawna pominięta; po 0,8 s ta sama → trening startuje
  B23 prośba w trakcie treningu → odmowa „trening”, stanowisko bez zmian
  S00 (sklep, 27.11) prawdziwy klik zakładki SHOP → sześć kafelków stanowisk, stan sklepu z serwera, poziomy 0
  S01 bez Rybek (Gold = 0): klik „LV UP” Siły → odmowa „za_malo” (brakuje 300), poziom i Gold bez zmian
  S02 Gold = 20000: klik „LV UP” Siły → poziom 1, Gold 19700, w profilu stanu gracza pakiet TreningAFK u.Sila = 1
  S03 ulepszenie zmienia przyrost: trening Siły (poziom 1) — pasek 3,64 powtórzenia, pełne paski co ok. 4,4 s;
      Kondycja (poziom 0) — pasek 4, co ok. 4,8 s (bez klikania skill checków)
  S04 Siła do poziomu 5 (4 kliki) → kolejny klik: odmowa „maks”, Gold bez zmian
  S05 spam: 5 próśb o wzmacniacz Kondycji w 0,1 s (zdalnym zdarzeniem) → jeden zakup (−600), wzmacniacz ok. 600 s
  S06 drugi wzmacniacz Kondycji → odmowa „aktywny”, Gold bez zmian; zrzut 04_sklep_wzmacniacz (zakładka SHOP, kafelek
      z licznikiem)
  S07 wzmacniacz ×2 i jego koniec: czas wzmacniacza w module danych na serwerze skrócony do 15 s, zakup dla Szczęścia,
      trening Szczęścia: pełny pasek w trakcie daje +2 (licznik nad panelem widać — zrzut 05_panel_wzmacniacz), po
      15 s +1; czas przywrócony
  S08 zakup z daleka (25 st od trenera, zdalnym zdarzeniem) → odmowa „daleko”, Gold bez zmian
  B30 zamykanie okna: X (klik), stuknięcie obok okna (klik w tło), przycisk B pada, odejście od trenera
  B40 zrzuty: 01_okno_trenera (okno otwarte), 02_sala_od_wejscia (korytarz od przedsionka), 03_wejscie_placyk (wejście
      do sali i studnia z placyku), 06_sala_z_gory (cała sala przez szklany dach); „?” przy --bez-zrzutow
  B50 konsola bez błędów skryptów TreningAFK
"""
import io
import json
import math
import os
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"),
           os.path.join(REPO, "swiat", "test_walki2", "testy"), PAKIET):
    if _s not in sys.path:
        sys.path.insert(0, _s)

H = 'local H = game:GetService("HttpService") '
J = ('local function J(v) local t = typeof(v) if t == "Vector3" then return { v.X, v.Y, v.Z } '
     'elseif t == "table" then local o = {} for a, b in v do o[tostring(a)] = J(b) end return o end return v end ')
GR = 'local gracz = game:GetService("Players"):GetPlayers()[1] '
LP = 'local lp = game:GetService("Players").LocalPlayer '
IDS = ["Sila", "Kondycja", "Pancerz", "Zrecznosc", "Inteligencja", "Szczescie"]
ATRYBUT = {"Sila": "Strength", "Kondycja": "Constitution", "Pancerz": "Armor", "Zrecznosc": "Dexterity",
           "Inteligencja": "Intelligence", "Szczescie": "Luck"}
SKRYPTY = [("src/server/TreningAFK.server.luau", 'game:GetService("ServerScriptService").Server:FindFirstChild("TreningAFK")'),
           ("src/client/TreningAFKClient.client.luau",
            'game:GetService("StarterPlayer").StarterPlayerScripts.Client:FindFirstChild("TreningAFKClient")'),
           ("src/shared/TreningAFKDane.luau", 'game:GetService("ReplicatedStorage").Shared:FindFirstChild("TreningAFKDane")')]

KOD = {
    "edit": H + 'local o = {} ' + " ".join('do local ok, s = pcall(function() return %s end) o["%s"] = ok and s and s.Source or false end'
                                          % (sc, p) for p, sc in SKRYPTY) + ' return H:JSONEncode(o)',
    "gotowy_klient": 'local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)',
    "imie": LP + 'return lp.Name',
    "bez_nazwy": ('local SG = game:GetService("StarterGui") for _, t in { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Chat } do '
                  'pcall(function() SG:SetCoreGuiEnabled(t, false) end) end return "ok"'),
    "wybor_klasy": (H + LP + 'local g = lp.PlayerGui:FindFirstChild("ClassSelect") local hud = lp.PlayerGui:FindFirstChild("HUD") '
                    'return H:JSONEncode({ ekran = g ~= nil and g.Enabled, hud = hud ~= nil and hud.Enabled, '
                    'klasa = lp:GetAttribute("Class") or false })'),
    "zmien_klase": 'game:GetService("ReplicatedStorage"):WaitForChild("ChooseClass"):FireServer("Warrior") return "ok"',
    "stanowiska": (H + J + 'local f = workspace:FindFirstChild("TreningAFK") if not f then return H:JSONEncode({ brak = true }) end '
                   'local o, tab, sg = {}, 0, 0 for _, d in f:GetDescendants() do if string.find(d.Name, "Tabliczka") then '
                   'tab += 1 end if d:IsA("SurfaceGui") then sg += 1 end end for _, m in f:GetChildren() do '
                   'local mata = m:IsA("Model") and m.PrimaryPart if mata then o[m.Name] = { p = J(mata.Position), '
                   'zajete = m:GetAttribute("Zajete") } end end '
                   'return H:JSONEncode({ st = o, tabliczki = tab, surface = sg })'),
    "trener": (H + J + 'local b = workspace:FindFirstChild("MiasteczkoBazarGra") local p = b and b:FindFirstChild("Punkty") '
               'local e = p and p:FindFirstChild("E training_center") local pp = e and e:FindFirstChildOfClass("ProximityPrompt") '
               'return H:JSONEncode({ p = e and J(e.Position), tekst = pp and pp.ActionText, wl = pp and pp.Enabled })'),
    # stan: serwer (atrybuty gracza, postać, stanowiska) + klient (okno, panel, wybór mini-gry, dymek bazaru)
    "stan_s": (H + J + GR + 'local hrp = gracz.Character and gracz.Character:FindFirstChild("HumanoidRootPart") '
               'local f = workspace:FindFirstChild("TreningAFK") local z = {} if f then for _, m in f:GetChildren() do '
               'z[m.Name] = m:GetAttribute("Zajete") == true end end local st = {} '
               'for _, a in { "Strength", "Constitution", "Armor", "Dexterity", "Intelligence", "Luck" } do '
               'st[a] = gracz:GetAttribute(a) or 0 end '
               'return H:JSONEncode({ afk = gracz:GetAttribute("TreningAFK") or false, poz = hrp and J(hrp.Position), '
               'kotwica = hrp ~= nil and hrp.Anchored, zajete = z, staty = st })'),
    "stan_k": (H + J + LP + 'local g = lp.PlayerGui:FindFirstChild("TreningAFKMenu") local t = lp.PlayerGui:FindFirstChild("TreningAFK") '
               'local o = g and g:FindFirstChild("Okno") local c = o and o:FindFirstChild("Cwiczenia") local kafle = {} '
               'if c then for _, b in c:GetChildren() do if b:IsA("TextButton") then local w = b:FindFirstChild("Wartosc") '
               'kafle[b.Name] = { zajete = b:GetAttribute("Zajete") == true, wartosc = w and w.Text, '
               'busy = b:FindFirstChild("Zajete") ~= nil and b.Zajete.Visible } end end end '
               'local tp = workspace:FindFirstChild("TreningProba") local tsg = tp and tp:FindFirstChild("Sygnaly") '
               'local th = tsg and tsg:FindFirstChild("SterowanieKlienta") local s = th and th:Invoke("stan") '
               'local bz = workspace:FindFirstChild("MiasteczkoBazarGra") local sb = bz and bz.Sygnaly.SterowanieKlienta:Invoke("stan") '
               'local h = sb and sb.historia local ost = h and h[#h] '
               'return H:JSONEncode({ menu = g ~= nil and g:GetAttribute("Otwarte") == true, menu_jest = g ~= nil, '
               'tytul = o and o.Tytul.Text, kafle = kafle, panel = t ~= nil and t.Enabled, '
               'wybor_mini = s ~= nil and s.wybor == true, dymek = ost ~= nil and ost.dymek == true, '
               'odmowa = lp:GetAttribute("ProbaOdmowa") or false, '
               'ekran = J(workspace.CurrentCamera.ViewportSize), kamera = workspace.CurrentCamera.CameraType.Name })'),
    "przestaw": (GR + 'local c = gracz.Character local hrp = c.HumanoidRootPart hrp.Anchored = false '
                 'hrp.AssemblyLinearVelocity = Vector3.zero c:PivotTo(CFrame.lookAt(Vector3.new(%r, %r, %r), '
                 'Vector3.new(%r, %r, %r))) return "ok"'),
    "kamera_za": (LP + 'local cam = workspace.CurrentCamera local h = lp.Character and lp.Character:FindFirstChild('
                  '"HumanoidRootPart") if h then cam.CameraType = Enum.CameraType.Custom task.delay(0.05, function() '
                  'cam.CFrame = CFrame.lookAt(h.Position - h.CFrame.LookVector * 10 + Vector3.new(0, 4, 0), '
                  'h.Position + h.CFrame.LookVector * 4) end) end return "ok"'),
    "sluchacz": (LP + 'if not lp:GetAttribute("ProbaSluchacz") then lp:SetAttribute("ProbaSluchacz", true) '
                 'game:GetService("ReplicatedStorage").TreningAFK.OnClientEvent:Connect(function(a, b) '
                 'if a == "odmowa" then lp:SetAttribute("ProbaOdmowa", tostring(b)) end end) end '
                 'lp:SetAttribute("ProbaOdmowa", nil) return "ok"'),
    "wyslij": 'game:GetService("ReplicatedStorage").TreningAFK:FireServer("wybierz", "%s") return "ok"',
    "wyslij_dwa": ('local Z = game:GetService("ReplicatedStorage").TreningAFK Z:FireServer("wybierz", "Nic") '
                   'task.wait(0.1) Z:FireServer("wybierz", "%s") return "ok"'),
    "zajete": 'workspace.TreningAFK["%s"]:SetAttribute("Zajete", %s) return "ok"',
    # sklep trenera (27.11.2026)
    "sluchacz_sklepu": (LP + 'if not lp:GetAttribute("ProbaSluchaczSklepu") then lp:SetAttribute("ProbaSluchaczSklepu", true) '
                        'local H = game:GetService("HttpService") local punkty = {} '
                        'game:GetService("ReplicatedStorage").TreningAFK.OnClientEvent:Connect(function(a, b, c, d, e) '
                        'if a == "odmowa" then lp:SetAttribute("ProbaOdmowa", tostring(b)) lp:SetAttribute("ProbaBrakuje", d) '
                        'elseif a == "start" then lp:SetAttribute("ProbaPasek", d) lp:SetAttribute("ProbaPrzyrost", c) '
                        'lp:SetAttribute("ProbaWzm", e) table.clear(punkty) lp:SetAttribute("ProbaPunkty", "[]") '
                        'elseif a == "punkt" then table.insert(punkty, { t = os.clock(), ile = c }) '
                        'lp:SetAttribute("ProbaPunkty", H:JSONEncode(punkty)) end end) end '
                        'lp:SetAttribute("ProbaOdmowa", nil) lp:SetAttribute("ProbaBrakuje", nil) return "ok"'),
    "stan_sklepu": (H + LP + 'local g = lp.PlayerGui:FindFirstChild("TreningAFKMenu") local o = g and g:FindFirstChild("Okno") '
                    'local s = o and o:FindFirstChild("Sklep") local k = {} if s then for _, f in s:GetChildren() do '
                    'if f:IsA("Frame") then k[f.Name] = { poziom = f:GetAttribute("Poziom"), wzm = f:GetAttribute("Wzmacniacz"), '
                    'ulepsz = f.Ulepsz.Text, wzm_tekst = f.Wzmacniacz.Text } end end end '
                    'local t = lp.PlayerGui:FindFirstChild("TreningAFK") local w = t and t.Panel:FindFirstChild("Wzmocnienie") '
                    'return H:JSONEncode({ sklep = g ~= nil and g:GetAttribute("Sklep") == true and s ~= nil and s.Visible, '
                    'tytul = o and o.Tytul.Text, kafle = k, odmowa = lp:GetAttribute("ProbaOdmowa") or false, '
                    'brakuje = lp:GetAttribute("ProbaBrakuje") or false, pasek = lp:GetAttribute("ProbaPasek") or false, '
                    'przyrost = lp:GetAttribute("ProbaPrzyrost") or false, wzm_start = lp:GetAttribute("ProbaWzm") or false, '
                    'punkty = H:JSONDecode(lp:GetAttribute("ProbaPunkty") or "[]"), panel_wzm = w ~= nil and w.Visible, '
                    'panel_wzm_tekst = w and w.Text or false })'),
    "profil_sklepu": (H + GR + 'local s = workspace:FindFirstChild("StanGracza") local f = s and s.Sygnaly:FindFirstChild("DanePakietu") '
                      'local v = f and f:Invoke("czytaj", gracz, "TreningAFK") '
                      'return H:JSONEncode({ stan = s ~= nil, dane = v or false, gold = gracz:GetAttribute("Gold") or 0 })'),
    "zloto": GR + 'gracz:SetAttribute("Gold", %d) return "ok"',
    "kup": 'game:GetService("ReplicatedStorage").TreningAFK:FireServer("kup", "%s", "%s") return "ok"',
    "kup_seria": ('local Z = game:GetService("ReplicatedStorage").TreningAFK for i = 1, 5 do '
                  'Z:FireServer("kup", "wzmacniacz", "%s") task.wait(0.02) end return "ok"'),
    "czas_wzm": ('local D = require(game:GetService("ReplicatedStorage").Shared.TreningAFKDane) '
                 'D.sklep.wzmacniacze.czas = %d return "ok"'),
}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def odl_xz(a, b):
    return math.hypot(a[0] - b[0], a[2] - b[2])



def sprawdz_kod():
    """Bez Studio (27.11.2026): każdy kawałek Luau z KOD (po podstawieniu zer) parsuje się w tools/walka/luau_mini."""
    import re
    sys.path.insert(0, os.path.join(REPO, "tools", "walka"))
    import luau_mini as LM  # noqa: E402
    bledy = []
    for n, k in KOD.items():
        kod = re.sub(r"%[sd]", "0", re.sub(r"%[-+]?[\d.]*[fr]", "0.5", k))
        try:
            LM.Parser(kod, n, LM.Interpreter()).program()
        except LM.BladSkladni as e:
            bledy.append("%s: %s" % (n, e))
    print("sprawdz: %d kawałków Luau, %s" % (len(KOD), "OK" if not bledy else "BŁĘDY:\n  " + "\n  ".join(bledy)))
    return 0 if not bledy else 1

def main():
    argv = sys.argv[1:]
    if argv[:1] == ["--sprawdz"]:
        return sprawdz_kod()
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    try:
        w_repo = os.path.commonpath([os.path.normcase(wyj), os.path.normcase(REPO)]) == os.path.normcase(REPO)
    except ValueError:
        w_repo = False
    if w_repo:
        sys.exit("Folder wyników leży w repozytorium (wyniki mogą zawierać nazwę konta) — podaj folder poza repo")
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    bez_zrzutow = "--bez-zrzutow" in argv
    os.makedirs(wyj, exist_ok=True)
    from cel_studio import wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    from wdroz_trening_afk import norm  # noqa: E402
    try:
        from czuwanie import nie_usypiaj  # noqa: E402
    except ImportError:
        def nie_usypiaj():
            return False
    try:
        from PIL import Image  # noqa: E402
    except ImportError:
        Image = None
    with open(os.path.join(REPO, "swiat", "miasteczko_bazar", "znaczniki.json"), encoding="utf-8-sig") as f:
        ZN = json.load(f)
    TC = ZN["training_center"]
    STOISKO = TC["stoisko"]                       # gdzie stoi gracz przed trenerem (świat)
    PODP = TC["podpowiedz"]                       # punkt E trenera
    KOR_A = ZN["trening_afk"]["przejscie"]["przedsionek"]   # wejście do sali z placyku (27.11.2026)
    KOR_B = ZN["trening_afk"]["przejscie"]["koniec"]        # koniec korytarza przy zachodniej ścianie

    WYNIKI, LISTA, nazwa = {}, [], [None]

    def anonim(v):
        t = json.dumps(v, ensure_ascii=False)
        if nazwa[0]:
            t = t.replace(nazwa[0], "<gracz>")
        return json.loads(t)

    def zapisz(k, v):
        WYNIKI[k] = anonim(v)
        with open(os.path.join(wyj, "wyniki.json"), "w", encoding="utf-8") as f:
            json.dump(WYNIKI, f, ensure_ascii=False, indent=1)

    def punkt(kod, ok, opis):
        LISTA.append((kod, "OK" if ok is True else ("BŁĄD" if ok is False else "?"), anonim(opis)))
        log("%s %s — %s" % LISTA[-1])
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
                    r = call("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=150)
                    if r["is_error"]:
                        raise StudioError(r["text"][:800])
                    return r["text"].strip()
                except Exception as e:  # noqa: BLE001 — Studio czasem chwilę nie odpowiada
                    if i == proby - 1:
                        raise
                    log("luau: ponawiam po błędzie:", str(e)[:200])
                    time.sleep(6)

        def js(kod, dm):
            try:
                w = json.loads(luau(kod, dm))
            except ValueError:
                return {}
            return w if isinstance(w, dict) else {}

        def stan():
            w = js(KOD["stan_s"], "Server")
            w.update(js(KOD["stan_k"], "Client"))
            return w

        def czekaj_na(warunek, limit, co=0.4):
            koniec = time.time() + limit
            while time.time() < koniec:
                w = warunek()
                if w:
                    return w
                time.sleep(co)
            return None

        def klawisz(k):
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": k}]})

        def klik(sciezka=None, xy=None):
            krok = {"action": "moveTo"}
            if sciezka:
                krok["instance_path"] = "LocalPlayer.PlayerGui." + sciezka
            else:
                krok["x"], krok["y"] = xy
            r = call("user_mouse_input", {"datamodel_type": "Client", "actions": [
                krok, {"action": "mouseButtonClick", "mouse_button": "left"}]})
            return not r["is_error"]

        def przestaw(p, patrz):
            luau(KOD["przestaw"] % (p[0], p[1], p[2], patrz[0], p[1], patrz[2]), "Server")
            time.sleep(0.9)

        def zrzut(nazwa_, kamera=None, patrz=None):
            if bez_zrzutow:
                return False
            nie_usypiaj()
            a = {"capture_id": "afk_" + nazwa_}
            if kamera:
                a["camera_position"], a["look_at_position"] = list(kamera), list(patrz)
            r = call("screen_capture", a, timeout=150)
            if r["is_error"] or not r.get("images"):
                log("zrzut %s: BŁĄD %s" % (nazwa_, r["text"][:120]))
                return False
            dane = r["images"][0]
            if Image is not None:
                im = Image.open(io.BytesIO(dane)).convert("RGB")
                if im.width > 1280:
                    im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
                im.save(os.path.join(wyj, nazwa_ + ".jpg"), "JPEG", quality=85)
            else:
                with open(os.path.join(wyj, nazwa_ + ".png"), "wb") as f:
                    f.write(dane)
            return True

        def do_trenera():
            """Postać przed trenerem twarzą do niego, kamera za plecami."""
            przestaw((STOISKO[0], STOISKO[1] + 3.2, STOISKO[2]), PODP)
            luau(KOD["kamera_za"], "Client")
            time.sleep(0.6)

        def otworz_menu():
            """Prawdziwe E przy trenerze (do 3 naciśnięć — bazar ma krótką blokadę po przeniesieniu)."""
            st = {}
            for i in range(3):
                klawisz("E")
                st = czekaj_na(lambda: (lambda t: t if t.get("menu") else None)(stan()), 3) or stan()
                if st.get("menu"):
                    st["naciśnięć_E"] = i + 1
                    return st
                time.sleep(1.2)
            return st

        def zakoncz_trening():
            st = stan()
            if st.get("afk"):
                klik("TreningAFK.Panel.Stop")
                st = czekaj_na(lambda: (lambda t: t if not t.get("afk") else None)(stan()), 5) or stan()
            return st

        nie_usypiaj()
        if "Current Studio Mode: Edit" not in call("get_studio_state")["text"]:
            sys.exit("Studio nie jest w trybie Edit — ta próba sama włącza Play")
        # ------------------------------------------------------------------ B00 Edit: skrypty = repo
        ed = js(KOD["edit"], "Edit")
        zgodne = {p: bool(ed.get(p)) and norm(ed[p]) == norm(open(os.path.join(REPO, p), encoding="utf-8").read())
                  for p, _ in SKRYPTY}
        zapisz("B00", zgodne)
        punkt("B00", all(zgodne.values()), "Studio = repo: %s" % ", ".join("%s %s" % (os.path.basename(p), "tak" if z else "NIE")
                                                                        for p, z in zgodne.items()))

        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        try:
            czekaj_na(lambda: "Client" in call("get_studio_state")["text"] and luau(KOD["gotowy_klient"], "Client") == "true",
                      90, 1.0)
            nazwa[0] = luau(KOD["imie"], "Client")
            luau(KOD["bez_nazwy"], "Client")
            time.sleep(3)
            wk = js(KOD["wybor_klasy"], "Client")
            for _ in range(10):
                if not wk.get("ekran") and wk.get("klasa") and wk.get("hud"):
                    break
                klawisz("Return")
                time.sleep(1.5)
                wk = js(KOD["wybor_klasy"], "Client")
            if not wk.get("klasa"):
                luau(KOD["zmien_klase"], "Client")
                time.sleep(2)
            luau(KOD["sluchacz"], "Client")

            # -------------------------------------------------------------- B01 stanowiska bez tabliczek
            sw = czekaj_na(lambda: (lambda w: w if len(w.get("st") or {}) >= 6 else None)(js(KOD["stanowiska"], "Server")),
                           40, 1.0) or {}
            st_ = sw.get("st") or {}
            zapisz("B01", sw)
            punkt("B01", sorted(st_) == sorted(IDS) and sw.get("tabliczki") == 0 and sw.get("surface") == 0
                  and all(v.get("zajete") is False for v in st_.values()),
                  "stanowisk %d, tabliczek %s, SurfaceGui %s, Zajete = false: %s" % (
                      len(st_), sw.get("tabliczki"), sw.get("surface"), all(v.get("zajete") is False for v in st_.values())))
            if len(st_) != 6:
                return 1
            tr = js(KOD["trener"], "Client")
            zapisz("trener", tr)

            # -------------------------------------------------------------- B02 E przy trenerze → okno
            do_trenera()
            st = otworz_menu()
            zapisz("B02", {"stan": st, "trener": tr})
            punkt("B02", st.get("menu") is True and len(st.get("kafle") or {}) == 6 and not st.get("wybor_mini")
                  and not st.get("dymek") and tr.get("tekst") == "Train",
                  "okno %s, kafelków %d, wybór mini-gry %s, dymek %s, podpowiedź „%s”, naciśnięć E %s" % (
                      st.get("menu"), len(st.get("kafle") or {}), st.get("wybor_mini"), st.get("dymek"), tr.get("tekst"),
                      st.get("naciśnięć_E")))
            ok_z1 = zrzut("01_okno_trenera")

            # -------------------------------------------------------------- B03 wartości na kafelkach
            k = st.get("kafle") or {}
            zle = [i for i in IDS if str(k.get(i, {}).get("wartosc")) != str(int(math.floor((st.get("staty") or {}).get(ATRYBUT[i], 0))))]
            zapisz("B03", {"kafle": k, "staty": st.get("staty")})
            punkt("B03", not zle and not any(v.get("zajete") for v in k.values()),
                  "wartości zgodne z atrybutami: %s, zajętych %d" % ("tak" if not zle else "NIE " + ",".join(zle),
                                                                    sum(1 for v in k.values() if v.get("zajete"))))

            # -------------------------------------------------------------- B1x sześć ćwiczeń
            for n, i in enumerate(IDS):
                zakoncz_trening()
                if not stan().get("menu"):
                    do_trenera()
                    otworz_menu()
                klik("TreningAFKMenu.Okno.Cwiczenia." + i)
                a = czekaj_na(lambda: (lambda t: t if t.get("afk") == i else None)(stan()), 6) or stan()
                od = odl_xz(a.get("poz") or [0, 0, 0], st_[i]["p"])
                time.sleep(1.0)
                b = zakoncz_trening()
                zapisz("B1%d" % n, {"id": i, "po_kliknieciu": a, "od_maty": od, "po_stop": b})
                punkt("B1%d" % n, a.get("afk") == i and not a.get("menu") and a.get("kotwica") is True and od <= 1.5
                      and (a.get("zajete") or {}).get(i) is True and a.get("panel") is True
                      and not b.get("afk") and b.get("kotwica") is False and not (b.get("zajete") or {}).get(i),
                      "%s: trening „%s”, okno %s, kotwica %s, %.1f st od maty, zajęte %s, panel %s → STOP: „%s”, kotwica %s" % (
                          i, a.get("afk"), "zamknięte" if not a.get("menu") else "OTWARTE", a.get("kotwica"), od,
                          (a.get("zajete") or {}).get(i), a.get("panel"), b.get("afk"), b.get("kotwica")))
                if n == 0:
                    # 27.11.2026: duża sala — z przedsionka wzdłuż korytarza ku zachodniej ścianie
                    zrzut("02_sala_od_wejscia", (KOR_A[0] + 1.0, 8.0, KOR_A[2] - 2.0), (KOR_B[0], 3.0, KOR_B[2]))

            # -------------------------------------------------------------- B20 zajęte stanowisko
            zakoncz_trening()
            luau(KOD["zajete"] % ("Sila", "true"), "Server")
            do_trenera()
            otworz_menu()
            time.sleep(0.8)
            a = stan()
            klik("TreningAFKMenu.Okno.Cwiczenia.Sila")
            time.sleep(1.5)
            b = stan()
            luau(KOD["zajete"] % ("Sila", "false"), "Server")
            time.sleep(1.0)
            klik("TreningAFKMenu.Okno.Cwiczenia.Sila")
            c = czekaj_na(lambda: (lambda t: t if t.get("afk") == "Sila" else None)(stan()), 6) or stan()
            zakoncz_trening()
            ka = (a.get("kafle") or {}).get("Sila", {})
            zapisz("B20", {"przed": ka, "po_kliku": {"afk": b.get("afk"), "tytul": b.get("tytul")}, "po_zwolnieniu": c.get("afk")})
            punkt("B20", ka.get("zajete") is True and ka.get("busy") is True and not b.get("afk") and c.get("afk") == "Sila",
                  "kafelek zajęty %s, BUSY %s, klik → trening „%s” (napis „%s”); po zwolnieniu klik → „%s”" % (
                      ka.get("zajete"), ka.get("busy"), b.get("afk"), b.get("tytul"), c.get("afk")))

            # -------------------------------------------------------------- B21 z daleka
            zakoncz_trening()
            daleko = (PODP[0], STOISKO[1] + 3.2, PODP[2] + 25.0)     # uliczka przed Training Center, 25 st od trenera
            przestaw(daleko, PODP)
            luau(KOD["sluchacz"], "Client")
            luau(KOD["wyslij"] % "Pancerz", "Client")
            time.sleep(1.5)
            a = stan()
            zapisz("B21", {"afk": a.get("afk"), "odmowa": a.get("odmowa"), "poz": a.get("poz")})
            punkt("B21", not a.get("afk") and a.get("odmowa") == "daleko",
                  "prośba z %.0f st od trenera: trening „%s”, odmowa „%s”" % (odl_xz(a.get("poz") or daleko, PODP),
                                                                           a.get("afk"), a.get("odmowa")))

            # -------------------------------------------------------------- B22 limit częstości
            do_trenera()
            time.sleep(1.0)
            luau(KOD["wyslij_dwa"] % "Pancerz", "Client")
            time.sleep(0.25)
            a = stan()
            time.sleep(0.8)
            luau(KOD["wyslij"] % "Pancerz", "Client")
            b = czekaj_na(lambda: (lambda t: t if t.get("afk") == "Pancerz" else None)(stan()), 5) or stan()
            zapisz("B22", {"po_dwoch": a.get("afk"), "po_przerwie": b.get("afk")})
            punkt("B22", not a.get("afk") and b.get("afk") == "Pancerz",
                  "zła + poprawna w 0,1 s → „%s” (ma być nic); po 0,8 s → „%s”" % (a.get("afk"), b.get("afk")))

            # -------------------------------------------------------------- B23 w trakcie treningu
            luau(KOD["sluchacz"], "Client")
            time.sleep(0.7)
            luau(KOD["wyslij"] % "Sila", "Client")
            time.sleep(1.2)
            a = stan()
            zakoncz_trening()
            zapisz("B23", {"afk": a.get("afk"), "odmowa": a.get("odmowa")})
            punkt("B23", a.get("afk") == "Pancerz" and a.get("odmowa") == "trening",
                  "prośba w trakcie: trening „%s” (ma zostać Pancerz), odmowa „%s”" % (a.get("afk"), a.get("odmowa")))

            # ============================================================== sklep trenera (27.11.2026)
            def sklep():
                return js(KOD["stan_sklepu"], "Client")

            def profil():
                return js(KOD["profil_sklepu"], "Server")

            def otworz_sklep():
                zakoncz_trening()
                do_trenera()
                otworz_menu()
                klik("TreningAFKMenu.Okno.ZakladkaSklep")
                return czekaj_na(lambda: (lambda s_: s_ if s_.get("sklep") and len(s_.get("kafle") or {}) == 6
                                          and all(v.get("poziom") is not None for v in s_["kafle"].values()) else None)(sklep()), 5) \
                    or sklep()

            def klik_kup(id_, rodzaj):
                luau(KOD["sluchacz_sklepu"], "Client")
                klik("TreningAFKMenu.Okno.Sklep.%s.%s" % (id_, "Ulepsz" if rodzaj == "ulepszenie" else "Wzmacniacz"))
                time.sleep(1.0)
                return sklep(), profil()

            def odstepy(punkty):
                return [round(b_["t"] - a_["t"], 2) for a_, b_ in zip(punkty, punkty[1:])]

            def trenuj(id_, paskow, limit):
                """Trening przez okno (zakładka TRAIN) do `paskow` pełnych pasków → stan sklepu u klienta."""
                zakoncz_trening()
                do_trenera()
                otworz_menu()
                luau(KOD["sluchacz_sklepu"], "Client")
                klik("TreningAFKMenu.Okno.Cwiczenia." + id_)
                czekaj_na(lambda: (lambda t_: t_ if t_.get("afk") == id_ else None)(stan()), 6)
                return czekaj_na(lambda: (lambda s_: s_ if len(s_.get("punkty") or []) >= paskow else None)(sklep()), limit) \
                    or sklep()

            luau(KOD["sluchacz_sklepu"], "Client")
            # -------------------------------------------------------------- S00 zakładka SHOP
            s0 = otworz_sklep()
            pr0 = profil()
            zapisz("S00", {"sklep": s0, "profil": pr0})
            poziomy0 = {k_: v.get("poziom") for k_, v in (s0.get("kafle") or {}).items()}
            punkt("S00", (s0.get("sklep") is True and sorted(poziomy0) == sorted(IDS) and pr0.get("stan") is True)
                  if all(v == 0 for v in poziomy0.values()) else None,
                  "SHOP %s, kafelków %d, poziomy %s, stan gracza %s, tytuł „%s”" % (
                      s0.get("sklep"), len(poziomy0), poziomy0, pr0.get("stan"), s0.get("tytul")))
            # -------------------------------------------------------------- S01 bez Rybek
            luau(KOD["zloto"] % 0, "Server")
            time.sleep(0.6)
            a, pa = klik_kup("Sila", "ulepszenie")
            zapisz("S01", {"sklep": a, "profil": pa})
            punkt("S01", a.get("odmowa") == "za_malo" and a.get("brakuje") == 300 and a["kafle"]["Sila"]["poziom"] == 0
                  and pa.get("gold") == 0,
                  "Gold 0, LV UP Siły → odmowa „%s”, brakuje %s, poziom %s, Gold %s, tytuł „%s”" % (
                      a.get("odmowa"), a.get("brakuje"), a["kafle"]["Sila"]["poziom"], pa.get("gold"), a.get("tytul")))
            # -------------------------------------------------------------- S02 zakup ulepszenia
            luau(KOD["zloto"] % 20000, "Server")
            time.sleep(0.6)
            a, pa = klik_kup("Sila", "ulepszenie")
            dane_ = pa.get("dane") or {}
            zapisz("S02", {"sklep": a, "profil": pa})
            punkt("S02", a["kafle"]["Sila"]["poziom"] == 1 and pa.get("gold") == 19700 and (dane_.get("u") or {}).get("Sila") == 1,
                  "LV UP Siły → poziom %s, Gold %s, profil %s, tytuł „%s”" % (
                      a["kafle"]["Sila"]["poziom"], pa.get("gold"), dane_, a.get("tytul")))
            # -------------------------------------------------------------- S03 ulepszenie zmienia przyrost
            u1 = trenuj("Sila", 3, 25)
            u0 = trenuj("Kondycja", 3, 25)
            zakoncz_trening()
            o1, o0 = odstepy(u1.get("punkty") or []), odstepy(u0.get("punkty") or [])
            zapisz("S03", {"sila_lv1": {"pasek": u1.get("pasek"), "odstepy": o1}, "kondycja_lv0": {"pasek": u0.get("pasek"), "odstepy": o0}})
            sr1 = sum(o1) / len(o1) if o1 else 0
            sr0 = sum(o0) / len(o0) if o0 else 0
            punkt("S03", abs((u1.get("pasek") or 0) - 4 / 1.1) < 0.01 and abs((u0.get("pasek") or 0) - 4) < 0.01
                  and abs(sr1 - 4.36) < 0.45 and abs(sr0 - 4.8) < 0.45,
                  "Siła poz. 1: pasek %s, pełne paski co %.2f s; Kondycja poz. 0: pasek %s, co %.2f s" % (
                      u1.get("pasek"), sr1, u0.get("pasek"), sr0))
            # -------------------------------------------------------------- S04 najwyższy poziom
            otworz_sklep()
            for _ in range(4):
                klik_kup("Sila", "ulepszenie")
                time.sleep(0.3)
            a, pa = klik_kup("Sila", "ulepszenie")
            zapisz("S04", {"sklep": a, "profil": pa})
            punkt("S04", a["kafle"]["Sila"]["poziom"] == 5 and a.get("odmowa") == "maks" and pa.get("gold") == 19700 - 14300
                  and a["kafle"]["Sila"]["ulepsz"] == "MAX",
                  "Siła poziom %s (przycisk „%s”), kolejny klik → odmowa „%s”, Gold %s (ma być %d)" % (
                      a["kafle"]["Sila"]["poziom"], a["kafle"]["Sila"]["ulepsz"], a.get("odmowa"), pa.get("gold"), 19700 - 14300))
            # -------------------------------------------------------------- S05 spam wzmacniacza
            g0 = profil().get("gold")
            luau(KOD["kup_seria"] % "Kondycja", "Client")
            time.sleep(1.5)
            a, pa = sklep(), profil()
            wzm = (pa.get("dane") or {}).get("w") or {}
            zapisz("S05", {"sklep": a, "profil": pa, "gold_przed": g0})
            punkt("S05", pa.get("gold") == (g0 or 0) - 600 and "Constitution" in wzm and 590 <= a["kafle"]["Kondycja"]["wzm"] <= 600,
                  "5 próśb w 0,1 s → Gold %s → %s (jeden zakup = −600), wzmacniacz Kondycji %s s (napis „%s”)" % (
                      g0, pa.get("gold"), a["kafle"]["Kondycja"]["wzm"], a["kafle"]["Kondycja"]["wzm_tekst"]))
            # -------------------------------------------------------------- S06 drugi wzmacniacz tej samej statystyki
            a, pa = klik_kup("Kondycja", "wzmacniacz")
            zapisz("S06", {"sklep": a, "profil": pa})
            ok_z4 = zrzut("04_sklep_wzmacniacz")
            punkt("S06", a.get("odmowa") == "aktywny" and pa.get("gold") == (g0 or 0) - 600,
                  "drugi wzmacniacz Kondycji → odmowa „%s”, Gold %s; zrzut 04_sklep_wzmacniacz %s" % (
                      a.get("odmowa"), pa.get("gold"), ok_z4))
            # -------------------------------------------------------------- S07 ×2 i koniec wzmacniacza
            luau(KOD["czas_wzm"] % 15, "Server")
            try:
                otworz_sklep()
                t_zakupu = time.time()
                klik_kup("Szczescie", "wzmacniacz")
                w1 = trenuj("Szczescie", 1, 12)
                ok_z5 = zrzut("05_panel_wzmacniacz")
                koniec_ = t_zakupu + 16.0
                while time.time() < koniec_:
                    time.sleep(0.5)
                n0 = len(w1.get("punkty") or [])
                w2 = czekaj_na(lambda: (lambda s_: s_ if len(s_.get("punkty") or []) >= n0 + 2 else None)(sklep()), 15) or sklep()
            finally:
                luau(KOD["czas_wzm"] % 600, "Server")
            zakoncz_trening()
            p1 = [x["ile"] for x in (w1.get("punkty") or [])]
            p2 = [x["ile"] for x in (w2.get("punkty") or [])]
            zapisz("S07", {"w_trakcie": {"przyrost_start": w1.get("przyrost"), "wzm_start": w1.get("wzm_start"), "punkty": p1,
                                         "panel": w1.get("panel_wzm"), "napis": w1.get("panel_wzm_tekst")}, "po": p2})
            punkt("S07", w1.get("przyrost") == 2 and p1[:1] == [2] and w1.get("panel_wzm") is True and p2[-1:] == [1],
                  "wzmacniacz 15 s: start +%s/pasek, pierwszy pasek +%s, licznik nad panelem %s („%s”); po końcu ostatni pasek +%s;"
                  " zrzut 05 %s" % (w1.get("przyrost"), p1[:1], w1.get("panel_wzm"), w1.get("panel_wzm_tekst"), p2[-1:], ok_z5))
            # -------------------------------------------------------------- S08 z daleka
            g0 = profil().get("gold")
            przestaw((PODP[0], STOISKO[1] + 3.2, PODP[2] + 25.0), PODP)
            luau(KOD["sluchacz_sklepu"], "Client")
            luau(KOD["kup"] % ("ulepszenie", "Inteligencja"), "Client")
            time.sleep(1.2)
            a, pa = sklep(), profil()
            zapisz("S08", {"odmowa": a.get("odmowa"), "gold": [g0, pa.get("gold")]})
            punkt("S08", a.get("odmowa") == "daleko" and pa.get("gold") == g0,
                  "zakup 25 st od trenera → odmowa „%s”, Gold %s → %s" % (a.get("odmowa"), g0, pa.get("gold")))

            # -------------------------------------------------------------- B30 zamykanie okna
            zam = {}
            do_trenera()
            otworz_menu()
            klik("TreningAFKMenu.Okno.Zamknij")
            zam["X"] = czekaj_na(lambda: (lambda t: t if not t.get("menu") else None)(stan()), 3) is not None
            otworz_menu()
            e = stan().get("ekran") or [1280, 720]
            klik(xy=(12, int(e[1] * 0.5)))
            zam["tlo"] = czekaj_na(lambda: (lambda t: t if not t.get("menu") else None)(stan()), 3) is not None
            otworz_menu()
            klawisz("ButtonB")
            zam["B"] = czekaj_na(lambda: (lambda t: t if not t.get("menu") else None)(stan()), 3) is not None
            otworz_menu()
            przestaw((PODP[0], STOISKO[1] + 3.2, PODP[2] + 23.0), PODP)   # uliczka, 23 st od trenera (> D.trener.zasieg)
            zam["odejscie"] = czekaj_na(lambda: (lambda t: t if not t.get("menu") else None)(stan()), 3) is not None
            zapisz("B30", zam)
            punkt("B30", all(zam.values()), "zamknięte: " + ", ".join("%s %s" % (k_, "tak" if v else "NIE") for k_, v in zam.items()))

            # -------------------------------------------------------------- B40 zrzuty
            ok_z2 = os.path.isfile(os.path.join(wyj, "02_sala_od_wejscia.jpg"))
            # z uliczki na skos (linia widzenia mija studnię od północy): front sali, wolny pas, studnia z lewej
            ok_z3 = zrzut("03_wejscie_placyk", (KOR_A[0] + 6.0, 12.0, KOR_A[2] + 24.0), (KOR_A[0] - 4.0, 4.0, KOR_A[2] - 6.0))
            ok_z6 = zrzut("06_sala_z_gory", ((KOR_A[0] + KOR_B[0]) / 2.0 + 4.0, 62.0, KOR_B[2] + 30.0),
                          ((KOR_A[0] + KOR_B[0]) / 2.0, 0.0, KOR_B[2]))
            punkt("B40", None if bez_zrzutow else bool(ok_z1 and ok_z2 and ok_z3 and ok_z6),
                  "01_okno_trenera %s, 02_sala_od_wejscia %s, 03_wejscie_placyk %s, 06_sala_z_gory %s" % (
                      ok_z1, ok_z2, ok_z3, ok_z6))

            # -------------------------------------------------------------- B50 konsola
            out = call("get_console_output")["text"]
            zle = [w for w in out.splitlines() if "TreningAFK" in w and ("rror" in w or "Script '" in w)]
            zapisz("B50", {"bledy": zle[:20]})
            punkt("B50", not zle, "błędów skryptów treningu AFK w konsoli: %d" % len(zle))
        finally:
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
    zle = [x for x in LISTA if x[1] == "BŁĄD"]
    log("KONIEC: %d punktów, błędów %d" % (len(LISTA), len(zle)))
    return 1 if zle else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
