#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zrzuty ekranu z Roblox Studio z listy ujęć — te same kadry co rendery z Blendera, ale w prawdziwym oświetleniu gry.

    python tools/studio_zrzuty.py swiat/krzywe_miasteczko/ujecia.json --wyj <folder> [--przesun 0,0,-700] [--tylko a,b]

Plik ujęć: [[nazwa, [x,y,z] kamery, [x,y,z] celu, ogniskowa, skala rzutu prostokątnego albo null], …] w układzie mapy
(ten sam format co `--ujecia` w tools/blender/klocki.py). `--przesun` dodaje przesunięcie mapy w świecie Studio.
Ujęcia w rzucie prostokątnym (mapa z góry) są robione jako zwykła perspektywa z wysoka.

Tylko odczyt: skrypt niczego w miejscu nie zmienia (kamera edytora wraca na miejsce po każdym zrzucie — robi to Studio).
Okno Studio musi być widoczne (zminimalizowane daje czarny obraz). Wynik: pliki JPG (PNG, gdy brak Pillow).
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from studio_mcp import StudioMCP, StudioError, first_studio_id  # noqa: E402


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Zrzuty ze Studio według listy ujęć")
    ap.add_argument("ujecia")
    ap.add_argument("--wyj", required=True)
    ap.add_argument("--przesun", default="0,0,0", help="przesunięcie mapy w świecie Studio: x,y,z")
    ap.add_argument("--tylko", default="")
    ap.add_argument("--jakosc", type=int, default=88)
    ap.add_argument("--czekaj", type=float, default=0,
                    help="opcjonalnie: przed każdym zrzutem czekaj do N minut, aż Studio wróci z trybu Play do Edit")
    ap.add_argument("--rozmiar", default="",
                    help="opcjonalnie: zmniejsz zrzut do szerokości w pikselach (np. 1600), żeby JPG był mniejszy")
    a = ap.parse_args()
    dx, dy, dz = (float(v) for v in a.przesun.split(","))
    with open(a.ujecia, encoding="utf-8") as f:
        ujecia = json.load(f)
    tylko = [t for t in a.tylko.split(",") if t]
    os.makedirs(a.wyj, exist_ok=True)
    try:
        from PIL import Image
    except ImportError:
        Image = None
    zrobione = 0
    try:
        with StudioMCP() as s:
            sid = first_studio_id(s)
            if not sid:
                sys.exit("Roblox Studio nie jest podłączone.")
            for u in ujecia:
                nazwa, pos, cel = u[0], u[1], u[2]
                orto = u[4] if len(u) > 4 else None
                if tylko and not any(t in nazwa for t in tylko):
                    continue
                if orto:                                       # rzut z góry: perspektywa z wysokości dobranej do skali kadru
                    pos = [cel[0], cel[1] + float(orto) * 1.25, cel[2] + 0.5]
                if a.czekaj > 0:                               # ktoś inny testuje w Play: zrzut w Edit dopiero po powrocie
                    import time
                    koniec = time.time() + 60 * a.czekaj
                    while time.time() < koniec:
                        tryby = [x.get("mode") for x in s.studios() if isinstance(x, dict) and x.get("mode")]
                        if not tryby or all(t == "Edit" for t in tryby):
                            break
                        time.sleep(20)
                r = s.call("screen_capture", {"studio_id": sid, "capture_id": "ujecie_" + nazwa,
                                              "camera_position": [pos[0] + dx, pos[1] + dy, pos[2] + dz],
                                              "look_at_position": [cel[0] + dx, cel[1] + dy, cel[2] + dz]}, timeout=120)
                if r["is_error"] or not r["images"]:
                    print("  %s: BŁĄD %s" % (nazwa, (r["text"] or "brak obrazu")[:200]))
                    continue
                png = os.path.join(a.wyj, nazwa + ".png")
                with open(png, "wb") as f:
                    f.write(r["images"][0])
                wynik = png
                if Image is not None:
                    jpg = os.path.join(a.wyj, nazwa + ".jpg")
                    im = Image.open(png).convert("RGB")
                    if a.rozmiar and im.width > int(a.rozmiar):
                        im = im.resize((int(a.rozmiar), round(im.height * int(a.rozmiar) / im.width)), Image.LANCZOS)
                    im.save(jpg, "JPEG", quality=a.jakosc)
                    os.remove(png)
                    wynik = jpg
                zrobione += 1
                print("  %s -> %s" % (nazwa, wynik), flush=True)
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)
    print("zrzutów: %d -> %s" % (zrobione, os.path.abspath(a.wyj)))


if __name__ == "__main__":
    main()
