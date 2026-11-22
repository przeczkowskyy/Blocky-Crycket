#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smok ewolucji: jedno polecenie odtwarza wszystko (dane dla gry, podglądy, eksporty).

    python -B swiat/ewolucja/modele/generuj.py wszystko      # dane + podglądy + eksport FBX/GLB (kilkanaście minut)
    python -B swiat/ewolucja/modele/generuj.py dane          # dane/ : rig z części Roblox + próbki klipów (Blender w tle)
    python -B swiat/ewolucja/modele/generuj.py podglady      # podglad/*.jpg (plansze, rząd stadiów, paski klatek)
    python -B swiat/ewolucja/modele/generuj.py styl          # plansza trzech kierunków stylu
    python -B swiat/ewolucja/modele/generuj.py eksport       # FBX/GLB/.blend przez bibliotekę — POZA repozytorium
    python -B swiat/ewolucja/modele/generuj.py filmy [klipy] # filmy MP4 klipów stadiów 1, 4, 8 — POZA repozytorium
    python -B swiat/ewolucja/modele/generuj.py licz          # liczba części i klipów (bez Blendera)

Duże pliki (rendery, filmy, .blend, FBX/GLB, tekstury) trafiają do %LOCALAPPDATA%/BlockyCrycket/modele/smok_ewolucja/.
Blender startuje tylko pod wspólną blokadą biblioteki (swiat/biblioteka/podglad.py). Niczego nie wgrywa do Roblox.
"""
import json
import os
import subprocess
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TU)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.biblioteka.podglad import blender_exe, zajmij_blender, zwolnij_blender  # noqa: E402
from swiat.postacie.biblioteka.postac import pakiet, pudelko, zapisz_json  # noqa: E402
from swiat.postacie.biblioteka import roblox_klocki as rk  # noqa: E402
from swiat.ewolucja.modele import smok_model as sm  # noqa: E402
from swiat.ewolucja.modele import smok_klipy as sk  # noqa: E402

DANE = os.path.join(TU, "dane")
PODGLAD = os.path.join(TU, "podglad")
BIB = os.path.join(REPO, "swiat", "postacie", "biblioteka")
GRA = (0.0, 0.848, -0.53)             # kamera gry: z tyłu i z góry, nachylenie 58° (ustawienia.json → kamera)
GRA34 = (0.32, 0.80, -0.5)            # kamera gry lekko z boku (żeby było widać bryłę)
BOK = (-1.0, 0.12, 0.0)
BOHATER = (0.55, 0.22, 1.0)
STYLE = (("zabawka", "1. Klockowa zabawka"), ("krysztal", "2. Krysztal z rdzeniem"), ("zar", "3. Zaroluska (nasz)"))


def wyjscie(*czesci):
    root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    p = os.path.join(root, "BlockyCrycket", "modele", "smok_ewolucja", *czesci)
    os.makedirs(p, exist_ok=True)
    return p


def blender(skrypt, argumenty, opis, limit_s=11 * 60):
    """Jedno uruchomienie Blendera w tle pod wspólną blokadą; wypisuje linie „POSTAC |”."""
    polecenie = [blender_exe(), "-b", "--factory-startup", "--python-exit-code", "1", "--python", skrypt, "--"] + argumenty
    blokada = zajmij_blender()
    t0 = time.time()
    try:
        r = subprocess.run(polecenie, capture_output=True, timeout=limit_s,
                           creationflags=0x08000000 if os.name == "nt" else 0)
    finally:
        zwolnij_blender(blokada)
    wyj = (r.stdout + r.stderr).decode("utf-8", "replace")
    for linia in wyj.splitlines():
        if linia.startswith("POSTAC |") and ("UWAGA" in linia or "GOTOWE" in linia or "RZAD" in linia):
            print(linia)
    if r.returncode != 0:
        print("BLENDER | %s: błąd (kod %d). Ostatnie linie:" % (opis, r.returncode))
        for linia in wyj.splitlines()[-25:]:
            print("   ", linia)
        raise SystemExit(1)
    print("BLENDER | %s: %.0f s" % (opis, time.time() - t0))


def widoki(modele, zadania, folder, opis):
    """Modele (Postac) + lista zadań blender_widoki.py -> pliki JPG w `folder`."""
    for m in modele:
        b, u = m.sprawdz()
        for x in b:
            raise SystemExit("BŁĄD danych: " + x)
    pj, zj = os.path.join(folder, "_pakiet.json"), os.path.join(folder, "_zadania.json")
    zapisz_json(pakiet(modele), pj)
    with open(zj, "w", encoding="utf-8") as f:
        json.dump(zadania, f)
    blender(os.path.join(TU, "blender_widoki.py"), [pj, zj, folder], opis)


# --------------------------------------------------------------------------- składanie plansz (PIL)
def _czcionka(rozmiar, gruba=False):
    from PIL import ImageFont
    for nazwa in (("arialbd.ttf", "DejaVuSans-Bold.ttf") if gruba else ("arial.ttf", "DejaVuSans.ttf")):
        try:
            return ImageFont.truetype(nazwa, rozmiar)
        except OSError:
            continue
    return ImageFont.load_default()


def siatka_obrazow(wiersze, cel, tytul=None, etykiety_wierszy=None, etykiety_kolumn=None, kom=420, lewy=0,
                   jakosc=84, tlo=(27, 22, 37), miniatury=None):
    """wiersze: lista list ścieżek (None = pusta komórka). miniatury: {(wiersz, kolumna): rozmiar} — wklejka obrazu
    zmniejszonego do rozmiaru miniatury (sprawdzian czytelności na telefonie)."""
    from PIL import Image, ImageDraw
    kol = max(len(w) for w in wiersze)
    gora = (46 if tytul else 0) + (26 if etykiety_kolumn else 0)
    W, H = lewy + kol * kom, gora + len(wiersze) * kom
    im = Image.new("RGB", (W, H), tlo)
    dr = ImageDraw.Draw(im)
    if tytul:
        dr.text((12, 10), tytul, fill=(255, 255, 255), font=_czcionka(24, True))
    if etykiety_kolumn:
        for c, t in enumerate(etykiety_kolumn):
            dr.text((lewy + c * kom + 8, gora - 24), t, fill=(200, 195, 215), font=_czcionka(16))
    for r, wiersz in enumerate(wiersze):
        for c, sciezka in enumerate(wiersz):
            if not sciezka or not os.path.isfile(sciezka):
                continue
            ob = Image.open(sciezka).convert("RGB")
            if ob.size != (kom, kom):
                ob = ob.resize((kom, kom), Image.LANCZOS)
            im.paste(ob, (lewy + c * kom, gora + r * kom))
            mini = (miniatury or {}).get((r, c))
            if mini:
                m = ob.resize((mini, mini), Image.LANCZOS)
                x0, y0 = lewy + (c + 1) * kom - mini - 6, gora + (r + 1) * kom - mini - 6
                dr.rectangle((x0 - 2, y0 - 2, x0 + mini + 1, y0 + mini + 1), fill=(255, 255, 255))
                im.paste(m, (x0, y0))
        if etykiety_wierszy:
            dr.text((lewy + 8, gora + r * kom + 6), etykiety_wierszy[r], fill=(255, 255, 255), font=_czcionka(20, True),
                    stroke_width=3, stroke_fill=(20, 16, 28))
    for c in range(1, kol):
        dr.line((lewy + c * kom, gora, lewy + c * kom, H), fill=tlo, width=2)
    for r in range(1, len(wiersze)):
        dr.line((0, gora + r * kom, W, gora + r * kom), fill=tlo, width=2)
    os.makedirs(os.path.dirname(cel), exist_ok=True)
    im.save(cel, quality=jakosc, optimize=True)
    print("PLANSZA | %s (%d×%d, %d kB)" % (cel, W, H, os.path.getsize(cel) // 1024))
    return cel


# --------------------------------------------------------------------------- polecenia
def cmd_styl():
    folder = wyjscie("styl")
    modele, zadania = [], []
    for styl, _ in STYLE:
        for nr in (1, 8):
            m = sm.zbuduj_stadium(nr, styl=styl, id="styl_%s_%d" % (styl, nr))
            modele.append(m)
            zadania.append({"typ": "widoki", "model": m.id, "widoki": {"gra": GRA34, "bok": BOK}, "rozmiar": 440})
    widoki(modele, zadania, folder, "plansza stylu (6 modeli)")
    wiersze, etyk, mini = [], [], {}
    for r, (styl, nazwa) in enumerate(STYLE):
        wiersze.append([os.path.join(folder, "styl_%s_%d_%s.jpg" % (styl, nr, w)) for nr in (1, 8) for w in ("gra", "bok")])
        etyk.append(nazwa)
        mini[(r, 0)] = mini[(r, 2)] = 72
    return siatka_obrazow(wiersze, os.path.join(PODGLAD, "01_plansza_stylu.jpg"),
                          tytul="Smok ewolucji — trzy kierunki stylu (pisklę i Prastary; kamera gry + bok; wklejka = miniatura 72 px)",
                          etykiety_wierszy=etyk, miniatury=mini, kom=440,
                          etykiety_kolumn=["HATCHLING — kamera gry", "HATCHLING — bok", "ANCIENT — kamera gry", "ANCIENT — bok"])


def cmd_przeglad(*nry):
    """Roboczy przegląd stadiów (poza repozytorium): kamera gry z tyłu, 3/4 z przodu, bok."""
    folder = wyjscie("przeglad")
    nry = [int(x) for x in nry] or list(range(1, 9))
    modele = [sm.zbuduj_stadium(nr) for nr in nry]
    zadania = [{"typ": "widoki", "model": m.id, "widoki": {"gra": GRA, "przod": BOHATER, "bok": BOK}, "rozmiar": 360}
               for m in modele]
    widoki(modele, zadania, folder, "przegląd stadiów")
    wiersze = [[os.path.join(folder, "%s_%s.jpg" % (m.id, w)) for m in modele] for w in ("gra", "przod", "bok")]
    return siatka_obrazow(wiersze, os.path.join(folder, "przeglad.jpg"), kom=300 if len(nry) > 4 else 360,
                          etykiety_kolumn=[sm.stadium(n)["nazwa"] for n in nry])


def modele_pelne(nry=None, jajo=True):
    """Stadia z kompletem klipów (+ jajo z klipem wyklucia o długości klipu pisklęcia)."""
    wyn = [sk.dodaj_klipy(sm.zbuduj_stadium(nr)) for nr in (nry or range(1, 9))]
    if jajo:
        n = next(k.dlugosc for k in sk.dodaj_klipy(sm.zbuduj_stadium(1), dodatkowe=False).klipy if k.nazwa == "wyklucie")
        wyn.append(sk.klipy_jaja(sm.zbuduj_jajo(1), n))
    return wyn


def pasek_klipu(folder, m, klip, ile=8, kierunek=BOHATER, rozmiar=260):
    k = next(x for x in m.klipy if x.nazwa == klip)
    kl = [round(k.dlugosc * i / (ile if k.petla else ile - 1), 2) for i in range(ile)]
    return ({"typ": "pasek", "model": m.id, "klip": klip, "klatki": kl, "kierunek": kierunek, "rozmiar": rozmiar},
            [os.path.join(folder, "%s_%s_%02d.jpg" % (m.id, klip, i)) for i in range(ile)])


def cmd_paski(nr="1", *klipy):
    """Roboczy podgląd klipów jednego stadium (poza repozytorium): po 8 klatek na klip."""
    folder = wyjscie("paski")
    m = modele_pelne([int(nr)], jajo=False)[0]
    klipy = list(klipy) or [k.nazwa for k in m.klipy]
    zadania, wiersze = [], []
    for kl in klipy:
        z, pliki = pasek_klipu(folder, m, kl)
        zadania.append(z)
        wiersze.append(pliki)
    widoki([m], zadania, folder, "paski klipów stadium %s" % nr)
    return siatka_obrazow(wiersze, os.path.join(folder, "paski_%s.jpg" % nr), kom=200, etykiety_wierszy=klipy)


# --------------------------------------------------------------------------- dane dla gry
KROK = 2                              # próbka co 2 klatki (15 na sekundę); gra interpoluje liniowo
WARIANTY = (("GOLD", {"cialo": "FFC83D", "brzuch": "FFF1B0", "blona": "FF9A2E", "kolce": "FFFFFF", "zar": "FFF6B0"}),
            ("CRYSTAL", {"cialo": "7FE9FF", "brzuch": "EAFBFF", "blona": "B9A6FF", "kolce": "FFFFFF", "zar": "FFFFFF"}),
            ("RUBY", {"cialo": "E8204E", "brzuch": "FFC2D0", "blona": "7A1038", "kolce": "FFE9A8", "zar": "FFB21F"}),
            ("linia LODU", {"cialo": "CFEFFF", "brzuch": "FFFFFF", "blona": "4FA8FF", "kolce": "2F6FDB", "zar": "7CF4FF"}))


def _zapisz(dane, sciezka):
    with open(sciezka, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dane, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    return os.path.getsize(sciezka)


def rig_modelu(m):
    """Rig z części Roblox (ścieżka biblioteki roblox_klocki.rig) + region koloru każdej części + wymiary."""
    r = rk.rig(m)
    d = m.json()
    regiony = m.regiony() if hasattr(m, "regiony") else ["stale"] * len(d["czesci"])
    reg = []
    for c, g in zip(d["czesci"], regiony):
        reg += [sm.REGIONY.index(g)] * len([1 for x in rk.rozloz(c) if min(x[3]) >= 0.001])
    assert len(reg) == len(r["czesci"]), "regiony nie pasują do części"
    for wiersz, g in zip(r["czesci"], reg):
        wiersz.append(g)
    pud = pudelko([dict(c, r=tuple(c["r"])) for c in d["czesci"]])
    r.pop("klipy", None)
    r.update({"format": "smok-ewolucji-rig/2", "skala": m.skala, "regiony": list(sm.REGIONY),
              "liczba_czesci": len(r["czesci"]), "liczba_stawow": len(r["kosci"]),
              "wymiary": {"szer": round(pud[1][0] - pud[0][0], 2), "wys": round(pud[1][1], 2),
                          "przod": round(pud[1][2], 2), "tyl": round(-pud[0][2], 2)}})
    P = getattr(m, "dane_stadium", None)
    if P:
        r.update({"nr": P["nr"], "nazwa_gry": P["nazwa"], "promien_gry": P["r"], "waga": P["waga"],
                  "paleta": {k: v for k, v in sm.paleta_stadium(P["nr"]).items()
                             if k in ("cialo", "cialo_c", "brzuch", "blona", "kolce", "zar", "zar_c", "zar_j", "oko")}})
    return r


def klipy_modelu(m, r, pr):
    """Próbki klipów (Blender, co KROK klatek) w układzie rigu Roblox: obrót w 0,1 stopnia, przesunięcie w 0,001 studa."""
    nazwy = [k[0] for k in r["kosci"]]
    klipy = {}
    for kl in m.klipy:
        p_ = pr[kl.nazwa]
        stawy = [n for n in nazwy if n in p_]
        zprzes = [n for n in stawy if any(abs(v) > 1e-4 for w in p_[n].get("przes", []) for v in w)]
        wiersze = []
        for f in range(0, kl.dlugosc + 1, KROK):
            w = []
            for n in stawy:
                if n in zprzes:
                    x, y, z = p_[n]["przes"][f]
                    w += [int(round(-x * 1000)), int(round(y * 1000)), int(round(-z * 1000))]
                o = p_[n].get("obrot")
                rx, ry, rz = o[f] if o else (0.0, 0.0, 0.0)
                w += [int(round(-rx * 10)), int(round(ry * 10)), int(round(-rz * 10))]
            wiersze.append(w)
        if hasattr(kl, "predkosc"):                             # prędkość (studs/s), przy której stopy się nie ślizgają
            dodatki = {"predkosc": round(kl.predkosc * m.skala, 2)}
        else:
            dodatki = {}
        klipy[kl.nazwa] = {"dl": kl.dlugosc, "petla": kl.petla, "zdarzenia": getattr(kl, "zdarzenia", {}), **dodatki,
                           "stawy": [nazwy.index(n) + 1 for n in stawy], "przes": [nazwy.index(n) + 1 for n in zprzes],
                           "probki": wiersze}
    return {"format": "smok-ewolucji-klipy/2", "id": m.id, "fps": 30, "krok": KROK, "stawy": nazwy, "klipy": klipy}


def cmd_dane():
    os.makedirs(DANE, exist_ok=True)
    folder = wyjscie("dane_robocze")
    modele = modele_pelne()
    pj, wj = os.path.join(folder, "_pakiet.json"), os.path.join(folder, "_probki.json")
    zapisz_json(pakiet(modele), pj)
    blender(os.path.join(BIB, "blender_probki.py"), [pj, wj], "próbki klipów (9 modeli)")
    with open(wj, encoding="utf-8") as f:
        probki = json.load(f)
    indeks = {"format": "smok-ewolucji-indeks/2", "wersja": 2, "fps": 30, "krok": KROK, "stawy": list(sm.KOSCI),
              "zaczepy": list(sm.ZACZEPY), "regiony": list(sm.REGIONY),
              "klipy_podstawowe": list(sk.KLIPY_PODSTAWOWE), "klipy_dodatkowe": list(sk.KLIPY_DODATKOWE),
              "zdarzenia": sk.ZDARZENIA_OPIS, "stadia": []}
    for m in modele:
        r = rig_modelu(m)
        for u in r["uwagi"]:
            print("UWAGA %s: %s" % (m.id, u))
        k = klipy_modelu(m, r, probki[m.id])
        a = _zapisz(r, os.path.join(DANE, m.id + "_rig.json"))
        lod = None
        if r.get("nr"):                                         # wersja uproszczona: te same stawy i klipy
            lod = rig_modelu(sm.zbuduj_stadium_lod(r["nr"]))
            _zapisz(lod, os.path.join(DANE, m.id + "_lod_rig.json"))
        b = _zapisz(k, os.path.join(DANE, m.id + "_klipy.json"))
        indeks["stadia"].append({"id": m.id, "nr": r.get("nr", 0), "nazwa": r.get("nazwa_gry", m.nazwa),
                                 "promien_gry": r.get("promien_gry"), "skala": m.skala, "czesci": r["liczba_czesci"],
                                 "stawy": r["liczba_stawow"], "wymiary": r["wymiary"], "klipy": len(m.klipy),
                                 "klatki": sum(x.dlugosc for x in m.klipy),
                                 "pliki": [m.id + "_rig.json", m.id + "_klipy.json"],
                                 "czesci_lod": lod["liczba_czesci"] if lod else None,
                                 "plik_lod": (m.id + "_lod_rig.json") if lod else None})
        print("DANE | %-10s części %3d (uproszczony %s)  stawy %2d  klipy %2d  rig %3d kB  klipy %3d kB" % (
            m.id, r["liczba_czesci"], lod["liczba_czesci"] if lod else "-", r["liczba_stawow"], len(m.klipy),
            a // 1024, b // 1024))
    stary = os.path.join(DANE, "indeks.json")
    if os.path.isfile(stary):                                   # liczby trójkątów dopisuje polecenie „siatki”
        with open(stary, encoding="utf-8") as f:
            indeks["siatki"] = json.load(f).get("siatki", {})
    _zapisz(indeks, stary)


def cmd_siatki():
    """Ścieżka siatek na później: siatka na staw i region koloru (FBX + GLB poza repozytorium), bez wgrywania."""
    folder = wyjscie("siatki")
    modele = modele_pelne()
    pak = pakiet(modele)
    for d, m in zip(pak["modele"], modele):
        d["regiony_czesci"] = m.regiony()
        d["klipy"] = []
    pj, mj = os.path.join(folder, "_pakiet.json"), os.path.join(folder, "_manifest.json")
    zapisz_json(pak, pj)
    blender(os.path.join(TU, "blender_siatki.py"), [pj, folder, mj], "siatki na staw i region (9 modeli)")
    with open(mj, encoding="utf-8") as f:
        man = json.load(f)
    ip = os.path.join(DANE, "indeks.json")
    indeks = {}
    if os.path.isfile(ip):
        with open(ip, encoding="utf-8") as f:
            indeks = json.load(f)
    indeks["siatki"] = {i: {"liczba_siatek": v["liczba_siatek"], "trojkaty": v["trojkaty"],
                            "siatki": [[w[0], w[3], w[4], w[5]] for w in v["siatki"]]} for i, v in man.items()}
    _zapisz(indeks, ip)
    for i, v in man.items():
        print("SIATKI | %-10s %3d siatek  %5d trójkątów" % (i, v["liczba_siatek"], v["trojkaty"]))
    print("SIATKI | pliki <id>_czesci.fbx / .glb w folderze wyników: siatki")


def _biblioteka(argumenty, opis):
    r = subprocess.run([sys.executable, "-B", os.path.join(BIB, "podglad_postaci.py"), "--modul",
                        os.path.join(TU, "smoki.py")] + argumenty, capture_output=True, cwd=REPO)
    wyj = (r.stdout + r.stderr).decode("utf-8", "replace")
    for linia in wyj.splitlines():
        if "BŁĄD" in linia or "NIEZGOD" in linia or "Traceback" in linia or "Error" in linia:
            print("   ", linia[:200])
    print("BIBLIOTEKA | %s: kod %d" % (opis, r.returncode))
    return r.returncode


def cmd_eksport(*ids):
    """FBX (model + jeden plik na klip), GLB i .blend przez bibliotekę, z kontrolą wczytania — poza repozytorium."""
    folder = wyjscie("eksport")
    for i in (ids or ["smok_%d" % n for n in range(1, 9)] + ["smok_jajo"]):
        _biblioteka(["--wyj", folder, "--tylko", i, "--eksport", "--bez-renderu"], "eksport " + i)
    print("EKSPORT | pliki w folderze wyników: eksport")


def cmd_filmy(*stadia):
    # Filmy MP4 (biblioteka): chod, bieg, lancuch ugryzien i zioniecie; stadia 1, 3, 5, 8; poza repozytorium.
    import glob
    import shutil
    folder = wyjscie("filmy")
    for stary in glob.glob(os.path.join(folder, "smok_*")):
        if os.path.isfile(stary):
            os.remove(stary)
    ffmpeg = shutil.which("ffmpeg")
    for n in (stadia or ("1", "3", "5", "8")):
        i = "smok_%s" % n
        for kl in ("chod", "bieg", "gryz1", "gryz2", "gryz3", "ogien_start", "ogien_petla", "ogien_koniec"):
            _biblioteka(["--wyj", folder, "--tylko", i, "--klip", kl, "--bez-obrysu"], "film %s %s" % (i, kl))
        for nazwa, czesci in (("gryzienie", ("gryz1", "gryz2", "gryz3")), ("ogien", ("ogien_start", "ogien_petla", "ogien_koniec"))):
            pliki = [os.path.join(folder, "%s_%s.mp4" % (i, c)) for c in czesci]
            if ffmpeg and all(os.path.isfile(x) for x in pliki):
                arg = [ffmpeg, "-y", "-loglevel", "error"]
                for x in pliki:
                    arg += ["-i", x]
                arg += ["-filter_complex", "concat=n=%d:v=1:a=0" % len(pliki), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        os.path.join(folder, "%s_%s.mp4" % (i, nazwa))]
                subprocess.run(arg, capture_output=True)
                for x in pliki:
                    os.remove(x)
    print("FILMY | pliki w folderze wyników: filmy (smok_N_chod, _bieg, _gryzienie, _ogien)")


def cmd_podglady():
    """Podglądy do repozytorium (podglad/, najwyżej 12 małych JPG) — duże rendery zostają poza repozytorium."""
    folder = wyjscie("podglady")
    modele = modele_pelne()
    smoki, jajo = modele[:8], modele[8]
    ids = [m.id for m in smoki]
    plansza = {"przod": BOHATER, "gra": GRA, "bok": BOK, "tyl": (-0.6, 0.45, -1.0)}
    zadania = [{"typ": "rzad", "modele": ids[::-1], "kierunek": (-1.0, 0.1, 0.12), "rozmiar": [2400, 520], "plik": "rzad_bok.jpg",
                "os": "z", "odstep": 0.04},
               {"typ": "rzad", "modele": ids, "kierunek": GRA, "rozmiar": [2400, 900], "plik": "rzad_gra.jpg",
                "odstep": 0.1}]
    zadania += [{"typ": "widoki", "model": "smok_%d" % n, "widoki": plansza, "rozmiar": 450} for n in (1, 4, 8)]
    zadania += [{"typ": "widoki", "model": i, "widoki": {"gra": GRA, "przod": BOHATER, "bok": BOK}, "rozmiar": 300,
                 "przyrostek": "m"} for i in ids]
    paski = {}
    for klip in ("chod", "gryz3", "ogien_start", "ogien_petla"):
        for n in (1, 4, 8):
            z, pliki = pasek_klipu(folder, smoki[n - 1], klip, rozmiar=200)
            zadania.append(z)
            paski[(klip, n)] = pliki
    z, wykl = pasek_klipu(folder, smoki[0], "wyklucie", kierunek=(0.7, 0.35, 1.0), rozmiar=300)
    z["dodatkowe"] = [jajo.id]
    zadania.append(z)
    warianty = [sm.zbuduj_stadium(5, zmiany_kolorow=zm, id="wariant_%d" % i) for i, (_, zm) in enumerate(WARIANTY)]
    from swiat.ewolucja.modele import rekwizyty
    lod = [sm.zbuduj_stadium_lod(n) for n in range(1, 9)]
    rekw = [rekwizyty.skarb(1), rekwizyty.skarb(3), rekwizyty.cokol(), rekwizyty.gniazdo()]
    from swiat.ewolucja.modele import stwory
    rekw += [stwory.owca(), stwory.golem(1), stwory.golem(3), stwory.golem(5)]
    zadania += [{"typ": "widoki", "model": m.id, "widoki": {"gra": GRA}, "rozmiar": 300, "przyrostek": "m"} for m in lod]
    zadania += [{"typ": "widoki", "model": m.id, "widoki": {"przod": BOHATER}, "rozmiar": 300} for m in rekw]
    zadania += [{"typ": "widoki", "model": m.id, "widoki": {"przod": BOHATER, "gra": GRA}, "rozmiar": 300} for m in warianty]
    widoki(modele + warianty + lod + rekw, zadania, folder, "podglądy (%d zadań)" % len(zadania))

    from PIL import Image
    for plik, cel in (("rzad_bok.jpg", "02_rzad_stadiow_bok.jpg"), ("rzad_gra.jpg", "03_rzad_stadiow_kamera_gry.jpg")):
        im = Image.open(os.path.join(folder, plik)).convert("RGB")
        im.save(os.path.join(PODGLAD, cel), quality=84, optimize=True)
        print("PLANSZA |", os.path.join(PODGLAD, cel))
    nazwy = [m.dane_stadium["nazwa"] for m in smoki]
    siatka_obrazow([[os.path.join(folder, "%s_%sm.jpg" % (i + x, w)) for i in ids] for x, w in (("", "gra"), ("_lod", "gra"), ("", "przod"))],
                   os.path.join(PODGLAD, "04_stadia_przeglad.jpg"), kom=300, etykiety_kolumn=nazwy,
                   tytul="Osiem stadiów: kamera gry — pełny model / wersja uproszczona (35 części) / 3/4 z przodu; wklejka = 64 px",
                   miniatury={(r_, c): 64 for c in range(8) for r_ in (0, 1)})
    for nr, n in ((5, 1), (6, 4), (7, 8)):
        i = "smok_%d" % n
        siatka_obrazow([[os.path.join(folder, "%s_przod.jpg" % i), os.path.join(folder, "%s_gra.jpg" % i)],
                        [os.path.join(folder, "%s_bok.jpg" % i), os.path.join(folder, "%s_tyl.jpg" % i)]],
                       os.path.join(PODGLAD, "%02d_stadium_%d.jpg" % (nr, n)), kom=450,
                       tytul="%s — %d części Roblox, %d stawów" % (smoki[n - 1].dane_stadium["nazwa"],
                                                                 sm.liczba_czesci_roblox(smoki[n - 1]), len(sm.KOSCI)))
    for nr, klipy, nazwa in ((8, ("chod",), "chod"), (9, ("gryz3",), "gryz"), (10, ("ogien_start", "ogien_petla"), "ogien")):
        wiersze, etyk = [], []
        for klip in klipy:
            for n in (1, 4, 8):
                wiersze.append(paski[(klip, n)])
                etyk.append("%s — %s" % (klip, smoki[n - 1].dane_stadium["nazwa"]))
        siatka_obrazow(wiersze, os.path.join(PODGLAD, "%02d_klatki_%s.jpg" % (nr, nazwa)), kom=200, etykiety_wierszy=etyk)
    siatka_obrazow([wykl[:4], wykl[4:]], os.path.join(PODGLAD, "11_klatki_wyklucie.jpg"), kom=300,
                   tytul="wyklucie — pisklę + jajo (osobny rig smok_jajo)")
    siatka_obrazow([[os.path.join(folder, "%s_przod.jpg" % m.id) for m in warianty], [os.path.join(folder, "%s_przod.jpg" % m.id) for m in rekw[:4]],
                    [os.path.join(folder, "%s_przod.jpg" % m.id) for m in rekw[4:]]],
                   os.path.join(PODGLAD, "12_warianty_i_rekwizyty.jpg"), kom=300, etykiety_kolumn=[n for n, _ in WARIANTY],
                   tytul="Warianty kolorów · rekwizyty legowiska · owca i KNIGHT GOLEM (1, 3, 5)")


def cmd_rekwizyty():
    # Rekwizyty legowiska (skarb 1-3, cokol, gniazdo): rigi z czesci do dane/rekwizyt_<id>_rig.json
    from swiat.ewolucja.modele import rekwizyty
    ip = os.path.join(DANE, "indeks.json")
    with open(ip, encoding="utf-8") as f:
        indeks = json.load(f)
    indeks["rekwizyty"] = []
    for m in rekwizyty.wszystkie():
        r = rig_modelu(m)
        _zapisz(r, os.path.join(DANE, "rekwizyt_%s_rig.json" % m.id))
        indeks["rekwizyty"].append({"id": m.id, "nazwa": m.nazwa, "czesci": r["liczba_czesci"], "wymiary": r["wymiary"],
                                    "plik": "rekwizyt_%s_rig.json" % m.id})
        print("REKWIZYT | %-8s czesci %2d" % (m.id, r["liczba_czesci"]))
    _zapisz(indeks, ip)


def cmd_stwory():
    # Owca (ofiara) i KNIGHT GOLEM w pieciu stopniach: rigi i klipy do dane/
    from swiat.ewolucja.modele import stwory
    folder = wyjscie("dane_robocze")
    modele = [stwory.owca()] + [stwory.golem(t) for t in range(1, 6)]
    for m in modele:
        for x in m.sprawdz()[0]:
            raise SystemExit("BŁĄD danych: " + x)
    pj, wj = os.path.join(folder, "_pakiet_stwory.json"), os.path.join(folder, "_probki_stwory.json")
    zapisz_json(pakiet(modele), pj)
    blender(os.path.join(BIB, "blender_probki.py"), [pj, wj], "próbki klipów (owca, golem)")
    with open(wj, encoding="utf-8") as f:
        probki = json.load(f)
    ip = os.path.join(DANE, "indeks.json")
    with open(ip, encoding="utf-8") as f:
        indeks = json.load(f)
    indeks["stwory"] = []
    for m in modele:
        r = rig_modelu(m)
        k = klipy_modelu(m, r, probki[m.id])
        _zapisz(r, os.path.join(DANE, m.id + "_rig.json"))
        b = _zapisz(k, os.path.join(DANE, m.id + "_klipy.json"))
        indeks["stwory"].append({"id": m.id, "nazwa": m.nazwa, "skala": m.skala, "czesci": r["liczba_czesci"],
                                 "stawy": [x[0] for x in r["kosci"]], "zaczepy": [x[0] for x in r["zaczepy"]],
                                 "klipy": {x.nazwa: getattr(x, "zdarzenia", {}) for x in m.klipy}, "wymiary": r["wymiary"],
                                 "pliki": [m.id + "_rig.json", m.id + "_klipy.json"]})
        print("STWOR | %-8s części %2d  stawy %2d  klipy %d (%d kB)" % (m.id, r["liczba_czesci"], len(r["kosci"]), len(m.klipy), b // 1024))
    _zapisz(indeks, ip)


def cmd_swiat():
    # Zestaw swiata (laka, las, legowisko, wyspa lawy, woda, znaki, kule, stos zlota): nowe pliki rekwizyt_<id>_rig.json
    from swiat.ewolucja.modele import swiat_zestaw
    ip = os.path.join(DANE, "indeks.json")
    with open(ip, encoding="utf-8") as f:
        indeks = json.load(f)
    indeks["swiat"] = []
    for m, strefa, limit in swiat_zestaw.wszystkie():
        r = rig_modelu(m)
        _zapisz(r, os.path.join(DANE, "rekwizyt_%s_rig.json" % m.id))
        indeks["swiat"].append({"id": m.id, "nazwa": m.nazwa, "strefa": strefa, "czesci": r["liczba_czesci"], "limit": limit,
                                "wymiary": r["wymiary"], "plik": "rekwizyt_%s_rig.json" % m.id})
        print("SWIAT | %-22s %-10s części %2d / %2d%s" % (m.id, strefa, r["liczba_czesci"], limit,
                                                      "  PONAD LIMIT" if r["liczba_czesci"] > limit else ""))
    _zapisz(indeks, ip)


def cmd_mapa():
    # Propozycja mapy: dane/mapa_propozycja.json, render z gory i z kamery gry, plansza zestawu
    from swiat.ewolucja.modele import mapa
    inst, czesci, strefy, razem = mapa.zrob(sys.modules[__name__])
    ip = os.path.join(DANE, "indeks.json")
    with open(ip, encoding="utf-8") as f:
        indeks = json.load(f)
    indeks["mapa"] = {"plik": "mapa_propozycja.json", "czesci_razem": razem, "czesci_stref": strefy}
    _zapisz(indeks, ip)


def cmd_golem_grozny():
    # KNIGHT GOLEM w wersji groznej: NOWE pliki golem_grozny_<1-5>_rig.json i _klipy.json, plansza podgladu 20
    from swiat.ewolucja.modele import stwory_grozne
    folder = wyjscie("dane_robocze")
    modele = [stwory_grozne.golem_grozny(t) for t in range(1, 6)]
    pj, wj = os.path.join(folder, "_pakiet_golem2.json"), os.path.join(folder, "_probki_golem2.json")
    zapisz_json(pakiet(modele), pj)
    blender(os.path.join(BIB, "blender_probki.py"), [pj, wj], "próbki klipów (golem groźny)")
    with open(wj, encoding="utf-8") as f:
        probki = json.load(f)
    ip = os.path.join(DANE, "indeks.json")
    with open(ip, encoding="utf-8") as f:
        indeks = json.load(f)
    indeks["stwory_grozne"] = []
    for m in modele:
        r = rig_modelu(m)
        _zapisz(r, os.path.join(DANE, m.id + "_rig.json"))
        _zapisz(klipy_modelu(m, r, probki[m.id]), os.path.join(DANE, m.id + "_klipy.json"))
        indeks["stwory_grozne"].append({"id": m.id, "nazwa": m.nazwa, "skala": m.skala, "czesci": r["liczba_czesci"],
                                        "wymiary": r["wymiary"], "pliki": [m.id + "_rig.json", m.id + "_klipy.json"]})
        print("GOLEM | %-16s części %2d" % (m.id, r["liczba_czesci"]))
    _zapisz(indeks, ip)
    rob = wyjscie("podglady")
    wyb = [modele[0], modele[2], modele[4]]
    zad = [{"typ": "widoki", "model": m.id, "widoki": {"przod": [0.5, 0.12, 1.0], "bok": [-1.0, 0.1, 0.25]}, "rozmiar": 360} for m in wyb]
    widoki(wyb, zad, rob, "golem groźny: plansza")
    siatka_obrazow([[os.path.join(rob, "%s_przod.jpg" % m.id) for m in wyb], [os.path.join(rob, "%s_bok.jpg" % m.id) for m in wyb]],
                   os.path.join(PODGLAD, "20_golem_grozny.jpg"), kom=360, tytul="KNIGHT GOLEM — wersja groźna, stopnie 1, 3, 5")


def cmd_interfejs():
    # Grafika interfejsu: ikony, portrety, makiety (czyta dane/ i render mapy; niczego w dane/ nie zmienia)
    from swiat.ewolucja.modele import interfejs
    interfejs.zrob(sys.modules[__name__])


def cmd_etap():
    # Etap: zmienione i nowe pliki danych do dane_nastepne/ (folderu dane/ nie dotyka), film biegu nad krata
    from swiat.ewolucja.modele import etap
    etap.zrob(sys.modules[__name__])


def cmd_obrazy():
    # Ikona i trzy miniatury strony gry (wymaga dane/)
    from swiat.ewolucja.modele import obrazy_gry
    obrazy_gry.zrob(sys.modules[__name__])


def cmd_wszystko():
    cmd_dane()
    cmd_rekwizyty()
    cmd_stwory()
    cmd_swiat()
    cmd_golem_grozny()
    cmd_styl()
    cmd_podglady()
    cmd_obrazy()
    cmd_mapa()
    cmd_siatki()
    cmd_eksport()


def cmd_licz():
    for P in sm.STADIA:
        p = sm.zbuduj_stadium(P["nr"])
        d = p.json()
        sk.dodaj_klipy(p)
        b, u = p.sprawdz()
        print("%-15s skala %.2f  bryły %3d  części Roblox %3d  kości %d  klipy %d  klatek %d%s" % (
            P["nazwa"], p.skala, len(d["czesci"]), sm.liczba_czesci_roblox(p), len(d["kosci"]) - 1, len(p.klipy),
            sum(k.dlugosc for k in p.klipy), ("  BŁĘDY: %s" % b) if b else ""))
        for x in u:
            if "pętla" in x or "skal" in x:
                print("    UWAGA:", x)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    co = sys.argv[1] if len(sys.argv) > 1 else "licz"
    fn = globals().get("cmd_" + co)
    if fn is None:
        raise SystemExit(__doc__)
    fn(*sys.argv[2:])


if __name__ == "__main__":
    main()
