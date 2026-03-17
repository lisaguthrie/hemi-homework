# Contributing — Update Protocol

This document describes how improvements discovered during worksheet generation get propagated back into the framework and profile files.

It is written as instructions *to the model* as much as to human contributors.

---

## The Two-Phase Loop

**Phase 1 — Discovery:** During iteration on a worksheet, an improvement is identified and confirmed working. Examples:
- A new interaction pattern (e.g., tapping the speaking toast cancels speech)
- A profile insight (e.g., slower speech rate works better)
- A new worksheet type successfully implemented
- A build constraint that turned out to be wrong or missing

**Phase 2 — Propagation:** The confirmed improvement is written back into the correct file and submitted as a PR.

---

## Which File Gets Updated?

Use this decision tree:

| Change type | File to update |
|---|---|
| New or revised interaction pattern / JS snippet | `framework/INTERACTION_PATTERNS.md` |
| Visual design change (color, spacing, component) | `framework/DESIGN_SYSTEM.md` |
| New worksheet type documented | `framework/WORKSHEET_TYPES.md` |
| New build rule or constraint | `framework/BUILD_CONSTRAINTS.md` |
| Child-specific preference (speech rate, font size, etc.) | `profiles/{child}/PROFILE.md` |
| Change to how updates are propagated | `framework/CONTRIBUTING.md` |

If a change spans multiple files, list each one separately in the update block.

---

## The `📋 Update Suggested` Block

Whenever the model identifies a confirmed improvement, it appends a `📋` update block at the end of its response.

Preferred rich format:

```
---
## 📋 Framework Update — New Worksheet Type 7

**File:** `framework/WORKSHEET_TYPES.md`
**Section:** Add after Type 6

### Type 7: Proofreading / Error Correction

Describe the change in normal markdown. Include examples, snippets, constraints, and any optional
`*Trigger:*` note if useful.
```

Legacy compact format is also accepted:

```
---
📋 Framework Update Suggested

**File:** `framework/INTERACTION_PATTERNS.md`
**Change:** Add cancel-on-tap behavior to the Speaking Toast pattern. The toast's `onclick` handler should call `window.speechSynthesis.cancel()` followed by `hideToast()`. Without this, speech cannot be interrupted once started.
**Trigger:** Discovered during iteration on `worksheets/maya/2026-03-11-pronouns-2.html`.
```

Parser requirements:
- Every block must contain a `📋` marker.
- Every block must contain `**File:**`.
- Use either `**Change:**` or a heading plus `**Section:**` and markdown body.
- If a change spans multiple files, emit one block per file.

Preferred labels:
- `## 📋 Framework Update — ...` for changes to any file in `/framework/`
- `## 📋 Profile Update — ...` for changes to a child's `PROFILE.md`
- `## 📋 Baseline Spec Update — ...` is also acceptable for framework-level changes

---

## Propagation via CLI or Automation

The `runners/propagate.py` script handles Phase 2 when run explicitly. It:

1. Reads `📋` update blocks from stdin, a file argument, or `pending-updates.md`
2. Identifies the target file(s)
3. Generates an updated version of each file by calling the Claude API with the current file content + the described change block
4. Commits each change to a new branch: `update/{slug}-{date}`
5. Opens a GitHub PR with:
   - Title: the parsed change summary
   - Body: full update block content
   - Label: `framework-update` or `profile-update`

You review and merge (or close) the PR. The main branch stays clean until you approve.

---

## Manual Propagation (claude.ai workflow)

If running from claude.ai without the propagation runner:

1. At the end of an iteration session, prompt: *"Write an updated version of `[filename]` that incorporates the changes we made."*
2. Download the updated file
3. Replace the file in your local repo
4. Commit and push

The `📋 Update Suggested` blocks from earlier in the conversation serve as your checklist.

---

## What Not to Propagate

- Changes that only make sense for one specific worksheet (those belong in the worksheet HTML itself)
- Changes you haven't confirmed working (don't propagate from a plan, only from a verified outcome)
- Stylistic preferences that don't generalize (if you just wanted a different color once, that's not a framework change)
