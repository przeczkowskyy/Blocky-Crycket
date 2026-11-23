# -*- coding: utf-8 -*-
"""Propozycja mapy świata: rozstawienie zestawu (swiat_zestaw.py) na łące, w lesie, w legowiskach, na wyspie lawy
i nad wodą, z licznikiem części, oraz rendery: z góry i z kamery gry.

Układ GRY (jak w ustawienia.json): początek = środek łąki, DEEP WOODS w +Z (0, 240), jednostka = stud, obrót wokół
pionu w stopniach (CFrame.Angles(0, rad(obrot), 0)); rekwizyt patrzy przodem (−Z rigu) w kierunku (−sin, −cos) obrotu.
Do Blendera układ zamienia się na układ biblioteki (x, z) -> (−x, −z), obrót bez zmian.

    python -B swiat/ewolucja/modele/generuj.py mapa      # dane/mapa_propozycja.json + rendery + plansza zestawu
"""
import math
import os
import random

from swiat.ewolucja.modele import smok_model as sm
from swiat.ewolucja.modele import swiat_zestaw as sz

LAKA_R, LAS, LAS_R = 150.0, (0.0, 240.0), 115.0
WYSPA, WYSPA_R, JEZIORO_R = (-250.0, 70.0), 42.0, 80.0
STAWY = (((55.0, 38.0), 16.0), ((-62.0, -60.0), 11.0))
LEGOWISKA = [(126.0 * math.sin(math.radians(a)), 126.0 * math.cos(math.radians(a)))
             for a in (42 + i * 276.0 / 11 for i in range(12))]
SZABLON_LEGOWISKA = (("legowisko_krag", 0.0, 0.0, 0.0), ("legowisko_brama", 0.0, 16.5, 0.0), ("sztandar", 8.5, 17.0, 0.0))
ZNAKI = (("czaszka_smoka", -60.0, 44.0, 150.0, 1.0), ("posag_prastarego", 0.0, 300.0, 0.0, 1.0),
         ("brama_zapieczetowana", 176.0, -24.0, 82.0, 1.0), ("krag_kamienny", 46.0, 214.0, 0.0, 1.0),
         ("oltarz_kul", WYSPA[0], WYSPA[1], 0.0, 1.0), ("luk_korzeni", 0.0, 131.0, 0.0, 1.3))


def _obrot_ku(dx, dz):
    """Obrót, przy którym przód rekwizytu patrzy w kierunku (dx, dz) układu gry."""
    return math.degrees(math.atan2(-dx, -dz))


