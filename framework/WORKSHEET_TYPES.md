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

## Default Review Policy — Three Whole-Worksheet Checks

For objectively verifiable questions, the default checking model is **three initial chances to check every response in one action at the bottom of the page**. No per-card Check buttons, automatic correctness on selection, unlimited student-initiated attempts, or adult-check-only mode unless the user explicitly requests an exception. An incomplete submission first raises a warning; proceeding after confirmation consumes a chance and distinguishes blanks from attempted-but-incorrect answers. Checked question progress pips are green for correct and red for incorrect, while unchecked/revised answers stay neutral and unanswered questions stay gray. After all checks are spent, an adult can enter the configured code to unlock **one** further check without discarding responses or history; repeat authorization is required after that check. Use the source-verified key, exact-set matching for multiple-choice, persistent attempt counts/grants, and neutral feedback on changed answers. See `framework/BUILD_CONSTRAINTS.md` and `framework/INTERACTION_PATTERNS.md` for complete behavior.

For inherently open-ended work, such as original sentence continuations or comprehension writing, a meaningful answer cannot be validated by an exact-string key. Retain adult review as an **explicit documented exception** and preserve the writing task. Do not invent model answers to simulate a machine-gradable worksheet.

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
  requiredPos: "verb"
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
  // One candidate from every lesson word family. Tag the displayed form with its POS.
  { value: "arrogant",    label: "arrogant",    pos: "adjective" },
  { value: "boycott",     label: "boycott",     pos: "verb" },
  { value: "campaign",    label: "campaign",    pos: "noun" },
  { value: "ceremony",    label: "ceremony",    pos: "noun" },
  { value: "custody",     label: "custody",     pos: "noun" },
  { value: "degrade",     label: "degrade",     pos: "verb" },
  { value: "detained",    label: "detained",    pos: "verb" },
  { value: "extend",      label: "extend",      pos: "verb" },
  { value: "integrated",  label: "integrated",  pos: "verb" },
  { value: "segregation", label: "segregation", pos: "noun" },
  { value: "supreme",     label: "supreme",     pos: "adjective" },
  { value: "triumph",     label: "triumph",     pos: "noun" },
  { value: "vacated",     label: "vacated",     pos: "verb" },
  { value: "verdict",     label: "verdict",     pos: "noun" },
  { value: "violated",    label: "violated",    pos: "verb" }
];
```

### Answer control

The bold phrase is a composite inline answer area, not a text field.

- Render ordinary sentence text as normal inline prose, not visible word/button chips. Individual words remain tappable for word-level TTS using invisible/unstyled tap targets.
- Render the bold replacement phrase with a subtle orange highlight.
- Put only a small dropdown arrow (`▾`) at the right edge of the highlighted phrase; do not show "Pick a word" text in the sentence itself. The arrow opens a large touch-friendly choice panel.
- Before any scaffold is requested, the choice panel shows **one candidate from every word family in the lesson bank**. Do not narrow the list per question by default.
- Tag every displayed candidate form with its source-supported part of speech so the optional POS scaffold can filter accurately.
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
- Each base word is a large tappable button. Show abbreviated, color-coded POS tag(s) after the headword (`n`, `v`, `adj`, `adv`) using the canonical POS palette from `framework/DESIGN_SYSTEM.md`.
- If the word-family entry contains related forms with different parts of speech, show each unique POS tag in the bank; the definition popup resolves the exact POS for each related form.
- Tapping a bank word opens a definition modal; it does **not** answer a question.
- Definitions must be transcribed from the provided source. Do not simplify, rewrite, or substitute general-knowledge definitions.
- Preserve multiple senses and related forms (for example `integrate` / `integration`) as separate definition cards when the source presents them separately.
- Use the canonical **Vocabulary Definition Modal Card** style from `framework/DESIGN_SYSTEM.md`: compact green `▶` at the far left, headword/part of speech above the text, and clearly separated **Definition** and **Example** rows.
- Use the speech behavior in `framework/INTERACTION_PATTERNS.md` so headword and part of speech are spoken with clear sentence breaks (for example, "ceremony. noun.") rather than reading the visual separator literally.
- A word-level 🔊 control in the modal may read the headword alone.
- Exclude unrelated partner/activity prompts from the dictionary entry unless the user asks to include them.

Use the reusable definition-modal behavior in `framework/INTERACTION_PATTERNS.md`.

### Optional part-of-speech scaffold

Include an icon-only `💡` button directly under the sentence play button. This is a one-way support scaffold, not correctness feedback.

- Before the student taps it, leave the phrase highlight and full vocabulary picker unchanged.
- When tapped, color the phrase/replacement area using the required POS color and filter that card's word picker to candidate forms with that same part of speech.
- Determine the required POS from the source-supported correct replacement form; do not guess from surface wording alone.
- The scaffold must not select an answer, mark anything correct, or expose a score.
- Persist the scaffold state per card so it stays active after answer changes and reloads.
- Visible button content is only `💡`; provide an accessible label such as `Show part-of-speech hint`.

Use the **Part-of-Speech Filter Scaffold** in `framework/INTERACTION_PATTERNS.md`.

### Feedback

Apply the default **three whole-worksheet checks** against the source-verified replacement words, unless the user explicitly requests adult review.

- Choosing a word updates the sentence, saves state, and reads the revised sentence aloud after about 300 ms, **without revealing correctness**.
- The optional `💡` scaffold only reveals part of speech and filters candidates; it never evaluates the response.
- At the bottom, check every replacement together; an unselected sentence is **unanswered**, not an incorrect choice. Keep verified correct / needs-review / unanswered visually separate.

### Progress + persistence

- Persist the selected word and `hinted` scaffold state in `localStorage`.
- Progress pips report response completion only: unanswered vs. answered.
- The progress label reports `answered / total`, not correctness.
- Preserve responses across reloads and provide the standard double-tap `Clear all responses` action.

### Export / Print

For a **Just the Right Word** phrase-replacement exercise, preserve the original full sentence with its bold paraphrase, the separate `Replacement:` line, and the full sentence with the student's chosen word inserted. On that **completed-sentence line only**, format **the student's replacement word** as **bold + single underline**; leave the surrounding sentence text unmarked. Preserve punctuation and spacing from the original `before` and `after` text.

- Render the actual saved selection (even if incorrect), not the answer-key word. If no word was selected, display the existing plain blank (`_____`) rather than bolding or underlining a placeholder.
- Use a print-only class and escape each of the three text segments separately so only the inserted word is emphasized. Do not alter the original-sentence line, the `Replacement:` line, interactive controls, read-aloud, autosave, or three-check grading.
- Use `Print / Export — Phrase Replacement in the Completed Sentence` in `framework/INTERACTION_PATTERNS.md`.

**Reference implementations:** `docs/worksheets/2026-10-05-wordly-wise-lesson-3b-just-the-right-word.html` (prior pattern) and `docs/worksheets/2026-10-19-wordly-wise-lesson-5b-just-the-right-word.html` (bold-underlined replacement in completed sentence)

---


## Type 2: Vocabulary Word Relationships — Select Two of Four

*Wordly Wise “Word Study” synonym / antonym style: each row contains four words, and the student identifies the two whose meanings are alike or opposite.*

**Use case:** Vocabulary word-study exercises where four candidates contain exactly one related pair. Antonyms-only exercises ask for the pair; mixed synonyms-and-antonyms exercises also ask the student to identify the relationship.

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
- Permit no third selected word. Because every checkbox also speaks its word when tapped, keep other boxes tappable for **audio only** when two words are already selected (visually indicate the selection limit, but do not use a native `disabled` control that blocks speech). Keep selected boxes available for deselection and revision.
- For antonyms-only exercises, a row is response-complete when exactly two choices are checked.
- For mixed synonyms-and-antonyms exercises, add large `S · Synonyms` and `A · Antonyms` selectors below the words. Completion requires exactly two choices **and** one relationship choice; either selection remains independently editable.
- Do not infer correctness from completion styling; use neutral/blue completion treatment rather than the green correct-answer treatment.

### Read-aloud + vocabulary support

Use mixed support based on the lesson source.

- Make the instructions tappable and read them aloud using the profile speech settings.
- **Checkbox target:** Tapping its box selects/deselects the word (up to two per row) **and speaks just that one word**, whether the tap selected or deselected it. If two are already selected, tapping an unselected checkbox speaks the word but does not add a third answer.
- **Word-text target:** Tapping the displayed word opens the **same Vocabulary Definition Modal Card** for *every* word, without changing selection or automatically speaking. The modal's own green `▶` reads the definition and example when requested.
- **This week's lesson word or exact listed related form:** Show the usual **yellow word-bank style** on the word target; use the exact definition and example from the packet, preserving senses, source wording and part-of-speech tags. Do not replace these with an outside dictionary.
- **Other printed word (including a term from another lesson):** Keep the word text visually plain; research an authoritative outside dictionary for a context-appropriate definition and example. Embed the content in the self-contained HTML for offline use, and identify/link the outside source in the popup. Do not fabricate a source or quietly pass off external definitions as packet text.
- Keep separate large keyboard-accessible targets with clear labels and visible focus. The word's definition popup must never alter answers, checking chances, or progress. Use the **Word Study — Checkbox Speaks / Word Opens Definition** pattern in `framework/INTERACTION_PATTERNS.md` and the yellow styling in `framework/DESIGN_SYSTEM.md`.

### Feedback

Use the default **three whole-worksheet checks** when a reliable pair key is available. Validate the exact two-word pair; in the mixed variant, validate the chosen `S` / `A` relationship **as well**. Do not show correctness while the student is still selecting.

- A row with fewer than two selections, or without a required `S` / `A` selection, is **incomplete/unanswered** for the warning and review, distinct from a completed but incorrect pair.
- Selection alone never shows correctness; verified feedback appears only when the bottom Check all responses action is used.
- Adult-check-only remains an explicit user-requested exception.

### Progress + persistence

- Persist each row's selected words and, when present, its `S` / `A` classification in `localStorage`.
- Progress pips and labels count a row only when all controls required for that variant are answered.
- Preserve responses across reloads and provide the standard double-tap `Clear all responses` action.

### Export / Print

For the mixed synonyms-and-antonyms variant, mirror the printed four-word exercise instead of creating a separate answer summary:

- Keep the item number, **all four original words in source order**, and the `S` and `A` labels on **one horizontal line**. Space the four words evenly; leave a slightly larger gap before `S` and a small gap between `S` and `A`.
- Use **bold + underline** on precisely the two words the student actually selected and the `S` or `A` they selected. Leave unselected words/letters in regular type. If selections are incomplete, mark only what was selected.
- Do not repeat the chosen pair on a `Selected:` line, expand `S/A` into `Synonyms/Antonyms`, print check results, or substitute the correct answer key. Keep the source directions and question numbering.
- Prevent the words and S/A from wrapping in print. Apply this formatting **only to the export**, leaving the accessible interactive controls unchanged. Use `Print / Export — Four-Word Pair with S/A` in `framework/INTERACTION_PATTERNS.md`.

**Reference implementations:** `worksheets/christina/2026-09-30-wordly-wise-lesson-2d.html` (antonyms only) and `worksheets/christina/2026-10-19-wordly-wise-lesson-5d-word-study-synonyms-antonyms.html` (mixed pair + classification).

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

Use the default **three whole-worksheet checks**, not individual `Check answer` buttons.

- Validate every selected phrase pair on the same bottom-of-page check. Fewer than two chosen phrases is **unanswered/incomplete**.
- Correct: calm green ✅ feedback. Answered but incorrect: a 💡 relationship hint based on the source definition, without naming the answer.
- Changing a pair clears only that item's previous result until the next whole-page check.

### Progress + persistence

- Persist the two selected phrase IDs and check state for each item.
- Count an item as answered when exactly two phrases are selected.
- Progress pips may distinguish selected from checked/correct.

### Export / Print

- Keep the source fragments, question numbering, `Sentence:` label, and assembled response wording and placement unchanged.
- Format **only the student's assembled answer sentence** in **bold + single underline** in the print/export view. Keep the label and source fragments as previously styled; never apply the emphasis to the answer key or substitute a model/correct sentence for a student's incomplete or incorrect selection.
- Use a print-only class (for example `.print-a-answer{font-weight:800;text-decoration:underline;text-decoration-thickness:1.5px;text-underline-offset:3px}`) around the escaped output of `buildPairSentence(q, state.answers[i])`. Interactive controls, TTS, autosave, progress, and three-check feedback do not change.

**Reference implementation:** `docs/worksheets/2026-10-05-wordly-wise-lesson-3a-finding-meanings.html` and `docs/worksheets/2026-10-19-wordly-wise-lesson-5a-finding-meanings.html` (bold-underlined assembled sentence on export)

---

## Type 4: Vocabulary Applying Meanings — Multi-Select

*Wordly Wise “Applying Meanings” style: each question has four choices and may have from one to four correct answers.*

**Use case:** Vocabulary application questions where the printed source explicitly allows multiple correct choices.

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
  ],
  answer: ["b", "c"], // source-verified IDs; may contain 1–4 letters
  hint: "Graze means to feed on growing grass. Think about which animals do that."
}
```

