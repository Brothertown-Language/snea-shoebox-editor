# Branch Naming Conventions

## Branch Naming Rules

**Feature branches MUST use one of these prefixes:**
- `spec/<short-name>` — For spec-driven implementation
- `feature/<description>` — For feature development
- `hotfix/<description>` — For urgent production fixes

**Branch Naming is NOT Enforced by Hooks:**
- Git hooks block AI commits to `main`/`master`/`dev` but do NOT validate branch naming
- AI intelligence determines appropriate branch name
- Developer can override AI-suggested names

## Three-Branch Architecture

**Branch Model:**
- **Feature branches** (`spec/*` or `feature/*`): Short-lived, one per issue/spec
- **Dev branch** (`dev`): Evergreen staging/integration branch (never deleted)
- **Main branch** (`main` or `master`): Production-ready code

**Merge Paths:**
1. **Feature → Dev**: PR required (squash to single commit, no CI tests required)
2. **Release: Dev → Main**: Human-triggered (no approval required, CI tests required)
3. **Hotfix**: Parallel branches to dev + main (paired issues, cross-referenced)

## Branching Workflow

**ALL feature branch creation uses worktrees (mandatory, no exceptions).** See `using-git-worktrees` skill.

### Feature Development

```bash
# 1. Sync main working tree with dev
git checkout dev && git pull origin dev

# 2. Create feature worktree (using-git-worktrees skill)
git worktree add .worktrees/spec-my-feature -b spec/my-feature dev

# 3. Work in the worktree (use workdir parameter on all commands)
# ... make changes, commit inside .worktrees/spec-my-feature ...

# 4. Push feature branch from worktree
git push -u origin spec/my-feature

# 5. Create PR targeting dev
# PR base: dev (not main)

# 6. After PR merge, cleanup (git-workflow --task cleanup)
git worktree remove .worktrees/spec-my-feature
git worktree prune
```

### Release Workflow (Human-Only)

**Releases merge from `dev` to `main` via human-triggered workflow:**

1. Human decides to release from `dev`
2. Create release worktree: `git worktree add .worktrees/release-v1.2.3 -b release/v1.2.3 dev`
3. Run CI tests on release branch
4. Merge release branch to `main`
5. Tag release on `main`
6. Delete release worktree and branch

**AI DOES NOT:**
- Create release branches
- Merge `dev` to `main`
- Tag releases
- Bypass `dev` branch

### Hotfix Workflow

**Hotfixes create PAIRED branches to both `dev` and `main`:**

1. Create paired issues (one for `dev`, one for `main`)
2. Create hotfix worktree from `main`: `git worktree add .worktrees/hotfix-urgent-fix -b hotfix/urgent-fix main`
3. Make fix, create PR to `main`
4. Create IDENTICAL hotfix worktree from `dev`: `git worktree add .worktrees/hotfix-urgent-fix-dev -b hotfix/urgent-fix-dev dev`
5. Make SAME fix, create PR to `dev`
6. BOTH PRs must merge before issues close

**Cross-referencing:**
- Hotfix issue for `main`: Cross-reference hotfix issue for `dev`
- Hotfix issue for `dev`: Cross-reference hotfix issue for `main`
- Both issues close only after BOTH PRs merge

## Protected Branches

**AI Commits Blocked On:**
- `main` (production)
- `master` (production)
- `dev` (staging/integration)

**Enforcement:**
- Local git hooks (`pre-commit`, `post-commit`) detect AI agent environment variables
- GitBucket branch protection (defense-in-depth)
- No bypass mechanism

## Dev Branch Maintenance

**Dev is evergreen:**
- Never delete `dev` branch
- Keep `dev` in sync with features
- `dev` is NOT for direct commits — only via PR

**Sync workflow (in main working tree):**
```bash
# After merging feature PR to dev (cleanup removes worktree first)
git checkout dev && git pull origin dev

# Before starting new feature (syncing main tree for worktree creation)
git checkout dev && git pull origin dev
```

## Examples

### Good Branch Names

```
spec/git-workflow-dev-branch
feature/oauth-authentication
hotfix/security-vulnerability-xss
```

### Bad Branch Names

```
my-feature                    # Missing prefix
spec/Git Workflow            # Spaces, wrong case
feature/add_oauth_and_tests  # Mixing concerns
```