# Task: step

Execute a single step from the plan, collect evidence, and report progress.

## Step Execution Process

For each step in the plan:

### 1. Read Step Content

- Parse step from plan issue
- Identify specific tasks
- Identify verification method

### 2. Execute Tasks

- Perform implementation actions
- Collect evidence (logs, outputs, test results)
- Run static analysis (lint, typecheck)

### 3. Verify Step

- Run step verification method
- Check all evidence collected
- Update step status to ☑

### 4. Report Progress

Report step completion to chat:

```markdown
**Progress:** Step N of M complete

**Evidence:**
- [Task 1]: [Evidence]
- [Task 2]: [Evidence]
- Verification: [Result]

**Next:** Step N+1 - [Next concern]
```

- Update STATUS in plan issue body
- HALT and wait for user

### 5. Proceed to Next

- User says `next step` → Continue to next step
- User says `continue` → Continue to next step
- All steps done → Transition to verification

## Evidence Collection

| Evidence Type | Collection Method |
|---------------|-------------------|
| Code changes | `git diff` output |
| Test results | Test pass/fail output |
| Lint check | `ruff check` output |
| Type check | `pyright` output |
| File creation | Path and content hash |
| API response | Status code and body |

**Evidence storage:**
- Store artifacts in `./tmp/`
- Report evidence to chat

## Enforcement

During execution:
- Is evidence collected for each task?
- Is verification run for each step?
- Is progress reported to chat?

Evidence missing for task → REQUIRE evidence before marking complete.
Verification not run → RUN verification before marking complete.

### Enforcement Messages

**Missing evidence:**

```
Step verification requires evidence.

Task: [Task description]
Expected evidence: [What to collect]

Please provide evidence before marking step complete.
```

**Verification failed:**

```
Step verification failed.

Verification: [Verification method]
Result: [Failure output]

Fix issues before marking step complete.
```