# Git Protocol: PR Workflow

**See `pr-creation-workflow` skill for PR timing requirements including:**
- Authorization boundary (what authorizes implementation vs PR)
- Developer must test before PR
- HALT after PR creation

---

## Review Phase (Mandatory)

**⚠️ This phase is MANDATORY and AUTOMATIC — there is NO choice to skip it.**

After implementation completes and BEFORE PR creation authorization:

### Mandatory Post-Implementation Sequence

**The following sequence is MANDATORY after every implementation:**

1. **Commit all changes**:
   ```bash
   git add -A
   git commit -m "Descriptive message"
   ```

2. **Push feature branch to remote**:
   ```bash
   git push -u origin <branch-name>
   ```

3. **Generate GitHub compare URL**:
   ```
   https://github.com/<owner>/<repo>/compare/dev...<branch-name>
   ```

4. **Post compare URL to issue AND chat**:
   - GitHub Issue Comment: Full executive summary with compare URL
   - Chat Output: Same executive summary

5. **HALT and wait** for "create a PR" instruction

### Executive Summary Format (Mandatory)

**When reporting completion after review-prep, include:**

```
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

GitHub compare URL: https://github.com/<owner>/<repo>/compare/dev...<branch-name>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

**⚠️ CRITICAL: URL placement**

URL MUST be the final line of the comment - never in the middle and never in GitHub Issue comments (chat only).

| Context | Location | Summary Type | Contains URL? |
|---------|----------|--------------|---------------|
| GitHub Issue update (substantive) | GitHub Issue | Context-based | NO |
| Implementation complete | Chat | Executive summary | YES |
| PR created | Chat | PR URL only | YES |
| Issue closure | GitHub Issue | Closure summary | NO |

### Why This Matters

- Developers need visibility into ALL changes before PR creation
- GitHub diff viewer provides superior review experience
- Clear separation between "implementation done" and "PR requested"
- Compare URL is canonical way for developers to review branch changes
- Prevents accidental PRs without developer review

### Developer Review Flow

1. Agent posts compare URL
2. Developer reviews changes via GitHub diff viewer
3. Developer decides whether to create PR or request changes
4. If satisfied, developer says "create a PR"
5. Agent creates PR (squash, push, create PR, HALT)

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
| **Local** | `.githooks/pre-commit` | Blocks commit to `main` and `dev` | No |
| **Local** | `.githooks/post-commit` | Warns after commit to protected branches | N/A (post) |
| **Local** | `ai_bin/session_init.py` | Warns if hooks not installed | N/A (warning only) |
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
git reset --hard origin/dev

# Switch to recovery branch
git checkout feature/recovery

# Push and create PR
git push origin feature/recovery
```

---

## Enforcement Reference

**The git-workflow skill automatically enforces the review phase.**

- **After implementation completes** → `git-workflow` skill → `review-prep` task is invoked AUTOMATICALLY
- **Mandatory actions** → Push branch, generate compare URL, HALT
- **NO decision point** → Review-prep runs regardless of "minor changes" or "already reviewed"

**See `git-workflow` skill → `review-prep` task for the complete workflow.**

---

*Source: Content migrated from `110-git-protocol.md`*