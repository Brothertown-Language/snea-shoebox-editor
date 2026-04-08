# Sub-Issue Task Template

Use this template for individual implementation tasks that are children of a parent orchestrator issue.

---

## Template

```markdown
# Task: [Descriptive Title]

Parent: #NNN
Subtask: X.Y  # Must match STATUS in parent

---

## Purpose

[What this subtask accomplishes - 2-3 sentences]

---

## Entry Criteria

- [ ] Authorization received for this specific subtask
- [ ] STATUS in parent matches this subtask number
- [ ] Previous subtask completed (if applicable)

---

## Exit Criteria

- [ ] [What defines completion - testable criteria]
- [ ] [Each criterion should be independently verifiable]

---

## Procedure

1. ☐ [Step 1 - concrete action]
2. ☐ [Step 2 - concrete action]
3. ☐ [Step 3 - concrete action]
...

---

## Constraints

| Constraint | Details |
|------------|---------|
| [Constraint 1] | [Description] |
| [Constraint 2] | [Description] |

---

## Cross-References

- Parent: #NNN (Link to parent issue)
- Related: `[skill-name]` skill
- Related: `XXX-guideline-name.md`

---

## Context Required

- Guidelines: `.opencode/guidelines/XXX.md`
- Skills: `.opencode/skills/YYY/`
- Files: `path/to/relevant/files`

---

🤖 ✨ Created by <AgentName> (<ModelID>)
```

---

## Template Size

Sub-issues should be **~60-150 lines**:

- Purpose: 5-10 lines
- Entry/Exit criteria: 10-20 lines
- Procedure: 20-50 lines
- Constraints: 5-15 lines
- Cross-references: 5-15 lines
- Context: 10-30 lines

---

## Self-Contained Requirement

**Each sub-issue MUST be implementable WITHOUT reading other sub-issues.**

### ✅ REQUIRED

- All context in THIS sub-issue
- File paths with stable anchors (function names, section headers)
- Code snippets for short sections
- Decision rationale documented
- Success criteria testable

### ❌ PROHIBITED

- "See Phase 1 for context"
- "As described in the parent"
- "Continue from subtask X"
- "Refer to other sub-issue for details"

---

## Subtask Number Format

| Format | Meaning |
|--------|---------|
| `X.Y` | Phase X, Subtask Y |
| `1.1` | Phase 1, Subtask 1 (first task) |
| `1.2` | Phase 1, Subtask 2 (second task in phase 1) |
| `2.1` | Phase 2, Subtask 1 (first task in phase 2) |

**The subtask number MUST match STATUS in parent issue.**

---

## Title Format

### ✅ Required Format

```
[Task: #<parent-number>] <descriptive-title>
```

### ✅ Good Examples

```
[Task: #469] Refactor Tier 1 Skills with Sub-Task Architecture
[Task: #469] Design sub-issue orchestrator template
[Task: #469] Update AGENTS.md with sub-issue invocation guidance
```

### ❌ Bad Examples

```
[Task: #469] Phase 1 - Implementation      # Only type, no description
[Task: #469] Phase 2 - Testing              # Only type, no description
Task: Database schema                       # Missing parent reference
[Task] Create database schema               # Missing parent number
```

---

## Entry Criteria

**Before starting ANY work:**

| Criterion | How to Verify |
|-----------|---------------|
| Authorization received | User said "approved: X.Y" for this subtask |
| STATUS matches | Parent issue shows `STATUS: X.Y` |
| Previous completed | Previous subtask issue is CLOSED |

**If ANY criterion fails → HALT and report.**

---

## Exit Criteria

**Each criterion MUST be:**

1. **Testable** - Can be verified programmatically or manually
2. **Specific** - Clear pass/fail determination
3. **Complete** - No ambiguity about what "done" means

### ✅ Good Exit Criteria

```
- [ ] All Tier 1 skills refactored with tasks/ subdirectory
- [ ] Each skill has SKILL.md orchestrator + task files
- [ ] Context savings measured (target: 50%+ reduction)
- [ ] Backwards compatibility maintained
```

### ❌ Bad Exit Criteria

```
- [ ] Complete implementation
- [ ] Refactor skills
- [ ] Make it work
```

---

## Procedure

