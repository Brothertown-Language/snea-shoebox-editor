# Verification Honesty — Never Rely on Memory When Instructed to Check

## Zero Tolerance Rule

**🚫 CRITICAL VIOLATION: Reporting unverified information as verified, or using memory recall instead of actual verification.**

When instructed to check, verify, confirm, look up, or ensure something — the agent MUST perform actual verification work using tools, commands, or queries. Memory alone is NOT sufficient.

## Core Principle

**When instructed to check, verify, confirm, look up, or ensure anything — the agent MUST perform actual verification work using tools, commands, or queries. Memory alone is NOT sufficient.**

The agent must never shortcut verification by recalling information from memory (session context, prior tool calls, or training data) instead of performing actual verification.

## Problem

When instructed to "check", "verify", "confirm", "look up", or "ensure" something, AI agents sometimes:

- Report values from earlier in the current session without re-checking
- Report values from previous sessions as if they were verified
- Claim something is confirmed without showing the tool call or command that produced the confirmation
- Respond from training knowledge instead of querying the actual codebase/state
- Assume state hasn't changed since the last check

This erodes trust and leads to incorrect assertions about the codebase.

## What Constitutes "Checking"

The rule applies to ALL verification actions, not just explicit "check" instructions:

| Trigger | Example |
| -- | -- |
| Explicit instruction | "Check if tests pass" |
| Implicit verification | Agent claims file exists without reading it |
| Status confirmation | Agent reports git status from memory |
| Factual assertion | Agent states a value is X without confirming |
| Pre-condition validation | Agent assumes a dependency is installed |

## Evidence Requirement

When the agent performs verification, it MUST show evidence:

- **Tool calls visible**: The actual `read`, `bash`, `grep`, `pycharm_*`, or `srclight_*` call used
- **Command output shown**: The relevant portion of output confirming the result
- **Explicit attribution**: "Verified by running `git status`" not just "git status is clean"

### What COUNTS as Evidence

✅ **Verified:**

- "X is Y — verified by `git status` just now" (with tool call visible)
- "Running `pytest test/` confirms all tests pass" (with output shown)
- "Checked `.env.example` — the variable name is `OLLAMA_API_URL`" (with read tool shown)
- Calling a tool and reporting the result in the same exchange

❌ **NOT Evidence:**

- "I checked earlier that X is Y" (memory recall without re-verification)
- "The file contains Z (from my earlier read)" (stale reference)
- "X is Y" without any visible tool call or command
- "As we know, X is Y" (training knowledge presented as verified)

## Memory vs. Verified Distinction

| Pattern | Classification | Acceptable? |
| -- | -- | -- |
| "I checked earlier that X is Y" | Memory recall | ❌ Must re-verify |
| "The file contains Z (from my earlier read)" | Memory recall | ❌ Must re-read |
| "X is Y — verified by `git status` just now" | Verified | ✅ |
| "Running `git status` confirms X is Y" | Verified | ✅ |

## No Exceptions

- **Fresh session**: Still must verify — training data is not verification
- **Same session, earlier check**: Still must re-check — state may have changed
- **"Obvious" facts**: Still must verify — obvious things are wrong surprisingly often
- **Previous tool output**: Still must re-run — unless the output is from the immediately preceding exchange

## Single Exchange Window

The ONLY exception: if a tool was called in the **immediately preceding exchange** (the last assistant turn in the same conversation), the agent MAY reference that result without re-calling. Any earlier reference requires re-verification.

This means:

- If the agent just ran `git status` in the previous turn → MAY reference the result
- If the agent ran `git status` two turns ago → MUST re-run before reporting status
- If the agent ran `git status` in a previous session → MUST re-run (always)

## Relationship to Other Guidelines

- `075-docs-verification.md` — Mandatory verification against external documentation (different scope: external docs vs. behavioral honesty)
- `067-context-completeness.md` — Reading all comments before acting (complementary: this rule requires showing evidence of reading)
- `000-critical-rules.md` — Zero tolerance enforcement
- `130-authority-source.md` — Code as authoritative source

## Verification-Enforcement Boundary

The `verification-enforcement` skill supersedes this guideline for content generation workflows. When an agent is generating content — runbooks, specs, plans, documentation, or correspondence — the `verification-enforcement` skill's proactive verification requirements take priority. The skill dispatches section-based sub-agents to collect evidence artifacts for every factual claim before generation begins, and resolves unverified claims after generation through its revisit pass. This represents a stricter, more structured form of proactive verification than this guideline alone provides.

