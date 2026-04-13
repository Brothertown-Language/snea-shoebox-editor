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
