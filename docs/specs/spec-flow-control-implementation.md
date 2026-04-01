# Implementing Spec Flow Control in AI Agent Guidelines

## Purpose

This document explains how to integrate the spec flow control system (`spec-flow-control.md`) into your AI agent's guidelines.

**Important:** This is permanent reference documentation for AI agent workflow. It is NOT a plan. Actual spec files are created in `plans/` directory.

---

## Directory Structure

| Location | Purpose |
|----------|---------|
| `docs/specs/*.md` | Permanent reference docs (this file, how-to guides) |
| `plans/` | Actual spec files created during work |
| `plans/completed/` | Approved and finished specs |
| `plans/` | Actual spec files created during work |
| `plans/completed/` | Approved and finished specs |

---

## Critical Understanding

### Two Workflow Stages

**Stage 1: Before Spec Creation (Auto-Completed)**
- Investigation phases: research, analysis, exploration
- Planning phases: design, architecture, breakdown
- These are DONE before the spec is submitted
- NOT included in the final spec

**Stage 2: In the Spec (Requires Approval)**
- Implementation phases: build, code, integrate
- Verification phases: test, review, validate
- Completion phases: ship, deploy, release
- These appear in the spec with numbered phases and numbered steps

### Common Mistake

**WRONG:** Including investigation/planning phases in the spec

```markdown
## Phase 1: Investigation (auto-approved)
- Research auth patterns
- Analyze current system

## Phase 2: Planning (auto-approved)
- Design solution
- Plan implementation

## Phase 3: Implementation (requires approval)
...
```

**RIGHT:** Spec starts with implementation (investigation/planning already done)

```markdown
## Phase 1: Implementation (requires approval)

### Steps
1. ☐ Add OAuth2 client configuration
2. ☐ Implement token refresh logic
3. ☐ Update authentication middleware
```

---

## Numbering System

### Phases Numbered Sequentially

Phases are numbered 1, 2, 3... (not named):

```
Phase 1, Phase 2, Phase 3...
```

### Steps Numbered Within Phase

Steps use decimal notation: phase.step

```
Phase 1: Implementation
  - Step 1
  - Step 2
  - Step 3

Phase 2: Testing
  - Step 1
  - Step 2
```

---

## Required Elements in Specs

Every spec must have:

1. **STATUS field** with phase.step format: `1.2` (phase 1, step 2)
2. **Numbered phases**: Phase 1, Phase 2, Phase 3
3. **Numbered steps**: 1, 2, 3 within each phase
4. **Status markers with icons**: `☐`, `↻`, `☑`, `☒`
5. **Approval log table**

---

## STATUS Format

| Format | Meaning |
|--------|---------|
| `1` | Phase 1, no specific step |
| `1.2` | Phase 1, step 2 |
| `2.1-3` | Phase 2, steps 1-3 |
| `completed` | All done |

---

## Status Markers (Visual Icons)

| Marker | Meaning | When to Use |
|--------|---------|-------------|
| `☐` | Not started | Task not begun |
| `↻` | In progress | Currently working (MARK DURING WORK) |
| `☑` | Complete | Task done |
| `☒` | Blocked | Issue found |

**Critical:** Update to `↻` during implementation, not just after completion.

The circling arrow (`↻`) conveys "it's in motion" - actively working.

The circling arrow (`↻`) conveys "it's in motion" - actively working.

---

## Phase Types in Specs

Only these phase types appear in specs:

| Type | Approval | Keywords |
|------|----------|----------|
| Implementation | Requires approval | build, implement, code, develop, integrate, create, write, fix, add, update, remove |
| Verification | Auto-progress | test, verify, review, validate, check, ensure, confirm |
| Completion | Auto-archive | complete, done, finish, ship, deploy, release |

---

## Creating Specs

### What to Include

1. Implementation details from planning phase
2. Verification steps
3. Review/approval steps

### What NOT to Include

1. Investigation phases (already done)
2. Planning phases (already done)
3. Research notes (that was investigation)
4. Architecture decisions (that was planning)

---

## Template

```markdown
# Spec: [Title]

STATUS: 1.1
CREATED: YYYY-MM-DD

---

## Phase 1: Implementation (requires approval)

### Steps
1. ☐ [first implementation task]
2. ☐ [second implementation task]
3. ☐ [third implementation task]

### Content
[Implementation details from planning phase]

---

## Phase 2: Testing (auto-progress)

### Steps
1. ☐ [first test task]
2. ☐ [second test task]

---

## Phase 3: Review (requires approval)

### Steps
1. ☐ [first review task]
2. ☐ [second review task]

---

## Approval Log
| Date | Phase | Command | Notes |
|------|-------|---------|-------|
```

---

## Revision = Replanning

When revising:

1. Re-examine all phases and steps
2. Add/remove/modify steps as needed
3. Cascade changes to downstream phases
4. Renumber steps sequentially
5. No code changes during revision

**Example:**
```
STATUS: 1.2
Command: "revise: discovered OAuth2 requires PKCE"

New steps:
1. ☐ Add OAuth2 client configuration
2. ☐ Implement token refresh logic
3. ☐ Add PKCE challenge generation  <- NEW
4. ☐ Update authentication middleware  <- RENUMBERED from 1.3
```

---

## Gotchas

### 1. Including Investigation/Planning in Spec

**Wrong:** Creating a spec with investigation and planning phases

**Right:** Spec starts AFTER investigation and planning are complete.

### 2. Non-Numbered Phases

**Wrong:** "Phase: Authentication" "Phase: Testing"

**Right:** "Phase 1: Implementation" "Phase 2: Testing"

### 3. Wrong Step Numbering

**Wrong:** Phase.step numbering like 1.1, 1.2

```
### Steps
- ☐ 1.1. Add OAuth2
- ☐ 1.2. Configure token
```

**Right:** Step numbers within phase: 1, 2, 3

```
### Steps
1. ☐ Add OAuth2
2. ☐ Configure token
```

### 4. Status Marker Updates After Completion

**Wrong:** Only updating to `☑` after entire phase done

**Right:** Marking `↻` when starting task, `☑` when completing, during implementation

### 5. Using [ ]/[x] Instead of Icons

**Wrong:** `1. [ ] Task` or `1. [x] Task`

**Right:** `1. ☐ Task` or `1. ☑ Task`

Icons are more scannable and convey meaning at a glance.

---

## Integration Checklist

- [ ] Number phases: 1, 2, 3...
- [ ] Number steps within phase: 1, 2, 3
- [ ] STATUS uses phase.step format: `1.2`
- [ ] Investigation/planning NOT in spec (already done)
- [ ] Only implementation+ phases in spec
- [ ] Status markers use icons: `☐`, `↻`, `☑`, `☒`
- [ ] Status `↻` marked during implementation
- [ ] Revision correctly renumbers steps

---

## Testing Your Integration

Create a spec and verify:

1. ✓ Phases are numbered (1, 2, 3...)
2. ✓ Steps are numbered (1, 2, 3 within each phase)
3. ✓ No investigation/planning phases present
4. ✓ STATUS uses `phase.step` format
5. ✓ Icons used (`☐`, `↻`, `☑`, `☒`) not `[ ]`/`[x]`
6. ✓ `↻` can be marked during work
7. ✓ Revision correctly renumbers steps

---

## Reference Files

- Full specification: `docs/specs/spec-flow-control.md`
- Master spec guidance: `docs/specs/how-to-write-good-spec-ai-agents.md`
- Guideline example: `.opencode/guidelines/140-planning-spec-creation.md`