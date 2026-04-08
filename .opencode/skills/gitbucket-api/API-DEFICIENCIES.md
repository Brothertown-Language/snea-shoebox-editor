# GitBucket API Deficiencies

## Overview

This document records discovered API deficiencies between the OpenAPI specification and actual GitBucket API behavior. These deficiencies were discovered through testing against `NewSRX-Tech-LLC/ai-agent-testing` repository.

**Testing Date:** 2026-04-06
**GitBucket Version:** v4.42.1 (per OpenAPI spec)
**Last Retest:** 2026-04-06 (after GitBucket upgrade)

## Ongoing Test Suite

**Test Script:** `.opencode/skills/gitbucket-api/tests/verify_api.py` (permanent test suite)

**Test Repository:** `NewSRX-Tech-LLC/ai-agent-testing`

**How to Retest:**
```bash
uv run python .opencode/skills/gitbucket-api/tests/verify_api.py
```

## Deficiencies Discovered (Post-Upgrade Status)

### 1. PATCH /issues/:number Returns 404

**OpenAPI Spec Claims:**
```
PATCH /repos/{owner}/{repo}/issues/{issue_number}
Request body: { "title": "string", "body": "string", "state": "string", ... }
Response: 200 OK with updated Issue object
```

**Actual GitBucket Behavior:**
```
PATCH /repos/{owner}/{repo}/issues/{issue_number}
Response: 404 Not Found
```

**Impact:** `update_issue()` method fails with 404

**Workaround:** None. GitBucket does NOT support updating issue title, body, or state.

**Affected Operations:**
- ❌ Cannot update issue title
- ❌ Cannot update issue body
- ❌ Cannot close issues via PATCH
- ❌ Cannot change issue state

**Open Issue:** This may be fixed in later GitBucket versions. Test against target GitBucket version.

**Apache Reverse Proxy Analysis (Investigated):**

Apache config for `gitbucket.newsrx.com` was reviewed. **PATCH is NOT blocked by Apache:**

```apache
# Apache forwards ALL methods to GitBucket
ProxyPass /gitbucket ajp://tomcat-0002:8009/gitbucket
# No LimitExcept, no mod_security, no AllowMethods restrictions
```

**Verified:**
- No `LimitExcept` directive restricting HTTP methods
- No `mod_security` rules visible
- No `AllowMethods` directive
- AJP proxy forwards all methods to backend

**Conclusion:** The 404 error is from GitBucket itself, not Apache. GitBucket v4.42.1 does NOT implement `PATCH /repos/{owner}/{repo}/issues/{issue_number}`.

**GitBucket Issue:** This is a missing API implementation in GitBucket. The OpenAPI spec documents the endpoint, but GitBucket returns 404.

### 2. Labels Operations Return Empty Array (STILL BROKEN)

**OpenAPI Spec Claims:**
```
POST /repos/{owner}/{repo}/issues/{issue_number}/labels
Request body: ["label1", "label2"]
Response: 200 OK with array of Label objects
```

**Actual GitBucket Behavior:**
```
POST /repos/{owner}/{repo}/issues/{issue_number}/labels
Response: 200 OK with empty array []
```

**Impact:** `add_labels_to_issue()` returns empty array and labels are NOT added to the issue.

**Post-Upgrade Test (2026-04-06):**
```bash
Testing POST https://gitbucket.newsrx.com/gitbucket/api/v3/repos/NewSRX-Tech-LLC/ai-agent-testing/issues/6/labels
   Labels to add: ['test-label-1', 'test-label-2']
   Status: 200
   Response: []
   Issue actually has 0 labels:
```

**Workaround:** Use `create_issue()` with labels parameter (labels are added during creation).

**Workaround FAILED:** `replace_issue_labels()` also returns empty array.
```
Testing PUT https://gitbucket.newsrx.com/gitbucket/api/v3/repos/NewSRX-Tech-LLC/ai-agent-testing/issues/7/labels
   Labels to set: ['replace-test-1', 'replace-test-2']
   Status: 200
   Response: []
```

### 3. Label Auto-Creation During Issue Creation (WORKS)

**OpenAPI Spec Claims:** Labels are auto-created when added to issues.

