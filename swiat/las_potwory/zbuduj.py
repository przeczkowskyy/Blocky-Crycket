#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Odtwarza w Roblox Studio kontener pakietu „potwory w ruchu” (Workspace/LasPotwory) ze źródeł w tym folderze.

    python -B swiat/las_potwory/zbuduj.py --sucho      # bez Studio: generuj_dane --sprawdz, sprawdz_luau, strażniki, plan
    python -B swiat/las_potwory/zbuduj.py              # buduje / odbudowuje Workspace/LasPotwory (idempotentnie)
    python -B swiat/las_potwory/zbuduj.py --skrypty    # tylko skrypty i moduły do istniejącego kontenera
    python -B swiat/las_potwory/zbuduj.py --usun       # usuwa Workspace/LasPotwory (np. przed publikacją)
    python -B swiat/las_potwory/zbuduj.py --studio <studio_id>   # wymagane, gdy otwartych jest kilka okien Studio

Kontrakt: PROJEKT.md rozdz. 1.1 (co powstaje) i 8.7 (ten skrypt). Wzór: swiat/test_walki2/zbuduj.py.

Co powstaje (tylko w Workspace/LasPotwory z atrybutem Wygenerowane = true; bez żadnych części):
  Moduly/      Stale, DanePotworow (wygenerowany), Logika, Wzorcowe (kopia swiat/test_walki2/zrodla/Wzorcowe.luau),
               Walka/{Dane, Los, Statystyki, Przeciwnicy, Umiejetnosci, Silnik} — KOPIA src/server/Walka robiona przy
               każdej budowie, z dopiskiem i strażnikiem Studio na początku
  Stan/        pusty (serwer wkłada tu Configuration żywych potworów w trybie Play)
  Zdalne/RozpocznijWalke2 (RemoteFunction), Sygnaly/SterowanieSerwera i Sygnaly/SterowanieKlienta (BindableFunction)
  SerwerPotworow (Script, RunContext = Server), KlientPotworow (Script, RunContext = Client)
Atrybuty kontenera: Wygenerowane, Zrodlo, Zbudowano, Skrot (= DanePotworow.skrot). Atrybuty testowe ustawione ręcznie
w Edit (ZiarnoTestowe, TestBezSesji, TestGraczy, TestBezBiomu) przechodzą na odbudowany kontener.

Zasady bezpieczeństwa (wspólne miejsce Team Create) — jak w swiat/test_walki2/zbuduj.py:
- wszystko trafia do JEDNEGO kontenera Workspace/LasPotwory z atrybutem Wygenerowane = true; odbudowa i --usun ruszają
  TYLKO ten kontener — jeśli pod tą nazwą jest coś bez atrybutu, skrypt przerywa;
- przed budową tylko odczyt i ostrzeżenia (nie przerywa): czy jest Workspace/BiomLas z Wygenerowane, czy jest
  Workspace/TestWalki2/Moduly/OdtwarzaczWalki2 i TestWalki2/Aktorzy/<4 klucze>; pakiet nie ma części, więc bez pudła;
- przed i po budowie punkt historii (ChangeHistoryService) — całość cofa się przez Ctrl+Z;
- każdy skrypt i moduł w kontenerze zaczyna się od strażnika „poza Studio nic nie rób” (sprawdzane przed wysłaniem);
- tylko tryb Edit; niczego nie publikuje, nie zapisuje miejsca, nie zmienia Lighting ani cudzych instancji;
- okno Studio wybiera swiat/test_walki_roblox/cel_studio.py (jedno okno albo --studio, zawsze placeId gry,
  sprawdzany jeszcze raz w Studio przez game.PlaceId w każdym wysyłanym kodzie).
