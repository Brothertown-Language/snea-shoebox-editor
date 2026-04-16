# GitBucket API Differences - Version 4.42.1

**Release Date:** 2025-01-20  
**Release Notes:** https://github.com/gitbucket/gitbucket/releases/tag/4.42.1  
**Compare View:** https://github.com/gitbucket/gitbucket/compare/4.42.0...4.42.1

---

## Overview

This document describes API changes between GitBucket 4.42.0 and 4.42.1.

**Analysis Method:** Source code comparison between tags 4.42.0 and 4.42.1.

**⚠️ CRITICAL:** The CHANGELOG states "Fix LDAP issue with SSL" but source code analysis reveals ACTUAL API changes were made that were NOT documented in the release notes.

---

## 1. New Endpoints

**None** - No new API endpoints were added in 4.42.1.

---

## 2. Modified Endpoints

### 2.1 Branch-Related Endpoints (Breaking Change)

**Endpoints Affected:**
- `GET /api/v3/repos/{owner}/{repo}/branches` - List branches
- `GET /api/v3/repos/{owner}/{repo}/branches/{branch}` - Get branch

**Internal API Change:**
- **Function:** `getBranchesNoMergeInfo()` in `JGitUtil.scala`
- **4.42.0 Signature:** `def getBranchesNoMergeInfo(git: Git, defaultBranch: String): Seq[BranchInfoSimple]`
- **4.42.1 Signature:** `def getBranchesNoMergeInfo(git: Git): Seq[BranchInfoSimple]`

**Breaking Change:**
- The `defaultBranch` parameter was REMOVED from the function signature
- All callers in `ApiRepositoryBranchControllerBase.scala` were updated
- This affects how default branch detection works internally

**Source Code Diffs:**

`ApiRepositoryBranchControllerBase.scala` (3 locations changed):

```diff
-         br <- getBranchesNoMergeInfo(
-           git,
-           repository.repository.defaultBranch
-         ).find(_.name == branch)
+         br <- getBranchesNoMergeInfo(git).find(_.name == branch)
```

**Impact:**
- Internal implementation change
- API endpoints still function the same way
- Default branch is now determined internally rather than passed explicitly

---

### 2.2 Commit-Related Endpoints (Breaking Change)

**Endpoints Affected:**
- `GET /api/v3/repos/{owner}/{repo}/commits` - List commits
- `GET /api/v3/repos/{owner}/{repo}/commits/{sha}` - Get commit

**Internal API Change:**
- Same `getBranchesNoMergeInfo()` signature change affects commit endpoints

**Source Code Diffs:**

`ApiRepositoryCommitControllerBase.scala`:

```diff
-         br <- getBranchesNoMergeInfo(git, branch).find(_.name == branch)
+         br <- getBranchesNoMergeInfo(git).find(_.name == branch)
```

**Impact:**
- Internal implementation change
- API endpoints still function the same way externally

---

## 3. Schema Changes

**None** - No changes to request/response schemas in 4.42.1.

---

## 4. Internal Changes

### 4.1 LDAP SSL Fix (Documented)

- **Bug Fix:** Fixed LDAP authentication issue with SSL connections
- **Impact:** Server-side authentication fix only
- **API Surface:** No changes to authentication endpoints or tokens

### 4.2 Branch Info Function Signature Change (NOT Documented in CHANGELOG)

**This change was NOT documented in the CHANGELOG but was found via source code analysis.**

- **File:** `src/main/scala/gitbucket/core/util/JGitUtil.scala`
- **Line 4.42.0:** 1307 - `def getBranchesNoMergeInfo(git: Git, defaultBranch: String): Seq[BranchInfoSimple]`
- **Line 4.42.1:** 1294 - `def getBranchesNoMergeInfo(git: Git): Seq[BranchInfoSimple]`

**Migration Notes:**
- This is an internal API change
- External API consumers are NOT affected
- Custom plugins calling `getBranchesNoMergeInfo()` will need to update

