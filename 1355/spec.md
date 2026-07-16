---
title: Migrate to trunk-based development — retire dev branch
status: draft
created: 2026-07-16
license: MIT
provenance: AI-generated
issue: 1355
authors:
  - OpenCode (deepseek-v4-flash-free)
---

**STATUS:** DRAFT
**CREATED:** 2026-07-16

> **Compliance Requirement:** All steps and sub-steps in this document MUST be followed in order. Failure to comply with any step — including but not limited to verification gates, test phases, audit checkpoints, and review steps — will result in the feature branch being rejected and discarded, requiring a full rework from scratch and loss of all prior work. There is no valid reason to skip, compress, reorder, or omit any step. If a step appears redundant or unnecessary, follow it anyway — the cost of following an extra step is negligible compared to the cost of rework from a skipped step.

## Problem

The current workflow uses `dev` as an accumulation branch: feature branches merge into `dev`, then `dev` merges into `main` via release PRs. As of this writing, `dev` is 139 commits ahead of `main` (verified by `git rev-list --count main..dev`). This accumulation-branch model creates:

- A persistent gap between development and production code
- Complex release coordination across the dev→main boundary
- Branch confusion in AGENTS.md directives that reference `dev` and `main` as distinct workflow targets

The goal is to make `main` the single trunk where all work targets directly, retiring the `dev` branch entirely.

## Anti-Lobotomization

Tests MUST NOT be lobotomized. Removing or weakening a behavioral test assertion to work around a timeout, failure, or infrastructure issue is a CRITICAL VIOLATION. SCs must achieve 100% clean PASS. No SC may be weakened, deferred, or reclassified to a lower evidence type to evade implementation. Read [Test Integrity Mandate](guidelines/080-code-standards.md).

## Scope

### In Scope

1. **AGENTS.md** — Remove dev-specific workflow instructions (the sync script instruction referencing `dev`, the "Feature PRs merging to `dev`" exception). Add note that `.opencode/` directory is off-limits and not managed by the main repo.
2. **docs/git-workflow-migration-guide.md** — Update to reflect trunk-based workflow (all branches target `main`, no `dev` stage).
3. **docs/streamlit-dev-workflow.md** — Update or archive as appropriate.
4. **Delete `dev` branch** — Locally and remotely after migration is complete, ensuring `main` is fast-forwarded to include all 139 commits from `dev`.

### Out of Scope

- `.opencode/` directory — off-limits, must not be modified
- Feature branch workflow changes — already handled by opencode skills
- Release process changes — already handled by opencode skills
- Changes to application source code (`src/`) — no stale `dev` branch references found in application code (verified by `grep`); all `dev` references in `src/database/connection.py` refer to "local development", not the `dev` git branch

## Key Considerations

- `dev` is 139 commits ahead of `main` (verified: `git rev-list --count main..dev` = 139, `git rev-list --count dev..main` = 0). Migration MUST fast-forward `main` to match `dev` (or equivalent merge strategy) before `dev` can be deleted.
- No open PRs should target `dev` at migration time — verify before deletion.
- The `.opencode/` submodule directory is managed separately and MUST NOT be modified by this spec.

## Alternative Approaches Considered

- **Keep dev as a long-lived integration branch**: Discarded — defeats the purpose of trunk-based development, maintains the 139-commit gap.
- **Cherry-pick specific commits from dev to main**: Discarded — all 139 commits represent legitimate work destined for main; a fast-forward is the correct low-risk strategy.
- **Delete dev without merging**: Discarded — would lose 139 commits of work.

## After this spec is approved

Invoke `writing-plans` to create `.issues/1355/plan.md` before implementation begins.

## Success Criteria

