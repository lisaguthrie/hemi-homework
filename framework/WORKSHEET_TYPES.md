# Worksheet Type Taxonomy

Each entry documents a worksheet type that has been successfully implemented. When a new type is built, add it here.

When processing a new worksheet, scan this list first. If the type matches, apply the pattern directly without re-inventing it.

---

## Type 1: Fill-in-the-blank — Word Class Replacement

*A sentence contains an underlined or highlighted word/phrase. The student replaces it with a word from a specific grammatical class (pronoun, verb tense, adjective, etc.).*

**Sentence structure:** `[before text?] [HIGHLIGHTED PHRASE] [after text]`

**Data shape:**
```javascript
{
  before:  "",                    // text before the phrase (may be empty string)
  phrase:  "Talent shows",        // the underlined/highlighted content
  after:   " can make people nervous.",
  answers: ["They"],              // accepted answers, case-insensitive compared
  hint:    "more than one show"   // shown on incorrect selection; names the concept
}

function buildFullSentence(q, answer) {
  return q.before + answer + q.after;
}
```

**Answer control:** Dropdown (`<select>`). Curate options to the plausible set for the worksheet — do not include every word in the class, only those that could be correct for at least one question.

**Answer evaluation:** `q.answers.map(a => a.toLowerCase()).includes(val.toLowerCase())`

**Reference:** `profiles/reference/2026-03-10-pronouns.html` — 14 questions, talent show theme. First implementation; treat as gold standard for this type.

---

## Type 2: [To be added]

*Add new types here as they are implemented. Include: description, data shape, answer control type, any special interaction considerations, and a reference to the first implementation.*

---

## Type 3: Guess and Check (Logic / Word Problem)

*A multi-constraint word problem where the student guesses values for variables and checks each relationship against the clues.*

**Interaction model:** Problem text broken into tappable sentences and highlighted clue pills. One numeric input per variable — **no mic buttons on number fields**. A second row of **intermediate step fields** shows derived values (e.g. Joy + Heidi, Joy + Heidi + Saul). An **auto-calculate checkbox** (unchecked by default) drives whether those fields compute automatically from primary inputs or accept manual entry — when checked, intermediate inputs become disabled and update live; when unchecked they are free-entry so the student works them out herself. A sequence of relationship-check buttons verifies each constraint and gives a directional hint. A guess history table logs every checked attempt, **upserting rows by input values to avoid duplicates**. Win state fires only when all checks pass simultaneously.

**Duplicate suppression in `logGuess` — upsert pattern:**
```javascript
function logGuess() {
  const {joy, heidi, saul} = getVals();  // adapt variable names per problem
  if (joy === null && heidi === null && saul === null) return;
  // Upsert: find existing row with same input values and update pass flags,
  // or append a new row. This ensures each check press on the same guess
  // updates the single row rather than being suppressed or duplicated.
  const existing = state.guesses.findIndex(
    g => g.joy === joy && g.heidi === heidi && g.saul === saul
  );
  const entry = {
    joy, heidi, saul,
    c1: state.passed[0], c2: state.passed[1], c3: state.passed[2]
  };
  if (existing >= 0) {
    state.guesses[existing] = entry;
  } else {
    state.guesses.push(entry);
  }
  saveState();
  renderHistory();
}
```
Adapt variable names and the number of `c` fields to match the problem's variables and constraint count.

**Intermediate fields pattern:**
```javascript
function onAutoCalcChange() {
  const auto = document.getElementById('autoCalc').checked;
  document.getElementById('inputJoyHeidi').disabled = auto;
  document.getElementById('inputTotal').disabled    = auto;
  if (auto) updateIntermediates();
  saveState();
}

function updateIntermediates() {
  if (!document.getElementById('autoCalc').checked) return;
  const {joy, heidi, saul} = getVals();
  document.getElementById('inputJoyHeidi').value = (joy !== null && heidi !== null) ? joy + heidi : '';
  document.getElementById('inputTotal').value    = (joy !== null && heidi !== null && saul !== null) ? joy + heidi + saul : '';
}
```
Call `updateIntermediates()` at the top of `onInputChange()`. Checkbox defaults unchecked — she practices the arithmetic manually, but can switch to auto-calc to focus on the logic.

**Data shape:** Constraints encoded directly in check functions; no declarative data object needed.

