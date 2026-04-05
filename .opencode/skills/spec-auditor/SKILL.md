---
name: spec-auditor
description: Audits GitHub Issue [SPEC] specs for LLM implementability - fresh-start context, completeness, and content quality. Runs SECOND after concern-separation-auditor.
license: MIT
compatibility: opencode
---

## When to Invoke

**See `AGENTS.md` → "Skill Invocation Guidance" for the complete trigger table.**

This skill is invoked at these workflow triggers:

| Workflow Trigger | Invocation | Purpose |
|------------------|------------|---------|
| Creating new specs | `/skill spec-auditor --task generate-independent-spec --issue N` | First: clean-room draft |
| After concern-separation-auditor | `/skill spec-auditor --task audit --issue N` | Third: content quality |
| After spec changes | `/skill spec-auditor --task audit --issue N` | Post-change verification |

## This Skill's Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `overview` | Full skill content for spec content quality auditing | ~1800 |
| `generate-independent-spec` | Generate complete, implementable spec draft from scratch | ~600 |
| `audit` | Run full audit: fresh-start context, codebase verification, content quality | ~600 |
| `verify-codebase` | Verify spec references match live codebase | ~400 |

## Scope: Content Quality for LLM Implementation

**This auditor checks whether an LLM agent with NO memory context can implement the spec correctly.**

**Phase structure, deployment independence, and risk isolation are NOT checked here** — they belong to `concern-separation-auditor` which runs SECOND (after clean-room draft generation).

### Division of Responsibility

| Auditor | Scope | Role |
|---------|-------|------|
| `spec-auditor --task generate-independent-spec` | Clean-room draft generation | FIRST - generate spec WITHOUT viewing live (pollution prevention) |
| `concern-separation-auditor` | Phase structure, deployment independence, risk isolation, blast radius, phase names | SECOND - structural safety |
| `spec-auditor --task audit` | Fresh-start context, completeness, content quality, LLM implementability | THIRD - content quality |
| `dev-architect --task review-spec` | Architectural correctness, compliance, interdependencies, ordering | FOURTH - architectural correctness |

**CRITICAL: All FOUR auditors are MANDATORY. No skipping.**

**Workflow:**

```
Create spec issue #N →
Invoke spec-auditor --task generate-independent-spec --issue N (FIRST - clean-room draft) →
Invoke concern-separation-auditor --issue N (SECOND - phase structure, auto-fix) →
Invoke spec-auditor --task audit --issue N (THIRD - content quality) →
Invoke dev-architect --task review-spec (FOURTH - architectural correctness) →
Add needs-approval label →
Post "ready for review" comment
```

## Available Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `overview` | Full skill content for spec content quality auditing | ~1800 |
| `generate-independent-spec` | **Generate complete, implementable spec draft from scratch** (NOT a checklist) | ~600 |
| `audit` | Run full audit: fresh-start context, codebase verification, content quality | ~600 |
| `verify-codebase` | Verify spec references match live codebase (files, modules, functions) | ~400 |

## Independent Draft = Real Spec (CRITICAL)

**The "independent draft" created by this skill is a COMPLETE SPEC DRAFT that could be implemented from scratch — NOT a checklist, NOT meta-commentary, NOT "what makes a good spec."**

### What the Draft IS

- An implementable specification
- Specific problem statement for THIS issue
- Technical solution with architecture
- Affected files with function/section anchors
- Testable success criteria
- Edge cases specific to THIS implementation
- Dependencies and risk assessment

### What the Draft IS NOT

- A checklist of "what specs should include"
- A prose description of "expected structure"
- A template of "six core areas coverage"
- Generic advice about spec writing

### Detection: How to Know If You're Doing It Wrong

**If you're writing:**
- "A good spec should include..."
- "Expected structure for this spec type..."
- "What makes a good spec..."
- "Common pitfalls for specs..."

**You're generating meta-commentary, NOT a spec. STOP and write a real spec.**

