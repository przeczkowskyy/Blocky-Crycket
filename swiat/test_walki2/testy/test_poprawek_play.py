#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test w trybie PLAY poprawek po niezależnym przeglądzie prototypu walki v2 (sam wraca do trybu Edit).

    python -B swiat/test_walki2/testy/test_poprawek_play.py              # wszystko → testy/wynik_poprawek.json
    python -B swiat/test_walki2/testy/test_poprawek_play.py --tylko kadr,paski

Części (--tylko):
  kadr    KAMERA: w chwili trafienia (i tuż przed nim, i tuż po) obaj aktorzy są w kadrze, a cel nie chowa się za
          atakującym — dla każdej umiejętności ataku (pocisk, krytyk przy Potężnym cięciu, wyskok przy Uderzeniu z góry
          i reszta) oraz dla każdego trafienia w długiej walce. Pomiar: Sygnaly/Sterowanie „kadr” — ułamek części aktora
          w kadrze 16:9 i ułamek niezasłoniętych przez drugiego aktora (promień z kamery).
  zero    „−0”: trafienie w całości na tarczy (blok Wojownika i zwykły cios) pokazuje „TARCZA −n”, a nie „−0”.
  efekt   napis i wygląd statusu (v3): „SPOWOLNIENIE!” i lód przy lodowym pocisku; „OGŁUSZENIE!” z pnączami przy
          uścisku korzeni i z gwiazdkami przy ogłuszającym uderzeniu (nazwa z dziennika).
  wynik   odmiana liczebników w panelu wyniku („— 3 tury”, „w 1 turze”, „N zdarzeń / zdarzenia”).
  odmowa  odmowa serwera po WALCZ: komunikat dla gracza (dymek z dala od tablicy; przy tablicy panel z polem Status).
  paski   paski, licznik tury i ikony efektów z licznikami NA EKRANIE po każdym zdarzeniu kilku walk = stan silnika
          (port w Pythonie z podglądem stanu efektów przy każdym zdarzeniu) — niezależnie od księgowości odtwarzacza.
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
from sesja_play import SesjaPlay, log  # noqa: E402

PROGI = {"wKadrze": 0.6, "odslonietyCel": 0.45, "odslonietyAtak": 0.3}
WYNIKI = []


def wynik(nazwa, ok, opis=""):
    WYNIKI.append({"test": nazwa, "ok": bool(ok), "opis": opis})
    log("%s %s %s" % ("OK  " if ok else "BŁĄD", nazwa, opis))


