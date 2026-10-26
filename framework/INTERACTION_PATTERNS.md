# Interaction Patterns

Reusable JavaScript patterns for all worksheet apps. Each pattern is self-contained and can be copied directly into a generated HTML file.

---

## Speech Synthesis (TTS)

### Core `speak()` function

```javascript
function speak(text) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.rate  = 0.88;   // slightly slower than default; do not change without reason
  utter.pitch = 1.05;
  utter.onstart = showToast;
  utter.onend   = hideToast;
  utter.onerror = hideToast;
  window.speechSynthesis.speak(utter);
}

function showToast()   { document.getElementById('speakingToast').classList.add('visible'); }
function hideToast()   { document.getElementById('speakingToast').classList.remove('visible'); }
function cancelSpeak() { window.speechSynthesis.cancel(); hideToast(); }
```

### Speaking Toast

Fixed bottom indicator. **Tapping it cancels speech in progress.** Uses `pointer-events: none` when hidden so it never intercepts taps invisibly; switches to `pointer-events: auto` only when visible. Hover turns red and appends "— tap to stop" to make the affordance clear.

```html
<div class="speaking-toast" id="speakingToast" onclick="cancelSpeak()" title="Tap to stop">
  🔊 <span class="toast-label">Reading aloud…</span>
</div>
```

```css
.speaking-toast {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%) translateY(80px);
  background: #1a6fa8;
  color: white;
  font-family: 'Nunito', sans-serif;
  font-weight: 700;
  font-size: 1rem;
  padding: 10px 24px;
  border-radius: 30px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  transition: transform 0.3s ease, background 0.2s;
  z-index: 100;
  pointer-events: none;   /* never intercepts taps when hidden */
  cursor: pointer;
  user-select: none;
}
.speaking-toast.visible {
  transform: translateX(-50%) translateY(0);
  pointer-events: auto;   /* tappable only when shown */
}
.speaking-toast.visible:hover { background: #c0392b; }
.speaking-toast.visible:hover .toast-label::after { content: ' — tap to stop'; }
```

### Auto-read after answer selection

```javascript
// Inside any onchange / onclick answer handler:
if (val) setTimeout(() => speak(buildFullSentence(q, val)), 300);
```

The 300ms delay makes the read-back feel intentional rather than immediate/jarring.

**Do not auto-read when an answer is marked correct or when all gaps are filled.** The play button and tappable sentence segments already give on-demand access to the full sentence. Auto-reading on completion is disruptive and has been removed from worksheets where it was initially added. Only auto-read on an explicit selection change (i.e. the student just picked something), and only when the interaction model calls for it (see Play Button Gating below).

### Part-of-Sentence Tap-to-Speak

Used when a sentence is rendered in segments (e.g. `before` text + choice chip + `after` text). Each segment speaks **only its own text** on tap, rather than the full sentence. The full sentence is still accessible via the green ▶ play button.

```javascript
// Before-text span
sp.title = 'Tap to hear just this part';
sp.onclick = function() { speak(q.before.trim()); };

// After-text span
sp2.title = 'Tap to hear just this part';
sp2.onclick = function() { speak(q.after.trim()); };

// Choice chip speaks the options
chip.onclick = function(e) {
  e.stopPropagation();
  speak(q.choices[0] + ' or ' + q.choices[1] + '?');
};

// Play button reads the full sentence with current answer substituted
playBtn.onclick = function() { speak(buildSentence(q, userAnswers[i])); };
```

**When to use:** Any worksheet where a sentence contains an inline widget (dropdown, input) that breaks the sentence into segments. Prefer this over tapping-reads-full-sentence when the segments are long enough to be independently meaningful.

### Focus-Safe Rendering (typing and dictation)

For editable controls (`input`, `textarea`, `select`), do not trigger a full `render()` on every keystroke/change just to update progress text. Re-rendering replaces DOM nodes and can drop focus/caret, which breaks typing and speech-to-text.

Use this two-layer approach:

- **Primary:** update progress counters in place (DOM text update only)
- **Fallback:** if a full `render()` happens, capture and restore focused control + caret

```javascript
function captureFocusState() {
  const active = document.activeElement;
  if (!active || !active.id) return null;
  if (!['INPUT', 'TEXTAREA', 'SELECT'].includes(active.tagName)) return null;

  const state = { id: active.id };
  if (typeof active.selectionStart === 'number' && typeof active.selectionEnd === 'number') {
    state.selectionStart = active.selectionStart;
    state.selectionEnd = active.selectionEnd;
  }
  return state;
}

function restoreFocusState(state) {
  if (!state || !state.id) return;
  const next = document.getElementById(state.id);
  if (!next) return;

  try { next.focus({ preventScroll: true }); } catch (e) { next.focus(); }

  if (typeof state.selectionStart !== 'number' || typeof state.selectionEnd !== 'number') return;
  if (typeof next.setSelectionRange !== 'function') return;

  const len = typeof next.value === 'string' ? next.value.length : 0;
  const start = Math.max(0, Math.min(state.selectionStart, len));
  const end = Math.max(0, Math.min(state.selectionEnd, len));
  try { next.setSelectionRange(start, end); } catch (e) {}
}

function render() {
  const focusState = captureFocusState();
  // ...build HTML...
  app.innerHTML = html;
  wireDynamicControls();
  restoreFocusState(focusState);
}
```

Also update dynamic widgets directly where possible instead of re-rendering whole cards (for example, update a punctuation slot button label/class and the related "Built sentence" line in place).

### Inline Dropdown Tap Scope (Part-Only TTS)

When a sentence includes inline dropdowns, do not attach full-sentence read-aloud to the whole sentence container. Keep full-sentence TTS on the green play button only, and make each visible text segment speak only itself.

**Required behavior:**

- Tapping the green `▶` button reads the full sentence with current selections.
- Tapping any sentence text segment reads only that segment.
- Tapping the dropdown opens/changes the control and does not trigger container speech.
- If a segment is empty after splitting around a placeholder, render it but skip speech for that segment.

```javascript
// Sentence with one inline placeholder, e.g. "Sometimes ___ we take our cousins."
const prompt = document.createElement('div');
prompt.className = 'prompt inline-fill';

const parts = q.prompt.split('___');

const before = document.createElement('span');
before.className = 'inline-text part-tap';
before.textContent = parts[0] || '';
before.onclick = function (e) {
  e.stopPropagation();
  if ((parts[0] || '').trim()) speak((parts[0] || '').trim());
};

const sel = createSelect(q.options, state[i].phrase, onChange, '- phrase -');
sel.classList.add('inline-select');

const after = document.createElement('span');
after.className = 'inline-text part-tap';
after.textContent = parts[1] || '';
after.onclick = function (e) {
  e.stopPropagation();
  if ((parts[1] || '').trim()) speak((parts[1] || '').trim());
};

prompt.appendChild(before);
prompt.appendChild(sel);
prompt.appendChild(after);

// Keep full sentence on play button only
playBtn.onclick = function () { speak(buildFullSentence(q, state[i])); };
```

### Inline Dropdown Blank (Fill-in-the-blank default)

For fill-in-the-blank sentence stems, render the dropdown directly at the blank location instead of placing it in a separate row below.

```javascript
function renderInlineBlank(container, q, i) {
  // q.before + [dropdown] + q.after
  const before = document.createElement('span');
  before.className = 'readable-span';
  before.textContent = q.before;
  before.onclick = function() { speak(q.before.trim()); };

  const sel = document.createElement('select');
  sel.className = 'gap-select';
  const blank = document.createElement('option');
  blank.value = ''; blank.textContent = '— pick —';
  sel.appendChild(blank);
  q.options.forEach((opt) => {
    const o = document.createElement('option');
    o.value = opt; o.textContent = opt;
    sel.appendChild(o);
  });
  sel.value = answers[i] || '';
  sel.onchange = function() {
    answers[i] = sel.value;
    saveState();
    if (sel.value) setTimeout(() => speak(q.before + sel.value + q.after), 300);
    render();
  };

  const after = document.createElement('span');
  after.className = 'readable-span';
  after.textContent = q.after;
  after.onclick = function() { speak(q.after.trim()); };

  container.appendChild(before);
  container.appendChild(sel);
  container.appendChild(after);
}
```

Use a below-the-line dropdown row only when the user explicitly requests that layout.

### Export/Print Answer Emphasis (single vs double underline)

