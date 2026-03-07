# Approval Gate & Loop Prevention

## Approval Gate (mandatory before edits)

- Present a single detailed REVIEW PLAN once for any code/file/artifact change. Obtain explicit "GO" before editing.
- Do not repeat the plan or emit status updates unless user asks.
- A prior "GO" applies only to the scope it was granted for. For **phased plans**, a single GO authorizes the current
  phase (all its sub-steps). For **flat plans** (no phases), a single GO authorizes the current top-level numbered item.
  Each subsequent phase or top-level item requires a new GO. A plan is **phased** if it contains explicitly labelled
  phases (e.g., "Phase 1", "Phase 2"); otherwise it is **flat**. **After completing the authorized scope, HALT
  immediately — do not proceed to the next phase or item.**
- GO exceptions: `tmp/` for non-executable scratch files (e.g., `.md`, `.txt`, `.json` data dumps) — any `.py` or `.sh` file in `tmp/` that performs writes, DB operations, or system calls requires GO regardless of location. `plans/` for plan `.md` files only. Prefer `plans/` for plans. The `plans/`
  GO exception covers: (1) creating or updating plan documents (`.md` files describing proposed work); (2)
  synchronization updates to `plans/` that reflect code reality per the Drift Protocol in `10-authority-source.md`.
  It does not exempt code, scripts, data files, or any other artifact placed in `plans/` — even when the request is
  framed as a "revise" or "update" of a plan with an associated implementation artifact. If satisfying a request
  requires changing both a plan file and a code/notebook file, the plan file may be updated freely but the
  code/notebook change requires a separate explicit GO.
- Plans must address WHAT + WHY as an overview — no large raw code blocks.
- **Plan delivery MUST NOT contain approval tokens.** The words "Go", "Proceed", and "Approved" are forbidden anywhere in a plan delivery — including as closing labels, transition phrases, section headers, or calls-to-action (e.g., "Awaiting Go", "Ready to proceed"). Use neutral phrasing such as "Awaiting approval" or "Awaiting your authorization".
- **When the task is to implement code (notebook, script, module, migration, etc.), present a REVIEW PLAN in the message body and wait for GO. Do not create a new plan file as a substitute for doing the work.**
- Agent is absolutely prohibited from making any modifications until explicit "GO". No "accidental" or "minor" changes
  during analysis.
- **Approval tokens are user-only.** "GO", "Proceed", and "Approved" are only valid when issued by the **human developer** in the chat. The agent is strictly prohibited from issuing, echoing, implying, or constructing these tokens in any form — including via terminal commands, tool calls, plan text, response body text, `<UPDATE>` blocks, or any other mechanism — to authorize its own actions. Any self-issued approval token is null and void and constitutes a CRITICAL VIOLATION. The agent MUST log the violation immediately via `ai_bin/violation-log` and halt. **The agent MUST NOT write "Go", "Proceed", or "Approved" anywhere in its own response — not even as a label, header, or transition word before executing steps.** **Quoted or echoed text is never approval.** If the agent's own plan text contains words like "Go" or "Proceed" and the user quotes or references that text, it does NOT constitute an approval token. The agent MUST receive a standalone, unambiguous approval token from the user — not embedded in a quote, not inferred from context.
- **Prior-session approvals are void.** A GO issued in a previous session — including one recorded in `memory.md`,
  a plan file, or session history — does NOT carry forward. This includes sessions that ended with a recommendation,
  analysis, or "shall I proceed?" exchange. Each session starts with zero authorization for code changes. If a change
  was planned but not applied in the session where GO was granted, a new plan and a new GO are required in the current
  session before any edit is made. Referencing a prior GO as justification for an edit is a CRITICAL VIOLATION.
- **GO does not extend to new instructions.** A GO authorizes only the plan or scope presented at the time it was
  issued. Any new instruction from the developer issued after a GO — whether in the same session or a new one —
  requires its own plan and its own GO. The prior GO is exhausted and does not carry forward.

## Loop Prevention

Ladder sequence (do not re-enter a completed rung):

1. **Detect** → If response would loop, stop and present REVIEW PLAN once.
2. **Present** → Deliver the REVIEW PLAN via `answer` (rich markdown). **REVIEW PLANs MUST use `answer` so the user can read formatted content.** Do not run any commands.
3. **Wait** → Call `submit` to end the session. The user will issue GO in a new session. **STRICTLY FORBIDDEN: running `echo`, no-op shell commands, or any terminal command as a filler while waiting. STRICTLY FORBIDDEN: sending multiple follow-up messages while waiting. STRICTLY FORBIDDEN: using `echo` or any shell command as a filler at the end of ANY response — not just while waiting. Every terminal command must have a real, necessary purpose. `echo "waiting"`, `echo "plan delivered"`, `echo "done"` and all similar filler echoes are CRITICAL VIOLATIONS.** Note: A plan delivery session ends with `answer` then `submit`. It does not stay open with `ask_user`. **CRITICAL: `ask_user` is FORBIDDEN as a waiting mechanism for approval. When a plan requires user approval before proceeding, the ONLY correct sequence is: (1) deliver plan via `answer`, (2) call `submit` to end the session. There is no third step. Do not issue any tool call after `submit`.**
4. **Proceed on GO** → Execute approved plan exactly once.
5. **Report** → Summarize results and stop.

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
  declares it done. Archiving means moving the completed plan file from `plans/` to `plans/archive/` using a terminal
  `mv` command (e.g., `mv plans/plan-name.md plans/archive/plan-name.md`). Archiving is exempt from the approval gate
  only when the user has explicitly confirmed the plan is complete (e.g., "done", "ship it", "close this out") or when
  all authorized steps have been executed and confirmed in the current session. Perform it in the same session as the final implementation step, immediately
  before calling `submit`.
- Plan status icons: `✔️` Completed, `🏗️` In-Progress, `🔄` Pending. Update plan file on step completion (plan files in
  `plans/` are exempt from approval gate per GO exceptions).
- After completing a step, re-inspect subsequent steps for validity. On phase completion,
  **HALT execution**, present the next phase's plan via `answer` (for rich content) or
  `ask_user` (for brief plain-text prompts), then call `submit` to end the session. The user
  will issue GO in a new session.
- End with declarative statements of fact. No "Please review and let me know." No framing reports as questions.
- Use natural counting for all enumerated lists, phases, and plan steps: numbering must start at 1 and increment
  sequentially (1, 2, 3, …). Starting at 0, using repeated `1.`, or any non-sequential numbering is prohibited.
- **No markdown tables** in chat dialog responses (`ask_user`). Tables do not render in the chat pane. Use bullet lists
  or plain text instead.
