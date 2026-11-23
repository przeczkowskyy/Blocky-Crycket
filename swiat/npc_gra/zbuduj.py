#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Postacie niezależne w Roblox Studio (D-109; propozycja): kontener Workspace/NpcGra — same moduły i skrypty.

    python -B swiat/npc_gra/zbuduj.py --sucho      # policz, sprawdź dane i źródła, bez Studio
    python -B swiat/npc_gra/zbuduj.py              # zbuduj od nowa moduły i skrypty (kotwice zostają)
    python -B swiat/npc_gra/zbuduj.py --stan       # odczyt: co stoi w kontenerze (niczego nie zmienia)
    python -B swiat/npc_gra/zbuduj.py --usun       # usuń własny kontener (cudzy obiekt o tej nazwie zostaje)
    python -B swiat/npc_gra/zbuduj.py --kotwica trener_sila --klucz trening_sila --poz 10,0.5,20 --patrz 10,30
                                                   # kotwica NPC w Workspace/NpcGra/Kotwice (stopy w poz, twarzą ku patrz)
    python -B swiat/npc_gra/zbuduj.py --bez-kotwicy trening_sila
    python -B swiat/npc_gra/zbuduj.py --trenerzy          # sześciu trenerów mini-gier w punktach z danych pakietu treningu
    python -B swiat/npc_gra/zbuduj.py --trenerzy --stan   # tylko porównanie: czy arena w Studio zgadza się z danymi
    python -B swiat/npc_gra/zbuduj.py --trenerzy --sucho  # plan bez Studio
    python -B swiat/npc_gra/zbuduj.py --bez-trenerow

