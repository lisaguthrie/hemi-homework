# Completing Sentences activity

Reusable template for Wordly Wise-style "Completing Sentences" practice: each item is a sentence stem containing a vocabulary word, and the student finishes the sentence in their own words. Built from the Lesson 6D worksheet, with an upgraded speech-to-text mic.

## Configure a new activity

Copy `template.html` (never a previous instance) to `activities/completing-sentences/{child}/YYYY-MM-DD-wordly-wise-lesson-{N}{letter}-completing-sentences.html` and edit **only** the JSON in the `activityConfig` block near the top:

- `meta.lessonLabel`, `meta.title`, `meta.instructions` — header text
- `meta.wordListLabel` — label on the word bank (e.g. `Word List 8`)
- `meta.storageKey` — **must be unique per instance** (progress is saved under it). Pattern: `ww{book}_lesson_{N}{letter}_completing_sentences_{child}_{YYYY_MM_DD}_v1`
- `meta.backHref`, `meta.backLabel` — link back to the lesson index
- `meta.bookLabel`, `meta.printTitle`, `meta.studentName` — header and Export / Print heading
- `words` — one object per word in the lesson's word bank: `senses` with `form`, `pos` (`n`/`v`/`adj`/`adv`), `num`, `definition`, `example`. Powers tap-for-definition.
- `formPairs` — word → inflected forms that should be tappable in the stems.
- `questions` — array of sentence-stem strings, exactly as printed (e.g. `"A food that has fiber is"`).

The template ships with the Lesson 6D content as a worked example; replace `meta`, `words`, `formPairs`, and `questions`.

## Built-in behaviour

- Tap a vocabulary word (stem or word bank) for definition and example; tap a stem or ▶ to hear it
- **Speech to text:** 🎤 Dictate per question. Continuous listening that auto-restarts if the browser ends the session, ignores silence, appends finished phrases to the answer, stops TTS first, stops when the tab is hidden or reading aloud starts, and gives a spoken/visible message if the microphone is blocked. The button is disabled where the browser has no speech recognition (typing always works).
- ▶ Read my answer reads the stem plus the student's ending
- No scoring: answers are original writing for an adult to review
- Progress pips, autosave to localStorage, double-tap Clear, Export / Print
