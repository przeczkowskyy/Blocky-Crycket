#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bronie Maga i Zwiadowcy (swiat/postacie/bronie_klas.py) → Roblox: zasoby Model z GLB i kontener
ReplicatedStorage/BronieKlas z gotowymi akcesoriami (Accessory: Handle + zaczep dłoni). Status: propozycja.

    python -B swiat/postacie/bronie_klas_roblox.py --sucho     # bez Studio: pliki, stan wgrań, plan
    python -B swiat/postacie/bronie_klas_roblox.py wgraj       # GLB → zasoby Model (Open Cloud przez Studio), prawo Use
    python -B swiat/postacie/bronie_klas_roblox.py wstaw       # insert_asset + akcesoria w ReplicatedStorage/BronieKlas
    python -B swiat/postacie/bronie_klas_roblox.py sprawdz     # tylko odczyt: co jest w kontenerze
    (--studio <studio_id>, gdy otwartych jest kilka okien Studio; --tylko id1,id2 — wybrane bronie)

Pliki: swiat/postacie/wynik/bronie_klas/przedmioty/<id>.glb (przebuduj.py bronie_klas) — folder wyników postaci
jest zatwierdzony w Studio do wgrywania; gdy Studio odrzuci plik, skrypt przerywa (nie szuka innego folderu).
Wgrywanie: konto osoby zalogowanej w Studio (MCP open_cloud_invoke), zgoda Karola z 14.11.2026 — modele i materiały
do gry B&C bez pytania, póki gra jest w testach; gra należy do innego konta, więc każdy zasób dostaje dla gry prawo
„Use”. Ochrona przed podwójnym wgraniem: stan w bronie_klas_zasoby.json zapisywany PRZED wysłaniem i zaraz po numerze
operacji; zasób już wgrany (albo wysyłka o nieznanym wyniku) nie jest wysyłany drugi raz. W pliku stanu nie ma
numeru konta.

Akcesorium w kontenerze (jedno na broń, nazwa = id modelu): Handle = MeshPart z importu (bez kolizji, Massless),
Attachment o nazwie zaczepu dłoni (RightGripAttachment, łuki LeftGripAttachment) w punkcie chwytu modelu
z Blendera — Humanoid:AddAccessory człowieka spawa broń od razu tak jak w bibliotece (ostrze do przodu przy
zwisającej ręce). Kot: korekta chwytu według rodzaju (zaczep kota, pos, rot) jest w wynik/bronie_klas/ekwipunek.json
(jak w puli wojownika) — spawanie do łapy kota to osobny krok z Pawłem. Atrybuty: Wygenerowane, Zrodlo, IdPrzedmiotu,
Nazwa, Klasa, Chwyt, Lapa, Zestaw, Ikona, ZasobModelu. Przedmiot zestawu: słabe PointLight „Poswiata”.
Orientację siatki po imporcie mierzy skrypt (EditableMesh: środek ciężkości wierzchołków względem skrzynki,
porównany z GLB), zamiast zakładać, jak importer obraca glTF.

