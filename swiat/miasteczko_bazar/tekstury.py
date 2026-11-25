#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tekstury i kreska miasteczka-bazaru w stylu sali wyboru rasy (D-147, Karol 25.11.2026). Reguły: tekstury.json.

    python -B swiat/miasteczko_bazar/tekstury.py kafle     # tnie arkusz assets/raw/TownTextures/v1.png → TownTex01–16
    python -B swiat/miasteczko_bazar/tekstury.py mapy      # kafelki → mapy do barwienia TownMap_<nazwa>.png (+ manifest)
    python -B swiat/miasteczko_bazar/tekstury.py wgraj     # mapy bez ID → Roblox (Open Cloud) + imageId ze Studio
    python -B swiat/miasteczko_bazar/tekstury.py raport    # co dostaje który materiał (bez Studio)
    python -B swiat/miasteczko_bazar/tekstury.py pomiar --etykieta po   # czas klatki i rysowanie w emulacji telefonu

Jak to działa: generuj.py woła `zastosuj(s)` — kreska (kolor tuszu i grubość listew) zmienia części w pliku, a do
czesci.json dochodzi blok „tekstury”: lista materiałów własnych (MaterialVariant: nazwa, baza, mapa, StudsPerTile,
wzór) i numer materiału każdej części. tools/studio_buduj.py tworzy z tego folder MaterialService/BC_MiasteczkoBazar
(atrybut Wygenerowane) i ustawia częściom Material + MaterialVariant w tej samej paczce, w której je buduje — więc każda
przebudowa kontenera zachowuje wygląd, a w miasteczku nie przybywa ani jedna instancja (zamiast ok. 20 000 Texture).

Mapa do barwienia: kolor części w Roblox MNOŻY mapę koloru materiału. Kafelki z paczek mają własne barwy (fiolet kamienia,
beż tynku), więc tu dzielimy je przez ich typową barwę: płaska powierzchnia mapy wychodzi prawie biała (jasnosc), a kreska,
cegły i słoje zostają jako ciemniejsze wzory. Dzięki temu miasteczko zostaje w swojej palecie, a dostaje rysunek z sali.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
PLIK = os.path.join(TU, "tekstury.json")
MANIFEST = os.path.join(REPO, "assets", "manifest.json")
ARKUSZ = os.path.join(REPO, "assets", "raw", "TownTextures", "v1.png")
FOLDER = os.path.join(REPO, "assets", "processed", "TownTextures")
KAFLE = ["Trawa", "PlytaKamienna", "Dachowka", "Lupek", "Strzecha", "Plotno", "Liscie", "Igliwie",
         "Woda", "Ziemia", "Skala", "Kora", "Mech", "TynkGladki", "Piasek", "KocieLby"]
TUSZ_GENERATORA = "1D1916"          # PALETA["tusz"] w swiat/krzywe_miasteczko/paleta.py (z niej buduje generator)
BLOK, KULA, WALEC = 0, 1, 2


def wczytaj(plik=PLIK):
    with open(plik, encoding="utf-8") as f:
        return json.load(f)


def manifest():
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)["assets"]


# =========================================================================== reguły
def pasuje(wzor, tekst):
    if wzor == "*":
        return True
    if len(wzor) > 2 and wzor[0] == "*" and wzor[-1] == "*":
        return wzor[1:-1].lower() in tekst.lower()
    if wzor[0] == "*":
        return tekst.endswith(wzor[1:])
    if wzor[-1] == "*":
        return tekst.startswith(wzor[:-1])
    return tekst == wzor


def czlony(grupa):
    """'Workspace/MiasteczkoBazar/Karczma/Barman/Glowa' → ['Karczma', 'Barman', 'Glowa']"""
    return grupa.split("/")[2:]


