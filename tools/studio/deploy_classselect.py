#!/usr/bin/env python3
"""Wdraża ekran wyboru klasy do otwartego Studio (miejsce z chmury, bez Rojo).

Kolejność: (0) python -B swiat/wybor_klasy/generuj.py  → czesci.json + efekty.json
           (1) sala z klocków: python tools/studio_buduj.py swiat/wybor_klasy/czesci.json --obrysy
           (2) ten skrypt: światła i efekty sali (z efekty.json), tekstury z paczki (tekstury.json + ID z manifestu),
               kopie modeli bohaterów, ScreenGui ClassSelect, skrypty.
Użycie: python tools/studio/deploy_classselect.py  [--bez-skryptow]

Własne kontenery: Workspace/WyborKlasy (atrybut Wygenerowane, z tools/studio_buduj.py) — tu dochodzi model „Efekty”
(światła, snop światła nad podestem, pyłki);
ReplicatedStorage/WyborKlasyModele (atrybut Wygenerowane) — kopie modeli z Workspace/TestPostaci (Karola; nie ruszane).
Punkt historii „Ekran wyboru klasy” (Ctrl+Z). Projekt: B&C/UI/Selektor bohatera.md.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/studio"))
from model_to_luau import build_luau  # noqa: E402

MODELE = {"Warrior": "Rycerz Blocky", "Scout": "Zwiadowca (import FBX)", "Mage": "Kot-Mag Crycket"}
SCRIPTS = [
    ('game:GetService("ReplicatedStorage"):WaitForChild("Shared")', "ClassData", "ModuleScript", "src/shared/ClassData.luau"),
    ('game:GetService("ReplicatedStorage"):WaitForChild("Shared")', "ClassSelectIcons", "ModuleScript", "src/shared/ClassSelectIcons.luau"),
    ('game:GetService("ReplicatedStorage"):WaitForChild("Shared")', "RaceData", "ModuleScript", "src/shared/RaceData.luau"),
    ('game:GetService("ReplicatedStorage"):WaitForChild("Shared")', "RaceIcons", "ModuleScript", "src/shared/RaceIcons.luau"),
    ('game:GetService("ReplicatedStorage"):WaitForChild("Shared")', "Items", "ModuleScript", "src/shared/Items.luau"),
    ('game:GetService("ServerScriptService"):WaitForChild("Server")', "ClassSelect", "Script", "src/server/ClassSelect.server.luau"),
    ('game:GetService("StarterPlayer").StarterPlayerScripts:WaitForChild("Client")', "ClassSelectClient", "LocalScript",
     "src/client/ClassSelectClient.client.luau"),
    ('game:GetService("StarterPlayer").StarterPlayerScripts:WaitForChild("Client")', "HUDClient", "LocalScript",
     "src/client/HUDClient.client.luau"),
]

SWIATLA = r'''
local sala = workspace:FindFirstChild("WyborKlasy")
assert(sala and sala:GetAttribute("Wygenerowane"), "najpierw: python tools/studio_buduj.py swiat/wybor_klasy/czesci.json --obrysy")
-- streaming: sala stoi daleko od gracza — grupy trwałe, żeby klient zawsze je miał (kontener sam jest Folderem)
for _, m in ipairs(sala:GetChildren()) do
	if m:IsA("Model") then m.ModelStreamingMode = Enum.ModelStreamingMode.Persistent end
end
for _, nazwa in ipairs({ "Swiatla", "Efekty" }) do
	local old = sala:FindFirstChild(nazwa)
	if old then old:Destroy() end
end
local E = game:GetService("HttpService"):JSONDecode(EFEKTY_JSON)
local ef = Instance.new("Model")
ef.Name = "Efekty"
ef.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
local function v3(t) return Vector3.new(t[1], t[2], t[3]) end
local function kotwica(nazwa, pos, cel)
	local p = Instance.new("Part")
	p.Name = nazwa
	p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch, p.CastShadow = true, false, false, false, false
	p.Transparency = 1
	p.Size = Vector3.new(0.5, 0.5, 0.5)
	p.CFrame = cel and CFrame.lookAt(pos, cel) or CFrame.new(pos)
	p.Parent = ef
	return p
end
-- światła: punktowe albo reflektor (gdy jest cel); atrybut Migot = siła migotania (animuje ClassSelectClient)
for _, d in ipairs(E.swiatla) do
	local p = kotwica(d.n, v3(d.p), d.cel and v3(d.cel))
	local l
	if d.cel then
		l = Instance.new("SpotLight")
		l.Face = Enum.NormalId.Front
		l.Angle = d.kat
	else
		l = Instance.new("PointLight")
	end
	l.Range, l.Brightness, l.Color, l.Shadows = d.zasieg, d.jasnosc, Color3.fromHex(d.kolor), d.cienie
	if d.migot and d.migot > 0 then l:SetAttribute("Migot", d.migot) end
	l.Parent = p
end
-- snop światła nad podestem: wstęgi zwrócone do kamery, jaśniejsze u góry
for _, d in ipairs(E.snopy) do
	local a, b = kotwica(d.n, v3(d.p0)), kotwica(d.n .. " dół", v3(d.p1))
	local a0, a1 = Instance.new("Attachment"), Instance.new("Attachment")
	a0.Parent, a1.Parent = a, b
	local beam = Instance.new("Beam")
	beam.Attachment0, beam.Attachment1 = a0, a1
	beam.Width0, beam.Width1 = d.w0, d.w1
	beam.FaceCamera = true
	beam.Segments = 1
	beam.Color = ColorSequence.new(Color3.fromHex(d.kolor))
	beam.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, d.alfa),
		NumberSequenceKeypoint.new(0.7, d.alfa + (1 - d.alfa) * 0.4),
		NumberSequenceKeypoint.new(1, 1),
	})
	beam.LightEmission, beam.LightInfluence = 1, 0
	beam.Parent = a
end
-- pyłki-iskierki unoszące się w snopie
for _, d in ipairs(E.pylki) do
	local p = kotwica(d.n, v3(d.p))
	p.Size = v3(d.rozmiar)
	local pe = Instance.new("ParticleEmitter")
	pe.Texture = "rbxasset://textures/particles/sparkles_main.dds"
	pe.Rate = d.ile
	pe.Lifetime = NumberRange.new(d.zycie[1], d.zycie[2])
	pe.Speed = NumberRange.new(d.predkosc[1], d.predkosc[2])
	pe.EmissionDirection = Enum.NormalId.Top
	pe.SpreadAngle = Vector2.new(20, 20)
	pe.Size = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(0.2, d.wielkosc),
		NumberSequenceKeypoint.new(0.8, d.wielkosc * 0.7), NumberSequenceKeypoint.new(1, 0),
	})
	pe.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.2, 0.1),
		NumberSequenceKeypoint.new(0.8, 0.3), NumberSequenceKeypoint.new(1, 1),
	})
	pe.Color = ColorSequence.new(Color3.fromHex(d.kolor))
	pe.LightEmission, pe.LightInfluence = 1, 0
	pe.Rotation = NumberRange.new(0, 360)
	pe.RotSpeed = NumberRange.new(-40, 40)
	pe.Parent = p
end
ef.Parent = sala
'''

TEKSTURY = r"""
local sala = workspace:FindFirstChild("WyborKlasy")
local D = game:GetService("HttpService"):JSONDecode(TEKSTURY_JSON)
local R, MAT = D.reguly, D.materialy
local function pasuje(wzor, nazwa)
	if wzor == "*" then return true end
	if #wzor > 2 and wzor:sub(1, 1) == "*" and wzor:sub(-1) == "*" then
		return nazwa:lower():find(wzor:sub(2, -2):lower(), 1, true) ~= nil
	end
	if wzor:sub(1, 1) == "*" then return nazwa:sub(-(#wzor - 1)) == wzor:sub(2) end
	if wzor:sub(-1) == "*" then return nazwa:sub(1, #wzor - 1) == wzor:sub(1, -2) end
	return nazwa == wzor
end
local SCIANY = { all = Enum.NormalId:GetEnumItems(), top = { Enum.NormalId.Top } }
local function wymiar(p, f)
	local s = p.Size
	if f == Enum.NormalId.Front or f == Enum.NormalId.Back then return s.X, s.Y end
	if f == Enum.NormalId.Left or f == Enum.NormalId.Right then return s.Z, s.Y end
	return s.X, s.Z
end
local function zloty(c: Color3)
	return c.R > 0.7 and c.G > 0.5 and c.B < 0.45
end
local function naloz(p, r)
	for _, f in ipairs(SCIANY[r.sciany or "all"] or SCIANY.all) do
		local t = Instance.new("Texture")
		t.Name = "Tekstura"
		t.Texture = "rbxassetid://" .. r.id
		t.Face = f
		local u, v = wymiar(p, f)
		if r.studs == "czesc" then
			t.StudsPerTileU, t.StudsPerTileV = u, v
		else
			t.StudsPerTileU, t.StudsPerTileV = r.studs, r.studs
		end
		if r.barwa then t.Color3 = p.Color end
		t.Transparency = r.przezr or 0
		t.Parent = p
	end
end
local n, czesci, ogolne = 0, 0, 0
for _, p in ipairs(sala:GetDescendants()) do
	if p:IsA("BasePart") then
		for _, old in ipairs(p:GetChildren()) do
			if old:IsA("Texture") and old.Name == "Tekstura" then old:Destroy() end
		end
		-- kule (jabłka, gałki, płomienie) bez tekstur; bloki, kliny i walce — tak
		local kula = p:IsA("Part") and p.Shape == Enum.PartType.Ball
		local grupa = p.Parent and p.Parent.Name
		if p.Transparency < 1 and p.Material ~= Enum.Material.Neon then
			local trafiona = nil
			for _, r in ipairs(R) do
				local ok = (r.grupa == "*" or r.grupa == grupa) and pasuje(r.nazwa, p.Name) and r.id ~= nil
					and (not kula or r.kula == true)
				if ok and r.bez then
					for _, b in ipairs(r.bez) do
						if p.Name:find(b, 1, true) then ok = false end
					end
				end
				if ok then trafiona = r break end
			end
			if not trafiona and MAT and not kula then
				local m = p.Material.Name
				if m == "Metal" and zloty(p.Color) then m = "zloto" end
				local r = MAT[m]
				if r and r.id then trafiona = r ogolne += 1 end
			end
			if trafiona then
				naloz(p, trafiona)
				czesci += 1
			end
		end
	end
end
for _, p in ipairs(sala:GetDescendants()) do
	if p:IsA("Texture") and p.Name == "Tekstura" then n += 1 end
end
print("[WyborKlasy] tekstury:", czesci, "części (", ogolne, "z reguły materiałów ),", n, "ścian")
"""


def bronie_startowe_luau():
    """Bronie startowe (swiat/postacie/bronie_startowe.py) -> Luau budujący WyborKlasyModele.Weapon_<klasa>:
    Model z niewidzialnym Handle w (0, 0, 0) i częściami w układzie RightGripAttachment (te same bryły, z których
    Blender robi siatki; rozkład na części: swiat/postacie/biblioteka/roblox_klocki.py)."""
    sys.path.insert(0, str(ROOT))
    from swiat.postacie.bronie_startowe import akcesoria, PRZEDMIOTY
    from swiat.postacie.biblioteka.roblox_klocki import akcesoria_noszone
    klasa = {p["id"]: p["klasa"] for p in PRZEDMIOTY}

    class _P:
        pass
    dane = []
    for a in akcesoria():
        p = _P()
        p.zalozone = [(a, a.zaczep, (0, 0, 0), (0, 0, 0), True)]
        wyn, mat, _uwagi = akcesoria_noszone(p)
        dane.append({"klasa": klasa[a.id], "id": a.id, "materialy": mat, "czesci": wyn[0]["czesci"]})
    js = json.dumps(dane, ensure_ascii=False)
    assert "]==]" not in js
    return ("do local HS = game:GetService(\"HttpService\") "
            "for _, b in ipairs(HS:JSONDecode([==[" + js + "]==])) do "
            "local m = Instance.new(\"Model\") m.Name = \"Weapon_\" .. b.klasa m:SetAttribute(\"Bron\", b.id) "
            "local h = Instance.new(\"Part\") h.Name = \"Handle\" h.Size = Vector3.new(0.2, 0.2, 0.2) h.Transparency = 1 "
            "h.Anchored = true h.CanCollide = false h.CanTouch = false h.CanQuery = false h.CFrame = CFrame.new() h.Parent = m "
            "for i, c in ipairs(b.czesci) do local ks = c[1] local p "
            "if ks == 3 then p = Instance.new(\"WedgePart\") elseif ks == 4 then p = Instance.new(\"CornerWedgePart\") "
            "else p = Instance.new(\"Part\") p.Shape = if ks == 1 then Enum.PartType.Ball elseif ks == 2 then "
            "Enum.PartType.Cylinder else Enum.PartType.Block end "
            "p.Name = b.id .. \"_\" .. i p.Size = Vector3.new(c[8], c[9], c[10]) p.Color = Color3.fromHex(c[11]) "
            "local mt = b.materialy[c[12] + 1] p.Material = Enum.Material[mt[1]] p.Reflectance = mt[2] "
            "p.TopSurface = Enum.SurfaceType.Smooth p.BottomSurface = Enum.SurfaceType.Smooth "
            "p.Anchored = true p.CanCollide = false p.CanTouch = false p.CanQuery = false p.Massless = true "
            "if c[13] ~= \"\" then local sm = Instance.new(\"SpecialMesh\") sm.MeshType = Enum.MeshType[c[13]] sm.Parent = p end "
            "p.CFrame = CFrame.new(c[2], c[3], c[4]) * CFrame.fromOrientation(c[5], c[6], c[7]) p.Parent = m end "
            "m.PrimaryPart = h m.Parent = f end print(\"[WyborKlasy] bronie startowe: 3\") end")


def find(node, name):
    if node.get("Name") == name:
        return node
    for c in node.get("Children", []):
        r = find(c, name)
        if r:
            return r
    return None


def main():
    gui = json.loads((ROOT / "src/gui/ClassSelect.model.json").read_text(encoding="utf-8"))
    efekty = (ROOT / "swiat/wybor_klasy/efekty.json").read_text(encoding="utf-8")
    assert "]==]" not in efekty
    # tekstury z paczki: ID z manifestu; reguła bez wgranej tekstury jest pomijana
    man = json.loads((ROOT / "assets/manifest.json").read_text(encoding="utf-8"))["assets"]
    reguly = json.loads((ROOT / "swiat/wybor_klasy/tekstury.json").read_text(encoding="utf-8"))["reguly"]
    dane = json.loads((ROOT / "swiat/wybor_klasy/tekstury.json").read_text(encoding="utf-8"))
    materialy = dane.get("materialy", {})
    for r in list(reguly) + list(materialy.values()):
        r["id"] = man.get(r["tekstura"], {}).get("roblox_image")
    brak = sorted({r["tekstura"] for r in list(reguly) + list(materialy.values()) if not r["id"]})
    if brak:
        print("tekstury bez ID Roblox (pominięte):", ", ".join(brak))
    tekstury = json.dumps({"reguly": reguly, "materialy": materialy}, ensure_ascii=False)
    out = ['local CHS = game:GetService("ChangeHistoryService")',
           'local rec = CHS:TryBeginRecording("Ekran wyboru klasy")',
           "do", "local EFEKTY_JSON = [==[" + efekty + "]==]", SWIATLA, "end",
           "do", "local TEKSTURY_JSON = [==[" + tekstury + "]==]", TEKSTURY, "end",
           # kopie modeli bohaterów
           "do",
           'local RS = game:GetService("ReplicatedStorage")',
           'local f = RS:FindFirstChild("WyborKlasyModele")',
           'if f and not f:GetAttribute("Wygenerowane") then error("ReplicatedStorage.WyborKlasyModele nie jest nasz") end',
           'if f then f:Destroy() end',
           'f = Instance.new("Folder") f.Name = "WyborKlasyModele" f:SetAttribute("Wygenerowane", true)',
           'local src = workspace:WaitForChild("TestPostaci")']
    for cls, name in MODELE.items():
        out.append(f'do local m = src:FindFirstChild({json.dumps(name, ensure_ascii=False)}) assert(m, "brak modelu {name}") '
                   f'local c = m:Clone() c.Name = "{cls}" '
                   'for _, d in ipairs(c:GetDescendants()) do if d:IsA("Script") or d:IsA("LocalScript") then d:Destroy() end end '
                   'c.Parent = f end')
    # goły model do ekranu ras (D-079, D-071): pierwszy model w TestPostaci z „ciało”/„goł”/„baz” w nazwie
    # najpierw własny kontener z tools/studio/baza_rasy.py (ciało bazowe Rycerza z kodu Karola)
    out.append('do local baza = nil local wb = workspace:FindFirstChild("WyborKlasyBaza") '
               'if wb then baza = wb:FindFirstChildWhichIsA("Model") end '
               'if not baza then for _, m in ipairs(src:GetChildren()) do local n = m.Name:lower() '
               'if m:IsA("Model") and (n:find("ciało") or n:find("cialo") or n:find("goł") or n:find("gol") or n:find("baz")) then '
               'baza = m break end end end '
               'if baza then local c = baza:Clone() c.Name = "Base" '
               'for _, d in ipairs(c:GetDescendants()) do if d:IsA("Script") or d:IsA("LocalScript") then d:Destroy() end end '
               'c.Parent = f print("[WyborKlasy] goły model ras:", baza.Name) '
               'else warn("[WyborKlasy] brak gołego modelu w TestPostaci — ekran ras użyje modelu klasy") end end')
    # figury ras z wystawy Karola (Workspace/RasyProba, D-104) — tylko kopie, kontener Karola nietknięty
    rasy = {"Human": "czlowiek", "Demon": "demon", "DarkElf": "mroczny_elf", "Elf": "elf", "Orc": "ork",
            "Goblin": "goblin", "Demigod": "polbog"}
    out.append('do local rp = workspace:FindFirstChild("RasyProba") local n = 0 '
               'if rp then for id, nazwa in pairs(' + "{" + ", ".join('%s = "%s"' % kv for kv in rasy.items()) + "}" + ') do '
               'local m = rp:FindFirstChild(nazwa) if m and m:IsA("Model") then local c = m:Clone() c.Name = "Race_" .. id '
               'for _, d in ipairs(c:GetDescendants()) do if d:IsA("Script") or d:IsA("LocalScript") or d.Name == "Tabliczka" '
               'or d:IsA("BillboardGui") then d:Destroy() end end c.Parent = f n += 1 end end end '
               'print("[WyborKlasy] modele ras:", n) end')
    # bronie startowe klas w dłoni figury rasy (Paweł 18.11)
    out.append(bronie_startowe_luau())
    # Paweł 28.11: obrys sali ciemniejszy i wyraźniejszy, jak na podglądzie miasteczka low poly (2E2022 / 0,3; było
    # 3A2A20 / 0,5). Po pełnym wdrożeniu sali uruchom jeszcze tools/studio/sala_odswiez.luau (spokojniejsze drewno,
    # przyciemnione szczyty dachu — reguły szczegółowe tekstur tego nie obejmują).
    # miększa kreska sali (Paweł 24.11): obrysy sylwetek grup sali brązowe i w połowie przezroczyste (po przebudowie
    # sali studio_buduj.py --obrysy daje czarne — tu je zmiękczamy); postacie na podeście mają własny, wyraźny obrys
    out.append("do local k = workspace:FindFirstChild(\"WyborKlasy\") if k then for _, d in ipairs(k:GetDescendants()) do "
               "if d:IsA(\"Highlight\") then d.OutlineColor = Color3.fromHex(\"2E2022\") d.OutlineTransparency = 0.3 end end "
               "k:SetAttribute(\"KreskaMiekka\", true) end end")
    out += ["f.Parent = RS", "end",
            'local SG = game:GetService("StarterGui")',
            "do", build_luau(gui, "root", "ClassSelect"),
            'local old = SG:FindFirstChild("ClassSelect") if old then old:Destroy() end',
            "root.Parent = SG", "end"]
    if "--bez-skryptow" not in sys.argv:
        out += ["local function put(parent, name, class, src)",
                "\tlocal s = parent:FindFirstChild(name)",
                "\tif s and s.ClassName ~= class then s:Destroy() s = nil end",
                "\tif not s then s = Instance.new(class) s.Name = name s.Parent = parent end",
                "\ts.Source = src", "end"]
        for parent, name, cls, path in SCRIPTS:
            src = (ROOT / path).read_text(encoding="utf-8")
            assert "]===]" not in src
            out.append(f'put({parent}, "{name}", "{cls}", [===[{src}]===])')
    out += ["if rec then CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit) end",
            'return "ok: efekty sali, WyborKlasyModele, ClassSelect, skrypty"']
    dst = ROOT / "build/deploy_classselect.luau"
    dst.parent.mkdir(exist_ok=True)
    dst.write_text("\n".join(out), encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "tools/studio_mcp.py"), "luau", str(dst)], capture_output=True, text=True,
                       encoding="utf-8")
    print(r.stdout.strip() or r.stderr.strip())
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