**If you're writing:**
- "The problem is that users can't find the search results..."
- "The proposed solution adds two search modes..."
- "Affected files: `src/services/search.py`..."
- "Success criteria: Search 'wampuw' finds record..."

**You're generating a REAL spec. CORRECT.**

## Workflow

**⚠️ MANDATORY AUDIT CHAIN (ALL SKILLS RUN)**

**When ANY request comes for spec/issue/task audit/review/revisit, ALL auditor skills must run in order. NO SKIPPING.**

### Complete Audit Chain

| Order | Skill | Purpose |
|-------|-------|---------|
| **1st** | `spec-auditor --task generate-independent-spec` | Generate complete, implementable spec draft WITHOUT viewing live spec (pollution prevention) |
| **2nd** | `concern-separation-auditor` | Phase structure, deployment independence, risk isolation, blast radius, phase names |
| **3rd** | `spec-auditor --task audit` | Fresh-start context, completeness, content quality, LLM implementability |
| **4th** | `dev-architect --task review-spec` | Architectural correctness, compliance, interdependencies, ordering |

**Trigger words that require ALL skills:**

- "audit this spec"
- "review this issue"
- "revisit this task"
- "check this [SPEC]"
- "validate the spec"
- "audit the issue"
- Any request involving spec quality or structure

**CRITICAL: If you run ONE auditor, you MUST run ALL FOUR in order.**

______________________________________________________________________

1. **Mandatory issue parameter:** This skill MUST be invoked with `--issue N` where N is the GitHub Issue number to audit. If invoked without this parameter, immediately error: "Usage: /skill spec-auditor --issue N"
1. **AUTO-FIX BY DEFAULT:** Apply fixes automatically unless user says "don't fix" or "just report". This is the default behavior - no asking for permission.
1. **One issue at a time.** Present exactly one identified problem per interaction. Do not batch or preview other issues.
1. **BREVITY IN COMMENTS (CRITICAL):** All GitHub Issue comments MUST be concise:
   - Maximum 200 words total
   - Maximum 10 rows in any table
   - No verbatim spec quotes longer than 3 lines
   - Put detailed findings in the audit log (`./tmp/audit-spec-YYYYMMDD.md`), NOT in the comment
   - The comment is for stakeholder visibility, not documentation
   - Format: `Issue #N: PROBLEM_CLASS - 1-sentence summary. Fixed: [brief description].`
   - If complex detail is needed, write to audit log first, then reference it briefly in comment
1. **Issue report format:**
   - **Issue Location**: Which section/requirement of the spec has the problem.
   - **Problem class**: One of: `FRESH-START-VIOLATION`, `SIX-AREA-INCOMPLETE`, `MISSING-ELEMENT`, `STRUCTURE-VIOLATION`, `AMBIGUOUS`, `CONFLICTING`, `SCOPE-CREEP-RISK`, `VERIFICATION-GAP`, `CONTEXT-OVERFLOW`, `SUPERSEDED-CLOSURE-VIOLATION`, `COMMENT-FORMAT-VIOLATION`, `ARCHITECTURAL-REASONING-GAP`, `DEPENDENCY-INCOMPLETE`.
   - **Explanation**: Why this is a problem for LLM implementation (1-3 sentences).
   - **Proposed minimal fix**: The smallest change that resolves the issue.
   - **Required remediation indicators**: Explicitly list the exact edits needed (section + concrete change).
   - **Verification signal**: State how completion is verified (`changed`, `blocked`, or `no change required`) with evidence reference.
1. **AUTO-FIX BY DEFAULT**: Apply fixes automatically unless user says "don't fix" or "just report". Post GitHub Issue comment documenting the fix with brief one-liner.
1. **User responses drive action:**
   - No response → AUTO-FIX immediately, post comment, proceed to next issue.
   - "don't fix" → Skip this issue, move to next.
   - "just report" → Skip fixing, post finding only, move to next.
   - "stop" → End the audit session.