Co robi w Studio (tylko tryb Edit, tylko miejsce gry — numer z swiat/test_walki_roblox/cel_studio.py): punkt historii,
własny kontener Workspace/NpcGra (atrybut Wygenerowane): Moduly/{DaneNpc, LogikaNpc, RigNpc}, Moduly/Rigi/Rig_<id>,
Sygnaly/{Polecenie, SterowanieKlienta, SterowanieSerwera}, skrypty SerwerNpc i KlientNpc, folder Kotwice. Żadnych
części postaci: rigi składa klient w grze. Niczego nie zapisuje ani nie publikuje, nie rusza cudzych instancji
(figur bazaru też nie — chowa je klient w grze, lokalnie). Inny pakiet może postawić NPC sam: część z tagiem
i atrybutem Npc (kotwica_luau niżej) albo polecenie Sygnaly/Polecenie w grze — README.
"""
import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (REPO, os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
    if _s not in sys.path:
        sys.path.append(_s)
if TU in sys.path:
    sys.path.remove(TU)
sys.path.insert(0, TU)                                 # własne moduły pakietu zawsze pierwsze (dane, zbuduj)
import dane as DN  # noqa: E402

ZRODLA = os.path.join(TU, "zrodla")
MODULY = ("LogikaNpc", "RigNpc")                        # obok wygenerowanego DaneNpc
SKRYPTY = (("SerwerNpc", "SerwerNpc.server.luau", "Server"), ("KlientNpc", "KlientNpc.client.luau", "Client"))
SYGNALY = ("Polecenie", "SterowanieKlienta", "SterowanieSerwera")
FOLDER_KOTWIC = "Kotwice"

# wspólny początek każdego kodu wysyłanego do Studio: właściwe miejsce, tryb Edit, tylko własny kontener
WSTEP = r'''
if game.PlaceId ~= __MIEJSCE__ then
	return "STOP: to nie jest miejsce gry — nic nie zmieniono"
end
if game:GetService("RunService"):IsRunning() then
	return "STOP: Studio nie jest w trybie Edit — nic nie zmieniono"
end
local KONTENER = "__KONTENER__"
local function kontenery()
	local nasze, obce = {}, {}
	for _, d in workspace:GetChildren() do
		if d.Name == KONTENER then
			table.insert(if d:GetAttribute("Wygenerowane") == true then nasze else obce, d)
		end
	end
	return nasze, obce
end
local function kontener()
	local nasze, obce = kontenery()
	if #obce > 0 then
		return nil, string.format("STOP: w Workspace jest %d obiekt(ów) '%s' bez atrybutu Wygenerowane — nie ruszam cudzej pracy", #obce, KONTENER)
	end
	if #nasze > 1 then
		return nil, string.format("STOP: w Workspace są %d kontenery '%s' — usuń je (--usun) i zbuduj od nowa", #nasze, KONTENER)
	end
	return nasze[1], nil
end
'''

START = WSTEP + r'''
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
local CH = game:GetService("ChangeHistoryService")
CH:SetWaypoint("NpcGra: przed budową")
if not kont then
	kont = Instance.new("Folder")
	kont.Name = KONTENER
	kont:SetAttribute("Wygenerowane", true)
	kont.Parent = workspace
end
local zostaly = 0
for _, d in kont:GetChildren() do
	if d.Name == "__KOTWICE__" and d:IsA("Folder") then
		zostaly = #d:GetChildren()
	else
		d:Destroy()
	end
end
kont:SetAttribute("Zrodlo", "__ZRODLO__")
kont:SetAttribute("Zbudowano", "__CZAS__")
kont:SetAttribute("Skrot", "__SKROT__")
if kont:GetAttribute("__WYLACZNIK__") == nil then
	kont:SetAttribute("__WYLACZNIK__", true)
end
local function folder(rodzic, nazwa)
	local f = rodzic:FindFirstChild(nazwa)
	if not f then
		f = Instance.new("Folder")
		f.Name = nazwa
		f.Parent = rodzic
	end
	return f
end
local moduly = folder(kont, "Moduly")
folder(moduly, "Rigi")
folder(kont, "__KOTWICE__")
local sygnaly = folder(kont, "Sygnaly")
for _, nazwa in { __SYGNALY__ } do
	local b = Instance.new("BindableFunction")
	b.Name = nazwa
	b.Parent = sygnaly
end
return string.format("kontener gotowy (kotwic zostało: %d)", zostaly)
'''

ZRODLO = WSTEP + r'''
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
if not kont then
	return "STOP: brak kontenera Workspace/" .. KONTENER
end
local rodzic = kont
for kawalek in string.gmatch("__RODZIC__", "[^/]+") do
	rodzic = rodzic:FindFirstChild(kawalek)
	if not rodzic then
		return "STOP: brak folderu __RODZIC__ w kontenerze"
	end
end
local stary = rodzic:FindFirstChild("__NAZWA__")
if stary then
	stary:Destroy()
end
local s = Instance.new("__KLASA__")
s.Name = "__NAZWA__"
if s:IsA("Script") then
	s.RunContext = Enum.RunContext.__KONTEKST__
end
s.Source = __TEKST__
s.Parent = rodzic
return string.format("__NAZWA__: %d bajtów", #s.Source)
'''

KONIEC = WSTEP + r'''
local kont = kontener()
if kont then
	game:GetService("ChangeHistoryService"):SetWaypoint("NpcGra: zbudowano")
end
return "punkt historii"
'''

USUN = WSTEP + r'''
local nasze, obce = kontenery()
local zostawione = ""
if #obce > 0 then
	zostawione = string.format("; zostawiono %d obiekt(ów) '%s' bez atrybutu Wygenerowane (cudza praca, nie ruszam)", #obce, KONTENER)
end
if #nasze == 0 then
	return (if #obce > 0 then "STOP: nic nie usunięto" else "nie ma czego usuwać") .. zostawione
end
local CH = game:GetService("ChangeHistoryService")
CH:SetWaypoint("NpcGra: przed usunięciem")
for _, k in nasze do
	k:Destroy()
end
CH:SetWaypoint("NpcGra: usunięto")
return string.format("USUNIĘTO %d × Workspace/%s%s", #nasze, KONTENER, zostawione)
'''

# kotwica NPC: niewidzialna część z tagiem i atrybutem Npc; RODZIC = wyrażenie Luau dające instancję-rodzica
KOTWICA = r'''
do
	local rodzic = __RODZIC__
	local stara = rodzic:FindFirstChild("__NAZWA__")
	if stara then
		stara:Destroy()
	end
	local a = Instance.new("Part")
	a.Name = "__NAZWA__"
	a.Size = Vector3.new(1, 0.2, 1)
	a.Transparency = 1
	a.Anchored = true
	a.CanCollide = false
	a.CanTouch = false
	a.CanQuery = false
	a.CastShadow = false
	local poz = Vector3.new(__POZ__)
	a.CFrame = CFrame.lookAt(poz, Vector3.new(__PATRZ_X__, poz.Y, __PATRZ_Z__))
	a:SetAttribute("Npc", "__NPC__")
	a:SetAttribute("NpcKlucz", "__KLUCZ__")
	__DODATKI__
	a:AddTag("__TAG__")
	a.Parent = rodzic
end
'''

# trenerzy mini-gier: kotwice w punktach z danych pakietu treningu — najpierw kontrola (tylko odczyt), czy arena w Studio
# to ta z repozytorium (figura każdej gry stoi przy swoim punkcie); przy niezgodności nic nie powstaje
TRENERZY = WSTEP + r'''
local D = __DANE__
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
if not kont then
	return "STOP: brak kontenera Workspace/" .. KONTENER .. " — najpierw zbuduj.py"
end
local folder = kont:FindFirstChild("__KOTWICE__")
if not folder then
	return "STOP: brak folderu __KOTWICE__ — najpierw zbuduj.py"
end
local function znajdz(sciezka)
	local o = game
	for kawalek in string.gmatch(sciezka, "[^/]+") do
		o = o and o:FindFirstChild(kawalek)
	end
	return o
end
local zle, opisy, podloza = {}, {}, {}
for i, t in D.trenerzy do
	local punkt = Vector3.new(t.poz[1], t.poz[2], t.poz[3])
	local pomin = { kont }
	if t.zastepuje then
		local fig = znajdz(t.zastepuje)
		if not fig or not fig:IsA("Model") then
			table.insert(zle, t.gra .. ": brak figury " .. t.zastepuje)
		else
			table.insert(pomin, fig)
			local cf = fig:GetBoundingBox()
			local d = Vector3.new(cf.Position.X - punkt.X, 0, cf.Position.Z - punkt.Z).Magnitude
			if d > D.tolerancja then
				table.insert(zle, string.format("%s: figura stoi %.1f st od punktu z danych", t.gra, d))
			end
		end
	end
	local p = RaycastParams.new()
	p.FilterType = Enum.RaycastFilterType.Exclude
	p.FilterDescendantsInstances = pomin
	local traf = workspace:Raycast(punkt + Vector3.new(0, 8, 0), Vector3.new(0, -16, 0), p)
	if not traf then
		table.insert(zle, t.gra .. ": brak podłoża pod punktem trenera")
	else
		podloza[i] = traf.Position.Y
		table.insert(opisy, string.format("%s → %s (podłoże %s, y = %.2f)", t.gra, t.npc, traf.Instance.Name, traf.Position.Y))
	end
end
if #zle > 0 then
	return "STOP: arena w Studio nie zgadza się z danymi pakietu treningu — nic nie postawiono: " .. table.concat(zle, "; ")
end
if D.tylko_stan then
	return "zgodne — można stawiać: " .. table.concat(opisy, "; ")
end
local CH = game:GetService("ChangeHistoryService")
CH:SetWaypoint("NpcGra: przed trenerami")
for i, t in D.trenerzy do
	local nazwa = "Kotwica_" .. t.klucz
	local stara = folder:FindFirstChild(nazwa)
	if stara then
		stara:Destroy()
	end
	local a = Instance.new("Part")
	a.Name = nazwa
	a.Size = Vector3.new(1, 0.2, 1)
	a.Transparency = 1
	a.Anchored = true
	a.CanCollide = false
	a.CanTouch = false
	a.CanQuery = false
	a.CastShadow = false
	local poz = Vector3.new(t.poz[1], podloza[i], t.poz[3])
	a.CFrame = CFrame.lookAt(poz, Vector3.new(t.patrz[1], poz.Y, t.patrz[2]))
	a:SetAttribute("Npc", t.npc)
	a:SetAttribute("NpcKlucz", t.klucz)
	a:SetAttribute("NpcSkala", t.skala)
	if t.zastepuje then
		a:SetAttribute("NpcZastepuje", t.zastepuje)
	end
	if t.zostaw then
		a:SetAttribute("NpcZostaw", t.zostaw)
	end
	a:AddTag("__TAG__")
	a.Parent = folder
end
CH:SetWaypoint("NpcGra: trenerzy")
return "POSTAWIONO kotwice trenerów: " .. table.concat(opisy, "; ")
'''

BEZ_TRENEROW = WSTEP + r'''
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
local f = kont and kont:FindFirstChild("__KOTWICE__")
local ile = 0
if f then
	game:GetService("ChangeHistoryService"):SetWaypoint("NpcGra: przed usunięciem trenerów")
	for _, nazwa in { __NAZWY__ } do
		local a = f:FindFirstChild(nazwa)
		if a then
			a:Destroy()
			ile += 1
		end
	end
	game:GetService("ChangeHistoryService"):SetWaypoint("NpcGra: usunięto trenerów")
end
return string.format("USUNIĘTO kotwic trenerów: %d", ile)
'''

BEZ_KOTWICY = WSTEP + r'''
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
local f = kont and kont:FindFirstChild("__KOTWICE__")
local a = f and f:FindFirstChild("__NAZWA__")
if not a then
	return "nie ma kotwicy __NAZWA__"
end
game:GetService("ChangeHistoryService"):SetWaypoint("NpcGra: przed usunięciem kotwicy")
a:Destroy()
game:GetService("ChangeHistoryService"):SetWaypoint("NpcGra: usunięto kotwicę")
return "USUNIĘTO kotwicę __NAZWA__"
'''

# odczyt stanu kontenera (Edit i Play): JSON; niczego nie zmienia
STAN = r'''
local HS = game:GetService("HttpService")
local kont = workspace:FindFirstChild("__KONTENER__")
if not kont or kont:GetAttribute("Wygenerowane") ~= true then
	return HS:JSONEncode({ jest = false })
end
local w = { jest = true, skrot = kont:GetAttribute("Skrot"), zbudowano = kont:GetAttribute("Zbudowano"),
	wlaczone = kont:GetAttribute("__WYLACZNIK__"), zrodla = {}, sygnaly = {}, kotwice = {}, czesci = 0 }
for _, d in kont:GetDescendants() do
	if d:IsA("LuaSourceContainer") then
		w.zrodla[d.Name] = { klasa = d.ClassName, bajtow = #d.Source, rodzic = d.Parent.Name,
			kontekst = if d:IsA("Script") then d.RunContext.Name else nil }
	elseif d:IsA("BindableFunction") then
		table.insert(w.sygnaly, d.Name)
	elseif d:IsA("BasePart") then
		w.czesci += 1
		if d.Parent.Name == "__KOTWICE__" then
			table.insert(w.kotwice, { nazwa = d.Name, npc = d:GetAttribute("Npc"), klucz = d:GetAttribute("NpcKlucz"),
				skala = d:GetAttribute("NpcSkala"), tag = d:HasTag("__TAG__"), widoczna = d.Transparency < 1,
				fizyka = d.CanCollide or d.CanTouch or d.CanQuery,
				poz = { d.Position.X, d.Position.Y, d.Position.Z }, przod = { d.CFrame.LookVector.X, d.CFrame.LookVector.Z } })
		end
	end
end
return HS:JSONEncode(w)
'''


def log(*a):
    print("NPC-GRA |", *a, flush=True)


def wstaw(szablon, **w):
    for k, v in w.items():
        szablon = szablon.replace("__%s__" % k, v)
    return szablon


def czytaj(nazwa):
    with open(os.path.join(ZRODLA, nazwa), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def zrodla(pliki):
    """Wszystko, co trafia do Studio: [(folder w kontenerze, nazwa, klasa, kontekst, tekst)]."""
    w = [("Moduly", "DaneNpc", "ModuleScript", "", pliki[DN.PLIK_DANYCH])]
    w += [("Moduly", n, "ModuleScript", "", czytaj(n + ".luau")) for n in MODULY]
    w += [("Moduly/Rigi", os.path.basename(p)[:-5], "ModuleScript", "", t) for p, t in pliki.items() if p.startswith("rigi/")]
    w += [("", nazwa, "Script", kontekst, czytaj(plik)) for nazwa, plik, kontekst in SKRYPTY]
    return w


def pliki_luau():
    return ([os.path.join(ZRODLA, n + ".luau") for n in MODULY] + [os.path.join(ZRODLA, p) for _, p, _ in SKRYPTY]
            + [os.path.join(ZRODLA, DN.PLIK_DANYCH)]
            + sorted(os.path.join(DN.RIGI, n) for n in os.listdir(DN.RIGI) if n.endswith(".luau")))


def kontrola_luau():
    """Moduł kontroli statycznej swiat/las_potwory/sprawdz_luau.py wczytany po ścieżce (tylko odczyt)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "kontrola_luau_potworow", os.path.join(REPO, "swiat", "las_potwory", "sprawdz_luau.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sprawdz_zrodla():
    return kontrola_luau().sprawdz_pliki(pliki_luau(), wypisz=lambda t: None)


def dane_trenerow(U, tylko_stan=False):
    """Dane dla kodu TRENERZY: punkty z pakietu treningu (DN.punkty_trenerow) w układzie listy Luau."""
    T = DN.punkty_trenerow(U)
    trenerzy = [{"gra": t["gra"], "npc": t["npc"], "klucz": t["klucz"], "poz": t["poz"], "patrz": t["patrz"],
                 "skala": t["skala"], "zastepuje": t["zastepuje"], "zostaw": ",".join(t["zostaw"]) or None} for t in T]
    return T, {"trenerzy": trenerzy, "tolerancja": U["trenerzy"]["tolerancja_figury"], "tylko_stan": tylko_stan}


def kod_trenerow(U, wspolne, tylko_stan=False):
    T, d = dane_trenerow(U, tylko_stan)
    return T, wstaw(TRENERZY, DANE=DN.luau(d), KOTWICE=FOLDER_KOTWIC, TAG=U["tag_kotwicy"], **wspolne)


def kotwica_luau(U, npc, klucz, poz, patrz, rodzic, skala=None, zastepuje=None, imie=None, rola=None, nazwa=None,
                 zostaw=None):
    """Kawałek Luau (do wklejenia w kod budowniczego innego pakietu, tryb Edit): niewidzialna kotwica NPC w `rodzic`
    (wyrażenie Luau, np. 'workspace.TreningProba.Arena'). poz = stopy NPC (x, y, z), patrz = punkt (x, z), ku
    któremu NPC stoi twarzą. Klient NpcGra postawi tam NPC `npc` sam, gdy gracz będzie blisko."""
    DN.wpis_npc(U, npc)
    dodatki = []
    for atr, v in (("NpcSkala", skala), ("NpcZastepuje", zastepuje), ("NpcImie", imie), ("NpcRola", rola),
                   ("NpcZostaw", ",".join(zostaw) if zostaw else None)):
        if v is not None:
            dodatki.append("a:SetAttribute(%s, %s)" % (json.dumps(atr), DN.luau(v)))
    return wstaw(KOTWICA, RODZIC=rodzic, NAZWA=nazwa or ("Kotwica_" + klucz), POZ="%r, %r, %r" % tuple(float(v) for v in poz),
                 PATRZ_X=repr(float(patrz[0])), PATRZ_Z=repr(float(patrz[1])), NPC=npc, KLUCZ=klucz,
                 DODATKI="\n\t".join(dodatki), TAG=U["tag_kotwicy"])


def kod_stanu(U):
    return wstaw(STAN, KONTENER=U["kontener"], WYLACZNIK=U["wylacznik"], KOTWICE=FOLDER_KOTWIC, TAG=U["tag_kotwicy"])


def _liczby(tekst, ile):
    w = [float(x) for x in tekst.split(",")]
    if len(w) != ile:
        raise SystemExit("oczekiwane %d liczb po przecinku, jest: %r" % (ile, tekst))
    return w


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Postacie niezależne w Studio: Workspace/NpcGra")
    ap.add_argument("--sucho", action="store_true", help="tylko policz i sprawdź, bez Studio")
    ap.add_argument("--usun", action="store_true", help="usuń własny kontener")
    ap.add_argument("--stan", action="store_true", help="odczytaj, co stoi w kontenerze")
    ap.add_argument("--kotwica", default=None, metavar="NPC", help="postaw kotwicę tej postaci w NpcGra/Kotwice")
    ap.add_argument("--klucz", default=None, help="klucz stanowiska kotwicy (nazwa dla poleceń „graj”)")
    ap.add_argument("--poz", default=None, help="x,y,z — stopy NPC")
    ap.add_argument("--patrz", default=None, help="x,z — punkt, ku któremu NPC stoi twarzą")
    ap.add_argument("--skala", type=float, default=None)
    ap.add_argument("--bez-kotwicy", default=None, metavar="KLUCZ", help="usuń kotwicę o tym kluczu")
    ap.add_argument("--trenerzy", action="store_true",
                    help="postaw sześciu trenerów mini-gier w punktach z danych pakietu treningu (z --stan: tylko porównanie)")
    ap.add_argument("--bez-trenerow", action="store_true", help="usuń kotwice trenerów mini-gier")
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    try:
        U, D, R, pliki = DN.wszystkie_pliki()
    except DN.BladDanych as e:
        log("BŁĄD danych:", e)
        return 2
    zle = DN.nieaktualne(pliki)
    if zle:
        log("BŁĄD: nieaktualne dane (%s) — uruchom python -B swiat/npc_gra/dane.py" % ", ".join(zle))
        return 1
    Z = zrodla(pliki)
    bledy = sprawdz_zrodla()
    bledy += ["%s: %d znaków ponad limit %d" % (n, len(t), U["limit_zrodla"]) for _, n, _, _, t in Z
              if len(t) > U["limit_zrodla"]]
    for b in bledy:
        log("BŁĄD źródeł:", b)
    for linia in DN.tabela(U, D, R, pliki):
        log(linia)
    log("do Studio: %d modułów i skryptów, %d kB; sygnały: %s; źródła Luau: %s"
        % (len(Z), sum(len(t.encode("utf-8")) for *_, t in Z) // 1000, ", ".join(SYGNALY),
           "bez błędów" if not bledy else "%d błędów" % len(bledy)))
    if a.kotwica:
        if not (a.klucz and a.poz and a.patrz):
            ap.error("--kotwica wymaga --klucz, --poz i --patrz")
        kod_kotwicy = kotwica_luau(U, a.kotwica, a.klucz, _liczby(a.poz, 3), _liczby(a.patrz, 2),
                                   "kont:FindFirstChild(%s)" % json.dumps(FOLDER_KOTWIC), skala=a.skala)
    if a.trenerzy:
        bez_punktu = []
        DN.punkty_trenerow(U, bez_punktu)
        for gra in bez_punktu:
            log("trener %-13s pominięty — pakiet treningu nie ma dla tej gry punktu trenera" % gra)
        for t in DN.punkty_trenerow(U):
            log("trener %-13s %-20s ×%.2f  stopy (%.1f; %.1f; %.1f)  %s%s" % (
                t["gra"], t["npc"], t["skala"], t["poz"][0], t["poz"][1], t["poz"][2],
                "chowa " + t["zastepuje"].split("/", 2)[-1] if t["zastepuje"] else "nic nie chowa (puste miejsce trenera)",
                "; zostają widoczne: " + ", ".join(t["zostaw"]) if t["zostaw"] else ""))
    if bledy:
        return 1
    if a.sucho:
        return 0
    from studio_mcp import StudioMCP  # noqa: E402
    from cel_studio import MIEJSCE, wybierz_studio  # noqa: E402
    wspolne = dict(MIEJSCE=str(MIEJSCE), KONTENER=U["kontener"])
    with StudioMCP(timeout=240) as s:
        sid = wybierz_studio(s, a.studio)
        if "Current Studio Mode: Edit" not in s.call("get_studio_state", {"studio_id": sid})["text"]:
            log("PRZERWANO — Studio nie jest w trybie Edit (ktoś może grać); nic nie zmieniono")
            return 1

        def wykonaj(kod, opis):
            r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
            tekst = (r["text"] or "").strip()
            if r["is_error"] or tekst.startswith("STOP"):
                log("PRZERWANO — Studio odmówiło (%s): %s" % (opis, tekst[:600]))
                raise SystemExit(1)
            return tekst

        if a.trenerzy:
            _, kod = kod_trenerow(U, wspolne, tylko_stan=a.stan)
            log(wykonaj(kod, "trenerzy"))
            return 0
        if a.bez_trenerow:
            nazwy = ", ".join(json.dumps("Kotwica_" + t["klucz"]) for t in DN.punkty_trenerow(U))
            log(wykonaj(wstaw(BEZ_TRENEROW, KOTWICE=FOLDER_KOTWIC, NAZWY=nazwy, **wspolne), "trenerzy"))
            return 0
        if a.stan:
            print(json.dumps(json.loads(wykonaj(kod_stanu(U), "stan")), ensure_ascii=False, indent=1))
            return 0
        if a.usun:
            log(wykonaj(wstaw(USUN, **wspolne), "usuwanie"))
            return 0
        if a.bez_kotwicy:
            log(wykonaj(wstaw(BEZ_KOTWICY, KOTWICE=FOLDER_KOTWIC, NAZWA="Kotwica_" + a.bez_kotwicy, **wspolne), "kotwica"))
            return 0
        if a.kotwica:
            kod = (wstaw(WSTEP, **wspolne) + "local kont, odmowa = kontener()\nif odmowa then\n\treturn odmowa\nend\n"
                   "if not kont then\n\treturn \"STOP: brak kontenera — najpierw zbuduj.py\"\nend\n"
                   "game:GetService(\"ChangeHistoryService\"):SetWaypoint(\"NpcGra: przed kotwicą\")\n" + kod_kotwicy
                   + "game:GetService(\"ChangeHistoryService\"):SetWaypoint(\"NpcGra: kotwica\")\nreturn \"kotwica %s (%s) postawiona\"\n"
                   % (a.klucz, a.kotwica))
            log(wykonaj(kod, "kotwica"))
            return 0
        log(wykonaj(wstaw(START, KOTWICE=FOLDER_KOTWIC, ZRODLO="swiat/npc_gra", CZAS=time.strftime("%Y-%m-%d %H:%M"),
                          SKROT=D["skrot"], WYLACZNIK=U["wylacznik"],
                          SYGNALY=", ".join(json.dumps(n) for n in SYGNALY), **wspolne), "start"))
        for rodzic, nazwa, klasa, kontekst, tekst in Z:
            log(wykonaj(wstaw(ZRODLO, RODZIC=rodzic, NAZWA=nazwa, KLASA=klasa, KONTEKST=kontekst or "Legacy",
                              TEKST=DN.luau(tekst), **wspolne), nazwa))
        wykonaj(wstaw(KONIEC, **wspolne), "koniec")
        stan = json.loads(wykonaj(kod_stanu(U), "stan"))
        niezgodne = []
        for _, nazwa, klasa, kontekst, tekst in Z:
            m = stan["zrodla"].get(nazwa)
            if not m or m["klasa"] != klasa or m["bajtow"] != len(tekst.encode("utf-8")) or (kontekst and m.get("kontekst") != kontekst):
                niezgodne.append(nazwa)
        if sorted(stan["sygnaly"]) != sorted(SYGNALY) or stan["skrot"] != D["skrot"]:
            niezgodne.append("sygnały albo skrót")
        log("kontrola po budowie: %s" % ("zgodne — %d źródeł, skrót %s, kotwic %d, części %d"
                                         % (len(stan["zrodla"]), stan["skrot"], len(stan["kotwice"]), stan["czesci"])
                                         if not niezgodne else "NIEZGODNE: " + ", ".join(niezgodne)))
        return 1 if niezgodne else 0


if __name__ == "__main__":
    sys.exit(main())