### Answer control

Use four independent checkbox-style selections.

- Do not cap the number of selected choices.
- Keep the selection control and the visible answer text as separate tap targets: the selection control changes the answer; the text control reads the option aloud.
- Make the full question tappable/readable.
- Provide the lesson vocabulary definition through the standard definition modal without changing the answer.

### Feedback

Use the default **three whole-worksheet checks** against a verified publisher/teacher key, evaluating the **exact full selection set** for each question. The answer controls themselves remain multi-select and independent of listening.

- Before falling back to adult checking merely because the provided student worksheet omits answers, **look for an edition-matched teacher/publisher key**. Verify its exercise, page, question wording, and option order against the student's pages. When the matching key is available, implement automated three-chance checking rather than adult review.
- Store the correct option letters (one to four) as an `answer` array in each question's data. Ignore selection order but require the chosen set to match the source key exactly: missing or extra options both mean **needs another look**. Never treat a partially correct subset as correct.
- A question with no selections is **unanswered**. A nonempty selection that omits a correct choice or includes a distractor is **answered but needs review**; keep a concept-specific hint on each card and reveal it only after checking, without listing the correct options.
- Use the reusable **Publisher-Keyed Multi-Select Review** pattern in `framework/INTERACTION_PATTERNS.md`. All three attempts are shared across the worksheet, saved across reloads, and consumed only by a completed/confirmed whole-worksheet check.
- If no trustworthy, matching key can be established, do not invent one. Adult review remains an explicit fallback for genuinely uncheckable items or unavailable keys.

