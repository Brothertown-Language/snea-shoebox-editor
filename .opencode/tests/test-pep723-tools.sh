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
    matches=$(grep -rn "uv run python .opencode" .opencode/guidelines/ AGENTS.md .opencode/skills/ 2>/dev/null | grep -v "Do NOT use" || true)
    if [ -n "$matches" ]; then
        echo "FAIL: Old 'uv run python .opencode' references found:"
        echo "$matches"
        FAIL=$((FAIL + 1))
    else
        PASS=$((PASS + 1))
    fi

    local md_matches
    md_matches=$(grep -rn 'uv run python ' .opencode/ --include='*.md' 2>/dev/null | grep -v '# Do NOT use' | grep -v 'Do NOT use' | grep -v 'FORBIDDEN' | grep -v 'python -m unittest' || true)
    if [ -n "$md_matches" ]; then
        echo "FAIL: Old 'uv run python' references found in .md files:"
        echo "$md_matches"
        FAIL=$((FAIL + 1))
    else
        PASS=$((PASS + 1))
    fi
}

check_python_script() {
    local file="$1"
    check_shebang "$file"
    check_pep723_metadata "$file"
    check_python_version_pinned "$file"
}

ENTRY_POINTS=(
    guidelines memory md py jupyter help file-exists
    schema-version jupyter-start jupyter-stop symbolic session-init
    gitbucket-api
)

for tool in "${ENTRY_POINTS[@]}"; do
    file="$TOOLS_DIR/$tool"
    check_shebang "$file"
    check_pep723_metadata "$file"
    check_execute "$file"
    check_python_version_pinned "$file"
done

IMPL_DIR=".opencode/tools/impl"
for impl_file in "$IMPL_DIR"/*; do
    [ -f "$impl_file" ] || continue
    check_python_script "$impl_file"
done

SCRIPTS_DIR=".opencode/scripts"
for script_file in "$SCRIPTS_DIR"/*.py; do
    [ -f "$script_file" ] || continue
    check_python_script "$script_file"
done

SKILL_SCRIPTS_DIR=".opencode/skills"
find "$SKILL_SCRIPTS_DIR" -name '*.py' -not -path '*/tests/*' | while read -r skill_py; do
    check_python_script "$skill_py"
done

check_no_old_references

check_plugin_invocations() {
    local plugin_failures=0
    local plugin_files
    plugin_files=$(find .opencode/plugins -name '*.ts' -o -name '*.js' 2>/dev/null || true)
    for pf in $plugin_files; do
        local bare_matches
        bare_matches=$(grep -n 'uv run [^ ]*\.opencode/' "$pf" 2>/dev/null | grep -v '\-\-script' || true)
        if [ -n "$bare_matches" ]; then
            echo "FAIL: $pf has bare 'uv run' without --script:"
            echo "$bare_matches"
            FAIL=$((FAIL + 1))
            plugin_failures=$((plugin_failures + 1))
        fi
    done
    if [ "$plugin_failures" -eq 0 ]; then
        PASS=$((PASS + 1))
    fi
}

check_plugin_invocations

check_no_python_imports() {
    local import_matches
    import_matches=$(grep -rn 'from skills.gitbucket_api' .opencode/ 2>/dev/null | grep -v 'test-pep723-tools.sh' || true)
    if [ -n "$import_matches" ]; then
        echo "FAIL: Old 'from skills.gitbucket_api' import references found (should use CLI tool):"
        echo "$import_matches"
        FAIL=$((FAIL + 1))
    else
        PASS=$((PASS + 1))
    fi
}

check_no_python_imports

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]