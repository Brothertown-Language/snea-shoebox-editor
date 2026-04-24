#!/bin/bash
# Content Verification: dispatch and dispatch-multi DispatchResult schema
#
# Verifies that:
# 1. dispatch.md produces correct DispatchResult schema (status, modality, model_used, findings, evidence_artifacts, unverified_modalities, error)
# 2. dispatch.md documents nested sub-agent architecture (REQ-6)
# 3. dispatch.md prevents circular dispatch
# 4. dispatch-multi.md produces correct per-modality DispatchResult list
# 5. Both tasks handle graceful degradation (REQ-5)
#
# Co-authored with AI: OpenCode (ollama-cloud/glm-5.1)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"

OVERALL_RESULT=0

echo "=== Content Verification: dispatch DispatchResult schema ==="

DISPATCH_FILE="$PROJECT_DIR/.opencode/skills/multimodal-dispatch/tasks/dispatch.md"

# Check 1: DispatchResult schema fields are documented
if [ -f "$DISPATCH_FILE" ]; then
    # Required schema fields
    for field in status modality model_used findings evidence_artifacts unverified_modalities error; do
        FIELD_COUNT=$(grep -c "$field" "$DISPATCH_FILE" 2>/dev/null || echo "0")
        if [ "$FIELD_COUNT" -ge 1 ]; then
            echo "  dispatch.md DispatchResult.$field: PASS"
        else
            echo "  dispatch.md DispatchResult.$field: FAIL (not found)"
            OVERALL_RESULT=1
        fi
    done

    # Check 2: Status values are documented
    STATUS_VALUES=$(grep -c "completed.*partial.*unverified.*failed\|completed | partial | unverified | failed" "$DISPATCH_FILE" 2>/dev/null || echo "0")
    if [ "$STATUS_VALUES" -ge 1 ]; then
        echo "  dispatch.md status values documented: PASS"
    else
        echo "  dispatch.md status values documented: FAIL"
        OVERALL_RESULT=1
    fi

    # Check 3: Nested sub-agent architecture (REQ-6)
    NESTED_COUNT=$(grep -c "nested\|sub-agent\|dispatch chain\|re-invokes\|circular" "$DISPATCH_FILE" 2>/dev/null || echo "0")
    if [ "$NESTED_COUNT" -ge 2 ]; then
        echo "  dispatch.md nested sub-agents (REQ-6): PASS (found $NESTED_COUNT references)"
    else
        echo "  dispatch.md nested sub-agents (REQ-6): FAIL (found $NESTED_COUNT references, need >= 2)"
        OVERALL_RESULT=1
    fi

    # Check 4: Circular dispatch prevention
    CIRCULAR_COUNT=$(grep -c "circular\|re-invokes\|call chain\|calling skill" "$DISPATCH_FILE" 2>/dev/null || echo "0")
    if [ "$CIRCULAR_COUNT" -ge 1 ]; then
        echo "  dispatch.md circular dispatch prevention: PASS"
    else
        echo "  dispatch.md circular dispatch prevention: FAIL"
        OVERALL_RESULT=1
    fi

    # Check 5: FAIL never downgraded
    FAIL_COUNT=$(grep -ci "FAIL.*never.*downgrad\|never downgraded\|downgrad.*FAIL" "$DISPATCH_FILE" 2>/dev/null || echo "0")
    if [ "$FAIL_COUNT" -ge 1 ]; then
        echo "  dispatch.md FAIL invariant: PASS"
    else
        echo "  dispatch.md FAIL invariant: FAIL"
        OVERALL_RESULT=1
    fi

    # Check 6: Graceful degradation
    UNVERIFIED_DEGRADE=$(grep -c "unverified\|never block\|graceful" "$DISPATCH_FILE" 2>/dev/null || echo "0")
    if [ "$UNVERIFIED_DEGRADE" -ge 2 ]; then
        echo "  dispatch.md graceful degradation (REQ-5): PASS (found $UNVERIFIED_DEGRADE references)"
    else
        echo "  dispatch.md graceful degradation (REQ-5): FAIL (found $UNVERIFIED_DEGRADE references)"
        OVERALL_RESULT=1
    fi
else
    echo "  dispatch.md exists: FAIL (file not found)"
    OVERALL_RESULT=1
fi

# Check 7: dispatch-multi.md exists and has multi-modality support
DISPATCH_MULTI_FILE="$PROJECT_DIR/.opencode/skills/multimodal-dispatch/tasks/dispatch-multi.md"
if [ -f "$DISPATCH_MULTI_FILE" ]; then
    echo "  dispatch-multi.md exists: PASS"

    MULTI_MOD=$(grep -c "multi-modality\|per-modality\|modalities\|DispatchResult" "$DISPATCH_MULTI_FILE" 2>/dev/null || echo "0")
    if [ "$MULTI_MOD" -ge 3 ]; then
        echo "  dispatch-multi.md multi-modality support: PASS (found $MULTI_MOD references)"
    else
        echo "  dispatch-multi.md multi-modality support: FAIL (found $MULTI_MOD references, need >= 3)"
        OVERALL_RESULT=1
    fi

    AGGREGATE=$(grep -c "aggregate\|overall status\|combine\|per-modality" "$DISPATCH_MULTI_FILE" 2>/dev/null || echo "0")
    if [ "$AGGREGATE" -ge 2 ]; then
        echo "  dispatch-multi.md result aggregation: PASS (found $AGGREGATE references)"
    else
        echo "  dispatch-multi.md result aggregation: FAIL (found $AGGREGATE references, need >= 2)"
        OVERALL_RESULT=1
    fi

    DEGRADE_MULTI=$(grep -c "unverified\|never block\|graceful" "$DISPATCH_MULTI_FILE" 2>/dev/null || echo "0")
    if [ "$DEGRADE_MULTI" -ge 1 ]; then
        echo "  dispatch-multi.md graceful degradation (REQ-5): PASS"
    else
        echo "  dispatch-multi.md graceful degradation (REQ-5): FAIL"
        OVERALL_RESULT=1
    fi
else
    echo "  dispatch-multi.md exists: FAIL (file not found)"
    OVERALL_RESULT=1
fi

echo ""
if [ "$OVERALL_RESULT" -eq 0 ]; then
    echo "PASS: dispatch DispatchResult schema verification"
else
    echo "FAIL: dispatch DispatchResult schema verification"
fi

exit $OVERALL_RESULT