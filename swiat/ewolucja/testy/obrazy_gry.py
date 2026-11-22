#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Obrazy strony gry z własnych modeli (bez wgrywania i bez zewnętrznego generowania): ikona 512 × 512 i dwie
miniatury 1920 × 1080, renderowane w Studio (tryb Edit) i opisane w PIL tylko tytułem „DRAGON LAIR EVOLUTION”.

    python -B swiat/ewolucja/testy/obrazy_gry.py --studio <id>

Pliki pełne POZA repo: <TEMP>/ewolucja_demo/ (jak filmy demo); podglądy: klatki/20_ikona.jpg, 21_miniatura1.jpg,
22_miniatura2.jpg. Scena powstaje na chwilę w Workspace/EwolucjaGra/Obrazy z dala od pól i jest usuwana; widok edytora
wraca na swoje miejsce. Okno Studio ma ok. 761 px szerokości — miniatury są powiększane (miękkie).
"""
import argparse
import io
import os
import sys
import tempfile

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
sys.path.append(os.path.join(REPO, "tools"))
from studio_mcp import StudioMCP  # noqa: E402

WSPOLNE = r'''
if game:GetService("RunService"):IsRunning() then return "STOP" end
local k = workspace.EwolucjaGra
local D = require(k.Moduly.DaneEwolucji)
local stary = k:FindFirstChild("Obrazy")
if stary then stary:Destroy() end
local f = Instance.new("Folder")
f.Name = "Obrazy"
f.Parent = k
local C = Vector3.new(D.pole.srodek[1] + 520, 0, D.pole.srodek[3])
local cam = workspace.CurrentCamera
if k:GetAttribute("KameraEdycji") == nil then k:SetAttribute("KameraEdycji", cam.CFrame) end
local function czesc(roz, cf, kolor, mat, ksztalt)
	local p = Instance.new("Part")
	p.Anchored = true
	p.Size = roz
	p.CFrame = cf
	p.Color = kolor
	p.Material = mat or Enum.Material.SmoothPlastic
	if ksztalt then p.Shape = ksztalt end
	p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
	p.Parent = f
	return p
end
local function smok(i, wys, cf, czarny)
	local F = D.formy[i]
	local m = k.Wzorce:FindFirstChild(F.wzorzec):Clone()
	m:PivotTo(CFrame.new())
	m:ScaleTo(wys / F.model_h)
	if czarny then
		for _, d in m:GetDescendants() do
			if d:IsA("BasePart") then
				d.Color = Color3.fromRGB(12, 10, 16)
				d.Material = Enum.Material.SmoothPlastic
			end
		end
	end
	m:PivotTo(cf)
	m.Parent = f
	return m
end
czesc(Vector3.new(400, 1, 400), CFrame.new(C + Vector3.new(0, -0.5, 0)), Color3.fromHex("86C062"), Enum.Material.Grass)
'''

IKONA = WSPOLNE + r'''
smok(8, 34, CFrame.new(C + Vector3.new(0, 0, 26)) * CFrame.Angles(0, math.rad(200), 0), true)
smok(1, 7.5, CFrame.new(C + Vector3.new(0, 0, -6)) * CFrame.Angles(0, math.rad(160), 0), false)
cam.FieldOfView = 50
cam.CFrame = CFrame.lookAt(C + Vector3.new(0, 7, -24), C + Vector3.new(0, 12, 8))
return "ok"
'''

MINIATURA1 = WSPOLNE + r'''
local x = 0
for i = 1, 8 do
	local wys = 2.2 * (1.42 ^ (i - 1))
	local F = D.formy[i]
	local dl = F.model_r * 2.9 * wys / F.model_h
	x += dl * 0.5 + 1
	smok(i, wys, CFrame.new(C + Vector3.new(-x, 0, 0)) * CFrame.Angles(0, math.rad(90), 0), i == 8)
	x += dl * 0.5 + 1
end
cam.FieldOfView = 40
cam.CFrame = CFrame.lookAt(C + Vector3.new(x * 0.05, x * 0.17, -x * 1.08), C + Vector3.new(x * 0.05, x * 0.08, 0))
return tostring(x)
'''

MINIATURA2 = WSPOLNE + r'''
czesc(Vector3.new(0.4, 40, 40), CFrame.new(C + Vector3.new(0, 0.2, 0)) * CFrame.Angles(0, 0, math.pi / 2), Color3.fromHex("C8A070"), Enum.Material.WoodPlanks, Enum.PartType.Cylinder)
-- skarb: kopiec złotych monet i kul
local los = Random.new(4)
for i = 1, 140 do
	local a, r = los:NextNumber() * math.pi * 2, math.sqrt(los:NextNumber()) * 9
	local h = (1 - r / 9) * 5
	local s = 1 + los:NextNumber() * 1.4
	local p = czesc(Vector3.new(0.35, s * 1.6, s * 1.6), CFrame.new(C + Vector3.new(math.sin(a) * r, h * los:NextNumber() + 0.4, math.cos(a) * r))
		* CFrame.Angles(los:NextNumber() * 3, los:NextNumber() * 3, los:NextNumber() * 3), Color3.fromHex(if i % 3 == 0 then "FFE14D" else "FFC83D"),
		Enum.Material.Neon, Enum.PartType.Cylinder)
	if i % 4 == 0 then p.Shape = Enum.PartType.Ball end
end
local m = smok(7, 13, CFrame.new(C + Vector3.new(0, 4.2, 0)) * CFrame.Angles(0, math.rad(215), 0), false)
-- korona nad głową smoka
local _, roz = m:GetBoundingBox()
local glowa = m:FindFirstChild("Glowa")
local kc = (glowa and glowa.Position or (C + Vector3.new(0, roz.Y + 4, 0))) + Vector3.new(0, 2.2, 0)
czesc(Vector3.new(3.2, 0.8, 3.2), CFrame.new(kc), Color3.fromHex("FFC83D"), Enum.Material.Neon)
for i = 0, 4 do
	local a = i * math.pi * 2 / 5
	czesc(Vector3.new(0.7, 1.6, 0.7), CFrame.new(kc + Vector3.new(math.cos(a) * 1.25, 1, math.sin(a) * 1.25)), Color3.fromHex("FFC83D"), Enum.Material.Neon)
end
for i = 1, 6 do
	local a = math.rad(150 + i * 12)
	local p = C + Vector3.new(math.sin(a) * 15, 0, math.cos(a) * 15)
	czesc(Vector3.new(1.2, 3.2, 3.2), CFrame.new(p + Vector3.new(0, 0.6, 0)) * CFrame.Angles(0, 0, math.pi / 2), Color3.fromHex("B8B0C8"), Enum.Material.Slate, Enum.PartType.Cylinder)
	smok(i, 2.6 + i * 0.25, CFrame.new(p + Vector3.new(0, 1.2, 0)) * CFrame.Angles(0, a + math.pi, 0), false)
end
cam.FieldOfView = 45
cam.CFrame = CFrame.lookAt(C + Vector3.new(-6, 16, -34), C + Vector3.new(0, 6, 0))
return "ok"
'''

SPRZATANIE = r'''
local k = workspace.EwolucjaGra
local f = k:FindFirstChild("Obrazy")
if f then f:Destroy() end
local cf = k:GetAttribute("KameraEdycji")
if typeof(cf) == "CFrame" then workspace.CurrentCamera.CFrame = cf end
workspace.CurrentCamera.FieldOfView = 70
k:SetAttribute("KameraEdycji", nil)
return "ok"
'''


def czcionka(px):
    from PIL import ImageFont
    for n in ("ariblk.ttf", "impact.ttf", "arialbd.ttf"):
        try:
            return ImageFont.truetype(n, px)
        except OSError:
            continue
    return ImageFont.load_default()


def napis(img, tekst, xy, px, kolor=(255, 200, 61), obrys=(27, 20, 36), srodek=True):
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    f = czcionka(px)
    b = d.textbbox((0, 0), tekst, font=f, stroke_width=max(2, px // 12))
    x, y = xy
    if srodek:
        x -= (b[2] - b[0]) // 2
    d.text((x, y), tekst, font=f, fill=kolor, stroke_width=max(2, px // 12), stroke_fill=obrys)


def kadr(img, w, h):
    """Kadr o proporcjach w:h ze środka, potem skalowanie."""
    from PIL import Image, ImageFilter
    W, H = img.size
    if W / H > w / h:
        nw = int(H * w / h)
        img = img.crop(((W - nw) // 2, 0, (W - nw) // 2 + nw, H))
    else:
        nh = int(W * h / w)
        img = img.crop((0, (H - nh) // 2, W, (H - nh) // 2 + nh))
    img = img.resize((w, h), Image.LANCZOS)
    return img.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2)) if w > 1000 else img


def main():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio", required=True)
    a = ap.parse_args()
    from PIL import Image
    wyj = os.path.join(tempfile.gettempdir(), "ewolucja_demo")
    os.makedirs(wyj, exist_ok=True)
    klatki = os.path.join(PAKIET, "klatki")
    with StudioMCP(timeout=180) as s:
        if "Current Studio Mode: Edit" not in s.call("get_studio_state", {"studio_id": a.studio})["text"]:
            raise SystemExit("Studio nie jest w trybie Edit")

        def zrzut(kod):
            r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": a.studio}, timeout=180)
            if r["is_error"] or (r["text"] or "").startswith("STOP"):
                raise SystemExit("scena: " + (r["text"] or "")[:300])
            r = s.call("screen_capture", {"capture_id": "obraz", "studio_id": a.studio}, timeout=120)
            return Image.open(io.BytesIO(r["images"][0])).convert("RGB")
        try:
            ik = kadr(zrzut(IKONA), 512, 512)
            napis(ik, "?", (256, 40), 230, (255, 225, 77))
            m1 = kadr(zrzut(MINIATURA1), 1920, 1080)
            napis(m1, "DRAGON LAIR EVOLUTION", (960, 40), 120)
            napis(m1, "?", (1690, 330), 330, (255, 225, 77))
            m2 = kadr(zrzut(MINIATURA2), 1920, 1080)
            napis(m2, "DRAGON LAIR EVOLUTION", (960, 40), 120)
        finally:
            s.call("execute_luau", {"code": SPRZATANIE, "datamodel_type": "Edit", "studio_id": a.studio})
    for img, pelna, pod, rozm in ((ik, "ikona_512.png", "20_ikona.jpg", (512, 512)), (m1, "miniatura1_1920.png", "21_miniatura1.jpg", (960, 540)),
                                  (m2, "miniatura2_1920.png", "22_miniatura2.jpg", (960, 540))):
        img.save(os.path.join(wyj, pelna))
        img.resize(rozm).save(os.path.join(klatki, pod), quality=86)
        print("zapisano", pelna, "+ klatki/" + pod)


if __name__ == "__main__":
    main()
