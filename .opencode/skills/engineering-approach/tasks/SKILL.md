# Task: implement-design

## Purpose

Execute implementation after design is approved, following established design decisions.

## Entry Criteria

- Design approved by user
- Spec has STATUS with approved phases

## Exit Criteria

- Implementation completed per design
- All success criteria verified
- Tests passing (if applicable)

## Procedure

### Step 1: Verify Design Approval

**Check:**
- User explicitly approved design with "approved", "go", or "approved: N.M"
- STATUS field shows approved phases
- No `needs-approval` label blocking

### Step 2: Execute Implementation

**For each approved phase:**
1. Create feature branch (if not exists)
2. Implement per design specification
3. Run linting/type checking
4. Run tests (if applicable)
5. Commit with proper trailers

### Step 3: Verify Success Criteria

**From spec:**
- [ ] Success criterion 1 verified
- [ ] Success criterion 2 verified
- [ ] Success criterion 3 verified

### Step 4: Report Completion

**Post to GitHub Issue:**
```markdown
**Summary:**

<1-2 sentences describing impact>

**Outcome:** <What changed>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

### Step 5: HALT

- Do NOT create PR automatically
- Wait for explicit "create a PR" instruction

## Common Issues

| Issue | Resolution |
|-------|------------|
| Design not approved | HALT, wait for approval |
| Tests failing | Fix tests, re-verify |
| Lint errors | Fix, re-run |
| Scope creep | Report, ask for clarification |

## Context Required

- Session values: GIT_OWNER, GIT_REPO, DEV_NAME, DEV_EMAIL
- Related tasks: `verify-understanding`, `verify-design`
