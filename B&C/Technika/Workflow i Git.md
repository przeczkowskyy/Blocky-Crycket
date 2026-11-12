---
status: propozycja
tags: [technika, workflow, git]
---
# Workflow i Git

> [!info] Fakty i zalecenia
> **Fakty:** repozytorium istnieje i jest publiczne (utworzone przez Game Directora 2026-11-12). **Zalecenia** (lista niżej) to propozycja Claude do akceptacji.

## Repozytorium
- GitHub: https://github.com/przeczkowskyy/Blocky-Crycket, gałąź `main`, **publiczne**.
- Pełne podsumowanie projektu dla osób spoza sejfu: `DOKUMENTACJA.md` w głównym folderze repo. Źródłem prawdy pozostaje ten sejf.
- Poza repo (`.gitignore`): `node_modules/`, `dashboard/data/` i `.env`, `*.rbxl.lock`, `B&C/.obsidian/workspace.json`, `.claude/settings.local.json`.

## Codzienna praca
1. `git pull`.
2. Studio z `Blocky&Crycket.rbxl` → `rojo serve` → Plugins → Rojo → **Connect** (po każdym ponownym otwarciu Studio). Zob. [[Rojo i struktura projektu]].
3. [[Zadania]] i [[Pytania otwarte]] → praca z Claude Code → Claude aktualizuje sejf.
4. **Ctrl+S** w Studio → commit → push.

## Testowanie (stosowane w praktyce)
- `rojo build default.project.json -o <katalog_tymczasowy>/check.rbxlx`: walidacja plików.
- Podgląd w edytorze: tymczasowa kopia GUI (`_Nazwa`, `Enabled = true`) w StarterGui, zrzut ekranu, usunięcie kopii.
- Play Solo przez Roblox Studio MCP: Output, stan obiektów klienta i serwera, symulowane kliknięcia.
- Ręcznie: emulator telefonu (Test → Device), hover myszą, prawdziwy serwer.

## Zalecenia (propozycja)
- Commit po skończonym kawałku pracy, razem z aktualizacją sejfu ([[Dziennik zmian]]).
- Przed commitem zapis Studio: część gry istnieje tylko w `.rbxl` (np. [[Ekran ładowania]]).
- `.rbxl` jest binarny i Git go nie scala: miejsce naraz edytuje jedna osoba.
- Nigdy żadnych sekretów w repo (klucze API, `.env`): repo jest publiczne.
- Claude Code robi commit i push tylko na wyraźną prośbę.

## Do ustalenia
- Czy repo ma zostać publiczne?
- Czy pracujemy na gałęziach (np. jedna na funkcję), czy wszystko idzie na `main`?
- Gra jest już opublikowana na Roblox i Studio otwiera wersję z chmury. Czy dalej trzymamy w repo plik `.rbxl` (Studio → File → Save to File), czy źródłem jest miejsce w chmurze?

## Powiązane
- [[Narzędzia]] · [[Pipeline Figma → Roblox]] · [[Rojo i struktura projektu]] · [[00 Start]]