**Feedback:** Uses `showFeedback(fbId, pass, text)` from INTERACTION_PATTERNS.md — **never auto-speaks**. Each hint names the specific relationship that failed and says whether the value is too high or too low. The `feedbackTexts` store is required.

**Guess history table columns:** attempt #, one column per variable, one column per constraint (✅ / ✗).

**Win state:** Detect when all checks pass simultaneously; show a banner and speak a congratulatory message with the solution values.

**Export / Print button:** Required. See Export / Print section in INTERACTION_PATTERNS.md.

**Reference implementation:** `profiles/reference/2026_03_11_guess-check.html` - skating rink problem, Joy/Heidi/Saul, 3 constraints, total = 64 min

---

## Type 4: Identify the Antecedent (Sentence Pair)

*Two related sentences are shown together as a pair. A pronoun in the second sentence is highlighted. The student identifies which noun from the first sentence the pronoun replaces.*

**Sentence structure:**
```
Sentence 1: [full sentence containing the antecedent noun]
Sentence 2: [sentence with pronoun highlighted]
```

**Data shape:**
```javascript
{
  s1:      "The woodcutter saw a neighbor working in the garden.",
  s2:      "The woodcutter approached him.",
  pronoun: "him",           // the highlighted pronoun in s2
  answer:  "a neighbor",   // the correct antecedent from s1
  options: ["The woodcutter", "a neighbor", "the garden"],  // dropdown choices
  hint:    "him = one man receiving the action"
}
```

**Answer control:** Dropdown listing the candidate nouns from s1. Label reads: `"[pronoun]" replaces →`. Auto-reads `"[pronoun]" replaces [selected noun].` after selection (300ms delay).

**Interaction decisions:**
- Both sentences are tappable (read full text on tap)
- Pronoun in s2 is highlighted with a blue chip (`background: #e8f0ff; border: 2px solid #3b9ede`) to distinguish it from the yellow phrase chips used for tappable noun phrases in Type 1
- Per-card play button reads both sentences together
- Feedback: correct → `Yes! "[pronoun]" replaces [noun].` / incorrect → hint naming the pronoun type and number
- **Print rendering:** Pronoun in S2 is underlined+bold. Answered noun is highlighted inline in S1 using a colored span (green `#d0f5e0`/`#5dca7e` if correct, orange `#ffeedd`/`#ff9966` if incorrect); match the noun case-insensitively. Unanswered items show sentences plain with no label row. Do not include a "replaces →" label — the visual relationship between highlighted noun and underlined pronoun is self-evident.

**Passage panel + one-card navigation (for proofreading worksheets):**

The full-stack-of-cards layout is visually cluttered for proofreading worksheets. Use a passage panel + one active card at a time instead.

**Passage panel** (always visible at top of page): Full passage text rendered as inline tappable sentence `<span>` elements. Tapping any sentence navigates to that sentence's work card.

Passage sentence CSS states:
- `.ps-active` — bold, yellow background, gold outline ring (currently active)
- `.ps-done` — muted gray text (correctly completed)
- `.ps-second-pass` — soft yellow background (needs revisiting)

**One work card at a time:** All sentence cards are `display:none` by default. Only the active card gets the `.visible` class (`display:block`). `navigateTo(i)` hides the current card, shows card `i`, auto-reads the sentence, and scrolls into view.

**Next button:** Appears inside the correct-answer feedback. Calls `goToNext()`, which finds the next unsubmitted sentence (wraps around; respects second-pass mode). Hidden when all sentences are submitted.

**Navigation function:**
```javascript
function navigateTo(i) {
  if (currentCard) currentCard.classList.remove('visible');
  state.activeIndex = i;
  saveState();
  currentCard = document.getElementById(`card-${i}`);
  currentCard.classList.add('visible');
  updatePassageHighlights();
  updateProgress();
  setTimeout(() => speak(sentences[i].text), 200);
  setTimeout(() => currentCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 100);
}
```

**Collapsible marks legend:** Proofreading marks panel starts collapsed. Tap the header to expand. Reduces visual noise on load.

**Reference implementation:** `profiles/reference/2026-03-16-subj-obj-pronouns-a.html`

## Type 5: Label Pronouns Subject or Object (S/O Classification)
 
*Each sentence contains one or more pronouns, each highlighted in yellow. The student classifies each pronoun as S (subject pronoun) or O (object pronoun) using a per-pronoun dropdown.*
 
