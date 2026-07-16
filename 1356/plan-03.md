# Phase 3: Verification sweep

## SC-to-Step Traceability

| SC ID | Criterion | Phase | Step(s) |
|-------|-----------|-------|---------|
| SC-5 | No `dev` branch workflow references in `docs/` | 3 | 3.1, 3.2 |
| SC-6 | No SC weakened or deferred | 3 | 3.2 (cross-cutting audit) |

## Steps

### Step 3.1 — Grep sweep `docs/` for stale `dev` references

- **Pattern**: `(scripts from \`dev\`|branch.*dev|origin dev|to \`dev\`|base.*\bdev\b|merging to \`dev\`)`
- **Command**: `grep -rnE '(scripts from \`dev\`|branch.*\bdev\b|origin dev|to \`dev\`|base.*\bdev\b|merging to \`dev\`)' docs/`
- **Pre-condition**: Files from Phase 1 are deleted, edits from Phase 2 applied
- **Expected**: 0 matches (SC-5)
- **Evidence type**: string

### Step 3.2 — Anti-lobotomization audit (SC-6)

- **Review**: Read all three phases' diffs. Confirm no behavioral test assertion was removed, weakened, or reclassified.
- **Check**: No SC's evidence type was downgraded. No behavioral assertion was replaced with grep/string.
- **Evidence type**: behavioral
- **Gate**: `behavioral-test-evaluation` clean-room dispatch after artifact generation

## Safety/Rollback

- **Destructive operations**: None (read-only grep sweep)
- **Rollback plan**: N/A — verification is read-only
- **Data loss risk**: None

## Feasibility Verification

| Step | Reference | Verified? | Evidence |
|------|-----------|-----------|----------|
| 3.1 | `docs/` directory | ✅ | `ls docs/` confirmed exists |
| 3.2 | SC-6 spec text | ✅ | Read from spec.md |

## Evidence/Provenance

| Claim | Evidence Source | Verified? |
|-------|----------------|----------|
| `docs/` directory exists | `ls docs/` | ✅ |
| SC-6 is cross-cutting anti-lobotomization | `sc-summary.yaml` | ✅ |

## Exit Criteria (post-implementation gate)

- `grep -rnE '(scripts from \`dev\`|branch.*\bdev\b|origin dev|to \`dev\`|base.*\bdev\b|merging to \`dev\`)' docs/` → 0 matches (SC-5: string)
- Clean-room `behavioral-test-evaluation` dispatch returns PASS for SC-6 (behavioral)
- ALL 6 SCs verified as PASS before the implementation is claimed complete
- Post-sweep: commit with message `phase-3: verify no stale dev references remain`
- Full verification-before-completion gate pass
- Finishing-a-development-branch checklist
- PR creation
