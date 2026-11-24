#!/usr/bin/env python3
"""Jajko korowe w Studio (Paweł 24.11): model z swiat/postacie/jajko_korowe.py zbudowany narzędziem Karola
swiat/postacie/roblox_postac.py (części Roblox z klipami z Blendera) we WŁASNYM kontenerze
Workspace/JajkoKorowePodglad (atrybut Wygenerowane), na wolnym bruku placu obok kotów ras. W Play skrypt
PokazAnimacji gra po kolei spoczynek, napięcie i pęknięcie. Słup światła (kość Promien) Roblox pokazuje zawsze
(skali z klipu nie przenosi) — w grze zapala go klient przy wykluciu.

Po budowie nakłada własne tekstury jajka (Paweł 24.11: „wygeneruj nowe stricte pod to jajko”, z jego referencji):
kora, korzeń, mech i skorupa (assets/processed/JajkoTekstury, ID w assets/manifest.json). Samo nałożenie:
python -B -c "import tools.studio.jajko_korowe_studio as J; J.tekstury()" albo pełna przebudowa tym skryptem.

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
    """Tekstury jajka z jego referencji (assets/processed/JajkoTekstury, tools/jajko_tekstury.py): kora na płyty kory
    i odłamki, korzeń na korzenie, mech na mech, skorupa na elipsoidy skorupy (kule też przyjmują Texture)."""
    import json
    import subprocess
    man = json.loads(open(os.path.join(ROOT, "assets", "manifest.json"), encoding="utf-8").read())["assets"]
    i = {n: man[n]["roblox_image"] for n in ("JajkoKora", "JajkoKorzen", "JajkoMech", "JajkoSkorupa")}
    luau = (
        'local CHS = game:GetService("ChangeHistoryService") local rec = CHS:TryBeginRecording("Jajko: tekstury") '
        'local m = workspace.JajkoKorowePodglad:FindFirstChild("Jajko korowe") local n = 0 '
        'for _, p in ipairs(m:GetDescendants()) do if p:IsA("Texture") and p.Name == "TeksturaKreskowka" then p:Destroy() end end '
        'local REGULY = { {"^Kora", "%(kora)s", 1.0}, {"^Odlamek kora", "%(kora)s", 1.0}, {"^Korzen", "%(korzen)s", 1.2}, '
        '{"^Mech", "%(mech)s", 0.8}, {"^Skorupka", "%(skorupa)s", 2.0}, {"^Czubek$", "%(skorupa)s", 2.0} } '
        'for _, p in ipairs(m:GetDescendants()) do if p:IsA("BasePart") and p.Material ~= Enum.Material.Neon then '
        'for _, r in ipairs(REGULY) do if p.Name:find(r[1]) then '
        'for _, f in ipairs(Enum.NormalId:GetEnumItems()) do local t = Instance.new("Texture") t.Name = "TeksturaKreskowka" '
        't.Texture = "rbxassetid://" .. r[2] t.Face = f t.StudsPerTileU = r[3] t.StudsPerTileV = r[3] '
        't.Color3 = Color3.new(1, 1, 1) t.Parent = p end n += 1 break end end end end '
        'if rec then CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit) end return "tekstury: " .. n'
    ) % {"kora": i["JajkoKora"], "korzen": i["JajkoKorzen"], "mech": i["JajkoMech"], "skorupa": i["JajkoSkorupa"]}
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