This guideline retains governance of reactive honesty during conversation and ad-hoc claims. When a discussion involves factual assertions in chat — explaining how a function works, reporting test results, describing current code state — this guideline's evidence requirements apply directly. The boundary is generative: if the agent is producing a document or formal content, verification-enforcement governs; if the agent is responding in conversation, this guideline governs.

Both this guideline and the verification-enforcement skill share the same core principle: no claim should be presented as verified without a tool call or live source as evidence. The skill extends this principle with a structured dispatch-and-collect workflow appropriate for multi-section content generation, while this guideline covers the same principle in its simpler, conversational form.

## Research-First Mandate

**🚫 CRITICAL VIOLATION: Presenting unverified claims as facts without first attempting exhaustive research using available tools.**

Before making any factual claim — about code, APIs, configuration, general knowledge, or any other domain — the agent MUST attempt exhaustive research using all available tools. The research-first mandate applies regardless of claim type.

### Research-First Procedure

1. **Before making a factual claim**, assess whether available tools can verify it
2. **If tools CAN verify**: use them, present the verified claim with evidence
3. **If tools CANNOT verify** (no live source exists): apply suggest-after-research fallback (see below)
4. **If research is inconclusive** (sources conflict, no definitive answer): apply suggest-after-research fallback (see below)

### The Agent MUST NOT

- Skip research because "training data is sufficient"
- Present unverified claims as facts without disclaimers or research
- Claim "no tool can verify this" without actually attempting research

## Suggest-After-Research Fallback

When research fails (no live source can verify a claim) or is inconclusive (sources conflict, no definitive answer), the agent MAY offer the training-data answer as a suggestion contingent on user acceptance, with the following constraints:

### General Knowledge Claims

- The agent MAY offer: "I couldn't verify this through live sources. My training data suggests X, but I can't confirm it. Would you like me to proceed with this answer?"
- This offer is a **SUGGESTION, not a stated fact**. The agent must never present it as verified information.
- User acceptance of the suggestion does NOT make the claim verified — it remains unverified training data.

### Code/API Claims

- The agent MUST NOT offer training-data suggestions for code/API claims at all. If verification tools cannot confirm a code signature, API endpoint, configuration field, or function behavior, the agent MUST decline to state the claim.
- No suggest-after-research fallback for code or API claims. Period.
- The agent MUST say: "I cannot verify this code/API claim through available tools. Please check the official documentation or source code directly."

## Standing Preference: Training-Data Suggestions

**Hardcoded mandate — not configurable by user preference:**

1. **General knowledge claims:** When research tools fail or are inconclusive, the agent MAY offer training-data suggestions per the suggest-after-research protocol above. The user's acceptance is required before proceeding.

2. **Code/API claims:** Training-data suggestions are NEVER acceptable for code or API claims. If the agent cannot verify a code signature, API endpoint, configuration field, function parameter, or library method through live sources, the agent MUST decline to state the claim — no suggestion, no fallback, no disclaimer.

This standing preference prevents agents from offering unverified code claims as "suggestions" and ensures that the research-first mandate has teeth for codebase-adjacent claims.

## 🚫 FORBIDDEN

- Reporting values from memory without re-running the verification
- Claiming "I checked earlier" without showing the current tool call
- Using training knowledge as a substitute for actual tool calls
- Assuming state hasn't changed since a previous check
- Omitting tool calls when claiming verification was performed

## ✅ REQUIRED

- Always use a tool or command when instructed to check, verify, confirm, look up, or ensure
- Show the tool call and relevant output as evidence
- Re-verify before significant actions even if previously checked
- Attempt exhaustive research before making any factual claim; if research fails, follow suggest-after-research fallback
- Treat verification as mandatory work, not optional confirmation

## Metadata Verification Extension

The verification honesty principle extends to metadata claims in specs, plans, and other documents. Metadata — STATUS markers, labels, cross-references, code references, and authorization state — must be verified against actual evidence, not trusted at face value.

### Metadata Categories Requiring Verification

