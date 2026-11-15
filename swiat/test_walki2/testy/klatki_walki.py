#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arkusze klatek z PRAWDZIWEGO odtwarzania walki v2 (tryb Play; sam wraca do trybu Edit).

    python -B swiat/test_walki2/testy/klatki_walki.py                    # wszystkie arkusze → swiat/test_walki2/klatki/
    python -B swiat/test_walki2/testy/klatki_walki.py --tylko kula_ognia,final_wygrana
    python -B swiat/test_walki2/testy/klatki_walki.py --lista            # nazwy arkuszy

Jak: walka z wybranym wyborem i ziarnem (atrybut serwera ZiarnoTestowe) startuje z opcją `reczny` — czas sceny stoi,
a skrypt przesuwa go (Sygnaly/Sterowanie „przewinDo”) do kolejnych chwil zdarzenia i robi zrzut z bieżącej kamery
odtwarzacza (z interfejsem walki). Chwile zdarzeń liczy port silnika w Pythonie (ten sam dziennik co na serwerze).
Arkusz: 8 klatek wierszami; podpis = czas sceny, numer i typ zdarzenia, umiejętność, ujęcie kamery.
Między walkami serwer ma ustawiony atrybut TestBezSesji (inaczej każda walka czekałaby na koniec poprzedniej).
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

BOK = (480, 270)


def zaladuj_ziarna():
    with open(os.path.join(TU, "ziarna.json"), encoding="utf-8") as f:
        return json.load(f)


def dziennik(p):
    return S.symuluj(WZ.postac(p["klasa"], p["poziom"]), {"potwor": p["przeciwnik"], "poziom": p["poziom"]}, p["ziarno"])


def okno_zdarzenia(w, i, klatek=8, przed=0.1, po=0.35):
    z = w["dziennik"][i]
    koniec = z["t"] + z["trwa"]
    # jeśli po zdarzeniu jest nałożenie efektu (z tej samej akcji), pokaż i je
    if i + 1 < len(w["dziennik"]) and w["dziennik"][i + 1]["typ"] == "efekt_nalozony":
        koniec = w["dziennik"][i + 1]["t"] + w["dziennik"][i + 1]["trwa"]
    a, b = z["t"] - przed, koniec + po
    return [a + (b - a) * k / (klatek - 1) for k in range(klatek)]


def plan_arkuszy(Z):
    """nazwa → (wybór, chwile sceny, opis). Wybór = wpis z ziarna.json."""
    plan = {}
    for uid, p in Z["umiejetnosci"].items():
        w = dziennik(p)
        idx = next((i for i, z in enumerate(w["dziennik"]) if z["umiejetnosc"] == uid and z["typ"] == "umiejetnosc"), None)
        if idx is None:
            idx = next(i for i, z in enumerate(w["dziennik"]) if z["umiejetnosc"] == uid)
        plan["umiejetnosc_" + uid] = (p, okno_zdarzenia(w, idx), "umiejętność %s (zdarzenie %d)" % (uid, idx + 1))

    def pierwsze(p, warunek, nazwa, opis, przed=0.1, po=0.35):
        w = dziennik(p)
        idx = next((i for i, z in enumerate(w["dziennik"]) if warunek(z)), None)
        if idx is not None:
            plan[nazwa] = (p, okno_zdarzenia(w, idx, przed=przed, po=po), "%s (zdarzenie %d)" % (opis, idx + 1))

    wt = Z["wszystkie_typy"]
    for p in [wt["wojownik"], wt["zwiadowca"], wt["mag"]] + Z["play"]:
        if "krytyk" not in plan:
            pierwsze(p, lambda z: z["typ"] == "krytyk", "krytyk", "krytyk wręcz (zwolnienie, wjazd kamery)")
        if "blok" not in plan:
            pierwsze(p, lambda z: z["typ"] == "blok", "blok", "blok tarczą Wojownika")
        if "unik" not in plan:
            pierwsze(p, lambda z: z["typ"] == "unik", "unik", "unik")
        if "tykniecie" not in plan:
            pierwsze(p, lambda z: z["typ"] == "efekt_tick" and z["obrazenia"] > 0, "tykniecie", "tyknięcie efektu", przed=0.2, po=0.3)
        if "utrata_tury" not in plan:
            pierwsze(p, lambda z: z["typ"] == "utrata_tury", "utrata_tury", "utrata tury (ogłuszenie)", przed=0.5, po=0.3)
    # finał: wygrana i przegrana
    for nazwa, p in (("final_wygrana", Z["shard"]), ("final_przegrana", Z["krotka"])):
        w = dziennik(p)
        ost = w["dziennik"][-1]
        a, b = ost["t"] - 0.1, w["czas"] - 0.01
        plan[nazwa] = (p, [a + (b - a) * k / 6 for k in range(7)] + ["wynik"], "finał (%s), ostatnia klatka = panel wyniku" % w["wynik"])
    # pełna walka z Leśnym Slime'em i ze Strażnikiem Gaju (właściwe modele od 15.11): przekrój od startu do panelu wyniku
    for klucz, uid in (("lesny_slime", "kwasny_plusk"), ("straznik_lasu", "uscisk_korzeni")):
        p = Z["umiejetnosci"].get(uid)
        if p and p["przeciwnik"] == klucz:
            w = dziennik(p)
            plan["pelna_walka_" + klucz] = (p, [0.6 + (w["czas"] - 0.6) * k / 14 for k in range(15)] + ["wynik"],
                                            "pełna walka z aktorem %s (%d tur, %s) — przekrój i panel wyniku"
                                            % (klucz, w["tury"], w["wynik"]))
    # długa walka: przekrój co kilka sekund (zróżnicowanie ujęć)
    p = Z["dluga"]
    w = dziennik(p)
    plan["dluga_walka"] = (p, [1.0 + (w["czas"] - 3.0) * k / 15 for k in range(16)], "długa walka (%d tur) — przekrój ujęć" % w["tury"])
    return plan


