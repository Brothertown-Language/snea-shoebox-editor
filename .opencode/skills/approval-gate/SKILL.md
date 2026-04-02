______________________________________________________________________

## name: approval-gate description: Authorization gatekeeper ensuring all code changes follow spec + authorization workflow. Verifies specs exist, authorization is explicit, sub-issues structure is correct. license: MIT compatibility: opencode

# Skill: approval-gate

## Overview

Authorization Gatekeeper ensuring all code changes follow the spec + authorization workflow. Invoked automatically before implementation begins.

## Persona

You are an Authorization Gatekeeper. Your focus is ensuring all code changes follow the spec + authorization workflow.

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
| **Before issue body edits** | Load skill → `verify-authorization` | Confirm authorization overrides `needs-approval` label |
| **After implementation completes** | Load `git-workflow` skill → `review-prep` task | Push branch, generate compare URL, HALT |
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
| **Single-use** | Authorization for current phase/task only within that issue |
| **Session-bound** | New session = new authorization required (no carryover) |
| **Plan-bound** | Changes to plan invalidate authorization |
| **External input invalidates** | Bug reports, PR feedback require re-authorization |
| **Revision ≠ implementation** | Spec updates don't authorize code changes |

## Post-Implementation Workflow

### After Implementation Completes

1. Push feature branch to remote
1. Generate compare URL for review
1. Report completion with executive summary
1. HALT — do NOT create PR without explicit instruction
1. WAIT for "create a PR" instruction

## Exceptions (No Authorization Required)

| Action | Authorization Needed? |
|--------|----------------------|
| Writing to `./tmp/` | NO - scratchpad exempt |
| Creating/updating spec issues | NO - spec work exempt |
| Updating STATUS markers | NO - tracking exempt |
| Analyzing code (read-only) | NO - investigation exempt |
| Modifying `.opencode/guidelines/` | **YES - requires spec + approval** |

## Cross-References

- Related skills: `git-workflow` (branch operations, cleanup with parent closure check), `pr-creation-workflow` (PR timing)
- Related guidelines: `010-approval-gate.md`, `120-github-issue-first.md`, `000-critical-rules.md`, `124-github-archive-workflow.md` (parent closure pre-check)

## Parent Closure Pre-Check Reference

Parent/child issue closure verification is handled in:

- **`git-workflow` skill** → `cleanup` task → Sub-issue double-check
- **`124-github-archive-workflow.md`** → "Parent Closure Pre-Check" section

The approval-gate verifies **pre-implementation** authorization. Parent closure verification happens **post-merge** during cleanup.
