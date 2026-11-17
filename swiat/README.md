# swiat/ — mapy z klocków i previzy

Źródła świata 3D gry. Zasada: **jeden plik `czesci.json` na scenę**, z którego powstają scena w Blenderze, części w Roblox Studio i model w podglądzie 3D panelu. Opis i uzasadnienie: [`B&C/Technika/Klocki — Blender i Roblox.md`](../B%26C/Technika/Klocki%20%E2%80%94%20Blender%20i%20Roblox.md). Status: propozycja D-017.

| Folder | Co to jest |
|---|---|
| `demo_lesna_baza/` | demo „Leśna baza startowa”: `generuj.py` (scena opisana kodem) → `czesci.json` (2599 części), plik Blendera, rendery w `podglad/` |
| `test_cutscenki/` | previz 9-sekundowej auto-walki 3D (Rycerz kontra Leśny Slime): `cutscenka.py`, `cutscenka_v1.mp4`, klatki |
| `biblioteka/` | wspólny kręgosłup generatorów v2: `scena.py` (układy lokalne do krzywych, pochylonych brył, prymitywy, obrys „tuszem”, cechy części, kontrola jakości) i `podglad.py` (podgląd budynku albo całej mapy w Blenderze w tle) |
| `krzywe_miasteczko/` | mapa v2 „Krzywe Miasteczko” w stylu komiksowym: `PROJEKT.md` (przykazania stylu, paleta, układ, karty budynków), `paleta.py`, `zestaw.py`, `budynki/*.py` (jeden plik na budynek), `generuj.py` → `czesci.json`, `ujecia.json`, `podglad/` |
| `las_pas/` | Las jako wąski pas (propozycja, plan z `biom_las/pas/`): `generuj.py` → `czesci.json` (8601 części, kontener `Workspace/LasPas`), `znaczniki.json`, `sprawdz.py` (kontrola offline), `podglad.py` → `podglad/` (rysunek w Pillow, bez Blendera); w Studio stoi od 16.11.2026, zrzuty w `klatki/` — README |
| `las_pas_gra/` | Skrypty gry lasu-pasa (propozycja, kontener `Workspace/LasPasGra`): potwory w przegrodach na wspólnym kodzie z `las_potwory/`, brama do Bagna po Strażniku, teleport i Kamień Powrotu, mgła, przelot kamery przy pierwszym wejściu; `zbuduj.py`, `testy/` (bez Studio i lista prób w trybie Play), `klatki/` — README |
| `bagno_pas/` | Bagno jako odcinek pasa za lasem (propozycja do akceptacji, niezbudowane w Studio): `generuj.py` → `czesci.json` (9017 części, kontener `Workspace/BagnoPas`), `znaczniki.json`, `sprawdz.py` (kontrola offline), `podglad.py` → `podglad/`; importuje moduły `las_pas/`. |
| `biomy/` | `PLAN_BIOMOW.md` — zarys biomów 2–8 (propozycja): nazwy, palety, potwory z klasami, strażnicy, poziomy w obu wariantach tempa. |
| `dzwiek_gra/` | Własne dźwięki i muzyka w grze (propozycja, kontener `Workspace/DzwiekGra`): `KatalogDzwiekow` z odcinkami arkusza efektów (`assets/audio/arkusz/`) i muzyką stref, skrypt klienta z muzyką bazaru i lasu-pasa; identyfikatory wpisuje `zbuduj.py --identyfikatory` po wgraniu plików. |
| `trening_proba/` | Training Center na próbę (propozycja, kontener `Workspace/TreningProba`): `PROJEKT.md` z sześcioma mini-grami, wspólna rama, Siła i Pancerz grywalne; o przyrostach decyduje serwer. |
| `miasteczko_bazar/` | Miasteczko jako ciasny bazar (propozycja, D-084, D-085): pierwszy blok pasa przed Lasem, sklepy z wnętrzami i sprzedawcami, portal do krain, działka, zagroda petów, tablica; `uklad.json` → `generuj.py` → `czesci.json` (4410 części, kontener `Workspace/MiasteczkoBazar`) + `znaczniki.json`, `sprawdz.py`, `podglad.py` → `podglad/` (Pillow); w Studio stoi od 17.11.2026, zrzuty w `klatki/` — README |
| `miasteczko_bazar_gra/` | Skrypty gry miasteczka-bazaru (propozycja, kontener `Workspace/MiasteczkoBazarGra`): 13 miejsc z klawiszem E (`miejsca.json`), zdarzenie `OknoMiejsca` dla okien 2D, dymki sprzedawców, portal krain, Brama Leśna, tablica z rankingiem, przejścia stare ↔ nowe miasteczko; `zbuduj.py`, `testy/`, `klatki/` — README |
| `teleport_chmury/` | Przejście przez chmury zamiast okna mapy (propozycja, D-075; kontener `Workspace/TeleportChmury`): makieta dziewięciu krain widziana z góry, wybór dotknięciem, kamera opada na gracza; `krainy.json`, `zbuduj.py`, `testy/`, `klatki/` — README |
| `test_walki_roblox/` | test cutscenki auto-walki w samym Roblox (kontener `Workspace/TestWalki`): źródła Luau, `zbuduj.py`, testy, klatki, README z pomiarami |

