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
| "I recall X is Y (unverified)" | Honest memory tag | ✅ Only if tagged unverified |
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
- Tag unverified recollections explicitly as "(unverified)"
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

✅ **CORRECT:** "The `timeout` field defaults to 30 seconds (unverified)" — tagged when verification is not yet available

### When Proactive Verification Applies

| Situation | Proactive Verification Required? |
|-----------|----------------------------------|
| Writing a spec that references config fields | ✅ Yes — verify fields exist in schema |
| Writing a spec that references API endpoints | ✅ Yes — verify endpoints and parameters |
| Writing a spec that references function signatures | ✅ Yes — verify via srclight or source |
| Implementing code that calls an API | ✅ Yes — verify signature before calling |
| Creating a config file | ✅ Yes — verify schema compliance |
| Describing existing code behavior | ✅ Yes — verify via read or srclight |
| General explanation or reasoning about approach | ❌ No — but tag unverified assertions |
| Brainstorming alternatives | ❌ No — but tag assertions as speculative |

### Unverified Assertion Tagging

When proactive verification is not immediately feasible (e.g., external service unavailable, schema not yet published), the agent MUST tag unverified assertions:

- Format: `(unverified)` after the assertion
- Example: "The API accepts `page_size` as a query parameter (unverified)"
- Limitations: No more than 3 unverified assertions per spec section before verification becomes mandatory

### Relationship to Other Sections

This Proactive Verification section extends the core Verification Honesty rule (verify when instructed) by adding a proactive duty (verify BEFORE claiming). It does NOT replace the reactive duty — both apply simultaneously:

- **Reactive** (core rule): When instructed to check, verify, confirm — use tools
- **Proactive** (this section): Before asserting schema/API/code claims — verify against live source
- **Metadata** (previous section): Before trusting metadata claims — verify against actual state

All three duties share the same evidence requirement: visible tool call or command output confirming the result.
