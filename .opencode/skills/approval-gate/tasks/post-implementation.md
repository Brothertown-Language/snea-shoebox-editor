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

Using session values (GIT_OWNER, GIT_REPO):

```
https://github.com/${GIT_OWNER}/${GIT_REPO}/compare/dev...<branch-name>
```

### Step 4: Report Completion

Report to chat (exec summary + URL):
```
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

https://github.com/<owner>/<repo>/compare/dev...<branch-name>

🤖 <AgentName> (<ModelID>) <status>
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

## Context Required

- Session values: GIT_OWNER, GIT_REPO, branch name
- Related tasks: `pr-creation` (PR)

## Why This Task Is Critical

- Developers need visibility before PR creation
- Prevents premature PR creation
- Clear separation between "done implementing" and "create PR"