## Polecenia (z głównego folderu repozytorium)
```
# 1. wygeneruj scenę (zmień liczby w generuj.py → nowa wersja mapy)
python swiat/demo_lesna_baza/generuj.py

# 2. podgląd w Blenderze: rendery + plik .blend (ścieżki BEZWZGLĘDNE, Blender 5.0)
blender -b --factory-startup --python-exit-code 1 --python tools/blender/klocki.py -- ^
    --z-json C:\...\swiat\demo_lesna_baza\czesci.json --render C:\...\podglad --zapisz C:\...\scena.blend

# 3. po ręcznej edycji klocków w Blenderze: zapisz zmiany z powrotem do JSON
blender -b --factory-startup C:\...\scena.blend --python tools/blender/klocki.py -- --do-json C:\...\czesci.json

# 4. zbuduj w otwartym Roblox Studio (jeden kontener Workspace/<Nazwa>, do cofnięcia Ctrl+Z)
python tools/studio_buduj.py swiat/demo_lesna_baza/czesci.json
python tools/studio_buduj.py swiat/demo_lesna_baza/czesci.json --usun      # usuń wygenerowany kontener

# 5. pokaż na panelu: migawka + raport
python panel/narzedzia/migawka.py --tytul "…" --korzen Workspace/DemoLesnaBaza
python panel/narzedzia/raport.py dodaj --tytul "…" --opis-plik opis.md --migawka <id>
```

## Mapy v2 (biblioteka)
```
# podgląd jednego budynku (stoi na podłożu, z ludzikiem wzrostu gracza): kadry a_przod34, b_tyl34, c_bok, d_oczy, e_gora
python swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/karczma.py --wyj <folder> [--swiatlo studio]

# cała mapa: generator, rendery z własnych ujęć, budowa w Studio, zrzuty ze Studio z tych samych ujęć
python swiat/krzywe_miasteczko/generuj.py
python swiat/biblioteka/podglad.py --json swiat/krzywe_miasteczko/czesci.json --ujecia swiat/krzywe_miasteczko/ujecia.json --przesun 0,0,-700 --wyj <folder>
python tools/studio_buduj.py swiat/krzywe_miasteczko/czesci.json
python tools/studio_zrzuty.py swiat/krzywe_miasteczko/ujecia.json --przesun 0,0,-700 --wyj <folder>
```
Budynek to moduł z `NAZWA`, `OBRYS` i `buduj(s, rnd)`: powstaje wokół (0, 0, 0) frontem ku +Z, a miejsce, obrót i pochylenie nadaje `with s.uklad(...)`. `--swiatlo studio` renderuje w płaskim, szarym świetle — uczciwy test, czy bryły nie zlewają się bez cieni. Blender działa w tle, a rendery ustawiają się w kolejce.

## Zasady
- 1 jednostka = 1 stud; układ Roblox (Y w górę, przód −Z). Geometria klinów, walców i kul: [`panel/luau/KSZTALTY.md`](../panel/luau/KSZTALTY.md).
- Skrypt budujący rusza tylko własny kontener (atrybut `Wygenerowane`); niczego nie publikuje i nie zmienia oświetlenia.
- Rendery i klatki robocze trzymaj poza repozytorium; do repo trafiają tylko wybrane podglądy (JPG) i krótki film (MP4 H.264).
- Postacie, pety i detale organiczne to siatki (FBX/GLB) — osobna droga, wymaga zgody na upload assetów.
