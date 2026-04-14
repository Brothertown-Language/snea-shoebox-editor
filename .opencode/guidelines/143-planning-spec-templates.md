# Planning: Spec Templates

## Intent, Not Templates

**These examples illustrate possibilities, not mandatory formats.** Agents should adapt structure to match the spec's complexity and domain.

A simple bug fix needs only a few sentences of problem, context, and criteria. A multi-phase feature benefits from more structure. The goal is always: can a fresh agent pick up this spec and implement it correctly without additional context?

## Content Coverage Checklist

Before creating any spec, bug report, or issue, verify these intent questions are answered. The *format* of the answers is up to the agent — the *content* must be present:

| Question | Intent |
|----------|--------|
| Does the spec describe what problem it solves and why? | Problem statement — what's broken or needed, with context |
| Does the spec explain the background and affected systems? | Context — who is affected, what triggered this, what's the current state |
| Does the spec define testable completion criteria? | Success criteria — binary pass/fail conditions for each requirement |
| Does the spec address what could go wrong? | Edge cases and risk — boundary conditions, failure modes |
| Does the spec explain why this approach was chosen? | Decision rationale — alternatives considered and reasons for rejection |
| Does the spec list constraints and assumptions? | Technical, resource, time, and compatibility limits |
| Does the spec reference related issues with context? | Related issues — links with summaries and relevance (not bare links) |
| Does the spec identify affected files with anchors? | Affected files — file paths with function names or section headers, not line numbers |
| Does the spec provide enough context for a fresh agent? | Self-containment — no "as discussed above" or "see previous comment" |

**Simple specs may address several questions in a single paragraph. Complex specs may need separate sections for each. The format adapts to complexity.**

## Self-Containment Rules

These are content quality rules, not structural requirements:

- NO "as discussed above" — all context stated inline
- NO "see previous comment" — information restated
- NO "as mentioned in chat" — decisions documented
- File paths use STABLE ANCHORS — function names `process_data()` or section headers `"Section Name"`
- AVOID line numbers `file.py:42` — they break on every edit
- Code snippets included for short sections (<20 lines)
- Issue links include URLs and summaries

______________________________________________________________________

## Example Variants: Feature Spec

### Minimal Feature Spec (simple change, single file)

> **Objective:** Add `retry_count` parameter to `fetch_data()` in `src/api/client.py` so callers can control retry behavior.
>
> **Problem:** Currently `fetch_data()` retries indefinitely on transient failures, causing timeout cascades in production.
>
> **Success Criteria:**
> 1. ✅ `fetch_data(retry_count=3)` retries exactly 3 times then raises
> 2. ✅ Default behavior unchanged (current retries for backward compatibility)
> 3. ✅ Existing tests pass
>
> **Edge Cases:** retry_count=0 means no retries (fail immediately).

This minimal spec works because the change is small and self-explanatory. Separate sections for context, dependencies, and risk aren't needed — they're obvious.

### Standard Feature Spec (moderate change, multiple files)

> **Objective:** Add Redis caching layer for frequently accessed article metadata.
>
> **Problem:** Article metadata API calls average 150ms response time, causing slow page loads. 85% cache hit potential identified.
>
> **Context:** Current queries hit PostgreSQL directly. Most queries target the same ~1000 recently-published articles. Article metadata changes infrequently. Redis already deployed per infra team.
>
> **Fix Approach:** Redis as cache layer with 1-hour TTL. Fallback to DB when Redis unavailable.
>
> **Affected Files:**
> | File | Anchor | Changes |
> |------|--------|---------|
> | `src/api/articles.py` | `get_article_metadata()` | Add cache check before DB query |
> | `src/cache/__init__.py` | new file | Redis client wrapper |
> | `src/config.py` | "Configuration" section | Add Redis connection config |
>
> **Constraints:** Must not exceed 512MB Redis memory. Must handle Redis unavailable gracefully.
>
> **Success Criteria:**
> 1. ✅ API response time <20ms for cached queries
> 2. ✅ Cache hit rate >80%
> 3. ✅ Graceful fallback when Redis unavailable
> 4. ✅ Cache invalidation on article update
>
> **Edge Cases:** Redis unavailable → fallback to DB (log warning). Cache full → LRU eviction. Article updated → invalidate entry.
>
> **Risk Assessment:** Redis memory limit (Low prob, High impact → monitor). Cache invalidation bugs (Med prob, Med impact → test update flows).

This standard spec adds context, affected files, constraints, and risk because the change touches multiple files and has infrastructure dependencies.

### Comprehensive Feature Spec (large change, cross-cutting)

See the full example in `144-planning-spec-examples.md` for comprehensive specs with phased implementation, full risk assessment, and detailed decision rationale. Comprehensive specs use all the structure they need — phases, affected files with code snippets, extended risk assessment, dependencies table, and decision rationale with alternatives.

______________________________________________________________________

## Example Variants: Bug Fix Spec

### Minimal Bug Fix Spec (obvious fix, one line change)

> **Problem:** `process_data()` crashes when input list is empty, raising `IndexError` at `src/core/processor.py:42`.
>
> **Fix:** Add empty list guard before accessing `data[0]`.
>
> **Success Criteria:**
> 1. ✅ Empty list input returns empty result (no crash)
> 2. ✅ Non-empty list input behavior unchanged

### Standard Bug Fix Spec (needs investigation context)

> **Problem:** OAuth2 refresh_token fails on expiry, causing unexpected logout for ~15% of users who don't log in for more than 7 days.
>
> **Expected Behavior:** Automatically re-authenticate using stored credentials when refresh token expires.
>
> **Root Cause:** `refresh_token()` in `src/auth/oauth_client.py` catches `TokenExpiredError` but re-raises instead of calling `authenticate()`.
>
> **Fix Approach:** Catch `TokenExpiredError` and call `authenticate()` with stored credentials.
>
> **Side Effects:** None — existing refresh logic unchanged for valid tokens.
>
> **Success Criteria:**
> 1. ✅ Users with expired refresh tokens auto-re-authenticated
> 2. ✅ Auth failures surface appropriate error messages
> 3. ✅ No credentials logged or exposed
> 4. ✅ Existing refresh logic unchanged for valid tokens
>
> **Edge Cases:** Credentials no longer valid → prompt re-login. Network failure → propagate error. Rate limiting → backoff and retry.
>
> **Related Issues:** #100 (persistent sessions), #150 (token rotation)

______________________________________________________________________

## Example Variants: Guideline Update Spec

### Minimal Guideline Update (small rule change)

> **Problem:** Current guidelines don't address when to use `--no-verify` with git commands.
>
> **Proposed Change:** Add rule to `000-critical-rules.md` prohibiting `--no-verify` unless explicitly authorized.
>
> **Success Criteria:** Guidelines load correctly. Search finds new content.

### Standard Guideline Update (philosophy or process change)

See `144-planning-spec-examples.md` for a standard guideline update example with problem statement, context, proposed change, decision rationale, and verification steps.

______________________________________________________________________

*Source: Migrated from rigid templates to intent-driven prose per spec #821*