# -*- coding: utf-8 -*-
"""Dżungla w Studio (tryb Play): bieg od przybycia do bramy, szerokość pola i zrzuty miejsc dla Karola. Sama włącza
i wyłącza Play; niczego nie zapisuje w miejscu.

    python -B swiat/dzungla_pas_gra/testy/proba_widokow.py <folder wyników POZA repo> [--studio <id>]

  W01 bieg postaci (PathfindingService + Humanoid:MoveTo u klienta) z Tarasu Przybycia do bramy do Pustyni — ok. 25 s
  W02 szerokość pola: marsz w bok w obie strony na Tarasie i przed bramą — ok. 4 s (ściana na |v| 34 minus postać)
  W03 poziomy w scalonych zagrodach przy 1 graczu (najniższy poziom zagrody chodzi)
Zrzuty (lista graczy i czat schowane) → swiat/dzungla_pas_gra/klatki/w_*.jpg: przejście bramą Bagna, przybycie
z inkubatorem i Kamieniem Powrotu, Dróżka pod liśćmi-parasolami, trzy zagrody, Ruiny Pancernika, Wąż na wyspie, brama do
Pustyni, widok z góry.
"""
import io
import json
import os
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"), TU,
           os.path.join(REPO, "swiat", "biomy")):
    if _s not in sys.path:
        sys.path.insert(0, _s)

import proba_play as PP  # noqa: E402  (KOD, J, G Dżungli)
import proba_biegu as PB  # noqa: E402  (kawałki Luau biegu i marszu w bok)

KLATKI = os.path.join(PAKIET, "klatki")
G = PP.G


def _plan():
    with open(os.path.join(REPO, "swiat", "dzungla_pas", "krotki", "plan_dzungli.json"), encoding="utf-8") as f:
        return json.load(f)


PLAN = _plan()
X0 = float(PLAN["swiat"]["X0"])
STRAZNIK = X0 + PLAN["straznik"]["miejsce"][0]
ZN = json.load(open(os.path.join(REPO, "swiat", "dzungla_pas", "krotki", "znaczniki.json"), encoding="utf-8"))
JAJKO = next(m for m in ZN["miejsca"] if m["id"] == "jajko")["punkt_swiat"]
KAMIEN = next(m for m in ZN["miejsca"] if m["id"] == "kamien_powrotu")["punkt_swiat"]
POZIOMY = PP.KB + ('local o = {} for _, c in k.Stan:GetChildren() do if c:GetAttribute("Strefa") == "%s" then '
                   'table.insert(o, c:GetAttribute("Poziom")) end end table.sort(o) return H:JSONEncode(o)')


