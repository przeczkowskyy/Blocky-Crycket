# -*- coding: utf-8 -*-
"""Wspólny kształt jajek biomów (Bagno, Dżungla) — czyste Pythonowe funkcje bez zależności, używane przez
tekstury.py (malowanie pęknięć w miejscu podziału skorupy) i blender_jajko.py (siatki Egg i Shell*).

Układ jak w leśnym jaju Pawła (tools/studio/jajo_lesne_ustaw.luau, src/client/JajkoKoroweClient.client.luau):
metry pliku = study przed skalą ×1,5; Y w górę; przód modelu = +Z pliku (Blender −Y); najniższy punkt całego
modelu leży na Y = 0 (tam skrypt ustawiający stawia niewidzialny korzeń). Klient Pawła stawia świecący rdzeń
1,59 m nad korzeniem i słup światła od 1,66 m — jajo jest tak ustawione, żeby rdzeń siedział w dolnej skorupie.

Parametry powierzchni jaja: θ (od czubka 0 do dna π), α (azymut od tyłu −Z, przez +X, przód +Z, −X).
Tekstura: U = α / 2π, V = θ / π · V_MAX (pas pod V_MAX: wnętrze skorupy i krawędź pęknięcia).
"""
import math
import random

# wymiary dobrane do leśnego jaja: klient Pawła kadruje scenkę na model wysoki 3,03 m pliku („jajo ze skałami”),
# rdzeń 1,59 nad korzeniem — czubek jaja wypada na 3,0 m, rdzeń w dolnej skorupie pod najniższym zębem obrzeża
SZER = 1.85          # średnica jaja (bez „brzuszka”)
WYS = 2.62           # wysokość jaja
DOL = 0.38           # dno jaja nad najniższym punktem modelu
ZWEZENIE = 0.16      # czubek węższy od dołu
GRUBOSC = 0.05       # grubość kawałków skorupy

KOLUMNY = 54         # podział po obwodzie (wierzchołki zębów obrzeża co 3 kolumny)
ZEBY_CO = 3
RZEDY_DOL = 14
RZEDY_GORA = 10

V_MAX = 0.93
PAS_WNETRZE = (0.938, 0.962)   # V: wnętrze skorupy
PAS_KRAWEDZ = (0.970, 0.996)   # V: krawędź pęknięcia (świeci)

RDZEN_Y = 1.59       # stała z klienta Pawła (rdzeń nad korzeniem, przed skalą)


def srodek():
    return (0.0, DOL + WYS / 2.0, 0.0)


def punkt(theta, alfa):
    """Punkt na powierzchni jaja (x, y, z), Y w górę, przód +Z."""
    s, c = math.sin(theta), math.cos(theta)
    f = 1.0 - ZWEZENIE * c
    phi = alfa - math.pi / 2.0
    return (SZER / 2.0 * f * s * math.cos(phi), DOL + WYS / 2.0 + WYS / 2.0 * c, SZER / 2.0 * f * s * math.sin(phi))


class Podzial:
    """Linie pęknięcia: zębate obrzeże dolnej skorupy i zębata linia z przodu między górnymi kawałkami
    (z tyłu prosto po szwie tekstury α = 0, żeby UV kawałków nie przechodziło przez szew)."""

    def __init__(self, ziarno, theta0=math.radians(70.0), amp=math.radians(8.0), przod=0.88 * math.pi):
        r = random.Random(ziarno)
        n = KOLUMNY // ZEBY_CO
        self.zeby = [theta0 + (amp if i % 2 else -amp) * r.uniform(0.55, 1.0) for i in range(n)]
        # linia przednia: α(t) dla t = 0..1 (od obrzeża do czubka), zęby co 1/8
        kz = [przod]
        for i in range(1, 8):
            kz.append(przod + (0.21 if i % 2 else -0.21) * r.uniform(0.5, 1.0))
        kz.append(przod)
        self.przod_zeby = kz
        # α(0) musi trafić w kolumnę obrzeża
        self.kol_przod = int(round(przod / (2 * math.pi) * KOLUMNY))
        self.przod_zeby[0] = 2 * math.pi * self.kol_przod / KOLUMNY

    def obrzeze(self, alfa):
        """θ obrzeża dolnej skorupy dla azymutu α (okresowe)."""
        n = len(self.zeby)
        x = (alfa / (2 * math.pi)) * n
        x = x % n
        i = int(math.floor(x))
        u = x - i
        return self.zeby[i] * (1 - u) + self.zeby[(i + 1) % n] * u

    def linia_przod(self, t):
        k = self.przod_zeby
        x = max(0.0, min(1.0, t)) * (len(k) - 1)
        i = min(int(x), len(k) - 2)
        u = x - i
        return k[i] * (1 - u) + k[i + 1] * u

    # --- siatki parametryczne kawałków: listy rzędów [(theta, alfa, U), ...]
    def rzedy_dol(self):
        rz = []
        for k in range(RZEDY_DOL + 1):
            t = k / RZEDY_DOL
            rzad = []
            for i in range(KOLUMNY + 1):
                a = 2 * math.pi * i / KOLUMNY
                th = self.obrzeze(a)
                rzad.append((th + (math.pi - th) * t, a, i / KOLUMNY))
            rz.append(rzad)
        return rz  # rząd 0 = obrzeże, ostatni = dno (biegun)

    def rzedy_gora(self, prawa):
        """prawa=True: kawałek ShellTopRight (+X, α 0..linia), inaczej ShellTopLeft (linia..2π)."""
        rz = []
        kols = self.kol_przod if prawa else KOLUMNY - self.kol_przod
        for k in range(RZEDY_GORA + 1):
            t = k / RZEDY_GORA
            lp = self.linia_przod(t)
            a0, a1 = (0.0, lp) if prawa else (lp, 2 * math.pi)
            rzad = []
            for j in range(kols + 1):
                a = a0 + (a1 - a0) * j / kols
                th = self.obrzeze(a) * (1 - t)
                rzad.append((th, a, a / (2 * math.pi)))
            rz.append(rzad)
        return rz  # rząd 0 = obrzeże, ostatni = czubek (biegun)

    def linie_uv(self, kroki=400):
        """Linie pęknięcia w UV (do malowania tekstury): obrzeże, linia przednia, szew z tyłu."""
        obr = [(i / kroki, self.obrzeze(2 * math.pi * i / kroki) / math.pi * V_MAX) for i in range(kroki + 1)]
        prz = []
        for i in range(kroki + 1):
            t = i / kroki
            a = self.linia_przod(t)
            prz.append((a / (2 * math.pi), self.obrzeze(a) * (1 - t) / math.pi * V_MAX))
        tyl = [(0.0, self.obrzeze(0.0) * (1 - i / kroki) / math.pi * V_MAX) for i in range(kroki + 1)]
        return [obr, prz, tyl]
