# Worksheet Accessibility App Builder

Converts scanned homework worksheets into accessible single-page web apps, customized for a specific child's barriers and needs. Also maintains a library of reusable **math and literacy tools** the child can use independently alongside paper worksheets.

---

## Quick Start

```bash
python -m pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...

# Build one worksheet
python runners/cli.py --worksheet path/to/worksheet.pdf --child maya

# Watch a folder for new worksheets (automated)
python runners/watcher.py
```

Output lands in `worksheets/{child}/YYYY-MM-DD-subject.html`.

Suggested command order (chat-first):
1. `/Worksheet Intake`
2. `Worksheet Brainstorm` (approach only)
3. `Worksheet Coach` and then `BUILD NOW` when ready
4. `python runners/propagate.py` if update suggestions are produced and accepted

Suggested command order (CLI-first):
1. `python runners/cli.py --worksheet <path> --child <n> [--subject <subject>]`
2. Review generated output in `worksheets/{child}/`
3. `python runners/propagate.py` if update suggestions are produced and accepted
4. `python runners/watcher.py` when you want ongoing folder-based automation

---

## VS Code Chat Workflow (Optional)

If you want a guided chat-first flow before building:

1. Run `/Worksheet Intake` to provide:
	- worksheet path
	- child
	- notes
2. Use **Worksheet Brainstorm** for read-only planning (never builds).
3. Use **Worksheet Coach** when ready to build; it waits for explicit approval and can auto-apply suggested framework/profile updates.

Customization files:
- `.github/prompts/worksheet-intake.prompt.md`
- `.github/agents/worksheet-brainstorm.agent.md`
- `.github/agents/worksheet-coach.agent.md`
- `.github/instructions/runner-approval.instructions.md`

---

## How It Works

1. The **framework files** (`framework/`) contain generalizable knowledge: design system, interaction patterns, build constraints, worksheet type taxonomy, tool type taxonomy
2. The **child profile** (`profiles/{child}/PROFILE.md`) contains what's specific to one child: their barriers, what works, design overrides
3. The **runners** assemble these files into a system prompt, send it to the Claude API along with the worksheet image/PDF, and write the HTML output
4. The **propagation runner** takes confirmed improvements and opens GitHub PRs to update the framework files

The model's job is identical whether you're running from the CLI, a folder watcher, or claude.ai manually — only the I/O mechanism differs.

---

## Two Output Types

### Worksheets (`worksheets/{child}/`)
Reproduce a specific assignment as an accessible app. Each problem card has:
- Tap-to-speak on all text
- A **💡 Hint** button that breaks the problem into mathematical steps and links to the relevant tool(s)
- Answer input appropriate to the problem type

### Tools (`tools/{subject}/`)
General-purpose computation helpers the child operates herself. She enters the numbers from her paper worksheet and works through the problem step by step. Tools are reusable across any assignment.

Current tools:
- `tools/math/subtraction.html` — vertical subtraction with tap-to-borrow

See `framework/TOOL_TYPES.md` for the full tool taxonomy and conventions.

---

## Using with claude.ai (manual workflow)

Attach these files to a new conversation:
- `SYSTEM_PROMPT.md`
- `framework/DESIGN_SYSTEM.md`
- `framework/INTERACTION_PATTERNS.md`
- `framework/BUILD_CONSTRAINTS.md`
- `framework/WORKSHEET_TYPES.md`
- `framework/TOOL_TYPES.md`
- `profiles/{child}/PROFILE.md`
- The worksheet PDF or image

Then send: *"Build an accessible worksheet app for [child] from this worksheet."*

---

## Adding a New Child

```bash
cp profiles/PROFILE_TEMPLATE.md profiles/{name}/PROFILE.md
# Edit profiles/{name}/PROFILE.md
```

---

## Propagating Improvements

When you confirm an improvement works during iteration:

1. The model appends a `📋 Update Suggested` block to its response
2. Run `python runners/propagate.py` to auto-PR the changes
3. Review and merge the PR on GitHub

Or manually: download the updated file from claude.ai and commit it yourself.

---

## GitHub Pages Setup

1. Push this repo to GitHub
2. Go to Settings → Pages → Source: `main` branch, `/` root (or `/docs` if you prefer)
3. Worksheets are accessible at `https://{you}.github.io/{repo}/worksheets/{child}/`
4. Tools are accessible at `https://{you}.github.io/{repo}/tools/`

For the watcher's auto-commit to trigger a Pages deploy, set `AUTO_COMMIT=true` in your environment.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |
| `GITHUB_TOKEN` | For propagate.py | Personal access token with R/W permissions for Contents and Pull Requests |
| `GITHUB_REPO` | For propagate.py | `owner/repo-name` |
| `INCOMING_DIR` | No | Folder to watch (default: `./incoming`) |
| `OUTPUT_DIR` | No | Output folder (default: `./worksheets`) |
| `CHILD` | No | Child profile to use (default: `maya`) |
| `AUTO_COMMIT` | No | `true` to auto-commit watcher output |

---

## File Structure

```
/
├── framework/
│   ├── DESIGN_SYSTEM.md          # visual design tokens and CSS components
│   ├── INTERACTION_PATTERNS.md   # JS patterns: TTS, STT, answer handling, persistence
│   ├── BUILD_CONSTRAINTS.md      # output rules, file naming, build behavior
│   ├── WORKSHEET_TYPES.md        # taxonomy of known worksheet types
│   ├── TOOL_TYPES.md             # taxonomy of known tools and tool conventions
│   └── CONTRIBUTING.md           # update propagation protocol
│
├── profiles/
│   ├── PROFILE_TEMPLATE.md       # blank template for a new child
│   └── {child}/
│       └── PROFILE.md            # filled-in profile
│
├── runners/
│   ├── cli.py                    # build one worksheet from command line
│   ├── watcher.py                # watch folder, auto-process new worksheets
│   └── propagate.py              # apply update suggestions → GitHub PRs
│
├── worksheets/
│   └── {child}/
│       └── YYYY-MM-DD-subject.html
│
├── tools/
│   ├── index.html                # top-level subject launcher (child-facing)
│   └── math/
│       ├── index.html            # math tools launcher (child-facing)
│       └── subtraction.html      # vertical subtraction with tap-to-borrow
│
├── incoming/                     # drop worksheet scans here (watcher picks up)
│   └── done/                     # processed worksheets moved here
│
├── pending-updates.md            # staging area for framework update suggestions
├── requirements.txt
├── SYSTEM_PROMPT.md              # assembly instructions for the model
├── package.json
└── README.md
```
