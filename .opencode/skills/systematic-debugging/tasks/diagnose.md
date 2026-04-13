# Task: diagnose

## Purpose

Systematic bug diagnosis workflow that enforces root cause analysis before any fix is attempted. Diagnosis is read-only.

## Operating Protocol

1. Invoked by: `/skill systematic-debugging --task diagnose`
2. When to use: When a bug or error is reported or encountered during implementation
3. Exit criteria: Root cause identified with evidence, documented in chat

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

## Bug Discovery Guardrail

**⚠️ Finding a bug during diagnosis does NOT authorize fixing it.**

Diagnosis is read-only. Fixing requires separate authorization.

When diagnosis is triggered as a side-effect of other work:
1. **STOP all code changes** — diagnosis is read-only
2. **Complete diagnosis** — identify root cause
3. **Create bug report** — file a GitHub/GitBucket issue
4. **Invoke `analyze-and-spec`** — `/skill issue-review --issue N --task analyze-and-spec` to create fix spec sub-issue
5. **HALT** — do NOT proceed to `--task fix` without explicit authorization

### Self-Correction Protocol

If the agent catches itself about to edit code without an approved spec:
1. **STOP** — do not proceed with the edit
2. **REVERT** — `git checkout -- <affected-files>` to undo unauthorized changes
3. **REPORT** — document what happened as a factual observation
4. **HALT** — wait for explicit authorization

## Context Required

- Related skills: `systematic-debugging` (parent skill), `approval-gate` (authorization), `issue-review` (analyze-and-spec task for fix spec creation)
- Related tasks: `fix`