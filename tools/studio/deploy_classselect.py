#!/usr/bin/env python3
"""Wdraża ekran wyboru klasy do otwartego Studio (miejsce z chmury, bez Rojo).

Kolejność: (0) python -B swiat/wybor_klasy/generuj.py  → czesci.json + efekty.json
           (1) sala z klocków: python tools/studio_buduj.py swiat/wybor_klasy/czesci.json --obrysy
           (2) ten skrypt: światła i efekty sali (z efekty.json), kopie modeli bohaterów, ScreenGui ClassSelect, skrypty.
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
    out = ['local CHS = game:GetService("ChangeHistoryService")',
           'local rec = CHS:TryBeginRecording("Ekran wyboru klasy")',
           "do", "local EFEKTY_JSON = [==[" + efekty + "]==]", SWIATLA, "end",
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
