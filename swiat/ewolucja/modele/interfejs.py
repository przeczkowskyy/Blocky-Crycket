# -*- coding: utf-8 -*-
"""Grafika interfejsu w stylu smoków: ikony 256 px (przezroczyste PNG), portrety ośmiu stadiów z czarnymi sylwetkami
oraz trzy makiety 1280 × 590 (HUD na telefonie, panel legowiska, odsłona ewolucji).

    python -B swiat/ewolucja/modele/generuj.py interfejs      # wymaga wcześniejszych „dane” i „mapa” (tylko czyta)

Bryły ikon renderuje Blender (biblioteka, wspólna blokada), obrys, poświatę i makiety składa PIL. Pełne pliki:
%LOCALAPPDATA%/BlockyCrycket/modele/smok_ewolucja/interfejs/{ikony,portrety,makiety}; podglądy: podglad/21–25.
Napisy w makietach składa czcionka zastępcza z tego komputera (Arial Rounded) — w grze: czcionki Roblox z README.
"""
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

from swiat.ewolucja.modele import obrazy_gry as og
from swiat.ewolucja.modele import rekwizyty
from swiat.ewolucja.modele import swiat_zestaw as sz

K = {"panel": (43, 34, 56), "panel2": (62, 50, 80), "pas": (28, 22, 44), "obrys": (26, 20, 36), "tekst": (255, 246, 224),
     "tekst2": (190, 178, 212), "zar": (255, 122, 42), "zar_j": (255, 210, 63), "hp": (255, 77, 106), "zloto": (255, 201, 52),
     "krysztal": (127, 248, 255), "ogien": (232, 76, 44), "moc": (58, 128, 234), "kosc": (255, 246, 224), "zielen": (124, 227, 139)}
NAZWY = ("HATCHLING", "WHELP", "DRAKE", "FIRE DRAKE", "DRAGON", "WAR DRAGON", "ELDER DRAGON", "ANCIENT DRAGON")
CZ, CI, ZO, BI = "E3412B", "C9362E", "FFC934", "FFFDF4"


# --------------------------------------------------------------------------- bryły ikon (małe modele z klocków)
def _m(id, faza=0.12):
    return sz._nowy("ik_" + id, "Ikona " + id, faza=faza)


def _plomien(p, x, y, z, w, h, kolor, rot):
    p.ostroslup("Plomien", (x, y, z), (w, h, w), kolor, "swiecacy", rot=rot, gora=(0.0, 0.0), faza=0.0)


def m_bite():
    p = _m("bite")
    with p.uklad(pos=(0, 0.5, 0), obrot=(-24, 0, 0)):
        p.blok("Gora", (0, 0.6, 1.4), (3.0, 1.3, 3.6), CZ)
        p.blok("Nos", (0, 1.3, 2.4), (2.0, 0.3, 1.2), "F2643A")
        p.blok("Oko", (1.52, 0.9, 0.5), (0.08, 0.36, 0.8), "FFE066", "swiecacy", faza=0.0)
        p.blok("Oko 2", (-1.52, 0.9, 0.5), (0.08, 0.36, 0.8), "FFE066", "swiecacy", faza=0.0)
        for x in (-1.2, -0.4, 0.4, 1.2):
            p.klin("Zab", (x, -0.45, 3.0), (0.5, 0.9, 0.5), BI, "polysk", rot=(180, 0, 0), faza=0.02)
        for zn in (1, -1):
            p.klin("Kiel", (zn * 1.35, -0.6, 1.9), (0.4, 1.2, 0.6), BI, "polysk", rot=(180, 0, 0), faza=0.02)
    with p.uklad(pos=(0, -0.5, 0), obrot=(22, 0, 0)):
        p.blok("Dol", (0, -0.5, 1.3), (2.8, 1.0, 3.4), CI)
        p.blok("Jezyk", (0, 0.05, 1.5), (1.6, 0.14, 2.4), "F06E86", "matowy")
        for x in (-1.1, 0.0, 1.1):
            p.klin("Zab dolny", (x, 0.4, 2.8), (0.5, 0.8, 0.5), BI, "polysk", rot=(0, 180, 0), faza=0.02)
    p.blok("Gardlo", (0, 0, -0.4), (2.6, 2.0, 0.6), "4A1220", "matowy")
    return p


def m_dash():
    p = _m("dash", 0.08)
    for i, (x, s, kol) in enumerate(((-2.3, 0.7, "CFF8FF"), (-0.2, 0.9, "7FE9FF"), (2.2, 1.15, "2F8FEA"))):
        for zn in (1, -1):
            p.blok("Strzalka", (x, zn * 0.62 * s, 0), (2.1 * s, 0.7 * s, 0.7), kol, "swiecacy" if i < 2 else "zwykly",
                   rot=(0, 0, -zn * 36))
    return p


def m_ember():
    p = _m("ember")
    p.kula("Kula", (0.6, 0, 0), 2.5, "FFA62E", "swiecacy", segm=12)
    p.kula("Rdzen", (0.9, 0.1, 0.7), 1.5, "FFF7C8", "swiecacy", segm=12)
    for y, x, h, kol in ((0.0, -1.6, 2.6, "FF6A1A"), (0.9, -1.1, 1.8, "FFB52E"), (-0.9, -1.1, 1.8, "FFB52E"), (0.3, -2.6, 1.6, "E8381A")):
        _plomien(p, x, y, 0, 1.0, h, kol, (0, 0, 90))
    return p


def m_inferno():
    p = _m("inferno")
    p.walec("Ziemia", (0, 0.1, 0), (6.4, 0.2, 6.4), "37323F", "matowy", segm=8)
    p.walec("Zar", (0, 0.16, 0), (5.4, 0.2, 5.4), "FF7A2A", "swiecacy", segm=8)
    p.kula("Rdzen", (0, 1.0, 0), 1.8, "FFF7C8", "swiecacy", segm=12)
    for n, r_, h, th, kol in ((7, 1.1, 3.4, 12, "FFE680"), (9, 2.1, 2.6, 30, "FF8A2A"), (11, 2.9, 1.7, 46, "E8381A")):
        for i in range(n):
            a = 360.0 * i / n + 13 * n
            with p.uklad(pos=(r_ * math.cos(math.radians(a)), 0.3, r_ * math.sin(math.radians(a))), obrot=(th, 90 - a, 0)):
                _plomien(p, 0, h / 2, 0, 0.9, h, kol, (0, 0, 0))
    return p