def uklad(ziarno=7):
    """{id: [(x, z, obrot, skala), …]} w układzie gry — deterministycznie."""
    los = random.Random(ziarno)
    inst = {}
    zakazy = [(x, z, 21.0) for x, z in LEGOWISKA] + [(c[0], c[1], r + 3) for c, r in STAWY] + \
             [(x, z, 16.0) for _, x, z, _, _ in ZNAKI] + [(0.0, 140.0, 12.0)]

    def wolne(x, z):
        return all(math.hypot(x - a, z - b) > r for a, b, r in zakazy)

    def kepy(id, ile_kep, w_kepie, srodek, r0, r1, rozrzut):
        # Drobiazg w kępach (kwietniki, zarośla trawy): bogato tam, gdzie patrzy gracz, pusto pomiędzy.
        for _ in range(ile_kep):
            a, rr = math.radians(los.uniform(0, 360)), math.sqrt(los.uniform(r0 * r0, r1 * r1))
            cx, cz = srodek[0] + rr * math.sin(a), srodek[1] + rr * math.cos(a)
            if not wolne(cx, cz):
                continue
            for _ in range(w_kepie):
                b, d = math.radians(los.uniform(0, 360)), los.uniform(0.6, rozrzut)
                inst.setdefault(id, []).append((round(cx + d * math.sin(b), 1), round(cz + d * math.cos(b), 1),
                                                round(los.uniform(0, 360)), round(los.uniform(0.85, 1.25), 2)))

    def siej(id, n, srodek, r0, r1, skale=(0.85, 1.2), kat=None, tylko_wolne=True):
        proby = 0
        while n > 0 and proby < 4000:
            proby += 1
            a = math.radians(los.uniform(*kat) if kat else los.uniform(0, 360))
            rr = math.sqrt(los.uniform(r0 * r0, r1 * r1))
            x, z = srodek[0] + rr * math.sin(a), srodek[1] + rr * math.cos(a)
            if tylko_wolne and not wolne(x, z):
                continue
            inst.setdefault(id, []).append((round(x, 1), round(z, 1), round(los.uniform(0, 360)), round(los.uniform(*skale), 2)))
            n -= 1

    # --- łąka (koło 150): dużo drobiazgu przy ziemi, drzewa głównie za murem
    siej("trawa_1", 110, (0, 0), 0, 146)
    kepy("trawa_2", 16, 5, (0, 0), 0, 142, 5.0)
    for k in ("czerwony", "zolty", "niebieski", "bialy"):
        kepy("kwiat_" + k, 4, 6, (0, 0), 8, 140, 4.5)
    for kat in range(0, 360, 9):                                # skalne obrzeże łąki z przerwami na bramy
        if min(abs((kat - b + 180) % 360 - 180) for b in (0, 98, 286)) < 13:
            continue
        x, z = 158.0 * math.sin(math.radians(kat)), 158.0 * math.cos(math.radians(kat))
        inst.setdefault("sciana_skalna", []).append((round(x, 1), round(z, 1), round(_obrot_ku(-x, -z)), round(los.uniform(0.9, 1.15), 2)))
    siej("kamyk", 20, (0, 0), 0, 146)
    siej("glaz_1", 5, (0, 0), 30, 135)
    siej("glaz_2", 3, (0, 0), 40, 130)
    siej("krzak", 20, (0, 0), 95, 146)
    siej("krzak", 10, (0, 0), 10, 95)
    for i, id in enumerate(("drzewo_1", "drzewo_2", "drzewo_3")):
        siej(id, (4, 3, 3)[i], (0, 0), 45, 138, (0.9, 1.15))
        siej(id, (8, 8, 6)[i], (0, 0), 160, 186, (1.0, 1.4), kat=(25, 335), tylko_wolne=False)
    siej("grzyb", 14, (0, 0), 20, 146)
    siej("kloda", 4, (0, 0), 50, 135)
    inst["drogowskaz"] = [(0.0, 120.0, 0, 1.2), (112.0, -14.0, 80, 1.2), (-128.0, 30.0, 290, 1.2)]
    # --- woda: lilie na tafli, trzciny przy brzegu
    for (c, r) in STAWY + ((WYSPA, JEZIORO_R),):
        duzy = r > 40
        siej("lilia", 14 if duzy else 6, c, (WYSPA_R + 6) if duzy else 0, r - 3, tylko_wolne=False)
        siej("trzcina", 14 if duzy else 6, c, r - 1.5, r + 1.5, tylko_wolne=False)
    # --- DEEP WOODS (koło 115 w +Z): ciemne sosny na obwodzie, w środku grzyby, ruiny, łuki
    siej("sosna_1", 5, LAS, 30, 100, (0.9, 1.1))
    siej("sosna_2", 3, LAS, 30, 100, (0.9, 1.1))
    siej("sosna_1", 13, LAS, 118, 140, (1.0, 1.3), kat=(-140, 140), tylko_wolne=False)
    siej("sosna_2", 13, LAS, 118, 142, (1.0, 1.3), kat=(-140, 140), tylko_wolne=False)
    siej("grzyb_wielki", 8, LAS, 20, 105, (0.8, 1.25))
    siej("grzyby_swiecace", 20, LAS, 0, 110)
    siej("luk_korzeni", 3, LAS, 40, 95, (0.9, 1.1))
    siej("filar_ruin", 3, (46.0, 214.0), 14, 22, tylko_wolne=False)
    siej("filar_ruin", 3, (0.0, 300.0), 22, 30, tylko_wolne=False)
    # --- wyspa lawy: słupy bazaltu na brzegu, skały z żarem, ołtarz pośrodku
    siej("bazalt_1", 6, WYSPA, 30, 40, (0.9, 1.3), tylko_wolne=False)
    siej("bazalt_2", 4, WYSPA, 30, 40, (1.0, 1.4), tylko_wolne=False)
    siej("skala_lawy", 12, WYSPA, 12, 36, (0.8, 1.3), tylko_wolne=False)
    # --- legowiska (12 miejsc na obwodzie łąki, otwarte ku środkowi) i punkty charakterystyczne
    for x, z in LEGOWISKA:
        o = _obrot_ku(-x, -z)
        c, s_ = math.cos(math.radians(o)), math.sin(math.radians(o))
        for id, dx, dz, do in SZABLON_LEGOWISKA:               # (dx, dz) w układzie legowiska: +dz = ku środkowi łąki
            fx, fz = dx * c - dz * s_, -dx * s_ - dz * c         # prawo (cos o, −sin o), przód (−sin o, −cos o)
            inst.setdefault(id, []).append((round(x + fx, 1), round(z + fz, 1), round(o + do), 1.0))
    for id, x, z, o, sk in ZNAKI:
        inst.setdefault(id, []).append((x, z, o, sk))
    return inst