### Progress + persistence

- Persist selected option IDs, check count, review statuses, and revised markers in `localStorage`. Changing one selection clears that question's stale review feedback only.
- Progress counts questions with at least one selection, independently of correctness.
- Preserve all selections across reloads and provide the standard double-tap clear action.

### Export / Print

Mirror the original Applying Meanings printed exercise rather than adding a separate answer summary.

- Preserve each question and its four original lettered choices. Bold the target lesson vocabulary word **in the question prompt**, including its printed related form (for example `evolved` from `evolve` or `inscription` from `inscribe`); do not bold the entire prompt or silently rewrite vocabulary forms.
- Follow the printed choice arrangement when practical (the two-column `a`/`b` left and `c`/`d` right layout for Wordly Wise Book 6 Lesson 5C). Mark **only the student's selected answer options** in place with **bold + underline** on both the printed letter and choice text; other options remain plain.
- Print every selected option, including incomplete or incorrect selections, without exposing the answer key or three-check review status. Remove the redundant `Selected:` answer line; this pattern does not affect the interactive controls or saved attempts.
- Use `Print / Export — Applying Meanings In-Place Selection` in `framework/INTERACTION_PATTERNS.md`.

**Reference implementations:** `docs/worksheets/2026-10-19-wordly-wise-lesson-5c-applying-meanings.html` (edition-matched publisher key, three whole-worksheet checks) and `docs/worksheets/2026-10-05-wordly-wise-lesson-3c-applying-meanings.html` (earlier implementation).

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

