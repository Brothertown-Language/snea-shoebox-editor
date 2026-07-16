---
title: Retire dev branch — purge all references from docs and guidelines
status: draft
created: 2026-07-16
license: MIT
provenance: AI-generated
issue: 1356
authors:
  - OpenCode (deepseek-v4-flash-free)
---

**STATUS:** DRAFT
**CREATED:** 2026-07-16

> **Compliance Requirement:** All steps and sub-steps in this document MUST be followed in order. Failure to comply with any step — including but not limited to verification gates, test phases, audit checkpoints, and review steps — will result in the feature branch being rejected and discarded, requiring a full rework from scratch and loss of all prior work. There is no valid reason to skip, compress, reorder, or omit any step. If a step appears redundant or unnecessary, follow it anyway — the cost of following an extra step is negligible compared to the cost of rework from a skipped step.

## Problem

The `dev` branch has been merged into `main` (PR #1354) and is being retired. All documentation and guidelines that reference `dev` as a workflow target, integration branch, or process dependency must be purged. References to `dev` in generic prose (e.g., "local dev machines") are not affected.

## Context

The project previously used a `feature → dev → main` two-tier branch workflow. After PR #1354, `dev` has been merged into `main` and is no longer an active integration target. Documentation and guidelines that still reference `dev` as a workflow target will confuse developers and cause incorrect branch targeting.

The `dev` branch itself remains as a git ref for history preservation but MUST NOT be referenced in any workflow documentation.

## Goals

- Remove all documentation that describes the `dev` branch workflow
- Remove agent-facing exception for PRs merging to `dev`
- Update remaining doc references from `dev` to `main`
- Verify zero `dev` branch workflow references remain in docs

## Non-Goals

- **Changes to `.opencode/` directory** — Off-limits per project policy; any `dev` references in `.opencode/` are outside this spec's scope
- **Changes to `src/` code files** — Documentation-only change; no source code modifications
- **Generic uses of "dev" in prose** — "Development", "dev machine", "dev environment" are not workflow references and are excluded from this purge
- **Deleting the `dev` git branch** — The branch remains for history; only documentation references are purged

## Root Cause Analysis

The `dev` branch was the integration target in the two-tier `feature → dev → main` workflow. After migrating to a single-trunk workflow where `main` is the sole integration target, documentation was not updated to reflect the new workflow. This left stale references that could cause developers to target the wrong branch.

The root cause is not a code defect but a documentation gap: the workflow migration completed (PR #1354 merged `dev` into `main`) without a corresponding documentation cleanup pass.

## Alternatives Considered & Why Discarded

| Alternative | Rationale for Discard |
|-------------|----------------------|
| Inline-edit the files to replace `dev`→`main` in-place | The migration guide and dev workflow doc describe a workflow that no longer exists; editing them to describe `main` workflow would produce a confusing hybrid document. Deletion is cleaner. |
| Leave docs as-is with an addendum | Developers would need to read both old docs and addendum to understand the workflow, increasing cognitive load. Complete purge is clearer. |
| Add a deprecation notice to the docs | The workflow is already retired (PR #1354 merged). A deprecation period would extend confusion without benefit. |

## Affected Files

| File | Action | Anchor | Rationale |
|------|--------|--------|-----------|
| `docs/git-workflow-migration-guide.md` | DELETE | Entire file | Documents the `feature → dev → main` workflow that no longer exists |
| `docs/streamlit-dev-workflow.md` | DELETE | Entire file | Documents running from `dev` branch which is retired |
| `AGENTS.md` | REMOVE line | Line 52: Exception for PRs merging to `dev` | No longer applicable after `dev` retirement |
| `docs/security/credential-leakage-remediation.md` | UPDATE line 84 | `git push --force-with-lease origin dev` → `git push --force-with-lease origin main` | Still a valid doc; only the target branch reference needs updating |

## Success Criteria

| ID | Criterion | Verification Method | Remediation | Pipeline Step Binding | Artifact Path | Requirement Traceability | Phase Binding | Verification Gate | Integration Mode | Affinity Group | Re-Entry Step | Test File | Phase Mapping |
|----|-----------|-------------------|-------------|----------------------|--------------|-------------------------|--------------|-----------------|----------------|--------------|-------------|-----------|--------------|
| SC-1 | `docs/git-workflow-migration-guide.md` is deleted from the working tree | `test ! -f docs/git-workflow-migration-guide.md` | Re-run `git rm docs/git-workflow-migration-guide.md` | RED/GREEN | `.issues/1356/` | File deleted per spec | Phase 1 | pre-commit | independent | — | — | — | Phase 1 |
| SC-2 | `docs/streamlit-dev-workflow.md` is deleted from the working tree | `test ! -f docs/streamlit-dev-workflow.md` | Re-run `git rm docs/streamlit-dev-workflow.md` | RED/GREEN | `.issues/1356/` | File deleted per spec | Phase 1 | pre-commit | independent | — | — | — | Phase 1 |
| SC-3 | `AGENTS.md` line 52 (dev exception for PRs) is removed | `grep -c 'merging to \`dev\`' AGENTS.md` returns 0 | Re-edit `AGENTS.md` to remove the dev exception line | RED/GREEN | `.issues/1356/` | Line removed | Phase 2 | pre-commit | independent | — | — | — | Phase 2 |
| SC-4 | `docs/security/credential-leakage-remediation.md` line 84 references `origin main` not `origin dev` | `grep -c 'origin dev' docs/security/credential-leakage-remediation.md` returns 0 | Re-update line 84 from `origin dev` to `origin main` | RED/GREEN | `.issues/1356/` | Branch target updated | Phase 2 | pre-commit | independent | — | — | — | Phase 2 |
| SC-5 | No remaining `dev` branch workflow references in `docs/` directory | `grep -rn '\`dev\`' docs/` (excluding generic prose) returns only false positives or empty | Expand grep scope; update any missed references | VbC | `.issues/1356/` | Verification sweep zero | Phase 3 | post-implementation | independent | — | — | — | Phase 3 |
| SC-6 | No SC may be weakened, deferred, or reclassified to a lower evidence type to evade implementation | All SCs achieve PASS with their declared evidence type; behavioral SCs use test execution, not structural/grep substitution | The violating SC's evidence type is determined by the substrate question: if the change affects runtime behavior, the evidence type MUST be behavioral. Any SC found with mismatched evidence type after VbC classification gate MUST be reclassified and re-verified before pipeline proceeds. | VbC | `.issues/1356/` | SC integrity | Common | pre-commit | independent | — | — | — | Common |

## Implementation Approach

The work is straightforward file operations. Delete two entire documents, remove one line from `AGENTS.md`, and update one line in the credential leakage doc. A verification grep at the end confirms no stale `dev` branch workflow references remain.

## Risk and Edge Cases

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Missed `dev` reference in non-obvious file | Low | Medium | Verification grep covers all `docs/` files |
| References to `dev` as a git ref (not workflow) incorrectly removed | Low | Low | Only `\`dev\`` backtick patterns are targeted; generic "dev" in prose is explicit out-of-scope |
| `.opencode/` rules reference `dev` | Medium | Low | Out of scope per policy; `.opencode/` is off-limits |

## Interdependency

| Issue | Classification | Description |
|-------|---------------|-------------|
| [#1354](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1354) | RELATED | Merged `dev` → `main`; this spec is the documentation cleanup follow-up |

## Anti-Lobotomization

Tests MUST NOT be lobotomized. Removing or weakening a behavioral test assertion to work around a timeout, failure, or infrastructure issue is a CRITICAL VIOLATION. SCs must achieve 100% clean PASS. No SC may be weakened, deferred, or reclassified to a lower evidence type to evade implementation. Read [Test Integrity Mandate](guidelines/080-code-standards.md).

## Decision Ledger

| DEC-ID | Decision | Rationale | Requirement Key | Affected SCs |
|--------|----------|-----------|-----------------|--------------|
| DEC-1 | Delete rather than edit migration guide and dev workflow docs | The workflow described no longer exists; editing would produce a confusing hybrid | MUST | SC-1, SC-2 |
| DEC-2 | Update credential doc in-place rather than delete | The doc is still valid; only the target branch reference is stale | MUST | SC-4 |
| DEC-3 | Restrict grep verification to `\`dev\`` backtick patterns | Generic "dev" in prose ("development", "dev environment") is not a workflow reference | MUST | SC-5 |

## Documentation Sources

| Source Category | What Was Consulted | Purpose |
|----------------|-------------------|---------|
| Direct source search | `ls docs/git-workflow-migration-guide.md` | Verify file exists for deletion |
| Direct source search | `ls docs/streamlit-dev-workflow.md` | Verify file exists for deletion |
| Direct source search | `grep -n 'dev' AGENTS.md` | Confirm line 52 contains dev exception |
| Direct source search | `grep -n 'origin dev' docs/security/credential-leakage-remediation.md` | Confirm line 84 contains `origin dev` |
| Direct source search | `rg -n 'origin dev|\\`dev\\`' docs/` | Broader sweep for remaining dev references |

## Plan Format Requirements

After this spec is approved, the implementation plan MUST:
- Use the canonical `skill({name: "..."})` → `task(..., prompt: "execute <task> task from <skill>")` form for every dispatch step
- Not contain inline procedure text — the plan is a routing document, not a re-implementation of skill task cards
- Enumerate the full implementation pipeline: coherence gate, pre-red-baseline, RED/GREEN per item, VbC, audit, cross-validate, regression check, finishing checklist, review-prep, cleanup
- Use sequential per-item TDD: each RED must be immediately followed by its GREEN before the next RED begins

> **Compliance Requirement:** All steps and sub-steps in this document MUST be followed in order. Failure to comply with any step — including but not limited to verification gates, test phases, audit checkpoints, and review steps — will result in the feature branch being rejected and discarded, requiring a full rework from scratch and loss of all prior work. There is no valid reason to skip, compress, reorder, or omit any step. If a step appears redundant or unnecessary, follow it anyway — the cost of following an extra step is negligible compared to the cost of rework from a skipped step.

Co-authored with AI: OpenCode (deepseek-v4-flash-free)
