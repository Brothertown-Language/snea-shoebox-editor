#!/bin/bash
# Phase 3: Decompose pre-implementation-analysis + screen-issue — Scoped Content-Verification Tests
#
# Tests that Phase 3 decomposition changes are correct:
# - pre-impl atomic tasks exist and are ≤3,000 words each
# - screen gate tasks exist and are ≤3,000 words each
# - SKILL.md is ≤4,000 words and references new atomic tasks
# - Old monolithic files are routing documents delegating to atomic tasks
#
# Follows #1236 principle: each phase tests only what it changes.
# Phase 3 does NOT test Phase 4/5/6/7 deliverables (chain-of-responsibility,
# remaining SKILL.md condensation, end-to-end verification, word-count metrics).
#
# Usage:  bash .opencode/tests/test-enforcement-phase3-scoped.sh
#         bash .opencode/tests/test-enforcement-phase3-scoped.sh --scenario SC-2

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
            echo "SC-2: pre-impl atomic tasks exist and are ≤3,000 words"
            echo "SC-3: screen gate tasks exist and are ≤3,000 words"
            echo "SC-6: approval-gate SKILL.md ≤4,000 words"
            echo "SC-pre-impl-routing: pre-implementation-analysis.md is routing file (≤500 words) delegating to pre-impl/"
            echo "SC-screen-routing: screen-issue.md is routing file (≤500 words) delegating to screen/"
            echo "SC-skill-refs: SKILL.md references Phase 3 atomic tasks in task list"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: bash .opencode/tests/test-enforcement-phase3-scoped.sh [--scenario NAME]... [--list]" >&2
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

# ── SC-2: pre-impl atomic tasks exist and are ≤3,000 words ──────────────

if should_run "SC-2"; then
    echo "=== SC-2: pre-impl atomic tasks exist and are ≤3,000 words ==="

    ATOMIC_DIR="$SKILLS_DIR/approval-gate/tasks/pre-impl"
    ATOMIC_TASKS=(
        "collect-screening-results.md"
        "reconcile-status.md"
        "build-dependency-graph.md"
        "check-cross-spec-overlap.md"
        "write-work-state.md"
        "yield-to-assemble-work.md"
    )

    ALL_EXIST=true
    ALL_WITHIN_LIMIT=true

    for f in "${ATOMIC_TASKS[@]}"; do
        FILE="$ATOMIC_DIR/$f"
        if [ ! -f "$FILE" ]; then
            report "SC-2" "FAIL" "Atomic task missing: $f"
            ALL_EXIST=false
        else
            WORDS=$(wc -w < "$FILE")
            if [ "$WORDS" -gt 3000 ]; then
                report "SC-2" "FAIL" "$f has $WORDS words (max 3,000)"
                ALL_WITHIN_LIMIT=false
            else
                echo "  $f: $WORDS words (≤3,000) ✓"
            fi
        fi
    done

    if [ "$ALL_EXIST" = true ] && [ "$ALL_WITHIN_LIMIT" = true ]; then
        report "SC-2" "PASS" "All 6 pre-impl atomic tasks exist and are ≤3,000 words"
    fi
fi

# ── SC-3: screen gate tasks exist and are ≤3,000 words ────────────────

if should_run "SC-3"; then
    echo "=== SC-3: screen gate tasks exist and are ≤3,000 words ==="

    GATE_DIR="$SKILLS_DIR/approval-gate/tasks/screen"
    GATE_TASKS=(
        "screen-issue-gate1.md"
        "screen-issue-gate2.md"
    )

    ALL_EXIST=true
    ALL_WITHIN_LIMIT=true

    for f in "${GATE_TASKS[@]}"; do
        FILE="$GATE_DIR/$f"
        if [ ! -f "$FILE" ]; then
            report "SC-3" "FAIL" "Gate task missing: $f"
            ALL_EXIST=false
        else
            WORDS=$(wc -w < "$FILE")
            if [ "$WORDS" -gt 3000 ]; then
                report "SC-3" "FAIL" "$f has $WORDS words (max 3,000)"
                ALL_WITHIN_LIMIT=false
            else
                echo "  $f: $WORDS words (≤3,000) ✓"
            fi
        fi
    done

    if [ "$ALL_EXIST" = true ] && [ "$ALL_WITHIN_LIMIT" = true ]; then
        report "SC-3" "PASS" "Both screen gate tasks exist and are ≤3,000 words"
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

