#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Postacie z biblioteki jako rigi z KLOCKÓW w Roblox Studio — bez wgrywania czegokolwiek na konto Roblox.

    # z głównego folderu repozytorium
    python -B swiat/postacie/roblox_postac.py                        # wszystkie postacie z ROZMIESZCZENIE
    python -B swiat/postacie/roblox_postac.py --tylko rycerz,pies    # wybrane
    python -B swiat/postacie/roblox_postac.py --sucho                # tylko policz i zapisz JSON, bez Studio
    python -B swiat/postacie/roblox_postac.py --usun                 # usuń kontener Workspace/TestPostaci
    python -B swiat/postacie/roblox_postac.py --liniowo              # bez Blendera (klipy liniowo między kluczami)

Co powstaje w Studio (tylko we własnym kontenerze `Workspace/TestPostaci` z atrybutem `Wygenerowane`):
  Model <Nazwa> → HumanoidRootPart (zakotwiczony) + niewidzialne części kości połączone Motor6D + bryły przyspawane
  do kości + Attachmenty + AnimationController/Animator + `AnimSaves` z klipami jako KeyframeSequence.
Klipy można od razu otworzyć w Animation Editorze; opublikowanie ich jako zasobów Animation to osobna decyzja
(zasób animacji działa tylko w grach tego samego właściciela co animacja).

Zasady wspólnego miejsca Team Create: nic poza własnym kontenerem nie jest zmieniane; przed i po budowie punkt
historii (cofa się jednym Ctrl+Z); skrypt niczego nie publikuje i nie zapisuje miejsca.
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for sciezka in (REPO, os.path.join(REPO, "tools")):
    if sciezka not in sys.path:
        sys.path.insert(0, sciezka)

from swiat.biblioteka.podglad import blender_exe, zajmij_blender, zwolnij_blender  # noqa: E402
from swiat.postacie.biblioteka.postac import Akcesorium, Postac, pakiet, przymiarka, zapisz_json  # noqa: E402
from swiat.postacie.biblioteka.roblox_klocki import akcesoria_noszone, probki_liniowe, rig  # noqa: E402

KONTENER = "TestPostaci"
PLACE_ID = 129485428021967                                        # to miejsce i żadne inne
PRZESUNIECIE = (0.0, -700.0)                                      # miasteczko w Studio: układ miasta + (0, 0, −700)
# id modułu -> (x, z w układzie miasta, punkt, na który postać patrzy, wysokość nad ziemią)
ROZMIESZCZENIE = {
    # „komitet powitalny” przed punktem startu: gracz po wejściu patrzy w stronę gospody (słońce ma za plecami),
    # postacie stoją w słońcu po obu stronach czerwonej ścieżki i patrzą na płytę startu
    "rycerz": {"poz": (32.0, 17.5), "patrz": (21.4, 18.0)},
    "karczmarz": {"poz": (38.0, 22.5), "patrz": (21.4, 18.0)},
    "kot_mag": {"poz": (25.5, 28.0), "patrz": (21.4, 18.0)},
    "pies": {"poz": (30.0, 31.0), "patrz": (21.4, 18.0)},
    "slime": {"poz": (20.0, 30.5), "patrz": (21.4, 18.0)},
    "smok": {"poz": (15.0, 26.5), "patrz": (21.4, 18.0)},
    # manekiny z zestawami ekwipunku („przymierzalnia”) po drugiej stronie płyty startu; zestaw = nazwa na podpowiedzi
    "zestaw_rekrut": {"poz": (28.5, 8.5), "patrz": (21.4, 18.0), "nazwa": "Manekin Rekrut", "zestaw": "Zestaw Rekruta"},
    "zestaw_rycerz": {"poz": (34.5, 10.0), "patrz": (21.4, 18.0), "nazwa": "Manekin Rycerz", "zestaw": "Zestaw Rycerza"},
    "zestaw_mag": {"poz": (40.0, 13.5), "patrz": (21.4, 18.0), "nazwa": "Manekin Mag", "zestaw": "Zestaw Maga"},
}
PRIORYTETY = {"idle": "Idle", "idle_lot": "Idle", "chod": "Movement", "bieg": "Movement", "lot": "Movement"}

