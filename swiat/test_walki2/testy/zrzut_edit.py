#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zrzut ekranu Studio w trybie Edit z kamery w podanym miejscu (nic w miejscu nie zmienia).

    python -B swiat/test_walki2/testy/zrzut_edit.py --kamera 0,20,200 --cel 0,3,250 --wyj <plik.jpg>
"""
import argparse
import io
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TU)))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
    sys.path.insert(0, _s)
from studio_mcp import StudioMCP  # noqa: E402
from cel_studio import wybierz_studio  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kamera", required=True)
    ap.add_argument("--cel", required=True)
    ap.add_argument("--wyj", required=True)
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    from PIL import Image
    kam = [float(v) for v in a.kamera.split(",")]
    cel = [float(v) for v in a.cel.split(",")]
    with StudioMCP() as s:
        sid = wybierz_studio(s, a.studio)
        if "Current Studio Mode: Edit" not in s.call("get_studio_state", {"studio_id": sid})["text"]:
            sys.exit("Studio nie jest w trybie Edit")
        r = s.call("screen_capture", {"studio_id": sid, "capture_id": "testwalki2", "camera_position": kam,
                                      "look_at_position": cel}, timeout=120)
        if r["is_error"] or not r["images"]:
            sys.exit("zrzut: %s" % (r["text"] or "brak obrazu")[:300])
        Image.open(io.BytesIO(r["images"][0])).convert("RGB").save(a.wyj, quality=88)
        print(a.wyj)


if __name__ == "__main__":
    main()
