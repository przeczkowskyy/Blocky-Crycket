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

## Praca równoległa dwóch osób (od 15.11.2026)
- Przed ciężką pracą (przebudowa modelu, mapa, budowa kontenera w Studio, większa przeróbka) agent zgłasza ją w panelu razem z tym, czego dotyczy: `python panel/narzedzia/praca.py start --id … --tytul "…" --koniec +45m --obszar model:rycerz --stop-przy-kolizji`, a na końcu `praca.py koniec --id …`. Szczegóły: [[Panel zespołu]], `CLAUDE.md`.
- Jeśli druga osoba pracuje nad tym samym, narzędzie mówi o tym od razu (kod 3) — wtedy agent zatrzymuje się i pyta człowieka. Przebudowa modelu sprawdza to sama i nie ruszy Blendera.
- Gdy wymiana prac jest włączona (domyślnie wyłączona, włącza ją Karol w `panel/konfiguracja.json`), stan trwających prac każdego komputera leży na osobnej, publicznej gałęzi `stan/prace-<osoba>` (sam plik `prace.json`, wysyła ją narzędzie i panel; historia zostaje na zawsze, więc w tytułach prac nic prywatnego). Tych gałęzi nie scalamy, nie zmieniamy ręcznie i nie usuwamy; `main` zostaje jedyną gałęzią pracy.

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
