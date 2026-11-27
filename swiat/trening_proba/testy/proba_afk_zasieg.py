# -*- coding: utf-8 -*-
"""Próba zasięgu podpowiedzi E stanowisk treningu AFK w sali Training Center (tryb Play). Nie zmienia miejsca: sama
włącza i wyłącza Play, niczego nie zapisuje i nie publikuje. Ok. 6–8 minut.

    python -B swiat/trening_proba/testy/proba_afk_zasieg.py <folder wyników POZA repo> [--studio <id>] [--zasieg 4.5]
    python -B swiat/trening_proba/testy/proba_afk_zasieg.py --sprawdz     # bez Studio: kawałki Luau w luau_mini

Powód (26.11.2026): przy zasięgu 10 studów E naciśnięte przy jednym stanowisku włączało sąsiednie. Paweł: „4.5 git”.
27.11.2026 rano (diagnoza w Play): zasięg liczy klient w 3-D od korzenia postaci (R15, korzeń ok. 3,54 nad ziemią) do
podpowiedzi — gdy wisiała w macie (0,65), w poziomie zostawało ok. 3,48 st; przy Zręczności rama bieżni wystawała 3,4 st
w stronę przejścia i podnosiła postać; po Kondycji (ławka) Humanoid ok. 1 s jest w FallingDown i przestawienie kończy
się poślizgiem. 27.11.2026 (duża sala, polecenie Pawła): korytarz 9,3 st, maty co 9 st, rekwizyty nie wystają za matę
w stronę korytarza, podpowiedź na zaczepie D.podpowiedzWysokosc nad matą, zejście w korytarz. Kierunek „ku korytarzowi”
każdego stanowiska i oś korytarza próba bierze z swiat/miasteczko_bazar/znaczniki.json (blok trening_afk).
Przed każdym przestawieniem próba czeka, aż postać stoi (stan Humanoida u klienta).

LISTA (OK / BŁĄD / ?):
  A00 w Edit: skrypt serwera ma zasięg z --zasieg (domyślnie 4.5) i podpowiedź na zaczepie; dane: D.podpowiedzWysokosc
  A01 Play: kontener Workspace/TreningAFK, sześć stanowisk w miejscach ze znaczników (±0,05 st), zasięg na żywych
      podpowiedziach, podpowiedź na zaczepie „Podpowiedz” nad matą
  A1x każde stanowisko od korytarza: postać podchodzi od korytarza (od 5,5 st, co 0,2 st, w kierunku „korytarz”) do
      pierwszego miejsca, gdzie klient POKAZUJE podpowiedź tego stanowiska — najpóźniej 3,2 st od środka maty (stoi na
      posadzce ok. 1 st przed matą, zapas ≥ 0,5 st), prawdziwe E włącza TO stanowisko, drugie E kończy; po zejściu postać
      stoi w korytarzu (2,5–4,5 st od środka maty w stronę korytarza) w zwykłym stanie najpóźniej po 3 s
  A2x każde stanowisko z 5,5 st od strony korytarza: prawdziwe E nic nie włącza
  A3x oś korytarza naprzeciw każdej maty: E nic nie włącza (idąc korytarzem nic się samo nie zaczyna)
  A4x marsz z osi korytarza do maty (Humanoid:MoveTo do punktu 3 st od środka maty): postać staje na posadzce (korzeń
      ≤ 0,3 st wyżej niż na posadzce — żaden rekwizyt jej nie podnosi), podpowiedź widać, E włącza to stanowisko
  A50 konsola bez błędów skryptów treningu AFK
"""
import json
import math
import os
import re
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"),
           os.path.join(REPO, "swiat", "test_walki2", "testy")):
    if _s not in sys.path:
        sys.path.insert(0, _s)

