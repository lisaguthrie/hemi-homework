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

**Reference:** `worksheets/reference/2026-03-10-pronouns.html` — 14 questions, talent show theme. First implementation; treat as gold standard for this type.

---

## Type 2: [To be added]

*Add new types here as they are implemented. Include: description, data shape, answer control type, any special interaction considerations, and a reference to the first implementation.*

---

## Type 3: Guess and Check (Logic / Word Problem)

*A multi-constraint word problem where the student guesses values for variables and checks each relationship against the clues.*

**Interaction model:** Problem text broken into tappable sentences and highlighted clue pills. One numeric input per variable — **no mic buttons on number fields**. A second row of **intermediate step fields** shows derived values (e.g. Joy + Heidi, Joy + Heidi + Saul). An **auto-calculate checkbox** (unchecked by default) drives whether those fields compute automatically from primary inputs or accept manual entry — when checked, intermediate inputs become disabled and update live; when unchecked they are free-entry so the student works them out herself. A sequence of relationship-check buttons verifies each constraint and gives a directional hint. A guess history table logs every checked attempt, **skipping duplicates**. Win state fires only when all checks pass simultaneously.

**Duplicate suppression in `logGuess`:**
```javascript
if (guesses.length > 0) {
  const last = guesses[guesses.length - 1];
  if (last.joy === joy && last.heidi === heidi && last.saul === saul) return;
}
```

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

**Reference implementation:** `worksheets/reference/2026_03_11_guess-check` - skating rink problem, Joy/Heidi/Saul, 3 constraints, total = 64 min

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

**Reference implementation:** `worksheets/reference/2026-03-16-subj-obj-pronouns-a.html`

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

**Reference implementation:** `worksheets/reference/2026-03-16-subj-obj-pronouns-b.html`

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

**Reference implementation:** `worksheets/reference/2026-03-16-subj-obj-pronouns-c.html`

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