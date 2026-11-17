# -*- coding: utf-8 -*-
"""Próba starego lasu (Workspace/LasPotwory) w trybie PLAY z silnikiem walki v3 i pomijaniem walk (D-078).

    python -B swiat/las_potwory/testy/proba_play.py <folder wyjściowy poza repo> [--studio <studio_id>] [--bez-zrzutow]

Przepisana 17.11.2026 (noc, wdrożenie v3) z wcześniejszej diagnozy podpowiedzi E. Warunki: Studio w trybie Edit,
miejsce gry (placeId sprawdza cel_studio), zbudowane Workspace/TestWalki2 i Workspace/LasPotwory (oba z silnikiem v3,
LasPotwory z Sygnaly/WynikWalki i Sygnaly/ZwolnijPoPominieciu). Skrypt sam włącza i wyłącza Play, niczego nie
zapisuje w miejscu i niczego nie publikuje. Wyniki: <wyj>/wyniki.json i <wyj>/lista.txt, zrzuty <wyj>/<nazwa>.jpg.

LISTA KONTROLNA:
  L1 serwer i klient lasu gotowi (SerwerGotowy, KlientGotowy), ekran wyboru klasy zamknięty Enterem
  L2 pierwsza walka ze slime'em (haczyk „walcz” jak po E): dziennik v3 na ekranie (mana obu stron = liczby),
     bez pomijania (powód pierwsza_walka, bez przycisku), kontrola pasków i many = 0, po walce kamera Custom
  L3 Strażnik Gaju (inny gatunek, też bez pomijania; po nim slime jest „poznany” — następna walka z tego źródła)
  L4 druga walka ze slime'em (bez TestBezSesji): zgoda serwera, przycisk POMIŃ, spacja → wynik, serwer „ok”,
     gracz wolny od razu (NastepnaWalkaOd ≤ teraz + 0,5 s), potwór wolny, następna walka przyjęta od razu
  L5 konsola bez błędów [LasPotwory] i [TestWalki2]
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
from studio_mcp import StudioMCP, StudioError  # noqa: E402
from cel_studio import wybierz_studio  # noqa: E402
from czuwanie import nie_usypiaj  # noqa: E402

K = 'local k = workspace:FindFirstChild("LasPotwory") local H = game:GetService("HttpService") '
SLIMY = (-200, 6, -2310)      # polana slime'ów (strefa z01)
STRAZNIK = (5, 36, -1634)     # Strażnik Gaju stoi w miejscu
WYNIKI, LISTA = {}, []


def log(*a):
    print("[%s]" % time.strftime("%H:%M:%S"), *a, flush=True)


def main():
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    bez_zrzutow = "--bez-zrzutow" in argv
    os.makedirs(wyj, exist_ok=True)

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

        def luau(kod, dm):
            r = call("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=120)
            if r["is_error"]:
                raise StudioError(r["text"][:800])
            return r["text"].strip()

        def js(kod, dm):
            return json.loads(luau(K + kod, dm))

        def stan():
            return call("get_studio_state")["text"]

        def zrzut(nazwa, kamera=None):
            if bez_zrzutow:
                return
            nie_usypiaj()
            time.sleep(0.3)
            a = {"capture_id": "lasstary_" + nazwa}
            if kamera and kamera.get("kamera"):
                a["camera_position"] = kamera["kamera"]
                a["look_at_position"] = kamera["patrz"]
            r = call("screen_capture", a, timeout=150)
            if r["is_error"] or not r.get("images"):
                log("zrzut %s: BŁĄD %s" % (nazwa, (r.get("text") or "")[:120]))
                return
            from PIL import Image
            im = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
            if im.width > 1280:
                im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
            im.save(os.path.join(wyj, nazwa + ".jpg"), "JPEG", quality=85)
            log("zrzut", nazwa)

        def klient():
            return js('return H:JSONEncode(k.Sygnaly.SterowanieKlienta:Invoke("stan"))', "Client")

        def odtw(polecenie):
            return json.loads(luau('local H = game:GetService("HttpService") return H:JSONEncode('
                                   'workspace.TestWalki2.Sygnaly.Sterowanie:Invoke(%s))' % polecenie, "Client"))

        def atr_klient(nazwy):
            return js('local o = {} for _, n in { %s } do o[n] = k:GetAttribute(n) end return H:JSONEncode(o)'
                      % ", ".join('"%s"' % n for n in nazwy), "Client")

        def przestaw(x, y, z):
            luau('local p = game:GetService("Players"):GetPlayers()[1] p.Character:PivotTo(CFrame.new(%f, %f, %f)) '
                 'p.Character.HumanoidRootPart.AssemblyLinearVelocity = Vector3.zero return "ok"' % (x, y, z), "Server")

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

        def najblizszy(gatunek):
            return js('local p = game:GetService("Players"):GetPlayers()[1] local hrp = p.Character.HumanoidRootPart '
                      'local naj, d = nil, 1e9 for _, c in k.Stan:GetChildren() do '
                      'if c:GetAttribute("Gatunek") == "%s" and c:GetAttribute("Stan") ~= "zajety" then '
                      'local o = k.Sygnaly.SterowanieSerwera:Invoke("potwor", c.Name) '
                      'if o then local dd = (o.pozycja - hrp.Position).Magnitude if dd < d then naj, d = o, dd end end end end '
                      'if not naj then return "{}" end '
                      'return H:JSONEncode({ id = naj.id, x = naj.pozycja.X, y = naj.pozycja.Y, z = naj.pozycja.Z, d = d })'
                      % gatunek, "Server")

        def walcz(gatunek, proby=4):
            """Doskok do najbliższego wolnego potwora i haczyk „walcz” (jak po E). → (id, czy walka trwa)"""
            for _ in range(proby):
                m = najblizszy(gatunek)
                if not m.get("id"):
                    time.sleep(2)
                    continue
                przestaw(m["x"] + 1.5, m["y"] + 3.2, m["z"] + 1.5)
                time.sleep(0.8)
                luau(K + 'k:SetAttribute("OstatniaOdmowa", nil) '
                     'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("walcz", "%s"))' % m["id"], "Client")
                if czekaj_na(lambda: klient().get("walka"), 6, 0.5):
                    return m["id"], True
            return None, False

        def v3_teraz():
            so = odtw('"stan"')
            return so, {"mana": [so.get("manaGracz"), so.get("manaWrog")], "pomijanie": so.get("pomijanie"),
                        "powod": so.get("powodPominiecia"), "przycisk": so.get("pomijanieNaEkranie"), "faza": so.get("faza")}

        def do_konca():
            odtw('"przewinDo", 1000')
            time.sleep(2.5)
            odtw('"zamknij"')
            czekaj_na(lambda: not klient().get("walka"), 30, 1.0)
            time.sleep(1.0)

        nie_usypiaj()
        if "Current Studio Mode: Edit" not in stan():
            sys.exit("Studio nie jest w trybie Edit — nie zaczynam.")
        log("Play:", call("start_stop_play", {"is_start": True})["text"][:40])
        try:
            for _ in range(160):
                if "Client" in stan():
                    try:
                        if luau('local p = game:GetService("Players").LocalPlayer local k = workspace:FindFirstChild("LasPotwory") '
                                'return tostring(p ~= nil and p.Character ~= nil and k ~= nil and k:GetAttribute("KlientGotowy") == true)',
                                "Client") == "true":
                            break
                    except StudioError:
                        pass
                time.sleep(0.5)
            # stan gracza (swiat/stan_gracza, 17.11.2026): ta próba sprawdza regułę testową T1 (klasa i poziom z panelu)
            # — bez atrybutu TestBohater bohater byłby z danych gracza; atrybut znika razem z sesją Play
            luau(K + 'k:SetAttribute("TestBohater", true) return "ok"', "Server")
            time.sleep(1.5)
            # ---------------------------------------------------------------- L1
            wybor = {}
            for _ in range(20):
                wybor = json.loads(luau('local p = game:GetService("Players").LocalPlayer local g = p.PlayerGui:FindFirstChild("ClassSelect") '
                                        'return game:GetService("HttpService"):JSONEncode({ ekran = g ~= nil and g.Enabled, '
                                        'kamera = workspace.CurrentCamera.CameraType.Name })', "Client"))
                if not wybor["ekran"] and wybor["kamera"] == "Custom":
                    break
                nacisnij("Return")
                time.sleep(1.5)
            gotowosc = js('return H:JSONEncode({ serwer = k:GetAttribute("SerwerGotowy"), potworow = k:GetAttribute("Potworow"), '
                          'zgodnosc = k:GetAttribute("ZgodnoscLogiki"), wynik = k.Sygnaly:FindFirstChild("WynikWalki") ~= nil, '
                          'zwolnij = k.Sygnaly:FindFirstChild("ZwolnijPoPominieciu") ~= nil })', "Server")
            kl = klient()
            zapisz("L1", {"serwer": gotowosc, "klient": {x: kl.get(x) for x in ("tryb", "widoki", "walka")}, "wybor_klasy": wybor})
            punkt("L1", gotowosc.get("serwer") is True and gotowosc.get("wynik") and gotowosc.get("zwolnij")
                  and not wybor["ekran"] and wybor["kamera"] == "Custom",
                  "serwer %s, klient tryb %s, wybór klasy %s" % (gotowosc, kl.get("tryb"), wybor))

            luau(K + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("bohater", "mag", "auto"))', "Client")
            luau(K + 'k:SetAttribute("TestBezSesji", true) return "ok"', "Server")
            # ---------------------------------------------------------------- L2 pierwsza walka ze slime'em
            przestaw(*SLIMY)
            time.sleep(10)
            sid1, trwa = walcz("lesny_slime")
            l2 = {"id": sid1, "walka": trwa}
            if trwa:
                time.sleep(4)
                so, l2["v3"] = v3_teraz()
                zrzut("walka_slime_v3", so)
                do_konca()
                l2["kontrola"] = atr_klient(["OstatniaNiezgodnoscMany", "OstatniaNiezgodnoscPaskow", "OstatnieBledyObslugi",
                                             "OstatniWynik"])
                l2["kamera"] = luau('return workspace.CurrentCamera.CameraType.Name', "Client")
            zapisz("L2", l2)
            v = l2.get("v3") or {}
            kon = l2.get("kontrola") or {}
            punkt("L2", trwa and all(isinstance(x, (int, float)) for x in v.get("mana", [None]))
                  and v.get("pomijanie") is False and v.get("powod") == "pierwsza_walka" and not v.get("przycisk")
                  and not kon.get("OstatniaNiezgodnoscMany") and not kon.get("OstatniaNiezgodnoscPaskow")
                  and not kon.get("OstatnieBledyObslugi") and l2.get("kamera") == "Custom", str(l2))

            # ---------------------------------------------------------------- L3 Strażnik Gaju
            przestaw(*STRAZNIK)
            time.sleep(10)
            luau(K + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("bohater", "zwiadowca", "auto"))', "Client")
            sid_s, trwa = walcz("straznik_lasu", 3)
            l3 = {"id": sid_s, "walka": trwa}
            if trwa:
                time.sleep(5)
                so, l3["v3"] = v3_teraz()
                zrzut("walka_straznik_v3", so)
                do_konca()
                l3["kontrola"] = atr_klient(["OstatniaNiezgodnoscMany", "OstatniaNiezgodnoscPaskow", "OstatnieBledyObslugi",
                                             "OstatniWynik"])
            zapisz("L3", l3)
            v = l3.get("v3") or {}
            punkt("L3", trwa and v.get("pomijanie") is False and v.get("powod") == "pierwsza_walka"
                  and not (l3.get("kontrola") or {}).get("OstatnieBledyObslugi"), str(l3))

            # ---------------------------------------------------------------- L4 druga walka ze slime'em: pominięcie
            luau(K + 'k:SetAttribute("TestBezSesji", nil) return "ok"', "Server")
            luau(K + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("bohater", "mag", "auto"))', "Client")
            przestaw(*SLIMY)
            time.sleep(10)
            sid2, trwa = walcz("lesny_slime")
            l4 = {"id": sid2, "walka": trwa}
            if trwa:
                l4["zgoda"] = bool(czekaj_na(lambda: odtw('"stan"').get("pomijanie"), 8, 0.5))
                so, l4["przed"] = v3_teraz()
                zrzut("druga_walka_pomin", so)
                nacisnij("Space")
                czekaj_na(lambda: odtw('"stan"').get("faza") in ("wynik", "brak"), 8, 0.4)
                time.sleep(1.2)
                kl = atr_klient(["OstatniaOdpowiedzPominiecia", "OstatnioPominieto", "NastepnaWalkaOd"])
                teraz_s = float(luau('return tostring(workspace:GetServerTimeNow())', "Server"))
                l4["po"] = {"odpowiedz": kl.get("OstatniaOdpowiedzPominiecia"), "pominieto": kl.get("OstatnioPominieto"),
                            "wolna_za_s": round((kl.get("NastepnaWalkaOd") or 0) - teraz_s, 2),
                            "potwor": js('local c = k.Stan:FindFirstChild("%s") return H:JSONEncode({ jest = c ~= nil, '
                                         'stan = c and c:GetAttribute("Stan") or "" })' % sid2, "Server")}
                odtw('"zamknij"')
                czekaj_na(lambda: not klient().get("walka"), 20, 0.5)
                time.sleep(1.0)
                sid3, trwa3 = walcz("lesny_slime", 2)
                l4["nastepna"] = {"id": sid3, "walka": trwa3,
                                  "odmowa": luau(K + 'return tostring(k:GetAttribute("OstatniaOdmowa"))', "Client")}
                if trwa3:
                    time.sleep(1.0)
                    odtw('"pomin", true')
                    time.sleep(1.0)
                    odtw('"zamknij"')
                    czekaj_na(lambda: not klient().get("walka"), 20, 0.5)
            zapisz("L4", l4)
            po = l4.get("po") or {}
            pot = po.get("potwor") or {}
            punkt("L4", trwa and l4.get("zgoda") is True and (l4.get("przed") or {}).get("przycisk") is True
                  and po.get("odpowiedz") == "ok" and po.get("pominieto") is True and po.get("wolna_za_s", 99) <= 0.5
                  and (not pot.get("jest") or pot.get("stan") != "zajety") and (l4.get("nastepna") or {}).get("walka") is True,
                  str(l4))

            # ---------------------------------------------------------------- L5 konsola
            kons = call("get_console_output", {}, timeout=60)["text"]
            # [TestWalki2] pisze tylko ostrzeżenia; [LasPotwory] drukuje też zwykłe „walka …” — liczą się błędy i
            # ostrzeżenia oraz ślady błędów skryptów z obu kontenerów
            zle = [x.strip()[:230] for x in kons.splitlines()
                   if "[TestWalki2]" in x or "Workspace.LasPotwory." in x or "Workspace.TestWalki2." in x
                   or ("[LasPotwory]" in x and any(w in x for w in ("rror", "arn", "BŁĄD", "błąd", "ostrzeż")))]
            zapisz("L5", zle[:20])
            punkt("L5", not zle, "; ".join(zle[:5]))
        finally:
            try:
                luau(K + 'if k then k:SetAttribute("TestBezSesji", nil) end return "ok"', "Server")
            except Exception:  # noqa: BLE001
                pass
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:40])
            for _ in range(60):
                time.sleep(0.5)
                if "Current Studio Mode: Edit" in stan():
                    break
            log("Edit:", "Current Studio Mode: Edit" in stan())
    zle = [x for x in LISTA if x[1] != "OK"]
    log("WYNIK: %d/%d OK%s" % (len(LISTA) - len(zle), len(LISTA), "" if not zle else " — nie: " + ", ".join(x[0] for x in zle)))
    sys.exit(1 if zle else 0)


if __name__ == "__main__":
    main()
