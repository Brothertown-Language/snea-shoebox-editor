# Task: verify-qa-mode

## Purpose

Detect when AI agent receives implementation instructions WITHOUT proper authorization, spec/issue, or feature branch — and switch to Q/A mode.

## Entry Criteria

- User gives instruction (any text that could be interpreted as implementation request)
- Invoked BEFORE ANY other work begins

## Exit Criteria

- Q/A mode switch decision made
- Single question asked if needed

## Critical: When This Task Is Invoked

**This task is the FIRST CHECK before ANY implementation work.**

**Invocation Points:**
- Before branching (git-workflow pre-work)
- Before authorization check (verify-authorization)
- Before ANY implementation work

## Procedure

### Step 1: Detect Implementation Request Keywords

Check if user instruction contains implementation-related keywords:

**Implementation Keywords (require gate):**
- Implement, implement this, implement #N, implement: X
- Fix, fix this, fix the bug, fix #N
- Create, create X, add X
- Update, update X, modify X
- Change, change X, change the X
- Write, write X, add X to Y
- Remove, remove X, delete X
- Refactor, refactor X, clean up X
- Optimize, optimize X, improve X
- Want me to, shall I, I can change, I can update, I can fix, I can modify
- Edit the skill, update the guideline, fix the skill file, update the guideline file, modify SKILL.md

**Offer-to-Edit Patterns (ALSO require gate):**
Phrases that offer to make changes without going through the spec workflow:
- "Want me to update X?" → Redirect to spec creation, HALT
- "Shall I fix this?" → Redirect to bug report or fix spec, HALT
- "I can change X to Y" → Redirect to spec creation, HALT
- "Ready to implement?" → Redirect to spec creation, HALT
- "I'll just update this" → Redirect to spec creation, HALT

**Spec/Planning Keywords (skip gate):**
- Create a spec, create an issue, create a bug report
- Plan, spec out, write a spec for X
- Revise the spec, update the spec
- Analyze, investigate, check X, look at X
- List specs, pending, specs

**Ambiguous Keywords (PROCEED TO STEP 2):**
- Any instruction not clearly implementation or planning
- User says "continue" or "proceed"

### Step 2: Check Pre-Implementation Requirements

**The Three Gate Checks:**

```
GATE 1: Is there an associated GitHub Issue?
GATE 2: Is authorization documented (explicit "approved"/"go" comment)?
GATE 3: Is current branch a feature branch (not main/dev/master)?
```

### Step 2.5: Search for Existing Spec/Plan Candidates (MANDATORY before Q/A mode)

**When ANY gate fails (no spec, no authorization, or wrong branch), the agent MUST search GitHub Issues for existing candidates before entering Q/A mode.** A silent halt without searching is a critical violation — see `000-critical-rules.md` §Silent Halt Without Prompt.

**Search Procedure:**

1. **Label search:** Search GitHub Issues with labels `[SPEC]`, `[PLAN]`, `[SPEC-FIX]` in the repository
2. **Keyword search:** Search GitHub Issues using keywords from the implementation request (e.g., feature name, component, module, bug area)
3. **Evaluate candidates:** For each result, assess relevance to the request target
4. **Present candidates:** If candidates found, list them with:
   - Issue number and title
   - URL
   - Brief relevance assessment (why it matches)
5. **Offer create-or-select:** Present user with options: select an existing candidate OR create a new spec
6. **Report failure if no candidates:** If search yields no relevant candidates, explicitly state "No existing spec/plan found for [topic]" before offering spec creation

**This step is MANDATORY.** Skipping it and going straight to Q/A mode is a critical violation.

### Step 3: Evaluate Gate Results

#### Scenario A: All Checks Pass → PROCEED

```
✅ GitHub Issue exists
✅ Authorization documented
✅ On feature branch (or creating one)

ACTION: Invoke git-workflow --task pre-work
```

#### Scenario B: Any Check Fails → SEARCH → Q/A MODE

```
❌ Gate failed

ENFORCEMENT:
1. STOP implementation work immediately
2. Do NOT create branch
3. Do NOT write code
4. Do NOT commit
5. SEARCH GitHub Issues for existing candidates (Step 2.5)
6. PRESENT candidates or failure state
7. Switch to Q/A mode
8. Offer create-or-select before halting
```

### Step 4: Q/A Mode Response Format

**When switching to Q/A mode:**

