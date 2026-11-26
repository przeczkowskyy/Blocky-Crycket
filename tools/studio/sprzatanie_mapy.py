#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sprzątanie mapy w Roblox Studio (zlecenie Karola z 26.11.2026): z miejsca gry znikają stara wioska startowa,
stary las, stare duże miasteczko i prototypy-zaślepki, a gracz zaczyna w miasteczku-bazarze. Źródła wszystkich
usuwanych pakietów ZOSTAJĄ w repozytorium (swiat/<pakiet>/) — kontener da się w każdej chwili zbudować od nowa.

    python -B tools/studio/sprzatanie_mapy.py --sucho      # tylko odczyt: co zostałoby usunięte (instancje, części)
    python -B tools/studio/sprzatanie_mapy.py              # usuwa (Studio w trybie Edit; Ctrl+Z cofa kontener po kontenerze)
    python -B tools/studio/sprzatanie_mapy.py --tylko BonkGra,TestWalki    # tylko wybrane z listy
    python -B tools/studio/sprzatanie_mapy.py --studio <studio_id>         # gdy otwartych jest kilka okien Studio

Co robi (tylko to, co jest na liście niżej — nic innego):
  1. KONTENERY: całe kontenery Workspace/<nazwa>. Każdy musi mieć atrybut Wygenerowane = true (inaczej STOP —
     to nie nasza praca) i nie może zawierać niczego z listy CHRONIONE ani żadnego SpawnLocation (inaczej STOP).
  2. CZESCI: pojedyncze dzieci naszych kontenerów, które zostają (np. tablica Training Center przy starym starcie).
     Rodzic musi mieć Wygenerowane = true. Te same rzeczy znikają też przy pełnej przebudowie ich pakietów —
     tu usuwamy je od razu, żeby stan był czysty nawet przy samej wymianie skryptów (zbuduj.py --skrypty).
  3. Usuwanie po kawałku: najpierw potomkowie od najgłębszych, task.wait() co PACZKA instancji (kontener z 25 tys.
     instancji nie znika jednym, długim wywołaniem), na końcu sam kontener. Jedno wywołanie execute_luau na kontener.
  4. Punkty historii przed i po każdym kontenerze; każdy wysyłany kod sprawdza placeId gry i tryb Edit (w Play — STOP).