Use the default **three whole-worksheet checks**, never unlimited per-card checking unless explicitly requested.

- Correct: calm green ✅ confirmation. Answered but incorrect: a 💡 relationship hint naming the source-taught relationship without revealing the correct choice (for example, “HUMID and ARID are opposites. Look for another pair of opposites.”).
- A row with no selected pair remains **unanswered**; do not add broader analogy rules absent from the source.

### Progress + persistence

- Persist selected choice and check/correct state.
- Count any selected pair as answered; distinguish checked/correct with the standard progress styling.
- Provide the standard double-tap clear action.

**Reference implementation:** `docs/worksheets/2026-10-05-wordly-wise-lesson-3d-word-study.html`

---

---

## Type 6: Vocabulary in Context — Passage + Sentence Responses

*Wordly Wise “Vocabulary in Context” style: the student reads a passage containing lesson vocabulary, then answers comprehension/context questions in complete sentences.*

**Use case:** Long reading passages followed by open-response questions where vocabulary meaning must be understood in context and the printed directions may require unused lesson words in answers.

### Layout

Use a two-pane reading/response workspace on wider screens and stack the panes on narrow screens.

- **Left pane:** passage, split into paragraph cards.
- **Right pane:** directions, a **collapsible lesson word bank (collapsed by default)**, question cards, and progress. Place the disclosure inside the response pane so the 15-word bank never crowds the questions until requested.
- Preserve the printed directions verbatim; use adult review for open-ended written responses.
- Each sentence is independently tappable for TTS.
- Each paragraph has a green `▶` button that reads the full paragraph.
- Map inline vocabulary taps to the exact source headword/form, including related forms; do not guess a match by stemming.
- Lesson vocabulary in the passage and questions opens the standard definition modal without changing an answer or interrupting answer editing.

