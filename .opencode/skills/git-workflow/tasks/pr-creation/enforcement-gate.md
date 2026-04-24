# Task: pr-creation/enforcement-gate

## Purpose

Enforce mandatory pre-conditions before PR creation. Verify explicit PR instruction, review-prep completion, and branch push status.

## Entry Criteria

- Implementation is complete
- Developer may have said "create a PR" or similar

## Exit Criteria

- All enforcement gates pass
- PR creation is authorized to proceed

## Procedure

### Step 0: Submodule PR Dependency Check (MANDATORY GATE)

**If `.gitmodules` does NOT exist:** Skip entirely.

**If `.gitmodules` EXISTS:**

For each submodule entry:
1. Get committed SHA: `git ls-tree HEAD <path> | awk '{print $3}'`
2. Get remote dev HEAD SHA: `git ls-remote <url> refs/heads/dev | awk '{print $1}'`
3. Compare SHA:
   - Match → pass
   - Mismatch → **BLOCK PR creation** — hard gate, no override
4. For `main`-branch PRs: verify SHA is a tagged release

**There is NO `--force` override for submodule dependency gates.**

### Step 1: Verify PR Instruction (MANDATORY)

**If ANY check fails → STOP and report. DO NOT proceed.**

| Check | Requirement |
| -- | -- |
| Explicit PR instruction | "create a PR", "make a PR", "push and create PR", "let's get a PR up" |
| review-prep completed | Compare URL was generated and reported |
| Branch pushed to remote | `git branch -vv` shows `[origin/branch]` |

**What does NOT authorize PR creation (HALT):**

| Phrase | Reason |
| -- | -- |
| "approved" | Authorizes implementation ONLY, NOT PR creation |
| "go" | Authorizes implementation ONLY, NOT PR creation |
| Implementation complete | Does NOT authorize PR |
| "continue" | Ambiguous — could mean next phase |

### Step 1.5: Check Existing PR State

Query GitHub API for existing PRs on this branch:

- **Open PR:** Update existing PR (push new commits)
- **Closed PR (not merged):** Check reason, proceed with caution
- **Merged PR:** Rebase branch on dev, check for remaining changes

If branch already merged (no remaining changes):
```
✅ BRANCH ALREADY MERGED
The branch '{branch_name}' has already been merged via PR #{pr_number}.
No new PR needed.
```

### Step 1.5d: Merge Conflict Detection

For OPEN PRs, check `mergeable` attribute:
- `True` / `"clean"` → Proceed
- `False` / `"dirty"` → Classify and resolve conflicts per `conflict-resolution` skill
- `None` / `"unknown"` → Wait and retry, or check locally

**For AI-objective conflicts (imports, whitespace, additive):** Auto-resolve.
**For AI-subjective conflicts (logical, architectural, intent):** HALT and request developer input.

## Enforcement Mechanisms

| Layer | Mechanism | Scope | Bypassable? |
| -- | -- | -- | -- |
| Local | `.opencode/hooks/pre-commit` | Blocks commit to main/master/dev | No |
| Local | `.opencode/hooks/post-commit` | Warns after commit to main/master/dev | N/A (post) |
| GitBucket | Branch protection rules | Requires PR for dev/main | No |

## Context Required

- Related tasks: `pr-creation/squash-push`, `pr-creation/create-pr`
- Related skills: `conflict-resolution`