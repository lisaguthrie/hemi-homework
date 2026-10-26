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

### Paired Source and Docs Copies (Required)

Whenever a student-facing worksheet, lesson launcher, tool, activity, index, or public supporting asset is **created or changed**, keep **two identical copies**: one in the source folders under `hemi-homework/` and one in the matching publishable folder under `hemi-homework/docs/`. This applies to revisions as well as first builds, including changes made after testing or user feedback.

| Artifact | Source location | Published mirror |
|---|---|---|
| Worksheet or lesson launcher | `worksheets/{child}/{filename}.html` | `docs/worksheets/{filename}.html` |
| Tool page, index, or supporting asset | `tools/{relative-path}` | `docs/tools/{relative-path}` |
| Activity instance | `activities/{type}/{child}/{filename}.html` | `docs/activities/{type}/{filename}.html` |
| Shared activity index or other publishable asset | `activities/{relative-public-path}` | `docs/activities/{relative-public-path}` |

**Path conventions:** The current `docs/worksheets/` folder is flat; do not add a child subfolder for worksheet output. The current activity instance mirror likewise omits the child segment (`docs/activities/proofreading/{filename}.html`). Keep any subject or type subfolders used by tools and activities. Use the same filename and final contents in each pair. Before writing to a flat destination, check for filename collisions across children; choose an unambiguous new filename and update references rather than overwriting another child's work.

**Required delivery check:**

1. Build or revise the source copy and validate it.
2. Create or update the corresponding `docs/` copy from the **same final content**; create missing public subfolders when appropriate.
3. Mirror related launchers, index changes, and public assets, and check that relative links and asset paths work from both copies.
4. Read back or list **both** destinations and compare names and file sizes, preferably content hashes as well. If either write or verification fails, report the incomplete pair; do not claim the artifact is fully delivered.
5. When working on Google Drive only, update both Drive folders without creating a GitHub commit. Respect explicit instructions about whether GitHub may be modified.

This is a rule for **publishable student-facing files**, not a request to copy private/source-only materials into `docs/`. Keep `SYSTEM_PROMPT.md`, `framework/`, `profiles/`, `.env`, runner code, and other private or implementation-only files out of `docs/`; never expose child profiles or secrets. Updating the instructions does not by itself synchronize files edited outside this build workflow.

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
- Tappable content must normally be visually distinct (background + border, not underline alone). **Exception:** per-word TTS in continuous prose may use visually unstyled inline word targets so the sentence still reads as normal text; keep keyboard focus styling and reserve persistent visual affordances for the actual answer controls.
- **Do not add microphone buttons to number-only input fields** — they provide no benefit and add visual clutter
- **Do not full re-render on every keystroke/change in editable controls** (`input`, `textarea`, `select`). Update progress/status text in place so focus and caret remain stable during typing and speech-to-text.
- If a full render is unavoidable, implement focus/caret capture-and-restore around render.

### Passage + Free-Text Variants

- Honor explicit microphone inclusion/omission requests, including delivering both variants. Speech recognition availability must never gate typing, autosave, read-back, or print export.
- Use distinct persistence keys for separate variants so their responses cannot overwrite one another.
- Preserve original passage paragraphs across printed page breaks. Store sentence boundaries explicitly when abbreviations make automatic splitting unsafe.
- Keep passage and question scrolling independent in a two-pane layout, and retain both panes on small screens.
- Inline definition controls must be independent of question read-aloud and answer editing.
- For open-ended written responses, count nonempty responses as answered without marking them correct or applying exact-string grading.
- Simulated microphone tests establish event handling only; document live capture as unverified until tested in the target browser.

### Export / Print Student Name

- When an export has a student name line, take the exact name/identifier from the current child's profile, not from a previous lesson's reference HTML. Old `Tina #18` reference exports must not override the current `Tina #14` profile setting.
- Do not hardcode a child's name or identifier into a general framework component; keep that value child-specific, and never commit private child profile contents to GitHub.
- **Source-matched date line:** Include a date line in an Export / Print view **only when the original worksheet includes one**. Do not automatically add a `Date:` line or populate today's date when the printed source has no date field. Preserve existing printed header fields rather than imposing a generic Name / Date header.

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

### Whole-Worksheet Review — Three Chances by Default

For every worksheet with objectively checkable responses, the **default is exactly three opportunities to check the complete worksheet**, unless the user explicitly requests a different model. This policy supersedes older reference examples that use instant correctness, unlimited checks, per-question `Check answer` buttons, or adult-check-only feedback.

- Put the single **Check all responses** action and the remaining-check count **at the bottom of the worksheet**, after all question cards. Never distribute the three chances across individual problems. A separately delivered exercise file gets its own three-check allowance.
- Before each check, look for unanswered questions. If any are incomplete, first show a clear, accessible inline warning naming the unanswered question numbers. Offer **Keep working** or **Check anyway**. Showing or dismissing the warning does **not** consume a check; only the explicit confirmation evaluates and consumes one of the remaining chances.
- Every confirmed check evaluates **all questions**, including those left unanswered. Display distinct states for **correct** (green ✅), **answered but needs review** (warm orange 💡), and **unanswered** (neutral/dashed ○). Incorrect and unanswered must never look the same. Do not reveal individual correct letters or a full answer key in response to a check.
- For multiple-selection questions, correctness means that the **entire selected set** matches the verified answer set: missing or extra selections require review. Choosing one option counts as *answered* for warning purposes if the question permits one or more answers, even if more choices are actually correct. For a task requiring exactly two choices, fewer than two counts as unanswered/incomplete.
- Let the student revise responses between checks without showing live correctness. If a checked answer changes, clear **only that question's stale feedback** and identify it as revised until the next whole-worksheet check; other unchanged reviewed states may remain visible.
- Persist answers, attempts consumed, review status, and revised markers in `localStorage`. Reloading cannot grant more chances. After the third check, disable further checks but permit editing and Export / Print; double-tap **Clear all responses** remains an explicit full reset. If everything is correct, mark completion without spending additional checks.
- **Require a reliable answer key** for automatic evaluation. Prefer a supplied or publisher/teacher key; verify it against the exact printed edition and choices. For fixed-response multi-select exercises, proactively look for an edition-matched publisher/teacher key when the student pages omit answers; do not choose adult-check-only solely because the uploaded student worksheet has no key. Compare question wording, answer letters, and option order before using the key, and record its provenance in implementation notes. Do not fabricate a key from ambiguous semantics. If a trustworthy key cannot be established, report the limitation and obtain a valid key or explicit alternate checking instructions before claiming an auto-checking build is complete.
- Free-form writing, creative completions, and other responses without an objectively verifiable key remain adult-review tasks **only as an explicit type-level or user-requested exception**. Do not impose exact-string grading on meaningful open-ended answers or replace them with easier multiple choice just to enable checking.
- After implementing, verify the full check lifecycle: incomplete warning and zero attempt consumption, exact-set answer grading, all three attempts and reload persistence, distinct status styles, stale-result clearing on edit, and continued editing after attempts run out.

Use `framework/INTERACTION_PATTERNS.md` → **Whole-Worksheet Three-Chance Review (Default)** for reusable wiring.

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