#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teleport przez chmury i makieta pasa krain — budowa kontenera Workspace/TeleportChmury w Roblox Studio.

    python -B swiat/teleport_chmury/zbuduj.py --sucho     # bez Studio: dane, Dane.luau, makieta, kontrola Luau, plan
    python -B swiat/teleport_chmury/zbuduj.py             # buduje / odbudowuje kontener (Studio w trybie Edit)
    python -B swiat/teleport_chmury/zbuduj.py --skrypty   # tylko Dane + dwa skrypty do istniejącego kontenera
    python -B swiat/teleport_chmury/zbuduj.py --usun      # usuwa Workspace/TeleportChmury
    python -B swiat/teleport_chmury/zbuduj.py --studio <studio_id>   # gdy otwartych jest kilka okien Studio

Co powstaje (tylko w Workspace/TeleportChmury z atrybutem Wygenerowane = true):
  Dane               ModuleScript — wygenerowany z krainy.json (zrodla/Dane.luau, nie edytować ręcznie)
  SerwerTeleportu    Script, RunContext = Server (zrodla/SerwerTeleportu.server.luau)
  KlientTeleportu    Script, RunContext = Client (zrodla/KlientTeleportu.client.luau)
  Zdalne/Teleport    RemoteFunction (klient → serwer: "stan", "przenies")
  Otworz             BindableEvent — uchwyt dla przycisku TELEPORT w HUD (klient: Otworz:Fire())
  Sygnaly/SterowanieSerwera, Sygnaly/SterowanieKlienta   BindableFunction — haczyki testowe
  Makieta            Model (ModelStreamingMode = Persistent, bez kolizji): Krainy/<id> (płytka, akcent, tabliczka,
                     kłódka), Chmury (morze i kłęby), Wskaznik (złota strzałka), Pinezka (chorągiewka „tu jesteś”)

Zasady (wspólne miejsce Team Create, PlaceId gry): okno wybiera swiat/test_walki_roblox/cel_studio.py; każdy
wysyłany kod sprawdza game.PlaceId i tryb Edit; ruszany jest tylko własny kontener (cudzy obiekt o tej nazwie
bez atrybutu → STOP); punkty historii przed i po; nic nie jest zapisywane ani publikowane; oświetlenia miejsca
budowa tylko CZYTA (kierunek słońca → obrót makiety). --sucho nie importuje studio_mcp ani cel_studio.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if TU not in sys.path:
    sys.path.insert(0, TU)
import makieta  # noqa: E402

DANE_JSON = os.path.join(TU, "krainy.json")
PLAN_PASA = os.path.join(REPO, "swiat", "las_pas", "krotki", "plan_pasa.json")   # krótki pas gry (D-096)
ZRODLA = os.path.join(TU, "zrodla")
DANE_LUAU = os.path.join(ZRODLA, "Dane.luau")
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
LIMIT_ZRODLA = 199000
PARTIA = 110  # części na jedno wywołanie execute_luau

SKRYPTY = [  # (plik, klasa, nazwa w kontenerze, RunContext)
    ("Dane.luau", "ModuleScript", "Dane", None),
    ("SerwerTeleportu.server.luau", "Script", "SerwerTeleportu", "Server"),
    ("KlientTeleportu.client.luau", "Script", "KlientTeleportu", "Client"),
]

NAGLOWEK_MIEJSCA = ('if game.PlaceId ~= __MIEJSCE__ then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end\n'
                    'if game:GetService("RunService"):IsRunning() then return "STOP: Studio jest w trybie Play — buduję tylko w trybie Edit" end\n')

