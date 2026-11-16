# -*- coding: utf-8 -*-
"""Zrzut makiety w trybie Edit z tego samego kadru, który klient ustawia przy wyborze (tylko odczyt).

    python -B swiat/teleport_chmury/testy/zrzut_edit.py [nazwa] [--blisko <id krainy>]

Kadr liczony jak w KlientTeleportu (pozaWidoku) dla bieżącego rozmiaru okna Studio. Wynik: klatki/<nazwa>.jpg.
"""
import io
import json
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
KAT = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(KAT))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"),
           os.path.join(REPO, "swiat", "test_walki2", "testy")):
    sys.path.insert(0, _s)
from studio_mcp import StudioMCP  # noqa: E402
from cel_studio import wybierz_studio  # noqa: E402
from czuwanie import nie_usypiaj  # noqa: E402

ODCZYT = r'''
local m = workspace.TeleportChmury.Makieta
local P = m:GetAttribute("Pivot")
local vp = workspace.CurrentCamera.ViewportSize
local c = { P:GetComponents() }
return game:GetService("HttpService"):JSONEncode({ p = c, vp = { vp.X, vp.Y } })
'''


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    nazwa = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "edit_makieta"
    blisko = sys.argv[sys.argv.index("--blisko") + 1] if "--blisko" in sys.argv else None
    with open(os.path.join(KAT, "krainy.json"), encoding="utf-8") as f:
        dane = json.load(f)
    sys.path.insert(0, KAT)
    import makieta
    xs = makieta.srodki(dane)
    pol = makieta.polowa_dlugosci(dane)
    K = dane["kamera"]
    from PIL import Image
    with StudioMCP(timeout=180) as s:
        s.studios(wait=15)
        sid = wybierz_studio(s)
        r = s.call("execute_luau", {"code": ODCZYT, "datamodel_type": "Edit", "studio_id": sid})
        d = json.loads(r["text"])
        c = d["p"]
        pos, R = c[:3], [c[3:6], c[6:9], c[9:12]]

        def swiat(v):
            return [pos[i] + sum(R[i][k] * v[k] for k in range(3)) for i in range(3)]
        aspekt = d["vp"][0] / d["vp"][1]
        # screen_capture w Edit używa kąta kamery edytora (70°): odległość dobrana tak, by kadr był jak przy 40° w grze
        tanH = math.tan(math.radians(35)) * aspekt
        dd = pol * (1 + K["margines"]) / tanH
        nach = math.radians(K["nachylenie_stopnie"])
        cel = list(K["cel"])
        kam = [cel[0], cel[1] + math.sin(nach) * dd, cel[2] + math.cos(nach) * dd]
        if blisko:
            i = [k["id"] for k in dane["krainy"]].index(blisko)
            cel = [xs[i], 2, 2]
            kam = [xs[i], 2 + math.sin(nach) * 70, 2 + math.cos(nach) * 70]
        nie_usypiaj()
        r = s.call("screen_capture", {"studio_id": sid, "capture_id": "tc_" + nazwa,
                                      "camera_position": swiat(kam), "look_at_position": swiat(cel)}, timeout=150)
        if r["is_error"] or not r["images"]:
            sys.exit("zrzut: BŁĄD " + (r["text"] or "")[:300])
        im = Image.open(io.BytesIO(r["images"][0])).convert("RGB")
        os.makedirs(os.path.join(KAT, "klatki"), exist_ok=True)
        wyj = os.path.join(KAT, "klatki", nazwa + ".jpg")
        im.save(wyj, "JPEG", quality=86)
        print("zrzut %s (%dx%d, okno %s) -> %s" % (nazwa, im.width, im.height, d["vp"], wyj))


main()
