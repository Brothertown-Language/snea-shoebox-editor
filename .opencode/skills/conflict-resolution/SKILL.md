---
name: conflict-resolution
description: Use when resolving git conflicts during rebase, merge, or cherry-pick operations. Triggers on: conflict, merge conflict, rebase conflict, resolve conflict, cherry-pick conflict, conflict resolution, intent conflict, conflict classification.
---

# Skill: conflict-resolution

## Overview

Procedural workflow for classifying and resolving git conflicts with proper intent preservation. Prevents silent erosion of committed work during rebase, merge, cherry-pick, or any git operation that produces conflicts.

## Persona

You are a Conflict Resolution Specialist. Your focus is ensuring no committed work or spec intent is silently lost during git conflict resolution.

## Invocation

- **Automatic**: Invoked by `git-workflow` tasks when conflicts are detected during rebase/merge
- **Manual**: Agent invokes when encountering conflicts in any git operation

## Conflict Classification Tiers

Before resolving ANY conflict, classify it:

| Tier | Name | Criteria | Agent Action |
|------|------|----------|-------------|
| 1 | **Trivial** | Whitespace, formatting, reordering of unchanged lines | Auto-resolve, silent |
| 2 | **Textual but safe** | Same intent on both sides, just different text (e.g., both rename same variable) | Auto-resolve, note in chat |
| 3 | **Intent conflict** | Different goals, or resolution could alter spec compliance | HALT, flag for developer review |

## Procedure

### Step 1: Detect Conflicts

When a git operation reports conflicts:

```bash
git status --porcelain | grep "^UU\|^AA\|^DU\|^UD"
```

List all conflicting files. Proceed to classify each one.

### Step 2: Classify Each Conflict

For EACH conflicting file, read both sides of the conflict:

```bash
git diff --name-only --diff-filter=U
```

Then examine conflict markers in the file. Determine the tier:

**Tier 1 — Trivial (auto-resolve, silent):**
- Whitespace-only differences
- Formatting changes (indentation, trailing whitespace)
- Reordering of unchanged lines
- Import ordering changes

**Tier 2 — Textual but safe (auto-resolve, notify chat):**
- Same intent expressed differently (e.g., both sides rename the same variable to the same name)
- Duplicate additions (both sides add the same or equivalent content)
- Minor wording differences in comments/docstrings that don't change behavior

**Tier 3 — Intent conflict (HALT, flag for developer):**
- Different goals between the two sides
- Resolution could alter spec compliance
- Architectural decisions differ between branches
- Feature branch changes would be erased by accepting "theirs"
- Parent branch changes would be erased by accepting "ours"
- Any uncertainty about whether the resolution preserves spec intent

**Classification rule:** When in doubt, classify UP to the next tier. If unsure whether something is Tier 2 or Tier 3, treat it as Tier 3.

### Step 3: Resolve According to Tier

**Tier 1 — Trivial:**

```bash
# Accept whichever side is more consistent
git checkout --theirs <file>  # or --ours, depending on context
git add <file>
```

No notification required. Proceed silently.

**Tier 2 — Textual but safe:**

```bash
# Accept whichever side is more consistent or merge manually
git checkout --theirs <file>  # or --ours
git add <file>
```

Notify in chat:

```
**Conflict Resolution (Tier 2 - Textual):**
- File: <path>
- Reason: <why it's textual but safe>
- Resolution: <which side was accepted>
```

**Tier 3 — Intent conflict:**

1. **HALT** — do NOT resolve the conflict
2. **Read both sides carefully** — understand what each branch intended
3. **Assess complexity:**
   - **Minor (devil in the details):** Few files, narrow scope, no architectural impact
   - **Complex (architectural):** Multiple files, architectural decisions, spec compliance at risk
4. **Report to developer in chat:**

