# Task: verify-authorization — Step 0.5: Scope Auto-Resolve

## Purpose

Resolve `authorization_scope` from the authorization phrase using the verb-prefix parsing table BEFORE any human-facing output or sub-agent dispatch. Scope detection is NEVER ambiguous — the parsing table is deterministic.

## Mandatory Position

This step MUST execute before Step 1, Step 2.0, and before any screen-issue dispatch. Per `000-critical-rules.md` → "Pushing Agent Intelligence Decisions" and `020-go-prohibitions.md` §1 "ASK FIRST", scope detection via parsing table is NEVER ambiguous.

**Under NO circumstances does the agent ask the user to classify scope.** The verb-prefix parsing table in Step 2.0 is the sole authority. Every possible authorization phrase maps to exactly one scope.

## Procedure

Parse the authorization text using the verb-prefix regex patterns from the Scope Parsing Module (`enforcement/scope-parsing.md`).

| Authorization Phrase | Resolved Scope |
| -- | -- |
| "approved #N" (no qualifier) | `standard` |
| "approved #N to PR" / "for PR" | `for_pr` |
| "approved #N to implementation" / "for implementation" | `for_implementation` |
| "approved #N to plan" / "for plan" | `for_plan` |
| "approved #N for review" | `for_code_review` |
| "approved #N to spec" / "for spec" | `for_spec` |

If a qualifier matches, set `authorization_scope` to the corresponding scope value with `scope_source = "parsed"`. If no qualifier matches, set `authorization_scope = "standard"` with `scope_source = "default"`.

Derive `halt_at`, `pr_strategy`, and `gap_fill_actions` from the resolved scope per the Auto-Dispatch Table Module (`enforcement/auto-dispatch-table.md`).

Record the parsed result as an evidence artifact — no human input is solicited.

## Evidence Artifact

The parsed authorization text, matched regex pattern (or default fallback), and resulting `(authorization_scope, scope_source, halt_at, pr_strategy, gap_fill_actions)` tuple MUST be recorded in the verification report without soliciting human input.

## Work State I/O

- **Reads from:** None (first task in chain)
- **Writes to:** `## scope-auto-resolve`

After completing this task, write results to the work state file under section `## scope-auto-resolve` using the YAML format defined in `enforcement/work-state-schema.md`.