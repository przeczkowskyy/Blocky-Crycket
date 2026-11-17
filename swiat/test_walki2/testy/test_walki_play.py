#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test prototypu walki v2 w trybie PLAY (Roblox Studio). Na końcu ZAWSZE wraca do trybu Edit.

    python -B swiat/test_walki2/testy/test_walki_play.py [--studio <id>] [--szybko]

Wymaga zbudowanego kontenera (zbuduj.py), testy/ziarna.json (test_odtwarzacza.py --ziarna) i Studio w trybie Edit.
Sprawdza (wzór: swiat/test_walki_roblox/testy/test_play.py):
  1. wejście przez tablicę: postać przy tablicy, klawisz E → panel wyboru; klik klasy, przeciwnika, poziomu i WALCZ
     (myszą, przez prawdziwe przyciski) → walka startuje; dziennik zgodny z portem silnika w Pythonie;
  2. pełne walki: każda klasa z trzema różnymi przeciwnikami (ziarna z ziarna.json), do panelu wyniku; po każdej:
     wszystkie zdarzenia obsłużone, brak braków choreografii i błędów, paski = dziennik po każdym zdarzeniu i na końcu,
     tury odtwarzacza = tury silnika, łup na panelu = łup z dziennika;
  3. długa walka (> 20 tur) i krótka (3 tury); tempo ×4 klikiem w trakcie; POMIŃ (D-078: przycisk tylko przy gatunku
     poznanym wcześniej w tej sesji Play — Strażnik Gaju walczył w p. 2; po pominięciu za zgodą serwera gracz wolny od
     razu, więc JESZCZE RAZ bez odliczania; pierwszą walkę bez przycisku sprawdza testy/test_v3_play.py); JESZCZE RAZ;
     ZAMKNIJ (kamera, GUI gry, lista graczy, czat, podpowiedź, sterowanie wracają; postać chodzi);
  4. reset postaci w trakcie walki → wszystko posprzątane, po odrodzeniu postać chodzi;
  5. bezpieczeństwo: złe wybory i liczby od klienta odrzucone albo zignorowane, limit próśb, sesja walki, odległość;
  6. obcy w kadrze schowani lokalnie i przywróceni; 7. symulacja publikacji (kontener znika poza Studio);
  8. konsola bez komunikatów z naszego kodu; 9. pomiary czasu klatki i kosztu naszego kodu (PC).
