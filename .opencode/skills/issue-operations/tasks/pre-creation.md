# Task: pre-creation

## Purpose

Validate spec before creating GitHub Issue to prevent conflicts, superseded issues, and missing essential content.

## Operating Protocol

1. **Mandatory invocation:** This task MUST run before ANY issue creation.

## Entry Criteria

- Spec content is ready for issue creation
- Title follows proper format
- User has authorized creation

## Exit Criteria

- Spec validated (no conflicts, no superseded issues)
- Essential content coverage confirmed
- Ready to create issue

## Procedure

### Step 1: Check for Superseding Issues and Overlap

**Query for all open `[SPEC]`, `[SPEC-FIX]`, and `[SPEC-ENHANCEMENT]` issues:**

```
github_list_issues(owner, repo, state="open")
```

For each open spec issue, perform overlap analysis at three levels:

#### 1a: Title/Objective Overlap (Quick Filter)

Compare title and objectives with the new spec title. This is a fast initial filter.

#### 1b: File/Symbol/Concern-Level Overlap (Mandatory Deep Analysis)

For specs that pass the quick filter, extract and compare:

- **File references:** Extract file paths from affected-files, file_references, or code path sections
- **Symbol references:** Extract function, class, and module names referenced in the spec body
- **Concern boundaries:** Extract the concern area each phase addresses (what problem each phase solves)

Use `srclight_get_dependents` or `srclight_get_callers` where possible to verify actual dependencies overlap, not just spec-claimed overlap.

#### 1c: Classify Overlap Using Four-Tier Model

