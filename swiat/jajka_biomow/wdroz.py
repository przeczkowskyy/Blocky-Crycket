#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wdrożenie jajek biomów (Bagno, Dżungla) do Roblox Studio — kontener Workspace/JajkaBiomowPodglad.
Pakiet swiat/jajka_biomow (Karol 25.11.2026), status: propozycja (PROJEKT.md). Modele buduje zbuduj.py (Blender),
skrypty ustawiające generuje studio_skrypty.py; ten plik tylko wysyła rzeczy do Studio.

    python -B swiat/jajka_biomow/wdroz.py --sucho     # bez Studio: pliki, stan wgrań, plan
    python -B swiat/jajka_biomow/wdroz.py skrypty     # kontener + Moduly/JajkaBiomowDane + JajkaBiomowSpoczynek (Client)
    python -B swiat/jajka_biomow/wdroz.py wgraj       # modele GLB -> zasoby Model (Open Cloud przez Studio), prawo Use
    python -B swiat/jajka_biomow/wdroz.py wstaw       # insert_asset do kontenera + studio/jajko_<biom>_ustaw.luau
    python -B swiat/jajka_biomow/wdroz.py wszystko    # wgraj + wstaw + skrypty
    (--studio <studio_id>, gdy otwartych jest kilka okien Studio)

Animacja spoczynku jak w innych pakietach próby Karola (swiat/pety_proba/zbuduj.py): Script z RunContext = Client
i ModuleScript z danymi we WŁASNYM kontenerze w Workspace — bez src/ (pliki Pawła i mapowanie Rojo). Skrypt klienta
zaczyna się od strażnika Studio (poza Studio nic nie robi).

Wgrywanie: konto osoby zalogowanej w Studio (narzędzie MCP open_cloud_invoke, bez klucza w .env). Zgoda: Karol
14.11.2026 — modele i materiały do gry B&C bez pytania, póki gra jest w testach. Gra należy do innego konta, więc każdy
zasób dostaje dla gry (universe) prawo „Use”. Studio przyjmuje pliki tylko z folderów zatwierdzonych przez człowieka
(Assistant → Settings → MCP Permissions → approved upload directories); gdy folder modele/ nie jest zatwierdzony, skrypt
NIE kopiuje plików gdzie indziej (narzędzie tego zabrania) — wypisuje, co kliknąć, i kończy z kodem 3.
Ochrona przed podwójnym wgraniem: stan w studio/zasoby.json zapisywany PRZED wysłaniem; zasób już wgrany (albo
wysyłka o nieznanym wyniku) nie jest wysyłany drugi raz — wznowienie czeka na operację albo staje z prośbą
o sprawdzenie Creator Dashboard.
Maski blasku (JajkoBagnaBlask, JajkoDzungliBlask) wgrane 25.11 przez Studio MCP upload_image — ID w studio_skrypty.py
(BLASK_ID) i w assets/manifest.json.

Zasady (wspólne miejsce Team Create): każdy kod sprawdza game.PlaceId i tryb Edit; ruszany jest tylko własny kontener
(obiekt o tej nazwie bez atrybutu Wygenerowane → STOP); punkty historii przed i po; nic nie jest zapisywane ani
publikowane, Lighting nietknięty; starych jajek z klocków ani jajka Pawła skrypt nie dotyka.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
MIEJSCE = 129485428021967   # placeId gry (to samo co swiat/test_walki_roblox/cel_studio.py)
UNIVERSE = 10776202722      # universe gry — dostaje prawo Use do wgranych zasobów
KONTENER = "JajkaBiomowPodglad"
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
STAN = os.path.join(TU, "studio", "zasoby.json")
BIOMY = {
    "bagno": {"nazwa": "Jajko Bagna", "import": "JajkoBagnaImport", "glb": "modele/jajko_bagno.glb",
              "manifest": "JajkoBagnaModel", "ustaw": "studio/jajko_bagno_ustaw.luau"},
    "dzungla": {"nazwa": "Jajko Dżungli", "import": "JajkoDzungliImport", "glb": "modele/jajko_dzungla.glb",
                "manifest": "JajkoDzungliModel", "ustaw": "studio/jajko_dzungla_ustaw.luau"},
}
SKRYPTY = [  # plik w studio/, klasa, ścieżka w kontenerze, RunContext
    ("JajkaBiomowDane.luau", "ModuleScript", "Moduly/JajkaBiomowDane", None),
    ("JajkaBiomowSpoczynek.client.luau", "Script", "JajkaBiomowSpoczynek", "Client"),
]
OPERACJA_MAX, MODERACJA_MAX = 180, 300