1. **After applying a fix**, post brief GitHub Issue comment documenting the change, then proceed to the next issue.
1. **Independence**: Each issue is evaluated and resolved independently. Fixing one issue must not silently alter the resolution of another.
1. **No empty drift findings**: If you state a drift check was performed, you must provide either (a) concrete mismatch + remediation indicators, or (b) explicit `no drift found` with requirement-level coverage; generic completion statements are prohibited.

## Issue Report Template (for each turn)

Issue Location: \<section/requirement in spec>
Problem class: \<FRESH-START-VIOLATION|SIX-AREA-INCOMPLETE|MISSING-ELEMENT|STRUCTURE-VIOLATION|AMBIGUOUS|CONFLICTING|SCOPE-CREEP-RISK|VERIFICATION-GAP|CONTEXT-OVERFLOW|SUPERSEDED-CLOSURE-VIOLATION|COMMENT-FORMAT-VIOLATION|ARCHITECTURAL-REASONING-GAP|DEPENDENCY-INCOMPLETE>
Explanation: \<1-3 sentences>
Proposed minimal fix: <smallest change>
Required remediation indicators: \<section + exact change list>
Verification signal: \<changed|blocked|no change required> — <one-line evidence>

## Audit Standards

This auditor uses `docs/specs/how-to-write-good-spec-ai-agents.md` as the master spec standard. Key requirements include:

### Fresh-Start Context Requirements (CRITICAL)

Per `045-open-questions.md` and `140-planning-spec-creation.md`, specs MUST be self-contained for agents with NO memory context:

1. **NO "see above" or "as discussed" references**

   - ❌ "As discussed above..."
   - ❌ "See the previous comment..."
   - ❌ "As mentioned in the chat..."
   - ✅ RESTATE all information inline in the spec

1. **Explicit file/line references**

   - Include exact file paths: `src/module/file.py`
   - Use STABLE ANCHORS: function names `process_data()`, class names `ClassName`, or section headers `"Section Name"`
   - ⚠️ AVOID line numbers `file.py:42` — they break on every edit
   - Include relevant code snippets (if short, \<20 lines)

1. **Cross-references with context**

   - When referencing other issues/specs: include issue number AND brief summary
   - Include URLs: `https://github.com/<owner>/<repo>/issues/123`
   - State WHY the reference matters

1. **Decision rationale documented**

   - Why was this approach chosen?
   - What alternatives were considered?
   - What constraints drove the decision?

### Six Core Areas (from master spec)

Every spec MUST cover:

1. **Commands**: Executable commands with flags (npm test, pytest -v, etc.)
1. **Testing**: How to run tests, framework, test locations, coverage
1. **Project Structure**: Where source code lives, tests go, docs belong
1. **Code Style**: Naming conventions, formatting, code examples
1. **Git Workflow**: Branch naming, commit message format, PR requirements
1. **Boundaries**: Three-tier boundary system (always/ask-first/never)

### Structure Requirements

Per `140-planning-spec-creation.md`:

- **STATUS header**: `STATUS: phase.step` (e.g., `STATUS: 1.2`)
- **CREATED date**: `CREATED: YYYY-MM-DD`
- **Numbered Phases**: Phase 1, Phase 2, Phase 3...
- **Numbered Steps**: 1, 2, 3 within each phase
- **Status Markers**: `☐`/`↻`/`☑`/`☒` for each step

### Verification Requirements

Per `085-engineering-approach.md`:

- Success criteria must be testable and measurable
- Edge cases must be identified and documented
- All tests must pass before declaring complete
- Documentation must be updated

## Subtask Separation Requirement (CRITICAL)

**⚠️ MANDATORY: Independent draft generation BEFORE viewing live spec.**

### Why This Matters

When auditors view the live spec first, their analysis is influenced by what they see. Spec drifts, missing elements, and conflicts may be missed because they become "normal" through exposure. Independent draft generation ensures fresh eyes.

### Workflow Sequence

| Step | Task | Purpose |
|------|------|---------|
| 1 | `generate-independent-spec` | Generate COMPLETE spec draft WITHOUT viewing live spec |
| 2 | `audit` | Load live spec, compare to draft, identify gaps and conflicts |
| 3 | `verify-codebase` | Check spec references against live codebase |
| 4 | Post audit log | Attach results to GitHub Issue |