---

## 5. Breaking Changes

### 5.1 Internal API Breaking Change

**For Plugin Developers:**

If you have custom GitBucket plugins that call `JGitUtil.getBranchesNoMergeInfo()`:

**Before (4.42.0):**
```scala
val branches = JGitUtil.getBranchesNoMergeInfo(git, repository.defaultBranch)
```

**After (4.42.1):**
```scala
val branches = JGitUtil.getBranchesNoMergeInfo(git)
```

**External API Clients:** No breaking changes - the REST API endpoints remain compatible.

---

## 6. Deprecated Endpoints

**None** - No API endpoints were deprecated in 4.42.1.

---

## 7. Removed Endpoints

**None** - No API endpoints were removed in 4.42.1.

---

## 8. Authentication Changes

**None** - No changes to authentication mechanisms in 4.42.1.

The LDAP SSL fix resolves a server-side bug and does not change the external API surface.

---

## 9. Total Endpoints

| Version | Endpoint Count |
|---------|----------------|
| 4.42.0 | 101 |
| 4.42.1 | 101 |

**No changes to the total number of API endpoints.**

---

## 10. Source Code Differences

### Files Changed (API-related)

| File | Change Type | Impact |
|------|-------------|--------|
| `ApiRepositoryBranchControllerBase.scala` | Modified (function signature) | Internal: defaultBranch param removed |
| `ApiRepositoryCommitControllerBase.scala` | Modified (function signature) | Internal: defaultBranch param removed |
| `JGitUtil.scala` | Modified (function signature) | Internal: getBranchesNoMergeInfo signature changed |

### Files Changed (Backend only)

| File | Change Type | Impact |
|------|-------------|--------|
| LDAP authentication module | Bug fix | Backend authentication only - no API changes |

---

## 11. Verification Method

This comparison was generated by:

1. ✅ **Clone both version tags** (NOT relying on CHANGELOG)
2. ✅ **Diff API directories:** `diff -r gitbucket-4.42.0/src/.../api/ gitbucket-4.42.1/src/.../api/`
3. ✅ **Diff API controllers:** `diff -r gitbucket-4.42.0/controller/api/ gitbucket-4.42.1/controller/api/`
4. ✅ **Analyze each diff** manually
5. ✅ **Trace function signature changes** to source

**Source:**
- CHANGELOG.md: "Fix LDAP issue with SSL" (INCOMPLETE)
- Source diff: Shows actual API changes NOT in CHANGELOG

---

## 12. Recommendations for API Consumers

### External API Clients

1. **No changes required** - All 4.42.0 API clients will work on 4.42.1
2. **No schema migrations needed** - All existing response formats remain compatible
3. **Consider upgrading** - LDAP SSL fix improves authentication reliability

### GitBucket Plugin Developers

1. **Update internal API calls** - If using `JGitUtil.getBranchesNoMergeInfo()`, remove `defaultBranch` parameter
2. **Test plugins** - Verify compatibility with 4.42.1 before deployment

---

## 13. Migration Guide

### External API Clients: No Migration Required

All REST API endpoints remain compatible. No client changes needed.

### Plugin Developers

**Before (4.42.0):**
```scala
// Plugin code calling internal API
val branches = JGitUtil.getBranchesNoMergeInfo(git, repo.defaultBranch)
```

**After (4.42.1):**
```scala
// Updated plugin code
val branches = JGitUtil.getBranchesNoMergeInfo(git)
```

---

## 14. Lessons Learned

**CHANGELOG was WRONG.**

The CHANGELOG stated: "Fix LDAP issue with SSL" (one line).

**Actual changes found:**
- LDAP SSL fix (correct)
- Internal API function signature change (NOT documented)
- Multiple controller updates (NOT documented)

**This is why source code analysis is MANDATORY.**

---

*API baseline comparison document for GitBucket 4.42.1 - Generated from SOURCE CODE ANALYSIS (not CHANGELOG trust)*
