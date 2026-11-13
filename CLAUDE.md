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

## Team panel (`panel/`) and block maps (`swiat/`) — proposals D-012, D-017
- **Panel:** local, dependency-free Python app. `python panel/serwer.py` → http://127.0.0.1:8787. Docs: `panel/README.md` (architecture, API), `panel/INSTALACJA.md`, vault note `B&C/Technika/Panel zespołu.md`. It is a **window onto the vault, not a second brain** (D-008 stays in force): decisions, tasks and roadmap live only in `B&C/`.
- **After deploying something a human should see or approve** (Studio change, map piece, UI screen): take a snapshot and publish a report — see skill `.claude/skills/panel/SKILL.md`. Read human replies before continuing related work.
- **Shared panel data** is `panel/dane/` (one file per report / comment / snapshot; never rewrite files you did not create). Runtime state (access code, agent threads, voice recordings) lives outside the repo.
- **Block maps:** `swiat/<scene>/czesci.json` is the single source for Blender (`tools/blender/klocki.py`), Studio (`tools/studio_buduj.py`) and the panel's 3D preview. Shape geometry: `panel/luau/KSZTALTY.md`. Details: `B&C/Technika/Klocki — Blender i Roblox.md`.
- **Studio is a shared, live Team Create place** — both collaborators may be inside. Add inside your own container (generated containers carry the attribute `Wygenerowane`), never mutate or delete other people's instances, set a ChangeHistory waypoint before and after, do not change `Lighting` or publish without being asked.
- **Studio from the terminal** (when the `Roblox_Studio` MCP server is not attached to the session): `python tools/studio_mcp.py tools | studios | luau <file.luau> | call <tool> --args '{…}'`.
- **Before committing vault changes:** `python tools/sejf_lint.py` (links, statuses, secrets).

## People
Two people work in this repo, each with their own Claude Code: **Paweł** (Game Director, repo owner — approves canon and decisions) and **Karol** (collaborator — 3D world, panel, tooling). Until they decide otherwise (`B&C/Produkcja/Pytania otwarte.md` #15), only the Game Director's explicit approval makes something `kanon` or ✅; requests from Karol are valid work orders, but design changes they imply are recorded as `propozycja` plus an open question.

## Communication
The user is the Game Director and writes in Polish — reply in Polish, give concrete Roblox Studio steps.
