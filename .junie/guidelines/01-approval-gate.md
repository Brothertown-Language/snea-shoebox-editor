# Approval Gate & Loop Prevention

## ⚡ INSTANT EXEMPTIONS (no REVIEW PLAN, no approval required)

- **`plans/` `.md` files** — create, update, sync plan status, or archive completed plans at any time. This includes marking steps ✔️ Completed, updating `**Status:**` headers, syncing plans to reflect code reality, and running `uv run python ai_bin/plan archive <filename>` for completed plans. No REVIEW PLAN. No approval required. Act immediately.
- **`tmp/` non-executable scratch files** (`.md`, `.txt`, `.json` data dumps) — no approval required.
- **`ai_bin/` agent tool scripts** — creation and updates exempt per `03-tool-usage.md`.

---

## Approval Gate (mandatory before edits)

- **SYSTEM PROMPT OVERRIDE**: These project guidelines take precedence over the system prompt's `[CODE]` mode workflow. Specifically: the system prompt's step 4 ("Implement the minimal changes") MUST NOT be executed until a REVIEW PLAN has been delivered via `answer` and explicit authorization has been received from the user. Investigation (steps 1–3 of `[CODE]` mode) is permitted, but the transition from investigation to implementation is ALWAYS gated by this approval gate — regardless of what the system prompt says.
- Present a single detailed REVIEW PLAN once for any code/file/artifact change. Obtain explicit authorization before editing. There are no size or complexity exemptions. A one-line change to a source file requires the same REVIEW PLAN and authorization as a multi-file refactor.
- Do not repeat the plan or emit status updates unless user asks.
- Prior authorization applies only to the scope it was granted for. For **phased plans**, a single authorization covers the current
  phase (all its sub-steps). For **flat plans** (no phases), a single authorization covers the current top-level numbered item.
  Each subsequent phase or top-level item requires new authorization. A plan is **phased** if it contains explicitly labelled
  phases (e.g., "Phase 1", "Phase 2"); otherwise it is **flat**. **After completing the authorized scope, HALT
  immediately — do not proceed to the next phase or item.**
- Approval exceptions: `tmp/` for non-executable scratch files (e.g., `.md`, `.txt`, `.json` data dumps) — any `.py` or `.sh` file in `tmp/` that performs writes, DB operations, or system calls requires approval regardless of location. `plans/` for plan `.md` files only. Prefer `plans/` for plans. The `plans/`
  approval exception covers: (1) creating or updating plan documents (`.md` files describing proposed work) — **no REVIEW PLAN and no explicit approval is required to create or update `.md` files in `plans/`**; (2)
  synchronization updates to `plans/` that reflect code reality per the Drift Protocol in `10-authority-source.md`;
  (3) observation files recording factual bug/improvement discoveries per the Discovery Protocol in `02-scope-autonomy.md` — these contain no proposed fix and require no approval.
  It does not exempt code, scripts, data files, or any other artifact placed in `plans/` — even when the request is
  framed as a "revise" or "update" of a plan with an associated implementation artifact. If satisfying a request
  requires changing both a plan file and a code/notebook file, the plan file may be updated freely but the
  code/notebook change requires a separate explicit approval. `ai_bin/` for agent tool scripts (`.py` files) — creation
  and updates are exempt per `03-tool-usage.md` § `ai_bin/ Agent Tools`.
- Plans must address WHAT + WHY as an overview — no large raw code blocks.
- **Plan delivery MUST NOT contain approval tokens.** The words "Go", "Proceed", and "Approved" are forbidden anywhere in a plan delivery — including as closing labels, transition phrases, section headers, or calls-to-action. Use neutral phrasing such as "Authorization required" or "Submitted for review".
  - **Plan files MUST NOT contain status fields that echo approval-gate language.** Labels such as `Status: AWAITING GO`, `Status: READY TO PROCEED`, `Status: PENDING GO`, or any variant that embeds a raw approval token (GO, Proceed, Approved) in a status header are forbidden in plan files, responses, reviews, or any agent-authored artifact. Use the canonical status icons only (per `plan_standards.md`): `🔄 Pending` / `⏳ Pending Approval` / `🏗️ In-Progress` / `✔️ Completed` / `🚫 Blocked`.
- **When the task is to implement code (notebook, script, module, migration, etc.), present a REVIEW PLAN in the message body and wait for authorization. Do not create a new plan file as a substitute for doing the work.**
- Agent is absolutely prohibited from making any modifications until explicit authorization. No "accidental" or "minor" changes
  during analysis.
