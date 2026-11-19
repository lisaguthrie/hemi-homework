# Just the Right Word activity

Reusable template for Wordly Wise "Just the Right Word" (section B) practice. Each sentence has a bold phrase; the student replaces it with a single lesson word (or a form of one) chosen from a drop-down. Built from the Lesson 7B worksheet (`docs/worksheets/archive/2026-11-02-wordly-wise-lesson-7b-just-the-right-word.html`).

## Configure a new activity

Copy `template.html` (never a previous instance) to `activities/just-the-right-word/{child}/YYYY-MM-DD-wordly-wise-lesson-{N}b-just-the-right-word.html` and edit **only** the JSON in the `<script type="application/json" id="activityConfig">` block:

- `meta.lessonLabel`, `meta.title`, `meta.instructions` — header text
- `meta.storageKey` — **must be unique per activity instance** (progress is saved under this key). Pattern: `ww{book}_lesson_{N}b_just_the_right_word_{child}_{YYYY_MM_DD}_v1`
- `meta.backHref`, `meta.backLabel` — link back to the lesson index
- `meta.bookLabel`, `meta.wordListLabel`, `meta.printTitle`, `meta.studentName` — header, word-bank title, Export / Print heading
- `words` — one object per word in the lesson's word list: `word` + `senses` (`form`, `pos` of `n`/`v`/`adj`/`adv`, `num`, `definition`, `example`). Powers the word bank and tap-for-definition.
- `formPairs` — word → every inflected form that should be tappable
- `answerOptions` — the drop-down menu, as `[form, pos, family]` rows (`family` = the word-bank headword). Include **every** form of **every** lesson word the student might reasonably pick: each sense's own form and part of speech (`exhaust` n, `punctuation` n, `monotony` n, …) **plus** every inflected form any answer needs (`exhausted`, `originated`, `punctuated`, …). This list is the answer menu for every question, so keep it identical for all questions. `pos` is shown beside each option and drives the 💡 hint.
- `questions` — array of `[before, phrase, after, answer]`:
  - `before` / `after` — the sentence text on either side of the bold phrase, exactly as printed (include the spaces; `before` may be `""` if the phrase opens the sentence)
  - `phrase` — the bold phrase to replace
  - `answer` — the correct form, lower-case, **exactly as it appears in `answerOptions`**; its `pos` there colours the bold phrase and filters the 💡 hint
  - optional 5th element — a custom hint; the default is a generic "compare the bold phrase with the definitions in {wordListLabel}"

If an `answer` is missing from `answerOptions`, the browser console logs a warning on load. Check the console after filling in a new instance.

## Built-in behaviour

- The bold phrase is colour-coded by the part of speech of its answer; each menu option shows its own part of speech
- Choosing a word swaps it into the sentence in place, shows the original phrase underneath, and reads the new sentence aloud. A word that opens the sentence is displayed capitalized.
- 💡 narrows the menu to words with the answer's part of speech and names it
- Tap the sentence or ▶ to hear it; tap a word-bank word for its definition and example
- Whole-worksheet review: 3 checks, warning (no check spent) for unanswered items
- Pips: gray unanswered, blue answered/edited, green correct, red needs another look
- Adult code-gated "unlock another check" (code in `framework/INTERACTION_PATTERNS.md`)
- Autosave to localStorage, double-tap Clear, Export / Print (student responses only, no key)

The template ships with the Lesson 7B content as a worked example; replace `meta`, `words`, `formPairs`, `answerOptions`, and `questions` for a new activity.
