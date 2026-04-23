# Task: post-implementation

## Purpose

Push feature branch, generate compare URL, and report completion for developer review.

## ⚠️ MANDATORY INVOCATION

**This task MUST be invoked after every implementation completes. There is NO decision point. The agent MUST call this explicitly — it is NOT auto-triggered.**

The sequence is:
1. Implementation complete → **MUST invoke post-implementation**
2. Branch pushed, compare URL generated → HALT
3. Wait for developer to say "create a PR"

**DO NOT skip this task after implementation. DO NOT ask the developer if they want review. Just push the branch.**

## Entry Criteria

- Implementation work complete
- All changes committed on feature branch
- Authorization scope verified

## Exit Criteria

- Feature branch pushed to remote
- GitHub compare URL generated
- Completion reported to issue (NO URL) and chat (with URL)
- HALT for developer review

## Procedure

### Step 1: Determine Implementation Outcome

**Check if any changes were made:**

```bash
git status --porcelain
```

**If EMPTY (no file changes):**
- Skip to "No-Changes Path" below
- This means implementation was already complete or no changes needed

**If NOT EMPTY (file changes exist):**
- Continue to Step 2 (Push Feature Branch)

---

### No-Changes Path (Already Implemented)

**When implementation determined no changes were needed:**

1. **Report completion to chat:**
    - Summarize what was completed
    - No compare URL needed

2. **HALT after reporting:**
    - No branch push (already pushed)
    - No PR creation

---

### Step 2: Push Feature Branch

```bash
git push -u origin <branch-name>
```

This pushes the branch WITHOUT creating a PR.

### Step 3: Generate Compare URL

**Pre-Creation URL — Construct from verified session-init values:**

1. Read `<github.owner>`, `<github.repo>`, `<gitbucket.html_url>` from session init
2. Construct the Compare URL using those exact values
3. **Character-match verification:** Confirm the constructed URL contains the exact `<github.owner>` and `<github.repo>` strings from session init (character-for-character match, no typos, no cached values)
4. If any mismatch: HALT and report

### Step 4: Report Completion

Report to chat (exec summary + URL):
```
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

Compare URL: <Character-match verified URL from session-init values>

🤖 <AgentName> (<ModelId>) <status>
```

**If a PR was created during this workflow**, use the `html_url` from the `github_create_pull_request` API response instead of a constructed Compare URL:

```
PR URL: <html_url from github_create_pull_request API response>

🤖 <AgentName> (<ModelId>) <status>
```

### Step 4.5: Verify Chat Output Format (MANDATORY)

**Before sending the chat message in Step 4, verify ALL elements are present and correctly ordered:**

- [ ] Executive summary present as **first** element (before any URL)
- [ ] Outcome line present after summary
- [ ] URL present IF relevant (after outcome, before byline) — required when branch pushed, **omitted** when no branch/compare URL exists
- [ ] AI byline present as **LAST** element (after URL, or after outcome when no URL)
- [ ] No URL before executive summary
- [ ] No byline before URL/outcome

**Evidence requirement:** Each checkpoint verification MUST produce a tool-call artifact (e.g., `read` of the composed message, or a verification command) confirming the element is present or correctly absent. Verbal assertion without tool-call evidence is insufficient.

**URL applicability:**

| Scenario | URL Required? | Action |
| -- | -- | -- |
| Branch pushed, compare URL generated | ✅ Yes | Include compare URL between outcome and byline |
| No branch pushed (no-changes path) | ❌ No | Omit URL element entirely; byline follows outcome directly |
| PR already created | ✅ Yes | Use PR URL label with `pull/<N>` format instead of "Compare URL" |

