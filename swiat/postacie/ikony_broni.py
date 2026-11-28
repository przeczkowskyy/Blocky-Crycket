#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ikony broni Maga i Zwiadowcy (pula Lv 1–10) → Roblox (przez Studio) → rejestr ikony_broni.json i moduł IkonyBroni.

    python -B swiat/postacie/ikony_broni.py stan           # lista ikon, sha256, co już jest w Roblox (bez Studio)
    python -B swiat/postacie/ikony_broni.py wgraj --sucho  # co zostałoby wgrane (nic nie wysyła, bez Studio)
    python -B swiat/postacie/ikony_broni.py wgraj          # wgrywa TYLKO ikony bez numeru obrazu albo zmienione
    python -B swiat/postacie/ikony_broni.py moderacja      # odświeża stan moderacji wgranych obrazów
    python -B swiat/postacie/ikony_broni.py luau           # roblox/IkonyBroni.luau z JSON (też po wgraj)

Źródło obrazów: assets/processed/Item<…>.png (512 px, przezroczyste tło) — ikony z arkuszy Higgsfield (styl Glossy
Ink) z 27.11.2026, warianty „Mag A” i „Zwiadowca B” wybrane przez Karola; wycinki z arkuszy w
assets/raw/BronieKlas/ciete/ (poza gitem). Ten plik ikon nie obrabia — wgrywa dokładnie pliki 512 px z processed/.

Wgrywanie: konto osoby zalogowanej w Studio (narzędzie MCP open_cloud_invoke; tools/roblox_upload.py nie ma dziś
konfiguracji Open Cloud) — ta sama droga co swiat/test_walki2/ikony_potworow.py. Studio przyjmuje pliki tylko
z zatwierdzonych folderów, więc plik idzie na czas wysyłki przez kopię w swiat/postacie/wynik/_ikony_broni (folder
wyników postaci), potem kopia znika. Numer operacji zapisuje się w JSON PRZED czekaniem na wynik: przerwane
wgrywanie przy następnym razie tylko dopytuje o tę operację, nie wysyła pliku drugi raz. Ikona z numerem obrazu
i tym samym sha256 nigdy nie jest wgrywana ponownie. Gra należy do innego konta niż obrazy, więc grze nadaje się
prawo „Use”. Zgoda: Karol 2026-11-27 („Tak, wgraj” — dokładnie te 10 ikon). Numerów NIE wpisujemy do
assets/manifest.json (tam jest nierozwiązany konflikt) — jedynym rejestrem jest ikony_broni.json obok.
Obrazów nie wstawiamy do Studio ani nie podpinamy do UI (okno ekwipunku i sklep to pliki Pawła) — tylko rejestr
i moduł Luau z mapą nazwa → rbxassetid.
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
JSON = os.path.join(TU, "ikony_broni.json")
LUAU = os.path.join(TU, "roblox", "IkonyBroni.luau")
IKONY_DIR = os.path.join(REPO, "assets", "processed")
WYCINKI = "assets/raw/BronieKlas/ciete"
POCZEKALNIA = os.path.join(TU, "wynik", "_ikony_broni")
ZGODA = "Karol 2026-11-27: „Tak, wgraj” (10 ikon broni Maga i Zwiadowcy z Higgsfield)"

# klucz (nazwa pliku ikony w assets/processed) -> nazwa (propozycja z puli Lv 1–10), klasa, wycinek z arkusza,
# id modelu 3D (swiat/postacie/bronie_klas.py), przedmiot zestawu (5. przedmiot slotu)
IKONY = [
    ("ItemStickWand", "Różdżka z Patyka", "mag", "mag_a_1.png", "mag_rozdzka_z_patyka", False),
    ("ItemBroomStaff", "Kostur z Miotły", "mag", "mag_a_2.png", "mag_kostur_z_miotly", False),
    ("ItemMagicRollingPin", "Wałek Czarodziejski", "mag", "mag_a_3.png", "mag_walek_czarodziejski", False),
    ("ItemCandleWand", "Różdżka ze Świeczki", "mag", "mag_a_4.png", "mag_rozdzka_ze_swieczki", False),
    ("ItemApprenticeStaff", "Kostur Ucznia", "mag", "mag_a_5.png", "mag_kostur_ucznia", True),
    ("ItemBranchSlingshot", "Proca z Gałęzi", "zwiadowca", "zwiad_b_1.png", "zwiad_proca_z_galezi", False),
    ("ItemHangerBow", "Łuk z Wieszaka", "zwiadowca", "zwiad_b_2.png", "zwiad_luk_z_wieszaka", False),
    ("ItemButterKnife", "Nóż do Masła", "zwiadowca", "zwiad_b_3.png", "zwiad_noz_do_masla", False),
    ("ItemPineconeDagger", "Sztylet z Szyszki", "zwiadowca", "zwiad_b_4.png", "zwiad_sztylet_z_szyszki", False),
    ("ItemTrackerBow", "Łuk Tropiciela", "zwiadowca", "zwiad_b_5.png", "zwiad_luk_tropiciela", True),
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
    d.setdefault("opis", "Ikony broni Maga i Zwiadowcy (pula Lv 1–10): obrazy wgrane do Roblox. Rejestr pisze "
                         "swiat/postacie/ikony_broni.py — nie edytować ręcznie. Nazwy to propozycja, nie kanon.")
    d["zgoda"] = ZGODA
    tmp = JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, JSON)