NAGLOWEK = ('if game.PlaceId ~= %d then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end\n'
            'if game:GetService("RunService"):IsRunning() then return "STOP: Studio jest w trybie Play — tylko Edit" end\n'
            % MIEJSCE)

KONTENER_KOD = r'''
local k = workspace:FindFirstChild("__K__")
if k and k:GetAttribute("Wygenerowane") ~= true then
	return "STOP: w Workspace jest obiekt '__K__' bez atrybutu Wygenerowane — nie ruszam cudzej pracy"
end
game:GetService("ChangeHistoryService"):SetWaypoint("__K__: przed (__CO__)")
if not k then
	k = Instance.new("Folder")
	k.Name = "__K__"
	k:SetAttribute("Wygenerowane", true)
	k:SetAttribute("Zrodlo", "swiat/jajka_biomow (Karol 25.11): jajka Bagna i Dżungli do oceny, propozycja")
	k.Parent = workspace
end
if not k:FindFirstChild("Moduly") then
	local f = Instance.new("Folder")
	f.Name = "Moduly"
	f.Parent = k
end
return "OK"
'''

SKRYPT_KOD = r'''
local k = workspace:FindFirstChild("__K__")
if not k or k:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera"
end
local sciezka = string.split("__SCIEZKA__", "/")
local rodzic = k
for i = 1, #sciezka - 1 do
	rodzic = rodzic:FindFirstChild(sciezka[i])
	if not rodzic then return "STOP: brak folderu " .. sciezka[i] end
end
local stary = rodzic:FindFirstChild(sciezka[#sciezka])
if stary then stary:Destroy() end
local s = Instance.new("__KLASA__")
s.Name = sciezka[#sciezka]
__RUNCONTEXT__
s.Source = __ZRODLO__
s.Parent = rodzic
return "OK " .. s:GetFullName() .. " (" .. #s.Source .. " znaków)"
'''

PRZED_WSTAWIENIEM = r'''
local k = workspace:FindFirstChild("__K__")
if not k or k:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera"
end
local stary = k:FindFirstChild("__IMPORT__")
if stary then
	stary:Destroy() -- pozostałość nieudanego ustawienia (tylko we własnym kontenerze)
end
return "OK"
'''

PO_WSTAWIENIU = r'''
local k = workspace:FindFirstChild("__K__")
local imp = k and k:FindFirstChild("__IMPORT__")
if not imp then return "STOP: insert_asset nie wstawił __IMPORT__ do __K__" end
local n, tekstury = 0, 0
for _, d in ipairs(imp:GetDescendants()) do
	if d:IsA("MeshPart") then
		n += 1
		if d.TextureID ~= "" or d:FindFirstChildWhichIsA("SurfaceAppearance") then tekstury += 1 end
	end
end
return string.format("OK %s: %d siatek, z teksturą %d", imp.ClassName, n, tekstury)
'''

KONIEC_KOD = r'''
game:GetService("ChangeHistoryService"):SetWaypoint("__K__: po (__CO__)")
local k = workspace:FindFirstChild("__K__")
local opis = {}
for _, c in ipairs(k and k:GetChildren() or {}) do
	table.insert(opis, c.Name)
end
return "OK: " .. table.concat(opis, ", ")
'''


def wczytaj(sciezka):
    with open(os.path.join(TU, *sciezka.split("/")), encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def dlugi_napis(tekst):
    poziom = 3
    while ("]" + "=" * poziom + "]") in tekst or ("[" + "=" * poziom + "[") in tekst:
        poziom += 1
    return "[" + "=" * poziom + "[\n" + tekst + "]" + "=" * poziom + "]"


def kod(szablon, **zm):
    for k, v in dict(K=KONTENER, **zm).items():
        szablon = szablon.replace("__%s__" % k, v)
    return szablon


def sha256(sciezka):
    h = hashlib.sha256()
    with open(sciezka, "rb") as f:
        for kawalek in iter(lambda: f.read(1 << 20), b""):
            h.update(kawalek)
    return h.hexdigest()


def stan():
    if os.path.isfile(STAN):
        with open(STAN, encoding="utf-8") as f:
            return json.load(f)
    return {}


def zapisz_stan(s):
    tmp = STAN + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(s, ensure_ascii=False, indent=2) + "\n")
    os.replace(tmp, STAN)