BUDOWA = r'''
local D = __DANE__
local KONTENER = "__KONTENER__"
if game.PlaceId ~= __PLACE__ then
	return "STOP: to nie jest miejsce gry (PlaceId " .. tostring(game.PlaceId) .. ")"
end
local CH = game:GetService("ChangeHistoryService")
local kont = workspace:FindFirstChild(KONTENER)
if kont and kont:GetAttribute("Wygenerowane") ~= true then
	return "STOP: w Workspace jest już obiekt '" .. KONTENER .. "' bez atrybutu Wygenerowane — nie ruszam cudzej pracy"
end
CH:SetWaypoint("Postacie: przed budową " .. D.model)
if not kont then
	kont = Instance.new("Folder")
	kont.Name = KONTENER
	kont:SetAttribute("Wygenerowane", true)
	kont:SetAttribute("Zrodlo", "swiat/postacie/roblox_postac.py")
	kont.Parent = workspace
end
local stary = kont:FindFirstChild(D.model)
if stary then
	stary:Destroy()
end

-- podłoże pod postacią: promień w dół z pominięciem własnego kontenera
local params = RaycastParams.new()
params.FilterType = Enum.RaycastFilterType.Exclude
params.FilterDescendantsInstances = { kont }
local traf = workspace:Raycast(Vector3.new(D.poz[1], 200, D.poz[2]), Vector3.new(0, -400, 0), params)
local y = traf and traf.Position.Y or 0
local pos = Vector3.new(D.poz[1], y + D.nad, D.poz[2])
local baza = CFrame.lookAt(pos, Vector3.new(D.patrz[1], pos.Y, D.patrz[2]))

local model = Instance.new("Model")
model.Name = D.model
model:SetAttribute("Wygenerowane", true)
model:SetAttribute("Postac", D.id)
model:SetAttribute("Zbudowano", "__CZAS__")
if D.zestaw ~= "" then
	model:SetAttribute("Zestaw", D.zestaw)
	model:SetAttribute("ZestawId", D.id_modulu)
end

local function bezFizyki(p)
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.Massless = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
end

local hrpPos = Vector3.new(D.hrp[1], D.hrp[2], D.hrp[3])
local hrp = Instance.new("Part")
hrp.Name = "HumanoidRootPart"
hrp.Size = Vector3.new(2, 2, 1)
hrp.Transparency = 1
hrp.Anchored = true
bezFizyki(hrp)
hrp.CFrame = baza * CFrame.new(hrpPos)
hrp.Parent = model
model.PrimaryPart = hrp

local kosci = {}
for i, k in D.kosci do
	local p = Instance.new("Part")
	p.Name = k[1]
	p.Size = Vector3.new(k[9], k[10], k[11])
	p.Transparency = 1
	p.Anchored = false
	p.CastShadow = false
	bezFizyki(p)
	p.CFrame = baza * CFrame.new(k[6], k[7], k[8])
	p.Parent = model
	kosci[i] = p
end
for i, k in D.kosci do
	local rodzic, srodekRodzica
	if k[2] == 0 then
		rodzic, srodekRodzica = hrp, hrpPos
	else
		local kr = D.kosci[k[2]]
		rodzic, srodekRodzica = kosci[k[2]], Vector3.new(kr[6], kr[7], kr[8])
	end
	local staw = Vector3.new(k[3], k[4], k[5])
	local m = Instance.new("Motor6D")
	m.Name = k[12]
	m.C0 = CFrame.new(staw - srodekRodzica)
	m.C1 = CFrame.new(staw - Vector3.new(k[6], k[7], k[8]))
	m.Part0 = rodzic
	m.Part1 = kosci[i]
	m.Parent = kosci[i]
end

local grupy = {}
for i, nazwa in D.grupy do
	if i > 1 then
		local g = Instance.new("Model")
		g.Name = nazwa
		g.Parent = model
		grupy[i] = g
	end
end
local n = 0
for _, c in D.czesci do
	local ks = c[2]
	local p
	if ks == 3 then
		p = Instance.new("WedgePart")
	elseif ks == 4 then
		p = Instance.new("CornerWedgePart")
	else
		p = Instance.new("Part")
		p.Shape = if ks == 1 then Enum.PartType.Ball elseif ks == 2 then Enum.PartType.Cylinder else Enum.PartType.Block
	end
	p.Name = c[3]
	p.Size = Vector3.new(c[10], c[11], c[12])
	p.CFrame = baza * CFrame.new(c[4], c[5], c[6]) * CFrame.fromOrientation(c[7], c[8], c[9])
	p.Color = Color3.fromHex(c[13])
	local mat = D.materialy[c[14] + 1]
	p.Material = Enum.Material[mat[1]]
	p.Reflectance = mat[2]
	p.Anchored = false
	bezFizyki(p)
	if c[16] ~= "" then
		local sm = Instance.new("SpecialMesh")
		sm.MeshType = Enum.MeshType[c[16]]
		sm.Parent = p
	end
	local kosc = kosci[c[1]]
	local w = Instance.new("WeldConstraint")
	w.Part0 = kosc
	w.Part1 = p
	w.Parent = p
	p.Parent = if c[15] == 0 then kosc else grupy[c[15] + 1]
	n += 1
end
for _, z in D.zaczepy do
	local a = Instance.new("Attachment")
	a.Name = z[1]
	a.CFrame = CFrame.new(z[3], z[4], z[5]) * CFrame.fromOrientation(z[6], z[7], z[8])
	a.Parent = kosci[z[2]]
end
local ac = Instance.new("AnimationController")
ac.Parent = model
local an = Instance.new("Animator")
an.Parent = ac
local saves = Instance.new("Model")
saves.Name = "AnimSaves"
saves.Parent = model
model.Parent = kont
CH:SetWaypoint("Postacie: zbudowano " .. D.model)
return string.format("%s: %d brył, %d kości, %d zaczepów; podłoże: %s na y = %.2f; stoi w (%.1f; %.1f; %.1f)",
	D.model, n, #D.kosci, #D.zaczepy, traf and traf.Instance:GetFullName() or "BRAK", y, pos.X, pos.Y, pos.Z)
'''