def uzupelnij(d):
    """Wpisy rejestru dla każdej ikony: plik, sha256 pliku do wgrania, nazwa, klasa, wycinek, model 3D."""
    ik = d.setdefault("ikony", {})
    for klucz, nazwa, klasa, wycinek, model, zestaw in IKONY:
        plik = os.path.join(IKONY_DIR, klucz + ".png")
        if not os.path.isfile(plik):
            raise SystemExit("brak ikony: " + rel(plik))
        e = ik.setdefault(klucz, {})
        nowe = sha(plik)
        if e.get("sha256") and e["sha256"] != nowe and e.get("obraz"):
            print("  %s: plik zmienił się po wgraniu (obraz %s) — wgraj wyśle nową wersję" % (klucz, e["obraz"]))
        e.update({"nazwa": nazwa, "klasa": klasa, "zestaw": zestaw, "plik": rel(plik), "sha256": nowe,
                  "wycinek_arkusza": WYCINKI + "/" + wycinek, "model": model})
    return d


def cmd_stan(_a):
    d = uzupelnij(wczytaj())
    for klucz, *_ in IKONY:
        e = d["ikony"][klucz]
        print("  %-20s %-22s %s  obraz: %s  moderacja: %s" % (klucz, e["nazwa"], e["sha256"][:12],
                                                              e.get("obraz") or "-", e.get("moderacja") or "-"))


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
    sys.path.insert(0, TU)
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
    for klucz, *_ in IKONY:
        e = d.get("ikony", {}).get(klucz) or {}
        plik = os.path.join(REPO, e.get("plik") or "")
        if not e.get("plik") or not os.path.isfile(plik):
            print("  %s: brak pliku ikony" % klucz)
            continue
        if e.get("obraz") and e.get("wgrany_sha256") == sha(plik):
            continue  # już w Roblox — nigdy nie wgrywamy drugi raz tego samego pliku
        wynik.append(klucz)
    return wynik


def cmd_wgraj(a):
    d = uzupelnij(wczytaj())
    if not a.sucho:
        zapisz(d)
    lista = do_wgrania(d)
    print("do wgrania / dokończenia: %d %s" % (len(lista), ", ".join(lista)))
    if a.sucho:
        for k in lista:
            e = d["ikony"][k]
            print("  %-20s %s (%d B) → Decal „BC ikona %s”, potem obraz, prawo Use dla gry"
                  % (k, e["plik"], os.path.getsize(os.path.join(REPO, e["plik"])), k))
        print("sucho: nic nie wysłano (Studio nieużywane)")
        return
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
            e = d["ikony"][klucz]
            try:
                kod, dane, tekst, blad = chmura("POST", "/assets/v1/assets", {"request": {
                    "assetType": "Decal", "displayName": ("BC ikona " + klucz)[:50],
                    "description": "Blocky&Crycket: ikona broni (%s, klasa %s)" % (e["nazwa"], e["klasa"]),
                    "creationContext": {"creator": {"userId": str(kto["userId"])}}}},
                    files=[{"name": "fileContent", "path": sciezka}], scopes=("asset:read", "asset:write"))
                return RI.ocen_wyslanie(kod, dane, tekst, None, blad)
            except StudioError as ex:
                return RI.ocen_wyslanie(0, None, "", ex, True)

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
                    print("  %s: operacja %s jeszcze bez numeru zasobu (%s) — powtórz wgraj później"
                          % (klucz, op, stan.get("blad")))
                    continue
                e.update({"decal": str(stan["asset"]), "moderacja_decal": stan.get("moderacja") or "?"})
                zapisz(d)
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
            print("  %-20s obraz %-16s moderacja: %s" % (k, e["obraz"], e["moderacja"]))
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
    for klucz, nazwa, klasa, _w, _m, zestaw in IKONY:
        e = d.get("ikony", {}).get(klucz) or {}
        if e.get("obraz"):
            wiersze.append('\t%s = "rbxassetid://%s", -- %s (%s%s)'
                           % (klucz, e["obraz"], nazwa, klasa, ", zestaw" if zestaw else ""))
    tekst = ("--[[\n\tIkonyBroni — WYGENEROWANE przez swiat/postacie/ikony_broni.py luau z ikony_broni.json\n"
             "\t(nie edytować ręcznie). Ikony broni Maga i Zwiadowcy z puli Lv 1–10 (propozycja, nazwy nie są kanonem):\n"
             "\tklucz przedmiotu → obraz w Roblox (512 px, Higgsfield „Glossy Ink”, 27.11.2026). Sam rejestr — nigdzie\n"
             "\tniepodpięty; okno ekwipunku i sklep (pliki Pawła) wezmą go przy integracji.\n]]\n\nreturn {\n"
             + "\n".join(wiersze) + "\n}\n")
    os.makedirs(os.path.dirname(LUAU), exist_ok=True)
    with open(LUAU, "w", encoding="utf-8", newline="\n") as f:
        f.write(tekst)
    print("%s: %d obrazów" % (rel(LUAU), len(wiersze)))


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("stan").set_defaults(fn=cmd_stan)
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
