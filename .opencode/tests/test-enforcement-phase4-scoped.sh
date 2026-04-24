#!/bin/bash
# Phase 4: Chain-of-Responsibility Orchestrator — Scoped Content-Verification Tests
#
# Tests that Phase 4 chain-of-responsibility changes are correct:
# - work-state-schema exists and is ≤500 words
# - verify-authorization atomic tasks have "Work State I/O" sections
# - pre-impl atomic tasks have "Work State I/O" sections
# - screen gate tasks have "Work State I/O" sections
# - SKILL.md contains fast/medium/full path routing docs
# - SKILL.md is ≤4,000 words
#
# Follows #1236 principle: focused scenarios, no uber tests.
# Phase 4 does NOT test Phase 1/2/3 deliverables (enforcement extraction,
# verify-authorization decomposition, pre-impl/screen decomposition).
#
# Usage:  bash .opencode/tests/test-enforcement-phase4-scoped.sh
#         bash .opencode/tests/test-enforcement-phase4-scoped.sh --scenario SC-work-state-schema

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
            echo "SC-work-state-schema: work-state-schema.md exists and ≤500 words"
            echo "SC-chain-io-verify-auth: ≥5 verify-authorization atomic tasks have Work State I/O section"
            echo "SC-chain-io-pre-impl: ≥4 pre-impl atomic tasks have Work State I/O section"
            echo "SC-chain-io-screen: ≥2 screen gate tasks have Work State I/O section"
            echo "SC-skill-paths: SKILL.md contains fast-path, medium-path, and full-path routing docs"
            echo "SC-skill-word-count: SKILL.md is ≤4,000 words"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: bash .opencode/tests/test-enforcement-phase4-scoped.sh [--scenario NAME]... [--list]" >&2
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

# ── SC-work-state-schema: work-state-schema.md exists and ≤500 words ───

if should_run "SC-work-state-schema"; then
    echo "=== SC-work-state-schema: work-state-schema.md exists and ≤500 words ==="

    SCHEMA_FILE="$SKILLS_DIR/approval-gate/enforcement/work-state-schema.md"
    if [ ! -f "$SCHEMA_FILE" ]; then
        report "SC-work-state-schema" "FAIL" "work-state-schema.md not found: $SCHEMA_FILE"
    else
        WORDS=$(wc -w < "$SCHEMA_FILE")
        if [ "$WORDS" -gt 500 ]; then
            report "SC-work-state-schema" "FAIL" "work-state-schema.md has $WORDS words (max 500)"
        else
            report "SC-work-state-schema" "PASS" "work-state-schema.md has $WORDS words (≤500)"
        fi
    fi
fi

# ── SC-chain-io-verify-auth: ≥5 verify-authorization tasks have Work State I/O ──