**CRITICAL: Step 1 MUST complete BEFORE Step 2 starts.**

### Draft Quality Requirement

**The draft must be an IMPLEMENTABLE SPEC, NOT meta-commentary.**

When comparing draft to live spec, you're comparing:
- Two specs for the same problem
- Real problem statements
- Concrete file references
- Testable success criteria

You're NOT comparing:
- A checklist to a spec
- "What makes a good spec" to a spec
- Generic advice to actual content

### Pollution Prevention

The `generate-independent-spec` task runs in a subtask to prevent ANY access to the live spec:

- Subtask has NO access to the live spec GitHub Issue body
- Subtask works ONLY from the issue number and general knowledge
- Draft is written to `./tmp/tmp-spec-{issue}-draft.md`
- Live spec is loaded ONLY after draft is complete

**This separation is MANDATORY and CANNOT be bypassed.**

## Independent Draft Generation (CRITICAL)

**The draft is NOT a format checklist. It's a prose-driven analysis.**

### What the Draft Contains

- **Expected Structure**: Prose description of what a good spec should include
- **Fresh-Start Requirements**: Prose explanation of inline context requirements
- **Six Core Areas**: Prose coverage of commands, testing, structure, style, git, boundaries
- **Common Pitfalls**: Prose description of typical issues for this spec type
- **Draft Checklist**: Checklist of essential elements (NOT static format checks)

### What the Draft Does NOT Contain

- Static format checks (e.g., "STATUS header must exist")
- Boilerplate requirements (e.g., "Phases must be numbered")
- Copy-paste checks from templates

**The draft is a narrative that EXPLAINS what should be in the spec, not a checklist that ENFORCES formats.**

## Codebase Verification (CRITICAL)

**Specs MUST reference live codebase accurately. Obsolete references cause implementation failures.**

### Why Codebase Verification Matters

- Spec references a file that was deleted or moved → implementation fails
- Spec references a function that was renamed → implementation fails
- Spec references a module pattern that no longer exists → implementation fails
- Spec references a dependency that was removed → implementation fails

### Codebase Verification Process

| Step | Action | Tool |
|------|------|------|
| 1 | Extract all file/function/module references from spec | Parse spec body |
| 2 | Verify each file exists | `pycharm_find_files_by_glob` or `srclight_symbols_in_file` |
| 3 | Verify each function exists | `srclight_get_symbol` |
| 4 | Verify each module exists | `srclight_search_symbols` |
| 5 | Identify obsolete references | Compare spec references to live codebase |
| 6 | Identify missing context | Find codebase elements that SHOULD be referenced |

### Tool Preference for Codebase Verification

Per `016-srclight-preference.md`:

| Task | Tool |
|------|------|
| Verify Python symbol exists | `srclight_get_symbol` |
| Find Python symbols by name | `srclight_search_symbols` |
| Find Python symbols by meaning | `srclight_semantic_search` |
| Verify Python file exists | `srclight_symbols_in_file` |
| Verify non-Python file exists | `pycharm_find_files_by_glob` |
| Search text in files | `pycharm_search_in_files_by_text` |

**Use srclight tools PREFERENTIALLY for Python code verification.**

### New Problem Classes for Codebase Verification

- **STALE-SPEC**: Spec references code that has changed, moved, or been removed.
- **CONFLICTING-SPEC**: Spec contradicts current codebase architecture.
- **SUPERSEDED-SPEC**: Another spec has already implemented this work.
- **DUPLICATE-SPEC**: Multiple specs describe the same work.

## Prose-Driven Analysis Requirement (CRITICAL)

**Audits are prose-driven analysis, NOT static format enforcement.**

### What This Means

- **Analyze content quality through prose explanations**, NOT tick boxes
- **Explain WHY something is problematic**, NOT just flag it
- **Describe what SHOULD be there**, NOT just check if template matches
- **Focus on LLM implementability**, NOT template compliance

