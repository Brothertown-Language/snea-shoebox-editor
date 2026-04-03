---
name: approval-gate
description: Authorization gatekeeper ensuring all code changes follow spec + authorization workflow. Verifies specs exist, authorization is explicit, sub-issues structure is correct.
license: MIT
compatibility: opencode
---

# Skill: approval-gate

Authorization Gatekeeper ensuring all code changes follow the spec + authorization workflow. Invoked automatically before implementation begins.

## When to Use

- Before ANY file edit (MANDATORY - auto-loaded)
- Before implementation (verify auth + sub-issues)
- Before issue body edits (verify authorization)

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `verify-authorization` | Check explicit auth and needs-approval label | ~400 |
| `verify-sub-issues` | Verify sub-issue structure for multi-task specs | ~480 |
| `verify-codebase` | Re-evaluate codebase state, detect staleness | ~400 |
| `verify-blockers` | Check for blocking issues/dependencies | ~320 |
| `verify-open-questions` | Check for unresolved questions in spec | ~370 |
| `post-implementation` | Push branch, generate compare URL, HALT | ~480 |

## Invocation

- `/skill approval-gate --task verify-authorization` - Check auth before work
- `/skill approval-gate --task verify-sub-issues` - Check sub-issue structure
- `/skill approval-gate --task verify-codebase` - Check codebase state
- `/skill approval-gate --task verify-blockers` - Check for blockers
- `/skill approval-gate --task verify-open-questions` - Check for unresolved questions
- `/skill approval-gate --task post-implementation` - After implementation done
- `/skill approval-gate` - Overview only

## Operating Protocol

1. **Automatic invocation (mandatory):** This skill is referenced when:

   - User says `approved`, `go`, or similar authorization
   - User asks about approval workflow
   - Implementation is about to begin
   - DO NOT prompt for invocation - the skill is triggered automatically

1. **Pre-Implementation Verification:**

   - Verify spec exists as GitHub Issue
   - Verify spec has received explicit authorization
   - Verify sub-issues structure (multi-task only)
   - Check for blocking issues/updates

1. **Implementation Scope:**

   - Authorization grants ONLY the specified phase/task
   - HALT after completing authorized work
   - Wait for explicit authorization for next phase/task

## Automatic Invocation Triggers

**This skill MUST be invoked automatically (no user prompt) at these enforcement points:**

| Trigger Point | Action | Verification |
|---------------|--------|--------------|
| **Before ANY file edit** | Load skill → `verify-authorization` task | Confirm spec + approval exist |
| **Before implementation** | Load skill → `verify-authorization` + `verify-sub-issues` | Confirm multi-task specs have sub-issues |
| **After user says "approved" or "go"** | Load `git-workflow` → `pre-work` task | Stash changes (with --include-untracked), create branch |
| **After implementation completes** | Load `git-workflow` → `review-prep` task | Push branch, generate compare URL, HALT |
| **Before posting GitHub comments** | Load `github-comments` skill | Verify byline format, agent identity |

**Enforcement:** Do NOT proceed with edits, implementation, or comments without first loading this skill and verifying authorization.

### ⚠️ MANDATORY: Post-Implementation Review-Prep Invocation

**After implementation completes, the agent MUST invoke review-prep from the git-workflow skill — this is AUTOMATIC.**

The sequence is FIXED:

1. `approval-gate` verifies authorization → implementation begins
2. Implementation task finishes all file changes
3. Implementation task commits AND pushes the branch
4. Implementation task reports completion
5. **git-workflow review-prep task is invoked AUTOMATICALLY**
6. review-prep generates compare URL → HALTs

**DO NOT:**
- Return to chat after implementation without invoking review-prep
- Report completion and HALT without pushing branch first
- Skip compare URL generation because "no changes needed"

**The review-prep task provides MANDATORY developer visibility before PR creation.**

See `git-workflow` skill → `review-prep` task for the complete workflow.

## Authorization Requirements

### Mandatory Before ANY Code Change

