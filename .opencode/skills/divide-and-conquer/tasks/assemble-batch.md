# Task: assemble-batch

Migrated from `implementation-workflow` task batch-orchestrate.

## Purpose

Orchestrate batch implementation by dispatching sub-agents for each approved issue, using branch-per-issue with merge-based dependency resolution. This task makes the main agent a pure orchestrator that never edits implementation files directly.

## Entry Criteria

- Approval-gate has verified authorization for one or more issues
- `pre-implementation-analysis` has expanded sub-issues and produced the flat item list
- Worktree is created and ready

## Exit Criteria

- All issues in batch have been implemented via sub-agents in separate branches
- Each sub-agent ran verification + finishing before returning
- All feature branches squash-merged into a single batch branch
- Compare URL generated, executive summary in chat
- HALT after review-prep (no PR creation without explicit instruction)

## Procedure

### Step 1: Determine Execution Order

- Read the batch state file from `pre-implementation-analysis` (`.opencode/tmp/batch-*.md`)
- For multi-issue: use dependency order from `pre-implementation-analysis`
- For single issue: treat as batch of one — no special casing, no shortcuts
- Determine complexity level for each issue (simple/moderate/complex)

**Single issue = batch of one.** There is no separate code path. The `assemble-batch` task handles single-issue dispatch as the default. This eliminates forked execution paths.

### Step 2: Create Feature Branches and Worktrees

For each issue in the batch:

1. Create a worktree with feature branch using `using-git-worktrees --task create-worktree`
2. `BASE_BRANCH` defaults to `dev` for the first/only issue in the batch
3. For dependent issues: `BASE_BRANCH` is set to the prior issue's feature branch (the merged branch, not the batch branch)
4. Record each issue's branch name and worktree path

### Step 3: Execute Issues in Dependency Order

For each issue in execution order:

1. **Before sub-agent dispatch**, if this issue depends on a prior issue:

   - Merge the prior issue's feature branch into this issue's feature branch:
     ```bash
     git merge <prior-issue-branch> -m "Merge <prior-issue-branch> into <current-branch> — dependency chain (#<prior>, #<current>)"
     ```
   - If merge produces conflicts:
     - Tiers 1-2 (trivial/formatting): Auto-resolve per `conflict-resolution` skill
     - Tier 3 (intent conflict): HALT and flag for developer review

2. **Build dispatch context** with AI-composed intent-and-context metadata:

   ```yaml
   batch:
     authorized_issues: [#A, #B, #C]
     completed_issues: [<completed>]
   issue: #<current>
   spec: "<full spec body from GitHub Issue>"
   authorization: "User approved #A, #B, #C on <date>"
   prior_context: "<AI-composed intent and context from prior issues>"
   dependency_branches: ["spec/<prior-branch>"]
   env_vars:
     WORKTREE_PATH: ".worktrees/spec-<name>"
     BRANCH_NAME: "spec/<name>"
     GIT_OWNER: "<from-session>"
     GIT_REPO: "<from-session>"
     DEV_NAME: "<from-session>"
     DEV_EMAIL: "<from-session>"
   ```

3. **Spawn sub-agent** via `task(subagent_type="general", prompt=...)`

4. **Sub-agent responsibilities:**

   - Load spec + session context + prior context
   - Run `divide-and-conquer` skill for the specific issue
   - Make WIP commits as needed
   - Run `verification-before-completion --task verify`
   - Run `finishing-a-development-branch --task checklist`
   - Return structured result: `{status, files_changed, summary}`

5. **Collect result** from sub-agent