KLIP = r'''
local K = __KLIP__
local kont = workspace:FindFirstChild("__KONTENER__")
local model = kont and kont:FindFirstChild(K.model)
if not model or kont:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak modelu " .. K.model
end
local saves = model:FindFirstChild("AnimSaves")
local stary = saves:FindFirstChild(K.n)
if stary then
	stary:Destroy()
end
-- które kości potrzebują pozy: animowane i wszyscy ich przodkowie (łańcuch od HumanoidRootPart musi być ciągły)
local kolumna, potrzebna = {}, {}
for j, idx in K.kosci do
	kolumna[idx] = j
	local i = idx
	while i ~= 0 and not potrzebna[i] do
		potrzebna[i] = true
		i = K.szkielet[i][2]
	end
end
local ks = Instance.new("KeyframeSequence")
ks.Name = K.n
ks.Loop = K.petla
ks.Priority = Enum.AnimationPriority[K.priorytet]
local poz = 0
for f = 0, K.dl do
	local w = K.klatki[f + 1]
	local kf = Instance.new("Keyframe")
	kf.Name = if f == 0 then "Start" elseif f == K.dl then "Koniec" else "Keyframe"
	kf.Time = f / K.fps
	local korzen = Instance.new("Pose")
	korzen.Name = "HumanoidRootPart"
	korzen.Weight = 0
	korzen.Parent = kf
	local pozy = {}
	for i, b in K.szkielet do
		if potrzebna[i] then
			local ps = Instance.new("Pose")
			ps.Name = b[1]
			ps.EasingStyle = Enum.PoseEasingStyle.Linear
			local j = kolumna[i]
			if j then
				local o = (j - 1) * 6
				ps.CFrame = CFrame.new(w[o + 1], w[o + 2], w[o + 3]) * CFrame.fromOrientation(w[o + 4], w[o + 5], w[o + 6])
				ps.Weight = 1
			else
				ps.Weight = 0
			end
			ps.Parent = if b[2] == 0 then korzen else pozy[b[2]]
			pozy[i] = ps
			poz += 1
		end
	end
	kf.Parent = ks
end
ks.Parent = saves
return string.format("%s/%s: %d klatek (%.2f s), %d póz, pętla %s", K.model, K.n, K.dl + 1, K.dl / K.fps, poz, tostring(K.petla))
'''

