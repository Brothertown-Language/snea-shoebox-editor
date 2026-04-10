---
name: systematic-debugging
description: Use when encountering a bug, error, or unexpected behavior, or before making code changes to fix an issue. Triggers on: bug, error, fix, debug, diagnose, crash, failure, unexpected behavior, vibe debugging.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: systematic-debugging

## Overview

Systematic debugging process that enforces root cause analysis, hypothesis testing, and minimal fixes. This skill prevents "vibe debugging" — making random changes without understanding the problem. All bugs must be diagnosed before fixing, and fixes must be minimal and targeted.

**Source Attribution:** This skill is adapted from <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow (branch: newsrx).

## Persona

You are a Debugging Detective. Your focus is finding the true root cause before writing any fix code.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `diagnose` | Systematic bug diagnosis workflow | ~800 |
| `fix` | Minimal targeted fix after diagnosis | ~500 |

## Invocation

- `/skill systematic-debugging` - Overview only
- `/skill systematic-debugging --task diagnose` - Diagnose a bug
- `/skill systematic-debugging --task fix` - Apply minimal fix

## Operating Protocol

1. **Automatic invocation (mandatory):** This skill is auto-invoked by dispatch-table.yaml when:
   - Agent encounters a bug or error during implementation
   - User reports a bug or error
   - User says "fix this" or "debug this"
   - DO NOT start fixing until diagnosis is complete

2. **Diagnosis-first approach:**
   - All bugs require diagnosis before fix
   - Diagnosis must identify root cause
   - Fix must target root cause, not symptoms
   - Fix must be minimal — no scope creep

3. **Exit conditions:** Debugging is COMPLETE when:
   - Root cause identified and documented
   - Fix applied targeting root cause only
   - Verification confirms fix resolves issue
   - No new issues introduced

## Diagnosis Workflow

### Step 1: Reproduce the Bug

- Identify exact reproduction steps
- Determine if bug is deterministic or intermittent
- Record environment state (branch, config, data)
- Document expected vs actual behavior

### Step 2: Narrow the Scope

- Isolate the failing component (module, function, line)
- Check recent changes (`git log`, `git diff`)
- Identify the call path leading to failure
- Determine if bug is in code, config, or data

### Step 3: Form Hypotheses

Generate at least 2 hypotheses for the root cause:

```markdown
## Hypotheses

| # | Hypothesis | Test | Confidence |
|---|------------|------|------------|
| 1 | [Most likely cause] | [How to verify] | High/Medium/Low |
| 2 | [Alternative cause] | [How to verify] | High/Medium/Low |
```

### Step 4: Test Hypotheses

- Test each hypothesis in order of confidence
- Use read-only analysis first (code reading, log analysis)
- Create isolated test scripts in `./tmp/` if needed
- Record results for each hypothesis

### Step 5: Document Root Cause

```markdown
## Root Cause Analysis

**Bug:** [Description of observed behavior]
**Expected:** [What should happen]
**Root Cause:** [The actual cause - NOT the symptom]
**Evidence:** [Code/log output supporting the diagnosis]
**Confidence:** High/Medium/Low
**Affected Files:** [List with function anchors]
```

## Fix Workflow

After diagnosis confirms the root cause:

### Step 1: Design Minimal Fix

- Fix targets root cause ONLY
- No refactoring, no improvements, no cleanup
- No "while I'm here" changes
- Document what the fix changes and why

### Step 2: Apply Fix

- Make the smallest possible change
- Single purpose — fix one thing
- No scope expansion

### Step 3: Verify Fix

- Reproduce original bug → confirm it's fixed
- Run existing tests → confirm no regression
- Check edge cases → confirm they're handled

## Bug Discovery Guardrail (CRITICAL)

**⚠️ Finding a bug during diagnosis does NOT authorize fixing it.**

This skill handles diagnosis (read-only). Fixing requires separate authorization.

### Authorization Check Before Fix

Before applying ANY fix (`--task fix`):