6. **Compose prior_context** for the next issue based on what was implemented:

   - Design decisions made
   - Edge cases handled
   - Assumptions that later issues depend on
   - Interfaces exposed that later issues should use
   - NOT a change summary (that's in git) — intent and context only

7. **Mark prior issue's branch as frozen** — no rebasing, amending, or force-pushing

8. **Handle failures:**

   - If sub-agent fails: record failure
   - For independent issues: continue to next issue
   - For must-precede chains: skip dependent issues, report both

### Step 4: Batch Assembly

After ALL issues in the batch complete:

1. **Create a batch branch** (name chosen by agent at creation time, e.g., `batch/<short-name>` or `spec/<short-name>`):

   ```bash
   git checkout dev
   git checkout -b <batch-branch-name>
   ```

2. **Squash-merge each feature branch** into the batch branch, one commit per issue:

   ```bash
   git merge --squash spec/issue-a
   git commit -m "Implement #A: <description>"

   git merge --squash spec/issue-b
   git commit -m "Implement #B: <description> (#A dependency)"
   ```

3. **Commit message format:**

   - MUST include issue number for GitHub auto-linking
   - Dependents reference their dependencies
   - Example: `Implement #703: add reprocessing logic (#698 dependency)`

### Step 5: Post-Batch Review-Prep

1. **Verify all results** — check git log for all expected commits
2. **Run git-workflow --task review-prep** for the batch branch
3. **Collect compare URL**

### Step 6: Report and HALT

**Chat output:**

```markdown
**Summary:**

Implemented <N> issues via branch-per-issue batch orchestration.

**Outcome:**

- #A: <summary> ✅
- #B: <summary> ✅
- #C: <summary> ⚠️ (partial — see details)

Compare URL: https://github.com/<owner>/<repo>/compare/dev...<batch-branch>
```

**Issue comments:**
Post completion comment on each issue ONLY if substantive (per `github-comments` skill Substantive Comment Gate). Skip comment for non-substantive completions.

**HALT condition:**

- Do NOT create PR
- Do NOT close issues
- Wait for explicit "create a PR" instruction

## Intent-and-Context Metadata

`prior_context` replaces the old `prior_results` field. It is:

- **AI-composed**: The orchestrating agent intelligently composes the metadata based on the relationship between issues
- **No fixed template**: Format is flexible prose, not a structured form
- **Focus on intent**: Design decisions, edge case handling, assumptions, non-obvious constraints, interfaces that later issues depend on
- **NOT a change summary**: What changed is in git; why it changed is in prior_context

**What to include in prior_context:**

- Key design decisions made during implementation
- Non-obvious constraints discovered (e.g., "API returns 404 for missing items, not 403")
- Interfaces exposed that dependents should use
- Edge cases handled and how
- Assumptions that downstream code relies on

**What NOT to include:**

- List of files changed (available via `git diff`)
- Diff contents (available via `git log -p`)
- Verbatim spec text (sub-agent reads the spec directly)

## Frozen Branches

Once a prior issue's branch is merged into a dependent branch, it is **frozen**:

- No rebasing, amending, or force-pushing the frozen branch
- If a backtrack is needed:
  - Minor fix: Fix on the frozen branch, then each dependent branch re-merges
  - Major change: Full review of all dependent implementations, potential discard-and-restart
  - AI agent assesses scope based on blast radius
  - Always requires explicit developer authorization before proceeding

## Edge Cases

### Sub-Agent Failure

```
assemble-batch:
    → Dispatch sub-agent for #B
        → Sub-agent fails (error/timeout)
        → Record failure
    → If #B has dependents (#C requires #B): skip #C, report both
    → If #C is independent: continue with #C
    → After all possible issues complete:
        → Report failures clearly
        → HALT with partial results if any issues succeeded
```

### Sub-Agent Discovers Bug

```
assemble-batch:
    → Dispatch sub-agent for #B
        → Sub-agent discovers bug per bug-discovery protocol
        → Sub-agent reports bug as finding (read-only)
        → Sub-agent HALTs implementation for #B
        → Records: "#B halted — bug discovered at <location>"
    → Continue to next independent issue
    → Report bug in batch summary
```

### Tier 3 Conflict During Dependency Merge

- HALT immediately
- Report the conflict and which two branches are involved
- Do NOT attempt to resolve intent conflicts automatically
- Wait for developer review per `conflict-resolution` skill

### Session Restart Mid-Batch

- Use `git log --oneline` on the batch branch to determine completed issues
- Each squash-merged commit in the batch branch corresponds to one completed issue
- Resume from the first incomplete issue by checking which issue numbers appear in commit messages
- Feature branches still contain the individual issue work for reference

### Parallel-Safe Issues (No Dependencies) — Opportunistic Only

- Even independent issues SHOULD be stacked sequentially. Parallel execution is opportunistic — it depends on circumstances genuinely allowing it (no shared files, no logical coupling, no hidden dependencies).
- "Independent" in a batch context means "no declared dependency," not "safe to run in parallel." Stacking catches hidden dependencies automatically.
- If parallel execution is chosen for an independent issue, document the justification in the batch state file with explicit reasoning (why stacking was bypassed, what makes the issue genuinely independent).

## Mandatory Rules

01. **Main agent NEVER edits implementation files** — only orchestrates
02. **Every sub-agent runs verification + finishing** — no skipping
03. **One branch per issue** — each issue gets its own feature branch, never shared
04. **Dependency resolution via git merge** — later issues merge prior branches, not branch-from-prior
05. **Frozen branches after merge** — no rebasing or amending a merged branch
06. **No HALTs between issues** — all issues complete before single HALT
07. **Single batch PR** — squash-merge each feature branch into batch branch, then one PR
08. **Intent-and-context metadata** — AI-composed, no fixed template, focus on why not what
09. **Conflict resolution tiers** — auto-resolve 1-2, HALT on tier 3 during dependency merges
10. **Always batch mode** — single issue = batch of one, no special-case path

Co-authored with AI: OpenCode (ollama-cloud/glm-5.1)