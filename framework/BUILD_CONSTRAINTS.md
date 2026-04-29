# Build Constraints

Rules that apply to every generated worksheet app and tool, regardless of profile or worksheet type.

---

## Output Format

- Single self-contained HTML file
- All CSS and JS inline — no external files except Google Fonts
- No `<form>` tags (use event handlers directly)
- No framework dependencies (vanilla JS only)
- `localStorage` and `sessionStorage` are available and encouraged — output runs as a local file or via GitHub Pages, not inside the Claude.ai artifact sandbox

---

## File Naming

### Worksheets
```
worksheets/{child-name}/YYYY-MM-DD-{subject-slug}.html
```

Examples:
- `worksheets/christina/2026-03-10-pronouns.html`
- `worksheets/christina/2026-03-12-fractions.html`

Subject slug: lowercase, hyphens, no special characters.

### Tools
```
tools/{subject}/_{tool-name}.html
```

Examples:
- `tools/math/subtraction.html`
- `tools/math/place-value.html`

Tools are not date-stamped — they are versioned by content, not by assignment date.

Each subject folder contains an `index.html` (child-friendly launcher listing all tools in that subject). The top-level `tools/index.html` lists all subject folders.

### Multi-Section / Multi-Page Splitting Rule

When a worksheet contains multiple distinct exercise sections (e.g. Part A and Part B on one page, or multiple pages), default to **one file per distinct exercise section**, not one file per physical worksheet page.

**Type-mapping rule (required):** Printed parts map to separate worksheet types in `framework/WORKSHEET_TYPES.md`. Even when a user asks for one combined app file, keep each part modeled as its own type pattern internally.

**Rationale:** Each section typically has a different interaction model, progress tracking scope, and cognitive demand. Combining them in one file creates a longer scroll and conflates progress across different skills. Separate files allow each section to be assigned, completed, and reviewed independently.

**Naming convention:**
```
worksheets/{child}/YYYY-MM-DD-{subject-slug}.html
```

### Multi-Section Single-App Layout (Card Navigation)

When a worksheet image contains two or more distinct skill sections (e.g. Commas + Adverbs) and the user requests a **single combined app**, use card-based tab navigation between sections rather than a long scroll:

- Render a fixed header bar with one named tab per section.
- Show one section at a time — hide non-active sections.
- Persist the active section index in `localStorage` alongside other answer state.
- Bump the storage key (`_v2`, `_v3`, etc.) if the section structure changes between builds.
- Keep section logic separated by type pattern (one type per printed part), even though delivery is one file.

**When to split into separate files instead:** Only when the user explicitly requests separate files, or when sections have incompatible interaction models that would make shared state error-prone.

---

## Touch / Accessibility

- Minimum tap target: 44px in both dimensions
- All interactive elements reachable by tap — no hover-only interactions
- No text selection required for any interaction
- Tappable content must be visually distinct (background + border, not underline alone)
- **Do not add microphone buttons to number-only input fields** — they provide no benefit and add visual clutter
- **Do not full re-render on every keystroke/change in editable controls** (`input`, `textarea`, `select`). Update progress/status text in place so focus and caret remain stable during typing and speech-to-text.
- If a full render is unavoidable, implement focus/caret capture-and-restore around render.

### Selective Read-Aloud

Not every section requires read-aloud. Matching/labeling sections (e.g. Type 1B: match subject pronoun to possessive pronoun) where the interaction is purely visual and the words are short labels do not benefit from TTS and should omit it entirely:

- Remove `cursor: pointer` and `onclick` from label elements
- Remove `speak()` calls from `onchange` handlers
- Change the instructions box from tappable (blue, `onclick`) to static (keep the blue style but set `cursor: default` and no `onclick`)

Only add read-aloud where it removes a genuine barrier — reading a full sentence aloud, confirming a selected answer in context, or speaking a definition. Single-word labels and match arrows do not need it.

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

### Transcribe the original text exactly — do not silently correct errors

When building a Type 4 proofreading worksheet, transcribe the passage **exactly as it appears in the original scan**, including all seeded errors and all structural problems. The student's job is to find these problems.

**Run-on sentences (missing period):** Represent as one card with the full run-on text. Example: `"The arctic fox has a thick coat of fur to protect it from the cold this thick fur also covers its paws and tale."` — the missing period after "cold" and the un-capitalized "this" are both errors on the same card. Do not split into two clean sentences.

**Wrongly split sentences (period where comma belongs):** Also represent as one card. Example: `"Like the arctic fox. The arctic hare also changes color according to the season."` — the period after "fox" should be a comma and "The" should be lowercase.

**Species names are not proper nouns.** "arctic fox" and "arctic hare" are NOT capitalization errors — they are common noun phrases used generically. Only flag "Arctic" as a capitalization error when used as a place name ("Arctic Ocean", "the Arctic").

**Bump the storage key when sentence count changes.** Use `_v2`, `_v3`, etc. to prevent stale localStorage (keyed to the old sentence array length) from corrupting the new layout on reload.

### Verify all word indices programmatically before writing data

Never assign `wordIndex` by reading the sentence by eye. Always verify:

```javascript
const text = "The sentence text exactly as it appears in the data.";
text.split(' ').forEach((w, i) => console.log(i, w));
```

Incorrect indices are silent failures — the submit logic never matches and every attempt shows the generic hint regardless of what the student selects.

### Validate the full sentences array before building the UI

After writing the data, run a validation pass to confirm each `wordIndex` resolves to the expected word:

```javascript
sentences.forEach((s, si) => {
  if (!s.hasError) return;
  s.errors.forEach(e => {
    const word = s.text.split(' ')[e.wordIndex];
    console.log(`S${si+1} wi=${e.wordIndex}:`, JSON.stringify(word), e.errorType);
  });
});
```

Review the output before proceeding. Any mismatch must be corrected in the data, not guessed at.

*Trigger: Multiple word index errors and missed/reordered sentences discovered during iteration on the Arctic Animals worksheet. All of the above patterns were confirmed working in the reference implementation.*

---

## Build Behavior

- Do not ask clarifying questions before building unless the ambiguity would require a full rebuild if guessed wrong
- Note your interpretation of ambiguous content at the top of your response, then proceed
- Do not include setup instructions, "open in browser" notes, or other operational guidance in responses
- Parse worksheet content from the uploaded image/PDF directly — do not ask the user to transcribe it
- When a worksheet contains multiple distinct exercise sections, default to creating one file per section (see Multi-Section / Multi-Page Splitting Rule above)
- Regardless of file packaging, map each printed section to a separate worksheet type pattern (do not merge Part A/B/C into one type definition)
- For Activity 1 proofreading outputs (`activities/proofreading/{child}/...`), treat `activities/proofreading/template.html` as immutable: edit only the top `#worksheetData` JSON block in the copied output file.

---

## Response Format When Generating

1. If worksheet type is known from taxonomy: build directly
2. If worksheet type is new: one sentence naming your interpretation and interaction model, then build
3. Output the complete HTML file
4. If you identified anything that should update the framework or profile files, append a **📋 Update Suggested** block (see `CONTRIBUTING.md`)