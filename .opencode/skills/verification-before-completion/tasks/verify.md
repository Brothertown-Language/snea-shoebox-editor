# Task: verify

Verify all success criteria have evidence before allowing completion claims.

## Prerequisites

- Task or phase claimed complete
- Plan issue has success criteria defined
- Evidence collection may still be pending

## Verification Workflow

### 1. Query Success Criteria

- Read plan issue for defined success criteria
- Parse each criterion as a testable statement
- Identify evidence needed for each

### 2. Check for Evidence

- Review issue comments for evidence
- Check `./tmp/` for artifacts
- Verify evidence matches criteria

### 3. Mark Verified/Unverified

```markdown
## Success Criteria Verification

1. ✅ [Criterion] - EVIDENCE: [Link/output]
2. ✅ [Criterion] - EVIDENCE: [Link/output]
3. ❌ [Criterion] - MISSING EVIDENCE
```

### 4. Report Status

- If all verified → Allow completion claim
- If any unverified → HALT and require evidence

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
🤖 OpenCode (ollama-cloud/glm-5) verification
```

## Post-Verification Chain

After verification passes, the following skills MUST be invoked in sequence:

1. **finishing-a-development-branch --task checklist** — Branch readiness verification
2. **git-workflow --task review-prep** — Push verification, compare URL, chat output

These are NOT optional. Verification passing triggers the chain:
`verify` → `finishing-a-development-branch --task checklist` → `git-workflow --task review-prep`

If verification fails, HALT — do NOT proceed to the chain.

## Enforcement

### What Skills MUST Check

1. Before marking complete:
   - Are ALL success criteria defined?
   - Do ALL criteria have evidence?
   - Is evidence verifiable?

2. Enforcement matrix:
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