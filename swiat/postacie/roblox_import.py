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

Ochrona przed podwójnym wgraniem: PRZED wysłaniem skrypt zapisuje `wynik/_roblox/wgranie_<moduł>_<format>.json`
(etap „wysylanie”) i uzupełnia go numerem operacji, numerem zasobu i stanem moderacji, gdy tylko są znane. Kolejne
uruchomienie z --tak-wgraj NIE wgrywa drugi raz, tylko wznawia od tego, co wiadomo (czeka na operację albo od razu
wstawia zasób); gdy stan jest nieznany, zatrzymuje się i każe sprawdzić Creator Dashboard. Świadome drugie wgranie
(kolejny trwały zasób) wymaga osobnej opcji --nowy-zasob-mimo-poprzedniego.
Każdy import trafia do kontenera pod nazwą, której tam jeszcze nie było (starszych importów skrypt nie rusza);
kontrola i naprawa działają dokładnie na tym nowym modelu.

Stan: napisany 13.11.2026 PRZED pierwszym udanym wgraniem — części „wstaw / sprawdź / napraw” są sprawdzone tylko na
modelu z klocków. Pierwszy prawdziwy import trzeba obejrzeć krok po kroku.
Logika bez Studio (odpowiedzi Open Cloud, moderacja, plik stanu, nazwy, wybór nowego modelu) ma sprawdzian:
    python -B swiat/postacie/biblioteka/test_roblox_import.py
