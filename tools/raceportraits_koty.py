#!/usr/bin/env python3
"""Ramki portretu z kotami ras (Paweł 24.11, D-145): te same złote ramki z torem paska doświadczenia, nowy portret.

Paweł: „nie zmieniać w ogóle ułożenia tych pasków, bo one są teraz idealnie dopasowane”. Dlatego ramki NIE są
generowane od nowa: z obecnych assets/processed/RacePortraits/RaceFrame<Id>.png zostaje złota ramka, tabliczka
z torem paska i obrysy co do piksela, a wnętrze okna (to, co ramka odsłania nad tabliczką) dostaje portret kota.
Tor paska (Tor w src/shared/RacePortraits.luau, z Figmy) zostaje bez zmian.

1. Arkusz assets/raw/RacePortraits/portrety_koty_v3.png — 7 kwadratowych kafelków 4 + 3 z czarną ramką i tłem
   (Higgsfield, Nano Banana 2.1, job 928f26c9, elfy z poprawki uszu 8ba946d5; koty jak na ikonach ras, Paweł 24.11: „te aktualne portrety są za
   bardzo realistyczne”). Cięcie jak w tools/raceportraits_assets.py -> Portrait<Id>_v2.png (512 px).
2. Wnętrze okna ramki: piksele dalej niż GRUBOSC od przezroczystego brzegu ramki, bez tabliczki paska (prostokąt
   wykryty od toru paska na zewnątrz do końca zewnętrznego obrysu). Portret wypełnia wnętrze (przycięty od dołu
   do kwadratu okna), łączenie z miękką krawędzią 1,5 px -> RaceFrame<Id>_v2.png (512 × 556).
3. Podgląd wszystkich ramek: assets/processed/RacePortraits/ramki_koty_podglad.jpg.

Użycie: python tools/raceportraits_koty.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
import raceportraits_assets as RP  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "assets/raw/RacePortraits/portrety_koty_v3.png"
# poprawka uszu elfów (job 8ba946d5) — z niej tylko elfy, bo przy okazji zgubiła rogi demona
RAW_ELFY = ROOT / "assets/raw/RacePortraits/portrety_koty_v3_elfy.png"
Z_ELFOW = ("DarkElf", "Elf")
OUT = ROOT / "assets/processed/RacePortraits"
GRUBOSC = 35.5  # złota ramka okna z obu obrysami (zmierzone na RaceFrameHuman: obrys wewnętrzny kończy się na 34 px)


def portrety():
    a = np.array(Image.open(RAW).convert("RGB"))
    e = np.array(Image.open(RAW_ELFY).convert("RGB"))
    kaf_e = dict(zip(RP.KOLEJNOSC, RP.kafelki(e)))
    wynik = {}
    for nazwa, s in zip(RP.KOLEJNOSC, RP.kafelki(a)):
        k = e[kaf_e[nazwa]] if nazwa in Z_ELFOW else a[s]
        g = RP.grubosc_ramki(k)
        h, w = k.shape[:2]
        z = g + round(RP.ZAPAS * min(h, w))
        wn = Image.fromarray(k[z:h - z, z:w - z])
        bok = min(wn.size)
        wn = wn.crop(((wn.width - bok) // 2, wn.height - bok, (wn.width + bok) // 2, wn.height))
        wn = wn.resize((RP.ROZMIAR, RP.ROZMIAR), Image.LANCZOS)
        wn.save(OUT / f"Portrait{nazwa}_v2.png", optimize=True)
        wynik[nazwa] = wn
        print("portret", nazwa, f"kafelek {w}×{h}, ramka {g} px")
    return wynik


def tabliczka(a, tor):
    """Prostokąt tabliczki paska: od toru na zewnątrz przez obrys, złoto i zewnętrzny obrys (w każdą stronę)."""
    jas = a[..., :3].astype(int).sum(axis=2)
    x, y, w, h = tor
    cx, cy = x + w // 2, y + h // 2

    def idz(px, py, dx, dy):
        # tor (granat) -> ciemny obrys -> złoto (jasne) -> ciemny obrys -> poza tabliczką
        etap = 0
        while 0 <= px < a.shape[1] and 0 <= py < a.shape[0] and a[py, px, 3] > 0:
            v = jas[py, px]
            if etap == 0 and v > 450:
                etap = 1
            elif etap == 1 and v < 180:
                etap = 2
            elif etap == 2 and v >= 180:
                return px, py
            px += dx
            py += dy
        return px - dx, py - dy

    lewo = idz(x + 6, cy, -1, 0)[0]
    prawo = idz(x + w - 6, cy, 1, 0)[0]
    gora = min(idz(cx + o, y + 6, 0, -1)[1] for o in (-w // 4, 0, w // 4))
    return lewo, gora, prawo, a.shape[0]


def ramka(nazwa, portret):
    stara = np.array(Image.open(OUT / f"RaceFrame{nazwa}.png").convert("RGBA"))
    H, W = stara.shape[:2]
    # obramowanie zerami: ramka dotyka krawędzi obrazka, a odległość ma się liczyć też od niej
    odl = ndimage.distance_transform_edt(np.pad(stara[..., 3] > 0, 1))[1:-1, 1:-1]
    wnetrze = odl >= GRUBOSC
    l, g, p, d = tabliczka(stara, RP.TOR_FIGMA[nazwa])
    wnetrze[g:d, max(l - 1, 0):p + 2] = False
    wnetrze = ndimage.binary_opening(wnetrze, iterations=2)
    ys, xs = np.nonzero(wnetrze)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    # portret: szerokość okna, przyklejony do góry okna (głowa kota w oknie, ramiona schodzą pod tabliczkę)
    bok = x1 - x0
    por = np.array(portret.convert("RGB").resize((bok, bok), Image.LANCZOS))
    tlo = np.zeros((H, W, 3), np.uint8)
    wys = min(bok, H - y0)
    tlo[y0:y0 + wys, x0:x1] = por[:wys]
    if y0 + wys < H:  # okno dłuższe niż portret: dół dopełniony ostatnim wierszem portretu
        tlo[y0 + wys:, x0:x1] = por[wys - 1]
    m = np.array(Image.fromarray((wnetrze * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)),
                 dtype=float)[..., None] / 255
    nowa = stara.copy()
    nowa[..., :3] = (stara[..., :3] * (1 - m) + tlo * m).astype(np.uint8)
    out = Image.fromarray(nowa)
    out.save(OUT / f"RaceFrame{nazwa}_v2.png", optimize=True)
    print("ramka", nazwa, f"okno {x0}-{x1} × {y0}-{y1}, tabliczka {l}-{p} od y {g}")
    return out


def main():
    por = portrety()
    ramki = [ramka(n, por[n]) for n in RP.KOLEJNOSC]
    W, H = ramki[0].size
    pod = Image.new("RGB", (W * 4 + 50, H * 2 + 30), (120, 120, 130))
    for i, r in enumerate(ramki):
        pod.paste(r, (10 + (i % 4) * (W + 10), 10 + (i // 4) * (H + 10)), r)
    pod.save(OUT / "ramki_koty_podglad.jpg", quality=88)
    print("podgląd", OUT / "ramki_koty_podglad.jpg")


if __name__ == "__main__":
    main()
