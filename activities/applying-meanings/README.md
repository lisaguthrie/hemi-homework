# Applying Meanings activity

Reusable template for Wordly Wise "Applying Meanings" (section C) practice. Each question asks which of four choices fit a lesson word; **one to four** choices may be correct, so the student taps the letter of every correct answer. Built from the Lesson 7C worksheet (`docs/worksheets/archive/2026-11-02-wordly-wise-lesson-7c-applying-meanings.html`).

## Configure a new activity

Copy `template.html` (never a previous instance) to `activities/applying-meanings/{child}/YYYY-MM-DD-wordly-wise-lesson-{N}c-applying-meanings.html` and edit **only** the JSON in the `<script type="application/json" id="activityConfig">` block:

- `meta.lessonLabel`, `meta.title`, `meta.instructions` — header text (use the printed directions)
- `meta.storageKey` — **must be unique per activity instance** (progress is saved under this key). Pattern: `ww{book}_lesson_{N}c_applying_meanings_{child}_{YYYY_MM_DD}_v1`
- `meta.backHref`, `meta.backLabel` — link back to the lesson index
- `meta.bookLabel`, `meta.wordListLabel`, `meta.printTitle`, `meta.studentName` — header, word-bank title, Export / Print heading
- `words` — one object per word in the lesson's word list: `word` + `senses` (`form`, `pos` of `n`/`v`/`adj`/`adv`, `num`, `definition`, `example`). Powers the word bank and tap-for-definition.
- `formPairs` — word → every inflected form that should be tappable (e.g. `punctuate` → `punctuated`, `punctuation`). The lesson word in each question must appear here so it becomes a tap-for-definition button.
- `questions` — array of `[question, [4 choices], "correct letters", hint]`:
  - `question` — the printed question text, exactly as printed
  - choices — in printed order, so letters `a`–`d` match the book
  - correct letters — every correct letter, e.g. `"bcd"`; order does not matter. Take these from the publisher/teacher answer key for the matching edition (see *Publisher-Keyed Multi-Select Review* in `framework/INTERACTION_PATTERNS.md`); do not infer them.
  - hint — one short sentence shown after a check if the student's selection is not right. Point to the word's meaning; do not reveal how many answers are correct or which ones.

## Built-in behaviour

- Tap a lettered button to select or deselect it; any number from zero to four may be selected. A question counts as answered once at least one letter is selected.
- Tap the question, a choice, or a 🔊/▶ button to hear it; lesson words inside the question or a choice are tappable for their definition and example, as are the word-bank words
- Whole-worksheet review: 3 checks, warning (no check spent) for unanswered items. A question is correct only when the selected set exactly matches the key.
- Pips: gray unanswered, blue answered/edited, green correct, red needs another look
- Adult code-gated "unlock another check" (code in `framework/INTERACTION_PATTERNS.md`)
- Autosave to localStorage, double-tap Clear
- Export / Print mirrors the printed exercise: question with the lesson word in bold, choices in two columns (a/b left, c/d right), and the student's chosen answers in bold + underline. Student responses only; no key, grading, or hints.

The template ships with the Lesson 7C content as a worked example; replace `meta`, `words`, `formPairs`, and `questions` for a new activity.