POKAZ = r'''
local kont = workspace:FindFirstChild("__KONTENER__")
if not kont or kont:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera"
end
local stary = kont:FindFirstChild("PokazAnimacji")
if stary then
	stary:Destroy()
end
local s = Instance.new("Script")
s.Name = "PokazAnimacji"
s.Source = __ZRODLO__
s.Parent = kont
game:GetService("ChangeHistoryService"):SetWaypoint("Postacie: skrypt pokazu animacji")
local modeli, czesci = 0, 0
for _, d in kont:GetChildren() do
	if d:IsA("Model") then
		modeli += 1
	end
end
for _, d in kont:GetDescendants() do
	if d:IsA("BasePart") then
		czesci += 1
	end
end
return string.format("skrypt pokazu zainstalowany (%d znaków); w kontenerze %d postaci, %d części", #s.Source, modeli, czesci)
'''

EKWIPUNEK = r'''
local kont = workspace:FindFirstChild("__KONTENER__")
if not kont or kont:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera"
end
for _, nazwa in { "DaneEkwipunku", "Przymierzalnia" } do
	local stary = kont:FindFirstChild(nazwa)
	if stary then
		stary:Destroy()
	end
end
local dane = Instance.new("ModuleScript")
dane.Name = "DaneEkwipunku"
dane.Source = __DANE__
dane.Parent = kont
local s = Instance.new("Script")
s.Name = "Przymierzalnia"
s.Source = __ZRODLO__
s.Parent = kont
game:GetService("ChangeHistoryService"):SetWaypoint("Postacie: przymierzalnia zestawów")
return string.format("przymierzalnia zainstalowana: dane %d znaków, skrypt %d znaków", #dane.Source, #s.Source)
'''

USUN = r'''
local CH = game:GetService("ChangeHistoryService")
local kont = workspace:FindFirstChild("__KONTENER__")
if not kont then
	return "nie ma czego usuwać"
end
if kont:GetAttribute("Wygenerowane") ~= true then
	return "STOP: '__KONTENER__' nie ma atrybutu Wygenerowane — nie ruszam cudzej pracy"
end
CH:SetWaypoint("Postacie: przed usunięciem __KONTENER__")
kont:Destroy()
CH:SetWaypoint("Postacie: usunięto __KONTENER__")
return "USUNIĘTO Workspace/__KONTENER__"
'''


