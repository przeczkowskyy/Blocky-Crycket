#!/usr/bin/env python3
"""Wdraża drzewko umiejętności do otwartego Studio (miejsce z chmury, bez Rojo):
ScreenGui SkillTree, przycisk drzewa w oknie ekwipunku i skrypty z plików repozytorium.

Użycie: python tools/studio/deploy_skilltree.py  (zapisuje Luau do build/ i uruchamia przez tools/studio_mcp.py)
Podmienia tylko własne obiekty o tych nazwach; punkt historii „Drzewko umiejętności” (Ctrl+Z).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/studio"))
from model_to_luau import build_luau  # noqa: E402

SCRIPTS = [  # (rodzic w Studio, nazwa, klasa, plik)
    ('game:GetService("ReplicatedStorage"):WaitForChild("Shared")', "SkillTreeData", "ModuleScript", "src/shared/SkillTreeData.luau"),
    ('game:GetService("ReplicatedStorage"):WaitForChild("Shared")', "SkillTreeIcons", "ModuleScript", "src/shared/SkillTreeIcons.luau"),
    ('game:GetService("ServerScriptService"):WaitForChild("Server")', "SkillTree", "Script", "src/server/SkillTree.server.luau"),
    ('game:GetService("StarterPlayer").StarterPlayerScripts:WaitForChild("Client")', "SkillTreeClient", "LocalScript",
     "src/client/SkillTreeClient.client.luau"),
    # testowe 1000 Diamentów na start (TEST, Paweł 15.11)
    ('game:GetService("ServerScriptService"):WaitForChild("Server")', "PlayerStatsDefaults", "Script",
     "src/server/PlayerStatsDefaults.server.luau"),
]


def find(node, name):
    if node.get("Name") == name:
        return node
    for c in node.get("Children", []):
        r = find(c, name)
        if r:
            return r
    return None


def main():
    gui = json.loads((ROOT / "src/gui/SkillTree.model.json").read_text(encoding="utf-8"))
    eq = json.loads((ROOT / "src/gui/EquipmentPanel.model.json").read_text(encoding="utf-8"))
    btn = find(eq, "SkillTreeButton")
    out = ['local CHS = game:GetService("ChangeHistoryService")',
           'local rec = CHS:TryBeginRecording("Drzewko umiejętności")',
           'local SG = game:GetService("StarterGui")',
           "do", build_luau(gui, "root", "SkillTree"),
           'local old = SG:FindFirstChild("SkillTree") if old then old:Destroy() end',
           "root.Parent = SG", "end",
           "do", build_luau(btn, "root"),
           'local char = SG:WaitForChild("EquipmentPanel"):WaitForChild("Panel"):WaitForChild("Character")',
           'local old = char:FindFirstChild("SkillTreeButton") if old then old:Destroy() end',
           "root.Parent = char", "end",
           "local function put(parent, name, class, src)",
           "\tlocal s = parent:FindFirstChild(name)",
           "\tif s and s.ClassName ~= class then s:Destroy() s = nil end",
           "\tif not s then s = Instance.new(class) s.Name = name s.Parent = parent end",
           "\ts.Source = src", "end"]
    for parent, name, cls, path in SCRIPTS:
        src = (ROOT / path).read_text(encoding="utf-8")
        assert "]===]" not in src
        out.append(f'put({parent}, "{name}", "{cls}", [===[{src}]===])')
    out += ["if rec then CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit) end",
            'return "ok: SkillTree, SkillTreeButton, skrypty"']
    dst = ROOT / "build/deploy_skilltree.luau"
    dst.parent.mkdir(exist_ok=True)
    dst.write_text("\n".join(out), encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "tools/studio_mcp.py"), "luau", str(dst)], capture_output=True, text=True,
                       encoding="utf-8")
    print(r.stdout.strip() or r.stderr.strip())
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
