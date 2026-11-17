# -*- coding: utf-8 -*-
"""Pozy aktora DOKŁADNIE tak, jak liczy je gra: lustro modułu swiat/test_walki2/zrodla/Klipy.luau + stawy Motor6D.

Gra (Klipy.luau):
  przelicz   klatka kości = CFrame.new(x, y, z) * CFrame.fromOrientation(rx, ry, rz)        (dane co klatkę, 30 kl./s)
  probka     czas klipu → klatki i0 = floor(czas·fps), i0 + 1 i ułamek u; po ostatniej klatce — ostatnia klatka
  zastosuj   każda kość: pa:Lerp(pb, u) (kość spoza klipu = CFrame.identity); tory od najstarszego, poza =
             stara:Lerp(nowa, w / suma wag); gdy suma wag < 1 — CFrame.identity:Lerp(poza, suma)
  krok       przejście: nowy tor waga 0 → 1 w czasie `przejscie`, stare 1 → 0 w tym samym czasie; czas toru biegnie
             z jego prędkością; klip niezapętlony stoi w ostatniej klatce, zapętlony zawija się
Stawy (budowa/szablon.luau): Part1.CFrame = Part0.CFrame * C0 * Transform * C1:Inverse(), C0 = CFrame.new(staw −
środek rodzica), C1 = CFrame.new(staw − środek kości); korzeń (HumanoidRootPart) zakotwiczony w `hrp`; bryła
przyspawana = kość * CFrame.new(−środek kości) * bryła w spoczynku. To te same wzory co swiat/test_walki2/geometria.py
(istniejące lustro — test test_przenikania.py pilnuje, że oba dają to samo do 1e-9).
CFrame:Lerp = położenie liniowo, obrót po kwaternionach (slerp, krótszą drogą).

Odtwarzacz walki NIE używa nakładek kości (ustawNakladke) — ruch proceduralny (doskok, pochylenie, obrót, zejście
w tył) przesuwa i obraca całego aktora sztywno, więc nie zmienia położenia broni względem głowy i tułowia.
"""
import math
import os
import sys

import numpy as np

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TU)))
WALKA = os.path.join(REPO, "swiat", "test_walki2")
if WALKA not in sys.path:
    sys.path.insert(0, WALKA)
from geometria import orientacja  # noqa: E402  (CFrame.fromOrientation z lustra pakietu walki)