def ziarna():
    with open(os.path.join(TU, "ziarna.json"), encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------- port silnika z podglądem stanu
def dziennik_ze_stanem(klasa, wrog, poziom, ziarno):
    """Walka z portu + po każdym zdarzeniu migawka stanu silnika: życie, tura, efekty stron (id → tury)."""
    migawki = []
    oryginal = S.zdarzenie

    def zdarzenie(w, typ, kto, cel, trwa, pola):
        z = oryginal(w, typ, kto, cel, trwa, pola)
        migawki.append({"tura": w["tura"], "efekty": {s: {e["id"]: e["trwa"] for e in w["stan"][s]["efekty"]} for s in ("gracz", "wrog")}})
        return z
    S.zdarzenie = zdarzenie
    try:
        w = S.symuluj(WZ.postac(klasa, poziom), {"potwor": wrog, "poziom": poziom}, ziarno)
    finally:
        S.zdarzenie = oryginal
    return w, migawki


def dziennik(p):
    return S.symuluj(WZ.postac(p["klasa"], p["poziom"]), {"potwor": p["przeciwnik"], "poziom": p["poziom"]}, p["ziarno"])


# --------------------------------------------------------------------------- pomocnicze Play
def start(s, klasa, wrog, poziom, ziarno, opcje="{ reczny = true }"):
    s.steruj('"zamknij"')
    time.sleep(0.8)
    s.ziarno(ziarno)
    s.start(klasa, wrog, str(poziom), opcje)
    st, _ = s.czekaj(("odtwarzanie",), 15)
    return st.get("OstatniStan") == "odtwarzanie"


def przewin(s, tau):
    return json.loads(s.steruj('"przewinDo", %f' % max(0.0, tau)))


def kadr(s):
    return json.loads(s.steruj('"kadr"'))


def napisy(s):
    """Napisy tego trafienia: widoczne i czekające w kolejce przy postaci (od 15.11 napisy wchodzą po kolei)."""
    d = json.loads(s.steruj('"napisy"'))
    return (d.get("napisy") or []) + (d.get("czekajace") or [])


def ocen_kadr(k, atak, cel):
    """Progi zależą od typu ujęcia: w ujęciach dwóch postaci obie w kadrze (≥ 60% części), cel niezasłonięty (≥ 45%);
    zza pleców postać na pierwszym planie może być ucięta (≥ 25%); zbliżenie celu pokazuje z atakującego tylko rękę
    z bronią (≥ 15%). Ujęcie jednej postaci (na siebie, efekt) w chwili ataku to błąd."""
    a, d = k[atak], k[cel]
    typ = k.get("ujecie")
    progA, progD = PROGI["wKadrze"], PROGI["wKadrze"]
    if typ == "zaAtakujacym":
        progA = 0.25
    elif typ == "zaBroniacym":
        progD = 0.25
    elif typ == "zblizenie":
        progA = 0.15
    ok = (typ not in ("naSiebie", "efekt") and a["wKadrze"] >= progA and d["wKadrze"] >= progD
          and d["odsloniete"] >= min(progD, PROGI["odslonietyCel"]) and a["odsloniete"] >= min(progA, PROGI["odslonietyAtak"]))
    opis = "%s: atak w kadrze %.2f odsł. %.2f | cel w kadrze %.2f odsł. %.2f" % (
        k.get("ujecie"), a["wKadrze"], a["odsloniete"], d["wKadrze"], d["odsloniete"])
    return ok, opis


# --------------------------------------------------------------------------- części testu
def test_kadr(s, Z):
    # 1) każda umiejętność ataku (walka z ziarna.json, w której trafia): tuż przed trafieniem, w chwili trafienia, tuż po
    for uid, p in Z["umiejetnosci"].items():
        if S.UMIEJETNOSCI[uid]["cel"] == "sam":
            continue
        w = dziennik(p)
        idx = next(i for i, z in enumerate(w["dziennik"]) if z["umiejetnosc"] == uid and z["typ"] == "umiejetnosc")
        z = w["dziennik"][idx]
        if not start(s, p["klasa"], p["przeciwnik"], p["poziom"], p["ziarno"]):
            wynik("kadr " + uid, False, "walka nie wystartowała")
            continue
        st = przewin(s, z["t"] + 0.01)
        hit = st.get("trafienie") or (z["t"] + z["trwa"] * 0.5)
        zle = []
        for dt in (-0.25, 0.0, 0.2):
            przewin(s, hit + dt)
            ok, opis = ocen_kadr(kadr(s), z["kto"], z["cel"])
            if not ok:
                zle.append("τ=trafienie%+.2f %s" % (dt, opis))
        wynik("kadr %s (%s/%s/%d, zd. %d, %s)" % (uid, p["klasa"], p["przeciwnik"], p["poziom"], idx + 1, st.get("styl")),
              not zle, "; ".join(zle) if zle else opis)
    # 2) wszystkie trafienia w długiej walce i krytyki w walkach Play
    for nazwa, p in (("dluga", Z["dluga"]), ("najdluzsza", Z["najdluzsza"])):
        w = dziennik(p)
        if not start(s, p["klasa"], p["przeciwnik"], p["poziom"], p["ziarno"]):
            wynik("kadr " + nazwa, False, "walka nie wystartowała")
            continue
        zle, n = [], 0
        for i, z in enumerate(w["dziennik"]):
            if z["typ"] not in ("cios", "krytyk", "blok", "unik") and not (z["typ"] == "umiejetnosc" and z["kto"] != z["cel"]):
                continue
            st = przewin(s, z["t"] + 0.01)
            hit = st.get("trafienie") or (z["t"] + z["trwa"] * 0.5)
            przewin(s, hit)
            n += 1
            ok, opis = ocen_kadr(kadr(s), z["kto"], z["cel"])
            if not ok:
                zle.append("zd. %d %s %s: %s" % (i + 1, z["typ"], z["umiejetnosc"], opis))
        # unik: cel z założenia schodzi z linii — liczymy tylko, czy jest w kadrze; reszta jak wyżej
        wynik("kadr %s: %d trafień (%s/%s/%d)" % (nazwa, n, p["klasa"], p["przeciwnik"], p["poziom"]),
              len(zle) == 0, "; ".join(zle[:6]) + (" … i %d innych" % (len(zle) - 6) if len(zle) > 6 else ""))


def test_zero(s):
    # (klasa, wróg, poziom, ziarno, numer zdarzenia od 0, typ) — z przeszukania portu: obrażenia 0, pochłonięte > 0
    for klasa, wrog, poziom, ziarno, idx, typ in (("wojownik", "cierniowy_wilk", 10, 475464, 11, "blok"),
                                                  ("mag", "cierniowy_wilk", 10, 150785, 17, "cios")):
        w = dziennik({"klasa": klasa, "przeciwnik": wrog, "poziom": poziom, "ziarno": ziarno})
        z = w["dziennik"][idx] if idx < len(w["dziennik"]) else None
        if not z or z["typ"] != typ or z["obrazenia"] != 0 or not z.get("pochloniete"):
            # dziennik v3 (17.11.2026): tarcza procentowa — trafienie „w całości na tarczy” nie występuje (przeszukanie
            # 17 955 walk: 3 klasy × 5 potworów × poziomy 1/5/10 × ziarna 1–399, zero takich zdarzeń); ziarna z v2 nie pasują
            log("  zero: nie dotyczy dziennika v3 (%s/%s/%d ziarno %d nie ma trafienia 0 z tarczą)" % (klasa, wrog, poziom, ziarno))
            continue
        if not start(s, klasa, wrog, poziom, ziarno):
            wynik("bez −0 (%s)" % typ, False, "walka nie wystartowała")
            continue
        st = przewin(s, z["t"] + 0.01)
        przewin(s, (st.get("trafienie") or z["t"] + z["trwa"] * 0.5) + 0.04)
        teksty = [n["tekst"] for n in napisy(s)]
        zero = [t for t in teksty if t.replace("−", "-").strip() in ("-0", "−0")]
        tarcza = [t for t in teksty if t.startswith("TARCZA")]
        wynik("bez −0 przy pełnej tarczy (%s, %s/%s/%d ziarno %d, zd. %d)" % (typ, klasa, wrog, poziom, ziarno, idx + 1),
              not zero and tarcza == ["TARCZA −%d" % z["pochloniete"]], "napisy: %s" % teksty)


def test_efekt(s):
    # v3: lodowy pocisk SPOWALNIA (lód), uścisk korzeni i ogłuszające uderzenie OGŁUSZAJĄ (pnącza, gwiazdki)
    oczek = {"lodowy_pocisk": "Krysztal", "uscisk_korzeni": "Pnacze", "ogluszajace_uderzenie": "Gwiazdka"}
    efekt_um = {"lodowy_pocisk": "spowolnienie", "uscisk_korzeni": "ogluszenie", "ogluszajace_uderzenie": "ogluszenie"}
    znalezione = {}
    for klasa in WZ.KLASY:
        for wrog in [p["id"] for p in S.PRZECIWNICY_LISTA]:
            for zi in range(1, 300):
                ziarno = zi * 104729 + 7
                w = S.symuluj(WZ.postac(klasa, 5), {"potwor": wrog, "poziom": 5}, ziarno)
                d = w["dziennik"]
                for i in range(1, len(d)):
                    if d[i]["typ"] == "efekt_nalozony" and d[i - 1]["umiejetnosc"] in oczek \
                            and d[i]["efekt"] == efekt_um[d[i - 1]["umiejetnosc"]] \
                            and d[i - 1]["umiejetnosc"] not in znalezione:
                        znalezione[d[i - 1]["umiejetnosc"]] = (klasa, wrog, 5, ziarno, i)
                if len(znalezione) == len(oczek):
                    break
            if len(znalezione) == len(oczek):
                break
        if len(znalezione) == len(oczek):
            break
    for uid, (klasa, wrog, poziom, ziarno, i) in znalezione.items():
        w = dziennik({"klasa": klasa, "przeciwnik": wrog, "poziom": poziom, "ziarno": ziarno})
        z = w["dziennik"][i]
        if not start(s, klasa, wrog, poziom, ziarno):
            wynik("spowolnienie " + uid, False, "walka nie wystartowała")
            continue
        przewin(s, z["t"] + 0.05)
        teksty = [n["tekst"] for n in napisy(s)]
        czesci = json.loads(s.luau(
            'local k = workspace.TestWalki2:FindFirstChild("ScenaLokalna") local n = {} '
            'if k then for _, d in k:GetDescendants() do if d:IsA("BasePart") then n[d.Name] = (n[d.Name] or 0) + 1 end end end '
            'return game:GetService("HttpService"):JSONEncode(n)'))
        napis, inny = ("SPOWOLNIENIE!", "OGŁUSZENIE!") if efekt_um[uid] == "spowolnienie" else ("OGŁUSZENIE!", "SPOWOLNIENIE!")
        ok = napis in teksty and inny not in teksty and czesci.get(oczek[uid], 0) > 0
        wynik("%s od %s (%s/%s/%d ziarno %d, zd. %d)" % (efekt_um[uid], uid, klasa, wrog, poziom, ziarno, i + 1), ok,
              "napisy %s; ozdoba %s: %d szt." % (teksty, oczek[uid], czesci.get(oczek[uid], 0)))


def test_wynik(s, Z):
    for p in (Z["krotka"], Z["dluga"]):
        w = dziennik(p)
        if not start(s, p["klasa"], p["przeciwnik"], p["poziom"], p["ziarno"]):
            wynik("odmiana w panelu wyniku", False, "walka nie wystartowała")
            continue
        s.steruj('"przewinDo", 1000')
        time.sleep(1.2)
        t = json.loads(s.luau(
            'local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("TestWalki2Cutscenka") '
            'local w = g and g:FindFirstChild("Wynik", true) '
            'return game:GetService("HttpService"):JSONEncode({ podtytul = w and w:FindFirstChild("Podtytul", true).Text, '
            'stopka = w and w:FindFirstChild("Stopka", true).Text })'))
        n, zd = w["tury"], len(w["dziennik"])

        def odm(x, a, b, c):
            return "%d %s" % (x, a if x == 1 else (b if 2 <= x % 10 <= 4 and not 12 <= x % 100 <= 14 else c))
        if w["wynik"] == "wygrana":
            pod = "pokonany w 1 turze" if n == 1 else "pokonany w %d turach" % n
        else:
            pod = "był silniejszy — " + odm(n, "tura", "tury", "tur")
        ok = pod in (t["podtytul"] or "") and odm(n, "tura", "tury", "tur") in t["stopka"] and odm(zd, "zdarzenie", "zdarzenia", "zdarzeń") in t["stopka"]
        wynik("odmiana w panelu wyniku (tury: %d, zdarzenia: %d, %s)" % (n, zd, w["wynik"]), ok, "%s | %s" % (t["podtytul"], t["stopka"]))


def test_odmowa(s):
    s.steruj('"zamknij"')
    time.sleep(1.0)
    s.luau('workspace.TestWalki2:SetAttribute("OstatniKomunikat", nil) return "ok"')
    # 1) z dala od tablicy: serwer odmawia (za_daleko) → dymek z powodem
    s.daleko()
    time.sleep(0.6)
    s.ziarno(None)
    s.start("wojownik", "lesny_slime", "5", "nil")
    st, _ = s.czekaj(("odmowa", "odtwarzanie"), 10)
    time.sleep(0.5)
    g = json.loads(s.luau(
        'local pg = game:GetService("Players").LocalPlayer.PlayerGui local d = pg:FindFirstChild("TestWalki2Komunikat") '
        'return game:GetService("HttpService"):JSONEncode({ dymek = d and d:FindFirstChild("Dymek") and d.Dymek.Text, '
        'komunikat = workspace.TestWalki2:GetAttribute("OstatniKomunikat"), stan = workspace.TestWalki2:GetAttribute("OstatniStan"), '
        'odmowa = workspace.TestWalki2:GetAttribute("OstatniaOdmowa") })'))
    wynik("odmowa za_daleko → dymek z powodem", g["stan"] == "odmowa" and g["odmowa"] == "za_daleko" and g["dymek"]
          and "daleko" in g["dymek"].lower(), str(g))
    # 2) przy tablicy: zły wybór (spoza listy) → panel wyboru z komunikatem w polu Status
    s.przy_tablicy()
    time.sleep(1.2)
    s.start("czarnoksieznik", "lesny_slime", "5", "nil")
    st, _ = s.czekaj(("odmowa", "odtwarzanie"), 10)
    time.sleep(0.6)
    g = json.loads(s.luau(
        'local pg = game:GetService("Players").LocalPlayer.PlayerGui local p = pg:FindFirstChild("TestWalki2Wybor") '
        'local st = p and p:FindFirstChild("Status", true) '
        'return game:GetService("HttpService"):JSONEncode({ panel = p ~= nil, status = st and st.Text, '
        'odmowa = workspace.TestWalki2:GetAttribute("OstatniaOdmowa") })'))
    wynik("odmowa zly_wybor przy tablicy → panel z komunikatem", g["panel"] and g["odmowa"] == "zly_wybor" and bool(g["status"]), str(g))
    s.luau('local p = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("TestWalki2Wybor") if p then p:Destroy() end return "ok"')


ODCZYT_EKRANU = r'''
local s = workspace.TestWalki2.Sygnaly.Sterowanie
s:Invoke("przewinDo", __TAU__)
local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("TestWalki2Cutscenka")
local w = { tura = g.Kadr.Tura.Text }
for strona, nazwa in { gracz = "TabliczkaGracza", wrog = "TabliczkaWroga" } do
	local t = g.Kadr[nazwa]
	local ef = {}
	for _, e in t.Efekty:GetChildren() do
		if e:IsA("Frame") and string.sub(e.Name, 1, 6) == "Efekt_" then
			ef[string.sub(e.Name, 7)] = tonumber(e.Licznik.Tury.Text)
		end
	end
	w[strona] = { liczba = t.Pasek.Liczba.Text, efekty = ef }
end
return game:GetService("HttpService"):JSONEncode(w)
'''


def test_paski(s, Z):
    proby = [("wojownik", "cierniowy_wilk", 1, 53484), ("mag", "cierniowy_wilk", 5, 910854),
             ("zwiadowca", "lesny_troll", 10, 950601), ("wojownik", "lesny_slime", 10, 4043),
             (Z["dluga"]["klasa"], Z["dluga"]["przeciwnik"], Z["dluga"]["poziom"], Z["dluga"]["ziarno"])]
    for klasa, wrog, poziom, ziarno in proby:
        w, mig = dziennik_ze_stanem(klasa, wrog, poziom, ziarno)
        if not start(s, klasa, wrog, poziom, ziarno):
            wynik("paski %s/%s/%d" % (klasa, wrog, poziom), False, "walka nie wystartowała")
            continue
        maks = {"gracz": w["strony"]["gracz"]["zycie"], "wrog": w["strony"]["wrog"]["zycie"]}
        zle, n = [], 0
        for i, z in enumerate(w["dziennik"]):
            if z["typ"] == "efekt_koniec":
                continue  # silnik zdejmuje efekty w pętli końca tury — migawka w środku pętli nie jest stanem „po zdarzeniu”
            e = json.loads(s.luau(ODCZYT_EKRANU.replace("__TAU__", "%f" % (z["t"] + z["trwa"] - 0.02))))
            n += 1
            m = mig[i]
            for strona, hp in (("gracz", z["hp_gracz"]), ("wrog", z["hp_wrog"])):
                if e[strona]["liczba"] != "%d / %d" % (hp, maks[strona]):
                    zle.append("zd. %d %s: pasek %r, silnik %d" % (i + 1, strona, e[strona]["liczba"], hp))
                ekran = {k: v for k, v in (e[strona]["efekty"] or {}).items()}
                silnik = {k: max(1, v) for k, v in m["efekty"][strona].items()}
                if ekran != silnik:
                    zle.append("zd. %d %s: efekty na ekranie %s, w silniku %s" % (i + 1, strona, ekran, silnik))
            if e["tura"] != "TURA %d" % m["tura"]:
                zle.append("zd. %d: %r, silnik tura %d" % (i + 1, e["tura"], m["tura"]))
        wynik("paski, tura i efekty = silnik (%s/%s/%d ziarno %d, %d zdarzeń)" % (klasa, wrog, poziom, ziarno, n), not zle, "; ".join(zle[:5]))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tylko", default="")
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    czesci = [x for x in a.tylko.split(",") if x] or ["kadr", "zero", "efekt", "wynik", "odmowa", "paski"]
    Z = ziarna()
    t0 = time.time()
    with SesjaPlay(a.studio) as s:
        for _ in range(40):  # ekran ładowania gry
            if s.luau('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("LoadingScreen") '
                      'local b = g and g:FindFirstChild("Background") '
                      'return tostring(g == nil or not g.Enabled or b == nil or not b.Visible or b.BackgroundTransparency >= 0.99)').strip() == "true":
                break
            time.sleep(0.5)
        s.przy_tablicy()
        s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", true) return "ok"', "Server")
        try:
            if "kadr" in czesci:
                test_kadr(s, Z)
            if "zero" in czesci:
                test_zero(s)
            if "efekt" in czesci:
                test_efekt(s)
            if "wynik" in czesci:
                test_wynik(s, Z)
            if "paski" in czesci:
                test_paski(s, Z)
            if "odmowa" in czesci:
                test_odmowa(s)
            s.steruj('"zamknij"')
        finally:
            try:
                s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", nil) workspace.TestWalki2:SetAttribute("ZiarnoTestowe", nil) return "ok"', "Server")
            except Exception:  # noqa: BLE001
                pass
        kons = s.konsola()
        zle = [w for w in kons.splitlines() if "TestWalki2" in w]
        wynik("konsola bez komunikatów z TestWalki2", not zle, "; ".join(z[:200] for z in zle[:5]))
    wynik("Studio wróciło do trybu Edit", s.edit_po)
    dobre = sum(w["ok"] for w in WYNIKI)
    log("WYNIK: %d/%d OK (%.0f s)" % (dobre, len(WYNIKI), time.time() - t0))
    with open(os.path.join(TU, "wynik_poprawek.json"), "w", encoding="utf-8") as f:
        json.dump({"data": time.strftime("%Y-%m-%d %H:%M"), "wynik": "%d/%d" % (dobre, len(WYNIKI)), "testy": WYNIKI, "progi_kadru": PROGI},
                  f, ensure_ascii=False, indent=1)
    sys.exit(0 if dobre == len(WYNIKI) else 1)


if __name__ == "__main__":
    main()
