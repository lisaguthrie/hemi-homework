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

## Type 5: Click-to-Identify Pronouns (Subject or Object)

*Every word in a sentence is tappable. The student clicks words to identify which are pronouns, then classifies each pronoun as subject or object.*

**Interaction model:** 
- Every word in each sentence is a tappable span (speaks the word aloud on tap).
- Tapping a word that **is** a pronoun (per the answer key) highlights it yellow and reveals a labeled S/O answer row below the sentence.
- Tapping a word that **is not** a pronoun flashes it red briefly — no dropdown appears.
- Answer rows appear in a `.pronoun-answers-below` container beneath the sentence, indented to connect visually. Each row shows a yellow chip with the word, the S/O dropdown, and (after selection) the feedback badge.
- The word span gains `.answered` (green) when the S/O selection is correct.
- Pre-identification removed — the act of finding pronouns is part of the task.
- Inline dropdowns are NOT used; all answer rows live below the sentence in a dedicated area.
- Feedback is displayed in the below-sentence rows, not inline.

**Data shape:**
```javascript
{
  text: "The full sentence text",
  pronouns: [
    { word: "I", type: "subject" },
    { word: "her", type: "object" }
  ]
}
```

**Answer control:** Dropdown (`<select>`) with options "subject" and "object", displayed in the answer row below the sentence after a pronoun is identified.

**Answer evaluation:** Compare selected type against the pronoun's `type` property in the answer key.

**Reference implementation:** `worksheets/reference/2026-03-16-subj-obj-pronouns-b.html` (post-iteration)

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