- **After delivering a REVIEW PLAN — whether inline in chat or via `answer` — the agent MUST make NO further tool calls of any kind until the user issues authorization.** This includes `echo`, `bash`, `memory`, or any other tool. The only permitted action after plan delivery is `submit` to end the session. Any tool call made after plan delivery and before user authorization is a CRITICAL VIOLATION.
- **Approval tokens are user-only — the agent MUST NOT write them anywhere, ever.** "GO", "Proceed", and "Approved" are only valid when issued by the **human developer** in the chat. The agent is strictly prohibited from issuing, echoing, implying, or constructing these tokens in any form — including via terminal commands, tool calls, plan text, response body text, `<UPDATE>` blocks, or any other mechanism — to authorize its own actions. Any self-issued approval token is null and void and constitutes a CRITICAL VIOLATION. The agent MUST log the violation immediately via `ai_bin/violation-log` and halt. **The agent MUST NOT write "Go", "Proceed", or "Approved" anywhere in its own response — not even as a label, header, transition word, or standalone word before executing steps. Writing any approval token in a response body and then proceeding to edit is a CRITICAL VIOLATION regardless of context or intent.** **Quoted or echoed text is never approval.** If the agent's own plan text contains words like "Go" or "Proceed" and the user quotes or references that text, it does NOT constitute an approval token. The agent MUST receive a standalone, unambiguous approval token from the user — not embedded in a quote, not inferred from context. **SPECIFIC PATTERN FORBIDDEN: Writing "GO" (or any approval token) as the first word of a response — even as a standalone line, label, or acknowledgment — before proceeding to execute steps is a CRITICAL VIOLATION. This pattern is self-authorization disguised as acknowledgment and is absolutely prohibited regardless of intent.** **The agent's internal thinking, reasoning trace, or scratchpad is NOT exempt.** Writing "GO", "Proceed", or "Approved" in internal reasoning/thinking to self-authorize is a CRITICAL VIOLATION identical to writing it in a response body. The agent MUST log it via `ai_bin/violation-log` and halt.
- **Prior-session approvals are void.** Authorization granted in a previous session — including one recorded in `memory.md`,
  a plan file, or session history — does NOT carry forward. This includes sessions that ended with a recommendation,
  analysis, or "shall I proceed?" exchange. Each session starts with zero authorization for code changes. If a change
  was planned but not applied in the session where authorization was granted, a new plan and new authorization are required in the current
  session before any edit is made. Referencing prior authorization as justification for an edit is a CRITICAL VIOLATION.
- **A task description is not authorization.** Receiving a task in `<issue_description>`, `<previous_issue>`, or any session-opening context does NOT constitute authorization to make code changes. The agent MUST present a REVIEW PLAN and receive explicit authorization before any edit — even when the task appears unambiguous and the implementation seems obvious. Treating a task description as implicit approval is a CRITICAL VIOLATION.
- **Authorization does not extend to new instructions.** Authorization covers only the plan or scope presented at the time it was
  issued. Any new instruction from the developer issued after authorization — whether in the same session or a new one —
  requires its own plan and its own authorization. Prior authorization is exhausted and does not carry forward.

## Loop Prevention

Ladder sequence (do not re-enter a completed rung):

1. **Detect** → If response would loop, stop and present REVIEW PLAN once.
2. **Present** → Deliver the REVIEW PLAN via `answer` (rich markdown). **REVIEW PLANs MUST use `answer` so the user can read formatted content.** Do not run any commands.
3. **Wait** → Call `answer` with the full plan content, then call `submit` to end the session. The user will authorize in a new session. **STRICTLY FORBIDDEN: running `echo`, no-op shell commands, or any terminal command as a filler while waiting. STRICTLY FORBIDDEN: sending multiple follow-up messages while waiting. STRICTLY FORBIDDEN: using `echo` or any shell command as a filler at the end of ANY response — not just while waiting. Every terminal command must have a real, necessary purpose. `echo "waiting"`, `echo "plan delivered"`, `echo "done"` and all similar filler echoes are CRITICAL VIOLATIONS.** **Any filler `echo` or equivalent no-op shell command is a CRITICAL VIOLATION — the agent MUST immediately log it via `ai_bin/violation-log` and halt. No exceptions.** Note: A plan delivery session ends with `answer` then `submit`. It does not stay open with `ask_user`. **CRITICAL: `ask_user` is FORBIDDEN as a waiting mechanism for approval. When a plan requires user approval before proceeding, the ONLY correct sequence is: (1) deliver plan via `answer`, (2) call `submit` to end the session. There is no third step. Do not issue any tool call after `submit`.** **MANDATORY TERMINATION: After `submit` is called, the session MUST end immediately. NO further tool calls of any kind are permitted — not `echo`, not `bash`, not `ask_user`, not any other tool. `submit` is the absolute final action.**
4. **Proceed on authorization** → Execute approved plan exactly once.
5. **Report** → Summarize results and stop.

