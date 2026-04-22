# Task: fix

## Purpose

Apply a minimal targeted fix after diagnosis has confirmed the root cause. Requires separate authorization — diagnosis does not authorize fixes.

## Operating Protocol

1. Invoked by: `/skill systematic-debugging --task fix`
2. When to use: After `--task diagnose` has identified root cause AND user has explicitly authorized the fix
3. Exit criteria: Fix applied, verified, no regression introduced

## Authorization Check (CRITICAL)

Before applying ANY fix:

1. **Check authorization**: Was this bug explicitly authorized for fixing?
   - Does an approved spec issue exist for this fix?
   - Did the user explicitly say "approved" or "go" for this fix?
2. **If NO authorization**: HALT immediately
   - Report diagnosis findings
   - Do NOT apply any code changes
   - Wait for explicit authorization

## Fix Workflow

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

## Anti-Patterns

### 🚫 Vibe Debugging

```python
# ❌ WRONG: Random changes without diagnosis
# "Maybe this will fix it..."
result = some_function(timeout=30)
# Still broken? Try changing something else...
result = some_function(timeout=60, retries=3)
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

## Enforcement Matrix

| Situation | Action |
|-----------|--------|
| Bug reported, no diagnosis | REQUIRE diagnosis first |
| Diagnosis incomplete | COMPLETE diagnosis before fix |
| Fix targets symptoms, not root cause | REJECT fix, require root cause fix |
| Fix includes unrelated changes | REJECT scope creep |
| Fix is refactoring disguised as bug fix | REJECT, require spec |

## Context Required

- Related skills: `systematic-debugging` (parent skill), `approval-gate` (authorization)
- Related tasks: `diagnose`

## Live Verification: Fix Evidence Claims (MANDATORY)

**Each fix claim MUST be verified against actual test/code state. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Fix resolves root cause" | Verify fix targets identified root cause location | `srclight_get_symbol(name="target")` → confirm change location | VERIFICATION-GAP |
| "Tests pass after fix" | Run actual test suite | `uv run pytest test/` → check exit code | VERIFICATION-GAP |
| "No unrelated changes" | Verify diff scope matches fix spec | `git diff --name-only` → compare with spec file list | CONFLICTING |
| "Fix is minimal" | Verify no refactoring or enhancement included | `git diff dev` → check change scope | CONFLICTING |

**Evidence artifact:** Tool call results for each fix verification step.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Fix doesn't target root cause | VERIFICATION-GAP | flag-for-review | HALT — re-diagnose before fixing |
| Tests still failing | VERIFICATION-GAP | flag-for-review | Fix tests before claiming complete |
| Unrelated changes in diff | CONFLICTING | flag-for-review | Report scope deviation |
| Refactoring disguised as fix | CONFLICTING | flag-for-review | Revert and create spec |