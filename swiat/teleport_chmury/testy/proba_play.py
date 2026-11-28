# -*- coding: utf-8 -*-
"""Próba teleportu przez chmury w trybie Play (Studio), sterowana haczykami Sygnaly/SterowanieKlienta i …Serwera.

    python -B swiat/teleport_chmury/testy/proba_play.py                 # testy 1–6, wyniki do wyniki/
    python -B swiat/teleport_chmury/testy/proba_play.py --zrzuty        # tylko zrzuty (z pauzami w fazach) do klatki/
    python -B swiat/teleport_chmury/testy/proba_play.py --tylko 1,4     # wybrane testy

Testy: 1 miasteczko → Las · 2 Las → miasteczko (prawdziwe kliknięcie myszą) · 3 rezygnacja (dotknięcie obok
i Backspace) · 4 zamknięta kraina (klient i serwer) · 5 dwa szybkie żądania · 6 błąd w połowie przejścia
(faza B i faza C) i śmierć postaci w czasie wyboru. Play tylko na czas bloku `with Sesja()` — zawsze kończy się
zatrzymaniem i sprawdzeniem trybu Edit. Zmienia wyłącznie stan sesji Play.
"""
import io
import json
import math
import os
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
KAT = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(KAT))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"),
           os.path.join(REPO, "swiat", "test_walki2", "testy")):
    sys.path.insert(0, _s)
from studio_mcp import StudioMCP, StudioError  # noqa: E402
from cel_studio import wybierz_studio  # noqa: E402
from czuwanie import nie_usypiaj  # noqa: E402

K = 'local k = workspace:WaitForChild("TeleportChmury", 10) local H = game:GetService("HttpService") '
WYNIKI = os.path.join(KAT, "wyniki")
KLATKI = os.path.join(KAT, "klatki")
LAS = (1114, -700)


def _start_bazaru():
    """(x, z) startu bazaru ze swiat/miasteczko_bazar/znaczniki.json — 26.11.2026: „miasteczko” to zawsze bazar
    (starego miasteczka przy (−64; −772) nie ma już w miejscu)."""
    with open(os.path.join(REPO, "swiat", "miasteczko_bazar", "znaczniki.json"), encoding="utf-8-sig") as f:
        st = json.load(f)["start"]["swiat"]
    return (st[0], st[2])


MIASTO = _start_bazaru()


def log(*a):
    print("[%s]" % time.strftime("%H:%M:%S"), *a, flush=True)


def lua_arg(v):
    if v is None:
        return "nil"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    return json.dumps(v, ensure_ascii=False)