"""
import argparse
import hashlib
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
WYNIK = os.path.join(TU, "wynik")
# plik stanu wgrania leży zawsze tutaj (niezależnie od --wyj), żeby inna ścieżka wyników nie obeszła ochrony
STAN_DIR = os.path.join(WYNIK, "_roblox")
OPERACJA_MAX, OPERACJA_CO = 240, 4             # s: ile czekać na operację wgrania i co ile pytać
MODERACJA_MAX, MODERACJA_CO = 300, 15          # s: ile czekać na moderację zasobu i co ile pytać
NOWY_MIMO = "--nowy-zasob-mimo-poprzedniego"
# ROZMIESZCZENIE / PRZESUNIECIE / literał Luau z roblox_postac są importowane w main(), żeby sam import tego pliku
# (np. w sprawdzianie) nie ciągnął reszty narzędzi

KTO = r'''
return game:GetService("HttpService"):JSONEncode({
	placeId = game.PlaceId, creatorType = tostring(game.CreatorType), creatorId = game.CreatorId,
	userId = game:GetService("StudioService"):GetUserId(),
	kontener = workspace:FindFirstChild("__KONTENER__") ~= nil,
})
'''

# spis dzieci kontenera i Workspace (nazwa, klasa, DebugId jeśli dostępny) — przed i po wstawieniu
SPIS = r'''
-- roblox_import: SPIS
local HS = game:GetService("HttpService")
local function spis(rodzic)
	local w = {}
	if not rodzic then
		return w
	end
	for _, c in rodzic:GetChildren() do
		local ok, id = pcall(function()
			return c:GetDebugId()
		end)
		table.insert(w, { n = c.Name, k = c.ClassName, id = (ok and type(id) == "string") and id or nil })
	end
	return w
end
return HS:JSONEncode({ kontener = spis(workspace:FindFirstChild("__KONTENER__")), workspace = spis(workspace) })
'''

# nowy model: znajdź dokładnie tę instancję, w razie potrzeby przenieś do kontenera i nadaj wybraną nazwę
PRZENIES = r'''
-- roblox_import: PRZENIES
local HS = game:GetService("HttpService")
local CH = game:GetService("ChangeHistoryService")
local P = HS:JSONDecode(__JSON__)
local kont = workspace:FindFirstChild("__KONTENER__")
if not kont then
	return HS:JSONEncode({ blad = "brak kontenera" })
end
local rodzic = (P.rodzic == "kontener") and kont or workspace
local trafione = {}
for _, c in rodzic:GetChildren() do
	if c.Name == P.n and c.ClassName == P.k then
		if P.id == "" then
			table.insert(trafione, c)
		else
			local ok, id = pcall(function()
				return c:GetDebugId()
			end)
			if ok and id == P.id then
				table.insert(trafione, c)
			end
		end
	end
end
if #trafione ~= 1 then
	return HS:JSONEncode({ blad = string.format("pasujących instancji „%s” (%s): %d zamiast 1", P.n, P.k, #trafione) })
end
local m = trafione[1]
local w = { kroki = {} }
if m.Parent ~= kont or m.Name ~= P.cel then
	CH:SetWaypoint("Postacie: przed przeniesieniem importu " .. P.cel)
	if m.Parent ~= kont then
		m.Parent = kont
		table.insert(w.kroki, "przeniesiono z Workspace do Workspace/" .. kont.Name)
	end
	if m.Name ~= P.cel then
		table.insert(w.kroki, string.format("zmieniono nazwę „%s” → „%s”", m.Name, P.cel))
		m.Name = P.cel
	end
	CH:SetWaypoint("Postacie: przeniesiono import " .. P.cel)
end
local ile = 0
for _, c in kont:GetChildren() do
	if c.Name == P.cel then
		ile += 1
	end
end
if ile ~= 1 then
	return HS:JSONEncode({ blad = string.format("w kontenerze jest %d instancji o nazwie „%s”", ile, P.cel) })
end
w.nazwa, w.klasa, w.sciezka = m.Name, m.ClassName, m:GetFullName()
return HS:JSONEncode(w)
'''

KONTROLA = r'''
-- roblox_import: KONTROLA
local HS = game:GetService("HttpService")
local kont = workspace:FindFirstChild("__KONTENER__")
local model, ile = nil, 0
if kont then
	for _, c in kont:GetChildren() do
		if c.Name == __MODEL__ then
			model, ile = c, ile + 1
		end
	end
end
if ile > 1 then
	return HS:JSONEncode({ blad = string.format("w kontenerze jest %d instancji o tej nazwie — nie wiem, którą sprawdzić", ile) })
end
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
-- roblox_import: NAPRAWA
local HS = game:GetService("HttpService")
local CH = game:GetService("ChangeHistoryService")
local kont = workspace:FindFirstChild("__KONTENER__")
local model, ile = nil, 0
if kont then
	for _, c in kont:GetChildren() do
		if c.Name == __MODEL__ then
			model, ile = c, ile + 1
		end
	end
end
if ile > 1 then
	return HS:JSONEncode({ blad = string.format("w kontenerze jest %d instancji o tej nazwie — nie wiem, którą naprawić", ile) })
end
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


# ---------------------------------------------------------------- logika bez Studio (sprawdzian: test_roblox_import.py)

_NAGLOWEK = re.compile(r"^\s*[A-Z]{3,7}\s+\S+.*?->\s*(\d{3})\b", re.M)
_ID_OPERACJI = re.compile(r"^[A-Za-z0-9_.-]{1,200}$")
_ID_ZASOBU = re.compile(r"^\d{1,20}$")


def rozbierz_odpowiedz(tekst):
    """Tekst z open_cloud_invoke („METHOD url -> 200 OK\\n\\n{json}”) -> (kod HTTP albo 0, słownik albo None).

    Kod bierze się tylko z linii w tym formacie przed pierwszą pustą linią, treść — spod niej. None oznacza, że
    treści nie da się odczytać jako obiekt JSON (co NIE znaczy, że żądanie się nie udało)."""
    tekst = tekst or ""
    czesci = re.split(r"\r?\n\r?\n", tekst, maxsplit=1)
    m = _NAGLOWEK.search(czesci[0])
    kod = int(m.group(1)) if m else 0
    dane = None
    if len(czesci) == 2:
        try:
            dane = json.loads(czesci[1])
        except ValueError:
            dane = None
    if not isinstance(dane, dict):
        dane = None
    return kod, dane


def id_operacji(dane):
    """operationId z odpowiedzi na POST (albo ostatni człon „path”: operations/<id>); "" gdy brak/podejrzany."""
    if not isinstance(dane, dict):
        return ""
    op = str(dane.get("operationId") or "")
    if not op and isinstance(dane.get("path"), str) and dane["path"].startswith("operations/"):
        op = dane["path"].split("/")[-1]
    return op if _ID_OPERACJI.match(op) else ""


def moderacja_z_zasobu(zasob):
    """moderationResult.moderationState z obiektu zasobu (Open Cloud Assets v1) albo ""."""
    if not isinstance(zasob, dict):
        return ""
    mr = zasob.get("moderationResult")
    return str(mr.get("moderationState") or "") if isinstance(mr, dict) else ""


def id_zasobu(zasob):
    """assetId z obiektu zasobu (albo z „path”: assets/<id>); "" gdy brak albo nie są to same cyfry."""
    if not isinstance(zasob, dict):
        return ""
    asset = str(zasob.get("assetId") or "")
    if not asset and isinstance(zasob.get("path"), str) and zasob["path"].startswith("assets/"):
        asset = zasob["path"].split("/")[-1]
    return asset if _ID_ZASOBU.match(asset) else ""


def wynik_operacji(dane):
    """Odpowiedź GET /assets/v1/operations/<id> -> {gotowe, asset, moderacja, blad}."""
    if not isinstance(dane, dict):
        return {"gotowe": False, "asset": "", "moderacja": "", "blad": None}
    odp = dane.get("response") if isinstance(dane.get("response"), dict) else {}
    return {"gotowe": bool(dane.get("done")), "asset": id_zasobu(odp), "moderacja": moderacja_z_zasobu(odp),
            "blad": dane.get("error")}


def klasa_moderacji(stan):
    """Stan moderacji ('Approved', 'MODERATION_STATE_REVIEWING'…) -> zatwierdzony / odrzucony / oczekuje / nieznany.

    Spacje, podkreślenia i łączniki są pomijane, więc „Not Approved”, „NOT_APPROVED” i „not-approved” to to samo."""
    s = re.sub(r"[\s_-]+", "", str(stan or "").lower())
    if any(x in s for x in ("reject", "unapprov", "disapprov", "notapprov", "denied", "declin")):
        return "odrzucony"
    # oczekiwanie sprawdzamy PRZED „approv”: „PendingApproval” albo „AWAITING_APPROVAL” to jeszcze nie zgoda
    if any(x in s for x in ("review", "pend", "await", "queue", "progress", "process")):
        return "oczekuje"
    if "approv" in s:
        return "zatwierdzony"
    return "nieznany"


def _folder_niezatwierdzony(tekst):
    t = str(tekst or "").lower()
    return "approved" in t and "director" in t


def ocen_wyslanie(kod, dane, tekst, wyjatek=None, blad=False):
    """Co wiadomo po POST /assets/v1/assets -> (etap, operacja, opis).

    etap: „operacja” (jest numer operacji — czyli plik na pewno dotarł, nawet gdy kodu HTTP nie da się odczytać),
    „nie_wyslano” (Studio odmówiło przed wysłaniem — folder niezatwierdzony; rozpoznawane TYLKO przy błędzie bez kodu
    HTTP, wyjątku MCP albo 4xx, nigdy przy 2xx), „odrzucone_zadanie” (Open Cloud odpowiedział 4xx — zasób nie powstał),
    „nieznane” (wywołanie przerwane, odpowiedź nieczytelna, 5xx albo 2xx bez numeru operacji — NIE WIADOMO, czy zasób
    powstał). blad: znacznik is_error z wyniku narzędzia."""
    if wyjatek is not None:
        if _folder_niezatwierdzony(wyjatek):
            return "nie_wyslano", "", "folder nie jest zatwierdzony do wgrywania (błąd MCP: %s)" % wyjatek
        return "nieznane", "", "wywołanie przerwane: %s" % wyjatek
    tekst = tekst or ""
    op = id_operacji(dane)
    if op:
        return "operacja", op, "" if kod in (200, 201) else "numer operacji jest, kod HTTP %s" % (kod or "nieczytelny")
    if ((not kod and blad) or 400 <= kod < 500) and _folder_niezatwierdzony(tekst):
        return "nie_wyslano", "", "folder nie jest zatwierdzony do wgrywania"
    if 400 <= kod < 500:
        return "odrzucone_zadanie", "", "Open Cloud odpowiedział HTTP %d" % kod
    if not kod:
        return "nieznane", "", "nie da się odczytać kodu HTTP z odpowiedzi"
    if dane is None:
        return "nieznane", "", "HTTP %d, ale treści odpowiedzi nie da się odczytać" % kod
    return "nieznane", "", "HTTP %d bez numeru operacji" % kod


# etapy, po których wiadomo na pewno, że żaden zasób nie powstał — można wgrać bez dodatkowej opcji
ETAPY_BEZ_ZASOBU = ("nie_wyslano", "odrzucone_zadanie")


def decyzja_wgrania(stan, nowy_mimo=False):
    """Co zrobić z --tak-wgraj przy zapisanym stanie poprzedniego wgrania -> (akcja, komunikat).

    akcja: „wgraj” (wolno wysłać plik), „wznow_operacje” (czekać na zapisaną operację), „wznow_zasob” (zasób jest —
    od razu moderacja i wstawienie), „stop” (nie wgrywać; komunikat mówi dlaczego i co sprawdzić)."""
    if not stan:
        return "wgraj", ""
    etap = stan.get("etap", "?")
    asset = str(stan.get("asset") or "")
    op = str(stan.get("operacja") or "")
    if nowy_mimo:
        if etap in ETAPY_BEZ_ZASOBU:
            return "wgraj", ""
        return "wgraj", ("UWAGA: %s — wgranie mimo poprzedniego (etap „%s”%s%s) utworzy KOLEJNY trwały zasób na koncie."
                         % (NOWY_MIMO, etap, ", zasób %s" % asset if asset else "",
                            ", operacja %s" % op if op else ""))
    if etap in ETAPY_BEZ_ZASOBU and not asset and not op:
        return "wgraj", "Poprzednia próba nie wysłała pliku albo Open Cloud ją odrzucił (%s) — wolno spróbować ponownie." % etap
    if asset:
        if klasa_moderacji(stan.get("moderacja")) == "odrzucony":
            return "stop", ("Zasób %s został ODRZUCONY przez moderację (%s). Nie wgrywaj tego samego pliku drugi raz; "
                            "popraw plik i świadomie użyj %s." % (asset, stan.get("moderacja"), NOWY_MIMO))
        return "wznow_zasob", "Zasób %s jest już wgrany — wznawiam od niego, nic nie wgrywam." % asset
    if op:
        if etap == "operacja_blad":
            return "stop", ("Operacja %s zakończyła się błędem (%s). Sprawdź w Creator Dashboard, czy zasób nie powstał; "
                            "dopiero potem ewentualnie %s." % (op, json.dumps(stan.get("blad"), ensure_ascii=False)[:200],
                                                                NOWY_MIMO))
        return "wznow_operacje", "Plik był już wysłany (operacja %s) — czekam na tę operację, nic nie wgrywam." % op
    return "stop", ("Poprzednie wgranie ma stan NIEZNANY (etap „%s”): nie wiadomo, czy zasób powstał. NIE wgrywaj na "
                    "ślepo. Sprawdź Creator Dashboard (Development Items → Models, zasób „%s”). Jeśli jest — wstaw go "
                    "przez --asset <numer>; jeśli na pewno go nie ma — %s."
                    % (etap, stan.get("nazwa_zasobu", "?"), NOWY_MIMO))


def sciezka_stanu(modul, fmt, katalog=None):
    return os.path.join(katalog or STAN_DIR, "wgranie_%s_%s.json" % (modul, fmt))


def wczytaj_stan(sciezka):
    """Stan poprzedniego wgrania albo None; uszkodzony plik -> etap „uszkodzony” (czyli stop, nie „brak stanu”)."""
    if not os.path.exists(sciezka):
        return None
    try:
        with open(sciezka, encoding="utf-8") as f:
            stan = json.load(f)
    except (OSError, ValueError) as e:
        return {"etap": "uszkodzony", "blad": "nie da się odczytać %s: %s" % (sciezka, e)}
    return stan if isinstance(stan, dict) else {"etap": "uszkodzony", "blad": "to nie jest obiekt JSON"}


def zapisz_stan(sciezka, stan, proby=5):
    """Zapis przez plik tymczasowy i podmianę (OneDrive potrafi chwilę trzymać plik — kilka prób)."""
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    tmp = sciezka + ".tmp"
    for i in range(proby):
        try:
            with open(tmp, "w", encoding="utf-8", newline="\n") as f:
                json.dump(stan, f, ensure_ascii=False, indent=1)
            os.replace(tmp, sciezka)
            return
        except OSError:
            if i == proby - 1:
                try:
                    os.remove(tmp)
                except OSError:
                    pass
                raise
            time.sleep(0.5)


def wybierz_nazwe(bazowa, istniejace):
    """Nazwa dla nowego importu, której nie ma wśród `istniejace` (starszych importów nie ruszamy)."""
    zajete = set(istniejace)
    if bazowa not in zajete:
        return bazowa
    i = 2
    while "%s #%d" % (bazowa, i) in zajete:
        i += 1
    return "%s #%d" % (bazowa, i)


def _nowe(przed, po):
    """Wpisy z `po`, których nie było w `przed`. Z DebugId — dokładnie; bez — po (nazwa, klasa), a wpis, którego
    klucz istniał już wcześniej, dostaje znacznik „niejednoznaczny” (nie wiadomo, który z takich samych jest nowy)."""
    if przed is not None and all(e.get("id") for e in list(przed) + list(po)):
        stare = {e["id"] for e in przed}
        return [dict(e) for e in po if e["id"] not in stare]
    ile = {}
    for e in przed or []:
        ile[(e.get("n"), e.get("k"))] = ile.get((e.get("n"), e.get("k")), 0) + 1
    grupy = {}
    for e in po:
        grupy.setdefault((e.get("n"), e.get("k")), []).append(e)
    wynik = []
    for klucz, lista in grupy.items():
        bylo = ile.get(klucz, 0)
        for _ in range(len(lista) - bylo):
            wynik.append({"n": klucz[0], "k": klucz[1], "id": "", "niejednoznaczny": bylo > 0})
    return wynik


def wybierz_nowa(przed, po, nazwy, tekst=""):
    """Który obiekt wstawił insert_asset -> (wybór, błąd). Dokładnie jedno z nich jest None.

    przed/po: {"kontener": [{n, k, id?}], "workspace": [...]} ze spisu SPIS. nazwy: nazwy, pod którymi model mógł
    się pojawić (wybrana nazwa, displayName). Kandydaci: każde nowe dziecko kontenera i każde nowe dziecko Workspace
    o jednej z `nazwy` (cudzych nowych rzeczy w Workspace nie bierzemy). Przy kilku kandydatach zawęża po `nazwy`,
    potem po nazwie wymienionej w odpowiedzi insert_asset. Jedyny kandydat o nazwie spoza `nazwy` (np. narzędzie
    nazwało model inaczej) jest przyjmowany tylko wtedy, gdy w Workspace nie pojawiło się nic innego nowego — inaczej
    może to być cudza rzecz z Team Create (sama wzmianka w odpowiedzi insert_asset tu nie wystarcza, bo nazwy w rodzaju
    „Model” trafiają się w każdym tekście). Wybór: {rodzic, n, k, id}."""
    nazwy = {x for x in nazwy if x}
    nowe_k = _nowe(przed.get("kontener"), po.get("kontener") or [])
    nowe_w = [e for e in _nowe(przed.get("workspace"), po.get("workspace") or []) if e["n"] != KONTENER]
    kandydaci = [dict(e, rodzic="kontener") for e in nowe_k]
    kandydaci += [dict(e, rodzic="workspace") for e in nowe_w if e["n"] in nazwy]
    if not kandydaci:
        inne = ", ".join("„%s” (%s)" % (e["n"], e["k"]) for e in nowe_w) or "brak"
        return None, ("Po wstawieniu nie widać nowego obiektu w Workspace/%s ani w Workspace pod nazwą %s "
                      "(nowe w Workspace: %s)." % (KONTENER, " / ".join("„%s”" % x for x in sorted(nazwy)), inne))
    if len(kandydaci) > 1:
        po_nazwie = [e for e in kandydaci if e["n"] in nazwy]
        if len(po_nazwie) == 1:
            kandydaci = po_nazwie
    if len(kandydaci) > 1 and tekst:
        w_tekscie = [e for e in kandydaci if e["n"] and e["n"] in tekst]
        if len(w_tekscie) == 1:
            kandydaci = w_tekscie
    if len(kandydaci) > 1:
        return None, ("Więcej niż jeden kandydat na nowy model: %s — nie zgaduję, który to import."
                      % ", ".join("„%s” (%s, %s)" % (e["n"], e["k"], e["rodzic"]) for e in kandydaci))
    e = kandydaci[0]
    inne_w = [x for x in nowe_w if x["n"] not in nazwy]
    if e["n"] not in nazwy and inne_w:
        return None, ("Nowy obiekt „%s” (%s, %s) ma nieoczekiwaną nazwę, a w Workspace pojawiło się też: %s — nie wiem, "
                      "który z nich to import, a cudzych rzeczy nie ruszam."
                      % (e["n"], e["k"], e["rodzic"], ", ".join("„%s” (%s)" % (x["n"], x["k"]) for x in inne_w)))
    if e.get("niejednoznaczny"):
        return None, ("Nowy obiekt „%s” (%s) ma taką samą nazwę i klasę jak starszy, a Studio nie podało DebugId — "
                      "nie wiem, który jest nowy." % (e["n"], e["k"]))
    return {"rodzic": e["rodzic"], "n": e["n"], "k": e["k"], "id": e.get("id") or ""}, None


def sha256_pliku(sciezka):
    h = hashlib.sha256()
    with open(sciezka, "rb") as f:
        for kawalek in iter(lambda: f.read(1 << 20), b""):
            h.update(kawalek)
    return h.hexdigest()


def teraz():
    return time.strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------- przebieg ze Studio


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Próba importu siatki postaci do Roblox Studio (Open Cloud)")
    ap.add_argument("--modul", required=True, help="np. rycerz (plik wynik/<moduł>/<moduł>.<format>)")
    ap.add_argument("--format", default="fbx", choices=["fbx", "glb"])
    ap.add_argument("--tak-wgraj", action="store_true", help="NAPRAWDĘ wgraj plik na konto Roblox zalogowane w Studio")
    ap.add_argument(NOWY_MIMO, dest="nowy_mimo", action="store_true",
                    help="z --tak-wgraj: wgraj mimo zapisanego wcześniejszego wgrania — tworzy KOLEJNY trwały zasób")
    ap.add_argument("--asset", default="", help="pomiń wgrywanie: wstaw istniejący zasób o tym numerze")
    ap.add_argument("--sprawdz", default="", help="sama kontrola modelu o tej nazwie w kontenerze (bez wgrywania i wstawiania)")
    ap.add_argument("--bez-naprawy", action="store_true")
    ap.add_argument("--wyj", default=os.path.join(WYNIK, "_roblox"))
    a = ap.parse_args(argv)
    if a.asset and not _ID_ZASOBU.match(a.asset):
        ap.error("--asset to numer zasobu (same cyfry)")
    if a.nowy_mimo and (not a.tak_wgraj or a.asset or a.sprawdz):
        ap.error("%s działa tylko razem z --tak-wgraj (bez --asset i --sprawdz)" % NOWY_MIMO)

    from studio_mcp import StudioMCP, StudioError, first_studio_id
    from swiat.postacie.roblox_postac import ROZMIESZCZENIE, PRZESUNIECIE, luau as literal

    plik = os.path.join(WYNIK, a.modul, "%s.%s" % (a.modul, a.format))
    raport = os.path.join(WYNIK, a.modul, "raport.json")
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

    # --- stan poprzedniego wgrania: decyzja zapada PRZED połączeniem ze Studio
    plik_stanu = sciezka_stanu(a.modul, a.format)
    stan = None
    akcja = None
    plik_zmieniony = False
    if not a.sprawdz and not a.asset:
        stan = wczytaj_stan(plik_stanu)
        akcja, komunikat = decyzja_wgrania(stan, a.nowy_mimo)
        if stan:
            print("poprzednie:  %s — etap „%s”, operacja %s, zasób %s, moderacja %s (%s)"
                  % (os.path.relpath(plik_stanu, REPO).replace("\\", "/"), stan.get("etap"), stan.get("operacja") or "-",
                     stan.get("asset") or "-", stan.get("moderacja") or "-", stan.get("czas") or "?"))
        if komunikat:
            print(komunikat)
        if akcja in ("wznow_operacje", "wznow_zasob") and stan.get("sha256") and os.path.isfile(plik) \
                and stan["sha256"] != sha256_pliku(plik):
            plik_zmieniony = True
            print("UWAGA: plik %s zmienił się od wgrania — --tak-wgraj wstawi STARĄ wersję z poprzedniego wgrania "
                  "(operacja %s, zasób %s), nie nową. Żeby wgrać nową wersję: --tak-wgraj %s (to utworzy KOLEJNY trwały "
                  "zasób na koncie)." % (os.path.relpath(plik, REPO).replace("\\", "/"), stan.get("operacja") or "-",
                                         stan.get("asset") or "-", NOWY_MIMO))
        if akcja == "stop" and a.tak_wgraj:
            sys.exit("Zatrzymano bez wgrywania (stan w %s)." % plik_stanu)
        if akcja == "wgraj":
            if not os.path.isfile(plik):
                sys.exit("Nie ma pliku — najpierw `python -B swiat/postacie/przebuduj.py %s` (eksporty są poza gitem)." % a.modul)
            mb = os.path.getsize(plik) / 1e6
            print("rozmiar:     %.2f MB (limit %d MB)" % (mb, LIMIT_MB))
            if mb > LIMIT_MB:
                sys.exit("Plik za duży na jedno wgranie.")
    roz = ROZMIESZCZENIE.get(a.modul)
    os.makedirs(a.wyj, exist_ok=True)

    st = {}                                                         # bieżący stan wgrania (to, co jest w pliku)

    def aktualizuj(**zmiany):
        st.update(zmiany, czas=teraz())
        try:
            zapisz_stan(plik_stanu, st)
        except OSError as e:
            print("!!! NIE UDAŁO SIĘ ZAPISAĆ STANU %s (%s). ZANOTUJ RĘCZNIE: %s"
                  % (plik_stanu, e, json.dumps({k: st.get(k) for k in ("etap", "operacja", "asset", "moderacja")},
                                               ensure_ascii=False)))

    try:
        with StudioMCP() as s:
            sid = first_studio_id(s)
            if not sid:
                sys.exit("Roblox Studio nie jest podłączone.")

            def luau(kod):
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
                if r["is_error"]:
                    raise StudioError(r["text"])
                try:
                    return json.loads(r["text"])
                except ValueError:
                    raise StudioError("execute_luau nie zwróciło JSON: %s" % (r["text"] or "")[:300])

            def chmura(metoda, endpoint, body=None, files=None, scopes=("asset:read",)):
                arg = {"method": metoda, "endpoint": endpoint, "scopes": list(scopes), "studio_id": sid}
                if body is not None:
                    arg["body"] = json.dumps(body)
                if files:
                    arg["files"] = files
                r = s.call("open_cloud_invoke", arg, timeout=300)
                tekst = r["text"] or ""
                kod, dane = rozbierz_odpowiedz(tekst)
                return kod, dane, tekst, bool(r["is_error"])

            def kontrola(model):
                return luau(KONTROLA.replace("__KONTENER__", KONTENER).replace("__MODEL__", json.dumps(model, ensure_ascii=False)))

            def spis():
                return luau(SPIS.replace("__KONTENER__", KONTENER))

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
                nazwa_zasobu = nazwa[:50]
                if not asset:
                    if not a.tak_wgraj:
                        if akcja == "wgraj":
                            print("PLAN: wgranie „%s” jako zasób Model, wstawienie do Workspace/%s, kontrola, naprawa, zrzuty."
                                  % (nazwa, KONTENER))
                        elif akcja in ("wznow_operacje", "wznow_zasob"):
                            print("PLAN: z --tak-wgraj skrypt NIC nie wgra, tylko wznowi poprzednie wgranie (%s)." % akcja)
                        else:
                            print("PLAN: z --tak-wgraj skrypt się zatrzyma (patrz wyżej).")
                        print("Nic nie wysłano. Żeby naprawdę wgrać, dodaj --tak-wgraj.")
                        return
                    if stan and str(stan.get("userId") or "") not in ("", str(kto["userId"])):
                        print("UWAGA: poprzednie wgranie zrobiło konto %s, w Studio jest zalogowane %s."
                              % (stan.get("userId"), kto["userId"]))
                    if akcja == "wgraj":
                        poprzednie = []
                        if stan:
                            poprzednie = list(stan.get("poprzednie") or []) + [{k: v for k, v in stan.items() if k != "poprzednie"}]
                        st.clear()
                        st.update(modul=a.modul, format=a.format, plik=os.path.relpath(plik, REPO).replace("\\", "/"),
                                  sha256=sha256_pliku(plik), rozmiar=os.path.getsize(plik), nazwa_zasobu=nazwa_zasobu,
                                  userId=kto["userId"], placeId=kto["placeId"], operacja="", asset="", moderacja="")
                        if poprzednie:
                            st["poprzednie"] = poprzednie
                        st.update(etap="wysylanie", czas=teraz())
                        try:
                            zapisz_stan(plik_stanu, st)               # BEZ tego zapisu nie wysyłamy
                        except OSError as e:
                            sys.exit("Nie da się zapisać stanu wgrania (%s): %s — nic nie wysłano." % (plik_stanu, e))
                        kod, dane, tekst, blad_post, wyjatek = 0, None, "", False, None
                        try:
                            kod, dane, tekst, blad_post = chmura("POST", "/assets/v1/assets", {"request": {
                                "assetType": "Model", "displayName": nazwa_zasobu, "description": "Test importu siatki z Blendera.",
                                "creationContext": {"creator": {"userId": str(kto["userId"])}}}},
                                files=[{"name": "fileContent", "path": plik}], scopes=("asset:read", "asset:write"))
                        except StudioError as e:
                            wyjatek = e
                        etap, op, opis = ocen_wyslanie(kod, dane, tekst, wyjatek, blad_post)
                        aktualizuj(etap=etap, operacja=op, kod_http=kod, odpowiedz=(tekst or str(wyjatek or ""))[:4000])
                        if etap == "nie_wyslano":
                            print("STUDIO ODRZUCIŁO PLIK: folder nie jest zatwierdzony do wgrywania.")
                            print("Do kliknięcia przez człowieka: Assistant → Settings → MCP Permissions → approved upload directories →")
                            print("  " + os.path.dirname(os.path.dirname(plik)))
                            sys.exit(3)
                        if etap == "odrzucone_zadanie":
                            sys.exit("Wgranie nie powiodło się (%s), zasób nie powstał: %s" % (opis, tekst[:400]))
                        if etap != "operacja":
                            sys.exit("NIE WIADOMO, CZY ZASÓB POWSTAŁ (%s). NIE powtarzaj wgrania na ślepo — sprawdź Creator "
                                     "Dashboard. Surowa odpowiedź jest w %s." % (opis, plik_stanu))
                        print("wgrano, operacja %s — czekam na wynik…" % op)
                    else:
                        st.clear()
                        st.update(stan)
                        op = str(st.get("operacja") or "")
                    asset = str(st.get("asset") or "")
                    moderacja = str(st.get("moderacja") or "")
                    if not asset:
                        koniec = time.time() + OPERACJA_MAX
                        while True:
                            kod, dane, tekst, _ = chmura("GET", "/assets/v1/operations/%s" % op)
                            wo = wynik_operacji(dane)
                            if wo["gotowe"] or time.time() >= koniec:
                                break
                            time.sleep(OPERACJA_CO)
                        if not wo["gotowe"]:
                            sys.exit("Operacja %s nie skończyła się w %d s — NIE wgrywaj ponownie; to samo polecenie z "
                                     "--tak-wgraj później wznowi czekanie (stan w %s). Ostatnia odpowiedź: %s"
                                     % (op, OPERACJA_MAX, plik_stanu, tekst[:300]))
                        if wo["blad"] or not wo["asset"]:
                            aktualizuj(etap="operacja_blad" if wo["blad"] else "nieznane", blad=wo["blad"],
                                       odpowiedz=tekst[:4000])
                            sys.exit("Operacja %s skończyła się bez numeru zasobu (%s). NIE wgrywaj ponownie na ślepo — "
                                     "sprawdź Creator Dashboard." % (op, json.dumps(wo["blad"], ensure_ascii=False)[:300]))
                        asset, moderacja = wo["asset"], wo["moderacja"]
                        aktualizuj(etap="zasob", asset=asset, moderacja=moderacja)
                    klasa = klasa_moderacji(moderacja)
                    print("zasób %s, moderacja: %s (%s)" % (asset, moderacja or "?", klasa))
                    koniec = time.time() + MODERACJA_MAX
                    while klasa in ("oczekuje", "nieznany") and time.time() < koniec:
                        time.sleep(MODERACJA_CO)
                        kod, dane, tekst, _ = chmura("GET", "/assets/v1/assets/%s" % asset)
                        nowa = moderacja_z_zasobu(dane)
                        if nowa and nowa != moderacja:
                            moderacja, klasa = nowa, klasa_moderacji(nowa)
                            aktualizuj(moderacja=moderacja)
                            print("moderacja:   %s (%s)" % (moderacja, klasa))
                    wynik.update(asset=asset, moderacja=moderacja)
                    if klasa == "odrzucony":
                        sys.exit("Zasób %s ODRZUCONY przez moderację (%s). Nie wgrywaj tego samego pliku drugi raz."
                                 % (asset, moderacja))
                    if klasa == "nieznany":
                        sys.exit("Zasób %s jest wgrany, ale stanu moderacji nie da się odczytać (%s) po %d s. NIE wgrywaj "
                                 "ponownie. Sprawdź zasób w Creator Dashboard; gdy jest zatwierdzony, wstaw go przez "
                                 "--asset %s (to niczego nie wgrywa). Numer jest w %s."
                                 % (asset, moderacja or "brak pola moderationResult", MODERACJA_MAX, asset, plik_stanu))
                    if klasa != "zatwierdzony":
                        sys.exit("Zasób %s czeka na moderację (%s) — NIE wgrywaj ponownie. Numer jest w %s; to samo polecenie "
                                 "z --tak-wgraj później wznowi czekanie i wstawi go po zatwierdzeniu (gdy Creator Dashboard "
                                 "pokaże zatwierdzenie, można też od razu --asset %s)." % (asset, moderacja, plik_stanu, asset))
                    if plik_zmieniony:
                        wynik["plik_zmieniony_od_wgrania"] = True
                        print("UWAGA: wstawiam zasób %s z poprzedniego wgrania — to STARA wersja pliku (patrz wyżej)." % asset)
                    nazwa_zasobu = str(st.get("nazwa_zasobu") or nazwa_zasobu)

                # --- wstawienie pod nazwą, której jeszcze nie ma w kontenerze, i odszukanie dokładnie tego obiektu
                przed = spis()
                cel = wybierz_nazwe(nazwa, [e["n"] for e in przed.get("kontener") or []])
                if cel != nazwa:
                    print("nazwa:       „%s” już jest w kontenerze — nowy import dostaje nazwę „%s”" % (nazwa, cel))
                r = s.call("insert_asset", {"assetId": asset, "assetName": cel, "assetType": "Model",
                                            "parentPath": "game.Workspace.%s" % KONTENER, "studio_id": sid}, timeout=300)
                print("wstawianie:", (r["text"] or "")[:300].replace("\n", " "))
                wynik["wstawianie"] = (r["text"] or "")[:1500]
                if r["is_error"]:
                    if a.asset:
                        sys.exit("Nie udało się wstawić zasobu %s. Zasób już istnieje — NIE wgrywaj go ponownie (--tak-wgraj "
                                 "utworzyłoby nowy zasób); uruchom ponownie z --asset %s." % (asset, asset))
                    sys.exit("Nie udało się wstawić zasobu %s. Zasób jest wgrany — NIE wgrywaj go ponownie; to samo polecenie "
                             "z --tak-wgraj (stan w %s) albo --asset %s spróbuje wstawić go jeszcze raz."
                             % (asset, plik_stanu, asset))
                po = spis()
                wybor, blad = wybierz_nowa(przed, po, {cel, nazwa, nazwa_zasobu, cel[:50]}, r["text"] or "")
                if blad:
                    sys.exit("Wstawianie: %s Sprawdź Workspace/%s w Studio ręcznie." % (blad, KONTENER))
                prz = luau(PRZENIES.replace("__KONTENER__", KONTENER).replace(
                    "__JSON__", json.dumps(json.dumps(dict(wybor, cel=cel)))))
                if prz.get("blad"):
                    sys.exit("Wstawianie: %s" % prz["blad"])
                for krok in prz.get("kroki") or []:
                    print("wstawianie:  %s" % krok)
                print("model:       %s" % prz.get("sciezka", cel))
                wynik["model"] = {"nazwa": cel, "sciezka": prz.get("sciezka"), "klasa": prz.get("klasa"),
                                  "znaleziony": wybor, "kroki": prz.get("kroki") or []}
                model = cel

            bledy = []
            try:
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
                    cel_xz = [px + lewo[0] * 6.5, pz + lewo[1] * 6.5]
                    par = {"wzrost": oczek["wymiary"][1], "cel": cel_xz, "zrodlo": "%s.%s" % (a.modul, a.format)}
                    if k.get("przod"):
                        par["przod_teraz"], par["przod_cel"] = k["przod"], [fx, fz]
                    n = luau(NAPRAWA.replace("__KONTENER__", KONTENER).replace("__MODEL__", json.dumps(model, ensure_ascii=False))
                             .replace("__PARAMETRY__", literal(par)))
                    wynik["naprawa"] = n
                    if n.get("blad"):
                        bledy.append("naprawa: %s" % n["blad"])
                    for krok in n.get("kroki", [n.get("blad", "?")]):
                        print("naprawa:     %s" % krok)
                    wynik["kontrola_po"] = kontrola(model)
                    if wynik["kontrola_po"].get("blad"):
                        bledy.append("kontrola po naprawie: %s" % wynik["kontrola_po"]["blad"])
                    for i, (odl, bok) in enumerate(((11.0, 0.35), (9.0, -0.6))):
                        sx, sz = (px + cel_xz[0]) / 2, (pz + cel_xz[1]) / 2
                        kx, kz = fx * math.cos(bok) - fz * math.sin(bok), fx * math.sin(bok) + fz * math.cos(bok)
                        try:
                            r = s.call("screen_capture", {"studio_id": sid, "capture_id": "import_%s_%d" % (a.modul, i),
                                                          "camera_position": [sx + kx * odl, 5.5, sz + kz * odl],
                                                          "look_at_position": [sx, 3.0, sz]}, timeout=120)
                        except StudioError as e:
                            bledy.append("zrzut %d: %s" % (i, e))
                            continue
                        if r["is_error"] or not r["images"]:
                            bledy.append("zrzut %d: %s" % (i, (r["text"] or "brak obrazu")[:200]))
                            continue
                        png = os.path.join(a.wyj, "import_%s_%s_%d.png" % (a.modul, a.format, i))
                        with open(png, "wb") as f:
                            f.write(r["images"][0])
                        print("zrzut:       %s (po lewej ręce postaci z klocków stoi import)" % png)
            except StudioError as e:
                bledy.append("Studio: %s" % e)
            if bledy:
                wynik["bledy"] = bledy
            sciezka = os.path.join(a.wyj, "import_%s_%s.json" % (a.modul, a.format))
            with open(sciezka, "w", encoding="utf-8", newline="\n") as f:
                json.dump(wynik, f, ensure_ascii=False, indent=1)
            print("zapisano:    %s" % sciezka)
            if bledy:
                sys.exit("Niektóre kroki się nie udały: %s" % "; ".join(bledy))
    except StudioError as e:
        if st:
            print("Stan wgrania jest zapisany w %s — to samo polecenie z --tak-wgraj wznowi od niego, NIE wgra drugi raz."
                  % plik_stanu)
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