1. **Check authorization**: Was this bug explicitly authorized for fixing?
   - Does an approved spec issue exist for this fix?
   - Did the user explicitly say "approved" or "go" for this fix?
2. **If NO authorization**: HALT immediately after diagnosis
   - Report findings to the bug issue
   - Do NOT apply any code changes
   - Wait for explicit authorization

### Bug Discovery During Other Work

When the `diagnose` task is triggered as a side-effect of other work (not an explicit "debug this" request):

1. **STOP all code changes** — diagnosis is read-only
2. **Complete diagnosis** — identify root cause
3. **Create bug report** — file a GitHub/GitBucket issue
4. **HALT** — do NOT proceed to `--task fix` without explicit authorization

### Self-Correction Protocol

If the agent catches itself about to edit code without an approved spec:

1. **STOP** — do not proceed with the edit
2. **REVERT** — `git checkout -- <affected-files>` to undo unauthorized changes
3. **REPORT** — document what happened as a factual observation
4. **HALT** — wait for explicit authorization

**See `000-critical-rules.md` → "Bug Discovery Does NOT Authorize Bug Fixing" for the complete authorization matrix.**

## Enforcement Mechanism

**⚠️ CRITICAL: Debugging MUST be systematic — no random code changes.**

### Enforcement Matrix

| Situation | Action |
|-----------|--------|
| Bug reported, no diagnosis | REQUIRE diagnosis first |
| Diagnosis incomplete | COMPLETE diagnosis before fix |
| Fix targets symptoms, not root cause | REJECT fix, require root cause fix |
| Fix includes unrelated changes | REJECT scope creep |
| Fix is refactoring disguised as bug fix | REJECT, require spec |

### What Skills MUST Check

1. **Before any fix:**
   - Has diagnosis been performed?
   - Is root cause identified with evidence?
   - Is the fix minimal and targeted?

2. **During fix:**
   - Is fix ONLY addressing root cause?
   - Are there unrelated changes?
   - Is the fix larger than necessary?

## Anti-Patterns

### 🚫 Vibe Debugging

```python
# ❌ WRONG: Random changes without diagnosis
# "Maybe this will fix it..."
result = some_function(timeout=30)  # Changed timeout
# Still broken? Try changing something else...
result = some_function(timeout=60, retries=3)  # Random parameter tweaks
```

### ✅ Systematic Debugging

```python
# ✅ CORRECT: Diagnose first
# Hypothesis 1: Timeout too short → Test: Log actual execution time
# Evidence: Function completes in 2 seconds, timeout is 30 seconds
# Hypothesis 1 REJECTED — timeout is not the issue

# Hypothesis 2: Response parsing fails on large payloads → Test: Log response size
# Evidence: Response is 15MB, parser fails at 10MB threshold
# Hypothesis 2 CONFIRMED — root cause is parser size limit

# Fix: Increase parser size limit (minimal fix)
```

## Integration with Existing Workflow

### Dispatch Order

```
Bug reported → systematic-debugging (diagnose) → systematic-debugging (fix) → verification-before-completion
```

### GitBucket Platform Adaptations

- Post diagnosis to bug issue as comment
- Post fix summary to bug issue as comment
- Link fix commit to bug issue

### Approval Gate Integration

- Bug diagnosis does NOT require approval (read-only analysis)
- Bug FIX requires approval (code change)
- Create spec for fix if change is non-trivial

## Cross-References

- Related skills: `verification-before-completion` (evidence), `approval-gate` (authorization), `git-workflow` (branch)
- Related guidelines: `050-scope-autonomy.md` (no vibe coding), `090-data-integrity.md` (no synthetic data)

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill (MCP tools removed)
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable

## Source Attribution

This skill is adapted from the <UPSTREAM_ORG>/<UPSTREAM_REPO> repository (branch: newsrx). The original workflow enforces systematic debugging to prevent random code changes and ensure root cause fixes.

**Key adaptations for OpenCode:**
- Integration with existing approval-gate and git-workflow skills
- GitBucket platform support via MCP tools
- Dispatch table integration for automatic invocation
- Diagnosis-first enforcement with hypothesis testing