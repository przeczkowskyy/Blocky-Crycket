# -*- coding: utf-8 -*-
"""ŻOŁĘDZIAK — pet pospolity z leśnego jajka (próba swiat/pety_proba; status: propozycja).

Przebudowa 25/26.11.2026 według arkusza obrotów Pawła (`zoledziak_obroty.jpg`: przód, bok, tył, drugi bok; model
z 17.11 był kanciastym klockiem). Wzór wyglądu: wydłużony, obły żołądź (ok. 2,2 studa z ogonkiem) na dwóch krótkich
nóżkach-walcach, jaśniejszy dół brzuszka z przodu, czapka-kopułka w ciemniejsze pasy z DASZKIEM z przodu (jak czapka
z daszkiem), ogonek z jednym liściem, rączki-patyczki z rozgałęzionymi palcami, okrągłe oczy z odblaskami, rumieńce
i uśmiech. Kości, nazwy kości i klipy jak w modelu z 17.11 (gra: wyklucie, chodzenie za graczem, zagroda).

    python -B swiat/postacie/przebuduj.py zoledziak --bez-filmow

Budowa (typ="stwor", 1 jednostka = 1 stud, patrzy w +Z, lewa = +X):
  Root > Tulow > {Czapka > Ogonek, RekaL, RekaP, NogaL, NogaP}
Klipy: spoczynek (pętla), chod (kaczy chód z podskokiem, pętla), radosc (podskok z obrotem), wyklucie (z jajka).
"""
from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import (klip_radosc, klip_wyklucie, lata_przez, model, naklejka, oczy_okragle,
                                       usmiech)

ID = "zoledziak"

PALETA = {
    "orzech": "DE8E30", "orzech_jasny": "F5C874", "orzech_ciemny": "A8692C",
    "czapka": "7E5230", "czapka_ciemna": "5A371C", "ogonek": "6B4423", "patyk": "6E4626",
    "lisc": "5DBB3F", "lisc_zylka": "3E8A2C", "oko": "2E180C", "rumieniec": "F4A2A2", "buzia": "4A2414",
}

ORZECH = ((0.0, 0.84, 0.0), (1.0, 1.42, 0.92))        # elipsoida ciała: środek, średnice
Y_STAW = 0.42                                         # staw tułowia (nisko — kołysze się od spodu)
KOPULA = ((0.0, 1.57, 0.0), (1.18, 0.64, 1.18))       # kopułka czapki (okrągła w poziomie — pasy po obrocie pasują)
Y_CZAPKI = 1.32
Y_OGONKA = 1.86
RAMIE = (0.47, 0.83, 0.02)                             # staw rączki (lewej; prawa: −x)
NOGA = (0.21, 0.33, 0.02)


def zbuduj():
    p = Postac(ID, "Żołędziak", typ="stwor", skala=1.0, faza=0.06, paleta=PALETA)
    (cx, cy, cz), (w, h, d) = ORZECH
    p.kosc("Tulow", "Root", staw=(0, Y_STAW, 0), czesc=(w, h, d), srodek=(0, cy - Y_STAW, 0))
    p.kosc("Czapka", "Tulow", staw=(0, Y_CZAPKI, 0), czesc=(1.24, 0.6, 1.24), srodek=(0, 0.25, 0))
    p.kosc("Ogonek", "Czapka", staw=(0, Y_OGONKA, 0), czesc=(0.14, 0.32, 0.14), srodek=(0, 0.15, 0))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Reka" + s, "Tulow", staw=(zn * RAMIE[0], RAMIE[1], RAMIE[2]), czesc=(0.08, 0.4, 0.08),
               srodek=(zn * 0.12, -0.15, 0))
        p.kosc("Noga" + s, "Tulow", staw=(zn * NOGA[0], NOGA[1], NOGA[2]), czesc=(0.2, 0.3, 0.2),
               srodek=(0, -0.15, 0))

    # ------------------------------------------------------------------ orzech: obła kropla, jasny dół brzuszka z przodu
    with model(p, "Tulow"):
        p.kula("Orzech", (cx, cy, cz), (w, h, d), "orzech", segm=28)
        # jasny dół brzuszka: łata z granicą ukośną jak na boku arkusza (z przodu ok. 0,7 studa, z tyłu przy spodzie)
        p.kula("Brzuszek", *lata_przez(ORZECH, (0.78, 1), (0.22, -1), s=0.14, bok=(0, -1, 1)), "orzech_jasny", segm=28)
        p.kula("Czubek spodu", (0, 0.16, 0.02), (0.2, 0.2, 0.19), "orzech_ciemny", segm=10)
        oczy_okragle(p, ORZECH, 0.2, 1.1, szer=0.19, wys=0.22, kolor="oko", grub=0.07)
        for zn, s in ((1, "L"), (-1, "P")):
            naklejka(p, "Rumieniec " + s, ORZECH, zn * 0.34, 0.97, (0.15, 0.08, 0.03), "rumieniec")
        usmiech(p, ORZECH, 0.96, szer=0.15, kolor="buzia", grub=0.032)

    # ------------------------------------------------------------------ czapka-kopułka w pasy, z daszkiem z przodu
    with model(p, "Czapka"):
        (kx, ky, kz), (kw, kh, kd) = KOPULA
        p.kula("Czapka", (kx, ky, kz), (kw, kh, kd), "czapka", segm=20)
        p.walec("Brzeg czapki", (0, 1.34, 0), (kw + 0.06, 0.12, kd + 0.06), "czapka", segm=20, faza=0.03)
        # pasy: cienkie „plastry” kopułki 5% większe — wystają wąskim pasem wzdłuż południka (4 plastry = 8 pasów)
        for kat in (0, 45, 90, 135):
            p.kula("Pas czapki", (kx, ky, kz), (0.3, kh * 1.05, kd * 1.05), "czapka_ciemna", rot=(0, kat, 0),
                   segm=16)
        p.kula("Daszek", (0, 1.35, 0.5), (0.86, 0.07, 0.66), "czapka", rot=(8, 0, 0), segm=16)

    # ------------------------------------------------------------------ ogonek z jednym liściem
    with model(p, "Ogonek"):
        p.walec("Ogonek", (0.0, 2.0, 0), (0.13, 0.32, 0.13), "ogonek", rot=(0, 0, -6), segm=10, faza=0.02)
        with p.uklad(pos=(0.24, 2.1, 0.0), obrot=(0, -25, 28)):
            p.kula("Listek", (0, 0, 0), (0.4, 0.21, 0.045), "lisc", "matowy", segm=12)
            p.blok("Listek zylka", (0, 0, 0.022), (0.32, 0.025, 0.022), "lisc_zylka", "matowy", faza=0.0)

    # ------------------------------------------------------------------ rączki-patyczki z trzema palcami, nóżki-walce
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Reka" + s, od="staw"), p.uklad(obrot=(0, 0, zn * 42)):
            p.walec("Raczka", (0, -0.18, 0), (0.075, 0.4, 0.075), "patyk", segm=8, faza=0.0)
            for kat, dl in ((-zn * 38, 0.13), (zn * 34, 0.12)):
                with p.uklad(pos=(0, -0.34, 0), obrot=(0, 0, kat)):
                    p.walec("Palec", (0, -0.06, 0), (0.05, dl, 0.05), "patyk", segm=6, faza=0.0)
        with p.na("Noga" + s, od="staw"):
            p.walec("Nozka", (0, -0.165, 0), (0.2, 0.33, 0.2), "orzech", segm=14, faza=0.04)

    p.zaczep("RootAttachment", "Tulow", (0, -Y_STAW, 0))
    p.zaczep("GlowaAttachment", "Czapka", (0, 0.88, 0))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 0)
    return p


