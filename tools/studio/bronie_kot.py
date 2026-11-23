#!/usr/bin/env python3
"""Kocie wersje broni startowych (Paweł 24.11, D-145) -> ReplicatedStorage.WyborKlasyModele.Weapon_<klasa>_Kot.

Te same bryły co swiat/postacie/bronie_startowe.py, przerobione funkcją kocia(): krótsze wzdłuż rękojeści, grubsze
w poprzek (klockowe jak kostur Kota-Maga). Ekran wyboru (ClassSelectClient.holdWeapon) daje je figurom z atrybutem
BronDoGlowy (koty ras), zwykłe Weapon_<klasa> zostają dla ludzików. Budowa części jak w deploy_classselect.py.

Użycie: python -B tools/studio/bronie_kot.py [--dlugosc 0.62] [--grubosc 1.1]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dlugosc", type=float, default=None)
    ap.add_argument("--grubosc", type=float, default=None)
    a = ap.parse_args()
    from swiat.postacie import bronie_startowe as B
    from swiat.postacie.biblioteka.roblox_klocki import akcesoria_noszone
    klasa = {p["id"]: p["klasa"] for p in B.PRZEDMIOTY}
    dl = a.dlugosc if a.dlugosc is not None else B.KOT_DLUGOSC
    gr = a.grubosc if a.grubosc is not None else B.KOT_GRUBOSC

    class _P:
        pass
    dane = []
    for akc in B.akcesoria_kocie(dl, gr):
        p = _P()
        p.zalozone = [(akc, akc.zaczep, (0, 0, 0), (0, 0, 0), True)]
        wyn, mat, _uwagi = akcesoria_noszone(p)
        dane.append({"klasa": klasa[akc.id[:-4]], "id": akc.id, "materialy": mat, "czesci": wyn[0]["czesci"]})
    js = json.dumps(dane, ensure_ascii=False)
    assert "]==]" not in js
    luau = ("local CHS = game:GetService(\"ChangeHistoryService\") local rec = CHS:TryBeginRecording(\"Kocie bronie\") "
            "local f = game:GetService(\"ReplicatedStorage\"):WaitForChild(\"WyborKlasyModele\") "
            "local HS = game:GetService(\"HttpService\") local n = 0 "
            "for _, b in ipairs(HS:JSONDecode([==[" + js + "]==])) do "
            "local stary = f:FindFirstChild(\"Weapon_\" .. b.klasa .. \"_Kot\") if stary then stary:Destroy() end "
            "local m = Instance.new(\"Model\") m.Name = \"Weapon_\" .. b.klasa .. \"_Kot\" m:SetAttribute(\"Bron\", b.id) "
            "m:SetAttribute(\"Wygenerowane\", true) "
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
            "m.PrimaryPart = h m.Parent = f n += 1 end "
            "if rec then CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit) end "
            "return \"kocie bronie: \" .. n")
    dst = ROOT / "build" / "bronie_kot.luau"
    dst.parent.mkdir(exist_ok=True)
    dst.write_text(luau, encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "tools/studio_mcp.py"), "luau", str(dst)], capture_output=True,
                       text=True, encoding="utf-8")
    print(r.stdout.strip() or r.stderr.strip())
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
