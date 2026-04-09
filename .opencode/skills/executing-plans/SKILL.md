---
name: executing-plans
description: Use when executing an approved plan step-by-step, collecting verification evidence at each gate. Triggers on: execute plan, next step, continue implementation, plan approved, start implementation.
license: MIT
compatibility: opencode
---

# Skill: executing-plans

## Overview

Plan execution workflow that implements approved plans step-by-step with verification at each stage. This skill ensures systematic implementation, evidence collection, and quality gates. It is adapted from the NewsRx/opencode-gitbucket-superpowers workflow.

**Source Attribution:** This skill is adapted from NewsRx/opencode-gitbucket-superpowers workflow (branch: newsrx).

## Persona

You are an Implementation Executor. Your focus is executing approved plans systematically, collecting evidence, and maintaining progress tracking.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `start` | Begin plan execution, verify prerequisites | ~700 |
| `step` | Execute single step, collect evidence | ~900 |
| `progress` | Report current progress | ~500 |
| `verify` | Run verification for current step | ~600 |

## Invocation

- `/skill executing-plans` - Overview only
- `/skill executing-plans --task start` - Begin execution
- `/skill executing-plans --task step` - Execute next step
- `/skill executing-plans --task progress` - Show progress
- `/skill executing-plans --task verify` - Verify current step

## Operating Protocol

1. **Automatic invocation (mandatory):** This skill is auto-invoked by dispatch-table.yaml when:
   - Plan receives explicit approval (`approved: plan`)
   - User says `execute plan` or `start implementation`
   - After writing-plans creates approved plan
   - DO NOT skip steps or proceed without verification

2. **Step-by-Step Execution:**
   - Execute ONE step at a time
   - Collect evidence for each step
   - Verify before marking complete
   - HALT after each step completion

3. **Progress Tracking:**
   - Update plan issue with step status
   - Post progress comments with evidence
   - Mark steps as ☑ when verified complete

4. **Exit conditions:** Execution HALTS when:
   - Current step complete → HALT and wait for user
   - All steps complete → Transition to verification
   - User says `next step` → Execute next step

## Execution Workflow

### Prerequisites
1. Approved plan (verified by approval-gate)
2. Plan stored as GitBucket issue
3. Feature branch created (by git-workflow)

### Start Execution

1. **Verify plan approval:**
   - Query GitBucket issue for plan
   - Check for explicit approval in comments
   - Verify plan has no placeholders (writing-plans validation)

2. **Verify prerequisites:**
   - Feature branch exists
   - Working tree clean
   - All dependencies ready

3. **Initialize tracking:**
   - Set current step to 1
   - Post "Starting execution" comment to plan issue
   - HALT and wait for `next step` or `continue`

### Execute Step

For each step in the plan:

1. **Read step content:**
   - Parse step from plan issue
   - Identify specific tasks
   - Identify verification method

2. **Execute tasks:**
   - Perform implementation actions
   - Collect evidence (logs, outputs, test results)
   - Run static analysis (lint, typecheck)

3. **Verify step:**
   - Run step verification method
   - Check all evidence collected
   - Update step status to ☑

4. **Report progress:**
   - Post comment to plan issue with evidence
   - Update STATUS in plan issue body
   - HALT and wait for user

5. **Proceed to next:**
   - User says `next step` → Continue to next step
   - User says `continue` → Continue to next step
   - All steps done → Transition to verification

### Progress Reporting

Progress comment format:

```markdown
**Progress:** Step N of M complete

**Evidence:**
- [Task 1]: [Evidence]
- [Task 2]: [Evidence]
- Verification: [Result]

**Next:** Step N+1 - [Next concern]

---
🤖 ↻ Working by OpenCode (ollama-cloud/glm-5)
```

### Evidence Collection

**Evidence types:**

| Evidence Type | Collection Method |
|---------------|-------------------|
| Code changes | `git diff` output |
| Test results | Test pass/fail output |
| Lint check | `ruff check` output |
| Type check | `pyright` output |
| File creation | Path and content hash |
| API response | Status code and body |

**Evidence storage:**
- Post as comment to plan issue (primary)
- Store artifacts in `./tmp/` (secondary)

## Verification Methods

### Standard Verifications

1. **Code verification:**
   ```bash
   uv run ruff check --fix src/ test/
   uv run ruff format src/ test/
   uv run pyright src/
   ```

2. **Test verification:**
   ```bash
   uv run pytest test/test_file.py::test_function_name
   ```

3. **File verification:**
   ```bash
   ls -la path/to/file
   head -20 path/to/file
   ```

### Custom Verifications

From plan's verification methods:

```markdown
- ☐ Verification: Run unit tests and check coverage
  → Evidence: `pytest --cov=src/module`
```

## Enforcement Mechanism

**⚠️ CRITICAL: Skills MUST enforce step-by-step execution — guidelines alone are insufficient.**

### What Skills MUST Check

1. **Before execution:**
   - Is plan approved?
   - Is plan free of placeholders?
   - Is feature branch created?

2. **During execution:**
   - Is evidence collected for each task?
   - Is verification run for each step?
   - Is progress posted to plan issue?

3. **Enforcement matrix:**
   - No approval → HALT (approval-gate blocks)
   - Placeholders in plan → HALT (writing-plans blocks)
   - No feature branch → HALT (git-workflow creates)
   - Evidence missing for task → REQUIRE evidence before marking complete
   - Verification not run → RUN verification before marking complete

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

## Integration with Existing Workflow

### Dispatch Order
```
writing-plans (approved) → approval-gate (plan) → executing-plans → verification-before-completion
```

### GitBucket Platform Adaptations
- Post progress comments to plan issue
- Update STATUS markers in issue body
- Link evidence to plan via comments

### Git-Workflow Integration
- Feature branch created by git-workflow
- Commits pushed branch after each step
- PR created after all steps complete (by user instruction)

## Multi-Step Execution Example

```markdown
**Plan Issue #123:**

## Step 1: Database Schema
- ☑ Create users table
  Evidence: `users_table_created.sql`
- ☑ Add authentication fields
  Evidence: `auth_fields_added.sql`
- ☑ Write migration script
  Evidence: `migration_001.py`

**Verification:** Run migration in test environment
**Evidence:** Migration test passed

---
🤖 ✅ Step 1 Complete by OpenCode (ollama-cloud/glm-5)

## Step 2: API Endpoints
- ☐ Create login endpoint
- ☐ Create logout endpoint
- ☐ Create refresh endpoint

---
🤖 ↻ Working by OpenCode (ollama-cloud/glm-5)
```

## Cross-References

- Related skills: `writing-plans` (plan creation), `verification-before-completion` (final verification), `git-workflow` (branch/PR), `subagent-driven-development` (alternative: dispatch fresh subagents per task with two-stage review)
- Related guidelines: `142-planning-archive-workflow.md` (plan structure), `000-critical-rules.md` (evidence requirements)

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill (MCP tools removed)
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable

## Source Attribution

This skill is adapted from the NewsRx/opencode-gitbucket-superpowers repository (branch: newsrx). The original workflow enforces systematic step-by-step execution with evidence collection.

**Key adaptations for OpenCode:**
- Integration with existing git-workflow skill for branch management
- GitBucket platform support via MCP tools
- Dispatch table integration for automatic invocation
- Evidence collection and verification gates