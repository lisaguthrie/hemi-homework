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

For simple fill-in-the-blank worksheets with a fixed answer key, the generic handler below is sufficient. For more complex worksheets (e.g. Type 3 Guess and Check), use `showFeedback()` directly.

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

### Deferred Answer Review (`Check Answers`)

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

### Retry-Until-Correct Pattern

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

The print HTML should: reproduce the original worksheet layout (problem text, clues, any work including guess tables), include `@media print { button { display: none } }`, provide an explicit Print button for non-Ctrl+P users, pre-fill the student's name on the name line, and include a footer with source attribution if known. Name/date header lines must use `align-items: flex-end` on their flex container so label text sits at the baseline of the underline, not floating in the middle.

**Type-specific print styling override (Type 7 Proofreading):**
- Do not default to plain black-and-white score tables for proofreading/error-correction worksheets.
- Export should visually mirror handwritten teacher markup in a typewritten way: marked words inline, proofreading symbols visible, and per-sentence correction notes shown as margin callouts.
- Keep color in print for annotation meaning (for example, warm marker highlight plus red/orange outlines) when the worksheet relies on those distinctions.
- Include the corrected/annotated passage and comprehension answers; avoid replacing this with a sentence-status-only report.

```css
/* Name/date header — used in every print page */
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