GR = 'local gracz = game:GetService("Players"):GetPlayers()[1] '
ZLE_STANY = ("FallingDown", "GettingUp", "Ragdoll", "Physics", "PlatformStanding", "Freefall", "Dead", "brak")
KOD = {
    "edit": ('local s = game:GetService("ServerScriptService").Server:FindFirstChild("TreningAFK") '
             'local d = game:GetService("ReplicatedStorage").Shared:FindFirstChild("TreningAFKDane") '
             'if not s or not d then return "brak" end local z = string.match(s.Source, "MaxActivationDistance = ([%d%.]+)") '
             'local w = string.match(d.Source, "D%.podpowiedzWysokosc = ([%d%.]+)") '
             'local zp = string.find(s.Source, "pp.Parent = zaczep", 1, true) ~= nil '
             'return tostring(z) .. "|" .. tostring(w) .. "|" .. tostring(zp)'),
    "gotowy_klient": 'local p = game:GetService("Players").LocalPlayer return tostring(p ~= nil and p.Character ~= nil)',
    "bez_nazwy": ('local SG = game:GetService("StarterGui") for _, t in { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Chat } do '
                  'pcall(function() SG:SetCoreGuiEnabled(t, false) end) end return "ok"'),
    "wybor_klasy": ('local H = game:GetService("HttpService") local p = game:GetService("Players").LocalPlayer '
                    'local g = p.PlayerGui:FindFirstChild("ClassSelect") local hud = p.PlayerGui:FindFirstChild("HUD") '
                    'return H:JSONEncode({ ekran = g ~= nil and g.Enabled, hud = hud ~= nil and hud.Enabled, '
                    'klasa = p:GetAttribute("Class") or false })'),
    "zmien_klase": 'game:GetService("ReplicatedStorage"):WaitForChild("ChooseClass"):FireServer("%s") return "ok"',
    "stanowiska": ('local H = game:GetService("HttpService") local f = workspace:FindFirstChild("TreningAFK") '
                   'if not f then return "[]" end local o = {} for _, m in ipairs(f:GetChildren()) do '
                   'local mata = m:IsA("Model") and m.PrimaryPart local pp = mata and mata:FindFirstChildWhichIsA("ProximityPrompt", true) '
                   'if pp then local z = pp.Parent table.insert(o, { id = m.Name, x = mata.Position.X, y = mata.Position.Y, '
                   'z = mata.Position.Z, zasieg = pp.MaxActivationDistance, zaczep = z.ClassName .. ":" .. z.Name, '
                   'nad_mata = if z:IsA("Attachment") then z.WorldPosition.Y - mata.Position.Y else 0 }) end end '
                   'return H:JSONEncode(o)'),
    "stan": (GR + 'local H = game:GetService("HttpService") local hrp = gracz.Character and gracz.Character:FindFirstChild("HumanoidRootPart") '
             'return H:JSONEncode({ afk = gracz:GetAttribute("TreningAFK") or false, '
             'x = hrp and hrp.Position.X or 0, y = hrp and hrp.Position.Y or 0, z = hrp and hrp.Position.Z or 0, '
             'kotwica = hrp ~= nil and hrp.Anchored })'),
    "przestaw": (GR + 'local hrp = gracz.Character.HumanoidRootPart hrp.Anchored = false '
                 'hrp.AssemblyLinearVelocity = Vector3.zero '
                 'hrp.CFrame = CFrame.lookAt(Vector3.new(%f, %f, %f), Vector3.new(%f, %f, %f)) return "ok"'),
    # stan Humanoida u klienta (właściciel fizyki postaci; stan po stronie serwera bywa nieaktualny)
    "stan_postaci": ('local p = game:GetService("Players").LocalPlayer local h = p.Character and p.Character:FindFirstChildOfClass("Humanoid") '
                     'return h and (string.gsub(tostring(h:GetState()), "Enum.HumanoidStateType.", "")) or "brak"'),
    # podejście od korytarza: postać co 0,2 st bliżej środka maty (kierunek kx, kz = „korytarz” ze znaczników), aż klient
    # pokaże podpowiedź TEGO stanowiska (domyślny wygląd: BillboardGui w PlayerGui, Adornee = zaczep albo mata)
    "podejscie": ('local H = game:GetService("HttpService") local p = game:GetService("Players").LocalPlayer '
                  'local hrp = p.Character.HumanoidRootPart local m = workspace.TreningAFK:FindFirstChild("%s") '
                  'local mata = m.PrimaryPart local mx, mz, wys, kx, kz = mata.Position.X, mata.Position.Z, %f, %f, %f '
                  'local function widac() for _, g in ipairs(p.PlayerGui:GetDescendants()) do '
                  'if g:IsA("BillboardGui") and g.Adornee ~= nil and (g.Adornee == m or g.Adornee:IsDescendantOf(m)) then '
                  'return true end end return false end '
                  'local function stan(r) hrp.AssemblyLinearVelocity = Vector3.zero '
                  'hrp.CFrame = CFrame.lookAt(Vector3.new(mx + r * kx, wys, mz + r * kz), Vector3.new(mx, wys, mz)) end '
                  'stan(5.5) local t = os.clock() while widac() and os.clock() - t < 2 do task.wait(0.05) end '
                  'for i = 0, 19 do local r = 5.4 - i * 0.2 stan(r) local t0 = os.clock() '
                  'while os.clock() - t0 < 0.3 do task.wait() end '
                  'if widac() then local d = hrp.Position - mata.Position '
                  'return H:JSONEncode({ r = r, x = hrp.Position.X, y = hrp.Position.Y, z = hrp.Position.Z, '
                  'poziom = Vector3.new(d.X, 0, d.Z).Magnitude }) end end '
                  'return H:JSONEncode({ r = false })'),
    # marsz z osi korytarza do punktu przy macie (serwer: Humanoid:MoveTo), potem odczyt korzenia i podpowiedzi
    "marsz": (GR + 'local H = game:GetService("HttpService") local c = gracz.Character local h = c:FindFirstChildOfClass("Humanoid") '
              'local hrp = c.HumanoidRootPart local cel = Vector3.new(%f, hrp.Position.Y, %f) local gotowe = false '
              'local pol = h.MoveToFinished:Connect(function() gotowe = true end) h:MoveTo(cel) local t0 = os.clock() '
              'while not gotowe and os.clock() - t0 < 4 do task.wait(0.05) end pol:Disconnect() task.wait(0.4) '
              'return H:JSONEncode({ x = hrp.Position.X, y = hrp.Position.Y, z = hrp.Position.Z, doszedl = gotowe, '
              'do_celu = Vector3.new(hrp.Position.X - cel.X, 0, hrp.Position.Z - cel.Z).Magnitude })'),
    "widac_podpowiedz": ('local p = game:GetService("Players").LocalPlayer local m = workspace.TreningAFK:FindFirstChild("%s") '
                         'for _, g in ipairs(p.PlayerGui:GetDescendants()) do if g:IsA("BillboardGui") and g.Adornee ~= nil '
                         'and (g.Adornee == m or g.Adornee:IsDescendantOf(m)) then return "tak" end end return "nie"'),
    "kamera_za_plecy": ('local c = workspace.CurrentCamera local p = game:GetService("Players").LocalPlayer '
                        'local hrp = p.Character and p.Character:FindFirstChild("HumanoidRootPart") if not hrp then return "brak" end '
                        'c.CameraType = Enum.CameraType.Custom '
                        'c.CFrame = CFrame.lookAt(hrp.Position - hrp.CFrame.LookVector * 9 + Vector3.new(0, 5, 0), hrp.Position) return "ok"'),
}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def sprawdz_kod():
    """Bez Studio: każdy kawałek Luau z KOD (po podstawieniu zer) parsuje się w tools/walka/luau_mini."""
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


