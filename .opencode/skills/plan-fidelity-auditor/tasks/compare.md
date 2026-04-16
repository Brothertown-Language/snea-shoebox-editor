# Task: compare

## Purpose

Compare a clean-room plan against the existing spec plan at phase-level, step-level, and content-level.

## Procedure

### Step 1: Parse Both Plans

Parse the clean-room plan and the existing spec plan into structured data:
- Extract phases with names
- Extract steps within each phase
- Extract success criteria
- Extract affected files (if listed)

### Step 2: Phase-Level Comparison

For each clean-room phase:
1. Find semantic match in existing plan (or identify as missing)
2. For each existing plan phase, find semantic match in clean-room (or identify as extra)

Semantic matching examples:
- "User Schema" ↔ "Database Tables" → MATCH (same concept)
- "Authentication Setup" ↔ "OAuth2 Integration" → MATCH if OAuth2 is auth method
- "API Endpoints" ↔ "REST API" → MATCH (same concept)

### Step 3: Step-Level Comparison

For each matched phase pair:
1. Compare steps within the phase
2. Identify missing steps, extra steps, ordering differences

### Step 4: Content-Level Comparison

For matched phase pairs:
1. Compare approaches and strategies
2. Identify edge case coverage differences
3. Check for different implementation strategies

### Step 5: Classify Findings

| Finding Type | Severity | Description |
|-------------|----------|-------------|
| MISSING_PHASE | HIGH | Clean-room has phase not in original |
| EXTRA_PHASE | MEDIUM | Original has phase not in clean-room |
| MISSING_STEP | MEDIUM | Clean-room has step not in original |
| EXTRA_STEP | LOW | Original has step not in clean-room |
| APPROACH_DIFFERENCE | HIGH | Same goal, different implementation |
| MISSING_EDGE_CASE | MEDIUM | Clean-room covers edge case not in original |
| MISSING_FILE_REF | LOW | Clean-room identifies affected file not in original |
| ORDERING_DIFFERENCE | LOW | Steps in different order |
| SCOPE_EXPANSION | MEDIUM | Clean-room significantly larger than original |

## Yield-Back Context

Return structured comparison results:
```yaml
status: "success|failure"
findings: [...]
phases_compared: N
phases_matched: M
phases_missing: K
phases_extra: L
```

Co-authored with AI: <AI-Name> (<model-id>)

## Live Verification: Comparison Claims (MANDATORY)

**Each comparison finding MUST be verified against actual content. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Phase is missing from original" | Verify clean-room phase exists and original lacks it | `github_issue_read(method=get)` on both issues → search body | VERIFICATION-GAP |
| "Phase is extra in original" | Verify original plan has phase not derived from spec | `github_issue_read(method=get)` → compare with spec requirements | CONFLICTING |
| "Step differs from clean-room" | Verify both plan steps against actual code state | `srclight_search_symbols(query="step_target")` | VERIFICATION-GAP |
| "File reference is missing" | Verify referenced file exists in codebase | `glob(pattern="**/filepath")` | MISSING-TRACEABILITY |

**Evidence artifact:** Tool call results for each comparison finding claim.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Missing phase verified absent | VERIFICATION-GAP | flag-for-review | Report — original plan needs this phase |
| Extra phase found in spec but not clean-room | CONFLICTING | conditional | Verify spec alignment before reporting |
| File reference does not exist | MISSING-TRACEABILITY | flag-for-review | Developer must confirm |
| Comparison claim without evidence | VERIFICATION-GAP | conditional | Re-verify with tool calls |