### Answer control

Use one large free-text area per question with a `▶ Read my answer` control.

- Preserve the printed requirement to answer in a sentence.
- This open-ended comprehension task is an **explicit adult-review exception** to the default three automated checks; do not score it with exact-string matching.
- Typing must remain focus-safe; update progress in place rather than rebuilding the question card.
- Include speech recognition only when requested. If both microphone and no-microphone versions are requested, make both while keeping typing, autosave, read-back, and print fully usable in either version.

When the printed directions say that a question without a lesson word must use one in the answer, pair those questions with the **Unique Vocabulary-Family Allocation** interaction in `framework/INTERACTION_PATTERNS.md`. Include a final **“Choose a different word…”** option in those drop-downs: it is an independence reminder, not a special word or automatic answer. Leave the written response fully editable and have an adult review any independently chosen word.

### Vocabulary support

Use the standard Word List bank and definition modal.

- Preserve source definitions, related forms, sense numbers, Definition/Example separation, spoken punctuation, and POS tags.
- Related forms belong to one word family for “use each word only once” tracking. Prevent duplicate assignments among named dropdown options; the “Choose a different word…” option remains available for manual choices without pretending to track which family was used.
- A question that already contains a lesson word does not need an extra vocabulary selector.

### Progress + persistence

- Persist answer text and any assigned vocabulary family in `localStorage`.
- A normal vocabulary-in-question item is complete when its response is non-empty.
- An item requiring an added lesson word is complete only when response text and a vocabulary choice are present. The independent “Choose a different word…” choice counts as the chooser response, but does not imply that the written text was automatically checked for a particular vocabulary word.
- Progress represents response completion, never correctness.
- Provide the standard double-tap clear action and Export / Print.
- Give separately delivered variants distinct persistence keys.

**Reference implementations:** `docs/worksheets/2026-10-08-wordly-wise-lesson-3e-vocabulary-in-context.html` and `worksheets/christina/2026-10-19-wordly-wise-lesson-5e-vocabulary-in-context.html` (collapsible bank and independent word choice).

