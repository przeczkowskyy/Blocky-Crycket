# -*- coding: utf-8 -*-
"""Przejście „po ludzku” do Bagna w Roblox Studio (tryb Play) — jedno wejście tak, jak zrobi to gracz. Sama włącza i
wyłącza Play, niczego nie zapisuje ani nie publikuje. Kawałki Luau z testy/proba_play.py (KOD) i kilka własnych.

    python -B swiat/bagno_pas_gra/testy/proba_ludzka.py <folder wyników POZA repo> [--studio <id>]
    python -B swiat/bagno_pas_gra/testy/proba_ludzka.py --sprawdz    # bez Studio: parsuje własne kawałki Luau

Gracz w zwykłym trybie (bez TestBohater; bohater z danych gracza — Workspace/StanGracza), Level = 11, Strażnik lasu
„pokonany” haczykiem lasu (brama otwarta), przelot lasu wyłączony (gracz go już widział):
  H01 przed bramą lasu: brama otwarta, za nią Bagno (zrzut h01)
  H02 prawdziwe chodzenie przez bramę → pierwszy przelot Bagna (zrzuty h02, h03), potem pierwszy widok z Pomostu (h04)
  H03 prawdziwe E przy Rechotku (strefa r1) → walka na poziomie gracza (h05), wynik i karta zamknięta Spacją (h06),
      łup w HUD = atrybuty gracza (h07)
  H04 teleport przez chmury: makieta pokazuje Bagno jako otwarte (h08), wybór Bagna → gracz na Pomoście Bagna
Zrzuty → swiat/bagno_pas_gra/klatki/ (lista graczy i czat schowane); wyniki do podanego folderu.
"""
import io
import json
import os
import re
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import proba_play as PP  # noqa: E402

KOD = dict(PP.KOD)
KOD.update({
    "tele_klient": 'local t = workspace:FindFirstChild("TeleportChmury") return H:JSONEncode(J(t.Sygnaly.SterowanieKlienta:Invoke("%s"%s)))',
    "hud": ('local pg = game:GetService("Players").LocalPlayer.PlayerGui local hud = pg:FindFirstChild("HUD") '
            'local p = hud and hud:FindFirstChild("PlayerPanel") local function t(n) local l = p and p:FindFirstChild(n) '
            'return l and l.Text or false end return H:JSONEncode({ gold = t("Gold"), level = t("Level") })'),
    "kamera_na_brame": ('local cam = workspace.CurrentCamera cam.CameraType = Enum.CameraType.Scriptable '
                        'cam.CFrame = CFrame.lookAt(Vector3.new(%.1f, 9, -688), Vector3.new(%.1f, 4, -700)) return "ok"'
                        % (PP.G["brama_lasu"] - 24, PP.G["brama_lasu"] + 26)),       # brama lasu z krótkiej mapy (D-096)
})


def sprawdz_kod():
    import luau_mini as LM
    bledy = []
    for nazwa in ("tele_klient", "hud", "kamera_na_brame"):
        kod = re.sub(r"%[df]", "0", re.sub(r"%s", "x0", KOD[nazwa].replace('"%s"%s', '"x0", x0')))
        kod = 'local H = game:GetService("HttpService") ' + PP.J + kod
        try:
            LM.Parser(kod, nazwa, LM.Interpreter()).program()
        except LM.BladSkladni as e:
            bledy.append("%s: %s" % (nazwa, e))
    print("sprawdz: %s" % ("OK" if not bledy else bledy))
    return 0 if not bledy else 1