START = r'''
local CH = game:GetService("ChangeHistoryService")
local nazwa = "__KONTENER__"
local stare = {}
for _, d in workspace:GetChildren() do
	if d.Name == nazwa then
		if d:GetAttribute("Wygenerowane") ~= true then
			return "STOP: w Workspace jest obiekt '" .. nazwa .. "' bez atrybutu Wygenerowane — nie ruszam cudzej pracy"
		end
		table.insert(stare, d)
	end
end
if __USUN__ then
	if #stare == 0 then
		return "USUNIETO (kontenera nie było)"
	end
	CH:SetWaypoint(nazwa .. ": przed usunięciem")
	for _, d in stare do d:Destroy() end
	CH:SetWaypoint(nazwa .. ": usunięto")
	return "USUNIETO"
end
CH:SetWaypoint(nazwa .. ": przed budową")
for _, d in stare do d:Destroy() end
local f = Instance.new("Folder")
f.Name = nazwa
f:SetAttribute("Wygenerowane", true)
f:SetAttribute("Zrodlo", "swiat/teleport_chmury/zbuduj.py")
f:SetAttribute("Zbudowano", "__CZAS__")
f:SetAttribute("Skrot", "__SKROT__")
local function nowy(klasa, n, rodzic)
	local o = Instance.new(klasa)
	o.Name = n
	o.Parent = rodzic
	return o
end
nowy("RemoteFunction", "Teleport", nowy("Folder", "Zdalne", f))
local sy = nowy("Folder", "Sygnaly", f)
nowy("BindableFunction", "SterowanieSerwera", sy)
nowy("BindableFunction", "SterowanieKlienta", sy)
nowy("BindableEvent", "Otworz", f)
-- obrót makiety ze słońca miejsca (tylko odczyt): słońce zza kamery, przesunięte o __OBROT__°
local slonce = game:GetService("Lighting"):GetSunDirection()
local poziom = Vector3.new(slonce.X, 0, slonce.Z)
local yaw = if poziom.Magnitude > 1e-3 then math.atan2(poziom.X, poziom.Z) else 0
yaw += math.rad(__OBROT__)
local P = CFrame.new(__SRODEK__) * CFrame.Angles(0, yaw, 0)
local m = Instance.new("Model")
m.Name = "Makieta"
m.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
m:SetAttribute("Pivot", P)
m:SetAttribute("LiczbaCzesci", __LICZBA__)
m:SetAttribute("ObrotStopnie", math.deg(yaw))
nowy("Folder", "Krainy", m)
m.Parent = f
f.Parent = workspace
return string.format("OK (obrót makiety %.1f°, słońce %.2f %.2f %.2f)", math.deg(yaw), slonce.X, slonce.Y, slonce.Z)
'''

CZESCI = r'''
local f = workspace:FindFirstChild("__KONTENER__")
local m = f and f:FindFirstChild("Makieta")
if not m or f:GetAttribute("Wygenerowane") ~= true then return "STOP: brak kontenera albo makiety" end
local P = m:GetAttribute("Pivot")
local KOLOR_NAPISU = Color3.fromHex("__NAPIS__")
local TUSZ = Color3.fromHex("__TUSZ__")
local dane = {
__WIERSZE__
}
local function grupa(sciezka)
	local r = m
	for _, n in string.split(sciezka, "/") do
		local d = r:FindFirstChild(n)
		if not d then
			d = Instance.new(if n == "Krainy" then "Folder" else "Model")
			d.Name = n
			d.Parent = r
		end
		r = d
	end
	return r
end
local n = 0
for _, w in dane do
	local p = Instance.new(w[2])
	p.Name = w[1]
	if w[2] == "Part" then p.Shape = Enum.PartType[w[3]] end
	p.Size = Vector3.new(w[4], w[5], w[6])
	p.CFrame = P * CFrame.new(w[7], w[8], w[9], w[10], w[11], w[12], w[13], w[14], w[15], w[16], w[17], w[18])
	p.Color = Color3.fromHex(w[19])
	p.Material = Enum.Material[w[20]]
	p.Transparency = w[21]
	p.Anchored = true
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = w[23] ~= "chmura"
	p.CastShadow = w[24]
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	if string.match(w[22], "^Krainy/") then
		if w[23] == "klodka" then
			p:SetAttribute("Klodka", true)
		else
			p:SetAttribute("KolorJasny", p.Color)
			if w[20] == "Neon" then p:SetAttribute("Neon", true) end
		end
	end
	if w[23] == "tabliczka" then
		local sg = Instance.new("SurfaceGui")
		sg.Name = "Tablica"
		sg.Face = Enum.NormalId.Front
		sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
		sg.PixelsPerStud = 12
		sg.LightInfluence = 0.15
		sg.MaxDistance = 5000
		local t = Instance.new("TextLabel")
		t.Name = "Napis"
		t.BackgroundTransparency = 1
		t.Size = UDim2.fromScale(0.94, 0.84)
		t.Position = UDim2.fromScale(0.03, 0.08)
		t.Font = Enum.Font.FredokaOne
		t.TextScaled = true
		t.Text = w[25]
		t.TextColor3 = KOLOR_NAPISU
		local s = Instance.new("UIStroke")
		s.Thickness = 3
		s.Color = TUSZ
		s.Parent = t
		t.Parent = sg
		sg.Parent = p
	end
	p.Parent = grupa(w[22])
	n += 1
end
return "OK " .. n
'''