---

## Type 7: Vocabulary Making Connections — Multi-Select Word Associations

*Wordly Wise “Making Connections” style: each prompt asks which of four words relate in meaning to a named concept; more than one choice may fit.*

**Use case:** Word association exercises where recognizing semantic connections, including related lesson and non-lesson words, is the academic task.

### Answer control

- Show the original prompt and all four lettered choices, without removing distractors or limiting the number of selections.
- Use an independent checkbox-style selection control for each answer. Make the word itself a separate TTS/definition target; tapping a word must not change the selected response.
- Speak non-lesson answer words aloud without inventing definitions. For lesson words or source-specified related forms, open the standard definition modal and speak the tapped word.
- Make printed directions and question prompts independently readable.

### Feedback

- Use the default **three whole-worksheet checks** and the publisher/teacher answer key when available, as in Lesson 4B. Only the bottom check action evaluates all ten questions.
- Mark exactly matched answer sets **correct**; nonempty mismatched sets **needs review**; no selection **unanswered**. Keep multiple selections editable between checks and after the third.
- Never infer a definitive key from a vague semantic association if a more authoritative key can be found; use adult review only as an explicit fallback when validation cannot be supported.

### Progress + persistence

- Persist selected answer indices for every question, separately from other lesson parts.
- Show neutral response-completion progress, plus the standard double-tap clear and Export / Print actions.
- Include the lesson word bank and source-defined definition/example modal.

### Export / Print

- Reproduce the printed prompt and all four lettered options without interactive checkboxes or checkbox outlines.
- Show **only the student's selected answers** in place using **bold + underline on both the answer letter and choice text**. Unselected choices remain plain, including if the selected set is incomplete or not correct.
- Do not replace the original option list with a detached `Selected:` summary, the teacher key, or checking-status badges. The interactive screen retains independent checkbox-style selection and word-read/definition controls.
- Use **Print / Export — Selected Multiple-Choice Answers In Place (Types 7 and 8)** from `framework/INTERACTION_PATTERNS.md`.

**Reference implementation:** `docs/worksheets/2026-10-13-wordly-wise-lesson-4b-making-connections.html`

---

## Type 8: Vocabulary Determining Meanings — Multi-Select Sentence Completions

*Wordly Wise “Determining Meanings” style: a sentence stem includes a lesson vocabulary word, followed by four possible continuations; more than one can complete it meaningfully.*

**Use case:** Vocabulary questions where the student identifies all printed continuations that make meaningful sentences using the target lesson word.

### Answer control

- Display the exact sentence stem and all four lettered continuations.
- Provide separate checkbox-style controls for selecting responses and controls for reading each complete stem-plus-continuation aloud; listening must never toggle selection.
- Allow one or more options per question. Do not force a single choice or reveal the answer from the selection control.
- Make the stem and instructions tappable for TTS; offer the source vocabulary definition through the shared word bank/modal.

### Feedback

- Use the default **three whole-worksheet checks** against a verified teacher/publisher key, as in Lesson 4C. A check validates every completed sentence set together, not one sentence at a time.
- Show **correct**, **answered but needs review**, and **unanswered** distinctly; never give feedback just by tapping answer choices. Use adult review only as an explicit exception if no reliable answer key exists.

### Progress + persistence

- Count a question as response-complete when at least one continuation is selected.
- Persist the selected option indices and provide progress pips, double-tap clear, and Export / Print.

### Export / Print

- Preserve the exact printed stem and four lettered completions for every question, including all unselected options.
- Do **not** print checkboxes. Print selected letter-plus-continuation text in **bold + underline**, with unselected choices in plain type; never derive which options are emphasized from the answer key or grading outcome.
- Keep a student's partial or incorrect selected set visible as selected, and omit review badges, answer-key indicators, and redundant selection-summary lines.
- Use **Print / Export — Selected Multiple-Choice Answers In Place (Types 7 and 8)** from `framework/INTERACTION_PATTERNS.md`.

**Reference implementation:** `docs/worksheets/2026-10-13-wordly-wise-lesson-4c-determining-meanings.html`

