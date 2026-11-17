#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zrzuty aren walki z prawdziwych walk w trybie Play (sam włącza Play i wraca do Edit) → <arena>/klatki/*.jpg.

    python -B swiat/areny_walki/testy/zrzuty_aren_play.py                  # wszystkie walki z listy WALKI
    python -B swiat/areny_walki/testy/zrzuty_aren_play.py --tylko proba,las_slime --przyrostek _po
    python -B swiat/areny_walki/testy/zrzuty_aren_play.py --klatka         # + czas klatki w walce ×1 na każdej arenie

Źródła walk jak w grze: tablica prototypu (Workspace/TestWalki2, Sygnaly/Sterowanie „start”, czas ręczny), las-pas
(LasPasGra), Bagno (BagnoPasGra) i stary las (LasPotwory) — tu potwór prawdziwy, w trybie testowym bohatera
(TestBohater, hak SterowanieKlienta „bohater”/„walcz”), walka biegnie w czasie rzeczywistym, a kadry wybiera
przewijanie odtwarzacza (Sygnaly/Sterowanie „przewinDo”). Po starcie odczyt OstatniaArena / OstatniaArenaPowod
z kontenera źródła (atrybuty klienta). Kadry: plan ogólny (i to samo ujęcie z drugiej strony przy czasie ręcznym),
ujęcia w trakcie walki co ok. 1 s sceny (typ ujęcia w nazwie), powalenie, objazd w finale (4 chwile), karta wyniku.
Bez nazwy konta w kadrze (lista graczy i czat wyłączone u klienta). Zmienia tylko stan sesji Play.
"""
import argparse
import io
import json
import math
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (os.path.join(REPO, "swiat", "test_walki2", "testy"), PAKIET):
    if _s not in sys.path:
        sys.path.insert(0, _s)
from sesja_play import SesjaPlay, log  # noqa: E402
import plan as P  # noqa: E402

# (klucz, arena, źródło, klasa, gatunek/przeciwnik, poziom, ziarno)
WALKI = [
    ("proba", "proba", "TestWalki2", "wojownik", "cierniowy_wilk", "5", 104729),
    ("las_slime", "las", "LasPasGra", "wojownik", "lesny_slime", "auto", None),
    ("las_troll", "las", "LasPasGra", "mag", "lesny_troll", "auto", None),
    ("bagno_rechotek", "bagno", "BagnoPasGra", "zwiadowca", "rechotek", "auto", None),
    ("bagno_straznik", "bagno", "BagnoPasGra", "wojownik", "straznik_topieli", "auto", None),
    ("stary_las", "las", "LasPotwory", "wojownik", None, "auto", None),
]

BEZ_NAZWY = ('local SG = game:GetService("StarterGui") for _, t in { Enum.CoreGuiType.PlayerList, Enum.CoreGuiType.Chat } do '
             'pcall(function() SG:SetCoreGuiEnabled(t, false) end) end return "ok"')
J = ('local H = game:GetService("HttpService") local function J(v) local t = typeof(v) if t == "Vector3" then return { v.X, v.Y, v.Z } '
     'elseif t == "table" then local o = {} for a, b in v do o[tostring(a)] = J(b) end return o '
     'elseif t == "Instance" then return v:GetFullName() elseif t == "number" and (v ~= v or v == math.huge or v == -math.huge) '
     'then return tostring(v) end return v end ')
POTWOR = J + ('local k = workspace:FindFirstChild("%s") local najl for _, c in k.Stan:GetChildren() do '
              'if (%s) and c:GetAttribute("Stan") ~= "zajety" then najl = c break end end '
              'if not najl then return "{}" end return H:JSONEncode({ id = najl.Name, p = J(najl:GetAttribute("Pozycja")), '
              'gatunek = najl:GetAttribute("Gatunek"), strefa = najl:GetAttribute("Strefa") })')
PRZESTAW = ('local hrp = game:GetService("Players"):GetPlayers()[1].Character.HumanoidRootPart '
            'local p = Vector3.new(%f, %f, %f) hrp.Parent:PivotTo(CFrame.lookAt(p, p + Vector3.new(1, 0, 0))) '
            'hrp.AssemblyLinearVelocity = Vector3.zero return "ok"')
HAK = J + 'local k = workspace:FindFirstChild("%s") return H:JSONEncode(J(k.Sygnaly.%s:Invoke(%s)))'
ATRYBUTY = J + ('local k = workspace:FindFirstChild("%s") local o = {} for _, n in { "OstatniaArena", "OstatniaArenaPowod", '
                '"OstatniaSredniaKlatki", "OstatniP95Klatki", "OstatniaMaksKlatki", "OstatniaLiczbaKlatek", "OstatniStan", '
                '"OstatniKosztSkryptuSredni", "OstatniaLiczbaInstancji", "OstatniaOdmowa", "KlientOstatniaWalka" } do o[n] = J(k:GetAttribute(n)) end '
                'local a = game:GetService("Lighting"):FindFirstChildOfClass("Atmosphere") '
                'o.mgla = a and { a.Density, a.Offset, a.Haze, a.Color:ToHex() } or false '
                'o.celMgly = workspace.ArenyWalki:GetAttribute("CelMglyPasa") o.przywrocenia = workspace.ArenyWalki:GetAttribute("PrzywroceniaMgly") '
                'local n = workspace.TestWalki2:FindFirstChild("NastrojAreny", true) or k:FindFirstChild("NastrojAreny", true) '
                'o.detale = n and #n:GetChildren() or 0 return H:JSONEncode(o)')


# to samo ujęcie z drugiej strony: kamera ustawiana po odtwarzaczu (priorytet Camera + 10) tylko na czas zrzutu
LUSTRO_ON = ('local RS = game:GetService("RunService") local c = workspace.CurrentCamera '
             'RS:BindToRenderStep("ArenyZrzutLustro", Enum.RenderPriority.Camera.Value + 10, function() '
             'c.CFrame = CFrame.lookAt(Vector3.new(%f, %f, %f), Vector3.new(%f, %f, %f)) end) return "ok"')
LUSTRO_OFF = 'game:GetService("RunService"):UnbindFromRenderStep("ArenyZrzutLustro") return "ok"'


def kadr169(im):
    w, h = im.size
    if w / h > 16 / 9:
        nw = int(h * 16 / 9)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w * 9 / 16)
        im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    if im.width > 1280:
        from PIL import Image
        im = im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
    return im


class Zrzuty:
    def __init__(self, s, przyrostek=""):
        self.s = s
        self.przyrostek = przyrostek
        self.wyniki = {}

    def js(self, kod, dm="Client"):
        t = self.s.luau(kod, dm).strip()
        return json.loads(t) if t else {}

    def odtw(self, arg):
        return json.loads(self.s.steruj(arg))

    def zapisz(self, arena, nazwa, kamera=None, patrz=None):
        im = self.s.zrzut(kamera, patrz) if kamera else self.s.zrzut()
        folder = os.path.join(PAKIET, arena, "klatki")
        os.makedirs(folder, exist_ok=True)
        p = os.path.join(folder, nazwa + self.przyrostek + ".jpg")
        kadr169(im).save(p, "JPEG", quality=86)
        return os.path.relpath(p, REPO).replace(os.sep, "/")

    def lustro(self, arena, st):
        """To samo ujęcie z drugiej strony placu (kamera odbita w osi Z sceny) — świat = (Ox − x, y, Oz − z)."""
        O = P.ARENY[arena]["O"]
        k, c = st["kamera"], st["patrz"]
        k2 = [k[0], k[1], 2 * O[2] - k[2]]
        c2 = [c[0], c[1], 2 * O[2] - c[2]]
        return k2, c2

    def start_tablica(self, arena, klasa, wrog, poziom, ziarno):
        s = self.s
        s.przy_tablicy()
        s.ziarno(ziarno)
        biom = "nil" if arena == "proba" else '"%s"' % arena
        s.luau('workspace.TestWalki2:SetAttribute("BiomAreny", %s) return "ok"' % biom)    # lokalny atrybut klienta
        s.start(klasa, wrog, poziom, "{ reczny = true }")

    def start_potwor(self, zrodlo, klasa, gatunek, poziom):
        s = self.s
        warunek = 'c:GetAttribute("Gatunek") == "%s"' % gatunek if gatunek else 'c:GetAttribute("Strefa") ~= "straznik"'
        cel = {}
        for _ in range(12):
            cel = self.js(POTWOR % (zrodlo, warunek), "Server")
            if cel.get("id"):
                break
            time.sleep(2.5)
        if not cel.get("id"):
            return None
        p = cel["p"]
        s.luau('game:GetService("Players"):GetPlayers()[1]:RequestStreamAroundAsync(Vector3.new(%f, %f, %f), 5) return "ok"'
               % (p[0], p[1], p[2]), "Server")
        for proba in range(6):
            # potwory chodzą (4 Hz) i stają przy graczu — przy każdej próbie świeże położenie i postać tuż obok (zakotwiczona)
            p = self.js(J + 'local c = workspace.%s.Stan:FindFirstChild("%s") return H:JSONEncode(J(c and c:GetAttribute("Pozycja") or false))'
                        % (zrodlo, cel["id"]), "Server") or p
            s.luau(PRZESTAW % (p[0] - 2.0, p[1] + 2.6, p[2]), "Server")
            s.luau('game:GetService("Players"):GetPlayers()[1].Character.HumanoidRootPart.Anchored = true return "ok"', "Server")
            b = self.js(HAK % (zrodlo, "SterowanieKlienta", '"bohater", "%s", "%s"' % (klasa, poziom)))
            w = self.js(HAK % (zrodlo, "SterowanieKlienta", '"walcz", "%s"' % cel["id"]))
            t0 = time.time()
            while time.time() - t0 < 5:
                if self.odtw('"stan"').get("faza") == "odtwarzanie":
                    return cel
                time.sleep(0.3)
            atr = self.js(ATRYBUTY % zrodlo)
            blok = s.luau('local g = game:GetService("Players"):GetPlayers()[1] local o = {} for n, v in g:GetAttributes() do '
                          'if type(v) == "boolean" and v then table.insert(o, n) end end return table.concat(o, ",")', "Server")
            log("  próba %d: bohater %s, walcz %s, odmowa %s, flagi gracza: %s" % (proba + 1, b, w, atr.get("OstatniaOdmowa"), blok.strip()))
            time.sleep(3.0)
        return cel
    def czekaj_odtwarzanie(self, limit=20):
        t0 = time.time()
        st = {}
        while time.time() - t0 < limit:
            try:
                st = self.odtw('"stan"')
            except Exception:  # noqa: BLE001
                st = {}
            if st.get("faza") == "odtwarzanie" and st.get("czasKonca"):
                return st
            time.sleep(0.3)
        return st

    def walka(self, klucz, arena, zrodlo, klasa, wrog, poziom, ziarno, gesto=True):
        s = self.s
        log("== walka", klucz, zrodlo, klasa, wrog, poziom)
        reczny = zrodlo == "TestWalki2"
        try:
            s.steruj('"zamknij"')
        except Exception:  # noqa: BLE001
            pass
        time.sleep(1.0)
        if reczny:
            self.start_tablica(arena, klasa, wrog, poziom, ziarno)
            cel = {"id": wrog}
        else:
            cel = self.start_potwor(zrodlo, klasa, wrog, poziom)
            if not cel:
                self.wyniki[klucz] = {"blad": "brak wolnego potwora"}
                log("  brak wolnego potwora")
                return
        st = self.czekaj_odtwarzanie()
        atr = self.js(ATRYBUTY % zrodlo)
        log("  start:", st.get("faza"), "arena:", atr.get("OstatniaArena"), atr.get("OstatniaArenaPowod"), "mgła:", atr.get("mgla"),
            "detale:", atr.get("detale"))
        wynik = {"cel": cel, "arena": atr.get("OstatniaArena"), "powod": atr.get("OstatniaArenaPowod"), "mgla_start": atr.get("mgla"),
                 "detale": atr.get("detale"), "zrzuty": []}
        time.sleep(1.5)
        atr2 = self.js(ATRYBUTY % zrodlo)
        wynik["mgla_1_5s"] = atr2.get("mgla")
        wynik["przywrocenia_mgly"] = atr2.get("przywrocenia")
        log("  mgła po 1,5 s:", atr2.get("mgla"), "przywróceń:", atr2.get("przywrocenia"))
        self.wyniki[klucz] = wynik
        if st.get("faza") != "odtwarzanie":
            wynik["blad"] = "walka nie ruszyła"
            return
        if not gesto:
            return wynik
        # 1) plan ogólny i to samo ujęcie z drugiej strony
        st = self.odtw('"przewinDo", 0.95')
        time.sleep(1.5 if reczny else 0.3)                     # baner „WALKA!” gaśnie
        st = self.odtw('"stan"')
        wynik["zrzuty"].append(self.zapisz(arena, "%s_01_ogolny" % klucz))
        if st.get("kamera"):
            k2, c2 = self.lustro(arena, st)
            s.luau(LUSTRO_ON % tuple(k2 + c2))
            try:
                time.sleep(0.2)
                wynik["zrzuty"].append(self.zapisz(arena, "%s_02_ogolny_druga_strona" % klucz))
            finally:
                s.luau(LUSTRO_OFF)
        # 2) ujęcia w trakcie walki: co ok. 1,1 s sceny, po dwa każdego typu (najwyżej 9)
        czas = st.get("czasKonca") or 20
        tpok = st.get("tPokonany") or czas - 3
        widziane = {}
        nr = 3
        tau = 1.6
        while tau < tpok - 0.6 and nr < 12:
            st = self.odtw('"przewinDo", %f' % tau)
            if st.get("faza") != "odtwarzanie":
                break
            typ = st.get("ujecie") or "?"
            if widziane.get(typ, 0) < 2:
                widziane[typ] = widziane.get(typ, 0) + 1
                time.sleep(0.15 if reczny else 0.0)
                wynik["zrzuty"].append(self.zapisz(arena, "%s_%02d_%s" % (klucz, nr, typ)))
                nr += 1
            tau += 1.1 if reczny else 2.4
        # 3) finał: powalenie, objazd (4 chwile), karta wyniku
        st = self.odtw('"stan"')
        tpok, trad = st.get("tPokonany"), st.get("tRadosc")
        if tpok:
            self.odtw('"przewinDo", %f' % (tpok + 0.7))
            time.sleep(0.2)
            wynik["zrzuty"].append(self.zapisz(arena, "%s_20_powalenie" % klucz))
        if trad:
            for i, dt in enumerate((0.5, 1.4, 2.4)):
                st = self.odtw('"przewinDo", %f' % (trad + dt))
                if st.get("faza") != "odtwarzanie":
                    break
                time.sleep(0.15)
                wynik["zrzuty"].append(self.zapisz(arena, "%s_2%d_objazd_%d" % (klucz, i + 1, i + 1)))
        self.odtw('"przewinDo", 1000')
        time.sleep(1.2)
        wynik["zrzuty"].append(self.zapisz(arena, "%s_24_objazd_4" % klucz))
        time.sleep(2.0)
        wynik["zrzuty"].append(self.zapisz(arena, "%s_25_wynik" % klucz))
        atr = self.js(ATRYBUTY % zrodlo)
        wynik["koniec"] = atr
        log("  zrzutów:", len(wynik["zrzuty"]))
        return wynik

    def klatka(self, klucz, arena, zrodlo, klasa, wrog, poziom, ziarno, stara=False):
        """Walka ×1 bez przewijania do końca → OstatniaSredniaKlatki / P95 z odtwarzacza. stara = przez lokalny atrybut
        Wylaczone na Workspace/ArenyWalki (zapas: stara arena prototypu) — punkt odniesienia i próba zapasu."""
        s = self.s
        log("== klatka", klucz, "(stara arena)" if stara else "")
        s.luau('workspace.ArenyWalki:SetAttribute("Wylaczone", %s) return "ok"' % ("true" if stara else "nil"))
        if stara:
            klucz = klucz + "_stara"
        try:
            s.steruj('"zamknij"')
        except Exception:  # noqa: BLE001
            pass
        time.sleep(1.0)
        if zrodlo == "TestWalki2":
            s.przy_tablicy()
            s.ziarno(ziarno)
            biom = "nil" if arena == "proba" else '"%s"' % arena
            s.luau('workspace.TestWalki2:SetAttribute("BiomAreny", %s) return "ok"' % biom)
            s.start(klasa, wrog, poziom, "{ tempo = 1 }")
        else:
            if not self.start_potwor(zrodlo, klasa, wrog, poziom):
                return None
            self.odtw('"tempo", 1')
        st = self.czekaj_odtwarzanie()
        t0 = time.time()
        while time.time() - t0 < 90:
            st = self.odtw('"stan"')
            if st.get("faza") != "odtwarzanie":
                break
            time.sleep(1.0)
        time.sleep(1.0)
        atr = self.js(ATRYBUTY % zrodlo)
        self.wyniki["klatka_" + klucz] = atr
        log("  klatka:", atr.get("OstatniaArena"), atr.get("OstatniaSredniaKlatki"), "ms śr.,", atr.get("OstatniP95Klatki"), "ms p95,",
            atr.get("OstatniaLiczbaKlatek"), "klatek")
        return atr


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tylko", default="")
    ap.add_argument("--przyrostek", default="")
    ap.add_argument("--klatka", action="store_true")
    ap.add_argument("--bez-zrzutow", action="store_true")
    ap.add_argument("--wyniki", default=os.path.join(PAKIET, "klatki_wyniki.json"))
    a = ap.parse_args()
    tylko = [t for t in a.tylko.split(",") if t]
    with SesjaPlay() as s:
        for _ in range(40):
            if s.luau('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("LoadingScreen") '
                      'local b = g and g:FindFirstChild("Background") '
                      'return tostring(g == nil or not g.Enabled or b == nil or not b.Visible or b.BackgroundTransparency >= 0.99)').strip() == "true":
                break
            time.sleep(0.5)
        s.luau(BEZ_NAZWY)
        for n in ("LasPasGra", "BagnoPasGra", "LasPotwory"):
            s.luau('local k = workspace:FindFirstChild("%s") if k then k:SetAttribute("TestBohater", true) '
                   'k:SetAttribute("TestBezSesji", true) end return "ok"' % n, "Server")
        s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", true) return "ok"', "Server")
        time.sleep(2.0)
        z = Zrzuty(s, a.przyrostek)
        try:
            for w in WALKI:
                if tylko and w[0] not in tylko:
                    continue
                try:
                    z.walka(*w, gesto=not a.bez_zrzutow)
                except Exception as e:  # noqa: BLE001
                    z.wyniki[w[0]] = {"blad": str(e)[:300]}
                    log("  BŁĄD:", e)
            if a.klatka:
                for w, stara in ((WALKI[0], True), (WALKI[0], False), (WALKI[1], False), (WALKI[3], False)):
                    try:
                        z.klatka(*w, stara=stara)
                    except Exception as e:  # noqa: BLE001
                        log("  BŁĄD klatki:", e)
                s.luau('workspace.ArenyWalki:SetAttribute("Wylaczone", nil) return "ok"')
            try:
                s.steruj('"zamknij"')
            except Exception:  # noqa: BLE001
                pass
            time.sleep(1.5)
            # po walce: mgła wróciła, detale posprzątane
            z.wyniki["po_walce"] = z.js(ATRYBUTY % "TestWalki2")
        finally:
            try:
                s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", nil) workspace.TestWalki2:SetAttribute("ZiarnoTestowe", nil) '
                       'return "ok"', "Server")
            except Exception:  # noqa: BLE001
                pass
            stare = {}
            if os.path.isfile(a.wyniki):
                with open(a.wyniki, encoding="utf-8") as f:
                    stare = json.load(f)
            stare.update({k + a.przyrostek: v for k, v in z.wyniki.items()})
            with open(a.wyniki, "w", encoding="utf-8", newline="\n") as f:
                json.dump(stare, f, ensure_ascii=False, indent=1)
                f.write("\n")
    log("gotowe")


if __name__ == "__main__":
    main()
