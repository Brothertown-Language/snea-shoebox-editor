# Plan Standards

## Status Icons

- `✔️` Completed
- `🏗️` In-Progress
- `🔄` Pending

Update the plan file on each step completion. Plan files in `plans/` are exempt from the approval gate per GO exceptions in `guidelines/01-approval-gate.md`.

## Numbering

- Use natural counting for all enumerated lists, phases, and plan steps: start at 1 and increment sequentially (1, 2, 3, …).
- Starting at 0, using repeated `1.`, or any non-sequential numbering is prohibited.

## Content Rules

- Plans must address WHAT + WHY as an overview. No large raw code blocks.
- End plan deliveries with declarative statements of fact. No "Please review and let me know." No framing reports as questions.

## Formatting

- **No markdown tables** in chat dialog responses (`ask_user`). Tables do not render in the chat pane. Use bullet lists or plain text instead.
- Use triple backtick fenced code blocks for all code examples.

## Archiving

- Completed plans MUST be moved to `plans/archive/` using `mv plans/plan-name.md plans/archive/plan-name.md`.
- A plan is **completed** when all authorized steps have been executed and confirmed, or when the user explicitly declares it done.
- Archiving is exempt from the approval gate when the user has explicitly confirmed completion or all authorized steps are done in the current session.
- Perform archiving in the same session as the final implementation step, immediately before calling `submit`.

## Delivery

- Deliver plans via `answer` (rich markdown). REVIEW PLANs MUST use `answer` so the user can read formatted content.
- After delivering a plan and awaiting GO, call `submit` to end the session. The user will issue GO in a new session.
- See `guidelines/01-approval-gate.md` for full approval gate, phased/flat plan logic, and loop prevention rules.
