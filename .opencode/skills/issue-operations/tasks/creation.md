# Task: creation

## Purpose

Create issue with proper title format, labels, and byline after validation passes. Routes to appropriate platform sub-skill.

## Operating Protocol

1. **Run after `pre-creation` validation passes.**
2. **DO NOT skip validation.**
3. **HALT if Step 0.5 dedup gate evidence is missing.**

## Entry Criteria

- Pre-creation validation passed
- Step 0.5 dedup gate evidence available (OR Step 0.75 runtime search fallback completed)
- Single-task vs multi-task determination complete
- User has authorized creation

## Exit Criteria

- Issue created via platform sub-skill
- `needs-approval` label applied
- Creation byline included in issue body footer
- Issue number available for sub-issue linking

## Procedure

### Step 0.5: Dedup Evidence Gate

**MANDATORY before proceeding to any creation step.**

Verify that the `pre-creation` task's Step 0.5 title dedup gate was executed. This step MUST produce evidence that dedup was performed before the creation API call is allowed.

**Required evidence (from `pre-creation` Step 0.5 output):**

```
Check: Title dedup gate for "<proposed title>"
Tool: github_search_issues / gitbucket-api issues
Result: [N candidates found, match levels classified]
Classification: [EXACT-DUPLICATE|NEAR-DUPLICATE|CLOSED-IN-ERROR|RELATED-BUT-DISTINCT|FALSE-POSITIVE]
Action: [auto-resolved strategy | proceed | HALT]
```

**Gate logic:**

| Evidence Present? | Result Classified Non-Duplicate? | Action |
|-------------------|----------------------------------|--------|
| Yes | Yes | Proceed to Step 1 |
| Yes | No (EXACT-DUPLICATE / NEAR-DUPLICATE) | HALT — do not create duplicate |
| No | — | Proceed to Step 0.75 (runtime search fallback) |

**If Step 0.5 evidence is missing and runtime search fallback (Step 0.75) also fails → HALT with:**

```
Cannot create issue: Step 0.5 dedup gate evidence missing. Run pre-creation task first.
```

### Step 0.75: Runtime Search Fallback

**When Step 0.5 evidence is unavailable, perform a lightweight dedup search before allowing creation.**

This fallback catches the scenario where `pre-creation` was not run or its output is not in the current session context.

1. Extract significant keywords from the proposed title (remove stop words, prefixes like `[SPEC]`, `[SPEC-FIX]`, `[Task:]`)
2. Search for existing issues via platform API:
   - **GitHub:** `github_search_issues(query="<keywords> repo:<owner>/<repo>", owner=<owner>, repo=<repo>)`
   - **GitBucket:** `./.opencode/tools/gitbucket-api issues --state open` + `--state closed` (filter client-side by keyword match)
3. Collect candidate matches (issues whose titles share ≥2 significant keywords with proposed title)
4. For each candidate, classify match level per `pre-creation.md` Step 0.5 Phase 2 classification table
5. If any EXACT-DUPLICATE or NEAR-DUPLICATE found → HALT, report conflict
6. If all candidates are RELATED-BUT-DISTINCT or FALSE-POSITIVE → generate runtime search evidence artifact, proceed to Step 1

**Evidence artifact (MANDATORY):**

```
Check: Runtime search fallback for "<proposed title>"
Tool: github_search_issues / gitbucket-api issues
Result: [N candidates found, match levels classified]
Classification: [EXACT-DUPLICATE|NEAR-DUPLICATE|CLOSED-IN-ERROR|RELATED-BUT-DISTINCT|FALSE-POSITIVE]
Action: [HALT | proceed with runtime evidence]
Fallthrough reason: Step 0.5 evidence unavailable
```

**If this fallback also fails (search API unavailable or returns error) → HALT with:**

```
Cannot create issue: Step 0.5 dedup gate evidence missing and runtime search fallback failed. Run pre-creation task first.
```

### Step 1: Determine Title Format

| Issue Type | Title Format | Example |
|------------|--------------|---------|
| Primary spec | `[SPEC] <Feature Name>` | `[SPEC] PubMed API Rate Limiting` |
| Bug fix | `[SPEC-FIX] <Bug Description>` | `[SPEC-FIX] Token Refresh Failure` |
| Enhancement | `[SPEC-ENHANCEMENT] <Enhancement>` | `[SPEC-ENHANCEMENT] Add Rate Limiting` |
| Task | `[Task: #<parent>] <Task Description>` | `[Task: #100] Create user tables` |

### Step 2: Create Issue (Platform Routing)

**GitHub platform:**
```python
github_issue_write(
    method="create",
    owner=owner,
    repo=repo,
    title=title,
    body=body,
    labels=["needs-approval"]
)
```

