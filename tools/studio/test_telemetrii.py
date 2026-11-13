#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator testu telemetrii gry do uruchomienia w Roblox Studio.

    python tools/studio/test_telemetrii.py                      # zapisuje test w katalogu tymczasowym i wypisuje ścieżkę
    python tools/studio/test_telemetrii.py --wyjscie plik.luau
    python tools/studio_mcp.py luau plik.luau                   # uruchamia test w otwartym Studio

Skleja JEDEN plik Luau: źródła src/server/Telemetria/Agregator.luau, Magazyn.luau i Zrodla.luau (wklejone bez zmian,
każde jako funkcja zwracająca moduł) oraz asercje: klucze godzin, sygnatury błędów, czyszczenie danych graczy,
scalanie i przycinanie kubełków, ponawianie zapisu, sesje i błędy z podstawionych usług.

Test niczego nie zapisuje i niczego nie zmienia w miejscu: magazyn, mapa serwerów, gracze i zegar są atrapami
w pamięci. Wynik to jedno zdanie („TEST TELEMETRII: … OK” albo lista niezaliczonych asercji).

Wartości oczekiwane, które da się policzyć niezależnie (klucze godzin z kalendarza, sygnatury błędów), liczy ten
skrypt w Pythonie — test porównuje z nimi wynik kodu Luau.
"""
import argparse
import datetime
import os
import re
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZRODLA = os.path.join(REPO, "src", "server", "Telemetria")
WYMAGANIE = "local Agregator = require(script.Parent.Agregator)\n"
# Globalne nazwy Roblox, których nie może być w czystej logice (Agregator.luau).
GLOBALE_ROBLOX = ("game", "workspace", "script", "task", "os", "Instance", "Enum", "typeof", "warn", "wait", "spawn",
                  "delay", "tick", "time", "shared", "_G", "require", "DateTime")

CHWILE = [0, 3599, 3600, 951782400, 951868799, 1709251199, 1709251200, 1794546000, 1794549599, 1798761599, 1798761600,
          1835395200, 4102444800, 4107542400]
KOMUNIKATY = [
    "ServerScriptService.Server.Walka:42: attempt to index nil with 'Zdrowie'",
    "ServerScriptService.Server.Karczma:118: zadanie 7 nie istnieje",
    "ServerScriptService.Server.Karczma:118: zadanie 9 nie istnieje",
    "ServerScriptService.Server.Karczma:119: zadanie 7 nie istnieje",
    "Błąd zapisu: zażółć gęślą jaźń 12",
    "bez numeru linii",
    "",
]


def klucz_godziny(t):
    """Klucz wpisu w Data Store policzony z kalendarza (niezależnie od algorytmu w Agregator.luau)."""
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("g_%Y%m%d_%H")


def sygnatura(komunikat):
    """Sygnatura błędu jak w Agregator.sygnatura: liczby → '#', dopisany pierwszy numer linii, skrót djb2 (32 bity)."""
    b = komunikat.encode("utf-8")[:300]
    linia = re.search(rb":(\d+)", b)
    wzorzec = re.sub(rb"\d+", b"#", b) + b"|" + (linia.group(1) if linia else b"")
    skrot = 5381
    for bajt in wzorzec:
        skrot = (skrot * 33 + bajt) % 4294967296
    return "%08x" % skrot


def napis_luau(tekst):
    """Literał napisu Luau w cudzysłowach (znaki sterujące jako \\ddd)."""
    wynik = []
    for znak in tekst:
        if znak == "\\":
            wynik.append("\\\\")
        elif znak == '"':
            wynik.append('\\"')
        elif ord(znak) < 32 or ord(znak) == 127:
            wynik.append("\\%03d" % ord(znak))
        else:
            wynik.append(znak)
    return '"' + "".join(wynik) + '"'


def bez_komentarzy_i_napisow(kod):
    """Kod Luau bez komentarzy i literałów napisów (do szukania nazw globalnych)."""
    kod = re.sub(r"--\[\[.*?\]\]", " ", kod, flags=re.S)
    kod = re.sub(r"--[^\n]*", " ", kod)
    kod = re.sub(r'"(?:\\.|[^"\\\n])*"', '""', kod)
    return re.sub(r"'(?:\\.|[^'\\\n])*'", "''", kod)


def globale_roblox(kod):
    """Nazwy globalne Roblox użyte w kodzie (pola po kropce, np. kubelek.time, się nie liczą)."""
    czysty = bez_komentarzy_i_napisow(kod)
    return sorted({m.group(1) for m in re.finditer(r"(?<![\w.:])(%s)\b" % "|".join(GLOBALE_ROBLOX), czysty)})


def czytaj(nazwa):
    with open(os.path.join(ZRODLA, nazwa), encoding="utf-8") as f:
        kod = f.read().replace("\r\n", "\n")
    if not kod.rstrip().endswith("return " + os.path.splitext(nazwa)[0]):
        raise SystemExit("%s: plik ma się kończyć zwróceniem modułu (return %s)" % (nazwa, os.path.splitext(nazwa)[0]))
    return kod


def jako_funkcja(nazwa, kod):
    return "local %s = (function()\n%s\nend)()\n" % (nazwa, kod.rstrip("\n"))


def zbuduj():
    agregator, magazyn, zrodla = czytaj("Agregator.luau"), czytaj("Magazyn.luau"), czytaj("Zrodla.luau")
    obce = globale_roblox(agregator)
    if obce:
        raise SystemExit("Agregator.luau ma być czystą logiką, a używa globali Roblox: %s" % ", ".join(obce))
    if magazyn.count(WYMAGANIE) != 1:
        raise SystemExit("Magazyn.luau: nie znalazłem linii „%s”" % WYMAGANIE.strip())
    magazyn = magazyn.replace(WYMAGANIE, "-- (test) Agregator jest zmienną zdefiniowaną wyżej w tym pliku\n")
    klucze = "\n".join("\t{ %d, %s }," % (t, napis_luau(klucz_godziny(t))) for t in CHWILE)
    sygnatury = "\n".join("\t{ %s, %s }," % (napis_luau(k), napis_luau(sygnatura(k))) for k in KOMUNIKATY)
    return (NAGLOWEK + jako_funkcja("Agregator", agregator) + "\n" + jako_funkcja("Magazyn", magazyn) + "\n"
            + jako_funkcja("Zrodla", zrodla) + "\n"
            + TESTY.replace("--@KLUCZE@", klucze).replace("--@SYGNATURY@", sygnatury))


NAGLOWEK = """-- WYGENEROWANE przez tools/studio/test_telemetrii.py — nie poprawiaj ręcznie, popraw generator albo źródła.
-- Test telemetrii gry (src/server/Telemetria): czysta logika i atrapy w pamięci. Niczego nie zapisuje i niczego
-- nie zmienia w miejscu. Uruchom w Roblox Studio:  python tools/studio_mcp.py luau <ten plik>
-- Wynik: jedno zdanie „TEST TELEMETRII: … OK” albo lista niezaliczonych asercji.

