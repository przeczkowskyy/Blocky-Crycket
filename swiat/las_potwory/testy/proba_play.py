# -*- coding: utf-8 -*-
"""Diagnoza: dlaczego przy potworze nie ma podpowiedzi E i walka z haczyka nie rusza.
Uzycie: python -B las_diag.py <korzen repo> <folder wyjsciowy>"""
import io
import json
import os
import sys
import time

REPO, WYJ = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(REPO, "tools"))
sys.path.insert(0, os.path.join(REPO, "swiat", "test_walki2", "testy"))
from studio_mcp import StudioMCP, StudioError, first_studio_id  # noqa: E402
from czuwanie import nie_usypiaj  # noqa: E402
from PIL import Image  # noqa: E402

os.makedirs(WYJ, exist_ok=True)
K = 'local k = workspace:FindFirstChild("LasPotwory") '
JSON = 'local H = game:GetService("HttpService") '
NAJ = (K + JSON + 'local p = game:GetService("Players"):GetPlayers()[1] '
       'local hrp = p.Character.HumanoidRootPart local naj, d = nil, 1e9 '
       'for _, c in k.Stan:GetChildren() do local o = k.Sygnaly.SterowanieSerwera:Invoke("potwor", c.Name) '
       'if o then local dd = (o.pozycja - hrp.Position).Magnitude if dd < d then naj, d = o, dd end end end '
       'return H:JSONEncode({id = naj.id, stan = naj.stan, x = naj.pozycja.X, y = naj.pozycja.Y, z = naj.pozycja.Z, '
       'd = math.floor(d * 10) / 10, hy = math.floor(hrp.Position.Y * 10) / 10})')