| Requirement | Description |
|-------------|-------------|
| **Spec exists as GitHub Issue** | No local fallback - GitHub Issues only |
| **Explicit authorization** | User says `approved`, `go`, or `approved: N.M` — **OVERRIDES `needs-approval` label** |
| **Open questions resolved** | No unresolved items in spec |
| **Sub-issues verified** | Multi-task specs require phase-level sub-issues |

### Authorization Does NOT Authorize

- Creating a spec does NOT authorize implementation
- Analyzing/investigating is NOT authorization
- Answering questions is NOT authorization
- `"Should I do X?"` is seeking permission, not receiving it

## Authorization Scope Rules

| Rule | Scope |
|------|-------|
| **Issue-bound** | Authorization applies ONLY to the specific issue where it was given |
| **Session-bound** | New session = new authorization required (no carryover) |
| **Plan-bound** | Changes to plan invalidate authorization |
| **External input invalidates** | Bug reports, PR feedback require re-authorization |
| **Revision ≠ implementation** | Spec updates don't authorize code changes |

### Authorization Scope for Multi-Phase Specs (CRITICAL)

**⚠️ Unqualified approval authorizes ALL phases of a spec.**

When a developer says `approved` or `go` **without a phase qualifier**, the agent is authorized to implement ALL phases of the spec in sequence. The agent will proceed from Phase 1 through all phases without stopping for re-approval between phases.

| Command | Scope | Behavior |
|---------|-------|----------|
| `approved` | ALL phases | Proceed through all phases without stopping |
| `go` | ALL phases | Proceed through all phases without stopping |
| `approved: 1` | Phase 1 only | HALT after Phase 1, wait for next authorization |
| `approved: 2.3` | Phase 2 Step 3 only | HALT after completing Step 3, wait for next authorization |

**Rationale:**
- Unqualified approval matches developer mental model of "approved means go ahead"
- Phase-by-phase approval is intentional scoping (opt-in via qualifiers)
- Prevents unnecessary back-and-forth on multi-phase implementations

**Developer Workflow:**

- **Approve entire spec:** Use `approved` or `go` without qualifiers
- **Approve one phase:** Use `approved: N` where N is the phase number
- **Approve specific step:** Use `approved: N.M` where N is phase and M is step

**Agent Behavior:**

**With unqualified approval (`approved` or `go`):**
1. Proceed through Phase 1
2. Continue to Phase 2 (no HALT)
3. Continue through all remaining phases
4. HALT only after completing the entire spec

**With qualified approval (`approved: 1` or `approved: 2.3`):**
1. Proceed through the authorized phase/step ONLY
2. HALT after completing that phase/step
3. Wait for next authorization before continuing

## Compound Command Handling

**Compound command:** A user message containing multiple instructions without proper separation, where approval parsing may be ambiguous.

### Recognition Pattern

| Message | Parsed As | Authorization? |
|---------|-----------|----------------|
| `"check pr"` | Verify PR status only | NO - verification command |
| `"#196 approvedcheck pr"` | Issue reference + compound text | NO - approval not standalone |
| `"#196 approved"` | Issue #196 approved | YES - explicit, standalone |
| `"approved check pr"` | Approval + verification | YES - properly separated |
| `"approved - check pr"` | Approval + verification | YES - properly separated |

**Key Principle:** Authorization tokens must be **standalone** (separated by whitespace or end-of-message) to constitute valid approval.

### Standalone Definition

An approval word is standalone when:
- It is separated by whitespace: `"approved check pr"` (space after "approved")
- It is the only content: `"approved"`
- It is separated by punctuation: `"approved - check"` (hyphen separator)

An approval word is **NOT** standalone when:
- Part of a compound word: `"approvedcheck pr"` (no space, single compound)
- Embedded in text without separation: `"#196 approvedcheck pr"`

### Pattern Matching Rules

See `verify-authorization` task for complete pattern matching algorithm including:
- Approval patterns (`approved`, `go`, `approved: N.M`)
- Non-approval patterns (verification commands, questions)
- Separation requirements for compound commands

## Post-Implementation Workflow

