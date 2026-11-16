# Using Words in Context activity

This folder contains a reusable activity template for Wordly Wise-style vocabulary-in-context judgments.

## Configure a new activity

Open `template.html` and edit only the JSON in the `activityConfig` block near the top:

- `meta.title`, `meta.subtitle`, and `meta.instructions`
- `meta.storageKey` — give each activity instance a unique key
- `words` — add one object per vocabulary word
- `definition` — the definition spoken when the vocabulary button is tapped
- `sentences` — add as many sentence objects as needed
- `correctUse` — `true` when the word is used correctly, `false` when it is not
- `hint` — a short concept-based explanation shown after checking

The activity automatically lays out every sentence, updates progress, provides tap-to-speak, checks answers, and stores progress locally in the browser.

## Checking, pips, and adult unlock

- One progress pip per vocabulary word: gray = not started or incomplete, blue = answered but unchecked (or changed since the last check), green = all sentences checked and correct, red = checked with at least one incorrect. Each pip has a text label for screen readers and hover.
- `meta.maxChecks` (default 3) checks are allowed. After that, answers stay editable but checking is disabled until an adult uses the **🔒 Adult: add one check** button and enters the code. Each correct code grants exactly one more check; the used-check count is never reset.
- Checking with unanswered sentences shows a **Keep working / Check anyway** warning; the warning alone never spends a check.
- **Clear answers** uses double-tap confirmation and also clears any adult-granted checks.

## Christina accessibility choices

- Tappable vocabulary word reads the word and definition.
- Tapping a sentence reads the full sentence.
- Selecting C or I automatically reads the sentence back.
- Large C/I controls, visible progress pips, and concise concept hints.
- Speech defaults: rate 0.88, pitch 1.05.

## Lesson 6A content

The original Lesson 6A sentence/answer data was not available in the active Drive connection during this build, so this package intentionally does not recreate or guess that copyrighted exercise content. Add the original lesson data to the configuration block when the source worksheet is available.
