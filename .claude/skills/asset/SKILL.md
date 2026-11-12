---
name: asset
description: Pipeline grafik Blocky&Crycket – generuje asset w Higgsfield wg stylu gry, obrabia (tło, trim, rozmiar), wrzuca do Figmy i do Roblox (Open Cloud + ReplicatedStorage.AssetIds) i aktualizuje assets/manifest.json. Użyj przy każdej prośbie o nową grafikę/ikonę/przycisk/peta/przedmiot/ramkę do gry, oraz dla "/asset sync" i "/asset status".
---

# /asset – pipeline grafik Blocky&Crycket

Wejście: opis od użytkownika (+ opcjonalnie `--auto`, `batch:`, `sync`, `status`).
Wyjście: gotowy asset w `assets/processed/`, w Figmie, w Roblox, wpis w manifeście, raport.

Przed startem przeczytaj: `references/project-rules.md`, `references/style-guide.md`, `references/prompt-templates.md`, `assets/manifest.json`.
Załaduj `.env` (skrypty robią to same przez python-dotenv).

---

## Tryby specjalne
- **`/asset status`** → `python tools/manifest.py status`, pokaż tabelę, koniec.
- **`/asset sync`** → przejdź od razu do kroku **8** (AssetIds), koniec.
- **`/asset approve <Name>`** → asset w statusie `awaiting_approval`: i tak **pokaż finalny obraz** jeszcze raz, potwierdź „tak” i dopiero wtedy krok 5b(3) → 6 → 7 → 8 → 9 → 10.

---

## Krok 0 – Plan (bez kosztów)
Dla każdego assetu ustal i pokaż w 1 tabeli:
| pole | przykład |
|---|---|
| `name` (PascalCase, project-rules.md reguła 8) | `IconArena` |
| `category` | `icon` / `button` / `item` / `pet` / `currency` / `frame` / `background` |
| `usage` | „przycisk HUD, prawa kolumna” |
| docelowy rozmiar | wg tabeli w project-rules.md |
| `figma_target` | node do podpięcia (jeśli zastępuje istniejący) albo `Assets Library` |
| `roblox_target` | np. `StarterGui.HUD.RightColumn.ArenaSlot.Arena.Image` albo „tylko AssetIds” |
| warianty × koszt | 3 × (koszt modelu wg Higgsfield) |

Sprawdź w manifeście, czy nazwa już istnieje → jeśli tak, to nowa **wersja** (`v2`), nie nadpisuj historii.
Batch > 5 assetów albo szacunek > 60 kredytów → **zatrzymaj się i poproś o OK**. W przeciwnym razie leć dalej.

## Krok 1 – Prompt
Złóż prompt z `references/prompt-templates.md` (szablon kategorii) + blok stylu z `style-guide.md`.
Zasady: angielski prompt, **bez tekstu w obrazie**, **czysto białe tło**, gruby czarny obrys, centralna kompozycja.
Jeśli narzędzie Higgsfield przyjmuje obraz referencyjny – dołącz 1–2 pliki z `assets/refs/` najbliższe kategorii (np. dla ikon HUD: `Shop.png`, `Pets.png`; dla walut: `Coin.png`, `Gem.png`).

## Krok 2 – Generowanie (Higgsfield MCP)
1. Sprawdź dostępne modele/parametry narzędzia `generate_image` (schemat narzędzia). Wybierz model obrazkowy o najlepszej zgodności z promptem; proporcje 1:1 (ikony) lub 16:9 (tła).
2. Wygeneruj **3 warianty** (różne seedy / lekkie wariacje opisu).
3. Odpytuj `get_generation_status` aż do `completed` (co ~5 s, max ~3 min; przy błędzie 1 ponowienie).
4. Pobierz wyniki do `assets/raw/<Name>/v<N>_<i>.png` (np. `curl -L -o ...`).
5. `python tools/manifest.py upsert <Name> category=<cat> status=generated prompt="<prompt>" raw=assets/raw/<Name>`

