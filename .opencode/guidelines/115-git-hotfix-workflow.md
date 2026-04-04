# Git Protocol: Hotfix Workflow

## Overview

Hotfixes are urgent fixes that must be applied to production (`main`) and then backported to the integration branch (`dev`).

---

## Branch Structure

| Branch | Purpose | Protection |
|--------|---------|------------|
| `main` | Production (Streamlit Cloud) | No direct commits |
| `dev` | Integration testing | No direct commits |
| `hotfix/*` | Urgent production fixes | Allowed |

---

## Hotfix Workflow

### When to Use Hotfix

A hotfix is appropriate when:

1. **Production is broken** — Critical bug affecting users
2. **Security vulnerability** — Urgent security patch needed
3. **Data corruption** — Immediate fix required
4. **No time for normal PR workflow** — Must deploy immediately

A hotfix is **NOT** appropriate for:

- Regular feature development (use normal workflow)
- Low-priority bugs (use normal workflow)
- Cosmetic changes (use normal workflow)

---

## Hotfix Procedure

### Step 1: Create Hotfix Branch from main

```bash
git checkout main
git pull origin main
git checkout -b hotfix/urgent-fix
```

**Critical:** Hotfix branches MUST branch from `main`, not `dev`.

---

### Step 2: Implement Fix

Make the minimum necessary changes to fix the issue:

- Keep hotfixes small and focused
- Fix ONLY the urgent issue
- Do NOT include unrelated improvements

Commit with descriptive message:

```bash
git add -A
git commit -m "fix: <description of hotfix>"
```

---

### Step 3: Create PR Targeting main

```bash
git push -u origin hotfix/urgent-fix
```

Create PR:
- Base: `main`
- Head: `hotfix/urgent-fix`
- Labels: `hotfix`
- Request expedited review

---

### Step 4: After Merge to main

**After human merges the hotfix PR to `main`:**

1. **Sync to `dev`:**
   ```bash
   git checkout dev
   git merge main
   git push origin dev
   ```
   
   Or create a PR from `main` to `dev` if preferred.

2. **Delete hotfix branch:**
   ```bash
   git branch -d hotfix/urgent-fix
   git push origin --delete hotfix/urgent-fix
   ```

---

## Why Merge main to dev?

Hotfixes must reach `dev` so that:

- Integration branch has the fix
- Future releases don't regress the fix
- Feature branches created from `dev` include the fix
- No merge conflicts when `dev` eventually merges to `main`

---

## Enforcement

### Pre-commit Hook

Hotfix branches pass the pre-commit hook because they are not `main` or `dev`:

```bash
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "dev" ]; then
    # Block commits
    exit 1
fi
# hotfix/* branches are allowed
```

### Agent Behavior

- **Agent does NOT create hotfix branches** without explicit developer instruction
- **Agent does NOT merge hotfix PRs** — human only
- **Agent can suggest hotfix workflow** when production issue is identified

---

## Summary

| Step | Action | Branch |
|------|--------|--------|
| 1 | Create hotfix branch | `hotfix/*` from `main` |
| 2 | Implement fix | `hotfix/*` |
| 3 | Create PR | Target `main` |
| 4 | Human merges | `main` |
| 5 | Sync to dev | `dev` ← `main` |
| 6 | Delete branch | Cleanup |

---

*Source: Created for main/dev/feature workflow*