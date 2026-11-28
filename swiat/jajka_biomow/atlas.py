# -*- coding: utf-8 -*-
"""Atlas ozdób jajek (1024 × 1024): prostokąty pól w pikselach (x0, y0, x1, y1; y od góry) i kształty liści,
wspólne dla tekstury.py (malowanie) i blender_jajko.py (UV). Bez zależności."""
import math

ROZMIAR = 1024

POLA = {
    "bagno": {
        "bloto": (0, 0, 512, 512),
        "kamien": (512, 0, 768, 256),
        "kora": (768, 0, 1024, 256),
        "trzcina": (512, 256, 640, 512),
        "palka": (640, 256, 768, 512),
        "lodyga": (768, 256, 832, 512),
        "grzybien": (0, 512, 256, 768),
        "platek": (256, 512, 384, 640),
        "srodek": (384, 512, 512, 640),
        "woda": (512, 512, 768, 768),
        "bloto_bok": (768, 512, 1024, 768),
    },
    "dzungla": {
        "plyta": (0, 0, 512, 512),
        "fryz": (512, 0, 1024, 128),
        "fryz2": (512, 128, 1024, 256),
        "mech": (512, 256, 768, 512),
        "liana": (768, 256, 832, 512),
        "kora": (832, 256, 1024, 512),
        "lisc": (0, 512, 256, 1024),
        "platek": (256, 512, 384, 640),
        "precik": (384, 512, 512, 640),
        "listek": (256, 640, 384, 768),
        "kamien": (512, 512, 768, 768),
    },
}

MARGINES = 0.06   # margines kształtów liści w polu (ułamek)


def uv(biom, pole, x, y):
    """(x, y) w [0,1]² pola (y od DOŁU pola) -> UV Blendera (V w górę)."""
    x0, y0, x1, y1 = POLA[biom][pole]
    px = x0 + (x1 - x0) * (MARGINES + (1 - 2 * MARGINES) * x) if pole in KSZTALTY else x0 + (x1 - x0) * x
    py_od_dolu = (MARGINES + (1 - 2 * MARGINES) * y) if pole in KSZTALTY else y
    py = y1 - (y1 - y0) * py_od_dolu
    return (px / ROZMIAR, 1.0 - py / ROZMIAR)


def px(biom, pole, x, y):
    """To samo co uv(), ale w pikselach obrazu (y od góry) — do malowania."""
    u, v = uv(biom, pole, x, y)
    return (u * ROZMIAR, (1.0 - v) * ROZMIAR)


# kształty liści: szerokość (ułamek pola, 0..1) w funkcji wysokości y (0 = nasada, 1 = czubek)
def szer_lisc(y):          # wielki liść Dżungli: jajowaty, ostry czubek
    return 0.98 * math.sin(math.pi * min(1.0, y ** 0.85)) ** 0.75 * (1.0 - 0.25 * y) if 0 < y < 1 else 0.0


def szer_trzcina(y):       # liść trzciny: długi, zwężony
    return 0.9 * (1.0 - y) ** 0.8 * min(1.0, y * 6 + 0.35) if y < 1 else 0.0


def szer_platek(y):        # płatek: kropla
    return 0.95 * math.sin(math.pi * min(1.0, y ** 0.7)) ** 0.6 if 0 < y < 1 else 0.0


def szer_listek(y):
    return 0.95 * math.sin(math.pi * y) ** 0.8 if 0 < y < 1 else 0.0


KSZTALTY = {"lisc": szer_lisc, "trzcina": szer_trzcina, "platek": szer_platek, "listek": szer_listek}
RZEDY_KSZTALTU = {"lisc": 9, "trzcina": 4, "platek": 4, "listek": 4}


def kontur(pole, rzedy=None):
    """Wielokąt konturu (x, y) w [0,1]² dla kształtu, ten sam, który ma siatka (rzędy jak w siatce)."""
    f = KSZTALTY[pole]
    n = rzedy or RZEDY_KSZTALTU[pole]
    ys = [k / n for k in range(n + 1)]
    prawa = [(0.5 + f(y) / 2, y) for y in ys]
    lewa = [(0.5 - f(y) / 2, y) for y in reversed(ys)]
    return prawa + lewa


def grzybien_kontur(n=18, wciecie=0.42):
    """Liść grzybienia (lilii wodnej): koło z klinowym wcięciem; punkty (x, y) w [0,1]² pola."""
    pts = []
    for i in range(n + 1):
        a = wciecie / 2 + (2 * math.pi - wciecie) * i / n
        pts.append((0.5 + 0.47 * math.sin(a), 0.5 + 0.47 * math.cos(a)))
    return [(0.5, 0.5)] + pts
