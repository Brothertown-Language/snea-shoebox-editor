# Git Workflow Migration Guide

## Overview

This guide helps migrate existing work to the new **feature → dev → main** workflow.

## For Existing Open PRs Targeting `main`

If you have open PRs targeting `main`:

### Step 1: Retarget the PR

```bash
# On your feature branch
git checkout feature/your-feature
git pull origin feature/your-feature

# Rebase onto dev (NOT main)
git fetch origin
git rebase origin/dev

# Push with force (if needed)
git push --force-with-lease origin feature/your-feature
```

### Step 2: Update PR Target Branch

1. Go to your PR in GitHub
2. Click "Edit" next to the branch name
3. Change base branch from `main` to `dev`
4. The PR will retarget to `dev`

### Step 3: Verify CI Passes

- CI should run against `dev` branch
- Verify all checks pass
- Request review for `dev` merge

### Step 4: After Merge to `dev`

When your PR merges to `dev`:

1. Your feature is now in integration testing
2. Local dev Streamlit runs from `dev` for testing
3. Wait for release PR to merge `dev` → `main`

## For Local Feature Branches Not Yet Pushed

If you have local work not yet pushed:

```bash
# Branch from dev (not main)
git checkout dev
git pull origin dev
git checkout -b feature/your-feature

# Make your changes
# Commit your work
git add -A
git commit -m "Your changes"

# Push and create PR targeting dev
git push -u origin feature/your-feature
gh pr create --base dev --title "..." --body "..."
```

## For Hotfixes

Hotfixes still branch from `main`:

```bash
# Branch from main
git checkout main
git pull origin main
git checkout -b hotfix/urgent-fix

# Make hotfix changes
# ...

# Create PR targeting main
git push -u origin hotfix/urgent-fix
gh pr create --base main --title "..." --body "..."

# After merge to main, also merge to dev
git checkout dev
git merge main
git push origin dev
```

## Branch Cleanup After Migration

After migration, clean up stale branches:

```bash
# Fetch latest
git fetch --all --prune

# Delete local branches merged to dev
git branch --merged dev | grep -v "^\*\|main\|dev" | xargs git branch -d

# Delete remote tracking branches
git remote prune origin
```

## Verification Checklist

After migrating:

- [ ] Feature branch rebased on `dev`
- [ ] PR retargeted from `main` to `dev`
- [ ] CI passes on `dev`
- [ ] Local dev Streamlit runs from `dev` branch
- [ ] Hooks installed (run `./scripts/install-hooks.sh`)

## Common Issues

### Issue: Rebase conflicts with `dev`

**Solution:** Resolve conflicts, then continue:
```bash
git rebase --continue
```

### Issue: PR shows old commits from `main`

**Solution:** Force push after rebase:
```bash
git push --force-with-lease origin feature/your-feature
```

### Issue: CI configuration references `main`

**Solution:** Update CI config to run on `dev` PRs instead of `main`.

## Timeline

- Existing PRs should retarget within **1 week** of workflow change
- New PRs should target `dev` immediately
- Release PRs (`dev` → `main`) will be created periodically