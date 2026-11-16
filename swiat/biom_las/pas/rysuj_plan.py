#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plansza „Las jako wąski pas” z lotu ptaka — rysuje plan_pasa.png z plan_pasa.json (Pillow, bez Blendera).

    python -B swiat/biom_las/pas/rysuj_plan.py [--wyj swiat/biom_las/pas/plan_pasa.png] [--szer 1600]

Pas jest narysowany pionowo: na dole przybycie z miasteczka, u góry brama do Bagna (jak strzałka „w górę” na mapie
stref z HUD). Kolorowe przegrody, kojce, pętle potworów ze znaczkami i poziomami, domy, punkty orientacyjne, przejścia,
trasa przelotu kamery (czasy i wysokości w prawych kulisach), linijka w sekundach biegu i studach (lewe kulisy), a pod
spodem szerokość pasa, świat w jednej linii (miasteczko → 8 biomów) i legenda. Rysujemy w podwójnej rozdzielczości i
zmniejszamy (gładkie krawędzie). Wszystkie napisy ≥ 22 px przy szerokości 1600.
"""
import argparse
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
sys.dont_write_bytecode = True
import sprawdz_plan as SP  # noqa: E402  (krzywa kamery i wzór `cel` — jedna kopia)

K = 2               # nadpróbkowanie
S = 3.0             # px na stud (przy szerokości 1600)
BIEG = 16.0

POTWOR = {  # litera, kolor (jak swiat/biom_las/plan.py)
    "Leśny Slime": ("S", (46, 170, 60)),
    "Muchomornik": ("M", (214, 52, 42)),
    "Cierniowy Wilk": ("W", (104, 72, 160)),
    "Leśny Troll": ("T", (130, 82, 40)),
    "Strażnik Gaju": ("G", (20, 140, 125)),
}
TUSZ = (29, 25, 22)
TLO = (248, 244, 232)
KULISY = (54, 104, 62)
KULISY_CIEMNE = (38, 80, 46)
TYL = (96, 102, 88)
SCIEZKA = (226, 204, 152)
WODA = (70, 155, 220)
KAMERA = (240, 120, 20)
SZARY = (110, 110, 110)
BIOMY_KOLOR = {"las": (96, 170, 80), "bagno": (112, 132, 78), "dzungla": (36, 140, 66), "pustynia": (232, 198, 118),
               "gory": (158, 168, 182), "lodowiec": (170, 214, 238), "wulkan": (204, 84, 52), "krysztal": (168, 120, 220)}


def czcionka(rozmiar, gruba=False, kursywa=False):
    if gruba:
        kand = ["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]
    elif kursywa:
        kand = ["segoeuii.ttf", "ariali.ttf", "DejaVuSans-Oblique.ttf"]
    else:
        kand = ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"]
    for n in kand:
        for d in (r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu", "/Library/Fonts", ""):
            p = os.path.join(d, n) if d else n
            try:
                return ImageFont.truetype(p, int(rozmiar * K))
            except OSError:
                continue
    return ImageFont.load_default()


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def ciemniej(c, f=0.55):
    return tuple(int(x * f) for x in c)


def l1(x):
    return ("%.1f" % x).replace(".", ",")


class Plansza:
    def __init__(self, plan, szer):
        self.p = plan
        self.W = szer
        pas = plan["pas"]
        self.pol = pas["szerokosc"] / 2
        self.kul = pas["kulisy"]
        self.u_od, self.u_do = pas["u_od"], pas["u_do"]
        self.CX = 800 * szer / 1600
        self.GORA = 330                      # y (px) punktu u = u_do
        self.dol_pasa = self.y(self.u_od)
        self.H = int(self.dol_pasa + 1400)   # zapas; po narysowaniu przycinamy
        self.img = Image.new("RGB", (int(self.W * K), int(self.H * K)), TLO)
        self.d = ImageDraw.Draw(self.img)
        self.lewa = []    # zajęte przedziały y w kolumnach napisów
        self.prawa = []

    # ------------------------------------------------------------------ układ
    def y(self, u):
        return self.GORA + (self.u_do - u) * S

    def x(self, v):
        return self.CX + v * S

    def xy(self, u, v):
        return (self.x(v), self.y(u))

    @property
    def x_pasa(self):
        return self.x(-self.pol - self.kul), self.x(self.pol + self.kul)

    # ------------------------------------------------------------------ prymitywy (px końcowe → ×K)
    def _k(self, pts):
        return [(a * K, b * K) for a, b in pts]

    def prost(self, x0, y0, x1, y1, fill=None, outline=None, w=1, r=0):
        box = [min(x0, x1) * K, min(y0, y1) * K, max(x0, x1) * K, max(y0, y1) * K]
        if r:
            self.d.rounded_rectangle(box, radius=r * K, fill=fill, outline=outline, width=int(w * K))
        else:
            self.d.rectangle(box, fill=fill, outline=outline, width=int(w * K))

    def kolo(self, x, y, r, fill=None, outline=None, w=1):
        self.d.ellipse([(x - r) * K, (y - r) * K, (x + r) * K, (y + r) * K], fill=fill, outline=outline,
                       width=int(w * K))

    def linia(self, pts, fill, w=1):
        self.d.line(self._k(pts), fill=fill, width=max(1, int(w * K)), joint="curve")

    def kreski(self, pts, fill, w=1, dl=8, przerwa=6):
        for a, b in zip(pts, pts[1:]):
            d = math.dist(a, b)
            if d == 0:
                continue
            n = d / (dl + przerwa)
            i = 0.0
            while i < n:
                f0 = i * (dl + przerwa) / d
                f1 = min(1.0, (i * (dl + przerwa) + dl) / d)
                self.linia([(a[0] + (b[0] - a[0]) * f0, a[1] + (b[1] - a[1]) * f0),
                            (a[0] + (b[0] - a[0]) * f1, a[1] + (b[1] - a[1]) * f1)], fill, w)
                i += 1

    def wielokat(self, pts, fill=None, outline=None, w=1):
        self.d.polygon(self._k(pts), fill=fill, outline=outline, width=int(w * K) if outline else 0)

    def tekst(self, x, y, s, f, kolor=TUSZ, kotwica="la", obrys=None):
        if obrys:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx or dy:
                        self.d.text((x * K + dx * K, y * K + dy * K), s, font=f, fill=obrys, anchor=kotwica)
        self.d.text((x * K, y * K), s, font=f, fill=kolor, anchor=kotwica)

    def szer_tekstu(self, s, f):
        b = self.d.textbbox((0, 0), s, font=f)
        return (b[2] - b[0]) / K

    # ------------------------------------------------------------------ kolumny napisów bez nakładania
    def miejsce(self, kolumna, y_cel, h, odstep=8):
        y0 = y_cel - h / 2
        for krok in range(0, 1200, 2):
            for kand in (y0 + krok, y0 - krok):
                if all(kand + h + odstep <= a or kand >= b + odstep for a, b in kolumna):
                    kolumna.append((kand, kand + h))
                    return kand
        kolumna.append((y0, y0 + h))
        return y0

    def blok(self, strona, y_cel, linie, x_cel=None, kolor_linii=SZARY):
        """Blok napisów w lewej albo prawej kolumnie, z odnośnikiem do (x_cel, y_cel), gdy blok odjechał."""
        h = sum(l[2] for l in linie)
        xl, xp = self.x_pasa
        if strona == "lewa":
            y0 = self.miejsce(self.lewa, y_cel, h)
            xk = xl - 18
            for s, f, wys, kol in linie:
                self.tekst(xk, y0, s, f, kol, "ra")
                y0 += wys
            krawedz = xl - 4
            xt = xk + 6
        else:
            y0 = self.miejsce(self.prawa, y_cel, h)
            xk = xp + 18
            for s, f, wys, kol in linie:
                self.tekst(xk, y0, s, f, kol, "la")
                y0 += wys
            krawedz = xp + 4
            xt = xk - 6
        srodek = y0 - h / 2
        if abs(srodek - y_cel) > 12:
            self.linia([(xt, srodek), (krawedz, y_cel)], kolor_linii, 1.5)
            self.kolo(krawedz, y_cel, 3.5, fill=kolor_linii)
        return srodek

    # ================================================================== rysowanie
    def rysuj(self):
        p = self.p
        self.naglowek()
        self.pas_tlo()
        self.przegrody()
        self.przejscia()
        self.sciezka()
        self.strefy_tlo()
        self.arena()
        self.znaki()
        self.miejsca()
        self.kamera()
        self.strefy()
        self.straznik()
        self.linijka()
        self.gora_dol()
        y = self.szerokosc_pasa()
        y = self.swiat(y + 40)
        y = self.legenda(y + 30)
        self.H = int(y + 90)
        self.stopka()
        self.img = self.img.crop((0, 0, int(self.W * K), int(self.H * K)))
        return self.img.resize((int(self.W), int(self.H)), Image.LANCZOS)

    def naglowek(self):
        p = self.p
        pas = p["pas"]
        t_prosto = (p["miejsca"][[m["id"] for m in p["miejsca"]].index("brama_bagna")]["u"] - 14) / BIEG
        self.tekst(40, 34, "Las jako wąski pas — plan układu", czcionka(46, True))
        self.tekst(40, 104, "propozycja 16.11.2026 · pas %d × %d st · %s s biegu w poprzek · przybycie → brama %s s"
                   % (pas["szerokosc"], pas["u_do"] - pas["u_od"], l1(pas["szerokosc_s"]), l1(t_prosto)),
                   czcionka(26), (70, 64, 58))
        b = SP.budzet_czasu(p, t_prosto)
        self.tekst(40, 144, "Las ok. %d min gry: walki i farmienie, chodzenie ok. %d%% · do góry = kierunek marszu = "
                   "wschód świata (+X)" % (p["czas"]["cel_min"], round(100 * b["chodzenie_s"] / b["x1_s"])),
                   czcionka(26), (70, 64, 58))
        self.tekst(40, 184, "poziomy potworów to propozycja do uzgodnienia z krzywą doświadczenia · nic tu nie jest kanonem",
                   czcionka(24, kursywa=True), (120, 60, 40))

    def pas_tlo(self):
        xl, xp = self.x_pasa
        y_g, y_d = self.y(self.u_do), self.y(self.u_od)
        # kulisy
        self.prost(xl, y_g, xp, y_d, fill=KULISY)
        # drzewa kulis (kropki, deterministycznie)
        u = self.u_od + 3
        i = 0
        while u < self.u_do - 2:
            for strona in (-1, 1):
                for rzad, v0 in enumerate((self.pol + 6, self.pol + 15)):
                    vv = strona * (v0 + ((i * 7 + rzad * 3) % 5))
                    uu = u + (rzad * 4)
                    if uu < self.u_do - 2:
                        self.kolo(self.x(vv), self.y(uu), 4.2 + (i + rzad) % 3, fill=KULISY_CIEMNE)
            u += 9
            i += 1
        # tył (ściana zamykająca)
        self.prost(self.x(-self.pol), self.y(0), self.x(self.pol), y_d, fill=TYL)
        self.tekst(self.x(-22), self.y(-12) - 13, "ściana", czcionka(22), (230, 230, 220), "mm")
        self.tekst(self.x(-22), self.y(-12) + 14, "zamykająca", czcionka(22), (230, 230, 220), "mm")
        # granica gry
        self.linia([(self.x(-self.pol), y_g), (self.x(-self.pol), self.y(0))], TUSZ, 2)
        self.linia([(self.x(self.pol), y_g), (self.x(self.pol), self.y(0))], TUSZ, 2)

    def przegrody(self):
        for q in self.p["przegrody"]:
            kol = hex_rgb(q["kolor"])
            self.prost(self.x(-self.pol), self.y(q["u_do"]), self.x(self.pol), self.y(q["u_od"]), fill=kol)
            # kojce / polanki: przegródki z przerwą 24 na środku
            for pod in q.get("pod", [])[1:]:
                yy = self.y(pod["u_od"])
                for a, b in ((-self.pol, -12), (12, self.pol)):
                    self.kreski([(self.x(a), yy), (self.x(b), yy)], ciemniej(kol, 0.6), 2, 6, 5)
            # tytuł w lewej kolumnie
            od = max(0.0, (q["u_od"] - 14) / BIEG)
            linie = [(q["nazwa"].upper(), czcionka(29, True), 38, ciemniej(kol, 0.42)),
                     ("u %d–%d · %d st · %s s biegu" % (q["u_od"], q["u_do"], q["u_do"] - q["u_od"],
                                                         l1((q["u_do"] - q["u_od"]) / BIEG)), czcionka(22), 29, TUSZ)]
            if q["id"] != "wejscie":
                linie.append(("od przybycia %s s" % l1(od), czcionka(22), 29, TUSZ))
            poz = self.poziomy_przegrody(q)
            if poz:
                linie.append((poz, czcionka(22, True), 29, TUSZ))
            self.blok("lewa", (self.y(q["u_od"]) + self.y(q["u_do"])) / 2, linie)

    def poziomy_przegrody(self, q):
        if q["id"] == "arena":
            return "boss: poziom %d" % self.p["straznik"]["poziom"]
        sts = [s for s in self.p["strefy"] if s["podbiom"] == q["id"]]
        if not sts:
            return None
        if len(sts) == 1:
            a, b = sts[0]["poziomy"]
            return "poziom %s" % (str(a) if a == b else "%d–%d" % (a, b))
        cz = []
        for s in sts:
            a, b = s["poziomy"]
            cz.append(str(a) if a == b else "%d–%d" % (a, b))
        return "poziomy: " + " → ".join(cz)

    def przejscia(self):
        for t in self.p["przejscia"]:
            y0, y1 = self.y(t["u_do"]), self.y(t["u_od"])
            o1, o2 = t["otwarcie"]
            if t["id"] == "plot_z_furtka":
                yy = self.y((t["u_od"] + t["u_do"]) / 2)
                for a, b in ((-self.pol, o1), (o2, self.pol)):
                    self.linia([(self.x(a), yy), (self.x(b), yy)], (120, 76, 40), 4)
                    v = a
                    while v <= b:
                        self.kolo(self.x(v), yy, 2.6, fill=(90, 56, 30))
                        v += 6
                # furtka otwarta (skrzydło odchylone)
                self.linia([(self.x(o2), yy), (self.x(o2 - 2), yy - 16)], (120, 76, 40), 4)
            elif t["id"] == "strumyk_z_mostkiem":
                w0, w1 = t["woda"]
                self.prost(self.x(-self.pol - self.kul), self.y(w1), self.x(self.pol + self.kul), self.y(w0), fill=WODA)
                m0, m1 = t["mostek"]
                self.prost(self.x(m0), self.y(w1 + 3), self.x(m1), self.y(w0 - 3), fill=(176, 120, 70),
                           outline=TUSZ, w=1.5, r=4)
                for v in t["kamienie"]:
                    for du in (-3, 0, 3):
                        self.kolo(self.x(v + du), self.y((w0 + w1) / 2 + du), 3.2, fill=(150, 150, 150), outline=TUSZ)
            elif t["id"] in ("jezynowe_zwezenie", "kamienny_prog"):
                kol = (124, 70, 140) if t["id"] == "jezynowe_zwezenie" else (128, 124, 116)
                for a, b in ((-self.pol, o1), (o2, self.pol)):
                    self.prost(self.x(a), y0 + 4, self.x(b), y1 - 4, fill=kol, outline=TUSZ, w=1.5, r=10)
            elif t["id"] == "brama_menhirow":
                for v in range(-34, 35, 5):
                    if abs(v) > 18:
                        self.kolo(self.x(v), self.y((t["u_od"] + t["u_do"]) / 2), 2.4, fill=(150, 150, 150))
                for u, v in t["menhiry"]:
                    self.kolo(self.x(v), self.y(u), 7, fill=(92, 98, 112), outline=TUSZ, w=1.5)
            linie = [(t["nazwa"], czcionka(23, True), 30, (60, 54, 48)),
                     (self.opis_przejscia(t), czcionka(22, kursywa=True), 29, (80, 74, 66))]
            self.blok("lewa", (y0 + y1) / 2, linie)

    @staticmethod
    def opis_przejscia(t):
        o = t["otwarcie"][1] - t["otwarcie"][0]
        return {"plot_z_furtka": "furtka %d otwarta, płot 1,2" % o,
                "strumyk_z_mostkiem": "płytka woda, mostek 12",
                "jezynowe_zwezenie": "przejście %d, jeżyny 6 wys." % o,
                "kamienny_prog": "przejście %d, głazy 8–10" % o,
                "brama_menhirow": "przejście %d między menhirami" % o}.get(t["id"], "")

    def sciezka(self):
        pts = self.p["pas"]["sciezka"]["pts"]
        sz = self.p["pas"]["sciezka"]["szer"] / 2
        for a, b in zip(pts, pts[1:]):
            self.prost(self.x(-sz), self.y(b[0]), self.x(sz), self.y(max(a[0], 0)), fill=SCIEZKA)
        # mostek i przejścia przykryły ścieżkę — dorysuj mostek jeszcze raz
        for t in self.p["przejscia"]:
            if t["id"] == "strumyk_z_mostkiem":
                w0, w1 = t["woda"]
                m0, m1 = t["mostek"]
                self.prost(self.x(m0), self.y(w1 + 3), self.x(m1), self.y(w0 - 3), fill=(176, 120, 70),
                           outline=TUSZ, w=1.5, r=4)

    @staticmethod
    def punkt_na_petli(tr, s):
        n = len(tr)
        dl = [0.0]
        for i in range(n):
            dl.append(dl[-1] + math.dist(tr[i], tr[(i + 1) % n]))
        L = dl[-1]
        s %= L
        for i in range(n):
            if s <= dl[i + 1]:
                f = (s - dl[i]) / max(1e-9, dl[i + 1] - dl[i])
                a, b = tr[i], tr[(i + 1) % n]
                return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        return tuple(tr[0])

    def znaczek(self, u, v, litera, kol, r=11):
        x, y = self.xy(u, v)
        self.kolo(x, y, r, fill=kol, outline=TUSZ, w=2)
        self.tekst(x, y + 1, litera, czcionka(r * 1.45, True), (255, 255, 255), "mm")

    def strefy_tlo(self):
        for st in self.p["strefy"]:
            lit, kol = POTWOR[st["potwor"]]
            tr = st["trasa"]
            pts = [self.xy(u, v) for u, v in tr] + [self.xy(*tr[0])]
            self.kreski(pts, kol, 3, 9, 6)
            for u, v in tr:
                self.kolo(*self.xy(u, v), 3.2, fill=kol)
            for u, v in st["dom"]["pts"]:
                x, y = self.xy(u, v)
                self.prost(x - 6, y - 6, x + 6, y + 6, fill=(92, 60, 36), outline=TUSZ, w=1.5)
                self.prost(x - 2.2, y - 1, x + 2.2, y + 6, fill=(30, 22, 16))

    def strefy(self):
        p = self.p
        for st in p["strefy"]:
            lit, kol = POTWOR[st["potwor"]]
            tr = st["trasa"]
            # potwory przy 8 graczach rozłożone po pętli (wataha: członkowie gęsiego)
            n = SP.cel(st["naraz"], st["max"], 8)
            L = st["obwod"]
            gr = st.get("grupa") or {}
            wat = gr.get("watahy", 0) or 0
            poz = []
            if wat > 0:
                miejsc = math.ceil(st["max"] / wat)
                for i in range(n):
                    g, m = i % wat, i // wat
                    poz.append(g * L / wat + 6 - m * max(12.7, 26 / S))
            else:
                poz = [i * L / n + 6 for i in range(n)]
            for s in poz:
                u, v = self.punkt_na_petli(tr, s)
                self.znaczek(u, v, lit, kol, 10 if lit != "T" else 13)
            # poziom w środku pętli
            a, b = st["poziomy"]
            napis = "poz. %s" % (str(a) if a == b else "%d–%d" % (a, b))
            f = czcionka(23, True)
            x, y = self.xy(*st["srodek"])
            w = self.szer_tekstu(napis, f)
            self.prost(x - w / 2 - 7, y - 16, x + w / 2 + 7, y + 16, fill=(255, 255, 255), outline=kol, w=2, r=8)
            self.tekst(x, y + 1, napis, f, ciemniej(kol, 0.7), "mm")
            # karta w prawej kolumnie
            c = [SP.cel(st["naraz"], st["max"], g) for g in (1, 8, 20)]
            nazwa_pod = ""
            for q in p["przegrody"]:
                for pd in q.get("pod", []):
                    if pd["id"] == st.get("pod"):
                        nazwa_pod = pd["nazwa"]
            if st.get("odrodzenie_stale"):
                l2 = "rzadki: 1 naraz, wraca po %d s" % st["odrodzenie_s"]
                l3 = "legowisko pod lewą ścianą"
            else:
                wat_txt = ""
                if wat > 0:
                    wat_txt = " · %d %s" % (wat, "watahy" if wat > 1 else "wataha")
                elif gr.get("samotniki"):
                    wat_txt = " · samotniki"
                l2 = "1 / 8 / 20 graczy: %d / %d / %d%s" % (c[0], c[1], c[2], wat_txt)
                l3 = "odrodzenie %d s · pętla %d st" % (st["odrodzenie_s"], round(st["obwod"]))
            tyt = "%s · %s · %s" % (st["id"].upper(), st["potwor"], napis.replace("poz.", "poziom"))
            linie = [(tyt, czcionka(23, True), 30, ciemniej(kol, 0.75))]
            if nazwa_pod:
                linie.append((nazwa_pod, czcionka(22, kursywa=True), 28, (80, 74, 66)))
            linie += [(l2, czcionka(22), 28, TUSZ), (l3, czcionka(22), 28, TUSZ)]
            self.blok("prawa", self.y(st["srodek"][0]), linie)

    def arena(self):
        a = self.p["straznik"]["arena"]
        x, y = self.xy(*a["srodek"])
        r = a["r"] * S
        self.kolo(x, y, r, fill=(196, 206, 214), outline=(70, 80, 96), w=2)
        for i in range(10):
            ang = 2 * math.pi * i / 10 + 0.3
            self.kolo(x + math.cos(ang) * r, y + math.sin(ang) * r, 5, fill=(92, 98, 112), outline=TUSZ, w=1.2)

    def straznik(self):
        s = self.p["straznik"]
        u, v = s["miejsce"]
        self.znaczek(u, v, "G", POTWOR["Strażnik Gaju"][1], 17)
        # kierunek spojrzenia: w stronę wejścia (w dół planszy)
        gx, gy = self.xy(u, v)
        self.wielokat([(gx - 8, gy + 22), (gx + 8, gy + 22), (gx, gy + 34)], fill=POTWOR["Strażnik Gaju"][1])
        self.tekst(gx - 20, gy - 26, "RYK!", czcionka(24, True), (200, 30, 30), "rm", obrys=(255, 255, 255))
        linie = [("G · Strażnik Gaju · poziom %d" % s["poziom"], czcionka(23, True), 30, (14, 100, 90)),
                 ("boss biomu; stoi twarzą do wejścia", czcionka(22), 28, TUSZ),
                 ("przelot kończy się jego rykiem (2 s)", czcionka(22), 28, TUSZ),
                 ("wraca po %d s (albo osobny dla gracza)" % s["odrodzenie_s"], czcionka(22), 28, TUSZ)]
        self.blok("prawa", gy, linie)

    def znaki(self):
        for z in self.p["punkty_orientacyjne"]:
            x, y = self.xy(z["u"], z["v"])
            if z["id"].startswith("pien"):
                self.kolo(x, y, 6, fill=(110, 70, 40), outline=TUSZ, w=1.5)
                continue
            if z["id"].startswith("menhir"):
                continue
            if z["id"] == "wielki_kapelusz":
                self.kolo(x, y, z["korona"]["r"] * S, fill=(214, 52, 42), outline=TUSZ, w=2)
                for dx, dy in ((-12, -10), (10, -14), (14, 8), (-8, 12), (0, 0)):
                    self.kolo(x + dx, y + dy, 4, fill=(255, 250, 240))
            elif z["id"] == "pasnik":
                self.prost(x - 9, y - 9, x + 9, y + 9, fill=(150, 104, 60), outline=TUSZ, w=1.5)
                self.kolo(x, y, 5, fill=(120, 220, 110))
            elif z["id"] == "wilcza_skala":
                r = z["r"] * S + 4
                self.wielokat([(x, y - r), (x + r * 0.9, y + r * 0.7), (x - r * 0.9, y + r * 0.7)],
                              fill=(84, 88, 104), outline=TUSZ, w=2)
                self.kolo(x - 4, y + 2, 2.5, fill=(250, 180, 40))
                self.kolo(x + 4, y + 2, 2.5, fill=(250, 180, 40))
            elif z["id"] == "glazy_legowiska":
                for dx, dy, rr in ((-8, -4, 11), (9, -6, 9), (0, 9, 10)):
                    self.kolo(x + dx, y + dy, rr, fill=(150, 130, 104), outline=TUSZ, w=1.5)
                self.kolo(x + 18, y + 14, 6, fill=(40, 40, 40))
            elif z["id"] == "filar_krysztal":
                self.wielokat([(x, y - 16), (x + 10, y), (x, y + 16), (x - 10, y)], fill=(80, 230, 140),
                              outline=TUSZ, w=2)
            else:
                self.kolo(x, y, z["r"] * S, fill=(160, 160, 160), outline=TUSZ)
            strona = "prawa" if z["v"] > 0 or z["id"] == "filar_krysztal" else "lewa"
            linie = [(z["nazwa"], czcionka(22, True), 28, (70, 60, 50)),
                     ("punkt orientacyjny, %d wys." % z["wys"], czcionka(22, kursywa=True), 28, (90, 84, 76))]
            self.blok(strona, y, linie)

    def miejsca(self):
        m = {x["id"]: x for x in self.p["miejsca"]}
        # Kamień Powrotu
        k = m["kamien_powrotu"]
        x, y = self.xy(k["u"], k["v"])
        self.wielokat([(x, y - 10), (x + 9, y), (x, y + 10), (x - 9, y)], fill=(150, 150, 160), outline=TUSZ, w=2)
        # jajko
        j = m["jajko"]
        x, y = self.xy(j["u"], j["v"])
        r = j["r"] * S
        self.prost(x - r, y - r, x + r, y + r, fill=(214, 196, 160), outline=TUSZ, w=1.5, r=5)
        self.d.ellipse([(x - 8) * K, (y - 11) * K, (x + 8) * K, (y + 11) * K], fill=(255, 248, 226), outline=TUSZ,
                       width=2 * K)
        self.linia([(x - 7, y), (x + 7, y)], (236, 110, 150), 3)
        # przybycie
        pr = m["przybycie"]
        x, y = self.xy(pr["u"], pr["v"])
        gw = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rr = 14 if i % 2 == 0 else 6
            gw.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
        self.wielokat(gw, fill=(230, 40, 50), outline=TUSZ, w=1.5)
        # brama do Bagna
        b = m["brama_bagna"]
        yy = self.y(b["u"])
        o1, o2 = b["otwarcie"]
        for a, c in ((-self.pol, o1), (o2, self.pol)):
            self.prost(self.x(a), yy - 5, self.x(c), yy + 5, fill=(86, 54, 30), outline=TUSZ, w=1.5)
        self.prost(self.x(o1), yy - 4, self.x(o2), yy + 4, fill=(210, 40, 40), outline=TUSZ, w=1.5)
        # kłódka
        lx, ly = self.x(0), yy
        self.prost(lx - 7, ly - 2, lx + 7, ly + 9, fill=(250, 200, 60), outline=TUSZ, w=1.5, r=2)
        self.d.arc([(lx - 5) * K, (ly - 10) * K, (lx + 5) * K, (ly + 2) * K], 180, 360, fill=TUSZ, width=2 * K)
        # napisy (prawa kolumna)
        t_j = math.dist((pr["u"], pr["v"]), (j["u"], j["v"])) / BIEG
        t_k = math.dist((pr["u"], pr["v"]), (k["u"], k["v"])) / BIEG
        self.blok("prawa", self.y(pr["u"]), [
            ("Przybycie z miasteczka", czcionka(23, True), 30, (180, 30, 40)),
            ("teleport; tu start przelotu kamery", czcionka(22), 28, TUSZ)])
        self.blok("prawa", self.y(j["u"]), [
            ("Stanowisko jajka (farbowanie)", czcionka(23, True), 30, (130, 90, 40)),
            ("tylko miejsce · %s s od przybycia" % l1(t_j), czcionka(22), 28, TUSZ)])
        self.blok("prawa", self.y(k["u"]) + 30, [
            ("Kamień Powrotu → miasteczko", czcionka(23, True), 30, (90, 90, 100)),
            ("E · %s s od przybycia · lewa strona" % l1(t_k), czcionka(22), 28, TUSZ)])
        self.blok("prawa", yy, [
            ("Brama do Bagna", czcionka(23, True), 30, (150, 30, 30)),
            ("zamknięta, póki gracz nie pokona", czcionka(22), 28, TUSZ),
            ("Strażnika (osobno dla gracza)", czcionka(22), 28, TUSZ)])

    def kamera(self):
        k = self.p["przelot_kamery"]
        probki = SP.krzywa_kamery(k["punkty"], 0.02)
        pts = [self.xy(u, v) for _, u, v, _ in probki]
        # obwódka, żeby linia była widoczna na każdym tle
        self.kreski(pts, (255, 255, 255), 6, 10, 6)
        self.kreski(pts, KAMERA, 3.5, 10, 6)
        _, xp = self.x_pasa
        xk = xp - self.kul * S / 2
        f = czcionka(22, True)
        f2 = czcionka(22)
        widziane = set()
        for i, x in enumerate(k["punkty"]):
            u, v, h = x["poz"]
            key = (u, v, h)
            px, py = self.xy(u, v)
            self.kolo(px, py, 6, fill=KAMERA, outline=(255, 255, 255), w=2)
            if key in widziane:
                continue
            widziane.add(key)
            nast = k["punkty"][i + 1] if i + 1 < len(k["punkty"]) else None
            if nast and nast["poz"] == x["poz"]:
                linie = ["%s s" % l1(x["t"]), "STOP", "%s s" % l1(nast["t"])]
            else:
                linie = ["%s s" % l1(x["t"]), "%d st" % h]
            yy = py - 14 * len(linie)
            for j, s in enumerate(linie):
                self.tekst(xk, yy + j * 27, s, f if j == 0 else f2, (255, 214, 150) if j == 0 else (255, 255, 255),
                           "ma", obrys=(30, 50, 34))

    def linijka(self):
        """Lewe kulisy: kreska co 5 s biegu od przybycia (80 st)."""
        xl, _ = self.x_pasa
        xk = xl + self.kul * S / 2
        u0 = 14
        k = 1
        while u0 + 80 * k <= self.u_do - 10:
            u = u0 + 80 * k
            y = self.y(u)
            self.linia([(xl, y), (xl + 14, y)], (255, 255, 255), 2.5)
            self.linia([(self.x(-self.pol) - 10, y), (self.x(-self.pol), y)], (255, 255, 255), 2.5)
            self.tekst(xk, y - 27, "%d s" % (5 * k), czcionka(22, True), (255, 240, 170), "ma", obrys=(30, 50, 34))
            self.tekst(xk, y + 2, "%d st" % (80 * k), czcionka(22), (255, 255, 255), "ma", obrys=(30, 50, 34))
            k += 1
        y = self.y(u0)
        self.linia([(xl, y), (self.x(-self.pol), y)], (255, 255, 255), 2.5)
        self.tekst(xk, y - 27, "0 s", czcionka(22, True), (255, 240, 170), "ma", obrys=(30, 50, 34))

    def gora_dol(self):
        xl, xp = self.x_pasa
        # u góry: dalej Bagno
        y = self.y(self.u_do)
        kol = BIOMY_KOLOR["bagno"]
        self.prost(self.x(-self.pol), y - 46, self.x(self.pol), y, fill=kol)
        self.prost(xl, y - 46, self.x(-self.pol), y, fill=KULISY)
        self.prost(self.x(self.pol), y - 46, xp, y, fill=KULISY)
        self.wielokat([(self.CX - 26, y - 60), (self.CX + 26, y - 60), (self.CX, y - 100)], fill=(150, 30, 30))
        self.prost(self.CX - 9, y - 62, self.CX + 9, y - 30, fill=(150, 30, 30))
        self.tekst(self.CX + 40, y - 92, "do Bagna — dalej ten sam pas (Bagno, Dżungla, …)", czcionka(24, True),
                   (150, 30, 30), "la")
        # na dole: z miasteczka
        y = self.y(self.u_od)
        self.wielokat([(self.CX - 22, y + 30), (self.CX + 22, y + 30), (self.CX, y - 4)], fill=(230, 40, 50))
        self.prost(self.CX - 8, y + 28, self.CX + 8, y + 62, fill=(230, 40, 50))
        self.tekst(self.CX, y + 70, "z miasteczka teleportem (E przy Bramie Miejskiej albo przycisk Teleport: przejście przez chmury)",
                   czcionka(24, True), (180, 30, 40), "ma")

    def szerokosc_pasa(self):
        y = self.y(self.u_od) + 200
        x0, x1 = self.x(-self.pol), self.x(self.pol)
        xl, xp = self.x_pasa
        for a, b, yy, kol in ((x0, x1, y, TUSZ), (xl, xp, y + 58, (90, 90, 90))):
            self.linia([(a, yy), (b, yy)], kol, 2)
            for xx in (a, b):
                self.linia([(xx, yy - 10), (xx, yy + 10)], kol, 2)
        self.tekst((x0 + x1) / 2, y - 6, "%d st = %s s biegu (pole gry)" % (
            self.p["pas"]["szerokosc"], l1(self.p["pas"]["szerokosc_s"])), czcionka(24, True), TUSZ, "md")
        self.tekst((xl + xp) / 2, y + 52, "z kulisami %d st" % (self.p["pas"]["szerokosc"] + 2 * self.kul),
                   czcionka(22), (90, 90, 90), "md")
        # podziałka w studach
        xs = 60
        ys = y + 20
        self.tekst(xs, ys - 34, "skala", czcionka(22, True), TUSZ)
        for i in range(5):
            self.prost(xs + i * 25 * S, ys, xs + (i + 1) * 25 * S, ys + 10, fill=TUSZ if i % 2 == 0 else (255, 255, 255),
                       outline=TUSZ, w=1)
        self.tekst(xs, ys + 16, "0", czcionka(22), TUSZ)
        self.tekst(xs + 125 * S, ys + 16, "125 st", czcionka(22), TUSZ, "ra")
        self.tekst(xs, ys + 46, "125 st = 7,8 s biegu (16 st/s)", czcionka(22), TUSZ)
        return y + 90

    def swiat(self, y):
        p = self.p
        sw = p["swiat"]
        X_od, X_do = -300, sw["X0"] + p["kolejne_biomy"][-1]["u_do"] + 60
        sx = (self.W - 80) / (X_do - X_od)
        self.tekst(40, y, "Świat w jednej linii (rzut z góry, północ u góry, %d razy mniejszy niż plan pasa)"
                   % round(S / sx), czcionka(26, True))
        y += 50

        def xw(X):
            return 40 + (X - X_od) * sx

        yc = y + 92
        h = (p["pas"]["szerokosc"] / 2 + self.kul) * sx
        h = max(h, 12)
        # słońce
        self.kolo(60, y + 22, 14, fill=(255, 210, 60), outline=(200, 140, 20), w=2)
        self.linia([(76, y + 34), (110, y + 56)], (200, 140, 20), 3)
        self.tekst(84, y + 8, "słońce z pn.-zach. → za plecami idącego na wschód", czcionka(22), (150, 100, 20))
        # miasteczko
        self.kolo(xw(0), yc, 140 * sx, fill=(232, 170, 90), outline=TUSZ, w=2)
        self.tekst(xw(0), yc + 34, "miasteczko", czcionka(22, True), TUSZ, "ma")
        # koniec Baseplate
        self.kreski([(xw(1024), yc - 40), (xw(1024), yc + 30)], (120, 120, 120), 2, 6, 5)
        # biomy
        biomy = [("las", "Las", sw["X0"] + p["pas"]["u_od"], sw["X0"] + p["pas"]["u_do"])]
        biomy += [(b["id"], b["nazwa"], b["swiat_x"][0], b["swiat_x"][1]) for b in p["kolejne_biomy"]]
        minuty = p["czas"]["rozklad_rosnacy_min"]
        for i, (bid, nazwa, a, b) in enumerate(biomy):
            kol = BIOMY_KOLOR.get(bid, (150, 150, 150))
            self.prost(xw(a), yc - h, xw(b), yc + h, fill=kol, outline=TUSZ, w=3 if bid == "las" else 1.2)
            f = czcionka(22, True) if bid == "las" else czcionka(22)
            self.tekst((xw(a) + xw(b)) / 2, yc + h + 8, nazwa, f, TUSZ, "ma")
            mi = minuty.get(bid)
            self.tekst((xw(a) + xw(b)) / 2, yc - h - 6, ("%d min" % mi) if mi else "cel", czcionka(22),
                       (90, 84, 76), "md")
        self.tekst(xw(sw["X0"] + p["pas"]["u_od"]) + 2, yc + h + 40, "X %d" % (sw["X0"] + p["pas"]["u_od"]),
                   czcionka(22), (90, 84, 76), "la")
        self.tekst(xw(X_do) - 10, yc + h + 40, "X %d" % (sw["X0"] + p["kolejne_biomy"][-1]["u_do"]), czcionka(22),
                   (90, 84, 76), "ra")
        y = yc + h + 80
        self.tekst(40, y, "oś pasa z = %d (oś miasteczka); świat = (%d + u; y; %d + v); przerywana kreska = koniec "
                   "płyty Baseplate (X 1024)" % (sw["Z0"], sw["X0"], sw["Z0"]), czcionka(22), (70, 64, 58))
        self.tekst(40, y + 32, "minuty nad biomami: propozycja rozkładu rosnącego, razem %d min do ósmego biomu "
                   "(wariant równy: ok. %s min na biom)" % (sum(minuty.values()),
                                                           l1(p["czas"]["rozklad_rowny_min"])),
                   czcionka(22), (70, 64, 58))
        return y + 72

    def legenda(self, y):
        self.tekst(40, y, "Legenda", czcionka(26, True))
        y += 44
        kol1, kol2, kol3 = 40, 560, 1080
        wiersze = [
            (kol1, "znak", "S"), (kol1, "znak", "M"), (kol1, "znak", "W"), (kol1, "znak", "T"), (kol1, "znak", "G"),
            (kol2, "petla", None), (kol2, "wezel", None), (kol2, "dom", None), (kol2, "kamera", None),
            (kol2, "przegrodka", None),
            (kol3, "przybycie", None), (kol3, "jajko", None), (kol3, "kamien", None), (kol3, "brama", None),
            (kol3, "linijka", None), (kol1, "znak_or", None), (kol2, "stop", None),
        ]
        opisy = {
            "S": "Leśny Slime", "M": "Muchomornik", "W": "Cierniowy Wilk", "T": "Leśny Troll (rzadki)",
            "G": "Strażnik Gaju (boss)",
            "petla": "pętla potwora (8 węzłów)", "wezel": "węzeł = plac walki r 12", "dom": "dom potwora (pod ścianą)",
            "kamera": "przelot kamery (czas, wys.)", "przegrodka": "przegródka kojca (przerwa 24)",
            "przybycie": "przybycie (teleport)", "jajko": "stanowisko jajka", "kamien": "Kamień Powrotu",
            "brama": "brama zamknięta do Strażnika", "linijka": "lewe kulisy: sekundy i study",
            "znak_or": "punkt orientacyjny", "stop": "STOP: kamera stoi, Strażnik ryczy",
        }
        licz = {kol1: 0, kol2: 0, kol3: 0}
        for x, typ, lit in wiersze:
            yy = y + licz[x] * 40
            licz[x] += 1
            cx, cy = x + 16, yy + 14
            if typ == "znak":
                l, k = POTWOR[{"S": "Leśny Slime", "M": "Muchomornik", "W": "Cierniowy Wilk", "T": "Leśny Troll",
                               "G": "Strażnik Gaju"}[lit]]
                self.kolo(cx, cy, 12, fill=k, outline=TUSZ, w=2)
                self.tekst(cx, cy + 1, l, czcionka(17, True), (255, 255, 255), "mm")
                opis = opisy[lit]
            else:
                opis = opisy[typ]
                if typ == "petla":
                    self.kreski([(cx - 14, cy), (cx + 14, cy)], (46, 170, 60), 3, 7, 4)
                elif typ == "wezel":
                    self.kolo(cx, cy, 4, fill=(46, 170, 60))
                elif typ == "dom":
                    self.prost(cx - 6, cy - 6, cx + 6, cy + 6, fill=(92, 60, 36), outline=TUSZ, w=1.5)
                elif typ == "kamera":
                    self.kreski([(cx - 14, cy), (cx + 14, cy)], KAMERA, 3.5, 7, 4)
                    self.kolo(cx, cy, 5, fill=KAMERA, outline=(255, 255, 255), w=1.5)
                elif typ == "przegrodka":
                    self.kreski([(cx - 14, cy), (cx + 14, cy)], (110, 140, 80), 2, 5, 4)
                elif typ == "przybycie":
                    self.kolo(cx, cy, 9, fill=(230, 40, 50), outline=TUSZ)
                elif typ == "jajko":
                    self.d.ellipse([(cx - 7) * K, (cy - 10) * K, (cx + 7) * K, (cy + 10) * K], fill=(255, 248, 226),
                                   outline=TUSZ, width=2 * K)
                elif typ == "kamien":
                    self.wielokat([(cx, cy - 10), (cx + 9, cy), (cx, cy + 10), (cx - 9, cy)], fill=(150, 150, 160),
                                  outline=TUSZ, w=2)
                elif typ == "brama":
                    self.prost(cx - 14, cy - 4, cx + 14, cy + 4, fill=(210, 40, 40), outline=TUSZ, w=1.5)
                elif typ == "linijka":
                    self.prost(cx - 14, cy - 10, cx + 14, cy + 10, fill=KULISY)
                    self.linia([(cx - 14, cy), (cx, cy)], (255, 255, 255), 2.5)
                elif typ == "znak_or":
                    self.wielokat([(cx, cy - 11), (cx + 10, cy + 8), (cx - 10, cy + 8)], fill=(84, 88, 104),
                                  outline=TUSZ, w=2)
                elif typ == "stop":
                    self.kolo(cx, cy, 6, fill=KAMERA, outline=(255, 255, 255), w=2)
            self.tekst(x + 40, yy, opis, czcionka(22))
        return y + max(licz.values()) * 40

    def stopka(self):
        self.tekst(40, self.H - 50, "Źródło: swiat/biom_las/pas/plan_pasa.json · kontrola: sprawdz_plan.py · "
                   "rysuje: rysuj_plan.py", czcionka(22), (110, 104, 96))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Plansza pasa lasu z plan_pasa.json")
    ap.add_argument("--plan", default=os.path.join(TU, "plan_pasa.json"))
    ap.add_argument("--wyj", default=os.path.join(TU, "plan_pasa.png"))
    ap.add_argument("--szer", type=int, default=1600)
    a = ap.parse_args()
    if a.szer != 1600:
        global S
        S = S * a.szer / 1600
    with open(a.plan, encoding="utf-8") as f:
        plan = json.load(f)
    obraz = Plansza(plan, a.szer).rysuj()
    obraz.save(a.wyj, optimize=True)
    print("zapisano %s (%d × %d px)" % (os.path.basename(a.wyj), obraz.width, obraz.height))


if __name__ == "__main__":
    main()
