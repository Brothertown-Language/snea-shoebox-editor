# Task: verify-codebase

Verify spec references match the live codebase.

## Purpose

Per `130-authority-source.md`, the current state of the filesystem (the code) is the only absolute source of truth. Specs must match reality. This task verifies that spec references to files, modules, functions, and classes actually exist in the codebase.

## Workflow

**Step 1: Extract References from Spec**

Parse the spec for:
- File paths: `src/module/file.py`
- Function anchors: `process_data()`
- Class anchors: `ClassName`
- Section anchors: `"Section Name"` (less common, verify context)

**Step 2: Verify File Existence**

For each file path:
```
pycharm_find_files_by_glob(globPattern="**/file.py")
pycharm_find_files_by_name_keyword(nameKeyword="file")
```

Report:
- ✅ VERIFIED: File exists
- ⚠️ PATH CHANGED: File exists at different location
- ❌ MISSING: File not found

**Step 3: Verify Symbol Existence**

For each function/class anchor:
```
srclight_get_symbol(name="ClassName")
srclight_search_symbols(query="function_name")
```

Report:
- ✅ VERIFIED: Symbol exists
- ❌ MISSING: Symbol not found
- ⚠️ DEFINITION CHANGED: Symbol exists but signature changed

**Step 4: Detect Staleness**

Compare spec descriptions against current implementation:
- Read referenced files via `pycharm_get_file_text_by_path`
- Compare spec description to actual code behavior
- Identify discrepancies between spec and implementation

Report:
- ✅ MATCHES: Description matches implementation
- ⚠️ STALE: Description doesn't match current code
- ❌ CONFLICT: Spec contradicts implementation

**Step 5: Detect Obsolescence**

Check for merged PRs that supersede open specs:
```
github_pull_request_read(method="get", pullNumber=N)
github_list_pull_requests(state="merged")
```

Report:
- ✅ ACTIVE: No merged PR addresses this topic
- ⚠️ POTENTIALLY SUPERSEDED: Related merged PR found
- ❌ SUPERSEDED: Merged PR directly addresses spec topic

**Step 6: Detect Duplicates**

Query open specs for overlapping objectives:
```
github_list_issues(state="open")
github_search_issues(query="is:issue is:open [SPEC]")
```

Report:
- ✅ UNIQUE: No overlap with other open specs
- ⚠️ POTENTIAL OVERLAP: Similar topics found (review needed)
- ❌ DUPLICATE: Multiple specs cover same ground

## Verification Report Format

```markdown
# Codebase Verification Report

Issue: #{issue_number}
Generated: {timestamp}

## File References

| File | Status | Notes |
|------|--------|-------|
| path/to/file.py | ✅ VERIFIED | File exists at expected location |

## Symbol References

| Symbol | Type | Status | Notes |
|--------|------|--------|-------|
| ClassName | class | ✅ VERIFIED | Symbol exists |
| process_data() | function | ❌ MISSING | Function removed |

## Staleness Detection

| Description | Status | Notes |
|-------------|--------|-------|
| "function returns X" | ⚠️ STALE | Now returns Y |

## Conflicts

| Requirement | Implementation | Status |
|-------------|---------------|--------|
| "Must validate input" | No validation code | ❌ CONFLICT |

## Obsolescence

| Related PR | Status | Notes |
|------------|--------|-------|
| #123 | ⚠️ POTENTIALLY SUPERSEDED | PR merged, may address topic |

## Duplicates

| Related Issue | Topic | Status |
|---------------|-------|--------|
| #456 | Same feature | ❌ DUPLICATE |

## Summary

- Files Verified: {count}
- Files Missing: {count}
- Symbols Verified: {count}
- Symbols Missing: {count}
- Stale References: {count}
- Conflicts Found: {count}
- Superseded Specs: {count}
```

## Tool Fallback Protocol

**Per `015-mcp-preference.md`:**
1. Use **srclight tools** for Python symbol search (semantic analysis)
2. If srclight unavailable, **fallback to pycharm tools** for symbol search
3. Use **pycharm tools** for file operations and content reading (not srclight)
4. Use **GitHub MCP** for PR status checks

**Fallback Chain:**
```
srclight_get_symbol/srclight_search_symbols
    ↓ (unavailable)
pycharm_get_symbol_info/pycharm_search_in_files_by_text
```

**File operations ALWAYS use pycharm:**
- File existence: `pycharm_find_files_by_glob`
- File reading: `pycharm_get_file_text_by_path`
- Content search: `pycharm_search_in_files_by_text`

## Constraints

- Use srclight for Python symbol search
- Use pycharm for file operations and content reading
- Use GitHub MCP for PR status checks
- Report errors gracefully, continue with remaining verifications

## Return Value

- Verification report with all checked references
- Count of verified/missing/stale/conflicting items
- Recommendations for spec updates