# Phase 4 Pipeline Plan — Search Logic Dispatch

**Spec:** [#400 [SPEC] Add Headword and Gloss Search Modes](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/400)
**Phase:** 4 (Backend Search Logic)
**Scope:** Strategy-dispatch for search mode routing in `search_records()`, `get_all_records_for_export()`, `stream_records_to_temp_file()`
**Authorization Required:** `for_implementation` or above (Phase 4 NOT labeled `approved-for-phase-4`)

---

## 1. Pipeline Structure

All 14 steps follow the `implementation-pipeline` skill's serial dispatch model with Z3-verified state transitions. Each step produces a YAML artifact at `./tmp/{issue-N}/artifacts/pipeline-{step_label}-{STATUS}-{timestamp}.yaml`.

**Dispatch pattern:** 13 of 14 steps are **blind dispatch** (sub-agent via `task()` with routing metadata only). Only `pre-red-baseline` is orchestrator inline (simple bash: mkdir + solve state update + artifact cleanup).

### Dispatch Target Summary

| # | Step | Dispatch Target | Blind? | When to Skip |
|---|------|----------------|--------|-------------|
| 1 | sc-coherence-gate | `adversarial-audit` coherence-extraction | YES | If no SCs reference Phase 4 |
| 2 | pre-red-baseline | Orchestrator inline (bash) | NO | Never — always required before RED |
| 3 | red-phase | `test-driven-development` red | YES | If SC type is `structural` or `semantic` only |
| 4 | red-doublecheck | `verification-before-completion` verify | YES | If SC evidence type is `structural` (no behavioral test) |
| 5 | green-phase | `test-driven-development` green | YES | Never — RED without GREEN is incomplete |
| 6 | checkpoint-commit | `git-workflow` commit-prep | YES | Never — checkpoint before structural checks |
| 7 | structural-checks | `finishing-a-development-branch` checklist | YES | If structural checks pass on first try |
| 8 | green-doublecheck | `verification-before-completion` verify | YES | If green-phase has zero lint/type errors |
| 9 | green-vbc | `verification-before-completion` completion | YES | Never — every item must pass VbC |
| 10 | adversarial-audit | `adversarial-audit` verification-audit | YES | If GREEN-phase structural checks already passed |
| 11 | cross-validate | `adversarial-audit` cross-validate | YES | If adversarial-audit passed |
| 12 | regression-check | `test-driven-development` patterns | YES | If no regression in related SCs |
| 13 | review-prep | `git-workflow` review-prep | YES | Never — mandatory before PR |
| 14 | exec-summary | `completion-core` completion | YES | Never — final step |

---

## 2. Blind Dispatch Protocol

For each step labeled "Blind? YES", the orchestrator provides ONLY:

```yaml
dispatch_context:
  must_receive:
    - adventure_scope: for_implementation
    - halt_at: verification_complete
    - pr_strategy: stacked
  must_not_receive:
    - file_paths (pre-determined)
    - line_numbers
    - expected_outcomes
    - orchestrator_reasoning
    - cached_results
    - derivation_traces
```

The sub-agent independently:
1. Discovers affected files via codebase search
2. Designs test cases from spec SCs
3. Determines refactoring approach
4. Verifies own work

**Result contract** (returned to orchestrator):
```yaml
status: DONE | BLOCKED | DONE_WITH_CONCERNS
finding_summary: 1-3 sentences
artifact_path: ./tmp/{issue-N}/artifacts/pipeline-{step_label}-{STATUS}-{timestamp}.yaml
blocker_reason: required only if BLOCKED
```

---

## 3. Z3 Contract Gates

Pipeline state machine is defined in `./tmp/400-pipeline/pipeline-contract.yaml` (18 variables, 37 invariants, 4 postconditions). Verified SAT on init state.

### Step Transition Gates

Each gate checks preconditions before advancing `current_step`:

| From Step | To Step | Gate Check |
|-----------|---------|------------|
| sc-coherence-gate | pre-red-baseline | `sc_coherence` ∈ {passed, failed} |
| pre-red-baseline | red-phase | `pre_red_baseline == done` |
| red-phase | red-doublecheck | `red_phase == done` |
| red-doublecheck | green-phase | `red_doublecheck` ∈ {passed, failed} |
| green-phase | checkpoint-commit | `green_phase == done` |
| checkpoint-commit | structural-checks | `checkpoint_commit == committed` |
| structural-checks | green-doublecheck | `structural_checks` ∈ {passed, failed} |
| green-doublecheck | green-vbc | `green_doublecheck` ∈ {passed, failed} |
| green-vbc | adversarial-audit | `green_vbc` ∈ {done, failed} |
| adversarial-audit | cross-validate | `adversarial_audit` ∈ {passed, failed} |
| cross-validate | regression-check | `cross_validate` ∈ {passed, failed} |
| regression-check | review-prep | `regression_check` ∈ {passed, failed} |
| review-prep | exec-summary | `review_prep == done` |
| exec-summary | complete | `exec_summary == done` |

### Rollback Protocol

On failure at any gate:
1. Report diagnostics (`git status`, `git diff --stat`)
2. Read pipeline state → determine `$LAST_PASS_PHASE`
3. Execute rollback: `git reset --hard <parent>/checkpoint/<issue>/phase-<LAST_PASS_PHASE>-<submodule> && git submodule update --init`
4. Read restored pipeline state
5. Re-dispatch failed step with original parameters

---

## 4. Item Decomposition

Phase 4 is a single-item phase (one concern: search dispatch). No sub-items.

### Affected Files

| File | Concern | Change Description |
|------|---------|-------------------|
| `src/services/linguistic_service.py` | Search dispatch | Add Headword/Gloss strategy-dispatch to `search_records()` (line 325), `get_all_records_for_export()` (line 462), `stream_records_to_temp_file()` (~line 560) |
| `src/database/core.py` (if needed) | Query helpers | Add `HeadwordSearchEntry`/`GlossSearchEntry` query builders |
| `tests/services/test_linguistic_service.py` | Test coverage | Add behavioral tests for SC-1 through SC-8, SC-14, SC-24, SC-25 |

### SCs Covered by Phase 4

| SC | Evidence Type | Concern | Test Name |
|----|--------------|---------|-----------|
| SC-1 | behavioral | Headword finds primary lx | `test_headword_search_primary_lx` |
| SC-2 | behavioral | Headword finds primary va | `test_headword_search_primary_va` |
| SC-3 | behavioral | Headword excludes nested va | `test_headword_excludes_nested_va` |
| SC-4 | behavioral | Gloss finds primary ge | `test_gloss_search_primary_ge` |
| SC-5 | behavioral | Gloss excludes nested ge | `test_gloss_excludes_nested_ge` |
| SC-6 | behavioral | Gloss excludes headword | `test_gloss_excludes_headword` |
| SC-7 | behavioral | Lexeme mode UNCHANGED | `test_lexeme_mode_unchanged` |
| SC-8 | behavioral | FTS mode UNCHANGED | `test_fts_mode_unchanged` |
| SC-14 | behavioral | Search performance <500ms | `test_search_performance` |
| SC-24 | behavioral | Empty input no crash | `test_empty_search_input` |
| SC-25 | behavioral | Special chars no crash | `test_special_characters_search` |

---

## 5. Artifact Output

Each pipeline step writes to `./tmp/400-pipeline/artifacts/`:

```
pipeline-sc-coherence-gate-{STATUS}-{ts}.yaml
pipeline-pre-red-baseline-{STATUS}-{ts}.yaml
pipeline-red-phase-{STATUS}-{ts}.yaml
pipeline-red-doublecheck-{STATUS}-{ts}.yaml
pipeline-green-phase-{STATUS}-{ts}.yaml
pipeline-checkpoint-commit-{STATUS}-{ts}.yaml
pipeline-structural-checks-{STATUS}-{ts}.yaml
pipeline-green-doublecheck-{STATUS}-{ts}.yaml
pipeline-green-vbc-{STATUS}-{ts}.yaml
pipeline-adversarial-audit-{STATUS}-{ts}.yaml
pipeline-cross-validate-{STATUS}-{ts}.yaml
pipeline-regression-check-{STATUS}-{ts}.yaml
pipeline-review-prep-{STATUS}-{ts}.yaml
pipeline-exec-summary-{STATUS}-{ts}.yaml
```

### Artifact Schema

```yaml
step: <step_label>
status: PASS | FAIL | SKIP | BLOCKED
timestamp: <ISO-8601>
checkpoint_tag: <parent>/checkpoint/<issue>/phase-<N>-<submodule>
evidence:
  - type: behavioral|semantic|string|structural
    source: <tool/command used>
    result: <summary>
contract_state: <path to state.yaml after step>
blocker_reason: <optional>
```

---

## 6. Solve State Management

State file at `./tmp/400-pipeline/state/state.yaml` manages the Z3 contract.

### State Update After Each Step

```bash
./.opencode/tools/solve state update ./tmp/400-pipeline/state/ \
  -n current_step -v <next-step-label> \
  -n <step-label> -v passed|done \
  --contract-path ./tmp/400-pipeline/pipeline-contract.yaml
```

### Contract Validation After Each State Update

```bash
./.opencode/tools/solve check \
  --state-path ./tmp/400-pipeline/state/state.yaml \
  --contract-path ./tmp/400-pipeline/pipeline-contract.yaml
```

---

## 7. Execution Workflow

For each item in the decomposition:

### per-item loop:
1. **sc-coherence-gate** — Verify spec coherence against codebase (sub-agent: adversarial-audit coherence-extraction)
2. **pre-red-baseline** — Create pipeline artifacts, update solve state, clean previous artifacts
3. **red-phase** — Write behavioral tests that FAIL (RED phase of TDD)
4. **red-doublecheck** — Verify RED tests actually fail (sub-agent: verification-before-completion verify)
5. **green-phase** — Implement code to make RED tests pass (GREEN phase of TDD)
6. **checkpoint-commit** — Git commit with solve state checkpoint tag
7. **structural-checks** — Lint, type check, format (finishing-a-development-branch checklist)
8. **green-doublecheck** — Verify GREEN code passes all tests (verification-before-completion verify)
9. **green-vbc** — Full verification-before-completion for item
10. **adversarial-audit** — Cross-family adversarial audit of implementation
11. **cross-validate** — Cross-validate audit results
12. **regression-check** — Verify no regressions in related SCs
13. **review-prep** — Prepare for code review (git-workflow review-prep)
14. **exec-summary** — Produce completion summary

---

## 8. Rollback Tag Convention

Checkpoints use pattern: `<parent-repo>/checkpoint/<issue>/phase-<N>-<submodule>`

For Phase 4 of issue #400:

```
snea-shoebox-editor/checkpoint/400/phase-4-snea-shoebox-editor
```

Each per-item gate advance produces:
```bash
git tag snea-shoebox-editor/checkpoint/400/phase-4-snea-shoebox-editor
```

---

## 9. Implementation Checklist

### Pre-Flight (before Phase 4 starts)
- [ ] Z3 contract validated (SAT on preconditions + invariants + postconditions) — **DONE**
- [ ] Solve state initialized at `./tmp/400-pipeline/state/state.yaml` — **DONE**
- [ ] Phase 4 approved label (`approved-for-phase-4`) present on issue #400
- [ ] `authorization_scope` set to `for_implementation` or above

### Per-Step Execution
- [ ] Step 1: SC coherence gate — verify spec SCs reference real code paths
- [ ] Step 2: Pre-RED baseline — artifacts ready, solve state updated
- [ ] Step 3: RED phase — behavioral tests for SC-1–SC-8, SC-14, SC-24, SC-25
- [ ] Step 4: RED double-check — all RED tests FAIL as expected
- [ ] Step 5: GREEN phase — strategy-dispatch for search_records + export + stream
- [ ] Step 6: Checkpoint commit — tagged and solve state updated
- [ ] Step 7: Structural checks — lint, typecheck, format pass
- [ ] Step 8: GREEN double-check — all tests PASS
- [ ] Step 9: GREEN VbC — full verification before completion
- [ ] Step 10: Adversarial audit — cross-family verification
- [ ] Step 11: Cross-validate — audit consensus check
- [ ] Step 12: Regression check — no regressions in Lexeme/FTS modes
- [ ] Step 13: Review prep — PR-ready branch
- [ ] Step 14: Exec summary — completion report

### Post-Phase
- [ ] Solve state: `exec_summary == done`, `pipeline_state == complete`
- [ ] Z3 contract check: SAT on final state
- [ ] All artifacts in `./tmp/400-pipeline/artifacts/`
- [ ] PR created against `dev`
- [ ] Phase 4 marked complete in spec body

---

## 10. Files That Must NOT Change

These files are specified as regression invariants in the spec:

| File | Invariant |
|------|-----------|
| `src/database/models/search.py` | NO changes to existing `SearchEntry` |
| `src/database/models/core.py` | NO changes to existing `Record.search_entries` |
| `src/services/upload_service.py` | NO changes to existing `SearchEntry` population |
| `src/database/migrations.py` | NO migration changes — Phase 3 migrations already ran |
| `src/frontend/pages/records.py` | NO UI changes — Phase 5 handles this |