def wariant_czesci(c, grupa, mat, R):
    """Nazwa wariantu (klucz z R['warianty']) albo None = część zostaje gładka."""
    nazwa, kolor = c[14], c[11].upper()
    P = R["pomin"]
    tusz = R["kreska"]["kolor"].upper()
    if mat in P["materialy"] or c[13] >= 0.99 or kolor in (tusz, TUSZ_GENERATORA):
        return None
    cz = czlony(grupa)
    if any(g in cz for g in P["grupy"]) or any(pasuje(w, nazwa) for w in P["nazwy"]):
        return None
    for r in R["reguly"]:
        if not any(pasuje(w, nazwa) for w in r["nazwa"]):
            continue
        if "grupa" in r and not any(g in cz for g in r["grupa"]):
            continue
        if "kolor" in r and kolor not in [k.upper() for k in r["kolor"]]:
            continue
        return r["wariant"]
    return R["materialy"].get(mat)


def przypisz(czesci, grupy, materialy, R):
    return [wariant_czesci(c, grupy[c[1]], materialy[c[12]], R) for c in czesci]


# =========================================================================== kreska
def kreska(czesci, grupy, R):
    """Kolor tuszu i grubość listew tuszu (w miejscu). Zwraca (przebarwione, pogrubione)."""
    K = R["kreska"]
    kolor, k = K["kolor"].upper(), float(K.get("grubosc", 1.0))
    bez = set(R.get("kreska_bez_zmian_grup", []))
    narozniki = set(R.get("kreska_narozniki", []))
    n_kol = n_gr = 0
    for c in czesci:
        if c[11].upper() != TUSZ_GENERATORA or bez & set(czlony(grupy[c[1]])):
            continue
        if kolor != TUSZ_GENERATORA:
            c[11] = kolor
            n_kol += 1
        if abs(k - 1.0) < 1e-6 or c[0] == KULA or (k < 1.0 and c[14] in narozniki):
            continue
        wym = c[8:11]
        kol = sorted(range(3), key=lambda i: wym[i])            # od najmniejszego
        a, b, d = (wym[i] for i in kol)
        if d >= 2.5 * b:                                         # listwa: grubszy/cieńszy przekrój, ta sama długość
            for i in kol[:2]:                                    # + 0,03: ściany nie wpadają w płaszczyznę sąsiada (migotanie)
                c[8 + i] = round(max(0.06, wym[i] * k + (0.03 if k > 1.0 else -0.03)), 3)
        elif b >= 2.5 * a:                                       # podkładka (ramka za oknem, obrys): szerszy brzeg
            for i in kol[1:]:
                c[8 + i] = round(max(0.05, wym[i] + 2 * 0.3 * (k - 1.0)), 3)
        else:
            continue
        n_gr += 1
    return n_kol, n_gr


# =========================================================================== blok do czesci.json
def nazwa_mapy(w):
    return "TownMap_" + w


def blok_tekstur(R, przypisania, man=None):
    """Blok „tekstury” do czesci.json: definicje wariantów z ID map (tylko wgrane) + numer wariantu każdej części."""
    man = manifest() if man is None else man
    uzyte = sorted({w for w in przypisania if w})
    defs, idx, brak = [], {}, []
    for w in uzyte:
        v = R["warianty"][w]
        img = (man.get(nazwa_mapy(w)) or {}).get("roblox_image")
        if not img:
            brak.append(w)
            continue
        idx[w] = len(defs) + 1
        defs.append([R["prefiks_wariantow"] + w, "SmoothPlastic", "rbxassetid://" + str(img), v["studs"], v["wzor"]])
    return {"kontener": R["kontener_wariantow"], "definicje": defs,
            "czesci": [idx.get(w, 0) if w else 0 for w in przypisania]}, brak


def zastosuj(s, R=None):
    """Dla generuj.py: kreska w częściach sceny + blok tekstur. Zwraca (blok, opis)."""
    R = wczytaj() if R is None else R
    n_kol, n_gr = kreska(s.czesci, s.grupy, R)
    przyp = przypisz(s.czesci, s.grupy, s.materialy, R)
    blok, brak = blok_tekstur(R, przyp)
    n_tex = sum(1 for x in blok["czesci"] if x)
    opis = "KRESKA: kolor %s, grubość %.2f (przebarwione %d, zmieniony przekrój %d) · TEKSTURY: %d z %d części, %d materiałów" % (
        R["kreska"]["kolor"], float(R["kreska"].get("grubosc", 1.0)), n_kol, n_gr, n_tex, len(s.czesci), len(blok["definicje"]))
    if brak:
        opis += " · bez wgranej mapy (gładkie): " + ", ".join(brak)
    return blok, opis


