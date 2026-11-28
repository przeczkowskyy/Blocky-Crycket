#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Portrety potworów w walce: ikony z Blendera → obróbka → Roblox (przez Studio) → moduł IkonyPotworow.

    python -B swiat/test_walki2/ikony_potworow.py obrob         # 15 ikon → ikony/<klucz>.png (256 px), sha256 w JSON
    python -B swiat/test_walki2/ikony_potworow.py wgraj --sucho # co zostałoby wgrane (nic nie wysyła)
    python -B swiat/test_walki2/ikony_potworow.py wgraj         # wgrywa TYLKO ikony bez numeru obrazu albo zmienione
    python -B swiat/test_walki2/ikony_potworow.py moderacja     # odświeża stan moderacji wgranych obrazów
    python -B swiat/test_walki2/ikony_potworow.py luau          # zrodla/IkonyPotworow.luau z JSON (też po wgraj)

Źródło obrazów: swiat/postacie/wynik/<postać>/<postać>_ikona.png (render z Blendera, 512 px, przezroczyste tło).
Obróbka: przycięcie do treści, kwadrat z marginesem 4 %, 256 × 256, kolor pikseli przezroczystych „rozlany” z
krawędzi (bez ciemnej obwódki po filtrowaniu tekstury w Roblox).

Wgrywanie: konto osoby zalogowanej w Studio (narzędzie MCP open_cloud_invoke; w repo nie ma klucza Open Cloud) —
ta sama droga co swiat/miasteczko_bazar/tekstury.py. Studio przyjmuje pliki tylko z zatwierdzonych folderów, więc
plik idzie na czas wysyłki przez kopię w swiat/postacie/wynik/_ikony_walki (folder wyników postaci), potem kopia
znika. Numer operacji zapisuje się w JSON PRZED czekaniem na wynik: przerwane wgrywanie przy następnym razie tylko
dopytuje o tę operację, nie wysyła pliku drugi raz. Ikona z numerem obrazu i tym samym sha256 nigdy nie jest
wgrywana ponownie. Gra należy do innego konta niż obrazy, więc grze nadaje się prawo „Use” (jak w tekstury.py).
Zgoda: Karol 2026-11-27 („Tak, wgraj” — ikony potworów do portretów walki). Numerów NIE wpisujemy do
assets/manifest.json (tam jest nierozwiązany konflikt) — jedynym rejestrem jest ikony_potworow.json obok.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
JSON = os.path.join(TU, "ikony_potworow.json")
KATALOG = os.path.join(TU, "ikony")
LUAU = os.path.join(TU, "zrodla", "IkonyPotworow.luau")
WYNIK_POSTACI = os.path.join(REPO, "swiat", "postacie", "wynik")
POCZEKALNIA = os.path.join(WYNIK_POSTACI, "_ikony_walki")
BOK = 256
MARGINES = 0.04
ZGODA = "Karol 2026-11-27: „Tak, wgraj” (ikony potworów z Blendera do portretów walki)"

# klucz aktora walki (TestWalki2/Aktorzy, IKONY w InterfejsWalki2) → folder postaci z ikoną
POTWORY = [
    ("lesny_slime", "lesny_slime", "las"), ("muchomornik", "muchomornik", "las"),
    ("cierniowy_wilk", "cierniowy_wilk", "las"), ("lesny_troll", "lesny_troll", "las"),
    ("straznik_lasu", "straznik_gaju", "las"),
    ("rechotek", "rechotek", "bagno"), ("bulgotnik", "bulgotnik", "bagno"), ("klodoklap", "klodoklap", "bagno"),
    ("ropucha_z_chatka", "ropucha_z_chatka", "bagno"), ("straznik_topieli", "straznik_topieli", "bagno"),
    ("zwijogon", "zwijogon", "dzungla"), ("gebokwiat", "gebokwiat", "dzungla"),
    ("kokosowy_silacz", "kokosowy_silacz", "dzungla"), ("pancernik_ruin", "pancernik_ruin", "dzungla"),
    ("waz_stu_lian", "waz_stu_lian", "dzungla"),
]


def rel(p):
    return os.path.relpath(p, REPO).replace(os.sep, "/")


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def wczytaj():
    if os.path.isfile(JSON):
        with open(JSON, encoding="utf-8") as f:
            return json.load(f)
    return {}


def zapisz(d):
    d.setdefault("opis", "Portrety potworów w walce (InterfejsWalki2): obrazy wgrane do Roblox. Rejestr pisze "
                         "swiat/test_walki2/ikony_potworow.py — nie edytować ręcznie.")
    d["zgoda"] = ZGODA
    tmp = JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, JSON)


