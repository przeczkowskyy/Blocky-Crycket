# -*- coding: utf-8 -*-
"""Uzupełnienie próby bazaru w trybie Play (17.11.2026, po pierwszym przebiegu testy/proba_play.py): to, czego lista
B01–B15 nie obejmuje, i zrzuty z gry do README.

    python -B swiat/miasteczko_bazar_gra/testy/proba_dodatkowa.py <folder wyjściowy poza repo> [--studio <id>]
           [--bez-zrzutow] [--tylko D01,D04,Z]

Warunki jak w proba_play.py (Studio w trybie Edit, zbudowane MiasteczkoBazar i MiasteczkoBazarGra; do D04 także LasPas
+ LasPasGra). Skrypt sam włącza i wyłącza Play; w Play zmienia tylko stan graczy (haczyki pakietów), atrybuty
WŁASNEGO kontenera (Proba*) i rzeczy lokalne u klienta na czas zrzutu (kamera Scriptable, dymek bez AlwaysOnTop, nazwa
konta na tablicy zamieniona na „Gracz” — repozytorium jest publiczne). D04 na chwilę odpina uchwyt
Sygnaly/PrzeniesDoBazaru W SESJI PLAY (po stronie serwera, przywracany w finally) — w miejscu nic się nie zmienia.

  D01 kamera i sprzedawca na każdym stoisku z postacią (6): kamera nie w części, nie nad stropem, odległość od głowy,
      promień kamera → głowa sprzedawcy trafia sprzedawcę (albo nic), czy własna postać zasłania twarz
  D02 dymki wszystkich 11 miejsc (haczyk klienta „dymek”, kamera za plecami gracza na stoisku): dymek na ekranie,
      ≥ 0,8 st pod stropem, po tej stronie ściany co punkt E (dymek ma AlwaysOnTop, więc zasłony nie liczymy)
  D03 (26.11.2026, zamiast przejść stare ↔ nowe miasteczko) bez przejść do starego miasteczka: w Punkty nie ma
      „E stare_miasteczko” ani „E nowe_miasteczko”, a E o tych id (haczyk „e”) → nieznane_miejsce
  D04 Kamień Powrotu w lesie-pasie prawdziwym E → start bazaru; bez uchwytu bazaru → też start bazaru (zapasowy punkt
      pasa z danych bazaru; od 26.11.2026 nie ma już starego miasteczka ani Workspace/LasTeleport)
  D05 koszt u klienta: części i instancje w Workspace na starcie bazaru, czas klatki (Studio z oknem w tle rysuje
      15 kl./s — przed pomiarem: python -B tools/studio_okno.py --na-wierzch)
  Z   zrzuty z gry (bez filmów): start, uliczka, karczma z dymkiem, karczmarz z bliska, zbrojownia, sklep magiczny,
      zagroda, tablica, portal, Brama Leśna
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

KP = 'local k = workspace:FindFirstChild("MiasteczkoBazarGra") local H = game:GetService("HttpService") '
J = ('local function J(v) local t = typeof(v) if t == "Vector3" then return { v.X, v.Y, v.Z } '
     'elseif t == "table" then local o = {} if #v > 0 then for i, b in ipairs(v) do o[i] = J(b) end '
     'else for a, b in v do o[tostring(a)] = J(b) end end return o '
     'elseif t == "number" and (v ~= v or v == math.huge or v == -math.huge) then return tostring(v) '
     'elseif t == "Instance" then return v:GetFullName() end return v end ')
HRP = 'local hrp = game:GetService("Players"):GetPlayers()[1].Character.HumanoidRootPart '
# szukanie modelu po ścieżce „Workspace/A/B”
SC = ('local function sc(p) local o = game for _, n in string.split(p, "/") do if o == game and n == "Workspace" then o = workspace '
      'else o = o and o:FindFirstChild(n) end end return o end ')
WYNIKI = {}
LISTA = []
STOISKA_Z_POSTACIA = ("karczma", "mistrz_gier", "sklep_magiczny", "zbrojownia", "training_center", "zagroda_petow")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def odl_xz(a, b):
    return math.hypot(a[0] - b[0], a[2] - b[2])


def main():
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    if os.path.commonpath([wyj, REPO]) == REPO:
        sys.exit("Folder wyjściowy ma być poza repozytorium: %s" % wyj)
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    bez_zrzutow = "--bez-zrzutow" in argv
    tylko = set(argv[argv.index("--tylko") + 1].split(",")) if "--tylko" in argv else {"D01", "D02", "D03", "D04", "D05", "Z"}
    os.makedirs(wyj, exist_ok=True)

    sys.path.insert(0, PAKIET)
    import dane as DANE  # noqa: E402
    _, _, D = DANE.dane_z_przypadkami()
    M = D["miejsca"]

    for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"),
               os.path.join(REPO, "swiat", "test_walki2", "testy")):
        sys.path.insert(0, _s)
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
        with open(os.path.join(wyj, "wyniki_dodatkowe.json"), "w", encoding="utf-8") as f:
            json.dump(WYNIKI, f, ensure_ascii=False, indent=1)

    def punkt(kod, ok, opis):
        LISTA.append((kod, "OK" if ok is True else ("BŁĄD" if ok is False else "?"), opis))
        log("%s %s — %s" % (kod, LISTA[-1][1], opis))
        with open(os.path.join(wyj, "lista_dodatkowa.txt"), "w", encoding="utf-8") as f:
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
                    time.sleep(6)

        def js(kod, dm):
            w = json.loads(luau(KP + J + SC + kod, dm))
            return w if isinstance(w, (dict, list)) else {}

        def stan_studio():
            return call("get_studio_state")["text"]

        def nacisnij(klawisz):
            if klawisz == "E":
                # podpowiedź E działa tylko na ekranie — kamera za plecami postaci (po PivotTo patrzy jak wcześniej)
                luau('local c = workspace.CurrentCamera local ch = game:GetService("Players").LocalPlayer.Character '
                     'if c.CameraType == Enum.CameraType.Custom and ch and ch:FindFirstChild("Head") then '
                     'c.CFrame = CFrame.lookAt(ch.Head.Position - ch.HumanoidRootPart.CFrame.LookVector * 12 + Vector3.new(0, 3.5, 0), ch.Head.Position) '
                     'end return "ok"', "Client")
                time.sleep(0.5)
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": klawisz}]})

        def czekaj_na(warunek, limit, co=0.5):
            t0 = time.time()
            while time.time() - t0 < limit:
                w = warunek()
                if w:
                    return w
                time.sleep(co)
            return None

        def przestaw(p, patrz=None, y_plus=3.2):
            x, y, z = p
            px, pz = (patrz[0], patrz[2]) if patrz else (x + 1, z)
            if math.hypot(px - x, pz - z) < 0.1:  # ten sam X, Z → lookAt dałby NaN (postać ginie pod mapą)
                px, pz = x + 1, z
            luau(HRP + 'local p = Vector3.new(%f, %f, %f) hrp.Parent:PivotTo(CFrame.lookAt(p, Vector3.new(%f, p.Y, %f))) '
                       'hrp.AssemblyLinearVelocity = Vector3.zero return "ok"' % (x, y + y_plus, z, px, pz), "Server")

        def poz():
            return js(HRP + 'return H:JSONEncode(J(hrp.Position))', "Server")

        def hak(polecenie, *argi, dm="Server"):
            nazwa = "SterowanieSerwera" if dm == "Server" else "SterowanieKlienta"
            a = ", ".join("nil" if x is None else json.dumps(x, ensure_ascii=False) for x in argi)
            return js('return H:JSONEncode(J(k.Sygnaly.%s:Invoke("%s"%s)))' % (nazwa, polecenie, (", " + a) if a else ""), dm)

        def liczniki():
            return js('local o = {} for _, n in { "ProbaOdrodzen", "ProbaSmierci", "OstatnieE", "OstatniePrzejscie" } do '
                      'o[n] = k:GetAttribute(n) end return H:JSONEncode(o)', "Server")

        def kamera(cam, cel):
            """Kamera skryptowa u klienta: z cam na cel; gdy między nimi jest ściana — kamera tuż przed nią. Promień zaczyna
            się 2,5 st od celu (inaczej trafiał w głowę sprzedawcy albo w samą tablicę i kamera lądowała za nimi)."""
            return js('local c = workspace.CurrentCamera c.CameraType = Enum.CameraType.Scriptable '
                      'local cam, cel = Vector3.new(%f, %f, %f), Vector3.new(%f, %f, %f) '
                      'local par = RaycastParams.new() par.FilterType = Enum.RaycastFilterType.Exclude '
                      'local pom = {} for _, g in game:GetService("Players"):GetPlayers() do if g.Character then table.insert(pom, g.Character) end end '
                      'par.FilterDescendantsInstances = pom '
                      'local od = cel + (cam - cel).Unit * math.min(2.5, (cam - cel).Magnitude * 0.5) '
                      'local r = workspace:Raycast(od, cam - od, par) local przes = false '
                      'if r and r.Instance.Transparency < 1 then cam = r.Position + (cel - cam).Unit * 0.6 przes = true end '
                      'c.CFrame = CFrame.lookAt(cam, cel) return H:JSONEncode({ cam = J(cam), przesunieta = przes, '
                      'sciana = r and r.Instance:GetFullName() or nil })' % (tuple(cam) + tuple(cel)), "Client")

        def kamera_gracza():
            luau('workspace.CurrentCamera.CameraType = Enum.CameraType.Custom return "ok"', "Client")

        def zrzut(nazwa):
            if bez_zrzutow:
                return
            # u klienta (tylko na czas zrzutu): dymki rysowane w świecie (narzędzie zrzutu pomija AlwaysOnTop),
            # nazwa konta na tablicy → „Gracz”
            luau('local p = game:GetService("Players").LocalPlayer '
                 'for _, g in p.PlayerGui:GetChildren() do if g:IsA("BillboardGui") then g.AlwaysOnTop = false end end '
                 'local t = workspace.MiasteczkoBazarGra:FindFirstChild("Tablica") '
                 'if t then for _, l in t:GetDescendants() do if l:IsA("TextLabel") then '
                 'l.Text = string.gsub(l.Text, p.Name, "Gracz") l.Text = string.gsub(l.Text, p.DisplayName, "Gracz") end end end '
                 'return "ok"', "Client")
            time.sleep(0.4)
            nie_usypiaj()
            r = call("screen_capture", {"capture_id": "bazar_" + nazwa}, timeout=150)
            if r["is_error"] or not r.get("images"):
                log("zrzut %s: BŁĄD %s" % (nazwa, r["text"][:120]))
                return
            im = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
            if im.width > 1280:
                im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
            im.save(os.path.join(wyj, nazwa + ".jpg"), "JPEG", quality=85)
            log("zrzut", nazwa)

        def model_info(sciezka):
            return js('local m = sc("%s") if not m then return H:JSONEncode({}) end local cf, r = m:GetBoundingBox() '
                      'return H:JSONEncode({ srodek = J(cf.Position), rozmiar = J(r), przod = J(cf.LookVector), '
                      'glowa = J(cf.Position + Vector3.new(0, r.Y / 2 - 1.3, 0)) })' % sciezka, "Server")

        nie_usypiaj()
        if "Current Studio Mode: Edit" not in stan_studio():
            sys.exit("Studio nie jest w trybie Edit — ta próba sama włącza Play")
        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        uchwyt_odpiety = False
        try:
            czekaj_na(lambda: "Client" in stan_studio() and luau(
                'local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)', "Client") == "true",
                90, 1.0)
            time.sleep(3)
            for _ in range(20):
                w = js('local p = game:GetService("Players").LocalPlayer local g = p.PlayerGui:FindFirstChild("ClassSelect") '
                       'return H:JSONEncode({ ekran = g ~= nil and g.Enabled, kamera = workspace.CurrentCamera.CameraType.Name, '
                       'podpowiedzi = game:GetService("ProximityPromptService").Enabled })', "Client")
                if not w["ekran"] and w["kamera"] == "Custom" and w["podpowiedzi"]:
                    break
                nacisnij("Return")
                time.sleep(1.5)
            luau(KP + 'local g = game:GetService("Players"):GetPlayers()[1] '
                      'local function smierc(c) local h = c:WaitForChild("Humanoid", 5) if h then h.Died:Connect(function() '
                      'k:SetAttribute("ProbaSmierci", (k:GetAttribute("ProbaSmierci") or 0) + 1) end) end end '
                      'if g.Character then task.spawn(smierc, g.Character) end '
                      'g.CharacterAdded:Connect(function(c) k:SetAttribute("ProbaOdrodzen", (k:GetAttribute("ProbaOdrodzen") or 0) + 1) task.spawn(smierc, c) end) '
                      'return "ok"', "Server")
            czekaj_na(lambda: js('return H:JSONEncode({ g = k:GetAttribute("SerwerBazaruGotowy") == true })', "Server")["g"], 40, 1.0)

            # ---------------------------------------------------------------- D01 kamera i sprzedawca
            if "D01" in tylko:
                wynik = {}
                for mid in STOISKA_Z_POSTACIA:
                    m = M[mid]
                    przestaw(m["stoisko"], m["punkt"])
                    time.sleep(1.5)
                    # kamera gracza (Custom) ustawiona za plecami (tak wchodzi gracz) i odwrócona (gracz obraca kamerę
                    # przy ladzie) — moduł kamery przejmuje kierunek, Poppercam sam ją przysuwa
                    wynik[mid] = js(
                        'local c = workspace.CurrentCamera local lp = game:GetService("Players").LocalPlayer local ch = lp.Character '
                        'local g, hrp = ch.Head, ch.HumanoidRootPart local m = sc("%s") local cf, r = m:GetBoundingBox() '
                        'local glowa = cf.Position + Vector3.new(0, r.Y / 2 - 1.3, 0) '
                        'local par = RaycastParams.new() par.FilterType = Enum.RaycastFilterType.Exclude par.FilterDescendantsInstances = { ch } '
                        'local op = OverlapParams.new() op.FilterType = Enum.RaycastFilterType.Exclude op.FilterDescendantsInstances = { ch } '
                        'local out = {} for _, tryb in { "za_plecami", "odwrocona" } do '
                        'local kier = if tryb == "za_plecami" then hrp.CFrame.LookVector else -hrp.CFrame.LookVector '
                        'c.CFrame = CFrame.lookAt(g.Position - kier * 12 + Vector3.new(0, 3.5, 0), g.Position) task.wait(1.2) '
                        'local cp = c.CFrame.Position '
                        'local w, wb = {}, {} for _, q in workspace:GetPartBoundsInRadius(cp, 0.02, op) do if q.Transparency < 1 then '
                        'table.insert(if q.CanCollide then w else wb, q:GetFullName()) end end '
                        'local rg = workspace:Raycast(cp, g.Position - cp, par) '
                        'local zas = rg and not rg.Instance:IsDescendantOf(m) and rg.Instance.Transparency < 0.95 and rg.Instance:GetFullName() or nil '
                        'local rz = workspace:Raycast(cp, glowa - cp, par) '
                        'local up = workspace:Raycast(g.Position, Vector3.new(0, 40, 0), par) '
                        'out[tryb] = { odleglosc = (g.Position - cp).Magnitude, przy_scianie = w, w_ozdobie = wb, zaslona_gracza = zas or false, '
                        'sprzedawca = rz == nil or rz.Instance:IsDescendantOf(m), trafia = rz and rz.Instance:GetFullName() or nil, '
                        'nad_stropem = up ~= nil and cp.Y > up.Position.Y - 0.2 } end '
                        'c.CFrame = CFrame.lookAt(g.Position - hrp.CFrame.LookVector * 12 + Vector3.new(0, 3.5, 0), g.Position) '
                        'return H:JSONEncode(out)' % m["model"], "Client")
                zapisz("D01", wynik)
                # błąd: kamera wewnątrz części BEZ kolizji (ozdoba, sprzedawca — Poppercam ich nie widzi, ekran zasłonięty)
                # albo nad stropem, zasłona gracza przez coś, co nie jest sprzedawcą (oba kierunki), sprzedawca niewidoczny
                # z kamery za plecami. Kamera oparta o część z kolizją (ściana, rama) to zwykła praca Poppercam — tylko opis.
                zle = sorted({mid for mid, w in wynik.items() for t, x in w.items()
                              if x.get("w_ozdobie") or x.get("nad_stropem") or x.get("zaslona_gracza")
                              or (t == "za_plecami" and not x.get("sprzedawca"))})
                punkt("D01", not zle, "kamera za plecami / odwrócona (odległość od głowy, o co się opiera): %s; złe: %s" % (
                    {mid: (round(w["za_plecami"]["odleglosc"], 1), round(w["odwrocona"]["odleglosc"], 1),
                           [x.split(".")[-1] for t in w for x in ((w[t].get("przy_scianie") or []) + (w[t].get("w_ozdobie") or [])
                                                                  + [w[t].get("zaslona_gracza") or ""]) if x])
                     for mid, w in wynik.items()}, zle))

            # ---------------------------------------------------------------- D02 dymki
            if "D02" in tylko:
                wynik = {}
                for mid in D["kolejnosc"]:
                    m = M[mid]
                    przestaw(m["stoisko"], m["punkt"])
                    time.sleep(1.2)
                    # kamera za plecami (tak stoi gracz przed sprzedawcą)
                    luau('local c = workspace.CurrentCamera local ch = game:GetService("Players").LocalPlayer.Character '
                         'c.CFrame = CFrame.lookAt(ch.Head.Position - ch.HumanoidRootPart.CFrame.LookVector * 12 + Vector3.new(0, 3.5, 0), ch.Head.Position) '
                         'return "ok"', "Client")
                    time.sleep(1.0)
                    hak("dymek", mid, m.get("dymek") or mid, dm="Client")
                    time.sleep(0.4)
                    # Dymek ma AlwaysOnTop — rysuje się nad wszystkim, więc „zasłona” nie gra roli. Sprawdzamy: czy jest
                    # na ekranie gracza, czy wisi po tej stronie ściany/stropu co punkt E (promień punkt E → dymek nie
                    # trafia w część z kolizją spoza postaci sprzedawcy) i ile ma miejsca do stropu.
                    model = m.get("model") or ""
                    wynik[mid] = js(
                        'local lp = game:GetService("Players").LocalPlayer local ch = lp.Character local b = nil '
                        'for _, g in lp.PlayerGui:GetChildren() do if g:IsA("BillboardGui") and string.find(g.Name, "%s", 1, true) then b = g end end '
                        'if not b or not b.Adornee then return H:JSONEncode({ brak = true }) end '
                        'local p = b.Adornee.Position + b.StudsOffsetWorldSpace local m = sc("%s") '
                        'local pom = { ch, k } if m then table.insert(pom, m) end '
                        'local par = RaycastParams.new() par.FilterType = Enum.RaycastFilterType.Exclude par.FilterDescendantsInstances = pom '
                        'par.RespectCanCollide = true '
                        'local zr = b.Adornee.Position local rs = workspace:Raycast(zr, p - zr, par) '
                        'local up = workspace:Raycast(p, Vector3.new(0, 30, 0), par) '
                        'local v, na = workspace.CurrentCamera:WorldToViewportPoint(p) '
                        'return H:JSONEncode({ punkt = J(p), za_sciana = rs and rs.Instance:GetFullName() or false, '
                        'do_stropu = up and (up.Position.Y - p.Y) or false, na_ekranie = na, '
                        'odl_kamery = (workspace.CurrentCamera.CFrame.Position - p).Magnitude, '
                        'tekst = b:FindFirstChild("Tekst", true) and b:FindFirstChild("Tekst", true).Text })'
                        % (mid, model), "Client")
                zapisz("D02", wynik)
                zle = [mid for mid, w in wynik.items() if w.get("brak") or w.get("za_sciana") or not w.get("na_ekranie")
                       or (w.get("do_stropu") not in (None, False) and w["do_stropu"] < 0.8)]
                punkt("D02", not zle, "dymki (na ekranie, do stropu, za ścianą): %s; złe: %s" % (
                    {mid: (w.get("na_ekranie"), w.get("do_stropu") and round(w["do_stropu"], 1), w.get("za_sciana") or "")
                     for mid, w in wynik.items()}, zle))

            # ---------------------------------------------------------------- D03 bez przejść do starego miasteczka
            if "D03" in tylko:
                resztki = js('local o = {} for _, n in { "E stare_miasteczko", "E nowe_miasteczko" } do '
                             'if k.Punkty:FindFirstChild(n) then table.insert(o, n) end end return H:JSONEncode(o)', "Server")
                resztki = resztki if isinstance(resztki, list) else []
                odp = {mid: hak("e", mid) for mid in ("stare_miasteczko", "nowe_miasteczko")}
                zapisz("D03", {"resztki": resztki, "e": odp})
                punkt("D03", not resztki and all((w or {}).get("powod") == "nieznane_miejsce" for w in odp.values()),
                      "punkty E starych przejść: %s; E o ich id: %s" % (resztki or "brak",
                                                                        {m: (w or {}).get("powod") for m, w in odp.items()}))

            # ---------------------------------------------------------------- D04 Kamień Powrotu
            if "D04" in tylko:
                jest_las = luau('return tostring(workspace:FindFirstChild("LasPasGra") ~= nil)', "Server") == "true"
                if not jest_las:
                    punkt("D04", None, "brak Workspace/LasPasGra — pominięte")
                else:
                    def do_lasu():
                        # bez przelotu pierwszego wejścia (haczyk pasa „zapomnijPrzelot”: nie startuje sam) — przelot
                        # i to, że nie odpala się drugi raz, sprawdza próba pasa (swiat/las_pas_gra/testy/proba_play.py)
                        luau('local f = workspace.LasPasGra.Sygnaly.SterowaniePasa f:Invoke("zapomnijPrzelot") '
                             'f:Invoke("przenies", nil, "las") return "ok"', "Server")
                        time.sleep(2.5)
                        # przelot pierwszego wejścia (jeśli ruszył) — czekamy na koniec
                        czekaj_na(lambda: js('local g = workspace.LasPasGra.Sygnaly.SterowaniePasa:Invoke("gracz") '
                                             'return H:JSONEncode({ b = g == nil or g.faza == "brak" })', "Server")["b"], 30, 1.0)
                        time.sleep(2.2)

                    kam = js('return H:JSONEncode(J(workspace.LasPasGra.Punkty.KamienPowrotu.Position))', "Server")
                    do_lasu()
                    przestaw([kam[0] + 4, kam[1] - 2.2, kam[2] + 3], kam)
                    time.sleep(1.5)
                    l0 = liczniki()
                    nacisnij("E")
                    pa = czekaj_na(lambda: (lambda q: q if q[0] < 1070 else None)(poz()), 8, 0.3) or poz()
                    d_baz = odl_xz(pa, D["start"]["korzen"])
                    # bez uchwytu bazaru (odpięty tylko w tej sesji Play) → zapasowy punkt pasa = też start bazaru
                    luau('local f = workspace.MiasteczkoBazarGra.Sygnaly.PrzeniesDoBazaru f.Parent = workspace.MiasteczkoBazarGra return "ok"', "Server")
                    uchwyt_odpiety = True
                    time.sleep(3.2)
                    do_lasu()
                    przestaw([kam[0] + 4, kam[1] - 2.2, kam[2] + 3], kam)
                    time.sleep(1.5)
                    nacisnij("E")
                    pb = czekaj_na(lambda: (lambda q: q if q[0] < 1070 else None)(poz()), 8, 0.3) or poz()
                    luau('local f = workspace.MiasteczkoBazarGra:FindFirstChild("PrzeniesDoBazaru") if f then f.Parent = workspace.MiasteczkoBazarGra.Sygnaly end return "ok"', "Server")
                    uchwyt_odpiety = False
                    d_st = odl_xz(pb, D["start"]["korzen"])
                    l1 = liczniki()
                    zapisz("D04", {"kamien": kam, "z_uchwytem": {"pozycja": pa, "od_startu_bazaru": d_baz},
                                   "bez_uchwytu": {"pozycja": pb, "od_startu_bazaru": d_st},
                                   "liczniki": [l0, l1]})
                    punkt("D04", d_baz < 2 and d_st < 3,
                          "Kamień Powrotu (E) → %.1f st od startu bazaru; bez uchwytu bazaru → %.1f st od startu bazaru"
                          % (d_baz, d_st))

            # ---------------------------------------------------------------- D05 koszt u klienta
            if "D05" in tylko:
                hak("przenies", "bazar")
                time.sleep(4)
                ile = js('local n, w = 0, 0 for _, d in workspace:GetDescendants() do w += 1 if d:IsA("BasePart") then n += 1 end end '
                         'local b = workspace:FindFirstChild("MiasteczkoBazar") local nb = 0 if b then for _, d in b:GetDescendants() do '
                         'if d:IsA("BasePart") then nb += 1 end end end '
                         'local RS = game:GetService("RunService") local t = {} local c = RS.RenderStepped:Connect(function(dt) table.insert(t, dt) end) '
                         'task.wait(5) c:Disconnect() table.sort(t) local s = 0 for _, d in t do s += d end '
                         'return H:JSONEncode({ czesci = n, instancje = w, czesci_bazaru = nb, streaming = workspace.StreamingEnabled, '
                         'klatka_sr_ms = s / math.max(1, #t) * 1000, klatka_p95_ms = (t[math.max(1, math.floor(#t * 0.95))] or 0) * 1000, '
                         'fps_studio = workspace:GetRealPhysicsFPS() })', "Client")
                zapisz("D05", ile)
                punkt("D05", None, "u klienta na starcie bazaru: części %s (bazar %s z 4410), instancji %s, streaming %s; klatka śr. %.1f ms, "
                      "p95 %.1f ms (miarodajne tylko przy oknie Studio na wierzchu)" % (ile["czesci"], ile["czesci_bazaru"], ile["instancje"],
                                                                                 ile["streaming"], ile["klatka_sr_ms"], ile["klatka_p95_ms"]))

            # ---------------------------------------------------------------- Z zrzuty z gry
            if "Z" in tylko and not bez_zrzutow:
                st = D["start"]
                hak("przenies", "bazar")
                time.sleep(3.5)
                kamera_gracza()
                time.sleep(1.5)
                zrzut("01_start_bazaru")
                # uliczka sklepów (ujęcie u2 mapy, gracz na starcie)
                kamera([985.0, 11.0, -694.0], [1054.0, 7.0, -701.0])
                zrzut("02_uliczka_sklepow")

                def u_sprzedawcy(mid, nazwa, bok=3.0, odsun=9.0, wys=4.5, dymek=True, blisko=False):
                    m = M[mid]
                    mi = model_info(m["model"])
                    st_ = m["stoisko"]
                    gl = mi["glowa"]
                    # kierunek od sprzedawcy do stoiska (przód sprzedawcy)
                    dx, dz = st_[0] - gl[0], st_[2] - gl[2]
                    dl = math.hypot(dx, dz) or 1.0
                    ux, uz = dx / dl, dz / dl
                    przestaw([st_[0] + uz * bok, st_[1], st_[2] - ux * bok], [gl[0], 0, gl[2]])
                    time.sleep(1.2)
                    if dymek:
                        hak("dymek", mid, m["dymek"], dm="Client")
                        time.sleep(0.3)
                    if blisko:
                        cam = [gl[0] + ux * 6.5, gl[1] + 0.6, gl[2] + uz * 6.5]
                        cel = [gl[0], gl[1] - 0.8, gl[2]]
                    else:
                        cam = [gl[0] + ux * odsun - uz * 2.5, gl[1] + wys - 2.5, gl[2] + uz * odsun + ux * 2.5]
                        cel = [gl[0], gl[1] - 0.6, gl[2]]
                    k_ = kamera(cam, cel)
                    zrzut(nazwa)
                    return k_

                ujecia = {}
                ujecia["karczma"] = u_sprzedawcy("karczma", "03_karczma_dymek", odsun=11.0)
                ujecia["karczmarz"] = u_sprzedawcy("karczma", "04_karczmarz_z_bliska", dymek=False, blisko=True)
                ujecia["zbrojownia"] = u_sprzedawcy("zbrojownia", "05_zbrojownia", odsun=10.0)
                ujecia["sklep_magiczny"] = u_sprzedawcy("sklep_magiczny", "06_sklep_magiczny", odsun=10.0)
                ujecia["zagroda"] = u_sprzedawcy("zagroda_petow", "07_zagroda_petow", odsun=13.0, wys=6.0)
                # tablica z rankingiem: przed powierzchnią po normalnej
                T = D["tablica"]
                c0, n0 = T["srodek"], T["normalna"]
                przestaw([M["tablica"]["stoisko"][0] + 3.0, 0.5, M["tablica"]["stoisko"][2]], c0)
                time.sleep(1.5)
                ujecia["tablica"] = kamera([c0[0] + n0[0] * 7.5, c0[1] + 0.8, c0[2] + n0[2] * 7.5], c0)
                zrzut("08_tablica_ranking")
                # portal krain
                mp = M["portal_krain"]
                przestaw(mp["stoisko"], mp["punkt"])
                time.sleep(1.2)
                ujecia["portal"] = kamera([mp["stoisko"][0] - 5.0, 8.0, mp["stoisko"][2] + 11.0], [mp["punkt"][0], 6.0, mp["punkt"][2]])
                zrzut("09_portal_krain")
                # Brama Leśna
                mb = M["brama_lesna"]
                przestaw(mb["stoisko"], mb["punkt"])
                time.sleep(1.2)
                ujecia["brama"] = kamera([mb["stoisko"][0] - 13.0, 7.0, mb["stoisko"][2] + 6.0], [mb["punkt"][0], 6.0, mb["punkt"][2]])
                zrzut("10_brama_lesna")
                kamera_gracza()
                zapisz("Z", ujecia)
        finally:
            if uchwyt_odpiety:
                try:
                    luau('local f = workspace.MiasteczkoBazarGra:FindFirstChild("PrzeniesDoBazaru") if f then f.Parent = workspace.MiasteczkoBazarGra.Sygnaly end return "ok"', "Server")
                except Exception:  # noqa: BLE001 — i tak zatrzymujemy Play (w miejscu nic się nie zmieniło)
                    pass
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
            for _ in range(60):
                time.sleep(0.5)
                if "Current Studio Mode: Edit" in stan_studio():
                    break
            print("\nLISTA DODATKOWA:")
            for x in LISTA:
                print("  %s %-4s %s" % x)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