**Sentence structure:**
```
[sentence with one or more pronouns highlighted]
```
 
**Data shape:**
```javascript
{
  sentence: '"I want you to chop some wood," she said.',
  pronouns: [
    { word: "I",   answer: "S", hint: "I performs the action — subject pronoun" },
    { word: "you", answer: "O", hint: "you receives the action here — object pronoun" },
    { word: "she", answer: "S", hint: "she performs the action of saying — subject pronoun" }
  ]
}
```

**Answer control:** One `S — subject / O — object` dropdown per pronoun. Pronouns are tokenized from the sentence text and highlighted as yellow phrase chips. After selection, auto-reads `"[pronoun] is a subject/object pronoun. It performs/receives the action."` (300ms delay).

**Progress tracking:** Flatten all per-pronoun answers across all questions into a single array for pip counting and answered/total display.

**Card state:** Card border turns green only when all pronouns in that card are answered correctly (`all-correct` class).

**Interaction decisions:**
- Every word in each sentence is a tappable span (speaks the word aloud on tap).
- Tapping a word that **is** a pronoun (per the answer key) highlights it yellow and reveals a labeled S/O answer row below the sentence.
- Tapping a word that **is not** a pronoun flashes it red briefly — no dropdown appears.
- Answer rows appear in a `.pronoun-answers-below` container beneath the sentence, indented to connect visually. Each row shows a yellow chip with the word, the S/O dropdown, and (after selection) the feedback badge.
- The word span gains `.answered` (green) when the S/O selection is correct.
- **Print rendering:** Each pronoun is underlined+bold with its S/O label as a superscript badge (colored span: green if correct, orange if incorrect, grey `_` if unanswered). Sentence text is reconstructed by tokenising on word boundaries and replacing pronoun occurrences in order — handle repeated words (e.g. "I" appearing twice) by tracking a per-word usage count.

**Reference implementation:** `profiles/reference/2026-03-16-subj-obj-pronouns-b.html`

---

## Type 6: Choose the Correct Pronoun (Binary Parenthetical)

*A sentence contains a parenthetical pair of pronoun choices, e.g. `(he, him)`. The student selects the grammatically correct one.*

**Sentence structure:** `[before text?] (choice1, choice2) [after text?]`

**Data shape:**
```javascript
{
  before:  "The woodcutter's wife warns ",
  choices: ["he", "him"],
  after:   ".",
  answer:  "him",
  hint:    "the woodcutter receives the warning — object pronoun"
}
```

**Answer control:** Dropdown showing both choices. A tappable yellow chip displays the choices inline in the sentence (`(he, him)`); tapping it reads both options aloud. Part-of-sentence tap-to-speak applies to `before` and `after` segments.

**Interaction decisions:**
- Yellow chip reads `"choice1 or choice2?"` on tap
- After selection, auto-reads the full sentence with the chosen word substituted (300ms delay)
- Feedback: correct → full sentence read aloud / incorrect → hint naming subject vs. object role
- If a bonus free-text section is present, pair with mic button (STT) and read-back button
- **Print rendering:** Both choices are always kept in parentheses — never collapse to just the answer. The selected choice is highlighted inline with a colored span (green if correct, orange if incorrect); the other choice renders as plain text. Unanswered items show the plain parenthetical with no highlight. This mirrors the original worksheet's "circle the correct word" format.

**Reference implementation:** `profiles/reference/2026-03-16-subj-obj-pronouns-c.html`

---

## Type 7: Proofreading / Error Correction

*A paragraph or passage contains seeded errors. The student reads sentence by sentence, decides if each sentence has an error, identifies the word and error type using proofreading marks, and receives feedback. A second-pass mode re-presents any missed sentences.*

**Layout:** Passage panel (always visible) + one work card at a time — see Passage Panel pattern below.

**For each work card:**
1. Two large decision buttons: ✅ Looks good / 🔍 Fix it
   - "Looks good" on a no-error sentence → finalizes immediately (correct)
   - "Looks good" on an error sentence → shows hint, keeps card open so student can switch to "Fix it"
   - "Fix it" → reveals the mark panel
