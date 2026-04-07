# Git Protocol: Commit Workflow

## 1. Commit Policy (User-Initiated Only)

### 🚫 NEVER DO

- **NEVER run `git restore`, `git checkout`, `git reset`, `git clean`, or any other git command that discards or modifies working tree state.**
- **NEVER discard uncommitted changes** — even if they appear to be formatting-only, unintended, or erroneous. Analysis commands are read-only.
- **NEVER commit or merge without direct instruction.** Commits and merges may ONLY be initiated by the developer as a direct instruction to the AI agent. Autonomously committing or merging is FORBIDDEN.
- **NEVER create a PR without direct instruction.** PRs require explicit developer request — the agent does NOT automatically create PRs after completing implementation. See `113-git-pr-workflow.md`.
- Agent MUST NOT create commit messages or scripts proactively (without user request).
- When asked to "prepare a commit" — see Section 2 for the mandatory script-based workflow.

### STOP ASKING FOR COMMITS AND PRS

The developer will say "commit" or "create a PR" when they want git operations. Until then, do nothing—no questions, no prompts:

1. **After completing implementation**: Report completion concisely, then STOP and wait silently
1. **Do NOT ask**: "Commit?", "Ready to commit?", "Should I commit?", "Ready for a PR?", "Create a PR?", "Push and PR?"
1. **Do NOT automatically create PRs**: PR creation requires the same explicit instruction as commits

### ✅ ALWAYS DO

- **Include co-author trailers for both AI and human collaborator.** Every implementation commit MUST include TWO trailers:
  - AI author: Use the AI's actual identity dynamically (the AI knows its own name)
  - Human collaborator: Use session-cached values from `000-session-init.md` "MANDATORY FIRST STEP" (`DEV_NAME`, `DEV_EMAIL`)
- Re-run discovery (`git status`, `git diff`) before any commit workflow.
- If `pyproject.toml` changed, include `uv.lock`.

### Co-Author Trailer Workflow

**⚠️ CRITICAL: AI Identity is DYNAMIC — NEVER copy the AI name from examples!**

The AI must use its **own identity**, not the example name. Examples show placeholders like `OpenCode` — the actual AI must substitute its own name/email.

**Step 1: Determine AI identity dynamically:**

| Identity Component | How to Detect | FORBIDDEN |
|-------------------|---------------|-----------|
| `<AgentName>` | Agent's actual name at runtime | Copying "OpenCode" or "AI Assistant" from examples |
| `<ModelID>` | Backing model ID at runtime | Copying "ollama-cloud/*" from examples |
| `<ai-email>` | Agent's noreply email | Using project domain email |

- The AI uses its **own actual identity** (the AI knows its own name and email)
- **DO NOT use generic placeholders like "AI"** — use the actual AI agent name (e.g., "OpenCode Desktop", "OpenCode")
- **Email format**: Use a noreply address associated with the AI service (e.g., `noreply@opencode.ai`, `noreply@anthropic.com`)
- **NEVER use the project domain** (e.g., `ai@<project-domain>.com` is WRONG — those belong to the human collaborators)
- **MODEL INFO REQUIRED**: The AI MUST include the backing model name and size/provider in the co-author trailer:
  - Format: `<AgentName> (<ModelID>) <ai-email>`
  - **Example:** `Co-authored-by: <AgentName> (<ModelID>) <ai-email>`

**When Identity Unknown:**
- STOP and ask user for clarification
- DO NOT use example values as defaults
- DO NOT guess or invent identity values

**Example Values in Guidelines are ILLUSTRATIVE:**
- `<AgentName> (<ModelID>)` → Example only
- `AI Assistant (model-id)` → Placeholder only
- **DETECT YOUR OWN IDENTITY** at runtime

**Step 2: Use cached human identity from session start:**

- Human collaborator values are cached at session start via `000-session-init.md` "MANDATORY FIRST STEP"
- `DEV_NAME`: Human's name (or `$USER` fallback)
- `DEV_EMAIL`: Human's email (or `$USER@$HOSTNAME` fallback)
- **Do NOT re-run `git config`** — use stored session values

**Step 3: Include BOTH trailers (MANDATORY):**

```bash
git commit -m "message" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"
```

______________________________________________________________________

## 2. Preparing Commits (Script-Based Workflow)

When asked to "prepare a commit" (or similar READ-ONLY phrase):

**Mandatory Steps:**