Use this when a worksheet has an Export/Print view and the printed output should visually preserve which selected words play different grammatical roles.

**Formatting rules:**

- If the directions state that a part of speech should be underlined, use **bold + single underline**.
- If the directions state that a part of speech should be circled, use **bold + double underline**.

```javascript
function escHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function singleUnderline(value) {
  return '<strong><span class="single-underline">' + escHtml(value) + '</span></strong>';
}

function doubleUnderline(value) {
  return '<strong><span class="double-underline">' + escHtml(value) + '</span></strong>';
}

function replaceFirstLiteral(source, needle, replacement) {
  if (!needle) return source;
  const idx = source.indexOf(needle);
  if (idx === -1) return source;
  return source.slice(0, idx) + replacement + source.slice(idx + needle.length);
}

/* Print CSS */
const printCss =
  '.single-underline{text-decoration-line:underline;text-decoration-thickness:2px}' +
  '.double-underline{text-decoration-line:underline;text-decoration-style:double;text-decoration-thickness:2px}';

/* Part B sentence example */
let sentenceHtml = escHtml(sentence);
sentenceHtml = replaceFirstLiteral(sentenceHtml, escHtml(selectedAdj), singleUnderline(selectedAdj));
sentenceHtml = replaceFirstLiteral(sentenceHtml, escHtml(selectedNoun), doubleUnderline(selectedNoun));

/* Part D answer line example */
const phraseHtml = selectedPhrase ? singleUnderline(selectedPhrase) : '___';
const prepHtml = selectedPrep ? doubleUnderline(selectedPrep) : '___';
```

Keep these markings in the print/export HTML only; on-screen worksheet controls keep the standard interactive styling.

### Print / Export — Phrase Replacement in the Completed Sentence

Use for Type 1 **Just the Right Word** exercises that export the original sentence (with the original bold paraphrase), a `Replacement:` answer line, and the sentence with the student's chosen replacement inserted. Keep those three lines, their wording, and their spacing unchanged. In the **completed sentence only**, make the saved replacement word **bold and single-underlined**. The surrounding sentence remains plain; the `Replacement:` line remains as originally styled. Do not format the whole sentence or underline a missing-word placeholder.

Always render the student's current chosen form, not the stored correct answer. Escape `q.before`, the chosen word, and `q.after` separately to maintain punctuation, spacing and safe HTML. An unanswered item keeps the same plain `_____` blank. This is an **export-only** display change and does not affect the interactive sentence, grading, or saved answers.

```javascript
// escHtml is the normal HTML-escaping helper; selectedWord comes from saved state.
function printCompletedReplacementSentence(q, selectedWord) {
  const middle = selectedWord
    ? '<strong class="print-b-replacement">' + escHtml(selectedWord) + '</strong>'
    : '_____';
  return '<p>' + escHtml(q.before) + middle + escHtml(q.after) + '</p>';
}
```

```css
.print-b-replacement {
  font-weight: 800;
  text-decoration-line: underline;
  text-decoration-thickness: 1.5px;
  text-underline-offset: 3px;
}
```

**Reference implementation:** `docs/worksheets/2026-10-19-wordly-wise-lesson-5b-just-the-right-word.html` (print view only).

---

### Print / Export — Applying Meanings In-Place Selection

Use for Wordly Wise **Applying Meanings** (Type 4), where each question has four lettered choices and the student may select any subset. Keep the wording and options exactly as printed, bold the source vocabulary word inside each question, and show **only the student's chosen answers** with **bold + underline** on their letter and phrase. Never include a separate `Selected:` line, grading badges, or answers inferred from the publisher key. Incomplete and incorrect student selections print exactly as chosen.

For the original two-column layout, keep choices in DOM/reading order `a, b, c, d`; use CSS grid column flow to show `a`/`b` down the left and `c`/`d` down the right. Use print-only classes; leave the on-screen accessibility controls unchanged. Match the **printed** vocabulary form through the word-family map (`evolved` for `evolve`, `inscription` for `inscribe`) rather than bolding a base word that does not occur in the source question.

```javascript
// escHtml() is the escaping helper documented earlier in this section.
// q: { question: string, vocab: string, choices: [string,string,string,string] }
// selected: student's selected letter IDs, e.g. ['a','d']; NOT q.answer.
function printApplyingMeaningsPrompt(q, vocabForms) {
  const forms = Object.keys(vocabForms).filter(form => vocabForms[form] === q.vocab)
    .sort((a,b) => b.length - a.length);
  for (const form of forms) {
    const safe = form.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const match = new RegExp('\\b' + safe + '\\b', 'i').exec(q.question);
    if (!match) continue;
    const start = match.index;
    return escHtml(q.question.slice(0,start)) +
      '<strong class="print-c-vocab">' + escHtml(match[0]) + '</strong>' +
      escHtml(q.question.slice(start + match[0].length));
  }
  return escHtml(q.question);
}

function printApplyingMeaningsChoices(q, selected) {
  const letters = ['a','b','c','d'];
  return '<div class="print-c-choices">' + q.choices.map((choice, index) => {
    const letter = letters[index];
    const text = '(' + letter + ') ' + escHtml(choice);
    return '<div class="print-c-choice">' +
      (selected.includes(letter) ? '<strong class="print-c-selected">' + text + '</strong>' : text) +
      '</div>';
  }).join('') + '</div>';
}
```

```css
.print-c-q { break-inside: avoid; margin: 13px 0; }
.print-c-prompt { margin: 0 0 3px; }
.print-c-vocab { font-weight: 800; }
.print-c-choices { display: grid; grid-template-columns: repeat(2,minmax(0,1fr));
  grid-template-rows: repeat(2,auto); grid-auto-flow: column;
  column-gap: 18px; row-gap: 1px; padding-left: 18px;
  font-size: 14px; line-height: 1.45; }
.print-c-selected { font-weight: 800; text-decoration: underline;
  text-decoration-thickness: 1.5px; text-underline-offset: 3px; }
```

**Reference:** `worksheets/christina/2026-10-19-wordly-wise-lesson-5c-applying-meanings.html` (print output only).

---

### Word Study — Checkbox Speaks / Word Opens Definition

For **Type 2 Word Study** (`synonyms` / `antonyms`), do not make the checkbox and word trigger the same speech behavior. A student can hear a printed word while committing to a selection, or examine the meaning independently without selecting it.

- **Checkbox** (44px minimum): toggle the saved selected pair and call `speak(word)` with **only the tapped word**, never a sentence or definition. Maintain the two-choice cap; when already at two, let another checkbox speak without selecting it rather than natively disabling speech access. Preserve the student's existing selections, three-check review state, and export behavior.
- **Word** (44px minimum): open the existing reusable source-labeled definition dialog for both lesson and nonlesson words. Do **not** call `speak(word)` automatically on that tap; the modal's green `▶` reads the definition and example on demand. The word tap must never select or deselect the checkbox.
- **Weekly packet word or listed related form:** use the packet's exact definition/example text, including multiple senses and source part of speech, and apply the yellow vocabulary button treatment from `framework/DESIGN_SYSTEM.md`. Check membership by exact headword/form lookup, not by substring matching or a potentially misleading partial stem.
- **Nonweekly word:** leave the word text plain. Look up a dictionary definition and example from a credible external source, preserving the meaning relevant to the printed exercise. Embed the entry in the worksheet's HTML for offline use; label and link the source in the modal. Do not invent outside source attributions or write a made-up dictionary quotation. Avoid overriding supplied packet content with external definitions.

```javascript
// Type 2 example; `state.answers[i].pair` is the student's selection indices.
const selected = state.answers[i].pair.includes(j);
const atLimit = state.answers[i].pair.length === 2 && !selected;
const box = document.createElement('button');
box.type = 'button'; box.textContent = selected ? '☑' : '☐';
box.setAttribute('aria-pressed', String(selected));
box.onclick = () => {
  speak(word);                       // exactly one word, even when an answer changes
  if (atLimit) return;              // listen only: do not add a third choice
  const pair = selected
    ? state.answers[i].pair.filter(index => index !== j)
    : [...state.answers[i].pair, j];
  setAnswer(i, { pair, relation: state.answers[i].relation });
};
const wordButton = document.createElement('button');
wordButton.type = 'button'; wordButton.textContent = word;
wordButton.className = 'word-definition' + (isLessonForm(word) ? ' lesson-vocab' : '');
wordButton.setAttribute('aria-haspopup', 'dialog');
wordButton.onclick = () => openDefinition(word); // sourced modal; no auto-speech
```