---

## Type 9: Vocabulary Completing Sentences — Open-Ended Continuations

*Wordly Wise “Completing Sentences” style: each printed sentence starts with a lesson word or related form, and the student supplies a meaningful continuation demonstrating understanding.*

**Use case:** Open-response sentence stems requiring the student to use vocabulary meaning accurately without substituting a multiple-choice task.

### Answer control

- Preserve each printed sentence stem and highlighted vocabulary word exactly.
- Provide a large free-text area for the student's continuation, with a green `▶ Read my answer` control; include an optional microphone only if requested or supported by the child's profile.
- Never replace the creative completion with a list of prewritten responses. Typing, dictation, read-back, autosave, and printing remain independent of speech-recognition availability.
- Make directions and stems tappable for read-aloud. Keep the full lesson word bank and standard definition modal available throughout.
- Do not rebuild cards on every keystroke, so the cursor and dictation remain focus-safe.

### Feedback

- A nonempty continuation counts as a response; this authentic open-ended composition is an **explicit adult-review exception** to automated three-chance checking. Evaluate meaning by adult review rather than exact-string matching.
- Do not show a correctness score or fabricate a reference answer.

### Progress + persistence

- Persist each text response in a part-specific `localStorage` key.
- Show neutral completion progress and include double-tap Clear all responses and Export / Print using the child's print name.

**Reference implementation:** `docs/worksheets/2026-10-13-wordly-wise-lesson-4d-completing-sentences.html`

---

## Type 10: Vocabulary Using Words in Context — Correct / Incorrect Judgments

*Wordly Wise “Using Words in Context” style: each numbered group names one vocabulary word and prints four lettered sentences; the student judges whether the bold word or related form is used correctly in each sentence.*

**Use case:** Vocabulary usage discrimination across several separate sentences for each lesson word. A student records `C` for correctly used or `I` for incorrectly used; this is not a four-choice single-answer or multi-select exercise.

### Answer control

