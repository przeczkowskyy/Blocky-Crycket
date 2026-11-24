#!/usr/bin/env python3
"""Wdraża skrypty serwera z src/server do otwartego Studio (miejsce z chmury, bez Rojo):
src/server/<Nazwa>.server.luau -> ServerScriptService.Server.<Nazwa> (stary o tej nazwie jest podmieniany).
Punkt historii „Wdrożenie serwera” (Ctrl+Z).

Użycie: python tools/studio/deploy_serwer.py MistrzGier JajkoKorowe
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    nazwy = sys.argv[1:]
    czesci = ['local CHS = game:GetService("ChangeHistoryService") local rec = CHS:TryBeginRecording("Wdrożenie serwera")',
              'local SSS = game:GetService("ServerScriptService") local srv = SSS:FindFirstChild("Server")',
              'if not srv then srv = Instance.new("Folder") srv.Name = "Server" srv.Parent = SSS end local out = {}']
    for n in nazwy:
        src = (ROOT / f"src/server/{n}.server.luau").read_text(encoding="utf-8")
        assert "]=====]" not in src
        czesci.append(f'do local old = srv:FindFirstChild("{n}") if old then old:Destroy() end '
                      f'local s = Instance.new("Script") s.Name = "{n}" s.Source = [=====[{src}]=====] s.Parent = srv '
                      f'table.insert(out, "{n}") end')
    czesci.append('if rec then CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit) end '
                  'return "ok: " .. table.concat(out, ", ")')
    dst = ROOT / "build" / "deploy_serwer.luau"
    dst.write_text("\n".join(czesci), encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "tools/studio_mcp.py"), "luau", str(dst)], capture_output=True,
                       text=True, encoding="utf-8")
    print(r.stdout.strip() or r.stderr.strip())


if __name__ == "__main__":
    main()
