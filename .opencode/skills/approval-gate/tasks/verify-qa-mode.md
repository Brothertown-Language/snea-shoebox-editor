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

### Step 3: Evaluate Gate Results

#### Scenario A: All Checks Pass → PROCEED

```
✅ GitHub Issue exists
✅ Authorization documented
✅ On feature branch (or creating one)

ACTION: Invoke git-workflow --task pre-work
```

#### Scenario B: Any Check Fails → Q/A MODE

```
❌ Gate failed

ENFORCEMENT:
1. STOP implementation work immediately
2. Do NOT create branch
3. Do NOT write code
4. Do NOT commit
5. Switch to Q/A mode
6. Ask single question: "What would you like me to do?"
```

### Step 4: Q/A Mode Response Format

**When switching to Q/A mode:**

```
I see you'd like me to implement [X], but I need clarification first.

[If no spec] There's no GitHub Issue tracking this work. 
  Would you like me to create a spec first?

[If on main/dev] I'm currently on the [main] branch. 
  I need to create a feature branch first, but I need a spec/issue to associate it with.

[If no authorization] This work hasn't been authorized yet.
  Would you like to create a spec for review first?

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
- Action: Q/A Mode

**Agent Response:**
```
I see you'd like me to fix an authentication bug, but there's no GitHub Issue 
tracking this work.

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

- Related guideline: `AGENTS.md` "Q/A Mode" section
- Related guideline: `010-approval-gate.md`
- Related task: `verify-authorization.md`
- Related skill: `git-workflow` (pre-work task)
- Label state machine: `141-planning-status-tracking.md §10` (label transitions for authorization gates)