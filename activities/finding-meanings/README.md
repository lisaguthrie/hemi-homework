# Finding Meanings activity

Reusable template for Wordly Wise "Finding Meanings" (section A) practice. Each item shows four phrases; the student picks **two** that join into a sentence correctly using a lesson word (one phrase starts the sentence, the other ends it). Built from the Lesson 7A worksheet (`docs/worksheets/archive/2026-11-02-wordly-wise-lesson-7a-finding-meanings.html`).

## Configure a new activity

Copy `template.html` (never a previous instance) to `activities/finding-meanings/{child}/YYYY-MM-DD-wordly-wise-lesson-{N}a-finding-meanings.html` and edit **only** the JSON in the `<script type="application/json" id="activityConfig">` block:

- `meta.lessonLabel`, `meta.title`, `meta.instructions` — header text
- `meta.storageKey` — **must be unique per activity instance** (progress is saved under this key). Pattern: `ww{book}_lesson_{N}a_finding_meanings_{child}_{YYYY_MM_DD}_v1`
- `meta.backHref`, `meta.backLabel` — link back to the lesson index
- `meta.bookLabel`, `meta.wordListLabel`, `meta.printTitle`, `meta.studentName` — header, word-bank title, Export / Print heading
- `words` — one object per word in the lesson's word list: `word` + `senses` (`form`, `pos` of `n`/`v`/`adj`, `num`, `definition`, `example`). Powers the word bank and tap-for-definition.
- `formPairs` — word → every inflected form that should be tappable (e.g. `punctuate` → `punctuated`, `punctuation`)
- `questions` — array of `[[4 phrases], "two answer letters", hint]`. Phrases are in printed order. The answer string names the two phrases that form the correct sentence, e.g. `"ba"`; order does not matter. The sentence is assembled with the phrase beginning with a capital letter or "To" first.

## Built-in behaviour

- Pick exactly two phrases (a third is disabled until one is deselected); the assembled sentence previews and is read aloud
- Tap any phrase or ▶ to hear it; tap a word-bank word for its definition and example
- Whole-worksheet review: 3 checks, warning (no check spent) for unanswered items
- Pips: gray unanswered, blue answered/edited, green correct, red needs another look
- Adult code-gated "unlock another check" (code in `framework/INTERACTION_PATTERNS.md`)
- Autosave to localStorage, double-tap Clear, Export / Print (student responses only, no key)

The template ships with the Lesson 7A content as a worked example; replace `words`, `formPairs`, and `questions` for a new activity.
