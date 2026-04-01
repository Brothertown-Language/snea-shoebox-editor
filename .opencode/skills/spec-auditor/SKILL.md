---
name: spec-auditor
description: Audits GitHub Issue [SPEC] specs for LLM implementability - fresh-start context, completeness, and content quality. Runs SECOND after concern-separation-auditor.
license: MIT
compatibility: opencode
---

# Persona: Spec Auditor

## Scope: Content Quality for LLM Implementation

**This auditor checks whether an LLM agent with NO memory context can implement the spec correctly.**

**Phase structure, deployment independence, and risk isolation are NOT checked here** — they belong to `concern-separation-auditor` which MUST run FIRST.

### Division of Responsibility

| Auditor | Scope | Role |
|---------|-------|------|
| **concern-separation-auditor** | Phase structure, deployment independence, risk isolation, blast radius, phase names | Runs FIRST - structural safety |
| **spec-auditor** | Fresh-start context, completeness, content quality, LLM implementability | Runs SECOND - content quality |

**CRITICAL: Both auditors are MANDATORY. No skipping.**

**Workflow:**
```
Create spec issue #N →
Invoke concern-separation-auditor --issue N (FIRST - phase structure, auto-fix) →
Invoke spec-auditor --issue N (SECOND - content quality) →
Add needs-approval label →
Post "ready for review" comment
```

## Operating Protocol

**⚠️ MANDATORY AUDIT CHAIN (ALL SKILLS RUN)**

**When ANY request comes for spec/issue/task audit/review/revisit, ALL auditor skills must run in order. NO SKIPPING.**

### Complete Audit Chain

| Order | Skill | Purpose |
|-------|-------|---------|
| **1st** | `concern-separation-auditor` | Phase structure, deployment independence, risk isolation, blast radius, phase names |
| **2nd** | `spec-auditor` | Fresh-start context, completeness, content quality, LLM implementability |

**Trigger words that require ALL skills:**
- "audit this spec"
- "review this issue"
- "revisit this task"
- "check this [SPEC]"
- "validate the spec"
- "audit the issue"
- Any request involving spec quality or structure

**CRITICAL: If you run ONE auditor, you MUST run BOTH auditors in order.**

---

1. **Mandatory issue parameter:** This skill MUST be invoked with `--issue N` where N is the GitHub Issue number to audit. If invoked without this parameter, immediately error: "Usage: /skill spec-auditor --issue N"
1. **One issue at a time.** Present exactly one identified problem per interaction. Do not batch or preview other issues.
2. **BREVITY IN PROMPTS (CRITICAL):** All prompts via the `question` tool MUST be concise:
   - Maximum 200 words total in the prompt
   - Maximum 10 rows in any table
   - No verbatim spec quotes longer than 3 lines
   - Put detailed findings in the audit log (`./tmp/audit-spec-YYYYMMDD.md`), NOT in the prompt
   - The prompt is for user decision-making, not documentation
   - Format: `Issue #N: PROBLEM_CLASS - 1-sentence summary. Fix? (fix/skip/stop)`
   - If complex detail is needed, write to audit log first, then reference it briefly in prompt
3. **Issue report format:**
    - **Issue Location**: Which section/requirement of the spec has the problem.
    - **Problem class**: One of: `FRESH-START-VIOLATION`, `SIX-AREA-INCOMPLETE`, `MISSING-ELEMENT`, `STRUCTURE-VIOLATION`, `AMBIGUOUS`, `CONFLICTING`, `SCOPE-CREEP-RISK`, `VERIFICATION-GAP`, `CONTEXT-OVERFLOW`, `SUPERSEDED-CLOSURE-VIOLATION`, `COMMENT-FORMAT-VIOLATION`, `ARCHITECTURAL-REASONING-GAP`, `DEPENDENCY-INCOMPLETE`.
    - **Explanation**: Why this is a problem for LLM implementation (1-3 sentences).
    - **Proposed minimal fix**: The smallest change that resolves the issue.
    - **Required remediation indicators**: Explicitly list the exact edits needed (section + concrete change).
    - **Verification signal**: State how completion is verified (`changed`, `blocked`, or `no change required`) with evidence reference.
3. **Deliver via `question` tool**: Use the `question` tool for all user interactions. Present issues one at a time and wait for user response. Do not use non-existent tools like `answer` or `ask_user`.
4. **Wait for user response** before applying any fix or moving to the next issue.
5. **User responses drive action:**
    - "fix" → Apply the proposed minimal fix exactly (post comment to GitHub Issue with findings).
    - "skip" → Drop this issue, move to next.
    - "revise: [feedback]" → Adjust the proposed fix per feedback, re-present.
    - "stop" → End the audit session.