1. Run read-only commands: `git status`, `git diff`, `git diff --cached`, `git log`
1. Summarize the changes (grouped logically if multiple files)
1. **Create a shell script in `./tmp/`** containing the `git add` and `git commit` commands
1. **STOP** — do NOT run the script, do NOT run `git add` or `git commit`
1. Report the script path and proposed commit message for the user to review and execute

______________________________________________________________________

## 3. Reading Historical Content

### ✅ ALWAYS DO

- To inspect a file at a historical commit, use `git show <ref>:<path> > ./tmp/historical_file.ext`.
- Process the saved file with the appropriate `ai_bin/` or IDE tool.

### 🚫 NEVER DO

- Using `python3`, `python -c`, `json.tool`, `grep`, or `sed` to process `git show` output is a critical violation.

______________________________________________________________________

## 4. Lockfile Policy

- This repository is an application/CI repo — commit `uv.lock`.

______________________________________________________________________

## 5. WIP Commit Before HALT (MANDATORY)

**CRITICAL: Work-in-progress commits MUST be made before ANY HALT to prevent data loss.**

### Why WIP Commits Are Required

When implementation halts (for ANY reason), uncommitted changes are at risk:

- Session crashes
- Context window exhaustion
- Developer needs to switch branches
- Machine restarts
- Awaiting clarification/approval

WIP commits preserve work in progress in recoverable git history.

### When to Commit WIP

| Scenario | Commit Type | Message Format |
|----------|-------------|----------------|
| Task complete | Full commit | `[Phase N] Task description` |
| Phase complete | Full commit | `[Phase N] Phase complete` |
| Mid-task HALT | WIP commit | `WIP: Phase N - description` |
| Awaiting clarification | WIP commit | `WIP: Phase N - awaiting clarification` |
| Error encountered | WIP commit | `WIP: Phase N - error: description` |
| Session ending | WIP commit | `WIP: Phase N - session end` |

### WIP Commit Workflow

**Before ANY HALT (awaiting approval, clarification, error, session end):**

```bash
# Step 1: Check for uncommitted changes
git status

# Step 2: If changes exist, commit WIP
git add -A
git commit -m "WIP: Phase N - <brief description>" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"

# Step 3: Verify commit was created
git log -1 --oneline

# Step 4: Report WIP commit made
```

### WIP Commit Characteristics

| Characteristic | Description |
|---------------|-------------|
| **Prefix** | Always starts with `WIP:` for easy identification |
| **Phase** | Includes phase number for context |
| **Description** | Brief description of what was being worked on |
| **Trailers** | Same co-author trailers as full commits |
| **Squashable** | Can be squashed or amended later with subsequent work |

### After WIP Commit

- **Continue work**: Next commit can amend or squash the WIP commit
- **Session resumes**: Rebase or continue from WIP commit
- **PR creation**: Squash WIP commits with final work before PR

### What Counts as HALT

| HALT Trigger | WIP Required? |
|-------------|--------------|
| Awaiting approval | ✅YES |
| Awaiting clarification | ✅ YES |
| Mid-task pause | ✅ YES |
| Error encountered | ✅ YES |
| Session ending | ✅ YES |
| Task complete | ❌ NO (use full commit) |
| Phase complete | ❌ NO (use full commit) |

______________________________________________________________________

## 5.5. Todo Lifecycle During Workflow Transitions (MANDATORY)

**Clear todos at these transition points:**

| Transition Point | Action |
|------------------|--------|
| Implementation → PR creation | Clear implementation todos (no todo needed for PR steps) |
| After PR creation | Clear PR workflow todos (waiting for human merge) |
| After cleanup | Clear all todos (workflow complete) |

**Why:** Each workflow phase has explicit steps in skills. Todo lists track implementation progress, not procedural steps.

### When to Clear Todos

**After authorization received (before implementation starts):**

If workflow was interrupted by clarification, revision, context switch, or error:

```python
todowrite(todos=[])
```

**Workflow interruptions include:**

- Developer conversation (clarification questions)
- Spec revision
- Context switch to different issue/task
- Error recovery
- Session boundary

**Edge cases:**

| Scenario | Action |
|----------|--------|
| No interruption (immediate auth) | Skip todo clearing (todos still valid) |
| Todo list already empty | Skip todo clearing (no-op) |
| Clarification question answered | Clear todos (workflow restarted) |
| Spec revised | Clear todos (scope changed) |

**Before PR creation workflow:**

```python
# See git-workflow skill pr-creation task
todowrite(todos=[])
```

**After cleanup workflow:**

```python
# See git-workflow skill cleanup task
todowrite(todos=[])
```

### Why Todo Clearing Matters