KONIEC = r'''
local f = workspace:FindFirstChild("__KONTENER__")
local m = f and f:FindFirstChild("Makieta")
if not m then return "STOP: brak makiety" end
local P = m:GetAttribute("Pivot")
local NJ, NS = __JASNOSC__, __NASYCENIE__
local OTWARTY, ZAMKNIETY = Color3.fromHex("__NAPIS__"), Color3.fromHex("__NAPIS_Z__")
for i, k in { __KRAINY__ } do
	local model = m.Krainy:FindFirstChild(k[1])
	if not model then return "STOP: brak krainy " .. k[1] end
	model:SetAttribute("Kraina", k[1])
	model:SetAttribute("Indeks", i)
	model.WorldPivot = P * CFrame.new(k[2], 0, 0)
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") then
			if d:GetAttribute("Klodka") then
				d.Transparency = if k[3] then 0 else 1
			elseif k[3] and d:GetAttribute("KolorJasny") then
				local h, s, v = d.Color:ToHSV()
				d.Color = Color3.fromHSV(h, s * NS, v * NJ)
				if d:GetAttribute("Neon") then d.Material = Enum.Material.SmoothPlastic end
			end
		elseif d:IsA("TextLabel") and d.Name == "Napis" then
			d.TextColor3 = if k[3] then ZAMKNIETY else OTWARTY
		end
	end
end
local wsk = m:FindFirstChild("Wskaznik")
if wsk then wsk.WorldPivot = P * CFrame.new(__WSK__) end
local pin = m:FindFirstChild("Pinezka")
if pin then pin.WorldPivot = P * CFrame.new(__PIN__) end
m.WorldPivot = P
local razem, czesci, skrypty = 0, 0, 0
for _, d in f:GetDescendants() do
	razem += 1
	if d:IsA("BasePart") then czesci += 1 end
	if d:IsA("LuaSourceContainer") then skrypty += 1 end
end
if czesci ~= m:GetAttribute("LiczbaCzesci") then
	return "STOP: części " .. czesci .. " zamiast " .. tostring(m:GetAttribute("LiczbaCzesci"))
end
game:GetService("ChangeHistoryService"):SetWaypoint("__KONTENER__: zbudowano")
return string.format("instancji: %d, części: %d, skryptów: %d, Skrot = %s", razem, czesci, skrypty, tostring(f:GetAttribute("Skrot")))
'''