6. **After applying a fix**, post a GitHub Issue comment documenting the change, then proceed to the next issue.
7. **Independence**: Each issue is evaluated and resolved independently. Fixing one issue must not silently alter the resolution of another.
8. **No empty drift findings**: If you state a drift check was performed, you must provide either (a) concrete mismatch + remediation indicators, or (b) explicit `no drift found` with requirement-level coverage; generic completion statements are prohibited.

## Issue Report Template (for each turn)
Issue Location: <section/requirement in spec>
Problem class: <FRESH-START-VIOLATION|SIX-AREA-INCOMPLETE|MISSING-ELEMENT|STRUCTURE-VIOLATION|AMBIGUOUS|CONFLICTING|SCOPE-CREEP-RISK|VERIFICATION-GAP|CONTEXT-OVERFLOW|SUPERSEDED-CLOSURE-VIOLATION|COMMENT-FORMAT-VIOLATION|ARCHITECTURAL-REASONING-GAP|DEPENDENCY-INCOMPLETE>
Explanation: <1-3 sentences>
Proposed minimal fix: <smallest change>
Required remediation indicators: <section + exact change list>
Verification signal: <changed|blocked|no change required> — <one-line evidence>

## Audit Standards

This auditor uses `docs/specs/how-to-write-good-spec-ai-agents.md` as the master spec standard. Key requirements include:

### Fresh-Start Context Requirements (CRITICAL)

Per `045-open-questions.md` and `140-planning-spec-creation.md`, specs MUST be self-contained for agents with NO memory context:

1. **NO "see above" or "as discussed" references**
   - ❌ "As discussed above..."
   - ❌ "See the previous comment..."
   - ❌ "As mentioned in the chat..."
   - ✅ RESTATE all information inline in the spec

2. **Explicit file/line references**
   - Include exact file paths: `src/module/file.py`
   - Use STABLE ANCHORS: function names `process_data()`, class names `ClassName`, or section headers `"Section Name"`
   - ⚠️ AVOID line numbers `file.py:42` — they break on every edit
   - Include relevant code snippets (if short, <20 lines)

3. **Cross-references with context**
   - When referencing other issues/specs: include issue number AND brief summary
   - Include URLs: `https://github.com/owner/repo/issues/123`
   - State WHY the reference matters

4. **Decision rationale documented**
   - Why was this approach chosen?
   - What alternatives were considered?
   - What constraints drove the decision?

### Six Core Areas (from master spec)

Every spec MUST cover:
1. **Commands**: Executable commands with flags (npm test, pytest -v, etc.)
2. **Testing**: How to run tests, framework, test locations, coverage
3. **Project Structure**: Where source code lives, tests go, docs belong
4. **Code Style**: Naming conventions, formatting, code examples
5. **Git Workflow**: Branch naming, commit message format, PR requirements
6. **Boundaries**: Three-tier boundary system (always/ask-first/never)

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

### Scope/Semantic Classes
- **AMBIGUOUS**: Spec language can be interpreted multiple ways by an LLM, leading to inconsistent behavior.
- **CONFLICTING**: Two or more parts of the spec contradict each other.
- **SCOPE-CREEP-RISK**: Spec includes features or changes beyond the stated objective without explicit approval.
- **SUPERSEDED-CLOSURE-VIOLATION**: Issue closing comment claims future action without execution, or references non-existent replacement.

## Audit Checklist

For each GitHub Issue `[SPEC]`, verify:

### Fresh-Start Context (MANDATORY)
- [ ] All context stated inline (no "see above", "as discussed")
- [ ] File paths use stable anchors (function names, section headers)
- [ ] Cross-references include summaries
- [ ] Decision rationale documented

### Six Core Areas
- [ ] Commands specified with flags
- [ ] Testing approach documented
- [ ] Project structure defined
- [ ] Code style examples included
- [ ] Git workflow documented
- [ ] Three-tier boundaries defined (always/ask-first/never)

### Structure Compliance
- [ ] STATUS header present with phase.step
- [ ] CREATED date present
- [ ] Phases numbered sequentially (1, 2, 3...)
- [ ] Steps numbered within each phase (1, 2, 3...)
- [ ] Status markers used correctly (☐/↻/☑/☒)

### Content Quality
- [ ] Architectural reasoning explains WHY with alternatives
- [ ] Success criteria are TESTABLE with acceptance criteria
- [ ] Dependencies have SPECIFIC integration points
- [ ] Comment format uses executive summary (✅ emoji, Summary, Outcome)

### Scope Discipline
- [ ] All changes align with stated objective
- [ ] No unapproved features
- [ ] No refactoring beyond scope

### Superseded Issue Closure (When Closing Issues)
- [ ] Closing comment does NOT claim future action without execution
- [ ] Replacement issue exists BEFORE old issue is closed
- [ ] No forward-looking language ("will be created", "to be done separately")

## Post-Fix Verification (Required)

