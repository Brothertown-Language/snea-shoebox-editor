#!/bin/bash
# Phase 2: Decompose verify-authorization — Scoped Content-Verification Tests
#
# Tests that Phase 2 decomposition changes are correct:
# - Atomic tasks exist and are ≤3,000 words each
# - SKILL.md is ≤4,000 words (routing document)
# - Old monolithic verify-authorization.md is a routing file (≤500 words)
# - SKILL.md references new atomic tasks in its task list
#
# Follows #1236 principle: each phase tests only what it changes.
# Phase 2 does NOT test Phase 3/4/5 deliverables (pre-impl-analysis, 
# screen-issue, chain-of-responsibility, remaining SKILL.md condensation).
#
# Usage:  bash .opencode/tests/test-enforcement-phase2-scoped.sh
#         bash .opencode/tests/test-enforcement-phase2-scoped.sh --scenario SC-1

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILLS_DIR="$PROJECT_DIR/.opencode/skills"

SCENARIO_FILTER=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --scenario)
            SCENARIO_FILTER+=("$2")
            shift 2
            ;;
        --list)
            echo "SC-1: verify-authorization atomic tasks exist and are ≤3,000 words"
            echo "SC-1-naming: Atomic task files match spec naming"
            echo "SC-6: approval-gate SKILL.md ≤4,000 words"
            echo "SC-routing: Old verify-authorization.md is routing file (≤500 words)"
            echo "SC-skill-refs: SKILL.md references atomic tasks in task list"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: bash .opencode/tests/test-enforcement-phase2-scoped.sh [--scenario NAME]... [--list]" >&2
            exit 1
            ;;
    esac
done

PASS=0
FAIL=0
RESULTS=()

report() {
    local scenario="$1"
    local status="$2"
    local detail="$3"
    RESULTS+=("$scenario | $status | $detail")
    if [ "$status" = "PASS" ]; then
        PASS=$((PASS + 1))
    else
        FAIL=$((FAIL + 1))
    fi
}

