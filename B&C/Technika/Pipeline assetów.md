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

1. **Generowanie** w Higgsfield (MCP) modelem **Nano Banana 2.1** (`nano_banana_2_1`, polecenie Game Directora; nie GPT Image), domyślnie 3 warianty. Prompt powstaje według [[Instrukcja promptów — Glossy Ink]] (opis niżej, „Budowa promptu”), a jako obraz referencyjny stylu idzie key-art ekranu ładowania z `assets/refs/`.
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

## Dźwięk i muzyka — pierwsza partia (16.11.2026)
Po sesji głównej 16.11 (D-082, D-083) i zgodzie Karola na kredyty powstała pierwsza partia audio z Higgsfield. Partia jest zaakceptowana przez Karola (16.11), ale nic nie jest wgrane do Roblox.
- **Co jest:** 12 utworów instrumentalnych po 90 s (menu, trzy dla Krzywego Miasteczka, osiem biomów), drugie wersje menu i lasu, każdy z wersją do pętli w OGG; 22 krótkie efekty walki, każdy w dwóch wariantach (A główny, B zapasowy).
- **Gdzie:** `assets/audio/` — `muzyka/` (pełne wersje i wersje do pętli), `dzwieki/` (warianty A i B), `manifest_audio.json` (prompty, modele, koszty, pomiary) i `README.md`. Karol przesłuchał partię 16.11, zaakceptował ją w panelu („jest bardzo dobre”, dalsze poprawki możliwe) i poprosił o wypchnięcie plików, więc gotowe pliki są w repo; lokalnie zostają oryginały sprzed obróbki.
- **Modele i koszt:** muzyka — ElevenLabs Music v2.5, efekty — Seed Audio 1.0 (A) i Mirelo (B); razem 229,5 kredytu, na koncie zostało ok. 205.
- **Kontrola techniczna:** głośność wyrównana (muzyka ok. −16 LUFS, efekty ok. −14 LUFS), cisza przycięta, pętle z jednosekundowym przenikaniem. Płynności pętli, braku wokalu i jakości melodii nie da się ocenić bez ucha — ocenia Karol. Lodowiec ma na szwie pętli spadek głośności 6,8 dB.
- **Zanim wgramy do Roblox** (źródła i szczegóły w `assets/audio/README.md`): Roblox przyjmuje mp3, ogg, wav i flac do 7 minut i 20 MB, audio przechodzi moderację, a za treść z generatora odpowiada wgrywający. Warunki Higgsfield nie ograniczają użycia komercyjnego na płatnym planie. Warunki ElevenLabs Music dopuszczają gry mieszczące się w definicji „Indie Game”, ale **nie ustalono pewnie**, czy obowiązują przy generowaniu przez Higgsfield — przed publikacją trzeba zapytać pomoc Higgsfield na piśmie (zadanie w [[Zadania]]). Warunków dla efektów z Seed i Mirelo przez Higgsfield nie znaleziono.

## Dźwięk wgrany do Roblox (17.11.2026)
Karol zgodził się na wgranie pierwszej partii 17.11 ok. 09:05 („Tak wgrywaj. Potem najwyżej się zmieni”), a o 12:40 potwierdził drogę („tak przez folder modeli”). Wgrał agent Karola 17.11 o 12:43, na konto osoby zalogowanej w Studio (Karol); właścicielem gry jest inne konto.

| Plik | Identyfikator zasobu |
|---|---|
| `assets/audio/arkusz/sfx_arkusz_a.ogg` (22 efekty walki w jednym pliku) | 93573204965127 |
| `assets/audio/muzyka/muzyka_02_bazar_targ_petla.ogg` | 94425435537814 |
| `assets/audio/muzyka/muzyka_03_bazar_rzemieslnicy_petla.ogg` | 116217836078354 |
| `assets/audio/muzyka/muzyka_04_bazar_wieczor_petla.ogg` | 75722490819761 |
| `assets/audio/muzyka/muzyka_05_las_a_petla.ogg` | 70497074484606 |
| `assets/audio/muzyka/muzyka_05_las_b_petla.ogg` | 106582652985449 |
| `assets/audio/muzyka/muzyka_06_bagno_petla.ogg` (wgrany 18.11) | 116759284253061 |
| `assets/audio/muzyka/muzyka_07_dzungla_petla.ogg` (wgrany 18.11) | 78060184641141 |

- **Stan:** wszystkie sześć zasobów przyjęte, moderacja Roblox w toku w chwili wgrania. Rejestr: `assets/audio/wgrane.json`, zgoda z sumami kontrolnymi plików: `assets/audio/zgoda_wgrania.json`, identyfikatory w grze: `swiat/dzwiek_gra/identyfikatory.json`.
- **Jak:** `tools/roblox_upload_audio.py wgraj-studio` — przez Roblox Studio, bo w repo nie ma klucza Open Cloud. Studio przyjmuje pliki tylko z folderów zatwierdzonych ręcznie przez człowieka; folder dźwięku nie jest zatwierdzony, więc każdy plik był na czas wgrania kopiowany do zatwierdzonego folderu wyników postaci i od razu usuwany. Taka droga wymaga wyraźnej zgody człowieka za każdym razem — ogólne „leć” nie wystarcza (system uprawnień odmówił o 12:20, zanim Karol potwierdził drogę).
- **Limit:** Roblox liczy wgrania audio na miesiąc (10 bez weryfikacji tożsamości konta, 100 z weryfikacją). W listopadzie 2026 wykorzystane 8 (sześć 17.11, dwa 18.11). Dlatego efekty są w jednym arkuszu granym odcinkami (`tools/audio_arkusz.py`).
- **Prawa gry do zasobów:** samo bycie współtwórcą gry nie wystarcza — każdy plik audio trzeba osobno udostępnić grze (Creator Hub → lista plików audio → plik → Uprawnienia → dodać grę po identyfikatorze; nadania nie da się cofnąć). Karol nadał prawa wszystkim sześciu plikom 17.11 ok. 19:45; kontrola w grze: wszystkie sześć wczytane, muzyka bazaru gra. Muzyka menu nie jest wgrana (Karol nie wybrał wersji A albo B). Pytanie o prawa do muzyki przed publikacją gry zostaje otwarte (wyżej).
- **18.11.2026 — muzyka Bagna i Dżungli:** Karol na czacie zgodził się na wgranie („Wgraj i zaprojektuj pozostałe muzyki”) i potwierdził drogę („Tak, przez folder modeli”). Wgrał agent Karola o 12:24 na konto Karola; moderacja w toku w chwili wgrania. **Grze trzeba jeszcze nadać prawa do obu plików** (Karol, Creator Hub, jak 17.11) — dopiero potem zagrają w grze. Podpięcie w grze: `swiat/dzwiek_gra/` (w toku). Pięć nowych utworów z 18.11 (walka, Strażnik, mini-gry, drugie utwory Bagna i Dżungli) nie jest wgranych — czekają na odsłuch (pytanie 66 w [[Pytania otwarte]]).
