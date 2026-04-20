# Task: checklist

## Purpose

Run the completion checklist to verify a branch is fully ready for PR creation.

## Operating Protocol

1. Invoked by: `/skill finishing-a-development-branch --task checklist`
2. When to use: After `--task prepare` is complete
3. Exit criteria: All checklist items pass, compare URL verified, HALT and report readiness

## Branch Completion Checklist

```markdown
## Branch Completion Checklist

### Changes
- [ ] All changes committed
- [ ] No untracked files remaining
- [ ] Commit messages are descriptive
- [ ] Co-authored-by trailers present

### Code Quality
- [ ] `ruff check` passes (zero errors)
- [ ] `ruff format` applied
- [ ] `pyright` passes (zero errors)
- [ ] No dead code detected

### Tests
- [ ] All tests pass
- [ ] No skipped tests without reason
- [ ] New code has test coverage

### Branch
- [ ] Branch pushed to remote
- [ ] Upstream tracking set
- [ ] Compare URL generated
- [ ] Compare URL accessible

### Todowrite State
- [ ] No stale todowrite state (all items `completed` or cleared via `todowrite(todos=[])`)

### Documentation
- [ ] AI co-authored attribution in new files
- [ ] Module docstrings present
- [ ] No narration print statements

### Chat Output Format (MANDATORY — Zero Tolerance)
- [ ] Executive summary present as **first** chat output element (before any URL)
- [ ] Outcome line present after summary
- [ ] URL label is context-appropriate: "Compare URL" (pre-PR, `compare/dev...`) or "PR URL" (post-PR, `pull/N`) — label and URL format MUST match; mismatch is a critical violation
- [ ] URL present (after summary, before byline)
- [ ] AI byline in format `🤖 <AgentName> (<ModelId>) <status>` appears **last** (after URL)
- [ ] No URL before executive summary (CRITICAL VIOLATION if violated)
- [ ] No byline before URL (CRITICAL VIOLATION if violated)

**This format applies to EVERY halt point where implementation is reported complete:**
- review-prep after implementation
- Sub-agent result reports from divide-and-conquer dispatch
- Phase boundary halts (merge gates between phases)
- Approval-gate post-implementation reports

**Evidence requirement:** Verify format by reviewing chat output before marking this checklist item complete. Assertions without reviewing the actual output are VERIFICATION-GAP findings.

**Auto-fix on failure:** If any element is missing or misordered, fix the output before proceeding. Missing elements are MISSING-ELEMENT (auto-fix). Wrong ordering is STRUCTURE-VIOLATION (auto-fix).

### Ready for PR?
- [ ] All checklist items pass
- [ ] Compare URL verified

### Issue Closure Verification
- [ ] Verify all issues referenced by the merged PR are closed on GitHub
- [ ] If issues remain open after verified merge, close them with a comment referencing the merged PR

### Post-Merge Cleanup Verification
- [ ] `git-workflow --task cleanup` invoked after PR merge confirmation (CRITICAL — skipping is a guideline violation)
- [ ] Local dev branch synced with origin/dev (dev HEAD matches origin/dev HEAD)
- [ ] Merged feature branch deleted (local and remote)
- [ ] No stale worktrees remaining from the merged branch

### Sub-Issue Linkage Verification
- [ ] If the plan has multiple phases, verify that `get_sub_issues` count on the plan issue matches the number of phases in the plan body. If counts don't match, run `issue-operations --task link-sub-issue` to create missing linkages before proceeding to review-prep
```

## What Skills MUST Check

1. **Before reporting readiness:**

   - Is working tree clean?
   - Do all quality checks pass?
   - Is branch pushed?
   - Is compare URL accessible?

2. **During preparation:**

   - Are there leftover debug prints?
   - Are there TODO/FIXME comments?
   - Are there unrelated changes?

## Context Required

- Related skills: `finishing-a-development-branch` (parent skill), `verification-before-completion` (evidence)
- Related tasks: `prepare`

## Live Verification: Checklist Evidence (MANDATORY)

**Each checklist item MUST be verified via tool call, not just checked off. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Checklist Item | Verification Action | Tool Call | Problem Class |
|----------------|-------------------|-----------|---------------|
| "All changes committed" | Verify clean working tree | `git status --porcelain` → check empty | VERIFICATION-GAP |
| "Branch pushed to remote" | Verify tracking branch exists | `git branch -vv` → check `[origin/<branch>]` | MISSING-ELEMENT |
| "Tests passing" | Run actual test command | `uv run pytest test/` → check exit code | VERIFICATION-GAP |
| "Lint passing" | Run actual lint command | `uvx ruff check src/ test/` → check exit code | VERIFICATION-GAP |
| "No debug prints" | Search for debug statements | `grep(pattern="print\\(|debugger|breakpoint")` | STRUCTURE-VIOLATION |
| "No TODO/FIXME" | Search for placeholder comments | `grep(pattern="TODO|FIXME|HACK")` | STRUCTURE-VIOLATION |
| "No unrelated changes" | Verify diff scope matches spec | `git diff dev --name-only` → compare with spec files | CONFLICTING |

**Evidence artifact:** Tool call results for each checklist verification.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Uncommitted changes found | VERIFICATION-GAP | conditional | Commit before proceeding |
| Branch not pushed | MISSING-ELEMENT | auto-fix | Push immediately |
| Lint/test failures | VERIFICATION-GAP | flag-for-review | HALT — fix issues before PR |
| Debug prints or TODOs found | STRUCTURE-VIOLATION | auto-fix | Remove before proceeding |
| Unrelated files in diff | CONFLICTING | flag-for-review | Report — scope may have deviated |