2. Word chips — each word in the sentence is a tappable chip; tapping selects it as the error target. Any word can be selected at any time, including already-found ones (visual only — re-submitting a found word gives a gentle nudge: "You already found that one!")
3. Mark type grid — 8 buttons: Capitalize, Lowercase, Delete, Add comma, Fix spelling, Add apostrophe, Add punctuation, Fix verb
4. Confirm button — enabled only when both a word chip and a mark type are selected
5. Wrong attempts show feedback but do NOT lock the card — student can re-tap and resubmit
6. Card only finalizes (locks, turns green) on a fully correct answer

**Multi-error sentences:** The `errors` array supports multiple errors per sentence. Finding one error shows positive feedback + "There are N more errors — keep looking!" and highlights the found word. Card finalizes only when all errors are found.

**Alternative mark types:** Some errors can reasonably be marked with either of two mark types (e.g. "Add punctuation" or "Add comma" for a missing comma). Use `altErrorType` on the error object and check both in the match logic:
```javascript
const matchedError = s.errors.find(e =>
  e.wordIndex === wi && (e.errorType === mark || e.altErrorType === mark)
);
```

**Second-pass mode:** After all sentences are submitted, sentences with errors the student missed are re-presented with a yellow highlight and a spoken prompt. Cards reset fully (decisions, selections, foundErrors) to allow re-answering. Win state fires only when all error sentences are correctly identified.

**Data shape:**
```javascript
// Error sentence (single error)
{
  text: "Exact sentence text as it appears in the original, errors preserved.",
  hasError: true,
  errors: [
    {
      wordIndex: 1,              // 0-based index in text.split(' ') — verify programmatically
      errorType: "capitalize",   // mark type id (see list below)
      altErrorType: null,        // optional second accepted mark type, or null
      feedbackCorrect: "Yes! 'Arctic' is a proper noun and should be capitalized.",
      correctSpelling: null      // corrected word, only for spelling errors
    }
  ],
  errorNote: "Arctic is a proper noun — capitalize it",   // shown in wrong-mark-type hint
  feedbackHint: "Is there a proper noun that needs a capital letter?"
}

// Multi-error sentence
{
  text: "They huddle toogether in large groups to keep warm and to protect each other form predators.",
  hasError: true,
  errors: [
    { wordIndex: 2,  errorType: "spelling", altErrorType: null, feedbackCorrect: "...", correctSpelling: "together" },
    { wordIndex: 14, errorType: "spelling", altErrorType: null, feedbackCorrect: "...", correctSpelling: "from" }
  ],
  errorNote: "Two spelling errors in this sentence",
  feedbackHint: "There are two misspelled words in this sentence."
}

// No-error sentence
{
  text: "In the winter, the fur is white to camouflage it.",
  hasError: false,
  noError: true,
  feedbackOk: "Correct — this sentence has no errors!"
}
```

**Mark type IDs:** `capitalize` | `lowercase` | `delete` | `comma` | `spelling` | `apostrophe` | `punctuation` | `verb`

**State shape (additions over base):**
```javascript
foundErrors: new Array(sentences.length).fill(null),
// Per sentence: array of wordIndexes already correctly identified
// e.g. foundErrors[2] = [8] means word at index 8 found, index 11 still needed

activeIndex: 0,
// Persists last-viewed sentence across reloads
```

**Partial-find feedback grammar:**
```javascript
const remaining = s.errors.length - state.foundErrors[i].length;
partialText += ` There ${remaining === 1 ? 'is 1 more error' : `are ${remaining} more errors`} in this sentence — keep looking!`;
```

**Comprehension Questions Phase:**

After proofreading completes (win state fires), the proofreading UI is hidden and a comprehension section is revealed. This is the canonical pattern for Type 7 worksheets that include reading comprehension.

*Hide proofreading UI on completion:*
```javascript
function hideProofreadingSection() {
  [
    document.querySelector('.instructions'),
    document.getElementById('marksLegend'),
    document.querySelector('.passage-card'),
    document.querySelector('.progress-bar'),
    document.getElementById('phaseBadge'),
    document.getElementById('secondPassIntro'),
    document.getElementById('winBanner'),
    document.getElementById('sentenceList')
  ].forEach(el => { if (el) el.style.display = 'none'; });
}
```
Call `hideProofreadingSection()` at the start of `showQSection()`. Also guard `navigateTo()` on init — only call it when proofreading is not yet complete, since there is no active card once the Q phase is shown.