- **Begin every numbered question group with a prominent, independently tappable lesson headword**, before its four `(a)`–`(d)` sentences (e.g., **shed** for Lesson 6A #1). Tapping the headword opens the standard source-definition modal without selecting or checking anything.
- Preserve the source's complete sentence wording, letters, ordering, and **bold treatment of the vocabulary word or exact related form within every sentence**, whether that sentence uses the word correctly or incorrectly. Match explicit forms rather than guessing based on substrings.
- Each of the four sentences gets its own pair of large, mutually exclusive `C · Correct` / `I · Incorrect` answer buttons. A selection affects **only that sentence**, not its siblings; the absence of either choice means unanswered.
- Make each entire sentence independently tappable for read-aloud, with an optional per-group play button to read the four sentences. The bold vocabulary target may independently open its definition, but must not change the C/I response. Hearing a sentence never selects a letter.
- If an answer selection triggers a read-back, speak the sentence in either case without announcing correctness. The app does not assess or reveal correctness until the deliberate whole-exercise Check action.
- Retain the ordinary tappable directions, word bank, POS tags, and source definition/example cards. Use the original academic task, not a simplified multiple-choice paraphrase.

### Feedback

- Use the default **three whole-worksheet checks** against an **edition-matched and verified publisher/teacher answer key**. Check all forty sentence judgments in one action for a ten-group exercise; a group is not an indivisible question for scoring.
- On a check, distinguish **correct**, **answered but needs review**, and **unanswered** for **each individual sentence**. An untouched sentence remains unanswered even if another sentence in that group has an answer.
- Display a concept-specific hint about the vocabulary word's meaning for a needs-review judgment, without revealing the correct C/I label. Do not mark an answer correct immediately upon selection.
- Do not infer an answer key from a sentence's apparent plausibility if source verification is available. Use adult review only as an explicit, documented fallback when a reliable key cannot be established.

### Progress + persistence

- Count completion per individual sentence judgment (e.g., `14 / 40 answered`); optionally show ten group-level progress pips that fill when all four answers in the group have been selected.
- Persist all letter responses, remaining-check count, reviewed states, and revision flags in a part-specific `localStorage` key. Editing a reviewed sentence clears its stale status only, and does not reset review chances.
- Include double-tap Clear all responses and Export / Print.

### Export / Print

- Recreate all numbered groups and their four complete printed sentences, with the vocabulary word **bold** in each sentence and the headword before the group.
- Show each student's chosen `C` or `I` on that sentence's answer line using bold + underline. Leave unanswered lines blank. Omit interactive button outlines, review statuses, and publisher-key markings.

**Reference implementation:** `worksheets/christina/2026-10-26-wordly-wise-lesson-6a-using-words-in-context.html`.

---

## Type 11: Vocabulary Word Study — Latin Roots with Shared Previous-Lesson Bank

*Wordly Wise “Word Study: Word Parts” style: the student completes printed sentences by identifying vocabulary from earlier lessons using a parenthetical Latin prefix/root explanation.*

**Use case:** Sentence completion requires understanding and retrieval of prior vocabulary. A shared word reference reduces the recall and transcription barrier while preserving the need to apply root clues, word meaning, and sentence grammar. This is not question-by-question multiple choice.

### Layout + source fidelity

- Preserve all printed sentence stems, blanks, question numbers, and parenthetical root explanations. Do not reduce or rewrite the original Latin evidence or academic demand.
- Make the directions, full sentence, and root explanation separately tappable for read-aloud; the per-card green `▶` reads the full current sentence, with the selected word inserted.
- Place an alphabetized **previous-lesson reference bank at the top, collapsed by default**. Use the same yellow vocabulary word buttons, POS tags, source-definition modal cards, Definition/Example labeling, and card-level read-aloud as the weekly lesson word banks.
- Tapping a word in this top bank opens **only its definition and example**; it must never fill a blank, change the active question, mark a word used, update progress, or consume a check. Keep the reference word bank independent of the answer picker even if both show the same words.
- Include the needed answer forms and enough verified previous-lesson distractors to require meaningful comparison (Lesson 7D uses 30 shared choices: ten answers and 20 distractors from earlier lessons). Use previous-lesson source definitions and examples where available; if absent, clearly identify any supplementary outside-dictionary reference rather than presenting it as publisher wording.
- Do not replace the common bank with four targeted choices per question, filter to a handful of candidates based on the clue, or display a per-question answer hint in the bank.

### Answer control

- **Only tapping a missing-word blank within a numbered exercise opens the answer-selection dialog.** Its words are actual selectable choices; those in the top reference bank are not.
- The blank's dialog shows the full shared set of choices every time; retain used words unless the printed source requires unique usage. A subtle `used` marker is permitted in this answer picker, but never in a way that reveals correctness.
- Selecting a word in the **blank's dialog** fills that blank, closes the dialog, preserves source capitalization, and automatically reads the completed sentence after approximately 300ms. The student can reopen the same blank to revise.
- Keep root-clue read-aloud independent of word selection. Listening, opening the top reference, or viewing any definition never fills a blank or consumes a check.
- Retain the reference disclosure's expanded state during same-page answer updates where practical; always default closed on a fresh page load. Keep the worksheet's existing `localStorage` key and responses when making this UI-only correction.

### Feedback + progress

- Use a source-verified teacher/publisher key for three whole-worksheet checks. Compare the student's selected word/form to the corresponding printed answer, ignoring capitalization only where appropriate.
- An incorrect selection receives a conceptual reminder to review the prefix or Latin root **after checking**; never expose the target word as the hint or show instant correctness upon selection.
- Persist all selections, check attempts, and per-question review states in a part-specific `localStorage` key. Use neutral completion pips until checking; editing one answer clears only its own stale status.
- Provide double-tap Clear all responses and Export / Print. Print each original sentence and root explanation, showing only the student's selected word in the blank as bold + underline, without revealing a teacher key.

**Reference implementation:** `worksheets/christina/2026-11-02-wordly-wise-lesson-7d-word-study-word-parts.html` with matching published mirror `docs/worksheets/2026-11-02-wordly-wise-lesson-7d-word-study-word-parts.html`.