- Implementation todos track progress within a workflow
- PR creation has explicit procedural steps - no todo needed
- Stale todos cause confusion about "X of Y complete"
- Clean state on completion prevents confusion in next session

______________________________________________________________________

______________________________________________________________________

## 6. Grouped-Step Commit Strategy

When implementing specs with multiple steps, create commits per logical group (not per step).

### What Is a Commit Group?

A commit group is a cohesive set of related changes that:

- Implements one logical feature or fix
- Can be reviewed independently
- Makes sense as a standalone commit
- Could be reverted without breaking other work

### Examples of Commit Groups

| Scenario | Commit Strategy | Reasoning |
|----------|-----------------|-----------|
| Single file change | Single commit | Atomic change |
| Multiple files, same feature | Single commit | Cohesive change |
| Multiple concerns (DB + API) | Grouped commits | Independent review |
| Implementation + tests | Grouped commits (impl first, then tests) | Separation of concerns |
| Multi-phase spec with sub-phases | Grouped commits by phase | Review atomicity |

### Anti-Patterns (DO NOT)

- One commit per file (too granular)
- One commit per step of multi-step spec (too granular)
- All changes in one commit (too broad if multiple concerns)

### Grouped Commit Workflow

**Step 1: Identify Groups**

- Analyze implementation to determine logical groups
- Each group = one cohesive change
- Groups should be independently reviewable

**Step 2: Commit Each Group**

```bash
# Stage group changes
git add <files-for-this-group>

# Commit with descriptive message
git commit -m "[Phase N] <group description>"

# Post progress comment to issue
```

**Step 3: Progress Comments**
After EACH commit group, post to the issue:

```markdown
**Summary:**

<1-2 sentences describing the impact of this commit group.>

**Outcome:** <What changed for stakeholders>

**Commit Group:** <group name> (X of Y)

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

### When to Use Grouped vs Single

| Implementation Type | Commit Strategy |
|---------------------|-----------------|
| Single-concern, cohesive | Single commit |
| Multi-concern, separable | Grouped commits |
| Large phase with sub-phases | Grouped by sub-phase |
| Implementation + tests | Two commits (impl, then tests) |

---

## 7. Discrete Units and Concern-Based Phases

**Discrete units map to git commits at concern boundaries.**

### Discrete Unit Definition

A discrete unit is an atomic, concern-scoped change that:

- Modifies files related to ONE concern (layer, module, responsibility)
- Can be cherry-picked independently without breaking builds
- Can be reverted without leaving orphaned dependencies
- Maps to exactly ONE git commit

### Discrete Units vs. Commit Groups

| Concept | Scope | Mapping |
|---------|-------|---------|
| **Phase** | Entire concern boundary | Multiple commits (one per discrete unit) |
| **Discrete Unit** | Atomic change within phase | ONE git commit |
| **Commit Group** | Multiple discrete units (same concern) | Multiple commits (reviewed together) |

### Example: Authentication Feature

**Phase 1: Data Layer (Risk: LOW, Blast Radius: SMALL)**

```
Phase 1 contains 3 discrete units:

Step 1.1: Add user table schema        → Commit 1 (discrete unit)
Step 1.2: Create migration script      → Commit 2 (discrete unit)
Step 1.3: Add seed data for testing    → Commit 3 (discrete unit)

All 3 commits are in the SAME phase (same concern boundary).
```

**Phase 2: Business Logic (Risk: MEDIUM, Blast Radius: MEDIUM)**

```
Phase 2 depends on Phase 1 (interdependency).

Phase 2 contains 3 discrete units:

Step 2.1: Create AuthRepository class   → Commit 4 (discrete unit)
Step 2.2: Implement password hashing  → Commit 5 (discrete unit)
Step 2.3: Add session management        → Commit 6 (discrete unit)

All 3 commits are in the SAME phase (same concern boundary).
```

### WIP Commit Positioning

**WIP commits happen BETWEEN phases, NOT within phases.**

```
✅ CORRECT: WIP commits at phase boundaries

Phase 1 commits:
  Step 1.1 → Commit 1
  Step 1.2 → Commit 2
  Step 1.3 → Commit 3
  [Phase 1 complete]

WIP Commit (Phase 1 → Phase 2 boundary)  ← WIP HERE

Phase 2 commits:
  Step 2.1 → Commit 4
  Step 2.2 → Commit 5
  Step 2.3 → Commit 6
  [Phase 2 complete]
```

```
❌ WRONG: WIP commits within phases

