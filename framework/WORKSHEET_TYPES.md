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

**Reference:** `worksheets/christina/2026-03-10-pronouns.html` — 14 questions, talent show theme. First implementation; treat as gold standard for this type.

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

**Reference implementation:** Skating rink problem, March 2026 (Joy/Heidi/Saul, 3 constraints, total = 64 min).

---

## Type 4: Proofreading - Error Identification and Correction

*A passage contains errors (spelling, grammar, punctuation, capitalization). Each error is presented as a fill-in-the-blank where the student selects the corrected form.*

**Sentence structure:** `[before text] [ERROR PHRASE] [after text]`

**Data shape:**
```javascript
{
  before:  "However, ",               // text before the error
  phrase:  "their",                   // incorrect text as it appears in the source
  after:   " are many animals...",    // text after the error
  answers: ["there"],                 // accepted corrections (may include alternatives)
  hint:    "homophones - their vs. there"
}

function buildFullSentence(q, answer) {
  return q.before + answer + q.after;
}
```

**Answer control:** Dropdown (`<select>`). Populate with all unique correct answers from across all questions in the worksheet, sorted alphabetically, so the student must decide which correction belongs in each sentence.

**Answer evaluation:** `q.answers.some(a => a.toLowerCase() === val.toLowerCase())`

**Special considerations:**
- Show the full original passage at the top as read-only context, preserving worksheet text exactly (including original errors, capitalization, and punctuation)
- Include a proofreading marks legend box (tappable/read-aloud) when provided on the worksheet
- Hint text should name the error type (homophones, capitalization, punctuation, spelling, etc.) instead of generic negative feedback

**Reference:** `worksheets/christina/2026-03-15-arctic-animals.html` - Arctic Animals passage with proofreading corrections.

---

## Adding a New Type

When you implement a worksheet that doesn't match an existing type:

1. Build it
2. At the end of your response, include a **📋 Baseline Spec Update Suggested** block with:
   - The type name and one-sentence description
   - The data shape
   - The answer control used
   - Any interaction decisions worth preserving
   - The filename of the reference implementation

The human will add it to this file manually (or the propagation runner will PR it).
