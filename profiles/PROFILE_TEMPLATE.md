# Child Profile — [Name]

*Copy this file to `profiles/{name}/PROFILE.md` and fill it in. Delete sections that don't apply. The model reads this alongside the framework files to customize every worksheet app for this child.*

---

## About This Child

**Age / grade:** 
**Primary diagnosis or situation:** 
**Cognitive level:** e.g., "at grade level," "2 years below grade level in reading"

---

## Barriers to Learning (in order of impact)

List the specific barriers this child faces, most impactful first. Be concrete — the model uses this to decide which accessibility features to prioritize.

1. 
2. 
3. 

*Example: "1. Decoding and encoding written text. 2. Fine motor control. 3. Expressive language."*

---

## What Works

Specific approaches, interactions, or features that have proven effective for this child.

- 
- 

*Examples:*
- *"Tap-to-speak on individual phrases — she uses it constantly and it visibly reduces frustration"*
- *"Auto-read of full sentence after answer selection — helps her self-correct without adult intervention"*
- *"Dropdown selectors instead of writing — eliminates the fine motor barrier completely for most question types"*

---

## What Doesn't Work

Approaches that have been tried and found ineffective or counterproductive.

- 

*Examples:*
- *"Long instruction text — she skips it; keep all instructions tappable and very short"*
- *"Animations during answer selection — distracting, not motivating"*

---

## Emotional / Motivational Notes

How does this child respond to feedback? Any sensitivities around error states?

*Example: "Responds well to positive signals. Error states should never use 'wrong' — use hints that name the concept instead. Keep the emotional register calm and encouraging."*

---

## Design Overrides

Override any value from `framework/DESIGN_SYSTEM.md` here. Only list values that differ from the defaults.

```css
/* Example overrides — uncomment and adjust as needed */

/* :root {
  --bg-start:    #f0fff0;   /* different background color */
  --bg-end:      #fffde0;
  --phrase-bg:   #ffe0f0;   /* different phrase chip color */
  --phrase-border: #ff99cc;
} */

/* body { font-size: 1.2rem; }  /* large text mode */
```

---

## Speech Settings

Override TTS parameters if the defaults (rate 0.88, pitch 1.05) don't work well for this child.

```javascript
// utter.rate  = 0.88;   // 0.5 (very slow) to 1.5 (fast)
// utter.pitch = 1.05;   // 0.5 (low) to 2.0 (high)
```

---

## Free-Text Input

Is free-text input used for this child? If so, note any preferences.

- [ ] Use speech-to-text mic button alongside text areas
- [ ] Read-back button to hear what was typed/dictated
- [ ] Large text area (min-height: 120px instead of 80px)
- Other notes:

---

## Output Location

Where finished worksheet HTML files should be saved for this child.

**Local path:** e.g., `~/Dropbox/Maya/Worksheets/`  
**GitHub Pages URL:** e.g., `https://yourname.github.io/worksheets/maya/`

---

## Reference Implementations

Good examples to consult when building new worksheets for this child.

| Date | Subject | File | Notes |
|------|---------|------|-------|
| | | | |