def main():
    argv = sys.argv[1:]
    if "--sprawdz" in argv:
        return sprawdz_kod()
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    if os.path.normcase(wyj).startswith(os.path.normcase(PP.REPO)):
        sys.exit("Folder wyników leży w repozytorium — podaj folder poza repo")
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    os.makedirs(wyj, exist_ok=True)
    os.makedirs(PP.KLATKI, exist_ok=True)
    from cel_studio import wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    from PIL import Image  # noqa: E402
    try:
        from czuwanie import nie_usypiaj  # noqa: E402
    except ImportError:
        def nie_usypiaj():
            return False
    W, LISTA = {}, []

    def zapisz(k, v):
        W[k] = v
        with open(os.path.join(wyj, "wyniki.json"), "w", encoding="utf-8") as f:
            json.dump(W, f, ensure_ascii=False, indent=1)

    def punkt(kod, ok, opis):
        LISTA.append((kod, "OK" if ok is True else ("BŁĄD" if ok is False else "?"), opis))
        PP.log("%s %s — %s" % (kod, LISTA[-1][1], opis))
        with open(os.path.join(wyj, "lista.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join("%s %-4s %s" % x for x in LISTA) + "\n")

    with StudioMCP(timeout=180) as s:
        sid = wybierz_studio(s, studio)

        def call(n, a=None, timeout=None):
            d = dict(a or {})
            d["studio_id"] = sid
            return s.call(n, d, timeout=timeout)

        def luau(kod, dm):
            for i in range(3):
                try:
                    r = call("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=120)
                    if r["is_error"]:
                        raise StudioError(r["text"][:800])
                    return r["text"].strip()
                except Exception:  # noqa: BLE001
                    if i == 2:
                        raise
                    time.sleep(8)

        def js(kod, dm):
            w = json.loads(luau('local H = game:GetService("HttpService") ' + PP.J + kod, dm))
            return {} if w == [] else w

        def zrzut(nazwa):
            nie_usypiaj()
            r = call("screen_capture", {"capture_id": "bagno_" + nazwa}, timeout=150)
            if r["is_error"] or not r.get("images"):
                PP.log("zrzut %s: BŁĄD" % nazwa)
                return
            im = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
            if im.width > 1280:
                im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
            im.save(os.path.join(PP.KLATKI, nazwa + ".jpg"), "JPEG", quality=85)
            PP.log("zrzut", nazwa)

        def czekaj_na(w, limit, co=0.5):
            t0 = time.time()
            while time.time() - t0 < limit:
                x = w()
                if x:
                    return x
                time.sleep(co)
            return None

        def hak(kont, syg, pol, *argi, dm="Server"):
            a = "".join(", " + ("nil" if x is None else json.dumps(x)) for x in argi)
            return js(KOD["hak"] % (kont, syg, pol, a), dm)

        def tele(pol, *argi):
            a = "".join(", " + json.dumps(x) for x in argi)
            return js(KOD["tele_klient"] % (pol, a), "Client")

        def gracz(atr):
            return js(KOD["gracz_atr"] % ", ".join('"%s"' % n for n in atr), "Server")

        def poz():
            return js(KOD["poz"], "Server")

        def nacisnij(k):
            call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": k}]})

        def odtw(p):
            return js(KOD["odtw"] % p, "Client")

        def klient_potworow():
            return js(KOD["klient_potworow"], "Client")

        if "Current Studio Mode: Edit" not in call("get_studio_state")["text"]:
            sys.exit("Studio nie jest w trybie Edit")
        PP.log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        imie = None
        try:
            czekaj_na(lambda: "Client" in call("get_studio_state")["text"] and luau(KOD["gotowy_klient"], "Client") == "true", 90, 1.0)
            imie = luau(KOD["imie"], "Server")
            luau(KOD["bez_nazwy"], "Client")
            czekaj_na(lambda: luau('local k = workspace:FindFirstChild("BagnoPasGra") return tostring(k ~= nil and '
                                   'k:GetAttribute("SerwerPasaGotowy") == true)', "Server") == "true", 60, 1.0)
            for _ in range(20):
                wyb = js(KOD["wybor_klasy"], "Client")
                if not wyb["ekran"] and wyb["kamera"] == "Custom" and wyb["podpowiedzi"]:
                    break
                nacisnij("Return")
                time.sleep(1.5)
            # gracz „po lesie”: poziom 11, Strażnik lasu pokonany (haczyk), przelot lasu już widziany (wyłączony)
            luau(KOD["gracz_ustaw"] % ("Level", "11"), "Server")
            hak("LasPasGra", "SterowaniePasa", "zapomnijPrzelot")
            hak("LasPasGra", "SterowaniePasa", "otworzBrame")
            hak("LasPasGra", "SterowaniePasa", "przenies", None, "przed_brama")
            time.sleep(3.0)
            a0 = gracz(["Class", "Level", "XP", "Gold", "PokonalStraznikaLasu"])
            zapisz("H00", a0)

            # H01 brama otwarta na Bagno
            luau(KOD["kamera_na_brame"], "Client")
            time.sleep(2.0)
            zrzut("h01_brama_lasu_otwarta_na_bagno")
            luau(KOD["kamera_zwykla"], "Client")
            wr = js('local m = workspace.LasPas.BramaBagna.Wrota local kol = 0 for _, d in m:GetDescendants() do '
                    'if d:IsA("BasePart") and d.CanCollide then kol += 1 end end return H:JSONEncode({ kolizja = kol })', "Client")
            punkt("H01", a0.get("PokonalStraznikaLasu") is True and wr.get("kolizja") == 0, "gracz %s, wrota lasu u klienta %s" % (a0, wr))

            # H02 chodzenie przez bramę → przelot Bagna
            call("character_navigation", {"datamodel_type": "Client", "x": PP.G["przybycie"] + 8, "y": 3, "z": -700})
            fazy, t_trwa, zrob = [], None, [(PP.tp(2.0), "h02_przelot_bagna_oczka"), (PP.tp(10.6), "h03_przelot_straznik_topieli")]
            t0 = time.time()
            while time.time() - t0 < 45:
                g = hak("BagnoPasGra", "SterowaniePasa", "gracz")
                if not fazy or fazy[-1] != g.get("faza"):
                    fazy.append(g.get("faza"))
                if g.get("faza") == "trwa" and t_trwa is None:
                    t_trwa = time.time()
                if t_trwa and zrob and time.time() - t_trwa >= zrob[0][0]:
                    zrzut(zrob.pop(0)[1])
                    continue
                if g.get("faza") == "brak" and len(fazy) > 1:
                    break
                time.sleep(0.3)
            time.sleep(2.0)
            zrzut("h04_pierwszy_widok_bagna")
            p2 = poz()
            zapisz("H02", {"fazy": fazy, "pozycja": p2})
            punkt("H02", "trwa" in fazy and fazy[-1] == "brak" and p2[0] > PP.G["brama_lasu"] + 2, "fazy %s, gracz w X %.1f" % (fazy, p2[0]))

            # H03 Rechotek prawdziwym E (zwykły tryb: bohater z danych gracza)
            przed = {"gracz": gracz(["Level", "XP", "Gold"]), "stan": js(KOD["kont_atr"] % ("StanGracza", '"LicznikLupow", "OstatniLup"'), "Server")}
            walka, cel = False, {}
            for _ in range(8):
                cel = js(KOD["potwor_w_strefie"] % "r1", "Server")
                if not cel.get("id"):
                    time.sleep(2)
                    continue
                p = cel["p"]
                call("character_navigation", {"datamodel_type": "Client", "x": p[0] - 4, "y": 3, "z": p[2]})
                time.sleep(1.0)
                pp = js(KOD["podpowiedz"], "Client")
                if pp.get("podpowiedz"):
                    nacisnij("E")
                    if czekaj_na(lambda: klient_potworow().get("walka"), 5, 0.4):
                        walka = True
                        break
            if walka:
                time.sleep(4.0)
                zrzut("h05_walka_z_rechotkiem")
                czekaj_na(lambda: odtw('"stan"').get("faza") == "wynik", 90, 1.0)
                time.sleep(1.5)
                zrzut("h06_wynik_walki")
                nacisnij("Space")
                czekaj_na(lambda: not klient_potworow().get("walka"), 20, 0.5)
                time.sleep(2.5)
                zrzut("h07_hud_po_walce")
            po = {"gracz": gracz(["Level", "XP", "Gold"]), "stan": js(KOD["kont_atr"] % ("StanGracza", '"LicznikLupow", "OstatniLup"'), "Server"),
                  "walka": js(KOD["kont_atr"] % ("BagnoPasGra", '"SerwerOstatniaWalka"'), "Server"), "hud": js(KOD["hud"], "Client")}
            zapisz("H03", {"cel": cel, "walka": walka, "przed": przed, "po": po})
            ow = str(po["walka"].get("SerwerOstatniaWalka") or "")
            m = re.search(r"/(\w+)/(\w+)→(\d+)/(\w+)$", ow)
            hud_ok = str(po["hud"].get("gold")).replace(" ", "") == str(po["gracz"].get("Gold")) and str(po["hud"].get("level")) == str(po["gracz"].get("Level"))
            punkt("H03", walka and bool(m) and int(m.group(3)) == (przed["gracz"].get("Level") or 0)
                  and (po["stan"].get("LicznikLupow") or 0) > (przed["stan"].get("LicznikLupow") or 0) and hud_ok,
                  "walka %s; łup %s; Gold %s→%s, XP %s→%s, Level %s→%s; HUD %s" % (
                      ow, po["stan"].get("OstatniLup"), przed["gracz"].get("Gold"), po["gracz"].get("Gold"), przed["gracz"].get("XP"),
                      po["gracz"].get("XP"), przed["gracz"].get("Level"), po["gracz"].get("Level"), po["hud"]))

            # H04 teleport przez chmury: Bagno otwarte, wybór Bagna
            tele("otworz")
            time.sleep(6.0)          # wejście w chmury 1,1 s + wyłonienie makiety 1,0 s (krainy.json, czasy) z zapasem
            st = tele("stan")
            tele("kursor", "bagno")
            time.sleep(1.0)
            zrzut("h08_mapa_krain_bagno_otwarte")
            wyb = tele("wybierz", "bagno")
            time.sleep(9.0)
            p4 = poz()
            zapisz("H04", {"stan": st, "wybor": wyb, "pozycja": p4})
            punkt("H04", "bagno" not in (st.get("zamkniete") or ["?"]) and wyb.get("ok") is True and abs(p4[0] - PP.G["przybycie"]) < 6,
                  "zamknięte na makiecie %s, wybór Bagna %s → gracz (%.1f; %.1f)" % (st.get("zamkniete"), wyb, p4[0], p4[2]))
        finally:
            PP.log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
            for _ in range(60):
                time.sleep(0.5)
                if "Current Studio Mode: Edit" in call("get_studio_state")["text"]:
                    break
            if imie:
                W["_konto"] = imie
                zapisz("_koniec", time.strftime("%Y-%m-%d %H:%M:%S"))
            print("\nLISTA:")
            for x in LISTA:
                print("  %s %-4s %s" % x)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
