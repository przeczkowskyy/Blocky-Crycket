---
status: propozycja
tags: [technika, grafika, pipeline]
---
# Pipeline assetów

> [!info] Fakty i propozycje
> **Fakty:** paczka jest zainstalowana (stan niżej, 2026-11-12). **Propozycja:** przyjęcie zasad paczki jako obowiązujących, zob. [[Rejestr decyzji#D-011 Pipeline assetów `/asset` i moduł `AssetIds`|D-011]].

## Co to jest
Pierwotnie paczka `blocky-asset-pipeline` w osobnym folderze. **Od 2026-11-12 jest w projekcie gry**, więc działa w tym samym oknie Claude Code co reszta pracy. Pliki: skill `.claude/skills/asset/` (zasady: `references/project-rules.md`), narzędzia `tools/*.py`, rejestr `assets/manifest.json`, instrukcja `docs/asset-pipeline-setup.md`, klucze w `.env` (poza Git). Jedna komenda prowadzi grafikę od pomysłu do gry:

`/asset ikona Arena do HUD, styl jak przyciski Shop/Pets`

1. **Generowanie** w Higgsfield (MCP), domyślnie 3 warianty. Prompt powstaje według [[Instrukcja promptów — Glossy Ink]] (opis niżej, „Budowa promptu”), a jako obraz referencyjny stylu idzie key-art ekranu ładowania z `assets/refs/`.
2. **Wybór wariantu** przez Game Directora (bez `--auto`).
3. **Obróbka** `tools/process_image.py`: wycięcie tła, przycięcie, kwadrat, rozmiar docelowy.
4. **Figma**: wrzucenie do biblioteki assetów albo podmiana obrazka w komponencie.
5. **⛔ Akceptacja Game Directora** przed Roblox. Zawsze, także z `--auto` i w batchu.
6. **Upload** przez Roblox Open Cloud (`tools/roblox_upload.py`). Skrypt sam blokuje wysyłkę bez akceptacji zapisanej w manifeście (z sumą sha256 pliku).
7. **ID obrazka** z ID decala (w Studio) i moduł `AssetIds` z manifestu.
8. **Wpis** w `assets/manifest.json`, czyli rejestrze: co, gdzie i z jakim ID.

| Komenda | Co robi |
|---|---|
| `/asset <opis>` | pełny pipeline dla jednego assetu |
| `/asset <opis> --auto` | bez pytania o wariant; akceptacja przed Roblox nadal obowiązkowa |
| `/asset batch: …` | kilka assetów naraz; przy dużym batchu najpierw szacunek kredytów Higgsfield |
| `/asset approve <Nazwa>` | akceptacja assetu, który czeka → upload |
| `/asset status` | tabela z manifestu |
| `/asset sync` | ponowne wygenerowanie modułu `AssetIds` |

## Budowa promptu (Glossy Ink, D-027 od 13.11.2026)
Od 13.11.2026 skill `/asset` składa każdy prompt według [[Instrukcja promptów — Glossy Ink]] (kanon, decyzja D-027). Szablony są w `.claude/skills/asset/references/prompt-templates.md`.
1. **Stały początek** — przepisany 1:1 z instrukcji, bez zmian i bez tłumaczenia.
2. **Zmienny środek** — szablon kategorii (ikona, przycisk, przedmiot, pet, waluta, ramka, okno, tło, mapa izometryczna, arkusz pinezek) z podstawionym opisem. Tu idą wszystkie dopiski, np. „no text, no letters” po nieudanym wariancie.
3. **Stały koniec** — przepisany 1:1. Daje białe tło, które narzędzie obróbki wycina. Mapa miasteczka kończy się drewnianą ramką z przyciskiem „X” zamiast zdania o białym tle; pełne tła i key-art kończą się bez tego zdania (to rozszerzenie skilla, nie zapis z instrukcji).
4. **Stały negative prompt** — przepisany 1:1 i zawsze podawany osobno.

Przed generowaniem skill sprawdza żelazne zasady instrukcji: nic nie wystaje poza ramki, portret i sloty są puste, okna to jedna scalona bryła ze statystykami w 2 kolumnach po 3 wiersze, mapy izometryczne nie mają pinezek ani napisów. Dawny prefiks z [[Style Lock]] (D-001) i dawny blok stylu paczki nie są już używane. Zasada „zero tekstu w grafikach AI” zostaje: napisy w obrazie tylko na wyraźną prośbę, np. przy makiecie okna.

## Stan instalacji (2026-11-12)
- [x] Zależności Python (`pip install -r requirements.txt`).
- [x] `.env`: typ twórcy `user` i ID konta właściciela gry (gra i dotychczasowe obrazki należą do tego samego konta, sprawdzone w Studio).
- [ ] `.env`: klucz `ROBLOX_API_KEY` (Open Cloud, Assets API: Read + Write). Wpisuje Game Director.
- [x] `.mcp.json`: `roblox-studio` przestawiony na **oficjalny** serwer MCP Roblox Studio, ten sam co w folderze gry. Społecznościowa wtyczka `robloxstudio-mcp` i włączanie HTTP Requests w grze nie są potrzebne.
- [x] Serwer Higgsfield dopisany do `.mcp.json` gry. Figma działa przez konektor claude.ai, Roblox Studio przez istniejący serwer tego folderu.
- [ ] Logowanie w Claude Code: `/mcp` → higgsfield → Authenticate (po ponownym uruchomieniu sesji).
- [ ] Figma z prawem edycji. Konto podłączone do Claude ma plan Starter z miejscem „View”, a krok Figmy zapisuje w pliku projektu.
- [x] Manifest: 10 istniejących assetów (6 przycisków HUD, ramka portretu, moneta, diament, key-art) z ID z Roblox, status `in_roblox`.
- [x] Test narzędzi: generator `AssetIds` i obróbka obrazka działają.
- ⚠️ `rembg` (lepsze wycinanie tła) jest blokowany przez Windows (Inteligentna kontrola aplikacji). Obróbka automatycznie używa flood fill, które dobrze działa przy białym tle wymuszanym przez prompt.

## Do ustalenia
- **Gdzie ma żyć moduł `AssetIds`.** Paczka wstawia `ReplicatedStorage.AssetIds` przez Studio, więc istniałby tylko w miejscu gry, a nie w plikach. Projekt trzyma kod w Rojo. Propozycja: plik `src/shared/AssetIds.luau` → `ReplicatedStorage.Shared.AssetIds`.
- **Przepięcie [[HUD]] i [[Ekran ładowania|ekranu ładowania]]** z ID wpisanych na sztywno na `AssetIds`, jeśli D-011 zostanie przyjęta.
- `CLAUDE.md` paczki wymienia systemy spoza kanonu (sklep z bronią i magią, gildie, teleport). Zob. [[Pytania otwarte]] #5.

## Powiązane
- [[Narzędzia]] · [[Instrukcja promptów — Glossy Ink]] · [[Style Lock]] (historia) · [[Pipeline Figma → Roblox]] · [[Workflow i Git]] · [[Rejestr decyzji]]