| ID | Criterion | Verification Method | Remediation | Pipeline Step Binding | Artifact Path | Requirement Traceability | Phase Binding | Verification Gate | Integration Mode | Affinity Group | Re-Entry Step | Test File | Phase Mapping |
|----|-----------|-------------------|-------------|----------------------|--------------|-------------------------|--------------|-----------------|----------------|--------------|-------------|-----------|--------------|
| SC-1 | AGENTS.md updated: dev-specific workflow instructions removed | `grep -n 'dev' AGENTS.md` — confirm no references to `dev` as merge target or workflow branch (except `.opencode/` off-limits note) | If stale refs remain, edit AGENTS.md and re-verify | spec-creation | `.issues/1355/spec.md` | Root cause: AGENTS.md defines dev-centric workflow | Phase 1 | string | sequential | — | — | — | Phase 1 |
| SC-2 | AGENTS.md updated: `.opencode/` off-limits note added | `grep -c '.opencode/' AGENTS.md` — confirm `.opencode/ off-limits` note is present | Add note if missing | spec-creation | `.issues/1355/spec.md` | Root cause: AGENTS.md needs boundary declaration | Phase 1 | string | sequential | — | — | — | Phase 1 |
| SC-3 | docs/git-workflow-migration-guide.md updated to trunk-based model | `grep -c 'trunk-based\|main' docs/git-workflow-migration-guide.md` — confirm content references `main` as the single trunk, no stale `dev` workflow references | Rewrite doc to trunk-based model | spec-creation | `.issues/1355/spec.md` | Root cause: docs reflect dev-centric workflow | Phase 2 | string | sequential | — | — | — | Phase 2 |
| SC-4 | docs/streamlit-dev-workflow.md updated or deleted | File either does not exist OR its content references `main` as the only trunk | If file exists with stale dev refs, update or delete | spec-creation | `.issues/1355/spec.md` | Root cause: docs reflect dev-centric workflow | Phase 2 | string | sequential | — | — | — | Phase 2 |
| SC-5 | `dev` branch deleted locally and remotely after migration | `git branch -a | grep -c '\sdev$'` — confirm no local `dev` branch; `git ls-remote origin dev | wc -l` — confirm no remote `dev` branch | If branch still exists, force-delete | post-implementation | `.issues/1355/spec.md` | Root cause: dev branch is the physical artifact of the accumulation model | Phase 3 | structural | sequential | — | — | — | Phase 3 |
| SC-6 | All application files still reference `main` as the only trunk (no stale dev references) | `grep -rn "'dev'" src/ --include="*.py"` — no stale `dev` branch references in application code (existing false positives for "local dev" documented) | If stale refs found, update to remove dev branch association | post-implementation verification | `.issues/1355/spec.md` | Root cause: stale dev references in code | Phase 3 | string | sequential | — | — | — | Phase 3 |
| SC-7 | No SC may be weakened, deferred, or reclassified to a lower evidence type to evade implementation | Auditor confirms all SCs implemented at declared evidence type or higher | HALT, report blocker | post-implementation | `.issues/1355/spec.md` | Anti-lobotomization gate | All | behavioral | — | — | — | — | All |

## Edge Cases & Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `dev` may have open PRs that would be orphaned | Low | High | Verify no open PRs targeting `dev` before deletion |
| Fast-forward merge of 139 commits introduces regression | Low | Medium | Run test suite after fast-forward before deleting `dev` |
| CI/CD pipelines reference `dev` branch | Medium | High | Check CI configs for `dev` branch references as part of migration |
| Team members have local `dev` checkouts | High | Low | Communicate branch deletion; stale local refs are harmless |

## Decision Ledger

| DEC-ID | Decision | Rationale | Requirement Key | Affected SCs |
|--------|----------|-----------|-----------------|--------------|
| DEC-1 | Fast-forward `main` to `dev` | Linear history, no merge commit, preserves commit authorship and ordering | MUST | SC-5 |
| DEC-2 | `.opencode/` declared off-limits in AGENTS.md | Prevents accidental modifications to the agent configuration submodule | MUST | SC-2 |

## Interdependency

No interdependencies with other open issues exist at creation time.

## Documentation Sources

| Source Category | What Was Consulted | Purpose |
|----------------|-------------------|---------|
| Direct source search | `grep -rn '"dev"' src/ --include="*.py" --include="*.md"` | Verify no stale dev branch references in application code |
| Direct source search | `grep -n 'dev' AGENTS.md` | Identify dev-specific workflow instructions to remove |
| Direct source search | `ls docs/git-workflow-migration-guide.md docs/streamlit-dev-workflow.md` | Verify docs exist for updating |
| Live verification | `git rev-list --count main..dev` | Establish dev is 139 commits ahead of main |
| Live verification | `git branch -a` | Confirm dev branch exists locally and remotely |

## Revision Policy

| Artifact | Cascade Trigger | Action on Parent Revision |
|----------|----------------|---------------------------|
| Implementation plan | MUST | Revise to match revised spec |
| Behavioral tests | SHOULD | Review for continued validity |
| Risk traceability | MAY | Update if new risks introduced |