```
I see you'd like me to implement [X], but I need clarification first.

[If search found candidates:]
I found the following existing specs/plans that may be relevant:
1. #123 [SPEC] Feature X implementation — <URL>
2. #456 [PLAN] Feature X rollout — <URL>

Would you like me to work with one of these, or create a new spec?

[If no spec] No existing spec/plan found for [X].
  Would you like me to create a spec first?

[If on main/dev] I'm currently on the [main] branch.
  I need to create a feature branch first, but I need a spec/issue to associate it with.

[If no authorization] This work hasn't been authorized yet.
  Would you like to review the spec and authorize it?

What would you like me to do?
```

**Response Format Rules:**
- One question per response
- Clear explanation of what's missing
- No leading questions about implementation
- Wait for user clarification

## Critical Enforcement Matrix

| Keyword Type | GitHub Issue? | Authorization? | Feature Branch? | Action |
|--------------|---------------|----------------|-----------------|--------|
| **Implementation** | ✅ YES | ✅ YES | ✅ YES (or creating) | ✅ PROCEED |
| **Implementation** | ❌ NO | - | - | 🛑 Q/A Mode |
| **Implementation** | ✅ YES | ❌ NO | - | 🛑 Q/A Mode |
| **Implementation** | ✅ YES | ✅ YES | ❌ NO (on main) | 🛑 Q/A Mode |
| **Planning** | - | - | - | ✅ PROCEED (no auth needed) |
| **Ambiguous** | - | - | - | 🛑 Q/A Mode (ask clarification) |

## Examples

### Example 1: Implement Without Spec

**User:** "Fix the authentication bug in login.py"

**Agent Internal Check:**
- Keyword: "Fix" = implementation
- GitHub Issue? NO
- Action: Search before Q/A Mode

**Agent Search:**
- Label search: `[SPEC]`, `[PLAN]`, `[SPEC-FIX]` for "authentication" or "login"
- Keyword search: "authentication bug", "login.py"

**Agent Response (if candidates found):**
```
I see you'd like me to fix an authentication bug, but there's no GitHub Issue 
tracking this work.

I found these existing issues that may be relevant:
1. #42 [SPEC] Authentication flow improvements — https://github.com/owner/repo/issues/42
2. #87 [SPEC-FIX] Login timeout bug — https://github.com/owner/repo/issues/87

Would you like me to work with one of these, or create a new spec/bug report?

What would you like me to do?
```

**Agent Response (if no candidates found):**
```
I see you'd like me to fix an authentication bug, but no existing spec/plan 
was found for this topic.

Would you like me to create a spec/bug report first?

What would you like me to do?
```

### Example 2: Implement With Spec But No Authorization

**User:** "Implement the search feature described in issue #45"

