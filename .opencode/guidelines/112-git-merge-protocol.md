# Git Protocol: Merge Protocol

## Branch Hierarchy

| Branch | Purpose | Merge Strategy |
|--------|---------|----------------|
| `main` | Production (Streamlit Cloud) | Merge commit from `dev` only |
| `dev` | Integration testing | Squash merge from `feature/*` |
| `feature/*` | Development work | Created from `dev` |

## Hotfix Workflow (from main)

**For urgent production fixes that need to go directly to production before dev:**

### Branch from main (EXCEPTION to normal workflow)

```bash
git checkout main
git pull origin main
git checkout -b hotfix/urgent-fix
```

**This is the ONLY time branches are created from main instead of dev.**

### After hotfix merge to main

Sync the fix to dev:

```bash
git checkout dev
git merge main
git push origin dev
```

## 5. Spec Implementation Branches

### ✅ ALWAYS DO

When implementing an approved spec:

1. **Branch Naming**: Derive from spec filename or issue — `feature/<short-name>` (e.g., Issue #15 → `feature/git-workflow-restructure`)

2. **Branch Creation**: Before any implementation, create and checkout the branch:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/<short-name>
   ```

3. **Work in Isolation**: All implementation commits go on the feature branch, never on `dev` or `main`

4. **Easy Rollback**: If implementation fails, simply `git checkout dev && git branch -D feature/<short-name>`

### 📋 Feature PR Workflow (feature → dev)

**When GitHub MCP Tools Available:**

**Before creating PR:**
1. **Rebase on dev**: `git fetch origin && git rebase origin/dev`
2. **Squash commits**: Combine all commits into one: `git reset --soft origin/dev && git commit`
3. **Force push**: `git push --force-with-lease origin <branch>`
4. **Then create PR**: Target `dev` branch, not `main`

**PR Workflow Steps:**
1. Create feature branch: `git checkout -b feature/issue-123-description`
2. Commit changes to feature branch
3. Push to remote: `git push origin feature/issue-123-description`
4. Create PR targeting `dev`: `github_create_pull_request` with base `dev`
5. Request review: `github_request_copilot_review`
6. Address feedback with new commits
7. **WAIT for human to merge** — NEVER call `github_merge_pull_request` yourself
8. Delete branch after human merges

### ⚠️ MANDATORY: SQUASH MERGE to dev

**All feature PRs MUST be squash-merged to `dev`.**

- One commit per PR on `dev`
- Each PR is identifiable for cherry-picking
- Clean history for integration testing

**For humans merging feature PRs:**
- GitHub "Squash and merge" button is required
- Target branch: `dev`
- Never merge directly to `main`

---

## Release PR Workflow (dev → main)

**When ready to release to production:**

1. **Create release PR from dev to main:**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b release/v1.2.3  # or just use dev directly
   ```

2. **PR targets `main`:**
   - Base: `main`
   - Head: `dev` (or release branch)

3. **Merge commit (NOT squash):**
   - Preserves all feature PR commits on `main`
   - Each feature PR remains as separate commit
   - Enables cherry-picking from `main`
   - Maintains `git blame` traceability

**For humans merging release PRs:**
- Use "Merge commit" button (NOT "Squash and merge")
- This preserves PR boundaries on `main`

---

## Hotfix Workflow (from main)

**For urgent production fixes:**

1. **Branch from main:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/urgent-fix
   ```

2. **Make fix and create PR:**
   - Target `main` for the fix
   - After merge to `main`, also merge to `dev`

3. **Sync back to dev:**
   ```bash
   git checkout dev
   git merge main  # or create PR from main to dev
   ```

---

## Hotfix Backport: Dev as Authoritative Source

**When merging `main` → `dev` after hotfix:**

**CRITICAL: `dev` is authoritative for ALL files except hotfix-specific code.**

### Conflict Resolution Priority

| File Type | Correct Source | Rationale |
|-----------|---------------|-----------|
| Hotfix-specific files | `main` | Hotfix fix location |
| All other files | `dev` | Dev is authoritative |
| `uv.lock` | `dev` | Dependency state authoritative in dev |
| `.opencode/*` | `dev` | Active development, dev authoritative |
| `CHANGELOG.md` | `dev` | Dev changelog format changes |
| Config files | `dev` | Dev configuration state |

### Hotfix-Specific File Identification

Files are considered hotfix-specific if they were modified in the hotfix PR:

```bash
# Identify hotfix files from PR
gh pr view <hotfix-pr-number> --json files --jq '.files[].path'

# Or from merge commit
git diff <hotfix-branch>^..<hotfix-branch> --name-only
```

**Hotfix-specific files MUST be limited to:**
- Files directly affected by the hotfix fix
- Files required for the fix to work
- NOT configuration, dependencies, or unrelated files

### Conflict Resolution Matrix

**When `git merge main` produces conflicts during hotfix backport:**

| Conflict Type | Resolution |
|--------------|------------|
| Hotfix-specific file changed | Take `main` version (hotfix fix) |
| Non-hotfix file changed | Take `dev` version (authoritative) |
| Both changed hotfix file | Manual resolution required |
| Unrelated file changed | Take `dev` version |

**Manual resolution process:**

1. Identify hotfix-specific files from PR diff
2. For each conflicting file:
   - If in hotfix list → take `main` (hotfix)
   - If NOT in hotfix list → take `dev` (authoritative)
3. Complete merge with resolved conflicts

### Example: `uv.lock` Conflict

**Problem:** Hotfix PR updated `uv.lock` in `main`, but `dev` has newer dependencies.

**Resolution:** Take `dev` version of `uv.lock` because:
- `dev` is the authoritative source for dependency state
- Hotfix changes should be code-only, not dependency changes
- If hotfix truly requires dependency update, that's a broader hotfix scope

**Command:**
```bash
git checkout --theirs uv.lock  # Take dev version
git add uv.lock
```

### Automated Backport Script (Future)

**When to automate:**

Complex hotfixes with many conflicts may benefit from automated conflict resolution. See `scripts/hotfix_backport.py` (future implementation).

**Automation logic:**
1. Parse hotfix PR diff to identify hotfix files
2. Configure git merge strategy for each file:
   - `hotfix file` → `ours` (take main)
   - `non-hotfix file` → `theirs` (take dev)
3. Run merge with configured strategy
4. Flag complex conflicts for manual review

---

## When GitHub MCP Tools Unavailable

**Use local squash-merge:**

### ✅ ALWAYS DO

**When merging a feature branch into dev:**
- Use **squash-merge** to create a single clean commit
- Delete the feature branch after merge
- Include spec reference in commit message

**When merging dev into main:**
- Use **merge commit** to preserve PR history
- All feature PRs become separate commits on `main`

**When keeping a feature branch up-to-date:**
- Use **rebase** (not merge) to pull latest changes from `dev`
- `git fetch origin && git rebase origin/dev`

### 🚫 NEVER DO
- **NEVER use regular merge** (`git merge`) to merge feature branches into `dev` — creates messy history
- **NEVER use merge** to sync feature branch with `dev` — use rebase instead
- **NEVER force-push to `main` or `dev`**
- **NEVER squash merge from `dev` to `main`** — loses PR granularity

### Rebase Workflow

```bash
# On feature branch
git fetch origin
git rebase origin/dev

# If conflicts occur, resolve them and continue
git status  # see which files conflict
# edit conflicting files
git add <resolved-files>
git rebase --continue
```

---

*Source: Content migrated from `110-git-protocol.md`*