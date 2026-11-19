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

---

## Wordly Wise activities (Activities 2–9)

Activities 2–9 share one pattern: a Wordly Wise lesson section (8A, 8B, 8C, …) delivered as a **template-driven activity** instead of a rebuilt worksheet. Each has `template.html` plus a `README.md` in `activities/{type}/`. The rules are the same as for proofreading:

- Copy `template.html` as-is — never a prior instance — and edit **only the JSON in the `<script type="application/json" id="activityConfig">` block**. Do not change HTML, CSS, or JS.
- `meta.storageKey` must be unique per instance (progress autosaves under it). Pattern: `ww{book}_lesson_{N}{letter}_{type}_{child}_{YYYY_MM_DD}_v1`.
- Save to `activities/{type}/{child}/YYYY-MM-DD-wordly-wise-lesson-{N}{letter}-{type}.html`. `runners/publish.py` flattens these to `docs/activities/{type}/`.
- Correct answers live in the config JSON, never in markup.
- Source content comes from the scanned worksheet. If the scan does not show the answer key, work answers out from the word meanings and flag the ambiguous items to the user.

Use the activity template when the worksheet section matches one of the types below; fall back to a worksheet build (see `WORKSHEET_TYPES.md`) only if it does not.

### Activity 2: Using Words in Context

**Template:** `activities/using-words-in-context/template.html` (see its `README.md`)

Shape: sentences that either use a vocabulary word correctly or incorrectly. The student taps **C** (correct) or **I** (incorrect).

Config:
- `meta` — `title`, `subtitle`, `instructions`, `storageKey`, `speechRate`, `speechPitch`, `maxChecks`
- `words[]` — `word`, `definition` (spoken when the word button is tapped), `sentences[]`
- `sentences[]` — `text`, `correctUse` (true/false), `hint` (short concept-based explanation shown after checking)

Behaviour: tapping a vocabulary word reads word + definition; tapping a sentence reads it; choosing C/I reads the sentence back; large C/I controls; progress pips; checks limited by `maxChecks`.

Reference instance: `activities/using-words-in-context/christina/2026-11-09-wordly-wise-lesson-8a-using-words-in-context.html`.

### Activity 3: Making Connections

**Template:** `activities/making-connections/template.html` (see its `README.md`)

Shape: each prompt is a phrase with a key word or phrase; the student picks which of four vocabulary words/choices connect to it. One or more choices may be correct.

Config:
- `meta` — `lessonLabel`, `title`, `instructions`, `storageKey`, `backHref`, `backLabel`, `bookLabel`, `printTitle`, `studentName`
- `words[]` — `word` + `senses[]` (`form`, `pos` of `n`/`v`/`adj`/`adv`, `num`, `definition`, `example`); powers tap-for-definition
- `formPairs` — optional map of word → inflected forms that should be tappable (defaults to the word itself)
- `questions[]` — `[prompt, [4 choices], "answer letters", hint]`. Wrap the key phrase in `<em>…</em>`: it is displayed but never read aloud. Answer letters are `a`–`d`, e.g. `"bc"`.

Reference instance: built from Lesson 8B (`worksheets/christina/2026-11-10-wordly-wise-lesson-8b-making-connections.html`).

Note: the template's README still says to save to `worksheets/{child}/`; use `activities/making-connections/{child}/` as above.

### Activity 4: Determining Meanings

**Template:** `activities/determining-meanings/template.html` (see its `README.md`)

Shape: each item gives a sentence stem (containing the vocabulary word) and four endings; one or more endings correctly complete the stem. The student selects every ending that works.

Config: same `meta` / `words` / `formPairs` structure as Making Connections, plus:
- `questions[]` — `[stem, [4 endings], "answer letters", hint]`. The stem is read together with each ending when an ending is tapped or selected, so write the stem so it flows into every ending. Answer letters are `a`–`d`, e.g. `"ad"`.
- `formPairs` should list every inflected form that appears in a stem (e.g. `convenient` → `convenience`; `captive` → `captivity`; `ecstasy` → `ecstatically`), since the printed stem often uses a different form than the word bank.

Include every word in the lesson's word bank in `words`, not just those in the questions.

Reference instance: `activities/determining-meanings/christina/2026-11-11-wordly-wise-lesson-8c-determining-meanings.html`.

### Activity 5: Completing Sentences

