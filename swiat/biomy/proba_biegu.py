# -*- coding: utf-8 -*-
"""Próba krótkiego pasa (D-096) w Roblox Studio: bieg od przybycia do bramy i szerokość pola w lesie i w Bagnie,
poziomy potworów w scalonych zagrodach, zrzuty dla Karola. Sama włącza i wyłącza Play; niczego nie zapisuje w miejscu.

    python -B swiat/biomy/proba_biegu.py <folder wyników POZA repo> [--studio <id>] [--bez-zrzutow]
    python -B swiat/biomy/proba_biegu.py --gora [--studio <id>]     # tylko zrzuty z góry (Play, kamera klienta)

Warunki: Studio w trybie Edit, zbudowane LasPas, BagnoPas (krótkie mapy), LasPasGra, BagnoPasGra.
  R01 poziomy w scalonych zagrodach przy 1 graczu: s1 i r1 mają potwora najniższego poziomu, rozkład bez losu
  R02 las: bieg postaci (PathfindingService + Humanoid:MoveTo u klienta) z przybycia do bramy — cel ok. 25 s
  R03 Bagno: to samo od Pomostu do bramy do Dżungli
  R04 szerokość pola: marsz w bok w obie strony w 2 miejscach każdego biomu — cel ok. 4 s (|v| ≤ 34 minus postać)
Zrzuty (bez nazwy konta, lista graczy i czat schowane) → swiat/biomy/klatki/d096_*.jpg.
"""
import io
import json
import os
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"),
           os.path.join(REPO, "swiat", "bagno_pas_gra", "testy")):
    if _s not in sys.path:
        sys.path.insert(0, _s)

import proba_play as PP  # noqa: E402  (KOD, J, G: położenia z krótkich map)

KLATKI = os.path.join(TU, "klatki")
G = PP.G
X0 = 1100.0


def _plan(sciezka):
    with open(os.path.join(REPO, *sciezka.split("/")), encoding="utf-8") as f:
        return json.load(f)


PLAN_B = _plan("swiat/bagno_pas/krotki/plan_bagna.json")
ZN_L = _plan("swiat/las_pas/krotki/znaczniki.json")
ZN_B = _plan("swiat/bagno_pas/krotki/znaczniki.json")
STRAZNIK_B = X0 + PLAN_B["straznik"]["miejsce"][0]


def miejsce(zn, i):
    return next(x for x in zn["miejsca"] if x["id"] == i)["punkt_swiat"]


PRZYBYCIE_L = miejsce(ZN_L, "przybycie")[0]      # G (z próby Bagna) ma „przybycie” Bagna


BIEG = r'''
local PFS = game:GetService("PathfindingService")
local g = game:GetService("Players").LocalPlayer
local hrp = g.Character.HumanoidRootPart local hum = g.Character:FindFirstChildOfClass("Humanoid")
local cel = Vector3.new(%f, hrp.Position.Y, %f)
local path = PFS:CreatePath({ AgentRadius = 2, AgentHeight = 5, AgentCanJump = true, WaypointSpacing = 6 })
local ok = pcall(function() path:ComputeAsync(hrp.Position, cel) end)
local punkty = {}
if ok and path.Status == Enum.PathStatus.Success then
	for _, w in path:GetWaypoints() do table.insert(punkty, w.Position) end
else
	table.insert(punkty, cel)
end
local start = hrp.Position
local t0 = os.clock()
local i, dl, utk, prev, ost, tUtk = 1, 0, 0, hrp.Position, hrp.Position, os.clock()
while i <= #punkty and os.clock() - t0 < 75 do
	local p = punkty[i]
	hum:MoveTo(Vector3.new(p.X, hrp.Position.Y, p.Z))
	local q = hrp.Position
	if Vector3.new(q.X - p.X, 0, q.Z - p.Z).Magnitude < 2.5 then i += 1 end
	dl += Vector3.new(q.X - prev.X, 0, q.Z - prev.Z).Magnitude
	prev = q
	if (q - ost).Magnitude > 1 then ost, tUtk = q, os.clock()
	elseif os.clock() - tUtk > 1.5 then utk += 1 tUtk = os.clock() hum.Jump = true end
	task.wait(0.05)
end
local czas = os.clock() - t0
hum:MoveTo(hrp.Position)
return game:GetService("HttpService"):JSONEncode({ czas = czas, droga = dl, sciezka = ok and path.Status == Enum.PathStatus.Success,
	punktow = #punkty, doszedl = i > #punkty, utkniecia = utk, start = { start.X, start.Z }, koniec = { hrp.Position.X, hrp.Position.Z },
	predkosc = hum.WalkSpeed })
'''