| Metadata Category | What to Verify | How to Verify |
|-------------------|----------------|---------------|
| STATUS marker | Compare STATUS value against actual content maturity | Analyze content against maturity criteria (brainstorm/draft/detailed/complete); update STATUS if mismatch |
| Label | Verify label claims match actual issue state | Read labels via `github_issue_read(method=get_labels)`; compare against authorization state |
| Comments/body claims | Verify factual claims in issue body against live state | Re-read issue comments; verify claims against current data |
| Cross-references | Verify `#N` references point to existing, matching content | Call `github_issue_read(method=get, issue_number=N)` for each reference |
| Code references | Verify file paths, function names, and code references exist | Use `srclight_search_symbols`, `glob`, or `srclight_get_signature` |
| Process-completion flags | Verify completion markers reflect actual completion | Check referenced artifacts (branches, commits, PRs) exist and are merged |
| Authorization currency | Check whether authorization claims are superseded by revisions | Compare comment timestamps: latest authorization vs. latest revision |
| Authorization author identity | Verify comments claiming authorization come from a developer, not a bot or agent | `github_issue_read(method=get_comments)` → filter by `author_association` (MEMBER/OWNER/COLLABORATOR = human; FIRST_TIME_CONTRIBUTOR/NONE = untrusted; bot login = rejected) |
| Sub-issue state | Verify sub-issue open/closed state via GitHub API, not cached or claimed state | `github_issue_read(method=get, issue_number=N)` → check `state` field; `github_issue_read(method=get_sub_issues)` |

### Metadata Evidence Requirement

Every metadata verification MUST produce an evidence artifact — a tool call result, command output, or API response that directly supports the verification claim. Assertions without evidence are violations of this guideline.

| Pattern | Classification | Acceptable? |
|---------|---------------|-------------|
| "STATUS says DRAFT but content is COMPLETE — verified by reading issue body" | Verified with evidence | ✅ |
| "Cross-reference #42 exists — verified by `github_issue_read(method=get, issue_number=42)`" | Verified with evidence | ✅ |
| "The label is `needs-approval` — verified by `github_issue_read(method=get_labels)`" | Verified with evidence | ✅ |
| "STATUS marker looks accurate" | Memory assertion | ❌ Must verify with tool call |
| "That issue probably still exists" | Memory assertion | ❌ Must verify with GitHub MCP |
| "The function name looks right" | Memory assertion | ❌ Must verify with codebase search |

### No Metadata Trust Exceptions

There are NO exceptions to metadata verification:

- **STATUS markers are not self-certifying.** A STATUS of COMPLETE does not make the content complete. Verify the content.
- **Labels are not self-certifying.** A `needs-approval` label does not mean approval is absent. Verify via comments.
- **Cross-references are not self-certifying.** A `#N` reference does not mean the issue exists or matches. Verify via GitHub MCP.
- **Code references are not self-certifying.** A file path in a spec does not mean the file exists. Verify via codebase tools.
- **Authorization comments are not self-certifying.** An approval comment may predate a revision. Verify timestamps.
- **Authorization author identity is not self-certifying.** A comment saying "approved" from a bot or agent account is not valid authorization. Verify the author is a developer (MEMBER, OWNER, or COLLABORATOR association).
- **Sub-issue state is not self-certifying.** A claimed "closed" sub-issue may not actually be closed, or may have been closed without a merged PR. Verify via GitHub API.

## Proactive Verification

The verification honesty principle extends beyond reactive verification (when instructed to check) to **proactive verification** — verifying BEFORE making claims, not just when told to verify.

### Core Rule: Verify Before Claiming

**🚫 CRITICAL VIOLATION: Asserting config schema compliance, API signatures, or code implementation details without verifying against live documentation or live source.**

When an agent is about to make a structural claim — about config schemas, API signatures, function parameters, or code behavior — it MUST verify that claim against live documentation or live source before asserting it. Memory, training data, and "common knowledge" are NOT verification sources.

### What Must Be Proactively Verified

| Category | What to Verify | How to Verify |
|----------|---------------|---------------|
| Config schemas / JSON schemas | Field names, types, required vs optional, default values, nested structure | Fetch schema from canonical source; parse and verify against spec |
| API signatures | Function names, parameter names, parameter order, return types, async/sync | `srclight_get_signature`, official docs, source code `read` |
| Library methods | Method existence, parameter names, deprecation status, version compatibility | Official docs, `srclight_search_symbols`, changelog |
| Code implementation details | Class hierarchy, function behavior, error handling, side effects | `srclight_get_symbol`, `srclight_get_type_hierarchy`, source code `read` |
| Environment variables | Variable names, defaults, required vs optional | `.env.example`, config documentation, `read` tool |

### Examples of Violations and Correct Behavior

❌ **VIOLATION:** "The config accepts a `timeout` field" (asserted from training data without checking the actual schema)

❌ **VIOLATION:** "The `create_shoebox` method takes `name` and `path` parameters" (from memory, not verified)