"""

TESTY = r'''-- =========================================================================== narzędzia testu
local zaliczone = 0
local niezaliczone = {}
local biezacy_test = "?"

local function sprawdz(warunek, opis)
	if warunek then
		zaliczone += 1
	else
		table.insert(niezaliczone, biezacy_test .. ": " .. tostring(opis))
	end
end

local function rowne(otrzymane, oczekiwane, opis)
	sprawdz(
		otrzymane == oczekiwane,
		tostring(opis) .. " — jest " .. tostring(otrzymane) .. ", ma być " .. tostring(oczekiwane)
	)
end

local function test(nazwa, funkcja)
	biezacy_test = nazwa
	local ok, blad = pcall(funkcja)
	if not ok then
		table.insert(niezaliczone, nazwa .. ": wyjątek — " .. tostring(blad))
	end
end

local function kopia(wartosc)
	if type(wartosc) ~= "table" then
		return wartosc
	end
	local wynik = {}
	for klucz, element in pairs(wartosc) do
		wynik[klucz] = kopia(element)
	end
	return wynik
end

local function takie_same(a, b)
	if type(a) ~= type(b) then
		return false
	end
	if type(a) ~= "table" then
		return a == b
	end
	for klucz, element in pairs(a) do
		if not takie_same(element, b[klucz]) then
			return false
		end
	end
	for klucz in pairs(b) do
		if a[klucz] == nil then
			return false
		end
	end
	return true
end

local function ile_kluczy(tabela)
	local n = 0
	for _ in pairs(tabela) do
		n += 1
	end
	return n
end

local function suma_n(slownik)
	local suma = 0
	for _, wpis in pairs(slownik) do
		suma += wpis.n
	end
	return suma
end

local LITERY = "abcdefghijklmnopqrstuvwxyz"
-- Nazwa z samych liter (liczby w komunikacie nie zmieniają sygnatury błędu, litery tak).
local function nazwa_literowa(numer)
	local wynik = ""
	local reszta = numer
	while true do
		local indeks = reszta % 26 + 1
		wynik = string.sub(LITERY, indeks, indeks) .. wynik
		reszta = math.floor(reszta / 26)
		if reszta == 0 then
			break
		end
	end
	return wynik
end

local T0 = 1794546000 -- 2026-11-13 05:00:00 UTC
local GODZINA_05 = "g_20261113_05"

-- Zegar do testów: czas.t ustawia test.
local function nowy_zegar(start)
	local czas = { t = start }
	return czas, function()
		return czas.t
	end
end

local function cisza() end

-- Atrapa zdarzenia Roblox (Connect / Disconnect / Fire).
local function sygnal()
	local s = { odbiorcy = {} }
	function s:Connect(funkcja)
		local wpis = { funkcja = funkcja, aktywny = true }
		table.insert(self.odbiorcy, wpis)
		local polaczenie = {}
		function polaczenie:Disconnect()
			wpis.aktywny = false
		end
		return polaczenie
	end
	function s:Fire(a, b, c)
		for _, wpis in ipairs(self.odbiorcy) do
			if wpis.aktywny then
				wpis.funkcja(a, b, c)
			end
		end
	end
	return s
end

-- =========================================================================== czas i klucze
local KLUCZE = {
--@KLUCZE@
}

test("klucze godzin (UTC)", function()
	for _, para in ipairs(KLUCZE) do
		rowne(Agregator.klucz_godziny(para[1]), para[2], "klucz dla chwili " .. tostring(para[1]))
	end
	rowne(Agregator.klucz_godziny(T0), GODZINA_05, "początek godziny")
	rowne(Agregator.klucz_godziny(T0 + 3599), GODZINA_05, "ostatnia sekunda godziny")
	rowne(Agregator.klucz_godziny(T0 + 3600), "g_20261113_06", "następna godzina")
	rowne(Agregator.godzina(T0 + 1234), T0, "godzina() obcina do pełnej godziny")
	rowne(Agregator.godzina(T0 + 0.5), T0, "godzina() dla ułamka sekundy")
	local rok, miesiac, dzien, godzina = Agregator.data_utc(T0 + 59)
	rowne(rok, 2026, "rok")
	rowne(miesiac, 11, "miesiąc")
	rowne(dzien, 13, "dzień")
	rowne(godzina, 5, "godzina")
end)

test("przedziały długości sesji", function()
	local przypadki = {
		{ 0, "do_1" }, { 59, "do_1" }, { 60, "do_5" }, { 299, "do_5" }, { 300, "do_15" }, { 899, "do_15" },
		{ 900, "do_30" }, { 1799, "do_30" }, { 1800, "do_60" }, { 3599, "do_60" }, { 3600, "ponad_60" },
		{ 999999, "ponad_60" }, { -5, "do_1" },
	}
	for _, para in ipairs(przypadki) do
		rowne(Agregator.przedzial_sesji(para[1]), para[2], "przedział dla " .. tostring(para[1]) .. " s")
	end
	rowne(Agregator.przedzial_sesji("x"), "do_1", "śmieć liczy się jak zero")
end)

-- =========================================================================== sygnatury i czyszczenie tekstów
local SYGNATURY = {
--@SYGNATURY@
}

test("sygnatury błędów", function()
	for _, para in ipairs(SYGNATURY) do
		rowne(Agregator.sygnatura(para[1]), para[2], "sygnatura „" .. para[1] .. "”")
	end
	rowne(#Agregator.sygnatura("cokolwiek"), 8, "sygnatura ma 8 znaków")
	rowne(
		Agregator.sygnatura("Server.Karczma:118: zadanie 7 nie istnieje"),
		Agregator.sygnatura("Server.Karczma:118: zadanie 12345 nie istnieje"),
		"inna liczba w komunikacie = ten sam błąd"
	)
	sprawdz(
		Agregator.sygnatura("Server.Karczma:118: blad") ~= Agregator.sygnatura("Server.Karczma:119: blad"),
		"inna linia = inny błąd"
	)
	sprawdz(
		Agregator.sygnatura("Server.Karczma:118: blad") ~= Agregator.sygnatura("Server.Walka:118: blad"),
		"inny skrypt = inny błąd"
	)
	local dlugi = string.rep("x", 400)
	rowne(Agregator.sygnatura(dlugi .. "A"), Agregator.sygnatura(dlugi .. "B"), "liczy się pierwsze 300 bajtów")
	rowne(Agregator.sygnatura(42), Agregator.sygnatura("42"), "liczba zamiast tekstu")
end)

test("dane graczy znikają z komunikatów", function()
	local f = Agregator.bez_danych_gracza
	rowne(
		f("Workspace.Jan_Kowalski.Miecz:12: attempt to index nil", { "Jan_Kowalski" }),
		"Workspace.<gracz>.Miecz:12: attempt to index nil",
		"nazwa gracza w ścieżce"
	)
	rowne(
		f("ServerScriptService.Server.Walka:42: blad", { "Server" }),
		"ServerScriptService.<gracz>.Walka:42: blad",
		"gracz „Server” nie psuje ServerScriptService"
	)
	rowne(f("Gracz Mr. X (1) wyszedł", { "Mr. X (1)" }), "Gracz <gracz> wyszedł", "znaki specjalne w nazwie")
	rowne(f("Gracz Żaba spadł, Żabangi nie", { "Żaba" }), "Gracz <gracz> spadł, Żabangi nie", "nazwa z polską literą")
	rowne(f("a+b = c", { "a+b" }), "<gracz> = c", "plus w nazwie")
	rowne(f("ab oraz abc", { "ab" }), "ab oraz abc", "nazwy krótsze niż 3 znaki zostają")
	rowne(
		f("Jan12345 i Janek, i Jan12345", { "Jan12345", "Janek" }),
		"<gracz> i <gracz>, i <gracz>",
		"kilka nazw, nazwa z cyframi"
	)
	rowne(
		f("Profil 123456789 nie wczytany, linia 42", nil),
		"Profil <n> nie wczytany, linia 42",
		"długa liczba (UserId) znika, numer linii zostaje"
	)
	rowne(
		f("Sesja 7c1e5a90-3b1f-4c0e-9a51-0d6f2b8e1a11 wygasła", {}),
		"Sesja <id> wygasła",
		"identyfikator GUID"
	)
	rowne(f("linia1\nlinia2\t\tkoniec", {}), "linia1 linia2 koniec", "znaki sterujące")
	rowne(f(42, {}), "42", "liczba zamiast tekstu")
	rowne(f("bez zmian: Script:7", { 5, false, "" }), "bez zmian: Script:7", "śmieci na liście nazw")
	rowne(#f(string.rep("y", 2000), {}), 600, "bardzo długi komunikat jest ucinany")
end)

test("teksty do zapisu: UTF-8 i długość", function()
	rowne(Agregator.oczysc_tekst("a\0b\nc", 10), "a b c", "znaki sterujące → spacja")
	rowne(Agregator.oczysc_tekst("ab\255cd", 10), "ab?cd", "niepoprawny UTF-8 → znak zapytania")
	rowne(Agregator.oczysc_tekst(12, 5), "12", "liczba")
	rowne(Agregator.oczysc_tekst("abcdef", 3), "abc", "ucięcie ASCII")
	local polski = "zażółć gęślą jaźń"
	for limit = 1, #polski do
		local wynik = Agregator.oczysc_tekst(polski, limit)
		sprawdz(#wynik <= limit, "limit " .. limit .. ": za długi wynik")
		sprawdz(utf8.len(wynik) ~= nil, "limit " .. limit .. ": ucięty w środku znaku")
		rowne(string.sub(polski, 1, #wynik), wynik, "limit " .. limit .. ": wynik jest początkiem tekstu")
		sprawdz(#wynik >= limit - 1, "limit " .. limit .. ": ucięto więcej niż jeden znak")
	end
	rowne(Agregator.klucz_tekstowy(5), "5", "klucz z liczby")
	rowne(Agregator.klucz_tekstowy(1234567890123), "1234567890123", "duży numer produktu bez notacji wykładniczej")
	rowne(Agregator.klucz_tekstowy("abc"), "abc", "klucz z tekstu")
	rowne(Agregator.klucz_tekstowy(""), "?", "pusty klucz")
	rowne(#Agregator.klucz_tekstowy(string.rep("k", 80)), 50, "klucz najwyżej 50 bajtów")
end)

-- =========================================================================== zdarzenia → kubełek
test("zdarzenia jednej godziny", function()
	local czas, zegar = nowy_zegar(T0 + 5)
	local a = Agregator.nowy(zegar)
	rowne(a:ma_dane(), false, "nowy agregator jest pusty")
	a:start_serwera()
	a:sesja_start()
	a:sesja_start()
	a:sesja_start()
	czas.t = T0 + 65
	a:probka_ccu(3)
	a:probka_ccu(7) -- druga próbka w tej samej minucie: tylko do ccu_max
	czas.t = T0 + 125
	a:probka_ccu(2)
	a:sesja_koniec(30)
	a:sesja_koniec(400)
	a:sesja_koniec(4000)
	a:zakup(111, 49, "Worek złota")
	a:zakup(111, 49, "Inna nazwa")
	a:zakup("222", 199, nil)
	a:blad("Server.Walka:42: indeks 7", {})
	a:blad("Server.Walka:42: indeks 9", {})
	a:blad("Server.Pety:7: nil", {})
	a:blad_bez_tresci()
	a:zdarzenie("quest")
	a:zdarzenie("quest")
	a:zdarzenie("zloto", 250)
	a:zdarzenie("zloto", 50)
	rowne(a:lejek(1, "Wejście"), true, "krok 1 przyjęty")
	a:lejek(1, "Wejście")
	a:lejek(2, "Bohater")
	rowne(a:lejek(0), false, "krok 0 odrzucony")
	rowne(a:lejek(101), false, "krok 101 odrzucony")
	rowne(a:lejek(1.5), false, "krok ułamkowy odrzucony")
	rowne(a:lejek("x"), false, "krok tekstowy odrzucony")
	a:zamkniecie("ServerEmpty")
	a:zamkniecie(nil)
	rowne(a:ma_dane(), true, "są dane do zapisu")

	local partie = a:zdejmij()
	rowne(#partie, 1, "jedna godzina")
	rowne(partie[1].klucz, GODZINA_05, "klucz godziny")
	local k = partie[1].kubelek
	rowne(k.wersja, 1, "wersja")
	rowne(k.t, T0, "początek godziny")
	rowne(k.zaktualizowano, T0 + 125, "czas ostatniego zdarzenia")
	rowne(k.serwery, 1, "serwer policzony raz")
	rowne(k.zapisy, 1, "jeden zapis")
	rowne(k.starty, 1, "start serwera")
	rowne(k.sesje, 3, "sesje")
	rowne(k.sesje_zakonczone, 3, "zakończone sesje")
	rowne(k.sekundy_gry, 4430, "sekundy gry")
	rowne(k.dlugosci.do_1, 1, "sesja do minuty")
	rowne(k.dlugosci.do_15, 1, "sesja 5–15 min")
	rowne(k.dlugosci.ponad_60, 1, "sesja ponad godzinę")
	rowne(k.ccu_max, 7, "najwięcej graczy naraz")
	rowne(k.ccu_suma, 5, "suma próbek (jedna na minutę)")
	rowne(k.ccu_probki, 2, "liczba próbek")
	rowne(#k.ccu_minuty, 60, "60 minut")
	rowne(k.ccu_minuty[1], 0, "minuta 0")
	rowne(k.ccu_minuty[2], 3, "minuta 1")
	rowne(k.ccu_minuty[3], 2, "minuta 2")
	rowne(k.robuxy, 297, "Robuxy razem")
	rowne(k.zakupy["111"].n, 2, "zakupy produktu 111")
	rowne(k.zakupy["111"].robuxy, 98, "Robuxy produktu 111")
	rowne(k.zakupy["111"].nazwa, "Worek złota", "pierwsza nazwa produktu zostaje")
	rowne(k.zakupy["222"].n, 1, "produkt z kluczem tekstowym")
	rowne(k.zakupy["222"].nazwa, "", "produkt bez nazwy")
	rowne(k.bledy_n, 4, "wszystkie błędy")
	local sygnatura = Agregator.sygnatura("Server.Walka:42: indeks 7")
	rowne(k.bledy[sygnatura].n, 2, "ten sam błąd z inną liczbą")
	rowne(k.bledy[sygnatura].komunikat, "Server.Walka:42: indeks 7", "komunikat pierwszego wystąpienia")
	rowne(k.bledy[Agregator.INNE].n, 1, "błąd bez treści")
	rowne(suma_n(k.bledy), k.bledy_n, "suma wpisów = licznik błędów")
	rowne(k.zdarzenia.quest, 2, "licznik zdarzeń")
	rowne(k.zdarzenia.zloto, 300, "suma wartości zdarzeń")
	rowne(k.lejek["1"].n, 2, "krok 1 lejka")
	rowne(k.lejek["1"].nazwa, "Wejście", "nazwa kroku")
	rowne(k.lejek["2"].n, 1, "krok 2 lejka")
	rowne(k.zamkniecia.ServerEmpty, 1, "powód zamknięcia")
	rowne(k.zamkniecia.Unknown, 1, "zamknięcie bez powodu")
	for nazwa, slownik in pairs({ zakupy = k.zakupy, bledy = k.bledy, zdarzenia = k.zdarzenia, lejek = k.lejek }) do
		for klucz in pairs(slownik) do
			rowne(type(klucz), "string", "klucz słownika " .. nazwa .. " jest tekstem")
		end
	end
	rowne(a:ma_dane(), false, "po zdjęciu nic nie czeka")
	rowne(#a:zdejmij(), 0, "drugie zdjęcie jest puste")

	-- nowe zdarzenia w tej samej godzinie i w następnej
	czas.t = T0 + 3590
	a:sesja_start()
	czas.t = T0 + 3605
	a:sesja_start()
	a:sesja_start()
	local dalej = a:zdejmij()
	rowne(#dalej, 2, "dwie godziny")
	rowne(dalej[1].klucz, GODZINA_05, "starsza godzina pierwsza")
	rowne(dalej[2].klucz, "g_20261113_06", "nowsza godzina druga")
	rowne(dalej[1].kubelek.sesje, 1, "sesja przed pełną godziną")
	rowne(dalej[2].kubelek.sesje, 2, "sesje po pełnej godzinie")
	rowne(dalej[1].kubelek.serwery, 0, "serwer nie liczy się drugi raz w tej samej godzinie")
	rowne(dalej[2].kubelek.serwery, 1, "w nowej godzinie liczy się znowu")
end)

test("zegar musi być funkcją", function()
	local ok = pcall(function()
		Agregator.nowy(nil)
	end)
	rowne(ok, false, "brak zegara to błąd")
end)

-- =========================================================================== scalanie
local function przykladowy_przyrost()
	local czas, zegar = nowy_zegar(T0 + 65)
	local a = Agregator.nowy(zegar)
	a:start_serwera()
	a:sesja_start()
	a:sesja_start()
	a:probka_ccu(4)
	a:sesja_koniec(120)
	a:zakup(111, 49, "Worek złota")
	a:blad("Server.Walka:42: nil", {})
	a:zdarzenie("quest")
	a:lejek(1, "Wejście")
	czas.t = T0 + 130
	a:probka_ccu(6)
	return a:zdejmij()[1].kubelek
end

test("scalanie kubełków", function()
	local przyrost = przykladowy_przyrost()
	local przed = kopia(przyrost)
	local pierwszy = Agregator.scal(nil, przyrost)
	sprawdz(takie_same(przyrost, przed), "scal nie zmienia przyrostu")
	sprawdz(takie_same(pierwszy, przyrost), "nil + przyrost = przyrost")
	sprawdz(takie_same(Agregator.scal(nil, przyrost), pierwszy), "powtórzone wywołanie daje ten sam wynik")

	local kopia_pierwszego = kopia(pierwszy)
	local drugi = Agregator.scal(pierwszy, przyrost) -- drugi serwer z takim samym przyrostem
	sprawdz(takie_same(pierwszy, kopia_pierwszego), "scal nie zmienia zapisanego kubełka")
	sprawdz(takie_same(przyrost, przed), "scal nadal nie zmienia przyrostu")
	rowne(drugi.t, T0, "początek godziny")
	rowne(drugi.sesje, 4, "sesje się sumują")
	rowne(drugi.sesje_zakonczone, 2, "zakończone sesje")
	rowne(drugi.sekundy_gry, 240, "sekundy gry")
	rowne(drugi.serwery, 2, "dwa serwery")
	rowne(drugi.zapisy, 2, "dwa zapisy")
	rowne(drugi.starty, 2, "dwa starty")
	rowne(drugi.ccu_max, 6, "ccu_max to największa wartość, nie suma")
	rowne(drugi.ccu_suma, 20, "suma próbek")
	rowne(drugi.ccu_probki, 4, "liczba próbek")
	rowne(drugi.ccu_minuty[2], 8, "minuta 1: gracze obu serwerów")
	rowne(drugi.ccu_minuty[3], 12, "minuta 2: gracze obu serwerów")
	rowne(#drugi.ccu_minuty, 60, "60 minut po scaleniu")
	rowne(drugi.robuxy, 98, "Robuxy")
	rowne(drugi.zakupy["111"].n, 2, "zakupy produktu")
	rowne(drugi.zakupy["111"].robuxy, 98, "Robuxy produktu")
	rowne(drugi.zakupy["111"].nazwa, "Worek złota", "nazwa produktu")
	rowne(drugi.bledy_n, 2, "błędy")
	rowne(suma_n(drugi.bledy), 2, "wpisy błędów")
	rowne(drugi.zdarzenia.quest, 2, "zdarzenia")
	rowne(drugi.lejek["1"].n, 2, "lejek")
	rowne(drugi.dlugosci.do_5, 2, "rozkład długości sesji")
	rowne(drugi.zaktualizowano, T0 + 130, "czas ostatniego zdarzenia")
	rowne(drugi.wersja, 1, "wersja")

	-- wynik nie dzieli tabel z argumentami
	drugi.zakupy["111"].n = 999
	drugi.ccu_minuty[2] = 999
	rowne(przyrost.zakupy["111"].n, 1, "zmiana wyniku nie rusza przyrostu (słownik)")
	rowne(przyrost.ccu_minuty[2], 4, "zmiana wyniku nie rusza przyrostu (minuty)")
	rowne(pierwszy.zakupy["111"].n, 1, "zmiana wyniku nie rusza zapisanego kubełka")
end)

test("scalanie znosi uszkodzone i nowsze dane", function()
	local przyrost = przykladowy_przyrost()
	for _, smiec in ipairs({ "tekst", 5, true }) do
		local wynik = Agregator.scal(smiec, przyrost)
		rowne(wynik.sesje, 2, "śmieć zamiast kubełka (" .. type(smiec) .. ")")
	end
	local zepsuty = {
		sesje = "dużo", robuxy = -50, zakupy = 5, bledy = { a = "zle", [7] = { n = 1 } }, ccu_minuty = "x",
		ccu_max = -3, t = -5, lejek = { ["1"] = 3 },
	}
	local wynik = Agregator.scal(zepsuty, przyrost)
	rowne(wynik.sesje, 2, "tekst zamiast liczby liczy się jak zero")
	rowne(wynik.robuxy, 49, "ujemna liczba liczy się jak zero")
	rowne(wynik.ccu_max, 6, "ujemne ccu_max")
	rowne(wynik.t, T0, "początek godziny z przyrostu")
	rowne(wynik.zakupy["111"].n, 1, "zepsuty słownik zakupów")
	rowne(wynik.bledy.a, nil, "wpis błędu, który nie jest tabelą, przepada")
	rowne(wynik.bledy[7], nil, "klucz liczbowy przepada")

	local nowszy = { wersja = 2, t = T0, sesje = 1, nowe_pole = { x = 1 }, nowy_licznik = 9 }
	local z_nowszym = Agregator.scal(nowszy, przyrost)
	rowne(z_nowszym.wersja, 2, "wersja nie cofa się")
	rowne(z_nowszym.sesje, 3, "znane pola się sumują")
	rowne(z_nowszym.nowe_pole.x, 1, "nieznane pole (tabela) przechodzi")
	rowne(z_nowszym.nowy_licznik, 9, "nieznane pole (liczba) przechodzi")

	local stary = Agregator.scal(nil, przyrost)
	stary.zakupy["111"].nazwa = "Stara nazwa"
	local zmieniony = kopia(przyrost)
	zmieniony.zakupy["111"].nazwa = "Nowa nazwa"
	rowne(Agregator.scal(stary, zmieniony).zakupy["111"].nazwa, "Nowa nazwa", "nowsza nazwa produktu wygrywa")
	zmieniony.zakupy["111"].nazwa = ""
	rowne(Agregator.scal(stary, zmieniony).zakupy["111"].nazwa, "Stara nazwa", "pusta nazwa nie kasuje starej")
end)

-- =========================================================================== przycinanie
test("przycinanie słowników", function()
	local produkty = {}
	for i = 1, 70 do
		produkty["p" .. string.format("%03d", i)] = { n = i, robuxy = i * 10, nazwa = "Produkt " .. i }
	end
	rowne(Agregator.przytnij(produkty, 60), 10, "dziesięć wpisów ponad limit")
	rowne(ile_kluczy(produkty), 61, "limit + wpis „_inne”")
	rowne(produkty.p001, nil, "najmniejszy wpis przeniesiony")
	rowne(produkty.p010, nil, "dziesiąty najmniejszy przeniesiony")
	rowne(produkty.p011.n, 11, "jedenasty został")
	rowne(produkty.p070.n, 70, "największy został")
	rowne(produkty[Agregator.INNE].n, 55, "suma n przeniesionych (1+…+10)")
	rowne(produkty[Agregator.INNE].robuxy, 550, "suma Robuxów przeniesionych")
	rowne(produkty[Agregator.INNE].nazwa, nil, "„_inne” nie ma nazwy")
	rowne(Agregator.przytnij(produkty, 60), 0, "drugi raz nie ma czego przenosić")
	produkty.nowy = { n = 2, robuxy = 5, nazwa = "Nowy" }
	rowne(Agregator.przytnij(produkty, 60), 1, "nowy mały wpis wypada")
	rowne(produkty[Agregator.INNE].n, 57, "„_inne” rośnie")
	rowne(produkty[Agregator.INNE].robuxy, 555, "„_inne” rośnie (Robuxy)")

	local remis = { b = { n = 1 }, a = { n = 1 }, c = { n = 1 }, d = { n = 1 } }
	Agregator.przytnij(remis, 2)
	sprawdz(remis.a ~= nil and remis.b ~= nil, "przy remisie zostają klucze wcześniejsze alfabetycznie")
	sprawdz(remis.c == nil and remis.d == nil, "przy remisie wypadają klucze późniejsze")
	rowne(remis[Agregator.INNE].n, 2, "remis: suma przeniesionych")

	local liczby = { x = 5, y = 1, z = 3 }
	Agregator.przytnij(liczby, 2)
	rowne(liczby.x, 5, "słownik liczb: największa zostaje")
	rowne(liczby.z, 3, "słownik liczb: druga zostaje")
	rowne(liczby.y, nil, "słownik liczb: najmniejsza wypada")
	rowne(liczby[Agregator.INNE], 1, "słownik liczb: „_inne” to liczba")

	local maly = { a = { n = 1 } }
	rowne(Agregator.przytnij(maly, 5), 0, "poniżej limitu nic się nie dzieje")
	rowne(maly[Agregator.INNE], nil, "poniżej limitu nie powstaje „_inne”")
end)

test("lawina różnych błędów nie rozdyma kubełka", function()
	local _, zegar = nowy_zegar(T0 + 10)
	local a = Agregator.nowy(zegar)
	for i = 1, 500 do
		a:blad("Server." .. nazwa_literowa(i) .. ":1: blad", {})
	end
	local k = a:zdejmij()[1].kubelek
	rowne(k.bledy_n, 500, "wszystkie błędy policzone")
	rowne(suma_n(k.bledy), 500, "suma wpisów = licznik błędów")
	sprawdz(ile_kluczy(k.bledy) <= Agregator.LIMITY.bledy + 1, "najwyżej limit sygnatur + „_inne”")
	sprawdz(k.bledy[Agregator.INNE] ~= nil, "nadmiar trafił do „_inne”")

	local b = Agregator.nowy(zegar)
	for i = 1, 300 do
		b:zdarzenie("zdarzenie_" .. nazwa_literowa(i), 2)
	end
	for i = 1, 100 do
		b:zakup(i, 10, "Produkt")
	end
	local kb = b:zdejmij()[1].kubelek
	sprawdz(ile_kluczy(kb.zdarzenia) <= Agregator.LIMITY.zdarzenia + 1, "zdarzenia: limit kluczy")
	local suma = 0
	for _, wartosc in pairs(kb.zdarzenia) do
		suma += wartosc
	end
	rowne(suma, 600, "zdarzenia: suma zachowana")
	sprawdz(ile_kluczy(kb.zakupy) <= Agregator.LIMITY.zakupy + 1, "zakupy: limit kluczy")
	rowne(suma_n(kb.zakupy), 100, "zakupy: liczba zachowana")
	rowne(kb.robuxy, 1000, "zakupy: Robuxy zachowane")
end)

-- =========================================================================== nieudany zapis
test("przyrost wraca po nieudanym zapisie", function()
	local czas, zegar = nowy_zegar(T0 + 10)
	local a = Agregator.nowy(zegar)
	a:sesja_start()
	a:zakup(1, 10, "A")
	local partia = a:zdejmij()[1]
	a:sesja_start() -- w czasie nieudanego zapisu przyszły nowe zdarzenia
	a:zakup(1, 5, "A")
	a:oddaj(partia.klucz, partia.kubelek)
	local razem = a:zdejmij()
	rowne(#razem, 1, "jedna godzina")
	rowne(razem[1].kubelek.sesje, 2, "sesje stare + nowe")
	rowne(razem[1].kubelek.robuxy, 15, "Robuxy stare + nowe")
	rowne(razem[1].kubelek.zakupy["1"].n, 2, "zakupy stare + nowe")
	rowne(razem[1].kubelek.serwery, 1, "serwer nadal policzony raz")
	rowne(razem[1].kubelek.zapisy, 1, "to wciąż jeden zapis")
	a:oddaj(razem[1].klucz, razem[1].kubelek) -- oddanie, gdy nic nowego nie przyszło
	rowne(a:zdejmij()[1].kubelek.sesje, 2, "oddany przyrost wraca bez zmian")

	-- zapis nie działa dłużej niż 48 godzin: najstarsze godziny przepadają, pamięć nie rośnie bez końca
	local b = Agregator.nowy(zegar)
	for godzina = 0, 59 do
		czas.t = T0 + godzina * 3600
		b:sesja_start()
	end
	local zalegle = b:zdejmij()
	rowne(#zalegle, 48, "najwyżej 48 oczekujących godzin")
	rowne(b.utracone_godziny, 12, "porzucone godziny są policzone")
	rowne(zalegle[1].klucz, Agregator.klucz_godziny(T0 + 12 * 3600), "zostają najnowsze godziny")
end)

test("wpis stanu modułu", function()
	local s1 = Agregator.scal_stan(nil, 1000)
	rowne(s1.starty, 1, "pierwszy start")
	rowne(s1.pierwszy_start, 1000, "czas pierwszego startu")
	rowne(s1.ostatni_start, 1000, "czas ostatniego startu")
	rowne(s1.wersja, 1, "wersja")
	local s2 = Agregator.scal_stan(s1, 2000)
	rowne(s2.starty, 2, "drugi start")
	rowne(s2.pierwszy_start, 1000, "pierwszy start się nie zmienia")
	rowne(s2.ostatni_start, 2000, "ostatni start rośnie")
	rowne(s1.starty, 1, "argument nietknięty")
	rowne(Agregator.scal_stan("smiec", 3000).starty, 1, "śmieć zamiast wpisu")
	local s4 = Agregator.scal_stan({ wersja = 3, starty = 9, pierwszy_start = 500, ostatni_start = 5000 }, 4000)
	rowne(s4.wersja, 3, "wersja nie cofa się")
	rowne(s4.starty, 10, "licznik startów")
	rowne(s4.pierwszy_start, 500, "pierwszy start zostaje")
	rowne(s4.ostatni_start, 5000, "ostatni start nie cofa się")
end)

-- =========================================================================== magazyn (atrapy w pamięci)
test("dwa serwery piszą do tej samej godziny", function()
	local _, zegar = nowy_zegar(T0 + 30)
	local sklad = Magazyn.w_pamieci()
	local mapa = Magazyn.mapa_w_pamieci()
	local function serwer(id)
		local agregator = Agregator.nowy(zegar)
		local magazyn = Magazyn.nowy({
			agregator = agregator, magazyn = sklad, mapa = mapa, zegar = zegar, czekaj = cisza, log = cisza,
			id_serwera = id,
		})
		return agregator, magazyn
	end
	local a1, m1 = serwer("serwer-1")
	local a2, m2 = serwer("serwer-2")
	a1:sesja_start()
	a1:zakup(5, 100, "X")
	a2:sesja_start()
	a2:sesja_start()
	local ok, zapisane, nieudane = m1:zapisz()
	rowne(ok, true, "zapis pierwszego serwera")
	rowne(zapisane, 1, "jeden kubełek zapisany")
	rowne(nieudane, 0, "nic nie wróciło")
	rowne(m2:zapisz(), true, "zapis drugiego serwera")
	local wpis = sklad:GetAsync(GODZINA_05)
	rowne(wpis.sesje, 3, "sesje obu serwerów")
	rowne(wpis.serwery, 2, "dwa serwery")
	rowne(wpis.zapisy, 2, "dwa zapisy")
	rowne(wpis.robuxy, 100, "Robuxy")
	rowne(m1:zapisz(), true, "zapis bez danych też się udaje")
	rowne(sklad.zapisy, 2, "pusty zapis nie dotyka magazynu")
	rowne(m1.zapisane_kubelki, 1, "licznik zapisanych kubełków")
	rowne(m1.ostatni_udany_zapis, T0 + 30, "czas udanego zapisu")

	rowne(m1:zapisz_stan(), true, "wpis stanu")
	m2:zapisz_stan()
	rowne(sklad:GetAsync(Magazyn.KLUCZ_STANU).starty, 2, "dwa starty serwerów")

	rowne(m1:puls({ gracze = 4, pamiec_mb = 900, fps = 59.5, bledy = 2, miejsce = 1, wersja_miejsca = 7 }), true, "puls")
	local zywy = mapa.dane["serwer-1"]
	rowne(zywy.wartosc.gracze, 4, "gracze na serwerze")
	rowne(zywy.wartosc.od, T0 + 30, "start serwera")
	rowne(zywy.wartosc.pamiec_mb, 900, "pamięć")
	rowne(zywy.wartosc.fps, 59.5, "klatki")
	rowne(zywy.wygasa_s, 180, "wpis wygasa po 3 minutach")
	rowne(zywy.klucz_sortowania, 4, "sortowanie po liczbie graczy")
	rowne(m1:puls({}), true, "puls bez danych")
	rowne(mapa.dane["serwer-1"].wartosc.gracze, 0, "brak liczby graczy = 0")
	a1:sesja_start()
	rowne(m1:zamknij(), true, "zamknięcie zapisuje resztę")
	rowne(sklad:GetAsync(GODZINA_05).sesje, 4, "sesja zapisana przy zamknięciu")
	rowne(mapa.dane["serwer-1"], nil, "wpis na żywo usunięty przy zamknięciu")

	local bez_mapy = Magazyn.nowy({ agregator = a2, magazyn = sklad, zegar = zegar, czekaj = cisza, log = cisza })
	rowne(bez_mapy:puls({ gracze = 1 }), false, "bez mapy nie ma pulsu")
	rowne(bez_mapy:zamknij(), true, "zamknięcie bez mapy")
	local ok_bez_opcji = pcall(function()
		Magazyn.nowy({})
	end)
	rowne(ok_bez_opcji, false, "magazyn bez agregatora to błąd")
end)

test("ponawianie zapisu i budżet", function()
	local _, zegar = nowy_zegar(T0 + 30)
	local agregator = Agregator.nowy(zegar)
	local awarie = 2
	local zepsuty = { dane = {} }
	function zepsuty:UpdateAsync(klucz, przeksztalc)
		if awarie > 0 then
			awarie -= 1
			error("DataStore request was throttled")
		end
		self.dane[klucz] = przeksztalc(self.dane[klucz])
		return self.dane[klucz]
	end
	local przerwy = {}
	local komunikaty = {}
	local magazyn = Magazyn.nowy({
		agregator = agregator, magazyn = zepsuty, zegar = zegar, proby = 3,
		czekaj = function(sekundy)
			table.insert(przerwy, sekundy)
		end,
		log = function(tekst)
			table.insert(komunikaty, tekst)
		end,
	})
	agregator:sesja_start()
	local ok, zapisane = magazyn:zapisz()
	rowne(ok, true, "trzecia próba się udała")
	rowne(zapisane, 1, "kubełek zapisany")
	rowne(#przerwy, 2, "dwie przerwy między próbami")
	rowne(przerwy[1], 1, "pierwsza przerwa 1 s")
	rowne(przerwy[2], 2, "druga przerwa 2 s")
	rowne(#komunikaty, 2, "dwa ostrzeżenia w logu")
	rowne(zepsuty.dane[GODZINA_05].sesje, 1, "dane zapisane raz")

	awarie = 3 -- wszystkie próby zawodzą
	agregator:sesja_start()
	agregator:sesja_start()
	local ok2, zapisane2, nieudane2 = magazyn:zapisz()
	rowne(ok2, false, "zapis nieudany")
	rowne(zapisane2, 0, "nic nie zapisano")
	rowne(nieudane2, 1, "jeden kubełek wrócił")
	rowne(agregator:ma_dane(), true, "przyrost czeka na następny zapis")
	rowne(magazyn.nieudane_zapisy, 1, "licznik nieudanych zapisów")
	sprawdz(magazyn.ostatni_blad ~= nil, "ostatni błąd zapamiętany")
	awarie = 0
	rowne(magazyn:zapisz(), true, "następny zapis się udaje")
	rowne(zepsuty.dane[GODZINA_05].sesje, 3, "nic nie zginęło i nic się nie podwoiło")

	-- budżet żądań wyczerpany: zwykły zapis czeka, zamknięcie zapisuje mimo wszystko
	local sklad = Magazyn.w_pamieci()
	local budzet = 0
	local oszczedny = Magazyn.nowy({
		agregator = agregator, magazyn = sklad, zegar = zegar, czekaj = cisza, log = cisza,
		budzet = function()
			return budzet
		end,
	})
	agregator:sesja_start()
	rowne(oszczedny:zapisz(), false, "bez budżetu nie zapisujemy")
	rowne(sklad.zapisy, 0, "magazyn nietknięty")
	rowne(agregator:ma_dane(), true, "dane czekają")
	rowne(oszczedny:zamknij(), true, "zamknięcie zapisuje mimo braku budżetu")
	rowne(sklad.zapisy, 1, "zapis przy zamknięciu")
	budzet = 5
	agregator:sesja_start()
	rowne(oszczedny:zapisz(), true, "z budżetem zapis działa")
end)

-- =========================================================================== źródła (atrapy usług)
local function atrapy_uslug()
	local gracze = {}
	local Players = { PlayerAdded = sygnal(), PlayerRemoving = sygnal() }
	function Players:GetPlayers()
		local lista = {}
		for i, gracz in ipairs(gracze) do
			lista[i] = gracz
		end
		return lista
	end
	local Stats = {}
	function Stats:GetTotalMemoryUsageMb()
		return 1234.4
	end
	local uslugi = {
		Players = Players,
		ScriptContext = { Error = sygnal() },
		RunService = { Heartbeat = sygnal() },
		Stats = Stats,
	}
	return uslugi, gracze
end

test("sesje, błędy i próbki z usług gry", function()
	local czas, zegar = nowy_zegar(T0 + 30)
	local stoper = { t = 100 }
	local agregator = Agregator.nowy(zegar)
	local uslugi, gracze = atrapy_uslug()
	local zrodla = Zrodla.nowe({
		agregator = agregator, zegar = zegar, uslugi = uslugi,
		stoper = function()
			return stoper.t
		end,
	})
	local jan = { Name = "Jan_Kowalski", DisplayName = "Janek", Parent = uslugi.Players }
	gracze[1] = jan -- gracz, który był na serwerze przed startem telemetrii
	zrodla:start()
	zrodla:start() -- drugie wywołanie nic nie podpina
	local ola = { Name = "Ola123", DisplayName = "Ola123", Parent = uslugi.Players }
	table.insert(gracze, ola)
	uslugi.Players.PlayerAdded:Fire(ola)
	uslugi.Players.PlayerAdded:Fire(ola) -- powtórzone zdarzenie nie liczy drugiej sesji

	czas.t = T0 + 120
	uslugi.ScriptContext.Error:Fire("Workspace.Jan_Kowalski.Miecz:12: Janek nie ma miecza 123456", "ślad", nil)
	for _ = 1, 120 do
		uslugi.RunService.Heartbeat:Fire(0.016)
	end
	stoper.t = 102
	local stan = zrodla:probka()
	rowne(stan.gracze, 2, "gracze na serwerze")
	rowne(stan.fps, 60, "klatki serwera na sekundę")
	rowne(stan.pamiec_mb, 1234, "pamięć serwera")
	rowne(stan.bledy, 1, "błędy od startu")
	stoper.t = 102.5
	rowne(zrodla:probka().fps, nil, "za krótki pomiar klatek nie daje wyniku")

	czas.t = T0 + 150
	table.remove(gracze, 2)
	ola.Parent = nil
	uslugi.Players.PlayerRemoving:Fire(ola)
	uslugi.Players.PlayerRemoving:Fire(ola) -- powtórzone wyjście nic nie zmienia
	uslugi.ScriptContext.Error:Fire("Ola123 rozłączona w trakcie zapisu", "", nil) -- błąd tuż po wyjściu gracza

	czas.t = T0 + 210
	table.remove(gracze, 1)
	jan.Parent = nil -- gracz zniknął bez zdarzenia wyjścia
	rowne(zrodla:probka().gracze, 0, "nikogo nie ma")

	local k = agregator:zdejmij()[1].kubelek
	rowne(k.sesje, 2, "dwie sesje")
	rowne(k.sesje_zakonczone, 2, "obie zakończone")
	rowne(k.sekundy_gry, 120 + 180, "długości sesji")
	rowne(k.ccu_max, 2, "najwięcej graczy naraz")
	rowne(k.bledy_n, 2, "dwa błędy")
	local komunikaty = {}
	for _, wpis in pairs(k.bledy) do
		komunikaty[wpis.komunikat] = wpis.n
	end
	rowne(komunikaty["Workspace.<gracz>.Miecz:12: <gracz> nie ma miecza <n>"], 1, "błąd bez nazw gracza i długiej liczby")
	rowne(komunikaty["<gracz> rozłączona w trakcie zapisu"], 1, "nazwa gracza wycięta także po jego wyjściu")

	-- zamknięcie serwera domyka otwarte sesje; po stop() zdarzenia nie są już liczone
	local ewa = { Name = "Ewa_Nowak", DisplayName = "Ewa_Nowak", Parent = uslugi.Players }
	table.insert(gracze, ewa)
	uslugi.Players.PlayerAdded:Fire(ewa)
	czas.t = T0 + 270
	zrodla:zamknij_sesje()
	zrodla:zamknij_sesje()
	zrodla:stop()
	uslugi.Players.PlayerAdded:Fire({ Name = "Po_Stopie", DisplayName = "Po_Stopie", Parent = uslugi.Players })
	uslugi.ScriptContext.Error:Fire("błąd po zatrzymaniu", "", nil)
	local koniec = agregator:zdejmij()[1].kubelek
	rowne(koniec.sesje, 1, "sesja przed zamknięciem")
	rowne(koniec.sesje_zakonczone, 1, "sesja domknięta raz")
	rowne(koniec.sekundy_gry, 60, "długość domkniętej sesji")
	rowne(koniec.bledy_n, 0, "po stop() błędy nie są liczone")
end)

test("lawina błędów w jednej minucie", function()
	local _, zegar = nowy_zegar(T0 + 30)
	local agregator = Agregator.nowy(zegar)
	local uslugi = atrapy_uslug()
	local zrodla = Zrodla.nowe({ agregator = agregator, zegar = zegar, uslugi = uslugi, stoper = zegar })
	zrodla:start()
	for _ = 1, 100 do
		uslugi.ScriptContext.Error:Fire("Server.Petla:5: ten sam blad", "", nil)
	end
	zrodla:blad("zgłoszony ręcznie")
	local k = agregator:zdejmij()[1].kubelek
	rowne(k.bledy_n, 101, "wszystkie błędy policzone")
	rowne(k.bledy[Agregator.sygnatura("Server.Petla:5: ten sam blad")].n, 60, "60 pierwszych z treścią")
	rowne(k.bledy[Agregator.INNE].n, 41, "reszta bez treści")
	rowne(zrodla.bledy_razem, 101, "licznik błędów od startu")
	local ok = pcall(function()
		Zrodla.nowe({})
	end)
	rowne(ok, false, "źródła bez agregatora to błąd")
end)

-- =========================================================================== tylko w Roblox Studio: zapis jako JSON
-- Data Store zapisuje wartość jako JSON. Sprawdzamy, że kubełek przechodzi tę drogę bez strat: minuty zostają
-- listą 60 liczb, słowniki słownikami, a kubełek po odczycie nadal da się scalić.
local HttpService = game and game:GetService("HttpService")
if HttpService then
	test("kubełek jako JSON (Roblox Studio)", function()
		local przyrost = przykladowy_przyrost()
		local zapis = HttpService:JSONEncode(Agregator.scal(nil, przyrost))
		sprawdz(#zapis < 4000, "mały kubełek ma poniżej 4 KB (jest " .. #zapis .. " bajtów)")
		local odczyt = HttpService:JSONDecode(zapis)
		rowne(#odczyt.ccu_minuty, 60, "minuty po odczycie")
		rowne(odczyt.zakupy["111"].n, 1, "słownik zakupów po odczycie")
		local razem = Agregator.scal(odczyt, przyrost)
		rowne(razem.sesje, 4, "scalenie po odczycie")
		rowne(razem.ccu_minuty[2], 8, "minuty po scaleniu z odczytem")
		rowne(razem.zakupy["111"].n, 2, "zakupy po scaleniu z odczytem")
		local pusty = HttpService:JSONDecode(HttpService:JSONEncode(Agregator.pusty_kubelek(T0)))
		rowne(Agregator.scal(pusty, przyrost).sesje, 2, "pusty kubełek po odczycie")
	end)
end

-- =========================================================================== wynik
local podsumowanie
if #niezaliczone == 0 then
	podsumowanie = "TEST TELEMETRII: " .. zaliczone .. " asercji OK"
else
	podsumowanie = "TEST TELEMETRII: NIEZALICZONE " .. #niezaliczone .. " (zaliczone " .. zaliczone .. ")\n- "
		.. table.concat(niezaliczone, "\n- ")
end
print(podsumowanie)
return podsumowanie
'''


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Generator testu telemetrii gry dla Roblox Studio")
    ap.add_argument("--wyjscie", default=None, help="plik .luau do zapisania (domyślnie w katalogu tymczasowym)")
    a = ap.parse_args()
    cel = os.path.abspath(a.wyjscie or os.path.join(tempfile.gettempdir(), "bc_test_telemetrii.luau"))
    if os.path.realpath(cel).startswith(os.path.realpath(os.path.join(REPO, "src")) + os.sep):
        raise SystemExit("Nie zapisuję testu do src/ — Rojo wgrałby go do gry.")
    tresc = zbuduj()
    os.makedirs(os.path.dirname(cel), exist_ok=True)
    with open(cel, "w", encoding="utf-8", newline="\n") as f:
        f.write(tresc)
    print("Test zapisany: %s (%d linii)" % (cel, tresc.count("\n")))
    print("Uruchom w otwartym Roblox Studio:  python tools/studio_mcp.py luau \"%s\"" % cel)


if __name__ == "__main__":
    main()
