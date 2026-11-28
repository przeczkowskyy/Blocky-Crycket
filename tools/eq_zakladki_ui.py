#!/usr/bin/env python3
"""Arkusz przebudowy okna ekwipunku (Paweł 26.11, jedna generacja: assets/raw/EqZakladki2/arkusz_v1.png) -> elementy:
4 długie zakładki (pomarańczowa, fioletowa, niebieska, zielona — rozciągane w Roblox przez 9-slice), strzałki stron
w lewo i w prawo, tabliczka numeru strony, pionowy drewniany pas z trzema slotami umiejętności.
Białe tło połączone z brzegiem -> przezroczyste (tools/hud_pety_ui.bez_tla). Wypisuje ułamki slotów w pasie
i środek 9-slice zakładek (do tools/eq_skille_build.py).

Użycie: python tools/eq_zakladki_ui.py
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

from hud_pety_ui import bez_tla

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/raw/EqZakladki2/arkusz_v1.png"
OUT = ROOT / "assets/processed/EqZakladki2"
ZAKLADKI = ["EqTab2Orange", "EqTab2Purple", "EqTab2Blue", "EqTab2Green"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    a = bez_tla(Image.open(SRC))
    lab, _ = ndimage.label(a[..., 3] > 0)
    el = []
    for i, s in enumerate(ndimage.find_objects(lab), 1):
        h, w = s[0].stop - s[0].start, s[1].stop - s[1].start
        if h * w > 150_000:
            wyc = a[s].copy()
            wyc[..., 3] = np.where(lab[s] == i, wyc[..., 3], 0)
            el.append({"x": s[1].start, "y": s[0].start, "w": w, "h": h, "im": Image.fromarray(wyc)})
    zakl = sorted([e for e in el if e["w"] > 6 * e["h"]], key=lambda e: e["y"])
    pas = [e for e in el if e["h"] > 2 * e["w"]]
    reszta = sorted([e for e in el if e not in zakl and e not in pas], key=lambda e: e["x"])
    assert len(zakl) == 4 and len(pas) == 1 and len(reszta) == 3, (len(zakl), len(pas), len(reszta))
    info = {}
    for e, n in zip(zakl, ZAKLADKI):
        im = e["im"]
        im = im.resize((1024, round(1024 * im.height / im.width)), Image.LANCZOS)
        im.save(OUT / f"{n}.png", optimize=True)
        info[n] = im.size
    for e, n in zip(reszta, ["EqStronaLewo", "EqStronaPrawo", "EqStronaTabliczka"]):
        im = e["im"]
        im.thumbnail((256, 256), Image.LANCZOS)
        im.save(OUT / f"{n}.png", optimize=True)
        info[n] = im.size
    im = pas[0]["im"]
    im.thumbnail((400, 1024), Image.LANCZOS)
    im.save(OUT / "EqPasSkilli.png", optimize=True)
    info["EqPasSkilli"] = im.size
    # sloty w pasie: ciemne wnętrza ramek
    b = np.array(im).astype(int)
    ciemne = (b[..., :3].max(axis=2) < 95) & (b[..., 3] > 200)
    lab2, n2 = ndimage.label(ciemne)
    sloty = []
    for j, sl in enumerate(ndimage.find_objects(lab2), 1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if hh * ww > 0.05 * im.width * im.width:
            sloty.append((sl[1].start / im.width, sl[0].start / im.height, ww / im.width, hh / im.height))
    sloty.sort(key=lambda r: r[1])
    info["sloty_pasa"] = [[round(v, 4) for v in r] for r in sloty]
    (OUT / "uklad.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
