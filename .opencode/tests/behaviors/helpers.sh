#!/bin/bash
# Behavioral assertion functions for enforcement tests.
# Source this file in behavioral test scripts.
#
# Usage:
#   source "$(dirname "${BASH_SOURCE[0]}")/helpers.sh"
#
# These helpers verify agent BEHAVIOR (tool calls, response patterns)
# rather than just content presence in guideline files.
#
# Co-authored with AI: <AgentName> (<ModelId>)

set -euo pipefail

BEHAVIOR_LOG_DIR="${BEHAVIOR_LOG_DIR:-.opencode/tmp/behavior-test-$(date +%Y%m%d-%H%M%S)}"
BEHAVIOR_TIMEOUT="${BEHAVIOR_TIMEOUT:-120}"
BEHAVIOR_MODEL="${BEHAVIOR_MODEL:-ollama-cloud/glm-5.1}"
BEHAVIOR_TEST_HOME="${BEHAVIOR_TEST_HOME:-.opencode/tests/with-test-home}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

behavior_run() {
    local scenario_name="$1"
    local message="$2"
    local log_dir="$BEHAVIOR_LOG_DIR/$scenario_name"
    mkdir -p "$log_dir"

    timeout "$BEHAVIOR_TIMEOUT" bash "$PROJECT_DIR/$BEHAVIOR_TEST_HOME" \
        opencode-cli run "$message" \
        --model "$BEHAVIOR_MODEL" \
        --print-logs \
        > "$log_dir/stdout.log" 2> "$log_dir/stderr.log" \
        || true

    sleep 1

    BEHAVIOR_STDOUT="$log_dir/stdout.log"
    BEHAVIOR_STDERR="$log_dir/stderr.log"
}

behavior_get_stdout() {
    cat "$BEHAVIOR_STDOUT"
}

behavior_get_stderr() {
    cat "$BEHAVIOR_STDERR"
}

assert_tool_calls_made() {
    local min_count="$1"
    shift
    local tool_patterns="$*"
    local log_file="${BEHAVIOR_STDOUT:-/dev/null}"
    local total=0
    for pattern in $tool_patterns; do
        local count
        count=$(grep -c "$pattern" "$log_file" 2>/dev/null || echo "0")
        total=$((total + count))
    done
    if [ "$total" -lt "$min_count" ]; then
        echo "FAIL: assert_tool_calls_made — expected at least $min_count tool call(s) matching [$tool_patterns], found $total"
        return 1
    fi
    echo "PASS: assert_tool_calls_made — found $total tool call(s) matching [$tool_patterns] (>= $min_count)"
    return 0
}

assert_forbidden_pattern_absent() {
    local pattern="$1"
    local description="${2:-forbidden pattern}"
    local log_file="${BEHAVIOR_STDOUT:-/dev/null}"
    local count
    count=$(grep -c "$pattern" "$log_file" 2>/dev/null || echo "0")
    if [ "$count" -gt 0 ]; then
        echo "FAIL: assert_forbidden_pattern_absent — found $count occurrence(s) of $description in agent output"
        return 1
    fi
    echo "PASS: assert_forbidden_pattern_absent — $description not found in agent output"
    return 0
}

assert_required_pattern_present() {
    local pattern="$1"
    local description="${2:-required pattern}"
    local log_file="${BEHAVIOR_STDOUT:-/dev/null}"
    local count
    count=$(grep -c "$pattern" "$log_file" 2>/dev/null || echo "0")
    if [ "$count" -eq 0 ]; then
        echo "FAIL: assert_required_pattern_present — $description not found in agent output"
        return 1
    fi
    echo "PASS: assert_required_pattern_present — $description found $count time(s) in agent output"
    return 0
}

assert_skill_invoked() {
    local expected_skill="$1"
    local log_file="${BEHAVIOR_STDERR:-/dev/null}"
    local found
    found=$(grep -c "Skill \"$expected_skill\"" "$log_file" 2>/dev/null || echo "0")
    if [ "$found" -eq 0 ]; then
        found=$(grep -oi "$expected_skill" "$BEHAVIOR_STDOUT" 2>/dev/null | head -1 | wc -l || echo "0")
    fi
    if [ "$found" -eq 0 ]; then
        echo "FAIL: assert_skill_invoked — expected skill '$expected_skill' was not invoked"
        return 1
    fi
    echo "PASS: assert_skill_invoked — skill '$expected_skill' was invoked"
    return 0
}

assert_no_skill_invoked() {
    local forbidden_skill="$1"
    local log_file="${BEHAVIOR_STDERR:-/dev/null}"
    local found
    found=$(grep -c "Skill \"$forbidden_skill\"" "$log_file" 2>/dev/null || echo "0")
    if [ "$found" -gt 0 ]; then
        echo "FAIL: assert_no_skill_invoked — forbidden skill '$forbidden_skill' was invoked ($found time(s))"
        return 1
    fi
    found=$(grep -ci "$forbidden_skill" "$BEHAVIOR_STDOUT" 2>/dev/null || echo "0")
    if [ "$found" -gt 0 ]; then
        echo "FAIL: assert_no_skill_invoked — forbidden skill '$forbidden_skill' found in output ($found time(s))"
        return 1
    fi
    echo "PASS: assert_no_skill_invoked — skill '$forbidden_skill' was not invoked"
    return 0
}