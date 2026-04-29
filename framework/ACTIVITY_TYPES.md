# Activity Types

Activities are different from worksheets. A worksheet's interaction model varies by type — the container is rebuilt each time from a type pattern. An activity has a **fixed, reusable container** that ships as a template. Only the content changes (passage, error data, corrected sentences, comprehension questions). The engine, CSS, and all interaction logic are identical across every instance of the same activity type.

For worksheet taxonomy behavior (including the rule that printed Part A / Part B / Part C sections map to separate worksheet types), follow `framework/WORKSHEET_TYPES.md` and `framework/BUILD_CONSTRAINTS.md`. This file defines activity templates only.

When you need to create a new proofreading activity, do not rebuild the container — fill in the template. NEVER use a prior instance of the same activity type as a base — fill in the template. 

**Non-negotiable template rule:** For `activities/proofreading/*.html` outputs, copy `activities/proofreading/template.html` as-is and edit only the top `#worksheetData` JSON block. Do not modify HTML structure, CSS, JS logic, or print/export layout outside that JSON block. Do not use any other files as a template.

---

## Activity 1: Proofreading + Comprehension

**Template:** `activities/proofreading/template.html`

### What it does

The student works through a passage sentence by sentence using standard proofreading marks, then answers comprehension questions about the corrected passage. Two phases:

1. **Proofreading phase** — passage panel always visible at top; one sentence work card active at a time. First pass, then automatic second pass for any missed sentences.
2. **Comprehension phase** — proofreading UI hides; corrected passage card + open-response questions appear.

The interaction model is identical every time. Only the top JSON data block changes.

---

### What to fill in

Four things change per instance. All are at the top of the `<script>` block, clearly marked with `// CONTENT:` comments.

#### 1. `sentences` — the passage with errors seeded in

```javascript
const sentences = [
  // No-error sentence
  {
    text: "Exact sentence text as it appears, errors preserved.",
    hasError: false, noError: true,
    feedbackOk: "Right! This sentence is correct."
  },
  // Single-error sentence
  {
    text: "Exact sentence text as it appears, errors preserved.",
    hasError: true,
    errors: [
      {
        wordIndex: 3,              // 0-based index in text.split(' ') — verify programmatically
        errorType: "capitalize",   // see Mark Type IDs below
        altErrorType: null,        // optional second accepted mark, or null
        feedbackCorrect: "Yes! [Word] is a proper noun and should be capitalized.",
        correctSpelling: null      // corrected word string, only for spelling errors
      }
    ],
    errorNote: "Brief description for wrong-mark hint",
    feedbackHint: "Hint shown when student chooses Looks good on an error sentence, or picks wrong word/mark."
  },
  // Multi-error sentence
  {
    text: "Exact sentence text as it appears.",
    hasError: true,
    errors: [
      { wordIndex: 2,  errorType: "spelling",   altErrorType: null, feedbackCorrect: "...", correctSpelling: "together" },
      { wordIndex: 10, errorType: "punctuation", altErrorType: "comma", feedbackCorrect: "...", correctSpelling: null }
    ],
    errorNote: "Two errors in this sentence",
    feedbackHint: "There are two errors in this sentence — ..."
  }
];
```

**Mark type IDs:** `capitalize` | `lowercase` | `delete` | `comma` | `spelling` | `apostrophe` | `punctuation` | `verb`

**`wordIndex` verification:** Split the sentence string on spaces and count from 0. Punctuation attached to a word (e.g. `bears,`) counts as part of that token.

**`altErrorType`:** Use when two marks are both defensible for the same error (e.g. `comma` and `punctuation` for a missing comma). The engine accepts either.

#### 2. `correctedSentences` — the fully corrected passage

```javascript
const correctedSentences = [
  "Sentence one, fully corrected.",
  "Sentence two, fully corrected.",
  // one string per sentence — shown in the corrected passage reference card
];
```

Note: if the original has two sentences run together (common in multi-error sentences), the corrected version may need to be split into two strings.

#### 3. `compQuestions` — comprehension questions

```javascript
const compQuestions = [
  { text: "What does the title mean?", num: 1 },
  { text: "Name two things that happen in spring.", num: 2 },
  // ...
];
```

Open-response only — no answer key. Student speaks or types. Typically 3–5 questions.

#### 4. `STORAGE_KEY` — unique localStorage key

```javascript
const STORAGE_KEY = 'worksheet_proofreading_{topic}_{YYYY_MM_DD}_v1';
```

Replace `{topic}` and `{YYYY_MM_DD}` with the subject slug and date. Increment `v1` if the content is revised in a way that would make old saved state incompatible (e.g. sentence count changes).

---

### Page metadata to update

In the `<head>`:
```html
<title>PASSAGE TITLE</title>
```

In the `<body>`:
```html
<h1>🦁 PASSAGE TITLE</h1>
<p class="subtitle">Proofreading Practice + Comprehension Questions</p>
```

In `exportPrint()`, update the print document title and footer date:
```javascript
<title>PASSAGE TITLE — Marked Worksheet</title>
...
<h1>PASSAGE TITLE</h1>
...
<div class="footer">PASSAGE TITLE · Generated YYYY-MM-DD</div>
```

---

### Output path

Save completed instances to:
```
activities/proofreading/{child}/YYYY-MM-DD-{subject}.html
```

Example: `activities/proofreading/christina/2026-04-20-polar-bears.html`