BOK = r'''
local g = game:GetService("Players").LocalPlayer
local hrp = g.Character.HumanoidRootPart local hum = g.Character:FindFirstChildOfClass("Humanoid")
local x = hrp.Position.X
local o = {}
for _, kier in { 1, -1 } do
	local t0 = os.clock()
	local skrajny = 0
	while os.clock() - t0 < 5 do
		hum:MoveTo(Vector3.new(x, hrp.Position.Y, -700 + kier * 80))
		skrajny = math.max(skrajny, math.abs(hrp.Position.Z + 700))
		task.wait(0.05)
	end
	o[kier == 1 and "plus" or "minus"] = skrajny
	local t1 = os.clock()
	while os.clock() - t1 < 3 and math.abs(hrp.Position.Z + 700) > 2 do
		hum:MoveTo(Vector3.new(x, hrp.Position.Y, -700))
		task.wait(0.05)
	end
end
hum:MoveTo(hrp.Position)
return game:GetService("HttpService"):JSONEncode(o)
'''

POZIOMY = PP.KB.replace("BagnoPasGra", "%s") + (
    'local o = {} for _, c in k.Stan:GetChildren() do if c:GetAttribute("Strefa") == "%s" then '
    'table.insert(o, c:GetAttribute("Poziom")) end end table.sort(o) return H:JSONEncode(o)')

# narzędzie execute_luau cofa zmiany kamery zrobione w czasie wywołania — kamerę Studio ustawiamy chwilę po nim
GORA_EDIT = ('task.delay(0.1, function() local c = workspace.CurrentCamera c.FieldOfView = 50 '
        'c.CFrame = CFrame.lookAt(Vector3.new(%f, %f, %f), Vector3.new(%f, 0, -700)) end) return "ok"')


