# Design System

Default visual design for worksheet apps. Profiles may override any value — see `profiles/PROFILE_TEMPLATE.md`.

---

## Typography

- **Display / headers / question numbers:** Fredoka One (Google Fonts)
- **Body / UI / labels:** Nunito (Google Fonts)

```html
<link href="https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
```

Base font size: `1rem`. Floor for question text: `0.95rem`. Large-text profile override: `1.2rem` base.

---

## Color Tokens

```css
:root {
  --bg-start:          #e0f4ff;
  --bg-end:            #f0e8ff;
  --card-bg:           #ffffff;
  --text-primary:      #1a2a3a;
  --text-muted:        #6a8299;
  --accent-blue:       #3b9ede;
  --accent-blue-dk:    #1a6fa8;
  --phrase-bg:         #fff3c4;
  --phrase-border:     #e6c800;
  --phrase-text:       #5a3a00;
  --btn-play:          #5dca7e;
  --btn-play-dk:       #3aaa5a;
  --btn-mic:           #3b9ede;
  --feedback-ok-bg:    #d0f5e0;
  --feedback-ok-txt:   #1d7a40;
  --feedback-hint-bg:  #ffeedd;
  --feedback-hint-txt: #c05000;
  --pip-empty:         #dde0e8;
  --pip-done:          #5dca7e;
}
```

---

## Page

```css
body {
  font-family: 'Nunito', sans-serif;
  background: linear-gradient(160deg, var(--bg-start) 0%, var(--bg-end) 100%);
  min-height: 100vh;
  color: var(--text-primary);
  padding: 20px 16px 60px;
}
```

Max content width: `700px`, centered. Sections stack with `gap: 14px`.

---

## Cards

```css
.question-card {
  background: var(--card-bg);
  border-radius: 18px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.10);
  padding: 16px 18px;
  border: 2.5px solid transparent;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.question-card.correct {
  border-color: var(--btn-play);
  background: #f0fff5;
}
```

---

## Tappable Phrase Chips

For any content chunk that speaks itself (not the full sentence) when tapped.

```css
.phrase-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--phrase-bg);
  border: 2px solid var(--phrase-border);
  border-radius: 8px;
  padding: 2px 8px;
  min-height: 44px;
  cursor: pointer;
  font-weight: 700;
  color: var(--phrase-text);
  white-space: nowrap;
  user-select: none;
  transition: background 0.15s, transform 0.1s;
}
.phrase-chip:hover  { background: #ffe88a; }
.phrase-chip:active { transform: scale(0.95); }
```

Always prepend `🔊` inside the chip. Wire: `chip.onclick = (e) => { e.stopPropagation(); speak(phraseText); }`

Plain-text spans adjacent to chips are also tappable and speak the full sentence (current answer substituted if selected).

### Pronoun Highlight Chip (blue variant)

Used when a specific word in a sentence needs to be marked as "the target" for an interaction (e.g. the pronoun being labeled or identified), as distinct from a tappable noun phrase the student is replacing.

```css
.pronoun-chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  background: #e8f0ff;
  border: 2px solid #3b9ede;
  border-radius: 7px;
  padding: 1px 8px;
  font-weight: 800;
  color: #1a6fa8;
  white-space: nowrap;
  font-size: 0.93rem;
}
```

Use the yellow `.phrase-chip` when the chip is independently tappable and reads itself aloud. Use the blue `.pronoun-chip` when the chip is a visual marker only and the surrounding sentence element handles the tap-to-speak.

---

## Buttons

```css
/* Play button — per card, speaks full sentence on demand */
.play-btn {
  background: var(--btn-play);
  border: none;
  border-radius: 50%;
  width: 44px; height: 44px;
  font-size: 1.2rem;
  cursor: pointer;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(93,202,126,0.4);
  transition: background 0.15s;
}
.play-btn:hover   { background: var(--btn-play-dk); }
.play-btn.playing { background: #ff7eb3; animation: btn-pulse 0.7s infinite alternate; }

/* Mic button — speech-to-text */
.mic-btn {
  background: var(--btn-mic);
  border: none;
  border-radius: 50%;
  width: 44px; height: 44px;
  font-size: 1.2rem;
  color: white;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s;
}
.mic-btn.listening { background: #ff7eb3; animation: btn-pulse 0.7s infinite alternate; }
.mic-btn:disabled  { opacity: 0.4; cursor: default; }

@keyframes btn-pulse {
  from { transform: scale(1); }
  to   { transform: scale(1.12); }
}

/* Check button — per-card answer submission */
.check-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 16px;
  min-width: 170px;
  min-height: 44px;
  font-family: 'Nunito', sans-serif;
  font-size: 0.95rem;
  font-weight: 800;
  background: linear-gradient(180deg, #ffe89b 0%, #ffd866 100%);
  color: #5f4700;
  border: 2px solid #d9a800;
  border-radius: 12px;
  box-shadow: 0 3px 10px rgba(217,168,0,0.22);
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s, color 0.2s;
}
.check-btn:hover { background: linear-gradient(180deg, #ffd866 0%, #f5c400 100%); }
.check-btn.done {
  background: linear-gradient(180deg, #7be09a 0%, #5dca7e 100%);
  border-color: #3aaa5a;
  color: white;
}
```

