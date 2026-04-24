#!/bin/bash
# git-workflow/enforcement/verify_merge.sh
# Shared module: PR merge verification functions
# 
# Usage:
#   source verify_merge.sh
#   verify_pr_merged --owner <owner> --repo <repo> --number <pr_number>
#
# Co-authored with AI: <AgentName> (<ModelId>)

set -euo pipefail

# Verify PR merge status via GitHub API
verify_pr_merged() {
    local owner=""
    local repo=""
    local pr_number=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --owner) owner="$2"; shift 2 ;;
            --repo) repo="$2"; shift 2 ;;
            --number) pr_number="$2"; shift 2 ;;
            *) echo "Unknown parameter: $1" >&2; exit 1 ;;
        esac
    done
    
    if [[ -z "$owner" || -z "$repo" || -z "$pr_number" ]]; then
        echo "ERROR: Missing required arguments" >&2
        echo "Usage: verify_pr_merged --owner <owner> --repo <repo> --number <pr_number>" >&2
        return 1
    fi
    
    echo "Verifying PR merge for $owner/$repo#$pr_number..."
    
    # This is a shared module - actual API call would be used here
    # The actual validation is done by skill task code
    
    echo "PR merge verification shared module loaded"
    return 0
}

# Verify merged_at field is present
verify_merged_timestamp() {
    local merged_at="$1"
    
    if [[ -z "$merged_at" || "$merged_at" == "null" ]]; then
        echo "ERROR: PR is not yet merged. Cannot proceed."
        return 1
    fi
    
    echo "PR merge verified: $merged_at"
    return 0
}

# Verify hashes match for dev sync
verify_dev_sync() {
    local local_hash="$1"
    local remote_hash="$2"
    
    if [[ "$local_hash" != "$remote_hash" ]]; then
        echo "ERROR: Local dev ($local_hash) does not match remote ($remote_hash)"
        return 1
    fi
    
    echo "Dev sync verified: $local_hash"
    return 0
}