**GitBucket platform:**
```bash
./.opencode/tools/gitbucket-api create-issue <github.owner> <github.repo> "<title>" --body "<body>" --labels needs-approval
```

**Note (GitBucket):** Labels can ONLY be set during creation. Post-creation label changes do not work.

**Response includes:**
- `number`: Issue number (database ID)
- `id`: Database ID for sub-issue linking
- `html_url`: Issue URL

**Post-Creation URL Extraction (MANDATORY — per `000-critical-rules.md` §URL Sourcing):**

The Issue URL MUST be extracted from the API response `html_url` field — NEVER constructed from template variables:

1. After the creation API call, extract the `html_url` field from the response
2. Use this exact value as the Issue URL for all subsequent references (chat output, cross-references, sub-issue linking reports)
3. **Template construction is FORBIDDEN for post-creation URLs** — do NOT assemble from `<gitbucket.html_url>`, `<github.owner>`, `<github.repo>`, or issue number
4. If `html_url` is not available in the API response: HALT and report

### Step 3: Verify Byline in Issue Body

**The issue body must already include a byline footer** (added during spec drafting):

```
🤖 <AgentName> (<ModelId>) created
```

**No separate comment needed.** The byline is part of the issue body content, not a standalone comment.

### Step 4: Report Issue Created

Report: "Created issue #<number>. Next step: Invoke auditors before approval."

## Multi-Task Spec Handling

**If spec has multiple phases:**

1. After creating parent issue
2. Invoke `issue-operations --task link-sub-issue`
3. Create phase-level sub-issues
4. Link each via platform sub-skill (GitHub: `github_sub_issue_write(method="add")`; GitBucket: comment-based linking)

**Single-task exemption:**
- If spec has ONE task, skip sub-issue creation
- Apply `needs-approval` label
- Proceed to `post-creation` task

## Safety Checks

Before proceeding, verify ALL:

- Step 0.5 dedup evidence present OR Step 0.75 runtime search fallback completed
- Pre-creation validation passed
- Title follows proper format
- `needs-approval` label applied
- Creation byline in body footer

**If ANY check fails → HALT and report.**

## Context Required

- Related tasks: `pre-creation` (runs first), `post-creation` (runs next), `link-sub-issue` (sub-issue creation)
- Platform routing: `../platforms/github-mcp/` or `../platforms/gitbucket-api/`
- Label state machine: `141-planning-status-tracking.md §10` (add `needs-approval` on creation; GitHub `labels` parameter replaces all labels)

## Live Verification: Creation Evidence (MANDATORY)

**Each creation precondition MUST be verified via tool call. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Title dedup gate performed" | Verify dedup was run before creation | Check pre-creation output for Step 0.5 evidence; if missing, run Step 0.75 runtime search fallback | MISSING-ELEMENT → HALT |
| "Pre-creation validation passed" | Verify validation result exists | Check pre-creation output in session | MISSING-ELEMENT |
| "No conflicting spec exists" | Search for overlapping issues | `github_search_issues(query="label:spec <keyword>")` | CONFLICTING |
| "Title follows format" | Verify title prefix | Check `[SPEC]`, `[SPEC-FIX]`, `[SPEC-ENHANCEMENT]`, `[Task:` prefix | STRUCTURE-VIOLATION |
| "Issue was created" | Verify API response | Check `number` field in creation response | MISSING-ELEMENT |
| "`needs-approval` label applied" | Verify label on created issue | `github_issue_read(method="get_labels", issue_number=N)` | MISSING-ELEMENT |
| "Byline in body" | Verify byline present | Check issue body for `🤖` marker | STRUCTURE-VIOLATION |

**Evidence artifact:** Pre-creation result, creation API response, post-creation label check.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Step 0.5 dedup evidence missing | MISSING-ELEMENT | HALT | HALT — "Cannot create issue: Step 0.5 dedup gate evidence missing. Run pre-creation task first." |
| Step 0.75 runtime search found duplicate | CONFLICTING | HALT | HALT — report duplicate, do not create |
| Pre-creation not run | MISSING-ELEMENT | flag-for-review | HALT — run pre-creation first |
| Conflicting spec found | CONFLICTING | flag-for-review | HALT — report conflict |
| Wrong title format | STRUCTURE-VIOLATION | auto-fix | Correct title before creation |
| Creation API failed | MISSING-ELEMENT | flag-for-review | HALT — retry or report error |
| Label missing post-creation | MISSING-ELEMENT | auto-fix | Add label immediately |
| Byline missing | STRUCTURE-VIOLATION | auto-fix | Add byline to body |