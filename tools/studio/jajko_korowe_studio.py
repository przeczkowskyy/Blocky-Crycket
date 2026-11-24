#!/usr/bin/env python3
"""Jajko korowe w Studio (Paweł 24.11): model z swiat/postacie/jajko_korowe.py zbudowany narzędziem Karola
swiat/postacie/roblox_postac.py (części Roblox z klipami z Blendera) we WŁASNYM kontenerze
Workspace/JajkoKorowePodglad (atrybut Wygenerowane), na wolnym bruku placu obok kotów ras. W Play skrypt
PokazAnimacji gra po kolei spoczynek, napięcie i pęknięcie. Słup światła (kość Promien) Roblox pokazuje zawsze
(skali z klipu nie przenosi) — w grze zapala go klient przy wykluciu.

Po budowie nakłada kreskówkowe tekstury z sali wyboru (ten sam styl Glossy Ink, już w Roblox — assets/manifest.json):
drewno (CsTex05) na płyty kory, odłamki i korzenie, liście (CsProp09) na mech; tekstura zabarwiona kolorem części
(Paweł 24.11: „nałożyć tekstury nadające mu kreskówkowy wygląd”).

Użycie: python -B tools/studio/jajko_korowe_studio.py [--usun]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "swiat", "postacie"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import roblox_postac as R  # noqa: E402

R.KONTENER = "JajkoKorowePodglad"
R.PRZESUNIECIE = (0.0, 0.0)
R.ROZMIESZCZENIE = {"jajko_korowe": {"poz": (983.0, -652.0), "patrz": (983.0, -666.0), "nazwa": "Jajko korowe"}}

def tekstury():
    import json
    import subprocess
    man = json.loads(open(os.path.join(ROOT, "assets", "manifest.json"), encoding="utf-8").read())["assets"]
    drewno = man["CsTex05"]["roblox_image"]
    liscie = man["CsProp09"]["roblox_image"]
    luau = (
        'local CHS = game:GetService("ChangeHistoryService") local rec = CHS:TryBeginRecording("Jajko: tekstury") '
        'local m = workspace.JajkoKorowePodglad:FindFirstChild("Jajko korowe") local n = 0 '
        'local REGULY = { {"^Kora", "%s", 1.2}, {"^Odlamek kora", "%s", 1.2}, {"^Korzen", "%s", 1.5}, '
        '{"^Mech korzenia", "%s", 1.2} } '
        'for _, p in ipairs(m:GetDescendants()) do if p:IsA("BasePart") and p.Shape == Enum.PartType.Block then '
        'for _, r in ipairs(REGULY) do if p.Name:find(r[1]) then '
        'for _, f in ipairs(Enum.NormalId:GetEnumItems()) do local t = Instance.new("Texture") t.Name = "TeksturaKreskowka" '
        't.Texture = "rbxassetid://" .. r[2] t.Face = f t.StudsPerTileU = r[3] t.StudsPerTileV = r[3] '
        't.Color3 = p.Color:Lerp(Color3.new(1, 1, 1), 0.25) t.Parent = p end n += 1 break end end end end '
        'if rec then CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit) end return "tekstury: " .. n'
    ) % (drewno, drewno, drewno, liscie)
    dst = os.path.join(ROOT, "build", "jajko_korowe_tekstury.luau")
    open(dst, "w", encoding="utf-8").write(luau)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "studio_mcp.py"), "luau", dst], capture_output=True,
                       text=True, encoding="utf-8")
    print(r.stdout.strip() or r.stderr.strip())


if __name__ == "__main__":
    reszta = [a for a in sys.argv[1:] if a == "--usun"]
    sys.argv = [sys.argv[0], "--tylko", "jajko_korowe", "--wyj", os.path.join(ROOT, "build", "jajko_korowe")] + reszta
    R.main()
    if "--usun" not in reszta:
        tekstury()