**Template:** `activities/completing-sentences/template.html` (see its `README.md`)

Shape: each item is a sentence stem containing a vocabulary word (e.g. "A food that has fiber is"). The student finishes the sentence in their own words by typing or dictating. Open-response — there is no answer key and no checking.

Config:
- `meta` — `lessonLabel`, `title`, `instructions`, `wordListLabel`, `storageKey`, `backHref`, `backLabel`, `bookLabel`, `printTitle`, `studentName`
- `words[]` — `word` + `senses[]` (`form`, `pos` of `n`/`v`/`adj`/`adv`, `num`, `definition`, `example`); powers tap-for-definition. Include every word in the lesson's word bank.
- `formPairs` — optional map of word → inflected forms that should be tappable in stems
- `questions[]` — array of stem strings, exactly as printed

Behaviour: tap a vocabulary word for its definition; tap a stem or ▶ to hear it; one textarea per stem with **🎤 Dictate** speech-to-text (continuous, auto-restarts when the browser ends a session, ignores silence, appends finished phrases, stops text-to-speech and the tab-hidden event, reports a blocked microphone, disabled where unsupported); **▶ Read my answer** reads stem + ending; progress pips; autosave; double-tap Clear; Export / Print. No checks, no scoring — an adult reviews meaning.

Reference instance: none yet; the template ships with Lesson 6D content (from `worksheets/christina/archive/2026-10-26-wordly-wise-lesson-6d-completing-sentences.html`).

### Activity 6: Vocabulary in Context

**Template:** `activities/vocabulary-in-context/template.html` (see its `README.md`)

Shape: the "E" section of a Wordly Wise lesson. A reading passage sits beside a list of comprehension questions; the student answers each with a complete sentence by typing or dictating. Questions that do not already contain a lesson word get a "use one lesson word" menu (each word usable once). Open-response — there is no answer key and no checking.

Config:
- `meta` — `lessonLabel`, `title`, `passageTitle`, `instructions`, `wordListLabel`, `storageKey`, `backHref`, `backLabel`, `bookLabel`, `printTitle`, `studentName`
- `words[]` — `word` + `senses[]` (`form`, `pos` of `n`/`v`/`adj`/`adv`, `num`, `definition`, `example`); powers tap-for-definition and the word menus. Include every word in the lesson's word bank.
- `formPairs` — word → every inflected form that appears in the passage or questions and should be tappable (e.g. `originate` → `origin`, `originated`)
- `passage[]` — paragraphs, each an array of sentence strings exactly as printed (the sentence is the tap-to-hear unit)
- `questions[]` — question strings, exactly as printed

Behaviour: passage and questions side by side on wide screens (stacked on narrow); tap a sentence, ▶ paragraph, question, or the directions to hear it; tap a highlighted vocabulary word for its definition; per-question textarea with **🎙️ Dictate** (same continuous, auto-restarting speech-to-text as Completing Sentences) and **▶ Read my answer**; progress pips; autosave; double-tap Clear; Export / Print. No checks, no scoring — an adult reviews meaning.

Output path: `activities/vocabulary-in-context/{child}/YYYY-MM-DD-wordly-wise-lesson-{N}e-vocabulary-in-context.html`.

Reference instance: none yet; the template ships with Lesson 7E content (from `worksheets/christina/archive/2026-11-02-wordly-wise-lesson-7e-vocabulary-in-context.html`).

### Activity 7: Finding Meanings

**Template:** `activities/finding-meanings/template.html` (see its `README.md`)

Shape: the "A" section of a Wordly Wise lesson. Each item offers four phrases; the student picks the **two** that join into a sentence correctly using a lesson word.

Config:
- `meta` — `lessonLabel`, `title`, `instructions`, `wordListLabel`, `storageKey`, `backHref`, `backLabel`, `bookLabel`, `printTitle`, `studentName`
- `words[]` — `word` + `senses[]` (`form`, `pos` of `n`/`v`/`adj`, `num`, `definition`, `example`); powers the word bank and tap-for-definition. Include every word in the lesson's word bank.
- `formPairs` — word → inflected forms that should be tappable
- `questions[]` — `[[4 phrases in printed order], "two answer letters", hint]`, e.g. `"ba"` (order irrelevant)

Behaviour: pick exactly two phrases; the assembled sentence previews and is read aloud; 3 checks, progress pips, adult-unlockable extra check, autosave, double-tap Clear, Export / Print (shared behaviour below).

