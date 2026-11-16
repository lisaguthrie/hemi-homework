# Determining Meanings activity

Reusable template for Wordly Wise-style "Determining Meanings" practice: each item gives a sentence stem and four endings, and one or more endings can correctly complete it. Built from the 6C worksheet, with the newer grading behaviour from the 8B Making Connections template.

## Configure a new activity

Copy `template.html` (never a previous instance) to `worksheets/{child}/YYYY-MM-DD-{slug}.html` and edit **only** the JSON in the `activityConfig` block near the top:

- `meta.lessonLabel`, `meta.title`, `meta.instructions` — header text
- `meta.storageKey` — **must be unique per activity instance** (progress is saved under this key)
- `meta.backHref`, `meta.backLabel` — link back to the lesson index
- `meta.bookLabel`, `meta.printTitle`, `meta.studentName` — header and Export / Print heading
- `words` — one object per word: `senses` with `form`, `pos` (`n`/`v`/`adj`/`adv`), `num`, `definition`, `example`. Powers tap-for-definition.
- `formPairs` — word → inflected forms that should be tappable in sentences.
- `questions` — array of `[stem, [4 endings], "answer letters", hint]`. The stem is read together with each ending when that choice is selected or tapped. Answer letters are `a`–`d`, e.g. `"ad"` for two correct endings.

## Built-in behaviour

- Whole-worksheet review: 3 checks, with a warning (no check spent) for unanswered items
- Pips: gray unanswered, blue answered/edited, green correct, red needs another look
- Adult code-gated "add one more check" (code in the framework's INTERACTION_PATTERNS.md)
- Tap any stem/ending to hear the completed sentence
- Autosave to localStorage, double-tap Clear, Export / Print
- No "Answers are checked together" footer note

The template ships with the Lesson 6C content as a worked example; replace `words`, `formPairs`, and `questions` for a new activity.
