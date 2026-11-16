# Vocabulary in Context activity

Reusable template for the Wordly Wise "Vocabulary in Context" section (the **E** exercise): a short reading passage on the left, comprehension questions on the right. The student answers each question with a complete sentence, typed or dictated. Built from the Lesson 7E worksheet.

## Configure a new activity

Copy `template.html` (never a previous instance) to `worksheets/{child}/YYYY-MM-DD-{slug}.html` and edit **only** the JSON in the `activityConfig` block near the top:

- `meta.lessonLabel`, `meta.title`, `meta.instructions` — header text and the printed directions (read aloud when tapped)
- `meta.passageTitle` — title of the reading passage
- `meta.wordListLabel` — label on the collapsible word bank (e.g. `Word List 8`)
- `meta.storageKey` — **must be unique per instance** (progress is saved under it). Pattern: `ww{book}_lesson_{N}e_vocabulary_in_context_{child}_{YYYY_MM_DD}_v1`
- `meta.backHref`, `meta.backLabel` — link back to the lesson index
- `meta.bookLabel`, `meta.printTitle`, `meta.studentName` — header and Export / Print heading
- `words` — one object per word in the lesson's word bank: `senses` with `form`, `pos` (`n`/`v`/`adj`/`adv`), `num`, `definition`, `example`. Powers tap-for-definition and the "choose a word" menus.
- `formPairs` — word → every inflected form that should be tappable in the passage or questions (e.g. `originate` → `origin`, `originated`).
- `passage` — array of paragraphs; each paragraph is an array of **sentences** (one string per sentence, as printed). Sentences are the tap-to-hear unit.
- `questions` — array of question strings, exactly as printed.

The template ships with the Lesson 7E content as a worked example; replace every block.

## Built-in behaviour

- Passage and questions side by side on wide screens (each pane scrolls independently); stacked on tablets and phones
- Tap a sentence, a ▶ paragraph, a question, or the directions to hear it; tap any highlighted vocabulary word (passage, question, or word bank) for its definition and example
- Questions that do not already contain a lesson word get a **"Use one lesson word"** menu; words already chosen for another question are removed from the other menus ("Choose a different word…" is always available) — this enforces "use each word only once"
- 🎙️ Dictate per question: continuous listening that auto-restarts if the browser ends the session, ignores silence, appends finished phrases, stops when reading aloud starts or the tab is hidden, and reports a blocked microphone. Disabled where the browser has no speech recognition (typing always works)
- ▶ Read my answer reads the student's sentence back
- No scoring or checks: answers are original writing for an adult to review. Progress pips count a question as answered once it has text (and a chosen lesson word where required)
- Autosave to localStorage, double-tap Clear, Export / Print (prints the passage, questions, and the student's answers; no answer key)