def m_tail():
    p = _m("tail", 0.06)
    for i in range(9):                                          # smuga zamachu: łuk rosnących klocków
        a = math.radians(30 + i * 30)
        p.blok("Smuga", (2.7 * math.cos(a), 0, 2.7 * math.sin(a)), (0.25 + 0.09 * i, 0.3, 1.5), "CFF8FF" if i % 2 else "7FE9FF",
               "swiecacy", rot=(0, -math.degrees(a), 0))
    a = math.radians(300)
    with p.uklad(pos=(2.7 * math.cos(a), 0.1, 2.7 * math.sin(a)), obrot=(0, -math.degrees(a), 0)):
        p.blok("Ogon", (0, 0, -1.6), (1.0, 0.9, 2.2), CZ)
        p.blok("Luska", (0, 0.5, -1.6), (1.16, 0.2, 1.3), "8C2A26", "matowy")
        p.blok("Ogon 2", (0, 0, 0.1), (0.8, 0.7, 1.6), CZ)
        for zn in (1, -1):
            p.klin("Grot", (zn * 0.6, 0, 1.9), (0.3, 1.2, 2.2), "FFE680", "swiecacy", rot=(0, 180, zn * 90), faza=0.0)
    return p


def m_wing():
    p = _m("wing", 0.04)
    p.blok("Ramie", (-1.2, 0.06, 0.3), (2.6, 0.4, 0.4), "6A3AC0", rot=(0, 12, 0))
    for i, (kat, dl, rozw) in enumerate(((0, 4.4, 30), (30, 4.0, 30), (60, 3.3, 28))):
        with p.uklad(pos=(0, 0, 0), obrot=(0, kat, 0)):
            szer = dl * math.tan(math.radians(rozw))
            p.klin("Blona", (dl / 2, 0, -szer / 2), (0.12, dl, szer), "35DDB4" if i % 2 == 0 else "239C8A", "matowy", rot=(0, 0, 90), faza=0.0)
            p.blok("Palec", (dl / 2, 0.1, 0), (dl + 0.1, 0.24, 0.24), "6A3AC0")
    for z in (-3.6, -4.3):
        p.blok("Wiatr", (1.4, 0, z), (6.0 + z, 0.16, 0.2), "FFFFFF", "swiecacy", faza=0.0)
    return p


def m_roar():
    p = _m("roar")
    p.blok("Czaszka", (0, 0.6, -0.6), (2.6, 2.2, 2.4), CZ)
    p.blok("Helm", (0, 1.8, -0.5), (2.9, 0.3, 2.1), "8C2A26", "matowy", rot=(9, 0, 0))
    for zn in (1, -1):
        p.klin("Rog", (zn * 0.9, 2.6, -1.6), (0.5, 0.8, 2.0), "3A1C1C", "polysk", rot=(-30, 0, 0), faza=0.03)
        p.blok("Oko", (zn * 1.32, 0.9, 0.0), (0.08, 0.36, 0.8), "FFE066", "swiecacy", rot=(zn * 14, 0, 0), faza=0.0)
    with p.uklad(pos=(0, 0.3, 0.5), obrot=(-16, 0, 0)):
        p.blok("Pysk", (0, 0.2, 1.2), (2.0, 0.9, 2.4), CZ)
        for x in (-0.7, 0.7):
            p.klin("Kiel", (x, -0.6, 2.0), (0.36, 0.9, 0.5), BI, "polysk", rot=(180, 0, 0), faza=0.02)
    with p.uklad(pos=(0, -0.3, 0.4), obrot=(30, 0, 0)):
        p.blok("Zuchwa", (0, -0.3, 1.1), (1.9, 0.6, 2.3), CI)
        p.blok("Jezyk", (0, 0.05, 1.2), (1.1, 0.12, 1.7), "F06E86", "matowy")
    for j, (r_, kol) in enumerate(((2.0, "FFFFFF"), (3.0, "FFE680"), (4.0, "FFB52E"))):        # fale ryku
        for t in (-36, -18, 0, 18, 36):
            p.blok("Fala", (0, 0.2 + r_ * math.sin(math.radians(t)), 2.4 + r_ * math.cos(math.radians(t))), (0.5, 0.26, 0.9 + 0.1 * j),
                   kol, "swiecacy", rot=(-t + 90, 0, 0), faza=0.0)
    return p


def m_meteor():
    p = _m("meteor")
    p.blok("Rdzen", (-1.0, -1.0, 0), (1.9, 1.9, 1.7), "FF7A2A", "swiecacy", rot=(0, 0, 20), faza=0.0)
    p.blok("Skala", (-1.5, -0.7, 0.2), (1.5, 2.2, 2.1), "37323F", "matowy", rot=(0, 0, 20))
    p.blok("Skala 2", (-0.5, -1.6, -0.2), (2.0, 1.2, 2.1), "26222F", "matowy", rot=(0, 0, 20))
    p.blok("Skala 3", (-0.6, -0.3, 0.3), (1.2, 1.0, 1.9), "37323F", "matowy", rot=(0, 0, 20))
    for i, (d, w, kol) in enumerate(((1.2, 1.5, "FFE680"), (2.2, 1.3, "FFB52E"), (3.2, 1.1, "FF6A1A"), (4.0, 0.8, "E8381A"))):
        _plomien(p, -1.0 + d * 0.72, -1.0 + d * 0.72, 0, w, 2.2, kol, (0, 0, -45))
        _plomien(p, -1.0 + d * 0.72 + 0.7 * (i % 2 * 2 - 1), -1.0 + d * 0.72 - 0.7 * (i % 2 * 2 - 1), 0.2, w * 0.6, 1.5, "FF8A2A", (0, 0, -45))
    for x, y in ((-2.9, -2.4), (-0.4, -3.0), (-3.2, -0.6)):
        p.blok("Iskra", (x, y, 0.2), (0.4, 0.4, 0.4), "FFE680", "swiecacy", rot=(0, 0, 45), faza=0.0)
    return p