# ------------------------------------------------------------------------------------------------ obróbka
def obrob_jedna(zrodlo, cel):
    import numpy as np
    from PIL import Image, ImageFilter
    im = Image.open(zrodlo).convert("RGBA")
    a = np.asarray(im.getchannel("A"))
    ys, xs = np.nonzero(a > 8)
    if len(xs) == 0:
        raise SystemExit("pusta ikona: " + rel(zrodlo))
    im = im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    bok = int(round(max(im.size) * (1 + 2 * MARGINES)))
    kw = Image.new("RGBA", (bok, bok), (0, 0, 0, 0))
    kw.paste(im, ((bok - im.width) // 2, (bok - im.height) // 2))  # bez maski: alfa przechodzi 1:1
    kw = kw.resize((BOK, BOK), Image.LANCZOS)
    # rozlanie koloru: piksele z alfą 0 dostają kolor sąsiednich krawędzi (rozmycie premnożone, kilka promieni)
    arr = np.asarray(kw).astype(np.float32)
    rgb, al = arr[..., :3], arr[..., 3:] / 255.0
    wynik = rgb.copy()
    pusty = al[..., 0] <= 0.0
    for r in (1, 2, 4, 8, 16, 32):
        pm = Image.fromarray(np.clip(rgb * al, 0, 255).astype(np.uint8))
        aa = Image.fromarray((al[..., 0] * 255).astype(np.uint8))
        pmb = np.asarray(pm.filter(ImageFilter.BoxBlur(r))).astype(np.float32)
        aab = np.asarray(aa.filter(ImageFilter.BoxBlur(r))).astype(np.float32)[..., None] / 255.0
        ok = (aab[..., 0] > 0.004) & pusty
        wynik[ok] = (pmb / np.maximum(aab, 1e-4))[ok]
        pusty = pusty & ~ok
    out = np.concatenate([np.clip(wynik, 0, 255), arr[..., 3:]], axis=2).astype(np.uint8)
    os.makedirs(os.path.dirname(cel), exist_ok=True)
    Image.fromarray(out, "RGBA").save(cel, optimize=True)


def cmd_obrob(_a):
    d = wczytaj()
    ik = d.setdefault("ikony", {})
    for klucz, postac, biom in POTWORY:
        zrodlo = os.path.join(WYNIK_POSTACI, postac, postac + "_ikona.png")
        if not os.path.isfile(zrodlo):
            raise SystemExit("brak ikony: " + rel(zrodlo))
        cel = os.path.join(KATALOG, klucz + ".png")
        obrob_jedna(zrodlo, cel)
        e = ik.setdefault(klucz, {})
        nowe = sha(cel)
        if e.get("sha256") and e["sha256"] != nowe and e.get("obraz"):
            print("  %s: plik zmienił się po wgraniu (obraz %s) — wgraj wyśle nową wersję" % (klucz, e["obraz"]))
        e.update({"biom": biom, "zrodlo": rel(zrodlo), "zrodlo_sha256": sha(zrodlo), "plik": rel(cel), "sha256": nowe})
        print("  %-17s %s (%d B)" % (klucz, rel(cel), os.path.getsize(cel)))
    zapisz(d)
    print("obrobiono %d ikon → %s" % (len(POTWORY), rel(KATALOG)))


# ------------------------------------------------------------------------------------------------ Studio
KTO = r"""
local SS = game:GetService("StudioService")
return game:GetService("HttpService"):JSONEncode({ placeId = game.PlaceId, universeId = game.GameId, userId = SS:GetUserId() })
"""

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


class Chmura:
    def __init__(self, s, sid, RI):
        self.s, self.sid, self.RI = s, sid, RI

    def __call__(self, metoda, endpoint, body=None, files=None, scopes=("asset:read",)):
        arg = {"method": metoda, "endpoint": endpoint, "scopes": list(scopes), "studio_id": self.sid}
        if body is not None:
            arg["body"] = json.dumps(body)
        if files:
            arg["files"] = files
        wynik = self.s.call("open_cloud_invoke", arg, timeout=300)
        kod, dane = self.RI.rozbierz_odpowiedz(wynik["text"] or "")
        return kod, dane, wynik["text"] or "", bool(wynik["is_error"])


def _sesja():
    sys.path.insert(0, os.path.join(REPO, "tools"))
    sys.path.insert(0, os.path.join(REPO, "swiat", "postacie"))
    import roblox_import as RI
    from studio_mcp import StudioMCP, StudioError, first_studio_id
    return RI, StudioMCP, StudioError, first_studio_id


def moderacja_zasobu(chmura, RI, asset):
    kod, dane, tekst, _ = chmura("GET", "/assets/v1/assets/%s?readMask=moderationResult" % asset)
    if kod == 200 and dane:
        return RI.moderacja_z_zasobu(dane) or "?"
    return "? (HTTP %s)" % kod


def nadaj_uzycie(chmura, universe, ids):
    if not ids:
        return 0
    kod, dane, tekst, blad = chmura("PATCH", "/asset-permissions-api/v1/assets/permissions", {
        "subjectType": "Universe", "subjectId": str(universe), "action": "Use",
        "requests": [{"assetId": int(i)} for i in ids]}, scopes=("asset-permissions:write",))
    ok = (dane or {}).get("successAssetIds") or []
    bl = (dane or {}).get("errors") or []
    print("prawo Use dla gry: %d z %d (HTTP %s)%s" % (len(ok), len(ids), kod, (", błędy: %s" % bl[:3]) if bl else ""))
    return len(ok)


def do_wgrania(d):
    wynik = []
    for klucz, _p, _b in POTWORY:
        e = d.get("ikony", {}).get(klucz) or {}
        plik = os.path.join(REPO, e.get("plik") or "")
        if not e.get("plik") or not os.path.isfile(plik):
            print("  %s: brak obrobionego pliku (najpierw: obrob)" % klucz)
            continue
        if e.get("obraz") and e.get("wgrany_sha256") == sha(plik):
            continue  # już w Roblox — nigdy nie wgrywamy drugi raz tego samego pliku
        wynik.append(klucz)
    return wynik


def cmd_wgraj(a):
    d = wczytaj()
    lista = do_wgrania(d)
    print("do wgrania / dokończenia: %d %s" % (len(lista), ", ".join(lista)))
    if a.sucho or not lista:
        if not lista:
            cmd_luau(a)
        return
    RI, StudioMCP, StudioError, first_studio_id = _sesja()
    with StudioMCP(timeout=300) as s:
        sid = a.studio or first_studio_id(s)
        r = s.call("execute_luau", {"code": KTO, "datamodel_type": "Edit", "studio_id": sid}, timeout=60)
        kto = json.loads(r["text"].strip())
        if kto["placeId"] != RI.PLACE_ID:
            raise SystemExit("To nie jest miejsce gry — nic nie wysłano.")
        chmura = Chmura(s, sid, RI)

        def wyslij(klucz, sciezka):
            try:
                kod, dane, tekst, blad = chmura("POST", "/assets/v1/assets", {"request": {
                    "assetType": "Decal", "displayName": ("BC portret " + klucz)[:50],
                    "description": "Blocky&Crycket: portret potwora w walce (%s)" % klucz,
                    "creationContext": {"creator": {"userId": str(kto["userId"])}}}},
                    files=[{"name": "fileContent", "path": sciezka}], scopes=("asset:read", "asset:write"))
                return RI.ocen_wyslanie(kod, dane, tekst, None, blad)
            except StudioError as e:
                return RI.ocen_wyslanie(0, None, "", e, True)

        nowe = {}
        try:
            for klucz in lista:
                e = d["ikony"][klucz]
                plik = os.path.join(REPO, e["plik"])
                op = e.get("operacja") if e.get("operacja_sha256") == sha(plik) else None
                if not op:
                    if e.get("operacja_nieznana") == sha(plik):
                        print("  %s: poprzednie wysłanie skończyło się niewiadomą — sprawdź w Creator Hub, nie wysyłam "
                              "drugi raz (usuń pole operacja_nieznana, by wymusić)" % klucz)
                        continue
                    os.makedirs(POCZEKALNIA, exist_ok=True)
                    kopia = os.path.join(POCZEKALNIA, klucz + ".png")
                    shutil.copyfile(plik, kopia)
                    try:
                        etap, op, opis = wyslij(klucz, kopia)
                    finally:
                        os.remove(kopia)
                    if etap != "operacja":
                        print("  %s: NIE WGRANO (%s: %s)" % (klucz, etap, str(opis)[:200]))
                        if etap == "nieznane":
                            e["operacja_nieznana"] = sha(plik)
                            zapisz(d)
                        if etap == "nie_wyslano":
                            raise SystemExit("Studio nie przyjęło pliku z folderu wyników postaci — przerywam.")
                        continue
                    e.update({"operacja": op, "operacja_sha256": sha(plik), "wgrano": time.strftime("%Y-%m-%d %H:%M")})
                    zapisz(d)  # numer operacji zapisany, zanim zaczniemy czekać
                stan = {"asset": ""}
                koniec = time.time() + 120
                while time.time() < koniec:
                    kod, dane, tekst, _ = chmura("GET", "/assets/v1/operations/%s" % op)
                    stan = RI.wynik_operacji(dane)
                    if stan["gotowe"] or stan["blad"]:
                        break
                    time.sleep(3)
                if not stan.get("asset"):
                    print("  %s: operacja %s jeszcze bez numeru zasobu (%s) — powtórz wgraj później" % (klucz, op, stan.get("blad")))
                    continue
                e.update({"decal": str(stan["asset"]), "moderacja_decal": stan.get("moderacja") or "?"})
                zapisz(d)
                nowe[klucz] = str(stan["asset"])
                print("  %s: decal %s (%s)" % (klucz, stan["asset"], stan.get("moderacja")))
        finally:
            if os.path.isdir(POCZEKALNIA):
                try:
                    os.rmdir(POCZEKALNIA)
                except OSError:
                    pass
        # numery obrazów (Decal → Image) dla wszystkich z numerem decal, a bez numeru obrazu
        brak = {k: e["decal"] for k, e in d["ikony"].items() if e.get("decal") and not e.get("obraz")}
        if brak:
            time.sleep(3)
            kod = RESOLVE.replace("__IDS__", "{" + ",".join(str(int(v)) for v in brak.values()) + "}")
            r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=300)
            if r["is_error"]:
                raise SystemExit("Studio: " + r["text"][:300])
            pary = dict(x.split("=") for x in r["text"].strip().strip('"').split(","))
            for k, dec in brak.items():
                img = pary.get(str(dec))
                e = d["ikony"][k]
                if img and img != "nil":
                    e.update({"obraz": str(img), "wgrany_sha256": e.get("operacja_sha256") or e.get("sha256")})
                    print("  %s: obraz %s" % (k, img))
                else:
                    print("  %s: brak numeru obrazu (moderacja w toku?) — powtórz wgraj" % k)
            zapisz(d)
        ids = [e["obraz"] for e in d["ikony"].values() if e.get("obraz") and not e.get("uzycie_gry")]
        if ids and nadaj_uzycie(chmura, kto["universeId"], ids) == len(ids):
            for e in d["ikony"].values():
                if e.get("obraz") in ids:
                    e["uzycie_gry"] = True
            zapisz(d)
        _moderacja(d, chmura, RI)
    cmd_luau(a)


def _moderacja(d, chmura, RI):
    for k, e in d.get("ikony", {}).items():
        if e.get("obraz"):
            e["moderacja"] = moderacja_zasobu(chmura, RI, e["obraz"])
            e["moderacja_sprawdzona"] = time.strftime("%Y-%m-%d %H:%M")
            print("  %-17s obraz %-14s moderacja: %s" % (k, e["obraz"], e["moderacja"]))
    zapisz(d)


def cmd_moderacja(a):
    d = wczytaj()
    RI, StudioMCP, StudioError, first_studio_id = _sesja()
    with StudioMCP(timeout=300) as s:
        sid = a.studio or first_studio_id(s)
        _moderacja(d, Chmura(s, sid, RI), RI)


# ------------------------------------------------------------------------------------------------ Luau
def cmd_luau(_a):
    d = wczytaj()
    wiersze = []
    for klucz, _p, biom in POTWORY:
        e = d.get("ikony", {}).get(klucz) or {}
        if e.get("obraz"):
            wiersze.append('\t%s = "rbxassetid://%s", -- %s' % (klucz, e["obraz"], biom))
    tekst = ("--[[\n\tIkonyPotworow — WYGENEROWANE przez swiat/test_walki2/ikony_potworow.py luau z ikony_potworow.json\n"
             "\t(nie edytować ręcznie). Portrety potworów w walce: klucz aktora → obraz w Roblox (render ikony z Blendera,\n"
             "\t256 px). InterfejsWalki2 kładzie obraz na portret z pikseli; gdy obraz się nie wczyta, zostają piksele.\n]]\n"
             'if not game:GetService("RunService"):IsStudio() then\n\treturn {}\nend\n\nreturn {\n'
             + "\n".join(wiersze) + "\n}\n")
    with open(LUAU, "w", encoding="utf-8", newline="\n") as f:
        f.write(tekst)
    print("%s: %d obrazów" % (rel(LUAU), len(wiersze)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("obrob").set_defaults(fn=cmd_obrob)
    w = sub.add_parser("wgraj")
    w.add_argument("--sucho", action="store_true")
    w.add_argument("--studio", default=None)
    w.set_defaults(fn=cmd_wgraj)
    m = sub.add_parser("moderacja")
    m.add_argument("--studio", default=None)
    m.set_defaults(fn=cmd_moderacja)
    sub.add_parser("luau").set_defaults(fn=cmd_luau)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