def main():
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    wyj = os.path.abspath(argv[0])
    if os.path.normcase(wyj).startswith(os.path.normcase(REPO)):
        sys.exit("Folder wyników leży w repozytorium — podaj folder poza repo")
    studio = argv[argv.index("--studio") + 1] if "--studio" in argv else None
    os.makedirs(wyj, exist_ok=True)
    os.makedirs(KLATKI, exist_ok=True)
    from cel_studio import wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    from PIL import Image  # noqa: E402
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
            r = call("screen_capture", {"capture_id": "dzungla_w_" + nazwa}, timeout=150)
            if r["is_error"] or not r.get("images"):
                log("zrzut %s: BŁĄD %s" % (nazwa, r["text"][:120]))
                return None
            im = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
            if im.width > 1280:
                im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
            sciezka = os.path.join(KLATKI, "w_" + nazwa + ".jpg")
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

        def przestaw(x, z=-700.0, y=3.2):
            luau(PP.KOD["przestaw"] % (x, y, z, 1.0), "Server")

        def kamera(oko, cel, czekaj=2.5):
            luau('task.delay(0.1, function() local c = workspace.CurrentCamera c.CameraType = Enum.CameraType.Scriptable '
                 'c.CFrame = CFrame.lookAt(Vector3.new(%g, %g, %g), Vector3.new(%g, %g, %g)) end) return "ok"'
                 % (*oko, *cel), "Client")
            time.sleep(czekaj)

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
            for k in ("LasPasGra", "BagnoPasGra", "DzunglaPasGra"):
                czekaj_na(lambda: js(PP.KOD["kont_atr"] % (k, '"SerwerGotowy"'), "Server").get("SerwerGotowy"), 60, 1.0)
            time.sleep(3)
            hak("LasPasGra", "otworzBrame")
            hak("BagnoPasGra", "otworzBrame")
            # przejście bramą Bagna (po Strażniku Topieli) — przelot Bagna odhaczony wcześniej, żeby nie zasłaniał
            hak("BagnoPasGra", "przenies", None, "przybycie")
            time.sleep(2)
            czekaj_na(lambda: hak("BagnoPasGra", "gracz").get("faza") == "brak", 40, 1.0)
            hak("BagnoPasGra", "przenies", None, "przed_brama")
            time.sleep(3)
            b = G["brama_lasu"]
            kamera((b - 16, 7, -704), (b + 30, 4, -700))
            zrzut("01_brama_bagna_na_dzungle")
            kamera_wroc()

            # ================================================================ przybycie i przelot Dżungli
            hak("DzunglaPasGra", "przenies", None, "przybycie")
            time.sleep(2)
            czekaj_na(lambda: hak("DzunglaPasGra", "gracz").get("faza") == "brak", 40, 1.0)
            hak("DzunglaPasGra", "przenies", None, "przybycie")
            time.sleep(3)
            p = G["przybycie"]
            kamera((p - 10, 8, -706), (JAJKO[0], 2.5, JAJKO[2]))
            zrzut("02_przybycie_inkubator_kamien")
            kamera((p - 6, 3.2, -700), (p + 60, 4, -700))
            zrzut("03_droga_pod_parasolami")
            r03 = {st: js(POZIOMY % st, "Server") for st in ("z1", "g1", "o1", "t1")}
            zapisz("W03", r03)
            punkt("W03", r03.get("z1") and min(r03["z1"]) == 17 and r03.get("g1") and min(r03["g1"]) == 19
                  and r03.get("o1") and min(r03["o1"]) == 21, "poziomy przy 1 graczu: %s" % r03)
            for nazwa, st in (("04_polana_zwijogonow", "z1"), ("05_kwietnik_gebokwiatow", "g1"),
                              ("06_gaj_kokosow", "o1"), ("07_ruiny_pancernika", "t1")):
                x = G["strefy"][st]
                przestaw(x - 20)
                time.sleep(2.5)
                kamera((x - 22, 12, -714), (x, 2, -700))
                zrzut(nazwa)
            przestaw(STRAZNIK - 30)
            time.sleep(2.5)
            kamera((STRAZNIK - 30, 10, -712), (STRAZNIK, 6, -700))
            zrzut("08_waz_na_wyspie")
            przestaw(G["brama"] - 20)
            time.sleep(2.5)
            kamera((G["brama"] - 18, 7, -706), (G["brama"] + 20, 4, -700))
            zrzut("09_brama_do_pustyni")
            xs = (G["brama_lasu"] + G["brama"]) / 2.0 + 10
            przestaw(xs)
            time.sleep(4)
            kamera((xs, 300, -630), (xs, 0, -700), 3.5)
            zrzut("10_z_gory")
            kamera_wroc()

            # ================================================================ W01 bieg, W02 szerokość
            hak("DzunglaPasGra", "przenies", None, "przybycie")
            time.sleep(2.5)
            p0 = js(PP.KOD["poz"], "Server")
            bieg = js(PB.BIEG % (G["brama"] - 1.5, -700.0), "Client", timeout=150)
            bieg["plan_s"] = round((G["brama"] - p0[0]) / 16.0, 1)
            zapisz("W01", bieg)
            punkt("W01", bieg.get("doszedl") is True and 23 <= bieg["czas"] <= 32,
                  "DzunglaPasGra: z X %.0f do bramy X %.0f — %.1f s (prosto %.1f s), droga %.0f st, WalkSpeed %s, "
                  "utknięcia %d" % (p0[0], G["brama"], bieg["czas"], bieg["plan_s"], bieg["droga"], bieg.get("predkosc"),
                                    bieg.get("utkniecia", 0)))
            szer = {}
            for nazwa, x in (("taras", G["przybycie"] + 6), ("przed_brama", G["brama"] - 12)):
                przestaw(x)
                time.sleep(1.5)
                w = js(PB.BOK, "Client", timeout=60)
                w["szerokosc_st"] = round(w.get("plus", 0) + w.get("minus", 0), 1)
                w["szerokosc_s"] = round(w["szerokosc_st"] / 16.0, 2)
                szer[nazwa] = w
            zapisz("W02", szer)
            punkt("W02", all(3.6 <= w["szerokosc_s"] <= 4.4 for w in szer.values()),
                  ", ".join("%s %.1f st = %.2f s" % (n, w["szerokosc_st"], w["szerokosc_s"]) for n, w in szer.items()))
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
