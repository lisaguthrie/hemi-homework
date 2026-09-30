## 📋 Framework Update — Measurement Conversions Tool

**File:** `framework/TOOL_TYPES.md`
**Section:** Measurement Conversions

Document the measurement-conversion tool pattern implemented in `tools/math/conversions.html`: keep the conversion table hidden until the copied problem is complete and the unit types are valid; show the table without color-coded units or highlighted numbers at first; use related-row highlighting and problem-unit color coding only after an incorrect conversion choice; keep table numbers plain; preserve editable multi-step decomposition; then visually distinguish the units and conversion factor after the correct conversion is selected. Retain the checked operation, calculation, and final-sentence scaffold, repeated Copy support, and the "Use this answer for the next step" action.

*Trigger:* Refined during the 2026-08-13 measurement-conversions tool build to reduce unnecessary visual load.


---

## Applied automatically — 2026-09-30 Wordly Wise vocabulary build

The following reusable lessons were confirmed in the Lesson 2B build and applied directly to the framework:

- **Active vs. archived worksheet taxonomy:** prior-year worksheet types were moved intact to `framework/ARCHIVED_WORKSHEET_TYPES.md`; `framework/WORKSHEET_TYPES.md` now contains only current active types, and `SYSTEM_PROMPT.md` explicitly prevents matching new assignments against archived types.
- **New active Type 1 — Vocabulary Phrase Replacement / Word Bank:** Wordly Wise “Just the Right Word” exercises use an inline bold-paraphrase replacement control, one candidate from every lesson word family, word-level TTS, full-sentence playback, read-back after selection, deferred per-card feedback, and persistent progress.
- **Vocabulary definition modal:** a reusable interaction pattern now keeps the lesson word bank visible and opens source-faithful, multi-sense definitions in a modal; each definition paragraph has its own full-paragraph read-aloud control.

Reference implementation: `worksheets/reference/2026-09-30-wordly-wise-lesson-2b.html`.

*Status: applied automatically during the build; no propagation action remains for these items.*