## Krok 3 – Akceptacja
Pokaż warianty (otwórz pliki obrazów, żeby je zobaczyć, i wypisz ścieżki) + 1 zdanie oceny każdego względem style-guide (obrys, paleta, czytelność w 64 px).
- bez `--auto`: **zapytaj, który wariant** (albo „żaden – popraw: …” → wróć do kroku 1 z poprawką).
- z `--auto`: wybierz sam wg checklisty QA ze style-guide, napisz którego i dlaczego.

## Krok 4 – Obróbka
```bash
python tools/process_image.py assets/raw/<Name>/<wybrany>.png assets/processed/<Name>.png --category <cat>
```
(tła `background` → `--bg none`). Potem **QA**: otwórz `assets/processed/<Name>.png` i sprawdź:
- tło przezroczyste, brak białej obwódki/halo, obrys nienaruszony,
- brak „dziur” wyciętych w środku (flood fill nie wszedł do środka),
- czytelne w małym rozmiarze (sprawdź też `<Name>@128.png`).
Problem z wycinaniem → spróbuj `--bg rembg` albo `--bg flood --tolerance 40`. Nie przechodź dalej z wadliwym plikiem.
`manifest.py upsert <Name> status=processed processed=assets/processed/<Name>.png`

## Krok 5 – Figma (Figma MCP)
1. `create_session` dla `FIGMA_FILE_KEY` (z `.env`), opis zadania.
2. Załaduj skill Figmy `figma-use` przed `use_figma`.
3. Cel:
   - **zastąpienie istniejącego** (np. ikona przycisku) → znajdź node docelowy (warstwa obrazu w komponencie, np. `Art (PNG)` / `Icon` / `Coin Icon (PNG)`), użyj jego ID;
   - **nowy asset** → na stronie `Assets Library` (utwórz, jeśli brak) dodaj prostokąt `<Name>` w siatce 6 kolumn, 256×256 (tła: 480×270), z podpisem nazwy (Pixelify Sans 14).
4. `upload_assets` z `nodeIds=[<id>]`, `scaleMode=FIT` → dostajesz `submitUrl`.
5. `python tools/figma_upload.py assets/processed/<Name>.png "<submitUrl>"`
6. Screenshot noda (`get_screenshot`) → szybka weryfikacja.
7. `manifest.py upsert <Name> status=in_figma figma_node=<id>`

## Krok 5b – ⛔ AKCEPTACJA PRZED ROBLOX (obowiązkowa, zawsze)
**Bez wyjątków – także w trybie `--auto` i w batchu.** Nic nie trafia do Roblox bez wyraźnej zgody użytkownika.
1. Pokaż użytkownikowi **finalny** plik `assets/processed/<Name>.png` (otwórz obraz) + podgląd `<Name>@128.png` + screenshot z Figmy (krok 5.6), jeśli asset jest podpięty w komponencie/HUD.
2. Wypisz: nazwę, kategorię, wymiary, gdzie zostanie podpięty w Roblox (`roblox_target`).
3. Zapytaj wprost: **„Akceptujesz upload `<Name>` do Roblox? (tak / popraw: … / odrzuć)”** – i **czekaj na odpowiedź**.
   - `tak` → `python tools/manifest.py approve <Name>` (zapisuje `approved_by_user`, czas i **sha256 pliku**) → krok 6.
     **Nigdy nie uruchamiaj `approve` bez wyraźnego „tak” od użytkownika w tej rozmowie** – nie wnioskuj zgody z wcześniejszych wiadomości, `--auto`, ani z akceptacji wariantu w kroku 3.
     Każda zmiana pliku po akceptacji (ponowna obróbka) unieważnia ją – upload zostanie zablokowany, trzeba pokazać i zaakceptować ponownie.
   - `popraw: …` → wróć do kroku 1 (nowy prompt) albo 4 (tylko obróbka), zależnie od uwagi; potem znowu 5b.
   - `odrzuć` → `manifest.py upsert <Name> status=rejected`, koniec dla tego assetu.
