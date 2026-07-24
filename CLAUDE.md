# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Converts scanned homework worksheets into accessible, self-contained single-page HTML apps customized for a specific child's physical/learning barriers. It also maintains a library of reusable math/literacy **tools** and template-driven **activities** the child can use independently. Output is published to GitHub Pages via `docs/`.

The core idea: the model's job (parse worksheet → apply framework + child profile → emit one HTML file) is identical whether triggered from the CLI, a folder watcher, or a manual claude.ai chat. Only the I/O mechanism differs.

## Commands

```bash
python -m pip install -r requirements.txt

# Build one worksheet
python runners/cli.py --worksheet <path> --child <name> [--date YYYY-MM-DD] [--subject <slug>]

# Watch incoming/ for new worksheet scans (auto-build + move to incoming/done/)
python runners/watcher.py

# Sync worksheets/{child}/, tools/, activities/{type}/{child}/ into docs/ (GitHub Pages)
python runners/publish.py --child <name> [--push] [--preserve]

# Turn pending-updates.md (or a file/stdin) into GitHub PRs against framework/profile files
python runners/propagate.py [--dry-run]
```

npm aliases exist for all four (`npm run build|watch|publish|propagate`).

There is no lint/test suite — correctness is verified by opening generated HTML and by the git hooks below. `runners/publish.py --preserve` skips rewriting unchanged files (hash-compares before overwrite).

### Git hooks (`.githooks/`)

`pre-commit` and `pre-push` both call `python runners/publish.py --child <CHILD>` and fail if `docs/` ends up dirty after publishing — this keeps `docs/` (the Pages output) always in sync with `worksheets/`, `tools/`, and `activities/`. `CHILD` resolves from `PUBLISH_CHILD` env var → `git config hooks.child` → `DEFAULT_CHILD` env var. Install hooks with `.githooks\install-hooks.cmd` (`npm run install-hooks`).

## Environment (`.env`)

| Variable | Required for | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | cli.py, watcher.py, propagate.py | |
| `ANTHROPIC_MODEL` | optional | defaults to `claude-opus-4-5` in every runner |
| `DEFAULT_CHILD` | optional | cli.py falls back to `maya`, watcher.py to `christina` — these differ, pass `--child`/`CHILD` explicitly when it matters |
| `GITHUB_TOKEN` / `GITHUB_REPO` | propagate.py | PAT needs Contents + Pull Requests R/W; `GITHUB_REPO` is `owner/repo` |
| `INCOMING_DIR`, `OUTPUT_DIR`, `CHILD`, `AUTO_COMMIT` | watcher.py | `AUTO_COMMIT=true` git add/commit/push generated output |

## Architecture

**Three layers of instructions get assembled into one system prompt per build** (see `assemble_system_prompt()` in both `runners/cli.py` and `runners/watcher.py`):

1. `SYSTEM_PROMPT.md` — the build process and non-negotiable goal ("never simplify content, only remove friction")
2. `framework/*.md` — generalizable knowledge shared across all children:
   - `DESIGN_SYSTEM.md` — CSS tokens/components
   - `INTERACTION_PATTERNS.md` — JS patterns (TTS, STT, answer handling, persistence, focus-safe rendering) — the largest and most load-bearing file
   - `BUILD_CONSTRAINTS.md` — output format, file naming, tap-target/accessibility rules, multi-section splitting rules
   - `WORKSHEET_TYPES.md` — numbered taxonomy of worksheet interaction patterns (Type 1, Type 3, Type 4, ...); a printed worksheet "part" always maps to its own type even if delivered as one combined file
   - `ACTIVITY_TYPES.md` — activity templates (fixed container + reusable engine, only content changes)
   - `TOOL_TYPES.md` — taxonomy/conventions for the reusable computation tools in `tools/`
   - `CONTRIBUTING.md` — the update-propagation protocol (below)
3. `profiles/{child}/PROFILE.md` — one child's specific barriers, what works, and design overrides applied on top of the framework

Read all of these before generating any worksheet code; do not skip straight to output.

### Two output types, one propagation loop

- **Worksheets** (`worksheets/{child}/YYYY-MM-DD-{subject}.html`) reproduce one specific assignment. Check `worksheets/reference/` first for a canonical implementation of the matched type before inventing new patterns.
- **Tools** (`tools/{subject}/{name}.html`) are general-purpose, child-operated, undated, reusable across assignments, linked from worksheet Hint panels and from `tools/{subject}/index.html`.
- **Activities** (`activities/{type}/{child}/...`) use a fixed template (e.g. `activities/proofreading/template.html`) — copy the template as-is and edit only the data block; never use a prior instance as a base.

When the model identifies a confirmed improvement (not a plan — something verified working), it appends a `📋 Update Suggested` block to its response, wrapped in `<!-- COPILOT_UPDATE_SUGGESTED_START ... COPILOT_UPDATE_SUGGESTED_END -->` when run through `cli.py`. `runners/cli.py`/`watcher.py` append these to `pending-updates.md`; `runners/propagate.py` parses `📋` blocks (needs `**File:**` plus either `**Change:**` or a heading+`**Section:**`+body), asks Claude to regenerate the target file with the change integrated, and opens one GitHub PR per file on a fresh `update/{slug}-{date}` branch. The decision-tree for which file a given change belongs in is in `framework/CONTRIBUTING.md`.

### Publishing (`runners/publish.py`)

One-way sync, not a build step for `worksheets/`/`tools/`/`activities/` themselves: copies `worksheets/{child}/*.html` (+ `archive/`) → `docs/worksheets/`, mirrors `tools/` → `docs/tools/` in full, and copies `activities/{type}/{child}/*.html` (+ `archive/`) → `docs/activities/{type}/` (flattened, no child subdir in the published path). Regenerates `docs/worksheets/index.html`, `docs/worksheets/archive/index.html`, and `docs/activities/index.html` from whatever's on disk. `docs/` is a generated artifact — don't hand-edit it, and don't add a child in `worksheets/` or `activities/` without expecting it to appear in `docs/` on next publish/commit.

### Chat-first workflow (VS Code agents)

`.github/agents/worksheet-brainstorm.agent.md` (read-only planning, never builds) and `.github/agents/worksheet-coach.agent.md` (plans, then builds in-context after explicit `BUILD NOW` approval, then auto-applies clear `📋` suggestions directly to `framework/`/`profiles/` files) implement the same read-framework→match-type→apply-profile→build sequence as the Python runners, without shelling out to them. Full behavioral contract (approval phrases, file-naming, auto-apply rules) lives in `.github/copilot-instructions.md` — treat it as authoritative for chat-based builds.

## Conventions worth knowing before editing generated-output logic

- Output is always one self-contained HTML file: inline CSS/JS, no external JS libraries, no `<form>` tags, tap-first controls, minimum 44×44 tap targets.
- Never simplify or reduce academic content — only remove access barriers.
- Don't full-re-render on every keystroke in editable controls; if a full render is unavoidable, capture/restore focus and caret around it.
- Correct answers belong in the JS data object, not hardcoded into markup.
- `worksheets/{child}/` uses `maya` and `christina` fallback defaults that differ between `cli.py` and `watcher.py` — always pass `--child`/`CHILD` explicitly rather than relying on the default when it matters which child you mean.
