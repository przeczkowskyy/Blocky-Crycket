#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Odczyt pomiaru prób z prawdziwymi graczami (D-128): anonimowe podsumowania sesji → tabela decyzji.

    python -B swiat/ewolucja/testy/odczyt_prob.py --fixtury <plik.json>                  # plik z rekordami (próba offline)
    python -B swiat/ewolucja/testy/odczyt_prob.py --play --studio <id>                    # magazyn w pamięci trwającej próby Play
    python -B swiat/ewolucja/testy/odczyt_prob.py --studio <id> --od 2026-11-23 --do 2026-11-30   # prawdziwy magazyn (patrz niżej)

Rekordy: magazyn `Ewolucja_Proby_v1` (ustawienia.json → zapis.magazyn_prob), klucz `RRRR-MM-DD_<losowy id>`, bez
identyfikatora i nazwy gracza. Pola: d (dzień), dl (długość sesji, s), maks (najwyższe stadium), t (czas do stadiów, −1
= nieosiągnięte), sm (śmierci), dalej (grał dalej po pierwszej śmierci), po (sekundy gry po pierwszej śmierci), leg
(wejścia do legowiska), zb (zbiory skarbu), ul (ulepszenia), tr (poziomy trofeów), bs (najwyższy pokonany stopień
bossa), war (wylosowane warianty), nowy (pierwsza sesja), dni (dni od pierwszej gry).

Prawdziwy magazyn czyta tylko Studio w trybie Edit tego miejsca i tylko wtedy, gdy człowiek włączy w Game Settings →
Security „Enable Studio Access to API Services” (skrypt niczego nie przełącza i niczego nie zapisuje — tylko
ListKeysAsync / GetAsync). Bez tego Studio odpowiada błędem, który skrypt wypisuje.
"""
import argparse
import datetime
import json
import os
import statistics
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
sys.path.append(os.path.join(REPO, "tools"))

ODCZYT = r'''
local HS = game:GetService("HttpService")
if game:GetService("RunService"):IsRunning() then return "STOP: Studio w trybie Play" end
local ok, wynik = pcall(function()
	local m = game:GetService("DataStoreService"):GetDataStore("__MAGAZYN__")
	local w = {}
	for _, dzien in HS:JSONDecode('__DNI__') do
		local strony = m:ListKeysAsync(dzien .. "_")
		while true do
			for _, k in strony:GetCurrentPage() do
				local r = m:GetAsync(k.KeyName)
				if type(r) == "table" then
					table.insert(w, r)
				end
			end
			if strony.IsFinished then break end
			strony:AdvanceToNextPageAsync()
		end
	end
	return w
end)
if not ok then
	return "BLAD: " .. tostring(wynik)
end
return HS:JSONEncode(wynik)
'''


def mediana(x):
    x = [v for v in x if v is not None]
    return statistics.median(x) if x else None


def zestawienie(rek):
    """Tabela D-128 z listy rekordów."""
    n = len(rek)
    if n == 0:
        return {"sesje": 0}
    zmarli = [r for r in rek if r.get("sm", 0) > 0]
    return {
        "sesje": n,
        "mediana_sesji_s": mediana([r.get("dl", 0) for r in rek]),
        "udzial_stadium_3": round(sum(1 for r in rek if r.get("maks", 1) >= 3) / n, 3),
        "udzial_stadium_5": round(sum(1 for r in rek if r.get("maks", 1) >= 5) / n, 3),
        "mediana_smierci": mediana([r.get("sm", 0) for r in rek]),
        "zginelo_sesji": len(zmarli),
        "gralo_dalej_po_1_smierci": round(sum(1 for r in zmarli if r.get("dalej")) / len(zmarli), 3) if zmarli else None,
        "mediana_gry_po_1_smierci_s": mediana([r.get("po", 0) for r in zmarli]),
        "udzial_powrotow_innego_dnia": round(sum(1 for r in rek if not r.get("nowy") and r.get("dni", 0) >= 1) / n, 3),
        "mediana_czasu_do_stadium_5_s": mediana([r["t"][4] for r in rek if isinstance(r.get("t"), list) and len(r["t"]) >= 5 and r["t"][4] >= 0]),
    }


def wypisz(Z):
    nazwy = [("sesje", "sesje"), ("mediana_sesji_s", "mediana długości sesji (s)"), ("udzial_stadium_3", "doszło do stadium 3"),
             ("udzial_stadium_5", "doszło do stadium 5"), ("mediana_smierci", "mediana śmierci"), ("zginelo_sesji", "sesje ze śmiercią"),
             ("gralo_dalej_po_1_smierci", "grało dalej po 1. śmierci"), ("mediana_gry_po_1_smierci_s", "mediana gry po 1. śmierci (s)"),
             ("udzial_powrotow_innego_dnia", "powroty innego dnia"), ("mediana_czasu_do_stadium_5_s", "mediana czasu do stadium 5 (s)")]
    print("Pomiar prób (D-128)")
    for k, opis in nazwy:
        v = Z.get(k)
        if isinstance(v, float) and k.startswith("udzial") or k == "gralo_dalej_po_1_smierci" and v is not None:
            v = "%.0f %%" % (v * 100)
        print("  %-34s %s" % (opis, "—" if v is None else v))


def dni(od, do):
    a = datetime.date.fromisoformat(od)
    b = datetime.date.fromisoformat(do)
    return [(a + datetime.timedelta(days=i)).isoformat() for i in range((b - a).days + 1)]


def main():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixtury")
    ap.add_argument("--play", action="store_true")
    ap.add_argument("--studio")
    ap.add_argument("--od", default=datetime.date.today().isoformat())
    ap.add_argument("--do", default=datetime.date.today().isoformat())
    a = ap.parse_args()
    if a.fixtury:
        rek = json.load(open(a.fixtury, encoding="utf-8"))
    else:
        from studio_mcp import StudioMCP
        sys.path.insert(0, PAKIET)
        import dane as DN
        mag = DN.ustawienia()["zapis"]["magazyn_prob"]
        with StudioMCP(timeout=120) as s:
            if a.play:
                kod = ('local HS = game:GetService("HttpService") local w = workspace.%s.Sygnaly.SterowanieSerwera:Invoke("proby") '
                       'local l = {} for _, r in w.rekordy do table.insert(l, r) end return HS:JSONEncode(l)') % DN.ustawienia()["kontener"]
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Server", "studio_id": a.studio})
            else:
                if "Current Studio Mode: Edit" not in s.call("get_studio_state", {"studio_id": a.studio})["text"]:
                    raise SystemExit("Studio nie jest w trybie Edit")
                kod = ODCZYT.replace("__MAGAZYN__", mag).replace("__DNI__", json.dumps(dni(a.od, a.do)))
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": a.studio})
            t = (r["text"] or "").strip()
            if r["is_error"] or t.startswith("BLAD") or t.startswith("STOP"):
                print("Odczyt nieudany:", t[:400])
                print("Jeśli to błąd dostępu: człowiek musi włączyć w Studio Game Settings → Security → "
                      "„Enable Studio Access to API Services” (skrypt tylko czyta).")
                return 1
            rek = json.loads(t)
    wypisz(zestawienie(rek))
    return 0


if __name__ == "__main__":
    sys.exit(main())