| Classification | Criteria | Pre-creation Action |
|---------------|----------|-------------------|
| **FULL-SUPERSESSION** | Existing spec B's scope entirely covers the new spec's scope (B's files ⊇ new files, B's concerns ⊇ new concerns, all new success criteria ⊇ B's) | **BLOCK creation** — HALT and report: "Existing spec #N fully covers this scope. Use that spec instead of creating a new one." |
| **PARTIAL-OVERLAP** | Existing spec shares file_references or symbol_references with the new spec, but has different core concerns | **Surface to user** — Report: "Spec #N partially overlaps — shared files: [list]. Consider scoping the new spec to avoid overlap." |
| **CONFLICT-RISK** | Existing spec modifies same files in conflicting ways (different intent for same code) | **Surface to user** — Report: "Spec #N conflicts on [files]. Coordinate before creating." |
| **INDEPENDENT** | No meaningful overlap in files, symbols, or concerns | **Proceed** — No action needed |

**Evidence artifacts (MANDATORY):**

```
Check: [existing spec #N overlap with new spec]
Tool: github_issue_read(method=get, issue_number=N) + srclight_get_dependents/srclight_get_callers
Result: [shared files, shared symbols, overlap classification]
Classification: [FULL-SUPERSESSION|PARTIAL-OVERLAP|CONFLICT-RISK|INDEPENDENT]
Action: [BLOCK|surface|surface|proceed]
```

**Key change from previous behavior:** Title/objective overlap alone is insufficient. File, symbol, and concern-level analysis MUST be performed before classifying overlap. The four-tier model (FULL-SUPERSESSION, PARTIAL-OVERLAP, CONFLICT-RISK, INDEPENDENT) replaces the previous binary overlap/superseded classification.

For each open spec issue:
1. Compare file references, symbol references, and concern boundaries with new spec
2. If FULL-SUPERSESSION found:
   - HALT
   - Report: "Existing spec #N fully covers this scope" with overlapping file/symbol/concern evidence
   - Do NOT proceed with creation — recommend using the existing spec
3. If PARTIAL-OVERLAP found:
   - WARN
   - Report: "Spec #N partially overlaps — shared files: [list], shared symbols: [list]"
   - Suggest resolution: scope the new spec to avoid overlapping concerns
4. If CONFLICT-RISK found:
   - HALT
   - Report: "Spec #N conflicts on [files/symbols] with different intent"
   - Suggest resolution: coordinate before creating

### Step 2: Check for Staleness

**If existing open specs:**
1. Check if any were implemented but left open
2. Check if referenced code locations have changed
3. Check if problem statement still applies

**If stale:**
1. HALT
2. Suggest updating or closing stale spec first

### Step 3: Validate Spec Content Coverage

**Ensure essential content is present, regardless of section header names.**

The check is content-coverage, not structural conformity. A spec that covers all required concerns under different section names passes. A spec with the exact "correct" headers but missing content fails.

| Content Area | What to Check |
|-------------|---------------|
| Problem description | Does the spec describe what problem it solves and why it matters? |
| Context | Does the spec provide enough background for a fresh agent to understand? |
| Success criteria | Does the spec include testable, binary pass/fail completion criteria? |

**Content coverage check examples:**

- A spec with "Background", "The Issue", "How We Know It Works" passes ✅ (covers problem, context, criteria)
- A spec with "Problem Statement", "Context", "Success Criteria" passes ✅ (covers problem, context, criteria)
- A spec with "Problem Statement" header but empty content fails ❌ (missing actual content)
- A spec with no problem description but a detailed implementation plan fails ❌ (what problem is it solving?)

**If content coverage is missing:**
1. HALT
2. Report missing content areas (not missing headers, missing *content*)
3. Do NOT proceed with creation

### Step 3.5: Check for Duplicate Plans

**Before creating any plan issue, check whether an existing plan already references the same spec.** This mirrors the duplicate plan check in `writing-plans/tasks/create.md` Step 1.6 and ensures that even when plan creation is invoked via a different path, the duplication check is performed.

1. Using `github_search_issues`, search for issues labeled `plan` in the repository:
   ```
   github_search_issues(query="label:plan", owner=<github.owner>, repo=<github.repo>, state="open")
   ```
2. Filter results for those whose body contains `Spec: #<spec_number>` referencing the spec that will be planned.
3. If one or more existing plans are found:
   - Collect each existing plan's issue number, title, and URL
   - Read each existing plan's body to extract its phase scope
   - Present the overlap to the developer in chat: list each existing plan with its URL and a scope summary
   - Offer the developer a choice:
     - **"proceed with new plan (will add reference to existing plan)"** — continue creation, adding `Supersedes/replaces #N` or `Parallel track to #N` in the new plan body
     - **"halt and review existing plan first"** — HALT and present the existing plan for review
4. If no existing plans are found for the same spec, proceed without modification.

### Step 4: Report Validation Result

**If all checks pass:**
- Report: "Pre-creation validation passed. Ready to create issue."
- Proceed to `single-task-check` task

**If ANY check fails:**
- HALT
- Report specific failure
- Do NOT proceed with creation

## Common Issues

| Issue | Resolution |
|-------|------------|
| Superseding spec found (FULL-SUPERSESSION) | HALT, report full scope overlap, recommend using existing spec |
| Partially overlapping spec found (PARTIAL-OVERLAP) | WARN, report shared files/symbols/concerns, suggest scoping to avoid overlap |
| Conflicting spec found (CONFLICT-RISK) | HALT, report conflicting intent, suggest coordination |
| Missing content coverage | HALT, require spec update before creation |
| Stale open spec detected | HALT, suggest updating or closing stale spec |

## Safety Checks

Before proceeding, verify ALL:

- No superseding issues exist
- No conflicting specs exist
- Essential content coverage is present (problem, context, success criteria)
- Spec is not stale

**If ANY check fails → HALT and report.**

## Example: Content Coverage Check

**New Spec:** "Add rate limiting to API endpoints"

**Check:** Content coverage
- Problem described? Yes — "API calls average 150ms, causing slow page loads"
- Context provided? Yes — "Current queries hit DB directly, 85% cache hit potential"
- Success criteria testable? Yes — "API response <20ms for cached queries, >80% cache hit rate"

**Result:** PASS. Content coverage is sufficient regardless of section headers.

**New Spec:** "Improve the API"

**Check:** Content coverage
- Problem described? No — "improve" is vague, no measurable problem stated
- Context provided? No — no background on what's wrong
- Success criteria testable? No — "better API" is not testable

**Result:** FAIL. Missing content coverage, not missing headers.

## Live Verification: Staleness Checks (MANDATORY)

**🚫 CRITICAL: Each staleness check in Steps 1-2 MUST verify against live GitHub and codebase state. Staleness assertions without live verification are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Staleness Claim | Verification Action | Tool Call | Problem Class |
|-----------------|-------------------|-----------|---------------|
| "Spec may be implemented but left open" | Verify referenced code exists and matches spec claims | `srclight_get_symbol(name="symbol")` or `glob(pattern="**/file")` | VERIFICATION-GAP |
| "Referenced code locations changed" | Verify file paths and symbols still exist as referenced | `srclight_get_symbol(name="symbol")` → confirm location | CONFLICTING |
| "Problem statement still applies" | Verify the original problem is not resolved | `github_issue_read(method=get_comments)` → check for resolution comments | VERIFICATION-GAP |
| "Superseding issue found" | Verify superseding issue actually supersedes (compare objectives) | `github_issue_read(method=get, issue_number=N)` → compare objectives | CONFLICTING |

**Evidence format:**

```
Check: [what was verified]
Tool: [tool call and parameters]
Result: [actual state found]
Classification: [STRUCTURE-VIOLATION|MISSING-ELEMENT|CONFLICTING|VERIFICATION-GAP|MISSING-TRACEABILITY]
Action: [auto-fix|conditional|flag-for-review]
```

**Classification on failure:**

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Spec claimed implemented but code not found | VERIFICATION-GAP | conditional | Verify with broader search before marking stale |
| Code location changed | CONFLICTING | auto-fix | Update spec reference to new location |
| Problem already resolved | VERIFICATION-GAP | auto-fix | Mark spec as resolved, suggest closure |
| Superseding issue not actually related | CONFLICTING | flag-for-review | HALT — do not block creation incorrectly |

## Context Required

- Related tasks: `creation` (create after validation)
- Related skills: `concern-separation-auditor`, `spec-auditor` (auditors invoked later)