### Anti-Patterns (DO NOT)

```markdown
❌ WRONG: "STATUS: 1.2 header is missing. All specs must have STATUS header."

✅ CORRECT: "A new LLM agent starting fresh has no way to know where this spec is in its workflow. 
The STATUS field provides crucial context: the agent knows whether to start from Phase 1 or 
continue from Phase 3. Without this, the agent might re-implement completed work or skip 
required steps. The STATUS should be: `STATUS: 1.2` to indicate Phase 1, Step 2 is in progress."
```

### Why Prose-Driven Matters

- **Focus on implementability**, NOT template compliance
- **Explain reasoning**, NOT enforce rules
- **Describe context gaps**, NOT check boxes
- **Identify conflicts through understanding**, NOT pattern matching

## Content Quality Checks (CRITICAL)

### What This Auditor Checks

| Check | Problem Class | Description |
|-------|---------------|-------------|
| Fresh-start context | `FRESH-START-VIOLATION` | Can agent with no memory understand this? |
| Six core areas | `SIX-AREA-INCOMPLETE` | Are all required areas covered? |
| Required elements | `MISSING-ELEMENT` | STATUS, CREATED, success criteria, etc. |
| Structure format | `STRUCTURE-VIOLATION` | Phase/step numbering, status markers |
| Architectural reasoning | `ARCHITECTURAL-REASONING-GAP` | WHY explained with alternatives? |
| Success criteria | `VERIFICATION-GAP` | Testable with acceptance criteria? |
| Dependencies | `DEPENDENCY-INCOMPLETE` | Specific integration points? |
| Comment format | `COMMENT-FORMAT-VIOLATION` | Executive summary format correct? |
| Scope discipline | `SCOPE-CREEP-RISK` | Changes align with objective? |
| Ambiguity | `AMBIGUOUS` | Could be interpreted multiple ways? |
| Conflicts | `CONFLICTING` | Parts contradict each other? |
| Superseded closure | `SUPERSEDED-CLOSURE-VIOLATION` | Closing comment claims future action? |

### What This Auditor Does NOT Check (Belongs to concern-separation-auditor)

| Check | Belongs To |
|-------|------------|
| Phase names describe concerns | `concern-separation-auditor` |
| Concern mixing (`PHASE-CONCERN-MERGE` → `CONCERN_MIXING`) | `concern-separation-auditor` |
| Deployment independence | `concern-separation-auditor` |
| Risk profile separation | `concern-separation-auditor` |
| Blast radius minimization | `concern-separation-auditor` |
| Dependency direction | `concern-separation-auditor` |
| BOILERPLATE-TITLE for phases/titles | `concern-separation-auditor` |

## Problem Class Definitions

### Fresh-Start Context Classes

- **FRESH-START-VIOLATION**: Spec relies on memory context, chat history, or external references not included inline.
- **CONTEXT-OVERFLOW**: Spec section is overly long or complex, risking truncation or dilution in LLM context.

### Structure Classes

- **SIX-AREA-INCOMPLETE**: Spec is missing one or more of the six core areas (commands, testing, structure, style, git, boundaries).
- **MISSING-ELEMENT**: Spec lacks a required element (STATUS, CREATED date, success criteria, edge cases, dependencies, risk assessment).
- **STRUCTURE-VIOLATION**: Spec doesn't follow the phase/step numbering or status marker format.

### Content Quality Classes

- **ARCHITECTURAL-REASONING-GAP**: Missing WHY explanation, alternatives, or constraints in architecture.
- **VERIFICATION-GAP**: Success criteria untestable, vague, or missing acceptance criteria.
- **DEPENDENCY-INCOMPLETE**: Dependencies lack specific integration points or migration guides.
- **COMMENT-FORMAT-VIOLATION**: Wrong comment format (wrong emoji, missing Summary/Outcome sections).
- **QUESTION-ASKING-VIOLATION**: Spec contains agent question patterns that violate silent HALT protocol (asking for preferences, continuation, PR readiness, etc.).

### Scope/Semantic Classes

