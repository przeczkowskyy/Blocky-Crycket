#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pojedyncze, pełne zrzuty do raportu dla ludzi (tryb Play; sam wraca do trybu Edit) → klatki/raport_*.jpg.

    python -B swiat/test_walki2/testy/zrzuty_raportu.py

Arkusze klatek (klatki/walka_*.jpg) mają po 8 małych kadrów — dobre do sprawdzania, za drobne na telefon. Tu powstaje
po jednym dużym kadrze 16:9 z prawdziwego odtwarzania (te same ziarna co w testach): panel wyboru, krytyk, kula ognia
w locie, spowolnienie na postaci (lód), panel wyniku z łupem.
"""
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

WYJ = os.path.join(KATALOG, "klatki")


def kadr169(im):
    w, h = im.size
    if w / h > 16 / 9:
        nw = int(h * 16 / 9)
        return im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    nh = int(w * 9 / 16)
    return im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))


def dziennik(klasa, wrog, poziom, ziarno):
    return S.symuluj(WZ.postac(klasa, poziom), {"potwor": wrog, "poziom": poziom}, ziarno)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    with open(os.path.join(TU, "ziarna.json"), encoding="utf-8") as f:
        Z = json.load(f)
    kula = Z["umiejetnosci"]["kula_ognia"]
    shard = Z["shard"]
    # (nazwa pliku, wybór, funkcja chwili: dziennik → (indeks zdarzenia, przesunięcie od trafienia albo od początku))
    plan = [
        ("raport_2_krytyk", ("wojownik", "lesny_troll", 5, None), "krytyk"),
        ("raport_3_kula_ognia", (kula["klasa"], kula["przeciwnik"], kula["poziom"], kula["ziarno"]), "kula_ognia"),
        ("raport_4_spowolnienie", ("mag", "lesny_slime", 5, 209465), "spowolnienie"),
        ("raport_5_wynik", (shard["klasa"], shard["przeciwnik"], shard["poziom"], shard["ziarno"]), "wynik"),
    ]
    # spowolnienie od lodowego pocisku i potem utrata tury celu (cel żyje — ozdoba lodu widoczna)
    for zi in range(1, 600):
        ziarno = zi * 104729 + 7
        d = dziennik("mag", "lesny_troll", 5, ziarno)["dziennik"]
        zrodlo = None
        for z in d:
            if z["typ"] == "umiejetnosc" and z["umiejetnosc"] == "lodowy_pocisk":
                zrodlo = "lod"
            elif z["typ"] == "efekt_nalozony" and z["efekt"] == "spowolnienie" and zrodlo != "lod":
                zrodlo = None
            elif z["typ"] == "utrata_tury" and zrodlo == "lod" and z["kto"] == "wrog":
                plan[2] = ("raport_4_spowolnienie", ("mag", "lesny_troll", 5, ziarno), "utrata")
                break
        if plan[2][2] == "utrata":
            break
    # krytyk wręcz Wojownika: pierwsze ziarno, w którym jest
    for zi in range(1, 400):
        ziarno = zi * 7919 + 13
        w = dziennik("wojownik", "lesny_troll", 5, ziarno)
        if any(z["typ"] == "krytyk" and z["kto"] == "gracz" for z in w["dziennik"]):
            plan[0] = ("raport_2_krytyk", ("wojownik", "lesny_troll", 5, ziarno), "krytyk")
            break
    with SesjaPlay() as s:
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
            # 1) panel wyboru
            s.steruj('"zamknij"')
            time.sleep(0.8)
            s.steruj('"wybor"')
            time.sleep(1.2)
            kadr169(s.zrzut()).save(os.path.join(WYJ, "raport_1_panel_wyboru.jpg"), "JPEG", quality=90)
            s.luau('local g = game:GetService("Players").LocalPlayer.PlayerGui:FindFirstChild("TestWalki2Wybor") if g then g:Destroy() end return "ok"')
            for nazwa, (klasa, wrog, poziom, ziarno), co in plan:
                w = dziennik(klasa, wrog, poziom, ziarno)
                d = w["dziennik"]
                s.steruj('"zamknij"')
                time.sleep(1.0)
                s.ziarno(ziarno)
                s.start(klasa, wrog, str(poziom), "{ reczny = true }")
                st, _ = s.czekaj(("odtwarzanie",), 15)
                if st.get("OstatniStan") != "odtwarzanie":
                    log(nazwa, "nie wystartowało")
                    continue
                if co == "wynik":
                    s.steruj('"przewinDo", 1000')
                    time.sleep(2.2)
                else:
                    if co == "krytyk":
                        i = next(i for i, z in enumerate(d) if z["typ"] == "krytyk" and z["kto"] == "gracz")
                        dt = 0.06
                    elif co == "kula_ognia":
                        i = next(i for i, z in enumerate(d) if z["umiejetnosc"] == "kula_ognia" and z["typ"] == "umiejetnosc")
                        dt = -0.12
                    elif co == "utrata":
                        i = next(i for i, z in enumerate(d) if z["typ"] == "utrata_tury" and z["kto"] == "wrog")
                        dt = None
                    else:
                        i = next(i for i, z in enumerate(d) if z["typ"] == "efekt_nalozony" and z["efekt"] == "spowolnienie")
                        dt = None
                    # napisy starzeją się w czasie rzeczywistym: najpierw do chwili tuż przed zdarzeniem, przerwa, aż
                    # stare napisy znikną, dopiero potem do kadru (inaczej na zrzucie piętrzą się napisy z kilku zdarzeń)
                    s.steruj('"przewinDo", %f' % max(0.0, d[i]["t"] - 0.05))
                    time.sleep(1.4)
                    o = json.loads(s.steruj('"przewinDo", %f' % (d[i]["t"] + 0.01)))
                    if co == "utrata":
                        s.steruj('"przewinDo", %f' % (d[i]["t"] + 0.45))
                    elif dt is None:
                        s.steruj('"przewinDo", %f' % (d[i]["t"] + d[i]["trwa"] + 0.5))
                    else:
                        s.steruj('"przewinDo", %f' % ((o.get("trafienie") or d[i]["t"] + 0.5) + dt))
                    time.sleep(0.25)
                im, o = s.zrzut_odtwarzacza()
                kadr169(im).save(os.path.join(WYJ, nazwa + ".jpg"), "JPEG", quality=90)
                log("zrzut:", nazwa, "%s/%s/%d ziarno %d" % (klasa, wrog, poziom, ziarno), o.get("ujecie"))
            s.steruj('"zamknij"')
        finally:
            try:
                s.luau('workspace.TestWalki2:SetAttribute("TestBezSesji", nil) workspace.TestWalki2:SetAttribute("ZiarnoTestowe", nil) return "ok"', "Server")
            except Exception:  # noqa: BLE001
                pass


if __name__ == "__main__":
    main()
