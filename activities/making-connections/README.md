# Making Connections activity

Reusable template for Wordly Wise-style "Making Connections" practice: each prompt asks which word or words go with a phrase, and one or more choices can be correct. Built from the 8B worksheet, so it keeps the same accessibility behaviour.

## Configure a new activity

Copy `template.html` (never a previous instance) to `worksheets/{child}/YYYY-MM-DD-{slug}.html` and edit **only** the JSON in the `activityConfig` block near the top:

- `meta.lessonLabel`, `meta.title`, `meta.instructions` — header text
- `meta.storageKey` — **must be unique per activity instance** (progress is saved under this key)
- `meta.backHref`, `meta.backLabel` — link back to the lesson index
- `meta.bookLabel`, `meta.printTitle`, `meta.studentName` — header and Export / Print heading
- `words` — one object per word: `senses` with `form`, `pos` (`n`/`v`/`adj`/`adv`), `num`, `definition`, `example`. Powers tap-for-definition.
- `formPairs` — optional; word → inflected forms to make tappable (e.g. `"bungle": ["bungle","bungled"]`). Defaults to the word itself.
- `questions` — array of `[prompt, [4 choices], "answer letters", hint]`. Wrap the key phrase in `<em>…</em>`; it is shown but never read aloud. Answer letters are `a`–`d`, e.g. `"bc"` for two correct choices.

## Built-in behaviour

- Whole-worksheet review: 3 checks, with a warning (no check spent) for unanswered items
- Pips: gray unanswered, blue answered/edited, green correct, red needs another look
- Adult code-gated "add one more check" (code in the framework's INTERACTION_PATTERNS.md)
- Tap any sentence or choice to hear it, with HTML tags stripped from speech
- Autosave to localStorage, double-tap Clear, Export / Print

The template ships with the Lesson 8B content as a worked example; replace `words` and `questions` for a new activity.