def m_klodka():
    p = _m("klodka")
    p.blok("Korpus", (0, -0.5, 0), (3.0, 2.4, 1.2), "3A3048")
    p.blok("Opaska", (0, 0.5, 0), (3.2, 0.4, 1.36), "1E1830", "matowy", faza=0.06)
    for x in (-0.95, 0.95):
        p.blok("Palak", (x, 1.5, 0), (0.56, 1.8, 0.56), "8C8AA0", "metal")
    p.blok("Palak gora", (0, 2.4, 0), (2.46, 0.56, 0.56), "8C8AA0", "metal")
    p.blok("Dziurka", (0, -0.4, 0.62), (0.6, 0.6, 0.1), "FF7A2A", "swiecacy", rot=(0, 0, 45), faza=0.0)
    p.blok("Dziurka 2", (0, -0.95, 0.62), (0.3, 0.7, 0.1), "FF7A2A", "swiecacy", faza=0.0)
    return p


def m_moneta():
    p = _m("moneta", 0.08)
    p.walec("Moneta", (0, 0, 0), (3.4, 0.6, 3.4), ZO, "metal", rot=(90, 0, 0), segm=8)
    p.walec("Rant", (0, 0, 0), (3.7, 0.36, 3.7), "E09A1A", "metal", rot=(90, 0, 0), segm=8)
    p.blok("Znak", (0, 0, 0.34), (1.4, 1.4, 0.12), "FFE680", "metal", rot=(0, 0, 45), faza=0.02)
    p.blok("Zar", (0, 0, 0.42), (0.6, 0.6, 0.1), "FF7A2A", "swiecacy", rot=(0, 0, 45), faza=0.0)
    return p


def m_klejnot(id, kolory):
    p = _m(id, 0.06)
    with p.uklad(obrot=(0, 0, 45)):
        if len(kolory) > 2:                                     # tęcza: skośne pasy
            for i, kol in enumerate(kolory):
                p.blok("Pas", ((i - 2) * 0.56, 0, 0), (0.56, 2.8, 1.0), kol, "polysk", faza=0.02)
        else:
            p.blok("Klejnot", (0, 0, 0), (2.8, 2.8, 1.0), kolory[0], "polysk")
            p.blok("Faseta", (-0.3, 0.3, 0.52), (1.5, 1.5, 0.12), kolory[1], "polysk", faza=0.02)
        for a in range(4):
            p.blok("Oprawa", (1.62 * math.cos(math.radians(a * 90)), 1.62 * math.sin(math.radians(a * 90)), 0), (0.44, 3.68, 1.2) if a % 2 == 0
                   else (3.68, 0.44, 1.2), "E09A1A" if a < 2 else ZO, "metal", faza=0.06)
    p.blok("Blysk", (-0.5, 0.9, 0.66), (0.5, 0.5, 0.08), "FFFFFF", "swiecacy", rot=(0, 0, 45), faza=0.0)
    return p


def m_korona():
    p = _m("korona", 0.08)
    p.walec("Obrecz", (0, 0, 0), (3.6, 1.1, 3.6), ZO, "metal", segm=8)
    p.walec("Zar", (0, -0.5, 0), (3.8, 0.24, 3.8), "FF7A2A", "swiecacy", segm=8)
    for i in range(6):
        a = math.radians(i * 60 + 30)
        p.klin("Zab korony", (1.55 * math.sin(a), 1.2, 1.55 * math.cos(a)), (0.8, 1.5, 0.5), "FFE680", "metal",
               rot=(0, math.degrees(a) + 180, 0), faza=0.02)
        if i % 2 == 0:
            p.blok("Rubin", (1.84 * math.sin(a), 0.0, 1.84 * math.cos(a)), (0.6, 0.6, 0.2), "FF3D6A", "swiecacy",
                   rot=(0, math.degrees(a), 45), faza=0.0)
    return p


def m_szczeka():
    p = _m("szczeka")
    p.blok("Zuchwa", (0, -0.4, 0.4), (3.2, 1.0, 3.4), "EDE4CF")
    p.blok("Zuchwa tyl", (0, 0.5, -1.5), (3.2, 1.9, 0.9), "CFC3A8", rot=(-14, 0, 0))
    for x, z, h in ((-1.25, 1.6, 1.5), (1.25, 1.6, 1.5), (-1.3, 0.5, 0.9), (1.3, 0.5, 0.9), (-0.45, 1.85, 0.8), (0.45, 1.85, 0.8)):
        p.klin("Zab", (x, 0.1 + h / 2, z), (0.5, h, 0.6), BI, "polysk", rot=(0, 180, 0), faza=0.02)
    p.blok("Zar", (0, 0.12, 0.3), (2.2, 0.1, 2.2), "FF7A2A", "swiecacy", faza=0.0)
    return p


def m_blyskawica():
    p = _m("blyskawica", 0.06)
    for x, y, rz, dl in ((0.5, 1.5, -24, 2.4), (0.0, 0.0, 62, 2.0), (-0.5, -1.5, -24, 2.6)):
        p.blok("Blysk", (x, y, 0), (1.0, dl, 0.7), "FFE14D", "swiecacy", rot=(0, 0, rz))
    for y, dl in ((1.0, 1.3), (-0.2, 1.8), (-1.3, 1.1)):
        p.blok("Ped", (-2.6, y, 0), (dl, 0.26, 0.3), "7FE9FF", "swiecacy", faza=0.0)
    return p


def m_mieso():
    p = _m("mieso", 0.3)
    p.blok("Mieso", (0.4, 0.3, 0), (2.8, 2.4, 2.2), "C9603A", rot=(0, 0, 30))
    p.blok("Mieso 2", (1.3, 1.1, 0), (1.9, 1.7, 1.9), "E07A4A", rot=(0, 0, 30))
    p.blok("Kosc", (-1.6, -1.2, 0), (2.4, 0.6, 0.6), "FFF6E0", rot=(0, 0, 38), faza=0.1)
    for dx, dy in ((-0.5, 0.2), (0.1, -0.5)):
        p.kula("Kosc koniec", (-2.5 + dx, -1.9 + dy, 0), 0.9, "FFF6E0", segm=8)
    p.blok("Zar", (1.7, 1.6, 1.0), (0.5, 0.5, 0.1), "FFD23F", "swiecacy", rot=(0, 0, 45), faza=0.0)
    return p


