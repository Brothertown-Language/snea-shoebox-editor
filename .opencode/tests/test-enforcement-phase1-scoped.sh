#!/bin/bash
# Phase 1 Enforcement Extraction — Scoped Content-Verification Tests
#
# Tests that Phase 1 (enforcement extraction) changes are correct:
# - Enforcement modules exist and have content
# - Surviving task files reference modules instead of embedding definitions
# - No embedded model definitions in surviving task files
#
# Follows the #1236 principle: each phase tests only what it changes.
#
# Usage:  bash .opencode/tests/test-enforcement-phase1-scoped.sh
#         bash .opencode/tests/test-enforcement-phase1-scoped.sh --scenario SC-4

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
            echo "SC-4: Enforcement modules exist"
            echo "SC-5-scoped: No embedded enforcement model definitions in surviving task files"
            echo "SC-4-wordcount: Enforcement modules have content"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: bash .opencode/tests/test-enforcement-phase1-scoped.sh [--scenario NAME]... [--list]" >&2
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

# ── SC-4: Enforcement modules exist ──────────────────────────────────

if should_run "SC-4"; then
    echo "=== SC-4: Enforcement modules exist ==="

    AG_MODULES=(
        "adversarial-verification.md"
        "scope-parsing.md"
        "auto-dispatch-table.md"
        "closed-issue-verification.md"
        "sub-issue-graph-traversal.md"
    )
    DC_MODULES=(
        "completion-checkpoint.md"
        "result-validation.md"
        "overflow-signal.md"
        "work-state-verification.md"
    )

    all_found=true

    for module in "${AG_MODULES[@]}"; do
        path="$SKILLS_DIR/approval-gate/enforcement/$module"
        if [ -f "$path" ] && [ -s "$path" ]; then
            echo "  OK: approval-gate/enforcement/$module exists and non-empty"
        else
            echo "  FAIL: approval-gate/enforcement/$module missing or empty"
            all_found=false
        fi
    done

    for module in "${DC_MODULES[@]}"; do
        path="$SKILLS_DIR/divide-and-conquer/enforcement/$module"
        if [ -f "$path" ] && [ -s "$path" ]; then
            echo "  OK: divide-and-conquer/enforcement/$module exists and non-empty"
        else
            echo "  FAIL: divide-and-conquer/enforcement/$module missing or empty"
            all_found=false
        fi
    done

    if [ "$all_found" = true ]; then
        report "SC-4" "PASS" "All 9 enforcement modules exist and are non-empty"
    else
        report "SC-4" "FAIL" "One or more enforcement modules missing or empty"
    fi
fi

# ── SC-5-scoped: No embedded enforcement model definitions in surviving task files ──

