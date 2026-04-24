#!/bin/bash
# git-workflow/enforcement/issue_closure_patterns.sh
# Shared module: Issue reference parsing and classification patterns
#
# Usage:
#   source issue_closure_patterns.sh
#   parse_issue_refs "<pr_body>"
#
# Co-authored with AI: <AgentName> (<ModelId>)

set -euo pipefail

# Issue reference patterns for parsing PR bodies
SPEC_REF_PATTERN="Spec:\s*#(\d+)"
PLAN_REF_PATTERN="Plan:\s*#(\d+)"
FIXES_PATTERN="Fixes\s*#(\d+)"
IMPLEMENTS_PATTERN="Implements\s*#(\d+)"
RELATED_PATTERN="Related\s*#(\d+)"

# Issue classification patterns
PLAN_LABEL="PLAN"
SPEC_LABEL="SPEC"
SPEC_FIX_LABEL="SPEC-FIX"

# Parse all issue references from a PR body
# Returns space-separated list of issue numbers
parse_issue_refs() {
    local pr_body="$1"
    local refs=""
    
    for pattern in "$SPEC_REF_PATTERN" "$PLAN_REF_PATTERN" "$FIXES_PATTERN" "$IMPLEMENTS_PATTERN" "$RELATED_PATTERN"; do
        while IFS= read -r match; do
            if [[ -n "$match" ]]; then
                refs="${refs} ${match}"
            fi
        done < <(echo "$pr_body" | grep -oP "$pattern" 2>/dev/null || true)
    done
    
    echo "$refs" | tr ' ' '\n' | sort -u | tr '\n' ' '
}

# Classify an issue based on labels and title
classify_issue() {
    local labels="$1"
    local title="$2"
    
    if echo "$labels" | grep -q "$PLAN_LABEL" || [[ "$title" == \[PLAN\]* ]]; then
        echo "plan"
    elif echo "$labels" | grep -q "$SPEC_LABEL" || echo "$labels" | grep -q "$SPEC_FIX_LABEL" || [[ "$title" == \[SPEC* ]]; then
        echo "spec"
    else
        echo "other"
    fi
}

# Check if deliverables are covered by PR file list
check_deliverables_in_pr() {
    local sub_body="$1"
    local pr_files="$2"
    
    local deliverable_patterns=$(echo "$sub_body" | grep -oP "(?:deliverable|file|path|modif(?:y|ied|ication)):\s*\K[^\s\`*#]+" || true)
    local title_paths=$(echo "$2" | grep -oP "\`\K[^\`]+" || true)
    
    local candidates="${deliverable_patterns} ${title_paths}"
    
    if [[ -z "$candidates" ]]; then
        echo "no_deliverables"
        return 0
    fi
    
    for candidate in $candidates; do
        if echo "$pr_files" | grep -q "$candidate"; then
            echo "covered"
            return 0
        fi
    done
    
    echo "not_covered"
}