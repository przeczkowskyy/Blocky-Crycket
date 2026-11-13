# Krzywe Miasteczko — mapa v2

Komiksowy hub gry zbudowany z samych prymitywów Roblox (bloki, kliny, walce, kule) — bez siatek, tekstur i uploadów. Status: **propozycja D-025**; według propozycji v2 gry miasteczko wchodzi do rozgrywki dopiero po sprawdzeniu samej pętli, więc na razie to demo stylu i poligon narzędzi.

| Plik | Co to jest |
|---|---|
| `PROJEKT.md` | kontrakt: przykazania stylu z liczbami, paleta, skala, układ miasta, karty budynków, ujęcia kontrolne |
| `paleta.py`, `zestaw.py` | kolory i elementy wspólne (okna, drzwi, latarnie, stragany, drzewa, domy tła…) |
| `budynki/*.py` | jeden plik na budynek: `NAZWA`, `OBRYS`, `buduj(s, rnd)` — budowany wokół (0, 0, 0), frontem ku +Z |
| `generuj.py` | teren, rynek, ulice, mur, rozmieszczenie budynków, zieleń, tło → `czesci.json` (5259 części) |
| `ujecia.json` | 11 ujęć kontrolnych (te same dla Blendera i dla zrzutów ze Studio) |
| `kontrola_kolizji.luau` | sprawdzian w Studio (tylko odczyt): podłoże i kolizje budynków |
| `podglad/`, `krzywe_miasteczko_claude_v1.blend` | rendery i scena Blendera |
| `szkolenie/` | pięć opracowań, z których powstał projekt |

## Polecenia (z głównego folderu repozytorium)
```
python swiat/krzywe_miasteczko/generuj.py                                   # przebuduj czesci.json
python swiat/biblioteka/podglad.py --json swiat/krzywe_miasteczko/czesci.json --ujecia swiat/krzywe_miasteczko/ujecia.json --przesun 0,0,-700 --wyj <folder>
python tools/studio_buduj.py swiat/krzywe_miasteczko/czesci.json            # Workspace/KrzyweMiasteczko (tylko własny kontener)
python tools/studio_zrzuty.py swiat/krzywe_miasteczko/ujecia.json --przesun 0,0,-700 --wyj <folder>
python tools/studio_mcp.py luau swiat/krzywe_miasteczko/kontrola_kolizji.luau
python tools/studio_buduj.py swiat/krzywe_miasteczko/czesci.json --usun     # usuń kontener ze Studio
```

## Co sprawdzono (13.11.2026)
- Rendery w Blenderze w dwóch światłach i zrzuty z prawdziwego Roblox Studio z tych samych ujęć.
- Dwóch niezależnych krytyków (styl 7/10, projekt poziomów 6/10 dla pierwszej wersji); wprowadzono 25 z 54 uwag. Drugiej wersji krytycy nie oceniali.
- Kontrola kolizji w Studio: 1092 punkty siatki w obrębie muru mają podłoże z kolizją; bryła wielkości postaci pchana z 16 stron zatrzymuje się na każdym zamkniętym budynku i na każdym domu tła; bramy mają przejścia tam, gdzie powinny.

## Czego nie sprawdzono i czego brakuje
- Chodzenia w trybie Play z prawdziwą postacią ani wydajności na telefonie (5259 części, 56 kul, ok. 500 walców).
- W mieście nie ma prawdziwego `SpawnLocation` — żółta płyta w grupie `Spawn` tylko oznacza punkt wejścia. O zmianie spawnu decyduje Game Director.
- Budynki nie mają wnętrz; drzwi to miejsca na interakcję (części w podgrupach `_Interakcja`).
- Niezrobione uwagi krytyków: krata w bramie miejskiej (do decyzji), sekret ze schodami na dach gospody, drobne poprawki stajni, podział pierścienia ulicy podmurnej.
- Koło stoi na mapie jako budynek, ale propozycja v2 gry odradza koło fortuny — do decyzji, czy zostaje jako „koło nagród”, czy znika.