--sucho nie importuje studio_mcp ani cel_studio (import dopiero po gałęzi --sucho).
"""
import argparse
import os
import re
import subprocess
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if TU not in sys.path:
    sys.path.insert(0, TU)
import sprawdz_luau  # noqa: E402  (własny plik pakietu, bez zależności)

KONTENER = "LasPotwory"
ZRODLO = "swiat/las_potwory"
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
STRAZNIK_MODULU = 'if not game:GetService("RunService"):IsStudio() then\n\treturn {}\nend\n'
LIMIT_ZRODLA = 199000  # Source ma limit 200 000 znaków
ATRYBUTY_TESTOWE = ["ZiarnoTestowe", "TestBezSesji", "TestGraczy", "TestBezBiomu"]
SZABLONY = ["lesny_slime", "cierniowy_wilk", "muchomornik", "straznik_lasu"]

# (plik względem repozytorium, klasa, ścieżka w kontenerze, RunContext, kto pisze)
SKRYPTY = [
    ("swiat/las_potwory/zrodla/Stale.luau", "ModuleScript", "Moduly/Stale", None, "K"),
    ("swiat/las_potwory/zrodla/DanePotworow.luau", "ModuleScript", "Moduly/DanePotworow", None, "S (generuj_dane.py)"),
    ("swiat/las_potwory/zrodla/Logika.luau", "ModuleScript", "Moduly/Logika", None, "S"),
    ("swiat/test_walki2/zrodla/Wzorcowe.luau", "ModuleScript", "Moduly/Wzorcowe", None, "prototyp (kopia)"),
    ("swiat/las_potwory/zrodla/SerwerPotworow.server.luau", "Script", "SerwerPotworow", "Server", "S"),
    ("swiat/las_potwory/zrodla/KlientPotworow.client.luau", "Script", "KlientPotworow", "Client", "K"),
]
# kopia silnika walki v2 (źródło prawdy: src/) — moduły szukają się przez script.Parent
SILNIK = [("src/server/Walka/%s.luau" % n, "Moduly/Walka/%s" % n)
          for n in ("Dane", "Los", "Statystyki", "Przeciwnicy", "Umiejetnosci", "Silnik")]
FOLDERY = ["Moduly", "Moduly/Walka", "Stan", "Zdalne", "Sygnaly"]
# (klasa, ścieżka) — jedyna zdalna funkcja i dwa haczyki testowe
INNE = [("RemoteFunction", "Zdalne/RozpocznijWalke2"), ("BindableFunction", "Sygnaly/SterowanieSerwera"),
        ("BindableFunction", "Sygnaly/SterowanieKlienta")]

# kontrola miejsca na początku KAŻDEGO wysyłanego kodu (__MIEJSCE__ wstawia wykonaj)
NAGLOWEK_MIEJSCA = ('if game.PlaceId ~= __MIEJSCE__ then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end\n'
                    'if game:GetService("RunService"):IsRunning() then return "STOP: Studio jest w trybie Play — buduję tylko w trybie Edit" end\n')

# tylko odczyt: co zastajemy w miejscu (ostrzeżenia, nie przerywa)
SPRAWDZ = r'''
local uwagi = {}
local biom = workspace:FindFirstChild("BiomLas")
if not biom then
	table.insert(uwagi, "brak Workspace/BiomLas (potwory nie wystartują bez TestBezBiomu = true)")
elseif biom:GetAttribute("Wygenerowane") ~= true then
	table.insert(uwagi, "Workspace/BiomLas nie ma atrybutu Wygenerowane = true")
else
	local grunt = biom:FindFirstChild("Teren") and biom.Teren:FindFirstChild("Grunt")
	local plyta = grunt and grunt:FindFirstChild("Płyta")
	if not plyta or not plyta:IsA("BasePart") then
		table.insert(uwagi, "brak BiomLas/Teren/Grunt/Płyta")
	else
		table.insert(uwagi, string.format("Płyta: Position (%.2f, %.2f, %.2f), Size (%.1f, %.1f, %.1f), Orientation.Y %.1f",
			plyta.Position.X, plyta.Position.Y, plyta.Position.Z, plyta.Size.X, plyta.Size.Y, plyta.Size.Z, plyta.Orientation.Y))
	end
end
local tw = workspace:FindFirstChild("__PROTOTYP__")
local m = tw and tw:FindFirstChild("Moduly")
if not m or not m:FindFirstChild("OdtwarzaczWalki2") then
	table.insert(uwagi, "brak Workspace/__PROTOTYP__/Moduly/OdtwarzaczWalki2 (walki niedostępne)")
end
local a = tw and tw:FindFirstChild("Aktorzy")
for _, k in { __SZABLONY__ } do
	if not a or not a:FindFirstChild(k) then
		table.insert(uwagi, "brak szablonu __PROTOTYP__/Aktorzy/" .. k .. " (klient pokaże bryły zastępcze)")
	end
end
return if #uwagi == 0 then "OK" else table.concat(uwagi, " | ")
'''

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
	CH:SetWaypoint("LasPotwory: przed usunięciem")
	for _, d in stare do d:Destroy() end
	CH:SetWaypoint("LasPotwory: usunięto")
	return "USUNIETO"
end
-- atrybuty testowe ustawione ręcznie przechodzą na nowy kontener
local testowe = {}
for _, d in stare do
	for _, a in { __TESTOWE__ } do
		local v = d:GetAttribute(a)
		if v ~= nil then testowe[a] = v end
	end
end
CH:SetWaypoint("LasPotwory: przed budową")
for _, d in stare do d:Destroy() end
local f = Instance.new("Folder")
f.Name = nazwa
f:SetAttribute("Wygenerowane", true)
f:SetAttribute("Zrodlo", "__ZRODLO__")
f:SetAttribute("Zbudowano", "__CZAS__")
f:SetAttribute("Skrot", "__SKROT__")
for a, v in testowe do f:SetAttribute(a, v) end
for _, sciezka in { __FOLDERY__ } do
	local rodzic = f
	local czesci = string.split(sciezka, "/")
	for i = 1, #czesci - 1 do rodzic = rodzic:FindFirstChild(czesci[i]) end
	local d = Instance.new("Folder")
	d.Name = czesci[#czesci]
	d.Parent = rodzic
end
f.Parent = workspace
return "OK"
'''

# zdalna funkcja i haczyki (idempotentnie; także przy --skrypty na starym kontenerze)
INNE_KOD = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera"
end
for _, nazwa in { __FOLDERY__ } do
	local rodzic = f
	local czesci = string.split(nazwa, "/")
	for i = 1, #czesci do
		local d = rodzic:FindFirstChild(czesci[i])
		if not d then
			d = Instance.new("Folder")
			d.Name = czesci[i]
			d.Parent = rodzic
		end
		rodzic = d
	end
end
local zrobione = {}
for _, w in { __INNE__ } do
	local sciezka = string.split(w[2], "/")
	local rodzic = f
	for i = 1, #sciezka - 1 do
		rodzic = rodzic:FindFirstChild(sciezka[i])
		if not rodzic then return "STOP: brak folderu " .. sciezka[i] end
	end
	local stary = rodzic:FindFirstChild(sciezka[#sciezka])
	if not stary or stary.ClassName ~= w[1] then
		if stary then stary:Destroy() end
		local o = Instance.new(w[1])
		o.Name = sciezka[#sciezka]
		o.Parent = rodzic
		table.insert(zrobione, w[2])
	end
end
f:SetAttribute("Skrot", "__SKROT__")
return "OK (" .. #zrobione .. " nowych)"
'''

SKRYPT = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera"
end
local sciezka = string.split("__SCIEZKA__", "/")
local rodzic = f
for i = 1, #sciezka - 1 do
	rodzic = rodzic:FindFirstChild(sciezka[i])
	if not rodzic then return "STOP: brak folderu " .. sciezka[i] end
end
local stary = rodzic:FindFirstChild(sciezka[#sciezka])
if stary then stary:Destroy() end
local s = Instance.new("__KLASA__")
s.Name = sciezka[#sciezka]
__RUNCONTEXT__
s.Source = __ZRODLO__
s.Parent = rodzic
return "OK " .. s:GetFullName() .. " (" .. #s.Source .. " znaków)"
'''

KONIEC = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f then return "STOP: brak kontenera" end
local razem, skrypty, czesci = 0, 0, 0
for _, d in f:GetDescendants() do
	razem += 1
	if d:IsA("LuaSourceContainer") then skrypty += 1 end
	if d:IsA("BasePart") then czesci += 1 end
end
game:GetService("ChangeHistoryService"):SetWaypoint("LasPotwory: zbudowano")
return "instancji: " .. razem .. ", skryptów: " .. skrypty .. ", części: " .. czesci .. ", Skrot = " .. tostring(f:GetAttribute("Skrot"))
'''


def wczytaj(sciezka):
    with open(sciezka, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def dlugi_napis(tekst):
    """Tekst jako literał Luau [==[ … ]==] z poziomem, którego nie ma w treści."""
    poziom = 3
    while ("]" + "=" * poziom + "]") in tekst or ("[" + "=" * poziom + "[") in tekst:
        poziom += 1
    return "[" + "=" * poziom + "[\n" + tekst + "]" + "=" * poziom + "]"


def luau_napis(s):
    """Napis Pythona jako literał Luau w cudzysłowie."""
    import json
    return json.dumps(s, ensure_ascii=False)


def zrodla_pakietu():
    """Lista (ścieżka w kontenerze, klasa, RunContext, źródło, plik). Przerywa (kod 2), gdy brakuje pliku."""
    wynik, braki = [], []
    for plik, klasa, sciezka, kontekst, kto in SKRYPTY:
        pelna = os.path.join(REPO, plik)
        if not os.path.isfile(pelna):
            braki.append("%s (pisze: %s)" % (plik, kto))
            continue
        wynik.append((sciezka, klasa, kontekst, wczytaj(pelna), plik))
    for plik, sciezka in SILNIK:
        pelna = os.path.join(REPO, plik)
        if not os.path.isfile(pelna):
            braki.append(plik)
            continue
        kopia = ("-- KOPIA %s zrobiona przez swiat/las_potwory/zbuduj.py (%s) — źródło prawdy jest w repozytorium.\n"
                 % (plik, time.strftime("%Y-%m-%d"))) + STRAZNIK_MODULU + wczytaj(pelna)
        wynik.append((sciezka, "ModuleScript", None, kopia, plik))
    if braki:
        print("BŁĄD: brak plików źródłowych:")
        for b in braki:
            print("  " + b)
        sys.exit(2)
    return wynik


def skrot_danych(tekst):
    m = re.search(r'\bskrot\s*=\s*"([0-9a-f]{12})"', tekst)
    return m.group(1) if m else None


def sprawdz_offline(zrodla):
    """--sucho i każda budowa: dane aktualne, sprawdz_luau czysto, strażniki, rozmiary. Zwraca skrót danych."""
    # 1. generuj_dane.py --sprawdz (kod 1 = nieaktualne dane)
    gen = os.path.join(TU, "generuj_dane.py")
    if not os.path.isfile(gen):
        sys.exit("BŁĄD: brak swiat/las_potwory/generuj_dane.py (pisze programista S)")
    r = subprocess.run([sys.executable, "-B", gen, "--sprawdz"], cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    wyjscie = (r.stdout + r.stderr).strip()
    print("generuj_dane.py --sprawdz: kod %d%s" % (r.returncode, (" — " + wyjscie.splitlines()[-1]) if wyjscie else ""))
    if r.returncode != 0:
        print(wyjscie)
        sys.exit("BŁĄD: zrodla/DanePotworow.luau jest nieaktualny — uruchom python -B swiat/las_potwory/generuj_dane.py")
    # 2. sprawdz_luau.py na zrodla/*.luau pakietu
    pliki = sorted(os.path.join(TU, "zrodla", n) for n in os.listdir(os.path.join(TU, "zrodla")) if n.endswith(".luau"))
    bledy = sprawdz_luau.sprawdz_pliki(pliki)
    print("sprawdz_luau.py: %d plików, %s" % (len(pliki), "OK" if not bledy else "BŁĘDY: %d" % len(bledy)))
    if bledy:
        for b in bledy:
            print("  " + b)
        sys.exit("BŁĄD: sprawdz_luau.py zgłosił błędy")
    # 3. strażnik Studio i limit Source w KAŻDYM źródle (także w kopiach silnika i Wzorcowe)
    for sciezka, klasa, kontekst, tekst, plik in zrodla:
        if not sprawdz_luau.pierwsza_instrukcja(tekst).startswith(STRAZNIK):
            sys.exit("BŁĄD: %s (%s) nie zaczyna się od strażnika „%s”" % (sciezka, plik, STRAZNIK))
        if len(tekst) > LIMIT_ZRODLA:
            sys.exit("BŁĄD: %s ma %d znaków (limit Source 200 000)" % (sciezka, len(tekst)))
    dane = next(t for s, k, c, t, p in zrodla if s == "Moduly/DanePotworow")
    skrot = skrot_danych(dane)
    if not skrot:
        sys.exit("BŁĄD: w zrodla/DanePotworow.luau nie ma pola skrot = \"<12 znaków>\"")
    return skrot


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje kontener Workspace/LasPotwory w Roblox Studio")
    ap.add_argument("--sucho", action="store_true", help="bez Studio: sprawdź dane i źródła, pokaż plan")
    ap.add_argument("--skrypty", action="store_true", help="tylko skrypty i moduły do istniejącego kontenera")
    ap.add_argument("--usun", action="store_true", help="usuń Workspace/LasPotwory")
    ap.add_argument("--studio", default=None, help="studio_id (wymagane, gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()

    zrodla = [] if a.usun else zrodla_pakietu()
    skrot = "" if a.usun else sprawdz_offline(zrodla)

    if not a.usun:
        print("Kontener: Workspace/%s · Skrot danych: %s · modułów i skryptów: %d" % (KONTENER, skrot, len(zrodla)))
        print("  %-52s → %s" % ("Folder", ", ".join(FOLDERY)))
        for klasa, sciezka in INNE:
            print("  %-52s → %s %s" % ("(nowa instancja)", klasa, sciezka))
        for sciezka, klasa, kontekst, tekst, plik in zrodla:
            print("  %-52s → %s %s%s (%d znaków)" % (plik, klasa, sciezka,
                                                      " [RunContext=%s]" % kontekst if kontekst else "", len(tekst)))
    if a.sucho:
        print("sucho: OK (Studio nieużywane)")
        return

    # --- dopiero tutaj Studio (zgodnie z kontraktem: --sucho niczego z tego nie importuje)
    for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
        if _s not in sys.path:
            sys.path.insert(0, _s)
    from cel_studio import MIEJSCE, wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    try:
        with StudioMCP() as s:
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

            def wyslij_skrypt(sciezka, klasa, kontekst, tekst):
                kod = (SKRYPT.replace("__KONTENER__", KONTENER).replace("__SCIEZKA__", sciezka).replace("__KLASA__", klasa)
                       .replace("__RUNCONTEXT__", "s.RunContext = Enum.RunContext.%s" % kontekst if kontekst else ""))
                kod = kod.replace("__ZRODLO__", dlugi_napis(tekst))
                return wykonaj(kod)

            t0 = time.time()
            if not a.usun:
                print("w miejscu (tylko odczyt):", wykonaj(SPRAWDZ.replace("__PROTOTYP__", "TestWalki2")
                                                           .replace("__SZABLONY__", ", ".join(luau_napis(k) for k in SZABLONY))))
            inne_kod = (INNE_KOD.replace("__KONTENER__", KONTENER).replace("__SKROT__", skrot)
                        .replace("__FOLDERY__", ", ".join(luau_napis(x) for x in FOLDERY))
                        .replace("__INNE__", ", ".join("{%s, %s}" % (luau_napis(k), luau_napis(p)) for k, p in INNE)))
            if a.skrypty:
                wykonaj('local f = workspace:FindFirstChild("%s") if not f or f:GetAttribute("Wygenerowane") ~= true '
                        'then return "STOP: brak kontenera — zbuduj całość" end '
                        'game:GetService("ChangeHistoryService"):SetWaypoint("LasPotwory: przed wymianą skryptów") return "OK"'
                        % KONTENER)
                print("  zdalne i haczyki:", wykonaj(inne_kod))
                for sciezka, klasa, kontekst, tekst, plik in zrodla:
                    print("  skrypt:", wyslij_skrypt(sciezka, klasa, kontekst, tekst))
                print("gotowe: %s (%.0f s)" % (wykonaj(KONIEC.replace("__KONTENER__", KONTENER)), time.time() - t0))
                return
            wynik = wykonaj(START.replace("__KONTENER__", KONTENER).replace("__USUN__", "true" if a.usun else "false")
                            .replace("__ZRODLO__", ZRODLO).replace("__SKROT__", skrot)
                            .replace("__TESTOWE__", ", ".join(luau_napis(x) for x in ATRYBUTY_TESTOWE))
                            .replace("__FOLDERY__", ", ".join(luau_napis(x) for x in FOLDERY))
                            .replace("__CZAS__", time.strftime("%Y-%m-%dT%H:%M:%S")))
            print("start:", wynik)
            if a.usun or not wynik.endswith("OK"):
                return
            print("  zdalne i haczyki:", wykonaj(inne_kod))
            for sciezka, klasa, kontekst, tekst, plik in zrodla:
                print("  skrypt:", wyslij_skrypt(sciezka, klasa, kontekst, tekst))
            print("gotowe: %s (%.0f s)" % (wykonaj(KONIEC.replace("__KONTENER__", KONTENER)), time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
