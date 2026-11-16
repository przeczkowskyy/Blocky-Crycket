# -*- coding: utf-8 -*-
"""Detale pasa: drobiazgi przy krawędziach ścieżki, kępy runa w wolnych miejscach pola gry, powalone kłody, kwiaty.
Rodziny drobiazgów i ich budowa — swiat/biom_las/detale.py (drobiazg, kloda); tu tylko rozsiew na pas.

Zasady jak w starym lesie, liczone na częściach (zasady.postaw): nic na ścieżce, w otwarciach przejść, na pętlach
potworów; rzeczy wyższe niż 1,4 nie wchodzą w place walki (r 12) — w kojcach zostają niskie: kwiatki, kamyki, pnącza,
korzenie, gałązki, grzybki. Drobiazgi bez kolizji i cienia, kłody z kolizją (tylko z dala od placów i pętli).
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import detale, rosliny  # noqa: E402
from swiat.las_pas.kontekst import ODCINKI_SCIEZKI, SZER_SCIEZKI, v_sciezki  # noqa: E402
from swiat.las_pas.zasady import postaw  # noqa: E402

# odcinek → (podbiom starego lasu dla kolorów, sztuk na 100 st ścieżki (obie strony), {rodzina: waga}, kępy runa, kłody)
GESTOSC = {
    "wejscie": ("laka", 26, {"kwiatek": 4, "kepka": 3, "kamyki": 1, "wysoka_trawa": 1, "lan_kwiatow": 1}, 20, 1),
    "plot_z_furtka": ("laka", 10, {"kwiatek": 2, "kepka": 2}, 0, 0),
    "zagroda": ("laka", 18, {"kepka": 3, "kwiatek": 3, "kamyki": 2, "kretowisko": 1}, 26, 0),
    "strumyk_z_mostkiem": ("laka", 10, {"kamyki": 2, "kepka": 1}, 0, 0),
    "lasek": ("kapeluszowo", 22, {"grzybki": 4, "paproc": 2, "kepka": 1, "korzen": 2, "pnacze": 2}, 32, 2),
    "jezynowe_zwezenie": ("ostepy", 10, {"korzen": 1, "pnacze": 1}, 0, 0),
    "zarosla": ("ostepy", 22, {"paproc": 3, "korzen": 3, "pnacze": 2, "kamyki": 2, "grzybki": 1, "patyk": 2}, 32, 3),
    "kamienny_prog": ("wawoz", 10, {"kamyki": 2, "kosc": 1}, 0, 0),
    "leze": ("wawoz", 18, {"kamyki": 4, "kepka_sucha": 2, "kosc": 2, "patyk": 1, "krzaczek": 1}, 20, 2),
    "brama_menhirow": ("korona", 8, {"kamyki": 1, "kwiatek": 1}, 0, 0),
    "arena": ("korona", 18, {"kamyki": 2, "kwiatek": 3, "kepka": 2}, 18, 1),
    "bagno": ("ostepy", 8, {"patyk": 1, "pnacze": 1}, 0, 0),
}
# najwyższy punkt drobiazgu (z detale.py) i zasięg na ziemi
WYS = {"kepka": 1.75, "kepka_sucha": 1.9, "kwiatek": 0.85, "lan_kwiatow": 1.45, "wysoka_trawa": 3.3, "kamyki": 0.8,
       "grzybki": 1.45, "korzen": 0.8, "patyk": 0.45, "pnacze": 0.3, "paproc": 2.0, "kretowisko": 0.7, "kosc": 0.5,
       "krzaczek": 2.3}
NISKIE = ("kwiatek", "kamyki", "pnacze", "korzen", "patyk")


def _losuj(rnd, wagi):
    suma = sum(wagi.values())
    t = rnd.uniform(0, suma)
    for k, w in wagi.items():
        t -= w
        if t <= 0:
            return k
    return k


def _gestosc(K, u):
    o = K.odcinek(u)
    return o, GESTOSC.get(o, GESTOSC["arena"])


def brzegi_sciezki(s, K, Z):
    """Drobiazgi przy krawędziach ścieżki: krok 2 st, strona losowa, 0,9–3,0 od krawędzi."""
    rnd = K.rnd_detale
    n = 0
    for a, b in ODCINKI_SCIEZKI:
        u = a + 1.0
        while u < b - 1.0:
            o, (pb, gest, wagi, _, _) = _gestosc(K, u)
            if rnd.random() < gest / 100.0 * 2.0 * 1.3:
                rodzina = _losuj(rnd, wagi)
                for proba in range(4):
                    zn = rnd.choice((-1, 1))
                    v = v_sciezki(u) + zn * (SZER_SCIEZKI / 2.0 + rnd.uniform(0.9, 3.0) + 0.5 * proba)
                    r = detale.ZASIEG.get(rodzina, 1.0)
                    if proba >= 2 and rodzina not in NISKIE:
                        rodzina = rnd.choice(NISKIE)
                    if not K.miejsce_ok(u, v, r, WYS[rodzina], sciezka_zapas=0.3):
                        continue

                    def bud(u=u, v=v, rodzina=rodzina, pb=pb):
                        with s.grupa("Detale/%s" % o.capitalize()):
                            detale.drobiazg(s, rnd, rodzina, (u, 0.0, v), pb)
                    if postaw(s, Z, bud):
                        K.zajmij(u, v, 0.9)
                        n += 1
                        break
            u += 2.0
    return n


def runo(s, K, Z):
    """Kępy runa (2–3 drobiazgi w promieniu ok. 3) w wolnych miejscach pola gry każdej przegrody i powalone kłody."""
    rnd = K.rnd_detale
    stat = {}
    for q in K.P["przegrody"]:
        pb, _, wagi, n_kep, n_klod = GESTOSC[q["id"]]
        postawione = proby = 0
        while postawione < n_kep and proby < n_kep * 60:
            proby += 1
            u = rnd.uniform(q["u_od"] + 2, q["u_do"] - 2)
            v = rnd.uniform(-34.0, 34.0)
            if not K.miejsce_ok(u, v, 3.0, 0.5):
                continue
            wys_ok = K.miejsce_ok(u, v, 3.0, 2.0)
            rodziny = []
            for i in range(rnd.choice((2, 2, 3))):
                r_ = _losuj(rnd, wagi)
                if not wys_ok and WYS[r_] > 1.4:
                    r_ = rnd.choice(NISKIE)
                rodziny.append(r_)

            def bud(u=u, v=v, rodziny=rodziny, pb=pb, qid=q["id"]):
                with s.grupa("Detale/%s" % qid.capitalize()):
                    for i, r_ in enumerate(rodziny):
                        a = rnd.uniform(0, 2 * math.pi)
                        rr = 0.0 if i == 0 else rnd.uniform(1.6, 2.8)
                        detale.drobiazg(s, rnd, r_, (u + rr * math.cos(a), 0.0, v + rr * math.sin(a)), pb)
            if postaw(s, Z, bud):
                K.zajmij(u, v, 3.2)
                postawione += 1
        klody = proby = 0
        while klody < n_klod and proby < 400:
            proby += 1
            u = rnd.uniform(q["u_od"] + 6, q["u_do"] - 6)
            v = rnd.choice((-1, 1)) * rnd.uniform(26.0, 33.0)
            if not K.miejsce_ok(u, v, 5.5, 2.6, kolizja=True):
                continue

            def bud(u=u, v=v, qid=q["id"], pb=pb):
                with s.grupa("Detale/%s" % qid.capitalize()):
                    detale.kloda(s, rnd, (u, 0.0, v), rnd.uniform(0.85, 1.1), mech=pb != "wawoz")
            if postaw(s, Z, bud):
                K.zajmij(u, v, 5.5)
                klody += 1
        stat[q["id"]] = (postawione, n_kep, klody, n_klod)
    return stat


def kwiaty(s, K, Z):
    """Kępy kwiatów na Polanie i w Arenie (rosliny.kwiaty, 3 części), poza ścieżką."""
    rnd = K.rnd_detale
    n = 0
    for qid, ile, kolory in (("wejscie", 16, (("zloto", "biel"), ("czerwien", "zloto"), ("biel", "dach_sklep"))),
                             ("arena", 10, (("biel", "biel"), ("biel", "dach_sklep"), ("biel", "zloto")))):
        q = K.przegrody[qid]
        proby = 0
        k = 0
        while k < ile and proby < ile * 40:
            proby += 1
            u, v = rnd.uniform(q["u_od"] + 2, q["u_do"] - 2), rnd.uniform(-34.0, 34.0)
            if not K.miejsce_ok(u, v, 1.4, 1.2):
                continue

            def bud(u=u, v=v):
                with s.grupa("Detale/%s" % qid.capitalize()):
                    rosliny.kwiaty(s, rnd, (u, 0.0, v), rnd.choice(kolory))
            if postaw(s, Z, bud):
                K.zajmij(u, v, 1.4)
                k += 1
                n += 1
    return n
