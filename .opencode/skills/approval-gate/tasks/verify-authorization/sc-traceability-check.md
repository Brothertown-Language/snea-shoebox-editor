# Task: verify-authorization — Step 4.6: Verify SC-to-Test Traceability, Behavioral Test Assertions, and RED-Phase Ordering

## Purpose

Before implementation proceeds, verify that the corresponding spec's success criteria have enforcement test assertions (BOTH content-verification AND behavioral where applicable) and that RED-phase ordering was followed. This gate applies at TWO checkpoints:

1. **Spec-creation RED gate** — When the spec was created (via `spec-creation` or `analyze-and-spec`), enforcement test assertions for each SC MUST have been written and verified in RED state BEFORE the spec was approved. This is enforced by the Step 0.5 RED gate in `spec-creation/tasks/write.md` and Step 4.1 in `issue-review/tasks/analyze-and-spec.md`.
2. **Implementation RED gate** — Each enforcement test assertion was written BEFORE the implementation commit for its corresponding item (the test was in RED state — exists and fails — before implementation began).

## Verification Checks

1. **Spec-creation RED gate was followed** — The spec's success criteria had enforcement test assertions written and verified in RED state before the spec was approved (not just before implementation). Evidence: `test-enforcement.sh` contains assertions referencing SC IDs from the spec, and those assertions were verified in RED state during spec creation.
2. **SC-to-test traceability exists** — For each success criterion in the corresponding spec, at least one enforcement test assertion references the SC ID (per `080-code-standards.md` SC-to-Test Traceability requirement)
3. **Behavioral test assertions for rule-changing SCs** — For each SC that changes agent behavior (guideline rules, skill enforcement, critical violations), at least one BEHAVIORAL enforcement test assertion must exist that verifies the agent's actual behavior, not just content presence in a file. Behavioral assertions use helpers from `.opencode/tests/behaviors/helpers.sh` (`assert_tool_calls_made`, `assert_forbidden_pattern_absent`, `assert_required_pattern_present`, `assert_skill_invoked`). A content-verification test (grep pattern) alone does NOT satisfy this requirement for rule-changing SCs — see `080-code-standards.md` → Behavioral Enforcement Tests (PRIMARY).
4. **RED-phase ordering confirmed** — Each enforcement test assertion was written BEFORE the implementation commit for its corresponding item (the test was in RED state — exists and fails — before implementation began)

## Procedure

```
# Read the corresponding spec
spec_issue = github_issue_read(method="get", issue_number=spec_number)
spec_body = spec_issue["body"]

# Parse success criteria from spec
success_criteria = parse_success_criteria(spec_body)

# 0. Verify spec-creation RED gate was followed
for sc in success_criteria:
    # Spec-creation RED gate: test assertions must exist and have been verified RED
    # during spec creation (Step 0.5 of spec-creation/tasks/write.md)
    has_spec_red_evidence = check_spec_creation_red_gate_evidence(sc["id"])
    if not has_spec_red_evidence:
        # VERIFICATION-GAP: No evidence that SC test assertions were verified RED during spec creation
        finding = f"SC {sc['id']}: no evidence that enforcement test assertions were verified in RED state during spec creation"
        action = "BLOCK; require spec-creation RED gate to be completed"
        severity = "VERIFICATION-GAP"

# For each SC, verify:
for sc in success_criteria:
    # 1. Traceability: enforcement test exists that references this SC ID
    has_test = check_enforcement_test_references_sc(sc["id"])
    if not has_test:
        # MISSING-TRACEABILITY: No enforcement test for SC
        finding = f"SC {sc['id']} has no corresponding enforcement test assertion"
        action = "BLOCK implementation; require test assertion with SC ID comment"
        severity = "MISSING-TRACEABILITY"

    # 2. Behavioral test assertion for rule-changing SCs
    if is_rule_changing_sc(sc):
        has_behavioral_test = check_behavioral_test_references_sc(sc["id"])
        if not has_behavioral_test:
            # MISSING-TRACEABILITY: Rule-changing SC has only content-verification test
            finding = f"SC {sc['id']} changes agent behavior but has no behavioral enforcement test — content-verification alone is insufficient for behavioral rule changes"
            action = "BLOCK implementation; require behavioral test assertion using helpers.sh"
            severity = "MISSING-TRACEABILITY"

    # 3. RED-phase ordering: test was written before implementation commit
    if has_test:
        test_commit = find_earliest_commit_for_test(sc["id"])
        impl_commit = find_earliest_commit_for_implementation(sc["id"])
        if test_commit and impl_commit and test_commit > impl_commit:
            # VERIFICATION-GAP: Test written after implementation (GREEN-without-RED)
            finding = f"SC {sc['id']}: test written after implementation (GREEN-without-RED)"
            action = "BLOCK; require test to be written first and shown to fail"
            severity = "VERIFICATION-GAP"
```

## Exemption

Existing SCs that were implemented before this mandate took effect are flagged but not blocked. RED-phase ordering is prospective (per `140-planning-spec-creation.md` constraints).

## Cross-Reference

See `080-code-standards.md` "SC-to-Test Traceability" and "RED-Phase Ordering" sections for the mandate. See `080-code-standards.md` "Behavioral Enforcement Tests (PRIMARY)" for the behavioral test requirement. See `091-incremental-build.md` for the per-item TDD cycle extended to SCs. See `spec-creation/tasks/write.md` Step 0.5 and `issue-review/tasks/analyze-and-spec.md` Step 4.1 for the content-creation RED gates that ensure enforcement test assertions exist before spec approval.

## Work State I/O

- **Reads from:** `## scope-auto-resolve`
- **Writes to:** `## sc-traceability-check`

After completing this task, write results to the work state file under section `## sc-traceability-check` using the YAML format defined in `enforcement/work-state-schema.md`.