---
status: kanon
tags: [technika, figma, ui]
---
# Pipeline Figma → Roblox

1. W Figmie: prawy przycisk na ramce → **Copy link to selection**.
2. Wklej link Claude i napisz, np. „przenieś to do Robloxa”.
3. Claude odczyta układ, kolory, czcionki, zaokrąglenia i obrysy, a potem zapisze `src/gui/<Nazwa>.model.json`.
4. Rojo przesyła GUI do **StarterGui** w Studio.

## Zamiany
Frame → `Frame`, tekst → `TextLabel`, przycisk → `TextButton`/`ImageButton`, zaokrąglenia → `UICorner`, obrys → `UIStroke`, gradient → `UIGradient`, auto layout → `UIListLayout`. Pozycje i rozmiary w skali (Scale), żeby GUI działało na telefonach.

## Ograniczenia
- **Obrazy:** eksport do `assets/figma/<Nazwa>/`, potem Studio → Asset Manager → Bulk Import i podanie Claude ID.
- **Czcionki spoza Robloxa** są zastępowane najbliższymi.
- **Cienie, rozmycia, tryby mieszania** nie mają natywnych odpowiedników w Roblox.
- Logika przycisków trafia osobno do `src/client/`.

Szczegóły techniczne: `.claude/skills/figma-to-roblox/SKILL.md`. Konto Figma ma miejsce typu *View* (odczyt wystarcza).