def main():
    with StudioMCP(timeout=180) as s:
        s.studios(wait=15)
        sid = first_studio_id(s)

        def call(n, a=None, timeout=None):
            d = dict(a or {})
            d["studio_id"] = sid
            return s.call(n, d, timeout=timeout)

        def luau(kod, dm):
            r = call("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=120)
            if r["is_error"]:
                raise StudioError(r["text"][:800])
            return r["text"].strip()

        def stan():
            return call("get_studio_state")["text"]

        def zrzut(nazwa):
            nie_usypiaj()
            time.sleep(0.5)
            r = call("screen_capture", {"capture_id": "lasf_" + nazwa}, timeout=150)
            if r["is_error"] or not r["images"]:
                print("zrzut %s: BLAD" % nazwa, flush=True)
                return
            im = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
            if im.width > 1280:
                im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
            im.save(os.path.join(WYJ, nazwa + ".jpg"), "JPEG", quality=85)
            print("zrzut", nazwa, flush=True)

        def klient():
            return luau(K + JSON + 'return H:JSONEncode(k.Sygnaly.SterowanieKlienta:Invoke("stan"))', "Client")

        nie_usypiaj()
        time.sleep(2)
        if "Current Studio Mode: Edit" not in stan():
            sys.exit("Studio nie jest w trybie Edit")
        print("Play:", call("start_stop_play", {"is_start": True})["text"][:40], flush=True)
        try:
            for _ in range(160):
                if "Client" in stan():
                    try:
                        if luau('local p = game:GetService("Players").LocalPlayer '
                                'return tostring(p ~= nil and p.Character ~= nil)', "Client") == "true":
                            break
                    except StudioError:
                        pass
                time.sleep(0.5)
            def serwer_potwor(pid):
                return luau(K + JSON + 'local o = k.Sygnaly.SterowanieSerwera:Invoke("potwor", "%s") '
                            'return o and H:JSONEncode({stan = o.stan, przez = o.zajetyPrzez ~= "", wynik = o.wynik}) or "brak"' % pid,
                            "Server")

            def czekaj_koniec(limit=150):
                t0 = time.time()
                while time.time() - t0 < limit:
                    if not json.loads(klient()).get("walka"):
                        break
                    time.sleep(3)
                return round(time.time() - t0)

            # --- Straznik Gaju: stoi w miejscu
            luau('local p = game:GetService("Players"):GetPlayers()[1] '
                 'p.Character:PivotTo(CFrame.new(5, 36, -1634)) return "ok"', "Server")
            time.sleep(10)
            sid_s = luau(K + 'for _, c in k.Stan:GetChildren() do if c:GetAttribute("Gatunek") == "straznik_lasu" then '
                         'return c.Name end end return ""', "Server")
            k = json.loads(klient())
            print("Straznik %s: klient najblizszy=%s podpowiedz=%s widoki=%s" % (sid_s, k.get("najblizszy"), k.get("podpowiedz"),
                                                                                 k.get("widoki")), flush=True)
            zrzut("1_podpowiedz_straznik")
            luau(K + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("bohater", "zwiadowca", "auto"))', "Client")
            print("walcz Straznik:", luau(K + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("walcz", "%s"))' % sid_s,
                                          "Client"), flush=True)
            time.sleep(4)
            print("  po 4 s: klient walka=%s | serwer %s" % (json.loads(klient()).get("walka"), serwer_potwor(sid_s)), flush=True)
            time.sleep(6)
            zrzut("2_walka_straznik")
            print("  walka trwala jeszcze %s s" % czekaj_koniec(), flush=True)
            time.sleep(1.5)
            zrzut("3_wynik_straznik")
            print("  po walce: serwer %s" % serwer_potwor(sid_s), flush=True)
            # --- slime: doskok i od razu walka
            luau('local p = game:GetService("Players"):GetPlayers()[1] '
                 'p.Character:PivotTo(CFrame.new(-200, 6, -2310)) return "ok"', "Server")
            time.sleep(12)
            luau(K + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("bohater", "mag", "auto"))', "Client")
            przed = luau(K + 'local n = 0 for _, c in k.Stan:GetChildren() do if c.Name:sub(1, 4) == "z01-" then n += 1 end end '
                         'return tostring(n)', "Server")
            for i in range(4):
                m = json.loads(luau(NAJ, "Server"))
                luau('local p = game:GetService("Players"):GetPlayers()[1] '
                     'p.Character:PivotTo(CFrame.new(%f, %f, %f)) return "ok"' % (m["x"] + 1.5, m["y"] + 3.2, m["z"] + 1.5), "Server")
                luau(K + 'return tostring(k.Sygnaly.SterowanieKlienta:Invoke("walcz", "%s"))' % m["id"], "Client")
                time.sleep(2.5)
                w = json.loads(klient()).get("walka")
                print("slime %s proba %d: klient walka=%s | serwer %s" % (m["id"], i, w, serwer_potwor(m["id"])), flush=True)
                if w:
                    break
            time.sleep(5)
            zrzut("4_walka_slime")
            print("  walka trwala jeszcze %s s" % czekaj_koniec(), flush=True)
            zrzut("5_wynik_slime")
            print("  slime po walce w Stan: %s; slime'ow z01 przed: %s" % (
                luau(K + 'return tostring(k.Stan:FindFirstChild("%s") ~= nil)' % m["id"], "Server"), przed), flush=True)
            time.sleep(22)
            print("  slime'ow z01 po 22 s: %s" % luau(
                K + 'local n = 0 for _, c in k.Stan:GetChildren() do if c.Name:sub(1, 4) == "z01-" then n += 1 end end '
                'return tostring(n)', "Server"), flush=True)
            print("klient na koniec:", klient()[:200], flush=True)
            kons = call("get_console_output", {}, timeout=60)["text"]
            linie = [x for x in kons.splitlines() if "LasPotwory" in x or "TestWalki2" in x or "rror" in x]
            print("KONSOLA (%d wierszy z LasPotwory/TestWalki2/error):" % len(linie), flush=True)
            for x in linie[-14:]:
                print("> " + x.strip()[:230], flush=True)
        finally:
            print("Stop:", call("start_stop_play", {"is_start": False})["text"][:40], flush=True)
            for _ in range(60):
                time.sleep(0.5)
                if "Current Studio Mode: Edit" in stan():
                    break
            print("Edit:", "Current Studio Mode: Edit" in stan(), flush=True)


main()
