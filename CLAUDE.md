# BLOCKY & CRYCKET — Roblox game

## Project brain: Obsidian vault `B&C/`
The Obsidian vault in `B&C/` is the **single source of truth** for this project (decision D-008). Everything about the game — design, characters, art direction, UI specs, technical setup, roadmap, tasks, decisions — lives there.

**Before any meaningful work:** read `B&C/00 Start.md`, `B&C/Jak prowadzimy sejf.md`, and the notes relevant to the task (follow `[[wikilinks]]`). Check `B&C/Produkcja/Rejestr decyzji.md` for what is approved.

**Status discipline** (frontmatter `status:`):
- `kanon` = decided by Karol or Paweł and confirmed by the other (decisions D-030 and D-043), binding. A decision with only one signature is a working agreement the other person may still overturn.
- `propozycja` = idea / older spec, NOT a fact — never present it as decided.
- `do-decyzji` = waiting for the user.
Never change a note to `kanon` or a decision to ✅ without explicit approval from Karol or Paweł, and when you do, record who decided and when (`zdecydował: <imię> <data>` in `Rejestr decyzji.md` plus an entry in `Dziennik zmian.md`). If a request conflicts with canon, say so and add the conflict to `B&C/Produkcja/Pytania otwarte.md` instead of silently overriding.

**After finishing work:**
1. Update the affected notes (e.g. "Stan implementacji" checklists in `B&C/UI/*.md`).
2. Tick/move items in `B&C/Produkcja/Zadania.md` (with date).
3. Add an entry at the top of `B&C/Produkcja/Dziennik zmian.md` (date, what changed, files/notes touched).
4. New ideas → `status: propozycja` notes or 💡 entries in `Rejestr decyzji.md`.
5. If the change affects something described in `DOKUMENTACJA.md` (repo-wide summary of the vault + code), update it too.

