# Phase 2: Edit remaining references

## SC-to-Step Traceability

| SC ID | Criterion | Phase | Step(s) |
|-------|-----------|-------|---------|
| SC-3 | `AGENTS.md` line 52 — remove `dev` exception | 2 | 2.1, 2.3 |
| SC-4 | Credential doc line 84 — point to `main` | 2 | 2.2, 2.3 |

## Steps

### Step 2.1 — Edit `AGENTS.md`: remove `merging to \`dev\`` exception

- **Target**: Line 52: `merging to \`dev\`` — remove this line
- **Command**: `sed -i '/merging to `dev`/d' AGENTS.md` (or edit tool)
- **Pre-condition**: `grep -n 'merging to `dev`' AGENTS.md` returns line 52
- **Post-condition**: `grep -c 'merging to \`dev\`' AGENTS.md || echo 0` → returns 0
- **Mapping**: SC-3

### Step 2.2 — Edit `docs/security/credential-leakage-remediation.md`: replace `origin dev`

- **Target**: Line 84: replace `'origin dev'` with trunk branch reference
- **Command**: Use edit tool to change the line
- **Pre-condition**: `grep -n 'origin dev' docs/security/credential-leakage-remediation.md` returns line 84
- **Post-condition**: `grep -c 'origin dev' docs/security/credential-leakage-remediation.md || echo 0` → returns 0
- **Mapping**: SC-4

### Step 2.3 — Verify edits (string checks) + commit

- **Verify SC-3**: `grep -c 'merging to \`dev\`' AGENTS.md || echo 0` → expected: 0
- **Verify SC-4**: `grep -c 'origin dev' docs/security/credential-leakage-remediation.md || echo 0` → expected: 0
- **Evidence type**: string (SC-3, SC-4)
- **Gate**: pre-commit verification

## Safety/Rollback

- **Destructive operations**: Line edits (reversible via git)
- **Rollback plan**: `git checkout HEAD -- AGENTS.md docs/security/credential-leakage-remediation.md`
- **Data loss risk**: None — files are in git history

## Feasibility Verification

| Step | Reference | Verified? | Evidence |
|------|-----------|-----------|----------|
| 2.1 | `AGENTS.md` line 52 | ✅ | `grep -n 'merging' AGENTS.md` returned line 52 |
| 2.2 | `docs/security/credential-leakage-remediation.md` line 84 | ✅ | `grep -n 'origin dev' docs/security/credential-leakage-remediation.md` returned line 84 |

## Evidence/Provenance

| Claim | Evidence Source | Verified? |
|-------|----------------|----------|
| `AGENTS.md` line 52 contains `merging to \`dev\`` | `grep -n 'merging' AGENTS.md` | ✅ |
| Credential doc line 84 contains `origin dev` | `grep -n 'origin dev' docs/security/credential-leakage-remediation.md` | ✅ |

## Exit Criteria

- `grep -c 'merging to \`dev\`' AGENTS.md || echo 0` → 0 (SC-3: string)
- `grep -c 'origin dev' docs/security/credential-leakage-remediation.md || echo 0` → 0 (SC-4: string)
- Phase committed with message: `phase-2: remove inline dev-branch references`
