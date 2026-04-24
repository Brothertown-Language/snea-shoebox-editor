# Task: Pre-Merge Verification

## Purpose
Verify PR is merged before cleanup begins.

## Entry Criteria
- PR merge confirmed via GitHub API

## Procedure
1. Call `github_pull_request_read(method=get)` to verify `merged_at` is not null
2. If not merged: HALT and report
3. If merged: proceed to cleanup

## Exit Criteria
- PR merge verified
- Ready for branch deletion

## References
- See cleanup.md for full workflow
