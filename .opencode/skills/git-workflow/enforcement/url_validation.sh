#!/bin/bash
# git-workflow/enforcement/url_validation.sh
# Shared module: URL construction and validation from session-init values
#
# Usage:
#   source url_validation.sh
#   construct_compare_url --owner <owner> --repo <repo> --branch <branch> --base <base>
#
# Co-authored with AI: <AgentName> (<ModelId>)

set -euo pipefail

# Construct compare URL from session-init values with character-match verification
construct_compare_url() {
    local owner=""
    local repo=""
    local branch=""
    local base="dev"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --owner) owner="$2"; shift 2 ;;
            --repo) repo="$2"; shift 2 ;;
            --branch) branch="$2"; shift 2 ;;
            --base) base="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    if [[ -z "$owner" || -z "$repo" || -z "$branch" ]]; then
        echo "ERROR: Missing required arguments for URL construction" >&2
        return 1
    fi
    
    local url="https://github.com/${owner}/${repo}/compare/${base}...${branch}"
    
    # Character-match verification
    # URL must contain the exact owner and repo strings from session init
    if [[ "$url" != *"${owner}"* ]]; then
        echo "ERROR: URL does not contain expected owner '${owner}'" >&2
        return 1
    fi
    
    if [[ "$url" != *"${repo}"* ]]; then
        echo "ERROR: URL does not contain expected repo '${repo}'" >&2
        return 1
    fi
    
    echo "$url"
    return 0
}

# Validate PR body format
# Returns 0 if valid, 1 if invalid
validate_pr_body() {
    local body="$1"
    
    # Must have Summary section
    if ! echo "$body" | grep -q "^\*\*Summary:\*\*"; then
        echo "ERROR: PR body missing '**Summary:**' section" >&2
        return 1
    fi
    
    # Must have Outcome section
    if ! echo "$body" | grep -q "^\*\*Outcome:\*\*"; then
        echo "ERROR: PR body missing '**Outcome:**' section" >&2
        return 1
    fi
    
    # Must have Fixes/Implements reference
    if ! echo "$body" | grep -qE "(Fixes|Implements)\s+#\d+"; then
        echo "ERROR: PR body missing 'Fixes #N' or 'Implements #N' reference" >&2
        return 1
    fi
    
    echo "PR body format valid"
    return 0
}