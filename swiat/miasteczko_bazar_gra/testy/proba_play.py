# -*- coding: utf-8 -*-
"""Próba „miasteczka-bazaru w grze” w Roblox Studio (tryb Play). Pierwsze przebiegi 17.11.2026 w nocy (wyniki w
../wyniki/, opis w README pakietu); poprawki po nich opisuje README („Poprawki po próbach w grze”, punkt 5).
Uzupełnienie: testy/proba_dodatkowa.py (kamera odwrócona, dymki 13 miejsc, Kamień Powrotu, koszt, zrzuty do README).

    python -B swiat/miasteczko_bazar_gra/testy/proba_play.py <folder wyjściowy poza repo> [--studio <studio_id>]
           [--bez-zrzutow] [--bez-biegu]

Warunki: Studio w trybie Edit, otwarte miejsce gry (placeId sprawdza cel_studio), zbudowane Workspace/MiasteczkoBazar
(swiat/miasteczko_bazar, tools/studio_buduj.py) i Workspace/MiasteczkoBazarGra (python -B swiat/miasteczko_bazar_gra/
zbuduj.py); najlepiej też TeleportChmury, LasPas + LasPasGra i LasTeleport (portal, Las). Skrypt sam włącza i wyłącza
Play, w trybie Play zmienia tylko atrybuty WŁASNEGO kontenera (DymkiWylaczone, BezDymku, Proba*) i stan graczy
haczykami pakietu; niczego nie zapisuje w miejscu i niczego nie publikuje. Wyniki: <wyj>/wyniki.json, lista kontrolna
na ekranie i w <wyj>/lista.txt, zrzuty <wyj>/<nazwa>.jpg (tylko zrzuty, bez filmów).

LISTA KONTROLNA (każdy punkt kończy się OK / BŁĄD / ? w liście):
  B01 gotowość: SerwerBazaruGotowy, ZgodnoscLogikiBazaru „OK n/n”, Podpowiedzi = 13, KlientBazaruGotowy, punkt
      w starym miasteczku (PunktPowrotuStare), atrybuty Las / Chmury (jest / brak — zapisane)
  B02 start bazaru: haczyk „przenies bazar” → postać ≤ 1,5 st od PunktStartuBazaru, patrzy na +X; podpowiedzi E
      włączone; tabliczka „STARE MIASTECZKO (E)” za plecami
  B03 czasy biegu: ze startu do każdego punktu E (character_navigation, pomiar w grze od ruszenia do 2,5 st od
      stoiska) — porównanie z planem siatki (czasy_biegu.plan) i celami: sklepy ≤ 5 s, portal ≤ 6 s
  B04 E przy każdym sprzedawcy i bramie (prawdziwe E z klawiatury, postać na stoisku twarzą do podpowiedzi):
      serwer OstatnieE = <gracz>:<id>:<akcja>, klient: OknoMiejsca z właściwym id (słuchacz próby), sygnał HUD tam,
      gdzie przypisany (karczma → Quests, sklepy → Shop, zagroda → Pets), dymek „… w budowie”, gdy nic się nie otworzyło
  B05 istniejące okna: które okna otworzyły się od razu (historia klienta „otwarto”) — dziś oczekiwane: żadne okno
      Pawła (Shop / Pets / Quests jeszcze nie istnieją), portal → TeleportChmury Trwa = true
  B06 kamera we wnętrzach: na stoisku karczmy, mistrza gier, maga, zbrojmistrza i trenera, kamera ustawiona za plecami
      — odległość kamery od głowy (domyślnie ok. 12,5; < 6 = kamera ściśnięta) i czy promień kamera → głowa trafia
      w część (obrócona kamera: testy/proba_dodatkowa.py, D01)
  B07 portal → chmury → Las i powrót: E przy portalu → TeleportChmury (Trwa), wybór „las” haczykiem klienta →
      postać w Lesie; potem Otworz → „miasteczko” → gdzie wylądowała (stare miasteczko albo bazar — zależy od wpisu
      w krainy.json, README: jednolinijkowa zmiana)
  B08 Brama Leśna → Las: E na stoisku Bramy Leśnej → postać w Lesie (X ≥ 1066) w ≤ 6 s; bez LasPasGra — dymek
      „Las jeszcze niegotowy”; drugie E zaraz po przejściu → dymek „Chwila…” (blokada czasu)
  B09 stare ↔ nowe miasteczko: E przy „Stare miasteczko (E)” → postać przy PunktPowrotuStare; po 3,2 s E przy
      „Nowe miasteczko (E)” → postać na starcie bazaru; od razu drugie E → „Chwila…”; tabliczka w starym miasteczku
      nie zasłania PortalStart (odległość zapisana)
  B10 tablica: SurfaceGui pokazuje gracza („1. <nazwa> — poz. …”), wiersze = liczba graczy
  B11 działka i lochy: E przy Bramie Twierdzy → „Działka — wkrótce”; E przy wrotach → „Zamknięte”; haczyk
      „lochy true” → BazarLochyOtwarte = true i kłódka niewidoczna TYLKO u klienta (LocalTransparencyModifier = 1,
      na serwerze bez zmian), E → OknoMiejsca("lochy"); „lochy false” przywraca
  B12 niewidzialne ściany: przy każdym z 4 brzegów pola gry marsz 30 st na zewnątrz (Humanoid:MoveTo) i skoki —
      postać zostaje w polu gry (± 1,5 st) i nie spada (y > −5)
  B13 dymek wyłączany atrybutem: DymkiWylaczone = true → E przy zbrojowni bez dymku; BezDymku = "zbrojownia" — też;
      po usunięciu atrybutów dymek wraca
  B14 czas klatki: RenderStepped 8 s na starcie, w karczmie, przy zagrodzie i przy Bramie Leśnej (średnio, p95)
  B15 konsola: bez błędów z [MiasteczkoBazarGra] i bez „error” ze skryptów pakietu
  (ręcznie, poza skryptem: telefon w emulatorze Studio — przycisk E i czytelność dymków; dwóch graczy (Test →
   Clients and Servers, 2) — dymki i lochy tylko u tego, kto nacisnął E, tablica z dwoma wierszami)

ZRZUTY (w <wyj>, 8 sztuk): 01_start_bazar, 02_podpowiedz_zbrojownia, 03_dymek_zbrojmistrz, 04_karczma_kamera,
  05_tablica_ranking, 06_chmury_makieta, 07_las_po_bramie, 08_stare_miasteczko_nowe.
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
# zamiana Vector3 / nieskończoności / instancji na liczby i napisy, żeby JSONEncode nie zawiódł
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


def odl_xz(a, b):
    return math.hypot(a[0] - b[0], a[2] - b[2])


def main():
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    if os.path.commonpath([wyj, REPO]) == REPO:
        sys.exit("Folder wyjściowy ma być poza repozytorium (zrzuty nie trafiają do git): %s" % wyj)
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    bez_zrzutow = "--bez-zrzutow" in argv
    bez_biegu = "--bez-biegu" in argv
    os.makedirs(wyj, exist_ok=True)

    # offline: dane pakietu i plan czasów biegu (bez Studio)
    sys.path.insert(0, PAKIET)
    import dane as DANE  # noqa: E402
    import czasy_biegu  # noqa: E402
    _, _, D = DANE.dane_z_przypadkami()
    M = D["miejsca"]
    plan = czasy_biegu.plan(D) or {}

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
                except Exception as e:  # noqa: BLE001 — Studio czasem chwilę nie odpowiada
                    if i == proby - 1:
                        raise
                    log("luau: ponawiam po błędzie:", str(e)[:200])
                    time.sleep(8)

        def js(kod, dm):
            return json.loads(luau(KP + J + kod, dm))

        def stan_studio():
            return call("get_studio_state")["text"]

        def zrzut(nazwa):
            if bez_zrzutow:
                return
            nie_usypiaj()
            r = call("screen_capture", {"capture_id": "bazar_" + nazwa}, timeout=150)
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

        def atrybuty(nazwy, dm="Server"):
            w = js('local o = {} if not k then return H:JSONEncode({ brak = true }) end '
                   'for _, n in { %s } do o[n] = J(k:GetAttribute(n)) end return H:JSONEncode(o)'
                   % ", ".join('"%s"' % n for n in nazwy), dm)
            # pusta tabela Luau (żaden atrybut nie ustawiony) przychodzi z JSONEncode jako [] — to „nic”, nie lista
            return w if isinstance(w, dict) else {}

        def hak(polecenie, *argi, dm="Server"):
            nazwa = "SterowanieSerwera" if dm == "Server" else "SterowanieKlienta"
            a = ", ".join("nil" if x is None else json.dumps(x, ensure_ascii=False) for x in argi)
            return js('return H:JSONEncode(J(k.Sygnaly.%s:Invoke("%s"%s)))' % (nazwa, polecenie, (", " + a) if a else ""), dm)

        def klient():
            return hak("stan", dm="Client")

        def przestaw(p, patrz=None):
            """Postać na punkcie p (grunt + 3,2), twarzą do patrz (poziomo)."""
            x, y, z = p
            px, pz = (patrz[0], patrz[2]) if patrz else (x + 1, z)
            # stoisko „Stare miasteczko” = jego punkt E (ten sam X, Z): CFrame.lookAt na punkt w tym samym miejscu daje
            # NaN i postać ginie pod mapą (próba 17.11.2026: B09 „przechodziło” dzięki odrodzeniu przy SpawnLocation)
            if math.hypot(px - x, pz - z) < 0.1:
                px, pz = x + 1, z
            luau(HRP + 'local p = Vector3.new(%f, %f, %f) hrp.Parent:PivotTo(CFrame.lookAt(p, Vector3.new(%f, p.Y, %f))) '
                       'hrp.AssemblyLinearVelocity = Vector3.zero return "ok"' % (x, y + 3.2, z, px, pz), "Server")

        def poz():
            return js(HRP + 'return H:JSONEncode(J(hrp.Position))', "Server")

        def nacisnij(klawisz):
            if klawisz == "E":
                kamera_za()
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": klawisz}]})

        def kamera_za():
            """Kamera gracza za plecami postaci. Podpowiedź E pokazuje się (i E działa) tylko, gdy jest na ekranie — po
            PivotTo kamera zostaje skierowana jak przy poprzednim punkcie (próba 17.11.2026: E przy zagrodzie nie działało,
            bo podpowiedź była za kamerą). Gracz, który podchodzi do sprzedawcy, ma ją przed sobą."""
            luau('local c = workspace.CurrentCamera local ch = game:GetService("Players").LocalPlayer.Character '
                 'if c.CameraType == Enum.CameraType.Custom and ch and ch:FindFirstChild("Head") then '
                 'c.CFrame = CFrame.lookAt(ch.Head.Position - ch.HumanoidRootPart.CFrame.LookVector * 12 + Vector3.new(0, 3.5, 0), ch.Head.Position) '
                 'end return "ok"', "Client")
            time.sleep(0.5)

        def czekaj_na(warunek, limit, co=0.5):
            t0 = time.time()
            while time.time() - t0 < limit:
                w = warunek()
                if w:
                    return w
                time.sleep(co)
            return None

        def e_w(mid, czekaj=1.2):
            """Postać na stoisku miejsca twarzą do podpowiedzi, prawdziwe E; → (OstatnieE serwera, ostatni wpis klienta)."""
            m = M[mid]
            przestaw(m["stoisko"], m["punkt"])
            time.sleep(0.9)
            hak("zeruj")
            nacisnij("E")
            time.sleep(czekaj)
            a = atrybuty(["OstatnieE"])
            if (":%s:" % mid) not in str(a.get("OstatnieE")):
                # podpowiedź pokazuje się chwilę po przeniesieniu postaci — drugie E (liczone w wynikach)
                WYNIKI.setdefault("ponowione_E", []).append(mid)
                nacisnij("E")
                time.sleep(czekaj)
                a = atrybuty(["OstatnieE"])
            kl = klient()
            hist = kl.get("historia") or []
            return a.get("OstatnieE"), (hist[-1] if hist else {}), kl

        def klatki(sekundy=8):
            return js('local RS = game:GetService("RunService") local t = {} local c = RS.RenderStepped:Connect(function(dt) '
                      'table.insert(t, dt) end) task.wait(%d) c:Disconnect() table.sort(t) local s = 0 for _, d in t do s += d end '
                      'return H:JSONEncode({ n = #t, sr_ms = s / math.max(1, #t) * 1000, p95_ms = (t[math.max(1, math.floor(#t * 0.95))] or 0) * 1000 })'
                      % sekundy, "Client")

        nie_usypiaj()
        if "Current Studio Mode: Edit" not in stan_studio():
            sys.exit("Studio nie jest w trybie Edit — ta próba sama włącza Play")
        edit = json.loads(luau('local H = game:GetService("HttpService") local k = workspace:FindFirstChild("MiasteczkoBazarGra") '
                               'return H:JSONEncode({ kontener = k ~= nil and k:GetAttribute("Wygenerowane") == true, '
                               'mapa = workspace:FindFirstChild("MiasteczkoBazar") ~= nil, '
                               'chmury = workspace:FindFirstChild("TeleportChmury") ~= nil, '
                               'las = workspace:FindFirstChild("LasPasGra") ~= nil, '
                               'stare = k and k:GetAttribute("PunktStaregoMiasteczka") and { k:GetAttribute("PunktStaregoMiasteczka").X, '
                               'k:GetAttribute("PunktStaregoMiasteczka").Z } or nil })', "Edit"))
        zapisz("edit", edit)
        if not edit["kontener"] or not edit["mapa"]:
            sys.exit("Brak Workspace/MiasteczkoBazarGra albo Workspace/MiasteczkoBazar w trybie Edit: %s" % edit)

        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        try:
            czekaj_na(lambda: "Client" in stan_studio() and luau(
                'local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)', "Client") == "true",
                90, 1.0)
            time.sleep(3)
            # ekran wyboru klasy (src/client/ClassSelectClient) trzyma kamerę i wyłącza podpowiedzi E — Enter jak gracz
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
            # licznik odrodzeń i śmierci postaci (atrybuty WŁASNEGO kontenera, tylko w Play) — pierwsza próba 17.11.2026
            # skończyła B09 przy SpawnLocation bez E: trzeba odróżnić przeniesienie od odrodzenia
            luau(KP + 'local g = game:GetService("Players"):GetPlayers()[1] '
                      'local function smierc(c) local h = c:WaitForChild("Humanoid", 5) if h then h.Died:Connect(function() '
                      'k:SetAttribute("ProbaSmierci", (k:GetAttribute("ProbaSmierci") or 0) + 1) '
                      'k:SetAttribute("ProbaOstatniaSmierc", string.format("%.0f;%.0f;%.0f", c:GetPivot().X, c:GetPivot().Y, c:GetPivot().Z)) end) end end '
                      'if g.Character then task.spawn(smierc, g.Character) end '
                      'g.CharacterAdded:Connect(function(c) k:SetAttribute("ProbaOdrodzen", (k:GetAttribute("ProbaOdrodzen") or 0) + 1) task.spawn(smierc, c) end) '
                      'return "ok"', "Server")
            # słuchacz próby: każde OknoMiejsca zapisuje id w atrybucie WŁASNEGO kontenera (tylko u klienta)
            luau(KP + 'local e = game:GetService("ReplicatedStorage"):WaitForChild("OknoMiejsca", 10) if e then '
                      'e.Event:Connect(function(id) k:SetAttribute("ProbaOkno", id) k:SetAttribute("ProbaOkien", (k:GetAttribute("ProbaOkien") or 0) + 1) end) end '
                      'return tostring(e ~= nil)', "Client")

            # ---------------------------------------------------------------- B01 gotowość
            gotowe = czekaj_na(lambda: (lambda a: a if a.get("SerwerBazaruGotowy") else None)(
                atrybuty(["SerwerBazaruGotowy", "ZgodnoscLogikiBazaru", "Podpowiedzi", "Las", "Chmury", "PunktPowrotuStare",
                          "PunktStartuBazaru", "PunktStaregoMiasteczka", "ZrodloStartuStarego"])), 40, 1.0) or {}
            kl = atrybuty(["KlientBazaruGotowy"], "Client")
            zapisz("B01", {"serwer": gotowe, "klient": kl})
            n = len(D["przypadki"])
            punkt("B01", gotowe.get("ZgodnoscLogikiBazaru") == "OK %d/%d" % (n, n) and gotowe.get("Podpowiedzi") == len(D["kolejnosc"])
                  and kl.get("KlientBazaruGotowy") is True and gotowe.get("PunktPowrotuStare") is not None,
                  "serwer %s | klient %s" % (gotowe, kl))

            # ---------------------------------------------------------------- B02 start bazaru
            w = hak("przenies", "bazar")
            time.sleep(1.5)
            p = poz()
            d = odl_xz(p, D["start"]["korzen"])
            pp = js('local n, wl = 0, 0 for _, c in k.Punkty:GetChildren() do local q = c:FindFirstChild("Podpowiedz") '
                    'if q then n += 1 if q.Enabled then wl += 1 end end end return H:JSONEncode({ n = n, wlaczone = wl })', "Client")
            zrzut("01_start_bazar")
            zapisz("B02", {"przenies": w, "pozycja": p, "odleglosc": d, "podpowiedzi": pp})
            punkt("B02", bool(w.get("ok")) and d <= 1.5 and pp["wlaczone"] == pp["n"] == len(D["kolejnosc"]),
                  "start: %.2f st od PunktStartuBazaru, podpowiedzi %s" % (d, pp))

            # ---------------------------------------------------------------- B03 czasy biegu
            if bez_biegu:
                punkt("B03", None, "pominięte (--bez-biegu)")
            else:
                biegi = {}
                for mid in D["kolejnosc"]:
                    m = M[mid]
                    if not m.get("stoisko"):
                        continue
                    hak("przenies", "bazar")
                    time.sleep(1.2)
                    st = m["stoisko"]
                    luau(KP + HRP + 'k:SetAttribute("ProbaBieg", nil) local s0 = hrp.Position local cel = Vector3.new(%f, hrp.Position.Y, %f) '
                                    'task.spawn(function() local t0, t1 = nil, nil local od = os.clock() while os.clock() - od < 20 do '
                                    'local p = hrp.Position if not t0 and (Vector3.new(p.X, 0, p.Z) - Vector3.new(s0.X, 0, s0.Z)).Magnitude > 0.5 then t0 = os.clock() end '
                                    'if t0 and (Vector3.new(p.X, 0, p.Z) - Vector3.new(cel.X, 0, cel.Z)).Magnitude < 2.5 then t1 = os.clock() break end '
                                    'task.wait() end k:SetAttribute("ProbaBieg", if t0 and t1 then t1 - t0 else -1) end) return "ok"'
                         % (st[0], st[2]), "Server")
                    call("character_navigation", {"datamodel_type": "Client", "x": st[0], "y": st[1] + 3, "z": st[2]}, timeout=60)
                    t = czekaj_na(lambda: atrybuty(["ProbaBieg"]).get("ProbaBieg"), 25, 0.5)
                    pl = plan.get(mid, {})
                    biegi[mid] = {"czas": t, "plan": pl.get("czas"), "cel": pl.get("cel"), "pozycja": poz()}
                zapisz("B03", biegi)
                zle = [mid for mid, b in biegi.items() if not (isinstance(b["czas"], (int, float)) and b["czas"] > 0)
                       or (b["cel"] is not None and b["czas"] > b["cel"] + 0.5)
                       or (b["plan"] is not None and b["czas"] > b["plan"] * 1.5 + 1.0)]
                punkt("B03", not zle, "bieg [s] (plan): %s; poza celem/planem: %s" % (
                    ", ".join("%s %s (%s)" % (mid, round(b["czas"], 2) if isinstance(b["czas"], (int, float)) else b["czas"], b["plan"])
                              for mid, b in biegi.items()), zle))

            # ---------------------------------------------------------------- B04–B05 E przy sprzedawcach i bramach
            okna = {}
            for mid in ("karczma", "mistrz_gier", "sklep_magiczny", "zbrojownia", "training_center", "zagroda_petow", "tablica",
                        "dzialka"):
                if mid == "zbrojownia":
                    m = M[mid]
                    przestaw(m["stoisko"], m["punkt"])
                    time.sleep(1.2)
                    zrzut("02_podpowiedz_zbrojownia")
                luau(KP + 'k:SetAttribute("ProbaOkno", nil) return "ok"', "Client")
                ost, wpis, kl = e_w(mid)
                okno = atrybuty(["ProbaOkno"], "Client").get("ProbaOkno")
                okna[mid] = {"serwer": ost, "zdarzenie": okno, "klient": wpis, "dymki": kl.get("dymki")}
                if mid == "zbrojownia":
                    zrzut("03_dymek_zbrojmistrz")
            zapisz("B04", okna)
            zle = [mid for mid, w in okna.items()
                   if not (str(w["serwer"]).endswith(":%s:okno" % mid) and w["zdarzenie"] == mid
                           and (w["klient"].get("hud") == M[mid].get("hud"))
                           and (w["klient"].get("otwarto") or (w["dymki"] or {}).get(mid) == M[mid]["dymek"]))]
            punkt("B04", not zle, "E → okno (serwer, OknoMiejsca, HUD, dymek) — niezgodne: %s" % zle)
            otwarte = {mid: w["klient"].get("otwarto") for mid, w in okna.items() if w["klient"].get("otwarto")}
            ost, wpis, _ = e_w("portal_krain", 1.5)
            trwa = js('local t = workspace:FindFirstChild("TeleportChmury") return H:JSONEncode({ trwa = t and t:GetAttribute("Trwa") })', "Client")
            if trwa.get("trwa"):
                czekaj_na(lambda: js('local t = workspace:FindFirstChild("TeleportChmury") local s = t.Sygnaly.SterowanieKlienta:Invoke("stan") '
                                     'return H:JSONEncode({ g = s.biezacy and s.biezacy.faza == "wybor" or false })', "Client")["g"], 8, 0.4)
                zrzut("06_chmury_makieta")
                luau('local t = workspace:FindFirstChild("TeleportChmury") t.Sygnaly.SterowanieKlienta:Invoke("rezygnuj") return "ok"', "Client")
                time.sleep(3.5)
            zapisz("B05", {"otwarte_od_razu": otwarte, "portal": {"serwer": ost, "klient": wpis, "chmury_trwa": trwa}})
            punkt("B05", (wpis.get("chmury") == "otwarte") == bool(edit["chmury"]),
                  "okna otwarte od razu: %s; portal → chmury: %s (TeleportChmury %s)" % (otwarte or "żadne", wpis.get("chmury"),
                                                                                       "jest" if edit["chmury"] else "brak"))

            # ---------------------------------------------------------------- B06 kamera we wnętrzach
            kamera = {}
            for mid in ("karczma", "mistrz_gier", "sklep_magiczny", "zbrojownia", "training_center"):
                m = M[mid]
                przestaw(m["stoisko"], m["punkt"])
                time.sleep(0.8)
                # kamera za plecami, jak u gracza, który wszedł do sklepu (bez tego kierunek kamery zostawał z poprzedniego
                # stoiska i wynik zależał od kolejności — pierwsza próba 17.11.2026); Poppercam przysuwa ją sam
                luau('local c = workspace.CurrentCamera local ch = game:GetService("Players").LocalPlayer.Character '
                     'c.CFrame = CFrame.lookAt(ch.Head.Position - ch.HumanoidRootPart.CFrame.LookVector * 12 + Vector3.new(0, 3.5, 0), ch.Head.Position) '
                     'return "ok"', "Client")
                time.sleep(1.2)
                kamera[mid] = js('local c = workspace.CurrentCamera local g = game:GetService("Players").LocalPlayer.Character.Head '
                                 'local par = RaycastParams.new() par.FilterType = Enum.RaycastFilterType.Exclude '
                                 'par.FilterDescendantsInstances = { game:GetService("Players").LocalPlayer.Character } '
                                 'local d = g.Position - c.CFrame.Position local r = workspace:Raycast(c.CFrame.Position, d, par) '
                                 'return H:JSONEncode({ odleglosc = d.Magnitude, zaslona = r and r.Instance:GetFullName() or nil })', "Client")
                if mid == "karczma":
                    zrzut("04_karczma_kamera")
            zapisz("B06", kamera)
            # próg 6 (było 8): przy mistrzu gier kamera za plecami opiera się o ramę drzwi karczmy (część z kolizją,
            # 7,8 st) i widać wszystko — to zwykła praca Poppercam, nie kamera w ścianie. Zasłona = błąd zawsze.
            # Kamerę odwróconą i ozdoby bez kolizji sprawdza testy/proba_dodatkowa.py (D01).
            zle = [mid for mid, w in kamera.items() if w["odleglosc"] < 6 or w.get("zaslona")]
            punkt("B06", not zle, "kamera (odległość od głowy, zasłona): %s" % {
                mid: (round(w["odleglosc"], 1), w.get("zaslona")) for mid, w in kamera.items()})

            # ---------------------------------------------------------------- B07 portal → chmury → Las i powrót
            if not edit["chmury"]:
                punkt("B07", None, "brak Workspace/TeleportChmury — pominięte")
            else:
                hak("przenies", "bazar")
                time.sleep(3.5)
                ost, wpis, _ = e_w("portal_krain", 0.5)
                ok_wybor = czekaj_na(lambda: js('local t = workspace.TeleportChmury local s = t.Sygnaly.SterowanieKlienta:Invoke("stan") '
                                                'return H:JSONEncode({ g = s.biezacy and s.biezacy.faza == "wybor" or false })', "Client")["g"], 8, 0.4)
                wybor_las = js('return H:JSONEncode(J(workspace.TeleportChmury.Sygnaly.SterowanieKlienta:Invoke("wybierz", "las")))', "Client")
                czekaj_na(lambda: not js('return H:JSONEncode({ t = workspace.TeleportChmury:GetAttribute("Trwa") == true })', "Client")["t"], 12, 0.5)
                p_las = poz()
                # pierwsze wejście do Lasu odpala przelot kamery pasa (ok. 2,4 + 13,4 s, postać zakotwiczona) — w tym
                # czasie chmury się nie otworzą („nie_w_wyborze” w pierwszej próbie 17.11.2026); czekamy na koniec
                # (przebieg 02:05: czekanie tylko na „brak” przechodziło, zanim przelot ruszył — rusza po 2,4 s — i przelot
                # startował po powrocie do bazaru, zostawiając kamerę skryptową na B09; haczyk „zapomnijPrzelot” w
                # przebiegu 02:13 zostawiał klienta pasa w oczekiwaniu na przelot — kamera skryptowa od B07 do końca)
                def faza_pasa():
                    return js('local l = workspace:FindFirstChild("LasPasGra") local f = l and l.Sygnaly:FindFirstChild("SterowaniePasa") '
                              'local g = f and f:Invoke("gracz") return H:JSONEncode({ faza = if g then g.faza else "brak", '
                              'widzial = g and g.pamiec and g.pamiec.widzialPrzelotLasu or false })', "Server")
                ruszyl = czekaj_na(lambda: (lambda w: w if w.get("faza") != "brak" else None)(faza_pasa()), 8, 0.4)
                przelot7 = czekaj_na(lambda: (lambda w: w if w.get("faza") == "brak" else None)(faza_pasa()), 30, 1.0)
                przelot7 = {"ruszyl": ruszyl, "koniec": przelot7}
                time.sleep(3.5)
                wybor_m, p_m = None, p_las
                for _ in range(3):
                    luau('workspace.TeleportChmury.Otworz:Fire() return "ok"', "Client")
                    if czekaj_na(lambda: js('local s = workspace.TeleportChmury.Sygnaly.SterowanieKlienta:Invoke("stan") '
                                            'return H:JSONEncode({ g = s.biezacy and s.biezacy.faza == "wybor" or false })', "Client")["g"], 8, 0.4):
                        wybor_m = js('return H:JSONEncode(J(workspace.TeleportChmury.Sygnaly.SterowanieKlienta:Invoke("wybierz", "miasteczko")))', "Client")
                        czekaj_na(lambda: not js('return H:JSONEncode({ t = workspace.TeleportChmury:GetAttribute("Trwa") == true })', "Client")["t"], 12, 0.5)
                        p_m = poz()
                        break
                    time.sleep(3.5)
                w_bazarze = D["bazar"]["pole_x"][0] <= p_m[0] <= D["bazar"]["pole_x"][1] and D["bazar"]["pole_z"][0] <= p_m[2] <= D["bazar"]["pole_z"][1]
                d_start = odl_xz(p_m, D["start"]["korzen"])
                # czy krainy.json przejścia przez chmury ma wpis bazaru (README pakietu: jednolinijkowa zmiana)
                try:
                    with open(os.path.join(REPO, "swiat", "teleport_chmury", "krainy.json"), encoding="utf-8") as f:
                        kr = json.load(f)
                    wpis_bazaru = any((p.get("atrybut") or [None])[0] == "MiasteczkoBazarGra" or p.get("gdy_jest") == "MiasteczkoBazarGra"
                                      for k7 in kr["krainy"] if k7["id"] == "miasteczko" for p in k7["przybycie"])
                except (OSError, ValueError, KeyError):
                    wpis_bazaru = None
                zapisz("B07", {"e": ost, "wybor": ok_wybor, "las": {"wybor": wybor_las, "pozycja": p_las}, "przelot": przelot7,
                               "powrot": {"wybor": wybor_m, "pozycja": p_m, "w_bazarze": w_bazarze, "od_startu": d_start},
                               "wpis_bazaru_w_krainy": wpis_bazaru})
                wrocil = odl_xz(p_m, p_las) > 50
                punkt("B07", bool(ok_wybor) and p_las[0] >= 1066 and wrocil and (w_bazarze and d_start < 3 if wpis_bazaru else not w_bazarze),
                      "portal → chmury → Las (%.0f; %.0f; %.0f) → powrót (%.0f; %.0f; %.0f) %s" % (
                          p_las[0], p_las[1], p_las[2], p_m[0], p_m[1], p_m[2],
                          ("W BAZARZE, %.1f st od startu" % d_start) if w_bazarze else
                          ("w starym miasteczku" if wrocil else "NIE WRÓCIŁ (%s)" % wybor_m)))

            # ---------------------------------------------------------------- B08 Brama Leśna → Las
            hak("przenies", "bazar")
            time.sleep(3.5)
            ost, wpis, _ = e_w("brama_lesna", 0.3)
            p8 = czekaj_na(lambda: (lambda q: q if q[0] >= 1066 else None)(poz()), 6, 0.3)
            dymek_las = (klient().get("dymki") or {}).get("brama_lesna")
            # drugie E zaraz po przejściu (blokada czasu 3 s): od razu, bez zerowania odstępu, haczykiem serwera „e”
            # (ta sama decyzja co po podpowiedzi, bez sprawdzania odległości) — prawdziwe E z ustawieniem kamery i zrzutem
            # trwało za długo i blokada mijała (przebieg 01:58), a powrót postaci pod bramę i znów do Lasu zostawiał
            # podpowiedzi E nieczynne w B09 (przebiegi 02:05, 02:19). Prawdziwe E przy bramie sprawdza pierwsze E wyżej.
            hak("e", "brama_lesna")
            time.sleep(0.5)
            drugie = atrybuty(["OstatnieE"]).get("OstatnieE")
            dymek2 = (klient().get("dymki") or {}).get("brama_lesna")
            if p8:
                zrzut("07_las_po_bramie")
            zapisz("B08", {"e": ost, "w_lesie": p8, "dymek": dymek_las, "drugie": drugie, "dymek2": dymek2, "las": edit["las"]})
            if edit["las"]:
                punkt("B08", p8 is not None and str(drugie).endswith("dymek/za_szybko") and str(dymek2).startswith("Chwila"),
                      "Brama Leśna → %s; drugie E: %s „%s”" % (p8, drugie, dymek2))
            else:
                punkt("B08", str(ost).endswith("dymek/brak_lasu") and dymek_las is not None,
                      "bez LasPasGra: %s „%s”" % (ost, dymek_las))

            # ---------------------------------------------------------------- B09 stare ↔ nowe miasteczko
            hak("przenies", "bazar")
            time.sleep(3.5)
            hak("zeruj")
            przed9 = atrybuty(["ProbaOdrodzen", "ProbaSmierci", "ProbaOstatniaSmierc", "OstatnieE"])
            ost, wpis, _ = e_w("stare_miasteczko", 2.5)
            p_st = poz()
            cel_st = gotowe.get("PunktPowrotuStare")
            d_st = odl_xz(p_st, cel_st) if cel_st else None
            po9 = atrybuty(["ProbaOdrodzen", "ProbaSmierci", "ProbaOstatniaSmierc", "OstatniePrzejscie"])
            zapisz("B09_diagnoza", {"przed": przed9, "po": po9})
            time.sleep(1.0)
            zrzut("08_stare_miasteczko_nowe")
            nowe = js('local c = k.Punkty:FindFirstChild("E nowe_miasteczko") local lt = workspace:FindFirstChild("LasTeleport") '
                      'local ps = lt and lt:FindFirstChild("PortalStart") return H:JSONEncode({ punkt = c and J(c.Position), '
                      'portal = ps and J(ps:GetPivot().Position) })', "Server")
            time.sleep(1.0)
            przestaw([nowe["punkt"][0] + 1.5, nowe["punkt"][1] - 3.5, nowe["punkt"][2] + 1.5], nowe["punkt"])
            time.sleep(0.8)
            nacisnij("E")
            time.sleep(1.5)  # krócej niż odstep_przejsc_s (3 s) — drugie E niżej ma trafić w blokadę czasu
            p_nowe = poz()
            d_nowe = odl_xz(p_nowe, D["start"]["korzen"])
            hak_e = hak("e", "stare_miasteczko")
            zapisz("B09", {"do_starego": {"e": ost, "pozycja": p_st, "odleglosc": d_st}, "nowe": nowe,
                           "do_bazaru": {"pozycja": p_nowe, "odleglosc": d_nowe}, "zaraz_drugie": hak_e})
            od_portalu = odl_xz(nowe["punkt"], nowe["portal"]) if nowe.get("portal") and nowe.get("punkt") else None
            punkt("B09", d_st is not None and d_st < 3 and d_nowe < 2 and hak_e.get("powod") == "za_szybko"
                  and str(po9.get("OstatniePrzejscie")).endswith("stare_miasteczko:ok")
                  and po9.get("ProbaSmierci") == przed9.get("ProbaSmierci"),
                  "do starego: %s st od PunktPowrotuStare; do bazaru: %.1f st od startu; zaraz drugie: %s; tabliczka %s st od PortalStart"
                  % (d_st and round(d_st, 1), d_nowe, hak_e.get("powod"), od_portalu and round(od_portalu, 1)))

            # ---------------------------------------------------------------- B10 tablica
            wiersze = hak("tablica")
            imie = luau('return game:GetService("Players"):GetPlayers()[1].Name', "Server")
            m = M["tablica"]
            przestaw(m["stoisko"], D["tablica"]["srodek"])
            time.sleep(1.5)
            zrzut("05_tablica_ranking")
            zapisz("B10", {"wiersze": wiersze, "gracz": imie})
            punkt("B10", isinstance(wiersze, list) and wiersze and str(wiersze[0]).startswith("1. %s — poz." % imie),
                  "tablica: %s" % (wiersze[:2] if isinstance(wiersze, list) else wiersze))

            # ---------------------------------------------------------------- B11 działka i lochy
            _, _, kd = e_w("dzialka")
            dzialka = (kd.get("dymki") or {}).get("dzialka")
            _, _, kl1 = e_w("lochy")
            zamk = (kl1.get("dymki") or {}).get("lochy")
            hak("lochy", True)
            time.sleep(1.0)
            klodka_k = js('local b = workspace.MiasteczkoBazar.BramaLochow:FindFirstChild("Blokada") local n, u = 0, 0 '
                          'if b then for _, d in b:GetDescendants() do if d:IsA("BasePart") then n += 1 if d.LocalTransparencyModifier > 0.99 then u += 1 end end end end '
                          'return H:JSONEncode({ czesci = n, ukryte = u, atrybut = game:GetService("Players").LocalPlayer:GetAttribute("BazarLochyOtwarte") })', "Client")
            klodka_s = js('local b = workspace.MiasteczkoBazar.BramaLochow:FindFirstChild("Blokada") local u = 0 '
                          'if b then for _, d in b:GetDescendants() do if d:IsA("BasePart") and d.LocalTransparencyModifier > 0.99 then u += 1 end end end '
                          'return H:JSONEncode({ ukryte = u })', "Server")
            luau(KP + 'k:SetAttribute("ProbaOkno", nil) return "ok"', "Client")
            ost_l, _, kl2 = e_w("lochy")
            okno_l = atrybuty(["ProbaOkno"], "Client").get("ProbaOkno")
            hak("lochy", False)
            time.sleep(1.0)
            po = js('local b = workspace.MiasteczkoBazar.BramaLochow:FindFirstChild("Blokada") local u = 0 '
                    'if b then for _, d in b:GetDescendants() do if d:IsA("BasePart") and d.LocalTransparencyModifier > 0.99 then u += 1 end end end '
                    'return H:JSONEncode({ ukryte = u })', "Client")
            zapisz("B11", {"dzialka": dzialka, "lochy_zamkniete": zamk, "klodka_klient": klodka_k, "klodka_serwer": klodka_s,
                           "otwarte": {"e": ost_l, "zdarzenie": okno_l, "dymki": kl2.get("dymki")}, "po_zamknieciu": po})
            punkt("B11", dzialka == "Działka — wkrótce" and zamk == "Zamknięte" and klodka_k["atrybut"] is True
                  and klodka_k["czesci"] > 0 and klodka_k["ukryte"] == klodka_k["czesci"] and klodka_s["ukryte"] == 0
                  and okno_l == "lochy" and po["ukryte"] == 0,
                  "działka „%s”, lochy „%s”, kłódka u klienta %s / serwer %s, po odblokowaniu E → %s" % (
                      dzialka, zamk, klodka_k, klodka_s, okno_l))

            # ---------------------------------------------------------------- B12 niewidzialne ściany
            B = D["bazar"]
            # punkty startowe: osiągalne ze startu i najbliżej każdej ściany (siatka chodzenia mapy, offline);
            # bez numpy/Pillow — Brama Leśna (wschód) i środek placu przy brzegach
            przy = czasy_biegu.punkty_przy_scianach(D) or {
                "zachod": [B["pole_x"][0] + 4, D["start"]["punkt"][1], D["start"]["punkt"][2]],
                "wschod": M["brama_lesna"]["stoisko"],
                "polnoc": [D["start"]["punkt"][0], D["start"]["punkt"][1], D["start"]["punkt"][2] - 14],
                "poludnie": [D["start"]["punkt"][0], D["start"]["punkt"][1], D["start"]["punkt"][2] + 8]}
            kierunki = {"zachod": [-30, 0, 0], "wschod": [30, 0, 0], "polnoc": [0, 0, -30], "poludnie": [0, 0, 30]}
            brzegi = {n: (przy[n], kierunki[n]) for n in kierunki}
            sciany = {}
            for nazwa, (p0, kier) in brzegi.items():
                przestaw(p0)
                time.sleep(0.6)
                sciany[nazwa] = js(HRP + 'local h = hrp.Parent:FindFirstChildOfClass("Humanoid") local cel = hrp.Position + Vector3.new(%f, 0, %f) '
                                         'local miny = hrp.Position.Y for i = 1, 12 do h:MoveTo(cel) h.Jump = true task.wait(0.3) miny = math.min(miny, hrp.Position.Y) end '
                                         'return H:JSONEncode({ pozycja = J(hrp.Position), miny = miny })' % (kier[0], kier[2]), "Server")
            zapisz("B12", sciany)
            zle = [n for n, w in sciany.items() if not (B["pole_x"][0] - 1.5 <= w["pozycja"][0] <= B["pole_x"][1] + 1.5
                                                        and B["pole_z"][0] - 1.5 <= w["pozycja"][2] <= B["pole_z"][1] + 1.5
                                                        and w["miny"] > -5)]
            punkt("B12", not zle, "ściany: %s; poza polem gry: %s" % ({n: [round(x, 1) for x in w["pozycja"]] for n, w in sciany.items()}, zle))

            # ---------------------------------------------------------------- B13 dymek wyłączany atrybutem
            wyniki13 = {}
            for opis, kod in (("DymkiWylaczone", 'k:SetAttribute("DymkiWylaczone", true)'),
                              ("BezDymku", 'k:SetAttribute("DymkiWylaczone", nil) k:SetAttribute("BezDymku", "karczma, zbrojownia")'),
                              ("bez atrybutów", 'k:SetAttribute("DymkiWylaczone", nil) k:SetAttribute("BezDymku", nil)')):
                luau(KP + kod + ' return "ok"', "Server")
                time.sleep(4.0)  # poprzedni dymek gaśnie po D.czasy.dymek_s
                _, wpis, kl = e_w("zbrojownia")
                wyniki13[opis] = {"dymek": wpis.get("dymek"), "widoczny": (kl.get("dymki") or {}).get("zbrojownia")}
            zapisz("B13", wyniki13)
            punkt("B13", wyniki13["DymkiWylaczone"]["dymek"] is False and wyniki13["BezDymku"]["dymek"] is False
                  and wyniki13["bez atrybutów"]["dymek"] is True, "dymek zbrojowni: %s" % wyniki13)

            # ---------------------------------------------------------------- B14 czas klatki
            kl14 = {}
            for nazwa, p14 in (("start", D["start"]["punkt"]), ("karczma", M["karczma"]["stoisko"]),
                               ("zagroda", M["zagroda_petow"]["stoisko"]), ("brama_lesna", M["brama_lesna"]["stoisko"])):
                przestaw(p14)
                time.sleep(2.0)
                kl14[nazwa] = klatki()
            zapisz("B14", kl14)
            punkt("B14", None, "klatka śr./p95 [ms]: %s — ocenia człowiek (Studio z zaciemnionym oknem rysuje wolniej)" % {
                n: (round(w["sr_ms"], 1), round(w["p95_ms"], 1)) for n, w in kl14.items()})

            # ---------------------------------------------------------------- B15 konsola
            kons = call("get_console_output", {}, timeout=60)["text"]
            linie = [x.strip()[:240] for x in kons.splitlines() if "MiasteczkoBazarGra" in x or "rror" in x]
            bledy = [x for x in linie if ("rror" in x or "błąd" in x.lower()) and ("MiasteczkoBazarGra" in x or "Bazaru" in x)]
            zapisz("B15", linie[-60:])
            punkt("B15", not bledy, "%d wierszy [MiasteczkoBazarGra]/error, błędów pakietu: %d %s" % (len(linie), len(bledy), bledy[:3]))
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
