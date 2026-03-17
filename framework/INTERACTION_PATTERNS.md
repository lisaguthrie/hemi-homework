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

---

## Speech Recognition (STT)

Browser support: Chrome/Edge reliable. Safari works, may re-prompt for mic. Firefox unsupported — button disables gracefully. On iOS, the OS dictation key on the keyboard is a zero-code fallback.

```javascript
function initSpeechInput(textareaEl, micBtnEl) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    micBtnEl.disabled = true;
    micBtnEl.title = 'Speech input not available in this browser';
    return;
  }
  const rec = new SR();
  rec.continuous     = false;
  rec.interimResults = false;
  rec.lang           = 'en-US';
  let listening = false;

  micBtnEl.onclick = () => {
    if (listening) { rec.stop(); return; }
    rec.start();
  };
  rec.onstart  = () => { listening = true;  micBtnEl.textContent = '⏹'; micBtnEl.classList.add('listening'); };
  rec.onresult = (e) => {
    const t = e.results[0][0].transcript;
    textareaEl.value += (textareaEl.value ? ' ' : '') + t;
  };
  rec.onend    = () => { listening = false; micBtnEl.textContent = '🎤'; micBtnEl.classList.remove('listening'); };
  rec.onerror  = (e) => { console.warn('STT error:', e.error); rec.onend(); };
}
```

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

<!-- 6. Bonus / extension activity — if present on original worksheet -->
<div class="bonus-section">...</div>

<!-- 7. Speaking toast (always last, fixed position) -->
<div class="speaking-toast" id="speakingToast" onclick="cancelSpeak()" title="Tap to stop">
  🔊 <span class="toast-label">Reading aloud…</span>
</div>
```

---

## Export / Print

When a worksheet has a printable export button, generate a clean black-and-white print-ready HTML page and open it using a **Blob URL** — never `window.open('', '_blank')`, which returns `null` when running from a local file and popup blockers are active.

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

The print HTML should: reproduce the original worksheet layout (problem text, clues, any work including guess tables), include `@media print { button { display: none } }`, provide an explicit Print button for non-Ctrl+P users, pre-fill the student's name on the name line, and include a footer with source attribution if known.