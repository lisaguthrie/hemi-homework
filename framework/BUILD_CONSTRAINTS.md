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

---

## Response Format When Generating

1. If worksheet type is known from taxonomy: build directly
2. If worksheet type is new: one sentence naming your interpretation and interaction model, then build
3. Output the complete HTML file
4. If you identified anything that should update the framework or profile files, append a **📋 Update Suggested** block (see `CONTRIBUTING.md`)