def manifest(*args):
    r = subprocess.run([sys.executable, "-B", os.path.join(REPO, "tools", "manifest.py")] + list(args),
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print("  manifest.py %s: %s" % (args[:2], (r.stderr or r.stdout)[-300:]))


def rozbierz(tekst):
    """Odpowiedź open_cloud_invoke „METODA url -> 200 OK\\n\\n{json}” -> (kod HTTP, dane JSON albo None)."""
    m = re.search(r"->\s*(\d{3})", tekst or "")
    i = (tekst or "").find("{")
    dane = None
    if i >= 0:
        try:
            dane = json.loads(tekst[i:])
        except ValueError:
            dane = None
    return (int(m.group(1)) if m else 0), dane


def folder_niezatwierdzony(tekst):
    t = (tekst or "").lower()
    return "approved for uploads" in t or "approved upload" in t


def sprawdz_offline():
    bledy = []
    for plik, _klasa, _sc, _ctx in SKRYPTY:
        tekst = wczytaj("studio/" + plik)
        if plik.endswith(".client.luau") and STRAZNIK not in tekst:
            bledy.append("%s bez strażnika Studio" % plik)
        if len(tekst) > 199000:
            bledy.append("%s za długi" % plik)
    for b, d in BIOMY.items():
        if not os.path.isfile(os.path.join(TU, d["glb"])):
            bledy.append("brak " + d["glb"])
        u = wczytaj(d["ustaw"])
        if 'local BLASK = "rbxassetid://0"' in u:
            bledy.append("%s: maska blasku bez ID (studio_skrypty.py BLASK_ID)" % d["ustaw"])
    return bledy


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Wdrożenie jajek biomów do Roblox Studio")
    ap.add_argument("co", nargs="?", default="plan", choices=["plan", "skrypty", "wgraj", "wstaw", "wszystko"])
    ap.add_argument("--sucho", action="store_true", help="bez Studio: sprawdź pliki i pokaż plan")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()

    bledy = sprawdz_offline()
    st = stan()
    print("Kontener: Workspace/%s · placeId %d · universe %d" % (KONTENER, MIEJSCE, UNIVERSE))
    for b, d in BIOMY.items():
        z = st.get(b) or {}
        print("  %-8s %s → %s/%s → „%s”; zasób: %s" % (b, d["glb"], KONTENER, d["import"], d["nazwa"],
                                                    z.get("asset") or ("etap " + z["etap"] if z.get("etap") else "brak")))
    for plik, klasa, sc, ctx in SKRYPTY:
        print("  %-26s → %s%s (studio/%s)" % (sc, klasa, " [RunContext=%s]" % ctx if ctx else "", plik))
    if bledy:
        sys.exit("BŁĘDY: " + "; ".join(bledy))
    if a.sucho or a.co == "plan":
        print("sucho: OK (Studio nieużywane)")
        return

    for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
        if _s not in sys.path:
            sys.path.insert(0, _s)
    from cel_studio import MIEJSCE as MIEJSCE_GRY, wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    if MIEJSCE_GRY != MIEJSCE:
        sys.exit("BŁĄD: placeId w cel_studio.py (%s) ≠ %s" % (MIEJSCE_GRY, MIEJSCE))

    with StudioMCP(timeout=300) as s:
        s.studios(wait=15)
        sid = wybierz_studio(s, a.studio)
        if "Current Studio Mode: Edit" not in s.call("get_studio_state", {"studio_id": sid})["text"]:
            sys.exit("Studio nie jest w trybie Edit — zatrzymaj Play i spróbuj ponownie.")

        def luau(k):
            r = s.call("execute_luau", {"code": NAGLOWEK + k, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
            if r["is_error"]:
                raise StudioError(r["text"][:2000])
            w = (r["text"] or "").strip().strip('"')
            if w.startswith("STOP"):
                sys.exit(w)
            return w

        def chmura(metoda, endpoint, body=None, files=None, scopes=("asset:read",)):
            arg = {"method": metoda, "endpoint": endpoint, "scopes": list(scopes), "studio_id": sid}
            if body is not None:
                arg["body"] = json.dumps(body)
            if files:
                arg["files"] = files
            r = s.call("open_cloud_invoke", arg, timeout=300)
            kod_http, dane = rozbierz(r["text"] or "")
            return kod_http, dane, r["text"] or "", bool(r["is_error"])

        if a.co in ("wgraj", "wszystko"):
            wgraj(chmura, luau, st, StudioError)
        if a.co in ("wstaw", "wszystko"):
            wstaw(s, sid, luau, stan())
        if a.co in ("skrypty", "wszystko"):
            print("kontener:", luau(kod(KONTENER_KOD, CO="skrypty")))
            for plik, klasa, sc, ctx in SKRYPTY:
                k = kod(SKRYPT_KOD, SCIEZKA=sc, KLASA=klasa,
                        RUNCONTEXT="s.RunContext = Enum.RunContext.%s" % ctx if ctx else "")
                print("  skrypt:", luau(k.replace("__ZRODLO__", dlugi_napis(wczytaj("studio/" + plik)))))
            print("gotowe:", luau(kod(KONIEC_KOD, CO="skrypty")))


def wgraj(chmura, luau, st, StudioError):
    uzytkownik = luau('return tostring(game:GetService("StudioService"):GetUserId())')
    if not uzytkownik.isdigit() or uzytkownik == "0":
        sys.exit("Studio nie podało konta zalogowanej osoby — nic nie wysłano.")
    nowe = []
    for b, d in BIOMY.items():
        z = st.get(b) or {}
        plik = os.path.join(TU, *d["glb"].split("/"))
        if z.get("asset"):
            print("  %s: zasób %s już jest (%s) — nie wgrywam ponownie" % (b, z["asset"], z.get("moderacja") or "?"))
            if z.get("sha256") != sha256(plik):
                print("    UWAGA: plik %s zmienił się od wgrania (nowy zasób tylko świadomie: usuń wpis z %s)"
                      % (d["glb"], os.path.relpath(STAN, REPO)))
            continue
        if z.get("etap") == "wysylanie" or (z.get("etap") and not z.get("operacja")):
            sys.exit("%s: poprzednia wysyłka ma nieznany wynik (%s). NIE wgrywam drugi raz — sprawdź Creator Dashboard "
                     "(Development Items → Models „%s”) i wpisz numer do %s." % (b, z.get("etap"), d["manifest"], STAN))
        if not z.get("operacja"):
            z = {"etap": "wysylanie", "plik": d["glb"], "sha256": sha256(plik), "czas": time.strftime("%Y-%m-%dT%H:%M:%S")}
            st[b] = z
            zapisz_stan(st)                                   # BEZ tego zapisu nie wysyłamy
            try:
                kod_http, dane, tekst, blad = chmura("POST", "/assets/v1/assets", {"request": {
                    "assetType": "Model", "displayName": d["manifest"], "description":
                    "Blocky&Crycket: %s (swiat/jajka_biomow)" % d["nazwa"],
                    "creationContext": {"creator": {"userId": uzytkownik}}}},
                    files=[{"name": "fileContent", "path": plik}], scopes=("asset:read", "asset:write"))
            except StudioError as e:
                kod_http, dane, tekst, blad = 0, None, str(e), True
            if blad and folder_niezatwierdzony(tekst):
                del st[b]
                if st:
                    zapisz_stan(st)
                elif os.path.isfile(STAN):
                    os.remove(STAN)
                print("STUDIO ODRZUCIŁO PLIK (nic nie wysłano): folder nie jest zatwierdzony do wgrywania.")
                print("Do kliknięcia przez człowieka: Studio → Assistant → Settings → MCP Permissions → approved upload "
                      "directories → dodać folder swiat/jajka_biomow/modele z tego repo; potem: wdroz.py wgraj")
                sys.exit(3)
            op = ((dane or {}).get("path") or "").split("/")[-1] or (dane or {}).get("operationId") or ""
            if not op:
                z.update(etap="nieznane", odpowiedz=tekst[:1500])
                zapisz_stan(st)
                sys.exit("%s: brak numeru operacji (HTTP %s) — NIE powtarzaj na ślepo, sprawdź Creator Dashboard: %s"
                         % (b, kod_http, tekst[:300]))
            z.update(etap="operacja", operacja=op)
            zapisz_stan(st)
            # plik wysłany: wpis w manifeście (approve = sha256 dokładnie wysłanego pliku; zgoda Karola 14.11.2026)
            manifest("upsert", d["manifest"], "category=model", "status=processed", "processed=swiat/jajka_biomow/" + d["glb"],
                     "usage=Model jajka biomu (%s) do Workspace/%s — swiat/jajka_biomow" % (d["nazwa"], KONTENER))
            manifest("approve", d["manifest"])
        koniec = time.time() + OPERACJA_MAX
        wynik = {}
        while time.time() < koniec:
            _k, dane, tekst, _b = chmura("GET", "/assets/v1/operations/%s" % z["operacja"])
            if (dane or {}).get("done"):
                wynik = (dane or {}).get("response") or {}
                break
            time.sleep(4)
        asset = str(wynik.get("assetId") or "")
        if not asset:
            sys.exit("%s: operacja %s bez numeru zasobu po %d s — uruchom wgraj ponownie później (wznowi czekanie)"
                     % (b, z["operacja"], OPERACJA_MAX))
        moderacja = ((wynik.get("moderationResult") or {}).get("moderationState") or "")
        z.update(etap="zasob", asset=asset, moderacja=moderacja)
        zapisz_stan(st)
        nowe.append(b)
        print("  %s: zasób Model %s (moderacja: %s)" % (b, asset, moderacja or "?"))
    # moderacja i prawo Use dla gry (także dla zasobów z wcześniejszych uruchomień)
    for b, z in st.items():
        if not z.get("asset"):
            continue
        koniec = time.time() + MODERACJA_MAX
        while "approved" not in (z.get("moderacja") or "").lower() and time.time() < koniec:
            if "reject" in (z.get("moderacja") or "").lower():
                sys.exit("%s: zasób %s ODRZUCONY przez moderację — nie wgrywaj tego samego pliku drugi raz" % (b, z["asset"]))
            time.sleep(15)
            _k, dane, _t, _b = chmura("GET", "/assets/v1/assets/%s" % z["asset"])
            z["moderacja"] = ((dane or {}).get("moderationResult") or {}).get("moderationState") or z.get("moderacja")
        zapisz_stan(st)
        print("  %s: moderacja %s" % (b, z.get("moderacja")))
    ids = [int(z["asset"]) for z in st.values() if z.get("asset")]
    if ids:
        _k, dane, tekst, _b = chmura("PATCH", "/asset-permissions-api/v1/assets/permissions", {
            "subjectType": "Universe", "subjectId": str(UNIVERSE), "action": "Use",
            "requests": [{"assetId": i} for i in ids]}, scopes=("asset-permissions:write",))
        ok = [str(i) for i in (dane or {}).get("successAssetIds") or []]
        print("  prawo Use dla gry: %d z %d%s" % (len(ok), len(ids), "" if len(ok) == len(ids) else " — " + tekst[:300]))
        for b, z in st.items():
            if z.get("asset"):
                z["use"] = z["asset"] in ok or z.get("use", False)
        zapisz_stan(st)
    for b in nowe:
        z, d = st[b], BIOMY[b]
        manifest("upsert", d["manifest"], "status=in_roblox", "moderation=%s" % (z.get("moderacja") or "?"),
                 "roblox_target=Workspace/%s/%s" % (KONTENER, d["nazwa"]),
                 "notes=zasób Model %s (wgrany przez Studio MCP open_cloud_invoke, prawo Use dla gry: %s); ustawienie: "
                 "swiat/jajka_biomow/%s" % (z["asset"], "tak" if z.get("use") else "NIE", d["ustaw"]))


def wstaw(s, sid, luau, st):
    print("kontener:", luau(kod(KONTENER_KOD, CO="wstawienie jajek")))
    for b, d in BIOMY.items():
        z = st.get(b) or {}
        if not z.get("asset"):
            print("  %s: brak zasobu (najpierw: wdroz.py wgraj) — pomijam" % b)
            continue
        luau(kod(PRZED_WSTAWIENIEM, IMPORT=d["import"]))
        r = s.call("insert_asset", {"assetId": str(z["asset"]), "assetName": d["import"], "assetType": "Model",
                                    "parentPath": "game.Workspace.%s" % KONTENER, "studio_id": sid}, timeout=300)
        if r["is_error"]:
            sys.exit("%s: insert_asset nie wstawił zasobu %s: %s" % (b, z["asset"], (r["text"] or "")[:400]))
        print("  %s: wstawiono —" % b, luau(kod(PO_WSTAWIENIU, IMPORT=d["import"])))
        print("  %s: ustawienie —" % b, luau(wczytaj(d["ustaw"])))
    print("gotowe:", luau(kod(KONIEC_KOD, CO="wstawienie jajek")))


if __name__ == "__main__":
    main()
