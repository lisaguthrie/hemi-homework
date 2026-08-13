# Tool Type Taxonomy

Tools are reusable, standalone HTML files that help a student work through a specific kind of computation or concept. Unlike worksheet apps (which reproduce a specific assignment), tools are general-purpose and child-operated — the student enters the numbers themselves.

Tools live in `tools/{subject}/` and are linked from subject index pages (`tools/math/index.html`, etc.) and from worksheet hint panels.

---

## Tool Conventions (apply to all tools)

### Input
- **Setup inputs** (entering the problem) use regular keyboard/numeric text fields — the student looks at her paper and types the numbers in.
- **Work inputs** (filling in intermediate steps and the answer) use a **numpad bottom sheet** — large tap targets (64px height), no keyboard. This is the core accessibility win for one-handed use.

### Numpad behavior
- **Single-digit cells** (answer digits, carry digits): each tap *replaces* the current value. Numpad closes immediately after one tap.
- **Multi-digit cells** (borrow boxes, or any cell that can hold a 2-digit value): each tap *appends* to the current value (max 2 digits). A value preview is shown in the numpad sheet as digits are entered. **Clear** wipes the whole value. Numpad stays open until the student taps outside.

### Settings
- Any configurable behavior should be exposed via a **settings bottom sheet** (⚙️ button in the header).
- Settings are persisted to `localStorage` using a tool-specific key (e.g. `subtraction-tool-v1-settings`).
- Keep settings minimal — one or two options max per tool.

### Feedback
- Correct answer: answer cells turn green, a result chip appears showing the full expression (e.g. `✅ 48 − 7 = 41`). Confirm button hides.
- Wrong answer: answer cells shake and show red briefly. A directional hint appears (e.g. "Too high — check your borrowing.").
- No TTS in tools — these are number-focused and the student can read the simple feedback labels.

### Navigation
- A **"← New problem"** button resets the tool to the setup state.
- A **back arrow** in the header links to the subject index (`../index.html`).

### Leading zeros
- Empty answer cells to the left of the first filled cell are treated as `0` for checking purposes — the student should not need to enter a leading zero.

---

## Tool 1: Subtraction

**File:** `tools/math/subtraction.html`
**Reference:** Built 2026-03-18

*The student enters a top number and a bottom number. The tool renders a vertical subtraction layout with a borrow row above the top number.*

**Setup:** Two keyboard text inputs (top number, bottom number). Validates that bottom ≤ top.

**Borrow interaction:**
- Tap any top-row digit to **cross it out** (strikethrough in red). A borrow box appears above it.
- Tap the same digit again to un-cross it and clear the borrow box.
- Borrow boxes accept multi-digit values (e.g. "13") via the append-mode numpad.
- Answer cells accept single digits via the replace-mode numpad.

**Settings:**
- **Borrowing helper** (default off): when on, crossing out a digit also crosses out the digit to its right and shows a borrow box there too. Intended as a scaffold for students still learning the borrowing algorithm. Un-crossing reverses both.

**Scales to:** any number of digits (1–4 digit numbers tested).

---

## Tool 2: Addition
*(not yet built — placeholder)*

Vertical addition layout with a carry row above the top number. Carry cells are single-digit, append to the carry row as the student works right-to-left.

---

## Tool 3: Multiplication
*(not yet built — placeholder)*

Multi-digit multiplication with partial products, laid out vertically.

---

## Tool 4: Division
*(not yet built — placeholder)*

Long division scaffold: divide → multiply → subtract → bring down, one step at a time.

---

## Tool 5: Fraction Addition & Subtraction
*(not yet built — placeholder)*

Add or subtract fractions and mixed numbers. Common denominator helper included.

---

## Tool 6: Place Value
*(not yet built — placeholder)*

The student types any number (including decimals). Each digit is rendered in a labeled place-value column (hundred-thousands → ones → tenths → hundredths → thousandths). Useful for extracting specific place values (e.g. "how many tenths are in 54.724?").

---

## Tool 7: Measurement Conversions

**File:** `tools/math/conversions.html`
**Reference:** Built 2026-08-13

*The student copies a measurement-conversion problem, identifies the relevant conversion fact, then works the operation, calculation, and final answer in separate checked steps.*

**Setup:** Inline problem builder: `How many [target unit] are in [number] [source unit]?`. Unit dropdowns contain the supported metric and standard length, weight, and capacity units. Invalid pairings across measurement families are flagged visually before the student proceeds.

**Conversion-table interaction:**
- Keep the conversion table hidden until the copied problem is complete and the two units belong to the same measurement family.
- Show full unit names rather than abbreviations.
- Conversion rows are tappable, but begin visually neutral: no unit color coding and no factor highlighting before the student attempts a choice.
- A correct tap must directly connect the two currently entered units.
- After an incorrect tap, highlight every conversion row containing either unit from the problem and color-code only those problem units within the highlighted rows. Keep conversion-table numbers visually plain to reduce unnecessary visual load.
- Keep the original problem editable after an incorrect tap so the student can recognize and enter an intermediate single-step conversion for a multi-step problem.
- Once a direct conversion is selected, hide the table and lock the copied problem.

**Worked scaffold:**
1. Show the selected conversion fact with source unit, target unit, and non-1 conversion factor visually distinguished. This is the first point at which the conversion factor needs emphasis.
2. Ask the student to choose `multiply` or `divide`; validate only after an explicit Check tap.
3. Reveal the numeric calculation sentence and collect the result with the work-input numpad; validate on Check.
4. Reveal the original problem and a final complete-sentence answer blank; validate on Check.

**Completion actions:** Keep all actions available after the final answer is validated:
- **Copy** copies the complete answer sentence and can be used repeatedly.
- **Use this answer for the next step** starts a new problem with the previous answer value and unit prefilled as the new starting quantity; both remain editable.
- **New problem** clears everything.

**Multi-step rule:** The tool never auto-chains compound conversions. The student explicitly chooses the intermediate unit and uses the completed value for the next step.

---

## Worksheet ↔ Tool Integration

Worksheet cards link to tools via a **Hint panel**:

```
[💡 Hint]  (tap to expand)
  ↓
  4⅛ + 5⅞  →  [Fraction Addition Tool ›]
  answer × 4  →  [Multiplication Tool ›]
```

The hint content is **authored per problem** when the worksheet is built — it is not auto-generated. Each step in the hint names the mathematical operation and links directly to the relevant tool file using a relative path (e.g. `../../tools/math/fraction-addition.html`).

Tool links open in a new tab (`target="_blank"`) so the student can return to the worksheet card after completing the computation.