# =========================================================================== obróbka obrazów
def _np():
    import numpy as np
    from PIL import Image
    return np, Image


def bez_szwow(a, pas=0.25):
    """Zszywa kafelek: brzegi bierze z kopii przesuniętej o pół boku (ciągłej przez krawędź), środek z oryginału."""
    np, _ = _np()
    h, w = a.shape[:2]
    s = np.roll(np.roll(a, h // 2, 0), w // 2, 1)
    y = np.minimum(np.arange(h), h - 1 - np.arange(h)) / (h * pas)
    x = np.minimum(np.arange(w), w - 1 - np.arange(w)) / (w * pas)
    m = np.clip(np.minimum.outer(y, x), 0.0, 1.0)
    m = m * m * (3 - 2 * m)
    return a * m[..., None] + s * (1 - m[..., None])


def mapa_do_barwienia(sciezka, v, bok=512):
    """Kafelek → mapa koloru do mnożenia przez kolor części (bok × bok, RGB). 512 px wystarcza na powtórzenie 3–12 st
    na ekranie telefonu, a to 4 × mniej pamięci tekstur i pobierania niż 1024 px (25 map ≈ 7 MB PNG zamiast ≈ 30 MB)."""
    np, Image = _np()
    im = Image.open(sciezka).convert("RGB")
    r = float(v.get("ramka", 0))
    if r:
        W, H = im.size
        im = im.crop((int(W * r), int(H * r), int(W * (1 - r)), int(H * (1 - r))))
    im = im.resize((1024, 1024), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255.0
    if v.get("zszyj"):
        a = bez_szwow(a)
    if bok != 1024:
        a = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).resize((bok, bok), Image.LANCZOS)
                       ).astype(np.float32) / 255.0
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    ref = np.median(a.reshape(-1, 3), axis=0) + 1e-4
    ref_l = float(np.median(lum)) + 1e-4
    r_l = (lum / ref_l)[..., None]
    wyn = r_l + float(v.get("nasycenie", 0.5)) * (a / ref - r_l)
    wyn = np.clip(wyn * float(v.get("jasnosc", 0.96)), 0.0, 1.0)
    return Image.fromarray((wyn * 255 + 0.5).astype(np.uint8))


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def man_cli(*args):
    r = subprocess.run([sys.executable, "-B", os.path.join(REPO, "tools", "manifest.py")] + list(args),
                       capture_output=True, text=True, encoding="utf-8", cwd=REPO)
    if r.returncode:
        raise SystemExit("manifest.py %s: %s" % (args[:2], (r.stderr or r.stdout)[-400:]))
    return r.stdout


def cmd_kafle(_a):
    """Arkusz z Higgsfield (szare tło) → 16 kafelków TownTexNN_<nazwa>.png narzędziem tools/tex_sheet.py + manifest."""
    r = subprocess.run([sys.executable, "-B", os.path.join(REPO, "tools", "tex_sheet.py"), ARKUSZ, FOLDER, "TownTex"] + KAFLE
                       + ["--prog", "212", "--wciecie", "20"], cwd=REPO)
    if r.returncode:
        raise SystemExit(r.returncode)
    man = manifest()
    pp = os.path.join(os.path.dirname(ARKUSZ), "prompt.txt")
    prompt = open(pp, encoding="utf-8").read().strip() if os.path.exists(pp) else ""
    for i, n in enumerate(KAFLE):
        klucz = "TownTex%02d" % (i + 1)
        rel = "assets/processed/TownTextures/TownTex%02d_%s.png" % (i + 1, n)
        if (man.get(klucz) or {}).get("processed") == rel:
            continue
        pola = ["category=texture", "status=processed", "processed=" + rel, "raw=assets/raw/TownTextures/v1.png",
                "usage=Tekstury miasteczka-bazaru (źródło map do barwienia TownMap_*)",
                "notes=kafelek %d/16 arkusza 4x4 z Higgsfield (nano_banana_2_1, 4k, referencje: arkusz v2 sali i KeyArt_ref), "
                "25.11.2026, D-147; świadomie bez stałego początku Glossy Ink (cienka brązowa kreska jak arkusz v2 sali); "
                "prompt w TownTex01" % (i + 1)]
        if i == 0 and prompt:
            pola.append("prompt=" + prompt)
        man_cli("upsert", klucz, *pola)
    print("kafle: %d w %s" % (len(KAFLE), os.path.relpath(FOLDER, REPO)))


def cmd_mapy(a):
    R = wczytaj()
    man = manifest()
    os.makedirs(FOLDER, exist_ok=True)
    for w, v in R["warianty"].items():
        zr = (man.get(v["zrodlo"]) or {}).get("processed")
        if not zr:
            print("  %-14s brak źródła %s w manifeście" % (w, v["zrodlo"]))
            continue
        rel = "assets/processed/TownTextures/%s.png" % nazwa_mapy(w)
        dst = os.path.join(REPO, rel)
        stary = sha(dst) if os.path.exists(dst) else None
        mapa_do_barwienia(os.path.join(REPO, zr), v, int(R.get("bok_map", 512))).save(dst, optimize=True)
        zmiana = stary != sha(dst)
        klucz = nazwa_mapy(w)
        if zmiana or klucz not in man:
            man_cli("upsert", klucz, "category=texture", "status=processed", "processed=" + rel,
                    "usage=Miasteczko-bazar: mapa koloru MaterialVariant BC_Bazar_%s (barwiona kolorem części)" % w,
                    "notes=z %s (%s) przez swiat/miasteczko_bazar/tekstury.py mapy; D-147" % (v["zrodlo"], zr))
        print("  %-14s %s %s" % (w, rel, "(nowa)" if zmiana else "(bez zmian)"))
    if a.podglad:
        podglad_map(R)


def podglad_map(R):
    """Plansza: mapa do barwienia × kolor części, po 2 × 2 powtórzenia (sprawdzenie szwów i barwy)."""
    np, Image = _np()
    kolory = {"Tynk": "FFE6A8", "TynkGladki": "BDF0CB", "Kamien": "E3C3A8", "KamienOkragly": "6B5848", "Cegla": "6B5848",
              "Belka": "5C3A22", "Deski": "D49A5A", "Skrzynia": "8B5A2E", "Beczka": "8B5A2E", "Zelazo": "4A5368",
              "Zloto": "F2B030", "Trawa": "6DB33F", "Bruk": "E0C48E", "Dachowka": "D8452E", "Lupek": "5E5A78",
              "Strzecha": "E2A93A", "Plotno": "D8452E", "Liscie": "72BF3A", "Igliwie": "3F8F35", "Woda": "2389D0",
              "Ziemia": "867555", "Skala": "4A4560", "Kora": "8B5A2E", "Mech": "7FBF3F", "Piasek": "C08A55"}
    W = 192
    nazwy = list(R["warianty"])
    kol = 6
    rz = (len(nazwy) + kol - 1) // kol
    pl = Image.new("RGB", (kol * (2 * W + 10), rz * (2 * W + 10)), "white")
    for i, w in enumerate(nazwy):
        p = os.path.join(FOLDER, nazwa_mapy(w) + ".png")
        if not os.path.exists(p):
            continue
        m = np.asarray(Image.open(p).convert("RGB").resize((W, W))).astype(np.float32) / 255
        k = np.array([int(kolory.get(w, "CCCCCC")[j:j + 2], 16) for j in (0, 2, 4)], dtype=np.float32) / 255
        t = Image.fromarray((np.clip(m * k, 0, 1) * 255).astype(np.uint8))
        q = Image.new("RGB", (2 * W, 2 * W))
        for dx in (0, W):
            for dy in (0, W):
                q.paste(t, (dx, dy))
        pl.paste(q, ((i % kol) * (2 * W + 10), (i // kol) * (2 * W + 10)))
    wyj = os.path.join(FOLDER, "_mapy_barwione.jpg")
    pl.save(wyj, quality=85)
    print("podgląd:", os.path.relpath(wyj, REPO))


# =========================================================================== wgrywanie
RESOLVE = r'''
local IS = game:GetService("InsertService")
local wyn = {}
for _, id in __IDS__ do
	local ok, m = pcall(IS.LoadAsset, IS, id)
	local img = nil
	if ok and m then
		local d = m:FindFirstChildWhichIsA("Decal", true)
		img = d and d.Texture:match("%d+")
		m:Destroy()
	end
	table.insert(wyn, tostring(id) .. "=" .. tostring(img))
end
return table.concat(wyn, ",")
'''


KTO = r"""
local SS = game:GetService("StudioService")
return game:GetService("HttpService"):JSONEncode({ placeId = game.PlaceId, universeId = game.GameId, userId = SS:GetUserId() })
"""


def nadaj_uzycie(chmura, universe, ids):
    """Gra należy do innego konta niż obrazy (wgrane na konto osoby w Studio) — bez prawa „Use” dla universe obraz
    może się nie wczytać w grze. PATCH /asset-permissions-api/v1/assets/permissions (zakres asset-permissions:write)."""
    if not ids:
        return
    kod, dane, tekst, blad = chmura("PATCH", "/asset-permissions-api/v1/assets/permissions", {
        "subjectType": "Universe", "subjectId": str(universe), "action": "Use",
        "requests": [{"assetId": int(i)} for i in ids]}, scopes=("asset-permissions:write",))
    ok = len((dane or {}).get("successAssetIds") or [])
    bl = (dane or {}).get("errors") or []
    print("prawo Use dla gry: %d z %d obrazów%s" % (ok, len(ids), (", błędy: %s" % bl[:3]) if bl else ""))


def cmd_wgraj(a):
    """Mapy bez roblox_image → Roblox przez Studio (narzędzie MCP open_cloud_invoke, konto osoby zalogowanej w Studio —
    ta sama droga co modele w swiat/postacie/roblox_import.py; bez klucza w .env) → imageId ze Studio → manifest.
    Zgoda: Karol 14.11.2026 — modele i materiały do gry B&C wgrywamy bez pytania, póki gra jest w testach; D-147 (25.11)
    zleca tekstury miasteczka. tools/manifest.py approve zapisuje sha256 dokładnie wgranego pliku.
    Studio przyjmuje pliki tylko z zatwierdzonych folderów; gdy assets/processed nim nie jest, plik idzie na czas wgrania
    przez kopię w swiat/postacie/wynik/_tekstury (zatwierdzony folder wyników postaci), a kopia jest potem usuwana."""
    import shutil
    R = wczytaj()
    man = manifest()
    do_wgrania = []
    for w in R["warianty"]:
        k = nazwa_mapy(w)
        e = man.get(k) or {}
        if not e.get("processed"):
            print("  %s: brak mapy (najpierw: tekstury.py mapy)" % k)
            continue
        if e.get("roblox_image") and e.get("approved_sha256") == sha(os.path.join(REPO, e["processed"])):
            continue
        do_wgrania.append(k)
    print("do wgrania: %d" % len(do_wgrania))
    if a.ile:
        do_wgrania = do_wgrania[:a.ile]
    if a.sucho:
        return
    sys.path.insert(0, os.path.join(REPO, "tools"))
    sys.path.insert(0, os.path.join(REPO, "swiat", "postacie"))
    import roblox_import as RI
    from studio_mcp import StudioMCP, StudioError, first_studio_id
    poczekalnia = os.path.join(REPO, "swiat", "postacie", "wynik", "_tekstury")
    decale = {}
    with StudioMCP(timeout=300) as s:
        sid = first_studio_id(s)
        r = s.call("execute_luau", {"code": KTO, "datamodel_type": "Edit", "studio_id": sid}, timeout=60)
        kto = json.loads(r["text"].strip())
        if kto["placeId"] != RI.PLACE_ID:
            raise SystemExit("To nie jest miejsce gry — nic nie wysłano.")

        def chmura(metoda, endpoint, body=None, files=None, scopes=("asset:read",)):
            arg = {"method": metoda, "endpoint": endpoint, "scopes": list(scopes), "studio_id": sid}
            if body is not None:
                arg["body"] = json.dumps(body)
            if files:
                arg["files"] = files
            wynik = s.call("open_cloud_invoke", arg, timeout=300)
            kod, dane = RI.rozbierz_odpowiedz(wynik["text"] or "")
            return kod, dane, wynik["text"] or "", bool(wynik["is_error"])

        def wyslij(k, sciezka):
            try:
                kod, dane, tekst, blad = chmura("POST", "/assets/v1/assets", {"request": {
                    "assetType": "Decal", "displayName": k[:50], "description": "Blocky&Crycket: tekstura miasteczka (%s)" % k,
                    "creationContext": {"creator": {"userId": str(kto["userId"])}}}},
                    files=[{"name": "fileContent", "path": sciezka}], scopes=("asset:read", "asset:write"))
                return RI.ocen_wyslanie(kod, dane, tekst, None, blad)
            except StudioError as e:
                return RI.ocen_wyslanie(0, None, "", e, True)

        for k in do_wgrania:
            plik = os.path.join(REPO, manifest()[k]["processed"])
            man_cli("approve", k)
            etap, op, opis = wyslij(k, plik)
            kopia = None
            if etap == "nie_wyslano":                          # folder assets/ nie jest zatwierdzony w Studio
                os.makedirs(poczekalnia, exist_ok=True)
                kopia = os.path.join(poczekalnia, os.path.basename(plik))
                shutil.copyfile(plik, kopia)
                try:
                    etap, op, opis = wyslij(k, kopia)
                finally:
                    os.remove(kopia)
            if etap != "operacja":
                print("  %s: NIE WGRANO (%s: %s)" % (k, etap, str(opis)[:160]))
                continue
            stan = {"asset": ""}
            koniec = time.time() + 90
            while time.time() < koniec:
                kod, dane, tekst, _ = chmura("GET", "/assets/v1/operations/%s" % op)
                stan = RI.wynik_operacji(dane)
                if stan["gotowe"] or stan["blad"]:
                    break
                time.sleep(3)
            if not stan.get("asset"):
                print("  %s: operacja bez numeru zasobu (%s) — sprawdź później" % (k, stan.get("blad")))
                man_cli("upsert", k, "notes=" + manifest()[k].get("notes", "") + " | wgrywanie: operacja %s bez wyniku" % op)
                continue
            decale[k] = stan["asset"]
            man_cli("upsert", k, "roblox_decal=%s" % stan["asset"], "moderation=%s" % (stan.get("moderacja") or "?"))
            print("  %s: decal %s (%s)" % (k, stan["asset"], stan.get("moderacja")))
        if os.path.isdir(poczekalnia):
            try:
                os.rmdir(poczekalnia)
            except OSError:
                pass
        if not decale:
            nadaj_uzycie(chmura, kto["universeId"], [manifest()[nazwa_mapy(w)].get("roblox_image") for w in R["warianty"]
                                                     if manifest().get(nazwa_mapy(w), {}).get("roblox_image")])
            return
        time.sleep(3)
        kod = RESOLVE.replace("__IDS__", "{" + ",".join(str(int(v)) for v in decale.values()) + "}")
        r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=300)
        if r["is_error"]:
            raise SystemExit("Studio: " + r["text"][:300])
        pary = dict(x.split("=") for x in r["text"].strip().strip('"').split(","))
        for k, d in decale.items():
            img = pary.get(str(d))
            if img and img != "nil":
                man_cli("upsert", k, "roblox_image=%s" % img, "status=in_roblox")
                print("  %s: image %s" % (k, img))
            else:
                print("  %s: brak imageId (moderacja w toku?) — powtórz: tekstury.py wgraj" % k)
        m = manifest()
        nadaj_uzycie(chmura, kto["universeId"], [m[nazwa_mapy(w)]["roblox_image"] for w in R["warianty"]
                                                 if m.get(nazwa_mapy(w), {}).get("roblox_image")])


# =========================================================================== raport
def cmd_raport(a):
    import collections
    R = wczytaj()
    with open(os.path.join(TU, "czesci.json"), encoding="utf-8") as f:
        d = json.load(f)
    G, M, C = d["grupy"], d["materialy"], d["czesci"]
    przyp = przypisz(C, G, M, R)
    ile = collections.Counter(w for w in przyp if w)
    print("części: %d · z teksturą: %d (%.0f%%) · gładkie: %d" % (len(C), sum(ile.values()), 100.0 * sum(ile.values()) / len(C),
                                                               len(C) - sum(ile.values())))
    for w, n in ile.most_common():
        print("  %-14s %5d" % (w, n))
    if a.gladkie:
        tusz = {R["kreska"]["kolor"].upper(), TUSZ_GENERATORA}
        gl = collections.Counter((re.sub(r"\s*\d+$", "", c[14]), M[c[12]], c[11]) for c, w in zip(C, przyp)
                                 if not w and c[11].upper() not in tusz and M[c[12]] != "Neon")
        print("gładkie (bez tuszu i Neonu), najczęstsze:")
        for (n, m, k), x in gl.most_common(a.gladkie):
            print("  %4d  %-28s %-13s %s" % (x, n, m, k))


# =========================================================================== pomiar
POMIAR = r'''
local S = game:GetService("Stats")
local RS = game:GetService("RunService")
local svc = game:GetService("StudioDeviceSimulatorService")
local HS = game:GetService("HttpService")
local cam = workspace.CurrentCamera
local stara = cam.CFrame
local wynik = { urzadzenie = "brak", ujecia = {} }
local ok, err = pcall(function()
	for _, id in svc:GetDeviceListAsync() do
		local info = svc:GetDeviceInfoAsync(id)
		if info.Name == "__URZADZENIE__" then
			svc:SetDeviceAsync(id)
			task.wait(0.5)
			wynik.urzadzenie = info.Name .. " " .. info.Width .. "x" .. info.Height
			break
		end
	end
end)
if not ok then wynik.blad_emulacji = tostring(err) end
wynik.viewport = tostring(cam.ViewportSize)
local f = workspace:FindFirstChild("MiasteczkoBazar")
local n, czesci, warianty = 0, 0, 0
if f then
	for _, d in f:GetDescendants() do
		n += 1
		if d:IsA("BasePart") then
			czesci += 1
			if d.MaterialVariant ~= "" then warianty += 1 end
		end
	end
end
wynik.instancje_miasteczka, wynik.czesci, wynik.czesci_z_wariantem = n, czesci, warianty
local mf = game:GetService("MaterialService"):FindFirstChild("__KONTENER__")
wynik.warianty_w_MaterialService = mf and #mf:GetChildren() or 0
local AB = __AB__
local proby = {}
for _, u in __UJECIA__ do
	if AB then
		for i = 1, 2 do
			table.insert(proby, { u, "z_teksturami" })
			table.insert(proby, { u, "bez_tekstur" })
		end
	else
		table.insert(proby, { u, "" })
	end
end
for _, pr in proby do
	local u, tryb = pr[1], pr[2]
	if mf then mf.Parent = (tryb == "bez_tekstur") and nil or game:GetService("MaterialService") end
	cam.CFrame = CFrame.lookAt(Vector3.new(u[2], u[3], u[4]), Vector3.new(u[5], u[6], u[7]))
	task.wait(2.0)
	local dts, cpu, gpu, dc, tri, sh = {}, 0, 0, 0, 0, 0
	local k = 0
	local t0 = os.clock()
	local c = RS.RenderStepped:Connect(function(dt)
		table.insert(dts, dt)
		cpu += S.RenderCPUFrameTime
		gpu += S.RenderGPUFrameTime
		dc += S.SceneDrawcallCount
		tri += S.SceneTriangleCount
		sh += S.ShadowsDrawcallCount
		k += 1
	end)
	task.wait(__SEKUNDY__)
	c:Disconnect()
	table.sort(dts)
	local suma = 0
	for _, x in dts do suma += x end
	k = math.max(k, 1)
	table.insert(wynik.ujecia, {
		nazwa = u[1] .. (tryb ~= "" and (" " .. tryb) or ""), klatek = #dts,
		klatka_sr_ms = #dts > 0 and 1000 * suma / #dts or -1,
		klatka_p95_ms = #dts > 0 and 1000 * dts[math.max(1, math.ceil(#dts * 0.95))] or -1,
		render_cpu_ms = 1000 * cpu / k, render_gpu_ms = 1000 * gpu / k,
		drawcalle = dc / k, trojkaty = tri / k, drawcalle_cieni = sh / k,
	})
end
if mf then mf.Parent = game:GetService("MaterialService") end
cam.CFrame = stara
pcall(function() svc:StopSimulationAsync() end)
return HS:JSONEncode(wynik)
'''


def cmd_pomiar(a):
    sys.path.insert(0, os.path.join(REPO, "tools"))
    from studio_mcp import StudioMCP, first_studio_id
    R = wczytaj()
    with open(os.path.join(TU, "ujecia_tekstury.json"), encoding="utf-8") as f:
        uj = json.load(f)
    lista = "{" + ",".join('{"%s",%s,%s}' % (u[0], ",".join(map(str, u[1])), ",".join(map(str, u[2]))) for u in uj) + "}"
    kod = (POMIAR.replace("__UJECIA__", lista).replace("__SEKUNDY__", str(a.sekundy)).replace("__URZADZENIE__", a.urzadzenie)
           .replace("__KONTENER__", R["kontener_wariantow"]).replace("__AB__", "true" if a.ab else "false"))
    with StudioMCP(timeout=600) as s:
        sid = first_studio_id(s)
        r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=600)
    if r["is_error"]:
        raise SystemExit("Studio: " + r["text"][:400])
    txt = r["text"].strip()
    w = json.loads(txt[txt.index("{"):txt.rindex("}") + 1])
    w["etykieta"], w["czas"] = a.etykieta, time.strftime("%Y-%m-%d %H:%M")
    wyj = os.path.join(TU, "podglad", "tekstury_pomiar.json")
    dane = {}
    if os.path.exists(wyj):
        with open(wyj, encoding="utf-8") as f:
            dane = json.load(f)
    dane[a.etykieta] = w
    with open(wyj, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dane, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("%s · %s · viewport %s · miasteczko: %d instancji, %d części, %d z materiałem własnym" % (
        a.etykieta, w["urzadzenie"], w["viewport"], w["instancje_miasteczka"], w["czesci"], w["czesci_z_wariantem"]))
    for u in w["ujecia"]:
        print("  %-30s klatka %.1f ms (p95 %.1f, %d kl.) · render CPU %.2f ms · GPU %.2f ms · drawcalle %.0f (+cienie %.0f) · trójkąty %.0f"
              % (u["nazwa"], u["klatka_sr_ms"], u["klatka_p95_ms"], u["klatek"], u["render_cpu_ms"], u["render_gpu_ms"],
                 u["drawcalle"], u["drawcalle_cieni"], u["trojkaty"]))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Tekstury i kreska miasteczka-bazaru")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("kafle").set_defaults(fn=cmd_kafle)
    p = sub.add_parser("mapy")
    p.add_argument("--podglad", action="store_true")
    p.set_defaults(fn=cmd_mapy)
    p = sub.add_parser("wgraj")
    p.add_argument("--sucho", action="store_true")
    p.add_argument("--ile", type=int, default=0, help="wgraj najwyżej N map (próba)")
    p.set_defaults(fn=cmd_wgraj)
    p = sub.add_parser("raport")
    p.add_argument("--gladkie", type=int, default=0, help="pokaż N najczęstszych części bez tekstury")
    p.set_defaults(fn=cmd_raport)
    p = sub.add_parser("pomiar")
    p.add_argument("--etykieta", required=True)
    p.add_argument("--sekundy", type=float, default=4.0)
    p.add_argument("--urzadzenie", default="Samsung Galaxy A06")
    p.add_argument("--ab", action="store_true", help="na każdym ujęciu na zmianę: z materiałami własnymi i bez nich "
                   "(folder wariantów na chwilę odpięty z MaterialService i od razu przywracany)")
    p.set_defaults(fn=cmd_pomiar)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