if should_run "SC-chain-io-verify-auth"; then
    echo "=== SC-chain-io-verify-auth: ≥5 verify-authorization atomic tasks have Work State I/O section ==="

    VERIFY_AUTH_DIR="$SKILLS_DIR/approval-gate/tasks/verify-authorization"
    IO_COUNT=0

    if [ -d "$VERIFY_AUTH_DIR" ]; then
        for f in "$VERIFY_AUTH_DIR"/*.md; do
            [ -f "$f" ] || continue
            if grep -q "^## Work State I/O" "$f" 2>/dev/null; then
                IO_COUNT=$((IO_COUNT + 1))
                echo "  $(basename "$f"): has Work State I/O ✓"
            else
                echo "  $(basename "$f"): missing Work State I/O"
            fi
        done
    fi

    if [ "$IO_COUNT" -ge 5 ]; then
        report "SC-chain-io-verify-auth" "PASS" "$IO_COUNT verify-authorization tasks have Work State I/O (≥5 required)"
    else
        report "SC-chain-io-verify-auth" "FAIL" "Only $IO_COUNT verify-authorization tasks have Work State I/O (need ≥5)"
    fi
fi

# ── SC-chain-io-pre-impl: ≥4 pre-impl tasks have Work State I/O ──────────

if should_run "SC-chain-io-pre-impl"; then
    echo "=== SC-chain-io-pre-impl: ≥4 pre-impl atomic tasks have Work State I/O section ==="

    PRE_IMPL_DIR="$SKILLS_DIR/approval-gate/tasks/pre-impl"
    IO_COUNT=0

    if [ -d "$PRE_IMPL_DIR" ]; then
        for f in "$PRE_IMPL_DIR"/*.md; do
            [ -f "$f" ] || continue
            if grep -q "^## Work State I/O" "$f" 2>/dev/null; then
                IO_COUNT=$((IO_COUNT + 1))
                echo "  $(basename "$f"): has Work State I/O ✓"
            else
                echo "  $(basename "$f"): missing Work State I/O"
            fi
        done
    fi

    if [ "$IO_COUNT" -ge 4 ]; then
        report "SC-chain-io-pre-impl" "PASS" "$IO_COUNT pre-impl tasks have Work State I/O (≥4 required)"
    else
        report "SC-chain-io-pre-impl" "FAIL" "Only $IO_COUNT pre-impl tasks have Work State I/O (need ≥4)"
    fi
fi

# ── SC-chain-io-screen: ≥2 screen gate tasks have Work State I/O ────────

if should_run "SC-chain-io-screen"; then
    echo "=== SC-chain-io-screen: ≥2 screen gate tasks have Work State I/O section ==="

    SCREEN_DIR="$SKILLS_DIR/approval-gate/tasks/screen"
    IO_COUNT=0

    if [ -d "$SCREEN_DIR" ]; then
        for f in "$SCREEN_DIR"/*.md; do
            [ -f "$f" ] || continue
            if grep -q "^## Work State I/O" "$f" 2>/dev/null; then
                IO_COUNT=$((IO_COUNT + 1))
                echo "  $(basename "$f"): has Work State I/O ✓"
            else
                echo "  $(basename "$f"): missing Work State I/O"
            fi
        done
    fi

    if [ "$IO_COUNT" -ge 2 ]; then
        report "SC-chain-io-screen" "PASS" "$IO_COUNT screen gate tasks have Work State I/O (≥2 required)"
    else
        report "SC-chain-io-screen" "FAIL" "Only $IO_COUNT screen gate tasks have Work State I/O (need ≥2)"
    fi
fi

# ── SC-skill-paths: SKILL.md contains fast/medium/full path routing ──────

if should_run "SC-skill-paths"; then
    echo "=== SC-skill-paths: SKILL.md contains fast-path, medium-path, and full-path routing docs ==="

    SKILL_FILE="$SKILLS_DIR/approval-gate/SKILL.md"
    if [ ! -f "$SKILL_FILE" ]; then
        report "SC-skill-paths" "FAIL" "SKILL.md not found: $SKILL_FILE"
    else
        PATHS_FOUND=0
        for path_name in "fast-path" "medium-path" "full-path"; do
            if grep -q "$path_name" "$SKILL_FILE" 2>/dev/null; then
                PATHS_FOUND=$((PATHS_FOUND + 1))
                echo "  $path_name: found ✓"
            else
                echo "  $path_name: missing"
            fi
        done

        if [ "$PATHS_FOUND" -eq 3 ]; then
            report "SC-skill-paths" "PASS" "SKILL.md contains all 3 chain-of-responsibility paths"
        else
            report "SC-skill-paths" "FAIL" "SKILL.md contains $PATHS_FOUND/3 chain-of-responsibility paths"
        fi
    fi
fi

# ── SC-skill-word-count: SKILL.md ≤4,000 words ──────────────────────────

if should_run "SC-skill-word-count"; then
    echo "=== SC-skill-word-count: SKILL.md ≤4,000 words ==="

    SKILL_FILE="$SKILLS_DIR/approval-gate/SKILL.md"
    if [ ! -f "$SKILL_FILE" ]; then
        report "SC-skill-word-count" "FAIL" "SKILL.md not found: $SKILL_FILE"
    else
        WORDS=$(wc -w < "$SKILL_FILE")
        if [ "$WORDS" -gt 4000 ]; then
            report "SC-skill-word-count" "FAIL" "SKILL.md has $WORDS words (max 4,000)"
        else
            report "SC-skill-word-count" "PASS" "SKILL.md has $WORDS words (≤4,000)"
        fi
    fi
fi

# ── Summary ─────────────────────────────────────────────────────────────

echo ""
echo "=== Phase 4 Enforcement Test Results ==="
for result in "${RESULTS[@]}"; do
    echo "$result"
done
echo ""
echo "Passed: $PASS | Failed: $FAIL"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0