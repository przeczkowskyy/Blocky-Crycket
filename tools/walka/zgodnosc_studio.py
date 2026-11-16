#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zgodnosc silnika walki v3: moduly Luau w Roblox Studio kontra wzorce z portu w Pythonie.

    python -B tools/walka/zgodnosc_studio.py [--studio <studio_id>]   # Studio w trybie Edit, TYLKO ODCZYT
    python -B tools/walka/zgodnosc_studio.py --sucho [--zapisz plik.luau]  # bez Studio: sklada kod i pokazuje rozmiar
    python -B tools/walka/zgodnosc_studio.py --offline                # bez Studio: te same sprawdzenia malym
                                                                      # interpreterem Luau (tools/walka/luau_mini.py)

Tryb --offline NIE zastepuje Studio (to podzbior Luau napisany w Pythonie, patrz luau_mini.py), ale lapie bledy
portu (inna kolejnosc rzutow, literowki w nazwach pol, zle indeksy) bez uruchamiania Roblox Studio.

Co robi:
  1. czyta ZRODLA modulow jako tekst z repozytorium (src/server/Walka/*.luau, src/shared/Walka/Dziennik.luau) —
     nie potrzebuje Rojo ani zsynchronizowanego miejsca i niczego nie wstawia do drzewa gry;
  2. sklada z nich jeden kawalek kodu: kazdy modul staje sie funkcja, a `require(script.Parent.X)` zamienia sie na
     wewnetrzne `wymagaj("X")` (inne uzycia `require` albo `script` w modulach przerywaja skladanie);
  3. wysyla go do Studio (execute_luau, tryb Edit). Kod w Studio: sprawdza game.PlaceId, liczy wszystkie walki
     z tools/walka/wzorce.json, porownuje skroty podpisow, sprawdza niezmienniki (Dziennik.sprawdz), powtarzalnosc
     i odrzucanie zlych wejsc. Nie tworzy instancji, nie zmienia miejsca, nie zapisuje, nie publikuje;
  4. wypisuje wynik: 4 punkty OK/BLAD, a przy roznicach pierwszy niezgodny podpis z Luau i z Pythona.

Okno Studio wybiera swiat/test_walki_roblox/cel_studio.py (jedno okno albo --studio; zawsze placeId gry).
Najpierw zaktualizuj wzorce, jesli zmieniales dane albo wzory: python -B tools/walka/wzorce.py.
"""
import argparse
import json
import os
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
MODULY = [
    ("Dane", os.path.join(REPO, "src", "server", "Walka", "Dane.luau")),
    ("Los", os.path.join(REPO, "src", "server", "Walka", "Los.luau")),
    ("Statystyki", os.path.join(REPO, "src", "server", "Walka", "Statystyki.luau")),
    ("Przeciwnicy", os.path.join(REPO, "src", "server", "Walka", "Przeciwnicy.luau")),
    ("Umiejetnosci", os.path.join(REPO, "src", "server", "Walka", "Umiejetnosci.luau")),
    ("Silnik", os.path.join(REPO, "src", "server", "Walka", "Silnik.luau")),
    ("Dziennik", os.path.join(REPO, "src", "shared", "Walka", "Dziennik.luau")),
]
WZORCE = os.path.join(TU, "wzorce.json")
WYMAGANIE = re.compile(r"require\(script\.Parent\.([A-Za-z_][A-Za-z0-9_]*)\)")

# Kod uruchamiany w Studio. __ZRODLA__ i __DANE__ wstawia Python. Format podpisu MUSI byc taki sam jak
# w tools/walka/wzorce.py (funkcja podpis).
LUAU = r'''
local HttpService = game:GetService("HttpService")
if game.PlaceId ~= __MIEJSCE__ then
	return HttpService:JSONEncode({ blad = "to nie jest miejsce gry (PlaceId " .. tostring(game.PlaceId) .. ") — przerywam" })
end

local zrodla = {}
local zaladowane = {}
local function wymagaj(nazwa)
	if zaladowane[nazwa] == nil then
		zaladowane[nazwa] = zrodla[nazwa]()
	end
	return zaladowane[nazwa]
end

__ZRODLA__

local Silnik = wymagaj("Silnik")
local Dziennik = wymagaj("Dziennik")
local W = HttpService:JSONDecode(__DANE__)

local function kopia(t)
	if type(t) ~= "table" then
		return t
	end
	local k = {}
	for a, b in t do
		k[a] = kopia(b)
	end
	return k
end

local function setne(x)
	return math.floor(x * 100 + 0.5)
end

local function podpis(w)
	local czesci = {}
	for _, z in w.dziennik do
		table.insert(czesci, string.format("%s:%s>%s:%d/%d:%d/%d@%d+%d:%s:%s:%s:%d:%d:%d:%d:%d/%d",
			z.typ, z.kto, z.cel, z.obrazenia, z.pochloniete, z.hp_gracz, z.hp_wrog,
			setne(z.t), setne(z.trwa), z.umiejetnosc, z.efekt, z.rodzaj, if z.krytyk then 1 else 0,
			z.wartosc, z.tury, z.stosy, z.mana_gracz, z.mana_wrog))
	end
	local L = w.lup
	return string.format("%s|%s|%d|%d|%d/%d/%d/%d/%d/%s|%d|%d/%d|%d/%d",
		table.concat(czesci, ","), w.wynik, w.tury, if w.bezpiecznik then 1 else 0,
		L.zloto, L.doswiadczenie, L.tokeny_krainy, L.gemy, L.shard_ewolucji, L.kraina,
		setne(w.czas), w.strony.gracz.zycie, w.strony.wrog.zycie, w.strony.gracz.mana, w.strony.wrog.mana)
end

local function skrot(napis)
	local h = 7
	for i = 1, #napis do
		h = (h * 131 + string.byte(napis, i)) % 2147483647
	end
	return h
end

local wynik = { skroty = {}, niezgodne = {}, zle = {}, bledy = {}, powtarzalne = true, odrzucone = 0, nieodrzucone = {} }
for nr, przypadek in W.przypadki do
	local ip, jp, ziarno = przypadek[1] + 1, przypadek[2] + 1, przypadek[3]
	local ok, a = pcall(Silnik.symuluj, kopia(W.postacie[ip]), kopia(W.przeciwnicy[jp]), ziarno)
	if not ok then
		table.insert(wynik.bledy, nr .. ": " .. tostring(a))
		table.insert(wynik.skroty, -1)
	else
		local dobre, opis = Dziennik.sprawdz(a)
		if not dobre then
			table.insert(wynik.zle, nr .. ": " .. tostring(opis))
		end
		local pa = podpis(a)
		local h = skrot(pa)
		table.insert(wynik.skroty, h)
		if h ~= W.skroty[nr] and #wynik.niezgodne < 3 then
			table.insert(wynik.niezgodne, { nr = nr, podpis = pa })
		end
		if nr % 10 == 0 then
			local b = Silnik.symuluj(kopia(W.postacie[ip]), kopia(W.przeciwnicy[jp]), ziarno)
			if podpis(b) ~= pa then
				wynik.powtarzalne = false
			end
		end
	end
	if nr % 100 == 0 then
		task.wait()
	end
end

-- zle wejscia: baza + jedna zmiana (tak samo jak zle_wejscie() w tools/walka/wzorce.py)
local function wartoscZnacznika(v)
	if v == "WZORCOWY_MAG" then
		return kopia(W.wzorcowa_mag)
	elseif v == "MAG_Z_TARCZA_JAKO_PRZECIWNIK" then
		local mag = kopia(W.wzorcowa_mag)
		mag.tarcza = { blok = 0.2 }
		return { postac = mag }
	elseif v == "UMIEJETNOSCI_Z_DZIURA" then
		return { [1] = "kula_ognia", [3] = "bariera" }
	end
	return kopia(v)
end
for _, spec in W.zle_wejscia do
	local gracz = kopia(W.bazy_zlych[spec.baza])
	local przeciwnik = { potwor = "lesny_slime", poziom = 5 }
	local ziarno = 1
	local v = spec.wartosc
	local specjalna = if type(v) == "table" then v.specjalna else nil
	if specjalna == "nan" then
		v = 0 / 0
	elseif specjalna == "nan_w_premii" then
		v = { cios = 0 / 0 }
	elseif specjalna == "inf" then
		v = math.huge
	elseif specjalna == "brak" then
		v = nil
	else
		v = wartoscZnacznika(v)
	end
	if spec.strona == "ziarno" then
		ziarno = v
	else
		local korzen = { gracz = gracz, przeciwnik = przeciwnik }
		if #spec.sciezka == 0 then
			korzen[spec.strona] = v
		else
			local cel = korzen[spec.strona]
			for i = 1, #spec.sciezka - 1 do
				cel = cel[spec.sciezka[i]]
			end
			cel[spec.sciezka[#spec.sciezka]] = v
		end
		gracz, przeciwnik = korzen.gracz, korzen.przeciwnik
	end
	local przeszlo, blad = pcall(Silnik.symuluj, gracz, przeciwnik, ziarno)
	if przeszlo then
		table.insert(wynik.nieodrzucone, spec.opis)
	elseif string.find(tostring(blad), "Walka: ", 1, true) then
		wynik.odrzucone += 1 -- czytelna odmowa walidacji
	else
		-- błąd wykonania (np. indeksowanie nil) to nie jest odrzucenie złych danych, tylko błąd silnika
		table.insert(wynik.nieodrzucone, spec.opis .. " [blad wykonania: " .. string.sub(tostring(blad), 1, 120) .. "]")
	end
end
return HttpService:JSONEncode(wynik)
'''


def zloz_zrodla():
    czesci = []
    for nazwa, sciezka in MODULY:
        with open(sciezka, encoding="utf-8") as f:
            tekst = f.read()
        tekst = WYMAGANIE.sub(lambda m: 'wymagaj("%s")' % m.group(1), tekst)
        bez_komentarzy = re.sub(r"--\[\[.*?\]\]", "", tekst, flags=re.S)
        bez_komentarzy = re.sub(r"--[^\n]*", "", bez_komentarzy)
        if re.search(r"\brequire\s*\(", bez_komentarzy) or re.search(r"\bscript\b", bez_komentarzy):
            sys.exit("Modul %s ma require albo script w innej postaci niz require(script.Parent.X) — nie umiem go zlozyc."
                     % nazwa)
        if re.search(r"^\s*(export\s+)?type\s", bez_komentarzy, flags=re.M):
            sys.exit("Modul %s deklaruje typy (type ...) — w zlozonym kodzie modul jest funkcja; usun deklaracje." % nazwa)
        czesci.append('zrodla["%s"] = function()\n%s\nend' % (nazwa, tekst))
    return "\n\n".join(czesci)


def dlugi_napis(tekst):
    for n in range(1, 20):
        z, k = "[" + "=" * n + "[", "]" + "=" * n + "]"
        if k not in tekst:
            return z + tekst + k
    sys.exit("nie da sie zapisac danych jako dlugiego napisu Luau")


def zloz_kod(wz):
    sys.path.insert(0, os.path.join(REPO, "swiat", "test_walki_roblox"))
    from cel_studio import MIEJSCE  # noqa: E402
    dane = {k: wz[k] for k in ("postacie", "przeciwnicy", "przypadki", "skroty", "zle_wejscia", "bazy_zlych", "wzorcowa_mag")}
    tekst_danych = json.dumps(dane, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return (LUAU.replace("__MIEJSCE__", str(MIEJSCE)).replace("__DANE__", dlugi_napis(tekst_danych))
            .replace("__ZRODLA__", zloz_zrodla()))


def uruchom_offline(kod):
    """Uruchamia ZLOZONY kod (ten sam, ktory poszedlby do Studio) w interpreterze luau_mini; game.PlaceId,
    HttpService (JSONDecode / JSONEncode) i task.wait sa podstawione. Zwraca odpowiedz jak ze Studio (slownik)."""
    sys.path.insert(0, TU)
    sys.path.insert(0, os.path.join(REPO, "swiat", "test_walki_roblox"))
    import luau_mini as LM  # noqa: E402
    from cel_studio import MIEJSCE  # noqa: E402
    interp = LM.Interpreter()
    http = LM.Tabela()
    http.set("JSONDecode", lambda _self, tekst: LM.do_luau(json.loads(tekst)))
    http.set("JSONEncode", lambda _self, v: json.dumps(LM.z_luau(v, pusta_jako_lista=True), ensure_ascii=False))
    game = LM.Tabela()
    game.set("PlaceId", float(MIEJSCE))
    game.set("GetService", lambda _self, _nazwa: http)
    task = LM.Tabela()
    task.set("wait", lambda *_: None)
    interp.globalne.z["game"] = game
    interp.globalne.z["task"] = task
    return json.loads(interp.wykonaj(kod, "zlozony")[0])


def ocen_odpowiedz(d, wz, wypisz=print):
    """Wspolne dla Studio i --offline: 4 punkty OK/BLAD. Zwraca True, gdy wszystko OK."""
    n = len(wz["przypadki"])
    rozne = [i for i in range(n) if d["skroty"][i] != wz["skroty"][i]]
    ok = True
    wypisz("1. powtarzalnosc:                %s" % ("OK" if d["powtarzalne"] else "BLAD"))
    ok &= bool(d["powtarzalne"])
    zle = d["zle"] + d["bledy"]
    wypisz("2. niezmienniki (%d walk):      %s" % (n, "OK" if not zle else "BLAD %s" % zle[:5]))
    ok &= not zle
    wypisz("3. zgodnosc z portem w Pythonie: %s" % ("OK (%d/%d identycznych dziennikow)" % (n, n) if not rozne
                                                  else "BLAD: %d roznic na %d" % (len(rozne), n)))
    ok &= not rozne
    for x in d["niezgodne"]:
        i = x["nr"] - 1
        wypisz("   przypadek %d %s\n   Luau:   %s\n   Python: %s" % (x["nr"], wz["przypadki"][i], x["podpis"][:600],
                                                                    wz["podpisy"][i][:600]))
    m = len(wz["zle_wejscia"])
    wypisz("4. odrzucanie zlych wejsc:       %s" % ("OK (%d/%d)" % (d["odrzucone"], m) if d["odrzucone"] == m
                                                  else "BLAD (%d/%d), przepuszczone: %s" % (d["odrzucone"], m, d["nieodrzucone"])))
    ok &= d["odrzucone"] == m
    return ok, {"przypadki": n, "rozne": len(rozne), "zle": len(zle), "odrzucone": d["odrzucone"], "zle_wejscia": m,
                "powtarzalne": bool(d["powtarzalne"])}


def sprawdz_offline(wz, wypisz=print):
    """Te same cztery sprawdzenia co w Studio, na tym samym zlozonym kodzie, ale w interpreterze luau_mini."""
    d = uruchom_offline(zloz_kod(wz))
    wypisz("tryb --offline (zlozony kod w interpreterze tools/walka/luau_mini.py, NIE Roblox Studio)")
    return ocen_odpowiedz(d, wz, wypisz)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Zgodnosc silnika walki v3: Luau w Studio kontra wzorce z Pythona")
    ap.add_argument("--studio", default=None, help="id okna Studio (python -B tools/studio_mcp.py studios)")
    ap.add_argument("--sucho", action="store_true", help="tylko zloz kod, bez laczenia ze Studio")
    ap.add_argument("--zapisz", default=None, help="z --sucho: zapisz zlozony kod do pliku")
    ap.add_argument("--offline", action="store_true", help="bez Studio: sprawdz modulami w interpreterze luau_mini")
    a = ap.parse_args()
    with open(WZORCE, encoding="utf-8") as f:
        wz = json.load(f)
    if a.offline:
        ok, _ = sprawdz_offline(wz)
        sys.exit(0 if ok else 1)
    kod = zloz_kod(wz)
    if a.sucho:
        print("zlozony kod: %d znakow, %d przypadkow, %d zlych wejsc" % (len(kod), len(wz["przypadki"]), len(wz["zle_wejscia"])))
        if a.zapisz:
            with open(a.zapisz, "w", encoding="utf-8", newline="\n") as f:
                f.write(kod)
            print("zapisano", a.zapisz)
        return
    sys.path.insert(0, os.path.join(REPO, "tools"))
    sys.path.insert(0, os.path.join(REPO, "swiat", "test_walki_roblox"))
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    from cel_studio import wybierz_studio  # noqa: E402
    try:
        with StudioMCP() as s:
            sid = wybierz_studio(s, a.studio)
            r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=300)
            if r["is_error"]:
                sys.exit("BLAD Studio: " + r["text"][:2000])
    except StudioError as e:
        sys.exit("BLAD Studio: %s" % e)
    d = json.loads(r["text"])
    if d.get("blad"):
        sys.exit(d["blad"])
    ok, _ = ocen_odpowiedz(d, wz)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
