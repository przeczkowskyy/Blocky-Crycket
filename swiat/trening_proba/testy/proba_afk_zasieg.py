# -*- coding: utf-8 -*-
"""Próba zasięgu podpowiedzi E stanowisk treningu AFK w sali Training Center (tryb Play). Nie zmienia miejsca: sama
włącza i wyłącza Play, niczego nie zapisuje i nie publikuje.

    python -B swiat/trening_proba/testy/proba_afk_zasieg.py <folder wyników POZA repo> [--studio <id>] [--zasieg 4.5]

Powód (26.11.2026): przy zasięgu 10 studów E naciśnięte przy jednym stanowisku włączało sąsiednie. Paweł: „4.5 git”.

LISTA (OK / BŁĄD / ?):
  A00 w Edit: skrypt serwera ma zasięg z --zasieg (domyślnie 4.5)
  A01 Play: kontener Workspace/TreningAFK, sześć stanowisk, zasięg podpowiedzi na żywych stanowiskach
  A1x każde stanowisko z przejścia (3 studa od środka maty): prawdziwe E włącza TO stanowisko, drugie E kończy
  A2x każde stanowisko z 5,5 studa: prawdziwe E nic nie włącza
  A3x od frontu rzędu (3 studa przed matą, na osi rzędu): E włącza to stanowisko, nie dalsze
  A40 środek przejścia: E nic nie włącza
  A50 konsola bez błędów skryptów treningu AFK
"""
import json
import os
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
KOD = {
    "edit": ('local s = game:GetService("ServerScriptService").Server:FindFirstChild("TreningAFK") '
             'if not s then return "brak" end local z = string.match(s.Source, "MaxActivationDistance = ([%d%.]+)") '
             'return tostring(z)'),
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
                   'local mata = m:IsA("Model") and m.PrimaryPart local pp = mata and mata:FindFirstChildOfClass("ProximityPrompt") '
                   'if pp then table.insert(o, { id = m.Name, x = mata.Position.X, y = mata.Position.Y, z = mata.Position.Z, '
                   'zasieg = pp.MaxActivationDistance }) end end return H:JSONEncode(o)'),
    "stan": (GR + 'local H = game:GetService("HttpService") local hrp = gracz.Character and gracz.Character:FindFirstChild("HumanoidRootPart") '
             'return H:JSONEncode({ afk = gracz:GetAttribute("TreningAFK") or false, '
             'x = hrp and hrp.Position.X or 0, y = hrp and hrp.Position.Y or 0, z = hrp and hrp.Position.Z or 0, '
             'kotwica = hrp ~= nil and hrp.Anchored })'),
    "przestaw": (GR + 'local hrp = gracz.Character.HumanoidRootPart hrp.Anchored = false '
                 'hrp.AssemblyLinearVelocity = Vector3.zero '
                 'hrp.CFrame = CFrame.lookAt(Vector3.new(%f, %f, %f), Vector3.new(%f, %f, %f)) return "ok"'),
    "kamera_za_plecy": ('local c = workspace.CurrentCamera local p = game:GetService("Players").LocalPlayer '
                        'local hrp = p.Character and p.Character:FindFirstChild("HumanoidRootPart") if not hrp then return "brak" end '
                        'c.CameraType = Enum.CameraType.Custom '
                        'c.CFrame = CFrame.lookAt(hrp.Position - hrp.CFrame.LookVector * 9 + Vector3.new(0, 5, 0), hrp.Position) return "ok"'),
}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def main():
    argv = sys.argv[1:]
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

        def stoj(p, patrz):
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
            return st

        nie_usypiaj()
        if "Current Studio Mode: Edit" not in call("get_studio_state")["text"]:
            sys.exit("Studio nie jest w trybie Edit — ta próba sama włącza Play")
        z_edit = luau(KOD["edit"], "Edit")
        punkt("A00", z_edit == ("%g" % zasieg), "zasięg w skrypcie serwera w Edit: %s (oczekiwany %g)" % (z_edit, zasieg))

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
            punkt("A01", len(st) == 6 and zasiegi == [zasieg],
                  "stanowisk %d, zasięg na żywych podpowiedziach %s, klasa %s" % (len(st), zasiegi, wk.get("klasa")))
            if len(st) != 6:
                return 1
            srodek_x = sum(x["x"] for x in st) / 6.0
            wys = st[0]["y"] + 3.2
            kol = {"L": sorted([x for x in st if x["x"] < srodek_x], key=lambda x: -x["z"]),
                   "P": sorted([x for x in st if x["x"] >= srodek_x], key=lambda x: -x["z"])}   # od frontu (większe Z) w głąb
            zapisz("A01_kolumny", {k: [x["id"] for x in v] for k, v in kol.items()})

            # --- A1x: z przejścia, 3 studa od środka maty
            for i, x in enumerate(st):
                zakoncz_jesli_trwa()
                kier = 1.0 if x["x"] < srodek_x else -1.0
                stoj((x["x"] + 3.0 * kier, wys, x["z"]), (x["x"], wys, x["z"]))
                a = e_i_stan()
                b = e_i_stan()
                zapisz("A1%d" % i, {"id": x["id"], "po_E": a, "po_drugim_E": b})
                punkt("A1%d" % i, a.get("afk") == x["id"] and not b.get("afk"),
                      "%s z przejścia (3 st): E włącza „%s”, drugie E → „%s”" % (x["id"], a.get("afk"), b.get("afk")))

            # --- A2x: z 5,5 studa — nic
            for i, x in enumerate(st):
                zakoncz_jesli_trwa()
                kier = 1.0 if x["x"] < srodek_x else -1.0
                stoj((x["x"] + 5.5 * kier, wys, x["z"]), (x["x"], wys, x["z"]))
                a = e_i_stan()
                zapisz("A2%d" % i, {"id": x["id"], "po_E": a})
                punkt("A2%d" % i, not a.get("afk"), "%s z 5,5 st: E → „%s” (ma być nic)" % (x["id"], a.get("afk")))
                zakoncz_jesli_trwa()

            # --- A3x: od frontu rzędu, 3 studa przed matą na osi rzędu, twarzą w głąb rzędu
            n = 0
            for k in ("L", "P"):
                for j, x in enumerate(kol[k]):
                    zakoncz_jesli_trwa()
                    stoj((x["x"], wys, x["z"] + 3.0), (x["x"], wys, x["z"] - 10.0))
                    a = e_i_stan()
                    zapisz("A3%d" % n, {"id": x["id"], "kolumna": k, "miejsce_w_rzedzie": j, "po_E": a})
                    dalsze = [y["id"] for y in kol[k][j + 1:]]
                    if j == 0:
                        punkt("A3%d" % n, a.get("afk") == x["id"],
                              "%s od frontu rzędu: E włącza „%s” (ma być %s)" % (x["id"], a.get("afk"), x["id"]))
                    else:
                        # między dwiema matami obie bywają w zasięgu — liczy się, że nie włącza się stanowisko DALSZE
                        punkt("A3%d" % n, a.get("afk") not in dalsze,
                              "%s od strony poprzedniej maty: E włącza „%s” (nie może dalszego: %s)" % (
                                  x["id"], a.get("afk"), dalsze))
                    n += 1
                    zakoncz_jesli_trwa()

            # --- A40: środek przejścia
            zakoncz_jesli_trwa()
            srodek_z = sum(x["z"] for x in st) / 6.0
            stoj((srodek_x, wys, srodek_z), (srodek_x, wys, srodek_z - 10.0))
            a = e_i_stan()
            zapisz("A40", a)
            punkt("A40", not a.get("afk"), "środek przejścia: E → „%s” (ma być nic)" % a.get("afk"))
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
    sys.exit(main())