Phase 1 commits:
  Step 1.1 → Commit 1
  WIP Commit (mid-Phase 1)  ← WRONG: Not at concern boundary
  Step 1.2 → Commit 2
  Step 1.3 → Commit 3
```

### Cherry-Pick Workflow for Discrete Units

**Each discrete unit can be cherry-picked independently:**

```bash
# Cherry-pick a single discrete unit from Phase 1
git cherry-pick <commit-1>  # User table schema

# Cherry-pick entire Phase 1
git cherry-pick <commit-1>..<commit-3>  # All of Phase 1

# Cherry-pick by concern
git cherry-pick <phase-1-commits>  # All data layer changes
```

**With interdependency ordering, cherry-picks are safe:**
- Phase 1 commits have NO dependencies (can be cherry-picked first)
- Phase 2 commits depend on Phase 1 (cherry-pick after Phase 1)
- Phase 3 commits depend on Phase 2 (cherry-pick after Phase 2)

### Revert Workflow for Single-Phase Changes

**Reverting by phase (not by commit):**

```bash
# Revert entire Phase 2
git revert <phase-2-first-commit>..<phase-2-last-commit>

# Revert single discrete unit
git revert <commit-4>  # Revert AuthRepository class only

# Revert and preserve history
git revert --no-commit <phase-2-commits>  # Stage for review
```

**Phase-level reverts preserve interdependency ordering:**
- Reverting Phase 2 doesn't break Phase 1 (Phase 1 has no dependencies)
- Reverting Phase 2 doesn't break Phase 3 (Phase 3 doesn't exist yet)

### Interactive Rebase for Rearranging Phases

**Phases can be reordered within dependency constraints:**

```bash
# Interactive rebase to rearrange phases
git rebase -i origin/dev

# Can swap Phase 2 and Phase 3 if they don't depend on each other
# CANNOT swap Phase 1 and Phase 3 if Phase 3 depends on Phase 1
```

**Dependency check before reordering:**
1. Build dependency graph for all phases
2. Verify no circular dependencies
3. Reorder only if dependencies are satisfied

### Examples of Discrete Unit Breakdown

**Example 1: Simple Feature (2 Phases)**

```
Phase 1: Config Update (Risk: LOW, Blast Radius: SMALL)
  └── Step 1.1: Update database connection string  ← 1 discrete unit = 1 commit

Phase 2: Documentation (Risk: LOW, Blast Radius: SMALL)
  └── Step 2.1: Update README with new config  ← 1 discrete unit = 1 commit

Total: 2 phases, 2 discrete units, 2 commits
```

**Example 2: Complex Feature (8 Phases)**

```
Phase 1: Database Schema (Risk: LOW, Blast Radius: SMALL)
  ├── Step 1.1: Create migration file           ← Discrete unit
  ├── Step 1.2: Add user table                  ← Discrete unit
  ├── Step 1.3: Add indexes                     ← Discrete unit
  ├── Step 1.4: Add foreign keys                ← Discrete unit
  └── Step 1.5: Update schema version           ← Discrete unit
  Total: 5 discrete units = 5 commits

Phase 2: Data Layer Tests (Risk: LOW, Blast Radius: SMALL)
  └── Step 2.1: Add tests for user table        ← 1 discrete unit = 1 commit

Phase 3: Business Logic (Risk: MEDIUM, Blast Radius: MEDIUM)
  ├── Step 3.1: Create AuthRepository class      ← Discrete unit
  ├── Step 3.2: Implement password hashing       ← Discrete unit
  └── Step 3.3: Add session management           ← Discrete unit
  Total: 3 discrete units = 3 commits

... (remaining phases follow same pattern)

Total: 8 phases, ~15 discrete units, ~15 commits
```

**Example 3: Refactoring (3 Phases)**

```
Phase 1: Extract Interfaces (Risk: MEDIUM, Blast Radius: MEDIUM)
  ├── Step 1.1: Create IUserRepository interface ← Discrete unit
  ├── Step 1.2: Extract method signatures         ← Discrete unit
  └── Step 1.3: Update existing implementations  ← Discrete unit
  Total: 3 discrete units = 3 commits

Phase 2: Integration Layer (Risk: MEDIUM, Blast Radius: MEDIUM)
  └── Step 2.1: Replace UserRepository usage ← 1 discrete unit = 1 commit

Phase 3: Remove Old Code (Risk: LOW, Blast Radius: SMALL)
  └── Step 3.1: Delete old UserRepository class ← 1 discrete unit = 1 commit

Total: 3 phases, 5 discrete units, 5 commits
```

______________________________________________________________________

*Source: Content migrated from `110-git-protocol.md`*
