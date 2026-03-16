# Project Guidelines

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
- `worksheets/{child}/` stores generated outputs as dated HTML files.

## Build and Test
- Install Python dependencies: `python -m pip install -r requirements.txt`
- Build one worksheet: `python runners/cli.py --worksheet <path> --child <name>`
- Watch incoming folder: `python runners/watcher.py`
- Propagate suggested updates: `python runners/propagate.py`
- NPM script aliases are available:
  - `npm run build`
  - `npm run watch`
  - `npm run propagate`

## Conventions
- Do not simplify academic content; remove access barriers while preserving learning goals.
- Follow framework constraints for generated HTML:
  - No external JS libraries
  - Inline CSS/JS
  - No form-based UX; prefer tap-first controls
  - Minimum 44x44 tap targets
- Keep worksheet filenames in `worksheets/{child}/` as `YYYY-MM-DD-subject.html`.
- Reuse established worksheet patterns from `framework/WORKSHEET_TYPES.md` before inventing new logic.
- If the model suggests framework/profile improvements, preserve `📋 ... Update Suggested` block structure so `runners/propagate.py` can parse it.

## Pitfalls
- `ANTHROPIC_API_KEY` is required for worksheet generation.
- Default model is read from `ANTHROPIC_MODEL` (fallback in runner code); unavailable model access can fail builds.
- HTML output is considered valid only when it starts with `<!DOCTYPE`.
- `runners/propagate.py` needs `GITHUB_TOKEN` and `GITHUB_REPO` for PR creation.