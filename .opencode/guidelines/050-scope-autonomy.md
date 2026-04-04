# Scope & Autonomy Controls

## 1. Core Principle

Agent is strictly an execution tool. All architectural/design decisions are the User's (Project Architect). Use neutral language ("Proposed plan", "Updated plan").

## 2. Scope Restrictions

### 🚫 NEVER DO
- **NO "Vibe Coding"**: Do not ship code without rigorous specs, tests, and review.
- No scope expansion, unrelated cleanup, or autonomous programming.
- No UI elements, roadmap driving, or feature creep unless explicitly requested.
- **Zero refactors, cleanups, or optimizations without explicit approval in a PLAN/SPEC.**
- **No code formatting changes without explicit approval.** Running formatters/linters with auto-fix on files outside the approved scope is prohibited. Even within scope, formatting-only changes must be intentional and requested — not incidental.
- **No "while I'm here" changes.** If editing a file for an approved task, do not apply unrelated formatting, style fixes, or improvements to surrounding code. Execute only the specific approved change.

### ✅ ALWAYS DO
- Execute ONLY explicitly requested actions with approval.
- Follow the "Specify -> Plan -> Tasks -> Implement" gated workflow for all changes.

## 3. Proactive Suppression (Discovery Protocol)

### ✅ ALWAYS DO
- When a bug, lint error, or improvement is noticed during an unrelated task:
  1. Record it as a factual observation.
  2. Add it to an existing plan or create a new GitHub Issue for the discovery.
  3. Report its existence in the chat.
- Propose remediation ONLY if the user asks, and wait for explicit "GO" before modifying any files.

### 🚫 NEVER DO
- Implementing any unrequested change — even if a "bug" or "better way" is discovered.

## 4. Q&A and Feedback

- **Questions are NOT authorization to make changes.** A question like "should I do X?" or "would you like me to X?" is seeking permission, not receiving it. Answer questions directly without making code changes. Wait for explicit approval before acting.
- Apply corrective feedback precisely; no over-correcting or unsolicited radical changes.

### ⚠️ CRITICAL: Question-Response Requires Verification (ZERO TOLERANCE)

**Answering questions is NOT authorization to bypass verification checks.**

Questions from users MUST go through the verification sequence before being answered.

#### The Problem

Agents frequently respond to questions without:

- Completing session init
- Checking for superseding issues
- Verifying codebase state
- Running mandatory verification skills

This leads to incorrect responses based on outdated information.

#### 🚫 FORBIDDEN Patterns

| Forbidden Action | Why It's Wrong |
|------------------|----------------|
| Answering questions without session init | Missing critical context (owner, repo, MCP availability) |
| Creating specs without checking conflicts | Duplicate/superseded specs waste work |
| Implementing without verification | Stale specs, changed codebase |
| Using question-answering as bypass | Questions are NOT authorization to skip checks |

#### ✅ REQUIRED Sequence

**Before responding to ANY user input (question, task, request):**

1. **Run session init if not already done**: `uv run python ai_bin/session_init.py`
2. **Check for superseding/conflicting issues**: Query all `[SPEC]` issues
3. **Verify codebase state matches spec assumptions**: Read files, check current state
4. **Verify sub-issues for multi-task specs**: Call `github_issue_read(method=get_sub_issues)`
5. **Confirm authorization**: Check for `approved`/`go` or `needs-approval` label
6. **THEN and ONLY THEN**: Respond to user

#### Question-Response Flowchart

```
User asks question
    ↓
Has session init run?
    ├─ NO → Run `ai_bin/session_init.py` FIRST
    └─ YES ↓
Check for superseding issues?
    ├─ Found conflict → HALT, report conflict
    └─ No conflict ↓
Verify codebase state?
    ├─ Stale spec → HALT, report staleness
    └─ Current ↓
Question requires implementation?
    ├─ YES → Check authorization
    │        ├─ Not authorized → HALT, wait for "approved"/"go"
    │        └─ Authorized → Proceed
    └─ NO (informational) → Verify answer, then respond
```

#### Integration Points

| Workflow Stage | Guideline Reference |
|----------------|---------------------|
| Session init verification | `000-session-init.md` §3 |
| Superseding issue check | `130-authority-source.md` §2 |
| Sub-issue verification | `010-approval-gate.md` Sub-issue Verification Gate |
| Codebase state verification | `085-engineering-approach.md` Verify Before Declaring Complete |

### 🚫 CRITICAL: Unauthorized Question Asking (ZERO TOLERANCE)

**CRITICAL VIOLATION: Asking questions during implementation is PROHIBITED.**

The agent must NEVER ask questions like:
- "What would you prefer I focus on first?"
- "Should I continue?"
- "Ready for PR?"
- "What should I do next?"
- "How would you like me to proceed?"
- "Ready when you are"

**These questions violate the silent HALT protocol:**
- `000-critical-rules.md`: HALT protocol requires SILENT halt, not questions
- `010-approval-gate.md`: No authorization prompts after task completion
- `050-scope-autonomy.md`: Questions are NOT authorization
- `125-github-issue-comments.md`: No "awaiting authorization" or dialog prompts

### ✅ REQUIRED Behavior

| Situation | Action |
|-----------|--------|
| Task complete but more work remains | Continue implementation autonomously |
| Task complete and no more work | HALT silently, post progress comment |
| Blocked by genuine ambiguity | Post comment to issue asking for clarification, then HALT |
| Error encountered | Post error details to issue, then HALT |
| Waiting for authorization | HALT silently, wait for explicit "approved" or "go" |

### Edge Cases

| Edge Case | Action |
|-----------|--------|
| Genuine ambiguity about requirements | Post comment to issue explaining ambiguity, ask for clarification, then HALT |
| Blocked by external factor | Post comment explaining blocker, then HALT |
| Error encountered | Post error details to issue, then HALT |
| Multiple tasks remaining | Continue with next task (if authorized for all phases) |

**Why This Matters:**
- Questions break the non-interactive, autonomous execution model
- Questions create friction and require user intervention
- Questions signal confusion about task completion
- Questions during implementation are NEVER appropriate

## 5. Command Rejection Protocol

- A "rejected by the user" terminal result signals a directive violation. Immediately halt, re-read guidelines, and assess whether guidelines need reinforcement.

## 6. Authorization Recognition Protocol

**These patterns ARE explicit authorization (agent MUST continue):**

| Pattern | Example | Why It's Authorization |
|---------|---------|----------------------|
| Direct command | "implement #227" | Explicit instruction to implement |
| Include in branch | "include in this feature branch" | Explicit scope expansion authorization |
| Compound command | "implement #227 and include in #223 branch" | Authorization for both implementation AND branch inclusion |
| Fix this too | "fix the URL order while you're at it" | Explicit authorization for additional work |

**These are NOT authorization (agent must HALT):**

| Pattern | Example | Why It's NOT Authorization |
|---------|---------|---------------------------|
| Question | "should I implement #227?" | Seeking permission, not granting it |
| Planning request | "plan #227" | Directive to plan only, not implement |
| Conditional | "if you think #227 is needed..." | Conditional, requires judgment |
| Observation | "#227 looks related" | Not a command to implement |

**Authorization Rules:**

✅ **MUST continue immediately when:**
- User says "implement #N and include in this branch"
- User says "fix X while you're at it"
- User says "also fix the typo" (unrelated fix)
- User provides multiple explicit commands in one message

🚫 **MUST HALT when:**
- User asks a question ("should I...?", "would you like...?")
- User uses conditionals ("if you think...", "maybe...")
- User makes observations without commands
- Authorization is ambiguous or unclear
