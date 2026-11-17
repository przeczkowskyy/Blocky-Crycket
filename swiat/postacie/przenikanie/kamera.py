# -*- coding: utf-8 -*-
"""„Broń zasłania twarz” z kamery walki i podgląd PNG — promienie rzucane na bryły (bez Studio).

Kamera finału (OdtwarzaczWalki2.luau, Sesja:ujecieSurowe, typ „objazd”, i Sesja:przygotujObjazd): zwycięzca stoi w W,
kamera w W + (znak·R·cos kat, hZ·0,55 + 1,6, R·sin kat), R = 1,25·hZ + 6,5; zwycięzca w radości obraca się do kamery
tak, że kąt twarzy (0° = przodem do kamery) jest 35° na początku objazdu i maleje do ok. 1° (wjazd i dryf). Gracz stoi
po lewej (kier = +1), więc kamera jest po PRAWEJ stronie jego twarzy; przeciwnik-lustro — po lewej. Dlatego kąty
−35…35° (obie strony). Ujęcia na postawę (spoczynek) z przodu w walce: „naSiebie” ok. 63°, „efekt” ok. 66°,
„zblizenie” ok. 70° od twarzy (wzory w tym samym miejscu) — postawę sprawdzamy w całym zakresie −70…70°.

Miara: promienie z kamery przez siatkę 64 × 64 na tarczy głowy. Piksel GŁOWY = promień trafia bryłę głowy (pierwsza
trafiona bryła głowy wyznacza, czy to oko). Piksel ZASŁONIĘTY BRONIĄ = promień trafia broń bliżej niż głowę
(zasłonięcie przez rękę czy rękaw się nie liczy). Wynik: ułamek zasłoniętych pikseli głowy i oczu.
"""
import math
import os
import sys

import numpy as np

TU = os.path.dirname(os.path.abspath(__file__))
if TU not in sys.path:
    sys.path.insert(0, TU)
import bryly as B  # noqa: E402

# zasłonięcie dopuszczalne (ułamek widocznych pikseli): broń może przeciąć brzeg głowy (hełm, kaptur, policzek), ale
# nie oczy i nie środek twarzy. Oczy liczone razem (jedno oko całe pod bronią = 50% = błąd).
PROG_OCZY = 0.25
PROG_RYSY = 0.35            # rysy twarzy: oczy, brwi, nos, usta, rumieńce, wąsy
SLOWA_OCZU = ("Oko", "Oczy")
SLOWA_RYSOW = ("Oko", "Oczy", "Blysk", "Brew", "Nos", "Usta", "Zeby", "Jezyk", "Kacik", "Mordka", "Was",
               "Rumieniec", "Pieg", "Podbrodek")


def kamera_objazdu(wysokosc, kat_deg, znak=1):
    """Położenie kamery objazdu w układzie aktora (przód −Z, prawo +X), kąt twarzy kat_deg (+ = z prawej)."""
    R = 1.25 * wysokosc + 6.5
    h = wysokosc * 0.55 + 1.6
    a = math.radians(kat_deg) * znak
    return np.array([R * math.sin(a), h, -R * math.cos(a)])


