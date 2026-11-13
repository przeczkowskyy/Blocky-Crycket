#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Próba importu SIATKI postaci (FBX albo GLB z Blendera) do Roblox Studio przez Open Cloud.

UWAGA: z opcją --tak-wgraj skrypt WGRYWA ZASÓB NA KONTO ROBLOX osoby zalogowanej w Studio. Zasób jest trwały
(usuwa się go tylko w Creator Dashboard). Bez tej opcji skrypt tylko pokazuje plan i niczego nie wysyła.

    python -B swiat/postacie/roblox_import.py --modul rycerz                    # plan: co i dokąd by poszło
    python -B swiat/postacie/roblox_import.py --modul rycerz --tak-wgraj        # wgraj, wstaw, sprawdź, napraw, zrzuty
    python -B swiat/postacie/roblox_import.py --modul rycerz --format glb --tak-wgraj
    python -B swiat/postacie/roblox_import.py --modul rycerz --asset 1234567    # bez wgrywania: wstaw istniejący zasób
    python -B swiat/postacie/roblox_import.py --modul rycerz --sprawdz "Nazwa modelu"   # sama kontrola modelu z kontenera

Wymagania po stronie Studio (Assistant → Settings → MCP Permissions):
  1. zakresy „Publish & manage assets” (asset:read, asset:write),
  2. folder `swiat/postacie/wynik` na liście approved upload directories — zatwierdza człowiek; skrypt tego nie obchodzi.