Nie przenosi SpawnLocation (to robi osobne narzędzie tools/studio/start_w_miasteczku.py), niczego nie zapisuje, nie
publikuje i nie rusza Lighting. Plik miejsca trzeba zapisać w Studio ręcznie (Ctrl+S), gdy wynik jest dobry.
"""
import argparse
import json
import os
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
    if _s not in sys.path:
        sys.path.insert(0, _s)

MIEJSCE = 129485428021967  # placeId miejsca gry (to samo co swiat/test_walki_roblox/cel_studio.py)
PACZKA = 1000

# (kontener w Workspace, źródło w repozytorium, co to jest) — kolejność = kolejność usuwania
KONTENERY = [
    ("DemoLesnaBaza", "swiat/demo_lesna_baza", "stara wioska startowa przy (0; 0; 0)"),
    ("BonkGra", "swiat/bonk", "brama i gra BONK przy starym starcie (BONK ma własną budowę osobnego miejsca)"),
    ("LasTeleport", "swiat/biom_las/teleport.py", "portal do starego lasu i jego skrypt"),
    ("BiomLas", "swiat/biom_las", "stary las (z −2637…−1280)"),
    ("LasPotwory", "swiat/las_potwory", "potwory starego lasu (ten sam kod gra dalej w LasPasGra)"),
    ("LasMgla", "swiat/biom_las/mgla.py", "mgła starego lasu"),
    ("RasyProba", "swiat/rasy_proba", "wystawa figur ras przy starym starcie"),
    ("TestWalki", "swiat/test_walki_roblox", "stara próba walki v1 (walki grają w TestWalki2)"),
    ("KrzyweMiasteczko", "swiat/krzywe_miasteczko", "stare duże miasteczko (Karol 26.11.2026: też usunąć)"),
]
# (kontener, ścieżka dziecka, co to jest) — kontener zostaje, znika tylko to dziecko
CZESCI = [
    ("TreningProba", "TablicaWejscia", "tablica Training Center z E przy starym starcie (wejście tylko z bazaru)"),
    ("StrojeProba", "Przymierzalnia", "przymierzalnia z E przy starym starcie (skrypty i dane strojów zostają)"),
    ("MiasteczkoBazarGra", "Punkty/E nowe_miasteczko", "przejście „Nowe miasteczko (E)” w starym miasteczku"),
    ("MiasteczkoBazarGra", "Punkty/E stare_miasteczko", "przejście „Stare miasteczko (E)” w bazarze"),
]
# tego nie wolno ruszyć: gdyby któraś nazwa była w środku usuwanego kontenera — STOP
CHRONIONE = ["TestPostaci", "TestWalki2", "WyborKlasy", "WyborKlasyBaza", "MiasteczkoBazar", "MiasteczkoBazarGra",
             "TreningProba", "StrojeProba", "LasPas", "LasPasGra", "BagnoPas", "BagnoPasGra", "DzunglaPas",
             "DzunglaPasGra", "TeleportChmury", "ArenyWalki", "StanGracza", "Baseplate", "SpawnLocation"]
CHRONIONE_KONCOWKA = "Podglad"   # wszystkie kontenery *Podglad (KotRasyPodglad, JajkaBiomowPodglad…) zostają

NAGLOWEK = ('if game.PlaceId ~= %d then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end\n'
            'if game:GetService("RunService"):IsRunning() then return "STOP: Studio jest w trybie Play — sprzątam tylko w trybie Edit" end\n'
            % MIEJSCE)

WSPOLNE = r'''
local H = game:GetService("HttpService")
local CHRONIONE = __CHRONIONE__
local KONCOWKA = "__KONCOWKA__"
local function chroniony(n)
	if string.sub(n, -#KONCOWKA) == KONCOWKA then return true end
	for _, c in CHRONIONE do if c == n then return true end end
	return false
end
-- chronione w środku = kontener (Folder / Model z atrybutem Wygenerowane) o chronionej nazwie albo prawdziwy
-- SpawnLocation (klasa, nie nazwa: mapy mają ozdobne części nazwane „SpawnLocation”, np. KrzyweMiasteczko/Spawn)
local function zlicz(k)
	local inst, cz, chr, sp = 0, 0, {}, 0
	for _, d in k:GetDescendants() do
		inst += 1
		if d:IsA("BasePart") then cz += 1 end
		if d:IsA("SpawnLocation") then sp += 1 end
		if (d:IsA("Folder") or d:IsA("Model")) and d:GetAttribute("Wygenerowane") == true and chroniony(d.Name) then
			table.insert(chr, d:GetFullName())
		end
	end
	for _, c in CHRONIONE do
		local t = workspace:FindFirstChild(c)
		if t and t ~= k and t:IsDescendantOf(k) then table.insert(chr, t:GetFullName()) end
	end
	return inst, cz, chr, sp
end
local function sciezka(k, s)
	local o = k
	for _, n in string.split(s, "/") do
		o = o and o:FindFirstChild(n)
	end
	return o
end
'''

# tylko odczyt: stan każdej pozycji listy
SPIS = WSPOLNE + r'''
local KONT = __KONTENERY__
local CZ = __CZESCI__
local o = { kontenery = {}, czesci = {}, spawny = {} }
for _, n in KONT do
	local k = workspace:FindFirstChild(n)
	if not k then
		table.insert(o.kontenery, { nazwa = n, jest = false })
	else
		local inst, cz, chr, sp = zlicz(k)
		table.insert(o.kontenery, { nazwa = n, jest = true, wyg = k:GetAttribute("Wygenerowane") == true, klasa = k.ClassName,
			inst = inst, czesci = cz, chronione = chr, spawny = sp })
	end
end
for _, c in CZ do
	local k = workspace:FindFirstChild(c[1])
	local d = k and sciezka(k, c[2])
	local inst, cz = 0, 0
	if d then
		for _, x in d:GetDescendants() do
			inst += 1
			if x:IsA("BasePart") then cz += 1 end
		end
		if d:IsA("BasePart") then cz += 1 end
	end
	table.insert(o.czesci, { kontener = c[1], sciezka = c[2], jest = d ~= nil, wyg = k ~= nil and k:GetAttribute("Wygenerowane") == true,
		inst = inst, czesci = cz })
end
for _, d in workspace:GetDescendants() do
	if d:IsA("SpawnLocation") then
		table.insert(o.spawny, string.format("%s (%.1f; %.1f; %.1f)%s", d:GetFullName(), d.Position.X, d.Position.Y,
			d.Position.Z, if d.Enabled then "" else " wyłączony"))
	end
end
return H:JSONEncode(o)
'''

# usunięcie jednego kontenera po kawałku
USUN_KONTENER = WSPOLNE + r'''
local CH = game:GetService("ChangeHistoryService")
local nazwa = "__NAZWA__"
local k = workspace:FindFirstChild(nazwa)
if not k then return "BRAK (kontenera nie ma)" end
if k:GetAttribute("Wygenerowane") ~= true then
	return "STOP: Workspace/" .. nazwa .. " nie ma atrybutu Wygenerowane — nie ruszam cudzej pracy"
end
local inst, cz, chr, sp = zlicz(k)
if #chr > 0 then return "STOP: w Workspace/" .. nazwa .. " jest chronione: " .. table.concat(chr, ", ") end
if sp > 0 then return "STOP: w Workspace/" .. nazwa .. " jest SpawnLocation (" .. sp .. ") — nie usuwam miejsca startu" end
CH:SetWaypoint("Sprzątanie mapy: przed usunięciem " .. nazwa)
local lista = k:GetDescendants()
local n, bledy = #lista, 0
for i = n, 1, -1 do
	local ok = pcall(function() lista[i]:Destroy() end)
	if not ok then bledy += 1 end
	if (n - i + 1) % __PACZKA__ == 0 then task.wait() end
end
k:Destroy()
CH:SetWaypoint("Sprzątanie mapy: usunięto " .. nazwa)
return string.format("USUNIETO %d instancji, %d części%s", inst, cz, if bledy > 0 then " (nieusuniętych osobno: " .. bledy .. ")" else "")
'''

USUN_CZESC = WSPOLNE + r'''
local CH = game:GetService("ChangeHistoryService")
local k = workspace:FindFirstChild("__KONTENER__")
if not k then return "BRAK (kontenera nie ma)" end
if k:GetAttribute("Wygenerowane") ~= true then return "STOP: Workspace/__KONTENER__ bez atrybutu Wygenerowane" end
local d = sciezka(k, "__SCIEZKA__")
if not d then return "BRAK (już nie ma)" end
if d:IsA("SpawnLocation") or d:FindFirstChildWhichIsA("SpawnLocation", true) then return "STOP: SpawnLocation w środku" end
local n = #d:GetDescendants() + 1
CH:SetWaypoint("Sprzątanie mapy: przed usunięciem __KONTENER__/__SCIEZKA__")
d:Destroy()
CH:SetWaypoint("Sprzątanie mapy: usunięto __KONTENER__/__SCIEZKA__")
return "USUNIETO " .. n .. " instancji"
'''


def luau_lista(v):
    return json.dumps(v, ensure_ascii=False).replace("[", "{").replace("]", "}")


def wspolne(kod):
    return (kod.replace("__CHRONIONE__", luau_lista(CHRONIONE)).replace("__KONCOWKA__", CHRONIONE_KONCOWKA)
            .replace("__PACZKA__", str(PACZKA)))


def kod_spisu(kontenery, czesci):
    return NAGLOWEK + wspolne(SPIS).replace("__KONTENERY__", luau_lista([k[0] for k in kontenery])).replace(
        "__CZESCI__", luau_lista([[c[0], c[1]] for c in czesci]))


def kod_usun_kontener(nazwa):
    return NAGLOWEK + wspolne(USUN_KONTENER).replace("__NAZWA__", nazwa)


def kod_usun_czesc(kontener, sciezka):
    return NAGLOWEK + wspolne(USUN_CZESC).replace("__KONTENER__", kontener).replace("__SCIEZKA__", sciezka)


def sprawdz_listy():
    """Kontrola offline: lista do usunięcia nie zawiera niczego chronionego."""
    bledy = []
    for n, _, _ in KONTENERY:
        if n in CHRONIONE or n.endswith(CHRONIONE_KONCOWKA):
            bledy.append("%s jest jednocześnie na liście usuwanych i chronionych" % n)
    for k, s, _ in CZESCI:
        if k not in CHRONIONE:
            bledy.append("część %s/%s: kontener %s nie jest na liście chronionych (miał zostać)" % (k, s, k))
    for k, s, _ in CZESCI:
        if any(k == n for n, _, _ in KONTENERY):
            bledy.append("część %s/%s leży w kontenerze, który i tak znika" % (k, s))
    return bledy


def wypisz_spis(spis, kontenery, czesci):
    opisy = {k[0]: k for k in kontenery}
    razem_i = razem_c = 0
    print("Kontenery do usunięcia (Workspace/<nazwa>):")
    for w in spis["kontenery"]:
        n = w["nazwa"]
        _, zrodlo, opis = opisy[n]
        if not w["jest"]:
            print("  %-18s — nie ma w miejscu (już usunięty)" % n)
            continue
        uwagi = []
        if not w.get("wyg"):
            uwagi.append("BEZ Wygenerowane → STOP")
        if w.get("chronione"):
            uwagi.append("CHRONIONE W ŚRODKU: %s → STOP" % ", ".join(w["chronione"]))
        if w.get("spawny"):
            uwagi.append("SpawnLocation w środku → STOP")
        razem_i += w["inst"]
        razem_c += w["czesci"]
        print("  %-18s %6d instancji, %6d części · %s · źródło %s%s" % (
            n, w["inst"], w["czesci"], opis, zrodlo, (" · " + "; ".join(uwagi)) if uwagi else ""))
    print("  razem: %d instancji, %d części" % (razem_i, razem_c))
    print("Części kontenerów, które zostają:")
    for w, c in zip(spis["czesci"], czesci):
        print("  %-44s %s · %s" % ("%s/%s" % (w["kontener"], w["sciezka"]),
                                    ("%d instancji, %d części" % (w["inst"], w["czesci"])) if w["jest"] else "nie ma",
                                    c[2]))
    print("SpawnLocation w miejscu: %s" % ("; ".join(spis["spawny"]) or "brak"))


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Sprzątanie mapy gry w Roblox Studio (lista w pliku)")
    ap.add_argument("--sucho", action="store_true", help="tylko odczyt: pokaż, co zostałoby usunięte")
    ap.add_argument("--tylko", default=None, help="nazwy z listy, po przecinku (kontenery albo kontener/ścieżka)")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()

    bledy = sprawdz_listy()
    if bledy:
        sys.exit("BŁĄD listy: " + "; ".join(bledy))
    kontenery, czesci = list(KONTENERY), list(CZESCI)
    if a.tylko:
        wybor = {x.strip() for x in a.tylko.split(",") if x.strip()}
        znane = {k[0] for k in KONTENERY} | {"%s/%s" % (c[0], c[1]) for c in CZESCI}
        obce = wybor - znane
        if obce:
            sys.exit("Spoza listy: %s (lista: %s)" % (", ".join(sorted(obce)), ", ".join(sorted(znane))))
        kontenery = [k for k in kontenery if k[0] in wybor]
        czesci = [c for c in czesci if "%s/%s" % (c[0], c[1]) in wybor]

    from cel_studio import MIEJSCE as MIEJSCE_GRY, wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    if MIEJSCE_GRY != MIEJSCE:
        sys.exit("BŁĄD: placeId w cel_studio.py (%s) ≠ %s — przerywam" % (MIEJSCE_GRY, MIEJSCE))
    try:
        with StudioMCP(timeout=300) as s:
            s.studios(wait=15)
            sid = wybierz_studio(s, a.studio)

            def wykonaj(kod):
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=600)
                if r["is_error"]:
                    raise StudioError(r["text"][:3000])
                return r["text"].strip()

            spis_txt = wykonaj(kod_spisu(kontenery, czesci))
            if spis_txt.startswith("STOP"):
                sys.exit(spis_txt)
            spis = json.loads(spis_txt)
            wypisz_spis(spis, kontenery, czesci)
            if a.sucho:
                print("sucho: nic nie zostało zmienione")
                return
            stan = s.call("get_studio_state", {"studio_id": sid})["text"]
            if "Current Studio Mode: Edit" not in stan:
                sys.exit("Studio nie jest w trybie Edit — zatrzymaj Play i spróbuj ponownie.\n" + stan)
            stop = [w["nazwa"] for w in spis["kontenery"] if w["jest"] and (not w.get("wyg") or w.get("chronione")
                                                                             or w.get("spawny"))]
            if stop:
                sys.exit("STOP: nie usuwam niczego, bo %s nie spełnia warunków (wyżej)" % ", ".join(stop))
            t0 = time.time()
            for n, _, _ in kontenery:
                t1 = time.time()
                w = wykonaj(kod_usun_kontener(n))
                print("  %-18s %s (%.0f s)" % (n, w, time.time() - t1), flush=True)
                if w.startswith("STOP"):
                    sys.exit(2)
            for k, sc, _ in czesci:
                w = wykonaj(kod_usun_czesc(k, sc))
                print("  %-44s %s" % ("%s/%s" % (k, sc), w), flush=True)
                if w.startswith("STOP"):
                    sys.exit(2)
            po = json.loads(wykonaj(kod_spisu(kontenery, czesci)))
            zostalo = [w["nazwa"] for w in po["kontenery"] if w["jest"]] + [
                "%s/%s" % (w["kontener"], w["sciezka"]) for w in po["czesci"] if w["jest"]]
            print("gotowe (%.0f s): %s" % (time.time() - t0, "wszystko z listy usunięte" if not zostalo
                                            else "ZOSTAŁO: " + ", ".join(zostalo)))
            print("SpawnLocation w miejscu: %s" % ("; ".join(po["spawny"]) or "brak"))
            print("Zapisz miejsce w Studio (Ctrl+S), gdy wynik jest dobry; Ctrl+Z cofa kontener po kontenerze.")
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