- **AMBIGUOUS**: Spec language can be interpreted multiple ways by an LLM, leading to inconsistent behavior.
- **CONFLICTING**: Two or more parts of the spec contradict each other.
- **SCOPE-CREEP-RISK**: Spec includes features or changes beyond the stated objective without explicit approval.
- **SUPERSEDED-CLOSURE-VIOLATION**: Issue closing comment claims future action without execution, or references non-existent replacement.

### Codebase Verification Classes

- **STALE-SPEC**: Spec references code that has changed, moved, or been removed since spec creation.
- **CONFLICTING-SPEC**: Spec contradicts current codebase architecture or patterns.
- **SUPERSEDED-SPEC**: Another spec has already implemented this work (duplicate or conflicting).
- **DUPLICATE-SPEC**: Multiple specs describe the same work (consolidate needed).

## Audit Checklist

For each GitHub Issue `[SPEC]`, verify:

### Fresh-Start Context (MANDATORY)

- \[ \] All context stated inline (no "see above", "as discussed")
- \[ \] File paths use stable anchors (function names, section headers)
- \[ \] Cross-references include summaries
- \[ \] Decision rationale documented

### Six Core Areas

- \[ \] Commands specified with flags
- \[ \] Testing approach documented
- \[ \] Project structure defined
- \[ \] Code style examples included
- \[ \] Git workflow documented
- \[ \] Three-tier boundaries defined (always/ask-first/never)

### Structure Compliance

- \[ \] STATUS header present with phase.step
- \[ \] CREATED date present
- \[ \] Phases numbered sequentially (1, 2, 3...)
- \[ \] Steps numbered within each phase (1, 2, 3...)
- \[ \] Status markers used correctly (☐/↻/☑/☒)

### Content Quality

- \[ \] Architectural reasoning explains WHY with alternatives
- \[ \] Success criteria are TESTABLE with acceptance criteria
- \[ \] Dependencies have SPECIFIC integration points
- \[ \] Comment format uses executive summary (✅ emoji, Summary, Outcome)

### Scope Discipline

- \[ \] All changes align with stated objective
- \[ \] No unapproved features
- \[ \] No refactoring beyond scope

### Superseded Issue Closure (When Closing Issues)

- [ ] Closing comment does NOT claim future action without execution
- [ ] Replacement issue exists BEFORE old issue is closed
- [ ] No forward-looking language ("will be created", "to be done separately")

### Codebase Verification (CRITICAL)

- [ ] All referenced files exist at specified paths
- [ ] All referenced functions/methods exist with matching signatures
- [ ] All referenced modules/classes exist and are importable
- [ ] Codebase patterns mentioned still exist (no obsolete references)
- [ ] Dependencies mentioned still exist in project
- [ ] No STALE-SPEC, CONFLICTING-SPEC, SUPERSEDED-SPEC, or DUPLICATE-SPEC issues

## Post-Fix Verification (Required)

After each fix is applied, the auditor MUST:

1. **Re-read the modified spec** (via GitHub MCP tools) to verify the change was applied correctly.
1. **Re-check compliance** for the specific requirement that was fixed — does the fix resolve the identified problem class?
1. **Re-verify codebase references** (if applicable) using srclight/pycharm tools per `016-srclight-preference.md`.
1. **Report verification** in the next response before moving to the next issue:
   - **Verification signal**: `changed` — the fix was applied and the issue is resolved.
   - **Verification signal**: `blocked` — the fix could not be applied (explain why).
   - **Verification signal**: `no change required` — the requirement was reviewed and found correct as-is.
1. **Post GitHub Issue comment** documenting each change.
1. **Document in audit log** (see Audit Log section below).

## GitHub Comment Format (MANDATORY)

Per `000-critical-rules.md` and `github-comments` skill, ALL completion comments MUST use executive summary format with byline at the BOTTOM:

```
**Summary:**

<1-2 sentences describing impact and stakeholder value>

**Outcome:** <What changed for stakeholders>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

**Required Elements:**

- **Summary section** FIRST with executive summary (1-2 sentences, stakeholder value)
- **Outcome section** describing what changed
- **Horizontal rule** (`---`) separator
- **Byline at BOTTOM** with ✅ emoji, agent name, and model ID

**FORBIDDEN:**

- Byline at TOP (belongs at BOTTOM)
- 📝 emoji for completion comments (use ✅)
- Missing Summary or Outcome sections
- Punch-list format (bullet point lists)
- Technical changelogs (focus on impact, not files)

### Error Handling

- If GitHub MCP is unavailable, report error and halt
- If issue cannot be read, report error and skip to next
- If issue cannot be updated, document in audit log and continue

## Audit Log (Required)

After the audit session completes (user says "stop" or no more issues found), the auditor MUST create an audit log:

**Location:** `./tmp/audit-spec-YYYYMMDD.md` (where YYYYMMDD is today's date)

**Format:**

```markdown
# Audit Log: Spec Content Quality

Date: YYYY-MM-DD
Auditor: spec-auditor
Issue: #N (URL to issue)
Scope: GitHub Issue [SPEC] content quality auditing

## Summary
- Issues Found: N
- Issues Fixed: M
- Issues Skipped: K
- Remaining: L (issues identified but not yet resolved)

## Issues Processed

### Issue 1
Issue Location: <section>
Problem class: <class>
Status: <fixed|skipped|pending>
Fix applied: <description of fix or "skipped per user request">
GitHub Comment: <URL to comment>

### Issue 2
...

## Unresolved Issues
<List any issues identified but not resolved during this session>

## Fresh-Start Context Compliance
- Inline context: <PASS|FAIL> (reason if fail)
- File references: <PASS|FAIL> (reason if fail)
- Cross-reference quality: <PASS|FAIL> (reason if fail)

## Six-Area Coverage
- Commands: <PASS|FAIL|N/A>
- Testing: <PASS|FAIL|N/A>
- Project Structure: <PASS|FAIL|N/A>
- Code Style: <PASS|FAIL|N/A>
- Git Workflow: <PASS|FAIL|N/A>
- Boundaries: <PASS|FAIL|N/A>