Co robi po wgraniu: czeka na operację i moderację, wstawia model do `Workspace/TestPostaci`, liczy siatki, kości,
stawy i zaczepy, sprawdza tekstury i kolory, mierzy wzrost w studach i poprawia skalę, kotwiczy części, stawia model
obok postaci z klocków i robi dwa zrzuty. Wynik zapisuje do `wynik/_roblox/import_<moduł>_<format>.json`.
Stan: napisany 13.11.2026 PRZED pierwszym udanym wgraniem — części „wstaw / sprawdź / napraw” są sprawdzone tylko na
modelu z klocków. Pierwszy prawdziwy import trzeba obejrzeć krok po kroku.
"""
import argparse
import json
import os
import re
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for sciezka in (REPO, os.path.join(REPO, "tools")):
    if sciezka not in sys.path:
        sys.path.insert(0, sciezka)

KONTENER = "TestPostaci"
PLACE_ID = 129485428021967
LIMIT_MB = 20
# gdzie stoi wersja z klocków (układ miasta) — import staje 6,5 studa po jej lewej ręce
from swiat.postacie.roblox_postac import ROZMIESZCZENIE, PRZESUNIECIE  # noqa: E402

KTO = r'''
return game:GetService("HttpService"):JSONEncode({
	placeId = game.PlaceId, creatorType = tostring(game.CreatorType), creatorId = game.CreatorId,
	userId = game:GetService("StudioService"):GetUserId(),
	kontener = workspace:FindFirstChild("__KONTENER__") ~= nil,
})
'''

KONTROLA = r'''
local HS = game:GetService("HttpService")
local kont = workspace:FindFirstChild("__KONTENER__")
local model = kont and kont:FindFirstChild(__MODEL__)
if not model then
	return HS:JSONEncode({ blad = "brak modelu w kontenerze" })
end
local w = { nazwa = model.Name, klasa = model.ClassName, klasy = {}, siatki = {}, zaczepy = {}, kosci = {} }
local minV, maxV = Vector3.new(math.huge, math.huge, math.huge), Vector3.new(-math.huge, -math.huge, -math.huge)
local czesci = {}
local function dodaj(d)
	w.klasy[d.ClassName] = (w.klasy[d.ClassName] or 0) + 1
	if d:IsA("BasePart") then
		czesci[d.Name] = d
		local h = d.Size / 2
		for _, zn in { Vector3.new(1, 1, 1), Vector3.new(-1, 1, 1), Vector3.new(1, -1, 1), Vector3.new(1, 1, -1),
			Vector3.new(-1, -1, 1), Vector3.new(-1, 1, -1), Vector3.new(1, -1, -1), Vector3.new(-1, -1, -1) } do
			local p = d.CFrame:PointToWorldSpace(h * zn)
			minV, maxV = minV:Min(p), maxV:Max(p)
		end
	end
	if d:IsA("MeshPart") and #w.siatki < 60 then
		local sa = d:FindFirstChildWhichIsA("SurfaceAppearance")
		table.insert(w.siatki, { n = d.Name, rozmiar = { d.Size.X, d.Size.Y, d.Size.Z }, tekstura = d.TextureID,
			colormap = sa and sa.ColorMap or "", kolor = d.Color:ToHex(), zakotwiczona = d.Anchored, mesh = d.MeshId })
	elseif d:IsA("Attachment") and #w.zaczepy < 60 then
		table.insert(w.zaczepy, d.Name .. "@" .. (d.Parent and d.Parent.Name or "?"))
	elseif d:IsA("Bone") and #w.kosci < 60 then
		table.insert(w.kosci, d.Name)
	end
end
if model:IsA("BasePart") then
	dodaj(model)
end
for _, d in model:GetDescendants() do
	dodaj(d)
end
if maxV.X >= minV.X then
	w.skrzynka_min = { minV.X, minV.Y, minV.Z }
	w.skrzynka_max = { maxV.X, maxV.Y, maxV.Z }
	w.wymiary = { maxV.X - minV.X, maxV.Y - minV.Y, maxV.Z - minV.Z }
end
-- kierunek przodu w świecie: stopa wystaje przed łydkę; lewa ręka ma być po lewej stronie przodu
local stopa, lydka = czesci.LeftFoot or czesci.LeftFoot_Geo, czesci.LeftLowerLeg or czesci.LeftLowerLeg_Geo
if stopa and lydka then
	local d = stopa.Position - lydka.Position
	local plasko = Vector3.new(d.X, 0, d.Z)
	if plasko.Magnitude > 0.02 then
		w.przod = { plasko.Unit.X, plasko.Unit.Z }
		local lewa, prawa = czesci.LeftUpperArm or czesci.LeftUpperArm_Geo, czesci.RightUpperArm or czesci.RightUpperArm_Geo
		if lewa and prawa then
			local wLewo = lewa.Position - prawa.Position
			-- dla przodu f lewa strona to (f.Z, −f.X) w płaszczyźnie XZ (Roblox: prawa = przód × góra)
			w.lewa_po_lewej = (wLewo.X * plasko.Unit.Z - wLewo.Z * plasko.Unit.X) > 0
		end
	end
end
if model:IsA("Model") then
	w.skala = model:GetScale()
	w.primary = model.PrimaryPart and model.PrimaryPart.Name or ""
end
return HS:JSONEncode(w)
'''

NAPRAWA = r'''
local HS = game:GetService("HttpService")
local CH = game:GetService("ChangeHistoryService")
local kont = workspace:FindFirstChild("__KONTENER__")
local model = kont and kont:FindFirstChild(__MODEL__)
if not model or not model:IsA("Model") then
	return HS:JSONEncode({ blad = "brak modelu (albo to nie Model)" })
end
local P = __PARAMETRY__
local w = { kroki = {} }
CH:SetWaypoint("Postacie: przed naprawą importu " .. model.Name)
local function skrzynka()
	local minV, maxV = Vector3.new(math.huge, math.huge, math.huge), Vector3.new(-math.huge, -math.huge, -math.huge)
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") then
			local h = d.Size / 2
			for _, zn in { Vector3.new(1, 1, 1), Vector3.new(-1, 1, 1), Vector3.new(1, -1, 1), Vector3.new(1, 1, -1),
				Vector3.new(-1, -1, 1), Vector3.new(-1, 1, -1), Vector3.new(1, -1, -1), Vector3.new(-1, -1, -1) } do
				local p = d.CFrame:PointToWorldSpace(h * zn)
				minV, maxV = minV:Min(p), maxV:Max(p)
			end
		end
	end
	return minV, maxV
end
-- 1) kotwiczenie: wszystkie części (figura do oglądania; rig do animacji wymaga potem odkotwiczenia poza korzeniem)
local n = 0
for _, d in model:GetDescendants() do
	if d:IsA("BasePart") and not d.Anchored then
		d.Anchored = true
		n += 1
	end
end
table.insert(w.kroki, "zakotwiczono części: " .. n)
-- 2) skala do oczekiwanego wzrostu
local minV, maxV = skrzynka()
local wzrost = maxV.Y - minV.Y
if wzrost > 0 and P.wzrost > 0 then
	local czynnik = P.wzrost / wzrost
	if math.abs(czynnik - 1) > 0.02 then
		model:ScaleTo(model:GetScale() * czynnik)
		table.insert(w.kroki, string.format("skala ×%.4f (wzrost %.2f → %.2f studa)", czynnik, wzrost, P.wzrost))
	else
		table.insert(w.kroki, string.format("skala bez zmian (wzrost %.2f studa)", wzrost))
	end
end
-- 3) obrót wokół pionu, żeby przód patrzył tam, gdzie wersja z klocków (jeśli da się wyznaczyć przód)
if P.przod_teraz and P.przod_cel then
	local a = math.atan2(P.przod_teraz[1], P.przod_teraz[2])
	local b = math.atan2(P.przod_cel[1], P.przod_cel[2])
	local kat = b - a
	if math.abs(kat) > 0.02 then
		model:PivotTo(CFrame.new(model:GetPivot().Position) * CFrame.Angles(0, kat, 0) * CFrame.new(-model:GetPivot().Position) * model:GetPivot())
		table.insert(w.kroki, string.format("obrót wokół pionu o %.1f°", math.deg(kat)))
	end
end
-- 4) miejsce: środek skrzynki nad punktem docelowym, spód na podłożu
minV, maxV = skrzynka()
local params = RaycastParams.new()
params.FilterType = Enum.RaycastFilterType.Exclude
params.FilterDescendantsInstances = { kont }
local traf = workspace:Raycast(Vector3.new(P.cel[1], 200, P.cel[2]), Vector3.new(0, -400, 0), params)
local y = traf and traf.Position.Y or 0
local srodek = (minV + maxV) / 2
local przesun = Vector3.new(P.cel[1] - srodek.X, y - minV.Y, P.cel[2] - srodek.Z)
model:PivotTo(model:GetPivot() + przesun)
table.insert(w.kroki, string.format("postawiono w (%.1f; %.2f; %.1f)", P.cel[1], y, P.cel[2]))
model:SetAttribute("Wygenerowane", true)
model:SetAttribute("ImportSiatki", P.zrodlo)
CH:SetWaypoint("Postacie: naprawa importu " .. model.Name)
return HS:JSONEncode(w)
'''


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Próba importu siatki postaci do Roblox Studio (Open Cloud)")
    ap.add_argument("--modul", required=True, help="np. rycerz (plik wynik/<moduł>/<moduł>.<format>)")
    ap.add_argument("--format", default="fbx", choices=["fbx", "glb"])
    ap.add_argument("--tak-wgraj", action="store_true", help="NAPRAWDĘ wgraj plik na konto Roblox zalogowane w Studio")
    ap.add_argument("--asset", default="", help="pomiń wgrywanie: wstaw istniejący zasób o tym numerze")
    ap.add_argument("--sprawdz", default="", help="sama kontrola modelu o tej nazwie w kontenerze (bez wgrywania i wstawiania)")
    ap.add_argument("--bez-naprawy", action="store_true")
    ap.add_argument("--wyj", default=os.path.join(TU, "wynik", "_roblox"))
    a = ap.parse_args()

    from studio_mcp import StudioMCP, StudioError, first_studio_id

    plik = os.path.join(TU, "wynik", a.modul, "%s.%s" % (a.modul, a.format))
    raport = os.path.join(TU, "wynik", a.modul, "raport.json")
    oczek = {}
    if os.path.isfile(raport):
        with open(raport, encoding="utf-8") as f:
            m = next((x for x in json.load(f)["modele"] if x.get("rodzaj") == "postac"), None)
        if m:
            oczek = {"nazwa": m["nazwa"], "wymiary": m["wymiary_ciala"], "siatek_ciala": len(m["siatki"]),
                     "kosci": len(m["kosci"]), "znacznikow_att": len(m.get("znaczniki_att", [])), "trojkaty": m["trojkaty_razem"]}
    nazwa = "%s (import %s)" % (oczek.get("nazwa", a.modul), a.format.upper())
    print("plik:        %s" % os.path.relpath(plik, REPO).replace("\\", "/"))
    print("oczekiwane:  %s" % json.dumps(oczek, ensure_ascii=False))
    if not a.sprawdz and not a.asset:
        if not os.path.isfile(plik):
            sys.exit("Nie ma pliku — najpierw `python -B swiat/postacie/przebuduj.py %s` (eksporty są poza gitem)." % a.modul)
        mb = os.path.getsize(plik) / 1e6
        print("rozmiar:     %.2f MB (limit %d MB)" % (mb, LIMIT_MB))
        if mb > LIMIT_MB:
            sys.exit("Plik za duży na jedno wgranie.")
    roz = ROZMIESZCZENIE.get(a.modul)
    os.makedirs(a.wyj, exist_ok=True)

    try:
        with StudioMCP() as s:
            sid = first_studio_id(s)
            if not sid:
                sys.exit("Roblox Studio nie jest podłączone.")

            def luau(kod):
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
                if r["is_error"]:
                    raise StudioError(r["text"])
                return json.loads(r["text"])

            def chmura(metoda, endpoint, body=None, files=None, scopes=("asset:read",)):
                arg = {"method": metoda, "endpoint": endpoint, "scopes": list(scopes), "studio_id": sid}
                if body is not None:
                    arg["body"] = json.dumps(body)
                if files:
                    arg["files"] = files
                r = s.call("open_cloud_invoke", arg, timeout=300)
                tekst = r["text"] or ""
                m = re.search(r"->\s*(\d{3})", tekst)
                kod = int(m.group(1)) if m else 0
                tresc = tekst.split("\n\n", 1)[1] if "\n\n" in tekst else ""
                try:
                    dane = json.loads(tresc)
                except ValueError:
                    dane = {}
                return kod, dane, tekst

            def kontrola(model):
                return luau(KONTROLA.replace("__KONTENER__", KONTENER).replace("__MODEL__", json.dumps(model, ensure_ascii=False)))

            kto = luau(KTO.replace("__KONTENER__", KONTENER))
            if kto["placeId"] != PLACE_ID:
                sys.exit("To nie jest miejsce gry (PlaceId %s)." % kto["placeId"])
            print("konto:       zasób trafi na konto użytkownika zalogowanego w Studio (userId %s); właściciel gry: %s %s"
                  % (kto["userId"], kto["creatorType"].replace("Enum.CreatorType.", ""), kto["creatorId"]))
            if not kto["kontener"]:
                sys.exit("Nie ma kontenera Workspace/%s — najpierw `python -B swiat/postacie/roblox_postac.py`." % KONTENER)

            wynik = {"modul": a.modul, "format": a.format, "oczekiwane": oczek, "nazwa": nazwa}
            model = a.sprawdz
            if not model:
                asset = a.asset
                if not asset:
                    if not a.tak_wgraj:
                        print("PLAN: wgranie „%s” jako zasób Model, wstawienie do Workspace/%s, kontrola, naprawa, zrzuty." % (nazwa, KONTENER))
                        print("Nic nie wysłano. Żeby naprawdę wgrać, dodaj --tak-wgraj.")
                        return
                    kod, dane, tekst = chmura("POST", "/assets/v1/assets", {"request": {
                        "assetType": "Model", "displayName": nazwa[:50], "description": "Test importu siatki z Blendera.",
                        "creationContext": {"creator": {"userId": str(kto["userId"])}}}},
                        files=[{"name": "fileContent", "path": plik}], scopes=("asset:read", "asset:write"))
                    if "approved" in tekst and "director" in tekst:
                        print("STUDIO ODRZUCIŁO PLIK: folder nie jest zatwierdzony do wgrywania.")
                        print("Do kliknięcia przez człowieka: Assistant → Settings → MCP Permissions → approved upload directories →")
                        print("  " + os.path.dirname(os.path.dirname(plik)))
                        sys.exit(3)
                    if kod not in (200, 201) or not dane.get("operationId") and not dane.get("path"):
                        sys.exit("Wgranie nie powiodło się: %s" % tekst[:400])
                    op = dane.get("operationId") or dane["path"].split("/")[-1]
                    print("wgrano, operacja %s — czekam na wynik…" % op)
                    koniec = time.time() + 240
                    while time.time() < koniec:
                        kod, dane, tekst = chmura("GET", "/assets/v1/operations/%s" % op)
                        if dane.get("done"):
                            break
                        time.sleep(4)
                    if not dane.get("done"):
                        sys.exit("Operacja %s nie skończyła się w 4 minuty — NIE wgrywaj ponownie, sprawdź ją później." % op)
                    odp = dane.get("response") or {}
                    asset = str(odp.get("assetId") or "")
                    stan = (odp.get("moderationResult") or {}).get("moderationState", "?")
                    print("zasób %s, moderacja: %s" % (asset, stan))
                    wynik.update(asset=asset, moderacja=stan)
                    if not asset or stan == "Rejected":
                        sys.exit("Brak zasobu do wstawienia (moderacja: %s). Nie wgrywaj tego samego pliku drugi raz." % stan)
                r = s.call("insert_asset", {"assetId": asset, "assetName": nazwa, "assetType": "Model",
                                            "parentPath": "game.Workspace.%s" % KONTENER, "studio_id": sid}, timeout=300)
                print("wstawianie:", (r["text"] or "")[:300].replace("\n", " "))
                if r["is_error"]:
                    sys.exit("Nie udało się wstawić zasobu %s." % asset)
                wynik["wstawianie"] = (r["text"] or "")[:1500]
                model = nazwa
            k = kontrola(model)
            if k.get("blad"):
                sys.exit("Kontrola: %s („%s”)" % (k["blad"], model))
            wynik["kontrola_przed"] = k
            kl = k.get("klasy", {})
            print("klasy:       %s" % ", ".join("%s %d" % (n, kl[n]) for n in sorted(kl)))
            print("wymiary:     %s (oczekiwane %s)" % ([round(v, 2) for v in k.get("wymiary", [])], oczek.get("wymiary")))
            bez_koloru = [x["n"] for x in k.get("siatki", []) if not x["tekstura"] and not x["colormap"]]
            print("siatki:      %d MeshPart, bez tekstury i bez ColorMap: %d" % (kl.get("MeshPart", 0), len(bez_koloru)))
            print("kości/stawy: Bone %d, Motor6D %d, Attachment %d; przód (świat): %s; lewa ręka po lewej: %s"
                  % (kl.get("Bone", 0), kl.get("Motor6D", 0), kl.get("Attachment", 0), k.get("przod"), k.get("lewa_po_lewej")))
            if not a.bez_naprawy and not a.sprawdz and roz and oczek:
                import math
                px, pz = roz["poz"][0] + PRZESUNIECIE[0], roz["poz"][1] + PRZESUNIECIE[1]
                fx, fz = roz["patrz"][0] - roz["poz"][0], roz["patrz"][1] - roz["poz"][1]
                dl = math.hypot(fx, fz)
                fx, fz = fx / dl, fz / dl
                lewo = (fz, -fx)                                   # lewa ręka postaci patrzącej w (fx, fz)
                cel = [px + lewo[0] * 6.5, pz + lewo[1] * 6.5]
                par = {"wzrost": oczek["wymiary"][1], "cel": cel, "zrodlo": "%s.%s" % (a.modul, a.format)}
                if k.get("przod"):
                    par["przod_teraz"], par["przod_cel"] = k["przod"], [fx, fz]
                from swiat.postacie.roblox_postac import luau as literal
                n = luau(NAPRAWA.replace("__KONTENER__", KONTENER).replace("__MODEL__", json.dumps(model, ensure_ascii=False))
                         .replace("__PARAMETRY__", literal(par)))
                for krok in n.get("kroki", [n.get("blad", "?")]):
                    print("naprawa:     %s" % krok)
                wynik["naprawa"] = n
                wynik["kontrola_po"] = kontrola(model)
                for i, (odl, bok) in enumerate(((11.0, 0.35), (9.0, -0.6))):
                    sx, sz = (px + cel[0]) / 2, (pz + cel[1]) / 2
                    kx, kz = fx * math.cos(bok) - fz * math.sin(bok), fx * math.sin(bok) + fz * math.cos(bok)
                    r = s.call("screen_capture", {"studio_id": sid, "capture_id": "import_%s_%d" % (a.modul, i),
                                                  "camera_position": [sx + kx * odl, 5.5, sz + kz * odl],
                                                  "look_at_position": [sx, 3.0, sz]}, timeout=120)
                    if not r["is_error"] and r["images"]:
                        png = os.path.join(a.wyj, "import_%s_%s_%d.png" % (a.modul, a.format, i))
                        with open(png, "wb") as f:
                            f.write(r["images"][0])
                        print("zrzut:       %s (po lewej ręce postaci z klocków stoi import)" % png)
            sciezka = os.path.join(a.wyj, "import_%s_%s.json" % (a.modul, a.format))
            with open(sciezka, "w", encoding="utf-8", newline="\n") as f:
                json.dump(wynik, f, ensure_ascii=False, indent=1)
            print("zapisano:    %s" % sciezka)
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
