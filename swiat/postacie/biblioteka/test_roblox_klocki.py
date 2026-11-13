# -*- coding: utf-8 -*-
"""Sprawdzian rozkładu brył na części Roblox (bez Blendera i bez Studio).

    python -B swiat/postacie/biblioteka/test_roblox_klocki.py

Dla losowych ostrosłupów porównuje punkt po punkcie „prawdziwą” bryłę (powłoka podstawy i góry, jak w blender_postac.py)
z sumą części, na które rozkłada ją roblox_klocki.rozloz() (klocek + kliny + kliny narożne w konwencji Roblox:
WedgePart — pionowa ściana po stronie +Z, CornerWedgePart — wierzchołek w rogu +X, +Y, −Z). Sprawdza też zamianę
układu: położenia, obroty brył i póz muszą dać ten sam wynik co obrót całego rigu o 180° wokół pionu.
"""
import math
import os
import random
import sys

sys.dont_write_bytecode = True
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.postacie.biblioteka.postac import macierz_obrotu, mnoz, razy_wektor  # noqa: E402
from swiat.postacie.biblioteka import roblox_klocki as rk  # noqa: E402


def w_ostroslupie(p, sx, sy, sz, tx, tz, dx, dz):
    v = p[1] / sy + 0.5
    if v < 0 or v > 1:
        return False
    xa, xb = -sx / 2 + (dx - tx / 2 + sx / 2) * v, sx / 2 + (dx + tx / 2 - sx / 2) * v
    za, zb = -sz / 2 + (dz - tz / 2 + sz / 2) * v, sz / 2 + (dz + tz / 2 - sz / 2) * v
    return xa <= p[0] <= xb and za <= p[2] <= zb


def w_czesci(p, ks, o, R, s):
    """Czy punkt p (układ bryły) leży w części Roblox o kształcie ks, środku o, obrocie R i rozmiarze s."""
    d = (p[0] - o[0], p[1] - o[1], p[2] - o[2])
    Rt = tuple(tuple(R[j][i] for j in range(3)) for i in range(3))     # odwrotność obrotu
    q = razy_wektor(Rt, d)
    u, v, w = q[0] / s[0] + 0.5, q[1] / s[1] + 0.5, q[2] / s[2] + 0.5
    if not (0 <= u <= 1 and 0 <= v <= 1 and 0 <= w <= 1):
        return False
    if ks == rk.BLOK:
        return True
    if ks == rk.KLIN:                                                   # skos od górnej krawędzi +Z do dolnej −Z
        return v <= w
    if ks == rk.NAROZNIK:                                               # wierzchołek nad rogiem (+X, −Z)
        return u >= v and w <= 1 - v
    raise ValueError(ks)


def test_ostroslupow(n=400, punktow=1500, ziarno=7):
    rnd = random.Random(ziarno)
    najgorszy, razem_zle, razem = 0.0, 0, 0
    for i in range(n):
        sx, sy, sz = rnd.uniform(0.3, 3), rnd.uniform(0.3, 3), rnd.uniform(0.3, 3)
        rodzaj = i % 5
        if rodzaj == 0:                                                 # szpic
            tx = tz = 0.0
        elif rodzaj == 1:                                               # grzbiet wzdłuż X
            tx, tz = rnd.uniform(0.1, sx), 0.0
        elif rodzaj == 2:                                               # grzbiet wzdłuż Z
            tx, tz = 0.0, rnd.uniform(0.1, sz)
        else:                                                           # ścięty
            tx, tz = rnd.uniform(0.05, sx), rnd.uniform(0.05, sz)
        dx = rnd.uniform(-(sx - tx) / 2, (sx - tx) / 2)
        dz = rnd.uniform(-(sz - tz) / 2, (sz - tz) / 2)
        if rodzaj == 4:                                                 # góra większa od podstawy (odwrotny)
            sx, tx, sz, tz = tx if tx > 0.05 else 0.3, sx, tz if tz > 0.05 else 0.3, sz
            dx = rnd.uniform(-(tx - sx) / 2, (tx - sx) / 2)
            dz = rnd.uniform(-(tz - sz) / 2, (tz - sz) / 2)
        c = {"k": "ostroslup", "n": "t", "s": (sx, sy, sz), "gora": [tx, tz], "pg": [dx, dz]}
        uwagi = []
        czesci = rk.rozloz(c, uwagi)
        assert not uwagi, "nieoczekiwane uproszczenie: %r" % (c,)
        zle = 0
        bx, bz = max(sx, tx + 2 * abs(dx)), max(sz, tz + 2 * abs(dz))
        for _ in range(punktow):
            p = (rnd.uniform(-bx / 2, bx / 2), rnd.uniform(-sy / 2, sy / 2), rnd.uniform(-bz / 2, bz / 2))
            a = w_ostroslupie(p, sx, sy, sz, tx, tz, dx, dz)
            b = any(w_czesci(p, ks, o, R, s) for ks, o, R, s, _siatka in czesci)
            zle += a != b
        razem_zle += zle
        razem += punktow
        najgorszy = max(najgorszy, zle / punktow)
    return razem_zle / razem, najgorszy


def test_ukladu(n=300, ziarno=11):
    """Bryła o obrocie R i położeniu p po zamianie układu = bryła obrócona razem z rigiem o 180° wokół Y.
    Zwraca (błąd brył, błąd póz). Błąd brył bywa rzędu 1e-3 przy obrocie rx bliskim ±90° — to próg „blokady
    przegubu” w katy_z_macierzy biblioteki (odchyłka do ok. 0,15°), nie błąd zamiany układu."""
    rnd = random.Random(ziarno)
    Y = rk.Y180
    blad_bryl, blad_poz = 0.0, 0.0
    for _ in range(n):
        r = (rnd.uniform(-180, 180), rnd.uniform(-180, 180), rnd.uniform(-180, 180))
        R = macierz_obrotu(*r)
        # 1) bryła: kąty zwrócone przez _katy_bryly muszą dawać macierz Y·R
        katy = [math.degrees(v) for v in rk._katy_bryly(R)]
        A, B = macierz_obrotu(*katy), mnoz(Y, R)
        blad_bryl = max(blad_bryl, max(abs(A[i][j] - B[i][j]) for i in range(3) for j in range(3)))
        # 2) poza: kąty z _katy_pozy muszą dawać sprzężenie Y·R·Y⁻¹ (Y jest własną odwrotnością)
        katy = [math.degrees(v) for v in rk._katy_pozy(r)]
        A, B = macierz_obrotu(*katy), mnoz(mnoz(Y, R), Y)
        blad_poz = max(blad_poz, max(abs(A[i][j] - B[i][j]) for i in range(3) for j in range(3)))
    return blad_bryl, blad_poz


if __name__ == "__main__":
    sredni, najgorszy = test_ostroslupow()
    print("ostrosłupy: średnio %.3f%% punktów niezgodnych, najgorszy przypadek %.2f%%" % (sredni * 100, najgorszy * 100))
    blad_bryl, blad_poz = test_ukladu()
    print("zamiana układu: największy błąd macierzy brył %.2e, póz %.2e" % (blad_bryl, blad_poz))
    ok = sredni < 0.002 and najgorszy < 0.01 and blad_bryl < 5e-3 and blad_poz < 1e-9
    print("WYNIK:", "ZGODNE" if ok else "NIEZGODNE")
    sys.exit(0 if ok else 1)
