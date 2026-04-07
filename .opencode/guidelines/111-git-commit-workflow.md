# Git Protocol: Commit Workflow

## 1. Commit Policy (User-Initiated Only)

### 🚫 NEVER DO

- **NEVER run `git restore`, `git checkout`, `git reset`, `git clean`, or any other git command that discards or modifies working tree state.**
- **NEVER discard uncommitted changes** — even if they appear to be formatting-only, unintended, or erroneous. Analysis commands are read-only.
- **NEVER commit or merge without direct instruction.** Commits and merges may ONLY be initiated by the developer as a direct instruction to the AI agent. Autonomously committing or merging is FORBIDDEN.
- **NEVER create a PR without direct instruction.** PRs require explicit developer request — see `113-git-pr-workflow.md`.
- Agent MUST NOT create commit messages or scripts proactively (without user request).

### STOP ASKING FOR COMMITS AND PRS

The developer will say "commit" or "create a PR" when they want git operations. Until then, do nothing—no questions, no prompts:

1. **After completing implementation**: Report completion concisely, then STOP and wait silently
2. **Do NOT ask**: "Commit?", "Ready to commit?", "Should I commit?", "Ready for a PR?", "Create a PR?", "Push and PR?"
3. **Do NOT automatically create PRs**: PR creation requires the same explicit instruction as commits

### ✅ ALWAYS DO

- **Include co-author trailers for both AI and human collaborator.** Every implementation commit MUST include TWO trailers:
  - AI author: Use the AI's actual identity dynamically (the AI knows its own name)
  - Human collaborator: Use session-cached values from `000-session-init.md`
- Re-run discovery (`git status`, `git diff`) before any commit workflow
- If `pyproject.toml` changed, include `uv.lock`

### Co-Author Trailer Workflow

**⚠️ CRITICAL: AI Identity is DYNAMIC — NEVER copy the AI name from examples!**

| Identity Component | How to Detect | FORBIDDEN |
|-------------------|---------------|-----------|
| `<AgentName>` | Agent's actual name at runtime | Copying "OpenCode" or "AI Assistant" from examples |
| `<ModelID>` | Backing model ID at runtime | Copying "ollama-cloud/*" from examples |
| `<ai-email>` | Agent's noreply email | Using project domain email |

**When Identity Unknown:**
- STOP and ask user for clarification
- DO NOT use example values as defaults
- DO NOT guess or invent identity values

**Format:**
```bash
git commit -m "message" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"
```

---

## 2. Preparing Commits (Script-Based Workflow)

When asked to "prepare a commit" (or similar READ-ONLY phrase):

**Mandatory Steps:**

1. Run read-only commands: `git status`, `git diff`, `git diff --cached`, `git log`
2. Summarize the changes (grouped logically if multiple files)
3. **Create a shell script in `./tmp/`** containing the `git add` and `git commit` commands
4. **STOP** — do NOT run the script, do NOT run `git add` or `git commit`
5. Report the script path and proposed commit message for the user to review and execute

---

## 3. Reading Historical Content

### ✅ ALWAYS DO

- To inspect a file at a historical commit, use `git show <ref>:<path> > ./tmp/historical_file.ext`
- Process the saved file with the appropriate `ai_bin/` or IDE tool

### 🚫 NEVER DO

- Using `python3`, `python -c`, `json.tool`, `grep`, or `sed` to process `git show` output is a critical violation

---

## 4. Lockfile Policy

- This repository is an application/CI repo — commit `uv.lock`

---

## 5. WIP Commit Before HALT (MANDATORY)

> **See `git-workflow` skill → `implementation` task for complete WIP commit workflow.**

**CRITICAL: Work-in-progress commits MUST be made before ANY HALT to prevent data loss.**

### When to Commit WIP

| Scenario | Commit Type | Message Format |
|----------|-------------|----------------|
| Task complete | Full commit | `[Phase N] Task description` |
| Phase complete | Full commit | `[Phase N] Phase complete` |
| Mid-task HALT | WIP commit | `WIP: Phase N - description` |
| Awaiting clarification | WIP commit | `WIP: Phase N - awaiting clarification` |
| Error encountered | WIP commit | `WIP: Phase N - error: description` |
| Session ending | WIP commit | `WIP: Phase N - session end` |

### What Counts as HALT

| HALT Trigger | WIP Required? |
|-------------|--------------|
| Awaiting approval | ✅ YES |
| Awaiting clarification | ✅ YES |
| Mid-task pause | ✅ YES |
| Error encountered | ✅ YES |
| Session ending | ✅ YES |
| Task complete | ❌ NO (use full commit) |
| Phase complete | ❌ NO (use full commit) |

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

---

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

---

*Source: Content migrated from `110-git-protocol.md`*