# --------------------------------------------------------------------------- kwaterniony (w, x, y, z)
def kwat_z_macierzy(R):
    R = np.asarray(R, dtype=float)
    t = R[0, 0] + R[1, 1] + R[2, 2]
    if t > 0:
        s = math.sqrt(t + 1.0) * 2
        q = (0.25 * s, (R[2, 1] - R[1, 2]) / s, (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s)
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = math.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2
        q = ((R[2, 1] - R[1, 2]) / s, 0.25 * s, (R[0, 1] + R[1, 0]) / s, (R[0, 2] + R[2, 0]) / s)
    elif R[1, 1] > R[2, 2]:
        s = math.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2
        q = ((R[0, 2] - R[2, 0]) / s, (R[0, 1] + R[1, 0]) / s, 0.25 * s, (R[1, 2] + R[2, 1]) / s)
    else:
        s = math.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2
        q = ((R[1, 0] - R[0, 1]) / s, (R[0, 2] + R[2, 0]) / s, (R[1, 2] + R[2, 1]) / s, 0.25 * s)
    q = np.array(q)
    return q / np.linalg.norm(q)


def macierz_z_kwat(q):
    """q (..., 4) -> (..., 3, 3)."""
    w, x, y, z = q[..., 0], q[..., 1], q[..., 2], q[..., 3]
    R = np.empty(q.shape[:-1] + (3, 3))
    R[..., 0, 0] = 1 - 2 * (y * y + z * z)
    R[..., 0, 1] = 2 * (x * y - z * w)
    R[..., 0, 2] = 2 * (x * z + y * w)
    R[..., 1, 0] = 2 * (x * y + z * w)
    R[..., 1, 1] = 1 - 2 * (x * x + z * z)
    R[..., 1, 2] = 2 * (y * z - x * w)
    R[..., 2, 0] = 2 * (x * z - y * w)
    R[..., 2, 1] = 2 * (y * z + x * w)
    R[..., 2, 2] = 1 - 2 * (x * x + y * y)
    return R


def slerp(q0, q1, u):
    """Slerp krótszą drogą; q0, q1 (..., 4), u skalar albo (...)."""
    u = np.asarray(u, dtype=float)
    dot = np.sum(q0 * q1, axis=-1)
    q1 = np.where((dot < 0)[..., None], -q1, q1)
    dot = np.abs(dot)
    blisko = dot > 0.9995
    th = np.arccos(np.clip(dot, -1, 1))
    s = np.sin(th)
    s_ = np.where(blisko, 1.0, s)
    a = np.where(blisko, 1 - u, np.sin((1 - u) * th) / s_)
    b = np.where(blisko, u, np.sin(u * th) / s_)
    q = a[..., None] * q0 + b[..., None] * q1
    return q / np.linalg.norm(q, axis=-1, keepdims=True)


IDQ = np.array([1.0, 0.0, 0.0, 0.0])


# --------------------------------------------------------------------------- aktor
class Aktor:
    """Rig z danych roblox_klocki.rig() (np. swiat/test_walki2/dane/<klucz>.json) z klipami jak w grze."""

    def __init__(self, dane):
        self.d = dane
        self.kosci = dane["kosci"]
        self.nk = len(self.kosci)
        self.indeks = {k[0]: i + 1 for i, k in enumerate(self.kosci)}
        self.rodzic = [0] + [int(k[1]) for k in self.kosci]          # indeks 0 = HumanoidRootPart
        hrp = np.array(dane["hrp"], dtype=float)
        sr = [hrp] + [np.array(k[5:8], dtype=float) for k in self.kosci]
        self.srodek = sr
        self.C0 = np.zeros((self.nk + 1, 4, 4))
        self.C1i = np.zeros((self.nk + 1, 4, 4))
        for i, k in enumerate(self.kosci, start=1):
            staw = np.array(k[2:5], dtype=float)
            self.C0[i] = _przes(staw - sr[k[1]])
            self.C1i[i] = _przes(-(staw - sr[i]))
        self.korzen = _przes(hrp)
        self.klipy = {}
        for kl in dane.get("klipy", []):
            F = kl["dl"] + 1
            poz = np.zeros((F, self.nk + 1, 3))
            kw = np.tile(IDQ, (F, self.nk + 1, 1))
            jest = np.zeros(self.nk + 1, dtype=bool)
            for f, w in enumerate(kl["klatki"]):
                for j, idx in enumerate(kl["kosci"]):
                    o = j * 6
                    poz[f, idx] = w[o:o + 3]
                    kw[f, idx] = kwat_z_macierzy(orientacja(w[o + 3], w[o + 4], w[o + 5]))
            for idx in kl["kosci"]:
                jest[idx] = True
            self.klipy[kl["n"]] = {"n": kl["n"], "fps": float(kl["fps"]), "petla": bool(kl["petla"]), "dl": kl["dl"],
                                   "dlugosc": kl["dl"] / float(kl["fps"]), "poz": poz, "kw": kw, "jest": jest}
        # bryły
        cz = dane["czesci"]
        self.nb = len(cz)
        self.kosc_bryly = np.array([int(c[0]) for c in cz])
        self.M = np.zeros((self.nb, 4, 4))
        for b, c in enumerate(cz):
            spocz = np.eye(4)
            spocz[:3, :3] = np.array(orientacja(c[6], c[7], c[8]))
            spocz[:3, 3] = c[3:6]
            self.M[b] = _przes(-sr[int(c[0])]) @ spocz

    # -- Klipy.probka + Lerp jednej kości
    def probka(self, nazwa, czas):
        """(położenia (nk+1, 3), kwaterniony (nk+1, 4), maska kości klipu) w chwili czas (s) toru — jak probka+Lerp."""
        k = self.klipy[nazwa]
        f = czas * k["fps"]
        i0 = int(math.floor(f))
        u = f - i0
        if i0 >= k["dl"]:
            return k["poz"][k["dl"]], k["kw"][k["dl"]], k["jest"]
        i0 = max(i0, 0)
        a_p, a_q = k["poz"][i0], k["kw"][i0]
        if u <= 0:
            return a_p, a_q, k["jest"]
        b_p, b_q = k["poz"][i0 + 1], k["kw"][i0 + 1]
        return a_p + (b_p - a_p) * u, slerp(a_q, b_q, u), k["jest"]

    def czas_toru(self, nazwa, czas):
        """Czas toru po upływie `czas` od początku (zapętlony zawija się, niezapętlony stoi na końcu) — jak krok."""
        k = self.klipy[nazwa]
        if k["petla"]:
            return czas % k["dlugosc"] if k["dlugosc"] > 0 else 0.0
        return min(max(czas, 0.0), k["dlugosc"])

    def transformy(self, tory):
        """tory = [(klip, czas, waga), …] od najstarszego -> (położenia, kwaterniony) Transform każdej kości (zastosuj)."""
        poz = np.zeros((self.nk + 1, 3))
        kw = np.tile(IDQ, (self.nk + 1, 1))
        suma = np.zeros(self.nk + 1)
        pierwszy = True
        for nazwa, czas, w in tory:
            if w <= 0:
                continue
            p, q, jest = self.probka(nazwa, czas)
            p = np.where(jest[:, None], p, 0.0)
            q = np.where(jest[:, None], q, IDQ)
            s = suma + w
            if pierwszy:
                poz, kw = p.copy(), q.copy()
                pierwszy = False
            else:
                u = w / s
                poz = poz + (p - poz) * u[:, None]
                kw = slerp(kw, q, u)
            suma = s
        if pierwszy:
            return poz, kw
        mniej = suma < 1
        if np.any(mniej):
            u = np.minimum(suma, 1.0)
            poz = poz * u[:, None]
            kw = np.where(mniej[:, None], slerp(np.tile(IDQ, (self.nk + 1, 1)), kw, u), kw)
        return poz, kw

    def kosci_swiat(self, poz, kw):
        """Transform każdej kości -> CFrame części kości w układzie modelu (nk+1, 4, 4); 0 = HumanoidRootPart."""
        T = np.zeros((self.nk + 1, 4, 4))
        T[:, :3, :3] = macierz_z_kwat(kw)
        T[:, :3, 3] = poz
        T[:, 3, 3] = 1.0
        W = np.zeros((self.nk + 1, 4, 4))
        W[0] = self.korzen
        for i in range(1, self.nk + 1):
            W[i] = W[self.rodzic[i]] @ self.C0[i] @ T[i] @ self.C1i[i]
        return W

    def bryly_swiat(self, W):
        """CFrame każdej bryły (nb, 4, 4) dla CFrame'ów kości W."""
        return W[self.kosc_bryly] @ self.M

    def poza(self, tory):
        """tory -> (kości (nk+1, 4, 4), bryły (nb, 4, 4))."""
        W = self.kosci_swiat(*self.transformy(tory))
        return W, self.bryly_swiat(W)

    def potomkowie(self, nazwy):
        """Indeksy kości z `nazwy` i wszystkich ich potomków."""
        zb = {self.indeks[n] for n in nazwy if n in self.indeks}
        zmiana = True
        while zmiana:
            zmiana = False
            for i in range(1, self.nk + 1):
                if i not in zb and self.rodzic[i] in zb:
                    zb.add(i)
                    zmiana = True
        return zb


def _przes(v):
    m = np.eye(4)
    m[:3, 3] = v
    return m