## Codebase Verification Results
- Files verified: <N/M> (<pass/fail count> / <total references>)
- Functions verified: <N/M>
- Modules verified: <N/M>
- Stale references found: <list or "none">
- Missing context: <list or "none">
- Problem classes: <STALE-SPEC|CONFLICTING-SPEC|SUPERSEDED-SPEC|DUPLICATE-SPEC|none>
```

**Requirements:**

- Log MUST be created after every audit session.
- Log MUST include all issues identified (fixed, skipped, or pending).
- Log MUST be written to `./tmp/` directory.
- Log file MUST NOT be committed to version control (tmp files are excluded).

## Fresh-Start Context Preservation (CRITICAL)

**After creating the audit log, ATTACH the content to the spec issue being audited.**

### Attachment Workflow

1. **After writing audit log to `./tmp/audit-spec-YYYYMMDD.md`:**

   - Read the full audit log content
   - Post as comment on the GitHub Issue specified by `--issue N`
   - Delete the temp file: `rm ./tmp/audit-spec-YYYYMMDD.md`

1. **Target Issue:**

   - ALWAYS attach to the issue specified by `--issue N` parameter
   - This is the spec being audited, so it needs the audit results

1. **Comment Format:**

   ```
   AI: <AgentName> <ModelID> 📝 Spec Audit: <issue-number>

   ## Summary
   - Issues Found: N
   - Issues Fixed: M
   - Issues Skipped: K

   <full audit log content>
   ```

1. **Why This Matters:**

   - Temp files (`./tmp/`) are NOT preserved between sessions
   - Fresh-start agents have no memory of previous sessions
   - The spec issue needs the audit results for context in future sessions
   - Ensures spec quality issues are visible to anyone reviewing the spec

**⚠️ CRITICAL: Always attach to the spec issue being audited, then delete temp file. No exceptions.**

## Mandatory Invocation (NO SKIPPING)

**AI agents creating new specs MUST invoke this auditor. NO EXCEPTIONS.**

When creating a GitHub Issue `[SPEC]`, the AI agent MUST:

1. Create the spec issue with all required content
1. Invoke `/skill spec-auditor --task generate-independent-spec --issue N` (FIRST - clean-room draft generation)
1. Invoke `/skill concern-separation-auditor --issue N` (SECOND - phase structure, auto-fix by default)
1. Invoke `/skill spec-auditor --task audit --issue N` (THIRD - content quality)
1. Invoke `/skill dev-architect --task review-spec` (FOURTH - architectural correctness)
1. Apply any fixes identified by auditors
1. Add `needs-approval` label
1. Post "ready for review" comment

**Skipping this auditor is a CRITICAL GUIDELINE VIOLATION.**

## Scope Boundaries

- Read-only analysis of GitHub Issue `[SPEC]` specs.
- Edits limited to the spec content via GitHub Issue updates.
- No changes to project source code, scripts, notebooks, or non-spec files.
- No new specs, expansions, or "improvements" beyond what the fix requires.
- Must use GitHub MCP tools for all issue operations.

## Coordination Points

### Integration with concern-separation-auditor and dev-architect

**ALL FOUR auditors are required. They check different things.**

| Auditor | Runs When | Checks |
|---------|----------|--------|
| `spec-auditor --task generate-independent-spec` | FIRST | Clean-room draft generation WITHOUT viewing live spec (pollution prevention) |
| `concern-separation-auditor` | SECOND | Phase structure, deployment independence, risk isolation, blast radius, phase names, BOILERPLATE-TITLE |
| `spec-auditor --task audit` | THIRD | Fresh-start context, completeness, content quality, LLM implementability |
| `dev-architect --task review-spec` | FOURTH | Architectural correctness, compliance, interdependencies, ordering |

**Order matters:** spec-auditor draft generation runs first to prevent pollution, then concern-separation-auditor fixes structural issues, then spec-auditor audit checks content quality, then dev-architect reviews architectural correctness.

### Integration with Approval Gate

- **Approval Gate (`010-approval-gate.md`)**: Before approving implementation, both auditors must have been run.
- **Critical Rules (`000-critical-rules.md`)**: References auditor skills for enforcement.
- **Planning Guidelines (`140-planning-spec-creation.md`)**: Defines the structure requirements enforced by these auditors.

### Enforcement Flow

1. User creates a [SPEC] issue.
1. spec-auditor generates independent draft WITHOUT viewing live spec (pollution prevention).
1. concern-separation-auditor runs (phase structure fixes).
1. spec-auditor audit runs (content quality fixes).
1. dev-architect runs (architectural correctness review).
1. After all FOUR auditors pass → Add `needs-approval` label.
1. After approval → Implementation begins.

## Example Session

```
User: /skill spec-auditor --issue 258

AI: <AgentName> (<ModelID>) 🤖 Auditing Issue #258 for content quality...

Issue Location: Problem Statement section
Problem class: FRESH-START-VIOLATION
Explanation: Spec references "as discussed above" and "see previous comment" without restating the context inline. LLM agents with no memory context cannot follow these references.
Proposed minimal fix: Replace all vague references with explicit inline context. Add "This means..." explanations where needed.
Required remediation indicators: Problem Statement section - replace "As discussed above" with explicit context; add "This means..." clarification paragraph.
Verification signal: changed — fixed fresh-start violation

[User responds: fix]

AI: Applying fix...

AI: <AgentName> (<ModelID>) 📝 Spec Update: Fixed fresh-start context violation

- Changed: Replaced "as discussed above" with explicit inline context in Problem Statement
- Reason: LLM agents cannot follow references to previous context
- Standard: docs/specs/how-to-write-good-spec-ai-agents.md - Fresh-Start Context Requirements

GitHub Comment: https://github.com/<owner>/<repo>/issues/258#issuecomment-xxxxx

Moving to next issue...

Issue Location: Success Criteria section
Problem class: VERIFICATION-GAP
...
```
