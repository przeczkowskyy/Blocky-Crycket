#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prezentacja całości: postacie w skali, pokaz animacji, katalog ekwipunku i lista przedmiotów.

    # z głównego folderu repozytorium (Blender 5.0, ffmpeg i Pillow muszą być dostępne)
    python -B swiat/postacie/zestawienie.py                    # wszystko
    python -B swiat/postacie/zestawienie.py --tylko json       # tylko przedmioty.json (bez Blendera)
    python -B swiat/postacie/zestawienie.py --tylko skala,film,katalog,json

Wyniki (folder swiat/postacie/wynik/_zestawienie/ i swiat/postacie/przedmioty.json):
  postacie_w_skali.jpg, postacie_w_skali_obrys.jpg — wszystkie postacie w jednym rzędzie, jedna skala, szary
                        manekin gracza R15 (5,25 studa) z lewej; kamera ortogonalna, każdy model przodem 3/4
  pokaz_animacji.mp4  — po kolei klipy każdej postaci (H.264 yuv420p, ok. 25 s), pokaz_animacji_klatki.jpg — arkusz
  katalog_ekwipunku.jpg — ikony przedmiotów w wierszach slotów + trzy przymiarki zestawów na manekinie
  przedmioty.json + zaczepy_akcesoriow.luau — lista przedmiotów z gotowymi Attachmentami (dane z wynik/*/raport.json)
  przymiarki_zestawow.jpg — same przymiarki (większe)
Blender działa pod wspólną blokadą (zajmij_blender / zwolnij_blender), jedno wywołanie na krótkie zadanie.
Pliki robocze idą do folderu tymczasowego systemu (usuwany na końcu).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.biblioteka.podglad import blender_exe, zajmij_blender, zwolnij_blender  # noqa: E402
from swiat.postacie.biblioteka.podglad_postaci import wczytaj_modul  # noqa: E402
from swiat.postacie.biblioteka.postac import (Akcesorium, Postac, manekin_r15, pakiet, przymiarka,  # noqa: E402
                                              zapisz_json)

SKRYPT = os.path.join(TU, "biblioteka", "blender_zestawienie.py")
WYNIK = os.path.join(TU, "wynik")
CEL = os.path.join(WYNIK, "_zestawienie")

# kolejność w rzędzie i w filmie
POSTACIE = [("rycerz", "Rycerz"), ("karczmarz", "Karczmarz"), ("kot_mag", "Kot-Mag"),
            ("pies", "Pies"), ("smok", "Smok"), ("slime", "Slime")]
# segmenty filmu: (klip, ile klatek [, przytrzymanie ostatniej klatki]) — 30 kl./s, razem ok. 25 s
SEGMENTY = {
    "rycerz": [("idle", 30), ("chod", 36), ("atak_miecz", 33, 8), ("wiwat", 36)],
    "karczmarz": [("idle", 30), ("zaproszenie", 60), ("smiech", 40)],
    "kot_mag": [("idle", 30), ("chod", 30), ("czar", 55, 8), ("wiwat", 30)],
    "pies": [("idle", 30), ("bieg", 24), ("szczek", 30)],
    "smok": [("idle_lot", 30), ("lot", 36), ("zioniecie", 49, 8)],
    "slime": [("idle", 30), ("skok", 40), ("atak", 37, 8)],
}
KLIPY_PL = {"idle": "spoczynek", "chod": "chód", "atak_miecz": "atak mieczem", "wiwat": "wiwat", "czar": "czar",
            "zaproszenie": "zaproszenie", "smiech": "śmiech", "bieg": "bieg", "szczek": "szczekanie",
            "skok": "skok", "atak": "atak", "idle_lot": "zawis w locie", "lot": "lot", "zioniecie": "zianie"}

SLOTY = [("Helmet", "Głowa"), ("Chest", "Tors"), ("Gloves", "Rękawice"), ("Boots", "Buty"), ("Belt", "Pas"),
         ("Weapon", "Broń"), ("OffHand", "Druga ręka"), ("Amulet", "Amulet"), ("Ring", "Pierścień"),
         ("Trinket", "Talizman")]
ZESTAWY = [("zestaw_rekrut", "Rekrut (start)", "C08A55"), ("zestaw_rycerz", "Rycerz", "3E7BEA"),
           ("zestaw_mag", "Mag", "A066F0"), ("bronie", "Zbrojownia", "E2583A"),
           ("kot_mag", "Rekwizyty Kota-Maga", "F39A2C")]
FONT = r"C:\Windows\Fonts\segoeui.ttf"
FONT_B = r"C:\Windows\Fonts\segoeuib.ttf"


def log(*a):
    print("ZESTAWIENIE |", *a, flush=True)


def wzgl(p):
    return os.path.relpath(p, TU).replace(os.sep, "/")


def modul(nazwa):
    return wczytaj_modul(os.path.join(TU, nazwa + ".py"))


def lista(w):
    return list(w) if isinstance(w, (list, tuple)) else [w]


def uruchom_blendera(pak, wyj, opis):
    os.makedirs(wyj, exist_ok=True)
    plik = os.path.join(wyj, "zadanie.json")
    zapisz_json(pak, plik)
    polecenie = [blender_exe(), "-b", "--factory-startup", "--python-exit-code", "1", "--python", SKRYPT, "--",
                 "--json", plik, "--wyj", wyj]
    blokada = zajmij_blender()
    t0 = time.time()
    try:
        r = subprocess.run(polecenie, capture_output=True, timeout=11 * 60,
                           creationflags=0x08000000 if os.name == "nt" else 0)
    finally:
        zwolnij_blender(blokada)
    wyjscie = (r.stdout + r.stderr).decode("utf-8", "replace")
    if r.returncode != 0:
        print("\n".join(wyjscie.splitlines()[-40:]))
        raise SystemExit("Blender: %s — błąd (kod %d)" % (opis, r.returncode))
    log("%s: %.0f s" % (opis, time.time() - t0))
    return wyjscie


def postacie():
    wynik = []
    for mid, _ in POSTACIE:
        p = next(o for o in lista(modul(mid).zbuduj()) if isinstance(o, Postac) and o.id == mid)
        wynik.append(p)
    return wynik


def przymiarki():
    """Trzy zestawy na szarym manekinie R15 (jak w podglad_postaci.py: same akcesoria -> manekin + założenie)."""
    wynik = []
    for mid in ("zestaw_rekrut", "zestaw_rycerz", "zestaw_mag"):
        obiekty = lista(modul(mid).zbuduj())
        p = next((o for o in obiekty if isinstance(o, Postac)), None)
        if p is None:
            p = przymiarka("przymiarka_" + mid, [a for a in obiekty if isinstance(a, Akcesorium)], "Przymiarka " + mid)
        p.id = "przym_" + mid
        wynik.append(p)
    return wynik


# --------------------------------------------------------------------------- 1. postacie w skali
def skala(tmp):
    pak = pakiet(postacie())
    pak["zestawienie"] = {"tryb": "rzad", "nazwa": "postacie_w_skali", "szer": 1800, "wys": 600, "probki": 16,
                          "obrot": -26.57, "odstep": 1.1, "obrys": [False, True], "grubosc_obrysu": 0.04, "margines": 1.09,
                          "manekin": manekin_r15("manekin_skali", "Manekin", klipy=False).json()["czesci"]}
    wyj = os.path.join(tmp, "skala")
    uruchom_blendera(pak, wyj, "postacie w skali")
    for n in ("postacie_w_skali.jpg", "postacie_w_skali_obrys.jpg"):
        shutil.copy(os.path.join(wyj, n), os.path.join(CEL, n))
        log("gotowe", wzgl(os.path.join(CEL, n)))


# --------------------------------------------------------------------------- 2. pokaz animacji
def film(tmp):
    from PIL import Image, ImageDraw, ImageFont
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("Brak ffmpeg w PATH.")
    wyj = os.path.join(tmp, "film")
    podpisy = []                                                # (od klatki, do klatki, postać, klip)
    nr = 0
    for p, (mid, nazwa) in zip(postacie(), POSTACIE):
        seg = SEGMENTY[mid]
        pak = pakiet([p])
        pak["zestawienie"] = {"tryb": "film", "rozmiar": 540, "probki": 8, "start": nr,
                              "segmenty": [list(s) for s in seg]}
        uruchom_blendera(pak, wyj, "film: " + nazwa)
        for s in seg:
            ile = s[1] + (s[2] if len(s) > 2 else 0)
            podpisy.append((nr, nr + ile, nazwa, KLIPY_PL.get(s[0], s[0])))
            nr += ile
    fb, fr = ImageFont.truetype(FONT_B, 24), ImageFont.truetype(FONT, 22)
    for od, do, kto, co in podpisy:                             # podpis w rogu (na kadrze, nie na modelu)
        for i in range(od, do):
            pth = os.path.join(wyj, "klatki", "%05d.png" % i)
            im = Image.open(pth).convert("RGBA")
            warstwa = Image.new("RGBA", im.size, (0, 0, 0, 0))
            dr = ImageDraw.Draw(warstwa)
            w1 = dr.textlength(kto, font=fb)
            w2 = dr.textlength(co, font=fr)
            dr.rounded_rectangle((12, 12, 12 + w1 + w2 + 44, 52), radius=10, fill=(24, 18, 36, 190))
            dr.text((24, 15), kto, font=fb, fill=(255, 255, 255, 255))
            dr.text((24 + w1 + 14, 17), co, font=fr, fill=(214, 200, 255, 255))
            Image.alpha_composite(im, warstwa).convert("RGB").save(pth)
    mp4 = os.path.join(CEL, "pokaz_animacji.mp4")
    r = subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-framerate", "30", "-i",
                        os.path.join(wyj, "klatki", "%05d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-crf", "27", "-preset", "slow", "-movflags", "+faststart", mp4], capture_output=True)
    if r.returncode:
        raise SystemExit("ffmpeg: " + r.stderr.decode("utf-8", "replace")[-500:])
    log("gotowe", wzgl(mp4), "(%d klatek, %.1f s)" % (nr, nr / 30.0))
    # arkusz klatek odczytanych z gotowego MP4 (dowód, że film się odtwarza): 6×4, równo rozłożone
    ark = os.path.join(CEL, "pokaz_animacji_klatki.jpg")
    krok = max(1, nr // 24)
    r = subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", mp4, "-vf",
                        "select='not(mod(n\\,%d))',scale=270:270,tile=6x4:padding=4:color=0x1f1a2e" % krok,
                        "-frames:v", "1", "-fps_mode", "vfr", "-q:v", "3", ark], capture_output=True)
    if r.returncode:
        raise SystemExit("ffmpeg (arkusz): " + r.stderr.decode("utf-8", "replace")[-500:])
    log("gotowe", wzgl(ark), "(co %d. klatka)" % krok)


# --------------------------------------------------------------------------- 3. przedmioty i katalog
def _raporty():
    """{id modelu: raport z Blendera} ze wszystkich wynik/<moduł>/raport.json (pisze je przebuduj.py)."""
    r = {}
    for nazwa in sorted(os.listdir(WYNIK)):
        p = os.path.join(WYNIK, nazwa, "raport.json")
        if os.path.isfile(p):
            with open(p, encoding="utf-8") as f:
                for m in json.load(f)["modele"]:
                    r[m["id"]] = m
    return r


def _czesc(zestaw, cid, zaczep, raporty):
    """Część przedmiotu: pliki + gotowe ustawienie Attachment w Handle (zamiast ręcznego liczenia z raportu).
    glb: ramka danych (przód +Z) — Attachment.Position = minus środek skrzynki siatki od punktu zaczepienia,
    Orientation (0, 0, 0). fbx: eksport Blendera obraca model o 180° wokół pionu (przód −Z), więc pozycja
    (x, −y, z) środka skrzynki i Orientation (0, 180, 0). Kierunek po imporcie FBX nie był sprawdzony w Studio."""
    sr = (raporty.get(cid) or {}).get("srodek_skrzynki_od_zaczepu") or [0.0, 0.0, 0.0]
    return {"id": cid, "zaczep": zaczep,
            "fbx": "wynik/%s/przedmioty/%s.fbx" % (zestaw, cid), "glb": "wynik/%s/przedmioty/%s.glb" % (zestaw, cid),
            "attachment": {"glb": {"pos": [round(-v, 3) for v in sr], "rot": [0, 0, 0]},
                           "fbx": {"pos": [round(sr[0], 3), round(-sr[1], 3), round(sr[2], 3)], "rot": [0, 180, 0]}}}


def _ikona(zestaw, iid):
    return "wynik/%s/ikony/%s_ikona.png" % (zestaw, iid)


# rekwizyty postaci eksportowane osobno (w FBX postaci ich nie ma): slot i kategoria z punktu zaczepienia
REKWIZYTY = ("kot_mag", "rycerz", "karczmarz")


def przedmioty():
    """Lista przedmiotów gry (propozycja, bez statystyk) z tabel w modułach zestawów i rekwizytów postaci."""
    wynik = []
    raporty = _raporty()

    def dodaj(gid, nazwa, z, zestaw, czesci, ikona):
        cz = [_czesc(zestaw, c, zc, raporty) for c, zc in czesci]
        wynik.append({"id": gid, "nazwa": nazwa, "slot": z["slot"], "kategoria": z["kategoria"], "zestaw": zestaw,
                      "plik_modelu": cz[0]["fbx"], "czesci": cz, "plik_ikony": _ikona(zestaw, ikona)})

    # Rekrut: ZESTAW (części + modele do ikon)
    rek = {z["id"]: z for z in modul("zestaw_rekrut").ZESTAW}
    grupy = {"rekrut_przeszywanica": (["rekrut_przeszywanica", "rekrut_rekaw_l", "rekrut_rekaw_p"],
                                      "rekrut_przeszywanica_cala"),
             "rekrut_rekawice": (["rekrut_rekawica_l", "rekrut_rekawica_p"], "rekrut_rekawice"),
             "rekrut_buty": (["rekrut_but_l", "rekrut_but_p"], "rekrut_buty")}
    for z in modul("zestaw_rekrut").ZESTAW:
        gid = next((k for k, g in grupy.items() if z["id"] in g[0] or z["id"] == g[1]), z["id"])
        if any(w["id"] == gid for w in wynik):
            continue
        if gid in grupy:
            czesci, ikona = grupy[gid]
            nazwa = rek[ikona]["nazwa"]
        else:
            czesci, ikona, nazwa = [z["id"]], z["id"], z["nazwa"]
        dodaj(gid, nazwa, z, "zestaw_rekrut", [(c, rek[c]["zaczep"]) for c in czesci], ikona)
    # Rycerz: PRZEDMIOTY z listą siatek (ikona = pierwsza siatka)
    for z in modul("zestaw_rycerz").PRZEDMIOTY:
        dodaj(z["id"], z["nazwa"], z, "zestaw_rycerz", z["siatki"], z["siatki"][0][0])
    # Mag: PRZEDMIOTY z „czesc_od”; szata ma ikonę całości (mag_szata_cala)
    mag = modul("zestaw_mag").PRZEDMIOTY
    nazwy_par = {"mag_rekawica_l": ("mag_rekawice", "Rękawice runiczne"),
                 "mag_cizma_l": ("mag_cizmy", "Zakręcone ciżmy")}
    for z in mag:
        if z.get("czesc_od"):
            continue
        czesci = [z] + [c for c in mag if c.get("czesc_od") == z["id"]]
        gid, nazwa = nazwy_par.get(z["id"], (z["id"], z["nazwa"]))
        dodaj(gid, nazwa, z, "zestaw_mag", [(c["id"], c["zaczep"]) for c in czesci],
              "mag_szata_cala" if z["id"] == "mag_szata" else z["id"])
    # Zbrojownia
    for z in sorted(modul("bronie").PRZEDMIOTY, key=lambda z: z["ranga"]):
        dodaj(z["id"], z["nazwa"], z, "bronie", [(z["id"], z["zaczep"])], z["id"])
    # Rekwizyty postaci (kapelusz i kostur Kota-Maga, miecz Rycerza, chochla Karczmarza)
    for mid in REKWIZYTY:
        for o in lista(modul(mid).zbuduj()):
            if isinstance(o, Akcesorium):
                z = ({"slot": "Helmet", "kategoria": "Armor"} if o.zaczep == "HatAttachment"
                     else {"slot": "Weapon", "kategoria": "Weapons"})
                dodaj(o.id, o.nazwa, z, mid, [(o.id, o.zaczep)], o.id)
    return wynik


def zapisz_przedmioty(lista_p):
    brak = []
    for w in lista_p:
        for p in [w["plik_modelu"], w["plik_ikony"]] + [c[k] for c in w["czesci"] for k in ("fbx", "glb")]:
            if not os.path.isfile(os.path.join(TU, p)):
                brak.append(p)
    if brak:
        raise SystemExit("Brak plików wskazanych w przedmioty.json: %s" % brak)
    dane = {"status": "propozycja",
            "opis": "Lista przedmiotów z modeli w swiat/postacie (proceduralnie, Blender). Propozycja, nie kanon: "
                    "sloty, kategorie plecaka i podział na części do akceptacji Game Directora. Bez statystyk. "
                    "Ścieżki względem folderu swiat/postacie/. Przedmiot z kilkoma częściami = kilka akcesoriów "
                    "(każda część ma własny punkt zaczepienia R15). Generator: swiat/postacie/zestawienie.py.",
            "attachment": "czesci[].attachment = gotowe ustawienie obiektu Attachment w Handle części (nazwa = "
                          "czesci[].zaczep): glb = model z pliku .glb (przód +Z), fbx = model z pliku .fbx (eksport "
                          "obraca go o 180° wokół pionu). pos w studach, rot = Orientation w stopniach. Liczone z "
                          "raportu Blendera (minus środek skrzynki siatki od punktu zaczepienia). Nie sprawdzone "
                          "w Studio. Skrypt: swiat/postacie/zaczepy_akcesoriow.luau.",
            "sloty": [s for s, _ in SLOTY],
            "kategorie": ["Weapons", "Armor", "Amulets", "Others"],
            "zestawy": {z: n for z, n, _ in ZESTAWY},
            "przedmioty": lista_p}
    p = os.path.join(TU, "przedmioty.json")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dane, f, ensure_ascii=False, indent=1)
        f.write("\n")
    log("gotowe", wzgl(p), "(%d przedmiotów)" % len(lista_p))
    zapisz_luau(lista_p)


def zapisz_luau(lista_p):
    """Skrypt Luau dla człowieka w Studio: tworzy Attachmenty w Handle zaimportowanych części (dane z przedmioty.json)."""
    wiersze = []
    for w in lista_p:
        for c in w["czesci"]:
            g, f = c["attachment"]["glb"], c["attachment"]["fbx"]
            wiersze.append('\t%s = {zaczep = "%s", glb = {%s}, fbx = {%s}},' % (
                c["id"], c["zaczep"], ", ".join("%g" % v for v in g["pos"] + g["rot"]),
                ", ".join("%g" % v for v in f["pos"] + f["rot"])))
    tekst = """--!nonstrict
-- Zaczepy akcesoriów z swiat/postacie/przedmioty.json (wygenerowane przez swiat/postacie/zestawienie.py — nie edytuj).
-- Status: propozycja; NIE sprawdzone w Studio. Uruchamia człowiek, po imporcie modeli (upload robi właściciel).
--
-- Jak użyć (Studio, pasek Command Bar albo Script w ServerScriptService na czas pracy):
--   1. Zaimportuj część (np. przedmioty/zr_helm.glb albo .fbx) przez Import 3D.
--   2. Włóż MeshPart do obiektu Accessory i nazwij go "Handle"; nazwij Accessory tak jak id części (np. zr_helm).
--   3. Zaznacz Accessory (albo folder z wieloma) i uruchom ten skrypt. ZRODLO = "glb" albo "fbx" (skąd import).
--   4. Skrypt dodaje do Handle Attachment o nazwie zaczepu (np. HatAttachment) z pozycją i obrotem z tabeli.
-- Gdy model po imporcie FBX jest obrócony tyłem, użyj ZRODLO = "glb" albo popraw obrót ręcznie.
local ZRODLO = "glb"

-- id = {zaczep, glb = {x, y, z, rx, ry, rz}, fbx = {x, y, z, rx, ry, rz}}
local DANE = {
%s
}

local Selection = game:GetService("Selection")

local function ustaw(akcesorium: Instance)
	local d = DANE[akcesorium.Name]
	local handle = akcesorium:FindFirstChild("Handle")
	if not d or not handle or not handle:IsA("BasePart") then
		return
	end
	local v = d[ZRODLO]
	local att = handle:FindFirstChild(d.zaczep) or Instance.new("Attachment")
	att.Name = d.zaczep
	att.Position = Vector3.new(v[1], v[2], v[3])
	att.Orientation = Vector3.new(v[4], v[5], v[6])
	att.Parent = handle
	print("Zaczep", d.zaczep, "->", akcesorium:GetFullName())
end

for _, obiekt in Selection:Get() do
	if obiekt:IsA("Accessory") then
		ustaw(obiekt)
	end
	for _, dziecko in obiekt:GetDescendants() do
		if dziecko:IsA("Accessory") then
			ustaw(dziecko)
		end
	end
end
""" % "\n".join(wiersze)
    p = os.path.join(TU, "zaczepy_akcesoriow.luau")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(tekst)
    log("gotowe", wzgl(p), "(%d części)" % len(wiersze))


def ikony_katalogu():
    """Ikony przedmiotów do katalogu jako (slot, zestaw, nazwa, plik). Jedna ikona na przedmiot (szata i
    przeszywanica jako całość); rękawice i buty pokazane parą L/P."""
    wynik = []
    pomin = {"rekrut_przeszywanica", "rekrut_rekaw_l", "rekrut_rekaw_p", "rekrut_rekawice", "rekrut_buty"}
    for z in modul("zestaw_rekrut").ZESTAW:
        if z["id"] not in pomin:
            wynik.append((z["slot"], "zestaw_rekrut", z["nazwa"], "zestaw_rekrut/ikony/%s_ikona.png" % z["id"]))
    for z in modul("zestaw_rycerz").PRZEDMIOTY:
        siatki = z["siatki"] if z["slot"] in ("Gloves", "Boots") else z["siatki"][:1]
        for i, _ in siatki:
            n = z["nazwa"] + (" (lewa)" if i.endswith("_l") else " (prawa)" if i.endswith("_p") else "")
            wynik.append((z["slot"], "zestaw_rycerz", n, "zestaw_rycerz/ikony/%s_ikona.png" % i))
    for z in modul("zestaw_mag").PRZEDMIOTY:
        if z.get("czesc_od") == "mag_szata":
            continue
        iid = "mag_szata_cala" if z["id"] == "mag_szata" else z["id"]
        wynik.append((z["slot"], "zestaw_mag", z["nazwa"], "zestaw_mag/ikony/%s_ikona.png" % iid))
    for z in sorted(modul("bronie").PRZEDMIOTY, key=lambda z: z["ranga"]):
        wynik.append(("Weapon", "bronie", z["nazwa"], "bronie/ikony/%s_ikona.png" % z["id"]))
    for o in lista(modul("kot_mag").zbuduj()):
        if isinstance(o, Akcesorium):
            wynik.append(("Helmet" if o.zaczep == "HatAttachment" else "Weapon", "kot_mag", o.nazwa,
                          "kot_mag/ikony/%s_ikona.png" % o.id))
    return wynik


def katalog(tmp):
    from PIL import Image, ImageDraw, ImageFont
    # przymiarki zestawów: jeden rząd, jedna skala (bez obrysu: obrys rysuje kreski na drobnych detalach)
    pak = pakiet(przymiarki())
    pak["zestawienie"] = {"tryb": "rzad", "nazwa": "przymiarki", "szer": 1800, "wys": 860, "probki": 16,
                          "obrot": -26.57, "odstep": 2.2, "obrys": [False], "margines": 1.08}
    wyj = os.path.join(tmp, "przymiarki")
    uruchom_blendera(pak, wyj, "przymiarki zestawów")
    shutil.copy(os.path.join(wyj, "przymiarki.jpg"), os.path.join(CEL, "przymiarki_zestawow.jpg"))
    with open(os.path.join(wyj, "przymiarki_pozycje.json"), encoding="utf-8") as f:
        pozycje = json.load(f)

    ikony = ikony_katalogu()
    kol = {z: "#" + c for z, _, c in ZESTAWY}
    W, KOM, WYS_KOM, LEWA, X0 = 1800, 128, 156, 196, 24
    fb = ImageFont.truetype(FONT_B, 34)
    fs = ImageFont.truetype(FONT_B, 21)
    fm = ImageFont.truetype(FONT, 18)
    fn = ImageFont.truetype(FONT, 13)
    wiersze = [(s, pl, [i for i in ikony if i[0] == s]) for s, pl in SLOTY]
    for s, _, it in wiersze:
        if len(it) * KOM + LEWA + X0 * 2 > W:
            raise SystemExit("Wiersz %s za długi (%d ikon)" % (s, len(it)))
    PRZ_W, PRZ_H = W - 2 * X0, int((W - 2 * X0) * 860 / 1800)
    gora = 120
    H = gora + len(wiersze) * (WYS_KOM + 8) + 70 + PRZ_H + 70
    im = Image.new("RGB", (W, H), "#1d1729")
    dr = ImageDraw.Draw(im)
    dr.text((X0, 22), "Katalog ekwipunku", font=fb, fill="#ffffff")
    dr.text((X0 + dr.textlength("Katalog ekwipunku", font=fb) + 18, 36),
            "propozycja, nie kanon · %d ikon · wszystko proceduralnie w Blenderze" % len(ikony), font=fm, fill="#b9acd9")
    x = X0                                                      # legenda zestawów
    for z, n, c in ZESTAWY:
        dr.rounded_rectangle((x, 78, x + 18, 96), radius=4, fill="#" + c)
        dr.text((x + 26, 74), n, font=fm, fill="#e8e1f7")
        x += 26 + dr.textlength(n, font=fm) + 34
    y = gora
    for slot, pl, it in wiersze:
        dr.rounded_rectangle((X0, y, W - X0, y + WYS_KOM), radius=12, fill="#262036")
        dr.text((X0 + 18, y + WYS_KOM // 2 - 26), pl, font=fs, fill="#ffffff")
        dr.text((X0 + 18, y + WYS_KOM // 2 + 2), slot, font=fm, fill="#9a8fbb")
        for j, (_, zestaw, nazwa, plik) in enumerate(it):
            cx = X0 + LEWA + j * KOM
            dr.rounded_rectangle((cx + 4, y + 8, cx + KOM - 4, y + 8 + 104), radius=10, fill="#3a3152",
                                 outline=kol[zestaw], width=3)
            ik = Image.open(os.path.join(WYNIK, plik)).convert("RGBA")
            ik.thumbnail((96, 96), Image.LANCZOS)
            im.paste(ik, (cx + (KOM - ik.width) // 2, y + 8 + (104 - ik.height) // 2), ik)
            # nazwa pod ikoną (dwie linie)
            slowa, linie, akt = nazwa.split(), [], ""
            for s in slowa:
                t = (akt + " " + s).strip()
                if dr.textlength(t, font=fn) <= KOM - 6:
                    akt = t
                else:
                    linie.append(akt)
                    akt = s
            linie.append(akt)
            if len(linie) > 2:
                linie = linie[:2]
                while dr.textlength(linie[1] + "…", font=fn) > KOM - 6 and linie[1]:
                    linie[1] = linie[1][:-1]
                linie[1] += "…"
            for k, t in enumerate(linie):
                dr.text((cx + (KOM - dr.textlength(t, font=fn)) // 2, y + 114 + k * 17), t, font=fn, fill="#d9d0ee")
        y += WYS_KOM + 8
    y += 14
    dr.text((X0, y), "Przymiarki zestawów na szarym manekinie R15", font=fs, fill="#ffffff")
    dr.text((X0 + dr.textlength("Przymiarki zestawów na szarym manekinie R15", font=fs) + 16, y + 3),
            "(5,25 studa, jedna skala, poza „trzymanie”)", font=fm, fill="#b9acd9")
    y += 44
    prz = Image.open(os.path.join(wyj, "przymiarki.jpg")).convert("RGB").resize((PRZ_W, PRZ_H), Image.LANCZOS)
    im.paste(prz, (X0, y))
    podpis = {"przym_zestaw_rekrut": "Rekrut (start)", "przym_zestaw_rycerz": "Rycerz", "przym_zestaw_mag": "Mag"}
    zest = {"przym_zestaw_rekrut": "zestaw_rekrut", "przym_zestaw_rycerz": "zestaw_rycerz",
            "przym_zestaw_mag": "zestaw_mag"}
    for p in pozycje:
        t = podpis.get(p["id"], p["id"])
        cx = X0 + p["x"] * PRZ_W
        w = dr.textlength(t, font=fs)
        dr.rounded_rectangle((cx - w / 2 - 14, y + PRZ_H + 10, cx + w / 2 + 14, y + PRZ_H + 46), radius=10,
                             fill=kol[zest[p["id"]]])
        dr.text((cx - w / 2, y + PRZ_H + 13), t, font=fs, fill="#ffffff")
    p = os.path.join(CEL, "katalog_ekwipunku.jpg")
    im.save(p, quality=88, optimize=True)
    log("gotowe", wzgl(p), "(%d ikon, %dx%d)" % (len(ikony), W, H))


def main():
    ap = argparse.ArgumentParser(description="Zestawienie postaci i ekwipunku (prezentacja)")
    ap.add_argument("--tylko", default="skala,film,katalog,json", help="skala, film, katalog, json (po przecinku)")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    co = set(a.tylko.split(","))
    os.makedirs(CEL, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="zestawienie_")
    try:
        if "json" in co:
            zapisz_przedmioty(przedmioty())
        if "skala" in co:
            skala(tmp)
        if "katalog" in co:
            katalog(tmp)
        if "film" in co:
            film(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
