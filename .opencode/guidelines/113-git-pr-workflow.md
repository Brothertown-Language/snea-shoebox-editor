# Git Protocol: PR Workflow

**See `pr-creation-workflow` skill for PR timing requirements including:**
- Authorization boundary (what authorizes implementation vs PR)
- Developer must test before PR
- HALT after PR creation

---

## Review Phase (Mandatory)

After implementation completes and BEFORE PR creation authorization:

1. **Agent pushes feature branch** to remote:
   ```bash
   git push -u origin <branch-name>
   ```

2. **Agent provides GitHub compare URL**:
   ```
   https://github.com/<owner>/<repo>/compare/main...<branch-name>
   ```

3. **Developer reviews changes** via GitHub diff viewer
4. **Developer decides** whether to create PR or request changes
5. **If satisfied, developer says** "create a PR"
6. **Agent creates PR** (squash, push, create PR, HALT)

**Why This Matters:**
- Developer can review changes before PR exists
- Clear separation between "implementation done" and "PR requested"
- No accidental PR creation without developer visibility
- GitHub diff viewer is superior to local review

---

## PR Requirements

- Reference issue: `Fixes #123` in PR description
- Pass CI checks
- **Human review required** — Copilot review is supplemental, not sufficient for merge

---

## 🚫 ABSOLUTE PROHIBITION: AGENTS MUST NEVER MERGE PRs

- **PR merging is HUMAN-ONLY.** The agent MUST NOT call `github_merge_pull_request` at any time.
- **ALL PRs require human review before merge** — no exceptions, no self-merging.
- **"go" does NOT authorize merging.** "go" means "proceed to the next task or phase" — NOT "merge the PR".
- After PR creation, the agent MUST report the PR URL and HALT.
- If PR is open and user says "go", the agent must clarify that merging requires explicit "merge" instruction.

---

## Enforcement Mechanisms

### Multi-Layer Defense

| Layer | Mechanism | Scope | Bypassable? |
|-------|-----------|-------|-------------|
| **Local** | `.githooks/pre-commit` | Blocks commit to main | No |
| **Local** | `.githooks/post-commit` | Warns after commit to main | N/A (post) |
| **GitHub** | Branch protection rules | Requires PR | No |

**There is NO emergency bypass.** If you need to make an urgent fix:
1. Create a feature branch: `git checkout -b hotfix/urgent-fix`
2. Make your changes and commit
3. Push and create PR with `hotfix` label
4. Request expedited review

### Recovery from Accidental Main Commit

If you somehow committed to main locally (hooks not installed):

```bash
# Create recovery branch from the commit
git branch feature/recovery HEAD

# Reset main to match remote
git checkout main
git reset --hard origin/main

# Switch to recovery branch
git checkout feature/recovery

# Push and create PR
git push origin feature/recovery
```

---

*Source: Content migrated from `110-git-protocol.md`*