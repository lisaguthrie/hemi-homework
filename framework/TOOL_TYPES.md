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
**Status:** Built and active

*The student enters a top number and a bottom number, then solves the subtraction in a vertical format with a borrow row above the top digit line.*

**Setup:** Two number inputs (top and bottom) with validation to keep the problem solvable for the student. The tool uses a large, tap-first layout and keeps all work steps visible in one card.

**Borrow interaction:**
- Tap any top-row digit to cross it out and open a borrow box above that place.
- Tap the same digit again to clear the borrow and remove the borrow box.
- Borrow boxes use the multi-digit append numpad so students can enter values like 13 or 12 as they work.
- Answer cells use the single-digit replace numpad so a student can enter only one digit at a time.
- Optional borrowing helper mode can also cross out the digit to the right and create a corresponding borrow box as a visual scaffold.

**Scales to:** One- to four-digit subtraction problems, including cases that require regrouping.

---

## Tool 2: Multiplication

**File:** `tools/math/multiplication.html`
**Status:** Built and active

*The student enters two positive whole numbers or decimals, decomposes each factor into place-value parts, and fills a partial-product area model before checking the final product.*

**Setup:** Two decimal-capable inputs accept whole numbers or decimal forms such as `.2`, `0.2`, or `3.50`, and normalize equivalent values before building the model. Each factor is limited to six digits excluding the decimal point.

**Place-value decomposition:**
- Each factor is broken into its nonzero place-value pieces.
- Zero-valued pieces are omitted to keep the model compact.
- Decimal arithmetic is done with exact scaled-integer math instead of floating-point calculations.

**Area model interaction:**
- The student fills the row and column decomposition boxes across the top and left side of the grid.
- Each partial-product cell is entered separately and checked only after an explicit Check action.
- Correct and incorrect entries receive visual feedback without negative wording.
- When the decomposition and all partial products are correct, the tool locks the model and reveals the final addition step.
- Completed partial-product cells can be read aloud, and the tool can read all partial products in sequence.

**Final step:** The student adds the partial products and enters the final product. Successful completion reveals the full multiplication fact and a brief celebration.

**Scales to:** Whole numbers and decimals that still create a manageable area model, with zero pieces omitted to keep the layout readable.

---

## Tool 3: Division

**File:** `tools/math/division.html`
**Status:** Built and active

*The student sets up a division problem and works through a long-division board with quotient, multiplication, subtraction, and bring-down steps laid out in a scaffolded format.*

**Setup:** The tool accepts a dividend and divisor, then shows the full division expression in an organized work layout. It is designed to model the standard division algorithm rather than hide the process behind a single answer box.

**Working flow:**
- The student sees the dividend, divisor, and quotient in a visible long-division layout.
- Key helper steps are represented in a subtraction-oriented board so the student can track the repeated process of divide, multiply, subtract, and continue.
- The tool emphasizes the partial-product and subtraction relationships that make long division systematic and transparent.
- The student uses tap-first input controls and the visual board to work through the problem step by step instead of jumping straight to the final quotient.

**Scales to:** Multi-digit division problems that are appropriate for scaffolded long-division practice, with the display tuned for a tablet-friendly, one-handed interaction style.

---

## Tool 4: Powers of 10

**File:** `tools/math/powers-of-ten.html`
**Status:** Built and active

*The student chooses a number, an operation, and a power of 10, then watches the digit values shift across place-value columns to understand multiplication and division by 10, 100, and 1000.*

**Setup:** A compact equation builder lets the student enter a starting number and select whether the operation is multiply or divide, then choose the power of 10.

**Place-value shift interaction:**
- The tool displays the starting number in a place-value chart.
- Moving from one power to another is shown as a clear digit-shift pattern across the chart.
- A direction arrow and preview make the conceptual movement visible without requiring the student to infer it from symbols alone.
- The student can then enter the final answer and validate it in a focused check step.

**Scales to:** Whole numbers and decimal numbers where the place-value shift is easy to visualize and compare across columns.

---

## Tool 5: Place Value

**File:** `tools/math/place-value.html`
**Status:** Built and active

*The student types any number, including decimals, and matches each digit to the correct place-value column in a labeled chart.*

**Setup:** One number input generates a place-value grid with the relevant columns for the entered value.

**Chart interaction:**
- Digits appear in a place-value board with labeled columns such as thousand, hundred, tens, ones, tenths, hundredths, and thousandths.
- The student taps each digit box in the chart to place or confirm the correct value in the appropriate column.
- The tool validates the answer and gives clear visual feedback for correct or incorrect placement.
- The chart is designed to reduce cognitive load by showing only the columns needed for the current number.

**Scales to:** Whole numbers and decimals that fit comfortably into the tool’s chart while keeping the place-value structure easy to read.

---

## Tool 6: Measurement Conversions

**File:** `tools/math/conversions.html`
**Status:** Built and active

*The student copies a conversion problem, selects the right conversion fact, and works through choose-operation, calculation, and final-answer steps in separate validated stages.*

**Setup:** The problem builder creates a question such as “How many [target unit] are in [number] [source unit]?” and uses dropdowns for supported metric and customary length, weight, and capacity units. Invalid pairings are flagged before the student proceeds.

**Conversion-table interaction:**
- The conversion table stays hidden until the student has a valid pair of units for the same measurement family.
- The table uses full unit names and neutral styling until the student attempts a direct match.
- A correct tap must connect the two units in the copied problem.
- If the student taps incorrectly, the tool highlights only the relevant rows and units, keeping the extra visual noise low.
- The original problem remains editable after an incorrect attempt so the student can reason through an intermediate single-step conversion.

**Worked scaffold:**
1. Show the selected conversion fact with the source unit, target unit, and conversion factor clearly distinguished.
2. Ask the student to choose multiply or divide, then validate after an explicit Check tap.
3. Reveal the calculation sentence and collect the numeric answer with the work-input numpad.
4. Show the original problem and the final complete-sentence answer blank for a final check.

**Completion actions:** After a correct final answer, the student can copy the final sentence, use the answer as the starting value for a new problem, or start fresh with a new problem.

**Multi-step rule:** The tool does not auto-chain compound conversions; the student must explicitly choose the intermediate unit and carry forward the completed value in a separate step.

---

## Tool 7: Addition
*(not yet built — placeholder)*

Vertical addition with a carry row and step-by-step regrouping support.

---

## Tool 8: Fraction Addition & Subtraction
*(not yet built — placeholder)*

Fraction and mixed-number practice with a common-denominator helper and structured worked steps.

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
