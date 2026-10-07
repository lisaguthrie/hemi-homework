# Active Worksheet Type Taxonomy

This file contains the worksheet types that should be considered for **new builds in the 2026–27 school year**.

The prior taxonomy is preserved in `framework/ARCHIVED_WORKSHEET_TYPES.md` for reference. Archived types are not eligible for automatic matching. They may be consulted for implementation ideas or legacy maintenance, but a new worksheet should be classified only against the active types in this file.

When a new worksheet type is successfully implemented and confirmed, add it here.

## Taxonomy Rule: Printed Parts Map to Separate Types

If a printed worksheet is divided into distinct labeled parts (for example, Part A / Part B / Part C), treat each part as its own worksheet type in this taxonomy.

- Keep type definitions part-specific (one interaction model per type).
- Do not bundle multiple printed parts into a single type entry.
- This taxonomy rule is independent of delivery format: a build may still combine multiple types into one app when the user explicitly asks for a single combined app.

---

## Type 1: Vocabulary Phrase Replacement — Word Bank

*Wordly Wise “Just the Right Word” style: each sentence contains a bold paraphrase. The student replaces that phrase with a vocabulary word, or an appropriate form of the word, from the lesson word list.*

**Use case:** Wordly Wise exercises where the academic task is choosing the vocabulary word whose meaning matches a bold phrase while preserving the grammar of the sentence.

**Sentence structure:**
```
[before text] [BOLD PARAPHRASE] [after text]
```

**Question data shape:**
```javascript
{
  before: "The separate companies were ",
  phrase: "brought together and formed",
  after: " into one large corporation.",
  answer: "integrated",
  hint: "Look for a form of the word meaning “to unite into a whole.”"
}
```

Keep the lesson word bank and the answer picker as separate data:

```javascript
const wordEntries = [
  {
    word: "integrate",
    paragraphs: [
      {
        label: "integrate · verb",
        text: "To unite into a whole; ... [source example sentence]"
      },
      {
        label: "integration · noun",
        text: "The act of uniting or bringing together; ... [source example sentence]"
      }
    ]
  }
];

const answerChoices = [
  // One candidate from every lesson word family.
  // Use the section-appropriate derived/inflected form when needed.
  "arrogant", "boycott", "campaign", "ceremony", "custody",
  "degrade", "detained", "extend", "integrated", "segregation",
  "supreme", "triumph", "vacated", "verdict", "violated"
];
```

### Answer control

The bold phrase is a composite inline answer area, not a text field.

- Render ordinary sentence text as normal inline prose, not visible word/button chips. Individual words remain tappable for word-level TTS using invisible/unstyled tap targets.
- Render the bold replacement phrase with a subtle orange highlight.
- Put only a small dropdown arrow (`▾`) at the right edge of the highlighted phrase; do not show "Pick a word" text in the sentence itself. The arrow opens a large touch-friendly choice panel.
- The choice panel shows **one candidate from every word family in the lesson bank**. Do not narrow the list per question.
- If the correct response requires a form of a word (for example `integrated`, `detained`, `segregation`, `vacated`, or `violated`), include that form directly in the choice panel so the student does not need to type it.
- After selection, replace the bold phrase with the chosen word/form and keep the original phrase available in a small “Original bold phrase” reminder below the sentence.

### Read-aloud behavior

This type uses three levels of TTS:

1. **Word level:** Every ordinary word in the exercise sentence is independently tappable and reads only that word, but the text should still look like normal continuous prose. Words inside the original bold phrase or selected replacement are independently tappable too.
2. **Sentence level:** Every card has a green ▶ button that reads the full current sentence. Before an answer is chosen, it reads the original sentence; after selection, it reads the revised sentence.
3. **Selection read-back:** After a choice is selected, wait about 300 ms and read the full revised sentence aloud so the student can self-correct by listening.

### Word bank + definitions

Keep the full lesson word bank visible above the exercises. For long exercises where the student repeatedly refers back to the bank, use the **Sticky Vocabulary Word Bank** component in `framework/DESIGN_SYSTEM.md` and the usage rules in `framework/INTERACTION_PATTERNS.md`.