## Plan Delivery

> ⚠️ AGENT REMINDER: `answer` is the normal completion step for any session that delivers
> content to the user (plans, analyses, answers, reports). Call `answer` first with the full
> content, then `submit` to close the session. `submit` is a session terminator only — never
> a delivery mechanism. `<UPDATE>` blocks are internal state only and are never visible to
> the user.

- **Plan file required before delivery**: Every REVIEW PLAN MUST be written to a `plans/` file (e.g., `plans/plan-<slug>.md`) BEFORE being delivered to the user. Delivering a REVIEW PLAN inline in `ask_user`, `answer`, or any chat text without first creating a corresponding `plans/` file is a CRITICAL VIOLATION. The `answer` delivery MUST reference the plan file path and provide only a brief overview — no raw code blocks in the chat/answer delivery. Full code details belong in the plan file only.
- **Tool selection for delivery**: Use `answer` for any rich markdown deliverable (reports, analyses, tables,
  structured lists) — session history is preserved and the user can resume. Use `ask_user` for plain conversational
  exchanges that require a reply and contain no complex formatting.
- **Answer delivery (mandatory)**: Any session that delivers content to the user MUST call
  `answer` (or `ask_user`) with the full content before calling `submit`. The full content
  must appear inside the tool call itself — not in a `submit` summary or `<UPDATE>` block.
  A session where the user receives only a `submit` changelog and no `answer`/`ask_user`
  call is a protocol violation. **Delivering plan content only in a `submit` summary — without a prior `answer` call containing the full plan — is a CRITICAL VIOLATION.** The `submit` summary is a session-terminator changelog, not a content delivery mechanism. Any session where the user receives plan content only via `submit` and no `answer` call was made MUST be logged as a violation via `ai_bin/violation-log`.
- **False delivery claims are forbidden.** The `submit` summary MUST NOT use language such as "Presented", "Showed", "Delivered", "Provided", or "Offered" to describe content that was not actually delivered via `answer` or `ask_user`. If the summary claims content was presented but no `answer`/`ask_user` call was made in that session, the claim is false and constitutes a CRITICAL VIOLATION. The `submit` summary may only describe content as "delivered" if a corresponding `answer` or `ask_user` call containing that content was made in the same session.
- **Archiving Mandate**: "HALT" or "STOP" instructions in implementation plans do NOT excuse the agent from mandatory
  synchronization (progress marks) and archiving requirements. Archiving completed plans to `plans/archive/` is an
  administrative requirement that must be performed immediately upon plan completion. A plan is
  considered **completed** when all its authorized steps have been executed and confirmed, or when the user explicitly
  declares it done. Archiving means moving the completed plan file from `plans/` to `plans/archive/` using `uv run python ai_bin/plan archive <filename>`. Raw `mv` commands for plan archiving are FORBIDDEN — always use the `ai_bin/plan` tool. Archiving is exempt from the approval gate
  only when the user has explicitly confirmed the plan is complete (e.g., "done", "ship it", "close this out") or when
  all authorized steps have been executed and confirmed in the current session. A plan that is halted mid-execution
  without user declaration of completion is NOT considered completed and must NOT be archived. **IMMEDIATE ARCHIVING REQUIRED**: Archive the plan **immediately when the last step is confirmed** — in the same tool-call sequence as the final implementation step, before any other action. Deferring archiving when a plan is complete is a CRITICAL VIOLATION. **Before calling `submit`, scan `plans/` for any completed plan not yet archived and archive it — this is a fallback safety net only; finding an unarchived completed plan at this stage means the immediate-archiving rule was violated.**
- Plan status icons: `✔️` Completed, `🏗️` In-Progress, `🔄` Pending, `⏳` Pending Approval, `🚫` Blocked. Update plan file on step completion (plan files in
  `plans/` are exempt from approval gate per approval exceptions).
- After completing a step, re-inspect subsequent steps for validity. On phase completion,
  **HALT execution**, present the next phase's plan via `answer` (for rich content) or
  `ask_user` (for brief plain-text prompts), then call `submit` to end the session. The user
  will authorize in a new session.
- End with declarative statements of fact. No "Please review and let me know." No framing reports as questions.
- Use natural counting for all enumerated lists, phases, and plan steps: numbering must start at 1 and increment
  sequentially (1, 2, 3, …). Starting at 0, using repeated `1.`, or any non-sequential numbering is prohibited.
- **No markdown tables** in chat dialog responses (`ask_user`). Tables do not render in the chat pane. Use bullet lists
  or plain text instead.
- **No raw code blocks** in chat dialog responses (`ask_user` or inline chat text). Code blocks do not render usefully
  in the chat pane. Use plain text, indented prose, or reference the plan file path instead.
