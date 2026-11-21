#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba zabawek w emulacji telefonu 667 × 375 (układ ekranu w punktach telefonu, czas klatki, zrzuty tel_eat / tel_lure).

    python -B swiat/zabawki/testy/proba_telefon.py --studio <id>

Emulacja: atrybut lokalnego gracza ZT_Emulacja = Vector2(667, 375) — ekran zabawek ma rozmiar telefonu i jest powiększony
do okna Studio (obraz 3D ma proporcje okna, zbliżone do telefonu).
"""
import argparse
import json
import math
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import proba_play as PP  # noqa: E402
from studio_mcp import StudioMCP  # noqa: E402

PROST = ('local HS = game:GetService("HttpService") local g = game:GetService("Players").LocalPlayer.PlayerGui.Zabawki '
         'local e = g.Ekran local k = e.UIScale.Scale local w = {} '
         'for _, n in { "Menu.Srodek.Zabawka1", "Menu.Srodek.Zabawka2", "Gora.Menu", "Forma", "Dash.Dash", "Licznik", "Podpowiedz" } do '
         'local o = e for _, c in string.split(n, ".") do o = o and o:FindFirstChild(c) end '
         'local wid = o ~= nil local q = o while wid and q and q ~= e do if q:IsA("GuiObject") and not q.Visible then wid = false end q = q.Parent end if wid then '
         'w[n] = { (o.AbsolutePosition.X - e.AbsolutePosition.X) / k, (o.AbsolutePosition.Y - e.AbsolutePosition.Y) / k, o.AbsoluteSize.X / k, o.AbsoluteSize.Y / k } end end '
         'return HS:JSONEncode(w)')


def w_ekranie(r):
    return r[0] >= -1 and r[1] >= -1 and r[0] + r[2] <= 668 and r[1] + r[3] <= 376


def nachodza(r, q):
    return r[0] < q[0] + q[2] and q[0] < r[0] + r[2] and r[1] < q[1] + q[3] and q[1] < r[1] + r[3]


def ocen(p, nazwa, przyciski):
    r = json.loads(p.luau(PROST, "Client"))
    ekr = all(w_ekranie(x) for x in r.values())
    minpt = min((min(r[n][2], r[n][3]) for n in przyciski if n in r), default=0)
    lista = list(r.items())
    nak = [(a[0], b[0]) for i, a in enumerate(lista) for b in lista[i + 1:] if nachodza(a[1], b[1])]
    return r, ekr, minpt, nak


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio", required=True)
    a = ap.parse_args()
    with StudioMCP(timeout=240) as s:
        p = PP.P(s, a.studio)
        try:
            p.call("start_stop_play", {"is_start": True})
            PP.czekaj(lambda: p.luau('return tostring(workspace.%s:GetAttribute("KlientGotowy"))' % PP.K, "Client") == "true", 60, 0.5)
            p.luau(PP.BEZ_LISTY, "Client")
            p.ustaw("ZT_Emulacja", "Vector2.new(667, 375)")
            time.sleep(1.0)
            r, ekr, minpt, nak = ocen(p, "menu", ["Menu.Srodek.Zabawka1", "Menu.Srodek.Zabawka2"])
            PP.wynik("T1 ekran wyboru", ekr and minpt >= 44 and not nak and len(r) == 2, prostokaty=r, min_pt=round(minpt), nakladanie=nak)
            p.zrzut("tel_menu.jpg")
            # EAT & EVOLVE
            p.akcja('"wybor"', "1")
            time.sleep(1.2)
            st = p.serwer('"stan"')
            b = PP.moj_byt(st)
            zywe = [PP.Z["kulkiPoz"][i - 1] for i in st.get("kulkiZywe", [])]
            k = min(zywe, key=lambda q: math.hypot(q[0] - b["x"], q[1] - b["z"]))
            dx, dz = k[0] - b["x"], k[1] - b["z"]
            d = max(0.1, math.hypot(dx, dz))
            p.ustaw("ZT_TestSter", "Vector3.new(%f, %f, 3)" % (-dx / d, dz / d))
            time.sleep(3.0)
            r, ekr, minpt, nak = ocen(p, "eat", ["Gora.Menu", "Dash.Dash"])
            at = p.atr()
            p.zrzut("tel_eat.jpg")
            PP.wynik("T2 EAT & EVOLVE", ekr and minpt >= 44 and not nak and (at.get("ZT_Klatka") or 99) < 25,
                     prostokaty=r, min_pt=round(minpt), nakladanie=nak, klatka_ms=round(at.get("ZT_Klatka") or 0, 1), kamera_y=round(at.get("ZT_KameraY") or 0))
            # LURE A MONSTER: trzy zwabienia (zagroda pod kamerą), potem celowanie
            p.akcja('"menu"')
            time.sleep(0.5)
            p.akcja('"wybor"', "2")
            time.sleep(1.2)
            st = p.serwer('"stan"')
            zp = PP.W["zagrodyPoz"][st["slot"] - 1]
            for i, m in enumerate([q for q in st["potwory"] if q["strefa"] == 1][:3]):
                zt = 30 + i * 8
                p.serwer('"potwor_tu", %d, %f, %f' % (m["id"], zp[0], zt))
                moc = (zt - (zp[1] + PP.W["zagroda_gl"] / 2) - PP.W["zasieg_min"]) / (st["zasieg"] - PP.W["zasieg_min"])
                p.ustaw("ZT_TestRzut", "Vector2.new(0, %f)" % moc)
                time.sleep(2.4)
            time.sleep(4.0)
            p.ustaw("ZT_TestCel", "Vector2.new(-0.15, 0.55)")
            time.sleep(1.2)
            r, ekr, minpt, nak = ocen(p, "lure", ["Gora.Menu"])
            at = p.atr()
            p.zrzut("tel_lure.jpg")
            p.ustaw("ZT_TestCel", "false")
            PP.wynik("T3 LURE A MONSTER", ekr and minpt >= 44 and not nak and (at.get("ZT_Klatka") or 99) < 25 and (at.get("ZW_Ile") or 0) >= 3,
                     prostokaty=r, min_pt=round(minpt), nakladanie=nak, klatka_ms=round(at.get("ZT_Klatka") or 0, 1), zwabione=at.get("ZW_Ile"))
            p.ustaw("ZT_Emulacja", "nil")
        finally:
            p.call("start_stop_play", {"is_start": False})
            PP.czekaj(lambda: "Current Studio Mode: Edit" in p.call("get_studio_state")["text"], 40, 0.5)
    print("WYNIK:", sum(PP.wyniki.values()), "/", len(PP.wyniki))


if __name__ == "__main__":
    main()