**Classification on failure:**

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Missing summary | MISSING-ELEMENT | auto-fix | Add summary before sending |
| Missing outcome | MISSING-ELEMENT | auto-fix | Add outcome before sending |
| Missing URL when required | MISSING-ELEMENT | auto-fix | Generate URL before sending |
| URL included when not applicable | STRUCTURE-VIOLATION | auto-fix | Remove URL, reorder to summary → outcome → byline |
| Missing byline | MISSING-ELEMENT | auto-fix | Add byline before sending |
| Wrong ordering | STRUCTURE-VIOLATION | auto-fix | Reorder to summary → outcome → [URL] → byline |

**Auto-fix on failure:** If any element is missing or misordered, fix the output before sending. Missing elements are auto-fixed before output is sent — NOT reported after the fact.

### Step 5: HALT

**DO NOT:**
- Create PR (requires explicit "create a PR")
- Squash commits (happens at PR creation)
- Push again (already pushed)

**WAIT for:**
- Developer to review via GitHub diff viewer
- Explicit "create a PR" instruction

## Adversarial Verification: Push and Commit Claims

**Before claiming implementation is pushed and complete, verify against actual git and GitHub state — not assumed state, not cached results.**

### Verify All Changes Are Actually Committed

```
git status --porcelain
- If output is NOT empty → VERIFICATION-GAP (conditional: commit remaining changes before push)
- If output IS empty → all changes committed (verified)

git diff --staged
- If staged diff is empty AND no unstaged changes → clean state confirmed
- If staged diff is non-empty → changes are staged but may not be committed yet
```

**Evidence artifact:** `git status --porcelain` and `git diff --staged` output confirming clean state.

### Verify Branch Is Actually Pushed to Remote

```
git branch -vv
- Verify tracking branch exists: [origin/<branch-name>]

git diff @{u} HEAD
- If diff is empty → all local commits are on remote (verified)
- If diff is non-empty → unpushed commits exist (auto-fix: push immediately)

git log origin/dev..HEAD --oneline
- Verify at least one commit exists ahead of dev
- If no commits → MISSING-ELEMENT (flag-for-review: branch may have empty diff)
```

**Evidence artifact:** `git branch -vv`, `git diff @{u} HEAD`, and `git log origin/dev..HEAD --oneline` output.

### Verify Compare URL Points to Actual Changes

```
After generating compare URL:
  - Verify URL uses correct base branch (dev, not main)
  - Verify URL uses session init values for <github.owner> and <github.repo> (not hardcoded)
  - If URL contains wrong base → STRUCTURE-VIOLATION (auto-fix: regenerate with correct base)
```

**Evidence artifact:** Compare URL string showing correct base branch and owner/repo values.

### Verify Chat Output Format Claims Match Actual Output

```
Before sending chat message in Step 4:
  - Verify each required element is present in the composed message
  - Use the checklist from Step 4.5 as verification
  - If any element missing → MISSING-ELEMENT (auto-fix: add before sending)
  - If elements misordered → STRUCTURE-VIOLATION (auto-fix: reorder before sending)
```

**Evidence artifact:** Review of composed message text confirming all format requirements are met.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Uncommitted changes detected | VERIFICATION-GAP | conditional | Commit before push |
| Unpushed commits detected | VERIFICATION-GAP | auto-fix | Push remaining commits immediately |
| Compare URL uses wrong base | STRUCTURE-VIOLATION | auto-fix | Regenerate with dev as base |
| Compare URL uses hardcoded values | STRUCTURE-VIOLATION | auto-fix | Regenerate with session init values |
| No commits ahead of dev | MISSING-ELEMENT | flag-for-review | Branch may have empty diff |
| Chat output missing required elements | MISSING-ELEMENT | auto-fix | Add element before sending |

## Context Required

- Session values: <github.owner>, <github.repo>, branch name
- Related tasks: `pr-creation` (PR)

## Why This Task Is Critical

- Developers need visibility before PR creation
- Prevents premature PR creation
- Clear separation between "done implementing" and "create PR"## Enforcement References
-  Evidence format + finding classification: see `enforcement/adversarial-verification.md`
-  Scope parsing: see `enforcement/scope-parsing.md`