**Reference:** `worksheets/christina/2026-10-19-wordly-wise-lesson-5d-word-study-synonyms-antonyms.html`; packet Word List 5 plus separately sourced Cambridge Dictionary entries for nonlesson words.

---

### Print / Export — Four-Word Pair with S/A

Use for Wordly Wise mixed synonym/antonym exercises (Type 2). The export represents the student's markings **in place**, in the same compact row as the paper exercise, not in a new `Selected` or `Type` answer line. Preserve source word order and show `S` and `A` as separate printed choices. A wrong or incomplete student choice is still printed as selected; never replace it with the answer key.

**Layout:** item number + four evenly spaced words + a noticeable gap + `S` and `A` with modest separation, **all on one line**. Render the student's selected words and selected `S`/`A` as **bold and underlined**, while all other terms remain plain. This affects only the print/export document, not the accessible on-screen selection controls.

```javascript
// q.words: four strings in original order
// answer: { pair: [0, 2], relation: 'S' } — student's choices, NOT q.pair / q.relation answer key
function printWordRelationshipRow(q, answer, questionNumber) {
  const mark = (value, chosen) => chosen
    ? '<strong class="print-d-marked">' + escHtml(value) + '</strong>'
    : escHtml(value);
  return '<div class="print-d-row">' +
    '<span class="print-d-number">' + questionNumber + '.</span>' +
    '<span class="print-d-words">' + q.words.map((word, index) =>
      '<span class="print-d-word">' + mark(word, answer.pair.includes(index)) + '</span>'
    ).join('') + '</span>' +
    '<span class="print-d-sa"><span>' + mark('S', answer.relation === 'S') + '</span>' +
    '<span>' + mark('A', answer.relation === 'A') + '</span></span>' +
    '</div>';
}
```

```css
.print-d-row{display:flex;align-items:baseline;white-space:nowrap;font-size:14px;line-height:1.6}
.print-d-number{flex:0 0 30px;font-weight:bold}
.print-d-words{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));column-gap:8px;flex:1;min-width:0}
.print-d-word{white-space:nowrap}
.print-d-sa{display:flex;gap:20px;margin-left:28px;flex:0 0 auto;padding-right:10px}
.print-d-marked{font-weight:800;text-decoration-line:underline;text-decoration-thickness:1.5px;text-underline-offset:3px}
```

Place each row in a `break-inside: avoid` print section. Do not use an answer status or correctness color in the export. This is an **in-place marking** pattern: printed students' choices, including incomplete and incorrect choices, are authoritative for the markings.

**Reference implementation:** `worksheets/christina/2026-10-19-wordly-wise-lesson-5d-word-study-synonyms-antonyms.html`.

---

### Gap-Fill Tappable Segments (Type: `__` delimiter)

Used when a prompt is stored with `__` markers for inline gap dropdowns (e.g. dialogue punctuation worksheets). Split the prompt on `__` and render each text segment as a tappable span; each `__` position becomes a `<select>`.

```javascript
const GAP_OPTION_VALUES = [',', '.', '?', '!', '"'];

function renderGapLine(container, q, i) {
  const parts = q.prompt.split('__');

  function makeReadableSpan(text) {
    const trimmed = text.trim();
    if (!trimmed) return document.createTextNode(text);
    const span = document.createElement('span');
    span.className = 'readable-span';
    span.textContent = text;
    span.title = 'Tap to hear this part';
    span.onclick = function() { speak(trimmed); };
    return span;
  }

  for (let g = 0; g < parts.length - 1; g++) {
    container.appendChild(makeReadableSpan(parts[g]));
    const sel = document.createElement('select');
    sel.className = 'gap-select';
    // first option is blank — no default selected
    const blank = document.createElement('option');
    blank.value = ''; blank.textContent = '';
    sel.appendChild(blank);
    GAP_OPTION_VALUES.forEach((opt) => {
      const el = document.createElement('option');
      el.value = opt; el.textContent = opt;
      sel.appendChild(el);
    });
    sel.value = picks[g] || '';
    sel.onchange = function() { /* update state, save, checkAnswer */ };
    container.appendChild(sel);
  }
  container.appendChild(makeReadableSpan(parts[parts.length - 1]));
}
```

```css
.readable-span {
  cursor: pointer;
  border-radius: 4px;
  padding: 0 1px;
  transition: background 0.15s;
}
.readable-span:hover { background: #daeeff; }

.gap-select {
  min-height: 44px;
  min-width: 70px;
  max-width: 150px;
  font-family: 'Nunito', sans-serif;
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--accent-blue-dk);
  background: #e8f4ff;
  border: 2.5px solid var(--accent-blue);
  border-radius: 8px;
  padding: 4px 6px;
  margin: 0 2px;
  vertical-align: baseline;
  cursor: pointer;
  outline: none;
}
.gap-select:focus { border-color: var(--accent-blue-dk); background: #d5edff; }
```

**Option list convention:** Use a single fixed set `[',', '.', '?', '!', '"']` for all gaps so the student is never given implicit hints from differing option counts. Always blank first option — no default selected. Do not vary the list per question.

**Completeness check:** A gap-fill item is considered answered only when every `__` gap has a non-empty selection. The play button reads the line with current gap values substituted (empty gaps shown as `...`).

**Do not auto-read on completion.** See the note under Auto-read after answer selection above.

### Whitespace-Insensitive Validation (Punctuation Builders)

When punctuation is edited via tappable space slots (for example cycling `space -> . -> , -> "`), students may arrive at the same punctuation/capitalization result with different temporary spacing around symbols. In these cases, validate by comparing versions of both strings with whitespace removed.

```javascript
function normalizeNoWhitespace(text) {
  return text.replace(/\s+/g, '');
}

function checkAnswer(i) {
  const built = buildCurrentSentence(i);      // includes user punctuation and caps
  const target = questions[i].target;
  const pass = normalizeNoWhitespace(built) === normalizeNoWhitespace(target);
  // set feedback/card state
}
```

Use this only when spacing is not the learning objective. Keep exact character checks for punctuation and capitalization.

### Play Button Reads Target Model (Punctuation Builders)

For sentence-repair punctuation sections, the per-card play button should read the correct target sentence, not the currently assembled sentence. This gives a reliable audio model while the student edits.

```javascript
playBtn.title = 'Read target sentence';
playBtn.onclick = function() {
  speak(questions[i].target);
};
```

### Section-local Question Numbering (Multi-part Worksheets)

For worksheets split into labeled parts (for example Part A, Part B, Part C), question numbers should restart within each part instead of continuing globally.

Use a section counter in `render()` and pass the section-local number to card construction:

```javascript
let activeSection = '';
let sectionItemNumber = 0;

questions.forEach((q, i) => {
  if (q.section !== activeSection) {
    activeSection = q.section;
    sectionItemNumber = 0;
    // render section header
  }

  sectionItemNumber += 1;
  app.appendChild(buildCard(q, i, sectionItemNumber));
});

function buildCard(q, i, displayNumber) {
  // ...
  num.textContent = displayNumber + '.';
}
```

This keeps numbering aligned with workbook conventions (A: 1-4, B: 1-4, C: 1-4) and avoids cross-part counting drift.

### Play Button Gating (Type 6 / Binary Choice)

On worksheets where a sentence contains a pronoun-choice dropdown inline, the per-card ▶ play button **must be disabled until the student has made a selection**. Without this, the play button reveals the answer by reading a default value.

```javascript
// On card creation:
pb.disabled = true;
pb.style.opacity = '0.4';
pb.style.cursor = 'default';

// In the dropdown onchange handler:
if (!val) {
  pb.disabled = true; pb.style.opacity = '0.4'; pb.style.cursor = 'default';
} else {
  pb.disabled = false; pb.style.opacity = ''; pb.style.cursor = '';
  // Always read aloud — correct OR wrong selection
  setTimeout(() => speak(buildSentence(val)), 300);
}

// On state restore (page reload):
if (savedAnswer) {
  pb.disabled = false; pb.style.opacity = ''; pb.style.cursor = '';
}
```

**Always read aloud on selection, correct or wrong.** Hearing the wrong sentence read back helps the student self-correct by ear — do not gate read-aloud on correctness.

---