# id ikony: (opis, [modele sceny: (id modelu, pozycja, obrót)], kierunek kamery, kolor poświaty albo None)
IKONY = (
    ("bite", "BITE", [("ik_bite", (0, 0, 0), 0)], (-0.85, 0.2, 0.5), None),
    ("dash", "DASH", [("ik_dash", (0, 0, 0), 0)], (0.0, 0.05, 1.0), (127, 233, 255)),
    ("ember_spit", "EMBER SPIT", [("ik_ember", (0, 0, 0), 0)], (0.0, 0.05, 1.0), (255, 150, 40)),
    ("fire_breath", "FIRE BREATH", [("ik_bite", (-3.0, 0, 0), 90), ("ogien", (0.2, 0, 0), 90)], (0.0, 0.12, 1.0), (255, 150, 40)),
    ("inferno_breath", "INFERNO BREATH", [("ik_inferno", (0, 0, 0), 0)], (0.2, 0.5, 1.0), (255, 110, 40)),
    ("tail_sweep", "TAIL SWEEP", [("ik_tail", (0, 0, 0), 0)], (0.0, 1.0, 0.45), (127, 233, 255)),
    ("wing_glide", "WING GLIDE", [("ik_wing", (0, 0, 0), 0)], (0.0, 1.0, 0.3), (127, 233, 255)),
    ("roar", "ROAR", [("ik_roar", (0, 0, 0), 0)], (-0.9, 0.12, 0.35), (255, 210, 90)),
    ("meteor_dive", "METEOR DIVE", [("ik_meteor", (0, 0, 0), 0)], (0.0, 0.05, 1.0), (255, 130, 40)),
    ("zablokowane", "locked ability", [("ik_klodka", (0, 0, 0), 0)], (0.3, 0.12, 1.0), None),
    ("moneta", "gold coin", [("ik_moneta", (0, 0, 0), 0)], (0.4, 0.2, 1.0), (255, 220, 90)),
    ("skarb", "hoard", [("stos_zlota_2", (0, 0, 0), 0)], (0.5, 0.5, 1.0), (255, 220, 90)),
    ("kula_mala", "orb small", [("kula_mala", (0, 0, 0), 0)], (0.4, 0.5, 1.0), (255, 225, 77)),
    ("kula_duza", "orb big", [("kula_duza", (0, 0, 0), 0)], (0.4, 0.5, 1.0), (79, 208, 255)),
    ("kula_wielka", "orb great", [("kula_wielka", (0, 0, 0), 0)], (0.4, 0.5, 1.0), (255, 77, 216)),
    ("wariant_gold", "variant GOLD", [("ik_w_gold", (0, 0, 0), 0)], (0.25, 0.1, 1.0), (255, 220, 90)),
    ("wariant_crystal", "variant CRYSTAL", [("ik_w_crystal", (0, 0, 0), 0)], (0.25, 0.1, 1.0), (127, 233, 255)),
    ("wariant_ruby", "variant RUBY", [("ik_w_ruby", (0, 0, 0), 0)], (0.25, 0.1, 1.0), (255, 61, 106)),
    ("wariant_rainbow", "variant RAINBOW", [("ik_w_rainbow", (0, 0, 0), 0)], (0.25, 0.1, 1.0), (255, 255, 255)),
    ("korona", "boss crown", [("ik_korona", (0, 0, 0), 0)], (0.3, 0.4, 1.0), (255, 220, 90)),
    ("ulepszenie_jaw", "upgrade JAW", [("ik_szczeka", (0, 0, 0), 0)], (-0.7, 0.45, 0.7), None),
    ("ulepszenie_speed", "upgrade SPEED", [("ik_blyskawica", (0, 0, 0), 0)], (0.0, 0.05, 1.0), (255, 225, 77)),
    ("ulepszenie_appetite", "upgrade APPETITE", [("ik_mieso", (0, 0, 0), 0)], (0.2, 0.1, 1.0), None),
    ("czaszka", "eaten", [("czaszka_smoka", (0, 0, 0), 0)], (0.8, 0.3, 1.0), None),
)


def modele_ikon():
    ogien = rekwizyty.ogien2(5.6)
    return [m_bite(), m_dash(), m_ember(), m_inferno(), m_tail(), m_wing(), m_roar(), m_meteor(), m_klodka(), m_moneta(),
            m_klejnot("w_gold", ("FFC83D", "FFE680")), m_klejnot("w_crystal", ("7FE9FF", "DFFBFF")),
            m_klejnot("w_ruby", ("FF3D6A", "FF9AB0")), m_klejnot("w_rainbow", ("FF4D5E", "FFB52E", "FFE14D", "35DD8A", "4FA8FF")),
            m_korona(), m_szczeka(), m_blyskawica(), m_mieso(), ogien] + [_bez_blasku(sz.zbuduj(i)) for i in
                                                                          ("stos_zlota_2", "kula_mala", "kula_duza", "kula_wielka", "czaszka_smoka")]


def _bez_blasku(p):
    # Kula jako ikona: bez krążka blasku na ziemi (sam rekwizyt w danych gry zostaje bez zmian)
    p.czesci = [c for c in p.czesci if c["n"] != "Blask na ziemi"]
    return p