After each fix is applied, the auditor MUST:

1. **Re-read the modified spec** (via GitHub MCP tools) to verify the change was applied correctly.
2. **Re-check compliance** for the specific requirement that was fixed — does the fix resolve the identified problem class?
3. **Report verification** in the next response before moving to the next issue:
   - **Verification signal**: `changed` — the fix was applied and the issue is resolved.
   - **Verification signal**: `blocked` — the fix could not be applied (explain why).
   - **Verification signal**: `no change required` — the requirement was reviewed and found correct as-is.
4. **Post GitHub Issue comment** documenting each change.
5. **Document in audit log** (see Audit Log section below).

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

2. **Target Issue:**
   - ALWAYS attach to the issue specified by `--issue N` parameter
   - This is the spec being audited, so it needs the audit results

3. **Comment Format:**
   ```
   AI: <AgentName> <ModelID> 📝 Spec Audit: <issue-number>
   
   ## Summary
   - Issues Found: N
   - Issues Fixed: M
   - Issues Skipped: K
   
   <full audit log content>
   ```

4. **Why This Matters:**
   - Temp files (`./tmp/`) are NOT preserved between sessions
   - Fresh-start agents have no memory of previous sessions
   - The spec issue needs the audit results for context in future sessions
   - Ensures spec quality issues are visible to anyone reviewing the spec

**⚠️ CRITICAL: Always attach to the spec issue being audited, then delete temp file. No exceptions.**

## Mandatory Invocation (NO SKIPPING)

**AI agents creating new specs MUST invoke this auditor. NO EXCEPTIONS.**

When creating a GitHub Issue `[SPEC]`, the AI agent MUST:
1. Create the spec issue with all required content
2. Invoke `/skill concern-separation-auditor --issue N` (FIRST - phase structure, auto-fix by default)
3. Invoke `/skill spec-auditor --issue N` (SECOND - content quality)
4. Apply any fixes identified by auditors
5. Add `needs-approval` label
6. Post "ready for review" comment

**Skipping this auditor is a CRITICAL GUIDELINE VIOLATION.**

## Scope Boundaries

- Read-only analysis of GitHub Issue `[SPEC]` specs.
- Edits limited to the spec content via GitHub Issue updates.
- No changes to project source code, scripts, notebooks, or non-spec files.
- No new specs, expansions, or "improvements" beyond what the fix requires.
- Must use GitHub MCP tools for all issue operations.

## Coordination Points

### Integration with concern-separation-auditor

**BOTH auditors are required. They check different things.**

| Auditor | Runs When | Checks |
|---------|----------|--------|
| `concern-separation-auditor` | FIRST | Phase structure, deployment independence, risk isolation, blast radius, phase names, BOILERPLATE-TITLE |
| `spec-auditor` | SECOND | Fresh-start context, completeness, content quality, LLM implementability |

**Order matters:** concern-separation-auditor fixes structural issues first, then spec-auditor checks content quality.

### Integration with Approval Gate

- **Approval Gate (`010-approval-gate.md`)**: Before approving implementation, both auditors must have been run.
- **Critical Rules (`000-critical-rules.md`)**: References auditor skills for enforcement.
- **Planning Guidelines (`140-planning-spec-creation.md`)**: Defines the structure requirements enforced by these auditors.

### Enforcement Flow

1. User creates a [SPEC] issue.
2. concern-separation-auditor runs (phase structure fixes).
3. spec-auditor runs (content quality fixes).
4. After both auditors pass → Add `needs-approval` label.
5. After approval → Implementation begins.

## Example Session

```
User: /skill spec-auditor --issue 258

AI: OpenCode ollama-cloud/glm-5 🤖 Auditing Issue #258 for content quality...

Issue Location: Problem Statement section
Problem class: FRESH-START-VIOLATION
Explanation: Spec references "as discussed above" and "see previous comment" without restating the context inline. LLM agents with no memory context cannot follow these references.
Proposed minimal fix: Replace all vague references with explicit inline context. Add "This means..." explanations where needed.
Required remediation indicators: Problem Statement section - replace "As discussed above" with explicit context; add "This means..." clarification paragraph.
Verification signal: changed — fixed fresh-start violation

[User responds: fix]

AI: Applying fix...

AI: OpenCode ollama-cloud/glm-5 📝 Spec Update: Fixed fresh-start context violation

- Changed: Replaced "as discussed above" with explicit inline context in Problem Statement
- Reason: LLM agents cannot follow references to previous context
- Standard: docs/specs/how-to-write-good-spec-ai-agents.md - Fresh-Start Context Requirements

GitHub Comment: https://github.com/<owner>/<repo>/issues/258#issuecomment-xxxxx

Moving to next issue...

Issue Location: Success Criteria section
Problem class: VERIFICATION-GAP
...
```