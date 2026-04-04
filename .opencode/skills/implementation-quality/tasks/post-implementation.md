# Task: post-implementation

## Purpose

Enforce mandatory review-prep workflow after every implementation. This is a CRITICAL verification gate with ZERO TOLERANCE for violations.

## Entry Criteria

- Implementation task has completed all file changes
- Agent is about to HALT or report completion

## Exit Criteria

- Branch is pushed to remote (verified)
- Compare URL is generated
- Executive summary posted to issue AND chat (BOTH locations required)
- Agent HALTs after posting

## Procedure

### Step 1: Verify Branch Is Pushed

```bash
# CHECK: Are there unpushed commits?
git log origin/<branch>..HEAD --oneline

# If output shows commits → PUSH IS REQUIRED
# If output is empty → Branch already pushed (skip to Step 2)
```

**If unpushed commits exist:**

```bash
git push -u origin <branch>
```

**Then verify:**

```bash
git branch -vv
# Must show: [origin/<branch>] tracking ref
```

### Step 2: Generate Compare URL

```bash
# Get current branch name
branch=$(git branch --show-current)

# Get owner/repo from session init
owner="<GIT_OWNER>"
repo="<GIT_REPO>"

# Generate compare URL
compare_url="https://github.com/${owner}/${repo}/compare/main...${branch}"
```

### Step 3: Post Executive Summary

**Post to BOTH locations (MANDATORY):**

| Location | Content | Why |
|----------|---------|-----|
| GitHub Issue Comment | Full executive summary + compare URL | Preserves history |
| Chat Output | Same executive summary + compare URL | Session visibility |

**Executive Summary Format:**

```markdown
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)

https://github.com/<owner>/<repo>/compare/main...<branch>
```

**Critical: Emoji must be PLAIN TEXT (not inside italic/bold formatting).**

### Step 4: HALT

After posting to both locations:

1. Report completion with executive summary
2. HALT - do NOT create PR without explicit instruction
3. WAIT for "create a PR" instruction

## Critical Violations

**These are ZERO TOLERANCE violations:**

| Violation | Why It's Critical | Recovery |
|-----------|-------------------|----------|
| HALTing without pushing branch | Progress invisible to review | Push, then continue workflow |
| HALTing without posting to issue | History lost | Post to issue before HALT |
| HALTing without posting to chat | Session context lost | Post to chat before HALT |
| Skipping compare URL generation | Developer visibility gap | Generate URL before HALT |

## Verification Checklist

**Before ANY HALT (MANDATORY):**

| Check | Command | Expected |
|-------|---------|----------|
| Branch pushed? | `git log origin/<branch>..HEAD --oneline` | Empty (already pushed) |
| Compare URL? | `https://github.com/<owner>/<repo>/compare/main...<branch>` | Valid URL |
| Posted to issue? | Check comment exists | Executive summary visible |
| Posted to chat? | Check chat output | Executive summary visible |

**If ANY check fails: STOP and FIX before HALT.**

## What NOT To Do

**DO NOT:**

- HALT after implementation without pushing branch
- HALT without posting compare URL
- Post to issue but skip chat (or vice versa)
- Report completion without executive summary
- Skip verification "because changes are trivial"
- Ask "ready for a PR?" or "should I create PR?" (just HALT)

## Auto-Issue Creation

If this workflow is violated (agent HALTs without review-prep), auto-create a tracking issue:

1. Create issue: `[SPEC-FIX] Review-prep workflow bypass`
2. Document which implementation phase was affected
3. Add `needs-approval` label
4. Post comment explaining the violation

## Cross-References

- `000-critical-rules.md` - Critical violation enforcement
- `010-approval-gate.md` - Mandatory post-implementation invocation
- `113-git-pr-workflow.md` - Review phase details
- `git-workflow` skill - `review-prep` task