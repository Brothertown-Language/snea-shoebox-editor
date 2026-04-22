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
🤖 <AgentName> (<ModelId>) completed
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

- Session values: <github.owner>, <github.repo>, <dev.name>, <dev.email>
- Related tasks: `verify-understanding`, `verify-design`

## Live Verification: Engineering Claims (MANDATORY)

**Each engineering checkpoint MUST produce a tool-call artifact. Assertions without artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Understanding verified" | Confirm code reading happened | `srclight_get_symbol` or `read` tool records | VERIFICATION-GAP |
| "Design approved" | Confirm approval exists from developer | `github_issue_read(method=get_comments)` → check for auth | CONFLICTING |
| "Implementation within scope" | Verify changes match spec file list | `git diff dev --name-only` → compare with spec | CONFLICTING |
| "Tests pass" | Run actual test suite | `uv run pytest test/` → check exit code | VERIFICATION-GAP |

**Evidence artifact:** Tool call results for each checkpoint.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Code not read during understanding | VERIFICATION-GAP | conditional | Read now before proceeding |
| No approval found | CONFLICTING | flag-for-review | HALT — needs authorization |
| Changes outside spec scope | CONFLICTING | flag-for-review | Report scope deviation |
| Test failures | VERIFICATION-GAP | flag-for-review | Fix before claiming complete |