def luau(v):
    """Wartość Pythona jako literał Luau (słownik -> tabela z kluczami-nazwami)."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, (list, tuple)):
        return "{" + ",".join(luau(x) for x in v) + "}"
    if isinstance(v, dict):
        return "{" + ",".join("%s=%s" % (k, luau(x)) for k, x in v.items()) + "}"
    raise TypeError(type(v))


def wczytaj_modul(sciezka):
    spec = importlib.util.spec_from_file_location("postac_" + os.path.splitext(os.path.basename(sciezka))[0], sciezka)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def postacie_z_modulu(sciezka):
    """Postacie z modułu. Moduł z samym ekwipunkiem (bez postaci) dostaje szary manekin R15 z założonymi częściami,
    tak jak w podglądzie Blendera (przymiarka())."""
    w = wczytaj_modul(sciezka).zbuduj()
    w = list(w) if isinstance(w, (list, tuple)) else [w]
    postacie = [o for o in w if isinstance(o, Postac)]
    if not postacie:
        akcesoria = [o for o in w if isinstance(o, Akcesorium)]
        if akcesoria:
            postacie = [przymiarka(os.path.splitext(os.path.basename(sciezka))[0] + "_przymiarka", akcesoria)]
    return postacie


def probki_z_blendera(postacie):
    """Próbki klipów co klatkę z Blendera (pod wspólną blokadą). Zwraca {id: {klip: {kość: {...}}}}."""
    tmp = tempfile.mkdtemp(prefix="bc_probki_")
    wej, wyj = os.path.join(tmp, "pakiet.json"), os.path.join(tmp, "probki.json")
    zapisz_json(pakiet(postacie), wej)
    polecenie = [blender_exe(), "-b", "--factory-startup", "--python-exit-code", "1", "--python",
                 os.path.join(TU, "biblioteka", "blender_probki.py"), "--", wej, wyj]
    blokada = zajmij_blender()
    try:
        r = subprocess.run(polecenie, capture_output=True, timeout=10 * 60,
                           creationflags=0x08000000 if os.name == "nt" else 0)
    finally:
        zwolnij_blender(blokada)
    if r.returncode != 0 or not os.path.isfile(wyj):
        tekst = (r.stdout + r.stderr).decode("utf-8", "replace")
        raise RuntimeError("Blender nie policzył próbek (kod %d):\n%s" % (r.returncode, "\n".join(tekst.splitlines()[-25:])))
    with open(wyj, encoding="utf-8") as f:
        return json.load(f)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Postacie jako rigi z klocków w Roblox Studio (bez uploadu)")
    ap.add_argument("--tylko", default="", help="id modułów po przecinku (domyślnie wszystkie z ROZMIESZCZENIE)")
    ap.add_argument("--sucho", action="store_true", help="tylko policz i zapisz JSON, bez Studio")
    ap.add_argument("--usun", action="store_true", help="usuń kontener Workspace/%s" % KONTENER)
    ap.add_argument("--liniowo", action="store_true", help="klipy liniowo między kluczami (bez Blendera)")
    ap.add_argument("--bez-klipow", action="store_true")
    ap.add_argument("--bez-pokazu", action="store_true", help="nie instaluj skryptu PokazAnimacji (pokaz klipów w Play/Run)")
    ap.add_argument("--wyj", default=os.path.join(TU, "wynik", "_roblox"), help="folder na <id>_klocki.json")
    a = ap.parse_args()

    from studio_mcp import StudioMCP, StudioError, first_studio_id

    def studio(fn):
        try:
            with StudioMCP() as s:
                sid = first_studio_id(s)
                if not sid:
                    sys.exit("Roblox Studio nie jest podłączone (Assistant → Manage MCP Servers → Enable Studio as MCP server).")

                def wykonaj(kod):
                    r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
                    if r["is_error"]:
                        raise StudioError(r["text"])
                    return r["text"].strip()
                return fn(wykonaj)
        except StudioError as e:
            sys.exit("BŁĄD Studio: %s" % e)

    if a.usun:
        print(studio(lambda wykonaj: wykonaj(USUN.replace("__KONTENER__", KONTENER))))
        return

    wybrane = [x for x in a.tylko.split(",") if x] or list(ROZMIESZCZENIE)
    postacie = []
    for mid in wybrane:
        if mid not in ROZMIESZCZENIE:
            sys.exit("Nie ma rozmieszczenia dla %r (są: %s)" % (mid, ", ".join(ROZMIESZCZENIE)))
        znalezione = postacie_z_modulu(os.path.join(TU, mid + ".py"))
        if not znalezione:
            sys.exit("Moduł %s nie zwraca postaci" % mid)
        postacie.append((mid, znalezione[0]))
    probki = {}
    if not a.bez_klipow:
        if a.liniowo:
            probki = {p.id: probki_liniowe(p) for _, p in postacie}
        else:
            t0 = time.time()
            probki = probki_z_blendera([p for _, p in postacie])
            print("próbki klipów z Blendera: %.0f s" % (time.time() - t0))
    os.makedirs(a.wyj, exist_ok=True)
    dane, ekwipunek = [], {}
    for mid, p in postacie:
        d = rig(p, probki.get(p.id))
        roz = ROZMIESZCZENIE[mid]
        d["model"] = p.nazwa.replace("„", "").replace("”", "").replace('"', "")
        d["poz"] = [roz["poz"][0] + PRZESUNIECIE[0], roz["poz"][1] + PRZESUNIECIE[1]]
        d["patrz"] = [roz["patrz"][0] + PRZESUNIECIE[0], roz["patrz"][1] + PRZESUNIECIE[1]]
        d["nad"] = float(roz.get("nad_ziemia", 0.0))
        if roz.get("nazwa"):
            d["model"] = roz["nazwa"]
        d["zestaw"], d["id_modulu"] = roz.get("zestaw", ""), mid
        if roz.get("zestaw"):
            akcesoria, materialy, uw = akcesoria_noszone(p)
            ekwipunek[mid] = {"nazwa": roz["zestaw"], "materialy": materialy, "akcesoria": akcesoria}
            d["uwagi"] += uw
        zapisz_json(d, os.path.join(a.wyj, p.id + "_klocki.json"))
        print("%-10s %3d brył -> %3d części Roblox, %2d kości, %2d zaczepów, klipy: %s"
              % (p.id, len(p.czesci) + sum(len(x[0].czesci) for x in p.zalozone), len(d["czesci"]), len(d["kosci"]),
                 len(d["zaczepy"]), ", ".join("%s %d kl." % (k["n"], k["dl"] + 1) for k in d["klipy"]) or "brak"))
        for u in d["uwagi"]:
            print("           uwaga:", u)
        dane.append(d)
    if ekwipunek:
        zapisz_json(ekwipunek, os.path.join(a.wyj, "ekwipunek_klocki.json"))
        for mid, e in ekwipunek.items():
            print("%-14s do noszenia: %d akcesoriów, %d części Roblox"
                  % (mid, len(e["akcesoria"]), sum(len(x["czesci"]) for x in e["akcesoria"])))
    if a.sucho:
        return

    def buduj(wykonaj):
        czas = time.strftime("%Y-%m-%dT%H:%M:%S")
        for d in dane:
            klipy = d.pop("klipy")
            d.pop("uwagi", None)
            kod = (BUDOWA.replace("__DANE__", luau(d)).replace("__KONTENER__", KONTENER)
                   .replace("__PLACE__", str(PLACE_ID)).replace("__CZAS__", czas))
            wynik = wykonaj(kod)
            print("Studio:", wynik)
            if wynik.startswith("STOP"):
                return
            szkielet = [[k[0], k[1]] for k in d["kosci"]]
            for k in klipy:
                k.update(model=d["model"], szkielet=szkielet, priorytet=PRIORYTETY.get(k["n"], "Action"))
                print("Studio:", wykonaj(KLIP.replace("__KLIP__", luau(k)).replace("__KONTENER__", KONTENER)))
        if not a.bez_pokazu and not a.bez_klipow:
            with open(os.path.join(TU, "roblox", "PokazAnimacji.server.luau"), encoding="utf-8") as f:
                zrodlo = f.read()
            print("Studio:", wykonaj(POKAZ.replace("__KONTENER__", KONTENER).replace("__ZRODLO__", luau(zrodlo))))
        if ekwipunek and not a.bez_pokazu:
            with open(os.path.join(TU, "roblox", "Przymierzalnia.server.luau"), encoding="utf-8") as f:
                zrodlo = f.read()
            modul = ("-- Wygenerowane przez swiat/postacie/roblox_postac.py — nie edytuj ręcznie." + chr(10) +
                     "return " + luau(ekwipunek) + chr(10))
            print("Studio:", wykonaj(EKWIPUNEK.replace("__KONTENER__", KONTENER).replace("__DANE__", luau(modul))
                                     .replace("__ZRODLO__", luau(zrodlo))))
    studio(buduj)


if __name__ == "__main__":
    main()