```
**⚠️ Intent Conflict Detected (Tier 3):**
- File: <path>
- Feature branch intent: <what the feature branch was trying to do>
- Parent branch intent: <what the parent branch changed>
- Agent assessment: <minor or complex>
- Agent recommendation: <which side to prefer and why, or flag for developer decision>
```

5. **For complex intent conflicts**, also create a GitHub Issue:

```python
github_issue_write(
    method="create",
    title=f"[Conflict] <descriptive-title> during rebase of <branch>",
    body=f"## Conflict During Rebase\n\nBranch: <branch>\nRebasing onto: dev\n\n## Tier 3 - Intent Conflict\n\nFile: <path>\nFeature branch intent: <...>\nParent branch intent: <...>\n\n## Assessment\n\n<agent analysis of the conflict and recommendation>\n\n## Context\n\nRebasing spec/<branch> onto updated dev. This conflict requires developer review to determine correct resolution.",
    labels=["conflict-resolution"]
)
```

6. **WAIT** for developer guidance before resolving Tier 3 conflicts
7. After developer provides guidance, resolve the conflict and continue

### Step 4: Post-Resolution Verification

After ALL conflicts are resolved and before continuing the rebase/merge:

1. **Verify spec compliance**: Read the rebased/merged files and check they still satisfy the original spec

```bash
# Check for key elements from the spec
grep -c "<spec-key-term>" <resolved-file>
```

2. **Verify no dropped changes**: Check that no committed work was silently erased

```bash
# Compare result against feature branch's original state
git diff <feature-branch-original>...HEAD -- <resolved-file>
```

3. **Report verification results in chat:**

```
**Post-Resolution Verification:**
- Files resolved: <count>
- Tier 1 (trivial): <count>
- Tier 2 (textual): <count>
- Tier 3 (intent): <count>
- Spec compliance: ✅ Verified / ❌ Needs review
- Dropped changes: None detected / ⚠️ <description>
```

### Step 5: Continue Git Operation

After verification passes:

```bash
git rebase --continue   # or: git merge --continue, git cherry-pick --continue
```

If verification fails, report the issue and HALT for developer review.

## Notification Format

### Chat Notification (Tier 2)

```
**Conflict Resolution (Tier 2 - Textual):**
- File: <path>
- Reason: <why it's textual but safe>
- Resolution: <which side was accepted>
```

### Chat Notification (Tier 3 Minor)

```
**⚠️ Intent Conflict Detected (Tier 3 - Minor):**
- File: <path>
- Feature branch intent: <what>
- Parent branch intent: <what>
- Resolution: <agent recommendation, awaiting developer confirmation>
```

### Chat + GitHub Issue (Tier 3 Complex)

Chat notification plus persistent GitHub Issue with `conflict-resolution` label for tracking.

## Integration Points

| Skill | When |
|-------|------|
| `git-workflow` `--task review-prep` | Automatically invokes this skill when rebase produces conflicts |
| `git-workflow` `--task implementation` | May invoke if mid-implementation merge produces conflicts |

## Anti-Patterns

**🚫 NEVER:**
- Resolve ALL conflicts with `git checkout --theirs` / `git checkout --ours`
- Use `git rebase --strategy-option=theirs/ours` as blanket resolution
- Skip reading the conflict content before resolving
- Assume formatting conflicts are always trivial (could hide intent changes)
- Continue rebase after resolving intent conflicts without verifying spec compliance
- Create commits that silently drop committed work

**✅ ALWAYS:**
- Classify every conflict into a tier before resolving
- When in doubt, classify UP (Tier 2 vs Tier 3 → Tier 3)
- Verify spec compliance after resolving all conflicts
- Notify developer for Tier 3 conflicts
- Create GitHub Issue for complex Tier 3 conflicts
- Preserve feature branch intent unless developer says otherwise

## Context

**See `000-critical-rules.md` → "Critical Violation: Blind Conflict Resolution" for the zero-tolerance rule.**

Base directory for this skill: file:///home/muksihs/git/snea-shoebox-editor/.opencode/skills/conflict-resolution