def dyski():
    """Płaty ziemi (koła) w układzie gry: (x, z, promień, kolor, wysokość, świeci)."""
    los = random.Random(3)
    d = [(0.0, 110.0, 560.0, "3D7A3A", -0.06, False), (0.0, 0.0, LAKA_R, "5FB04C", 0.0, False),
         (LAS[0], LAS[1], LAS_R, "2B5C44", 0.01, False)]
    for _ in range(16):
        a, rr = los.uniform(0, 6.283), los.uniform(0, 130)
        d.append((rr * math.sin(a), rr * math.cos(a), los.uniform(9, 18), los.choice(("67B652", "58A848")), 0.02, False))
    for _ in range(9):
        a, rr = los.uniform(0, 6.283), los.uniform(0, 95)
        d.append((LAS[0] + rr * math.sin(a), LAS[1] + rr * math.cos(a), los.uniform(9, 16), los.choice(("24503C", "32694C")), 0.03, False))
    d += [(x, z, 13.0, "B9A47C", 0.04, False) for x, z in LEGOWISKA]
    d += [(0.0, 0.0, 17.0, "C7B285", 0.035, False), (0.0, 0.0, 11.0, "B49C6E", 0.04, False)]      # plac pośrodku
    d += [(0.0, 20.0 + 7.5 * i, 3.4, "C7B285", 0.035, False) for i in range(15)]                 # ścieżka do lasu
    d += [(104.0 * math.sin(math.radians(a)), 104.0 * math.cos(math.radians(a)), 3.0, "C7B285", 0.035, False)
          for a in range(44, 320, 7)]                                                           # ścieżka wzdłuż legowisk
    d += [(c[0], c[1], r, "3E8FD8", 0.05, False) for c, r in STAWY]
    d += [(WYSPA[0], WYSPA[1], JEZIORO_R, "3E8FD8", 0.03, False), (WYSPA[0], WYSPA[1], WYSPA_R + 2.5, "FF7A2A", 0.06, True),
          (WYSPA[0], WYSPA[1], WYSPA_R, "37323F", 0.09, False)]
    return d


def policz(inst, czesci):
    """Statyczne części sceny: {strefa: liczba}, razem."""
    strefa = {i: s for i, _, s, _, _ in sz.ZESTAW}
    wyn = {}
    for id, m in inst.items():
        wyn[strefa[id]] = wyn.get(strefa[id], 0) + len(m) * czesci[id]
    return wyn, sum(wyn.values())


def _b(x, z):
    return (-x, -z)                                            # układ gry -> układ biblioteki