## Speech Recognition (STT) — Continuous Mode

Browser support: Chrome/Edge reliable on HTTPS or localhost. Safari works, may re-prompt for mic. Firefox unsupported — button disables gracefully. **Does not work on `file://` URLs in Chrome/Edge** (browser security restriction, not a code issue). On iOS, the OS dictation key on the keyboard is a zero-code fallback.

**Status:** Implemented but not yet fully validated across browsers. Known working context: Chrome/Edge on HTTPS or localhost.

```javascript
function initMic(btn, taEl, onResult) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    btn.disabled = true;
    btn.title = 'Speech input not available in this browser';
    btn.style.opacity = '0.4';
    return;
  }

  let rec = null;
  let listening = false;

  function startListening() {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    rec = new SR();
    rec.continuous = true;        // stay open until manually stopped
    rec.interimResults = false;
    rec.lang = 'en-US';

    rec.onstart = () => {
      listening = true;
      btn.textContent = '⏹';
      btn.classList.add('listening');
    };

    rec.onresult = (e) => {
      let transcript = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) transcript += e.results[i][0].transcript + ' ';
      }
      transcript = transcript.trim();
      if (transcript) {
        taEl.value += (taEl.value ? ' ' : '') + transcript;
        if (onResult) onResult(transcript);
      }
    };

    rec.onend = () => {
      if (listening) {
        // Browser ended session on its own — restart to keep it going
        try { rec.start(); return; } catch(err) {}
      }
      listening = false;
      btn.textContent = '🎤';
      btn.classList.remove('listening');
      rec = null;
    };

    rec.onerror = (e) => {
      if (e.error === 'no-speech') return; // ignore — onend handles restart
      listening = false;
      btn.textContent = '🎤';
      btn.classList.remove('listening');
      rec = null;
      if (e.error === 'not-allowed' || e.error === 'service-not-allowed') {
        btn.title = 'Microphone access was denied. Check browser permissions.';
        btn.style.opacity = '0.5';
      }
    };

    try {
      rec.start();
    } catch(err) {
      listening = false;
      btn.textContent = '🎤';
      btn.classList.remove('listening');
      rec = null;
    }
  }

  btn.onclick = (e) => {
    e.stopPropagation();
    if (listening) {
      // Manual stop — set flag BEFORE calling stop() so onend doesn't restart
      listening = false;
      if (rec) { try { rec.stop(); } catch(err) {} }
    } else {
      startListening();
    }
  };
}
```

**Key changes from previous pattern:**
- `continuous: true` keeps the session open across silences
- `onend` restarts the session if `listening` is still `true` (browser closed it on its own)
- Manual stop sets `listening = false` before `rec.stop()` so `onend` knows not to restart
- `no-speech` errors are silently ignored — `onend` handles the restart
- Fresh `SpeechRecognition` instance per session start (not reused)
- `e.stopPropagation()` on click prevents bubbling interference
- Cancels speech synthesis before starting mic

**Open issue (as of 2026-03-24):** Still not working reliably in Edge from local server — further investigation needed in a dedicated chat.

Always pair a free-text area with both a mic button (STT) and a read-back button that calls `speak(textarea.value)`.

---

## Answer Selection → Feedback

### Whole-Worksheet Three-Chance Review (Default)

**Use this instead of automatic feedback, per-card Check buttons, or unrestricted Check Answers** whenever a worksheet has a trustworthy fixed answer key. A worksheet file (or a single-file combined worksheet) has **three total check actions**. Place the check panel below the full question list and progress indicator, never inside a question card.

**User flow:** Students select all the responses they wish, without correctness feedback. On **Check all responses**, first count unanswered/incomplete items. If any exist, show an inline warning with their numbers, and two explicit choices: **Keep working** and **Check anyway · use 1 check**. The warning alone never spends a check. A completed submission validates immediately. Each confirmed check spends one chance and grades *every* problem at once, including blanks. Display three visually and verbally distinct states:

- **✅ Correct** — green border/badge for the full answer set.
- **💡 Needs another look** — orange border/badge for nonempty but incorrect responses. Give a concept clue without identifying which exact choice to select or deselect.
- **○ Unanswered** — neutral gray, preferably a dashed border, for blank/incomplete responses. Never report an unanswered problem as a wrong attempt.

For multi-select, require exact set equality rather than merely checking whether any chosen option is correct. Keep choice text/definition TTS independent of selection and feedback. Changing an answer removes stale checked feedback **for that card only** and shows a neutral “Changed since your last check” marker. No choice change, or reopening the page, ever grants more checks. After three checks, leave answers editable and printable but disable checking; a double-tap Clear all responses explicitly resets everything. If all cards match on an earlier check, disable checking as complete.

**Reference implementation:** `docs/worksheets/2026-10-13-wordly-wise-lesson-4b-making-connections.html` and `...-4c-determining-meanings.html`.

**Reusable state and check logic** (adapt `answers`, `isAnswered`, `isCorrect`, and UI functions to the worksheet type):

```javascript
const MAX_CHECKS = 3;
const review = {
  checksUsed: 0,
  statuses: questions.map(() => ''),  // '', 'correct', 'attention', 'unanswered'
  revised: questions.map(() => false)
};

function onAnswerChanged(i) {
  // First update the student's saved answer and the neutral answered progress.
  if (review.checksUsed > 0) {
    review.statuses[i] = ''; // Never leave an obsolete green/orange badge on an edited response.
    review.revised[i] = true;
  }
  hideIncompleteWarning();
  saveProgress();
  paintQuestionStatus(i);
}

function requestCheckAll() {
  if (review.checksUsed >= MAX_CHECKS || review.statuses.every(s => s === 'correct')) return;
  const missing = questions.map((_, i) => i).filter(i => !isAnswered(i));
  if (missing.length) {
    showIncompleteWarning(missing); // Show Keep working / Check anyway; do not spend a chance.
    return;
  }
  checkAllNow();
}

function checkAllNow() { // Only from Check all (fully answered) or Check anyway confirmation.
  if (review.checksUsed >= MAX_CHECKS) return;
  review.checksUsed++;
  review.statuses = questions.map((_, i) =>
    !isAnswered(i) ? 'unanswered' : isCorrect(i) ? 'correct' : 'attention'
  );
  review.revised.fill(false);
  hideIncompleteWarning();
  saveProgress();
  questions.forEach((_, i) => paintQuestionStatus(i));
  paintCheckPanel(); // Remaining count; disable when all correct or three checks used.
}
```

Make the footer warning and results accessible using `role="status"` / `aria-live="polite"`, at least 44px touch targets, and non-color labels as well as borders. For open responses without a dependable objective rubric/key, use an explicitly documented adult-review exception instead of pretending to grade. The book's teacher/publisher answer key is preferred over informal semantic guesses.

**Feedback badges never auto-speak.** Text appears immediately; a small 🔊 button lets her hear it on demand. Store feedback text in a module-level object keyed by element ID — **never pass dynamic text through `JSON.stringify()` into an inline `onclick` attribute**, as apostrophes and quotes will break HTML parsing.

```javascript
const feedbackTexts = {};

function showFeedback(fbId, pass, text) {
  feedbackTexts[fbId] = text;
  const el = document.getElementById(fbId);
  el.className = 'feedback show ' + (pass ? 'correct' : 'hint');
  el.innerHTML = (pass ? '✅ ' : '💡 Hint: ') + text +
    ` <button class="fb-play-btn" onclick="speak(feedbackTexts['${fbId}'])" title="Read aloud">🔊</button>`;
}
```

```css
.fb-play-btn {
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  padding: 0 2px;
  line-height: 1;
  flex-shrink: 0;
  opacity: 0.75;
  transition: opacity 0.15s, transform 0.1s;
}
.fb-play-btn:hover { opacity: 1; transform: scale(1.2); }
```

The generic immediate-feedback handler below is **legacy / explicit-override only**. For new fixed-answer worksheets, use the whole-worksheet three-chance review above; changing a choice must not reveal correctness. For explicitly requested immediate-feedback tasks, the handler remains available.

