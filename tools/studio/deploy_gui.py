#!/usr/bin/env python3
"""Wdraża okna GUI z src/gui i ich skrypty klienta do otwartego Studio (miejsce z chmury, bez Rojo).

Użycie: python tools/studio/deploy_gui.py HUD EquipmentPanel [--skrypty HUDClient EquipmentPanelClient]
- każde okno = src/gui/<Nazwa>.model.json -> StarterGui.<Nazwa> (stare okno o tej nazwie jest podmieniane);
- --skrypty = LocalScripty z src/client/<Nazwa>.client.luau -> StarterPlayerScripts.Client.<Nazwa>;
- --moduly = ModuleScripty: src/client/<Nazwa>.luau -> StarterPlayerScripts.Client.<Nazwa>,
  src/shared/<Nazwa>.luau -> ReplicatedStorage.Shared.<Nazwa> (szuka najpierw w src/client).
Przed podmianą porównaj liczbę obiektów okna w Studio z wersją w gicie — Studio nie może mieć cudzych zmian.
Punkt historii „Wdrożenie GUI” (Ctrl+Z). Drzewko i ekran wyboru klasy mają własne skrypty wdrożenia w tym folderze.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/studio"))
from model_to_luau import build_luau  # noqa: E402

CLIENT = 'game:GetService("StarterPlayer").StarterPlayerScripts:WaitForChild("Client")'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("okna", nargs="*")
    ap.add_argument("--skrypty", nargs="*", default=[])
    ap.add_argument("--moduly", nargs="*", default=[])
    a = ap.parse_args()
    out = ['local CHS = game:GetService("ChangeHistoryService")',
           'local rec = CHS:TryBeginRecording("Wdrożenie GUI")',
           'local SG = game:GetService("StarterGui")']
    for name in a.okna:
        gui = json.loads((ROOT / f"src/gui/{name}.model.json").read_text(encoding="utf-8"))
        out += ["do", build_luau(gui, "root", name),
                f'local old = SG:FindFirstChild("{name}") if old then old:Destroy() end',
                "root.Parent = SG", "end"]
    out += ["local function put(parent, name, src, cls)",
            '\tcls = cls or "LocalScript"',
            "\tlocal s = parent:FindFirstChild(name)",
            "\tif s and s.ClassName ~= cls then s:Destroy() s = nil end",
            "\tif not s then s = Instance.new(cls) s.Name = name s.Parent = parent end",
            "\ts.Source = src", "end"]
    # moduły przed skryptami: LocalScript i tak czeka na moduł (WaitForChild), ale tak jest czytelniej
    for name in a.moduly:
        plik, rodzic = ROOT / f"src/client/{name}.luau", CLIENT
        if not plik.exists():
            plik, rodzic = ROOT / f"src/shared/{name}.luau", 'game:GetService("ReplicatedStorage"):WaitForChild("Shared")'
        src = plik.read_text(encoding="utf-8")
        assert "]===]" not in src
        out.append(f'put({rodzic}, "{name}", [===[{src}]===], "ModuleScript")')
    for name in a.skrypty:
        src = (ROOT / f"src/client/{name}.client.luau").read_text(encoding="utf-8")
        assert "]===]" not in src
        out.append(f'put({CLIENT}, "{name}", [===[{src}]===])')
    out += ["if rec then CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit) end",
            f'return "ok: {", ".join(a.okna + a.moduly + a.skrypty)}"']
    dst = ROOT / "build/deploy_gui.luau"
    dst.parent.mkdir(exist_ok=True)
    dst.write_text("\n".join(out), encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "tools/studio_mcp.py"), "luau", str(dst)], capture_output=True, text=True,
                       encoding="utf-8")
    print(r.stdout.strip() or r.stderr.strip())
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
