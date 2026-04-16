---
name: engineering-approach
description: Use when implementing a spec, or when design, verification, and scope discipline are needed. Triggers on: implement, build, develop, engineering checklist, design before code, verify before complete.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Engineering Approach Checklist

## Core Principles

1. **Understand Before Solving**
   - Read all relevant code before proposing changes
   - Understand the "why" not just "what"
   - Identify stakeholders and their needs

2. **Design Before Implementing**
   - Document the approach in the spec
   - Consider multiple solutions and tradeoffs
   - Get approval on approach before coding

3. **Verify Before Declaring Complete**
   - Run all tests manually
   - Check for edge cases
   - Verify against all success criteria
   - Update documentation

4. **Communicate Changes**
   - Post comments when changes happen (PR created, task completed)
   - DO NOT post comments when creating issues
   - DO NOT post comments for non-substantive updates (cross-references, origin links, STATUS updates)

## Scope Discipline (Critical)

### No Feature Creep

- Implement ONLY what is specified in the approved spec
- No additions, enhancements, or "improvements" beyond scope
- No refactoring unless explicitly requested
- No unrelated fixes discovered during work (file separate issue)

### No Unapproved Work

- Never start implementation without explicit authorization
- "Should I do X?" is a question, not authorization
- Wait for clear "proceed" or "yes" before starting
- If unclear, ask - do not assume

## Anti-Patterns to Avoid

- Jumping straight to implementation without design
- Surface-level analysis without deep understanding
- Missing edge case consideration
- Skipping documentation updates
- Declaring complete without verification
- Posting comments when creating issues
- Being pedantic in communications
- Adding features not in the spec
- Starting work without explicit approval
- "While I'm here" refactoring
- Implementing "nice to haves"

## Requirements Analysis Checklist

Before any implementation:

- [ ] Problem statement documented with full context
- [ ] Constraints and assumptions identified
- [ ] Success criteria are testable and measurable
- [ ] Edge cases identified and documented
- [ ] Dependencies and integrations analyzed
- [ ] Risk assessment completed

## Design Phase Checklist

Before coding:

- [ ] Explored codebase for existing patterns
- [ ] Identified reusable components
- [ ] Documented design decisions
- [ ] Considered alternatives
- [ ] Documented tradeoffs
- [ ] Obtained approval on approach

## Implementation Phase Checklist

During coding:

- [ ] Following spec exactly - no additions
- [ ] Using established patterns from codebase
- [ ] Writing tests alongside implementation
- [ ] Updating documentation as needed
- [ ] **All temp files in `./tmp/` ONLY** — never `/tmp/` or project root

## Pre-Implementation Verification Checklist

Before writing ANY implementation code:

- ☐ **Verify all config schemas, API signatures, and code implementations against live documentation before proceeding.** Run `srclight_get_signature` for function signatures, `srclight_get_symbol` for code details, and fetch JSON schemas for config compliance. Tag any unverified assertions as `(unverified)`.

1. **Verify API Signatures**
   - [ ] Check official documentation for correct parameters
   - [ ] Use `srclight_get_signature` or type hints for function signatures
   - [ ] Confirm library version matches documentation

2. **Verify Environment Variables**
   - [ ] Check `.env.example` for correct names
   - [ ] Confirm from config documentation
   - [ ] Use exact names (no guessing)

3. **Verify Configuration Formats**
   - [ ] Check schema definitions
   - [ ] Review example configs
   - [ ] Confirm field names and types

4. **Document Verification Source**
   - [ ] Note where you verified (docs URL, source file, etc.)
   - [ ] Include verification reference in implementation comments if helpful

## During Implementation Verification

When actively writing code:

1. **Before EACH API Call:**
   - [ ] Verify parameter names from official docs or source
   - [ ] Confirm method/function exists (no invented APIs)
   - [ ] Check return types match expected usage

2. **Before EACH Environment Variable:**
   - [ ] Confirm exact name from `.env.example` or docs
   - [ ] Verify handling of missing values (required vs optional)

3. **Before EACH Library Import:**
   - [ ] Confirm import path matches current library version
   - [ ] Check for deprecation warnings in migration guides

4. **MCP Tool Usage:**
   - [ ] Use PyCharm MCP for file operations (not read/write/edit tools)
   - [ ] Use srclight for Python semantic analysis
   - [ ] Use notebook MCP for `.ipynb` files (never raw file tools)

5. **Temp File Location:**
   - [ ] All temp files go to `./tmp/` — NEVER `/tmp/` system temp
   - [ ] NEVER create temp files at project root
   - [ ] Use `./tmp/` for investigation scripts, test outputs, scratch files

## Post-Implementation Review

After implementation, before marking complete:

1. **Self-Review:**
   - [ ] All API calls verified against docs
   - [ ] All environment variables match config
   - [ ] No assumed or guessed parameter names
   - [ ] Library usage matches current version

2. **Evidence of Verification:**
   - [ ] Comments reference documentation sources where helpful
   - [ ] Complex APIs include doc references for future maintainers

3. **Temp File Cleanup:**
   - [ ] All temp scripts removed from `./tmp/` (unless intentionally cached)
   - [ ] No temp files left at project root
   - [ ] `ls ./tmp/` shows only intentional persistent files

## Verification Phase Checklist

Before declaring complete:

- [ ] All tests pass manually
- [ ] Edge cases verified
- [ ] Success criteria validated
- [ ] Documentation updated
- [ ] No scope creep introduced
- [ ] **Temp files cleaned up** — no `temp_*.py` or `*.json` left in `./tmp/`
- [ ] **No temp files at project root** — confirm with `ls *.py *.json 2>/dev/null`