```javascript
// Generic dropdown handler
sel.onchange = () => {
  const val = sel.value;
  userAnswers[i] = val;
  saveProgress();
  updateProgress();
  if (val) setTimeout(() => speak(buildFullSentence(q, val)), 300);
  updateFeedback(i, val);
};

function updateFeedback(i, val) {
  const fbId = `fb-${i}`;
  const q    = questions[i];
  if (!val) {
    document.getElementById(fbId).className = 'feedback';
    return;
  }
  const correct = q.answers.map(a => a.toLowerCase()).includes(val.toLowerCase());
  const text    = correct ? 'Great!' : q.hint;
  showFeedback(fbId, correct, text);
  document.getElementById(`card-${i}`).classList.toggle('correct', correct);
}
```

### Publisher-Keyed Multi-Select Review (Vocabulary Applying Meanings)

Use this variation of **Whole-Worksheet Three-Chance Review** for Wordly Wise Applying Meanings and other questions that may have **one to four correct choices**. Keep letter-selection buttons independent of word/audio buttons. Obtain a matching publisher/teacher answer key and verify the exact student-book edition, exercise, question text, and option order before enabling scoring. A missing key in a student worksheet is not, by itself, a reason to skip a key lookup or default to adult review.

Store the verified key and a concept-specific, non-answer-revealing hint with each question:

```javascript
const questions = [
  {
    question: 'Which animals graze?',
    choices: ['crocodiles', 'sheep', 'horses', 'cats'],
    answer: ['b', 'c'], // from an edition-matched teacher/publisher key
    hint: 'Graze means to feed on growing grass.'
  }
];

function isAnswered(i) {
  return state.answers[i].length > 0; // never require an assumed number of picks
}

function isCorrect(i) {
  const selected = state.answers[i]; // e.g. ['c', 'b']
  const expected = questions[i].answer;
  return selected.length === expected.length &&
    new Set(selected).size === selected.length &&
    expected.every(letter => selected.includes(letter));
}
```

- Do not restrict selection to an assumed count; some questions correctly select all four choices.
- On **Check all responses**, evaluate each entire selected set, treating no picks as **Unanswered** and nonempty mismatches as **Needs another look**. An incorrect selection never gets positive feedback just because one option happens to match.
- Provide hints after checking, not when making or changing a selection. Hints name the vocabulary concept but do not enumerate the correct choices.
- Use the ordinary three-check warning/confirmation flow and `localStorage` review state. Preserve existing response state when enabling checking on a previously adult-reviewed worksheet; do not reset a student's selections merely because the scoring feature changed.

**Reference:** `docs/worksheets/2026-10-19-wordly-wise-lesson-5c-applying-meanings.html` (Wordly Wise Book 6, Lesson 5C, source-verified eight-item key).

### Legacy Deferred Answer Review (`Check Answers` Without Attempt Limit)

**Explicit override / maintenance only:** The three-chance whole-worksheet pattern above is the default for new worksheets. This older snippet does not enforce a review limit and must not be copied unchanged into a new build.

Use this pattern for fixed-answer dropdown sections when immediate correctness feedback causes the student to click through options without committing to a choice first. Instead of marking each answer on `change`, wait until the whole section is answered and require an explicit `Check Answers` tap.

**When to use:** Small grammar sections with one correct answer per item, especially two-choice verb-form or pronoun-choice drills where the student may otherwise trial-and-error through the dropdowns.

**Interaction decisions:**

- Dropdown `onchange` updates saved state and progress only; it does **not** show correctness or hints
- A section-level `Check Answers` button stays disabled until every item in the section has a non-empty answer
- Pressing `Check Answers` reveals correct / hint feedback for the whole section in one pass
- Any later answer change clears the reviewed state and hides stale feedback until `Check Answers` is pressed again
- Section completion / auto-collapse should key off both `all answered` and `checked + all correct`

```javascript
function resetReview() {
  state.checked = false;
  questions.forEach((_, i) => {
    const card = document.getElementById(`card-${i}`);
    const fb = document.getElementById(`fb-${i}`);
    if (card) card.classList.remove('correct');
    if (fb) fb.className = 'feedback';
  });
}

function checkAnswers() {
  const answered = userAnswers.filter(v => v !== '').length;
  if (answered !== questions.length) return;

  state.checked = true;
  questions.forEach((q, i) => {
    const val = userAnswers[i];
    const pass = q.answers.map(a => a.toLowerCase()).includes(val.toLowerCase());
    document.getElementById(`card-${i}`).classList.toggle('correct', pass);
    showFeedback(`fb-${i}`, pass, pass ? 'Great!' : q.hint);
  });
  saveState();
  updateProgress();
}

sel.onchange = () => {
  resetReview();
  userAnswers[i] = sel.value;
  saveState();
  updateProgress();
};

function updateProgress() {
  const answered = userAnswers.filter(v => v !== '').length;
  checkBtn.disabled = answered !== questions.length;
  const allCorrect = questions.every((q, i) =>
    q.answers.map(a => a.toLowerCase()).includes((userAnswers[i] || '').toLowerCase())
  );
  section.classList.toggle('complete', answered === questions.length && state.checked && allCorrect);
}
```

### Legacy Per-Card Deferred Feedback (Single Check Button)

**Explicit override / maintenance only:** Per-question checking is not the default; use three whole-worksheet chances unless otherwise specified.

Use this for card-based two-choice dropdown tasks where immediate hinting on selection causes guessing behavior. The card should show no hint/correct badge until its check button is tapped.

```javascript
// state per card: { pickA: '', pickB: '', checked: false, correct: false }

function onDropdownChange(i, key, val) {
  state[i][key] = val;
  state[i].checked = false;  // hide stale feedback after edits
  state[i].correct = false;
  saveState();
  render();
}

function checkCard(i) {
  state[i].checked = true;
  state[i].correct = (state[i].pickA === answerKey[i].a && state[i].pickB === answerKey[i].b);
  saveState();
  render();
}

// Render feedback only when checked === true
if (state[i].checked) showFeedback(...);
```

Do not show hint text merely because a dropdown has a value.

### Free-Text Validation With Multiple Accepted Targets

When multiple phrasings are instructionally equivalent (for example contractions vs expanded forms), define an accepted list and compare against all normalized targets.

```javascript
const q = {
  accepted: [
    'I told my friends, "I\'m glad you came."',
    'I told my friends, "I am glad you came."'
  ]
};

function normalizeFreeText(text) {
  return text
    .replace(/[“”]/g, '"')
    .replace(/[‘’]/g, "'")
    .replace(/\s+/g, ' ')
    .trim();
}

const got = normalizeFreeText(userText);
const pass = q.accepted
  .map(normalizeFreeText)
  .includes(got);
```

If this pattern is used, avoid rendering a visible target line below the input unless explicitly requested.

### Retry-Until-Correct Pattern (Explicit Override Only)

This unlimited-attempt behavior is superseded by the three-chance whole-worksheet default for new objectively checked worksheets. Use it only when specifically requested or required by a standalone tool.

For worksheet types where a correct answer requires multiple selections (e.g. word chip + mark type), do NOT finalize the card on a wrong attempt. Show feedback and keep all controls live:

```javascript
if (pass) {
  state.submitted[i] = true;
  saveState();
  // lock card, update progress, check phase complete
} else {
  showFeedback(fbId, false, hintText);
  card.classList.add('missed');
  const confirmBtn = document.getElementById(`confirm-${i}`);
  if (confirmBtn) confirmBtn.disabled = false;
  updateProgress(); // pips don't advance until submitted[i] is true
}
```

`updateProgress()` must key off `state.submitted[i]`, not off whether a decision has been made — in-progress wrong attempts should not prematurely advance the pip count.

**Already-found word guard:** When a sentence has multiple errors and the student re-taps a word they already found, give a gentle nudge rather than counting it as a new submission:
```javascript
if (state.foundErrors[i].includes(wi)) {
  showFeedback(`fb-${i}`, true, "You already found that one! Look for another error in this sentence.", false);
  return;
}
```

Do NOT block the visual `.selected` highlight from appearing on already-found words — removing that guard caused taps to appear to do nothing, making the interface feel broken.

### Inline Word Toggle + Compact Verify Button (Quote Scope)

Use this pattern when the student must mark a contiguous spoken quote inside a mixed sentence (spoken words + dialogue tag), without using a dropdown.

**When to use:** Dialogue/quotation exercises where the first step is identifying exactly which words were said, before punctuation is added.

**Interaction decisions:**

