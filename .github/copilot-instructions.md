# Project Guidelines

## Recognizing Worksheet Build Requests

When a user provides a file path (PDF or image) together with a child name — with or without other context — treat it as a worksheet build request. Apply the Build Approval Guardrail before executing.

**Typical patterns:**
- `"path/to/file.pdf" for Christina`
- `Build this for maya: C:\...\worksheet.jpg`
- A bare PDF path on its own line when a child is clear from context

**In chat-based builds (without CLI):**
1. Read all framework files (`framework/DESIGN_SYSTEM.md`, `framework/INTERACTION_PATTERNS.md`, `framework/BUILD_CONSTRAINTS.md`, `framework/WORKSHEET_TYPES.md`) and `profiles/{child}/PROFILE.md` before writing any code.
2. Match the worksheet to a type in `WORKSHEET_TYPES.md`.
3. Check `worksheets/reference/` for a canonical reference implementation of that type before inventing new patterns.
4. Write the complete HTML output to `worksheets/{child}/YYYY-MM-DD-{subject}.html`.
5. Append any `📋 Update Suggested` blocks after the HTML per the Update Propagation Format below.

## Code Style
- Prefer small, focused edits that preserve existing prompt/framework wording unless the task explicitly asks for content changes.
- Keep Python scripts straightforward and CLI-oriented; use standard library types (`Path`, `argparse`) as in `runners/`.
- For generated worksheet apps, keep output as one self-contained HTML document with inline CSS and vanilla JS.

## Architecture
- `SYSTEM_PROMPT.md` defines the global build behavior and goals.
- `framework/` contains reusable standards and patterns:
  - `DESIGN_SYSTEM.md`
  - `INTERACTION_PATTERNS.md`
  - `BUILD_CONSTRAINTS.md`
  - `WORKSHEET_TYPES.md`
- `profiles/{child}/PROFILE.md` contains child-specific constraints and preferences.
- `runners/cli.py` builds one worksheet, `runners/watcher.py` automates folder processing, and `runners/propagate.py` turns suggested framework/profile updates into PRs.
- `worksheets/{child}/` stores generated outputs as dated HTML files. `worksheets/reference/` holds canonical reference implementations for each worksheet type — check here first.
- `docs/` is the GitHub Pages publish target. Run `python runners/publish.py` to sync `worksheets/{child}/` → `docs/` and regenerate `docs/index.html`. It is not edited directly.
- `incoming/` is the watcher's drop folder. Files placed here are auto-built then moved to `incoming/done/`.
- `pending-updates.md` accumulates `📋` update blocks extracted from CLI builds. `runners/propagate.py` reads this file to open PRs.
- `tmp/debug-response.txt` captures the raw Claude API response from the last CLI build (created on demand; not committed).

## Build and Test
- Install Python dependencies: `python -m pip install -r requirements.txt`
- Build one worksheet: `python runners/cli.py --worksheet <path> --child <name> [--date YYYY-MM-DD] [--subject <slug>]`
- Watch incoming folder: `python runners/watcher.py`
- Publish worksheets to docs: `python runners/publish.py [--child <name>] [--push]`
- Propagate suggested updates: `python runners/propagate.py` (or `python runners/propagate.py --dry-run`)
- NPM script aliases are available:
  - `npm run build`
  - `npm run watch`
  - `npm run propagate`
  - `npm run publish`

## Runner Defaults and Environment
- CLI defaults:
  - `DEFAULT_CHILD` fallback is `maya` when `--child` is omitted.
  - `--subject` defaults to `worksheet`; `--date` defaults to today.
- Watcher defaults:
  - `CHILD` fallback is `christina` (different from CLI default).
  - `INCOMING_DIR` defaults to `./incoming`; processed files are moved to `incoming/done/`.
  - `OUTPUT_DIR` defaults to `./worksheets`.
  - `AUTO_COMMIT=true` enables git add/commit/push of generated worksheet output.
- Publish defaults:
  - Reads from `worksheets/<child>/` and regenerates `docs/index.html` (plus `docs/archive/index.html` when archive content exists).
  - Child must be provided via `--child` or `DEFAULT_CHILD`.

## Environment Variables (`.env`)

Required keys (copy `.env.example` or set manually):

| Variable | Required | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Claude API access — required for all builds |
| `ANTHROPIC_MODEL` | optional | Defaults to `claude-opus-4-5` in all runners |
| `DEFAULT_CHILD` | optional | Overrides per-runner child fallbacks |
| `GITHUB_TOKEN` | propagate only | PAT with `repo` scope; needed by `runners/propagate.py` |
| `GITHUB_REPO` | propagate only | `owner/repo` format, e.g. `lisac/hemi-homework` |
| `AUTO_COMMIT` | optional | Set `true` in watcher to auto-push generated output |

## Build Approval Guardrail
- Treat worksheet generation as a gated action in chat-first workflows.
- Do not execute build steps until explicit approval is present.
- Preferred approval phrase: `BUILD NOW`.
- Also accepted: `go ahead and build`, `ok build it`.
- If approval is ambiguous, ask one concise confirmation question instead of executing.

## Conventions
- Do not simplify academic content; remove access barriers while preserving learning goals.
- Follow framework constraints for generated HTML:
  - No external JS libraries
  - Inline CSS/JS
  - No form-based UX; prefer tap-first controls
  - Minimum 44x44 tap targets
- Keep worksheet filenames in `worksheets/{child}/` as `YYYY-MM-DD-subject.html`.
- For multi-section worksheets, default to one file per distinct exercise section (e.g., `...-a.html`, `...-b.html`, `...-c.html`) unless the user explicitly requests one combined file.
- Reuse established worksheet patterns from `framework/WORKSHEET_TYPES.md` before inventing new logic.
- If the model suggests framework/profile improvements, preserve `📋 ... Update Suggested` block structure so `runners/propagate.py` can parse it.

## Update Propagation Format
- Preferred rich format:
  - Heading like `## 📋 Framework Update — ...` or `## 📋 Profile Update — ...`
  - Include `**File:**`, `**Section:**`, and normal markdown body describing the confirmed change.
- Legacy compact format is still accepted:
  - Include `📋`, `**File:**`, and `**Change:**`.
- If a change spans multiple files, emit one update block per file.
- Keep suggestions in markdown so `runners/propagate.py` can parse and open PRs cleanly.

## Pitfalls
- `ANTHROPIC_API_KEY` is required for worksheet generation.
- Default model is read from `ANTHROPIC_MODEL`; runner fallback is `claude-opus-4-5`.
- `watchdog` is required for `runners/watcher.py` and is installed from `requirements.txt`.
- HTML output is considered valid only when it starts with `<!DOCTYPE`.
- `runners/propagate.py` needs `GITHUB_TOKEN` and `GITHUB_REPO` for PR creation.
- `runners/watcher.py` and `runners/cli.py` use different default child values unless explicitly configured.