Zasady (wspólne miejsce Team Create): każdy kod sprawdza game.PlaceId i tryb Edit; ruszany jest tylko własny kontener
(obiekt o tej nazwie bez atrybutu Wygenerowane → STOP); punkty historii przed i po; nic nie jest zapisywane ani
publikowane, Lighting nietknięty; nic nie trafia do Workspace, walki, sklepu ani kotów Pawła.
"""
import argparse
import hashlib
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
MIEJSCE = 129485428021967
KONTENER = "BronieKlas"
STAN = os.path.join(TU, "bronie_klas_zasoby.json")
WYNIK = os.path.join(TU, "wynik", "bronie_klas")
ZRODLO = ("swiat/postacie/bronie_klas.py (Karol 27.11.2026): bronie Maga i Zwiadowcy, pula Lv 1-10 — modele według "
          "ikon z Higgsfield, propozycja; integracja z ekwipunkiem osobno")
OPERACJA_MAX, MODERACJA_MAX = 180, 300

NAGLOWEK = ('if game.PlaceId ~= %d then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end\n'
            'if game:GetService("RunService"):IsRunning() then return "STOP: Studio jest w trybie Play — tylko Edit" end\n'
            % MIEJSCE)

KONTENER_KOD = r'''
local RS = game:GetService("ReplicatedStorage")
local k = RS:FindFirstChild("__K__")
if k and k:GetAttribute("Wygenerowane") ~= true then
	return "STOP: w ReplicatedStorage jest obiekt '__K__' bez atrybutu Wygenerowane — nie ruszam cudzej pracy"
end
game:GetService("ChangeHistoryService"):SetWaypoint("__K__: przed (__CO__)")
if not k then
	k = Instance.new("Folder")
	k.Name = "__K__"
	k.Parent = RS
end
k:SetAttribute("Wygenerowane", true)
k:SetAttribute("Zrodlo", "__ZRODLO__")
return "OK"
'''

PRZED_WSTAWIENIEM = r'''
local k = game:GetService("ReplicatedStorage"):FindFirstChild("__K__")
if not k or k:GetAttribute("Wygenerowane") ~= true then return "STOP: brak kontenera" end
local stary = k:FindFirstChild("__IMPORT__")
if stary then stary:Destroy() end -- pozostałość nieudanego ustawienia (tylko we własnym kontenerze)
return "OK"
'''

# pomiar siatki z importu (tylko odczyt): rozmiar, skrzynka i środek ciężkości unikalnych wierzchołków
POMIAR = r'''
local HS = game:GetService("HttpService")
local AS = game:GetService("AssetService")
local k = game:GetService("ReplicatedStorage"):FindFirstChild("__K__")
local imp = k and k:FindFirstChild("__IMPORT__")
if not imp then return HS:JSONEncode({ blad = "brak __IMPORT__ w __K__" }) end
local siatki = {}
for _, d in imp:GetDescendants() do
	if d:IsA("MeshPart") then table.insert(siatki, d) end
end
if #siatki ~= 1 then return HS:JSONEncode({ blad = "import ma " .. #siatki .. " siatek (oczekiwana 1)" }) end
local mp = siatki[1]
local w = { siatka = mp.Name, klasa = imp.ClassName, size = { mp.Size.X, mp.Size.Y, mp.Size.Z },
	meshsize = { mp.MeshSize.X, mp.MeshSize.Y, mp.MeshSize.Z },
	sa = mp:FindFirstChildWhichIsA("SurfaceAppearance") ~= nil, tekstura = mp.TextureID ~= "" }
local ok, em = pcall(function()
	return AS:CreateEditableMeshAsync(Content.fromUri(mp.MeshId))
end)
if not ok or not em then
	w.blad_mesh = tostring(em)
	return HS:JSONEncode(w)
end
local mn, mx = Vector3.new(math.huge, math.huge, math.huge), Vector3.new(-math.huge, -math.huge, -math.huge)
local suma, n, byly = Vector3.zero, 0, {}
for _, v in em:GetVertices() do
	local p = em:GetPosition(v)
	mn, mx = mn:Min(p), mx:Max(p)
	local klucz = string.format("%.3f,%.3f,%.3f", p.X, p.Y, p.Z)
	if not byly[klucz] then
		byly[klucz] = true
		suma += p
		n += 1
	end
end
pcall(function() em:Destroy() end)
local c = (mn + mx) / 2
local sr = suma / math.max(n, 1)
w.unikalnych = n
w.skrzynka = { mx.X - mn.X, mx.Y - mn.Y, mx.Z - mn.Z }
w.srodek = { c.X, c.Y, c.Z }
w.ciezkosc = { sr.X - c.X, sr.Y - c.Y, sr.Z - c.Z }
return HS:JSONEncode(w)
'''

# akcesorium z importu: Handle + zaczep dłoni (CFrame z Pythona), atrybuty, poświata zestawu; import usunięty
USTAW = r'''
local HS = game:GetService("HttpService")
local P = HS:JSONDecode(__JSON__)
local k = game:GetService("ReplicatedStorage"):FindFirstChild("__K__")
local imp = k and k:FindFirstChild(P.import)
if not imp then return "STOP: brak " .. P.import end
local mp = imp:FindFirstChildWhichIsA("MeshPart", true)
if not mp then return "STOP: import bez MeshPart" end
local stary = k:FindFirstChild(P.id)
if stary then stary:Destroy() end
local acc = Instance.new("Accessory")
acc.Name = P.id
for nazwa, wartosc in P.atrybuty do
	acc:SetAttribute(nazwa, wartosc)
end
mp.Name = "Handle"
mp.Anchored = false
mp.CanCollide = false
mp.CanTouch = false
mp.CanQuery = false
mp.Massless = true
if P.size then
	mp.Size = Vector3.new(P.size[1], P.size[2], P.size[3])
end
mp.CFrame = CFrame.new()
for _, d in mp:GetChildren() do
	if d:IsA("Attachment") or d:IsA("Weld") or d:IsA("WeldConstraint") or d:IsA("Motor6D") then d:Destroy() end
end
local att = Instance.new("Attachment")
att.Name = P.zaczep
att.CFrame = CFrame.new(P.pos[1], P.pos[2], P.pos[3]) * CFrame.fromOrientation(math.rad(P.rot[1]), math.rad(P.rot[2]), math.rad(P.rot[3]))
att.Parent = mp
if P.poswiata then
	local l = Instance.new("PointLight")
	l.Name = "Poswiata"
	l.Color = Color3.fromHex(P.poswiata)
	l.Brightness = 0.6
	l.Range = 5
	l.Shadows = false
	l.Parent = mp
end
mp.Parent = acc
acc.Parent = k
imp:Destroy()
local sa = mp:FindFirstChildWhichIsA("SurfaceAppearance")
return string.format("OK %s: Handle %.2f×%.2f×%.2f, %s, %s %s", acc.Name, mp.Size.X, mp.Size.Y, mp.Size.Z,
	sa and "SurfaceAppearance" or (mp.TextureID ~= "" and "TextureID" or "BEZ TEKSTURY"), att.Name,
	tostring(att.Position))
'''

SPRAWDZ = r'''
local HS = game:GetService("HttpService")
local k = game:GetService("ReplicatedStorage"):FindFirstChild("__K__")
if not k then return HS:JSONEncode({ kontener = false }) end
local w = { kontener = true, wygenerowane = k:GetAttribute("Wygenerowane") == true, zrodlo = k:GetAttribute("Zrodlo"),
	elementy = {} }
for _, c in k:GetChildren() do
	local h = c:FindFirstChild("Handle")
	local att = h and h:FindFirstChildWhichIsA("Attachment")
	local sa = h and h:FindFirstChildWhichIsA("SurfaceAppearance")
	table.insert(w.elementy, { n = c.Name, k = c.ClassName, handle = h and h.ClassName or nil,
		size = h and { h.Size.X, h.Size.Y, h.Size.Z } or nil, zaczep = att and att.Name or nil,
		pos = att and { att.Position.X, att.Position.Y, att.Position.Z } or nil,
		rot = att and { att.Orientation.X, att.Orientation.Y, att.Orientation.Z } or nil,
		sa = sa ~= nil, chwyt = c:GetAttribute("Chwyt"), ikona = c:GetAttribute("Ikona"),
		zasob = c:GetAttribute("ZasobModelu"), swiatlo = h and h:FindFirstChildWhichIsA("PointLight") ~= nil })
end
return HS:JSONEncode(w)
'''

KONIEC_KOD = r'''
game:GetService("ChangeHistoryService"):SetWaypoint("__K__: po (__CO__)")
local k = game:GetService("ReplicatedStorage"):FindFirstChild("__K__")
local opis = {}
for _, c in k and k:GetChildren() or {} do
	table.insert(opis, c.Name)
end
return "OK: " .. table.concat(opis, ", ")
'''


def kod(szablon, **zm):
    for k, v in dict(K=KONTENER, ZRODLO=ZRODLO, **zm).items():
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
    s = dict(s)
    s["opis"] = ("Zasoby Model broni Maga i Zwiadowcy (GLB z wynik/bronie_klas/przedmioty) wgrane do Roblox przez Studio. "
                 "Pisze swiat/postacie/bronie_klas_roblox.py — nie edytować ręcznie.")
    s["zgoda"] = "Karol 2026-11-14: modele i materiały do gry B&C bez pytania, póki gra jest w testach"
    tmp = STAN + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(s, ensure_ascii=False, indent=2) + "\n")
    os.replace(tmp, STAN)


def bronie(tylko=None):
    from swiat.postacie import bronie_klas as BK
    wynik = []
    for id_, nazwa, klasa, chwyt, klucz, zestaw in BK.BRONIE:
        if tylko and id_ not in tylko:
            continue
        wynik.append({"id": id_, "nazwa": nazwa, "klasa": klasa, "chwyt": chwyt, "klucz": klucz, "zestaw": zestaw,
                      "glb": os.path.join(WYNIK, "przedmioty", id_ + ".glb"),
                      "lapa": "lewa" if chwyt == "luk" else "prawa",
                      "zaczep": "LeftGripAttachment" if chwyt == "luk" else "RightGripAttachment"})
    return wynik


def glb_ciezkosc(sciezka):
    """(skrzynka min, max, środek ciężkości unikalnych wierzchołków względem środka skrzynki) z GLB."""
    import struct
    with open(sciezka, "rb") as f:
        b = f.read()
    n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + n])
    binz = b[20 + n + 8:]
    pkt = set()
    for m in j["meshes"]:
        for pr in m["primitives"]:
            acc = j["accessors"][pr["attributes"]["POSITION"]]
            bv = j["bufferViews"][acc["bufferView"]]
            off = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
            krok = bv.get("byteStride", 12)
            for i in range(acc["count"]):
                x, y, z = struct.unpack_from("<3f", binz, off + i * krok)
                pkt.add((round(x, 3), round(y, 3), round(z, 3)))
    mn = [min(p[i] for p in pkt) for i in range(3)]
    mx = [max(p[i] for p in pkt) for i in range(3)]
    c = [(mn[i] + mx[i]) / 2 for i in range(3)]
    sr = [sum(p[i] for p in pkt) / len(pkt) - c[i] for i in range(3)]
    return mn, mx, sr


# obroty, którymi importer mógł przenieść układ GLB do układu siatki w Roblox (wszystkie zachowują osie)
KANDYDACI = {"bez_obrotu": (1, 1, 1), "Y180": (-1, 1, -1), "X180": (1, -1, -1), "Z180": (-1, -1, 1)}


def ocen_obrot(oczek, zmierz, rozm_oczek=None, rozm_zmierz=None):
    """Błąd dopasowania środka ciężkości (względem skrzynki) dla każdego kandydata: {nazwa: błąd}. Pomiar
    przeliczony na skalę GLB (gdyby importer zmienił jednostki), oś po osi."""
    k = [1.0, 1.0, 1.0]
    if rozm_oczek and rozm_zmierz:
        k = [rozm_oczek[i] / rozm_zmierz[i] if rozm_zmierz[i] > 1e-4 else 1.0 for i in range(3)]
    zm = [zmierz[i] * k[i] for i in range(3)]
    return {n: sum((zm[i] - z[i] * oczek[i]) ** 2 for i in range(3)) ** 0.5 for n, z in KANDYDACI.items()}


def uchwyt(oczek_mn, oczek_mx, obrot):
    """Zaczep dłoni w układzie Handle: pozycja = punkt chwytu modelu (0, 0, 0 z Blendera) w układzie siatki
    (środek skrzynki = 0), obrót = M · Ry(180) (biblioteka: przód +Z, lewa +X; zaczep R15 obrócony o −90° w X)."""
    z = KANDYDACI[obrot]
    c = [(oczek_mn[i] + oczek_mx[i]) / 2 for i in range(3)]
    pos = [round(-c[i] * z[i], 4) + 0.0 for i in range(3)]
    rot = {"bez_obrotu": (0, 180, 0), "Y180": (0, 0, 0), "X180": (0, 0, 180), "Z180": (180, 0, 0)}[obrot]
    return pos, list(rot)


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Bronie Maga i Zwiadowcy → Roblox (ReplicatedStorage/BronieKlas)")
    ap.add_argument("co", nargs="?", default="plan", choices=["plan", "wgraj", "wstaw", "sprawdz"])
    ap.add_argument("--sucho", action="store_true", help="bez Studio: sprawdź pliki i pokaż plan")
    ap.add_argument("--studio", default=None)
    ap.add_argument("--tylko", default="", help="id broni po przecinku")
    a = ap.parse_args()
    tylko = set(x for x in a.tylko.split(",") if x)
    lista = bronie(tylko)
    st = stan()
    bledy = []
    print("Kontener: ReplicatedStorage/%s · placeId %d" % (KONTENER, MIEJSCE))
    for b in lista:
        z = st.get(b["id"]) or {}
        if not os.path.isfile(b["glb"]):
            bledy.append("brak " + os.path.relpath(b["glb"], REPO))
            continue
        zmieniony = z.get("sha256") and z["sha256"] != sha256(b["glb"])
        print("  %-26s %-8s %-19s zasób: %s%s" % (b["id"], b["chwyt"], b["zaczep"], z.get("asset") or
                                                 ("etap " + z["etap"] if z.get("etap") else "brak"),
                                                 "  (GLB zmienił się od wgrania)" if zmieniony else ""))
    if bledy:
        sys.exit("BŁĘDY: " + "; ".join(bledy) + " — najpierw: python -B swiat/postacie/przebuduj.py bronie_klas")
    if a.sucho or a.co == "plan":
        print("sucho: OK (Studio nieużywane)")
        return

    sys.path.insert(0, os.path.join(REPO, "tools"))
    sys.path.insert(0, TU)
    import roblox_import as RI
    from studio_mcp import StudioError, StudioMCP, first_studio_id

    with StudioMCP(timeout=300) as s:
        sid = a.studio or first_studio_id(s)
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
            kod_http, dane = RI.rozbierz_odpowiedz(r["text"] or "")
            return kod_http, dane, r["text"] or "", bool(r["is_error"])

        if a.co == "wgraj":
            wgraj(lista, st, luau, chmura, RI, StudioError)
        elif a.co == "wstaw":
            wstaw(lista, st, s, sid, luau)
        else:
            print(json.dumps(json.loads(luau(kod(SPRAWDZ))), ensure_ascii=False, indent=1))


def wgraj(lista, st, luau, chmura, RI, StudioError):
    uzytkownik = luau('return tostring(game:GetService("StudioService"):GetUserId())')
    universe = luau("return tostring(game.GameId)")
    if not uzytkownik.isdigit() or uzytkownik == "0":
        sys.exit("Studio nie podało konta zalogowanej osoby — nic nie wysłano.")
    for b in lista:
        z = st.get(b["id"]) or {}
        plik = b["glb"]
        if z.get("asset"):
            print("  %s: zasób %s już jest (%s) — nie wgrywam ponownie%s" % (
                b["id"], z["asset"], z.get("moderacja") or "?",
                "" if z.get("sha256") == sha256(plik) else " (UWAGA: GLB zmienił się od wgrania — nowy zasób tylko "
                                                           "świadomie, po usunięciu wpisu ze stanu)"))
            continue
        if z.get("etap") in ("wysylanie", "nieznane") and not z.get("operacja"):
            sys.exit("%s: poprzednia wysyłka ma nieznany wynik (%s). NIE wgrywam drugi raz — sprawdź Creator Hub "
                     "(Models „BC %s”) i wpisz numer do %s." % (b["id"], z.get("etap"), b["id"],
                                                                os.path.relpath(STAN, REPO)))
        if not z.get("operacja"):
            z = {"etap": "wysylanie", "plik": os.path.relpath(plik, REPO).replace(os.sep, "/"), "sha256": sha256(plik),
                 "czas": time.strftime("%Y-%m-%d %H:%M"), **({"nieudane": z["nieudane"]} if z.get("nieudane") else {})}
            st[b["id"]] = z
            zapisz_stan(st)                                   # BEZ tego zapisu nie wysyłamy
            try:
                kod_http, dane, tekst, blad = chmura("POST", "/assets/v1/assets", {"request": {
                    "assetType": "Model", "displayName": ("BC " + b["id"])[:50],
                    "description": "Blocky&Crycket: broń %s (%s), model z Blendera — swiat/postacie/bronie_klas"
                                   % (b["nazwa"], b["klasa"]),
                    "creationContext": {"creator": {"userId": uzytkownik}}}},
                    files=[{"name": "fileContent", "path": plik}], scopes=("asset:read", "asset:write"))
                etap, op, opis = RI.ocen_wyslanie(kod_http, dane, tekst, None, blad)
            except StudioError as e:
                etap, op, opis = RI.ocen_wyslanie(0, None, "", e, True)
                tekst = str(e)
            if etap == "nie_wyslano":
                del st[b["id"]]
                zapisz_stan(st)
                sys.exit("STUDIO ODRZUCIŁO PLIK (nic nie wysłano): folder %s nie jest zatwierdzony do wgrywania — "
                         "przerywam." % os.path.relpath(os.path.dirname(plik), REPO))
            if etap == "odrzucone_zadanie":
                del st[b["id"]]
                zapisz_stan(st)
                sys.exit("%s: Open Cloud odrzucił żądanie (%s), zasób nie powstał: %s" % (b["id"], opis, tekst[:300]))
            if etap != "operacja":
                z.update(etap="nieznane", odpowiedz=tekst[:600])
                zapisz_stan(st)
                sys.exit("%s: NIE WIADOMO, czy zasób powstał (%s) — NIE powtarzaj na ślepo, sprawdź Creator Hub."
                         % (b["id"], opis))
            z.update(etap="operacja", operacja=op)
            zapisz_stan(st)                                   # numer operacji zapisany, zanim zaczniemy czekać
        koniec = time.time() + OPERACJA_MAX
        wo = {"gotowe": False, "asset": ""}
        while time.time() < koniec:
            _k, dane, tekst, _b = chmura("GET", "/assets/v1/operations/%s" % z["operacja"])
            wo = RI.wynik_operacji(dane)
            if wo["gotowe"] or wo["blad"]:
                break
            time.sleep(4)
        if not wo.get("asset") and wo.get("gotowe") and wo.get("blad"):
            # operacja ZAKOŃCZONA błędem (done + error, bez odpowiedzi) — zasób nie powstał; zapis do historii,
            # następne „wgraj” wyśle plik jeszcze raz (to nie jest drugi zasób)
            z.setdefault("nieudane", []).append({"operacja": z.pop("operacja"), "blad": wo["blad"],
                                                 "czas": time.strftime("%Y-%m-%d %H:%M")})
            z["etap"] = "operacja_blad"
            zapisz_stan(st)
            print("  %s: operacja zakończona błędem %s — zasób nie powstał; ponów: wgraj" % (b["id"], wo["blad"]))
            continue
        if not wo.get("asset"):
            sys.exit("%s: operacja %s bez numeru zasobu (%s) — uruchom wgraj ponownie później (wznowi czekanie)"
                     % (b["id"], z["operacja"], wo.get("blad")))
        z.update(etap="zasob", asset=wo["asset"], moderacja=wo.get("moderacja") or "")
        zapisz_stan(st)
        print("  %s: zasób Model %s (moderacja: %s)" % (b["id"], wo["asset"], wo.get("moderacja") or "?"))
    # moderacja i prawo Use dla gry (także dla zasobów z wcześniejszych uruchomień)
    for b in lista:
        z = st.get(b["id"]) or {}
        if not z.get("asset"):
            continue
        koniec = time.time() + MODERACJA_MAX
        while RI.klasa_moderacji(z.get("moderacja")) in ("oczekuje", "nieznany") and time.time() < koniec:
            time.sleep(10)
            _k, dane, _t, _b = chmura("GET", "/assets/v1/assets/%s?readMask=moderationResult" % z["asset"])
            z["moderacja"] = RI.moderacja_z_zasobu(dane) or z.get("moderacja")
        zapisz_stan(st)
        print("  %-26s zasób %-16s moderacja: %s" % (b["id"], z["asset"], z.get("moderacja")))
    ids = [int(st[b["id"]]["asset"]) for b in lista if (st.get(b["id"]) or {}).get("asset")
           and not st[b["id"]].get("use")]
    if ids:
        _k, dane, tekst, _b = chmura("PATCH", "/asset-permissions-api/v1/assets/permissions", {
            "subjectType": "Universe", "subjectId": str(universe), "action": "Use",
            "requests": [{"assetId": i} for i in ids]}, scopes=("asset-permissions:write",))
        ok = [str(i) for i in (dane or {}).get("successAssetIds") or []]
        print("  prawo Use dla gry: %d z %d%s" % (len(ok), len(ids), "" if len(ok) == len(ids) else " — " + tekst[:300]))
        for b in lista:
            z = st.get(b["id"]) or {}
            if z.get("asset") in ok:
                z["use"] = True
        zapisz_stan(st)


def wstaw(lista, st, s, sid, luau):
    from swiat.postacie import bronie_klas as BK
    ikony = BK.ikony_roblox()
    print("kontener:", luau(kod(KONTENER_KOD, CO="wstawienie broni")))
    gotowe = [b for b in lista if (st.get(b["id"]) or {}).get("asset")]
    for b in lista:
        if b not in gotowe:
            print("  %s: brak zasobu (najpierw: wgraj) — pomijam" % b["id"])
    # 1. import każdego zasobu i pomiar siatki (tylko odczyt)
    pomiary = {}
    for b in gotowe:
        imp = b["id"] + "_import"
        luau(kod(PRZED_WSTAWIENIEM, IMPORT=imp))
        r = s.call("insert_asset", {"assetId": str(st[b["id"]]["asset"]), "assetName": imp, "assetType": "Model",
                                    "parentPath": "game.ReplicatedStorage.%s" % KONTENER, "studio_id": sid}, timeout=300)
        if r["is_error"]:
            sys.exit("%s: insert_asset nie wstawił zasobu %s: %s" % (b["id"], st[b["id"]]["asset"],
                                                                     (r["text"] or "")[:400]))
        w = json.loads(luau(kod(POMIAR, IMPORT=imp)))
        if w.get("blad"):
            sys.exit("%s: %s" % (b["id"], w["blad"]))
        mn, mx, sr = glb_ciezkosc(b["glb"])
        w["oczek_mn"], w["oczek_mx"], w["oczek_ciezkosc"] = mn, mx, sr
        w["bledy_obrotu"] = ocen_obrot(sr, w["ciezkosc"], [mx[i] - mn[i] for i in range(3)],
                                       w.get("skrzynka")) if "ciezkosc" in w else {}
        pomiary[b["id"]] = w
        print("  %-26s siatka %s; Size %s; GLB %s; ciężkość GLB %s / Roblox %s; %s" % (
            b["id"], w["siatka"], [round(v, 3) for v in w["size"]], [round(mx[i] - mn[i], 3) for i in range(3)],
            [round(v, 3) for v in sr], [round(v, 3) for v in w.get("ciezkosc", [])] or w.get("blad_mesh"),
            "SurfaceAppearance" if w["sa"] else ("TextureID" if w["tekstura"] else "BEZ TEKSTURY")))
    # 2. obrót importera: jeden dla wszystkich (importer działa tak samo) — z broni o wyraźnej asymetrii
    glosy = {}
    for bid, w in pomiary.items():
        bo = w.get("bledy_obrotu") or {}
        if not bo:
            continue
        kol = sorted(bo.items(), key=lambda kv: kv[1])
        if kol[1][1] - kol[0][1] > 0.02:                  # rozstrzyga tylko broń, w której kandydaci się różnią
            glosy[kol[0][0]] = glosy.get(kol[0][0], 0) + 1
    if not glosy:
        sys.exit("Nie da się ustalić obrotu importera (brak pomiaru EditableMesh albo wszystkie bronie symetryczne) "
                 "— akcesoriów nie składam; importy zostają w kontenerze do obejrzenia.")
    obrot = max(glosy.items(), key=lambda kv: kv[1])[0]
    print("obrót importera GLB → siatka Roblox: %s (głosy: %s)" % (obrot, glosy))
    if len(glosy) > 1:
        print("UWAGA: bronie nie zgadzają się co do obrotu — biorę większość, sprawdź w Studio")
    # 3. akcesoria
    for b in gotowe:
        w = pomiary[b["id"]]
        pos, rot = uchwyt(w["oczek_mn"], w["oczek_mx"], obrot)
        rozm = [w["oczek_mx"][i] - w["oczek_mn"][i] for i in range(3)]
        size = None
        if any(abs(w["size"][i] - rozm[i]) > 0.01 for i in range(3)):
            size = [round(v, 4) for v in rozm]               # 1 jednostka Blendera = 1 stud (biblioteka)
        ik = ikony.get(b["id"]) or {}
        P = {"import": b["id"] + "_import", "id": b["id"], "zaczep": b["zaczep"], "pos": pos, "rot": rot, "size": size,
             "poswiata": "7FD3FF" if b["zestaw"] else None,
             "atrybuty": {"Wygenerowane": True, "Zrodlo": "swiat/postacie/bronie_klas.py", "IdPrzedmiotu": b["id"],
                          "Nazwa": b["nazwa"], "Klasa": b["klasa"], "Chwyt": b["chwyt"], "Lapa": b["lapa"],
                          "Zestaw": bool(b["zestaw"]), "Ikona": ik.get("obraz", ""),
                          "ZasobModelu": str(st[b["id"]]["asset"]), "ObrotImportu": obrot}}
        print("  " + luau(kod(USTAW, JSON=json.dumps(json.dumps(P, ensure_ascii=False), ensure_ascii=False))))
        st[b["id"]]["kontener"] = "ReplicatedStorage/%s/%s" % (KONTENER, b["id"])
        st[b["id"]]["zaczep"] = {"nazwa": b["zaczep"], "pos": pos, "rot": rot}
    st["_import"] = {"obrot": obrot, "glosy": glosy, "sprawdzono": time.strftime("%Y-%m-%d %H:%M")}
    zapisz_stan(st)
    print("gotowe:", luau(kod(KONIEC_KOD, CO="wstawienie broni")))


if __name__ == "__main__":
    main()