def _gladko(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def _wyjscie(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) * (1 - x)


def obrot_zwyciezcy():
    """(przed, czas) obrotu zwycięzcy do kamery z OdtwarzaczWalki2.luau (OBROT_ZWYCIEZCY); bez stałej — (0, 0,45),
    czyli obrót razem z radością, jak do 17.11.2026."""
    import re
    from pomiar import _tekst_zrodla
    t = _tekst_zrodla("OdtwarzaczWalki2.luau") or ""
    m = re.search(r"OBROT_ZWYCIEZCY\s*=\s*\{\s*przed\s*=\s*([\d.]+)\s*,\s*czas\s*=\s*([\d.]+)", t)
    return (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.45)


def przebieg_finalu(kat_start=62.0, do=1.2, krok=1.0 / 60, obrot_przed=None):
    """Kąt twarzy zwycięzcy w czasie od początku radości (τ, kąt): kamera objazdu kat = max(62 − 22·wyjscie(τ/2,6),
    kat_min), zwycięzca obraca się o (kat_start − 35)·gladko((τ + przed)/czas) — Sesja:aktualizujPozy,
    Sesja:ujecieSurowe; przed i czas z kodu gry (OBROT_ZWYCIEZCY), chyba że podano obrot_przed = (przed, czas).
    kat_start = max(62, kąt minimalny od leżącego pokonanego); drugi człon objazdu (dryf) zaczyna się po 2,6 s."""
    przed, czas = obrot_przed if obrot_przed is not None else obrot_zwyciezcy()
    obrot = min(max(kat_start - 35.0, 0.0), 150.0)
    wyn = []
    t = 0.0
    while t <= do + 1e-9:
        kat = max(62.0 - 22.0 * _wyjscie(t / 2.6), kat_start if kat_start > 62 else -1e9)
        wyn.append((t, kat - obrot * _gladko((t + przed) / czas)))
        t += krok
    return wyn


def _baza_kamery(C, cel, gora=(0, 1, 0)):
    f = cel - C
    f = f / np.linalg.norm(f)
    r = np.cross(f, np.array(gora, dtype=float))
    if np.linalg.norm(r) < 1e-9:
        r = np.array([1.0, 0, 0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return f, r, u


def rzucaj(pm, Wb, O, D, bryly=None):
    """Najbliższe trafienie promieni (O, D: (N, 3) świat) we wskazane bryły. Zwraca (t (N, nb'), normalne świat)."""
    bryly = range(pm.a.nb) if bryly is None else bryly
    T, N = [], []
    for b in bryly:
        R, t = Wb[b, :3, :3], Wb[b, :3, 3]
        tt, nn = B.przeciecie_promieni(pm.rodzaj[b], pm.pol[b], (O - t) @ R, D @ R)
        T.append(tt)
        N.append(nn @ R.T)
    return np.stack(T, axis=1), np.stack(N, axis=1)


class Twarz:
    """Zasłonięcie twarzy bronią dla aktora z pomiaru (Pomiar)."""

    def __init__(self, pm, rozdz=64):
        self.pm = pm
        g = next((s for s in pm.strefy if s.nazwa == "glowa"), None)
        self.glowa = list(g.bryly) if g is not None else []
        self.oczy = [b for b in self.glowa if pm.d["czesci"][b][2].startswith(SLOWA_OCZU)]
        self.rysy = [b for b in self.glowa if pm.d["czesci"][b][2].startswith(SLOWA_RYSOW)]
        self.bron = list(pm.bron)
        self.rozdz = rozdz

    def zmierz(self, Wb, C):
        """Kamera w C (układ aktora) -> {glowa, oczy, rysy: ułamki zasłonięte bronią; piksele_*: ile widać}."""
        if not self.glowa:
            return None
        srodki = Wb[self.glowa, :3, 3]
        H = srodki.mean(axis=0)
        r = np.max(np.linalg.norm(srodki - H, axis=1) + self.pm.promien[self.glowa])
        f, rr, u = _baza_kamery(C, H)
        dist = np.linalg.norm(H - C)
        pol = math.atan2(r * 1.05, dist)
        s = np.linspace(-math.tan(pol), math.tan(pol), self.rozdz)
        X, Y = np.meshgrid(s, -s)
        D = f[None, :] + X.reshape(-1, 1) * rr[None, :] + Y.reshape(-1, 1) * u[None, :]
        D /= np.linalg.norm(D, axis=1, keepdims=True)
        O = np.broadcast_to(C, D.shape)
        Tg, _ = rzucaj(self.pm, Wb, O, D, self.glowa)
        Tb, _ = rzucaj(self.pm, Wb, O, D, self.bron) if self.bron else (np.full((len(D), 1), np.inf), None)
        tg = Tg.min(axis=1)
        ig = np.array(self.glowa)[Tg.argmin(axis=1)]
        tb = Tb.min(axis=1)
        glowa = np.isfinite(tg)
        oko = glowa & np.isin(ig, self.oczy)
        rysy = glowa & np.isin(ig, self.rysy)
        zasl = glowa & (tb < tg)
        ng, no, nr = int(glowa.sum()), int(oko.sum()), int(rysy.sum())

        def ul(maska, n):
            return float((zasl & maska).sum()) / n if n else 0.0
        return {"glowa": ul(glowa, ng), "oczy": ul(oko, no), "rysy": ul(rysy, nr),
                "piksele_glowy": ng, "piksele_oczu": no, "piksele_rysow": nr}

    def ocena(self, r):
        """Wynik zmierz -> stopień przekroczenia progu (> 1 = twarz zasłonięta). Oczy liczą się, gdy widać ich
        co najmniej 12 pikseli (z boku oko to kilka pikseli na brzegu — ułamek byłby przypadkowy)."""
        s = r["rysy"] / PROG_RYSY if r["piksele_rysow"] >= 12 else 0.0
        if r["piksele_oczu"] >= 12:
            s = max(s, r["oczy"] / PROG_OCZY)
        return s


# --------------------------------------------------------------------------- podgląd PNG
def _kolor(hexs):
    hexs = str(hexs).lstrip("#")
    try:
        return np.array([int(hexs[i:i + 2], 16) for i in (0, 2, 4)], dtype=float) / 255.0
    except ValueError:
        return np.array([0.7, 0.7, 0.7])


def obraz(pm, Wb, kier, gora=(0, 1, 0), rozmiar=320, kadr=None, punkty=(), podswietl=(), tlo=(245, 245, 245),
          kamera=None):
    """Rzut prostokątny całego aktora (promienie równoległe, kierunek patrzenia `kier` w układzie aktora) -> obraz
    PIL. kadr = (środek, połowa szerokości) w świecie; punkty = [(xyz, kolor)] — kółka (np. najgłębszy punkt);
    podswietl = bryły rysowane jaśniej (broń). kamera = położenie kamery (perspektywa: promienie z kamery przez
    płaszczyznę kadru w środku kadru) zamiast rzutu prostokątnego."""
    from PIL import Image, ImageDraw
    srodki = Wb[:, :3, 3]
    if kamera is not None:
        cel = np.asarray(kadr[0], dtype=float) if kadr is not None else srodki.mean(axis=0)
        kier = cel - np.asarray(kamera, dtype=float)
    kier = np.asarray(kier, dtype=float)
    kier /= np.linalg.norm(kier)
    f = kier
    r = np.cross(f, np.array(gora, dtype=float))
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    if kadr is None:
        c = srodki.mean(axis=0)
        pol = float(np.max(np.abs((srodki - c) @ np.stack([r, u], axis=1))) + pm.promien.max()) * 1.05
    else:
        c, pol = np.asarray(kadr[0], dtype=float), float(kadr[1])
    s = np.linspace(-pol, pol, rozmiar)
    X, Y = np.meshgrid(s, -s)
    P = c[None, :] + X.reshape(-1, 1) * r[None, :] + Y.reshape(-1, 1) * u[None, :]
    if kamera is not None:
        O = np.broadcast_to(np.asarray(kamera, dtype=float), P.shape).copy()
        D = P - O
        D /= np.linalg.norm(D, axis=1, keepdims=True)
    else:
        O = P - f[None, :] * 50.0
        D = np.broadcast_to(f, O.shape).copy()
    T, Nw = rzucaj(pm, Wb, O, D)
    t = T.min(axis=1)
    i = T.argmin(axis=1)
    traf = np.isfinite(t)
    n = Nw[np.arange(len(t)), i]
    swiatlo = np.array([0.35, 0.8, -0.45])
    swiatlo /= np.linalg.norm(swiatlo)
    jasn = 0.45 + 0.55 * np.clip(np.abs(n @ swiatlo), 0, 1)
    kolory = np.array([_kolor(c_[12]) for c_ in pm.d["czesci"]])
    pod = np.zeros(pm.a.nb, dtype=bool)
    pod[list(podswietl)] = True
    k = kolory[i] * jasn[:, None]
    k = np.where(pod[i][:, None], 0.35 + 0.65 * k, k)
    img = np.where(traf[:, None], k * 255, np.array(tlo, dtype=float)[None, :])
    img = img.reshape(rozmiar, rozmiar, 3).astype(np.uint8)
    im = Image.fromarray(img, "RGB")
    dr = ImageDraw.Draw(im)
    for p, kol in punkty:
        q = np.asarray(p, dtype=float)
        if kamera is not None:                      # rzut środkowy na płaszczyznę kadru (przez środek kadru)
            C = np.asarray(kamera, dtype=float)
            v = q - C
            q = C + v * ((c - C) @ f) / max(v @ f, 1e-9)
        q = q - c
        x = (q @ r + pol) / (2 * pol) * (rozmiar - 1)
        y = (pol - q @ u) / (2 * pol) * (rozmiar - 1)
        dr.ellipse([x - 6, y - 6, x + 6, y + 6], outline=kol, width=3)
    return im
