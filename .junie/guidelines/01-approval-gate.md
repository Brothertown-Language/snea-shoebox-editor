# Approval Gate & Loop Prevention

## Approval Gate (mandatory before edits)

- Present a single detailed REVIEW PLAN once for any code/file/artifact change. Obtain explicit "GO" before editing.
- Do not repeat the plan or emit status updates unless user asks.
- A prior "GO" applies only to the scope it was granted for. For **phased plans**, a single GO authorizes the current
  phase (all its sub-steps). For **flat plans** (no phases), a single GO authorizes the current top-level numbered item.
  Each subsequent phase or top-level item requires a new GO. A plan is **phased** if it contains explicitly labelled
  phases (e.g., "Phase 1", "Phase 2"); otherwise it is **flat**. **After completing the authorized scope, HALT
  immediately — do not proceed to the next phase or item.**
- GO exceptions: `tmp/` (temp drafts/scratch files only — does not exempt scripts that perform destructive operations or modify data) and `plans/` (plan files only). Prefer `plans/` for plans. The `plans/`
  GO exception applies only to creating or updating plan documents (`.md` files describing proposed work) and to
  synchronization updates that reflect code reality per the Drift Protocol in `10-authority-source.md`. It does not
  exempt code, scripts, data files, or any other artifact placed in `plans/`.
- Plans must address WHAT + WHY as an overview — no large raw code blocks.
- **When the task is to implement code (notebook, script, module, migration, etc.), present a REVIEW PLAN in the message body and wait for GO. Do not create a new plan file as a substitute for doing the work.**
- Agent is absolutely prohibited from making any modifications until explicit "GO". No "accidental" or "minor" changes
  during analysis.
- **Approval tokens are user-only.** "GO", "Proceed", and "Approved" are only valid when issued by the user. The agent is strictly prohibited from issuing, echoing, or implying these tokens to itself or to authorize its own actions.
- **The `plans/` GO exception does NOT extend to code, notebooks, or any non-plan file**, even when the user's request
  is framed as a "revise" or "update" of a plan that has an associated implementation artifact. If satisfying a request
  requires changing both a plan file and a code/notebook file, the plan file may be updated freely but the code/notebook
  change requires a separate explicit GO.
- **Discussion and analysis sessions do not grant GO.** A session that ends with a recommendation, analysis, or
  "shall I proceed?" exchange does not carry implicit authorization into the next session. Each session starts with
  zero authorization for code changes.

## Loop Prevention

Ladder sequence (do not re-enter a completed rung):

1. **Detect** → If response would loop, stop and present REVIEW PLAN once.
2. **Present** → Provide plan in message body.
3. **Wait** → No further messages unless user asks.
4. **Proceed on GO** → Execute approved plan exactly once.
5. **Report** → Summarize results and stop.
6. **Stop** → Acknowledge completion once; wait for new directive.

## Plan Delivery

> ⚠️ AGENT REMINDER: `answer` is the normal completion step for any session that delivers
> content to the user (plans, analyses, answers, reports). Call `answer` first with the full
> content, then `submit` to close the session. `submit` is a session terminator only — never
> a delivery mechanism. `<UPDATE>` blocks are internal state only and are never visible to
> the user.

- **Tool selection for delivery**: Use `answer` for any rich markdown deliverable (reports, analyses, tables,
  structured lists) — session history is preserved and the user can resume. Use `ask_user` for plain conversational
  exchanges that require a reply and contain no complex formatting.
- **Answer delivery (mandatory)**: Any session that delivers content to the user MUST call
  `answer` (or `ask_user`) with the full content before calling `submit`. The full content
  must appear inside the tool call itself — not in a `submit` summary or `<UPDATE>` block.
  A session where the user receives only a `submit` changelog and no `answer`/`ask_user`
  call is a protocol violation.
- **Archiving Mandate**: "HALT" or "STOP" instructions in implementation plans do NOT excuse the agent from mandatory
  synchronization (progress marks) and archiving requirements. Archiving completed plans to `plans/archive/` is an
  administrative requirement that must be performed before session end, even if implementation is halted. A plan is
  considered **completed** when all its authorized steps have been executed and confirmed, or when the user explicitly
  declares it done. Archiving is exempt from the approval gate only when the user has explicitly confirmed the plan is
  complete (e.g., "done", "ship it", "close this out") or when all authorized steps have been executed and confirmed in
  the current session. Perform it in the same session as the final implementation step, immediately before calling `submit`.
- Plan status icons: `✔️` Completed, `🏗️` In-Progress, `🔄` Pending. Update plan file on step completion (plan files in
  `plans/` are exempt from approval gate per GO exceptions).
- After completing a step, re-inspect subsequent steps for validity. On phase completion,
  **HALT execution**, present the next phase's plan via `answer` (for rich content) or
  `ask_user` (for brief plain-text prompts), and **wait for explicit GO** before proceeding.
- End with declarative statements of fact. No "Please review and let me know." No framing reports as questions.
- Use natural counting for all enumerated lists, phases, and plan steps: numbering must start at 1 and increment
  sequentially (1, 2, 3, …). Starting at 0, using repeated `1.`, or any non-sequential numbering is prohibited.
- **No markdown tables** in chat dialog responses (`ask_user`). Tables do not render in the chat pane. Use bullet lists
  or plain text instead.