4. Batch: pokaż wszystkie naraz (siatka/lista), użytkownik może zaakceptować część (np. „tak: IconArena, IconDungeon; popraw IconFortress: …”). Upload tylko zaakceptowanych.
5. Brak odpowiedzi (sesja nienadzorowana) → **zatrzymaj się** po kroku 5, `status=awaiting_approval`, raport. Nie zgaduj zgody.

## Krok 6 – Upload do Roblox (Open Cloud)
Warunek: `manifest.py approve <Name>` wykonane po „tak” użytkownika. Skrypt sam weryfikuje akceptację i zgodność sha256 pliku – exit code `3` = brak akceptacji → wróć do 5b. **Nie obchodź tego `--force`** (flaga tylko do testów, za zgodą użytkownika).
```bash
python tools/roblox_upload.py upload assets/processed/<Name>.png --name <Name>
```
Wynik JSON: `decalId`, `moderationState`. Zapisz:
`manifest.py upsert <Name> roblox_decal=<decalId> moderation=<state>`
Błąd 401/403 → klucz/uprawnienia/IP (README §2.2); nie ponawiaj w pętli.

## Krok 7 – Decal ID → Image ID (Roblox Studio MCP)
Uruchom w Studio (narzędzie do wykonania kodu) zawartość `tools/resolve_image_id.luau` z podstawionym `DECAL_ID`. Wynik = `imageId`.
`manifest.py upsert <Name> roblox_image=<imageId> status=in_roblox`
Studio niedostępne → zostaw `roblox_image` puste (AssetIds użyje tymczasowo `rbxthumb://`), zaznacz w raporcie.

## Krok 8 – AssetIds (Roblox Studio MCP)
```bash
python tools/manifest.py gen-lua > build/AssetIds.lua
```
W Studio utwórz/zaktualizuj `ReplicatedStorage.AssetIds` (ModuleScript) z treścią `build/AssetIds.lua` (ustaw `Source`; jeśli narzędzie nie pozwala – użyj narzędzia do edycji skryptu).

## Krok 9 – Podpięcie (tylko jeśli podano `roblox_target`)
Ustaw właściwość w Studio przez `AssetIds`, nie przez wpisanie ID, np. w skrypcie budującym UI:
`button.Image = AssetIds.IconArena`. Jeśli UI jest budowane skryptem (np. `HUDClient` / BUILD z `docs/`), zaktualizuj ten skrypt, a nie tylko instancję.
Szybki test: Play Solo → screenshot.

## Krok 10 – Raport
Krótko, po polsku:
- tabela: `Name | wariant | Figma node | decalId | imageId | moderacja | gdzie podpięte`,
- zużyte kredyty (szacunek),
- co wymaga ręcznej akcji (np. moderacja w toku, brak Studio).
`manifest.py upsert <Name> status=done` gdy wszystko OK.

---

## Obsługa błędów (skrót)
| Problem | Działanie |
|---|---|
| Higgsfield: brak kredytów / błąd auth | stop, raport; nie próbuj innego dostawcy bez zgody |
| Wynik ma tekst/litery | odrzuć wariant, dopisz do promptu „no text, no letters, no logo” |
| Kolorowe/szare tło zamiast białego | `--bg rembg`; jeśli brak rembg – regeneruj z mocniejszym „pure white #FFFFFF background” |
| Figma upload 403 / timeout | 1 ponowienie z nowym `upload_assets`; dalej – raport |
| Roblox moderacja `Rejected` | raport + propozycja zmiany (zwykle: zbyt realistyczne/krwawe/tekst) |
| Studio rozłączone | kroki 7–9 pomiń, oznacz `status=pending_studio`, `/asset sync` później |
