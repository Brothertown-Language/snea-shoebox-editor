# Task: classify-and-resolve

## Purpose

Detect, classify, and resolve git conflicts according to a tiered system that prevents silent erosion of committed work.

## Operating Protocol

1. Invoked by: `/skill conflict-resolution --task classify-and-resolve`
2. When to use: When a git rebase/merge/cherry-pick operation produces conflicts
3. Exit criteria: All conflicts classified and resolved, post-resolution verification passes

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
git checkout --theirs <file>  # or --ours, depending on context
git add <file>
```

No notification required. Proceed silently.

**Tier 2 — Textual but safe:**

```bash
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
    body=f"## Conflict During Rebase\n\n...",
    labels=["conflict-resolution"]
)
```

6. **WAIT** for developer guidance before resolving Tier 3 conflicts
7. After developer provides guidance, resolve the conflict and continue

### Step 4: Post-Resolution Verification

After ALL conflicts are resolved and before continuing the rebase/merge:

1. **Verify spec compliance:** Read resolved files and check they still satisfy the original spec

```bash
grep -c "<spec-key-term>" <resolved-file>
```

2. **Verify no dropped changes:** Check that no committed work was silently erased

```bash
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

```bash
git rebase --continue   # or: git merge --continue, git cherry-pick --continue
```

If verification fails, report the issue and HALT for developer review.

## Context Required

- Related skills: `conflict-resolution` (parent skill), `git-workflow` (rebase/merge operations)
- Related guidelines: `000-critical-rules.md` (blind conflict resolution prohibition)