Output path: `activities/finding-meanings/{child}/YYYY-MM-DD-wordly-wise-lesson-{N}a-finding-meanings.html`.

Reference instance: none yet; the template ships with Lesson 7A content (from `worksheets/christina/archive/2026-11-02-wordly-wise-lesson-7a-finding-meanings.html`).

### Activity 8: Just the Right Word

**Template:** `activities/just-the-right-word/template.html` (see its `README.md`)

Shape: the "B" section of a Wordly Wise lesson. Each sentence contains a bold phrase; the student replaces it with a single lesson word (or a form of one) chosen from a drop-down menu.

Config:
- `meta` — `lessonLabel`, `title`, `instructions`, `wordListLabel`, `storageKey`, `backHref`, `backLabel`, `bookLabel`, `printTitle`, `studentName`
- `words[]` — `word` + `senses[]` (`form`, `pos` of `n`/`v`/`adj`/`adv`, `num`, `definition`, `example`); powers the word bank and tap-for-definition. Include every word in the lesson's word bank.
- `formPairs` — word → inflected forms that should be tappable
- `answerOptions[]` — the drop-down menu as `[form, pos, family]` rows: every sense form of every lesson word, **plus** each inflected form an answer needs (`exhausted`, `originated`, `punctuated`, …). Same menu for every question.
- `questions[]` — `[before, phrase, after, answer]` with an optional 5th element for a custom hint. `answer` is lower-case and must appear in `answerOptions`.

Behaviour: the bold phrase is colour-coded by its answer's part of speech; choosing a word swaps it into the sentence, shows the original phrase below, and reads the sentence aloud; 💡 filters the menu to the answer's part of speech; 3 checks, progress pips, adult-unlockable extra check, autosave, double-tap Clear, Export / Print (shared behaviour below).

Output path: `activities/just-the-right-word/{child}/YYYY-MM-DD-wordly-wise-lesson-{N}b-just-the-right-word.html`.

Reference instance: none yet; the template ships with Lesson 7B content (from `worksheets/christina/archive/2026-11-02-wordly-wise-lesson-7b-just-the-right-word.html`).

### Activity 9: Applying Meanings

**Template:** `activities/applying-meanings/template.html` (see its `README.md`)

Shape: the "C" section of a Wordly Wise lesson (Worksheet Type 4). Each question has four lettered choices and **one to four** may be correct; the student taps the letter of every correct answer.

Config:
- `meta` — `lessonLabel`, `title`, `instructions`, `wordListLabel`, `storageKey`, `backHref`, `backLabel`, `bookLabel`, `printTitle`, `studentName`
- `words[]` — `word` + `senses[]` (`form`, `pos` of `n`/`v`/`adj`/`adv`, `num`, `definition`, `example`); powers the word bank and tap-for-definition. Include every word in the lesson's word bank.
- `formPairs` — word → inflected forms that should be tappable; the lesson word in each question must be listed
- `questions[]` — `[question, [4 choices in printed order], "correct letters", hint]`, e.g. `"bcd"` (order irrelevant). The correct letters come from the edition-matched publisher key, never inferred.

Behaviour: letters toggle independently of the 🔊 buttons; a question is answered once any letter is selected and correct only on an exact set match; lesson words in questions and choices are tappable for definitions; 3 checks, progress pips, adult-unlockable extra check, autosave, double-tap Clear (shared behaviour below). Export / Print follows `Print / Export — Applying Meanings In-Place Selection` in `framework/INTERACTION_PATTERNS.md` (bold lesson word, two-column choices, chosen answers bold + underlined, no key).

Output path: `activities/applying-meanings/{child}/YYYY-MM-DD-wordly-wise-lesson-{N}c-applying-meanings.html`.

Reference instance: none yet; the template ships with Lesson 7C content (from `worksheets/christina/archive/2026-11-02-wordly-wise-lesson-7c-applying-meanings.html`).

### Shared built-in behaviour (Activities 3, 4, 7, 8 and 9)

- Whole-worksheet review with 3 checks; a warning (no check spent) for unanswered items
- Progress pips: gray unanswered, blue answered/edited, green correct, red needs another look
- Adult code-gated "add one more check" (see `INTERACTION_PATTERNS.md`)
- Tap any prompt/choice to hear it; autosave to localStorage; double-tap Clear; Export / Print