def kafel(im, podpis):
    from PIL import ImageDraw
    w, h = im.size
    if w / h > 16 / 9:
        nw = int(h * 16 / 9)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w * 9 / 16)
        im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    im = im.resize(BOK)
    d = ImageDraw.Draw(im)
    d.rectangle((0, BOK[1] - 15, BOK[0], BOK[1]), fill=(0, 0, 0))
    d.text((4, BOK[1] - 14), podpis, fill=(255, 255, 255))
    return im


def arkusz(kafle, sciezka, kolumny=4):
    from PIL import Image
    kol = min(kolumny, len(kafle))
    wiersze = (len(kafle) + kol - 1) // kol
    ark = Image.new("RGB", (kol * BOK[0], wiersze * BOK[1]), (20, 18, 24))
    for i, im in enumerate(kafle):
        ark.paste(im, ((i % kol) * BOK[0], (i // kol) * BOK[1]))
    ark.save(sciezka, "JPEG", quality=84)
    log("arkusz:", os.path.relpath(sciezka, REPO))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tylko", default="")
    ap.add_argument("--lista", action="store_true")
    ap.add_argument("--wyj", default=os.path.join(KATALOG, "klatki"))
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    Z = zaladuj_ziarna()
    plan = plan_arkuszy(Z)
    if a.lista:
        for n, (p, chwile, opis) in plan.items():
            print("%-34s %s/%s/%d ziarno %d — %s" % (n, p["klasa"], p["przeciwnik"], p["poziom"], p["ziarno"], opis))
        return
    plan["panel_wyboru"] = (None, [], "panel wyboru przy tablicy (C5): klasa, przeciwnik z rangą, poziom, WALCZ")
    wybrane = [x for x in a.tylko.split(",") if x] or list(plan)
    os.makedirs(a.wyj, exist_ok=True)
    raport = {}
    sciezka_raportu = os.path.join(a.wyj, "raport_klatek_walki.json")
    if os.path.isfile(sciezka_raportu):
        with open(sciezka_raportu, encoding="utf-8") as f:
            raport = json.load(f)
    with SesjaPlay(a.studio) as s:
        # ekran ładowania gry (LoadingScreen) zasłania scenę przez kilka sekund po starcie — czekamy, aż zniknie
        for _ in range(40):
            if s.luau('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("LoadingScreen") '
                      'local b = g and g:FindFirstChild("Background") '
                      'return tostring(g == nil or not g.Enabled or b == nil or not b.Visible or b.BackgroundTransparency >= 0.99)').strip() == "true":
                break
            time.sleep(0.5)
        time.sleep(1.0)
        s.przy_tablicy()
        s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", true) return "ok"', "Server")
        try:
            for nazwa in wybrane:
                p, chwile, opis = plan[nazwa]
                log(nazwa, "—", opis)
                if p is None:  # panel wyboru: otwarty jak po E przy tablicy, zrzut z kamery gracza
                    s.steruj('"zamknij"')
                    time.sleep(1.0)
                    s.steruj('"wybor"')
                    time.sleep(1.2)
                    im = s.zrzut()
                    w, h = im.size
                    im.save(os.path.join(a.wyj, "walka_panel_wyboru.jpg"), "JPEG", quality=86)
                    log("zrzut:", "walka_panel_wyboru.jpg", "%dx%d" % (w, h))
                    raport[nazwa] = {"opis": opis, "rozmiar": [w, h]}
                    s.luau('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("TestWalki2Wybor") if g then g:Destroy() end return "ok"')
                    continue
                s.steruj('"zamknij"')
                time.sleep(1.2)
                s.ziarno(p["ziarno"])
                s.start(p["klasa"], p["przeciwnik"], str(p["poziom"]), "{ reczny = true }")
                st, dt = s.czekaj(("odtwarzanie",), 15)
                if st.get("OstatniStan") != "odtwarzanie":
                    log("  nie wystartowało:", st.get("OstatniStan"), st.get("OstatniaOdmowa"))
                    raport[nazwa] = "nie wystartowało"
                    continue
                kafle = []
                for t in chwile:
                    if t == "wynik":
                        s.steruj('"przewinDo", 1000')
                        time.sleep(1.6)
                        im, o = s.zrzut_odtwarzacza()
                        kafle.append(kafel(im, "panel wyniku"))
                        continue
                    o = json.loads(s.steruj('"przewinDo", %f' % max(0.0, t)))
                    time.sleep(0.12)
                    im, o = s.zrzut_odtwarzacza()
                    kafle.append(kafel(im, "t=%.2f zd.%s %s %s | %s" % (o.get("tau", 0), o.get("biezace"), o.get("typ") or "",
                                                                      o.get("umiejetnosc") or "", o.get("ujecie"))))
                arkusz(kafle, os.path.join(a.wyj, "walka_%s.jpg" % nazwa))
                raport[nazwa] = {"wybor": "%s/%s/%d" % (p["klasa"], p["przeciwnik"], p["poziom"]), "ziarno": p["ziarno"], "opis": opis}
            s.steruj('"zamknij"')
        finally:
            try:
                s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", nil) workspace.TestWalki2:SetAttribute("ZiarnoTestowe", nil) return "ok"', "Server")
            except Exception:  # noqa: BLE001
                pass
        kons = s.konsola()
        zle = [w for w in kons.splitlines() if "TestWalki2" in w]
        log("konsola: komunikatów z TestWalki2:", len(zle))
        for w in zle[:10]:
            print("   ", w[:300])
    with open(sciezka_raportu, "w", encoding="utf-8") as f:
        json.dump(raport, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
