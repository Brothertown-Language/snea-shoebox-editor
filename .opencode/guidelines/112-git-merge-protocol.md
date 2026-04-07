# Git Protocol: Merge Protocol

## Branch Hierarchy

| Branch | Purpose | Merge Strategy |
|--------|---------|----------------|
| `main` | Production (Streamlit Cloud) | Merge commit from `dev` only |
| `dev` | Integration testing | Squash merge from `feature/*` |
| `feature/*` | Development work | Created from `dev` |

## Hotfix Workflow (from main)

**For urgent production fixes that need to go directly to production before dev:**

**Branch from main (EXCEPTION to normal workflow):**
```bash
git checkout main && git pull origin main && git checkout -b hotfix/urgent-fix
```

**After hotfix merge to main, sync to dev:**
```bash
git checkout dev && git merge main && git push origin dev
```

> **See `git-workflow` skill for complete merge protocol.**

## Feature PR Workflow (feature → dev)

> **See `git-workflow` skill → `pr-creation` task for complete workflow.**

**Key rules:**
- Feature PRs MUST be squash-merged to `dev`
- Target `dev` branch, not `main`
- One commit per PR on `dev`
- **Wait for human to merge** — NEVER call `github_merge_pull_request` yourself

## Release PR Workflow (dev → main)

> **See `git-workflow` skill for complete release workflow.**

**Key rules:**
- Release PRs MUST use MERGE COMMIT (not squash)
- Preserves all feature PR commits on `main`
- Enables cherry-picking from `main`
- Maintains `git blame` traceability

## Hotfix Backport: Dev as Authoritative Source

> **See `git-workflow` skill for complete hotfix backport workflow.**

**CRITICAL: `dev` is authoritative for ALL files except hotfix-specific code.**

| File Type | Correct Source | Rationale |
|-----------|---------------|------------|
| Hotfix-specific files | `main` | Hotfix fix location |
| All other files | `dev` | Dev is authoritative |
| `uv.lock`, configs, etc. | `dev` | Active development state |
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

| File Type | Correct Source | Rationale |
|-----------|---------------|------------|
| Hotfix-specific files | `main` | Hotfix fix location |
| All other files | `dev` | Dev is authoritative |
| `uv.lock` | `dev` | Dependency state authoritative in dev |
| `.opencode/*` | `dev` | Active development, dev authoritative |
| `CHANGELOG.md` | `dev` | Dev changelog format changes |
| Config files | `dev` | Dev configuration state |

**Hotfix-specific files:** Files modified in the hotfix PR, limited to:
- Files directly affected by the hotfix fix
- Files required for the fix to work
- NOT configuration, dependencies, or unrelated files

## When GitHub MCP Tools Unavailable

**Feature branches into dev:** Use squash-merge, delete branch after merge
**Dev into main:** Use merge commit to preserve PR history
**Keeping feature branch up-to-date:** Use rebase, not merge

**🚫 NEVER:**
- Regular merge to `dev` (creates messy history)
- Merge to sync feature with `dev` (use rebase)
- Force-push to `main` or `dev`
- Squash merge from `dev` to `main` (loses PR granularity)

> **See `git-workflow` skill for complete workflow.**

---

*Source: Content migrated from `110-git-protocol.md`*