*DOM order after proofreading completes:*
1. Section divider card (`#sectionDivider`) — heading "✨ Comprehension Questions", brief instruction line
2. Corrected passage card (`#correctedPassageCard`) — the fully corrected text
3. Q cards (`#qSection`) — one card per question

*Corrected passage card:* A purple-themed card placed **between** the section divider and the first question card. Contains:
- ▶ play button that reads the entire corrected passage via TTS
- Each corrected sentence rendered as a tappable `.passage-sentence` span; tap reads that sentence aloud
- A brief hint line: "Tap any sentence to hear it read aloud."
- Styled to match the Q section color family (purple borders, `#f8f4ff` background)

Author a `correctedSentences` array (string per sentence, all errors fixed) alongside the `sentences` data array. Build the card lazily on first reveal, idempotent:
```javascript
const correctedSentences = [
  "Sentence one, fully corrected.",
  // ...
];

function buildCorrectedCard() {
  const container = document.getElementById('correctedPassageText');
  if (container.children.length > 0) return; // already built
  correctedSentences.forEach((sentence, i) => {
    const span = document.createElement('span');
    span.className = 'passage-sentence';
    span.textContent = sentence;
    span.onclick = () => speak(sentence);
    container.appendChild(span);
    if (i < correctedSentences.length - 1) container.appendChild(document.createTextNode(' '));
  });
  document.getElementById('corrPlayBtn').onclick = () => speak(correctedSentences.join(' '));
  document.getElementById('correctedPassageCard').classList.add('show');
}
```

*Q card data shape:*
```javascript
const compQuestions = [
  { text: "What does In like a lion, out like a lamb mean?", num: 1 },
  // ...
];
```

*Q card interaction:*
- Question text tappable (reads aloud) + per-card ▶ play button (purple, matches Q section)
- `<textarea>` for typed responses (min-height 120px, resizable)
- Mic button (🎤 / ⏹ toggle, continuous STT, appends transcript to textarea)
- "🔊 Read back" button — speaks textarea value or "Nothing written yet."
- Q progress: pip row + answered count, same pattern as proofreading progress

*Page restore (proofreading already done):* `showQSection()` is the single entry point — it calls `hideProofreadingSection()`, `buildCorrectedCard()`, shows the divider/q-section/progress, and scrolls to the section divider. Do **not** call `navigateTo()` on init when `allSubmitted` is true.

**Print rendering (Type 7):**

Type 7 export/print must look like a typewritten version of handwritten markup, not a scoring report.

- Preserve full passage content sentence by sentence; do not reduce output to a checkmark-only table.
- Render expected error words inline with visible proofreading marks:
  - Found/correctly identified error words: red pen-style outline + warm yellow marker swash + proofreading symbol superscript.
  - Missed expected error words: orange dashed outline + light orange marker swash + proofreading symbol superscript.
- For each sentence, include a right-margin "teacher notes" callout bubble (red pen style) listing typed correction notes (example: `herd -> heard (Fix spelling)`, `Add comma after "bears"`).
- Keep the proofreading legend in the print view so symbols are self-explanatory.
- Keep comprehension responses in print output.
- Do not include a "Sentence Status" summary section for Type 7 unless explicitly requested.

This print format intentionally mimics manual paper markup while remaining fully typewritten and readable.

**Reference implementations:**
- `worksheets/christina/2026-03-30-in-like-a-lion.html` — full implementation with comprehension questions phase (canonical)

---

## Type 8: Two-Step Word Identification (Tap Pronoun → Tap Noun)

*A sentence is rendered word by word. The student first taps the target word (e.g. the possessive pronoun), which highlights it and prompts step 2. Then the student taps a second related word (e.g. the noun it describes). Both words highlight on completion; wrong taps flash red briefly.*

**Data shape:**
```javascript
{
  text:    "My family is moving next summer, so we're cleaning out the house.",
  pronoun: "My",       // the word to find in step 1
  noun:    "family"    // the word to find in step 2
}
```

**State shape:** Integer per question: `0` = untouched, `1` = step 1 complete, `2` = both steps complete. Store as array of integers (not booleans — bump storage key if migrating from boolean saves).