- Render the original sentence as regular inline text tokens (not chip bubbles)
- Each token is tappable and toggles selected state (for example, red + underline)
- Place a compact `✓` verify button to the right of the sentence row instead of a full-width action button
- Pressing `✓` validates the selected word indices against an answer-key index list
- On pass: convert the sentence display to the corrected version with quotation marks inserted automatically
- On fail: keep controls active, show a concept hint, and do not lock the card
- Keep the green per-card ▶ button; before pass it reads the original sentence, after pass it reads the corrected quoted sentence

```javascript
function checkQuoteScope(i) {
  const pass = arraysEqual(sorted(state.selectedWords[i]), answerKey[i].spokenWordIndexes);
  if (pass) {
    state.verified[i] = true;
    lineEl.textContent = answerKey[i].correctedSentence; // auto-insert quotes
    checkBtn.classList.add('done');
    showFeedback(`fb-${i}`, true, 'Great! You marked exactly what was said.');
  } else {
    state.verified[i] = false;
    checkBtn.classList.remove('done');
    showFeedback(`fb-${i}`, false, 'Underline only the exact spoken words, not the dialogue tag.');
  }
  saveState();
  updateProgress();
}
```

```css
.sentence-word.selected { color: #a91f1f; text-decoration: underline; }
.check-btn { width: 44px; height: 44px; border-radius: 10px; }
.check-btn.done { background: #5dca7e; border-color: #3aaa5a; color: #fff; }
```

### Sequential Multi-Target Tap Flow

Use this pattern when a sentence requires more than one correct tap before the answer control appears, for example: coordinated subjects in a subject-verb agreement sentence.

**Rule:** Do not advance to the next step after the first correct tap if the answer key contains multiple required targets for the current phase. Require every target in that phase before revealing the next phase.

**Typical phases:**

- Phase 1: tap all subject words
- Phase 2: tap the verb
- Phase 3: choose the classification answer (for example `S` or `P`)

**State shape:**

```javascript
{
  selectedSubjects: [],
  subjectFound: false,
  verbFound: false,
  sp: '',
  step: 0
}
```

`selectedSubjects` stores normalized word keys (`toLowerCase()`). `subjectFound` becomes `true` only when `selectedSubjects.length >= q.subject.length`.

```javascript
if (st.step === 0 && isSubject) {
  if (!st.selectedSubjects.includes(cleanLower)) {
    st.selectedSubjects.push(cleanLower);
  }

  (subjectSpanMap.get(cleanLower) || []).forEach(el => el.classList.add('subject-found'));
  st.subjectFound = st.selectedSubjects.length >= q.subject.length;

  stepHint.style.display = 'block';
  if (st.subjectFound) {
    st.step = 1;
    stepHint.textContent = '👆 Now tap the verb';
    speak(q.subject.length > 1
      ? 'You found both subjects. Now tap the verb.'
      : `${cleanLower} is the subject. Now tap the verb.`);
  } else {
    stepHint.textContent = '👆 Now tap the second subject';
    speak(`${cleanLower} is part of the subject. Now tap the second subject.`);
  }
}
```

**Interaction decisions:**

- Highlight each correctly tapped target immediately, even before the full phase is complete
- Change the step hint text to name the next missing target, not the final target
- Keep the answer control hidden until all required taps in the current phase are complete
- Re-tapping an already-found target should be harmless; speak the word if useful, but do not duplicate state
- Progress pips should advance only when the final answer for the item is submitted, not when an intermediate target is found

**Restore / migration rule:** If older saves only stored `subjectFound: true`, normalize them on load by backfilling `selectedSubjects` from the answer key before rebuilding the UI.

---

## Progress Tracking

```javascript
function updateProgress() {
  const done  = userAnswers.filter(a => a !== '' && a != null).length;
  const total = userAnswers.length;
  document.getElementById('progressPips').innerHTML =
    userAnswers.map(a => `<span class="pip ${a ? 'done' : ''}"></span>`).join('');
  document.getElementById('progressCount').textContent = `${done} / ${total} answered`;
}
```

---

## Collapsible Sections with Sticky Nav

For worksheets with multiple distinct exercise sections on one page (rather than splitting into separate files), use collapsible section cards with a sticky navigation bar.

**When to use:** When the user explicitly requests a single file for multiple short sections, or when sections are closely related and benefit from shared state/context.

**Sticky nav bar:**
```html
<nav class="section-nav" id="sectionNav">
  <button class="nav-btn active" onclick="scrollToSection('sec1')">🔍 1A: Find It</button>
  <button class="nav-btn" onclick="scrollToSection('sec2')">🔗 1B: Match It</button>
  <!-- ... -->
</nav>
```

```css
.section-nav {
  position: sticky; top: 0; z-index: 50;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(8px);
  border-bottom: 2px solid #e0eaf8;
  padding: 10px 12px;
  display: flex; gap: 8px; flex-wrap: wrap; justify-content: center;
}
.nav-btn {
  font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 0.82rem;
  padding: 7px 14px; border-radius: 22px;
  border: 2px solid #3b9ede; background: white; color: #1a6fa8;
  cursor: pointer; white-space: nowrap; min-height: 36px;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.nav-btn.active  { background: #3b9ede; color: white; }
.nav-btn.complete { border-color: #5dca7e; color: #1d7a40; }
.nav-btn.complete.active { background: #5dca7e; color: white; border-color: #5dca7e; }
```

**Section card collapse pattern:**
```javascript
function toggleSection(id) {
  document.getElementById(id).classList.toggle('collapsed');
  updateNavActive();
}
function scrollToSection(id) {
  const el = document.getElementById(id);
  el.classList.remove('collapsed');
  el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  updateNavActive();
}
// Auto-collapse completed sections after a short delay
function autoCollapseIfComplete(secId) {
  setTimeout(() => {
    document.getElementById(secId).classList.add('collapsed');
    updateNavActive();
  }, 1200);
}
```

**Section card HTML structure:**
```html
<div class="section-card" id="sec1">
  <div class="section-header" onclick="toggleSection('sec1')">
    <span class="section-title">🔍 Part A — Find the Pronoun</span>
    <span class="section-badge" id="sec1-badge">0 / 7</span>
    <span class="section-toggle">▼</span>  <!-- rotates -90deg when collapsed -->
  </div>
  <div class="section-body"><!-- content --></div>
</div>
```

**Completed section:** gains `.complete` class → green border, green badge background. Nav button also gains `.complete`.

---

## localStorage — Progress Persistence

Key format: `worksheet_{subject}_{YYYY_MM_DD}` — derive from worksheet metadata, not hardcoded.

```javascript
const STORAGE_KEY = `worksheet_${SUBJECT}_${DATE}`; // e.g. 'worksheet_pronouns_2026_03_10'

function saveProgress() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(userAnswers)); } catch(e) {}
}

function loadProgress() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : null;
  } catch(e) { return null; }
}

// On page init:
const saved = loadProgress();
if (saved && saved.length === questions.length) {
  saved.forEach((val, i) => {
    if (val) {
      userAnswers[i] = val;
      // re-populate UI control and feedback for question i
      const sel = document.getElementById(`sel-${i}`);
      if (sel) sel.value = val;
      updateFeedback(i, val);
    }
  });
  updateProgress();
}
```

---

## Destructive Actions

`confirm()` is silently blocked in `file://` contexts and some sandboxed browsers — it returns `false` without showing any dialog. **Never use it.** Use a double-tap inline confirmation instead:

```javascript
function clearAllResponses() {
  const btn = document.querySelector('.clear-btn');
  if (btn.dataset.confirming === 'true') {
    try { localStorage.removeItem(STORAGE_KEY); } catch(e) {}
    location.reload();
  } else {
    btn.dataset.confirming = 'true';
    btn.textContent = '⚠️ Tap again to confirm';
    btn.style.background = '#ffeedd';
    btn.style.color = '#c05000';
    btn.style.borderColor = '#c05000';
    setTimeout(() => {
      if (btn.dataset.confirming === 'true') {
        btn.dataset.confirming = 'false';
        btn.textContent = '🗑️ Clear all responses';
        btn.style.background = '';
        btn.style.color = '';
        btn.style.borderColor = '';
      }
    }, 3000);
  }
}
```

First tap relabels to "⚠️ Tap again to confirm" with a 3-second revert timeout. Second tap within that window executes the action.

---

## Clear All Responses Button

Every worksheet page should include a "Clear all responses" button below the progress bar. It resets all answers, clears localStorage, and restores all UI elements to their initial state. **Use the double-tap confirmation pattern from the Destructive Actions section — never `confirm()`.**