# --------------------------------------------------------------------------- wykończenie i rysowanie (PIL)
def _font(r, tytul=False):
    for n in (("COOPBL.TTF",) if tytul else ()) + ("ARLRDBD.TTF", "seguibl.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(n, int(r))
        except OSError:
            continue
    return ImageFont.load_default()


def wykoncz(sciezka, rozmiar=256, wypelnienie=0.78, obrys=7, poswiata=None, sylwetka=False, medalion=False):
    """Render z przezroczystym tłem -> ikona: postać dopasowana do pola, gruby ciemny obrys, cień, opcjonalna poświata."""
    im = Image.open(sciezka).convert("RGBA")
    if medalion:                                               # popiersie: ucięcia kadru zaokrąglone elipsą
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).ellipse((6, 6, im.width - 6, im.height - 6), fill=255)
        im.putalpha(ImageChops.multiply(im.getchannel("A"), m))
    im = im.crop(im.getchannel("A").getbbox())
    k = rozmiar * wypelnienie / max(im.size)
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    if sylwetka:
        czarny = Image.new("RGBA", im.size, (22, 14, 34, 255))
        czarny.putalpha(im.getchannel("A"))
        im = czarny
    pole = Image.new("RGBA", (rozmiar, rozmiar), (0, 0, 0, 0))
    x, y = (rozmiar - im.width) // 2, (rozmiar - im.height) // 2
    a = Image.new("L", (rozmiar, rozmiar), 0)
    a.paste(im.getchannel("A"), (x, y))
    gruby = a.filter(ImageFilter.MaxFilter(2 * obrys + 1))
    if poswiata:
        blask = a.filter(ImageFilter.MaxFilter(2 * obrys + 9)).filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.8))
        pole.paste(Image.new("RGBA", pole.size, tuple(poswiata) + (255,)), (0, 0), blask)
    pole.paste(Image.new("RGBA", pole.size, (10, 6, 18, 255)), (0, 5), gruby.point(lambda v: int(v * 0.45)))
    pole.paste(Image.new("RGBA", pole.size, K["obrys"] + (255,)), (0, 0), gruby)
    pole.alpha_composite(im, (x, y))
    return pole


def _warstwa(im):
    return Image.new("RGBA", im.size, (0, 0, 0, 0))


def ksztalt(im, box, rad, kolor, obrys=4, cien=5, alfa=255, kolor_obrysu=None):
    """Zaokrąglony prostokąt (albo koło, gdy rad = None) z obrysem i miękkim cieniem pod spodem."""
    w = _warstwa(im)
    d = ImageDraw.Draw(w)
    rys = (lambda b, **kw: d.ellipse(b, **kw)) if rad is None else (lambda b, **kw: d.rounded_rectangle(b, radius=rad, **kw))
    if cien:
        s = _warstwa(im)
        ds = ImageDraw.Draw(s)
        b2 = (box[0], box[1] + cien, box[2], box[3] + cien)
        (ds.ellipse if rad is None else (lambda b, **kw: ds.rounded_rectangle(b, radius=rad, **kw)))(b2, fill=(8, 4, 16, 110))
        im.alpha_composite(s.filter(ImageFilter.GaussianBlur(4)))
    rys(box, fill=tuple(kolor) + (alfa,), outline=tuple(kolor_obrysu or K["obrys"]) + (255,) if obrys else None, width=obrys)
    im.alpha_composite(w)


def tekst(im, xy, s, r, kolor=None, obrys=3, kotwica="la", tytul=False):
    ImageDraw.Draw(im).text(xy, s, font=_font(r, tytul), fill=tuple(kolor or K["tekst"]), stroke_width=obrys, stroke_fill=K["obrys"],
                            anchor=kotwica)


def wklej(im, obraz, c, rozmiar):
    o = obraz.resize((int(rozmiar), int(rozmiar)), Image.LANCZOS)
    im.alpha_composite(o, (int(c[0] - rozmiar / 2), int(c[1] - rozmiar / 2)))