class Sesja:
    def __init__(self):
        self.edit_po = None

    def __enter__(self):
        self.mcp = StudioMCP(timeout=180)
        self.s = self.mcp.__enter__()
        self.s.studios(wait=15)
        self.sid = wybierz_studio(self.s)
        if not self.tryb_edit():
            self.mcp.__exit__(None, None, None)
            sys.exit("Studio nie jest w trybie Edit — nie zaczynam.")
        nie_usypiaj()
        try:
            log("Play:", self.call("start_stop_play", {"is_start": True})["text"][:60])
            self.czekaj_na_gre()
        except BaseException:
            self.zatrzymaj()
            self.mcp.__exit__(None, None, None)
            raise
        return self

    def __exit__(self, typ, wart, tb):
        try:
            self.zatrzymaj()
        finally:
            self.mcp.__exit__(typ, wart, tb)
        return False

    def call(self, nazwa, args=None, timeout=None):
        a = dict(args or {})
        a["studio_id"] = self.sid
        return self.s.call(nazwa, a, timeout=timeout)

    def tryb_edit(self):
        return "Current Studio Mode: Edit" in self.call("get_studio_state")["text"]

    def zatrzymaj(self):
        try:
            log("Stop:", self.call("start_stop_play", {"is_start": False})["text"][:60])
        except Exception as e:  # noqa: BLE001
            log("Stop — błąd:", e)
        for _ in range(80):
            time.sleep(0.5)
            try:
                if self.tryb_edit():
                    break
            except Exception:  # noqa: BLE001
                pass
        self.edit_po = self.tryb_edit()
        log("Studio w trybie Edit:", self.edit_po)

    def luau(self, kod, dm="Client", timeout=120):
        r = self.call("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=timeout)
        if r["is_error"]:
            raise StudioError(r["text"][:2000])
        return r["text"]

    def klient(self, *args):
        kod = K + 'return H:JSONEncode(k.Sygnaly.SterowanieKlienta:Invoke(%s))' % ", ".join(lua_arg(a) for a in args)
        return json.loads(self.luau(kod, "Client"))

    def serwer(self, *args):
        kod = K + 'return H:JSONEncode(k.Sygnaly.SterowanieSerwera:Invoke(%s))' % ", ".join(lua_arg(a) for a in args)
        return json.loads(self.luau(kod, "Server"))

    def stan(self):
        return self.klient("stan")

    def czekaj_na_gre(self):
        t0 = time.time()
        gotowe = False
        while time.time() - t0 < 120:
            if "Client" in self.call("get_studio_state")["text"]:
                try:
                    w = self.luau('local p = game:GetService("Players").LocalPlayer local k = workspace:FindFirstChild("TeleportChmury") '
                                  'return tostring(p.Character ~= nil) .. " " .. tostring(k and k:GetAttribute("KlientGotowy")) .. " " '
                                  '.. tostring(p:GetAttribute("LoadingDone"))')
                    if w.strip().startswith("true true"):
                        gotowe = True
                        break
                except StudioError:
                    pass
            time.sleep(0.5)
        log("gra gotowa:", gotowe, "po %.0f s" % (time.time() - t0))
        # ekran wyboru klasy trzyma kamerę — Enter wybiera klasę (ClassSelectClient), potem kamera wraca do gracza
        for proba in range(20):
            st = self.stan()
            if st["kamera"] == "Custom" and st["podmiotHumanoid"]:
                log("kamera gracza gotowa (próba %d)" % proba)
                # las-pas (swiat/las_pas_gra), gdy stoi w Studio: jego przelot kamery przy pierwszym wejściu do lasu
                # zakotwiczyłby postać w teście 1 (ruch klawiszem W) — na czas tych testów wstrzymany haczykiem
                # testowym pasa (zapomnijPrzelot = nie startuj sam); przelot po chmurach sprawdza próba pasa
                w = self.luau('local k = workspace:FindFirstChild("LasPasGra") local s = k and k:FindFirstChild("Sygnaly") '
                              'local f = s and s:FindFirstChild("SterowaniePasa") '
                              'return tostring(f and k:GetAttribute("SerwerPasaGotowy") == true and f:Invoke("zapomnijPrzelot"))', "Server")
                log("przelot lasu-pasa wstrzymany na czas testów:", w)
                # 18.11.2026: to samo dla nowej cutscenki biomów (swiat/cutscenka_biomu) — biomy oznaczone jako
                # widziane jej uchwytem testowym; cutscenkę po chmurach sprawdza jej własna próba (punkt C11)
                w2 = self.luau('local k = workspace:FindFirstChild("CutscenkaBiomu") local s = k and k:FindFirstChild("Sygnaly") '
                               'local f = s and s:FindFirstChild("SterowanieCutscenki") '
                               'local g = game:GetService("Players"):GetPlayers()[1] '
                               'if not f or not g then return "brak" end '
                               'for _, b in { "las", "bagno", "dzungla" } do f:Invoke("oznacz", g.Name, b) end return "ok"', "Server")
                log("cutscenki biomów oznaczone jako widziane na czas testów:", w2)
                return
            self.call("user_keyboard_input", {"datamodel_type": "Client",
                                              "actions": [{"action": "keyPress", "key_code": "Return"}]})
            time.sleep(1.5)
        raise StudioError("kamera nie wróciła do gracza po wyborze klasy")

    def czekaj(self, warunek, limit, krok=0.15):
        t0 = time.time()
        st = None
        while time.time() - t0 < limit:
            st = self.stan()
            if warunek(st):
                return st, time.time() - t0
            time.sleep(krok)
        return st, time.time() - t0

    def czekaj_wybor(self, limit=12):
        return self.czekaj(lambda s: (s.get("biezacy") or {}).get("faza") == "wybor", limit)

    def czekaj_koniec(self, limit=25):
        return self.czekaj(lambda s: not s["trwa"], limit, 0.25)

    def zrzut(self, nazwa):
        from PIL import Image
        nie_usypiaj()
        t0 = time.time()
        r = self.call("screen_capture", {"capture_id": "tc_" + nazwa}, timeout=150)
        if r["is_error"] or not r["images"]:
            log("zrzut %s: BŁĄD %s" % (nazwa, (r["text"] or "")[:200]))
            return None
        im = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
        if im.width > 1600:
            im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
        os.makedirs(KLATKI, exist_ok=True)
        sciezka = os.path.join(KLATKI, nazwa + ".jpg")
        im.save(sciezka, "JPEG", quality=85)
        log("zrzut %s (%.1f s) -> %s" % (nazwa, time.time() - t0, sciezka))
        return sciezka

    def przesuniecie_w(self, ms=900):
        p1 = self.stan()["pozycja"]
        self.call("user_keyboard_input", {"datamodel_type": "Client", "actions": [
            {"action": "keyDown", "key_code": "W"}, {"action": "wait", "wait_time_ms": ms},
            {"action": "keyUp", "key_code": "W"}]})
        time.sleep(0.4)
        p2 = self.stan()["pozycja"]
        return math.hypot(p2[0] - p1[0], p2[2] - p1[2])

    def konsola(self):
        return self.call("get_console_output")["text"]


def odl_xz(poz, cel):
    return math.hypot(poz[0] - cel[0], poz[2] - cel[1])


def czysto(st, przed_gui):
    """Stan po przejściu: wszystko oddane graczowi."""
    problemy = []
    if st["trwa"]:
        problemy.append("trwa")
    if st["kamera"] != "Custom":
        problemy.append("kamera %s" % st["kamera"])
    if not st["podmiotHumanoid"]:
        problemy.append("podmiot kamery nie jest postacią")
    if not st["podpowiedzi"]:
        problemy.append("podpowiedzi wyłączone")
    if st["lokalne"] or st["zaslona"]:
        problemy.append("zostały chmury (%s/%s)" % (st["lokalne"], st["zaslona"]))
    if st["wiazanie"]:
        problemy.append("zostało wiązanie klawiszy")
    if st["sprzatanie"]:
        problemy.append("lista sprzątania niepusta (%d)" % st["sprzatanie"])
    if przed_gui is not None and st["ukryteGui"] != przed_gui:
        problemy.append("ukrytych ekranów %d zamiast %d" % (st["ukryteGui"], przed_gui))
    if abs(st["fov"] - 70) > 0.5:
        problemy.append("kąt widzenia %.1f" % st["fov"])
    if (st.get("ostatnie") or {}).get("sterowanieWylaczone"):
        problemy.append("sterowanie zostało wyłączone")
    return problemy


def zapisz(wyniki, nazwa):
    os.makedirs(WYNIKI, exist_ok=True)
    with open(os.path.join(WYNIKI, nazwa), "w", encoding="utf-8") as f:
        json.dump(wyniki, f, ensure_ascii=False, indent=1)


def streszczenie(st):
    o = st.get("ostatnie") or {}
    return {"wynik": o.get("wynik"), "blad": o.get("blad"), "czasy": o.get("czasy"), "klatki": o.get("klatki"),
            "odpowiedz": o.get("odpowiedz"), "obecna": o.get("obecna"), "wybor": o.get("wybor"),
            "odmowy": o.get("odmowy"), "pozycja": st.get("pozycja"), "przeniesiony": o.get("przeniesiony"),
            "uwaga": o.get("uwaga"), "sterowanieWylaczone": o.get("sterowanieWylaczone")}


def wybierz_kliknieciem(s, id_krainy, mysz=False):
    e = s.klient("ekran", id_krainy)
    if mysz:
        # narzędzie user_mouse_input: najpierw współrzędne okna gry (z paskiem u góry), potem bez niego
        for x, y, opis in ((e["vx"], e["vy"], "viewport"), (e["x"], e["y"], "gui")):
            s.call("user_mouse_input", {"datamodel_type": "Client", "actions": [
                {"action": "moveTo", "x": x, "y": y}, {"action": "wait", "wait_time_ms": 120},
                {"action": "mouseButtonClick", "mouse_button": "left"}]})
            time.sleep(0.6)
            st = s.stan()
            if (st.get("biezacy") or {}).get("faza") != "wybor":
                return "mysz (%s: %.0f, %.0f)" % (opis, x, y), e
        log("  kliknięcie myszą nie zadziałało — dotknięcie przez haczyk")
    w = s.klient("dotknij", e["x"], e["y"])
    return "dotknij (%.0f, %.0f) → %s trafiony=%s" % (e["x"], e["y"], w.get("kraina"), w.get("trafiony")), e


def testy(s, tylko):
    wyniki = {"start": time.strftime("%Y-%m-%d %H:%M:%S"), "testy": {}}
    nazwa_pliku = "proba_play_%s.json" % time.strftime("%Y%m%d_%H%M")
    st0 = s.stan()
    przed_gui = st0["ukryteGui"]
    wyniki["przed"] = {"ukryteGui": przed_gui, "kamera": st0["kamera"], "zamkniete": st0["zamkniete"]}
    # odniesienie: klatki przez 3 s bez przejścia (ta sama sesja Play, gracz stoi)
    wyniki["klatki_bez_przejscia"] = json.loads(s.luau(
        K + 'local RS = game:GetService("RunService") local t0 = os.clock() local n, mx, suma = 0, 0, 0 '
        'while os.clock() - t0 < 3 do local dt = RS.RenderStepped:Wait() n += 1 suma += dt mx = math.max(mx, dt) end '
        'return H:JSONEncode({ n = n, fps = n / suma, srednia_ms = suma / n * 1000, max_ms = mx * 1000 })'))
    log("klatki bez przejścia:", wyniki["klatki_bez_przejscia"])

    def zapis(nr, dane):
        wyniki["testy"][str(nr)] = dane
        zapisz(wyniki, nazwa_pliku)
        log("TEST %s: %s" % (nr, "OK" if dane.get("ok") else "NIE"), json.dumps(dane, ensure_ascii=False)[:900])

    # „miasteczko” to start bazaru: atrybut Workspace/MiasteczkoBazarGra (pierwszy wpis przybycia w krainy.json), bez
    # niego zapasowy punkt z krainy.json — ten sam start ze znaczników mapy bazaru (od 26.11.2026 bez starego miasteczka)
    global MIASTO
    baz = json.loads(s.luau('local k = workspace:FindFirstChild("MiasteczkoBazarGra") local p = k and k:GetAttribute("PunktStartuBazaru") '
                            'return game:GetService("HttpService"):JSONEncode(if typeof(p) == "Vector3" then { p.X, p.Z } else {})', "Server"))
    if len(baz) == 2:
        MIASTO = (baz[0], baz[1])
    log("cel krainy „miasteczko”:", MIASTO, "(atrybut bazaru)" if len(baz) == 2 else "(start bazaru ze znaczników)")

    # przygotowanie: gracz w miasteczku
    w = s.serwer("przenies", "miasteczko")
    log("przygotowanie (serwer przenosi do miasteczka):", w)
    time.sleep(3)

    if 1 in tylko:
        st, t = s.czekaj(lambda x: not x["trwa"], 5)
        o = s.klient("otworz")
        stw, tw = s.czekaj_wybor()
        sposob, e = wybierz_kliknieciem(s, "las", mysz=False)
        stk, tk = s.czekaj_koniec()
        poz = stk["pozycja"]
        ruch = s.przesuniecie_w()
        sz = streszczenie(stk)
        problemy = czysto(stk, przed_gui)
        ok = (o["ok"] and sz["wynik"] == "wybrano las" and (sz["odpowiedz"] or {}).get("ok") and odl_xz(poz, LAS) < 12
              and not problemy and ruch > 3)
        zapis(1, {"ok": bool(ok), "opis": "miasteczko → Las", "sposob": sposob, "ekran": e, "odl_od_celu": odl_xz(poz, LAS),
                  "ruch_po_W": ruch, "problemy": problemy, **sz})

    if 2 in tylko:
        time.sleep(3.2)
        o = s.klient("otworz")
        stw, tw = s.czekaj_wybor()
        sposob, e = wybierz_kliknieciem(s, "miasteczko", mysz=True)
        stk, tk = s.czekaj_koniec()
        poz = stk["pozycja"]
        sz = streszczenie(stk)
        problemy = czysto(stk, przed_gui)
        ok = (o["ok"] and sz["wynik"] == "wybrano miasteczko" and odl_xz(poz, MIASTO) < 12 and not problemy)
        zapis(2, {"ok": bool(ok), "opis": "Las → miasteczko", "sposob": sposob, "ekran": e, "odl_od_celu": odl_xz(poz, MIASTO),
                  "problemy": problemy, **sz})

    if 3 in tylko:
        time.sleep(3.2)
        p0 = s.stan()["pozycja"]
        # w pauzie fazy A: W i spacja nie mogą ruszyć postaci
        s.klient("pauza", "A", 0.4)
        o = s.klient("otworz")
        s.czekaj(lambda x: (x.get("biezacy") or {}).get("pauza") is not None, 8)
        s.call("user_keyboard_input", {"datamodel_type": "Client", "actions": [
            {"action": "keyDown", "key_code": "W"}, {"action": "keyPress", "key_code": "Space"},
            {"action": "wait", "wait_time_ms": 800}, {"action": "keyUp", "key_code": "W"}]})
        time.sleep(0.5)
        p_pauza = s.stan()["pozycja"]
        stoi = math.dist(p0, p_pauza)
        s.klient("wznow")
        stw, tw = s.czekaj_wybor()
        e = s.klient("ekran", "las")
        w = s.klient("dotknij", e["vp"][0] * 0.5, max(e["y"] - e["vp"][1] * 0.38, 20))
        stk, tk = s.czekaj_koniec()
        sz = streszczenie(stk)
        problemy = czysto(stk, przed_gui)
        a_ok = sz["wynik"] == "rezygnacja" and odl_xz(stk["pozycja"], (p0[0], p0[2])) < 2 and not problemy and stoi < 0.5
        a = {"ok": bool(a_ok), "dotknij": w, "wynik": sz["wynik"], "wybor": sz["wybor"], "problemy": problemy,
             "postac_przesunela_sie_o": stoi, "czasy": sz["czasy"]}
        # klawisz Backspace (klawiatura) — ten sam skutek co B na padzie
        o2 = s.klient("otworz")
        s.czekaj_wybor()
        s.call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": "Backspace"}]})
        stk2, _ = s.czekaj_koniec()
        sz2 = streszczenie(stk2)
        problemy2 = czysto(stk2, przed_gui)
        b_ok = sz2["wynik"] == "rezygnacja" and not problemy2
        zapis(3, {"ok": bool(a_ok and b_ok), "opis": "rezygnacja: dotknięcie obok pasa i Backspace", "obok": a,
                  "backspace": {"ok": bool(b_ok), "wybor": sz2["wybor"], "problemy": problemy2, "czasy": sz2["czasy"]}})

    if 4 in tylko:
        time.sleep(0.5)
        o = s.klient("otworz")
        s.czekaj_wybor()
        sposob, e = wybierz_kliknieciem(s, "bagno")
        time.sleep(0.8)
        st = s.stan()
        nadal = (st.get("biezacy") or {}).get("faza") == "wybor"
        odm = (st.get("biezacy") or {}).get("odmowy")
        # ta sama prośba wprost do serwera (z pominięciem makiety)
        w = json.loads(s.luau(K + 'return H:JSONEncode(k.Zdalne.Teleport:InvokeServer("przenies", "bagno"))'))
        w2 = json.loads(s.luau(K + 'return H:JSONEncode(k.Zdalne.Teleport:InvokeServer("przenies", "nie_ma_takiej"))'))
        w3 = json.loads(s.luau(K + 'return H:JSONEncode(k.Zdalne.Teleport:InvokeServer({ zle = true }, 5))'))
        s.klient("rezygnuj")
        stk, _ = s.czekaj_koniec()
        problemy = czysto(stk, przed_gui)
        ok = nadal and odm == 1 and w.get("powod") == "zamknieta" and w2.get("powod") == "nieznana" and \
            w3.get("powod") == "zle_dane" and not problemy
        zapis(4, {"ok": bool(ok), "opis": "zamknięta kraina (Bagno)", "sposob": sposob, "nadal_w_wyborze": nadal,
                  "odmowy": odm, "serwer_bagno": w, "serwer_nieznana": w2, "serwer_zle_dane": w3, "problemy": problemy})

    if 5 in tylko:
        time.sleep(3.2)
        o1 = s.klient("otworz")
        o2 = s.klient("otworz")
        s.czekaj_wybor()
        s.klient("rezygnuj")
        s.czekaj_koniec()
        # dwie prośby naraz prosto do serwera, potem trzecia od razu po nich
        kod = (K + 'local z = k.Zdalne.Teleport local w = {} '
               'task.spawn(function() w[1] = z:InvokeServer("przenies", "las") end) '
               'task.spawn(function() w[2] = z:InvokeServer("przenies", "las") end) '
               'local t0 = os.clock() while (not w[1] or not w[2]) and os.clock() - t0 < 15 do task.wait() end '
               'w[3] = z:InvokeServer("przenies", "miasteczko") '
               'local r = {} for i = 1, 3 do local x = w[i] or {} r[i] = { ok = x.ok, powod = x.powod, zostalo = x.zostalo } end '
               'return H:JSONEncode(r)')
        r = json.loads(s.luau(kod))
        time.sleep(1.0)
        poz = s.stan()["pozycja"]
        oki = [x.get("ok") for x in r[:2]]
        ok = (o1["ok"] and not o2["ok"] and o2.get("powod") == "trwa" and oki.count(True) == 1
              and any(x.get("powod") == "trwa" for x in r[:2]) and r[2].get("powod") == "za_szybko"
              and odl_xz(poz, LAS) < 12)
        zapis(5, {"ok": bool(ok), "opis": "dwa szybkie żądania", "otworz_1": o1, "otworz_2": o2, "serwer": r,
                  "odl_od_lasu": odl_xz(poz, LAS)})

    if 6 in tylko:
        time.sleep(3.2)
        wyn6 = {}
        # 6a: błąd w fazie B (gracz nad makietą, nic nie przeniesione)
        p0 = s.stan()["pozycja"]
        s.klient("blad", "B")
        s.klient("otworz")
        stk, _ = s.czekaj_koniec()
        sz = streszczenie(stk)
        pr = czysto(stk, przed_gui)
        ruch = s.przesuniecie_w(700)
        wyn6["B"] = {"ok": bool(sz["wynik"] == "błąd" and not pr and ruch > 2), "blad": sz["blad"], "problemy": pr,
                     "ruch_po_W": ruch}
        # 6b: błąd w fazie C (prośba do serwera już wysłana — serwer i tak przenosi, kamera ma wrócić do postaci)
        time.sleep(3.2)
        s.klient("blad", "C")
        s.klient("otworz")
        s.czekaj_wybor()
        s.klient("wybierz", "miasteczko")
        stk, _ = s.czekaj_koniec()
        time.sleep(2.5)
        stk = s.stan()
        sz = streszczenie(stk)
        pr = czysto(stk, przed_gui)
        ruch = s.przesuniecie_w(700)
        wyn6["C"] = {"ok": bool(sz["wynik"] == "błąd" and not pr and ruch > 2), "blad": sz["blad"], "problemy": pr,
                     "ruch_po_W": ruch, "odl_od_miasteczka": odl_xz(stk["pozycja"], MIASTO)}
        # 6c: śmierć postaci w czasie wyboru
        time.sleep(3.2)
        s.klient("otworz")
        s.czekaj_wybor()
        s.luau('local p = game:GetService("Players"):GetPlayers()[1] p.Character.Humanoid.Health = 0 return "ok"', "Server")
        stk, _ = s.czekaj_koniec(10)
        sz = streszczenie(stk)
        time.sleep(7)
        st2 = s.stan()
        pr = czysto(st2, None)
        wyn6["smierc"] = {"ok": bool(sz["wynik"] == "błąd" and not pr), "blad": sz["blad"], "problemy": pr,
                          "kamera_po_odrodzeniu": st2["kamera"], "podmiot": st2["podmiotHumanoid"]}
        zapis(6, {"ok": all(v["ok"] for v in wyn6.values()), "opis": "błąd w połowie przejścia", **wyn6})

    kons = s.konsola()
    linie = [x for x in kons.splitlines() if "TeleportChmury" in x or "Teleport" in x and "rror" in x]
    wyniki["konsola"] = linie[-30:]
    wyniki["koniec"] = time.strftime("%Y-%m-%d %H:%M:%S")
    zapisz(wyniki, nazwa_pliku)
    return wyniki


def zrzuty(s):
    wyn = {}
    s.serwer("przenies", "miasteczko")
    time.sleep(3)
    s.zrzut("0_miasteczko_przed")
    # 1: wejście w chmury (pauza w fazie A)
    s.klient("pauza", "A", 0.72)
    s.klient("otworz")
    s.czekaj(lambda x: (x.get("biezacy") or {}).get("pauza") is not None, 8)
    s.zrzut("1_wejscie_w_chmury")
    s.klient("pauza", "A", 1.0)
    s.czekaj(lambda x: ((x.get("biezacy") or {}).get("pauza") or "").startswith("A 1"), 8)
    s.zrzut("1b_biel_pelna")
    s.klient("pauza", "B", 0.38)
    s.czekaj(lambda x: ((x.get("biezacy") or {}).get("pauza") or "").startswith("B"), 8)
    s.zrzut("2_wylonienie_z_chmur")
    s.klient("wznow")
    s.czekaj_wybor()
    time.sleep(0.6)
    s.zrzut("3_makieta_z_gory")
    s.klient("kursor", "las")
    time.sleep(0.6)
    s.zrzut("4_podswietlony_wybor")
    s.klient("kursor", "pustynia")
    time.sleep(0.5)
    s.zrzut("5_zamknieta_kraina")
    e = s.klient("ekran", "pustynia")
    s.klient("dotknij", e["x"], e["y"])
    s.zrzut("5b_odmowa")
    s.klient("pauza", "C", 0.55)
    s.klient("wybierz", "las")
    s.czekaj(lambda x: ((x.get("biezacy") or {}).get("pauza") or "").startswith("C"), 8)
    s.zrzut("6_zanurzenie")
    s.klient("pauza", "D", 0.3)
    s.czekaj(lambda x: ((x.get("biezacy") or {}).get("pauza") or "").startswith("D"), 15)
    s.zrzut("7a_opadanie_poczatek")
    s.klient("pauza", "D", 0.6)
    s.czekaj(lambda x: ((x.get("biezacy") or {}).get("pauza") or "").startswith("D 0.6"), 15)
    s.zrzut("7_opadanie_na_gracza")
    s.klient("wznow")
    s.czekaj_koniec()
    time.sleep(0.8)
    s.zrzut("8_po_przejsciu_las")
    wyn["stan"] = streszczenie(s.stan())
    zapisz(wyn, "zrzuty_%s.json" % time.strftime("%Y%m%d_%H%M"))
    return wyn


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    tylko = {1, 2, 3, 4, 5, 6}
    if "--tylko" in sys.argv:
        tylko = {int(x) for x in sys.argv[sys.argv.index("--tylko") + 1].split(",")}
    with Sesja() as s:
        if "--zrzuty" in sys.argv:
            w = zrzuty(s)
        else:
            w = testy(s, tylko)
        log("koniec:", json.dumps(w, ensure_ascii=False)[:400])
    log("Studio w Edit po teście:", s.edit_po)


main()
