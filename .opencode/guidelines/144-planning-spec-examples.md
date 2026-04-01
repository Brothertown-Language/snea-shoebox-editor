# Planning: Spec Examples

## Good vs Bad Spec Context

This document provides examples of good and bad spec context to illustrate the fresh-start requirements.

---

## Example 1: Bug Report

### ❌ BAD Bug Report (Assumes Memory Context)

> **Title:** Fix authentication bug as discussed
>
> **Description:** Fix the bug in auth where users get logged out. See previous comments for details.
>
> **Steps:** Implement the fix we talked about.

This is BAD because:
- No context about WHAT bug
- No WHERE (which file, which function)
- No WHY (what causes the bug)
- No HOW to fix (no approach documented)
- References "previous comments" instead of restating

---

### ✅ GOOD Bug Report (Self-Contained)

> **Title:** OAuth2 refresh_token fails on expiry, causing unexpected logout
>
> **Problem:** Users are unexpectedly logged out after 7 days when their OAuth2 refresh token expires. The current implementation does not handle the `TokenExpiredError` and instead propagates the exception, terminating the user session.
>
> **Location:** `refresh_token()` in `src/auth/oauth_client.py`:
> ```python
> def refresh_token(self):
>     # BUG: Does not handle expired refresh_token
>     response = self._request_token(self._refresh_token)
>     # Raises TokenExpiredError instead of re-authenticating
>     return response
> ```
>
> **Root Cause:** When `refresh_token` is called with an expired token, the API returns `TokenExpiredError`. The current code catches this error but simply re-raises it, instead of attempting to re-authenticate using stored credentials.
>
> **Expected Behavior:** When refresh token expires, automatically re-authenticate using stored credentials (username/password in secure storage) and return a valid token.
>
> **Context:** This affects ~15% of users who don't log in for more than 7 days. Related to #100 (persistent sessions) and #150 (token rotation strategy).
>
> **Decision:** Implement re-authentication flow by catching `TokenExpiredError` and calling `authenticate()` with stored credentials.
>
> **Constraints:**
> - Must not break existing token refresh logic
> - Must work with the new credential storage added in #100
> - Must not expose credentials in logs
>
> **Edge Cases:**
> - Credentials no longer valid → prompt user to re-login
> - Network failure during re-auth → propagate error
> - Rate limiting on auth API → backoff and retry
>
> **Related Issues:**
> | Issue | Summary | Relevance |
> |-------|---------|-----------|
> | [#100](https://github.com/owner/repo/issues/100) | Persistent sessions | Credential storage implementation |
> | [#150](https://github.com/owner/repo/issues/150) | Token rotation | Future improvement for longer sessions |
>
> **Success Criteria:**
> 1. ✅ Users with expired refresh tokens are automatically re-authenticated
> 2. ✅ Re-authentication failures surface appropriate error messages
> 3. ✅ No credentials logged or exposed
> 4. ✅ Existing refresh logic unchanged for valid tokens

This is GOOD because:
- ✅ Problem clearly stated with symptom and impact
- ✅ Exact file/line location provided
- ✅ Code snippet included
- ✅ Root cause analysis
- ✅ Expected behavior specified
- ✅ Context with related issues linked and explained
- ✅ Decision rationale documented
- ✅ Constraints listed
- ✅ Edge cases identified
- ✅ Success criteria testable

---

## Example 2: Feature Specification

### ❌ BAD Feature Spec (Assumes Memory Context)

> **Title:** Add caching as discussed in yesterday's meeting
>
> **Description:** Implement caching for the API. We decided on Redis.
>
> **Steps:** Add caching layer, update API handlers, add tests.

This is BAD because:
- References "yesterday's meeting" without restating decisions
- No context for WHY caching is needed
- No details on WHAT to cache
- No alternatives considered documented
- No success criteria
- No constraints or edge cases

---

### ✅ GOOD Feature Spec (Self-Contained)

> **Title:** Add Redis caching layer for frequently accessed article metadata
>
> **Problem Statement:** Article metadata API calls average 150ms response time, causing slow page loads for article lists. Users report poor experience on mobile devices with slower connections.
>
> **Objective:** Reduce API response time from 150ms average to <20ms for article metadata queries by implementing a Redis caching layer.
>
> **Context:**
> - Current article metadata queries hit PostgreSQL directly
> - Most queries are for the same ~1000 recently-published articles
> - Article metadata changes infrequently (title, author, publication date)
> - Previous analysis showed 85% cache hit potential
>
> **Decision:** Use Redis as cache layer with 1-hour TTL for article metadata.
>
> **Why Redis over Alternatives:**
> | Option | Pros | Cons | Decision |
> |--------|------|------|----------|
> | Redis | Fast, supports TTL, already in infra | Memory-based | ✅ CHOSEN |
> | Memcached | Simple, fast | No built-in TTL management | ❌ More config needed |
> | In-process | No network overhead | Lost on restart | ❌ Not suitable for HA |
>
> **Affected Files:**
> | File | Anchor | Changes |
> |------|--------|--------|
> | `src/api/articles.py` | `get_article_metadata()` function | Add cache layer |
> | `src/cache/__init__.py` | new file | New Redis client wrapper |
> | `src/config.py` | "Configuration" section | Add Redis connection config |
>
> **Code Context:**
> Current `get_article_metadata()` in `src/api/articles.py`:
> ```python
> def get_article_metadata(article_id: str) -> dict:
>     """Fetch article metadata from database."""
>     # TO BE MODIFIED: Add cache check before DB query
>     result = db.query("SELECT * FROM articles WHERE id = ?", article_id)
>     return result
> ```
>
> **Constraints:**
> - Must not exceed 512MB Redis memory allocation
> - Cache invalidation required on article updates
> - Must handle Redis unavailable gracefully (fallback to DB)
> - TTL of 1 hour (3600 seconds)
>
> **Assumptions:**
> - Redis server already deployed (per infra team confirmation)
> - Article metadata structure stable (no schema changes planned)
>
> **Success Criteria:**
> 1. ✅ API response time <20ms for cached article queries
> 2. ✅ Cache hit rate >80%
> 3. ✅ Graceful fallback when Redis unavailable
> 4. ✅ Cache invalidation on article update works
>
> **Edge Cases:**
> - Redis unavailable → Fallback to DB query (log warning)
> - Article updated → Invalidate cache entry
> - Cache full → Redis LRU eviction handles automatically
>
> **Dependencies:**
> - Redis server (already deployed: `redis.internal:6379`)
> - `redis-py` library (add to requirements)
>
> **Risk Assessment:**
> | Risk | Probability | Impact | Mitigation |
> |------|-------------|--------|------------|
> | Redis memory limit exceeded | Low | High | Monitor usage, set TTL |
> | Cache invalidation bugs | Medium | Medium | Tests for update flows |
> | Increased complexity | Medium | Low | Clear abstraction layer |
>
> **Related Issues:**
> | Issue | Summary | Relevance |
> |-------|---------|-----------|
> | [#50](https://github.com/owner/repo/issues/50) | Performance audit | Original performance report |
> | [#200](https://github.com/owner/repo/pull/200) | Redis infra setup | Infrastructure PR |

This is GOOD because:
- ✅ Problem statement with measurable impact
- ✅ Context explaining current state and why change is needed
- ✅ Decision documented with alternatives considered
- ✅ Affected files with function/section anchors (NOT line numbers)
- ✅ Code snippets included
- ✅ Constraints and assumptions listed
- ✅ Success criteria are testable and measurable
- ✅ Edge cases identified with handling
- ✅ Dependencies documented
- ✅ Risk assessment with mitigations
- ✅ Related issues with context on why they matter

---

## Example 3: Guideline Update

### ❌ BAD Guideline Update

> **Title:** Update guidelines
>
> **Description:** Add the rule we talked about for specs.

This is BAD because:
- No context on WHAT rule
- No WHY the rule is needed
- No WHERE to add it
- No decision rationale

---

### ✅ GOOD Guideline Update

> **Title:** Guidelines: Add fresh-start context requirements for all specs
>
> **Problem Statement:** Specs often assume context from prior conversations. When a new AI agent picks up a spec (or the same agent after context reset), critical information is missing, leading to incorrect implementations or repeated questions.
>
> **Current State:** Guidelines in the "Mandatory Elements Checklist" section of `144-planning-spec-templates.md` describe requirements analysis but don't mandate self-containment for agent context-loss scenarios.
>
> **Proposed Change:** Add new section 1.2 "Fresh-Start Context Requirements" mandating that all specs include full context inline, with no reliance on "see above" or "as discussed" references.
>
> **Why This Change:**
> 1. AI agents have no persistent memory between sessions
> 2. Different agents may work on the same spec at different times
> 3. Context loss leads to implementation errors
> 4. Self-contained specs reduce back-and-forth questions
>
> **Decision Rationale:**
> - Considered adding to `000-critical-rules.md` — rejected because this is a process improvement, not a zero-tolerance violation
> - Considered separate file — rejected because spec creation workflow should be in one place
> - Chosen: Add to `00-spec-creation.md` as section 1.2, after engineering requirements
>
> **Success Criteria:**
> 1. ✅ New section added
> 2. ✅ Checklist template created
> 3. ✅ Bad/Good examples documented
> 4. ✅ Guidelines load correctly

This is GOOD because:
- ✅ Clear problem statement
- ✅ Current state with file references
- ✅ Proposed change described
- ✅ Decision rationale with alternatives
- ✅ Success criteria listed

---

## Quick Reference: Fresh-Start Checklist

Before finalizing any spec, verify:

| Element | Include This |
|---------|--------------|
| **Problem** | What and WHY (with context) |
| **Location** | File path + function/section anchors + snippets |
| **References** | Issue URL + summary + relevance |
| **Context** | Background, history, affected systems |
| **Constraints** | Technical, time, resource limits |
| **Assumptions** | What might not be true |
| **Criteria** | Testable success conditions |
| **Edges** | Boundary conditions |
| **Deps** | External systems/libraries |
| **Risks** | What could go wrong |

**Golden Rule:** If a new agent with no memory context cannot implement the spec correctly from the spec alone, the spec is incomplete.

---

## Example 4: Sub-issue Structure (Multi-task Spec)

### ✅ GOOD Multi-task Spec with Sub-issues

When a spec has multiple phases/tasks, each phase MUST be tracked as a separate sub-issue.

**Parent Issue:**
> **Title:** [SPEC] Add user authentication
>
> **STATUS:** 1.1
>
> **Objective:** Implement user authentication with OAuth2 and session management.
>
> **Phases:**
> 1. Phase 1: Database schema (user tables, indexes)
> 2. Phase 2: API endpoints (login, logout, refresh)
> 3. Phase 3: UI components (login form, session handling)
>
> **Implementation details in body...**

**Sub-issues CREATED:**
- `#101: [Task: #100] Create database schema for user authentication`
- `#102: [Task: #100] Implement authentication API endpoints`
- `#103: [Task: #100] Build user login UI components`

**Why this works:**
- Each phase is trackable as its own issue
- Progress visible in GitHub's sub-issue view
- Agents can verify which phase to implement
- Clear parent-child hierarchy

### ✅ GOOD Single-task Spec (No Sub-issues Needed)

When a spec has ONE task, no sub-issues are required.

**The Issue:**
> **Title:** [SPEC] Fix typo in README
>
> **STATUS:** 1.1
>
> **Problem:** README contains " instalation" (missing 'l')
>
> **Solution:** Fix the typo in the installation section
>
> **Success Criteria:** Typo corrected

**No sub-issues needed because:**
- ✅ Exactly ONE implementation task
- ✅ No decomposition needed
- ✅ Single unit of work
- ✅ Can be implemented directly

### ✅ GOOD Auto-create Workflow

When a multi-task spec has NO sub-issues, the agent AUTO-CREATES them.

**Scenario:**
- Agent starts implementing spec #100
- Calls `github_issue_read method=get_sub_issues` on #100
- Result: Empty array `[]`
- Spec has 3 phases → multi-task

**Agent Actions:**
```
1. For each PHASE in spec:
   - Create issue: github_issue_write method=create with title "[Task: #100] <phase-description>"
   - Get database ID from response
   - Link: github_sub_issue_write method=add

2. Post comment: "Created 3 sub-issues for phase tracking"

3. Proceed to implement first phase
```

**Result:**
- Sub-issues created: #101, #102, #103
- Parent issue #100 now shows sub-issues
- Progress tracking established
- Agent can proceed with implementation

**Why AUTO-CREATE instead of BLOCK:**
- Maintains workflow momentum
- Developer doesn't have to manually create sub-issues
- Reduces friction in implementation
- Sub-issues still created for proper tracking

---

## Example 5: Issue-First Strategy (No Local Fallback)

### ❌ BAD: Local Plan Files When GitHub Available

> **Title:** [SPEC] Add rate limiting
>
> **Notes:** Created plan file `plans/SPEC-rate-limiting.md` because GitHub MCP was unavailable.

This is BAD because:
- Local files fragment tracking
- No centralized visibility
- Manual sync required
- History is not preserved in GitHub
- Different agents can't see the plan

### ✅ GOOD: GitHub Issues as Sole Mechanism

When GitHub MCP tools are available, GitHub Issues are the ONLY authoritative source.

**Workflow:**
1. Create GitHub Issue with `[SPEC]` prefix
2. Link sub-issues via `github_sub_issue_write method=add`
3. Track STATUS in issue body
4. Post progress comments to issue
5. Close issue after PR merge

**Why this works:**
- Single source of truth in GitHub
- All agents can access
- History preserved automatically
- Progress visible to stakeholders
- No sync required

**When GitHub MCP Unavailable:**
- STOP immediately
- Report: "GitHub MCP tools unavailable. Cannot create or track specs without GitHub Issues."
- Wait for GitHub MCP to be restored
- NO fallback to local plan files

---

*Source: Created to illustrate fresh-start context requirements*