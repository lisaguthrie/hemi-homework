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

---

## Build Behavior

- Do not ask clarifying questions before building unless the ambiguity would require a full rebuild if guessed wrong
- Note your interpretation of ambiguous content at the top of your response, then proceed
- Do not include setup instructions, "open in browser" notes, or other operational guidance in responses
- Parse worksheet content from the uploaded image/PDF directly — do not ask the user to transcribe it

---

## Response Format When Generating

1. If worksheet type is known from taxonomy: build directly
2. If worksheet type is new: one sentence naming your interpretation and interaction model, then build
3. Output the complete HTML file
4. If you identified anything that should update the framework or profile files, append a **📋 Update Suggested** block (see `CONTRIBUTING.md`)
