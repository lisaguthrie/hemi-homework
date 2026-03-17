# Build Constraints

Rules that apply to every generated worksheet app, regardless of profile or worksheet type.

---

## Output Format

- Single self-contained HTML file
- All CSS and JS inline — no external files except Google Fonts
- No `<form>` tags (use event handlers directly)
- No framework dependencies (vanilla JS only)
- `localStorage` and `sessionStorage` are available and encouraged — output runs as a local file or via GitHub Pages, not inside the Claude.ai artifact sandbox

---

## File Naming

```
worksheets/{child-name}/YYYY-MM-DD-{subject-slug}.html
```

Examples:
- `worksheets/christina/2026-03-10-pronouns.html`
- `worksheets/christina/2026-03-12-fractions.html`

Subject slug: lowercase, hyphens, no special characters.

### Multi-Section / Multi-Page Splitting Rule

When a worksheet contains multiple distinct exercise sections (e.g. Part A and Part B on one page, or multiple pages), default to **one file per distinct exercise section**, not one file per physical worksheet page.

**Rationale:** Each section typically has a different interaction model, progress tracking scope, and cognitive demand. Combining them in one file creates a longer scroll and conflates progress across different skills. Separate files allow each section to be assigned, completed, and reviewed independently.

**Naming convention:**
```
worksheets/{child}/YYYY-MM-DD-{subject-slug}-{section}.html
```
Where `{section}` is a lowercase letter (a, b, c) or a short descriptor (e.g. `-pairs`, `-label`, `-choose`).

**Example:** A worksheet with Part A (identify antecedent), Part B (label S/O), and a second page (choose correct pronoun) becomes three files:
- `2026-03-16-subj-obj-pronouns-a.html`
- `2026-03-16-subj-obj-pronouns-b.html`
- `2026-03-16-subj-obj-pronouns-c.html`

**Override:** If the user explicitly requests a single file, or if the sections are closely interdependent (e.g. Part B refers to answers from Part A), combine them and use section headers within the page.

---

## Touch / Accessibility

- Minimum tap target: 44px in both dimensions
- All interactive elements reachable by tap — no hover-only interactions
- No text selection required for any interaction
- Tappable content must be visually distinct (background + border, not underline alone)
- **Do not add microphone buttons to number-only input fields** — they provide no benefit and add visual clutter

---

## Answer Data

Correct answers live in the JavaScript data object, not hardcoded in HTML. This makes answer keys easy to correct without touching markup.

### String Quoting in feedbackCorrect

When a `feedbackCorrect` string needs to show a word that contains an apostrophe (e.g. `change's`), do not escape the apostrophe with a backslash inside a double-quoted JS string — the backslash will be visible to the user. Instead, wrap the word in double quotes within the string:

```javascript
// Wrong — backslash visible to user:
feedbackCorrect: "Good catch! 'change\\'s' has a wrong apostrophe — it should be 'changes.'"

// Correct — double-quotes around the word:
feedbackCorrect: "Good catch! \"change's\" has a wrong apostrophe — it should be 'changes.'"
```

*Trigger: Backslash appeared literally in feedback text shown to user.*

---

## Build Behavior

- Do not ask clarifying questions before building unless the ambiguity would require a full rebuild if guessed wrong
- Note your interpretation of ambiguous content at the top of your response, then proceed
- Do not include setup instructions, "open in browser" notes, or other operational guidance in responses
- Parse worksheet content from the uploaded image/PDF directly — do not ask the user to transcribe it
- When a worksheet contains multiple distinct exercise sections, default to creating one file per section (see Multi-Section / Multi-Page Splitting Rule above)

---

## Response Format When Generating

1. If worksheet type is known from taxonomy: build directly
2. If worksheet type is new: one sentence naming your interpretation and interaction model, then build
3. Output the complete HTML file
4. If you identified anything that should update the framework or profile files, append a **📋 Update Suggested** block (see `CONTRIBUTING.md`)