**Placement:** Centered `div` immediately after the progress bar, before the closing `</div>` of the main container.

```html
<div style="text-align:center">
  <button class="clear-btn" onclick="clearAllResponses()">🗑️ Clear all responses</button>
</div>
```

```css
.clear-btn {
  background: #f0f0f0;
  color: #888;
  border: 2px solid #ccc;
  border-radius: 18px;
  padding: 7px 18px;
  font-family: 'Nunito', sans-serif;
  font-weight: 700;
  font-size: 0.88rem;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.clear-btn:hover { background: #ffeedd; color: #c05000; border-color: #c05000; }
```

**JS pattern for Type 1 / Type 4 (flat `userAnswers` array):**
```javascript
function clearAllResponses() {
  const btn = document.querySelector('.clear-btn');
  if (btn.dataset.confirming === 'true') {
    userAnswers.fill('');
    try { localStorage.removeItem(STORAGE_KEY); } catch(e) {}
    questions.forEach((q, i) => {
      const sel = document.getElementById('sel-' + i);
      if (sel) sel.value = '';
      const fb = document.getElementById('fb-' + i);
      if (fb) fb.className = 'feedback';
      const card = document.getElementById('card-' + i);
      if (card) card.classList.remove('correct');
    });
    updateProgress();
    btn.dataset.confirming = 'false';
    btn.textContent = '🗑️ Clear all responses';
    btn.style.background = '';
    btn.style.color = '';
    btn.style.borderColor = '';
  } else {
    btn.dataset.confirming = 'true';
    btn.textContent = '⚠️ Tap again to confirm';
    btn.style.background = '#ffeedd';
    btn.style.color = '#c05000';
    btn.style.borderColor = '#c05000';
    setTimeout(() => {
      if (btn.dataset.confirming === 'true') {
        btn.dataset.confirming = 'false';
        btn.textContent = '🗑️ Clear all responses';
        btn.style.background = '';
        btn.style.color = '';
        btn.style.borderColor = '';
      }
    }, 3000);
  }
}
```

**JS pattern for Type 5 (nested `userAnswers`, click-to-identify):**
```javascript
function clearAllResponses() {
  const btn = document.querySelector('.clear-btn');
  if (btn.dataset.confirming === 'true') {
    questions.forEach((q, qi) => { userAnswers[qi] = q.pronouns.map(() => ''); });
    try { localStorage.removeItem(STORAGE_KEY); } catch(e) {}
    questions.forEach((q, qi) => {
      const card = document.getElementById('card-' + qi);
      if (!card) return;
      card.querySelectorAll('.word-token').forEach(span => {
        span.classList.remove('pronoun-found', 'answered');
      });
      const area = document.getElementById('pronouns-area-' + qi);
      if (area) area.innerHTML = '';
      card.classList.remove('all-correct');
    });
    updateProgress();
    btn.dataset.confirming = 'false';
    btn.textContent = '🗑️ Clear all responses';
    btn.style.background = '';
    btn.style.color = '';
    btn.style.borderColor = '';
  } else {
    btn.dataset.confirming = 'true';
    btn.textContent = '⚠️ Tap again to confirm';
    btn.style.background = '#ffeedd';
    btn.style.color = '#c05000';
    btn.style.borderColor = '#c05000';
    setTimeout(() => {
      if (btn.dataset.confirming === 'true') {
        btn.dataset.confirming = 'false';
        btn.textContent = '🗑️ Clear all responses';
        btn.style.background = '';
        btn.style.color = '';
        btn.style.borderColor = '';
      }
    }, 3000);
  }
}
```

**Note:** If the page includes a bonus free-text area, also clear it:
```javascript
const ta = document.getElementById('bonusTextarea');
if (ta) ta.value = '';
```

---

## Page Layout Template

Standard section order for every worksheet:

```html
<!-- 1. Header -->
<header>
  <h1><!-- worksheet title --></h1>
  <p class="subtitle">Tap any highlighted phrase to hear it read aloud!</p>
</header>

<!-- 2. Concept box (tappable, yellow) — if worksheet has a definition/reteaching box -->
<div class="concept-box" onclick="speak('...')">🔊 ...</div>

<!-- 3. Instructions (tappable, blue) -->
<div class="instructions" onclick="speak('...')">🔊 ...</div>

<!-- 4. Question cards -->
<div class="questions-list" id="questionsList"></div>

<!-- 5. Progress -->
<div class="progress-bar">
  <span id="progressPips"></span>
  <span id="progressCount"></span>
</div>

<!-- 6. Clear + Export buttons (both required on every worksheet) -->
<div style="text-align:center">
  <button class="clear-btn" onclick="clearAllResponses()">🗑️ Clear all responses</button>
  &nbsp;
  <button class="export-btn" onclick="exportPrint()">🖨️ Export / Print</button>
</div>

<!-- 7. Bonus / extension activity — if present on original worksheet -->
<div class="bonus-section">...</div>

<!-- 8. Speaking toast (always last, fixed position) -->
<div class="speaking-toast" id="speakingToast" onclick="cancelSpeak()" title="Tap to stop">
  🔊 <span class="toast-label">Reading aloud…</span>
</div>
```

---

## Export / Print

When a worksheet has a printable export button, generate a print-ready HTML page and open it using a **Blob URL** — never `window.open('', '_blank')`, which returns `null` when running from a local file and popup blockers are active.

```javascript
function exportPrint() {
  const html = `<!DOCTYPE html>...[print HTML]...`;
  const blob = new Blob([html], { type: 'text/html' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.target   = '_blank';
  a.rel      = 'noopener';
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 10000);
}
```

The print HTML should: reproduce the original worksheet layout (problem text, clues, any work including guess tables), include `@media print { button { display: none } }`, provide an explicit Print button for non-Ctrl+P users, pre-fill the student's name on the name line **if the original has one**, and include a footer with source attribution if known. **Preserve only the source worksheet's header fields**: add a `Date:` line only when one exists on the original worksheet; never generate an extra date line or auto-fill today's date just because an export is being created. Use `align-items: flex-end` for retained header fields so label text aligns to any underline.

**Type-specific print styling override (Type 7 Proofreading):**
- Do not default to plain black-and-white score tables for proofreading/error-correction worksheets.
- Export should visually mirror handwritten teacher markup in a typewritten way: marked words inline, proofreading symbols visible, and per-sentence correction notes shown as margin callouts.
- Keep color in print for annotation meaning (for example, warm marker highlight plus red/orange outlines) when the worksheet relies on those distinctions.
- Include the corrected/annotated passage and comprehension answers; avoid replacing this with a sentence-status-only report.

```css
/* Source-matched header — name, with date only when the original includes one */
.name-line { display: flex; gap: 20px; margin: 12px 0 18px; font-size: 0.95rem; }
.name-line span { display: flex; align-items: flex-end; gap: 6px; }  /* flex-end keeps label at baseline */
.name-line .line { display: inline-block; width: 180px; border-bottom: 1.5px solid #333; }
```

```css
/* Export / Print button */
.export-btn {
  background: #7c5cbf;
  color: white;
  border: none;
  border-radius: 18px;
  padding: 9px 22px;
  font-family: 'Nunito', sans-serif;
  font-weight: 700;
  font-size: 0.92rem;
  cursor: pointer;
  transition: background 0.15s;
  box-shadow: 0 2px 8px rgba(124,92,191,0.25);
}
.export-btn:hover { background: #5a3fa0; }
```

---

## Vocabulary Word Bank + Definition Modal

Use this pattern for vocabulary curricula such as Wordly Wise when a worksheet depends on a lesson word bank and the student needs source definitions without leaving the exercise.

### Data shape

```javascript
const wordEntries = [
  {
    word: 'campaign',
    paragraphs: [
      {
        label: 'campaign · noun · 1',
        text: 'A series of actions intended to accomplish a goal. [Source example sentence.]'
      },
      {
        label: 'campaign · verb',
        text: 'To take part in actions planned to accomplish a particular goal. [Source example sentence.]'
      }
    ]
  }
];
```

### Interaction rules

