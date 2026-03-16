# Pending Framework Updates

Update suggestions from worksheet generation sessions accumulate here.
Run `python runners/propagate.py` to process them into GitHub PRs.

<!-- Updates appended below by watcher.py and cli.py -->


---
Trigger Worksheet: C:\Users\lisac\OneDrive\Scans\Arctic Animals.pdf
Generated Output: worksheets/christina/2026-03-15-arctic-animals.html

📋 Update Suggested

**Target:** `framework/WORKSHEET_TYPES.md`

**Rationale:** This worksheet represents a new type not in the taxonomy — proofreading with error correction.

**Proposed Addition:**

---

## Type 4: Proofreading — Error Identification and Correction

*A passage contains errors (spelling, grammar, punctuation, capitalization). Each error is presented as a fill-in-the-blank where the student selects the corrected form.*

**Sentence structure:** `[before text] [ERROR PHRASE] [after text]`

**Data shape:**
```javascript
{
  before:  "However, ",              // text before the error
  phrase:  "their",                   // the incorrect text as it appears
  after:   " are many animals...",    // text after the error
  answers: ["there"],                 // accepted corrections (may include alternatives)
  hint:    "homophones — their vs. there"  // names the error type
}

function buildFullSentence(q, answer) {
  return q.before + answer + q.after;
}
```

**Answer control:** Dropdown (`<select>`). Populate with all unique correct answers from across all questions in the worksheet, sorted alphabetically. This creates a realistic proofreading challenge — she must identify which correction applies to each error.

**Answer evaluation:** `q.answers.some(a => a.toLowerCase() === val.toLowerCase())`

**Special considerations:**
- The passage should be presented in full at the top of the worksheet (read-only, with errors intact) so she can see the complete text before working through corrections
- Include a proofreading marks legend box (tappable, speaks full description) if the original worksheet provides one
- Hint text should name the error type (homophones, capitalization, punctuation, spelling, etc.) rather than generic "try again"

**Reference:** `worksheets/christina/2026-03-15-proofreading.html` — Arctic Animals passage, 14 errors across spelling, grammar, punctuation, and capitalization.


---
Trigger Worksheet: C:\Users\lisac\OneDrive\Scans\Arctic Animals.pdf
Generated Output: worksheets/christina/2026-03-15-arctic-animals.html

📋 Update Suggested

**File:** `framework/WORKSHEET_TYPES.md`

**Section:** Add after Type 3

**Content:**

```markdown
## Type 4: Proofreading / Error Identification

*A passage contains sentences with deliberate errors (capitalization, punctuation, spelling, grammar). The student identifies the error type using a proofreading mark key.*

**Sentence structure:** Full sentence with one identifiable error. Often a specific phrase contains the error.

**Data shape:**
```javascript
{
  sentence: "The arctic fox has a thick coat of fur to protect it from the cold.",
  phrase:   "arctic fox",      // the portion containing the error (for chip highlighting)
  error:    "arctic should be capitalized",  // human-readable description
  answers:  ["Capitalize", "≡"],  // accepted answer forms (text + symbol)
  hint:     "capitalize proper nouns"  // concept-level hint
}
```

**Answer control:** Dropdown with proofreading mark options. Include both text labels and symbols where applicable (e.g. "Capitalize" and "≡").

**UI requirements:**
- Proofreading marks key displayed prominently above questions
- Each sentence tappable to hear full sentence
- Error phrase highlighted as a chip that reads just that phrase on tap
- Feedback hints name the grammatical concept, never just "wrong"

**Interaction notes:**
- Auto-read after answer selection reads: "The error is: [error description]. Your answer: [selected mark]."
- Some errors may have multiple valid interpretations (e.g. "blubber." could take either period or colon) — accept correct in context

**Reference:** Arctic Animals proofreading worksheet, March 2026 (12 questions, passage format).
```

**Reason:** This is a distinct worksheet type not covered by existing patterns. The proofreading mark taxonomy and the interplay between full-sentence reading and error-phrase highlighting create specific interaction requirements worth documenting.


---
Trigger Worksheet: C:\Users\lisac\OneDrive\Scans\Arctic Animals.pdf
Generated Output: worksheets/christina/2026-03-15-arctic-animals.html

📋 Update Suggested

**File:** `framework/WORKSHEET_TYPES.md`

**Section:** Add new type after Type 3

**Content:**

```markdown
## Type 4: Proofreading — Error Identification and Correction

*A passage contains embedded errors (spelling, punctuation, capitalization, grammar). Each question isolates one error within a sentence. The student identifies the error type and selects the appropriate correction from a dropdown.*

**Sentence structure:** Full sentence from passage quoted in question text. Error is embedded within it (not highlighted, as the task is to find it).

**Data shape:**
```javascript
{
  text:      "Find the error in: 'The arctic fox has a thick coat...'",  // question prompt
  sentence:  "The arctic fox has a thick coat of fur...",                // full sentence for TTS
  errorType: "Capitalize",                                                // category of error
  answers:   ["Capitalize 'Arctic'", "Capitalize Arctic"],                // accepted phrasings
  hint:      "the name of a specific place should be capitalized"        // concept-specific hint
}
```

**Answer control:** Dropdown (`<select>`). Options curated to the errors present in the worksheet — typically one option per question plus a default "— pick an answer —".

**Answer evaluation:** `q.answers.some(a => val.toLowerCase().includes(a.toLowerCase().trim()))` — allows flexible matching on phrasing.

**Interaction considerations:**
- **Passage card:** The full passage (with all errors intact) is presented in a tappable card above the questions. Tapping it reads the entire passage aloud. This lets her hear the errors in context before working through the questions.
- **Proofreading marks legend:** If the original worksheet includes a proofreading marks reference (≡ for capitalize, ^ for add comma, etc.), include it as a tappable reference card. Do not require her to use the marks — the dropdown handles all input.
- **Play button per question:** Each question has a play button that reads the full sentence aloud (not just the question text), so she can re-hear the error in context while working.
- **Sentence-level granularity:** Each question isolates one error in one sentence. If a sentence has multiple errors, create multiple questions targeting that sentence (see Q9 in reference implementation, which identifies two spelling errors in one sentence).

**Reference:** `worksheets/christina/2026-03-12-proofreading-arctic.html` — Arctic Animals passage, 9 questions covering capitalization, punctuation, spelling, article usage, and sentence fragments.
```

**Reason:** This is a new worksheet type not currently in the taxonomy. Proofreading worksheets are common in elementary curricula and have a distinct interaction model: error identification within a continuous passage, sentence-level TTS on demand, and curated dropdown corrections. The pattern is worth preserving.