**Each step MUST be:**

1. **Concrete** - Specific action to take
2. **Verifiable** - Can confirm completion
3. **Atomic** - Single clear action

### ✅ Good Procedure Steps

```
1. ☐ Create `tasks/` directory structure for git-workflow skill
2. ☐ Refactor git-workflow SKILL.md to overview-only
3. ☐ Create task files: pre-work.md, implementation.md, cleanup.md
4. ☐ Test sub-task invocation with `/skill git-workflow --task pre-work`
5. ☐ Measure context savings for git-workflow skill
```

### ❌ Bad Procedure Steps

```
1. ☐ Refactor the skill
2. ☐ Make changes
3. ☐ Test everything
```

---

## Context Required Section

**List ALL files, guidelines, and skills needed to implement:**

```markdown
## Context Required

- Guidelines: `.opencode/guidelines/110-git-branch-first.md`
- Guidelines: `.opencode/guidelines/120-github-issue-first.md`
- Skills: `.opencode/skills/git-workflow/SKILL.md`
- Files: `.opencode/skills/git-workflow/tasks/*.md`
```

This ensures fresh-start agents have all references without searching.

---

## Integration Points

| Component | Purpose |
|-----------|---------|
| Parent issue | STATUS verification, subtask number matching |
| `approval-gate` skill | Verify authorization for THIS subtask |
| `git-workflow` skill | Create branch named for this subtask |
| `github-sub-issues` skill | Sub-issue linked to parent |

---

## Example

```markdown
# Task: GitHub Sub-Issue Sub-Task Architecture

Parent: #469
Subtask: 1.2

---

## Purpose

Design and implement the architecture for GitHub sub-issue sub-task tracking, ensuring parallel subtasks do NOT interfere with each other for edits and git repository management.

---

## Entry Criteria

- [ ] Tier 1 skills refactored (Phase 1 complete)
- [ ] Sub-task pattern validated (PR #471 merged)
- [ ] Authorization received for subtask 1.2

---

## Exit Criteria

- [ ] Parent issue orchestrator template defined
- [ ] Sub-issue task template defined
- [ ] AGENTS.md updated with `/issue --task` guidance
- [ ] Context savings measured for spec loading
- [ ] Architecture enforces single subtask execution at a time

---

## Procedure

1. ☐ Design parent issue orchestrator template with STATUS gate
2. ☐ Design sub-issue task template with subtask number
3. ☐ Update AGENTS.md with single-subtask enforcement rules
4. ☐ Create transformation guide for existing multi-task specs
5. ☐ Add STATUS verification to `approval-gate` skill
6. ☐ Test with existing multi-task specs (e.g., #469)
7. ☐ Measure context savings for spec loading
8. ☐ Document pattern in guidelines

---

## Constraints

| Constraint | Details |
|------------|---------|
| Backwards compatible | Existing spec format must still work |
| Self-contained | Sub-issue must have all needed context |
| Task table required | Parent issue must have task table linking sub-issues |
| Single subtask flow | Architecture MUST prevent parallel subtask execution |
| STATUS gate | Agent must check STATUS before implementing |

---

## Cross-References

- Parent: #469 (Skills: Sub-Task Architecture)
- Related: `git-workflow` skill (pre-work task)
- Related: `approval-gate` skill (verify-sub-issues task)
- Related: `120-github-issue-first.md` (issue management)

---

## Context Required

- Guidelines: `.opencode/guidelines/120-github-issue-first.md`
- Guidelines: `.opencode/guidelines/010-approval-gate.md`
- Skills: `.opencode/skills/github-sub-issues/SKILL.md`

---

🤖 ✨ Created by OpenCode Desktop (ollama-cloud/glm-5)
```

---

## Size Comparison

| Component | Parent Issue | Sub-Issue |
|-----------|-------------|-----------|
| Total lines | ~100 lines | ~60-150 lines |
| Purpose | ~50 lines | ~5-10 lines |
| Procedure | Task table only | ~20-50 lines |
| Context | ~30 lines | ~10-30 lines |
| Entry/Exit | ~10 lines | ~10-20 lines |

**Parent = Orchestrator (~100 lines)**  
**Sub-Issue = Implementation details (~60-150 lines)**