SLABOSCI = [
    "Kości własne (nie R15) — klipy idą przez Motor6D w grze (prototyp z klocków).",
    "Obłe bryły to elipsoidy i walce (w Roblox Part Ball / Cylinder albo SpecialMesh) — w grze są gładkie, ale bez "
    "fazowania krawędzi i bez komiksowego obrysu z renderu.",
    "Pasy czapki to cienkie plastry kopułki (wystają o 5%) — z bliska widać, że są wypukłe, a nie namalowane.",
    "Liść na arkuszu w bokach przeczy sobie (raz widać go z jednej, raz z drugiej strony) — w modelu jest po lewej "
    "stronie peta (+X), obrócony o 25°, więc widać go z przodu, z tyłu i z lewego boku.",
    "Brak nóg w klipie wyklucia: w jajku żołądź siedzi cały, nóżki są schowane w skorupce.",
]


def _klipy(p):
    k = p.klip("spoczynek", 60, petla=True)
    k.cykl("Tulow", "przes", (0, 0.03, 0), czestosc=2)
    k.cykl("Tulow", "obrot", (0, 0, 3), czestosc=1)
    k.cykl("Czapka", "obrot", (0, 0, -4), czestosc=1, faza=0.1)
    k.cykl("Ogonek", "obrot", (0, 0, 12), czestosc=2)
    k.cykl("RekaL", "obrot", (0, 0, 9), czestosc=1)
    k.cykl("RekaP", "obrot", (0, 0, -9), czestosc=1, faza=0.15)

    k = p.klip("chod", 20, petla=True)
    k.cykl("Tulow", "obrot", (0, 0, 9), czestosc=1)                              # kaczy chód
    k.cykl("Tulow", "przes", (0, 0.07, 0), czestosc=2, srodek=(0, 0.07, 0))      # podskok przy każdym kroku
    k.cykl("NogaL", "obrot", (32, 0, 0), czestosc=1)
    k.cykl("NogaP", "obrot", (32, 0, 0), czestosc=1, faza=0.5)
    k.cykl("RekaL", "obrot", (-28, 0, 0), czestosc=1, faza=0.5)
    k.cykl("RekaP", "obrot", (-28, 0, 0), czestosc=1)
    k.cykl("Czapka", "obrot", (0, 0, -6), czestosc=1, faza=0.1)
    k.cykl("Ogonek", "obrot", (0, 0, 16), czestosc=2, faza=0.2)

    def rece(k, szczyt, koniec):
        for s, zn in (("L", 1), ("P", -1)):
            k.klucz(0, "Reka" + s, obrot=(0, 0, 0))
            k.klucz(szczyt, "Reka" + s, obrot=(0, 0, zn * 120))
            k.klucz(koniec, "Reka" + s, obrot=(0, 0, 0))
        k.klucz(0, "Czapka", obrot=(0, 0, 0))
        k.klucz(szczyt, "Czapka", obrot=(-22, 0, 0))
        k.klucz(szczyt + 6, "Czapka", obrot=(10, 0, 0))
        k.klucz(koniec, "Czapka", obrot=(0, 0, 0))

    klip_radosc(p, "Tulow", wysokosc=0.75, dodatki=lambda k: rece(k, 15, 36))
    klip_wyklucie(p, "Tulow", glebokosc=0.95, wyskok=0.95, dodatki=lambda k: rece(k, 12, 30))