def pasek(im, box, ulamek, kolory, rad=None):
    """Pasek postępu: ciemne tło, wypełnienie z gradientem i jasną górną krawędzią."""
    rad = rad if rad is not None else (box[3] - box[1]) // 2
    ksztalt(im, box, rad, K["pas"], obrys=3, cien=3)
    x1 = box[0] + 4 + int((box[2] - box[0] - 8) * ulamek)
    if x1 > box[0] + 10:
        w = _warstwa(im)
        d = ImageDraw.Draw(w)
        d.rounded_rectangle((box[0] + 4, box[1] + 4, x1, box[3] - 4), radius=max(2, rad - 4), fill=tuple(kolory[0]) + (255,))
        d.rounded_rectangle((box[0] + 6, box[1] + 5, x1 - 2, box[1] + 4 + (box[3] - box[1] - 8) // 2), radius=max(2, rad - 5),
                            fill=tuple(kolory[1]) + (255,))
        im.alpha_composite(w)


def przycisk(im, c, r, kolor, ikona, odnowa=0.0, zablokowany=False, napis=None):
    """Okrągły przycisk akcji: płytka w kolorze linii, obrys, połysk, ikona; odnowa = wycinek zegara; zablokowany = kłódka."""
    plyt = (70, 60, 88) if zablokowany else kolor
    ksztalt(im, (c[0] - r, c[1] - r, c[0] + r, c[1] + r), None, plyt, obrys=5, cien=6)
    w = _warstwa(im)
    d = ImageDraw.Draw(w)
    d.ellipse((c[0] - r + 7, c[1] - r + 7, c[0] + r - 7, c[1] + r - 7), outline=(255, 255, 255, 70), width=3)
    d.pieslice((c[0] - r + 8, c[1] - r + 8, c[0] + r - 8, c[1] + r - 8), 200, 340, fill=(255, 255, 255, 34))
    im.alpha_composite(w)
    wklej(im, ikona, c, r * 1.62)
    if odnowa > 0:
        w = _warstwa(im)
        ImageDraw.Draw(w).pieslice((c[0] - r + 5, c[1] - r + 5, c[0] + r - 5, c[1] + r - 5), -90, -90 + 360 * odnowa, fill=(16, 10, 28, 170))
        im.alpha_composite(w)
        tekst(im, c, napis or "2", r * 0.8, kotwica="mm")


def kolo_portretu(im, c, r, obraz, tlo=(62, 50, 80), ring=None, skala=1.9):
    ksztalt(im, (c[0] - r, c[1] - r, c[0] + r, c[1] + r), None, tlo, obrys=4, cien=4, kolor_obrysu=ring)
    maska = Image.new("L", im.size, 0)
    ImageDraw.Draw(maska).ellipse((c[0] - r + 4, c[1] - r + 4, c[0] + r - 4, c[1] + r - 4), fill=255)
    w = _warstwa(im)
    wklej(w, obraz, c, r * skala)
    w.putalpha(Image.composite(w.getchannel("A"), Image.new("L", im.size, 0), maska))
    im.alpha_composite(w)


def pigulka(im, xy, s, r=15, kolor=None, tlo=None, kotwica="mm", ikona=None):
    f = _font(r)
    szer = int(ImageDraw.Draw(im).textlength(s, font=f)) + 26 + (r * 2 if ikona is not None else 0)
    x0 = xy[0] - szer // 2 if kotwica == "mm" else xy[0]
    ksztalt(im, (x0, xy[1] - r - 3, x0 + szer, xy[1] + r + 5), r + 4, tlo or K["panel"], obrys=3, cien=3, alfa=235)
    if ikona is not None:
        wklej(im, ikona, (x0 + r + 8, xy[1] + 1), r * 2.3)
    tekst(im, (x0 + 13 + (r * 2 if ikona is not None else 0), xy[1] + 1), s, r, kolor, obrys=0, kotwica="lm")
    return szer


# --------------------------------------------------------------------------- całość
def zrob(g):
    """g = moduł generuj. Renderuje bryły ikon i portrety, składa ikony, sylwetki, arkusze i trzy makiety."""
    from swiat.ewolucja.modele import sprawdz_dane as sd
    rob = g.wyjscie("interfejs_robocze")
    cel = {n: g.wyjscie("interfejs", n) for n in ("ikony", "portrety", "makiety")}
    smoki = g.modele_pelne()                                   # 8 stadiów + jajo
    zad = [{"typ": "scena", "plik": "ik_%s.png" % i, "rozmiar": [512, 512], "orto": True, "kierunek": list(kier), "margines": 1.04,
            "modele": [{"id": m, "poz": list(poz), "obrot_y": ob} for m, poz, ob in mod]} for i, _, mod, kier, _ in IKONY]
    for n in range(1, 9):                                       # portret: kadr na głowę, szyję i pierś (zaczepy z danych gry)
        rig = sd.wczytaj("smok_%d_rig.json" % n)
        sw = sd.poza(rig, None, 0)
        pk = [sd.punkt_zaczepu(rig, sw, z) for z in ("GlowaAttachment", "PyskAttachment", "PiersAttachment", "Zar1Attachment")]
        pk = [(-x, y, -z) for x, y, z in pk]
        dl = max(math.dist(pk[0], q) for q in pk[1:])
        kadr = pk + [(pk[0][0] + s * dl * 0.42, pk[0][1] + dl * 0.2, pk[0][2]) for s in (1, -1)]
        zad.append({"typ": "scena", "plik": "po_%d.png" % n, "rozmiar": [512, 512], "orto": True, "kierunek": [0.6, 0.14, 1.0],
                    "margines": 1.12, "kadr_punkty": [list(q) for q in kadr], "modele": [{"id": "smok_%d" % n}]})
    ryk = next(k for k in smoki[5].klipy if k.nazwa == "ryk")
    zad.append({"typ": "scena", "plik": "odslona_smok.png", "rozmiar": [900, 900], "kierunek": [0.5, 0.16, 1.0],
                "modele": [{"id": "smok_6", "poza": ["ryk", ryk.dlugosc // 2]}]})
    zad.append({"typ": "scena", "plik": "odslona_jajo.png", "rozmiar": [500, 500], "kierunek": [0.5, 0.2, 1.0], "modele": [{"id": "smok_jajo"}]})
    g.widoki(smoki + modele_ikon(), zad, rob, "interfejs: ikony i portrety (%d scen)" % len(zad))

    ik = {}
    for i, _, _, _, blask in IKONY:
        ik[i] = wykoncz(os.path.join(rob, "ik_%s.png" % i), poswiata=blask)
        ik[i].save(os.path.join(cel["ikony"], "%s.png" % i))
    por, syl = {}, {}
    for n in range(1, 9):
        por[n] = wykoncz(os.path.join(rob, "po_%d.png" % n), wypelnienie=0.86, obrys=6, medalion=True)
        syl[n] = wykoncz(os.path.join(rob, "po_%d.png" % n), wypelnienie=0.86, obrys=6, sylwetka=True, medalion=True)
        por[n].save(os.path.join(cel["portrety"], "stadium_%d.png" % n))
        syl[n].save(os.path.join(cel["portrety"], "stadium_%d_sylwetka.png" % n))

    # ---- arkusze: ikony (256 i 64 px na jasnym i ciemnym tle) i portrety
    kol, kom = 8, 150
    ark = Image.new("RGBA", (kol * kom, 3 * (kom + 22) + 96), (36, 28, 48, 255))
    d = ImageDraw.Draw(ark)
    for nr, (i, opis, _, _, _) in enumerate(IKONY):
        x, y = (nr % kol) * kom, (nr // kol) * (kom + 22)
        wklej(ark, ik[i], (x + kom // 2, y + kom // 2), kom - 8)
        d.text((x + kom // 2, y + kom + 2), opis, font=_font(12), fill=(230, 224, 240), anchor="ma")
    y64 = 3 * (kom + 22) + 8
    d.rectangle((0, y64 + 40, ark.width, ark.height), fill=(124, 190, 100, 255))        # dolna połowa na tle łąki
    for nr, (i, _, _, _, _) in enumerate(IKONY):
        wklej(ark, ik[i], (44 + nr * 48, y64 + 24 + (42 if nr % 2 else 0)), 64 if nr % 2 == 0 else 44)
    ark.convert("RGB").save(os.path.join(g.PODGLAD, "21_ikony.jpg"), quality=86)
    ark = Image.new("RGBA", (8 * 180, 2 * 180 + 30), (36, 28, 48, 255))
    for n in range(1, 9):
        wklej(ark, por[n], ((n - 1) * 180 + 90, 90), 172)
        wklej(ark, syl[n], ((n - 1) * 180 + 90, 270), 172)
        ImageDraw.Draw(ark).text(((n - 1) * 180 + 90, 362), NAZWY[n - 1], font=_font(14), fill=(230, 224, 240), anchor="ma")
    ark.convert("RGB").save(os.path.join(g.PODGLAD, "22_portrety.jpg"), quality=86)

    tlo_gry = Image.open(os.path.join(g.wyjscie("mapa"), "mapa_kamera_gry.png")).convert("RGBA").resize((1280, 720), Image.LANCZOS)
    tlo_gry = tlo_gry.crop((0, 65, 1280, 655))

    # ---- makieta 1: HUD na telefonie (1280 × 590 px = 844 × 390 pt; 44 pt = 67 px)
    im = tlo_gry.copy()
    kolo_portretu(im, (398, 56), 40, por[5], ring=K["zar_j"])
    tekst(im, (448, 14), "DRAGON", 26, tytul=False)
    tekst(im, (884, 20), "STAGE 5 / 8", 15, K["tekst2"], kotwica="ra")
    pasek(im, (446, 46, 884, 74), 0.62, (K["zar"], K["zar_j"]))
    tekst(im, (665, 60), "620 / 1000", 15, kotwica="mm")
    kolo_portretu(im, (912, 60), 24, syl[6], tlo=K["pas"])
    tekst(im, (912, 60), "?", 22, K["zar_j"], kotwica="mm")
    pasek(im, (446, 80, 760, 98), 0.8, (K["hp"], (255, 154, 168)))
    tekst(im, (458, 89), "HP", 12, kotwica="lm")
    pigulka(im, (960, 34), "12 450", 16, tlo=K["panel"], kotwica="la", ikona=ik["moneta"])
    pigulka(im, (960, 78), "+36 / s", 16, K["zar_j"], tlo=K["panel"], kotwica="la", ikona=ik["skarb"])
    # drabina ewolucji po lewej: zdobyte stadia, obecne większe, następne jako sylwetka, dalsze jako kropki
    ys = [414 - i * 42 for i in range(8)]
    w = _warstwa(im)
    ImageDraw.Draw(w).line((58, ys[7], 58, ys[0]), fill=K["obrys"] + (255,), width=12)
    ImageDraw.Draw(w).line((58, ys[4], 58, ys[0]), fill=K["zar"] + (255,), width=6)
    im.alpha_composite(w)
    for i in range(8):
        if i < 4:
            kolo_portretu(im, (58, ys[i]), 18, por[i + 1])
        elif i == 4:
            kolo_portretu(im, (58, ys[i]), 27, por[5], ring=K["zar_j"])
            pigulka(im, (94, ys[i]), "DRAGON", 13, kotwica="la")
        elif i == 5:
            kolo_portretu(im, (58, ys[i]), 21, syl[6], tlo=K["pas"])
            tekst(im, (58, ys[i]), "?", 20, K["zar_j"], kotwica="mm")
        else:
            ksztalt(im, (48, ys[i] - 10, 68, ys[i] + 10), None, K["pas"], obrys=3, cien=2)
    # drążek (podpowiedź) po lewej na dole
    w = _warstwa(im)
    d = ImageDraw.Draw(w)
    d.ellipse((96, 392, 244, 540), fill=(255, 255, 255, 46), outline=(255, 255, 255, 150), width=4)
    d.ellipse((160, 430, 226, 496), fill=(255, 255, 255, 170), outline=K["obrys"] + (200,), width=3)
    im.alpha_composite(w)
    # przyciski akcji po prawej na dole: BITE największy, wokół niego łuk
    przycisk(im, (1166, 476), 78, K["kosc"], ik["bite"])
    przycisk(im, (1020, 512), 52, (96, 200, 220), ik["dash"], odnowa=0.62, napis="2")
    przycisk(im, (1056, 378), 52, K["ogien"], ik["fire_breath"])
    przycisk(im, (1170, 318), 52, K["moc"], ik["wing_glide"])
    for (x, y), s in (((1166, 574), "BITE"), ((1020, 578), "DASH")):
        tekst(im, (x, y), s, 14, kotwica="ms")
    pigulka(im, (1010, 312), "INFERNO at ANCIENT", 12, K["tekst2"], ikona=ik["zablokowane"])
    pigulka(im, (1160, 250), "ROAR at WAR DRAGON", 12, K["tekst2"], ikona=ik["zablokowane"])
    im.convert("RGB").save(os.path.join(cel["makiety"], "hud_telefon_1280x590.png"))
    im.convert("RGB").save(os.path.join(g.PODGLAD, "23_makieta_hud.jpg"), quality=88)

    # ---- makieta 2: panel legowiska (trofea, ulepszenia, szanse wariantów)
    im = Image.alpha_composite(tlo_gry.filter(ImageFilter.GaussianBlur(3)), Image.new("RGBA", tlo_gry.size, (16, 10, 30, 120)))
    ksztalt(im, (110, 34, 1170, 560), 24, K["panel"], obrys=5, cien=8)
    ksztalt(im, (110, 34, 1170, 104), 24, K["pas"], obrys=5, cien=0)
    ImageDraw.Draw(im).rectangle((116, 100, 1164, 106), fill=K["zar"] + (255,))                 # żar pod pasem tytułu
    tekst(im, (140, 69), "YOUR LAIR", 30, kotwica="lm", tytul=True)
    ksztalt(im, (400, 50, 580, 92), 20, K["zar"], obrys=3, cien=2)
    tekst(im, (490, 71), "TROPHIES", 17, kotwica="mm")
    ksztalt(im, (596, 50, 776, 92), 20, K["panel2"], obrys=3, cien=2)
    tekst(im, (686, 71), "UPGRADES", 17, K["tekst2"], kotwica="mm")
    pigulka(im, (960, 71), "12 450", 16, tlo=K["panel2"], ikona=ik["moneta"])
    ksztalt(im, (1104, 48, 1150, 94), None, K["hp"], obrys=4, cien=2)
    tekst(im, (1127, 70), "X", 20, kotwica="mm")
    poziomy, warianty = (5, 4, 3, 3, 2, 0, 0, 0), {1: "wariant_gold", 3: "wariant_crystal", 4: "wariant_ruby"}
    for i in range(8):
        x, y = 134 + (i % 4) * 172, 122 + (i // 4) * 190
        zdobyte = poziomy[i] > 0
        ksztalt(im, (x, y, x + 160, y + 176), 16, K["panel2"] if zdobyte else K["pas"], obrys=4, cien=4)
        wklej(im, por[i + 1] if zdobyte else syl[i + 1], (x + 80, y + 66), 116)
        tekst(im, (x + 80, y + 128), NAZWY[i] if zdobyte else "? ? ?", 13, kotwica="mm")
        if zdobyte:
            for j in range(5):                                  # poziom trofeum: pięć rombów
                cx = x + 44 + j * 18
                ImageDraw.Draw(im).regular_polygon((cx, y + 152, 7), 4, rotation=0, fill=K["zar_j"] if j < poziomy[i] else K["pas"],
                                                   outline=K["obrys"])
            tekst(im, (x + 152, y + 152), "+%d/s" % (3 * poziomy[i] * (i + 1)), 12, K["zielen"], obrys=2, kotwica="rm")
            if i in warianty:
                wklej(im, ik[warianty[i]], (x + 138, y + 22), 52)
        else:
            wklej(im, ik["zablokowane"], (x + 138, y + 22), 44)
    for j, (nazwa, ikona, poz, cena) in enumerate((("JAW", "ulepszenie_jaw", 4, "1 200"), ("SPEED", "ulepszenie_speed", 2, "400"),
                                                    ("APPETITE", "ulepszenie_appetite", 3, "900"))):
        y = 122 + j * 118
        ksztalt(im, (836, y, 1146, y + 104), 16, K["panel2"], obrys=4, cien=4)
        wklej(im, ik[ikona], (884, y + 52), 84)
        tekst(im, (936, y + 12), nazwa, 18)
        tekst(im, (1132, y + 14), "Lv %d" % poz, 14, K["tekst2"], kotwica="ra")
        pasek(im, (936, y + 42, 1132, y + 58), poz / 6.0, (K["krysztal"], (220, 252, 255)))
        ksztalt(im, (1010, y + 66, 1132, y + 96), 15, K["zielen"], obrys=3, cien=2)
        wklej(im, ik["moneta"], (1030, y + 81), 30)
        tekst(im, (1084, y + 81), cena, 15, kotwica="mm")
    ksztalt(im, (134, 506, 1146, 546), 20, K["pas"], obrys=3, cien=0)
    tekst(im, (154, 526), "VARIANT ODDS", 14, K["tekst2"], kotwica="lm")
    for j, (ikona, s) in enumerate((("wariant_gold", "GOLD 8%  x2"), ("wariant_crystal", "CRYSTAL 3%  x4"), ("wariant_ruby", "RUBY 1%  x8"),
                                    ("wariant_rainbow", "RAINBOW 0.2%  x20"))):
        wklej(im, ik[ikona], (316 + j * 212, 526), 38)
        tekst(im, (338 + j * 212, 526), s, 14, kotwica="lm")
    im.convert("RGB").save(os.path.join(cel["makiety"], "panel_legowiska_1280x590.png"))
    im.convert("RGB").save(os.path.join(g.PODGLAD, "24_makieta_legowisko.jpg"), quality=88)

    # ---- makieta 3: odsłona ewolucji (blask kokonu -> nowe stadium, tabliczka z nazwą i tym, co odblokowuje)
    im = Image.alpha_composite(tlo_gry.filter(ImageFilter.GaussianBlur(5)), Image.new("RGBA", tlo_gry.size, (16, 8, 34, 170)))
    promienie = og.tlo(1280, 590, (0.5, 0.52), ((255, 236, 150), (255, 140, 60), (40, 16, 60)), promienie=22, sila=50).convert("RGBA")
    promienie.putalpha(Image.radial_gradient("L").resize((1280, 590)).point(lambda v: max(0, 255 - int(v * 1.5))))
    im.alpha_composite(promienie)
    jajo = og.wytnij(os.path.join(rob, "odslona_jajo.png"), wys=150)
    biale = Image.new("RGBA", jajo.size, (255, 244, 190, 255))
    biale.putalpha(jajo.getchannel("A"))
    im.alpha_composite(og.naklejka(biale, 8, (255, 210, 90)).filter(ImageFilter.GaussianBlur(1)), (250, 250))
    for j in range(3):
        tekst(im, (424 + j * 28, 330), ">", 34, K["zar_j"], kotwica="mm")
    smok = og.naklejka(og.wytnij(os.path.join(rob, "odslona_smok.png"), wys=330), 6)
    im.alpha_composite(smok, (640 - smok.width // 2 + 96, 120))
    tekst(im, (640, 56), "EVOLVED!", 22, K["zar_j"], kotwica="mm")
    napis = og.litery("WAR DRAGON", 78)
    im.alpha_composite(napis, (640 - napis.width // 2, 64))
    ksztalt(im, (400, 468, 880, 528), 30, K["panel"], obrys=4, cien=6)
    wklej(im, ik["roar"], (446, 498), 74)
    tekst(im, (494, 484), "NEW POWER", 13, K["tekst2"], obrys=0)
    tekst(im, (494, 500), "ROAR  -  stun everyone near you", 17, obrys=0)
    kolo_portretu(im, (960, 498), 30, syl[7], tlo=K["pas"])
    tekst(im, (960, 498), "?", 24, K["zar_j"], kotwica="mm")
    tekst(im, (1000, 498), "NEXT", 13, K["tekst2"], kotwica="lm")
    ksztalt(im, (560, 540, 720, 580), 20, K["zar"], obrys=4, cien=3)
    tekst(im, (640, 560), "CONTINUE", 17, kotwica="mm")
    im.convert("RGB").save(os.path.join(cel["makiety"], "odslona_ewolucji_1280x590.png"))
    im.convert("RGB").save(os.path.join(g.PODGLAD, "25_makieta_ewolucja.jpg"), quality=88)
    print("INTERFEJS | %d ikon, 8 portretów + 8 sylwetek, 3 makiety w folderze wyników: interfejs; podglądy 21–25" % len(IKONY))