**Agent Internal Check:**
- Keyword: "Implement" = implementation
- GitHub Issue? YES (#45)
- Authorization documented? Check issue comments...

**If no "approved" comment found:**
```
I found the spec for the search feature in issue #45, but I don't see 
explicit authorization to begin implementation.

Would you like to review the spec and authorize it?

What would you like me to do?
```

### Example 3: Implement With Spec and Authorization But Wrong Branch

**User:** "#47 approved" (with agent on `main` branch)

**Agent Internal Check:**
- Keyword: "approved" = implementation authorization
- GitHub Issue? YES (#47)
- Authorization documented? YES (comment says "approved")
- Feature branch? NO (on `main`)
- Action: Q/A Mode

**Agent Response:**
```
I have authorization for issue #47, but I'm currently on the main branch.

The three-branch workflow requires feature branches for all implementation work.

Would you like me to create a feature branch for this spec?

What would you like me to do?
```

### Example 4: Create Spec Request

**User:** "Create a spec for the user authentication feature"

**Agent Internal Check:**
- Keyword: "Create a spec" = planning
- Action: PROCEED (no gate check needed)

**Agent Response:** (proceeds to create spec)

### Example 5: Ambiguous Request

**User:** "Continue" (after analysis phase)

**Agent Internal Check:**
- Keyword: "Continue" = ambiguous
- Check context: Was user asking for analysis or implementation?
- If unclear: Q/A Mode

**Agent Response:**
```
I'm not sure what you'd like me to continue with.

Would you like me to:
1. Continue analysis?
2. Create a spec for the findings?
3. Implement the findings (requires authorization)?

What would you like me to do?
```

## What This Task Does NOT Do

- Does NOT create branches (that's git-workflow pre-work)
- Does NOT create specs (that's a separate task)
- Does NOT implement changes
- Does NOT check for needs-approval label (that's verify-authorization)
- Does NOT record authorization scope (that's verify-authorization)

## Integration with Dispatch Table

**This task MUST be invoked BEFORE all other gates:**

```yaml
# FIRST CHECK - before any implementation work
- trigger: "Any user instruction"
  skill: "approval-gate"
  task: "verify-qa-mode"
  purpose: "Detect spec-less implementation requests, switch to Q/A mode"
  automatic: false  # Always check, but only HALT if gates fail
  
# SECOND CHECK - after Q/A mode gates pass
- trigger: "User says 'approved' or 'go'"
  skill: "approval-gate"
  task: "verify-authorization"
  purpose: "Verify explicit authorization"
  
# THIRD CHECK - before branch creation
- trigger: "User authorizes implementation"
  skill: "git-workflow"
  task: "pre-work"
  purpose: "Branch creation and git state"
```

## Adversarial Verification: Spec-Less Detection

Adversarial verification model (evidence format, classification tiers, tier actions): see `enforcement/adversarial-verification.md`

### Verify Issue Exists and Contains Actual Spec Content

```
If user references an issue number:
  issue = github_issue_read(method="get", issue_number=N)
  body = issue["body"]
  
  - Verify issue actually exists (404 = no issue → Gate 1 FAILS)
  - Verify body contains spec content (not empty or placeholder text)
  - Check if body has STATUS marker — if so, compare against actual content maturity
  - If STATUS says BRAINSTORM but content is DETAILED/COMPLETE → STRUCTURE-VIOLATION
    (Gate still passes — issue exists — but NOTE the maturity mismatch)
  - If body is empty or placeholder → Gate 1 FAILS (no real spec)
```

**Evidence artifact:** `github_issue_read(method=get)` response showing issue body content and STATUS marker.

### Verify Authorization Against Actual Comment State

```
If user claims authorization exists:
  comments = github_issue_read(method="get_comments", issue_number=N)
  
  - Search ALL comments for "approved", "go", "authorized"
  - Verify author is a developer (author_association: MEMBER/OWNER/COLLABORATOR)
  - Bot/agent "approved" comments are NOT valid authorization
  - If no valid authorization comment found → Gate 2 FAILS
  - If authorization comment found but spec was revised after → Gate 2 FAILS (stale auth)
```

**Evidence artifact:** `github_issue_read(method=get_comments)` response with author details for authorization claims.

### Verify Branch State Against Actual Git State

```
current_branch = git branch --show-current
git_status = git status

- If claimed to be on feature branch but actually on main/dev → Gate 3 FAILS
- If claimed to be clean but has uncommitted changes → VERIFICATION-GAP
  (uncommitted changes may indicate prior unauthorized work)
```

**Evidence artifact:** `git branch --show-current` and `git status` output.

### Task-Specific Findings

See `enforcement/adversarial-verification.md` for the three-tier classification model (auto-fix, conditional, flag-for-review) and evidence artifact format.

## Edge Cases

### Edge Case 1: User Bypass Attempt

**User:** "Just do it" or "Go ahead without all that process"

**Agent Response:**
```
I understand you'd like to proceed, but I need a spec/issue to track 
the work and proper authorization.

This ensures:
1. Changes are tracked and auditable
2. Stakeholders can review before implementation
3. Authorization is documented for compliance

Would you like me to create a spec for review first?

What would you like me to do?
```

### Edge Case 2: Analysis Results Presented

**Agent:** (presents analysis results)

**User:** "See? This is why you should fix it"

**Agent Response:**
```
I've found the issue during analysis. However, analysis results are NOT 
authorization to implement.

Would you like me to create a bug report with these findings for review 
and authorization?

What would you like me to do?
```

### Edge Case 3: User Gets Frustrated

**User:** "Why are you asking so many questions? Just implement it!"

**Agent Response:**
```
I understand the frustration. The spec-first workflow exists because:

1. Untracked changes can't be audited
2. Authorization protects against unintended changes
3. Feature branches prevent broken main/master code

I can create a spec in under 2 minutes. Would that help?

What would you like me to do?
```

## Cross-References

- Related guideline: `.opencode/AGENTS.md` "Q/A Mode" section
- Related guideline: `010-approval-gate.md`
- Related task: `verify-authorization.md`
- Related skill: `git-workflow` (pre-work task)
- Label state machine: `141-planning-status-tracking.md §10` (label transitions for authorization gates)

## Enforcement References

- Evidence format + finding classification: see `enforcement/adversarial-verification.md`
- Scope parsing: see `enforcement/scope-parsing.md`