**Interaction decisions:**
- Step 1 correct tap: word highlights gold (`.pronoun-found`), a purple step-hint banner appears below the sentence: "👆 Now tap the noun it describes"
- Step 1 wrong tap: flash red animation, speak the tapped word, no state change
- Step 2 correct tap: noun highlights gold+green (`.pronoun-found.answered`), pronoun also gains `.answered`, banner hides, card turns green, speaks confirmation e.g. *"their describes honeymoon. Well done!"*
- Step 2 wrong tap: flash red, speak the tapped word, no state change; tapping the pronoun again in step 2 just speaks it
- Tapping the whole sentence area (non-word zone) reads the full sentence at any time
- Per-card ▶ play button reads the full sentence
- Cards lock (state 2) and cannot be un-done

**Progress tracking:** Pips and count key off `state === 2` only — step-1-only progress does not advance pips.

**Reference implementation:** `worksheets/reference/2026-03-24-possessive-pronouns.html`, Section 1 (Part A)

---

## Type 9: Pronoun Pair Sentence Composer (Choose Pair → Free Write + Optional Scaffold)

*The student chooses a pronoun pair from a dropdown (e.g. "her / hers"), then writes a sentence using both pronouns in a free-text area with mic + read-back. A "Help Me" button reveals a pre-authored scaffold sentence with inline dropdowns for the blanks. When all scaffold dropdowns are correct, the full sentence auto-fills the textarea.*

**Use case:** Part C of pronoun worksheets — "Choose three pairs and write a sentence using each."

**Data shape (pre-authored scaffolds — one per possible pair):**
```javascript
{
  label: "her / hers",
  speak: "her and hers",       // spoken when pair is selected
  scaffold: {
    segments: [
      { text: "Sofia forgot " },
      { blank: true, options: ["— pick —","her","hers"], answer: "her" },
      { text: " umbrella, so the blue one must be " },
      { blank: true, options: ["— pick —","her","hers"], answer: "hers" },
      { text: "." }
    ],
    full: "Sofia forgot her umbrella, so the blue one must be hers."
  }
}
```

**Key authoring rule:** Author a scaffold for **every possible pair** the student might pick — not just the required number of slots. At runtime the student selects N pairs (e.g. 3) and each slot renders the scaffold for whichever pair she chose.

**Interaction decisions:**
- Pair picker dropdown auto-reads the pair name (e.g. "her and hers") on selection
- Free-text area + mic + read-back always visible, not gated behind Help Me
- Help Me button: reveals the scaffold sentence; text segments within the scaffold are individually tappable (speak just that segment); the full-sentence ▶ button speaks the `full` string
- When all scaffold blanks are correct: `full` sentence auto-fills the textarea (only if textarea is currently empty), reads aloud, and `updateProgress()` is called
- Wrong scaffold blank: shows `💡 Try [answer]` feedback inline
- Changing the pair selector clears the scaffold and resets scaffold answers
- Progress pips key off whether the free-text area has any non-empty content

**Storage:** Per slot: `{ pair: '3', freeText: 'Sofia forgot...', scaffoldAnswers: ['her','hers'], scaffoldShown: true }`

**Rewrite-with-Help Sub-Pattern:**

*The student rewrites a sentence by replacing an underlined noun phrase with a pronoun. Default view: free-text area + mic + read-back only. "Help Me" replaces the text box label area with a structured version of the sentence where the underlined noun is swapped for a full-pronoun-set dropdown.*

**Key difference from Type 9 scaffold:** Help Me does not hide the textarea — it adds the dropdown above it. Selecting the correct pronoun from the dropdown auto-fills the textarea with the rewritten sentence.

**Interaction decisions:**
- Always read aloud the sentence with the chosen pronoun on dropdown change, correct or wrong
- Wrong selection: shows hint, speaks the (wrong) sentence so she can hear why it sounds off
- Correct selection: fills textarea, speaks sentence, advances pip
- Help Me button hides itself after tap (one-way reveal)

**Reference implementation:** `profiles/reference/2026-03-24-possessive-pronouns.html`, Section 5 (Part B p.2)
**Reference implementation:** `worksheets/reference/2026-03-24-possessive-pronouns.html`, Section 3 (Part C)

---

## Adding a New Type

When you implement a worksheet that doesn't match an existing type:

1. Build it
2. At the end of your response, include a **📋 Framework Update Suggested** block with:
   - The type name and one-sentence description
   - The data shape
   - The answer control used
   - Any interaction decisions worth preserving
   - The filename of the reference implementation

The human will add it to this file manually (or the propagation runner will PR it).