if should_run "SC-5-scoped"; then
    echo "=== SC-5-scoped: No embedded enforcement model definitions in surviving task files ==="

    # Files scheduled for decomposition — EXCLUDED from this check
    EXCLUDED_FILES=(
        "verify-authorization.md"
        "pre-implementation-analysis.md"
        "screen-issue.md"
    )
    # Also exclude the verify-authorization/ subdirectory
    EXCLUDED_DIRS=(
        "verify-authorization"
    )

    # Build excluded path patterns
    EXCLUDE_PATTERN=""
    for ex in "${EXCLUDED_FILES[@]}"; do
        if [ -n "$EXCLUDE_PATTERN" ]; then
            EXCLUDE_PATTERN="$EXCLUDE_PATTERN|"
        fi
        EXCLUDE_PATTERN="${EXCLUDE_PATTERN}${ex}"
    done

    # Pattern 1: Evidence Artifact Format definition — the 4-line code block template
    # This is the MODEL DEFINITION, not task-specific "Evidence artifact: github_issue_read(...)" lines
    EVIDENCE_MODEL_PATTERN='Check: \[what was verified\]'
    # Also match the broader code block context: "Evidence Artifact Format" heading in a task file
    EVIDENCE_HEADING_PATTERN='^## Evidence Artifact Format$'

    # Pattern 2: Three-tier Finding Classification definition — the table row with "auto-fix | Safe, mechanical"
    # This is the MODEL DEFINITION, not task-specific finding tables
    THREE_TIER_PATTERN='auto-fix.*Safe.*mechanical'

    has_violations=false
    violations=()

    # Check approval-gate surviving task files
    for taskfile in "$SKILLS_DIR/approval-gate/tasks/"*.md; do
        basename=$(basename "$taskfile")

        # Skip excluded files (scheduled for decomposition)
        skip=false
        for ex in "${EXCLUDED_FILES[@]}"; do
            if [ "$basename" = "$ex" ]; then
                skip=true
                break
            fi
        done
        if [ "$skip" = true ]; then
            continue
        fi

        # Check for embedded evidence model definition
        if grep -q "$EVIDENCE_MODEL_PATTERN" "$taskfile" 2>/dev/null; then
            has_violations=true
            violations+=("approval-gate/tasks/$basename: contains embedded Evidence Artifact Format code block template")
        fi

        # Check for embedded three-tier classification definition
        if grep -q "$THREE_TIER_PATTERN" "$taskfile" 2>/dev/null; then
            has_violations=true
            violations+=("approval-gate/tasks/$basename: contains embedded three-tier Finding Classification definition")
        fi
    done

    # Check divide-and-conquer surviving task files
    for taskfile in "$SKILLS_DIR/divide-and-conquer/tasks/"*.md; do
        basename=$(basename "$taskfile")

        if grep -q "$EVIDENCE_MODEL_PATTERN" "$taskfile" 2>/dev/null; then
            has_violations=true
            violations+=("divide-and-conquer/tasks/$basename: contains embedded Evidence Artifact Format code block template")
        fi

        if grep -q "$THREE_TIER_PATTERN" "$taskfile" 2>/dev/null; then
            has_violations=true
            violations+=("divide-and-conquer/tasks/$basename: contains embedded three-tier Finding Classification definition")
        fi
    done

    # Check that references to enforcement modules DO exist in surviving files (positive check)
    # At least some surviving files should reference enforcement/ modules
    reference_count=0
    for taskfile in "$SKILLS_DIR/approval-gate/tasks/"*.md; do
        basename=$(basename "$taskfile")
        skip=false
        for ex in "${EXCLUDED_FILES[@]}"; do
            if [ "$basename" = "$ex" ]; then
                skip=true
                break
            fi
        done
        if [ "$skip" = true ]; then
            continue
        fi

        if grep -q 'enforcement/' "$taskfile" 2>/dev/null; then
            reference_count=$((reference_count + 1))
        fi
    done

    for taskfile in "$SKILLS_DIR/divide-and-conquer/tasks/"*.md; do
        if grep -q 'enforcement/' "$taskfile" 2>/dev/null; then
            reference_count=$((reference_count + 1))
        fi
    done

    if [ "$reference_count" -gt 0 ]; then
        echo "  OK: $reference_count surviving task files reference enforcement/ modules (expected)"
    else
        echo "  WARN: No surviving task files reference enforcement/ modules (expected references)"
        has_violations=true
        violations+=("No surviving task files contain enforcement/ module references (expected)")
    fi

    if [ "$has_violations" = false ]; then
        report "SC-5-scoped" "PASS" "No embedded model definitions in surviving task files; module references present"
    else
        for v in "${violations[@]}"; do
            echo "  VIOLATION: $v"
        done
        report "SC-5-scoped" "FAIL" "Embedded model definitions found in surviving task files or references missing"
    fi
fi

# ── SC-4-wordcount: Enforcement modules have content ──────────────────

if should_run "SC-4-wordcount"; then
    echo "=== SC-4-wordcount: Enforcement modules have content ==="

    AG_MODULES=(
        "adversarial-verification.md"
        "scope-parsing.md"
        "auto-dispatch-table.md"
        "closed-issue-verification.md"
        "sub-issue-graph-traversal.md"
    )
    DC_MODULES=(
        "completion-checkpoint.md"
        "result-validation.md"
        "overflow-signal.md"
        "work-state-verification.md"
    )

    all_have_content=true

    echo "  --- approval-gate enforcement modules ---"
    for module in "${AG_MODULES[@]}"; do
        path="$SKILLS_DIR/approval-gate/enforcement/$module"
        if [ -f "$path" ]; then
            words=$(wc -w < "$path")
            if [ "$words" -gt 0 ]; then
                echo "  OK: $module — $words words"
            else
                echo "  FAIL: $module — 0 words"
                all_have_content=false
            fi
        else
            echo "  FAIL: $module — file not found"
            all_have_content=false
        fi
    done

    echo "  --- divide-and-conquer enforcement modules ---"
    for module in "${DC_MODULES[@]}"; do
        path="$SKILLS_DIR/divide-and-conquer/enforcement/$module"
        if [ -f "$path" ]; then
            words=$(wc -w < "$path")
            if [ "$words" -gt 0 ]; then
                echo "  OK: $module — $words words"
            else
                echo "  FAIL: $module — 0 words"
                all_have_content=false
            fi
        else
            echo "  FAIL: $module — file not found"
            all_have_content=false
        fi
    done

    if [ "$all_have_content" = true ]; then
        report "SC-4-wordcount" "PASS" "All 9 enforcement modules have content (>0 words)"
    else
        report "SC-4-wordcount" "FAIL" "One or more enforcement modules are empty or missing"
    fi
fi

# ── Summary ──────────────────────────────────────────────────────────

echo ""
echo "=== Phase 1 Scoped Enforcement Test Results ==="
for r in "${RESULTS[@]}"; do
    echo "  $r"
done
echo ""
echo "  Total: $((PASS + FAIL)) | PASS: $PASS | FAIL: $FAIL"

if [ "$FAIL" -gt 0 ]; then
    echo ""
    echo "FAILED: $FAIL scenario(s) failed"
    exit 1
else
    echo ""
    echo "ALL PASSED"
    exit 0
fi