Macierz walk z p. 2 idzie z atrybutem serwera TestBezSesji (bez czekania na koniec sesji między walkami);
blokadę sesji sprawdza osobno p. 5 (bez tego atrybutu); odliczanie po pominięciu BEZ zgody — test_v3_play.py (P4).
"""
import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
KATALOG = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(KATALOG))
for _s in (TU, os.path.join(REPO, "tools", "walka")):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import silnik as S  # noqa: E402
import wzorcowe as WZ  # noqa: E402
from sesja_play import SesjaPlay, log, PRZY_TABLICY  # noqa: E402

WYNIKI = []
POMIARY = []
GUI_WYBOR = "TestWalki2Wybor.Ekran.Karta."  # Ekran = cały ekran albo emulowany telefon (testy/telefon.py)
GUI_WALKA = "TestWalki2Cutscenka.Kadr."


def sprawdz(nazwa, warunek, szczegoly=""):
    WYNIKI.append((nazwa, bool(warunek)))
    log("%-66s %s %s" % (nazwa, "OK" if warunek else "BŁĄD", szczegoly))


def oczekiwana(p):
    w = S.symuluj(WZ.postac(p["klasa"], p["poziom"]), {"potwor": p["przeciwnik"], "poziom": p["poziom"]}, p["ziarno"])
    ost = w["dziennik"][-1]
    lup = w["lup"]
    return {"wynik": w["wynik"], "tury": w["tury"], "zdarzen": len(w["dziennik"]), "czas": w["czas"],
            "paski": "%d/%d" % (ost["hp_gracz"], ost["hp_wrog"]),
            "lup": [lup["zloto"], lup["doswiadczenie"], lup["tokeny_krainy"], lup["gemy"], lup["shard_ewolucji"]]}


def ocen_walke(nazwa, s, p, ocz, pelna=True):
    """Sprawdzenia po walce (stan = atrybuty klienta + panel wyniku)."""
    sprawdz(nazwa + ": panel wyniku", s.get("OstatniStan") == "wynik" and s.get("_wynikWidoczny"), "(%s)" % s.get("OstatniStan"))
    podpis = (s.get("OstatniWynik"), s.get("OstatniaLiczbaTur"), s.get("OstatniaLiczbaZdarzen"))
    sprawdz(nazwa + ": dziennik z serwera = port Pythona", podpis == (ocz["wynik"], ocz["tury"], ocz["zdarzen"]),
            "(%s vs %s)" % (podpis, (ocz["wynik"], ocz["tury"], ocz["zdarzen"])))
    sprawdz(nazwa + ": każde zdarzenie obsłużone, bez braków i błędów",
            s.get("OstatniaLiczbaObsluzonych") == ocz["zdarzen"] and s.get("OstatnieBrakiChoreografii") == 0
            and s.get("OstatnieBledyObslugi") == 0,
            "(obsłużone %s/%d, braki %s, błędy %s)" % (s.get("OstatniaLiczbaObsluzonych"), ocz["zdarzen"],
                                                      s.get("OstatnieBrakiChoreografii"), s.get("OstatnieBledyObslugi")))
    sprawdz(nazwa + ": paski = dziennik (po każdym zdarzeniu i na końcu)",
            (not pelna or s.get("OstatniaNiezgodnoscPaskow") == 0) and s.get("OstatniePaskiKoniec") == ocz["paski"],
            "(niezgodności %s, koniec %s, dziennik %s)" % (s.get("OstatniaNiezgodnoscPaskow"), s.get("OstatniePaskiKoniec"), ocz["paski"]))
    sprawdz(nazwa + ": licznik tur = silnik, łup na panelu = dziennik",
            s.get("OstatniaLiczbaTurOdtworzona") == ocz["tury"] and s.get("_lupPanelu") == ocz["lup"],
            "(tury %s, łup %s vs %s)" % (s.get("OstatniaLiczbaTurOdtworzona"), s.get("_lupPanelu"), ocz["lup"]))


def pomiar(nazwa, s, ocz):
    pola = ("OstatniCzasTrwania", "OstatniaSredniaKlatki", "OstatniP95Klatki", "OstatniaMaksKlatki", "OstatniKosztSkryptuSredni",
            "OstatniKosztSkryptuP95", "OstatniKosztSkryptuMaks", "OstatniaLiczbaInstancji", "OstatniaLiczbaUjec", "OstatniCzasPrzygotowania",
            "OstatniCzasSerwera", "OstatnieTempo")
    w = {p: s.get(p) for p in pola}
    w["nazwa"] = nazwa
    w["czas_dziennika"] = ocz["czas"]
    w["tury"] = ocz["tury"]
    POMIARY.append(w)
    log("  pomiar %s: %s" % (nazwa, ", ".join("%s=%s" % (k.replace("Ostatnia", "").replace("Ostatni", "").replace("Ostatnie", ""), v)
                                               for k, v in w.items() if k.startswith("Ostatn"))))


def stan_po_walce(nazwa, s):
    sprawdz(nazwa + ": kamera Custom na postaci", s["_kamera"] == "Custom" and s["_podmiotToHumanoid"],
            "(%s, podmiot = humanoid: %s, hp %s)" % (s["_kamera"], s["_podmiotToHumanoid"], s["_hp"]))
    sprawdz(nazwa + ": GUI walki i scena lokalna usunięte", not s["_gui"] and not s["_scena"])
    sprawdz(nazwa + ": lista graczy i czat z powrotem", s["_lista"] and s["_czat"])
    sprawdz(nazwa + ": blokady klawiszy zdjęte, podpowiedź włączona", not s["_blokada"] and not s["_pominKlawisz"] and s["_podpowiedz"])
    sprawdz(nazwa + ": szablony aktorów znów widoczne", s["_szablonUkryty"] == 0, "(%s)" % s["_szablonUkryty"])


BEZPIECZENSTWO = r'''
local HS = game:GetService("HttpService")
local rf = workspace.TestWalki2.Zdalne.RozpocznijWalke2
local w = {}
local function prosba(nazwa, ...)
	task.wait(1.05)
	local ok, r = pcall(rf.InvokeServer, rf, ...)
	w[nazwa] = if ok then { ok = r.ok, powod = r.powod, ponowZa = r.ponowZa, odleglosc = r.odleglosc,
		zycie = r.walka and r.walka.strony.gracz.zycie, ziarno = r.walka and r.walka.ziarno, tury = r.walka and r.walka.tury,
		zloto = r.walka and r.walka.lup.zloto, nastepnaOd = r.nastepnaOd, teraz = workspace:GetServerTimeNow() } else { blad = tostring(r) }
end
workspace.TestWalki2:SetAttribute("ZiarnoTestowe", 5) -- zmiana u klienta: nie replikuje się
prosba("zla_klasa", { klasa = "rycerz", przeciwnik = "lesny_troll", poziom = "5" })
prosba("poziom_liczba", { klasa = "mag", przeciwnik = "lesny_troll", poziom = 5 })
prosba("poziom_spoza", { klasa = "mag", przeciwnik = "lesny_troll", poziom = "50" })
prosba("zly_wrog", { klasa = "mag", przeciwnik = "smok", poziom = "5" })
prosba("nie_tabela", "mag")
prosba("bez_argumentow")
prosba("z_liczbami", { klasa = "__KLASA__", przeciwnik = "__WROG__", poziom = "__POZIOM__", statystyki = { sila = 1e9 }, zycie = 1e9,
	zloto = 1e9, ziarno = 1, wynik = "wygrana" }, 999999, { hp = 1e9 })
local ok, r = pcall(rf.InvokeServer, rf, { klasa = "__KLASA__", przeciwnik = "__WROG__", poziom = "__POZIOM__" })
w.za_szybko = { ok = r.ok, powod = r.powod }
prosba("w_trakcie", { klasa = "__KLASA__", przeciwnik = "__WROG__", poziom = "__POZIOM__" })
return HS:JSONEncode(w)
'''

OBCY = r'''
local CS = game:GetService("CollectionService")
local k = workspace.TestWalki2
local f = Instance.new("Folder")
f.Name = "TestowyIntruz"
local m = Instance.new("Part")
m.Name = "WPudle"
m.Size = Vector3.new(3, 6, 3)
m.Anchored = true
m.Color = Color3.fromRGB(0, 255, 0)
m.Material = Enum.Material.Neon
m.CFrame = CFrame.new(0, 4, 252)
m.Parent = f
local t = Instance.new("Part")
t.Name = "ZTagiem"
t.Size = Vector3.new(2, 2, 2)
t.Anchored = true
t.CanQuery = false
t.Color = Color3.fromRGB(255, 0, 255)
t.CFrame = CFrame.new(4, 6, 246)
CS:AddTag(t, "TestWalki2Ukryj")
t.Parent = f
f.Parent = k
return "ok"
'''
STAN_OBCYCH = ('local f = workspace.TestWalki2:FindFirstChild("TestowyIntruz") if not f then return "brak" end '
               'return f.WPudle.LocalTransparencyModifier .. " " .. f.ZTagiem.LocalTransparencyModifier')

PUBLIKACJA = r'''
local f = Instance.new("Folder")
f.Name = "ProbaPublikacji"
local slup = Instance.new("Part")
slup.Anchored = true
slup.Size = Vector3.new(1, 6, 1)
slup.CFrame = CFrame.new(30, 3, 215)
slup.Parent = f
f.Parent = workspace.TestWalki2
task.wait(0.8)
local s = Instance.new("Script")
s.Name = "SerwerWalki2"
s.RunContext = Enum.RunContext.Server
s.Source = __ZRODLO__
s.Parent = f
local t0 = os.clock()
while f.Parent and os.clock() - t0 < 5 do task.wait(0.05) end
return if f.Parent then "NADAL JEST" else "USUNIETY"
'''


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio", default=None)
    ap.add_argument("--szybko", action="store_true", help="macierz walk z tempem ×4 (bez pomiarów przy ×1)")
    a = ap.parse_args()
    with open(os.path.join(TU, "ziarna.json"), encoding="utf-8") as f:
        Z = json.load(f)
    zrodlo_serwera = open(os.path.join(KATALOG, "zrodla", "SerwerWalki2.server.luau"), encoding="utf-8-sig").read().replace("\r\n", "\n")

    with SesjaPlay(a.studio) as t:
        def walka(nazwa, p, opcje="nil", limit=120, sprawdzaj=True, pelna=True):
            t.ziarno(p["ziarno"])
            time.sleep(1.1)
            t.start(p["klasa"], p["przeciwnik"], str(p["poziom"]), opcje)
            s1, dt = t.czekaj(("odtwarzanie", "blad", "odmowa"), 15)
            if s1.get("OstatniStan") != "odtwarzanie":
                sprawdz(nazwa + ": start", False, "(%s, %s)" % (s1.get("OstatniStan"), s1.get("OstatniaOdmowa")))
                return None
            s2, dt = t.czekaj(("wynik", "blad", "przerwano"), limit)
            time.sleep(1.0)
            s2 = t.stan()
            ocz = oczekiwana(p)
            if sprawdzaj:
                ocen_walke(nazwa, s2, p, ocz, pelna)
            return s2, ocz

        # --- 1. wejście przez tablicę i panel wyboru (myszą)
        t.przy_tablicy()
        time.sleep(1.0)
        p1 = Z["play"][0]
        t.ziarno(p1["ziarno"])
        t.klawisz("E")
        time.sleep(1.0)
        s = t.stan()
        sprawdz("1a. E przy tablicy otwiera panel wyboru", s.get("_panel"), "(podpowiedź: %s)" % s.get("_podpowiedzTekst"))
        for sciezka in ("Klasy.Klasa_%s" % p1["klasa"], "Wrogowie.Wrog_%s" % p1["przeciwnik"], "Poziomy.Poziom_%d" % p1["poziom"]):
            t.klik(GUI_WYBOR + sciezka)
            time.sleep(0.3)
        wybrane = t.luau('local k = game:GetService("Players").LocalPlayer.PlayerGui.TestWalki2Wybor.Ekran.Karta '
                         'return tostring(k.Klasy.Klasa_%s:GetAttribute("Wybrany")) .. tostring(k.Wrogowie.Wrog_%s:GetAttribute("Wybrany")) '
                         '.. tostring(k.Poziomy.Poziom_%d:GetAttribute("Wybrany"))' % (p1["klasa"], p1["przeciwnik"], p1["poziom"]))
        sprawdz("1b. kliknięcia zaznaczają klasę, przeciwnika i poziom", wybrane.strip() == "truetruetrue", "(%s)" % wybrane.strip())
        t.klik(GUI_WYBOR + "Walcz.Przycisk")
        s1, dt = t.czekaj(("odtwarzanie",), 10)
        sprawdz("1c. WALCZ → walka startuje, panel znika", s1.get("OstatniStan") == "odtwarzanie" and not s1.get("_panel"),
                "(%.1f s; wybór %s)" % (dt, s1.get("OstatniWybor")))
        s2, _ = t.czekaj(("wynik",), 120)
        time.sleep(1.0)
        s2 = t.stan()
        ocz = oczekiwana(p1)
        ocen_walke("1d. walka z panelu (%s/%s/%d)" % (p1["klasa"], p1["przeciwnik"], p1["poziom"]), s2, p1, ocz)
        pomiar("%s/%s/%d ×1" % (p1["klasa"], p1["przeciwnik"], p1["poziom"]), s2, ocz)
        sprawdz("1e. po pełnej walce JESZCZE RAZ od razu dostępne", s2.get("_jeszczeZablokowany") is False, "(%s)" % s2.get("_jeszczeTekst"))
        t.klik(GUI_WALKA + "Wynik.Karta.Zamknij.Przycisk")
        # bez wywołań execute_luau w trakcie zamykania: narzędzie przywraca typ kamery, jaki zastało na początku
        # wywołania (Scriptable z panelu wyniku), więc odpytywanie zaraz po kliknięciu dawało fałszywy błąd 1f
        # (2 z 2 pierwszych przebiegów 15.11) — najpierw czekamy, aż sprzątanie skończy się na pewno
        time.sleep(2.0)
        t.czekaj(("zamknieto",), 5)
        time.sleep(0.5)
        stan_po_walce("1f. po ZAMKNIJ", t.stan())
        droga = t.klawisz_w()
        sprawdz("1g. po ZAMKNIJ postać chodzi (W 0,9 s)", droga > 5, "(%.1f studa)" % droga)
        t.przy_tablicy()

        # --- 2. macierz: każda klasa × 3 przeciwników (bez blokady sesji między walkami)
        t.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", true) return "ok"', "Server")
        klasy_wrogowie = {}
        for i, p in enumerate(Z["play"][1:], 2):
            tempo = 1 if (not a.szybko and i in (4, 7)) else 4
            nazwa = "2.%d %s/%s/%d ×%d" % (i, p["klasa"], p["przeciwnik"], p["poziom"], tempo)
            w = walka(nazwa, p, "{ tempo = %d }" % tempo)
            if w and tempo == 1:
                pomiar(nazwa[4:], w[0], w[1])
            klasy_wrogowie.setdefault(p["klasa"], set()).add(p["przeciwnik"])
            t.steruj('"zamknij"')
            time.sleep(0.6)
        klasy_wrogowie.setdefault(p1["klasa"], set()).add(p1["przeciwnik"])
        sprawdz("2. każda klasa walczyła z ≥ 3 różnymi przeciwnikami",
                all(len(v) >= 3 for v in klasy_wrogowie.values()) and len(klasy_wrogowie) == 3,
                str({k: sorted(v) for k, v in klasy_wrogowie.items()}))

        # --- 3. długa i krótka walka, tempo ×4 klikiem, POMIŃ, JESZCZE RAZ
        pd = Z["dluga"]
        w = walka("3a. długa walka %d tur (%s/%s/%d)" % (pd["tury"], pd["klasa"], pd["przeciwnik"], pd["poziom"]), pd, "{ tempo = 1 }", limit=150)
        if w:
            pomiar("długa %d tur ×1" % pd["tury"], w[0], w[1])
            sprawdz("3a'. długa walka: odtworzenie trwa ≥ czas dziennika (nic nie skrócone)",
                    (w[0].get("OstatniCzasTrwania") or 0) >= w[1]["czas"] - 0.3,
                    "(%.1f s odtworzenia, dziennik %.1f s)" % (w[0].get("OstatniCzasTrwania") or 0, w[1]["czas"]))
        t.steruj('"zamknij"')
        pk = Z["krotka"]
        w = walka("3b. krótka walka %d tury (%s/%s/%d)" % (pk["tury"], pk["klasa"], pk["przeciwnik"], pk["poziom"]), pk, "{ tempo = 1 }")
        if w:
            pomiar("krótka %d tury ×1" % pk["tury"], w[0], w[1])
        t.steruj('"zamknij"')
        # tempo ×4 kliknięte w trakcie
        p4 = Z["najdluzsza"]
        t.ziarno(p4["ziarno"])
        time.sleep(1.1)
        t.start(p4["klasa"], p4["przeciwnik"], str(p4["poziom"]), "{ tempo = 1 }")
        t.czekaj(("odtwarzanie",), 10)
        time.sleep(2.0)
        t.klik(GUI_WALKA + "Tempo.Tempo4.Przycisk")
        time.sleep(0.5)
        s = t.stan()
        sprawdz("3c. klik ×4 w trakcie walki zmienia tempo", (s.get("_odtw") or {}).get("tempo") == 4, "(%s)" % (s.get("_odtw") or {}).get("tempo"))
        s, dt = t.czekaj(("wynik",), 60)
        ocz = oczekiwana(p4)
        ocen_walke("3d. najdłuższa walka %d tur przy ×4" % ocz["tury"], s, p4, ocz)
        # od 15.11 finał (cios kończący, ujęcie pokonanego, radość) gra zawsze w ×1 — ok. 3–4 s ponad resztę/4
        sprawdz("3e. ×4 skraca odtwarzanie (≈ 2 s + reszta/4 + finał w ×1)", (s.get("OstatniCzasTrwania") or 99) < 2.5 + ocz["czas"] / 4 + 3 + 4,
                "(%.1f s, dziennik %.1f s)" % (s.get("OstatniCzasTrwania") or -1, ocz["czas"]))
        t.steruj('"zamknij"')
        t.steruj('"tempo", 1')
        # POMIŃ (gatunek poznany w p. 2, zgoda serwera) → wynik od razu, gracz wolny od razu (D-078), JESZCZE RAZ
        t.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", nil) return "ok"', "Server")
        pp = Z["shard"]
        t.ziarno(pp["ziarno"])
        time.sleep(1.1)
        t.start(pp["klasa"], pp["przeciwnik"], str(pp["poziom"]), "{ tempo = 1 }")
        t.czekaj(("odtwarzanie",), 10)
        time.sleep(2.5)
        t.klik(GUI_WALKA + "Pomin.Przycisk")
        s, dt = t.czekaj(("wynik",), 6)
        time.sleep(1.0)
        s = t.stan()
        ocz = oczekiwana(pp)
        sprawdz("3f. POMIŃ → panel wyniku od razu", s.get("OstatniStan") == "wynik" and s.get("OstatnioPominieto") is True, "(%.2f s)" % dt)
        ocen_walke("3g. po POMIŃ", s, pp, ocz, pelna=False)
        sprawdz("3h. po POMIŃ za zgodą serwera JESZCZE RAZ od razu dostępne (D-078: gracz wolny od razu)",
                s.get("OstatniaOdpowiedzPominiecia") == "ok" and s.get("_jeszczeZablokowany") is False
                and s.get("_jeszczeTekst") == "JESZCZE RAZ", "(%s, %s)" % (s.get("OstatniaOdpowiedzPominiecia"), s.get("_jeszczeTekst")))
        zostalo = t.czekaj_wolna(5)
        sprawdz("3j. serwer zwolnił sesję (NastepnaWalkaOd ≤ teraz)", zostalo <= 0.2, "(%.1f s)" % zostalo)
        t.klik(GUI_WALKA + "Wynik.Karta.JeszczeRaz.Przycisk")
        s, _ = t.czekaj(("odtwarzanie",), 10)
        sprawdz("3k. JESZCZE RAZ → nowa walka (ten sam wybór)", s.get("OstatniStan") == "odtwarzanie" and
                s.get("OstatniWybor") == "%s/%s/%d" % (pp["klasa"], pp["przeciwnik"], pp["poziom"]), "(%s)" % s.get("OstatniWybor"))

        # --- 4. reset postaci w trakcie
        time.sleep(2.0)
        t.luau('local p = game:GetService("Players"):GetPlayers()[1] p.Character:FindFirstChildOfClass("Humanoid").Health = 0 return "ok"', "Server")
        s4, _ = t.czekaj(("przerwano",), 6)
        time.sleep(0.6)
        s4 = t.stan()
        sprawdz("4a. reset przerywa walkę", s4.get("OstatniStan") == "przerwano")
        stan_po_walce("4b. zaraz po resecie", s4)
        for _ in range(40):
            time.sleep(0.5)
            s4 = t.stan()
            if s4["_hp"] > 0 and s4["_podmiotToHumanoid"]:
                break
        time.sleep(1.5)
        s4 = t.stan()
        stan_po_walce("4c. po odrodzeniu", s4)
        sprawdz("4d. po odrodzeniu własna postać widoczna", s4.get("_postacUkryta") == 0, "(%s)" % s4.get("_postacUkryta"))
        droga = t.klawisz_w()
        sprawdz("4e. po odrodzeniu postać chodzi", droga > 5, "(%.1f studa)" % droga)

        # --- 5. bezpieczeństwo (bez TestBezSesji)
        t.przy_tablicy()
        t.czekaj_wolna(60)
        pb = Z["play"][1]
        t.ziarno(pb["ziarno"])
        kod = (BEZPIECZENSTWO.replace("__KLASA__", pb["klasa"]).replace("__WROG__", pb["przeciwnik"]).replace("__POZIOM__", str(pb["poziom"])))
        b = json.loads(t.luau(kod, timeout=60))
        ocz = oczekiwana(pb)
        zycie_ocz = S.symuluj(WZ.postac(pb["klasa"], pb["poziom"]), {"potwor": pb["przeciwnik"], "poziom": pb["poziom"]}, 1)["strony"]["gracz"]["zycie"]
        for k in ("zla_klasa", "poziom_liczba", "poziom_spoza", "zly_wrog", "nie_tabela", "bez_argumentow"):
            sprawdz("5a. zły wybór „%s” → odmowa zly_wybor" % k, b[k].get("ok") is False and b[k].get("powod") == "zly_wybor", str(b[k]))
        z = b["z_liczbami"]
        sprawdz("5b. liczby od klienta zignorowane (ziarno i statystyki serwera)",
                z.get("ok") and z.get("ziarno") == pb["ziarno"] and z.get("tury") == ocz["tury"] and z.get("zycie") == zycie_ocz
                and (z.get("zloto") or 0) < 1e6, str(z))
        sprawdz("5c. druga prośba w 1 s → za_szybko", b["za_szybko"].get("powod") == "za_szybko", str(b["za_szybko"]))
        sprawdz("5d. prośba w trakcie sesji walki → walka_trwa", b["w_trakcie"].get("powod") == "walka_trwa", str(b["w_trakcie"]))
        t.daleko()
        time.sleep(1.2)
        d = json.loads(t.luau('task.wait(1.1) local r = workspace.TestWalki2.Zdalne.RozpocznijWalke2:InvokeServer({ klasa = "mag", '
                              'przeciwnik = "lesny_slime", poziom = "1" }) return game:GetService("HttpService"):JSONEncode(r)'))
        sprawdz("5e. prośba z daleka (≈ 33 studów) → za_daleko", d.get("powod") == "za_daleko" and not d.get("walka"), str({k: d.get(k) for k in ("ok", "powod", "odleglosc")}))
        sprawdz("5f. bez walki nie ma łupu (odmowy nie niosą dziennika ani łupu)",
                all("zloto" not in str(b[k]) or b[k].get("zloto") is None for k in ("zla_klasa", "za_szybko", "w_trakcie")) and "lup" not in d)
        t.przy_tablicy()

        # --- 6. obcy w kadrze
        t.luau(OBCY, "Server")
        time.sleep(1.0)
        przed = t.luau(STAN_OBCYCH).strip()
        t.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", true) return "ok"', "Server")
        t.czekaj_wolna(60)
        time.sleep(1.1)
        t.ziarno(Z["play"][2]["ziarno"])
        p6 = Z["play"][2]
        t.start(p6["klasa"], p6["przeciwnik"], str(p6["poziom"]), "nil")
        t.czekaj(("odtwarzanie",), 10)
        time.sleep(1.0)
        w_trakcie = t.luau(STAN_OBCYCH).strip()
        t.steruj('"pomin", true')   # wymuszony pokaz (D-078: bez zgody serwera sam przycisk by nie zadziałał)
        time.sleep(0.5)
        t.steruj('"zamknij"')
        time.sleep(1.0)
        po = t.luau(STAN_OBCYCH).strip()
        sprawdz("6. obcy w pudle sceny i z tagiem: schowani w walce, widoczni przed i po", przed == "0 0" and w_trakcie == "1 1" and po == "0 0",
                "(przed %s, w trakcie %s, po %s)" % (przed, w_trakcie, po))
        t.luau('workspace.TestWalki2.TestowyIntruz:Destroy() return "ok"', "Server")

        # --- 7. symulacja publikacji
        kopia = zrodlo_serwera.replace('game:GetService("RunService"):IsStudio()', "false", 1)
        poziom = 3
        while ("]" + "=" * poziom + "]") in kopia:
            poziom += 1
        literal = "[" + "=" * poziom + "[\n" + kopia + "]" + "=" * poziom + "]"
        w7 = t.luau(PUBLIKACJA.replace("__ZRODLO__", literal), "Server").strip()
        time.sleep(0.8)
        klient = t.luau('return tostring(workspace.TestWalki2:FindFirstChild("ProbaPublikacji") ~= nil)').strip()
        sprawdz("7. poza Studio serwer usuwa swój kontener (serwer i klient)", w7 == "USUNIETY" and klient == "false",
                "(serwer: %s, klient widzi folder: %s)" % (w7, klient))
        t.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", nil) workspace.TestWalki2:SetAttribute("ZiarnoTestowe", nil) return "ok"', "Server")

        # --- 8. konsola
        kons = t.konsola()
        zle = [w for w in kons.splitlines() if "TestWalki2" in w]
        sprawdz("8. konsola bez komunikatów z TestWalki2", not zle, "\n".join(zle[:8]))
        obce = [w for w in kons.splitlines() if ("rror" in w or "arn" in w) and "TestWalki2" not in w]
        log("  (inne komunikaty konsoli, nie z naszego kodu: %d, np. %s)" % (len(obce), obce[0][:120] if obce else "—"))

    sprawdz("Studio wróciło do trybu Edit", getattr(t, "edit_po", False))
    with open(os.path.join(TU, "wynik_play.json"), "w", encoding="utf-8") as f:
        json.dump({"wyniki": WYNIKI, "pomiary": POMIARY, "data": time.strftime("%Y-%m-%d %H:%M")}, f, ensure_ascii=False, indent=1)
    zle = [n for n, ok in WYNIKI if not ok]
    log("WYNIK: %d/%d zaliczonych%s" % (len(WYNIKI) - len(zle), len(WYNIKI), "" if not zle else " — nie: " + "; ".join(zle)))
    sys.exit(1 if zle else 0)


if __name__ == "__main__":
    main()