**Actual Behavior:** Labels ARE auto-created when specified in `create_issue()` call, but label management operations (`add_labels_to_issue`, `replace_issue_labels`) return empty arrays and do NOT update the issue.

**Verified:** Labels specified in `create_issue(labels=["label1", "label2"])` are correctly added to the newly created issue.

## Working Operations

The following operations were tested and confirmed working:

### Read Operations (All Work)

| Operation | Returns | Notes |
|-----------|---------|-------|
| `get_current_user()` | `dict` | ✅ Works |
| `get_repository()` | `dict` | ✅ Works |
| `list_branches()` | `list[dict]` | ✅ Works, returns array |
| `list_issues()` | `list[dict]` | ✅ Works, returns array |
| `list_labels()` | `list[dict]` | ✅ Works, returns array |
| `list_pull_requests()` | `list[dict]` | ✅ Works, returns array |
| `get_issue()` | `dict` | ✅ Works |

### Write Operations (Partial - Post-Upgrade Test)

| Operation | Returns | Notes |
|-----------|---------|-------|
| `create_issue()` | `dict` | ✅ Works, auto-creates labels |
| `add_issue_comment()` | `dict` | ✅ Works (assumed, not retested) |
| `update_issue()` | ❌ 404 | ❌ **STILL BROKEN** - GitBucket doesn't support |
| `add_labels_to_issue()` | `[]` | ❌ **STILL BROKEN** - Returns empty, labels NOT added |
| `replace_issue_labels()` | `[]` | ❌ **STILL BROKEN** - Returns empty, labels NOT set |

## Documented in SKILL.md

These deficiencies are documented in `SKILL.md` under "API Deficiencies Documentation" section.

## Testing Methodology

**Test Repository:** `NewSRX-Tech-LLC/ai-agent-testing`

**Test Script:** See `./tmp/test_gitbucket_api_operations.py` (temporary, deleted after testing)

**Test Operations:**
1. Create test issue
2. Add comment to test issue
3. Update test issue → **FAILED with 404**
4. Add labels to test issue → **Returned empty array**
5. Close test issue → **FAILED (depends on update_issue)**

## Recommendations

### For Python Client Users

1. **Avoid `update_issue()`** - Not supported by GitBucket API (returns 404)
2. **Avoid `add_labels_to_issue()` and `replace_issue_labels()`** - Return empty arrays, labels NOT added/set
3. **Use `create_issue(labels=[...])` for label management** - Only reliable way to add labels to issues
4. **Verify operations with `get_issue()`** - Check actual state after any operation
5. **Report API discrepancies** - Document any additional deficiencies found
6. **Retest after upgrades** - Run `verify_api.py` after GitBucket version changes

### For GitBucket Users

1. **Update issue via web UI** - Title/body changes require web interface
2. **Add labels during issue creation** - Cannot add labels after creation via API
3. **Close issues via web UI** - Cannot close via API PATCH
4. **Retest API after upgrades** - API behaviors may change between versions

## Test Results History

| Test Date | GitBucket Version | `update_issue()` | `add_labels_to_issue()` | `replace_issue_labels()` |
|------------|------------------|------------------|-------------------------|-------------------------|
| 2026-04-06 (initial) | v4.42.1 | ❌ 404 | ⚠️ Empty array, needs verification | ❓ Not tested |
| 2026-04-06 (post-upgrade) | v4.42.1 | ❌ 404 | ❌ Empty array, labels NOT added | ❌ Empty array, labels NOT set |

## Future Investigation

- ~~Test `replace_issue_labels()` to verify it works~~ → **TESTED: BROKEN**
- Test `create_issue()` with various combinations of labels, assignees, milestones
- Test milestone operations
- Test release operations
- Test webhook operations
- Test against newer GitBucket versions (v4.46.0+)
- Investigate why label operations return 200 but don't update issues

## Cross-References

- OpenAPI Spec: `.opencode/skills/gitbucket-api/reference/openapi-v4.42.1.json`
- Python Client: `.opencode/skills/gitbucket-api/tools/gitbucket_api.py`
- Skill Docs: `.opencode/skills/gitbucket-api/SKILL.md`
- Issue Operations: `.opencode/skills/gitbucket-api/tasks/issue-operations.md`