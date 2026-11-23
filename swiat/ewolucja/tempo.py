#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Symulacja tempa Monster Evolution (bez Studio): kiedy pierwsza i druga ewolucja, pierwsze ulepszenie, pierwsze
zagrożenie, forma 5 i Olbrzym — dla „sprawnego gracza” na polu z botami.

    python -B swiat/ewolucja/tempo.py [--prob 6] [--minut 18] [--gracz sprawny|sredni]

Model: przeniesione do Pythona te same zasady co w zrodla/LogikaEwolucji.luau (liczby z tych samych danych, dane.py):
ruch, kulki, BITE, DASH, umiejętności, boty (ucieczka / pościg / kulki / strefy startu), śmierć o formę niżej,
legowisko, ulepszenia. Kulki szukane w siatce (tylko szybkość; zasady te same). Krok 0,1 s (w grze 0,05 s).
Gracz „sprawny”: idzie do najlepszej zdobyczy (wartość / odległość), ucieka przed większymi w pobliżu, gryzie i używa
umiejętności, gdy coś jest w zasięgu, EVOLVE od razu, kupuje najtańsze dostępne ulepszenie. „Średni”: reaguje wolniej,
widzi bliżej i co jakiś czas się rozprasza.
Cele (projekt): 1. ewolucja 20–30 s, 2. do 1:30, 1. ulepszenie 1:30–2:00, zagrożenie ok. 2:00, forma 5 w 6–7 min,
Olbrzym ok. 15 min.
"""
import argparse
import math
import os
import random
import statistics
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import dane as DN  # noqa: E402

# odczucie1: warianty małych celów do porównań (domyślnie: jak w grze)
# czy gracz idzie do legowiska specjalnie po poziom trofeum: brak (jak w grze od odczucie1) | pelne | przy_zlocie
TROFEA_DOM = os.environ.get("TEMPO_TROFEA", "brak")
POLOWA = os.environ.get("TEMPO_POLOWA", "1") == "1"  # baner połowy paska liczony jako nowość


def dlug(x, z):
    return math.sqrt(x * x + z * z)


class Swiat:
    def __init__(self, D, los):
        self.D, self.los, self.czas = D, los, 0.0
        self.byty, self.nast = [], 1
        self.kulki = [0.0] * len(D["kulkiPoz"])
        # owce (swiat1): stadka na łące jako zdobycz dotykiem (bez ucieczki — sprawny gracz i tak dogania: 16+ st./s > 13)
        Ow = (D.get("swiat") or {}).get("owce")
        self.owce = []
        if Ow:
            for sx, sz in Ow["stada"]:
                for k in range(Ow["na_stado"]):
                    a = k * 2.1
                    self.owce.append({"x": sx + math.cos(a) * 4, "z": sz + math.sin(a) * 4, "do": 0.0})
        self.owce_wzrost = Ow["wzrost"] if Ow else 0
        # retencja1: trzy zadania dnia gracza (typowe losowanie: kulki, owce, walki) — nagroda złoto + wzrost, liczone jako nowość
        Z = D.get("zadania")
        self.zadania = []
        if Z:
            for zid in ("kulki", "owce", "walki"):
                q = next(x for x in Z["pula"] if x["id"] == zid)
                self.zadania.append({"id": zid, "cel": q["cel"], "p": 0, "zloto": q["zloto"], "wzrost": q["wzrost"], "g": False})
        self.owce_powrot = Ow["powrot_s"] if Ow else 0
        self.strefy = []
        self.siatka = {}
        for i, p in enumerate(D["kulkiPoz"]):
            self.siatka.setdefault((int(p[0] // 12), int(p[1] // 12)), []).append(i)
        self.U = {u["id"]: u for u in D["ulepszenia"]}

    # ------------------------------------------------ liczby
    def r(self, b):
        return self.D["formy"][b["forma"] - 1]["r"]

    def potrzeba(self, f):
        return self.D["formy"][f - 1]["potrzeba"]

    def stawka(self, m):
        return sum(self.D["formy"][i]["trofeum"] for i in range(m))

    def wx(self, w):
        return next((W["x"] for W in self.D["warianty"] if W["id"] == w), 1)

    def stawkaB(self, b):
        G = self.D["legowisko"]
        s = sum(self.D["formy"][f]["trofeum"] * G["poziomy_x"][b["trofea"].get(f + 1, 1) - 1] * self.wx(b["warianty"].get(f + 1))
                for f in range(b["max"]))
        return s + sum(G["boss_trofea"][:b["boss_trofea"]])

    def leg(self, b):
        return self.D["legowiska"][(b["slot"] - 1) % len(self.D["legowiska"])]

    def w_legowisku(self, b):
        if not b["slot"]:
            return False
        x, z = self.leg(b)
        return dlug(b["x"] - x, b["z"] - z) < self.D["legowisko"]["r"]

    def los_wariant(self):
        x = self.los.random()
        for W in reversed(self.D["warianty"]):
            x -= W["szansa"]
            if x < 0:
                return W["id"]
        return None

    def cena_trofeum(self, b, f):
        p = b["trofea"].get(f, 1)
        c = self.D["legowisko"]["ceny_x"]
        return None if p > len(c) else int(c[p - 1] * self.D["formy"][f - 1]["trofeum"])

    def v(self, b):
        baza = self.U["szybkosc"]["wartosci"][b["pz"]["szybkosc"] - 1] if b["slot"] else self.D["ruch"]["bot_v"]
        return baza * self.D["formy"][b["forma"] - 1]["v"]

    def apetyt(self, b):
        return self.U["apetyt"]["wartosci"][b["pz"]["apetyt"] - 1] if b["slot"] else 1

    def zasieg(self, b):
        return self.U["szczeka"]["zasieg"][b["pz"]["szczeka"] - 1] if b["slot"] else self.D["gryzienie"]["bot_zasieg"]

    def przerwa(self, b):
        return self.U["szczeka"]["przerwa_s"][b["pz"]["szczeka"] - 1] if b["slot"] else self.D["gryzienie"]["bot_przerwa_s"]

    def wartosc(self, b):
        w = self.D["jedzenie"]["za_forme"][b["forma"] - 1]
        return w * self.D["jedzenie"]["gracz_x"] if b["slot"] else w

    def moze(self, a, b):
        if a.get("boss") or b.get("boss") or a["forma"] < b["forma"] + 1:
            return False
        return not (a["slot"] and b["slot"] and b["forma"] <= self.D["smierc"]["chronione_formy"])

    def wolny(self, b):
        return b["martwy"] is None and b["kokon"] is None and b["skok"] is None

    def bezbronny(self, b):
        return self.wolny(b) and b["tarcza"] <= self.czas and not (b["slot"] and self.w_legowisku(b))

    def ster_serwer(self, b):
        return b["martwy"] is not None or b["kokon"] is not None or b["skok"] is not None or b["ogl"] > self.czas

    def maska(self, b):
        if not b["slot"]:
            return b.get("strefa", 1)
        return 3 if b["max"] >= self.D["las"]["od_formy"] else 1

    def w_lesie(self, x, z):
        LS = self.D["las"]
        return dlug(x - LS["x"], z - LS["z"]) < LS["r"] and dlug(x, z) > self.D["pole"]["r"] - 2

    def ogranicz(self, x, z, r, maska=1):
        LS = self.D["las"]
        m1, m2 = self.D["pole"]["r"] - r * 0.6, LS["r"] - r * 0.6
        d1 = dlug(x, z)
        lx, lz = x - LS["x"], z - LS["z"]
        d2 = dlug(lx, lz)
        if not ((maska != 2 and d1 <= m1) or (maska >= 2 and d2 <= m2)):
            e1 = d1 - m1 if maska != 2 else 1e9
            e2 = d2 - m2 if maska >= 2 else 1e9
            if e1 <= e2:
                x, z = x / d1 * m1, z / d1 * m1
            else:
                x, z = LS["x"] + lx / d2 * m2, LS["z"] + lz / d2 * m2
        for s in self.D["przeszkody"]:
            ds = dlug(x - s["x"], z - s["z"])
            mn = s["r"] + r * 0.7
            if 0.01 < ds < mn:
                x, z = s["x"] + (x - s["x"]) / ds * mn, s["z"] + (z - s["z"]) / ds * mn
        return x, z

    def bezpieczne(self, forma, gracz, strefa=1, slot=0):
        D = self.D
        if gracz and slot:
            x, z = D["legowiska"][(slot - 1) % len(D["legowiska"])]
            return x * 0.97, z * 0.97
        best, wynik = -1, None
        for _ in range(24):
            if gracz:
                k = D["kulkiPoz"][int(self.los.random() * len(D["kulkiPoz"]))]
                x, z = k[0] * 0.97 + 3, k[1] * 0.97 - 3
            elif strefa == 2:
                LS = D["las"]
                a, r = self.los.random() * 2 * math.pi, math.sqrt(self.los.random()) * (LS["r"] - 14)
                x, z = LS["x"] + math.sin(a) * r, LS["z"] + math.cos(a) * r
                if dlug(x, z) < D["pole"]["r"] + 6:
                    x, z = LS["x"], LS["z"] + LS["r"] * 0.4
            else:
                a, r = self.los.random() * 2 * math.pi, math.sqrt(self.los.random()) * (D["pole"]["r"] - 14)
                x, z = math.sin(a) * r, math.cos(a) * r
            x, z = self.ogranicz(x, z, D["formy"][forma - 1]["r"], 1 if gracz else strefa)
            nb = 999
            for q in self.byty:
                if q["martwy"] is None:
                    d = dlug(q["x"] - x, q["z"] - z)
                    if gracz and q["forma"] > forma:
                        nb = min(nb, d - q["forma"] * 2)
                    elif not gracz and q["slot"]:
                        nb = min(nb, d)
            if nb > best:
                best, wynik = nb, (x, z)
            if (gracz and nb > 45) or (not gracz and nb > D["boty"]["od_graczy"]):
                break
        return wynik

    def dodaj(self, slot, forma, strefa=1):
        x, z = self.bezpieczne(forma, slot > 0, strefa, slot)
        b = {"id": self.nast, "slot": slot, "forma": forma, "x": x, "z": z, "vx": 0.0, "vz": 0.0, "wx": 0.0, "wz": 0.0, "kier": 0.0,
             "tarcza": self.czas + (self.D["smierc"]["tarcza_s"] if slot else 0), "martwy": None, "kokon": None, "skok": None,
             "zryw": 0.0, "zryw_ok": 0.0, "gryz_ok": 0.0, "um_ok": 0.0, "ogl": 0.0, "szarza": 0.0, "szarza_v": 1.0, "mysl": 0.0,
             "cel": 0, "cel_od": 0.0, "odp": 0, "odp_do": 0.0, "wzrost": 0.0, "max": forma, "zloto": 0.0,
             "pz": {"szczeka": 1, "szybkosc": 1, "apetyt": 1}, "laska": self.czas + self.D["boty"]["laska_s"] if slot else 0, "strefa": strefa,
             "zloto_leg": 0.0, "warianty": {}, "trofea": {}, "boss_trofea": 0, "kokon_w": None,
             "zyc": 0.0, "zycm": 0.0, "ost_r": -99.0, "lanc": 0, "lanc_do": 0.0}
        self.nast += 1
        self.byty.append(b)
        if slot:
            self.strefy.append((x, z, self.czas + self.D["boty"]["strefa_startu_s"]))
        return b

    def dodaj_bossa(self):
        B, LS = self.D["boss"], self.D["las"]
        b = self.dodaj(0, B["forma"], 2)
        b["x"], b["z"] = LS["x"], LS["z"]
        self.boss_st = 1
        b.update({"boss": True, "hp": B["stopnie_hp"][0], "dom": (b["x"], b["z"]), "ost_rana": -99.0})
        self.boss = b
        return b

    def obrazenia(self, g):
        W = self.D["walka"]
        s = W["gryz_baza"] * W["gryz_wzrost"] ** (g["forma"] - 1)
        if g["slot"]:
            s *= W["szczeka_x"][g["pz"]["szczeka"] - 1]
        return s

    # ------------------------------------------------ walka1 (jak LogikaEwolucji: życie, łańcuch BITE, rozmiar)
    def zycm(self, b):
        W = self.D["walka"]
        return W["hp_baza"] * W["hp_wzrost"] ** (b["forma"] - 1)

    def rozm(self, a, q):
        if a.get("boss") or q.get("boss"):
            return 1.0
        return self.D["walka"]["rozmiar_x"][max(-3, min(3, a["forma"] - q["forma"])) + 3]

    def rana(self, a, q, ile, kryt=True):
        W = self.D["walka"]
        if q.get("boss"):
            self.ran(q, a, ile)
            return
        ile *= self.rozm(a, q)
        if kryt and self.los.random() < W["kryt_szansa"]:
            ile *= W["kryt_x"]
        q["zyc"] -= max(1, round(ile))
        q["ost_r"] = self.czas
        if q["zyc"] <= 0:
            self.zjedz(a, q)

    def cios(self, b, q):
        """Jeden cios łańcucha BITE w q (rytm lancuch_s, trzeci mocniejszy)."""
        W = self.D["walka"]
        if self.czas > b["lanc_do"]:
            b["lanc"] = 0
        k = b["lanc"] % 3 + 1
        b["lanc"] = k
        b["gryz_ok"] = self.czas + W["lancuch_s"][k - 1]
        b["lanc_do"] = b["gryz_ok"] + W["lancuch_reset_s"]
        self.rana(b, q, self.obrazenia(b) * W["lancuch_x"][k - 1])
        if k == 3 and not q.get("boss") and q["martwy"] is None:
            q["ogl"] = max(q["ogl"], self.czas + W["przewrot_s"])

    def boss_w(self, g, zas):
        b = getattr(self, "boss", None)
        if not b or b["martwy"] is not None or not g["slot"]:
            return None
        return b if dlug(b["x"] - g["x"], b["z"] - g["z"]) < self.r(g) + zas + self.r(b) else None

    def ran(self, boss, g, ile):
        if boss["martwy"] is not None or boss["hp"] <= 0:
            return
        boss["hp"] = max(0, boss["hp"] - ile)
        boss["ost_rana"] = self.czas
        if g["slot"]:
            self.zdarzenia.append(("boss_rana", 0))
        if boss["hp"] <= 0:
            B = self.D["boss"]
            st = self.boss_st
            g["zloto"] += B["stopnie_skrzynia"][st - 1]
            self.zdarzenia.append(("boss_pokonany", 0))
            if g["boss_trofea"] < st:
                g["boss_trofea"] = st
                self.zdarzenia.append(("boss_stopien", st))
            self.boss_pokonany = True
            self.boss_st = min(len(B["stopnie_hp"]), st + 1)
            boss["martwy"] = self.czas + (B["odrodzenie_s"] if st == 1 else B["odrodzenie_dalej_s"])

    # ------------------------------------------------ jedzenie
    def kulki_w(self, x, z, r, ile):
        lista = []
        cx, cz, n = int(x // 12), int(z // 12), int(r // 12) + 1
        for i in range(cx - n, cx + n + 1):
            for j in range(cz - n, cz + n + 1):
                for k in self.siatka.get((i, j), ()):
                    if self.kulki[k] == 0:
                        p = self.D["kulkiPoz"][k]
                        d = dlug(p[0] - x, p[1] - z)
                        if d < r:
                            lista.append((d, k))
        lista.sort()
        return [k for _, k in lista[:ile]]

    def wzrost(self, b, ile):
        if b["forma"] >= len(self.D["formy"]):
            return
        b["wzrost"] = min(self.potrzeba(b["forma"]) * self.D["ewolucja"]["pasek_maks"], b["wzrost"] + ile)

    def zadanie(self, b, zid):
        if not b["slot"]:
            return
        for q in self.zadania:
            if q["id"] == zid and not q["g"]:
                q["p"] += 1
                if q["p"] >= q["cel"]:
                    q["g"] = True
                    b["zloto"] += q["zloto"]
                    if b["forma"] < len(self.D["formy"]):
                        p_ = self.potrzeba(b["forma"])
                        b["wzrost"] = min(p_ * self.D["ewolucja"]["pasek_maks"], b["wzrost"] + q["wzrost"] * p_)
                    self.zdarzenia.append(("zadanie", zid))

    def zjedz_kulke(self, b, i):
        J = self.D["jedzenie"]
        typ = self.D["kulkiPoz"][i][2]
        if b["zycm"]:
            b["zyc"] = min(b["zycm"], b["zyc"] + b["zycm"] * self.D["walka"]["kulka_leczy"][typ - 1])
        self.kulki[i] = self.czas + (J["powrot_duza_s"] if typ >= 2 else J["powrot_mala_s"])
        if b["slot"]:
            self.wzrost(b, (J["wielka"] if typ == 3 else (J["duza"] if typ == 2 else J["mala"])) * self.apetyt(b))
            self.zadanie(b, "kulki")

    def zgin(self, b):
        b["martwy"] = self.czas + (self.D["smierc"]["odrodzenie_s"] if b["slot"] else self.D["boty"]["odrodzenie_s"])
        b["vx"] = b["vz"] = b["wx"] = b["wz"] = 0.0
        b["szarza"] = b["zryw"] = 0.0
        b["skok"] = None
        b["zycm"] = 0.0  # pełne życie po odrodzeniu (krok ustawia z nowej formy)
        if b["slot"]:
            self.zdarzenia.append(("smierc", b["forma"]))

    def zjedz(self, a, b):
        if a["slot"]:
            self.wzrost(a, self.wartosc(b) * self.apetyt(a))
            self.zadanie(a, "walki")
        self.zgin(b)

    def przypadkiem(self, a, q):
        if a["slot"] or not q["slot"]:
            return False
        return q["laska"] > self.czas or (q["forma"] <= self.D["smierc"]["chronione_formy"] and a["cel"] != q["id"])

    def ofiara(self, a, zas):
        if a["slot"] and self.w_legowisku(a):
            return None
        ra = self.r(a)
        best, bd = None, 1e9
        for q in self.byty:
            if q is not a and self.bezbronny(q) and self.moze(a, q) and not self.przypadkiem(a, q):
                d = dlug(q["x"] - a["x"], q["z"] - a["z"])
                if d < ra + zas + self.r(q) and d < bd:
                    best, bd = q, d
        return best

    def gryz(self, b):
        if self.ster_serwer(b) or self.czas < b["gryz_ok"]:
            return False
        q = self.ofiara(b, self.zasieg(b))
        boss = None if q else self.boss_w(b, self.zasieg(b))
        if q or boss:
            self.cios(b, q or boss)
        else:
            b["gryz_ok"] = self.czas + self.D["walka"]["lancuch_s"][0]
            for i in self.kulki_w(b["x"], b["z"], self.r(b) + self.zasieg(b) + self.D["jedzenie"]["mala_r"], 3):
                self.zjedz_kulke(b, i)
        return True

    def zryw(self, b):
        if self.ster_serwer(b) or self.czas < b["zryw_ok"]:
            return False
        b["zryw"] = self.czas + self.D["ruch"]["zryw_s"]
        b["zryw_ok"] = self.czas + self.D["ruch"]["zryw_odnowa_s"]
        return True

    def oglusz(self, b, r, czas):
        for q in self.byty:
            if q is not b and self.wolny(q) and q["tarcza"] <= self.czas and dlug(q["x"] - b["x"], q["z"] - b["z"]) < r + self.r(q) \
                    and not (b["slot"] and q["slot"] and q["forma"] <= self.D["smierc"]["chronione_formy"]):
                q["ogl"] = self.czas + (czas * 0.5 if q.get("boss") else czas)
                q["vx"] = q["vz"] = 0.0

    def umiejetnosc(self, b):
        if self.ster_serwer(b) or self.czas < b["um_ok"]:
            return False
        A = self.D["formy"][b["forma"] - 1]["um"]
        b["um_ok"] = self.czas + A["odnowa_s"]
        rb = self.r(b)
        t = A["typ"]
        if t == "wsysanie":
            for i in self.kulki_w(b["x"], b["z"], rb + A["r"], 99):
                self.zjedz_kulke(b, i)
        elif t == "jezyk":
            q = self.ofiara(b, A["r"])
            boss = None if q else self.boss_w(b, A["r"])
            if q:
                self.rana(b, q, self.obrazenia(b) * 6)
            elif boss:
                self.ran(boss, b, self.D["boss"]["um_obrazenia"])
            else:
                for i in self.kulki_w(b["x"], b["z"], rb + A["r"], 4):
                    self.zjedz_kulke(b, i)
        elif t == "szarza":
            b["szarza"], b["szarza_v"] = self.czas + A["s"], A["v"]
        elif t == "ogluszenie":
            self.oglusz(b, rb + A["r"], A["s"])
            if self.boss_w(b, A["r"]):
                self.ran(self.boss, b, self.D["boss"]["um_obrazenia"])
        elif t == "skok":
            d = dlug(b["wx"], b["wz"]) or 1
            kx, kz = (b["wx"] / d, b["wz"] / d) if (b["wx"] or b["wz"]) else (math.sin(b["kier"]), math.cos(b["kier"]))
            x1, z1 = self.ogranicz(b["x"] + kx * A["d"], b["z"] + kz * A["d"], rb, self.maska(b))
            b["skok"] = (b["x"], b["z"], x1, z1, self.czas, self.czas + A["s"], A["r"])
        elif t == "podmuch":
            for q in self.byty:
                d = dlug(q["x"] - b["x"], q["z"] - b["z"])
                if q is not b and self.wolny(q) and q["tarcza"] <= self.czas and not q.get("boss") and d < rb + A["r"] + self.r(q) \
                        and not (b["slot"] and q["slot"] and q["forma"] <= self.D["smierc"]["chronione_formy"]):
                    d = max(0.1, d)
                    q["x"], q["z"] = self.ogranicz(q["x"] + (q["x"] - b["x"]) / d * A["sila"], q["z"] + (q["z"] - b["z"]) / d * A["sila"], self.r(q), self.maska(q))
                    q["ogl"] = self.czas + A["s"]
        elif t == "oddech":
            kx, kz = math.sin(b["kier"]), math.cos(b["kier"])
            ck = math.cos(math.radians(A["kat_st"] / 2))

            def w_st(x, z, zas):
                dx, dz = x - b["x"], z - b["z"]
                d = dlug(dx, dz)
                return d < zas and (d < 0.5 or (dx * kx + dz * kz) / d >= ck)
            if not (b["slot"] and self.w_legowisku(b)):
                n = 0
                for q in list(self.byty):
                    if n < 3 and q is not b and self.bezbronny(q) and self.moze(b, q) and not self.przypadkiem(b, q) and w_st(q["x"], q["z"], rb + A["r"] + self.r(q) * 0.5):
                        self.rana(b, q, self.obrazenia(b) * 6)
                        n += 1
                for i in self.kulki_w(b["x"], b["z"], rb + A["r"], 99):
                    p = self.D["kulkiPoz"][i]
                    if w_st(p[0], p[1], rb + A["r"]):
                        self.zjedz_kulke(b, i)
                boss = self.boss_w(b, A["r"])
                if boss and w_st(boss["x"], boss["z"], rb + A["r"] + self.r(boss)):
                    self.ran(boss, b, self.D["boss"]["um_obrazenia"])
        elif t == "fala":
            self.oglusz(b, rb + A["r"], A["s"])
            if self.boss_w(b, A["r"]):
                self.ran(self.boss, b, self.D["boss"]["um_obrazenia"])
            for i in self.kulki_w(b["x"], b["z"], rb + A["r"], 99):
                self.zjedz_kulke(b, i)
        return True

    def ewoluuj(self, b):
        if b["forma"] >= len(self.D["formy"]) or b["wzrost"] < self.potrzeba(b["forma"]) or self.ster_serwer(b):
            return False
        nowa = b["forma"] + 1 > b["max"]
        b["kokon"] = self.czas + (self.D["ewolucja"]["kokon_s"] if nowa else self.D["ewolucja"]["kokon_znana_s"])
        b["kokon_w"] = self.los_wariant() if b["slot"] else None
        b["vx"] = b["vz"] = b["wx"] = b["wz"] = 0.0
        return True

    def kup(self, b, uid):
        U = self.U[uid]
        p = b["pz"][uid]
        if p > len(U["ceny"]) or b["zloto"] < U["ceny"][p - 1]:
            return False
        b["zloto"] -= U["ceny"][p - 1]
        b["pz"][uid] = p + 1
        return True

    # ------------------------------------------------ boty
    def mysl(self, b):
        D, B = self.D, self.D["boty"]
        r = self.r(b)
        zagr, dz, of, dof = None, 1e9, None, 1e9
        for q in self.byty:
            if q is b or q["martwy"] is not None:
                continue
            d = dlug(q["x"] - b["x"], q["z"] - b["z"])
            if self.moze(q, b) and self.wolny(q):
                if d < B["widzi"] + self.r(q) and d < dz:
                    zagr, dz = q, d
            elif self.moze(b, q) and self.bezbronny(q):
                w = B["widzi_mlodych"] if (q["slot"] and q["forma"] <= D["smierc"]["chronione_formy"]) else B["widzi"]
                if (q["id"] == b["odp"] and self.czas < b["odp_do"]) or (q["slot"] and q["laska"] > self.czas):
                    w = -999
                if d < w + r and d < dof:
                    of, dof = q, d
        strefa = None
        if b["forma"] > 1:
            for s in self.strefy:
                if self.czas < s[2] and dlug(b["x"] - s[0], b["z"] - s[1]) < B["strefa_startu_r"] + r:
                    strefa = s
        if of and of["slot"]:
            for s in self.strefy:
                if self.czas < s[2] and dlug(of["x"] - s[0], of["z"] - s[1]) < B["strefa_startu_r"]:
                    of = None
                    break
        if zagr:
            d = max(0.1, dz)
            ux, uz = (b["x"] - zagr["x"]) / d, (b["z"] - zagr["z"]) / d
            cx, cz, R = (D["las"]["x"], D["las"]["z"], D["las"]["r"]) if b["strefa"] == 2 else (0, 0, D["pole"]["r"])
            dc = dlug(b["x"] - cx, b["z"] - cz)
            if dc > R - 20:
                tx, tz = -(b["z"] - cz) / dc, (b["x"] - cx) / dc
                if tx * ux + tz * uz < 0:
                    tx, tz = -tx, -tz
                ux, uz = ux * 0.4 + tx * 0.6 - (b["x"] - cx) / dc * 0.3, uz * 0.4 + tz * 0.6 - (b["z"] - cz) / dc * 0.3
            n = max(0.01, dlug(ux, uz))
            b["wx"], b["wz"] = ux / n * B["panika"], uz / n * B["panika"]
            if dz < self.r(zagr) + r + 5 and self.los.random() < B["zryw_szansa"]:
                self.zryw(b)
            b["cel"] = 0
        elif strefa:
            d = max(0.1, dlug(b["x"] - strefa[0], b["z"] - strefa[1]))
            b["wx"], b["wz"] = (b["x"] - strefa[0]) / d, (b["z"] - strefa[1]) / d
            b["cel"] = 0
        elif of:
            if b["cel"] != of["id"]:
                b["cel"], b["cel_od"] = of["id"], self.czas
                if of["slot"] and getattr(self, "poscig", None) is None:
                    self.poscig = self.czas
            elif self.czas - b["cel_od"] > B["goni_maks_s"]:
                b["odp"], b["odp_do"], b["cel"] = of["id"], self.czas + B["odpuszcza_s"], 0
            d = max(0.1, dof)
            b["wx"], b["wz"] = (of["x"] - b["x"]) / d, (of["z"] - b["z"]) / d
            if dof < r + self.r(of) + 6 and self.los.random() < B["zryw_szansa"]:
                self.zryw(b)
        else:
            b["cel"] = 0
            k = self.kulki_w(b["x"], b["z"], 34, 1) if b["forma"] <= B["kulki_do"] else []
            if k:
                p = D["kulkiPoz"][k[0]]
                d = max(0.1, dlug(p[0] - b["x"], p[1] - b["z"]))
                b["wx"], b["wz"] = (p[0] - b["x"]) / d * 0.85, (p[1] - b["z"]) / d * 0.85
            elif self.los.random() < 0.25 or (b["wx"] == 0 and b["wz"] == 0):
                a = self.los.random() * 2 * math.pi
                cx, cz, R = (D["las"]["x"], D["las"]["z"], D["las"]["r"]) if b["strefa"] == 2 else (0, 0, D["pole"]["r"])
                b["wx"] = math.sin(a) * 0.6 - (b["x"] - cx) / R * 0.3
                b["wz"] = math.cos(a) * 0.6 - (b["z"] - cz) / R * 0.3
        b["mysl"] = self.czas + B["myslenie_s"] * (0.7 + self.los.random() * 0.6)

    def mysl_bossa(self, b):
        B = self.D["boss"]
        cel, dc = None, B["widzi"]
        for q in self.byty:
            if q["slot"] and self.wolny(q) and self.w_lesie(q["x"], q["z"]):
                d = dlug(q["x"] - b["x"], q["z"] - b["z"])
                if d < dc:
                    cel, dc = q, d
        if cel:
            b["cel"] = cel["id"]
            d = max(0.1, dc)
            b["wx"], b["wz"] = (cel["x"] - b["x"]) / d * B["v"], (cel["z"] - b["z"]) / d * B["v"]
        else:
            b["cel"] = 0
            dx, dz = b["dom"][0] - b["x"], b["dom"][1] - b["z"]
            d = dlug(dx, dz)
            b["wx"], b["wz"] = (dx / d * B["v"] * 0.6, dz / d * B["v"] * 0.6) if d > 6 else (0.0, 0.0)
        b["mysl"] = self.czas + 0.3

    # ------------------------------------------------ krok
    def krok(self, dt):
        D = self.D
        self.czas += dt
        self.strefy = [s for s in self.strefy if self.czas < s[2]]
        for b in self.byty:
            if b["slot"]:
                b["zloto_leg"] += self.stawkaB(b) * dt
                if b["martwy"] is None and self.w_legowisku(b):
                    b["zloto"] += b["zloto_leg"]
                    b["zloto_leg"] = 0.0
            # walka1: życie z formy (pełne po zmianie formy / odrodzeniu), regeneracja bez ran
            if not b.get("boss"):
                hm = self.zycm(b)
                if b["zycm"] != hm:
                    b["zyc"], b["zycm"] = hm, hm
                elif b["martwy"] is None and b["zyc"] < hm and self.czas - b["ost_r"] > D["walka"]["regen_po_s"]:
                    b["zyc"] = min(hm, b["zyc"] + hm * D["walka"]["regen_na_s"] * dt)
            r = self.r(b)
            if b["martwy"] is not None:
                if self.czas >= b["martwy"]:
                    if b["slot"]:
                        b["forma"] = max(1, b["forma"] - 1)
                        b["wzrost"] = self.potrzeba(b["forma"]) * D["smierc"]["pasek_po"]
                        b["tarcza"] = self.czas + D["smierc"]["tarcza_s"]
                    else:
                        b["tarcza"] = self.czas + 1
                    b["martwy"], b["ogl"] = None, 0.0
                    if b.get("boss"):
                        b["hp"] = D["boss"]["stopnie_hp"][self.boss_st - 1]
                        b["x"], b["z"] = b["dom"]
                        continue
                    b["x"], b["z"] = self.bezpieczne(b["forma"], b["slot"] > 0, b["strefa"])
                    if b["slot"]:
                        self.strefy.append((b["x"], b["z"], self.czas + D["boty"]["strefa_startu_s"]))
            elif b["kokon"] is not None:
                if self.czas >= b["kokon"]:
                    p = self.potrzeba(b["forma"])
                    b["forma"] += 1
                    b["kokon"] = None
                    if b["forma"] > b["max"]:
                        b["max"] = b["forma"]
                        if b["slot"]:
                            self.zdarzenia.append(("forma", b["forma"]))
                            if b["forma"] == D["las"]["od_formy"]:
                                self.zdarzenia.append(("las", 0))
                    b["wzrost"] = min(max(0, b["wzrost"] - p), self.potrzeba(b["forma"]) * D["ewolucja"]["nadmiar"]) if b["forma"] < len(D["formy"]) else 0
                    b["tarcza"] = max(b["tarcza"], self.czas + D["ewolucja"]["tarcza_po_s"])
                    w = b.get("kokon_w")
                    if w and self.wx(w) > self.wx(b["warianty"].get(b["forma"])):
                        b["warianty"][b["forma"]] = w
                    b["um_ok"] = 0.0
            elif b["skok"] is not None:
                x0, z0, x1, z1, t0, t1, kr = b["skok"]
                f = min(1, max(0, (self.czas - t0) / (t1 - t0)))
                b["x"], b["z"] = x0 + (x1 - x0) * f, z0 + (z1 - z0) * f
                if f >= 1:
                    b["skok"] = None
                    n = 0
                    for q in self.byty:
                        if q is not b and self.bezbronny(q) and self.moze(b, q) and n < 3 and dlug(q["x"] - b["x"], q["z"] - b["z"]) < r + kr + self.r(q) * 0.5:
                            self.rana(b, q, self.obrazenia(b) * 8)
                            n += 1
                    self.oglusz(b, r + kr + 4, 1.0)
                    if self.boss_w(b, kr + 2):
                        self.ran(self.boss, b, D["boss"]["um_obrazenia"])
                    for i in self.kulki_w(b["x"], b["z"], r + kr, 99):
                        self.zjedz_kulke(b, i)
            elif b["ogl"] > self.czas:
                b["vx"] *= 0.8
                b["vz"] *= 0.8
            else:
                if b.get("boss"):
                    if self.czas >= b["mysl"]:
                        self.mysl_bossa(b)
                    if self.czas - b["ost_rana"] > D["boss"]["regen_po_s"]:
                        b["hp"] = min(D["boss"]["hp"], b["hp"] + D["boss"]["hp"] * D["boss"]["regen_na_s"] * dt)
                elif not b["slot"] and self.czas >= b["mysl"]:
                    self.mysl(b)
                m = 1.0
                if self.czas < b["zryw"]:
                    m = D["ruch"]["zryw_v"]
                if self.czas < b["szarza"]:
                    m = max(m, b["szarza_v"])
                v = self.v(b) * m
                a = min(1, D["ruch"]["przyspieszenie"] * dt * (3 if m > 1 else 1))
                b["vx"] += (b["wx"] * v - b["vx"]) * a
                b["vz"] += (b["wz"] * v - b["vz"]) * a
                b["x"] += b["vx"] * dt
                b["z"] += b["vz"] * dt
                if b["wx"] or b["wz"]:
                    b["kier"] = math.atan2(b["wx"], b["wz"])
                b["x"], b["z"] = self.ogranicz(b["x"], b["z"], r, self.maska(b))
                if not b["slot"]:
                    for (px, pz) in D["legowiska"]:
                        d = dlug(b["x"] - px, b["z"] - pz)
                        mn = D["legowisko"]["r"] + r * 0.7
                        if 0.01 < d < mn:
                            b["x"], b["z"] = px + (b["x"] - px) / d * mn, pz + (b["z"] - pz) / d * mn
                if b.get("boss"):
                    q = next((x for x in self.byty if x["id"] == b["cel"]), None) if b["cel"] else None
                    B = D["boss"]
                    if q and self.czas >= b["gryz_ok"] and self.bezbronny(q) and dlug(q["x"] - b["x"], q["z"] - b["z"]) < r + B["zasieg"] + self.r(q):
                        b["gryz_ok"] = self.czas + B["przerwa_s"] + (B.get("zamach_s") or 0)
                        d = max(0.1, dlug(q["x"] - b["x"], q["z"] - b["z"]))
                        nx, nz = (q["x"] - b["x"]) / d, (q["z"] - b["z"]) / d
                        q["x"], q["z"] = self.ogranicz(q["x"] + nx * 5, q["z"] + nz * 5, self.r(q), self.maska(q))
                        q["vx"], q["vz"] = nx * B["odrzut"], nz * B["odrzut"]
                        q["ogl"] = self.czas + B["ogluszenie_s"]
                        self.rana(b, q, B["stopnie_gryz"][self.boss_st - 1], False)
                elif (not b["slot"] or self.czas < b["szarza"]) and self.czas >= b["gryz_ok"]:
                    q = self.ofiara(b, self.zasieg(b) if not b["slot"] else 2)
                    boss = None if q or not b["slot"] else self.boss_w(b, 2)
                    if q or boss:
                        self.cios(b, q or boss)
        n = len(self.byty)
        for i in range(n):
            a = self.byty[i]
            for j in range(i + 1, n):
                b = self.byty[j]
                if not (self.wolny(a) and self.wolny(b)):
                    continue
                ra, rb = self.r(a), self.r(b)
                dx, dz = b["x"] - a["x"], b["z"] - a["z"]
                d = dlug(dx, dz)
                if d >= ra + rb:
                    continue
                duzy, maly, rd, rm = (b, a, rb, ra) if b["forma"] > a["forma"] else (a, b, ra, rb)
                moze = (self.moze(duzy, maly) and not self.przypadkiem(duzy, maly) and not (maly["slot"] and self.w_legowisku(maly))
                        and not (duzy["slot"] and self.w_legowisku(duzy)))
                if True:  # walka1: bez połykania dotykiem

                    nx, nz = (dx / d, dz / d) if d > 0.01 else (1, 0)
                    w = ra + rb - d
                    wa = 0.25 if a["forma"] > b["forma"] else (0.75 if a["forma"] < b["forma"] else 0.5)
                    a["x"] -= nx * w * wa
                    a["z"] -= nz * w * wa
                    b["x"] += nx * w * (1 - wa)
                    b["z"] += nz * w * (1 - wa)
        zz = D["jedzenie"]["zasieg_zbierania"]
        for b in self.byty:
            if self.wolny(b) and (b["slot"] or b["forma"] <= D["boty"]["kulki_do"]):
                g = self.r(b) + 1.65 + zz
                for i in self.kulki_w(b["x"], b["z"], g, 99):
                    p = D["kulkiPoz"][i]
                    kr = D["jedzenie"]["wielka_r"] if p[2] == 3 else (D["jedzenie"]["duza_r"] if p[2] == 2 else D["jedzenie"]["mala_r"])
                    if dlug(p[0] - b["x"], p[1] - b["z"]) < self.r(b) + kr + zz:
                        self.zjedz_kulke(b, i)
        for i in range(len(self.kulki)):
            if self.kulki[i] and self.czas >= self.kulki[i]:
                self.kulki[i] = 0.0


def gracz_mysl(S, g, styl):
    """Polityka „sprawnego gracza” (styl='sprawny') albo średniego."""
    D = S.D
    if S.ster_serwer(g):
        return
    widzi = 46 if styl == "sprawny" else 30
    r = S.r(g)
    zagr, dz = None, 1e9
    best, bw = None, 0.0
    for q in S.byty:
        if q is g or q["martwy"] is not None:
            continue
        d = dlug(q["x"] - g["x"], q["z"] - g["z"])
        if S.moze(q, g) and S.wolny(q) and d < S.r(q) + r + (18 if styl == "sprawny" else 10) and d < dz:
            zagr, dz = q, d
        elif S.moze(g, q) and S.bezbronny(q) and d < widzi:
            w = S.wartosc(q) / (d + 6)
            if w > bw:
                best, bw = q, w
    if zagr and g["tarcza"] <= S.czas:
        d = max(0.1, dz)
        ux, uz = (g["x"] - zagr["x"]) / d, (g["z"] - zagr["z"]) / d
        dc = dlug(g["x"], g["z"])
        if dc > D["pole"]["r"] - 25:
            ux, uz = ux - g["x"] / dc * 0.8, uz - g["z"] / dc * 0.8
        n = max(0.01, dlug(ux, uz))
        g["wx"], g["wz"] = ux / n, uz / n
        if dz < S.r(zagr) + r + 4:
            S.zryw(g)
            if D["formy"][g["forma"] - 1]["um"]["typ"] in ("ogluszenie", "fala", "skok", "podmuch"):
                S.umiejetnosc(g)
        if not g.get("zagr_t"):
            g["zagr_t"] = S.czas
        return
    # kulki w pobliżu: wartość / odległość
    J = D["jedzenie"]
    for i in S.kulki_w(g["x"], g["z"], 30, 6):
        p = D["kulkiPoz"][i]
        if S.maska(g) == 1 and S.w_lesie(p[0], p[1]):
            continue  # las zamknięty: kulki za płotem się nie liczą
        d = dlug(p[0] - g["x"], p[1] - g["z"])
        w = (J["wielka"] if p[2] == 3 else (J["duza"] if p[2] == 2 else J["mala"])) / (d + 6)
        if w > bw:
            best, bw = ("kulka", p), w
    # owce: wartość wzrostu / odległość; dotyk zjada
    for o in S.owce:
        if o["do"] <= S.czas:
            d = dlug(o["x"] - g["x"], o["z"] - g["z"])
            if d < r + 1.6:
                S.wzrost(g, S.owce_wzrost * S.apetyt(g))
                S.zadanie(g, "owce")
                o["do"] = S.czas + S.owce_powrot
                continue
            if d < 34:
                w = S.owce_wzrost / (d + 6)
                if w > bw:
                    best, bw = ("owca", (o["x"], o["z"])), w
    # mini-boss: sprawny gracz walczy od formy 4 (gryzie, po ugryzieniu bossa odskakuje zrywem)
    boss = getattr(S, "boss", None)
    if styl == "sprawny" and boss and boss["martwy"] is None and g["forma"] >= 3 + S.boss_st:
        db = dlug(boss["x"] - g["x"], boss["z"] - g["z"])
        if db < 70 and not g.get("boss_widziany"):
            g["boss_widziany"] = S.czas
        if bw < 2.5:
            d = max(0.1, db)
            g["wx"], g["wz"] = (boss["x"] - g["x"]) / d, (boss["z"] - g["z"]) / d
            if S.boss_w(g, S.zasieg(g)):
                S.gryz(g)
                S.umiejetnosc(g)
            return
    # legowisko: gdy złota (zebranego + w legowisku) starczy na najtańszy zakup — po złoto (i zakup na miejscu)
    if g.get("do_domu") and best is None or g.get("do_domu") and isinstance(best, tuple):
        x, z = S.leg(g)
        d = max(0.1, dlug(x - g["x"], z - g["z"]))
        g["wx"], g["wz"] = (x - g["x"]) / d, (z - g["z"]) / d
        return
    # las: od formy 4 sprawny gracz idzie tam, gdy w pobliżu nie ma nic lepszego
    if (best is None or isinstance(best, tuple)) and g["forma"] >= D["las"]["od_formy"] and S.maska(g) == 3 and not S.w_lesie(g["x"], g["z"]):
        tx, tz = D["las"]["x"], D["las"]["z"]
        d = max(0.1, dlug(tx - g["x"], tz - g["z"]))
        g["wx"], g["wz"] = (tx - g["x"]) / d, (tz - g["z"]) / d
        return
    if best is None:
        if g["wx"] == 0 and g["wz"] == 0 or S.los.random() < 0.05:
            a = S.los.random() * 2 * math.pi
            g["wx"], g["wz"] = math.sin(a) - g["x"] / D["pole"]["r"], math.cos(a) - g["z"] / D["pole"]["r"]
        return
    if isinstance(best, tuple):
        tx, tz = best[1][0], best[1][1]
    else:
        tx, tz = best["x"], best["z"]
    d = max(0.1, dlug(tx - g["x"], tz - g["z"]))
    g["wx"], g["wz"] = (tx - g["x"]) / d, (tz - g["z"]) / d
    A = D["formy"][g["forma"] - 1]["um"]
    if not isinstance(best, tuple):
        if d < r + S.zasieg(g) + S.r(best) * 0.5:
            S.gryz(g)
        elif d < r + S.r(best) + 10 and styl == "sprawny":
            S.zryw(g)
        if A["typ"] in ("jezyk", "oddech") and d < r + A["r"]:
            S.umiejetnosc(g)
        elif A["typ"] == "szarza" and d < 18:
            S.umiejetnosc(g)
        elif A["typ"] == "skok" and d < A["d"] + 2:
            S.umiejetnosc(g)
        elif A["typ"] in ("ogluszenie", "fala", "podmuch") and d < r + A["r"]:
            S.umiejetnosc(g)
    else:
        if A["typ"] in ("wsysanie", "fala") and len(S.kulki_w(g["x"], g["z"], r + A.get("r", 0), 5)) >= 3:
            S.umiejetnosc(g)
        elif A["typ"] in ("jezyk", "oddech") and len(S.kulki_w(g["x"], g["z"], r + A["r"], 5)) >= 3:
            S.umiejetnosc(g)
        if d < r + S.zasieg(g) + 1:
            S.gryz(g)


def przebieg(D, ziarno, minut, styl):
    los = random.Random(ziarno)
    S = Swiat(D, los)
    S.zdarzenia = []
    for f, ile in enumerate(D["boty"]["formy"], 1):
        for _ in range(ile):
            S.dodaj(0, f)
    for f, ile in enumerate(D["boty"]["las_formy"], 1):
        for _ in range(ile):
            S.dodaj(0, f, 2)
    S.dodaj_bossa()
    g = S.dodaj(1, 1)
    dt = 0.1
    wyn = {"forma": {1: 0.0}, "ulepszenie": None, "zagrozenie": None, "smierci": 0, "zakupy": [], "polowy": {}, "las": None, "boss_rana": None,
           "boss_pokonany": None}
    nast_mysl = 0.0
    rozpr = 0.0
    while S.czas < minut * 60:
        S.zdarzenia = []
        if S.czas >= nast_mysl:
            nast_mysl = S.czas + (0.2 if styl == "sprawny" else 0.35)
            if styl == "sredni" and S.czas >= rozpr and los.random() < 0.02:
                rozpr = S.czas + 4  # rozproszenie: chwilę idzie prosto
            if S.czas >= rozpr:
                gracz_mysl(S, g, styl)
            if g["forma"] < len(D["formy"]) and g["wzrost"] >= S.potrzeba(g["forma"]):
                S.ewoluuj(g)
            # najtańszy zakup: ulepszenie (wszędzie) albo poziom trofeum (w legowisku); po złoto do legowiska
            ceny = sorted((u["ceny"][g["pz"][u["id"]] - 1], u["id"]) for u in D["ulepszenia"] if g["pz"][u["id"]] <= len(u["ceny"]))
            tro = sorted((S.cena_trofeum(g, f), f) for f in range(1, g["max"] + 1) if S.cena_trofeum(g, f)) if wyn["ulepszenie"] else []
            najt = min([c for c, _ in ceny[:1]] + [c for c, _ in tro[:1]] or [1e18])
            # odczucie1 (wariant TEMPO_TROFEA=pelne / przy_zlocie): do legowiska także, gdy najtańszy jest poziom trofeum
            # (kupowany tylko w legowisku); w grze tej podpowiedzi nie ma — trofeum kupuje się przy drodze po złoto
            tro_tani = bool(tro) and (not ceny or tro[0][0] < ceny[0][0]) and tro[0][0] <= g["zloto"] + g["zloto_leg"]
            if TROFEA_DOM == "brak":
                tro_tani = False
            elif TROFEA_DOM == "przy_zlocie":
                tro_tani = tro_tani and tro[0][0] <= g["zloto"]
            g["do_domu"] = ((g["zloto"] < najt <= g["zloto"] + g["zloto_leg"]) or (tro_tani and not S.w_legowisku(g))) and g["forma"] < len(D["formy"])
            if ceny and g["zloto"] >= ceny[0][0] and S.kup(g, ceny[0][1]):
                wyn["zakupy"].append((round(S.czas), ceny[0][1]))
                if wyn["ulepszenie"] is None:
                    wyn["ulepszenie"] = S.czas
            elif tro and S.w_legowisku(g) and g["zloto"] >= tro[0][0]:
                g["zloto"] -= tro[0][0]
                g["trofea"][tro[0][1]] = g["trofea"].get(tro[0][1], 1) + 1
                wyn["zakupy"].append((round(S.czas), "trofeum%d" % tro[0][1]))
        S.krok(dt)
        # odczucie1: połowa paska do następnego stadium (baner „HALFWAY to …” z zapowiedzią zdolności) — mały cel
        if 2 <= g["forma"] < len(D["formy"]) and g["forma"] not in wyn["polowy"] and g["wzrost"] >= 0.5 * S.potrzeba(g["forma"]):
            wyn["polowy"][g["forma"]] = S.czas
        for z in S.zdarzenia:
            if z[0] == "forma" and z[1] not in wyn["forma"]:
                wyn["forma"][z[1]] = S.czas
            elif z[0] == "smierc":
                wyn["smierci"] += 1
            elif z[0] == "zadanie":
                wyn.setdefault("zadania", []).append(S.czas)
            elif z[0] in ("las", "boss_rana", "boss_pokonany") and wyn[z[0]] is None:
                wyn[z[0]] = S.czas
            elif z[0] == "boss_stopien":
                wyn.setdefault("stopnie", {})[z[1]] = S.czas
        if wyn["zagrozenie"] is None and getattr(S, "poscig", None) is not None:
            wyn["zagrozenie"] = S.poscig
        if g["forma"] == len(D["formy"]) and g["max"] == len(D["formy"]) and minut * 60 - S.czas > 60:
            pass
    wyn["boss_widziany"] = g.get("boss_widziany")
    # najdłuższa przerwa bez czegoś nowego (forma, las, boss widziany, boss pokonany, zadanie dnia, zakup: ulepszenie albo
    # poziom trofeum — małe cele odczucie1) w pierwszych 10 min
    nowe = sorted([0.0, 600.0] + [t for t in list(wyn["forma"].values()) + [wyn["las"], wyn["boss_widziany"], wyn["boss_pokonany"]]
                                  + list(wyn.get("stopnie", {}).values()) + wyn.get("zadania", []) + [float(t) for t, _ in wyn["zakupy"]]
                                  + (list(wyn["polowy"].values()) if POLOWA else [])
                                  if t is not None and t <= 600])
    wyn["przerwa"] = max(b - a for a, b in zip(nowe, nowe[1:]))
    bez = sorted(set(nowe) - set(wyn["polowy"].values()) | {0.0, 600.0})
    wyn["przerwa_bez_polowy"] = max(b - a for a, b in zip(bez, bez[1:]))
    wyn["koniec_forma"] = g["max"]
    wyn["zloto"] = round(g["zloto"])
    return wyn


def mmss(t):
    if t is None:
        return "—"
    return "%d:%02d" % (int(t // 60), int(t % 60))


def main():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--prob", type=int, default=6)
    ap.add_argument("--minut", type=float, default=18)
    ap.add_argument("--gracz", default="sprawny", choices=["sprawny", "sredni"])
    a = ap.parse_args()
    D = DN.dane()
    wyniki = [przebieg(D, 100 + i, a.minut, a.gracz) for i in range(a.prob)]
    nf = len(D["formy"])

    def med(lista):
        lista = [x for x in lista if x is not None]
        return statistics.median(lista) if len(lista) * 2 > len(wyniki) else None

    print("Tempo (%s gracz, %d prób, %g min): mediana [najszybszy–najwolniejszy]" % (a.gracz, a.prob, a.minut))
    cele = {2: (20, 30), 3: (0, 90), 5: (360, 420), nf: (780, 1020)}
    ok = True
    for f in range(2, nf + 1):
        t = [w["forma"].get(f) for w in wyniki]
        m = med(t)
        tt = [x for x in t if x is not None]
        cel = cele.get(f)
        spel = None if cel is None else (m is not None and cel[0] <= m <= cel[1])
        if spel is False:
            ok = False
        print("  forma %d %-13s %6s  [%s–%s]%s%s" % (f, D["formy"][f - 1]["nazwa"], mmss(m), mmss(min(tt) if tt else None), mmss(max(tt) if tt else None),
                                                   "  doszło %d/%d" % (len(tt), len(t)) if len(tt) < len(t) else "",
                                                   "" if cel is None else ("  cel %s–%s %s" % (mmss(cel[0]), mmss(cel[1]), "OK" if spel else "NIE"))))
    u = med([w["ulepszenie"] for w in wyniki])
    spel = u is not None and 90 <= u <= 120
    ok = ok and spel
    print("  1. ulepszenie       %6s  cel 1:30–2:00 %s" % (mmss(u), "OK" if spel else "NIE"))
    z = med([w["zagrozenie"] for w in wyniki])
    spel = z is not None and z >= 110
    ok = ok and spel
    print("  1. pościg bota      %6s  cel ≥ 1:50 %s" % (mmss(z), "OK" if spel else "NIE"))
    for k, n in (("las", "DEEP WOODS otwarty"), ("boss_widziany", "boss spotkany"), ("boss_pokonany", "boss pokonany")):
        print("  %-19s %6s" % (n, mmss(med([w[k] for w in wyniki]))))
    for st in range(2, 6):
        print("  boss stopień %d      %6s" % (st, mmss(med([w.get("stopnie", {}).get(st) for w in wyniki]))))
    prz = statistics.median([w["przerwa"] for w in wyniki])
    spel = prz <= 150
    ok = ok and spel
    print("  najdłuższa przerwa bez nowości (0–10 min) %s  [%s–%s]  cel ≤ 2:30 %s" % (mmss(prz), mmss(min(w["przerwa"] for w in wyniki)),
                                                                                mmss(max(w["przerwa"] for w in wyniki)), "OK" if spel else "NIE"))
    print("  (bez banera połowy paska: %s; trofea: %s)" % (mmss(statistics.median([w["przerwa_bez_polowy"] for w in wyniki])), TROFEA_DOM))
    print("  śmierci (mediana)   %6s" % statistics.median([w["smierci"] for w in wyniki]))
    print("  zakupy (próba 1):   %s" % ", ".join("%s %s" % (mmss(t), i) for t, i in wyniki[0]["zakupy"]))
    print("  złoto na końcu (mediana): %d" % statistics.median([w["zloto"] for w in wyniki]))
    print("WYNIK:", "cele tempa spełnione" if ok else "cele tempa NIE wszystkie spełnione")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