**Questions and proposals for people must be short** (Karol's request, 2026-11-14): a title of at most ten words, then two to four bullet points saying what it is about and what the options are; longer context goes below, under a line starting with `Szczegóły:`. One question = one matter: before adding a question, check `Pytania otwarte.md` for one that already covers it and extend that instead. If a decision settles the question, add the line `Rozstrzyga: D-0XX`.

**Vault rules:** write in Polish; use `[[wikilinks]]` to existing note names; never edit `B&C/Źródła/` (original documents — cite them); never touch `B&C/.obsidian/` except settings the user asks for; use templates from `B&C/Szablony/`.

## Code (Rojo 7.6.1)
- `src/server` → ServerScriptService.Server, `src/client` → StarterPlayerScripts.Client, `src/shared` → ReplicatedStorage.Shared, `src/gui` → StarterGui (`*.model.json`). Details: `B&C/Technika/Rojo i struktura projektu.md`.
- All nodes use `$ignoreUnknownInstances: true`; content that exists only in `Blocky&Crycket.rbxl` is invisible to file tools. Never edit the `.rbxl`.
- Figma → GUI: skill `figma-to-roblox` (`.claude/skills/figma-to-roblox/SKILL.md`).
- Asset pipeline (new graphics: Higgsfield → processing → Figma → Roblox Open Cloud): skill `asset` (`.claude/skills/asset/SKILL.md`, rules in `references/project-rules.md`), tools in `tools/*.py`, registry `assets/manifest.json`, secrets in `.env` (gitignored — never print it). Upload to Roblox ONLY after the user's explicit "tak". Status: `B&C/Technika/Pipeline assetów.md`.
- `ReplicatedFirst` (loading screen) is not mapped by Rojo; its reproducible source is `tools/studio/build_loading_screen.luau` (run via Roblox Studio MCP).

## Git (GitHub)
- Repo: https://github.com/przeczkowskyy/Blocky-Crycket — **public**, branch `main`.
- **Push finished work right away (D-070, Karol's decision of 2026-11-14, awaiting Paweł's confirmation):** whatever Karol or Paweł (or their Claude Code) changes in the game, the vault or the code goes to GitHub at once — pull before you start, and after each finished and checked change commit and push to `main`, so the other person sees it immediately in the panel (the single place where both look at the state of work). In Paweł's sessions ask him first until he confirms D-070. Do not push half-finished work, never force-push, and on a pull conflict stop and resolve it together with the person.
- Never commit secrets (`.env`, API keys, tokens). `.gitignore` covers lock files, Obsidian `workspace.json`, `.claude/settings.local.json`, `dashboard/` data and `node_modules`.
- `Blocky&Crycket.rbxl` is committed as a binary snapshot — ask the user to save in Studio (Ctrl+S) before committing it.

## Team panel (`panel/`) and block maps (`swiat/`) — D-028 approved; D-012, D-017 proposals
- **The panel is the place of work on the vault (D-028, since 2026-11-13):** people answer open questions, tick and add tasks and change decision statuses there. It writes to the same vault files and logs each change in `Dziennik zmian.md` (section `Panel (ludzie)`) — treat those entries as the humans' own words and read them before related work. A decision status change is signed by the server with the person's name and date; an entry marked `gość panelu` is not an approval.
- **Panel:** local, dependency-free Python app. `python panel/serwer.py` → http://127.0.0.1:8787. Docs: `panel/README.md` (architecture, API), `panel/INSTALACJA.md`, vault note `B&C/Technika/Panel zespołu.md`. It is a **window onto the vault, not a second brain** (D-008 stays in force): decisions, tasks and roadmap live only in `B&C/`.
- **After deploying something a human should see or approve** (Studio change, map piece, UI screen): take a snapshot and publish a report — see skill `.claude/skills/panel/SKILL.md`. Read human replies before continuing related work.
- **Shared panel data** is `panel/dane/` (one file per report / comment / snapshot; never rewrite files you did not create). Runtime state (access code, agent threads, voice recordings) lives outside the repo.
- **Block maps:** `swiat/<scene>/czesci.json` is the single source for Blender (`tools/blender/klocki.py`), Studio (`tools/studio_buduj.py`) and the panel's 3D preview. Shape geometry: `panel/luau/KSZTALTY.md`. Details: `B&C/Technika/Klocki — Blender i Roblox.md`.
- **Studio is a shared, live Team Create place** — both collaborators may be inside. Add inside your own container (generated containers carry the attribute `Wygenerowane`), never mutate or delete other people's instances, set a ChangeHistory waypoint before and after, do not change `Lighting` or publish without being asked.
- **Studio from the terminal** (when the `Roblox_Studio` MCP server is not attached to the session): `python tools/studio_mcp.py tools | studios | luau <file.luau> | call <tool> --args '{…}'`.
- **Before committing vault changes:** `python tools/sejf_lint.py` (links, statuses, secrets).

## People
Two people work in this repo, each with their own Claude Code: **Paweł** (Game Director, repo owner) and **Karol** (3D world, panel, tooling). Since 2026-11-13 (decision D-030, answer to `B&C/Produkcja/Pytania otwarte.md` #15) both have equal rights: explicit approval from either one makes something `kanon` or ✅ — one decision is enough, but every decision must stay in the logs (who and when, in `Rejestr decyzji.md` and `Dziennik zmian.md`). Since 2026-11-14 (decision D-043, agreed aloud by both in the first main session and approved in the panel by Karol) one person decides and the other confirms: the decision is recorded with the first person's signature and waits for the other's answer — agree, disagree or discuss. It is fully binding once both have signed. The confirmation channel (a Telegram alert sent by the panel) is being built; until it works, treat single-signature decisions as working agreements, never add the second signature yourself, and remember that Paweł has not yet reviewed the decisions Karol made alone on 13–14.11 (`Pytania otwarte.md` #27). A request that is not an explicit approval is still a work order: record the design changes it implies as `propozycja` plus an open question. If the two disagree, put the conflict in `Pytania otwarte.md` and override nothing.

## Communication
The user is Karol or Paweł and writes in Polish — reply in Polish, give concrete Roblox Studio steps.