## Live Verification: Understanding Claims (MANDATORY)

**🚫 CRITICAL: When this skill claims understanding of code (patterns, dependencies, architecture), it MUST verify against live codebase state. Understanding claims without code verification are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Understanding Claim | Verification Action | Tool Call | Problem Class |
|-------------------|-------------------|-----------|---------------|
| "Codebase uses pattern X" | Verify pattern actually exists in codebase | `srclight_search_symbols(query="pattern", kind="class")` → confirm results | VERIFICATION-GAP |
| "Function Y depends on Z" | Verify actual call relationship | `srclight_get_callers(symbol_name="Y")` or `srclight_get_callees(symbol_name="Y")` | CONFLICTING |
| "Module follows architecture A" | Verify architectural boundaries in code | `srclight_search_symbols(query="module", kind="function")` → check file paths | STRUCTURE-VIOLATION |
| "Library X available in project" | Verify library is in dependencies | `read(filePath="pyproject.toml")` → check dependencies | MISSING-ELEMENT |
| Pre-implementation verification complete | Verify each checklist item has tool-call evidence, not just assertions | Review checklist items for tool-call artifacts | VERIFICATION-GAP |

**Evidence format:**

```
Check: [what was verified]
Tool: [tool call and parameters]
Result: [actual state found]
Classification: [STRUCTURE-VIOLATION|MISSING-ELEMENT|CONFLICTING|VERIFICATION-GAP|MISSING-TRACEABILITY]
Action: [auto-fix|conditional|flag-for-review]
```

**Classification on failure:**

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Pattern not found | VERIFICATION-GAP | conditional | Search alternates, verify with broader query |
| Call relationship wrong | CONFLICTING | flag-for-review | HALT — design may be based on wrong dependencies |
| Architecture assumption wrong | STRUCTURE-VIOLATION | flag-for-review | HALT — redesign may be needed |
| Library not in dependencies | MISSING-ELEMENT | flag-for-review | HALT — add dependency or use alternative |
| Checklist items lack evidence | VERIFICATION-GAP | conditional | Re-verify items with tool calls |

## Cross-Reference Verification (MANDATORY)

**🚫 CRITICAL: Each cross-reference must be verified against actual skill content. Assertions without verification are VERIFICATION-GAP findings.**

| Reference | Verification | Finding Class |
| -- | -- | -- |
| `programming-principles` in Cross-References | File exists at `.opencode/skills/programming-principles/SKILL.md` | MISSING-TRACEABILITY if missing |
| `code-size-enforcement` in Cross-References | File exists at `.opencode/skills/code-size-enforcement/SKILL.md` | MISSING-TRACEABILITY if missing |
| `spec-auditor` ground-truth subtask | File exists at `.opencode/skills/spec-auditor/tasks/ground-truth.md` | MISSING-TRACEABILITY if missing |
| `065-verification-honesty.md` metadata extension | Guideline contains "Metadata Verification Extension" section | CONFLICTING if missing |
| `080-code-standards.md` in Cross-References | Guideline exists at `.opencode/guidelines/080-code-standards.md` | MISSING-TRACEABILITY if missing |
| Task table entry `verify-understanding` | File exists at `.opencode/skills/engineering-approach/tasks/verify-understanding.md` | MISSING-TRACEABILITY if missing |
| `programming-principles` principle definitions | Matches actual SKILL.md: 20 engineering principles defined | CONFLICTING if mismatched |

**Verification Procedure:**

Before invoking any cross-referenced skill:
1. `ls .opencode/skills/<skill-name>/SKILL.md` → EVIDENCE: file exists or MISSING-TRACEABILITY
2. `grep -c "<task-name>" .opencode/skills/<skill-name>/SKILL.md` → EVIDENCE: task referenced or MISSING-TRACEABILITY
3. Compare described behavior with actual content → EVIDENCE: match or CONFLICTING

**Classification on failure:**

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Referenced skill file missing | MISSING-TRACEABILITY | flag-for-review | Cannot verify cross-reference |
| Referenced guideline missing | MISSING-TRACEABILITY | flag-for-review | Guideline may have been renamed |
| Described behavior mismatches | CONFLICTING | flag-for-review | Cross-reference may be stale |

**Adversarial cross-reference:** The `spec-auditor --task ground-truth` subtask (Phase 1 of spec #827) performs adversarial verification of code references including file paths, function names, and code references in specs. When this skill's pre-implementation verification finds code references in a spec that may not exist in the codebase, invoke `spec-auditor --task ground-truth` to verify. See `065-verification-honesty.md` → "Metadata Verification Extension" for the extended principle.

## Cross-References

| Reference | Relationship |
|-----------|-------------|
| `programming-principles` skill | Design judgment for 20 engineering principles — this skill owns *when* to verify, that skill owns *what* principles to apply |
| `code-size-enforcement` skill | Size limit enforcement — SRP and "No Monoliths" have hard limits there |
| `spec-auditor` (ground-truth subtask) | Adversarial verification of code references in specs |
| `080-code-standards.md` | Project-specific conventions (typing, modern Python, libraries, linting) |
| `065-verification-honesty.md` | Metadata verification extension for spec/code claims |

## Invocation

Use this skill when:
- Starting implementation of an approved spec
- Before creating a PR
- During code review to check for scope creep
- After completing work to verify completeness

Example: `/skill engineering-approach`