def zrob(g):
    """g = moduł generuj. Zapisuje dane/mapa_propozycja.json, renderuje mapę i planszę zestawu."""
    import json
    from PIL import Image, ImageDraw
    from swiat.ewolucja.modele import rekwizyty, stwory
    rob, cel = g.wyjscie("mapa_robocze"), g.wyjscie("mapa")
    zestaw = {m.id: m for m, _, _ in sz.wszystkie()}
    czesci = {i: sm.liczba_czesci_roblox(m) for i, m in zestaw.items()}
    inst = uklad()
    strefy, razem = policz(inst, czesci)
    strefy["platy_ziemi"] = len(dyski())
    razem += len(dyski())
    with open(os.path.join(g.DANE, "mapa_propozycja.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"format": "smok-ewolucji-mapa/1", "uklad": "gra: środek łąki = (0, 0), DEEP WOODS w +Z, studs, obrót w stopniach",
                   "strefy": {"laka_r": LAKA_R, "las": list(LAS) + [LAS_R], "wyspa_lawy": list(WYSPA) + [WYSPA_R],
                              "jezioro_r": JEZIORO_R, "stawy": [list(c) + [r] for c, r in STAWY]},
                   "szablon_legowiska": [list(x) for x in SZABLON_LEGOWISKA],
                   "czesci_rekwizytu": czesci, "czesci_stref": strefy, "czesci_razem": razem,
                   "platy_ziemi": [[round(x, 1), round(z, 1), round(r, 1), k, y, sw] for x, z, r, k, y, sw in dyski()],
                   "instancje": {i: [list(m) for m in v] for i, v in sorted(inst.items())}}, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print("MAPA | części statycznych razem %d: %s" % (razem, ", ".join("%s %d" % kv for kv in sorted(strefy.items()))))

    # ---- scena do renderu: rekwizyty + trochę życia (smoki, owce, kule, cokoły i złoto w jednym legowisku)
    smoki = g.modele_pelne(jajo=False)
    dod = {m.id: m for m in (rekwizyty.cokol(), stwory.owca())}
    lx, lz = LEGOWISKA[11]
    o = _obrot_ku(-lx, -lz)
    zycie = {"cokol": [], "stos_zlota_2": [(lx, lz, o, 1.0)], "kula_mala": [], "kula_duza": [], "kula_wielka": [], "owca": []}
    for i in range(8):                                          # cokoły w łuku pod tylną ścianą legowiska
        a = math.radians(o + 180 - 70 + i * 20)
        zycie["cokol"].append((lx - 9.0 * math.sin(a), lz - 9.0 * math.cos(a), o, 0.42))
    los = random.Random(11)
    for id, n, r0, r1 in (("kula_mala", 60, 0, 140), ("kula_duza", 12, 20, 140), ("owca", 9, 30, 120)):
        for _ in range(n):
            a, rr = los.uniform(0, 6.283), math.sqrt(los.uniform(r0 * r0, r1 * r1))
            zycie[id].append((rr * math.sin(a), rr * math.cos(a), los.uniform(0, 360), 1.0))
    zycie["kula_wielka"] = [(LAS[0] + 30 * math.sin(i), LAS[1] + 40 * math.cos(i * 1.7), 0, 1.0) for i in range(8)] + \
                           [(WYSPA[0], WYSPA[1], 0, 1.0)]
    wszystkie = dict(inst)
    wszystkie.update(zycie)
    instancje = [{"id": i, "m": [[_b(x, z)[0], _b(x, z)[1], ob, sk] for x, z, ob, sk in v]} for i, v in wszystkie.items() if v]
    platy = [{"x": _b(x, z)[0], "z": _b(x, z)[1], "r": r, "kolor": k, "y": y, "swieci": sw} for x, z, r, k, y, sw in dyski()]
    kx, kz = lx * 0.8, lz * 0.8                                # środek kadru kamery gry: przed legowiskiem nr 12

    def smok(nr, x, z, obrot, klip, u):
        k = next(c for c in smoki[nr - 1].klipy if c.nazwa == klip)
        return {"id": "smok_%d" % nr, "poz": [_b(x, z)[0], 0, _b(x, z)[1]], "obrot_y": obrot, "poza": [klip, int(k.dlugosc * u)]}

    aktorzy = [smok(1, kx + 6, kz - 4, o + 150, "chod", 0.2), smok(2, kx - 9, kz + 2, o + 200, "bieg", 0.4),
               smok(3, kx + 16, kz + 10, o + 60, "chod", 0.6), smok(5, lx * 0.86, lz * 0.86, o + 180, "cokol", 0.0),
               smok(4, kx - 22, kz - 14, o + 120, "gryz3", 0.5), smok(1, kx - 2, kz - 16, o + 30, "spoczynek", 0.3),
               smok(8, 20.0, 60.0, 200, "ryk", 0.5)]
    wsp = {"instancje": instancje, "dyski": platy, "modele": []}
    gora = dict(wsp, typ="scena", plik="mapa_gora.png", rozmiar=[1800, 1800], orto=True, kierunek=[0.0, 1.0, 0.0],
                kadr_punkty=[[-210, 0, -395], [340, 0, -395], [-210, 0, 195], [340, 0, 195]], margines=1.0, modele=aktorzy)
    kam = dict(wsp, typ="scena", plik="mapa_kamera.png", rozmiar=[1920, 1080], kierunek=[0.0, 0.848, 0.53], ogniskowa=38,
               kadr_punkty=[[_b(kx, kz)[0] + dx, y, _b(kx, kz)[1] + dz] for dx in (-36, 36) for dz in (-26, 26) for y in (0, 12)],
               margines=1.0, modele=aktorzy)
    plansza = [{"typ": "widoki", "model": i, "widoki": {"p": g.BOHATER}, "rozmiar": 240, "przyrostek": ""} for i in zestaw]
    g.widoki(list(zestaw.values()) + list(dod.values()) + smoki, [gora, kam] + plansza, rob, "mapa i plansza zestawu")

    im = Image.open(os.path.join(rob, "mapa_gora.png")).convert("RGB").rotate(180)       # las u góry
    d = ImageDraw.Draw(im)
    f = g._czcionka(30, True)
    for tekst, x, y in (("DEEP WOODS", 590, 130), ("ŁĄKA", 650, 1180), ("WYSPA LAWY", 1340, 790), ("legowiska ×12", 570, 1672)):
        d.text((x, y), tekst, fill=(255, 255, 255), font=f, stroke_width=4, stroke_fill=(20, 16, 28))
    im.save(os.path.join(cel, "mapa_z_gory.png"))
    im.resize((1000, 1000), Image.LANCZOS).save(os.path.join(g.PODGLAD, "17_mapa_z_gory.jpg"), quality=84)
    im = Image.open(os.path.join(rob, "mapa_kamera.png")).convert("RGB")
    im.save(os.path.join(cel, "mapa_kamera_gry.png"))
    im.resize((1280, 720), Image.LANCZOS).save(os.path.join(g.PODGLAD, "18_mapa_kamera_gry.jpg"), quality=84)
    # plansza zestawu: komórka 240 px + podpis „id · części”
    ids = list(zestaw)
    kol, kom, pas = 9, 200, 26
    wiersze = (len(ids) + kol - 1) // kol
    ark = Image.new("RGB", (kol * kom, wiersze * (kom + pas)), (27, 22, 37))
    d = ImageDraw.Draw(ark)
    f = g._czcionka(14)
    for n, i in enumerate(ids):
        x, y = (n % kol) * kom, (n // kol) * (kom + pas)
        ark.paste(Image.open(os.path.join(rob, "%s_p.jpg" % i)).convert("RGB").resize((kom, kom), Image.LANCZOS), (x, y))
        d.text((x + 5, y + kom + 4), "%s · %d" % (i, czesci[i]), fill=(235, 230, 245), font=f)
    ark.save(os.path.join(g.PODGLAD, "19_zestaw_swiata.jpg"), quality=84)
    print("MAPA | mapa_z_gory.png, mapa_kamera_gry.png w folderze wyników: mapa; podglądy 17–19")
    return inst, czesci, strefy, razem
