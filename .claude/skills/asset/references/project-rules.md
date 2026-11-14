# Blocky&Crycket – zasady pipeline'u assetów

> **Uwaga (projekt gry):** kanon gry jest w sejfie `B&C/` (opis systemów poniżej NIE jest kanonem, zob. `B&C/Produkcja/Pytania otwarte.md` #5). Reguły 4 i 9 (asset ID tylko przez `AssetIds`) to propozycja D-011 w `B&C/Produkcja/Rejestr decyzji.md`: do jej zatwierdzenia nie przepinaj istniejącego kodu gry bez zgody Game Directora. Status pipeline'u: `B&C/Technika/Pipeline assetów.md`.

## Projekt
Gra Roblox: grind / incremental / RPG inspirowana *Shakes & Fidget*. Styl: kreskówkowy Roblox + akcenty pixel art.
Systemy: misje, dungeony, sklep z bronią/magią, arena, twierdza (tycoon), pety, gildie, teleport, ekwipunek.
Zespół: 2 osoby. Komunikacja: **po polsku, zwięźle**. Preferowane: gotowe, kompletne wyniki zamiast dopytywania – pytaj tylko o rzeczy nieodwracalne lub kosztowne (kredyty, publikacja).

## Kluczowe ID
| Co | Wartość |
|---|---|
| Figma – plik projektu | `BbLd4jDnvxAmOWZN1hAZQJ` (`FIGMA_FILE_KEY` w `.env`) |
| Figma – strona HUD | `HUD Buttons` (node `9:74`) |
| Figma – HUD layout 1920×1080 | `9:1571` |
| Figma – komponent przycisków `HUD Button` (property `Type`) | `9:1570` |
| Figma – `Player Panel` (ramka + XP + złoto + diamenty) | `14:145` |
| Figma – Loading Screen | `2:75`, pasek `ProgressBar / Loading` `2:2` |
| Figma – strona biblioteki assetów | `Assets Library` (tworzy ją skill, jeśli nie istnieje) |
| Roblox – moduł ID assetów | `ReplicatedStorage.AssetIds` (generowany – nie edytuj ręcznie) |

## Pipeline assetów
Każdy nowy asset graficzny przechodzi przez skill **`/asset`** (`.claude/skills/asset/SKILL.md`). Nie rób tego „na skróty”.
Źródło prawdy: **`assets/manifest.json`** – po każdym kroku aktualizuj wpis (`python tools/manifest.py upsert ...`).

## Twarde reguły
1. **Styl** – prompty zawsze w formacie „Glossy Ink” z `prompt-templates.md` (stały początek / koniec / negative 1:1), uzupełniająco `style-guide.md`. Model Higgsfield: `nano_banana_2_1`. Zawsze dołączaj `assets/refs/KeyArt_ref.jpg` jako referencję stylu.
2. **Zero tekstu w grafikach AI.** Napisy robimy natywnie (Figma / Roblox, font Luckiest Guy; drobny tekst: Pixelify Sans w Figmie, `Enum.Font.Arcade` w Roblox).
3. **Białe, jednolite tło** przy generowaniu (łatwe wycinanie), potem `tools/process_image.py`.
4. **Asset ID tylko przez `AssetIds`** – w kodzie gry `require(ReplicatedStorage.AssetIds).NazwaAssetu`. Nigdy hardcode `rbxassetid://`.
5. **Kredyty** – domyślnie 3 warianty na asset; przy batchu > 5 assetów najpierw pokaż szacunek kredytów i poczekaj na OK.
6. **Akceptacja** – dwa progi:
   - **wybór wariantu** po generowaniu (pomijany tylko z `--auto`),
   - **⛔ akceptacja przed uploadem do Roblox – ZAWSZE, bez wyjątków** (także `--auto` i batch). Pokaż finalny, obrobiony plik (+ podgląd z Figmy) i czekaj na wyraźne „tak”. Bez zgody: `status=awaiting_approval` i stop. Zgodę zapisuje `python tools/manifest.py approve <Name>` (z sha256 pliku) – uruchamiaj to **wyłącznie po wyraźnym „tak” użytkownika**. `tools/roblox_upload.py` odmawia uploadu bez akceptacji lub gdy plik zmienił się po akceptacji. Nie używaj `--force`.
7. **Sekrety** – nigdy nie wypisuj `ROBLOX_API_KEY` ani zawartości `.env` w odpowiedziach / logach / commitach.
8. **Nazwy assetów** – PascalCase, angielskie, jednoznaczne: `Teleport`, `IconArena`, `PetDragonBaby`, `WeaponSwordIron`. Ta sama nazwa: plik PNG, warstwa w Figmie, klucz w manifeście i w `AssetIds`.
9. **Roblox UI** – skaluj w `Scale`, obrysy `UIStroke` skalowane runtime (patrz `docs/hud_full_roblox_prompt.md`), HUD pokazywany dopiero po atrybucie `LoadingDone`.

## Kategorie i rozmiary docelowe
| Kategoria | Plik processed | Uwagi |
|---|---|---|
| `icon` (HUD, menu) | 512×512 | kwadrat, przezroczyste tło, padding 4% |
| `button` (pełny przycisk) | 512×512 | bez napisu; napis natywnie |
| `item` (broń, magia, zbroja) | 512×512 | ikona przedmiotu, lekki skos 3/4 |
| `pet` | 512×512 | front 3/4, przyjazny wyraz |
| `currency` | 256×256 | moneta / diament / żeton |
| `frame` (ramki, panele) | wymiar natywny, max 1024 | bez wypalonych wartości liczbowych |
| `background` / `keyart` | 1920×1080 lub 2752×1536 | bez wycinania tła |

## Komendy pomocnicze
```bash
python tools/process_image.py IN.png assets/processed/Name.png --category icon
python tools/roblox_upload.py check
python tools/roblox_upload.py upload assets/processed/Name.png --name Name
python tools/manifest.py status
python tools/manifest.py gen-lua > build/AssetIds.lua
```
