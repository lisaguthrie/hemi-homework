---
name: Runner Approval Guardrails
description: Use when working on runner scripts or worksheet build flows to standardize approval wording and avoid accidental early execution.
applyTo: "runners/**/*.py"
---

# Runner Approval Guardrails

- Treat worksheet generation as a gated action.
- Do not trigger build execution until explicit approval is present.

## Approval Wording Standard

- Preferred approval phrase: `BUILD NOW`
- Also accepted: `go ahead and build`, `ok build it`
- Not approval: `maybe`, `draft only`, `let us think`

## Execution Rules

- In planning mode, discuss approach and stop.
- Before running any build step, restate that build is pending approval.
- If approval is ambiguous, ask one concise confirmation question instead of executing.
- If user says `build only`, skip any automatic framework/profile edits.