should_run() {
    local scenario="$1"
    if [ ${#SCENARIO_FILTER[@]} -eq 0 ]; then
        return 0
    fi
    for f in "${SCENARIO_FILTER[@]}"; do
        if [ "$f" = "$scenario" ]; then
            return 0
        fi
    done
    return 1
}

# ── SC-1: verify-authorization atomic tasks exist and are ≤3,000 words ──────

if should_run "SC-1"; then
    echo "=== SC-1: verify-authorization atomic tasks exist and are ≤3,000 words ==="

    ATOMIC_DIR="$SKILLS_DIR/approval-gate/tasks/verify-authorization"
    ATOMIC_TASKS=(
        "scope-auto-resolve.md"
        "item-decomposition-check.md"
        "sc-traceability-check.md"
        "sub-issue-verification.md"
        "spec-to-plan-cascade.md"
        "gap-fill-cascade.md"
        "auto-dispatch.md"
    )

    ALL_EXIST=true
    ALL_WITHIN_LIMIT=true

    for f in "${ATOMIC_TASKS[@]}"; do
        FILE="$ATOMIC_DIR/$f"
        if [ ! -f "$FILE" ]; then
            report "SC-1" "FAIL" "Atomic task missing: $f"
            ALL_EXIST=false
        else
            WORDS=$(wc -w < "$FILE")
            if [ "$WORDS" -gt 3000 ]; then
                report "SC-1" "FAIL" "$f has $WORDS words (max 3,000)"
                ALL_WITHIN_LIMIT=false
            else
                echo "  $f: $WORDS words (≤3,000) ✓"
            fi
        fi
    done

    if [ "$ALL_EXIST" = true ] && [ "$ALL_WITHIN_LIMIT" = true ]; then
        report "SC-1" "PASS" "All 7 atomic tasks exist and are ≤3,000 words"
    fi
fi

# ── SC-1-naming: Atomic task files match spec naming ──────────────────────

if should_run "SC-1-naming"; then
    echo "=== SC-1-naming: Atomic task files match spec naming ==="

    ATOMIC_DIR="$SKILLS_DIR/approval-gate/tasks/verify-authorization"
    SPEC_NAMES=(
        "scope-auto-resolve"
        "item-decomposition-check"
        "sc-traceability-check"
        "sub-issue-verification"
        "spec-to-plan-cascade"
        "gap-fill-cascade"
        "auto-dispatch"
    )

    ALL_MATCH=true
    for name in "${SPEC_NAMES[@]}"; do
        if [ ! -f "$ATOMIC_DIR/$name.md" ]; then
            report "SC-1-naming" "FAIL" "Missing atomic task file: $name.md"
            ALL_MATCH=false
        else
            echo "  $name.md exists ✓"
        fi
    done

    if [ "$ALL_MATCH" = true ]; then
        report "SC-1-naming" "PASS" "All atomic task files match spec naming"
    fi
fi

# ── SC-6: approval-gate SKILL.md ≤4,000 words ──────────────────────────

if should_run "SC-6"; then
    echo "=== SC-6: approval-gate SKILL.md ≤4,000 words ==="

    SKILL_FILE="$SKILLS_DIR/approval-gate/SKILL.md"
    if [ ! -f "$SKILL_FILE" ]; then
        report "SC-6" "FAIL" "SKILL.md not found: $SKILL_FILE"
    else
        WORDS=$(wc -w < "$SKILL_FILE")
        if [ "$WORDS" -gt 4000 ]; then
            report "SC-6" "FAIL" "SKILL.md has $WORDS words (max 4,000)"
        else
            report "SC-6" "PASS" "SKILL.md has $WORDS words (≤4,000)"
        fi
    fi
fi

# ── SC-routing: Old verify-authorization.md is routing file (≤500 words) ──

if should_run "SC-routing"; then
    echo "=== SC-routing: verify-authorization.md is routing file (≤500 words) ==="

    ROUTING_FILE="$SKILLS_DIR/approval-gate/tasks/verify-authorization.md"
    if [ ! -f "$ROUTING_FILE" ]; then
        report "SC-routing" "FAIL" "Routing file not found: $ROUTING_FILE"
    else
        WORDS=$(wc -w < "$ROUTING_FILE")
        if [ "$WORDS" -gt 500 ]; then
            report "SC-routing" "FAIL" "Routing file has $WORDS words (max 500 for routing-only)"
        else
            # Also verify it delegates to sub-tasks
            if grep -q "scope-auto-resolve\|item-decomposition-check\|sub-issue-verification" "$ROUTING_FILE"; then
                report "SC-routing" "PASS" "Routing file has $WORDS words and delegates to atomic tasks"
            else
                report "SC-routing" "FAIL" "Routing file has $WORDS words but does not delegate to atomic tasks"
            fi
        fi
    fi
fi

# ── SC-skill-refs: SKILL.md references atomic tasks in task list ────────

if should_run "SC-skill-refs"; then
    echo "=== SC-skill-refs: SKILL.md references atomic tasks in task list ==="

    SKILL_FILE="$SKILLS_DIR/approval-gate/SKILL.md"
    ATOMIC_REFS=(
        "scope-auto-resolve"
        "item-decomposition-check"
        "sc-traceability-check"
        "sub-issue-verification"
        "spec-to-plan-cascade"
        "gap-fill-cascade"
        "auto-dispatch"
    )

    ALL_REFERENCED=true
    for ref in "${ATOMIC_REFS[@]}"; do
        if ! grep -q "$ref" "$SKILL_FILE" 2>/dev/null; then
            report "SC-skill-refs" "FAIL" "SKILL.md does not reference atomic task: $ref"
            ALL_REFERENCED=false
        else
            echo "  SKILL.md references $ref ✓"
        fi
    done

    if [ "$ALL_REFERENCED" = true ]; then
        report "SC-skill-refs" "PASS" "SKILL.md references all atomic tasks"
    fi
fi

# ── Summary ─────────────────────────────────────────────────────────────

echo ""
echo "=== Phase 2 Enforcement Test Results ==="
for result in "${RESULTS[@]}"; do
    echo "$result"
done
echo ""
echo "Passed: $PASS | Failed: $FAIL"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0