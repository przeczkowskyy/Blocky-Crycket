# BLOCKY & CRYCKET — Roblox game

## Project brain: Obsidian vault `B&C/`
The Obsidian vault in `B&C/` is the **single source of truth** for this project (decision D-008). Everything about the game — design, characters, art direction, UI specs, technical setup, roadmap, tasks, decisions — lives there.

**Before any meaningful work:** read `B&C/00 Start.md`, `B&C/Jak prowadzimy sejf.md`, and the notes relevant to the task (follow `[[wikilinks]]`). Check `B&C/Produkcja/Rejestr decyzji.md` for what is approved.

**Status discipline** (frontmatter `status:`):
- `kanon` = approved by the Game Director, binding.
- `propozycja` = idea / older spec, NOT a fact — never present it as decided.
- `do-decyzji` = waiting for the user.
Never change a note to `kanon` or a decision to ✅ without the user's explicit approval. If a request conflicts with canon, say so and add the conflict to `B&C/Produkcja/Pytania otwarte.md` instead of silently overriding.

**After finishing work:**
1. Update the affected notes (e.g. "Stan implementacji" checklists in `B&C/UI/*.md`).
2. Tick/move items in `B&C/Produkcja/Zadania.md` (with date).
3. Add an entry at the top of `B&C/Produkcja/Dziennik zmian.md` (date, what changed, files/notes touched).
4. New ideas → `status: propozycja` notes or 💡 entries in `Rejestr decyzji.md`.
5. If the change affects something described in `DOKUMENTACJA.md` (repo-wide summary of the vault + code), update it too.

**Vault rules:** write in Polish; use `[[wikilinks]]` to existing note names; never edit `B&C/Źródła/` (original documents — cite them); never touch `B&C/.obsidian/` except settings the user asks for; use templates from `B&C/Szablony/`.

## Code (Rojo 7.6.1)
- `src/server` → ServerScriptService.Server, `src/client` → StarterPlayerScripts.Client, `src/shared` → ReplicatedStorage.Shared, `src/gui` → StarterGui (`*.model.json`). Details: `B&C/Technika/Rojo i struktura projektu.md`.
- All nodes use `$ignoreUnknownInstances: true`; content that exists only in `Blocky&Crycket.rbxl` is invisible to file tools. Never edit the `.rbxl`.
- Figma → GUI: skill `figma-to-roblox` (`.claude/skills/figma-to-roblox/SKILL.md`).
- Asset pipeline (new graphics: Higgsfield → processing → Figma → Roblox Open Cloud): skill `asset` (`.claude/skills/asset/SKILL.md`, rules in `references/project-rules.md`), tools in `tools/*.py`, registry `assets/manifest.json`, secrets in `.env` (gitignored — never print it). Upload to Roblox ONLY after the user's explicit "tak". Status: `B&C/Technika/Pipeline assetów.md`.
- `ReplicatedFirst` (loading screen) is not mapped by Rojo; its reproducible source is `tools/studio/build_loading_screen.luau` (run via Roblox Studio MCP).

## Git (GitHub)
- Repo: https://github.com/przeczkowskyy/Blocky-Crycket — **public**, branch `main`. Commit/push only when the user asks.
- Never commit secrets (`.env`, API keys, tokens). `.gitignore` covers lock files, Obsidian `workspace.json`, `.claude/settings.local.json`, `dashboard/` data and `node_modules`.
- `Blocky&Crycket.rbxl` is committed as a binary snapshot — ask the user to save in Studio (Ctrl+S) before committing it.

## Communication
The user is the Game Director and writes in Polish — reply in Polish, give concrete Roblox Studio steps.
