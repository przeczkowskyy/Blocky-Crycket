# Blocky&Crycket – Asset Pipeline (Claude Code → Higgsfield → Figma → Roblox)

Jedna komenda w Claude Code:

```
/asset ikona Arena do HUD, styl jak przyciski Shop/Pets
```

…i lecą kroki: **generowanie (Higgsfield)** → wybór wariantu przez Ciebie → **obróbka** (wycięcie tła, trim, rozmiar) → **Figma** (biblioteka assetów + podpięcie do komponentu) → **⛔ Twoja akceptacja finalnego obrazka** → **Roblox** (upload przez Open Cloud + aktualizacja `ReplicatedStorage.AssetIds`) → wpis w `assets/manifest.json`.

> **Nic nie trafia do Roblox bez Twojego „tak”.** Claude Code zawsze pokazuje finalny obrazek (i podgląd z Figmy) i czeka na akceptację – również w trybie `--auto` i w batchu. Dodatkowo skrypt uploadu sam blokuje wysyłkę, jeśli asset nie ma w manifeście flagi akceptacji.

---

## 1. Wymagania
| Co | Po co |
|---|---|
| [Claude Code](https://docs.claude.com/en/docs/claude-code) | orkiestracja całego pipeline'u |
| Python 3.10+ | skrypty w `tools/` |
| Node.js 18+ | serwer MCP Roblox Studio (`npx`) |
| Roblox Studio + plugin MCP | wstawianie assetów / UI do gry |
| Konto Higgsfield | generowanie grafik (kredyty!) |
| Konto Figma (edycja pliku) | plik projektu `BbLd4jDnvxAmOWZN1hAZQJ` |
| Klucz Roblox Open Cloud | upload obrazków bez klikania w Studio |

## 2. Instalacja (raz)

### 2.1 Folder projektu
Rozpakuj paczkę, np. do `C:\dev\blocky-asset-pipeline`, i otwórz tam terminal:
```bash
cd C:\dev\blocky-asset-pipeline
python -m pip install -r requirements.txt
```
> `rembg` przy pierwszym użyciu ściąga model (~170 MB). Jeśli nie chcesz – skrypt sam przełączy się na wycinanie tła „flood fill” (działa dobrze przy białym tle + grubym czarnym obrysie, a takie tło wymusza nasz prompt).

### 2.2 Zmienne środowiskowe
Skopiuj `.env.example` → `.env` i uzupełnij:
```
ROBLOX_API_KEY=...            # Open Cloud API key
ROBLOX_CREATOR_TYPE=user      # user albo group
ROBLOX_CREATOR_ID=...         # Twoje userId albo groupId grupy z grą
FIGMA_FILE_KEY=BbLd4jDnvxAmOWZN1hAZQJ
```
**Klucz Roblox Open Cloud:** creator.roblox.com → Dashboard → Open Cloud → API Keys → Create API Key
- Access Permissions: **Assets API** → `Read` + `Write`
- Security: dodaj swoje IP (albo `0.0.0.0/0` na czas testów)
- jeśli gra jest na grupie – klucz twórz w kontekście grupy i ustaw `ROBLOX_CREATOR_TYPE=group`

### 2.3 Serwery MCP
`.mcp.json` w paczce ma już 3 serwery. Claude Code zapyta o zgodę przy pierwszym uruchomieniu w tym folderze.

| Serwer | Logowanie |
|---|---|
| `higgsfield` (`https://mcp.higgsfield.ai/mcp`) | OAuth w przeglądarce przy pierwszym użyciu (`/mcp` → higgsfield → Authenticate) |
| `figma` (`https://mcp.figma.com/mcp`) | OAuth w przeglądarce (`/mcp` → figma → Authenticate) |
| `roblox-studio` (`npx robloxstudio-mcp`) | wymaga pluginu w Studio – patrz niżej |

**Windows:** jeśli `npx` nie startuje, w `.mcp.json` zamień blok `roblox-studio` na:
```json
"roblox-studio": { "command": "cmd", "args": ["/c", "npx", "-y", "robloxstudio-mcp@latest"] }
```

**Plugin Roblox Studio:** zainstaluj plugin „Roblox Studio MCP” (link w repo `boshyxd/robloxstudio-mcp` na GitHubie), w Studio: *Game Settings → Security → Allow HTTP Requests = ON*, otwórz swój place – plugin pokaże **Connected**.
> Alternatywa: oficjalny serwer MCP Robloxa (w Studio: Assistant → … → Enable Studio as MCP server). Wtedy podmień wpis `roblox-studio` w `.mcp.json` zgodnie z instrukcją Robloxa. Skill korzysta z ogólnych operacji (uruchom kod / utwórz skrypt), więc działa z oboma.

### 2.4 Test połączeń
```bash
claude
```
W Claude Code:
```
/mcp
```
Wszystkie 3 serwery mają być `connected`. Potem:
```
Sprawdź pipeline: whoami w Figmie, lista modeli Higgsfield, ping Roblox Studio, i `python tools/roblox_upload.py check`.
```

## 3. Użycie
| Komenda | Co robi |
|---|---|
| `/asset <opis>` | pełny pipeline dla 1 assetu (z akceptacją wariantu) |
| `/asset <opis> --auto` | bez pytania o wybór wariantu (bierze najlepszy wg QA) – **akceptacja przed Roblox nadal obowiązkowa** |
| `/asset approve <Name>` | akceptacja assetu czekającego (`awaiting_approval`) → upload do Roblox |
| `/asset batch: ikony Arena, Dungeon, Fortress` | kilka assetów naraz, jedna akceptacja dla wszystkich |
| `/asset sync` | przegenerowuje `ReplicatedStorage.AssetIds` z manifestu |
| `/asset status` | tabela z manifestu: co jest w Figmie / Robloxie / co czeka |

W kodzie gry **nigdy nie wpisuj asset ID ręcznie**:
```lua
local AssetIds = require(game.ReplicatedStorage.AssetIds)
button.Image = AssetIds.Teleport
```

## 4. Struktura
```
blocky-asset-pipeline/
├─ CLAUDE.md                     # zasady projektu dla Claude Code (styl, reguły, ID plików)
├─ .mcp.json                     # higgsfield + figma + roblox-studio
├─ .env.example
├─ requirements.txt
├─ .claude/skills/asset/
│  ├─ SKILL.md                   # pipeline /asset krok po kroku
│  └─ references/
│     ├─ style-guide.md          # styl wizualny Blocky&Crycket
│     └─ prompt-templates.md     # szablony promptów per kategoria
├─ tools/
│  ├─ process_image.py           # wycinanie tła, trim, kwadrat, rozmiary
│  ├─ figma_upload.py            # POST pliku na upload URL z Figma MCP
│  ├─ roblox_upload.py           # Open Cloud: upload, polling, status
│  ├─ manifest.py                # rejestr assetów + generator AssetIds.lua
│  └─ resolve_image_id.luau      # decal ID → image ID (uruchamiane w Studio)
├─ assets/
│  ├─ manifest.json              # źródło prawdy: co, gdzie, jakie ID
│  ├─ refs/                      # referencje stylu (wrzucane do Higgsfield)
│  ├─ raw/                       # surowe wyniki z Higgsfield
│  └─ processed/                 # gotowe PNG
└─ docs/                         # wcześniejsze prompty (loading screen, HUD)
```

## 5. Ograniczenia (warto wiedzieć)
- **Decal ID ≠ Image ID.** Open Cloud zwraca ID decala; UI potrzebuje ID obrazka. Skill rozwiązuje to automatycznie w Studio (`InsertService:LoadAsset`). Jeśli Studio nie jest otwarte → tymczasowo `rbxthumb://` (niższa rozdzielczość, max 420 px) i oznaczenie w manifeście do poprawki.
- **Moderacja Roblox:** nowy obraz może przez chwilę być pusty / szary. Skill zapisuje `moderationState` w manifeście.
- **Obrazów w Roblox nie da się „zaktualizować”** – każda poprawka = nowy asset ID (manifest trzyma historię).
- **Kredyty Higgsfield:** domyślnie 3 warianty na asset. Każdy batch skill najpierw pokazuje szacunek.
- **Tekst na grafikach AI wychodzi krzywo** – napisy (np. „SHOP”) robimy natywnie w Figmie/Roblox (font Luckiest Guy), AI generuje tylko grafikę.