### ⚠️ MANDATORY PUSH BEFORE HALT CHECKLIST

**CRITICAL VIOLATION WARNING: Implementation task MUST push branch BEFORE any HALT.**

**Pre-HALT Verification Checklist (MANDATORY):**

Before ANY HALT (task complete, phase complete, awaiting approval, awaiting clarification, error, session ending):

```bash
# Step 1: CHECK FOR COMMITS
git log origin/<branch>..HEAD --oneline

# If output shows commits → PUSH IS REQUIRED
# If output is empty → No push needed (skip to HALT)

# Step 2: PUSH IF COMMITS EXIST
git push -u origin <branch>

# Step 3: VERIFY PUSH
git branch -vv
# Must show: [origin/<branch>] tracking ref

# Step 4: REPORT PUSH STATUS
"Branch pushed with X commits. Ready for review-prep."
```

**Violation Detection:**

If review-prep is invoked AND branch is NOT pushed:

1. **STOP** - Workflow violation detected
2. **FIX IMMEDIATELY:** `git push -u origin <branch-name>`
3. **REPORT:** "Implementation task failed to push - workflow violation fixed"
4. **CONTINUE:** Generate compare URL
5. **DOCUMENT:** Note gap in completion comment

**This is NOT optional. This is ZERO TOLERANCE. Violation = CRITICAL GUIDELINE BREACH.**

### After Implementation Completes

1. Push feature branch to remote
1. **WIP commit if halting** (if awaiting approval, clarification, or session end)
1. Generate compare URL for review
1. Report completion with executive summary
1. HALT — do NOT create PR without explicit instruction
1. WAIT for "create a PR" instruction

### WIP Commit Before HALT

**CRITICAL: Work-in-progress commits MUST be made before ANY HALT to prevent data loss.**

When implementation halts (awaiting approval, awaiting clarification, error, session end):

1. Check for uncommitted changes: `git status`
1. If changes exist, commit WIP: `git commit -m "WIP: Phase N - description"`
1. Report WIP commit made
1. THEN HALT

**See `111-git-commit-workflow.md` → "WIP Commit Before HALT" section for complete workflow.**

## Exceptions (No Authorization Required)

| Action | Authorization Needed? |
|--------|----------------------|
| Writing to `./tmp/` | NO - scratchpad exempt |
| Creating/updating spec issues | NO - spec work exempt |
| Updating STATUS markers | NO - tracking exempt |
| Analyzing code (read-only) | NO - investigation exempt |
| Modifying `.opencode/guidelines/` | **YES - requires spec + approval** |

## Git Workflow Sequence

**After authorization, the git workflow is automatically triggered:**

1. **Pre-Work Task** (automatic via approval-gate)
   - Check current branch
   - Stash changes with `--include-untracked`
   - Create feature branch
   - Verify working tree is clean

2. **Implementation Phase** (agent performs work)
   - Grouped commits per logical concern
   - WIP commits before any HALT
   - Executive summary after completion

3. **Review-Prep Task** (automatic)
   - Push branch
   - Generate compare URL
   - Post to issue AND chat
   - HALT for developer review

4. **PR Creation** (requires explicit "create a PR")
   - Squash to single commit
   - Push
   - Create PR
   - HALT

5. **Cleanup** (after PR merge confirmed)
   - Verify merge via GitHub API
   - Close issues
   - Delete branches

## Cross-References

- Related skills: `git-workflow` (branch operations, cleanup with parent closure check), `pr-creation-workflow` (PR timing)
- Related guidelines: `010-approval-gate.md`, `120-github-issue-first.md`, `000-critical-rules.md`, `124-github-archive-workflow.md` (parent closure pre-check)

## Parent Closure Pre-Check Reference

Parent/child issue closure verification is handled in:

- **`git-workflow` skill** → `cleanup` task → Sub-issue double-check
- **`124-github-archive-workflow.md`** → "Parent Closure Pre-Check" section

The approval-gate verifies **pre-implementation** authorization. Parent closure verification happens **post-merge** during cleanup.