- Keep sticky-bank copy minimal; do not add text explaining the scrolling behavior.
- Each base word is a large tappable button.
- Tapping a bank word opens a definition modal; it does **not** answer a question.
- Definitions must be transcribed from the provided source. Do not simplify, rewrite, or substitute general-knowledge definitions.
- Preserve multiple senses and related forms (for example `integrate` / `integration`) as separate definition cards when the source presents them separately.
- Use the canonical **Vocabulary Definition Modal Card** style from `framework/DESIGN_SYSTEM.md`: compact green `▶` at the far left, headword/part of speech above the text, and clearly separated **Definition** and **Example** rows.
- Use the speech behavior in `framework/INTERACTION_PATTERNS.md` so headword and part of speech are spoken with clear sentence breaks (for example, "ceremony. noun.") rather than reading the visual separator literally.
- A word-level 🔊 control in the modal may read the headword alone.
- Exclude unrelated partner/activity prompts from the dictionary entry unless the user asks to include them.

Use the reusable definition-modal behavior in `framework/INTERACTION_PATTERNS.md`.

### Feedback

Use **deferred per-card feedback** rather than marking a choice immediately.

- Choosing a word updates the sentence, saves state, and reads the revised sentence.
- Correctness is revealed only when the student taps `Check answer`.
- Correct: show a calm green ✅ confirmation and mark the card complete.
- Incorrect: show a `💡 Hint:` using the relevant source definition or meaning. Never use “wrong” or an unsupported guess-and-check prompt.
- A new selection clears the prior check state.

### Progress + persistence

- Persist the selected word and checked/correct state in `localStorage`.
- Progress pips may distinguish unanswered, selected, and correct states.
- The progress label should report answered/total, not a running score.

**Reference implementation:** `worksheets/reference/2026-09-30-wordly-wise-lesson-2b.html`

---


## Type 2: Vocabulary Antonyms — Select Two of Four

*Wordly Wise “Word Study” antonym style: each row contains four words, and the student identifies the two whose meanings are opposite or nearly opposite.*

**Use case:** Vocabulary word-study exercises where each row contains four candidate words and the academic task is to select exactly one antonym pair.

**Question data shape:**
```javascript
{
  choices: ["release", "detain", "campaign", "decide"]
}
```

### Answer control

Use four large checkbox choices per row.

- Keep the checkbox and the visible word as **separate tap targets**. Tapping the word provides reading/definition support and must never toggle the answer.
- Permit at most two checked choices in a row.
- As soon as two choices are selected, disable the two unchecked boxes. Keep the selected boxes enabled so the student can uncheck one and revise the response.
- A row is considered response-complete when exactly two choices are checked.
- Do not infer correctness from completion styling; use neutral/blue completion treatment rather than the green correct-answer treatment.

### Read-aloud + vocabulary support

Use mixed support based on the lesson source.

- Make the instructions tappable and read them aloud using the profile speech settings.
- If a displayed word is part of the lesson word list, or a source-provided related form, tapping the word **opens the reusable definition modal and immediately reads just the tapped word aloud**. Do not auto-read the definition. This keeps the immediate auditory experience consistent with non-word-list choices while still exposing source definitions on screen.
- If a displayed word is not in the lesson word list, tapping it reads that word aloud and does **not** open a definition. Do not invent or substitute a general-knowledge definition for distractors.
- For a displayed related form (for example `degrading`), the modal may show only the matching related-form paragraph when that is the clearest support.
- The definition modal and checkbox selection are independent; opening a definition never changes the student's selected answers.

### Feedback

This type supports **adult-check-only** completion when requested.

- Do not include a `Check Answers` button, automatic correctness feedback, hints, or a score.
- The app does not need an answer key in its interaction logic when correctness is intentionally deferred to an adult.
- Progress reflects response completion only (two choices selected), not correctness.

### Progress + persistence

- Persist each row's selected words in `localStorage`.
- Progress pips and labels count rows with exactly two selections.
- Preserve responses across reloads and provide the standard double-tap `Clear all responses` action.

**Reference implementation:** `worksheets/christina/2026-09-30-wordly-wise-lesson-2d.html`

---

## Type 3: Vocabulary Sentence Pairing — Choose Two Phrases

*Wordly Wise “Finding Meanings” style: each item contains four sentence fragments, and the student chooses the two fragments that form one sentence correctly using a lesson vocabulary word.*

**Use case:** Vocabulary exercises where two of four printed phrases must be paired to demonstrate the meaning of a word.

**Question data shape:**
```javascript
{
  phrases: [
    ["a", "Squalid areas are those"],
    ["b", "with little rainfall."],
    ["c", "Rural areas are those"],
    ["d", "away from large cities."]
  ],
  answer: ["c", "d"],
  hint: "Rural means “of or relating to the country and the people who live there.”"
}
```

