# Git Protocol: Branch Cleanup

## 6. Branch Cleanup After Merge — MANDATORY

### ⚠️ CRITICAL: Cleanup is NOT Optional

**After EVERY merged PR, cleanup is MANDATORY — no exceptions, no "I'll do it later".**

### ✅ ALWAYS DO — IMMEDIATELY After Merge Confirmation

1. **Delete local feature branch** — `git branch -d <branch-name>`
2. **Delete remote branch** — `git push origin --delete <branch-name>` (if not auto-deleted by GitHub)
3. **Verify cleanup** — `git branch -vv` to confirm deletion
4. **Prune remote references** — `git fetch --prune`

**This is NOT optional.** Cleanup happens in the same session as merge confirmation.

### ✅ ALWAYS DO — When User Asks "cleanup branches"

When asked to "cleanup dead branches" or similar:

1. **List merged local branches** — `git branch --merged main`
2. **Delete merged local branches** — `git branch -d <branch-name>` for each
3. **List merged remote branches** — `git branch -r --merged main`
4. **Delete merged remote branches** — `git push origin --delete <branch-name>` for each
5. **Prune stale remote refs** — `git fetch --prune`
6. **Verify cleanup** — `git branch -a` to confirm clean state

**⚠️ CRITICAL: Clean BOTH local AND upstream.** Leaving stale remote branches defeats the purpose.

## 6.1. Automatic Branch Cleanup Detection

### Automatic Detection via git-workflow Skill

The `git-workflow` skill can automatically detect merged branches that need cleanup:

#### Detection Triggers

| Trigger | Behavior |
|---------|----------|
| User says `"approved"` or `"go"` | Pre-work verification, then check for cleanup candidates |
| User says `"PR merged"` | Immediate cleanup of specified branch |
| User says `"cleanup branches"` | Check all merged branches and prompt for cleanup |

#### Detection Process

1. **Query GitHub MCP for merged PRs:**
   - Use `github_list_pull_requests(state="merged")`
   - Extract head branch names and merge status

2. **Check local merge status:**
   - Use `git branch --merged main` to identify fully merged branches

3. **Identify cleanup candidates:**
   - Local branch exists
   - Branch is merged into main
   - Branch is not current branch
   - Branch is not protected (`main`, `master`)

4. **Safety checks before deletion:**

| Check | Purpose | Method |
|-------|---------|--------|
| Branch merged | Prevent deleting unmerged work | `git branch --merged main` |
| PR status | Confirm merge (not just closed) | GitHub API |
| Not current | Prevent deleting active branch | `git branch --show-current` |
| Not protected | Block main/master deletion | Hardcoded exclusion |
| Clean working tree | Ensure no uncommitted changes | `git status --porcelain` |

5. **Report and prompt:**
   - List branches that can be cleaned up
   - Ask user if cleanup should proceed
   - Execute cleanup on confirmation

#### Edge Cases

| Case | Handling |
|------|----------|
| PR closed without merge | Do NOT clean up — branch may be reopened |
| Local has extra commits | Detect with `git log main..<branch>`, warn user |
| Multiple PRs from same branch | Only clean up after ALL PRs merged |
| Remote branch already deleted | Skip remote deletion, clean local only |
| Cleanup conflicts with active work | Defer cleanup, warn user |

### Branch Status Categories

| Status | Condition | Action |
|--------|-----------|--------|
| **Fully merged** | `ahead=0, behind=0` or PR merged | **DELETE IMMEDIATELY** |
| **Superseded** | PR closed/merged, changes incorporated via other branch | **DELETE IMMEDIATELY** |
| **Stale** | Behind main by many commits, no PR, no recent work | Safe to delete |
| **Active** | Has unmerged commits, open PR, or active work | **Do NOT delete** |

### Cleanup Commands

```bash
# Check which branches are merged into main
git branch --merged main

# Check which branches have diverged (ahead and behind)
git branch -vv

# Delete merged branch
git branch -d <branch-name>

# Force delete if needed (unmerged but superseded)
git branch -D <branch-name>

# Delete remote tracking reference (if remote branch deleted)
git fetch --prune
```

### 🚫 NEVER DO

- **NEVER delete branches while working on them** — switch to main first
- **NEVER delete branches with unmerged work** without explicit instruction
- **NEVER delete `main` or other protected branches**
- **NEVER leave merged branches uncleaned** — cleanup is mandatory, not optional
- **NEVER defer cleanup to "later"** — do it in the same session
- **NEVER leave stale remote branches** — always clean upstream too
- **NEVER ask "should I delete remote branches too?"** — just delete them as part of cleanup

---

## 7. Enforcement Summary

### Enforcement is NON-NEGOTIABLE

The `--no-verify` flag exists but should NEVER be used. Guidelines explicitly forbid it. Using `--no-verify` to commit to main is a policy violation.

If a situation arises where you think bypass is necessary:
1. STOP
2. Report to team lead
3. Create feature branch instead
4. Follow normal PR process

---

*Source: Content migrated from `110-git-protocol.md`*