**HTML convention:**
```html
<button class="check-btn" onclick="checkCard(i)">
  <span class="check-btn-icon">📝</span><span>Check answers</span>
</button>
```

- Always include visible text ("Check answers"), not just an icon or checkmark symbol.
- Transitions to green (`.done`) after a correct submission — keeps it visually distinct from unchecked state.
- Do not reuse the play button's green color here; use the gradient yellow → green pattern above.

```css

---

## Answer Controls

### Dropdown
```css
.answer-select {
  font-family: 'Nunito', sans-serif;
  font-size: 1rem; font-weight: 700;
  color: var(--accent-blue-dk);
  background: #e8f4ff;
  border: 2.5px solid var(--accent-blue);
  border-radius: 10px;
  padding: 6px 10px;
  min-width: 110px;
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s, background 0.2s;
}
.answer-select:focus { border-color: var(--accent-blue-dk); background: #d0eaff; }
```
First option always: `<option value="">— pick —</option>`

### Space Slot (Punctuation Builder)

Used in sentence-repair exercises where students tap between words to insert punctuation. Canonical sizing confirmed across Type 12 and derivatives.

```css
/* Space slot — tappable punctuation insert point */
.space-slot {
  min-width: 26px;
  min-height: 44px;
  padding: 0 4px;
  border-radius: 7px;
  border: 2px solid #d0deec;
  background: #f4f9ff;
  color: #1a6fa8;
  font-family: 'Nunito', sans-serif;
  font-size: 0.95rem;
  font-weight: 900;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: pre;
}
/* State variants — extend per exercise as needed */
.space-slot.slot-blank  { background: #f7fbff; color: transparent; }  /* no punctuation chosen */
.space-slot.slot-comma  { background: #fff3c4; color: #7a5b00; border-color: #e6c800; }
.space-slot.slot-colon  { background: #ffe4d9; color: #a2441a; border-color: #f08a5d; }
.space-slot.slot-period { background: #e8f5e9; color: #1b5e20; border-color: #66bb6a; }
.space-slot.slot-quote  { background: #ede7f6; color: #4a148c; border-color: #9c69d0; }
```

**Key sizing rule:** `min-width: 26px` — do not inflate to `44px`. The `min-height: 44px` satisfies the tap-target floor without making slots visually blocky. The `slot-blank` state uses `color: transparent` so the slot appears visually empty without collapsing its width.

### Free-text area
```css
.answer-textarea {
  font-family: 'Nunito', sans-serif;
  font-size: 1rem; font-weight: 600;
  color: var(--text-primary);
  background: #f8fbff;
  border: 2.5px solid var(--accent-blue);
  border-radius: 12px;
  padding: 10px 14px;
  width: 100%;
  min-height: 80px;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
}
.answer-textarea:focus { border-color: var(--accent-blue-dk); }
```

---

## Feedback Badge

```css
.feedback {
  display: none; align-items: center; gap: 5px;
  font-size: 0.9rem; font-weight: 700;
  padding: 4px 12px; border-radius: 20px; flex-shrink: 0;
}
.feedback.show    { display: flex; }
.feedback.correct { background: var(--feedback-ok-bg);   color: var(--feedback-ok-txt); }
.feedback.hint    { background: var(--feedback-hint-bg); color: var(--feedback-hint-txt); }
```

Correct: `✅` + short affirmation. Incorrect: `💡 Hint:` + specific concept name. Never "wrong" or "try again."

---

## Progress Pips

```css
.pip {
  display: inline-block; width: 18px; height: 18px;
  border-radius: 50%; background: var(--pip-empty);
  transition: background 0.3s;
}
.pip.done { background: var(--pip-done); }
```

Show `answered / total` as text. Do not show a score until all questions answered.

---

## Speaking Toast

Fixed bottom. **Tapping cancels speech.** `pointer-events: none` when hidden, `auto` when visible.

```css
.speaking-toast {
  position: fixed; bottom: 20px; left: 50%;
  transform: translateX(-50%) translateY(80px);
  background: var(--accent-blue-dk); color: white;
  font-family: 'Nunito', sans-serif; font-weight: 700; font-size: 1rem;
  padding: 10px 24px; border-radius: 30px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  transition: transform 0.3s ease, background 0.2s;
  z-index: 100; cursor: pointer; user-select: none;
  pointer-events: none;
}
.speaking-toast.visible {
  transform: translateX(-50%) translateY(0);
  pointer-events: auto;
}
.speaking-toast.visible:hover { background: #c0392b; }
.speaking-toast.visible:hover .toast-label::after { content: ' — tap to stop'; }
```

---

## Responsive

At `max-width: 480px`: card padding `12px`, font floor `0.95rem`, dropdown min-width `90px`. Never hide questions.