# ── SC-pre-impl-routing: pre-implementation-analysis.md is routing file ──

if should_run "SC-pre-impl-routing"; then
    echo "=== SC-pre-impl-routing: pre-implementation-analysis.md is routing file (≤500 words) ==="

    ROUTING_FILE="$SKILLS_DIR/approval-gate/tasks/pre-implementation-analysis.md"
    if [ ! -f "$ROUTING_FILE" ]; then
        report "SC-pre-impl-routing" "FAIL" "Routing file not found: $ROUTING_FILE"
    else
        WORDS=$(wc -w < "$ROUTING_FILE")
        if [ "$WORDS" -gt 500 ]; then
            report "SC-pre-impl-routing" "FAIL" "Routing file has $WORDS words (max 500 for routing-only)"
        else
            if grep -q "collect-screening-results\|build-dependency-graph\|yield-to-assemble-work" "$ROUTING_FILE"; then
                report "SC-pre-impl-routing" "PASS" "Routing file has $WORDS words and delegates to pre-impl/ atomic tasks"
            else
                report "SC-pre-impl-routing" "FAIL" "Routing file has $WORDS words but does not delegate to pre-impl/ atomic tasks"
            fi
        fi
    fi
fi

# ── SC-screen-routing: screen-issue.md is routing file ──────────────────

if should_run "SC-screen-routing"; then
    echo "=== SC-screen-routing: screen-issue.md is routing file (≤500 words) ==="

    ROUTING_FILE="$SKILLS_DIR/approval-gate/tasks/screen-issue.md"
    if [ ! -f "$ROUTING_FILE" ]; then
        report "SC-screen-routing" "FAIL" "Routing file not found: $ROUTING_FILE"
    else
        WORDS=$(wc -w < "$ROUTING_FILE")
        if [ "$WORDS" -gt 500 ]; then
            report "SC-screen-routing" "FAIL" "Routing file has $WORDS words (max 500 for routing-only)"
        else
            if grep -q "screen-issue-gate1\|screen-issue-gate2\|tasks/screen/" "$ROUTING_FILE"; then
                report "SC-screen-routing" "PASS" "Routing file has $WORDS words and delegates to screen/ gate tasks"
            else
                report "SC-screen-routing" "FAIL" "Routing file has $WORDS words but does not delegate to screen/ gate tasks"
            fi
        fi
    fi
fi

# ── SC-skill-refs: SKILL.md references Phase 3 atomic tasks ───────────

if should_run "SC-skill-refs"; then
    echo "=== SC-skill-refs: SKILL.md references Phase 3 atomic tasks ==="

    SKILL_FILE="$SKILLS_DIR/approval-gate/SKILL.md"
    ATOMIC_REFS=(
        "collect-screening-results"
        "reconcile-status"
        "build-dependency-graph"
        "check-cross-spec-overlap"
        "write-work-state"
        "yield-to-assemble-work"
        "screen-issue/gate1"
        "screen-issue/gate2"
    )

    ALL_REFERENCED=true
    for ref in "${ATOMIC_REFS[@]}"; do
        if ! grep -q "$ref" "$SKILL_FILE" 2>/dev/null; then
            report "SC-skill-refs" "FAIL" "SKILL.md does not reference: $ref"
            ALL_REFERENCED=false
        else
            echo "  SKILL.md references $ref ✓"
        fi
    done

    if [ "$ALL_REFERENCED" = true ]; then
        report "SC-skill-refs" "PASS" "SKILL.md references all Phase 3 atomic tasks"
    fi
fi

# ── Summary ─────────────────────────────────────────────────────────────

echo ""
echo "=== Phase 3 Enforcement Test Results ==="
for result in "${RESULTS[@]}"; do
    echo "$result"
done
echo ""
echo "Passed: $PASS | Failed: $FAIL"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0