def dane_sali():
    """Stanowiska (świat: środek maty, kierunek ku korytarzowi) i oś korytarza z znaczniki.json mapy."""
    with open(os.path.join(REPO, "swiat", "miasteczko_bazar", "znaczniki.json"), encoding="utf-8-sig") as f:
        T = json.load(f)["trening_afk"]
    return {s["id"]: s for s in T["stanowiska"]}, T["przejscie"]


def na_osi(p, a, b):
    """Rzut punktu p (x, z) na prostą a–b (oś korytarza) — punkt w świecie [x, z]."""
    ax, az, bx, bz = a[0], a[2], b[0], b[2]
    dx, dz = bx - ax, bz - az
    t = ((p[0] - ax) * dx + (p[1] - az) * dz) / (dx * dx + dz * dz)
    return ax + t * dx, az + t * dz


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
    zasieg = float(argv[argv.index("--zasieg") + 1]) if "--zasieg" in argv else 4.5
    os.makedirs(wyj, exist_ok=True)
    ZN, KOR = dane_sali()
    from cel_studio import wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    try:
        from czuwanie import nie_usypiaj  # noqa: E402
    except ImportError:
        def nie_usypiaj():
            return False

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
            return json.loads(luau(kod, dm))

        def czekaj_na(warunek, limit, co):
            koniec = time.time() + limit
            while time.time() < koniec:
                w = warunek()
                if w:
                    return w
                time.sleep(co)
            return None

        def nacisnij(klawisz):
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": klawisz}]})

        def stan():
            return js(KOD["stan"], "Server")

        def czekaj_az_stoi(limit=6.0):
            """Czeka, aż Humanoid u klienta jest w zwykłym stanie (nie przewrócony, nie wstaje, nie spada).
            Zwraca (sekundy czekania, ostatni stan)."""
            t0 = time.time()
            st_ = luau(KOD["stan_postaci"], "Client")
            while st_ in ZLE_STANY and time.time() - t0 < limit:
                time.sleep(0.2)
                st_ = luau(KOD["stan_postaci"], "Client")
            return round(time.time() - t0, 1), st_

        def stoj(p, patrz):
            czekaj_az_stoi()   # przestawienie przewróconej postaci (np. tuż po Kondycji) kończy się poślizgiem
            luau(KOD["przestaw"] % (p[0], p[1], p[2], patrz[0], p[1], patrz[2]), "Server")
            time.sleep(0.9)
            luau(KOD["kamera_za_plecy"], "Client")
            time.sleep(0.6)

        def e_i_stan():
            nacisnij("E")
            time.sleep(1.1)
            return stan()

        def zakoncz_jesli_trwa():
            st = stan()
            if st.get("afk"):
                nacisnij("E")
                time.sleep(1.0)
                st = stan()
            czekaj_az_stoi()
            return st

        nie_usypiaj()
        if "Current Studio Mode: Edit" not in call("get_studio_state")["text"]:
            sys.exit("Studio nie jest w trybie Edit — ta próba sama włącza Play")
        z_edit = luau(KOD["edit"], "Edit").split("|")
        wys_podp = float(z_edit[1]) if len(z_edit) > 1 and z_edit[1] not in ("nil", "") else None
        punkt("A00", z_edit[0] == ("%g" % zasieg) and wys_podp is not None and z_edit[2:] == ["true"],
              "zasięg w skrypcie serwera: %s (oczekiwany %g), D.podpowiedzWysokosc %s, podpowiedź na zaczepie %s" % (
                  z_edit[0], zasieg, wys_podp, z_edit[2:]))

        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        try:
            czekaj_na(lambda: "Client" in call("get_studio_state")["text"] and luau(KOD["gotowy_klient"], "Client") == "true",
                      90, 1.0)
            luau(KOD["bez_nazwy"], "Client")
            time.sleep(3)
            czekaj_na(lambda: js(KOD["wybor_klasy"], "Client").get("ekran"), 30, 1.0)
            wk = js(KOD["wybor_klasy"], "Client")
            for _ in range(10):
                if not wk.get("ekran") and wk.get("klasa") and wk.get("hud"):
                    break
                nacisnij("Return")
                time.sleep(1.5)
                wk = js(KOD["wybor_klasy"], "Client")
            if not wk.get("klasa"):
                luau(KOD["zmien_klase"] % "Warrior", "Client")
                time.sleep(2)
                wk = js(KOD["wybor_klasy"], "Client")
            st = czekaj_na(lambda: (lambda a: a if len(a) >= 6 else None)(js(KOD["stanowiska"], "Server")), 40, 1.0) or []
            zapisz("A01", {"klasa": wk, "stanowiska": st})
            zasiegi = sorted({round(x["zasieg"], 2) for x in st})
            odchyl = max([math.hypot(x["x"] - ZN[x["id"]]["pozycja"][0], x["z"] - ZN[x["id"]]["pozycja"][2])
                          for x in st if x["id"] in ZN] or [99])
            zaczepy = sorted({x["zaczep"] for x in st})
            nad = sorted({round(x["nad_mata"], 2) for x in st})
            punkt("A01", len(st) == 6 and zasiegi == [zasieg] and odchyl <= 0.05 and zaczepy == ["Attachment:Podpowiedz"]
                  and wys_podp is not None and nad == [round(wys_podp, 2)],
                  "stanowisk %d, zasięg %s, odchyłka od znaczników %.3f st, zaczep %s %s st nad matą, klasa %s" % (
                      len(st), zasiegi, odchyl, zaczepy, nad, wk.get("klasa")))
            if len(st) != 6:
                return 1
            wys = st[0]["y"] + 3.2

            # --- A1x: od korytarza — podejście krokami do pierwszego miejsca z widoczną podpowiedzią tego stanowiska
            for i, x in enumerate(st):
                zakoncz_jesli_trwa()
                kor = ZN[x["id"]]["korytarz"]
                czekaj_az_stoi()
                pod = js(KOD["podejscie"] % (x["id"], wys, kor[0], kor[2]), "Client")
                time.sleep(0.3)
                a = e_i_stan() if pod.get("r") else stan()
                b = e_i_stan()
                wstaje, stan_po = czekaj_az_stoi()
                po = stan()
                dx, dz = po["x"] - x["x"], po["z"] - x["z"]
                wzdluz = dx * kor[0] + dz * kor[2]
                w_bok = abs(dx * kor[2] - dz * kor[0])
                zapisz("A1%d" % i, {"id": x["id"], "podejscie": pod, "po_E": a, "po_drugim_E": b,
                                    "po_zejsciu": {"czekanie_s": wstaje, "stan": stan_po, "wzdluz": wzdluz, "w_bok": w_bok}})
                r = pod.get("r")
                gdzie = ("podpowiedź od %.1f st od środka maty (korzeń %.2f nad matą)" % (r, pod["y"] - x["y"])
                         if r else "podpowiedź nie pokazała się do 1,6 st")
                punkt("A1%d" % i, bool(r) and r >= 3.2 and a.get("afk") == x["id"] and not b.get("afk")
                      and stan_po not in ZLE_STANY and wstaje <= 3.0 and 2.5 <= wzdluz <= 4.5 and w_bok <= 1.5,
                      "%s od korytarza: %s; E → „%s”, drugie E → „%s”; zejście %.1f st w stronę korytarza (%.1f w bok), "
                      "postać stoi po %.1f s (%s)" % (x["id"], gdzie, a.get("afk"), b.get("afk"), wzdluz, w_bok, wstaje, stan_po))

            # --- A2x: z 5,5 studa od strony korytarza — nic
            for i, x in enumerate(st):
                zakoncz_jesli_trwa()
                kor = ZN[x["id"]]["korytarz"]
                stoj((x["x"] + 5.5 * kor[0], wys, x["z"] + 5.5 * kor[2]), (x["x"], wys, x["z"]))
                a = e_i_stan()
                zapisz("A2%d" % i, {"id": x["id"], "po_E": a})
                punkt("A2%d" % i, not a.get("afk"), "%s z 5,5 st: E → „%s” (ma być nic)" % (x["id"], a.get("afk")))
                zakoncz_jesli_trwa()

            # --- A3x: oś korytarza naprzeciw maty — nic
            for i, x in enumerate(st):
                zakoncz_jesli_trwa()
                ox, oz = na_osi((x["x"], x["z"]), KOR["przedsionek"], KOR["koniec"])
                stoj((ox, wys, oz), (KOR["koniec"][0], wys, KOR["koniec"][2]))
                a = e_i_stan()
                zapisz("A3%d" % i, {"id": x["id"], "punkt": [ox, oz], "od_maty": math.hypot(ox - x["x"], oz - x["z"]), "po_E": a})
                punkt("A3%d" % i, not a.get("afk"), "oś korytarza naprzeciw %s (%.1f st od maty): E → „%s” (ma być nic)" % (
                    x["id"], math.hypot(ox - x["x"], oz - x["z"]), a.get("afk")))
                zakoncz_jesli_trwa()

            # --- A4x: marsz z osi korytarza do maty (prawdziwy ruch postaci, kolizje rekwizytów)
            for i, x in enumerate(st):
                zakoncz_jesli_trwa()
                kor = ZN[x["id"]]["korytarz"]
                ox, oz = na_osi((x["x"], x["z"]), KOR["przedsionek"], KOR["koniec"])
                stoj((ox, wys, oz), (x["x"], wys, x["z"]))
                y_posadzka = stan()["y"]
                m = js(KOD["marsz"] % (x["x"] + 3.0 * kor[0], x["z"] + 3.0 * kor[2]), "Server")
                widac = luau(KOD["widac_podpowiedz"] % x["id"], "Client") == "tak"
                a = e_i_stan()
                zapisz("A4%d" % i, {"id": x["id"], "marsz": m, "y_posadzka": y_posadzka, "widac": widac, "po_E": a})
                punkt("A4%d" % i, m.get("y", 99) - y_posadzka <= 0.3 and m.get("do_celu", 99) <= 0.8 and widac
                      and a.get("afk") == x["id"],
                      "%s marszem z korytarza: doszedł %s (%.2f st od celu), korzeń %+.2f względem posadzki, podpowiedź %s, "
                      "E → „%s”" % (x["id"], m.get("doszedl"), m.get("do_celu", 99), m.get("y", 99) - y_posadzka,
                                   "widać" if widac else "NIE WIDAĆ", a.get("afk")))
                zakoncz_jesli_trwa()

            out = call("get_console_output")["text"]
            zle = [w for w in out.splitlines() if "TreningAFK" in w and ("Error" in w or "error" in w or "Script '" in w)]
            zapisz("A50", {"bledy": zle[:20]})
            punkt("A50", not zle, "błędów skryptów treningu AFK w konsoli: %d" % len(zle))
        finally:
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
    zle = [x for x in LISTA if x[1] == "BŁĄD"]
    log("KONIEC: %d punktów, błędów %d" % (len(LISTA), len(zle)))
    return 1 if zle else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
