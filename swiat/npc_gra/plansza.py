#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plansza zbiorcza wszystkich NPC w skali gry obok człowieka (D-109) → podglady/npc_razem.jpg.

    python -B swiat/npc_gra/plansza.py [--wyj <folder>] [--robocze <folder poza repo>]

Jedno uruchomienie Blendera (pod wspólną blokadą): każda postać z obsady (ustawienia.json → npc) w skali swojego
stanowiska (bazar: stanowiska_bazaru; trenerzy: trenerzy.skala, golem: skala_golema), w pozie pierwszej klatki klipu
spoczynku (rekwizyty są ustawione na tę pozę), widok 3/4, jedna skala obrazu i wspólna linia stóp; pierwsza kolumna
to człowiek gracza (goły Rycerz, 5,3 studa). Rendery: swiat/postacie/rasy_plansze_blender.py (tylko odczyt),
składanie: Pillow. Status: propozycja.
"""
import argparse
import os
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
if TU in sys.path:
    sys.path.remove(TU)
sys.path.insert(0, TU)
import dane as DN  # noqa: E402

WYS = (-0.4, 10.4)                    # zakres wysokości kadru (studs): stopy … kryształ kostura maga
PX = 62.0                             # pikseli na stud
WIDOK = ("trzy_czwarte", (-0.75, 0.1, 1.0))
W_WIERSZU = 7
TLO, TEKST, TEKST2 = "#1d1729", "#ffffff", "#d9d0ee"


def poza_spoczynku(p, nazwa_klipu):
    """Obroty kości z klatki 0 klipu spoczynku: {kość: [rx, ry, rz]} (stopnie, układ danych)."""
    kl = next(k for k in p.klipy if k.nazwa == nazwa_klipu)
    poza = {}
    for (kosc, kanal) in kl.kanaly:
        if kanal == "obrot":
            poza[kosc] = [float(v) for v in kl.wartosc(kosc, "obrot", 0)]
    return poza


def plansza(cel_folder, robocze=None):
    from PIL import Image, ImageDraw
    from swiat.postacie import rasy, rasy_plansze as RP, rycerz
    U = ustawienia = DN.ustawienia()
    S = DN.skale(U)
    sprzataj = robocze is None
    robocze = robocze or tempfile.mkdtemp(prefix="npc_razem_")
    zakres = WYS[1] - WYS[0]
    zad_wspolne = {"widoki": [[WIDOK[0], list(WIDOK[1])]], "wys": list(WYS), "rozmiar": int(round(zakres * PX * 1.5)),
                   "obrys": True}
    czlowiek = rycerz.cialo()
    czlowiek.id = "razem_czlowiek"
    modele, zadania = [czlowiek], {czlowiek.id: dict(zad_wspolne)}
    kolumny = [(czlowiek.id, "Człowiek gracza", "goły Rycerz", 1.0, 5.3, 4.6)]
    for w in ustawienia["npc"]:
        p = DN.postac_modulu(w)
        kl = DN.klipy_npc(U, w)
        poza = poza_spoczynku(p, kl["spoczynek"])
        r = DN.rig_npc(U, w)
        m = rasy.w_skali(p, S[w["id"]], id="razem_" + w["id"])
        modele.append(m)
        zadania[m.id] = dict(zad_wspolne, poza=poza)
        szer = max(5.2, min(zakres, r["szerokosc"] * S[w["id"]] + 1.6))
        kolumny.append((m.id, w["imie"], w["rola"], S[w["id"]], r["wysokosc"] * S[w["id"]], szer))
    RP.renderuj_widoki(modele, zadania, robocze)
    fb, fn = RP._czcionki()
    wys = round(zakres * PX)
    N1, N2 = 64, 78
    wiersze = [kolumny[i:i + W_WIERSZU] for i in range(0, len(kolumny), W_WIERSZU)]
    szer_obrazu = max(sum(round(k[5] * PX) for k in w) for w in wiersze)
    im = Image.new("RGB", (szer_obrazu, N1 + (wys + N2) * len(wiersze)), TLO)
    dr = ImageDraw.Draw(im)
    dr.text((18, 12), "Postacie niezależne (NPC) w skali gry obok człowieka gracza — propozycja, D-109 "
                      "(imiona, wygląd i gesty do oceny)", font=fb, fill=TEKST)
    for wi, w in enumerate(wiersze):
        x = (szer_obrazu - sum(round(k[5] * PX) for k in w)) // 2
        y = N1 + wi * (wys + N2)
        for mid, imie, rola, skala, wzrost, szer in w:
            K = round(szer * PX)
            im.paste(RP._wytnij(os.path.join(robocze, "%s_%s.png" % (mid, WIDOK[0])), szer, PX, wys), (x, y))
            t = "%s — %s" % (imie, rola)
            dr.text((x + (K - dr.textlength(t, font=fn)) // 2, y + wys + 8), t, font=fn, fill=TEKST)
            t = "× %s, do czubka %s st" % (("%.2f" % skala).replace(".", ","), ("%.1f" % wzrost).replace(".", ","))
            dr.text((x + (K - dr.textlength(t, font=fn)) // 2, y + wys + 40), t, font=fn, fill=TEKST2)
            x += K
    os.makedirs(cel_folder, exist_ok=True)
    cel = os.path.join(cel_folder, "npc_razem.jpg")
    im.save(cel, quality=88)
    if sprzataj:
        shutil.rmtree(robocze, ignore_errors=True)
    return cel


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Plansza zbiorcza NPC w skali gry")
    ap.add_argument("--wyj", default=os.path.join(TU, "podglady"))
    ap.add_argument("--robocze", default="", help="folder roboczy (zostaje po przebiegu); domyślnie tymczasowy")
    a = ap.parse_args()
    cel = plansza(a.wyj, a.robocze or None)
    print("NPC | plansza gotowa: %s" % os.path.relpath(cel, REPO).replace("\\", "/"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