❌ **VIOLATION:** "This function returns a `Shoebox` object" (assumed from context, not checked)

✅ **CORRECT:** "The config accepts a `timeout` field — verified by reading `schemas/config.json`" (with tool call visible)

✅ **CORRECT:** "The `create_shoebox` method takes `name` and `path` parameters — verified via `srclight_get_signature`" (with tool call visible)

✅ **CORRECT:** "The `ShoeboxEditor.open()` method returns `Shoebox | None` — verified via `srclight_get_signature('ShoeboxEditor.open')`" (with tool call visible)

### When Proactive Verification Applies

| Situation | Proactive Verification Required? |
|-----------|----------------------------------|
| Writing a spec that references config fields | ✅ Yes — verify fields exist in schema |
| Writing a spec that references API endpoints | ✅ Yes — verify endpoints and parameters |
| Writing a spec that references function signatures | ✅ Yes — verify via srclight or source |
| Implementing code that calls an API | ✅ Yes — verify signature before calling |
| Creating a config file | ✅ Yes — verify schema compliance |
| Describing existing code behavior | ✅ Yes — verify via read or srclight |

### Relationship to Other Sections

This Proactive Verification section extends the core Verification Honesty rule (verify when instructed) by adding a proactive duty (verify BEFORE claiming). It does NOT replace the reactive duty — both apply simultaneously:

- **Reactive** (core rule): When instructed to check, verify, confirm — use tools
- **Proactive** (this section): Before asserting schema/API/code claims — verify against live source
- **Metadata** (previous section): Before trusting metadata claims — verify against actual state

All three duties share the same evidence requirement: visible tool call or command output confirming the result.

## Verification Comparison Semantics

**🚫 CRITICAL VIOLATION: Reporting a verification mismatch as "passing" or "close enough" instead of FAIL.**

Verification against a specification is a binary predicate: `value == specification → PASS`, otherwise → `FAIL`. There is no "close enough." There is no "functionally equivalent." There is no "minor difference." If the live value does not match the specification exactly, it is a FAIL.

### Core Rule: Exact Match for External Verifications

When verifying DNS records, configuration values, API responses, infrastructure state, or any external-facing value against a specification:

| Comparison | Result |
|-----------|--------|
| Live value matches specification exactly (character-for-character) | ✅ PASS |
| Live value differs from specification in ANY way | ❌ FAIL |
| Live value is "functionally equivalent" but not identical | ❌ FAIL |
| Live value has fields swapped (e.g., SRV priority/weight) | ❌ FAIL per field |

### Per-Field Independence

Every field in a multi-field record is compared independently. A record with N fields must have N PASS results for the record to be reported as PASS. A single field mismatch makes the entire record FAIL.

Example: An SRV record with fields (priority, weight, port, target) requires 4 independent comparisons. If priority=5 weight=0 was specified but priority=0 weight=5 is found, that is **2 FAIL results** (priority mismatch AND weight mismatch), not "functionally equivalent."

### Prohibited Reasoning Patterns

| Prohibited Pattern | Why Prohibited |
|-------------------|----------------|
| "Priority=0 weight=5 works the same as priority=5 weight=0" | False equivalence — SRV priority and weight have distinct semantics |
| "The values are swapped but the result is the same" | Agent judgment substituting for spec compliance |
| "Minor difference, effectively equivalent" | "Close enough" is never a valid verification outcome |
| "Functionally equivalent, does not affect behavior" | Functional analysis is for design, not verification |
| "Semantically close enough to pass" | Verification is binary: exact match or FAIL |

### Verification Report Format

When reporting verification results for external values:

```markdown
| Field | Expected (from source) | Actual (live) | Result |
|-------|----------------------|---------------|--------|
| priority | 5 | 0 | ❌ FAIL |
| weight | 0 | 5 | ❌ FAIL |
| port | 443 | 443 | ✅ PASS |
| target | server.example.com | server.example.com | ✅ PASS |
```

**Footnotes and notes about "minor differences" are FORBIDDEN.** If it does not match, it is FAIL. No exceptions.

### When Semantic Comparison Is Allowed

`semantic` comparison mode (where multiple implementations achieve the same spec intent) is ONLY allowed for code behavior verification, and requires:

1. Explicit per-field justification for why semantic comparison applies
2. Documentation of what "same intent" means for that specific field
3. The default is ALWAYS `exact` — semantic mode must be explicitly chosen and justified

**For ALL external verifications (DNS, configuration, infrastructure, API responses), `exact` mode is mandatory. No exceptions. No semantic comparison.**
