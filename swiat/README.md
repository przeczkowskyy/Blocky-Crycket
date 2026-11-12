# swiat/ — mapy z klocków i previzy

Źródła świata 3D gry. Zasada: **jeden plik `czesci.json` na scenę**, z którego powstają scena w Blenderze, części w Roblox Studio i model w podglądzie 3D panelu. Opis i uzasadnienie: [`B&C/Technika/Klocki — Blender i Roblox.md`](../B%26C/Technika/Klocki%20%E2%80%94%20Blender%20i%20Roblox.md). Status: propozycja D-017.

| Folder | Co to jest |
|---|---|
| `demo_lesna_baza/` | demo „Leśna baza startowa”: `generuj.py` (scena opisana kodem) → `czesci.json` (2599 części), plik Blendera, rendery w `podglad/` |
| `test_cutscenki/` | previz 9-sekundowej auto-walki 3D (Rycerz kontra Leśny Slime): `cutscenka.py`, `cutscenka_v1.mp4`, klatki |

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

## Zasady
- 1 jednostka = 1 stud; układ Roblox (Y w górę, przód −Z). Geometria klinów, walców i kul: [`panel/luau/KSZTALTY.md`](../panel/luau/KSZTALTY.md).
- Skrypt budujący rusza tylko własny kontener (atrybut `Wygenerowane`); niczego nie publikuje i nie zmienia oświetlenia.
- Rendery i klatki robocze trzymaj poza repozytorium; do repo trafiają tylko wybrane podglądy (JPG) i krótki film (MP4 H.264).
- Postacie, pety i detale organiczne to siatki (FBX/GLB) — osobna droga, wymaga zgody na upload assetów.
