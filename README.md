# BLOCKY & CRYCKET

Gra na Roblox: **RPG / Incremental / Tycoon / Pet Collector** z komiksowym humorem w stylu *Shakes & Fidget*, przeniesionym na aktywną rozgrywkę 3D zamiast biernego czekania. Bohaterowie to Rycerz i Kot-Mag; do tego Karczma z questami, własna Twierdza z dropperami i pety z jaj.

**Stan:** Faza 1 — Frontend. W grze działają już ekran ładowania i HUD z Figmy.

## Dokumentacja
- 📘 **[DOKUMENTACJA.md](DOKUMENTACJA.md):** pełna wiedza o projekcie: gra, styl, UI, architektura, narzędzia, workflow, decyzje.
- 🧠 **[Sejf Obsidian `B&C/`](B%26C/00%20Start.md):** źródło prawdy (otwórz folder `B&C` jako vault w Obsidianie).
- 🤖 **[CLAUDE.md](CLAUDE.md):** instrukcje dla Claude Code.

## Szybki start
1. Otwórz `Blocky&Crycket.rbxl` w Roblox Studio.
2. W folderze projektu uruchom `rojo serve` (Rojo 7.6.1).
3. W Studio: **Plugins → Rojo → Connect**. Pliki z `src/` synchronizują się na żywo.

| Folder | Trafia do |
|---|---|
| `src/server` | `ServerScriptService.Server` |
| `src/client` | `StarterPlayer.StarterPlayerScripts.Client` |
| `src/shared` | `ReplicatedStorage.Shared` |
| `src/gui` | `StarterGui` (`*.model.json`) |

Ekran ładowania (`ReplicatedFirst`) nie jest mapowany przez Rojo. Jego źródło to [`tools/studio/build_loading_screen.luau`](tools/studio/build_loading_screen.luau).
