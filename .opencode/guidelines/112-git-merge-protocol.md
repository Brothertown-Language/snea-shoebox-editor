# Git Protocol: Merge Protocol

## 5. Spec Implementation Branches

### ✅ ALWAYS DO

When implementing an approved spec:

1. **Branch Naming**: Derive from spec filename or issue — `spec/<short-name>` (e.g., `plans/SPEC-mesh-descriptor-lookup.md` → `spec/mesh-descriptor-lookup` or Issue #15 → `spec/project-first-strategy`)

2. **Branch Creation**: Before any implementation, create and checkout the branch:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b spec/<short-name>
   ```

3. **Work in Isolation**: All implementation commits go on the spec branch, never on main

4. **Easy Rollback**: If implementation fails, simply `git checkout main && git branch -D spec/<short-name>`

### 📋 Merging Spec Branches

**When GitHub MCP Tools Available:**

Use PR workflow instead of local merge:

**Before creating PR:**
1. **Rebase on main**: `git fetch origin && git rebase origin/main`
2. **Squash commits**: Interactive rebase to consolidate multiple commits
3. **Force push**: `git push --force-with-lease origin <branch>`
4. **Then create PR**: Only after branch is clean and rebased

**PR Workflow Steps:**
1. Create feature branch: `git checkout -b feature/issue-123-description`
2. Commit changes to feature branch
3. Push to remote: `git push origin feature/issue-123-description`
4. Create PR: `github_create_pull_request` with `Fixes #123` in description
5. Request review: `github_request_copilot_review`
6. Address feedback with new commits
7. **WAIT for human to merge** — NEVER call `github_merge_pull_request` yourself
8. Delete branch after human merges

### ⚠️ MANDATORY: SQUASH MERGE ONLY

**All PRs MUST be squash-merged to `main`.**

- Never use regular merge — always squash
- Never use rebase-merge — always squash
- This maintains a clean commit history on `main`
- One commit per PR, with PR number in commit message

**For humans merging PRs:**
- GitHub "Squash and merge" button is required
- Never click "Merge" or "Rebase and merge" buttons

**When Local Merge is Acceptable (even with MCP tools):**
- Trivial fixes (typos, whitespace, single-line changes)
- Urgent hotfixes requiring immediate deployment
- Docs-only changes that don't affect production code

---

## When GitHub MCP Tools Unavailable

**Use local squash-merge:**

### ✅ ALWAYS DO

**When merging a feature branch into main:**
- Use **squash-merge** to create a single clean commit
- Delete the feature branch after merge
- Include spec reference in commit message

**When keeping a feature branch up-to-date:**
- Use **rebase** (not merge) to pull latest changes from main
- `git fetch origin && git rebase origin/main`

### 🚫 NEVER DO
- **NEVER use regular merge** (`git merge`) to merge feature branches into main — creates messy history
- **NEVER use merge** to sync feature branch with main — use rebase instead
- **NEVER force-push to main**

### Rebase Workflow

```bash
# On feature branch
git fetch origin
git rebase origin/main

# If conflicts occur, resolve them and continue
git status  # see which files conflict
# edit conflicting files
git add <resolved-files>
git rebase --continue
```

---

*Source: Content migrated from `110-git-protocol.md`*