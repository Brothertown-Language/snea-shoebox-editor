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

### 2a. Todowrite Cleanup Verification

- Verify no stale todowrite items remain (`pending` or `in_progress`)
- If todowrite was used during the session, confirm `todowrite(todos=[])` was called before HALT
- Evidence: todowrite state is empty or all items are `completed`
- Failure: HALT and require todowrite cleanup before allowing completion

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
| -- | -- | -- |
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
| -- | -- |
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

🤖 <AgentName> (<ModelId>) ✅ completed
```

## Comparison Mode Enforcement (MANDATORY)

**🚫 CRITICAL: When verifying DNS records, configuration values, API responses, or infrastructure state, use `exact` comparison mode. Soft-passing a mismatch as "functionally equivalent" is a CRITICAL VIOLATION.**

### Verification Table Format (MANDATORY for External Verifications)

When verifying live values against specifications, use this row-by-row comparison table:

```markdown
| Field | Expected (from source) | Actual (live) | Result |
|-------|----------------------|---------------|--------|
| priority | 5 | 0 | ❌ FAIL |
| weight | 0 | 5 | ❌ FAIL |
| port | 443 | 443 | ✅ PASS |
| target | server.example.com | server.example.com | ✅ PASS |
```

### Prohibited Patterns

| Pattern | Why Prohibited |
| -- | -- |
| "Functionally equivalent" | Agent judgment substituting for spec compliance |
| "Minor difference" | "Close enough" is never a valid verification outcome |
| "Works the same" | Functional analysis is for design, not verification |
| Reporting swapped fields as PASS | Each field is independently compared |

### Enforcement Matrix

| Verification Type | Comparison Mode | Default | Override? |
| -- | -- | -- | -- |
| DNS records | Exact | Exact | Never |
| Configuration values | Exact | Exact | Never |
| API responses | Exact | Exact | Never |
| Infrastructure state | Exact | Exact | Never |
| Code behavior | Semantic (with justification) | Exact | Per-field justification required |
| File existence | Exact | Exact | Never |

## Per-SC Evidence Table (MANDATORY)

**🚫 CRITICAL: Before marking ANY task or phase complete, the agent MUST produce a per-SC evidence table with one row per success criterion from the corresponding spec. This table is the completion gate — no row may be skipped, and no row may show PASS without exact-match evidence.**

### Table Format

| SC ID | Success Criterion Text | Verification Command Run | Exact Output Observed | Pass/Fail |
| -- | -- | -- | -- | -- |
| SC-1 | \[criterion text\] | `command --flag` | \[exact output\] | PASS/FAIL/MISSING EVIDENCE |

### Mandatory Outcomes Per Row

| Outcome | Meaning | When Applied |
| -- | -- | -- |
| **PASS** | Exact match between observed output and literal SC text | Observed output character-for-character matches the SC's specified value |
| **FAIL** | Mismatch between observed output and literal SC text | Observed output differs from the SC's specified value in any way |
| **MISSING EVIDENCE** | No verification command was run for this SC | Agent skipped verification for this criterion |

### 🚫 FORBIDDEN Outcomes (Zero Tolerance)

| Pattern | Why FORBIDDEN |
| -- | -- |
| "functionally equivalent" | Agent judgment substituting for spec compliance |
| "close enough" | "Close enough" is never a valid verification outcome |
| "semantically similar" | Semantic analysis is for design, not verification |
| "works the same way" | Behavioral proximity is not spec compliance |
| PASS with caveat or footnote | A PASS with an asterisk is a FAIL |

**Any row using a FORBIDDEN outcome is automatically reclassified as FAIL. The agent cannot override this reclassification.**

### Enforcement

- All rows MUST show PASS before completion is allowed
- Any FAIL or MISSING EVIDENCE row blocks completion
- Agent MUST re-run the verification command for any FAIL row
- Agent MUST provide a verification command for any MISSING EVIDENCE row

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

## Live Verification: Completion Evidence Claims (MANDATORY)

**Each completion claim MUST be verified against live state — not assumed from checklist assertions. This extends `065-verification-honesty.md` to completion verification.**

| Claim | Verification Action | Tool Call | Problem Class |
| -- | -- | -- | -- |
| "Success criterion met" | Verify criterion against actual code/test output | `read` or `srclight_get_symbol` or test execution | VERIFICATION-GAP |
| "Test passing" | Run the actual test command | `uv run pytest test/test_file.py` | VERIFICATION-GAP |
| "Files modified as specified" | Verify file changes match spec | `git diff dev --name-only` → compare with spec | CONFLICTING |
| "No uncommitted changes" | Verify clean working tree | `git status --porcelain` | VERIFICATION-GAP |
| "Branch pushed to remote" | Verify tracking branch exists | `git branch -vv` → check `[origin/<branch>]` | MISSING-ELEMENT |
| "Evidence artifact produced" | Verify tool call exists for each criterion | Check tool-call records in context | MISSING-ELEMENT |

**Evidence artifact:** Each verification check MUST produce a tool-call result. Assertions without tool-call artifacts are VERIFICATION-GAP findings.

### Finding Classification

| Finding | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Criterion claimed met without evidence | VERIFICATION-GAP | conditional | Re-verify with actual tool call |
| Test not actually passing | CONFLICTING | flag-for-review | HALT — fix test before claiming completion |
| Files differ from spec | CONFLICTING | flag-for-review | Report — scope may have deviated |
| Uncommitted changes exist | VERIFICATION-GAP | conditional | Commit before proceeding |
| Branch not pushed | MISSING-ELEMENT | auto-fix | Push immediately |