SKRYPT = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then return "STOP: brak kontenera" end
local stary = f:FindFirstChild("__NAZWA__")
if stary then stary:Destroy() end
local s = Instance.new("__KLASA__")
s.Name = "__NAZWA__"
__RUNCONTEXT__
s.Source = __ZRODLO__
s.Parent = f
return "OK " .. s:GetFullName() .. " (" .. #s.Source .. " znaków)"
'''


# ------------------------------------------------------------------ pomocnicze
def wczytaj(sciezka):
    with open(sciezka, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def dlugi_napis(tekst):
    poziom = 3
    while ("]" + "=" * poziom + "]") in tekst or ("[" + "=" * poziom + "[") in tekst:
        poziom += 1
    return "[" + "=" * poziom + "[\n" + tekst + "]" + "=" * poziom + "]"


def luau_napis(s):
    return json.dumps(s, ensure_ascii=False)


SLOWA = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in", "local", "nil", "not",
         "or", "repeat", "return", "then", "true", "until", "while", "continue", "type", "export"}


def luau_wartosc(v, wc=1):
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "nil"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return repr(round(v, 6))
    if isinstance(v, str):
        return luau_napis(v)
    if isinstance(v, list):
        return "{ " + ", ".join(luau_wartosc(x, wc + 1) for x in v) + " }"
    if isinstance(v, dict):
        linie = []
        for k, x in v.items():
            if k == "opis":
                continue
            klucz = k if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", k) and k not in SLOWA else "[%s]" % luau_napis(k)
            linie.append("\t" * wc + "%s = %s," % (klucz, luau_wartosc(x, wc + 1)))
        return "{\n" + "\n".join(linie) + "\n" + "\t" * (wc - 1) + "}"
    raise TypeError(type(v))


def skrot_danych(dane):
    return hashlib.sha1(json.dumps(dane, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]


# ------------------------------------------------------------------ kontrola danych
def sprawdz_dane(dane):
    bledy, uwagi = [], []
    ids = [k["id"] for k in dane["krainy"]]
    if len(ids) != len(set(ids)):
        bledy.append("powtórzone id krain")
    if ids[:2] != ["miasteczko", "las"]:
        bledy.append("kolejność: pierwsze muszą być miasteczko i las")
    for k in dane["krainy"]:
        for pole in ("kolor_gruntu", "kolor_podloza", "kolor_drogi"):
            if not re.match(r"^[0-9A-Fa-f]{6}$", k[pole]):
                bledy.append("%s.%s: zły kolor %r" % (k["id"], pole, k[pole]))
        if k["id"] not in makieta.AKCENTY:
            bledy.append("%s: brak akcentu w makieta.py" % k["id"])
        if not k["przybycie"]:
            bledy.append("%s: brak punktu przybycia" % k["id"])
        for p in k["przybycie"]:
            if not any(x in p for x in ("atrybut", "xyz", "xz", "uchwyt")):
                bledy.append("%s: wpis przybycia bez atrybut/xyz/xz/uchwyt: %r" % (k["id"], p))
            if "uchwyt" in p and not (p.get("gdy_jest") and p.get("punkt")
                                      and 0 <= p.get("przelot_po_s", 0) <= 10):
                bledy.append("%s: uchwyt bez gdy_jest/punkt albo przelot_po_s poza 0–10: %r" % (k["id"], p))
            if "xz" in p and "patrz_xz" not in p:
                bledy.append("%s: xz bez patrz_xz" % k["id"])
            if "xyz" in p and "patrz_xyz" not in p:
                bledy.append("%s: xyz bez patrz_xyz" % k["id"])
        if len(k["napis"]) > 12:
            uwagi.append("%s: napis „%s” ma %d znaków (na telefonie mało miejsca)" % (k["id"], k["napis"], len(k["napis"])))
    if not any(k["od_poczatku"] for k in dane["krainy"]):
        bledy.append("żadna kraina nie jest otwarta od początku")
    cz = dane["czasy"]
    jedna = cz["wejscie_s"] + cz["wylonienie_s"] + cz["zanurzenie_s"] + cz["opadanie_s"] + cz["biel_min_s"]
    if not 3.0 <= jedna <= 5.5:
        uwagi.append("przejście bez wyboru trwa %.2f s (cel 3–5 s)" % jedna)
    # zgodność z planem pasa (tylko odczyt krótkiego planu gry swiat/las_pas/krotki/plan_pasa.json, D-096)
    if os.path.isfile(PLAN_PASA):
        with open(PLAN_PASA, encoding="utf-8") as f:
            plan = json.load(f)
        X0, Z0 = plan["swiat"]["X0"], plan["swiat"]["Z0"]
        poid = {k["id"]: k for k in dane["krainy"]}
        las = next((p for p in plan["punkty_przybycia"] if p["id"] == "las"), None)
        if las:
            oczek = [X0 + las["u"], Z0 + las["v"]]
            jest = next((p["xz"] for p in poid["las"]["przybycie"] if "xz" in p), None)
            if jest != oczek:
                uwagi.append("las: przybycie %r, a plan pasa mówi %r" % (jest, oczek))
        for b in plan.get("kolejne_biomy", []):
            k = poid.get(b["id"])
            if not k:
                uwagi.append("plan pasa ma biom %s, którego nie ma w krainy.json" % b["id"])
                continue
            oczek = [X0 + b["przybycie_u"], Z0]
            jest = next((p["xz"] for p in k["przybycie"] if "xz" in p), None)
            if jest != oczek:
                uwagi.append("%s: przybycie %r, plan pasa %r" % (k["id"], jest, oczek))
            if k["obszary_xz"][0][:2] != b["swiat_x"]:
                uwagi.append("%s: obszar x %r, plan pasa %r" % (k["id"], k["obszary_xz"][0][:2], b["swiat_x"]))
    else:
        uwagi.append("brak swiat/las_pas/krotki/plan_pasa.json — bez porównania z planem pasa")
    return bledy, uwagi, jedna


def generuj_dane_luau(dane, info):
    d = json.loads(json.dumps(dane))
    d["makieta"]["srodki_x"] = info["srodki_x"]
    d["makieta"]["polowa_dlugosci"] = info["polowa_dlugosci"]
    d["skrot"] = skrot_danych(dane)
    tekst = ("-- Dane — WYGENEROWANE przez swiat/teleport_chmury/zbuduj.py z krainy.json. Nie edytuj ręcznie: zmień\n"
             "-- krainy.json i uruchom zbuduj.py (--sucho też odświeża ten plik).\n"
             + STRAZNIK + "\n\treturn {}\nend\n\nreturn " + luau_wartosc(d) + "\n")
    stary = wczytaj(DANE_LUAU) if os.path.isfile(DANE_LUAU) else None
    if stary != tekst:
        with open(DANE_LUAU, "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst)
        return True, d["skrot"]
    return False, d["skrot"]


def kontrola_luau():
    sys.path.insert(0, os.path.join(REPO, "swiat", "las_potwory"))
    import sprawdz_luau  # noqa: E402  (tylko odczyt: reguły 1–4 z pakietu potworów)
    bledy = []
    pliki = sorted(n for n in os.listdir(ZRODLA) if n.endswith(".luau"))
    for n in pliki:
        tekst = wczytaj(os.path.join(ZRODLA, n))
        bledy += sprawdz_luau.sprawdz_tekst(tekst, "swiat/teleport_chmury/zrodla/" + n, pelne=True)
        if len(tekst) > LIMIT_ZRODLA:
            bledy.append("%s: %d znaków (limit Source 200 000)" % (n, len(tekst)))
    return pliki, bledy


def wiersz_czesci(c):
    w = [c["n"], c["k"], c["s"]] + c["r"] + c["cf"] + [c["c"], c["m"], c["t"], c["g"], c["rola"], c["cien"],
                                                       c.get("napis", "")]
    return "{" + ", ".join(luau_wartosc(x) for x in w) + "}"


# ------------------------------------------------------------------ główna
def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje Workspace/TeleportChmury w Roblox Studio")
    ap.add_argument("--sucho", action="store_true", help="bez Studio: sprawdź dane i źródła, pokaż plan")
    ap.add_argument("--skrypty", action="store_true", help="tylko Dane i skrypty do istniejącego kontenera")
    ap.add_argument("--usun", action="store_true", help="usuń Workspace/TeleportChmury")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()

    with open(DANE_JSON, encoding="utf-8") as f:
        dane = json.load(f)
    kontener = dane["kontener"]
    if not a.usun:
        bledy, uwagi, jedna = sprawdz_dane(dane)
        czesci, info = makieta.zbuduj_czesci(dane)
        zmienione, skrot = generuj_dane_luau(dane, info)
        pliki, bl_luau = kontrola_luau()
        print("krainy.json: %d krain, skrót %s; zrodla/Dane.luau %s" % (len(dane["krainy"]), skrot,
                                                                         "odświeżony" if zmienione else "aktualny"))
        print("przejście w jedną stronę bez wyboru: %.2f s (A %.2f + B %.2f + C %.2f + biel %.2f + D %.2f)" % (
            jedna, dane["czasy"]["wejscie_s"], dane["czasy"]["wylonienie_s"], dane["czasy"]["zanurzenie_s"],
            dane["czasy"]["biel_min_s"], dane["czasy"]["opadanie_s"]))
        print("makieta: %d części (%s)" % (info["razem"], ", ".join("%s %d" % kv for kv in info["liczba"].items())))
        print("kontrola Luau (reguły 1–4 swiat/las_potwory/sprawdz_luau.py): %d plików, %s" % (
            len(pliki), "OK" if not bl_luau else "BŁĘDY %d" % len(bl_luau)))
        for u in uwagi:
            print("  uwaga: " + u)
        for b in bledy + bl_luau:
            print("  BŁĄD: " + b)
        if bledy or bl_luau:
            sys.exit(2)
        for plik, klasa, nazwa, ctx in SKRYPTY:
            tekst = wczytaj(os.path.join(ZRODLA, plik))
            print("  %-34s → %s %s%s (%d znaków)" % ("zrodla/" + plik, klasa, nazwa,
                                                    " [RunContext=%s]" % ctx if ctx else "", len(tekst)))
    if a.sucho:
        print("sucho: OK (Studio nieużywane)")
        return

    for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
        if _s not in sys.path:
            sys.path.insert(0, _s)
    from cel_studio import MIEJSCE, wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    try:
        with StudioMCP() as s:
            s.studios(wait=15)
            sid = wybierz_studio(s, a.studio)
            stan = s.call("get_studio_state", {"studio_id": sid})["text"]
            if "Current Studio Mode: Edit" not in stan:
                sys.exit("Studio nie jest w trybie Edit — zatrzymaj Play i spróbuj ponownie.\n" + stan)

            def wykonaj(kod):
                kod = NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", str(MIEJSCE)) + kod
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
                if r["is_error"]:
                    raise StudioError(r["text"][:3000])
                w = r["text"].strip()
                if w.startswith("STOP"):
                    print(w)
                    sys.exit(2)
                return w

            def skrypty():
                for plik, klasa, nazwa, ctx in SKRYPTY:
                    kod = (SKRYPT.replace("__KONTENER__", kontener).replace("__NAZWA__", nazwa)
                           .replace("__KLASA__", klasa)
                           .replace("__RUNCONTEXT__", "s.RunContext = Enum.RunContext.%s" % ctx if ctx else ""))
                    kod = kod.replace("__ZRODLO__", dlugi_napis(wczytaj(os.path.join(ZRODLA, plik))))
                    print("  skrypt:", wykonaj(kod))

            t0 = time.time()
            if a.skrypty:
                wykonaj('local f = workspace:FindFirstChild("%s") if not f or f:GetAttribute("Wygenerowane") ~= true '
                        'then return "STOP: brak kontenera — zbuduj całość" end '
                        'game:GetService("ChangeHistoryService"):SetWaypoint("%s: przed wymianą skryptów") '
                        'f:SetAttribute("Skrot", "%s") return "OK"' % (kontener, kontener, skrot))
                skrypty()
                wykonaj('game:GetService("ChangeHistoryService"):SetWaypoint("%s: skrypty wymienione") return "OK"'
                        % kontener)
                print("gotowe (%.0f s)" % (time.time() - t0))
                return
            md = dane["makieta"]
            wynik = wykonaj(START.replace("__KONTENER__", kontener).replace("__USUN__", "true" if a.usun else "false")
                            .replace("__CZAS__", time.strftime("%Y-%m-%dT%H:%M:%S"))
                            .replace("__SKROT__", "" if a.usun else skrot)
                            .replace("__OBROT__", repr(float(md["slonce_obrot_stopnie"])))
                            .replace("__SRODEK__", ", ".join(repr(float(x)) for x in md["srodek"]))
                            .replace("__LICZBA__", str(0 if a.usun else len(czesci))))
            print("start:", wynik)
            if a.usun:
                return
            for i in range(0, len(czesci), PARTIA):
                kod = (CZESCI.replace("__KONTENER__", kontener).replace("__NAPIS__", md["napis_kolor"])
                       .replace("__TUSZ__", makieta.TUSZ)
                       .replace("__WIERSZE__", ",\n".join(wiersz_czesci(c) for c in czesci[i:i + PARTIA])))
                print("  części %d–%d: %s" % (i + 1, min(i + PARTIA, len(czesci)), wykonaj(kod)))
            skrypty()
            xs = info["srodki_x"]
            krainy = ", ".join("{%s, %r, %s}" % (luau_napis(k["id"]), float(x), "false" if k["od_poczatku"] else "true")
                               for k, x in zip(dane["krainy"], xs))
            d = md["plytka"][1]
            kod = (KONIEC.replace("__KONTENER__", kontener).replace("__KRAINY__", krainy)
                   .replace("__JASNOSC__", repr(float(md["przyciemnienie"]["jasnosc"])))
                   .replace("__NASYCENIE__", repr(float(md["przyciemnienie"]["nasycenie"])))
                   .replace("__NAPIS__", md["napis_kolor"]).replace("__NAPIS_Z__", md["napis_kolor_zamkniety"])
                   .replace("__WSK__", "%r, %r, 0" % (float(xs[0]), float(md["wskaznik_y"])))
                   .replace("__PIN__", "%r, 0, %r" % (float(xs[0] - 11.5), float(d / 2 - 2.5))))
            print("gotowe: %s (%.0f s)" % (wykonaj(kod), time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