### Answer control

Use one selection control plus one phrase-reading control per printed phrase.

- Permit exactly two selected phrases.
- Once two are selected, disable unselected choices until the student deselects one.
- Keep selection and TTS as separate tap targets so listening never changes the answer.
- After two phrases are selected, assemble them into a readable sentence in grammatical order and show that sentence below the choices.
- Auto-read the assembled sentence about 300 ms after the second selection.

### Feedback

Use deferred per-card checking.

- `Check answer` is disabled until two phrases are selected.
- Correct: calm green ✅ feedback.
- Incorrect: a `💡 Hint:` based on the source definition of the vocabulary word used in the correct sentence.
- A changed selection clears prior correctness feedback.

### Progress + persistence

- Persist the two selected phrase IDs and check state for each item.
- Count an item as answered when exactly two phrases are selected.
- Progress pips may distinguish selected from checked/correct.

**Reference implementation:** `docs/worksheets/2026-10-05-wordly-wise-lesson-3a-finding-meanings.html`

---

## Type 4: Vocabulary Applying Meanings — Multi-Select, Adult Review

*Wordly Wise “Applying Meanings” style: each question has four choices and may have from one to four correct answers.*

**Use case:** Vocabulary application questions where the printed source explicitly allows multiple correct choices but does not provide an answer key in the supplied material.

**Question data shape:**
```javascript
{
  question: "Which of the following animals graze?",
  vocab: "graze",
  choices: [
    ["a", "crocodiles"],
    ["b", "sheep"],
    ["c", "horses"],
    ["d", "cats"]
  ]
}
```

### Answer control

Use four independent checkbox-style selections.

- Do not cap the number of selected choices.
- Keep the selection control and the visible answer text as separate tap targets: the selection control changes the answer; the text control reads the option aloud.
- Make the full question tappable/readable.
- Provide the lesson vocabulary definition through the standard definition modal without changing the answer.

### Feedback

When the supplied source does not contain an answer key, use **adult-check-only** completion.

- Do not infer or manufacture correctness from general knowledge.
- Do not include automatic hints, scoring, or correct/incorrect labels.
- A question is response-complete after at least one option is selected.
- A short neutral note may state that selections are saved for review.

If a trustworthy answer key is supplied with a future worksheet, correctness logic may be added without changing the selection interaction.

### Progress + persistence

- Persist selected option IDs per question.
- Progress counts questions with at least one selection.
- Preserve all selections across reloads and provide the standard double-tap clear action.

**Reference implementation:** `docs/worksheets/2026-10-05-wordly-wise-lesson-3c-applying-meanings.html`

---

## Type 5: Vocabulary Analogy — Choose Related Pair

*Word Study analogy style: a stem pair is shown in capitals, followed by four candidate word pairs; the student chooses the pair with the same semantic relationship.*

**Use case:** Vocabulary analogies where the source teaches a specific relationship, such as antonyms, and asks the student to choose one matching pair.

**Question data shape:**
```javascript
{
  pair: ["HUMID", "ARID"],
  choices: [
    ["a", "square", "round"],
    ["b", "sloppy", "careless"],
    ["c", "thirsty", "hungry"],
    ["d", "wet", "dry"]
  ],
  answer: "d"
}
```

### Answer control

Use four large single-select pair buttons.

- Display the source pair prominently above the choices.
- Selecting a choice replaces any prior selection.
- After selection, auto-read the complete analogy sentence (for example, “Humid is to arid as wet is to dry.”).
- Keep the lesson word bank available through the standard definition modal for lesson words; do not invent definitions for non-lesson distractors.
- Preserve any source-provided analogy explanation/example in a collapsible support section when it would otherwise add substantial visual load.

### Feedback

Use deferred per-card checking.

- Correct: calm green ✅ confirmation.
- Incorrect: a relationship hint that names the source-taught relationship without revealing the correct choice (for example, “HUMID and ARID are opposites. Look for another pair of opposites.”).
- Do not add broader analogy rules not present in the source.

### Progress + persistence

- Persist selected choice and check/correct state.
- Count any selected pair as answered; distinguish checked/correct with the standard progress styling.
- Provide the standard double-tap clear action.

**Reference implementation:** `docs/worksheets/2026-10-05-wordly-wise-lesson-3d-word-study.html`

---
