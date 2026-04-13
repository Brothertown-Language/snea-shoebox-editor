#!/usr/bin/env bash
set -euo pipefail

TOOLS_DIR=".opencode/tools"
PASS=0
FAIL=0

check_shebang() {
    local file="$1"
    if head -1 "$file" | grep -q '^#!/usr/bin/env -S uv run --script$'; then
        PASS=$((PASS + 1))
    else
        echo "FAIL: $file missing PEP 723 shebang"
        FAIL=$((FAIL + 1))
    fi
}

check_pep723_metadata() {
    local file="$1"
    if grep -q '^# /// script$' "$file" && grep -q '^# requires-python' "$file" && grep -q '^# dependencies' "$file"; then
        PASS=$((PASS + 1))
    else
        echo "FAIL: $file missing PEP 723 metadata"
        FAIL=$((FAIL + 1))
    fi
}

check_execute() {
    local file="$1"
    if [ -x "$file" ]; then
        PASS=$((PASS + 1))
    else
        echo "FAIL: $file not executable"
        FAIL=$((FAIL + 1))
    fi
}

check_python_version_pinned() {
    local file="$1"
    if grep -q '^# requires-python = "~=3\.12"' "$file"; then
        PASS=$((PASS + 1))
    else
        echo "FAIL: $file python version not pinned with ~="
        FAIL=$((FAIL + 1))
    fi
}

check_no_old_references() {
    local matches
    matches=$(grep -rn "uv run python .opencode/tools" .opencode/guidelines/ AGENTS.md .opencode/skills/ 2>/dev/null | grep -v "Do NOT use" || true)
    if [ -n "$matches" ]; then
        echo "FAIL: Old 'uv run python .opencode/tools' references found:"
        echo "$matches"
        FAIL=$((FAIL + 1))
    else
        PASS=$((PASS + 1))
    fi
}

ENTRY_POINTS=(
    guidelines memory md py jupyter help file-exists
    schema-version jupyter-start jupyter-stop symbolic session-init
)

for tool in "${ENTRY_POINTS[@]}"; do
    file="$TOOLS_DIR/$tool"
    check_shebang "$file"
    check_pep723_metadata "$file"
    check_execute "$file"
    check_python_version_pinned "$file"
done

check_no_old_references

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]