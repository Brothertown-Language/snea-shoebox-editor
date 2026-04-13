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

### Documentation
- [ ] AI co-authored attribution in new files
- [ ] Module docstrings present
- [ ] No narration print statements

### Ready for PR?
- [ ] All checklist items pass
- [ ] Compare URL verified
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
