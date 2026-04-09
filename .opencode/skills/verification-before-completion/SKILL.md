---
name: verification-before-completion
description: Use when claiming a task is complete, marking a step done, or closing an issue. Triggers on: task complete, done, finished, step complete, mark done, verify completion, success criteria.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: verification-before-completion

## Overview

Evidence-based verification workflow that prevents premature completion claims. This skill ensures ALL success criteria are verified with actual evidence before ANY task or phase is marked complete. It is adapted from the NewsRx/opencode-gitbucket-superpowers workflow.

**Source Attribution:** This skill is adapted from NewsRx/opencode-gitbucket-superpowers workflow (branch: newsrx).

## Persona

You are a Verification Gatekeeper. Your focus is ensuring NO completion claim without verified evidence.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `verify` | Verify all success criteria have evidence | ~800 |
| `collect` | Collect evidence for incomplete criteria | ~700 |

## Invocation

- `/skill verification-before-completion` - Overview only
- `/skill verification-before-completion --task verify` - Verify completion readiness
- `/skill verification-before-completion --task collect` - Collect missing evidence

## Operating Protocol

1. **Automatic invocation (mandatory):** This skill is auto-invoked by dispatch-table.yaml when:
   - Agent claims "task complete" or "step complete"
   - Agent marks step as ☑ in plan
   - Agent attempts to close issue or create PR
   - DO NOT allow completion claims without evidence

2. **Evidence Requirements:**
   - Every success criterion must have evidence
   - Evidence must be verifiable (logs, test outputs, screenshots)
   - Evidence must be posted to issue or in `./tmp/`
   - No placeholders or "trust me" claims

3. **Exit conditions:** Verification is COMPLETE when:
   - All success criteria have evidence
   - Evidence is posted to plan issue or stored in `./tmp/`
   - HALT and report verification results

## Verification Workflow

### Prerequisites
- Task or phase claimed complete
- Plan issue has success criteria defined
- Evidence collection may still be pending

### Verify Completion

1. **Query success criteria:**
   - Read plan issue for defined success criteria
   - Parse each criterion as testable statement
   - Identify evidence needed for each

2. **Check for evidence:**
   - Review issue comments for evidence
   - Check `./tmp/` for artifacts
   - Verify evidence matches criteria

3. **Mark verified/unverified:**
   ```markdown
   ## Success Criteria Verification

   1. ✅ [Criterion] - EVIDENCE: [Link/output]
   2. ✅ [Criterion] - EVIDENCE: [Link/output]
   3. ❌ [Criterion] - MISSING EVIDENCE
   ```

4. **Report status:**
   - If all verified → Allow completion claim
   - If any unverified → HALT and require evidence

### Evidence Collection

For each missing criterion:

1. **Identify what evidence is needed:**
   - Test output? → Run test, capture output
   - File creation? → Show file path and content hash
   - Code change? → Show `git diff` output
   - API response? → Show status code and body

2. **Collect evidence:**
   - Run required verification commands
   - Store output in `./tmp/` or post to issue
   - Verify evidence is complete and accurate

3. **Update verification status:**
   - Mark criterion as verified
   - Post evidence to issue
   - Proceed to next missing criterion

## Evidence Types

### Valid Evidence

| Type | Description | Storage |
|------|-------------|---------|
| Test output | `pytest` pass/fail | Issue comment |
| Lint output | `ruff check` clean | Issue comment |
| Type check | `pyright` clean | Issue comment |
| File path | Created file exists | Issue comment + `ls -la` |
| File content | File content hash | Issue comment + `head -20` |
| Git diff | Code changes | Issue comment + `git diff` |
| API response | Status code and body | Issue comment + curl output |
| Screenshot | Visual verification | Issue comment + attachment |

### Invalid Evidence

| Type | Why Invalid |
|------|-------------|
| "Trust me" | No verification |
| "It should work" | Assumption, not proof |
| "I checked" | No artifact |
| "Code is correct" | No test run |
| Placeholder text | "TBD" or "TODO" |

## Verification Report Format

```markdown
## Verification Report

**Task:** [Task description]
**Plan Issue:** #N

### Success Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| ✅ Test passed | ✅ VERIFIED | `pytest test/x.py` output |
| ✅ Lint clean | ✅ VERIFIED | `ruff check src/` output |
| ✅ File created | ❌ MISSING | Need: `ls -la path/to/file` |

### Missing Evidence

1. **File created**: Need to verify file exists
   - Expected: `ls -la path/to/file`
   - Current: No evidence provided

### Required Actions

- [ ] Provide evidence for missing criteria
- [ ] Re-run verification after evidence added

---
🤖 🔍 Verification by OpenCode (ollama-cloud/glm-5)
```

## Enforcement Mechanism

**⚠️ CRITICAL: Skills MUST enforce evidence before completion — guidelines alone are insufficient.**

### What Skills MUST Check

1. **Before marking complete:**
   - Are ALL success criteria defined?
   - Do ALL criteria have evidence?
   - Is evidence verifiable?

2. **Enforcement matrix:**
   - All criteria verified → ALLOW completion claim
   - Some criteria unverified → HALT, require evidence
   - No criteria defined → HALT, require success criteria
   - Evidence placeholder → HALT, require real evidence

### Enforcement Messages

**Missing evidence:**
```
Completion claim rejected. Evidence missing for:

- [ ] Success criterion: "[Criterion description]"
- [ ] Expected: [What evidence to provide]
- [ ] Current: [What evidence exists]

Please provide evidence before claiming completion.
```

**Success criteria undefined:**
```
Cannot verify completion. Success criteria not defined.

Task: [Task description]
Plan Issue: #N

Please define success criteria in the plan before execution.
```

**Evidence placeholder:**
```
Evidence placeholder detected. Real evidence required.

- [ ] Placeholder: "TBD" or "TODO"
- [ ] Expected: Verifiable test output, file path, or code diff

Please replace placeholder with actual evidence.
```

## Integration with Existing Workflow

### Dispatch Order
```
executing-plans → verification-before-completion → (completion claim allowed)
```

### GitBucket Platform Adaptations
- Post verification reports to plan issue
- Store large artifacts in `./tmp/`
- Link evidence to plan via comments

### Git-Workflow Integration
- Verification happens BEFORE branch push
- Evidence collected during execution phase
- PR created only after all verification passes

## Common Verification Commands

### Code Changes

```bash
# Show changed files
git diff --name-only

# Show changed content
git diff

# Show staged changes
git diff --cached
```

### Test Verification

```bash
# Run specific test
uv run pytest test/test_file.py::test_function_name

# Run with coverage
uv run pytest --cov=src/module test/
```

### Code Quality

```bash
# Lint check
uv run ruff check --fix src/ test/

# Format check
uv run ruff format src/ test/

# Type check
uv run pyright src/
```

### File Verification

```bash
# File exists
ls -la path/to/file

# File content preview
head -20 path/to/file

# File hash
md5sum path/to/file
```

## Cross-References

- Related skills: `executing-plans` (implementation), `git-workflow` (branch push), `approval-gate` (authorization)
- Related guidelines: `000-critical-rules.md` (evidence requirements), `142-planning-archive-workflow.md` (success criteria)

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill (MCP tools removed)
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable

## Source Attribution

This skill is adapted from the NewsRx/opencode-gitbucket-superpowers repository (branch: newsrx). The original workflow enforces evidence-based verification to prevent premature completion claims.

**Key adaptations for OpenCode:**
- Integration with existing executing-plans and git-workflow skills
- GitBucket platform support via MCP tools
- Dispatch table integration for automatic invocation
- Structured evidence collection and verification gates