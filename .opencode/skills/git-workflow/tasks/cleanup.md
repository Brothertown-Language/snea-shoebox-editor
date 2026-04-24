# Task: cleanup

## Purpose

Delete merged branches after PR merge, clean stale references, and verify repository state is ready for next work session.

## Operating Protocol

1. **After PR merge:** Run when human confirms "PR merged" or similar
2. **Automatic detection:** Can also run when invoked to check for merged branches
3. **Mandatory cleanup:** ALL merged branches must be deleted (local and remote)

## Entry Criteria

- Human confirms "PR merged" or similar
- OR skill invoked with cleanup detection enabled

## Exit Criteria

- Local merged branch deleted
- Remote merged branch deleted (if applicable)
- Stale remote references pruned
- Working tree clean

## Procedure

### Step 1: Verify PR Merge and Run Gates

**Route to:** `cleanup/verify-merge`

Verifies PR merge via GitHub API, runs SC-verification gate, phase-completion gate, and rebase pending PRs.

### Step 2: Hierarchical Issue Closure

**Route to:** `cleanup/issue-closure`

Collects all referenced issues from PR body, classifies each (plan/spec/other), closes hierarchically, and runs transitive graph reconciliation.

### Step 3: Branch Cleanup and Sync

**Route to:** `cleanup/branch-cleanup`

Switches to dev, syncs with remote, removes feature worktree, deletes merged branches, verifies clean state.

## Branch Cleanup After Merge — MANDATORY

**⚠️ CRITICAL: Cleanup is NOT Optional**

After EVERY merged PR, cleanup is MANDATORY — no exceptions.

### ✅ ALWAYS DO — IMMEDIATELY After Merge Confirmation

1. Switch to dev and sync: `git checkout dev && git pull origin dev`
2. Verify dev sync: `git log --oneline -5` must show the merge commit
3. Delete local feature branch: `git branch -d <branch-name>`
4. Delete remote branch: `git push origin --delete <branch-name>`
5. Verify cleanup: `git branch -vv`
6. Prune remote references: `git fetch --prune && git remote prune origin`

## Branch Status Categories

| Status | Condition | Action |
| -- | -- | -- |
| **Fully merged** | `ahead=0, behind=0` or PR merged | **DELETE IMMEDIATELY** |
| **Superseded** | PR closed/merged, changes incorporated | **DELETE IMMEDIATELY** |
| **Stale** | Behind main by many commits, no PR, no recent work | Safe to delete |
| **Active** | Has unmerged commits, open PR, or active work | **Do NOT delete** |

## Automatic Cleanup Detection

**Entry triggers:** "PR merged" confirmation, "cleanup branches" request, or "check pr" / "check prs" / "check pull request" / "check pull requests" phrases.

### "Check PR" Workflow

1. List all PRs (open and merged) using `github_list_pull_requests`
2. For each merged PR with local branch still existing → activate full cleanup
3. For each open PR → report PR number, title, and status
4. If only open PRs exist → report and HALT

### Safety Checks Before Deletion

| Check | Purpose | Method |
| -- | -- | -- |
| Branch merged | Prevent deleting unmerged work | `git branch --merged dev` |
| PR status | Confirm merge (not just closed) | GitHub API |
| Not current | Prevent deleting active branch | `git branch --show-current` |
| Not protected | Block main/master deletion | Hardcoded exclusion |
| Clean working tree | Ensure no uncommitted changes | `git status --porcelain` |

**If ANY check fails → SKIP that branch with warning.**

## Sub-Issue Closure Enforcement (CRITICAL)

**⚠️ CRITICAL: Sub-issues are closed by the cleanup task via API, NOT by platform autoclose.**

GitHub autoclose is inert for this repo (PRs merge to `dev`, not `main`). The cleanup task is the SOLE closure mechanism.

## Issue Closure Timing

**Issues are closed ONLY AFTER the PR is merged — NEVER before.**

| Step | Action | Agent Role |
| -- | -- | -- |
| Implementation complete | Create PR with `Fixes #123` | ✅ Agent creates PR |
| PR created | Report URL, HALT | ✅ Agent waits |
| Human merges PR | Merge happens | 🚫 Human ONLY |
| User confirms merge | Call `github_pull_request_read method=get` | ✅ Agent verifies |
| PR state = merged | Close issue | ✅ Agent closes |

## Parent/Child Issue Closure

**Parent issues MUST NOT be closed while ANY child issues remain open.**

Example:
```
SPEC #100 (parent)
├── Task #101: Phase 1 → PR merges → Close #101 ONLY
├── Task #102: Phase 2 → PR merges → Close #102 ONLY
└── Task #103: Phase 3 → PR merges → Close #103 AND #100
```

## Closing Summary (Conditional)

Post a closing comment ONLY if it conveys substantive information stakeholders need. Skip for routine closures.

## Archive Workflow

**All specs use GitHub Issues as the authoritative source.**

⚠️ **CRITICAL:** NEVER edit the issue body when closing. Status updates MUST be added as comments.

**Body-Preservation Safeguard:** `len(new_body) >= 0.8 * len(original_body)` — HALT if content erasure detected.

## Live Verification (MANDATORY)

Each verification point requires a tool call for evidence. Assertions without tool-call artifacts are VERIFICATION-GAP findings.

| Check | Tool Call | Expected Result | On Failure |
| -- | -- | -- | -- |
| PR merge status | `github_pull_request_read(method=get, ...)` | `merged_at` is not None | CONFLICTING → HALT |
| Local dev synced | `git log --oneline -1 dev` equals remote | Hashes match exactly | VERIFICATION-GAP → re-pull |
| Sub-issues closed | `github_issue_read(method=get_sub_issues, ...)` | All state=closed | VERIFICATION-GAP → close or investigate |

## Sub-Task Files

| Sub-Task | Purpose | Words |
| -- | -- | -- |
| `cleanup/verify-merge` | PR merge verification, SC gate, phase gate | ≈750 |
| `cleanup/issue-closure` | Hierarchical issue closure, graph reconciliation | ≈800 |
| `cleanup/branch-cleanup` | Dev sync, worktree removal, branch deletion | ≈700 |

## Context Required

- Related skills: `issue-operations`, `conflict-resolution`
- Related tasks: `rebase-pending`, `check-pr`