def main():
    argv = sys.argv[1:]
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    from cel_studio import wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    try:
        from PIL import Image  # noqa: E402
    except ImportError:
        Image = None
    os.makedirs(KLATKI, exist_ok=True)
    gora = "--gora" in argv
    if not gora:
        if not argv or argv[0].startswith("--"):
            sys.exit(__doc__)
        wyj = os.path.abspath(argv[0])
        if os.path.normcase(wyj).startswith(os.path.normcase(REPO)):
            sys.exit("Folder wyników leży w repozytorium — podaj folder poza repo")
        os.makedirs(wyj, exist_ok=True)
    bez_zrzutow = "--bez-zrzutow" in argv
    WYNIKI, LISTA = {}, []

    def log(*a):
        print(time.strftime("%H:%M:%S"), *a, flush=True)

    def zapisz(k, v):
        WYNIKI[k] = v
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

        def luau(kod, dm, timeout=120):
            r = call("execute_luau", {"code": kod, "datamodel_type": dm}, timeout=timeout)
            if r["is_error"]:
                raise StudioError(r["text"][:800])
            return r["text"].strip()

        def js(kod, dm, timeout=120):
            if "local H" not in kod:
                kod = 'local H = game:GetService("HttpService") ' + kod
            w = json.loads(luau(PP.J + kod, dm, timeout))
            return {} if w == [] else w

        def zrzut(nazwa):
            if bez_zrzutow:
                return None
            r = call("screen_capture", {"capture_id": "d096_" + nazwa}, timeout=150)
            if r["is_error"] or not r.get("images"):
                log("zrzut %s: BŁĄD %s" % (nazwa, r["text"][:120]))
                return None
            sciezka = os.path.join(KLATKI, "d096_" + nazwa + ".jpg")
            if Image is not None:
                im = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
                if im.width > 1280:
                    im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
                im.save(sciezka, "JPEG", quality=85)
            log("zrzut", os.path.relpath(sciezka, REPO))
            return sciezka

        def hak(kontener, polecenie, *argi):
            a = "".join(", " + ("nil" if x is None else json.dumps(x)) for x in argi)
            return js(PP.KOD["hak"] % (kontener, "SterowaniePasa", polecenie, a), "Server")

        def czekaj_na(warunek, limit, co=0.5):
            t0 = time.time()
            while time.time() - t0 < limit:
                w = warunek()
                if w:
                    return w
                time.sleep(co)
            return None

        def kamera_na(oko, cel):
            luau('task.delay(0.1, function() local c = workspace.CurrentCamera c.CameraType = Enum.CameraType.Scriptable '
                 'c.CFrame = CFrame.lookAt(Vector3.new(%g, %g, %g), Vector3.new(%g, %g, %g)) end) return "ok"'
                 % (*oko, *cel), "Client")

        def kamera_wroc():
            luau(PP.KOD["kamera_zwykla"], "Client")

        log("Play:", call("start_stop_play", {"is_start": True})["text"][:60])
        try:
            czekaj_na(lambda: "Client" in call("get_studio_state")["text"]
                      and luau(PP.KOD["gotowy_klient"], "Client") == "true", 90, 1.0)
            luau(PP.KOD["bez_nazwy"], "Client")
            for _ in range(20):
                w = js(PP.KOD["wybor_klasy"], "Client")
                if not w["ekran"] and w["kamera"] == "Custom":
                    break
                call("user_keyboard_input", {"datamodel_type": "Client", "actions": [{"action": "keyPress", "key_code": "Return"}]})
                time.sleep(1.5)
            czekaj_na(lambda: js(PP.KOD["kont_atr"] % ("BagnoPasGra", '"SerwerGotowy"'), "Server").get("SerwerGotowy"), 60, 1.0)
            czekaj_na(lambda: js(PP.KOD["kont_atr"] % ("LasPasGra", '"SerwerGotowy"'), "Server").get("SerwerGotowy"), 60, 1.0)
            time.sleep(4)

            if gora:
                # ============================================================ zrzuty z góry (kamera skryptowa klienta;
                # w trybie Edit narzędzie nie przestawia kamery Studio). Postać na środku biomu — streaming mapy wokół niej
                for nazwa, (xa, xb) in (("gora_las", (1066, 1520)), ("gora_bagno", (1514, 1966))):
                    xs = (xa + xb) / 2.0
                    luau(PP.KOD["przestaw"] % (xs, 3.2, -700, 1.0), "Server")
                    time.sleep(3)
                    kont = "LasPasGra" if nazwa == "gora_las" else "BagnoPasGra"
                    czekaj_na(lambda: hak(kont, "gracz").get("faza") == "brak", 40, 1.0)   # pierwszy przelot biomu
                    time.sleep(2)
                    kamera_na((xs, 300, -630), (xs, 0, -700))
                    time.sleep(3)
                    zrzut(nazwa)
                kamera_wroc()
                return 0

            # ================================================================ R01 poziomy w scalonych zagrodach
            r01 = {}
            for kont, strefy in (("LasPasGra", ("s1", "m1", "w1")), ("BagnoPasGra", ("r1", "b1", "k1"))):
                for st in strefy:
                    r01[st] = js(POZIOMY % (kont, st), "Server")
            zapisz("R01", r01)
            punkt("R01", r01.get("s1") and min(r01["s1"]) == 1 and r01.get("r1") and min(r01["r1"]) == 10
                  and r01.get("w1") and min(r01["w1"]) == 6,
                  "poziomy przy 1 graczu: " + ", ".join("%s %s" % kv for kv in r01.items()))

            # ================================================================ R02 / R03 bieg przybycie → brama
            hak("LasPasGra", "otworzBrame")
            biegi = {}
            for kod, kont, punkt_przyb, x_bramy in (("R02", "LasPasGra", "las", G["brama_lasu"]),
                                                     ("R03", "BagnoPasGra", "przybycie", G["brama"])):
                hak(kont, "przenies", None, punkt_przyb)
                # pierwszy przelot (gracz go nie widział) — czekamy, aż się skończy
                time.sleep(2.0)
                czekaj_na(lambda: hak(kont, "gracz").get("faza") == "brak", 40, 1.0)
                time.sleep(1.5)
                hak(kont, "przenies", None, punkt_przyb)
                time.sleep(2.5)
                if kod == "R02":
                    kamera_na((PRZYBYCIE_L - 8, 9, -703), (PRZYBYCIE_L + 40, 2, -690))
                    time.sleep(2.0)
                    zrzut("las_przybycie_inkubator")
                    kamera_wroc()
                else:
                    inc = miejsce(ZN_B, "jajko")
                    kamera_na((G["przybycie"] - 10, 8, -716), (inc[0] + 2, 2.5, inc[2]))
                    time.sleep(2.0)
                    zrzut("bagno_pomost_inkubator")
                    kamera_wroc()
                    time.sleep(0.5)
                p0 = js(PP.KOD["poz"], "Server")
                b = js(BIEG % (x_bramy - 1.5, -700.0), "Client", timeout=150)
                b["plan_s"] = round((x_bramy - p0[0]) / 16.0, 1)
                biegi[kod] = b
                zapisz(kod, b)
                punkt(kod, b.get("doszedl") is True and 23 <= b["czas"] <= 32,
                      "%s: z X %.0f do bramy X %.0f — %.1f s (prosto %.1f s), droga %.0f st, WalkSpeed %s, ścieżka %s, "
                      "utknięcia %d" % (kont, p0[0], x_bramy, b["czas"], b["plan_s"], b["droga"], b.get("predkosc"),
                                        b.get("sciezka"), b.get("utkniecia", 0)))
                if kod == "R02":
                    kamera_na((x_bramy - 22, 10, -712), (x_bramy + 40, 3, -700))
                    time.sleep(2.0)
                    zrzut("brama_lasu_bagno_za_nia")
                    kamera_wroc()
                else:
                    kamera_na((STRAZNIK_B - 26, 9, -708), (STRAZNIK_B, 5, -700))
                    time.sleep(2.0)
                    zrzut("straznik_topieli")
                    kamera_wroc()

            # ================================================================ R04 szerokość pola
            szer = {}
            for nazwa, x in (("las_polana", PRZYBYCIE_L + 6), ("las_przed_brama", G["brama_lasu"] - 12),
                             ("bagno_pomost", G["przybycie"] + 6), ("bagno_przed_brama", G["brama"] - 12)):
                luau(PP.KOD["przestaw"] % (x, 3.2, -700, 1.0), "Server")
                time.sleep(1.5)
                w = js(BOK, "Client", timeout=60)
                w["szerokosc_st"] = round(w.get("plus", 0) + w.get("minus", 0), 1)
                w["szerokosc_s"] = round(w["szerokosc_st"] / 16.0, 2)
                szer[nazwa] = w
            zapisz("R04", szer)
            punkt("R04", all(3.6 <= w["szerokosc_s"] <= 4.4 for w in szer.values()),
                  "szerokość dojścia postaci: " + ", ".join("%s %.1f st = %.2f s (±%.1f/%.1f)" % (
                      n, w["szerokosc_st"], w["szerokosc_s"], w.get("plus", 0), w.get("minus", 0)) for n, w in szer.items()))
        finally:
            log("Stop:", call("start_stop_play", {"is_start": False})["text"][:60])
            for _ in range(60):
                time.sleep(0.5)
                if "Current Studio Mode: Edit" in call("get_studio_state")["text"]:
                    break
    print("\n".join("%s %-4s %s" % x for x in LISTA))
    return 0 if all(x[1] != "BŁĄD" for x in LISTA) else 1


if __name__ == "__main__":
    sys.exit(main())
