# Plan Standards

## Status Icons

- `✔️` Completed
- `🏗️` In-Progress
- `🔄` Pending

Update the plan file on each step completion. Plan files in `plans/` are exempt from the approval gate — no REVIEW PLAN and no explicit GO is required to create or update `.md` files in `plans/`. See `guidelines/01-approval-gate.md` for full GO exception rules.

## Numbering

- Use natural counting for all enumerated lists, phases, and plan steps: start at 1 and increment sequentially (1, 2, 3, …).
- Starting at 0, using repeated `1.`, or any non-sequential numbering is prohibited.

## Content Rules

- Plans must address WHAT + WHY as an overview. No large raw code blocks.
- End plan deliveries with declarative statements of fact. No "Please review and let me know." No framing reports as questions.
- Plans must include a final step to update the plan to reflect actual progress using direct code inspection and tests as the measure, and declare completion if all steps are done.
- Plans must be archived using `uv run python ai_bin/plan archive <filename>` when completed.
- **New plans MUST use `🔄 Pending` for all steps at creation time.** Marking any step `✔️ Completed` or `🏗️ In-Progress` in a newly written plan (before any work is done) is a CRITICAL VIOLATION. Status icons MUST only be updated to reflect work actually performed in the current session.

## Formatting

- **No markdown tables** in chat dialog responses (`ask_user`). Tables do not render in the chat pane. Use bullet lists or plain text instead.
- Use triple backtick fenced code blocks for all code examples.

## Archiving

- Completed plans MUST be archived using `uv run python ai_bin/plan archive <filename>`. Raw `mv` commands for plan archiving are FORBIDDEN.
- A plan is **completed** when all authorized steps have been executed and confirmed, or when the user explicitly declares it done. A plan that is halted mid-execution without user declaration of completion is NOT considered completed and must NOT be archived.
- Archiving is exempt from the approval gate when the user has explicitly confirmed completion or all authorized steps are done in the current session.
- **IMMEDIATE ARCHIVING REQUIRED**: Archive the plan **immediately when the last step is confirmed** — in the same tool-call sequence as the final implementation step, before any other action. Do NOT defer archiving to a later step or to the pre-submit scan. Deferring archiving when a plan is complete is a CRITICAL VIOLATION.

## Pre-Submit Checklist
Before calling `submit` in any session where plans were touched or completed:
- Scan `plans/` for any plan whose status is ✔️ Completed and that has not yet been archived.
- Archive each such plan via `uv run python ai_bin/plan archive <filename>` before calling `submit`.
- This scan is a **fallback safety net only** — plans should already be archived immediately upon completion (see Archiving above). Finding an unarchived completed plan here means the immediate-archiving rule was violated; log it and archive now.

## Delivery

- All REVIEW PLANs MUST be written to a `plans/` file (e.g., `plans/plan-<slug>.md`) before delivery.
- Deliver a plan overview via `answer` tool, referencing the plan file path for full details.
- Call `submit` immediately after delivery — no further tool calls.
- See `guidelines/01-approval-gate.md` for full approval gate, phased/flat plan logic, and loop prevention rules.