- Keep the visible word bank separate from answer controls.
- For long card-based vocabulary exercises where the student repeatedly refers back to the word list, keep the bank visible with the reusable sticky-bank component from `framework/DESIGN_SYSTEM.md`. **Exception:** Type 6 reading-plus-writing uses the collapsed-by-default disclosure component below to keep the right pane focused on answers.
- Use a compact responsive grid so the persistent reference does not consume excessive vertical space: default to five columns on wider layouts and three columns on narrower/tablet layouts, while preserving the 44px tap-target floor where practical.
- Keep the bank label task-focused and minimal. Use wording such as `Word List 3 · tap a word for its definition`. Do **not** add explanatory copy such as “stays here while you scroll”; the sticky behavior should explain itself without adding reading load.
- Each bank word is a minimum-44px button that opens the definition modal.
- Opening a definition never changes an exercise answer.
- The modal title is the base word and may include a `🔊 Word` button that speaks only the headword.
- Preserve the source's multiple senses and related forms as distinct paragraphs.
- Each paragraph gets its own `▶ Read this paragraph` button. The spoken string should include the paragraph label/headword, part of speech, definition, and example sentence.
- Definitions are source transcription, not a simplification task. Do not silently rewrite the wording or replace the source's examples.
- Leave unrelated discussion/partner prompts out of the modal unless the user asks for them.
- Provide a 44px close button; allow Escape and backdrop-tap to close.
- Cancel ongoing speech when opening another modal or definition so clips do not overlap.

### Collapsible Reading-Pane Word Bank

For two-pane `Vocabulary in Context` worksheets, place the lesson word bank in a native `<details>` element **without** the `open` attribute. The right pane shows only the `Show / hide Word List` summary until the student expands it. Use the same word button and source-definition modal as the expanded bank on other worksheet types.

- Toggling the bank must not alter selections, answers, progress, or scroll position in the passage pane.
- Vocabulary words in the passage and the questions continue to open their definitions when the bank is collapsed.
- On reopening, default to collapsed rather than restoring a full expanded bank into the constrained right pane.

### Unique Vocabulary-Family Allocation — Optional Independent Word

When a Wordly Wise comprehension question **does not already contain** a lesson vocabulary word, show an unused-word dropdown immediately above the free-text response. Track named selections by **word family** rather than by inflected form. A word family selected for one question is absent from other questions' suggested choices; do not auto-insert or grammar-rewrite the written response.

Always append a final menu item labeled **`Choose a different word…`**. It is a reminder that the student can use another lesson word if none of the suggestions appeal. Treat it as a sentinel, not a vocabulary family:

```javascript
const INDEPENDENT_WORD = '__different__';
select.add(new Option('Choose a different word…', INDEPENDENT_WORD));
// Do not auto-fill an answer or claim a particular family was used.
```

- The student still writes a complete sentence in the normal focus-safe textarea and may choose a related form.
- A named selected family is unavailable in other dropdowns. The independent option remains selectable everywhere and makes no guesses about the student's choice.
- A nonempty response plus either an assigned family or the sentinel counts as *response-complete*, not correct; adult review checks the word is actually used and the printed “use each word only once” requirement is honored.
- Save the choice and text separately; when exporting, label the sentinel `Chosen in written response` rather than printing it as though it were a vocabulary word.

**Reference implementation:** `worksheets/christina/2026-10-19-wordly-wise-lesson-5e-vocabulary-in-context.html`.

### Part-of-Speech tags in vocabulary banks

Use the canonical POS colors from `framework/DESIGN_SYSTEM.md`.

- Parse each source label into exact headword/form, part of speech, and optional sense number.
- In the word bank, show abbreviated tags (`n`, `v`, `adj`, `adv`) for all unique parts of speech represented in the entry.
- In each definition card, show the exact source headword/form plus its matching POS tag.
- Color is not the only cue; keep the abbreviation visible.
- TTS still speaks full POS words using the spoken-punctuation rule below; do not read the abbreviations aloud.

### Definition / Example separation and spoken punctuation

Source entries often store a definition and its example sentence in one string. When the source format reliably places the example after the first complete definition sentence, split the string for presentation so the student can immediately tell which text is the definition and which is the example.

```javascript
function splitDefinitionAndExample(text) {
  const match = String(text).match(/^(.+?\.)(?:\s+)(.+)$/);
  if (!match) return { definition: text, example: '' };
  return { definition: match[1], example: match[2] };
}
```

The visual card should show:

```
[ ▶ ]  ceremony · noun
       Definition   A formal event held in honor of a special occasion.
       Example      The bride and groom exchanged rings during the wedding ceremony.
```

For speech synthesis, do **not** send a typographic separator such as `·` directly between the headword and part of speech. Some voices run the words together. Convert the label to spoken sentence boundaries so `ceremony · noun` is spoken as **"ceremony. noun."** Likewise, explicitly say "Definition" and "Example" before those parts.

```javascript
function buildDefinitionSpeech(label, definition, example) {
  const spokenLabel = label
    .split('·')
    .map(part => part.trim())
    .filter(Boolean)
    .join('. ') + '.';

  return spokenLabel +
    ' Definition: ' + definition +
    (example ? ' Example: ' + example : '');
}

// Compact icon-only button at the far left of the whole card:
readButton.textContent = '▶';
readButton.className = 'definition-read-btn';
readButton.setAttribute('aria-label', 'Read definition and example aloud');
readButton.onclick = () => {
  const parts = splitDefinitionAndExample(paragraph.text);
  speak(buildDefinitionSpeech(paragraph.label, parts.definition, parts.example));
};
```

Keep the source wording unchanged; this pattern changes only presentation and speech punctuation.

### Part-of-Speech Filter Scaffold

Use this as an optional, student-requested scaffold on vocabulary phrase-replacement cards.

- Put an icon-only `💡` button directly below the play button with `aria-label="Show part-of-speech hint"`.
- Before activation, show the normal full candidate list.
- On activation, identify the required POS from the source-supported correct replacement form, recolor the phrase slot, and filter the picker to displayed forms with that POS.
- The scaffold must not select an answer, reveal correctness, show a score, or trigger correctness feedback.
- Persist `hinted: true` and preserve it when the student changes an answer; normalize older saved state that lacks the field.

```javascript
// state per card
{ selected: '', hinted: false }

function showPosHint(i){
  state.items[i].hinted=true;
  save();
  renderCard(i);
}
```

If filtering leaves one candidate, that is acceptable when POS filtering is intentionally used as a strong scaffold.

### Minimal wiring

```javascript
function openDefinition(word) {
  const entry = wordEntries.find(e => e.word === word);
  if (!entry) return;

  title.textContent = entry.word;
  body.innerHTML = '';

  entry.paragraphs.forEach(p => {
    const box = document.createElement('div');
    const text = document.createElement('div');
    text.textContent = p.label + '. ' + p.text;

    const play = document.createElement('button');
    play.textContent = '▶ Read this paragraph';
    play.onclick = () => speak(p.label + '. ' + p.text);

    box.append(text, play);
    body.appendChild(box);
  });

  showModal();
}
```

**Trigger:** Confirmed in the first 2026–27 Wordly Wise “Just the Right Word” build, where definitions had to remain available as an accessibility support while the full vocabulary-selection task stayed intact.


### Plain-Prose Word Tap-to-Speak

Use this when every word in a sentence must be independently tappable for TTS but the sentence should still look like ordinary continuous text.

- Render each word as an unstyled inline `span` (or equivalent), not as a visible button/chip.
- Preserve normal prose appearance: transparent background, no border, no rounded box, inherited font/weight, and natural spacing.
- Keep keyboard access with `role="button"`, `tabindex="0"`, and Enter/Space activation.
- A focus-visible outline may appear for keyboard users, but no persistent visual affordance is required on every word.
- This is an explicit exception to the general “tappable content must be visually distinct” rule because marking every word would destroy readable continuous prose. The surrounding exercise already provides visible affordances for the actual answer interaction.

```javascript
function addReadableWords(container, text) {
  text.trim().split(/\\s+/).filter(Boolean).forEach(token => {
    const span = document.createElement('span');
    span.className = 'plain-word-tap';
    span.textContent = token;
    span.setAttribute('role', 'button');
    span.tabIndex = 0;
    span.onclick = (e) => { e.stopPropagation(); speak(cleanWord(token)); };
    span.onkeydown = (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        e.stopPropagation();
        speak(cleanWord(token));
      }
    };
    container.appendChild(span);
  });
}
```

*Trigger:* Confirmed while refining the first active Wordly Wise Type 1 worksheet; visible per-word button styling made sentences look fragmented and impaired normal reading.
