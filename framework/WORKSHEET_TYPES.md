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

Keep the full lesson word bank visible above the exercises.

- Each base word is a large tappable button.
- Tapping a bank word opens a definition modal; it does **not** answer a question.
- Definitions must be transcribed from the provided source. Do not simplify, rewrite, or substitute general-knowledge definitions.
- Preserve multiple senses and related forms (for example `integrate` / `integration`) as separate definition paragraphs when the source presents them separately.
- Give each definition paragraph its own ▶ button that reads the **entire paragraph**, including the headword/part of speech, definition, and example sentence.
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

## Type 2: Vocabulary Sentence Completion — Multi-Select

*Wordly Wise “Determining Meanings” style: a vocabulary word appears in the sentence stem, and the student selects every answer choice that can correctly complete the sentence. More than one choice may be valid.*

**Use case:** Vocabulary exercises where the academic task is applying one lesson word across several possible sentence completions, including multiple meanings of the same word.

**Question data shape:**
```javascript
{
  before: "The nation ",
  target: "extends",
  after: "",
  definitionKey: "extend",
  options: [
    "from one ocean to another ocean.",
    "greetings to the people of Japan.",
    "to be the site of the next summer Olympic Games.",
    "millions of people from all over the world."
  ]
}
```

### Answer control

Use one independent checkbox per answer choice.

- Multiple choices may be selected for the same question.
- Keep the checkbox and answer text as **separate tap targets**.
- Tapping the checkbox toggles only that selection.
- Tapping the answer text reads the entire answer choice aloud and must not toggle the checkbox.
- Do not wrap the answer text in a `<label>` associated with the checkbox; that would make reading the answer accidentally change the response.
- Give the checkbox itself a minimum 44px surrounding tap area even if the native control is visually smaller.
- Persist every checkbox state to `localStorage`.

### Read-aloud behavior

This type uses distinct TTS scopes:

1. **Stem word level:** Ordinary words in the sentence stem are independently tappable and speak only that word while remaining visually normal continuous prose.
2. **Vocabulary target:** The lesson vocabulary word does **not** speak on direct tap. Tapping it opens the source-definition modal.
3. **Answer choice level:** Tapping an answer choice's text reads the entire choice aloud. It does not change selection.
4. **Instructions:** Keep the directions as one tappable block that reads the full directions aloud.

Do not auto-read after a checkbox toggle. Selection and listening are intentionally separate actions for this type.

### Definitions

Use the shared Vocabulary Word Bank + Definition Modal pattern, but open it directly from the vocabulary word in the stem rather than requiring a separate visible word bank.

- Definitions must use the provided curriculum wording; do not simplify or replace them with general-knowledge definitions.
- Preserve every source sense needed to reason about the question. For a word such as `extend`, include all relevant numbered meanings because multiple answer choices may rely on different senses.
- When the worksheet uses an inflected form such as `integrated`, `vacated`, or `boycotted`, the modal may display the source headword entry while keeping the inflected form as the visible stem word.
- Definition paragraphs may include their own read-aloud buttons using the standard definition-modal behavior.

### Feedback + progress

Default to **selection-only** behavior unless the user explicitly requests answer checking.

- Do not reveal correctness merely because a choice was selected.
- If the assignment will be reviewed by an adult, omit answer keys, `Check Answers`, correctness styling, and hints entirely.
- A progress pip may count a question as started/answered when it has at least one selected choice; it is not a score.
- A two-tap reset control may clear saved selections.

---
